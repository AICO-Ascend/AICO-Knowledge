# Swap Optimizer

> 仓 `mindspeed-rl` · 路径 `docs/zh/features/swap_optimizer.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-rl/docs/zh/features/swap_optimizer.md

# Swap Optimizer 文档深度解读

## 【定位】

这篇文档描述了 mindspeed-rl（昇腾强化学习加速库）中一项用于**缓解大模型训练显存峰值压力**的特性：通过将优化器状态卸载到主机端（host）内存、仅在每次 step 时按需加载到设备端（device），减少 device 侧的显存占用，从而避免 OOM 中断训练。

---

## 【技术要点】

1. **显存开销基线**：在大模型训练中，前反向使用 BF16、权重更新使用 FP32，优化器需同时保存 FP32 权重 + 两个 FP32 动量，单参数显存占用为 `参数量 * 12` Bytes。
2. **核心思路——状态卸载**：将优化器状态卸载到 host 内存，device 仅保留必要的逻辑视图；每次 step 时再把优化器状态从 host 重新加载到 device。
3. **初始化阶段的 swap**：执行 `shard_fp32_from_float16_groups` 时，将 BF16 权重复制为 FP32 格式，并在每次复制后**及时将权重交换到 host**，避免冲击显存峰值；初始化阶段执行一次，性能影响可忽略。
4. **Step 阶段分片传输**：每次 step 时，先按约 `numel(shard_fp32_from_float16_groups) // swap_optimizer_times` 大小做一轮 H2D（host → device），再在该分片上跑 AdamW，把结果拷回 BF16 权重，最后做 D2H（device → host）释放 device 显存。
5. **异步拷贝时序保证**：D2H 与 H2D 是异步的，为保证时序正确，**第二轮 D2H 必须等待第一轮 H2D 完成**才会执行。
6. **可调并行度**：`swap_optimizer_times` 默认值为 `16`，该值越大 → 每次传输分片越小、H2D/D2H 并行度越高 → 性能劣化越小，但 device 显存峰值会升高。

---

## 【关键机制与数据】

- **优化器状态显存计算（原文）**：FP32 权重 + 两个 FP32 动量 ⇒ 单参数 `12 Bytes`，仅在权重更新阶段使用，前反向不被使用，但会推高峰值导致 OOM。
- **数据流（原文拆解）**：
  1. **Init**：`shard_fp32_from_float16_groups` 把 BF16 权重拷到 FP32 → 拷贝过程中同步 swap 到 host → 权重加载到 device 时同样做 swap。
  2. **Step**：每次切出约 `numel(...) // swap_optimizer_times` 的分片做 H2D → AdamW 计算 → 结果回写 BF16 权重 → D2H 释放。
  3. **并发编排**：H2D 与 D2H 异步并行；通过"下一轮 D2H 等上一轮 H2D 完成"约束保证时序不乱。
- **效果（原文定性描述）**：能够有效减少训练过程中 device 侧的显存占用，缓解因 OOM 导致的训练中断问题。原文未给出量化性能/显存数据。

---

## 【表格解读】

原文无表格。

---

## 【公式解读】

原文无公式（仅有一个描述性表达式 `参数量 * 12` Bytes，属于显存估算说明而非公式；以及 step 阶段分片大小 `numel(shard_fp32_from_float16_groups) // swap_optimizer_times`，属于伪代码式大小描述，按原文逐字保留如下）。

- 优化器状态显存占用：`参数量 * 12` Bytes（原文: FP32 权重 + 两个 FP32 动量 的总量）。
- Step 阶段单次 H2D 传输分片大小：`numel(shard_fp32_from_float16_groups) // swap_optimizer_times`（原文: step 阶段一次传输的参数规模）。

---

## 【关联】

依据文末"内部链接: (无)"，本文档未提供内部跳转链接；以下关系均来自正文文本：

- **依赖项 / 适用前置**：
  - 分布式优化器 `use_distributed_optimizer: true`——本特性仅在该优化器下生效。
  - `optimizer_selection: fused_adamw`——优化器选择必须为 fused_adamw。
- **互斥 / 不兼容项**：
  - `reuse_fp32_param`（暂不兼容）。
  - fused ema adamw 优化器（暂不兼容）。
  - 其他"优化器相关特性"（泛指）。
- **运行环境配置**：`CPU_AFFINITY_CONF=1,lazy_bind:0`——与本特性搭配使用的推荐绑核配置，用于把任务绑定到 NPU 对应的 NUMA CPU 核心，避免跨 NUMA 内存访问。
- **上下游动机**：文档背景中提到分布式优化器虽能减小显存但效果依赖 DP 数量且无法完全消除额外显存，本特性作为其补充进一步卸载 host 端状态。

---

## 【使用方法】

**启用条件（原文）：** 仅适用于"开启了分布式优化器 `use_distributed_optimizer` 且 `optimizer_selection` 为 `fused_adamw`"的训练场景。

**配置项（原文）：**

| 配置项 | 取值 | 作用 |
|---|---|---|
| `use_distributed_optimizer` | `true` | 使用分布式优化器（前置） |
| `optimizer_selection` | `fused_adamw` | 优化器选用 fused_adamw（前置） |
| `swap_optimizer` | `true` | 开启 swap optimizer 特性 |
| `swap_optimizer_times` | `[int]`，默认 `16` | 设置 step 更新阶段 swap 次数；值越大并行越多、性能劣化越小，但显存峰值更高 |

**推荐环境变量（原文）：**

```bash
export CPU_AFFINITY_CONF=1,lazy_bind:0
```

作用：启用粗粒度绑核模式，将任务绑定到 NPU 对应的 NUMA CPU 核心，避免跨 NUMA 内存访问、减少调度开销，提升计算稳定性与性能。

**注意事项（原文）：**

1. 本特性仅适用于开启 `use_distributed_optimizer` 且 `optimizer_selection` 为 `fused_adamw` 的场景。
2. 与 `reuse_fp32_param`、fused ema adamw 优化器等其他优化器相关特性暂不兼容。

## 图文联合解读

- `swap_optimizer.png`: **图文联合解读：**

**1) 图示内容：** 三泳道流水线（H2D流/计算流/D2H流），左右两轮各分3块。箭头方向：H2D→AdamW+copy→D2H；且后一轮H2D依赖前一轮D2H完成，呈现H2D与D2H并行重叠、计算夹在中间的分块流水线结构。

**2) 技术结论：** 论证了"分块swap + 三流并行"可行性：将优化器状态切成`swap_optimizer_times`份，H2D、AdamW+copy、D2H三流以流水方式重叠执行，仅通过跨轮的D2H→H2D依赖保证时序正确，从而以小显存峰值换得接近无swap的性能。

**3) 与文档关系：** 图直接对应「解决方案」第2、3条——可视化"一次性传输约`numel//swap_optimizer_times`"的分块策略，以及"第二轮D2H需等待第一轮H2D"的异步时序约束，是该特性的核心机制示意。
