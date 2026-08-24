---
paper_num: "27"
title: "BERTopic: Neural topic modeling with a class-based TF-IDF procedure"
authors: "Maarten Grootendorst maartengrootendorst@gmail.com"
date: "2026/1/19"
arxiv: "https://arxiv.org/abs/2203.05794"
pdf: "papers/bertopic-neural-topic-modeling-with-a-class-based-tf-idf-procedure.pdf"
slug: "bertopic-neural-topic-modeling-with-a-class-based-tf-idf-procedure"
tags: []
---

# BERTopic: Neural topic modeling with a class-based TF-IDF procedure

> [!abstract] 摘要（原文）
> 1\. 💡 BERTopic 提出了一种新的主题建模方法，通过使用预训练的 Transformer 模型生成文档嵌入，对这些嵌入进行聚类，并采用一种类别的 TF-IDF (c-TF-IDF) 过程来提取连贯的主题表示。 2. ⚙️ 该模型首先利用 SBERT 框架生成文档嵌入，然后使用 UMAP 对其进行降维并通过 HDBSCAN 进行聚类，最终通过创新的 c-TF-IDF 机制为每个文档簇生成主题关键词。 3. 🏆 实验证明 BERTopic 在主题一致性和多样性方面表现出色，与现有模型相比具有竞争力，并且其灵活的架构允许在文档嵌入和主题表示阶段进行独立优化，也支持动态主题建模。

## 元信息
- **发表日期**: 2026/1/19
- **作者**: Maarten Grootendorst maartengrootendorst@gmail.com
- **arXiv**: https://arxiv.org/abs/2203.05794
- **本地 PDF**: `papers/bertopic-neural-topic-modeling-with-a-class-based-tf-idf-procedure.pdf`
- **页数**: 10

## 图表（原文 caption + 页码）

### Figure 1 (p.7) ⭐深度解读
![[assets/crops/bertopic-neural-topic-modeling-with-a-class-based-tf-idf-procedure-fig01.png]]
*整页渲染: ![[assets/bertopic-neural-topic-modeling-with-a-class-based-tf-idf-procedure-p07.png]]*
> [!quote] caption
> Computation time (wall time) in seconds of each topic model on the Trump dataset. Increasing sizes of vocabularies were regulated through selection of documents ranging from 1000 documents until 43000 documents with steps of 2000. Left: computational results with CTM. Right: computational results without CTM as it inﬂates the y-axis making differentiation between other topic models difﬁcult to vis

> [!tip] 技术解读（多模态）
> 【图文联合解读】1) 两子图对比9个主题模型在Trump数据集上的墙钟耗时（秒），横轴为词汇量≈2500–18000（由文档数1000→43000调控）。左图含CTM-MPNET（紫），随词量陡升至~1500s，其余8模型均<100s；右图剔除CTM后y轴缩至0–100s：NMF（棕）最快~33s，LDA~45s，Top2Vec-MPNET（灰）与BERTopic-MPNET（绿）最高达~95–100s。

2) 论证BERTopic（非MPNET变体）效率可比LDA/NMF，并显著优于CTM等神经主题模型；CTM极端耗时会掩盖其他模型差异。

3) 为BERTopic的类TF-IDF流程提供可扩展性证据，支撑其"质量+效率"双重卖点，奠定后文主题质量比较的可行性前提。

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.5) ⭐深度解读
![[assets/crops/bertopic-neural-topic-modeling-with-a-class-based-tf-idf-procedure-tab01.png]]
> [!quote] caption
> Ranging from 10 to 50 topics with steps of 10, topic coherence (TC) and topic diversity (TD) were calculated at each step for each topic model. All results were averaged across 3 runs for each step. Thus, each score is the average of 15 separate runs.

> [!tip] 表格解读（多模态）
> 【图文联合解读】图中未呈现Table 1的实际数值，仅显示其caption与5.3节正文段落。据caption，该表记录各主题模型在10–50个主题（步长10）下的TC（topic coherence）与TD（topic diversity）得分，每个数值是5档×3次共15次运行的均值。

正文表明，TC/TD是评估主题质量的代理指标，结合NPMI用于横向对比BERTopic与LDA、CTM、Top2Vec等基线在一致性与多样性上的表现；同时指出NPMI与人类判断的相关性可能仅对经典模型成立，对神经主题模型未必可靠。

该表作为§5.3 Evaluation的核心量化结果，支撑BERTopic在主题质量与多样性上的相对优势论证，回应引言中"提升一致性同时保留多样性"的核心主张。

### Table 2 (p.6) ⭐深度解读
![[assets/crops/bertopic-neural-topic-modeling-with-a-class-based-tf-idf-procedure-tab02.png]]
> [!quote] caption
> Using four different language models in BERTopic, coherence score (TC) and topic diversity (TD) were calculated ranging from 10 to 50 topics with steps of 10. All results were averaged across 3 runs for each step. Thus, each score is the average of 15 separate runs.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**说明**：图像中 Table 2 的标题与 6.1、6.3 节正文清晰可见，但表格的数值内容并未呈现于该截图中，故数值细节仅依据原文 caption 推断。

---

**图文联合解读（≤220字）**

**1) 表格结构（基于 caption）**：行为 4 种语言模型，列为主题一致性（TC）与主题多样性（TD），主题数从 10 到 50、步长 10，每格为 3 次运行均值（共 15 次）。

**2) 支撑的关键技术结论**：在 6.2 节（"mains competitive regardless of the embedding model"）语境下，该表用以论证 BERTopic 对嵌入模型选择不敏感——因其将文档嵌入与词-主题分布构建解耦，嵌入步骤可灵活替换。

**3) 在论文整体链路中的作用**：作为"模块化设计"主张的实证依据，衔接 6.1 节整体性能对比与 6.3 节动态主题建模的灵活性论述，凸显 BERTopic 方法的工程可替换性。

### Table 3 (p.6) ⭐深度解读
![[assets/crops/bertopic-neural-topic-modeling-with-a-class-based-tf-idf-procedure-tab03.png]]
> [!quote] caption
> The topic coherence (TC) and topic diversity (TD) scores were calculated on dynamic topic model- ing tasks. The TC and TD scores were calculated for each of the 9 timesteps in each dataset. Then, all results were averaged across 3 runs for each step. Thus, each score represents the average of 27 val

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读**

该表对比 **LDA Sequence、BERTopic、BERTopic-Evolve** 三种方法在**动态主题建模（DTM）**任务上的 **TC（主题一致性）** 与 **TD（主题多样性）** 得分，每个数值为 9 个时间步 × 3 次运行共 27 个结果的均值，应分两组数据集呈现。

**核心结论**：BERTopic 显著优于 LDA Sequence——首组数据 TC 由 .009 提升至 **.079**，TD 由 .715 提升至 **.862**；次组数据 TC 由 .173 升至 **.231**（加粗为最佳）。BERTopic-Evolve 与 BERTopic 表现几近持平（.079/.226 vs .079/.231），表明动态演化版本未以牺牲质量为代价。

**作用**：作为论文主实验证据之一，量化支撑 BERTopic 凭借 class-based TF-IDF 流程，在主题一致性与多样性上对传统 LDA 的双重超越，奠定其"神经主题建模新范式"的核心论点。

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
W_{t,d} = tf_{t,d} \cdot \log({\frac{N}{df_t}})
$$

$$
W_{t,c} = tf_{t,c} \cdot \log({1+\frac{A}{tf_t}})
$$

$$
W_{t,c,i} = tf_{t,c,i} \cdot \log({1+\frac{A}{tf_{t}}})
$$

## 技术点深读（DEEP）

![[deep/bertopic-neural-topic-modeling-with-a-class-based-tf-idf-procedure]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/bertopic-neural-topic-modeling-with-a-class-based-tf-idf-procedure.txt`（38314 字符）供引用检索。