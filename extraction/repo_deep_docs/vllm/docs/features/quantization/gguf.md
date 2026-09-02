# GGUF

> 仓 `vllm` · 路径 `docs/features/quantization/gguf.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm/docs/features/quantization/gguf.md

# vLLM GGUF 支持特性文档深度解读

---

## 【定位】

这篇文档介绍 vLLM 中 **GGUF 量化模型推理支持** 的能力：如何通过 OOT（Out-Of-Tree）插件 `vllm-gguf-plugin` 安装并运行 GGUF 格式的量化模型（如 `Q4_K_M`），覆盖 CLI（`vllm serve`）和 Python（`LLM` 入口）两种调用方式，并强调当前主要用途是 **降低显存占用**，但仍属于高度实验性、未充分优化的特性。

---

## 【技术要点】

1. **插件化架构**：GGUF 支持已从 vLLM 主干迁出到 OOT 插件 `vllm-gguf-plugin`（GitHub: `vllm-project/vllm-gguf-plugin`），需先安装该插件才能服务 GGUF 模型，安装命令为 `uv pip install vllm-gguf-plugin`。

2. **模型加载格式 `repo_id:quant_type`**：直接从 HuggingFace 加载 GGUF 量化模型时使用 `仓库ID:量化类型` 格式，例如 `unsloth/Qwen3-0.6B-GGUF:Q4_K_M` 表示从 HuggingFace 加载该仓库中 Q4_K_M 量化变体。

3. **Tokenizer 推荐使用基模型**：强烈建议通过 `--tokenizer Qwen/Qwen3-0.6B` 显式指定使用基模型的 tokenizer，而非 GGUF 模型自带的 tokenizer，因为 GGUF → tokenizer 的转换耗时且不稳定，对 **大词表模型尤其明显**。

4. **Tensor Parallelism 支持**：通过 `--tensor-parallel-size 2` 开启 2 张 GPU 的张量并行推理，命令与 HF repo 加载方式组合使用。

5. **本地 GGUF 文件支持**：可使用 `wget` 下载 `.gguf` 文件后通过本地路径（`./Qwen3-0.6B-Q4_K_M.gguf`）加载，无需 HuggingFace 仓库。

6. **手动 config 兜底**：当 HuggingFace 无法将 GGUF 元数据转换为 config 时，可通过 `--hf-config-path Qwen/Qwen3-0.6B` 手动传入基模型的 HF 兼容 config。

7. **Python API 调用**：通过 `vllm.LLM(model="unsloth/Qwen3-0.6B-GGUF:Q4_K_M", tokenizer="Qwen/Qwen3-0.6B")` 实例化，配合 `SamplingParams(temperature=0.8, top_p=0.95)` 及 `llm.chat(conversation, sampling_params)` 调用对话式推理。

---

## 【关键机制与数据】

### 工作原理与数据流

- **GGUF 假设 HuggingFace 能将元数据转换为 config 文件**（原文：`GGUF assumes that HuggingFace can convert the metadata to a config file`），若 HF 不支持该模型，用户必须手动提供 hf-config-path。
- **当前定位是"降低显存占用"**（原文：`Currently, you can use GGUF as a way to reduce memory footprint`），文档未提及具体的吞吐量、时延或显存节省数字。
- **Tokenizer 数据路径**：原始 GGUF 模型内置 tokenizer 转换链路不稳定 → 推荐绕过它，直接复用基模型 tokenizer。

### 限制与稳定性

- **高度实验性**（原文：`highly experimental and under-optimized at the moment`）。
- **与其他特性可能不兼容**（原文：`it might be incompatible with other features`）。
- **遇到问题需上报 vLLM 团队**（原文：`please report them to the vLLM team`）。

### 性能 / 基准数据

原文未提供任何性能数字（如 tokens/s、显存节省百分比、量化精度对比等），本节不做推测。

---

## 【表格解读】

**原文无表格**。文档以命令块、warning/note 注示和一段 Python 代码示例为主要呈现形式，未列出参数表、性能对比表或配置矩阵。

---

## 【公式解读】

**原文无公式**。文档不涉及任何 LaTeX 公式或伪代码公式（量化机制、内存占用计算等内部细节均未在本文档中给出）。

---

## 【关联】

文档以"安装 OOT 插件"和"加载方式"为主线，涉及的上下游/关联模块有：

| 关联对象 | 关系 | 来源 |
|---|---|---|
| `vllm-gguf-plugin` (https://github.com/vllm-project/vllm-gguf-plugin) | GGUF 功能已迁出至该 OOT 插件，必须先安装 | 原文 note + 安装命令 |
| HuggingFace repo `unsloth/Qwen3-0.6B-GGUF` | 示例 GGUF 量化模型来源（Q4_K_M 变体） | 原文示例 |
| 基模型 `Qwen/Qwen3-0.6B` | 提供 tokenizer 与 `--hf-config-path` 兜底 config | 原文示例 |
| HuggingFace 平台元数据转换链路 | GGUF 默认依赖其将 GGUF metadata → config | 原文说明 |
| vLLM `vllm serve` CLI | 模型服务入口 | 原文命令 |
| vLLM Python `LLM` / `SamplingParams` | 离线推理入口 | 原文 Python 代码块 |

文档内未提供任何指向仓内其他 docs/ 模块（如 KV cache、Speculative Decoding、Other Quantization 方案如 AWQ/GPTQ）的内部链接，故不做进一步跨特性串联。

---

## 【使用方法】

### 1. 安装 OOT 插件（前置条件）

```bash
uv pip install vllm-gguf-plugin
```

### 2. CLI：从 HuggingFace 直接加载 + 基模型 tokenizer

```bash
vllm serve unsloth/Qwen3-0.6B-GGUF:Q4_K_M --tokenizer Qwen/Qwen3-0.6B
```

### 3. CLI：开启张量并行（2 GPU）

```bash
vllm serve unsloth/Qwen3-0.6B-GGUF:Q4_K_M \
   --tokenizer Qwen/Qwen3-0.6B \
   --tensor-parallel-size 2
```

### 4. CLI：使用本地 `.gguf` 文件

```bash
wget https://huggingface.co/unsloth/Qwen3-0.6B-GGUF/resolve/main/Qwen3-0.6B-Q4_K_M.gguf
vllm serve ./Qwen3-0.6B-Q4_K_M.gguf --tokenizer Qwen/Qwen3-0.6B
```

### 5. CLI：手动提供 hf-config-path 兜底

```bash
vllm serve unsloth/Qwen3-0.6B-GGUF:Q4_K_M \
   --tokenizer Qwen/Qwen3-0.6B \
   --hf-config-path Qwen/Qwen3-0.6B
```

### 6. Python：LLM 入口 + chat 对话

```python
from vllm import LLM, SamplingParams

conversation = [
    {"role": "system", "content": "You are a helpful assistant"},
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hello! How can I assist you today?"},
    {"role": "user", "content": "Write an essay about the importance of higher education."},
]

sampling_params = SamplingParams(temperature=0.8, top_p=0.95)

llm = LLM(
    model="unsloth/Qwen3-0.6B-GGUF:Q4_K_M",
    tokenizer="Qwen/Qwen3-0.6B",
)
outputs = llm.chat(conversation, sampling_params)

for output in outputs:
    prompt = output.prompt
    generated_text = output.outputs[0].text
    print(f"Prompt: {prompt!r}, Generated text: {generated_text!r}")
```

### 关键配置项汇总

| 配置项 / 参数 | 作用 | 原文依据 |
|---|---|---|
| `--tokenizer <repo>` | 指定基模型 tokenizer，避免 GGUF 自带 tokenizer 转换慢/不稳定 | 推荐用 base model tokenizer 的 warning |
| `--tensor-parallel-size N` | 张量并行 GPU 数（示例为 2） | TP 推理示例 |
| `--hf-config-path <repo>` | 当 HF 无法从 GGUF 元数据生成 config 时，手动提供 HF 兼容 config 路径 | 手动 config 说明 |
| `model="repo_id:quant_type"` | 量化类型选择（如 `Q4_K_M`） | HuggingFace 加载示例 |
| 插件 `vllm-gguf-plugin` | 提供 GGUF 模型加载/推理能力 | 安装说明 note |

> 注：原文未涉及如 `--quantization` 显式参数、`--dtype`、KV cache dtype、scheduler 选项等其他 vLLM 通用参数在 GGUF 路径下的特殊配置，故不列出。
