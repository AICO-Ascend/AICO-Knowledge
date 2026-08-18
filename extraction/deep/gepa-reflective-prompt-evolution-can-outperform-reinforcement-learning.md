# GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning — 技术点深读（DEEP 2026-08-18）

> 独立文件，extract_phase1 重跑不丢。全文+图+表+公式一体化深读。
> 论文：GEPA (Genetic-Pareto): Reflective Prompt Evolution Can Outperform Reinforcement Learning · arXiv:2507.19457v2 · ICLR 2026 (Oral)

## 核心问题

LLM 适配下游任务的主流路径是 RLVR（如 GRPO），但 RL 方法**样本效率极差**：典型 GRPO 工作需上万到几十万 rollouts（§1 列举 Chen/Wu/Zhang 等 2025 系列工作，常达数十万 rollouts）。这在三类现实场景下成为瓶颈：(a) rollouts 自身昂贵（工具调用、推理预算受限）；(b) 最强闭源模型**无法微调权重**；(c) 长时 agent rollout 单步代价高。Figure 1（p.1，M3 解读：HotpotQA/IFBench 双面板，rollouts 对数轴，三条曲线 GEPA 绿/MIPROv2 橙/GRPO 蓝阶跃）直观呈现这一痛点——GRPO 需逼近 24000 rollouts 才缓慢爬升，而 prompt 优化器数百 rollouts 即抵达更高平台。

GEPA 的核心论点（§1）：复合 AI 系统的一次 rollout 可被**序列化为自然语言轨迹**（各模块指令、推理链、工具调用、以及 reward 函数内部文本如编译器报错——在塌缩成 scalar reward 之前）。这些轨迹富含 LLM 已能理解的诊断信号；**在自然语言空间反思式学习**比在标量 policy-gradient 空间学习能更好利用 LLM 的语言先验，从而用极少 rollouts 达到大幅质量提升。

形式化（§2，公式 1-2）：复合 AI 系统 Φ=(M,C,X,Y)，M=⟨M₁,…,M_{|M|}⟩ 为语言模块，C 为控制流，X/Y 为全局 IO schema。每个 module M_i=(π_i, θ_i, X_i, Y_i)，π 为 prompt（含指令与 few-shot）、θ 为底层权重。系统对任务实例 (x,m) 产出 y=Φ(x;⟨Π,Θ⟩)，度量 μ:Y×M→[0,1] 衡量输出质量。优化目标：
- 公式(1)：argmax_{⟨Π,Θ⟩} E_{(x,m)~T}[μ(Φ(x;⟨Π,Θ⟩);m)]——允许同时更新 prompts 与权重，以兼容不同参数空间优化器（GEPA vs GRPO）的可比性。
- 公式(2)：在 rollout 预算 B 约束下的 argmax 版本。

GEPA 只更新 Π（prompts），Θ 冻结——这使其天然可用于闭源模型，并与权重空间优化器（GRPO）形成"学习媒介"维度的对照（Figure 3，p.5，M3 解读：迭代循环 propose→minibatch 评估→若改进则升评到 D_pareto→Pareto 采样保多样→写入 pool P 含 ancestry；Figure 4，p.6 给出 Algorithm 1 主循环 + Algorithm 2 SelectCandidate 的形式化伪代码）。

## 关键创新点

### 1. Reflective Prompt Mutation（§3，Algorithm 1）——把 rollout 轨迹作为语言空间梯度
- **机制**：每轮从 Pareto 前沿（见下条）随机选一候选，在 minibatch（b=3，§E.4）上执行，抽取每个 module 的输入/输出/推理轨迹；feedback 函数 μ_f 返回数值分 + **text feedback**（编译器报错、失败 rubric、各 hop 检索缺口等）。按 round-robin 选定待更新 module j，reflection LM 读入 (current prompt π_j, trajectory, score, feedback)，反思维度式归因到 prompt 元素并提出修订 π'_j；新组合在 minibatch 重评，**仅当分数提升**才加入候选池并升评到全 D_pareto 验证集（Algorithm 1 line 14）。Meta-prompt 见 Appendix C（Figure C，p.22）：要求 LM 从样例中提取"niche and domain specific factual information"与可泛化策略写进新指令——这是 GEPA 产出 declarative 详尽指令而非 quasi-exemplars 的机制根因。
- **效果**：§1 称"even just a few rollouts into a large quality gain"；Figure 5（p.7，M3 解读：PUPA 任务 Figure 25d 的标注子树，红箭头标注每步针对性增强，candidate 0→11 对应 82.26→94.44，Appendix K.1 给出 Node 0/2/4 全文 prompt：Node 0 是两行 seed，Node 2 进化成含"Privacy Preservation / Query Understanding / Quality Maximization / Reasoning Explanation"五节、含占位符抽象策略的 rubric 式指令，分数 82.26→90.99→94.44）直观演示"单次 reflective update 即可观涨点"。
- **Evaluation traces 作为第二诊断源**（§3）：除执行轨迹外，识别出**评估过程产生的文本**（编译/执行/profiling 的报错在被压成 reward=0 之前）也是高价值反馈，扩展 μ 成 μ_f 同时返回 feedback_text，可按 module 细化（multi-hop 系统 per-hop 反馈）；并支持 human-grader 解释作为辅助 feedback_text。

### 2. Pareto-based Candidate Selection（§3.1，Algorithm 2）——"illumination" 策略逃局部最优
- **机制**：朴素"总选最高分候选"（TextGrad 策略）一旦找到一种主导策略就被锁死，budget 耗尽无法超越。GEPA 采用 quality-diversity（Mouret & Clune 2015）思路：对每个训练实例 i 记录所有候选的最高分 s*[i]，形成**逐实例 Pareto 集 P*[i]**；剔除被严格支配的候选；剩余候选按"在多少个实例的 Pareto 前沿中出现"（频率 f[·]）加权随机采样（Algorithm 2）。
- **效果**（Table 3，Qwen3-8B 四任务聚合）：SelectBestCandidate +6.05%、BeamSearch(N=4) +5.11%、**GEPA Pareto +12.44%**——Pareto 比 greedy 高 6.4%、比 beam 高 7.33%；单任务最大差距达 8.17%（vs greedy）/11.33%（vs beam）。Figure 6（p.10，M3 解读：左 SelectBestCandidate 树一代后塌缩到单支停滞，右 Pareto 树多节点并行扩展、同 budget 收敛到更高分程序）与公式推导一致——逐实例 Pareto 前沿天然保持多策略共存，避免单一最优解对预算的吞噬。

### 3. System-Aware Merge（§D.1，Algorithm 3/4）——遗传交叉合并互补谱系
- **机制**（Figure 9，p.24，M3 解读：Algorithm 3 DESIRABLE 逐 module 比对 ancestor 与两 descendant 的 prompt，仅当"一方等于 ancestor 而另一方已改"才返回 True；Algorithm 4 MERGE 用 seeded sampler r 抽两个 distinct parent，跳过直系祖先后逐 module 取"已改进的那一方"版本，若两方都改取高分者、tie 随机）：需同时满足 (a) 共享某公共祖先 a 但**优化了不相交的 module 子集**；(b) 二者均 Pareto-optimal；(c) 均在聚合分上超越祖先 S[a]。血缘条件苛刻→merge 稀疏触发（每 run 最多 5 次，§E.4）。
- **效果**（Observation 5）：GPT-4.1 Mini 上 GEPA+Merge 比 GEPA 再多 +2% 聚合、个别任务 +5%；但 Qwen3-8B 上超参未针对调优时反退化（IFBench 38.61→28.23、PUPA 91.85→86.26，Table 1）——作者归因为 mutation/crossover 预算分配与 merge 调用时机不当（merge 应在"已演化出充分不同的独立 lineage"时触发），留作 future work。

### 4. Instruction-only 优于 joint instruction+few-shot（Observation 2）——扭转 prior trend
- **机制**：GEPA 只优化指令不优化 demo，但 reflectively evolved instructions 含详尽 declarative 指令（Figure 2，p.3，M3 解读：seed 仅"given question, summary_1, produce query"一行；GEPA 进化版含 Input Understanding / Purpose and Context / Key Observations and Lessons / How to Build the Query / Practical Strategy / Output 六节，含 parish→archipelago 等具体 worked example 与"避免复述 first-hop"等负约束）。这与 prior work（Wan 2024）所指"quasi-exemplars"（指令退化成隐式示例）形成对照，归因于现代 LLM 指令遵循与自反思能力提升 + GEPA meta-prompt 显式要求"提取 domain facts 与 generalizable strategy"。
- **效果**：六任务两模型全胜 MIPROv2，GPT-4.1 Mini 边际达 11.1%、Qwen3 8B 达 10.3%；GEPA/GEPA+Merge 聚合增益 +12.19%/+13.33%，是 MIPROv2 +5.64% 的两倍多。Figure 16（p.30，M3 解读：按 optimizer 分组的 generalization gap，即 test 减 best validation）显示反思式指令的 generalization gap 也低于 exemplar 类——颠覆 Wan 2024"exemplar generalize better"的旧结论。

### 5. 紧凑 prompt 即更便宜更泛化（Observation 4）
GEPA/GEPA+Merge 的 prompt 比 MIPROv2 **短最多 9.2×**、约仅 1/3 长度（Figure 17/18，p.30-31，M3 解读：Figure 17 双模型散点图 aggregate score 对 aggregate prompt token 数，GEPA 点稳定落在 MIPROv2 左上方即"更短且更高分"；Figure 18 分 benchmark 柱状对比 token 数，GEPA+Merge 普遍低于 SelectBestCandidate ablation）。因 MIPROv2 token 多花在 few-shot demo。更短 prompt → 输入计费降、延迟降、serving 效率升（引 Kwon 2023 vLLM、Zheng 2024 SGLang、Agrawal 2023 Sarathi、Yu 2025 Pensieve）。趋势：性能更高的优化器往往 prompt 更短。

### 6. 跨模型迁移（Observation 6）
GEPA-Qwen-Opt：用较弱 Qwen3-8B 优化、迁到 GPT-4.1-Mini 评测，聚合 +9.00%（HotpotQA 单任务 +27.67%），**反超直接在 GPT-4.1-Mini 上优化的 MIPROv2(+5.64%)/TextGrad(+6.11%)/Trace(+3.27%)**——证明反思式学到的指令是模型无关的高层规则，可在弱模型上低成本优化后部署到强模型。

### 7. 推理时搜索（§5.1）——把任务集当 train，"overfit" 全集互学
把待解任务全集作为 D_train 与 D_pareto（如 35 个 KernelBench 模块），GEPA 跨任务迁移 lessons。NPU Kernels（NPUEval/AMD XDNA2，GPT-4o，Figure 7 p.13 M3 解读：GEPA 单 prompt 使 Sequential10 agent 无 RAG 达 26.85% 向量利用率，含 RAG 的 Sequential10+GEPA 均值 30.52%、单 kernel 达 70%）：Sequential10 仅 4.25% 均值，加 RAG 16.33%，再加 MIPRO 19.03%。CUDA Kernels（KernelBench 代表子集 35 任务，Figure 8 p.13 M3 解读：fast_p 对 rollouts 曲线，p∈[0.5,1]，GEPA+GPT-4o 把 close-to-0% 的 fast₁ 提到 >20%）。关键技术：feedback 函数 μ_f 按 rollout 失败动态检索技术手册段落注入领域知识（§5.1 提及 Figure 27 给出 NPUEval 的进化 prompt 全文，但该图不在本文 16 张 caption 范围内，not-available）；cache 下消除温度随机性、改进归因于 prompt 而非采样。

### 8. 对抗 prompt 搜索（§5.2）——反转 reward
对 AIME 反转奖励（最小化 pass@1，要求不矛盾任务、保留解题信息），用 AIME 2022-2024 进化单一通用对抗指令 prepend 到每 query。GPT-5 Mini 在 AIME-2025 pass@1 从 76% 降到 **10%**（5 runs×30 题=150 generations）。学到的对抗 prompt 注入无关 trivia（蜂蜜永不变质、尼罗河最长 6650km、海豚睁一眼睡觉）+ 严格格式约束 `### <final answer>`，触发模型把字面占位符当答案输出——揭示 instruction-following 的脆弱交互（非格式约束单独所致），可作 red-team/regression 套件与 safety training 数据源。

## 表格（原文结构化）

### Table 1：Qwen3 8B 各优化器基准得分（test set）
| 方法 | HotpotQA | IFBench | HoVer | PUPA | AIME-2025 | LiveBench-Math | 聚合 | 增益 |
|---|---|---|---|---|---|---|---|---|
| Baseline | 42.33 | 36.90 | 35.33 | 80.82 | 27.33 | 48.70 | 45.23 | — |
| GRPO | 43.33 | 35.88 | 38.67 | 86.66 | 38.00 | 51.26 | 48.91 | +3.68 |
| MIPROv2 | 55.33 | 36.22 | 47.33 | 81.55 | 20.00 | 46.60 | 47.84 | +2.61 |
| **GEPA** | **62.33** | **38.61** | **52.33** | **91.85** | 32.00 | 51.95 | **54.85** | **+9.62** |
| GEPA+Merge | 64.33 | 28.23 | 51.67 | 86.26 | 32.00 | 51.95 | 52.40 | +7.17 |

GEPA 总 rollouts（+Merge）：6871/3593/7051/2426/1839/1839（聚合 3936）；GRPO 固定 24000/任务。**注 AIME 上 GRPO 仍领先（38 vs 32）——GEPA 并非全胜，纯单步 CoT 数学任务 RL 仍有优势。** Figure 10（p.28，M3 解读：双面板柱状图 a=GPT-4.1 Mini / b=Qwen3 8B，aggregate + 各 benchmark 对比多优化器）与 Table 1/2 互证。

### Table 2：GPT-4.1 Mini 各优化器基准得分（test set）
| 方法 | HotpotQA | IFBench | HoVer | PUPA | AIME-2025 | LiveBench-Math | 聚合 | 增益 |
|---|---|---|---|---|---|---|---|---|
| Baseline | 38.00 | 47.79 | 46.33 | 78.57 | 49.33 | 58.20 | 53.03 | — |
| Trace (OptoPrime) | 60.33 | 51.19 | 46.00 | 74.18 | 45.33 | 60.74 | 56.30 | +3.27 |
| MIPROv2-No-Demos | 38.00 | 52.04 | 51.33 | 91.85 | 48.67 | 60.97 | 57.14 | +4.11 |
| MIPROv2 | 58.00 | 49.15 | 48.33 | 83.37 | 51.33 | 61.84 | 58.67 | +5.64 |
| TextGrad | 62.33 | 48.64 | 47.67 | 85.68 | 46.67 | 63.84 | 59.14 | +6.11 |
| **GEPA** | **69.00** | 52.72 | 51.67 | 94.47 | **59.33** | 64.13 | 65.22 | +12.19 |
| **GEPA+Merge** | 65.67 | **55.95** | **56.67** | **96.46** | **59.33** | **64.13** | **66.36** | **+13.33** |
| GEPA-Qwen-Opt（Qwen 优化迁 GPT-4.1-Mini 评测） | 65.67 | 49.83 | 54.67 | 90.05 | 52.67 | 59.31 | 62.03 | +9.00 |

### Table 3：候选选择策略对比（Qwen3 8B，Figure 6 对应实验）
| 策略 | HotpotQA | IFBench | HoVer | PUPA | 聚合 | 增益 |
|---|---|---|---|---|---|---|
| Baseline | 42.33 | 36.90 | 35.33 | 80.82 | 48.84 | — |
| SelectBestCandidate（TextGrad 风格） | 58.33 | 30.44 | 45.33 | 85.45 | 54.89 | +6.05 |
| BeamSearch（APO, N=4） | 57.33 | 36.39 | 41.00 | 81.08 | 53.95 | +5.11 |
| **GEPA（Pareto）** | **62.33** | **38.61** | **52.33** | **91.85** | **61.28** | **+12.44** |

### Table（成本，§E.3）：GPT-4.1 Mini 全部实验 < $500
GEPA $86 / GEPA-Merge $67 / MIPROv2 $76 / Trace+TextGrad $172 合计。

### Table（GRPO 超参，§E.4）
复合系统：group size 12、4 实例/步（batch 48）、LoRA rank 16 α=64 dropout 0.05、bf16、目标 [q,k,v,o,up,down,gate]、lr 1e-5、β=0.01、reward scale normalization、grad clip 0.1、20 步梯度累积、constant-with-warmup、500 步=固定 24000 rollouts、validation 每 20 步早停、1×H100/A100 80GB（rollout 用独立 GPU）。单模块（Figure 11 全参数实验）：full-parameter、group 16、global batch 32（8 GPU×4 micro）、FSDP2、per-GPU forward micro-batch 12、温度 1.0、KL 正则、lr 1e-6、validation 每 5 步、评测 temp 0.6/top-p 0.95/top-k 20。Figure 11（p.28，M3 解读：2-hop HoVer GEPA vs full-param GRPO 学习曲线，相对差距与 LoRA 版 Figure 1 一致）证明 GEPA 优势非 LoRA 限制所致。

### 搜索树 ablation 汇总（Figures 19-26，p.31-34）
每 benchmark×model 一组 4 子图：(a) SelectBestCandidate、(b) SelectBestCandidate+Merge、(c) GEPA(-Best Config)、(d) GEPA+Merge(-Best Config)，统一隔离 selection 策略与 merge 贡献。M3 解读：GEPA+Merge 树普遍更宽更深，SelectBestCandidate 树早期塌缩——与 Table 3 数字一致。

## 与同类对比

- **vs GRPO（权重空间 RL，LoRA 与 full-param）**：6 任务平均 +6%、单任务最高 +19-20%，rollouts 少最多 35×；GEPA 仅 79-737 train rollouts 即达最优，匹配 GRPO 最佳 validation 仅需 102/32/6/179 train rollouts（最多 78× 更省）。Figure 11 证明对 full-parameter GRPO 同样存在差距——非 LoRA 限制所致。
- **vs MIPROv2（SOTA prompt 优化器，Bayesian 联合优化 instruction+demo，auto=heavy 即 18 instruction candidates + 18 bootstrapped few-shot sets）**：所有 benchmark×model 全胜，聚合增益翻倍（+13.33 vs +5.64）；prompt 短 9.2×、约 1/3；instruction-only 反超 joint instruction+demo。
- **vs TextGrad / Trace(OptoPrime)**：TextGrad 用 SelectBestCandidate 易陷局部最优（Table 3 直接证据；Trace 不支持 per-module feedback，论文按 BBH tutorial 格式给 fallback feedback）。GPT-4.1 Mini 聚合 GEPA +12.19 vs TextGrad +6.11 vs Trace +3.27。
- **vs APO（BeamSearch）**：Pareto 比 beam 高 7.33% 聚合（Table 3）。
- **vs EvoPrompt / Rainbow Teaming / AlphaEvolve / OpenEvolve**（§6）：演化算法同族，但 GEPA 额外引入领域 textual feedback 做靶向 mutation、Pareto 前沿而非单一最优、跨 domain 的 prompt evolution（AlphaEvolve 单一硬问题、面向代码）。
- **vs Reflexion / Self-Refine / in-context bandit / Dynamic Cheatsheet / reasoning cache**（§6）：同属"语言空间学习"，但这些是 in-context/工作流记忆；GEPA 用样例提出**新指令**生成任务特定规则，并维持 Pareto 候选池做 evolution。
- **vs Optimas**：Optimas 给每 module 设全局对齐局部 reward；GEPA 用全局 reward + 每 module 环境 textual feedback + 逐实例 Pareto 前沿。
- **vs Agent-Pro**：Agent-Pro 通过动态 belief 生成与交互经验反思演化 agent policy；GEPA 维持显式 Pareto 前沿 + 谱系感知 merge。

## 跨论文关系（→ MOC 谱系）

- **[[deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning]] — RL 路径代表、GEPA 直接对照靶**：DeepSeek-R1 用 GRPO 类 RLVR 在权重空间激励推理能力，是 GEPA 在 §1/§4 反复对标（24k rollouts GRPO）的"样本低效但权重可学"对照分支。GEPA 论证：在 prompt 空间反思可同样涨点（AIME 等）而省 35× rollouts，且可用于 R1 类强模型不可微调的场景。二者共同点是都依赖 verifiable reward，分歧在学习媒介（标量梯度 vs 自然语言反思）。
- **[[search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning]] — 检索增强 RL，正交可互补**：Search-R1 用 RL 训 LLM 学会调用搜索引擎的多跳推理；GEPA 的 multi-hop QA 系统（HotpotQA/HoVer，Figure 2 的 second-hop query writer）优化的正是同类 query-writer module 但走 prompt evolution。GEPA 可作为 Search-R1 风格系统的样本高效替代/前置优化（论文未直接联用，留作 future direction）。
- **[[hybridflow-a-flexible-and-rlhf-framework]] — RLHF 训练基础设施**：HybridFlow 是 RLHF/RL 训练分布式框架（PPO/RLHF 系），代表"权重空间 RL 的系统侧工程"。GEPA 是"算法侧避开权重 RL"的对照——HybridFlow 降 RL 训练成本、GEPA 直接绕过权重训练，两条路共同缓解 RL 样本昂贵痛点。
- **[[areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning]] — 大规模异步 RL 系统**：AREAL 用异步架构扩 RLVR 规模以应对长 rollout（仍是权重空间）。GEPA 论证此类规模化 RL 在样本效率上本质受限（仍需万级 rollouts）；AREAL 降的是单步成本，GEPA 降的是所需 rollout 数（35×）。二者代表"把 RL 做便宜" vs "不用 RL 也能涨"的两种哲学。
- **genealogy 定位**：GEPA 是 RL-vs-prompt-evolution 谱系中"反思式 prompt 进化可超越 RL"的对比分支代表（ICLR 2026 Oral），与上述 RL 路径（R1/Search-R1）与 RL 系统（HybridFlow/AREAL）形成"学习媒介"维度的对照系。其 Pareto illumination + 语言反馈也可作为 RL 系统的 prompt 侧增强（如 Ziems 2025 Multi-module GRPO 已在尝试组合 policy gradient 与 prompt optimization，论文 §6 显式引用）。

## 局限与边界

1. **非全胜——AIME（纯数学单步 CoT）GRPO 仍领先**（Qwen3 8B：GRPO 38 vs GEPA 32；GPT-4.1 Mini 上 GEPA 反超至 59.33）。GEPA 在单模块、可验证答案、纯推理链任务上 RL 仍有优势；强项是复合系统与含丰富 textual feedback 的任务。
2. **+Merge 超参敏感**：GPT-4.1 Mini 增益但 Qwen3 8B 反退化（IFBench 38.61→28.23、PUPA 91.85→86.26），merge 时机/预算分配需按模型调优，论文未给自适应方案。
3. **多数 rollout 预算耗在 validation**（Observation 1）：GEPA 总 budget 中 train-rollout 仅 79-737，validation 占大头（用于候选选择而非学习）。作者承认可在更小/动态 validation 子集上评测以进一步省——future work。
4. **反思 LM 自身成本与质量依赖**：GEPA 依赖一个强 reflection LM（meta-prompt Appendix C）；若用弱模型反思可能失效，论文未系统消融 reflection LM 能力影响（附录 J 只统计 reflection LM 调用次数）。
5. **推理时搜索仅 preliminary**（§5.1 自述 early results）：NPU/CUDA 实验用 cache 消除随机性，跨任务迁移机制需更多系统研究；代码生成外其他 domain 未验证。Figure 27（NPUEval 进化 prompt 全文）被引用但不在本文 16 张 caption 范围。
6. **对抗 prompt（§5.2）双刃**：可作 red-team，但也演示了 LLM 对无关 trivia+严格格式的脆弱性——GEPA 自身优化的 prompt 是否对此类对抗鲁棒未测。
7. **Pareto 选择开销随候选池与实例数增长**：Algorithm 2 每轮对所有实例建 Pareto 集、剔除被支配项，规模大时计算开销未讨论。
8. **公平性细节**：GEPA budget 按 MIPROv2 逐 benchmark 对齐（差异 ≤10.15%），但 GRPO 固定 24000 rollouts——与 GRPO 比较并非严格同 budget，而是论证"远少 budget 即超"。
9. **Trace/TextGrad 的 per-module feedback 不公平**：§E.4 承认 Trace/TextGrad 不支持 per-module feedback，fallback 用 BBH tutorial 格式——GEPA 享有更丰富的 feedback_text 通道，对比并非纯算法等条件。
