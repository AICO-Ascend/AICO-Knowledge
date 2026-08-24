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
> 【图文联合解读】图1为多面板水平柱状对比图，Kimi K3以蓝色高亮、Fable 5/Opus 4.8/GPT-5、5.6 Sol/GLM-5.2为基线，覆盖12项Coding与通用/视觉Agent基准。在可见面板中，Kimi K3于FrontierSWE(81.2)、SWE-Marathon(42.0)、AutomationBench(30.8)三项夺魁，对GLM-5.2最大领先近17分；仅ZeroBench w/tool(41.0)略逊于Fable 5(46.0)。该图置于首页，作为全文方法-实验链路的开篇主结果，集中论证Kimi K3在编码与Agent推理上达到开源前沿水平，为后续章节提供核心实证锚点。

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
> 【图文联合解读】**图(b)核心对象**：两个4×4分块矩阵对比KDA分块计算。Kimi Linear：主对角线4个橙色"Position-pair Diagonal"块需显式位置对计算，下三角6格用蓝色Tensor Core；Kimi K3：经log-decay下界化后，全部10个因果块（主对角+下三角）统一为蓝色Tensor Core稠密矩阵乘，白色上三角保留因果掩码。

**论证的技术结论**：log-decay下界化（sigmoid钳至g_min=-5）使对角块不再需要特殊计算路径，所有因果块均可纳入Tensor Core加速，硬件利用率显著提升，复杂度从"对角线特殊+其余稠密"简化为"统一稠密GEMM"。

**论文整体作用**：这是K3相对Kimi Linear的核心工程优化之一，支撑其在大规模长序列训练/推理中的硬件效率，是"前沿智能"得以在KDA架构上落地实现的关键链路。

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
> 【图文联合解读】**图文联合解读：**

该图展示Quantile Balancing路由机制的核心步骤：m=8 token、n=4 routed experts、k=1选一。(a) 标准Top-k产生负载(4,3,1,0)严重倾斜；(b) 图中灰色横杠为各margin $s_{i,j}+b_j-\alpha_i$，红色虚线为新偏置阈值$\widehat{b}_j^{(t+1)}$，置于第(q+1)大margin处，使每列恰q=2个margin越过；(c) 经此重新路由后，t1–t8被均匀分给E1–E4，每专家恰收2 token。

**论证结论：** Quantile Balancing通过对每专家偏置的"分位数截断"，将不均衡Top-k路由强制转化为均匀分配，从根本上抑制过热/饿死专家。

**论文作用：** 作为Kimi K3稀疏MoE路由层关键算法可视化证据，支撑其大规模专家并行训练中负载均衡与训练稳定性的方法论主张。

### Figure 6 (p.9) ⭐深度解读
![[assets/crops/kimi-k3-open-frontier-intelligence-fig06.png]]
*整页渲染: ![[assets/kimi-k3-open-frontier-intelligence-p09.png]]*
> [!quote] caption
> Vision-tower gradient norms in our pre-training ablations. Compared with the SigLIP-initialized MoonViT-3D, the from-scratch MoonViT-V2 maintains lower gradient norms with fewer spikes, indicating more stable optimization. 9

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

该图呈现预训练消融阶段视觉塔梯度范数随训练步（7k–22k+）的完整轨迹，对比MoonViT-3D（蓝，SigLIP初始化）与MoonViT-V2（红，从零训练）。MoonViT-3D多次出现0.5–0.75的高尖峰，尤其集中在14k–15k步处；而MoonViT-V2梯度主体低于0.2，尖峰稀少且小，仅在22k附近出现约0.4的脉冲。

此图论证的核心结论：**从零训练的MoonViT-V2优化更稳定、梯度更可控**，显著优于基于SigLIP初始化的MoonViT-3D方案。

在论文整体方法链路中，它为"弃用外部预训练初始化、改用从零训练视觉编码器"的架构决策提供了直接的训练稳定性实证，是MoonViT-V2最终取代MoonViT-3D成为默认视觉塔的关键支撑证据之一。

### Figure 7 (p.11) ⭐深度解读
![[assets/crops/kimi-k3-open-frontier-intelligence-fig07.png]]
*整页渲染: ![[assets/kimi-k3-open-frontier-intelligence-p11.png]]*
> [!quote] caption
> Fitted scaling-law curves for Kimi K2 and Kimi K3. Kimi K3 achieves 2.5× gain in scaling efficiency over Kimi K2.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

1) **核心对象与结构**：图示为对数–对数坐标系下的两条拟合 scaling-law 曲线（虚线），横轴为训练 FLOPs（10²¹ 刻度可见），纵轴为评估损失。蓝色虚线为 Kimi K2，红色虚线为 Kimi K3，每条曲线上标有星号表示实测数据点。两曲线整体平行下移，K3 在相同 FLOPs 下损失更低，或达到相同损失所需计算量约为 K2 的 1/2.5。

2) **关键结论**：以 2.5× 的横向位移定量证明 K3 在 scaling efficiency 上相较 K2 取得显著增益，即每单位算力可获得更优模型质量，验证了 K3 架构/训练方案的有效性。

3) **论文作用**：该图位于实验论证环节，作为支撑 K3 跨入 "open frontier intelligence" 主张的核心定量证据之一，将抽象的"更强"转化为可测量的计算效率提升，为 K3 资源分配决策与代际跃迁论断提供经验依据。

### Figure 8 (p.13) ⭐深度解读
![[assets/crops/kimi-k3-open-frontier-intelligence-fig08.png]]
*整页渲染: ![[assets/kimi-k3-open-frontier-intelligence-p13.png]]*
> [!quote] caption
> Scores and the average assistant steps across a variety of public and in-house evaluations during RL. By scaling RL FLOPs, tool-call steps scale up consistently, accompanied by a comprehensive improvement in the model’s overall capability.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读（图8）：**

图8为2×2四宫格双轴折线图，覆盖Web Development、Agentic Search、Agentic Chart Understanding、Agentic Visual Puzzles四项评测。横轴为RL FLOPs，蓝实线（左轴）为得分(%)，红虚线（右轴）为平均助手步数。量化趋势：Web Development得分由~10%升至~80%、步数~5→10；Agentic Chart Understanding得分~30%→70%、步数~3→6；Agentic Visual Puzzles得分~40%→80%；Agentic Search得分~10%→60%；四任务步数整体均随FLOPs同步增长。

原文据此论证**"RL FLOPs扩展→工具调用步长与综合能力协同提升"**这一核心scaling结论。该图与Figure 7互补，构成论文"算力驱动Agentic能力与推理深度共增长"主线论断的关键实证，支撑Kimi K3以RL为后训练主要杠杆的方法学定位。

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
> 【图文联合解读】1) 图中4条阶梯曲线比较黑盒“相机维修管理系统”的复现进度：工具调用从50%推进至100%，完成度由验证器评估；终值约为红/橙90、紫82、蓝81、绿52。  
2) 曲线表明，代理借助 oracle 查询可逐层还原隐藏的3D维修系统及Web应用，但过程是阶段性的，代理能力决定完成效率与上限。  
3) 该实验构成“黑盒探测—工具执行—系统复现—验证评测”链路，证明方法可处理开放式长程应用复制。

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
> 【图文联合解读】**图文联合解读：**

**① 核心对象与结构：** 1个6144-token物理块被切分为12个512-token的prefix-hash子块，其中前5块为蓝色（已缓存的MLA块，对应B=2560/512=5），后7块为浅灰色（空块）；下方12个标记对应每个hash边界的KDA checkpoint状态（○=无checkpoint，●=已持久化，橙色●=在B=2560处命中）。

**② 关键结论：** KDA checkpoint稀疏分布且通常与对话轮次边界对齐；新请求到达B=2560时，以copy-on-write方式复用前5个MLA hash块与该处KDA checkpoint，对区间[0, B)实现零重算（zero-recompute）即可直接续写prefill。

**③ 在论文中的作用：** 展示"细粒度prefix caching + 状态checkpoint"的协同机制，是Kimi K3长上下文推理高效prefill恢复与KV复用方案的核心可视化证据。

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

**1) 核心对象与结构**：该图为AttnRes算子GPU kernel优化的纵向case study，横轴为优化耗时（小时，约15–20h区间），纵轴为相对加速比。四条阶梯状轨迹分别对应四个模型的迭代优化过程，×号标记为单次尝试散点，水平虚线表示各自达到的最高性能平台：Kimi K3（红）**+59.7%**、Claude Fable 5（蓝）**+57.1%**、GPT-5.5（绿）**+30.8%**、GPT-5.6 Sol（深红）**+17.3%**。

**2) 关键技术结论**：Kimi K3在约17h即触及性能天花板，最终加速比领先第二名约2.6个百分点、领先GPT系列25–42个百分点；其轨迹爬升更快、平台更早稳定，说明该模型在编译反馈—profiling—改写循环中具备更高效的多轮迭代搜索与"通过"判定能力，而GPT-5.6 Sol虽耗时相近却仅获+17.3%，凸显Kimi K3在底层算子优化任务上显著优于同期前沿闭源模型。

**3) 在论文链路中的作用**：作为Figure 14 case study，它与上游基准评测互补，从"过程性"维度具象化K3的智能边界——不再仅给出最终分数，而是展示模型在长时程、需工具反馈的复杂系统工程任务中的探索效率与上限突破能力，支撑"开放前沿智能"（open frontier intelligence）这一核心论断。

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

### Table 2 (p.27) ⭐深度解读
![[assets/crops/kimi-k3-open-frontier-intelligence-tab02.png]]
> [!quote] caption
> Performance comparison of Kimi K3 against proprietary and open-source models. Bold denotes the best result for each benchmark and underline the second-best. Unless otherwise noted, Kimi K3 results are obtained with reasoning effort set to max and temperature equal to 1 . 0 . For HLE-Full, MMMU-Pro, 

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读**

该表分三大类共30余项基准（推理知识4项、编码8项、Agentic约20项），横向对比Kimi K3（max）与其余五个模型（Claude Fable 5、GPT-5.6 Sol、Claude Opus 4.8、GPT-5.5及开源GLM-5.2），HLE-Full等以"无工具/有工具"双数值呈现。

**关键结论**：Kimi K3在Agentic类全面领跑，BrowseComp 91.2、DeepSearchQA 95.0、MCPMark 94.5、Harvey Lab-AA 94.6等均为最佳；编码侧SWE-Marathon 42.0、ProgramBench 77.8居首；推理侧AA-LCR 74.7第一，但GPQA（93.5，次优）、HLE-Full w/ tools（56.0）仍弱于GPT-5.6 Sol（94.1/63.0）。这表明Kimi K3在开放权重条件下已对齐闭源前沿，尤其在长程Agent与工具使用上突破明显，纯知识推理仍是与GPT系列的差距所在。

**论文作用**：Table 2是方法链路终点——验证token/channel/layer混合架构（图2）配合原生视觉通路后，模型在真实工作流基准上达到前沿，是主张"开放权重对标闭源"的核心证据。

### Table 3 (p.29) ⭐深度解读
![[assets/crops/kimi-k3-open-frontier-intelligence-tab03.png]]
> [!quote] caption
> Results on our in-house benchmarks. Bold denotes the best reported result per benchmark; “-” denotes scores not yet included in this report. Unless otherwise noted, models are evaluated at maximum reasoning effort (GPT-5.5 at xhigh); harness assignments are shown in the Harness column. a 13 fallback

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

1) **结构与核心数据**：Table 3 将Kimi K3在三类自建基准（Coding/General Agent/Conversational）上与Claude Fable 5、GPT-5.6 Sol、Claude Opus 4.8、GPT-5.5及开源GLM-5.2做量化对照。Kimi K3在Coding Experience(59.9)、CLIF(52.4)、Swarm(76.3)、Deep Research(90.0)四项加粗最优；GPT-5.6 Sol横扫8项Agent基准（如KAET 85.4、Online 84.0、DECK 74.7）；GPT-5.5在Faithfulness 86.5领先；Claude Fable 5在MIRA 72.9、Chat All-in-One 88.0占优。

2) **关键结论**：Kimi K3以开源权重身份全面逼近顶级闭源模型，并在深度研究类任务实现SOTA；多harness交叉（Claude Code/Kimi Code/Codex等）验证方法稳健。

3) **论文作用**：与公开榜单表互补，作为"K3达到开源前沿智能"核心叙事的收口实证。

### Table 4 (p.29) ⭐深度解读
![[assets/crops/kimi-k3-open-frontier-intelligence-tab04.png]]
> [!quote] caption
> Results on the in-house Kimi Webdev Bench: Kimi K3 (max) against Claude Opus 4.8 (max), both run with the Claude Code harness. The comparison is performed under blind expert judging, where experts score each output on code quality, feature completeness, visual fidelity, and interaction experience wi

> [!tip] 表格解读（多模态）
> 【图文联合解读】**注**：表标题描述的是 Kimi K3 vs Claude Opus 4.8 在 Webdev Bench 上的对比，但图片实际展示的是跨 17 项基准的全面对比表，与 caption 不完全一致；引用段落亦为 Figure 4 内容（非本表）。以下按图片实际内容解读。

**1) 结构与数据**：表格分 Coding Experience（Kimi Code Bench 2.0、Coding Experience）、General Agent Experience（24/7 ClawBench 2.0、MIRA、KAET、CLIF、Agentic Vision、Swarm、Online、Deep Research、Finance、KWV、DECK、Agent Behavior，共 12 项）、Conversational Experience（Faithfulness、Chat All-in-One）三类，共 17 个基准；列含 Harness 与 6 个模型（Kimi K3、Claude Fable 5、GPT-5.6 Sol、Claude Opus 4.8、GPT-5.5、GLM-5.2）。Kimi K3 在 Coding Experience(Claude Code) **59.9**（最高）、CLIF **52.4**、Swarm **76.3**、Deep Research **90.0** 上领先；KAET 85.4、Agent Vision 82.9 等由 GPT-5.6 Sol 居首。

**2) 论证结论**：体现 K3 在编码与通用 Agent 任务上具备前沿竞争力，多项 harness 下达到 SOTA 或并列。

**3) 在论文中的作用**：作为综合能力评测总表，支撑"开放前沿智能"的全栈定位结论。

### Table 5 (p.32) ⭐深度解读
![[assets/crops/kimi-k3-open-frontier-intelligence-tab05.png]]
> [!quote] caption
> Headline independent third-party evaluations of Kimi K3 (as of July 23, 2026). Bold denotes the best result per benchmark and underline the second best. Baseline scores are as reported by each source under its own evaluation setup a Text Arena entry is the xhigh variant listed on the leaderboard. b 

> [!tip] 表格解读（多模态）
> 【图文联合解读】**注：** 引用段落实为 Figure 5（Quantile Balancing 示意图）caption，与 Table 5 内容不对应，故以下解读严格基于表格本身。

**Table 5 图文联合解读：**

Table 5 给出 Kimi K3 截至 2026.7.23 在 6 项独立第三方基准上与 5 个模型（Claude Fable 5、GPT-5.6 Sol、Claude Opus 4.8、GPT-5.5、GLM-5.2；前 4 为闭源，GLM-5.2 为开源权重）的横向对比。量化结果：Artificial Analysis v4.1 = 57.1（#4/580）；Vals Index = 74.7（#2/39，次席）；WebDev Arena = 1,678 Elo（#1/99，榜首）；Text Arena = 1,486（#8/200，次席）；Agent Arena = 9.1（#4/37）。Claude Fable 5 在 5 项中 4 项夺魁，K3 主观 Arena 表现尤为突出。

**关键结论：** K3 作为 Open Weight 类模型，在人类偏好类榜单已追平甚至超越顶级闭源，整体逼近闭源前沿，从而实证"开源前沿智能"的论文核心主张。

**论文作用：** 作为模型最终对外公布的第三方能力背书，与 Figure 5 的 Quantile Balancing 等训练/架构技术创新章节前后呼应——"方法创新 + 独立评测"共同构成论文"open frontier intelligence"主张的完整证据链。

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