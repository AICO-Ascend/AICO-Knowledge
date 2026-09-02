# chunked_scheduler

> 仓 `xllm` · 路径 `docs/src/content/docs/zh/features/chunked_scheduler.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/xllm/docs/src/content/docs/zh/features/chunked_scheduler.md

# ChunkedPrefill调度器 — 一体化深度解读

---

## 【定位】

本文档介绍 xLLM 推理引擎中 **Chunked Prefill（分块预填充）调度策略**的功能、开启方式与性能收益，回答"如何通过将长 prompt 切分为多个 chunk 来降低显存峰值、提升 Device 利用率，并改善与 decode 阶段请求的混合调度"这一问题。

---

## 【技术要点】

- **核心思想**：将长 prompt 拆分为多个较小的 chunk 进行分批处理，而非一次性处理整个 prompt（原文："将长prompt分割成多个较小的chunk进行分批处理，而不是一次性处理整个prompt"）。
- **三大收益**（原文明确列出）：① 有效降低显存峰值使用量；② 提高 Device 利用率；③ 更好地与 decode 阶段的请求进行调度和混合处理。
- **功能开关方式**：通过 **gflag 参数**向外暴露控制开关（原文："上述策略已在xLLM实现，并向外暴露gflag参数，控制功能的开关"）。
- **必选开关**：`--enable_chunked_prefill=true` 用于启用该策略。
- **可选参数**：`--max_tokens_per_chunk_for_prefill=20480`，用于设置每个 chunk 的大小；若不手动设置，默认等于 `max_tokens_per_batch`（原文："如果不手动设置chunked size，则默认等于max_tokens_per_batch"）。
- **实测性能**：在 Qwen3-8B 模型上、TPOT 限制为 50ms 的条件下，开启 chunked_prefill 后 **TTFT 时延下降 46%**（原文："限制TPOT 50ms，TTFT时延 **下降46%**"）。

---

## 【关键机制与数据】

### 工作机制（原文提炼）

- **分块处理**：长 prompt 被分割为多个较小的 chunk，逐批送入推理管线，避免单次完整 prefill 对显存的瞬时压力。
- **混合调度友好性**：将 prefill 拆分为多个较小计算单元后，可以与 decode 阶段的请求进行更细粒度的混合调度（interleaved scheduling），从而提升 Device 利用率。
- **chunk size 来源**：chunk 大小由 `max_tokens_per_chunk_for_prefill` 显式控制，或在未设置时回退为 `max_tokens_per_batch`。

### 数据/性能（原文明确给出的）

| 项目 | 内容 | 出处 |
|---|---|---|
| 模型 | Qwen3-8B | 原文性能小节 |
| TPOT 约束 | 50ms | 原文性能小节 |
| 性能指标 | TTFT 时延下降 **46%** | 原文性能小节 |
| `max_tokens_per_chunk_for_prefill` 默认值 | `20480`（示例值） | 原文使用方式 |
| chunk size 缺省回退值 | `max_tokens_per_batch` | 原文使用方式 |

> 原文未给出更细粒度的数据流描述、显存峰值绝对数值或吞吐量数据，本节不做臆造。

---

## 【表格解读】

**原文无表格。**

文档以纯文字段落+代码片段形式组织，未包含任何 markdown 表格，因此本节按要求标注"原文无表格"。

---

## 【公式解读】

**原文无公式。**

文档未出现任何 LaTeX 公式或伪代码形式的数学表达式，因此本节按要求标注"原文无公式"。

---

## 【关联】

**原文无内部链接。** 用户提供的元数据明确标注"内部链接: (无)"，因此本节不进行臆造性关联。

从原文语义可观察到的上下游逻辑联系（仅基于文档自述，未引用外部链接）：
- **与 decode 阶段的关系**：chunked prefill 通过将 prefill 切分，使 prefill 计算块能更细粒度地与 decode 请求交织调度，属于 prefill–decode 联合调度范畴（原文："能够更好地与decode阶段的请求进行调度和混合处理"）。
- **与 batch 配置的关系**：chunk size 的缺省值复用 `max_tokens_per_batch`，表明该参数与 xLLM 现有的 batch 容量配置存在直接耦合（原文："默认等于max_tokens_per_batch"）。
- **与 SLO 约束的关系**：性能数据中显式出现 TPOT 50ms 的限制，说明该策略的收益评估与 TPOT/TTFT 这类时延指标直接挂钩。

> 文档自身未通过链接指向其他特性/模块页面（如 continuous batching、prefix caching 等），故不展开相关特性的具体描述。

---

## 【使用方法】

原文明确给出了完整的启用命令，分必选与可选两部分，原文如下：

```bash
--enable_chunked_prefill=true
--max_tokens_per_chunk_for_prefill=20480 # optional
```

要点说明（原文表述）：
1. **启用开关**：`--enable_chunked_prefill=true` —— 开启 chunked prefill 策略。
2. **chunk 大小（可选）**：`--max_tokens_per_chunk_for_prefill=20480` —— 设置每个 chunk 的 token 数上限；若不手动设置，则默认等于 `max_tokens_per_batch`。
3. **参数暴露形式**：通过 gflag 全局标志位参数对外暴露控制开关。
