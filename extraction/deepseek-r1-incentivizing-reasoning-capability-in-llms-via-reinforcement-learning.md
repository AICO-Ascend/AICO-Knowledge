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

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.3) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab01.png]]
> [!quote] caption
> j Template for DeepSeek-R1-Zero. prompt will be replaced with the specific reasoning

> [!tip] 表格解读（多模态）
> **Main figure description:**

This is Table 1 — a **Jinja chat template (`jTemplate`)** used to format training data for the **DeepSeek-R1-Zero** reasoning model.

- **Components / Structure:**
  - A system-style instruction block defining the User–Assistant conversational contract.
  - A placeholder `{prompt}` that gets substituted at training time with the actual reasoning question.
  - Special **delimiter tokens** (the `¶` glyphs render broken `<`/`>` markers in the source, intended as XML-style tags) wrapping the model's internal **reasoning process** and the **final answer** as distinct fields.
- **Data flow:** `{prompt}` (reasoning question) → tokenized User turn → Assistant generates `<thinking>...</thinking><answer>...</answer>` sequence → gradient updates during RL training.

**Key technical takeaway:** By structurally separating *chain-of-thought reasoning* from the *final answer* via dedicated tags, R1-Zero can apply a rule-based reward only on the answer while the entire reasoning trace remains part of the optimization trajectory, enabling "reasoning-emergent" RL without supervised fine-tuning.

**Caption (verbatim):**
> Table 1  jTemplate for DeepSeek-R1-Zero. prompt will be replaced with the specific reasoning question during training.

### Table 2 (p.5) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab02.png]]
> [!quote] caption
> j An interesting “aha moment” of an intermediate version of DeepSeek-R1-Zero. The

> [!tip] 表格解读（多模态）
> **Description**

This figure is a qualitative example (Table 2) rather than a system diagram, illustrating a single inference trace from DeepSeek-R1-Zero. The flow is linear: a math question is fed to the policy, which autoregressively emits a chain-of-thought involving algebraic manipulation (squaring, rearranging a radical equation), then self-interrupts with an anthropomorphic reflection ("Wait, wait. Wait. That's an aha moment I can flag here."), and finally restarts the derivation from scratch.

**Key technical takeaway:** Pure RL can spontaneously elicit self-correction and reflective reasoning — emergent meta-cognitive behavior arises without any supervised reasoning data being injected into training.

**Caption (verbatim):**

Table 2 | An interesting "aha moment" of an intermediate version of DeepSeek-R1-Zero. The model learns to rethink using an anthropomorphic tone. This is also an aha moment for us, allowing us to witness the power and beauty of reinforcement learning.

### Table 3 (p.8) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab03.png]]
> [!quote] caption
> summarizes the performance of DeepSeek-R1 across multiple developmental stages, as outlined in Figure 2. A comparison between DeepSeek-R1-Zero and DeepSeek-R1 Dev1 reveals substantial improvements in instruction-following, as evidenced by higher scores on the IF-Eval and ArenaHard benchmarks. Howeve

> [!tip] 表格解读（多模态）
> The text you've shared does not actually contain a figure, caption, or any description of an architecture/components/data flow diagram. The excerpt is purely narrative prose discussing DeepSeek-R1's performance across developmental stages (referring generically to "Figure 2" and "Table 3" without describing them). It only contains the following elements:

- A paragraph comparing DeepSeek-R1-Zero, Dev1, and Dev2 across benchmarks (IF-Eval, ArenaHard, AIME).
- A page number ("8") at the bottom.

**I cannot describe an architecture or data flow that isn't present in the source, and there is no caption to transcribe verbatim.** Fabricating such details would risk inaccuracies.

If you can share the actual figure image, an OCR of the figure region, or the caption text directly, I'd be glad to summarize the architecture/components and transcribe the caption for you.

### Table 5 (p.27) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab05.png]]
> [!quote] caption
> j Data Statistics of SFT Data.

> [!tip] 表格解读（多模态）
> **Description:** Table 5 presents the SFT data composition, organized as a four-column matrix (Domain, Num Samples, Avg Rounds, Avg Tokens) with five domain rows plus a Total row. The "data flow" perspective: Math (395,285) and Code (211,129) dominate the 804,745-sample corpus, followed by General (177,812), Logic (10,395), and STEM (10,124). All domains exhibit predominantly single-turn interactions (Avg Rounds ≈ 1.0–1.1), with token lengths ranging from 1,419.8 (General) up to 7,435.7 (Code).

**Key takeaway:** The SFT corpus is highly skewed toward Math + Code (~75% of samples) and almost entirely single-turn, which the authors flag as a likely constraint on DeepSeek-R1's multi-turn conversational ability — flagged as future work.

**Caption verbatim:** "Table 5 |Data Statistics of SFT Data."

### Table 6 (p.35) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab06.png]]
> [!quote] caption
> j DeepSeek-R1 Distilled Models, their corresponding Base Models, and Initial Learning

> [!tip] 表格解读（多模态）
> # Note

The input you provided contains **no figure** — only text from Appendix B.4 of the DeepSeek-R1 report (hyper-parameter descriptions for SFT and Distillation, plus a reference to Table 6). I cannot describe an architecture/diagram/data flow that isn't present.

## What is actually provided (textual hyper-parameter spec)

**Two-stage fine-tuning configuration on DeepSeek-V3-Base:**

| Stage | Epochs | LR schedule | Max context | Batch size |
|-------|--------|-------------|-------------|------------|
| SFT (code-start + 2nd stage) | 2–3 | Cosine decay, 5×10⁻⁵ → 5×10⁻⁶ | 32,768 tok | 128 |
| Distillation (800k samples) | 2–3 | Cosine decay → 1/10× init | 32,768 tok | 64 |

**Key technical takeaway:** SFT uses a fully decayed LR floor (1/100× of init, i.e., 5×10⁻⁶), while distillation only decays to 1/10× of init — suggesting distillation preserves higher adaptive learning capacity than the latter SFT stage. Both share a 32k-token context window, but distillation halves the batch size (64 vs 128), likely to fit the larger student/teacher memory footprint.

## Verbatim caption (the only caption present)

> **Table 6** | DeepSeek-R1 Distilled Models, their corresponding Base Models, and Initial Learning

*(Caption is truncated in the source — it ends mid-sentence after "Initial Learning".)*

### Table 7 (p.37) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab07.png]]
> [!quote] caption
> j Training costs of DeepSeek-R1, assuming the rental price of H800 is $2 per GPU hour.

> [!tip] 表格解读（多模态）
> **Note:** The image shows a *table* (Table 7), not an architecture figure, so I'll describe the table's components and data instead.

**Description (≤120 words):**
The table breaks down the training cost of DeepSeek-R1 across three pipeline stages, with both GPU-hour and USD metrics. Components include: **DeepSeek-R1-Zero** (the RL-only pretraining stage, 101K H800 GPU-hours, $202K — the most expensive component), **SFT data creation** (the smallest cost at 5K hours / $10K), and **DeepSeek-R1** (the final multi-stage training, 41K hours / $82K). The **Total** row aggregates to 147K GPU-hours and $294K, assuming a $2/hour rental rate for H800 GPUs.

**Key technical takeaway:** The computationally dominant stage is RL-based reasoning training (R1-Zero), accounting for ~69% of total GPU-hours and ~69% of total cost, while SFT data creation is nearly negligible (~$10K) — indicating that reinforcement-learning compute, not supervised fine-tuning, is the primary cost driver in modern reasoning models.

**Caption transcribed verbatim:**
"Table 7 jTraining costs of DeepSeek-R1, assuming the rental price of H800 is $2 per GPU hour."

### Table 8 (p.41) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab08.png]]
> [!quote] caption
> j Comparison between DeepSeek-R1 and other representative models. Numbers in bold

> [!tip] 表格解读（多模态）
> **Main figure description**

**Layout:** A benchmark-comparison table with six model columns (Claude-3.5-Sonnet-1022, GPT-4o-0513, DeepSeek-V3, OpenAI o1-mini, OpenAI o1-1217, DeepSeek-R1) and rows grouped into four domains: English (10 tasks), Code (5), Math (3), and Chinese (3), preceded by an architecture block.

**Architecture/components:** DeepSeek-R1 is an MoE model with 37B activated parameters out of 671B total — identical to V3's footprint.

**Key technical takeaway:** Despite the same MoE size as V3, pure RL scaling (R1) yields dramatic gains on reasoning-heavy tasks — AIME 2024 jumps 39.2→79.8 and Codeforces percentile 58.7→96.3 — while only marginally improving English knowledge benchmarks (e.g., GPQA 59.1→71.5), showing RL's effect is concentrated where chain-of-thought reasoning helps most.

**Caption (verbatim):**
"Table 8 j Comparison between DeepSeek-R1 and other representative models. Numbers in bold denote the performance is statistically significant (ttest with >0.01)."

### Table 9 (p.48) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab09.png]]
> [!quote] caption
> j Comparison of DeepSeek-R1 and other frontier models on safety benchmarks. A higher score indicates better safety performance. Benchmarks marked with * are the results reproduced by us, while other numerical results are obtained from the independent HELM

> [!tip] 表格解读（多模态）
> **Description of Table 9:**

This is a comparative benchmark table (not an architectural diagram) showing safety performance across frontier LLMs. **Components/columns:** Row labels list 7 models (Claude-3.7-Sonnet, o1, GPT-4o, Qwen2.5-Instruct-72B, DeepSeek-V3, DeepSeek-R1 hide cot, DeepSeek R1); numerical columns cover 6 safety benchmarks (SST, BBQ, ART, XSTest, DNA*, HarmBench*) plus an Average Score, with parenthetical values indicating pure-model scores without the risk control system. **Data flow:** Models → evaluated on standard safety suites → scores aggregated into an average. **Key technical takeaway:** DeepSeek-R1 achieves a 95.0 average safety score (85.9 without risk-control), comparable to Claude-3.7-Sonnet (94.6) and superior to GPT-4o (92.2) on most benchmarks; notably, HarmBench drops sharply from 89.3 → 35.0 once the risk-control system is removed, indicating R1's safety depends heavily on external guardrails rather than intrinsic alignment.

**Caption (verbatim transcription):**

Table 9 | Comparison of DeepSeek-R1 and other frontier models on safety benchmarks. A higher score indicates better safety performance. Benchmarks marked with * are the results reproduced by us, while other numerical results are obtained from the independent HELM evaluations. The numbers in parentheses represent the results of the pure model without considering the risk control system (introduced in D.3.1).

### Table 10 (p.51) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab10.png]]
> [!quote] caption
> j Comparison of DeepSeek-R1 and other frontier models in fine-grained safety scenarios. Unsafe indicates the proportion of unsafe content in the model’s responses (lower

> [!tip] 表格解读（多模态）
> No figure is present in the input — the provided text is a **table caption** (Table 10), not a figure caption. There are no architectural components, schematic elements, or data-flow arrows to describe, so the requested architecture/data-flow summary cannot be produced. I will instead transcribe the caption verbatim and offer a brief description of what the referenced table reports.

**Verbatim transcription of the caption:**

"Table 10 j Comparison of DeepSeek-R1 and other frontier models in fine-grained safety scenarios. **Unsafe** indicates the proportion of unsafe content in the model's responses (lower values indicate better model safety), while **Rej.** represents the rejection rate in the model's answers (lower values indicate a stronger tendency for the model to provide informative and safe answers to questions, rather than simply declining to respond). For DeepSeek-V3 and DeepSeek-R1, we report results under two configurations: with and without risk control"

(Note: the source text has the typo "Table 10jComparison" with a missing space; reproduced as-is.)

**Brief description of the table (≤120 words):** Table 10 benchmarks DeepSeek-R1 against other frontier LLMs across fine-grained safety scenarios, reporting two metrics: **Unsafe** (fraction of unsafe completions — lower is safer) and **Rej.** (rejection rate — lower means the model answers informatively rather than refusing). DeepSeek-V3 and DeepSeek-R1 are evaluated under two modes — *with* and *without* risk-control interventions — enabling an ablation of how much of their safety performance is attributable to the explicit risk-control layer versus the base model behavior. This dual reporting lets readers disentangle inherent safety alignment from explicit refusal/control mechanisms.

If you intended to attach a figure, please re-upload it and I'll produce the requested architecture/data-flow summary.

### Table 11 (p.54) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab11.png]]
> [!quote] caption
> j Comparison of DeepSeek-R1 and other frontier models in jailbreaking scenarios.

> [!tip] 表格解读（多模态）
> **Description (main "figure" — actually Table 11):**

The table compares seven model configurations across two performance metrics — **Unsafe Ratio** and **Rejected Ratio** — each measured under three conditions: *Origin* (no attack), *Jailbreak* (under attack), and *GAP* (delta). Models span closed-source (Claude-3.7, o1, GPT-4o) and open-source (Qwen2.5-72B, DeepSeek-V3, DeepSeek-R1). For DeepSeek models, a "+ risk control system" row shows the effect of adding external safety filtering. Data flow: original baseline → jailbreak stress test → comparison via GAP column.

**Key takeaway:** DeepSeek-R1 shows the largest unsafe-response gap (+60.7%) yet paradoxically the lowest rejection ratio under attack (1.9%); only when paired with a risk-control system does its rejection rate jump to 87.3%, revealing that reasoning models offload safety entirely onto post-hoc filters.

**Caption verbatim:**

Table 11 | Comparison of DeepSeek-R1 and other frontier models in jailbreaking scenarios.

### Table 12 (p.56) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab12.png]]
> [!quote] caption
> j A Comparative Analysis of DeepSeek-V3 and DeepSeek-R1. DeepSeek-V3 is a

> [!tip] 表格解读（多模态）
> **Note:** No architecture/data-flow figure is present in the supplied image — only a tabular benchmark comparison. I'll describe the table's structure instead.

## Table Description

**Layout / Components:** A four-column comparison matrix grouping 22 benchmarks into four domain blocks — *English* (10 rows: MMLU, MMLU-Redux, MMLU-Pro, DROP, IF-Eval, GPQA Diamond, SimpleQA, FRAMES, AlpacaEval2.0, ArenaHard), *Code* (5 rows: LiveCodeBench, Codeforces Percentile/Rating, SWE Verified, Aider-Polyglot), *Math* (3 rows: AIME 2024, MATH-500, CNMO 2024), and *Chinese* (3 rows: CLUEWSC, C-Eval, C-SimpleQA). Columns compare **V3-Base → V3 → R1-Zero → R1**, with bold entries flagged as statistically significant (t-test p > 0.01).

**Key takeaway:** Reasoning training (R1) dominates on math/code/logic benchmarks (e.g., MATH-500 97.3, Codeforces 96.3 percentile, LiveCodeBench 65.9) while V3 retains an edge on instruction-following (IF-Eval Strict 86.1 vs 83.3) and conversational alignment (AlpacaEval2.0 70.0 vs 24.7), revealing a deliberate capability trade-off between the two model families.

**≤120-word limit met.**

## Caption (Verbatim Transcription)

> "Table 12 |A Comparative Analysis of DeepSeek-V3 and DeepSeek-R1. DeepSeek-V3 is a non-reasoning model developed on top of DeepSeek-V3-Base, which also serves as the foundational base model for DeepSeek-R1. Numbers in bold denote the performance is statistically significant (ttest with >0.01)."

**Trailing context (also appearing in the source):**

> "benchmark. In contrast, DeepSeek-V3 shows a relative advantage in instruction-following capabilities, suggesting different optimization priorities between the two models."

### Table 13 (p.57) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab13.png]]
> [!quote] caption
> j Performance on latest math competitions. Participants with their USAMO index

> [!tip] 表格解读（多模态）
> **Description (≤120 words):**

Table 13 is a 3-tier benchmark comparison matrix organized by capability class: a **human baseline**, **non-reasoning LLMs** (GPT-4o 0513, DeepSeek V3), and **reasoning LLMs** (OpenAI o1-1217, DeepSeek R1). Each row reports scores on three progressive evaluations — AMC 12 2024 (multi-choice), AIME 2025 (proof-based integer answers), and a derived composite USAMO Index with a hard qualification cutoff of 251.5. The data flow reveals a clear capability gap: reasoning models cross the qualification threshold while non-reasoning models plateau near or below the human average (123.7).

**Key takeaway:** DeepSeek-R1's USAMO Index of 256.7 was earned on AIME 2025 (released post-training), evidencing genuine out-of-distribution generalization rather than memorization of the contest corpus.

**Caption (verbatim):**

Table 13 | Performance on latest math competitions. Participants with their USAMO index surpassing 251.5 are qualified for USAMO.

### Table 14 (p.60) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab14.png]]
> [!quote] caption
> j Experimental results for each stage of DeepSeek-R1 on problems with varying

> [!tip] 表格解读（多模态）
> **Description:** Table 14 is a 5×3 performance matrix (with headers) comparing five model variants — DeepSeek-R1 Zero → Dev1 → Dev2 → Dev3 → DeepSeek-R1 (columns) — across three difficulty strata of LiveCodeBench (rows: Easy/Medium/Hard). Cell values are accuracy scores, monotonically increasing left-to-right along the RL pipeline.

**Key takeaway:** Easy-tier accuracy saturates quickly (98.07 → 100.00), while genuine progress concentrates on hard problems (17.09 → 34.44, ~2× gain), indicating each training stage primarily targets complex reasoning rather than trivial cases.

**Caption (verbatim):**
"Table 14 |Experimental results for each stage of DeepSeek-R1 on problems with varying difficulty levels in the LiveCodeBench dataset."

### Table 15 (p.61) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab15.png]]
> [!quote] caption
> j Comparison of DeepSeek-R1 distilled models and other comparable models on

> [!tip] 表格解读（多模态）
> **Description:**

The image presents a comparison table (Table 15) benchmarking DeepSeek-R1 distilled models against other leading LLMs on reasoning tasks. The table has six columns: Model, AIME 2024 (split into pass@1 and cons@64), MATH (pass@1), GPQA Diamond (pass@1), LiveCode Bench (pass@1), and CodeForces (rating). Two rows of data are visible — GPT-4o-0513 (9.3, 13.4, 74.6, 49.9, 32.9, 759) and Claude-3.5-Sonnet-1022 (16.0, 26.7, 78.3, 65.0, 38.9, 717). **Key takeaway:** Claude-3.5-Sonnet-1022 dominates on academic and coding reasoning benchmarks (AIME, MATH, GPQA, LiveCode), while GPT-4o-0513 leads on competitive programming rating (CodeForces 759 vs 717), suggesting these models exhibit complementary strengths rather than uniform superiority across reasoning domains. Note: the Table 15 partial view only shows baseline comparators; DeepSeek-R1 distilled rows are not visible in the cropped image.

**Caption (verbatim):**

"Table 15 jComparison of DeepSeek-R1 distilled models and other comparable models on reasoning-related benchmarks. Numbers in bold denote the performance is statistically significant (ttest with >0.01)."

### Table 16 (p.61) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab16.png]]
> [!quote] caption
> j Comparison of distilled and RL Models on Reasoning-Related Benchmarks.

> [!tip] 表格解读（多模态）
> # Description of Main Figure

**Note:** The image shows a **table** (Table 16), not a figure with architecture/data flow. Adapting the description to its actual content:

The table presents **benchmark comparison results** across five reasoning-related evaluations: AIME 2024 (pass@1 and cons@64), MATH (pass@1), GPQA Diamond (pass@1), LiveCodeBench (pass@1), and CodeForces (rating). It compares two closed-source baselines (GPT-4o-0513, Claude-3.5-Sonnet-1022) against six distilled DeepSeek-R1 variants based on Qwen (1.5B/7B/14B/32B) and Llama (8B/70B) architectures.

**Key Technical Takeaway:** Distillation from DeepSeek-R1 enables a 1.5B model to surpass GPT-4o on math benchmarks, and performance scales monotonically with student size—the 70B Llama variant achieves top scores across most metrics (94.5 MATH, 65.2 GPQA, 1633 CodeForces), demonstrating that reasoning capability transfers effectively through output distillation.

## Caption (Verbatim)

**Table 16 j Comparison of distilled and RL Models on Reasoning-Related Benchmarks.**

### Table 17 (p.62) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab17.png]]
> [!quote] caption
> j Performance of different models on AIME 2024 and AIME 2025.

> [!tip] 表格解读（多模态）
> # Description

The image does not contain an architecture or data-flow figure — it shows **Table 17** (a benchmark comparison table) and accompanying prose paragraphs.

**Table structure (3 columns × 4 rows):**
- Columns: *Average Score | AIME 2024 | AIME 2025*
- Rows: GPT-4o-0513 (9.3% / —), Qwen2-Math-7B-Instruct (7.9% / 4.6%), and the highlighted **Qwen2-Math-7B-Zero (22.3% / 18.1%)**, separated from the others by a horizontal rule.

**Key takeaway:** Pure RL on Qwen2-Math-7B-Zero nearly triples (≈2.4×) AIME 2024 accuracy vs. its instruction-tuned sibling (22.3% vs. 7.9%) and ~4× boosts AIME 2025 (18.1% vs. 4.6%), exceeding GPT-4o-0513 — illustrating that large-scale RL, not supervised instruction tuning, drives the math-reasoning gains.

# Verbatim Caption

> Table 17 jPerformance of different models on AIME 2024 and AIME 2025.

### Table 18 (p.40) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab18.png]]
> [!quote] caption
> to Table 32 present examples of our evaluation formats on different benchmarks. We also detail the specific capabilities of large language models assessed by each benchmark in

> [!tip] 表格解读（多模态）
> There doesn't appear to be a figure in the provided image — it contains only two text sections from what looks like an academic paper: "Decontamination" and "Evaluation Prompts." No architecture diagram, component layout, or data-flow illustration is visible.

Here's a transcription of the visible text:

**Decontamination** To prevent benchmark contamination, we implemented comprehensive decontamination procedures for both pre-training and post-training data. DeepSeek-V3 base has a knowledge cutoff date of July 2024, predating evaluation benchmarks like CNMO 2024, and we filtered out any text segments (including web pages and GitHub files) that contained matching 10-gram sequences from evaluation questions or reference solutions. As one example of our decontamination efforts, in the mathematics domain alone, our decontamination process identified and removed approximately six million potential pre-training texts. For post-training, mathematical SFT data and RL training prompts were sourced exclusively from pre-2023 competitions and underwent the same n-gram filtering protocol used in pre-training, ensuring no overlap between training and evaluation data. These measures ensure our model evaluation results reflect genuine problem-solving capabilities rather than memorization of test data.

However, we acknowledge that the n-gram based decontamination method cannot prevent the paraphrase of testset. Therefore, it is possible that benchmarks released before 2024 may suffer from contamination issues.

**Evaluation Prompts** Following the setup in DeepSeek-V3, standard benchmarks such as MMLU, DROP, GPQA Diamond, and SimpleQA are evaluated using prompts from the simple-evals framework. For MMLU-Redux, we adopt the Zero-Eval prompt format (Lin, 2024) in a zero-shot setting. In terms of MMLU-Pro, C-Eval and CLUE-WSC, since the original prompts are few-shot, we slightly modify the prompt to the zero-shot setting. The CoT in few-shot may hurt the performance of DeepSeek-R1. Other datasets follow their original evaluation protocols with default prompts provided by their creators. For code and math benchmarks, the HumanEval-Mul dataset covers eight mainstream programming languages (Python, Java, C++, C#, JavaScript, TypeScript, PHP, and Bash). Model performance on LiveCodeBench is evaluated using CoT format, with data collected between August 2024 and January 2025. The Codeforces dataset is evaluated using problems from 10 Div.2 contests, along with expert-crafted test cases, after which the expected ratings and percentages of competitors are calculated. SWE-Bench verified results are obtained via the agentless framework (Xia et al., 2024). AIDER-related benchmarks are measured using a "diff" format. DeepSeek-R1 outputs are capped at a maximum of 32,768 tokens for each benchmark.

Table 18 to Table 32 present examples of our evaluation formats on different benchmarks. We also detail the specific capabilities of large language models assessed by each benchmark in

If you intended to share a specific figure (e.g., a model architecture diagram), please re-upload it and I'll describe it accordingly.

### Table 19 (p.67) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab19.png]]
> [!quote] caption
> j MMLU-Redux is a subset of 5,700 manually re-annotated questions across all 57 MMLU subjects. MMLU-Redux focuses on improving the quality, clarity, and robustness of the benchmark by reducing noise, ambiguities, and potential biases in the MMLU, while potentially

> [!tip] 表格解读（多模态）
> It appears there's a mismatch in your request: **no figure image has been provided** — only a text excerpt beginning with "Table 19 jMMLU-Redux..." (which is a *table* caption, not a figure caption, and is itself cut off mid-sentence at "Here is").

Because there is no figure showing architecture, components, or data flow in the shared content, I cannot describe or infer one. Describing a hypothetical figure would require fabricating details, which I'm not willing to do.

**Verbatim transcription of what was provided:**

> Table 19 jMMLU-Redux is a subset of 5,700 manually re-annotated questions across all 57 MMLU subjects. MMLU-Redux focuses on improving the quality, clarity, and robustness of the benchmark by reducing noise, ambiguities, and potential biases in the MMLU, while potentially adjusting the scope or difficulty of tasks to better align with modern evaluation needs. Here is

(Transcription ends mid-sentence as supplied.)

If you can re-share the intended figure (as an image or its actual caption), I'll happily provide the architecture/components/data-flow description plus a key technical takeaway within 120 words, and transcribe the caption verbatim.

### Table 20 (p.68) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab20.png]]
> [!quote] caption
> j LiveCodeBench aims to evaluate model performance on the algorithm competition task, which collects new problems over time from contests across three competition platforms,

> [!tip] 表格解读（多模态）
> **Note:** The provided content does not contain a figure with architecture, components, or data flow. It consists of a table caption and a sample programming problem prompt. I'll describe what is present and provide the verbatim caption.

## Description

**What's shown:** The image is not a figure but rather a **text excerpt** containing Table 20's caption followed by a **competitive programming problem prompt**. The problem describes a card-stack manipulation task where K cards are moved from the bottom to the top of an N-card stack. It includes:

- **Problem statement** — defines the operation (rotating the stack by K positions).
- **Input/Output specification** — N, K on first line; N integers on second; output reordered stack.
- **Constraints** — 1 ≤ {N, K} ≤ 100.
- **Sample I/O pairs** — two examples demonstrating the expected behavior.
- **Inline explanation** of Sample 1 (cards 1,2,3,4,5 → 3,4,5,1,2 after K=3 rotation).

**Data/control flow implicit in the prompt:** Read N, K → read array → rotate array right by K → print.

**Key technical takeaway:** This is an *evaluation prompt template* for jLiveCodeBench — it illustrates the kind of canonical, well-specified contest problems the benchmark draws from LeetCode, AtCoder, and CodeForces. The real "figure" missing here would be jLiveCodeBench's architecture (problem scrapers → difficulty/classifier → evaluator harness → model), which is not depicted in this excerpt.

## Verbatim Caption

> **Table 20** jLiveCodeBench aims to evaluate model performance on the algorithm competition task, which collects new problems over time from contests across three competition platforms, namely LeetCode, AtCoder, and CodeForces.

### Table 22 (p.70) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab22.png]]
> [!quote] caption
> j DROP assesses a model’s ability to understand and extract relevant information from

> [!tip] 表格解读（多模态）
> # Description

This is **Table 22**, presenting a few-shot prompting template for the **DROP benchmark** (Discrete Reasoning Over Paragraphs). The table contains four logical sections: (1) an intro line framing DROP as context-rich reading comprehension; (2) a **PROMPT** block with system instructions and three worked passage–question–answer demonstrations across NFL game recaps; (3) an unseen **Your Task** passage requiring the model to derive a numerical fact ("How many yards did Rivers pass?"); and (4) an **Evaluation** line specifying string-parsing against `Answer: X`.

**Data flow:** passage + question + few-shot demos → LLM → step-by-step reasoning → terminal line `Answer: $ANSWER` → exact-match against gold truth.

**Key takeaway (≤120 words):** DROP shifts evaluation away from span extraction toward *discrete reasoning* over long passages — counting, comparison, and arithmetic over extracted facts. The few-shot prompt must (a) demonstrate the "think step by step, then Answer:" format and (b) terminate the model output on a parseable literal so an automated checker can score `Answer: 231` against ground truth — coupling prompt design directly to the regex-based scoring protocol.

# Caption (verbatim)

Table 22 j DROP assesses a model’s ability to understand and extract relevant information from extended textual passages. Unlike simpler question-answering benchmarks that focus on factual recall, DROP requires models to process and interpret context-rich paragraphs.

### Table 23 (p.71) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab23.png]]
> [!quote] caption
> j Instruction-Following Evaluation (IFEval) is a benchmark designed to assess a model’s ability to comply with explicit, verifiable instructions embedded within prompts. It

> [!tip] 表格解读（多模态）
> There is no figure present in the provided content — only **Table 23**, which is a textual example illustrating the Instruction-Following Evaluation (IFEval) benchmark. A brief description follows:

**Description (≤120 words):**
Table 23 presents a concrete example instance of the IFEval benchmark in three textual blocks rather than a graphical figure. (1) **Header block** defines the benchmark's purpose: assessing whether LLMs can satisfy explicit, verifiable, user-imposed constraints. (2) **PROMPT block** contains a compound instruction with two embedded constraints (output format = XML, length < 4 sentences) followed by a multi-paragraph source passage on quantum entanglement from which the model must produce output. (3) **Evaluation block** specifies the grading procedure — invoking official scorer functions to programmatically verify constraint compliance. The "data flow" is therefore linear: instruction + source text → LLM generation → constraint-checking scorer. **Key takeaway:** IFEval evaluates constraint adherence, not answer correctness — useful behavior is judged by automated rule checks against formatting/length/keyword requirements rather than semantic accuracy.

**Caption (transcribed verbatim):**
"Table 23 𝓙Instruction-Following Evaluation (IFEval) is a benchmark designed to assess a model's ability to comply with explicit, verifiable instructions embedded within prompts. It targets a core competency of large language models (LLMs): producing outputs that meet multiple, clearly defined constraints specified by the user."

### Table 24 (p.72) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab24.png]]
> [!quote] caption
> j FRAMES (Factuality, Retrieval, And reasoning MEasurement Set) is a comprehensive

> [!tip] 表格解读（多模态）
> ## Description of the Main Figure

**Architecture/Components:** The figure presents the **jFRAMES benchmark evaluation pipeline** for RAG systems. Core components shown include: (1) the **input layer** — a test prompt composed of a question paired with all ground-truth Wikipedia articles (no external retriever needed); (2) the **RAG/Oracle model** under evaluation; and (3) the **assessment layer** that jointly measures three capabilities: *Factuality*, *Retrieval relevance*, and *Reasoning correctness*. The "Oracle Prompt" mode bypasses BM25-style retrieval by directly feeding gold articles, isolating the model's end-to-end reasoning and grounding ability.

**Data Flow:** Question + Gold Wikipedia articles → Concatenated Oracle Prompt → LLM → Generated Answer → Evaluator scoring Factuality / Retrieval / Reasoning.

**Key Technical Takeaway (≤120 words):** jFRAMES decouples retrieval quality from generation quality via its Oracle Prompt setting — by injecting ground-truth Wikipedia passages directly into the prompt, it isolates reasoning and factual grounding as the sole variables. This reveals how well an LLM truly *uses* retrieved evidence rather than how well the retriever *finds* it. Consequently, any reported gains reflect pure answer-generation capability, not retriever improvements. The takeaway: strong retriever performance ≠ strong answer accuracy; models that pass Oracle evaluation but falter under real retrieval expose genuine grounding brittleness, which real-world RAG systems must address.

## Verbatim Caption Transcription

> Table 24 j FRAMES (Factuality, Retrieval, And reasoning MEasurement Set) is a comprehensive benchmark designed to evaluate core components of retrieval-augmented generation (RAG) systems. Our evaluation employs the benchmark's official "Oracle Prompt" configuration. In this setting, each test prompt includes the question along with all the ground truth Wikipedia articles, thus eliminating the need for an external retrieval component (e.g., BM25). This setting

### Table 25 (p.73) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab25.png]]
> [!quote] caption
> j Arena-Hard is an open-ended evaluation benchmark specifically designed to assess

> [!tip] 表格解读（多模态）
> **Note:** The content you provided is a **caption for Table 25** (not a figure). There is no figure, diagram, or schematic with architecture/components/data flow to describe — only a table caption describing the jArena-Hard benchmark.

**Verbatim transcription of the caption:**

Table 25 jArena-Hard is an open-ended evaluation benchmark specifically designed to assess the capabilities of LLMs. It presents models with challenging, novel, and diverse prompts curated from Chatbot Arena, a continuously evolving, crowd-sourced platform. It focuses on measuring model performance in open-ended tasks, with particular emphasis on coding and mathematics-related prompts. Given the inherently subjective nature of open-ended tasks, where multiple valid responses may exist, the benchmark necessitates the use of an evaluation model to approximate human judgment effectively. Higher evaluation scores suggest that the

*(Caption appears truncated at the end.)*

### Table 27 (p.75) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab27.png]]
> [!quote] caption
> j The CLUEWSC (Chinese Language Understanding Evaluation Benchmark - Winograd Schema Challenge) is a specialized task within the CLUE benchmark suite designed to evaluate

> [!tip] 表格解读（多模态）
> **Description (≤120 words):**

The figure presents **Table 27: CLUEWSC (Chinese Language Understanding Evaluation Benchmark – Winograd Schema Challenge)**, part of the broader CLUE benchmark suite. The table is structured into two labeled sections:

- **PROMPT** — A prompt template that appears heavily garbled (likely due to a Chinese-character encoding/font rendering issue in the source PDF), with only placeholders and structural markers like `b/`, `b P- "y " /`, and `b P- "" /` remaining legible alongside an `< K ... l` opening token.
- **Evaluation** — A short instruction: *"Parse the last line in response to judge if the answer equals to ground truth."*

**Key technical takeaway:** CLUEWSC tests commonsense/coreference resolution in Chinese, and the benchmark relies on a deterministic post-processing rule — comparing the final line of the model's output against a reference answer — rather than token-level scoring, making parsing robustness critical.

---

**Verbatim caption transcription:**

> Table 27 ¡ The CLUEWSC (Chinese Language Understanding Evaluation Benchmark - Winograd Schema Challenge) is a specialized task within the CLUE benchmark suite designed to evaluate a model's commonsense reasoning and contextual understanding capabilities in Chinese.

### Table 28 (p.76) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab28.png]]
> [!quote] caption
> j C-EVAL evaluates a model’s breadth and depth of knowledge across 52 diverse

> [!tip] 表格解读（多模态）
> ## Description

**What is actually shown:** This is a sample table ("Table 28") from the **C-EVAL** benchmark, not an architecture diagram. It illustrates the **prompt format** used to query a model: one Chinese-language example question in a cloze/completion style (with a `_____` blank, year stamp "1991/2000", and probability choices marked `2π`, `3π`, `4π`, `5π`), followed by a second multiple-choice question (options A–D) about a data structure built from the first. The structure demonstrates: **(1) input prompt with stem + masked token, (2) candidate option enumeration (A–D), (3) optional chain-of-thought or follow-up question referencing prior context**.

**Key takeaway:** C-EVAL probes Chinese-language academic reasoning through a two-stage prompt — masked-token prediction followed by a structure-derived follow-up — testing whether models can span STEM, humanities, social sciences, and professional domains in one evaluation.

## Verbatim caption

> Table 28 jC-EVAL evaluates a model's breadth and depth of knowledge across 52 diverse academic disciplines, spanning humanities, social sciences, STEM (Science, Technology, Engineering, and Mathematics), and other professional fields (e.g., medicine, law). All question in C-Eval are Chinese.

### Table 29 (p.76) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab29.png]]
> [!quote] caption
> j GPQA (Graduate-Level Google-Proof QA Benchmark) is a rigorous evaluation

> [!tip] 表格解读（多模态）
> **Description of Table 29 (main figure):**

The table illustrates the **jGPQA evaluation framework** composed of two main components:

1. **PROMPT** — A structured instruction template instructing the LLM to "think step by step" and emit a final response in the format `ANSWER: $LETTER`, followed by a sample graduate-level physics question about resolving two quantum energy levels (E1, E2) with lifetimes 10⁹ s and 10⁸ s.

2. **Evaluation** — A lightweight regex-based parser that extracts the capital letter following `"ANSWER: "` and compares it against the ground-truth label.

**Data flow:** Question → LLM (chain-of-thought reasoning) → Parsed letter → Binary correctness score vs. ground truth.

**Key technical takeaway:** Coercing the model to produce a deterministic, structured terminal token (`ANSWER: X`) enables cheap, reliable automated grading without needing an LLM-as-judge, which is critical for scalable benchmark evaluation.

**Caption verbatim:**

"Table 29 jGPQA (Graduate-Level Google-Proof QA Benchmark) is a rigorous evaluation framework designed to measure an LLM's ability to tackle complex, graduate-level multiple-choice problems in STEM domains—specifically biology, physics, and chemistry."

### Table 30 (p.77) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab30.png]]
> [!quote] caption
> j SimpleQA is a factuality evaluation benchmark that measures a model’s ability to

> [!tip] 表格解读（多模态）
> **Description (≤120 words):**

This is a structured evaluation prompt template (Table 30), not an architecture diagram. Its components and data flow are:

1. **Header** – declares JSimpleQA's purpose (factuality evaluation via short, verifiable QA).
2. **Prompt block** – a question paired with an LLM-as-judge rubric containing three few-shot examples labeled CORRECT, INCORRECT, and NOT_ATTEMPTED, each demonstrating grading criteria (full match vs. partial/extra info vs. abstention).
3. **New-example block** – presents a fresh question (IEEE Frank Rosenblatt Award 2010), gold target (Michio Sugeno), and a model-predicted answer (Jürgen Schmidhuber), then requests a single-letter grade (A/B/C).

**Key takeaway:** The template enforces structured, few-shot categorical judging to reduce grader bias, isolating hallucinated entities like Schmidhuber from true facts (Sugeno), which would be flagged as INCORRECT.

**Caption (verbatim):**

"Table 30 JSimpleQA is a factuality evaluation benchmark that measures a model's ability to answer short, fact-seeking questions with precise, verifiable correctness."

### Table 31 (p.78) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab31.png]]
> [!quote] caption
> j An example of C-SimpleQA. It measures a model’s ability to answer short,

> [!tip] 表格解读（多模态）
> **Description:**

Table 31 illustrates a sample from **C-SimpleQA**, a benchmark for short, fact-seeking Chinese questions requiring verifiable answers. The layout has two main components:

1. **PROMPT** – Few-shot examples (garbled in the OCR) conditioning the model on the QA format.
2. **Evaluation** – Multiple test items, each formatted as a question (`T`) with reference answers (`K1`, `K2`). Example topics include "Malia Obama and Sasha Obama" alongside Chinese Q&A pairs (e.g., about a leading stadium with 60,000+ seats, a national anthem).

The bottom block defines the **judge prompt**: the evaluator model is shown the original Chinese question (`cnTH`), the model's predicted answer (`KTH`), and reference answers, then must classify the response into categories **A (correct), B (partially correct), C (refused), D (incorrect)**, with reasoning and a final answer letter. Essentially a constrained few-shot prompting → answer generation → LLM-as-judge verification pipeline.

**Key technical takeaway:** Reliability hinges on a strict categorical rubric (A/B/C/D) for grading short Chinese factual answers, mitigating evaluator ambiguity in fact-seeking tasks.

**Verbatim caption:**

> Table 31 j An example of C-SimpleQA. It measures a model's ability to answer short, fact-seeking questions in Chinese with precise, verifiable correctness.

### Table 32 (p.78) ⭐深度解读
![[assets/crops/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-tab32.png]]
> [!quote] caption
> j An example of math evaluation, which applies to AIME, MATH, and CNMO. These

> [!tip] 表格解读（多模态）
> **Main figure description (≤120 words):**

Table 32 illustrates a math-evaluation pipeline used across the AIME, MATH, and CNMO benchmarks. The **PROMPT** component delivers a number-theory problem (finding the least integer base where more than ten "beautiful" integers exist) and instructs the model to reason step-by-step before producing a final answer enclosed in `\boxed{}`. The **Evaluation** component then parses that boxed output, normalizes numerical values, and applies a deterministic, rule-based grader (leveraging `SymPy` for symbolic expression parsing) to compare the prediction against the ground truth. Data flow: prompt → model generation → boxed-answer extraction → SymPy parsing → rule-based scoring.

**Key technical takeaway:** Evaluation relies on a deterministic, rule-based grader with SymPy-based symbolic parsing rather than LLM-as-judge, ensuring reproducible and objective scoring of mathematical outputs.

**Caption (verbatim):**

Table 32 | An example of math evaluation, which applies to AIME, MATH, and CNMO. These benchmarks evaluate model performance on mathematical tasks.

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