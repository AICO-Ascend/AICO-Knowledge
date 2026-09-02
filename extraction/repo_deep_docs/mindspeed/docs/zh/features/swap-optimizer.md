# Swap Optimizer

> 仓 `mindspeed` · 路径 `docs/zh/features/swap-optimizer.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed/docs/zh/features/swap-optimizer.md

# Swap Optimizer 文档深度解读

---

## 【定位】

本文档描述了 mindspeed 中的一种**显存优化特性**：在大模型训练的前反向阶段，将优化器状态（FP32 权重 + FP32 动量）从 device 侧卸载到 host 侧内存，在 step 更新阶段再加载回 device 侧，从而**降低训练过程中的显存峰值，缓解 OOM 问题**。

---

## 【技术要点】

1. **显存占用来源**：大模型训练中，前反向使用 BF16 计算，梯度更新时使用 FP32。优化器需保存一份 FP32 权重 + 两份 FP32 动量，显存开销为 **`参数量 × 12` Byte**。该部分显存在前反向阶段闲置但仍占用显存，推高峰值。

2. **优化思路**：前反向阶段将优化器状态卸载到 host 侧，device 侧仅保留逻辑视图；step 阶段再加载回 device 侧做 AdamW 更新。

3. **初始化阶段 swap**：优化器初始化调用 `shard_fp32_from_float16_groups` 时，从模型 BF16 权重复制到优化器 FP32 权重，**每复制一份权重就立即 swap 到 host 侧**，避免冲击显存峰值；反向加载时同理。原文称对性能影响"可忽略"（仅初始化阶段）。

4. **Step 阶段分块并行**：step 更新时，先一次性下发约 **`numel(shard_fp32_from_float16_groups) // swap_optimizer_times`** 大小参数的 h2d（host→device）操作，再做 AdamW 计算并将结果 copy 回 BF16 模型权重，最后做 d2h（device→host）释放显存。

5. **异步时序约束**：d2h 与 h2d 是异步拷贝，因此**下一轮的 h2d 必须等待前一轮的 d2h 操作结束后才能下发**，以保证时序正确。

6. **参数 trade-off**：`--swap-optimizer-times` 默认值为 16，参数越小并行越多，可减少性能劣化，但会提高显存峰值。

---

## 【关键机制与数据】

| 维度 | 内容 |
|---|---|
| 显存节省对象 | FP32 优化器权重 + 两份 FP32 动量 |
| 显存占用公式 | `参数量 × 12` Byte（原文直接给出） |
| 卸载时机 | 前反向阶段 → host；step 阶段 → device |
| 初始化 swap 粒度 | 每复制一份权重即 swap 一次 |
| Step 阶段 h2d 分块大小 | `numel(shard_fp32_from_float16_groups) // swap_optimizer_times` |
| 关键变量 | `swap_optimizer_times`（默认 16） |
| 异步时序 | 下一轮 h2d 需等待前一轮 d2h 结束 |

原文通过一张流程图（`figures/swap-optimizer.png`，未在文本中展开）展示了 Swap Optimizer 的整体流程。

---

## 【表格解读】

**原文无表格。** 文档中仅以文字、列表和公式形式描述机制，未提供参数表、性能对比表或配置项表格。

---

## 【公式解读】

原文仅包含一个分块大小表达式（伪代码形式）：

```
h2d 单次下发大小 ≈ numel(shard_fp32_from_float16_groups) // swap_optimizer_times
```

- **`shard_fp32_from_float16_groups`**：分布式优化器中的 FP32 优化器权重（按 shard 切分），其元素总数为 `numel(...)`。
- **`swap_optimizer_times`**：step 阶段进行 swap 的次数（命令行参数，默认 16）。
- **整除 `//`**：将总元素数平均切分为 `swap_optimizer_times` 份，每份大小即为单次 h2d 操作的数据量。

> 该式子隐含的含义是：**`swap_optimizer_times` 越大，每份数据越小，显存峰值越低；反之则并行粒度更大，但显存峰值更高**。

文档未给出更复杂的数学公式，显存占用的 `参数量 × 12` 仅为常量倍数关系。

---

## 【关联】

- **前置依赖特性**：
  - `--use-distributed-optimizer`（分布式优化器）：本特性基于其 shard 切分的 FP32 权重做 swap；
  - `--optimizer-selection fused_adamw`：本特性仅在该优化器下生效。

- **互补方案**：文档开篇提到"可以通过分布式优化器等特性来减少这部分显存占用，但无法完全消除，且减少比例过于依赖 DP 数"，表明 swap optimizer 是对分布式优化器显存优化的**进一步补充**。

- **不兼容特性**（原文 NOTE 明确列出）：
  - `--reuse-fp32-param`
  - fused ema adamw 优化器
  - 其他优化器相关特性

- **上游流程图**：引用了 `figures/swap-optimizer.png` 来说明 h2d → AdamW 计算 → 写回 BF16 权重 → d2h 的整体流程。

---

## 【使用方法】

**启用参数**：

| 参数 | 含义 |
|---|---|
| `--swap-optimizer` | 开启 swap optimizer 特性 |
| `--swap-optimizer-times` | 设置 step 阶段 swap 次数，默认 16；参数越小并行越多、性能越好，但显存峰值更高 |

**推荐环境变量配置**（粗粒度 NUMA 绑核，避免跨 NUMA 内存访问）：

```bash
export CPU_AFFINITY_CONF=1,lazy_bind:0
```

**使用前提（原文 NOTE 强约束）**：

1. 必须同时开启 `--use-distributed-optimizer` 且 `--optimizer-selection` 为 `fused_adamw`；
2. **不得**与 `--reuse-fp32-param`、`fused ema adamw` 等优化器相关特性同时使用。

## 图文联合解读

- `swap-optimizer.png`: **图示解读：**

1）图含H2D流（上）、计算流（中）、D2H流（下）三条并行轨道，竖线分左右两轮；每轮3次H2D→AdamW+copy→D2H的流水线，右轮首箭头依赖左轮末D2H。

2）论证h2d与d2h可在异构流并行、计算与传输流水化，但相邻轮次的h2d须在前轮d2h完成后才可下发，以保障异步拷贝时序正确。

3）图直观对应文档第2、3条方案：通过`swap_optimizer_times`切分参数实现step内流水并行，降低显存峰值。
