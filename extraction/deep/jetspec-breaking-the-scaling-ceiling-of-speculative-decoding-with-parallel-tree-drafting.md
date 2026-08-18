# JETSPEC: Breaking the Scaling Ceiling of Speculative Decoding with Parallel Tree Drafting — 技术点深读（DEEP 2026-08-18）
> 独立深读文件，extract_phase1 重跑不丢失。图文交织分析，M3 figure caption 已织入各节。
> 论文：arXiv:2606.18394v3 (25 Jun 2026) · UC San Diego / 浙大 / UIUC / 南京大学 / StepFun
> 代码：https://github.com/hao-ai-lab/JetSpec

## 核心问题

Speculative Decoding (SD) 的端到端加速由两个因子联合决定（§2.1, Eq. 2）：

$$\mathrm{Speedup} = \frac{1-\alpha^{N+1}}{(1-\alpha)(Nc+1)}$$

其中 α=平均接受率，N=draft token 数，c=单步 draft head 与 target model 单步耗时之比。该公式暴露一个 **scaling ceiling**：增大 draft budget N 只有在「α 保持高」且「累积 drafting overhead Nc 保持小」时才能换得更高吞吐；任一条件崩塌，收益即被抵消。**Figure 2（p.3, M3 要点）** 用两面板直观印证：左面板 c=0.05（typical SD）随 draft length γ 增长很快饱和，α 从 0.70→0.95 也只能把 256-budget 的 speedup 推到 ~6×；右面板 c=0.0005（ultra low-cost）下同 α 序列单调放大到 ~20×。M3 解读点出"加速随 γ 单调增长、破解 c/α 鱼与熊掌"——即把 c 压低 + 把 α 抬高是 unlock 长 draft scaling 的两个独立必要条件。

既有 head-based SD 陷入 **causality–efficiency dilemma**（§1, §2.2）：
- **Autoregressive drafters（EAGLE 系列）**：生成 path-conditioned 候选，tree-SD 接受率 α 高；但 draft cost 随 tree depth 增长（每深一层多一次 draft 前向），c 项膨胀 → 难以扩 N。
- **Bidirectional block-diffusion drafters（DFlash）**：一次前向并行出 N 个 token，c 极低（§Appendix G, Table 12: L=1024 时 N=256 c≈0.054%，约 1/N 衰减）；但各位置分布 r_i(·|x) 是 **branch-agnostic marginals**，不以上游 ancestor token 为条件，组合出的树分支"单 token 各自合理、合在一起互相不一致"（§2.2 Eq. 3 的 surrogate q_sur），浪费 budget、压低 α → 难以把低 c 转化为高 speedup。

JetSpec 要回答的核心问题：**能否在一次前向（低 c）并行 drafting 的同时，保持 branch-wise causal conditioning（高 α），从而把更大 draft budget 真正转化为更长 accepted prefix？**（§2.2 "Can We Enable Both?"）Figure 2（p.3）的右面板正是该问题成立的物理依据：在 c≈0.05% 的 ultra-low-cost 区，唯一瓶颈回到 α，而 JetSpec 的目标就是把 α 在大 budget 下稳住。

## 关键创新点

### 1. Causal-Parallel Draft Head：单次前向 + 树因果掩码（§2.2, Figure 3 p.4）
核心架构是 head-based：draft head 复用 frozen target model M_p 的中间层 fused hidden feature h_x^o，在其 KV cache 中注入目标上下文（继承自 DFlash 的 feature fusion 设计），但新增一层 **tree-causal attention mask**。对树节点 u, v（Eq. 5）：

$$M_{v,u} = \begin{cases} 0, & u \in \mathrm{Anc}(v)\cup\{v\} \\ -\infty, & \text{otherwise} \end{cases}$$

prefix tokens 对所有树节点可见。该掩码使所有树节点可在一次前向并行计算 logits，同时每个分支遵循 **branch-wise 因子分解**（Eq. 7）：

$$q(\pi(v)\mid x) = \prod_{u\in\pi(v)} q(y_u \mid x, h_x^o, \pi_{<u})$$

它镜像 target model 的自回归因子分解（Eq. 4），但每个 draft node 以**本路径上具体 ancestor token** 为条件。

**Figure 3（p.4, M3 解读）** 给出三阶段设计：(1) 从 frozen target model Layer M 抽 hidden state，经 Feature Fusion 模块输出统一 fused feature；(2) Causal-parallel draft head M_q（Layers 1…m）以 fused feature + anchor + draft slots 为输入，在 **tree-causal attention mask** 约束下，单次前向产出整棵候选树（root → 各分支节点携带 score 如 s=-0.87/-1.39/-2.48/-4.05 等）；(3) frozen target model M_p 用同一 tree mask 验证，产出 step i+1 的 verified tokens。M3 强调该 mask"preserve correct autoregressive conditioning across sibling branches, enabling higher acceptance than branch-agnostic per-position drafting"。效果：既保留并行预测的低 c，又使 draft 分布与 M_p 自回归分布对齐 → tree acceptance 随 budget 扩展而良好 scale。

### 2. 树构造：Parallel Tree Drafting + 累积 log-prob 堆（§2.4, Algorithm 1）
每个 decode step i：draft head 以已验证 token 的 h_x^o 为条件，构造 max depth N、branching width W、total node budget B 的候选树。一次 draft-head forward 拿到所有 depth 的 logits，每层取 top-W；再用分支打分函数 best-first 展开至 budget 满。默认打分（Eq. 10）：累积 draft log-probability

$$s(\pi(v)) = \sum_{u\in\pi(v)} \log q(y_u \mid x, h_x^o, \pi_{<u})$$

Algorithm 1（§Appendix B）：维护按 Score 排序的优先队列，反复弹出最高分节点、加最多 W 子节点、以更新后的路径分回插，直到 |V_T|=B 或队列空。**Table 10（§Appendix C）** ablate 三种打分：accum_logp=8.15×/τ9.81（默认）；entropy-only 崩到 4.76×/τ5.52（−42%）；hybrid (Σlog r + α·H_i) 在 α≤1 收敛到同 plateau（8.15–8.27×），α=8 降到 7.42×。结论：累积 log-prob 是稳态最优，per-depth entropy 单独不足以识别高接受分支。

### 3. 训练：block-causal mask + Forward-KL 蒸馏（§2.3, §Appendix D, Figure 5/6 p.18-19）
- **数据**：target-aligned 序列，可来自训练语料（MTP 风格）或 target model 重新生成（on-policy）。每序列采多个 anchor，每个 anchor 构造长度 N 的训练 block，block 内首 token 留作 anchor（不参与 loss），其余 N-1 位并行预测。
- **训练 mask（Figure 5, p.18, M3 解读）**：2D attention 矩阵，列区分"verified prefix（x₀–x₃）"与多个"sampled blocks"，每 block 含 anchor aᵢ + 5 个未来位 aᵢ,₁…aᵢ,₅。黄色 ✓ = 允许 attention，dark = 禁止。规则：(a) 所有 query 位全可见 verified prefix；(b) 每 block 内严格下三角——query 只见本 block anchor 及更早位；(c) 无跨 block attention、无未来位 attention。M3 要点：该 mask "enables parallel prediction of all masked tokens across multiple blocks while preserving autoregressive causality within each block"。
- **block 监督（Figure 6, p.19, M3 解读）**：3 行（Block 1/2/3）× 6 位。anchor（白框，"no loss"）+ 5 个 future 位（橙框，"loss"）。M3 要点：anchor 把 context 与训练目标解耦——排除其 loss 后，模型学习"conditioned on preserved anchor, predict future positions"，避免标准 causal masking 的 leakage。
- **损失（Eq. 8, 9）**：温度归一化 forward KL。关键 ablate（§3.4.1 Table 4）：SFT 与 forward-KL 在 4 个 math 基准上差 ~3% 以内；**reverse-KL 相对 forward-KL 掉 36–46%**（GSM8K 6.11→3.29, MATH-500 8.46→5.25）。原因：reverse-KL mode-seeking 把概率过度集中到高置信 mode，而 tree drafting 恰恰需要保留**多支合理 continuation 的软标签**；forward-KL 覆盖 target 概率质量，更适配预算化树展开。
- **Draft head 配置（Qwen3-8B, §Appendix D）**：从 target layers {1,9,17,25,33}（共 36 层）抽 hidden state，沿 channel 拼成 5d 后经 bias-free linear + RMSNorm 投回 d=4096。Draft head 本体：5 层 Qwen3-style decoder，32 attn heads，8 KV heads，head dim 128，MLP 12288。每层把投影后的 target feature 作为 contextual K/V 注入并与 draft-token hidden state 拼接。Target model 全程冻结。
- **数据量**：780K examples from Nemotron Post-Training Dataset V2（coding+math 全量 + STEM/chat 随机）+ 20K CodeAlpaca，8×H100 训练，LR=3×10^-4（Table 3 grid：5e-5→1e-3，3e-4 峰值 8.30×，6e-4/1e-3 在峰值 2% 内）。

### 4. 验证：tree attention + 标准 SD 接受规则（§2.4, Eq. 11-12）
Target model M_p 用 tree attention 并行验证所有节点。对候选分支 π(v)=y_{1:k}，按自回归 Eq. 4 分解。每 draft token y_t 接受决策 A_t~Bernoulli(α_t)（Eq. 11），非贪心下用拒绝采样 α_t=min(1, p/q)（Eq. 12），拒绝时采样 correction token（**lossless**）。贪心下：draft token 匹配 target 同上下文 next-token 预测即接受。接受前缀长 a=max{r≤k : A_t=1 ∀t≤r}。

### 5. 系统集成：vLLM + 自研 SM90 paged tree-attention kernel（§3.3, §Appendix E）
- 集成进 vLLM：proposer 产 top-k token + log-prob，按累积 log-prob 构造 budget 限定的树，树存 token id / parent idx / depth。
- **自研 fused paged tree-attention kernel**：基于 NVIDIA CuTe DSL 的 SM90 paged FlashAttention 扩展，在 attention 内部应用 tree mask、构建 ancestor 关系，**不物化 dense per-request mask**。接受：比对每节点 token 与 target 在其 parent 处的 greedy 预测，选最深全接受 root-to-node 路径，commit 并以最终接受节点的 target 预测作 correction。
- **Budget 分配洞察（Table 11, §3.3）**：大 budget 在小 batch 最有用——batch 1 时 budget 16→128 把 224.0→553.3 TPS（1.75×→4.33×）；batch 增大收益递减，batch 16 时 budget 256 反降到 2.80×（vs budget 128 的 3.10×）。结论：**budget 应随 serving load 动态调度**（论文留作 future work，仅评 static policy）。

### 6. 结构性鲁棒性：因果掩码消除了 γ 调参需求（§3.4.2, §Appendix A）
γ 控制 DFlash 训练 loss 对远离 anchor 位的指数衰减权重 w_i=exp(−max(i−i_anchor,0)/γ)，γ=0 即无衰减均匀。**Table 7**：causal head 在 γ∈{0,3,7,15} 间 speedup 8.29–8.50×、τ 9.81–10.00× 极稳；diffusion head 对 γ 敏感，端点崩塌（γ=0: 5.46×；γ=15: 6.17×；γ=7 才到 8.36×）。即 causal mask between depths 使 rank-1 alignment 不依赖 loss-weighting 先验，**免去 γ 调参**。

### 7. 失败模式定量与可视化：rank-1 gap（§3.4.2, Table 8/9, Figure 4 p.15, §Appendix A）
**Figure 4（p.15, M3 解读）** 用 MATH-500 prompt #0 step 0（root token "We"）的 rank-1 vs rank-3 对比直观展示失败模式。两面板各画 rank-1 与 rank-3 分支为彩色 token chips（绿=faithful，红=incoherent），标注 gap（Σlog p − Σlog r）与 verifier 接受 token 数：
- **(a) Causal head, γ=0**：rank-1 "are told that" faithful（gap=−0.34），verifier 接受 6 token；其 rank-3 "are given that the2product" gap=+42.50 退化。
- **(b) Diffusion head, γ=0**：rank-1 "given told that" incoherent（gap=+59.56，target joint=−63.32 nats，概率≈e^−63），verifier 仅接受 4 token；真正连贯的 "are given that the"（gap=−3.69）被压到 rank-3。M3 要点点出核心：diffusion head 的 branch-agnostic per-position predictor 把"given"(depth1)+"told"(depth2) 独立组合进 surrogate，而真实 continuation 从不把它们连续摆放——"surrogate scoring can rank incoherent concatenations above coherent continuations, truncating accepted drafts"。

**Table 8** 给出全 top-5：causal rank-1 gap=−0.34（faithful）；diffusion rank-1 gap=+59.56、rank-2 gap=+87.02、rank-5 gap=+92.57 全是"given told"变体，仅 rank-3（gap=−3.69）连贯。**Table 9** 跨 50 prompt 分布：γ=0 时 diffusion 26% prompt 的 rank-1 gap ≥+80 nats（target 联合概率 <10^-35），causal 0%；faithful（gap<+5）diffusion 仅 6% vs causal 42%；中位 gap diffusion +62.81 vs causal +12.36 nats；mean accepted length diffusion 4.84 vs causal 9.46。即使 γ=7 让 diffusion 复苏到 9.42，causal 仍以 9.64 领先。

## 表格（原文结构化）

### Figure 1（p.2, M3 解读）— 全基准 speedup 柱状图（Qwen3-8B, H100, budget 256）
M3：7 benchmark（GSM8K/MATH-500/AIME25/HumanEval/MBPP/LCB/MT-Bench），每基准三柱 DFlash(蓝)/DDTree(橙)/JetSpec(绿)，y 轴 0–11×。代表值：MATH-500 三柱 6.12/8.78/**9.64**；MT-Bench 2.72/4.26/**4.58**；GSM8K 4.80/7.04/**7.82**；AIME25 5.85/8.33/**8.78**。JetSpec 全基准领先，M3 总结"causal parallel draft head + branch-wise causal attention 解决 causality–efficiency dilemma"。

### Table 1 — Low-budget regime（Qwen3-8B, H100, 3072 max tokens, non-thinking）
Speedup / τ，Temp=0 与 Temp=1 各 budget 16/32，跨 7 benchmark。EAGLE-3 在 16/32 远低于 DFlash/JetSpec（EAGLE-3 顺序 draft 开销大）。budget 16 时 DFlash≈JetSpec；budget 32 时 JetSpec 略升而 DFlash 饱和/退化。代表值（Temp=0, budget 16）：JetSpec MATH-500 6.06×/τ7.75、MT-Bench 2.68×/τ3.98；EAGLE-3 MATH-500 2.10×/τ3.61。

### Table 2 — High-budget regime（Qwen3-8B, budget ≥64, Temp=0/1）
JetSpec 随 budget 64→128→256 持续上升。Temp=0, budget 256：MATH-500 **9.64×/τ10.76**（摘要的 9.64× 即此，与 Figure 1 柱状图一致），GSM8K 7.82×/τ8.62，HumanEval 7.12×/τ7.78，MT-Bench 4.58×/τ5.94。DDTree 256 在 MATH-500 为 8.78×/τ9.81（更温和 9× scaling）。EAGLE-3 tree mode max depth 8，大 budget 增益极小甚至变差（training mismatch）。Figure 1（p.2）即 budget 256 下三方法的柱状总览。

### Table 3 — 学习率 ablation（JetSpec, γ=0, GSM8K/MATH-500）
LR 5e-5→1e-3；3e-4 峰值 8.30×（MATH-500 forward-KL）；6e-4/1e-3 在 2% 内。

### Table 4 — 损失目标 ablation（LR 6e-4, γ=0, math-only）
SFT≈forward-KL（差 ≤3%）；**reverse-KL 掉 36–46%**（GSM8K 5.96→3.29, MATH-500 8.42→5.25）。

### Table 5 — 模型泛化（Qwen3-30B-A3B MoE, SFT, 800K 同配方, budget 256, Temp=0）
JetSpec 全基准领先 DDTree：MATH-500 9.45×/τ10.65 vs 8.61×/τ9.49；MT-Bench 4.33×/τ5.59 vs 4.26×/τ5.35。证明 causal tree drafting 不限于 dense 模型。

### Table 6 — 训练数据 ablation（Qwen3-8B, SFT, 800K）
JetSpec（regenerated）远强于 JetSpec-Corpus（直接语料）。budget 256 MATH-500：8.78× vs 3.66×。但 Corpus 版仍有一致加速，暗示 causal parallel drafting 可嵌入 mid/pre-training（regeneration 那时不可承受）。

### Table 7 — 架构 × γ ablation（MATH-500, LR 3e-4, forward-KL）
Causal head 跨 γ 全稳（8.29–8.50×）；Diffusion head 对 γ 敏感（γ=0: 5.46×；γ=7: 8.36× peak；γ=15: 6.17×）。

### Table 8 — MATH-500 prompt #0 step 0 top-5 分支（rank-1 gap 个案，配合 Figure 4 p.15）
Causal γ=0 rank1=" are told that"：Σlog r=−3.88, Σlog p=−3.54, Δ=−0.34（faithful，verifier 接受 6 token）。Diffusion γ=0 rank1=" given told that"：Σlog r=−3.76, Σlog p=−63.32, Δ=+59.56（incoherent，接受 4 token）；其 rank3 才是真正的" are given that the"（Σlog p=−0.08, Δ=−3.69）。Diffusion rank-2/5 gap 高达 +87.02/+92.57，全是"given told"变体。

### Table 9 — 50 prompt rank-1 gap 分布
γ=0：causal faithful 42% / extreme(≥+80) 0%；diffusion faithful 6% / extreme 26%。median gap 12.36 vs 62.81；mean accepted 9.46 vs 4.84。γ=7：diffusion 复苏（extreme 4%, faithful 26%, mean accepted 9.42）但终不及 causal（extreme 2%, mean accepted 9.64）。

### Table 10 — 树构造算法 ablation（MATH-500, n=500, production setting）
accum_logp 8.15×/τ9.81（默认）；entropy-only 4.76×/τ5.52（−42%）；hybrid α≤1 plateau（8.15–8.27×），α=8 降到 7.42×。

### Table 11 — vLLM serving（MATH-500, Qwen3-8B, 单 H100）
batch 1：budget 16→128 给 224.0→553.3 TPS（1.75×→4.33×）。batch 16：budget 256 反降 2.80×（vs 128 的 3.10×）。**budget 需随 load 动调**。

### Table 12 — 经验 per-token drafting cost c=T_draft/(N·T_verify)（%, H200 NVL, DFlash-style head, Qwen3-8B target）
L=1024: N=2 c=6.72%，N=16 c=0.845%，N=256 c=0.054%（≈1/N 衰减，对应 Figure 2 p.3 ultra-low-cost 区）。L≤2048、N≥16 时 c<1%。支撑主 scaling 论证：大 N 把 c 压到 0.05% 量级，此时只有 α 是瓶颈 → 正是 causal tree drafting 要解决的。

## 与同类对比

| 维度 | EAGLE-2/3 (autoregressive) | DFlash (block-diffusion) | DDTree (DFlash+tree) | **JetSpec (causal-parallel)** |
|---|---|---|---|---|
| Draft 方式 | 顺序、path-conditioned | 单次前向、branch-agnostic marginal | 单次前向 + best-first 树 | **单次前向 + tree-causal mask（Figure 3 p.4）** |
| c（per-token cost） | 随 tree depth 增长 | 极低（~0.05%@N=256, Table 12） | 极低 | 极低（同 DFlash 量级） |
| α（接受率） | 高（因果对齐） | 低（marginal 组合不一致, Figure 4 p.15） | 中（树缓解但不根治） | **高（branch-wise 因果对齐 Eq.7）** |
| 大 budget scaling | 受限（c 膨胀 + training mismatch） | 饱和/退化 | 温和到 9× | **持续到 9.64×/τ10.76（Figure 1 p.2, Table 2）** |
| 训练目标敏感性 | — | 依赖 γ 调参 | 同 DFlash | **γ-robust（Table 7）** |
| 蒸馏损失 | — | — | — | forward-KL > SFT >> reverse-KL（Table 4） |
| Tree 构造打分 | dynamic draft tree | — | best-first | accum_logp 默认（Table 10） |
| 训练 mask | 标准 causal | block-causal | 同 DFlash | **多 block + 跨 block 隔离（Figure 5 p.18, Figure 6 p.19）** |

定位：JetSpec 不是取代 EAGLE-2/3 的 path-conditioning 思想，而是**把 path-conditioning 从「顺序实现」重写为「tree-causal mask 下的单次前向并行实现」**，从而把 EAGLE 的高 α 与 DFlash 的低 c 在同一 head 内统一。对 DDTree 的优势是结构性而非调参性：DDTree 仍用 branch-agnostic head，靠 loss-weighting γ 缓解不一致；JetSpec 用因果掩码从架构上消除该不一致（Figure 4 p.15 可视化），故 γ-robust。

## 跨论文关系（→ MOC 谱系）

JetSpec 位于 **speculative-decoding 谱系中的「parallel-tree drafting」分支**——同时占有「单次前向并行（低 c）」与「branch-wise causal conditioning（高 α）」两个此前分立的子分支。

- → [[eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees]]：EAGLE-2 是「single-tree dynamic」分支代表——动态构造 draft tree、path-conditioned，但 draft head 顺序推进、c 随 depth 增长。JetSpec 的 tree-causal mask 可视为「把 EAGLE-2 的 path-conditioning 压进单次前向」的正交重写；两者思想可潜在复合（dynamic tree shape × causal-parallel head）。
- → [[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]]：EAGLE-3 是 JetSpec 的直接 baseline（Table 1/2）。EAGLE-3 multi-layer feature fusion + training-time test，但大 budget 下因 training mismatch 增益停滞；JetSpec 在 budget≥64 全面超越之，证明并行 + 因果对齐比单纯堆树深更有效。
- → [[eagle-speculative-sampling-requires-rethinking-feature-uncertainty]]：原始 EAGLE 引入 feature uncertainty 处理 draft-target 分布错配。JetSpec 继承 feature-fusion head 思路但用 forward-KL 蒸馏 + tree-causal mask 解决对齐，是同一对齐目标的不同路径。
- → [[dflash-block-diffusion-for-flash-speculative-decoding]]：DFlash 是 JetSpec 最直接的前身与 baseline——block-parallel draft head + fused target feature 注入的设计被 JetSpec 直接继承（§2.2 Architecture 明确"Building on this design"）。JetSpec 的增量是「把 block 内的双向 attention 换成 tree-causal mask」（Figure 3 p.4），使 branch-agnostic marginal 变为 branch-wise conditional（Figure 4 p.15 失败模式对照）。两者在 §Appendix G 共享 per-token cost 量级论证（Table 12）。
- → [[deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference]]：DeFT 提供 tree-attention 的高效 kernel。JetSpec 的大候选树（budget 256）使 tree verification 开销显著——JetSpec 在 vLLM 中自研 SM90 paged tree-attention kernel（CuTe DSL）正是该需求的实例；DeFT 类方法是其天然的 kernel 层搭档/可替换实现。
- → [[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]：Medusa 是 multi-head parallel drafting 先驱，多头各自预测未来位（branch-agnostic marginal 的早期形态）。JetSpec 的 tree-causal mask 可看作「Medusa 多头 + 因果条件」的演进——保留并行性但补上因果依赖。
- → [[longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification]] / [[specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences]] / [[dspark-confidence-scheduled-speculative-decoding-with-semi-autoregressive-generation]]：同属 SD 加速家族，但分别聚焦 long-context、drop-in 增强、confidence-scheduled semi-AR；JetSpec 聚焦 head-based parallel-tree 的因果性，与这些方法在「draft 生成阶段」正交，原则上可叠加（如 LongSpec 的长上下文 draft + JetSpec 的 causal-parallel head）。

谱系一句话：Medusa（并行多头）→ EAGLE-2（dynamic tree, 顺序）→ DFlash（block-并行, branch-agnostic）→ **JetSpec（block-并行 + tree-causal, branch-wise conditional）**，DeFT/[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]-类 serving 栈作为 kernel/系统层底座。

## 局限与边界

1. **因果近似的结构性代价（§Appendix A.4）**：tree-causal mask 让 r_2 锚定到「depth-1 argmax」而非 off-argmax 分支的真实 ancestor。rank-1（argmax-aligned）分支的 surrogate 忠实（Figure 4 p.15 panel (a) gap=−0.34），但 **off-argmax 分支继承的 r_2 conditioning 与其自身 ancestor 不匹配**——Table 8 中 causal head rank 3–5（共享 off-argmax depth-2 token " given"）在 depth 4–5 退化（gap +42.50、+45.75、+36.58）。即因果性在树头部分忠实、尾部仍偏。这是 head-based 并行的固有近似，非完美自回归。
2. **budget 随 load 饱和（§3.3, Table 11）**：大 budget 仅在 low-to-moderate batch 有用；batch≥16 时 budget 256 反而劣于 128。论文**仅评 static policy，dynamic serving-time budget scheduling 明确留作 future work**——真实生产负载下需自适应调度器，当前实现不提供。
3. **仅 static tree shape**：Algorithm 1 用固定 N/W/B；未做如 EAGLE-2 的 dynamic draft tree（按 context 动态调树形）。作者在 future work 暗示可复合，但当前 JetSpec 与 EAGLE-2 的 dynamic tree 思想未结合。
4. **训练数据依赖 target regeneration（Table 6）**：regenerated 序列显著优于直接语料（MATH-500 budget 256: 8.78× vs 3.66×）。虽然 Corpus 版仍可用（暗示 mid/pre-training 可嵌入），但最优效果需要 target model 重新生成数据，对大模型成本不低。
5. **评估范围**：仅 Qwen3-8B（dense）与 Qwen3-30B-A3B（MoE）两类 Qwen3 系；non-thinking mode；3072 max tokens。未覆盖 thinking/reasoning-chain 模式、超长生成、非 Qwen 架构（Llama/Mistral 等）。B200 上的 serving 评估有限（§3.3 提及 B200 高端 GPU 尤佳，但主表以 H100 为准）。
6. **Greedy 为主，non-greedy 收益缩水**：Table 1/2 显示 Temp=1 下 speedup 普遍低于 Temp=0（如 MATH-500 budget 256：9.64×→7.83×）。拒绝采样 correction 在非贪心下引入额外采样开销，因果优势虽 robust 但绝对增益减小。
7. **Tree-attention kernel 自研耦合**：vLLM 集成依赖自研 SM90 paged tree-attention kernel（CuTe DSL），**强绑 Hopper 架构**；非 Hopper/非 vLLM 栈的可移植性未论证，DeFT 类替代 kernel 未实测对比。
8. **未与 draft-free retrieval SD（REST/PLD+/SAM Decoding/SuffixDecoding）对比**：相关工作中列举但未实验对照，这些方法在重复模式/词法重叠场景可能极低 overhead，与 JetSpec 的 learned causal head 在不同 workload 上孰优未明。
