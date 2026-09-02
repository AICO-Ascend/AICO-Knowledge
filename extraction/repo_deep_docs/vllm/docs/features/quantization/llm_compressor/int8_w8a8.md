# INT8 W8A8

> 仓 `vllm` · 路径 `docs/features/quantization/llm_compressor/int8_w8a8.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm/docs/features/quantization/llm_compressor/int8_w8a8.md

# vLLM INT8 W8A8 量化文档深度解读

---

## 【定位】

这篇文档描述了 vLLM 通过 [llm-compressor](https://github.com/vllm-project/llm-compressor) 库将 LLM 的**权重与激活同时量化为 INT8（W8A8）**的端到端流程,用于在保持模型性能的前提下降低显存占用并加速推理。

---

## 【技术要点】

1. **量化方案**: 权重(Weight)与激活(Activation)均量化为 8-bit 整数,方案标识为 `W8A8`,采用 **Dynamic Per-Token** 粒度(从输出目录名 `Meta-Llama-3-8B-Instruct-W8A8-Dynamic-Per-Token` 可读出)。
2. **算法组合(Rcipe)**: 由两个 modifier 级联组成 —— `SmoothQuantModifier(smoothing_strength=0.8)` 负责激活平滑,`GPTQModifier(targets="Linear", scheme="W8A8", ignore=["lm_head"])` 负责权重量化,且明确**忽略 `lm_head`** 输出层。
3. **校准数据规范**: 样本量 `NUM_CALIBRATION_SAMPLES = 512`,最大序列长度 `MAX_SEQUENCE_LENGTH = 2048`,使用 `HuggingFaceH4/ultrachat_200k` 数据集的 `train_sft` split,随机种子 `seed=42`,并应用模型自身的 chat template。
4. **硬件支持边界**:
   - 支持: NVIDIA GPU 计算能力 **> 7.5**(Turing、Ampere、Ada Lovelace、Hopper)。
   - 不支持: 计算能力 **≥ 10.0**(如 RTX 6000 Blackwell),需改用 [FP8](fp8.md)。
5. **环境隔离要求**: `llm-compressor` 与 `vllm` **必须分别装在不同虚拟环境**中(原文示例用 `venv-llm-compressor` 和 `venv-llm`),且 `lm-evaluation-harness` 需 `>= 0.4.12`。
6. **量化敏感性**: 原文专门提示,量化后的模型对 **BOS token** 敏感,评估时必须传 `add_bos_token=True`,否则结果会失真。

---

## 【关键机制与数据】

**数据流(原文):**

```
加载 HF 模型(Meta-Llama-3-8B-Instruct)
        ↓
准备校准数据(ultrachat 512 条 × 2048 tokens,经 chat template 预处理)
        ↓
oneshot() 应用 [SmoothQuantModifier(0.8) + GPTQModifier(W8A8, 忽略 lm_head)]
        ↓
save_pretrained(save_compressed=True) → Meta-Llama-3-8B-Instruct-W8A8-Dynamic-Per-Token/
        ↓
vLLM LLM("./...-W8A8-Dynamic-Per-Token") 加载推理
        ↓
lm_eval → gsm8k (5-shot, limit=250) 评测
```

**性能/规模数据(原文):**
- 校准样本数: **512**(起点,精度下降则增加)
- 序列长度: **2048**(起点)
- 评测任务: `gsm8k`,**5-shot** (`--num_fewshot 5`),样本上限 **`--limit 250`**,batch_size 为 `auto`
- 模型示例: `meta-llama/Meta-Llama-3-8B-Instruct`(8B 规模)
- SmoothQuant 平滑强度: **`0.8`**

**模型输出命名约定(原文):** `<model-name>-W8A8-Dynamic-Per-Token`,由 `MODEL_ID.split("/")[1]` 拼接而成。

**指标数字/加速比等量化效果: 原文未提供任何加速比、显存节省百分比或 accuracy 数值。**

---

## 【表格解读】

**原文无表格。** 整篇文档未出现任何 markdown 表格、参数对照表或性能对比表。量化配置信息以代码块和散文形式给出。

---

## 【公式解读】

**原文无公式。** 文档未出现任何 LaTeX 数学公式或伪代码形式的算式。量化过程仅以 Python 代码配方(recipe)和命令行参数描述。

---

## 【关联】

- **替代/互补特性 — [FP8](fp8.md)**: 原文在硬件不支持 INT8 的告警(WARNING)区块中明确指引:Blackwell 架构(计算能力 ≥ 10.0)上 INT8 不可用,**应改用 FP8 量化**(链接至 `fp8.md`),这是本文档最直接指向的内部特性替代方案。
- **依赖生态**:
  - [llm-compressor](https://github.com/vllm-project/llm-compressor/)(`vllm-project` 旗下):提供 `oneshot`、`GPTQModifier`、`SmoothQuantModifier` 等核心 API,问题反馈渠道也指向该仓库的 [issues](https://github.com/vllm-project/llm-compressor/issues)。
  - [lm-evaluation-harness](https://github.com/EleutherAI/lm-evaluation-harness) (`>= 0.4.12`):用于量化后的精度评测。
  - Hugging Face [`neuralmagic/int8-llms-for-vllm`](https://huggingface.co/collections/neuralmagic/int8-llms-for-vllm-668ec32c049dca0369816415):Neural Magic 提供的**预量化 INT8 模型集合**,作为开箱即用的捷径。
- **上游模型**: 文档示例以 `meta-llama/Meta-Llama-3-8B-Instruct` 为模板,适用于通用指令微调 LLM 的量化改造;若为已 fine-tune 模型,最佳实践建议改用训练数据子集做校准(原文: "If you've fine-tuned a model, consider using a sample of your training data for calibration")。

---

## 【使用方法】

**启用与配置(原文涉及的部分):**

1. **环境安装**:
   ```bash
   # 量化环境(独立 venv)
   (venv-llm-compressor) pip install llmcompressor
   # 推理/评测环境(独立 venv)
   (venv-llm-compressor) pip install llmcompressor
   (venv-llm) pip install vllm "lm-eval[api]>=0.4.12"
   ```

2. **加载与校准数据准备**:
   ```python
   MODEL_ID = "meta-llama/Meta-Llama-3-8B-Instruct"
   NUM_CALIBRATION_SAMPLES = 512
   MAX_SEQUENCE_LENGTH = 2048
   # 使用 ultrachat_200k train_sft split,seed=42 shuffle
   ```

3. **应用量化(核心 recipe)**:
   ```python
   from llmcompressor import oneshot
   from llmcompressor.modifiers.quantization import GPTQModifier
   from llmcompressor.modifiers.smoothquant import SmoothQuantModifier

   recipe = [
       SmoothQuantModifier(smoothing_strength=0.8),
       GPTQModifier(targets="Linear", scheme="W8A8", ignore=["lm_head"]),
   ]
   oneshot(model=model, dataset=ds, recipe=recipe,
           max_seq_length=MAX_SEQUENCE_LENGTH,
           num_calibration_samples=NUM_CALIBRATION_SAMPLES)
   model.save_pretrained(SAVE_DIR, save_compressed=True)
   ```

4. **在 vLLM 中加载量化模型**:
   ```python
   from vllm import LLM
   llm = LLM("./Meta-Llama-3-8B-Instruct-W8A8-Dynamic-Per-Token")
   ```

5. **精度验证命令**:
   ```bash
   lm_eval --model vllm \
     --model_args pretrained="./Meta-Llama-3-8B-Instruct-W8A8-Dynamic-Per-Token",add_bos_token=true \
     --tasks gsm8k \
     --num_fewshot 5 \
     --limit 250 \
     --batch_size 'auto'
   ```
   ⚠️ **务必带上 `add_bos_token=True`** —— 原文明确指出量化模型对 BOS token 敏感。

6. **直接使用预量化模型(无需自行量化)**: 访问 Hugging Face 集合 [`neuralmagic/int8-llms-for-vllm`](https://huggingface.co/collections/neuralmagic/int8-llms-for-vllm-668ec32c049dca0369816415) 下载已量化 checkpoint,直接进入步骤 4 加载即可。

7. **服务/CLI 启动参数、OpenAI 兼容 server 配置项**: **原文未涉及**(本文档仅描述本地 Python 加载与 `lm_eval` 评估路径,未给出 `vllm serve` 启动命令或 API server 相关参数)。
