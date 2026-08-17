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

### Figure 4 (p.4)
![[assets/parallel-scan-on-ascend-ai-accelerators-p04.png]]
> [!quote] caption
> 1: Data path from an input tile xℓto an output tile yℓof the ScanU (Algorithm 4.1).

### Figure 5 (p.7)
![[assets/parallel-scan-on-ascend-ai-accelerators-p07.png]]
> [!quote] caption
> 1: A diagram of well-known parallel scan applica- tions considered here along with their dependencies.

### Figure 6 (p.8)
![[assets/parallel-scan-on-ascend-ai-accelerators-p08.png]]
> [!quote] caption
> 1:

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\texttt{scan}(\z) = \matA_s\ @\ \matU_s + \matL^{-}_s\ @\ \matA_s\ @ \ \ones_s,
$$

$$
\matC_1 &= \matA_s\ @\ \ones_s \nonumber \\ \matC_2 &= \matA_s\ @\ \matU_s \nonumber \\ \matC_2 &= \matC_2 + \matL_s^{-}\ @\ \matC_1. \nonumber
$$

## 全文文本
全文已存 `extraction/fulltext/parallel-scan-on-ascend-ai-accelerators.txt`（66637 字符）供引用检索。