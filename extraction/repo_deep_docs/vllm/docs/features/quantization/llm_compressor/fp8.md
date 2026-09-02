# FP8 W8A8

> 仓 `vllm` · 路径 `docs/features/quantization/llm_compressor/fp8.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm/docs/features/quantization/llm_compressor/fp8.md

# FP8 W8A8 文档深度解读

## 【定位】

这篇文档描述 vLLM 中 **FP8 (8-bit 浮点) 权重与激活同时量化 (W8A8)** 的能力、硬件适配性、离线量化流程与在线动态量化使用方法, 是面向需要在 Hopper/Ada Lovelace 等 GPU 上落地 FP8 推理用户的实操性 feature 文档。

## 【技术要点】

1. **支持硬件分级**: Hopper (NVIDIA H100)、Ada Lovelace 与 AMD MI300x 为 W8A8 官方支持对象; Turing/Ampere 仅支持 weight-only 的 W8A16 路径, 借助 **Marlin kernels** 完成 FP8 权重 + 高精度激活的反量化计算。
2. **两类 FP8 数值格式**: **E4M3** (1 符号 + 4 指数 + 3 尾数, 取值范围 ±448, 含 nan); **E5M2** (1 符号 + 5 指数 + 2 尾数, 取值范围 ±57344, 含 ±inf 与 nan, 动态范围更大但精度更低)。
3. **硬件算力门槛**: FP8 计算需 NVIDIA GPU compute capability ≥ **8.9** (对应 Ada Lovelace 与 Hopper); compute capability ≥ **7.5** (Turing) 仅能跑 W8A16 via FP8 Marlin。
4. **核心收益**: 模型显存占用 **2×** 下降, 吞吐最高 **1.6×** 提升, 精度影响极小。
5. **离线量化配方 (`FP8_DYNAMIC`)**:
   - **权重**: static, per-channel 量化
   - **激活**: dynamic, per-token 量化
   - **目标层**: 所有 `Linear` 层, 显式 `ignore=["lm_head"]`
   - 采用简单 RTN, **无需校准数据**
6. **在线动态量化 (离线 BF16/FP16 → 在线 FP8)**: 无需任何校准数据, 启动开关 `--quantization="fp8"` 或 `quantization="fp8"`, 权重一次性量化为 **FP8_E4M3** + **per-tensor scale**, 激活在每个 forward pass 内动态计算 min/max 得到 per-tensor scale。

## 【关键机制与数据】

- **离线量化数据流** (原文): ① 用 `transformers` 的 `AutoModelForCausalLM.from_pretrained(MODEL_ID, device_map="auto", dtype="auto")` 加载原始模型 (`meta-llama/Meta-Llama-3-8B-Instruct`) 与 tokenizer; ② 通过 `llmcompressor` 的 `QuantizationModifier(targets="Linear", scheme="FP8_DYNAMIC", ignore=["lm_head"])` 构造离线 PTQ 配方并以 `oneshot()` 执行; ③ 序列化到 `Meta-Llama-3-8B-Instruct-FP8-Dynamic`; ④ 使用 `vllm.LLM` 加载该目录推理。
- **推理时验证输出**: 原文给出最小推理片段 `llm.generate("Hello my name is")`, 打印 `result[0].outputs[0].text`。
- **评测基线 (原文)**: 在 `gsm8k` 上 5-shot、limit 250 样本, 同时给出 `add_bos_token=True` 的注意事项 (因为 lm_eval 默认不加 `bos` token, 而量化模型对 `bos` 敏感)。
- **在线量化运行时开销 (原文)**: 由于激活需要每个 forward pass 计算 min/max 形成动态 per-tensor scale, **此模式下 latency 改善有限**。
- **在线量化显存读数 (原文)**: 加载 `facebook/opt-125m` 时日志 `Loading model weights took 0.1550 GB`。
- **环境隔离要求 (原文)**: `llm-compressor` 与 `vllm` 可能不兼容, 必须使用**独立虚拟环境** 分别安装。

## 【表格解读】

原文给出一张 `lm_eval` 输出格式的评测结果表, 逐字还原如下:

| Tasks | Version | Filter            | n-shot | Metric      |   | Value |   | Stderr |
| ----- | ------: | ----------------- | -----: | ----------- | - | ----: | - | -----: |
| gsm8k |       3 | flexible-extract  |      5 | exact_match | ↑ | 0.768 | ± | 0.0268 |
|       |         | strict-match      |      5 | exact_match | ↑ | 0.768 | ± | 0.0268 |

逐行解读:
- **Tasks 列**: `gsm8k` (grade-school math word problems), Version 为 3, 表明所用 benchmark 版本。
- **Filter 列第一行** `flexible-extract`: 宽松匹配策略, 允许从生成结果中灵活抽取最终数值。
- **Filter 列第二行** `strict-match`: 严格匹配, 要求生成文本中精准命中答案格式。两种 filter 下完全相同 (均 0.768) 说明模型答案既能被宽松抽取又能被严格命中。
- **n-shot 列**: 都为 5, 即评测时附带 5 个 few-shot 示例。
- **Metric 列**: 都为 `exact_match` (精确匹配率), 方向箭头 `↑` 表示数值越高越好。
- **Value 列**: 两行均为 **0.768**, 即在 250 条样本中有 ~76.8% 的题目被正确回答。
- **Stderr 列**: 两行均为 **±0.0268**, 为指标在样本上的标准误差, 表明精度估计的不确定性区间。

## 【公式解读】

原文无公式 (无 LaTeX 或伪代码形式的符号化推导公式)。仅在文字层面用 max 取值 (±448、±57344) 描述了两种 FP8 格式的数值范围, 未给出显式的浮点表示公式或量化公式。

## 【关联】

- **上游/工具链**:
  - [`vllm-project/llm-compressor`](https://github.com/vllm-project/llm-compressor/) 提供 `QuantizationModifier`、`oneshot()` 等离线 PTQ 原语; 文档结尾指向该仓库的 [issue tracker](https://github.com/vllm-project/llm-compressor/issues) 作为问题反馈渠道。
  - `[lm-eval](https://github.com/EleutherAI/lm-evaluation-harness)` (`lm-eval[api]>=0.4.12`) 用于量化后精度回归测试。
  - `transformers` 的 `AutoModelForCausalLM`、`AutoTokenizer` 提供原始模型加载与序列化。
  - vLLM 自身的 `LLM` 推理类为离线量化模型与在线动态量化提供运行时入口。
- **部署侧资源**: 文档外链 [Hugging Face 量化 FP8 模型集合](https://huggingface.co/collections/neuralmagic/fp8-llms-for-vllm-666742ed2b78b7ac8df13127), 提供可直接服务于 vLLM 的现成 checkpoint。
- **硬件层关联**: Hopper/Ada Lovelace 的 FP8 tensor core 与 Turing/Ampere 的 FP8 Marlin kernel 是该特性的两套硬件加速后端, 文档通过 compute capability 阈值 (8.9 与 7.5) 把这两条路径区分开。
- **同文档其他章节**: 内部链接表标注 **(无)**; 外部链接全部为 GitHub/ HF 资源。

## 【使用方法】

**离线 PTQ 量化 (在 vllm 启动前执行)**:
```bash
# 环境 A: 量化环境
(venv-llm-compressor) pip install llmcompressor

# 环境 B: 推理+评测环境 (与上者完全隔离)
(venv-llm) pip install vllm "lm-eval[api]>=0.4.12"
```
```python
from transformers import AutoTokenizer, AutoModelForCausalLM
from llmcompressor import oneshot
from llmcompressor.modifiers.quantization import QuantizationModifier

MODEL_ID = "meta-llama/Meta-Llama-3-8B-Instruct"
model = AutoModelForCausalLM.from_pretrained(MODEL_ID, device_map="auto", dtype="auto")
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)

recipe = QuantizationModifier(targets="Linear", scheme="FP8_DYNAMIC", ignore=["lm_head"])
oneshot(model=model, recipe=recipe)
SAVE_DIR = MODEL_ID.split("/")[1] + "-FP8-Dynamic"
model.save_pretrained(SAVE_DIR); tokenizer.save_pretrained(SAVE_DIR)
```

**离线模型推理验证 (原文)**:
```python
from vllm import LLM
llm = LLM("./Meta-Llama-3-8B-Instruct-FP8-Dynamic")
result = llm.generate("Hello my name is")
print(result[0].outputs[0].text)
```

**精度评估 (原文 lm-eval 调用)**:
```bash
MODEL=$PWD/Meta-Llama-3-8B-Instruct-FP8-Dynamic
lm_eval \
  --model vllm \
  --model_args pretrained=$MODEL,add_bos_token=True \
  --tasks gsm8k  --num_fewshot 5 --batch_size auto --limit 250
```

**在线动态量化 (无需任何校准数据, 直接作用于 BF16/FP16 原始模型)**:
- 命令行: `vllm serve ... --quantization="fp8"` (原文给出 CLI 形式)。
- 编程接口:
```python
from vllm import LLM
llm = LLM("facebook/opt-125m", quantization="fp8")
# INFO 06-10 17:55:42 model_runner.py:157] Loading model weights took 0.1550 GB
result = llm.generate("Hello, my name is")
print(result[0].outputs[0].text)
```

**关键启用开关汇总**:
| 模式 | 入口 | 关键参数 |
| --- | --- | --- |
| 离线 RTN 量化 | `llmcompressor.oneshot` | `QuantizationModifier(scheme="FP8_DYNAMIC", targets="Linear", ignore=["lm_head"])` |
| 在线动态量化 | vLLM CLI / `LLM()` | `--quantization="fp8"` 或 `quantization="fp8"` |
