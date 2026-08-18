# 跨论文关系与演进（人工维护）

> 独立文件，extract_phase1 重跑不丢。MOC.md 通过 `![[moc_relations]]` 嵌入此页。
> 由夜间深读（DEEP_LEARNING_PROTOCOL）逐篇补充、串联。绝不猜来源，仅基于已读论文确证的关系。

## KV cache 复用谱系
- **vLLM / PagedAttention**（#52 Efficient Memory Management…PagedAttention）：分页 KV 奠基，按单请求分块管理、用完即弃。
- **SGLang RadixAttention**（#43）：把"简单系统提示共享"升级为"radix tree + 叶子优先 LRU + cache-aware 调度"多级树结构自动复用，覆盖 few-shot/self-consistency/multi-turn/ToT 四级共享模式。
- **Mooncake**（#45）：同机 → 跨节点 disagg，KV 在 GPU/CPU/DRAM/SSD 分层迁移。
- **IndexCache**（#1）：跨层 sparse attention 索引复用，正交于 SGLang 前缀复用。
- **Prefill-as-a-Service**（#58）：Mooncake 跨节点思想的进一步跨数据中心规模化。

## 调度谱系
- **Sarathi**（#17）：prefill-decode 混合（piggyback decodes on chunked prefills）。
- **Sarathi-Serve**（#18）：吞吐-延迟折中调度优化。
- **SGLang**（#43）：多调用间前缀复用调度，与 Sarathi 正交可叠加。

## 推测解码谱系
- **Medusa**（#2）→ **EAGLE**（#4）→ **EAGLE-2**（#5）→ **EAGLE-3**（#3）：多头/特征不确定性 → 动态 draft 树 → 训练时测试扩展。
- **Block Diffusion**（#6）→ **DFlash**（#7）/ **DSpark**（#8）：块级半自回归扩散解码分支。
- **JetSpec**（#9）：并行树 drafting 破 scaling 上限。
- **LongSpec**（#59）/ **SpecExtend**（#60）：长上下文场景的 draft 与上下文增强。

## 训练系统谱系
- **Megatron-LM**（#49）→ **Megatron-LM 分布式**（#48）→ **MegaScale**（#46）：模型并行 → 大规模 GPU 集群 → 万卡级。
- **ZeRO**（#47）：内存优化，与 Megatron 正交可组合。
- **Megatron Core MoE**（#12）：MoE 可扩展训练。

## RL 系统谱系
- **DeepSeek-R1**（#34）→ **Search-R1**（#25）：RL 激励推理 → RL + 搜索引擎。
- **HybridFlow**（#30）/ **AREAL**（#33）：统一灵活 RLHF 框架 / 大规模异步 RL 系统。
- **GEPA**（#16/#19）：反思式 prompt 进化，可超越 RL——与 RL 路线互补对比。GEPA 在**复合多模块系统 + 富 textual feedback** 任务上省 ~35× rollouts 超 RL；但 **AIME 纯数学单步 CoT** 上 GRPO 仍领先（Qwen3 8B: GRPO 38 vs GEPA 32）。注意 GEPA budget 按 MIPROv2 逐基准对齐（≤10.15% 差异），GRPO 固定 24k rollouts——"省 rollout"是样本效率论证非严格同预算赛。GEPA 也可作 RL 系统 prompt 侧增强。

## 线性/混合注意力谱系
- **Gated DeltaNet / Mamba2 / GLA** → **KDA**（[[kimi-linear-an-expressive-efficient-attention-architecture]]）：KDA 把 GDN 的 head-wise 粗门控升级为 **channel-wise 细门控**（每特征维独立遗忘率）+ DPLR 变体定制 chunkwise 算法。
- **Kimi Linear** 3:1 混合 KDA 与全 MLA，首次公平对比下（1.4T tokens）混合线性架构**全面超越**全注意力（MMLU-Pro 51.0 vs 47.2、RULER 84.3 vs 81.3），KV cache −75%、1M 上下文 TPOT 6.3×。
- 互补 [[gated-delta-networks-improving-mamba2-with-delta-rule]]：同属 delta-rule 线性注意力改进分支，正交于 [[indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse]] 的跨层稀疏索引复用。

## 残差/层间拓扑谱系
- **[[hyper-connections]]**（ByteDance Seed, ICLR 2025）是基底方法：把残差连接换成学习的 `(n+1)×(n+1)` 连接矩阵（深度+宽度连接，可选输入自适应动态权重 DHC），是 Pre/Post-Norm → ResiDual/Altup 家族的可学习残差超类。
- **[[hc-manifold-constrained-hyper-connections]]**（#36）/ **[[mhc-manifold-constrained-hyper-connections]]**：HC 的流形约束变体，对 HC 可学习/动态连接权重（Eq.8–13）施加几何正则化。HC 提供载体，HC/mHC 约束其流形结构。
- HC 不增推理 KV-cache 开销（早期隐藏态可在下一层前释放），与稀疏注意力正交，可在长上下文部署中堆叠。

## 推测解码 tree-attention 分支
- **[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]**：多头并行预测 + tree attention 一次校验多候选，无需 draft 模型（>2.2× 无损 / 2.3-2.8× MEDUSA-2）。
- **[[deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference]]**：DeFT 是 attention kernel 层 IO 优化（非 draft/树构造优化），把 Medusa tree-attention 验证 kernel 换成 Flash Tree-attention——给定树拓扑下 attention 1.02-1.70× over Medusa attention，端到端解码最高 2.23×。KV IO 几乎不随候选树规模 `ln` 增长（73-99% KV IO reduction）→ 与 [[jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting]]（并行树起草扩大候选）天然搭档。
- **EAGLE 系列**（[[eagle-speculative-sampling-requires-rethinking-feature-uncertainty]]/[[eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees]]）改进 draft 质量 + 动态 draft tree；DeFT 仅优化给定树的验证 kernel，可作 EAGLE-2 动态树验证阶段的 drop-in 升级。
- **[[sglang-efficient-execution-of-structured-language-model-programs]]** RadixAttention 是 DeFT 最强 decoding baseline；DeFT 基于 paged memory，可作 SGLang attention kernel 的 drop-in 升级。

## 调度/disagg 谱系（第一轮深读补充）
- **[[taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve]]** = [[sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills]] 的 serving 化演进：chunked-prefills + piggybacking 机制源自 SARATHI，Sarathi-Serve 做成 production-grade online server，新增 stall-free scheduling + token budget 调参 + PP 优化。同一团队（MSR India + Georgia Tech）。
- **两种 prefill-decode 干扰解法对比**：Sarathi-Serve 走 **collocated hybrid batch**（同 replica 内 chunk 混合，不需 KV 迁移但 prefill 不能完全高效）；[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]] 走 **disagg**（物理分离 + KV 跨节点池化，prefill 高效但需 KV 迁移）。论文 §6 把 disagg 列第三类并讨论 tradeoff。
- 与 [[sglang-efficient-execution-of-structured-language-model-programs]] 正交：SGLang 多调用间 KV 前缀复用，Sarathi-Serve 单 replica 内 prefill-decode 混合调度——可叠加。

## 第一轮深读锚点（2026-08-18，DEEP 笔记已落 extraction/deep/）
`[[sglang-efficient-execution-of-structured-language-model-programs]]` · `[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]` · `[[kimi-linear-an-expressive-efficient-attention-architecture]]` · `[[taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve]]` · `[[hyper-connections]]` · `[[deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference]]` · `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]` —— 每篇含核心问题/创新点/表格/对比/局限全要素深读，后续夜间任务按 [[extract-phase1-overwrite-gotcha]] 持续补充。

