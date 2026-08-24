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
> 【图文联合解读】该图上部展示3D仿生机器人：球形躯干+4条腿肢（每肢2自由度，共8维连续动作空间），置于棋盘格地面/蓝天的MuJoCo仿真环境；下部以5帧序列呈现习得步态，证明策略可驱动多肢协调移动。

原文在6.2.1 ARCHITECTURE节以该图建立具身仿真基准，论证GAE能处理躯干姿态与肢体关节耦合的高维连续控制，相对TD(λ)在多步信用分配上具优势。

该图位于方法/实验链路起点，为后续TRPO+GAE训练提供高维任务载体，支撑策略学习的定量对比。

### Figure 2 (p.10) ⭐深度解读
![[assets/crops/high-dimensional-continuous-control-using-generalized-advantage-estimation-fig02.png]]
*整页渲染: ![[assets/high-dimensional-continuous-control-using-generalized-advantage-estimation-p10.png]]*
> [!quote] caption
> Left: learning curves for cart-pole task, using generalized advantage estimation with varying values of λ at γ = 0.99. The fastest policy improvement is obtain by intermediate values of λ in the range [0.92, 0.98]. Right: performance after 20 iterations of policy optimization, as γ and λ are varied. White means higher reward. The best results are obtained at intermediate values of both. 0 100 200 

> [!tip] 技术解读（多模态）
> 【图文联合解读】左图：cart-pole在γ=0.99下10种λ设置（0/0.36/0.68/…/1.0及No VF）的cost-迭代曲线，λ∈[0.92,0.98]约30次迭代降至≈-10，No VF与λ=0仅≈-2。右图：5×7的γ-λ网格热图，20次迭代后白色（高reward）集中于γ、λ均取中间值处。论证：GAE通过λ实现偏差-方差权衡，中间值在收敛速度与最终性能上最优。该图为GAE超参选择提供经验依据，并支撑后续三维双足/四足运动等复杂任务的方法推广。

### Figure 3 (p.10) ⭐深度解读
![[assets/crops/high-dimensional-continuous-control-using-generalized-advantage-estimation-fig03.png]]
*整页渲染: ![[assets/high-dimensional-continuous-control-using-generalized-advantage-estimation-p10.png]]*
> [!quote] caption
> Left: Learning curves for 3D bipedal locomotion, averaged across nine runs of the algo- rithm. Right: learning curves for 3D quadrupedal locomotion, averaged across ﬁve runs.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图3图文联合解读**

**1) 核心对象与数据：** 左图为3D双足机器人9次平均的学习曲线，横轴为策略迭代次数0–500，纵轴代价由0降至约−2.5，涵盖10组(γ, λ)配置；其中红色曲线(γ=0.995, λ=0.98)最低降至≈−2.2。右图为3D四足机器人5次平均曲线，横轴0–1000，代价0至−12，三条γ=0.995曲线对比：λ=0.96(黄)≈−11.5最优，λ=1(橙)≈−10.5次之，无value函数(绿)≈−8.5最差。

**2) 关键结论：** 在双足上(γ, λ)敏感、最优组合落在偏倚-方差折中区；四足上明确显示GAE引入value函数(λ<1)显著优于无baseline与λ=1的vanilla策略梯度。

**3) 在论文中的作用：** 在高维连续运动控制任务上实证GAE的有效性与超参鲁棒性区间，支撑其作为TRPO优势估计核心组件的实证依据。

### Figure 4 (p.11) ⭐深度解读
![[assets/crops/high-dimensional-continuous-control-using-generalized-advantage-estimation-fig04.png]]
*整页渲染: ![[assets/high-dimensional-continuous-control-using-generalized-advantage-estimation-p11.png]]*
> [!quote] caption
> (a) Learning curve from quadrupedal walking, (b) learning curve for 3D standing up, (c) clips from 3D standing up. 7 DISCUSSION

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图4（c）可见内容解读**（图中仅含站立片段，(a)(b)学习曲线未呈现，故结合原文caption综合解读）：

**1) 核心对象与结构**
图4(c)以编号1–6的6个连续姿态，呈现3D模拟人形体由仰卧（1）→侧卧（2）→蜷缩撑地（3）→双手触地推起（4）→近直立并抬臂平衡（5）→完全站立举手（6）的运动序列；每帧姿态由MuJoCo渲染的多刚体棒人组成，对应二维状态特征。

**2) 论证的关键技术结论**
该序列与(a)四足行走、(b)3D站立学习曲线互相印证，证明GAE在高维连续控制任务（含63维髋膝踝力矩+17维刚体姿态）中可稳定收敛，并习得具备"翻身—撑起—平衡—直立"语义结构的有意义行为，而非局部最优。

**3) 在论文链路中的作用**
作为GAE从低维基准推广至类人/多足高维运动控制的核心实验证据，支撑第7节"Discussion"中关于GAE可扩展至复杂3D locomotion与manipulation类任务的结论。

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