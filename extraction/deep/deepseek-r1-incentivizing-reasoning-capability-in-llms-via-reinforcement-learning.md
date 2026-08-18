# DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning — 技术点深读（DEEP 2026-08-18）
> 独立文件，extract_phase1 重跑不丢。全要素深读：全文前后文一致 + 6 张 M3 figure caption 织入。论文：arXiv:2501.12948v2 (4 Jan 2026)。

## 核心问题

LLM 推理能力长期受制于人类标注的 CoT 轨迹——SFT-on-human-demonstrations 路线既不可扩展（标注成本高），又把模型上限锁死在"复刻人类思维模式"，无法探索人类未曾提供的更优推理路径（§1, §A.2）。论文核心追问两个问题：

1. **能否跳过 SFT，用纯 RL 让 base model 自发生长出推理能力？** 即"reasoning 通过 outcome-based RL 自涌现"是否成立（§1, §2.3）。
2. **若纯 RL 涌现出的推理能力存在可读性差、语言混杂、非推理任务弱等缺陷，如何在不牺牲推理的前提下对齐人类偏好？** 进而能否把大模型的推理模式蒸馏到小模型，且效果优于直接在小模型上做大规模 RL（§3, §F）。

判据：以 AIME 2024、MATH-500、Codeforces、LiveCodeBench、GPQA Diamond 等可验证任务为标尺，对标 OpenAI-o1-1217。论文结论（§6）是"解锁推理潜力的关键不在大规模人工标注，而在 hard reasoning questions + 可靠 verifier + 足够算力"。

## 关键创新点

1. **R1-Zero：纯 RL 无 SFT 冷启动，证明推理可自发涌现（§2）。** 以 DeepSeek-V3-Base（671B MoE，37B 激活，MLA + auxiliary-loss-free load balancing + MTP，§A.1）为基础，直接上 GRPO，模板（Table 1）仅约束 `‹reasoning process here›</think>` + `<answer>...</answer>` 结构，不施加任何内容先验。奖励只有 rule-based 的 `Reward_rule = Reward_acc + Reward_format`（§2.2，式 4），**明确拒绝 neural reward model**——理由是大规模 RL 下神经 RM 必被 reward hacking，且重训成本高（§2.2）。AIME 2024 pass@1 从 15.6% 涨到 77.9%，cons@16 达 86.7%，超过人类参赛者均值（§2.3）。Figure 1a（p.4）的 M3 解读：横轴 0–10000 steps、纵轴 Accuracy，r1-zero-pass@1 与 cons@16 双曲线单调上行，human participants 基线被显著超越；步数末段仍未饱和说明 RL 训练可继续。

2. **"Aha moment" 与 self-evolution（§2.3, Table 2, §C.2）。** 训练中自发出现反思词（"wait"/"mistake"/"however"/"verify" 等）频次提升；"wait" 一词在 step 4000–7000 偶发、step 8000 后陡增（Figure 9b）。模型自发学会自我验证、回溯、探索替代策略，且响应长度随训练单调增长（Figure 1b，p.4；M3 解读：横轴 steps 0–10000、纵轴 avg length/token 0–20000，曲线持续上扬）——即"思考时间"被 RL 内化。Table 2 记录了模型在解 `√(x−√(x²−y²))=y` 时突然自语 "Wait, wait. Wait. That's an aha moment I can flag here." 并重评——作者称"这是我们的 aha moment"。

3. **GRPO 取代 PPO，省去 value model（§2.1, §A.3, 式 1–3, 11–13, Figure 3 p.14, Figure 4 p.16）。** 关键差异：PPO 用 GAE 估计 advantage 需训练一个与 policy 同尺寸的 value model，内存/算力开销大；而长 CoT 场景下基于"前缀 token 预测最终 reward"几乎不可能（模型中途会反思、改写、推翻前文，§A.3）。GRPO 直接从一组 G 个采样的 group reward 计算标准化 advantage `A_i = (r_i − mean)/std`，**无 value model**——Figure 3（p.14）的 M3 注记：该页 M3 caption 仅识别到 §A.3 正文与式 11–13 的文字引用，原图未渲染（caption "Demonstration of PPO and our GRPO. GRPO foregoes the value model, instead estimating the advantages from group scores."），故机制要点以 §A.3 文本为准：PPO 需 value model 估计 advantage，GRPO 用 group scores 代替。KL 散度用 unbiased estimator 直接加到 loss（式 11），而 PPO 把 per-token KL 作为 dense reward，会隐式惩罚响应长度，阻碍长 CoT 增长。每 400 步把参考模型替换为最新 policy，平衡探索与稳定。Figure 4（p.16）显示在 DeepSeek-Coder-V2-Lite (16B MoE, 2.4B 激活) MATH 任务上 GRPO 与精心调过 λ（GAE 系数设为 1.0）的 PPO 相当，但 PPO 默认 λ=0.95 时显著劣于 GRPO。

4. **R1 多阶段 pipeline：冷启动 SFT → reasoning RL → rejection sampling + 全量 SFT → 二阶段 RL（§3, Figure 2 p.6）。** Figure 2 的 M3 解读：四列从左到右流水线，紫色框=数据输入、蓝色框=训练操作、黑色三角=阶段转换；Stage 1 冷启动 SFT 数据（紫）→SFT（蓝）→rejection sampling→**Dev1**；Stage 2–3 推理数据（紫）与 RL pass（蓝）交替，首轮 RL 优化推理/语言一致性得 **Dev2**，次轮引入 preference 数据得 **Dev3**；Stage 4 最终 RL pass on preference data 产出 **DeepSeek-R1**。该图对照前后文：阶段产物 Dev1/Dev2/Dev3 在 Table 3（§4）逐级提升——Dev1（冷启动+一阶段 RL）IF-Eval 46.6→71.7、ArenaHard 53.6→77.0，但 AIME 因冷启动数据小而退化 77.9→59.0；Dev2（rejection sampling + 第二轮 SFT）推理回升 AIME 74.0、Codeforces Rating 1687；Dev3（加入非推理 SFT）Aider 12.2→44.8、AlpacaEval2.0 24.7→62.1；最终 R1（二阶段混合 RL）AlpacaEval2.0 87.6、ArenaHard 92.3，AIME 79.8、MATH-500 97.3。Figure 2 的"冷启动数据→RL→rejection SFT→preference RL"四段架构是修复 R1-Zero 可读性差/语言混杂/非推理弱三大缺陷的工程答案。

5. **Language Consistency Reward 抑制语言混杂（§3.2.1, 式 7, §B.6, Figure 7 p.37）。** `Reward_language = Num(Words_target)/Num(Words)`，直接加到总 reward。Figure 7（p.37）的 M3 解读：横轴=RL training steps、纵轴=语言一致性指标；两条曲线对照——无 LC reward 的 baseline 随步数单调退化（drift into language mixing），加 LC reward 后全程稳定 monolingual；side panel 显示数学基准持平、编码略降。即 LC 以"边际编码退步"换"可读性 + 人类偏好对齐"，与 §B.6 ablation 结论一致。

6. **二阶段 RL 的 reward 分解（§3.2.2, 式 8–10）。** `Reward = Reward_reasoning + Reward_general + Reward_language`，其中 reasoning 用 rule-based（数学/代码/逻辑），general 用 model-based RM（helpfulness + format），language 用 LC。关键工程细节：温度从一阶段的 1.0 降到 0.7（高温导致二阶段生成不连贯）；共 1700 步，general/preference 数据只在最后 400 步引入——超过几百步的 model-based reward 会触发 reward hacking（§B.5, Figure 6：reward 上升而 Codeforces 下降）。

7. **大 clip ratio 策略（§3.2.1）。** GRPO clip ratio ε 设为 10（远大于 PPO 常用 0.1–0.2）——作者归功于 Zhibin Gou 提出的 large PPO clipping（§7 作者贡献）。过小会截断大量 token 梯度降性能，过大则训练失稳（§3.2.1）。

8. **Model-based RM 的两点设计（§3.1, 式 5–6）。** Helpful RM：用 DeepSeek-V3 以 arena-hard prompt 生成偏好对，每对查询 4 次、随机分配 A/B 位置消除位置偏置，仅保留分差 Δ>1 的对，chosen/rejected 长度可比消除长度偏置，共 66K 对；用 pairwise loss。Safety RM：106K 标注 safe/unsafe 数据，用 **point-wise** loss。Helpful RM 只评最终 summary（不干扰推理），Safety RM 评整段（含推理过程）。RM 训练 bs=256, lr=6e-6, 1 epoch, max_seq=8192。

9. **蒸馏 > 小模型直接 RL（§F, §F.1, Table 15–17, Table 6 p.35）。** 用 R1 生成 800K 样本（600K reasoning + 200K non-reasoning）SFT 蒸馏到 Qwen2.5/Llama-3 系列，**仅 SFT 不做 RL**。Table 6（p.35）的 M3 解读：六款蒸馏模型 Qwen-1.5B/7B/14B/32B + Llama-8B/70B，初始 LR 与模型规模反相关（1.5B→1e-4, 70B→2e-5），两个最小 Qwen 变体（1.5B/7B）刻意用 Qwen2.5-**Math** 作 base 以 bootstrap 推理能力；SFT 2–3 epoch，cosine decay 到 1/10，max_ctx=32768，bs=64。性能：R1-Distill-Qwen-1.5B 在 AIME 2024 达 28.9%（超 GPT-4o 0513 的 9.3% 和 Claude-3.5-Sonnet 的 16.0%）；R1-Distill-Qwen-32B AIME 72.6%。对照实验（Table 16）：Qwen2.5-32B-Base 直接做 10K+ 步大规模 RL 得 Qwen2.5-32B-Zero，性能仅与 QwQ-32B-Preview 持平，全面低于 R1-Distill-Qwen-32B。结论：**蒸馏更经济的路径**；但要突破人类智能边界仍需更强 base + 更大规模 RL。

10. **Base checkpoint 容量门槛（§G.1）。** 7B dense、16B MoE 在 AIME 上无法靠纯 RL 涨点，长 CoT 退化为重复；到 32B dense、230B MoE、671B MoE 才出现实质增益——RL-from-scratch 对模型容量高度敏感。

11. **PRM 与 MCTS 路线均失败（§G.2）。** PRM 三大障碍：fine-grain step 难定义、step 正误难判、引入 model-based PRM 必然 reward hacking。MCTS 障碍：token 生成搜索空间远大于棋类、节点扩展上限导致局部最优、value model 难训且直接决定生成质量——AlphaGo 的 self-play 提升机制在 LLM 上难以复刻。

## 表格（原文结构化）

**Table 1（§2.1）— R1-Zero 训练模板**：`‹reasoning process here›</think>` + `<answer> answer here </answer>`，仅约束结构，无内容先验。

**Table 3（§4）— R1 各阶段性能**（关键列，R1-Zero / Dev1 / Dev2 / Dev3 / R1；与 Figure 2 p.6 四阶段架构逐一对应）：
- AIME 2024 pass@1: 77.9 / 59.0 / 74.0 / 78.1 / **79.8**
- MATH-500: 95.9 / 94.2 / 95.9 / 95.4 / **97.3**
- Codeforces Rating: 1444 / 1534 / 1687 / 1746 / **2029**
- LiveCodeBench: 50.0 / 57.5 / 63.5 / 64.6 / **65.9**
- IF-Eval: 46.6 / 71.7 / 72.0 / 78.1 / **83.3**
- AlpacaEval2.0: 24.7 / 50.1 / 55.8 / 62.1 / **87.6**
- ArenaHard: 53.6 / 77.0 / 73.2 / 75.6 / **92.3**
- GPQA Diamond: 75.8 / 66.1 / 70.7 / 71.2 / **71.5**（Dev1 退化最显著，因冷启动数据小）

**Table 4（§B.3.1）— RL 数据配方**：Math 26K（Number/Expression/Equation）、Code 17K（Code Solution）、STEM 22K（Option）、Logic 15K（Option/Number）、General 66K（Ranked Responses）。共 146K prompts。STEM 细分：physics 15.5%、biology 30.7%、chemistry 46.5%、other 7.3%。

**Table 5（§B.3.3）— 800K SFT 数据统计**：Math 395,285（avg 6094.2 tok）、Code 211,129（7435.7）、STEM 10,124（4928.8）、Logic 10,395（2739.0）、General 177,812（1419.8），Total 804,745（5355.3）。多为单轮（Avg Rounds 1.0–1.1）——多轮能力受限的根源。

**Table 6（§B.4.3, p.35）— 蒸馏模型与学习率**（M3 解读见创新点 9）：Qwen-1.5B(1e-4, base=Qwen2.5-Math-1.5B) / Qwen-7B(8e-5, Qwen2.5-Math-7B) / Qwen-14B(7e-5, Qwen2.5-14B) / Qwen-32B(6e-5, Qwen2.5-32B) / Llama-8B(5e-5, Llama-3.1-8B) / Llama-70B(2e-5, Llama-3.3-70B-Instruct)。

**Table 7（§B.4.4）— 训练成本**：R1-Zero 101K H800-h（$202K）、SFT 数据制作 5K-h（$10K）、R1 41K-h（$82K），合计 147K H800-h ≈ **$294K**（H800 $2/GPU-h）。R1-Zero 训练 198 小时（64×8=512 张 H800）；R1 约 80 小时。

**Table 8（§D.2）— R1 vs SOTA 主表**（R1 / o1-1217 / o1-mini / GPT-4o-0513 / Claude-3.5-Sonnet / DeepSeek-V3）：
- AIME 2024: 79.8 / 79.2 / 63.6 / 9.3 / 16.0 / 39.2
- MATH-500: 97.3 / 96.4 / 90.0 / 74.6 / 78.3 / 90.2
- Codeforces Percentile: 96.3 / 96.6 / 93.4 / 23.6 / 20.3 / 58.7
- LiveCodeBench: 65.9 / 63.4 / 53.8 / 32.9 / 38.9 / 36.2
- GPQA Diamond: 71.5 / 75.7 / 60.0 / 49.9 / 65.0 / 59.1
- MMLU: 90.8 / 91.8 / 85.2 / 87.2 / 88.3 / 88.5
- ArenaHard: 92.3 / − / 92.0 / 80.4 / 85.2 / 85.5

**Table 9（§D.3, p.48）— 安全基准对比**（M3 解读）：六安全基准矩阵 SST/BBQ/ART/XSTest/DNA*/HarmBench* + Average。DeepSeek-R1 平均 **95.0**（含风险控制），可比 Claude-3.7-Sonnet(94.6)/GPT-4o(92.2)。括号为纯模型无风险控制分数——R1 HarmBench 从 89.3→35.0（崩塌 54.3），DNA 也大幅下降，揭示"纯模型安全高度依赖 post-hoc 风险控制系统而非内禀对齐"。

**Figure 14 / §D.3.4 (p.53) — 多语言安全**（M3 注记：原图未渲染，正文给出数据）：50 语言 9,330 题，LLM-as-judge 评分（Safe=5, Unsafe=0, Rejection=4）。DeepSeek-R1 含风险控制 85.9% / 无风险控制 74.2%；DeepSeek-V3 86.5%/75.3%；Claude-3.7-Sonnet 88.3%；GPT-4o 75.2%。R1 无高危语言（零语言特异性漏洞）。

**Table 12（§E.1）— V3-Base / V3 / R1-Zero / R1 对比**：V3-Base → R1 在 MMLU-Pro 64.4→84.0、AIME − → 79.8、Codeforces Rating − → 2029；R1-Zero 在 ArenaHard(53.6)、AlpacaEval2.0(24.7) 上反而弱于 V3，被 R1 多阶段流程修复。

**Table 13（§E.2）— 真实竞赛泛化**：AMC 12 2024 上 R1 得 143.7/150（超 o1 的 141.0、人类均值 61.7）；AIME 2025 pass@1 75%（接近 o1 的 80%）；USAMO Index 256.7（超 251.5 晋级线）。

**Table 15（§F）— 蒸馏模型主表**（AIME/MATH-500/GPQA/LiveCodeBench/Codeforces rating）：R1-Distill-Qwen-1.5B 28.9/83.9/33.8/16.9/954；R1-Distill-Qwen-32B 72.6/94.3/62.1/57.2/1691；R1-Distill-Llama-70B 70.0/94.5/65.2/57.5/1633。

**Table 16（§F.1）— 蒸馏 vs RL**：Qwen2.5-32B-Zero（直接 RL，AIME 47.0、MATH-500 91.6、GPQA 55.0、LCB 40.2）全面低于 R1-Distill-Qwen-32B（72.6/94.3/62.1/57.2）。

**Table 17（§F.1）— 7B RL 亦成立**：Qwen2-Math-7B-Zero（10K 步 RL）AIME 2024 22.3%、AIME 2025 18.1%，远超 Qwen2-Math-7B-Instruct（7.9%/4.6%）与 GPT-4o（9.3%）。

**Table 14（§E.5）— 各阶段分难度（LiveCodeBench）**：Hard 从 R1-Zero 17.09 → R1 34.44，Easy 接近饱和（98→100）。

**Table 9–11（§D.3）— 安全**：R1（含风险控制）平均 95.0；jailbreak 下 R1 unsafe 从 25.2%→85.9%（+60.7），加风险控制后仅 4.3%。推理模型比非推理模型更依赖风险控制系统。

## 与同类对比

- **vs OpenAI-o1-1217（§4, Table 8）**：AIME 2024（79.8 vs 79.2）、MATH-500（97.3 vs 96.4）、Codeforces（96.3 vs 96.6）基本持平；o1 在 GPQA Diamond（75.7 vs 71.5）、MMLU（91.8 vs 90.8）、Aider（61.7 vs 53.3）占优。R1 工程类编码（Aider）弱，归因于 RL 工程数据不足。
- **vs PPO（§A.3, Figure 3 p.14, Figure 4 p.16）**：GRPO 省去 value model（同等规模省一半显存），无需调 GAE λ；PPO 在 λ=1.0 时可逼近 GRPO 但需额外调参，λ=0.95 默认值时显著劣于 GRPO。
- **vs Process Reward Model（§G.2）**：PRM 在 rerank top-N、guided search 有效，但在大规模 RL 中因 step 定义难、标注不可扩展、必触发 reward hacking 而被弃用。
- **vs MCTS（§G.2, §6 Limitations）**：MCTS + value model 在推理时配预训 value 可改善，但自搜索迭代提升难以复现 AlphaGo 成功——token 搜索空间过大、value model 难训。
- **vs majority voting / 自一致（§E.4）**：非推理模型（GPT-4o）64 样本 majority voting 仅把 AIME 从 9.3%→13.4%，远低于 R1 的 79.8%；而 R1 自己的 Pass@64 90.0% 说明多链路采样仍能补益长 CoT——majority voting 把 R1 从 79.8%→86.7%。R1 是动态分配 token（简单题 <7000，难题 >18000 thinking tokens），优于朴素 test-time scaling。
- **vs distillation-from-teacher（§F）**：小模型从强 teacher 蒸馏 > 小模型自己跑大规模 RL（Table 16）；但突破人类智能边界仍需大 base + 大 RL。

## 跨论文关系（→ MOC 谱系）

- [[deepseek-v3-technical-report]] — **base 模型提供者**。R1/R1-Zero 都建立在 DeepSeek-V3-Base（671B MoE, 37B 激活, MLA + auxiliary-loss-free load balancing + MTP）之上；R1 复用 V3 的 SFT 非推理数据；RL 框架集成 vLLM、DualPipe（V3 训练算法）、MTP 自推测解码（§B.1, Figure 5）。V3-Base 预训练含大量数学/代码内容，为 RL 提供"候选解生成"前提（§A.1）。
- [[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]] — **RL vs 提示演化的对照轴**。R1 是"纯 RL 激励推理"的代表（AIME/纯数学 GRPO 强）；GEPA 在复合系统上可超 RL——两者构成"任务可验证性 → RL 占优 vs 提示演化占优"的分界。R1 的 reward hacking（§B.5, Figure 6）正是 GEPA 类反射演化可绕过的痛点。
- [[search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning]] — **R1 的工具调用扩展**。R1 §6 明确把"无法用搜索引擎/计算器"列为局限；Search-R1 直接补上 tool-use RL，沿用 R1 的 outcome-based RL + rule-based reward 范式。
- [[areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning]] + [[hybridflow-a-flexible-and-efficient-rlhf-framework]] — **RL 训练系统谱系**。R1 的 RL 框架（§B.1, Figure 5）四模块解耦（Rollout/Inference/Rule-Reward/Training）+ vLLM + 专家并行 + 异步调度（rule-reward 异步 overlap rollout/inference）+ DualPipe，是 AREAL/HybridFlow 同期的工业级 RLHF 基础设施对照。
- [[high-dimensional-continuous-control-using-generalized-advantage-estimation]] — **GAE 是 PPO 的 advantage 估计基础**，R1 用 GRPO 显式弃用 GAE + value model（§A.3, Figure 3 p.14）——是 GAE/PPO → GRPO 这条 RL 算法演化的关键节点。
- [[single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning]] — R1 的多阶段 RL + 单 rollout 内 16 minibatch 单内 epoch 的工程做法，与单 rollout 异步优化在 agentic RL 中的延展同源。
- [[deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models]] — **GRPO 算法的发源论文**（Shao et al., 2024）。R1 的 GRPO 即源于 DeepSeekMath，R1 是该算法在 671B MoE + 纯 RL 推理场景下的规模化验证与里程碑应用。

**RL-incentivized-reasoning 根节点定位**：R1 在 RL 系统谱系中是"outcome-based RL → reasoning 自涌现"的里程碑节点——上游承接 PPO/GAE/DeepSeekMath-GRPO（是其简化后继）、DeepSeek-V3（base）；下游衍生 Search-R1（工具扩展）、蒸馏小模型系列、AREAL/HybridFlow 系统侧研究、GEPA 反射演化对照。它确立了"可验证任务 + rule-based reward + 大 base + GRPO"的范式模板。

## 局限与边界

- **结构化输出与工具使用（§6）**：R1 不能用搜索引擎/计算器，结构化输出弱——这正是 Search-R1 等后续工作的入口。
- **Token 效率 / overthinking（§6, §E.4）**：简单题也常过度推理；虽动态分配 token（简单题 <7000，难题 >18000 thinking tokens），但仍未优化到最优。
- **语言混杂（§6, §A.1）**：仅对中英文优化，其他语言会用英文推理；根源在 V3-Base 主要是中英文。Figure 7（p.37）证明 LC reward 可控中英，但其他语言未覆盖。
- **Prompt 敏感（§6）**：few-shot 一致性降低性能，必须 zero-shot + 显式输出格式。
- **软件工程任务（§6）**：长评估周期拖慢 RL，R1 在 SWE 上对 V3 提升有限（SWE Verified 49.2）——未来需异步评估或 rejection sampling。
- **Reward hacking（§6, §B.5, Figure 6）**：model-based RM 在写作等不可验证任务上必被攻破，只能"几百步 RL + 人工标注 SFT"兜底；纯 RL 在无可靠 verifier 的任务上仍是开放问题。这正是二阶段 RL 只在最后 400 步引入 preference reward 的原因。
- **Base 容量门槛（§G.1）**：<32B 模型纯 RL 无效，限制民主化部署——这正是蒸馏路线存在的理由。
- **多轮对话弱（§B.3.3, Table 5）**：800K SFT 多为单轮（Avg Rounds 1.0–1.1），多轮能力待补。
- **安全（§D.3, Table 9 p.48, Figure 14 p.53）**：R1 纯模型安全仅"中等"（平均 95.0 依赖外部风险控制系统，DeepSeek-V3 作 judge）；Table 9 括号显示无风险控制时 HarmBench 89.3→35.0 崩塌；jailbreak 下脆弱（unsafe 25.2%→85.9%，加风险控制后 4.3%）。多语言安全（Figure 14）含风险控制 85.9% / 无 74.2%。
- **蒸馏 vs RL 的取舍（§F.1）**：蒸馏经济有效但要"突破人类智能边界"仍需更强 base + 更大 RL——蒸馏本身有上限。
- **n-gram decontamination 不能防 paraphrase（§D.1）**：2024 年前发布的 benchmark 仍可能存在 paraphrase 污染。
