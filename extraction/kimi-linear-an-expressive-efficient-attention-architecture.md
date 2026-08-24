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
> 【图文联合解读】```thinking
The image is Figure 1(b) from the Kimi Linear paper, showing TPOT (Time Per Output Token, ms) vs Decoding Length (4K to 1M tokens). Three curves: MLA (teal dashed, steep growth), GDN-H (orange, low growth), Kimi Linear (purple, low growth, overlapping with GDN-H). At 1M tokens: Kimi Linear ≈1.84ms vs MLA ≈11.48ms (6.3× speedup). Red arrows mark 4.8×/5.7×/6.3× speedups at 256K/512K/1M.

Need ≤220 Chinese chars covering: 1) quantified data/structure, 2) key technical conclusion from caption/text, 3) role in paper's overall argument chain.
```

**图文联合解读：**

图(b)展示TPOT(ms)随解码长度(4K→1M)的变化曲线：MLA(青色虚线)急剧攀升，1M时达约11.48ms；Kimi Linear(紫色)与GDN-H(橙色)近乎重合且低增长，1M时Kimi仅1.84ms。红色箭头标注256K/512K/1M处相对MLA的加速比依次为4.8×/5.7×/6.3×。

**原文论证结论：** Kimi Linear在长序列解码中维持低TPOT，与GDN-H持平并显著优于MLA，支持更大batch，从而实现端到端推理加速。

**论文作用：** 与(a)图"性能-加速比Pareto前沿"互补，构成"质量不减、速度更优"的双重证据链，是验证Kimi Linear架构实用价值(尤其长上下文场景)的核心实验支撑。

### Figure 2 (p.5) ⭐深度解读
![[assets/crops/kimi-linear-an-expressive-efficient-attention-architecture-fig02.png]]
*整页渲染: ![[assets/kimi-linear-an-expressive-efficient-attention-architecture-p05.png]]*
> [!quote] caption
> Execution time of kernels for vary- ing input lengths, with a uniform batch size of 1 and 16 heads.

> [!tip] 技术解读（多模态）
> 【图文联合解读】图2展示了batch=1、16头条件下，KDA（ours）与DPLR两种注意力内核在输入长度2K–64K（对数刻度）下的执行时间（ms）对比。KDA（紫色实线）从2K约2ms平稳增长至64K约30ms；DPLR（青色虚线）在64K时陡升至约58ms，曲线明显更陡。两者差距随序列长度扩大而显著拉大。

原文借此论证：KDA内核相对DPLR在长序列上具有更优的推理效率与更好的复杂度表现，是论文"expressive yet efficient"核心主张的关键效率证据，支撑Kimi Linear在长上下文场景下的实际部署可行性。

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
> 【图文联合解读】**图文联合解读：**

图4为2×3网格：上行绘制256–2048序列长度下的峰值准确率，下行绘制1K token下20K步训练收敛曲线，对比KDA/GDN/Mamba2在Palindrome、MQAR、Stack三任务表现。数据上，KDA与GDN在短序列均近100%，但KDA约5K步即收敛，GDN需15–20K步；Mamba2于Palindrome（≥512）、Stack（≥1024）即降至0%，完全失效。论文借此论证KDA兼具**快速收敛**与**长序列表达力**，是唯一在三项任务同时有效的方案，为下游真实语言基准评测提供合成任务层面的理论支撑。

### Figure 5 (p.9) ⭐深度解读
![[assets/crops/kimi-linear-an-expressive-efficient-attention-architecture-fig05.png]]
*整页渲染: ![[assets/kimi-linear-an-expressive-efficient-attention-architecture-p09.png]]*
> [!quote] caption
> The fitted scaling law curves for MLA and Kimi Linear. balanced positional bias across layers, which improves robustness and extrapolation at long ranges, leading to stronger long-context performance. Regarding long context performance, as shown in Table 5, Kimi Linear achieves the best average score across different long context benchmarks, which verifies the benefits we claim in the last section

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图中以双对数坐标对比 MLA（蓝，虚线，2.3092·C⁻⁰·⁰⁵³⁶）与 Kimi Linear（红，虚线，2.2879·C⁻⁰·⁰⁵²⁷）在不同算力 C（FLOP/s-days，约 10¹ 量级）下的损失曲线。两曲线斜率相近（衰减指数仅差 0.0009），表明两者随算力提升的收益节奏一致；但 Kimi Linear 曲线整体下移，等损失下算力节省约 **1.16×**。论文借此论证 Kimi Linear 在保持与 MLA 几乎相同 scaling 行为的同时，实现了显著的"常数级"效率优势，从而支撑其作为新注意力架构在长上下文场景中可扩展且更优的结论，是实验链路中验证方法有效性的关键定量证据。

### Figure 6 (p.12) ⭐深度解读
![[assets/crops/kimi-linear-an-expressive-efficient-attention-architecture-fig06.png]]
*整页渲染: ![[assets/kimi-linear-an-expressive-efficient-attention-architecture-p12.png]]*
> [!quote] caption
> The training and test accuracy curves for Kimi Linear@1.4T and MLA@1.4T during Math RL training. Kimi Linear consistently outperforms the full attention baseline by a sizable margin during the whole RL process.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图6核心对象与量化数据**

图6展示双面板折线图，追踪RL训练约20–110步过程中Kimi Linear@1.4T（紫实线）与MLA@1.4T（青虚线）在**(b) MATH 500 Test** 与 **(c) AIME 2025** 两个数学基准上的准确率。可读出关键数值：MATH 500上Kimi Linear收敛至约87–88%，MLA约78–80%，全程领先约6–8个百分点；AIME 2025上Kimi Linear达约22–23%，MLA约19%，领先约3–4个百分点。

**原文论证的关键结论**

Kimi Linear的KDA+MLA混合架构在整个RL阶段始终显著优于纯全注意力基线，证明高效注意力不会损害数学推理能力。

**在论文链路中的作用**

前文已论证训练效率与长上下文优势，此图补全"RL后训练推理能力不退化"的关键实证闭环，为"线性注意力可替代全注意力"这一核心主张提供下游任务维度的支撑。

### Figure 7 (p.13) ⭐深度解读
![[assets/crops/kimi-linear-an-expressive-efficient-attention-architecture-fig07.png]]
*整页渲染: ![[assets/kimi-linear-an-expressive-efficient-attention-architecture-p13.png]]*
> [!quote] caption
> (a) The prefilling time of MLA (full attention), hybrid GDN-H and our Kimi Linear. (b) The time per output token (TPOT) for MLA, GDN-H and Kimi Linear during decoding. (We use batch size = 1 here for tests.) performance curves are virtually indistinguishable, confirming that our method maintains high efficiency. The hybrid

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图(b)为batch=1时TPOT随解码长度（4K→1M，对数刻度）变化曲线：MLA虚线随长度近似线性攀升至~18ms（1M处）；Kimi Linear（紫实线）与GDN-H（橙）几乎重合，1M处仅~8ms；图中标注在512K处提速1.8×、1M处提速2.2×。

**关键结论：** 长序列解码场景下，Kimi Linear较全注意力MLA取得1.8–2.2倍加速，且与GDN-H性能曲线几乎不可区分，说明其用线性注意力取代部分MLA层后，仍保持了类GDN的高效推理特性。

**论文作用：** 与图(a)预填充时延互为补充，从"预填充+解码"两端共同证明Kimi Linear相对MLA的全链路效率优势，是论证该架构具备实际部署价值的关键效率证据。

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.8) ⭐深度解读
![[assets/crops/kimi-linear-an-expressive-efficient-attention-architecture-tab01.png]]
> [!quote] caption
> Ablation study on the hybrid ratio of KDA to MLA attention and other key components. We list the training and validation perplexities (lower is better) for comparison. The best-performing model, used in our final experiments, is highlighted in gray.

> [!tip] 表格解读（多模态）
> 【图文联合解读】表1比较KDA:MLA混合比，指标为训练/验证PPL（↓）：0:1为9.45/5.77，1:1为9.29/5.66，3:1为9.23/5.65，7:1为9.23/5.70，15:1为9.34/5.82。3:1验证PPL最低，训练PPL与7:1并列最低，故选为最终架构。该表承担消融决策，适量引入KDA、保留MLA可兼顾困惑度与长程效率；Figure 1进一步验证1.4T token下MMLU-Pro 51.0、RULER 84.3及1M token时1.84ms对11.48ms。

### Table 2 (p.9) ⭐深度解读
![[assets/crops/kimi-linear-an-expressive-efficient-attention-architecture-tab02.png]]
> [!quote] caption
> Model configurations and hyperparameters for scaling law experiments.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 2 图文联合解读：**

该表列出 5 个 MoE 模型用于缩放律实验的配置：激活参数量从 653M（16 层/16 头/h=1216）递增至 1.7B（24 层/24 头/h=1776），训练 token 数对应从 38.8B 增至 128.0B，batch size 与学习率随之按比例调整（lr 由 2.006×10⁻³ 降至 1.371×10⁻³），上下文长度统一为 4096。

配套散点图显示 Kimi Linear 与 MLA 的 Loss-算力拟合曲线分别为 2.2879·C⁻⁰·⁰⁵²⁷ 与 2.3092·C⁻⁰·⁰⁵³⁶，同等算力下 Kimi Linear 实现约 **1.16× 训练效率提升**，且两种架构遵循相近幂律趋势。

该表是论文"新注意力架构有效性"论证链的关键一环：在控制 MoE 路由、训练配比的前提下，沿 5 个规模点系统对比 MLA 基线，为后文更大规模实验中 Kimi Linear 取代 MLA 提供缩放律层面的可迁移证据。

### Table 3 (p.11) ⭐深度解读
![[assets/crops/kimi-linear-an-expressive-efficient-attention-architecture-tab03.png]]
> [!quote] caption
> Performance comparison of Kimi Linear with the full-attention MLA baseline and the hybrid GDN baseline, all after the same pretraining recipe. Kimi Linear consistently outperforms both MLA and GDN-H on short-context pretrain evaluations. Best per-column results are bolded .

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 3 联合解读：**

**1）核心结构与数据：** 该表在完全一致的预训练配方（1.4T tokens）下，对三类注意力架构——全注意力 MLA、混合 GDN-H、Kimi Linear——在 General / Math & Code / Chinese 三类共 14 项基准上进行横向对比。Kimi Linear 在 12 项上取得最佳（加粗），典型差距如 MMLU-Pro 51.0 vs 47.2（GDN-H）/47.2（MLA），BBH 72.9 vs 71.6/70.6；唯独 EvalPlus 上 GDN-H 以 63.1 领先（Kimi Linear 60.2），MATH 上与 MLA 并列 54.7。

**2）关键结论：** 在相同训练开销下，Kimi Linear 全面优于全注意力 MLA 与现有混合 GDN 基线，证明其线性核 + 有限注意力的混合设计在表达能力上并未折损，反而在短上下文预训练评估中具有一致优势。

**3）在论文中的位置：** 这是"质量—效率"实验链中的受控消融证据，配合后文长上下文评测，共同支撑"Kimi Linear 既高效又不牺牲表达力"的核心论断，是论文验证章节的主表之一。

### Table 4 (p.11) ⭐深度解读
![[assets/crops/kimi-linear-an-expressive-efficient-attention-architecture-tab04.png]]
> [!quote] caption
> Performance comparison of Kimi Linear with the full-attention MLA baseline and the hybrid GDN baseline, all using the same SFT recipe after pretraining. Kimi Linear consistently outperforms both MLA and GDN-H on short-context instruction-tuned benchmarks. Best per-column results are bolded .

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 4 图文联合解读**

该表在相同 1.4T tokens 预训练 + 同 SFT 配方下，对比 MLA（全注意力）、GDN-H（混合 GDN）与 Kimi Linear 三种架构在 12 项短上下文指令微调基准上的表现，分 *General*（BBH、MMLU 家族、GPQA-Diamond、LiveBench）与 *Math & Code*（AIME 2025、MATH500、HMMT 2025、PolyMath-en、LiveCodeBench v6、EvalPlus）两组。

**核心数据**：Kimi Linear 在 10/12 项上取得最佳，如 BBH 69.4、MMLU 77.0、MMLU-Pro 67.4、GPQA-Diamond 62.1、AIME 2025 21.3、HMMT 2025 12.5、PolyMath-en 43.6、LiveCodeBench v6 26.0；仅 LiveBench（GDN-H 46.4）、MATH500（GDN-H 83.0）、EvalPlus（MLA 62.6）落后。

**论文作用**：与 Figure 4 合成任务（验证 KDA 在 Palindrome/MQAR/Stack 上的快速收敛与长程能力）形成"机制→实测"闭环——前者证明 KDA 表达力，后者证明该优势在真实 SFT 评测中切实转化为 SOTA，支撑"Kimi Linear 兼具表达力与效率"的核心主张。

### Table 5 (p.12) ⭐深度解读
![[assets/crops/kimi-linear-an-expressive-efficient-attention-architecture-tab05.png]]
> [!quote] caption
> Comparisons of Kimi Linear with MLA, GDN-H, and Kimi Linear (RoPE) across long-context benchmarks. The last column reports the overall average ( ↑ ). All models is trained on 1.4T tokens. Best per-column results are bolded .

> [!tip] 表格解读（多模态）
> 【图文联合解读】Table 5 在 1.4T token 同训条件下，对比 Kimi Linear 与 MLA、GDN-H、Kimi Linear(RoPE) 四种架构在八项长上下文基准上的表现。Kimi Linear 以 RULER 84.3、MRCR 29.6、HELMET-ICL 90.0、RepoQA 68.5、Long Code Arena-Lib 37.1 及均值 54.5 共六项居首，仅 LongBench V2(35.0)、Frames(58.8)、Code Commit(32.7) 略逊于 MLA。原文据此论证：层间均衡的位置偏置带来更强长程鲁棒与外推，验证 Kimi Linear 在保持线性复杂度的同时实现甚至超越全注意力的长上下文质量，是连接架构设计与消融论证的关键实证。

### Table 6 (p.14) ⭐深度解读
![[assets/crops/kimi-linear-an-expressive-efficient-attention-architecture-tab06.png]]
> [!quote] caption
> An overview of attention mechanisms in their mathematically equivalent recurrent ( o t ) and parallel ( O ) forms. We omitted the normalization term and β t to achieve a more concise representation. The function ϕ refers to the infinite-dimensional feature space corresponding to the exponential kern

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 6 图文联合解读**

Table 6 以双栏（循环形式 oₜ 与并行形式 O）并列展示 12 种注意力机制的数学表达：SA、SA+RoPE、LA、Mamba2、GLA、DeltaNet、FoX、DeltaFormer、PaTH-FoX、GDN、Comba、RWKV7，并以灰底高亮末行的 KDA（ours）。

**核心论证**：KDA 循环式为 Σⱼ qₜᵀ (Πₛ Diag(αₛ)(I−kₛkₛᵀ)) kⱼ vⱼ，并行式为 ((Q⊙Γ)(K/Γ)ᵀ⊙M)(I+(K⊙Γ)(K/Γ)ᵀ⊙M⁻¹)⁻¹V。红色标注揭示 KDA 将 GLA 的逐位置门控 Diag(αₛ) 与 DeltaNet 的 delta 更新规则 (I−kₛkₛᵀ) 统一于同一框架，兼顾表达力与递推效率。

**论文作用**：该表为 KDA 给出严格数学定义并将其定位于线性注意力谱系中，作为概念坐标系，支撑后续 Kimi Linear 三段式（KDA+MLA 混合）架构设计，是方法论部分的"族谱图"。

### Table 7 (p.16) ⭐深度解读
![[assets/crops/kimi-linear-an-expressive-efficient-attention-architecture-tab07.png]]
> [!quote] caption
> An overview of different attention mechanisms through the lens of state updating rules and their learning objective under the TTT framework [ 90 ]. We ignore all normalizer terms and activation/kernel functions for brevity.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 7 图文联合解读**

1）**核心对象与结构**：该表以 TTT（Test-Time Training）框架为统一视角，纵向罗列 10 种注意力机制（LA、RetNet、Mamba2、GLA、HGRN2、Longhorn、Comba、RWKV7、GDN、KDA），横向分两列：左列为对状态 S 的损失目标 ℒ，右列推导出的状态更新规则 S� = Sₜ₋₁ − ∇ℒ。可清晰看出其递进关系——LA 为线性更新；RetNet/Mamba2 引入标量衰减 α；GLA/HGRN2 升级为对角衰减 Diag(αₜ)；Longhorn/Comba/RWKV7/GDN 进一步引入 βₜ、kₜkₜᵀ 修正；最后作者提出的 **KDA** 以 (I − βₜkₜkₜ�) Diag(αₜ) Sₜ₋₁ + βₜkₜvₜᵀ 形式，将对角遗忘与 Kronecker 类门控合二为一。

2）**论证的关键结论**：通过把十余种线性注意力统一到"目标→梯度→更新"三步式，作者表明 KDA 并非孤立设计，而是自然融合了 GDN 的 Kronecker 门控（βₜkₜkₜᵀ 项）与 GLA/HGRN2 的逐通道对角遗忘 Diag(α�)，在表达力上严格优于任一单家族方法。

3）**在论文中的作用**：该表承担理论锚点——承接 TTT 框架综述文献 [90]，为后续 KDA 在 Kimi Linear 架构中替代 MLA 提供形式化依据，并与实验（图 7 的延迟对比）形成"理论统一 + 工程高效"的双重支撑。

### Table 8 (p.28) ⭐深度解读
![[assets/crops/kimi-linear-an-expressive-efficient-attention-architecture-tab08.png]]
> [!quote] caption
> Performance of Kimi-Linear-Base and Moonlight-Base across diverse tasks.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图联合解读（Table 8）**

**① 核心对象与数据：** 表8对比Kimi-Linear-Base与Moonlight-Base，两者同为MoE架构、3B激活参数、训练5.7T token；Kimi总参48B多于Moonlight的16B。在General/Math/Code/Chinese四类共16项基准上，Kimi-Linear全面胜出，如TriviaQA 75.2 vs 66.2、GPQA-Diamond 40.4 vs 35.2、MATH 58.5 vs 45.3、CRUXEval-I-cot 61.0 vs 45.9、C-Eval 83.3 vs 77.6等。

**② 关键结论：** 在激活参数与训练量相同的公平条件下，Kimi-Linear跨任务稳定优于Moonlight，证明其线性注意力架构兼顾效率与表达力，并未因引入线性化而损失下游能力。

**③ 论文作用：** 作为核心定量证据，支撑"Kimi-Linear可替代标准注意力而不损性能"的整体论点，是论文方法有效性论证的关键一环。

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