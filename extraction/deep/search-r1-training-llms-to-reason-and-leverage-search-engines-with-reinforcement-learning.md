# Search-R1 — 技术点深读（DEEP 2026-08-18）

> 全要素深读笔记。独立文件，extract_phase1 重跑不丢。
> 论文：Search-R1: Training LLMs to Reason and Leverage Search Engines with Reinforcement Learning · arXiv:2503.09516v5 (COLM 2025)

## 核心问题

让 LLM 在 step-by-step reasoning 中**自主**调用搜索引擎获取外部/实时知识，存在三个被作者明确点出的挑战（§1）：

1. **RL Framework & Stability**：如何把（不可微、非参数化的）搜索引擎接入 LLM 的 RL 训练管线，且在 rollout 序列混入"模型生成 token"与"外部检索 token"两类异质内容时仍能稳定优化。检索内容若直接进入 policy gradient，会让模型去"学习"它根本不该负责生成的外部文档分布，产生 unintended learning dynamics。
2. **Multi-Turn Interleaved Reasoning + Search**：理想行为是模型按问题难度动态调整检索策略、迭代推理-检索-再推理，而非单轮 retrieve-then-generate。
3. **Reward Design**：在搜索+推理联合任务上，是否真的需要复杂的 process-based reward / 神经 reward model？还是 outcome-based 的简单信号就足够引导出 meaningful & consistent 的搜索行为？

既有路径的不足（§1, §2.1-2.2）：(a) RAG 以输入为 query 一次性检索，无关噪声多、context 不足；(b) IRCoT/ReAct 走 prompting 路线，泛化差、未在训练时优化"如何与搜索引擎交互"；(c) Toolformer 走 SFT 路线，依赖大规模高质量标注轨迹，且 search 操作本身不可微使端到端梯度下降不适用；(d) DPO/SimPO 等 direct optimization 存在 off-policy 问题，不及纯 RL。DeepSeek-R1（Guo et al. 2025）证明了纯 outcome reward 的 RL 能让 LLM 涌现 self-verification / self-correction，但**其潜力在搜索引擎调用场景几乎未被探索**——这正是 Search-R1 要补的空白。Search-R1 自我定位为 DeepSeek-R1-Zero 的扩展：从 parametric reasoning 延伸到 search-augmented RL（§1 末）。

## 关键创新点

### 1. 把搜索引擎建模为 RL 环境的一部分（§3.1，Eq.1/6）

- **机制**：经典 RLHF 目标 `max_{πθ} E[rϕ(x,y)] − β D_KL[πθ||πref]` 假设整条 y 由 policy LLM 独立生成。Search-R1 把目标改写为条件于搜索引擎 R 的形式：`max_{πθ} E_{y∼πθ(·|x;R)}[rϕ(x,y)] − β D_KL[πθ(·|x;R)||πref(·|x;R)]`（Eq.6）。轨迹 y 现在是"LLM 生成 token"与"R 检索回的 passage"交错拼接的序列，形式化记为 `πθ(·|x;R) = πθ(·|x) ⨝ R`（⨝ 表示 interleaved retrieval-and-reasoning，§3.1）。KL 散度在"条件于 prompt 与检索增强 context 的联合分布"上计算，保证即便混入外部信息，policy 仍被 reference 锚定。
- **效果**：使 PPO 与 GRPO 两种主流 policy-gradient 方法都能直接挂载搜索引擎 rollout，无需改算法骨架。Figure 1 给出 PPO/GRPO with Search Engine 的 rollout module 示意：policy LLM + Search Engine 在 Rollout Module 内交互，再回灌给 Reward Model / Group Computation / Value LLM。

### 2. Retrieved Token Loss Masking ——梯度只流过 LLM 自己生成的 token（§3.1，Table 4/6）

- **机制**：在 PPO（Eq.2）与 GRPO（Eq.3）的 token-level loss 中引入指示函数 `I(y_t)`：`I(y_t)=1` 当 y_t 是 LLM 生成 token，`I(y_t)=0` 当 y_t 是被 `<information>…</information>` 包裹的检索 token。求和项 `1/Σ I(y_t) · Σ_{t: I(y_t)=1}` 保证 policy gradient 只对 LLM 生成 token 计梯度，检索内容仅作 context 影响 advantage/未来 token 概率。**KL 散度损失 D_KL 的计算同样施加 retrieved token masking**（§3.1 末），避免 reference policy 被外部文档分布污染。
- **效果**（Table 4，Qwen2.5-7b-base/PPO）：w. mask 在 7 个数据集全面胜过 w.o. mask，Avg 0.431 vs 0.343（绝对 +0.088，相对 +25.6%）；NQ 0.480 vs 0.388、Musique 0.196 vs 0.108（近乎翻倍）。3b 上同样成立（Table 6：0.303 vs 0.262）。Figure 3 训练曲线显示 mask 版训练更稳、reward 持续上行，无 mask 版趋于震荡。这是论文最关键的稳定性贡献，也是"为何把搜索引擎塞进 RL 不会塌"的工程答案。

### 3. Multi-turn 交错推理-检索的 rollout 协议（§3.2，Algorithm 1，Table 1）

- **机制**：定义四对特殊 token：`<search>…</search>`（触发检索，内夹 query）、`<information>…</information>`（系统回填 top-k 检索结果）、`<think>…</think>`（reasoning 步）、`<answer>…</answer>`（终答）。Rollout 是一个 while 循环：当前 action 内 LLM 逐 token 生成直到遇到 `</search>`/`</answer>`/`<eos>`；若检测到 `<search>…</search>`，系统 `Parse` 抽取 query、`R(q)` 检索、把结果包进 `<information>` 拼回 y；若检测到 `<answer>` 则返回；否则注入"My action is not correct. Let me rethink."让模型重试。循环终止条件：达到最大 action 预算 B（实验设 B=4）或模型自发给出 `<answer>`。
- **Training Template**（Table 1）刻意只约束**结构**而非**内容**：禁止强制 reflective reasoning、禁止偏向特定解题策略，"ensures that the model's natural learning dynamics during the RL process remain observable and unbiased"——这是为了把搜索行为是否涌现作为可观测现象，而非模板的产物。
- **效果**（§5.3，Figure 2c/2d）：训练过程中 **# valid search 次数单调上升**（模型自发学会多检索）；response length 呈"先降后升再稳"——前 100 step 急降（base model 剔除 filler words、适应任务格式），100 step 后随模型学会频繁调用搜索而 length 与 reward 同步上行。Case study（Table 9/10）显示模型涌现 **self-verification through iterative retrieval**：在第二轮已获足够信息后仍主动发起第三轮检索去验证结论（与 R1-Zero 在纯推理中观察到的 self-verification 现象同源，§I）。

### 4. 极简 outcome-based reward ——拒绝 format reward 与神经 reward model（§3.4，Eq.4）

- **机制**：reward 仅 `rϕ(x,y) = EM(a_pred, a_gold)`（Exact Match 规则判定），a_pred 是从 `<answer>` 抽取的答案。**显式声明与 Guo et al. 2025 不同：不引入 format rewards**，理由是"learned model already demonstrates strong structural adherence"。同时拒绝训练神经 reward model，避免大规模 RL 对特定 reward 形式的敏感性 + 重训 reward model 的算力/复杂度成本。
- **效果**：仅凭 0/1 EM 信号即能引导出多轮检索、self-verification、query refinement 等复杂涌现行为——回答了挑战 (3)："simple outcome-based rewards are sufficient"。对比基线 R1（无搜索引擎的同套 RL，§4.2）证明加 search 的增益不是 reward 工程的产物。

### 5. PPO vs GRPO 的实证裁决 ——PPO 默认，稳定性优先（§5.1，Table 3，Figure 5）

- **机制/观察**：(1) GRPO 收敛更快——因 PPO 依赖 critic value function 需 warm-up；(2) PPO 训练更稳——GRPO 在长 step 后出现 reward collapse，PPO 全程稳定；(3) 两者 final reward 可比。作者据此把 PPO 设为默认（§4.3 "Unless stated otherwise, PPO is used as the default RL method"）。
- **数据**（Table 3，Qwen2.5-7b-base）：PPO Avg 0.431 vs GRPO 0.350；但 instruct 上 GRPO 反超（0.396 vs 0.385）——结论是"comparable"，选 PPO 主因是稳定性而非最终分。Figure 5 跨 4 个 LLM（3b/7b × base/it）复现同一规律：GRPO 早期上行陡、后期塌；PPO 平缓持续。

### 6. Base vs Instruct：RL 抹平起点差距（§5.2，Figure 4）

instruct 模型收敛快、起点高，但 base 模型经 RL 后 final reward 与 instruct 几乎一致（§5.2 "RL can effectively bridge the gap over time"）。含义：在 reasoning+search 场景，post-training 的价值主要在加速早期；对算力受限但能跑长 RL 的场景，base 模型是可行起点。这也支撑 Search-R1 把 R1-Zero-style RL 从"纯推理"推广到"搜索增强推理"的论断（§4.4 observation 3）。

### 7. 其他工程性发现

- **# retrieved passages（top-k）**（Appendix G，Table 7，7b-base/PPO）：k=3 最优（Avg 0.431），k=5 早期收敛最快但后期不稳、k=1 召回不足。归因：k=5 引入噪声 passage（low precision，引 Jin et al. 2024）不仅损推理还"discouraging the model from leveraging retrieved content when it learns the additional context is often unhelpful"——即 RL 会学到"忽略检索"的退化策略。
- **Group size（GRPO）**（Appendix H，Table 8，7b-base）：size=5 收敛最快但易塌；**size=1（退化为 REINFORCE）最稳且泛化最好**（Avg 0.410 vs size=5 的 0.350）——揭示 GRPO 中"learning speed vs stability"的 trade-off。
- **规模效应**（Appendix C，Table 5，14b）：Search-R1-base 14b Avg 0.479，全面碾压各基线；"increasing model size leads to consistent performance gains"。"Larger models are better on learning how to do search"（§4.4 observation 4）——7B 相对 RAG 的 gap 显著大于 3B。

## 表格（原文结构化）

### Table 2：主结果（Exact Match），7 个 QA 数据集（† in-domain / ⋆ out-of-domain）

| 方法 | NQ† | TriviaQA⋆ | PopQA⋆ | HotpotQA† | 2wiki⋆ | Musique⋆ | Bamboogle⋆ | Avg |
|---|---|---|---|---|---|---|---|---|
| **Qwen2.5-7b-Base/Instruct** | | | | | | | | |
| Direct Inference | 0.134 | 0.408 | 0.140 | 0.183 | 0.250 | 0.031 | 0.120 | 0.181 |
| CoT | 0.048 | 0.185 | 0.054 | 0.092 | 0.111 | 0.022 | 0.232 | 0.106 |
| IRCoT | 0.224 | 0.478 | 0.301 | 0.133 | 0.149 | 0.072 | 0.224 | 0.239 |
| Search-o1 | 0.151 | 0.443 | 0.131 | 0.187 | 0.176 | 0.058 | 0.296 | 0.206 |
| RAG | 0.349 | 0.585 | 0.392 | 0.299 | 0.235 | 0.058 | 0.208 | 0.304 |
| SFT | 0.318 | 0.354 | 0.121 | 0.217 | 0.259 | 0.066 | 0.112 | 0.207 |
| R1-base | 0.297 | 0.539 | 0.202 | 0.242 | 0.273 | 0.083 | 0.296 | 0.276 |
| R1-instruct | 0.270 | 0.537 | 0.199 | 0.237 | 0.292 | 0.072 | 0.293 | 0.271 |
| Rejection Sampling | 0.360 | 0.592 | 0.380 | 0.331 | 0.296 | 0.123 | 0.355 | 0.348 |
| **Search-R1-base** | **0.480** | **0.638** | **0.457** | **0.433** | 0.382 | 0.196 | 0.432 | **0.431** |
| Search-R1-instruct | 0.393 | 0.610 | 0.397 | 0.370 | **0.414** | 0.146 | 0.368 | 0.385 |
| **Qwen2.5-3b-Base/Instruct** | | | | | | | | |
| Direct Inference | 0.106 | 0.288 | 0.108 | 0.149 | 0.244 | 0.020 | 0.024 | 0.134 |
| CoT | 0.023 | 0.032 | 0.005 | 0.021 | 0.021 | 0.002 | 0.000 | 0.015 |
| IRCoT | 0.111 | 0.312 | 0.200 | 0.164 | 0.171 | 0.067 | 0.240 | 0.181 |
| Search-o1 | 0.238 | 0.472 | 0.262 | 0.221 | 0.218 | 0.054 | 0.320 | 0.255 |
| RAG | 0.348 | 0.544 | 0.387 | 0.255 | 0.226 | 0.047 | 0.080 | 0.270 |
| SFT | 0.249 | 0.292 | 0.104 | 0.186 | 0.248 | 0.044 | 0.112 | 0.176 |
| R1-base | 0.226 | 0.455 | 0.173 | 0.201 | 0.268 | 0.055 | 0.224 | 0.229 |
| R1-instruct | 0.210 | 0.449 | 0.171 | 0.208 | 0.275 | 0.060 | 0.192 | 0.224 |
| Rejection Sampling | 0.294 | 0.488 | 0.332 | 0.240 | 0.233 | 0.059 | 0.210 | 0.265 |
| **Search-R1-base** | **0.406** | **0.587** | **0.435** | **0.284** | 0.273 | 0.049 | 0.088 | **0.303** |
| Search-R1-instruct | 0.341 | 0.545 | 0.378 | 0.324 | **0.319** | **0.103** | **0.264** | 0.325 |

- **相对增益**（§4.4）：7B 相对 RAG 基线 Avg 0.431 vs 0.304 → +41%（abstract 称 24% 是相对"various RAG baselines"的均值口径，41%/20% 是相对 RAG 单一最强基线口径，二者一致）。3B 为 +20%。增益在 in-domain（NQ/HotpotQA）与 out-of-domain（TriviaQA/PopQA/2wiki/Musique/Bamboogle）同时成立。
- **Search-R1 > R1**（无检索 RL）：证明把 search 接入推理链提供外部知识确实带来净增益，而非 RL 本身的副作用。
- **7B 的 "performance gap" 大于 3B**：规模越大越会"学搜索"。

### Table 3：PPO vs GRPO（Search-R1，7 个数据集 EM）

| 模型 / 方法 | NQ | TriviaQA | PopQA | HotpotQA | 2wiki | Musique | Bamboogle | Avg |
|---|---|---|---|---|---|---|---|---|
| 7b-base (GRPO) | 0.395 | 0.560 | 0.388 | 0.326 | 0.297 | 0.125 | 0.360 | 0.350 |
| 7b-instruct (GRPO) | 0.429 | 0.623 | 0.427 | 0.386 | 0.346 | 0.162 | 0.400 | 0.396 |
| **7b-base (PPO)** | **0.480** | **0.638** | **0.457** | **0.433** | **0.382** | **0.196** | **0.432** | **0.431** |
| 7b-instruct (PPO) | 0.393 | 0.610 | 0.397 | 0.370 | 0.414 | 0.146 | 0.368 | 0.385 |
| 3b-base (GRPO) | 0.421 | 0.583 | 0.413 | 0.297 | 0.274 | 0.066 | 0.128 | 0.312 |
| 3b-instruct (GRPO) | 0.397 | 0.565 | 0.391 | 0.331 | 0.310 | 0.124 | 0.232 | 0.336 |
| 3b-base (PPO) | 0.406 | 0.587 | 0.435 | 0.284 | 0.273 | 0.049 | 0.088 | 0.303 |
| 3b-instruct (PPO) | 0.341 | 0.545 | 0.378 | 0.324 | 0.319 | 0.103 | 0.264 | 0.325 |

### Table 4 / 6：Retrieved Token Loss Masking 消融（PPO）

| 模型 | mask | NQ | TriviaQA | PopQA | HotpotQA | 2wiki | Musique | Bamboogle | Avg |
|---|---|---|---|---|---|---|---|---|---|
| 7b-base | w. mask | 0.480 | 0.638 | 0.457 | 0.433 | 0.382 | 0.196 | 0.432 | 0.431 |
| 7b-base | w.o. mask | 0.388 | 0.567 | 0.391 | 0.325 | 0.321 | 0.108 | 0.304 | 0.343 |
| 3b-base | w. mask | 0.406 | 0.587 | 0.435 | 0.284 | 0.273 | 0.049 | 0.088 | 0.303 |
| 3b-base | w.o. mask | 0.346 | 0.484 | 0.365 | 0.241 | 0.244 | 0.053 | 0.104 | 0.262 |

### Table 5：14B 主结果（Appendix C，证明规模收益）

| 方法 | NQ† | TriviaQA⋆ | PopQA⋆ | HotpotQA† | 2wiki⋆ | Musique⋆ | Bamboogle⋆ | Avg |
|---|---|---|---|---|---|---|---|---|
| Direct Inference | 0.198 | 0.531 | 0.184 | 0.217 | 0.253 | 0.045 | 0.160 | 0.227 |
| CoT | 0.190 | 0.495 | 0.148 | 0.269 | 0.297 | 0.054 | 0.432 | 0.269 |
| IRCoT | 0.114 | 0.375 | 0.166 | 0.230 | 0.248 | 0.102 | 0.312 | 0.221 |
| Search-o1 | 0.347 | 0.635 | 0.241 | 0.268 | 0.161 | 0.099 | 0.416 | 0.310 |
| RAG | 0.327 | 0.585 | 0.376 | 0.279 | 0.160 | 0.051 | 0.192 | 0.281 |
| SFT | 0.361 | 0.467 | 0.150 | 0.248 | 0.278 | 0.089 | 0.160 | 0.250 |
| R1-base | 0.369 | 0.626 | 0.270 | 0.306 | 0.326 | 0.117 | 0.488 | 0.357 |
| R1-instruct | 0.334 | 0.628 | 0.253 | 0.294 | 0.325 | 0.108 | 0.432 | 0.339 |
| **Search-R1-base** | **0.486** | **0.676** | **0.480** | **0.468** | **0.470** | **0.241** | **0.528** | **0.479** |
| Search-R1-instruct | 0.424 | 0.660 | 0.442 | 0.436 | 0.379 | 0.210 | 0.480 | 0.433 |

### Table 7：检索 passage 数（top-k）消融（7b-base/PPO，step 500）

| top-k | NQ | TriviaQA | PopQA | HotpotQA | 2wiki | Musique | Bamboogle | Avg |
|---|---|---|---|---|---|---|---|---|
| 1 | 0.426 | 0.614 | 0.422 | 0.393 | 0.296 | 0.146 | 0.328 | 0.375 |
| **3** | **0.480** | **0.638** | **0.457** | **0.433** | **0.382** | **0.196** | **0.432** | **0.431** |
| 5 | 0.479 | 0.634 | 0.440 | 0.394 | 0.343 | 0.156 | 0.352 | 0.400 |

### Table 8：GRPO group size 消融（7b-base）

| size | NQ | TriviaQA | PopQA | HotpotQA | 2wiki | Musique | Bamboogle | Avg |
|---|---|---|---|---|---|---|---|---|
| **1 (=REINFORCE)** | 0.463 | 0.605 | 0.449 | 0.392 | 0.413 | 0.163 | 0.384 | **0.410** |
| 3 | 0.385 | 0.580 | 0.396 | 0.329 | 0.333 | 0.117 | 0.400 | 0.363 |
| 5 | 0.395 | 0.560 | 0.388 | 0.326 | 0.297 | 0.125 | 0.360 | 0.350 |

### 关键超参（Appendix B.2）

PPO：policy lr 1e-6，value lr 1e-5，500 steps，warm-up ratio 0.285/0.015，GAE λ=γ=1，8×H100，total batch 512 / mini 256 / micro 64，max seq 4096，max response 500，max retrieved 500 token，FSDP + CPU offloading + gradient checkpointing，vLLM rollout（tp=1，gpu mem util 0.6），temp=1.0 top-p=1.0，β=0.001，ϵ=0.2。GRPO：policy lr 1e-6，group size 5（Verl 实现），500 steps，warm-up 0.285，其余同 PPO。max action budget B=4，top-3 retrieval 默认。检索知识源：2018 Wikipedia dump（Karpukhin 2020）；retriever：E5（Wang 2022）。训练集：NQ+HotpotQA 训练集合并。

## 与同类对比

| 维度 | Search-R1 | RAG (Lewis 2020) | IRCoT/ReAct (prompting) | Toolformer (SFT) | R1/DeepSeek-R1-Zero (Guo 2025) | Rejection Sampling |
|---|---|---|---|---|---|---|
| 检索触发方 | LLM 自主学（`<search>` token） | 固定：输入即 query | LLM 被 prompt 触发 | LLM 被 SFT 学会触发 | 无检索 | 复用 Search-R1 rollout 机制 + SFT |
| 训练范式 | RL（PPO/GRPO）+ outcome EM reward | 无训练 | 无训练 | SFT（需标注轨迹） | RL（纯推理） | SFT（拒绝采样） |
| 多轮交错推理-检索 | ✅ 原生支持（Algorithm 1） | ❌ 单轮 | ✅（prompt 限制） | ✅ | ❌ | ✅ |
| 检索 token 梯度处理 | **Masked（核心创新）** | N/A | N/A | N/A | N/A | N/A |
| 标注数据需求 | 仅 (question, gold answer) | 无 | 无 | 大规模高质量轨迹 | 仅 outcome | 仅 outcome 但 rollout 昂贵 |
| 公平对比下表现（7b） | Avg 0.431 | 0.304 | 0.239 (IRCoT) | 0.207 (SFT) | 0.276 (R1-base) | 0.348 |

Search-R1 的差异化定位：(1) 相对 prompting 系（IRCoT/ReAct/Search-o1）——在训练时优化"如何检索"，而非靠 prompt 泛化；(2) 相对 SFT 系（Toolformer）——绕开不可微 search 操作、绕开标注轨迹瓶颈；(3) 相对 R1——把 R1-Zero 的 outcome-RL 范式从 parametric reasoning 扩展到 retrieval-augmented reasoning，核心新增物是"retrieved token masking + 多轮 rollout 协议"；(4) 相对 Rejection Sampling——同样是 outcome 信号，但 Search-R1 用 online RL 而非离线 best-of-N，且 Table 2 显示 Search-R1-base 7b (0.431) > Rejection Sampling (0.348)。作者明确把 Re2G/RetroLLM 等复杂 retrieve-rerank-generate 排除出基线（§B.1），理由是它们 task-specific engineering 重、泛化/可扩展性差，与 Search-R1 的"lightweight and general"定位不符。

## 跨论文关系（→ MOC 谱系）

- **[[deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning]]** —— 直接父节点。Search-R1 自述为"extension of DeepSeek-R1 Zero"（§1 末），继承其 outcome-based reward、放弃神经 reward model、放弃 format reward 的极简哲学；不同处在于把 search 接入 rollout 并引入 retrieved token masking。R1 = RL-reasoning root，Search-R1 = R1 → +tool/search 的谱系延伸。
- **[[single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning]]** + **[[beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl]]** —— 同属"agentic search + RL"家族。Search-R1 是该谱系中**最早确立"outcome-RL + tool-use rollout + token masking"范式**的工作（arXiv 2503），后续 beyond-ten-turns 等把它推向长 horizon / 大规模异步；SRAO 关注单 rollout 异步优化。Search-R1 的 B=4 action budget 正是后续长 horizon 工作要突破的边界。
- **[[areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning]]** + **[[hybridflow-a-flexible-and-efficient-rlhf-framework]]** —— RL 训练系统侧。Search-R1 的工程栈（vLLM rollout + FSDP + CPU offloading + Verl/GRPO 实现）正是这类 RLHF 框架的消费者；HybridFlow/Verl 被直接引用为实现基底（§B.2 脚注 2）。Search-R1 可视为这些系统在 agentic tool-use 场景的典型负载。
- **[[cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation]]** —— 同属 agentic RL（LLM + 工具 + outcome RL），但工具是编译器/ profiler 而非搜索引擎；共享"retrieved/external token 不参与 policy gradient"的 masking 思想（cuda-agent 对编译器反馈文本同样需 mask）。
- **[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]** —— 对照节点。GEPA 主张"在自然语言轨迹空间反思式学习"可优于标量 policy-gradient，且不需微调权重（适用于闭源模型）；Search-R1 走的是相反路线——online RL 微调权重、reward 是 0/1 EM 标量。二者共同点：都把 rollout 轨迹作为学习信号，都强调 minimal reward design。可作"prompt-space vs weight-space optimization for tool-use"的对照实验对。
- 谱系定位：Search-R1 处于 **"RL-reasoning（R1 系）× tool-use / agentic-search"** 二维谱系的交点，是 R1-Zero 范式向 tool-augmented reasoning 迁移的奠基性工作。

## 局限与边界

1. **Reward 仅 EM、仅 QA 任务**：rϕ = Exact Match 限定于有 gold answer 的 factual QA；开放式生成、多可接受答案、主观任务无法直接套用。作者承认"leave the exploration of more complex format rewards for future work"（§3.4）。
2. **知识源单一**：仅 2018 Wikipedia dump + E5 retriever，且 top-k=3 固定。对实时性、多源（web、结构化库）、多模态信息未覆盖——作者列为 future work（§6 "diverse information sources beyond search"）。
3. **B=4 action budget**：多轮检索深度受限。复杂多跳问题（Musique 在 7b-base 仅 0.196）暴露了 horizon 不足——这正是后续 beyond-ten-turns 类工作要解决的边界。
4. **GRPO 不稳定性未根治**：Figure 5 显示 GRPO 在 4 个 LLM 上均出现 reward collapse，作者仅以"改用 PPO"回避，未给出 stabilizing GRPO 的方法（group size=1 退化为 REINFORCE 反而更稳，Table 8——但这削弱了 GRPO 的 group-relative 优势）。
5. **Base vs Instruct 的"gap 抹平"依赖长训练**：§5.2 结论成立的前提是能跑到 final reward 收敛；算力受限时 instruct 的早期优势仍重要，base 模型未必实用。
6. **未与复杂 RAG pipeline 直接对比**：Re2G、RetroLLM 等被显式排除（§B.1），故"超越 RAG baseline"的结论是在 lightweight RAG 口径下成立，未与 SOTA 重排/细粒度证据管线正面对决。
7. **检索 token masking 是经验性技巧，无理论保证**：论文以消融证明有效，但未给出为何 mask 在所有数据集一致正向的理论解释；mask 是否在更复杂工具（多步 API、有状态环境）下仍有效未知。
8. **Case study 揭示的失败模式**（Table 11）：模型有时无法分解复杂问题、会被无关检索 passage 误导——说明学到的搜索策略并非鲁棒，存在被噪声 passage 带偏的风险（与 top-k=5 噪声观察呼应）。
9. **未探索 process reward / dynamic retrieval based on uncertainty**：作者在 §6 明确列为 future work，意味着当前 reward 设计对"检索质量本身"无直接监督，模型只通过最终 EM 间接学习"何时不该信检索"。

---

**文件位置**：`/mnt/project/g00952465/AICO-knowledge/extraction/deep/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning.md`
**全文依据**：`extraction/fulltext/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning.txt`（arXiv:2503.09516v5, COLM 2025, 31 页）
