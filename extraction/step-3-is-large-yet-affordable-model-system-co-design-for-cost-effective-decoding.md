---
paper_num: "42"
title: "Step-3 is Large yet Affordable: Model-system Co-design for Cost-effective Decoding"
authors: "Model-system Co-design for Cost-effective Decoding StepFun Inc."
date: "2026/1/4"
arxiv: "https://arxiv.org/abs/2507.19427"
pdf: "papers/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding.pdf"
slug: "step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding"
tags: []
---

# Step-3 is Large yet Affordable: Model-system Co-design for Cost-effective Decoding

> [!abstract] 摘要（原文）
> 1\. 🚀 Step-3 是一种 321B VLM，通过以成本效益为目标的硬件感知模型-系统协同设计，显著优化了大型语言模型的解码效率。 2. 💡 其核心创新包括 Multi-Matrix Factorization Attention (MFA) 机制，大幅减少 KV cache 和计算量，以及 Attention-FFN Disaggregation (AFD) 系统，解耦 Attention 和 FFN 层以优化效率。 3. 💰 Step-3 在理论解码成本上显著优于 DeepSeek-V3 和 Qwen3 MoE 等模型，并在 Hopper GPUs 上实现了高达 4,039 tokens per second per GPU 的吞吐量，设定了 LLM 解码的新 Pareto frontier。

## 元信息
- **发表日期**: 2026/1/4
- **作者**: Model-system Co-design for Cost-effective Decoding StepFun Inc.
- **arXiv**: https://arxiv.org/abs/2507.19427
- **本地 PDF**: `papers/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding.pdf`
- **页数**: 18

## 图表（原文 caption + 页码）

### Figure 1 (p.1)
![[assets/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-p01.png]]
> [!quote] caption
> The Pareto frontier of recent models regarding acti- vated parameters and decoding costs. The darker area is GQA models’ Pareto frontier. Note: Step-3 also has the highest attention effective rank [7], the same as DSv3 and doubling some other models like Qwen3 MoE 235B and Kimi K2. expensive per token (because of low MFU) compared with training and prefill. 2) For reasoning models, longer thinking

### Figure 2 (p.6)
![[assets/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-p06.png]]
> [!quote] caption
> With all the results shown, we make the following observations:

### Figure 3 (p.6)
![[assets/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-p06.png]]
> [!quote] caption
> Second, the time spent on each layer will be largely unbal- anced – when running with long context, the full GQA layers consume much more time than the linear attention layers. This may not be a problem for single-node inference deployment, 6

### Figure 4 (p.8) ⭐深度解读
![[assets/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-p08.png]]
> [!quote] caption
> Step-3 and Pangu Pro MoE have very different trends of decoding cost and training cost.

> [!tip] 技术解读（多模态）
> 【MiniMax 解读】Step-3 attention 设计对比(Fig.5)：Decode 计算 vs 内存访问(8K→32K ctx)，对比 DSv3 MLA / Qwen3-MoE GQA / Step-3 MFA，叠 H800/910B/A800/H20 roofline。DSv3 MLA 算术强度512=H800 compute-bound；Qwen3 GQA 强度32=H20 memory-bound；Step-3 MFA 强度128≈910B(175)/A800(156) ridge 点→计算仅 DSv3 1/4、访存仅 Qwen3 1/3，跨硬件都省。⭐直击 910B roofline，与昇腾相关。

### Figure 5 (p.8) ⭐深度解读
![[assets/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-p08.png]]
> [!quote] caption
> The compute and memory access of different atten- tion designs during decoding, including DSv3’s MLA, Qwen3

> [!tip] 技术解读（多模态）
> 【MiniMax 解读】Step-3 attention 设计对比(Fig.5)：Decode 计算 vs 内存访问(8K→32K ctx)，对比 DSv3 MLA / Qwen3-MoE GQA / Step-3 MFA，叠 H800/910B/A800/H20 roofline。DSv3 MLA 算术强度512=H800 compute-bound；Qwen3 GQA 强度32=H20 memory-bound；Step-3 MFA 强度128≈910B(175)/A800(156) ridge 点→计算仅 DSv3 1/4、访存仅 Qwen3 1/3，跨硬件都省。⭐直击 910B roofline，与昇腾相关。

### Figure 6 (p.11)
![[assets/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-p11.png]]
> [!quote] caption
> Module disaggregation in AFD architecture. FFN can be deployed in TP-only, EP-only, or a hybrid TP+EP way, depending on hardware and model architecture. start to be concerned about other issues like expert imbalance, stability, etc.

### Figure 7 (p.12) ⭐深度解读
![[assets/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-p12.png]]
> [!quote] caption
> Communication topology and the multi-stages pipeline of the AFD architecture.

> [!tip] 技术解读（多模态）
> **1) 主要架构/组件/数据流描述**

图示展示了 **AFD（Attention-FFN 分离）架构** 的通信拓扑与多阶段流水线：
- **Attention 实例**（下方）和 **FFN 实例**（上方）通过 **Direct RDMA** 直连，每侧各包含多块 GPU（G）。
- 数据流沿时间轴分为 **Layer0 / Layer1** 两个阶段，三个样本 **D1, D2, D3** 依次经 Attn→A→F（fp8）送至 FFN，FFN 计算后经 **F→A（bf16）** 回传残差，再进入下一层 Attn。
- 三条独立通道并行：**Attn** 计算、**A→F（fp8）前向广播**、**F→A（bf16）反向回传**，互不抢占带宽。

**2) 关键技术要点**

**混合精度通信 + 多阶段流水线重叠**：Attention→FFN 方向采用 **FP8 量化**以节省带宽，FFN→Attention 方向保留 **BF16** 以保护残差精度；通过让 **A→F 与 F→A 两条独立路径并发**（不抢带宽），结合各阶段近似的计算耗时，使通信完全被计算掩盖，实现 **低延迟下的高吞吐** 流水（同一层可连续接收 D1', D2', D3'）。**

**3) 图 caption 逐字转录**

**Figure 7: Communication topology and the multi-stages pipeline of the AFD architecture.**

### Figure 8 (p.13)
![[assets/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-p13.png]]
> [!quote] caption
> StepMesh communication workflow tailored for AFD.

### Figure 9 (p.13)
![[assets/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-p13.png]]
> [!quote] caption
> StepMesh framework for multiple accelerators. AF-

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\max(FLOP_{Attn}U_{FLOP}, Byte_{KV}U_{byte}) + FLOP_{Linear}U_{FLOP}
$$

$$
2 \times N_{\text{token}} \times W_{\text{FFN}}
$$

$$
2 \times B_{\text{dense}} \ge \frac{\text{FLOPs}}{\text{Bandwidth}}
$$

$$
B_{\text{MoE}} = \frac{B_{\text{dense}}}{S}
$$

$$
B_{\text{MoE}} \ge \frac{\text{FLOPs}}{2 \times S \times \text{Bandwidth}}
$$

$$
3 \times H \times B_{\text{MoE}}
$$

$$
\frac{3 \times H \times B_{\text{MoE}}}{\text{Net}} \le \frac{16.6\text{ms}}{L}
$$

$$
\frac{H \times \text{FLOPs} \times L}{\text{Net} \times S \times \text{Bandwidth}} \le \frac{16.6\text{ms} \times 2}{3} = 11.1\text{ms}
$$

$$
S \ge \frac{H \times \text{FLOPs} \times L}{\text{Net} \times \text{Bandwidth} \times 11.1\text{ms}}
$$

## 技术点深读（DEEP）

![[deep/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding.txt`（78380 字符）供引用检索。