---
paper_num: "57"
title: "Kimi K3: Open Frontier Intelligence"
authors: ""
date: "2026/7/27"
arxiv: "https://arxiv.org/abs/2607.24653"
pdf: "papers/kimi-k3-open-frontier-intelligence.pdf"
slug: "kimi-k3-open-frontier-intelligence"
tags: []
---

# Kimi K3: Open Frontier Intelligence

> [!abstract] 摘要（原文）
> We introduce Kimi K3, a 2.8T parameter Mixture-of-Experts model with 104 billion activated parameters, native vision capabilities, and a 1-million-token context window. Kimi K3 is built on Kimi Delta Attention and Attention Residuals, which improve information flow across sequence length and model depth. Together with Stable LatentMoE, which effectively activates 16 of 896 routed experts per token, and refined training and data recipes, these advances yield an approximately 2.5x improvement in overall scaling efficiency over Kimi K2. Post-training highlights reinforcement learning across general, agentic, and coding domains and multiple reasoning-effort levels, enabling compositional generalization and robust long-horizon execution. At 2.8T scale, Kimi K3 is supported by infrastructure advances in multiple areas: algorithm-system co-design for KDA, perfectly balanced expert-parallel training with efficient memory management, million-token agentic RL with persistent rollout and sandbox states, and deployment innovations. Extensive evaluations show that Kimi K3 achieves frontier-level performance across long-horizon coding, agentic, knowledge, reasoning, and vision tasks. While its overall performance still trails the most powerful proprietary models, namely Claude Fable 5 and GPT-5.6 Sol, Kimi K3 consistently outperforms other open and proprietary models evaluated in our suite. We release the full Kimi K3 model weights to facilitate future research and accelerate the broader deployment and adoption of frontier intelligence.

## 元信息
- **发表日期**: 2026/7/27
- **作者**: —
- **arXiv**: https://arxiv.org/abs/2607.24653
- **本地 PDF**: `papers/kimi-k3-open-frontier-intelligence.pdf`
- **页数**: 47

## 图表（原文 caption + 页码）

### Figure 1 (p.1)
![[assets/kimi-k3-open-frontier-intelligence-p01.png]]
> [!quote] caption
> Kimi K3 main results. 1https://huggingface.co/moonshotai/Kimi-K3[cs.CL] 7 Aug 2026

### Figure 2 (p.3) ⭐深度解读
![[assets/kimi-k3-open-frontier-intelligence-p03.png]]
> [!quote] caption
> The Kimi K3 architecture, organized around token, channel, and layer mixing, with a native vision pathway at the input.

> [!tip] 技术解读（多模态）
> Kimi K3 架构总览：每个 block 由 3 层 Kimi Delta Attention (KDA) + 1 层 Gated MLA 组成混合注意力，每个注意力层后接 Stable LatentMoE（16/896 路由专家+共享专家）做稀疏 channel mixing。深度维度引入 Attention Residuals (AttnRes)：用可学习 pseudo-query w 对 embedding 及前序各 block 输出算注意力权重 α，实现跨层选择性信息检索，突破顺序残差累积。输入侧原生视觉通路：MoonViT-V2 编码图像/视频经轻量 projector 映射进共享 embedding 空间。token/channel/layer 三维信息流设计，scaling 效率较 K2 提升 ~2.5×。

### Figure 3 (p.5) ⭐深度解读
![[assets/kimi-k3-open-frontier-intelligence-p05.png]]
> [!quote] caption
> Lower-bounded decay and its effect on chunkwise KDA computation. (a) Kimi Linear uses an unbounded negative-Softplus mapping, whereas Kimi K3 bounds the log-decay with a scaled sigmoid; the curves show A = 0 and gmin = −5. (b) Kimi Linear evaluates each diagonal tile with an explicit position-pair computation, while the bounded range in Kimi K3 allows all causal tiles to use dense Tensor Core matr

> [!tip] 技术解读（多模态）
> 下界衰减与 chunkwise KDA 计算：(a) Kimi Linear 用无界 negative-Softplus 映射 g=−e^A·Softplus(z)，K3 改为 g=g_min·Sigmoid(e^A·z) 把 log-decay 下界到 g_min=−5；(b) 有界范围使所有 causal tile（含对角 tile）都能用稠密 Tensor Core 矩阵乘，消掉逐位置对的 diagonal 路径。g_min=−5 时 16-token tile 累计 log-decay∈(−80,0)，rescale 因子 <e^80 仍在 BF16 动态范围内——分块线性注意力在 Tensor Core/NPU 上高效落地的关键参数化技巧。

### Figure 4 (p.7)
![[assets/kimi-k3-open-frontier-intelligence-p07.png]]
> [!quote] caption
> Gate and up branches of GLU, SwiGLU, and SiTU-GLU, together with their scalar responses, where σ denotes the sigmoid function. Both branches receive the scalar input x, and all curves share the domain x ∈[−10, 100]; the inset magnifies the near-origin region. SiTU-GLU, shown in red with β1 = 4 and β2 = 25, closely follows SwiGLU near the origin and approaches the bound |f(x)| ≤β1β2 = 100 for large

### Figure 5 (p.8) ⭐深度解读
![[assets/kimi-k3-open-frontier-intelligence-p08.png]]
> [!quote] caption
> Illustration of Quantile Balancing with m = 8 tokens, n = 4 routed experts, and k = 1 selected expert per token. (a)

> [!tip] 技术解读（多模态）
> **1) 架构描述**

图示展示 MoE 路由的 **Quantile Balancing (QB)** 三阶段流程：
- **(a) 不均衡路由**：8 个 token 通过 Top-1 路由到 4 个专家，产生负载 (4,3,1,0)；深色圆圈表示过载专家，浅色虚线圈表示欠训专家。
- **(b) Quantile Balancing**：每个专家列添加偏置调整 $b_j^{(t+1)} - b_j^{(t)}$（红色虚线），置于 margin $s_{i,j} + b_j^{(t)} - \alpha_i^{(t)}$ 的第 (q+1) 大值处，使得恰好 q=2 个 margin 高于阈值；★ 标记减去列调整后的行级 Top-k 选择。
- **(c) 均衡路由**：调整后负载变为 (2,2,2,2)，红色边表示被 QB 修改的分配。

**2) 关键技术要点**

**无辅助损失的负载均衡**：QB 通过单次前向传播从路由器得分分位数直接推导专家偏置 $b_j$，既调节分发又不影响混合权重 $p_{i,j}$ 与路由器梯度更新，避免了传统辅助损失在大规模专家池（如 LatentMoE 的 896 个专家）下适应性慢、易振荡的问题。**

**3) 图注逐字转录**

**Figure 5**: Illustration of Quantile Balancing with $m=8$ tokens, $n=4$ routed experts, and $k=1$ selected expert per token. (a) Token-wise Top-$k$ routing (tokens on the left, experts on the right) produces loads (4, 3, 1, 0); darker circles indicate overheated experts, whereas faded and dashed circles indicate underutilized and dying experts, respectively. (b) Each gray bar is the margin of the currently biased score, $s_{i,j} + b_j^{(t)} - \alpha_i^{(t)}$, so the row-wise maxima reproduce the routing in (a). The dashed red line in each column is the bias adjustment $b_j^{(t)} - \widehat{b}_j^{(t+1)}$, placed at the $(q+1)$-th largest margin so that exactly $q=2$ margins exceed it. The marker ★ denotes the row-wise Top-$k$ choice after subtracting the column adjustments, i.e., the routing in (c). (c) The retained choices yield the balanced load (2, 2, 2, 2); red edges denote assignments changed by **QB**.**

### Figure 6 (p.9)
![[assets/kimi-k3-open-frontier-intelligence-p09.png]]
> [!quote] caption
> Vision-tower gradient norms in our pre-training ablations. Compared with the SigLIP-initialized MoonViT-3D, the from-scratch MoonViT-V2 maintains lower gradient norms with fewer spikes, indicating more stable optimization. 9

### Figure 7 (p.11)
![[assets/kimi-k3-open-frontier-intelligence-p11.png]]
> [!quote] caption
> Fitted scaling-law curves for Kimi K2 and Kimi K3. Kimi K3 achieves 2.5× gain in scaling efficiency over Kimi K2.

### Figure 8 (p.13)
![[assets/kimi-k3-open-frontier-intelligence-p13.png]]
> [!quote] caption
> Scores and the average assistant steps across a variety of public and in-house evaluations during RL. By scaling RL FLOPs, tool-call steps scale up consistently, accompanied by a comprehensive improvement in the model’s overall capability.

### Figure 9 (p.15)
![[assets/kimi-k3-open-frontier-intelligence-p15.png]]
> [!quote] caption
> Overview of knowledge-graph-guided task synthesis. The hierarchically organized knowledge graph represents concepts at multiple levels, ranging from broad domains to fine-grained concepts. Related nodes are sampled to form a keyword set that guides the retrieval of publicly available source materials. For each synthesis instance, the system selects a task type and uses the retrieved materials to s

### Figure 10 (p.17)
![[assets/kimi-k3-open-frontier-intelligence-p17.png]]
> [!quote] caption
> Completion curves on Camera Repair Management System, a black-box system replication task in which the agent reconstructs a hidden 3D-camera repair system as a web application through oracle queries. Completion denotes verifier-assessed task progress. 5

### Figure 11 (p.19)
![[assets/kimi-k3-open-frontier-intelligence-p19.png]]
> [!quote] caption
> Computation, communication and offloading overlapped in different PP phases.

### Figure 12 (p.23)
![[assets/kimi-k3-open-frontier-intelligence-p23.png]]
> [!quote] caption
> Fine-grained prefix caching within a physical cache block. A 6144-token physical block contains twelve 512-token hash blocks, with cached MLA blocks shown in blue and empty blocks in light gray. The markers below show the KDA checkpoint status at each hash boundary. An open circle (◦) denotes a boundary without a stored checkpoint, a gray dot (•) denotes a persisted KDA checkpoint, and an orange d

### Figure 13 (p.32)
![[assets/kimi-k3-open-frontier-intelligence-p32.png]]
> [!quote] caption
> Score vs. per-task inference cost on Kimi Code Bench 2.0, BrowseComp, GDPval-AA v2, and AA-Briefcase. Kimi K3 is marked with a star.

### Figure 14 (p.33)
![[assets/kimi-k3-open-frontier-intelligence-p33.png]]
> [!quote] caption
> Case study: GPU kernel optimization on AttnRes. 7

### Figure 15 (p.34)
![[assets/kimi-k3-open-frontier-intelligence-p34.png]]
> [!quote] caption
> Case study: GPU compiler development with MiniTriton. (a) CUDA-core and (b) tensor-core rooflines of MiniTriton kernels on an NVIDIA L20 (sm_89) against torch eager, torch.compile, Triton, and cuBLAS baselines (losing points included); (c) training-loss curves of the character-level GPT trained with MiniTriton versus torch eager; (d) two-GPU data-parallel training built on MiniTriton’s own distrib

### Figure 16 (p.46)
![[assets/kimi-k3-open-frontier-intelligence-p46.png]]
> [!quote] caption
> Structure of the Kimi K3 chat template. (a) Context layout: global option messages precede the input messages, while one-shot option messages follow them, so that per-request options leave the history KV cache intact; dynamically loaded tools are injected mid-session as input option messages (dashed). (b) Anatomy of an assistant message: the body is organized into think, response, and tools channe

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\mathbf{S}_t = \left(\mathbf{I}-\beta_t\bm{k}_t\bm{k}_t^{\top}\right) \operatorname{Diag}(\bm{\alpha}_t)\mathbf{S}_{t-1} + \beta_t\bm{k}_t\bm{v}_t^{\top}, \qquad \tilde{\bm{o}}_t = \mathbf{S}_t^{\top}\bm{q}_t.
$$

$$
\bm{\gamma}_{[t]}^{i\rightarrow j} := \prod_{r=i}^{j}\bm{\alpha}_{[t]}^r, \qquad \bm{\gamma}_{[t]}^r := \bm{\gamma}_{[t]}^{1\rightarrow r}.
$$

$$
\bm{y}_t = \mathbf{W}_o\!\left[ \operatorname{Sigmoid}\!\left(\mathbf{W}_g\bm{x}_t\right) \odot \operatorname{RMSNorm}(\tilde{\bm{o}}_t) \right].
$$

$$
\bm{k}_{i} = \bm{v}_{i} = \begin{cases} \bm{h}_1 & i = 0 \\ f_i(\bm{h}_{i}) & 1 \leq i \leq l-1 \end{cases}
$$

$$
{\alpha_{i \to l}} = \frac{\phi\left(\bm{q}_{l}, \bm{k}_{i}\right)}{\sum_{j=0}^{l-1} \phi\left(\bm{q}_{l}, \bm{k}_{j}\right)}, \qquad \bm{h}_{l} = \sum_{i=0}^{l-1} {\alpha_{i \to l}} \cdot \bm{v}_{i}.
$$

$$
\mathbf{V} = \begin{cases} [\bm{b}_0, \bm{b}_1, \ldots, \bm{b}_{n-1}]^\top & \text{if } i = 1 \text{ (first layer of block } n\text{)} \\ [\bm{b}_0, \bm{b}_1, \ldots, \bm{b}_{n-1}, \bm{b}_n^{i-1}]^\top & \text{if } i \geq 2 \text{ (subsequent layers)} \end{cases}
$$

$$
\operatorname{SiTU\text{-}GLU}(\bm{x}) = \left[\beta_1\tanh\!\left(\frac{\mathbf{W}_g\bm{x}}{\beta_1}\right)\odot\operatorname{Sigmoid}(\mathbf{W}_g\bm{x})\right] \odot \left[\beta_2\tanh\!\left(\frac{\mathbf{W}_u\bm{x}}{\beta_2}\right)\right],
$$

$$
\mathcal{T}_i = \operatorname{argtop}_{k}\!\left(\bm{s}_i+\bm{b}\right), \qquad p_{i,j} = \frac{s_{i,j}}{\sum_{r\in\mathcal{T}_i}s_{i,r}}, \quad j\in\mathcal{T}_i.
$$

$$
\sum_{i=1}^{m}\mathbf{1}\!\left[s_{i,j}+\widehat{b}_j^{(t+1)}>\alpha_i^{(t)}\right],
$$

$$
\mathcal{L}_{\mathrm{LK}} = -\log \sum_{x \in \mathcal{V}} \min\!\left(p(x), q(x)\right),
$$

$$
\begin{aligned} \mathbf{M}_{[i+1]}^{t \leftarrow 1} := \prod_{r \leftarrow 1}^{t}\mathbf{M}_r \in \mathbb{R}^{d_k\times d_k}, \qquad \mathbf{S}_{[i+1]}^{t} & =\widetilde{\mathbf{S}}_{[i+1]}^{t} + \mathbf{M}_{[i+1]}^{t \leftarrow 1}\mathbf{S}_{[i]}^{T_i} \\ & = \widetilde{\mathbf{S}}_{[i+1]}^{t} + \mathbf{M}_{[i+1]}^{t \leftarrow 1}\sum_{j=1}^{i}\Big(\prod_{l \leftarrow j+1}^{i}\mathbf{M}_{[l]}^{T_l \leftarrow 1}\Big)\widetilde{\mathbf{S}}_{[j]}^{T_j}\in \mathbb{R}^{d_k\times d_v}. \end{aligned}
$$

$$
\beta\tanh\!\left(\frac{z}{\beta}\right) = z + O\!\left(\frac{z^3}{\beta^2}\right).
$$

$$
\left\|\operatorname{SiTU\text{-}GLU}(\bm{x})\right\|_{\infty} \leq \beta_1\beta_2 = 100,
$$

$$
\max_{x_{i,j}\in\{0,1\}} \sum_{i,j} x_{i,j}s_{i,j} \qquad \text{s.t.}\qquad \sum_j x_{i,j}=k, \qquad \sum_i x_{i,j}=\frac{mk}{n}.
$$

$$
\max_{x_{i,j}\in[0,1]}\min_{\alpha_i,\beta_j}\; \sum_{i,j} x_{i,j}s_{i,j} - \sum_i \alpha_i\Big(\sum_j x_{i,j} - k\Big) - \sum_j \beta_j\Big(\sum_i x_{i,j} - \tfrac{mk}{n}\Big).
$$

$$
\min_{\alpha_i,\beta_j}\max_{x_{i,j}\in[0,1]}\; \sum_{i,j} x_{i,j}\big(s_{i,j} - \alpha_i - \beta_j\big) + k\sum_i \alpha_i + \frac{mk}{n}\sum_j \beta_j.
$$

$$
\min_{\alpha_i,\beta_j}\; \mathcal{L}(\bm{\alpha},\bm{\beta}) := \sum_{i,j}\max\big(0,\; s_{i,j} - \alpha_i - \beta_j\big) + k\sum_i \alpha_i + \frac{mk}{n}\sum_j \beta_j.
$$

$$
\min_{\alpha}\; k\alpha + \sum_{j}\max\big(0,\; s_{i,j} - \beta_j - \alpha\big).
$$

$$
\alpha_i^* = \operatorname{quantile}_{1-k/n}\big(\bm{s}_i - \bm{\beta}\big).
$$

$$
\beta_j^* = \operatorname{quantile}_{1-k/n}\big(\bm{s}_{:,j} - \bm{\alpha}\big).
$$

## 技术点深读（DEEP）

![[deep/kimi-k3-open-frontier-intelligence]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/kimi-k3-open-frontier-intelligence.txt`（189122 字符）供引用检索。