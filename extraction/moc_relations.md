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
- **GEPA**（#16/#19）：反思式 prompt 进化，可超越 RL——与 RL 路线互补对比。
