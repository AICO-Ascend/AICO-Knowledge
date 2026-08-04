---
paper_num: "3"
title: "EAGLE-3: Scaling up Inference Acceleration of Large Language Models via Training-Time Test"
authors: "Models via Training-Time Test Yuhui Li1,3, Fangyun Wei2, Chao Zhang1, Hongyang Zhang3,4 1Peking University 2Microsoft Research 3University of Waterloo 4Vector Institute yuhui.li@stu.pku.edu.cn, fawe@microsoft.com c.zhang"
date: "2025/3/3"
arxiv: "https://arxiv.org/abs/2503.01840"
pdf: "papers/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test.pdf"
slug: "eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test"
tags: [speculative, training]
---

# EAGLE-3: Scaling up Inference Acceleration of Large Language Models via Training-Time Test

> [!abstract] 摘要（原文）
> 1\. 🚀 EAGLE-3 通过放弃特征预测约束，直接进行 token 预测并引入 multi-layer feature fusion 技术，显著提升了 draft model 的表达能力与推理效率。 2. 📈 该研究提出了 training-time test 训练方法，使 draft model 能够有效利用规模化训练数据，从而在 LLaMA 等主流模型上实现了高达 6.5 倍的推理速度提升。 3. ⚙️ 实验表明，EAGLE-3 在 SGLang 等工业级推理框架中表现优异，在 batch size 为 64 时仍能保持 1.38 倍的吞吐量提升，优于现有的 speculative sampling 方法。

## 元信息
- **发表日期**: 2025/3/3
- **作者**: Models via Training-Time Test Yuhui Li1,3, Fangyun Wei2, Chao Zhang1, Hongyang Zhang3,4 1Peking University 2Microsoft Research 3University of Waterloo 4Vector Institute yuhui.li@stu.pku.edu.cn, fawe@microsoft.com c.zhang
- **arXiv**: https://arxiv.org/abs/2503.01840
- **本地 PDF**: `papers/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test.pdf`
- **页数**: 12

## 图表（原文 caption + 页码）

### Figure 1 (p.1)
![[assets/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-p01.png]]
> [!quote] caption
> Scaling law evaluated on the MT-bench using LLaMA-Instruct 3.1 8B as the target model, with the x-axis representing the data scale relative to ShareGPT.

### Figure 2 (p.2) ⭐MiniMax深度解读
![[assets/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-p02.png]]
> [!quote] caption
> Speedup ratios of different methods at temperature=0. For the standard speculative sampling, Vicuna-13B uses Vicuna-68M as the draft model. In Table 1, we present comparisons with additional methods, but this figure only showcases a subset. Chat model’s evaluation dataset is MT-bench, and the reasoning model’s evaluation dataset is GSM8K. DeepSeek R1 LLaMA 8B refers to DeepSeek-R1-Distill-LLaMA 8B

> [!tip] 技术解读（MiniMax 多模态）
> 【MiniMax 解读】EAGLE-3 加速比柱状图（temp=0）：在 Vicuna-13B/LLaMA-3.1-8B/3.3-70B/DeepSeek-R1-LLaMA-8B 上对比 Vanilla/SpecDec/Medusa/HASS/EAGLE/EAGLE-2/EAGLE-3，EAGLE-3 分别达 5.6x/4.4x/4.1x/5.0x，全面最优。适合做「EAGLE-3 性能优势」论据。

### Figure 3 (p.3)
![[assets/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-p03.png]]
> [!quote] caption
> Illustration of training-time test (the bottom part) and its comparison with other draft methods (the upper and middle parts). f denotes the feature, t denotes the token, and a represents the unconstrained vectors.

### Figure 4 (p.2) ⭐MiniMax深度解读
![[assets/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-p02.png]]
> [!quote] caption
> We can address this issue by incorporating Step 1 into the training process (the bottom of Figure 3). Using this method, the benefits of increasing training data become more pronounced. We name this technique as training-time test. EAGLE and speculative sampling methods such as Medusa (Cai et al., 2024) reuse the top-layer fea- tures of the target model, specifically the features immediately befor

> [!tip] 技术解读（MiniMax 多模态）
> 【MiniMax 解读】EAGLE-3 加速比柱状图（temp=0）：在 Vicuna-13B/LLaMA-3.1-8B/3.3-70B/DeepSeek-R1-LLaMA-8B 上对比 Vanilla/SpecDec/Medusa/HASS/EAGLE/EAGLE-2/EAGLE-3，EAGLE-3 分别达 5.6x/4.4x/4.1x/5.0x，全面最优。适合做「EAGLE-3 性能优势」论据。

### Figure 5 (p.4)
![[assets/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-p04.png]]
> [!quote] caption
> Diagram of the EAGLE-3 inference pipeline, illustrating the three steps of the draft model. l, m, and h represent the low, middle, and high-level features of the target model, respectively. e denotes the embedding. 3 EAGLE-3

### Figure 6 (p.5)
![[assets/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-p05.png]]
> [!quote] caption
> All attention masks are diagonal, except when the original training data is used as the key. Using matrix multiplication in this case would result in significant computational waste, so we can use vector dot products to calculate the attention score only for the corresponding positions. HASS (Zhang et al., 2024) and EAGLE-3 both make similar modifications to the attention mecha- nism to simulate t

### Figure 7 (p.8)
![[assets/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-p08.png]]
> [!quote] caption
> Acceptance rate of EAGLE and EAGLE-3 on MT-bench, with the target model being LLaMA-

## 全文文本
全文已存 `extraction/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test.txt`（45552 字符）供引用检索。