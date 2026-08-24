---
paper_num: "64"
title: "Muon is Scalable for LLM Training"
authors: ""
date: "2025/2/24"
arxiv: "https://arxiv.org/abs/2502.16982"
pdf: "papers/muon-is-scalable-for-llm-training.pdf"
slug: "muon-is-scalable-for-llm-training"
tags: [training]
---

# Muon is Scalable for LLM Training

> [!abstract] 摘要（原文）
> Recently, the Muon optimizer based on matrix orthogonalization has demonstrated strong results in training small-scale language models, but the scalability to larger models has not been proven. We identify two crucial techniques for scaling up Muon: (1) adding weight decay and (2) carefully adjusting the per-parameter update scale. These techniques allow Muon to work out-of-the-box on large-scale training without the need of hyper-parameter tuning. Scaling law experiments indicate that Muon achieves $\sim\!2\times$ computational efficiency compared to AdamW with compute optimal training. Based on these improvements, we introduce Moonlight, a 3B/16B-parameter Mixture-of-Expert (MoE) model trained with 5.7T tokens using Muon. Our model improves the current Pareto frontier, achieving better performance with much fewer training FLOPs compared to prior models. We open-source our distributed Muon implementation that is memory optimal and communication efficient. We also release the pretrained, instruction-tuned, and intermediate checkpoints to support future research.

## 元信息
- **发表日期**: 2025/2/24
- **作者**: —
- **arXiv**: https://arxiv.org/abs/2502.16982
- **本地 PDF**: `papers/muon-is-scalable-for-llm-training.pdf`
- **页数**: 19

## 图表（原文 caption + 页码）

### Figure 1 (p.1) ⭐深度解读
![[assets/crops/muon-is-scalable-for-llm-training-fig01.png]]
*整页渲染: ![[assets/muon-is-scalable-for-llm-training-p01.png]]*
> [!quote] caption
> Scaling up with Muon. (a) Scaling law experiments comparing Muon and Adam. Muon is ∼2× more computational efficient than Adam with compute optimal training. (b) The MMLU performance of our Moonlight model optimized with Muon and other comparable models. Moonlight advances the Pareto frontier of performance vs training FLOPs. ∗Corresponding author: zhouxinyu@moonshot.cn[cs.LG] 24 Feb 2025

> [!tip] 技术解读（多模态）
> 【图文联合解读】图(a)给出Muon与AdamW在0.1–10 PFLOP/s-days下的LM loss拟合曲线：Muon(蓝)全程低于AdamW(红)，达相同loss仅需约**0.519×算力**，即~2倍计算效率。(b)将MMLU得分对训练FLOPs散点化，**Moonlight-2.4B-1.2T(≈60.5)**与**Moonlight-2.4B-5.7T(≈70)**均落在或贴近前沿虚线，同算力档优于Qwen-2.5-3B(≈65.5)、OLMo-2-7B(≈63.5)等。作为论文首图，它定量锚定"Muon可扩展且更高效"的核心主张，为后续优化器机制分析与大规模训练奠定结论基础。

### Figure 2 (p.4) ⭐深度解读
![[assets/crops/muon-is-scalable-for-llm-training-fig02.png]]
*整页渲染: ![[assets/muon-is-scalable-for-llm-training-p04.png]]*
> [!quote] caption
> Validation loss curves for AdamW (green), Muon without weight decay (red), and Muon with weight decay (blue).

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图示核心**：横轴为训练迭代(0~66k+)，纵轴为验证损失(2.25~2.55)，对比 AdamW(绿)、Muon 无权重衰减(红)、Muon 带权重衰减(蓝)三条曲线。三者起点均≈2.55；前期(≤49k 步)红线无 WD 下降最快，绿线 AdamW 始终最高；约第 49k 步三线交汇于≈2.275 后蓝线反超，终态约 2.24/2.255/2.26。插图量化差值：第 24k 步时无 WD 领先 0.023，第 66k 步时带 WD 反超 0.017。

**技术结论**：Muon 全程稳定优于 AdamW；但权重衰减在长程训练不可或缺——无 WD 初期收敛更快，却牺牲终态泛化，引入 WD 显著降低最终损失。

**论文作用**：与 Table 2 缩放实验配套，提供 Muon 在 LLM 训练中的消融证据，支撑其可扩展性主张并指导 WD 超参选择。

### Figure 3 (p.7) ⭐深度解读
![[assets/crops/muon-is-scalable-for-llm-training-fig03.png]]
*整页渲染: ![[assets/muon-is-scalable-for-llm-training-p07.png]]*
> [!quote] caption
> Fitted scaling law curves for Muon and AdamW optimizers.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图3以对数横轴PFLOP/s-days（≈10⁻²–10¹）与纵轴LM loss（2.2–4.0）绘制Muon（蓝）与AdamW（红）的拟合标度律曲线，叠加多个模型规模下的实际训练轨迹（浅色实线）。Muon曲线在全程显著低于AdamW：约10 PFLOP/s-days时Muon达~2.23，AdamW约~2.30；低算力端差距更大（Muon~3.3 vs AdamW~3.48）。

**论证结论**：Muon在标度律意义上系统性地更省算力，二者均呈幂律下降且斜率近似，故该优势可外推至更大规模。

**作用**：作为核心实证，将单点对比升级为"整条标度律对比"，是支撑"Muon可扩展至LLM训练"主张的关键证据，衔接Table 3参数与正文结论。

### Figure 4 (p.10) ⭐深度解读
![[assets/crops/muon-is-scalable-for-llm-training-fig04.png]]
*整页渲染: ![[assets/muon-is-scalable-for-llm-training-p10.png]]*
> [!quote] caption
> SVD entropy of weight matrices across different training iterations. We categorize the weight matrices into 6 different groups: 1) AttnQO denotes the weight matrices related to the query and output projection in the attention layer; 2) AttnKV denotes the weight matrices related to the key and value projection in the attention layer; 3) Experts denotes the weight matrices in expert models; 4) Share

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

1. **核心对象与结构**：图展示六类权重矩阵（AttnQO、AttnKV、Experts、SharedExperts、Router、Dense）在约0–40K训练迭代下的SVD熵演化，蓝色为Muon、红色为AdamW。

2. **量化结论**：Muon在全部六组熵值均高于AdamW，例如AttnQO终点约0.88 vs 0.82，Router约0.90 vs 0.78，SharedExperts约0.93 vs 0.90；AdamW早期出现显著凹陷（最低跌至0.69，Router组）后部分回升，Muon则自高位平稳略降。

3. **论文作用**：该图以谱分析直接论证Muon的正交化更新有效抑制权重矩阵的秩坍塌，保持奇异值分布均衡，从而维护模型表达能力，是支撑"Muon可扩展至LLM训练"这一核心论断的关键谱性质证据。

### Figure 5 (p.15) ⭐深度解读
![[assets/crops/muon-is-scalable-for-llm-training-fig05.png]]
*整页渲染: ![[assets/muon-is-scalable-for-llm-training-p15.png]]*
> [!quote] caption
> Optimization Landscapes for Scaling Law Hyper-parameters Across FLOPs Budgets

> [!tip] 技术解读（多模态）
> 【图文联合解读】该图展示Muon优化器在5个FLOPs预算（1.0e+20~1.1e+21）下三组超参扫描的Loss景观：左图为Loss随训练token数（~1.5e9~6e9）单调下降；中图为Loss随学习率（0.0006~0.0014）呈平坦U形曲线，最优点集中在0.0008~0.0010；右图为Loss随batch size（200~900）单调上升，最小值出现在各FLOPs预算的左端。关键结论：最优学习率跨预算近乎恒定，最优batch size随FLOPs预算增大而增大。该图经验性地证明Muon超参可沿FLOPs预测性扩展，支撑论文"scaling law超参可稳定外推"的核心论点，为后续表5 scaling law拟合提供数据基础。

### Figure 6 (p.15) ⭐深度解读
![[assets/crops/muon-is-scalable-for-llm-training-fig06.png]]
*整页渲染: ![[assets/muon-is-scalable-for-llm-training-p15.png]]*
> [!quote] caption
> D

> [!tip] 技术解读（多模态）
> 【图文联合解读】**Figure 6 联合解读**

**核心对象**：MoE 门控缩放因子的 Python 实现。函数 `calc_gate_scaling_factor(num_experts, topk, iter_times)` 对 `num_experts` 维高斯 logits 经 sigmoid、排序后截取 top‑k、归一化得到概率向量 p；缩放因子即 `1/‖p‖₂`（p 的 ℓ₂ 范数倒数），经 `iter_times` 次蒙特卡洛采样取均值返回。

**论证结论**：Muon 优化器应用于 MoE 路由场景时，门控输出须乘以 `1/‖p‖₂`，才能保证经 Newton‑Schulz 正交化后的更新等价于谱范数归一化，从而维持 Muon 的尺度不变性前提。

**链路作用**：该图为论文将 Muon 从稠密 LLM 扩展至 MoE 架构提供了可复现的数值校准实现，与 Table 6 中预训练/SFT 阶段优化器互换实验互为支撑，闭环证明 Muon 在稀疏路由下的可扩展性。

### Figure 7 (p.17) ⭐深度解读
![[assets/crops/muon-is-scalable-for-llm-training-fig07.png]]
*整页渲染: ![[assets/muon-is-scalable-for-llm-training-p17.png]]*
> [!quote] caption
> Training dynamics comparison between Moonlight and Moonlight-A

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图7 联合解读：**

该图含4子图，对比Moonlight（蓝，原始Muon）与Moonlight-A（红，改进版）在~37k迭代内的训练动态。(a) 训练Loss：两者均从~2.20下降至~1.95，Moonlight略低；(b) 梯度范数：Moonlight-A在~12k、17k等处出现尖峰（高达1.0），Moonlight更平稳；(c) 第1层最大Attention Logit：Moonlight从~20飙升至~120（20k步附近）再回落，Moonlight-A稳定在20–30；(d) 大Logit占比：Moonlight在15k–25k间突增达1.4×10⁻⁴，Moonlight-A全程近零。

**技术结论：** Muon优化器会导致训练中注意力Logit异常膨胀及大值集中（attention sink问题），而Moonlight-A通过权重衰减改进有效抑制了该现象，同时保持相近Loss。该图是论文"Muon可扩展性"论证的关键实验支撑，证明了修正后方法的训练稳定性优于基线。

### Figure 8 (p.9) ⭐深度解读
![[assets/crops/muon-is-scalable-for-llm-training-fig08.png]]
*整页渲染: ![[assets/muon-is-scalable-for-llm-training-p09.png]]*
> [!quote] caption
> 6.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图8为散点图，横轴为训练FLOPs（对数尺度，2e22–2e24），纵轴为GSM8k分数（10–90），蓝色虚线表示GSM8k性能前沿。两个Moonlight模型（红星★）位置突出：**Moonlight-2.4B-1.2T**在约2e22 FLOPs下得46分，**Moonlight-2.4B-5.7T**在约8e22 FLOPs下得77分，均位于同算力区间主流模型（Qwen-2.5-3B得79、OLMo-2-7B得68、LLaMA-3.1-8B得57、DeepSeek-V3-Small-2.4B仅31等）之上并紧贴前沿曲线。

**技术结论：** Muon优化器使Moonlight以显著更低的训练算力，匹配甚至超越参数量相近的Qwen、OLMo、LLaMA等模型，验证了Muon在大规模LLM训练中的算力效率与可扩展性。

**论文作用：** 该图是"Muon可扩展"主张的核心实证之一，配合Table 8的RMS分析，从下游任务性能维度为Muon取代AdamW提供直接定量支撑。

### Figure 9 (p.18) ⭐深度解读
![[assets/crops/muon-is-scalable-for-llm-training-fig09.png]]
*整页渲染: ![[assets/muon-is-scalable-for-llm-training-p18.png]]*
> [!quote] caption
> Distribution of singular values for each weight matrix in the attention layers. We use WC to denote the weight matrices at each layer that compress the hidden states to the shared latent spaces for keys and values, WV to denote the weight matrices up-projecting the values from the latent space, WO to denote the output projection matrices, and WKR, WKC, WQR and WQC to denote the projection matrices

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读（≤220字）：**

1) **结构与数据**：该图为7×27=189子图的网格矩阵，行对应7类注意力层权重矩阵（WC压缩K/V共享潜空间、WKC/WKR带/不带RoPE的K投影、WO输出投影、WQC/WQR带/不带RoPE的Q投影、WV值上投影），列对应L1–L27共27层。每子图含两条奇异值谱曲线——红为AdamW、蓝为Muon；红框标记Muon奇异值熵低于AdamW的层。

2) **关键结论**：Muon在大多数注意力矩阵上产出更陡峭、更集中（低熵）的奇异值谱——尤其WQC、WQR行几乎全层红框，WO行多数红框，WV行也有较多——表明Muon隐式正则化于低秩解，对查询/输出投影尤为明显。

3) **论文作用**：从谱结构视角解释Muon优于AdamW的内在机理，作为机制分析的核心证据嵌入论文"现象→原因→性能"的完整论证链。

### Figure 10 (p.19) ⭐深度解读
![[assets/crops/muon-is-scalable-for-llm-training-fig10.png]]
*整页渲染: ![[assets/muon-is-scalable-for-llm-training-p19.png]]*
> [!quote] caption
> Distribution of singular values for each weight matrix in the feed-forward network (FFN) layers. We use WI, WV and WO to denote the weight matrices involved in the FFN layer with SwiGLU activation function, where WI represents the input projection to the Swish1 function, WV represents the extra input projection interacting with Swish1 activations, and WO represents the output projection. We use E0

> [!tip] 技术解读（多模态）
> 【图文联合解读】**1) 核心对象与结构**
图为 16×26 的网格热力可视化：行 = 4 个专家(E0–E3)各 × {WO, WI, WV} + 共享专家 SE 的三投影 + 路由器 RW，共 16 行；列 = L2–L27 共 26 层。每格两条排序奇异值衰减曲线，红=AdamW、蓝=Muon；红框标注 Muon 奇异值熵更低的格（图中约数十处，集中在 E0WO、E1WO、SEWO 等少数投影的浅层与末层）。

**2) 关键结论**
Muon 经 Newton–Schulz 正交化后，其训练得到的 FFN 权重矩阵奇异值谱整体更陡峭、低秩特征更显著，与 AdamW 产生系统性差异，且在不同专家/投影/层上差异并不均匀。

**3) 在论文中的作用**
作为机理证据，从权重内部谱结构层面解释 Muon 相对 AdamW 的损失/性能优势，与论文"Muon 可规模化训练 LLM"的核心主张形成实验-机理闭环。

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.6) ⭐深度解读
![[assets/crops/muon-is-scalable-for-llm-training-tab01.png]]
> [!quote] caption
> Controlling Muon’s Update RMS Across Different Model Params

> [!tip] 表格解读（多模态）
> 【图文联合解读】**表1图文联合解读：**

表1对比Baseline、Update Norm、Adjusted LR三种方法在训练loss、验证loss、查询权重RMS与MLP权重RMS上的表现：Update Norm将验证loss由2.812降至**2.789**，但MLP权重RMS从2.52e-2飙升至5.01e-2（约2倍），查询权重RMS也由3.586e-2升至4.918e-2，参数间RMS严重失衡；Adjusted LR在保持val loss=**2.789**的同时，将权重RMS拉回基线附近（3.496e-2 / 4.89e-2）。

该表论证了Muon规模化训练的核心结论：直接归一化更新虽能降损，但会破坏不同参数类型的更新RMS平衡，需按参数类型（如attention/MLP）调整学习率以稳定权重规模——这是论文提出Moonlight模型参数级自适应预处理的关键实验支撑。

### Table 2 (p.7) ⭐深度解读
![[assets/crops/muon-is-scalable-for-llm-training-tab02.png]]
> [!quote] caption
> Scaling Law Models and Hyper-Parameters

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 2 联合解读**

1) **核心对象与数据**：表格列出5个规模档（399M / 545M / 822M / 1.1B / 1.5B，不含Embedding参数）模型的超参配置——Head=Layer=(12→20)、Hidden=(1536→2560)、Tokens=(8.92B→38.91B)、LR≈(9.503e-4 → 8.305e-4，随规模微降)、Batch Size=(96→256，以8K上下文样本计数)。五档规模在深度、宽度、数据量上同步放大。

2) **论证结论**：作为Figure 2缩放律实验的配置清单，表明Muon在各档规模下复用相近的学习率量级（约8e-4–1e-3），无需随模型变大做大幅调参，印证其对规模的兼容性/稳定性。

3) **整体作用**：该表是论文"Muon可规模化"主张的实验骨架——通过统一架构族在1.5B规模内与AdamW（见同图红/蓝损失曲线对比）做同等条件benchmark，为后续"Muon优于AdamW且可扩展"的结论提供可复现的依据。

### Table 3 (p.7) ⭐深度解读
![[assets/crops/muon-is-scalable-for-llm-training-tab03.png]]
> [!quote] caption
> Fitted parameters of the scaling law curves

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

**核心对象与数据**：表格呈现 LM loss（seqlen=8K）随计算量 C 的幂律拟合 L = A·C^(-α)。Muon 的前因子 A=2.506、指数 α=0.052；AdamW 对应为 2.608 与 0.054。两式形式相同，但 Muon 的 A 显著更低（差≈4%），指数仅微浅（0.052 vs 0.054）。

**关键技术结论**：Muon 与 AdamW 共享几乎一致的 scaling 斜率（α≈0.053），说明两者随算力增长呈现**可预测、平行的下降趋势**；但 Muon 整条曲线在任意 C 处都**系统性下移**，即同等算力下损失更低。这从量化角度印证 Figure 3 曲线结论。

**论文链路作用**：作为 Figure 3 的参数化补充，将"曲线更优"的可视化证据转化为可外推的数学表达，证明 Muon 并非局部 trick 而是具备与 AdamW 同等的可扩展性，从而支撑"Muon is scalable for LLM training"的核心主张。

### Table 4 (p.8) ⭐深度解读
![[assets/crops/muon-is-scalable-for-llm-training-tab04.png]]
> [!quote] caption
> Comparison of different models at around 1.2T tokens.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 4 图文联合解读**

**1) 核心结构与数据**：表格在相同规模（激活2.24B / 总参15.29B，不含embedding）和相近token量（DSV3-Small 1.33T，Moonlight两版均1.2T）下，对比三组模型——DSV3-Small、AdamW基线 Moonlight-A@1.2T 与 Muon 版 Moonlight@1.2T，覆盖英、中、代码、数学四类共11个基准。Muon版在多数项领先：MMLU 60.4、MMLU-pro 28.1、HumanEval 37.2、MBPP 52.9、GSM8K 45.0、MATH 19.8、CMath 60.2、C-Eval 59.9、CMMLU 58.8。

**2) 关键结论**：原文指出，Moonlight-A 已强于同级公开模型；换上 Muon 后进一步显著超越基线，证明 Muon 在大模型上的**可扩展性**；尤其在 **Math 与 Code** 类任务上提升最为突出（如 HumanEval 由 29.3→37.2，MATH 由 16.1→19.8）。

**3) 论文中的作用**：该表是 Muon 大规模有效性的**核心实证支点**，承上（消融、缩放实验）启下（Table 5 在 5.7T token 上与 Llama3-3B、Qwen2.5-3B 等公开 3B 模型对标），构成"Muon 可规模化"主张的关键一环。

### Table 5 (p.9) ⭐深度解读
![[assets/crops/muon-is-scalable-for-llm-training-tab05.png]]
> [!quote] caption
> Comparison of different models on various benchmarks.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 5 图文联合解读：**

表5横向对比Llama3.2-3B、Qwen2.5-3B、DSV2-Lite与Moonlight四款~3B级模型在英文（MMLU/BBH等）、代码（HumanEval/MBPP）、数学（GSM8K/MATH/CMath）、中文（C-Eval/CMMLU）共12项基准的表现。

**核心控制变量**：DSV2-Lite与Moonlight架构完全相同（激活参2.24B、总参15.29B、训练token 5.7T），唯一差异是优化器——前者AdamW，后者Muon。

**关键结论**：Moonlight在11/12项基准大幅领先DSV2-Lite，如MMLU 70.0 vs 58.3、HumanEval 48.1 vs 29.9、MATH 45.3 vs 17.1、C-Eval 77.2 vs 60.3；且训练token仅为Llama3.2-3B的63%、Qwen2.5-3B的32%即实现超越。该表是论文的核心消融实证：相同架构与训练预算下，Muon显著提升LLM训练效率与最终质量，论证其作为AdamW可规模化替代方案的有效性。

### Table 6 (p.10) ⭐深度解读
![[assets/crops/muon-is-scalable-for-llm-training-tab06.png]]
> [!quote] caption
> Examining the impact of optimizer interchangeability between pretraining and SFT phases.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

该表以 Moonlight-1.2T 为载体，横向对比四种"预训练+SFT 优化器"组合（Muon/Muon、AdamW/Muon、Muon/AdamW、AdamW/AdamW）在 MMLU、HumanEval、MBPP、GSM8K 四个基准上的表现。结果显示 **Muon→Muon 全链路最优**：MMLU 55.7、HumanEval 57.3、MBPP 55.6、GSM8K 68.0，全面领先；而 AdamW→AdamW 组合在多数项垫底（50.2–64.6）；两种混合方案介于其间，且采用 Muon 预训练的两列（55.6–68.0、55.2–64.9）整体优于 AdamW 预训练两列，表明**预训练阶段选用 Muon 的收益大于 SFT 阶段**。该表作为论文"优化器可互换性"章节的核心实验证据，支撑其关键结论：Muon 的优势可贯穿预训练到 SFT 完整管线，无需中途切换为 AdamW，从而夯实"Muon 可规模化替代 AdamW"的主张。

### Table 7 (p.10) ⭐深度解读
![[assets/crops/muon-is-scalable-for-llm-training-tab07.png]]
> [!quote] caption
> Comparison of Adam and Muon optimizers applied to the SFT of the Qwen2.5-7B pretrained model.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 7 联合解读**

**①核心对象与数据**：表对比Qwen2.5-7B预训练模型在SFT阶段使用Muon vs AdamW的效果，列出4项基准——MMLU(0-shot CoT)、HumanEval(Pass@1)、MBPP(Pass@1)、GSM8K(5-shot EM)。加粗最优值55.7 / 57.3 / 55.6 / 68.0对应"Muon预训练+Muon SFT"组合；单用Muon做SFT(配合Muon预训练)取得最佳，明显优于Muon+AdamW(50.2/52.4/55.2/64.9)与AdamW+AdamW(52.0/53.1/55.2/64.6)配置。

**②关键结论**：结合3.5.2节——实验以tulu-3-sft-mixture、8k序列、余弦LR(2e-5→2e-6)微调Qwen2.5-7B，证实Muon-SFT与Adam-SFT性能持平甚至略优；但Muon真正的增益发生在预训练阶段，而非SFT阶段。

**③在论文链路中的作用**：作为Muon适用边界的"反证实验"，呼应第3节Moonlight的预训练结论，划清Muon作为"预训练可扩展优化器"的方法定位，避免读者误用至SFT场景。

### Table 8 (p.14) ⭐深度解读
![[assets/crops/muon-is-scalable-for-llm-training-tab08.png]]
> [!quote] caption
> Muon Update RMS Experiments

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图像内容说明**：图中最下方仅显示表格标题"Table 8: Muon Update RMS Experiments"，表格具体数值（loss/RMS数据）未在裁图中呈现，故主要依据文字段落解读。

**联合解读**：

该表实验对象为小模型上 Muon 优化器在 Update RMS 五档设置 [0.05, 0.1, 0.2, 0.4, 0.8] 下的表现，以 AdamW 为基线，报告 2k 步（约 2B tokens）时的 loss 与代表性权重矩阵 RMS。上方推导给出理论依据：Muon 更新矩阵 X=U·V 的 RMS² = r/(mn)，满秩时为 √(1/n)。

**关键结论**：0.2 与 0.4 RMS 设置表现相近且显著优于其余档位；这与 AdamW 更新 RMS 经验上落在 0.2~0.4 区间相吻合，验证"对齐 Muon 与 AdamW 更新尺度"可获得更优损失。论文据此将 Muon 更新 RMS 固定为 **0.2**，作为后续大规模实验（如 Moonlight、Moonshot）的标准超参。

**论文链路作用**：承接 §2.2 提出"对齐 AdamW update RMS"的动机假设，以小规模消融提供经验佐证，为主实验中 Muon 的实现细节定调，构成"理论分析→小规模消融→大规模生产"的完整证据链中的一环。

### Table 9 (p.14) ⭐深度解读
![[assets/crops/muon-is-scalable-for-llm-training-tab09.png]]
> [!quote] caption
> Empirical Relationships Between Scaling Law Parameters and Computational Budget (FLOPs)

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 9 图文联合解读：**

**1) 核心对象与数据：** 表展示6种优化器配置（AdamW基线 + 5个控制RMS的Muon变体：0.05/0.1/0.2/0.4/0.8 RMS）在LM训练/验证损失、AttnQ与Mlp层权重RMS上的对比。其中0.2 RMS取得最低训练损失3.198，0.4 RMS取得最低验证损失3.314；而RMS越大，权重RMS从5.74e-3升至7.23e-2。

**2) 关键结论：** 论文在B节明确指出，表9记录的是**在固定FLOPs预算C下，针对AdamW系统搜索最优模型规模N、训练token数D、学习率η、批量大小B**的缩放律参数结果，为后续Muon对比提供公平基线。

**3) 链路作用：** 该表是**AdamW基线缩放律校准**的关键步骤，确保在等算力约束下对比Muon与AdamW，排除超参选择对结论的干扰，支撑"Muon可扩展"的核心论断。

### Table 10 (p.17) ⭐深度解读
![[assets/crops/muon-is-scalable-for-llm-training-tab10.png]]
> [!quote] caption
> Comparison of different models on various benchmarks.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

表格将 Moonlight（2.24B 激活参数 / 15.29B 总参数，Muon 优化器，仅 5.7T token）与 LLAMA3.1-8B、Gemma2-9B、Qwen2.5-7B 三款 7–9B 模型（AdamW，15–18T token）在英/代码/数学共 8 项基准上对照。Moonlight 以更少的激活参数和训练 token，在 MMLU（70.0 vs 66.7）、BBH（65.2 vs 57.7）、GSM8K（77.4 vs 57.2）、MATH（45.3 vs 20.3）等多项显著超越 LLAMA3.1-8B，与更大的 Gemma2-9B、Qwen2.5-7B 亦具竞争力。论文借此实证 Muon 优化器的可扩展性——能以更低算力达到主流优化器训练大模型的水平，是全文"Muon 可规模化"核心论点的关键支撑。

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
H(\sigma) = -\frac{1}{\log n}\sum_{i=1}^n \frac{\sigma^2_i}{\sum_{j=1}^n \sigma^2_j} \log \frac{\sigma^2_i}{\sum_{j=1}^n \sigma^2_j} \notag
$$

$$
\mathbf{M}_t &= \mu \mathbf{M}_{t-1} + \nabla\mathcal{L}_t(\mathbf{W}_{t-1}) \notag \\ \mathbf{O}_t &= \text{Newton-Schulz}(\mathbf{M}_t)\text{\footnotemark[1]} \\ \mathbf{W}_t &= \mathbf{W}_{t-1} - \eta_t \mathbf{O}_t \notag
$$

$$
\mathbf{X}_k &= a \mathbf{X}_{k-1} + b (\mathbf{X}_{k-1} \mathbf{X}_{k-1}^\mathrm{T}) \mathbf{X}_{k-1} + c (\mathbf{X}_{k-1} \mathbf{X}_{k-1}^\mathrm{T})^2 \mathbf{X}_{k-1}
$$

$$
\mathbf{W}_t = \mathbf{W}_{t-1} - \eta_t (\mathbf{O}_t + \lambda \mathbf{W}_{t-1})
$$

$$
\mathbf{W}_t = \mathbf{W}_{t-1} - \eta_t (0.2\cdot\mathbf{O}_t\cdot\sqrt{\max(A,B)} + \lambda \mathbf{W}_{t-1})
$$

$$
\mathbf{W}_t = \mathbf{W}_{t-1} - \eta_t (0.2\cdot\mathbf{O}_t\cdot\sqrt{H} + \lambda \mathbf{W}_{t-1})
$$

$$
\mathbf{W}_t = \mathbf{W}_{t-1} - \eta_t (0.2\cdot\mathbf{O}_t/\mathop{\text{RMS}}(\mathbf{O}_t) + \lambda \mathbf{W}_{t-1})
$$

## 相关论文

- [[scalable-training-of-mixture-of-experts-models-with-megatron-core]] — Scalable Training of Mixture-of-Experts Models with Megatron Core
- [[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]] — From ATOP to ZCube: Automated Topology Optimization Pipeline and A Highly Cost-Effective Network Topology for Large Model Training
- [[zero-memory-optimizations-toward-training-trillion-parameter-models]] — ZeRO: Memory Optimizations Toward Training Trillion Parameter Models
- [[gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints]] — GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints
- [[megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism]] — Megatron-LM: Training Multi-Billion Parameter Language Models Using Model Parallelism
- [[efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey]] — Efficient Training of Large Language Models on Distributed Infrastructures: A Survey

## 技术点深读（DEEP）

![[deep/muon-is-scalable-for-llm-training]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/muon-is-scalable-for-llm-training.txt`（55936 字符）供引用检索。