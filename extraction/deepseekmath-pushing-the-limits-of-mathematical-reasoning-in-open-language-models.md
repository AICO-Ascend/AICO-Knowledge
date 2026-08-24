---
paper_num: "22"
title: "DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models"
authors: "Reasoning in Open Language Models Zhihong Shao1,2∗†, Peiyi Wang1,3∗†, Qihao Zhu1,3∗†, Runxin Xu1, Junxiao Song1 Xiao Bi1, Haowei Zhang1, Mingchuan Zhang1, Y.K. Li1, Y. Wu1, Daya Guo1∗ 1DeepSeek-AI, 2Tsinghua University, "
date: "2026/1/19"
arxiv: "https://arxiv.org/abs/2402.03300"
pdf: "papers/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models.pdf"
slug: "deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models"
tags: []
---

# DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models

> [!abstract] 摘要（原文）
> 1\. 💡 DeepSeekMath 7B 是一个开放语言模型，通过在DeepSeek-Coder-Base-v1.5 7B基础上进行120B数学相关token的预训练，在MATH benchmark上实现了51.7%的Top1准确率，接近GPT-4和Gemini-Ultra的性能。 2. 🛠️ 模型的出色表现归因于从Common Crawl中精心筛选的120B高质量DeepSeekMath Corpus，以及引入了Group Relative Policy Optimization (GRPO)——一种无需critic模型的PPO变体，显著优化了强化学习资源消耗。 3. 🔬 论文还探讨了Code训练对数学推理的积极作用，并提出了一个统一的RL范式来分析不同算法，指出强化学习主要通过提升Maj@K来增强模型性能，而非直接提升其基础能力。

## 元信息
- **发表日期**: 2026/1/19
- **作者**: Reasoning in Open Language Models Zhihong Shao1,2∗†, Peiyi Wang1,3∗†, Qihao Zhu1,3∗†, Runxin Xu1, Junxiao Song1 Xiao Bi1, Haowei Zhang1, Mingchuan Zhang1, Y.K. Li1, Y. Wu1, Daya Guo1∗ 1DeepSeek-AI, 2Tsinghua University, 
- **arXiv**: https://arxiv.org/abs/2402.03300
- **本地 PDF**: `papers/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models.pdf`
- **页数**: 30

## 图表（原文 caption + 页码）

### Figure 1 (p.1) ⭐深度解读
![[assets/crops/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-fig01.png]]
*整页渲染: ![[assets/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-p01.png]]*
> [!quote] caption
> Top1 accuracy of open-source models on the competition-level MATH benchmark

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读（Figure 1）：**

该图以时间为横轴，展示开源模型在MATH竞赛级基准Top1准确率的变化：LLaMA1-65B约10.6%（2023初）→WizardMath约21%（2023末），并用三条水平参考线标示闭源前沿——GPT-4早期版约42%、GPT-4 API约50%、Gemini-Ultra约54%。虚线趋势显示开源进步明显但仍落后闭源达2–3倍差距。

作为论文**开篇动机图**，此图直观论证"开源模型在数学推理上仍未逼近前沿"这一核心问题，为后续提出DeepSeekMath填补这一能力缺口、突破开源数学推理上限的立题与实验链路提供必要的前提铺垫。

### Figure 2 (p.5) ⭐深度解读
![[assets/crops/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-fig02.png]]
*整页渲染: ![[assets/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-p05.png]]*
> [!quote] caption
> An iterative pipeline that collects mathematical web pages from Common Crawl.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图1解读：**

图示DeepSeekMath从Common Crawl采集数学网页的迭代流水线：①以种子数学语料训练fastText分类器；②从全网召回数学网页构建Math Corpus；③挖掘高密度数学域名；④新域名回灌至第②步形成闭环迭代。

**图2原文论点：**
通过"种子→分类器→域名发现"自举闭环，无需昂贵人工标注即可自动化、规模化地从无标注网页扩展高质量数学数据，验证数据规模与质量可兼得。

**图3链路作用：**
该流程产出120B token数学预训练语料，是DeepSeekMath-Base 7B训练的数据基石，并与下游GRPO强化学习协同，最终奠定模型数学推理的领先性能。

### Figure 3 (p.7) ⭐深度解读
![[assets/crops/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-fig03.png]]
*整页渲染: ![[assets/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-p07.png]]*
> [!quote] caption
> Benchmark curves of DeepSeek-LLM 1.3B trained on different mathematical corpora.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图3 联合解读**

**核心对象与结构**：四个子图横向对比DeepSeek-LLM 1.3B在四种语料（MathPile蓝、OpenWebMath橙、Proof-Pile-2绿、DeepSeekMath Corpus红）上、训练0–150B tokens期间，在GSM8K、MATH、CMATH、BBH四项基准的准确率曲线。

**关键数据**：
- GSM8K：DeepSeekMath Corpus攀升至约22–23%，其余仅12–14%，MathPile几乎停滞于2%。
- MATH：DeepSeekMath Corpus达~13–14%，OpenWebMath/Proof-Pile-2约10%，MathPile保持~3%。
- CMATH：DeepSeekMath Corpus达~44–45%，OpenWebMath/Proof-Pile-2仅~18%，MathPile趋近于0。
- BBH：差距收窄，DeepSeekMath Corpus约34%，最低约25%。

**论证结论**：DeepSeekMath Corpus在数学推理任务上显著优于现有开源数学语料库，且随训练量持续提升，验证其数据质量与构建方法的有效性。

**在论文中的作用**：该实验链路中"语料对比"环节的关键可视化证据，为后续基于该语料训练DeepSeekMath 7B并取得SOTA提供数据层面的合法性支撑。

### Figure 4 (p.13) ⭐深度解读
![[assets/crops/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-fig04.png]]
*整页渲染: ![[assets/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-p13.png]]*
> [!quote] caption
> Demonstration of PPO and our GRPO. GRPO foregoes the value model, instead

> [!tip] 技术解读（多模态）
> 【图文联合解读】图分上下两部分对比PPO与GRPO流程。PPO由策略模型对问题q采样单输出o，经Reference（KL）、Reward（r）、Value（v）三模型后用GAE计算优势A；GRPO对同一q采样G个输出{o₁…o_G}，仅用Reference与Reward，通过Group Computation由组内奖励{r₁…r_G}直接生成{A₁…A_G}，彻底取消Value模型。颜色上黄色为训练模型、蓝色为冻结模型。该图论证GRPO以组分数统计量替代Value基线，可显著节省显存与算力，构成论文RLHF训练阶段的方法基础。

### Figure 5 (p.19) ⭐深度解读
![[assets/crops/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-fig05.png]]
*整页渲染: ![[assets/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-p19.png]]*
> [!quote] caption
> Performance of the DeepSeekMath-Instruct 1.3B model, which was further trained

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

该图为 DeepSeekMath-Instruct 1.3B 模型在 GSM8K 基准上、采用不同方法继续训练 0–9000 步的准确率曲线对比。可见至少四条曲线：

- **蓝色方法**表现最佳，从约 56.5% 上升至 ~65–66%；
- **橙色方法**次之，最终达 ~64%；
- **Online RFT（绿色）**波动较大，由 ~56.5% 提升至 ~62–63%；
- **RFT（紫色）**几乎停滞，长期徘徊在 59–60%。

**关键结论**：原文据此论证——在 SFT 模型基础上，单纯的离线 RFT 已接近性能天花板（甚至饱和），而引入在线探索/采样的方法（如 Online RFT 及更强变体）能持续突破上限，验证了"在线强化"对数学推理进一步提升的必要性。

**论文链路作用**：该图作为消融/方法对比证据，支撑论文主张的 GRPO 等在线策略优于 RFT 的核心论点，衔接其整体方法（监督 → RFT → Online RFT/GRPO）的演进叙事。

### Figure 6 (p.20) ⭐深度解读
![[assets/crops/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-fig06.png]]
*整页渲染: ![[assets/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-p20.png]]*
> [!quote] caption
> Performance of iterative reinforcement learning with DeepSeekMath-Instruct 7B on

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

该图展示 DeepSeekMath-Instruct 7B 在 GSM8K 与 MATH 上三轮迭代 RL 的训练曲线（步数 0–5300）。GSM8K 准确率从 Iteration-0 起点 ~83% 提升至 ~86%，Iteration-1 起步 ~87%、峰值 ~88%，Iteration-2 起步 ~87%、峰值 ~89%；MATH 从 ~46.8% 经 ~49% 升至 ~50.5%，三轮峰值均逼近 52%。

核心结论：**每轮迭代起点显著高于上一轮末值，证明 RL 切实带来能力提升；但迭代间增益边际递减**（GSM8K 仅 +1–1.5pp，MATH 仅 +1.5–2pp）。

方法链作用：该图为"为何需要 GRPO+迭代 SFT 融合"提供经验依据——纯迭代 RL 收益趋缓、且训练步数逐轮增加（3000→5000+），论文据此提出用新 SFT 数据重置 RL 起点，突破 RL 自身天花板。

### Figure 7 (p.21) ⭐深度解读
![[assets/crops/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-fig07.png]]
*整页渲染: ![[assets/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-p21.png]]*
> [!quote] caption
> The Maj@K and Pass@K of SFT and RL DeepSeekMath 7B on GSM8K and MATH

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图示 GSM8K 上 Maj@K 与 Pass@K 随候选数 K（1→64，温度 0.7）的变化：Maj@K-Instruct（紫，81.5%→89.6%）与 Maj@K-RL（橙，88%→91%）在 K≥8 后趋于平台；Pass@K-Instruct（蓝，88.2%→97.4%）与 Pass@K-RL（绿，81.5%→99.2%）随 K 陡升。原文据此论证：**RL 显著提升 Maj@K**（橙高于紫约 1.4 个百分点），但对 Pass@K 无明显增益，说明 RL 改善的是多数投票的可靠性，而非单条解的正确率或解空间覆盖。该图是论文揭示"RL 主要强化自一致投票稳定性"这一核心增益模式的关键证据。

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.6) ⭐深度解读
![[assets/crops/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-tab01.png]]
> [!quote] caption
> | Performance of DeepSeek-LLM 1.3B trained on different mathematical corpora, evalu- ated using few-shot chain-of-thought prompting. Corpus sizes are calculated using our tokenizer with a vocabulary size of 100K.

> [!tip] 表格解读（多模态）
> 【图文联合解读】表1对比DeepSeek-LLM 1.3B在五种语料（含120.2B tokens的DeepSeekMath Corpus及Proof-Pile-2 51.9B、OpenWebMath 13.6B、MathPile 8.9B、无数学预训练基线）下8项基准（GSM8K、MATH、OCW、SAT、MMLU STEM、CMATH、Gaokao两套）的few-shot CoT准确率。DeepSeekMath语料以GSM8K 23.8%、MATH 13.6%、SAT 56.3%、CMATH 41.5%等全面领先，体量更小的Proof-Pile-2仅GSM8K 14.3%、MATH 11.2%。该表作为论文方法链路起点，验证其120B数学语料质量优于既有开源方案，为后续SFT/RL训练DeepSeekMath-RL奠定数据基座。

### Table 2 (p.8) ⭐深度解读
![[assets/crops/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-tab02.png]]
> [!quote] caption
> | Comparisons between DeepSeekMath-Base 7B and strong base models on English and Chinese mathematical benchmarks. Models are evaluated with chain-of-thought prompting. Minerva results are quoted from Lewkowycz et al. (2022a).

> [!tip] 表格解读（多模态）
> 【图文联合解读】**表2图文联合解读**

表2在8项英中数学基准（GSM8K / MATH / CollegeMath / CMATH / MGSM-zh / Gaokao-Math / AGIEval-Math-zh / CEval-Math）上以CoT评测，分两组：闭源Minerva 7B/62B/540B；开源Mistral 7B、Llemma 7B/34B与**DeepSeekMath-Base 7B**。

**关键数据**：DeepSeekMath-Base 7B以**64.2%、36.2%、15.4%、84.4%、56.5%、71.7%、20.3%、35.3%**全部加粗领先开源模型；其中英文GSM8K(64.2% vs 58.8%)与MATH(36.2% vs 33.6%)两项甚至**反超**参数规模大77倍的Minerva 540B，中文基准同样全面领先Llemma 34B。

**论证作用**：该表是全文核心实验证据——为Figure 2"数学网页迭代采集管线"的有效性背书：仅靠高质量数据+继续预训练，7B开源模型即可逼近/超越闭源专用数学大模型，支撑"开源可追平闭源"的核心论点。

### Table 3 (p.9) ⭐深度解读
![[assets/crops/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-tab03.png]]
> [!quote] caption
> | Few-shot evaluation of base models’ ability to solve mathematical problems using tools and the ability to conduct informal-to-formal theorem proving in Isabelle.

> [!tip] 表格解读（多模态）
> 【图文联合解读】该表横向对比 6 个基础模型（含 7B/34B 两种规格）在 4 项 Few-shot 任务上的得分：GSM8K+Python、MATH+Python、miniF2F-valid、miniF2F-test。DeepSeekMath-Base 7B 以 66.9% / 31.4% / 25.8% / 24.6% 全面领先，同时优于 Llemma 34B（64.6%/26.3%/21.0%/21.3%）和 CodeLlama 34B（52.7%/23.5%/18.5%/18.0%），而其参数量仅为其约 1/4–1/5。

关键结论：仅 7B 规模便在"工具辅助解题"与"Isabelle 非形式→形式定理证明"两类任务上同时超越更大对手，证明高质量数学专用预训练语料可有效替代纯规模扩张。

在论文中的作用：作为基础模型能力基线评估的核心证据，佐证"数据驱动优于模型缩放"的方法论主张，为后续 RL 与 SFT 阶段提供强起点。

### Table 4 (p.9) ⭐深度解读
![[assets/crops/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-tab04.png]]
> [!quote] caption
> | Evaluation on natural language understanding, reasoning, and code benchmarks. DeepSeek-Coder-Base-v1.5 † is the checkpoint right before learning rate decay, which is used to train DeepSeekMath-Base. On MMLU and BBH, we use few-shot chain-of-thought prompting. On HumanEval and MBPP, we evaluate mod

> [!tip] 表格解读（多模态）
> 【图文联合解读】**注意**：原文引用段落实际讲解的是 Figure 4（GRPO 示意图），并非 Table 4，故以下解读依据表格图像及 caption。

**核心数据**：对比 4 个 7B 模型在 MMLU、BBH、HumanEval、MBPP 上的表现。Mistral 在 MMLU 最高（62.4%）但代码能力弱（HumanEval 28.0%）；DeepSeekMath-Base 在 BBH 最高（59.5%），MMLU 达 54.9%，相比其训练起点 DeepSeek-Coder-Base-v1.5† 分别提升 +12.0 与 +16.6 个百分点；代码指标较 v1.5 略降（HumanEval 43.2%→40.9%，MBPP 60.4%→52.6%）。

**论证结论**：数学专项训练未损害通用理解/推理能力，反而相对基座大幅增强；代码能力仅小幅回落，证明知识遗忘可控。

**论文链路作用**：作为"实验链路"中的能力保留性证据，支撑后续 GRPO 强化学习训练所选基座（DeepSeekMath-Base）的合理性，说明从代码基座经数学继续预训练得到的模型具备均衡的综合能力。

### Table 5 (p.12) ⭐深度解读
![[assets/crops/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-tab05.png]]
> [!quote] caption
> | Performance of Open- and Closed-Source models with both Chain-of-Thought and Tool-Integrated Reasoning on English and Chinese Benchmarks. Scores in gray denote majority votes with 32 candidates; The others are Top1 scores. DeepSeekMath-RL 7B beats all open- source models from 7B to 70B, as well as

> [!tip] 表格解读（多模态）
> 【图文联合解读】Table 5 对比开源/闭源模型在 CoT 与 TIR 两种范式下于 GSM8K、MATH 及中文基准的 Top1 成绩（灰字为 32 候选 majority vote）。

**核心数据**：DeepSeekMath-RL 7B 在 CoT 下取得 88.2%/51.7%/79.6%/88.8%，TIR 下取得 86.7%/58.8%/78.4%/87.6%，全面超越 7B–70B 开源模型（如 MetaMath 70B 仅 82.3%/26.6%）及多数闭源模型，仅弱于 GPT-4 与 Gemini Ultra。

**技术结论**：仅以 GSM8K 与 MATH 的 CoT 数据做 RL 微调，RL 版即在所有基准上稳定优于 Instruct 版（如 MATH 由 46.8%→51.7%、CMath 由 73.2%→79.6%），证明 GRPO 显著提升数学推理及跨任务、跨语种泛化能力。

**论文作用**：与 Figure 5 消融互补，构成"方法→结果"的主实验证据链，支撑"7B 开源模型以低成本超越大模型"的核心论点。

### Table 6 (p.16) ⭐深度解读
![[assets/crops/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-tab06.png]]
> [!quote] caption
> | Investigation of how code affects mathematical reasoning under different training settings. We experiment with DeepSeek-LLM 1.3B, and evaluate its mathematical reasoning performance without and with tool use via few-shot chain-of-thought prompting and few-shot program-of-thought prompting, respect

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读**

该表以 DeepSeek-LLM 1.3B 为基座，对比"无继续训练、两阶段（General/Code→Math）、单阶段（Math 或 Code+Math 混合）"五类设置，在 GSM8K/MATH/CMATH 三个基准上"无工具（CoT）"与"有工具（PoT+Python）"的准确率。关键数据：两阶段"Code→Math"无工具推理最高（21.9%/15.3%/39.7%），证明代码预训练显著增强纯链式数学推理；Code+Math 混合训练在有工具下最优（19.7%/13.5%），表明代码与数学混合最利于 Python 工具调用。该消融为论文核心论点——"代码数据是数学预训练的关键要素"——提供量化依据，直接支撑 DeepSeekMath-Base 数据配比及"先代码后数学"两阶段训练流程的设计。

### Table 7 (p.17) ⭐深度解读
![[assets/crops/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-tab07.png]]
> [!quote] caption
> | Investigation of how different settings of code and math training affect model perfor- mance of language understanding, reasoning, and coding. We experiment with DeepSeek-LLM 1.3B. We evaluate the models on MMLU and BBH using few-shot chain-of-thought prompting. On HumanEval and MBPP, we conduct z

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 7 解读**

**1) 核心对象与数据**：以 DeepSeek-LLM 1.3B 与 DeepSeek-Coder-Base-v1.5 7B 为基座，对比三种训练设置（无数学训练 / MathPile / ArXiv-RedPajama）在中英文基准上的表现。其中 Coder 7B 无数学训练即达 GSM8K 29.0%、MATH 12.5%、CMATH 45.9%，远超 1.3B 的 2.9%/3.0%/12.3%；加入 MathPile 或 ArXiv 数据后，多数指标不升反降（Coder GSM8K 降至 23.6%/28.1%）。

**2) 关键技术结论**：单纯堆砌数学网页语料对数学推理提升有限甚至有害，而代码预训练却带来显著增益，说明代码能力对数学推理迁移更有效。

**3) 论文链路作用**：为 DeepSeekMath 数据策略提供消融依据——否定"增大通用数学语料"的路径，转而强调数据质量与精选的重要性。

### Table 8 (p.17) ⭐深度解读
![[assets/crops/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-tab08.png]]
> [!quote] caption
> | Effect of math training on different arXiv datasets. Model performance is evaluated with few-shot chain-of-thought prompting.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 8 解读**

**结构数据**：对比 1.3B DeepSeek-LLM 与 7B DeepSeek-Coder-Base-v1.5 在三种训练条件（无数学训练 / MathPile / ArXiv-RedPajama）下，于 GSM8K、MATH、OCW、SAT、MMLU STEM 及 CMATH、Gaokao 等中英文 8 个基准上的 few-shot CoT 表现。

**关键结论**：仅用现有 MathPile 或 ArXiv-RedPajama 等数学语料继续训练，相较无数学训练基线（如 7B 模型 GSM8K 29.0%→23.6%/28.1%，MMLU STEM 38.1%→35.8%/35.2%）整体无明显增益，甚至部分指标下降，说明通用数学语料存在噪声大、质量参差的问题。

**论文作用**：作为数据构建章节的动机实验，论证了"直接抓取数学数据不足以提升推理能力"，为后续 DeepSeekMath 设计基于 LLM 评分与去重的高质量数据 pipeline 提供必要性支撑。

### Table 9 (p.17) ⭐深度解读
![[assets/crops/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-tab09.png]]
> [!quote] caption
> | Effect of math training on different arXiv corpora, the base model being DeepSeek- Coder-Base-v1.5 7B. We evaluate informal-to-formal proving in Isabelle.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 9 图文联合解读**

该表以 DeepSeek-Coder-Base-v1.5 7B 为基座，对比了三种 arXiv 语料在 Isabelle "informal-to-formal" 证明任务（miniF2F valid/test）上的表现：无数学训练 20.1%/21.7%，加入 MathPile 后反而降至 16.8%/16.4%，ArXiv-RedPajama 进一步掉到 14.8%/11.9%。

**关键结论**：通用 arXiv 数学语料预训练对形式化证明任务呈**负向作用**，非形式数学推理能力无法迁移到 Isabelle 形式证明，甚至可能损害模型原有的代码/逻辑能力。

**论文作用**：该消融结果为作者的核心方法论（精细的数学数据筛选与处理管线）提供了反面动机——证明单纯堆叠未加工的网络数学语料不可行，从而支撑其后提出的高质量数据构建策略与整体训练链路。

### Table 10 (p.19) ⭐深度解读
![[assets/crops/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-tab10.png]]
> [!quote] caption
> | The data source and gradient coefficient of different methods. 𝑃 𝑠𝑓𝑡 denotes the data distribution of supervised fine-tuning datasets. 𝜋 𝜃 𝑠𝑓𝑡 and 𝜋 𝜃 denote the supervised fine-tuned model and the real-time policy model during the online training process, respectively.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图像与 caption 不匹配提示**：caption 描述的是"各方法的数据来源与梯度系数对比表"（涉及 P_sft、π_θ_sft、π_θ 等符号），但实际呈现的是 **RFT、Online RFT、GRPO+OS、GRPO+PS 四种方法在 GSM8K 与 MATH 上的训练准确率曲线**（横轴 0–~9000 steps），并非表格。以下按图像实际内容解读：

1) **结构/量化数据**：GSM8K 面板——GRPO+PS（蓝）峰值约 66%，GRPO+OS（橙）约 64%，Online RFT（绿）约 62%，RFT（紫）约 60%；MATH 面板——GRPO+PS 约 30%，GRPO+OS 约 29.5%，Online RFT 约 29%，RFT 约 28%。

2) **关键结论**：四条曲线在两基准上排序一致（PS > OS > Online RFT > RFT），证明采用**实时策略 π_θ 采样 + 拒绝式微调**的 GRPO+PS 训练效率与最终性能最优。

3) **链路作用**：该曲线图为论文 GRPO 改进路线（PS/OS/RFT 消融）提供**训练动态证据**，支撑"在线策略采样优于离线 SFT 数据"的核心方法论主张。

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\footnotesize \mathcal{J}_{PPO}(\theta) = \mathbb{E}{[q \sim P(Q), o \sim \pi_{\theta_{old}}(O|q)]} \frac{1}{|o|} \sum_{t=1}^{|o|} \min \left[ \frac{\pi_\theta(o_{t} | q, o_{<t})}{\pi_{\theta_{old}}(o_{t} | q, o_{<t})} A_{t}, \text{clip} \left( \frac{\pi_\theta(o_{t} | q, o_{<t})}{\pi_{\theta_{old}}(o_{t} | q, o_{<t})}, 1 - \epsilon, 1 + \epsilon \right) A_{t} \right] ,
$$

$$
r_{t} = r_\phi(q, o_{\le t}) - \beta \log\frac{\pi_{\theta}(o_{t}|q, o_{<t})}{\pi_{ref}(o_{t}|q, o_{<t})},
$$

$$
\footnotesize \begin{split} \mathcal{J}_{GRPO}(\theta) &= \mathbb{E}{[q \sim P(Q), \{o_i\}_{i=1}^G \sim \pi_{\theta_{old}}(O|q)]} \\ & \frac{1}{G}\sum_{i=1}^G\frac{1}{|o_i|} \sum_{t=1}^{|o_i|} \left\{ \min \left[ \frac{\pi_\theta(o_{i,t} | q, o_{i,<t})}{\pi_{\theta_{old}}(o_{i,t} | q, o_{i,<t})} \hat{A}_{i,t}, \text{clip} \left( \frac{\pi_\theta(o_{i,t} | q, o_{i,<t})}{\pi_{\theta_{old}}(o_{i,t} | q, o_{i,<t})}, 1 - \epsilon, 1 + \epsilon \right) \hat{A}_{i,t} \right] - \beta \mathbb{D}_{KL}\left[\pi_{\theta} || \pi_{ref}\right]\right\} , \end{split}
$$

$$
\small \mathbb{D}_{KL}\left[\pi_{\theta} || \pi_{ref}\right] = \frac{\pi_{ref}(o_{i,t}|q,o_{i,<t})}{\pi_{\theta}(o_{i,t}|q,o_{i,<t})}- \log\frac{\pi_{ref}(o_{i,t}|q,o_{i,<t})}{\pi_{\theta}(o_{i,t}|q,o_{i,<t})} - 1,
$$

$$
\nabla_{\theta}\mathcal{J}_{\textcolor{red}{\mathcal{A}}}(\theta) = \mathbb{E}[\underbrace{(q,o) \sim \textcolor{red}{\mathcal{D}}}_{Data \ Source}]\left( \frac{1}{|o|} \sum_{t=1}^{|o|} \underbrace{GC_{{\mathcal{A}}}(q, o, t, \textcolor{red}{\pi_{{rf}}})}_{Gradient \ Coefficient} \nabla_{\theta}\log \pi_{\theta}(o_t | q, o_{<t})\right).
$$

$$
\mathcal{J}_{SFT}(\theta)=\mathbb{E}[q, o \sim P_{sft}(Q, O)]\left(\frac{1}{|o|}\sum_{t=1}^{|o|} \log \pi_\theta(o_t | q, o_{<t})\right).
$$

$$
\nabla_{\theta}\mathcal{J}_{SFT} = \mathbb{E}[q, o \sim P_{sft}(Q, O)]\left(\frac{1}{|o|}\sum_{t=1}^{|o|} \nabla_{\theta} \log \pi_\theta(o_{t} | q, o_{<t})\right).
$$

$$
\mathcal{J}_{RFT}(\theta)= \mathbb{E}[q \sim P_{sft}(Q), o \sim \pi_{sft}(O|q)]\left( \frac{1}{|o|}\sum_{t=1}^{|o|} \mathbb{I}(o) \log \pi_\theta(o_{t} | q, o_{<t})\right).
$$

$$
\nabla_{\theta}\mathcal{J}_{RFT}(\theta)= \mathbb{E}[{q \sim P_{sft}(Q), o \sim \pi_{sft}(O|q)}]\left( \frac{1}{|o|}\sum_{t=1}^{|o|} {\mathbb{I}(o)} \nabla_{\theta}\log \pi_\theta(o_{t} | q, o_{<t})\right).
$$

$$
GC_{RFT}(q, o, t) = \mathbb{I}(o)=\left\{ \begin{aligned} 1 & & {\rm the \ answer \ of \ o \ is \ correct} \\ 0 & & {\rm the \ answer \ of \ o \ is \ incorrect} \\ \end{aligned} \right.
$$

$$
\nabla_{\theta}\mathcal{J}_{OnRFT}(\theta)= \mathbb{E}[{q \sim P_{sft}(Q), o \sim \pi_{\theta}(O|q)}]\left( \frac{1}{|o|}\sum_{t=1}^{|o|} {\mathbb{I}(o)} \nabla_{\theta}\log \pi_\theta(o_{t} | q, o_{<t})\right).
$$

$$
\footnotesize \begin{split} \mathcal{J}_{DPO}(\theta) = \mathbb{E}{[q \sim P_{sft}(Q), o^+, o^- \sim \pi_{sft}(O|q)]} \log \sigma \left( \beta \frac{1}{|o^+|}\sum_{t=1}^{|o^+|} \log \frac{\pi_{\theta}(o^+_t | q, o^+_{<t})}{\pi_{\text{ref}}(o^+_t | q, o^+_{<t})} - \beta \frac{1}{|o^-|}\sum_{t=1}^{|o^-|} \log \frac{\pi_{\theta}(o^-_{<t} | q, o^-_{<t})}{\pi_{\text{ref}}(o^-_{<t} | q,o^-_{<t})} \right) \end{split}
$$

$$
\footnotesize \begin{split} \nabla_{\theta}\mathcal{J}_{DPO}(\theta) = \mathbb{E}{[q \sim P_{sft}(Q), o^+, o^- \sim \pi_{sft}(O|q)]} & \left( \frac{1}{|o^+|}\sum_{t=1}^{|o^+|} GC_{DPO} (q,o,t) \nabla_{\theta}\log\pi_{\theta}(o^+_t | q, o^+_{<t}) \right. \\ - & \left. \frac{1}{|o^-|}\sum_{t=1}^{|o^-|} GC_{DPO} (q,o,t) \nabla_{\theta}\log\pi_{\theta}(o^-_t | q, o^-_{<t}) \right) \end{split}
$$

$$
\footnotesize GC_{DPO}(q,o,t) = \sigma\left(\beta\log \frac{\pi_{\theta}(o^-_t | q, o^-_{<t})}{\pi_{\text{ref}}(o^-_t | q, o^-_{<t})} - \beta\log \frac{\pi_{\theta}(o^+_t | q, o^+_{<t})}{\pi_{\text{ref}}(o^+_t | q, o^+_{<t})}\right)
$$

$$
\footnotesize \mathcal{J}_{PPO}(\theta) = \mathbb{E}{[q \sim P_{sft}(Q), o \sim \pi_{\theta_{old}}(O|q)]} \frac{1}{|o|} \sum_{t=1}^{|o|} \min \left[ \frac{\pi_\theta(o_{t} | q, o_{<t})}{\pi_{\theta_{old}}(o_{t} | q, o_{<t})} A_{t}, \text{clip} \left( \frac{\pi_\theta(o_{t} | q, o_{<t})}{\pi_{\theta_{old}}(o_{t} | q, o_{<t})}, 1 - \epsilon, 1 + \epsilon \right) A_{t} \right].
$$

$$
\footnotesize \begin{split} \nabla_{\theta}\mathcal{J}_{PPO}(\theta) = \mathbb{E}{[q \sim P_{sft}(Q), o \sim \pi_{\theta_{old}}(O|q)]} \frac{1}{|o|} \sum_{t=1}^{|o|} A_t \nabla_{\theta}\log \pi_\theta(o_{t} | q, o_{<t}) \end{split}
$$

$$
GC_{PPO}(q, o, t, \pi_{\theta_{rm}}) = A_t,
$$

$$
\footnotesize \begin{split} \mathcal{J}_{GRPO}(\theta) &= \mathbb{E}{[q \sim P_{sft}(Q), \{o_i\}_{i=1}^G \sim \pi_{\theta_{old}}(O|q)]} \\ & \frac{1}{G}\sum_{i=1}^G\frac{1}{|o_i|} \sum_{t=1}^{|o_i|} \left[\frac{\pi_\theta(o_{i,t} | q, o_{i,<t})}{\pi_{\theta_{old}}(o_{i,t} | q, o_{i,<t})} \hat{A}_{i,t} - \beta (\frac{\pi_{ref}(o_{i,t}|q,o_{i,<t})}{\pi_{\theta}(o_{i,t}|q,o_{i,<t})}- \log\frac{\pi_{ref}(o_{i,t}|q,o_{i,<t})}{\pi_{\theta}(o_{i,t}|q,o_{i,<t})} - 1)\right]. \end{split}
$$

$$
\footnotesize \begin{split} \nabla_{\theta}\mathcal{J}_{GRPO}(\theta) & = \mathbb{E}{[q \sim P_{sft}(Q), \{o_i\}_{i=1}^G \sim \pi_{\theta_{old}}(O|q)]} \\ & \frac{1}{G}\sum_{i=1}^G\frac{1}{|o_i|} \sum_{t=1}^{|o_i|} \left[\hat{A}_{i,t} + \beta \left(\frac{\pi_{ref}(o_{i,t}|o_{i,<t})}{\pi_{\theta}(o_{i,t}|o_{i,<t})} - 1\right)\right] \nabla_{\theta}\log \pi_\theta(o_{i,t} | q, o_{i,<t}). \end{split}
$$

$$
\footnotesize GC_{GRPO}(q, o, t, \pi_{\theta_{rm}}) = \hat{A}_{i,t} + \beta \left(\frac{\pi_{ref}(o_{i,t}|o_{i,<t})}{\pi_{\theta}(o_{i,t}|o_{i,<t})} - 1\right),
$$

## 技术点深读（DEEP）

![[deep/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models.txt`（81353 字符）供引用检索。