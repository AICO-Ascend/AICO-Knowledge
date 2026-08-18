---
paper_num: "56"
title: "Parallel Scan on Ascend AI Accelerators"
authors: "Bart lomiej Wr´oblewski∗ Gioele Gottardo† Anastasios Zouzias†"
date: "2025/5/20"
arxiv: "https://arxiv.org/abs/2505.15112"
pdf: "papers/parallel-scan-on-ascend-ai-accelerators.pdf"
slug: "parallel-scan-on-ascend-ai-accelerators"
tags: []
---

# Parallel Scan on Ascend AI Accelerators

> [!abstract] 摘要（原文）
> 1. . We design and implement parallel pre- fix sum (scan) algorithms using Ascend AI accelera- tors. Ascend accelerators feature specialized computing units—the cube units for efficient matrix multiplication and the vector units for optimized vector operations. A key feature of the proposed scan algorithms is their ex- tensive use of matrix multiplications and accumulations enable

## 元信息
- **发表日期**: 2025/5/20
- **作者**: Bart lomiej Wr´oblewski∗ Gioele Gottardo† Anastasios Zouzias†
- **arXiv**: https://arxiv.org/abs/2505.15112
- **本地 PDF**: `papers/parallel-scan-on-ascend-ai-accelerators.pdf`
- **页数**: 16

## 图表（原文 caption + 页码）

### Figure 3 (p.3) ⭐深度解读
![[assets/parallel-scan-on-ascend-ai-accelerators-p03.png]]
> [!quote] caption
> 1 shows the Ascend architecture where the

> [!tip] 技术解读（多模态）
> 【MiniMax 解读】⭐Ascend 910B AI Core 架构(Fig.3)：单 AI Core = 1 个 AI Cube(AIC 矩阵乘引擎) + 2 个 AI Vector(AIV SIMD 核)，各有独立 Unified Buffer(UB) scratchpad，加 Memory Transfer Engine(MTE)+标量+控制块。AIC/AIV 共享全局 HBM/L2，Cube↔Vector 数据交换须走全局内存/L2（AIC 无直接写 AIV UB 的本地路径）。并行 scan：AIV 跑 element-wise/局部 scan + 解耦 look-back（在 UB 上），AIC 改作跨块前缀累积（矩阵乘式），MTE 编排块级 tile 传输。⭐结论：Ascend 非对称 Cube/Vector 划分 + UB 局部计算 + Cube↔Vector 仅全局通信→偏好 block-tiled、通信最小化的解耦 scan 设计，而非密集 GEMM 中心。直击昇腾线性注意力/SSM scan。

### Figure 4 (p.4) ⭐深度解读
![[assets/parallel-scan-on-ascend-ai-accelerators-p04.png]]
> [!quote] caption
> 1: Data path from an input tile xℓto an output tile yℓof the ScanU (Algorithm 4.1).

> [!tip] 技术解读（多模态）
> **Description (≤120 words):**
Figure 3.1 depicts the Ascend 910B AI core architecture. Global Memory connects bidirectionally to the L1 Buffer, which fans out to L0A/L0B/BT/FP Buffers feeding the Cube Unit; its output flows through the L0C Buffer and FixPipe back to Global Memory. Two AI Vector Units flank a shared Scalar Unit, each comprising a Scalar Unit, Vector Unit, and Vector Scratchpad Memory. The Cube Unit also interfaces with the Scalar Unit via the FixPipe. **Key takeaway:** the 2:1 vector-to-cube ratio (with dedicated vector scratchpads) enables flexible load balancing — a critical design point when mapping data-parallel scan kernels across these heterogeneous compute units.

**Caption (verbatim):**
Figure 3.1: Architecture of Ascend 910B accelerators. Each AI core contains one cube and two vector units.

### Figure 5 (p.7) ⭐深度解读
![[assets/parallel-scan-on-ascend-ai-accelerators-p07.png]]
> [!quote] caption
> 1: A diagram of well-known parallel scan applica- tions considered here along with their dependencies.

> [!tip] 技术解读（多模态）
> **Figure 5.1 Description**

The diagram is a directed acyclic graph (DAG) showing dependencies among parallel scan applications, organized top-down by abstraction level.

**Components (top→bottom):**
- **Parallel Scan** (root primitive, no incoming edges)
- **Split**, **Compress**, **Weighted Sampling**, **Radixsort** (intermediate operators)
- **Top-P Sampling** and **Top-K Sampling** (high-level end applications at the bottom)

**Data flow / dependencies:** Solid arrows show direct implementation dependencies — `Parallel Scan` feeds into `Split`, `Compress`, `Radixsort`, and `Weighted Sampling`. `Split` underpins `Compress`, `Radixsort`, and both sampling routines. `Compress` and `Radixsort` further feed `Top-K` and `Top-P` sampling. Dotted lines indicate indirect/transitive links (e.g., Parallel Scan ↔ Weighted Sampling, Parallel Scan ↔ Radixsort).

**Key technical takeaway:** A single low-level primitive — multi-core parallel scan (MCScan) — composes into a rich hierarchy of operators, ultimately enabling critical LLM inference primitives (top-k, top-p / nucleus sampling, radix sort) on AscendC hardware.

**Caption (verbatim):** "Figure 5.1: A diagram of well-known parallel scan applications considered here along with their dependencies."

### Figure 6 (p.8) ⭐深度解读
![[assets/parallel-scan-on-ascend-ai-accelerators-p08.png]]
> [!quote] caption
> 1:

> [!tip] 技术解读（多模态）
> ## Figure Description

**Main figure (Figure 6.1):** A line plot titled "MCSCAN Bandwidth (fp16)" showing achieved memory bandwidth (GB/s, y-axis) versus input length (x-axis, 0 to 1.0×10⁸) on the Ascend 910B4 accelerator. Five curves are compared:
- **memcpy** (yellow) — hardware peak reference, saturating near ~560 GB/s
- **s = 128** (red) — MCScan with segment size 128, saturating near ~300 GB/s
- **s = 64** (orange dashed) — saturating near ~200 GB/s
- **s = 32** (blue) — saturating near ~100 GB/s
- **PyTorch** (light blue dashed) — `torch.cumsum` baseline, remaining very low

**Key technical takeaway:** MCScan's bandwidth utilization grows monotonically with segment size *s*, with s=128 reaching ~300 GB/s versus near-zero for the PyTorch cumsum baseline — a 15.2× speedup that demonstrates larger tile sizes better saturate Ascend's memory bandwidth on 20 AI cores.

## Caption (Verbatim)

> Figure 6.1: Bandwidth of MCScan (Algorithm 4.3) for s = 32, 64, 128. MCScan has 15.2× speedup against ScanU on 910B4 (20 AI cores).

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\texttt{scan}(\z) = \matA_s\ @\ \matU_s + \matL^{-}_s\ @\ \matA_s\ @ \ \ones_s,
$$

$$
\matC_1 &= \matA_s\ @\ \ones_s \nonumber \\ \matC_2 &= \matA_s\ @\ \matU_s \nonumber \\ \matC_2 &= \matC_2 + \matL_s^{-}\ @\ \matC_1. \nonumber
$$

## 技术点深读（DEEP）

![[deep/parallel-scan-on-ascend-ai-accelerators]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/parallel-scan-on-ascend-ai-accelerators.txt`（66637 字符）供引用检索。