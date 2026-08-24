---
paper_num: "63"
title: "Kimi Linear: An Expressive, Efficient Attention Architecture"
authors: ""
date: "2025/10/30"
arxiv: "https://arxiv.org/abs/2510.26692"
pdf: "papers/kimi-linear-an-expressive-efficient-attention-architecture.pdf"
slug: "kimi-linear-an-expressive-efficient-attention-architecture"
tags: []
---

# Kimi Linear: An Expressive, Efficient Attention Architecture

> [!abstract] 摘要（原文）
> We introduce Kimi Linear, a hybrid linear attention architecture that, for the first time, outperforms full attention under fair comparisons across various scenarios -- including short-context, long-context, and reinforcement learning (RL) scaling regimes. At its core lies Kimi Delta Attention (KDA), an expressive linear attention module that extends Gated DeltaNet with a finer-grained gating mechanism, enabling more effective use of limited finite-state RNN memory. Our bespoke chunkwise algorithm achieves high hardware efficiency through a specialized variant of the Diagonal-Plus-Low-Rank (DPLR) transition matrices, which substantially reduces computation compared to the general DPLR formulation while remaining more consistent with the classical delta rule. We pretrain a Kimi Linear model with 3B activated parameters and 48B total parameters, based on a layerwise hybrid of KDA and Multi-Head Latent Attention (MLA). Our experiments show that with an identical training recipe, Kimi Linear outperforms full MLA with a sizeable margin across all evaluated tasks, while reducing KV cache usage by up to 75% and achieving up to 6 times decoding throughput for a 1M context. These results demonstrate that Kimi Linear can be a drop-in replacement for full attention architectures with superior performance and efficiency, including tasks with longer input and output lengths. To support further research, we open-source the KDA kernel and vLLM implementations, and release the pre-trained and instruction-tuned model checkpoints.

## 元信息
- **发表日期**: 2025/10/30
- **作者**: —
- **arXiv**: https://arxiv.org/abs/2510.26692
- **本地 PDF**: `papers/kimi-linear-an-expressive-efficient-attention-architecture.pdf`
- **页数**: 28

## 图表（原文 caption + 页码）

### Figure 1 (p.1) ⭐深度解读
![[assets/crops/kimi-linear-an-expressive-efficient-attention-architecture-fig01.png]]
*整页渲染: ![[assets/kimi-linear-an-expressive-efficient-attention-architecture-p01.png]]*
> [!quote] caption
> (a) Performance vs. acceleration. With strict fair comparisons with 1.4T training tokens, on MMLU-Pro (4k context length, red stars), Kimi Linear leads performance (51.0) at similar speed. On RULER (128k context length, blue circles), it is Pareto-optimal, achieving top performance (84.3) and 3.98× acceleration. (b) Time per output token (TPOT) vs. decoding length. Kimi Linear (blue line) maintain

> [!tip] 技术解读（多模态）
> 【图文联合解读】图(a)性能–加速比散点图：MMLU-Pro(4k)上Kimi Linear以51.0分同速领先（GDN-H 47.9、MLA 47.2），RULER(128k)上以84.3分达Pareto最优并实现3.98×加速（MLA 81.3、GDN-H 80.5）。图(b)TPOT–解码长度曲线显示，Kimi Linear在1M tokens时约1.84ms，较MLA的11.48ms分别于256K/512K/1M处实现4.8×/5.7×/6.3×加速，曲线几乎贴合GDN-H。该开篇图以统一1.4T token作严格公平对比，从任务精度与推理时延双维度论证Kimi Linear在长上下文下兼具高表达与高效率的核心卖点，为后续混合架构设计及扩展实验提供核心动机。

### Figure 2 (p.5) ⭐深度解读
![[assets/crops/kimi-linear-an-expressive-efficient-attention-architecture-fig02.png]]
*整页渲染: ![[assets/kimi-linear-an-expressive-efficient-attention-architecture-p05.png]]*
> [!quote] caption
> Execution time of kernels for vary- ing input lengths, with a uniform batch size of 1 and 16 heads.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图2展示在 batch=1、16 heads 固定条件下，两种注意力核 **KDA（作者方法，蓝色实线）与 DPLR（绿色虚线）** 随输入长度 2K→64K 的执行时间（ms）。具体数据：2K 时两者均约 1 ms，几无差异；8K 起 KDA 拉开优势（KDA≈3 ms vs DPLR≈8 ms）；16K 时 KDA≈6 ms、DPLR≈15 ms；32K 时 KDA≈14 ms、DPLR≈30 ms；64K 时差距最大，KDA≈30 ms，DPLR≈58 ms，DPLR 约为 KDA 的 2 倍。

原文借此论证：在不牺牲表达性的前提下，KDA 核在长序列上具有显著的 **线性复杂度效率优势**，且序列越长优势越显著，为后续 Table 2 的 scaling law 实验和端到端训练吞吐收益提供了底层算子级证据支撑。

### Figure 3 (p.5) ⭐深度解读
![[assets/crops/kimi-linear-an-expressive-efficient-attention-architecture-fig03.png]]
*整页渲染: ![[assets/kimi-linear-an-expressive-efficient-attention-architecture-p05.png]]*
> [!quote] caption
> Neural Parameterization

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图3展示Kimi Linear架构：每个块由token-mixing层（Norm+注意力）后接MoE通道混合层（Norm+MoE）组成，**采用"N个KDA层间插1个MLA层"的混合模式（图中标注N×与1×，N=3）**。右上展开MoE细节：含Ns个Shared Expert与Nr个Routed Expert（Router门控按概率分布选择）；右下展开KDA：两条路径分别经Linear+Conv与σ门控融合后送入Kimi Delta Attention。

**技术结论**：主体使用线性复杂度KDA保留细粒度信息，**周期性MLA层维持全局注意力锚点**；MoE的共享+路由专家设计兼顾通用知识与专项能力。

**论文作用**：作为方法总览图，与Table 3呼应——为"Kimi Linear同时超越纯MLA基线与GDN-H混合基线"的短上下文评估结果提供结构性依据，奠定"线性注意力+周期全注意力"的设计范式。

### Figure 4 (p.7) ⭐深度解读
![[assets/crops/kimi-linear-an-expressive-efficient-attention-architecture-fig04.png]]
*整页渲染: ![[assets/kimi-linear-an-expressive-efficient-attention-architecture-p07.png]]*
> [!quote] caption
> Results on synthetic tasks: palindrome, multi query associative recall, and the state tracking.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读（Figure 4）**

该图通过 2×3 子图矩阵，对比 **KDA、GDN、Mamba2** 三种架构在三类合成任务——**Palindrome（回文）、MQAR（多查询关联回忆）、Stack（状态跟踪）**——的表现：上排刻画序列长度 256→2048 的**长度外推**，下排刻画 0–20K 步的**收敛曲线**。

核心定量发现：(1) **Mamba2 在三类任务中均崩塌至 0%**，表明其表达力不足以求解此类精确记忆/状态任务；(2) **长度外推差距明显**——MQAR 在 1024→2048 时，KDA 仍保持 ~47%，GDN 仅 ~28%；(3) **收敛效率 KDA ≫ GDN**——Palindrome 中 KDA 约 5K 步即达 100%，而 GDN 需约 17K 步；Stack 上 KDA 3K 步收敛，GDN 需 ~5K 步。

该图为论文核心主张提供**受控合成证据**：KDA（Kimi Linear 的内核）同时具备更强表达力、更好长度泛化与更快收敛，**为后续在 Table 4 中论证 Kimi Linear 替代 full-attention MLA 的可行性奠定实验基础**，构成从合成任务→短上下文 benchmark→长上下文评测的完整验证链路的第一步。

### Figure 5 (p.9) ⭐深度解读
![[assets/crops/kimi-linear-an-expressive-efficient-attention-architecture-fig05.png]]
*整页渲染: ![[assets/kimi-linear-an-expressive-efficient-attention-architecture-p09.png]]*
> [!quote] caption
> The fitted scaling law curves for MLA and Kimi Linear. balanced positional bias across layers, which improves robustness and extrapolation at long ranges, leading to stronger long-context performance. Regarding long context performance, as shown in Table 5, Kimi Linear achieves the best average score across different long context benchmarks, which verifies the benefits we claim in the last section

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

**1）核心对象与数据：** 该图以双对数坐标绘制 PFLOPS/s-days（横轴，约 4–25） vs Loss（纵轴，约 1.98–2.26）的缩放曲线。两条幂律拟合分别为 MLA：L=2.3092·C⁻⁰·⁰⁵³⁶（蓝）与 Kimi Linear：L=2.2879·C⁻⁰·⁰⁵²⁷（红），星标为各计算预算下的实测点。红线在所有尺度上系统性低于蓝线，并在图中标注"Kimi Linear 达到同等 Loss 仅需约 1.16× 更少算力"。

**2）关键结论：** Kimi Linear 在 MLA 同等训练成本下取得更低损失，或在相同损失下减少 ~16% 算力，证明其替代 MLA 时具有更优的标度效率。

**3）论文作用：** 该图是连接"架构设计 → 训练效率"的核心证据，配合 Table 5 的长上下文评测，共同支撑"用 Kimi Linear 替换 MLA 兼具高效与长程性能更强"的整体论断。

### Figure 6 (p.12) ⭐深度解读
![[assets/crops/kimi-linear-an-expressive-efficient-attention-architecture-fig06.png]]
*整页渲染: ![[assets/kimi-linear-an-expressive-efficient-attention-architecture-p12.png]]*
> [!quote] caption
> The training and test accuracy curves for Kimi Linear@1.4T and MLA@1.4T during Math RL training. Kimi Linear consistently outperforms the full attention baseline by a sizable margin during the whole RL process.

> [!tip] 技术解读（多模态）
> 【图文联合解读】图(a)(b)(c)分别展示Math RL训练中 Kimi Linear@1.4T 与 MLA@1.4T 在训练集、MATH 500、AIME 2025 上的精度曲线：(a) 训练精度 Kimi Linear 升至约 58–60，MLA 仅约 52；(b) MATH 500 测试 Kimi Linear 稳定在 ~86，MLA ~84；(c) AIME 2025 Kimi Linear 达 ~22，MLA ~19。原文据此论证：高效线性注意力在 RL 后训练阶段全程持续领先全注意力基线（MLA），验证"Kimi Linear 可替代 MLA"这一核心结论，补齐了从预训练到 RL 的完整实验证据链。

### Figure 7 (p.13) ⭐深度解读
![[assets/crops/kimi-linear-an-expressive-efficient-attention-architecture-fig07.png]]
*整页渲染: ![[assets/kimi-linear-an-expressive-efficient-attention-architecture-p13.png]]*
> [!quote] caption
> (a) The prefilling time of MLA (full attention), hybrid GDN-H and our Kimi Linear. (b) The time per output token (TPOT) for MLA, GDN-H and Kimi Linear during decoding. (We use batch size = 1 here for tests.) performance curves are virtually indistinguishable, confirming that our method maintains high efficiency. The hybrid

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图7展示在batch=1条件下，三种注意力机制的效率对比。左图(a)为预填充延迟：当序列达1M时，MLA约64s，Kimi Linear仅约22s（2.9×加速），512K处达2.3×；右图(b)为解码TPOT：1M处MLA约17ms，Kimi Linear约8ms（2.2×），512K处1.8×。GDN-H曲线与Kimi Linear几乎重合。

原文借此论证：**Kimi Linear在保持表达能力的同时，效率与线性注意力基线GDN-H基本一致**，并显著优于全注意力MLA，随长度增长优势放大。

该图在论文中充当**效率与可扩展性证据**，与Table 7（机制理论统一性）相互呼应，证明Kimi Linear不仅在TTT框架下与主流注意力机制同构，更在长序列场景下具备实际部署的推理优势，支撑"expressive且efficient"的核心主张。

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.8) ⭐深度解读
![[assets/crops/kimi-linear-an-expressive-efficient-attention-architecture-tab01.png]]
> [!quote] caption
> Ablation study on the hybrid ratio of KDA to MLA attention and other key components. We list the training and validation perplexities (lower is better) for comparison. The best-performing model, used in our final experiments, is highlighted in gray.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 1 图文联合解读：**

Table 1 对比 5 种 KDA:MLA 混合比（0:1、1:1、3:1、7:1、15:1）的训练与验证困惑度。3:1（灰底高亮）取得训练 PPL 9.23、验证 PPL 5.65 的双优结果；纯 MLA（0:1）为 9.45/5.77，纯 KDA 过多（15:1）降至 9.34/5.82，整体呈倒 U 型分布。

**技术结论：** 线性注意力 KDA 需略多于 MLA 但不能过度，3:1 为最佳配比，证明混合架构优于任一单组件，验证了 Kimi Linear 设计的合理性。

**链路作用：** 作为核心消融依据，为最终模型结构选择提供经验支撑；与图 1 中 Pareto 最优性能（MMLU-Pro 51.0、RULER 84.3、3.98× 加速）衔接，构成"组件消融 → 架构定型 → 性能实证"的完整论证链。

### Table 2 (p.9) ⭐深度解读
![[assets/crops/kimi-linear-an-expressive-efficient-attention-architecture-tab02.png]]
> [!quote] caption
> Model configurations and hyperparameters for scaling law experiments.

> [!tip] 表格解读（多模态）
> 【图文联合解读】表列5组MoE缩放模型：激活参数（不含嵌入）653M→1.7B，层数/头数均16→24，隐宽1216→1776；训练Token为38.8B→128.0B，批量336→640，学习率2.006e−3→1.371e−3，上下文固定4096。该设置支持受控比较模型规模，连接Kimi Linear的效率分析与缩放律拟合，用于研判扩模后的性能趋势、计算需求和训练配置选择。

### Table 3 (p.11) ⭐深度解读
![[assets/crops/kimi-linear-an-expressive-efficient-attention-architecture-tab03.png]]
> [!quote] caption
> Performance comparison of Kimi Linear with the full-attention MLA baseline and the hybrid GDN baseline, all after the same pretraining recipe. Kimi Linear consistently outperforms both MLA and GDN-H on short-context pretrain evaluations. Best per-column results are bolded .

> [!tip] 表格解读（多模态）
> 【图文联合解读】Table 3 在 1.4T tokens 同条件预训练下，对比 MLA（满注意）、GDN-H（混合线性）与 Kimi Linear 在 General / Math & Code / Chinese 三类共 15 项基准的表现。General 类 Kimi Linear 全部领先（7/7），如 MMLU 73.8 vs 72.2、HellaSwag 82.9 vs 82.2、MMLU-Pro 51.0 vs 47.9；Math & Code 中 GSM8K 83.9、CRUXEval-O-cot 62.0 最佳；中文 CEval 79.5、CMMLU 80.8 亦小幅领先。该表用以论证 Kimi Linear 的混合架构在短上下文预训练中已全面超越全注意力与纯线性基线，为方法有效性与后续长上下文评测奠定实验基础。

### Table 4 (p.11) ⭐深度解读
![[assets/crops/kimi-linear-an-expressive-efficient-attention-architecture-tab04.png]]
> [!quote] caption
> Performance comparison of Kimi Linear with the full-attention MLA baseline and the hybrid GDN baseline, all using the same SFT recipe after pretraining. Kimi Linear consistently outperforms both MLA and GDN-H on short-context instruction-tuned benchmarks. Best per-column results are bolded .

> [!tip] 表格解读（多模态）
> 【图文联合解读】Table 4对比MLA、GDN-H、Kimi Linear（同1.4T token、同SFT）在12项短文指令基准的表现。Kimi Linear在General 6项中夺5冠（BBH 69.4、MMLU 77.0、MMLU-Pro 67.4、MMLU-Redux 80.3、GPQA-Diamond 62.1），仅LiveBench 45.2略输于GDN-H 46.4；Math & Code 6项再夺4冠（AIME 21.3、HMMT 12.5、PolyMath 43.6、LiveCodeBench 26.0），GDN-H仅MATH500 83.0领先，合计10/12胜出。论文据此论证：在同预训练+微调条件下，线性注意力的Kimi Linear可系统性击败全注意力MLA与混合GDN-H。该表承接图4合成任务对表达力的证明，将结论由受控实验推广至真实短文下游基准，是论文"理论→实用"证据链的关键环节。

### Table 5 (p.12) ⭐深度解读
![[assets/crops/kimi-linear-an-expressive-efficient-attention-architecture-tab05.png]]
> [!quote] caption
> Comparisons of Kimi Linear with MLA, GDN-H, and Kimi Linear (RoPE) across long-context benchmarks. The last column reports the overall average ( ↑ ). All models is trained on 1.4T tokens. Best per-column results are bolded .

> [!tip] 表格解读（多模态）
> 【图文联合解读】Table 5 在 8 个长上下文基准上对比 Kimi Linear、MLA、GDN-H、Kimi Linear(RoPE) 四种架构（均训于 1.4T tokens）：Kimi Linear 平均分 54.5 居首，分别超 MLA(52.2)、GDN-H(51.2)、RoPE 变体(51.8)，并在 RULER(84.3)、MRCR(29.6)、HELMET-ICL(90.0)、RepoQA(68.5)、Long Code Arena-Lib(37.1) 五项夺魁；MLA 仅在 LongBench V2、Frames、Commit 三项领先。原文借此验证"Kimi Linear 替换 MLA 后长程性能更优"的核心结论，与 Figure 5 缩放律曲线共同构成"架构设计→训练高效且长上下文更强"的闭环证据。

### Table 6 (p.14) ⭐深度解读
![[assets/crops/kimi-linear-an-expressive-efficient-attention-architecture-tab06.png]]
> [!quote] caption
> An overview of attention mechanisms in their mathematically equivalent recurrent ( o t ) and parallel ( O ) forms. We omitted the normalization term and β t to achieve a more concise representation. The function ϕ refers to the infinite-dimensional feature space corresponding to the exponential kern

> [!tip] 表格解读（多模态）
> 【图文联合解读】Table 6以递推式(oₜ)与并行式(O)两列对照，列出SA、SA+RoPE、LA、Mamba2、GLA、DeltaNet、FoX、DeltaFormer、PaTH-FoX、GDN、Comba、RWKV7共12种机制（省略归一化与βₜ），末行高亮作者提出的KDA。

论证：KDA递推式∏Diag(αₛ)(I−kₛkₛᵀ)整合GLA的对角衰减门控与DeltaNet的差分更新；并行式((Q⊙Γ)(K/Γ)ᵀ⊙M)(I+(K⊙Γ)(K/Γ)ᵀ⊙M⁻¹)⁻¹V支持分块并行训练，证其兼具高效推理与高效训练能力。

作用：建立KDA在近期线性/线性化注意力谱系中的位置，为后续Kimi Linear混合架构（KDA层+MLA层）的选型与硬件高效实现提供理论前置。

### Table 7 (p.16) ⭐深度解读
![[assets/crops/kimi-linear-an-expressive-efficient-attention-architecture-tab07.png]]
> [!quote] caption
> An overview of different attention mechanisms through the lens of state updating rules and their learning objective under the TTT framework [ 90 ]. We ignore all normalizer terms and activation/kernel functions for brevity.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**核心对象与结构**：表7在TTT框架下并列展示10种注意力机制（LA、RetNet、Mamba2、GLA、HGRN2、Longhorn、Comba、RWKV7、GDN）的目标函数ℒ与状态更新规则S_t=S_{t-1}−∇ℒ。KDA（本文）目标简化为β_t/2‖S̃_{t-1}k_t−v_t‖²（仅保留数据拟合项，无正则项），更新采用Diag(α_t)逐维门控，是对GDN标量门控α_t的细粒化扩展。

**技术结论**：KDA将标量衰减（RetNet/Mamba2的高效性）与逐维门控（GLA的表达力）统一在同一更新式中，其更新可解释为对细粒度衰减状态S̃执行SGD步骤，理论上同时获得两类方法的优势。

**论文作用**：作为Kimi Linear核心理论支柱，承接Table 6的形式化能力上界证明，为后续KDA算法实现与Figure 7的效率实验提供统一形式化基础，是方法论证的关键一环。

### Table 8 (p.0) ⭐深度解读
![[assets/crops/kimi-linear-an-expressive-efficient-attention-architecture-tab08.png]]
> [!quote] caption
> Performance of Kimi-Linear-Base and Moonlight-Base across diverse tasks.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 8 图文解读**

该表在相同激活参数（3B MoE）与训练量（5.7T tokens）条件下对比 Kimi-Linear-Base（48B 总参）与 Moonlight-Base（16B 总参）在 16 项基准上的表现。Kimi-Linear 在全部任务上均领先：通用类 TriviaQA 75.2 vs 66.2、MMLU-Pro 54.8 vs 42.4、WinoGrande 81.5 vs 74.6；数学类 MATH 58.5 vs 45.3、GSM8k 86.3 vs 77.2、CMATH 85.5 vs 79.6；代码类 CRUXEval-I-cot 61.0 vs 45.9、EvalPlus 64.9 vs 50.3；中文 C-Eval 83.3 vs 77.6、CSimpleQA 53.5 vs 34.7。原文借此论证新线性注意力架构在显著减少 KV 内存的同时不牺牲质量，且跨任务均稳定优于同等激活预算的标准 MoE 基线。该表是论文"效率–表达力等价"实验链路的关键支撑：在通用、数学、代码、中文多维度证明 Kimi-Linear 具备可扩展性与任务普适性。

### Table 9 (p.28) ⭐深度解读
![[assets/crops/kimi-linear-an-expressive-efficient-attention-architecture-tab09.png]]
> [!quote] caption
> Performance of Kimi-Linear-Instruct and Moonlight-Instruct across diverse tasks.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

图片仅显示 Table 9 的局部——中文任务部分：在 C-Eval（5-shots）上，Kimi-Linear-Instruct 得 83.3，Moonlight-Instruct 得 77.6；在 CSimpleQA（5-shots）上，前者 53.5，后者 34.7。两列数值均显示 Kimi-Linear-Instruct 显著优于 Moonlight-Instruct，中文知识与推理任务差距分别达 5.7 与 18.8 分。

**技术结论：** 该表用以证明 Kimi-Linear 采用线性注意力后，跨语言（含中文）的综合任务能力不仅未下降，反而优于同基座的 Moonlight，验证其在多样任务上的通用性与表达力。

**作用：** 属于论文实验链路的综合评测环节，作为"多样化下游任务性能"的证据支撑核心主张——线性注意力架构在保持效率的同时不牺牲多任务表现。

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\mathbf{S}_t = \left(\mathbf{I}-\beta_t\bm{k}_{t}\bm{k}_{t}^{\top}\right)\brickred{\operatorname{Diag}\left(\bm{\alpha}_t \right)}\mathbf{S}_{t-1} + \beta_t\bm{k}_{t}\bm{v}_{t}^{\top}\in\mathbb{R}^{d_k\times d_v}; \qquad \bm{o}_t = \mathbf{S}^\top_t \bm{q}_t\in\mathbb{R}^{d_v}
$$

$$
\begin{aligned} \mathbf{S}_{[t]}^r & = \underbrace{\left(\prod_{i=1}^r \left(\mathbf{I} - \beta_{[t]}^i \boldsymbol{k}_{[t]}^i \boldsymbol{k}_{[t]}^{i\top}\right) \brickred{\operatorname{Diag}(\boldsymbol{\alpha}_{[t]}^i)}\right)}_{:= \mathbf{P}_{[t]}^r} \cdot\mathbf{S}_{[t]}^{0} + \underbrace{\sum_{i=1}^{r} \left(\prod_{j=i+1}^r \left(\mathbf{I} - \beta_{[t]}^j \boldsymbol{k}_{[t]}^j \boldsymbol{k}_{[t]}^{j\top}\right)\brickred{\operatorname{Diag}(\boldsymbol{\alpha}_{[t]}^j)}\right)\cdot\beta_{[t]}^i \boldsymbol{k}_{[t]}^i\boldsymbol{v}_{[t]}^{i\top}}_{:=\mathbf{H}_{[t]}^r} \end{aligned}
$$

$$
\mathbf{S}_{[t+1]} = \brickred{\operatorname{Diag}(\boldsymbol{\gamma}_{[t]}^C)} \mathbf{S}_{[t]} + \left(\brickred{\bm{\Gamma}_{[t]}^{i\rightarrow C}} \odot \mathbf{K}_{[t]}\right)^\top \left(\mathbf{U}_{[t]} - \mathbf{W}_{[t]} \mathbf{S}_{[t]}\right) \in \mathbb{R}^{d_k\times d_v}
$$

$$
\mathbf{O}_{[t]} = \underbrace{\left(\brickred{{\bm{\Gamma}}_{[t]}^{1\rightarrow C}} \odot\mathbf{Q}_{[t]}\right) \mathbf{S}_{[t]}}_\text{inter chunk} + \underbrace{\operatorname{Tril}\left(\left(\brickred{{\bm{\Gamma}}_{[t]}^{1\rightarrow C}} \odot \mathbf{Q}_{[t]} \right) \left(\frac{\mathbf{K}_{[t]}}{\brickred{{\bm{\Gamma}}_{[t]}^{1\rightarrow C}}} \right)^\top \right)}_\text{intra chunk} \underbrace{\left(\mathbf{U}_{[t]} - \mathbf{W}_{[t]} \mathbf{S}_{[t]}\right)}_{\text{``pseudo''-value term}} \in \mathbb{R}^{C\times d_v}
$$

$$
\begin{aligned} \bm{o}_t = \mathbf{W}_o\left( \operatorname{Sigmoid}\left(\mathbf{W}_g^{\uparrow}\mathbf{W}_g^{\downarrow} \bm{x}_t\right)\odot \operatorname{RMSNorm}\left(\operatorname{KDA}\left( \bm{q}_t,\bm{k}_t,\bm{v}_t,\brickred{\bm{\alpha}_t},\beta_t \right) \right)\right) \end{aligned}
$$

$$
s_{t,i} = \bm{q}_t^{\top} \left( \prod_{j=i+1}^t \mathbf{R}_j\right) \bm{k}_i
$$

$$
\mathrm{FLOPs}_{\text{Attn}}(T; d_h) \;=\; 2 T^2 d_h.
$$

$$
\mathbf{S}_{t}=\brickred{\mathbf{A}_t}\mathbf{S}_{t-1} + \bm{k}_t\bm{v}_t^\top,\quad\bm{o}_{t}=\mathbf{S}_t^\top\bm{q}_t.
$$

$$
\mathbf{P}_{[t]}^r = \brickred{\operatorname{Diag}(\boldsymbol{\gamma}_{[t]}^r)} - \sum_{i=1}^{r} \brickred{\operatorname{Diag}(\boldsymbol{\gamma}_{[t]}^{i\rightarrow r})} \boldsymbol{k}_{[t]}^i \boldsymbol{w}_{[t]}^{i\top}
$$

$$
\boldsymbol{w}_{[t]}^r = \beta_{[t]}^r \left( \brickred{\operatorname{Diag}(\boldsymbol{\gamma}_{[t]}^r)} \boldsymbol{k}_{[t]}^r - \sum_{i=1}^{r-1} \boldsymbol{w}_{[t]}^i\left( \boldsymbol{k}_{[t]}^{i\top}\brickred{\operatorname{Diag}\left(\boldsymbol{\gamma}_{[t]}^{i\rightarrow r} \right)}\boldsymbol{k}_{[t]}^r \right) \right)
$$

$$
\mathbf{H}_{[t]}^r = \sum_{i=1}^{r} \brickred{\operatorname{Diag}\left(\boldsymbol{\gamma}_{[t]}^{i\rightarrow r}\right)} \boldsymbol{k}_{[t]}^i \boldsymbol{u}_{[t]}^{i\top}
$$

$$
\boldsymbol{u}_{[t]}^r = \beta_{[t]}^r \left(\boldsymbol{v}_{[t]}^r - \sum_{i=1}^{r-1}\boldsymbol{u}_{[t]}^i \left(\boldsymbol{k}_{[t]}^{i\top} \brickred{\operatorname{Diag}\left(\boldsymbol{\gamma}_{[t]}^{i\rightarrow r}\right)} \boldsymbol{k}_{[t]}^r\right) \right)
$$

$$
\boldsymbol{w}_{[t]}^r &= \beta_{[t]}^r \left( \brickred{\operatorname{Diag}(\boldsymbol{\gamma}_{[t]}^r)} \boldsymbol{k}_{[t]}^r - \sum_{i=1}^{r-1} \boldsymbol{w}_{[t]}^i\left( \boldsymbol{k}_{[t]}^{i\top}\brickred{\operatorname{Diag}\left(\boldsymbol{\gamma}_{[t]}^{i\rightarrow r} \right)}\boldsymbol{k}_{[t]}^r \right) \right) \\ \boldsymbol{u}_{[t]}^r &= \beta_{[t]}^r \left(\boldsymbol{v}_{[t]}^r - \sum_{i=1}^{r-1}\boldsymbol{u}_{[t]}^i \left(\boldsymbol{k}_{[t]}^{i\top} \brickred{\operatorname{Diag}\left(\boldsymbol{\gamma}_{[t]}^{i\rightarrow r}\right)} \boldsymbol{k}_{[t]}^r\right) \right)
$$

$$
\mathbf{M}_{[t]}&=\left(\mathbf{I} + \operatorname{StrictTril} \left(\operatorname{Diag}\left(\beta_{[t]}\right) \left(\brickred{{\bm{\Gamma}}_{[t]}^{1\rightarrow C}} \odot \mathbf{K}_{[t]} \right) \left(\frac{\mathbf{K}_{[t]}}{\brickred{\bm{\Gamma}_{[t]}^{1\rightarrow C}}} \right)^\top\right) \right)^{-1} \operatorname{Diag}\left(\beta_{[t]}\right)\\ \mathbf{W}_{[t]} &= \mathbf{M}_{[t]} \left(\brickred{{\bm{\Gamma}}_{[t]}^{1\rightarrow C}}\odot\mathbf{K}_{[t]}\right), \quad\quad\quad \mathbf{U}_{[t]}=\mathbf{M}_{[t]} \mathbf{V}_{[t]}
$$

$$
\bm{q}^h_t,\bm{k}^h_t &= \operatorname{L2Norm}(\operatorname{Swish}(\operatorname{ShortConv}(\mathbf{W}^h_{q/k}\bm{x}_t)))\in \mathbb{R}^{d_k}\\ \bm{v}^h_t &= \operatorname{Swish}(\operatorname{ShortConv}(\mathbf{W}^h_v\bm{x}_t))\in \mathbb{R}^{d_v} \\ \brickred{\bm{\alpha}^h_t} &= f(\mathbf{W}_{\alpha}^{\uparrow}\mathbf{W}_{\alpha}^{\downarrow}\bm{x}_t) \in [0,1]^{d_k}\\ \beta^h_t &= \operatorname{Sigmoid}(\mathbf{W}_{\beta}^h\bm{x}_t) \in [0,1]\\
$$

$$
\bm{o}_t = \sum_{i=1}^t \left( \bm{q}_t^{\top} \left(\prod_{j=i+1}^t\brickred{\mathbf{A}_j}\left(\mathbf{I}-\beta_j\bm{k}_j\bm{k}_j^\top\right) \right)\bm{k}_j\right) \bm{v}_j
$$

$$
\mathrm{FLOPs}_{\text{KDA}}(T; C, d_h) &= 6 T d_h^2 + 3 T C d_h + T C^2.
$$

$$
\mathbf{S}_t = \mathbf{S}_{t-1} + \bm{k}_t \bm{v}_t^\top, \qquad \bm{o}_t = \mathbf{S}_t^\top \bm{q}_t .
$$

$$
\mathcal{L}_t(\mathbf{S}) = -\langle \mathbf{S}^\top \bm{k}_t, \bm{v}_t \rangle ,
$$

$$
\mathcal{L}_t(\mathbf{S}) = \tfrac{1}{2}\|\mathbf{S}^\top\bm{k}_t - \bm{v}_t\|^2 .
$$

## 技术点深读（DEEP）

![[deep/kimi-linear-an-expressive-efficient-attention-architecture]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/kimi-linear-an-expressive-efficient-attention-architecture.txt`（94726 字符）供引用检索。