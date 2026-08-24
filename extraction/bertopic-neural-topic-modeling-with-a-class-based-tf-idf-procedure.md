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
> 【图文联合解读】**Table 1 图文联合解读**

**1）核心数据**：表内为6个主题模型（LDA、NMF、T2V-MPNET、T2V-Doc2Vec、CTM、BERTopic-MPNET）在3个数据集（20 NewsGroups、BBC News、Trump）上的主题一致性（TC）与主题多样性（TD）得分，每格为10–50主题、共15次运行的均值。BERTopic-MPNET的TC为.166/.167/.066，TD为.851/.794/.663；表现最优的对比项中，T2V-Doc2Vec TC居首（.192/.171）但Trump上仅-.169，CTM则在TD上三数据集全部领先（.886/.819/.855）。

**2）关键结论**：BERTopic-MPNET在TC上稳居第二（仅略逊T2V-Doc2Vec），并在Trump集上TC反超（.066 vs -.169/-.213），同时TD保持.66–.85的高位，证明其*c-TF-IDF*类簇流程在主题质量与多样性之间取得了最稳健的平衡，而非追求单一指标峰值。

**3）在论文中的作用**：作为主实验核心证据表，用于支撑"BERTopic在不牺牲多样性的前提下产出语义连贯主题"的核心主张，并与经典基线（LDA/NMF）及同类神经模型（T2V、CTM）做横向对比，验证方法有效性。

### Table 2 (p.6) ⭐深度解读
![[assets/crops/bertopic-neural-topic-modeling-with-a-class-based-tf-idf-procedure-tab02.png]]
> [!quote] caption
> Using four different language models in BERTopic, coherence score (TC) and topic diversity (TD) were calculated ranging from 10 to 50 topics with steps of 10. All results were averaged across 3 runs for each step. Thus, each score is the average of 15 separate runs.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 2 图文联合解读：**

表2在三个数据集（20NG、BBC News、Trump）上对比BERTopic嵌入USE、Doc2Vec、MiniLM、MPNET四种语言模型后的TC（一致性）与TD（多样性），数值为10–50话题各3次共15次运行的均值。

**量化结果**：20NG上Doc2Vec双优（TC=.173、TD=.871）；BBC上MiniLM TC最高(.170)、Doc2Vec TD最高(.819)；Trump集整体偏低，Doc2Vec TC出现负值(-.088)，USE与MPNET TC仅约.05–.07。

**关键结论**：BERTopic性能显著依赖底层嵌入，无单一通用最优模型；Doc2Vec利于一致性却牺牲多样性，MiniLM/MPNET则较均衡。

**论文作用**：该表支撑核心论点——c-TF-IDF流程与嵌入解耦，证明BERTopic框架通用、嵌入可替换，是方法可扩展性的关键实证。

### Table 3 (p.6) ⭐深度解读
![[assets/crops/bertopic-neural-topic-modeling-with-a-class-based-tf-idf-procedure-tab03.png]]
> [!quote] caption
> The topic coherence (TC) and topic diversity (TD) scores were calculated on dynamic topic model- ing tasks. The TC and TD scores were calculated for each of the 9 timesteps in each dataset. Then, all results were averaged across 3 runs for each step. Thus, each score represents the average of 27 val

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 3 解读**

**① 核心对象与结构**：表比较 LDA Sequence、BERTopic、BERTopic-Evolve 三种方法在动态主题建模任务上的主题一致性（TC）与主题多样性（TD）得分；右侧两组指标对应两个数据集，每个数值为 27 次（9 时间步×3 次运行）平均。BERTopic 系列在 TC 上大幅领先 LDA（如 .079 vs .009），BERTopic-Evolve 在首数据集 TD 上最高（.863），BERTopic 在第二数据集 TC 上最高（.231）。

**② 关键结论**：BERTopic 及其-Evolve 变体在动态主题场景下，主题质量（一致性）显著优于传统 LDA Sequence；Evolve 机制进一步提升多样性，证明其在时序主题追踪中的有效性。

**③ 实验链路作用**：作为对 BERTopic 应用于 dynamic topic modeling 的实证支撑，验证该方法不仅适用于静态语料，也能稳健处理时序演化语料。

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