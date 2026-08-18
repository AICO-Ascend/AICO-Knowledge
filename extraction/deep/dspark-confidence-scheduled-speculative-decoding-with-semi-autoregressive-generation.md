<!-- 独立文件：DSpark 深读 note，与 extract_phase1 生成的 MD/MOC 解耦；深读内容只写本文件，不回灌 MD body。M3 figure caption 来源：extraction/minimax_captions.json（key 前缀 ...-p04，共 1 张，对应 Figure 1 DSpark 架构与解码循环总览）。Figure 2-8 的 verbatim caption 见 fulltext。公式权威源：extraction/formulas.json（20 条 LaTeX，覆盖 Eq.1-12 + Algorithm 1 目标 + Appendix A 反例）。DEEP 重写 2026-08-18：全部核心公式改为 formulas.json 权威 LaTeX（$$ 包裹），补全 Appendix A selection-bias 反例的 LaTeX 渲染。-->
# DSpark: Confidence-Scheduled Speculative Decoding with Semi-Autoregressive Generation — 技术点深读（DEEP 重写 2026-08-18）

## 核心问题

DSpark 攻击的是推测解码（speculative decoding）在生产级高并发推理服务中两个相互耦合的瓶颈。per-token 延迟模型（§2.1，式 1，权威 LaTeX）：

$$L = \frac{T_{\text{draft}} + T_{\text{verify}}}{\tau}.$$

三个杠杆：降 `T_draft`、提 τ、降有效 `T_verify`。Figure 1（p.4）的总览图把这两类瓶颈及其互补对策一次画清——其 verbatim caption（fulltext lines 234–241）描述了完整解码循环：target model 先用 prompt `ABC` 跑一步得到 anchor token `D`；DSpark 以 `D` 为输入，经"heavy parallel backbone + lightweight sequential head"产出 draft token `EFGH` 及置信度 `c1–c4`；Hardware-Aware Prefix Scheduler 评估这些分数保留 prefix `EFG`、丢掉低置信度 `H`；最后 target model 并行验证被调度的 prefix，`E F` 被接受、`G` 被拒绝，target 生成修正 token `G*` 完成本轮。

**LaTeX↔M3 双源校验**：M3 对 p04 的解读与 verbatim caption + 式 1 完全一致——M3 复述"L = (T_draft + T_verify)/τ"，并指出上半支 semi-autoregressive generation（§3.1）以并行 backbone 承担 bulk draft 计算（保持 `T_draft` 近似与 block size γ 无关），再接轻量 sequential block 注入 draft token 间依赖、廉价抬高接受率 τ；下半支 confidence-scheduled verification（§3.2）用 confidence head 估计 per-position 接受概率，hardware-aware scheduler 剪掉低置信度尾部 token，削减冗余 `T_verify`。M3 进一步点出"DSpark decouples draft latency (parallel backbone) from draft quality (sequential dependency injection) and prunes verification by confidence"——与 caption 中 `EFGH → 保留 EFG / 丢弃 H` 的图示、以及 Algorithm 1 的全局吞吐最大化目标完全吻合。双源无冲突。

**生成质量侧瓶颈（§1, §3.1）**：并行 drafter（DFlash、Medusa）单次 forward 产出全部 γ 个 draft token，使 `T_draft` 几乎与 γ 无关，理论上可堆深网络 + 长 block。但每位置**独立预测**，无法建模 block 内 inter-token dependency。后果是**multi-modal collision**：当上下文存在多个合理续写（如 "of course" / "no problem"），并行 drafter 把不同模式片段拼成 "of problem" / "no course"，因为每位置 marginalize 了所有可能前驱而非 condition 在已采样的前驱上（§3.1）。这导致**沿 block 快速 suffix decay**，γ 越长浪费越多。

**系统效率侧瓶颈（§1, §3.2）**：即便能生成长 block，**无差别验证全部 draft token** 在高并发下严重退化吞吐。理想验证长度沿两轴变化：(1) 数据侧——code/数学高接受率，开放 chat 低接受率；(2) 系统侧——轻载时多验证一个 token 几乎免费，重载时每个高拒绝风险的 token 占用本可服务其他请求的 batch capacity（§1）。理想验证长度应是 **per-request 动态、load-aware** 的。两个瓶颈耦合：质量侧 suffix decay 让"长 block 是否值得验证"成疑；系统侧若不解决，质量侧的长 block 反而有害。DSpark 的贡献是把两者**统一**到一个 framework。

## 关键创新点

1. **Semi-autoregressive generation（半自回归生成，§3.1）**
   - 机制：保留 DFlash 作为重的并行 backbone（单次 forward 产出 `h_1..h_γ` 与 base logits `U_1..U_γ`），追加**轻量 sequential head** 注入 block 内 prefix 依赖。draft 分布被自回归分解为因果 block 分布（§3.1，式 4，权威 LaTeX）：

     $$P(X \mid x_0) = \prod_{k=1}^{\gamma} p_k(x_k \mid x_0, x_{<k}), \qquad p_k(v \mid x_0, x_{<k}) = \frac{ \exp\!\left(U_k(v) + B_k(x_0, x_{<k}, v)\right) }{ \sum_{u \in \mathcal{V}} \exp\!\left(U_k(u) + B_k(x_0, x_{<k}, u)\right) }.$$

     其中 `x_0` 为上一验证周期的 anchor token，`U_k` 为并行 backbone 在位置 k 产出的 base logit，`B_k` 即 prefix-dependent transition bias。关键约束：保持 `T_sequential ≪ T_parallel`，使总体 draft latency 仍由并行阶段主导——这正是 Figure 1 caption 中"heavy parallel backbone + lightweight sequential head"分工的数学化表达。
   - 两种实例化（§3.1）：
     - **Markov head**（默认）：`B_k` 仅依赖上一 token，低秩分解 `B = W_1 W_2`，`W_1 ∈ R^{V×r}` 作 embedding lookup、`W_2 ∈ R^{r×V}` 作 logit projection（§3.1，式 5，权威 LaTeX）：

       $$B(x_{k-1},\, \cdot\,) = W_1[x_{k-1}] \, W_2 \;\in\; \RR^{V}.$$

       per-step 计算仅一次 lookup + 一次矩阵-向量积，低秩 `r=256` 对大词表仍高效。机制直击 multi-modal collision：位置 1 一旦采到 "of"，Markov head 在位置 2 抬高 "course" 抑制 "problem"（§3.1）。
     - **RNN head**：维护 recurrent state `s_k` 累积全 prefix 历史，输入 `z_k = [s_{k-1}; W_1[x_{k-1}]; h_k] ∈ R^{2r+d}`，gated update 与 bias（§3.1，式 6，权威 LaTeX）：

       $$\begin{aligned} s_k = \sigma(W_g\, z_k)& \odot s_{k-1} \;+\; \bigl(1 - \sigma(W_g\, z_k)\bigr) \odot \tanh(W_c\, z_k), \\ &B_k(x_{<k},\, \cdot\,) = W_2^\top\, \tanh(W_o\, z_k), \end{aligned}$$

       其中 `W_g, W_c, W_o ∈ R^{r×(2r+d)}` 由单一线性 projection 切分为 gate/candidate/output，`s_0` 初始化为零。
   - 额外改动：把 DFlash 的 anchor token 也当作第一个预测位置（anchor + γ−1 masks → γ logits），减少 draft 计算同时维持质量（§3.1）。
   - 效果（§4.2）：在 Qwen3-{4B,8B,14B} 上，macro-average accepted length τ 相对 autoregressive Eagle3 提升 **30.9% / 26.7% / 30.0%**，相对 parallel DFlash 提升 **16.3% / 18.4% / 18.3%**；在 Gemma4-12B 上同样泛化。Position-wise 分析（§4.3.1，Figure 2）显示 DSpark 继承并行 backbone 的高初始接受率（Math 起始 0.93），同时 sequential head 抑制 suffix decay，全 block 维持高且稳定的 conditional acceptance。**2 层 DSpark 即超过 5 层 DFlash**（§4.3.2，Figure 3），证明少量 autoregression 参数效率极高。latency overhead（§4.3.2，Figure 4 右图）：draft 长度从 4→16 仅增加 **0.2%–1.3%** 全轮延迟（batch=128，跨 {512,1024,2048,4096} context 平均），换来最高 30% 的 τ 提升。

2. **Confidence head + STS 校准（§3.2.1）**
   - 机制：每个 draft 位置输出标量 `c_k ∈ (0,1)`，建模**条件存活概率**——给定前缀全部被接受，第 k 个 token 存活的概率。架构为轻量线性 projection + sigmoid（§3.2.1，式 7，权威 LaTeX）：

     $$c_k = \sigma\bigl(w^\top [h_k;\, W_1[x_{k-1}]]\bigr),$$

     其中 `h_k` 为 backbone hidden state，`W_1[x_{k-1}]` 为前一 draft token 的 Markov embedding。监督标签为解析的 per-step acceptance rate（§3.2.1，式 8，权威 LaTeX）：

     $$c_k^* = 1 - \tfrac{1}{2}\|p_k^d - p_k^t\|_1.$$

     即 draft 与 target 分布 total variation 距离的补。
   - **Sequential Temperature Scaling (STS)**：scheduler 需要的是**累积存活概率**的绝对量级（用于算期望 τ），而神经置信度估计系统性 overconfident。STS 利用链式法则，joint 接受概率 = 累积积 `Π_{i≤k} c_i`；在 held-out validation set 上从左到右**逐位置**做 1D grid search 找最优温度，最小化累积积的 ECE，且每次固定前面已校准的分数。温度缩放是 order-preserving，不破坏置信度头学到的相对排序。
   - 效果（§4.3.3，Figure 6 reliability diagram）：原始估计 ROC-AUC 0.81–0.90（Position 1: AUC 0.818 ECE 5.7%→2.0%；Position 3: 0.812, 8.2%→1.7%；Position 5: 0.864, 5.8%→0.8%；Position 7: 0.907, 3.3%→0.4%）但 ECE 3%–8%；STS 后平均 ECE 降至 ~1%。

3. **Hardware-aware prefix scheduler（§3.2.2，Algorithm 1）**
   - 机制：把验证长度选择形式化为**全局吞吐最大化问题**。对 R 个并发请求，每个请求有 `ℓ_r ∈ {0..γ}` 的验证长度。survival prob（§3.2.2，权威 LaTeX）：

     $$a_{r,j} = \prod_{i \leq j} c_{r,i}$$

     （累积积，单调非增）。batch 总 token 数 `B = Σ(1+ℓ_r)`，期望接受 token 数 `τ = Σ(1 + Σ_{j≤ℓ_r} a_{r,j})`，目标 `Θ = τ · SPS(B)`，其中 `SPS(B)` 是引擎 profiled 的 steps-per-second 容量曲线（初始化时测一次、存为 cost table）。Figure 1 中"Hardware-Aware Prefix Scheduler 保留 EFG、丢弃 H"正是此算法的单请求投影。
   - 因 `a_{r,j}` 单调非增，全局按 survival prob 降序排序候选即天然遵守 intra-block prefix 依赖，**贪心 admission** 即可。当 `Θ` 不再增长时 early-stop。
   - **lossless 保证（§3.2.2, §5.2, Appendix A）**：speculative decoding 的 non-anticipating property 要求 admission 决策不能依赖未来候选 token。由于 confidence head 用 Markov 特征（上一采样 token），计算下一个 `a_{r,k+1}` 需要已实例化的 `x_{r,k}`，回顾式全局搜索会把 `x_{r,k}` 泄漏进第 k 步的 admission 决策，引入 selection bias。早期 stopping 机制使截断决策只依赖已处理的 prefix，隔离未来 token，确保精确恢复 target 分布。
   - **生产级异步改造（§5.2）**：真实硬件 SPS(B) 是 jagged step-wise，且 ZOS（Zero-Overhead Scheduling）/CUDA graph replay 要求下一步 batch size 在当前步完成前已知。冲突解决：用**两步前**的 confidence head 输出近似 upcoming verification capacity，当前步的候选 token 仍严格按**真实、最新**的累积置信度排序——历史预测仅用于决定动态截断长度 K（dynamic top-K selection），保证 rank-preserving。更进一步，移除 early-stopping break 做无约束全局搜索（正常会破坏 lossless 保证），但因 ZOS 使决策只依赖两步前的历史信息，自然形成 causal barrier，决策隔离于当前 token `x_{r,k}` 的实现，仍保持精确 target 分布。
   - **变长执行（§5.3）**：标准 decode kernel 优化为固定 query length，变长 prefix 会导致 padding 浪费。DSpark 将所有 token 跨请求 flatten 当独立元素处理，intra-sequence 依赖通过 sparse attention 中的 marker tensor 传达。DeepSeek-V4 上只需修改 index-attention 与 compress kernel。
   - 效果（§5.4，Figure 7 Pareto frontier + Figure 8 load-adaptive）：DeepSeek-V4-Flash 上相对 MTP-1 baseline，在 80 tok/s/user SLA 下吞吐 +51%、matched-throughput 下 per-user 速度 +60%–85%；在 120 tok/s/user SLA 下基准进入低并发 regime、DSpark 名义吞吐 +661%。V4-Pro 上 35 tok/s/user SLA 吞吐 +52%，50 tok/s/user SLA 名义 +406%，matched throughput 下 +57%–78%。scheduler 在 <200（Flash）/ <150（Pro）并发时分配 4–6 token 验证预算（vs MTP-1 静态 2），并发升高时动态缩减预算（Figure 8 底排）。

4. **Training 目标（§3.3）**
   - 三项 loss，均按 `w_k = exp(−(k−1)/γ)` 位置加权（强调前部位置因 prefix verification 下贡献更大）：
     - `L_ce`：next-token cross-entropy（§3.3，式 9，权威 LaTeX）：

       $$\Ll_{\text{ce}} = -\sum_{k=1}^{\gamma} w_k \log p^d_{k}(x_k^*).$$

     - `L_tv`：draft vs target 分布的 total variation 距离（§3.3，式 10，权威 LaTeX），直接最大化 acceptance rate（因 per-step acceptance = `1 − ½‖p_d − p_t‖₁`）：

       $$\Ll_{\text{tv}} = \sum_{k=1}^{\gamma} w_k \|p_k^d - p_k^t\|_1.$$

     - `L_conf`：二值 BCE，训练 confidence head 预测 `c*_k`（§3.3，式 11，权威 LaTeX）：

       $$\Ll_{\text{conf}} = -\sum_{k=1}^{\gamma} w_k \bigl[c_k^* \log c_k + (1 - c_k^*) \log(1 - c_k)\bigr].$$

   - 总目标（§3.3，式 12，权威 LaTeX），默认权重 `α_ce=0.1, α_tv=0.9, α_conf=1.0`：

     $$\Ll = \alpha_{\text{ce}}\,\Ll_{\text{ce}} + \alpha_{\text{tv}}\,\Ll_{\text{tv}} + \alpha_{\text{conf}}\,\Ll_{\text{conf}}.$$

     target model 全程 frozen；drafter 共享 target 的 embedding 层与 LM head 且 frozen，只更新 backbone + sequential block + confidence head。

5. **Scalable training 工程优化（§5.1）**
   - **Hidden state communication**：跨 worker 传 `V≈10^5` 全词表 logits 是带宽瓶颈；改为缓存 target model forward activations，仅传 LM head 前的 hidden states，LM head 投影在 drafter worker 本地只对采样位置执行，per-token 通信降到 `O(d)`。
   - **Anchor-bounded sequence packing**：用 token-level attention indices 而非 2D mask 管理多个独立 anchor 块的 packing，维持精确 causal masking，避免标准 padding 的计算/内存开销，使 drafter 计算成本与 target context length 解耦。

6. **Appendix A 反例：无 early-stopping 的 selection bias（§A，公式式 12-19）**
   - 这是 lossless 保证的**严格证明**，原 note 仅 prose 描述，此处补全权威 LaTeX。设定：单请求 R=1，最大 draft 长度 γ=2，首位置 survival prob `a_1 = 0.8`，profiled 容量曲线（§A，权威 LaTeX）：

     $$\mathrm{SPS}(1) = 1.0,\qquad \mathrm{SPS}(2) = 0.5,\qquad \mathrm{SPS}(3) = 0.45.$$

   - 验证 0 与 1 个 draft token 的期望吞吐（§A，权威 LaTeX）：

     $$\Theta_0 = 1 \cdot \mathrm{SPS}(1) = 1.0, \quad \Theta_1 = (1 + 0.8) \cdot \mathrm{SPS}(2) = 0.9.$$

   - 因 Markov confidence head 用上一采样 token，下一置信度 `c_2` 显式依赖 `x_1` 的实现，故第二前缀存活概率（§A，权威 LaTeX）：

     $$a_2 = a_1 c_2$$

     也依赖 `x_1`。
   - **Case 1**（`x_1` 产生高 `c_2=0.9`，§A，权威 LaTeX）：

     $$a_2 = 0.8 \times 0.9 = 0.72, \qquad \Theta_2 = (1 + 0.8 + 0.72) \times 0.45 = 1.134.$$

     `Θ_2` 为全局最大，scheduler 返回 ℓ=2，`x_1` 被准入。
   - **Case 2**（`x_1` 产生低 `c_2=0`，§A，权威 LaTeX）：

     $$\Theta_2 = (1 + 0.8 + 0) \times 0.45 = 0.81.$$

     全局最大仍是 `Θ_0=1.0`，scheduler 返回 ℓ=0，`x_1` 不被准入。
   - **分布偏置显式化**：词表 {A, B}，首位置 target 与 draft 分布（§A，权威 LaTeX）：

     $$p_{\mathrm{t}}(A)=0.7,\qquad p_{\mathrm{t}}(B)=0.3, \qquad p_{\mathrm{d}}(A)=0.5,\qquad p_{\mathrm{d}}(B)=0.5.$$

     标准推测接受概率 = `min(0.7,0.5)+min(0.3,0.5)=0.8`，匹配 `a_1=0.8`。若回顾式 scheduler 按上述行为：`x_1=A` 则 ℓ=2 且接受概率 `min(1, 0.7/0.5)=1`；`x_1=B` 则 ℓ=0，target 重新从 `p_t` 采样。最终 `Pr(Y=A)=0.5·1 + 0.5·0.7 = 0.85`、`Pr(Y=B)=0.15`，输出分布 (0.85, 0.15) ≠ target (0.7, 0.3)——**非 lossless**。early-stopping 在 `Θ_1 < Θ_0` 时立即停止并返回 ℓ=0，在评估任何依赖 continuation 的量（如 `c_2`）之前，admission 决策只依赖 pre-token 信息，恢复 non-anticipating property。生产侧 ZOS 改造的 causal barrier 是此性质的工程对应物。

## 表格（原文结构化）

### Table 1：主结果——accepted length τ（per decoding round，含 bonus token）

| Target | Drafter | GSM8K | MATH500 | AIME25 | MBPP | HumanEval | LCB | MT-Bench | Alpaca | Arena-Hard |
|---|---|---|---|---|---|---|---|---|---|---|
| Qwen3-4B | Eagle3 | 5.14 | 4.62 | 3.92 | 3.69 | 4.16 | 3.77 | 2.39 | 2.26 | 2.55 |
| Qwen3-4B | DFlash | 5.40 | 4.85 | 4.15 | 4.40 | 4.74 | 4.18 | 3.07 | 2.96 | 2.83 |
| Qwen3-4B | **DSpark** | **6.11** | **5.70** | **4.89** | **5.13** | **5.38** | **4.86** | **3.64** | **3.54** | **3.29** |
| Qwen3-8B | Eagle3 | 5.30 | 4.77 | 3.91 | 3.96 | 4.33 | 4.17 | 2.66 | 2.54 | 2.54 |
| Qwen3-8B | DFlash | 5.33 | 4.91 | 4.07 | 4.36 | 4.64 | 4.39 | 3.11 | 2.98 | 2.81 |
| Qwen3-8B | **DSpark** | **6.17** | **5.78** | **5.01** | **5.16** | **5.52** | **5.17** | **3.72** | **3.58** | **3.21** |
| Qwen3-14B | Eagle3 | 5.24 | 4.60 | 3.71 | 3.81 | 4.14 | 4.01 | 2.62 | 2.47 | 2.48 |
| Qwen3-14B | DFlash | 5.41 | 4.84 | 3.98 | 4.44 | 4.59 | 4.33 | 3.10 | 2.94 | 2.72 |
| Qwen3-14B | **DSpark** | **6.21** | **5.74** | **4.94** | **5.26** | **5.43** | **5.02** | **3.70** | **3.58** | **3.13** |
| Gemma4-12B | Eagle3 | 5.87 | 5.46 | 4.83 | 4.72 | 5.37 | 4.16 | 3.19 | 3.06 | 2.72 |
| Gemma4-12B | DFlash | 5.45 | 5.04 | 4.22 | 4.39 | 4.95 | 3.70 | 2.98 | 2.84 | 2.59 |
| Gemma4-12B | **DSpark** | **6.05** | **5.78** | **5.12** | **5.11** | **5.64** | **4.51** | **3.49** | **3.35** | **2.92** |

域效应（§4.2）：Qwen3-4B 上 math 平均 5.57、code 5.12，远高于 chat 3.49——结构化任务天然高接受率，正是 confidence scheduler 动态剪枝的动机。

### DSpark 关键配置（§4.1, §5.1）

| 项 | 值 |
|---|---|
| 默认 sequential head | Markov head（RNN head 仅 §4.3.2 分析） |
| Markov 低秩 r | 256 |
| Block size γ | 7（offline eval）；5（DeepSeek-V4 生产部署，DSpark-5） |
| Drafter layers | 5（DSpark/DFlash）；1（Eagle3） |
| Eagle3 TTT horizon | 7（与 block size 对齐） |
| Loss 权重 | α_ce=0.1, α_tv=0.9, α_conf=1.0 |
| 位置权重 | w_k = exp(−(k−1)/γ) |
| 训练数据 | Open-PerfectBlend 1.3M 样本（chat 17.6%, math 39.4%, code 38.9%, instruction 4.1%） |
| Epoch | 10 |
| Eval 采样温度 | 1.0（chain-based drafting） |
| DSpark-V4 backbone | 3 层 MoE + mHC + sliding window attn=128 |
| 数据/评估模式 | non-thinking mode |

### Position-wise conditional acceptance（Qwen3-4B，§4.3.1，Figure 2 关键点）

| 域 | Position 1 DFlash vs Eagle3 | 尾部趋势 |
|---|---|---|
| Math | 0.88 vs 0.81 | DFlash 衰减；Eagle3 稳定/上升 |
| Code | 0.72（DFlash） | DFlash 0.87→0.78 |
| Chat | 0.72 vs 0.53 | DFlash 0.72→0.63；Eagle3 0.53→0.74 |
| DSpark（Math 起始） | 0.93 | 全 block 高且稳定 |

### Confidence head 可靠性（§4.3.3，Figure 6，Alpaca 数据集）

| Position | ROC-AUC | ECE 前 → STS 后 |
|---|---|---|
| 1 | 0.818 | 5.7% → 2.0% |
| 3 | 0.812 | 8.2% → 1.7% |
| 5 | 0.864 | 5.8% → 0.8% |
| 7 | 0.907 | 3.3% → 0.4% |

### Confidence threshold sweep（§4.3.3，Figure 5，Qwen3-4B）

| 域 | 阈值=0 acceptance rate | 高阈值 acceptance rate |
|---|---|---|
| Math | 76.9% | 92.5% |
| Code | 67.6% | 92.0% |
| Chat | 45.7% | 95.7%（剪枝最显著） |

### 提案长度 γ 扩展（§4.3.2，Figure 4 左三图，Qwen3-4B，5 层）

| γ | Math 增益（vs DFlash） | Code 增益 | Chat 增益 |
|---|---|---|---|
| 7 | +16% | +15% | +18% |
| 15 | +30% | +26% | +22% |

### 生产 Pareto frontier（§5.4，Figure 7）

| 引擎 | SLA（tok/s/user） | 吞吐增益 | matched-throughput 下 per-user 加速 |
|---|---|---|---|
| V4-Flash | 80 | +51% | +60%–85% |
| V4-Flash | 120（baseline 接近边界） | 名义 +661%（基准低并发） | — |
| V4-Pro | 35 | +52% | +57%–78% |
| V4-Pro | 50（baseline 接近边界） | 名义 +406% | — |

### 验证预算随负载变化（§5.4，Figure 8 底排）

| 引擎 | 低并发阈值 | 分配验证预算 | 高并发行为 |
|---|---|---|---|
| V4-Flash | <200 并发 | 4–6 token（vs MTP-1 静态 2） | 平滑缩减 |
| V4-Pro | <150 并发 | 4–6 token | 平滑缩减 |

## 与同类对比

- **vs Eagle3（autoregressive drafter，TTT-based，§2.2, §4.3.1）**：Eagle3 每位置 condition 于已采样前驱，suffix coherence 强（Chat 上 conditional acceptance 从 0.53→0.74），但 `T_draft ∝ γ` 强迫浅网络（1 层），position-1 capacity 不足（Chat 0.53）。DSpark 用 5 层并行 backbone 在 position-1 占据容量优势（Math 0.93 vs Eagle3 0.81），并用 sequential head 补回 suffix coherence。机制级胜负点：speculative decoding 是 prefix-survival 过程，position-1 拒绝即全 block 作废（§4.3.1 明确"the first token carries the highest leverage—a rejection here immediately invalidates the entire block"），第一 token 杠杆最高——并行 drafter 的深网络优势在此被放大。最终 τ 在 Qwen3-{4B,8B,14B} 上高出 30.9%/26.7%/30.0%。

- **vs DFlash（parallel drafter，KV injection，§2.2, §4.3.1）**：DFlash 是 DSpark 的并行 backbone 基础（§3.1 明确"in our instantiation, DFlash"）。其 prefill 阶段把 target 多层 hidden states 拼接投影进 draft 空间并注入每层 KV（§2.2，式 2-3，权威 LaTeX）：

  $$H_{\text{ctx}} = \mathrm{RMSNorm}\bigl(W_c\,[H^{(l_1)};\, \ldots;\, H^{(l_m)}]\bigr),$$

  $$K_i = [W_i^K H_{\text{ctx}};\; W_i^K H_d], \quad V_i = [W_i^V H_{\text{ctx}};\; W_i^V H_d].$$

  DFlash position-1 强（深网络 + bidirectional attention + 注入 target context hidden states），但 suffix 衰减快（Code 0.87→0.78，Chat 0.72→0.63）。DSpark 的 sequential head 直接针对此衰减，γ 越长优势越显著（γ=7 时 +16%/15%/18%，γ=15 时 +30%/26%/22%）。**2 层 DSpark > 5 层 DFlash**（Figure 3）说明 stack deeper parallel layers 不如注入少量 autoregression。

- **vs CRF-NAT / CTC-drafter（§6）**：CRF-NAT 也在并行 hidden states 上放 sequential 模块，但全局归一化 partition function 使其无法计算精确 per-token 概率，无法用于 rejection sampling；CTC-drafter 因 alignment path 的 latent marginalization 只能 greedy verification。DSpark 保持 sequential correction 局部化（式 4 的逐位置 softmax），per-token 概率仍是精确 softmax 评估，满足 lossless speculative decoding 要求。

- **vs 静态阈值方法（Huang et al. 2024; Li et al. 2024b；§3.2.1, §4.3.3）**：静态阈值只需 confidence 能正确排序 token 质量；DSpark 的 hardware-aware scheduler 需要置信度的**绝对量级**来算期望 τ，因此引入 STS 校准。静态阈值在孤立单请求下有效，但忽略系统负载，高并发下次优——Figure 5 的 threshold sweep 是诊断工具，论文明确指出 static threshold "sub-optimal in dynamic serving environments because it ignores system load"。

- **vs Domino / DFlare（concurrent work，§6）**：Domino 的 CausalEncoder 概念上接近 DSpark 的 RNN head；DFlare 通过 layer-wise fusion 解决 conditioning 瓶颈。

- **vs MTP-1（生产 baseline，§5.4）**：MTP-1 是 DeepSeek-V3/V4 此前的单 token 生产设置，DSpark 发布后两周即取代之。历史上不部署静态多 token drafter（MTP-3/5）是因为高并发下过量验证开销严格降低聚合吞吐。DSpark 是首个能安全解锁更大 draft block 的方案——通过 confidence scheduler 在并发升高时自动收缩验证预算（Figure 8）。

## 跨论文关系（→ MOC 谱系）

DSpark 属于**推测解码 → 并行/半并行 drafter** 谱系，并引入**load-aware verification scheduling** 这一系统侧分支。

- **[[dflash-block-diffusion-for-flash-speculative-decoding]]** — 姊妹方法。DFlash 是 DSpark 的并行 backbone 直接基底（§3.1 明确"in our instantiation, DFlash"，式 2-3 的 KV injection 来自 DFlash）。DSpark 的关键改动：(1) 把 anchor 也当首个预测位置；(2) 追加 sequential head + confidence head。理解 DSpark 必须先读 DFlash。两者同源 DeepSpec 训练仓库。
- **[[block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models]]** — DFlash 的命名来源与思想前身，block-level 自回归与扩散的插值；DSpark 继承"block + 半自回归"理念但改为并行+sequential head 的工程化形态。
- **[[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]]** — 主要 autoregressive 对比 baseline（TTT-based）。DSpark 在所有 Qwen3 规模上以 ~30% 优势胜出，关键机制差异见"与同类对比"。
- **[[eagle-speculative-sampling-requires-rethinking-feature-uncertainty]]** 与 **[[eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees]]** — Eagle 谱系前身，确立了 feature-based drafter + tree verification 范式；DSpark 的 confidence scheduler 与 Eagle 系的 dynamic draft tree 都在做"按置信度分配验证预算"，但 DSpark 是系统级全局吞吐优化而非单请求树扩展。
- **[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]** — 并行 drafter 谱系的开创者（multiple heads 单 forward 产出多 token）。DSpark 解决了 Medusa 类方法固有的 independence → suffix decay 问题。

谱系定位：Medusa（并行开端）→ DFlash（KV-injected 并行，强 position-1）→ **DSpark（半自回归 + load-aware scheduling）**；与 Eagle/Eagle2/Eagle3（autoregressive 谱系）形成对照。

## 局限与边界

1. **固定 draft-side 成本不可回收（§5.4 Limitations）**：scheduler 只能剪枝验证侧浪费，无法剪枝 draft 侧。对 inherently 低接受率的复杂 query，并行 backbone 生成完整 γ-block 的 upfront compute 仍被消耗。作者明确建议未来做 difficulty-aware early exiting 让此类请求跳过 full-block drafting——但 DSpark 未实现。

2. **lossless 保证依赖强工程假设**：Algorithm 1 的 early-stop 给出全局最优当且仅当 `Θ(B)` unimodal，**隐式假设平滑衰减的硬件容量曲线**（§3.2.2）。真实 SPS(B) 是 jagged step-wise（§5.2），需异步 ZOS 改造绕过。改造后用"两步前"历史预测近似 capacity K——作者承认引入"slight temporal offset"，依赖 rank-preserving 性质维持正确性，但 offset 在负载剧烈波动时的鲁棒性未量化。Append A 的反例（Pr(Y=A)=0.85 vs target 0.7）则严格证明了**移除 early-stopping 且无 ZOS causal barrier 时**确实破坏 target 分布——两道防线缺一不可。

3. **Markov head 的记忆边界**：默认 Markov head 只看上一 token，position k 无法访问 k-2 及更早 token（§3.1）。RNN head 能缓解但仅 marginal 额外增益且部署属性更差（§4.3.2），故未默认采用。对需要长程 block 内依赖的场景，DSpark 的 sequential head 可能仍不足。

4. **STS 校准依赖 held-out set + 域分布**：STS 在 held-out validation set 上逐位置 grid search（§3.2.1）。若线上分布与校准集漂移（如新域、新 prompt 风格），累积积的绝对量级可能再次失准，直接扭曲 `Θ = τ·SPS(B)` 的吞吐估计，导致次优调度。论文未给线上漂移的再校准机制。

5. **生产部署依赖特定系统栈**：变长执行需修改 DeepSeek-V4 的 index-attention 与 compress kernel（§5.3）；ZOS 集成是前提（§5.2）。在无 ZOS / 无 sparse attention marker tensor 支持的引擎上，性能数字不可直接复现。V4-Flash/Pro 的 +60%–85% / +57%–78% 是 DeepSeek-V4 内部引擎特定结果。

6. **高 SLA 点的"+661%/+406%"不可作代表性倍率解读**（§5.4）：在 120/50 tok/s/user SLA 下 MTP-1 baseline 进入低并发 regime，基准本身接近退化为小 batch，DSpark 的名义倍率被基准的分母缩小放大。作者明确将该点解读为"扩展可行交互性前沿"而非"对良利用基准的乘性加速"。

7. **block size 在生产被限制为 γ=5**（§5.1），小于 offline eval 的 γ=7。生产配置更保守，长 block 的 τ 增益（γ=15 时 +30%）未在生产部署中兑现——生产侧受限于 serving 系统对变长验证的实际承受度。

8. **未涉及 thinking mode**（§4.1）：数据生成与评估均用 non-thinking mode。对 reasoning-heavy 的 thinking/CoT 长输出场景的收益未验证。
