# AutoAWQ

> 仓 `vllm` · 路径 `docs/features/quantization/auto_awq.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm/docs/features/quantization/auto_awq.md

# vLLM AutoAWQ 文档深度解读

---

## 【定位】

这篇文档原本用于说明如何借助 **AutoAWQ** 库对模型进行 **4-bit (INT4) 量化** 并在 vLLM 中加载运行,但文档开头即以 ⚠️ 警告形式声明该库已**弃用 (deprecated)**,其能力已被 vLLM 项目吸收至 [`llm-compressor`](https://github.com/vllm-project/llm-compressor/tree/main/examples/awq) 项目中,因此本文档同时充当一条**迁移指引**,引导用户转向新的 AWQ 量化流程。

---

## 【技术要点】

1. **能力定位**:AutoAWQ 提供 **BF16/FP16 → INT4** 的权重量化,主要收益为**降低延迟 (lower latency) 与降低显存占用 (memory usage)**。
2. **生态规模**:Huggingface 上已有 **6500+ 个预量化 AWQ 模型** 可直接选用,无需自行量化。
3. **安装命令**:`pip install autoawq`。
4. **核心量化配置参数**(以 `mistralai/Mistral-7B-Instruct-v0.2` 为例):
   - `zero_point = True`(启用 zero-point 量化)
   - `q_group_size = 128`(每 128 个权重共享一组量化参数)
   - `w_bit = 4`(权重量化到 4 bit)
   - `version = "GEMM"`(使用 GEMM 内核实现)
5. **vLLM 加载端标识**:通过 CLI 参数 `--quantization auto_awq` 或 Python API 的 `quantization="auto_awq"` 显式指定。
6. **示例推理模型**:`TheBloke/Llama-2-7b-Chat-AWQ`。
7. **加载辅助参数**:量化前加载原始模型时使用 `low_cpu_mem_usage=True, use_cache=False`。

---

## 【关键机制与数据】

- **数据流(量化阶段,原文)**:
  1. 通过 `AutoAWQForCausalLM.from_pretrained(model_path, low_cpu_mem_usage=True, use_cache=False)` 加载预训练模型;
  2. 同步加载 `AutoTokenizer`;
  3. 调用 `model.quantize(tokenizer, quant_config=quant_config)` 执行量化;
  4. 通过 `model.save_quantized(quant_path)` 与 `tokenizer.save_pretrained(quant_path)` 落盘,产物路径即 `quant_path`。

- **数据流(推理阶段,原文)**:
  1. CLI 入口:`python examples/deployment/llm_engine_example.py --model TheBloke/Llama-2-7b-Chat-AWQ --quantization auto_awq`;
  2. Python 入口:`LLM(model="TheBloke/Llama-2-7b-Chat-AWQ", quantization="auto_awq")`;
  3. 使用 `SamplingParams(temperature=0.8, top_p=0.95)` 生成,遍历 `RequestOutput` 输出 `prompt` 与 `generated_text`。

- **关键数字与参数(原文)**:`BF16/FP16 → INT4`、`6500+ Huggingface 模型`、`q_group_size=128`、`w_bit=4`、`zero_point=True`、`version="GEMM"`、`temperature=0.8`、`top_p=0.95`。

- **性能收益(原文)**:降低延迟 + 降低显存占用(原文未给出量化前后具体的倍数或显存数字,故不补全)。

- **关键信号**:文档顶部警告已明确表达**功能已迁移至 llm-compressor**,因此下文给出的量化与推理示例属于**遗留路径**,新的推荐路径需参阅 llm-compressor 的 AWQ examples。

---

## 【表格解读】

**原文无表格**。文档仅通过代码块与命令块展示配置项与调用方式,未出现任何 markdown 表格或参数对照表结构。

---

## 【公式解读】

**原文无公式**。文档未包含任何 LaTeX 数学公式或伪代码形式的算法表达;量化算法细节 (`zero_point`、`q_group_size`、`w_bit`、`GEMM` 版本) 均以字典配置形式给出,无数学描述。

---

## 【关联】

文档虽显式声明内部链接为空,但内容中通过外链形成了清晰的上下游关系图:

| 文档提及的对象 | 与本文档的关系 |
|---|---|
| [`llm-compressor/examples/awq`](https://github.com/vllm-project/llm-compressor/tree/main/examples/awq) | **新主入口**:AutoAWQ 弃用后,AWQ 量化能力的官方承接项目,推荐工作流 |
| [`AutoAWQ` 原仓库](https://github.com/casper-hansen/AutoAWQ) | **弃用源**:原 AutoAWQ 库所在仓库,内含 deprecation 详情 |
| [AutoAWQ 文档](https://casper-hansen.github.io/AutoAWQ/examples/#basic-quantization) | **量化细节参考**:Basic Quantization 用法的官方说明页 |
| [Huggingface AWQ 模型集合](https://huggingface.co/models?search=awq) | **预量化模型生态**:6500+ 开箱即用的 AWQ 模型 |
| `mistralai/Mistral-7B-Instruct-v0.2` | **量化示例输入**:被量化的原始 FP 模型 |
| `TheBloke/Llama-2-7b-Chat-AWQ` | **推理示例模型**:在 vLLM 中以 `auto_awq` 加载的目标 |
| `examples/deployment/llm_engine_example.py` | **CLI 部署脚本**:通过 `--quantization auto_awq` 演示命令行加载 |
| `vllm.LLM` / `vllm.SamplingParams` | **Python 推理 API**:对应同一能力的编程入口 |

整体上,文档构成一条**"弃用通知 → 迁移指引 → 遗留量化示例 → 遗留推理示例"** 的链式说明,核心是把用户从 `AutoAWQ` 引导至 `llm-compressor`。

---

## 【使用方法】

**1. 安装(原文)**:
```bash
pip install autoawq
```

**2. 量化一个模型(原文,基于 mistralai/Mistral-7B-Instruct-v0.2)**:
```python
from awq import AutoAWQForCausalLM
from transformers import AutoTokenizer

model_path = "mistralai/Mistral-7B-Instruct-v0.2"
quant_path = "mistral-instruct-v0.2-awq"
quant_config = {"zero_point": True, "q_group_size": 128, "w_bit": 4, "version": "GEMM"}

model = AutoAWQForCausalLM.from_pretrained(model_path, low_cpu_mem_usage=True, use_cache=False)
tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)

model.quantize(tokenizer, quant_config=quant_config)
model.save_quantized(quant_path)
tokenizer.save_pretrained(quant_path)
```

**3. 在 vLLM 中以 CLI 加载 AWQ 模型(原文)**:
```bash
python examples/deployment/llm_engine_example.py \
    --model TheBloke/Llama-2-7b-Chat-AWQ \
    --quantization auto_awq
```

**4. 在 vLLM 中以 Python API 加载 AWQ 模型(原文)**:
```python
from vllm import LLM, SamplingParams

prompts = [
    "Hello, my name is",
    "The president of the United States is",
    "The capital of France is",
    "The future of AI is",
]
sampling_params = SamplingParams(temperature=0.8, top_p=0.95)

llm = LLM(model="TheBloke/Llama-2-7b-Chat-AWQ", quantization="auto_awq")
outputs = llm.generate(prompts, sampling_params)

for output in outputs:
    prompt = output.prompt
    generated_text = output.outputs[0].text
    print(f"Prompt: {prompt!r}, Generated text: {generated_text!r}")
```

**补充说明(基于文档警告):** 上述安装命令、量化代码、`auto_awq` 后端名称均属于**已弃用路径**;新的推荐量化流程需遵循 [`llm-compressor` 的 AWQ examples](https://github.com/vllm-project/llm-compressor/tree/main/examples/awq),原文未给出新路径下的具体配置项或命令,故不补全。
