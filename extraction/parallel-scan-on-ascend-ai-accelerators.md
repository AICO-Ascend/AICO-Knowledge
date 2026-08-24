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
> 【图文联合解读】**1) 图示对象与结构**：展示Ascend 910B单AI Core架构：含1个AI Cube Unit（Cube核心+L0A/L0B/L0C、BT/FP、L1 Buffer+FixPipe+Scalar）与2个AI Vector Unit（各含Vector核+Vector Scratchpad+Scalar），三者均经左侧Global Memory互联。

**2) 关键技术结论**：Cube与Vector各持独立scratchpad，跨单元无本地直连通路，仅能经全局内存/L2交换数据；非对称划分迫使parallel scan采用block-tiled、解耦look-back的通信最小化设计，而非GEMM中心方案。

**3) 论文方法链作用**：为解耦scan方法提供硬件依据——AIV跑element-wise/局部scan，AIC做跨块前缀累积，MTE编排块级tile传输，从而在Ascend上高效实现线性注意力/SSM scan。

### Figure 4 (p.4) ⭐深度解读
![[assets/crops/parallel-scan-on-ascend-ai-accelerators-fig04.png]]
*整页渲染: ![[assets/parallel-scan-on-ascend-ai-accelerators-p04.png]]*
> [!quote] caption
> 1: Data path from an input tile xℓto an output tile yℓof the ScanU (Algorithm 4.1).

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图4核心内容：**

图示 ScanU 单 tile（x_l → y_l）的片上数据通路。左下为 Global Memory，含输入张量 x（含 tile x_l）、上方的 U_s（通常为上一轮的累加结果），以及输出 y（含 y_l）。右上 Cube unit：从 GM 读 x_l 至 L0A（矩阵缓冲），与 L0B 中 1/0 选择矩阵（实现下三角扫描矩阵）做矩阵乘，结果落入 L1C；随后 L1C 数据经 DMA 进入右下 Vector unit 的 UB，并在 UB 内通过一串 "+" 链式累加（向量级 prefix-sum），最终写回 y_l。

**论证结论：** ScanU 把"扫描"拆解为 Cube 端的大规模矩阵乘（构造 partial sum）+ Vector 端的链式累加（完成 prefix-sum），即"超立方算子 + 向量归约"混合实现，避开显式多步同步扫描。

**在论文中的作用：** 作为 Algorithm 4.1 的微观数据流证据，支撑其"用 Cube unit 完成并行扫描主体、用 Vector unit 完成剩余归约"的核心设计；与性能模型及实验部分呼应，论证该混合策略在 Ascend 上的吞吐与访存优势。

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