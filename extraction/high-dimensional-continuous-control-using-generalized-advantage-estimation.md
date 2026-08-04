---
paper_num: "23"
title: "High-Dimensional Continuous Control Using Generalized Advantage Estimation"
authors: ""
date: "2026/1/19"
arxiv: "https://arxiv.org/abs/1506.02438"
pdf: "papers/high-dimensional-continuous-control-using-generalized-advantage-estimation.pdf"
slug: "high-dimensional-continuous-control-using-generalized-advantage-estimation"
tags: []
---

# High-Dimensional Continuous Control Using Generalized Advantage Estimation

> [!abstract] 摘要（原文）
> 1\. 📝 这篇论文通过引入广义优势估计（Generalized Advantage Estimation, GAE），解决了强化学习中策略梯度方法样本效率低和非稳态性问题。 2. 📝 GAE是一种指数加权的优势函数估计器，它通过在偏置与方差之间进行权衡来显著降低策略梯度估计的方差，并与基于神经网络的信赖域优化方法（包括策略和价值函数）相结合。 3. 😁 实验结果表明，该方法在三维机器人运动控制等高难度连续控制任务上取得了显著成果，能够使用高维神经网络策略学习复杂的步态。

## 元信息
- **发表日期**: 2026/1/19
- **作者**: —
- **arXiv**: https://arxiv.org/abs/1506.02438
- **本地 PDF**: `papers/high-dimensional-continuous-control-using-generalized-advantage-estimation.pdf`
- **页数**: 14

## 图表（原文 caption + 页码）

### Figure 1 (p.8)
![[assets/high-dimensional-continuous-control-using-generalized-advantage-estimation-p08.png]]
> [!quote] caption
> 6.2.1 ARCHITECTURE

### Figure 2 (p.10)
![[assets/high-dimensional-continuous-control-using-generalized-advantage-estimation-p10.png]]
> [!quote] caption
> Left: learning curves for cart-pole task, using generalized advantage estimation with varying values of λ at γ = 0.99. The fastest policy improvement is obtain by intermediate values of λ in the range [0.92, 0.98]. Right: performance after 20 iterations of policy optimization, as γ and λ are varied. White means higher reward. The best results are obtained at intermediate values of both. 0 100 200 

### Figure 3 (p.10)
![[assets/high-dimensional-continuous-control-using-generalized-advantage-estimation-p10.png]]
> [!quote] caption
> Left: Learning curves for 3D bipedal locomotion, averaged across nine runs of the algo- rithm. Right: learning curves for 3D quadrupedal locomotion, averaged across ﬁve runs.

### Figure 4 (p.11)
![[assets/high-dimensional-continuous-control-using-generalized-advantage-estimation-p11.png]]
> [!quote] caption
> (a) Learning curve from quadrupedal walking, (b) learning curve for 3D standing up, (c) clips from 3D standing up. 7 DISCUSSION

## 全文文本
全文已存 `extraction/high-dimensional-continuous-control-using-generalized-advantage-estimation.txt`（43324 字符）供引用检索。