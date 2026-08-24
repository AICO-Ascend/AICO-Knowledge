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
> 【图文联合解读】**图文联合解读：**

图1为二维散点图，横轴为8K上下文下的理论解码成本（0.05–0.10 USD），纵轴为激活参数量（0–50B）。Step-3以红星标于约(0.056 USD, 38B)，处于同激活参数规模下解码成本最低的位置；DSv3约(0.069, 37B)、Kimi K2约(0.066, 32B)均在其右上方，灰色阴影区域为GQA模型的Pareto前沿。原文借此论证：解码阶段因MFU低、推理模型thinking长，导致每token成本居高，Step-3通过系统协同设计打破了"高激活参数⇔高成本"的传统权衡，实现"大而省"。该图作为全文动机图，将"高激活参数×低解码成本"确立为Step-3的核心设计目标，为后续架构与推理系统共设计奠定论证基础。

### Figure 2 (p.6) ⭐深度解读
![[assets/crops/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-fig02.png]]
*整页渲染: ![[assets/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-p06.png]]*
> [!quote] caption
> With all the results shown, we make the following observations:

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图2以双柱状图对比Step-3、DSv3、Qwen3 MoE、Qwen3 32B在H800、H20、A800、910B、AFD五种部署方案下的**每百万token理论解码成本**，分别对应8K（左）与32K（右）上下文。8K下Step-3成本约0.055–0.080，32K下AFD方案降至约0.13，**均显著低于Qwen3 32B（8K约0.083–0.197，32K约0.28–0.73）和DSv3**；AFD部署通过为Attention与FFN分别选用最优硬件，使各模型成本降至最低。

该图直接支撑论文核心论点——Step-3虽**激活参数最多（38B）**，但凭借模型-系统协同设计（AFD等），解码成本反而最低，验证了"大而经济"的设计主张，是论文方法链路中**实验验证**的关键证据。

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
> 【图文联合解读】**图文联合解读（Figure 6）**

**1) 图示结构（量化）**：左路Attention模块（Norm→Attn→Norm+残差）本地计算；中路由Norm→Router→Expert Combine本地完成，右路由TP gather/EP scatter→Expert Compute→TP scatter/EP gather置于远端专家池。隐藏状态以fp8经中间虚线跨域传输，回传bf16；Router下发expert distribution，Expert Combine回传TopK score。

**2) 关键技术结论**：FFN模块可依硬件与模型结构，自适应选择TP-only、EP-only或TP+EP混合并行部署，体现模块解耦的灵活性。

**3) 论文作用**：作为Step-3模型-系统协同设计中AFD（Attention/FFN Disaggregation）架构的核心示意图，奠定"注意力本地低延迟+专家远端弹性扩展"的设计思想，是后续讨论专家均衡、稳定性及整体成本-性能权衡的方法基础。

### Figure 7 (p.12) ⭐深度解读
![[assets/crops/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-fig07.png]]
*整页渲染: ![[assets/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-p12.png]]*
> [!quote] caption
> Communication topology and the multi-stages pipeline of the AFD architecture.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

**1) 核心对象与结构**
左侧展示通信拓扑：8卡FFN实例与8卡Attention实例通过**Direct RDMA**实现1对1直连（GPU数量相等、无中间路由）。右侧为时间轴上的多阶段流水线：Layer0/Layer1各承载3个批次（D1–D3与D1'–D3'），FFN（顶行）与Attention（底行）交替执行；两者间存在两条非对称传输——FFN→Attention 采用 **bf16**（黄块1/2/3、1'/2'/3'），Attention→FFN 采用 **fp8**（棕色块）。

**2) 关键论证结论**
图文共同证明AFD架构通过：(a) 解耦Attention/FFN并直连以消除PCIe/NCCL瓶颈；(b) **非对称精度传输**（前向高保真、反向压缩）平衡精度与带宽；(c) 批次×层级二维流水，使通信与计算深度重叠，掩盖访存延迟。

**3) 在论文中的作用**
该图是AFD系统设计的核心机制图，作为前文MoE解码算力–带宽失衡问题与后续系统级硬件协同（cost-effective decoding）论证之间的桥梁，奠定"模型–系统协同"立论基础。

### Figure 8 (p.13) ⭐深度解读
![[assets/crops/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-fig08.png]]
*整页渲染: ![[assets/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-p13.png]]*
> [!quote] caption
> StepMesh communication workflow tailored for AFD.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图联合解读：**

**核心对象与结构：** 图示StepMesh为AFD设计的双实例流水线。左侧Attention实例含CPU三线程（NetRecv Thread经RDMA PollCQ收张量、Main Thread执行Wait→Launch Attention→PushPull、NetSend Thread做Kernel Sync与RDMA PostSend）与GPU（Attention Kernel将Activation Tensors转为Token Tensors）；右侧FFN实例结构对称（GPU跑FFN Kernel反向产出Activation Tensors），两实例经底部RDMA NIC交叉互连。

**关键结论：** 通过Recv/Send/Main三线程并行，Main Thread Wait与Launch Kernel期间网络收发被Kernel Sync完全隐藏，实现通信-计算全重叠；Token与Activation张量在Attention↔FFN间直接RDMA交换，无中心调度。

**论文作用：** 该图为AFD（Attention-FFN解耦）提供系统级实现证据，支撑论文"大模型廉价协同解码"的整体论点——异构低成本节点按Attention/FFN分工组网即可承担超大模型推理。

### Figure 9 (p.13) ⭐深度解读
![[assets/crops/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-fig09.png]]
*整页渲染: ![[assets/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-p13.png]]*
> [!quote] caption
> StepMesh framework for multiple accelerators. AF-

> [!tip] 技术解读（多模态）
> 【图文联合解读】## Figure 9 图文联合解读

**1) 核心结构（三层架构）：**
- **顶层 API 层**：左侧 AFTensorWorker API 封装 `Wait`、`PushPull`（供 attention 实例）；右侧 AFTensorServer API 封装 `GetBatch`、`Respond`（供 FFN 实例）。
- **中间核心层**：StepMesh Core，含 NetSend/NetRecv 线程，负责跨设备张量传输调度。
- **底层后端层**：分两条路径——Network API（RDMATransport → RDMA NIC）与 Accelerator API（CPUBackend / GPUBackend / xPUBackend → CPU / GPU / xPU 设备）。

**2) 关键结论：**
该图论证 StepMesh 将张量通信逻辑与底层硬件解耦，通过 Attention-FFN 解耦后两套对偶 API（PushPull 与 GetBatch/Respond）实现异构多加速器（CPU/GPU/xPU）间的 RDMA 高效协同。

**3) 论文链路作用：**
作为"模型–系统协同设计"中的**系统栈组件**，StepMesh 与 MFA 注意力、MoE 路由等算法级创新配套，支撑论文"大规模但低成本解码"的核心主张。

## 表格（裁剪图 + caption，可直接插入报告）

### Table 2 (p.5) ⭐深度解读
![[assets/crops/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-tab02.png]]
> [!quote] caption
> Theoretical computation and memory access per decoding token at 8K context length.

> [!tip] 表格解读（多模态）
> 【图文联合解读】Table 2 量化对比9个模型在8K上下文下的每token解码开销：Step-3的KV/State访存仅2.56×10⁸ bytes，与DSv3/Kimi K2并列最低，约为Qwen3 32B（1.07×10⁹）的1/4；Attention FLOPs（不含Linear）为3.27×10¹⁰，远低于DSv3的1.47×10¹¹；Attention前后Linear为2.07×10¹⁰；FFN计算5.33×10¹⁰，介于ERNIE 4.5（7.61×10¹⁰）与Llama 4 M（2.42×10¹⁰）之间。

该表支撑论文"模型-系统协同设计"的核心主张：Step-3在大参数规模前提下，通过Attention架构与算子优化将KV访存及Attention算力压至最低档，为后续在自研芯片上的低成本部署实验提供理论算力/带宽依据，是论证"规模大但推理便宜"的关键定量证据。

### Table 3 (p.5) ⭐深度解读
![[assets/crops/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-tab03.png]]
> [!quote] caption
> Theoretical computation and memory access per decoding token at 32K context length.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

该表对比9个主流模型在32K上下文长度下每解码token的理论开销，涵盖KV/State访存、Attention（含/不含Linear）和FFN四列FLOPs。Step-3的KV/State访存仅1.02×10⁹ bytes，为表中最低；Attention计算1.31×10¹¹ FLOPs远低于DSv3（5.89×10¹¹）和Kimi K2（2.95×10¹¹）。论文借此论证：通过在多数层采用线性注意力、仅保留少量MLA层，Step-3在长上下文解码时显著降低显存带宽瓶颈与Attention计算量，是其"既大又经济"架构设计（混合线性/全注意力+MoE FFN）成本优势的关键定量证据，支撑后续推理部署与系统协同优化的论证。

### Table 4 (p.6) ⭐深度解读
![[assets/crops/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-tab04.png]]
> [!quote] caption
> Comparison of accelerator specifications. *We do not have publicly available 910B pricing. We estimate its price proportionally based on its FLOPs and A800’s. As far as we know, there are multiple versions of 910B. We show the weakest and (presumably) most affordable one that we know.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 4 解读**

**1) 核心数据**：对比4款加速卡的单价（USD/h）、BF16/FP16与FP8算力、显存带宽及roofline算力带宽比——H800（$2，9.89×10¹⁴/1.98×10¹⁵，3.35×10¹² B/s，比值591）、H20（$0.8，比值74）、A800（$0.75，比值156）、Ascend 910B（约$0.67，比值175，FP8缺失）。

**2) 关键结论**：H800算力带宽比高达591，属计算密集型且价格最贵；而H20、A800、910B比值仅74–175，显存带宽相对突出，是memory-bound形态。说明解码（访存密集）对廉价卡的"屋顶线比值"远比绝对算力重要，H800在解码场景存在巨大算力浪费与价格溢价。

**3) 论文作用**：该表为Step-3"低算力带宽比友好"架构设计（如Attention-FFN解耦）提供硬件依据，证明模型可高效跑在H20/A800/910B等廉价卡上，从而支撑"大而便宜"的成本可控解码这一核心论断。

### Table 5 (p.6) ⭐深度解读
![[assets/crops/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-tab05.png]]
> [!quote] caption
> The unit cost of different accelerators assuming full utilization for the whole month. For FLOP costs, we consider FP8 for H800 and H20, BF16/FP16 for A800 and 910B.

> [!tip] 表格解读（多模态）
> 【图文联合解读】## Table 5 图文联合解读

**1) 核心数据**：四款加速器在满月利用率假设下的单位成本——
- **每 FLOP 成本**：H800 最低(2.80e-19)，H20 最高(7.51e-19)，A800 (6.68e-19) 与 910B (6.65e-19) 几乎持平
- **每字节访存成本**：H20 最低(5.56e-17)，H800 最高(1.66e-16)，A800 (1.04e-16) 与 910B (1.16e-16) 接近
- **关键比率**：H800 计算/访存价比最低（ridge point≈512），H20 最高（≈32），A800/910B 居中（≈156/175）

**2) 技术结论**：算力便宜≠访存便宜。Step-3 的 MFA 算术强度≈128，恰落在 A800/910B 的 ridge 点附近，因此**跨硬件都能平衡利用**——相比 DSv3 MLA（强度512，仅 H800 划算）省 3/4 计算量，相比 Qwen3 GQA（强度32，仅 H20 划算）省 2/3 访存量。

**3) 论文作用**：本表是论文"Affordable"主张的成本模型基石——证明通过**模型与系统协同设计**（让 attention 的算术强度匹配硬件 ridge），而非堆砌 FLOPs，能在中国 910B 等国产硬件上实现与 H800 同阶的部署成本，支撑 Step-3 "大而省钱" 的核心叙事。

### Table 6 (p.7) ⭐深度解读
![[assets/crops/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-tab06.png]]
> [!quote] caption
> Theoretical decoding cost analysis for each model on each hardware, in USD. As a reminder, these models have different number of activated parameters: DSv3 37B, Qwen3 MoE 22B, Qwen3 32B, MM M1 46B, ERNIE 4.5 47B, Pangu Pro MoE 16.5B and Step-3 38B.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 6 图文联合解读**

**1) 核心对象与结构**：Table 6 以双柱状图对比四个代表性模型（DSv3、Qwen3 MoE、Qwen3 32B、Step-3）在 5 种部署方案（H800、H20、A800、910B、AFD）下，8K 与 32K 上下文的单次理论解码成本（USD）。

**2) 关键结论**：Step-3 在所有硬件配置上均为最低（如 32K + AFD 仅 ≈ $0.13，对比 Qwen3 32B 同配置 ≈ $0.27，降幅近 50%）；AFD 方案整体优于传统 H800/A800/910B 单卡部署，原文借此论证 Step-3"小激活参数 MoE + MLA"协同搭配 AFD 模块解耦架构所换来的解码成本优势。

**3) 在论文中的作用**：该表是论文标题 "large yet affordable" 主张的核心量化支撑，串联"模型设计 → AFD 系统 → 解码经济性"完整论证链。

### Table 7 (p.10) ⭐深度解读
![[assets/crops/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-tab07.png]]
> [!quote] caption
> Minimum MoE sparsity for different hardware plat- forms to achieve good MFU, where H = 7168, L = 61.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 7 图文联合解读**

**核心对象与数据**：表格给出在 H=7168、L=61 的 Step-3 MoE 配置下，四种加速器（H800、H20、A800、910B）实现良好 MFU 所需的最小专家激活稀疏度 S：H800=0.058、H20=0.007、A800=0.031、910B=0.034。

**关键结论**：稀疏度阈值由公式 S ≥ (H·FLOPs·L)/(Net·Bandwidth·11.1ms) 推导，受算力（FLOPs）与网络带宽共同制约。尽管 H800/H20 带宽（400Gbps×8 NIC）高于 A800/910B（200Gbps×8 NIC），但 H800 算力更强、FLOPs 更高，反而需要更大稀疏度（5.8%）；而 H20 算力较弱，仅需 0.7% 即可隐藏通信。

**论文作用**：该表是"模型-系统协同设计"论证链的核心——证明最优 MoE 稀疏度必须匹配硬件特性，为 Step-3 针对自研硬件选择特定稀疏度（如 AFD 中专家调度）提供量化依据。

### Table 8 (p.14) ⭐深度解读
![[assets/crops/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-tab08.png]]
> [!quote] caption
> Performance comparison with reported number of DSv3 under 20 tokens/s decoding SLA. TGS: Tokens/GPU/s.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 8 图文联合解读**

**核心数据**：在 20 tokens/s 解码 SLA 约束下，对比 DSv3 与 Step-3 的 Tokens/GPU/s (TGS)。Step-3 (BF16, 4096 len) 以 40 卡 (3A2F) 达到 **3321 TGS**；升级为 FP8 attention 后仅需 32 卡 (2A2F) 即达 **4039 TGS**；即便长度翻倍至 8192，仍以 48 卡 (4A2F) 取得 **2643 TGS**。相比之下，DSv3-blog 与 DSv3-profile 分别需 144 卡/128 卡，仅获 1850/2324 TGS。

**关键结论**：Step-3 以更少 GPU、更低精度 (FP8) 取得显著更高的单卡吞吐，单位算力成本远优于 DSv3，证明"模型–系统协同设计"在大模型解码场景下的成本有效性。

**论文作用**：作为核心成本论据，量化佐证文题"Large Yet Affordable"，支撑系统级 AFD 与 FP8 注意力优化的工程价值。

### Table 9 (p.14) ⭐深度解读
![[assets/crops/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-tab09.png]]
> [!quote] caption
> Performance comparison of MFA/MLA/GQA. For MLA, we use FlashMLA which does not have official SM80 implementation, so its A800 number is not tested. We use FA3 (SM90) and FA2 (SM80) for MFA/GQA. Here the attention layer includes the linear projection before and after the core attention op. Each exper

> [!tip] 表格解读（多模态）
> 【图文联合解读】表9以4卡、batch 256比较8k/32k、H800/H20/A800注意力层延迟（μs，含前后投影）：MFA-Step3=281/438/531、791/1452/1484；MLA-DSv3=372/1252/—、1125/4817/—；GQA-Qwen3=382/812/791、1391/3042/3010。MFA三平台均最低，且8k→32k增幅最小，支撑模型—注意力—硬件协同的低成本解码；MLA因无SM80实现缺A800数据。

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