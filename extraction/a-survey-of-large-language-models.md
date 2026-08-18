---
paper_num: "61"
title: "A Survey of Large Language Models"
authors: "A Survey of Large Language Models Wayne Xin Zhao, Kun Zhou*, Junyi Li*, Tianyi Tang, Xiaolei Wang, Yupeng Hou, Yingqian Min, Beichen Zhang, Junjie Zhang, Zican Dong, Yifan Du, Chen Yang, Yushuo Chen, Zhipeng Chen, Jinhao"
date: "2023/3/31"
arxiv: "https://arxiv.org/abs/2303.18223"
pdf: "papers/a-survey-of-large-language-models.pdf"
slug: "a-survey-of-large-language-models"
tags: []
---

# A Survey of Large Language Models

> [!abstract] 摘要（原文）
> Language is essentially a complex, intricate system of human expressions governed by grammatical rules. It poses a significant challenge to develop capable AI algorithms for comprehending and grasping a language. As a major approach, language modeling has been widely studied for language understanding and generation in the past two decades, evolving from statistical language models to neural language models. Recently, pre-trained language models (PLMs) have been proposed by pre-training Transformer models over large-scale corpora, showing strong capabilities in solving various NLP tasks. Since researchers have found that model scaling can lead to performance improvement, they further study the scaling effect by increasing the model size to an even larger size. Interestingly, when the parameter scale exceeds a certain level, these enlarged language models not only achieve a significant performance improvement but also show some special abilities that are not present in small-scale language models. To discriminate the difference in parameter scale, the research community has coined the term large language models (LLM) for the PLMs of significant size. Recently, the research on LLMs has been largely advanced by both academia and industry, and a remarkable progress is the launch of ChatGPT, which has attracted widespread attention from society. The technical evolution of LLMs has been making an important impact on the entire AI community, which would revolutionize the way how we develop and use AI algorithms. In this survey, we review the recent advances of LLMs by introducing the background, key findings, and mainstream techniques. In particular, we focus on four major aspects of LLMs, namely pre-training, adaptation tuning, utilization, and capacity evaluation. Besides, we also summarize the available resources for developing LLMs and discuss the remaining issues for future directions.

## 元信息
- **发表日期**: 2023/3/31
- **作者**: A Survey of Large Language Models Wayne Xin Zhao, Kun Zhou*, Junyi Li*, Tianyi Tang, Xiaolei Wang, Yupeng Hou, Yingqian Min, Beichen Zhang, Junjie Zhang, Zican Dong, Yifan Du, Chen Yang, Yushuo Chen, Zhipeng Chen, Jinhao
- **arXiv**: https://arxiv.org/abs/2303.18223
- **本地 PDF**: `papers/a-survey-of-large-language-models.pdf`
- **页数**: 144

## 图表（原文 caption + 页码）

### Figure 1 (p.3) ⭐深度解读
![[assets/a-survey-of-large-language-models-p03.png]]
> [!quote] caption
> As discussed before, language model is not a new tech- nical concept specially for LLMs, but has evolved with the advance of artificial intelligence over the decades. Early lan- guage models mainly aim to model and generate text data, while latest language models (e.g., GPT-4) focus on complex task solving. From language modeling to task solving, it is an important leap in scientific thinking, whi

> [!tip] 技术解读（多模态）
> No figure is visible on this page. Page 3 contains only two columns of body text from the survey (introducing LLMs vs. PLMs, referencing Figure 1 and Figure 2 elsewhere), along with three footnotes. The actual figures (Figure 1 — arXiv submission trends; Figure 2 — four-generation evolution of language models) are not rendered in the image you provided, so I cannot describe their architecture/components/data flow or transcribe a caption verbatim.

If you can share the page containing the figure, I can provide the requested description.

### Figure 3 (p.99) ⭐深度解读
![[assets/a-survey-of-large-language-models-p99.png]]
> [!quote] caption
> – Section 4: add LLM-based data filtering and selec- tion methods in Section 4.1.2; update Section 4.2.1, “Emergent Architectures” to include more discus- sions about SSM-based architectures; add Table 6 to compare parallelism and complexity of different architectures. – Section 5: add latest discussion about instruction quality improvement and instruction selection in

> [!tip] 技术解读（多模态）
> I'm unable to complete this request as described. The image you've provided (page 99 of what appears to be a survey paper on Large Language Models) contains **only text content** — specifically:

- A chronological list of updates to various sections of the paper
- An **Acknowledgments** section
- Lists of contributions (experiments and tips)
- The very beginning of a **References** section (starting with reference [1], Bengio et al.)

There is **no figure, diagram, or illustration** present on this page, and consequently no caption to transcribe. The text does mention "Figure 3" being updated with new LLMs, but the figure itself is not shown on this page.

If you'd like, I could instead:
1. Summarize the main textual content of this page (e.g., the update history, acknowledgments, or contributor lists)
2. Describe a different page that actually contains a figure from this paper

Please let me know how you'd like to proceed, or share the page containing the figure you'd like described.

### Figure 4 (p.7) ⭐深度解读
![[assets/a-survey-of-large-language-models-p07.png]]
> [!quote] caption
> The basic principle underlying GPT models is to compress the world knowledge into the decoder-only

> [!tip] 技术解读（多模态）
> I cannot complete this request accurately because **no figure is visible on this page**. 

The provided image shows page 7 of a survey paper on LLMs, which contains only text content:
- Discussion of RLHF (reinforcement learning with human feedback) and InstructGPT
- "Tools manipulation" subsection
- Section 2.2 "Technical Evolution of GPT-series Models"
- Subsections on "Early Explorations," "GPT-1," "GPT-2," and "Capacity Leap"

The text *references* "Figure 4" (described as a schematic diagram depicting the technological evolution of GPT-series models), but **Figure 4 itself is not included in the image you provided**. There is also no visible caption on this page to transcribe verbatim.

To complete your request, I would need an image containing the actual figure and its caption. If you can share the page containing Figure 4, I can then describe its architecture/components/data flow, provide a technical takeaway, and transcribe the caption.

### Figure 5 (p.12) ⭐深度解读
![[assets/a-survey-of-large-language-models-p12.png]]
> [!quote] caption
> Public API of LLMs. Instead of directly using the model copies, APIs provide a more convenient way for common users to use LLMs, without the need of running the model locally. As a representative interface for using LLMs, the APIs for the GPT-series models [46, 55, 66, 105] have been widely used for both academia and industry19.

> [!tip] 技术解读（多模态）
> ## Figure Description

**Architecture/Components:** A radial evolutionary tree rooted at **LLaMA** (top-center, with llama icon) branching into dozens of derivative models via three edge types defined in the legend: **red dashed** = continue pre-training, **green solid** = model inheritance, **blue solid** = data inheritance. Boxes are color-coded as parameter-efficient (yellow) vs. full-parameter (green) fine-tuning. Major subtrees include **Chinese-LLaMA** (Chinese Vicuna, Panda, Open-Chinese-LLaMA), **Alpaca** (BELLE, BiLLa, Ziya, Koala, Baize, Chinese Alpaca), **Vicuna** → Yulan-Chat, and a dashed-bordered **Multimodal** cluster (LLaVA, MiniGPT-4, OpenFlamingo, PandaGPT, VisionLLM, InstructBLIP). Domain icons denote Math/Finance/Medicine/Law/Bilingualism/Education.

**Key takeaway:** LLaMA's dominance stems from a reusable adaptation recipe—small extension (continue pre-training) + model or data inheritance—enabling cheap domain/multilingual/multimodal specialization without retraining from scratch.

## Caption (verbatim)

Fig. 5: An evolutionary graph of the research work conducted on LLaMA. Due to the huge number, we cannot include all the LLaMA variants in this figure, even much excellent work. To support incremental update, we share the source file of this figure, and welcome the readers to include the desired models by submitting the pull requests on our GitHub page.

### Figure 7 (p.18) ⭐深度解读
![[assets/a-survey-of-large-language-models-p18.png]]
> [!quote] caption
> Filtering and Selection. To remove low-quality data from the collected corpus, existing work generally adopts two ap- proaches, namely classifier-based and heuristic-based. The former approach trains a selection classifier based on high- quality texts and leverages it to identify and filter out low- quality data. Typically, these methods train a binary classi- fier using positive instances that ar

> [!tip] 技术解读（多模态）
> # Response

**No figure is visible on the provided page.** The page contains only body text discussing data sources (scientific text, code) and data preprocessing techniques (filtering and selection, de-duplication, privacy reduction) for LLM pre-training. The text *references* "Figure 7" as illustrating "A typical pipeline of preprocessing the pre-training data for LLMs," but the figure itself does not appear on this page — it would likely be on a separate page in the original document.

**Caption (transcribed verbatim from in-text reference):**
> "A typical pipeline of preprocessing the pre-training data for LLMs has been illustrated in Figure 7."

If you can provide the page containing the actual figure, I'd be happy to describe its architecture, components, data flow, and identify a key technical takeaway for you.

### Figure 8 (p.20) ⭐深度解读
![[assets/a-survey-of-large-language-models-p20.png]]
> [!quote] caption
> Data Mixture. Since each kind of data source is closely related to the development of certain capacities for LLMs (referring to the discussions in Section 4.1), it is important to set a suitable distribution to mix these data. The data mixture is generally set in a global level (i.e., the distribution of the entire pre-training data), and can be also locally set to varied proportions at different 

> [!tip] 技术解读（多模态）
> ## Figure 8 Description

**Architecture/Components:**
- **Legend/Data Sources:** Four data sources labeled 1–4, color-coded (yellow, blue, light blue, pink).
- **Bar Charts:** Four bar groups across the horizontal axis representing **Stage 1 → Stage 2 → … → Stage n−1 → Stage n**.
- **Data Mixture:** Arrow pointing to the bars, indicating the *proportion* of each source within a single stage.
- **Data Curriculum:** Brace spanning all stages, indicating the *ordering/scheduling* of sources across stages.

**Data Flow:** Pre-training proceeds left-to-right through discrete stages. At each stage, sources are mixed in varying ratios (shown by bar heights), and across stages the emphasis shifts — e.g., Source 1 (yellow) dominates early, while Sources 3/4 grow in later stages.

**Key Technical Takeaway (≤120 words):**
Effective LLM pre-training requires orchestrating two coupled dimensions: a **data mixture** (which sources to sample from at a given stage) and a **data curriculum** (when each source is emphasized). Higher-weighted sources are sampled more frequently. Empirical evidence (e.g., LLaMA) shows heterogeneous mixtures — ~80% webpages, 6.5% GitHub/StackExchange code, 4.5% books, 2.5% arXiv science — outperform homogeneous ones. Strategies include increasing source diversity, optimizing mixtures via small proxy models (DoReMi), and upweighting sources tied to targeted capabilities (math/coding). Dropping heterogeneous sources like webpages degrades performance more than dropping low-heterogeneity sources like academic corpora.

## Caption (Verbatim Transcription)

**Fig. 8:** An illustration of data scheduling for pre-training LLMs.

### Figure 9 (p.22) ⭐深度解读
![[assets/a-survey-of-large-language-models-p22.png]]
> [!quote] caption
> Encoder-decoder Architecture. The vanilla Transformer model is built on the encoder-decoder architecture [22], which consists of two stacks of Transformer blocks as the encoder and decoder, respectively. The encoder adopts stacked multi-head self-attention layers to encode the input sequence for generating its latent representations, while the decoder performs cross-attention on these representa- 

> [!tip] 技术解读（多模态）
> I'm unable to complete this request as described because **there is no figure visible on this page**. 

The page (numbered 22) contains only text content from what appears to be a survey paper on Large Language Models (likely "A Survey of Large Language Models" by Zhao et al.). The text explicitly references "Figure 9" in the context of categorizing LLM architectures into three types (encoder-decoder, causal decoder, and prefix decoder), but the actual figure is not displayed on this page.

**What the page contains instead:**

**Section 4.2.1 – Typical Architectures**, which discusses:
- **Encoder-decoder Architecture** – e.g., T5, BART, Flan-T5
- **Causal Decoder Architecture** – e.g., GPT-series, OPT, BLOOM, Gopher (unidirectional attention mask)
- **Prefix Decoder Architecture** – non-causal decoder with bidirectional prefix + unidirectional generation (e.g., GLM-130B, U-PaLM)
- **Mixture-of-Experts (MoE)** – sparse activation for parameter scaling (e.g., Switch Transformer, GLaM)
- **Emergent Architectures** – State Space Models (SSMs) like Mamba, RWKV, RetNet, Hyena, designed to overcome Transformer's quadratic complexity

**Key technical takeaway from the text:** The three mainstream LLM architectures differ primarily in their **attention masking strategies** — causal decoders use strict unidirectional masks, prefix decoders allow bidirectional attention over the input prefix only, and encoder-decoders process input/output through separate stacks with cross-attention. These masking choices have cascading effects on pre-training efficiency, in-context learning ability, and downstream task performance.

If you intended to share an image of the actual figure, it didn't come through in your message.

### Figure 13 (p.43) ⭐深度解读
![[assets/a-survey-of-large-language-models-p43.png]]
> [!quote] caption
> Adapter Tuning. Adapter tuning incorporates small neural network modules (called adapter) into the Transformer mod- els [406]. To implement the adapter module, a bottleneck architecture has been proposed in [406, 407], which first compresses the original feature vector into a smaller di- mension (followed by a nonlinear transformation) and then recovers it to the original dimension. The adapter mo

> [!tip] 技术解读（多模态）
> **Note:** The provided page contains only the textual description of Figure 13 (referenced in §5.3.1). The actual figure illustration and its caption are not present in this page excerpt — only the body text describing the four methods. The following description is reconstructed from the textual explanation of Figure 13.

**Description of Figure 13 (as described in text):**
Figure 13 illustrates four parameter-efficient fine-tuning (PEFT) methods for Transformer language models, with the original model weights frozen (shown in gray) and only small trainable components updated (shown in color):

1. **Adapter Tuning** — Small bottleneck neural modules (down-project → nonlinearity → up-project) inserted *serially* after each Transformer sub-layer (attention & FFN), or placed *in parallel* alongside them.
2. **Prefix Tuning** — Trainable prefix vectors prepended to the keys/values at every Transformer layer (layer-wise).
3. **Prompt Tuning** — Trainable soft prompts attached only at the **input embedding layer** (input-level).
4. **LoRA (Low-Rank Adaptation)** — Low-rank decomposition ΔW = AB inserted alongside frozen weight matrices in each dense layer, with rank k ≪ min(m, n).

**Key technical takeaway:** All four methods freeze the pre-trained backbone and inject a tiny number of trainable parameters at different architectural granularities (sub-layer, layer-wise, input-only, or weight-level), trading a small accuracy gap for dramatically reduced storage — one backbone can serve many tasks via small task-specific modules.

**Verbatim caption transcription:** *Not visible on this page.* The page text states only: "The illustration of these four methods are shown in Figure 13." The actual figure caption (e.g., "Figure 13: Overview of four parameter-efficient fine-tuning methods…") would appear on the page containing the illustration, which is not included in the provided excerpt.

### Figure 16 (p.54) ⭐深度解读
![[assets/a-survey-of-large-language-models-p54.png]]
> [!quote] caption
> In this paradigm, there are typically three components: task planner, plan executor, and environment36. Specifically, task planner, which is played by LLMs, aims to generate the whole plan to solve a target task. The plan can be presented in various forms, e.g., an action sequence in the form of natural language [432] or an executable program written in programming language [436]. The LLM-based ta

> [!tip] 技术解读（多模态）
> ## Figure 16 Description

The figure depicts a **Planning Framework** for LLM-based task solving, organized into a closed loop with three primary components and auxiliary modules:

**Core Components:**
- **Task Planner (LLM)** — yellow box, the decision-making module
- **Plan Executor** — blue box, carries out the actions
- **Environment** — pink box, where actions are performed

**Supporting Modules:**
- **Memory** (yellow) — bidirectional dashed link to Task Planner, stores/retrieves plans for long-horizon tasks
- **Tool** (blue) — bidirectional dashed link to Plan Executor, enables code interpreters/APIs

**Data Flow:** A *Task* enters the Task Planner, which produces a *Plan* (labeled "generate & refine") sent to the Plan Executor. The Executor emits *Action* into the Environment and uses Tools, producing a *Result*; Environment returns *Feedback* to the Planner for iterative refinement.

**Sources** are categorized as **Internal** (LLM) or **External** (Human, World, Others).

**Key Takeaway:** Planning decouples reasoning from execution — the LLM-as-planner iteratively refines its plan using environment feedback rather than acting directly, enabling decomposition of complex multi-step tasks.

## Caption (verbatim)

> **Fig. 16:** An illustration of the formulation for prompt based planning by LLMs for solving complex tasks.

### Figure 17 (p.59) ⭐深度解读
![[assets/a-survey-of-large-language-models-p59.png]]
> [!quote] caption
> Hallucination widely occurs in existing LLMs, even the most superior LLMs such as GPT-4 [46]. Furthermore, existing work shows that LLMs encounter difficulties in recognizing the hallucinated con- tent in text [604], even the powerful ChatGPT. Additionally, beyond language tasks, a recent study has shown that large vision-language models (LVLM) also face challenges with hallucination, i.e., genera

> [!tip] 技术解读（多模态）
> ## Main Figure Description (Figure 17)

**Components / data flow:** The figure is a two-panel comparison of LLM hallucination types using a chatbot dialogue mockup (user avatar + robot avatar). **(a) Intrinsic hallucination**: Given the prompt "Bob's wife is Amy. Bob's daughter is Cindy. Who is Cindy to Amy?", the LLM replies "Cindy is Amy's daughter-in-law" (red, conflicting with the stated input facts). **(b) Extrinsic hallucination**: Prompted with "Explain RLHF for LLMs", the model defines RLHF as "Rights, Limitations, Harms, and Freedoms" (red), while correctly expanding LLMs as "Large Language Models" (black).

**Key takeaway:** Hallucinations split into intrinsic (factually contradicts the supplied prompt/context) and extrinsic (fabricates unverifiable world knowledge), and a single model can mix correct and wrong content in the same answer.

## Caption (verbatim)

Fig. 17: Examples of intrinsic and extrinsic hallucination for a public LLM (access date: March 19, 2023). As an example of intrinsic hallucination, the LLM gives a conflicting judgment about the relationship between Cindy and Amy, which contradicts the input. For extrinsic hallucination, in this example the LLM seems to have an incorrect understanding of the meaning of RLHF (reinforcement learning from human feedback), though it can correctly understand the meaning of LLMs (in this context).

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\text{LLM} \big(I, \underbrace{ f(x_1, y_1), \dots, f(x_k, y_k)}_{\text{demonstrations}}, f(\underbrace{x_{k+1}}_{\text{input}}, \underbrace{\vphantom{\hat{y}_{k+1}} \_\_\_}_{\text{answer}}) \big) \rightarrow \hat{y}_{k+1}.
$$

$$
L(N, D) = E + \frac{A}{N^\alpha} + \frac{B}{D^{\beta}},
$$

$$
\Theta = \{\theta_i = b^{-2(i-1)/d} | i \in \{1, 2, \dots , d/2 \}\}.
$$

$$
\lambda_i = 2\pi b^{2(i-1)/d}=2 \pi / \theta_i.
$$

$$
\mathcal{L}_{LM}(\mathbf{x})=\sum_{i=1}^n \log P(x_i|\mathbf{x}_{<i}).
$$

$$
\mathcal{L}_{DAE}(\mathbf{x})= \log P(\Tilde{\mathbf{x}}|\mathbf{x}_{\backslash \Tilde{\mathbf{x}}}).
$$

$$
{ x_i = \underset{x}{\arg\max} P(x |\mathbf{x}_{<i}),}
$$

$$
x_i \sim P(x|\mathbf{x}_{<i}).
$$

$$
P(x_j|\mathbf{x}_{<i}) = \frac{\exp{(l_j/t)}}{\sum_{j'} \exp{(l_{j'}/t)}},
$$

$$
L(N) &=& \bigg(\frac{N_c}{N}\bigg)^{\alpha_N}, \text{~~~} \alpha_N \sim 0.076, N_c \sim 8.8\times 10^{13} \\\nonumber L(D) &=& \bigg(\frac{D_c }{D}\bigg)^{\alpha_D}, \text{~~~} \alpha_D \sim 0.095, D_c \sim 5.4\times 10^{13} \\\nonumber L(C) &=& \bigg(\frac{C_c}{C}\bigg)^{\alpha_C}, \text{~~~} \alpha_C \sim 0.050, C_c \sim 3.1\times 10^{8}\nonumber
$$

$$
N_{opt}(C)=G \bigg(\frac{C}{6}\bigg)^a, \text{~~~} D_{opt}(C)=G^{-1} \bigg(\frac{C}{6}\bigg)^b,
$$

## 技术点深读（DEEP）

![[deep/a-survey-of-large-language-models]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/a-survey-of-large-language-models.txt`（860409 字符）供引用检索。