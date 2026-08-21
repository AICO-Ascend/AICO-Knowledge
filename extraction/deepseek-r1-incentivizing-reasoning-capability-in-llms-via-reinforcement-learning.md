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
![[assets/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-p06.png]]
> [!quote] caption
> In the initial stage, we collect thousands of cold-start data that exhibits a conversational, human-aligned thinking process. RL training is then applied to improve the model perfor- mance with the conversational thinking process and language consistency. Subsequently, we apply rejection sampling and SFT once more. This stage incorporates both reasoning and non- reasoning datasets into the SFT pro

> [!tip] 技术解读（多模态）
> # Figure Description

**Architecture/Components/Data Flow:**

The figure depicts DeepSeek-R1's multi-stage training pipeline as four sequential columns flowing left to right. **Stage 1** begins with cold-start SFT data (purple) feeding into a Supervised Fine-Tuning step (SFT, blue), followed by rejection sampling that produces intermediate checkpoint **Dev1**. **Stages 2–3** alternate reasoning data (purple) with Reinforcement Learning passes (RL, blue) — the first RL optimizes reasoning/language consistency, yielding **Dev2**; the second incorporates preference data, yielding **Dev3**. **Stage 4** applies a final RL pass on preference data to produce **DeepSeek-R1**. Purple boxes denote data inputs; blue boxes denote training operations; black triangles indicate stage transitions.

**Key Technical Takeaway:**

DeepSeek-R1 improves over R1-Zero's poor readability/language-mixing by injecting **cold-start human-aligned data** before RL, then iteratively interleaving reasoning-focused RL, rejection-sampled SFT with reasoning+non-reasoning data, and preference-driven RL.

**Caption (verbatim):**

"Figure 2 |The multi-stage pipeline of DeepSeek-R1. A detailed background on DeepSeek-V3 Base and DeepSeek-V3 is provided in Supplementary A.1. The models DeepSeek-R1 Dev1, Dev2, and Dev3 represent intermediate checkpoints within this pipeline."

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