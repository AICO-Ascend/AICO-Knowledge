# Sarathi-Serve — 技术点深读（DEEP 2026-08-18）

> 全要素深读笔记：文本技术点提炼 + 跨论文关系。独立文件，extract_phase1 重跑不丢。
> 论文：Taming Throughput-Latency Tradeoff in LLM Inference with Sarathi-Serve · arXiv:2403.02310

## 核心问题

LLM 推理每个请求分 prefill（compute-bound，并行处理整段 prompt）与 decode（memory-bound，每步一 token）两阶段，二者批处理行为截然相反：decode 批处理近线性提速而 prefill 几乎不受益于批处理（§3.1，Figure 3）。现有 scheduler 因此陷入吞吐-延迟 tradeoff：
- **Prefill-prioritizing**（Orca/vLLM，iteration-level + eager admission）：吞吐高但产生 **generation stalls**——一个长 prompt 的 prefill 可卡住所有 decode 数秒（Figure 1a 显示 vLLM stall 长达数秒），P99 TBT 飙升。
- **Decode-prioritizing**（FasterTransformer，request-level batching）：TBT 低但吞吐差，请求完成后批大小缩水、GPU 空转。
- **Pipeline bubbles**（§3.3）：PP 部署下微批次执行时间因 prefill/decode 组合差异巨大（Falcon-180B 一个 4k prompt prefill ≈1150ms vs batch=32 decode-only ≈200ms，bubble ≈950ms），浪费 GPU cycle。

## 关键创新点

### 1. Chunked-prefills（§4.1）
- **机制**：把长 prefill 按 token budget 切成近似等大的 chunk，跨多个 iteration 计算。两条 insight 支撑：(i) 单条 prefill 在 ~512 token 即可饱和 GPU compute（Figure 4），(ii) 实际 prompt 数千 token（sharegpt4 中位 1730、arxiv_summarization 中位 7059），可拆成仍能饱和 compute 的小单元。
- **效果**：相比"decode + full prefill"混合批（Orca naive hybrid，TBT 最多涨 28.3×），chunked 把每 iteration 计算量钳在预算内，TBT 受控（Figure 9）。开销可控：chunk=512 时 prefill runtime overhead ≤25%，chunk=2048 时几乎可忽略（§5.4.1，Figure 14）。

### 2. Stall-free batching（§4.2，Algorithm 3）
- **机制**：iteration-level 调度器，每轮按固定顺序填充 token budget τ：(1) 先放所有运行中的 decode token（lines 6-8），(2) 再放未完成 prefill 的下一个 chunk（lines 9-12），(3) 最后才在新预算内 admit 新请求的 chunk（lines 13-20）。τ 由 TBT SLO 反推。这样**新 prefill 不打断 ongoing decode**——decode 既不 stall 也不被 prefill 长尾拖死，prefill 也不被 decode 阻塞（双向 stall-free）。
- **效果**：相比 vLLM 的 eager prefill-prioritizing，P99 TBT 在 SLO 内可承载高得多的 load；Mistral-7B 单 A100 capacity ×2.6，Yi-34B 双 A100 最高 ×3.7，Falcon-180B 8×A100 PP 最高 ×5.6（摘要 + §5.1）。
- **副产物**：hybrid batch 计算量近似均匀 → 直接缓解 PP 的 pipeline bubbles（§4.2 末段，§5.3 验证）。

### 3. Token Budget 调参（§4.3）
- **机制**：τ 在"TBT SLO"与"chunking overhead"间权衡。小 τ → TBT 低但 chunking 多、KV-cache 重复读取（N 个 chunk 中第 1 个 KV 被加载 N-1 次）+ kernel launch 固定开销 + 低 arithmetic intensity。还须考虑 **tile-quantization**（matmul tile 边界，chunk=257 比 256 prefill 时间多 32%）。PP 场景还要兼顾 bubble。论文用 **Vidur**（LLM inference profiler/simulator，[28]）一次性 profile 选 τ。
- **实际取值**（§5.1）：relaxed SLO 用 τ=2048，strict SLO 用 τ=512；LLaMA2-70B relaxed 特殊用 τ=1536 以压 PP bubble。τ 可按 SLO 动态切（动态 τ 留作 future work）。
- **效果**：Yi-34B strict SLO（100ms）下用 τ=512 比 vLLM ×3.5 capacity；Yi-34B relaxed（1s）用 τ=2048 比 vLLM ×1.65（§5.2，Figure 12）。

### 4. 使 Pipeline Parallel 可行（§5.3）
- **机制**：uniform hybrid batch 天然平衡 PP 微批次执行时间，消除三类 bubble：PB1（连续微批 prefill token 数不一）、PB2（prefill 后接 decode 的计算时差）、PB3（decode attention cost 随 KV-cache 上下文长度变）。
- **效果**：Falcon-180B 跨节点（2 节点 ×4 A100，100Gbps Ethernet）TP4-PP2 相比 vLLM TP8（跨节点 all-reduce）：median TBT decode-only 低 >2×（TP8 cross-node 比 TP4-in-node+PP-cross-node 高 2×，Figure 13a）；strict SLO 下 capacity ×3.6 over vLLM hybrid，×4.3 over vLLM TP-only；relaxed SLO 下 ×1.48（§5.3）。

## 表格（原文结构化）

### Table 1：模型与 GPU 配置
| Model | Attention | GPU Config | Memory (per-GPU) |
|---|---|---|---|
| Mistral-7B | GQA-SW | 1 A100 | 80GB (80GB) |
| Yi-34B | GQA | 2 A100 (TP2) | 160GB (80GB) |
| LLaMA2-70B | GQA | 8 A40 (TP4-PP2) | 384GB (48GB) |
| Falcon-180B | GQA | 4 A100s×2 nodes (TP4-PP2) | 640GB (80GB) |

### Table 2：数据集（prompt/output token 统计）
| Dataset | Prompt Median / P90 / Std | Output Median / P90 / Std |
|---|---|---|
| openchat_sharegpt4 | 1730 / 5696 / 2088 | 415 / 834 / 101 |
| arxiv_summarization | 7059 / 12985 / 3638 | 208 / 371 / 265 |

### Table 3：各模型 SLO（P99 TBT，秒）
| Model | Relaxed SLO (SLO-R) | Strict SLO (SLO-S) |
|---|---|---|
| Mistral-7B | 0.5 | 0.1 |
| Yi-34B | 1 | 0.2 |
| LLaMA2-70B | 5 | 1 |
| Falcon-180B | 5 | 1 |

SLO 定义：strict = 5× decode-only iteration 时延，relaxed = 25×（4k prefill、batch=32 基线）。

### Capacity 增益（Figure 10/11，Sarathi-Serve vs Orca/vLLM，相对倍数）
| Model | Dataset | vs Orca (SLO-S / SLO-R) | vs vLLM (SLO-S / SLO-R) |
|---|---|---|---|
| Mistral-7B | sharegpt4 | 2.78× / 2.15× | 4.00× / 2.44× |
| Yi-34B | sharegpt4 | — / — | 3.69× / 1.94× |
| Mistral-7B | arxiv_summ | 1.82× / 1.97× | 1.69× / 1.94× |
| Yi-34B | arxiv_summ | — / — | — / — |
| LLaMA2-70B | sharegpt4 | 5.54× / 6.31× | 4.69× / 5.62× |
| Falcon-180B | sharegpt4 | — / — | 4.30× / 3.60× (TP8/TP4-PP2) |
| LLaMA2-70B | arxiv_summ | 4.60× / 3.00× | 4.20× / 2.75× |

### Table 4：消融（Yi-34B，2×A100，τ=1024，128 请求，秒）
| Scheduler | sharegpt4 P50 TTFT / P99 TBT | arxiv_summ P50 TTFT / P99 TBT |
|---|---|---|
| hybrid-batching-only | 0.53 / 0.68 | 3.78 / 1.38 |
| chunked-prefills-only | 1.04 / 0.17 | 5.38 / 0.20 |
| **Sarathi-Serve (combined)** | **0.76 / 0.14** | **3.90 / 0.17** |

结论：两技术互补——chunking-only 伤 TTFT（prefill chunk 低效），hybrid-only 伤 TBT（长 prefill 仍 stall），合用两指标都最优。

## 与同类对比

- **vs vLLM**（prefill-prioritizing + PagedAttention）：vLLM eager admit prefill，generation stall 不可避免；即使 PagedAttention 允许大 batch，实际受 TBT SLO 限制三种 batch size（32/64/128）capacity 几乎相同（Figure 12）——大 batch 用不上。Sarathi-Serve 用 τ 精细控制 tradeoff，strict SLO 下 Yi-34B ×3.5 capacity。
- **vs Orca**（prefill-prioritizing + iteration-level，支持 hybrid batch 但不 chunking）：Orca 虽支持混合批，但整个 prefill 一 iteration 跑完，长 prompt 仍 stall；且无 PagedAttention + activation memory 大，batch size 远小于 vLLM，relaxed SLO 下反被 vLLM 反超。
- **vs FasterTransformer**（decode-prioritizing, request-level）：无 stall 但吞吐低一个数量级（vLLM iteration-level + PagedAttention 比 FT 高 ~10×）。
- **vs Disaggregated（SplitWise/DistServe/TetriInfer，§6）**：disagg 把 prefill/decode 物理分离到不同 replica，彻底消除干扰、prefill 最大效率（TTFT 更好），但代价是 KV-cache 跨 replica 迁移（无 high-bandwidth interconnect 难做）+ prefill replica 的 GPU memory 利用率低（不存 KV）。论文把与 disagg 的定量对比留作 future work。
- **vs FastServe**：preemption-based 调度减 head-of-line blocking，与 Sarathi 正交可叠加。

## 跨论文关系（→ MOC 谱系）

- **直接继承 [[sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills]]**：Sarathi-Serve 是 SARATHI 的 serving 化演进——chunked-prefills + piggybacking decodes 机制源自 SARATHI，Sarathi-Serve 把它做成 production-grade online server（命名也直接延续），新增 stall-free scheduling + token budget 调参 + PP 优化，并补齐与 vLLM/Orca 的端到端 capacity 对比。两文同一作者团队（Microsoft Research India + Georgia Tech）。
- **互补 [[sglang-efficient-execution-of-structured-language-model-programs]]**：SGLang 做"多调用间 KV 前缀复用 + 结构化输出加速"，Sarathi-Serve 做"单 replica 内 prefill-decode 混合调度"——正交维度，可叠加（SGLang runtime 下层换 Sarathi-Serve 调度器）。
- **对比/互补 [[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]**：Mooncake 走 disagg 路线（prefill/decode 分离 + KV 跨节点池化），把 KV-cache 迁移做成一等公民；Sarathi-Serve 走 collocated hybrid batch 路线（同 replica 内 chunk 混合），不需要 KV 迁移但 prefill 不能完全高效。两种哲学对 prefill-decode 干扰的不同解法——Mooncake 用"物理隔离"，Sarathi-Serve 用"时间分片 + 预算钳制"。论文 §6 明确把 disagg 列为第三类并讨论其 tradeoff。
- **演进路线**：Sarathi-Serve 的 chunked-prefill 已被业界广泛采纳（vLLM 后续版本、APIServe [26] 等），是现代 LLM serving 调度的事实标准基线之一。

## 局限与边界

- **chunking 不为零开销**：小 chunk（512）有 ≤25% prefill overhead；τ 太小会因 kernel launch + 重复 KV 读取 + 低 arithmetic intensity 而伤效率。τ 选择依赖一次性 profile（用 Vidur），非自适应。
- **tile-quantization 陷阱**：τ 不整除 tile size 会显著拖慢 prefill（chunk=257 比 256 多 32%），需硬件感知选 τ。
- **动态 τ 未实现**：τ 按 SLO 静态选，按 workload 动态调 τ 留作 future work。
- **与 disagg 未定量对比**：论文承认未做 Sarathi-Serve vs SplitWise/DistServe 的定量评测，disagg 在 TTFT 上可能更优。
- **仅 evaluate GQA 模型**（Mistral/Yi/LLaMA2/Falcon），未涉 MQA-only 或 MHA 模型；长 context（>16k）场景未评测（数据集已截断到 8192/16384）。
- **基于 vLLM fork 实现**，是 research prototype，"doesn't have complete feature parity with open-source vLLM"（Artifact Appendix），生产可用性需自行补齐。
- **TBT SLO 定义依赖基线 decode 时延**（5×/25×），不同 batch size / prefill length 的基线选取会影响 SLO 严格度的可比性。
