# Adaptive Verification

> 仓 `vllm` · 路径 `docs/features/speculative_decoding/adaptive_verification.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm/docs/features/speculative_decoding/adaptive_verification.md

# Adaptive Verification 深度解读

## 【定位】
这篇文档描述 vLLM 中 **Adaptive Verification（自适应验证）** 能力：解决 speculative decoding 在高并发（batch size 上升）下"草稿 token 与真实 token 争抢算力、被拒 token 浪费算力"的吞吐瓶颈，让单一配置在整个负载区间内自适应地决定每步要验证多少草稿 token，从而消除按部署逐个调参 `num_speculative_tokens` 的负担。

## 【技术要点】

1. **核心思想**：把 `num_speculative_tokens` 从"每请求一个静态块大小"改为"每步基于生存概率打分后跨请求竞争 GPU 算力预算"。
2. **打分机制**：每个 (request, position) 草稿槽位用 *survival probability*（即该请求各位置置信度的累乘 / running product）打分，分数高的优先被接纳直至预算耗尽。
3. **跨请求竞争**：例如一个高置信请求的 position 5 可以胜过另一个低置信请求的 position 1，意味着前者保留完整块、后者在 1~2 个 token 后即被截断。
4. **算力预算来源**：在启动时通过 *cost model* 剖析（profile）每种 shape 下的一步成本，再选出使"每秒被接受的 token 数（accepted tokens/sec）"最大化的 token 数。
5. **当前支持范围**：仅 DSpark 且带 **confidence head** 的模型，因为需要逐位置（per-position）的接受率估计。
6. **关键默认与限制**：默认针对 8192 token 的合成 KV 上下文做 profile；需要 full cudagraphs（启动时拒绝 `--enforce-eager`）；与 LoRA、pipeline parallelism 不兼容；要求 attention backend 能容忍设备端决定的 query 长度（CPU 长度只是上界）。

## 【关键机制与数据】

**工作原理（原文视角串联）**

1. **背景矛盾**：speculative decoding 用更多算力换取更少 decode 步数。在 batch size 1 时 GPU 是 memory-bound，闲置算力让草稿 token 几乎免费；到了 batch size 256（原文数字），草稿与真实 token 同台争算力，且每拒绝一个 token 都意味着算力浪费，累计起来吞吐会下降。
2. **接受率衰减**：per-position acceptance 衰减很快。memory-bound 时该槽位几乎免费、值得博弈；一旦算力饱和，博弈就有真实吞吐代价。最优 crossover 点随负载与"随工作负载变化的接受率"漂移，因此没有静态的 `num_speculative_tokens` 能覆盖全并发区间。
3. **打分 + 准入循环**：
   - 输入：每一步所有 (request, position) 草稿槽位 + 各请求的位置级置信度。
   - 打分：槽位分数 = 该请求到该位置的 survival probability（各位置置信度累乘）。
   - 准入：按分数排序，挑出最高分槽位填入预算，直到全局算力预算花完。
4. **预算（Budget）来源**：vLLM 在启动时剖析每种 shape 下"一步"的开销，然后挑出最大化 *expected accepted tokens per second* 的 token 数。这是把"算力预算"这个抽象量换算为具体 token 数的方式。
5. **实际效果**：同一配置在低负载（memory-bound）和高负载（compute-bound）下都成立（原文："one configuration holds up across the whole load range"），从而消除按部署调 `num_speculative_tokens` 的需要。

**性能/权衡数据（原文给出的数字，原文标注）**

- 原文：batch size 1 下 speculative decoding "is a good trade"（GPU memory-bound，算力有余）。
- 原文：batch size 256 下 "every rejected token is compute wasted; with enough of them, throughput drops"——即被拒 token 直接削减吞吐。
- 原文：默认 profile 上下文长度 8192 tokens。
- 原文示例：调高到 131072 tokens 用于更长上下文的部署。
- 原文示例：`num_speculative_tokens: 7`（仅作为示例配置，不是最优值）。
- 原文："the cheap indexer is the main cost that scales with context length"——对稀疏注意力（如 DeepSeek-v4）来说 profile 上下文长度影响较小，因为主导开销是便宜的 indexer。

## 【表格解读】

原文无表格。

## 【公式解读】

原文无公式（文档以自然语言形式描述 "survival probability = 该请求各位置置信度的 running product" 与 "expected accepted tokens per second" 的优化目标，但未给出 LaTeX 或伪代码公式）。

## 【关联】

Adaptive Verification 是 vLLM **speculative decoding** 框架内的一个开关，与下列模块/特性有明确耦合：

- **Speculative decoding 基础机制**：本特性的所有设计动机都建立在"草稿 token 与目标 token 共享算力预算、且被拒 token 是浪费"这一前提上，与 speculative decoding 的整体目标一致。
- **`num_speculative_tokens`**：原参数在 adaptive verification 下变成"块大小的上界 / 草稿预算上限"，由框架按步动态调整每请求实际验证量。
- **DSpark 草稿方法**：当前唯一受支持的草稿方法；要求其带 **confidence head**，因为打分需要逐位置置信度。
- **`draft_sample_method`**：示例中配置为 `"probabilistic"`，说明在 DSpark 下自适应验证依赖概率式采样以暴露置信度。
- **Attention backend / attention selector**：需要 backend 能容忍 device 端决定的 query 长度（CPU 端给出的只是上界）；依赖 CPU 长度的 backend 会被 attention selector 排除，对硬编码 backend 的模型会在启动时拒绝。
- **CUDA graphs（`--enforce-eager` 对立项）**：step cost 是从 captured graphs 中 profile 得到的，因此要求 full cudagraphs；启用 `--enforce-eager` 会在启动时被拒。
- **LoRA**：不支持（因为 per-token LoRA 映射按 CPU 端边界构造，与 device 端动态长度不一致）。
- **Pipeline parallelism**：不支持（cost curves 与 confidences 只存在于最后那个 rank）。
- **稀疏注意力模型（DeepSeek-v4）**：profile 上下文长度的选择对其影响较小，因为占主导的、随上下文扩展的开销是"便宜的 indexer"。
- **环境变量 `VLLM_ADAPTIVE_VERIFICATION_PROFILE_CONTEXT_LEN`**：决定 cost profile 的合成 KV 上下文长度，是与本特性最直接的调参接口。

## 【使用方法】

**启用方式（原文示例命令）**：

```bash
vllm serve deepseek-ai/DeepSeek-V4-Flash-DSpark \
  --tokenizer-mode deepseek_v4 --trust-remote-code \
  --speculative-config '{
    "method": "dspark",
    "model": "deepseek-ai/DeepSeek-V4-Flash-DSpark",
    "num_speculative_tokens": 7,
    "draft_sample_method": "probabilistic",
    "enable_adaptive_verification": true
  }'
```

**关键配置项**：

- `enable_adaptive_verification: true` —— 打开自适应验证（默认关闭，原文："It is off by default"）。
- `enable_adaptive_verification: false` —— 关闭，对每个请求都验证完整块。
- `method: "dspark"` + `draft_sample_method: "probabilistic"` —— 当前必须组合（DSpark + 置信度头 / 概率采样），否则无法做 per-position 打分。
- `num_speculative_tokens: 7` —— 此处为示例值，表示草稿块大小的上界；实际每步每请求验证多少由框架动态决定。

**调优 profile（原文）**：

```bash
export VLLM_ADAPTIVE_VERIFICATION_PROFILE_CONTEXT_LEN=131072
```

默认值为 8192；当部署上下文显著更长时上调，可让 profile 出的 step cost 读到一个更真实大小的 cache（对稀疏注意力模型影响较小）。

**启动期约束（原文）**：

- attention backend 必须能容忍 device-decided query 长度，否则启动时被拒。
- 必须开启 full cudagraphs（`--enforce-eager` 会在启动时被拒）。
- 与 LoRA、pipeline parallelism 不兼容，原文未给出启用方式。
