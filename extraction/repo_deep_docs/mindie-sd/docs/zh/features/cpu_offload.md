# CPU 卸载

> 仓 `mindie-sd` · 路径 `docs/zh/features/cpu_offload.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-sd/docs/zh/features/cpu_offload.md

# 深度解读：CPU 卸载（CPU Offload）

## 【定位】
本文档描述 mindie-sd 仓库中针对 DiT 类模型推理场景的 **异步 Offload 能力**——当模型规模超出单卡 NPU 显存容量时，将部分层权重卸载到 CPU 内存并通过异步流水线与计算并行化，从而显著提升推理时的 GPU 利用率。

---

## 【技术要点】

1. **问题定义**：DiT 模型推理中所有 block 权重需常驻 NPU 显存；单卡显存不足时需把部分层的权重暂卸到 CPU 内存，到该层计算时再搬运回 NPU，该技术称为 offload。
2. **同步 Offload 痛点**：GPU 计算完一层后必须停下等待下一层权重从 CPU 搬运到 NPU，搬运完成才能继续计算，**GPU 大部分时间处于空闲等待状态**，利用率降低。
3. **异步 Offload 方案核心**：通过**异步流水线**将计算与权重加载并行化——GPU 计算第 N 层时，第 N+1 层的权重已在后台搬运；当第 N 层计算完成时，第 N+1 层权重已加载就绪，**计算耗时掩盖搬运耗时**，GPU 空闲时间显著减少。
4. **四实现机制**：
   - **独立拷贝流**：`h2d_stream`（Host → Device）与 `d2h_stream`（Device → Host），与计算流分离，实现拷贝与计算并行。
   - **前向预 Hook**：block 执行前，**异步加载**后续 block 权重到 NPU。
   - **前向 Hook**：block 执行后，将已用完的权重从 NPU 卸载，**释放显存**。
   - **预留 block 数**：通过 `min_reserved_blocks_count` 参数控制始终保留在 NPU 上的 block 数量，其余 block 动态换入换出。
5. **公开接口**：`mindiesd.offload.enable_offload(model, blocks, min_reserved_blocks_count=2)`，其中 `min_reserved_blocks_count` 默认值为 **`2`**。
6. **使用约束**：与 `DyEPLB.md` 所述特性同时使用时可能存在带宽争抢，需自行调整执行时机避免相互阻塞。

---

## 【关键机制与数据】

**工作原理（异步流水线）**：
- GPU/NPU 计算第 N 层 block 时，后台预先把第 N+1 层（甚至更靠后）的权重通过 `h2d_stream` 拷贝到设备上；
- 第 N 层计算完成后，前向 Hook 立即触发 `d2h_stream`，把该层不再需要的权重卸载回 CPU 内存；
- 通过 `min_reserved_blocks_count` 把一小批 block 始终钉在 NPU 上，避免所有 block 都频繁换入换出；
- 关键收益：搬运耗时被下一层计算耗时所掩盖，因此 GPU 空闲时间显著下降。

**数据流（按 block 推进）**：
> 原文中以配图 `figures/offload_process_image.png`（同步）与 `figures/async_offload_image.png`（异步）两图并列展示流程对比，原文未给出具体的耗时数字、吞吐数字或加速比数值。

**关于"性能数据"**：
> 原文未给出任何量化性能指标（如延迟、吞吐、加速比、显存节省幅度等），仅以定性描述"GPU 空闲时间显著减少"。

---

## 【表格解读】

### 原文表格：`enable_offload` 参数说明表

| 参数 | 类型 | 必选 | 默认值 | 说明 |
|------|------|------|--------|------|
| `model` | `torch.nn.Module` | 是 | - | 需要启用 offload 的目标模型 |
| `blocks` | `ModuleList` | 是 | - | 模型中按顺序排列的 block 列表 |
| `min_reserved_blocks_count` | `int` | 否 | `2` | 始终保留在 NPU 上的 block 数量 |

**逐行解读**：

- **`model: torch.nn.Module`**（必选，无默认值）：传入需要启用 offload 的目标模型，即要被管理的 DiT 模型实例本身；接口会对该模型原地注入 hook，因此属于"原地修改"，不返回新对象。
- **`blocks: ModuleList`**（必选，无默认值）：传入**按顺序排列**的 block 列表——这里的顺序很关键，因为前向预 Hook 需要按这个顺序决定"下一个要被预加载的是哪个 block"，offload 才能正确流水化；调用方需自行保证 list 与模型前向执行顺序一致。
- **`min_reserved_blocks_count: int`**（选填，默认 `2`）：始终钉在 NPU 上的 block 数量。其余 block 按需动态换入换出。提高此值可减少搬运频率，但会占用更多 NPU 显存；降低此值可释放更多显存，但可能增加搬运次数。需要根据模型总层数、单层权重体积与显存余量做权衡。

---

## 【公式解读】

**原文无公式**（文档中仅有 Python 函数签名与代码示例，未给出任何数学公式或 LaTeX 表达式）。

---

## 【关联】

文档末尾通过内部链接指向 **DyEPLB.md**，指出二者同时启用时存在**带宽争抢风险**：

- **CPU Offload** 会持续在 `h2d_stream` / `d2h_stream` 上做权重搬运，占用 Host↔Device 带宽；
- **DyEPLB**（从链接名推测为动态 Expert/层负载均衡类机制，详见 DyEPLB.md）同样会进行设备间调度与数据移动；
- 二者并发执行时若不协调执行时机，可能在 H2D/D2H 链路上相互阻塞；
- 因此文档建议：**自行调整执行时机**，让两套机制错峰运行，避免带宽争抢。

文档未给出上下游框架（如 vLLM Omni、Diffusers+CacheDit、lightx2v）是否直接调用 `enable_offload` 的说明，仅以"创建 DiTModel → 启用 offload → `.to('npu')` → 正常推理"的通用示例呈现。

---

## 【使用方法】

**启用方式**（原文提供完整示例）：

```python
from mindiesd.offload import enable_offload

# 创建模型
model = DiTModel(...)

# 启用 offload，保留 2 个 block 在 NPU
enable_offload(model, model.blocks, min_reserved_blocks_count=2)

# 将模型移动到 NPU
model.to("npu")

# 正常执行推理，框架自动管理权重的异步换入换出
with torch.no_grad():
    output = model(x)
```

**配置项总结**（均来自原文接口说明）：

- 调用入口：`mindiesd.offload.enable_offload`
- 必传参数：`model`（`torch.nn.Module`）、`blocks`（`ModuleList`）
- 可选参数：`min_reserved_blocks_count`（`int`，默认 `2`）
- 返回值：`None`，原地修改
- 模型放置：调用 `enable_offload` 之后再调用 `model.to("npu")`
- 推理上下文：示例中使用 `torch.no_grad()`，表明该能力面向推理而非训练

**注意事项**：

- 与 `DyEPLB.md` 同时使用需注意带宽争抢并自行错峰执行时机（原文明确给出此提示）。
- 原文未涉及命令行 CLI、环境变量、yaml 配置或脚本化开关的启用方式。

## 图文联合解读

- `offload_process_image.png`: **图文联合解读：**

1. **画面内容**：顶部横向排列Layer0–Layer3四个色块，下方为四条时间轴，每条轴依次显示"loading→computing→d（空闲等待）"三段，箭头将各层映射到对应时间轴，呈现严格的串行流水。

2. **技术结论**：同步offload下，loading与computing必须顺序衔接，computing结束后存在显著空闲"d"间隙，整体吞吐受限于权重传输，无法直接决定效率天花板。

3. **与文档关系**：该图即文档引用的`offload_process_image.png`，对应"同步offload模式"段落，与右侧异步offload图对照，反衬本仓库异步流水线方案的必要性。
- `async_offload_image.png`: **图文联合解读：**

**画面**：四层（Layer0-3）沿时间轴错位排列，每层含绿色"computing"块和紫色"loading"块，呈流水线式交叠——第N层计算时，第N+1层已在后台加载。

**结论**：异步流水线使权重搬运与计算并行，搬运耗时被计算耗时掩盖，GPU 空等显著减少。

**与文档关系**：直观印证"独立拷贝流+预取 Hook+min_reserved_blocks"机制所实现的异步 Offload 并行化效果。
