# GPTQModel

> 仓 `vllm` · 路径 `docs/features/quantization/gptqmodel.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm/docs/features/quantization/gptqmodel.md

# GPTQModel 文档深度解读

## 【定位】
这篇文档解决的是：**如何在 vLLM 中使用 ModelCloud.AI 的 GPTQModel 工具链创建 4-bit 或 8-bit 的 GPTQ 量化模型，并将其接入 vLLM 推理引擎运行**——重点覆盖安装、量化（quantize）、命令行运行、Python API 运行四个环节。

---

## 【技术要点】

1. **量化精度路径**：将模型从 BF16/FP16（16-bit）精度降至 INT4（4-bit）或 INT8（8-bit），以降低模型显存占用并提升推理吞吐。
2. **专用算子内核**：兼容的 GPTQModel 量化模型可调用 vLLM 自定义内核 `Marlin` 与 `Machete`，针对 **Ampere（A100+）** 与 **Hopper（H100+）** 两代 NVIDIA GPU 做高度优化，分别优化 `tps`（transactions-per-second）与 token-latency。
3. **Dynamic 量化能力**：GPTQModel 支持**逐模块（per-module）动态量化**——即同一 LLM 内部不同 layer/module 可独立指定不同的量化参数；该能力由 ModelCloud.AI 团队支持并已完整集成进 vLLM。
4. **生态规模**：Hugging Face 上有 **5000+** 已发布 GPTQ 量化模型可直接选用。
5. **典型量化配置参数**：`QuantizeConfig(bits=4, group_size=128)`——`bits=4` 表示权重量化到 4-bit，`group_size=128` 表示每 128 个权重通道共享一组量化参数。
6. **校准（calibration）数据**：使用 `allenai/c4` 数据集 `en/c4-train.00001-of-01024.json.gz`，取前 **1024** 条 `text` 样本；`batch_size=2` 可按显存规格调高以加速量化过程。

---

## 【关键机制与数据】

- **数据流（量化阶段）**：
  原文：`load(model_id, quant_config)` → `quantize(calibration_dataset, batch_size=2)` → `save(quant_path)`。
  即先用 `QuantizeConfig` 实例化量化配置，加载原始 FP/BF16 模型后，喂入 1024 条 C4 校准文本进行 GPTQ 量化，最后将量化后的模型持久化到 `quant_path`（示例中为 `Llama-3.2-1B-Instruct-gptqmodel-4bit`）。

- **数据流（推理阶段）**：
  原文展示两种调用路径——
  1. 命令行：`examples/deployment/llm_engine_example.py --model <hf_repo_id>`；
  2. Python：`vllm.LLM(model=...)` → `llm.generate(prompts, sampling_params)` → 输出 `RequestOutput` 列表（含 prompt、generated text）。
  量化模型在加载阶段即被 vLLM 识别并自动调度到 `Marlin` / `Machete` 内核执行 INT4/INT8 反量化与矩阵乘运算。

- **性能数据**：原文未给出具体 benchmark 数字，仅定性描述"Marlin 和 Machete 经 vLLM 与 NeuralMagic（现属 Red Hat）高度优化，可达到 world-class 推理性能"。**性能数据未涉及具体数值**。

- **硬件支持范围**：原文明确仅覆盖 Ampere（A100+）与 Hopper（H100+）NVIDIA GPU；其它架构未在本文档中提及。

---

## 【表格解读】

**原文无表格**。

（文中仅以代码块形式给出 `QuantizeConfig(bits=4, group_size=128)` 这一个**参数赋值语句**，并非表格结构，因此不进行表格化还原。）

---

## 【公式解读】

**原文无公式**。

（全文未出现任何 LaTeX 公式或伪代码数学表达式；GPTQ 的层间误差传递与 Hessian-based 量化求解过程在本文档中未涉及，相关细节需跳转至 GPTQModel 仓库自身的 README。）

---

## 【关联】

- **上游 / 工具链依赖**：
  - **[GPTQModel](https://github.com/ModelCloud/GPTQModel)** — ModelCloud.AI 维护的量化工具，本文档中所有量化步骤均调用其 Python API（`GPTQModel.load / quantize / save` 与 `QuantizeConfig`）。
  - **[GPTQModel README — Quantization 章节](https://github.com/ModelCloud/GPTQModel/?tab=readme-ov-file#quantization)** — 本文 `## Quantizing a model` 明确指向此处获取更详细的量化说明。
  - **[GPTQModel README — Dynamic Quantization 章节](https://github.com/ModelCloud/GPTQModel?tab=readme-ov-file#dynamic-quantization-per-module-quantizeconfig-override)** — 本文 `Dynamic` 段落指向此处获取 per-module 量化参数覆盖细节。

- **下游 / vLLM 内核绑定**：
  - **Marlin kernel** 与 **Machete kernel** — vLLM 自定义 INT4/INT8 GEMM 内核，由 vLLM 与 NeuralMagic（现 Red Hat）联合优化，是 GPTQModel 模型在 vLLM 中获得高 `tps` 与低 token-latency 的关键。
  - **vLLM LLM Python API** — 文档结尾给出 `from vllm import LLM, SamplingParams` 的最小可运行示例，表明 GPTQModel 量化模型作为 `model=` 参数直接传入，与其它 HF 模型同等待遇。

- **模型 / 数据源**：
  - **Hugging Face GPTQ 模型库（[5000+ models](https://huggingface.co/models?search=gptq)）** — 用户可直接挑选现成量化模型而无需自行量化。
  - **示例推理模型**：[ModelCloud/DeepSeek-R1-Distill-Qwen-7B-gptqmodel-4bit-vortex-v2](https://huggingface.co/ModelCloud/DeepSeek-R1-Distill-Qwen-7B-gptqmodel-4bit-vortex-v2) — 同时用于 `llm_engine_example.py` 与 `vllm.LLM` 两个示例。
  - **示例量化对象**：`meta-llama/Llama-3.2-1B-Instruct`（原始 FP 模型）。
  - **校准数据集**：`allenai/c4` 的 `en/c4-train.00001-of-01024.json.gz` 子文件，`.select(range(1024))["text"]`。

- **与其它量化方案的关系**（文档未直接点名，仅作背景关联）：本特性属于 vLLM 量化家族（与 AWQ、FP8 等并列）中的 GPTQ 路径，并独享 `Marlin`/`Machete` 双内核加速。

---

## 【使用方法】

### 1. 安装 GPTQModel（原文给出）

```bash
pip install -U gptqmodel --no-build-isolation -v
```

### 2. 量化一个 FP/BF16 模型（原文示例，Llama-3.2-1B-Instruct）

关键配置项：
- `bits = 4`（亦可设为 8，文档前言提及支持 INT4/INT8）
- `group_size = 128`
- `batch_size = 2`（可按 GPU/VRAM 调高以加速）
- 校准样本数 `range(1024)`

```python
from datasets import load_dataset
from gptqmodel import GPTQModel, QuantizeConfig

model_id = "meta-llama/Llama-3.2-1B-Instruct"
quant_path = "Llama-3.2-1B-Instruct-gptqmodel-4bit"

calibration_dataset = load_dataset(
    "allenai/c4",
    data_files="en/c4-train.00001-of-01024.json.gz",
    split="train",
).select(range(1024))["text"]

quant_config = QuantizeConfig(bits=4, group_size=128)

model = GPTQModel.load(model_id, quant_config)
model.quantize(calibration_dataset, batch_size=2)
model.save(quant_path)
```

### 3. 命令行启动 vLLM 推理（原文给出）

```bash
python examples/deployment/llm_engine_example.py \
    --model ModelCloud/DeepSeek-R1-Distill-Qwen-7B-gptqmodel-4bit-vortex-v2
```

### 4. Python API 启动 vLLM 推理（原文给出）

关键调用项：
- `LLM(model="ModelCloud/DeepSeek-R1-Distill-Qwen-7B-gptqmodel-4bit-vortex-v2")`
- `SamplingParams(temperature=0.6, top_p=0.9)`
- `llm.generate(prompts, sampling_params)` → 返回 `RequestOutput` 列表

```python
from vllm import LLM, SamplingParams

prompts = [
    "Hello, my name is",
    "The president of the United States is",
    "The capital of France is",
    "The future of AI is",
]
sampling_params = SamplingParams(temperature=0.6, top_p=0.9)
llm = LLM(model="ModelCloud/DeepSeek-R1-Distill-Qwen-7B-gptqmodel-4bit-vortex-v2")
outputs = llm.generate(prompts, sampling_params)

for output in outputs:
    print(f"Prompt: {output.prompt!r}\nGenerated text: {output.outputs[0].text!r}")
```

### 5. 动态（Dynamic）逐模块量化
原文**未给出完整代码示例**，仅指引读者跳转至 GPTQModel README 的 [Dynamic Quantization 章节](https://github.com/ModelCloud/GPTQModel?tab=readme-ov-file#dynamic-quantization-per-module-quantizeconfig-override) 查阅；具体 `QuantizeConfig` 子模块级别的 override 写法**原文未涉及**。
