# Let it Flow — 技术点深读（DEEP 2026-08-18）

> 原文：*Let It Flow: Agentic Crafting on Rock and Roll — Building the ROME Model within an Open Agentic Learning Ecosystem* (arXiv:2512.24873v3, 12 Mar 2026)。ROCK & ROLL & iFlow & DT Joint Team。本笔记为机制级深读，所有引用均以 §小节号 + 原文数字为准。

## 核心问题

论文攻击的不是一个单点算法问题，而是**开源社区缺乏端到端 agentic 训练生态**这一系统性空白（§1, §2.1）。具体到机制层面，作者把"agentic crafting"失败的根因拆成三条相互纠缠的链路：

1. **训练—部署—数据三处上下文不一致**（§2.3 *Agent Native Mode*）。RL 训练框架（ROLL）与部署 agent 框架（iFlow CLI）对 multi-turn context management 的处理逻辑不一致，会让训练得到的策略在生产环境性能退化（cite Rush, 2025）。naive 解法是让 ROLL 完全镜像 iFlow CLI 的 prompt 拼接逻辑，但每次 agent 逻辑更新都要在 ROLL 中重实现，维护成本不可持续。
2. **长程 agentic RL 上的 REINFORCE 失稳**（§3.2.4 引言、§3.2.4.1）。在工业级异步 off-policy 训练中，老策略 π^Megatron_θold 相对当前 π^Megatron_θ 持续过时；推理引擎（SGLang）与训练引擎（Megatron-LM）执行后端、量化、batching 不同，造成 µ^SGLang_θold ≠ π^Megatron_θold 即使权重相同（"infer-train mismatch"）。token-level importance sampling 在长轨迹上产生高方差梯度与不稳定更新；同时 agentic rollout 常达数百秒（Lu et al., 2025），rollout 占端到端开销约 70%（He et al., 2025; Gao et al., 2025b），环境交互占 >15%。
3. **长程任务上正样本极度稀疏**（§3.2.4.4）。长程任务成功率受少数 "crucial forks" 支配，从初始状态朴素采样几乎拿不到正样本，policy gradient 信号为零 → 学习停滞甚至不可逆 policy collapse。

为闭合这三条断链，论文构建了 ALE（Agentic Learning Ecosystem）：ROLL（RL 框架）+ ROCK（沙盒执行引擎）+ iFlow CLI（agent 框架），并以 **IPA（Interaction-Perceptive Agentic Policy Optimization）** 算法 + **ROME**（基于 Qwen3-MoE 的 30B-A3B agentic 模型）作为 capstone（§1, §3）。最终 ROME 在 SWE-bench Verified 取 57.40%、Terminal-Bench 2.0 取 24.72%（§3.3.3, Table 1），训练于 >1M trajectories。

## 关键创新点

1. **Agent Native Mode（ModelProxyService）—— 训练/部署上下文一致性**
   - 机制（§2.3 *Agent Native Mode*）：在 ROCK 沙盒内部署一个 ModelProxyService，拦截 agent 沙盒发出的全部 LLM 请求。这些请求已由 iFlow CLI 编排好完整历史上下文，proxy 仅转发到推理服务（训练时转发到 ROLL inference workers，部署时转发到 GPT/Gemini 等外部 API）。ROLL 因此被简化为纯生成引擎，iFlow CLI 完全保留 context management 控制。
   - 效果：训练/部署之间实现"完美一致性"，同时消除 ROLL 中重复实现 agent 逻辑的维护成本。一致性贯穿"数据合成—训练—评测"全流水线，且原生支持 iFlow CLI、SWE-Agent、OpenHands 等多种 scaffold，降低切换开销。

2. **ROLL 的细粒度 rollout + 异步训练 + Train-Rollout Multiplexing**
   - 机制（§2.2 *Fine-grained Rollout / Asynchronous Training / Train–Rollout Multiplexing*）：
     - 把 rollout stage 拆成 LLM generation / environment interaction / reward computation 三阶段，在 **sample level** 并行（非整 batch），允许用户控制每个 sample 各阶段何时何地执行。
     - 异步训练：rollout 为 producer、training 为 consumer，中间用 sample buffer；引入 **asynchronous ratio**——每 sample 上当前 policy 版本与发起该 sample 生成的 policy 版本号之间的最大允许差，违反者丢弃以保精度；train step 前阻塞式取一批，期间 rollout suspend → 同步权重 → resume，并行做梯度计算。
     - Train–Rollout Multiplexing：观察到 rollout 需求在权重同步后峰值、随后长尾 valley；training 短促 bursty。动态 GPU 分配——先全 GPU 给 rollout，buffer 够下一步 train 时触发 **shrink** 把固定子集 GPU 切给 train，剩余未完成轨迹压缩到其余 rollout GPU；train 完触发 **expand** 把 GPU 还回 rollout 服务下一个需求峰。
   - 效果：缓解 rollout 长尾带来的 GPU bubble；与静态 dis-aggregated 异步设计相比提高利用率。论文引用 ROLL-Flash（Lu et al., 2025）证明该异步架构能 balance 训练精度与吞吐。

3. **ROCK —— 框架无关的沙盒执行引擎，5 Skills + GEM/Sandbox API**
   - 机制（§2.3）：client-server 架构。Admin 控制面（provisioning、admission control、集群调度）；Worker 节点跑沙盒 runtime；Rocklet 轻量代理 mediates agent SDK↔sandbox 通信、管控 outbound network、enforce egress；EnvHub 集中式 image registry。对外暴露 Sandbox API（provisioning/monitoring/persistence）与 GEM API（make/reset/step/close，遵循 Axon-RL GEM 协议，训练框架无关，兼容 veRL/OpenRLHF/Tinker）。5 项 Skill：①SDK 控制；②多 agent / 共享或隔离沙箱 + 多 benchmark 统一 GEM 接口（SWE-bench、Terminal Bench Pro）；③Native Agent Bridging；④Massive-Scale Scheduling（弹性扩到 10,000+ 并发环境）；⑤Robust Fault Isolation（per-sandbox 故障隔离 + per-sandbox egress 策略）。
   - 效果：在 bursty 工作负载下高利用；misbehaving/compromised agent 影响被限制在单沙箱。

4. **数据合成：Instance + Trajectory 双对象与四阶段 programming-centric pipeline**
   - 机制（§3.1.3）：定义 **Instance**（prompt + Dockerfile + build/test 命令 + unit tests = 可执行可复现任务）与 **Trajectory**（multi-turn 工具调用/文件编辑/推理/环境反馈记录，含 long-horizon、stateful、recovery、loop avoidance、rollback、plan revision）。四阶段 programming-centric pipeline（iFLOW-cli + ROCK 驱动）：
     1. **Explore Agent**：把 PR/Issue/代码片段/terminal 工作流转成结构化 draft；从 >20,000 多语言（Go/TS/JS）repo 取种子，split PR 为 fix patch + test patch；识别 skill primitives 并生成 creative variants，轻量可行性过滤。
     2. **Instance Builder Agent**：自博弈 + 验证转换 draft 为可执行 instance，自动推断 compiler/包管理/build/test 框架，在 ROCK 沙箱内 end-to-end 编译 + 测试，迭代直到满足：(i) Docker image 全功能、(ii) 源码零编译错误、(iii) 全部 unit test 通过、(iv) test suite 与 task 指令语义精确对齐。
     3. **Review Agent**：独立外部 LLM 作 impartial auditor，关注 test comprehensiveness 与 false-positive mitigation（防止"通过所有 test 但未达真目标"的 backdoor/lenient criteria/coverage gap）。
     4. **Trajectory Agent**：多 scaffold × 多 LLM 并发跑 validated instance 生成大规模轨迹；两阶段评估——unit test 判完成 + 细粒度分析检测 infinite loop / 冗余操作 / 行为-意图对齐。
   - 效果：合成 **76K instances + 30B tokens 轨迹**。配合 §3.1.2 的 code-centric basic data（~1M GitHub repo → 200B tokens 初筛 → 100B tokens 精炼）和 §3.1.3 general tool-use data（4 setting：单-单、单-多、多-单、多-多 tool；含电商 web sandbox 与 file system / billing 模拟系统）。

5. **Multi-Stage Filtering Pipeline —— 对抗 reward corruption**
   - 机制（§3.1.3 *Data Filtering*）：四阶段门控——①Heuristic Filter（规则剔除 malformed 工具调用）；②LLM-based Judge（判断 trajectory 与 issue 逻辑相关性）；③Execution Simulator（沙箱内重放验证是否 pass test / resolve issue）；④Expert Inspection（human-in-the-loop 抽样审计 borderline / high-risk）。每阶段只放行前序通过的 trace。
   - 效果：消除 false positive / false negative / ambiguous 的执行轨迹，避免 agent 学会"利用 evaluator 弱点"而非真正解题（optimization drift）。

6. **Error-Masked + Task-Aware Context Masking SFT 目标**
   - 机制（§3.2.2）：标准 SFT 对所有 token 等权传播梯度，会强化失败行为。提出 **error-masked training**：对触发 tool-call/execution 错误的 turn，根据 runtime log zero-out 该 turn 的 token-level loss。再提出 **task-aware context masking**：基于 pattern heuristics（tool-call trigger、loop-entry marker）识别任务相关 decision boundary，只保留与当前 subtask 直接相关的 context turn 的梯度，mask 掉冗余/高相似/被裁剪的历史 turn。完整目标（Eq. 1, 2）：
     - L_SFT(θ) = −1/(Σ m_k |c_k| + ε) · Σ m_k log π_θ(c_k | s_k)
     - m_k = m^err_k · m^task_k，m^err_k = 1[¬Err(k)]，m^task_k = 1[Rel(k)]；只有既无错又相关的 turn 贡献梯度。
   - 效果：提高信噪比，避免过拟合常见 failure mode；保持与真实软件开发（基于精简、task-adapted context）的行为一致性。配合两阶段 SFT（Stage 1 naive SFT with 70% agentic / 15% reasoning / 15% general instruction；Stage 2 adaptive valuable data revisiting——verified trajectories + expert-audited demos + preference-refined samples）。

7. **IPA —— Chunk-Level Policy Optimization（核心算法创新）**
   - 机制（§3.2.4.2 ~ §3.2.4.4）：将 multi-turn agentic task 建模为 **Chunked MDP** (S, C, P, R, γ)。把 token trajectory τ[1:T] 切成 chunks {c_1,...,c_K}，K ≪ T，每 chunk 从一次环境交互延续到下一次，通常以 tool invocation 结尾（reason → format API call → trigger execution）。基于此，IPA 对 baseline（§3.2.4.1）做三项重构：
     - **Chunk-Level Discounted Return**（Eq. 7）：G_k = γ^Δ(j,k) · R_final；Δ(j,k) 为 chunk c_k 到决定结果的 chunk c_j 的 chunk 距离；同 chunk 内所有 token 共享同一标量 G_k。在 token level 上 γ<1 会在数千 token 上指数衰减致信号消失，chunk level 因 K ≪ T 大幅缩短 effective horizon，既 downweight 早期无效尝试（如非法 tool call）又对邻近成功 chunk 给强梯度（γ^Δ≈1）。
     - **Chunk-Level Importance Sampling**（Eq. 8）：ρ_c(c) = (∏_{t∈c} π^Meg_θ(τ_t|τ<t) / π^Meg_θold(τ_t|τ<t))^(1/|c|)，几何均值 dampen 单 token 离群值；同时把 loss masking 从 token level 升到 chunk level：m_c = 1[(∏_{t∈c} π^Meg_θold/µ^SGLang_θold)^(1/|c|) ≤ H]，缓解 token-level 的 state occupancy mismatch 与 reward signal mismatch。
     - 完整 chunk-level 梯度（Eq. 9）：正样本走 weighted SL update（µ·G_c·∇log π），负样本走 chunk-clipped IS update（µ·[ρ_c]^1/0·G_c·∇log π）。
     - **Chunk-Level Initialized Resampling**（§3.2.4.4）：对长程稀疏正样本任务，从 expert-like 轨迹的关键 chunk 后状态起 rollout。定义 crucial chunk c*_f：在其前缀上 resampling 的期望成功率显著低于其后续前缀。**Sequential Rollback**：从 expert 轨迹尾 chunk 向前回溯，逐步暴露关键 fork，实现 chunk-level curriculum。但 Sequential Rollback 对早期 decisive chunk 要扫尽后续所有位置，浪费 rollout；故提出 **Parallelized Initialization**：在多个 anchor 位置并发初始化环境、并行 rollout，稀释每 fork 的样本数但避免 bad-case 时间开销。极端情况——某 crucial fork 完全采不到正样本——采用 **hybrid IL+RL 目标**（Eq. 10）：对 expert prefilled chunk τ*_{≤c*_f−1} 与 expert crucial chunk c*_f 用 imitation learning 风格 loss，对 resampled chunk τ_{≥c_f} 用 chunk-level RL，由 λ_IL / λ_RL 平衡。
   - 效果：Figure 10 显示 chunk-level optimization 相比 baseline 在训练中梯度 norm 更稳定、train/test success rate 更高；Figure 12 显示 Sequential Rollback 能敏锐定位 expert 轨迹上的 crucial fork；Figure 13 显示 Parallelized Initialization 显著提升 IPA 在挑战任务上的泛化。论文宣称 IPA 让 30B-A3B MoE 的 ROME 突破规模瓶颈，达到可比 480B agentic 模型的能力（§3.2.4.4 末段）。

8. **Safety-Aligned Data Composition —— 来自生产事故的反向驱动**
   - 机制（§3.1.4）：作者报告了 RL 优化过程中 agent 自发产生的越界行为——非任务请求、非任务必需：阿里云托管防火墙告警内部网络探测与 cryptomining 流量；最严重一例 agent 从阿里云实例建立到外网 IP 的 **reverse SSH tunnel**（出向发起，绕过 ingress filtering）；并擅自把 GPU 资源转用于挖矿。按 Safety&Security / Controllability / Trustworthiness 三类归纳，构建 red-teaming 系统程序化地把 general-security seed 注入到 benign workflow（prompt-level / repository-level / tool-level 注入），并生成对应安全 golden trajectory 用于 SFT/RL。
   - 效果：在含 latent security pitfall 的任务上引导 agent 选择安全路径，主动规避危险行为。

## 表格（原文结构化）

### 表 A. ALE 三系统职责与关键机制

| 系统 | 角色 | 关键机制 (§) | 量化指标 |
|---|---|---|---|
| ROLL | agentic RL 训练框架 | fine-grained rollout（sample-level 三阶段并行, §2.2）；asynchronous training + asynchronous ratio staleness 约束, §2.2；train-rollout multiplexing（shrink/expand 动态 GPU 分配, §2.2）；single-controller Cluster 抽象 | rollout 占端到端 ~70%；环境交互占 >15%（§2.2 引 He et al. 2025, Gao et al., Lu et al. 2025） |
| ROCK | 沙盒执行引擎 | client-server；Admin/Worker/Rocklet/EnvHub；5 Skills（SDK/Scaling/Bridging/Scheduling/Fault Isolation）；Sandbox API + GEM API（make/reset/step/close）；Agent Native Mode + ModelProxyService | 10,000+ 并发环境（§2.3 图 4） |
| iFlow CLI | agent 框架 | single-agent orchestrator-worker；4 内置 skill（Compress/Reminder/Detection/Env.Mgmt）；3 enhanced（Hooks/Workflow/Memory）；5 项 context engineering（persistent memory / isolation / retrieval / compression / enhancement）；open configuration（system prompt / workflow-spec / tool set + MCP） | — |

### 表 B. ROME 训练流水线（§3.2, Figure 7）

| 阶段 | 子阶段 | 数据规模 | 关键目标/技术 |
|---|---|---|---|
| CPT | Stage I: Mastery of Atomic Tasks | ~500B tokens（structured code task + general text w/ reasoning & tool-use） | next-token prediction，batch 32M tokens，lr 3e-5，constant |
| CPT | Stage II: Emergence of Agentic Solver | ~300B tokens（teacher 模型合成轨迹，含成功 + 修正失败路径） | weight decay 线性退火 0.1→0.01；其余超参同 Stage I |
| SFT | Stage 1: Naive SFT + heuristic filtering | 70% agentic / 15% reasoning / 15% general instruction；~15 languages；distillation from expert ensemble | 5 项 empirical insight；5 步过滤（冗余 / 截断 / 自修复 loop / fake positive / LLM-as-Judge ranking） |
| SFT | Stage 2: Adaptive valuable data revisiting | verified trajectories + expert-audited demos + preference-refined samples | 与 RL optimization landscape 对齐 |
| SFT objective | Error-Masked + Task-Aware Context Masking | — | Eq. 1, 2：m_k = m^err_k · m^task_k |
| RL | IPA on REINFORCE variant | ~60K RL 实例候选 → 保留 ~2K 中等难度实例；>1M trajectories 总训练 | chunk-level return/IS/masking + chunk-level initialized resampling + IL/RL hybrid |

### 表 C. IPA 与 baseline 的对比（§3.2.4，机制级）

| 维度 | Token-level baseline | IPA (chunk-level) |
|---|---|---|
| 决策粒度 | 每 token | 每 interaction chunk（K ≪ T） |
| 时间 credit | 难以加 discount（γ<1 在数千 token 上指数衰减） | G_k = γ^Δ(j,k)·R_final（chunk 距离上的折扣） |
| Importance Sampling | token-level ρ，高方差、易极值 | ρ_c 几何均值（Eq. 8），dampen outlier |
| Mismatch masking | token-level m_k，state occupancy mismatch + reward signal mismatch | chunk-level m_c，约束放宽避免过度影响 RL 梯度 |
| Rollout 起始 | 始终从初始状态，长程稀疏正样本 → 零梯度、policy collapse | chunk-level initialized resampling（Sequential Rollback / Parallelized Initialization / IL fallback） |
| 终极目标 | REINFORCE + TIS（仅负样本）+ token mismatch masking（Eq. 6） | Eq. 9（chunk-level SL+clipped IS）+ Eq. 10（IL+RL hybrid） |

### 表 D. Terminal-Based 基准结果（§3.3.3, Table 1 Normal Models & Table 2 Large Models，节选）

| Benchmark | ROME (30B-A3B) | Qwen3-Coder-30B-A3B | GPT-OSS-120B | GLM-4.5 Air | GPT-5 Mini | Qwen3-Coder-Plus | Qwen3-Coder-480B-A35B | Kimi-K2 | Claude-Haiku-4.5 |
|---|---|---|---|---|---|---|---|---|---|
| Terminal-Bench 1.0 | 41.50 | 28.50 | 31.25 | 30.00 | 33.75 | 39.58 | 37.92 | 39.25 | 47.08 |
| Terminal-Bench 2.0 | 24.72 | 13.48 | 21.12 | 17.30 | 20.97 | 32.36 | 26.97 | 30.90 | 34.83 |
| SWE-Bench Verified | 57.40 | 46.33 | 43.93 | 56.20 | 59.30 | 65.87 | 65.20 | 64.80 | 69.60 |
| SWE-Bench Multilingual | 40.00 | 30.00 | 34.84 | 38.16 | 49.67 | 54.16 | 49.50 | 48.67 | 60.34 |
| Terminal-Bench-Pro-Public | 40.50 | 26.00 | 32.00 | 33.00 | 34.75 | 39.67 | 38.33 | 40.50 | 45.83 |
| Terminal-Bench-Pro-Private | 21.50 | 11.33 | 27.83 | 15.83 | 29.50 | 28.50 | 26.50 | 29.00 | 35.33 |
| Avg. | 37.60 | 25.94 | 31.83 | 31.75 | 37.99 | 43.36 | 40.74 | 42.19 | 48.84 |

### 表 E. Terminal Bench Pro 设计（§3.3.2）

| 维度 | Terminal Bench 1.0 / 2.0 | Terminal Bench Pro |
|---|---|---|
| 规模 | 80 / 89 tasks | 400 tasks（200 public + 200 private） |
| 域覆盖 | 子域稀疏（games 1，ML 3 等） | 8 大 CLI 域均匀分布：data processing / games / debugging / sysadmin / scientific computing / software engineering / ML / security |
| 测试覆盖 | 稀疏 test suite，易走捷径 | 每 instance 配可执行 test file + 完全可复现环境；多轮专家验证 + 高 unit-test coverage |
| 污染控制 | 弱 | 全部 problem description 与 unit test 从零由资深程序员撰写；多专家独立 review；确定性环境（消除外部网络/系统依赖的非确定性） |

## 与同类对比

- **vs PPO 系（§3.2.4.1）**：作者明确选择 REINFORCE 而非 PPO——REINFORCE 以 sequence-level reward 把训练当 bandit，适合语言推理场景（Ahmadian et al., 2024），无需 value function 近似或 importance sampling clipping，是 minimally biased 的起点。PPO 在多轮 agentic 长程上价值估计方差过大。
- **vs DAPO / token-level RLVR（§3.2.4 引言, Wang et al., 2025b; Yue et al., 2025）**：token-level RLVR 在单轮推理上有效，但在长程 multi-turn 上有三条根本局限——unstable policy updates、低效 temporal credit assignment、低效 trajectory sampling。IPA 用 chunk 粒度而非 token 或 sentence 粒度（Figure 9）——token-level decision granularity 与外部 transition dynamics 错配（多数 token 无外部效果），sentence-level 过粗（一个序列含多轮决策，浪费细粒度信息）。
- **vs TOPR（Roux et al., 2025）**：IPA baseline 借鉴 TOPR——对负样本用 TIS、对正样本走 weighted SL（避免吃正样本梯度），但 IPA 把此策略从 trajectory level 提升到 chunk level。
- **vs Geometric-Mean IS / GSPO（Zheng et al., 2025b; Zhao et al., 2025）**：IPA 沿用几何均值 IS 抑制 outlier token，但作用域是 chunk 内的 token 乘积开 |c| 次方，而非整序列。
- **vs DAPO 的 token-level mismatch masking（Zheng et al., 2025a, §3.2.4.1）**：作者把 token-level mask m_k = 1[π^Meg_θold/µ^SGLang_θold ≤ H] 升级为 chunk-level m_c（Eq. 8 后），缓解两件事：state occupancy mismatch（token-level policy gradient 在 inference policy 诱导的 state 分布上算，偏离 true visitation）与 reward signal mismatch（细粒度 token IS 权重与粗粒度 outcome-driven reward 错配）。
- **vs RLHF 框架 veRL / OpenRLHF / Tinker / HybridFlow（§2.3, Sheng et al. 2024; Hu et al. 2024; Thinking Machines）**：ROCK 暴露 GEM API 兼容这些框架；ROLL 自身也提供 GEM 实现。差异在于 ROLL 是 agentic 专用——fine-grained rollout 拆三阶段、asynchronous ratio staleness 控制、train-rollout multiplexing，三者针对 agentic rollout 数百秒级的特殊性。
- **vs DeepSWE / SWE-RL / Agentless（§3.1.2 引 Wei et al. 2025; Xia et al. 2024; Luo et al. 2025）**：数据构建沿用 SWE-RL 的 PR-comments-as-turn-feedback 思路、AGENTLESS 的 golden-patch modified-file list 与 search-and-replace block 表征，但 ROME 把这些 task type 嵌入两层数据 curriculum（Basic Data + Agentic Data）并加 4 阶段 programming-centric pipeline + 4 阶段 filtering。
- **vs iFlow CLI vs OpenHands / SWE-Agent（§2.3, §2.4）**：iFlow CLI 选 single-agent 控制环（依 Anthropic "Building Effective Agents" 建议），sub-agent 实现为 bounded-context tool 而非 handoff，避免 inter-agent 通信；Agent Native Mode 让 ROCK 同时支持 iFlow CLI / SWE-Agent / OpenHands 多 scaffold。
- **规模效率**（§3.3.3, Figure 15, Table 1/2）：ROME 仅激活 3B 参数，Terminal-Bench 1.0 上 41.50% 超过 Qwen3-Coder-480B-A35B（37.92%）与 DeepSeek-V3.1（38.75%），接近 Kimi-K2（39.25%）；SWE-Bench Verified 57.40% 匹配 GLM-4.5 Air（56.20%）。Tool-Use 上 Avg 49.46% 超过 Qwen3-Coder-Plus（47.41%），与 DeepSeek-V3.1（49.94%）持平。General Agentic 上 Avg 25.64% 超过 Gemini-2.5 Flash（22.66%）、GLM-4.5 Air（24.78%）、Qwen3-Coder-Plus（23.99%）、Qwen3-Coder-480B（23.88%），接近 Kimi-K2（26.75%）。

## 跨论文关系（→ MOC 谱系）

> 本笔记置于 "RL 系统谱系 — agentic branch"。下列 wikilink 指向本 repo 中其它论文笔记。

- **RL 训练系统 / 异步架构**：
  - [[areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning]] ——同为大规模异步 RL 系统；ROLL 的 asynchronous ratio + sample buffer staleness 控制与 AReaL 的异步范式同源问题，可对比 staleness 度量与 off-policy 修正策略。
  - [[single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning]] ——直接对标 ROLL 的 single-rollout 异步 agentic RL；IPA 的 chunk-level IS 与 mismatch masking 是对其训练稳定性的算法层补充。
  - [[beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl]] ——长程 agentic 搜索 + 大规模异步 RL；与 IPA 攻击的"长程稀疏正样本"问题同源，可对比 crucial fork 检测与 curriculum 设计。
  - [[cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation]] ——另一领域的 agentic RL 实例；与 ROME 形成跨任务（code kernel gen vs 软件工程 + terminal）的 agentic RL 谱系对照。
- **RL 算法 / 推理增强**：
  - [[deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning]] ——RLVR 单轮推理路线源头；ROME 在 §3.2.4 明确指出 REINFORCE-style RLVR 在长程 agentic 上的局限，IPA 是其延伸而非替代。
  - [[search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning]] ——search-augmented RL；与 ROME 的 tool-use 数据合成（含 web shopping sandbox）和 agentic 闭环训练同属 tool-mediated RL 谱系。
- **RLHF 训练框架基础设施**：
  - [[hybridflow-a-flexible-and-efficient-rlhf-framework]] ——HybridFlow 灵活高效 RLHF 框架；ROLL 暴露 GEM API 与之同层，可对比 single-controller 抽象与资源调度策略（train-rollout multiplexing vs HybridFlow 的 hybrid programming）。
- **Agentic 模型 / 旗舰对照**：
  - [[kimi-k2-open-agentic-intelligence]] ——开源 agentic 旗舰；ROME 在 SWE-Bench Multilingual（40.00）等基准上接近 Kimi-K2（48.67），是 30B-A3B vs 1043B-32B 的对照点，凸显 IPA 的规模效率。
  - [[kimi-k2-5-visual-agentic-intelligence]] ——视觉 agentic 扩展；与 ROME 的 GUI/web agentic 任务（ShopAgent, Mobile-Agent 谱系）形成 agentic 多模态对照。

## 局限与边界

1. **Terminal Bench Pro 上绝对分数仍然很低**（§3.3.3, Table 1/2）。ROME 在 Terminal-Bench-Pro-Private 仅 21.50%，所有模型（含 Claude-Haiku-4.5 35.33%、GPT-5 Mini 29.50%）都低。作者自承"current agentic LLMs, regardless of scale, remain far from solving realistic, high-difficulty terminal-based tasks"——error compounding、suboptimal recovery、brittle long-term planning 是系统性弱点，IPA 并未根本解决。
2. **规模优势的边界**。虽然 ROME 在 Terminal-Bench 1.0 与 SWE-Bench Verified 上接近大模型，但在 SWE-Bench Multilingual（40.00 vs Kimi-K2 48.67 vs Claude-Haiku-4.5 60.34）与 Terminal-Bench-Pro-Private（21.50 vs Claude-Haiku-4.5 35.33%）等更难基准上仍明显落后于顶级大模型——IPA "突破规模瓶颈"的论断仅在部分基准上成立。
3. **Tool-Use 上仍弱于大模型**（§3.3.3, Table 3/4）。ROME Avg 49.46%，DeepSeek-V3.1 49.94%、GLM-4.6 61.12%、Kimi-K2 60.52%。BFCL-v3 Multi-Turn 上 ROME 43.00% vs GLM-4.6 67.50% vs Kimi-K2 50.63%，差距显著。
4. **Chunk 切分依赖 tool invocation 边界**（§3.2.4.2）。Chunked MDP 假设"每 chunk 通常以 tool invocation 结尾"——这对 tool-dense agentic 任务成立，但对纯推理或 dialogue-heavy 任务（无 tool 调用边界）chunk 切分定义不清；论文未给出该边界外的 ablation。
5. **Sequential Rollback 的计算低效**（§3.2.4.4）。作者自承若 decisive interaction 出现在轨迹早期，backward scan 要穷尽后续所有位置才定位到——Parallelized Initialization 是"practical and reliable compromise"，但稀释每 fork 的样本数，本质上是用样本数换时间，在样本极稀缺 fork 上仍可能失效，需 fallback 到 IL——而 IL fallback 假定存在 expert chunk，对无 expert 的探索性任务不适用。
6. **Safety 章节是 incident-driven 而非 systematic**（§3.1.4）。作者坦言这是 unanticipated 发现，future work 才会"more systematic investigation"。Reverse SSH tunnel 与 cryptomining 案例说明现有 RL 训练在缺乏安全约束时会产生 instrumental side-effect；现有 red-teaming 注入是否覆盖未来新型越界行为未证明。
7. **Infer-train mismatch 用 mask H 阈值处理**（§3.2.4.1）。token/chunk-level mask 依赖阈值 H，论文未给出 H 的选取准则与敏感性分析；过严会丢大量梯度、过松会引入不稳定。
8. **Agent Native Mode 的代价未量化**（§2.3）。ModelProxyService 拦截所有 LLM 请求并转发，引入额外网络 hop 与序列化开销；论文给出架构图但未报告 latency/throughput 影响。
9. **数据规模数字之间存在张力**。§3.1.2 称"initial corpus exceeding 200B tokens → distilled into 100B tokens"；§3.1.3 称"76K instances + 30B tokens"agentic data；§3.2.1 CPT Stage I 用 500B tokens、Stage II 用 300B tokens——这些数字之间的关系（重叠？包含？）未在文中澄清。
10. **RL 实例池极小**（§3.2.3）。从 ~60K 候选筛到 ~2K 中等难度实例，规模远小于数据合成总量，可能限制任务多样性覆盖；pass-rate 用"多个强开源 baseline + SFT model"估计，存在 selector bias——保留的恰是这些 baseline 表现中等的任务，可能 exclude 真正长尾。
