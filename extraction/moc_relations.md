# 跨论文关系与演进（人工维护）

> 独立文件，extract_phase1 重跑不丢。MOC.md 通过 `![[moc_relations]]` 嵌入此页。
> 由夜间深读（DEEP_LEARNING_PROTOCOL）逐篇补充、串联。绝不猜来源，仅基于已读论文确证的关系。

## KV cache 复用谱系
- **vLLM / PagedAttention**（[[efficient-memory-management-for-large-language-model-serving-with-pagedattention]]，#52）：**谱系根**——首次把 OS 虚拟内存 + 分页引入 LLM serving：KV block(page) + block table(page table) + COW(fork) + 抢占式 swap/recompute。KV 有效利用率 20.4%(Orca Max) → 96.3%，吞吐 2–4× over SOTA。后续所有 paging/eviction/hierarchy 工作的 block 抽象来源。
- **SGLang RadixAttention**（#43）：把"简单系统提示共享"升级为"radix tree + 叶子优先 LRU + cache-aware 调度"多级树结构自动复用，覆盖 few-shot/self-consistency/multi-turn/ToT 四级共享模式。在 vLLM *显式* 前缀共享之上做 *自动* 前缀树复用。
- **Mooncake**（[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]，#45）：**跨节点 disagg 锚点**。vLLM block 从"单机内存管理单位"推广为"跨节点调度/迁移/复制/swap 的全局单位"，KV 在 GPU/CPU/DRAM/SSD 分层迁移；KVCache-centric，prefill(compute-bound)/decode(memory-bound) 物理分离 + 全局池。reuse 逻辑与 vLLM 类似但 vLLM 仅本地（§6.1）。生产 trace：ArXiv +20%、L-Eval +40%、Simulated +50%~+525%、Real +75% 请求且 TBT 满足率 ~100% vs vLLM 57%；调度 TTFT 6.26s vs random 92.07s。
- **IndexCache**（[[indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse]]，#1）：**跨层 sparse-index 复用锚点**——复用的是 sparse attention 的 *index 张量*（哪些 token 被 attend），不是 KV 张量；与 SGLang 前缀复用、Mooncake 跨节点 KV 池三条正交路径。1.82× prefill / 1.48× decode @ 200K，cross-layer overlap 0.7–1.0。正交于 [[kimi-linear-an-expressive-efficient-attention-architecture]]（架构级降二次 vs 算子级去冗余，可叠加）。DeepSeek-V3.2/GLM-5 默认 DSA-style sparse attention，作者预期 cross-layer index reuse 成前沿 LLM 推理标配。
- **Prefill-as-a-Service**（#58）：Mooncake 跨节点思想的进一步跨数据中心规模化。
- **Huawei CloudMatrix384**（[[huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod]]）：KV cache 跨 NPU P2P 迁移 + KV INT8 量化（non-RoPE 部分稳定）—— paging 思想在 Ascend SuperPod UB fabric 上的工业实例，对照 GPU/RoCE 系 vLLM/Mooncake。

## 调度谱系
- **SARATHI**（[[sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills]]，#17）：**chunked-prefill 根**——prefill 切 ≤C chunk + piggyback decodes（decode-maximal batching）消 prefill bubble、提 GPU 利用率。decode per-token 12.49→1.2ms（~10×），GPT-3/64×A100 bubble 降 6.29×、端到端 1.91×。原实现用预分配 KV，§7.1 把 vLLM 列为互补（vLLM paged memory 天然吸收 chunk 边界，二者正交可叠加）。
- **Sarathi-Serve**（[[taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve]]，#18）：SARATHI 的 serving 化演进（同团队 MSR India + Georgia Tech），production-grade online server，新增 stall-free scheduling + token budget τ + PP 量化。
- **SGLang**（#43）：多调用间前缀复用调度，与 Sarathi 单 replica 内 prefill-decode 混合调度正交可叠加。

## 推测解码谱系
- **Medusa**（[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]，#2）→ **EAGLE**（[[eagle-speculative-sampling-requires-rethinking-feature-uncertainty]]，#4）→ **EAGLE-2**（[[eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees]]，#5）→ **EAGLE-3**（#3）：多头/特征不确定性 → 动态 draft 树 → 训练时测试扩展。
  - EAGLE 是 **feature-prediction 分支 anchor**：复用 target LLM 末层特征、单头 1-layer draft（7B→0.24B 可训练参）+ **shifted-token（超前一拍 token）**消解特征自回归采样二义（Vicuna-7B speedup 1.9×→2.8×）+ Multi-round speculative sampling（§A.2 Alg.1）保 tree draft 下分布无损。上游 Medusa 多头独立预测，EAGLE 改单头特征级自回归链 + shifted-token 补无损 non-greedy 保证，取代 Medusa 成新 anchor。论文自承树结构 "not rigorously optimized"（§A.1）→ EAGLE-2 埋点。
  - EAGLE-2 = **context-aware 动态树**：把 EAGLE-1 静态直觉树换成 confidence-driven 动态树（draft 置信度 = 接受率代理，路径连乘打分 → top-k 扩展 → top-m reranking 保连通树不变式 → ancestor-only attention mask）。无需额外训练，复用 EAGLE-1 draft 模型。3.39×–4.10× @ T=0 vs EAGLE 2.78×–3.09×；τ≈4.6–4.7 vs EAGLE ≈3.7–3.9。confidence<0.05→accept≈0.04、>0.95→≈0.98 是经验基础。
  - MoE 局限：Mixtral 8x7B 仅 1.50×（expert 调度削弱算力复用红利），EAGLE 在 dense decoder-only 上最优。
- **Block Diffusion**（#6）→ **DFlash**（#7）/ **DSpark**（#8）：块级半自回归扩散解码分支。
- **JetSpec**（#9）：并行树 drafting 破 scaling 上限——与 EAGLE-2 单树动态 shaping 正交可组合（并行动态树）。
- **LongSpec**（#59）/ **SpecExtend**（#60）：长上下文场景的 draft 与上下文增强。
- **Block Diffusion**（#6）→ **DFlash**（#7）/ **DSpark**（#8）：块级半自回归扩散解码分支。
- **JetSpec**（#9）：并行树 drafting 破 scaling 上限。
- **LongSpec**（#59）/ **SpecExtend**（#60）：长上下文场景的 draft 与上下文增强。
- **Huawei CloudMatrix384 MTP**（[[huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod]]）：vLLM/EAGLE MTP 默认调度有 stall，FlowServe 用 5 步 pipeline 消 CPU bubble；训练专用第二 MTP（28 万样本）使 tokens/step 2.26→2.35。MTP 是 speculative 在工业 serving 的部署形态。

## 训练系统谱系
- **Megatron-LM**（[[megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism]]，#49）：**模型并行根**——intra-layer tensor parallelism（column-parallel linear → row-parallel linear，fused pair 一次 all-reduce；f/g 共轭 autograd 算子）+ 与 pipeline parallelism 正交声明。无 compiler，原生 PyTorch。沿 MP 轴切分（vs ZeRO 沿 DP 轴切分，可组合）。峰值 15.1 PetaFLOPs @ 8.3B/512 GPU。
- **Megatron-LM 分布式**（#48）→ **MegaScale**（[[megascale-scaling-large-language-model-training-to-more-than-10000-gpus]]，#46）：**10k-GPU 生产 apex**——继承 Megatron TP/PP/DP+SP + interleaved 1F1B，推到 12,288 GPU / 55.2% MFU（1.34× over Megatron，2166 PFlops/s）。算法-系统协同（PTB/SWA/TP·PP·DP overlap）+ 容错（>90% 自动、<15min 恢复）+ 深可观测。DP overlap 直接基于 ZeRO2 all-reduce→reduce-scatter+all-gather 拆分。
- **ZeRO**（[[zero-memory-optimizations-toward-training-trillion-parameter-models]]，#47）：沿 DP 轴切分 optimizer state/grads/params，与 Megatron 沿 MP 轴切分**正交可组合**（Megatron-DeepSpeed 叠加）。MegaScale DP overlap 即基于 ZeRO2。
- **Megatron Core MoE**（#12）：在 Megatron MP/DP 拓扑之上的 expert-parallel 扩展。
- **Muon**（[[muon-is-scalable-for-llm-training]]）：优化器轴——对标 AdamW（element-wise adaptive momentum），Muon 对 2D 权重矩阵经 Newton-Schulz 正交化 momentum。Scaling law ~2× compute efficiency（52% FLOPs 匹配 AdamW compute-optimal）；Distributed Muon 构建在 Megatron TP/PP/EP/DP 之上，ZeRO-1 gather 范围从 global 收窄到 DP group；仅 1 个 momentum buffer，额外内存为 ZeRO-1 AdamW 的一半。Appendix D：RMSNorm gamma 必须加 weight decay。MoE 侧线：Router 权重从 Muon 获益最大（SVD entropy 分析）。Muon 的 gather/compute overlap 与 MegaScale 的 TP/SP overlap 共享"通信-计算重叠"内核。

## 归一化原语谱系
- **RMSNorm**（[[root-mean-square-layer-normalization]]）：**归一化家族根**（BatchNorm→LayerNorm→RMSNorm）——把归一化从 re-centering+re-scaling 缩减到 re-scaling 一项（去均值，仅 RMS+gain γ），7-64% faster、质量相当。现代 LLM 栈（LLaMA/DeepSeek/Qwen）默认归一化原语，"re-centering 非必要"工程共识的起点。
- **与 [[hyper-connections]] 正交可叠加**：残差拓扑承运层间流、RMSNorm 承运层内激活稳定；§7 明示与低精度、kernel fusion 正交。
- **与 [[muon-is-scalable-for-llm-training]] 稳定性耦合**：Muon Appendix D 指出 RMSNorm gain γ **必须施加 weight decay**，否则输出 RMS spike——补上 RMSNorm §4.2 留下的"γ 长期发散控制"缺口。

## KV-cache 架构性压缩谱系
- **GQA**（[[gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints]]）：**KV 架构压缩根**——MHA↔MQA 可调插值（GQA-1=MQA, GQA-H=MHA），分组共享 KV head；uptraining 配方把转换成本压到 ~5% 原预训练算力。GQA-8-XXL 0.28s（MHA-XXL ~18.5%）达 47.1（逼近 47.2），几乎与 MQA 同速且质量更高。
- → **MLA**（[[kimi-linear-an-expressive-efficient-attention-architecture]]）：GQA 思路的更深压缩继任——GQA=分组共享原始 KV，MLA=将 KV 投影到压缩潜空间。谱系：MQA → GQA（分组）→ MLA（低秩）。
- 与 [[efficient-memory-management-for-large-language-model-serving-with-pagedattention]] 正交叠加：GQA 在结构上缩小被分页的 KV 总量，PagedAttention 治理其碎片化分配；二者共构现代 serving 栈支柱。是 [[a-survey-on-large-language-model-acceleration-based-on-kv-cache-management]] 中 architectural KV-reduction 入口。

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
`[[sglang-efficient-execution-of-structured-language-model-programs]]` · `[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]` · `[[kimi-linear-an-expressive-efficient-attention-architecture]]` · `[[taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve]]` · `[[hyper-connections]]` · `[[deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference]]` · `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]` · `[[efficient-memory-management-for-large-language-model-serving-with-pagedattention]]`（KV-cache 根）· `[[eagle-speculative-sampling-requires-rethinking-feature-uncertainty]]`（speculative feature-prediction anchor）· `[[muon-is-scalable-for-llm-training]]`（优化器轴）· `[[huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod]]`（Ascend SuperPod serving 工业实例）· `[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]`（跨节点 disagg 锚点）· `[[megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism]]`（模型并行根）· `[[indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse]]`（跨层 sparse-index 复用锚点）· `[[eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees]]`（context-aware 动态树）· `[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]`（跨节点 disagg 锚点）· `[[megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism]]`（模型并行根）· `[[indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse]]`（跨层 sparse-index 复用锚点）· `[[sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills]]`（chunked-prefill 根）· `[[gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints]]`（KV 架构压缩根）· `[[root-mean-square-layer-normalization]]`（归一化原语根）· `[[megascale-scaling-large-language-model-training-to-more-than-10000-gpus]]`（10k-GPU 训练 apex）—— 共 19 篇全要素深读，每篇含核心问题/创新点/表格/对比/局限；后续夜间任务按 [[extract-phase1-overwrite-gotcha]] 持续补充剩余论文。

