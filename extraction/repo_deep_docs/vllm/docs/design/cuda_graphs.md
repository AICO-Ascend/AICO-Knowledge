# CUDA Graphs

> 仓 `vllm` · 路径 `docs/design/cuda_graphs.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm/docs/design/cuda_graphs.md

# vLLM CUDA Graphs 设计文档深度解读

## 【定位】
本文档系统阐述 vLLM v1 中**重构后的 CUDA Graphs 架构**——通过把 CUDA Graph 捕获与 torch.compile 解耦、引入 `CudagraphDispatcher` 中央调度器和 `BatchDescriptor` 分发键，解决原有方案中"编译与 CUDA Graph 紧耦合、全有/全无、注意力后端兼容性混乱"的问题，从而在不同 batch 组成（uniform-decode / 非均匀 prefill-mixed）和不同后端能力下灵活、可扩展地选择 CUDA Graph 运行时模式。

---

## 【技术要点】

1. **统一的模式开关 `cudagraph_mode`**（位于 `CompilationConfig.cudagraph_mode`），提供五种枚举值：`NONE`、`PIECEWISE`、`FULL`、`FULL_DECODE_ONLY`、`FULL_AND_PIECEWISE`，单模式与对偶模式共存。
2. **CUDA Graph 捕获与编译正交化**：同一份编译后的图既可被 piecewise 捕获，也可被 full 捕获；full CUDA Graph 捕获不再强依赖 piecewise 编译。
3. **`CudagraphDispatcher` 中央调度器**：维护 `FULL` 与 `PIECEWISE` 两套有效 dispatch key 集合，运行时根据 batch 组成动态选择具体运行时模式与对应 key。
4. **`BatchDescriptor` 作为分发键**（`vllm.forward_context.BatchDescriptor`），由 `num_tokens`、`num_reqs`、`uniform`、`has_lora` 四个字段构成，最小化地唯一标识一个 (padded) batch。
5. **`CUDAGraphWrapper`**（`vllm.compilation.cuda_graph`）：负责 wrapped callable 上的 CUDA Graph capture & replay，同时支持 full 和 piecewise。
6. **注意力后端兼容性与自动降级**：例如 FlashAttention 3 支持 full cudagraphs；Flashinfer、FlashMLA、Mamba 仅支持 uniform decode；不支持时调度器会自动"downgrade"到最近支持的模式（如 `FULL` → `FULL_AND_PIECEWISE`（如 piecewise 编译启用）或 `FULL_DECODE_ONLY`）。Cascade attention 不与 cudagraph 兼容，但与所有 cudagraph 模式配置都兼容；若使用 cascade attention 且 PIECEWISE 可用则总是分发到 `PIECEWISE`，否则 `NONE`。

---

## 【关键机制与数据】

- **uniform decode 定义**（原文）：
  - 纯 decode 时 `max_query_len=1`；
  - speculative decode 时 `max_query_len=1+num_spec_tokens`；
  - 反之则为 **non-uniform**（即 prefill 或混合 prefill-decode）。
- **历史痛点（原文）**：
  - 初始 piecewise 编译通过排除 attention 实现 piecewise cudagraph capture；
  - 后来加入"full cudagraphs"以进一步降低 latency，但要求 attention 支持 cudagraph；
  - 二者紧耦合 → "all-or-nothing"体验，且许多 attention 后端尚未准备好 unified full CUDA Graphs 捕获（仅 FlashAttention 3 支持），或只支持 pure decode（Flashinfer/FlashMLA/Mamba 等）。
- **设计目标（原文）**：
  - 对 prefill/mixed 与 (uniform-)decode batch 分别显式感知并独立捕获 CUDA Graph；
  - 将 CUDA Graph 捕获逻辑与编译解耦（用同一份编译图捕获 piecewise 和 full cudagraph，full cudagraph 捕获可不依赖编译）；
  - 在运行时按 batch 组成在 full 与 piecewise 间 dispatch；
  - 集中式控制以降低代码复杂度并提升可扩展性。
- **调度键的最小化目标（原文）**：用尽可能少的字段唯一标识一个对应到某条 CUDA Graph 的 (padded) batch。
- **cascade attention 处理（原文）**：使用 cascade attention 的 batch 若 `PIECEWISE` 可用则总是被分发到 `PIECEWISE`，否则 `NONE`。
- **自动降级示例（原文）**：
  - 仅支持 pure decode/uniform 的后端 → `FULL` 降级为 `FULL_AND_PIECEWISE`（如 piecewise 编译启用）或 `FULL_DECODE_ONLY`。
- **架构对比（原文）**：
  - **Before**：CUDA Graphs 逻辑与编译逻辑紧耦合在 vLLM `PiecewiseBackend` 内，CUDA Graphs 仅通过 `batch_size` "隐式"分发；
  - **After**：CUDA Graphs 逻辑被抽出到 `CUDAGraphWrapper`（同时承担 full 与 piecewise 能力），并通过 runtime mode + `BatchDescriptor` 作为 dispatch key，由 `CudagraphDispatcher` **显式**分发。
- **设计来源**：本文内容基于 PR <https://github.com/vllm-project/vllm/pull/20059> 的最后一次 commit；`BatchDescriptor` 的扩展方向（如新增 `uniform_query_len`）见 PR <https://github.com/vllm-project/vllm/pull/23679>（原文引用）。
- 性能数据/吞吐数字：原文未涉及具体 benchmark 数字。

---

## 【表格解读】

**原文无表格**。文档中关于五种 CUDA Graph 模式的关键配置信息是以**枚举列表 + 解释段落**的形式给出（而非 markdown 表格）。以下用表格形式对原文枚举内容做"逐字还原 + 解读"以辅助理解：

| 模式 | 类型 | 原文定义（行为） | 适用场景 / 备注（原文） |
|---|---|---|---|
| `NONE` | 单模式 | 关闭 CUDA Graphs | "Good for debugging." |
| `PIECEWISE` | 单模式（过去默认） | attention 或其他与 CUDA Graphs 不兼容的操作保持 eager，其余进入 CUDA Graphs | "the most flexible"；需要 piecewise 编译 |
| `FULL` | 单模式 | 只为 non-uniform batch 捕获 full CUDA Graphs；uniform-decode batch 复用相同 `batch_size` 的 non-uniform batch 的 CUDA Graph（兼容性） | "can be good for small models or workloads with small prompts" |
| `FULL_DECODE_ONLY` | 对偶模式（新） | uniform decode 用 full CUDA Graph；prefill/mixed 等不用 cudagraph | "suitable for decode instances in a P/D setup where prefill is not as important"；可省去 `PIECEWISE` CUDA Graphs 所需显存 |
| `FULL_AND_PIECEWISE` | 对偶模式（新，默认） | uniform decode 用 full CUDA Graph，其余用 piecewise CUDA Graphs | "generally the most performant setting, especially for low latency with small models or MoEs"；显存占用最大、capture 耗时最长 |

**默认行为（原文）**：v1 + piecewise 编译时默认 `FULL_AND_PIECEWISE`（pooling 模型仍为 `PIECEWISE`）；否则（如 piecewise 编译不可用）默认 `NONE`。

**调度器视角（原文）**：`NONE`、`PIECEWISE`、`FULL` 三个单模式既可作为最终运行时模式，也作为 dispatcher 可分发的成员模式；对偶模式的总是在其成员模式之间（必要时加 `NONE`）按 batch 组成动态分发。

---

## 【公式解读】

**原文无数学公式（LaTeX）**，但含一段**关键 Python 类型原型**（`BatchDescriptor`），按原文逐字保留并逐字段解读：

```python
class BatchDescriptor(NamedTuple):
    num_tokens: int
    num_reqs: int
    uniform: bool = False
    has_lora: bool = False
```

| 字段 | 类型 | 默认值 | 含义与作用（原文） |
|---|---|---|---|
| `num_tokens` | `int` | — | (padded) token 长度；可填填充后的 token 数，作为分发键的核心尺寸量 |
| `num_reqs` | `int` | — | 请求数量；与 `num_tokens` 共同唯一标识一个 padded batch |
| `uniform` | `bool` | `False` | 标识 batch 内所有请求是否具有相同的 query 长度；许多 attention 后端仅在 batch uniform 时才支持 full cudagraphs |
| `has_lora` | `bool` | `False` | 标识是否含 LoRA 适配，用于对带 LoRA 的 batch 与普通 batch 区分 dispatch key |

**补充说明（原文）**：
- pure decode batch 是 uniform 的，但 `num_tokens` 不一定等于 1，例如 spec-decode 的验证阶段"decode" batch 的 query 长度为 `1+num_spec_tokens`，此时 `num_tokens == num_reqs`。
- 原型未来可能扩展更多字段，如 `uniform_query_len`（支持多种 uniform decode 长度配置，参见 PR #23679），或为多模态等非 token-length 感知的输入模型增加必要字段。

---

## 【关联】

- **`torch_compile.md`**：本文明确把"CUDA Graphs"定位为 v1 中**超越** torch.compile 集成的进一步能力。新的 CUDA Graphs 架构建立在 piecewise 编译之上，并刻意将 CUDA Graph 捕获与编译逻辑解耦（即"CUDA Graph 能力与编译正交"），但仍依赖 `CompilationConfig.cudagraph_mode` 入口及 piecewise 编译基础设施。
- **`cuda_graphs_multimodal.md`**（即"Vision Encoder (ViT) CUDA Graphs"）：本文在目录中将其作为姊妹章节单独列出，针对多模态 ViT 场景的 CUDA Graph 捕获设计，且与本文中提到的 `BatchDescriptor` 未来扩展方向（非 token-length 感知的输入，例如某些多模态输入）直接相关——即多模态场景可能推动 `BatchDescriptor` 增加额外字段以唯一标识 batch。
- **注意力后端生态（原文引用）**：FlashAttention 3（支持 full cudagraphs）、Flashinfer / FlashMLA / Mamba（仅支持 pure decode CUDA Graph）、cascade attention（不 cudagraph 兼容，但与所有模式配置兼容）。这些后端决定了 dispatcher 的可降级路径。
- **PR 链路**：
  - 设计主体基于 <https://github.com/vllm-project/vllm/pull/20059>；
  - `BatchDescriptor` 扩展（`uniform_query_len` 等）路线图见 <https://github.com/vllm-project/vllm/pull/23679>。

---

## 【使用方法】

原文给出的启用与配置方式如下（按原文逐字保留要点）：

- **唯一开关**（原文）：在 `CompilationConfig.cudagraph_mode` 中调参 `CUDAGraphMode`（`vllm.config.compilation.CUDAGraphMode`）。
- **可选值**（原文枚举）：`NONE`、`PIECEWISE`、`FULL`、`FULL_DECODE_ONLY`、`FULL_AND_PIECEWISE`。
- **默认值**（原文）：
  - v1 + piecewise 编译：默认 `FULL_AND_PIECEWISE`（pooling 模型仍为 `PIECEWISE`）；
  - 其他情况（如 piecewise 编译不可用）：默认 `NONE`。
- **典型场景选型指引**（原文）：
  - 调试 → `NONE`；
  - 最高灵活度（兼容所有 attention 后端） → `PIECEWISE`；
  - 小模型 / 小 prompt 工作负载 → `FULL`；
  - P/D 分离中仅承担 decode、且希望节省显存 → `FULL_DECODE_ONLY`；
  - 低延迟小模型 / MoE 等极致性能 → `FULL_AND_PIECEWISE`（显存与 capture 时间代价最高）。
- **关于命令行的具体启动参数（如 `--cudagraph-mode` 之类的命令行 flag）**：原文未涉及具体 CLI 命令/参数名称，仅说明配置位于 `CompilationConfig.cudagraph_mode`。

## 图文联合解读

- `previous_design.png`: **图解读：**
1. **结构**：上层model经torch.compile切分为多个Piecewise Backend（submod+attn），底层经"Dispatched by Bs"调度器分流，可走"Piecewise cudagraph"（cg与eager交替）或"No cudagraph"（纯eager）两条路径。
2. **技术结论**：CUDA Graphs捕获与torch.compile解耦，attention不被编译，但可通过cg节点被图捕获；dispatcher按batch动态选模式。
3. **与文档关系**：图示佐证三论点——灵活cudagraph_mode配置、CUDA Graphs与编译正交、dispatcher按batch自动选取运行时模式。
- `current_design.png`: **图文联合解读：**

图示呈现CUDA Graphs的三种运行时模式：FULL模式下整个模型由单一`CUDAGphWrapper(mode=FULL)`捕获为整图执行；PIECEWISE模式经`torch.compile`拆分后，每个子模块(submod)由独立`CUDAGphWrapper`包裹，交替以cg/eager片段执行以避开attention的限制；NONE模式则纯eager。顶部Dispatcher依据`runtime_mode+key`自动派发。

论证了CUDA Graphs配置正交于torch.compile、可按batch灵活切换模式的核心结论，呼应文档"灵活cudagraph_mode配置"与"dispatcher按batch自动选模"的主张。
- `executor_runtime.png`: **图文联合解读：**

1. **图像内容**：图示按虚线分为三层流水线——**Input**（输入Batch经预处理）、**Plan**（检查"cg padding?"与"uniform_decode?"，生成`BatchDescriptor(num_tokens, uniform_decode)`作为`init_key`，送入"Cudagraph Dispatcher"做Dispatch）、**Execute**（通过`set_fw_ctx(runtime_mode, final_key)`设上下文后执行`self.model(input)`）。

2. **技术结论**：Dispatcher根据batch的token数与是否均匀解码，自动选择FULL/PIECE/NONE三种runtime mode及最终cudagraph key，实现"按batch自动匹配"的集中调度，把规划与执行解耦。

3. **与文档论点呼应**：对应文中"引入CUDA Graphs dispatcher作为中央控制器，按batch自动选取runtime模式与cudagraph"这一核心设计，证明cudagraph选择不再是静态配置，而是由运行时batch特征（uniform decode与否、padding与否）动态驱动，从而支持"与compilation正交"和"灵活cudagraph_mode配置"两个论点。
- `wrapper_flow.png`: **图文联合解读：**

1) **图示内容**：左侧展示模型前向的两条封装路径——FULL 模式直接包 `Model`，PIECEWISE 模式（仅 vLLM 编译启用时）经 `torch.compile → SplitGraph → PiecewiseBackend → Model Forward`；右侧为 `CUDAGraphWrapper.__call__()` 流程：先校验 Runtime Mode 是否匹配，再查 `cuda_graphs` 映射表（DispatchKey→GraphItem），命中则 Replay，未命中则 Capture。

2) **技术结论**：CUDA Graphs 捕获/重放与编译路径解耦，统一由 Dispatcher 按运行时模式与 batch key 自动路由，避免重复捕获开销。

3) **与论点呼应**：印证文档第 1、3 点——灵活的 `cudagraph_mode` 配置与中央调度器设计，使 FULL/PIECEWISE 模式可正交启用与自动选取。
