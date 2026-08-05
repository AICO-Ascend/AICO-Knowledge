---
paper_num: "6"
title: "BLOCK DIFFUSION: INTERPOLATING BETWEEN AUTOREGRESSIVE AND DIFFUSION LANGUAGE MODELS"
authors: ""
date: "2025/3/12"
arxiv: "https://arxiv.org/abs/2503.09573"
pdf: "papers/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models.pdf"
slug: "block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models"
tags: [speculative]
---

# BLOCK DIFFUSION: INTERPOLATING BETWEEN AUTOREGRESSIVE AND DIFFUSION LANGUAGE MODELS

> [!abstract] 摘要（原文）
> 1\. 🚀 本文提出了块扩散语言模型（BD3-LMs），通过在离散去噪扩散和自回归模型之间进行插值，成功解决了传统离散扩散模型在处理任意长度生成和推理效率上的限制。 2. 💡 研究人员开发了一种高效的训练算法及数据驱动的噪声调度策略，通过显著降低梯度方差，有效弥补了扩散模型与自回归模型在困惑度（Perplexity）上的性能差距。 3. 📈 实验结果表明，BD3-LMs 在多个语言建模基准测试中达到了离散扩散模型的新前沿水平，并支持长序列的高质量、并行化生成，同时提升了推理效率。

## 元信息
- **发表日期**: 2025/3/12
- **作者**: —
- **arXiv**: https://arxiv.org/abs/2503.09573
- **本地 PDF**: `papers/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models.pdf`
- **页数**: 28

## 图表（原文 caption + 页码）

### Figure 1 (p.2)
![[assets/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-p02.png]]
> [!quote] caption
> Block diffusion sequentially generates blocks of tokens by performing diffusion within each block and conditioning on previous blocks. By combining strength from autoregressive and diffusion models, block diffusion overcomes the limitations of both approaches by supporting variable-length, higher-quality generation and improving inference efficiency with KV caching and parallel sampling. network a

### Figure 2 (p.6)
![[assets/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-p06.png]]
> [!quote] caption
> Train NLLs for modeling the per-token likelihood on LM1B. Models are trained on 16B tokens. Training under the discrete diffusion NELBO, where half of the tokens in a batch are masked on average, has similar training variance to an AR model with a random batch size. so that Et∼U[0,1]q(xℓ t = m|xℓ) = 0.5. Thus, training on the diffusion objective involves estimating loss gradients with 2x fewer tok

### Figure 3 (p.21)
![[assets/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-p21.png]]
> [!quote] caption
> x1 t x2 t x3 t x1 x2 x3 x1 t x2 t x3 t x1 x2 x3

### Figure 4 (p.22)
![[assets/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-p22.png]]
> [!quote] caption
> We can adapt the masking strategy from Fig. 3 to a FlexAttention compatible sparse masking function as above. This enables the creation of a customized JIT attention operation that uses significantly less memory with up to ≈5X speedup over the naive native scaled_dot_product_attention implementation in PyTorch (≥2.5) on a A5000 GPU with L = 1024 and batch size B = 16. 22

### Figure 5 (p.23)
![[assets/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-p23.png]]
> [!quote] caption
> Attention computation using FlexAttention with our proposed custom mask.

### Figure 6 (p.26)
![[assets/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-p26.png]]
> [!quote] caption
> Sample from MDLM (Sahoo et al., 2024a) of length L = 1024 and T = 5K diffusion steps.

### Figure 7 (p.27)
![[assets/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-p27.png]]
> [!quote] caption
> Sample from BD3-LM for block size L′ = 16 of length L = 2031 under T = 5K diffusion steps (trained with a context length of L = 1024). The generative perplexity of this sample under GPT2-Large is 24.3, and its entropy is 5.5. 27

### Figure 8 (p.28)
![[assets/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-p28.png]]
> [!quote] caption
> Sample from an AR model (Sahoo et al., 2024a) with length L = 2003 (trained with a context length of L = 1024). The generative perplexity of this sample under GPT2-Large is 10.6 and its entropy is 5.5. 28

## 全文文本
全文已存 `extraction/fulltext/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models.txt`（98874 字符）供引用检索。