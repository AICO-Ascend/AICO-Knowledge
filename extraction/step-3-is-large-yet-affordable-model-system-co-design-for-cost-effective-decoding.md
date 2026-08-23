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
![[assets/crops/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-fig01.png]]
*整页渲染: ![[assets/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-p01.png]]*
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
![[assets/crops/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-fig02.png]]
*整页渲染: ![[assets/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-p06.png]]*
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
![[assets/crops/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-fig03.png]]
*整页渲染: ![[assets/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-p06.png]]*
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
![[assets/crops/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-fig04.png]]
*整页渲染: ![[assets/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-p08.png]]*
> [!quote] caption
> Step-3 and Pangu Pro MoE have very different trends of decoding cost and training cost.

> [!tip] 技术解读（多模态）
> 【MiniMax 解读】Step-3 attention 设计对比(Fig.5)：Decode 计算 vs 内存访问(8K→32K ctx)，对比 DSv3 MLA / Qwen3-MoE GQA / Step-3 MFA，叠 H800/910B/A800/H20 roofline。DSv3 MLA 算术强度512=H800 compute-bound；Qwen3 GQA 强度32=H20 memory-bound；Step-3 MFA 强度128≈910B(175)/A800(156) ridge 点→计算仅 DSv3 1/4、访存仅 Qwen3 1/3，跨硬件都省。⭐直击 910B roofline，与昇腾相关。

### Figure 5 (p.8) ⭐深度解读
![[assets/crops/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-fig05.png]]
*整页渲染: ![[assets/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-p08.png]]*
> [!quote] caption
> The compute and memory access of different atten- tion designs during decoding, including DSv3’s MLA, Qwen3

> [!tip] 技术解读（多模态）
> 【MiniMax 解读】Step-3 attention 设计对比(Fig.5)：Decode 计算 vs 内存访问(8K→32K ctx)，对比 DSv3 MLA / Qwen3-MoE GQA / Step-3 MFA，叠 H800/910B/A800/H20 roofline。DSv3 MLA 算术强度512=H800 compute-bound；Qwen3 GQA 强度32=H20 memory-bound；Step-3 MFA 强度128≈910B(175)/A800(156) ridge 点→计算仅 DSv3 1/4、访存仅 Qwen3 1/3，跨硬件都省。⭐直击 910B roofline，与昇腾相关。

### Figure 6 (p.11) ⭐深度解读
![[assets/crops/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-fig06.png]]
*整页渲染: ![[assets/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-p11.png]]*
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
![[assets/crops/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-fig07.png]]
*整页渲染: ![[assets/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-p12.png]]*
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
![[assets/crops/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-fig08.png]]
*整页渲染: ![[assets/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-p13.png]]*
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
![[assets/crops/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-fig09.png]]
*整页渲染: ![[assets/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-p13.png]]*
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

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.3) ⭐深度解读
![[assets/crops/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-tab01.png]]
> [!quote] caption
> Model card for Step-3.

> [!tip] 表格解读（多模态）
> **Note:** The provided image contains only textual content (Section 3 of the paper) with a table caption — the actual contents of Table 1 (the model card itself) are not visible in the supplied image. I therefore cannot describe concrete architecture/components/data flow from the figure itself. Below is a faithful description drawn strictly from the surrounding visible text, followed by the verbatim caption.

**Description (based on visible text, not figure content):**
The page introduces Step-3 as one of the first production-quality LLM serving systems exploiting **Attention-FFN Disaggregation (AFD)** for high-throughput decoding under strict SLOs. The rationale: attention layers are smaller in parameters but memory-intensive due to the per-token KV-cache, whereas FFN layers (especially in MoE) carry the bulk of parameters but store no intermediate state. Existing monolithic serving systems ignore these asymmetries, causing suboptimal GPU utilization.

**Key technical takeaway:** Disaggregating attention from FFN exploits each component's distinct hardware affinity — memory-bound attention vs. compute-bound FFN — enabling both components to operate under ideal conditions and achieve high MFU.

**Verbatim caption transcription:**
> Table 1: Model card for Step-3.

### Table 2 (p.5) ⭐深度解读
![[assets/crops/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-tab02.png]]
> [!quote] caption
> Theoretical computation and memory access per decoding token at 8K context length.

> [!tip] 表格解读（多模态）
> ## Description

The figure is **Table 2**, a quantitative comparison matrix that profiles the per-decoding-token cost breakdown across transformer architectures at an 8K context length. It is organized as a four-metric × multi-model grid:

**Columns (cost dimensions):**
1. **KV/State Memory Access** — bytes touched in cache (memory bandwidth bottleneck).
2. **Attention FLOPs (w/o Linear)** — core QKᵀ·V dot-product compute.
3. **Linear layers before/after Attention** — projection compute (Q, K, V, output).
4. **FFN FLOPs** — feed-forward network compute.

**Data flow / reading direction:** Each row is one candidate model, and each cell exposes where cycles and bytes are spent during *decode* (the memory-bound, single-token regime) — letting the reader trade off state size against attention compute, then both against FFN.

**Key takeaway:** During decode, **FFN compute (~2 × d_model · d_ff per token, per layer) dwarfs both attention compute and KV-cache memory bandwidth**, so the FFN column is the dominant cost driver and the most fruitful target for optimizations.

## Caption (verbatim)

*Table 2: Theoretical computation and memory access per decoding token at 8K context length.*

### Table 3 (p.5) ⭐深度解读
![[assets/crops/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-tab03.png]]
> [!quote] caption
> Theoretical computation and memory access per decoding token at 32K context length.

> [!tip] 表格解读（多模态）
> **Note:** The provided image contains only two columns of body text from a paper (Section 4.2 "Theoretical Decoding Cost") and a table caption — **no figure, diagram, or architecture illustration is present**. I cannot describe a figure that isn't in the image without fabricating content. Below I describe the textual content shown and transcribe the caption verbatim.

---

**Description of visible content:**

The text presents a methodology section ("4.2 Theoretical Decoding Cost") of a paper analyzing LLM inference costs. It breaks model decoding cost into three components: (1) attention (with KV cache), (2) linear projections before/after attention, and (3) FFN/MoE. The authors assume compute-bound performance from sufficient batching, amortizing weight memory access into FLOPs. They flag exceptions: the q/k/v projections of MLA and MFA may be non-TP-friendly and not run in H800's compute-bound regime; for not-too-sparse MoE, FFN reaches high MFU. Cost formulas derive a per-token cost combining attention's KV-memory-bound term with FLOPs for projections and FFN:

max(FLOP_Attn · U_FLOP, Byte_KV · U_byte) + FLOP_... + FLOP_FFN.

**Key technical takeaway:** The total per-decoding-token cost decomposes into a memory-bound attention term (driven by KV-cache bytes) plus compute-bound linear/FFN terms (driven by FLOPs), enabling comparison of model architectures on different accelerators using unit costs U_FLOP and U_byte.

---

**Caption transcribed verbatim:**

"Table 3: Theoretical computation and memory access per decoding token at 32K context length."

### Table 4 (p.6) ⭐深度解读
![[assets/crops/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-tab04.png]]
> [!quote] caption
> Comparison of accelerator specifications. *We do not have publicly available 910B pricing. We estimate its price proportionally based on its FLOPs and A800’s. As far as we know, there are multiple versions of 910B. We show the weakest and (presumably) most affordable one that we know.

> [!tip] 表格解读（多模态）
> **Description (Table 4 — not an architecture figure):**

This is a **specification comparison table** rather than a architecture/data-flow diagram. It benchmarks four AI accelerators (NVIDIA H800, H20, A800, and Huawei Ascend 910B) across five columns: unit price (likely USD thousands), two FLOPs throughput columns (different precisions), a memory-bandwidth column, and a derived cost-effectiveness/performance-per-dollar figure. The rows are ordered roughly by raw FLOPs, descending from H800 → 910B.

**Key technical takeaway:** The H800 dominates in raw compute (~2×10¹⁵ FLOPs) and bandwidth (3.35×10¹²), but the Ascend 910B delivers competitive FP16 throughput (~3×10¹⁴) at roughly one-third the H800's price, making it the most cost-efficient option (175) after the H20 — highlighting that peak FLOPS alone misrepresents accelerator value when bandwidth and price are factored in.

**Caption (verbatim):**

> Table 4: Comparison of accelerator specifications. *We do not have publicly available 910B pricing. We estimate its price proportionally based on its FLOPs and A800's. As far as we know, there are multiple versions of 910B. We show the weakest and (presumably) most affordable one that we know.

### Table 5 (p.6) ⭐深度解读
![[assets/crops/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-tab05.png]]
> [!quote] caption
> The unit cost of different accelerators assuming full utilization for the whole month. For FLOP costs, we consider FP8 for H800 and H20, BF16/FP16 for A800 and 910B.

> [!tip] 表格解读（多模态）
> I don't see a figure in the provided content — only text from page 6 with the Table 5 caption and prose referencing Figure 2. I cannot describe the architecture/components/data flow of a figure that isn't visible.

**Caption transcribed verbatim from the page:**

> **Table 5:** The unit cost of different accelerators assuming full utilization for the whole month. For FLOP costs, we consider FP8 for H800 and H20, BF16/FP16 for A800 and 910B.

**What the text tells us about Figure 2 (referenced, not shown):**

The page discusses a cost model with two components — attention cost and FFN cost — combined to derive per-token decoding costs. "AFD" picks the cheapest hardware for each part independently (attention cheapest on one accelerator, FFN on another), and communication is ignored under a multi-batch pipeline assumption. Figure 2 plots decoding cost per 1M tokens for Qwen family (GQA), DSv3 (MLA), and Step-3 at varying context lengths.

**Key technical takeaway from the surrounding text:**
*Attention cost, not parameter count, drives decoding economics* — Qwen3 32B has fewer total *and* activated parameters than Step-3 or DSv3 yet posts the *highest* decoding cost in Figure 2; Step-3 is the cheapest at $0.055/1M tokens (8K) and $0.129 (32K), the gap widening at long context because MLA-style attention scales better than GQA.

If you can share the actual Figure 2 image, I can describe its architecture/panels/data flow directly.

### Table 6 (p.7) ⭐深度解读
![[assets/crops/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-tab06.png]]
> [!quote] caption
> Theoretical decoding cost analysis for each model on each hardware, in USD. As a reminder, these models have different number of activated parameters: DSv3 37B, Qwen3 MoE 22B, Qwen3 32B, MM M1 46B, ERNIE 4.5 47B, Pangu Pro MoE 16.5B and Step-3 38B.

> [!tip] 表格解读（多模态）
> **Figure Description:**

The figure presents a dual-panel grouped bar chart comparing theoretical decoding costs (in USD) of four LLM models—DSv3 (blue), Qwen3 MoE (green), Qwen3 32B (red), and Step-3 (cyan, shown with hatched patterns)—deployed across five hardware setups: H800, H20, A800, 910B, and AFD. The left panel shows costs at an 8K context length (y-axis up to 0.200 USD), while the right panel shows costs at 32K context (y-axis up to ~0.75 USD). Cost ranges expand roughly 3–4× at 32K versus 8K, reflecting longer-sequence inference overhead.

**Key Technical Takeaway:** Step-3 consistently achieves the lowest decoding cost across every hardware configuration and both context lengths, while Qwen3 32B is consistently the most expensive—highlighting that architectural efficiency matters more than raw parameter count for inference economics.

**Caption (verbatim):**

Table 6: Theoretical decoding cost analysis for each model on each hardware, in USD. As a reminder, these models have different number of activated parameters: DSv3 37B, Qwen3 MoE 22B, Qwen3 32B, MM M1 46B, ERNIE 4.5 47B, Pangu Pro MoE 16.5B and Step-3 38B.

### Table 7 (p.10) ⭐深度解读
![[assets/crops/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-tab07.png]]
> [!quote] caption
> Minimum MoE sparsity for different hardware plat- forms to achieve good MFU, where H = 7168, L = 61.

> [!tip] 表格解读（多模态）
> ## Description of the Main Figure

The main figure here is **Table 7**, which presents minimum MoE (Mixture-of-Experts) sparsity requirements across four accelerator platforms: **H800 (0.058), H20 (0.007), A800 (0.031), and 910B (0.034)**. It is the empirical output of the analytical framework derived earlier in the text — a bound on sparsity *S* ensuring that all-to-all expert routing/communication can be hidden behind the compute pipeline (≤ 11.1 ms latency budget). Inputs to the derivation are H = 7168 (hidden size), L = 61 layers, and per-NIC bandwidth (400 Gbps × 8 for H800/H20; 200 Gbps × 8 for A800/910B).

**Key technical takeaway:** H20 needs ~6× more aggressive sparsity than H800 to saturate MFU, because its lower per-NIC bandwidth (400 Gbps effectively constrained) makes communication the bottleneck sooner; H800's higher minimum sparsity reflects its tighter bandwidth-to-compute ratio.

## Caption (verbatim)

**Table 7:** Minimum MoE sparsity for different hardware platforms to achieve good MFU, where *H* = 7168, *L* = 61.

### Table 8 (p.14) ⭐深度解读
![[assets/crops/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-tab08.png]]
> [!quote] caption
> Performance comparison with reported number of DSv3 under 20 tokens/s decoding SLA. TGS: Tokens/GPU/s.

> [!tip] 表格解读（多模态）
> **Description:** Table 8 (rather than an architectural figure) presents a performance comparison between Step-3 and DeepSeek-V3 (DSv3) under a 20 tokens/s decoding SLA, with deployment configurations parameterized by number of attention (A) and FFN (F) instances — e.g., "2A2F" (2 attention + 2 FFN instances, 32 GPUs total). The data flow shows: batch size 6144 → split into 3 micro-batches of 2,048 → fill a 3-stage pipeline. Key columns include context length (4K, 8K, 32K), peak TGS (Tokens/GPU/s), and the A:F ratio used per deployment (2A2F, 4A2F, 16A2F). Step-3 is shown achieving ~74% higher average TGS than DSv3 at 4K context on Hopper GPUs with FP8 GEMM/attention.

**Key takeaway (≤120 words):** Step-3 scales efficiently across context lengths by simply rebalancing attention vs. FFN instances in the pipeline (A:F ratio scales as √context for fixed total batch), keeping total batch, latency, MFU, and SLA intact while peak TGS drops predictably (e.g., 4,039 → 2,693 for 4A2F at 8K). On top of that, Multi-Token Prediction (MTP) is projected to add ~50% throughput on non-H20 accelerators by doubling attention efficiency while FFN compute (and its high MFU) is unaffected. Combined, Step-3's advantage over DSv3 widens with longer contexts and cheaper hardware than H800.

**Caption transcribed verbatim:**
> **Table 8: Performance comparison with reported number of DSv3 under 20 tokens/s decoding SLA. TGS: Tokens/GPU/s.**

### Table 9 (p.14) ⭐深度解读
![[assets/crops/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-tab09.png]]
> [!quote] caption
> Performance comparison of MFA/MLA/GQA. For MLA, we use FlashMLA which does not have official SM80 implementation, so its A800 number is not tested. We use FA3 (SM90) and FA2 (SM80) for MFA/GQA. Here the attention layer includes the linear projection before and after the core attention op. Each exper

> [!tip] 表格解读（多模态）
> ## Main Figure Description

Table 9 is a **latency benchmark comparison** of three attention mechanism designs: **MFA** (Step-3), **MLA** (DSv3), and **GQA** (Qwen3-235B). The table reports per-attention-layer latency across multiple GPU tiers—H100 (SM90), A100/A800 (SM80), and H20—covering different context lengths and prefill/decode phases.

**Columns (mechanisms):**
- MFA-Step3 — FA3 (SM90) / FA2 (SM80), DP attention
- MLA-DSv3 — FlashMLA (SM90 only; no SM80 kernel → A800 not tested), DP attention
- GQA-Qwen3 — FA3 (SM90) / FA2 (SM80), TP attention

**Rows (configs):** chip + context length combinations.

**Reported setup:** attention layer wrapped around pre/post linear projections; 4 GPUs; total batch size 256; GEMM in FP8 (SM90) or INT8 (SM80); attention compute in BF16.

## Key Technical Takeaway

MFA-Step3 achieves the **lowest per-attention latency** across all hardware tiers, followed by MLA-DSv3 then GQA-Qwen3. The advantage **widens on lower-end accelerators (H20, A800)** and on **longer context lengths**, indicating that MFA's factored-attention design scales more gracefully under bandwidth-constrained, long-context inference—precisely the regime most relevant to AFD production serving.

## Caption (verbatim)

> Table 9: Performance comparison of MFA/MLA/GQA. For MLA, we use FlashMLA which does not have official SM80 implementation, so its A800 number is not tested. We use FA3 (SM90) and FA2 (SM80) for MFA/GQA. Here the attention layer includes the linear projection before and after the core attention op. Each experiment uses 4 GPUs and a total batch sze of 256. Both MFA and MLA use DP attention, while GQA uses TP attention. GEMM runs with *FP8* (SM90) or *INT8* (SM80) while attention runs with *BF16*.

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