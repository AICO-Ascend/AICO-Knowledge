# CURATION.md — 知识书架策展定义（人工维护的唯一文件）

> `bookshelf_build.py` 读取本文件内嵌的 ```yaml 块生成 `SHELF.md` / `ascend_infra.md`。
> **只改这里，不改产物**；改完跑 `python3 skills/bookshelf/bookshelf_build.py`（死链 lint 不过关会非零退出）。
>
> 条目引用协议：`paper:<slug>` 论文深读 · `papermd:<slug>` 结构化解构 · `reponote:<slug>:<path>` 仓文档深读 ·
> `repocard:<slug>` 仓卡片（有分析层优先链 deep/）· `web:<slug>` 网页深读 · `concept:<slug>` 概念页 ·
> `crop:<file>` 裁剪图 · `ext:<label>:<url>` 外链。
> 条目可标注：`heat`/`difficulty`（1-3，🔥/⚡）· `note` 自由备注 · `ascend` 昇腾亲和注记 ·
> `assets: [{label, ref}]` 资产链接 · `category` 知识分类（缺省继承分区）。
> 发表时间由生成器从 arXiv ID 机械派生（papers.json 的 date 对 2026-01 批次混入了入库日期，不作展示）。

```yaml
layers:
  L1: Agent
  L2: 模型/算法
  L3: 训推框架
  L4: 算子
  L5: 系统软件
  L6: 硬件/集群

shelf_intro: |
  这不是链接收藏夹——每条目都挂着**自有深读资产**（点开即全文解读/裁剪图/LaTeX 公式/逐字还原表）。
  组织轴是一条技术栈主线：**一个 Agent 需求往下钻**——选什么模型（L2）→ 怎么训怎么推（L3）→
  落在哪些算子上（L4）→ 跑在什么系统软件栈上（L5）→ 钉在什么硬件与集群拓扑上（L6）。
  与 InfraTech 的差异：他们链知乎文章，我们链 69 篇论文 6 段深读 + 134 仓 1,719 篇文档七节深读 +
  官方手册网页深读；与 AscendV 官方可视化平台共生互链（见昇腾专区）。

layer_intros:
  L1: |
    Agent 层的核心问题是**长周期自主性与训练信号**：怎么让模型学会多轮工具调用与搜索（Agentic RL），
    以及训推两套系统怎么高效耦合（共卡/权重同步/异步 rollout）。
  L2: |
    模型与算法层回答"用什么结构"。每个条目尽量回答一个昇腾视角的问题：**这个算法落到昇腾需要哪些算子**——
    DSA 需要稀疏 gather/index 算子，KDA 需要 chunkwise 线性注意力算子（vllm-ascend ChunkKdaFwd 设计文档可证），
    MoE 需要 dispatch/combine 通信算子。
  L3: |
    训推框架是算法与硬件之间的系统层。GPU 侧看 Megatron/vLLM/SGLang 论文与源码文档；
    昇腾侧看 MindSpeed（训练）/ MindIE · vllm-ascend（推理）——本库 497 篇特性文档七节深读全部在册。
  L4: |
    算子是性能的最后一公里。GPU 侧 CUDA/Triton/CUTLASS；昇腾侧 AscendC/Triton-Ascend/CATLASS——
    交互式算子演示与精度/性能方法论见 [AscendInfra 专区](ascend_infra.md)的 AscendV 引用地图。
  L5: |
    系统软件层：驱动/运行时/编译器/通信库。昇腾侧 CANN + HCCL 的环境变量手册已逐字入库
    （商用 900 与社区 910beta1 两版内容一致——本库独家版本对照结论）。
  L6: |
    硬件与集群层：昇腾 950 架构白皮书与 CloudMatrix384 超节点论文是本库的独家深读资产；
    三代 AI Core 的交互式架构动画引用 AscendV。

# ═══════════ SHELF.md 分区（六层主线） ═══════════
sections:
  # ────── L1 Agent ──────
  - id: agentic-rl
    layer: L1
    title: Agentic RL 与训推耦合
    category: RL
    intro: |
      推荐路径：先 DeepSeek-R1 建立 GRPO 直觉 → HybridFlow 看训推框架设计 →
      AREAL 看异步 rollout 规模化 → CUDA-Agent 看 Agentic RL 的极致工程化。
    items:
      - ref: paper:deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning
        heat: 3
        difficulty: 2
        note: GRPO 实战原点；纯 RL 激发推理
      - ref: paper:deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models
        heat: 2
        difficulty: 3
        note: GRPO 算法出处
      - ref: paper:hybridflow-a-flexible-and-efficient-rlhf-framework
        heat: 2
        difficulty: 3
        note: 训推框架解耦设计
      - ref: paper:areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning
        heat: 2
        difficulty: 3
        note: 异步 rollout 规模化
        ascend: 异步训推架构对 MindSpeed-RL 直接有参考价值
      - ref: paper:search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning
        heat: 2
        difficulty: 2
        note: 工具调用 RL（检索）
      - ref: paper:cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-gen
        heat: 3
        difficulty: 3
        note: Agentic RL 生成 CUDA kernel——算子自动化的前沿
        ascend: 方法论可平移到 AscendC 算子生成
      - ref: paper:single-rollout-asynchronous-optimization-for-agentic-reinforcement-lea
        difficulty: 3
      - ref: paper:gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning
        difficulty: 2
        note: 非梯度替代路线（反思式 prompt 进化）
      - ref: paper:high-dimensional-continuous-control-using-generalized-advantage-estima
        difficulty: 2
        note: GAE 原始论文（RL 基础）
      - ref: reponote:mindspeed-rl:docs/zh/features/EPLB.md
        note: 昇腾侧 MoE 负载均衡（RL 场景）
        ascend: MindSpeed-RL 原生
  # ────── L1 Agent · 长周期 ──────
  - id: agentic-long-horizon
    layer: L1
    title: 长周期 Agent 系统
    category: Agent
    items:
      - ref: paper:let-it-flow-agentic-crafting-on-rock-and-roll
        difficulty: 3
        note: Agentic 工作流编排
      - ref: paper:beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scal
        difficulty: 3
        note: 长周期搜索 Agent（十轮以上）
      - ref: paper:kimi-k2-open-agentic-intelligence
        heat: 2
        difficulty: 2
        note: Agentic 模型能力设计

  # ────── L2 模型/算法 ──────
  - id: attn-arch
    layer: L2
    title: 注意力与架构创新
    category: 架构
    intro: |
      推荐路径：GQA（多查询注意力基线）→ RMSNorm/Hyper-Connections（构件级创新）→
      Gated DeltaNet / Kimi Linear（线性注意力）→ 条件记忆（稀疏化新轴）。
    items:
      - ref: paper:deepseek-v3-technical-report
        heat: 3
        difficulty: 3
        note: MLA+MoE+FP8+DualPipe 集大成；本库深读含 MLA 裁剪子图
        ascend: 昇腾适配标杆模型（MindSpeed/vllm-ascend 均支持）
        assets:
          - {label: MLA 架构裁剪图, ref: crop:deepseek-v3-technical-report-fig02-mla.png}
      - ref: paper:gqa-training-generalized-multi-query-transformer-models-from-multi-hea
        heat: 2
        difficulty: 2
        note: GQA 基线（KV cache 减半的起点）
      - ref: paper:root-mean-square-layer-normalization
        difficulty: 1
        note: RMSNorm 原始论文
      - ref: paper:hyper-connections
        difficulty: 3
        note: 残差连接拓扩展
      - ref: paper:hc-manifold-constrained-hyper-connections
        difficulty: 3
      - ref: paper:attention-residuals
        difficulty: 3
        note: 注意力残差新范式
      - ref: paper:gated-delta-networks-improving-mamba2-with-delta-rule
        heat: 2
        difficulty: 3
        note: GDN——KDA 的直接前身
        ascend: chunkwise 算子需求 → vllm-ascend ChunkKdaFwd
      - ref: paper:kimi-linear-an-expressive-efficient-attention-architecture
        heat: 3
        difficulty: 3
        note: KDA——线性注意力前沿；GLM 5.3-Flash 同源技术
        ascend: vllm-ascend ChunkKdaFwd 仓内设计文档互证
      - ref: paper:conditional-memory-via-scalable-lookup-a-new-axis-of-sparsity-for-larg
        difficulty: 3
        note: 条件记忆——稀疏化新轴
      - ref: paper:dynamic-large-concept-models-latent-reasoning-in-an-adaptive-semantic-
        difficulty: 3
      - ref: paper:kimi-k3-open-frontier-intelligence
        heat: 2
        difficulty: 3
        note: KDA+Gated MLA 组合架构
      - ref: concept:linear-attention
        note: 概念页：线性注意力跨论文综合
      - ref: concept:residual-topology
        note: 概念页：残差拓扑谱系
  - id: sparse-attn
    layer: L2
    title: 稀疏注意力与长上下文
    category: 稀疏注意力
    items:
      - ref: paper:indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse
        difficulty: 3
        note: 跨层索引复用加速稀疏注意力
        ascend: 稀疏 gather/index 算子需求
      - ref: paper:deepseek-v4-towards-highly-efficient-million-token-context-intelligenc
        heat: 2
        difficulty: 3
        note: 百万 token 上下文（DSA 演进）
      - ref: concept:long-context
  - id: moe-arch
    layer: L2
    title: MoE 架构
    category: MoE
    items:
      - ref: paper:scalable-training-of-mixture-of-experts-models-with-megatron-core
        heat: 2
        difficulty: 3
        note: Megatron-Core MoE 训练系统化
        ascend: MindSpeed MoE 特性族（fb-overlap/EPLB）的上游基线
      - ref: concept:moe
        note: 概念页：MoE 谱系
  - id: spec-decoding
    layer: L2
    title: 投机解码（10+ 篇成簇）
    category: 投机解码
    intro: |
      推荐路径：Medusa（多头草案直觉）→ EAGLE（特征层草案，必读）→ EAGLE-2（动态草案树）→
      EAGLE-3（训练时扩展）→ LongSpec/SpecExtend（长上下文扩展）→ DFlash/DSpark（块扩散新方向）→
      JetSpec（并行扩展天花板）。部署侧参数见 L3 的 vLLM serve CLI 手册。
    items:
      - ref: paper:medusa-simple-llm-inference-acceleration-framework-with-multiple-decod
        heat: 2
        difficulty: 2
        note: 入门：多头草案
      - ref: paper:eagle-speculative-sampling-requires-rethinking-feature-uncertainty
        heat: 3
        difficulty: 3
        note: 必读：特征层草案
        ascend: vllm-ascend 实验性支持 EAGLE3
      - ref: paper:eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees
        heat: 2
        difficulty: 3
      - ref: paper:eagle-3-scaling-up-inference-acceleration-of-large-language-models-via
        heat: 2
        difficulty: 3
      - ref: paper:longspec-long-context-lossless-speculative-decoding-with-efficient-dra
        difficulty: 3
        note: 长上下文无损化
      - ref: paper:specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequ
        difficulty: 2
      - ref: paper:dspark-confidence-scheduled-speculative-decoding-with-semi-autoregress
        difficulty: 3
      - ref: paper:dflash-block-diffusion-for-flash-speculative-decoding
        difficulty: 3
        note: 块扩散×投机解码
      - ref: paper:block-diffusion-interpolating-between-autoregressive-and-diffusion-lan
        difficulty: 3
        note: 块扩散语言模型基础
      - ref: paper:jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-para
        difficulty: 3
      - ref: paper:deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-
        difficulty: 3
        note: 树注意力解码
      - ref: concept:speculative-decoding
        note: 概念页：投机解码全谱系
  - id: multimodal-arch
    layer: L2
    title: 多模态架构
    category: 多模态
    items:
      - ref: paper:qwen2-5-vl-technical-report
        heat: 2
        difficulty: 2
      - ref: paper:qwen3-vl-technical-report
        heat: 2
        difficulty: 2
        note: DeepStack+交错 MRoPE
        ascend: MindSpeed-MM 多模态训练支持
      - ref: paper:kimi-vl-technical-report
        difficulty: 2
      - ref: paper:kimi-k2-5-visual-agentic-intelligence
        difficulty: 2
      - ref: paper:deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-eff
        difficulty: 2
      - ref: concept:multimodal
  - id: surveys-taxonomy
    layer: L2
    title: 综述与分类学
    category: 综述
    items:
      - ref: paper:a-survey-of-large-language-models
        difficulty: 1
        note: LLM 总综述（入门第一站）
      - ref: paper:a-survey-on-large-language-model-acceleration-based-on-kv-cache-manage
        difficulty: 2
      - ref: concept:llm-taxonomy
      - ref: concept:frontier-models
  - id: extended-reading
    layer: L2
    title: 扩展阅读（主题模型/表格学习/蒸馏）
    category: 扩展
    items:
      - ref: paper:bertopic-neural-topic-modeling-with-a-class-based-tf-idf-procedure
        difficulty: 1
      - ref: paper:linear-optimal-topic-transport-for-document-similarity
        difficulty: 2
      - ref: paper:rllm-relational-table-learning-with-llms
        difficulty: 2
      - ref: paper:dual-head-reasoning-distillation-improving-classifier-accuracy-with-tr
        difficulty: 2
      - ref: concept:topic-modeling
      - ref: concept:table-learning

  # ────── L3 训推框架 ──────
  - id: training-sys
    layer: L3
    title: 大规模训练系统
    category: 训练系统
    intro: |
      推荐路径：Megatron-LM（3D 并行原点）→ ZeRO（显存优化）→ MegaScale（万卡工程）→
      Muon（优化器新范式）。昇腾侧对照：MindSpeed 特性文档族（497 篇深读全量在册）。
    items:
      - ref: paper:megatron-lm-training-multi-billion-parameter-language-models-using-mod
        heat: 3
        difficulty: 3
        note: TP/PP 原点
      - ref: paper:efficient-large-scale-language-model-training-on-gpu-clusters-using-me
        heat: 2
        difficulty: 3
        note: 3D 并行组合 + 通信掩盖
      - ref: paper:zero-memory-optimizations-toward-training-trillion-parameter-models
        heat: 2
        difficulty: 3
        note: 显存切分原点
      - ref: paper:megascale-scaling-large-language-model-training-to-more-than-10000-gpu
        heat: 2
        difficulty: 3
        note: 万卡工程全集
      - ref: paper:efficient-training-of-large-language-models-on-distributed-infrastruct
        difficulty: 2
      - ref: paper:muon-is-scalable-for-llm-training
        heat: 2
        difficulty: 3
        note: Muon 优化器
      - ref: paper:from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-high
        difficulty: 3
        note: 并行拓扑自动搜索
      - ref: paper:step-3-is-large-yet-affordable-model-system-co-design-for-cost-effecti
        difficulty: 3
        note: 模型-系统协同设计
      - ref: repocard:mindspeed
        heat: 3
        difficulty: 2
        note: 昇腾训练加速库卡片（fb-overlap 3 图 M3 解读）
        ascend: 昇腾训练栈核心
      - ref: reponote:mindspeed:docs/zh/features/megatron_moe/megatron-moe-fb-overlap.md
        heat: 2
        difficulty: 3
        note: MoE 前反向通信掩盖（含 3 图图文联合解读）
        ascend: MindSpeed 原生特性
      - ref: reponote:mindspeed:docs/zh/features/Automatic_Parallelism.md
        difficulty: 2
        note: 自动并行
        ascend: MindSpeed 原生特性
      - ref: reponote:mindspeed-rl:docs/zh/features/context_parallel.md
        difficulty: 3
        note: 长序列并行
        ascend: MindSpeed-RL 原生
      - ref: concept:training
  - id: inference-sys
    layer: L3
    title: 推理系统与调度
    category: 推理系统
    intro: |
      推荐路径：PagedAttention（vLLM 原点，必读）→ Sarathi（chunked prefill）→ SGLang（结构化执行）→
      Mooncake（KV 中心 PD 分离）→ NanoFlow（设备内流水）。部署参数查 L3 底部的 vLLM CLI 手册深读。
    items:
      - ref: paper:efficient-memory-management-for-large-language-model-serving-with-page
        heat: 3
        difficulty: 3
        note: PagedAttention——vLLM 原点
      - ref: paper:sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-p
        heat: 2
        difficulty: 3
        note: chunked prefill 原点
      - ref: paper:taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve
        difficulty: 3
      - ref: paper:sglang-efficient-execution-of-structured-language-model-programs
        heat: 2
        difficulty: 3
        note: RadixAttention
      - ref: paper:mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving
        heat: 3
        difficulty: 3
        note: KV 中心 PD 分离生产系统
        ascend: vllm-ascend PD 分离教程以 Mooncake 为后端
      - ref: paper:nanoflow-towards-optimal-large-language-model-serving-throughput
        difficulty: 3
        note: 设备内纳米流水
      - ref: paper:cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowl
        difficulty: 3
        note: RAG KV 复用
      - ref: paper:prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-
        difficulty: 3
      - ref: paper:kv-cache-optimization-strategies-for-scalable-and-efficient-llm-infere
        difficulty: 2
      - ref: paper:efficiently-serving-large-multimodal-models-using-epd-disaggregation
        difficulty: 3
        note: 多模态 EPD 分离
      - ref: repocard:vllm
        heat: 3
        difficulty: 2
        note: vLLM 仓卡片（版本线 v0.28.1rc0）
      - ref: repocard:vllm-ascend
        heat: 3
        difficulty: 2
        note: 昇腾后端卡片（v0.25.1rc1 · ChunkKdaFwd 发现）
        ascend: 昇腾推理栈核心
      - ref: reponote:vllm-ascend:docs/source/tutorials/features/pd_disaggregation_mooncake_multi_node.md
        difficulty: 3
        note: 昇腾 PD 分离实战（Mooncake 多机）
        ascend: vllm-ascend 原生教程
      - ref: reponote:vllm-ascend:docs/source/tutorials/features/dynamic_chunked_pipeline_parallel.md
        difficulty: 3
        ascend: vllm-ascend 原生教程
      - ref: reponote:xllm:docs/src/content/docs/en/features/disagg_pd.md
        difficulty: 3
        note: xLLM PD 分离设计
      - ref: reponote:xllm:docs/src/content/docs/en/features/chunked_scheduler.md
        difficulty: 2
      - ref: repocard:xllm
        heat: 2
        difficulty: 2
        note: xLLM 卡片（v0.10.1 · GLM-5.3-Flash day-0 时间线）
      - ref: web:vllm-cli-serve
        heat: 2
        difficulty: 1
        note: vLLM serve 312 项参数手册（网页深读，逐字还原）
      - ref: web:vllm-ascend-quickstart
        difficulty: 1
        note: vllm-ascend 中文快速上手 + Atlas 硬件支持表
        ascend: 昇腾容器化部署入口
      - ref: concept:disaggregated-serving
      - ref: concept:kv-cache
  - id: mindie-stack
    layer: L3
    title: MindIE 推理栈（昇腾商用）
    category: MindIE
    items:
      - ref: repocard:mindie-llm
        heat: 2
        difficulty: 2
        ascend: 昇腾商用推理引擎
      - ref: reponote:mindie-llm:docs/zh/developer_guide/architecture_design/architecture_overview.md
        difficulty: 2
        note: MindIE 架构设计
        ascend: MindIE 原生文档
      - ref: reponote:mindie-llm:docs/zh/user_guide/feature/asynchronous_scheduling.md
        difficulty: 2
        ascend: MindIE 原生特性
      - ref: reponote:mindie-llm:docs/zh/user_guide/feature/attention_quantization.md
        difficulty: 3
        ascend: MindIE 原生特性
      - ref: repocard:mindie-turbo
        ascend: 昇腾推理加速
      - ref: repocard:mindie-motor
        ascend: 昇腾推理编排
      - ref: repocard:mindie-sd
        ascend: 昇腾多模态推理

  # ────── L4 算子 ──────
  - id: operators
    layer: L4
    title: 算子库与算子开发
    category: 算子
    intro: |
      算子层是昇腾亲和的最前沿：GPU 论文（FlashAttention 族）在此对照昇腾算子仓实现。
      交互式算子动画/AscendC API 可视化/精度性能 12 步方法论 → 见 AscendInfra 专区的 AscendV 引用地图。
    items:
      - ref: paper:parallel-scan-on-ascend-ai-accelerators
        heat: 2
        difficulty: 3
        note: 昇腾加速器上的并行 scan（线性注意力底层算子）
        ascend: 昇腾算子研究论文（本库独家深读）
      - ref: repocard:triton-ascend
        heat: 2
        difficulty: 2
        note: Triton 昇腾后端（已迁 triton-lang 主线）
        ascend: GPU 算子迁移昇腾的最低门槛
      - ref: reponote:triton-ascend:docs/zh/architecture_design_and_core_features.md
        difficulty: 2
        ascend: Triton-Ascend 原生文档
      - ref: reponote:triton-ascend:docs/zh/migration_guide/architecture_difference.md
        heat: 2
        difficulty: 2
        note: 昇腾与 GPU 的开发差异（迁移必读）
        ascend: 迁移指南
      - ref: repocard:catlass
        difficulty: 3
        note: CATLASS——CANN 版 CUTLASS（v1.1.0）
        ascend: 昇腾 Cube 算子模板库
      - ref: repocard:torch_npu_ops
        difficulty: 2
        ascend: torch_npu 算子库
      - ref: repocard:xllm_ops
        difficulty: 2
        ascend: xLLM 高性能算子库
      - ref: reponote:vllm-ascend:csrc/attention/chunk_kda_fwd/docs/design.md
        heat: 2
        difficulty: 3
        note: ChunkKdaFwd 算子设计（KDA 落地的直接证据）
        ascend: vllm-ascend 仓内设计文档
      - ref: reponote:vllm-ascend:csrc/attention/sparse_attention_score/docs/sparse_attention_score_design.md
        difficulty: 3
        note: 稀疏注意力打分算子设计
        ascend: vllm-ascend 仓内设计文档

  # ────── L5 系统软件 ──────
  - id: system-software
    layer: L5
    title: CANN / HCCL 与图编译
    category: 系统软件
    intro: |
      昇腾系统软件层的两份官方手册已逐字入库：**商用版 900 与社区版 910beta1 环境变量清单内容一致**
      （本库独家版本对照结论，知识可跨版复用）。
    items:
      - ref: web:ascend-cann-commercial-envvars
        heat: 3
        difficulty: 1
        note: CANN 商用 900 环境变量索引（132 表行逐字还原）
        ascend: CANN 官方手册
      - ref: web:ascend-cann-community-envvars
        heat: 2
        difficulty: 1
        note: 社区 910beta1 版（与商用版一致）
        ascend: CANN 官方手册
      - ref: web:ascend-pytorch-envvars
        heat: 2
        difficulty: 1
        note: PyTorch NPU 环境变量（22 变量：算子执行/编译/内存/HCCL）
        ascend: Ascend Extension for PyTorch 官方手册
      - ref: web:ascend-cann-hccl-guide
        heat: 2
        difficulty: 2
        note: HCCL 用户指南·基于 root 节点信息创建通信域（9 表逐字还原）
        ascend: HCCL 官方手册
      - ref: repocard:torchair
        difficulty: 2
        note: 图编译（Ascend IR）
        ascend: 昇腾图编译栈
      - ref: reponote:torchair:docs/zh/ascend_ir/features/advanced/cc_parallel.md
        difficulty: 3
        note: 计算与通信并行（图编译层）
        ascend: torchair 原生特性
      - ref: reponote:torchair:docs/zh/ascend_ir/features/advanced/deterministic.md
        difficulty: 2
        note: 算子级确定性计算
        ascend: torchair 原生特性
      - ref: repocard:hccl_transfer
        difficulty: 2
        note: HCCL KV cache 传输
        ascend: 昇腾集合通信

  # ────── L6 硬件/集群 ──────
  - id: hardware-cluster
    layer: L6
    title: 芯片架构与超节点
    category: 硬件
    intro: |
      本层的两篇论文深读是**本库独家资产**（公开渠道难找同规格解读）；
      三代 AI Core 的交互式架构动画引用 AscendV 平台（见 AscendInfra 专区）。
    items:
      - ref: paper:ascend-950-npu-architecture-whitepaper
        heat: 3
        difficulty: 3
        note: 昇腾 950 架构白皮书——SIMD/SIMT 双模式、自研 HBM
        ascend: 官方架构白皮书深读（独家）
      - ref: paper:huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod
        heat: 3
        difficulty: 3
        note: CloudMatrix384 超节点生产实践
        ascend: 华为云超节点论文深读（独家）
      - ref: web:vllm-ascend-quickstart
        difficulty: 1
        note: Atlas A2/A3/950DT/300I DUO 支持矩阵
        ascend: 硬件支持表（逐字还原）
      - ref: concept:npu-ascend
        note: 概念页：昇腾 NPU 跨论文综合

# ═══════════ 横向专题（跨层学习路径） ═══════════
topics:
  - id: topic-spec
    layer: L2
    title: 专题·投机解码全链路
    category: 专题
    intro: 从算法（L2）到部署参数（L3）到昇腾支持状态的一条龙。
    items:
      - ref: paper:eagle-speculative-sampling-requires-rethinking-feature-uncertainty
        note: 算法原点
      - ref: paper:eagle-3-scaling-up-inference-acceleration-of-large-language-models-via
        note: 训练时扩展
      - ref: web:vllm-cli-serve
        note: 部署参数（--speculative-* 族）
      - ref: repocard:vllm-ascend
        note: 昇腾侧支持状态
        ascend: EAGLE3 实验性支持
  - id: topic-kvcache
    layer: L3
    title: 专题·KV Cache 全景
    category: 专题
    intro: 显存管理算法（L2）→ 框架机制（L3）→ 昇腾内存环境变量（L5）。
    items:
      - ref: paper:efficient-memory-management-for-large-language-model-serving-with-page
        note: PagedAttention 原点
      - ref: paper:mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving
        note: KV 中心架构
      - ref: paper:cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowl
        note: RAG 复用
      - ref: web:ascend-pytorch-envvars
        note: 昇腾内存管理变量（PYTORCH_NPU_ALLOC_CONF 等）
        ascend: 官方手册
  - id: topic-comm-overlap
    layer: L3
    title: 专题·通信掩盖与并行
    category: 专题
    intro: 同一个思想的三个层次：论文算法（DualPipe）→ 框架特性（fb-overlap）→ 图编译（cc_parallel）。
    items:
      - ref: paper:deepseek-v3-technical-report
        note: DualPipe 双向流水（论文 §3.2）
      - ref: reponote:mindspeed:docs/zh/features/megatron_moe/megatron-moe-fb-overlap.md
        note: MoE 前反向掩盖（昇腾实现）
        ascend: MindSpeed 原生
      - ref: reponote:torchair:docs/zh/ascend_ir/features/advanced/cc_parallel.md
        note: 图编译层计算通信并行
        ascend: torchair 原生
  - id: topic-quant
    layer: L2
    title: 专题·量化
    category: 专题
    intro: 训练侧 FP8（论文）→ 推理侧 Attention 量化（MindIE）→ 压缩工具（msmodelslim）。
    items:
      - ref: paper:deepseek-v3-technical-report
        note: FP8 混合精度训练
      - ref: reponote:mindie-llm:docs/zh/user_guide/feature/attention_quantization.md
        ascend: MindIE 原生特性
      - ref: repocard:msmodelslim
        ascend: 昇腾模型压缩工具

# ═══════════ 模型卡片 ═══════════
model_cards:
  - name: DeepSeek V3
    keywords: MLA+MoE+FP8+DualPipe
    links:
      - {label: 论文深读, ref: paper:deepseek-v3-technical-report}
      - {label: MLA 裁剪图, ref: crop:deepseek-v3-technical-report-fig02-mla.png}
  - name: DeepSeek V4
    keywords: MLA+DSA · 百万上下文
    links:
      - {label: 论文深读, ref: paper:deepseek-v4-towards-highly-efficient-million-token-context-intelligenc}
  - name: DeepSeek R1
    keywords: GRPO+RL 推理
    links:
      - {label: 论文深读, ref: paper:deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning}
  - name: Kimi K2 / K2.5 / K3
    keywords: MLA+MoE → 视觉 Agentic → KDA+Gated MLA
    links:
      - {label: K2 深读, ref: paper:kimi-k2-open-agentic-intelligence}
      - {label: K2.5 深读, ref: paper:kimi-k2-5-visual-agentic-intelligence}
      - {label: K3 深读, ref: paper:kimi-k3-open-frontier-intelligence}
  - name: Kimi Linear
    keywords: KDA 线性注意力
    links:
      - {label: 论文深读, ref: paper:kimi-linear-an-expressive-efficient-attention-architecture}
      - {label: 昇腾算子佐证, ref: reponote:vllm-ascend:csrc/attention/chunk_kda_fwd/docs/design.md}
  - name: Qwen2.5-VL / Qwen3-VL
    keywords: Dense+ViT → DeepStack+交错 MRoPE
    links:
      - {label: 2.5-VL 深读, ref: paper:qwen2-5-vl-technical-report}
      - {label: 3-VL 深读, ref: paper:qwen3-vl-technical-report}
  - name: GLM 5.3-Flash
    keywords: KDA+DSA（昇腾 day-0 适配）
    links:
      - {label: xllm 仓卡片, ref: repocard:xllm}
```

## AscendInfra 专区策展定义

```yaml
ascend_infra:
  intro: |
    **AscendInfra** 是昇腾全栈知识专区：与主书架同一条技术栈主线，但自下而上（L6→L1）从开发者视角展开——
    先看清硬件，再理解系统软件，再掌握算子开发，最后打通训推框架与模型算法。
    与官方 AscendV 可视化平台**共生互链**：交互动画/案例库去 AscendV（引用地图见文末），
    论文机制深读/版本血缘/环境变量手册留在这里。
  sections:
    - id: ai-hardware
      layer: L6
      title: 芯片与超节点
      category: 硬件
      items:
        - ref: paper:ascend-950-npu-architecture-whitepaper
          heat: 3
          note: 昇腾 950 白皮书深读（独家资产）
        - ref: paper:huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod
          heat: 3
          note: CloudMatrix384 超节点（独家资产）
        - ref: reponote:agent-skills:community/Op/ascendc-operator-design/references/hardware-architecture.md
          heat: 2
          note: 910B/A2/A3 AI Core 抽象架构（L1 512KB/L0 64KB/UB 192KB/三流并行）
        - ref: web:vllm-ascend-quickstart
          note: Atlas A2/A3/950DT/300I DUO 支持矩阵
        - ref: concept:npu-ascend
    - id: ai-system-software
      layer: L5
      title: CANN / HCCL / 图编译
      category: 系统软件
      items:
        - ref: web:ascend-cann-commercial-envvars
          heat: 3
          note: 商用 900 环境变量索引（132 表行逐字还原）
        - ref: web:ascend-cann-community-envvars
          note: 社区 910beta1——与商用版内容一致（独家对照结论）
        - ref: web:ascend-pytorch-envvars
          note: PyTorch NPU 2600 环境变量（22 变量）
        - ref: web:ascend-cann-hccl-guide
          note: HCCL 通信域创建指南（root 节点方式）
        - ref: repocard:torchair
          note: 图编译栈
        - ref: repocard:hccl_transfer
    - id: ai-operators
      layer: L4
      title: 算子开发（AscendC / Triton-Ascend / CATLASS）
      category: 算子
      items:
        - ref: repocard:triton-ascend
          heat: 2
          note: GPU 迁移最低门槛
        - ref: reponote:triton-ascend:docs/zh/migration_guide/architecture_difference.md
          note: 昇腾与 GPU 开发差异（迁移必读）
        - ref: repocard:catlass
          note: Cube 算子模板库（v1.1.0）
        - ref: repocard:torch_npu_ops
        - ref: repocard:xllm_ops
        - ref: paper:parallel-scan-on-ascend-ai-accelerators
          note: 昇腾并行 scan 研究论文
        - ref: reponote:vllm-ascend:csrc/attention/chunk_kda_fwd/docs/design.md
          note: KDA 算子设计实证
    - id: ai-frameworks
      layer: L3
      title: 训推框架（MindSpeed / MindIE / vllm-ascend）
      category: 框架
      items:
        - ref: repocard:mindspeed
          heat: 3
          note: 训练加速库（26.1.0_core_r0.12.1 · 配套 Megatron-Core 0.12.1）
        - ref: reponote:mindspeed:docs/zh/features/megatron_moe/megatron-moe-fb-overlap.md
          note: fb-overlap 通信掩盖（3 图 M3 解读）
        - ref: repocard:mindspeed-rl
        - ref: repocard:mindspeed-mm
        - ref: repocard:megatronadaptor
          note: Megatron-Core 适配层
        - ref: repocard:vllm-ascend
          heat: 3
          note: 开源推理后端（v0.25.1rc1）
        - ref: reponote:vllm-ascend:docs/source/tutorials/features/pd_disaggregation_mooncake_multi_node.md
          note: PD 分离实战
        - ref: repocard:mindie-llm
          heat: 2
          note: 商用推理引擎
        - ref: reponote:mindie-llm:docs/zh/developer_guide/architecture_design/architecture_overview.md
        - ref: web:vllm-ascend-quickstart
          note: 容器化快速上手
    - id: ai-models
      layer: L2
      title: 模型算法的昇腾落地
      category: 模型
      items:
        - ref: paper:kimi-linear-an-expressive-efficient-attention-architecture
          note: KDA → ChunkKdaFwd 算子（论文↔仓互证）
        - ref: paper:deepseek-v3-technical-report
          note: MLA+MoE 的昇腾适配标杆
        - ref: paper:gated-delta-networks-improving-mamba2-with-delta-rule
          note: GDN——chunkwise 算子需求源头
        - ref: reponote:mindie-llm:docs/zh/user_guide/feature/attention_quantization.md
          note: Attention 量化落地
    - id: ai-agent
      layer: L1
      title: 昇腾 Agentic / RL
      category: Agent
      items:
        - ref: repocard:mindspeed-rl
          note: 昇腾 RL 训练栈
        - ref: reponote:mindspeed-rl:docs/zh/features/EPLB.md
          note: EPLB 负载均衡
        - ref: paper:cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-gen
          note: Agentic 算子生成（GPU 前沿 → 昇腾方法论借鉴）
  cross_table:
    - concept: double buffer（搬运/计算并行）
      external: AscendV 知识可视化（概念动画）
      ours: reponote:mindspeed:docs/zh/features/megatron_moe/megatron-moe-fb-overlap.md
      impl: repocard:mindspeed
    - concept: 通信掩盖流水
      external: AscendV 算子运行图（MTE/Cube 流水动画）
      ours: paper:deepseek-v3-technical-report
      impl: repocard:mindspeed
    - concept: 线性注意力算子（KDA/GDN）
      external: AscendV Attention 算子全景图
      ours: paper:kimi-linear-an-expressive-efficient-attention-architecture
      impl: reponote:vllm-ascend:csrc/attention/chunk_kda_fwd/docs/design.md
    - concept: tiling 切分
      external: AscendV 知识可视化（tiling 概念）
      ours: web:ascend-cann-commercial-envvars
      impl: repocard:catlass
    - concept: 集合通信 HCCL
      external: AscendV 知识可视化（HCCL/LCCL）
      ours: web:ascend-cann-commercial-envvars
      impl: repocard:hccl_transfer
    - concept: Cube/Vector 双单元
      external: AscendV 硬件可视化（910B/910_95 架构动画 + FCodeQ Q1 同步代码）
      ours: reponote:agent-skills:community/Op/ascendc-operator-design/references/hardware-architecture.md
      impl: repocard:catlass
    - concept: 超节点组网
      external: AscendV 硬件可视化（A5 代际）
      ours: paper:huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod
      impl: web:ascend-cann-commercial-envvars
  reference_map:
    - {platform: AscendV, module: 硬件可视化, url: 'https://ascendv.openx.huawei.com/', desc: 910_95/910B/310P 三代 AI Core 架构图 + 算子单步执行动画, when: 需要交互式理解 Cube/Vec/MTE 流水时}
    - {platform: AscendV, module: 算子可视化, url: 'https://ascendv.openx.huawei.com/', desc: Matmul/量化/Attention/MoE/多模态算子全景图 + 运行图, when: 选算子、看算子边界时}
    - {platform: AscendV, module: AscendC API 可视化, url: 'https://ascendv.openx.huawei.com/', desc: API 按类组织（搬运/单目/双目/排序/精度转换）+ 数据通路标注, when: 写 AscendC 算子查 API 时}
    - {platform: AscendV, module: 知识可视化, url: 'https://ascendv.openx.huawei.com/', desc: double buffer/tiling/TPipe/TQue/GlobalTensor/内存格式概念体系, when: 建立 AscendC 概念框架时}
    - {platform: AscendV, module: 精度使能, url: 'https://ascendv.openx.huawei.com/', desc: "12步搞定算子精度问题 + 精度案例库", when: 算子精度调优卡壳时}
    - {platform: AscendV, module: 性能使能, url: 'https://ascendv.openx.huawei.com/', desc: "12步搞定算子性能优化 + Vec/MTE2/MTE3/Cube API 性能数据", when: 算子性能调优时}
    - {platform: AscendV, module: FCodeQ, url: 'https://ascendv.openx.huawei.com/', desc: 算子开发 FAQ + AI 问答, when: 具体开发问题速查}
    - {platform: AscendV, module: 模型可视化, url: 'https://ascendv.openx.huawei.com/', desc: DeepSeek-R1/Qwen3/Pangu 模型卡片, when: 快速了解模型定位（机制深读回本库）}
  gap_list:
    - ~~达芬奇架构手册~~（2026-09-04 关闭：agent-skills 仓 hardware-architecture 深读覆盖抽象架构层）
    - ~~HCCL 使用指南~~（2026-09-04 关闭：hcclug 通信域创建页已入库深读）
    - MindIE vs vllm-ascend 选型对照（官方无此页，需自建或补抓第三方分析）
    - HCCL vs NCCL 接口语义对照（待找权威来源）
    - CANN 软件栈分层总览（驱动/runtime/编译器关系图）→ webs_download_list.txt
  repo_landscape:
    - {name: MindSpeed 训练家族, match: ['mindspeed', 'mindspeed-.*', 'megatronadaptor', 'transformerenginenpu']}
    - {name: MindIE 推理家族, match: ['mindie-.*']}
    - {name: 推理引擎与后端, match: ['vllm', 'vllm-ascend', 'xllm', 'xllm_ops', 'xllm-.*', 'xllm_atb_layers', 'text-embeddings-inference', 'mindinferenceservice']}
    - {name: 算子与编译, match: ['triton-ascend', 'triton-ascend-kernels', 'triton-distributed-ascend', 'catlass', 'torch_npu_ops', 'torchair', 'op-plugin', 'apex', 'tilelang-ascend', 'ascend-transformer-boost', 'fbgemm-ascend', 'hierarchicalkv-ascend', 'torchao_npu', 'torchcomms_npu', 'monarch_npu', 'ascendnpu-ir', 'tvm', 'tvm-ffi', 'llvm-project', 'torch-mlir', 'ascendc-kernelgen-data', 'ops-rec']}
    - {name: 通信与存储, match: ['hccl.*', 'memfabric.*', 'memcache', 'parakv', 'mooncake', 'tensorpipe', 'transferqueue', 'brpc']}
    - {name: 集群管理与部署, match: ['mind-cluster', 'mindcluster-.*', 'ascend-deployer', 'ascend-docker-image', 'fsdpturbo', 'ray-ascend', 'slime-ascend', 'torchtitanturbo']}
    - {name: 调优与工具链 (msIT/mstt 族), match: ['msit', 'mstt', 'msprof.*', 'msdebug', 'msprobe', 'mstx', 'mspti', 'msmemscope', 'msmonitor', 'mscommreport', 'msop.*', 'msinsight', 'msboost', 'mskl', 'mskpp', 'msmodeling', 'msmodelslim', 'msserviceprofiler', 'mssanitizer', 'msot', 'msagent', 'mef', 'perf-reference-ascend', 'atk']}
    - {name: 模型套件与行业 SDK, match: ['modelzoo.*', 'recsdk', 'visionsdk', 'ragsdk', 'multimodalsdk', 'mindsdk-referenceapps', 'indexsdk', 'omsdk', 'drivingsdk', 'model-agent', 'vision', 'pytorch', 'pytorch-ecosystem', 'pytorch-xllmai', 'docs', 'community', 'agent-skills', 'agentsdk', 'solution-agent', 'ecodevhub', 'ascend-agreements', 'release-management', 'infrastructure', 'ci-infra']}
    - {name: 三方依赖镜像, match: ['cutlass', 'composable_kernel', 'faiss', 'sentencepiece', 'flashinfer', 'flashgen', 'spdlog', 'etcd-cpp-apiv3', 'cpprestsdk', 'gperftools', 'libbacktrace', 'libdevice', 'minja', 'mockcpp', 'parallel-hashmap', 'smhasher', 'taco', 'xxhash', 'dlpack']}
```
