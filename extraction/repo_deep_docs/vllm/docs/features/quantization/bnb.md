# BitsAndBytes

> 仓 `vllm` · 路径 `docs/features/quantization/bnb.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm/docs/features/quantization/bnb.md

# 「vllm/docs/features/quantization/bnb.md」深度解读

## 【定位】

这篇文档描述 vLLM 通过 out-of-tree 插件 `vllm-bnb-plugin` 接入 [BitsAndBytes](https://github.com/TimDettemons/bitsandbytes) 量化方案的能力，重点说明其"无需校准数据"的特性以及"读取已量化 checkpoint"和"运行时 (inflight) 量化"两种启用方式。

---

## 【技术要点】

1. **特性定位**：BitsAndBytes 量化用于"降低显存、提升性能"且"对精度影响不显著"，相比其他量化方法**省去了用输入数据校准 (calibration) 量化模型**的步骤。
2. **插件式集成**：vLLM 主仓本身**不内置** BitsAndBytes 支持，而是由外部插件 `vllm-bnb-plugin` 提供，安装命令为：
   ```bash
   uv pip install vllm-bnb-plugin
   ```
3. **两种使用模式并列**：
   - **读取已量化 checkpoint (Read quantized checkpoint)**：vLLM 会从模型 `config.json` 中的 `quantization_config` 段推断量化方法，**无需**显式传 `quantization` 参数。
   - **Inflight 4bit 量化**：必须显式指定 `quantization="bitsandbytes"` 参数。
4. **数据类型约定**：示例中统一使用 `dtype=torch.bfloat16`，并对部分模型启用 `trust_remote_code=True`。
5. **HF 模型来源指引**：可从 Hugging Face 上搜索 `bitsandbytes` 关键字获取已量化的 checkpoint；这些仓库通常在 `config.json` 中带有 `quantization_config` 段。
6. **OpenAI 兼容服务 (OpenAI Compatible Server)**：在模型参数后追加 `--quantization bitsandbytes` 即可启用 4bit inflight 量化。

---

## 【关键机制与数据】

**工作原理与数据流（综合原文）：**

- **原文**：模型配置文件（`config.json`）是量化方法的"单一事实源 (single source of truth)"。vLLM **读取**该文件并**从中推断**量化方式，从而支持"读取已量化 checkpoint"模式。
- **原文**：对于"inflight 量化"路径，用户必须在调用 `LLM(...)` 时显式传入 `quantization="bitsandbytes"`，触发 vLLM 在加载阶段把权重按 BitsAndBytes 方案量化。
- **原文**："config.json" 中包含 `quantization_config` 字段是支持读取预量化 checkpoint 的前提条件。

**性能/精度相关数据：**
- 原文无具体数字（如 VRAM 节省、吞吐提升、精度损失指标等），仅以定性描述 "without significantly sacrificing accuracy"。
- 原文未给出 inflight 量化加载时间、与 FP16/BF16 的对比基准或量化粒度（per-tensor / per-channel / NF4/FP4 等）参数。
- 原文未指定 BitsAndBytes 的具体 bit-width 范围（如 4bit、8bit），但所有 inflight 示例明确标注为 "**load as 4bit quantization**" 和 "**4bit inflight quantization**"。

---

## 【表格解读】

**原文无表格。** 全文以文字说明 + 代码块形式呈现，没有参数表、性能对比表或配置项表。

---

## 【公式解读】

**原文无公式。** 全文不包含任何 LaTeX 公式或伪代码形式的量化推导式（如 $Q(x)=\text{round}(x/\Delta)+z$ 之类均未出现）。

---

## 【关联】

- **外部项目依赖**：核心关联是 [`vllm-bnb-plugin`](https://github.com/vllm-project/vllm-bnb-plugin)，位于 out-of-tree 树外，必须先 `uv pip install` 才可用；这是 vLLM 量化生态中"插件化"扩展策略的具体实例。
- **上游生态**：上游 [BitsAndBytes 项目](https://github.com/TimDettmers/bitsandbytes) 提供核心量化算法，vLLM 端只是消费方。
- **模型源**：通过 [Hugging Face 上按 `bitsandbytes` 搜索](https://huggingface.co/models?search=bitsandbytes) 找到的预量化模型仓库可以无缝接入 "Read quantized checkpoint" 模式，关键要求是仓库中存在带 `quantization_config` 段的 `config.json`。
- **服务形态**：BitsAndBytes 既可在 Python `LLM(...)` API 中使用，也可通过 OpenAI 兼容 Server（命令行加 `--quantization bitsandbytes`）使用；表明其对 vLLM **编程接口与 HTTP 服务**两种调用形态同时生效。
- **横向比较**：原文将 BitsAndBytes 与"其它需要校准输入数据的量化方法"形成对比，但**未具体点名**其他方法（如 GPTQ、AWQ、FP8 等），因此不能据本段判定这些方法的差异。

> 附注：原文文末内部链接区域为「(无)」，未提供文档站内的相关 feature/quantization 模块的跳转链接。

---

## 【使用方法】

**1. 安装插件（前置步骤，原文命令）：**
```bash
uv pip install vllm-bnb-plugin
```

**2. 读取已量化 checkpoint（无需 `quantization` 参数，原文示例）：**
```python
from vllm import LLM
import torch

model_id = "unsloth/tinyllama-bnb-4bit"
llm = LLM(
    model=model_id,
    dtype=torch.bfloat16,
    trust_remote_code=True,
)
```

**3. Inflight 4bit 量化（必须显式指定 `quantization="bitsandbytes"`，原文示例）：**
```python
from vllm import LLM
import torch

model_id = "huggyllama/llama-7b"
llm = LLM(
    model=model_id,
    dtype=torch.bfloat16,
    trust_remote_code=True,
    quantization="bitsandbytes",
)
```

**4. OpenAI 兼容 Server 启用 4bit inflight 量化（原文命令）：**
```bash
--quantization bitsandbytes
```
（文档说明 "Append the following to your model arguments"，即作为 vLLM 服务启动时模型参数列表中的额外参数传入。）

**未在原文出现的配置项**：bitsandbytes 的具体计算 dtype、量化类型（NF4 / FP4）、是否 `double_quant`、是否 `load_in_4bit`/`load_in_8bit` 切换等 vLLM 端是否暴露的开关，原文均**未涉及**。
