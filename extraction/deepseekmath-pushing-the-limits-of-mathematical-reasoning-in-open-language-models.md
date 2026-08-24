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
> 【图文联合解读】图1展示2023-02至2024-01开源模型MATH Top@1走势：LLaMA1-65B（10.6%）→WizardMath-70B（22%）→Qwen-14B（24.5%）→Mistral-7B（28.5%）→Llemma-34B（31.5%）→Qwen-72B（35.2%），DeepSeekMath-7B（红星）跃至51.7%，超越GPT-4早期版（42.5%），逼近GPT-4 API与Gemini-Ultra（≈52–53%）。

原文以此论证：仅用7B参数与高质量数学语料即可匹敌百亿级闭源模型，验证"数据/方法杠杆≫纯扩模型"。

该图为论文开篇锚定DeepSeekMath-7B的性能标杆，并衔接表1（语料消融）与后续方法/实验论证链。

### Figure 2 (p.5) ⭐深度解读
![[assets/crops/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-fig02.png]]
*整页渲染: ![[assets/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-p05.png]]*
> [!quote] caption
> An iterative pipeline that collects mathematical web pages from Common Crawl.

> [!tip] 技术解读（多模态）
> 【图文联合解读】图示从Common Crawl 400亿HTML页面中迭代挖掘数学网页的闭环流程：①训练FastText分类器→②召回数学相关网页→③发现数学相关新域名→④人工标注URL路径，结果回灌Math Seed并循环。原文借此论证"种子扩充→分类器更准→召回更全→新域被发现"的自我增强数据飞轮机制。该管道为DeepSeekMath-Base 7B产出120B token级高质量数学预训练语料，是Table 2中数学推理性能领先的关键数据基础，串联起"数据-训练-评测"全链路。

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
> 【图文联合解读】**图文联合解读**

图分上下两栏对比 PPO 与 GRPO 流程。PPO（上）含策略、参考、奖励、价值四个模型，对问题 *q* 生成单输出 *o*，由奖励模型与 KL 计算得 *r*、价值模型得 *v*，再经 GAE 输出优势 *A*；GRPO（下）省去价值模型，对同一 *q* 采样 *G* 个输出（*o*₁…*o*_G），仅用参考模型计算 KL、奖励模型打分 *r*₁…*r*_G，由 "Group Computation" 以组内分数均值作基线直接生成 A₁…A_G。

**关键论证**：GRPO 以组内相对奖励替代逐状态价值估计，省去价值模型，显存/算力显著降低，且更契合数学题"一题多解"的群体奖励特性。

**论文作用**：该图是方法链路核心，直观支撑 DeepSeekMath 在 RL 阶段采用 GRPO 而非 PPO 的设计选择，为后续 R1-Zero 式实验提供算法依据。

### Figure 5 (p.19) ⭐深度解读
![[assets/crops/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-fig05.png]]
*整页渲染: ![[assets/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-p19.png]]*
> [!quote] caption
> Performance of the DeepSeekMath-Instruct 1.3B model, which was further trained

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图5图文联合解读**

**对象**：DeepSeekMath-Instruct 1.3B经四种方法（RFT/Online RFT/GRPO+OS/GRPO+PS）继续训练约9000步，在GSM8K（左，56–66%）与MATH（右，27–30.5%）上的准确率（Acc）随训练步数曲线。

**量化对比**：GRPO+PS（蓝）在两基准全程领先——GSM8K峰值≈65.5%（约5000–7000步），MATH峰值≈30.5%（约4000–5000步）；GRPO+OS（橙）次之（约64% / 30%）；Online RFT（绿）波动较大但仍有提升（约62% / 29%）；离线RFT（紫）全程近乎停滞，GSM8K稳定在60%附近、MATH仅约28%。

**论证作用**：该消融实验证明，在线GRPO算法显著优于传统拒绝采样微调，且PS（正例策略）带来稳定增益。它直接支撑论文最终选用GRPO作为RL主干方法，构成"SFT→GRPO强化学习"方法链路中的关键实证环节。

### Figure 6 (p.20) ⭐深度解读
![[assets/crops/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-fig06.png]]
*整页渲染: ![[assets/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-p20.png]]*
> [!quote] caption
> Performance of iterative reinforcement learning with DeepSeekMath-Instruct 7B on

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图6联合解读**

该图展示DeepSeekMath-Instruct 7B在GSM8K（左）与MATH（右）两个基准上三次迭代RL的准确率-训练步数曲线。

**具体数据**：GSM8K上，迭代0从约82.8%升至约87%后回落至约86%；迭代1在87–88%区间波动并出现约88.2%峰值；迭代2稳步攀升至约89%。MATH上，迭代0从约46.8%升至约50%后回落至约49%；迭代1峰值约52.3%；迭代2稳定在约51.5%。三条曲线呈"迭代2≥迭代1≥迭代0"的单调递进，未见饱和迹象。

**关键结论**：论文据此论证GRPO迭代强化学习可在SFT基础上持续获得稳定增益（约+6.2点GSM8K、约+5.5点MATH）。

**链路作用**：作为RL阶段核心实证，验证论文"用当前最优策略生成新SFT数据→再启动下一轮RL"的闭环有效性，是支撑整个两阶段迭代训练范式的关键证据。

### Figure 7 (p.21) ⭐深度解读
![[assets/crops/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-fig07.png]]
*整页渲染: ![[assets/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-p21.png]]*
> [!quote] caption
> The Maj@K and Pass@K of SFT and RL DeepSeekMath 7B on GSM8K and MATH

> [!tip] 技术解读（多模态）
> 【图文联合解读】图示温度0.7的DeepSeekMath‑7B：K=1至64时，Instruct（SFT）与RL在GSM8K、MATH上的Maj/Pass。RL使Maj@64由约89.5%升至91.0%、59.8%升至60.8%；Pass@64却由99.0%降至97.3%、87.0%降至86.2%，其余K优势不稳定。说明RL强化高共识答案、改善多数投票，却未提升至少一次命中的概率。该图处于SFT→RL→多样本评测链，检验后训练优化的是答案收敛还是候选覆盖。

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.6) ⭐深度解读
![[assets/crops/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-tab01.png]]
> [!quote] caption
> | Performance of DeepSeek-LLM 1.3B trained on different mathematical corpora, evalu- ated using few-shot chain-of-thought prompting. Corpus sizes are calculated using our tokenizer with a vocabulary size of 100K.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 1 联合解读**

1) **对象与数据**：以 DeepSeek-LLM 1.3B 为基模型，对比在 5 种数学语料（No Training / MathPile 8.9B / OpenWebMath 13.6B / Proof-Pile-2 51.9B / DeepSeekMath Corpus **120.2B tokens**）下 8 项基准（英文 GSM8K、MATH、OCW、SAT、MMLU STEM；中文 CMATH、Gaokao MathCloze、MathQA）的少样本 CoT 准确率。结果显示 DeepSeekMath Corpus **全部 8 项均最优**：GSM8K 23.8%、MATH 13.6%、CMATH 41.5%、Gaokao MathQA 23.6%，相对无数学训练基线（2.9%/3.0%）提升 4–8 倍。

2) **关键结论**：数据规模与质量并重——仅靠增大语料（Proof-Pile-2 51.9B）提升有限，而 DeepSeekMath Corpus 以约 2.3× 于 Proof-Pile-2 的体量取得显著优势，证明其筛选与去重策略有效。

3) **论文作用**：作为核心动机实验，为后续 DeepSeekMath 7B 训练及整套数据构建方法（迭代分类、网页转换、去重）提供经验支撑。

### Table 2 (p.8) ⭐深度解读
![[assets/crops/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-tab02.png]]
> [!quote] caption
> | Comparisons between DeepSeekMath-Base 7B and strong base models on English and Chinese mathematical benchmarks. Models are evaluated with chain-of-thought prompting. Minerva results are quoted from Lewkowycz et al. (2022a).

> [!tip] 表格解读（多模态）
> 【图文联合解读】该表横向对比 DeepSeekMath-Base 7B 与闭源 Minerva（7B/62B/540B）以及开源 Mistral 7B、Llemma（7B/34B）在 4 个英文+4 个中文数学基准上的 CoT 表现。数据显示：DeepSeekMath-Base 7B 以 64.2%、36.2%、15.4%、84.4%、56.5%、71.7%、20.3%、35.3%（全部加粗）在 8 个基准上同时刷新 SOTA——全面超越参数约 77 倍的 Minerva 540B（最高 63.9%）和 5 倍大的 Llemma 34B（最高 56.1%）。论文借此论证"高质量数学预训练语料可大幅压缩模型参数差距"，该表是整条方法链路的"基座证明"，为后续指令微调（SFT）与 RL 阶段提供起点并锚定性能上限。

### Table 3 (p.9) ⭐深度解读
![[assets/crops/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-tab03.png]]
> [!quote] caption
> | Few-shot evaluation of base models’ ability to solve mathematical problems using tools and the ability to conduct informal-to-formal theorem proving in Isabelle.

> [!tip] 表格解读（多模态）
> 【图文联合解读】该表少样本评测6个基座模型，分两类任务：「带Python工具解题（GSM8K/MATH）」与「Isabelle形式化证明（miniF2F）」。核心数据：DeepSeekMath-Base 7B以66.9%/31.4%/25.8%/24.6%四指标全面领跑，分别超过Llemma-34B（64.6%/26.3%/21.0%/21.3%），并碾压Mistral 7B与两档CodeLlama。论文借此论证：基于数学网络语料的预训练不仅提升纯推理，还显著增强「工具调用」与「非形式→形式化证明」这两项被低估的能力，验证DeepSeekMath作为"通用数学基座"的定位，为后续指令微调与RL阶段奠定更高起点。

### Table 4 (p.9) ⭐深度解读
![[assets/crops/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-tab04.png]]
> [!quote] caption
> | Evaluation on natural language understanding, reasoning, and code benchmarks. DeepSeek-Coder-Base-v1.5 † is the checkpoint right before learning rate decay, which is used to train DeepSeekMath-Base. On MMLU and BBH, we use few-shot chain-of-thought prompting. On HumanEval and MBPP, we evaluate mod

> [!tip] 表格解读（多模态）
> 【图文联合解读】该表对比四个7B模型在MMLU、BBH、HumanEval、MBPP上的表现。DeepSeekMath-Base在BBH以59.5%最优，MMLU达54.9%，代码能力略低于完整版Coder基座（HumanEval 40.9% vs 43.2%）。

关键结论：相比起点Coder-v1.5†（学习率衰减前检查点），数学专项训练使通用推理显著提升（MMLU 42.9%→54.9%，BBH 42.9%→59.5%），且代码能力基本保持，证明120B数学token训练未灾难性遗忘通用能力。

该表支撑论文"数学微调不损害通用能力"的核心论点，通过对照起点与最终模型，体现整条训练链路的全面增益。

### Table 5 (p.12) ⭐深度解读
![[assets/crops/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-tab05.png]]
> [!quote] caption
> | Performance of Open- and Closed-Source models with both Chain-of-Thought and Tool-Integrated Reasoning on English and Chinese Benchmarks. Scores in gray denote majority votes with 32 candidates; The others are Top1 scores. DeepSeekMath-RL 7B beats all open- source models from 7B to 70B, as well as

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

表5按"CoT推理"与"工具集成推理"两栏，对比闭源（Gemini Ultra 94.4/53.2%、GPT-4 Code 97.0/69.7%）与开源（7B–70B）模型在GSM8K/MATH及中文MGSM-zh/CMATH上的成绩。核心数据：DeepSeekMath-RL 7B以CoT方式取得88.2%/51.7%，工具集成下86.7%/58.8%，中文79.6%/88.8%，全面超越同尺寸乃至70B开源模型与多数闭源模型，仅依赖GSM8K+MATH CoT微调数据即泛化至中文。该表是论文方法链（数学预训练→SFT→GRPO强化学习）成效的最终验证，证明7B小模型可达到开源SOTA。

### Table 6 (p.16) ⭐深度解读
![[assets/crops/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-tab06.png]]
> [!quote] caption
> | Investigation of how code affects mathematical reasoning under different training settings. We experiment with DeepSeek-LLM 1.3B, and evaluate its mathematical reasoning performance without and with tool use via few-shot chain-of-thought prompting and few-shot program-of-thought prompting, respect

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 6 图文联合解读**

Table 6 用 DeepSeek-LLM 1.3B 对比 5 种训练设置在 GSM8K/MATH/CMATH 及对应 +Python 工具版本上的准确率。两阶段 Code→Math 在无工具下最优（GSM8K 21.9%、MATH 15.3%、CMATH 39.7%）；一次性 Code&Math 混合训练在使用 Python 工具下最优（19.7%、13.5%）。关键结论：代码预训练显著提升数学推理，且代码能力是 PoT 工具调用的必要前提——无代码训练时，引入工具反而使性能下降（如 GSM8K 19.1%→+Python 14.3%）。该消融为论文"代码+数学联合预训练"的核心路线提供了直接经验支撑。

### Table 7 (p.17) ⭐深度解读
![[assets/crops/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-tab07.png]]
> [!quote] caption
> | Investigation of how different settings of code and math training affect model perfor- mance of language understanding, reasoning, and coding. We experiment with DeepSeek-LLM 1.3B. We evaluate the models on MMLU and BBH using few-shot chain-of-thought prompting. On HumanEval and MBPP, we conduct z

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 7 图文联合解读**

该表对比 DeepSeek-LLM 1.3B 与 DeepSeek-Coder-Base 7B 在"No Math / MathPile / ArXiv-RedPajama"三种数学语料设置下，于 GSM8K、MATH、CMATH、Gaokao 等 8 项基准的成绩。**关键发现**：① 1.3B 无数学训练时 GSM8K 仅 2.9%，而 7B 代码基模型无数学训练即达 29.0%，验证代码预训练对数学推理的显著增益；② ArXiv-RedPajama 真实网页语料在多数任务上优于 MathPile 合成语料（如 1.3B 的 CMATH 由 1.2% 升至 7.4%）。该表为论文"代码与数学语料协同驱动"的核心动机提供了关键消融证据。

### Table 8 (p.17) ⭐深度解读
![[assets/crops/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-tab08.png]]
> [!quote] caption
> | Effect of math training on different arXiv datasets. Model performance is evaluated with few-shot chain-of-thought prompting.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**核心对象与数据**：表对比 DeepSeek-LLM 1.3B 与 DeepSeek-Coder-Base-v1.5 7B 在"无数学训练/MathPile/ArXiv-RedPajama"三种 arXiv 语料下，于 GSM8K、MATH、OCW、SAT、MMLU STEM、CMATH、Gaokao 等中英文基准上的少样本 CoT 得分。1.3B 模型加入数学语料后多数指标下滑（如 GSM8K 2.9%→2.7%、CMATH 12.3%→1.2%）；7B Coder 表现参半，SAT 从 40.6% 升至 50.0%，但 GSM8K 由 29.0% 降至 23.6%。

**论证结论**：仅以现有通用数学语料继续预训练，并不能稳定提升数学推理能力，反而常损害泛化性能，说明数据筛选与质量远比数量关键。

**论文作用**：作为 DeepSeekMath 提出高质量数学语料构造与筛选流程的动机铺垫，凸显改进数据策略的必要性。

### Table 9 (p.17) ⭐深度解读
![[assets/crops/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-tab09.png]]
> [!quote] caption
> | Effect of math training on different arXiv corpora, the base model being DeepSeek- Coder-Base-v1.5 7B. We evaluate informal-to-formal proving in Isabelle.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读（Table 9）**

1) **核心对象与数据**：以DeepSeek-Coder-Base-v1.5 7B为基座，在Isabelle上做非形式化→形式化证明评测，对比三种arXiv语料设置在miniF2F-valid/test上的通过率：无数学训练 20.1%/21.7%、MathPile 16.8%/16.4%、ArXiv-RedPajama 14.8%/11.9%。

2) **关键技术结论**：结果反直觉——不进行数学训练反而最优，加入数学数据持续损害Isabelle形式证明能力。这表明通用数学预训练与形式化证明所依赖的代码/逻辑能力存在权衡，印证DeepSeekMath"以代码为锚、仅针对性补数学"路线的必要性。

3) **整体链路作用**：为后续保留代码底座、仅注入高质量数学语料的训练方案提供消融依据，支撑方法设计中的能力权衡取舍。

### Table 10 (p.19) ⭐深度解读
![[assets/crops/deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models-tab10.png]]
> [!quote] caption
> The data source and gradient coefficient of different methods. Ps​f​t denotes the data distribution of supervised fine-tuning datasets. πθs​f​t and πθ denote the supervised fine-tuned model and the real-time policy model during the online training process, respectively.

> [!tip] 表格解读（多模态）
> 【图文联合解读】表10从数据源、奖励函数、梯度系数三维度横向对比SFT、RFT、DPO、Online RFT、PPO、GRPO六种方法。SFT采用Psft(Q,O)联合采样；RFT/DPO由SFT模型πsft采样；Online RFT、PPO、GRPO则切换到在线策略πθ采样。奖励函数由Rule-based逐步演化为Model-based（PPO、GRPO），GRPO以G个样本{oi}替代单样本o。梯度系数依次对应公式10、14、10、18、21。该表作为方法谱系图，论证GRPO（公式21）以分组相对优势替代PPO的价值模型，是论文核心创新推导与R1-zero训练链路的方法学起点。

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