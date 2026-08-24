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
![[assets/crops/parallel-scan-on-ascend-ai-accelerators-fig03.png]]
*整页渲染: ![[assets/parallel-scan-on-ascend-ai-accelerators-p03.png]]*
> [!quote] caption
> 1 shows the Ascend architecture where the

> [!tip] 技术解读（多模态）
> 【图文联合解读】该图展示Ascend 910B单AI核的异构结构：1个AI Cube Unit（含L1 Buffer分解为L0A/L0B/BT/FP四个子缓冲，配套Cube Unit计算后经L0C输出，再汇入FixPipe）+ 2个对称的AI Vector Unit（各含Scalar Unit、Vector Unit与Vector Scratchpad Memory），三者均通过双向通道挂接Global Memory。

原文借此论证其"矩阵立方+向量"双计算引擎与L0/L1/Global多层内存层次，为后续parallel scan算子的硬件映射奠定基础：算法须同时利用Cube的高吞吐矩阵乘与Vector的灵活访存，才能高效实现扫描归约类操作。该图是论文方法链路中连接硬件特性与并行扫描实现策略的关键参照。

### Figure 4 (p.4) ⭐深度解读
![[assets/crops/parallel-scan-on-ascend-ai-accelerators-fig04.png]]
*整页渲染: ![[assets/parallel-scan-on-ascend-ai-accelerators-p04.png]]*
> [!quote] caption
> 1: Data path from an input tile xℓto an output tile yℓof the ScanU (Algorithm 4.1).

> [!tip] 技术解读（多模态）
> 【图文联合解读】**核心对象与结构**：展示向量 x 在 Global Memory 中的子块 **x_ℓ** 经 Cube + Vector 异构单元处理后回写为 **y_ℓ** 的完整数据通路。
- **Cube 单元**：x_ℓ→L0A，s×s 下三角单位阵 **U_s**（对角线为1）→L0B；A @ U_s 一次性算出 tile 内 s 个**并行局部前缀和**，结果落入 L1C。
- **Vector 单元**：L1C→UB，由 5 个并行加法器完成 tile 间**顺序累加**。
- 最终 y_ℓ 写回 Global Memory 的 y。

**技术结论**：ScanU 将前缀扫描拆解为「**Cube 做 tile 内并行局部扫描 + Vector 做 tile 间顺序累加**」，复用矩阵乘算力实现扫描并行化。

**论文作用**：是 Algorithm 4.1 到 Ascend 硬件映射的**桥梁图**，支撑后续性能建模与吞吐分析，论证异构 AI 加速器天然适配并行扫描负载。

### Figure 5 (p.7) ⭐深度解读
![[assets/crops/parallel-scan-on-ascend-ai-accelerators-fig05.png]]
*整页渲染: ![[assets/parallel-scan-on-ascend-ai-accelerators-p07.png]]*
> [!quote] caption
> 1: A diagram of well-known parallel scan applica- tions considered here along with their dependencies.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

该图以有向依赖图形式，自顶向下展示了"Parallel Scan"作为根节点，向下派生出 **Weighted Sampling** 与 **Split** 两条主线；Split 又分出 **Radixsort** 与 **Compress**；Radixsort 进一步支撑 **Top-K Sampling**，Weighted Sampling 衍生 **Top-P Sampling**（含虚线连接）。各应用间以实/虚箭头标注直接调用与衍生依赖。

原文借此论证关键结论：**多种主流算法（采样、基数排序、压缩、Top-K/Top-P）均可被归约为 parallel scan 原语**，因此在 Ascend 加速器上高效实现 parallel scan 即能同时加速整条应用链路。

在论文整体定位上，该图属于**动机图（motivating figure）**，位于方法章节前部，为后续面向 Ascend 的并行扫描算子设计与性能实验提供应用场景清单，论证研究工作的覆盖面与实用价值。

### Figure 6 (p.8) ⭐深度解读
![[assets/crops/parallel-scan-on-ascend-ai-accelerators-fig06.png]]
*整页渲染: ![[assets/parallel-scan-on-ascend-ai-accelerators-p08.png]]*
> [!quote] caption
> 1:

> [!tip] 技术解读（多模态）
> 【图文联合解读】图示910B4上fp16 MCSCAN带宽随输入长度(0~1×10⁸)的变化：memcpy峰值~560 GB/s，s=128/64/32分别饱和约300/200/100 GB/s，PyTorch cumsum近0。段长越大带宽越高，s=128达memcpy约53%，验证其相对ScanU 15.2×加速。作为Algorithm 4.3的实测支撑，定量呈现段长对硬件利用率的影响，佐证分段扫描方案在910B4上的高效性。

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