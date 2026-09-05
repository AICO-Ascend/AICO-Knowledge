# 📇 知识库内容索引（LLM-reads-first）

> LLM Wiki 簿记层的内容目录：回答查询时**先读本页定位，再钻取**。
> 由 `wiki_index.py` 在 full_pipeline 里自动重建（幂等），勿手改。
> 编年动态见 [[log]]；主题图谱见 [[MOC]]；跨论文谱系见 [[moc_relations]]。

## 使用约定

- 查论文 → 下方「论文」节按主题分组，每行：标题（链接）+ 一句定位 + 要素计数
- 查概念/谱系 → `wiki/concepts/` 原子概念页（跨论文综合，图谱 hub）
- 查图/表/公式 → [[INTERPRETATION_MAP]]（三层产物与 key 规则）
- 机器查询 → `kb_query.py search|fig|formula|topics|info|stats`（--json）

## 论文（69 篇，按主题）


### architecture（3）

- [[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm|Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM]] — 2026/1/4 ｜ fig18 tab2 +深读
- [[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training|From ATOP to ZCube: Automated Topology Optimization Pipeline and A Highly Cost-E]] — 2025/8/27 ｜ fig24 tab6 +深读
- [[gated-delta-networks-improving-mamba2-with-delta-rule|Gated Delta Networks: Improving Mamba2 with Delta Rule]] — 2024/12/9 ｜ fig3 tab5 +深读

### disaggregated-serving（5）

- [[efficiently-serving-large-multimodal-models-using-epd-disaggregation|Efficiently Serving Large Multimodal Models Using EPD Disaggregation]] — 2026/1/4 ｜ fig12 tab9 +深读
- [[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving|Mooncake: A KVCache-centric Disaggregated Architecture for LLM Serving]] — 2026/1/4 ｜ fig11 tab3 +深读
- [[sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills|SARATHI: Efficient LLM Inference by Piggybacking Decodes with Chunked Prefills]] — 2023/8/31 ｜ fig13 tab4 +深读
- [[sglang-efficient-execution-of-structured-language-model-programs|SGLang: Efficient Execution of Structured Language Model Programs]] — 2026/1/4 ｜ fig13 tab1 +深读
- [[taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve|Taming Throughput-Latency Tradeoff in LLM Inference with Sarathi-Serve]] — 2024/3/4 ｜ fig14 tab4 +深读

### kv-cache（5）

- [[a-survey-on-large-language-model-acceleration-based-on-kv-cache-management|A Survey on Large Language Model Acceleration based on KV Cache Management]] — 2026/1/4 ｜ fig5 tab12 +深读
- [[cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion|CacheBlend: Fast Large Language Model Serving for RAG with Cached Knowledge Fusi]] — 2024/5/26 ｜ fig16 tab0 +深读
- [[indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse|IndexCache: Accelerating Sparse Attention via Cross-Layer Index Reuse]] — 2026/3/12 ｜ fig3 tab5 +深读
- [[kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference|KV Cache Optimization Strategies for Scalable and Efficient LLM Inference]] — 2026/3/20 ｜ fig14 tab6 +深读
- [[prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter|Prefill-as-a-Service: KVCache of Next-Generation Models Could Go Cross-Datacente]] — 2026/4/16 ｜ fig5 tab4 +深读

### long-context（2）

- [[deepseek-v4-towards-highly-efficient-million-token-context-intelligence|DeepSeek-V4: Towards Highly Efficient Million-Token Context Intelligence]] — 2026/4/28 ｜ fig1 tab0 +深读
- [[longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification|LongSpec: Long-Context Lossless Speculative Decoding with Efficient Drafting and]] — 2025/2/24 ｜ fig6 tab5 +深读

### moe（1）

- [[scalable-training-of-mixture-of-experts-models-with-megatron-core|Scalable Training of Mixture-of-Experts Models with Megatron Core]] — 2026/3/8 ｜ fig42 tab19 +深读

### multimodal（5）

- [[deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms|DeepStack: Deeply Stacking Visual Tokens is Surprisingly Simple and Effective fo]] — 2026/6/10 ｜ fig5 tab0 +深读
- [[kimi-k2-5-visual-agentic-intelligence|KIMI K2.5: VISUAL AGENTIC INTELLIGENCE]] — 2026/2/1 ｜ fig7 tab6 +深读
- [[kimi-vl-technical-report|KIMI-VL TECHNICAL REPORT]] — 2025/4/10 ｜ fig13 tab5 +深读
- [[qwen2-5-vl-technical-report|Qwen2.5-VL Technical Report]] — 2026/1/5 ｜ fig1 tab9 +深读
- [[qwen3-vl-technical-report|Qwen3-VL Technical Report]] — 2026/6/10 ｜ fig3 tab11 +深读

### other（27）

- [[a-survey-of-large-language-models|A Survey of Large Language Models]] — 2023/3/31 ｜ fig19 tab21 +深读
- [[ascend-950-npu-architecture-whitepaper|昇腾 950 NPU 架构白皮书]] — 2026/1/1 ｜ fig22 tab4 +深读
- [[attention-residuals|Attention Residuals]] — 2026/3/16 ｜ fig8 tab5 +深读
- [[bertopic-neural-topic-modeling-with-a-class-based-tf-idf-procedure|BERTopic: Neural topic modeling with a class-based TF-IDF procedure]] — 2026/1/19 ｜ fig1 tab3 +深读
- [[beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl|Beyond Ten Turns: Unlocking Long-Horizon Agentic Search with Large-Scale Asynchr]] — 2026/1/17 ｜ fig11 tab5 +深读
- [[conditional-memory-via-scalable-lookup-a-new-axis-of-sparsity-for-large-language-models|Conditional Memory via Scalable Lookup: A New Axis of Sparsity for Large Languag]] — 2026/1/17 ｜ fig8 tab6 +深读
- [[cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation|CUDA Agent: Large-Scale Agentic RL for High-Performance CUDA Kernel Generation]] — 2026/2/27 ｜ fig14 tab3 +深读
- [[deepseek-v3-technical-report|DeepSeek-V3 Technical Report]] — 2026/1/4 ｜ fig10 tab9 +深读
- [[deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models|DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Mode]] — 2026/1/19 ｜ fig7 tab10 +深读
- [[deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference|DeFT: Decoding with Flash Tree-attention for Efficient Tree-structured LLM Infer]] — 2024/4/1 ｜ fig16 tab21 +深读
- [[dual-head-reasoning-distillation-improving-classifier-accuracy-with-train-time-only-reasoning|Dual-Head Reasoning Distillation: Improving Classifier Accuracy with Train-Time-]] — 2026/1/19 ｜ fig2 tab6 +深读
- [[dynamic-large-concept-models-latent-reasoning-in-an-adaptive-semantic-space|Dynamic Large Concept Models: Latent Reasoning in an Adaptive Semantic Space]] — 2026/1/19 ｜ fig6 tab6 +深读
- [[efficient-memory-management-for-large-language-model-serving-with-pagedattention|Efficient Memory Management for Large Language Model Serving with PagedAttention]] — 2023/9/13 ｜ fig18 tab1 +深读
- [[hc-manifold-constrained-hyper-connections|HC: Manifold-Constrained Hyper-Connections]] — 2026/1/5 ｜ fig8 tab5 +深读
- [[high-dimensional-continuous-control-using-generalized-advantage-estimation|High-Dimensional Continuous Control Using Generalized Advantage Estimation]] — 2026/1/19 ｜ fig4 tab0 +深读
- [[huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod|Huawei Cloud Model-as-a-Service on the CloudMatrix384 SuperPod]] — 2025/8/4 ｜ fig20 tab0 +深读
- [[hyper-connections|HYPER-CONNECTIONS]] — 2026/1/19 ｜ fig18 tab15 +深读
- [[kimi-k2-open-agentic-intelligence|KIMI K2: OPEN AGENTIC INTELLIGENCE]] — 2026/1/19 ｜ fig9 tab6 +深读
- [[kimi-k3-open-frontier-intelligence|Kimi K3: Open Frontier Intelligence]] — 2026/7/27 ｜ fig16 tab5 +深读
- [[kimi-linear-an-expressive-efficient-attention-architecture|Kimi Linear: An Expressive, Efficient Attention Architecture]] — 2025/10/30 ｜ fig7 tab9 +深读
- [[let-it-flow-agentic-crafting-on-rock-and-roll|Let It Flow: Agentic Crafting on Rock and Roll]] — 2026/1/17 ｜ fig18 tab7 +深读
- [[linear-optimal-topic-transport-for-document-similarity|Linear Optimal Topic Transport for Document Similarity]] — 2026/1/17 ｜ fig2 tab2 +深读
- [[nanoflow-towards-optimal-large-language-model-serving-throughput|NanoFlow: Towards Optimal Large Language Model Serving Throughput]] — 2024/8/23 ｜ fig11 tab4 +深读
- [[parallel-scan-on-ascend-ai-accelerators|Parallel Scan on Ascend AI Accelerators]] — 2025/5/20 ｜ fig4 tab0 +深读
- [[rllm-relational-table-learning-with-llms|rLLM: Relational Table Learning with LLMs]] — 2024/7/29 ｜ fig4 tab2 +深读
- [[root-mean-square-layer-normalization|Root Mean Square Layer Normalization]] — 2026/1/7 ｜ fig7 tab4 +深读
- [[step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding|Step-3 is Large yet Affordable: Model-system Co-design for Cost-effective Decodi]] — 2026/1/4 ｜ fig9 tab8 +深读

### rl（6）

- [[areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning|AREAL: A Large-Scale Asynchronous Reinforcement Learning System for Language Rea]] — 2026/1/17 ｜ fig6 tab7 +深读
- [[deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning|DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learni]] — 2026/1/17 ｜ fig2 tab29 +深读
- [[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning|GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM REINFORCEMENT LEARNING]] — 2026/1/1 ｜ fig5 tab3 +深读
- [[hybridflow-a-flexible-and-efficient-rlhf-framework|HybridFlow: A Flexible and Efficient RLHF Framework]] — 2026/1/17 ｜ fig14 tab1 +深读
- [[search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning|Search-R1: Training LLMs to Reason and Leverage Search Engines with Reinforcemen]] — — ｜ fig7 tab9 +深读
- [[single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning|Single-Rollout Asynchronous Optimization for Agentic Reinforcement Learning]] — 2026/7/8 ｜ fig6 tab5 +深读

### speculative（9）

- [[block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models|BLOCK DIFFUSION: INTERPOLATING BETWEEN AUTOREGRESSIVE AND DIFFUSION LANGUAGE MOD]] — 2025/3/12 ｜ fig5 tab8 +深读
- [[dflash-block-diffusion-for-flash-speculative-decoding|DFlash: Block Diffusion for Flash Speculative Decoding]] — 2026/2/4 ｜ fig5 tab12 +深读
- [[dspark-confidence-scheduled-speculative-decoding-with-semi-autoregressive-generation|DSpark: Confidence-Scheduled Speculative Decoding with Semi-Autoregressive Gener]] — 2024/1/1 ｜ fig8 tab1 +深读
- [[eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees|EAGLE-2: Faster Inference of Language Models with Dynamic Draft Trees]] — 2024/6/24 ｜ fig7 tab3 +深读
- [[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test|EAGLE-3: Scaling up Inference Acceleration of Large Language Models via Training]] — 2025/3/3 ｜ fig7 tab5 +深读
- [[eagle-speculative-sampling-requires-rethinking-feature-uncertainty|EAGLE: Speculative Sampling Requires Rethinking Feature Uncertainty]] — 2026/6/29 ｜ fig9 tab8 +深读
- [[jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting|JETSPEC: Breaking the Scaling Ceiling of Speculative Decoding with Parallel Tree]] — 2026/6/16 ｜ fig6 tab12 +深读
- [[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads|MEDUSA: Simple LLM Inference Acceleration Framework with Multiple Decoding Heads]] — 2024/1/19 ｜ fig22 tab8 +深读
- [[specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences|SpecExtend: A Drop-in Enhancement for Speculative Decoding of Long Sequences]] — 2025/5/27 ｜ fig6 tab8 +深读

### training（6）

- [[efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey|Efficient Training of Large Language Models on Distributed Infrastructures: A Su]] — 2026/1/4 ｜ fig15 tab0 +深读
- [[gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints|GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpo]] — 2026/1/7 ｜ fig6 tab1 +深读
- [[megascale-scaling-large-language-model-training-to-more-than-10000-gpus|MegaScale: Scaling Large Language Model Training to More Than 10,000 GPUs]] — 2026/1/4 ｜ fig12 tab3 +深读
- [[megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism|Megatron-LM: Training Multi-Billion Parameter Language Models Using Model Parall]] — 2026/1/4 ｜ fig8 tab7 +深读
- [[muon-is-scalable-for-llm-training|Muon is Scalable for LLM Training]] — 2025/2/24 ｜ fig10 tab10 +深读
- [[zero-memory-optimizations-toward-training-trillion-parameter-models|ZeRO: Memory Optimizations Toward Training Trillion Parameter Models]] — 2026/1/4 ｜ fig8 tab6 +深读

## 概念页（wiki/concepts/，19 页）

跨论文原子概念页：一个概念一页，累积综合 + 谱系嵌入 + 成员链接。
新论文 ingest 时按主题归属更新对应概念页。

- [[concepts/architecture|architecture]]
- [[concepts/disaggregated-serving|disaggregated-serving]]
- [[concepts/frontier-models|frontier-models]]
- [[concepts/kv-cache|kv-cache]]
- [[concepts/linear-attention|linear-attention]]
- [[concepts/llm-taxonomy|llm-taxonomy]]
- [[concepts/long-context|long-context]]
- [[concepts/moe|moe]]
- [[concepts/multimodal|multimodal]]
- [[concepts/normalization|normalization]]
- [[concepts/npu-ascend|npu-ascend]]
- [[concepts/reasoning-distillation|reasoning-distillation]]
- [[concepts/residual-topology|residual-topology]]
- [[concepts/rl|rl]]
- [[concepts/sparsity-axes|sparsity-axes]]
- [[concepts/speculative-decoding|speculative-decoding]]
- [[concepts/table-learning|table-learning]]
- [[concepts/topic-modeling|topic-modeling]]
- [[concepts/training|training]]

## 索引与清单文件

| 文件 | 内容 |
|---|---|
| [[MOC]] | 主题聚类图谱导航 |
| [[moc_relations]] | 跨论文演进谱系（机制级，人工/夜读维护） |
| [[figures_index]] | 全部图表主索引（⭐精选） |
| [[INTERPRETATION_MAP]] | 图/表/公式三层产物与 M3 解读 key 规则 |
| [[log]] | 编年日志（ingest/lint/crop-fix 动态） |
| papers.json | 论文 manifest（RAG 摄取入口；发表时间以 pub_month 字段为权威） |
| visuals.json | 裁剪图 manifest（fig 682 + tab 429 + eq） |
| minimax_captions.json | M3 图文联合解读（裁剪图 100%） |
| formulas.json | LaTeX 公式权威库 |

## 代码仓域与网页域（本索引由论文流水线重建 —— 三域全貌入口在此）

| 入口 | 内容 |
|---|---|
| repo_inventory.json | 134 仓清单 + 版本血缘 snapshots（重拉留历史快照） |
| repo_docs_index.json | 21,954 篇仓文档收割索引（九类分类/大纲/图片/互链） |
| repo_deep_index.json | 1,722 篇仓文档七节深读索引（85 仓） |
| repo_m3_captions.json | 881 张仓内图图文联合解读 |
| repo_cards/ + deep/repo-* | 仓卡片（机械骨架 / 分析层） |
| web_index.json | 网页注册表（抓取路由/版本线/深读登记） |
| web_deep_docs/ | 网页七节深读（表格逐字还原） |
| web_moc.md | 网页域知识地图（版本对照结论） |
| ../AGENTS.md | 面向 AI 系统的机器消费契约（铁律/注册表/RAG 建议） |
| ../bookshelf/SHELF.md | 面向人类学习者的知识书架（技术栈六层主线） |
