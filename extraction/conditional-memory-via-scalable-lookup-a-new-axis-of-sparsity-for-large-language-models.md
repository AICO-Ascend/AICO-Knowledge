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
> 【图文联合解读】图5展示Engram架构消融：深蓝曲线描绘3B MoE下Engram单模块插入层深（Layer 8–12）对验证损失的影响，呈先微升后回落趋势，结合原文揭示Layer 2早注最优。右栏5个×号标记消融变体：去多分支融合、去token压缩、去门控、加4-gram、去短卷积，分别落于橙虚线（基线）与绿虚线（完整Engram）之间梯度位置。原文借此论证三大核心组件——分支专属融合、上下文感知门控、tokenizer压缩——任一缺失即引最大回归。该图为论文"条件记忆需多组件协同"方法论的关键证据，串联架构设计→消融验证→相对3B MoE全面优越的实验闭环。

### Figure 7 (p.18) ⭐深度解读
![[assets/crops/conditional-memory-via-scalable-lookup-a-new-axis-of-sparsity-for-large-language-models-fig07.png]]
*整页渲染: ![[assets/conditional-memory-via-scalable-lookup-a-new-axis-of-sparsity-for-large-language-models-p18.png]]*
> [!quote] caption
> The results demonstrate a distinct pattern of selectivity. The gating mechanism consistently activates (shown in red) upon completing local, static patterns. In English, we observe strong activations on multi-token named entities (e.g., “Alexander the Great”, “the Milky Way”) and formulaic phrases (e.g., “By the way”, “Princess of Wales”). This behavior generalizes effectively across languages. In

> [!tip] 技术解读（多模态）
> 【图文联合解读】## Figure 7 联合解读

**核心对象与结构**：图以热力图形式展示 Engram 门控机制在多语言文本上的激活分布。颜色越深红表示门控标量 αₜ 越接近 1，每行对应一个 token 序列，N=3 后缀 n-gram 完成后触发。可观察到五行示例：(1) 英文 "…norse Brucephal us." 中 "Bruce" 与 "phalus" 显著激活；(2) "Way." 中 "Way" 激活；(3) "…iana, Princess of Wales." 中 "Princess of Wales" 连续高亮；(4) 中文 "印刷术。" 中 "术" 单独激活；(5) 中文 "…医圣',…《伤寒杂病论》" 中 "医圣"、"《伤寒杂病论》" 等命名实体高亮。

**关键论证结论**：门控机制并非均匀响应，而是呈现高度选择性——仅在**静态、可枚举的局部模式**完成时强烈激活，涵盖英语多 token 命名实体（如 Princess of Wales）与公式化短语；该选择性在中文场景同样成立（"医圣"、《伤寒杂病论》），证实跨语言泛化。

**链路作用**：此图构成 Engram "条件记忆"假设的定性证据，表明查找表能精准捕捉模式补全信号而非全段均匀检索，是后续量化稀疏性增益与推理加速实验的机理基础。

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.9) ⭐深度解读
![[assets/crops/conditional-memory-via-scalable-lookup-a-new-axis-of-sparsity-for-large-language-models-tab01.png]]
> [!quote] caption
> | Pre-training performance comparison between dense, MoE, and Engram models . All models are trained for 262B tokens and are matched in activated parameters (3.8B). Engram-27B is iso-parameters with MoE-27B by reallocating parameters from routed experts (72 → 55) to a 5.7B-parameter Engram memory. E

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 1 图文联合解读**

1) **核心对象与数据**：在 262B tokens、激活参数均为 3.8B 的公平设置下，对比 Dense-4B（4.1B 总参）、MoE-27B（2 共享 + 72 routed/top-6，26.7B）、Engram-27B（72→55 routed，新增 5.7B Engram 记忆，26.7B）和 Engram-40B（记忆扩至 18.5B，39.5B）四个模型。Engram-27B 在 Pile loss（1.950）、Validation（1.622）、MMLU（60.4）、CMMLU（61.9）、BBH（55.9）、GSM8K（60.6）、MATH（30.7）等绝大多数任务上加粗胜出；Engram-40B 进一步把 Pile loss 压至 1.942、MMLU 至 60.6。

2) **关键技术结论**：在等激活参数条件下，把 MoE 的 routed expert 参数量替换为 Engram 条件记忆即可全面超越纯 MoE，且扩大记忆容量（5.7B→18.5B）仍持续获益，验证了"条件查表式记忆"作为新稀疏轴的有效性。

3) **论文作用**：作为全文核心预训练实验基线，直接支撑 Engram=新稀疏性维度这一中心主张，并与后续 scaling/消融形成证据链。

### Table 2 (p.11) ⭐深度解读
![[assets/crops/conditional-memory-via-scalable-lookup-a-new-axis-of-sparsity-for-large-language-models-tab02.png]]
> [!quote] caption
> | Long-context performance comparison. Parenthetical values (e.g. (50k, 1.62) ) denote the pre-training steps and the corresponding loss prior to the long-context extension. Two key findings: (1) With only 82% of the pre-training FLOPs (41k vs. 50k), Engram-27B matches the baseline’s LongPPL ( Fang 

> [!tip] 表格解读（多模态）
> 【图文联合解读】该表对比MoE-27B基线与Engram-27B在32k长上下文下的LongPPL（Book/Paper/Code/L-CoT困惑度）与RULER（NIAH的S/MK/MV/MQ及VT/CWE/FWE/QA）表现，括号标注预训练步数与损失。核心结论：(1)仅用82% FLOPs（41k vs 50k），Engram-27B LongPPL与基线持平，RULER显著更优（如MQ 89.5 vs 84.2、QA 44.0 vs 34.5）；(2)等损失(46k)与等算力(50k)条件下各项指标全面胜出。该表作为关键实验证据，验证"条件记忆+查表稀疏"以更少预训练算力提升长文本建模能力，支撑论文新稀疏性轴的核心主张。

### Table 4 (p.18) ⭐深度解读
![[assets/crops/conditional-memory-via-scalable-lookup-a-new-axis-of-sparsity-for-large-language-models-tab04.png]]
> [!quote] caption
> | End-to-end Inference Throughput . We measure infernece throughput with a 100B- parameter Engram layer entirely offloaded to host memory.

> [!tip] 表格解读（多模态）
> 【图文联合解读】Table 4 展示端到端推理吞吐：硬件 H800、512 序列、长度 Uniform(100,1024)。4B-Dense 基线 9,031.62 tok/s，叠加 100B Engram（CPU offload）降至 8,858.28；8B-Dense 由 6,315.52 降至 6,140.02，降幅仅 1.9%~2.8%。核心结论：Engram 条件记忆以近乎零开销换得参数规模大幅扩展。该表支撑论文"可扩展查表式条件记忆不损推理速度"的核心主张，是稀疏性论证的关键实测依据，证明 host-memory 查表即可让模型"变大"而不牺牲吞吐。

### Table 5 (p.33) ⭐深度解读
![[assets/crops/conditional-memory-via-scalable-lookup-a-new-axis-of-sparsity-for-large-language-models-tab05.png]]
> [!quote] caption
> Detailed model architecture information and training hyper parameters.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

1）**核心对象与数据**：表格列出Dense-4B（4.1B/3.8B总/活跃参数）、MoE-27B（72路由/6激活/2共享专家）、Engram-27B与Engram-40B（总参26.7B/39.5B）四套配置的架构与超参。共享基础：30层、dim 2560、MLA注意力、RoPE θ=10000、mHC扩展率4、seq 4096、vocab 129280、batch 1280、5万步、Muon主干+Adam嵌入、LR 4e-4、Step Decay。Engram专有：dmem=1280、8头、层[2,15]、n-gram[2,3]、合并mHC+tokenizer压缩+Conv零初始化均启用，LR倍率×5、专属Adam。

2）**关键结论**：四模型共用主干超参，唯一变量为Engram模块，证明lookup稀疏性是独立"新轴"；tokenizer压缩、mHC融合、Engram专用优化器的高LR倍率（×5）共同验证了Figure 5所述三大关键组件——分支融合、上下文门控、tokenizer压缩——的必要性。

3）**整体作用**：作为附录配置表，保证全文消融与对比实验可复现，并清晰隔离基线与Engram创新点。

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