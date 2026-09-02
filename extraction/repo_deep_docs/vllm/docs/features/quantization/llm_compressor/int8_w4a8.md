# INT8 W4A8

> 仓 `vllm` · 路径 `docs/features/quantization/llm_compressor/int8_w4a8.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm/docs/features/quantization/llm_compressor/int8_w4a8.md

# INT8 W4A8 量化方案深度解读

## 【定位】
本文档阐述如何在 vLLM 中使用 `llm-compressor` 库对模型执行 **W4A8 量化**（权重 INT4 + 激活 INT8），通过 GPTQ 后训练量化算法实现模型体积压缩与推理加速，并提供基于 `lm-evaluation-harness` 的精度评估完整流程。

---

## 【技术要点】

1. **量化方案定义**：权重 4-bit、激活 8-bit（W4A8），通过 GPTQ 算法一次性（`oneshot`）完成；适合在保持较好精度的同时显著降低显存占用。
2. **双方案路线**：
   - **Groupwise**（精度优先）：使用字符串 `"W4A8"` 隐式配置，权重按 group（保存命名 `W4A8-G128-Dynamic-Per-Token`，即 group_size=128）。
   - **Channelwise**（性能优先）：显式构造 `scheme` 字典，权重 `strategy=CHANNEL`、`group_size=None`、对称、静态；激活 `strategy=TOKEN`、非对称、动态（`dynamic=True`）。
3. **依赖隔离**：`llm-compressor` 与 `vLLM` 必须安装在**不同的虚拟环境**（如 `venv-llm-compressor` 与 `venv-vllm`），避免依赖冲突。
4. **校准数据规范**：`NUM_CALIBRATION_SAMPLES = 512`，`MAX_SEQUENCE_LENGTH = 2048`，数据集为 `HuggingFaceH4/ultrachat_200k`（`train_sft` split），`shuffle(seed=42)` 后取前 512 条。
5. **核心算法参数**：`GPTQModifier` 中 `targets="Linear"`、`ignore=["lm_head"]`、`dampening_frac=0.01`；Groupwise 路径使用字符串 `scheme="W4A8"`，Channelwise 路径通过 `config_groups={"group_0": scheme}` 注入配置。
6. **硬件加速**（原文）："On Arm® CPUs, this is accelerated through [KleidiAI](https://github.com/ARM-software/kleidiai)."

---

## 【关键机制与数据】

**工作原理**：
- **GPTQ（Gradient Post-Training Quantization）**：基于校准样本计算激活分布并估计量化 scale，按层逐块最小化量化误差；`dampening_frac=0.01` 用于数值稳定（抑制 Hessian 极端值）。
- **激活量化（INT8）**：原文指出"you need sample data to estimate the activation scales"，因此 512 条校准样本是激活量化精度的前提；Groupwise 模式下 `W4A8` 字符串内含动态 per-token（`Dynamic-Per-Token`）激活量化语义。
- **权重量化（INT4）**：Groupwise 使用隐式 group_size=128（细粒度分组，保留更多精度）；Channelwise 按输出通道整层共享 scale/group_size=None（计算更快但精度略损）。

**数据流**：
1. `transformers.AutoModelForCausalLM.from_pretrained` 加载 `meta-llama/Meta-Llama-3-8B-Instruct`（`dtype="auto"`）；
2. `datasets.load_dataset` 加载并 `map` 应用 `apply_chat_template` → 再 `tokenize`（无 padding、无特殊 token，截断至 2048）；
3. `llmcompressor.oneshot(model, dataset=ds, recipe=recipe, max_seq_length=..., num_calibration_samples=...)` 应用 GPTQ；
4. `model.save_pretrained(SAVE_DIR, save_compressed=True)` 保存为压缩格式（compressed-tensors 序列化）；
5. `vllm.LLM(SAVE_DIR)` 直接推理；`lm_eval` 评估 `gsm8k` 任务。

**性能/精度数据**：原文未给出具体 throughput、显存占用或 accuracy 数字。

---

## 【表格解读】

**原文无表格**（文档以代码片段和参数列表形式给出两种方案的配置）。

---

## 【公式解读】

**原文无公式**（无 LaTeX 公式或伪代码形式的数学表达式）。

---

## 【关联】

本文档与其他模块/项目的关联如下：

- **上游工具：[`vllm-project/llm-compressor`](https://github.com/vllm-project/llm-compressor/)**：提供 `oneshot`、`GPTQModifier`、`QuantizationStrategy`、`QuantizationType` 等 API，是整篇流程的执行核心；问题反馈也指向其 [issue tracker](https://github.com/vllm-project/llm-compressor/issues)。
- **压缩序列化格式：[`compressed-tensors`](https://github.com/vllm-project/compressed-tensors)**：Channelwise 方案显式 `from compressed_tensors.quantization import QuantizationStrategy, QuantizationType`，负责将量化配置/权重打包为 `save_compressed=True` 的可被 vLLM 直接加载的格式。
- **推理后端：[vLLM `LLM` 类](https://docs.vllm.ai/)**：消费 `SAVE_DIR` 中的压缩权重，提供 W4A8 的运行时解码与算子（Channelwise 路径下通过 KleidiAI 在 Arm CPU 上加速）。
- **评估工具：[`lm-evaluation-harness`](https://github.com/EleutherAI/lm-evaluation-harness)**：通过 `--model vllm` 调用 vLLM 后端执行 `gsm8k` 5-shot 评估。
- **硬件加速库：[KleidiAI](https://github.com/ARM-software/kleidiai)**：Arm® CPU 上 INT4/INT8 矩阵乘的微内核加速库，仅对 Groupwise 与 Channelwise 两种 W4A8 路径生效。
- **校准数据源：[`HuggingFaceH4/ultrachat_200k`](https://huggingface.co/datasets/HuggingFaceH4/ultrachat_200k)**：通用指令微调语料，用于估计激活分布。

> 注：本文档内部链接列表标注为「无」，以上为文档正文中**外部/跨仓引用**的项目关联。

---

## 【使用方法】

**1. 安装依赖（原文）**

```bash
(venv-llm-compressor) pip install llmcompressor
(venv-vllm) pip install vllm "lm-eval[api]>=0.4.12"
```

**2. 量化脚本核心调用（原文摘录）**

Groupwise：
```python
recipe = [
    GPTQModifier(targets="Linear", scheme="W4A8",
                 ignore=["lm_head"], dampening_frac=0.01),
]
oneshot(model=model, dataset=ds, recipe=recipe,
        max_seq_length=MAX_SEQUENCE_LENGTH,
        num_calibration_samples=NUM_CALIBRATION_SAMPLES)
SAVE_DIR = MODEL_ID.split("/")[1] + "-W4A8-G128-Dynamic-Per-Token"
model.save_pretrained(SAVE_DIR, save_compressed=True)
tokenizer.save_pretrained(SAVE_DIR)
```

Channelwise：见原文，使用 `config_groups={"group_0": scheme}` 显式配置，保存名 `-W4A8-Channelwise-Dynamic-Per-Token`。

**3. vLLM 加载与精度评估（原文）**

```python
from vllm import LLM
llm = LLM("./Meta-Llama-3-8B-Instruct-W4A8-G128-Dynamic-Per-Token")
```

```bash
lm_eval --model vllm \
    --model_args pretrained="./Meta-Llama-3-8B-Instruct-W4A8-G128-Dynamic-Per-Token",add_bos_token=true \
    --tasks gsm8k --num_fewshot 5 --limit 250 --batch_size 'auto'
```

**4. 关键配置项（原文 best practices）**
- 校准样本数：起步 512，若精度下降再增加；
- 序列长度：起步 2048；
- 必须使用模型训练时的 chat/instruction template；
- 若模型为微调产物，建议从训练集中采样做校准；
- 评估命令必须加 `add_bos_token=True`（量化模型对 BOS token 敏感）。
