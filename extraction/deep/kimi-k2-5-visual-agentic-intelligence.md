# Kimi K2.5 — 技术点深读（DEEP 2026-08-18，公式重跑）

> Moonshot AI 技术报告（arXiv:2602.02276v1, 2026-02-02）。Kimi K2.5 是在 [[kimi-k2-open-agentic-intelligence]] 基础上构建的 native multimodal agentic model，两大主线：(1) 文本-视觉**联合优化**（joint pre-training + zero-vision SFT + joint multimodal RL），(2) **Agent Swarm**——基于 Parallel-Agent Reinforcement Learning (PARL) 的并行 agent 编排框架。开源 post-trained checkpoint。下方公式以 `extraction/formulas.json` 的 LaTeX 为权威源（5 条，全文 Eq.1/2 + r_PARL + CriticalSteps + Toggle 分相 reward），与 M3 caption 对架构/曲线图的解读做双源校验。

---

## 核心问题

K2.5 攻击两个相互独立但都关涉"agentic intelligence 规模化"的瓶颈：

1. **多模态训练的模态冲突与冷启动问题（§1, §2）**。传统 vision-adapted VLM 在文本 backbone 训练**后期**才注入视觉 token（late-fusion，vision ratio ≥50%），导致：(a) text 能力在 vision 注入瞬间出现"dip-and-recover"退化（§B.1，模态 domain shift 冲击已建立的 linguistic 表征空间）；(b) post-training 阶段 pretrained VLM 不会自然执行 vision-based tool-calling（cold-start），而人工/模板 CoT 数据多样性差，仅限于 crop/rotate/flip 等原语（§2.2）。问题是：**在固定 vision-text token 预算下，是否存在一种联合训练策略使两模态互不削弱反而互相增强？** K2.5 用 Table 1 的 ablation 给出反直觉答案——early fusion + lower ratio 更优。

2. **sequential agent execution 的线性延迟扩展（§1, §3）**。即使如 [[kimi-k2-open-agentic-intelligence]] Thinking 这样可执行数百步 reasoning 的系统，推理时间仍随任务复杂度**线性**增长，导致 wide-search / deep-search 类任务在固定 reasoning-step 与 tool-call 预算内无法完成。问题是：**如何让模型学会"何时、如何并行"——而非依赖预定义并行启发式——同时避免端到端多智能体共优化中的 credit assignment ambiguity 与 training instability？**

---

## 关键创新点

### 1. Native Multimodal Pre-Training：early-fusion + constant ratio（§2.1, §B.1, Table 1, Figure 9）
- **机制**：在固定 vision-text 总 token 预算下，对比三组（Early/0% 起步、Mid/50% 起步、Late/80% 起步；vision-text ratio 分别 10:90 / 20:80 / 50:50）。所谓"早融合"指从训练一开始就以恒定比例混入 vision token，而非把 vision 当作后期 add-on。
- **效果**：Table 1 显示 early fusion (10:90) 在全部 6 项指标上最优——Vision Knowledge 25.8 vs late 24.2、Vision Reasoning 43.8 vs 39.0、OCR 65.7 vs 61.5、Text Knowledge 45.5 vs 43.1、Text Reasoning 58.5 vs 57.8、Code 24.8 vs 24.0。§B.1 解释：late/mid fusion 引入 vision 时出现"dip-and-recover"文本退化，early fusion 维持更健康的 text 曲线、gradient landscape 更平滑。结论：vision ratio 对最终性能影响"minimal"，**关键是早融合**——颠覆了"vision 应在后期高比例注入"的传统 [8, 21]。
- **LaTeX↔M3 双源校验**：M3 对 Figure 9 的解读（"10:90 / 20:80 更优收敛、50:50 出现 dip-and-recover、text capability degrades mid-training before recovering，指示 modality domain shift"）与 §B.1 文本论证、Table 1 数值三向一致。

### 2. Zero-Vision SFT：纯文本 SFT 激活视觉 agentic 能力（§2.2, Figure 2）
- **机制**：post-training SFT 阶段**只用文本数据**，所有图像操作以 IPython 程序化操作代理（binarization、counting、object localization、OCR 等 pixel-level 操作），即把 vision tool-use 泛化为代码执行。不引入人工设计的 visual trajectory。
- **效果**：§2.2 明示——加入人设 visual trajectory 反而**损害泛化**；text-only SFT 表现更好，因为 §2.1 的 joint pre-training 已建立强 vision-text 对齐，能力可跨模态自然迁移。zero-vision SFT 作为 RL 起点（Figure 2）即可让 visual RL 曲线持续上升，证明"zero-vision 激活 + 长 RL"足以获得稳健视觉能力。
- **LaTeX↔M3 双源校验**：M3 对 Figure 2 的解读（"MMMU Pro 从 ~0.71 升至 ~0.76，右图 benchmark 从 ~0.68 升至 ~0.78；RL FLOPs 而非 vision pre-training 是稳健视觉能力的关键驱动"）与 §2.2 "zero-vision activation paired with long-running RL is sufficient" 文本完全吻合。

### 3. Joint Multimodal RL 与 cross-modal transfer（§2.3, Table 2）
- **机制**：outcome-based visual RL 在三类任务上施加——visual grounding/counting、chart/document understanding、vision-critical STEM。RL 域**不按输入模态**而**按能力**（knowledge / reasoning / coding / agentic）划分，GRM（Generative Reward Model）跨异构轨迹无模态壁垒地优化，确保任一模态获得的能力可迁移到另一模态。
- **效果**：Table 2——视觉 RL 之后**纯文本 benchmark 反而提升**：MMLU-Pro 84.7→86.4 (+1.7)、GPQA-Diamond 84.3→86.4 (+2.1)、LongBench v2 56.7→58.9 (+2.2)。§2.3 归因：visual RL 增强了结构化信息抽取区域的 calibration，减少"resemble visually grounded reasoning"类查询的不确定性。这是"text bootstraps vision, vision refines text"的双向增强证据。

### 4. MoonViT-3D：图像/视频共享嵌入空间 + 4× temporal compression（§4.2）
- **机制**：在 [[kimi-vl-technical-report]] 的 MoonViT（SigLIP-SO-400M 初始化 + NaViT patch-n'-pack）基础上推广到时间维——最多 4 帧组成 spatiotemporal volume，2D patches 联合 flatten 成 1D 序列，**同一 attention 机制**跨时空运作；参数与 image encoder 完全共享。MLP projector 前做 lightweight temporal pooling，patch 级时间平均，实现 **4× temporal compression**。
- **效果**：相同 context window 下可处理 4× 长视频；§5.1.2 报告长视频 SOTA——LVBench 75.9、LongVideoBench 79.8（喂入 >2000 帧）、MotionBench 70.4（高速运动/视觉效果），无需专门 video module 或架构分叉。§4.2 强调 image→video 知识迁移通过"一个共享参数空间 + 一种特征表示"整体完成。

### 5. Agent Swarm + PARL：解耦编排 + frozen subagent（§3, Table 6, Figure 3/4/8）
- **机制**：PARL 架构——trainable **orchestrator** + 从固定中间 policy checkpoint 实例化的 **frozen subagent**。subagent 输出当作"environment observations"而非可微决策点，**绕开** end-to-end 共优化的 credit assignment ambiguity 与 training instability。先训小 subagent 再切换大模型，支持动态调整 subagent/orchestrator 推理实例比。
- **PARL reward**（§3，formulas.json 权威 LaTeX）：

$$
r_{\mathrm{PARL}}(x, y) = \lambda_1 \cdot \mspace{-26mu} \underbrace{r_{\text{parallel}}}_{\text{instantiation reward}} \mspace{-9mu} + \mspace{18mu}\lambda_2 \cdot \mspace{-32mu}\underbrace{r_{\text{finish}}}_{\text{sub-agent finish rate}} + \underbrace{r_{\text{perf}}(x, y)}_{\text{task-level outcome}} \, .
$$

  机制：`r_parallel`（instantiation reward）抑制 **serial collapse**（orchestrator 退化为单 agent 的局部最优）；`r_finish`（sub-agent finish rate）抑制 **spurious parallelism**（reward hacking——滥生 subagent 但无有效分解）；`r_perf` 为 task-level outcome。λ1、λ2 在训练中 anneal 到 0，保证最终策略优化主目标。
- **Critical steps 约束**（§3，formulas.json 权威 LaTeX）：

$$
\text{CriticalSteps} = \sum_{t=1}^{T} \left( S_{\mathrm{main}}^{(t)} + \max_i S_{\mathrm{sub}, i}^{(t)} \right).
$$

  机制：以并行组中最长 subagent 为该 stage 时长，类比计算图 critical path。用 critical steps 而非 total steps 作为训练/评估约束，显式激励"缩短最长并行分支"的均衡分解。
- **效果**：Table 6——BrowseComp 60.6→78.4 (+17.8 abs，超过 GPT-5.2 Pro 77.9)、WideSearch 72.7→79.0 (+6.3，超 Claude Opus 4.5 76.2)、In-house Swarm Bench 41.6→58.3 (+16.7)。
- **LaTeX↔M3 双源校验**：(a) Figure 3（M3："centralized Orchestrator (trainable) + frozen subagents (AI/Physics/Life Sciences Researcher, Fact Checker, Web Developer)；orchestrator dynamically creates specialized frozen subagents"）与 §3 decoupled architecture 文本一致——trainable/frozen 边界双源确认。(b) Figure 4（M3："training accuracy 与 parallelism 同步上升，parallelism 是 training-induced emergent property 而非固定超参"）与 §3 "parallelism is explicitly learned through environmental feedback and RL-driven exploration" 文本一致——印证 orchestrator 通过 reward shaping 学会并行，而非显式指令。(c) Figure 8（M3："Agent Swarm 在 WideSearch 上目标 Item-F1 从 30%→70% 时 3×–4.5× 延迟降低，speedup 随任务复杂度扩大"）与 §5.2 "single agent 1.8×→>7.0×、Swarm 维持 0.6×–1.6×" 数值一致——critical steps 约束的端到端延迟收益被 M3 曲线佐证。

### 6. Togle：交替 token-efficient RL（§4.4.2, Figure 5）
- **机制**：解决 length-overfitting（rigid budget 下模型无法泛化到更高 compute scale，默认截断 reasoning）。每 m 次迭代交替两相（formulas.json 权威 LaTeX，分相 reward）：

$$
\tilde{r}(x,y) = \begin{cases} r(x, y) \cdot \mathbb{I}\left\{ \frac{1}{K} \sum_{i=1}^K r(x, y_i) < \lambda\ \mathrm{or}\ |y_i| \leq \mathrm{budget(x)} \right\} & \text{if } \lfloor t/m \rfloor \pmod 2 = 0\ (\mathrm{{Phase 0}}) \\ r(x, y) & \text{if } \lfloor t/m \rfloor \pmod 2 = 1\ (\mathrm{{Phase 1}}) \end{cases} \, .
$$

  其中 Phase0（budget limited）仅在 batch 平均准确率低于阈值 λ 或长度超 budget 时强制约束（避免过早牺牲质量换效率）；Phase1（standard scaling）使用原始 reward，鼓励利用 compute 做 test-time scaling。问题相关预算（formulas.json 权威 LaTeX，对应原文 Eq.2）：

$$
\mathrm{budget}(x) = \text{Percentile}\left(\{ |y_j| \mid r(x, y_i) = 1, i=1,\dots, K \}, \rho \right) \, .
$$

  机制：budget 取自正确响应 token 长度的 ρ-th percentile，训练前估一次固定。
- **效果**：在 [[kimi-k2-open-agentic-intelligence]] Thinking 上评测——output token 平均减少 **25%–30%**，性能 negligible 影响；CoT 中重复 verification / 机械计算等冗余模式大幅减少；且具强 domain generalization（仅在数学+编程训练，GPQA/MMLU-Pro 仍持续降 token）。
- **LaTeX↔M3 双源校验**：Figure 5（M3："Before/After Toggle 双面板，Performance(%) 与 Token Usage 对比，toggling preserves/slightly improves benchmark performance while substantially reducing token usage"）与 §4.4.2 "25∼30% token 减少 + negligible 性能影响" 文本一致。

### 7. Decoupled Encoder Process (DEP)：视觉编码器与 backbone 解耦并行（§4.5.1）
- **机制**：利用 vision encoder 在计算图中的拓扑位置（forward 起点 / backward 终点），三阶段：(a) Balanced Vision Forward——vision encoder 小，全 GPU 复制，按 image/patch count 均匀切分前向，丢弃所有中间 activation 只留最终输出，回传 PP Stage-0；(b) Backbone Training——因前阶段丢弃中间激活，可纯文本训练验证的高效并行策略直接复用；(c) Vision Recomputation & Backward——重算前向再反向。
- **效果**：K2.5 无缝继承 K2 并行策略，**多模态训练效率达纯文本训练的 90%**。彻底解决 Stage-0 因 image count/resolution 波动导致的 load imbalance（[54] 手调 text decoder 层数的妥协方案的根本替代）。注：LongCat-Flash-Omni [55] 有相似设计哲学的并发工作。

### 8. Token-level clipping RL 目标（§4.4.2, 原文 Eq.1，formulas.json 权威 LaTeX）

$$
L_{\mathrm{RL}}(\theta) = \mathbb{E}_{x \sim\mathcal{D}} \left[ \frac{1}{N} \sum_{j=1}^K \sum_{i=1}^{|y_j|} \mathrm{Clip} \left( \frac{\pi_{\theta}(y_j^i | x, y_j^{0:i})}{\pi_{\mathrm{old}}(y_j^i | x, y_j^{0:i}) }, \alpha, \beta \right) ({r}(x, y_j) - \bar{r}(x))- \tau \left( \log \frac{\pi_{\theta}(y_j^i | x, y_j^{0:i})}{\pi_{\mathrm{old}}(y_j^i | x, y_j^{0:i}) } \right)^2 \right] \, .
$$

- **机制**：相对 [[kimi-k1-5]] 的 policy optimization，引入 token-level clip——log-ratio 在 [α, β] 内正常算梯度，超出则梯度置零（gradient masking）。区别于标准 PPO clip [50]：**严格依赖 log-ratio 显式 bound off-policy drift，与 advantage 符号无关**，对齐 [74, 78] 的大规模 RL 稳定化策略。τ 项为 KL-ish 二次正则。
- **效果**：§4.4.2 实证指出该机制对 long-horizon、multi-step tool-use reasoning 复杂域的训练稳定"essential"。

---

## 表格（原文结构化）

### Table 1：vision-text joint-training 策略消融（固定 token 预算，§2.1）

| Vision Injection Timing | Vision-Text Ratio | Vision Knowledge | Vision Reasoning | OCR | Text Knowledge | Text Reasoning | Code |
|---|---|---|---|---|---|---|---|
| Early (0% 起步) | 10:90 | **25.8** | **43.8** | **65.7** | **45.5** | **58.5** | **24.8** |
| Mid (50% 起步) | 20:80 | 25.0 | 40.7 | 64.1 | 43.9 | 58.6 | 24.0 |
| Late (80% 起步) | 50:50 | 24.2 | 39.0 | 61.5 | 43.1 | 57.8 | 24.0 |

结论：vision ratio 影响极小，**early fusion + lower ratio 在全部指标领先**。

### Table 2：cross-modal transfer——Vision RL 提升文本（§2.3）

| Benchmark | Before Vision-RL | After Vision-RL | Improvement |
|---|---|---|---|
| MMLU-Pro | 84.7 | 86.4 | +1.7 |
| GPQA-Diamond | 84.3 | 86.4 | +2.1 |
| LongBench v2 | 56.7 | 58.9 | +2.2 |

### Table 3：训练阶段总览（§4.3）

| Stage | Data | Sequence Length | Tokens | Trainable Params |
|---|---|---|---|---|
| ViT Training | Alt text / Synthesis Caption / Grounding / OCR / Video | 4096 | 1T | ViT |
| Joint Pre-training | Text, Knowledge, Interleaving, Video, OS Screenshot | 4096 | 15T | ViT & LLM |
| Joint Long-context Mid-training | High-quality Text & Multimodal / Long Text, Long Video / Reasoning, Long-CoT | 32768→262144 | 500B→200B | ViT & LLM |

### Table 4 摘选：K2.5 vs 顶级 baseline（§5.1.2，bold=global SOTA）

| Benchmark | Kimi K2.5 | Claude Opus 4.5 | GPT-5.2 (xhigh) | Gemini 3 Pro | DeepSeek-V3.2 | Qwen3-VL-235B |
|---|---|---|---|---|---|---|
| HLE-Full w/ tools | **50.2** | 43.2 | 45.5 | 45.8 | 40.8† | - |
| AIME 2025 | 96.1 | 92.8 | **100** | 95.0 | 93.1 | - |
| HMMT 2025 (Feb) | 95.4 | 92.9* | 99.4 | 97.3* | 92.5 | - |
| IMO-AnswerBench | 81.8 | 78.5* | 86.3 | 83.1* | 78.3 | - |
| GPQA-Diamond | 87.6 | 87.0 | 92.4 | **91.9** | 82.4 | - |
| MMLU-Pro | 87.1 | 89.3* | 86.7* | **90.1** | 85.0 | - |
| SimpleQA Verified | 36.9 | 44.1 | 38.9 | **72.1** | 27.5 | - |
| AdvancedIF | 75.6 | 63.1 | **81.1** | 74.7 | 58.8 | - |
| LongBench v2 | 61.0 | 64.4* | 54.5* | **68.2*** | 59.8* | - |
| SWE-Bench Verified | 76.8 | **80.9** | 80.0 | 76.2 | 73.1 | - |
| SWE-Bench Multilingual | 73.0 | 77.5 | 72.0 | 65.0 | 70.2 | - |
| Terminal Bench 2.0 | 50.8 | 59.3 | 54.0 | 54.2 | 46.4 | - |
| PaperBench (CodeDev) | 63.5 | 72.9* | 63.7* | - | 47.1 | - |
| CyberGym | 41.3 | 50.6 | - | 39.9* | 17.3* | - |
| SciCode | 48.7 | 49.5 | 52.1 | **56.1** | 38.9 | - |
| OJBench (cpp) | 57.4 | 54.6* | - | **68.5*** | 54.7* | - |
| LiveCodeBench v6 | 85.0 | 82.2* | - | **87.4*** | 83.3 | - |
| BrowseComp | 60.6 | 37.0 | 65.8 | 37.8 | 51.4 | - |
| BrowseComp (w/ ctx manage) | 74.9 | 57.8 | 59.2 | 67.6 | - | - |
| BrowseComp (Agent Swarm) | **78.4** | - | - | - | - | - |
| WideSearch | 72.7 | 76.2* | - | 57.0 | 32.5* | - |
| WideSearch (Agent Swarm) | **79.0** | - | - | - | - | - |
| DeepSearchQA | 77.1 | 76.1* | 71.3* | 63.2* | 60.9* | - |
| FinSearchComp T2&T3 | 67.8 | 66.2* | - | 49.9 | 59.1* | - |
| Seal-0 | 57.4 | 47.7* | 45.0 | 45.5* | 49.5* | - |
| GDPVal-AA | 41.0 | 45.0 | 48.0 | 35.0 | 34.0 | - |
| MMMU-Pro | 78.5 | 74.0 | 79.5* | **81.0** | - | 69.3 |
| MMMU (val) | 84.3 | 80.7 | 86.7* | **87.5*** | - | 80.6 |
| CharXiv (RQ) | 77.5 | 67.2* | 82.1 | 81.4 | - | 66.1 |
| MathVision | 84.2 | 77.1* | 83.0 | **86.1*** | - | 74.6 |
| MathVista (mini) | 90.1 | 80.2* | 82.8* | 89.8* | - | 85.8 |
| SimpleVQA | 71.2 | 69.7* | 55.8* | 69.7* | - | 56.8* |
| WorldVQA | 46.3 | 36.8 | 28.0 | **47.4** | - | 23.5 |
| ZeroBench | 9 | 3* | 9* | 8* | - | 4* |
| ZeroBench w/ tools | 11 | 9* | 7* | **12*** | - | 3* |
| BabyVision | 36.5 | 14.2 | 34.4 | **49.7** | - | 22.2 |
| BLINK | 78.9 | 68.8* | - | 78.7* | - | 68.9 |
| MMVP | 87.0 | 80.0* | 83.0* | **90.0*** | - | 84.3 |
| OmniDocBench 1.5 | 88.8 | 87.7* | 85.7 | 88.5 | - | 82.0* |
| OCRBench | **92.3** | 86.5* | 80.7* | 90.3* | - | 87.5 |
| InfoVQA (test) | **92.6** | 76.9* | 84 | 57.2* | - | 89.5 |
| VideoMMMU | 86.6 | 84.4* | 85.9 | **87.6** | - | 80.0 |
| MMVU | 80.4 | 77.3* | 80.8* | 77.5* | - | 71.1 |
| MotionBench | **70.4** | 60.3* | 64.8* | 70.3 | - | - |
| Video-MME | 87.4 | 77.6* | 86.0* | **88.4*** | - | 79.0 |
| LongVideoBench | **79.8** | 67.2* | 76.5* | 77.7* | - | 65.6* |
| LVBench | **75.9** | 57.3 | - | 73.5* | - | 63.6 |
| OSWorld-Verified | 63.3 | **66.3** | 8.6* | 20.7* | - | 38.1 |
| WebArena | 58.9 | **63.4*** | - | - | - | 26.4* |

### Table 5 摘选：reasoning 模型 token 效率（§5.1.2，括号为平均 output token 千数）

| Benchmark | Kimi K2.5 | Kimi K2 Thinking | Gemini-3.0 Pro | DeepSeek-V3.2 Thinking |
|---|---|---|---|---|
| AIME 2025 | 96.1 (25k) | 94.5 (30k) | 95.0 (15k) | 93.1 (16k) |
| HMMT Feb 2025 | 95.4 (27k) | 89.4 (35k) | 97.3 (16k) | 92.5 (19k) |
| HMMT Nov 2025 | 91.1 (24k) | 89.2 (32k) | 94.5 (15k) | 90.2 (18k) |
| IMO-AnswerBench | 81.8 (36k) | 78.6 (37k) | 83.1 (18k) | 78.3 (27k) |
| LiveCodeBench | 85.0 (18k) | 82.6 (25k) | 87.4 (13k) | 83.3 (16k) |
| GPQA Diamond | 87.6 (14k) | 84.5 (13k) | 91.9 (8k) | 82.4 (7k) |
| HLE-Text | 31.5 (24k) | 23.9 (29k) | 38.4 (13k) | 25.1 (21k) |

### Table 6：Agent Swarm 增益（§5.2）

| Benchmark | K2.5 Agent Swarm | Kimi K2.5 (single) | Claude Opus 4.5 | GPT-5.2 | GPT-5.2 Pro |
|---|---|---|---|---|---|
| BrowseComp | **78.4** | 60.6 | 37.0 | 65.8 | 77.9 |
| WideSearch | **79.0** | 72.7 | 76.2 | - | - |
| In-house Swarm Bench | **58.3** | 41.6 | 45.8 | - | - |

### Agent Swarm step 预算（§E.8）

| Benchmark | Orchestrator 上限 | 每 sub-agent 上限 |
|---|---|---|
| BrowseComp | 15 | 100 |
| WideSearch | 100 | 100 |
| In-house Bench | 100 | 50 |

---

## 与同类对比

- **vs 传统 vision-adapted VLM（[8] Qwen3-VL / [21] Seed1.5-VL）**：后者在文本 backbone 训练后期高比例注入 vision，K2.5 反其道——early fusion + 恒定低 ratio（§2.1, Table 1），避免"dip-and-recover"文本退化。Table 4 vision 子项上 K2.5 在 OCRBench 92.3 / InfoVQA 92.6 / CharXiv 77.5 大幅领先 Qwen3-VL-235B（87.5 / 89.5 / 66.1），且未牺牲文本——MMLU-Pro 87.1 仍居第一梯队。

- **vs [[kimi-vl-technical-report]]**：MoonViT→MoonViT-3D，patch-n'-pack 推广到时间维，4 帧联合打包 + temporal pooling 4× 压缩；ViT continual pre-training 去掉 contrastive loss，仅用 cross-entropy caption loss（§4.2-4.3）。

- **vs sequential agentic RL（[2] Kimi-Researcher）**：[2] 优化单 agent tool execution via verifiable reward；PARL 增加 subagent creation / task delegation 接口（`create_subagent` / `assign_task`，§E.8），subagent frozen、轨迹不进优化目标，**解耦** coordination logic 与 execution proficiency。奖励设计显式对抗两种 failure mode（serial collapse / spurious parallelism），而 [2] 不涉及。

- **vs reactive context management（Hide-Tool-Result [2] / Summary [71] / Discard-all [14]）**：§3 + Figure 7——这些方法在 context 溢出后压缩/丢弃，reactive 且牺牲结构信息；Agent Swarm 是 **proactive context sharding**——长程任务分解为语义隔离的并行 subtask，subagent 维护独立 working memory 不污染 orchestrator 全局 context，只回传 task-relevant output。BrowseComp 上 Agent Swarm 在 accuracy 与 critical steps 双双优于 Discard-all。
- **LaTeX↔M3 双源校验（对比维度）**：Figure 7（M3："Agent Swarm pathway vs Discard-all pathway，proactive context sharding outperforms reactive history compression"）与 §3 "Agent Swarm as Proactive Context Management" 文本一致——proactive vs reactive 的核心论断双源确认。

- **vs Claude Opus 4.5 / GPT-5.2 / Gemini 3 Pro**：纯 reasoning 上未达 global SOTA（AIME 96.1 vs GPT-5.2 100、GPQA 87.6 vs Gemini 91.9、SimpleQA 36.9 vs Gemini 72.1），但在 **agentic search** 域显著领先——BrowseComp+Swarm 78.4 超 GPT-5.2 Pro 77.9；WideSearch+Swarm 79.0 超 Claude 76.2。OSWorld 63.3 仅次于 Claude 66.3 但远超 GPT-5.2 (8.6) 与 Gemini (20.7)。

- **vs 多 agent 启发式系统（[5][6][7] Anthropic multi-agent）**：那些是手工编排的 multi-agent research system；PARL 是**学习型**编排——orchestrator 通过 RL 探索学会何时/如何并行，而非预设启发式。

---

## 跨论文关系（→ MOC 谱系）

- 继承 [[kimi-k2-open-agentic-intelligence]]：K2.5 = K2 MoE backbone（1.04T total / 32B activated / 384 experts × 8 activated / sparsity 48）+ MuonClip optimizer + QK-Clip。§4.1 明确 K2.5 builds upon K2 checkpoint。RL 目标 Eq.1（`L_RL`，token-level clip）是对 [[kimi-k1-5]] policy optimization 的改造。
- 训练谱系 [[muon-is-scalable-for-llm-training]]：MuonClip 直接来自 Moonlight-16B-A3B 工作（§4.1, §4.3 ViT 对齐 Moonlight-16B-A3B）。
- VLM 谱系 [[kimi-vl-technical-report]]：MoonViT→MoonViT-3D，SigLIP-SO-400M 初始化 + NaViT packing 沿用自 Kimi-VL。
- 视觉 token 表征 [[deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms]]：同属"简化视觉 token 处理"路线，但 K2.5 走 patch-n'-pack 时空打包，DeepStack 走深度堆叠；可对照阅读。
- 同类 VLM [[qwen2-5-vl-technical-report]] / [8] Qwen3-VL：vision-adapted late-fusion 路线对照，K2.5 Table 4 全面压制。
- RL 谱系 [[deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning]]：同为 outcome-based verifiable reward RL，K2.5 在此基础上加 token-level clip + Togle 交替训练 + GRM。
- 后继 [[kimi-k3-open-frontier-intelligence]]：K3 为 frontier 续作，K2.5 的 joint multimodal + Agent Swarm 是其前置基础。
- Agentic RL 环境 [[kimi-researcher-end-to-end-rl]]：PARL 的 Unified Agentic RL Environment（§D，Gym-like 接口、Rollout Manager 100k 并发协程、partial rollout）是对 [2] 单 agent 环境的多智能体扩展。

---

## 局限与边界

1. **纯 reasoning 未达 global SOTA**：AIME 2025 (96.1 vs GPT-5.2 100)、HMMT (95.4 vs GPT-5.2 99.4)、IMO-AnswerBench (81.8 vs GPT-5.2 86.3)、GPQA (87.6 vs Gemini 91.9)、HLE-Full no-tools (30.1 vs Gemini 37.5)、AdvancedIF (75.6 vs GPT-5.2 81.1) 均落后。K2.5 优势在 agentic / multimodal，而非纯 STEM reasoning 巅峰。
2. **SimpleQA Verified 36.9 大幅落后 Gemini 72.1**：parametric knowledge factuality 仍是显著短板。
3. **Agent Swarm 仅在 3 个 benchmark 验证**（BrowseComp / WideSearch / In-house Swarm Bench，§5.2）。In-house Swarm Bench 为自建 benchmark，外部不可复现；WildSearch / Batch Download / WideRead / Long-Form Writing 四子域的细粒度数据未公开。
4. **PARL 的 subagent frozen 是工程妥协而非理论最优**：§3 明确——冻结 subagent 是为绕开 credit assignment ambiguity 与 training instability，意味着 subagent 的 execution proficiency 不会随 orchestrator 训练同步提升；orchestrator 优化的是"在给定 subagent 能力下的编排策略"，subagent 升级需重新训练。
5. **Agent Swarm step 预算人工设定**（§E.8）：BrowseComp orchestrator 15 步、subagent 100 步；WideSearch 各 100 步；In-house 100/50——这些上限是手调，而非学习所得。
6. **zero-vision SFT 依赖 joint pre-training 前提**：§2.2 自陈该现象"likely due to" joint pre-training 已建立强对齐——若脱离此前提（如 vision-adapted late-fusion 模型），zero-vision SFT 是否仍激活视觉能力未验证，泛化性存疑。
7. **cross-modal transfer 机制是事后归因**：§2.3 对"vision RL 提升文本"的解释为推测（"Analysis suggests... reducing uncertainty on queries that resemble visually grounded reasoning"），未给出机制级消融或 causal 证据。
8. **GPT-5.2 评估不完整**：§E.2 承认 GPT-5.2 API 不稳定，跳过 WideSearch 等高成本 benchmark；GPT-5.2-xhigh 在 vision 评估有 ~10% failure rate 被计为错误——baseline 数据是保守下界，部分对比的"领先"含水分。
9. **开源范围有限**：仅开源 post-trained checkpoint（§1），base model、GRM、subagent checkpoint、训练数据与 RL 环境代码均未开源，复现 PARL / Agent Swarm 需自建整套 Unified Agentic RL Environment（Appendix D）。
10. **computer-use 仍逊 Claude**：OSWorld 63.3 vs Claude 66.3、WebArena 58.9 vs 63.4——纯 GUI agent 能力未达 SOTA。
11. **长视频定性证据未量化**：Figure 11（Black Myth: Wukong 24h/32 视频/40GB，§F）仅以生成 HTML showcase 作 qualitative 演示，M3 也指出该图主体未渲染，无端到端 accuracy 数字支撑"多小时代码级长视频理解"的强主张。
