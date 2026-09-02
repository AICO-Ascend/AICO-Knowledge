# Design Document: 工具支持基于实测算子性能的建模

> 仓 `msmodeling` · 路径 `docs/design/profiling_driven_empirical_performance_model.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msmodeling/docs/design/profiling_driven_empirical_performance_model.md

# 一体化深度解读：基于实测算子性能的建模设计文档

## 【定位】

本文档描述 msmodeling 中 **基于实测算子 profiling 数据的 EmpiricalPerformanceModel 能力**：在 TensorCast Runtime 中新增"实测驱动"的性能模型分支，使性能建模可优先读取内置算子性能数据库中的真实 NPU profiling 数据，弥补现有 Roofline 理论模型在特定硬件平台、复杂算子实现、组合场景下与真实性能之间存在的偏差。

---

## 【技术要点】

1. **双模型并存与回退机制**：TensorCast Runtime 通过 TorchDispatchMode 拦截所有算子调用生成 `OpInvokeInfo`，由用户可选的 `PerformanceModel`（`EmpiricalPerformanceModel` / `AnalyticPerformanceModel`）处理。`EmpiricalPerformanceModel` 内置 `fallback_model`（默认 `AnalyticPerformanceModel`），实测数据库未命中时自动回退到 Roofline。

2. **DataSource 抽象接口与查询优先级**：查询优先级为「精确匹配 → 插值（未来扩展）→ 外推（未来扩展）」。`DataSource` 是抽象基类，TensorCast 只通过 `OpInvokeInfo` 查询，不感知底层映射关系；当前实现为 `ProfilingDataSource`，未来将扩展 `InterpolatingDataSource`。

3. **性能数据存储分层结构**：存储路径按 `设备名/vllm_ascend/vllm{版本}_torch{pytorch版本}_cann{CANN版本}/` 组织计算算子性能数据，通信算子数据放在 `hccl/{CANN版本}/`（与 CANN 版本绑定、跨 vLLM 版本复用）。每个目录下包含 `op_mapping.yaml`（TensorCast 虚拟算子到 NPU KernelType 的映射）与 `{KernelType}.csv`（kernel 性能数据库）。

4. **八种查询分派路径**：`ProfilingDataSource.lookup()` 去掉 `torch.ops.` 前缀后，在 `op_mapping.yaml` 中按以下顺序分派——Composite / Communication / Attention special / Elementwise / MoE fused / Zero cost / Accepted miss / Compute（默认）。不同路径返回 `MEASURED`、`INTERPOLATED`、`PARTIAL` 等不同 `QuerySource` 类型。

5. **单位换算**：命中结果以 `latency_us`（微秒）返回，转换为 SI 标准秒作为最终 `execution_time_s`，换算关系为 `execution_time_s = result.latency_us * 1e-6`。

6. **CLI 启用方式**：在 `cli/inference/text_generate.py` 中新增 `--performance-model` 参数，使用 `action="append"` 支持多次指定，取值包括 `'analytic'`（Roofline，默认）和 `'profiling'`（基于实测 profiling 数据库的 EmpiricalPerformanceModel）。

---

## 【关键机制与数据】

### 整体工作流

1. **算子拦截**：TensorCast Runtime 通过 `TorchDispatchMode` 拦截所有算子调用，生成 `OpInvokeInfo`。
2. **模型选择**：用户通过配置在 `EmpiricalPerformanceModel`（实测）与 `AnalyticPerformanceModel`（Roofline）之间选择。
3. **查询流程**：`EmpiricalPerformanceModel.process_op()` → `DataSource.lookup(OpInvokeInfo)` → 命中则返回 `Result(execution_time_s=result.latency_us * 1e-6)`；未命中则回退到 `fallback_model.process_op()`。
4. **数据加载**：`ProfilingDataSource` 加载 `op_mapping.yaml` 与 `{KernelType}.csv`，查询逻辑为 `func_name → mapping → CSV row → latency_us`。

### 查询分派路径详解

| 路径 | 触发条件 | 数据返回行为 |
|------|---------|------------|
| Composite | `composite: true` | 先用 decomposer 分解，再累加子算子（计算 + 通信）时长；子算子部分 MISS 时返回 `PARTIAL` |
| Communication | `category: communication` | 通信量/device 数/拓扑层级精准匹配 → `MEASURED`；否则按通信量插值 → `INTERPOLATED` |
| Attention special | `query_mode: attention_special` | 主用于 `FusedInferAttentionScore`，按 `alternate_kernel_types` 优先级查询 attention 维度数据 |
| Elementwise | `query_mode: elementwise` | 主用于 `aten.mul` 等，按输出 shape 严格匹配，支持按 dtype 字节比缩放 |
| MoE fused | `query_mode: moe_fused` | 主用于 `DispatchFFNCombine`，按 shape 与 ep_size 匹配 |
| Zero cost | `zero_cost: true` | 返回 `0.0 us`，标记为精准查询 |
| Accepted miss | `accepted_miss: <reason>` | 返回 `0.0 us` + 解释，用于"TensorCast 存在但 NPU profiling 中无独立 kernel"（已被融合到其他算子）的场景 |
| Compute | 默认路径 + 配置 `kernel_type` | 按优先级查询 `alternate_kernel_types` 中算子对应 shape 的数据 |

### 关键约束（原文）

- 原文："当前msmodeling主要基于roofline进行算子性能估算，虽能覆盖通用场景下的性能分析需求，但是在面对特定硬件平台、复杂算子实现及组合场景时，估算与真实评估性能存在一定偏差。"
- 原文："未命中 → fallback (Analytic) 使用roofline模型结果。"
- 原文："DataSource（抽象接口）...TensorCast 只通过 OpInvokeInfo 查询，不感知底层映射关系和数据格式。"
- 原文："通信: hccl/{cann_version}/*.csv...和 CANN 版本绑定，跨 vLLM 版本复用"

---

## 【表格解读】

### 表 1：修订记录（原文逐字还原）

| Date (日期) | Version (修订版本) | Change Description (修改描述) | Author (作者) | RFC Document (RFC文档) |
| ---------- | -------------- | ------------------------- | ----------- | -------------------- |
| 2026-06-12 | 1.0 | 初稿完成，工具支持基于实测算子性能的建模 | - | - |

**逐行解读**：该表为文档元数据表，标记本文档为 v1.0 初稿（2026-06-12），对应 RFC 文档暂无，作者栏留空（"-"占位）。说明本文档为方案初定稿，后续可能随 RFC 推进与实测数据扩充继续演进。

### 表 2：ProfilingDataSource 查询分派路径表（原文逐字还原）

| 路径 | `op_mapping.yaml` 触发条件 | 核心方法 | 返回行为 |
| ----------------- | ------------------------------- | --------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| Composite | `composite: true` | `_lookup_composite` | 复合算子的查询方式，按照先用定义的decomposer再查配置文件的顺序获取分解的子算子，再分别获取各个计算算子与通信算子的时长并累加。当decomposer查询子算子的场景，当部分子算子MISS 时可返回 `PARTIAL`。 |
| Communication | `category: communication` | `_lookup_comm` | 查询通信算子时长。通过通信量、device个数、通信拓扑层级进行查找数据，若可以精准查询，则返回对应时长，结果类型为`MEASURED`；若无法查询到，根据device个数与通信拓扑层级进行查找，以通信量进行插值推测，最终返回结果类型为`INTERPOLATED` |
| Attention special | `query_mode: attention_special` | `_lookup_attention` | 目前主要用于算子 `FusedInferAttentionScore`；存在 `alternate_kernel_types` 时按优先级查询对应算子在attention相关维度的数据。 |
| Elementwise | `query_mode: elementwise` | `_lookup_elementwise` | 适用于`aten.mul`等逐元素操作的算子。按输出 shape 严格匹配，也支持按 dtype 字节比缩放时长。 |
| MoE fused | `query_mode: moe_fused` | `_lookup_moe` | 目前主要用于算子DispatchFFNCombine。根据shape与ep_size进行匹配查询数据。 |
| Zero cost | `zero_cost: true` | 视为算子耗时为0 | 返回 `0.0 us`，设为精准查询。 |
| Accepted miss | `accepted_miss: <reason>` | 视为算子耗时为0 | 返回 `0.0 us` 和相应解释说明。用于 TensorCast 中存在、但 NPU profiling 中没有独立 kernel 的算子（如TensorCast存在，但是NPU profiling时已经被融到其他算子中的场景）。 |
| Compute | 默认路径，配置 `kernel_type` | `_lookup_compute` | 按优先级查询 `alternate_kernel_types`中对应算子对应shape的数据。 |

**逐行解读**：

- **Composite 路径**：是处理"复杂组合算子"的主入口，先通过 decomposer 把复合算子拆解为子算子（计算+通信），分别查询后累加时长。在 decomposer 拆解过程中若出现部分子算子 MISS，则返回 `PARTIAL` 状态，已累加的部分经验时长仍可使用。
- **Communication 路径**：通信算子查询会综合"通信量 + device 个数 + 拓扑层级"三要素做精准匹配；精准命中时返回 `MEASURED`，未命中时按通信量做插值推算并返回 `INTERPOLATED`（这是查询优先级链路"精确匹配 → 插值 → 外推"在通信算子上的具体体现）。
- **Attention special 路径**：专门服务 `FusedInferAttentionScore` 这类复杂融合算子，通过 `alternate_kernel_types` 按顺序在多个候选内核类型间查找，性能匹配按 attention 相关维度。
- **Elementwise 路径**：面向 `aten.mul` 这类逐元素操作，按"输出 shape"做严格匹配；当 shape 不完全一致时，可按 dtype 的字节数比例对时长做缩放估算。
- **MoE fused 路径**：当前主要覆盖 `DispatchFFNCombine`，匹配维度是 shape 与 ep_size（专家并行度）。
- **Zero cost 路径**：配置 `zero_cost: true` 时直接将算子耗时视为 0，并标注为精准查询结果。适用于开销极低、无需建模的元算子。
- **Accepted miss 路径**：针对"TensorCast 虚拟算子中存在、但 NPU profiling 中没有独立 kernel"（如算子已被融合进其他 kernel）的场景，主动认定为 0 时长但附带解释说明，避免被误判为 MISS。
- **Compute 路径（默认）**：所有未命中特殊配置的计算算子落入此路径，按 `alternate_kernel_types` 中声明的优先级顺序查找算子对应 shape 的实测数据。

---

## 【公式解读】

### 公式 1：单位换算

```python
Result(execution_time_s=result.latency_us * 1e-6, ...)
```

**符号说明**：
- `result.latency_us`：数据源查询返回的算子时延值，单位为微秒（μs）。
- `1e-6`：微秒到秒的换算系数（1 μs = 10⁻⁶ s）。
- `execution_time_s`：最终输出的算子执行时延，单位为秒（SI 标准），是性能模型对外暴露的标准时间量。

**作用**：`ProfilingDataSource` 内存储的所有 CSV 时延均以微秒计，但性能模型对外结果需要保持 SI 单位一致性，通过此换算式完成"μs → s"的单位归一化。

### 伪代码公式：查询优先级

```
查询优先级：精确匹配 → 插值（未来扩展） → 外推（未来扩展）
```

**符号说明**：
- **精确匹配**：直接命中 CSV 数据，返回 `MEASURED`。
- **插值**：未来 `InterpolatingDataSource` 提供的能力，按通信量、shape 等维度在已有数据点之间做线性/非线性插值，返回 `INTERPOLATED`。
- **外推**：未来扩展能力，在已有数据范围之外做推算（当前文档未给出具体实现）。

**作用**：定义 DataSource 的查询回退策略——在"精确命中"缺失时逐步降级到"估算"，避免直接 MISS 导致模型精度崩塌。

---

## 【关联】

本节基于文末标注"内部链接: (无)"的实际情况进行分析，文档中明确提及的关联模块/上下游如下：

### 上游（依赖）

- **TensorCast Runtime（TorchDispatchMode）**：所有算子调用的拦截入口，`EmpiricalPerformanceModel` 接收的 `OpInvokeInfo` 由其生成。
- **AnalyticPerformanceModel（`tensor_cast/performance_model/analytic.py`）**：现有的 Roofline 理论模型，作为 `EmpiricalPerformanceModel` 的默认 `fallback_model`。
- **CommAnalyticModel（`tensor_cast/performance_model/comm_analytic.py`）**：现有通信解析模型，与新增通信 profiling 路径形成对照。
- **MemoryTracker（`tensor_cast/performance_model/memory_tracker.py`）**：同目录下已有模块，与经验性能模型并列共存。

### 下游（被依赖）

- **CLI 入口 `cli/inference/text_generate.py`**：通过新增 `--performance-model` 参数对外暴露能力，是用户启用 EmpiricalPerformanceModel 的主要入口。
- **vLLM Ascend / HCCL**：性能数据库按软件栈版本组织（`vllm_ascend/{vllm版本}_torch{pytorch版本}_cann{CANN版本}/`、`hccl/{CANN版本}/`），说明该能力服务的是基于 vLLM Ascend + HCCL 的推理场景建模。

### 横向（同级/并行）

- **InterpolatingDataSource**：未来扩展模块，当前仅占位（"能力启用待未来扩展"）。
- **op_mapping.yaml**：作为 TensorCast 虚拟算子与 NPU profiling 数据间的解耦层，使 DataSource 对 TensorCast 屏蔽底层数据格式。

### 文档内交叉引用

- 第 2.1 节架构图 → 第 2.2 节模块结构 → 第 2.3 节核心模块设计，三层构成自顶向下的设计展开链路。
- 第 3.1 节 CLI 接口 → 复用第 2.3.1 节 `EmpiricalPerformanceModel` 的对外能力。

---

## 【使用方法】

### 启用方式（原文已给）

在 `cli/inference/text_generate.py` 中新增 `--performance-model` 参数：

```python
parser.add_argument("--performance-model",
                    action="append",
                    default=None,
                    help="性能模型类型，可多次指定。"
                         "'analytic': Roofline 模型（默认，无需数据）。"
                         "'profiling': 基于实测 Profiling 数据库的 EmpiricalPerformance"
```

### 配置项与命令摘要

| 配置项 / 参数 | 取值 | 行为 | 原文出处 |
|---------------|------|------|---------|
| `--performance-model analytic` | Roofline 理论模型 | 默认行为，无需任何 profiling 数据 | 第 3.1 节 |
| `--performance-model profiling` | 实测 Profiling 数据库 | 启用 `EmpiricalPerformanceModel`，优先查 `op_mapping.yaml + {KernelType}.csv` | 第 3.1 节 |
| `action="append"` | Python argparse 行为 | 支持多次指定，可叠加多个性能模型 | 第 3.1 节 |

### 配置文件约定（原文已给）

- `op_mapping.yaml` 配置项与触发条件：`composite`、`category`、`query_mode`、`zero_cost`、`accepted_miss`、`kernel_type`、`alternate_kernel_types`（详见表 2）。
- 性能数据文件路径规范：`{设备名}/vllm_ascend/vllm{vllm版本}_torch{pytorch版本}_cann{CANN版本}/{KernelType}.csv` 与 `{设备名}/hccl/{CANN版本}/*.csv`。

### 未涉及内容

- 具体哪些 `KernelType` 名/CSV 字段定义、采样条件、机器型号等：原文未涉及。
- 如何生成/灌入 `op_mapping.yaml` 与 `{KernelType}.csv` 的工具链：原文未涉及。
- `InterpolatingDataSource` 与"外推"能力的具体算法：原文标注"未来扩展"，未给出具体实现。
- `accepted_miss` 中 `<reason>` 的合法取值清单：原文未涉及。
