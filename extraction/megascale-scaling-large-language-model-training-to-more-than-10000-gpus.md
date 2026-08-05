---
paper_num: "46"
title: "MegaScale: Scaling Large Language Model Training to More Than 10,000 GPUs"
authors: "Ziheng Jiang1,∗Haibin Lin1,∗Yinmin Zhong2,∗Qi Huang1 Yangrui Chen1 Zhi Zhang1 Yanghua Peng1 Xiang Li1 Cong Xie1 Shibiao Nong1 Yulu Jia1 Sun He1 Hongmin Chen1 Zhihao Bai1 Qi Hou1 Shipeng Yan1 Ding Zhou1 Yiyao Sheng1 Zhuo "
date: "2026/1/4"
arxiv: "https://arxiv.org/abs/2402.15627"
pdf: "papers/megascale-scaling-large-language-model-training-to-more-than-10000-gpus.pdf"
slug: "megascale-scaling-large-language-model-training-to-more-than-10000-gpus"
tags: [training]
---

# MegaScale: Scaling Large Language Model Training to More Than 10,000 GPUs

> [!abstract] 摘要（原文）
> 1\. 🚀 MegaScale是一个用于在超过10,000个GPU上训练大型语言模型(LLM)的生产系统，旨在解决大规模训练中的效率和稳定性挑战。 2. ⚙️ MegaScale通过算法-系统协同设计，整合了模型优化、计算与通信重叠、算子优化、数据管道及网络调优，并利用深度可观测性和鲁棒训练框架实现故障容忍。 3. 💥 该系统在12,288个GPU上训练175B LLM时实现了55.2%的Model FLOPs Utilization (MFU)，比Megatron-LM提升1.34倍，并在数周的实际生产运行中自主修复和恢复了100多次。

## 元信息
- **发表日期**: 2026/1/4
- **作者**: Ziheng Jiang1,∗Haibin Lin1,∗Yinmin Zhong2,∗Qi Huang1 Yangrui Chen1 Zhi Zhang1 Yanghua Peng1 Xiang Li1 Cong Xie1 Shibiao Nong1 Yulu Jia1 Sun He1 Hongmin Chen1 Zhihao Bai1 Qi Hou1 Shipeng Yan1 Ding Zhou1 Yiyao Sheng1 Zhuo 
- **arXiv**: https://arxiv.org/abs/2402.15627
- **本地 PDF**: `papers/megascale-scaling-large-language-model-training-to-more-than-10000-gpus.pdf`
- **页数**: 16

## 图表（原文 caption + 页码）

### Figure 1 (p.2)
![[assets/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-p02.png]]
> [!quote] caption
> Data parallel training with ZeRO2. dependencies that contribute to stability issues. We develop a robust training framework to automate fault localization and recovery. We design heartbeat messages encapsulating various forms of information to facilitate real-time anomaly detection and provide early warnings. We implement a suite of diagnostic tests to identify nodes causing disruptions. We optimi

### Figure 2 (p.3)
![[assets/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-p03.png]]
> [!quote] caption
> Interleaved 1F1B pipeline. update the model. Instead of duplicating model states (like the optimizer states, gradients, and parameters), Zero Redun- dancy Optimizer (ZeRO) [11] shards these states across every data-parallel process. As a result, the traditional all-reduce operations that aggregate gradients are decomposed into sep- arate reduce-scatter and all-gather operations. This is because ev

### Figure 3 (p.4)
![[assets/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-p04.png]]
> [!quote] caption
> Overlapping communication in tensor parallelism (TP) and sequence parallelism (SP) with parallel transformer block (PTB). with a large receptive field created by stacking layers of such windowed attention. This enables faster training without com- promising the accuracy. LAMB optimizer. Efficient training at a large scale is often hindered by batch size constraints. Particularly, increasing the ba

### Figure 4 (p.4)
![[assets/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-p04.png]]
> [!quote] caption
> The cool-down phase can be viewed as the inverse of the warm-up phase, allowing for the inverse application of the same technique. As for the steady phase, both the forward and backward computation are independent of adjacent communication operations. Taking the backward as an example, as shown in the right part of

### Figure 5 (p.6)
![[assets/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-p06.png]]
> [!quote] caption
> Robust training workflow. interval and help recover the transmission more quickly when the link flapping period is short. 4

### Figure 6 (p.8)
![[assets/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-p08.png]]
> [!quote] caption
> Inconsistent MFU observed in large-scale training. Differ- ent colors denote distinct executions of the same training job. mitigates the bandwidth constraints of HDFS, leading to a substantial reduction in the recovery time. 5

### Figure 7 (p.8)
![[assets/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-p08.png]]
> [!quote] caption
> We gather latency data of the computation phase (forward and backward) across devices and average the latency across steps. The aggregated data is visualized host 0 0 1 2 3 host 3 12 13 14 15 host 6 24 25 26 27 host 9 36 37 38 39 host 4 16 17 18 19 host 7 28 29 30 31 host 10 40 41 42 43 host 5 20 21 22 23 host 8 32 33 34 35 host 11 44 45 46 47 host 1 4 5 6 7 host 2 8 9 10 11 DP Comm TP Comm PP Com

### Figure 8 (p.9)
![[assets/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-p09.png]]
> [!quote] caption
> The trace shows events collected in a pipeline group on a unified timeline. Dependencies become visible when an event is selected.

### Figure 9 (p.10)
![[assets/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-p10.png]]
> [!quote] caption
> Weak-scaling training performance of Megatron-LM and

### Figure 10 (p.11)
![[assets/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-p11.png]]
> [!quote] caption
> The training loss curves in microbenchmark experiments.

### Figure 11 (p.11)
![[assets/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-p11.png]]
> [!quote] caption
> The normalized training loss curve of a real production run on more than 10,000 GPUs for several weeks. This run trains a model with hundreds of billions of parameters on multi-trillion tokens. Different colors indicate training restarts. MegaScale repairs and recovers the training process for over 100 times in presence of failures.

### Figure 12 (p.12)
![[assets/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-p12.png]]
> [!quote] caption
> The MFU becomes stable after addressing the stragglers and problematic code segments. Different colors represent different training trials with the same setup. executing diagnostic tests is less than 10 minutes. Moreover, the system can catch up to the training progress prior to the crash within 15 minutes from the latest checkpoints, maintain- ing over 90% effective training time rate, which is c

## 全文文本
全文已存 `extraction/fulltext/megascale-scaling-large-language-model-training-to-more-than-10000-gpus.txt`（77210 字符）供引用检索。