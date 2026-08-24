---
paper_num: "21"
title: "KIMI-VL TECHNICAL REPORT"
authors: ""
date: "2025/4/10"
arxiv: "https://arxiv.org/abs/2504.07491"
pdf: "papers/kimi-vl-technical-report.pdf"
slug: "kimi-vl-technical-report"
tags: [multimodal]
---

# KIMI-VL TECHNICAL REPORT

> [!abstract] 摘要（原文）
> 1\. 🚀 Kimi-VL 是一个高效的开源 MoE VLM，具备先进的多模态推理、长上下文理解和强大的 agent 能力，其语言解码器（Kimi-VL-A3B）仅激活2.8B参数，并结合了原生分辨率的 MoonViT 视觉编码器。 2. 🏆 该模型在 OSWorld、大学级图像/视频理解、OCR 和数学推理等挑战性任务上表现出色，有效竞争并超越了 GPT-4o-mini、Qwen2.5-VL-7B 等前沿模型，且支持128K长上下文和超高分辨率视觉输入。 3. 💡 基于 Kimi-VL，Kimi-VL-Thinking-2506 通过长 CoT SFT 和 RL 进一步提升了长程推理能力，在 MMMU、MathVision 等基准测试中取得了突破性表现，以约3B激活参数重新定义了高效多模态思维模型的标准。

## 元信息
- **发表日期**: 2025/4/10
- **作者**: —
- **arXiv**: https://arxiv.org/abs/2504.07491
- **本地 PDF**: `papers/kimi-vl-technical-report.pdf`
- **页数**: 24

## 图表（原文 caption + 页码）

### Figure 1 (p.1) ⭐深度解读
![[assets/crops/kimi-vl-technical-report-fig01.png]]
*整页渲染: ![[assets/kimi-vl-technical-report-p01.png]]*
> [!quote] caption
> Comparison between Kimi-VL-Thinking-2506 and frontier open-source VLMs, including short-thinking VLMs (e.g. Gemma-3 series, Qwen2.5-VL series) and long-thinking VLMs (QVQ-72B/Max-Preview), on MathVision benchmark. Our model achieves strong multimodal reasoning with just 2.8B LLM activated parameters.

> [!tip] 技术解读（多模态）
> 【图文联合解读】图1为MathVision基准上的对比散点图（坐标轴标签与图例不可读）。可观察：深蓝星标位于左上最高位（推测Kimi-VL-Thinking-2506）、浅蓝星标次之（推测其轻量变体）；右上绿X标（推测QVQ-72B/Max-Preview）接近顶格；紫、灰虚线分别连接多枚圆点并随序列递增上行（推测Gemma-3与Qwen2.5-VL系列规模档位）；蓝、红圆点位于底部。该图论证关键结论：仅以2.8B激活参数的MoE轻量LLM，即在多模态数学推理上达到乃至逼近数十B级长思考VLM的水平，凸显稀疏激活架构的高效性。作为论文开篇"性能名片"，它先于Table 1的训练流程概览，构成"方法链路→实验结果"的入口性证据，强化"小参数、强推理"的整体叙事。

### Figure 2 (p.2) ⭐深度解读
![[assets/crops/kimi-vl-technical-report-fig02.png]]
*整页渲染: ![[assets/kimi-vl-technical-report-p02.png]]*
> [!quote] caption
> Highlights of Kimi-VL performance for a wide range of benchmarks like, general benchmarks (MMMU, MMBench), OCR (InfoVQA), multi-image (BLINK), long video (LongVideoBench, Video-MME), long document (MMLongBench-Doc), and agent (ScreenSpot-Pro and OSWorld). Detailed results are presented in Table 3. 1

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图2以八组柱状图横向对比Kimi-VL-A3B与Qwen2.5-VL-7B、DeepSeek-VL2、GPT-4o、GPT-4o-mini、Llama-3.2-11B-Instruct、Gemma-3-12B-IT在五大类共八项基准上的得分。具体表现：通用（MMMU 57、MMBench 83.1）、OCR（InfoVQA 83.2）、多图（BLINK 57.3）、长视频（LongVideoBench 64.5、Video-MME 67.8）、长文档（MMLongBench-Doc 35.1）、代理（ScreenSpot-Pro 34.5、OSWorld 8.2）上，Kimi-VL-A3B均处于领先或并列第一位置，尤其在长文档（MMLongBench-Doc领先GPT-4o约21分）和代理任务（OSWorld领先GPT-4o约3分）上优势显著。

**核心论证**：仅激活约3B参数的Kimi-VL-A3B以小模型之身全面超越或追平7B–12B开源模型，并在多数任务上反超参数量远大于自身的GPT-4o，验证了"高效MoE视觉语言架构"在保持推理成本优势的同时实现跨任务泛化的关键技术结论。

**论文作用**：该图是实验章节的"总览门面"，先于Table 3给出全局性能印象，用以支撑后续详细表格与消融研究，是论文展示方法竞争力与实用价值的核心证据。

### Figure 3 (p.3) ⭐深度解读
![[assets/crops/kimi-vl-technical-report-fig03.png]]
*整页渲染: ![[assets/kimi-vl-technical-report-p03.png]]*
> [!quote] caption
> The model architecture of Kimi-VL and Kimi-VL-Thinking, consisting of a MoonViT that allows native- resolution images, an MLP projector, and a Mixture-of-Experts (MoE) language decoder. 1) Kimi-VL is smart: it has comparable text ability against efficient pure-text LLMs; without long thinking, Kimi-VL is already competitive in multimodal reasoning and multi-turn agent benchmarks, e.g., MMMU, MathV

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读（Figure 3）：**

1) **核心结构**：图为 Kimi-VL 三段式架构——底部 **MoonViT** 以**原生分辨率**直接编码多种尺寸输入（小图 50×20px、细粒度图 1113×672px、长视频帧 480×270px、UI 截图 800×1731px、特殊长宽比 OCR 58px 条带），经 **MLP Projector** 映射后送入 **MoE 语言解码器**（Attention 层 + 含 Router 的 MoE FFN，区分 Non-shared Experts 与 Shared Experts，堆叠 ×N 层），最终输出带颜色的多模态 token 序列。

2) **论证结论**：MoonViT 原生分辨率处理避免了对超高分辨率图像（如 UI、OCR）强制 resize 造成的细节丢失；MoE 共享+非共享专家设计在保证文本/推理能力的同时控制激活参数，提升效率。

3) **论文作用**：作为方法论总纲图，支撑后续 Figure 2 的多基准结果（MMMU、InfoVQA、ScreenSpot-Pro 等），解释 Kimi-VL-Thinking 在多模态推理、长视频、文档、Agent 任务上竞争力的架构根基。

### Figure 4 (p.4) ⭐深度解读
![[assets/crops/kimi-vl-technical-report-fig04.png]]
*整页渲染: ![[assets/kimi-vl-technical-report-p04.png]]*
> [!quote] caption
> The pre-training stages of Kimi-VL consume a total of 4.4T tokens after text-only pre-training of its language model. To preserve text abilities, all stages that update the language model are joint training stages. preprocessing operations enable MoonViT to share the same core computation operators and optimization as a language model, such as the variable-length sequence attention mechanism suppo

> [!tip] 技术解读（多模态）
> 【图文联合解读】图示Kimi-VL预训练五阶段：纯文本5.2T、ViT训练2.0T→0.1T（CoCa-loss对齐LLM）、联合预训练1.4T（多模态≤40%渐进）、联合冷却0.6T（高质量+重warmup高LR）、联合长上下文0.3T（RoPE 50k→800k），后三阶段以"resumes LR scheduler"衔接。

论文用以论证：所有更新LM的阶段均做联合训练（joint training），通过渐进多模态比例、再warmup、长上下文扩展保留文本能力，避免纯视觉微调导致的语言能力退化。

论文作用：完整呈现方法论预训练框架，作为后文指令微调与Table 4多模态推理评测（MathVista、MMMU等）的方法基础。

### Figure 5 (p.6) ⭐深度解读
![[assets/crops/kimi-vl-technical-report-fig05.png]]
*整页渲染: ![[assets/kimi-vl-technical-report-p06.png]]*
> [!quote] caption
> The post-training stages of Kimi-VL and Kimi-VL-Thinking, including two stages of joint SFT in 32K and 128K context, and further long-CoT SFT and RL stages to activate and enhance long thinking abilities. to 800,000. The joint long-context stage is conducted in two sub-stages, where each one extends the model’s context length by four times. For data composition, we filter and upsample the ratio of

> [!tip] 技术解读（多模态）
> 【图文联合解读】该图展示Kimi-VL后训练三阶段流水线：①联合SFT阶段（文本+多模态数据，先32K后128K各1 epoch）产出Kimi-VL；②长CoT SFT阶段（引入规划、评估、反思、探索类长思维链数据）；③在线RL阶段（仅对答案奖励，含长度惩罚与难度控制）产出Kimi-VL-Thinking。原文借此论证：每阶段上下文4倍扩展以渐进建立长文本能力，并经长CoT SFT激活、RL增强推理思维，形成从基础VLM到思考型VLM的完整训练链路，支撑后文Table 5等推理基准的评测。

### Figure 6 (p.8) ⭐深度解读
![[assets/crops/kimi-vl-technical-report-fig06.png]]
*整页渲染: ![[assets/kimi-vl-technical-report-p08.png]]*
> [!quote] caption
> Manuscript reasoning visualization. Kimi-VL-Thinking demonstrates the ability to perform historical and scientific inference by analyzing handwritten manuscripts step by step. In this example, our model identifies the author as Albert Einstein based on handwriting style, content analysis, and language cues. It reasons that the manuscripts relate to gravitational field equations, consistent with Ei

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

该图左侧为用户指令"逐步推断手稿作者与内容"，右侧为Kimi-VL-Thinking的完整推理流程：先以千字级`<Think>`块分四步分析（纸张年代→公式变量→德语术语→作者风格），再输出结构化结论、Key Observations（字迹/内容/语言三条证据）与Final Answer，形成"证据→推理→结论"闭环，最终判定手稿为Einstein的引力场方程推导稿。

**论文论证结论：** 模型具备融合视觉（笔迹）、语义（公式内容）与语言线索（德语"Einheitsvektor"等）的多模态链式推理能力，输出可验证而非即答。

**论文定位：** 属"thinking with images"章节的定性案例，支撑Kimi-VL-Thinking在高阶历史/科学推理任务上优于纯生成式回答的核心卖点。

### Figure 7 (p.12) ⭐深度解读
![[assets/crops/kimi-vl-technical-report-fig07.png]]
*整页渲染: ![[assets/kimi-vl-technical-report-p12.png]]*
> [!quote] caption
> Kimi-VL exhibits strong visual reasoning capabilities by grounding visual content in spatial, contextual, and cultural knowledge. It accurately identifies matching urban locations based on structural and layout features, interprets scenes from video games like Cyberpunk 2077 using stylistic cues, and recognizes real-world landmarks such as the

> [!tip] 技术解读（多模态）
> 【图文联合解读】图7以3组指令-响应定性示例展示Kimi-VL视觉推理能力：①多图选择任务（4张候选城市子图中匹配Image1），依据建筑密度/圆顶结构判Image4胜出；②地标识别（多伦多Rogers Centre穹顶体育馆，并关联CN Tower城市天际线地标群）；③游戏场景判读（Cyberpunk 2077 Night City霓虹酒吧任务点）。用以论证Kimi-VL将视觉内容锚定于空间布局、上下文美术风格与文化知识三大维度，体现多模态推理链中从视觉感知到空间/文化综合判断的能力。在论文方法链路中，作为定性能力展示与定量benchmark互补，构成完整证据链，证明模型在跨域视觉理解任务上的泛化性。

### Figure 8 (p.13) ⭐深度解读
![[assets/crops/kimi-vl-technical-report-fig08.png]]
*整页渲染: ![[assets/kimi-vl-technical-report-p13.png]]*
> [!quote] caption
> Kimi-VL demonstrates its capability to perform symbolic reasoning and geometric inference by solving a circle geometry problem step by step. The model analyzes given conditions, applies geometric theorems such as the inscribed angle theorem and properties of triangle angles, and accurately derives the target angle. presented in visual contexts. On the more challenging MathVision benchmark, due to 

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图示为一道圆几何推理题：圆O中AB为直径，点C、D在圆上，∠D=62°，求∠ACO（选项A-D：26°/28°/30°/32°）。模型分三步求解：①由AB为直径推出∠ACB=90°（圆周角定理）；②由圆心角定理得∠AOC=2×62°=124°；③利用OA=OC构成等腰三角形，设∠ACO=x，列方程2x+124°=180°，解得x=28°，选B。

**技术结论：** 该例证明Kimi-VL具备链式符号推理能力，能识别视觉几何结构并调用圆周角/圆心角定理逐步推导。

**整体作用：** 作为定性案例，与定量评测（如MathVision基准）互证模型在视觉-数学跨模态推理任务上的有效性。

### Figure 9 (p.14) ⭐深度解读
![[assets/crops/kimi-vl-technical-report-fig09.png]]
*整页渲染: ![[assets/kimi-vl-technical-report-p14.png]]*
> [!quote] caption
> Diverse OCR visualization. Kimi-VL demonstrates strong OCR capabilities across varied content types, including structured financial tables, complex mathematical formulas, and handwritten Chinese text. The model accurately parses tabular data into markdown, converts formulas to LaTeX, and transcribes handwritten paragraphs with contextual understanding, showcasing its versatility in multimodal text

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

该图以三对"输入—输出"对照展示Kimi-VL的多场景OCR能力。**左列**为金融表格输入与多行Markdown表格输出（含列标题与数十行数值条目）；**中列**为手写公式图像与对应LaTeX源码，附"Rendered formula"渲染示意；**右列**为另一公式输入及完整LaTeX转写（含对齐环境`$$\begin{aligned}...$$`与多行变量结构）。

原文借此论证三点关键技术结论：(1) 模型能将结构化表格**无损映射**为语义化Markdown；(2) 能将含分数、上下标的复杂公式**精确转译**为可编译的LaTeX；(3) 能基于上下文**理解性转录**手写段落。

在论文链路中，该图作为**定性可视化证据**，与前文的定量OCR基准（精度、编辑距离等指标）互补，向评审者直观证明Kimi-VL在"金融—数学—手写"三类异构文本上的通用多模态文本提取与解释能力，是其相对纯语言OCR模型差异化优势的核心展示。

### Figure 10 (p.15) ⭐深度解读
![[assets/crops/kimi-vl-technical-report-fig10.png]]
*整页渲染: ![[assets/kimi-vl-technical-report-p15.png]]*
> [!quote] caption
> Kimi-VL is capable of following multi-step reasoning processes to complete complex GUI tasks. In this example, it successfully enables the “Do Not Track” feature in the Chrome browser to enhance online privacy. The agent interprets each screen, identifies relevant UI elements, and performs the appropriate actions sequentially with clear thoughts, actions, and API calls. 15

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读**

**1) 核心对象与结构**：图示展示Kimi-VL完成一项12步GUI代理任务。顶部为用户指令（启用Chrome"Do Not Track"）+ 初始桌面截图；下方按Step 1–12纵向排布，每步含三栏：屏幕截图、Thought（链式推理）、Action+Toolcall（精确API调用，如`click(x=0.884,y=0.144)`、`scroll(-5)`），所有坐标均为归一化值。

**2) 关键技术结论**：Agent在每步先"看"当前界面、再"想"下一步动作、最后以坐标级精度"点"。过程并非一蹴而就——Step 6误入"Manage HTTPS/SSL certificates"后，Step 9主动点击返回键修正路径，证明其具备多步规划、视觉定位与**自主错误恢复**能力。

**3) 论文整体作用**：作为定性案例（qualitative case），补足定量基准外的可解释性证据，验证"思维–动作–工具调用"框架在真实桌面GUI环境中的端到端可用性。

### Figure 11 (p.16) ⭐深度解读
![[assets/crops/kimi-vl-technical-report-fig11.png]]
*整页渲染: ![[assets/kimi-vl-technical-report-p16.png]]*
> [!quote] caption
> Video scene splitting. Kimi-VL processes a long-form video by segmenting it into coherent scenes and providing detailed start/end timestamps along with fine-grained natural language descriptions for each scene.†

> [!tip] 技术解读（多模态）
> 【图文联合解读】图11为Kimi-VL对一段约3分37秒长视频的"场景分割"定性示例。

核心结构：左侧为切分指令"按场景切分并给出起止时间与描述"；输入为均匀采样的视频帧网格；右侧输出12段连续场景（00:00:00→00:03:37），每段含秒级时间戳与细粒度自然语言描述，覆盖镜头运动（如close-up、aerial view、pan）、光线、纹理与抽象主题（spirituality、adventure、preparation）。

技术结论：示例论证模型具备（1）长视频全局时间感知与场景边界判别；（2）细粒度视觉-语言对齐（识别皱纹、转经筒、山脉等微线索）；（3）抽象主题归纳与情绪氛围刻画能力。

方法链作用：作为定性可视化案例，验证模型仅凭视觉帧即可完成时序切分与叙述性描述，无需ASR/检测器辅助，支撑论文"长视频理解"主张，属应用展示而非定量评测。

### Figure 12 (p.17) ⭐深度解读
![[assets/crops/kimi-vl-technical-report-fig12.png]]
*整页渲染: ![[assets/kimi-vl-technical-report-p17.png]]*
> [!quote] caption
> Catching and understanding key details from an hour-long video course. Kimi-VL demonstrates its ability to comprehend and interpret instructional video content by analyzing frame sequences and extracting conceptual progression over time. In this case, the model identifies a deepening of the traditional saying “Teach a man to fish, and you feed him for a lifetime” into a more nuanced idea: “Teach h

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图12图文联合解读**

图12由上下两栏组成：上栏为Instruction栏，含中文古谚"授人以鱼…授人以渔"及"找出作者进一步要求并详述"的指令，正文中"$$#$$"与圆点为视频帧采样占位符（代表小时级课程的多帧输入）；下栏为Response栏，模型准确识别深层要求为"教其鱼味并使之饥饿"，并阐释其"激发自驱学习"的内涵。

**论证结论**：Kimi-VL能从小时级视频帧序列中追踪概念递进，完成细粒度语义抽取与抽象归纳，证明其视频时序理解与跨模态推理能力。

**论文作用**：作为长视频理解的定性案例，与定量基准互补，支撑"thinking with images"在视频时序推理上的核心卖点，展示模型在真实长课程场景中的实用价值。

### Figure 13 (p.16) ⭐深度解读
![[assets/crops/kimi-vl-technical-report-fig13.png]]
*整页渲染: ![[assets/kimi-vl-technical-report-p16.png]]*
> [!quote] caption
> Specifically, increasing the max thinking token length at inference time consistently improves test-time accuracy across all three 16

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图13展示Kimi-VL-Thinking模型在三个基准（MathVision、MathVista、MMMU）上，测试精度随最大思维token长度（1k→2k→4k→8k→16k）变化的情况。

**关键数据：**
- **MathVision**：18.7% → 22.6% → 29.0% → 34.0% → 36.8%，近似翻倍（+18.1pp），单调上升且无明显饱和；
- **MathVista**：66.7% → 69.0% → 70.9% → 70.6% → 71.3%，4k后趋于平台（+4.6pp）；
- **MMMU**：49.2% → 52.4% → 56.2% → 60.1% → 61.7%，稳定增长（+12.5pp）。

**论证结论：** 推理阶段延长思维链长度可在三类任务上持续提升准确率，证明Kimi-VL-Thinking的思维机制具备可扩展的测试时计算红利。

**论文作用：** 该图属于"test-time scaling"分析，是论文方法链路中证明"thinking能力可被算力放大"的核心证据，与训练阶段强化学习成果共同支撑"思维链即推理算力"的整体叙事。

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.5) ⭐深度解读
![[assets/crops/kimi-vl-technical-report-tab01.png]]
> [!quote] caption
> Overview of training stages: data composition, token volumes, sequence lengths, and trainable components.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 1 图文联合解读**

该表以四阶段列结构展示 Kimi-VL 训练流水线：**ViT Training**（仅训视觉编码器，2T+0.1T tokens，seq=8192）→ **Joint Pre-training**（联合训练 ViT&LLM，1.4T tokens，数据涵盖 Caption/Grounding/OCR/Video/Agent，seq=8192）→ **Joint Cooldown**（0.6T tokens，高质量学术与多模态数据精炼）→ **Joint Long-context**（0.3T tokens，seq 从 32768 扩展至 131072，处理长文本/视频/文档）。

**论证的关键结论**：①采用"先视觉、后联合"的分阶段范式，LLM 仅在阶段 2 起参与训练以稳定收敛；②数据构成由粗到精、由短到长递进；③长上下文阶段通过 4× 序列长度扩展使模型具备长视频/长文档推理能力。该表是论文方法链路的核心路线图，为后续 Figure 1 在 MathVision 等基准上的强推理表现提供了训练配方的可复现说明。

### Table 2 (p.5) ⭐深度解读
![[assets/crops/kimi-vl-technical-report-tab02.png]]
> [!quote] caption
> Needle-in-a-Haystack (NIAH) test on text/video haystacks, where needles are uniformly distributed at various positions within the haystack. We report recall accuracy across different haystack lengths up to 131,072 tokens (128K).

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 2 联合解读**

**1) 核心对象与数据：**
该表展示 Kimi-VL 在 Needle-in-a-Haystack（NIAH）检索任务上的召回准确率，按 7 个长度区间（0–128K token）对比文本与视频两种 haystack。结果显示：在 0–32K 区间内，文本与视频均保持 **100%** 召回；进入 32K–65K 区间后均出现下滑，文本降至 **87.0%**，视频为 **91.7%**；65K–131K 区间标记为「-」，未给出数据。

**2) 关键技术结论：**
模型在 32K 量级内对两种模态均具备完美的"针"定位能力，验证了其长上下文窗口的有效性；视频模态在长序列下（32K–65K）反而略优于文本（91.7% vs 87.0%），暗示视频帧表征的压缩/采样策略并未折损长程检索能力。

**3) 在论文中的作用：**
NIAH 作为长上下文基线能力验证，与 Figure 2 所宣称的 LongVideoBench、Video-MME、MMLongBench-Doc 等长视频/长文档基准表现形成因果链——只有底层上下文检索稳健，上层多模态推理与 Agent 任务（ScreenSpot-Pro、OSWorld）的高分才有方法论根基。

### Table 3 (p.10) ⭐深度解读
![[assets/crops/kimi-vl-technical-report-tab03.png]]
> [!quote] caption
> presents a comprehensive evaluation of Kimi-VL against state-of-the-art vision-language models across multiple benchmarks. Although having a more parameter-efficient architecture (2.8B+0.4B activated parameters) compared to larger models such as GPT-4o, Llama-3.2-11B-Inst. and Gemma3-12B-IT, Kimi-VL

> [!tip] 表格解读（多模态）
> 【图文联合解读】**表3核心内容**：将2.8B+0.4B激活参数（16B总量）的Kimi-VL-A3B与GPT-4o、Qwen2.5-VL-7B、Llama3.2-11B、Gemma3-12B、DeepSeek-VL2在9大类（高校级/通用/多图/数学/OCR/OS代理/长文档/长视频/视频感知）约30项基准上对标。Kimi-VL多项夺粗体（最优）或下划线（次优），典型如OS Agent ScreenSpot-V2 92.8、ScreenSpot-Pro 34.5、OSWorld 8.22，OCR InfoVQA 83.2、OCRBench 867，长视频Video-MME 72.6、MLVU 74.2，MathVista 68.7、AI2D 84.9。

**论证结论**：以显著更少的激活参数即可匹配或超越参数量数倍于己的GPT-4o、Llama-3.2-11B、Gemma3-12B-IT，并在OS代理与长上下文场景上展现明显领先。

**链路作用**：作为Figure 2亮点声明的定量后盾，验证MoonViT+MLP+MoE架构的"小激活、强能力"核心主张，是全文实验论证的主表。

### Table 4 (p.17) ⭐深度解读
![[assets/crops/kimi-vl-technical-report-tab04.png]]
> [!quote] caption
> Performance of Kimi-VL-Thinking and Kimi-VL-Thinking-2506 on multimodal reasoning benchmarks. The metrics evaluated include MathVista (mini), MMMU (val), MMMU-Pro (average), MathVision (full) and VideoMMMU, with results expressed in Pass@1. The Kimi-VL-Thinking-2506 performs well in most cases, show

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 4 图文联合解读：**

表4对比Kimi-VL-Thinking与Kimi-VL-Thinking-2506及多款开源/闭源模型在5个多模态推理基准的Pass@1。2506版以MathVision 56.9、MathVista 80.1、MMMU-Pro 46.3、VideoMMMU 65.2四项居首，仅MMU(64.0)低于峰值77.3。原文据此论证"thinking"变体经强化训练后跨域推理能力全面跃升，作为论文方法链路中验证推理增强路径有效性的关键收尾实证，强化了多模态"思考"模式相较基线的优势。

### Table 5 (p.18) ⭐深度解读
![[assets/crops/kimi-vl-technical-report-tab05.png]]
> [!quote] caption
> Performance of Kimi-VL-A3B-Thinking-2506 on multimodal benchmarks that do not require extensive reasoning.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 5 联合解读**

Table 5 对比 GPT-4o、Qwen2.5-VL-7B、Gemma3-12B-IT 及 Kimi-VL 三个版本，在通用多模态、视频、OS-Agent、长文档共 11 项非深度推理基准上的表现。数据显示 Kimi-VL-A3B-Thinking-2506 在 MMBench-EN(84.4)、MMStar(70.4)、MMVet(78.1)、ScreenSpot-Pro(52.8)、MMLongBench-Doc(42.1) 等多数项上达 SOTA，且 OS-Agent 三项较 Instruct 版显著提升。该表与 Figure 5 的训练流程图呼应，用以佐证 Thinking-2506 即便不依赖长链推理亦保持领先，说明后续 32K/128K 长上下文 SFT 与长 CoT SFT+RL 未牺牲通用能力。

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\max_\theta \mathbb{E}_{(x, y^*)\sim\mathcal{D}}\left[ \mathbb{E}_{(y, z)\sim\pi_\theta} \left[r(x, y, y^*)\right] - \tau \mathrm{KL} (\pi_{\theta}(x) || \pi_{\theta_i}(x)) \right]\, ,
$$

## 相关论文

- [[qwen3-vl-technical-report]] — Qwen3-VL Technical Report
- [[qwen2-5-vl-technical-report]] — Qwen2.5-VL Technical Report
- [[kimi-k2-5-visual-agentic-intelligence]] — KIMI K2.5: VISUAL AGENTIC INTELLIGENCE
- [[deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms]] — DeepStack: Deeply Stacking Visual Tokens is Surprisingly Simple and Effective for LMMs
- [[efficiently-serving-large-multimodal-models-using-epd-disaggregation]] — Efficiently Serving Large Multimodal Models Using EPD Disaggregation

## 技术点深读（DEEP）

![[deep/kimi-vl-technical-report]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/kimi-vl-technical-report.txt`（122024 字符）供引用检索。