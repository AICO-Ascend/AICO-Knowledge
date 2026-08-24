---
paper_num: "13"
title: "Qwen3-VL Technical Report"
authors: "Qwen3-VL Technical Report Qwen Team"
date: "2026/6/10"
arxiv: "https://arxiv.org/abs/2511.21631"
pdf: "papers/qwen3-vl-technical-report.pdf"
slug: "qwen3-vl-technical-report"
tags: [multimodal]
---

# Qwen3-VL Technical Report

> [!abstract] 摘要（原文）
> 1\. 🚀 Qwen3-VL是Qwen系列迄今为止最强大的视觉-语言模型，在广泛的多模态基准测试中表现出色，原生支持高达256K tokens的文本、图像和视频交错上下文。 2. 💡 该模型家族包括密集型（2B/4B/8B/32B）和MoE型（30B-A3B/235B-A22B）变体，并通过增强的interleaved-MRoPE、DeepStack集成和基于文本的时间对齐等架构升级，提升了视觉-语言对齐和长上下文理解能力。 3. 📈 Qwen3-VL在通用VQA、多模态推理、文档理解、2D/3D Grounding和视频理解等任务中均实现领先性能，并且在纯文本能力方面超越了部分文本专用模型，同时在多语言OCR支持方面也取得了显著进展。

## 元信息
- **发表日期**: 2026/6/10
- **作者**: Qwen3-VL Technical Report Qwen Team
- **arXiv**: https://arxiv.org/abs/2511.21631
- **本地 PDF**: `papers/qwen3-vl-technical-report.pdf`
- **页数**: 42

## 图表（原文 caption + 页码）

### Figure 1 (p.3) ⭐深度解读
![[assets/crops/qwen3-vl-technical-report-fig01.png]]
*整页渲染: ![[assets/qwen3-vl-technical-report-p03.png]]*
> [!quote] caption
> The Qwen3-VL framework integrates a vision encoder and a language model decoder to process multimodal inputs, including text, images, and video. The vision encoder is specifically designed to handle dynamic, native-resolution visual inputs, mapping them to visual tokens of variable length.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图示Qwen3-VL整体架构：Vision Encoder接收**原生分辨率**输入——图1（1248×9376→**11427 tokens**）、图2（256×32→**8 tokens**，超小图）、图3（1440×800→**1125 tokens**）及视频流（含0.0/4.0/8秒帧，736×448），输出**变长视觉令牌**；DeepStack将多层视觉令牌同时注入LLM Block 1~N，Interleaved MRoPE编码位置、文本时间戳定位视频帧，最终由Dense/MoE Decoder统一自回归解码图文视频令牌。

该图佐证三大技术结论：①视觉令牌数与分辨率成正比、变长映射；②DeepStack多层注入保留细节；③统一解码器兼容文本/图像/视频。它是论文方法部分的**总览蓝图**，为后续章节的预训练、实验设计提供框架基础。

### Figure 2 (p.17) ⭐深度解读
![[assets/crops/qwen3-vl-technical-report-fig02.png]]
*整页渲染: ![[assets/qwen3-vl-technical-report-p17.png]]*
> [!quote] caption
> Multilingual OCR performance of our model on a self-built test set. The model achieves over 70% accuracy on 32 out of 39 supported languages, demonstrating strong and usable multilingual capabilities. establishes a new state of the art, marginally outperforming its “thinking” counterpart, Qwen3-VL- 235B-A22B-Thinking. On OCR-related visual question answering (VQA) benchmarks that require both OCR 

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图2为条形图，横轴列出39种语言（按准确率升序排列），纵轴为OCR准确率（%），色阶由浅紫渐变至深紫。最低为Romanian/Swahili约71%，最高为Swedish约98%，其中32种语言超70%；欧洲语种（瑞典、塞尔维亚、丹麦约97–98%）与韩语、阿拉伯语、泰语、印尼语表现突出。

该图作为OCR-VQA基准之外的补充实验，与原文"原生分辨率Vision Encoder + DeepStack多层视觉令牌注入 + Interleaved MRoPE"架构相呼应，论证模型视觉-文本对齐能力在跨语言文档理解任务中的泛化性，支撑论文"强且可用的多语言能力"这一核心结论，定位为方法链路中视觉编码器表征质量的实证验证环节。

### Figure 3 (p.25) ⭐深度解读
![[assets/crops/qwen3-vl-technical-report-fig03.png]]
*整页渲染: ![[assets/qwen3-vl-technical-report-p25.png]]*
> [!quote] caption
> Needle-in-a-Haystack performance heatmap for Qwen3-VL-235B-A22B-Instruct across varying video durations and needle positions. Each cell shows accuracy (%) for locating and answering questions about the inserted “needle” frame.

> [!tip] 技术解读（多模态）
> 【图文联合解读】图3为Qwen3-VL-235B-A22B-Instruct的视频"大海捞针"(NIAH)检索热力图：横轴为视频时长，左板为训练内上下文(0–30min/≤256K token)，右板为外推上下文(40–120min/最高1024K token)，纵轴为针帧插入深度(0–100%)，共约70个单元格按Accuracy Score(0–1，红→黄→绿)着色。实测中各深度×时长组合的格子几乎全部呈深绿(≈1.0)，无明显红/黄区，表明无论针帧置于首尾或中段、视频长达2小时/1024K token，模型均能稳定定位并正确作答。该图作为核心长上下文评测证据，支撑Qwen3-VL"原生小时级长视频理解"的关键卖点，并实证其从256K到1024K的上下文外推能力无明显退化。

## 表格（裁剪图 + caption，可直接插入报告）

### Table 2 (p.15) ⭐深度解读
![[assets/crops/qwen3-vl-technical-report-tab02.png]]
> [!quote] caption
> Performance of Qwen3-VL-235B-A22B and top-tier models on visual benchmarks. The highest scores of the reasoning and non-reasoning models are shown in bold and underlined , respectively. Results marked with an ∗ are sourced from the technical report. + denotes results with tool use.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读**

Table 2将Qwen3-VL-235B-A22B的thinking与instruct双版本，与Gemini 2.5 Pro、GPT-5、Claude Opus 4.1在5大类视觉基准（STEM 14项、General VQA 5项、Alignment 3项、Document Understanding 11项、2D/3D Grounding 6项）上横向对比。thinking版在MIA-Bench 92.7、DocVQA 96.5、MathVista-mini 85.8、MathVerse-mini 85.0、RefCOCO 92.1、CountBench 93.7取得领先；instruct版则在DocVQA 97.1、InfoVQA 89.2、OCRBench 920等文档/OCR任务上SOTA。该表用数据验证图1所提架构——原生分辨率视觉编码（含超小图8 token至极长图11427 tokens的变长令牌）、DeepStack多层注入、Interleaved MRoPE位置编码——的有效性，使开源MoE 235B模型整体对标顶级闭源对手，并在文档理解与细粒度定位上确立新SOTA，呼应文中"marginally outperforms its thinking counterpart"的双版本设计论断。

### Table 3 (p.16) ⭐深度解读
![[assets/crops/qwen3-vl-technical-report-tab03.png]]
> [!quote] caption
> Performance of medium-sized Qwen3-VL models and previous models on visual benchmarks. The highest scores are shown in bold . Results marked with an ∗ are sourced from the technical report. + denotes results with tool use.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 3 图文联合解读：**

该表横跨 STEM/Puzzle、General VQA、Alignment、Document Understanding、2D/3D Grounding 五大类共 40 项视觉基准，对比 Qwen3-VL 30B-A3B（MoE）与 32B（Dense，含 thinking/instruct 双模式）与 Gemini 2.5 Flash、GPT-5 mini。数据显示：Qwen3-VL-32B-thinking 在 MMMU（78.1）、MMBench-EN（89.5）、DocVQA（96.9）、InfoVQA（89.2）、MIA-Bench（92.3）等多项取得最高分，全面领先 Gemini 2.5 Flash，并在 STEM 与文档理解上多数超过 GPT-5 mini。

论文据此论证：原生分辨率编码 + DeepStack 多层融合 + Interleaved MRoPE 使中等规模模型即可在多模态推理、文档解析、长上下文（OCRBench_v2 计 855–903）上比肩甚至超越闭源旗舰。该表在论文实验链路中承担"中等规模竞争力验证"角色，为前述架构创新提供量化支撑，并衔接 Needle-in-a-Haystack（图3）的视频定位评测。

### Table 4 (p.18) ⭐深度解读
![[assets/crops/qwen3-vl-technical-report-tab04.png]]
> [!quote] caption
> Performance of small-sized Qwen3-VL models and GPT-5-nano on visual benchmarks.

> [!tip] 表格解读（多模态）
> 【图文联合解读】该表对比 Qwen3-VL 2B/4B/8B（thinking/instruct）与 GPT-5 nano 在 6 类视觉基准上的表现。核心数据：8B-thinking 在多数任务上显著领先 GPT-5 nano high，如 DocVQA（95.3 vs 88.2）、InfoVQA（86.0 vs 68.6）、ChartQA（88.6 vs 52.1）、OCRBench（819 vs 753）、MathVista（81.4 vs 71.5）、MIA-Bench（91.5 vs 89.9）。思考模式普遍优于指令模式；规模 2B→4B→8B 单调提升；GPT-5 nano 在 2D/3D Grounding 上无数据。该表论证 Qwen3-VL 小模型在文档理解、数学推理等任务已超越同级竞品 GPT-5 nano，是论文视觉能力评估的核心实证。

### Table 5 (p.21) ⭐深度解读
![[assets/crops/qwen3-vl-technical-report-tab05.png]]
> [!quote] caption
> Comparison among Qwen3-VL-235B-A22B (Instruct) and other baselines. The highest and second-best scores are shown in bold and underlined respectively.

> [!tip] 表格解读（多模态）
> 【图文联合解读】# Table 5 图文联合解读

**核心对象与数据**：对比 Qwen3-VL-235B-A22B (Instruct) 与 Qwen3 235B-A22B Instruct-2507、Deepseek V3 0324、Claude-Opus-4 共 4 个模型，在知识、推理、对齐、编程智能体、多语言 5 大类 17 项基准上的得分。关键亮点包括：推理维度 Qwen3-VL 在 AIME-25（74.7）、HMMT-25（57.4）大幅领先 Claude-Opus-4（33.9 / 15.9）；编程维度 LiveCodeBench v6 以 54.3 居首；多语言维度 MultiIF（76.3）与 MMLU-ProX（77.8）均夺第一。

**论证的技术结论**：Qwen3-VL 作为多模态模型在纯文本推理与编程任务上仍具强竞争力，未因视觉能力引入而牺牲 LLM 核心能力，并在多语言与数学推理上超越 Claude-Opus-4。

**论文中的作用**：作为旗舰模型整体能力的主对照表，是实验链路中"模型整体性能定位"的关键证据。

### Table 6 (p.22) ⭐深度解读
![[assets/crops/qwen3-vl-technical-report-tab06.png]]
> [!quote] caption
> Comparison among Qwen3-VL-235B-A22B (Thinking) and other reasoning baselines. The highest and second-best scores are shown in bold and underlined respectively.

> [!tip] 表格解读（多模态）
> 【图文联合解读】Table 6对比Qwen3-VL-235B-A22B(Thinking)与Qwen3-235B-A22B-Thinking-2507、OpenAI o3、Claude-Opus-4在知识/推理/代码/对齐/智能体/多语种6大类共21个基准上的表现。

核心数据：知识类MMLU-Pro 83.8略低于o3的85.9、SuperGPQA 64.3(次高)；推理LiveBench 79.6为四者最高，AIME-25 89.7居次；代码CFEval 1964、OJBench 27.5均第二；智能体TAU2-Airline 62.0(次高)、TAU2-Telecom 44.7；多语种PolyMATH 57.8(次高)显著优于o3的49.7。

论证结论：加入视觉模态后，Qwen3-VL在纯文本推理上仍逼近纯文本基线Qwen3-235B，并在LiveBench、PolyMATH等任务上反超o3，证实Thinking架构可向多模态无损扩展。

论文作用：与多模态基准表互补，构成"视觉-文本双优"的核心实验证据。

### Table 7 (p.22) ⭐深度解读
![[assets/crops/qwen3-vl-technical-report-tab07.png]]
> [!quote] caption
> Comparison among Qwen3-VL-32B-Instruct, Qwen3-VL-30B-A3B-Instruct, and corresponding baselines.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 7 图文联合解读**

该表跨知识（MMLU-Pro/Redux、GPQA、SuperGPQA）、推理（AIME-25、HMMT-25、LiveBench）、对齐（IFEval、Arena-Hard、写作）、代码/智能体（LiveCodeBench、BFCL）、多语言（MultiIF、MMLU-ProX、INCLUDE、PolyMATH）共 5 大类 17 项基准，对比 Qwen3-VL-32B、Qwen3-VL-30B-A3B 与同尺寸纯文本 Qwen3 基线及 30B-A3B-2507 版本。

核心结论有三：①视觉融合带来稳定增益——GPQA 上 VL-32B 达 68.9，较 Qwen3 32B（54.6）提升 14.3 分；SuperGPQA +11.4，AIME-25 由 20.2 跃升至 66.2。②MoE 版 VL-30B-A3B 在 GPQA（70.4）、PolyMATH（44.3）等任务上反超稠密 VL-32B，证明稀疏激活架构同样兼容视觉增强。③作为基线对照表，它在论文消融链路中量化论证"加视觉"对 Qwen3 全栈能力的普适提升，是支撑 VL 模型有效性的关键证据。

### Table 8 (p.23) ⭐深度解读
![[assets/crops/qwen3-vl-technical-report-tab08.png]]
> [!quote] caption
> Comparison among Qwen3-VL-32B (Thinking), Qwen3-VL-30B-A3B (Thinking), and corre- sponding baselines.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 8 图文联合解读：**

1) **结构与数据**：对比5个模型在6大类（知识/推理/编码/对齐/Agent/多语言）共21个基准上的表现。Qwen3-VL-32B(Thinking) 在MMLU-Pro(82.1)、GPQA(73.1)、AIME-25(83.7)、HMMT-25(64.6)、Arena-Hard V2(60.5)、TAU2-Telecom(46.9)、MultiIF(78.0) 等多数指标上领先；30B-A3B的MoE版本在激活参数仅3B的情况下，已逼近32B密集模型（如GPQA 74.4 vs 73.1、HMMT-25 67.6 vs 64.6）。

2) **关键结论**：视觉-语言融合显著增强Thinking模型的推理与Agent能力——VL版在TAU2三任务上较纯文本版提升超10–20分（Telecom: 46.9 vs 26.3）；且MoE架构配合Thinking+VL能在极低激活成本下复现稠密模型性能。

3) **作用**：作为论文核心实验链路，验证"Thinking + 视觉扩展 + MoE稀疏化"三重叠加的可行性，为Qwen3-VL系列旗舰与轻量版本的能力差异提供量化锚点。

### Table 11 (p.24) ⭐深度解读
![[assets/crops/qwen3-vl-technical-report-tab11.png]]
> [!quote] caption
> Ablation on Qwen3-ViT. We compare the performance metrics of Qwen3-ViT and SigLIP-2 during the CLIP pre-training stage, and further evaluate their downstream performance in the vision- language modeling (VLM) stage when paired with the same 1.7B Qwen3 language model.

> [!tip] 表格解读（多模态）
> 【图文联合解读】## Table 11 联合解读

**1) 核心对象与结构/数据**
该表横向对比 **SigLIP-2 vs Qwen3-ViT** 两个视觉编码器，分两组基准：① 预训练 CLIP Bench：ImageNet-1K/V2/A/R/S、ObjectNet、Omni 共 7 项；② 下游 VLM Bench：OCRB、AI2D、RLWDQA、InfoVQA、Omni 共 5 项（下游统一配 1.7B Qwen3 LLM）。定量上：CLIP 阶段两者基本持平——SigLIP-2 仅在 IN-R(96.1)、IN-S(76.2) 略胜；Qwen3-ViT 在 ImageNet-1K(84.6)、ObjectNet(81.0) 微优，**Omni 上大幅领先 +8.6（45.5 vs 36.9）**。VLM 阶段 Qwen3-ViT 五项**全面胜出**，RLWDQA 提升最大 **+7.4（66.1 vs 58.7）**。

**2) 关键结论**
Qwen3-ViT 在图文对齐预训练上不弱于、甚至在分布外任务上优于 SigLIP-2；更重要的是，作为 VLM 视觉塔时下游任务**全项稳定增益**，证明其为多模态理解生成而重设计的有效性。

**3) 论文链路中的作用**
位于 §5.12 视觉编码器消融，是验证 Qwen3-ViT 设计选型的核心证据表；与下方 §5.12.2 DeepStack 节共同支撑 Qwen3-VL 视觉前端的两大关键架构决策。

### Table 12 (p.24) ⭐深度解读
![[assets/crops/qwen3-vl-technical-report-tab12.png]]
> [!quote] caption
> Ablation on DeepStack. We conduct the ablation study on the DeepStack using an internal 15B- A2B LLM, with all experiments pretrained on 200 billion tokens. We directly evaluate these pretrained models on the validation sets, without any post-training.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 12 联合解读**

Table 12 对比 SigLIP-2 基线与启用 DeepStack 的 Qwen3-ViT，基于 15B-A2B LLM、以 200B tokens 预训练后直接评测。VLM Bench 上 Qwen3-ViT 全线提升：OCRB 77.2→78.7、AI2D 74.1→76.2、RLWDQA 58.7→66.1、InfoVQA 65.3→67.0、Omni 50.1→53.0；Clip Bench 中 Omni 由 36.9 跃升至 45.5（+8.6），ObjectNet 79.9→81.0 亦有增益。原文据此论证 DeepStack 通过融合多层视觉特征显著增强细粒度视觉理解能力，尤其在 InfoVQA、DocVQA 类文档任务上，是支撑其作为核心架构组件的消融验证证据。

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\frac{-b \pm \sqrt{b^2 - 4ac}}{2a}
$$

## 相关论文

- [[kimi-vl-technical-report]] — KIMI-VL TECHNICAL REPORT
- [[qwen2-5-vl-technical-report]] — Qwen2.5-VL Technical Report
- [[kimi-k2-5-visual-agentic-intelligence]] — KIMI K2.5: VISUAL AGENTIC INTELLIGENCE
- [[deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms]] — DeepStack: Deeply Stacking Visual Tokens is Surprisingly Simple and Effective for LMMs
- [[efficiently-serving-large-multimodal-models-using-epd-disaggregation]] — Efficiently Serving Large Multimodal Models Using EPD Disaggregation

## 技术点深读（DEEP）

![[deep/qwen3-vl-technical-report]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/qwen3-vl-technical-report.txt`（150008 字符）供引用检索。