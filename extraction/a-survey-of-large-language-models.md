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
> 【图文联合解读】**图文联合解读：**

图1以arXiv月度标题/摘要精确匹配统计：**(a)**"language model"自2018年6月起累计从约200篇（GPT-1锚点）增至2023年初近10000篇（GPT-4）；**(b)**"large language model"自2019年10月近乎零（T5锚点）飙至约1780篇（GPT-4），两曲线均呈指数式爆发。作者借此论证：从早期语言建模到GPT-4等复杂任务求解是科学思维的重要飞跃，LLM兴起标志着AI研究范式转折。该图作为引言动机，为后文Table 1对十亿级LLM的系统梳理与技术演进讨论奠定量化基础。

### Figure 3 (p.99) ⭐深度解读
![[assets/crops/a-survey-of-large-language-models-fig03.png]]
*整页渲染: ![[assets/a-survey-of-large-language-models-p99.png]]*
> [!quote] caption
> – Section 4: add LLM-based data filtering and selec- tion methods in Section 4.1.2; update Section 4.2.1, “Emergent Architectures” to include more discus- sions about SSM-based architectures; add Table 6 to compare parallelism and complexity of different architectures. – Section 5: add latest discussion about instruction quality improvement and instruction selection in

> [!tip] 技术解读（多模态）
> 【图文联合解读】图3以时间轴（2019–2026）呈现约70+款代表性LLM。2019年仅T5单点；2022–2024集中爆发（GPT-3/4、LLaMA2、Qwen、Claude 3.5、DeepSeek等）；2025年单年即含DeepSeek-R1、GPT-o3、Claude 4.5、LLaDA、M2等30+款；黄色高亮标记公开权重模型。

**技术结论**：LLM研发呈指数级扩张，开源生态与商业闭源双轨并行，中美欧多元主体激烈竞争，迭代周期压缩至月级。

**论文作用**：作为综述"全景基线图"，为后续预训练、对齐微调、应用等章节建立模型谱系与时序坐标，辅助读者跨章节交叉定位与引用。

### Figure 4 (p.7) ⭐深度解读
![[assets/crops/a-survey-of-large-language-models-fig04.png]]
*整页渲染: ![[assets/a-survey-of-large-language-models-p07.png]]*
> [!quote] caption
> The basic principle underlying GPT models is to compress the world knowledge into the decoder-only

> [!tip] 技术解读（多模态）
> 【图文联合解读】图4以时间线展示OpenAI GPT系列技术演化，含三分支结构：主干GPT-1(2018.06)→GPT-2(2019.02)→GPT-3(2020.05)→Codex(2021.07)→GPT-3.5(2022.03)→GPT-4(2023.03)；对齐链code-davinci-002→text-davinci-002/003→gpt-3.5-turbo；GPT-4 Turbo(2023.09)扩展长上下文与视觉。实线=官方继承证据，虚线=关联推断。原文借此论证GPT遵循"decoder-only预训练→规模缩放→in-context learning→代码预训练→指令/RLHF对齐→多模态"演进范式，作为后续预训练、对齐、能力评测章节的方法论奠基图谱。

### Figure 5 (p.12) ⭐深度解读
![[assets/crops/a-survey-of-large-language-models-fig05.png]]
*整页渲染: ![[assets/a-survey-of-large-language-models-p12.png]]*
> [!quote] caption
> Public API of LLMs. Instead of directly using the model copies, APIs provide a more convenient way for common users to use LLMs, without the need of running the model locally. As a representative interface for using LLMs, the APIs for the GPT-series models [46, 55, 66, 105] have been widely used for both academia and industry19.

> [!tip] 技术解读（多模态）
> 【图文联合解读】图5是以LLaMA为根节点的衍生模型演化树，约含30余个变体。结构上：①红色虚线表示"继续预训练"路径（如Chinese-LLaMA、Open-Chinese-LLaMA）；②绿色实线为指令微调中的"模型继承"，蓝色为"数据继承"（如Alpaca用合成数据、Vicuna用chat数据）；③黄/白框区分参数高效微调与全参数微调；④底部涵盖数学、金融、医学、法律、教育、双语六大领域，右侧虚线框归集多模态变体（LLaVA、MiniGPT-4等）。

该图论证三点结论：(1)开源基模LLaMA催生庞大衍生生态；(2)训练数据与微调策略是模型分化的核心轴；(3)LLaMA已向垂直领域与多模态双向扩展。

在论文整体方法链中，此图作为开源LLM生态的"可视化快照"，与Table 5（模型配置详情表）互补，从宏观分布与微观参数两个尺度支撑"开源驱动快速迭代"的中心论点。

### Figure 7 (p.18) ⭐深度解读
![[assets/crops/a-survey-of-large-language-models-fig07.png]]
*整页渲染: ![[assets/a-survey-of-large-language-models-p18.png]]*
> [!quote] caption
> Filtering and Selection. To remove low-quality data from the collected corpus, existing work generally adopts two ap- proaches, namely classifier-based and heuristic-based. The former approach trains a selection classifier based on high- quality texts and leverages it to identify and filter out low- quality data. Typically, these methods train a binary classi- fier using positive instances that ar

> [!tip] 技术解读（多模态）
> 【图文联合解读】**核心结构**：图7以6阶段流水线呈现LLM预训练数据预处理全流程——Raw Corpus（网页、图书、论文、GitHub等多源原始语料）→ Filtering & Selection（语言/指标/统计/关键词四类过滤）→ De-duplication（句级/文档级/集合级去重）→ Privacy Reduction（检测并替换PII）→ Tokenization（复用/SentencePiece/BPE）→ Ready to pre-train（输出数值token序列）。每阶段均以"Alice is writing a paper about LLMs."为例演示具体操作（如删除脏字、划线去重、Replace替换人名、Encode编码）。

**关键技术结论**：原文指出过滤筛选分classifier-based与heuristic-based两类，前者训练二分类器以高质量文本为正例识别低质数据；去重与隐私脱敏在多粒度执行以提升数据纯净度与合规性。

**论文作用**：该图作为第2章"Pre-training Data"的方法总纲，将散落于各小节的清洗、去重、脱敏、分词技术整合为端到端流程，为后续章节讨论各模型（Gopher、GPT-3、LLaMA等）的具体数据策略提供统一参照框架。

### Figure 8 (p.20) ⭐深度解读
![[assets/crops/a-survey-of-large-language-models-fig08.png]]
*整页渲染: ![[assets/a-survey-of-large-language-models-p20.png]]*
> [!quote] caption
> Data Mixture. Since each kind of data source is closely related to the development of certain capacities for LLMs (referring to the discussions in Section 4.1), it is important to set a suitable distribution to mix these data. The data mixture is generally set in a global level (i.e., the distribution of the entire pre-training data), and can be also locally set to varied proportions at different 

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图示4类数据源（Source 1–4）依次在Stage 1、Stage 2、…、Stage n–1、Stage n共n个预训练阶段中的占比柱状变化：Stage 1以Source 1为主，Stage 2趋向四源均衡，Stage n–1偏向Source 3，Stage n又以Source 4最重。曲线箭头标注"Data Mixture"指向任一阶段内的源配比，大括号"Data Curriculum"则横跨所有阶段。

原文借此论证两点关键结论：① 数据混合在**全局**层面设定源分布；② 数据课程在**局部**允许各阶段按比例动态调整，以契合不同能力的培养需求。该图是论文第4章数据准备部分的核心可视化，串联起数据源选择→混合策略→课程调度的完整预训练数据管线，为下游训练实验章节提供调度框架支撑。

### Figure 9 (p.22) ⭐深度解读
![[assets/crops/a-survey-of-large-language-models-fig09.png]]
*整页渲染: ![[assets/a-survey-of-large-language-models-p22.png]]*
> [!quote] caption
> Encoder-decoder Architecture. The vanilla Transformer model is built on the encoder-decoder architecture [22], which consists of two stacks of Transformer blocks as the encoder and decoder, respectively. The encoder adopts stacked multi-head self-attention layers to encode the input sequence for generating its latent representations, while the decoder performs cross-attention on these representa- 

> [!tip] 技术解读（多模态）
> 【图文联合解读】图以"A Survey of Large Language Models"（前3 token为prefix、后3为target）为示例，用三个6×6矩阵对比三种架构的注意力模式，颜色编码：前缀互注意（蓝）、前缀→目标（绿）、目标互注意（黄）、掩码（灰）。具体差异：
- **Causal Decoder**：prefix单向（左下蓝三角）、target因果（右下黄下三角）、prefix→target绿，无target→prefix；
- **Prefix Decoder**：prefix全蓝、target全黄（双向），仅target→prefix掩码；
- **Encoder-Decoder**：编码器3×3全蓝（双向），解码器行对编码器列绿（cross-attention），target自身因果。

论文借此论证三类主流架构的本质差异在于注意方向性与prefix/target是否解耦，奠定GPT系、LLaMA系、T5系LLM分类的架构谱系基础，是方法论总览部分的关键可视化锚点。

### Figure 13 (p.43) ⭐深度解读
![[assets/crops/a-survey-of-large-language-models-fig13.png]]
*整页渲染: ![[assets/a-survey-of-large-language-models-p43.png]]*
> [!quote] caption
> Adapter Tuning. Adapter tuning incorporates small neural network modules (called adapter) into the Transformer mod- els [406]. To implement the adapter module, a bottleneck architecture has been proposed in [406, 407], which first compresses the original feature vector into a smaller di- mension (followed by a nonlinear transformation) and then recovers it to the original dimension. The adapter mo

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读（Figure 13，p.43）**

**① 核心对象与结构**  
图示对比四种 PEFT 方法的 Transformer 接入方式：(a) Adapter Tuning — 每层在 MHA→FFN 之间、FFN 之后各嵌一个瓶颈 Adapter 模块；(b) Prefix Tuning — 在 Layer #1~#N 各层前均注入可训练 Prefix 向量；(c) Prompt Tuning — 仅在输入端前置一个 Prompt，深层不再附加；(d) LoRA — 在每层旁并行接入低秩矩阵对 W_up / W_down。

**② 原文技术结论**  
四种方案的差异本质在于"可训练参数注入位置"：层内瓶颈（Adapter）、逐层前缀（Prefix）、输入级提示（Prompt）、并行低秩分解（LoRA），均冻结原模型主体，仅训练极少附加参数即可适配下游任务。

**③ 论文整体作用**  
作为 Adaptation 章节的核心对比图，为读者建立 PEFT 方法全景认知，支撑后续"参数高效微调显著降低大模型部署与适配成本"的论述。

### Figure 16 (p.54) ⭐深度解读
![[assets/crops/a-survey-of-large-language-models-fig16.png]]
*整页渲染: ![[assets/a-survey-of-large-language-models-p54.png]]*
> [!quote] caption
> In this paradigm, there are typically three components: task planner, plan executor, and environment36. Specifically, task planner, which is played by LLMs, aims to generate the whole plan to solve a target task. The plan can be presented in various forms, e.g., an action sequence in the form of natural language [432] or an executable program written in programming language [436]. The LLM-based ta

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

该图展示LLM提示式规划的三组件闭环：**Task Planner(LLM)** 输出Plan→**Plan Executor** 执行Action→作用于**Environment**；执行结果通过**Feedback**回传Planner实现"generate & refine"迭代，最终输出Result。Environment分内部(LLM/Memory)与外部(Human/World/Other/Tool)两类。

论文借此论证：LLM作为任务规划器，可生成自然语言动作序列或可执行程序，通过人–机–世界反馈循环，将单步推理扩展为多步复杂任务求解。

在论文方法链中，该图为第4章"规划与决策"提供统一形式化框架，与Tool use、Memory、Reflection等子节并列，支撑后续实验评估中"复杂任务解决能力"的论证。

### Figure 17 (p.59) ⭐深度解读
![[assets/crops/a-survey-of-large-language-models-fig17.png]]
*整页渲染: ![[assets/a-survey-of-large-language-models-p59.png]]*
> [!quote] caption
> Hallucination widely occurs in existing LLMs, even the most superior LLMs such as GPT-4 [46]. Furthermore, existing work shows that LLMs encounter difficulties in recognizing the hallucinated con- tent in text [604], even the powerful ChatGPT. Additionally, beyond language tasks, a recent study has shown that large vision-language models (LVLM) also face challenges with hallucination, i.e., genera

> [!tip] 技术解读（多模态）
> 【图文联合解读】图17以两组对话展示LLM幻觉：(a)内在幻觉——输入"Bob之妻Amy、之女Cindy"的事实后，LLM却答"Cindy是Amy的儿媳"，与输入直接矛盾；(b)外在幻觉——问RLHF含义时，LLM凭空编造其代表"Rights, Limitations, Harms, and Freedoms"（实为Reinforcement Learning from Human Feedback）。原文借此定性论证：幻觉在GPT-4等顶级LLM中仍频发，且模型难以自识别已生成的幻觉内容。该图作为现象级案例证据，铺垫后文对幻觉分类（内在/外在）、检测与缓解方法的系统综述，是论述"可靠性挑战"这一关键议题的视觉锚点。

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.8) ⭐深度解读
![[assets/crops/a-survey-of-large-language-models-tab01.png]]
> [!quote] caption
> Statistics of large language models (having a size larger than 10B in this survey) in recent years, including the capacity evaluation, pre-training data scale (either in the number of tokens or storage size) and hardware resource costs. In this table, we only include LLMs with a public paper about t

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 1 联合解读**

**1) 核心对象与结构**：该表统计了 50 余款参数量 >10B 的 LLM，按"公开可用"与"闭源"两类纵列排列，横向涵盖 9 项指标：发布时间、参数量（B）、基模型、IT/RLHF 适配、预训练数据量、最新数据时间戳、硬件（GPU/TPU）、训练时长，以及 ICL/CoT 评测。量化上，参数量跨度 10B–1200B（GLaM），训练 token 从 100B 扩展到 3.2T（Skywork），算力从单卡到 6144 TPU v4（PaLM）。

**2) 关键技术结论**：① LLM 体量与训练数据持续增长，Chinchilla 后数据-参数比例更受重视；② IT 与 RLHF 自 2022 年起成为适配主流（InstructGPT、ChatGLM、Baichuan2 等）；③ ICL 已成标配，CoT 能力自 2022 年（UL2、PaLM）起逐步纳入评测；④ 开源/闭源并行发展，开源阵营在 2023 年迅速崛起（LLaMA 系列、Qwen、Baichuan2）。

**3) 论文作用**：作为定量基线，支撑后续章节对 LLM 演进时间线、能力评估与训练范式的纵向对比，奠定全文分类讨论的事实依据。

### Table 2 (p.13) ⭐深度解读
![[assets/crops/a-survey-of-large-language-models-tab02.png]]
> [!quote] caption
> Statistics of commonly-used data sources.

> [!tip] 表格解读（多模态）
> 【图文联合解读】表2以“语料库—规模—来源—更新时间”统计12种常用数据：BookCorpus为5 GB；C4 800 GB、CC‑Stories‑R 31 GB、CC‑NEWS 78 GB、REALNEWS 120 GB，均来自CommonCrawl；OpenWebText 38 GB、Pushshift.io 2 TB源于Reddit链接；Wikipedia 21 GB；Pile 800 GB、ROOTS 1.6 TB，更新时间横跨2015—2023年。表2说明大模型预训练依赖多源、TB级数据，覆盖面、清洗、配比与时效性至关重要；它是后续数据处理与训练讨论的资源底座，并非单项实验结果。

### Table 3 (p.14) ⭐深度解读
![[assets/crops/a-survey-of-large-language-models-tab03.png]]
> [!quote] caption
> A detailed list of available collections for instruc- tion tuning.

> [!tip] 表格解读（多模态）
> 【图文联合解读】Table 3 汇总了 17 个指令微调数据集，按"任务/对话/合成"三类列出名称、发布时间与样本量。**任务类**规模最大：xP3(81M)、OIG(43M)、MVPCorpus(41M)、Super-Nat.Inst(5M)；**对话类**多在万~十万级，如 OpenAssistant(161K)、HH-RLHF(160K)、ShareGPT(90K)；**合成类**以 BELLE(1.5M)、Guanaco(535K)领先。数据呈"来源多元、规模跨度大(15K–81M)、2023 年集中涌现"特征，支撑论文"指令数据来源广泛、规模与质量并重"的核心论点，并为第 4.1.2 节"指令质量改进与选择"提供分类基线与方法选型依据。

### Table 4 (p.14) ⭐深度解读
![[assets/crops/a-survey-of-large-language-models-tab04.png]]
> [!quote] caption
> A list of available collections for alignment.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

表4枚举2021–2023年三类对齐数据：Task类7个（最大P3/xP3达12.1M/81M条）、Chat类5个（HH-RLHF 160K、OpenAssistant 161K等）、Synthetic类5个（Alpaca 52K、Guanaco 535K、BELLE 1.5M）。原文借此论证三点：(1)对齐数据规模与形态两年内迅速扩张，从任务级百万条演进到对话与合成指令；(2)三类数据呈互补——任务数据支撑泛化，对话数据驱动交互，合成数据降低标注成本；(3)在论文"对齐技术"章节中作为资源地图，为RLHF、指令微调等方法提供可复用数据基础。

### Table 5 (p.23) ⭐深度解读
![[assets/crops/a-survey-of-large-language-models-tab05.png]]
> [!quote] caption
> Model cards of several selected LLMs with public configuration details. Here, PE denotes position embedding, #L denotes the number of layers, #H denotes the number of attention heads, d model denotes the size of hidden states, and MCL denotes the maximum context length during training.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**说明**：所提供图片实际为论文正文段落（涉及 Prefix Decoder、Mamba、RWKV、RetNet 等架构变体），并非 Table 5 表格本体，故图像无法直接辨认，仅依据 caption 解读如下：

该表以"模型卡片"形式罗列 GPT-2/3、PaLM、LLaMA、OPT、BLOOM、CodeGen 等主流 LLM 的公开配置，量化呈现 PE（位置编码）、#L（层数）、#H（头数）、d_model（隐藏维度）与 MCL（训练上下文长度）等超参。例如 LLaMA-13B 为 #L=40、#H=40、d_model=5120、MCL=2048；GPT-3 175B 则达 #L=96、#H=96、d_model=12288。

文中借此佐证两条关键技术结论：①主流 LLM 多采用 Decoder-only 架构并共享基本配置范式；②模型差异主要体现在规模伸缩（层数、隐藏维、上下文窗口）上，体现"扩展定律"驱动的设计思路。

在论文整体论证链中，该表承担"实证支撑"职能：衔接前文架构分类（Transformer 与替代架构）与后文预训练/适配讨论，为读者提供具体量化基准，便于横向对比各家族模型的技术取向与规模差异。

### Table 6 (p.23) ⭐深度解读
![[assets/crops/a-survey-of-large-language-models-tab06.png]]
> [!quote] caption
> Comparison of parallelism and complexity of dif- ferent models. T represents sequence length, H represents the dimension of the input representation, N represents the dimension after compression in SSMs, and M represents the number of layers in each Hyena module.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**表6核心**：量化对比6种模型在序列长度T、表征维度H、SSM压缩维度N、Hyena模块层数M下的解码与训练复杂度。

**数据要点**：
- Transformer：解码 O(H(T+H))，训练 O(TH(T+H))，对T呈二次方
- SSM/Mamba：解码 O(H(N²+H))，与T无关
- RWKV/RetNet：解码/训练分别为 O(H²)、O(TH²)，完全常数
- Hyena：解码 O(MH(T+H))，含M层堆叠开销

**论证结论**：Transformer训练对序列长度T为二次方，长序列存在效率瓶颈；SSM家族利用压缩维度N实现O(1)解码；RWKV与RetNet达最优常数复杂度；Hyena以M层模块换取并行训练能力，证明非Transformer架构在并行性与复杂度上均可超越Transformer。

**论文作用**：位于第4.2.1节"Emergent Architectures"，为Mamba、RWKV、RetNet、Hyena等新兴架构替代Transformer提供量化的复杂度依据，支撑论文"SSM等架构可突破二次方瓶颈"的核心技术观点。

### Table 7 (p.24) ⭐深度解读
![[assets/crops/a-survey-of-large-language-models-tab07.png]]
> [!quote] caption
> Detailed formulations for the network configurations. Here, Sublayer denotes a FFN or a self-attention module in a Transformer layer, d denotes the size of hidden states, p i denotes position embedding at position i , A ij denotes the attention score between a query and a key, r i − j denotes a lear

> [!tip] 表格解读（多模态）
> 【图文联合解读】表7以Transformer子层为核心，归纳3类配置：归一化位置3种（Post/Pre/Sandwich Norm）、归一化方法3种（LayerNorm、RMSNorm、DeepNorm）、激活函数5种（ReLU、GeLU、Swish、SwiGLU、GeGLU），并给出残差顺序、统计量及门控公式，d为隐藏维数。原文说明：归一化位置与残差缩放影响深层网络训练稳定性，门控激活影响表达效率，Pre-Norm、DeepNorm及GLU类适于深网。该表是统一“架构配置词典”，支撑后文比较模型深度、稳定性和能力，并非独立实验结果。

### Table 8 (p.29) ⭐深度解读
![[assets/crops/a-survey-of-large-language-models-tab08.png]]
> [!quote] caption
> Detailed optimization settings of several existing LLMs.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读**

该表横向对比17个主流LLM（GPT-3、PaLM、LLaMA 2、Falcon、PanGu-Σ等）在9项优化配置上的实践：批量大小、初始与峰值学习率、warmup、衰减方式、优化器、精度类型、权重衰减、梯度裁剪与Dropout。

**关键结论**：①批量调度已成共识，多模型采用训练中逐步增大策略（如GPT-3 32K→3.2M、MT-NLG 64K→3.75M、Chinchilla 1.5M→3M）；②学习率跨度近三个数量级（7×10⁻⁶–1×10⁻²），与模型规模无单调关系；③"AdamW+cosine decay至10%+warmup"为主流范式；④BF16/FP16低精度训练为标配；⑤PaLM/T5使用Adafactor+inverse square root代表另一支路线，表明不存在统一最优配方。

**论文作用**：为第4章预训练优化的方法学总结提供量化实证，揭示工业界实践的多样性与共性，指导后续LLM工程设计决策。

### Table 9 (p.33) ⭐深度解读
![[assets/crops/a-survey-of-large-language-models-tab09.png]]
> [!quote] caption
> Basic statistics of the required number of GPUs, tuning time, batch size (denoted as BS) per device (full tuning and LoRA tuning), and inference rate (the number of generated tokes per second). Our experiments are conducted based on two Linux servers having 8 A800-80G SXM4 GPUs with 6 NVSwitch and 8

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 9 图文联合解读**

**核心数据**：表格对比 LLaMA 7B/13B/30B/65B 四种规模在 A800 全量微调、A800 LoRA 微调、A800/3090 推理（16-bit 与 8-bit）下的 GPU 数量、batch size、调参耗时及生成速率（tokens/s）。

**关键结论**：（1）全量微调所需 GPU 随模型规模线性增长（7B 用 2 卡→65B 用 16 卡），而 LoRA 仅需 1 张 80G 卡即可完成全部规模调优，但 65B 耗时飙升至 60.6h；（2）推理速率随模型增大急剧下降（A800-16bit：36.6→8.8 tokens/s），8-bit 量化进一步使速率腰斩；（3）3090 推理明显慢于 A800，量化后差距更显著。

**论文作用**：以实测数据支撑"参数高效微调（LoRA）显著降低资源门槛"的论点，为后续讨论 PEFT 与部署成本提供量化依据。

### Table 10 (p.35) ⭐深度解读
![[assets/crops/a-survey-of-large-language-models-tab10.png]]
> [!quote] caption
> Results of instruction-tuning experiments (all in a single-turn conversation) based on the LLaMA (7B) and LLaMA (13B) model under the chat and QA setting. We employ four instruction improvement strategies on the Self- Instruct-52K dataset, i.e., enhancing the complexity ( w/ complexity ), increasing

> [!tip] 表格解读（多模态）
> 【图文联合解读】**说明：所提供的图片并非 Table 10 本身，而是论文第 5.1.4 节"Empirical Analysis for Instruction Tuning"及其前后相关文字段落（含 Domain Specialization 与 Improvement Strategies 的论述），表格数据并未在图像中呈现，因此仅能依据原文 caption 与可见正文进行解读。**

**联合解读：**

1) **核心对象与结构**：Table 10 报告在 LLaMA-7B 与 LLaMA-13B 上、Chat 与 QA 两种单轮场景下，以 Self-Instruct-52K 为基础数据集，依次叠加四种指令改进策略（增强复杂度 w/ complexity、增加主题多样性、增加指令数量、平衡难度 Easy-to-Hard 等）后的指令微调结果，是一张多策略消融对比表。

2) **关键论证结论**：原文 Section 5.1.4 强调合成指令存在"主题多样性差、难度不均（过易或过难）"的问题；Table 10 通过逐项叠加改进策略，定量验证**提升复杂度（如 WizardLM-70K 的约束/推理步扩展）**和**提升多样性（如 ChatGPT 重写至 293 主题得 70K 指令）**能持续改善下游表现，证明"数据质量改进"比单纯堆量更有效。

3) **在论文中的作用**：该表是综述第 5 章"Instruction Tuning"经验分析的核心实证支撑，把方法论综述（如何改进合成指令）与可复现实验（LLaMA 系列）连接起来，为后续讨论指令数据规模、多样性与难度平衡提供了量化证据链。

### Table 11 (p.45) ⭐深度解读
![[assets/crops/a-survey-of-large-language-models-tab11.png]]
> [!quote] caption
> Typical LLM utilization methods and their key points for ICL, CoT, and planning. Note that the key points only highlight the most important technical contribution.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

图片仅显示表头三列（Approach / Representative Work / Key Point）与 caption，**未呈现具体数据行内容**，故无法逐条列举各方法细节，仅能依据表头结构与原文定位解读。

该表归属论文第 45 页附近，归纳 LLM 三类典型"调用侧"使用范式：

1. **ICL（上下文学习）**：聚焦示范示例（demonstration）的选取与排序设计；
2. **CoT（思维链）**：聚焦中间推理步骤的激发与一致性聚合（如自洽性、思维树等）；
3. **Planning（规划）**：聚焦任务分解、子目标生成与多步计划执行。

每条记录以 "代表工作 + 单一最关键技术贡献" 形式呈现，强调"做了什么、亮点在哪"。

**在论文链路中的作用**：与前述偏训练侧的方法表（如 Table 10 的预训练/微调）形成互补——前者回答"LLM 怎么训出来"，本表回答"训好后怎么用"。二者共同构成"训练—利用"完整图景，为读者快速索引 prompting 与推理增强技术提供对照表。

### Table 12 (p.47) ⭐深度解读
![[assets/crops/a-survey-of-large-language-models-tab12.png]]
> [!quote] caption
> A collection of useful tips for designing prompts that are collected from online notes [446–449] and experiences from our authors, where we also show the related ingredients and principles (introduced in Section 6.1.1). We abbreviate principles as Prin. and list the IDs of the related principles for

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 12 图文联合解读**

**1) 核心对象与结构**：表格按"Ingredient（成分）—Collected Prompts（收集的提示技巧）—Prin.（关联原则编号）"三列组织，列举LLM提示设计实用技巧。已可见部分以"Task Description（任务描述）"为成分项，收录T1（提示应尽可能详尽，举例"50词内概括文章，保留主线与结论"）和T2（用前缀提示让LLM扮演专家角色，如"你是…领域资深专家"），均对应原则①（清晰表达任务目标）。

**2) 论证的关键结论**：作者通过该表将零散的提示工程经验系统化，建立"成分—原则"映射，证明有效的提示设计需围绕四大原则（①清晰目标、②分解子任务、③少样本示范、④模型友好格式）展开。

**3) 在论文中的作用**：作为第6.1.1节提示设计原则的实例化补充，连接理论原则与实操技巧，为读者提供可复用的prompt模板库。

### Table 13 (p.48) ⭐深度解读
![[assets/crops/a-survey-of-large-language-models-tab13.png]]
> [!quote] caption
> Example instructions collected from [447, 457]. The blue text denotes the task description, the red text denotes the contextual information, the green text denotes the demonstrations, and the gold text denotes the prompt style.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 13 图文联合解读**

Table 13 以四色编码拆解一条指令样本的结构组成：蓝色任务描述（指令模型"据三引号文章作答，未找到则输出 I could not find an answer"）、红色上下文（球员 Joao Moutinho 的背景文章）、绿色示范（含"Let's think step by step"的 CoT 式 Q–A 对，并以省略号代表更多示例）、金色提示风格，末尾附填空模板。

原文借此实例说明指令调优数据的标准四要素——任务描述、上下文、上下文学习示例与思维链风格——且样本源自 [447,457] 等外部指令集合，可作为额外训练信号扩充数据多样性。

该表在论文方法链中起实证锚点作用：支撑"指令调优通过整合异构任务与多源数据集，能显著提升模型零样本与跨任务泛化能力"这一核心技术结论，是连接第三章指令微调方法论述与后续能力评估实验的关键可视化样例。

### Table 14 (p.57) ⭐深度解读
![[assets/crops/a-survey-of-large-language-models-tab14.png]]
> [!quote] caption
> Representative basic and advanced abilities and corresponding representative datasets for evaluating.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 14 图文联合解读**

该表以"Level→Ability→Task→Dataset"四级结构系统梳理 LLM 评估体系，共 2 个 Level（Basic、Advanced）、6 个 Ability、19 个 Task，列举逾百个基准数据集（如 LAMBADA [252]、HumanEval [105]、MATH [362]、GSM8k [198]、TruthfulQA [558] 等）。

原文借此论证两条关键技术结论：① LLM 评估需分基本与高级两层次——基础侧重语言生成、知识利用与复杂推理（符号/数学），高级聚焦人本对齐（3H）、外部环境交互（家厨/网页/开放世界）与工具调用（5 类接口）；② 各能力拥有对应的代表性基准族（如 HumanEval/CodeContest 表代码合成，HotpotQA 表多跳推理，VirtualHome/ALFWorld 表具身智能）。

此表充当论文评估章节的"导航图"，串联后续能力评测、模型对比与方法讨论，为读者构建统一可比的 LLM 多维评估坐标系。

### Table 15 (p.64) ⭐深度解读
![[assets/crops/a-survey-of-large-language-models-tab15.png]]
> [!quote] caption
> A category of existing evaluation work.

> [!tip] 表格解读（多模态）
> 【图文联合解读】Table 15 以"方法×评估基准×模型类型×能力域×数据源"五维结构梳理现有LLM评估工作：方法分为Benchmark（25项，含MMLU/HELM/AGIEval等通用集，及KoLA/AgentBench/ToolBench等专项）、Human（Chatbot Arena、SciBench）、Model（AlpacaEval、MT-bench、TrustGPT、ChatEval）三类；能力覆盖General、知识利用、复杂推理、工具操控、环境交互、人类对齐、鲁棒性、代码合成、医疗/金融/法律等；数据源自人类考试标注、基准集合、网络爬取、合成生成四类。

作者借此论证三点结论：①LLM评估无单一银弹；②Benchmark量化全面但可能饱和/受污染，Human贴近真实偏好但成本高，Model可大规模但存偏差，三者互补；③能力评估需匹配模型类型（Base/Fine-tuned/Specialized）。该表衔接§7.1–7.2的能力定义与§7.3.2的方法优缺点讨论，是评估体系的结构化枢纽索引。

### Table 16 (p.67) ⭐深度解读
![[assets/crops/a-survey-of-large-language-models-tab16.png]]
> [!quote] caption
> Evaluation on the eight abilities of LLMs with specially selected tasks. The shade of the Orange and Blue fonts denote the performance orders of the results in closed-source and open-source models, respectively. This table will be continuously updated by incorporating the results of more models.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 16 图文联合解读**

**① 核心对象与结构**：该表对 LLMs 的**八项关键能力**进行专项任务评测。表头显示明确的分类框架：上半部「Language Generation」能力组下设 LRD、WMT、XSum、HumanEval 四子任务；下半部「Knowledge Utilization」能力组下设 TriviaQA、NaturalQ、WebQ、ARC、WikiFact 五子任务（图中仅可辨识表头与分类行，具体模型得分数据未在截图中呈现）。橙色/蓝色字体分别标记闭源、开源模型的性能排名。

**② 关键论证结论**：通过闭源 vs. 开源模型在同一基准上的并排量化对比，原文用以揭示两类生态在**语言生成精度**与**知识调用广度**上的相对优劣差距，支持"开源模型正在快速追赶闭源 SOTA"的论断。

**③ 在论文链路中的作用**：作为第 67 页能力评测实验的核心对照表，与 Figure 16（任务规划范式）形成「能力–应用」互补，串联起综述方法论中的**评估章节**，为后续能力短板讨论提供数据锚点。

### Table 17 (p.68) ⭐深度解读
![[assets/crops/a-survey-of-large-language-models-tab17.png]]
> [!quote] caption
> Prompt examples and their performance of ChatGPT on representative tasks. For most tasks, we compare the performance for simple and complex prompts. We also present the reported performance of supervised methods. “LG”, “KU”, “CR”, “SDG”, “IR” are short for “language generation”, “knowledge utilizati

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

**1）核心对象与数据：** 该表按"任务-数据集-指令-ChatGPT-有监督方法"五列组织，覆盖语言生成、知识利用、复杂推理、结构化数据生成、信息检索五类任务，对比简单提示与复杂提示的效果。可见的"翻译/WMT"行：简单提示"请将英语译为捷克语"得20.66，复杂提示（含角色扮演与上下文要求）得21.12，而有监督方法高达41.40[741]。

**2）关键结论：** 复杂提示在同任务上略优于简单提示（21.12>20.66），验证提示工程有效性；但ChatGPT成绩仍仅为有监督方法的一半左右，说明通用LLM通过提示远未达到专用监督模型水平，存在明显能力差距。

**3）论文作用：** 该表为综述提供量化实证，支撑"提示设计重要但LLM在多数任务上仍逊于监督方法"的判断，是讨论LLM能力边界与提示策略章节的关键经验性证据。

### Table 18 (p.82) ⭐深度解读
![[assets/crops/a-survey-of-large-language-models-tab18.png]]
> [!quote] caption
> The activation memory consumption of each computation within the LLaMA model based on research work [976]. We denote batch size by B , sequence length by T , the vocabulary size by V , the number of head in the attention module by N , the dimension of each head by D , the hidden size by H ( H = ND )

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

该表将 LLaMA 前向各步的**激活显存**按 B/T/H/N/V/H' 等参数逐层量化（公式①–⑨）。核心数据揭示三点：① 多数线性映射（Q/K/V、O、FFN 门控）需存 2BTH；② 注意力 softmax 产生 2BT²N，**随序列长度 T 二次增长**，是长上下文的主要瓶颈；③ FFN 中间态 D 占 4BTH'，因 H'≫H，往往是单层最大开销。各步结果再乘以层数 L 即得总量。

该表为论文**系统效率章节**提供显存分解依据，直接支撑 FlashAttention（避免存完整注意力矩阵）、激活重计算等优化技术的论证，是连接模型结构与训练/推理效率的关键桥梁。

### Table 19 (p.84) ⭐深度解读
![[assets/crops/a-survey-of-large-language-models-tab19.png]]
> [!quote] caption
> The computation, data transfer, and arithmetic intensity during the prefill stage. We use the asymptotic notation O to denote the complexity of data transfer amount, where the constant factor of the complexity is related to the specific implementation method. Table source: [983].

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

**1) 核心数据：** 表列出prefill阶段9个算子（Q/K/V投影、RoPE、Attention、输出投影、Add&Norm、门控G/U、Swish·U、下投影）的FLOPs、数据传输复杂度与算术强度AI。如Attention计算量为4BT²ND+4BT²N、传输为O(BT²N+BTND)；Q/K/V投影计算6BTH²、传输O(BTH+H²)。

**2) 关键结论：** RoPE、Swish等element-wise算子AI=O(1)；MatMul算子AI较低（如投影为O(1/(1/H+1/BT))），属memory-bound；Attention因T²二次项，AI显著更高，属compute-bound，揭示各算子的硬件瓶颈差异。

**3) 链路作用：** 为prefill阶段的算子融合、FlashAttention等优化策略提供roofline级别的量化依据。

### Table 20 (p.84) ⭐深度解读
![[assets/crops/a-survey-of-large-language-models-tab20.png]]
> [!quote] caption
> The computation, data transfer, and arithmetic intensity during the decoding stage. Table source: [983].

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 20 图文联合解读**

该表逐项量化Transformer解码阶段9步操作的FLOPs、数据传输量与算术强度：①Q/K/V投影(6BTH²)、②RoPE(6BTH)、③Attention(4BT²ND+4BT²N，计算量最大)、④输出投影(2BTH²)、⑤⑨Add&Norm(5BTH)、⑥门控上投影(4BTHH')、⑦Swish乘(2BTH')、⑧下投影(2BTHH')；其数据传输量为O(BTH+H²)等量级，矩阵乘类操作算术强度统一为O(1/(1/H+1/BT))，②⑦为O(1)。

**技术结论**：解码阶段各核心运算算术强度均极低，呈明显memory-bound特征，显存读写是性能瓶颈。

**论文作用**：为"高效推理"章节（如KV cache、量化、batch合并等优化讨论）提供量化依据，支撑"为何解码需特殊优化"的论证。

### Table 21 (p.88) ⭐深度解读
![[assets/crops/a-survey-of-large-language-models-tab21.png]]
> [!quote] caption
> Evaluation results for quantized LLaMA models (7B and 13B). We employ existing model checkpoints provided by [350] for quantization experiments, which have been fine-tuned on FLAN-v2, Alpaca-52K, and ShareGPT, respectively. Specifically, we report the performance with AlpacaFarm, MMLU, and BBH, as w

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

表21系统对比LLaMA-7B/13B在FLAN-v2、Alpaca-52K、ShareGPT三种SFT数据上，经bitsandbytes量化至16/8/4-bit后的AlpacaFarm、MMLU、BBH分数及显存占用。

核心结论：4-bit量化使显存由12.58→3.94 GiB（7B）、24.40→7.34 GiB（13B），压缩约3倍，而各项基准分数仅小幅下降（如13B-MMLU 51.67→50.48），说明低位宽量化在显著降低部署成本的同时基本保持能力。

论文作用：作为效率/部署章节的实证支撑，论证LLM量化是兼顾性能与资源开销的可行方案，为后续讨论推理优化提供定量依据。

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