# Vision Encoder (ViT) CUDA Graphs

> 仓 `vllm` · 路径 `docs/design/cuda_graphs_multimodal.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm/docs/design/cuda_graphs_multimodal.md

# Vision Encoder (ViT) CUDA Graphs — 深度解读

---

## 【定位】

本文档描述 vLLM 将 CUDA Graphs 机制从「decoder (语言模型) forward pass」扩展到「vision encoder (ViT) forward pass」的能力，并进一步支持 DeepSeek-OCR 这类「双塔 (two-tower) 视觉编码器」的多路径 (multi-path) graph 捕获与回放，从而消除 ViT 在 host 端的 CUDA kernel launch 开销。

---

## 【技术要点】

1. **Encoder 与 Decoder 独立捕获 (Orthogonal)**：Encoder CUDA Graphs 与 Decoder CUDA Graphs 解耦，可同时启用。前者捕获 ViT 等视觉编码器执行（如 Qwen3-VL 的 ViT），后者捕获语言模型执行（见 `cuda_graphs.md`）。

2. **Budget-Based 捕获策略**：在模型初始化阶段按多个 token budget 级别预捕获完整 encoder 前向图。默认预算示例：`[2048, 4096, 8192, 13824]`。预算由 `get_encoder_cudagraph_budget_range()` 提供的范围按 2 的幂自动生成，**最大预算即使不落在 2 的幂边界上也会被强制包含**。用户可通过 `CompilationConfig.encoder_cudagraph_token_budgets` 显式指定。

3. **共享 `max_batch_size`**：所有 budget 共享相同的最大批大小（图像数），仅 token 容量不同。每个 `BudgetGraphMetadata` 包含 `token_budget`、`max_batch_size`、`max_frames_per_batch`、`graph`、`input_buffers`、`output_buffer` 六项核心字段。

4. **Greedy Bin-Packing + Smallest-Fitting Budget**：运行时按 `output_tokens` 升序排序图像，按"最大 budget + 最大 batch_size"双重约束贪心打包成 sub-batch；子批确定后在该 sub-batch 总 token 上选择**最小**适配 budget 回放。超出全部 budget 的图像回退到 eager 执行。

5. **双塔 Multi-Path 捕获 (DeepSeek-OCR 范式)**：为「全局图像路径 (SAM)」与「局部 patch 路径 (CLIP)」独立捕获 graph：
   - **Global path 预算示例**：`[272, 544, 1088, 2176, 4352, 8704, 13824]`，每张全局图像产出 **272 tokens**。
   - **Local path 预算示例**：`[0, 100, 200, 400, 800, 1600, 3200, 6400, 12800, 13824]`，每个局部 patch 产出 **100 tokens**；含 `0` budget 时由 `allow_zero_tokens=True` 启用，用于处理 ≤ **640×640** 的纯全局图像（不产生 local patch）。

6. **Runtime Checkable 协议 + 模块化接口**：模型通过实现 `SupportsEncoderCudaGraph` 协议 opt-in；管理由 `EncoderCudaGraphManager` 统一负责 capture / replay / greedy packing / data-parallel 调度；每个输入项由 `EncoderItemSpec` 描述（含 `path_output_tokens` 映射每条路径的贡献）。

---

## 【关键机制与数据】

### 工作原理

- **捕获阶段 (Initialization-time)**：
  1. 模型在 `__init__` 时为若干 budget 级别各执行一次「warmup + `torch.cuda.graph` capture」，将 ViT 前向图与对应的 I/O buffer 一起固化下来。
  2. 对 multi-path 模型，`EncoderCudaGraphConfig.paths` 中每条路径独立生成 budget 集合并独立捕获，存放在 `budget_graphs["global"]` / `budget_graphs["local"]` 字典下。

- **回放阶段 (Runtime)**：
  1. 调用 `prepare_encoder_cudagraph_replay_buffers()` 由实际 batch 输入计算 buffer 值（含 `pixel_values` 与预计算 metadata）。
  2. **清零** 预分配的 `input_buffers`，再 slice-copy 回放值。
  3. 触发 CUDA Graph `replay()`。
  4. **必须 clone** `output_buffer`（因 buffer 在多次 replay 间被复用）。

- **触发动机（原文）**：「Vision encoder inference incurs CUDA kernel launch overhead on the host side. The overhead is more significant when the batch size is small or image size is small.」即小 batch、小图像场景下 host launch 开销占比显著，graph replay 可显著摊销。

- **Multi-path 必要性（原文）**：「Capturing a single monolithic graph for both paths would significantly reduce packing efficiency.」因为 global (272 tok/图) 与 local (100 tok/patch) 拥有**完全独立的 token profile**，单图无法高效混合 packing。

### 性能数据
原文未提供具体数字（如加速比、吞吐量提升百分比等）。

---

## 【表格解读】

### 表格 1：Model × Feature（架构 × 特性支持矩阵）

> **符号说明（原文）**：✅︎ = Full compatibility； = Partial compatibility；❌︎ = No compatibility； = Unknown or TBD

| Architecture | Models | CG for Image | CG for Video | Multi-Path Graph |
| ------------ | ------ | ------------ | ------------ | --------------- |
| `DeepseekOCRForCausalLM` | `DeepSeek-OCR` | ✅︎ | ❌︎ | ✅︎ |
| `Ernie4_5_VLMoeForConditionalGeneration` | `ERNIE-4.5-VL` | ✅︎ | ❌︎ | ❌︎ |
| `Gemma3ForConditionalGeneration` | `Gemma3` | ✅︎ | ❌︎ | ❌︎ |
| `Glm4vForConditionalGeneration` | `GLM-4.1V, GLM-4.6V-Flash` | ✅︎ | ✅︎ | ❌︎ |
| `Gemma4ForConditionalGeneration` | `Gemma-4` | ✅︎ | ✅︎ | ❌︎ |
| `InternVLChatModel` | `InternVL3.5`, `InternVL3`, `InternVL2.5`, `InternVL2` | ✅︎ | ✅︎ | ❌︎ |
| `KimiVLForConditionalGeneration` | `Kimi-VL` | ✅︎ | ❌︎ | ❌︎ |
| `Llama4ForConditionalGeneration` | `Llama 4` | ✅︎ | ❌︎ | ❌︎ |
| `Qwen2VLForConditionalGeneration` | `Qwen2-VL` | ✅︎ | ✅︎ | ❌︎ |
| `Qwen2_5_VLForConditionalGeneration` | `Qwen2.5-VL` | ✅︎ | ✅︎ | ❌︎ |
| `Qwen3VLForConditionalGeneration` | `Qwen3-VL` | ✅︎ | ✅︎ | ︎ |
| `Qwen3_5ForConditionalGeneration` | `Qwen3.5`, `Qwen3.6` | ✅︎ | ✅︎ | ❌︎ |
| `Qwen3_5MoeForConditionalGeneration` | `Qwen3.5-MoE`, `Qwen3.6-MoE` | ✅︎ | ✅︎ | ❌︎ |
| `Step3VLForConditionalGeneration` | `Step3-VL` | ✅︎ | ❌︎ | ✅︎ |

**逐行解读**：

- **`DeepSeek-OCR` 与 `Step3-VL`** 是**唯二**支持 `Multi-Path Graph` ✅︎ 的模型——前者是文档明确点名的两塔架构（SAM+CLIP dynamic tiling），后者未在文档正文中详细解释为何需多路径（属于 TBD 信息）。
- **`Qwen3.5` / `Qwen3.6` / `Qwen3.5-MoE` / `Qwen3.6-MoE`** 类（`Qwen3_5*`）是较新的多模态架构，已支持图像 + 视频双模态的 encoder graph，但尚未开启 multi-path。
- **`Llama 4`**、**`Kimi-VL`**、**`Gemma3`**、**`ERNIE-4.5-VL`**、**`DeepSeek-OCR`** 均**不支持视频** (`CG for Video = ❌︎`)，这与其模型架构侧重图像理解有关。
- **`GLM-4.1V` / `GLM-4.6V-Flash`** 与 **`Gemma-4`**、**`InternVL2/2.5/3/3.5`**、**`Qwen2-VL` / `Qwen2.5-VL` / `Qwen3-VL`** 覆盖了目前**图像 + 视频双模态全兼容**（两列均为 ✅︎）的主流模型家族。

### 表格 2：Model × Hardware（架构 × 硬件支持矩阵）

| Architecture | NV Blackwell | NV Ampere | AMD MI300X | AMD MI350X / MI355X |
| ------------ | ---------------- | ------------- | -------------- | --------------------- |
| `DeepseekOCRForCausalLM` | ✅︎ | ✅︎ | ❔ | ✅︎ |
| `Ernie4_5_VLMoeForConditionalGeneration` | ✅︎ | ✅︎ | ❔ | ✅︎ |
| `Gemma3ForConditionalGeneration` | ✅︎ | ✅︎ | ❔ | ✅︎ |
| `Glm4vForConditionalGeneration` | ✅︎ | ✅︎ | ❔ | ✅︎ |
| `Gemma4ForConditionalGeneration` | ✅︎ | ✅︎ | ❔ | ✅︎ |
| `InternVLChatModel` | ✅︎ | ✅︎ | ❔ | ✅︎ |
| `KimiVLForConditionalGeneration` | ✅︎ | ✅︎ | ❔ | ✅︎ |
| `Llama4ForConditionalGeneration` | ✅︎ | ✅︎ | ❔ | ✅︎ |
| `Qwen2VLForConditionalGeneration` | ✅︎ | ✅︎ |  | ✅︎ |
| `Qwen2_5_VLForConditionalGeneration` | ✅︎ | ✅︎ | ❔ | ✅︎ |
| `Qwen3VLForConditionalGeneration` | ✅︎ | ✅︎ | ❔ | ✅︎ |
| `Qwen3_5ForConditionalGeneration` | ✅︎ | ✅︎ | ❔ | ✅︎ |
| `Qwen3_5MoeForConditionalGeneration` | ✅︎ | ✅︎ | ❔ | ✅︎ |
| `Step3VLForConditionalGeneration` | ✅︎ | ✅︎ | ❔ | ✅︎ |

**逐行解读**：

- 在 NV Blackwell / NV Ampere 上**全部架构均 ✅︎**——表明 NVIDIA 是当前测试覆盖最完整的两类硬件。
- **AMD MI300X 列为 ❔**（Unknown/TBD），意味着尚未在该硬件上完成 Encoder CUDA Graph 的验证测试。
- **AMD MI350X / MI355X 全列 ✅︎**——结合原文 note："Encoder CUDA Graph has also been tested with AMD MI350X (gfx950) used `--mm-encoder-attn-backend=FLASH_ATTN` (the ROCm default)"，可知该验证基于 `gfx950` (MI350X) + FA backend 完成。
- 整体硬件覆盖呈「**NV 全 / AMD 仅 MI350X 系**」的不对称态势，文档明确存在 **AMD 验证缺口**。

---

## 【公式解读】

原文无数学公式（无 LaTeX 表达式）。但存在一段 Python dataclass 伪代码，作为核心数据结构的形式化定义，逐字保留如下：

```python
@dataclass
class BudgetGraphMetadata:
    token_budget: int
    max_batch_size: int
    max_frames_per_batch: int
    graph: torch.cuda.CUDAGraph
    input_buffers: dict[str, torch.Tensor]  # e.g. pixel_values, embeddings, seq metadata
    output_buffer: torch.Tensor      # encoder hidden states
```

**符号含义逐项解读**：

| 字段 | 类型 / 值域 | 作用 |
|---|---|---|
| `token_budget` | `int` | 该 graph 的 token 容量上限（例如 `2048`、`4096` 等），是回放时**最小适配**匹配的标尺。 |
| `max_batch_size` | `int` | 该 graph 可容纳的**图像/样本数**上限。所有 budget 共享同一最大值。 |
| `max_frames_per_batch` | `int` | 单批次的最大帧数，专用于视频多帧输入场景（如 Qwen-VL）。 |
| `graph` | `torch.cuda.CUDAGraph` | 预先捕获的 CUDA Graph 对象，运行时直接 `replay()`。 |
| `input_buffers` | `dict[str, torch.Tensor]` | 预分配的输入张量字典，例如 `pixel_values`、`embeddings`、序列 metadata 等——**回放前必须先清零再 slice-copy**。 |
| `output_buffer` | `torch.Tensor` | 编码器 hidden states 输出张量，**因跨 replay 复用，必须 clone 出来**。 |

---

## 【关联】

根据文末与正文内出现的内部链接与组件引用，本设计与 vLLM 生态中下列模块存在上下游关系：

1. **上游基础机制** — [cuda_graphs.md](cuda_graphs.md)：本文是 `cuda_graphs.md` 的"encoder 侧扩展专题"。原 `cuda_graphs.md` 文档描述 decoder forward pass 的 graph 捕获与回放；本文复用其 capture / replay 抽象但将其作用域前移到 ViT。文中明确："Encoder graphs capture the vision encoder execution... while decoder graphs capture the language model execution as described in the [CUDA Graphs design document](cuda_graphs.md)."

2. **上游 PR 来源** —
   - <https://github.com/vllm-project/vllm/pull/35963>：基础 encoder CUDA Graph 功能的合入 PR。
   - <https://github.com/vllm-project/vllm/pull/43586>：multi-path / dual-path graph 模式（DeepSeek-OCR 范式）的合入 PR。

3. **实现组件之间的层级关系**：
   - **`EncoderCudaGraphManager`** (`vllm.v1.worker.encoder_cudagraph`)：顶层编排器，调度的"调度层"。
   - **`SupportsEncoderCudaGraph`** (`vllm.model_executor.models.interfaces`)：模型侧 opt-in 协议（runtime-checkable Protocol），决定哪些模型类支持该特性。
   - **`EncoderItemSpec`** (`vllm.v1.worker.encoder_cudagraph_defs`)：数据描述层，描述单个输入项（image / video）的输入尺寸与输出 token 数。
   - **`BudgetGraphMetadata`** (`vllm.v1.worker.encoder_cudagraph`)：资源层，持有具体某 budget 级别的 graph 与 I/O buffer。
   - **`EncoderCudaGraphConfig.paths` → `EncoderCudaGraphPathConfig`**：配置层，定义每条路径的捕获策略（含 `allow_zero_tokens=True` 等开关）。

4. **正交关系** — Encoder Graph 与 Decoder Graph 是**完全独立**的两套机制，可同时启用也可单独启用；multi-path graph 又是 Encoder Graph 的**子模式**，受同一 greedy packing 循环的多重约束。

5. **与硬件/后端的耦合** — 通过 `--mm-encoder-attn-backend` 与 attention backend（FLASH_ATTN / FLASHINFER / FA2 / FA3）耦合，是 graph capture **能否成功**的关键依赖；ROCm 端默认 `FLASH_ATTN`。

---

## 【使用方法】

### 启用方式（原文摘录）

- **默认行为**：Encoder CUDA Graphs 默认随 vLLM 的 CUDA Graph 框架启用（前提是模型实现 `SupportsEncoderCudaGraph` 协议）。
- **自定义预算**：`CompilationConfig.encoder_cudagraph_token_budgets`（用户显式覆盖默认的 power-of-2 预算）。
- **覆盖 budget 范围**：模型通过 `get_encoder_cudagraph_budget_range()` 提供预算范围，系统按 2 的幂在该范围内自动生成；最大预算**总是被包含**。
- **Multi-Path 路径配置**：`EncoderCudaGraphConfig.paths` → `EncoderCudaGraphPathConfig`；启用 `allow_zero_tokens=True` 以支持 0-token batch（如 DeepSeek-OCR 的纯全局图像场景）。

### Attention Backend（必须）

```bash
# Blackwell GPU（推荐，已测试）
--mm-encoder-attn-backend=FLASH_ATTN
--mm-encoder-attn-backend=FLASHINFER

# Qwen2-VL / Qwen2.5-VL 仅 FA2、FA3 已测试

# AMD MI350X (gfx950)，ROCm 默认
--mm-encoder-attn-backend=FLASH_ATTN
```

### 验证硬件清单（原文）

| 硬件 | 状态 | 备注 |
|---|---|---|
| NVIDIA Blackwell | ✅︎ 已测试 | + FLASH_ATTN / FLASHINFER |
| NVIDIA Ampere | ✅︎ 已测试 | — |
| AMD MI350X / MI355X | ✅︎ 已测试 | gfx950 + FLASH_ATTN (ROCm default) |
| AMD MI300X | ❔ TBD | 尚未完成 Encoder CUDA Graph 验证 |

### 注意事项

- Encoder 与 Decoder CUDA Graph **可同时启用**（彼此正交）。
- 超出所有 budget 的图像**自动回退到 eager 执行**，无需手动配置。
- 同一 `EncoderCudaGraphConfig.paths` 中每条路径独立捕获、独立预算；同一 batch 中所有路径的 packing 约束会被**同时**校验（参见原文 "Multi-path greedy packing" 一节，**原文在该节末尾被截断**，未给出 `EncoderItemSpec.path_output_tokens` 的完整使用细节与最终数据流结束步骤）。
