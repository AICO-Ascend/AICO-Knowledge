# DeepSeekMath — 技术点深读（DEEP 2026-08-18）

> 论文：DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models
> Shao, Wang, Zhu et al. (DeepSeek-AI / Tsinghua / Peking), arXiv:2402.03300v3, 27 Apr 2024
> 深读锚点：GRPO 算法根（RL 系统谱系的起点）、数学语料 pipeline、code→math 训练顺序、unified RL paradigm

---

## 1. 核心问题

DeepSeekMath 攻击三个机制级瓶颈，而非"再做一次数学 SFT"：

1. **公开 web 数据被低估为数学训练源**（§2.1, §1.1）。在 DeepSeekMath 之前，open-source 数学语料规模停留在 OpenWebMath 13.6B / Proof-Pile-2 51.9B / MathPile 8.9B（§2.2 Table 1），且以 arXiv 与英文为主。Minerva 540B 用的数学 web 规模约 17B tokens（DeepSeekMath Corpus 是其 ~7×）。论文要回答：Common Crawl 中是否还有可大规模回收的高质量数学 token？
2. **PPO 在 LLM-RL 场景的 value-function 失配**（§4.1.1）。PPO 的 advantage A_t 依赖 GAE + 学习的 value function V_ψ（§4.1.1 Eq. 1）。但 LLM RL 中 reward model 通常只对**最后一个 token**给一个标量 reward（§4.1.1），逐 token 训练一个准确的 V_ψ 既困难又要求一个与 policy 同量级的 critic 模型——带来显著的显存与算力负担（§4.1.1）。这是 RL 系统谱系中 [[high-dimensional-continuous-control-using-generalized-advantage-estimation]]（GAE）方法在 LLM 上的直接继承与卡点。
3. **RL 在 SFT 之后是否仍能提升强基线、以及"为什么能"**（§5.2.1, §5.2.2）。DeepSeekMath-Instruct 7B 已在 MATH 达 46.8%、GSM8K 达 82.9%（§3.2 Table 5），此时 RL 还有没有空间？若有效，是因为模型"变强了"还是因为分布"变稳了"？论文用 Pass@K / Maj@K 解耦给出机制回答（§5.2.2, Figure 7）。

---

## 2. 关键创新点

### 创新点 1 — 迭代式 fastText 语料回收 pipeline（DeepSeekMath Corpus, 120B tokens）

**机制**（§2.1, Figure 2）：以 OpenWebMath 为 seed，训练 fastText 分类器（vector dim 256, lr 0.1, n-gram=3, min word count=3, 3 epochs；500K 正例 + 500K CC 负例），对 40B HTML 去重后的 CC 打分召回 → 保留 top-ranking → **domain-based seed 扩容**（base URL 聚合为 domain，召回率 >10% 的 domain 判为 math-related，如 mathoverflow.net，再人工标注 URL path 如 mathoverflow.net/questions）→ 用扩充后的 seed 重训 fastText → 进入下一轮。4 轮迭代后得 35.5M web pages / 120B tokens；第 4 轮新增数据中 98% 已在第 3 轮被收集，遂停止。去污染用 10-gram 精确匹配（<10g 且 ≥3g 也匹配）剔除 GSM8K/MATH/CMATH/AGIEval（§2.1）。

**效果**（§2.2 Table 1, 1.3B 对照实验）：DeepSeekMath Corpus (120.2B) 在 DeepSeek-LLM 1.3B 上训练 150B tokens 后，GSM8K 23.8% / MATH 13.6% / CMATH 41.5%，全面碾压 Proof-Pile-2 (51.9B, 14.3%/11.2%/19.9%) 与 OpenWebMath (13.6B, 11.5%/8.9%/16.8%)。MathPile (8.9B) 甚至比 no-math-training 还差（GSM8K 2.7% vs 2.9%）。Figure 3 表明 DeepSeekMath Corpus 在 50B token 处即已超过 Proof-Pile-2 的 1 epoch 全量，证明**平均质量更高**而非单纯更大。

### 创新点 2 — DeepSeekMath-Base 7B：从 code 模型续训 + 500B tokens 混合配比

**机制**（§2.3）：以 DeepSeek-Coder-Base-v1.5 7B 初始化，训 500B tokens，配比 56% DeepSeekMath Corpus / 20% GitHub / 10% arXiv / 4% AlgebraicStack / 10% CC 英中自然语言。lr 4.2e-4, batch 10M tokens, 4K context（§2.3）。

**效果**（§2.3 Table 2）：GSM8K 64.2% / MATH 36.2% / CMATH 71.7% / SAT 84.4% / MMLU-STEM 56.5%，**MATH 超开源基线 10%+，且超过 77× 大的闭源 Minerva 540B（MATH 33.6%）**。Table 4 显示数学续训反而把 MMLU 从 49.1% 拉到 54.9%、BBH 从 55.2% 拉到 59.5%（相对 DeepSeek-Coder-Base-v1.5），证明数学训练正向迁移到通用推理。

### 创新点 3 — **GRPO（Group Relative Policy Optimization）**：去 value model 的 PPO 变体（本论文最大遗产，RL 系统谱系的算法根）

**机制**（§4.1.1 Eq. 3, Figure 4）：对每个 question q，从 old policy π_θ_old 采样 **G 个 outputs {o_1..o_G}**，用 reward model r_φ 打分得 r={r_1..r_G}。优势不再经 GAE+V_ψ，而是**组内归一化**：

- Outcome supervision（§4.1.2）：Â_{i,t} = r̃_i = (r_i − mean(r)) / std(r)，对该 output 内所有 token 共享同一标量优势。
- Process supervision（§4.1.3）：对第 i 个 output 的第 j 步给 reward r^{index(j)}_i，归一化为 r̃^{index(j)}_i；token t 的 advantage = 该步及之后所有步的归一化 reward 之和，Â_{i,t} = Σ_{index(j)≥t} r̃^{index(j)}_i。

GRPO 还把 KL 正则**从 reward 中移出**，直接加到 loss 上（Eq. 3 末项 −β·D_KL[π_θ||π_ref]），并用 Schulman 2020 的无偏 KL 估计器（Eq. 4: π_ref/π_θ − log(π_ref/π_θ) − 1，保证非负）。这避免了 per-token KL penalty 污染 advantage 估计。

**效果**（§4.2, Table 5）：DeepSeekMath-RL 7B（仅用 144K 条 GSM8K+MATH 的 CoT 数据 RL，§4.2）→ GSM8K 82.9%→88.2%、MATH 46.8%→51.7%、CMATH 84.6%→88.8%、MGSM-zh 73.2%→79.6%。**开源 7B–70B 全域第一**，且 OOD 全面提升。训练配置（§4.2）：policy lr 1e-6, KL coeff β=0.04, 每题采样 64 outputs, max_len 1024, batch 1024, 每次探索后单次更新。

### 创新点 4 — Unified RL Paradigm（SFT/RFT/Online RFT/DPO/PPO/GRPO 的统一梯度框架）

**机制**（§5.2.1 Eq. 5, Table 10）：把所有方法的梯度统一写成 ∇θJ = E[(q,o)∼D] (1/|o|) Σ_t GC(q,o,t,π_rf) · ∇θ log π_θ(o_t|q,o_<t)，三要素 = **Data Source**（offline SFT-sample / online policy-sample）× **Reward Function**（Rule 答案正确性 / Model 学习的 RM）× **Gradient Coefficient**（GC, Appendix A.1 推导）。GRPO 的 GC（Eq. 21）= Â_{i,t} + β(π_ref/π_θ − 1)，是唯一基于 group-relative reward model 且 differential reinforce/penalize 的。

**效果**（§5.2.1 Figure 5）：在 1.3B 上对照——Online RFT > RFT（online sampling 后期优势）；GRPO > Online RFT（**关键：GRPO 对错误响应有负梯度而 Online RFT 仅对正确响应无差别 +1**）；GRPO+PS（process supervision）> GRPO+OS（outcome supervision），证明 step-aware 梯度系数更优。Iterative RL（2 轮，Figure 6）第一轮提升尤其显著。

### 创新点 5 — RL 为何有效：robustify 而非 empower（机制级诊断）

**机制 + 效果**（§5.2.2, Figure 7）：对比 Instruct vs RL 的 Maj@K 和 Pass@K。**RL 提升 Maj@K 但不提升 Pass@K**——这意味着 RL 没有扩展模型的"根本能力上界"（TopK 中至少一个正确的概率不变），而是把概率质量从错误响应挪到正确响应上（让 Top1/多数投票更稳）。作者据此指出 RL 在此更像 preference alignment（呼应 [[rrhf-rank-responses-to-align-language-models-with-human-feedback-without-tears]] 与 Song et al. 2023 PRO），而非能力增长。

### 创新点 6 — 两条预训练经验法则（负结果）

- **Code training → math training 优于 general → math**（§5.1.1, Table 6/7）：DeepSeek-LLM 1.3B 上，Stage1 code(400B) → Stage2 math(150B) 得 GSM8K 21.9% / MATH 15.3% / GSM8K+Python 17.4%，全面优于 general→math 的 19.1%/14.4%/14.3%。但 **one-stage code&math mixed** 反而损害 no-tool 数学（GSM8K 17.6% < 21.9%），推测因 1.3B 容量不足以同时消化 code+math，却缓解 catastrophic forgetting（HumanEval 保持 29.3%）。
- **arXiv 论文对数学推理无增益甚至有害**（§5.1.2, Table 8/9）：MathPile(85% arXiv) 在 1.3B 上 GSM8K 2.7% < no-training 2.9%；ArXiv-RedPajama(28B) 在 DeepSeek-Coder-Base 7B 上 40B tokens 后 MATH 11.1% < no-training 12.5%；miniF2F-test 从 21.7% 降到 11.9%。作者自陈此结论有边界（未测 informalization 任务、未测混合、未测更大模型）。

---

## 3. 表格（原文结构化）

### Table A — 语料对照（§2.2 Table 1, DeepSeek-LLM 1.3B, 150B tokens）

| Corpus | Size | GSM8K | MATH | OCW | SAT | MMLU-STEM | CMATH | Gaokao-MathCloze | Gaokao-MathQA |
|---|---|---|---|---|---|---|---|---|---|
| No Math Training | — | 2.9 | 3.0 | 2.9 | 15.6 | 19.5 | 12.3 | 0.8 | 17.9 |
| MathPile | 8.9B | 2.7 | 3.3 | 2.2 | 12.5 | 15.7 | 1.2 | 0.0 | 2.8 |
| OpenWebMath | 13.6B | 11.5 | 8.9 | 3.7 | 31.3 | 29.6 | 16.8 | 0.0 | 14.2 |
| Proof-Pile-2 | 51.9B | 14.3 | 11.2 | 3.7 | 43.8 | 29.2 | 19.9 | 5.1 | 11.7 |
| **DeepSeekMath Corpus** | **120.2B** | **23.8** | **13.6** | **4.8** | **56.3** | **33.1** | **41.5** | **5.9** | **23.6** |

### Table B — Unified Paradigm（§5.2.1 Table 10 + Appendix A.1）

| Method | Data Source | Reward Function | Gradient Coefficient (Eq.) |
|---|---|---|---|
| SFT | q,o ∼ P_sft(Q,O) | — | 1 |
| RFT | q∼P_sft, o∼π_sft(offline) | Rule | Eq. 10: I(o)∈{0,1} |
| DPO | q∼P_sft, o+,o−∼π_sft(offline) | Rule/preference | Eq. 14 |
| Online RFT | q∼P_sft, o∼π_θ(online) | Rule | Eq. 10 |
| PPO | q∼P_sft, o∼π_θ(online) | Model (RM) | Eq. 18: A_t (via GAE+V_ψ) |
| **GRPO** | q∼P_sft, **{o_i}^G ∼ π_θ(online, group)** | **Model (RM)** | **Eq. 21: Â_{i,t} + β(π_ref/π_θ − 1)** |

### Table C — GRPO 训练超参（§4.2）

| 项 | 值 |
|---|---|
| Base 模型 | DeepSeekMath-Instruct 7B |
| RL 数据 | 144K GSM8K+MATH CoT 问题 |
| Policy lr | 1e-6 |
| RM 初始 lr | 2e-5（基于 DeepSeekMath-Base 7B） |
| KL coeff β | 0.04 |
| Group size G | 64 outputs/question |
| Max len / batch | 1024 / 1024 |
| 更新策略 | 每探索阶段后单次 policy 更新 |
| Iterative RM replay | 10% 历史数据 |

### Table D — GRPO 收益（§4.2 Table 5, CoT）

| Benchmark | Instruct 7B | RL 7B | Δ |
|---|---|---|---|
| GSM8K | 82.9 | 88.2 | +5.3 |
| MATH | 46.8 | 51.7 | +4.9 |
| MGSM-zh | 73.2 | 79.6 | +6.4 |
| CMATH | 84.6 | 88.8 | +4.2 |

---

## 4. 与同类对比

- **vs PPO**（§4.1.1）：PPO 需一个与 policy 同量级的 V_ψ，且 per-token KL penalty 直接污染 reward（Eq. 2）。GRPO 删掉 V_ψ → 显存/算力大幅下降；KL 从 reward 移到 loss → advantage 干净。代价：每题须采 G=64 outputs（PPO 只需 1），**采样预算换价值函数预算**。
- **vs Online RFT**（§5.2.1 Figure 5）：Online RFT 的 GC = I(o)（Eq. 10），错误响应 GC=0（不惩罚），正确响应 GC=1（无差别强化）。GRPO 的 GC = group-normalized Â，可正可负且按 reward 量级 differential。实验上 GRPO 超越 Online RFT，证明"对错误响应负梯度 + 量级敏感"是关键。
- **vs DPO**（§A.1.4）：DPO 是 offline pairwise（o+, o− 均来自 π_sft），GC（Eq. 14）依赖 sigmoid(β·log-ratio 差)；本质是简化 RL（无显式 RM）。GRPO 用显式 RM + online group sampling，信号更细。
- **vs RFT/DPO 数据源**（Table 10）：RFT、DPO 是 offline（从 π_sft 采样），GRPO 是 online（从实时 π_θ 采样）。Figure 5 显示 online 在训练后期显著占优——因 actor 偏离 SFT 后，实时分布提供更 informative 的负样本。
- **vs Minerva 540B**（§2.3 Table 2）：7B 模型 MATH 36.2% > 540B Minerva 33.6%，证明参数量非唯一关键，高质量 web 语料 + code 初始化可弥补 77× 的规模差。

---

## 5. 跨论文关系（→ MOC 谱系）

GRPO 是本仓库 **RL 系统谱系的算法根**，下游分叉清晰：

- **算法根（本论文）** → [[deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning]] 直接继承 GRPO，去 RM（用 rule-based reward）做 RL 自我进化推理，是 GRPO 的 zero-RM 变体。
- **GAE 祖先** → [[high-dimensional-continuous-control-using-generalized-advantage-estimation]]：GRPO 的设计动机正是"在 LLM-only-last-token-reward 场景下 GAE 的 V_ψ 训不准"，是对 GAE 的简化替换而非延续。
- **多轮 agentic 搜索 RL 谱系（GRPO 的工程化延伸）**：[[search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning]]、[[areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning]]、[[beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl]]、[[single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning]] —— 这些后续工作普遍以 GRPO 为基线 RL 算法，但解决 GRPO 在多轮/异步/长 horizon 场景的同步瓶颈（GRPO 默认 group 内 G=64 同步采样，长 horizon 下 rollout 成本爆炸）。
- **DeepSeek 主线** → [[deepseek-v3-technical-report]]：DeepSeekMath 是 DeepSeek 数学能力的 7B 奠基，V3 在更大规模延续 GRPO 训练范式。
- **Prompt vs weight-space RL** → [[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]：GEPA 在 prompt 空间做进化，可视为 GRPO 重量级 weight 更新的轻量替代；本论文 §5.2.2 的"RL 提升 Maj@K 而非 Pass@K"暗示 RL 没扩展根本能力，正好为 GEPA 这类 prompt-空间方法留出空间。

---

## 6. 局限与边界

1. **几何与定理证明弱**（§6）：dry run 显示模型无法处理三角形与椭圆相关问题——预训练/SFT 数据选择偏差，非纯规模问题。
2. **few-shot 能力差**（§6）：GPT-4 随 few-shot input 提升明显，DeepSeekMath zero-shot ≈ few-shot——受限于 7B 规模。
3. **RL 不扩展根本能力**（§5.2.2 Figure 7）：Pass@K 不动，意味着 RL 是 alignment 性质而非 capability 性质。作者自陈"naive nucleus sampling"是潜在原因，但未验证——后续 tree-search-based sampling（[[tree-of-thoughts-deliberate-problem-solving-with-large-language-models]]，§5.2.3 引用 Yao et al. 2023）是否突破此上限是开放问题。
4. **arXiv 无用结论有边界**（§5.1.2）：未测 informalization、未测混合配比、未测更大模型；后续工作可能推翻。
5. **GRPO 的 group sampling 成本**：每题 G=64 outputs 是固定开销；长 horizon agentic 任务（多轮搜索、工具调用）下 rollout 同步开销是后续 AREAL/Beyond-10-Turns/SRAO 等工作要解决的工程瓶颈，本论文未触及。
6. **Reward model 噪声未处理**（§5.2.3）：作者指出 PRM800K 都有 ~20% 误标注，现行算法"完全信任 reward signal"是脆弱的；weak-to-strong alignment 留作 future work，本论文未实现。
7. **Code→Math 收益受模型容量限制**（§5.1.1）：one-stage mixed 在 1.3B 上反而损害 no-tool 数学，作者归因容量不足——更大模型上是否成立未验证。
