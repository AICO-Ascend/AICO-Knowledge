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

1) **核心对象与数据**：柱状图按升序展示模型在自建多语言OCR测试集上的准确率（%）。可见语言包括罗马尼亚语、斯瓦希里语、俄语、印地语、希伯来语、波兰语、Catanzarro、意大利语、德语、越南语、乌克兰语、乌兹别克语、西班牙语、法语、葡萄牙语、日语等；准确率范围约71%–84%，其中拉丁/日耳曼语族（葡、法、西、日）达到83–84%的最高档，东欧与南亚语种处于71–74%最低档。

2) **关键结论**：39种支持语言中有32种准确率超70%，证明Qwen3-VL具备"实用级"多语种OCR能力，而非仅覆盖主流语言。

3) **链路作用**：作为能力广度证据，补强论文"OCR相关VQA达到SOTA"的核心论点，体现模型在文档理解与多语言场景下的泛化优势。

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

Table 2 横向对比 Qwen3-VL-235B-A22B（thinking/instruct）与 Gemini 2.5 Pro、GPT-5、Claude Opus 4.1 在 STEM Puzzle、General VQA、Alignment、Document Understanding、2D/3D Grounding 五大类共约 40 项视觉基准上的得分。

**关键数据亮点**：
- **STEM**：Qwen3-VL-thinking 在 MathVistaₘᵢₙᵢ 达 85.8（全表最高）、MathVision 74.6、DynaMath 82.8、ZeroBench 4（满分级最高）；
- **文档/OCR-VQA**：DocVQA 96.5、InfoVQA 89.5、OCRBench 875、CC-OCR 81.5 均为四模型榜首；
- **2D/3D Grounding**：RefCOCO-avg 92.1 远超 Gemini 74.6，CountBench 93.7 领先，ODinW/ARKitScenes/Hypersim/SUNRGBD 全网独占。

**论证作用**：原文借该表佐证 Qwen3-VL-Instruct 在 OCR-VQA 上微幅超越其 Thinking 版本，确立新的 SOTA；同时系统展示了 Qwen3-VL 在文档理解与空间感知上对 GPT-5、Claude 4.1 的差异化优势，是支撑"全能视觉-语言模型"定位的核心实验证据。

### Table 3 (p.16) ⭐深度解读
![[assets/crops/qwen3-vl-technical-report-tab03.png]]
> [!quote] caption
> Performance of medium-sized Qwen3-VL models and previous models on visual benchmarks. The highest scores are shown in bold . Results marked with an ∗ are sourced from the technical report. + denotes results with tool use.

> [!tip] 表格解读（多模态）
> 【图文联合解读】表3对比Qwen3-VL 30B-A3B/32B（thinking/instruct）、Gemini 2.5 Flash、GPT-5 mini在38项视觉基准上的表现。Qwen3-VL 32B thinking在STEM类多项领先（MathVista 85.9、MathVerse 82.6、DynaMath 82.0、We-Math 71.6），Document Understanding全面占优（OCRBench 903、OCRBench_v2_en 68.4、OCRBench_v2_zh 62.1），General VQA的MMBench-EN 89.5、MMStar 79.4亦最优；GPT-5 mini high仅在MMMU 79.0、MathVision 71.9等少数项目胜出。

论文借此论证：中等规模Qwen3-VL在视觉理解、OCR与跨模态推理上已对标甚至超越闭源旗舰Gemini 2.5 Flash与GPT-5 mini。该表与Figure 3长视频NIAH热力图互补——前者覆盖广度（多任务benchmark），后者刻画深度（长上下文检索）——共同支撑论文"多尺度、全能强视觉"的整体叙事。

### Table 4 (p.18) ⭐深度解读
![[assets/crops/qwen3-vl-technical-report-tab04.png]]
> [!quote] caption
> Performance of small-sized Qwen3-VL models and GPT-5-nano on visual benchmarks.

> [!tip] 表格解读（多模态）
> 【图文联合解读】Table 4对比Qwen3-VL 2B/4B/8B（thinking/instruct双模式）与GPT-5 nano（high/minimal）在STEM、通用VQA、对齐、文档理解、2D/3D定位5类共39项视觉基准上的表现。数据显示：Qwen3-VL 8B thinking在文档理解上大幅领先GPT-5 nano high（DocVQA 95.3 vs 88.2、ChartQA 88.6 vs 52.1、OmniDocBench 0.209 vs 0.401），通用VQA亦胜（MMBench-EN 85.3 vs 78.4），STEM推理GPT-5 nano略胜（MMMU 75.8 vs 74.1）；同模型thinking普遍优于instruct；GPT-5 nano在定位任务无数据。该表论证小尺寸Qwen3-VL已可对标闭源旗舰，是实验链路的核心证据。

### Table 5 (p.21) ⭐深度解读
![[assets/crops/qwen3-vl-technical-report-tab05.png]]
> [!quote] caption
> Comparison among Qwen3-VL-235B-A22B (Instruct) and other baselines. The highest and second-best scores are shown in bold and underlined respectively.

> [!tip] 表格解读（多模态）
> 【图文联合解读】该表将Qwen3-VL-235B-A22B(Instruct)与旧版Qwen3-VL、纯文本Qwen3、Deepseek V3、Claude-Opus-4置于5大类18个基准上横评。量化亮点：VL版在推理(AIME-25 74.7、HMMT-25 57.4，均远超Claude的33.9/15.9)、代码(LiveCodeBench v6 54.3最高)与多语言(PolyMATH 45.1 vs Deepseek 32.2)居首；知识类仍由Claude领跑(MMLU-Pro 86.6、GPQA 74.9)，对齐任务与Qwen3基本持平。论文借此论证新旗舰VL模型相对纯文本版及最强闭源模型具综合竞争力，并验证视觉融合对推理与代码能力增益最显著。

### Table 6 (p.22) ⭐深度解读
![[assets/crops/qwen3-vl-technical-report-tab06.png]]
> [!quote] caption
> Comparison among Qwen3-VL-235B-A22B (Thinking) and other reasoning baselines. The highest and second-best scores are shown in bold and underlined respectively.

> [!tip] 表格解读（多模态）
> 【图文联合解读】该表对比 Qwen3-VL-235B-A22B（Thinking）与 Qwen3-235B-A22B、o3 (medium)、Claude-Opus-4 在知识/推理/代码/对齐/Agent/多语言 6 大类 22 项基准的表现。Qwen3-VL 在 LiveBench（79.6 最佳）、HMMT-25（77.4 次优）、PolyMATH（57.8 次优）、TAU2-Airline（62.0 最佳）等多项进入前二，推理与代码能力贴近纯文本版；但知识类（MMLU-Pro 83.8 < 85.9）、对齐类明显逊于 o3。该表论证：引入视觉模态未削弱文本推理，Qwen3-VL 在多类任务上已具备与顶级推理模型抗衡的实力，是论文定位 VL 模型综合能力的核心对照证据。

### Table 7 (p.22) ⭐深度解读
![[assets/crops/qwen3-vl-technical-report-tab07.png]]
> [!quote] caption
> Comparison among Qwen3-VL-32B-Instruct, Qwen3-VL-30B-A3B-Instruct, and corresponding baselines.

> [!tip] 表格解读（多模态）
> 【图文联合解读】表7横向对比Qwen3-VL-32B/30B-A3B与对应纯文本基线Qwen3 32B/30B-A3B及旧版2507，覆盖知识、推理、对齐、代码、多语言5类共15项基准。数据显示VL版本全面超越同规模文本基线：推理增益最显著（AIME-25 20.2→66.2、HMMT-25 10.9→46.1），知识类GPQA 54.6→68.9、SuperGPQA 43.2→54.6，代码LiveCodeBench 29.1→43.8，多语PolyMATH 22.5→40.5。该表为论文提供核心定量证据：证明引入视觉通路不仅未损纯文本能力，反而在多任务上带来增益，支撑Qwen3-VL多模态扩展方案的合理性与有效性。

### Table 8 (p.23) ⭐深度解读
![[assets/crops/qwen3-vl-technical-report-tab08.png]]
> [!quote] caption
> Comparison among Qwen3-VL-32B (Thinking), Qwen3-VL-30B-A3B (Thinking), and corre- sponding baselines.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**核心对象与结构**：该表横向对比5个模型——Qwen3-VL-32B/30B-A3B(Thinking)与3个纯文本基线(Qwen3-32B-Thinking、Qwen3-30B-A3B-Thinking、Qwen3-30B-A3B-Thinking-2507)——在6大类19个基准(Knowledge/Reasoning/Coding/Alignment/Agent/Multilingualism)上的得分。

**关键数据与结论**：VL版本普遍领先同尺寸文本基线。Qwen3-VL-32B-Thinking对比Qwen3-32B-Thinking：GPQA 73.1 vs 68.4(+4.7)、AIME-25 83.7 vs 72.9(+10.8)、HMMT-25 64.6 vs 51.8、TAU2-Telecom 46.9 vs 26.3(+20.6)、Arena-Hard V2 60.5 vs 50.3；30B-A3B组VL版本TAU2-Retail 64.0 vs 34.2(+29.8)、TAU2-Airline 48.0 vs 36.0(+12)。仅CFEval(1842 vs 1986)、OJBench(20.0 vs 24.1)等纯编码任务略弱于文本基线。

**实验链作用**：作为消融对照，量化视觉融合对Thinking模型各能力维度的增益边界，论证VL版本相对纯文本同尺寸基线的整体优势，并明示纯编码场景的取舍。

### Table 11 (p.24) ⭐深度解读
![[assets/crops/qwen3-vl-technical-report-tab11.png]]
> [!quote] caption
> Ablation on Qwen3-ViT. We compare the performance metrics of Qwen3-ViT and SigLIP-2 during the CLIP pre-training stage, and further evaluate their downstream performance in the vision- language modeling (VLM) stage when paired with the same 1.7B Qwen3 language model.

> [!tip] 表格解读（多模态）
> 【图文联合解读】该表对比 SigLIP-2 与 Qwen3-ViT 两个视觉编码器（均配 1.7B Qwen3 LM）。CLIP 阶段两者相当，但 Qwen3-ViT 的 Omni 指标从 36.9 升至 45.5（+8.6）；VLM 阶段五项任务全面领先，RLWDQA 提升最显著（58.7→66.1，+7.4），OCR/文档类（OCRB、InfoVQA）亦有可观增益。论证结论：Qwen3-ViT 在图文对齐上与 SigLIP-2 持平，在下游 VLM 任务（尤其文字识别与文档理解）上显著更优。该消融支撑了论文以自研 Qwen3-ViT 取代 SigLIP-2 作为 Qwen3-VL 视觉骨干的选型决策。

### Table 12 (p.24) ⭐深度解读
![[assets/crops/qwen3-vl-technical-report-tab12.png]]
> [!quote] caption
> Ablation on DeepStack. We conduct the ablation study on the DeepStack using an internal 15B- A2B LLM, with all experiments pretrained on 200 billion tokens. We directly evaluate these pretrained models on the validation sets, without any post-training.

> [!tip] 表格解读（多模态）
> 【图文联合解读】图文不匹配：图实际展示 SigLIP-2 与 Qwen3-ViT 在 Clip Bench（7项：ImageNet-1K/V2/A/R/S、ObjectNet、Omni）与 VLM Bench（5项：OCRB、AI2D、RLWDQA、InfoVQA、Omni）的对比，并非 DeepStack 消融。

**量化结论**：Qwen3-ViT 在 VLM Bench 全面领先——RLWDQA **+7.4**（66.1 vs 58.7）、InfoVQA +1.7、AI2D +2.1、OCRB +1.5、Omni +2.9；Clip Bench 中 Omni 显著 **+8.6**（45.5 vs 36.9），ObjectNet +1.1，仅 ImageNet-R（-0.4）/ImageNet-S（-1.7）略低。

**原文 Table 12 真正意图**：比较 Baseline 与 DeepStack，论证多层视觉特征融合对细粒度理解（InfoVQA、DocVQA）的有效性。该表在论文中支撑 DeepStack 作为核心架构组件的设计选择，属于消融验证环节。

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