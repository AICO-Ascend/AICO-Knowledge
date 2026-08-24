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
> 【图文联合解读】**图文联合解读**

图示 Kimi-VL 三模块架构：**MoonViT**（原生分辨率视觉编码器）→ **MLP Projector** → **MoE Language Decoder**（堆叠 N 层，每层含 Attention + MoE FFN，Router 将 token 分派至 Non-shared Experts 与 Shared Experts）。

MoonViT 直接处理多尺度异构输入，规避 resize 失真：小图 50×20px、长视频 480×270px 多帧、细粒度图 1113×672px（1008px 内含 ROI）、OCR 条带 58px 高、UI 截图 800×1731px。

**论证要点**：原生分辨率编码保留细节以适配异构视觉任务；MoE 兼顾容量与推理效率。**论文作用**：作为开篇架构总图，奠定后续多基准（OCR InfoVQA、Agent OSWorld/屏幕截图、长视频 LongVideoBench 等）泛化性能的方法学根基。

### Figure 4 (p.4) ⭐深度解读
![[assets/crops/kimi-vl-technical-report-fig04.png]]
*整页渲染: ![[assets/kimi-vl-technical-report-p04.png]]*
> [!quote] caption
> The pre-training stages of Kimi-VL consume a total of 4.4T tokens after text-only pre-training of its language model. To preserve text abilities, all stages that update the language model are joint training stages. preprocessing operations enable MoonViT to share the same core computation operators and optimization as a language model, such as the variable-length sequence attention mechanism suppo

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

该图展示 Kimi-VL 三阶段预训练流水线：(1) 文本预训练 5.2T tokens（纯文本）；(2) ViT 训练 2.0T→0.1T tokens，采用 CoCa-loss + 微型语言解码器对齐 LLM；(3) 联合预训练 1.4T tokens，多模态数据渐进式升至 40%，并以"resumes LR scheduler"衔接文本阶段。

论文借此论证两点关键结论：①预训练总计消耗 4.4T tokens（不含纯文本阶段）；②所有更新语言模型的阶段均为联合训练，以防止灾难性遗忘、保留文本能力。

该图为方法总纲，奠定后续 SFT/RLHF 的基础——先打牢文本与视觉编码器各自基础，再以渐进比例融合多模态，是 Kimi-VL 在不牺牲语言能力前提下获得视觉理解能力的关键架构设计。

### Figure 5 (p.6) ⭐深度解读
![[assets/crops/kimi-vl-technical-report-fig05.png]]
*整页渲染: ![[assets/kimi-vl-technical-report-p06.png]]*
> [!quote] caption
> The post-training stages of Kimi-VL and Kimi-VL-Thinking, including two stages of joint SFT in 32K and 128K context, and further long-CoT SFT and RL stages to activate and enhance long thinking abilities. to 800,000. The joint long-context stage is conducted in two sub-stages, where each one extends the model’s context length by four times. For data composition, we filter and upsample the ratio of

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

**1) 核心结构：** 图示 Kimi-VL 后训练三阶段流水线。阶段一为**联合监督微调（SFT）**，在文本+多模态数据上依次进行 **1 Epoch@32K + 1 Epoch@128K**，上下文每阶段扩展 4 倍；阶段二为**长思维链 SFT（Long-CoT SFT）**，覆盖 Planning、Evaluation 等推理数据；阶段三为 **RL**（强化学习）以增强长思考能力。

**2) 关键技术结论：** 通过"短上下文联合训练 → 上下文长度逐级倍增 → 长 CoT 微调 → RL 强化"的递进式设计，以约 80 万样本量实现长上下文与长链思考能力的协同激活。

**3) 在论文中的作用：** 位于预训练之后、推理评测之前，是 Kimi-VL 区别于普通 VLM 的核心增强链路，承担将基础模型升级为具备长思考能力的 Thinking 变体的关键职能。

### Figure 6 (p.8) ⭐深度解读
![[assets/crops/kimi-vl-technical-report-fig06.png]]
*整页渲染: ![[assets/kimi-vl-technical-report-p08.png]]*
> [!quote] caption
> Manuscript reasoning visualization. Kimi-VL-Thinking demonstrates the ability to perform historical and scientific inference by analyzing handwritten manuscripts step by step. In this example, our model identifies the author as Albert Einstein based on handwriting style, content analysis, and language cues. It reasons that the manuscripts relate to gravitational field equations, consistent with Ei

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图6图文联合解读**

图6展示Kimi-VL-Thinking对爱因斯坦手稿图像的逐步推理过程（部分文字片段呈现）。模型沿多条线索链式分析：①**视觉感知**——手写潦草但连贯，源自单一作者；②**数学内容**——含g(引力)、M(质量)、T(时间)等变量、偏导求和与张量记法，符合场论风格；③**语言线索**——出现德语"Gleichung"(方程)、"Gln"，指向德语母语者；④**知识匹配**——公式与广义相对论场方程吻合，最终判定作者为Albert Einstein。该图作为定性案例，定证Thinking模式具备**多模态链式推理**与**跨域(历史人物+科学理论)联合推断**能力，是论文论证"思考型VLM"区别于普通VLM的核心可视化证据之一。

### Figure 7 (p.12) ⭐深度解读
![[assets/crops/kimi-vl-technical-report-fig07.png]]
*整页渲染: ![[assets/kimi-vl-technical-report-p12.png]]*
> [!quote] caption
> Kimi-VL exhibits strong visual reasoning capabilities by grounding visual content in spatial, contextual, and cultural knowledge. It accurately identifies matching urban locations based on structural and layout features, interprets scenes from video games like Cyberpunk 2077 using stylistic cues, and recognizes real-world landmarks such as the

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

**1) 核心对象与结构：** 图为多子图问答演示，至少包含两个完整案例：①城市场景匹配——模型比对四张子图（含圆顶/天文台建筑），通过密度、布局、圆顶结构特征判定第4张与第1张同地；②地标识别——基于可伸缩屋顶与CN塔背景，定位为多伦多Rogers Centre体育场；③游戏场景识别——依据霓虹灯、全息屏、赛博朋克美学判断为《赛博朋克2077》Night City中的酒吧/俱乐部。每个案例以"图像+Response"配对呈现。

**2) 关键技术结论：** 论证Kimi-VL具备三类视觉推理能力——空间/结构匹配（layout grounding）、文化地标识别（cultural landmark grounding）、风格化场景理解（stylistic cue grounding），即视觉内容可被锚定于空间、语境与文化知识。

**3) 在论文中的作用：** 作为定性案例（qualitative showcase），与论文核心主张"激活视觉推理"互文，支撑其在M3原生训练阶段联合注入的OCR、图像描述、视觉定位与世界知识等多模态能力，无需CoT即可完成复杂跨模态推断。

### Figure 8 (p.13) ⭐深度解读
![[assets/crops/kimi-vl-technical-report-fig08.png]]
*整页渲染: ![[assets/kimi-vl-technical-report-p13.png]]*
> [!quote] caption
> Kimi-VL demonstrates its capability to perform symbolic reasoning and geometric inference by solving a circle geometry problem step by step. The model analyzes given conditions, applies geometric theorems such as the inscribed angle theorem and properties of triangle angles, and accurately derives the target angle. presented in visual contexts. On the more challenging MathVision benchmark, due to 

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

**1) 核心对象与结构：** 该图展示一道圆形几何题的求解示例。题目给定⊙O中AB为直径、D、C在圆上、∠D=62°，求∠ACO（选项A.26°/B.28°/C.30°/D.32°）。模型分三步作答：①由直径得∠ACB=90°；②圆心角∠AOC=2×62°=124°；③等腰△AOC中2x+124°=180°，解得x=28°，选B。

**2) 关键结论：** 证明Kimi-VL能将视觉几何信息转化为符号链，综合调用圆周角定理、直径性质、等腰三角形等多条定理，完成多步精准推理。

**3) 论文作用：** 作为定性案例，与MathVision等定量基准互补，展示模型在视觉-符号跨模态数学推理上的实际能力，强化其技术报告的方法学说服力。

### Figure 9 (p.14) ⭐深度解读
![[assets/crops/kimi-vl-technical-report-fig09.png]]
*整页渲染: ![[assets/kimi-vl-technical-report-p14.png]]*
> [!quote] caption
> Diverse OCR visualization. Kimi-VL demonstrates strong OCR capabilities across varied content types, including structured financial tables, complex mathematical formulas, and handwritten Chinese text. The model accurately parses tabular data into markdown, converts formulas to LaTeX, and transcribes handwritten paragraphs with contextual understanding, showcasing its versatility in multimodal text

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图像部分内容编码异常，仅能识别三栏布局与分隔结构，需结合原文解读。**

图9以三栏并列结构展示Kimi-VL的OCR能力：①左栏为结构化金融表格（含"Total Current Assets""Property, Plant"等多行条目，括号内数值列），被解析为markdown表格；②中栏为复杂数学公式（含分式、求和、上下标 `∑h^N O^N`、`Q^x ≤ N` 等符号），下方标注"Rendered formula"，体现LaTeX转换；③右栏为手写中文段落，转录为带语境的文字。

原文借此论证：模型在**结构化表格→markdown、符号公式→LaTeX、手写文本→转录**三类异构模态上均具备鲁棒的多模态文本抽取与解释能力。

在论文链路中，该图作为Figure 9位于实验可视化部分（p.14），与表格/榜单（定量）互补，以定性案例支撑前文OCR、ChartQA、DocVQA等基准结论，强化"Kimi-VL在真实异构文档场景中具备工程级可用性"的叙事。

### Figure 10 (p.15) ⭐深度解读
![[assets/crops/kimi-vl-technical-report-fig10.png]]
*整页渲染: ![[assets/kimi-vl-technical-report-p15.png]]*
> [!quote] caption
> Kimi-VL is capable of following multi-step reasoning processes to complete complex GUI tasks. In this example, it successfully enables the “Do Not Track” feature in the Chrome browser to enhance online privacy. The agent interprets each screen, identifies relevant UI elements, and performs the appropriate actions sequentially with clear thoughts, actions, and API calls. 15

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图像无法辨认，仅依据原文解读。**

图片渲染为乱码字符，仅可辨识出 Step 1–12 共 12 个步骤标签，原图应为 Chrome 浏览器中开启"Do Not Track"的截图序列（含思考、动作、API 调用三栏），实际内容未能呈现。

按 caption 与正文论述：

1) **核心对象**：Kimi-VL 在 GUI 智能体场景下的多步骤推理案例——12 步内依次完成 Chrome 隐私设置导航、菜单定位、开关切换等操作，每步均含 Thought / Action / API Call 三段结构；

2) **关键结论**：证明模型具备逐帧视觉解读 + UI 元素识别 + 顺序动作执行的链式推理与工具调用能力，可胜任复杂 GUI 任务；

3) **论文作用**：作为定性 case study，定向支撑"Kimi-VL 视觉–语言–动作闭环"的能力论述，是其与同类模型在 GUI agent 维度对比的直观佐证。

### Figure 11 (p.16) ⭐深度解读
![[assets/crops/kimi-vl-technical-report-fig11.png]]
*整页渲染: ![[assets/kimi-vl-technical-report-p16.png]]*
> [!quote] caption
> Video scene splitting. Kimi-VL processes a long-form video by segmenting it into coherent scenes and providing detailed start/end timestamps along with fine-grained natural language descriptions for each scene.†

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图11展示Kimi-VL长视频场景分割能力：左侧输入为一段约3分37秒的短片（密集帧采样网格），右侧模型输出12个场景切片（时间跨度00:00:00–00:03:37），每个均给出精确起止时间戳与细粒度描述，涵盖人物动作（如转经轮老者、滑雪跳跃）、镜头运动（特写/航拍/水下）、情绪氛围（神秘、敬畏）及贯穿主题（精神性、冒险、人与自然）。

**论证结论：** 模型具备分钟级长时序视频理解、精准时间定位与连贯叙事生成能力，能在多场景切换中保持语义一致性，并自动提炼主题线索。

**整体作用：** 作为定性示例，与其他视频能力图共同支撑Kimi-VL在长视频任务上的实用性与细粒度描述质量，强化论文"长上下文多模态理解"的核心主张。

### Figure 12 (p.17) ⭐深度解读
![[assets/crops/kimi-vl-technical-report-fig12.png]]
*整页渲染: ![[assets/kimi-vl-technical-report-p17.png]]*
> [!quote] caption
> Catching and understanding key details from an hour-long video course. Kimi-VL demonstrates its ability to comprehend and interpret instructional video content by analyzing frame sequences and extracting conceptual progression over time. In this case, the model identifies a deepening of the traditional saying “Teach a man to fish, and you feed him for a lifetime” into a more nuanced idea: “Teach h

> [!tip] 技术解读（多模态）
> 【图文联合解读】该图展示Kimi-VL对一段约36分钟（00:00–35:55）教学视频的10帧采样理解任务。指令要求在"授人以鱼/渔"谚语基础上找出作者的"进一步要求"。模型通过逐帧追踪幻灯片文本语义演进：从"give a man a fish"→"teach a man to fish"→"teach him the taste of fish and make him hungry"，精准定位第三层递进，并在响应中给出完整阐释（强调激励与持续学习的重要性）。

此例用以定性论证模型对**长视频帧序列的概念演化抽取与跨时序推理**能力。在论文评测链路中，它作为"长时序+概念理解"的典型案例，与定量基准互补，支撑 Kimi-VL 在视频理解维度的能力声明，体现其从稀疏关键帧中聚合高层语义的技术优势。

### Figure 13 (p.16) ⭐深度解读
![[assets/crops/kimi-vl-technical-report-fig13.png]]
*整页渲染: ![[assets/kimi-vl-technical-report-p16.png]]*
> [!quote] caption
> Specifically, increasing the max thinking token length at inference time consistently improves test-time accuracy across all three 16

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

1) **核心对象与数据**：图13展示Kimi-VL-Thinking在MMMU基准上，推理时最大思考token长度（1k/2k/4k/8k/16k）对测试准确率的影响。数据点为49.2%→52.4%→56.2%→60.1%→61.7%，呈单调递增；图中左侧另可见MathVista在8k时71.3%等数据点，共涉及三个benchmark。

2) **关键结论**：原文论证"在三个16k上限的benchmark上，增加推理时的最大思考token长度均能持续提升测试准确率"，即test-time scaling law在视觉推理模型上同样成立，思考预算越大收益越高，但16k→8k的边际增益（+1.6pp）小于4k→8k（+3.9pp），呈饱和趋势。

3) **论文作用**：该图作为"思考长度即性能杠杆"的实证支撑，强化了Kimi-VL-Thinking的核心卖点——通过扩展推理时的思考预算实现性能提升，与文本版Kimi k1.5的test-time compute scaling主张一脉相承，奠定视觉MLLM的scaling新范式。

## 表格（裁剪图 + caption，可直接插入报告）

### Table 2 (p.5) ⭐深度解读
![[assets/crops/kimi-vl-technical-report-tab02.png]]
> [!quote] caption
> Needle-in-a-Haystack (NIAH) test on text/video haystacks, where needles are uniformly distributed at various positions within the haystack. We report recall accuracy across different haystack lengths up to 131,072 tokens (128K).

> [!tip] 表格解读（多模态）
> 【图文联合解读】Table 2 展示 NIAH（Needle-in-a-Haystack）检索测试在文本/视频干草堆上、7 个长度区间（0–131072 token）的召回率。数据显示：前 5 个区间（0–32768 token）文本与视频均稳定达到 100% 满分；(32768,65536] 区间文本 87.0%、视频 91.7%；(65536,131072] 列无有效数值。该表用以支撑 Kimi-VL 具备 128K 级超长上下文高鲁棒检索能力的关键结论，与 Figure 2 的多模态综合基准亮点互补，是论文长文档/长视频理解能力实验链路中的核心实证之一。

### Table 3 (p.10) ⭐深度解读
![[assets/crops/kimi-vl-technical-report-tab03.png]]
> [!quote] caption
> presents a comprehensive evaluation of Kimi-VL against state-of-the-art vision-language models across multiple benchmarks. Although having a more parameter-efficient architecture (2.8B+0.4B activated parameters) compared to larger models such as GPT-4o, Llama-3.2-11B-Inst. and Gemma3-12B-IT, Kimi-VL

> [!tip] 表格解读（多模态）
> 【图文联合解读】**说明**：所提供图像实为论文正文段落（含脚注），并非 Table 3 表格本体，故"图像无法呈现具体数值"，以下解读基于原文论述：

1) **核心对象**：该表横向对比 Kimi-VL 与 GPT-4o、Llama-3.2-11B-Inst.、Gemma3-12B-IT、DeepSeek-VL2、Qwen2.5-VL-7B（实为 8.3B）等 SOTA 视觉语言模型，涵盖 24 项 benchmark 的量化得分。

2) **关键结论**：Kimi-VL 以 MoE 架构仅 2.8B+0.4B 激活参数（总参 16B）即超越 DeepSeek-VL2（4.5B 激活/28B 总），并在 24 项中 19 项击败 Qwen2.5-VL-7B，论证"少参数、优性能"的效率-效果优势。

3) **链路作用**：作为整篇论文核心实验证据，配合 Figure 2 高亮展示，全面支撑"参数高效 MoE 视觉语言模型仍具 SOTA 竞争力"这一中心论点。

### Table 4 (p.17) ⭐深度解读
![[assets/crops/kimi-vl-technical-report-tab04.png]]
> [!quote] caption
> Performance of Kimi-VL-Thinking and Kimi-VL-Thinking-2506 on multimodal reasoning benchmarks. The metrics evaluated include MathVista (mini), MMMU (val), MMMU-Pro (average), MathVision (full) and VideoMMMU, with results expressed in Pass@1. The Kimi-VL-Thinking-2506 performs well in most cases, show

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 4 联合解读**

该表展示 Kimi-VL-Thinking 与 Kimi-VL-Thinking-2506 在 5 项多模态推理基准（MathVision、MathVista、MMMU、MMMU-Pro、VideoMMMU）上的 Pass@1 得分，并与多款基线模型横向对比。量化数据上，2506 版本在三项取得最高分：MathVision **56.9**、MathVista **80.1**、VideoMMMU **65.2**；MMMU-Pro 上基础版 **51.7** 也为最优，MMMU(val) 上某基线 77.3 略高。

论文据此论证"thinking"变体在迭代训练后，于数学推理、视觉问答、视频理解等不同领域与尺度上均实现能力跃升，凸显其思维链推理机制在多模态场景的泛化性与有效性。该表承接 Figure 4 所示预训练流程（4.4T tokens 联合训练），共同构成"训练方法→推理评测"的闭环证据链，是支撑 Kimi-VL-Thinking 系列整体性能主张的核心实验支柱。

### Table 5 (p.18) ⭐深度解读
![[assets/crops/kimi-vl-technical-report-tab05.png]]
> [!quote] caption
> Performance of Kimi-VL-A3B-Thinking-2506 on multimodal benchmarks that do not require extensive reasoning.

> [!tip] 表格解读（多模态）
> 【图文联合解读】表5展示Kimi-VL-A3B-Thinking-2506在**通用多模态、视频理解、OS-Agent定位、长文档**四类非高强度推理基准上的表现，并与GPT-4o、Qwen2.5-VL-7B、Gemma3-12B-IT及Kimi自有基线（A3B-Instruct/Thinking）对比。量化亮点：MMBench-EN 84.4、OCRBench 869、MMStar 70.4、MMVet 78.1、RealWorldQA 70.0、MMVU 57.5、ScreenSpot-Pro 52.8、OSWorld-G 52.5均位列首位；MMLongBench-Doc 42.1逼近GPT-4o的42.8。

原文结合Figure 5所述后训练流程（两阶段32K/128K联合SFT + long-CoT SFT/RL），论证**经长链推理强化后，模型在通用感知与Agent任务上并未"此消彼长"**，而是同步刷榜。它在论文整体方法链路中，与Table 6（推理基准）形成互补——前证"会思考"，本表证"不忘看"，共同支撑"thinking不损感知"的实验结论。

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