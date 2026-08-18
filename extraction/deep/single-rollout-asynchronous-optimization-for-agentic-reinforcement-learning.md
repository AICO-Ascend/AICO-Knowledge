# Single-Rollout — 技术点深读（DEEP 2026-08-18）
> 全要素深读笔记。独立文件，extract_phase1 重跑不丢。
> 论文：Single-Rollout Asynchronous Optimization for Agentic Reinforcement Learning · arXiv:2607.07508

## 核心问题

LLM 后训练正从监督预训练转向 RL，但主流 RL pipeline 仍是 **同步、batch-interleaved**：policy 生成一整批 rollout 后才开始优化（§1）。在长程 agentic / coding 任务中，rollout 长度高度不均匀——短轨迹很快结束、长轨迹成为 straggler，导致 GPU 大片闲置等待最慢样本（§1）。

**异步 RL** 通过“rollout 到达即消费”缓解这一问题，但带来两个未被充分解决的痛点（§1）：

1. **Policy lag 与不可控 off-policy**：单条轨迹可能被多个版本的 rollout 模型生成，导致更严重、更不可预测的 off-policy，损害训练稳定性。现有异步 RL 工作（AREAL、Noukhovitch et al.）多聚焦吞吐而忽视 effectiveness（§1、§5.2）。
2. **GRPO group-wise sampling 与异步 / 在线 agentic 设置结构性不匹配**：GRPO 对每个 prompt 采样一组响应、用组内均值做 advantage（§2）。组必须等最慢样本完成才进入训练，引入 *latency-driven off-policy*；且在线 / 复杂 agentic 环境往往每 prompt 只回传单条轨迹反馈，group-wise 无法成立（§1、§5.1）。

核心张力：**如何在保持异步效率的同时，让异步 RL 既稳定又有效**——尤其当 GRPO 这种主流 advantage 构造方式在异步、单轨迹反馈场景下失效时，用什么替代它。

## 关键创新点

1. **Direct Double-Sided Importance Sampling (DIS) —— 直接双边 token 级裁剪/掩码**（§3.1）
   - **机制**：标准 decoupled PPO 维护三个模型 πθ / πθold / πrollout。但异步下 rollout 引擎在单条轨迹生成期间可能多次更新，精确追踪 πθold 需维护 checkpoint 历史 {πθold^(1),…,πθold^(N)}，实际不可行。SAO 直接用 πrollout 作为 behavior proxy、对 πθ 做 importance sampling，即 `rt(θ) = πθ/πrollout = exp(log πθ(at|st) − log πrollout(at|st))`（式 2），**直接复用 rollout 阶段产生的 log-probabilities**，丢掉不准确的 πθold，省去单独 old-policy inference 的开销。
   - **双边校准函数**：`f(x; εℓ, εh) = x if 1−εℓ < x < 1+εh, else 0`（式 3）。区别于标准 PPO 只裁剪 (A>0, r>1+εh) 或 (A<0, r<1−εℓ) 的 token：SAO 把 trust region 严格限制在 `[1−εℓ, 1+εh]` 区间，**落在区间外的 token 完全从梯度中 mask 掉**，防止极端 policy divergence 引发失稳。
   - **效果**：以可控 off-policy bias 换取计算复杂度大幅下降 + 消除用单一可能 stale 的“latest old policy”带来的误差。实证支持更激进的裁剪、更好正则化 update step，异步下稳定训练约 1000 步（§3.1、§4.4）。与 IcePop（Team et al. 2025）相似但更简——进一步移除 πθold 仍能稳定。
   - 目标式（式 1）：`L(θ) = Ê_t[ f(rt(θ), εl, εh) Ât log πθ(at|st) ]`。

2. **Single-Rollout Sampling —— 以单轨迹替代 group-wise**（§3.2）
   - **机制**：每 prompt 仅采 1 条 rollout，生成完立即送训练（Figure 2：GRPO 必须等全组生成完才能训练，SAO 每条轨迹完成即可用）。彻底消除 group-wise 的 latency-driven off-policy，且天然适配每 prompt 仅单反馈的在线 / agentic 环境。
   - **挑战**：单 rollout 的梯度估计方差高（类似 REINFORCE），需一个足够好的 value model 降方差——这是 §3.2 后续三设计的动机。

3. **Faster Value Update than Policy (TTUR)**（§3.2）
   - **机制**：policy 每 1 次 gradient update 对应 value network K 次更新（实验 K=2）。policy-value 的 interdependence 是单 rollout 失稳主因——value 不准则 Ât 噪声大、policy 更新破坏性。让 critic 更快适应当前 policy 再用于 advantage 计算。
   - **效果**：Figure 4(a) —— 约 400 步后 SAO 的 Explained Variance 显著高于 single-critic-update baseline，value 收敛更快、与 policy 分布对齐更好。

4. **Frozen-Attention Value Training**（§3.2）
   - **机制**：pilot 实验发现 value model 梯度范数远大于 policy；分解后失稳主要来自 **Full Attention 层**，**MoE 层相对稳定**。故 RL 中冻结 Vϕ 的 attention 参数、仅优化 MoE 投影。假设：预训练 attention 权重已具备足够语义能力去 attend 相关 token，限制优化到 MoE 层即正则化 value model。
   - **效果**：Figure 4(b) —— 全参数训练 critic 梯度范数显著更大、优化不稳定；frozen-attention 维持更低更平滑的梯度。

5. **Skip-Observation Token-level GAE（agentic 专用 advantage 估计）**（§3.2）
   - **机制**：agentic 轨迹结构 `T = [a0, o0, a1, o1, …]`，ai 为模型动作、oi 为环境反馈。标准 GAE 算相邻 token 价值差，但 action 末尾 ai,N 到下个 observation 开头 oi,start 的转移对模型是不连续的（模型不生成 oi）——跨此边界算 advantage 会把 value model V(oi,start) 逼去预测外部环境状态，引入噪声。
   - **推导**：显式修改 Bellman target 跳过 observation token，把当前 action 价值直接连到下个 action。设 ai,N 是 action i 末 token、ai+1,0 是下个 action 首 token（式 4、5）：
     - `Â(ai,N) = δ + γλ Â(ai+1,0)`
     - `δ = rt + γV(ai+1,0) − V(ai,N)`
   - **效果**：advantage 估计仅依赖模型输出，过滤环境反馈的随机性。Appendix A.1 对照 step-level GAE（Step Average / Last-Token），token-level 在 Figure 6 与 Table 5 均更优——token 级提供更细粒度监督信号，对复杂推理轨迹的逻辑转移捕捉更准。

6. **Scaling Value Pretraining**（§3.2）
   - 价值估计的 **cold-start** 是主要瓶颈。显著扩大 value pretraining 语料规模，为 single-rollout + TTUR 提供稳健初始化，使机制在训练早期就生效。

7. **Simulated Online Learning 验证**（§4.5）
   - 任务：写作风格在线适应，奖励偏好分阶段切换为 cute / chuunibyou / classical（系统提示从 Academic/Cute/Chuunibyou 候选集切到 Classical/Cute/Chuunibyou）。GLM-4.7 作 LLM judge，`r = r_quality × r_style`（二元）。
   - **机制**：GRPO 依赖组内相对奖励，与“每 prompt 仅单轨迹反馈”的在线环境不兼容；SAO 用 value-based critic 提供 advantage，可从单轨迹做 policy 更新。
   - **效果**：Figure 5a —— SAO 在每次偏好切换后迅速抑制旧主导风格、重新对齐新目标。Figure 5b 对比 Running-Mean baseline（sliding window 128）—— Running-Mean 因历史窗口惯性出现明显 adaptation lag、稳定性能更低；SAO critic 动态追踪奖励漂移、恢复快、收敛高。确认 state-dependent baseline 在非平稳环境所必需的精度。

## 表格（原文结构化）

### Table 1 — Math reasoning benchmarks (Accuracy %)（§4.2）

| Model | AIME2025 | BeyondAIME | HMMT Nov 2025 | IMOAnswerBench |
|---|---|---|---|---|
| Claude-Sonnet-4.5 | 87.0 | 62.0 | 81.7 | 65.8 |
| GPT-5 High | 94.6 | 74.0 | 89.2 | 76.0 |
| GLM-4.7 | 95.7 | - | 93.5 | 82.0 |
| Qwen3-30B-A3B w/ python | 14.6 | 10.5 | 17.3 | 7.8 |
| Qwen3-30B-A3B w/o python | 85.0 | 63.0 | 76.7 | 55.3 |
| SFT (w/ python) | 80.4 | 53.3 | 75.2 | 53.3 |
| SFT (w/o python) | 14.6 | 46.8 | 17.3 | 42.0 |
| GRPO (w/ python) | 84.2 | 54.8 | 76.0 | 55.8 |
| **Qwen3-30B-A3B SAO (ours)** | **97.3** | **74.8** | **88.3** | **74.0** |
| — SAO (w/ DIS only) | 94.2 | 71.5 | 86.7 | 71.3 |
| — GRPO (+ DIS) | 93.5 | 70.8 | 84.0 | 70.0 |

### Table 2 — SWE-Bench Verified (Accuracy %)（§4.2）

| Model | Accuracy (%) |
|---|---|
| Qwen3-30B-A3B | 23.0 |
| + GRPO (w/ DIS) | 27.0 |
| + SAO (ours) | 29.8 |

### Table 3 / Table 4 — Value-model ablations (Accuracy %)（§4.3）

注：原文 Table 3 与 Table 4 caption 相同、数据略有重叠，此处并表呈现。

| Variant | Value Training Strategy | Critic Update Freq | AIME2025 | BeyondAIME |
|---|---|---|---|---|
| **SAO** | Frozen Attention | 2 | **97.3** | **74.8** |
| Single-step-update | Frozen Attention | 1 | 95.0 | 69.75 |
| Full-Parameter Value Training | Full-Parameter | 2 | 90.62 | 74.50 |
| SAO w/o Faster value | — | 1 | 95.0 | 69.8 |
| SAO w/o Frozen attention | Full-Parameter | 2 | 90.6 | 74.5 |
| Vanilla VAPO (w/o DIS) | — | — | 91.3 | 69.0 |
| Running mean baseline | — | — | 79.8 | 55.3 |

### Table 5 — Action granularity ablation (400 steps)（§A.1）

| Granularity | AIME2025 | BeyondAIME |
|---|---|---|
| Step-level (Average) | 85.8 | 60.5 |
| Step-level (Last-Token) | 87.3 | 62.8 |
| **Token-level** | **89.8** | **66.8** |

### 关键超参（§4.1）

| 项 | 取值 |
|---|---|
| Batch size | 128 |
| Group size (SAO) | 1 |
| Max length | 128k tokens |
| Policy LR | 1e-6 |
| ϵlow / ϵhigh (math, TIR) | 0.3 / 5.0 |
| ϵlow / ϵhigh (coding, SWE-Bench) | 0.8 / 3.0 |
| Length-adaptive GAE | λpolicy = 1 − 1/α^l, α = 1.5 |
| Value LR | 5e-6, λcritic = 1, 10-step warmup |
| K (faster value update) | 2 |
| GRPO 对照 batch | 16 prompts × 8 rollouts = 128 |
| SWE-Bench scaffold | OpenHands, 300 turns, 128k context |
| Eval | top-p=1.0, temp=1.0, 128k max; AIME/HMMT/IMO 16 runs, BeyondAIME 4 runs, 最多 50 turn |

## 与同类对比

- **vs. GRPO / GRPO+DIS**：SAO 在全部 5 个 benchmark 上一致优于（Table 1、Table 2）。标准 GRPO 约在 160 步 performance collapse（分数取崩溃前最后有效值）；GRPO+DIS 可稳定但 SAO 在约 400 步后明显拉开差距（Figure 3）。GRPO group-wise 的 latency-driven off-policy 与单反馈环境不兼容是结构性缺陷，SAO 用单 rollout + value-based critic 绕开。
- **vs. Vanilla VAPO (w/o DIS)**：约 90 步即崩溃（Figure 4c）——VAPO 维持近零 clip ratio 却无法有效 gate divergent off-policy updates；SAO 的 DIS 能主动裁剪偏离 token，稳定训练。VAPO ablation 性能 91.3 / 69.0 低于 SAO 97.3 / 74.8（Table 4）。
- **vs. Running-Mean baseline**：单 rollout 下用滑动窗口（128）均值做 baseline 的简化方案性能 79.8 / 55.3，远低于 SAO，证明训练良好的 value model 必要性（Table 4、Figure 5b）。在线环境中 Running-Mean 因窗口惯性出现明显 adaptation lag。
- **vs. SPO (Single-stream Policy Optimization, Xu & Ding 2025)**：同为 single-rollout-per-prompt 路线，但 SPO 与 running-mean 依赖训练数据难度的先验信息，性能不及 SAO（§A.2）。
- **vs. step-level GAE (Average / Last-Token)**：Table 5 —— token-level (89.8/66.8) > Last-Token (87.3/62.8) > Average (85.8/60.5)。token 级监督更细粒度，能捕捉复杂推理的逻辑转移；step-level 假设 step 内 token 共享统一学习信号、过度平滑。
- **vs. IcePop (Team et al. 2025)**：DIS 思路相近（双边 token 级裁剪），但 SAO 进一步移除 πθold、直接用 πrollout log-probs，更简（§3.1）。

## 跨论文关系（→ MOC 谱系）

SAO 位于 **agentic-RL 异步分支**，定位为“异步效率 + 稳定 effectiveness”的算法层贡献（非系统层）。

- **[[areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning]]** — 同为异步 RL，但是 **系统层 sibling**：AREAL 完全 decouple rollout/training、staleness-aware PPO 更新，聚焦 reasoning 任务的吞吐与效率；SAO 明确指出 AREAL 等“mainly focus on efficiency optimization rather than effectiveness”（§1），SAO 补其 effectiveness 缺口（单 rollout + DIS + value 设计）。两者可视为异步 LLM-RL 的“系统侧 / 算法侧”互补。
- **[[beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl]]** — long-horizon agentic search 的异步 RL，与 SAO 同处理“长程 agentic rollout 不规则”问题；SAO 的 skip-observation GAE 直接面向多轮 agentic 轨迹结构 `[a0,o0,a1,o1,…]`，是该方向的 advantage 估计算法补强。
- **[[hybridflow-a-flexible-and-efficient-rlhf-framework]]** — **同步框架前身**：HybridFlow 的 data-flow / data-future 设计是同步 batch-interleaved 范式（§1 批评对象）；SAO 的异步单 rollout 是对其同步屏障的算法层超越。
- **[[search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning]]** — R1 + 搜索工具 baseline，agentic reasoning-with-tool 谱系；SAO 的 TIR (Tool-Integrated Reasoning) 设置（Python 工具交错推理）是同类 agentic-reasoning 任务，SAO 在 BeyondAIME/IMOAnswerBench 上提供更稳训练。
- **[[cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation]]** — agentic RL，工具=编译器；同为“多轮 agentic + 工具反馈”轨迹结构，SAO 的 skip-observation GAE 对此类 oi=编译器反馈的场景同样适用。
- **[[deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning]]** — R1 谱系 RL 后训练代表，GRPO 路线；SAO 是对 R1/GRPO group-wise 在异步 agentic 场景失效的直接修正。
- 工业落地：SAO 已部署于 **GLM-5.2 (750B-A40B)** 的 agentic RL pipeline（摘要、§1）。

## 局限与边界

- **模型与任务范围**（§B）：实验基于 Qwen3-30B-A3B + 大规模 agentic reasoning / coding / 模拟在线写作。结论**不一定迁移**到更小模型、非 agentic RLHF、密集奖励 + 短 rollout 环境。
- **基础设施依赖**：SAO 依赖训练好的 value model + rollout log-probabilities。部署需基础设施能在异步生成期间**可靠保存 token 级 behavior probabilities**（§B）——对 rollout engine 的 log-prob 持久化能力有硬要求。
- **在线学习的安全差距**：在线学习研究是受控模拟偏好切换；真实面向用户的在线自适应需更强 safeguards、monitoring、privacy review（§B）。
- **value model 冷启动瓶颈**：scaling value pretraining 是关键但成本不低；若 pretraining 语料不足，single-rollout + TTUR 在训练早期无法生效（§3.2）。
- **off-policy bias 的可控权衡**：DIS 以“可控 off-policy bias”换“大幅降复杂度 + 消除 stale old policy 误差”（§3.1）——bias 仍是 bias，在极端 policy 漂移场景下被 mask 的 token 比例可能升高（Figure 4c clip ratio 监控是必要的健康指标）。
- **双生 Table 3/4 文献瑕疵**：原文 Table 3 与 Table 4 caption 几乎相同、数值部分重叠（AIME 97.3/95.0/90.62 vs 97.3/95.0/90.6），疑为排版冗余，引用时需注意取值一致性。
- **DIS-only 与 SAO 差距**：SAO(w/ DIS only) 94.2/71.5/86.7/71.3 已接近全 SAO 97.3/74.8/88.3/74.0（Table 1）——DIS 单独贡献很大，single-rollout + value 设计的边际增益虽显著但非压倒性，说明 value model 工程化是 SAO 的主要成本所在。
