# Dual-Head Reasoning Distillation — 技术点深读（DEEP 2026-08-18, rewrite w/ M3 figure context）

> 论文：Xu et al., *Dual-Head Reasoning Distillation: Improving Classifier Accuracy with Train-Time-Only Reasoning*, NeurIPS 2025 (arXiv:2509.21487v2).
> 核心：把 CoT 的"推理成本"整体搬到训练期，推理期只跑 pooled classifier —— 即"推理即蒸馏，蒸馏不留痕"。

---

## 核心问题

Decoder-only LM 适配为 encoder-style 分类器时，主流做法是 **pooling hidden states + 轻量分类头**（如 HuggingFace `AutoModelForSequenceClassification`，§1）。这种适配虽高效，却**浪费了预训练阶段习得的潜在推理能力**（§1）。要激活推理，常规手段是 Chain-of-Thought (CoT) prompting，但 CoT 必须**逐 token 自回归解码 rationale**，对高吞吐场景造成严重的 throughput 惩罚（§1；Wei et al., 2022；Cheng and Van Durme, 2024）。

由此形成精确的两难：
- 用 pooled classifier → 快但欠利用推理能力；
- 用 CoT decoding → 准但 QPS 暴跌。

DHRD 攻击的就是这个 **accuracy-vs-throughput trade-off**：在保留 pooled classifier 推理期零开销的前提下，把 CoT 产生的 rationale 信号**仅在训练期**注入到 backbone 的表示学习中，使分类头在测试时无需任何 rationale 生成即可获得推理增益。论文给出的硬指标：在七个 SuperGLUE 任务上相对 pooled baseline 取得 **0.65%–5.47%** 的相对提升（§Abstract；§Table 1），同时推理 QPS 与 pooled classifier 持平，比同 backbone 的 CoT decoding 快 **96–142×**（§4.2）。这一"逼近 CoT 质量、零推理期解码"的定位在 Figure 1 的雷达图上一目了然（M3 caption 要点：DHRD 红色实线多边形稳定包围 baseline 蓝色虚线，并贴齐/超过紫色点线 Gemini 教师；CB/COPA/RTE 上缺口最大）。

---

## 关键创新点

### 1. 双头共享 decoder 架构（Dual-Head Architecture, §3.1 / Figure 2）
**机制**：在一个共享的 causal-attention decoder-only transformer 上挂两个轻量头，使单次 forward 同时支持分类与训练期推理（§3.1）。Figure 2（M3 caption 要点）刻画了这一数据流：共享 decoder 产出 hidden embedding tokens `ℝ^(L×D)`，向上分两支——
- **Classification head**（推理期使用）：Pooler 对输入 span（蓝色 tokens）做聚合，经 2-layer MLP 产出 K 类 logits `ℝ^K`。论文采用**最后一个真实输入 token**（即 `<REASON>` 之前）的 last-token pooling（§3.1，遵循 Suganthan et al., 2025 的 pooling-MLP 适配方案）。
- **Reasoning (LM) head**（仅训练期）：复用 base model 的 LM head，对完整序列 `s_i = [x_i, <REASON>, r_i, <ANS>, y_i]` 计算标准 causal LM next-token loss，产出 reasoning logits `ℝ^(L×V)`（§3.1, Eq. 1）。Figure 2 的 M3 要点明确：训练期输入是把分类序列（蓝）与教师 rationale tokens（橙）拼接，reasoning head 的 causal LM loss 覆盖两段，而 classification head 只作用于蓝色 span；推理期 rationale 被丢弃，仅走分类路径。

关键设计约束（§2）：**刻意保留 causal attention 与 last-token pooling**，避免 future-token leakage，并匹配 autoregressive pretraining 的归纳偏置（这是与 Gemma Encoder 这类双向注意力适配路线的明确分野）。

**效果**：单次 forward pass 同时支持分类与训练期推理；推理期只跑分类头 forward，无解码、无 KV-cache 增长、无额外参数开销 —— Figure 2 M3 要点的"key technical takeaway"即此：把教师 rationale 蒸馏进共享 decoder 的表示，推理期零延迟加成。

### 2. 加权联合目标（Weighted Objective, §3.2, Eq. 2–4）
**机制**：联合损失
```
L_total = β · L_cls + α · L_reason          (Eq. 4, α,β ≥ 0)
```
- `L_cls`：标准 K 类 cross-entropy（显式 log-softmax 形式，Eq. 2）。
- `L_reason`：覆盖**整个序列**（input + rationale + label）的 token-level causal LM cross-entropy，带 `m_{i,t+1}` mask（Eq. 3），N 为有效 token 数。

教师 rationale 由 **Gemini 2.5 Flash** 用 Zero-shot CoT prompt（"Let's think step by step"，Kojima et al., 2022）生成，且教师被**给定了 gold label** 但被规则禁止在 rationale 中复述 Yes/No（§E.3：须以 `[END OF REASONING]` sentinel 分隔解释与答案），以保证 rationale 是"解释"而非"答案泄漏"。

**效果**：α/β 在不同 backbone 上的最优点不同（§Table 1 / Table 3）：
- Llama-3.1-8B / Llama-3.2-3B / Qwen-3-8B：**α=β=1** 最优；
- Qwen-3-4B：**α=0.5, β=1** 最优（α=1 反而 −1.05%，Table 3）。
- 8B 的两个 DHRD 设置 Avg 都**超过教师 Gemini 2.5 Flash**（87.52 / 87.23 vs 86.40，§Table 1；Figure 1 M3 要点：8B 雷达图上 DHRD 红线在 Avg 轴上外扩超过紫色教师线）—— 学生反超教师，证明增益不是简单复制教师知识。

### 3. 推理期零 rationale（Train-Time-Only Reasoning, §3.2 / §4.2）
**机制**：推理时只输入 `x`，忽略 reasoning head，直接由 pooled 表示产出 `z`（§3.2 末段）。无 CoT 生成、无 KV-cache 增长、无采样。Figure 2 的 M3 caption 明示：reasoning head 与 rationale tokens 在 test time 被整体丢弃。

**效果（§Table 5）**：
| Backbone | QPS (pooled) | QPS (CoT) | 加速 |
|---|---|---|---|
| Llama-3.1-8B | 414.91 | 4.14 | ~100× |
| Llama-3.2-3B | 631.16 | 4.44 | ~142× |
| Qwen-3-8B | 341.15 | 3.56 | ~96× |
| Qwen-3-4B | 440.83 | 3.76 | ~117× |

pooled 路径比同 backbone CoT decoding 快 **96–142×**。

### 4. 关键消融：增益来自 input–rationale–label **三元组对齐**，而非通用 LM 正则（§4.3, Table 2）
**机制**：四组对照（均 α=β=1）：
- **ConsistentReasoningLabel**：`<REASON>` 与 `<ANS>` 均对齐（即 DHRD 正常设置）。
- **OnlyLabel**：去掉 `<REASON>`，只保留对齐的 `<ANS>`。
- **ShuffleReasoning**：`<REASON>` 错配（跨样本打乱），`<ANS>` 仍对齐。
- **ShuffleReasoningLabel**：`<REASON>` 与 `<ANS>` 均错配。

**效果（Llama-3.1-8B，相对 ConsistentReasoningLabel 的 Rel.Δ）**：
- OnlyLabel：**−1.75%**（去掉 rationale 即掉点，排除"纯 LM 正则"假说）。
- ShuffleReasoning：**−5.70%**（错配 rationale 比去掉更糟，说明错配信号是主动负信号）。
- ShuffleReasoningLabel：**−48.48%**，Avg 从 87.52 崩到 45.09（接近随机，MultiRC 的 F1/EM 跌到 0.0/0.5）。

3B 上同样模式：OnlyLabel −3.84%，ShuffleReasoning −20.24%，ShuffleReasoningLabel −45.27%（Table 2）。这是全文**最硬的证据**：lift 必须由对齐三元组产生，misalignment 在 entailment/causal 任务（CB/RTE/COPA）上崩得最狠（CB 在 ShuffleReasoning 下从 89.0/94.8 跌到 59.5/76.4）。这也印证 Figure 1 雷达图（M3 要点）—— CB/COPA/RTE 三个轴是 DHRD 相对 baseline 缺口最大的位置，恰是消融中崩得最狠的任务，机制上自洽。

### 5. 任务类型差异化增益（§4.1 / Figure 1）
**机制**：entailment / cause-effect 类任务依赖多步语言化推理，因此从 rationale 监督中获益最大；word-sense / coreference 类任务（WiC/WSC）主要依赖上下文锚定而非多步推理，因此增益小或持平。

**效果（§4.1）**：
- CB：Llama-8B 与 Qwen-8B 各 **+8.7% accuracy**；
- COPA：Llama-3B **+23.5% accuracy**（72.2 → 89.2，最显著单任务提升）；
- RTE / MultiRC / BoolQ：一致小幅提升；
- WiC/WSC：基本持平（WiC Llama-8B 74.8→74.6，WSC 91.5→91.1）。

Figure 1 的四张雷达图（M3 要点）直观呈现这一模式：四个 backbone 上 DHRD 多边形都在 CB/COPA/RTE 方向外扩最显著，而 WiC/WSC 方向与 baseline 几乎重合 —— 图与数一致。

---

## 表格（原文结构化）

### Table 1 — SuperGLUE 主结果（§4.1 / Figure 1 雷达图的数值版）
| Backbone | Setting | BoolQ | CB (F1/Acc) | COPA | MultiRC (F1a/EM) | RTE | WiC | WSC | Avg | Rel.Δ |
|---|---|---|---|---|---|---|---|---|---|---|
| Gemini 2.5 Flash | CoT Zero-shot | 88.8 | 83.1/92.0 | 98.4 | 86.2/59.1 | 91.3 | 71.6 | 94.5 | 86.40 | — |
| Llama-3.1-8B | Baseline | 90.7 | 81.9/90 | 93.8 | 88.9/62.9 | 91.4 | 74.8 | 91.5 | 86.29 | — |
| Llama-3.1-8B | DHRD (α=β=1) | 91.1 | 89.0/94.8 | 95.4 | 89.0/63.7 | 92.2 | 74.6 | 91.1 | **87.52** | +1.43% |
| Qwen-3-8B | Baseline | 89.4 | 83.5/93.2 | 93.8 | 88.2/62.0 | 91.9 | 75.1 | 89.0 | 86.09 | — |
| Qwen-3-8B | DHRD (α=β=1) | 90.5 | 90.8/95.6 | 93.2 | 88.5/62.5 | 91.9 | 76.6 | 89.7 | **87.23** | +1.32% |
| Llama-3.2-3B | Baseline | 89.0 | 78.6/88.8 | 72.2 | 83.5/49.8 | 84.3 | 68.1 | 77.4 | 77.34 | — |
| Llama-3.2-3B | DHRD (α=β=1) | 89.2 | 73.8/87.2 | 89.2 | 85.9/55.3 | 87.7 | 73.0 | 80.8 | **81.57** | **+5.47%** |
| Qwen-3-4B | Baseline | 88.9 | 84.3/91.6 | 92.4 | 87.7/62.0 | 90.4 | 71.4 | 85.6 | 84.50 | — |
| Qwen-3-4B | DHRD (α=0.5,β=1) | 89.5 | 84.4/92.0 | 92.8 | 88.1/62.4 | 90.8 | 71.4 | 87.4 | **85.05** | +0.65% |

要点：3B backbone 增益最大（+5.47%），4B 增益最小且需要更小的 α；8B 两模型 DHRD Avg 均超过教师 Gemini 2.5 Flash（与 Figure 1 雷达图 M3 要点一致：8B 红线 Avg 轴外扩超过紫线）。

### Table 2 — Rationale/Label 对齐消融（§4.3，摘 Llama-3.1-8B）
| DHRD Setting | BoolQ | CB | COPA | MultiRC | RTE | WiC | WSC | Avg | Rel.Δ |
|---|---|---|---|---|---|---|---|---|---|
| ConsistentReasoningLabel | 91.1 | 89.0/94.8 | 95.4 | 89.0/63.7 | 92.2 | 74.6 | 91.1 | 87.52 | — |
| OnlyLabel | 90.7 | 87.6/93.6 | 93.8 | 84.6/53.2 | 91.1 | 76.4 | 90.4 | 85.99 | −1.75% |
| ShuffleReasoning | 90.4 | 59.5/76.4 | 95.2 | 84.9/53.1 | 90.9 | 75.9 | 88.4 | 82.54 | −5.70% |
| ShuffleReasoningLabel | 62.2 | 35.4/51.6 | 44.6 | 0.0/0.5 | 50.0 | 50.0 | 65.1 | 45.09 | **−48.48%** |

### Table 3 — α/β 权重消融（§Appendix B，摘关键行）
| Backbone | Setting | Avg | Rel.Δ |
|---|---|---|---|
| Llama-3.1-8B | DHRD β=1,α=0.5 | 87.28 | +1.15% |
| Llama-3.1-8B | DHRD β=1,α=1 | 87.52 | +1.43% |
| Llama-3.1-8B | DHRD β=0.5,α=1 | 86.44 | +0.17% |
| Llama-3.1-8B | Reasoning/CoT (α=1,β=0) | 71.65 | −16.91% |
| Qwen3-8B | Reasoning/CoT (α=1,β=0) | 78.14 | −9.23% |
| Llama-3.2-3B | DHRD β=1,α=0.5 | 79.95 | +3.37% |
| Llama-3.2-3B | DHRD β=1,α=1 | 81.57 | +5.47% |
| Qwen-3-4B | DHRD β=1,α=0.5 | 85.05 | +0.65% |
| Qwen-3-4B | DHRD β=1,α=1 | 83.61 | **−1.05%** |
| Qwen-3-4B | DHRD β=0.5,α=1 | 82.67 | −2.17% |

要点：α 对小模型（4B）敏感且需更小值；β=1,α=1 是 8B/3B 的稳健最优点。Reasoning-only（β=0）+ 推理期 CoT 的 Avg 远低于 pooled baseline，证明联合训练与推理期弃用 reasoning head 两个设计缺一不可。

### Table 4 — SuperGLUE 数据规模（§Appendix C）
| Task | Type | Metric | Train | Val | Test |
|---|---|---|---|---|---|
| BoolQ | QA | Acc | 9427 | 3270 | 3245 |
| CB | NLI | F1/Acc | 250 | 56 | 250 |
| COPA | QA | Acc | 400 | 100 | 500 |
| MultiRC | QA | F1/EM | 27243 | 4848 | 9693 |
| RTE | NLI | Acc | 2490 | 277 | 3000 |
| WiC | WSD | Acc | 5428 | 638 | 1400 |
| WSC | Coref | Acc | 554 | 104 | 146 |

### Table 5 — QPS 吞吐（§Appendix D）
| Backbone | QPS (Pooled) | QPS (CoT) | Speedup |
|---|---|---|---|
| Llama-3.1-8B | 414.91 | 4.14 | ~100× |
| Llama-3.2-3B | 631.16 | 4.44 | ~142× |
| Qwen3-8B | 341.15 | 3.56 | ~96× |
| Qwen3-4B | 440.83 | 3.76 | ~117× |

### 配置摘要（§E.4 / §E.5）
| 项 | 值 |
|---|---|
| 硬件 | 8× H100 80GB, DDP NCCL |
| 微调方式 | PEFT-LoRA: q/k/v/o/up/down/gate_proj, r=16, α=32, dropout=0.1 |
| 可训练参数 | 仅 LoRA adapters + 分类头 |
| Optimizer | AdamW, LR 2e-4, wd 0.01, cosine warmup 5 |
| Precision | bf16 |
| Batching | per-device bs=1, grad_accum=32 |
| Epochs | 3 |
| Teacher | Gemini 2.5 Flash v3, Zero-shot CoT, gold label 注入但禁止复述 |
| 推理生成参数 | do_sample=True, temp=0.1, top_p=0.7, max_new_tokens=500 |

---

## 与同类对比

**vs. CoT prompting / decoding（Wei et al., 2022; Kojima et al., 2022）**
机制层差异：CoT 在推理期逐 token 解码 rationale，DHRD 把 rationale 监督**整体迁到训练期**并通过 LM loss 注入 backbone 表示，推理期零解码（Figure 2 M3 要点：reasoning head 与 rationale tokens 推理期被整体丢弃）。QPS 实测 96–142× 加速（§4.2 / Table 5）。质量上，DHRD 在 8B 上 Avg 反超教师 Gemini 2.5 Flash（87.52 vs 86.40，Figure 1 M3 要点：8B 雷达图 Avg 轴红线外扩超紫线），但单任务仍弱于教师（COPA 95.4 vs 98.4，WSC 91.1 vs 94.5）—— 即"逼近但不超越教师在需要显式推理的任务上"。

**vs. Self-Consistency / Tree-of-Thoughts（Wang et al., 2022; Yao et al., 2023）**
这类方法靠**多次采样 + 聚合**提升推理质量，进一步放大推理期成本。DHRD 不依赖采样，推理期是确定性单次 forward，方向相反：用训练期监督换推理期简化。

**vs. Classic Knowledge Distillation（Hinton et al., 2015; Kim & Rush, 2016）**
经典 KD 走 soft-label / logit matching 或 sequence-level KD。DHRD **不做 answer logit matching**（§2），而是对**教师生成的 rationale 文本本身**做 token-level LM loss，即"reasoning-aware distillation"。这与 e-SNLI（Camburu et al., 2018）、NILE（Kumar & Talukdar, 2020）、Shridhar et al. 2023 等 rationale distillation 工作的区别在于：DHRD 的 rationale **仅训练期使用**，推理期不生成、不依赖，student 是一个 pooled classifier 而非生成器。

**vs. Gemma Encoder（Suganthan et al., 2025）**
Gemma Encoder 把 decoder-only LM 改造成 encoder（启用双向注意力 + task-specific pooling + MLP 头）。DHRD **明确拒绝双向注意力**（§2），保留 causal attention + last-token pooling，理由是防止 future-token leakage 并匹配 autoregressive pretraining。两者共享 pooling-MLP 头设计（即 Figure 2 M3 所示的 classification head 蓝 span pooling→MLP），DHRD 在其上叠加 train-only reasoning head（橙 span 的 LM loss）。

**vs. CoT 压缩方法（HiddenCoT Liu et al. 2024；C3oT Kang et al. 2024；CCoT Cheng & Van Durme 2024）**
这些方法通过**减少 rationale token 数**（训练/推理期）来降低 CoT 成本，但**仍保留推理期 rationale 生成**。DHRD 是更激进的设计：推理期**完全不生成** rationale。论文承认（§A, §F）尚未做 budget-controlled 头对头对比，accuracy-per-token 与 calibration 的相对权衡**未解决**。

**vs. Reasoning-only fine-tuning（α=1, β=0，§Table 3）**
当把分类损失 β 设为 0、仅训练 reasoning head 并在推理期用 CoT decoding，Llama-3.1-8B Avg 仅 71.65（远低于 pooled baseline 86.29），Qwen3-8B 78.14。证明：纯 rationale 微调 + 推理期 CoT 反而劣化分类 —— DHRD 的联合训练（β>0）与推理期弃用 reasoning head 是**两个不可或缺**的设计选择。

**vs. Dual-head KD（Yang et al., 2024, arXiv:2411.08937）**
Yang et al. 用 auxiliary head 增强 logits 利用率。DHRD 的"双头"形态相似（Figure 2 M3 所示双分支结构）但机制不同：DHRD 的 reasoning head 不参与 logits 蒸馏，而是对 rationale 序列做 LM loss，作为**表示学习的辅助监督信号**。

---

## 跨论文关系（→ MOC 谱系）

DHRD 处于 **reasoning-distillation 分支** —— 它既不属纯 RL 推理涌现谱系，也不属纯 prompt-space 演化谱系，而是介于两者之间的"**推理监督 → 权重内化**"路线。

- **[[deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning]]**：R1 通过 RL 让推理能力在权重中涌现。DHRD 走的是"显式监督内化"而非 RL 涌现路径，但目标同构 —— 让推理不再依赖推理期显式生成。R1 用 reward 信号塑造 reasoning trace，DHRD 用教师 rationale 的 token-level LM loss 塑造 backbone 表示。两者构成"推理内化"谱系的两端：RL 端（无教师、reward 驱动）vs. 蒸馏端（有教师、rationale 监督）。
- **[[deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models]]**：GRPO 是 R1 之前的 RL 推理方法。DHRD 不用 RL，但其"训练期学推理、推理期不推理"的思路可视为对"推理期 compute 换精度"范式（含 GRPO 的多采样推理）的反向操作 —— 把推理 compute 前移到训练期一次性付清。
- **[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]**：GEPA 在 **prompt space** 演化推理模板，不更新权重。DHRD 是 GEPA 的对偶：在**权重空间**固化推理能力，推理期不再保留任何 prompt-level 推理模板。两者共同说明"推理能力可在 prompt 与权重两个空间之间迁移"，DHRD 是权重端的一个干净实例。
- **[[a-survey-of-large-language-models]]**：LLM survey 中的 distillation 与 adapter 适配语境。DHRD 把 decoder-only LM 适配为 encoder-style 分类器（pooling-MLP 头 + LoRA），叠加 reasoning distillation，是 survey 中"PEFT 适配 + 知识蒸馏"两条线的具体交汇。
- **[[root-mean-square-layer-normalization]]**：RMSNorm 是 Llama/Qwen 系 backbone 的标准 norm primitive。DHRD 在这些 backbone 上以 LoRA 微调，底层 normalization 不变 —— DHRD 的增益来自 head 与 loss 设计，不依赖 norm 层改动。

**谱系定位**：DHRD 属 "reasoning distillation" 子分支，位于 [[deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning]]（RL 涌现）与 [[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]（prompt 演化）之间的"权重内化"轴线，是其中"教师监督 + 推理期零开销"的极端点。

---

## 局限与边界

1. **强依赖教师 rationale 质量**（§A, §4.3）。教师必须产出 label-consistent 且不泄漏 label 的 rationale（§E.3 的 sentinel 规则）。Table 2 的 ShuffleReasoningLabel 把 Avg 从 87.52 砸到 45.09 —— 说明方法对"对齐"极度敏感，错配的 rationale 是主动负信号而非中性噪声。教师若系统性地产生错误或带偏见的 rationale，DHRD 会忠实放大（§A "amplification of biases under distribution shift"）。

2. **α 对小模型敏感**（§A, Table 3）。Qwen-3-4B 在 α=1 时 −1.05%，α=0.5 时 +0.65%；Llama-3.2-3B 在 α=0.5 时仅 +3.37% 而 α=1 时 +5.47%。没有跨规模的统一 α 调度，论文未给出 α 选择原则，仅靠验证集 grid search。curriculum anneal / task-aware α 是 future work（§F）。

3. **任务类型边界明确**（§4.1 / Figure 1）。增益集中在 entailment / causal 任务（CB、COPA、RTE，雷达图上外扩最显著的方向），WiC/WSC 基本持平甚至略降（WSC 91.5→91.1，雷达图上与 baseline 重合）。对依赖**多步语言化推理**的任务有效，对依赖**上下文锚定 / 词义消歧**的任务无效。这划定了方法的认知边界。

4. **未与 CoT 压缩方法直接对比**（§A, §F）。HiddenCoT / C3oT / CCoT 在"减少但保留推理期 rationale"的轴线上，与 DHRD"完全去除推理期 rationale"是不同设计点。论文明确承认未做 budget-controlled 头对头评估，accuracy-per-token 与 robustness-to-teacher-quality 的相对优劣**未解决**。

5. **单次运行，无置信区间**（§A）。受算力约束，每个设置只跑一次，仅靠 per-task 指标与 macro 平均、以及跨 backbone/α 的趋势一致性来缓解。统计显著性未建立。

6. **评估范围窄**（§A）。仅七个 SuperGLUE 任务（ReCoRD 作为抽取式 QA 被排除），仅 3–8B decoder-only backbone + last-token pooling + LoRA。其他语言、模态、领域、架构（encoder、encoder-decoder、更大 backbone、full fine-tuning）的泛化**完全未测**。

7. **推理期透明度损失**（§A）。推理期不生成 rationale，丧失了 contestability 与可解释性 —— 在高风险场景（审核、QA）中这是实质代价，论文建议 per-group model card + human-in-the-loop + 申诉机制作为缓解，但这是社会性而非技术性缓解。

8. **8B 反超教师的解释未深挖**。Llama-8B / Qwen-8B DHRD Avg 超过教师 Gemini 2.5 Flash（87.52 / 87.23 vs 86.40，Figure 1 雷达图可见），论文未深入解释为何 student 能超越 teacher —— 可能因 student 直接在任务训练集上 fine-tune 而教师是 zero-shot，也可能因 pooled 分类头比生成式 CoT 在某些任务上更稳定。这点既是亮点也是未解释的开放问题。

9. **仅硬监督，未尝试 soft-label KL**（§F）。当前 L_reason 是 token-level hard-target cross-entropy。temperature-scaled KL 蒸馏是否能在不增推理成本下提升稳定性与迁移，是 future work 但**尚未验证**。
