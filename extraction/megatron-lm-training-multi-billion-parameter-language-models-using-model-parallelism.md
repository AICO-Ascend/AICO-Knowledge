---
paper_num: "49"
title: "Megatron-LM: Training Multi-Billion Parameter Language Models Using Model Parallelism"
authors: "Model Parallelism Mohammad Shoeybi 1 2 Mostofa Patwary 1 2 Raul Puri 1 2 Patrick LeGresley 2 Jared Casper 2 Bryan Catanzaro 2"
date: "2026/1/4"
arxiv: "https://arxiv.org/abs/1909.08053"
pdf: "papers/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism.pdf"
slug: "megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism"
tags: [training]
---

# Megatron-LM: Training Multi-Billion Parameter Language Models Using Model Parallelism

> [!abstract] 摘要（原文）
> 1\. 🚀 Megatron-LM 提出了一种简单高效的层内模型并行方法，通过在原生 PyTorch 中少量修改即可训练数十亿参数的 Transformer 模型。 2. 📈 该方法成功地将 Transformer 模型扩展到 8.3 亿参数，使用 512 个 GPU 实现了 15.1 PetaFLOPs 的可持续性能和 76% 的扩展效率，并与流水线并行互补。 3. 💡 研究还发现 BERT 模型中 Layer Normalization 的放置对模型扩展至关重要，并用 GPT-2 和 BERT 模型在 WikiText103、LAMBADA 和 RACE 等数据集上取得了 SOTA 结果。

## 元信息
- **发表日期**: 2026/1/4
- **作者**: Model Parallelism Mohammad Shoeybi 1 2 Mostofa Patwary 1 2 Raul Puri 1 2 Patrick LeGresley 2 Jared Casper 2 Bryan Catanzaro 2
- **arXiv**: https://arxiv.org/abs/1909.08053
- **本地 PDF**: `papers/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism.pdf`
- **页数**: 15

## 图表（原文 caption + 页码）

### Figure 1 (p.2)
![[assets/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-p02.png]]
> [!quote] caption
> Model (blue) and model+data (green) parallel FLOPS as a function of number of GPUs. Model parallel (blue): up to 8-way model parallel weak scaling with approximately 1 billion parameters per GPU (e.g. 2 billion for 2 GPUs and 4 billion for 4 GPUs). Model+data parallel (green): similar conﬁguration as model parallel combined with 64-way data parallel. a baseline by training a model of 1.2 billion p

### Figure 2 (p.3)
![[assets/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-p03.png]]
> [!quote] caption
> Transformer Architecture. Purple blocks correspond to fully connected layers. Each blue block represents a single trans- former layer that is replicated N times. and compute efﬁciency. The original transformer formula- tion was designed as a machine translation architecture that transforms an input sequence into another output sequence using two parts, an Encoder and Decoder. However, recent work 

### Figure 3 (p.4)
![[assets/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-p04.png]]
> [!quote] caption
> Blocks of Transformer with Model Parallelism. f and g are conjugate. f is an identity operator in the forward pass and all reduce in the backward pass while g is an all reduce in the forward pass and identity in the backward pass.

### Figure 4 (p.5)
![[assets/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-p05.png]]
> [!quote] caption
> Communication operations in a transformer layer. There are 4 total communication operations in the forward and backward pass of a single model parallel transformer layer. contains a portion of the embedding table, an all-reduce (g operator) is required after the input embedding. For the output embedding, one approach is to perform the parallel GEMM [Y1, Y2] = [XE1, XE2] to obtain the logits, add a

### Figure 5 (p.6)
![[assets/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-p06.png]]
> [!quote] caption
> Model and model + data parallel weak scaling efﬁciency as a function of the number of GPUs. done by scaling the batch-size, however, this approach does not address training large models that do not ﬁt on a single GPU and it leads to training convergence degradation for large batch sizes. In contrast, here we use weak scaling to train larger models that were not possible otherwise. The baseline for

### Figure 6 (p.7)
![[assets/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-p07.png]]
> [!quote] caption
> Validation set perplexity. All language models are trained for 300k iterations. Larger language models converge notice- ably faster and converge to lower validation perplexities than their smaller counterparts.

### Figure 7 (p.8)
![[assets/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-p08.png]]
> [!quote] caption
> Training loss for BERT model using the original architec- ture (a) and the rearranged architecture (b). Left ﬁgure shows the training loss for 336M and 752M BERT model. While the original architecture performs well on the 336M model, the modiﬁcations in (b) enable stable training with lower training loss.

### Figure 8 (p.12)
![[assets/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-p12.png]]
> [!quote] caption
> Grouping of GPUs for hybrid model and data parallelism with 8-way model parallel and 64-way data parallel. C. Text Samples

## 全文文本
全文已存 `extraction/fulltext/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism.txt`（68294 字符）供引用检索。