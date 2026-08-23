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
> **Figure Description (≤120 words):**

The figure presents two side-by-side line plots comparing wall-time (seconds) of nine topic models on the Trump dataset as a function of vocabulary size (~2,500 to ~17,500 words). Models include BERTopic variants (Doc2Vec, MiniLM, MPNET, USE), Top2Vec variants (Doc2Vec, MPNET), plus CTM-MPNET, LDA, and NMF. The **left** plot includes all models; CTM-MPNET dominates the chart, scaling steeply to ~1,500 s, flattening the visibility of other curves near zero. The **right** plot excludes CTM-MPNET, rescaling the y-axis to 0–100 s, revealing that BERTopic-MPNET and Top2Vec-MPNET scale worst (~100 s), while LDA stays fastest (~35 s). **Key takeaway:** Classical models (LDA, NMF) scale most efficiently with vocabulary, whereas neural embedding–based models—especially CTM-MPNET—exhibit super-linear growth.

**Caption (verbatim):**

Figure 1: Computation time (wall time) in seconds of each topic model on the Trump dataset. Increasing sizes of vocabularies were regulated through selection of documents ranging from 1000 documents until 43000 documents with steps of 2000. **Left**: computational results with CTM. **Right**: computational results without CTM as it inflates the y-axis making differentiation between other topic models difficult to visualize.

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.5) ⭐深度解读
![[assets/crops/bertopic-neural-topic-modeling-with-a-class-based-tf-idf-procedure-tab01.png]]
> [!quote] caption
> Ranging from 10 to 50 topics with steps of 10, topic coherence (TC) and topic diversity (TD) were calculated at each step for each topic model. All results were averaged across 3 runs for each step. Thus, each score is the average of 15 separate runs.

> [!tip] 表格解读（多模态）
> **Description:** The figure (Table 1) outlines the experimental setup for evaluating topic modeling pipelines. *Components:* BERTopic, CTM (Song et al., 2020), and two Top2Vec variants (one with Doc2Vec, one with SBERT "all-mpnet-base-v2"); SBERT candidates include USE, Doc2Vec, "all-MiniLM-L6-v2", and "all-mpnet-base-v2". *Data flow:* topic count sweeps from 10→50 in steps of 10, producing TC and TD scores at each step; for dynamic topic models, NPMI is computed at K=50 across timesteps. *Protocol:* UMAP + HDBSCAN hyperparameters are held fixed across models for fair comparison. 

**Key takeaway:** Every reported score is the mean of 3 independent runs × 5 topic-count steps = 15 runs, controlling for stochastic variation in embedding-based clustering.

### Table 2 (p.6) ⭐深度解读
![[assets/crops/bertopic-neural-topic-modeling-with-a-class-based-tf-idf-procedure-tab02.png]]
> [!quote] caption
> Using four different language models in BERTopic, coherence score (TC) and topic diversity (TD) were calculated ranging from 10 to 50 topics with steps of 10. All results were averaged across 3 runs for each step. Thus, each score is the average of 15 separate runs.

> [!tip] 表格解读（多模态）
> **Note:** The image contains a table (Table 2), not a figure. Describing its structure below.

**Description (≤120 words):**
The table presents a comparative evaluation of a single BERTopic pipeline architecture instantiated with four interchangeable embedding-model components: **USE**, **Doc2Vec**, **MiniLM**, and **MPNET**. The data flow is: corpus → chosen sentence/document encoder → BERTopic's transformer-based clustering & c-TF-IDF topic extraction → evaluation. Six numeric columns report averaged coherence (TC) and topic-diversity (TD) scores across topic counts {10, 20, 30, 40, 50}.

**Key takeaway:** Doc2Vec yields the highest coherence scores (up to .819) but the worst topic diversity (–.088), indicating semantically tight yet semantically redundant topics. In contrast, MiniLM and MPNET deliver more balanced coherence–diversity trade-offs (.802–.851 coherence, ~.660–.663 diversity), making transformer-based sentence encoders the preferable default for general-purpose BERTopic deployments.

**Caption transcribed verbatim:**
> Table 2: Using four different language models in BERTopic, coherence score (TC) and topic diversity (TD) were calculated ranging from 10 to 50 topics with steps of 10. All results were averaged across 3 runs for each step. Thus, each score is the average of 15 separate runs.

### Table 3 (p.6) ⭐深度解读
![[assets/crops/bertopic-neural-topic-modeling-with-a-class-based-tf-idf-procedure-tab03.png]]
> [!quote] caption
> The topic coherence (TC) and topic diversity (TD) scores were calculated on dynamic topic model- ing tasks. The TC and TD scores were calculated for each of the 9 timesteps in each dataset. Then, all results were averaged across 3 runs for each step. Thus, each score represents the average of 27 val

> [!tip] 表格解读（多模态）
> **Note:** The main figure (Figure 1, referenced in §6.4 "Wall time") is not visible in the provided page — only body text appears. I can only infer its contents from textual references and cannot transcribe a figure caption that isn't shown.

**Description of Figure 1 (inferred from §6.4 text):**
The figure appears to be a wall-time comparison chart showing the runtime of various dynamic topic models, with "the left graph" comparing models like CTM (with MPNet/SBERT embeddings), classical models such as NMF, and likely Top2Vec variants. The figure likely plots execution time (y-axis) against something like dataset or timestep, with "both left" and "right graphs" suggesting a two-panel layout.

**Key takeaway:** CTM using MPNet-based SBERT embeddings is a significant computational bottleneck (slowest), while classical models like NMF are much faster; this trade-off between embedding quality and inference speed is critical for selecting topic models at scale.

**Caption verbatim (Table 3, the only caption actually shown):**

> Table 3: The topic coherence (TC) and topic diversity (TD) scores were calculated on dynamic topic modeling tasks. The TC and TD scores were calculated for each of the 9 timesteps in each dataset. Then, all results were averaged across 3 runs for each step. Thus, each score represents the average of 27 values.

If you can share the actual figure page, I'd be happy to provide a more accurate description of its architecture and components.

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