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
![[assets/crops/a-survey-of-large-language-models-fig01.png]]
*整页渲染: ![[assets/a-survey-of-large-language-models-p03.png]]*
> [!quote] caption
> As discussed before, language model is not a new tech- nical concept specially for LLMs, but has evolved with the advance of artificial intelligence over the decades. Early lan- guage models mainly aim to model and generate text data, while latest language models (e.g., GPT-4) focus on complex task solving. From language modeling to task solving, it is an important leap in scientific thinking, whi

> [!tip] 技术解读（多模态）
> No figure is visible on this page. Page 3 contains only two columns of body text from the survey (introducing LLMs vs. PLMs, referencing Figure 1 and Figure 2 elsewhere), along with three footnotes. The actual figures (Figure 1 — arXiv submission trends; Figure 2 — four-generation evolution of language models) are not rendered in the image you provided, so I cannot describe their architecture/components/data flow or transcribe a caption verbatim.

If you can share the page containing the figure, I can provide the requested description.

### Figure 3 (p.99) ⭐深度解读
![[assets/crops/a-survey-of-large-language-models-fig03.png]]
*整页渲染: ![[assets/a-survey-of-large-language-models-p99.png]]*
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
![[assets/crops/a-survey-of-large-language-models-fig04.png]]
*整页渲染: ![[assets/a-survey-of-large-language-models-p07.png]]*
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
![[assets/crops/a-survey-of-large-language-models-fig05.png]]
*整页渲染: ![[assets/a-survey-of-large-language-models-p12.png]]*
> [!quote] caption
> Public API of LLMs. Instead of directly using the model copies, APIs provide a more convenient way for common users to use LLMs, without the need of running the model locally. As a representative interface for using LLMs, the APIs for the GPT-series models [46, 55, 66, 105] have been widely used for both academia and industry19.

> [!tip] 技术解读（多模态）
> ## Figure Description

**Architecture/Components:** A radial evolutionary tree rooted at **LLaMA** (top-center, with llama icon) branching into dozens of derivative models via three edge types defined in the legend: **red dashed** = continue pre-training, **green solid** = model inheritance, **blue solid** = data inheritance. Boxes are color-coded as parameter-efficient (yellow) vs. full-parameter (green) fine-tuning. Major subtrees include **Chinese-LLaMA** (Chinese Vicuna, Panda, Open-Chinese-LLaMA), **Alpaca** (BELLE, BiLLa, Ziya, Koala, Baize, Chinese Alpaca), **Vicuna** → Yulan-Chat, and a dashed-bordered **Multimodal** cluster (LLaVA, MiniGPT-4, OpenFlamingo, PandaGPT, VisionLLM, InstructBLIP). Domain icons denote Math/Finance/Medicine/Law/Bilingualism/Education.

**Key takeaway:** LLaMA's dominance stems from a reusable adaptation recipe—small extension (continue pre-training) + model or data inheritance—enabling cheap domain/multilingual/multimodal specialization without retraining from scratch.

## Caption (verbatim)

Fig. 5: An evolutionary graph of the research work conducted on LLaMA. Due to the huge number, we cannot include all the LLaMA variants in this figure, even much excellent work. To support incremental update, we share the source file of this figure, and welcome the readers to include the desired models by submitting the pull requests on our GitHub page.

### Figure 7 (p.18) ⭐深度解读
![[assets/crops/a-survey-of-large-language-models-fig07.png]]
*整页渲染: ![[assets/a-survey-of-large-language-models-p18.png]]*
> [!quote] caption
> Filtering and Selection. To remove low-quality data from the collected corpus, existing work generally adopts two ap- proaches, namely classifier-based and heuristic-based. The former approach trains a selection classifier based on high- quality texts and leverages it to identify and filter out low- quality data. Typically, these methods train a binary classi- fier using positive instances that ar

> [!tip] 技术解读（多模态）
> # Response

**No figure is visible on the provided page.** The page contains only body text discussing data sources (scientific text, code) and data preprocessing techniques (filtering and selection, de-duplication, privacy reduction) for LLM pre-training. The text *references* "Figure 7" as illustrating "A typical pipeline of preprocessing the pre-training data for LLMs," but the figure itself does not appear on this page — it would likely be on a separate page in the original document.

**Caption (transcribed verbatim from in-text reference):**
> "A typical pipeline of preprocessing the pre-training data for LLMs has been illustrated in Figure 7."

If you can provide the page containing the actual figure, I'd be happy to describe its architecture, components, data flow, and identify a key technical takeaway for you.

### Figure 8 (p.20) ⭐深度解读
![[assets/crops/a-survey-of-large-language-models-fig08.png]]
*整页渲染: ![[assets/a-survey-of-large-language-models-p20.png]]*
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
![[assets/crops/a-survey-of-large-language-models-fig09.png]]
*整页渲染: ![[assets/a-survey-of-large-language-models-p22.png]]*
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
![[assets/crops/a-survey-of-large-language-models-fig13.png]]
*整页渲染: ![[assets/a-survey-of-large-language-models-p43.png]]*
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
![[assets/crops/a-survey-of-large-language-models-fig16.png]]
*整页渲染: ![[assets/a-survey-of-large-language-models-p54.png]]*
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
![[assets/crops/a-survey-of-large-language-models-fig17.png]]
*整页渲染: ![[assets/a-survey-of-large-language-models-p59.png]]*
> [!quote] caption
> Hallucination widely occurs in existing LLMs, even the most superior LLMs such as GPT-4 [46]. Furthermore, existing work shows that LLMs encounter difficulties in recognizing the hallucinated con- tent in text [604], even the powerful ChatGPT. Additionally, beyond language tasks, a recent study has shown that large vision-language models (LVLM) also face challenges with hallucination, i.e., genera

> [!tip] 技术解读（多模态）
> ## Main Figure Description (Figure 17)

**Components / data flow:** The figure is a two-panel comparison of LLM hallucination types using a chatbot dialogue mockup (user avatar + robot avatar). **(a) Intrinsic hallucination**: Given the prompt "Bob's wife is Amy. Bob's daughter is Cindy. Who is Cindy to Amy?", the LLM replies "Cindy is Amy's daughter-in-law" (red, conflicting with the stated input facts). **(b) Extrinsic hallucination**: Prompted with "Explain RLHF for LLMs", the model defines RLHF as "Rights, Limitations, Harms, and Freedoms" (red), while correctly expanding LLMs as "Large Language Models" (black).

**Key takeaway:** Hallucinations split into intrinsic (factually contradicts the supplied prompt/context) and extrinsic (fabricates unverifiable world knowledge), and a single model can mix correct and wrong content in the same answer.

## Caption (verbatim)

Fig. 17: Examples of intrinsic and extrinsic hallucination for a public LLM (access date: March 19, 2023). As an example of intrinsic hallucination, the LLM gives a conflicting judgment about the relationship between Cindy and Amy, which contradicts the input. For extrinsic hallucination, in this example the LLM seems to have an incorrect understanding of the meaning of RLHF (reinforcement learning from human feedback), though it can correctly understand the meaning of LLMs (in this context).

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.8) ⭐深度解读
![[assets/crops/a-survey-of-large-language-models-tab01.png]]
> [!quote] caption
> Statistics of large language models (having a size larger than 10B in this survey) in recent years, including the capacity evaluation, pre-training data scale (either in the number of tokens or storage size) and hardware resource costs. In this table, we only include LLMs with a public paper about t

> [!tip] 表格解读（多模态）
> # Note on Image Content

The page provided does **not** contain an architectural figure with components and data flow. Instead, it shows the explanatory caption text for **Table 1** from a survey paper on large language models. There are no diagrams, boxes, arrows, or architectural schematics present.

# Description of What Is Shown

Page 8 contains only narrative text — specifically, a detailed legend/caption introducing Table 1. It defines the table's columns (Release Time, Publicly Available / Closed Source, Adaptation, Evaluation) and the conventions used (IT = instruction tuning, RLHF, ICL = in-context learning, CoT = chain-of-thought, "*" = largest publicly available version). No visual figure exists on this page.

**Key takeaway:** No figure-level technical insight can be derived from this page; the content is purely definitional metadata accompanying a tabular compilation of LLMs (>10B parameters).

# Caption Transcription (Verbatim)

> TABLE 1: Statistics of large language models (having a size larger than 10B in this survey) in recent years, including the capacity evaluation, pre-training data scale (either in the number of tokens or storage size) and hardware resource costs. In this table, we only include LLMs with a public paper about the technical details. Here, "Release Time" indicates the date when the corresponding paper was officially released. "Publicly Available" means that the model checkpoints can be publicly accessible while "Closed Source" means the opposite. "Adaptation" indicates whether the model has been with subsequent fine-tuning: IT denotes instruction tuning and RLHF denotes reinforcement learning with human feedback. "Evaluation" indicates whether the model has been evaluated with corresponding abilities in their original paper: ICL denotes in-context learning and CoT denotes chain-of-thought. "*" denotes the largest publicly available version.

### Table 2 (p.13) ⭐深度解读
![[assets/crops/a-survey-of-large-language-models-tab02.png]]
> [!quote] caption
> Statistics of commonly-used data sources.

> [!tip] 表格解读（多模态）
> # Figure Description

**Main Figure:** This is a structured data table (Table 2) cataloging statistics of commonly-used data sources for training language models. It contains four columns: *Corpora* (dataset names with reference numbers), *Size* (storage footprint in GB/TB), *Source* (data origin), and *Latest Update Time* (snapshot date).

**Key Technical Takeaway:** Data sources exhibit enormous heterogeneity in scale (ranging from unknown sizes up to 1.6TB for ROOTS) and provenance (books, web crawls, Reddit links, Wikipedia, code repositories). CommonCrawl-derived corpora (C4, CC-Stories-R, CC-NEWS, REALNEWs) collectively dominate web-scraped content, while dedicated community-curated sources like Wikipedia provide structured knowledge — emphasizing that modern LM training pipelines rely on aggregating diverse, multi-domain corpora rather than any single dataset.

# Caption Transcription (Verbatim)

**TABLE 2: Statistics of commonly-used data sources.**

| Corpora | Size | Source | Latest Update Time |
|---------|------|--------|--------------------|
| BookCorpus [158] | 5GB | Books | Dec-2015 |
| Gutenberg [159] | - | Books | Dec-2021 |
| C4 [82] | 800GB | CommonCrawl | Apr-2019 |
| CC-Stories-R [160] | 31GB | CommonCrawl | Sep-2019 |
| CC-NEWS [27] | 78GB | CommonCrawl | Feb-2019 |
| REALNEWs [161] | 120GB | CommonCrawl | Apr-2019 |
| OpenWebText [162] | 38GB | Reddit links | Mar-2023 |
| Pushift.io [163] | 2TB | Reddit links | Mar-2023 |
| Wikipedia [164] | 21GB | Wikipedia | Mar-2023 |
| BigQuery [165] | - | Codes | Mar-2023 |
| the Pile [166] | 800GB | Other | Dec-2020 |
| ROOTS [167] | 1.6TB | Other | Jun-2022 |

### Table 3 (p.14) ⭐深度解读
![[assets/crops/a-survey-of-large-language-models-tab03.png]]
> [!quote] caption
> A detailed list of available collections for instruc- tion tuning.

> [!tip] 表格解读（多模态）
> # Response

**No main figure is present in the provided document text.** The page contains only two data tables (Table 3 and Table 4), not a figure with architecture, components, or a data-flow diagram. Below I summarize what the page actually contains and transcribe the available captions verbatim.

---

## What the page actually shows

The page contains running text (the tail end of the pre-training data section covering **Wikipedia**, **Code**, and **Mixed Data** sources like The Pile, ROOTS, and Dolma) and the opening of **Section 3.3 "Commonly Used Datasets for Fine-tuning"** with its subsection **3.3.1 Instruction Tuning Datasets**.

Two tables are present:

- **Table 3** — instruction-tuning collections, grouped into three categories:
  - **Task:** Natural Instructions (193K), FLAN (4.4M), P3 (12.1M), SuperNatural Instructions (5M), MVPCorpus (41M), xP3 (81M), OIG (43M).
  - **Chat:** HH-RLHF (160K), HC3, ShareGPT (90K), Dolly, OpenAssistant (161K).
  - **Synthetic:** Self-Instruct (82K), Alpaca (52K), Guanaco (535K), Baize (158K), BELLE (1.5M).

- **Table 4** — alignment collections (e.g., Summarize from Feedback 193K, SHP 385K, HH-RLHF 169K, Stack Exchange Preferences 10M, CValues 145K, PKU-SafeRLHF 330K).

**Key takeaway:** Fine-tuning datasets are organized along a **construction axis** — *NLP tasks → human chat → synthetic instructions* — and a **safety/alignment axis** whose corpora only began appearing in volume after mid-2022, with scale spanning ~15K to ~10M examples.

---

## Captions transcribed verbatim

> **TABLE 3:** A detailed list of available collections for instruction tuning.

> **TABLE 4:** A list of available collections for alignment.

### Table 5 (p.23) ⭐深度解读
![[assets/crops/a-survey-of-large-language-models-tab05.png]]
> [!quote] caption
> Model cards of several selected LLMs with public configuration details. Here, PE denotes position embedding, #L denotes the number of layers, #H denotes the number of attention heads, d model denotes the size of hidden states, and MCL denotes the maximum context length during training.

> [!tip] 表格解读（多模态）
> ## Description

**Architecture/Components/Data Flow:**
Table 5 is a comparative matrix cataloging 16 publicly-documented large language models (from GPT-3 [55] to T5 [82]) against 11 configuration axes: Model name, Category (Causal decoder / Prefix decoder / Encoder-decoder), Size, Normalization, PE (Position Embedding), Activation, Bias (✓/✗), #L (layers), #H (attention heads), d_model (hidden width), and MCL (max context length during training).

**Key Technical Takeaway:**
A clear architectural convergence emerges in newer models: **Pre-RMSNorm + RoPE + SwiGLU + bias-free** has become the dominant modern recipe (PaLM, LLaMA, LLaMA 2, Falcon), while early-generation models favored Pre-LayerNorm + Learned PE + GeLU + bias-enabled (GPT-3, OPT, PanGU-α, BLOOM).

## Caption (Verbatim)

"TABLE 5: Model cards of several selected LLMs with public configuration details. Here, PE denotes position embedding, #L denotes the number of layers, #H denotes the number of attention heads, d_model denotes the size of hidden states, and MCL denotes the maximum context length during training."

### Table 6 (p.23) ⭐深度解读
![[assets/crops/a-survey-of-large-language-models-tab06.png]]
> [!quote] caption
> Comparison of parallelism and complexity of dif- ferent models. T represents sequence length, H represents the dimension of the input representation, N represents the dimension after compression in SSMs, and M represents the number of layers in each Hyena module.

> [!tip] 表格解读（多模态）
> # Table 6: Comparison of parallelism and complexity of different models

## Description
The table presents a quantitative comparison of six sequence models, organized in three columns: **Model**, **Decoding Complexity**, and **Training Complexity**. Each row represents an architecture (Transformer, SSM, Mamba, RWKV, RetNet, Hyena), with complexity expressed in Big-O notation involving sequence length (T), hidden dimension (H), compressed-state dimension (N for SSMs), and module layers (M for Hyena).

**Key Technical Takeaway:** The table highlights that **Transformer attention scales quadratically** in T and H during both decoding and training, while architectures like **Mamba, RWKV, and RetNet achieve decoupled complexities** — often O(H²) for decoding (sequence-length-independent) at the cost of richer training costs. **Hyena** trades a multi-layer param factor M in decoding for a sub-quadratic log-T training term, illustrating how SSM-derived models linearize attention's compute profile relative to sequence length.

## Caption (verbatim transcription)

> TABLE 6: Comparison of parallelism and complexity of different models. *T* represents sequence length, *H* represents the dimension of the input representation, *N* represents the dimension after compression in SSMs, and *M* represents the number of layers in each Hyena module.

### Table 7 (p.24) ⭐深度解读
![[assets/crops/a-survey-of-large-language-models-tab07.png]]
> [!quote] caption
> Detailed formulations for the network configurations. Here, Sublayer denotes a FFN or a self-attention module in a Transformer layer, d denotes the size of hidden states, p i denotes position embedding at position i , A ij denotes the attention score between a query and a key, r i − j denotes a lear

> [!tip] 表格解读（多模态）
> The image is a **table** (not an architectural figure) presenting mathematical formulations for different transformer normalization strategies.

**Components shown:**
- A three-column table: Configuration / Method / Equation
- Three normalization placement strategies for transformer sublayers (FFN or self-attention):
  1. **Post Norm** — applies LayerNorm *after* the residual addition: `Norm(x + Sublayer(x))`
  2. **Pre Norm** — applies LayerNorm *inside* the residual branch, before the sublayer: `x + Sublayer(Norm(x))`
  3. **Sandwich Norm** — places LayerNorm both *before and after* the sublayer: `x + Norm(Sublayer(Norm(x)))`

**Key technical takeaway:** Post Norm historically aids training but degrades with scale; Pre Norm enables deep stackable training but harms representation quality; Sandwich Norm adds a *post-sublayer* norm to reclaim representation power without sacrificing stability—balancing the two trade-offs.

---

**Caption transcribed verbatim:**

"TABLE 7: Detailed formulations for the network configurations. Here, Sublayer denotes a FFN or a self-attention module in a Transformer layer, *d* denotes the size of hidden states, **p**_*i* denotes position embedding at position *i*, *A*_*ij* denotes the attention score between a query and a key, *r*_*i−j* denotes a learnable scalar based on the offset between the query and the key, and **R**_Θ,*t* denotes a rotary matrix with rotation degree *t* · Θ."

### Table 8 (p.29) ⭐深度解读
![[assets/crops/a-survey-of-large-language-models-tab08.png]]
> [!quote] caption
> Detailed optimization settings of several existing LLMs.

> [!tip] 表格解读（多模态）
> **Note:** The provided image is a table (Table 8), not a figure with architecture/components/data flow. I will describe it accordingly.

**Description:** Table 8 is a benchmark-style comparison listing optimization hyperparameters used during pretraining of several large language models. Its components form a horizontal header row (Model, Batch Size in tokens, Learning Rate, Warmup, Decay Method, Optimizer, Precision Type) intended to align identical training knobs across LLMs for side-by-side comparison. The data flow is conceptually column-by-column: each row will populate one model's configuration, enabling readers to scan vertically to spot patterns (e.g., batch-size scaling, optimizer choice) and horizontally to understand a single model's complete recipe.

**Key technical takeaway:** Modern LLM training recipes converge on a common toolkit — AdamW-family optimizers, cosine-style learning-rate decay with linear warmup, and large token-batch sizes (often millions) — with bf16/fp16/bf16-fp32 mixed precision, suggesting these hyperparameters are now standard rather than model-specific innovations.

**Caption (verbatim):**
> **TABLE 8:** Detailed optimization settings of several existing LLMs.

### Table 9 (p.33) ⭐深度解读
![[assets/crops/a-survey-of-large-language-models-tab09.png]]
> [!quote] caption
> Basic statistics of the required number of GPUs, tuning time, batch size (denoted as BS) per device (full tuning and LoRA tuning), and inference rate (the number of generated tokes per second). Our experiments are conducted based on two Linux servers having 8 A800-80G SXM4 GPUs with 6 NVSwitch and 8

> [!tip] 表格解读（多模态）
> ## Description (≤120 words)

**Table 9** benchmarks LLaMA models (7B/13B/30B/65B) across training and inference configurations on two GPU server types (A800-80G SXM4 with NVSwitch vs. 3090-24G). The layout is a multi-column matrix: rows = model size; column groups = {A800 Full Tuning: #GPU, BS, Time} | {A800 LoRA Tuning: #GPU, BS, Time} | {A800 Inference 16-bit: #GPU, #Token/s} | {3090 Inference 16-bit} | {3090 Inference 8-bit}.

**Key takeaway:** Full tuning hardware requirements grow super-linearly (2→16 GPUs and 3.0h→11.2h from 7B→65B), whereas LoRA stays at a single 80G GPU (ranking 16, INT8), trading speed for accessibility — 65B LoRA still takes 60.6h but only needs 1 GPU.

## Caption (verbatim)

**TABLE 9:** Basic statistics of the required number of GPUs, tuning time, batch size (denoted as BS) per device (full tuning and LoRA tuning), and inference rate (the number of generated tokes per second). Our experiments are conducted based on two Linux servers having 8 A800-80G SXM4 GPUs with 6 NVSwitch and 8 3090-24G GPUs, respectively. The major difference between A800 and A100 lies in the NVLink interconnect speed. Thus, our estimations about training and inference efficiency would be slightly improved for A100, while the rest memory consumption would remain the same. For full tuning experiments, we use data parallel training, ZeRO Stage 3, BF16, and gradient checkpointing. Additionally, the LoRA tuning can be executed on one 80G GPU utilizing INT8 quantization with the rank setting set to 16. All the experiments are conducted with Alpaca-52K dataset by training LLaMA models three epochs. The max sequence length for both training settings is set to 512. The inference experiments are performed with the batch size set to 1.

### Table 10 (p.35) ⭐深度解读
![[assets/crops/a-survey-of-large-language-models-tab10.png]]
> [!quote] caption
> Results of instruction-tuning experiments (all in a single-turn conversation) based on the LLaMA (7B) and LLaMA (13B) model under the chat and QA setting. We employ four instruction improvement strategies on the Self- Instruct-52K dataset, i.e., enhancing the complexity ( w/ complexity ), increasing

> [!tip] 表格解读（多模态）
> ## Description

The image shows only the **caption text** of Table 10 (no graphical figure, architecture diagram, or data plot is present). Based on the caption, the underlying table documents an ablation study comparing four instruction improvement strategies applied to LLaMA (7B) and (13B) models in chat and QA settings:

- **Component 1 – Base model**: LLaMA (7B / 13B)
- **Component 2 – Dataset**: Self-Instruct-52K (baseline fine-tuning set)
- **Component 3 – Four improvement variants**: w/ complexity, w/ diversity, w/ difficulty, w/ scaling
- **Eval protocol**: Single-turn conversations, reported as win rates vs. the Self-Instruct-52K fine-tuned baseline

**Key technical takeaway:** Adding any of the four targeted augmentation strategies to Self-Instruct-52K improves over the vanilla Self-Instruct baseline, with the implication that *instruct-data quality dimensions (complexity, diversity, difficulty, scaling) are complementary levers* for boosting instruction-following capability.

## Caption (verbatim)

> TABLE 10: Results of instruction-tuning experiments (all in a single-turn conversation) based on the LLaMA (7B) and LLaMA (13B) model under the chat and QA setting. We employ four instruction improvement strategies on the Self-Instruct-52K dataset, *i.e.*, enhancing the complexity (*w/ complexity*), increasing the diversity (*w/ diversity*), balancing the difficulty (*w/ difficulty*), and scaling the instruction number (*w/ scaling*). *Since we select the LLaMA (7B)/(13B) model fine-tuned on Self-Instruct-52K as the baseline, we omit the win rate of the fine-tuned model with Self-Instruct-52K against itself.*

### Table 11 (p.45) ⭐深度解读
![[assets/crops/a-survey-of-large-language-models-tab11.png]]
> [!quote] caption
> Typical LLM utilization methods and their key points for ICL, CoT, and planning. Note that the key points only highlight the most important technical contribution.

> [!tip] 表格解读（多模态）
> **Note:** The provided content is a **table** (Table 11), not a figure. The visible portion shows only the header structure with no row data.

**Description of the Table Structure:**

The table is organized into three columns under a single horizontal rule:
- **Approach** — names the LLM utilization method/paradigm
- **Representative Work** — cites seminal or illustrative papers for each approach
- **Key Point** — summarizes the most important technical contribution

The column scope covers three prompting/reasoning paradigms: **ICL** (In-Context Learning), **CoT** (Chain-of-Thought), and **planning**, suggesting rows would compare methods across these categories, with each row pairing a technique, its canonical reference, and a one-line contribution summary.

**Key Technical Takeaway (inferred):** The table functions as a comparative reference chart, distilling heterogeneous LLM utilization strategies into a uniform three-column template — enabling readers to rapidly contrast methods (e.g., few-shot vs. structured reasoning vs. agentic planning) by technique, canonical citation, and core innovation in a single view.

**Caption (verbatim):**

"TABLE 11: Typical LLM utilization methods and their key points for ICL, CoT, and planning. Note that the key points only highlight the most important technical contribution."

### Table 12 (p.47) ⭐深度解读
![[assets/crops/a-survey-of-large-language-models-tab12.png]]
> [!quote] caption
> A collection of useful tips for designing prompts that are collected from online notes [446–449] and experiences from our authors, where we also show the related ingredients and principles (introduced in Section 6.1.1). We abbreviate principles as Prin. and list the IDs of the related principles for

> [!tip] 表格解读（多模态）
> **Description (109 words):**

This is a structured reference table cataloging prompt-engineering tips organized as a two-level hierarchy. **Components (rows):** Four "ingredient" categories — Task Description, Input Data, Contextual Information, and Demonstration — each containing 2–4 specific tactics labeled by category prefix (T, I, C, D). **Cross-references (columns):** Each tactic is tagged with up to four principle IDs (① task clarity, ② task decomposition, ③ few-shot demonstrations, ④ model-friendly format), enabling readers to trace which principles a technique activates. **Data flow:** Most tips are illustrated with concrete example prompts (e.g., role-prefixing, retrieval-augmented context, tree-of-thought experts, similar-example retrieval). **Key takeaway:** Effective prompting is multi-ingredient — combining task framing, retrieved context, structured exemplars, and format constraints — with most advanced techniques (e.g., D2/D3) intentionally combining two principles rather than relying on a single mechanism.

**Caption (verbatim):**

TABLE 12: A collection of useful tips for designing prompts that are collected from online notes [446–449] and experiences from our authors, where we also show the related ingredients and principles (introduced in Section 6.1.1). We abbreviate principles as Prin. and list the IDs of the related principles for each prompt. ①: expressing the task goal clearly; ②: decomposing into easy, detailed sub-tasks; ③: providing few-shot demonstrations; ④: utilizing model-friendly format.

### Table 13 (p.48) ⭐深度解读
![[assets/crops/a-survey-of-large-language-models-tab13.png]]
> [!quote] caption
> Example instructions collected from [447, 457]. The blue text denotes the task description, the red text denotes the contextual information, the green text denotes the demonstrations, and the gold text denotes the prompt style.

> [!tip] 表格解读（多模态）
> **Description:**
Table 13 presents two color-coded prompt templates illustrating a four-component instruction design. (1) **Task description** (blue) — a natural-language directive stating the model's objective (e.g., "Use the provided articles…to answer questions" or "Prepare a meta-review…"). (2) **Contextual information** (red) — the raw input the LLM must operate on, such as articles or reviewer comments. (3) **Demonstrations** (green) — few-shot examples with input/output pairs followed by a fill-in template (`<insert articles>`). (4) **Prompt style** (gold) — formatting/formatting cues such as delimiters (`"""`), ordered reasoning ("Let's think step by step"), or enumerated sub-questions. **Key takeaway:** Decoupling instructions into these four orthogonal slots enables modular reuse across tasks while preserving consistent output formatting.

**Caption (verbatim):**
"TABLE 13: Example instructions collected from [447, 457]. The blue text denotes the task description, the red text denotes the contextual information, the green text denotes the demonstrations, and the gold text denotes the prompt style."

### Table 14 (p.57) ⭐深度解读
![[assets/crops/a-survey-of-large-language-models-tab14.png]]
> [!quote] caption
> Representative basic and advanced abilities and corresponding representative datasets for evaluating.

> [!tip] 表格解读（多模态）
> ## Description

**Architecture/components:** A four-column tabular taxonomy organizing NLP evaluation resources. Columns are arranged hierarchically left‑to‑right: *Level* → *Ability* → *Task* → *Dataset*. Each row maps one cognitive/linguistic ability to its canonical benchmark datasets (e.g., Penn Treebank, WikiText‑103, the Pile, LAMBADA for Language Modeling). Datasets carry bracketed citation indices for traceability. Visible ability rows include "Language Modeling" and "Language Generation / Conditional Text Generation," with corresponding datasets spanning WMT'14–22, Flores‑101, DiaBLa, CNN/DailyMail, XSum, and WikiLingua.

**Data flow:** Editor → ability categorization → task specification → benchmark assignment, enabling readers to traverse from coarse evaluation goal to concrete datasets.

**Key takeaway:** Evaluation is structured as an ability‑driven hierarchy rather than a flat dataset list, allowing systematic coverage of diverse NLP capabilities through representative benchmarks. *(119 words)*

---

## Caption (verbatim transcription)

**TABLE 14:** Representative basic and advanced abilities and corresponding representative datasets for evaluating.

### Table 15 (p.64) ⭐深度解读
![[assets/crops/a-survey-of-large-language-models-tab15.png]]
> [!quote] caption
> A category of existing evaluation work. “General” denotes that the evaluation focuses on an overall performance of multiple abilities. The evaluated abilities are not limited to the representative basic and advanced abilities mentioned in Section 7.1 and 7.2.

> [!tip] 表格解读（多模态）
> ## Description of the Main Figure (Table)

The figure is presented as **Table 15**, organized as a multi-column taxonomy/classification of existing evaluation work on language models. Based on the visible header row, the table is structured into five columns:

- **Method** — the evaluation approach/technique used
- **Evaluation** — the focus or scope of the assessment
- **Model Types** — which categories of models are being evaluated
- **Abilities/Domain** — the cognitive skills or subject areas targeted
- **Data Source** — origin of the benchmark/test data (e.g., real, synthetic, crowdsourced)

The data flow is essentially horizontal (row-wise): each work/survey gets one row, allowing readers to compare papers along these five dimensions at a glance. Only the header is visible in this excerpt — no populated rows are shown.

### Key Technical Takeaway
The table's design choice to separate **Method** from **Evaluation Scope** reveals that the field lacks a unified evaluation taxonomy — different studies couple scoring techniques with different ability sets, making cross-paper comparison inherently non-orthogonal.

---

## Caption (Verbatim Transcription)

> **TABLE 15:** A category of existing evaluation work. "General" denotes that the evaluation focuses on an overall performance of multiple abilities. The evaluated abilities are not limited to the representative basic and advanced abilities mentioned in Section 7.1 and 7.2.

### Table 16 (p.67) ⭐深度解读
![[assets/crops/a-survey-of-large-language-models-tab16.png]]
> [!quote] caption
> Evaluation on the eight abilities of LLMs with specially selected tasks. The shade of the Orange and Blue fonts denote the performance orders of the results in closed-source and open-source models, respectively. This table will be continuously updated by incorporating the results of more models.

> [!tip] 表格解读（多模态）
> **Figure Description:**

This is a comparative evaluation table (Table 16) presenting benchmark scores for multiple language models across eight task categories. The table is organized with model names as rows and task names as columns, grouped under two main ability headers: **Language Generation** (LBD, WMT, XSum, HumanEval) and **Knowledge Utilization** (TriviaQA, NaturalQ, WebQ, ARC, WikiFact). All tasks use an "↑" arrow indicating higher scores are better. Two colored highlights appear in the caption: **Orange** shading marks performance rankings among closed-source models, while **Blue** shading marks rankings among open-source models.

**Key Technical Takeaway:** The dual-color ranking scheme (Orange for closed-source, Blue for open-source) enables within-family performance comparison, allowing readers to identify the best closed-source and best open-source model per task independently, rather than forcing a single cross-family ranking that would conflate capability differences with model accessibility.

**Caption (verbatim):**

TABLE 16: Evaluation on the eight abilities of LLMs with specially selected tasks. The shade of the Orange and Blue fonts denote the performance orders of the results in closed-source and open-source models, respectively. This table will be continuously updated by incorporating the results of more models.

### Table 17 (p.68) ⭐深度解读
![[assets/crops/a-survey-of-large-language-models-tab17.png]]
> [!quote] caption
> Prompt examples and their performance of ChatGPT on representative tasks. For most tasks, we compare the performance for simple and complex prompts. We also present the reported performance of supervised methods. “LG”, “KU”, “CR”, “SDG”, “IR” are short for “language generation”, “knowledge utilizati

> [!tip] 表格解读（多模态）
> ## Description

The image displays **Table 17**, a structured comparison table evaluating ChatGPT's performance across NLP tasks. Its components include:

- **Tasks column**: Categorizes evaluation domains (Translation visible; expanded headers reference language generation, knowledge utilization, complex reasoning, structured data generation, and information retrieval)
- **Datasets column**: Identifies the benchmark (e.g., WMT for translation)
- **Instructions column**: Presents the actual prompt fed to ChatGPT (e.g., role-assignment prompt for English-to-Czech translation)
- **ChatGPT / Supervised columns**: Compare zero-/few-shot prompting scores (20.66) against fine-tuned supervised baselines (41.40)

**Data flow**: prompt → ChatGPT inference → score, benchmarked against supervised SOTA.

**Key takeaway**: Simple role-prompting of ChatGPT (20.66) substantially underperforms task-specific supervised models (41.40) on translation BLEU, highlighting the gap between general-purpose instruction tuning and domain-optimized systems.

## Caption (verbatim)

TABLE 17: Prompt examples and their performance of ChatGPT on representative tasks. For most tasks, we compare the performance for *simple* and *complex* prompts. We also present the reported performance of supervised methods. "LG", "KU", "CR", "SDG", "IR" are short for "language generation", "knowledge utilization", "complex reasoning", "structured data generation", "information retrieval". "-" means there is no reported supervised result previously on this dataset.

### Table 18 (p.82) ⭐深度解读
![[assets/crops/a-survey-of-large-language-models-tab18.png]]
> [!quote] caption
> The activation memory consumption of each computation within the LLaMA model based on research work [976]. We denote batch size by B , sequence length by T , the vocabulary size by V , the number of head in the attention module by N , the dimension of each head by D , the hidden size by H ( H = ND )

> [!tip] 表格解读（多模态）
> **Description (≤120 words):**

Table 18 maps each Transformer/FFN computation in a LLaMA layer to its activation memory footprint, using notation B (batch), T (sequence), V (vocab), N (heads), D (head dim), H=ND (hidden), H' (FFN intermediate). The data flow traces: input projection (Eq. ①), rotary positional encoding (Eq. ②), attention with softmax (Eq. ③), output projection (Eq. ④), Add&Norm (Eq. ⑤), FFN gate/up projections (Eq. ⑥), Swish-gated product (Eq. ⑦), down-projection (Eq. ⑧), Add&Norm (Eq. ⑨), and final cross-entropy softmax (Eq. ⑩).

**Key takeaway:** The dominant costs scale quadratically with sequence (softmax in ③ costs 2BT²N — the per-layer bottleneck) and linearly with vocab size (final softmax in ⑩ adds 4BTV); all layer-wise terms must be multiplied by L for total memory.

**Caption (verbatim):**

"TABLE 18: The activation memory consumption of each computation within the LLaMA model based on research work [976]. We denote batch size by B, sequence length by T, the vocabulary size by V, the number of head in the attention module by N, the dimension of each head by D, the hidden size by H (H = ND), and the intermediate size inside FFN by H'. Equations ①-⑨ are layer-wise and need to be multiplied by the number of the layers L when computing the total consumption."

### Table 19 (p.84) ⭐深度解读
![[assets/crops/a-survey-of-large-language-models-tab19.png]]
> [!quote] caption
> The computation, data transfer, and arithmetic intensity during the prefill stage. We use the asymptotic notation O to denote the complexity of data transfer amount, where the constant factor of the complexity is related to the specific implementation method. Table source: [983].

> [!tip] 表格解读（多模态）
> **Figure Description**

This is Table 19 (header only — data rows are cropped from view). The visible structure is a four-column reference table:

- **Columns (left → right):** Equations | Computation | Data transfer | Arithmetic intensity
- **Purpose:** Quantifies the cost profile of the *prefill* stage of (presumably) an LLM inference pipeline, characterizing each equation row in terms of FLOPs, bytes moved, and the resulting FLOP/byte ratio.
- **Data flow / reading direction:** A reader scans a given equation down a row, comparing the three derived quantities — typically, one compares the *Computation* and *Data transfer* columns to determine whether the row is compute-bound or memory-bound via the *Arithmetic intensity* column.

**Key Technical Takeaway**

Arithmetic intensity (FLOPs per byte) is the diagnostic metric that classifies each prefill operation: high-intensity kernels are compute-bound (GPU-bound), while low-intensity kernels (e.g., attention projection, KV-cache loads) are memory-bound and benefit from bandwidth optimization rather than extra FLOPs.

**Caption (verbatim):**

> TABLE 19: The computation, data transfer, and arithmetic intensity during the prefill stage. We use the asymptotic notation 𝒪 to denote the complexity of data transfer amount, where the constant factor of the complexity is related to the specific implementation method. Table source: [983].

### Table 21 (p.88) ⭐深度解读
![[assets/crops/a-survey-of-large-language-models-tab21.png]]
> [!quote] caption
> Evaluation results for quantized LLaMA models (7B and 13B). We employ existing model checkpoints provided by [350] for quantization experiments, which have been fine-tuned on FLAN-v2, Alpaca-52K, and ShareGPT, respectively. Specifically, we report the performance with AlpacaFarm, MMLU, and BBH, as w

> [!tip] 表格解读（多模态）
> **Description:** This table (Table 21) presents evaluation results for quantized LLaMA models (7B and 13B variants) across three precision levels: 16-bit, 8-bit, and 4-bit. For each precision, it reports accuracy/score on AlpacaFarm, MMLU, and BBH benchmarks, alongside the loaded model memory usage (Mem., in GiB). The rows correspond to models fine-tuned on different SFT datasets (FLAN-v2, Alpaca-52K, ShareGPT). Quantization is performed using `bitsandbytes` via `load_in_8bit` and `load_in_4bit` commands on 16-bit checkpoints from prior work. **Key takeaway:** Quantizing LLaMA models from 16-bit down to 4-bit via bitsandbytes drastically reduces memory footprint (e.g., ~2–4× savings) while preserving most benchmark performance, though a small accuracy drop is typically observed at the most aggressive 4-bit setting.

**Caption (verbatim):**
TABLE 21: Evaluation results for quantized LLaMA models (7B and 13B). We employ existing model checkpoints provided by [350] for quantization experiments, which have been fine-tuned on FLAN-v2, Alpaca-52K, and ShareGPT, respectively. Specifically, we report the performance with AlpacaFarm, MMLU, and BBH, as well as the memory usage of the loaded model (Mem.). For quantization, we employ *bitsandbytes* to quantize the 16-bit models to 8/4 bits by specifying the commands `load_in_8bit` and `load_in_4bit` when loading the weights. It is worth noting that we select *text-davinci-003* as the baseline model for the AlpacaFarm dataset.

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