# Kimi K2: Open Agentic Intelligence — 技术点深读（DEEP 2026-08-18）
> 全要素深读笔记。独立文件，extract_phase1 重跑不丢。
> 论文：Kimi K2: Open Agentic Intelligence · arXiv:2507.20534v2（3 Feb 2026）
> 本文文本/图/表/公式交织分析；图表上下文取自 M3（MiniMax-M3 vision）caption（10 张，按页码排序），不直接读原图。

## 核心问题

Moonshot 团队针对「agentic intelligence」（模型自主感知/规划/推理/行动的能力）作为下一代基础模型的 defining capability 这一范式转移（§1），试图同时解决预训练与后训练两侧的核心瓶颈：

1. **预训练侧 — Token 效率瓶颈**：高质量人类数据日益稀缺，token efficiency（每 token 带来的性能增量）成为 scaling 的「critical coefficient」（§2 引言）。Muon optimizer 在 [[muon-is-scalable-for-llm-training]]（Moonlight）中已被证明 ~2× compute-efficient，但 scaling Muon 会暴露 attention logits 爆炸的稳定性问题 —— 现有缓解手段（logit soft-cap、QK-Norm）对 MLA 不可用或不够（§2.1）。
2. **后训练侧 — Agentic 数据稀缺与对齐开放性**：多步推理、长期规划、工具使用在自然数据中罕见且昂贵；纯 RLVR 无法覆盖创意写作等主观任务的对齐需求（§1, §3.2.2）。
3. **系统性约束**：万亿参数 MoE 的训练基础设施需兼顾研究效率（小/大规模实验共享并行配置）与推理效率（agentic 场景对长上下文延迟敏感）（§2.4）。

K2 以 1.04T 总参 / 32B 激活参数的 MoE，在 15.5T tokens 上 zero-loss-spike 预训练 + 大规模 agentic 数据合成 + RLVR+self-critique 后训练，定位为「most capable open-weight LLM particularly in software engineering and agentic tasks」（§1, §6）。其结果总览见 **Figure 1（p.1）** —— 七 panel bar chart 对比 K2-Instruct 与 DeepSeek-V3-0324 / Qwen3-235B-A22B / GPT-4.1 / Claude 4 Opus+Sonnet / Gemini 2.5 Flash(non-thinking)，分 Agentic & Competitive Coding（SWE-bench Verified/Multilingual、LiveCodeBench v6、OJBench）与 Tool Use（AceBench、AIME 2025）两组；M3 解读要点：K2 在 SWE-bench Verified(65.8) 与 Multilingual(47.3) 领先开源非思维模型、LiveCodeBench(53.7) 追平 Claude Sonnet 4、但 SWE-bench Verified 仍落后 Claude Opus(72.5)，定位为「无扩展推理下最强 open agentic coder」。

## 关键创新点

1. **MuonClip = Muon + QK-Clip 稳定化（§2.1, Algorithm 1）**
   机制：在 Muon optimizer step（含 weight decay λ=0.1、Newton-Schulz 正交化、`0.2·√max(n,m)` RMS 匹配，继承自 [[muon-is-scalable-for-llm-training]]）之后，插入一个 **QK-Clip** 后处理步骤 —— 对每个 attention head，若该 batch 的 max logit `S_max^h = (1/√d)·max_{X∈B} max_{i,j} Q_i^h K_j^{h⊤}` 超过阈值 t，则对该 head 的 query/key 投影权重做缩放。
   关键设计（§2.1）：
   - **Per-head 而非 per-layer**：`γ^h = min(1, t/S_max^h)`，只干预爆炸的少数 head，最小化对其他 head 的扰动。
   - **不改变当前 step 的 forward/backward**：QK-Clip 仅用 S_max 作为「guiding signal」决定缩放强度，作用在已更新的权重上，影响后续 step。
   - **MLA 兼容**：对 MLA 的 unshared 分量分别处理 —— qC/kC（head-specific）各乘 √γ^h；qR（head-specific rotary）乘 γ^h；kR（shared rotary）保持不动以避免跨 head 副作用。这与 QK-Norm 在 MLA 下因 Key 矩阵推理时不完全 materialize 而失效形成对比。
   - **平衡参数 α=0.5**：`W_q^h ← γ^α·W_q^h`，`W_k^h ← γ^(1-α)·W_k^h`，对 query/key 等量缩放。
   效果（§2.1，对照 **Figure 2（p.4）** 与 **Figure 3（p.5）**）：Figure 2 是 twin line plot —— 左图 vanilla Muon 的 max attention logits 单调/超线性上升，约 16k 步即超过 1000（潜在发散区）；右图 MuonClip(t=100) 全程曲线先陡升到 cap=100 的平台、约 30% 训练步后自然衰减到稳定带 ~30。M3 要点：QK-Clip 把爆炸 head「夹在阈值再自愈」，证明机制既安全又自纠正。Figure 3 是 0–16T tokens 的逐 step 原始 loss 曲线（无平滑无抽样），M3 标注曲线应从 ~2.0 平滑降到 ~1.3 全程无 spike —— 这是 15.5T tokens **zero loss spike** 的直接视觉证据，对万亿规模非平凡。
   **Self-deactivation（Appendix D，对照 Figure 12 p.30）**：前 70000 步仅 12.7% 的 head 触发过 QK-Clip；70000 步后所有 head 的 S_max 都降到 100 以下，QK-Clip 自动失效、对后续训练零影响。Figure 12 是 0.5B-activated/3B-total 小规模消融，M3 解读为两条几乎重合的 loss 轨迹（vanilla Muon vs MuonClip 激进阈值 t=30），证明即便 t=30 也无统计显著的 loss 退化 —— QK-Clip 是 safe intervention。

2. **Muon 易爆 logit 的理论解释（Appendix E）**
   机制：SVD 视角下，`|q_i·k_j| ≤ ‖x_i‖‖x_j‖‖W_q‖‖W_k‖`，RMS-Norm 使 ‖x‖ 有界，故爆炸主因是 W_q/W_k 的 spectral norm 增长。
   - Adam 更新矩阵奇异值谱倾斜（少数大奇异值主导，effective rank 低）；Muon 的 `msign` 使更新矩阵所有奇异值相等（effective rank 满）。在 16B Moonlight 上实测 Muon 权重的 SVD entropy 高于 Adam（[[muon-is-scalable-for-llm-training]] 的 §3.4）。
   - 推论：满秩更新使 singular-vector 对 `u_i v_i^⊤` 更易与更新方向 `ū_j v̄_j^⊤` 对齐，导致 W_t 对应奇异值加性增长。
   - Attention 特有放大：`q_i·k_j = (x_i W_q)·(x_j W_k)`，乘积 `W_q W_k^⊤` 对 spectral norm 取平方，任一矩阵奇异值增长都被复合放大 → Muon 更易 logit 爆炸。

3. **Token Utility 提升的 Rephrasing 数据管线（§2.2）**
   知识域：Style-/perspective-diverse prompting（受 WRAP 启发）+ chunk-wise autoregressive generation（保全局一致性，规避 LLM 输出长度限制，原文 Figure 4 示意 chunk-wise 流程，未在 M3 caption 集中）+ fidelity verification（语义对齐质量门控）。
   数学域：改写为「learning-note」风格（受 SwallowMath 启发）+ 跨语言翻译增广多样性。
   效果（§2.2 Table 1，K2 早期 checkpoint 上 SimpleQA）：raw×10 epochs = 23.76；rephrase 1 次 ×10 epochs = 27.39；rephrase 10 次 ×1 epoch = 28.94。每语料最多 rephrase 2 次。

4. **Sparsity Scaling Law for MoE-Muon（§2.3，对照 Figure 5 p.7）**
   定义 sparsity = total experts / active experts。固定激活参数（即固定 FLOPs），增加总专家数（增 sparsity）持续降低 train/val loss。Figure 5 是 log-scale scatter/line，x=Training FLOPs(10²⁰→10²¹)，y=Validation Loss(1.3→1.8)，多条彩色曲线对应不同 sparsity level，每条以「V」形收敛 dip 收尾；M3 要点：曲线随 sparsity 增大整体下移。
   量化结论：达 val loss=1.5 时，sparsity 48 相对 sparsity 8/16/32 分别省 1.69× / 1.39× / 1.15× FLOPs。K2 选 sparsity 48（384 total / 8 active）平衡性能与基础设施复杂度。

5. **Attention Heads 数量的推理成本主导设计（§2.3，原文 Figure 6）**
   DeepSeek-V3 设 attention heads ≈ 2× layers（128 heads）以利用 memory bandwidth；但 agentic 长上下文场景下 doubling heads 的推理开销陡增 —— 128k 序列、固定 384 专家下，64→128 heads 使推理 FLOPs 增 83%。
   Iso-token 实验下 doubling heads 仅带来 0.5%~1.2% val loss 改善（原文 Figure 6），边际收益不抵推理成本。K2 选 64 heads。

6. **Agentic Data Synthesis 三阶段管线（§3.1.1，对照 Figure 8 p.10）**
   - **Tool spec generation**：3000+ 真实 MCP tools（GitHub 抓取）+ 20000+ 合成 tools（hierarchical domain evolution：financial trading / software apps / robot control 等大类 → 子域 → 专门 tool）。Figure 9（t-SNE）显示真实工具按 source category 自然聚类、合成工具按预定义域覆盖互补。
   - **Agent & task generation**：数千 agents（系统 prompt × tool 组合）+ rubric-based tasks（explicit 成功标准/工具使用模式/评估检查点）。
   - **Trajectory generation**：多代理模拟（User Simulation / Tool Simulator 维持状态 + 控制随机性产生成功/部分失败/edge case）+ LLM judge 按 rubric 过滤 → 等价于大规模 rejection sampling。
   Figure 8 是双层架构图：(a) synthesizing layer —— domains + MCP tools → Tool Repository（real + synthetic）→ agents & tasks-with-rubrics；(b) trajectory layer —— User Agent 与 Agent 交互，Agent observe/call Tool Simulator，trajectory 经 rubric-informed Judge Agent 过滤为 Filtered Data。M3 要点：tool-synthesis 与多代理 simulate-and-judge 耦合闭环，使 rubric-scored 多轮 tool-calling 轨迹可大规模生成。
   **Hybrid approach**：对 coding/软件工程任务补充真实执行 sandbox（Kubernetes 驱动、10000+ 并发实例、test-suite pass rate 提供 ground-truth feedback）弥补模拟保真度不足。

7. **Self-Critique Rubric Reward —— 将对齐从 verifiable 扩展到 open-ended（§3.2.2）**
   机制：K2 actor 生成响应 → K2 critic 做 pairwise 比较，rubric 由三部分构成：core rubrics（Appendix F.1：Clarity/Relevance、Conversational Fluency、Objective & Grounded Interaction）+ prescriptive rubrics（Appendix F.2：禁 Initial Praise、禁 Explicit Justification 等 anti-reward-hacking）+ 人工标注 rubric。部分 rubric 可设为 mandatory，但 K2 保留与内部 prior 权衡的灵活性。
   **Closed-loop critic refinement**：用 verifiable-reward prompt 的 on-policy rollout 持续更新 critic，将 RLVR 的客观信号蒸馏进 critic 的主观判断；critic 随 policy 演化持续再校准，使 verifiable 任务的收益迁移到 non-verifiable 任务。
   Limitation（Appendix F.3）：rubric 偏好自信/果断回答，可能惩罚合理 hedging，对模糊/主观场景可能 overstate certainty。

8. **RL 算法与三项扩展（§3.2.3）**
   基础：继承 [[kimi-k1-5]]（K1.5）的 policy optimization，目标 `L_RL(θ) = E[ (1/K)·Σ (r(x,y_i) − r̄(x) − τ·log(π_θ/π_old))² ]`（K 个 rollout、mean reward baseline、τ 正则），用 Muon optimizer 最小化。
   三项扩展：
   - **Budget Control**：per-sample 最大 token budget（按任务类型设定），超限截断并罚分 → 抑制 RL 导致的响应膨胀（非推理域尤其受益）。
   - **PTX Loss**：精选高质量样本作为 auxiliary PTX loss（继承 InstructGPT 思路 [55]），防 joint RL 训练遗忘高质量数据、缓解对训练任务集过拟合。
   - **Temperature Decay**：初期高温探索（创意/复杂推理），后期降温利用 → 平衡探索与收敛稳定性。

9. **Colocated RL 架构 + 分布式 Checkpoint Engine（§3.3）**
   - 沿用 K1.5 的 hybrid colocated 架构：训练/推理引擎同 worker，一方工作时另一方 offload GPU。
   - **Efficient Engine Switching（§3.3.2，对照 Figure 10 p.14）**：1T 模型下用网络文件系统 resharding 不可行（需 PB/s 级带宽）。Figure 10 是三层参数更新 pipeline：(1) Training Engine（DRAM 持权重）每 worker 贡献本地 shard；(2) Distributed Checkpoint Engine co-located 在训练节点，取本地副本后全集群广播全参数；(3) Inference Engine 按自身 sharding 只取所需 shard。M3 要点：广播「全参数」而非「按需传输」—— 数据量虽几倍于理论最优，但训练/推理引擎完全解耦、系统简单，实测因同步开销低 + 网络带宽利用率高反而更快 —— **完整参数更新 < 30 秒**（典型 RL 迭代中可忽略）。
   - **Efficient System Startup（§3.3.3）**：训练 worker 选择性读盘并 peer-broadcast（全集群只读一次 checkpoint）；推理副本复用 checkpoint engine 启动，避免副本间同步 barrier，对单点失败鲁棒。
   - **Agentic Rollout（§3.3.4）**：环境阻塞（VM/code interpreter 等待反馈）致 GPU idle → 两策略 (i) 重环境部署为可扩展 dedicated service (ii) 大量并发 rollout 摊销延迟；长尾轨迹用 **partial rollout**（K1.5）暂停并下轮恢复。
   - **RL 权重更新 pipeline（§3.3，Appendix，对照 Figure 13 p.32）**：Figure 13 给出三变体 (a)(b)(c) —— 每 GPU 持一个 H2D buffer + 两个 IPC buffer（与推理引擎 memory-map 共享）。(a) 理论 3-stage 流水：async H2D → copy 到 IPC + broadcast → 推理 reload；(b) H800 集群 PCIe 带宽受限，H2D 与 broadcast 并发会 saturate 共享 PCIe，三段塌缩成顺序；(c) 实际采用 fixed 2-stage：同步全设备 H2D → broadcast 与 reload 并行。M3 要点：大规模下参数集单次 H2D 即可装入，更简单的 2-stage 流水反成 PCIe-friendly 最优解。
   源码开源：https://github.com/MoonshotAI/checkpoint-engine

10. **并行调度：1F1B + 解耦 WGrad + EP=16 重叠（§2.4，对照 Figure 7 p.8）**
    Figure 7 是 timeline 图，三 track（Computation / Communication / Offload）分三 PP 阶段：Phase 1 warm-up（Attn+MLP 与 EP-D/EP-C comm 重叠，activation offload 到 CPU）；Phase 2 steady-state 1F1B（Attn→MLP→MLP→Attn→WGrad，EP comm 与 weight-grad 计算与 PP traffic 三方重叠，offload/onload 仅在 phase 边界）；Phase 3 cooldown（剩余 backward：MLP→Attn→WGrad）。M3 要点：三正交操作重叠使硬件近满利用 —— EP all-to-all 用 EP=16 小组隐藏在 attention/MLP compute 下、PP p2p 与解耦的 WGrad 重叠、optimizer-state offload 仅在 PP 边界。唯一 unscheduled 是 warm-up。该设计使单一并行配置可跨节点数 scale 无需 retune，是「研究效率（小规模）与训练效率（大规模）共享配置」目标的工程兑现。

11. **工具调用 Token 模板（Appendix B）**
    三组件：tool_declare（TypeScript 表达，比 OpenAI JSON 简洁得多，部分训练数据也用 JSON 保兼容）/ tool invoking section（`<|tool_call_section_begin|>` + 每个 call 唯一 id `functions.{tool-name}:{counter}`，支持并行多调用）/ tool result message。
    推理时用受 lm-format-enforcer 启发的 **enforcer** 约束解码模块，在 `<|tool_call_section_begin|>` 后强制 tool token 与 JSON args 遵循声明 schema。

## 表格（原文结构化）

**Table 1（§2.2）—— Rephrasing-Epoch 配置下 SimpleQA Accuracy**

| # Rephrasings | # Epochs | SimpleQA Accuracy |
|---|---|---|
| 0 (raw wiki-text) | 10 | 23.76 |
| 1 | 10 | 27.39 |
| 10 | 1 | 28.94 |

**Table 2（§2.3）—— Kimi K2 vs DeepSeek-V3 架构对比**

| 项 | DeepSeek-V3 | Kimi K2 | 变化 |
|---|---|---|---|
| #Layers | 61 | 61 | = |
| Total Parameters | 671B | 1.04T | +54% |
| Activated Parameters | 37B | 32.6B | −13% |
| Experts (total) | 256 | 384 | +50% |
| Experts Active per Token | 8 | 8 | = |
| Shared Experts | 1 | 1 | = |
| Attention Heads | 128 | 64 | −50% |
| Number of Dense Layers | 3 | 1 | −67% |
| Expert Grouping | Yes | No | — |

（hidden dim 7168，MoE expert hidden dim 2048，MLA attention，sparsity 48）

**Table 3（§4.1.2）—— Kimi-K2-Instruct 后训练评测（节选关键 benchmark，non-thinking mode）**

| Benchmark | Kimi-K2-Instruct | DeepSeek-V3-0324 | Qwen3-235B-A22B | Claude Sonnet 4 | Claude Opus 4 | GPT-4.1 | Gemini 2.5 Flash |
|---|---|---|---|---|---|---|---|
| LiveCodeBench v6 (Pass@1) | **53.7** | 46.9 | 37.0 | 48.5 | 47.4 | 44.7 | 44.7 |
| OJBench (Pass@1) | **27.1** | 24.0 | 11.3 | 15.3 | 19.6 | 19.5 | 19.5 |
| MultiPL-E (Pass@1) | 85.7 | 83.1 | 78.2 | 88.6 | **89.6** | 86.7 | 85.6 |
| SWE-bench Verified Agentless-Single-Patch | 51.8 | 36.6 | 39.4 | 50.2 | **53.0** | 40.8 | 32.6 |
| SWE-bench Verified Agentic-Single-Attempt | 65.8 | 38.8 | 34.4 | 72.7* | **72.5*** | 54.6 | — |
| SWE-bench Verified Agentic-Multi-Attempt | 71.6 | — | — | **80.2*** | 79.4* | — | — |
| SWE-bench Multilingual (Pass@1) | 47.3 | 25.8 | 20.9 | **51.0** | — | 31.5 | — |
| Multi-SWE-bench (Pass@1) | 18.3 | 8.0 | 9.0 | **29.2** | — | 11.7 | 14.0 |
| SWE-Lancer (Pass@1) | 39.1 | 30.5 | 24.1 | **40.8** | — | 23.0 | 38.5 |
| PaperBench Code-Dev | 27.8 | 12.2 | 13.2 | **43.3** | — | 29.9 | 5.7 |
| Terminal Bench In-House | 30.0 | — | — | 35.5 | **43.2** | 8.3 | — |
| Terminal Bench Terminus | 25.0 | 16.3 | 6.6 | — | — | **30.3** | 16.8 |
| Aider-Polyglot | 60.0 | 55.1 | 61.8 | 56.4 | **70.7** | 52.4 | 44.0 |
| Tau2 retail (Avg@4) | 70.6 | 69.1 | 57.0 | 75.0 | **81.8** | 74.8 | 64.3 |
| Tau2 airline (Avg@4) | 56.5 | 39.0 | 26.5 | 55.5 | **60.0** | 54.5 | 42.5 |
| Tau2 telecom (Avg@4) | **65.8** | 32.5 | 22.1 | 45.2 | 57.0 | 38.6 | 16.9 |
| AceBench (Acc.) | 76.5 | 72.7 | 70.5 | 76.2 | 75.6 | **80.1** | 74.5 |
| AIME 2024 (Avg@64) | **69.6** | 59.4* | 40.1* | 43.4 | 48.2 | 46.5 | 61.3 |
| AIME 2025 (Avg@64) | **49.5** | 46.7 | 24.7* | 33.1* | 33.9* | 37.0 | 46.6 |
| MATH-500 (Acc.) | **97.4** | 94.0* | 91.2* | 94.0 | 94.4 | 92.4 | 95.4 |
| HMMT 2025 (Avg@32) | **38.8** | 27.5 | 11.9 | 15.9 | 15.9 | 19.4 | 34.7 |
| CNMO 2024 (Avg@16) | 74.3 | 74.7 | 48.6 | 60.4 | 57.6 | 56.6 | **75.0** |
| PolyMath-en (Avg@4) | **65.1** | 59.5 | 51.9 | 52.8 | 49.8 | 54.0 | 49.9 |
| ZebraLogic (Acc.) | **89.0** | 84.0 | 37.7* | 79.7 | 59.3 | 58.5 | 57.9 |
| AutoLogi (Acc.) | 89.5 | 88.9 | 83.3* | **89.8** | 86.1 | 88.2 | 84.1 |
| GPQA-Diamond (Avg@8) | **75.1** | 68.4* | 62.9* | 70.0* | 74.9* | 66.3 | 68.2 |
| SuperGPQA (Acc.) | **57.2** | 53.7 | 50.2 | 55.7 | 56.5 | 50.8 | 49.6 |
| Humanity's Last Exam (Acc.) | 4.7 | 5.2 | 5.7 | 5.8 | **7.1** | 3.7 | 5.6 |
| MMLU (EM) | 89.5 | 89.4 | 87.0 | 91.5 | **92.9** | 90.4 | 90.1 |
| MMLU-Redux (EM) | 92.7 | 90.5 | 89.2* | 93.6 | **94.2** | 92.4 | 90.6 |
| MMLU-Pro (EM) | 81.1 | 81.2* | 77.3 | 83.7 | **86.6** | 81.8 | 79.4 |
| IFEval (Prompt Strict) | **89.8** | 81.1 | 83.2* | 87.6 | 87.4 | 88.0 | 84.3 |
| Multi-Challenge (Acc.) | **54.1** | 31.4 | 34.0 | 46.8 | 49.0 | 36.4 | 39.5 |
| SimpleQA (Correct) | 31.0 | 27.7 | 13.2 | 15.9 | 22.8 | **42.3** | 23.3 |
| Livebench (Pass@1) | **76.4** | 72.4 | 67.6 | 74.8 | 74.6 | 69.8 | 67.8 |
| Arena Hard v2.0 Hard Prompt | 54.5 | 39.9 | 39.9 | 51.6 | **59.7** | 51.7 | 48.7 |
| Arena Hard v2.0 Creative Writing | **85.0** | 59.3 | 59.8 | 54.6 | 68.5 | 61.5 | 72.8 |
| FACTS Grounding (Adjusted) | **88.5** | 68.3 | 68.5 | 83.6 | — | 79.2 | 86.6 |
| HHEM v2.1 (1−Hallu.) | **98.9** | 88.9 | 94.5 | 94.5 | — | 96.7 | 97.8 |
| FaithJudge (1−Hallu.) | 92.6 | 83.4 | 75.7 | 83.0 | — | 91.0 | **93.2** |
| LongBench v2 (Acc.) | 49.1 | 51.1 | — | 52.5 | — | 54.3 | **55.5** |
| FRAMES (Acc.) | 77.1 | **79.2** | — | 76.3 | — | 87.4 | 72.9 |
| MRCR (Acc.) | 55.0 | 50.8 | — | 74.4 | — | 66.9 | **81.7** |
| DROP (Acc.) | **93.5** | 91.2 | 84.3 | 92.0 | — | 79.1 | 81.7 |

LMSYS Arena（2025-07-17）：开源第 1、总榜第 5（超 3000 用户盲投）。
中文 in-house 评测见 **Figure 11（p.29）**：K2-Instruct 对 ChatGPT-4o-latest win-rate ~65.4%、对 Claude Sonnet 4 ~64.6%、对 DeepSeek-V3-0324 ~59.6%，loss-rate 三组均 ~17% 均匀低 —— M3 要点：高 win-rate + 均匀低 loss-rate（很少 outright 输/平）说明中文性能是 held-out contamination-controlled 集上的真实泛化，而非 benchmark overfit。

**Table 4（§4.2.2）—— Kimi-K2-Base 预训练 base 模型对比（节选）**

| Benchmark | Kimi-K2-Base | DeepSeek-V3-Base | Llama4-Maverick-Base | Qwen2.5-72B-Base |
|---|---|---|---|---|
| # Activated Params | 32B | 37B | 17B | 72B (dense) |
| # Total Params | 1043B | 671B | 400B | 72B |
| MMLU | **87.79** | 87.10 | 84.87 | 86.08 |
| MMLU-pro | **69.17** | 60.59 | 63.47 | 62.80 |
| SuperGPQA | **44.67** | 39.20 | 38.84 | 34.23 |
| GPQA-Diamond (avg@8) | 48.11 | **50.51** | 49.43 | 40.78 |
| SimpleQA | **35.25** | 26.49 | 23.74 | 10.31 |
| CRUXEval-I-cot | **74.00** | 62.75 | 67.13 | 61.12 |
| CRUXEval-O-cot | **83.50** | 75.25 | 75.88 | 66.13 |
| LiveCodeBench(v6) | **26.29** | 24.57 | 25.14 | 22.29 |
| EvalPlus | **80.33** | 65.61 | 65.48 | 66.04 |
| MATH | **70.22** | 61.70 | 63.02 | 62.68 |
| GSM8k | **92.12** | 91.66 | 86.35 | 90.37 |
| GSM8k-platinum | **94.21** | 93.38 | 88.83 | 92.47 |
| CMATH | 90.26 | **90.53** | 88.07 | 86.98 |
| C-Eval | **92.50** | 90.04 | 80.91 | 90.86 |
| CMMLU | **90.90** | 88.84 | 81.24 | 90.55 |
| CSimpleQA | **77.57** | 72.13 | 53.47 | 50.53 |

（base 模型在 12 个英文 benchmark 中 SOTA 10 个；coding/math/Chinese 全面领先）

**Table 5（§4.3.1）—— Safety 评估 Plugins & Strategies**

| Plugin 类 | 子项 |
|---|---|
| Harmful | Graphic Content, Harassment, Hate Speech, Insults, Profanity, Radicalization, Self Harm, Sexual Content, ToxicChat |
| Criminal | Chemical&Biological Weapons, Child Exploitation, Copyright Violations, Cybercrime, Illegal Activities, Illegal Drugs, Indiscriminate Weapons, IP Violation, Non-Violent Crime, Violent Crime, Sex Crimes |
| Misinformation | Competitor Endorsement, Excessive Agency, Hallucination, Misinformation/Disinformation, Specialized Advice, Unsafe Practices, Imitation, Overreliance, Political Opinions, Religious Sensitivity |
| Privacy | Privacy Violation, PII in API/Database, Direct PII Exposure, PII in Session Data, PII via Social Engineering |
| Security | ASCII Smuggling, CyberSecEval, Harmbench, Debug Access, Divergent Repetition, DoNotAnswer, Malicious Code, Pliny, Prompt Extraction, Reasoning DoS, Tool Discovery |
| Strategy | Basic, Prompt Injection, Iterative Jailbreak, Crescendo |

（每 plugin×strategy 生成 3 prompt；双语组合生成 6 prompt；人工多轮复核）

**Table 6（§4.3.2）—— Safety 评估通过率（节选关键，%为 passing rate 越高越安全）**

| Plugin | Strategy | Kimi-K2 | DeepSeek-V3-0324 | DeepSeek-R1 | Qwen3-235B-A22B |
|---|---|---|---|---|---|
| Harmful | Basic | 98.04 | 90.45 | 99.02 | 98.53 |
| Harmful | Base64 | 100 | 90.20 | 100 | 100 |
| Harmful | Prompt Injection | 93.14 | 100 | 95.10 | 99.02 |
| Harmful | Iterative Jailbreak | 92.16 | 66.67 | 72.55 | 74.51 |
| Harmful | Crescendo | 64.71 | 64.71 | 80.39 | 86.27 |
| Criminal | Basic | 100 | 99.62 | 95.45 | 99.24 |
| Criminal | Iterative Jailbreak | 57.57 | 21.21 | 25.76 | 53.03 |

## 与同类对比

- **vs DeepSeek-V3（[[deepseek-v3-technical-report]]）**：架构直接对标（Table 2）。K2 用更少激活参（32.6B vs 37B，−13%）+ 更多总参（1.04T vs 671B，+54%）实现更高 sparsity（48 vs 32），同 FLOPs 下 val loss 更低（Figure 5）。关键改造：heads 减半（64 vs 128）换 agentic 长上下文推理效率、放弃 DualPipe 与 expert grouping、dense layer 从 3 减到 1。后训练 K2 在 agentic/coding/math/中文全面超 V3-0324（Tau2 telecom 65.8 vs 32.5、SWE-bench Verified 65.8 vs 38.8、AIME 2025 49.5 vs 46.7、MMLU-Pro 81.1 vs 81.2 持平），但长上下文检索 LongBench v2/FRAMES/MRCR 落后 V3（与 heads 减半取舍直接相关）。
- **vs Claude Opus 4 / Sonnet 4（闭源 SOTA）**：在非思维设定下，agentic coding（SWE-bench Verified 65.8 vs Opus 72.5、SWE-bench Multilingual 47.3 vs Sonnet 51.0）仍落后，但差距远小于其他开源模型；数学 AIME 2025(49.5) / MATH-500(97.4) / HMMT 2025(38.8) / GPQA-Diamond(75.1) / SuperGPQA(57.2) 均超 Claude Opus 4 与 Sonnet 4；中文 Arena Hard Creative Writing(85.0) 大幅领先 Opus(68.5)/Sonnet(54.6)。事实性 SimpleQA(31.0) 落后 GPT-4.1(42.3)，HLE(4.7) 落后 Opus(7.1)。
- **vs Qwen3-235B-A22B**：同属开源 MoE，K2 在几乎所有非思维 benchmark 上领先（Tau2 telecom 65.8 vs 22.1、SWE-bench Multilingual 47.3 vs 20.9、AIME 2025 49.5 vs 24.7、ZebraLogic 89.0 vs 37.7）；唯一弱项是 safety 的 Harmful-Crescendo（64.71 vs 86.27）与 Criminal-Iterative Jailbreak（57.57 vs 53.03 略胜）。
- **vs GPT-4.1**：agentic/tool-use 互有胜负（Tau2 telecom 65.8 vs 38.6、AceBench 76.5 vs 80.1），事实性 SimpleQA 落后（31.0 vs 42.3），长上下文 MRCR 落后（55.0 vs 66.9）。
- **MuonClip vs 其他稳定化**：相对 logit soft-cap（cap 前点积仍可爆炸）与 QK-Norm（MLA 下 Key 矩阵推理时不完全 materialize 故失效），QK-Clip 是首个对 MLA 兼容、per-head、且能 self-deactivate 的方案。

## 跨论文关系（→ MOC 谱系）

- **[[muon-is-scalable-for-llm-training]]（Moonlight）**：K2 的 MuonClip 直接建立在 Moonlight 的 Muon-with-WD + consistent RMS matching 之上（Algorithm 1 的 step 1 即 Moonlight 的 Muon）；Appendix E 的 SVD-entropy/Moonlight 实测、logit 爆炸观察继承自 Moonlight §3.4 的稳定性发现。K2 把 Muon 从 16B scale 到 1T。
- **[[deepseek-v3-technical-report]]**：K2 架构（MLA + ultra-sparse MoE + DeepSeek-V3 风格）的直接对标与改造对象 —— 增加 experts 到 384、减半 heads 到 64、放弃 DualPipe 与 expert grouping、用 interleaved 1F1B + 解耦 weight-grad + 最小 EP=16。
- **[[kimi-k1-5]]**：RL 算法、colocated 架构、partial rollout 全部继承自 K1.5；self-critique 框架与 K1.5 的 mirror descent 一脉相承。
- **[[kimi-vl-technical-report]]**：同属 Moonshot RL 框架的 agentic line；Kimi-VL 的 long-thinking 继承 K1.5 mirror descent，K2 则走 non-thinking agentic 路线，二者在 K2.5 汇合。
- **[[kimi-k2-5-visual-agentic-intelligence]]（K2.5）**：K2 的视觉 agentic 后继 —— 继承 K2 的 agentic 数据合成与 self-critique RL 框架，扩展到多模态/视觉 agentic 场景。K2 是 K2.5 的文本 agentic 基座与直接前驱。
- **[[kimi-k3-open-frontier-intelligence]]（K3）**：K2 的下一代 frontier 模型 —— K3 在 K2 的 MuonClip + agentic 框架基础上继续推进 open frontier intelligence。K2 的开放权重策略与 agentic intelligence 定位由 K3 延续。
- **[[kimi-linear-an-expressive-efficient-attention-architecture]]**：Moonshot efficient-attention line —— 与 K2 的 MLA + 64-head 长上下文推理效率优化属于同一研究脉络（在长上下文下降低 attention 开销）。
- **[[cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation]]** + **[[search-r1]]** + **[[single-rollout]]** + **[[beyond-ten-turns]]**：agentic RL 家族 —— K2 的 self-critique rubric + verifiable-reward Gym + agentic rollout（partial rollout / 大量并发 / dedicated env service）与这些工作共享大规模 agentic RL 的工程范式（长 horizon、环境交互、并发摊销、rollout 异步化）。
- **[[hybridflow-a-flexible-and-efficient-rlhf-framework]]**：K2 的 colocated RL 架构（训练/推理引擎同 worker 切换）与 HybridFlow 的统一 RLHF 编排属同类思路 —— K2 通过 distributed checkpoint engine 实现毫秒级引擎切换（<30s 全参数更新），是对 colocated 范式在 1T 模型规模下的工程极致化。

K2 在 MOC 谱系中的定位：**open-agentic model anchor** —— 以 MuonClip（继承 Muon）+ DeepSeek-V3 改造架构（继承 DeepSeek-V3）+ K1.5 RL 框架（继承 K1.5）三者交汇，作为 Moonshot agentic line 的文本基座，向上衍生 K2.5（视觉）/ K3（frontier），横向连接 efficient-attention（Kimi-Linear）与 agentic RL 家族。

## 局限与边界

1. **作者自陈（§5）**：(a) 硬推理任务或工具定义不清时，模型可能产生过多 token，导致输出截断或工具调用不完整；(b) 不必要地启用 tool use 反而可能降低某些任务表现；(c) 构建完整软件项目时，one-shot prompting 成功率不如在 agentic coding framework 下使用 K2。
2. **Self-critique rubric 的过度自信偏差（Appendix F.3）**：prescriptive rubric 禁止 self-qualification/hedging、偏好 clarity & singularity，导致模型在模糊/主观场景下可能 overstate certainty，抑制合理的 epistemic humility 与多视角回答。作者承认未来需引入 calibrated uncertainty 的细粒度处理。
3. **Rephrasing 合成数据的开放问题（§2.2）**：合成数据作为持续 scaling 的策略仍在研究中 —— 跨源域泛化保真度、hallucination 与 unintended toxicity 控制、大规模数据集可扩展性是关键挑战。
4. **Safety 评估的局限（§4.3.2）**：(a) 人工复核引入主观性；(b) 涉及 API misuse / external tool invocation 的 plugin 更适合评估带 tool-calling 的 agent 模型，对 base LLM 相关性有限；(c) K2 未对评估场景做定向优化，Harmful–Iterative Jailbreak（92.16）、Criminal–Iterative Jailbreak（57.57）/ Crescendo（56.06）等复杂场景通过率相对 Qwen3 偏低；(d) 复杂攻击策略并不总是优于 basic（多轮变换可能稀释原意）。
5. **长上下文检索/推理的弱项**：LongBench v2（49.1，落后 DeepSeek-V3 51.1 与 Gemini 55.5）、FRAMES（77.1，落后 DeepSeek 79.2 与 GPT-4.1 87.4）、MRCR（55.0，落后 Gemini 81.7 与 Claude Sonnet 4 74.4）—— 与为 agentic 长上下文专门优化 attention heads 数量（减半到 64）的设计取舍直接相关，长上下文检索是结构性弱项。
6. **事实性短板**：SimpleQA（31.0）虽领先开源但仍显著落后 GPT-4.1（42.3）；HLE（4.7）落后 Claude Opus 4（7.1）—— 知识边界相对闭源 SOTA 仍有差距。
7. **QK-Clip 仅适用于 attention logits**：QK-Clip 是针对 attention logits 爆炸的定向方案，不解决 Muon 在其他算子可能出现的稳定性问题；其 MLA 兼容设计依赖 unshared/shared 分量的区分，迁移到其他 attention 变体需重新设计分量映射。
8. **Tool calling 格式的工程依赖**：推理时需 enforcer 约束解码以保证 tool token 与 JSON args 遵循 schema —— 模型本身仍可能生成 unexpected token，鲁棒性依赖后处理模块而非模型内生。
