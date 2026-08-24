---
paper_num: "24"
title: "KIMI K2: OPEN AGENTIC INTELLIGENCE"
authors: ""
date: "2026/1/19"
arxiv: "https://arxiv.org/abs/2507.20534"
pdf: "papers/kimi-k2-open-agentic-intelligence.pdf"
slug: "kimi-k2-open-agentic-intelligence"
tags: []
---

# KIMI K2: OPEN AGENTIC INTELLIGENCE

> [!abstract] 摘要（原文）
> 1\. 🚀 Kimi K2是一款万亿参数的MoE大型语言模型，激活参数达320亿，其预训练采用了新颖的MuonClip优化器，在15.5万亿token数据上实现了无损失尖峰的稳定训练。 2. 🤖 该模型通过大规模agentic数据合成管线和结合可验证奖励与自批判机制的强化学习框架进行后训练，显著提升了其在工具使用、软件工程和通用任务中的agentic能力。 3. 🏆 Kimi K2在Tau2-Bench、ACEBench、SWE-Bench Verified和LiveCodeBench v6等多个Agentic和编程基准测试中取得了领先的开放模型表现，并在LMSYS Arena排行榜上成为排名第一的开源模型。

## 元信息
- **发表日期**: 2026/1/19
- **作者**: —
- **arXiv**: https://arxiv.org/abs/2507.20534
- **本地 PDF**: `papers/kimi-k2-open-agentic-intelligence.pdf`
- **页数**: 32

## 图表（原文 caption + 页码）

### Figure 1 (p.1) ⭐深度解读
![[assets/crops/kimi-k2-open-agentic-intelligence-fig01.png]]
*整页渲染: ![[assets/kimi-k2-open-agentic-intelligence-p01.png]]*
> [!quote] caption
> Kimi K2 main results.2 1https://huggingface.co/moonshotai/Kimi-K2-Instruct 2All models evaluated above are non-thinking models. For SWE-bench Multilingual, we evaluated only Claude 4 Sonnet because the cost of Claude 4 Opus was prohibitive.[cs.LG] 3 Feb 2026

> [!tip] 技术解读（多模态）
> 【图文联合解读】**核心对象与数据**：Figure 1在"Agentic and Competitive Coding"分组下对比 Kimi-K2-Instruct 与 6 个开源/闭源基座（含 DeepSeek-V3-0324、Qwen3-235B-A22B、GPT-4.1、Claude 4 Opus/Sonnet、Gemini 2.5 Flash 非思考模式）在 6 项基准的得分：SWE-bench Verified K2=65.8（Claude 4 Opus 72.5 最高）、Multilingual 47.3、LiveCodeBench v6 53.7、OJBench 27.1、AceBench 66.1、AIME 2025 76.5。

**关键结论**：K2 在编码与智能体类任务全面领先开源对手（DeepSeek/Qwen3），并多数超越 GPT-4.1、Claude 4；仅在 SWE-bench Verified 与 AIME 2025 数学推理（GPT-4.1=80.1）上略逊于闭源 SOTA。

**作用**：作为首页主结果图，确立 K2 在非思考模式下作为开源开放智能体模型的整体竞争力定位。

### Figure 2 (p.4) ⭐深度解读
![[assets/crops/kimi-k2-open-agentic-intelligence-fig02.png]]
*整页渲染: ![[assets/kimi-k2-open-agentic-intelligence-p04.png]]*
> [!quote] caption
> Left: During a mid-scale training run, attention logits rapidly exceed 1000, which could lead to potential numerical instabilities and even training divergence. Right: Maximum logits for Kimi K2 with MuonClip and t = 100 over the entire training run. The max logits rapidly increase to the capped value of 100, and only decay to a stable range after approximately 30% of the training steps, demonstra

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图2解读：**

**核心数据**：左图（Vanilla + Muon）显示注意力 logits 在约16k步内单调上升至1200+且无收敛迹象；右图（Kimi K2 + MuonClip, τ=100）在约220k步训练中，logits 迅速触及封顶值100，持续约30%训练步后衰减至稳定的30–40区间。

**关键结论**：对比证明 Muon 优化器单独使用会引发注意力 logits 爆炸（>1000），导致数值不稳定甚至训练发散；而 QK-Clip 通过按头裁剪 W_q 权重，将 logits 硬性限制在 τ=100 以内，使其在训练前期触发后自然回落，验证了 QK-Clip 对注意力 logit 增长的有效调控。

**方法链路作用**：作为论文核心创新 MuonClip 的直接经验证据，衔接"问题暴露（logits爆炸）→ 机制设计（QK-Clip）→ 规模化可行性证明（K2全量训练）"，为后续百万亿token级训练稳定性背书。

### Figure 3 (p.5) ⭐深度解读
![[assets/crops/kimi-k2-open-agentic-intelligence-fig03.png]]
*整页渲染: ![[assets/kimi-k2-open-agentic-intelligence-p05.png]]*
> [!quote] caption
> Per-step training loss curve of Kimi K2, without smoothing or sub-sampling. It shows no spikes throughout the entire training process. Note that we omit the very beginning of training for clarity. A key advancement in the pre-training data of Kimi K2 over Kimi K1.5 is the introduction of a synthetic data generation strategy to increase token utility. Specifically, a carefully designed rephrasing p

> [!tip] 技术解读（多模态）
> 【图文联合解读】**Figure 3 图文联合解读**

Figure 3 展示 Kimi K2 逐 step 训练 loss 曲线：横轴为 0–15.5 万亿 tokens，纵轴 loss 范围约 1.3–2.0，未经平滑或下采样。曲线自起点 ~2.0 在前 2T tokens 内陡降至 ~1.55，中段缓慢下行，至末端约 1.27；曲线密集连续，**全程未出现任何 loss spike 或发散点**。

论文借此论证两点关键结论：① 引入合成数据生成策略后，预训练数据分布稳定、无异常样本冲击；② 整条工程管线（数据加载、混合、tokenization）足够鲁棒，支撑 15T+ tokens MoE 长程训练平稳收敛。

该图在论文链路中扮演**"预训练可靠性"的实证锚点**——它先于第 4 节 MuonClip 优化器、第 5 节 SFT/RL post-training 出现，证明 K2 底座在规模化、长时间训练下是健康可信的，从而为后续能力评测（Table 3 中多项 SOTA）提供方法论前提。

### Figure 4 (p.5) ⭐深度解读
![[assets/crops/kimi-k2-open-agentic-intelligence-fig04.png]]
*整页渲染: ![[assets/kimi-k2-open-agentic-intelligence-p05.png]]*
> [!quote] caption
> • Fidelity verification: To ensure consistency between original and rewritten content, we perform fidelity checks that compare the semantic alignment of each rephrased passage with its source. This serves as an initial quality control step prior to training.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图4展示自回归分块改写流水线结构：长文本被切分为3个输入块（顶部蓝色"WRNHQV"上下文窗口保留），每块经紫色"UHUULWH SUR"改写提示生成绿色"SDUWLDO RXWSXW"局部输出，前后块通过"DXWR UHJUHVVLYH"反馈串联，最终拼接为完整改写段落。

**论证结论**：通过切块+滑动上下文+顺序改写，可在保证语义衔接的前提下处理超长输入；配合fidelity verification（逐块语义对齐校验），为训练数据构建提供前置质量控制。

**链路作用**：该图对应数据预处理阶段，承担"长文本→训练可用改写语料"的转换职能，是模型训练前的关键清洗/改写环节。

### Figure 5 (p.7) ⭐深度解读
![[assets/crops/kimi-k2-open-agentic-intelligence-fig05.png]]
*整页渲染: ![[assets/kimi-k2-open-agentic-intelligence-p07.png]]*
> [!quote] caption
> Sparsity Scaling Law. Increasing sparsity leads to improved model performance. We fixed the number of activated experts to 8 and the number of shared experts to 1, and varied the total number of experts, resulting in models with different sparsity levels. 10 11

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

1) **核心对象与数据**：左图为 Validation Loss vs Training FLOPs（对数轴），含绿、紫、蓝、橙多条 MoE 训练曲线，每条对应"激活专家=8、共享专家=1、总专家数不同"的稀疏度配置，曲线呈典型 lr schedule 的"陡降–回升"末端形态；右图为 Loss vs Training Tokens，4 条虚线对应 1.2/2.2/4.5/9.0×10²⁰ FLOPs 四档算力，比较"层数=头数"方形模型与"头数翻倍"圆形对照。

2) **关键技术结论**：固定激活专家数下，增大总专家数（即提高稀疏度）能持续压低验证损失，呈现稳定的稀疏度 scaling law——同等算力时模型越稀疏越优。

3) **论文链路作用**：为 Kimi K2 选用高稀疏 MoE 架构（众多专家、少量激活）提供 scaling 实证支撑，奠定"以稀疏换性能"的设计前提，并与右图共同验证最优训练资源分配策略。

### Figure 6 (p.7) ⭐深度解读
![[assets/crops/kimi-k2-open-agentic-intelligence-fig06.png]]
*整页渲染: ![[assets/kimi-k2-open-agentic-intelligence-p07.png]]*
> [!quote] caption
> Scaling curves for models with number of atten- tion heads equals to number of layers and their counter- parts with doubled attention heads. Doubling the number of attention heads leads to a reduction in validation loss of approximately 0:5% to 1:2%.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**左图**：横轴为Training FLOPs（10²⁰–10²¹，对数刻度），纵轴为Validation Loss（≈1.3–1.8）。展示蓝、紫、绿、橙四组不同规模模型的loss下降轨迹——实线为含cosine学习率重启的原始训练loss（可见周期性尖峰回弹），虚线为对应的拟合下降趋势。

**右图**：横轴为Training Tokens（≈10¹¹），按1.2 / 2.2 / 4.5 / 9.0 ×10²⁰ FLOPs四档绘出U形loss曲线。方块标记代表"头数=层数"基线，圆点标记为"头数翻倍"对照组——在同一计算量档位下，圆点曲线稳定低于方块，降幅约0.5%–1.2%（最优loss由≈1.75降至≈1.38）。

**技术结论**：在Kimi K2的规模区间内，适度增加注意力头数（而非单纯加深层数）可稳定带来validation loss收益，且对所有四个计算档位一致生效。

**论文作用**：属于架构消融scaling实验，为Kimi K2选择"层数较浅、头数较多"的配置提供实证依据，支撑后续Muon优化器与MLA等结构设计决策。

### Figure 7 (p.8) ⭐深度解读
![[assets/crops/kimi-k2-open-agentic-intelligence-fig07.png]]
*整页渲染: ![[assets/kimi-k2-open-agentic-intelligence-p08.png]]*
> [!quote] caption
> Computation, communication and offloading overlapped in different PP phases.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

1）**图示结构**：采用 8 阶段 VPP+1 warmup 流水线，下方每阶段含 8 个微批次（编号 1–8），蓝色为前向、红色为反向；上方分三组高亮相，分别展示"Offload"、"Onload"、"Load"三类内存操作与 Attn/MLP/WGrad 计算、EP-D/EP-C 通信（绿色 PP 通信条）的时序叠加。

2）**关键技术结论**：EP 的 dispatch/combine 通信与 Offload/Onload/Load 内存传输均被成功隐藏在计算时间之下，三类资源（计算、通信、内存）实现并行重叠，避免了 EP 通信和 MoE 权重搬运成为流水线瓶颈。

3）**作用**：该图作为系统级训练效率证据，支撑论文"Kimi K2 大规模 MoE 训练低开销"的论断，证明其异构重叠调度机制可在不增加 bubble 的前提下容纳 EP 通信与权重 offload，是支撑万亿参数 MoE 可行训练的核心调度方案之一。

### Figure 8 (p.10) ⭐深度解读
![[assets/crops/kimi-k2-open-agentic-intelligence-fig08.png]]
*整页渲染: ![[assets/kimi-k2-open-agentic-intelligence-p10.png]]*
> [!quote] caption
> Data synthesis pipeline for tool use. (a) Tool specs are from both real-world tools and LLMs; agents and tasks are the generated from the tool repo. (b) Multi-agent pipeline to generate and filter trajectories with tool calling. (a) t-SNE visualization of real MCP tools, colored by their original source categories (b) t-SNE visualization of synthetic tools, colored by pre-defined domain categories

> [!tip] 技术解读（多模态）
> 【图文联合解读】**(a) 核心结构**：图分两部分。**(a) 工具规格合成**——MCP 真实工具与由 Domains→Applications 衍生的合成工具共同汇入 Tool Repository，进而生成 Agents 与带 rubric 的 Tasks；**(b) 轨迹生成与过滤**——Task 驱动 User Agent 与 Agent 交互，Agent 通过 observation/call 调用 Tool Simulator 产出 trajectories，再由 Judge Agent 依据 Rubrics 筛选为 Filtered Data。

**论证结论**：真实+合成双源工具库配合"多智能体—rubric 过滤"管道，可规模化产出高质量工具调用训练轨迹。

**整体作用**：作为 Kimi K2 agentic 能力 SFT 训练的数据合成基石，为下游 tool-use 评测与对齐提供可验证的监督数据。

### Figure 9 (p.10) ⭐深度解读
![[assets/crops/kimi-k2-open-agentic-intelligence-fig09.png]]
*整页渲染: ![[assets/kimi-k2-open-agentic-intelligence-p10.png]]*
> [!quote] caption
> t-SNE visualizations of tool embeddings. (a) Real-world MCP tools exhibit natural clustering based on their original source categories. (b) Synthetic tools are organized into pre-defined domain categories, providing systematic coverage of the tool space. Together, they ensure comprehensive representation across different tool functionalities.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图(a)为真实MCP工具的t-SNE二维投影，数百点按源类别着色(黄/绿/紫/蓝/橙/红等)，可见同色点呈局部弱聚类(如右侧黄色簇、左上绿色簇)，整体仍混合；图(b)区域在图中未渲染出散点，仅保留标题文字。

作者借此论证：真实工具自然聚类反映来源多样性，合成工具按预定义域系统铺开以补足盲区，二者融合使训练所用工具空间在功能维度上既多样又完备。

该图位于工具库构建环节，是面向后续SFT训练的数据分布证据——证明真实+合成双源策略能为工具调用训练提供均衡且覆盖充分的工具集合，而非偏倚于单一来源。

### Figure 10 (p.14) ⭐深度解读
![[assets/kimi-k2-open-agentic-intelligence-p14.png]]
> [!quote] caption
> Parameter update utilizing a checkpoint engine

> [!tip] 技术解读（多模态）
> **Architecture / Components / Data Flow**

Figure 10 illustrates a three-tier parameter-update pipeline:

1. **Training Engine (top layer)** – holds model weights in DRAM; each worker contributes its local parameter shard.
2. **Distributed Checkpoint Engine (middle layer)** – co-located workers that pull a local parameter copy from the training engine and then broadcast the *full* parameter set across all checkpoint workers, regardless of inference-side sharding.
3. **Inference Engine (bottom layer)** – uses a different sharding scheme, pulling only the parameter shard it needs from the checkpoint engine.

For the 1T Kimi K2 model, updates are streamed parameter-by-parameter in a pipelined fashion to minimize memory footprint.

**Key Technical Takeaway**

By broadcasting the full parameter set cluster-wide rather than using a network-file-system re-shard, the design fully decouples the training and inference engines, simplifies maintenance, and completes a full K2 parameter update in **<30 seconds** — negligible versus a single RL iteration.

**Caption (verbatim)**

> Figure 10: Parameter update utilizing a checkpoint engine

### Figure 11 (p.29) ⭐深度解读
![[assets/kimi-k2-open-agentic-intelligence-p29.png]]
> [!quote] caption
> Chinese in-house benchmark evaluation. rate, i.e. 98.9. On FaithJudge’s RAG tasks the hallucination rate is 7.4 %, likewise present as 92.6 for table consistency.

> [!tip] 技术解读（多模态）
> **Main Figure Description**

The figure content itself is not visibly rendered on this page — only its caption ("Figure 11: Chinese in-house benchmark evaluation.") appears above the surrounding paragraph, with the actual chart area blank. Based on the in-text reference, Figure 11 presents a model comparison chart evaluating Kimi-K2-Instruct against baseline LLMs (ChatGPT-4o-latest, Claude Sonnet 4, DeepSeek-V3-0324) on Chinese in-house held-out benchmarks, likely displayed as win-rate / loss-rate / tie-rate bars or radar-style comparisons per model pair.

**Key Technical Takeaway (≤120 words):**
Kimi-K2-Instruct demonstrates strong, balanced Chinese-language open-ended capability, posting high win-rates of ~65.4% vs ChatGPT-4o-latest, ~64.6% vs Claude Sonnet 4, and ~59.6% vs DeepSeek-V3-0324 on access-restricted in-house benchmarks. Critically, its loss-rate stays uniformly low (~17%) across all comparisons, indicating it rarely loses outright and rarely ties — it consistently wins or comes close. This combination of high win-rate and uniformly low loss-rate (verified on a held-out, contamination-controlled set) provides robust evidence that the Chinese performance is genuine generalization, not benchmark overfitting.

**Caption (verbatim):**
"Figure 11: Chinese in-house benchmark evaluation."

### Figure 12 (p.30) ⭐深度解读
![[assets/kimi-k2-open-agentic-intelligence-p30.png]]
> [!quote] caption
> Applying QK-Clip to Muon in a small-scale setting with an aggresive threshold (t = 30) has negligible impact on loss, indicating that it is a safe and effective method for constraining attention logits.

> [!tip] 技术解读（多模态）
> **Figure Description & Technical Takeaway**

The referenced figure (Figure 12) compares training loss curves between two small-scale MoE models — one using vanilla Muon and the other using MuonClip with an aggressive threshold (τ = 30). The architecture under test is a 0.5B-activated / 3B-total-parameter MoE (presumably the Kimi K2 / MuonScaffold stack), where QK-Clip caps the per-head maximum attention logit S_max at 100. The plot shows two nearly-overlapping loss trajectories over training steps.

**Key takeaway:** Even an aggressive QK-Clip threshold (τ = 30) produces no visible degradation in training loss, confirming that bounding attention logits via MuonClip is a safe intervention — it constrains logit explosion without harming convergence dynamics.

**Verbatim Caption:**

> Figure 12: Applying QK-Clip to Muon in a small-scale setting with an aggressive threshold (t = 30) has negligible impact on loss, indicating that it is a safe and effective method for constraining attention logits.

### Figure 13 (p.32) ⭐深度解读
![[assets/kimi-k2-open-agentic-intelligence-p32.png]]
> [!quote] caption
> pipeline for RL weight update

> [!tip] 技术解读（多模态）
> ## Main Figure Description

The figure presents **Figure 13: pipeline for RL weight update** in three variants (a, b, c), depicting how trained weights from RL engines are resharded into inference engines across GPUs.

**Architecture/Components:**
- Each GPU holds three equal-size device buffers: one **H2D buffer** (Host-to-Device loading of offloaded parameters) and two **IPC buffers** (GPU-to-GPU broadcast, shared with inference engines via memory mapping).
- **Subplot (a)** – Theoretical 3-stage pipeline: (1) async H2D copy of weight shard → (2) copy shard to IPC buffer + broadcast to all devices → (3) inference engines reload from second IPC buffer. All three stages overlap in a pipeline.
- **Subplot (b)** – PCIe-bounded 3-stage: stages collapse into sequential execution because concurrent H2D + broadcast saturate the shared PCIe fabric on H800 clusters.
- **Subplot (c)** – Fixed 2-stage pipeline adopted in practice: (1) synchronous, all-device H2D transfer → (2) broadcast and reload happen in parallel.

**Data flow:** Host memory (offloaded params) → H2D buffer → IPC buffer A → broadcast over NVLink/PCIe → IPC buffer B → inference engine reload.

**Key Technical Takeaway:** Overlapping H2D, Broadcast, and Reload operations yields high bandwidth for resharding weights from train to inference engines; at large scale the parameter set fits the H2D buffer in a single transfer, making the simpler 2-stage pipeline PCIe-friendly.

## Caption (verbatim)

**Figure 13:** pipeline for RL weight update

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.5) ⭐深度解读
![[assets/crops/kimi-k2-open-agentic-intelligence-tab01.png]]
> [!quote] caption
> SimpleQA Accuracy under three rephrasing-epoch configurations

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 1 图文联合解读**

1) **核心数据**：该表对比三组数据增强×训练轮次配置在 SimpleQA 上的准确率——0 改写（原始 wiki-text）/10 epoch = 23.76；1 次改写/10 epoch = 27.39；10 次改写/1 epoch = **28.94**。随改写多样性提升，准确率呈单调上升。

2) **关键技术结论**：在等量训练计算下，**改写带来的数据多样性优于延长 epoch**——10 改写×1 epoch（28.94）显著优于 1 改写×10 epoch（27.39），相较原始文本基线提升 5.18 个百分点，验证了"扩增语料多样性"比"加深单样本训练"更高效。

3) **论文链路作用**：该表为论文数据流水线提供了**消融依据**，支撑 Kimi-K2 训练语料采用大规模 query/answer 改写扩增策略的关键设计选择，与 Figure 1 主结果形成"方法合理性→最终性能"的因果链。

### Table 3 (p.16) ⭐深度解读
![[assets/crops/kimi-k2-open-agentic-intelligence-tab03.png]]
> [!quote] caption
> Performance comparison of Kimi-K2-Instruct against leading open-source and proprietary models across diverse tasks. Bold denotes the global SOTA; underlined bold indicates the best open-source result. Data points marked with * are taken directly from the model’s technical report or blog.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 3 联合解读**

表3对Kimi-K2-Instruct与6个模型（开源2+闭源4）横向评测，分编程、工具使用、数学与STEM三大类共约30项基准。Kimi-K2在编程上多项刷新全局SOTA（LiveCodeBench v6 Pass@1 53.7、OJBench 27.1、SWE-Lancer 39.1、SWE-bench Verified 71.6开源最佳）；工具使用Tau2 airline 56.5、 AceBench 76.5领跑开源；数学与STEM中AIME 2024 69.6、GPQA-Diamond 75.1、HMMT 2025 38.8亦为开源最优。该表与Figure 3稳定训练loss曲线互证，作为后训练阶段的整体能力验证，构成"MuonClip优化+合成数据预训练+大规模Agentic后训练→广域基准领先"的实验闭环核心证据。

### Table 4 (p.18) ⭐深度解读
![[assets/crops/kimi-k2-open-agentic-intelligence-tab04.png]]
> [!quote] caption
> Performance comparison of Kimi-K2-Base against leading open-source models across diverse tasks.

> [!tip] 表格解读（多模态）
> 【图文联合解读】Table 4 将 Kimi-K2-Base（MoE，激活32B/总1043B）与 DeepSeek-V3-Base（37B/671B）、Llama4-Maverick-Base（17B/400B）、Qwen2.5-72B-Base（72B Dense）横向对比，覆盖英语/代码/数学/中文四大类共22项基准。K2 在多数项目领先：SimpleQA 35.25（Qwen 10.31）、CSimpleQA 77.57（Qwen 50.53）、EvalPlus 80.33（V3 65.61）、MATH 70.22（V3 61.70）、AGIEval 84.23、C-Eval 92.50、TriviaQA 85.09；仅在 GPQA-Diamond（48.11 vs 50.51）、HellaSwag、CMATH、ARC-Challenge 等个别项略逊。

论证结论：以更低激活参数即可在广泛任务取得 SOTA，验证基础预训练质量。

链路作用：作为预训练基线，标定基模型能力上限，为后续指令微调与 agentic 能力扩展提供起点。

### Table 5 (p.19) ⭐深度解读
![[assets/crops/kimi-k2-open-agentic-intelligence-tab05.png]]
> [!quote] caption
> Enabled Plugins and Strategies

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 5 联合解读**

**1）核心对象与结构**
该表枚举了安全评估（红队测试）中启用的全部插件与攻击策略，按风险维度分为 **6 大类约 50 项**：Harmful（9 项，如 Hate Speech、Sexual Content、ToxicChat）、Criminal（11 项，覆盖生化武器、童童、网络犯罪、知识产权等）、Misinformation（11 项，含幻觉、错误信息、政治倾向等）、Privacy（5 项 PII 泄露场景）、Security（11 项，如 ASCII Smuggling、CyberSecEval、Harmbench、Prompt Extraction 等基准与攻击）以及 Strategy（4 项：Basic、Prompt Injection、Iterative Jailbreak、Crescendo）。

**2）论证结论**
体现 Kimi K2 的安全评测覆盖面广、攻击手段多样，既涵盖内容合规（有害/违法/虚假），也涵盖技术对抗（越狱、注入、隐私窃取），说明作者对模型进行了系统化、多角度的红队压力测试。

**3）在论文中的作用**
该表是 K2 安全对齐与防御验证章节的关键补充，明确披露评测所用插件清单，保证实验可复现性，并支撑后续安全性能结论的可靠性。

### Table 6 (p.19) ⭐深度解读
![[assets/crops/kimi-k2-open-agentic-intelligence-tab06.png]]
> [!quote] caption
> Safety Evaluation Results

> [!tip] 表格解读（多模态）
> 【图文联合解读】Table 6横向比较Kimi-K2-Instruct与DeepSeek-V3-0324、DeepSeek-R1、Qwen3-235B-A22B四模型，纵向为5类插件（Harmful/Criminal/Misinformation/Privacy/Security）×5种攻击策略的安全得分。K2在Basic/Base64下接近满分（96.97–100），面对Crescendo等强多轮越狱仍维持56–96分。论文据此论证Kimi K2在agent场景下的安全鲁棒性达到开源SOTA水平，与Qwen3-235B等强基线相当，构成其综合评测链中安全维度的关键证据。

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\mathbf W_q^{h} \gets \gamma^{\alpha} \mathbf W_q^{h} \qquad \mathbf W_k^{h} \gets \gamma^{1-\alpha} \mathbf W_k^{h}
$$

$$
S_{\max} = \max_{i,j} \bigl(q_i^{\vphantom{\top}}\! \cdot k_j\bigr)
$$

$$
|q_i \!\cdot\! k_j| \le \|q_i\|\|k_j\| \le \|x_i\|\|x_j\|\|\mathbf W_q\|\|\mathbf W_k\|,
$$

$$
\mathbf W_{t-1}=\sum_i \sigma_i\,u_i v_i^{\top}
$$

$$
q_i\cdot k_j=(x_i \mathbf W_q)\cdot (x_j \mathbf W_k).
$$

$$
L_{\mathrm{RL}}(\theta) = \mathbb{E}_{x \sim\mathcal{D}}\left[ \frac{1}{K} \sum_{i=1}^K \left[ \left( r(x, y_i) - \bar{r}(x)- \tau \log \frac{\pi_\theta(y_i | x)}{{\pi}_{\mathrm{old}}(y_i | x)} \right)^2 \right]\right] \, ,
$$

$$
\Delta\mathbf W_t &= \sum_j \bar\sigma\,\bar u_j \bar v_j^{\top}
$$

$$
\mathbf W_t \leftarrow \sum_i \sigma_i u_i v_i^{\top} + \sum_j \bar\sigma\,\bar u_j \bar v_j^{\top}
$$

$$
\mathbf{Q}^{h} = \mathbf X \mathbf W_q^{h}, \quad \mathbf K^{h} = \mathbf X \mathbf W_k^{h}, \quad \mathbf V^{h} = \mathbf X \mathbf W_v^{h}.
$$

$$
\mathbf O^{h} = \operatorname{softmax}\left( \frac{1}{\sqrt{d}} \mathbf Q^{h} \mathbf K^{h\top} \right) \mathbf V^{h}.
$$

$$
S_{\max}^{h} = \frac{1}{\sqrt{d}} \max_{\mathbf X \in B} \max_{i,j} \mathbf Q_i^{h} \mathbf K_j^{h\top}
$$

## 技术点深读（DEEP）

![[deep/kimi-k2-open-agentic-intelligence]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/kimi-k2-open-agentic-intelligence.txt`（112693 字符）供引用检索。