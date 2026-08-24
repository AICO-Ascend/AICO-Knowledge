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
> 【图文联合解读】Table 1为DeepSeek-R1-Zero训练提示模板，含三要素：①"User/Assistant"对话框架；②`<think>...`与`<answer>...</answer>`双标签，强制模型先输出推理再给答案；③"User: prompt"占位符在训练时替换为具体题。

原文用它论证：模板极简（仅格式约束、零示例），配合GRPO规则奖励即可让模型在纯RL下自发涌现长链CoT与自我反思，证明推理能力无需SFT冷启动即可"从零激励"。

链路作用：作为R1-Zero纯RL路线的输入接口，与后续R1（SFT冷启动+拒采样）形成对照基线，支撑"RL可独立激发推理"这一核心主张。

### Table 2 (p.5) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab02.png]]
> [!quote] caption
> An interesting “aha moment” of an intermediate version of DeepSeek-R1-Zero. The model learns to rethink using an anthropomorphic tone. This is also an aha moment for us, allowing us to witness the power and beauty of reinforcement learning.

> [!tip] 表格解读（多模态）
> 【图文联合解读】该表呈现DeepSeek-R1-Zero中间版本对一道数学题（已知a>1，求方程 a−a+x=x 实数解之和）的思维链过程。模型先两边平方展开为四次方程 x⁴−2ax²−x+(a²−a)=0，随后自发输出"Wait, wait. Wait. That's an aha moment I can flag here"，并主动决定"reevaluate this step-by-step"重新审视前序推导。

**关键结论**：纯强化学习（无SFT冷启动数据）即可激发模型涌现高阶元认知行为——自主反思、重新评估推理路径，并以拟人化语气表达"顿悟"。

**方法链路作用**：该案例是R1-Zero（纯RL）路径的核心定性证据，与图2所示的"冷启动SFT+RL"两阶段路线形成对照。它证明推理能力的自我反思与涌现不依赖显式监督，是RL驱动的R1训练范式成立的实证支撑。

### Table 3 (p.8) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab03.png]]
> [!quote] caption
> Experimental results at each stage of DeepSeek-R1. Numbers in bold denote the performance is statistically significant (t−test with p<0.01).

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 3 图文联合解读**

1）**核心对象与数据**：表展示 DeepSeek-R1 训练各阶段（R1-Zero → R1-Dev1/2/3 → R1）在英语、代码、数学、中文四类共 19 个基准上的表现。关键量化变化：AlpacaEval2.0 从 24.7 跃至 87.6，ArenaHard 53.6→92.3，IF-Eval 46.6→83.3，Aider-Polyglot 12.2→53.3，Codeforces 评分 1444→2029；加粗值经 t 检验（p<0.01）显著。

2）**技术结论**：纯 RL 的 R1-Zero 在推理任务（AIME 77.9、MATH-500 95.9）已很强，但通用能力（AlpacaEval 24.7、Aider 12.2）较弱；引入冷启动 SFT 与多阶段 RL 后，R1 在所有维度全面提升，证明"RL 激发推理 + SFT 补齐通用能力"的两阶段路线有效。

3）**论文作用**：作为实验核心证据，串联"R1-Zero 验证纯 RL 可行性 → R1-Dev 调试拒采/语言一致 → R1 最终成型"的方法链，支撑论文主张。

### Table 4 (p.18) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab04.png]]
> [!quote] caption
> j Description of RL Data and Tasks.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**注意**：图片实际内容为附录 **B.2 Reward Model Prompt**（奖励模型评判提示模板），并非 Table 4（RL 数据与任务描述），图文存在不匹配。以下按图片实际内容解读：

1) **核心对象**：一段用于奖励模型/评判的 LLM-as-judge 提示词，要求模型以"公正裁判"身份对两位助手（Assistant A/B）的回答做配对比较；评判维度涵盖 helpful/relevant/concise、创造性与信息完整性；输出为 5 级偏好标签（"A 显著更好"→"B 显著更好"含平局），以 `[[AB]]/[[BA]]` 强制位置交换以缓解位置偏置。

2) **论证结论**：DeepSeek-R1 在通用对齐/偏好类基准（如 Arena-Hard、AlpacaEval）上的胜率提升由该类 GPT-4-based 成对偏好奖励驱动，而非仅靠规则化 RL 奖励。

3) **链路作用**：该提示是 R1 训练管线中 **偏好奖励信号**的生成接口，与规则化准确率奖励并行，构成"规则+偏好"双轨奖励，为 RL 阶段对齐人类偏好提供监督。

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
> 【图文联合解读】**表格核心数据**
该表对比5个对象在AMC 12 2024、AIME 2025实测成绩及USAMO指数：DeepSeek R1（143.7 / 11.3/15 / 256.7）、OpenAI o1-1217（141.0 / 12.0/15 / 261.0）、DeepSeek V3（98.3 / 3.3/15 / 131.3）、GPT-4o 0513（84.0 / 2.0/15 / 104.0）、人类参赛者均值（61.7 / 6.2/15 / 123.7）。

**关键结论**
R1以AMC 143.7居首，USAMO指数256.7超过251.5入围线，与o1（261.0）双双达USAMO级；V3与GPT-4o均远未达标。

**论文中作用**
作为外部真实场景验证，证明纯RL训练的R1在最新奥赛实战中达到与OpenAI o1比肩的竞赛级推理能力，支撑全文"用RL激励推理能力"的核心方法论主张。

### Table 14 (p.60) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab14.png]]
> [!quote] caption
> Experimental results for each stage of DeepSeek-R1 on problems with varying difficulty levels in the LiveCodeBench dataset.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**1) 核心对象与数据**
Table 14 展示 DeepSeek-R1 五个训练阶段（Zero→Dev1→Dev2→Dev3→最终 R1）在 LiveCodeBench 三档难度题目上的通过率：Easy 由 98.07 升至 100.00；Medium 由 58.78 升至 83.45；Hard 由 17.09 升至 34.44（近乎翻倍）。

**2) 关键论证结论**
该表量化证明：随 RL 训练阶段推进并叠加冷启动 SFT，模型代码推理能力呈单调增强；Hard 档近 2 倍跃升是 R1 推理能力涌现的核心实证，支撑"纯 RL 已可激发推理、冷启动微调进一步强化"的迭代路径有效。

**3) 在论文中的作用**
与 AIME、MATH 等基准并列，共同刻画 R1 全开发链路中"推理能力逐步涌现"的实验轨迹，验证整体方法闭环。

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
> 【图文联合解读】**表16核心**：对比三款32B级模型在AIME 2024（pass@1 / cons@64）、MATH、GPQA、LiveCode 四个推理基准的表现。DeepSeek-R1-Distill-Qwen-32B 全面领先（AIME 72.6 / 83.3，LiveCode 57.2），显著优于 QwQ-32B-Preview（50.0 / 60.0 / 41.9）与 Qwen2.5-32B-Zero 纯 RL（47.0 / 60.0 / 40.2），各指标平均领先 15–20 分。

**技术结论**：证明 R1 的强推理能力通过蒸馏可高效迁移到 Qwen2.5-32B 基座，远超同规模纯 RL 路线（Qwen2.5-Zero）及同类开源推理模型 QwQ，验证"大模型蒸馏"优于"同规模从零 RL"。

**论文作用**：作为正文"Distill 路径优于同规模 RL"论断的关键实证，与"RL 训 R1、Distill 向下分发"的双轨设计形成互补。

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
> 【图文联合解读】表19呈现MMLU-Redux（57科目、5700题人工重标注子集）评测Prompt样例：以桑拿益处四选一题为载体，要求模型"先推理后选择"并以JSON格式输出`{"reasoning", "answer"}`，评估端解析后与ground truth比对。原文借此论证：经GRPO+RL训练后，模型在通用知识基准上仍保留结构化多步推理与指令遵循能力，验证RL未损害通用性。表中JSON结构化输出约束是实验链路中"推理能力不损通用能力"回归验证的关键评测协议。

### Table 22 (p.70) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab22.png]]
> [!quote] caption
> DROP assesses a model’s ability to understand and extract relevant information from extended textual passages. Unlike simpler question-answering benchmarks that focus on factual recall, DROP requires models to process and interpret context-rich paragraphs.

> [!tip] 表格解读（多模态）
> 【图文联合解读】表22给出DROP提示模板：含3个NFL段落问答示例、1个长文目标，要求逐步推理并以“Answer: $ANSWER”作答；目标答案“ Rivers传多少码”为231码。评测端比对“Answer:”后的结果与标准答案。它说明DROP重在长文本信息提取、关系理解与算术，而非简单事实记忆；论文借此检验RL模型能否将上下文理解与推理能力迁移到阅读理解，补足简单QA评测。

### Table 23 (p.71) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab23.png]]
> [!quote] caption
> Instruction-Following Evaluation (IFEval) is a benchmark designed to assess a model’s ability to comply with explicit, verifiable instructions embedded within prompts. It targets a core competency of large language models (LLMs): producing outputs that meet multiple, clearly defined constraints spec

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图像无法直接呈现 Table 23 的数值对比表**，仅展示 IFEval 的一个示例 Prompt：要求将量子纠缠文本以 XML 格式总结、且少于 4 句话，Evaluation 说明通过调用官方函数校验指令一致性。

**结合原文解读**：
1. **核心对象**：Table 23 是 IFEval 基准结果，对比 DeepSeek-R1 系列（Zero/Preview）与基座模型在 Prompt-level（Strict/Loose）与 Inst-level（Strict/Loose）四个维度的得分。
2. **技术结论**：论证 R1-Zero/R1-Preview 在显式、可验证指令遵循上显著优于基座，验证 GRRL 训练未损害指令遵从能力。
3. **链路作用**：与 Table 22 等共同构成"综合能力"评测闭环，证明推理强化在提升数学/代码的同时，不牺牲指令对齐等通用能力。

### Table 24 (p.72) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab24.png]]
> [!quote] caption
> FRAMES (Factuality, Retrieval, And reasoning MEasurement Set) is a comprehensive benchmark designed to evaluate core components of retrieval-augmented generation (RAG) systems. Our evaluation employs the benchmark’s official "Oracle Prompt" configuration. In this setting, each test prompt includes t

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

**1) 核心对象与结构**：Table 24 展示 FRAMES 基准的"Oracle Prompt"评测范式，含两部分——**PROMPT 模板**（注入完整维基文章+多跳推理查询，本例为"未来妻子姓名"题，涉及第15位第一夫人母亲的名字与第2位被刺杀总统母亲的娘家姓，标准答案"Jane Ballou"）与 **Evaluation 模板**（LLM-as-judge 三段式：对比预测/真值、判定输出 TRUE/FALSE）。

**2) 关键结论**：该表论证"隔离检索、纯测推理"——因外部文档已全部注入，无需 BM25 等检索器，故可直接衡量模型对给定上下文的综合推理与事实合成能力。

**3) 在论文中的作用**：作为附录评测规范，与第7章主表（FRAMES 准确率）配套，揭示 DeepSeek-R1 在多跳事实推理任务上的评估协议，强化"RL 激励的推理能力可泛化至复杂 RAG 场景"这一核心主张。

### Table 25 (p.73) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab25.png]]
> [!quote] caption
> j Arena-Hard is an open-ended evaluation benchmark specifically designed to assess

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

**图像内容说明：** 图中仅显示 Table 25 的标题与描述性文字（caption），未呈现具体的数据表格结构、数值或模型对比行/列，因此无法量化分析各模型得分。

**核心对象与描述：** 该表对应 jArena-Hard 基准——一个源自 Chatbot Arena 众包平台的开放式评估集，强调编码与数学类开放问题；评分由评估模型（近似人类判断）给出，分数越高代表模型在实际场景中越受用户青睐。

**论文中的作用：** 该表用于在 DeepSeek-R1 的整体实验链路中，将模型在"开放式人类偏好"维度上的表现与代码/数学等专项基准互补验证，作为衡量 RL 训练后模型通用开放域回答质量的关键证据。

### Table 26 (p.74) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab26.png]]
> [!quote] caption
> AlpacaEval 2.0 is an open-ended evaluation dataset, similar in nature to ArenaHard, and leverages an LLM to assess model performance on subjective tasks. However, in contrast to ArenaHard, the prompts in AlpacaEval 2.0 are generally less challenging and only a small subset necessitates the deploymen

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读（Table 26）：**

**1）表格内容：** 该表展示了 AlpacaEval 2.0 的 LLM-as-Judge 评估 Prompt 模板。以"What are the names of some famous actors that started their careers on Broadway?"为例，定义了 System 角色（高效评估员，输出排行榜）、User 指令（含 Instruction 和 JSON 格式的 Model Outputs，含 model_identifier "m"/"M" 与 output 字段），最终要求评估器仅输出获胜模型的标识符（m 或 M），实现自动化两两对比打分。

**2）原文论点：** 表格揭示了 AlpacaEval 2.0 依赖 LLM 裁判对模型输出进行开放式主观评估的机制，相比 ArenaHard 提示更简单、少需深度推理。

**3）论文作用：** 作为 DeepSeek-R1 主实验评估链路（与 GPT-4o、Claude 等对比）的核心评测基准之一，用于在开放式指令任务上验证 R1 通过纯 RL 激励获得的对齐与生成质量。

### Table 27 (p.0) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab27.png]]
> [!quote] caption
> The CLUEWSC (Chinese Language Understanding Evaluation Benchmark - Winograd Schema Challenge) is a specialized task within the CLUE benchmark suite designed to evaluate a model’s commonsense reasoning and contextual understanding capabilities in Chinese.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读（Table 27）**

**核心对象与结构：** 表27为CLUEWSC（中文Winograd指代消解）评测Prompt模板，含5个中文小说片段作in-context示例（"他伯父还有许多女弟子""韦大哥…张大义凛然"等），各段追问"她们/他/它"指代；测试题为崩龙珍与鞠琴的故事，要求模型在`<think>`后用一句话答出"他"指谁；评测机制为解析回答最后一行与ground truth比对。

**论证的关键结论：** 原文借此说明DeepSeek-R1在中英文常识推理与指代消解任务上均有效，证明纯RL激励的推理能力具备跨语言、跨任务泛化性。

**在论文中的作用：** 作为附录中多基准Prompt样本之一，与MMLU、GSM8K等评测共同构成"R1通过纯RL获得全面强推理能力"的实验证据链，支撑全文核心方法结论。

### Table 28 (p.76) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab28.png]]
> [!quote] caption
> C-EVAL evaluates a model’s breadth and depth of knowledge across 52 diverse academic disciplines, spanning humanities, social sciences, STEM (Science, Technology, Engineering, and Mathematics), and other professional fields (e.g., medicine, law). All question in C-Eval are Chinese.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 28 图文解读**

C-EVAL 基准的 Prompt 模板与评测协议。**Prompt** 部分展示两道中文四选一示例：①1991年皮纳图博火山喷发 SO₂ 与气候降温逻辑题；②哈萨克金雕追狼、无电信号仅 3 km 题；均为 A–D 四选项。**Evaluation** 规定解析模型回复的**最后一行**，判断所选选项是否等于标准答案。

该表支撑论文的关键结论：DeepSeek-R1 在 **52 个中文学科**（人文、社科、STEM、医学、法律）上具备与 GPT/Claude 相当的知识广度与深度，证明纯 RL 激励推理并未损害其中文知识储备。

在论文链路中，它与 MMLU、HUMAN-Eval、MATH 等并列为综合能力评估的"中文知识基准"一环，用于横向比较 R1 与 R1-zero、蒸馏模型及主流闭源模型的能力差异。

### Table 29 (p.76) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab29.png]]
> [!quote] caption
> GPQA (Graduate-Level Google-Proof QA Benchmark) is a rigorous evaluation framework designed to measure an LLM’s ability to tackle complex, graduate-level multiple-choice problems in STEM domains—specifically biology, physics, and chemistry.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 29 图文联合解读：**

1) **核心对象与结构**：该表呈现 GPQA 基准的 Prompt 模板与评测规则。Prompt 要求模型逐步思考（Think step by step）后，以 `ANSWER: $LETTER` 格式作答（LETTER∈{A,B,C,D}）。示例为量子力学题：两能级寿命分别为 10⁻⁹ s 和 10⁻⁸ s，候选能差选项为 A) 10⁻⁹ eV、B) 10⁻⁸ eV、C) 10⁻⁴ eV、D) 10⁻¹¹ eV。Evaluation 段规定：解析"ANSWER:"后大写字母与标准答案比对。

2) **论证的技术结论**：该模板用以评估 DeepSeek-R1 在 STEM（生物、物理、化学）研究生级难题上的推理能力，强调显式思维链（CoT）与严格答案格式控制，是验证强化学习后模型推理增强的关键评测之一。

3) **论文链路中的作用**：GPQA 与 MATH、AIME 等并列构成 R1 的"知识密集型推理"评测集，用于证明 GRRL 训练在不损害前沿学科推理的同时显著提升泛化推理能力。

### Table 31 (p.0) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab31.png]]
> [!quote] caption
> An example of C-SimpleQA. It measures a model’s ability to answer short, fact-seeking questions in Chinese with precise, verifiable correctness.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

表31以中文事实型问句"显脉香茶菜可用于治疗急性的什么类型黄疸型肝炎"为待评样例，完整呈现C-SimpleQA的评测提示词结构：由问题、标准答案、模型预测1/2构成，给出【正确】【错误】【未尝试】三类few-shot示范，再以A/B/C单选项强制评分模型新答案。

原文借此论证关键技术结论：采用三档可验证判定（正确/错误/未尝试）替代二元准确率，可显式区分模型的实质性错误与主动弃答，避免对"我不知道"等合理拒答作惩罚性扣分，更公平地量化中文短答案事实检索能力。

在论文链路中，该表作为SimpleQA的中文域并行评测组件，与R1整体实验框架中的多语言事实性问答基准共同支撑"推理能力激励不损害事实正确性"的核心结论。

### Table 32 (p.78) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab32.png]]
> [!quote] caption
> An example of math evaluation, which applies to AIME, MATH, and CNMO. These benchmarks evaluate model performance on mathematical tasks.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 32 图文联合解读**

Table 32 为 R1 在 AIME、MATH、CNMO 三大数学任务上的**统一评测模板**，由 PROMPT 与 Evaluation 两栏构成：PROMPT 给出示例题（求使 b-eautiful 整数超过 10 个的最小 b≥2），要求模型逐步推理并以 `\boxed{}` 输出最终数值；Evaluation 规定用 SymPy 解析 `\boxed{}` 内的数学表达式，通过基于规则的判分器与标准答案比对（图中实为开放求解题，并非 A/B/C 选择题）。

论文借此论证两点关键结论：① 纯 RL 训练即可激发 R1 的多步数学推理能力，无需过程监督；② 采用规则化判分（非 LLM 评判），保证了数学评测的客观性与可复现性。

该表位于实验验证环节，作为数学基准的标准化提示模板，使所有基线模型在同一格式下公平对比，是支撑 "R1 在数学推理上逼近 o1" 这一核心结论的实验基础设施。

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