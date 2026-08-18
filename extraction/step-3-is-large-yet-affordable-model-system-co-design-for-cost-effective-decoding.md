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

### Figure 1 (p.1) ⭐深度解读
![[assets/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-p01.png]]
> [!quote] caption
> The Pareto frontier of recent models regarding acti- vated parameters and decoding costs. The darker area is GQA models’ Pareto frontier. Note: Step-3 also has the highest attention effective rank [7], the same as DSv3 and doubling some other models like Qwen3 MoE 235B and Kimi K2. expensive per token (because of low MFU) compared with training and prefill. 2) For reasoning models, longer thinking

> [!tip] 技术解读（多模态）
> # Figure 1 Description

**Architecture/Components/Data Flow:**
Figure 1 is a 2D scatter plot presenting a Pareto frontier analysis of recent LLMs. The **x-axis** shows theoretical decoding cost (USD) at 8K context (range: 0.05–0.10), while the **y-axis** shows activated parameters (range: ~10–50B). Each point represents a model — Step-3 (highlighted as a red star at ~0.055 USD, ~38B params), Pangu Pro, Qwen3 MoE, Llama 4 Maverick, Kimi K2, DSv3, Qwen3 32B, ERNIE4.5, and MM M1. A shaded gray region denotes the GQA-based Pareto frontier. Dashed lines connect competing models. Step-3 sits leftmost, indicating the lowest decoding cost at comparable activated-parameter scale.

**Key Technical Takeaway (≤120 words):**
Step-3 achieves the lowest theoretical decoding cost among recent LLMs at 8K context despite activating ~38B parameters (more than DeepSeek-V3 and Qwen3 MoE 235B). This cost advantage stems from hardware-aware model-system co-design: Multi-Matrix Factorization Attention (MFA) cuts KV-cache size and computation while preserving attention expressiveness, and Attention-FFN Disaggregation (AFD) decouples attention/FFN into specialized subsystems. The result is a new Pareto frontier — Step-3 also matches DSv3 in attention effective rank, doubling Qwen3 MoE 235B and Kimi K2.

**Caption (verbatim):**
Figure 1: The Pareto frontier of recent models regarding activated parameters and decoding costs. The darker area is GQA models' Pareto frontier. Note: Step-3 also has the highest attention effective rank [7], the same as DSv3 and doubling some other models like Qwen3 MoE 235B and Kimi K2.

### Figure 2 (p.6) ⭐深度解读
![[assets/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-p06.png]]
> [!quote] caption
> With all the results shown, we make the following observations:

> [!tip] 技术解读（多模态）
> **Note:** This page contains two tables (Table 4 and Table 5) plus discussion text — there is no diagram/figure on this page. I'll treat Table 4 as the main visual.

## Description of Table 4 (Accelerator Specifications)

**Layout:** A 5-row × 6-column grid comparing four accelerators (NVIDIA H800, H20, A800, Ascend 910B) across: hourly price, BF16/FP16 FLOPs, FP8 FLOPs, memory bandwidth, and compute-to-bandwidth (roofline) ratio.

**Key data flow / insight:**
- **H800**: $2/hr, 9.89×10¹⁴ BF16 FLOPs, 3.35×10¹² B/s → ratio **591** (heavily compute-bound, FP8-capable)
- **H20**: $0.8/hr, 1.48×10¹⁴ FLOPs, 4.00×10¹² B/s → ratio **74** (memory-bound, cheap but slow)
- **A800**: $0.75/hr, 3.12×10¹⁴ FLOPs, ratio **156** (no FP8)
- **Ascend 910B**: $0.67*/hr, 2.80×10¹⁴ FLOPs, ratio **175**

**Key technical takeaway:** The H800's roofline ratio (~591) is ~4× higher than the A800/910B, meaning attention layers (which dominate decoding cost at 8K+ context) suffer a multi-fold slowdown on weaker hardware — driving Observation 4 ("hardware friendliness") and motivating the cost analysis in Table 5.

## Verbatim Caption (Table 4)

> **Table 4:** Comparison of accelerator specifications. *We do not have publicly available 910B pricing. We estimate its price proportionally based on its FLOPs and A800's. As far as we know, there are multiple versions of 910B. We show the weakest and (presumably) most affordable one that we know.

### Figure 3 (p.6) ⭐深度解读
![[assets/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-p06.png]]
> [!quote] caption
> Second, the time spent on each layer will be largely unbal- anced – when running with long context, the full GQA layers consume much more time than the linear attention layers. This may not be a problem for single-node inference deployment, 6

> [!tip] 技术解读（多模态）
> **Note:** This page contains two tables (Table 4 and Table 5) plus discussion text — there is no diagram/figure on this page. I'll treat Table 4 as the main visual.

## Description of Table 4 (Accelerator Specifications)

**Layout:** A 5-row × 6-column grid comparing four accelerators (NVIDIA H800, H20, A800, Ascend 910B) across: hourly price, BF16/FP16 FLOPs, FP8 FLOPs, memory bandwidth, and compute-to-bandwidth (roofline) ratio.

**Key data flow / insight:**
- **H800**: $2/hr, 9.89×10¹⁴ BF16 FLOPs, 3.35×10¹² B/s → ratio **591** (heavily compute-bound, FP8-capable)
- **H20**: $0.8/hr, 1.48×10¹⁴ FLOPs, 4.00×10¹² B/s → ratio **74** (memory-bound, cheap but slow)
- **A800**: $0.75/hr, 3.12×10¹⁴ FLOPs, ratio **156** (no FP8)
- **Ascend 910B**: $0.67*/hr, 2.80×10¹⁴ FLOPs, ratio **175**

**Key technical takeaway:** The H800's roofline ratio (~591) is ~4× higher than the A800/910B, meaning attention layers (which dominate decoding cost at 8K+ context) suffer a multi-fold slowdown on weaker hardware — driving Observation 4 ("hardware friendliness") and motivating the cost analysis in Table 5.

## Verbatim Caption (Table 4)

> **Table 4:** Comparison of accelerator specifications. *We do not have publicly available 910B pricing. We estimate its price proportionally based on its FLOPs and A800's. As far as we know, there are multiple versions of 910B. We show the weakest and (presumably) most affordable one that we know.

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

### Figure 6 (p.11) ⭐深度解读
![[assets/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-p11.png]]
> [!quote] caption
> Module disaggregation in AFD architecture. FFN can be deployed in TP-only, EP-only, or a hybrid TP+EP way, depending on hardware and model architecture. start to be concerned about other issues like expert imbalance, stability, etc.

> [!tip] 技术解读（多模态）
> ## Figure 6 Description

**Architecture & Components:**
The diagram shows AFD's two physically separable instances separated by a dashed line:

- **Attention Instance** (left): A residual block with Norm → Attn → Norm, processing the hidden state and outputting to the next layer.
- **FFN Instance** (right): A MoE pipeline of Norm → Router → Expert Compute → Expert Combine, with an auxiliary Topk-score branch feeding the combiner.

**Data Flow:**
Attention output flows rightward into FFN via **TP gather / EP scatter (fp8)**. The Router produces an expert distribution; experts compute, and results return leftward via **TP scatter / EP gather (bf16)** before a residual add (⊕) and forwarding back to the attention pipeline.

**Key Takeaway:**
AFD's flexibility allows FFN to be deployed as TP-only, EP-only, or hybrid TP+EP, letting system designers tune parallelism to hardware constraints and model topology independently from the attention servers.

## Caption (verbatim)

> Figure 6: Module disaggregation in AFD architecture. FFN can be deployed in TP-only, EP-only, or a hybrid TP+EP way, depending on hardware and model architecture.

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

### Figure 8 (p.13) ⭐深度解读
![[assets/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-p13.png]]
> [!quote] caption
> StepMesh communication workflow tailored for AFD.

> [!tip] 技术解读（多模态）
> **Main Figure Description (Figure 8):**

The figure depicts the StepMesh communication workflow tailored for AFD, showing two symmetric GPU sides (left/right) exchanging data. Each side contains:
- A core computation block labeled "1"## with three sub-stages: Prev Layer (=#"–!!#-:!;), Current Layer (=#"/#%7!:), and Next Layer (3+*$!:)
- A data transformation pipeline (¼'#$&(6 → ¼#$& → -+".'$(&)) feeding into the next layer
- **Activation Tensors** (green) and **Token Tensors** (green) attached as named memory regions
- A bottom tensor-allocation bus (234%!1,!) registered via unique tensor keys

Arrows show: Prev Layer activations → slice into token tensors → register/slice → send via token tensors → receive on remote side → feed into Current Layer computation.

**Key Technical Takeaway:** StepMesh registers tensors by unique keys and enables direct in-place slicing from contiguous GPU memory, eliminating the concatenation/copying overhead required for distributed inference.

**Caption (verbatim):** Figure 8: StepMesh communication workflow tailored for AFD.

### Figure 9 (p.13) ⭐深度解读
![[assets/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-p13.png]]
> [!quote] caption
> StepMesh framework for multiple accelerators. AF-

> [!tip] 技术解读（多模态）
> **Main Figure Description (Figure 8):**

The figure depicts the StepMesh communication workflow tailored for AFD, showing two symmetric GPU sides (left/right) exchanging data. Each side contains:
- A core computation block labeled "1"## with three sub-stages: Prev Layer (=#"–!!#-:!;), Current Layer (=#"/#%7!:), and Next Layer (3+*$!:)
- A data transformation pipeline (¼'#$&(6 → ¼#$& → -+".'$(&)) feeding into the next layer
- **Activation Tensors** (green) and **Token Tensors** (green) attached as named memory regions
- A bottom tensor-allocation bus (234%!1,!) registered via unique tensor keys

Arrows show: Prev Layer activations → slice into token tensors → register/slice → send via token tensors → receive on remote side → feed into Current Layer computation.

**Key Technical Takeaway:** StepMesh registers tensors by unique keys and enables direct in-place slicing from contiguous GPU memory, eliminating the concatenation/copying overhead required for distributed inference.

**Caption (verbatim):** Figure 8: StepMesh communication workflow tailored for AFD.

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