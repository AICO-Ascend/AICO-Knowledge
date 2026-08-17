---
paper_num: "44"
title: "Efficiently Serving Large Multimodal Models Using EPD Disaggregation"
authors: "Efficiently Serving Large Multimodal Models Using EPD Disaggregation Gursimran Singh 1 Xinglu Wang 2 Yifan Hu 1 Timothy Yu 1 Linzi Xing 1 Wei Jiang 3 Zhefeng Wang 3 Xiaolong Bai 3 Yi Li 3 Ying Xiong 1 Yong Zhang 1 Zhenan"
date: "2026/1/4"
arxiv: "https://arxiv.org/abs/2501.05460"
pdf: "papers/efficiently-serving-large-multimodal-models-using-epd-disaggregation.pdf"
slug: "efficiently-serving-large-multimodal-models-using-epd-disaggregation"
tags: [multimodal, disaggregated-serving]
---

# Efficiently Serving Large Multimodal Models Using EPD Disaggregation

> [!abstract] 摘要（原文）
> 1\. 💡 本文提出了一种新颖的Encode-Prefill-Decode (EPD) Disaggregation框架，通过将LMM推理的编码、Prefill和解码阶段解耦到专用资源上，解决了现有LMM服务系统中的性能瓶颈。 2. 🚀 该框架引入了多媒体令牌缓存、Intra-Request Parallelization (IRP)、优化资源分配和动态角色切换等创新机制，以提高LMM的服务效率。 3. 📈 实验结果表明，与现有系统相比，EPD显著提升了内存效率（高达15倍）、批处理大小（高达22倍）、每请求图像数量以及SLO达成率，并大幅降低了Time to First Token (TTFT)。

## 元信息
- **发表日期**: 2026/1/4
- **作者**: Efficiently Serving Large Multimodal Models Using EPD Disaggregation Gursimran Singh 1 Xinglu Wang 2 Yifan Hu 1 Timothy Yu 1 Linzi Xing 1 Wei Jiang 3 Zhefeng Wang 3 Xiaolong Bai 3 Yi Li 3 Ying Xiong 1 Yong Zhang 1 Zhenan
- **arXiv**: https://arxiv.org/abs/2501.05460
- **本地 PDF**: `papers/efficiently-serving-large-multimodal-models-using-epd-disaggregation.pdf`
- **页数**: 17

## 图表（原文 caption + 页码）

### Figure 1 (p.1)
![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p01.png]]
> [!quote] caption
> Aggregated (top) vs. disaggregated (bottom) sys- tem architectures. In the aggregated setup, the encoder (E) and LLM share the same GPUs, leading to interference be- tween encode and prefill stages (e.g., LLM-4 delays E5).

### Figure 2 (p.2)
![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p02.png]]
> [!quote] caption
> Impact of disaggregation on supported batch size and number of images per request for the MiniCPM- V 2.6 model. Removing the LLM from the GPU signifi- cantly increases capacity, enabling larger batches and higher- resolution inputs. This demonstrates the memory efficiency benefits of disaggregation. representations. This stage is computationally intensive, especially for high-resolution or complex

### Figure 3 (p.3)
![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p03.png]]
> [!quote] caption
> The inference pipeline of EPD Disaggregation. stages—EP-migration and PD-migration—handle the trans- fer of data from encoding to prefill and from prefill to de- code, respectively. We denote the input text prompt as ip, multimodal data as im, and the output text as o. The steps are as follows:

### Figure 4 (p.4)
![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p04.png]]
> [!quote] caption
> System architecture of the proposed EPD Disaggregated Inference. the data associated with the request. In the decoding stage, workers load the LLM weights for decoding tasks and use the KV cache.

### Figure 5 (p.6)
![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p06.png]]
> [!quote] caption
> SLO attainment (↑) for end-to-end inference across multiple models and image counts per request. Subfigures (a), (b), and (c) correspond to MiniCPM-V 2.6, InternVL2-8B, and InternVL2-26B, respectively. The top and bottom rows show results for 2 and 4 images per request. EPD consistently outperforms all baselines across configurations. question answering items that span diverse video lengths, topic

### Figure 6 (p.7)
![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p07.png]]
> [!quote] caption
> Distribution of TTFT (Y-axis) across varying numbers of images per request (X-axis) for (a) MiniCPM-V 2.6, (b)

### Figure 7 (p.7)
![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p07.png]]
> [!quote] caption
> SLO attainment (↑) versus request rate on the

### Figure 8 (p.7)
![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p07.png]]
> [!quote] caption
> As seen, EPD consistently outperforms vLLM and Dist-

### Figure 9 (p.9)
![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p09.png]]
> [!quote] caption
> As shown, EPD is the only configuration that achieves the SLO requirements, while the other baselines fail to meet the SLOs entirely, even at low request rates.

### Figure 10 (p.13)
![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p13.png]]
> [!quote] caption
> Left: Impact of varying the number of encoding workers in the EPD method. The notation xEyP denotes a configuration with x encoder and y prefill workers. The DistServe method uses a fixed 7P configuration, assigning 7 workers to handle both encoding and prefill steps. Middle: Effect of the number of images per request on end-to-end throughput. Right: Sensitivity to encoding and prefill batch sizes

### Figure 11 (p.13)
![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p13.png]]
> [!quote] caption
> SLO attainment (↑) for end-to-end inference across multiple models and image counts per request. Subfigures (a), (b), and (c) correspond to MiniCPM-V 2.6, InternVL2-8B, and InternVL2-26B, respectively. The top and bottom rows show results for 6 and 8 images per request. EPD consistently outperforms all baselines, demonstrating robust performance as image count increases.. content of this image?”),

### Figure 12 (p.16)
![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p16.png]]
> [!quote] caption
> Breakdown of latency for encode and prefill stages using the InternVL2-8B model across varying numbers of images per request. Subfigures (a) and (b) show results on GPU and NPU, respectively. Light green denotes encode latency and light blue indicates prefill latency. NPUs demonstrate distinct latency characteristics compared to GPUs as input size increases. E.3. SLO Criteria

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\max_{(\mathbf{p},\mathbf{b},\mathbf{s}) \in \mathcal{X}} f(\mathbf{p},\mathbf{b},\mathbf{s}) - \beta cost(\mathbf{p})
$$

$$
\max_{(\mathbf{p}, \mathbf{b}, \mathbf{s}) \in \mathcal{X}} f(\mathbf{p}, \mathbf{b}, \mathbf{s}) - \beta \cdot \text{cost}(\mathbf{p})
$$

$$
v_t^e = E(i_m)
$$

$$
v_t^p = \psi_{EP}(v_t^e)
$$

$$
kv_1^p, o_1^p = P(v_t, i_p)
$$

$$
kv_1^d, o_1^d = \psi_{PD}(kv_1^p, o_1^p)
$$

$$
kv_{t+1}^d, o_{t+1}^d = D(kv_t^d, o_t^d)
$$

## 相关论文

- [[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]] — Mooncake: A KVCache-centric Disaggregated Architecture for LLM Serving
- [[kimi-k2-5-visual-agentic-intelligence]] — KIMI K2.5: VISUAL AGENTIC INTELLIGENCE
- [[qwen3-vl-technical-report]] — Qwen3-VL Technical Report
- [[deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms]] — DeepStack: Deeply Stacking Visual Tokens is Surprisingly Simple and Effective for LMMs
- [[sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills]] — SARATHI: Efficient LLM Inference by Piggybacking Decodes with Chunked Prefills
- [[taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve]] — Taming Throughput-Latency Tradeoff in LLM Inference with Sarathi-Serve

## 全文文本
全文已存 `extraction/fulltext/efficiently-serving-large-multimodal-models-using-epd-disaggregation.txt`（69151 字符）供引用检索。