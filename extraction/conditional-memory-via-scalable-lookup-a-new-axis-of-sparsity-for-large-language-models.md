---
paper_num: "35"
title: "Conditional Memory via Scalable Lookup: A New Axis of Sparsity for Large Language Models"
authors: "A New Axis of Sparsity for Large Language Models Xin Cheng1,2∗, Rui Tian2∗, Wangding Zeng2, Damai Dai2, Qinyu Chen2, Bingxuan Wang2, Zhenda Xie2, Kezhao Huang2, Xingkai Yu2 Chengqi Deng2, Shangyan Zhou2, Chenggang Zhao2,"
date: "2026/1/17"
arxiv: "https://arxiv.org/abs/2601.07372"
pdf: "papers/conditional-memory-via-scalable-lookup-a-new-axis-of-sparsity-for-large-language-models.pdf"
slug: "conditional-memory-via-scalable-lookup-a-new-axis-of-sparsity-for-large-language-models"
tags: []
---

# Conditional Memory via Scalable Lookup: A New Axis of Sparsity for Large Language Models

> [!abstract] 摘要（原文）
> 1\. 💡 论文引入条件记忆作为 LLMs 稀疏性的补充轴，通过 Engram 模块实现，该模块利用现代化的 N-gram 嵌入提供 O(1) 知识查找，以解决 Transformer 在静态知识检索上的低效问题。 2. 🔬 通过对稀疏性分配问题的研究，作者发现 MoE（神经计算）和 Engram（静态记忆）之间存在 U 形缩放定律，混合分配能严格超越纯 MoE，在 iso-parameter 和 iso-FLOPs 的对比下，Engram-27B 在推理、代码和数学任务上表现更优。 3. 🚀 机制分析显示 Engram 有效减轻了早期层级的静态重建负担，从而加深了网络的有效深度并释放了注意力容量以处理全局上下文，实现了卓越的长上下文处理能力，同时其确定性寻址还支持基础设施感知的运行时预取，实现了显著的系统效率。

## 元信息
- **发表日期**: 2026/1/17
- **作者**: A New Axis of Sparsity for Large Language Models Xin Cheng1,2∗, Rui Tian2∗, Wangding Zeng2, Damai Dai2, Qinyu Chen2, Bingxuan Wang2, Zhenda Xie2, Kezhao Huang2, Xingkai Yu2 Chengqi Deng2, Shangyan Zhou2, Chenggang Zhao2,
- **arXiv**: https://arxiv.org/abs/2601.07372
- **本地 PDF**: `papers/conditional-memory-via-scalable-lookup-a-new-axis-of-sparsity-for-large-language-models.pdf`
- **页数**: 35

## 图表（原文 caption + 页码）

### Figure 2 (p.6) ⭐深度解读
![[assets/crops/conditional-memory-via-scalable-lookup-a-new-axis-of-sparsity-for-large-language-models-fig02.png]]
*整页渲染: ![[assets/conditional-memory-via-scalable-lookup-a-new-axis-of-sparsity-for-large-language-models-p06.png]]*
> [!quote] caption
> During training, to accommodate large-scale embedding tables, we employ standard model parallelism by sharding the tables across available GPUs. An All-to-All communication primitive is used to gather active rows in the forward pass and dispatch gradients in the backward pass, enabling the total memory capacity to scale linearly with the number of accelerators.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

**(a) 训练阶段**：图中展示两块 GPU 设备并行计算，底层 Input IDs 经 Vocab Embedding 与 Transformer Block 后分流入两卡，每卡按 Engram → Attention → MoE 顺序堆叠并带残差⊕；两卡 Engram 表之间通过 All2All 通信交换活跃行。

**(b) 推理阶段**：单设备上 Vocab Embedding → Transformer Block → 含 Engram 层（紫色）→ Transformer Block → 含 Engram 层，主机端 Engram 表存于"Memory Hierarchy"，通过 Host Communication 按需加载到 On Device Computation。

**论证结论**：训练通过表分片+All2All 实现容量随加速卡线性扩展；推理通过主机卸载释放设备显存，结合数据复用发挥条件记忆效用。

**论文作用**：该图为 Engram 方法提供系统级可行性证明，是后续 Table 2（Engram-27B 仅 82% FLOPs 即匹配基线 LongPPL）等效率实验的工程基础。

### Figure 5 (p.16) ⭐深度解读
![[assets/crops/conditional-memory-via-scalable-lookup-a-new-axis-of-sparsity-for-large-language-models-fig05.png]]
*整页渲染: ![[assets/conditional-memory-via-scalable-lookup-a-new-axis-of-sparsity-for-large-language-models-p16.png]]*
> [!quote] caption
> We find that three components yield the most significant gains: (i) branch- specific fusion within the multi-branch backbone, (ii) context-aware gating, and (iii) tokenizer compression. Removing any of these causes the largest regressions in validation loss. Specifically, for the “w/o multi branch” ablation, we retain the mHC backbone structure but replace the branch-specific gating with a single 

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

1）**核心对象与数据**：该图以Validation Loss为纵轴（含断轴，1.768–1.808区间），横轴左侧为层索引1–12，右侧为5种消融变体。橙色虚线代表3B MoE Baseline（约1.808），绿色虚线代表完整3B MoE+1.6B Engram（约1.768）；深蓝曲线为单模块插入不同层的扫掠结果，Layer 2处取得最低值≈1.7705，随后单调恶化至Layer 12的≈1.783；右侧×号标注的"w/o multi branch / token compress / gating"、"+4-gram"、"w/o short conv"五种变体loss均高于绿色基线。

2）**关键结论**：Engram需在浅层（如Layer 2）早期注入，深度越深收益越弱；同时证实三大核心组件——分支融合、上下文感知门控、tokenizer压缩——均为必要设计。

3）**论文作用**：该图为架构设计提供经验依据，定位最佳插入位置并验证各模块不可缺，是支撑"条件记忆+稀疏查找"整体方法有效性的关键消融证据。

### Figure 7 (p.18) ⭐深度解读
![[assets/crops/conditional-memory-via-scalable-lookup-a-new-axis-of-sparsity-for-large-language-models-fig07.png]]
*整页渲染: ![[assets/conditional-memory-via-scalable-lookup-a-new-axis-of-sparsity-for-large-language-models-p18.png]]*
> [!quote] caption
> The results demonstrate a distinct pattern of selectivity. The gating mechanism consistently activates (shown in red) upon completing local, static patterns. In English, we observe strong activations on multi-token named entities (e.g., “Alexander the Great”, “the Milky Way”) and formulaic phrases (e.g., “By the way”, “Princess of Wales”). This behavior generalizes effectively across languages. In

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

**核心对象与结构**：图中以热力图展示 Engram 门控标量 α_t∈[0,1]（白→深红）在 5 个句子（含 3 条英文、2 条中文）逐 token 上的取值，采用 N=3 后缀 n-gram。强激活（深红）集中在 "the Great"、"uce phal"、"Milky Way"、"Princess of Wales" 等多 token 命名实体，以及 "By the way" 这类固定短语；中文行则在 "四大 发明"、"造纸术"、"指南针"、"张仲景" 等成语/专名处显著激活。

**关键结论**：门控具有高度选择性——仅在**局部静态模式完成时**触发，而非逐词全开。这验证了条件记忆检索的"按需触发"假设，即 Engram 只对高复用、可枚举的多 token 模式做强记忆读取，且该行为在跨语言（英/中）下保持一致。

**论文链路作用**：该图作为质化证据，与定量检索命中率、困惑度互补，支撑"查找式记忆构成 LLM 稀疏性新维度"的核心论点——通过选择性门控，将稳定的模式化知识从注意力计算中剥离，使模型算力集中于需要组合推理的位置。

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.9) ⭐深度解读
![[assets/crops/conditional-memory-via-scalable-lookup-a-new-axis-of-sparsity-for-large-language-models-tab01.png]]
> [!quote] caption
> | Pre-training performance comparison between dense, MoE, and Engram models . All models are trained for 262B tokens and are matched in activated parameters (3.8B). Engram-27B is iso-parameters with MoE-27B by reallocating parameters from routed experts (72 → 55) to a 5.7B-parameter Engram memory. E

> [!tip] 表格解读（多模态）
> 【图文联合解读】**核心对象与结构**：对比Dense-4B、MoE-27B、Engram-27B、Engram-40B四模型，在相同262B训练token、3.8B激活参数条件下，涵盖语言建模（Pile loss: 2.091/1.960/**1.950**/1.942）、知识推理（MMLU: 48.6/57.4/**60.4**/60.6）、阅读理解、代码数学四类共30+基准。

**关键结论**：将MoE路由专家从72→55，把节省参数重分配给5.7B Engram记忆后，Engram-27B在绝大多数任务上反超MoE-27B；Engram-40B把记忆扩至18.5B，性能进一步单调提升。

**论文作用**：作为核心定量证据，支撑"条件记忆是优于/正交流水线于专家路由的新稀疏轴"这一核心主张，为后续规模化、消融分析奠基。

### Table 2 (p.11) ⭐深度解读
![[assets/crops/conditional-memory-via-scalable-lookup-a-new-axis-of-sparsity-for-large-language-models-tab02.png]]
> [!quote] caption
> | Long-context performance comparison. Parenthetical values (e.g. (50k, 1.62) ) denote the pre-training steps and the corresponding loss prior to the long-context extension. Two key findings: (1) With only 82% of the pre-training FLOPs (41k vs. 50k), Engram-27B matches the baseline’s LongPPL ( Fang 

> [!tip] 表格解读（多模态）
> 【图文联合解读】# Table 2 图文联合解读

**1) 核心对象与数据**
Table 2 对比 32k 长上下文下 MoE-27B 基线（50k 步, loss 1.63）与 Engram-27B 三档配置（41k/1.66、46k/1.63、50k/1.62），共 11 项指标：LongPPL 含 Book/Paper/Code/L-CoT，RULER 含 NIAH-S/MK/MV/MQ 及 VT/CWE/FWE/QA。Engram-50k 在 LongPPL 四项全面最优（4.14/2.82/2.44/13.41）；RULER 关键增益显著——MQ 由 84.2→97.0、VT 由 77.0→89.0、FWE 由 73.0→99.3。

**2) 关键结论**
仅以 82% 预训练 FLOPs（41k vs 50k），Engram 即匹配基线 LongPPL 并在 RULER 上反超；等 loss（46k）与等 FLOPs（50k）条件下 Engram 各项均优于 MoE 基线。

**3) 在论文中的作用**
该表是与 Figure 2（嵌入表模型并行工程可行性）配套的核心效率-有效性证据链，证明 Engram 这一"条件记忆"稀疏轴在长上下文场景兼具算力节省与精度提升，支撑全文核心主张。

### Table 3 (p.13) ⭐深度解读
![[assets/crops/conditional-memory-via-scalable-lookup-a-new-axis-of-sparsity-for-large-language-models-tab03.png]]
> [!quote] caption
> | Entity resolution example reproduced from Ghandeharioun et al. ( 2024 ). This table illustrates how LLMs gradually integrate context tokens through layers of attention and FFNs to construct the internal representation of the entity: “Diana, Princess of Wales” . The “Latent State Translation” colum

> [!tip] 表格解读（多模态）
> 【图文联合解读】**说明**：提供的图片并非 Table 3 本身，而是一段正文（介绍 Engram 通过显式知识查找模拟"模型深度增加"，并使用 LogitLens 与 CKA 两种机制可解释性工具验证该假设）。Table 3 实体内容不可见，以下依据原文 caption 与正文联合解读：

**1）核心对象与结构**：Table 3 复现自 Ghandeharioun et al. (2024) 的实体解析示例，追踪 LLM 各层（含注意力与 FFN）对目标实体 "Diana, Princess of Wales" 的隐状态表示；通过 "Latent State Translation" 列将每层 hidden state 解码为可读词，以观测模型在第几层才"识别出"完整实体身份。

**2）关键论证结论**：用作 Engram 核心假设的机制级证据——证明显式知识查找等效于"增加模型深度"，使早期层跳过基础特征组合，直接获得高层语义。

**3）论文链路作用**：与 LogitLens、CKA 共同支撑"条件记忆 = 新稀疏轴"这一可解释性主张，区别于 MoE/激活稀疏，从知识存储维度论证 Engram 的有效性。

### Table 4 (p.18) ⭐深度解读
![[assets/crops/conditional-memory-via-scalable-lookup-a-new-axis-of-sparsity-for-large-language-models-tab04.png]]
> [!quote] caption
> | End-to-end Inference Throughput . We measure infernece throughput with a 100B- parameter Engram layer entirely offloaded to host memory.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 4 图文联合解读**

表4展示端到端推理吞吐：H800硬件、512序列、长度Uniform(100,1024)下，4B-Dense基线9,031.62 tok/s，叠加CPU offload的100B Engram层仅降至8,858.28；8B-Dense由6,315.52降至6,140.02，降幅仅1.9%~2.8%。结论：Engram条件记忆以近零开销换得25×参数扩展。该表支撑"host-memory查表让LLM变大不变慢"的核心论断，是稀疏性论证的关键实测依据。

### Table 5 (p.33) ⭐深度解读
![[assets/crops/conditional-memory-via-scalable-lookup-a-new-axis-of-sparsity-for-large-language-models-tab05.png]]
> [!quote] caption
> Detailed model architecture information and training hyper parameters.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 5 图文联合解读**

表5对照Dense-4B、MoE-27B、Engram-27B/40B四模型的架构与训练设置：均30层、dim 2560、MLA注意力、RoPE θ=10000、seq 4096、batch 1280、262B tokens、50k步、Muon骨干+Adam嵌入、LR 4e-4、Step Decay；MoE/Engram采用Loss-Free均衡、6激活+2共享专家（路由72/55），首层为Dense。Engram新增dmem=1280、词表22.6M/72.4M、8头、嵌入第[2,15]层、n-gram[2,3]，启用mHC融合、tokenizer压缩、Conv零初始化，并独立用Adam优化、学习率×5。该统一训练配置为论文核心论断提供公平对照基线——证明在相同26.7B激活参预算下，Engram以查找式条件记忆作为**新稀疏轴**可匹配MoE性能，并将记忆由27B扩至40B时继续受益，从而将"条件记忆查找"确立为继MoE之后的第三种稀疏维度。

### Table 6 (p.35) ⭐深度解读
![[assets/crops/conditional-memory-via-scalable-lookup-a-new-axis-of-sparsity-for-large-language-models-tab06.png]]
> [!quote] caption
> | The table illustrates Top-5 merged tokens by Tokenizer Compression and the overall compression ratio is 23.43% for our 128k tokenizer.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

1）该表展示了Tokenizer Compression方法在128k词表上合并频率最高的Top-5归一化token及其对应的原始token：排名第1为空格类`'□'`（163次合并），涵盖`\t`、`\n`、连续空格等空白变体；第2–5名依次为元音`'a'(54)`、`'o'(40)`、`'e'(35)`、`'i'(30)`，各合并大小写、前置空格及带变音符号的字符（如á/ä/ã/â、é/è/ê/ë等）。整体压缩率达23.43%。

2）原文以此论证：压缩并非随机删除，而是优先合并高频冗余变体（空白与元音的大小写、空格前缀、变音符号），保留语义核心，验证方法的有效性与合理性。

3）在论文中，该表为"可扩展查找的条件记忆"提供词表精简的实证依据，是支撑其新稀疏性轴心的关键实验证据之一。

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\text{CKA}(K, L) = \frac{\text{HSIC}(K, L)}{\sqrt{\text{HSIC}(K, K)\text{HSIC}(L, L)}}
$$

$$
a_j = \frac{\sum_{i \in \mathcal{I}_j} S_{i,j} \cdot i}{\sum_{i \in \mathcal{I}_j} S_{i,j}}, \quad \text{where } \mathcal{I}_j = \mathop{\text{argtop}k}_{i} (S_{i,j}).
$$

$$
z_{t,n,k} \triangleq \phi_{n,k}(g_{t,n}), \quad \mathbf{e}_{t,n,k} = \mathbf{E}_{n,k}[z_{t,n,k}].
$$

$$
\mathbf{e}_t \triangleq \mathop{\Vert}_{n=2}^{N} \mathop{\Vert}_{k=1}^{K} \mathbf{e}_{t,n,k}.
$$

$$
\mathbf{k}_t = \mathbf{W}_K \mathbf{e}_t, \quad \mathbf{v}_t = \mathbf{W}_V \mathbf{e}_t
$$

$$
\alpha_t = \sigma\left( \frac{\text{RMSNorm}(\mathbf{h}_t)^\top \text{RMSNorm}(\mathbf{k}_t)}{\sqrt{d}} \right).
$$

$$
\mathbf{Y} = \text{SiLU}\left( \text{Conv1D}( \text{RMSNorm}(\tilde{\mathbf{V}}) ) \right) + \tilde{\mathbf{V}},
$$

$$
\alpha_t^{(m)} = \sigma\left( \frac{\text{RMSNorm}(\mathbf{h}_t^{(m)})^\top \text{RMSNorm}(\mathbf{W}_K^{(m)} \mathbf{e}_t)}{\sqrt{d}} \right).
$$

$$
P_{\mathrm{MoE}}^{(\mathrm{sparse })} = \rho\, P_{\mathrm{sparse}}, \qquad P_{\mathrm{Engram}} = (1-\rho)\, P_{\mathrm{sparse}}.
$$

## 技术点深读（DEEP）

![[deep/conditional-memory-via-scalable-lookup-a-new-axis-of-sparsity-for-large-language-models]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/conditional-memory-via-scalable-lookup-a-new-axis-of-sparsity-for-large-language-models.txt`（100228 字符）供引用检索。