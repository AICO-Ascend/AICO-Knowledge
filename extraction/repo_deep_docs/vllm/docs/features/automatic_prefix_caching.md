# Automatic Prefix Caching

> 仓 `vllm` · 路径 `docs/features/automatic_prefix_caching.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm/docs/features/automatic_prefix_caching.md

# Automatic Prefix Caching 文档深度解读

## 【定位】

这篇文档是对 vLLM「**Automatic Prefix Caching (APC)**」特性的功能导引文档,说明该特性**通过复用相同前缀的 KV cache 来跳过重复的 prefill 计算**,并给出启用方式、典型受益场景以及能力边界说明。需要深入实现细节时,以引用的设计文档为准。

---

## 【技术要点】

1. **机制核心**:APC 缓存已有 query 的 KV cache,新 query 若与已有 query 共享相同前缀,则直接复用该 KV cache,**跳过共享部分的重新计算**。
2. **启用方式**:在 vLLM engine 中设置 `enable_prefix_caching=True` 即可启用;完整示例见所引用的 `automatic_prefix_caching_offline.py`。
3. **优化阶段限定**:APC 只削减 **prefill 阶段** 的处理时间,**不削减 decode 阶段**(生成新 token)的时间。
4. **典型受益场景 ① 长文档问答**:对同一长文档(软件手册/年报等)重复查询时,长文档只被处理一次,后续 query 全部复用其 KV cache。
5. **典型受益场景 ② 多轮对话**:同一会话内多轮聊天时,历史对话的处理结果在后续轮次中被复用。
6. **能力边界**:APC 总体上不会降低 vLLM 的整体性能,但在不命中共享前缀、或回答很长(decode 占主导)时,无法带来性能收益;技术细节指向 `../design/prefix_caching.md`。

---

## 【关键机制与数据】

- **作用对象**:原文「caches the KV cache of existing queries」—— APC 的复用单位是已计算好的 **KV cache**,而非文本前缀本身。
- **触发条件**:原文「if it shares the same prefix with one of the existing queries」—— 命中条件是「与历史 query 共享前缀」。
- **复用结果**:原文「allowing the new query to skip the computation of the shared part」—— 命中后跳过共享段的计算。
- **典型性能收益(原文表述)**:针对长文档问答场景,原文「APC allows vLLM to serve future requests with **much higher throughput** and **much lower latency**」;长文档本身「only once」被处理。
- **多轮对话场景**:原文表述同样为「serve future requests with much higher throughput and much lower latency」。
- **不受益的场景(原文)**:① 原文「when the length of the answer is long」—— decode 占主导时无收益;② 原文「new queries do not share the same prefix with any of existing queries」—— 无可复用前缀时无收益。
- **总体性能影响**:原文「APC in general does not reduce the performance of vLLM」—— 作为通用陈述,说明启用 APC 不会对系统造成负面影响。
- 注:原文中**没有给出任何具体的数字指标**(如命中率、延迟减少百分比、token 数等),也未给出 KV cache 逐 token 的匹配粒度说明,这些细节被引导至设计文档。

---

## 【表格解读】

原文无表格。

---

## 【公式解读】

原文无公式。

---

## 【关联】

1. **设计实现细节**:`../design/prefix_caching.md` —— 原文以「Technical details on how vLLM implements APC can be found here」明确指向该文档,负责解释 APC 的底层实现原理(本页为功能使用侧说明)。
2. **离线使用示例**:`../../examples/features/automatic_prefix_caching/automatic_prefix_caching_offline.py` —— 原文作为「here is an example」链接,提供 `enable_prefix_caching=True` 设置的可运行样例。
3. **与两阶段推理的关系**:文档明确把 APC 的优化范围限定在「the prefilling phase」,与生成阶段的「decoding phase」做出区分,提示读者 APC 的改进面属于 prefill 而非 decode。

---

## 【使用方法】

- **启用开关**:在 vLLM engine 中将参数 `enable_prefix_caching=True` 即可启用 APC(原文给出该布尔参数名)。
- **可运行示例**:参引原文链接 `../../examples/features/automatic_prefix_caching/automatic_prefix_caching_offline.py`。
- **原文未涉及**:具体的命令行 flag、HTTP API 字段、KV cache 淘汰/TTL 策略、哈希匹配粒度(block-level/token-level)、最大缓存容量配置等参数,本文档均未给出;这些实现侧的可调参数应在所引用的 `../design/prefix_caching.md` 中查找。
