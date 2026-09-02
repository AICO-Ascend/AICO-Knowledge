# TorchAO

> 仓 `vllm` · 路径 `docs/features/quantization/torchao.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm/docs/features/quantization/torchao.md

# vLLM 文档深度解读 —— `docs/features/quantization/torchao.md`

---

## 【定位】

本文档介绍 vLLM 对 **TorchAO**（PyTorch 的架构优化库）的支持能力，重点说明如何利用 TorchAO 对 HuggingFace 上的预训练模型进行权重量化（以 INT8 weight-only 为例），并将量化后的 checkpoint 上传至 HuggingFace Hub，从而为 vLLM 推理提供经 TorchAO 量化的高性能模型加载与运行支持。

---

## 【技术要点】

1. **TorchAO 定位**：是 PyTorch 的 *architecture optimization* 库，提供高性能 dtypes、优化技术与 inference/training 内核，可与 PyTorch 原生特性（`torch.compile`、FSDP 等）组合使用（composability）。原文给出 benchmark 链接：`torchao/quantization#benchmarks`。
2. **安装方式**：推荐安装 **torchao nightly**（版本约束 `>=10.0.0`），通过 `pip install --pre` + PyTorch nightly 的 index-url 安装；CUDA 版本需根据系统选择（如 `cu126`、`cu128`）。
3. **量化对象**：支持对 HuggingFace 上的模型（含 `transformers` 与 `diffusers` 系列）进行量化，并将结果 checkpoint 保存/上传至 HuggingFace Hub。文档给出示例仓库 `jerryzh168/llama3-8b-int8wo`。
4. **量化方案示例**：使用 `torchao.quantization.Int8WeightOnlyConfig`，对应 vLLM/HF 侧的 `TorchAoConfig(Int8WeightOnlyConfig())`。
5. **模型加载方式**：通过 `AutoModelForCausalLM.from_pretrained()` + `TorchAoConfig` 完成；使用 `dtype="auto"`、`device_map="auto"`，并经由 `quantization_config=...` 注入量化配置。
6. **替代入口**：除代码方式外，可使用 HuggingFace 上的 [TorchAO Quantization Space](https://huggingface.co/spaces/medmekk/TorchAO_Quantization) 这个带 UI 的 Space 完成量化。

---

## 【关键机制与数据】

**工作原理 / 数据流（基于原文示例代码）：**

1. 调用方构造一个 `TorchAoConfig`，内部包装具体的 torchao 量化配方（此处为 `Int8WeightOnlyConfig`，即 **INT8 weight-only** 量化）。
2. `AutoModelForCausalLM.from_pretrained(model_name, dtype="auto", device_map="auto", quantization_config=quantization_config)` 在加载 `meta-llama/Meta-Llama-3-8B` 的同时按配置应用量化。
3. tokenizer 对输入文本 `"What are we having for dinner?"` 编码后送入 GPU（`to("cuda")`）。
4. 量化后的 `quantized_model` 与 `tokenizer` 通过 `push_to_hub(...)` 上传；其中 `push_to_hub(hub_repo, safe_serialization=False)` 显式关闭 safe serialization（原文标注 `safe_serialization=False`）。

**性能/数据（原文有的）：**
- 原文仅指向外部 benchmark 页面（`torchao/quantization#benchmarks`），**原文未提供** vLLM 侧的实测吞吐/精度/显存数字。
- 原文给出的具体版本/库标识：`torchao>=10.0.0`、CUDA tag `cu126`（示例）/ `cu128`（候选）、示例模型 `Meta-Llama-3-8B`、示例输入 `"What are we having for dinner?"`。

---

## 【表格解读】

**原文无表格。** 文档中未出现任何参数表、配置表或性能对比表；唯一可被视为"配置项列表"的内容是安装命令里的 CUDA tag（`cu126` / `cu128`）与 Python 示例中的字段（`dtype`、`device_map`、`quantization_config`、`safe_serialization`），均以命令/代码形式给出，未表格化。

---

## 【公式解读】

**原文无公式。** 文档不涉及任何量化数学公式（如 per-channel scaling factor、zero-point 推导、误差分析等），也未给出伪代码形式的算法描述。

---

## 【关联】

原文末标注"内部链接: (无)"，故本节仅梳理文档中**实际出现**的外部关联资源：

- **TorchAO 上游仓库 & 基准**：`pytorch/ao/tree/main/torchao/quantization#benchmarks` —— 用于查阅量化方案的 benchmark 数字（与本文档并行参考，但不在 vLLM 仓内）。
- **Transformers 量化文档**：`huggingface.co/docs/transformers/.../torchao` —— 与本文档示例代码同源，解释 `TorchAoConfig` 在 HF Transformers 侧的定义。
- **Diffusers 量化文档**：`huggingface.co/docs/diffusers/.../torchao` —— 扩展到扩散模型侧的量化路径。
- **示例 HF 模型仓库**：`huggingface.co/jerryzh168/llama3-8b-int8wo` —— 一个已上传的 INT8 weight-only Llama-3-8B 量化产物，可作为 vLLM 加载 TorchAO 量化 checkpoint 的参考实现。
- **UI 量化入口**：`huggingface.co/spaces/medmekk/TorchAO_Quantization` —— 无需写代码即可产出 TorchAO 量化模型的 HF Space。

> 在 vLLM 仓内，TorchAO 文档位于 `docs/features/quantization/torchao.md`，属于 `docs/features/quantization/` 量化专题子目录的一部分（与其它量化后端如 GPTQ、AWQ、FP8 等并列，**但原文未给出这些兄弟页面的链接**）。

---

## 【使用方法】

### 1) 安装（原文命令，逐字保留）

```bash
# Install the latest TorchAO nightly build
# Choose the CUDA version that matches your system (cu126, cu128, etc.)
pip install \
    --pre torchao>=10.0.0 \
    --index-url https://download.pytorch.org/whl/nightly/cu126
```

要点：`--pre` 启用 prerelease；版本下界 `>=10.0.0`；CUDA tag 需与本机匹配（示例为 `cu126`，可选 `cu128` 等）。

### 2) 量化 HF 模型并上传 Hub（原文 Python 示例，逐字保留）

```python
import torch
from transformers import TorchAoConfig, AutoModelForCausalLM, AutoTokenizer
from torchao.quantization import Int8WeightOnlyConfig

model_name = "meta-llama/Meta-Llama-3-8B"
quantization_config = TorchAoConfig(Int8WeightOnlyConfig())
quantized_model = AutoModelForCausalLM.from_pretrained(
    model_name,
    dtype="auto",
    device_map="auto",
    quantization_config=quantization_config
)
tokenizer = AutoTokenizer.from_pretrained(model_name)
input_text = "What are we having for dinner?"
input_ids = tokenizer(input_text, return_tensors="pt").to("cuda")

hub_repo = # YOUR HUB REPO ID
tokenizer.push_to_hub(hub_repo)
quantized_model.push_to_hub(hub_repo, safe_serialization=False)
```

关键配置项说明：
- `Int8WeightOnlyConfig()`：INT8 weight-only 量化配方（仅权重 INT8，激活保持原精度）。
- `TorchAoConfig(...)`：HF Transformers 与 torchao 之间的桥接配置类。
- `dtype="auto"` / `device_map="auto"`：由 HF Transformers 自动决定 dtype 与设备放置。
- `quantization_config=quantization_config`：将 torchao 量化方案注入到 `from_pretrained` 流程。
- `safe_serialization=False`：在 `push_to_hub` 时禁用 safe serialization（按原文标注）。

### 3) vLLM 侧的运行命令 / 配置项

**原文未涉及。** 本文给出的代码片段全部位于 `transformers` + `torchao` 流程内（量化 + 上传 Hub），并未展示在 vLLM 中如何加载上述量化 checkpoint 的启动命令、engine 参数、`--quantization torchao` 之类的 CLI flag 或 engine 配置项；这些内容需参考 vLLM 仓库其它章节，原文未提供。
