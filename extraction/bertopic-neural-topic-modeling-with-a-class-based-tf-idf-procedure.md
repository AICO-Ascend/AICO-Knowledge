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

### Figure 1 (p.7)
![[assets/bertopic-neural-topic-modeling-with-a-class-based-tf-idf-procedure-p07.png]]
> [!quote] caption
> Computation time (wall time) in seconds of each topic model on the Trump dataset. Increasing sizes of vocabularies were regulated through selection of documents ranging from 1000 documents until 43000 documents with steps of 2000. Left: computational results with CTM. Right: computational results without CTM as it inﬂates the y-axis making differentiation between other topic models difﬁcult to vis

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

## 全文文本
全文已存 `extraction/fulltext/bertopic-neural-topic-modeling-with-a-class-based-tf-idf-procedure.txt`（38314 字符）供引用检索。