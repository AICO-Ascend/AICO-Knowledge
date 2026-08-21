# CUDA-Agent — 技术点深读（DEEP 2026-08-18；图织入更新 2026-08-21）

## 核心问题

CUDA-Agent 攻击的不是"LLM 能不能写出 CUDA 代码"，而是更精确的机制级问题：**通用 LLM 即使能写对 CUDA kernel，也几乎打不过 `torch.compile` 这条静态编译器基线**。论文 §1 给出量化诊断——在 KernelBench 上，Claude Opus 4.5 / Gemini 3 Pro 虽然达到 91.2%–95.2% 的 Pass Rate（§4.2, Table 1），但 Faster Rate vs. Compile 仅为 66.4%–69.6%（Overall），即大部分通过正确性检查的 kernel 仍比 `torch.compile` 慢；它们产生的是"naïve kernels that fail to outperform torch.compile"（§4.2）。

论文进一步把根因归结为两类现有范式的结构性缺陷（§1, §2）：

1. **Training-free refinement 范式**（STARK / ReGraphT / EvoEngineer / CudaForge）：依赖 hand-designed 启发式和 base model 的固有 CUDA 能力，"do not remedy the fundamental lack of CUDA-coding abilities in the base models"——性能被 base model 内在能力封顶。
2. **Fixed multi-turn fine-tune 范式**（Kevin / CUDA-L1 / ConCuR）：在固定的 execution-feedback 回路里 SFT/RL，"waste context length by including all previous solutions and constrain the agent's autonomy to learn debugging, search, and profiling strategies"（§1）。且 Kevin、CUDA-L1、ConCuR 都直接/间接在 KernelBench 上训练，存在 data leakage（§2.2, Appendix C）。

CUDA-Agent 要解决的问题因此可精确表述为：**如何让 LLM 在一个自治（autonomous）、可执行验证、profiling 反馈驱动的 agent 环境中，通过大规模 RL 真正习得 CUDA 优化能力（而非依赖 test-time 启发式或 benchmark 泄露），从而在 KernelBench 上系统性地超越 `torch.compile` 与最强专有模型。**

## 关键创新点

### 1. 可扩展训练数据合成管线（CUDA-Agent-Ops-6K）

**机制**（§3.1）：三阶段管线，M3 解读的架构图（Figure 1, p.3）显示数据流为线性左→右三段——(a) **Seed Problem Crawling**（蓝框）：从 PyTorch / Transformers 库挖掘 matmul/relu/conv2d 等 seed operator，构建基础计算原语仓库（reference operator 类为 `torch.nn.Module` 子类，含 `__init__`/`forward`/`get_init_inputs`/`get_inputs`）；(b) **Combinatorial Problem Synthesis**（绿框）：LLM 从原语库采样 ≤5 个 operator 类顺序堆叠成 fused task（如 conv2d→relu→matmul；不采样 `transformers`，因其已封装多原语）；(c) **Rubric-based Problem Filtering**（白框）：四象限硬过滤——Executable、Non-random（确定性，排除随机算子）、Reasonable Workload（eager 执行时间 1ms–100ms）、Non-trivial（anti-hacking：不同输入输出不能恒等），并额外做 AST 相似度去重（阈值 0.9）剔除与 KernelBench 相似的样本。Figure 1 的 key takeaway 是**质量控制与生成解耦**——LLM 合成的任务由确定性 rubric 过滤器 post-hoc 把关，保证 fused CUDA 任务可执行、非平凡、可直接评测。

**防泄露证据**（§C）：AST 相似度直方图（Figure 7, p.13）显示每条训练样本与全部评测样本的最大 AST 相似度分布集中在 0.25–0.35（峰值占比 ≈12%），黄色虚线标出 0.9 阈值，几乎无样本越过——训练集与评测集基本不相交，数据泄露/污染风险极小。这为后文对 Kevin / CUDA-L1 / ConCuR 的 leakage 批评（§2.2, Appendix C）提供了对称的自证。

**效果**（§3.1, §A, Table 3）：最终 6,000 条样本（CUDA-Agent-Ops-6K）。组成上 2-op composition 占 83.77%（主峰），torch×1 3.40%、torch×3 7.62%、torch×4 2.80%、torch×5 1.23%、transformers 1.18%。关键 insight：融合问题"not equivalent to trivially optimizing each operator in isolation and then chaining"——fusion 重塑优化景观（避免中间 global-memory 物化、couple stages through shared register/SMEM/occupancy）。

### 2. Skill-augmented agent loop + 非可破坏 reward 信号

**机制**（§3.2, Figure 2, Appendix B）：基于 OpenHands 框架的 ReAct-style agent loop，工具集 = Bash/Read/Write/Edit/MultiEdit/Glob/Grep/NotebookEdit/BashOutput/KillBash。闭环结构见 M3 解读（Figure 2, p.4）：左侧 **SKILL.md** 专家指令 + 含原始 PyTorch model / utils / 验证脚本的 **Workdir** 喂给中央 **CUDA Agent**；agent 产出 `kernels/kernel.cu` + `kernel_binding.cpp` + `model_new.py` 三件 artifact，派发至 **GPU Pool** 执行；Performance 面板回传 correctness check、generated kernel time、Torch eager time、compile time 四项指标，闭合反馈回路。M3 takeaway：轻量文件式脚手架（SKILL.md + workdir）让 LLM agent 迭代产出 fused CUDA kernel 并对标 GPU pool 基准，用 agent 生成 kernel 取代手写 reference kernel。

CUDA-specific 指令以 Anthropic **Agent Skills** 形式封装进 `SKILL.md`（§B.2 全文），定义标准 4 步流程：profile → 实现 `model_new.py`+`kernels/*.cu`+`*_binding.cpp` → 编译验证 → 迭代至 ≥5% 优于 `torch.compile`。**五重 anti-hacking 约束**（§3.2）：(1) verify/profile 脚本经文件权限保护不可改；(2) context manager 禁止 fallback 到 `torch.nn.functional`；(3) 5 个随机输入做 correctness（遵循 KernelBench 协议）；(4) profiling 含 device sync + warmup + repeated averaging；(5) 不提供 web search / 外部检索工具。

**Robust Reward**（§3.2, Eq.1）：离散 r ∈ {−1, 1, 2, 3}：

$$r = \begin{cases} -1 & \text{if correctness check fails} \\ 3 & \text{if } b(t, t_{eager}) \wedge b(t, t_{compile}) \\ 2 & \text{if } b(t, t_{eager}) \\ 1 & \text{otherwise} \end{cases}$$

其中 $b(t, t_0) = \mathbb{I}\big[(t_0 - t)/t_0 > 5\%\big]$ 表示对基线 $t_0$ 有显著加速。用离散 milestone 替代 raw `speedup = tcompile/tgen` 这种易受 outlier / 简单 kernel 偏置的连续信号（算子优化难度差异大，raw speedup 是不可靠的代码质量代理）。

**效果**（§4.3.2, Table 2）：去掉 Robust Reward 改用 speedup reward，Pass Rate 基本持平（96.8% vs 98.8%），但 Faster Rate vs. Compile 从 96.8% 暴跌到 60.4%，Speed-up geomean vs. Compile 从 2.11× 降到 1.25×。

### 3. RL 算法：多阶段 warm-up 解决 importance-ratio 爆炸

**机制**（§3.3, Figure 3）：作者发现初始 RL 只能稳定训练 17 步就崩溃。根因诊断：CUDA 代码在预训练数据中占比 <0.01%（§3.3 引 [10,13]），域分布严重 mismatch，产生大量低概率 token；当训练用 BF16、推理用 FP16 时，`πθ(at|st) ≈ 1e−9` 量级，importance ratio `ρt = πθ(at|st)/πθ_old(at|st)` 在精度地板附近剧烈波动甚至爆炸（与 Liu et al. [15] 同源机制）。

解法：**三阶段 warm-up**，M3 解读的训练管线图（Figure 3, p.5）清晰呈现虚线分隔的三段流水线——(1) **Single-Turn Warm-up**：Base Model 经 PPO 微调为 Single-Turn Model，提升基础 CUDA 生成能力；(2) **Agent Warm-up**：Single-Turn Model 作为 agent 跑出采样轨迹，轨迹双向分流——(a) 经 RFT（rejection fine-tuning）初始化 **Actor Model**，(b) 经 value pretraining 预训 **Critic Model**；(3) **Agentic RL**：actor–critic 对经 PPO 产出最终 **CUDA Agent**。M3 takeaway：single-turn warm-up 的采样 rollout 同时播种 actor 和 critic，在 PPO agentic RL 之前消解冷启动。

- **Actor Initialization (RFT)**：用 single-turn RL 后的模型在 agent loop 中采样轨迹，rejection sampling 双过滤（outcome：只留 R>0 的轨迹；pattern：剔除冗余多轮循环与违反 tool-call schema 的幻觉轨迹），SFT 目标初始化 actor：

$$\mathcal{L}_{RFT}(\theta) = -\mathbb{E}_{\tau \sim \mathcal{D}'} \Big[ \sum_{t=1}^{T} \log \pi_\theta(a_t \mid s_t, a_{<t}) \Big] \tag{2}$$

- **Critic Initialization (Value Pretraining)**：用轨迹 + outcome reward（末 token 给 r，其余 rt=0）预训 critic，GAE（γ=1, λ=0.95）算 target：

$$V^{targ}_t = V_\phi(s_t) + \hat{A}_t, \quad \hat{A}_t = \sum_{l=0}^{T-1-t} (\gamma\lambda)^l \delta_{t+l}, \quad \delta_t = r_t + \gamma V_\phi(s_{t+1}) - V_\phi(s_t) \tag{3}$$

$$\mathcal{L}_{VP}(\phi) = \frac{1}{2}\, \mathbb{E}_{\tau \sim \mathcal{D}} \Big[ \frac{1}{T} \sum_{t=0}^{T-1} \big( V_\phi(s_t) - V^{targ}_t \big)^2 \Big] \tag{4}$$

最终 PPO 用 **asymmetric clip**（ϵ_lower = 0.2, ϵ_higher = 0.28，依 DAPO [25]）：

$$\mathcal{L}_{CLIP}(\theta) = \mathbb{E}_{\tau \sim \mathcal{D}} \Big[ \frac{1}{T} \sum_{t=0}^{T-1} \min\big( \rho_t(\theta)\,\hat{A}_t,\ \mathrm{clip}(\rho_t(\theta),\, 1-\epsilon_{lower},\, 1+\epsilon_{higher})\,\hat{A}_t \big) \Big] \tag{5}$$

**效果**（§3.3, §4.3.3, Table 2）：训练从 17 步崩溃延长到稳定 200 步 + 一致 reward 增长（论文标题级数字 150 步训练）。两张消融曲线图（Figure 4, p.10 / Figure 5, p.10）的 M3 解读给出机制级证据：

- **Figure 4（Ablation: RFT）**：双面板（Training Reward / Actor Entropy，x 轴均为 training step）。PPO w/ RFT（橙线）平稳上升；PPO w/o RFT（绿线）reward 在 ~step 20 附近急剧崩塌，同时 actor entropy 大幅上冲（从 ~0.09 涨到 ~0.12）——policy 变得越来越弥散、结构崩坏。
- **Figure 5（Ablation: Value Pretraining）**：双面板（value function 的 Explained Variation / Response-Length Clipped Ratio）。w/ Value Pretrain（橙线）EV 平稳在零附近；w/o Value Pretrain（绿线）EV 跌到 ≈ −8（critic 学不到有意义的 value function，note 前文记的"跌到 ~2"以曲线为准为崩塌至负值量级），response length clipped ratio 飙到 ~0.25，即"near-infinite interaction loops"，训练随即终止。

M3 takeaway：RFT 与 Value Pretraining 是不可移除的稳定性锚点——消融触发的是**相关联的失败模态**（reward 崩塌 ↔ 熵爆炸；EV 崩塌 ↔ 轨迹爆炸）。整体 Faster Rate vs. Compile：w/o RFT 49.8%、w/o Value Pretrain 50.9%，full 96.8%。

### 4. 系统规模与 sandbox 解耦

**机制**（§4.1, §3.2）：base model = Seed1.6 MoE（23B active / 230B total）；global batch 1024 = mini-batch；actor lr 3e−6，critic lr 6e−6；context 单轮 RL 32768，agentic RL 131072；训练 150 turns 上限，评估放宽到 200 turns。**CPU-GPU 解耦 sandbox**：Docker terminal sandbox 处理编译，GPU sandbox pool（128 × NVIDIA H20）做 verify/profile，进程级隔离保证 HBM 独占与稳定延迟测量。这套 sandbox 正是 Figure 2 (p.4) 中 "GPU Pool" 方框的工程实现。

**效果**（§4.2, Table 1）：KernelBench Overall——Pass 98.8%、Faster vs. Compile 96.8%、Speed-up vs. Compile geomean 2.11×；Level-1/2/3 Faster vs. Compile 分别 100% / 100% / 92%（论文标题数字），Level-2 Speed-up vs. Compile 达 2.80×。比 Claude Opus 4.5（Level-3 Faster vs. Compile 50%）在 Level-3 高约 40 个百分点。

## 表格（原文结构化）

**Table 1 — KernelBench 主结果**（§4.2, 按 Level 分层；Overall 按 Level 1:100 / 2:100 / 3:50 加权）

| Model | Subset | Pass Rate | Faster vs. Eager | Faster vs. Compile | Speed-up vs. Eager (GM×) | Speed-up vs. Compile (GM×) |
|---|---|---|---|---|---|---|
| Seed1.6 (base) | Overall | 74.0% | 43.6% | 27.2% | 0.95× | 0.69× |
| GLM 4.6 | Overall | 75.6% | 44.8% | 19.2% | 0.78× | 0.57× |
| Kimi K2 | Overall | 66.8% | 40.8% | 22.8% | 0.93× | 0.66× |
| Gemini 3 Pro | Overall | 91.2% | 87.6% | 69.6% | 1.92× | 1.42× |
| Claude Opus 4.5 | Overall | 95.2% | 90.4% | 66.4% | 1.99× | 1.46× |
| **CUDA Agent** | **Overall** | **98.8%** | **98.4%** | **96.8%** | **2.60×** | **2.11×** |
| Gemini 3 Pro | Level 3 | 80.0% | 76.0% | 52.0% | 1.58× | 1.17× |
| Claude Opus 4.5 | Level 3 | 88.0% | 82.0% | 50.0% | 1.52× | 1.10× |
| **CUDA Agent** | **Level 3** | **94.0%** | **94.0%** | **90.0%** | **1.80×** | **1.52×** |

**Table 2 — 消融（leave-one-out, agent loop 评估）**

| Variant | Pass | Faster vs. Eager | Faster vs. Compile | Speed-up Eager | Speed-up Compile |
|---|---|---|---|---|---|
| w/o Agent Loop | 77.1% | 43.5% | 14.1% | 0.89× | 0.69× |
| w/o Robust Reward | 96.8% | 90.4% | 60.4% | 1.70× | 1.25× |
| w/o RFT | 95.6% | 82.0% | 49.8% | 1.56× | 1.05× |
| w/o Value Pretraining | 98.6% | 85.0% | 50.9% | 1.49× | 1.00× |
| **Full CUDA Agent** | **98.8%** | **98.4%** | **96.8%** | **2.60×** | **2.11×** |

**Table 3 — CUDA-Agent-Ops-6K 组成**（§A）

| 类别 | 占比 |
|---|---|
| torch operators ×1 | 3.40% |
| torch operators ×2 | 83.77% |
| torch operators ×3 | 7.62% |
| torch operators ×4 | 2.80% |
| torch operators ×5 | 1.23% |
| transformers operator (standalone) | 1.18% |

**关键配置速查**（§4.1, §3.2, §3.3）

| 项 | 值 |
|---|---|
| Base model | Seed1.6 MoE (23B active / 230B total) |
| Global batch / mini-batch | 1024 / 1024 |
| Actor lr / Critic lr | 3e−6 / 6e−6 |
| Context (single-turn / agentic) | 32768 / 131072 |
| Max agent turns (train / eval) | 150 / 200 |
| Training steps | 150 |
| GPU sandbox pool | 128 × NVIDIA H20 |
| PPO clip | ϵ_lower=0.2, ϵ_higher=0.28 |
| GAE | γ=1, λ=0.95 |
| Reward levels | {−1, 1, 2, 3}，5% speedup 阈值 |
| 训练集规模 | 6,000 (CUDA-Agent-Ops-6K) |

## 与同类对比

- **vs. torch.compile（编译器基线）**：CUDA-Agent 在 Level-2 (Operator Sequences) 取得 100% Faster Rate + 2.80× Compile Speed-up，关键差异是"learned optimization policies can consistently outperform static compiler heuristics, particularly in complex scenarios like operator fusion"（§4.2）。编译器依赖预定义 fusion pattern，难以处理 non-trivial 算子组合；CUDA-Agent 通过 agent loop 探索更大设计空间，发现 hardware-specific 的 memory access pattern 与 tiling。三个 Case Study（§D）的 M3 图解读给出机制级佐证：

  - **Case D.2 对角矩阵乘法（73.31× vs. Torch Compile）**：reference operator（Figure 8, p.22）是 `torch.diag(A) @ B`，A 为 1D 对角张量 `(N,)`、B 为 `(N, M)` 稠密矩阵，M=N=4096——朴素实现先物化 2D 对角阵再做 O(N²·M) 稠密 matmul。agent 生成的 kernel（Figure 9, p.23）用 grid-stride loop：1024 blocks × 128 threads，每线程由 `row = idx / 4096` 推出行号，直接写 `output[idx] = A[row] * B[idx]`——**不物化对角阵**，O(N·M) 完成，且 `A[row]` 在一行 4096 列上广播复用，输入存储仅 O(N+M)。`ModelNew` 封装（Figure 10, p.23）只是把 `(A, B)` 前递给编译好的 CUDA extension。M3 takeaway：对角 matmul 的优化空间在"跳过冗余零乘"，agent 自动发现了这一代数结构。
  - **Case D.3 sum-then-dot（24.04× vs. Torch Compile）**：reference（Figure 11, p.25）是四层融合线性归约——`Gemm: y = x·Wᵀ` → `/2` → dim-1 `Sum(keepdim)` → `×scaling_factor(1.5)`，W 为 `(hidden=8192, input=8192)`，batch=1024；sum-after-matmul 把输出压成 `(batch,1)`，主导开销是 8192×8192 GEMM。agent 的 fused 实现（Figure 12, p.26）分两级 kernel：**Stage 1 `sum_weight_kernel`** 每线程一列循环 hidden 维预累加 weight 列和到 `sum_weight[8192]`；**Stage 2 `dot_product_kernel`** 1024 blocks × 128 threads，float4 向量化点积（每次 load 4 个乘加）+ 共享内存 log₂(128) 树归约，thread 0 输出 `smem[0]·(scaling/2)`。数学等价变形把 O(8192²·1024) 的 matmul-then-reduce 降为 O(8192²) 列预和 + O(8192·1024) 点积，消掉中间 host 可见归约。`ModelNew`（Figure 13, p.27）单次调用 `cuda_extension.fused_sum_dot_forward` 完成 sum+dot+scaling 全融合，消除 kernel-launch 开销与中间内存往返。
  - **Case D.4 ResNet BasicBlock（3.59× vs. Torch Compile）**：reference（Figure 14, p.28）是标准双 3×3 conv + BN + skip-add + ReLU 结构（expansion=1，测试配置 in=3/out=64/stride=1/batch=10/224×224）。agent 版（Figure 18, p.31）做**推理态 BN-folding**——把每个 BatchNorm 的 γ/β/μ/var 吸收进前置 conv 的 weight/bias（`γ·W/√(var+ε)`, `β−μ·γ/√(var+ε)`），整个 residual block 塌缩为两次自定义 CUDA 调用（`conv_forwardd` + `fused_add_relu_forward`），TF32 精度只 scoped 到 conv 内部。配套的 fused add-ReLU kernel（Figure 17, p.30）用 float4 向量 load + `__fadd_rn` + `fmaxf(·,0)` 寄存器内融合 ReLU，配 scalar 尾部循环保证非 4 倍数尺寸正确，每线程吞吐 ×4 且消除中间显存写。

- **vs. Kevin / CUDA-L1 / ConCuR（fine-tune 同类）**：机制级差异——(a) Kevin 在 KernelBench 子集上训（§2.2, Appendix C），可能学到了 benchmark-specific adaptation；(b) CUDA-L1 直接从 KernelBench reference 构造 SFT 数据并在同一 benchmark 上 RL，明确"significant data leakage"；(c) ConCuR 的合成 kernel 来自 Kevin-32B（已在 KB 子集上训），故 KernelCoder 性能不反映独立数据训练能力。CUDA-Agent 用独立合成的 6K 数据 + AST 去重到 KernelBench（分布证据见 Figure 7, p.13），可公平对比。

- **vs. STARK / ReGraphT / EvoEngineer / CudaForge（training-free 同类）**：这些方法被 base model 固有能力封顶，且 CudaForge/STARK 用固定多 agent 角色（Judge+Coder / planning+coding+debugging）；CUDA-Agent 用单一 autonomous agent 自行决定何时调用工具。EvoEngineer 仅在 250 题中选 91 题，存在 selection bias；ReGraphT 目标是蒸馏到小模型而非绝对性能。论文明确指出这些 test-time 方法与 CUDA-Agent"orthogonal, could be applied to our model"（§2.1）。

- **vs. 通用 LLM（Claude Opus 4.5 / Gemini 3 Pro）**：在相同 agent loop 下评估（§4.1 公平性保证）。差异核心：专有模型 Pass Rate 高（95%+）但 Faster vs. Compile 低（66%），即"naïve kernels"；CUDA-Agent 经专门 RL 把 Faster vs. Compile 拉到 96.8%。论文还 footnote（§1）称 ChatGPT-5 系列（5/5.1/5.2）对 CUDA prompt 一律拒答，无法评估。

## 跨论文关系（→ MOC 谱系）

CUDA-Agent 在 RL 系统谱系中的定位：

- **[[deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning]]** — RL+reasoning 的根方法。CUDA-Agent 把"用 RL 激励 LLM 推理"从文本推理迁移到 CUDA 优化推理：reward 从"答案对错"换成"执行反馈驱动的 correctness+speedup 离散 milestone"，但精神同源（RL 激励内在能力，而非 SFT 模仿）。
- **[[areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning]]** — 大规模 async-RL 系统。CUDA-Agent 同样面对"scale 到 1024 batch + 128k context + 150 turns"的工程挑战，但走的是 CPU-GPU 解耦 sandbox + PPO 同步路线；可对照"同步 vs 异步"在大规模 agentic-RL 中的取舍。
- **[[single-rollout-asynchronous-optimimization-for-agentic-reinforcement-learning]]** — async agentic-RL。CUDA-Agent 的多轮 agent rollout（≤200 turns）正是 agentic-RL 长轨迹场景，其 Value Pretraining 解决的"长轨迹 value 估计崩塌"（Figure 5, p.10 的 EV 崩塌证据）与单 rollout 异步优化的动机高度互补。
- **[[search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning]]** — RL + tool/search。CUDA-Agent 也是 RL + tool（Bash/profiling），但工具空间收敛到 CUDA 编译/验证/profiling 闭环，reward 来自真实执行而非检索质量，是"RL+工具调用"在系统优化领域的特化。
- **[[huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod]]** 与 **[[nanoflow-towards-optimal-large-language-model-serving-throughput]]** — kernel/systems 性能上下文。CUDA-Agent 的产物（更快 CUDA kernel）正是这类大模型 serving 系统的性能底座；它自动化了 nanoflow / CloudMatrix 这类系统所依赖的手写 kernel 工程，形成"AI 优化 AI 基础设施"的闭环。
- DAPO [[25]]（`dapo-an-open-source-llm-reinforcement-learning-system-at-scale`）— CUDA-Agent 直接采用 DAPO 的 asymmetric clip (0.2/0.28)，是 RL 算法层的直接继承。

## 局限与边界

1. **未对比 TVM 等成熟编译器**（§E）：作者承认只对比 `torch.compile`，更 sophisticated 的编译框架（TVM 等）因"tuning overhead + 部署复杂"难以接入大规模 RL 回路而被排除。这留下"vs. TVM/Ansor"的开放问号——CUDA-Agent 是否真能超越 AutoTVM 的全局调度，尚未证实。
2. **资源成本极高**（§E）：依赖 128×H20 GPU pool + 进程级隔离，computational/engineering cost 可观，限制社区复现；作者明确把"更省资源的训练策略"列为未来工作。
3. **训练数据规模仍小**：6,000 条 operator-level 样本，且 2-op composition 占 83.77%——多样性集中在浅层组合，对深 stack（4-op/5-op 仅 ~4%）覆盖薄弱，可能影响对超长 fused pipeline 的泛化。
4. **基准单一**：仅 KernelBench Level 1–3（250 题），未覆盖 KernelBench Level 4 / Level 5、真实生产 kernel（如 FlashAttention 类手写 kernel）；Case Study 的 ResNet BasicBlock 仅 3.59× 优于 compile（Figure 14/17/18 显示其优化主要靠 BN-folding + add-ReLU 融合这类工程化手段），说明在复杂真实 block 上加速空间远小于对角矩阵乘法那种代数化简场景（Figure 8–10 的 73.31×）。
5. **reward 设计的边界**：Robust Reward 用 5% speedup 阈值做 milestone，但阈值是固定的；对不同硬件代际（H20 vs H100 vs B200）、不同算子类型，单一阈值是否最优未讨论。且 correctness 容差 atol=1e-2/rtol=1e-2 较宽松（§B.2 SUCCESS CRITERIA），可能放过数值不精确但"快"的 kernel。
6. **NCHW vs NHWC 折中**（§D.4）：Case Study 中尝试 NHWC 以对齐 Tensor Core，但 layout 转换开销抵消收益而放弃——说明 CUDA-Agent 仍受限于 PyTorch 默认 layout 生态，未能自主突破数据布局约束。
7. **warm-up 的可迁移性未验证**：三阶段 warm-up（single-turn RL → RFT → Value Pretrain，Figure 3, p.5）是为 Seed1.6 + CUDA 域量身设计的；换 base model 或换域（如 Triton kernel、ROCm）时，<0.01% 预训练占比的假设是否成立、importance-ratio 爆炸是否同样出现，论文未做跨模型/跨域验证。
8. **评估公平性的潜在偏差**：所有 baseline 在 CUDA-Agent 自己的 agent loop 下评估（§4.1），而 baseline 模型可能在其原生 agent loop（如 Claude Code / Gemini CLI）下表现更好；论文未提供 baseline 在自有 loop 下的数据。
9. **ChatGPT-5 系列缺位**（§1 footnote）：5/5.1/5.2 对 CUDA prompt 拒答，无法评估——SOTA 对比不完整。
