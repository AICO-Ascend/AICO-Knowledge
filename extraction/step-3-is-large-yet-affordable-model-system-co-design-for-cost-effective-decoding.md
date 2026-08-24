---
paper_num: "42"
title: "Step-3 is Large yet Affordable: Model-system Co-design for Cost-effective Decoding"
authors: "Model-system Co-design for Cost-effective Decoding StepFun Inc."
date: "2026/1/4"
arxiv: "https://arxiv.org/abs/2507.19427"
pdf: "papers/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding.pdf"
slug: "step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding"
tags: []
---

# Step-3 is Large yet Affordable: Model-system Co-design for Cost-effective Decoding

> [!abstract] 摘要（原文）
> 1\. 🚀 Step-3 是一种 321B VLM，通过以成本效益为目标的硬件感知模型-系统协同设计，显著优化了大型语言模型的解码效率。 2. 💡 其核心创新包括 Multi-Matrix Factorization Attention (MFA) 机制，大幅减少 KV cache 和计算量，以及 Attention-FFN Disaggregation (AFD) 系统，解耦 Attention 和 FFN 层以优化效率。 3. 💰 Step-3 在理论解码成本上显著优于 DeepSeek-V3 和 Qwen3 MoE 等模型，并在 Hopper GPUs 上实现了高达 4,039 tokens per second per GPU 的吞吐量，设定了 LLM 解码的新 Pareto frontier。

## 元信息
- **发表日期**: 2026/1/4
- **作者**: Model-system Co-design for Cost-effective Decoding StepFun Inc.
- **arXiv**: https://arxiv.org/abs/2507.19427
- **本地 PDF**: `papers/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding.pdf`
- **页数**: 18

## 图表（原文 caption + 页码）

### Figure 1 (p.1) ⭐深度解读
![[assets/crops/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-fig01.png]]
*整页渲染: ![[assets/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-p01.png]]*
> [!quote] caption
> The Pareto frontier of recent models regarding acti- vated parameters and decoding costs. The darker area is GQA models’ Pareto frontier. Note: Step-3 also has the highest attention effective rank [7], the same as DSv3 and doubling some other models like Qwen3 MoE 235B and Kimi K2. expensive per token (because of low MFU) compared with training and prefill. 2) For reasoning models, longer thinking

> [!tip] 技术解读（多模态）
> 【图文联合解读】图1为散点图：X轴=8K上下文理论解码成本(0.05–0.10 USD)，Y轴=激活参数(0–50B)。Step-3以红星标于≈(0.055, 38B)，位居Pareto前沿最左下；对照点为DSv3≈(0.068,37)、Kimi K2(0.067,32)、Qwen3 MoE(0.062,22)、Pangu Pro(0.058,17)、Llama4(0.068,17)、ERNIE4.5(0.085,47)、MM M1(0.095,46)；深灰阴影区为GQA模型前沿。

原文论证：Step-3以最低解码成本实现≈38B激活参数，与DSv3量级相当却显著更便宜；其attention effective rank与DSv3持平，约为Qwen3 MoE 235B与Kimi K2的两倍，证"大而便宜"。

作用：开篇将"解码MFU低、长上下文昂贵"痛点可视化，奠定全文动机，引出AFD解耦与Multi-Matrix Factorization Attention两大核心创新。

### Figure 2 (p.6) ⭐深度解读
![[assets/crops/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-fig02.png]]
*整页渲染: ![[assets/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-p06.png]]*
> [!quote] caption
> With all the results shown, we make the following observations:

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图/表联合解读（Table 6，即文中 Figure 2 类解码成本图）**

**① 核心对象与数据**：双子图横轴为5种部署配置（H800、H20、A800、910B、AFD），纵轴为每百万token解码成本（USD），对比4模型在8K与32K上下文下的表现。8K下Qwen3 32B在H800高达约$0.195，Step-3在AFD仅约$0.055；32K下Qwen3 32B@H800飙至$0.73，而Step-3 AFD仅$0.135，且各硬件下Step-3均居最低。

**② 原文论证结论**：Step-3激活参数最多（38B）却全面成本最低，验证"大而实惠"；AFD通过为attention与FFN分别选用最优硬件（如H800跑attention、H20跑FFN）实现全局最优配置，进一步压低成本。

**③ 论文作用**：与Table 2的理论算力/访存量分析互补，以美元实证成本为系统-模型协同设计的经济可行性提供关键支撑，贯穿"模型×硬件×推理范式"联合优化主线。

### Figure 3 (p.6) ⭐深度解读
![[assets/crops/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-fig03.png]]
*整页渲染: ![[assets/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-p06.png]]*
> [!quote] caption
> Second, the time spent on each layer will be largely unbal- anced – when running with long context, the full GQA layers consume much more time than the linear attention layers. This may not be a problem for single-node inference deployment, 6

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图3 图文联合解读**

1. **核心对象与数据**：左图对比三种混合线性注意力模型在8K/32K/128K上下文下的KV cache大小（GB），Step-3从~0.3 GB线性增长至~4.1 GB，而Llama 4 M与MM M1在128K时分别达~7.2 GB与~6.0 GB。右图为H800上单token解码理论成本（USD），Step-3在128K时仅~0.70 USD，约为Llama 4 M（~1.13）的62%、MM M1（~1.02）的69%。

2. **关键结论**：Step-3凭借更激进的线性注意力层比例与更小的KV预算，在长上下文场景下KV占用与解码成本均显著低于MiniMax M1和Llama 4 Maverick，与Table 3（32K下每token算访开销）相互印证。

4. **论文作用**：作为"大而便宜"核心论点（affordable）的关键成本证据，量化支撑模型–系统协同设计在解码侧的经济性收益。

### Figure 4 (p.8) ⭐深度解读
![[assets/crops/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-fig04.png]]
*整页渲染: ![[assets/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-p08.png]]*
> [!quote] caption
> Step-3 and Pangu Pro MoE have very different trends of decoding cost and training cost.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图4解读**

**① 核心对象与数据**：横轴为910B加速器上的三种场景，纵轴为单token成本（USD）。Pangu MoE（红色斜线）三场景依次为0.114 / 0.395 / 0.076 USD；Step-3（青色实心）依次为0.078 / 0.168 / 0.213 USD。

**② 关键结论**：两条曲线趋势完全相反——Step-3在解码场景全面更便宜（8K省约32%，32K省约57%），但训练反而贵约2.8倍；序列越长，Step-3的解码成本优势越显著。说明Step-3把成本预算从训练侧前移到解码侧。

**③ 论文作用**：以Pangu MoE为对照基线，定量验证Step-3"模型-系统协同设计"的核心理念——牺牲训练经济性以换取大规模MoE在长上下文解码时的可负担性，从而支撑全文"large yet affordable"的论证主线。

### Figure 5 (p.8) ⭐深度解读
![[assets/crops/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-fig05.png]]
*整页渲染: ![[assets/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-p08.png]]*
> [!quote] caption
> The compute and memory access of different atten- tion designs during decoding, including DSv3’s MLA, Qwen3

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图5联合解读**

图示三种注意力设计在8K→32K解码下的算术强度轨迹，并叠绘H800/910B/A800/H20四类硬件roofline：
- **DSv3-MLA**：强度≈512（~1.1 GB / 590 GFLOPs），沿H800 ridge，**计算主导**；
- **Qwen3-GQA**：强度≈32（~3.1 GB / 100 GFLOPs），贴近H20，**访存主导**；
- **Step-3-MFA**（红星）：强度≈128（~1.0 GB / 130 GFLOPs），**精准落在910B(≈175)与A800(≈156) roofline的ridge交汇点**。

论文以此量化论证"硬件-算法协同"的核心结论：MFA相较DSv3 MLA**计算量降至约1/4**，相较Qwen3 GQA**访存量降至约1/3**，且在910B/昇腾等国产硬件上同样命中sweet spot。该图是Step-3"低成本大模型"系统级设计主张的**关键定量证据**，支撑全文硬件无关可部署的论证。

### Figure 6 (p.11) ⭐深度解读
![[assets/crops/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-fig06.png]]
*整页渲染: ![[assets/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-p11.png]]*
> [!quote] caption
> Module disaggregation in AFD architecture. FFN can be deployed in TP-only, EP-only, or a hybrid TP+EP way, depending on hardware and model architecture. start to be concerned about other issues like expert imbalance, stability, etc.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**1) 图示内容**：展示AFD架构的Attention与FFN模块解耦。左侧**Attention Instance**（Norm→Attn→Norm，含残差⊕）以**fp8**精度传给右侧**FFN Instance**（Router→TP gather/EP scatter→Expert Compute→TP scatter/EP gather→Expert Combine，含Top-k打分），FFN处理后以**bf16**返回下一层。FFN模块可按TP-only、EP-only或TP+EP混合三种方式部署。

**2) 论证结论**：Attention/FFN解耦后，FFN并行策略可依据硬件与模型灵活选择；借助fp8跨实例通信，仅需4×200Gbps或8×400Gbps等较弱互联即可满足带宽。

**3) 文中作用**：与L20算例配合，证明弱硬件在**272μs/层（16.6ms÷61层）**延迟预算内仍可跑通AFD三/四阶段流水线，从而支撑Table 6中Step-3相对其他MoE/稠密模型实现更低解码成本（USD）的核心结论。

### Figure 7 (p.12) ⭐深度解读
![[assets/crops/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-fig07.png]]
*整页渲染: ![[assets/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-p12.png]]*
> [!quote] caption
> Communication topology and the multi-stages pipeline of the AFD architecture.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

**1) 核心对象与结构：** 图左侧展示AFD（Attention-Feedforward Disaggregation）通信拓扑——FFN实例（8卡）与Attention实例（8卡）通过Direct RDMA逐卡点对点直连，无参数服务器中转。右侧展示多阶段流水线：沿时间轴，每个请求（Layer0的D1/D2/D3与Layer1的D1'/D2'/D3'）依次经历FFN层→F→A传输（bf16）→Attention层→A→F传输（fp8）→下一FFN层，多请求交错实现计算—通信重叠。

**2) 关键结论：** 拆分Attention与FFN为独立实例后，配合非对称精度传输（去程bf16、回程fp8以省带宽）和多请求流水线，可在保证低延迟的同时提升吞吐，传输路径不阻塞各请求的处理。

**3) 论文中的作用：** 作为AFD系统级co-design的核心架构证据，与Table 7（不同硬件平台达成高MFU所需的MoE最低稀疏度）共同支撑"大模型仍可低成本解码"这一总体主张。

### Figure 8 (p.13) ⭐深度解读
![[assets/crops/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-fig08.png]]
*整页渲染: ![[assets/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-p13.png]]*
> [!quote] caption
> StepMesh communication workflow tailored for AFD.

> [!tip] 技术解读（多模态）
> 【图文联合解读】# Figure 8 图文联合解读

**1) 核心对象与结构**

图示 AFD 架构下 StepMesh 的通信流程，分左右两大模块：
- **左侧 Attention Instances**：CPU 含 NetRecv Thread（Recv Tensors→RDMA PollCQ）、NetSend Thread（Kernel Sync→RDMA PostSend）、Main Thread（Wait 上一层→Launch Attention→PushPull 下一层）；GPU 含 Activation Tensors → Attention Kernel → Token Tensors。
- **右侧 FFN Instances**：结构对称但方向相反，GPU 接收 Token Tensors 经 FFN Kernel 输出 Activation Tensors；CPU Main Thread 执行 GetBatch→Launch FFN→Respond。
- 两侧通过底层 **RDMA NIC** 直连，形成跨节点的张量交换闭环。

**2) 关键技术结论**

该图论证了 AFD 三线程流水（接收/发送/计算）可隐藏 RDMA 延迟：Attention 实例的 PushPull 与 FFN 实例的 GetBatch 在 GPU kernel 异步执行时并行进行跨节点张量搬运，实现计算与通信重叠，从而保证解码吞吐满足 SLA。

**3) 在论文中的作用**

作为 StepMesh 的通信实现基础，为 Table 8 中与 DSv3 在 20 tokens/s 解码 SLA 下的 TGS 性能对比提供机制支撑，证明注意力–FFN 解耦 + 异步 RDMA 流水能以更少 GPU 达成成本可控的高吞吐解码。

### Figure 9 (p.13) ⭐深度解读
![[assets/crops/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-fig09.png]]
*整页渲染: ![[assets/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-p13.png]]*
> [!quote] caption
> StepMesh framework for multiple accelerators. AF-

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图9展示StepMesh框架的三层分层架构：(1) 顶层双API——AFTensorWorker（Wait/PushPull，对应Attention实例）与AFTensorServer（GetBatch/Respond，对应FFN实例）；(2) 中间StepMesh Core，基于NetSend/NetRecv线程统一通信；(3) 底层双抽象——Network API（RDMATransport/RDMA NIC）与Accelerator API（CPUBackend/GPUBackend/xPUBackend）。

**技术结论**：通过Attention/FFN解耦API设计＋统一RDMA传输＋异构后端抽象，证明StepMesh可在多类型加速器（CPU/GPU/xPU）上以低开销方式协同工作，支撑MoE双分支流水。

**论文作用**：作为系统级协同设计的"通信骨架"，衔接算法层（AF注意力/MFA）与硬件层（异构集群），是实现"大模型、低成本解码"的核心中间件设计证据。

## 表格（裁剪图 + caption，可直接插入报告）

### Table 2 (p.5) ⭐深度解读
![[assets/crops/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-tab02.png]]
> [!quote] caption
> Theoretical computation and memory access per decoding token at 8K context length.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

**1）核心对象与结构**：表格对比 9 个模型（DSv3、Kimi K2、Qwen3 MoE、Qwen3 32B、Llama 4 M、MM M1、ERNIE 4.5、Pangu Pro、Step-3）在 8K 上下文下每解码 token 的 4 项理论开销：KV/State 内存访问（bytes）、Attention FLOPs（不含 Linear）、Attention 前后 Linear FLOPs、FFN FLOPs。

**2）关键结论**：Step-3 的 KV 内存访问仅 2.56×10⁸ bytes，为全表最低，显著低于稠密模型（Qwen3 32B：1.07×10⁹、Llama 4 M：1.01×10⁹）及 DSv3、Kimi K2（均 2.88×10⁸）；Attention FLOPs（3.27×10¹⁰）远低于 DSv3（1.47×10¹¹）与 Kimi K2（7.37×10¹⁰）；FFN 开销居中。这证明 Step-3 在 memory-bound 的解码阶段成本最优。

**3）作用**：为论文"大而经济"的系统协同设计主张提供量化依据，支撑其架构选择（低 KV 缓存）的成本论证，是解码效率评估的理论基线。

### Table 3 (p.5) ⭐深度解读
![[assets/crops/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-tab03.png]]
> [!quote] caption
> Theoretical computation and memory access per decoding token at 32K context length.

> [!tip] 表格解读（多模态）
> 【图文联合解读】表3列出9个主流模型在32K上下文、每token解码时的理论开销，分四列：KV/State访存、注意力FLOPs（不含线性层）、线性层FLOPs、FFN FLOPs。关键数据：Step-3的KV/State访存仅1.02×10⁹ bytes，为全表最低（DSv3=1.15×10⁹、Qwen3 32B高达4.29×10⁹）；其注意力FLOPs为1.31×10¹¹，仅为DSv3（5.89×10¹¹）的约1/4，与Kimi K2同量级；线性层与FFN FLOPs分别为2.07×10¹⁰与5.33×10¹⁰，计算分布最均衡。

此表用于支撑论文"大而可负担"核心论点：通过模型–系统协同设计（低秩KV压缩+线性注意力），Step-3长上下文解码访存最小、计算最均衡，单token成本最低。它是从动机分析过渡到host–device分离、跨层流水线等硬件协同优化章节的关键量化桥梁。

### Table 4 (p.6) ⭐深度解读
![[assets/crops/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-tab04.png]]
> [!quote] caption
> Comparison of accelerator specifications. *We do not have publicly available 910B pricing. We estimate its price proportionally based on its FLOPs and A800’s. As far as we know, there are multiple versions of 910B. We show the weakest and (presumably) most affordable one that we know.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 4 解读**

1）**对象与数据**：对比 4 款推理加速卡——NVIDIA H800（$2/h，FP8=1.98×10¹⁵，roofline=591）、H20（$0.8/h，FP8=2.96×10¹⁴，roofline=74）、A800（$0.75/h，FP16=3.12×10¹⁴，roofline=156）、昇腾 910B（$0.67/h*，BF16=2.80×10¹⁴，roofline=175，*按 FLOPs 比 A800 估算）。

2）**关键结论**：H800 单价最贵但 roofline 远高于国产卡；910B 性价比最高但 FP8 不支持、roofline 仅 H800 的 30%。H20 roofline 仅 74，推理时易被带宽瓶颈，凸显卡型差异。

3）**论文作用**：作为解码成本建模的硬件输入，支撑"系统-模型协同设计"论点——Step-3 通过稀疏架构等设计补偿低 roofline 硬件的劣势，从而在廉价卡上实现 H800 级 cost-effective decoding。

### Table 5 (p.6) ⭐深度解读
![[assets/crops/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-tab05.png]]
> [!quote] caption
> The unit cost of different accelerators assuming full utilization for the whole month. For FLOP costs, we consider FP8 for H800 and H20, BF16/FP16 for A800 and 910B.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

1) **表格内容**：表5对比了4款加速器（H800、H20、A800、910B）在满月利用率下的"每FLOP成本"与"每字节内存访问成本"。H800算力最便宜（2.80×10⁻¹⁹），但访存最贵（1.66×10⁻¹⁶）；H20算力最贵（7.51×10⁻¹⁹），却拥有最低访存成本（5.56×10⁻¹⁷）；A800与910B算力成本接近（≈6.7×10⁻¹⁹），访存成本A800略低（1.04 vs 1.16×10⁻¹⁶）。

2) **关键结论**：解码为访存密集型任务，访存成本主导总开销，因此H20在解码场景下相比H800具备显著的成本优势，这为论文选择H20作为目标硬件提供了量化依据。

3) **论文作用**：该表为"大而经济"的系统设计提供了硬件成本基线，是后续注意力优化、MoE路由与解码策略优化的经济性度量锚点。

### Table 6 (p.7) ⭐深度解读
![[assets/crops/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-tab06.png]]
> [!quote] caption
> Theoretical decoding cost analysis for each model on each hardware, in USD. As a reminder, these models have different number of activated parameters: DSv3 37B, Qwen3 MoE 22B, Qwen3 32B, MM M1 46B, ERNIE 4.5 47B, Pangu Pro MoE 16.5B and Step-3 38B.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 6 图文联合解读：**

该表以双柱状图对比 4 个模型（DSv3 37B、Qwen3 MoE 22B、Qwen3 32B、Step-3 38B）在 H800、H20、A800、910B、AFD 五种硬件上、8K 与 32K 上下文下的理论解码成本（USD）。量化读数：8K 下 H800 上 Qwen3 32B 最贵约 0.196 USD，AFD 上 Step-3 最便宜约 0.056 USD；32K 下 H800 上 Qwen3 32B 飙至约 0.735 USD，而 AFD 上 Step-3 仍仅约 0.130 USD。原文借此论证：**Step-3 配合 AFD 硬件在所有平台、所有上下文长度下均取得最低解码成本**，且长序列优势进一步放大。

该表在论文中起到核心实证作用——以可量化的美元成本，将"模型–系统协同设计"（多矩阵乘法+AFD 分离架构）的"affordable"主张落地，为前文架构设计与后文推理部署评估提供经济性佐证。

### Table 7 (p.10) ⭐深度解读
![[assets/crops/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-tab07.png]]
> [!quote] caption
> Minimum MoE sparsity for different hardware plat- forms to achieve good MFU, where H = 7168, L = 61.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 7 图文联合解读**

1) **表内容**：在 H=7168、L=61 参数下，给出四款加速器实现良好 MFU 所需的 MoE 最低稀疏度 S——H800=0.058、H20=0.007、A800=0.031、910B=0.034；其中 H800/H20 配 400Gbps×8 NIC，A800/910B 配 200Gbps×8 NIC。

2) **关键结论**：由公式 S≥(H×FLOPs×L)/(Net×Bandwidth×11.1ms) 可知，相同带宽下 FLOPs 越低所需 S 越小（H20 因低精度 FLOPs 低，S 仅 0.007）；带宽减半时 S 几乎翻倍（A800 0.031、910B 0.034 vs H800 0.058），印证带宽与算力共同决定 MoE 激活比的下限。

3) **论文作用**：作为 Step-3 软硬协同设计的量化验证，为不同硬件下选择合适的 MoE 稀疏度（专家激活比例）提供理论门槛，支撑其"大规模但低成本"解码的部署决策。

### Table 8 (p.14) ⭐深度解读
![[assets/crops/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-tab08.png]]
> [!quote] caption
> Performance comparison with reported number of DSv3 under 20 tokens/s decoding SLA. TGS: Tokens/GPU/s.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 8 图文联合解读：**

**1) 核心对象与数据：** 在 20 tokens/s 解码 SLA 下，对比 DSv3 与 Step-3 的 TGS（Tokens/GPU/s）。DSv3-blog（144 GPU）TGS=1850，DSv3-profile（128 GPU）TGS=2324；Step-3 三档配置：BF16+3A2F（40 GPU）TGS=3321，FP8+2A2F（32 GPU）TGS=4039，FP8+4A2F 长上下文 8192（48 GPU）TGS=2643。

**2) 关键结论：** 同等 SLA 下，Step-3（FP8, 32 GPU）以 DSv3 四分之一 GPU 数实现 1.74× 的 TGS（4039 vs 2324）；即使长上下文 8192 配置也用更少 GPU 超过 DSv3-blog，直接验证 FP8 注意力与 AFD 部署带来的解码性价比优势。

**3) 在论文中的作用：** 作为 AFD 解码方案的核心定量证据，与 Figure 8 的 StepMesh 通信流图呼应，共同支撑"大而经济"的系统级主张——少卡、高吞吐、低成本。

### Table 9 (p.14) ⭐深度解读
![[assets/crops/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-tab09.png]]
> [!quote] caption
> Performance comparison of MFA/MLA/GQA. For MLA, we use FlashMLA which does not have official SM80 implementation, so its A800 number is not tested. We use FA3 (SM90) and FA2 (SM80) for MFA/GQA. Here the attention layer includes the linear projection before and after the core attention op. Each exper

> [!tip] 表格解读（多模态）
> 【图文联合解读】表9在4卡、batch 256、8k/32k上下文下比较3种注意力（含前后投影）的层延迟（μs）。H800/H20/A800上，8k/32k：MFA-Step3 281/438/531、791/1452/1484；MLA-DSv3 372/1252/未测、1125/4817/未测；GQA-Qwen3 382/812/791、1391/3042/3010。MFA在已测平台均最快；32k H800较GQA快43%，H20较MLA快70%，支撑长上下文低延迟、低成本解码。

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\max(FLOP_{Attn}U_{FLOP}, Byte_{KV}U_{byte}) + FLOP_{Linear}U_{FLOP}
$$

$$
2 \times N_{\text{token}} \times W_{\text{FFN}}
$$

$$
2 \times B_{\text{dense}} \ge \frac{\text{FLOPs}}{\text{Bandwidth}}
$$

$$
B_{\text{MoE}} = \frac{B_{\text{dense}}}{S}
$$

$$
B_{\text{MoE}} \ge \frac{\text{FLOPs}}{2 \times S \times \text{Bandwidth}}
$$

$$
3 \times H \times B_{\text{MoE}}
$$

$$
\frac{3 \times H \times B_{\text{MoE}}}{\text{Net}} \le \frac{16.6\text{ms}}{L}
$$

$$
\frac{H \times \text{FLOPs} \times L}{\text{Net} \times S \times \text{Bandwidth}} \le \frac{16.6\text{ms} \times 2}{3} = 11.1\text{ms}
$$

$$
S \ge \frac{H \times \text{FLOPs} \times L}{\text{Net} \times \text{Bandwidth} \times 11.1\text{ms}}
$$

## 技术点深读（DEEP）

![[deep/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding.txt`（78380 字符）供引用检索。