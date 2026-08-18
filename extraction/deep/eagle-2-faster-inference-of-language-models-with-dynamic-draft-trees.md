# EAGLE-2: Faster Inference of Language Models with Dynamic Draft Trees — 技术点深读（DEEP 2026-08-18）
> 独立文件，extract_phase1 重跑不丢。本 note 在原 deep 笔记基础上增强：把 5 张 M3 图表 caption 织进核心问题/创新点/对比/ablation 各节，前后文一致地对照公式与数字。
> 论文：EAGLE-2: Faster Inference of Language Models with Dynamic Draft Trees · arXiv:2406.16858v2 (30 Jun 2024)
> 作者：Yuhui Li (PKU) · Fangyun Wei (MSRA) · Chao Zhang (PKU) · Hongyang Zhang (Waterloo/Vector)

## 核心问题

EAGLE-1（及 Medusa、Sequoia 等 tree-structured speculative sampling 方法）在所有上下文中使用**静态、固定形状的 draft tree**：draft phase 第 i 步总是添加 k 个候选节点，k 是预设常量（§1, §2.2）。这一设计隐含一个假设——draft token 的接受率仅取决于其在树中的**位置**（position-dependent）。

EAGLE-2 指出该假设与 speculative sampling 的核心洞察（"某些 token 更简单、可被小模型正确预测"）相矛盾，并通过实验（§3.1）证明：**同一位置不同 query 间接受率方差显著**，即接受率高度**上下文相关**（context-dependent）。这一结论的实证依据是 Figure 5（p.3，M3 解读）：左图给出 6 节点二叉 draft tree 结构（root=Query → P1/P2 → P3/P4/P5/P6），右图将每个 query 在 P1-P6 各位置上的 acceptance rate 散点绘制——位置上 P1-P6 的均值整体递减（P1 最高、P6 最低），这支持静态树"上左多、下右少"的经验设计；但**同一位置散点跨度极大**（如 P6 的接受率在某些 query 上接近 0、另一些接近 1），证明接受率不只是 position-dependent。静态树因此存在结构性浪费：高置信分支仍被分配固定预算，低置信分支仍占据验证槽位。

进一步难点：获取真实接受率需要 original LLM 的前向结果，这与 speculative sampling "减少大模型前向次数"的目标相冲突。EAGLE-2 的核心突破口在于发现 EAGLE 的 draft model **well-calibrated**（§3.2）——draft model 的 confidence score 与真实接受率强正相关，从而提供了一条**零额外前向成本**估计接受率的途径。该相关性在论文中由 Figure 6（calibration 散点，原文 §3.2 描述：confidence<0.05 → 接受率≈0.04；confidence>0.95 → 接受率≈0.98，整条曲线贴近 (0,0)-(1,1) 对角线）证实，类似现象在 GLIDE / CAPE 等 draft model 上亦被观察到。

## 关键创新点

1. **Context-aware dynamic draft tree（核心创新，§4）**。
   EAGLE-2 不改变 draft model 的训练与推理，也不改变 verification stage，仅改进两点：(a) 如何**扩展** draft tree（§4.1 Expansion Phase），(b) 如何**重排** draft tokens（§4.2 Reranking Phase）。Tree shape 由 confidence 实时决定，而非预设。其与 EAGLE 的对比在 Figure 4（p.3，原文描述）中以算术例子 "10+2=" 直观呈现：当下一 token 极可能是 "1" 时，EAGLE 仍按固定形状补两个候选（"1" 和 "3"），而 EAGLE-2 在该高置信上下文只补一个候选 "1"；反之对 "10+2" 这种未给出等号的上下文（下一 token 难预测），EAGLE-2 才补两个候选。

2. **节点 value 定义——路径置信度乘积作为全局接受率近似（§4.1）**。
   对 draft tree 中节点 t_i，定义其 value：
   $$V_i = \prod_{t_j \in \text{Path(root, t_i)}} p_j \approx \prod_{t_j \in \text{Path(root, t_i)}} c_j$$
   其中 p_j 为真实接受率，c_j 为 draft model confidence。理论基础是 §3.2 的 calibration 观察：confidence 强正相关于 acceptance rate（confidence<0.05 → 接受率≈0.04；confidence>0.95 → 接受率≈0.98）。乘积形式源于 speculative sampling 的级联拒绝语义——一个 token 最终被接受当且仅当路径上所有前缀都被接受。这一"局部 confidence → 全局 value"的转换，是把 EAGLE 的局部校准性升级为全局接受率近似的关键算子。

3. **Expansion Phase：top-k 全局 value 节点扩展（§4.1）**。
   借助 tree attention，draft model 单次前向即可同时处理当前层所有 token 并生成下一层。但每层节点指数增长，需选择性扩展。EAGLE-2 选择**当前层中 value 最高的 top-k 节点**输入 draft model 形成下一层（而非无差别扩展所有节点）。这使预算集中到"最可能被整路径接受"的分支。Figure 7（p.5，M3 解读）的上半段给出标准示例：root "It" (value=1.0) → "is" (0.6) 与 "a" (0.48) 被选为 top-2 扩展节点（橙色块），低 value 节点如 "the" (0.06) 被剪枝；下一层生成的 "good" (0.34) 等绿色块挂接到树上。注意 expansion 只决定"哪些节点继续往下长"，尚未确定最终输入 LLM 的 token 集合。

4. **Reranking Phase：跨层全局重排 + 保证连通树（§4.2）**。
   Expansion 只加深树；但由于 value 是 [0,1] 乘积、随深度递减，某些**未被扩展的浅节点 value 可能高于已扩展的深节点**。因此不能直接用 expansion 选出的节点作为最终 draft。EAGLE-2 对**所有 draft token 全局重排**，选 top-m 最高 value 节点。关键不变量：**子节点 value ≤ 父节点 value**，故对相同 value 优先选浅节点，可保证 top-m 集合仍构成连通树（connected tree），这是 tree attention 验证所必需的。Figure 7 下半段（M3 解读）示出该过程：在扩张后的整树中全局选 top-8（蓝色块），结果为序列 [It, is, has, a, the, to, good, be]——注意 "has" (value 0.2) 这个浅节点被选入，而某些扩张阶段产生但 value 较低的深节点（如 "do" 0.03、"a" 0.02）被剔除，验证了"全局重排纠正 expansion 局部贪心"的设计意图。

5. **Attention mask 按树结构调整（§4.2）**。
   将选中的树状 token 拍平为 1D 序列输入 original LLM 验证。vanilla 自回归的下三角 attention mask 不再适用——不同分支 token 不可互相 attend。EAGLE-2 按树结构构造 mask（Figure 7 最下方矩阵，M3 解读：三角式 tree-structured causal mask，确保每个 token 只能看到其祖先节点 ancestor-only visibility），从而与 vanilla autoregressive decoding 在分布上一致——这是 lossless 保证的工程前提。该 mask 设计与 [[deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference]] 等 tree-attention kernel 的接口对齐，理论上可由专用 kernel 加速。

6. **Out-of-the-box + Lossless 双重保证（§1）**。
   (a) 不训练任何额外模型（无需训练 tree-structure predictor），直接复用 EAGLE 的 draft model confidence——对应 §1 "does not require training any extra models"；(b) 不微调 original LLM、不放松接受条件，provably 保持生成分布不变——对应 §1 "distribution of the generated text remains exactly the same, provably"。对比 Medusa 在 non-greedy 下放松接受条件、不保证无损；BiLD/CLLMs/SPACE 则微调 LLM 或放松条件换取速度。Figure 1（p.1，M3 解读）的柱状对比图刻意只展示 lossless 方法子集（EAGLE-2 / EAGLE / Speculative Sampling），将 Medusa 等不保证无损的方法排除在主图之外，仅因公平性。

7. **超参设置（Appendix A）**。
   7B/8B、13B、70B original LLM 对应 draft token 总数分别 60/50/48，draft tree 深度 6，expansion phase 选 10 节点。注意 Figure 7 中 top-2/top-8 仅为示意图，实际部署用 top-10 expansion 与 m∈{48,50,60} 的总预算。

## 表格（原文结构化）

### Table 1（节选）— Speedup / 平均接受长度 τ，temperature=0 与 temperature=1
（V=Vicuna, L2=LLaMA2-Chat, SpS=标准 speculative sampling 用 Vicuna-68M）

| Model | Method | MT-bench Spd/τ | HumanEval Spd/τ | GSM8K Spd/τ | Alpaca Spd/τ | CNN/DM Spd/τ | NatQ Spd/τ | Mean Spd/τ |
|---|---|---|---|---|---|---|---|---|
| V13B (T=0) | SpS | 1.93x / 2.27 | 2.23x / 2.57 | 1.77x / 2.01 | 1.76x / 2.03 | 1.93x / 2.33 | 1.66x / 1.88 | 1.88x / 2.18 |
| V13B (T=0) | EAGLE | 3.07x / 3.98 | 3.58x / 4.39 | 3.08x / 3.97 | 3.03x / 3.95 | 2.49x / 3.52 | 2.42x / 3.11 | 2.95x / 3.82 |
| V13B (T=0) | **EAGLE-2** | **4.26x / 4.83** | **4.96x / 5.41** | **4.22x / 4.79** | **4.25x / 4.89** | **3.40x / 4.21** | **3.13x / 3.74** | **4.04x / 4.65** |
| L2-13B (T=0) | EAGLE | 3.03x / 3.90 | 3.76x / 4.52 | 3.20x / 4.03 | 3.01x / 3.83 | 2.70x / 3.59 | 2.83x / 3.47 | 3.09x / 3.89 |
| L2-13B (T=0) | **EAGLE-2** | **4.21x / 4.75** | **5.00x / 5.52** | **4.31x / 4.90** | **4.13x / 4.61** | **3.45x / 4.24** | **3.51x / 4.04** | **4.10x / 4.68** |
| V7B (T=0) | EAGLE | 2.90x / 3.94 | 3.33x / 4.29 | 3.01x / 4.00 | 2.79x / 3.89 | 2.33x / 3.42 | 2.31x / 3.21 | 2.78x / 3.79 |
| V7B (T=0) | **EAGLE-2** | **3.62x / 4.98** | **3.95x / 5.33** | **3.63x / 4.97** | **3.46x / 4.86** | **2.94x / 4.12** | **2.76x / 3.82** | **3.39x / 4.68** |
| L2-7B (T=0) | EAGLE | 2.78x / 3.62 | 3.17x / 4.24 | 2.91x / 3.82 | 2.78x / 3.71 | 2.43x / 3.41 | 2.61x / 3.44 | 2.78x / 3.71 |
| L2-7B (T=0) | **EAGLE-2** | **3.43x / 4.70** | **4.03x / 5.39** | **3.52x / 4.77** | **3.45x / 4.66** | **3.01x / 4.12** | **3.15x / 4.19** | **3.43x / 4.64** |
| L2-13B (T=1) | EAGLE | 2.68x / 3.45 | 2.89x / 3.78 | 2.82x / 3.67 | 2.66x / 3.55 | 2.41x / 3.39 | 2.37x / 3.31 | 2.64x / 3.53 |
| L2-13B (T=1) | **EAGLE-2** | **3.92x / 4.51** | **4.58x / 5.29** | **4.21x / 4.80** | **3.85x / 4.48** | **3.31x / 4.08** | **3.43x / 3.89** | **3.88x / 4.51** |
| V13B (T=1) | EAGLE | 2.32x / 3.20 | 2.65x / 3.63 | 2.57x / 3.60 | 2.45x / 3.57 | 2.23x / 3.26 | 2.14x / 3.06 | 2.39x / 3.39 |
| V13B (T=1) | **EAGLE-2** | **3.80x / 4.40** | **4.22x / 4.89** | **3.77x / 4.41** | **3.78x / 4.37** | **3.25x / 3.97** | **3.07x / 3.54** | **3.65x / 4.26** |
| V7B (T=1) | EAGLE | 2.13x / 3.17 | 2.39x / 3.43 | 2.34x / 3.29 | 2.21x / 3.30 | 2.08x / 3.12 | 1.95x / 2.86 | 2.18x / 3.20 |
| V7B (T=1) | **EAGLE-2** | **3.05x / 4.28** | **3.33x / 4.65** | **3.07x / 4.49** | **3.08x / 4.43** | **2.63x / 3.76** | **2.48x / 3.56** | **2.94x / 4.20** |
| L2-7B (T=1) | EAGLE | 2.22x / 3.30 | 2.61x / 3.79 | 2.40x / 3.52 | 2.29x / 3.33 | 2.19x / 3.15 | 2.22x / 3.12 | 2.32x / 3.37 |
| L2-7B (T=1) | **EAGLE-2** | **3.19x / 4.41** | **3.67x / 5.06** | **3.35x / 4.62** | **3.20x / 4.48** | **2.73x / 3.85** | **2.81x / 4.01** | **3.15x / 4.41** |

数字与 Figure 1（p.1，T=1）、Figure 2（p.2，T=0，M3 解读：EAGLE-2 在每个模型组均列最高，3.29x–4.26x）的柱状图一致：Figure 1 中 V7B=3.05x、V13B=3.80x、L2-7B=3.19x、L2-13B=3.92x，与 Table 1 中 T=1 MT-bench 列完全对应；Figure 2 中 V7B=3.62x、V13B=4.26x、L2-70B=3.51x、LLaMA3-70B=3.29x、LLaMA3-8B=3.46x，与 Table 1 T=0 MT-bench 列及 Table 2 完全对应。

### Table 2 — LLaMA2-Chat 70B / LLaMA3-Instruct 70B / 8B, MT-bench, T=0

| Model | Method | Speedup | τ |
|---|---|---|---|
| LLaMA2-Chat 70B | PLD | 1.31x | 1.39 |
| LLaMA2-Chat 70B | Lookahead | 1.52x | 1.64 |
| LLaMA2-Chat 70B | EAGLE | 3.01x | 3.81 |
| LLaMA2-Chat 70B | **EAGLE-2** | **3.51x** | **4.48** |
| LLaMA3-Instruct 70B | EAGLE | 2.83x | 3.62 |
| LLaMA3-Instruct 70B | **EAGLE-2** | **3.29x** | **4.16** |
| LLaMA3-Instruct 8B | EAGLE | 2.72x | 3.65 |
| LLaMA3-Instruct 8B | **EAGLE-2** | **3.46x** | **4.53** |

### Table 3 — Ablation（Vicuna 7B, T=0）
"w/o value"=直接用 confidence 而非 path 乘积；"w/o reranking"=不做重排；"w/o both"=两者皆无

| Method | MT-bench Spd/τ | GSM8K Spd/τ |
|---|---|---|
| w/o both | 2.81x / 3.92 | 2.85x / 3.93 |
| w/o value | 3.21x / 4.39 | 2.93x / 3.96 |
| w/o reranking | 3.48x / 4.86 | 3.50x / 4.85 |
| **EAGLE-2 (full)** | **3.62x / 4.98** | **3.63x / 4.97** |

Ablation 对照 Figure 7 的两阶段设计：value 乘积（创新点 2）对应"w/o value"行的退化，reranking（创新点 4）对应"w/o reranking"行的退化。两行均低于 full，证明二者各自有效；但 w/o both 已达 2.81x/3.92（接近 EAGLE 的 2.78x/3.71），暗示"允许 dynamic"这一开关本身贡献大头，value/reranking 是增量优化。

### Figure 6 — Confidence → Acceptance rate 校准数据点（Vicuna 7B, Alpaca）

| Confidence 区间 | 平均接受率 |
|---|---|
| < 0.05 | ≈ 0.04 |
| > 0.95 | ≈ 0.98 |
| 整体 | 强正相关，接近 (0,0)-(1,1) 对角线 |

## 与同类对比

- **vs EAGLE-1**：EAGLE-2 在所有 model×task×temperature 组合上一致优于 EAGLE，speedup 提升 20%-40%（§1 摘要数字）。具体地 MT-bench Vicuna-7B T=1：3.05x vs 2.13x（Figure 1，M3 解读：EAGLE-2 浅粉柱高出 EAGLE 蓝柱约 43%）；Vicuna-7B T=0：3.62x vs 2.90x（Figure 2）。关键差异：EAGLE 用 fixed shape，EAGLE-2 用 confidence 驱动的 dynamic shape（Figure 4 算术例证）；EAGLE-2 不引入额外训练。Figure 3（p.3，M3 解读）展示的 EAGLE 的 feature-level autoregressive draft model + tree-structured verification pipeline（与标准 SpS 的 token-autoregressive + chain-structured pipeline 对比）是 EAGLE-2 直接复用的基础设施——EAGLE-2 的改进仅发生在 tree shape 的选择层。
- **vs Medusa**：Medusa 用 multiple heads 并行预测多 token，但在 non-greedy 下放松接受条件、**不保证无损**（§1, §5）。Figure 2（M3 解读）将 Medusa 列为绿色柱，在 V13B 上仅 2.07x（T=0），EAGLE-2 4.26x 约为其 2 倍。Medusa 也是 static tree。
- **vs Lookahead**：Jacobi 迭代生成 draft，无神经网络 draft model，draft 阶段开销极低、speedup 接近 τ。Figure 2 中 Lookahead 橙色柱在所有模型上仅 1.4x-1.6x，τ≈1.6 短；EAGLE-2 在 MT-bench 上约比 Lookahead 快 2.3x（§1）。
- **vs Hydra**：Hydra 在 Medusa 基础上加 sequentially-dependent heads，τ 高于 Medusa 但仍为 static tree。Table 1 V13B T=0：EAGLE-2 4.04x (mean) vs Hydra 2.69x (mean)。
- **vs SpS (Vicuna-68M)**：标准 speculative sampling 用 68M 小模型作 draft model，训练开销大（pretrain+SFT）。EAGLE-2 仅用 SFT 训 draft model 即超越之；但在 QA/CNN/DM 上 EAGLE 系列表现下滑（见局限）。
- **vs 部分 dynamic tree 先驱（§6 Related Work）**：BiLD/Kangaroo 用 confidence early-stopping 控制树**深度**；GLIDE/CAPE 在 top-1 confidence 低时**追加候选但不进一步展开**——结构受限。EAGLE-2 明确对比，强调自身"无此限制、可灵活调整树结构"。Sequoia 显式假设接受率仅与位置相关（§1），EAGLE-2 通过 Figure 5 的散点方差直接驳斥此假设。
- **vs 损失速度权衡类**：BiLD 放松接受条件，Medusa-2/CLLMs/SPACE 微调 original LLM。EAGLE-2 走无损路线，不碰 LLM 参数。

## 跨论文关系（→ MOC 谱系）

EAGLE-2 位于 **speculative feature-prediction 分支**的 **dynamic-tree step**：

- **[[eagle-speculative-sampling-requires-rethinking-feature-uncertainty]]**（EAGLE-1，前身）：EAGLE-2 直接 build upon。EAGLE-1 在其 §A.1 self-admits "tree structure not rigorously optimized"——EAGLE-2 正是针对此 admitted limitation 的直接回应，把 tree optimization 从手工固定形状升级为 confidence 驱动的动态优化。EAGLE-2 复用 EAGLE 的 feature-level autoregressive draft model（Figure 3a 所示）与 tree attention 验证（Figure 3b），不改其训练。
- **[[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]]**（EAGLE-3，后继）：进一步通过 training-time test 扩展 EAGLE 系列的规模与速度。EAGLE-2 的 dynamic tree 思路与 EAGLE-3 的训练侧改进互补。
- **[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]**（Medusa，多头前身）：EAGLE-2 把 Medusa 的 multi-head static tree 思想替换为 confidence-aware dynamic tree，并保留 lossless 性质（Medusa 在 non-greedy 不保证 lossless，见 §1）。
- **[[deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference]]**（DeFT，tree-attention kernel）：DeFT 提供 tree-structured attention 的高效 kernel。EAGLE-2 的 reranking phase 需要按树结构构造 attention mask（§4.2，Figure 7 最下方 tree-structured causal mask），DeFT 可作为 EAGLE-2 verification stage 的 drop-in kernel 加速。
- **[[jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting]]**（JetSpec，parallel tree drafting）：JetSpec 走并行多树 drafting 路线突破 scaling 上限，与 EAGLE-2 的单树动态优化是不同维度的扩展方向，二者可潜在组合（并行多棵 dynamic tree）。
- **[[dspark-confidence-scheduled-speculative-decoding-with-semi-autoregressive-generation]]**（DSpark，confidence-scheduled）：同样利用 confidence 调度 draft，与 EAGLE-2 的 confidence→tree-shape 思想形成 confidence-driven spec decoding 谱系内的对照。

谱系定位：speculative decoding → tree-structured draft → feature-level autoregression (EAGLE) → **context-aware dynamic tree (EAGLE-2, 本文)** → training-time scaling (EAGLE-3)。

## 局限与边界

1. **依赖 EAGLE draft model 的 calibration 假设（§3.2）**。整个 dynamic tree 机制依赖"draft model confidence ≈ acceptance rate"这一经验观察，由 Figure 6 在 Vicuna 7B + Alpaca 上验证。若 draft model 校准性差（如训练不充分、分布偏移严重），value 近似失真，dynamic tree 退化为噪声剪枝。论文未给出校准失败时的理论界或鲁棒性分析。Figure 6 本身只展示单一模型 + 单一数据点的校准曲线，跨模型族的泛化性未系统量化。

2. **QA / 摘要任务上 EAGLE 系列表现相对下滑（§5.1）**。Medusa/Hydra/EAGLE/EAGLE-2 在 Natural Questions、CNN/DM 上 τ 与 speedup 均下降，而标准 SpS 不下降。Table 1 中 V7B NatQ EAGLE-2 仅 2.76x/3.82，明显低于其在 HumanEval 的 3.95x/5.33。论文归因于 draft model 仅用 SFT 数据训练，而世界知识/摘要更多依赖 pretraining（如 "Where was the 2015 rugby union world cup held?" 类世界知识问题）。EAGLE-2 虽仍超越 SpS，但该短板源自 draft model 训练数据，**不在 EAGLE-2 的改进范围内**——dynamic tree 无法弥补 draft model 本身的能力缺口。

3. **超参对模型规模敏感（Appendix A）**。draft token 总数 60/50/48、depth 6、expansion top-10 随模型规模手工设定，未给出自动调节机制。迁移到新模型族需重新调参。

4. **Ablation 表明 value 与 reranking 各自贡献有限（Table 3）**。w/o both 已达 2.81x/3.92（接近 EAGLE 的 2.78x/3.71），说明"dynamic tree 框架本身"贡献大头，value 乘积形式与跨层重排是增量优化（full vs w/o both 约 +0.8x speedup、+1.0 τ on MT-bench）。这暗示 EAGLE-2 的边际收益相对 EAGLE 主要来自"允许 dynamic"这一开关，而非 value/reranking 的精巧设计本身——对创新点 2/4 的理论优雅性的实证回报相对有限。

5. **Expansion 仍是贪心 top-k（§4.1）**。基于 value 的 top-k 选择是贪心的、局部最优，未考虑兄弟节点间的相关性或全局树形最优。Figure 7 中 top-2 expansion 仅看当前层最高 value，不计入跨层组合优化。Sequoia 等硬件感知方法可在拓扑优化上互补，EAGLE-2 未结合硬件感知。

6. **无损性依赖严格 tree attention mask 正确性（§4.2）**。lossless 保证建立在"mask 严格按祖先关系构造"之上（Figure 7 最下方矩阵）；实现 bug 会破坏分布等价性，属工程风险而非理论局限，但需 careful 实现。

7. **未评估长上下文/极深 draft tree 场景**。draft depth 固定 6，长序列生成下深层节点的 value 衰减极快（乘积趋 0），dynamic tree 是否仍优于静态树、以及 top-k 选择在 depth 较大时的退化行为，论文未讨论。Figure 7 示例仅到 depth 3 左右，深层行为未可视化。
