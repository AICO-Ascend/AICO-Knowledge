# CURATION.md — 知识书架策展定义（人工维护的唯一文件）

> `bookshelf_build.py` 读取本文件内嵌的 ```yaml 块生成 `SHELF.md`（ascend_infra 为独立手工 HTML 体系，见文末）。
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
  **先知道有什么，才知道能问什么。** AI 时代的瓶颈从"找答案"移到了"提问题"——
  模型什么都能答，但人不知道有什么可问。这个书架是 AI Infra 领域的知识版图：
  按技术栈六层摆开，扫一遍就有了这个领域的词汇表和坐标系——
  知道 MLA、DSA、PD 分离、fb-overlap 这些概念存在，你才会去问它们。
  每个条目挂着实打实的深读资产，问完直接有答案。

  这不是链接收藏夹——每条目都挂着**自有深读资产**（点开即全文解读/裁剪图/LaTeX 公式/逐字还原表）。
  组织轴是一条技术栈主线：**一个 Agent 需求往下钻**——选什么模型（L2）→ 怎么训怎么推（L3）→
  落在哪些算子上（L4）→ 跑在什么系统软件栈上（L5）→ 钉在什么硬件与集群拓扑上（L6）。
  与 InfraTech 的差异：他们链知乎文章，我们链 69 篇论文 6 段深读 + 134 仓 1,719 篇文档七节深读 +
  官方手册网页深读；与 AscendV 官方可视化平台共生互链（见 AscendInfra 昇腾专区）。

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
    交互式算子图解与精度/性能方法论见 [AscendInfra 专区](ascend_infra.html)。
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
        title: MindSpeed-RL EPLB 专家负载均衡
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
        ascend: 适配标杆模型（MindSpeed/vllm-ascend 均支持）
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
    title: 投机解码
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
    title: 扩展阅读
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
        title: MindSpeed
        category: 训练框架
        heat: 3
        difficulty: 2
        note: 昇腾训练加速库卡片（fb-overlap 3 图 M3 解读）
        ascend: 昇腾训练栈核心
      - ref: reponote:mindspeed:docs/zh/features/megatron_moe/megatron-moe-fb-overlap.md
        title: MindSpeed MoE 前反向通信掩盖（fb-overlap）
        heat: 2
        difficulty: 3
        note: MoE 前反向通信掩盖（含 3 图图文联合解读）
        ascend: MindSpeed 原生特性
      - ref: reponote:mindspeed:docs/zh/features/Automatic_Parallelism.md
        title: MindSpeed 自动并行特性
        difficulty: 2
        note: 自动并行
        ascend: MindSpeed 原生特性
      - ref: reponote:mindspeed-rl:docs/zh/features/context_parallel.md
        title: MindSpeed-RL 长序列并行（Context Parallel）
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
        title: vLLM
        category: 推理框架
        heat: 3
        difficulty: 2
        note: vLLM 仓卡片（版本线 v0.28.1rc0）
      - ref: repocard:vllm-ascend
        title: vllm-ascend
        category: 推理框架
        heat: 3
        difficulty: 2
        note: 昇腾后端卡片（v0.25.1rc1 · ChunkKdaFwd 发现）
        ascend: 昇腾推理栈核心
      - ref: reponote:vllm-ascend:docs/source/tutorials/features/pd_disaggregation_mooncake_multi_node.md
        title: vllm-ascend PD 分离实战（Mooncake 多机）
        difficulty: 3
        note: 昇腾 PD 分离实战（Mooncake 多机）
        ascend: vllm-ascend 原生教程
      - ref: reponote:vllm-ascend:docs/source/tutorials/features/dynamic_chunked_pipeline_parallel.md
        title: vllm-ascend 动态 Chunked 流水并行
        difficulty: 3
        ascend: vllm-ascend 原生教程
      - ref: reponote:xllm:docs/src/content/docs/en/features/disagg_pd.md
        title: xLLM PD 分离设计
        difficulty: 3
        note: xLLM PD 分离设计
      - ref: reponote:xllm:docs/src/content/docs/en/features/chunked_scheduler.md
        title: xLLM Chunked 调度器
        difficulty: 2
      - ref: repocard:xllm
        title: xLLM
        category: 推理框架
        heat: 2
        difficulty: 2
        note: xLLM 卡片（v0.10.1 · GLM-5.3-Flash day-0 时间线）
      - ref: web:vllm-cli-serve
        title: vLLM serve CLI 参数手册
        category: 推理框架
        heat: 2
        difficulty: 1
        note: vLLM serve 312 项参数手册（网页深读，逐字还原）
      - ref: web:vllm-ascend-quickstart
        title: vllm-ascend 快速上手指南
        category: 推理框架
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
        title: MindIE-LLM
        category: 推理框架
        heat: 2
        difficulty: 2
        ascend: 昇腾商用推理引擎
      - ref: reponote:mindie-llm:docs/zh/developer_guide/architecture_design/architecture_overview.md
        title: MindIE 架构设计
        difficulty: 2
        note: MindIE 架构设计
        ascend: MindIE 原生文档
      - ref: reponote:mindie-llm:docs/zh/user_guide/feature/asynchronous_scheduling.md
        title: MindIE 异步调度特性
        difficulty: 2
        ascend: MindIE 原生特性
      - ref: reponote:mindie-llm:docs/zh/user_guide/feature/attention_quantization.md
        title: MindIE Attention 量化特性
        difficulty: 3
        ascend: MindIE 原生特性
      - ref: repocard:mindie-turbo
        title: MindIE-Turbo
        category: 推理框架
        ascend: 昇腾推理加速
      - ref: repocard:mindie-motor
        title: MindIE-Motor
        category: 推理框架
        ascend: 昇腾推理编排
      - ref: repocard:mindie-sd
        title: MindIE-SD
        category: 推理框架
        ascend: 昇腾多模态推理
      - ref: repocard:msmodelslim
        title: msModelSlim
        category: 推理框架
        note: 模型压缩工具链（量化专题归并入此）
        ascend: 昇腾模型压缩

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
        title: Triton-Ascend
        category: 算子
        heat: 2
        difficulty: 2
        note: Triton 昇腾后端（已迁 triton-lang 主线）
        ascend: GPU 算子迁移昇腾的最低门槛
      - ref: reponote:triton-ascend:docs/zh/architecture_design_and_core_features.md
        title: Triton-Ascend 架构设计与核心特性
        difficulty: 2
        ascend: Triton-Ascend 原生文档
      - ref: reponote:triton-ascend:docs/zh/migration_guide/architecture_difference.md
        title: Triton-Ascend 昇腾与 GPU 开发差异
        heat: 2
        difficulty: 2
        note: 昇腾与 GPU 的开发差异（迁移必读）
        ascend: 迁移指南
      - ref: repocard:catlass
        title: CATLASS
        category: 算子
        difficulty: 3
        note: CATLASS——CANN 版 CUTLASS（v1.1.0）
        ascend: 昇腾 Cube 算子模板库
      - ref: repocard:torch_npu_ops
        title: torch_npu_ops
        category: 算子
        difficulty: 2
        ascend: torch_npu 算子库
      - ref: repocard:xllm_ops
        title: xllm_ops
        category: 算子
        difficulty: 2
        ascend: xLLM 高性能算子库
      - ref: reponote:vllm-ascend:csrc/attention/chunk_kda_fwd/docs/design.md
        title: ChunkKdaFwd 算子设计文档
        heat: 2
        difficulty: 3
        note: ChunkKdaFwd 算子设计（KDA 落地的直接证据）
        ascend: vllm-ascend 仓内设计文档
      - ref: reponote:vllm-ascend:csrc/attention/sparse_attention_score/docs/sparse_attention_score_design.md
        title: SparseAttentionScore 算子设计文档
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
        title: CANN 环境变量参考 · 商用版 900
        category: 系统软件
        heat: 3
        difficulty: 1
        note: CANN 商用 900 环境变量索引（132 表行逐字还原）
        ascend: CANN 官方手册
      - ref: web:ascend-cann-community-envvars
        title: CANN 环境变量参考 · 社区版 910beta1
        category: 系统软件
        heat: 2
        difficulty: 1
        note: 社区 910beta1 版（与商用版一致）
        ascend: CANN 官方手册
      - ref: web:ascend-pytorch-envvars
        title: Ascend PyTorch 环境变量参考
        category: 系统软件
        heat: 2
        difficulty: 1
        note: PyTorch NPU 环境变量（22 变量：算子执行/编译/内存/HCCL）
        ascend: Ascend Extension for PyTorch 官方手册
      - ref: web:ascend-cann-hccl-guide
        title: HCCL 通信域创建指南
        category: 系统软件
        heat: 2
        difficulty: 2
        note: HCCL 用户指南·基于 root 节点信息创建通信域（9 表逐字还原）
        ascend: HCCL 官方手册
      - ref: repocard:torchair
        title: torchair
        category: 系统软件
        difficulty: 2
        note: 图编译（Ascend IR）
        ascend: 昇腾图编译栈
      - ref: reponote:torchair:docs/zh/ascend_ir/features/advanced/cc_parallel.md
        title: torchair 计算与通信并行
        difficulty: 3
        note: 计算与通信并行（图编译层）
        ascend: torchair 原生特性
      - ref: reponote:torchair:docs/zh/ascend_ir/features/advanced/deterministic.md
        title: torchair 算子级确定性计算
        difficulty: 2
        note: 算子级确定性计算
        ascend: torchair 原生特性
      - ref: repocard:hccl_transfer
        title: hccl_transfer
        category: 系统软件
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
        title: vllm-ascend 快速上手指南
        category: 推理框架
        difficulty: 1
        note: Atlas A2/A3/950DT/300I DUO 支持矩阵
        ascend: 硬件支持表（逐字还原）
      - ref: concept:npu-ascend
        note: 概念页：昇腾 NPU 跨论文综合

# ═══════════ 模型卡片 ═══════════
model_cards:
  - name: DeepSeek V3
    keywords: MLA · MoE · MTP
    structure: model:deepseek_v3.md
    others:
      - {label: 论文深读, ref: paper:deepseek-v3-technical-report}
      - {label: MLA 裁剪图, ref: crop:deepseek-v3-technical-report-fig02-mla.png}
  - name: DeepSeek V3.2
    keywords: MLA · DSA · MoE
    structure: model:deepseek_v3_2.md
  - name: DeepSeek V4
    keywords: MLA · DSA
    structure: model:deepseek_v4.md
    others:
      - {label: 论文深读, ref: paper:deepseek-v4-towards-highly-efficient-million-token-context-intelligence}
  - name: DeepSeek R1
    keywords: MLA · MoE
    structure: model:deepseek_r1.md
    others:
      - {label: 论文深读, ref: paper:deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning}
  - name: Kimi K2 / K2.5
    keywords: MLA · MoE / +MoonViT
    structure: model:kimi_k_2_5.md
    others:
      - {label: K2 结构解析, ref: model:kimi_k_2.md}
      - {label: K3 深读, ref: paper:kimi-k3-open-frontier-intelligence}
  - name: Kimi K3
    keywords: KDA · Gated MLA · AttnRes · Stable LatentMoE
    structure: model:kimi_k_3.md
    others:
      - {label: 论文深读, ref: paper:kimi-k3-open-frontier-intelligence}
  - name: Kimi Linear
    keywords: KDA
    structure: model:kimi_linear.md
    others:
      - {label: 论文深读, ref: paper:kimi-linear-an-expressive-efficient-attention-architecture}
      - {label: 昇腾算子佐证, ref: reponote:vllm-ascend:csrc/attention/chunk_kda_fwd/docs/design.md}
  - name: Qwen3-VL
    keywords: MoE · DeepStack · Interleaved-MRoPE
    structure: model:qwen3_vl.md
    others:
      - {label: 论文深读, ref: paper:qwen3-vl-technical-report}
  - name: Qwen2.5-VL
    keywords: ViT · Window Attention
    structure: model:qwen2_5_vl.md
    others:
      - {label: 论文深读, ref: paper:qwen2-5-vl-technical-report}
  - name: GLM 5.3-Flash
    keywords: KDA · DSA · MoE
    structure: model:glm_5_3_flash.md
    others:
      - {label: xllm day-0 适配, ref: repocard:xllm}

# ═══════════ 辅助工具 ═══════════
tools:
  - {name: MFU 计算器, ref: tool:mfu_calculator.html, category: 训练估算, note: 6ND 公式在线算 MFU/训练时长, 浏览器直接打开}
  - {name: 推理显存 & KV Cache 计算器, ref: tool:kv_memory_calculator.html, category: 推理估算, note: 权重+KV cache 显存估算, 支持 MHA/GQA/MLA 对照}
  - {name: LLM 大模型显存计算公式与优化, ref: ext:显存计算文章:https://zhuanlan.zhihu.com/p/687226668, category: 推理估算, note: 显存构成公式化拆解（社区文章）}
  - {name: LLM 预训练模型 MFU 计算方法, ref: ext:MFU 文章:https://zhuanlan.zhihu.com/p/20401860293, category: 训练估算, note: MFU 方法论（社区文章）}
```

## AscendInfra 专区（独立体系）

AscendInfra 昇腾专区**不是书架逻辑的延伸**，是独立的可视化 HTML 体系：
`bookshelf/ascend_infra.html`（手工维护的单文件页面，自绘 SVG 架构图/算子全景/概念卡，
数据全部来自本库深读资产）。本文件不再携带其策展 yaml。
