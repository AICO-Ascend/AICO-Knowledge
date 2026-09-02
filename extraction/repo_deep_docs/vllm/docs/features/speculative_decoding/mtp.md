# MTP (Multi-Token Prediction)

> 仓 `vllm` · 路径 `docs/features/speculative_decoding/mtp.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm/docs/features/speculative_decoding/mtp.md

# MTP (Multi-Token Prediction) 文档深度解读

## 【定位】
本文档系统介绍了 vLLM 中 **MTP（Multi-Token Prediction，多 Token 预测）推测解码**方法的使用方式,该方法利用目标模型自身的原生多 Token 预测能力进行推测解码,**无需单独的 draft 模型**,并重点说明了 Gemma 4 系列助手检查点与 MiMo-7B-Base 等支持 MTP 的模型的具体配置方法。

---

## 【技术要点】

1. **无独立 draft 模型的推测解码**:MTP 与基于 draft 模型的推测解码方法（如 EAGLE、draft model speculation）不同,直接利用目标模型自身的 MTP 能力,因此配置简单、无需额外模型。
2. **Gemma 4 助手检查点的特殊处理**:Gemma 4 助手检查点通过 `--speculative-config` 的 `model` 字段传入,但内部通过 `model_type: gemma4_assistant`(基于 tower 的变体)或 `model_type: gemma4_unified_assistant`(encoder-free Gemma 4 Unified 12B 变体)进行识别,统一映射到 `Gemma4MTPModel`。
3. **KV Cache 共享机制**:vLLM 在内部将 assistant 层与目标模型的 KV cache 进行共享(`share KV cache with the target model`),避免重复存储,提高显存利用率。
4. **支持的 Gemma 4 规模**:明确支持 E2B、E4B、12B、26B-A4B、31B 五种 Gemma 4 IT 助手检查点。
5. **`num_speculative_tokens` 参数**:控制推测解码的深度(spec depth),文档建议从较小的值(如 `1`)开始作为默认值。
6. **向后兼容性提示**:旧版本 vLLM 可能将 Gemma 4 助手检查点识别为通用 draft 模型(日志显示 `SpeculativeConfig(method='draft_model', ...)`),对多模态 Gemma 4 目标会在初始化时失败,需升级到包含 Gemma 4 MTP 支持的版本。

---

## 【关键机制与数据】

- **工作原理**(原文):MTP 使用目标模型自身的原生多 Token 预测能力,无需单独 draft 模型;Gemma 4 助手检查点作为辅助层(wire the assistant layers),其 KV cache 与目标模型**共享**,而非独立保存。
- **配置键值对**(原文):
  - `"method": "mtp"` —— 指定推测解码方法为 MTP。
  - `"model": "gg-hf-am/gemma-4-E2B-it-assistant"` —— 指定 Gemma 4 助手检查点。
  - `"num_speculative_tokens": 1` —— 推测深度参数。
- **典型 Serving 配置参数**(原文):`--tensor-parallel-size 1`、`--max-model-len 8192`(以 Gemma 4 E2B 为例)。
- **离线示例采样参数**(原文):`temperature=0.8, top_p=0.95`(XiaomiMiMo/MiMo-7B-Base 示例)。
- **支持模型清单**(原文):Gemma 4 IT 助手检查点——E2B、E4B、12B、26B-A4B、31B;XiaomiMiMo/MiMo-7B-Base。

---

## 【表格解读】

**原文无表格**。

---

## 【公式解读】

**原文无公式**。

---

## 【关联】

- **与同类推测解码方法的关系**:原文在"Notes"部分明确将 MTP 与 **EAGLE** 和 **draft model speculation** 并列,指出当模型不支持 MTP 时可改用这两种方法;同时强调 MTP 的特殊性在于利用**目标模型自身**的 MTP 能力。
- **Gemma 4 多模态场景的依赖**:旧版本 vLLM 在处理 Gemma 4 多模态目标时,若将助手检查点作为通用 draft 模型处理会初始化失败,说明 MTP 路径与 Gemma 4 的多模态处理管线存在绑定关系。
- **内部实现映射**:`gemma4_assistant` 与 `gemma4_unified_assistant` 两个 `model_type` 在 vLLM 内部均映射到 `Gemma4MTPModel`,是上游模型类型与 vLLM 内部实现的"适配层"。
- **推测解码家族**:MTP 是 vLLM 推测解码(SPECULATIVE_DECODING)特性集合中的一种实现,与 EAGLE、draft model 等并列存在。

---

## 【使用方法】

### 1. Gemma 4 + 助手检查点(Serving)
原文给出 Gemma 4 E2B 的启动命令示例:
```bash
vllm serve google/gemma-4-E2B-it \
    --tensor-parallel-size 1 \
    --max-model-len 8192 \
    --speculative-config '{"method":"mtp","model":"gg-hf-am/gemma-4-E2B-it-assistant","num_speculative_tokens":1}'
```
其中 `--speculative-config` 的关键字段:
- `method`:固定为 `"mtp"`;
- `model`:指定 Gemma 4 助手检查点路径(如 `gg-hf-am/gemma-4-E2B-it-assistant`);
- `num_speculative_tokens`:推测深度,推荐从 `1` 开始。

### 2. 离线推理(Offline)
使用 `vllm.LLM` 接口,传入 `speculative_config={"method": "mtp", "num_speculative_tokens": 1}`,完整示例见原文 Offline Example(MiMo-7B-Base + `SamplingParams(temperature=0.8, top_p=0.95)`)。

### 3. 在线 Serving(Online)
```bash
vllm serve XiaomiMiMo/MiMo-7B-Base \
    --tensor-parallel-size 1 \
    --speculative-config '{"method":"mtp","num_speculative_tokens":1}'
```
适用于本身原生支持 MTP 的模型(此处不需要额外指定 `model` 字段)。

### 4. 注意事项(原文 Notes)
- MTP 仅适用于 vLLM 中支持 MTP 的模型家族;
- `num_speculative_tokens` 建议从 `1` 开始;
- 模型不支持 MTP 时,应改用 EAGLE 或 draft model speculation。
