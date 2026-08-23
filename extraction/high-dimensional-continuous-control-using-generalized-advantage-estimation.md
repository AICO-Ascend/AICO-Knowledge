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

### Figure 1 (p.8) ⭐深度解读
![[assets/crops/high-dimensional-continuous-control-using-generalized-advantage-estimation-fig01.png]]
*整页渲染: ![[assets/high-dimensional-continuous-control-using-generalized-advantage-estimation-p08.png]]*
> [!quote] caption
> 6.2.1 ARCHITECTURE

> [!tip] 技术解读（多模态）
> **Description:**

The figure presents a side-by-side comparison of two simulated agents in a physics-based 3D environment (checkerboard-floored scene, MuJoCo-style). 

**Left panel:** A bipedal humanoid torso with two legs, rendered in an upright T-pose, shown in a standard reference configuration. **Right panel:** A quadrupedal/arachnid-like creature with a central body and four radiating limbs, shown in a crouched/grounded pose.

**Bottom strips (data flow / temporal sequence):** Below each main render is a timeline of five smaller snapshots showing learned motion primitives — a walking gait for the humanoid (sequential forward-stepping frames) and a crawling/locomotion gait for the quadruped (sequential reaching/contact frames). The arrows imply temporal progression from left → right.

**Key technical takeaway:** The figure illustrates that a single learned policy framework can generalize across morphologically distinct embodiments (biped vs. quadruped), producing stable cyclic locomotion gaits purely from physics simulation without hand-engineered controllers.

**Caption (verbatim):**
*No caption text is rendered within the figure itself; only image panels are shown.*

### Figure 2 (p.10) ⭐深度解读
![[assets/crops/high-dimensional-continuous-control-using-generalized-advantage-estimation-fig02.png]]
*整页渲染: ![[assets/high-dimensional-continuous-control-using-generalized-advantage-estimation-p10.png]]*
> [!quote] caption
> Left: learning curves for cart-pole task, using generalized advantage estimation with varying values of λ at γ = 0.99. The fastest policy improvement is obtain by intermediate values of λ in the range [0.92, 0.98]. Right: performance after 20 iterations of policy optimization, as γ and λ are varied. White means higher reward. The best results are obtained at intermediate values of both. 0 100 200 

> [!tip] 技术解读（多模态）
> **Description:** The page presents two figures from an ICLR 2016 paper on generalized advantage estimation (GAE). **Figure 2 (top)** compares cart-pole performance: the left panel plots cost vs. policy iterations for varying λ (0–1) at γ=0.99, while the right panel is a heatmap of final performance across a γ×λ grid (white = higher reward). **Figure 3 (bottom)** shows learning curves for 3D bipedal locomotion (left, 9 runs, varying γ∈[0.96,1] and λ∈[0.96,1]) and 3D quadrupedal locomotion (right, 5 runs, comparing γ=0.995 with no value fn, λ=1, and λ=0.96). All plots share axes of cost (vertical) vs. number of policy iterations (horizontal).

**Key takeaway:** Intermediate λ values (≈0.92–0.99) consistently outperform extreme settings, empirically validating the bias–variance sweet spot in GAE across tasks.

**Caption (verbatim):**

*Figure 2:* Left: learning curves for cart-pole task, using generalized advantage estimation with varying values of λ at γ = 0.99. The fastest policy improvement is obtain by intermediate values of λ in the range [0.92, 0.98]. Right: performance after 20 iterations of policy optimization, as γ and λ are varied. White means higher reward. The best results are obtained at intermediate values of both.

*Figure 3:* Left: Learning curves for 3D bipedal locomotion, averaged across nine runs of the algorithm. Right: learning curves for 3D quadrupedal locomotion, averaged across five runs.

### Figure 3 (p.10) ⭐深度解读
![[assets/crops/high-dimensional-continuous-control-using-generalized-advantage-estimation-fig03.png]]
*整页渲染: ![[assets/high-dimensional-continuous-control-using-generalized-advantage-estimation-p10.png]]*
> [!quote] caption
> Left: Learning curves for 3D bipedal locomotion, averaged across nine runs of the algo- rithm. Right: learning curves for 3D quadrupedal locomotion, averaged across ﬁve runs.

> [!tip] 技术解读（多模态）
> **Description:** The page presents two figures from an ICLR 2016 paper on generalized advantage estimation (GAE). **Figure 2 (top)** compares cart-pole performance: the left panel plots cost vs. policy iterations for varying λ (0–1) at γ=0.99, while the right panel is a heatmap of final performance across a γ×λ grid (white = higher reward). **Figure 3 (bottom)** shows learning curves for 3D bipedal locomotion (left, 9 runs, varying γ∈[0.96,1] and λ∈[0.96,1]) and 3D quadrupedal locomotion (right, 5 runs, comparing γ=0.995 with no value fn, λ=1, and λ=0.96). All plots share axes of cost (vertical) vs. number of policy iterations (horizontal).

**Key takeaway:** Intermediate λ values (≈0.92–0.99) consistently outperform extreme settings, empirically validating the bias–variance sweet spot in GAE across tasks.

**Caption (verbatim):**

*Figure 2:* Left: learning curves for cart-pole task, using generalized advantage estimation with varying values of λ at γ = 0.99. The fastest policy improvement is obtain by intermediate values of λ in the range [0.92, 0.98]. Right: performance after 20 iterations of policy optimization, as γ and λ are varied. White means higher reward. The best results are obtained at intermediate values of both.

*Figure 3:* Left: Learning curves for 3D bipedal locomotion, averaged across nine runs of the algorithm. Right: learning curves for 3D quadrupedal locomotion, averaged across five runs.

### Figure 4 (p.11) ⭐深度解读
![[assets/crops/high-dimensional-continuous-control-using-generalized-advantage-estimation-fig04.png]]
*整页渲染: ![[assets/high-dimensional-continuous-control-using-generalized-advantage-estimation-p11.png]]*
> [!quote] caption
> (a) Learning curve from quadrupedal walking, (b) learning curve for 3D standing up, (c) clips from 3D standing up. 7 DISCUSSION

> [!tip] 技术解读（多模态）
> ## Figure Description

The main figure (Figure 4) contains two side-by-side panels evaluating the 3D Standing Up task for simulated robotic locomotion:

**Left panel — Learning curve:** A 2D plot of *cost* (y-axis, 0.0–2.5) versus *number of policy iterations* (x-axis, 0–500). Three configurations are compared:
- γ=0.99, No value fn (green) — plateaus highest at ~1.0
- γ=0.99, λ=1 (orange) — converges to ~0.5
- γ=0.99, λ=0.96 (yellow) — achieves lowest cost (~0.4), with error bars

**Right panel — Trajectory clips:** Six sequential 3D humanoid poses (labeled 1–6) depicting the simulated robot transitioning from a supine position (1) through intermediate pushing/rising poses (2–5) to a fully upright standing posture (6).

**Key technical takeaway:** Introducing a learned value-function baseline with λ=0.96 yields substantially faster and lower asymptotic cost than omitting the value function entirely, demonstrating that variance reduction via the generalized advantage estimator is critical for high-dimensional locomotion control.

## Verbatim Caption

**Figure 4:** (a) Learning curve from quadrupedal walking, (b) learning curve for 3D standing up, (c) clips from 3D standing up.

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\begin{tabular}{cc} Task & Reward \\ \hline 3D biped locomotion & $v_{\mathrm{fwd}} - 10^{-5} \norm{u}^2 - 10^{-5} \norm{\fimp}^2 + 0.2$\\ Quadruped locomotion & $v_{\mathrm{fwd}} - 10^{-6} \norm{u}^2 - 10^{-3}\norm{\fimp}^2 + 0.05$\\ Biped getting up & $-(h_{\rm head} - 1.5)^2 - 10^{-5} \norm{u}^2$\\ \end{tabular}
$$

$$
\bg = \Ea{\sum_{t=0}^{\infty} \Psi_t \gradth \log \pith(a_t \given s_t)},
$$

$$
\Vpi(s_t) &\defeq \Eb{\substack{s_{t+1:\infty},\\a_{t:\infty} } }{\sum_{\delay=0}^{\infty} r_{t+\delay}} \hspace{0.5in} \Qpi(s_t,a_t) \defeq \Eb{\substack{s_{t+1:\infty},\\a_{t+1:\infty}}}{\sum_{\delay=0}^{\infty} r_{t+\delay}} \\ \Api(s_t, a_t) &\defeq \Qpi(s_t, a_t) - \Vpi(s_t), \quad \text{(Advantage function)}.
$$

$$
\Vpigam(s_t) &\defeq \Eb{\substack{s_{t+1:\infty},\\a_{t:\infty} } }{\sum_{\delay=0}^{\infty} \gamma^{\delay} r_{t+\delay}}\hspace{0.5in} \Qpigam(s_t,a_t) \defeq \Eb{\substack{s_{t+1:\infty},\\a_{t+1:\infty}}}{\sum_{\delay=0}^{\infty} \gamma^{\delay} r_{t+\delay}}\\ \Apigam(s_t, a_t)&\defeq\Qpigam(s_t,a_t) - \Vpigam(s_t).
$$

$$
\bgrad &\defeq \Eb{\substack{s_{0:\infty}\\ a_{0:\infty}}}{ \sum_{t=0}^{\infty}\Apigam(s_t,a_t) \gradth \log \pith(a_t \given s_t)}.
$$

$$
\Eb{\substack{s_{0:\infty}\\ a_{0:\infty}}}{ \hata_t(s_{0:\infty},a_{0:\infty}) \gradth \log \pith(a_t \given s_t)} = \Eb{\substack{s_{0:\infty}\\ a_{0:\infty}}}{ \Apigam(s_t,a_t) \gradth \log \pith(a_t \given s_t)}.
$$

$$
\Eb{\substack{s_{0:\infty}\\ a_{0:\infty}}}{ \sum_{t=0}^{\infty}\hata_t(s_{0:\infty},a_{0:\infty}) \gradth \log \pith(a_t \given s_t)} = \bgrad
$$

$$
\hat g = \frac{1}{N} \sum_{n=1}^N \sum_{t=0}^{\infty} \hata_t^n \gradth \log \pith(a_t^n \given s_t^n)
$$

$$
\Eb{s_{t+1}}{\delta^{\Vpigam}_t} &= \Eb{s_{t+1}}{r_t + \gamma \Vpigam(s_{t+1}) - \Vpigam(s_t)} \nonumber \\ &= \Eb{s_{t+1}}{\Qpigam(s_t, a_t) - \Vpigam(s_t)}= \Apigam(s_t, a_t).
$$

$$
\hata_t^{(k)} &\defeq \sum_{\delay=0}^{k-1} \gamma^{\delay} \dv_{t+l} = -V(s_t) + r_t + \gamma r_{t+1} + \dots + \gamma^{k-1} r_{t+k-1} + \gamma^{k} V(s_{t+k})
$$

$$
\hata_t^{(\infty)} = \sum_{\delay=0}^{\infty} \gamma^{\delay} \dv_{t+l} = -V(s_t) + \sum_{\delay=0}^{\infty} \gamma^{\delay} r_{t+\delay},
$$

$$
\hatalam_t &\defeq (1-\lambda)\lrparen*{ \hata_t^{(1)} + \lambda \hata_t^{(2)} + \lambda^2 \hata_t^{(3)} + \dots }\nonumber \\ &= (1-\lambda)\lrparen*{ \dv_t + \lambda (\dv_t + \gamma \dv_{t+1}) + \lambda^2 (\dv_t + \gamma \dv_{t+1} + \gamma^2 \dv_{t+2}) + \dots }\nonumber \\ &= (1-\lambda)( \dv_t (1 + \lambda + \lambda^2 + \dots) +\gamma \dv_{t+1} (\lambda + \lambda^2 + \lambda^3 + \dots)\nonumber \\ &\ \ \ \ \ \ \ \ \ \ \ +\gamma^2 \dv_{t+2} (\lambda^2 + \lambda^3 + \lambda^4 + \dots) +\dots) \nonumber \\ &= (1-\lambda)\lrparen*{ \dv_t \lrparen*{\frac{1}{1-\lambda}} +\gamma \dv_{t+1} \lrparen*{\frac{\lambda}{1-\lambda}} +\gamma^2 \dv_{t+2} \lrparen*{\frac{\lambda^2}{1-\lambda}} +\dots} \nonumber \\ &= \sum_{\delay=0}^{\infty} (\gamma \lambda)^{\delay} \dv_{t+\delay}
$$

$$
\bgrad &\approx \Ea{\sum_{t=0}^{\infty} \gradth \log \pith(a_t \given s_t) \hatalam_t} = \Ea{\sum_{t=0}^{\infty} \gradth \log \pith(a_t \given s_t) \sum_{\delay=0}^{\infty} (\gamma \lambda)^{\delay}\dv_{t+\delay}},
$$

$$
\tilr(s,a,s') = r(s,a,s') + \gamma \Phi(s') - \Phi(s),
$$

$$
\sum_{\delay=0}^{\infty} \gamma^{\delay}\tilr(s_{t+\delay},a_t,s_{t+\delay+1}) &= \sum_{\delay=0}^{\infty} \gamma^{\delay}r(s_{t+\delay},a_{t+\delay},s_{t+\delay+1}) - \Phi(s_{t}).
$$

$$
\tilde{Q}^{\pi,\gamma}(s, a) &= \Qpigam(s,a) - \Phi(s)\\ \tilde{V}^{\pi,\gamma}(s, a) &= \Vpigam(s) - \Phi(s)\\ \tilde{A}^{\pi,\gamma}(s, a) &= (\Qpigam(s,a) - \Phi(s)) - (\Vpigam(s) - \Phi(s)) = \Apigam(s,a).
$$

$$
\sum_{\delay=0}^{\infty} (\gamma \lambda)^{\delay}\tilr(s_{t+\delay},a_t,s_{t+\delay+1}) &= \sum_{\delay=0}^{\infty} (\gamma \lambda)^{\delay} \dv_{t+\delay} = \hatalam_t.
$$

$$
\resp(\delay; s_t, a_t) = \Ea{r_{t+\delay} \given s_t, a_t} - \Ea{r_{t+\delay} \given s_t}.
$$

$$
\gradth \log \pith(a_t \given s_t) A^{\pi,\gamma}(s_t, a_t) &= \gradth \log \pith(a_t \given s_t) \sum_{\delay=0}^{\infty} \gamma^{\delay} \chi(\delay; s_t,a_t) .
$$

$$
\minimize_{\phi} \sum_{n=1}^N \norm{ V_{\phi}(s_n) - \Vhat_n }^2,
$$

## 技术点深读（DEEP）

![[deep/high-dimensional-continuous-control-using-generalized-advantage-estimation]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/high-dimensional-continuous-control-using-generalized-advantage-estimation.txt`（43324 字符）供引用检索。