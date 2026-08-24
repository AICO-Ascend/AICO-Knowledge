---
paper_num: "57"
title: "Kimi K3: Open Frontier Intelligence"
authors: ""
date: "2026/7/27"
arxiv: "https://arxiv.org/abs/2607.24653"
pdf: "papers/kimi-k3-open-frontier-intelligence.pdf"
slug: "kimi-k3-open-frontier-intelligence"
tags: []
---

# Kimi K3: Open Frontier Intelligence

> [!abstract] 摘要（原文）
> We introduce Kimi K3, a 2.8T parameter Mixture-of-Experts model with 104 billion activated parameters, native vision capabilities, and a 1-million-token context window. Kimi K3 is built on Kimi Delta Attention and Attention Residuals, which improve information flow across sequence length and model depth. Together with Stable LatentMoE, which effectively activates 16 of 896 routed experts per token, and refined training and data recipes, these advances yield an approximately 2.5x improvement in overall scaling efficiency over Kimi K2. Post-training highlights reinforcement learning across general, agentic, and coding domains and multiple reasoning-effort levels, enabling compositional generalization and robust long-horizon execution. At 2.8T scale, Kimi K3 is supported by infrastructure advances in multiple areas: algorithm-system co-design for KDA, perfectly balanced expert-parallel training with efficient memory management, million-token agentic RL with persistent rollout and sandbox states, and deployment innovations. Extensive evaluations show that Kimi K3 achieves frontier-level performance across long-horizon coding, agentic, knowledge, reasoning, and vision tasks. While its overall performance still trails the most powerful proprietary models, namely Claude Fable 5 and GPT-5.6 Sol, Kimi K3 consistently outperforms other open and proprietary models evaluated in our suite. We release the full Kimi K3 model weights to facilitate future research and accelerate the broader deployment and adoption of frontier intelligence.

## 元信息
- **发表日期**: 2026/7/27
- **作者**: —
- **arXiv**: https://arxiv.org/abs/2607.24653
- **本地 PDF**: `papers/kimi-k3-open-frontier-intelligence.pdf`
- **页数**: 47

## 图表（原文 caption + 页码）

### Figure 1 (p.1) ⭐深度解读
![[assets/crops/kimi-k3-open-frontier-intelligence-fig01.png]]
*整页渲染: ![[assets/kimi-k3-open-frontier-intelligence-p01.png]]*
> [!quote] caption
> Kimi K3 main results. 1https://huggingface.co/moonshotai/Kimi-K3[cs.CL] 7 Aug 2026

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图1分"Coding"与"General & Visual Agents"两栏共12基准（DeepSWE、Kimi Code Bench 2.0、Terminal-Bench 2.1、ProgramBench、FrontierSWE、SWE-Marathon、GDPval-AA v2 Elo、BrowseComp、AutomationBench、JobBench、CharXiv w/ tool、ZeroBench Pass@5），以横向条形对比Kimi K3与GPT-5.6 Sol、Opus 4.8、Fable 5、GLM-5.2得分，K3以蓝色高亮。

**技术结论：** K3在ProgramBench(77.8)、FrontierSWE(81.4)、SWE-Marathon(42.0)、BrowseComp(91.2)、AutomationBench(30.8)居首；Terminal-Bench(88.3)、Kimi Code Bench(72.9)、CharXiv(91.3)、JobBench(54.3)紧追Fable 5；DeepSWE(67.5)居第4、GDPval-Elo(1686)居中。论证K3在编码与代理任务达开源前沿、与闭源SOTA相当但未全面超越。

**论文作用：** 开篇主结果图，定量锚定K3前沿定位，为后续方法/实验论证提供基准锚点。

### Figure 2 (p.3) ⭐深度解读
![[assets/crops/kimi-k3-open-frontier-intelligence-fig02.png]]
*整页渲染: ![[assets/kimi-k3-open-frontier-intelligence-p03.png]]*
> [!quote] caption
> The Kimi K3 architecture, organized around token, channel, and layer mixing, with a native vision pathway at the input.

> [!tip] 技术解读（多模态）
> 【图文联合解读】图示Kimi K3整体架构：输入经MoonViT-V2+MLP视觉通路→Embedding→堆叠Block，每Block由"3层KDA+1层Gated MLA"组成，每注意力层配Stable LatentMoE FFN，α/w门控贯穿残差。左上图展开LatentMoE：2个Shared Expert与N个Routed Expert由Router聚合；左下图展开KDA：q/k经Conv（q附L2归一化）、v直入，α/β由Linear生成，以Norm与⊗门控融合输出。该图论证"token/channel/layer三维度混合"的核心设计，是Table 2性能对比所依赖的结构基线蓝图。

### Figure 3 (p.5) ⭐深度解读
![[assets/crops/kimi-k3-open-frontier-intelligence-fig03.png]]
*整页渲染: ![[assets/kimi-k3-open-frontier-intelligence-p05.png]]*
> [!quote] caption
> Lower-bounded decay and its effect on chunkwise KDA computation. (a) Kimi Linear uses an unbounded negative-Softplus mapping, whereas Kimi K3 bounds the log-decay with a scaled sigmoid; the curves show A = 0 and gmin = −5. (b) Kimi Linear evaluates each diagonal tile with an explicit position-pair computation, while the bounded range in Kimi K3 allows all causal tiles to use dense Tensor Core matr

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图(a)** 展示对数衰减参数化对比（A=0）：Kimi Linear 用 g = -e^A·Softplus(z)（灰线无下界，z→-∞ 时趋于-∞）；K3 改用 g = g_min·Sigmoid(e^A·z)（红线在 g_min = -5 处饱和）。**图(b)** 展示 chunkwise KDA 对角块差异：Kimi Linear 中对角橙色块须显式位置对计算、非对角蓝色块才用 Tensor Core；K3 因衰减有下界，所有因果块统一为蓝色 Tensor Core 稠密矩阵乘法。

**论证结论**：对衰减施加下界约束，可消除"位置对 vs 稠密"的混合计算模式，统一为 Tensor Core 密集 GEMM，同时改善数值稳定性。

**论文作用**：作为 K3 相对 Kimi Linear 核心架构改进（数值稳定 + 训练效率）的可视化证据，支撑其"chunkwise 加速、长上下文可扩展"的方法级主张，属于方法论章节的关键图示。

### Figure 4 (p.7) ⭐深度解读
![[assets/crops/kimi-k3-open-frontier-intelligence-fig04.png]]
*整页渲染: ![[assets/kimi-k3-open-frontier-intelligence-p07.png]]*
> [!quote] caption
> Gate and up branches of GLU, SwiGLU, and SiTU-GLU, together with their scalar responses, where σ denotes the sigmoid function. Both branches receive the scalar input x, and all curves share the domain x ∈[−10, 100]; the inset magnifies the near-origin region. SiTU-GLU, shown in red with β1 = 4 and β2 = 25, closely follows SwiGLU near the origin and approaches the bound |f(x)| ≤β1β2 = 100 for large

> [!tip] 技术解读（多模态）
> 【图文联合解读】**核心对象**：左表给出 GLU、SwiGLU、SiTU-GLU 三者的 Gate/Up 分支公式（σ、x·σ(x)、β₁tanh(x/β₁)·σ(x) 等）；右图绘制其在 x∈[−10, 100] 上的标量响应曲线，插图放大原点附近。

**关键结论**：SiTU-GLU（红，β₁=4, β₂=25）在原点处紧贴 SwiGLU（绿），保留其类 SwiGLU 的训练动力学；但大 x 时收敛于 |f(x)|≤β₁β₂=100 的有界渐近线，而 SwiGLU 与 GLU 均无界增长。

**论文作用**：以可视化直观论证 SiTU-GLU 同时具备"近原点近似 SwiGLU"与"输出有界"两性质，为后续训练稳定性与消融实验提供几何直觉与设计依据。

### Figure 5 (p.8) ⭐深度解读
![[assets/crops/kimi-k3-open-frontier-intelligence-fig05.png]]
*整页渲染: ![[assets/kimi-k3-open-frontier-intelligence-p08.png]]*
> [!quote] caption
> Illustration of Quantile Balancing with m = 8 tokens, n = 4 routed experts, and k = 1 selected expert per token. (a)

> [!tip] 技术解读（多模态）
> 【图文联合解读】【核心对象】图5以 m=8 token、n=4 routed experts、k=1 为示例，三栏展示路由均衡全流程：(a) 原始 Top-1 路由产生负载 (4,3,1,0)，E₁ 过载、E₄ 空载；(b) Quantile Balancing 阶段按列对 token-专家得分设分位阈值（红色虚线），红星标记每列入选 token；(c) 重路由后每专家恰承接 2 token，负载严格均匀 (2,2,2,2)。

【技术结论】论证分位均衡可将偏斜的 Top-k 分配转化为均匀分配，避免过热专家过拟合、空闲专家欠训练，保障 MoE 专家利用率与训练稳定性。

【论文作用】作为 MoE 负载均衡机制的可视化证据，与辅助偏置损失互补，支撑稀疏激活模型在大规模训练中的基础设施论证。

### Figure 6 (p.9) ⭐深度解读
![[assets/crops/kimi-k3-open-frontier-intelligence-fig06.png]]
*整页渲染: ![[assets/kimi-k3-open-frontier-intelligence-p09.png]]*
> [!quote] caption
> Vision-tower gradient norms in our pre-training ablations. Compared with the SigLIP-initialized MoonViT-3D, the from-scratch MoonViT-V2 maintains lower gradient norms with fewer spikes, indicating more stable optimization. 9

> [!tip] 技术解读（多模态）
> 【图文联合解读】**Figure 6 图文联合解读**

**(1) 核心数据：** (a)展示7k–30k训练步两种视觉塔梯度范数全程曲线；(b)放大14k–16k区间。蓝色MoonViT-3D（SigLIP初始化）全程频繁出现0.4–0.75的尖峰，放大图显示其基线约0.02–0.03、尖峰达0.1–0.15。红色MoonViT-V2（从零训练）基线始终≤0.02，仅约22k步出现一次~0.4的孤立尖峰，其余区段近乎平坦。

**(2) 技术结论：** V2从头训练相比SigLIP初始化方案，梯度范数更低、尖峰显著更少，优化过程明显更稳定——为"放弃强视觉预训练权重、重新设计原生视觉编码器"这一关键决策提供量化稳定性证据。

**(3) 在论文中的作用：** 作为预训练消融（pre-training ablation）的客观度量，与下游任务性能互补，从训练动力学角度背书MoonViT-V2架构选择，强化"原生从头设计优于借用预训练初始化"的整体方法论主张。

### Figure 7 (p.11) ⭐深度解读
![[assets/crops/kimi-k3-open-frontier-intelligence-fig07.png]]
*整页渲染: ![[assets/kimi-k3-open-frontier-intelligence-p11.png]]*
> [!quote] caption
> Fitted scaling-law curves for Kimi K2 and Kimi K3. Kimi K3 achieves 2.5× gain in scaling efficiency over Kimi K2.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图7联合解读**

1. **核心对象与结构**：双对数坐标图，横轴为训练FLOPs（≈5×10¹⁹–2×10²¹），纵轴为Validation Loss。蓝色（K2）与红色（K3）两条拟合直线近似平行，K3整体左移；图中以"2.5×"标注在等Loss水平上K3相对K2的横向FLOPs位移比，数据点（星标）紧贴拟合线。

2. **关键技术结论**：K3在保持幂律scaling形式的同时，仅需K2约40%的算力即可达到相同验证损失，即scaling efficiency提升2.5×，证明K3的架构/训练改进切实转化为计算–性能收益。

3. **在论文中的作用**：作为method链路的关键经验证据，定量支撑"open frontier intelligence"的核心主张——K3并非单纯扩规模，而是以更高效scaling曲线实现前沿能力，呼应全文优化Muon、优化器、合成数据等改进的累积效果。

### Figure 8 (p.13) ⭐深度解读
![[assets/crops/kimi-k3-open-frontier-intelligence-fig08.png]]
*整页渲染: ![[assets/kimi-k3-open-frontier-intelligence-p13.png]]*
> [!quote] caption
> Scores and the average assistant steps across a variety of public and in-house evaluations during RL. By scaling RL FLOPs, tool-call steps scale up consistently, accompanied by a comprehensive improvement in the model’s overall capability.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图8由2×4共8个子图构成，横轴为RL FLOPs（强化学习计算量），纵轴双轴显示：蓝色实线为Score(%)、红色虚线为Avg. steps（平均工具调用步数），覆盖Coding Experience、General Tool Use、Web Development、Agentic Search、Professional Workflows、Office Deliverables、Agentic Chart Understanding与Agentic Visual Puzzles八类评测。随着RL FLOPs自左向右放大，绝大部分子图中两条曲线呈协同上升趋势——例如Professional Workflows与Office Deliverables的分数从约30%爬升至80%以上，Avg. steps同步由低位升至高位；Agentic Visual Puzzles与Coding Experience亦呈近似单调递增的强相关，General Tool Use的Avg. steps增幅显著。仅Web Development与Agentic Search波动较大，但整体仍呈正相关。

**论证结论：** 原文据此说明"RL算力规模化→工具调用链路变长→综合能力全面提升"，建立了"长链工具使用+能力增益"的可扩展关系。

**论文作用：** 作为RL scaling实验的核心证据，支撑"Kimi K2在RL阶段涌现更深层智能体行为"的论点，与Figure 7/9的tool-use统计、benchmark总分构成RL训练链路的完整佐证。

### Figure 9 (p.15) ⭐深度解读
![[assets/crops/kimi-k3-open-frontier-intelligence-fig09.png]]
*整页渲染: ![[assets/kimi-k3-open-frontier-intelligence-p15.png]]*
> [!quote] caption
> Overview of knowledge-graph-guided task synthesis. The hierarchically organized knowledge graph represents concepts at multiple levels, ranging from broad domains to fine-grained concepts. Related nodes are sampled to form a keyword set that guides the retrieval of publicly available source materials. For each synthesis instance, the system selects a task type and uses the retrieved materials to s

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

左侧分层知识图谱：1中心节点辐射7+领域（CS/AI、Coding、Math、Physics、Chemistry、Biomedicine、Humanities等），各领域再分叉约30+细粒度概念节点，呈多层辐射状。右侧三阶段流水线：①联合采样相关节点形成关键词集（如RoPE、GPU kernel）；②据此从互联网抓取公开素材（论文/博客/代码库）；③按实例选择任务类型（Coding/Knowledge/Vision等）合成任务。

原文论证：知识图谱的层级语义结构保证任务在广域学科覆盖与细粒度概念两个尺度上兼具多样性与可控性；关键词→素材→任务链路将开放网络数据自动转化为结构化训练任务，实现规模化数据合成。

论文作用：作为任务合成框架总览图，揭示训练数据如何由知识先验+公开语料自动生成，奠定大规模、多样化、可扩展训练集构建的方法基础。

### Figure 10 (p.17) ⭐深度解读
![[assets/crops/kimi-k3-open-frontier-intelligence-fig10.png]]
*整页渲染: ![[assets/kimi-k3-open-frontier-intelligence-p17.png]]*
> [!quote] caption
> Completion curves on Camera Repair Management System, a black-box system replication task in which the agent reconstructs a hidden 3D-camera repair system as a web application through oracle queries. Completion denotes verifier-assessed task progress. 5

> [!tip] 技术解读（多模态）
> 【图文联合解读】图示四模型在"Camera Repair Management System"黑盒系统复现任务上的完成度曲线（验证器评分，横轴为归一化工具调用进度）。Kimi K3以得分1.000成为唯一达100%完成度的模型，且在约90%–100%区间出现陡峭跃升；Opus 4.8（0.918）与GPT-5.5（0.893）分别止于约92%、89%并在末段趋于平台；Kimi K2.6仅0.560，封顶约56%。论文借此论证：Kimi K3在长程黑盒逆向与复杂Web复现中具备最高的探索—收敛效率，曲线末端跃升表明其在工具调用后期仍能持续突破。该图是支撑"前沿智能体能力"主张的核心实证之一。

### Figure 11 (p.19) ⭐深度解读
![[assets/crops/kimi-k3-open-frontier-intelligence-fig11.png]]
*整页渲染: ![[assets/kimi-k3-open-frontier-intelligence-p19.png]]*
> [!quote] caption
> Computation, communication and offloading overlapped in different PP phases.

> [!tip] 技术解读（多模态）
> 【图文联合解读】图11为PP0/PP1/PP2三阶段时间轴甘特图，含6个微批次（蓝前向/红反向），5条轨道并行跑DataLoader+ViT计算、EP gather param、NCCL与激活Onload/Offload。放大框拆解单阶段：Attn–SE1–MLP–SE2（穿插EP-C/EP-D）–WGrad，前后夹Offload块。

结论：MoE专家通信、跨卡NCCL与激活换页被精确流水线化，并与PP前反向深度重叠，从而掩盖Expert All-to-All与reduce-scatter开销。

作用：作为Kimi K3训练栈（ZeRO-Offload+EP重叠调度）的关键证据，支撑其超大规模MoE高效训练，使计算/通信/换页同步推进而不形成气泡。

### Figure 12 (p.23) ⭐深度解读
![[assets/crops/kimi-k3-open-frontier-intelligence-fig12.png]]
*整页渲染: ![[assets/kimi-k3-open-frontier-intelligence-p23.png]]*
> [!quote] caption
> Fine-grained prefix caching within a physical cache block. A 6144-token physical block contains twelve 512-token hash blocks, with cached MLA blocks shown in blue and empty blocks in light gray. The markers below show the KDA checkpoint status at each hash boundary. An open circle (◦) denotes a boundary without a stored checkpoint, a gray dot (•) denotes a persisted KDA checkpoint, and an orange d

> [!tip] 技术解读（多模态）
> 【图文联合解读】**1) 核心对象与结构：** 1个6144-token物理块划分为12个512-token哈希块；MLA KV行前5块蓝色（已缓存）、后7块浅灰（空）；KDA检查点行在第5块边界B=2560处标橙色命中点，第4块为灰色持久checkpoint，其余位置为开圈（无checkpoint）。

**2) 关键技术结论：** 命中B=2560时，从checkpoint恢复KDA状态、对部分MLA块执行copy-on-write，[0,B)区间零重算即可续prefill——证明512-token粒度的细粒度哈希前缀缓存与KDA状态持久化可协同工作，避免整块重新计算，实现按哈希边界的增量恢复。

**3) 论文作用：** 该图是"细粒度前缀缓存+KDA增量恢复"机制的可视化证据，与相关章节共同支撑系统级增量推理管线设计，论证检查点粒度选择（512-token哈希块）的工程合理性。

### Figure 13 (p.32) ⭐深度解读
![[assets/crops/kimi-k3-open-frontier-intelligence-fig13.png]]
*整页渲染: ![[assets/kimi-k3-open-frontier-intelligence-p32.png]]*
> [!quote] caption
> Score vs. per-task inference cost on Kimi Code Bench 2.0, BrowseComp, GDPval-AA v2, and AA-Briefcase. Kimi K3 is marked with a star.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图13联合解读**

图13含四个子图，对比Kimi K3（★）与GPT-5.6 Sol、Claude Fable 5/Opus 4.8/Sonnet 5/Mythos 5在代码、检索、智能体任务上得分/ELO与单任务成本关系。关键数据：(a) K3约$4达72.5%，成本不到Fable 5（$10.5/77.5%）一半；(b) K3(max)仅~$1即达~91.5%，以约1/27成本超越Opus 4.8 10M token(~88%)；(c)(d) K3 ELO略低于Fable 5（1680/1550 vs 1748/1580），但成本仅其1/3~1/2。该图作为"显著更低成本达前沿智能"主张的核心实证，支撑K3在性能–成本帕累托前沿上优于闭源同级的结论。

### Figure 14 (p.33) ⭐深度解读
![[assets/crops/kimi-k3-open-frontier-intelligence-fig14.png]]
*整页渲染: ![[assets/kimi-k3-open-frontier-intelligence-p33.png]]*
> [!quote] caption
> Case study: GPU kernel optimization on AttnRes. 7

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

该图为 AttnRes GPU kernel 优化任务的案例研究，纵轴为性能得分（0–64.1），横轴为有效工作时间（Active hours，0–22h），以阶梯线追踪四个模型的迭代优化轨迹。

**核心数据**：Kimi K3（红线）增长最快，约第 3 小时起步，第 5 小时已达 ~40%，第 15 小时封顶 ~60（+59.7%）；Claude Fable 5（蓝线）约第 4 小时起跑，第 15 小时达 ~57（+57.1%）；GPT-5.5（绿线）缓慢爬升至 ~30 后长期平台期（+30.8%）；GPT-5.6 Sol（深红线）全程落后，仅在第 20 小时达到 ~17（+17.3%）。

**关键结论**：原文以"前期加速+最终峰值"双重优势论证 Kimi K3 在长周期、迭代式深度优化任务中兼具探索效率与求解质量，显著优于同梯队模型。

**论文作用**：作为 frontier intelligence 的实证切片，支撑"K3 在开放式研究/工程难题上达到人类专家级推理"的整体论断。

### Figure 15 (p.34) ⭐深度解读
![[assets/crops/kimi-k3-open-frontier-intelligence-fig15.png]]
*整页渲染: ![[assets/kimi-k3-open-frontier-intelligence-p34.png]]*
> [!quote] caption
> Case study: GPU compiler development with MiniTriton. (a) CUDA-core and (b) tensor-core rooflines of MiniTriton kernels on an NVIDIA L20 (sm_89) against torch eager, torch.compile, Triton, and cuBLAS baselines (losing points included); (c) training-loss curves of the character-level GPT trained with MiniTriton versus torch eager; (d) two-GPU data-parallel training built on MiniTriton’s own distrib

> [!tip] 技术解读（多模态）
> 【图文联合解读】图15为MiniTriton自研GPU编译器的四项实证：(a)L20 fp32 CUDA-core roofline中matmul 4096³达2048³量级GFLOP/s，逼近cuBLAS 8192³实测峰38.1 TFLOP/s；(b)tf32/bf16张量核roofline，minitriton(红)与cuBLAS曲线几近重合，bf16峰值115.8 TFLOP/s；(c)字符级GPT 100步训练损失曲线与torch eager完全重合；(d)单卡vs DDP×2(L20 NCCL)120步交叉熵差max仅0.0033，final 2.4876/2.4870。论证结论：编译器在多算子多精度下达工业级roofline上限，且端到端收敛与分布式扩展均数值正确。该case study在论文中作为系统层证据，证明前沿智能体具备完整GPU编译器研发能力，而非仅应用层代码生成。

### Figure 16 (p.46) ⭐深度解读
![[assets/crops/kimi-k3-open-frontier-intelligence-fig16.png]]
*整页渲染: ![[assets/kimi-k3-open-frontier-intelligence-p46.png]]*
> [!quote] caption
> Structure of the Kimi K3 chat template. (a) Context layout: global option messages precede the input messages, while one-shot option messages follow them, so that per-request options leave the history KV cache intact; dynamically loaded tools are injected mid-session as input option messages (dashed). (b) Anatomy of an assistant message: the body is organized into think, response, and tools channe

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读（Figure 16，Kimi K3 Chat Template）：**

1) **结构对象**：图分三栏。(a) 上下文布局按"全局选项（tool-declare、thinking-effort）→ 输入消息（system/user/tool/assistant，mid-session 虚线注入 dynamic tool-declare）→ 单次选项（tool-choice、response-format）"三段式排列，前缀为 `[open]think[sep]` / `[open]response[sep]`；(b) assistant 消息体含 think、response、tools 三条独立通道，以 `[end_of_msg]` 收尾；(c) tools 通道按 `call tool="python|search" index=N` 形式承载参数化调用（如 `{"timeout":150}`）。

2) **关键论证**：全局选项前置 + 单次选项后置，保证 per-request 配置不破坏历史 KV cache；mid-session 工具以 input option 形式动态注入；三通道解耦使 thinking、回复、工具调用可独立采样与缓存复用。

3) **论文作用**：该模板是 K3 推理时 thinking-effort、tool-use 与 KV cache 高效复用的结构基础，支撑后续长上下文与 agent 评测链路。

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.11) ⭐深度解读
![[assets/crops/kimi-k3-open-frontier-intelligence-tab01.png]]
> [!quote] caption
> Architectural comparison between Kimi K2 and Kimi K3.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 1 解读**

**核心对象与数据：** 对比 K2/K3 架构参数及 Δ 变化。K3 多维扩容：总参 1.04T→2.78T（↑167%）、激活参 32.6B→104.2B（↑220%）、层数 61→93（↑52%）、路由专家 384→896（↑133%）、每 token 激活专家 8→16（↑100%）、共享专家 1→2、注意力头 64→96（↑50%）；隐藏维 7,168 与词表 160K 持平。K3 新增 Latent MoE（3584，0.5×）、401M ViT（27 层/patch 14/12 头）、混合 KDA–MLA 注意力（69 KDA + 24 MLA）、SiTU-GLU 激活函数，训练上下文 128K→1M（8×）。

**技术结论：** K3 在多维参数规模大幅扩容之上，引入 Latent MoE、混合注意力、原生 ViT 与超长上下文等架构创新，论证"开放前沿智能"源于规模与架构的双重跃迁。

**论文作用：** 作为整篇方法/实验链路的架构基线，定量锚定 Fig.1 主结果对比所依赖的容量上限与结构差异。

### Table 2 (p.27) ⭐深度解读
![[assets/crops/kimi-k3-open-frontier-intelligence-tab02.png]]
> [!quote] caption
> Performance comparison of Kimi K3 against proprietary and open-source models. Bold denotes the best result for each benchmark and underline the second-best. Unless otherwise noted, Kimi K3 results are obtained with reasoning effort set to max and temperature equal to 1 . 0 . For HLE-Full, MMMU-Pro, 

> [!tip] 表格解读（多模态）
> 【图文联合解读】Table 2将Kimi K3（max推理强度）与Claude Fable 5、GPT-5.6 Sol、Opus 4.8、GPT-5.5四个闭源模型及开源GLM-5.2在推理/知识、编码、代理三大类约30项基准上系统对比。**K3在代理类全面领先**：BrowseComp 91.2、DeepSearchQA 95.0、ResearchRubrics 76.2、MCPMark-Verified 94.5、Harvey Lab-AA 94.6、AutomationBench 30.8、SpreadsheetBench 2 34.8、τ³-Banking 33.4等均居首位；**编码**拿下ProgramBench 77.8、SWE-Marathon 42.0；**推理**与GPT-5.6 Sol互有胜负（GPQA 93.5平GPT-5.5，AA-LCR 74.7居首）。该表是论文核心实证，支撑"开源权重模型可达前沿、与最强闭源模型正面竞争"的主张，并凸显K3在长程工具调用与代理任务上的相对优势。

### Table 3 (p.29) ⭐深度解读
![[assets/crops/kimi-k3-open-frontier-intelligence-tab03.png]]
> [!quote] caption
> Results on our in-house benchmarks. Bold denotes the best reported result per benchmark; “-” denotes scores not yet included in this report. Unless otherwise noted, models are evaluated at maximum reasoning effort (GPT-5.5 at xhigh); harness assignments are shown in the Harness column. a 13 fallback

> [!tip] 表格解读（多模态）
> 【图文联合解读】表3对比Kimi K3与Claude Fable 5/Opus 4.8、GPT-5.6 Sol/5.5及开源GLM-5.2在Coding、General Agent、Conversational三类共15项自研基准的得分,各任务附不同harness。关键结论:Kimi K3在Coding Experience(59.9)、CLIF(52.4)、Swarm Bench(76.3)、Deep Research(90.0)等7项夺最佳,逼近或超越闭源SOTA;而通用Agent赛道多由GPT-5.6 Sol领跑(MIRA 52.0、KWV 66.9等),显示K3在长程工具调用类任务上仍有差距。该表作为论文实验收束,用统一评估框架量化证明K3已达开源前沿并具竞争力,同时诚实暴露相对短板。

### Table 4 (p.29) ⭐深度解读
![[assets/crops/kimi-k3-open-frontier-intelligence-tab04.png]]
> [!quote] caption
> Results on the in-house Kimi Webdev Bench: Kimi K3 (max) against Claude Opus 4.8 (max), both run with the Claude Code harness. The comparison is performed under blind expert judging, where experts score each output on code quality, feature completeness, visual fidelity, and interaction experience wi

> [!tip] 表格解读（多模态）
> 【图文联合解读】**注意**：图中所见为多基准综合评测表（含 Coding/Agent/Conversation 三类），与 caption 所述"Webdev Bench 的 Win/Tie/Lose 偏好对比"并不一致；以下按图像实际内容解读：

**1）核心对象与数据**：横向对比 Kimi K3 (max)、Claude Fable 5/Opus 4.8、GPT-5.6 Sol/5.5（Proprietary）与开源 GLM-5.2（Open Weight），覆盖 14 个基准。Kimi K3 关键得分：Code Bench 73.7、Code Exp (Claude Code) **59.9**（领先）、KAET 83.5、CLIF **52.4**（领先）、Swarm **76.3**（领先）、Deep Research **90.0**（领先）、Faithfulness 85.5、Chat All-in-One 85.2。

**2）关键结论**：Kimi K3 在编程、Agent、对话三类任务上与闭源前沿模型互有胜负并多次居首（如 Deep Research、Swarm、CLIF），整体大幅领先开源 GLM-5.2。

**3）实验链路作用**：作为主结果总览表，为论文"开放权重达到前沿智能"的核心论点提供跨域定量证据。

### Table 5 (p.32) ⭐深度解读
![[assets/crops/kimi-k3-open-frontier-intelligence-tab05.png]]
> [!quote] caption
> Headline independent third-party evaluations of Kimi K3 (as of July 23, 2026). Bold denotes the best result per benchmark and underline the second best. Baseline scores are as reported by each source under its own evaluation setup a Text Arena entry is the xhigh variant listed on the leaderboard. b 

> [!tip] 表格解读（多模态）
> 【图文联合解读】**【结构与数据】** Table 5对比Kimi K3与Claude Fable 5、GPT-5.6 Sol、Claude Opus 4.8、GPT-5.5及开源GLM-5.2在5项第三方基准的表现。Kimi K3以1,678 Elo登顶WebDev Arena(#1/99);Vals Index 74.7(#2/39)、Text Arena 1,486(#8/200)均第二;AA Index 57.1、Agent Arena 9.1列第三,五项稳入前三。

**【关键结论】** 论文据此论证:作为开放权重模型,Kimi K3在编码(WebDev)上反超所有闭源对手,综合智能评测达前沿前列,实现"开源前沿智能"。

**【论文作用】** 位于评估章节,串联前文MoE与Quantile Balancing等方法创新,为"Open Frontier Intelligence"主张提供核心实证,证明产出可对标GPT-5与Claude旗舰模型。

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\mathbf{S}_t = \left(\mathbf{I}-\beta_t\bm{k}_t\bm{k}_t^{\top}\right) \operatorname{Diag}(\bm{\alpha}_t)\mathbf{S}_{t-1} + \beta_t\bm{k}_t\bm{v}_t^{\top}, \qquad \tilde{\bm{o}}_t = \mathbf{S}_t^{\top}\bm{q}_t.
$$

$$
\bm{\gamma}_{[t]}^{i\rightarrow j} := \prod_{r=i}^{j}\bm{\alpha}_{[t]}^r, \qquad \bm{\gamma}_{[t]}^r := \bm{\gamma}_{[t]}^{1\rightarrow r}.
$$

$$
\bm{y}_t = \mathbf{W}_o\!\left[ \operatorname{Sigmoid}\!\left(\mathbf{W}_g\bm{x}_t\right) \odot \operatorname{RMSNorm}(\tilde{\bm{o}}_t) \right].
$$

$$
\bm{k}_{i} = \bm{v}_{i} = \begin{cases} \bm{h}_1 & i = 0 \\ f_i(\bm{h}_{i}) & 1 \leq i \leq l-1 \end{cases}
$$

$$
{\alpha_{i \to l}} = \frac{\phi\left(\bm{q}_{l}, \bm{k}_{i}\right)}{\sum_{j=0}^{l-1} \phi\left(\bm{q}_{l}, \bm{k}_{j}\right)}, \qquad \bm{h}_{l} = \sum_{i=0}^{l-1} {\alpha_{i \to l}} \cdot \bm{v}_{i}.
$$

$$
\mathbf{V} = \begin{cases} [\bm{b}_0, \bm{b}_1, \ldots, \bm{b}_{n-1}]^\top & \text{if } i = 1 \text{ (first layer of block } n\text{)} \\ [\bm{b}_0, \bm{b}_1, \ldots, \bm{b}_{n-1}, \bm{b}_n^{i-1}]^\top & \text{if } i \geq 2 \text{ (subsequent layers)} \end{cases}
$$

$$
\operatorname{SiTU\text{-}GLU}(\bm{x}) = \left[\beta_1\tanh\!\left(\frac{\mathbf{W}_g\bm{x}}{\beta_1}\right)\odot\operatorname{Sigmoid}(\mathbf{W}_g\bm{x})\right] \odot \left[\beta_2\tanh\!\left(\frac{\mathbf{W}_u\bm{x}}{\beta_2}\right)\right],
$$

$$
\mathcal{T}_i = \operatorname{argtop}_{k}\!\left(\bm{s}_i+\bm{b}\right), \qquad p_{i,j} = \frac{s_{i,j}}{\sum_{r\in\mathcal{T}_i}s_{i,r}}, \quad j\in\mathcal{T}_i.
$$

$$
\sum_{i=1}^{m}\mathbf{1}\!\left[s_{i,j}+\widehat{b}_j^{(t+1)}>\alpha_i^{(t)}\right],
$$

$$
\mathcal{L}_{\mathrm{LK}} = -\log \sum_{x \in \mathcal{V}} \min\!\left(p(x), q(x)\right),
$$

$$
\begin{aligned} \mathbf{M}_{[i+1]}^{t \leftarrow 1} := \prod_{r \leftarrow 1}^{t}\mathbf{M}_r \in \mathbb{R}^{d_k\times d_k}, \qquad \mathbf{S}_{[i+1]}^{t} & =\widetilde{\mathbf{S}}_{[i+1]}^{t} + \mathbf{M}_{[i+1]}^{t \leftarrow 1}\mathbf{S}_{[i]}^{T_i} \\ & = \widetilde{\mathbf{S}}_{[i+1]}^{t} + \mathbf{M}_{[i+1]}^{t \leftarrow 1}\sum_{j=1}^{i}\Big(\prod_{l \leftarrow j+1}^{i}\mathbf{M}_{[l]}^{T_l \leftarrow 1}\Big)\widetilde{\mathbf{S}}_{[j]}^{T_j}\in \mathbb{R}^{d_k\times d_v}. \end{aligned}
$$

$$
\beta\tanh\!\left(\frac{z}{\beta}\right) = z + O\!\left(\frac{z^3}{\beta^2}\right).
$$

$$
\left\|\operatorname{SiTU\text{-}GLU}(\bm{x})\right\|_{\infty} \leq \beta_1\beta_2 = 100,
$$

$$
\max_{x_{i,j}\in\{0,1\}} \sum_{i,j} x_{i,j}s_{i,j} \qquad \text{s.t.}\qquad \sum_j x_{i,j}=k, \qquad \sum_i x_{i,j}=\frac{mk}{n}.
$$

$$
\max_{x_{i,j}\in[0,1]}\min_{\alpha_i,\beta_j}\; \sum_{i,j} x_{i,j}s_{i,j} - \sum_i \alpha_i\Big(\sum_j x_{i,j} - k\Big) - \sum_j \beta_j\Big(\sum_i x_{i,j} - \tfrac{mk}{n}\Big).
$$

$$
\min_{\alpha_i,\beta_j}\max_{x_{i,j}\in[0,1]}\; \sum_{i,j} x_{i,j}\big(s_{i,j} - \alpha_i - \beta_j\big) + k\sum_i \alpha_i + \frac{mk}{n}\sum_j \beta_j.
$$

$$
\min_{\alpha_i,\beta_j}\; \mathcal{L}(\bm{\alpha},\bm{\beta}) := \sum_{i,j}\max\big(0,\; s_{i,j} - \alpha_i - \beta_j\big) + k\sum_i \alpha_i + \frac{mk}{n}\sum_j \beta_j.
$$

$$
\min_{\alpha}\; k\alpha + \sum_{j}\max\big(0,\; s_{i,j} - \beta_j - \alpha\big).
$$

$$
\alpha_i^* = \operatorname{quantile}_{1-k/n}\big(\bm{s}_i - \bm{\beta}\big).
$$

$$
\beta_j^* = \operatorname{quantile}_{1-k/n}\big(\bm{s}_{:,j} - \bm{\alpha}\big).
$$

## 技术点深读（DEEP）

![[deep/kimi-k3-open-frontier-intelligence]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/kimi-k3-open-frontier-intelligence.txt`（189122 字符）供引用检索。