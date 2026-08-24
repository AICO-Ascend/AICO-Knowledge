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
> 【图文联合解读】图示在batch=1、16 heads条件下，KDA（紫实线）与DPLR（青虚线）两核随序列长度2K→64K的执行耗时：KDA全程低于DPLR，差距随长度扩大——64K时KDA约30ms，DPLR约58ms，前者快近2倍。两条曲线均呈超线性增长，但KDA斜率更缓。原文借此论证KDA在保留DPLR表达性的同时具备显著的线性复杂度效率优势，且序列越长优势越显著，为后续Table 2的scaling law与端到端训练吞吐收益提供底层算子级证据。

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
> 【图文联合解读】该表列出5档MoE模型的scaling law配置：激活参数653M→1.7B，head/layer由16→24，hidden维度1216→1776，训练token量38.8B→128B，lr随规模递减（2.006e-3→1.371e-3）、batch递增（336→640），上下文长统一4096。下方拟合曲线显示Kimi Linear损失为2.2879·C^(-0.0527)，相较MLA的2.3092·C^(-0.0536)取得约1.16×效率提升。原文以Figure 2核级线性复杂度为底层算子证据，本表承接论证：基于该高效注意力，系统级scaling law更优，为后续端到端吞吐收益与更大规模模型训练提供算力–性能换算依据。

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
> 【图文联合解读】Table 6 以"递推式 o_t ‖ 并行式 O"双栏并置,枚举 13 种注意力机制及作者加粗高亮的 **KDA(ours)**,逐行列出严格数学等价式。

**技术结论**:KDA 递推核为 q_t^T·Diag(α_s)(I−k_s k_s^T)·k_j,较 GLA 的 Diag(α_s) 增入秩-1 修正项 (I−k_s k_s^T),既保留 O(N) 递推效率,又突破线性注意力的表达力上限;并行式 ((Q⊙Γ)(K/Γ)^T⊙M)(I+(K⊙Γ)(K/Γ)^T⊙M^{-1})^{-1}V 与递推式严格等价。红色项标识相对基线的结构增量。

**论文作用**:该表承担"方法谱系定位"——把 KDA 嵌入线性注意力演化树,与 GLA/RWKV7 同代、与 DeltaNet/Comba 同形,为后续训练吞吐、长上下文及 RL 实验的可解释优势提供形式化锚点。

### Table 7 (p.16) ⭐深度解读
![[assets/crops/kimi-linear-an-expressive-efficient-attention-architecture-tab07.png]]
> [!quote] caption
> An overview of different attention mechanisms through the lens of state updating rules and their learning objective under the TTT framework [ 90 ]. We ignore all normalizer terms and activation/kernel functions for brevity.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**【结构/数据】** 该表在 TTT（Test-Time Training）统一视角下，以两列对照 10 种注意力机制：左列为学习目标 ℒ，右列为对应的梯度下降更新规则 S_t = S_{t-1} − ∇_{S_{t-1}} ℒ。按损失形式用横线划为两区——上区（LA、RetNet、Mamba2、GLA、HGRN2）采用 −⟨S^T k, v⟩ 形式加 Frobenius 正则；下区（Longhorn、Comba、RWKV7、GDN、KDA）采用 β_t/2 ‖S^T k_t − v_t‖² 回归损失，并以 β_t 控制步长。

**【关键结论】** KDA（论文方法）与 GDN 目标完全相同，但更新规则中 α_t 的位置不同（图中红框高亮）：GDN 把 α_t 作为标量乘到状态外（α_t S_{t-1}），KDA 改为对角阵 Diag(α_t) 作用于 S_{t-1}，实现**逐通道（per-channel）衰减与遗忘**，而非全局均匀遗忘，因此表达力更强。

**【论文中的作用】** 此表承担方法论定位职能：将 KDA 锚定在线性注意力变体谱系中，论证它是当前最强基线 GDN 最自然的逐通道精细化推广，为后文高效分块算法与实验优势提供统一的理论锚点，支撑"既高效又具表达力"的核心主张。

### Table 8 (p.0) ⭐深度解读
![[assets/crops/kimi-linear-an-expressive-efficient-attention-architecture-tab08.png]]
> [!quote] caption
> Performance of Kimi-Linear-Base and Moonlight-Base across diverse tasks.

> [!tip] 表格解读（多模态）
> 【图文联合解读】表8对比Kimi-Linear-Base与Moonlight-Base在四类任务的性能。两者均为MoE、激活3B参数、训练5.7T token，但Kimi-Linear总参48B远多于Moonlight的16B。Kimi-Linear全面领先：通用TriviaQA 75.2 vs 66.2、MMLU-Pro 54.8 vs 42.4；数学MATH 58.5 vs 45.3；代码CRUXEval-I-cot 61.0 vs 45.9、LiveCodeBench 20.0 vs 14.3；中文C-Eval 83.3 vs 77.6。论文借此论证：相同激活参数与训练量下，Kimi-Linear混合线性注意力架构表达力显著优于纯线性基线，是验证核心方法有效性的关键对照。

### Table 9 (p.28) ⭐深度解读
![[assets/crops/kimi-linear-an-expressive-efficient-attention-architecture-tab09.png]]
> [!quote] caption
> Performance of Kimi-Linear-Instruct and Moonlight-Instruct across diverse tasks.

> [!tip] 表格解读（多模态）
> 【图文联合解读】Table 9 分 Math/Code/Chinese 三类对比 Kimi-Linear-Instruct 与 Moonlight-Instruct。图中具体数据：MATH 58.5 vs 45.3、GSM8k 86.3 vs 77.2、CRUXEval-I-cot 61.0 vs 45.9、LiveCodeBench(v6) 20.0 vs 14.3；原文重点引用的 Chinese 部分：C-Eval（5-shot）83.3 vs 77.6（差 5.7），CSimpleQA（5-shot）53.5 vs 34.7（差 18.8）。原文据此论证 Kimi-Linear-Instruct 在中文知识与推理任务上全面领先 Moonlight-Instruct。该表在论文实验链路中承担多任务综合评测之责，与代码、数学结果共同支撑"线性注意力架构保持高效的同时不损乃至超越基线性能"的核心结论。

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