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
> 【图文联合解读】**图文联合解读：**

**1）核心对象与结构：** 图中以时间轴串联GPT-1(2018.06)→GPT-2(2019.02)→GPT-3(2020.05)→Codex(2021.07)→GPT-3.5(2022.03)→GPT-4(2023.03)，并下挂两条虚线支链：一条经 code-davinci-002 → text-davinci-002（+instruction）→ text-davinci-003（+RLHF）→ gpt-3.5-turbo（+chat）；另一条延伸至GPT-4 Turbo与GPT-4 Turbo with vision(2023.09)。ChatGPT横跨GPT-3.5与GPT-4。

**2）关键论证结论：** GPT系列沿"decoder-only生成式预训练→规模化→上下文学习→代码专门化→指令微调→RLHF对齐→对话/多模态"路径演进，体现decoder-only架构与人类对齐技术是LLM能力跃迁的两大核心驱动力。

**3）论文中的作用：** 为综述提供GPT系发展时间锚点，作为代表性LLM案例支撑后续方法分类与能力分析。

### Figure 5 (p.12) ⭐深度解读
![[assets/crops/a-survey-of-large-language-models-fig05.png]]
*整页渲染: ![[assets/a-survey-of-large-language-models-p12.png]]*
> [!quote] caption
> Public API of LLMs. Instead of directly using the model copies, APIs provide a more convenient way for common users to use LLMs, without the need of running the model locally. As a representative interface for using LLMs, the APIs for the GPT-series models [46, 55, 66, 105] have been widely used for both academia and industry19.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**【图文联合解读·图5 LLaMA进化图】**

**1) 核心对象与结构：** 以LLaMA为根节点的有向进化图，共30+变体，按4类边演化——①红虚线"继续预训练"派生Chinese-LLaMA、BiLLa、Panda等中文化版本；②绿/蓝实线"模型/数据继承"对应指令微调，衍生Alpaca、Vicuna、BELLE、Ziya、Chinese-Alpaca等；③任务/领域适配支线（含图标分类：数学Goat、医疗ChatMed、法律Lawyer LLaMA、TaoLi等）+RLHF线（PKU-Beaver）；④虚线框内为多模态扩展（LLaVA、MiniGPT-4、OpenFlamingo、VisionLLM）。

**2) 关键论证：** 原图集中论证——开源LLaMA通过"继续预训练+指令微调+任务适配+多模态扩展"四条路径，在数月内引爆社区生态，验证了开源模型相对闭源在迭代速度与跨域扩散上的显著优势。

**3) 论文作用：** 作为开源生态爆炸式发展的具象证据，支撑全文核心论点"开源驱动LLM快速迭代与领域/模态扩散"，并串联方法论章节对指令微调、RLHF、领域适配、多模态技术的讨论。

### Figure 7 (p.18) ⭐深度解读
![[assets/crops/a-survey-of-large-language-models-fig07.png]]
*整页渲染: ![[assets/a-survey-of-large-language-models-p18.png]]*
> [!quote] caption
> Filtering and Selection. To remove low-quality data from the collected corpus, existing work generally adopts two ap- proaches, namely classifier-based and heuristic-based. The former approach trains a selection classifier based on high- quality texts and leverages it to identify and filter out low- quality data. Typically, these methods train a binary classi- fier using positive instances that ar

> [!tip] 技术解读（多模态）
> 【图文联合解读】图7展示LLM预训练前的**6阶段数据预处理流水线**：①原始语料（网页/书籍/代码等）→②过滤筛选（语言/度量/统计/关键词四类启发式规则）→③去重（句级、文档级、集合级）→④隐私脱敏（检测并移除PII）→⑤分词（SentencePiece、Byte-level BPE等）→⑥得到可直接喂入训练的token序列。

**原文论证**：高质量语料是预训练基础；过滤阶段采用分类器式与启发式两种互补策略，可显著降噪提质。

**论文作用**：作为数据准备章节的方法总览图，将文本采集到模型训练的全链路可视化，奠定后续分词、模型架构与训练策略论述的事实基础。

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
> 【图文联合解读】**图文联合解读：**

图13展示了四种参数高效微调（PEFT）方法的结构对比：

**(a) Adapter Tuning**：在每个Transformer层的MHA与FFN之后各插入一个瓶颈结构的Adapter模块（绿色），仅训练新增的小模块参数。

**(b) Prefix Tuning**：在每一层输入前拼接可训练前缀向量（红色），冻结原模型参数。

**(c) Prompt Tuning**：仅在输入层最前端添加可学习Prompt（黄色），不侵入各层结构，最轻量。

**(d) LoRA**：在权重矩阵旁并行低秩分解矩阵（W_up、W_down，橙色），推理时可合并。

**论证结论**：四种方法的核心思想一致——冻结预训练LLM绝大部分参数，仅微调极少量新增参数（Adapter、前缀、Prompt或低秩矩阵），即可适配下游任务。

**论文作用**：作为第43页"Parameter-Efficient Fine-Tuning"小节的核心图示，与Table 4的定量对比呼应，为后续章节讨论指令微调与RLHF的成本权衡提供方法论支撑，是LLM高效适配技术的总览入口。

### Figure 16 (p.54) ⭐深度解读
![[assets/crops/a-survey-of-large-language-models-fig16.png]]
*整页渲染: ![[assets/a-survey-of-large-language-models-p54.png]]*
> [!quote] caption
> In this paradigm, there are typically three components: task planner, plan executor, and environment36. Specifically, task planner, which is played by LLMs, aims to generate the whole plan to solve a target task. The plan can be presented in various forms, e.g., an action sequence in the form of natural language [432] or an executable program written in programming language [436]. The LLM-based ta

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读（Figure 16）：**

图示 **Planning Framework** 含三大核心组件——**Task Planner (LLM)**、**Plan Executor**、**Environment**，并附 Memory、Tool 两个辅助模块。流程为：Task→LLM 生成 Plan→Executor 输出 Action 作用于 Environment→Environment 经 Feedback 回传 Planner 触发 plan refine→最终输出 Result。底部按 **Internal(LLM 自身)** 与 **External(Human / World / Others)** 对组件分类。

原文据此论证：LLM 可作为 task planner，生成自然语言动作序列或可执行程序形式的多步整体方案，闭环反馈支持计划的迭代修正与泛化。

作用上，该图作为论文**规划范式的总纲（统一形式化框架）**，为后文具体方法（zero-shot / few-shot / CoT 规划、ReAct 等）提供一致的组件划分与交互参照。

### Figure 17 (p.59) ⭐深度解读
![[assets/crops/a-survey-of-large-language-models-fig17.png]]
*整页渲染: ![[assets/a-survey-of-large-language-models-p59.png]]*
> [!quote] caption
> Hallucination widely occurs in existing LLMs, even the most superior LLMs such as GPT-4 [46]. Furthermore, existing work shows that LLMs encounter difficulties in recognizing the hallucinated con- tent in text [604], even the powerful ChatGPT. Additionally, beyond language tasks, a recent study has shown that large vision-language models (LVLM) also face challenges with hallucination, i.e., genera

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读（图17）：**

该图以两组人机对话并排对比两类幻觉：**(a)内在幻觉**——输入"Bob之妻Amy、之女Cindy，谁是Cindy对Amy的关系？"，模型却答"Cindy是Amy的**daughter-in-law**（儿媳）"（红字标注），与输入直接矛盾，应为孙女关系；**(b)外在幻觉**——被问及"RLHF含义"时，模型将其臆造为"Rights, Limitations, Harms, and Freedoms"（红字），却正确解释了LLM，无中生有。

**论证结论：** 幻觉不仅在GPT-4等顶尖LLM中普遍发生，且模型自身难以识别文本中的幻觉内容。

**章节作用：** 作为第59页"幻觉挑战"小节的关键实证样例，与LVLM幻觉引用[604]共同支撑作者对可信度风险的定性论述，引导后续缓解策略章节。

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.8) ⭐深度解读
![[assets/crops/a-survey-of-large-language-models-tab01.png]]
> [!quote] caption
> Statistics of large language models (having a size larger than 10B in this survey) in recent years, including the capacity evaluation, pre-training data scale (either in the number of tokens or storage size) and hardware resource costs. In this table, we only include LLMs with a public paper about t

> [!tip] 表格解读（多模态）
> 【图文联合解读】该表汇总2019.10–2023.10间50余个>10B LLM，按公开/闭源两栏纵向排列，列出参数量（11B–1200B）、预训练数据（1T–3.2T tokens）、硬件（A100/A800、TPU v3/v4）、训练时长与ICL/CoT评估、IT与RLHF适配情况。原文借此论证三大趋势：①参数与数据双轨扩张（GLaM达1200B、Skywork达3.2T tokens）；②能力沿"基模型→IT→RLHF"逐级跃迁，GPT-4、LLaMA2、QWEN、Baichuan2同步具备IT+RLHF；③开源生态加速追赶。作为全文实证基础，该表支撑论文对LLM规模阈值（>10B）的界定、能力演进分类与发展阶段划分，为后续训练方法与涌现能力讨论提供量化锚点。

### Table 2 (p.13) ⭐深度解读
![[assets/crops/a-survey-of-large-language-models-tab02.png]]
> [!quote] caption
> Statistics of commonly-used data sources.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**联合解读：**

该表系统梳理了LLM预训练常用的12个公开数据集，结构为四列：数据集名称（含引用）、存储容量、数据来源、更新时间。量化层面：容量跨度从BookCorpus的5GB到Pushshift.io的2TB、ROOTS的1.6TB、the Pile与C4各800GB；来源构成上，CommonCrawl派生数据占4席（C4、CC-Stories-R、CC-NEWS、REALNEWs，共约1029GB），Reddit链接2席，Books、Wikipedia、Codes各1席，另有2个综合性语料。

原文以此论证三点关键技术结论：①预训练语料呈高度**多样化**（书、网页、百科、代码混合），避免单一分布偏差；②**CommonCrawl**是规模最大且最经济的原始数据池，但需经清洗方可使用（故C4、CC-NEWS等衍生集才进入主流）；③**时间新鲜度参差**（2015–2023）说明数据持续滚动更新，是LLM知识时效性的关键保障。

在论文整体链路中，该表位于"数据准备"章节，作为后续讨论清洗、去重、质量过滤、配比策略的事实依据与基准参考，支撑作者对数据工程是LLM训练核心瓶颈之一的论断。

### Table 3 (p.14) ⭐深度解读
![[assets/crops/a-survey-of-large-language-models-tab03.png]]
> [!quote] caption
> A detailed list of available collections for instruc- tion tuning.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 3 解读**

该表按 **Task / Chat / Synthetic** 三类汇总指令微调数据集：Task 类 7 个（含 FLAN 4.4M、xP3 81M、OIG 43M），Chat 类 5 个（ShareGPT 90K、OpenAssistant 161K），Synthetic 类 5 个（Alpaca 52K、Guanaco 535K、BELLE 1.5M），时间跨度从 2021.4 至 2023.4，并标注规模。

文中借此论证：① 指令数据已从早期任务型（如 Natural Instructions）演进为**对话型与自合成型**并存；② 数据规模与生成方式多样化，是指令微调与 RLHF 训练得以发展的关键基础设施。

该表是论文"指令微调"小节的数据支撑，为后文讨论指令质量筛选与 Self-Instruct 类方法提供具体基线与对比依据。

### Table 4 (p.14) ⭐深度解读
![[assets/crops/a-survey-of-large-language-models-tab04.png]]
> [!quote] caption
> A list of available collections for alignment.

> [!tip] 表格解读（多模态）
> 【图文联合解读】## 图文联合解读

**1）核心对象与结构**
表4罗列8个公开对齐数据集，按"数据集名—发布时间—样本量"三列组织。时间跨度从2020年9月（Summarize from Feedback，193K）至2023年10月（PKU-SafeRLHF，330K），约3年累计约1140万条偏好样本。规模差异悬殊：**Stack Exchange Preferences以10M独占鳌头（约占总量88%）**，WebGPT Comparisons仅19K为最末，多数数据集集中在10万–40万区间，体现问答（SHP、Stack Exchange）、对话（HH-RLHF）、安全（CValues、PKU-SafeRLHF）等多源异构特征。

**2）关键技术结论**
支撑原文"对齐数据已形成多样化生态"之判断：通用偏好、早期反馈、领域问答与中文安全对齐数据并存，为RLHF/DPO等方法提供充足训练燃料；同时揭示数据**长尾分布**——单一数据集（Stack Exchange）贡献近九成样本，提示后续研究需关注小样本、高质量对齐集的价值。

**3）在论文链路中的作用**
作为"对齐技术全景"章节的**基础设施盘点**，为后文对齐算法（PPO、DPO、RLAIF等）章节铺垫数据前提，体现"数据—算法—评估"的完整研究链条。

### Table 5 (p.23) ⭐深度解读
![[assets/crops/a-survey-of-large-language-models-tab05.png]]
> [!quote] caption
> Model cards of several selected LLMs with public configuration details. Here, PE denotes position embedding, #L denotes the number of layers, #H denotes the number of attention heads, d model denotes the size of hidden states, and MCL denotes the maximum context length during training.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读（说明：原文引用段落讲的是 Fig.5 公开 API/LLaMA 演化树，与 Table 5 无直接对应，故以下解读以表格内容为主）：**

表5横向对比15个公开LLM的核心架构配置：参数量跨越11B（T5）至540B（PaLM），层数24–118、隐藏维度1024–20480；除GLM-130B（前缀解码器）与T5（编码-解码器）外均为因果解码器。归一化以Pre LayerNorm为主流，PaLM/LLaMA/LLaMA2/Falcon/GLM均转向Pre RMSNorm；位置编码出现明显代际分化——早期GPT3/PanGU/OPT采用Learned，PaLM/LLaMA系列引入RoPE，BLOOM采用ALiBi；激活函数从GeLU向SwiGLU/GeGLU演进；训练上下文长度从2048（LLaMA2）扩展至4096。该表为论文论证"LLM架构逐步收敛于因果解码器+RoPE+RMSNorm+SwiGLU"的技术趋势提供量化基准，并支撑后续预训练、对齐、应用等章节的横向比较。

### Table 7 (p.24) ⭐深度解读
![[assets/crops/a-survey-of-large-language-models-tab07.png]]
> [!quote] caption
> Detailed formulations for the network configurations. Here, Sublayer denotes a FFN or a self-attention module in a Transformer layer, d denotes the size of hidden states, p i denotes position embedding at position i , A ij denotes the attention score between a query and a key, r i − j denotes a lear

> [!tip] 表格解读（多模态）
> 【图文联合解读】表7将Transformer配置拆为3组：3种归一化位置（Post/Pre/Sandwich）、3种归一化（LayerNorm、RMSNorm、DeepNorm）及5种激活（ReLU、GeLU、Swish、SwiGLU、GeGLU），并给出d维隐藏状态下的公式。它说明训练稳定性取决于归一化顺序与尺度，门控激活以双路乘积增强表达；表中用于统一比较主流LLM结构、支撑深层训练与性能分析，并非新实验结果。

### Table 8 (p.29) ⭐深度解读
![[assets/crops/a-survey-of-large-language-models-tab08.png]]
> [!quote] caption
> Detailed optimization settings of several existing LLMs.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 8 联合解读**

**核心对象与结构**：该表横向对比18个主流LLM（11B–1.085T参数）共9维优化配置——批量（32K→8.25M tokens）、学习率（7×10⁻⁶–1×10⁻²）、Warmup、衰减方式、优化器、精度（BF16/FP16）、权重衰减（多0.1）、梯度裁剪（多1.0）、Dropout。

**关键技术结论**：① **AdamW + 余弦衰减至10% + Warmup + BF16/FP16** 已成为LLM训练的事实标准配方；② PaLM/T5 采用 Adafactor 与反平方根衰减，形成差异化路线；③ PanGu-Σ 达 1.085T，刷新已公开模型参数规模上限；④ Dropout 在多数大模型中已弃用。

**论文作用**：作为第4章"预训练-模型优化"小节的实证基线，与 Fig.8（数据调度）、Table 5（数据来源）形成互补，共同构成完整的LLM预训练实践参考体系，为研究者复现或训练新模型提供可量化的工程基准。

### Table 11 (p.45) ⭐深度解读
![[assets/crops/a-survey-of-large-language-models-tab11.png]]
> [!quote] caption
> Typical LLM utilization methods and their key points for ICL, CoT, and planning. Note that the key points only highlight the most important technical contribution.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读**

图片仅显示表头三列（**Approach | Representative Work | Key Point**），行数据未呈现，故以下依据标题与上下文还原其内容。

1) **核心对象与结构**：该表纵向汇总LLM利用的三大范式——**ICL（In-Context Learning）、CoT（Chain-of-Thought）、Planning（规划）** 下各代表性工作的核心贡献，按"方法→代表工作→技术要点"三栏对照呈现，每行仅聚焦最关键的技术贡献。

2) **论证的关键结论**：三者在任务粒度上呈递进关系——ICL凭借少量示例激发能力、CoT引入中间推理步骤提升复杂推理、Planning进一步扩展至任务分解、子目标生成与多步决策，证明**LLM无需微调即可通过不同利用范式求解复杂任务**。

3) **在论文中的作用**：作为综述章节的**方法谱系索引表**，串联前文分述的ICL、CoT、Planning三条技术线，为读者提供一站式概览，呼应论文"如何高效利用LLM"这一贯穿全篇的核心议题。

### Table 12 (p.47) ⭐深度解读
![[assets/crops/a-survey-of-large-language-models-tab12.png]]
> [!quote] caption
> A collection of useful tips for designing prompts that are collected from online notes [446–449] and experiences from our authors, where we also show the related ingredients and principles (introduced in Section 6.1.1). We abbreviate principles as Prin. and list the IDs of the related principles for

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

该表汇总15条Prompt设计技巧，按4类成分组织：任务描述（T1–T4，均对应原则①）、输入数据（I1–I2，对应④）、上下文信息（C1–C4，C2对应①，其余对应②）、示范示例（D1–D5，主对应③），并标注对应原则①–④（明确目标、分解子任务、少样示范、模型友好格式）。

关键结论：作者将零散工程经验归纳为"**成分 × 原则**"二维框架，证明第6.1.1节提出的四大提示原则在每一类成分中均有具体落地映射（如"详尽描述→①"、"step-by-step→②"、"检索相关文档→④"、"格式规范示例→③"）。

作用：作为第6章Prompt工程的方法论支撑表，为后续具体提示技术（CoT、检索增强、专家角色、多轮分解等）提供可复用的操作清单，连接抽象原则与实践应用。

### Table 14 (p.57) ⭐深度解读
![[assets/crops/a-survey-of-large-language-models-tab14.png]]
> [!quote] caption
> Representative basic and advanced abilities and corresponding representative datasets for evaluating.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 14 图文联合解读：**

该表以两层结构（Basic/Advanced）系统罗列LLM评估能力与代表数据集。**Basic层**涵盖4大类：语言生成（含语言建模、条件生成、代码合成，对应Penn Treebank、HumanEval、APPS等）、知识利用（闭/开卷QA、知识补全，涉及Natural Questions、ARC、WikiFact等）、复杂推理（知识推理如HotpotQA、符号推理如CoinFlip、数学推理如GSM8k/MATH/MiniF2F），共约15项任务。**Advanced层**包含人对齐（Honesty/Helpfulness/Harmlessness）、外部环境交互（家庭、网站、开放世界）和工具调用（搜索引擎、代码执行、计算器）。

**技术结论**：论文借此论证LLM评估已从单一语言建模扩展至对齐、具身、工具使用等高阶智能，标志评估范式从"语言模型"向"通用智能体"演进。

**方法作用**：作为评估章节的索引式总览，为后续模型横向对比与局限性分析提供统一分类框架。

### Table 16 (p.67) ⭐深度解读
![[assets/crops/a-survey-of-large-language-models-tab16.png]]
> [!quote] caption
> Evaluation on the eight abilities of LLMs with specially selected tasks. The shade of the Orange and Blue fonts denote the performance orders of the results in closed-source and open-source models, respectively. This table will be continuously updated by incorporating the results of more models.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 16 图文联合解读：**

1）该表横向覆盖 8 大能力（语言生成、知识利用、推理、对齐、工具操作等），用专门任务（LBD、HumanEval、GSM8k、MATH、Gorilla 等）得分衡量；纵向对比 5 个闭源（橙色）与 9 个开源（蓝色）模型，色深代表排名。例如 ChatGPT 在 HumanEval 达 79.88、LBD 55.81，Claude 2 在 GSM8k 高达 82.87、Davinci003 在 LBD 最高 69.98，而 Vicuna-13B 在 MATH 仅 3.72、ALFW 仅 8.96。

2）关键结论：闭源整体领先，开源在对话微调后（如 LLaMA 2-Chat 对比 LLaMA 2）能力提升明显，但数学推理与环境交互仍是开源短板。

3）该表作为论文实验评估的"全景图"，支撑"LLM 能力可被任务化、可被开源追赶但仍有结构性差距"的核心论断。

### Table 17 (p.68) ⭐深度解读
![[assets/crops/a-survey-of-large-language-models-tab17.png]]
> [!quote] caption
> Prompt examples and their performance of ChatGPT on representative tasks. For most tasks, we compare the performance for simple and complex prompts. We also present the reported performance of supervised methods. “LG”, “KU”, “CR”, “SDG”, “IR” are short for “language generation”, “knowledge utilizati

> [!tip] 表格解读（多模态）
> 【图文联合解读】该表（截取片段）展示**翻译任务**（LG类）在WMT集上ChatGPT表现：简单提示得分20.66，加入"语义一致性"约束与格式化指令的复杂提示得分21.12，而监督方法高达41.40。原文借此论证两点：①**复杂prompt带来的增益极小**（仅+0.46 BLEU），提示工程的边际收益有限；②**ChatGPT在五大代表任务上仍显著落后于监督基线**，凸显通用LLM与任务专用模型之间的能力鸿沟。作为实验链路的一环，该表以统一框架量化ChatGPT零样本能力边界，为后文关于prompt敏感性、能力短板及与微调模型对比的讨论提供实证支撑。

### Table 18 (p.82) ⭐深度解读
![[assets/crops/a-survey-of-large-language-models-tab18.png]]
> [!quote] caption
> The activation memory consumption of each computation within the LLaMA model based on research work [976]. We denote batch size by B , sequence length by T , the vocabulary size by V , the number of head in the attention module by N , the dimension of each head by D , the hidden size by H ( H = ND )

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图像说明**：图片为论文正文段落（含 TABLE 18 caption 文字），未呈现表格本体，故结合 caption 与引文联合解读。

**1) 核心对象与结构**：Table 18 逐项列出 LLaMA 单层内 10 个计算（①输入投影、②RoPE、③注意力的 QKV/softmax、④输出投影、⑤Add&Norm、⑥FFN gate/up、⑦SwiGLU 乘积、⑧下投影、⑨Add&Norm、⑩交叉熵 softmax）对应的激活显存公式，符号含 B、T、V、N、D、H=ND、H'；①–⑨ 需乘层数 L。给定 V=32000、L=32、H=4096、H'=11008、N=32，B=1、T=2048 时单设备激活即占约 16 GB。

**2) 关键结论**：激活显存随 B·T·H 线性放大，仅前向激活已逼近单卡容量上限，凸显训练 LLM 必须依赖激活重计算、检查点或并行切分等显存优化手段。

**3) 论文作用**：为"LLM 训练成本与系统级优化"章节提供量化依据，支撑后续对 ZeRO、tensor/pipeline 并行、FlashAttention 等技术的必要性论证。

### Table 19 (p.84) ⭐深度解读
![[assets/crops/a-survey-of-large-language-models-tab19.png]]
> [!quote] caption
> The computation, data transfer, and arithmetic intensity during the prefill stage. We use the asymptotic notation O to denote the complexity of data transfer amount, where the constant factor of the complexity is related to the specific implementation method. Table source: [983].

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 19 图文联合解读：**

Table 19 逐行量化预填充（prefill）阶段9步子操作：①④⑧线性投影计算量 O(BTH²)，算术强度高，属计算密集；③Attention 为 4BT²ND+4BT²N，序列长度 T 二次方主导，是预填充最大瓶颈；②RoPE 与 ⑦Swish 强度仅 O(1)，属内存受限，需算子融合优化。

该表为论文"预填充以计算为主、Attention 主导开销"这一核心论断提供量化依据，支撑 FlashAttention、算子融合、KV 压缩等高效推理方案的理论基础，贯穿推理效率优化章节。

### Table 20 (p.84) ⭐深度解读
![[assets/crops/a-survey-of-large-language-models-tab20.png]]
> [!quote] caption
> The computation, data transfer, and arithmetic intensity during the decoding stage. Table source: [983].

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读**

Table 20 量化了Transformer解码阶段9步操作：①Q/K/V投影（6BTH²）、②RoPE（6BTH）、③Attention（4B²T²ND+4B²T²N）、④输出投影（2BTH²）、⑤⑨Add&Norm（5BTH）、⑥门控上投影（4BTHH'）、⑦Swish乘（2BTH'）、⑧下投影（2BTHH'），逐一给出对应数据传输量及算术强度（多为O(1/(1/H+1/BT))量级）。

**技术结论**：解码阶段批B小、序列T短，H较大，使线性层算术强度被压至O(1/H+1/BT)，整体属访存密集型，算力利用率低，故优化重心在访存而非算力。

**论文作用**：作为roofline分析依据，为后续解码加速策略（KV-cache管理、算子融合、量化）提供量化理论支撑。

### Table 21 (p.88) ⭐深度解读
![[assets/crops/a-survey-of-large-language-models-tab21.png]]
> [!quote] caption
> Evaluation results for quantized LLaMA models (7B and 13B). We employ existing model checkpoints provided by [350] for quantization experiments, which have been fine-tuned on FLAN-v2, Alpaca-52K, and ShareGPT, respectively. Specifically, we report the performance with AlpacaFarm, MMLU, and BBH, as w

> [!tip] 表格解读（多模态）
> 【图文联合解读】**表格内容**：展示 LLaMA-7B/13B 在三种 SFT 数据（FLAN-v2、Alpaca-52K、ShareGPT）上经 bitsandbytes 量化至 16/8/4-bit 后，于 AlpacaFarm、MMLU、BBH 三项基准的得分与显存（GiB）。

**关键结论**：16→4 bit 量化使 7B 模型显存由 12.58 GiB 降至 3.94 GiB，13B 由 24.40 GiB 降至 7.34 GiB（压缩约 3–4 倍）；与此同时各基准分数几乎不损失（如 ShareGPT-7B AlpacaFarm 仅 72.05→70.31，MMLU 41.30→40.08）。证实低比特量化能以极小性能代价大幅降低部署内存。

**论文作用**：为综述中"模型量化与小型化部署"章节提供经验证据，支撑"量化是 LLM 落地可行路径"的核心论断。

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