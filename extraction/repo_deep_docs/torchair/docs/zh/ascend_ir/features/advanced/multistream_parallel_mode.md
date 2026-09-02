# 多流并行模式配置功能

> 仓 `torchair` · 路径 `docs/zh/ascend_ir/features/advanced/multistream_parallel_mode.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/torchair/docs/zh/ascend_ir/features/advanced/multistream_parallel_mode.md

# 「多流并行模式配置功能」文档深度解读

---

## 【定位】

这篇文档解决的是：在 TorchAir 图模式场景下，如何通过配置 GE 图引擎的多流并行策略，让引擎自动分析算子依赖关系并分配到多条流上并行执行，从而提升推理图的执行性能。本质是 GE 引擎 `ge.autoMultistreamParallelMode` 选项在 TorchAir 框架层的暴露与使用方法说明。

---

## 【技术要点】

1. **多流并行的三种算法模式 + 一种关闭模式**：
   - `cv`：Cube 算子与 Vector 算子并行执行。
   - `LoadBalance:N`：负载均衡算法，N 为最大流数量，正整数，**取值范围 [1, 64]**，超出实际可用核数性能可能降低。
   - `MainStream:N`：主流算法，串行算子在主流上执行，可并行算子分布到其他流，N 同样为 [1, 64] 的正整数。
   - `None`（默认值）：不启用任何多流并行优化。

2. **静态与动态 Shape 行为差异**：静态 Shape 场景下配置直接生效；动态 Shape 场景下须先通过环境变量 `ENABLE_DYNAMIC_SHAPE_MULTI_STREAM=1` 使能，再通过本文参数选择具体算法。

3. **使用范围限制**：该参数**仅限于推荐类型网络使用**，且**不支持裸 `LoadBalance`（不携带 N）的配置**，必须显式写为 `LoadBalance:N`。

4. **配置入口**：通过 `torchair.get_npu_backend` 中的 `compiler_config` → `config.ge_config.multistream_parallel_mode` 字符串字段传入，字符串类型。

5. **生效层级**：仅适用于 GE 图模式场景（即通过 `torch.compile(model, backend=npu_backend)` 走图执行路径时）。

6. **性能边界提示**：原文明确"N 取值超过了实际可用核数，性能可能会降低"——这意味着参数设置需与 NPU 硬件拓扑匹配，并非越大越好。

---

## 【关键机制与数据】

**工作原理**（原文整合）：
- 开发者配置多流并行模式的自动分配策略后，由 **GE 图引擎**自动分析节点（算子）依赖关系，并将可并行的算子分配到不同流上。
- 三种模式对应不同的分配启发式：
  - `cv`：针对昇腾 NPU 的硬件特性，将 Cube 类（矩阵计算）与 Vector 类（向量计算）算子分到不同流并行。
  - `LoadBalance:N`：把所有算子尽量均匀铺到 N 条流上，目标是负载均衡。
  - `MainStream:N`：保留主流承载串行算子链，其余并行分支分到 N-1 条副流。

**数据流**（原文整合）：
- 用户代码 → `CompilerConfig` → `ge_config.multistream_parallel_mode` 字符串 → `get_npu_backend` 编译为 GE 图 → GE 引擎读 `ge.autoMultistreamParallelMode` → 图调度阶段按算法切流。

**性能数据**：原文未给出量化性能数据，仅有"提升图执行性能"的定性描述，以及"N 超过实际可用核数性能可能降低"的反向警告。

---

## 【表格解读】

**表 1　参数说明**（逐字还原）：

| 参数名 | 说明 |
|---|---|
| `multistream_parallel_mode` | 多流并行模式的自动分配策略，字符串类型。取值如下：<br>- **cv**：开启 Cube 算子与 Vector 算子的并行执行功能。<br>- **LoadBalance:N**：负载均衡算法，将所有算子均匀分布在 N 条流上执行，N 为正整数，取值范围 [1, 64]。<br>- **MainStream:N**：主流算法，串行算子分布在主流上执行，其他可并行算子分布在其他流上执行，N 为正整数，取值范围 [1, 64]。<br>- **None（默认值）**：不启用任何多流并行优化。 |

**逐行解读**：
- **参数名行**：该参数挂在 `CompilerConfig.ge_config` 之下，类型是字符串，所以 `LoadBalance:8` 这种"算法名+冒号+数字"的复合字符串必须严格匹配大小写与分隔符。
- **cv 取值**：硬件导向的切分，专门利用昇腾 NPU 中 Cube 与 Vector 单元可并行工作的特性，适合计算密集型网络中两类算子混杂的场景。
- **LoadBalance:N 取值**：N 限定 1–64，算法目标是让算子在流之间尽可能均匀分布，适合整体算子粒度相近、无明显串行链路的网络；若 N 超过硬件核数反而引入调度开销。
- **MainStream:N 取值**：保留一条主流承载固有串行依赖（如数据预处理→主计算→后处理这种链式结构），其他可并行分支用副流跑，N 同样受 1–64 约束。
- **None 默认值**：作为兜底，保证不启用多流并行优化，行为与传统单流图执行一致。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **上游/入口 API**：本文配置通过 `torchair.get_npu_backend` 注入，故与同仓 `../../api/torchair/get_npu_backend.md`（文档内内部链接）所描述的 `CompilerConfig` 体系直接耦合——`ge_config` 是 `CompilerConfig` 下专门承载 GE 后端选项的子对象。
- **环境变量依赖**：动态 Shape 场景下依赖 `ENABLE_DYNAMIC_SHAPE_MULTI_STREAM`，该变量定义见《CANN 环境变量参考》（外部链接 `https://hiascend.com/document/redirect/CannCommunityEnvRef`），属于 CANN 软件栈层面的开关，需先于本文参数使能。
- **底层引擎**：参数语义直接对应 GE 图引擎的 `ge.autoMultistreamParallelMode` 选项，因此本文与 GE 图编译流水线、`torch.compile` 后端注册路径密切相关；脱离 GE 图模式（即走算子直调）则本参数无效。
- **同模块其他特性**：作为 "advanced" 分类下的图执行优化特性，与图融合、内存优化等其他 `ge_config.*` 配置项并列存在，可组合使用。

---

## 【使用方法】

**启用方式（原文示例，仅供参考不支持直接拷贝运行）**：

```python
import torch_npu, torchair
config = torchair.CompilerConfig()
# 配置多流并行模式为负载均衡算法，使用 8 条流
config.ge_config.multistream_parallel_mode = "LoadBalance:8"
npu_backend = torchair.get_npu_backend(compiler_config=config)
opt_model = torch.compile(model, backend=npu_backend)
```

**配置项与命令**：
- **配置项**：`config.ge_config.multistream_parallel_mode`，字符串类型，取值 `"cv"` / `"LoadBalance:N"` / `"MainStream:N"` / `"None"`，N 为 [1, 64] 正整数。
- **动态 Shape 前置环境变量**：`ENABLE_DYNAMIC_SHAPE_MULTI_STREAM=1`（需在配置本文参数前设置）。
- **编译入口**：`torch.compile(model, backend=npu_backend, dynamic=False, fullgraph=True)`——文档示例中显式设置了 `dynamic=False`（静态 Shape）和 `fullgraph=True`。
- **使用示例中的辅助开关**：示例还启用了 `config.debug.graph_dump.type = "pbtxt"` 用于导出图结构以便调试，并非功能必需项。

原文未涉及更多关于不同模式在不同网络上的推荐选型或基准测试数据。
