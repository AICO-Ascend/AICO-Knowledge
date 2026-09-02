# Quantized KV Cache

> 仓 `vllm` · 路径 `docs/features/quantization/quantized_kvcache.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm/docs/features/quantization/quantized_kvcache.md

# 深度解读:Quantized KV Cache (FP8 KV-Cache 量化)

## 【定位】
本文档描述 vLLM 中 **FP8 KV Cache 量化**能力:通过对注意力机制的 Key/Value(在 Flash Attention 3 后端下还包括 Query)缓存张量进行 FP8 量化,显著压缩 LLM 推理时的显存占用,从而支持更长上下文窗口与更高吞吐,并给出两种 scale 校准路径、skip-layer 机制与可执行示例。

---

## 【技术要点】

1. **支持两种 FP8 KV-Cache 量化粒度**(原文逐字):
   - Per-tensor:`q/k/v_scale = [1]`,整个 Q/K/V 张量各共用一个 scale。
   - Per-attention-head:`q_scale = [num_heads]`,`k/v_scale = [num_kv_heads]`,每个注意力头独立一个 scale。

2. **Flash Attention 3 联动的全链路 FP8**:使用 FA3 后端 + FP8 KV cache 时,attention 运算也保持在 FP8 域,**Query 同样被量化到 FP8**(与 K、V 一起)。Per-attention-head 量化**仅在 Flash Attention 后端**可用,且必须走 **llm-compressor** 校准通路。

3. **三种 `kv_cache_dtype` 取值**(原文逐字):
   - `"fp8"` —— 默认,所有 scale = 1.0,无校准。
   - `"auto"` —— 采用模型自身默认 dtype。
   - `"fp8_e4m3"` —— 支持 CUDA 11.8+ 与 ROCm(AMD GPU)。
   - `"fp8_e5m2"` —— 支持 CUDA 11.8+。

4. **校准路径分两类**:① 无校准(`kv_cache_dtype="fp8"`,scale 全部置 1.0);② 推荐路径——借助 `llm-compressor` 在校准数据集(`HuggingFaceH4/ultrachat_200k`,示例 `NUM_CALIB_SAMPLES = 512`,`MAX_SEQ_LEN = 2048`)上做 one-shot 校准,以获得更高精度。

5. **按层跳过量化**:`--kv-cache-dtype-skip-layers` 标志可按**层索引**(如 `0 1 23`)或**层类型名**(如 `sliding_window`)让指定 attention 层保持原模型 dtype,其余层仍按所选量化 dtype 缓存——用于保护对量化敏感的层(如 sliding-window)。

6. **`QuantizationModifier` 双 scheme 配方**(原文代码逐字):
   - `config_groups["attention"]`:target = `["LlamaAttention"]`,`input_activations = fp8_args` —— 对 query 量化得到 `q_scale`。
   - `kv_cache_scheme = fp8_args` —— 对 KV cache 量化得到 `k_scale / v_scale`。
   - `fp8_args = QuantizationArgs(num_bits=8, type="float", strategy="tensor"|"attn_head")`。

---

## 【关键机制与数据】

- **核心动机**(原文):KV cache 量化到 FP8 → 显存占用下降 → **可缓存更多 token → 提升吞吐 + 支持更长上下文窗口**。
- **数据流(运行时)**:`LLM(model=..., kv_cache_dtype="fp8", ...)` 在每步推理把 attention 计算产生的 K/V 张量按所选 scheme(per-tensor 或 per-attention-head)映射到 FP8 域,使用 scale 还原回计算精度;FA3 后端下,Query 也参与同样量化。
- **数据流(离线校准)**:`AutoModelForCausalLM.from_pretrained(MODEL_ID, torch_dtype="auto")` → `load_dataset("HuggingFaceH4/ultrachat_200k", split="train_sft[:512]")` → `ds.shuffle(seed=42)` → `oneshot(model, dataset=ds, recipe=recipe, max_seq_length=2048, num_calibration_samples=512)` → `model.save_pretrained(save_dir, save_compressed=True)`,生成 `{MODEL}-kvattn-fp8-{STRATEGY}` 目录,可直接交给 vLLM serving 使用。
- **性能/精度数字**:原文**未给出**任何显存节省比例、吞吐数字或精度损失数字,亦无基准测试表——所有定量结论仅以"显著降低内存/支持更长上下文"等定性表述出现。**(原文无具体性能数据)**

---

## 【表格解读】

**原文无表格。** 文档通过分点说明(`q/k/v_scale = [1]`、`q_scale = [num_heads]`、`k/v_scale = [num_kv_heads]`)与代码块表达 scheme 与参数,未以表格形式罗列参数。

---

## 【公式解读】

**原文无公式。** 文档未给出数学公式或伪代码表达式;量化机制通过 `QuantizationArgs(num_bits=8, type="float", strategy=...)` 等参数化 API 描述,scale 的具体计算由 `llm-compressor` 内部完成,本文档未展开。

---

## 【关联】

- **依赖/调用方**:`llm-compressor`(`llmcompressor.oneshot`、`QuantizationModifier`)—— 提供校准通路与 per-attention-head scheme,是文档中显式标注的唯一外部依赖。
- **数据源**:`datasets.load_dataset("HuggingFaceH4/ultrachat_200k", split="train_sft")` —— 校准样本来源。
- **上游模块**:`vllm.LLM` / `SamplingParams`、`vllm serve` CLI —— 消费离线量化产物并启用 `kv_cache_dtype="fp8"`。
- **联动后端**:Flash Attention 3(开启 FP8 KV cache 时启用全链路 FP8 attention);Flash Attention(per-attention-head 量化唯一支持后端)。
- **层类型联动**:`sliding_window` attention layer —— 作为 `--kv-cache-dtype-skip-layers` 的典型敏感层示例。
- **官方示例仓**:`https://github.com/vllm-project/llm-compressor/tree/main/examples/quantization_kv_cache`(原文提供链接,作为更详细示例的来源)。
- **内部链接**:本文末标注 **(无)**。

---

## 【使用方法】

**A. 服务端 CLI**(原文逐字):
```bash
vllm serve <model> \
  --kv-cache-dtype fp8 \
  --kv-cache-dtype-skip-layers sliding_window
# 或按层索引跳过:
vllm serve <model> \
  --kv-cache-dtype fp8 \
  --kv-cache-dtype-skip-layers 0 1 23
```

**B. Python 编程接口(无校准)**(原文逐字):
```python
from vllm import LLM, SamplingParams
sampling_params = SamplingParams(temperature=0.7, top_p=0.8)
llm = LLM(
    model="meta-llama/Llama-2-7b-chat-hf",
    kv_cache_dtype="fp8",
)
```
带 skip-layer 的等价写法(原文逐字):
```python
llm = LLM(
    model="meta-llama/Llama-3.1-8B-Instruct",
    kv_cache_dtype="fp8",
    kv_cache_dtype_skip_layers=["sliding_window"],
)
```

**C. 推荐路径:离线校准生成量化模型**(原文逐字要点):
1. `pip install llmcompressor`
2. 构造 recipe:
   ```python
   fp8_args = QuantizationArgs(num_bits=8, type="float", strategy=STRATEGY)
   recipe = QuantizationModifier(
       config_groups={
           "attention": QuantizationScheme(
               targets=["LlamaAttention"],
               input_activations=fp8_args,
           )
       },
       kv_cache_scheme=fp8_args,
   )
   ```
   其中 `STRATEGY = "tensor"` 或 `"attn_head"`。
3. `oneshot(model, dataset=ds, recipe=recipe, max_seq_length=2048, num_calibration_samples=512)`,数据集来自 `HuggingFaceH4/ultrachat_200k` 的 `train_sft` 前 512 条,经 `shuffle(seed=42)` 打乱。
4. `model.save_pretrained(save_dir, save_compressed=True)` 保存到 `{模型名}-kvattn-fp8-{STRATEGY}` 目录,再交给 `vllm serve` 或 `LLM(...)` 加载。
5. 切换 model id 至上述 `save_dir`,复用 `kv_cache_dtype="fp8"` 即可在推理时启用已校准的 KV cache scale。
