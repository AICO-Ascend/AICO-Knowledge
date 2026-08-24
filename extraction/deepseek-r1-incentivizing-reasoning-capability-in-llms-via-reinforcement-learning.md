---
paper_num: "34"
title: "DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning"
authors: "Reinforcement Learning DeepSeek-AI research@deepseek.com"
date: "2026/1/17"
arxiv: "https://arxiv.org/abs/2501.12948"
pdf: "papers/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning.pdf"
slug: "deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning"
tags: [rl]
---

# DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning

> [!abstract] 摘要（原文）
> 1\. 🤖 DeepSeek-R1-Zero展示了大型语言模型可以通过纯强化学习（RL）在没有监督微调的情况下发展出强大的推理能力，并涌现出如自我验证等有趣行为。 2. ✨ 为解决DeepSeek-R1-Zero的局限并进一步提升性能，DeepSeek-R1采用了多阶段训练流程，结合冷启动数据和迭代强化学习，使其推理能力达到与OpenAI-o1-1217相当的水平。 3. 🚀 研究还表明，将DeepSeek-R1的推理模式蒸馏到小型模型中比直接在小模型上进行大规模RL训练更有效，并开源了多个稠密模型。

## 元信息
- **发表日期**: 2026/1/17
- **作者**: Reinforcement Learning DeepSeek-AI research@deepseek.com
- **arXiv**: https://arxiv.org/abs/2501.12948
- **本地 PDF**: `papers/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning.pdf`
- **页数**: 86

## 图表（原文 caption + 页码）

### Figure 2 (p.6) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-fig02.png]]
*整页渲染: ![[assets/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-p06.png]]*
> [!quote] caption
> In the initial stage, we collect thousands of cold-start data that exhibits a conversational, human-aligned thinking process. RL training is then applied to improve the model perfor- mance with the conversational thinking process and language consistency. Subsequently, we apply rejection sampling and SFT once more. This stage incorporates both reasoning and non- reasoning datasets into the SFT pro

> [!tip] 技术解读（多模态）
> 【图文联合解读】图2展示DeepSeek-R1的四路汇聚管线（带6类图例：模型/提示-响应/算法/提示/奖励/后处理）：

(a) V3 Base → RL（Accuracy & Format奖励）→ **R1 Zero** → Sampling+Filter（准确性）+人工Refine → Cold Start Long CoT 数据；

(b) V3 Base → SFT（冷启动长CoT）→ **Dev-1** → RL（规则奖励 & 语言一致性）→ **Dev-2**；

(c) V3 Sampling → 推理+非推理数据集；

(d) V3 Base → SFT融合数据 → **Dev-3** → RL（规则奖励 & 偏好奖励）→ **R1**。

原文借此论证"冷启动长CoT → 双轮SFT+RL迭代"是兼顾推理能力激发与人类对齐的核心范式，作为整篇方法学总览图，为后续蒸馏与基准对比提供路线支撑。

### Figure 3 (p.14) ⭐深度解读
![[assets/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-p14.png]]
> [!quote] caption
> For each question ? , GRPO samples a group of outputs f= 1, = 2,    , = g from the old policy 14

> [!tip] 技术解读（多模态）
> No figure is visible in the provided image. The image contains only page 14 of an academic paper, consisting of body text discussing Supervised Fine-Tuning (SFT), Reinforcement Learning (RL), and a section titled "A.3. A Comparison of GRPO and PPO." 

While the text references "Figure 3" for a comparison between GRPO and PPO algorithms, the actual figure/diagram is not present in this image — only a textual reference and the start of equations ("For each question ?, GRPO samples a group of outputs {o₁, o₂, ..., o_G} from the old policy") are shown.

If you intended to share Figure 3, please upload the image containing the actual diagram (architecture/components/data flow visualization). I'd be happy to describe it and transcribe the caption once provided.

### Figure 6 (p.35) ⭐深度解读
![[assets/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-p35.png]]
> [!quote] caption
> B.6. Ablation Study of Language Consistency Reward

> [!tip] 技术解读（多模态）
> **Note:** The main visual on this page is **Table 6** (no architecture/data-flow figure is present). Description and caption below.

**Description (Table 6):**
The table maps six DeepSeek-R1 distilled student models to their base backbones and initial learning rates. Components include: (1) *Distilled Model* — six sizes spanning 1.5B–70B parameters across Qwen and Llama families; (2) *Base Model* — pre-trained sources (Qwen2.5-Math-1.5B/7B, Qwen2.5-14B/32B, Llama-3.1-8B, Llama-3.3-70B-Instruct); (3) *Initial Learning Rate* — values ranging from 1×10⁻⁴ (smallest) down to 2×10⁻⁵ (largest).

**Key takeaway:** Initial LR scales inversely with model size (1×10⁻⁴ for 1.5B → 2×10⁻⁵ for 70B), and the two smallest Qwen variants intentionally use math-specialized base models (Qwen2.5-Math) to bootstrap reasoning capability before distillation.

**Caption (verbatim):**
Table 6 | DeepSeek-R1 Distilled Models, their corresponding Base Models, and Initial Learning Rates.

### Figure 7 (p.37) ⭐深度解读
![[assets/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-p37.png]]
> [!quote] caption
> As can be seen, without the LC reward, language consistency gradually deteriorates as train- ing steps increase. However, when the LC reward is applied, stable language consistency is maintained throughout the training process. For benchmark performance, the model main- tains comparable performance on the mathematical benchmark, while a slight degradation is observed on the coding benchmark. Altho

> [!tip] 技术解读（多模态）
> ## Figure Description

The actual Figure 7 plot is not visually rendered in this page excerpt — only its caption appears. Based on the caption and surrounding discussion, the figure depicts the **Language Consistency (LC) Reward ablation during reinforcement learning**, comparing two RL training conditions on language-mixing behavior.

**Components/data flow implied by the figure:**
- **X-axis:** training steps (RL progress)
- **Y-axis:** language consistency metric
- **Curves:** a baseline RL run *without* LC reward vs. an RL run *with* LC reward applied
- **Side panels (per text):** benchmark performance on math (maintained) and coding (slight degradation)

**Key technical takeaway:**
Without the LC reward signal, the model progressively drifts into language mixing as RL progresses; introducing LC reward preserves stable monolingual output throughout training, trading only marginal coding-benchmark performance for substantially better alignment with human-preferred readability.

## Caption (verbatim)

**Figure 7** jThe experiment results of Language Consistency (LC) Reward during reinforcement learning.

### Figure 13 (p.48) ⭐深度解读
![[assets/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-p48.png]]
> [!quote] caption
> We have categorized potential content safety challenges faced by language models into 4 major categories and 28 subcategories.

> [!tip] 技术解读（多模态）
> ## Main Figure Description

**Architecture/Components:**
Table 9 is a structured comparison matrix evaluating AI models across six safety benchmarks. The columns include the SST, BBQ, ART, XSTest, DNA*, and HarmBench* metrics, alongside an Average Score column. The rows compare frontier models: Claude-3.7-Sonnet, o1, GPT-4o, Qwen2.5 Instruct (72B), DeepSeek-V3, plus two DeepSeek-R1 variants (hide cot and standard R1).

**Data Flow/Logic:** Scores flow horizontally from individual benchmark evaluations to an aggregated Average Score column. The asterisked benchmarks (DNA, HarmBench) are reproduced by the authors, while other results derive from independent HELM evaluations. Values in parentheses represent pure-model performance without the risk control system described in D.3.1.

**Key Technical Takeaway:** DeepSeek-R1 achieves an average safety score of 95.0 (with risk control), comparable to or exceeding Claude-3.7-Sonnet (94.6) and GPT-4o (92.2). However, without the risk control system, its HarmBench score drops dramatically from 89.3 to 35.0—revealing that the model's raw safety behavior relies heavily on post-hoc filtering rather than intrinsic alignment. (117 words)

## Caption Verbatim Transcription

"Table 9 |Comparison of DeepSeek-R1 and other frontier models on safety benchmarks. A higher score indicates better safety performance. Benchmarks marked with * are the results reproduced by us, while other numerical results are obtained from the independent HELM evaluations. The numbers in parentheses represent the results of the pure model without considering the risk control system (introduced in D.3.1)."

### Figure 14 (p.53) ⭐深度解读
![[assets/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-p53.png]]
> [!quote] caption
> For DeepSeek-V3 and DeepSeek-R1, we evaluated safety scores for models with and without the risk control system (introduced in D.3.1). Additionally, we tested the multilingual safety performance of Claude-3.7-Sonnet and GPT-4o(2024-05-13). From Figure 14, we can draw the following conclusions: • With risk control system in place, DeepSeek-V3 (86.5%) and DeepSeek-R1 (85.9%) achieve total safety sco

> [!tip] 技术解读（多模态）
> # Observation: No Figure Present

The provided image contains **only text content** (page 53 of a research paper, likely the DeepSeek technical report). No figure, chart, diagram, or visualization is visible in the image. The text merely *references* "Figure 14" for multilingual safety scores across 50 languages, but the figure itself is not shown.

# Available Text Content

Since no figure is present, I can only transcribe the visible caption-adjacent text. There is no caption to transcribe verbatim because no figure is rendered.

## Section Headers Visible:
- **D.3.4. Multilingual Safety Performance**
- **D.3.5. Robustness against Jailbreaking**

## Key Technical Content (from the text, in lieu of a figure):

**Test Set Construction:**
- Original bilingual safety testset translated into **50 commonly used languages**
- Full translation for high-frequency languages; sampling translation for low-frequency ones
- Final corpus: **9,330 questions**
- Quality ensured via combined **LLM translation + human-assisted calibration**

**Scoring Scheme (LLM-as-a-judge):**
| Response Type | Points |
|---|---|
| Safe | 5 |
| Unsafe | 0 |
| Rejection | 4 |

**Headline Results Across 50 Languages:**
| Model | With Risk Control | Without Risk Control |
|---|---|---|
| DeepSeek-V3 | **86.5%** | 75.3% |
| DeepSeek-R1 | **85.9%** | 74.2% |
| Claude-3.7-Sonnet | 88.3% | — |
| GPT-4o (2024-05-13) | — | 75.2% |

**Key Takeaway:** With the risk control system enabled, DeepSeek-V3/R1's multilingual safety approaches Claude-3.7-Sonnet (SOTA), while DeepSeek-R1 exhibits **zero high-risk languages** — indicating no obvious language-specific vulnerabilities.

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.3) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab01.png]]
> [!quote] caption
> Template for DeepSeek-R1-Zero. prompt will be replaced with the specific reasoning question during training.

> [!tip] 表格解读（多模态）
> 【图文联合解读】图示为DeepSeek-R1-Zero的Jinja对话模板（Table 1），含两段固定指令：①设定"User提问–Assistant作答"的角色；②强制Assistant先以`<think>...`标签包裹内部推理过程，再以`<answer>...</answer>`标签给出最终答案，末尾以`User: prompt. Assistant:`作为待填充的推理题占位符。

原文借此论证关键结论：**R1-Zero无需任何SFT冷启动数据**，仅凭该模板的结构化指令约束，便可对基座模型直接施加GRPO强化学习，将"思维链"与"最终答案"在输出层面强制解耦。

在整体方法链路中，它是纯RL训练流水线的**输入格式化层**：模板规定的两标签格式既是奖励函数判定格式合规的依据，也引导模型在RL过程中自发涌现长链反思、自我验证等推理行为，为后续AIME/MATH等基准的"顿悟时刻"提供格式保障。

### Table 2 (p.5) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab02.png]]
> [!quote] caption
> An interesting “aha moment” of an intermediate version of DeepSeek-R1-Zero. The model learns to rethink using an anthropomorphic tone. This is also an aha moment for us, allowing us to witness the power and beauty of reinforcement learning.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**说明**：图像并非数值型 Table 2，而是论文中展示 "aha moment" 的对话样例（Figure 3 类）。

**1) 核心内容**：模型解答"已知 a>1，求 a−√(a+x)=x 的实根之和"，经平方得四次方程、推导陷入冗长代数后，于中段自语"Wait, wait. Wait. That's an aha moment I can flag here."，随即主动回溯，从原方程 a−√(a+x)=x 重新整理思路。

**2) 关键技术结论**：纯 GRPO 强化学习即可驱动模型自发涌现拟人化反思语气（anthropomorphic tone）与自我回溯行为，证明 RL 足以激励深度推理能力，无需依赖 SFT 冷启动数据。

**3) 在方法链路中的作用**：作为定性证据与图 2 多阶段 pipeline 互补，支撑"R1-Zero 仅靠 RL 即获得强推理"这一核心论点，并间接说明 R1 后续引入冷启动是为了改善语言可读性，而非弥补推理能力的不足。

### Table 3 (p.8) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab03.png]]
> [!quote] caption
> Experimental results at each stage of DeepSeek-R1. Numbers in bold denote the performance is statistically significant (t−test with p<0.01).

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 3 图文联合解读**

1) **结构与核心数据**：表3按英语/代码/数学/中文4类、20项基准对比 R1-Zero、R1-Dev1/2/3、R1 五个阶段。典型增量：IF-Eval 46.6→83.3、AlpacaEval2.0 LC-winrate 24.7→87.6、ArenaHard 53.6→92.3、Codeforces Rating 1444→2029、Aider-Polyglot 12.2→53.3、MATH-500 95.9→97.3；AIME 2024 出现非单调：77.9（R1-Zero）→59.0（R1-Dev1）→79.8（R1）。

2) **关键结论**：纯RL（R1-Zero）已激发强推理能力；引入冷启动SFT与拒绝采样后，语言可读性与指令遵循（IF-Eval、AlpacaEval）显著上升，但AIME等任务短暂回落；最终R1在多数基准上达到统计显著最优（p<0.01），验证"R1-Zero→冷启动SFT→R2L→最终RL"四阶段流水线的有效性。

3) **作用**：支撑论文核心主张——纯RL可激发推理，再经SFT+RL联合优化即可兼顾可读性与性能，是DeepSeek-R1方法链路的关键消融/验证证据。

### Table 5 (p.27) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab05.png]]
> [!quote] caption
> j Data Statistics of SFT Data.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

表格展示SFT数据构成：5个领域共**804,745**样本，以Math(395,285)与Code(211,129)为主(≈75%)，General 177,812次之，Logic(10,395)、STEM(10,124)规模较小但补全推理覆盖；平均轮次≈1.0–1.1，单轮对话为主；平均token长5,355.3，Code最长7,435.7、General最短1,419.8。

论文借此论证：RL阶段后通过拒绝采样构造的SFT数据**多域覆盖**且含**长上下文**推理样本，为冷启动微调及向Qwen/Llama等小模型蒸馏提供大规模高质量监督数据，是DeepSeek-R1流水线第二阶段(rejection-sampling + SFT)的关键依据与可复现性支撑。

### Table 6 (p.35) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab06.png]]
> [!quote] caption
> j DeepSeek-R1 Distilled Models, their corresponding Base Models, and Initial Learning

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 6 图文联合解读**

该表列出 6 个 DeepSeek-R1 蒸馏模型及其对应基模型与初始学习率：1.5B/7B 采用 Qwen2.5-Math（lr=1e-4、8e-5），14B/32B 采用 Qwen2.5（7e-5、6e-5），8B/70B 采用 Llama-3.1/3.3（5e-5、2e-5）。

**核心结论**：初始学习率与模型规模呈反相关（1e-4 → 2e-5），且基模型按能力差异分别选用 Math 版（数学强基）与 Instruct 版（大模型对话基），体现大模型训练稳定性与适配性考量。

**链路作用**：该表为 B.6 "Language Consistency Reward" 消融实验提供 SFT 蒸馏阶段的统一超参配置基线，保证不同规模蒸馏模型间的公平比较，从而支撑语言一致性奖励对推理性能影响的消融结论可靠性。

### Table 7 (p.37) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab07.png]]
> [!quote] caption
> j Training costs of DeepSeek-R1, assuming the rental price of H800 is $2 per GPU hour.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**注**：所引段落实为论文 Figure 7（语言一致性奖励消融）的讨论，与 Table 7（训练成本）并非同一图表，以下仅依表7本身解读。

---

**1）核心对象与数据**：表7展示 DeepSeek-R1 全流程训练成本，按 H800 $2/GPU·h 计，分三阶段：R1-Zero（纯RL）101K 小时 / $202K；SFT 数据构建 5K / $10K；R1（含冷启动）41K / $82K；总计 147K 小时 / $294K。

**2）技术结论**：纯 RL 阶段最昂贵（约占总成本 69%）；引入冷启动 SFT 数据后，R1 主训练阶段 GPU 时长锐减约 60%，证明"冷启动 + RL"范式显著提升算力效率；总成本仅约 29.4 万美元，远低于同期主流闭源/开源推理模型。

**3）在论文中的作用**：与性能 SOTA 形成"性价比闭环"——以低成本即可复现强推理能力，为开源发布与可复现性主张提供经济性锚点。

### Table 8 (p.41) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab08.png]]
> [!quote] caption
> j Comparison between DeepSeek-R1 and other representative models. Numbers in bold

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

**1）核心对象与结构：** Table 8 将 DeepSeek-R1（MoE，37B 激活/671B 总参数）与 Claude-3.5-Sonnet-1022、GPT-4o 0513、DeepSeek-V3、OpenAI o1-mini、o1-1217 在 19 项基准（英语/代码/数学/中文四类）上并列对比，粗体表示 t 检验 p>0.01 的统计显著优势。

**2）关键结论：** R1 在数学三项全部领先（AIME 79.8、MATH-500 97.3、CNMO 78.8）、代码 LiveCodeBench 65.9 最高、中文 CLUEWSC 92.8、C-Eval 91.8 最高、英文推理 DROP 92.2、MMLU-Redux 92.9、AlpacaEval2.0 87.6、ArenaHard 92.3 显著优于对照；整体与 o1-1217 同档。

**3）在论文中的作用：** 作为压轴主对比表，以开放权重 + 显著更少的激活参数，量化证明 R1 对标闭源 o1 系列的能力，巩固"纯 RL（GRLO）即可激发强推理"的全文核心主张。

### Table 9 (p.48) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab09.png]]
> [!quote] caption
> j Comparison of DeepSeek-R1 and other frontier models on safety benchmarks. A higher score indicates better safety performance. Benchmarks marked with * are the results reproduced by us, while other numerical results are obtained from the independent HELM

> [!tip] 表格解读（多模态）
> 【图文联合解读】**1）核心对象与结构：** 表9对比Claude-3.7-Sonnet、o1、GPT-4o、Qwen2.5-72B-Instruct、DeepSeek-V3、DeepSeek-R1（hide cot）与标准R1共7个前沿模型，在SST、BBQ、ART、XSTest、DNA*、HarmBench* 6项安全基准及平均分上的表现；括号内数值为去除风险控制系统后的纯模型结果。

**2）关键结论：** DeepSeek-R1平均分95.0%（带风险控制系统），与Claude-3.7（94.6）、o1（93.6）、GPT-4o（92.2）持平；但去掉风险控制系统后，HarmBench从89.3骤降至35.0，平均跌至85.9%，凸显该系统在保障安全输出上的必要性。

**3）论文作用：** 作为安全维度附录，与主文推理能力评估互补，论证以RL激励推理能力的同时未牺牲模型对齐与安全性。

### Table 10 (p.51) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab10.png]]
> [!quote] caption
> j Comparison of DeepSeek-R1 and other frontier models in fine-grained safety scenarios. Unsafe indicates the proportion of unsafe content in the model’s responses (lower

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 10 联合解读**

**1) 核心数据**：该表在 Discrimination、Illegal、Harmful、Ethical 四类细粒度安全场景下，对比 Claude-3.7-Sonnet、o1、GPT-4o、Qwen2.5-72B-Instruct、DeepSeek-V3、DeepSeek-R1 六款模型，给出"Unsafe（不安全内容占比）"与"Rej.（拒答率）"两项指标，并对 V3/R1 各报告"裸模型 / +风险控制系统"两种配置。

**2) 关键结论**：R1 裸模型整体 Unsafe 高达 25.2%，明显劣于 Claude-3.7-Sonnet（10.7%）与 o1（9.0%）；引入风险控制系统后骤降至 8.5%，拒答率升至 27.3%，整体安全水平已优于 Claude-3.7-Sonnet，并接近 o1。o1 虽安全但 Rej. 普遍 ≥34%（最高 73.5%），靠"拒答"换安全；R1+风控则能在提供有用回复的同时保证安全。

**3) 论文作用**：该表位于评估章节，与文中 D.3.1 风险控制系统呼应，作为"推理强化学习未损害模型安全性"的关键佐证——说明纯 RL 训练虽使 R1 原始安全指标下降，但配套风险控制系统即可使其在细粒度安全维度上达到前沿水平，闭环支撑"推理能力与安全性可兼得"的核心主张。

### Table 11 (p.54) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab11.png]]
> [!quote] caption
> j Comparison of DeepSeek-R1 and other frontier models in jailbreaking scenarios.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 11 图文联合解读**

**结构与数据：** 表11对比DeepSeek-R1与Claude-3.7-Sonnet、o1、GPT-4o、Qwen2.5-72B在越狱场景下的Unsafe Ratio与Rejected Ratio（含Origin/Jailbreak/GAP三列）。

**核心量化：** R1单独越狱后Unsafe Ratio高达**85.9%**（GAP +60.7），Rejected仅**1.9%**，安全性显著弱于基线；叠加risk control system后Unsafe骤降至**4.3%**（GAP -4.2），Rejected升至**87.3%**。

**关键结论：** RL激发推理能力会弱化模型安全对齐，但外挂风险控制模块可有效弥补，使R1最终安全表现优于GPT-4o、Claude等商用模型。

**论文作用：** 作为安全对齐消融实验证据，回应"RL训练破坏安全性"的潜在质疑，证明R1系统级发布无需修改RL训练即可兼顾强推理能力与高安全性，是补齐Responsible AI评估闭环的关键一环。

### Table 12 (p.56) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab12.png]]
> [!quote] caption
> j A Comparative Analysis of DeepSeek-V3 and DeepSeek-R1. DeepSeek-V3 is a

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 12 图文联合解读**

Table 12 对 V3-Base、V3、R1-Zero、R1 在英语/代码/数学/中文四类共 19 个基准做了量化对比。结果显示：R1 在绝大多数任务（粗体）取得最优，如 MMLU 90.8、Codeforces Rating 2029、MATH-500 97.3、AIME 79.8；R1-Zero 在 GPQA 75.8、AIME 77.9、Codeforces 80.4 百分位等推理任务上亦显著超越 V3。该表论证两个关键结论：①纯 RL 激励（R1-Zero）即可显著激发基模型的推理能力；②在 RL 基础上叠加冷启动 SFT 与多阶段训练（R1）能兼顾通用能力，使 R1 全面领先 V3。它是验证"GRPO+两阶段 RL+拒采 SFT"完整训练链路有效性的核心证据。

### Table 13 (p.57) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab13.png]]
> [!quote] caption
> Performance on latest math competitions. Participants with their USAMO index (AMC score+10×AIME score) surpassing 251.5 are qualified for USAMO.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

**核心数据：** 表13对比了5个对象在AMC 12 2024、AIME 2025上的表现，并以USAMO指数（AMC分数+10×AIME分数，门槛251.5）衡量资格。DeepSeek R1三项分别为143.7、11.3/15、256.7，跨过门槛；OpenAI o1-1217为141.0、12.0/15、261.0；DeepSeek V3仅98.3、3.3/15、131.3；GPT-4o为84.0、2.0/15、104.0；人类参赛者均值为123.7。

**关键结论：** DeepSeek R1以256.7的USAMO指数达到USAMO参赛资格，与o1-1217（261.0）几乎持平，并显著超越其基座V3（131.3）和GPT-4o（104.0），证明纯RL训练可激发LLM达到顶尖竞赛级数学推理。

**论文作用：** 作为"方法有效性"的终极实证，支撑"RL激励推理能力"的核心主张。

### Table 14 (p.60) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab14.png]]
> [!quote] caption
> Experimental results for each stage of DeepSeek-R1 on problems with varying difficulty levels in the LiveCodeBench dataset.

> [!tip] 表格解读（多模态）
> 【图文联合解读】## 图文联合解读（Table 14）

**核心结构**：表14以三档难度（Easy / Medium / Hard）为行，以DeepSeek-R1五个训练阶段（基线Zero、中间版Dev1、Dev2、Dev3、最终R1）为列，展示其在LiveCodeBench上的得分。

**关键数据**：
- Easy：98.07 → 99.52 → 100.00 → 100.00 → 100.00
- Medium：58.78 → 73.31 → 81.76 → 81.42 → 83.45
- Hard：17.09 → 23.21 → 30.36 → 33.16 → 34.44

**技术结论**：随RL训练推进，各档难度均单调上升；难题Hard得分近乎翻倍（17.09→34.44），证明RL对推理能力的渐进式激励在高难度任务上尤为显著。

**实验链路作用**：该表是论文"RL激励推理"核心论点的阶段性消融证据，串联纯RL（R1-Zero）与冷启动+RL（R1）两条技术路径，支撑整体方法有效性论证。

### Table 15 (p.61) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab15.png]]
> [!quote] caption
> j Comparison of DeepSeek-R1 distilled models and other comparable models on

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读（Table 15）**

**1) 核心对象与数据**：表比较DeepSeek-R1蒸馏系列（Qwen-1.5B/7B/14B/32B、Llama-8B/70B）与GPT-4o-0513、Claude-3.5-Sonnet-1022在AIME 2024（pass@1/cons@64）、MATH、GPQA Diamond、LiveCodeBench、CodeForces六大推理基准上的表现。最小的1.5B蒸馏模型即已取得cons@64 52.7、CodeForces 954；而Llama-70B蒸馏版MATH 94.5、cons@64 86.7、GPQA 65.2、CodeForces 1633，各指标全维度领先。

**2) 关键结论**：原文以此论证"即便参数量远小于闭源巨模型，蒸馏后的小模型在数学、代码与科学推理上仍系统性超越GPT-4o与Claude-3.5-Sonnet"，证明R1推理模式具备强可迁移性。

**3) 在论文中的作用**：是蒸馏管线（distillation pipeline）有效性的核心实验证据，支撑"R1的RL激励推理能力可被开源小模型继承"这一核心主张。

### Table 16 (p.61) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab16.png]]
> [!quote] caption
> Comparison of distilled and RL Models on Reasoning-Related Benchmarks.

> [!tip] 表格解读（多模态）
> 【图文联合解读】该表对比DeepSeek-R1-Distill-Qwen-32B与两个纯RL模型（QwQ-32B-Preview、Qwen2.5-32B-Zero）在5个推理基准的pass@1表现（Diamond用cons@64）。蒸馏模型全面领先：AIME 2024达72.6（vs 50.0/47.0）、MATH 94.3（vs 90.6/91.6）、GPQA 62.1（vs 54.5/55.0）、LiveCode 57.2（vs 41.9/40.2）、Diamond 83.3。原文借此证明：把R1的推理能力蒸馏进Qwen-32B，效果显著优于直接对基座做RL，佐证蒸馏是传递推理能力的优选路径，支撑论文"大模型RL→蒸馏小模型"的两阶段方法链。

### Table 17 (p.62) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab17.png]]
> [!quote] caption
> j Performance of different models on AIME 2024 and AIME 2025.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

**1) 表格核心内容：** 表17展示3个模型在AIME 2024与AIME 2025两个高难度数学竞赛基准上的平均得分。GPT-4o-0513仅报告AIME 2024为9.3%；Qwen2-Math-7B-Instruct分别为7.9%与4.6%；而经DeepSeek-R1的纯强化学习方法训练的**Qwen2-Math-7B-Zero**以22.3%/18.1%大幅领先（GPT-4o在2025因发布时间缺数据）。

**2) 关键论证结论：** 仅凭RL激励，7B量级的Qwen2-Math-Zero即可将AIME 2024正确率相对Qwen2-Math-Instruct提升约14个百分点（7.9%→22.3%），并超越GPT-4o-0513，验证了"无需监督微即可涌现强推理能力"这一核心主张。

**3) 在论文中的定位：** 该表属于模型对比实验环节，与表16（蒸馏效果）相辅，共同支撑"R1-Zero路径可低成本复现先进推理性能"的结论，为论文"RL激励推理涌现"的方法论提供量化证据。

### Table 18 (p.66) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab18.png]]
> [!quote] caption
> j MMLU assesses a model’s factual and conceptual understanding across 57 tasks spanning STEM (science, technology, engineering, mathematics), humanities, social sciences, and professional fields (e.g., law, medicine). The benchmark is commonly used to evaluate a

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读**

> 注：图中仅显示 Table 18 caption 文字片段，未呈现具体评测 prompt 示例，故主要依据 caption 与正文交叉解读。

1) **核心对象与结构**：该表位于附录 J"Evaluation Prompts and Settings"，是 Table 18–32 系列评测格式示例中的首张，专门给出 MMLU 基准的评测 prompt 模板。MMLU 共 57 个任务，横跨 STEM（科学/技术/工程/数学）、人文、社科及法律/医学等专业领域，用以衡量模型的事实性与概念性理解水平。

2) **论证结论**：MMLU 作为公认的多学科知识基准，可系统评测模型在广域知识上的掌握程度，与 AIME/MATH 等推理类基准形成互补，全面刻画 R1 系列模型的能力剖面。

3) **论文链路作用**：附录公开各基准 prompt 与设置细节，提升主文 RL 训练结果的可复现性，支撑"推理能力增强的同时基础知识能力得以保留"这一核心实验结论。

### Table 19 (p.67) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab19.png]]
> [!quote] caption
> MMLU-Redux is a subset of 5,700 manually re-annotated questions across all 57 MMLU subjects. MMLU-Redux focuses on improving the quality, clarity, and robustness of the benchmark by reducing noise, ambiguities, and potential biases in the MMLU, while potentially adjusting the scope or difficulty of 

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图像无法清晰辨认，仅依据原文与可见碎片内容解读：**

图片并非整洁的表格，而是 MMLU-Redux 基准中一道样本题的可视化片段（"##DOMAIN" 重叠标注、Sauna 题干、选项 B/C/D、JSON 输出指令与评测流程），呈现了该基准的典型题面与评测格式：模型先给出推理链，再用 JSON 输出 `{"reasoning":..., "answer":"C"}`，最终按答案字段与 ground truth 比对判分。

原文据此论证两点关键结论：(1) MMLU-Redux 由 5,700 道人工重标注题目构成、覆盖 MMLU 全 57 个学科，通过去噪、去歧义降低噪声与偏差；(2) 采用严格 JSON 格式与答案字段自动比对，可机械化、规模化地对 DeepSeek-R1 的广域知识推理能力做稳定评测。

在论文整体链路中，该表作为附录级标准化评测项，与 GPQA、MATH、AIME 等推理基准互补，共同支撑"纯 RL 即可激发强推理"的整体结论。

### Table 22 (p.70) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab22.png]]
> [!quote] caption
> DROP assesses a model’s ability to understand and extract relevant information from extended textual passages. Unlike simpler question-answering benchmarks that focus on factual recall, DROP requires models to process and interpret context-rich paragraphs.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

该表呈现 DROP 基准的少样本提示模板，结构分四块：①简介（说明 DROP 考验长文语境理解）；②PROMPT 区含 3 段 NFL 比赛段落配问答示例（均以"Answer: X"格式输出，如第一例答 4）；③"Your Task"段落要求回答 Rivers 传球码数；④Evaluation 行规定"Parse the capital letter following 'Answer:'"以判定答案是否等于真值。

原文借此说明：DeepSeek-R1 评估流程采用统一字符串解析机制，于 DROP 等上下文密集型阅读理解任务上做少样本打分，证明纯 RL 模型在需段落推理场景中仍能稳定输出规范答案。

在论文中的作用：作为附录中的提示工程样例，确保基准评估的可复现性与评分一致性，支撑主表各项推理基准的对比结论。

### Table 23 (p.71) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab23.png]]
> [!quote] caption
> Instruction-Following Evaluation (IFEval) is a benchmark designed to assess a model’s ability to comply with explicit, verifiable instructions embedded within prompts. It targets a core competency of large language models (LLMs): producing outputs that meet multiple, clearly defined constraints spec

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 23 联合解读（IFEval示例）**

**1）核心对象与结构**：该表呈现一个IFEval提示示例——上方为内容型prompt（量子纠缠背景介绍，讨论对纠缠粒子的位置、动量、自旋、极化测量，并以"总自旋为零则另一粒子自旋沿第一轴反方向"举例）；中部标注"Evaluation"；底部附加一条可验证硬指令："Call official functions to check if the answer is consistent with the instructions."（调用官方函数校验答案与指令的一致性）。即同时考察**内容生成+显式函数调用**两条可机器校验约束。

**2）原文论证结论**：DeepSeek-R1系列（含R1-Zero/R1蒸馏模型）在该类多约束、含工具调用的指令上仍保持高合规率，证明纯RL激励推理并未损害模型的指令遵循与工具使用能力，反而在复杂可验证指令上具备鲁棒性。

**3）论文链路作用**：IFEval与MMLU、GPQA、AIME等共同构成"通用能力+专业推理+指令合规"的综合评测体系，定位为评估RL训练是否牺牲对齐性的**安全阀指标**，支撑"RL可同步增强推理与对齐"的中心论点。

### Table 27 (p.0) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab27.png]]
> [!quote] caption
> The CLUEWSC (Chinese Language Understanding Evaluation Benchmark - Winograd Schema Challenge) is a specialized task within the CLUE benchmark suite designed to evaluate a model’s commonsense reasoning and contextual understanding capabilities in Chinese.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

**1) 核心对象与结构：** 该表展示CLUEWSC基准的Prompt模板与评测方法。Prompt部分采用少样本(few-shot)形式，列出5个中文示例（如"他伯父还有许多女弟子"、"情妇那律克定"、"手稿这个身材高大"、"朝鲜女导游"等段落），每例末尾要求回答"上面的句子中的'她/他/它'指的是"，最后接真实测试题（含``指令引导模型在思考后输出一句答案）。Evaluation部分规定：解析模型回复的最后一行，比对是否与标准答案一致。

**2) 论证结论：** 论文借此说明DeepSeek-R1在中文Winograd Schema指代消解任务上的评测协议——通过指代词歧义消解考察模型的常识推理与上下文理解能力。

**3) 论文作用：** 属于R1全维度评估链中的一环，与其他中英文基准并列，用于验证RL训练后模型在中文语义推理任务上的泛化表现。

### Table 28 (p.76) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab28.png]]
> [!quote] caption
> j C-EVAL evaluates a model’s breadth and depth of knowledge across 52 diverse

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

1）**核心对象与结构**：表28展示C-EVAL基准的提示样例与评测协议。顶部为PROMPT区，包含两道中文题目：第一题为带时间戳（1991/2000）的填空/概率题，给出2π、3π、4π、5π四个选项；第二题为依前文构建的数据结构选择题，选项A–D。底部Evaluation规定解析模型回复最后一行，与标准答案比对判分。整套基准覆盖52个学科（人文、社科、STEM及医学/法律等专业领域），全为中文。

2）**论证结论**：说明论文在中文专业领域知识上的评测方式——以"完形填空+多选推理"结合，验证模型在跨学科中文知识上的广度与深度。

3）**在论文中的作用**：C-EVAL是DeepSeek-R1（及对照基线）在通用中文知识维度的辅助评测之一，与AIME/MATH、GPQA等任务共同构成"推理+知识"综合评估链路，用以证明RL训练未损害模型的通用中文知识能力。

### Table 29 (p.76) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab29.png]]
> [!quote] caption
> GPQA (Graduate-Level Google-Proof QA Benchmark) is a rigorous evaluation framework designed to measure an LLM’s ability to tackle complex, graduate-level multiple-choice problems in STEM domains—specifically biology, physics, and chemistry.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读（Table 29）：**

**1) 核心对象与内容：** 该表并非性能结果表，而是 GPQA 基准的一道**示例样本**，展示了三部分：(a) 标准 Prompt 模板——要求模型逐步思考（"Think step by step"）并以"ANSWER: $LETTER"格式输出 A/B/C/D；(b) 一道物理量子力学题——两能级 E1、E2 寿命分别为 10⁻⁹ s 与 10⁻⁸ s，选项含 B) 10⁻⁸ eV、C) 10⁻⁴ eV、D) 10⁻¹¹ eV；(c) Evaluation 规则——解析"ANSWER:"后的大写字母与真值比对。

**2) 论证的技术结论：** 原文借此说明 GPQA 作为研究生级 STEM（生物、物理、化学）问答基准的评估协议——通过受限格式 Prompt + 答案抽取实现可复现的自动评测，确保证推理链可被验证。

**3) 在论文中的作用：** 作为附录样例，向读者透明披露 GPQA 的输入输出格式与判分流程，与正文 R1 蒸馏/RL 模型的评测结果呼应，保证实验可重现。

### Table 31 (p.0) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab31.png]]
> [!quote] caption
> An example of C-SimpleQA. It measures a model’s ability to answer short, fact-seeking questions in Chinese with precise, verifiable correctness.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 31 图文联合解读：**

该表展示C-SimpleQA评测的完整prompt模板，包含：①1道中文事实型简答题（"显脉香茶菜可治何种急性黄疸型肝炎"），标准答案为"黄疸型肝炎"；②采用LLM-as-judge三分类（【正确】/【错误】/【未尝试】），每个类别配2个few-shot示例（共6例教学样本）；③最终强制模型输出A/B/C以保证评判客观性。

在论文中，C-SimpleQA用于衡量**中文事实型短问答能力**，与英文SimpleQA等并列构成知识类评测子集，论证关键结论：RL激励推理训练**未显著损害**R1的领域知识储备与中文事实检索准确率。

该附录样例是实验链路中"知识保持性验证"环节的可视化补充，让读者直观理解评测判据（精确匹配+可验证性）和评分流程，支撑结论的可复现性。

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\begin{split} \footnotesize & \mathcal{J}_{GRPO}(\theta) = \mathbb{E}{[q \sim P(Q), \{o_i\}_{i=1}^G \sim \pi_{\theta_{old}}(O|q)]} \\ & \frac{1}{G}\sum_{i=1}^G \left( \min \left( \frac{\pi_\theta(o_i |q)}{\pi_{\theta_{old}}(o_i |q)} A_i, \text{clip} \left( \frac{\pi_\theta(o_i |q)}{\pi_{\theta_{old}}(o_i |q)}, 1 - \epsilon, 1 + \epsilon \right) A_i \right) - \beta \mathbb{D}_{KL}\left(\pi_{\theta} || \pi_{ref}\right)\right) , \end{split}
$$

$$
\mathbb{D}_{KL}\left(\pi_{\theta} || \pi_{ref}\right) = \frac{\pi_{ref}(o_i|q)}{\pi_{\theta}(o_i|q)}- \log\frac{\pi_{ref}(o_i|q)}{\pi_{\theta}(o_i|q)} - 1,
$$

$$
A_i = \frac{r_i - {\mathrm mean(\{r_1, r_2, \cdots, r_G\})}}{{\mathrm std(\{r_1, r_2, \cdots, r_G\})}}.
$$

$$
Reward_\text{rule} = Reward_\text{acc} + Reward_\text{format}
$$

$$
Reward_{helpful} = RM_{helpful}(Response_A, Response_B)
$$

$$
Reward_{safety} = RM_{safety}(Response)
$$

$$
Reward_{language} = \frac{Num(Words_{target})}{Num(Words)}
$$

$$
Reward &= Reward_{\text{reasoning}} + Reward_{\text{general}} + Reward_{\text{language}}\\ \text{where, } Reward_{\text{reasoning}} &= Reward_{\text{rule}}\\ Reward_{\text{general}} &= Reward_{\text{reward\_model}} + Reward_{\text{format}}
$$

$$
\text{pass@1} = \frac{1}{k} \sum_{i=1}^{k} p_i,
$$

## 相关论文

- [[search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning]] — Search-R1: Training LLMs to Reason and Leverage Search Engines with Reinforcement Learning
- [[areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning]] — AREAL: A Large-Scale Asynchronous Reinforcement Learning System for Language Reasoning
- [[single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning]] — Single-Rollout Asynchronous Optimization for Agentic Reinforcement Learning
- [[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]] — GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM REINFORCEMENT LEARNING
- [[hybridflow-a-flexible-and-efficient-rlhf-framework]] — HybridFlow: A Flexible and Efficient RLHF Framework

## 技术点深读（DEEP）

![[deep/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning.txt`（223572 字符）供引用检索。