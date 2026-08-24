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
> 【图文联合解读】**图文联合解读**

图示DeepSeek-R1三阶段流水线：①左路，V3 Base经纯RL（推理prompt+准确性/格式奖励）得R1 Zero，再采样并以"V3+人工"精炼产出冷启动长CoT；②中路，V3 Base经冷启动CoT SFT得Dev-1，再RL加入语言一致性奖励得Dev-2；③右路，融合Dev-2采样推理数据与非推理数据SFT得Dev-3，最终以多样化prompt+规则与偏好奖励RL产出R1。

该图论证两大结论：纯RL可自发激发长链推理（"aha moment"），但需冷启动与多轮SFT-RL迭代才能兼顾语言一致性与人类偏好。它是全文方法总纲，串联R1 Zero与R1两条主线，支撑后续实验对比。

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
> 【图文联合解读】**图文联合解读：**

1) **核心对象**：DeepSeek-R1-Zero 的对话提示模板，含两段固定指令（约60词）：设定 User–Assistant 角色，并强制 Assistant 输出须以 `<think>…` 包裹推理过程、以 `<answer>…</answer>` 包裹最终答案；末行 `User: prompt. Assistant:` 作为待填充推理题占位符。

2) **论证结论**：该模板为 R1-Zero 在纯 RL（GRPO）训练中划定了"思考-作答"的结构边界，使模型在不依赖监督微调数据的前提下，仍能以规则化标签形式区分内部推理链与最终答案，从而自发生成长 CoT。

3) **链路作用**：作为 R1-Zero 训练的输入格式基座，直接服务于后续"Aha moment"涌现与可读性分析；也是 R1 引入冷启动 SFT 数据前的零基线结构。

### Table 2 (p.5) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab02.png]]
> [!quote] caption
> An interesting “aha moment” of an intermediate version of DeepSeek-R1-Zero. The model learns to rethink using an anthropomorphic tone. This is also an aha moment for us, allowing us to witness the power and beauty of reinforcement learning.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

该表记录了 DeepSeek-R1-Zero 中间版本对一道数学题（a>1 时，求 √(a−√(a+x))=x 实数解之和）的完整解题轨迹：先按平方去根号→代入展开→化简得 x⁴−2ax²−x+(a²−a)=0→中途停顿自评 "Wait, wait. Wait. That's an aha moment I can flag here."→随即触发自我反思（"Let's reevaluate this step-by-step"），从方程原点重新审视并尝试再次平方，呈现典型的"顿悟—回溯—重审"行为链。

原文借此论证关键结论：模型在纯强化学习（GRPO）训练下，未经任何监督提示，便自发涌现出拟人化的反思、验证与自我纠错能力，是推理能力"可被激励涌现"的有力证据。

在论文方法链中，此例与 R1-Zero 的零冷启动路线互证，强化了"RL 即可激发高级推理"的核心主张，同时为后文引入冷启动 SFT、构造 DeepSeek-R1（解决语言混杂、可读性问题）的下一阶段训练提供动机与对照。

### Table 3 (p.8) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab03.png]]
> [!quote] caption
> Experimental results at each stage of DeepSeek-R1. Numbers in bold denote the performance is statistically significant (t−test with p<0.01).

> [!tip] 表格解读（多模态）
> 【图文联合解读】**表3图文联合解读：**

表3展示DeepSeek-R1从R1-Zero→R1-Dev1→R1-Dev2/3→R1最终版在四大类（英语/代码/数学/中文）共21个基准上的递进表现。

**关键数据趋势：**R1-Dev1阶段在推理类任务出现明显回退——GPQA Diamond 75.8→66.1、AIME 2024 77.9→59.0、CNMO 88.1→58.0、SWE Verified 43.2→39.6、Aider-Polyglot 12.2→6.7，说明冷启动SFT虽改善语言混杂与格式问题，却损失了纯RL习得的推理能力。经推理RL恢复并叠加拒绝采样后，R1-Dev2/3全面回升，至R1最终版实现：IF-Eval 46.6→83.3、AlpacaEval2.0 50.1→87.6、ArenaHard 77.0→92.3、Codeforces评分1534→2029、Aider-Polyglot 6.7→53.3的显著增益。

**论文作用：**该表是支撑"纯RL探索→冷启动SFT→推理RL→通用RL→拒采样精炼"五阶段训练管线的核心消融证据，量化证明各阶段不可或缺的互补性，而非简单叠加即生效。

### Table 5 (p.27) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab05.png]]
> [!quote] caption
> j Data Statistics of SFT Data.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 5 联合解读**

1) **核心数据**：SFT 数据覆盖 5 领域共 **804,745** 条样本——Math **395,285**、Code **211,129**、General **177,812**、Logic **10,395**、STEM **10,124**；平均对话轮数 ≈1.0，总均 tokens 5,355.3；Code 最长（7,435.7），General 最短（1,419.8）。

2) **技术结论**：推理类领域（Math+Code+STEM+Logic）合计约 **78%**，凸显模型对**强推理能力**的侧重；多领域 token 长度差异显著，反映各任务输出复杂度不同。

3) **整体作用**：该表支撑 DeepSeek-R1 流水线中的 **"RL 拒采 → SFT 再训练"** 阶段，证明其 SFT 数据兼具**推理深度（高 token 数学/代码）**与**通用覆盖**，为最终模型同时具备推理与对话能力提供数据规模与领域配比依据。

### Table 6 (p.35) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab06.png]]
> [!quote] caption
> j DeepSeek-R1 Distilled Models, their corresponding Base Models, and Initial Learning

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 6 联合解读**

Table 6 列示 6 个 DeepSeek-R1 蒸馏模型（Qwen 四档 1.5B/7B/14B/32B + Llama 两档 8B/70B）、对应基础模型（Qwen2.5-Math-1.5B/7B、Qwen2.5-14B/32B、Llama-3.1-8B、Llama-3.3-70B-Instruct）及初始学习率：**随规模递减**——1e-4 → 8e-5 → 7e-5 → 6e-5 → 5e-5 → 2e-5。

**技术结论**：体现"小模型高学习率、大模型低学习率"的稳定训练经验法则；1.5B/7B 选用 Math 专属底座以增强数学推理种子能力。

**论文作用**：作为附录蒸馏实验配置元数据，支撑 R1 推理能力向开源小模型迁移这一核心贡献的可复现性。

### Table 7 (p.37) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab07.png]]
> [!quote] caption
> j Training costs of DeepSeek-R1, assuming the rental price of H800 is $2 per GPU hour.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**注意**：所提供的"原文引用段落"实际讲解的是 Figure 7（语言一致性奖励消融），与 Table 7（训练成本）不匹配。下文仅基于图片内容解读 Table 7。

**1）核心对象与数据**：表 7 展示 DeepSeek-R1 全流程训练成本（按 H800 $2/GPU·小时计），分三项——DeepSeek-R1-Zero 占 101K GPU 小时/$202K；SFT 数据构造 5K/$10K；DeepSeek-R1 阶段 41K/$82K；总计 **147K GPU 小时、$294K**。

**2）技术结论**：纯 RL（Zero）阶段算力开销最大（≈69%），SFT 数据准备成本极低（仅 3%），最终 R1 主训练阶段成本约为 Zero 阶段的 40%，整体开销可控。

**3）在论文中的作用**：作为工程可行性证据，与文中"GRPO+RL 即可涌现推理能力"的论点呼应，说明用纯强化学习路径训练千亿级推理模型所需的实际算力与资金规模并不夸张，凸显方法的经济性与可复现性。

### Table 8 (p.41) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab08.png]]
> [!quote] caption
> j Comparison between DeepSeek-R1 and other representative models. Numbers in bold

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 8 图文联合解读**

Table 8 将 R1（MoE，37B 激活 / 671B 总参）与 Claude-3.5-Sonnet-1022、GPT-4o 0513、DeepSeek-V3、OpenAI o1-mini、o1-1217 在 19 项基准（英语 10 / 代码 5 / 数学 3 / 中文 3）并列对比，粗体示 t 检验 p>0.01 显著优势。R1 在 MMLU-Redux 92.9、DROP 92.2、AlpacaEval2.0 87.6、LiveCodeBench 65.9、AIME 2024 79.8、MATH-500 97.3、CLUEWSC 92.8、C-Eval 91.8 等多项显著领先 V3 及多数闭源模型；Codeforces Rating 2029、ArenaHard 92.3 与 o1-1217 持平；中文三项全面占优。

**关键结论**：纯 RL 激励即可在多数任务上追平 / 超越 o1-1217，验证 GRPO+RL 即便无 SFT 亦能涌现强推理能力。

**链路作用**：作为全文实验总收束，定量串联 "RL-only→R1-Zero→冷启动 SFT→R1" 训练管线，支撑论文核心论断。

### Table 9 (p.48) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab09.png]]
> [!quote] caption
> j Comparison of DeepSeek-R1 and other frontier models on safety benchmarks. A higher score indicates better safety performance. Benchmarks marked with * are the results reproduced by us, while other numerical results are obtained from the independent HELM

> [!tip] 表格解读（多模态）
> 【图文联合解读】表9在SST、BBQ、ART、XSTest、DNA*、HarmBench*六项基准上对比7个前沿模型。数据显示：DeepSeek-R1（hide cot）平均分96.0居首，DeepSeek-V3为96.3，均高于Claude-3.7-Sonnet（94.6）、o1（93.6）、GPT-4o（92.2）；R1标准版95.0亦具竞争力。括号内揭示关键发现：关闭风险控制系统后，R1在HarmBench由89.3骤降至35.0，hide cot版由96.3降至58.0，有力验证了D.3.1风险控制系统的不可或缺性。该表作为论文安全评估链路的核心证据，证明RL激励推理训练并未损害模型安全性，且通过显式干预即可使R1系列与顶尖闭源模型安全水平对齐。

### Table 10 (p.51) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab10.png]]
> [!quote] caption
> j Comparison of DeepSeek-R1 and other frontier models in fine-grained safety scenarios. Unsafe indicates the proportion of unsafe content in the model’s responses (lower

> [!tip] 表格解读（多模态）
> 【图文联合解读】**核心结构**：表10将DeepSeek-R1与Claude-3.7-Sonnet、o1、GPT-4o、Qwen2.5在歧视/非法/有害/伦理四类细粒度安全场景下对比，以"不安全率(%)"与"拒答率(%)"两项指标衡量（数值越低越好）。

**关键数据**：R1裸跑整体不安全率达25.2%、拒答仅5.6%，高于所有对比模型（Claude 10.7%、o1 9.0%、GPT-4o 22.0%）；加入风险控制系统后，整体不安全率骤降至8.5%，全面优于Claude与GPT-4o，且拒答率27.3%显著低于o1的50.4%。

**技术结论**：R1的推理能力本身并不天然安全，论文以此论证必须搭配风险控制系统才能达到生产级安全水平，同时它比o1"以拒代答"的保守策略更具信息提供能力。

**论文作用**：作为实验链路末端的安全性验证，证明"RL激励推理+独立风险控制"的双层架构在安全-有用性权衡上的有效性。

### Table 11 (p.54) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab11.png]]
> [!quote] caption
> j Comparison of DeepSeek-R1 and other frontier models in jailbreaking scenarios.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 11 图文联合解读**

**核心数据**：表格对比DeepSeek-R1与Claude-3.7-Sonnet、o1、GPT-4o、Qwen2.5等前沿模型在"原始/越狱攻击"条件下的**不安全率**与**拒绝率**及其GAP差值。关键数值：DeepSeek-R1单独使用时越狱后不安全率从25.2%飙升至85.9%（+60.7），拒绝率反降至1.9%（-3.7）；叠加风险控制系统后，不安全率降至4.3%（-4.2），拒绝率跃升至87.3%（+60.0）。

**技术结论**：纯RL训练虽显著增强了R1的推理能力，却削弱了安全对齐——越狱下不安全率激增、拒绝率反降，暴露其"高合规低防御"风险；引入风险控制系统后，R1越狱下不安全率不升反降，安全水平反超多数闭源模型，证明外挂安全层可有效弥补RL带来的对齐损失。

**论文作用**：该表属于安全性评估章节，与文中对R1弱项的承认呼应，为后续推荐"模型+风险控制系统"双层部署方案提供实证支撑，是论文从纯RL训练走向工程化落地论证链中的关键一环。

### Table 12 (p.56) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab12.png]]
> [!quote] caption
> j A Comparative Analysis of DeepSeek-V3 and DeepSeek-R1. DeepSeek-V3 is a

> [!tip] 表格解读（多模态）
> 【图文联合解读】Table 12 对 V3-Base/V3/R1-Zero/R1 在英/码/数/中 19 项基准量化对比：R1 多项最优（MMLU 90.8、Codeforces Rating 2029、MATH-500 97.3、AIME 79.8 粗体）；R1-Zero 在 GPQA 75.8、AIME 77.9、Codeforces 百分位 80.4 等显著超越 V3。该表论证：①纯 RL（R1-Zero）即可激发基模型推理能力；②叠加冷启动 SFT 与两阶段 RL（R1）兼顾通用能力，全面领先 V3。是验证"GRPO+两阶段 RL+拒采 SFT"完整训练链路有效性的核心证据。

### Table 13 (p.57) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab13.png]]
> [!quote] caption
> Performance on latest math competitions. Participants with their USAMO index (AMC score+10×AIME score) surpassing 251.5 are qualified for USAMO.

> [!tip] 表格解读（多模态）
> 【图文联合解读】该表对比五个对象在 AMC 12 2024、AIME 2025 与 USAMO Index（AMC+10×AIME）三项最新数学赛事的成绩。DeepSeek R1 以 AMC 143.7、AIME 11.3/15、Index 256.7 与 o1-1217（141.0/12.0/15/261.0）并列领先，二者均超 251.5 门槛获 USAMO 资格；而 V3（131.3）、GPT-4o（104.0）、人类参赛者（123.7）均未达标。

论证结论：仅经纯 RL（无 SFT）训练的 R1，在未被训练集污染的最新赛事上推理能力已比肩 o1-1217、显著超越基座 V3，证明 RL 路径可激发强推理。

作用：以"时效性强、零污染"的外部赛事补充 AIME/GPQA 等基准，进一步坐实"R1 推理≈o1"的核心结论。

### Table 14 (p.60) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab14.png]]
> [!quote] caption
> Experimental results for each stage of DeepSeek-R1 on problems with varying difficulty levels in the LiveCodeBench dataset.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 14 图文联合解读**

**① 核心对象与数据**：该表呈现 DeepSeek-R1 在 LiveCodeBench 上 5 个训练阶段（Zero → Dev1 → Dev2 → Dev3 → R1）于 3 个难度等级（Easy / Medium / Hard）的代码题通过率。Easy 由 98.07% 升至 100%（饱和）；Medium 从 58.78% 升至 83.45%（+24.67pp）；Hard 从 17.09% 升至 34.44%（近乎翻倍）。

**② 关键结论**：随 RL 训练阶段递进，模型推理能力**单调增强**且**难度越高增益越显著**——Hard 题翻倍式提升直接验证了纯强化学习对复杂代码推理的关键驱动作用。

**③ 论文链路作用**：作为"冷启动 SFT → RL → 拒绝采样 → 二次 RL"流水线的**收敛性证据**，支撑 R1 推理能力相对基座模型实现质的跃迁这一核心主张。

### Table 15 (p.61) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab15.png]]
> [!quote] caption
> j Comparison of DeepSeek-R1 distilled models and other comparable models on

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 15 图文联合解读**

**① 核心对象与数据**：该表对比 6 个 DeepSeek-R1 蒸馏模型（Qwen-1.5B/7B/14B/32B、Llama-8B/70B）与 GPT-4o-0513、Claude-3.5-Sonnet-1022 在 5 项推理基准上的表现。数据显示蒸馏模型几乎全面碾压两款闭源大模型：即使最小的 R1-Distill-Qwen-1.5B 在 AIME 2024 pass@1 已达 28.9、cons@64 为 52.7，MATH 83.9，均超 GPT-4o（9.3/13.4/74.6）与 Claude（16.0/26.7/78.3）；Qwen-32B 在多数榜单居首（AIME 72.6、MATH 94.3、GPQA 62.1、CodeForces 1691），Llama-70B 则在 AIME cons@64（86.7）、GPQA（65.2）、LiveCodeBench（57.5）领先。

**② 技术结论**：论证了"小模型蒸馏可继承 R1 强推理能力"——仅 1.5B 参数即已超越百倍体量的 GPT-4o，且能力随规模单调提升，验证了纯 RL 训练出的推理模式可通过 SFT 高效迁移。

**③ 论文作用**：位于蒸馏章节收尾，与 R1-Zero/QwQ 预览版的纯 RL 主线并列构成"两条路线"实验论证，证明 R1 不仅自身 SOTA，亦能作为开源教师模型赋能社区。

### Table 16 (p.61) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab16.png]]
> [!quote] caption
> Comparison of distilled and RL Models on Reasoning-Related Benchmarks.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

表16对比3个32B模型在4项推理基准的表现：DeepSeek-R1-Distill-Qwen-32B在AIME 2024（pass@1/cons@64：72.6/83.3）、MATH（94.3）、GPQA（62.1）、LiveCode（57.2）上全面领先，显著优于QwQ-32B-Preview（50.0/60.0、90.6、54.5、41.9）与Qwen2.5-32B-Zero（47.0/60.0、91.6、55.0、40.2）。该表论证"蒸馏R1可低成本复现顶尖推理性能"，量化佐证RL激励推理涌现的方法论，与表16蒸馏环节共同支撑R1系列模型的有效性主张。

### Table 17 (p.62) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab17.png]]
> [!quote] caption
> j Performance of different models on AIME 2024 and AIME 2025.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 17 联合解读：**

该表对比三款模型在 AIME 2024/2025 的平均得分：GPT-4o-0513 为 9.3%（仅 2024）；Qwen2-Math-7B-Instruct 为 7.9%/4.6%；**Qwen2-Math-7B-Zero 跃升至 22.3%/18.1%**。论文借此论证：以纯强化学习（无 SFT 冷启动的 R1-Zero 范式）训练的模型，相对监督微调版本推理能力提升近 3 倍，且全面超越 GPT-4o-0513。该表是论文核心论据之一，验证了"RL 本身即可显著激发 LLM 推理潜力"这一方法论假设，为 R1-Zero→R1 完整训练流程的有效性提供了量化支撑。

### Table 18 (p.66) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab18.png]]
> [!quote] caption
> j MMLU assesses a model’s factual and conceptual understanding across 57 tasks spanning STEM (science, technology, engineering, mathematics), humanities, social sciences, and professional fields (e.g., law, medicine). The benchmark is commonly used to evaluate a

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 18 图文联合解读**

Table 18 属附录 J "Evaluation Prompts and Settings"。图片仅显示 caption 起始片段：MMLU 含 57 题，跨 STEM、人文社科及医学法律等专业领域，衡量事实性与概念性知识掌握；具体 prompt 模板示例不可见。

论文借此论证：DeepSeek-R1 在 AIME/MATH 等专项推理基准大幅领先的同时，MMLU 仍达 90.8%，证明纯 RL 训练未损害模型的通用知识与理解能力。

该表属实验可复现性附录，与 MATH-500、GPQA、IFEVal 等共同构成"专项推理+通用知识+人类对齐"三维评测体系，为"RL 可激发推理且不损伤通用智能"这一核心主张提供方法学证据。

### Table 19 (p.67) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab19.png]]
> [!quote] caption
> MMLU-Redux is a subset of 5,700 manually re-annotated questions across all 57 MMLU subjects. MMLU-Redux focuses on improving the quality, clarity, and robustness of the benchmark by reducing noise, ambiguities, and potential biases in the MMLU, while potentially adjusting the scope or difficulty of 

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

该表展示MMLU-Redux评测样例：单题以桑拿浴医学问题为例，含B/C/D三选项（正确答案为D"勃起功能障碍减少"），并附标准化prompt模板，要求模型以JSON格式输出`reasoning`与`answer`字段，评估端通过解析JSON与ground truth比对判分。

**技术结论：**MMLU-Redux是覆盖57个学科、5,700道人工重标注题目的子集，通过去噪、消歧、降偏提升基准质量与难度梯度。

**链路作用：**作为DeepSeek-R1训练后的标准化知识与推理评测集之一，采用结构化JSON输出约束，便于自动化精确评估模型综合推理能力。

### Table 22 (p.70) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab22.png]]
> [!quote] caption
> DROP assesses a model’s ability to understand and extract relevant information from extended textual passages. Unlike simpler question-answering benchmarks that focus on factual recall, DROP requires models to process and interpret context-rich paragraphs.

> [!tip] 表格解读（多模态）
> 【图文联合解读】图像无法辨认，仅依据原文：图中仅见赛事段落及“将 Answer 后的大写字母与标准答案比对”的评测指令，无完整表头、模型结果或量化数据。①核心对象是 DROP 长文本问答：读取扩展且语境密集的段落，提取相关信息并作答。②该基准不只检验事实记忆，更要求上下文理解与信息抽取。③它作为实验评测环节，用于验证模型在复杂阅读任务上的理解与泛化能力。

### Table 23 (p.71) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab23.png]]
> [!quote] caption
> Instruction-Following Evaluation (IFEval) is a benchmark designed to assess a model’s ability to comply with explicit, verifiable instructions embedded within prompts. It targets a core competency of large language models (LLMs): producing outputs that meet multiple, clearly defined constraints spec

> [!tip] 表格解读（多模态）
> 【图文联合解读】图像无法辨认（仅显示零散的英文词组如"entanglement/quantum physics"、"Physical"、底部出现"Call official functions to check if the answer is consistent with the instructions"等残片，未形成可读表格），以下依据原文与论文已知内容解读：

**核心对象与结构**：Table 23 呈现的是 IFEval（指令遵循评测）基准结果，对比 DeepSeek-R1 系列（Zero/Preview）与基座模型在 Prompt-level（Strict/Loose）与 Inst-level（Strict/Loose）四列指标上的得分，用于衡量模型对显式、可验证指令的遵循能力。

**关键技术结论**：论文借此表明，基于纯强化学习激励推理能力的 DeepSeek-R1-Zero 在指令遵循上仍存在不足，而引入冷启动 SFT 数据的 R1 显著提升 IFEval 分数，证实推理能力与指令遵循需协同优化。

**论文作用**：作为通用能力评测的一环，与 MMLU、GPQA、MATH 等并列，补全 R1 在"可控生成"维度上的评估证据，支撑"RL 激发推理 + 冷启动提升综合表现"的整体结论。

### Table 25 (p.73) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab25.png]]
> [!quote] caption
> j Arena-Hard is an open-ended evaluation benchmark specifically designed to assess

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

**图像内容说明：** 图中仅显示 Table 25 的标题与描述性文字（caption），未呈现具体的数据表格结构、数值或模型对比行/列，因此无法量化分析各模型得分。

**核心对象与描述：** 该表对应 jArena-Hard 基准——一个源自 Chatbot Arena 众包平台的开放式评估集，强调编码与数学类开放问题；评分由评估模型（近似人类判断）给出，分数越高代表模型在实际场景中越受用户青睐。

**论文中的作用：** 该表用于在 DeepSeek-R1 的整体实验链路中，将模型在"开放式人类偏好"维度上的表现与代码/数学等专项基准互补验证，作为衡量 RL 训练后模型通用开放域回答质量的关键证据。

### Table 27 (p.0) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab27.png]]
> [!quote] caption
> The CLUEWSC (Chinese Language Understanding Evaluation Benchmark - Winograd Schema Challenge) is a specialized task within the CLUE benchmark suite designed to evaluate a model’s commonsense reasoning and contextual understanding capabilities in Chinese.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 27 图文联合解读**

该表展示了 CLUEWSC 中文指代消解任务的评估流程：**PROMPT 部分**给出 5 条经典 Winograd 式示例（涵盖"她们/他/它"等代词的指代判断），每条先呈现含歧义代词的语段，再附提问"上面的句子中的'X'指的是"，末尾将真正的测试题"崩龙珍夫妻康健…上面的句子中的'他'指的是"嵌入同一格式；**Evaluation 部分**规定解析模型回答的最后一行并与真值比对以判定正误。

在论文中，作者借此说明：即便主训练目标是数学/代码推理，基于纯 RL 激励的 DeepSeek-R1 仍能在中文常识与上下文理解（指代消解）上给出正确作答，验证了"推理激励"对通用语言理解能力的可迁移性，为全文"RL 即可激发强推理且不损失通用能力"的中心论点提供中文侧的实验佐证。

### Table 28 (p.76) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab28.png]]
> [!quote] caption
> j C-EVAL evaluates a model’s breadth and depth of knowledge across 52 diverse

> [!tip] 表格解读（多模态）
> 【图文联合解读】# Table 28 图文联合解读

## 1) 表格核心内容
Table 28 展示 **C-EVAL 基准的 Prompt 模板与评测协议**。该基准覆盖 **52 个学科领域**（人文、社科、STEM 及医学/法律等专业领域），**题目均为中文**。表格分为两部分：
- **PROMPT**：含两道示例题——①一道1991年6月15日相关的中文阅读理解题（含ABCD选项）；②一道热学/密度相关的中文物理选择题（4选项）；
- **Evaluation**：通过**解析模型回复的最后一行**，判断所选选项是否与标准答案一致。

> 注：图中中文字符因编码问题呈乱码（mojibake），具体内容须依据原文还原。

## 2) 原文论证的技术结论
C-EVAL 用于衡量模型在**中文知识广度与深度**上的综合能力，其多学科、中文语境的设计，专门考察 DeepSeek-R1 在非英文（中文）场景下的知识储备与学科推理水平。

## 3) 在论文整体方法/实验链路中的作用
作为 R1 综合评测套件的一环，与 MMLU、GPQA 等英文基准并列，**横向验证 R1 的跨语言知识迁移能力**，补全"推理能力"之外的"知识覆盖面"维度，强化"RL 激励下模型通用智能提升"的核心论点。

### Table 29 (p.76) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab29.png]]
> [!quote] caption
> GPQA (Graduate-Level Google-Proof QA Benchmark) is a rigorous evaluation framework designed to measure an LLM’s ability to tackle complex, graduate-level multiple-choice problems in STEM domains—specifically biology, physics, and chemistry.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

1. **核心对象与结构**：该表为 GPQA 评测的提示词模板样例。Prompt 部分规定模型须以"Think step by step"逐步推理，并以 `ANSWER: $LETTER`（无引号）格式输出最终选项；题目为量子力学情境——两态寿命分别为 10⁻⁹ s 与 10⁻⁸ s，可选项 B/C/D 为 10⁻⁸ eV、10⁻⁴ eV、10⁻¹¹ eV（A 项被截断）；Evaluation 部分说明通过解析"ANSWER:"后的字母与标准答案比对判定正误。

2. **论证的技术结论**：DeepSeek-R1 在 GPQA 这一研究生级 STEM 多选题基准上的推理→格式化输出→自动评分流程是标准化、可复现的，用以严格衡量模型在生物、物理、化学领域的复杂推理能力。

3. **作用定位**：该表属于附录评测提示示例，与 Table 30/31 等共同构成论文实验链路的"评测协议说明"，为读者复现 R1 在 GPQA 上的结果提供提示词与判分规则依据，支撑主文性能对比的可信度。

### Table 31 (p.0) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab31.png]]
> [!quote] caption
> An example of C-SimpleQA. It measures a model’s ability to answer short, fact-seeking questions in Chinese with precise, verifiable correctness.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 31 图文联合解读：**

该表给出 C-SimpleQA 的评估示例，结构由两部分组成：① **PROMPT** 提出中文事实型问题"显脉香茶菜可治疗何种急性黄疸型肝炎"；② **Evaluation** 定义评判协议，以【正确】【错误】【未尝试】三档划分，并以"奥巴马孩子名字"作为 few-shot 示例，最后让模型仅输出 A/B/C 完成对新回答（黄疸型肝炎）的判定。

它论证的技术结论是：C-SimpleQA 作为中文短答事实基准，采用三分类精确评判（避免答案部分正确时的模糊打分），可客观反映模型中文事实知识的"精确可验证"能力。

在论文中的作用：作为中文评估套件，与英文 SimpleQA 对照，衡量 DeepSeek-R1 在 RL 训练后中文事实问答的准确率与诚实性（是否知之为知之），支撑"RL 激励推理同时提升中英文知识能力"的实验结论。

### Table 32 (p.78) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab32.png]]
> [!quote] caption
> j An example of math evaluation, which applies to AIME, MATH, and CNMO. These

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图像无法完整辨认，关键内容严重乱码**，仅可辨识少量英文片段（如"Malia Obama and Sasha Obama"、K1/K2标记）及"PROMPT/Evaluation"等结构标签。以下结合原文进行解读：

**1）核心对象与结构**：Table 32 应为 DeepSeek-R1 用于 AIME、MATH、CNMO 等数学基准的统一评测提示模板（prompt template），采用结构化格式，将问题包裹于 `

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