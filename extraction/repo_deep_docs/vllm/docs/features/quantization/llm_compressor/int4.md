# INT4 W4A16

> 仓 `vllm` · 路径 `docs/features/quantization/llm_compressor/int4.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm/docs/features/quantization/llm_compressor/int4.md

# INT4 W4A16 文档深度解读

## 【定位】
本篇文档描述 vLLM 中 **W4A16 (权重 INT4、激活 FP16) 权重量化** 能力及其基于 `llm-compressor` 库的端到端量化与精度评估流程, 适用于低 QPS 场景下的显存压缩与低延迟推理。

---

## 【技术要点】

1. **量化方案 W4A16**: 仅将权重压缩到 INT4 (4-bit 整数), 激活保持 FP16 (16-bit), 通过 `GPTQModifier(targets="Linear", scheme="W4A16", ignore=["lm_head"])` 指定。
2. **硬件支持范围**: 仅 NVIDIA GPU 且 compute capability > 8.0 (Ampere / Ada Lovelace / Hopper / Blackwell)。
3. **校准数据规模**: 默认 `NUM_CALIBRATION_SAMPLES = 512`, `MAX_SEQUENCE_LENGTH = 2048`, 数据源为 `HuggingFaceH4/ultrachat_200k` 的 `train_sft` split, 通过 `shuffle(seed=42).select(range(512))` 采样。
4. **量化参数 (核心 recipe)**: `num_bits=4`, `type=QuantizationType.INT`, `strategy=QuantizationStrategy.GROUP`, `group_size=128`, `symmetric=True`, `dynamic=False`, `actorder="weight"`, `dampening_frac=0.01`, `update_size=NUM_CALIBRATION_SAMPLES`。
5. **环境隔离**: `llm-compressor` 与 `vllm` 必须分别安装在 **两个独立 venv** (如 `venv-llm-compressor` 与 `venv-vllm`), 因二者可能存在依赖冲突。
6. **精度评估命令**: `lm_eval --model vllm --model_args pretrained=...,add_bos_token=true --tasks gsm8k --num_fewshot 5 --limit 250 --batch_size auto`, 强调必须传 `add_bos_token=True` 以避免量化模型对 BOS token 敏感。

---

## 【关键机制与数据】

### 工作流 (四步流水线)
原文给出明确的四阶段流程:

1. **加载模型**: 通过 `transformers.AutoModelForCausalLM.from_pretrained(MODEL_ID, device_map="auto", dtype="auto")` 加载基模型 (示例为 `meta-llama/Meta-Llama-3-8B-Instruct`)。
2. **准备校准数据**: 对 ultrachat 的 `messages` 字段应用 `tokenizer.apply_chat_template` 后再 tokenize 到 2048 长度, 强调校准数据应**贴合部署分布**。
3. **应用量化**: 调用 `llmcompressor.oneshot(model=model, dataset=ds, recipe=recipe, max_seq_length=..., num_calibration_samples=...)` 执行 GPTQ 一次性量化, 再以 `model.save_pretrained(SAVE_DIR, save_compressed=True)` 输出**已压缩的 checkpoint**, 命名为 `Meta-Llama-3-8B-Instruct-W4A16-G128`。
4. **在 vLLM 中评估**: `vllm.LLM("./Meta-Llama-3-8B-Instruct-W4A16-G128")` 直接加载压缩模型并由 `lm-evaluation-harness` 跑 `gsm8k`。

### 关键调参机制
原文未提供量化前后精度 / 吞吐量 / 显存占用数据, 只给出调参经验:
- **`dampening_frac`**: 控制 GPTQ 算法影响力, 较低值可提升精度但可能引发数值不稳定导致算法失败 (原文未给具体推荐值, 唯一示例为 0.01)。
- **`actorder="weight"`**: 按权重大小排序通道, 在不增加推理延迟的前提下提升精度。
- **`group_size=128` + 对称量化**: 组内对称量化是 INT4 的默认选择, 平衡精度与显存。
- 文档**未提供任何基准性能数字** (原文: 无推理速度/显存对比表, 无 perplexity/gsm8k 数值)。

### 数据流
`原始 HF 模型 → transformers 加载 → ultrachat 校准集 → GPTQ 量化 (Linear 层, 跳过 lm_head) → 保存为 W4A16-G128 checkpoint → vLLM 直接推理 → lm_eval 评估`

---

## 【表格解读】

**原文无表格**。所有配置以代码块形式呈现, 无 markdown 表格。

---

## 【公式解读】

**原文无公式**。文档以 recipe / Python 代码形式给出量化配置, 未列出任何数学公式或伪代码推导。

---

## 【关联】

- **上游工具链**:
  - [`llm-compressor`](https://github.com/vllm-project/llm-compressor/): 提供 `oneshot`、`GPTQModifier`、`SmoothQuantModifier` (原文中虽 import 了 `SmoothQuantModifier` 但最终基础 recipe 并未使用, 仅在代码片段中出现 import 语句)。
  - [`compressed_tensors`](https://github.com/vllm-project/compressed-tensors): 提供 `QuantizationArgs` / `QuantizationScheme` / `QuantizationStrategy` / `QuantizationType` 等用于构造自定义 recipe 的 schema 类。
  - [`transformers`](https://huggingface.co/docs/transformers): 通过 `AutoModelForCausalLM` / `AutoTokenizer` 完成原始模型加载。
  - [`datasets`](https://huggingface.co/docs/datasets): 拉取 `HuggingFaceH4/ultrachat_200k` 校准集。
  - [`lm-evaluation-harness`](https://github.com/EleutherAI/lm-evaluation-harness) (`lm-eval[api]>=0.4.12`): 精度评估入口。

- **预量化模型资源**:
  - [Neural Magic HF Collection (int4-llms-for-vllm)](https://huggingface.co/collections/neuralmagic/int4-llms-for-vllm-668ec34bf3c9fa45f857df2c): 提供可直接用 vLLM 推理的 INT4 量化 checkpoint。

- **完整示例代码**: [llama3_example.py](https://github.com/vllm-project/llm-compressor/blob/main/examples/quantization_w4a16/llama3_example.py)。

- **支持/反馈渠道**: [vllm-project/llm-compressor Issues](https://github.com/vllm-project/llm-compressor/issues)。

- **与同仓其他特性关系**: 该路径 `docs/features/quantization/llm_compressor/int4.md` 属于量化特性下 `llm_compressor` 子目录, 与其他量化方案 (如 AWQ、FP8、GPTQ 等) 共享同一父目录 `quantization/`, 但原文**未引用任何内部链接** (`内部链接: 无`)。

---

## 【使用方法】

### 安装 (双虚拟环境)
```bash
# 量化端
(venv-llm-compressor) pip install llmcompressor

# 推理与评估端
(venv-vllm) pip install vllm "lm-eval[api]>=0.4.12"
```

### 量化 (Python 一键脚本)
```python
recipe = GPTQModifier(targets="Linear", scheme="W4A16", ignore=["lm_head"])
oneshot(model=model, dataset=ds, recipe=recipe,
        max_seq_length=2048, num_calibration_samples=512)
model.save_pretrained("Meta-Llama-3-8B-Instruct-W4A16-G128", save_compressed=True)
```

### 推理 (vLLM 直接加载压缩模型)
```python
from vllm import LLM
llm = LLM("./Meta-Llama-3-8B-Instruct-W4A16-G128")
```

### 精度评估 (lm_eval)
```bash
lm_eval --model vllm \
  --model_args pretrained="./Meta-Llama-3-8B-Instruct-W4A16-G128",add_bos_token=true \
  --tasks gsm8k \
  --num_fewshot 5 \
  --limit 250 \
  --batch_size 'auto'
```

### 高级可调 recipe
通过 `QuantizationScheme` 显式展开配置, 关键开关: `actorder="weight"`、`dampening_frac=0.01`、`group_size=128`、`symmetric=True`、`dynamic=False`, 详见原文"Best Practices"章节代码块。
