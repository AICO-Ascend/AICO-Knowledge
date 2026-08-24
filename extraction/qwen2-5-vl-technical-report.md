---
paper_num: "40"
title: "Qwen2.5-VL Technical Report"
authors: "Qwen2.5-VL Technical Report Qwen Team, Alibaba Group"
date: "2026/1/5"
arxiv: "https://arxiv.org/abs/2502.13923"
pdf: "papers/qwen2-5-vl-technical-report.pdf"
slug: "qwen2-5-vl-technical-report"
tags: [multimodal]
---

# Qwen2.5-VL Technical Report

> [!abstract] 摘要（原文）
> 1\. ✨ Qwen2.5-VL 是 Qwen 视觉语言系列的最新旗舰模型，通过原生动态分辨率处理和基于绝对时间编码的多模态旋转位置嵌入（MRoPE），显著提升了对图像和超长视频的理解能力。 2. ⚙️ 该模型重新设计了 Vision Transformer (ViT) 架构，引入窗口注意力以优化计算效率，并将其预训练语料库扩展至 4.1 万亿 tokens，以增强性能。 3. 🏆 Qwen2.5-VL 在文档解析、精确对象定位、超长视频理解及代理功能方面表现出色，其旗舰 72B 模型在多项基准测试中与 GPT-4o 和 Claude 3.5 Sonnet 等顶尖模型媲美甚至超越。

## 元信息
- **发表日期**: 2026/1/5
- **作者**: Qwen2.5-VL Technical Report Qwen Team, Alibaba Group
- **arXiv**: https://arxiv.org/abs/2502.13923
- **本地 PDF**: `papers/qwen2-5-vl-technical-report.pdf`
- **页数**: 23

## 图表（原文 caption + 页码）

### Figure 1 (p.3) ⭐深度解读
![[assets/crops/qwen2-5-vl-technical-report-fig01.png]]
*整页渲染: ![[assets/qwen2-5-vl-technical-report-p03.png]]*
> [!quote] caption
> The Qwen2.5-VL framework demonstrates the integration of a vision encoder and a language model decoder to process multimodal inputs, including images and videos. The vision encoder is designed to handle inputs at their native resolution and supports dynamic FPS sampling. Images of varying sizes and video frames with different FPS rates are dynamically mapped to token sequences of varying lengths. 

> [!tip] 技术解读（多模态）
> 【图文联合解读】图示Qwen2.5-VL架构：Vision Encoder支持原生分辨率与动态FPS采样（0.5/1/2FPS），视频宽644、时长8s，经Conv3D(2×14×14)窗口划分与Conv2D 2×时序合并后映射成644/1288/2576可变长token；ViT块由Window Attention×M+Full Attention×1构成，配RMSNorm与SwiGLU FFN；3D MRoPE沿时间轴对齐绝对时间ID(0–15s)，最终输入Qwen2.5 LM Decoder。原文借此论证三大核心：原生分辨率保细节、动态采样提效率、绝对时间编码增强时序/时刻定位，作为全篇方法总纲，为后续视频理解与时间定位实验提供架构基线。

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.4) ⭐深度解读
![[assets/crops/qwen2-5-vl-technical-report-tab01.png]]
> [!quote] caption
> Configuration of Qwen2.5-VL.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 1 图文联合解读**

该表列出 Qwen2.5-VL 3B/7B/72B 三个规格的架构配置，分三大模块：ViT、Vision-Language Merger、LLM。

**ViT 三档完全一致**：Hidden Size 1280、32 层、16 头、Patch Size 14、Window Size 112；仅在 [7,15,23,31] 四块使用全注意力，其余采用窗口注意力。**Merger** 输入通道均为 1280（对齐 ViT），输出通道随 LLM 扩展为 2048/3584/8192。**LLM** Hidden Size 对应 2048/3584/8192，KV Heads 2/4/8，Head Size 固定 128；仅 3B 启用 Embedding Tying，词表 151646，三档统一训练 4.1T tokens。

**原文论证结论**：①视觉前端跨规模解耦复用，规模伸缩只发生在语言侧；②窗口注意力+稀疏全注意力降低原生分辨率处理成本；③Merger 通道与 LLM Hidden Size 严格对齐，保障变长 token 序列无损注入，配合 MRoPE 在时间维度编码绝对时间。

**论文作用**：作为后续消融与基准评测的工程锚点，支撑"统一视觉前端+可扩展语言后端"的可扩展性论证。

### Table 2 (p.8) ⭐深度解读
![[assets/crops/qwen2-5-vl-technical-report-tab02.png]]
> [!quote] caption
> Training data volume and composition across different stages.

> [!tip] 表格解读（多模态）
> 【图文联合解读】该表展示Qwen2.5-VL三阶段训练配置：①OCR预训练（1.5T tokens，序列长度8192，仅训ViT）；②VQA/Video Grounding/Agent对齐（2T tokens，8192，ViT与LLM联合训练）；③长文档/长智能体（0.6T tokens，序列扩至32768，联合训练）。论文据此论证关键结论：先以海量OCR数据单独预训练视觉编码器夯实基础，再联合LLM完成多模态对齐，最后通过序列长度从8K扩展到32K提升长上下文与Agent能力。该课程化三阶段设计构成Qwen2.5-VL整体方法链路的核心训练流程，解释了模型在文档理解、视频定位、智能体任务上能力涌现的数据与算力基础。

### Table 3 (p.11) ⭐深度解读
![[assets/crops/qwen2-5-vl-technical-report-tab03.png]]
> [!quote] caption
> Performance of Qwen2.5-VL and State-of-the-art.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**结构与数据：** 表以8列模型（Claude-3.5、GPT-4o-0513、InternVL2.5-78B、Qwen2.5-VL 72B/7B/3B及开源SoTA）横向对比20项基准，覆盖高校难题（MMMU/Pro）、数学（MathVista/MATH-Vision/MathVerse）与通用VQA（MMBench、MMStar、MMVet等）三大类。Qwen2.5-VL-72B在MMMU（70.2）、MathVista（74.8）、MATH-Vision（38.1）、MMStar（70.8）、MMVet（76.2）等多项居首并多处超越GPT-4o-0513。**论证结论：** 72B版本达开源SoTA并对标闭源旗舰，7B/3B亦保持强竞争力，验证规模—性能的有效平衡。**论文作用：** 作为性能主表支撑"Qwen2.5-VL全尺寸多任务SOTA"这一核心主张，是实验评估章节的定量总纲。

### Table 4 (p.12) ⭐深度解读
![[assets/crops/qwen2-5-vl-technical-report-tab04.png]]
> [!quote] caption
> Performance on pure text tasks of the 70B+ Instruct models and Qwen2.5-VL.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读**

表4横向比较5个70B+模型在10个纯文本基准上的表现。Qwen2.5-VL-72B在LiveBench-0831(57.0)、MultiPL-E(79.5)、IFEval(86.3)三项夺魁;Llama-3.1-405B在MMLU-Pro(73.3)、GPQA(51.1)、GSM8K(96.8)、HumanEval(89.0)最强;Qwen2.5-72B领跑MMLU-redux(86.8)与MATH(83.1)。

**技术结论**:多模态Qwen2.5-VL-72B在纯文本任务上与同尺寸乃至更大纯文本模型整体持平甚至略优,证明视觉融合训练未损害语言能力;视觉能力加入并未引发灾难性遗忘。

**论文作用**:作为"视觉引入不牺牲文本性能"的关键能力保持证据,与多模态基准形成"视觉+文本"双轮评估闭环,支撑论文核心主张——Qwen2.5-VL是真正统一的多模态大模型。

### Table 5 (p.13) ⭐深度解读
![[assets/crops/qwen2-5-vl-technical-report-tab05.png]]
> [!quote] caption
> Performance of Qwen2.5-VL and other models on OCR, chart, and document understanding benchmarks.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 5 图文联合解读**

Table 5 以7列×15行的矩阵对比 Claude-3.5 Sonnet、Gemini 1.5 Pro、GPT-4o、InternVL2.5-78B 与 Qwen2.5-VL（72B/7B/3B）在三类OCR任务上的得分。**关键数据**：Qwen2.5-VL-72B 在 CC-OCR（79.8）、DocVQA（96.4）、InfoVQA（87.3）、OCRBench（885）、OCRBench_v2 en/zh（61.5/63.7）均居首；7B 版在 VCR_En-Hard-EM（80.5）夺冠。原文借此论证 Qwen2.5-VL 文档/OCR 能力全面超越三大闭源 VLM，并形成"72B→7B→3B"的全尺度能力阶梯。该表是论文实验链路中的核心验证环节，以标准化基准坐实"通用视觉-文档理解"能力主张，为后续 agent、定位、长视频等任务的能力跃升提供底层依据。

### Table 6 (p.14) ⭐深度解读
![[assets/crops/qwen2-5-vl-technical-report-tab06.png]]
> [!quote] caption
> Performance of Qwen2.5-VL and other models on grounding.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

Table 6 对比了 Qwen2.5-VL（3B/7B/72B）与 Gemini 1.5 Pro、Grounding DINO、Molmo 72B、InternVL2.5 78B 在 Refcoco、Refcoco+、Refcocog、ODINW 与 PointGrounding 上的 grounding 性能。

**核心数据**：在 Refcoco 系列与 Refcocog 上，InternVL2.5 78B 领先（如 Refcoco_val 93.7、Refcocog_val 92.7），Qwen2.5-VL 72B 紧随其后（92.7/89.9），且明显优于 Gemini 1.5 Pro；ODINW 上 Grounding DINO 以 55.0 居首，Qwen2.5-VL 72B 达 43.1，反超 InternVL2.5（31.7）；PointGrounding 仅 Molmo（69.2）与 Qwen2.5-VL 系列（72B 67.5、7B 67.3、3B 58.3）支持。

**技术结论**：Qwen2.5-VL 以小参数（7B/3B）即可逼近 Gemini 1.5 Pro 等大模型在 grounding 上的表现，说明其 grounding 训练对模型规模依赖较低；同时是少数支持 point-based grounding 的模型，凸显细粒度定位能力。

**论文作用**：该表是论文实验章节中视觉 grounding 能力的关键实证，配合 object detection 与 OCR 等表格共同支撑 Qwen2.5-VL 在"绝对坐标"原生输出与多粒度定位上的核心卖点。

### Table 7 (p.14) ⭐深度解读
![[assets/crops/qwen2-5-vl-technical-report-tab07.png]]
> [!quote] caption
> Performance of Qwen2.5-VL and other models on counting.

> [!tip] 表格解读（多模态）
> 【图文联合解读】【说明】该表实测为视觉指代 grounding 基准（RefCOCO/+/g、ODinW、PointGrounding），与 caption 标注的"counting"及正文描述的 CountBench 不一致。以下按图像实际内容解读：

1) **结构与数据**：7 个模型 × 10 个 grounding 任务。Qwen2.5-VL-72B 在 Refcoco_val 达 92.7，逼近 InternVL2.5-78B（93.7）与 Grounding DINO（90.6）；7B/3B 同项得 90.0/89.1。Gemini 1.5 Pro 整体偏弱（Refcoco_val 仅 73.2）；ODinW 上 Grounding DINO 以 55.0 领先，Qwen2.5-VL-72B 为 43.1；PointGrounding 上 Molmo-72B 居首（69.2），Qwen2.5-VL-72B 为 67.5。

2) **技术结论**：72B 版本在主流 grounding 基准接近 SOTA，且 3B/7B 小模型仍具可用定位能力，体现系列对"看图指物"细粒度任务的竞争力。

3) **论文作用**：作为视觉定位能力的关键证据，支撑目标引用、GUI Agent 等下游应用，与论文"原生动态分辨率+绝对坐标输出"的技术路线相互印证。

### Table 8 (p.14) ⭐深度解读
![[assets/crops/qwen2-5-vl-technical-report-tab08.png]]
> [!quote] caption
> Performance of Qwen2.5-VL and other models on video benchmarks.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**核心对象与结构**：Table 8 以矩阵形式对比 5 个模型（Gemini 1.5-Pro、GPT-4o、Qwen2.5-VL-72B/7B/3B）在 11 项视频理解任务（Video-MME、Video-MMMU、MMVU、MVBench、MMBench-Video、LongVideoBench、LVBench、EgoSchema、PerceptionTest、MLVU、TempCompass）与 1 项视频定位任务（Charades-STA mIoU）上的得分。Qwen2.5-VL-72B 在 8 项粗体夺魁，含 LVBench 47.3、EgoSchema 76.2、MLVU 74.6、Charades-STA 50.9；Gemini 1.5-Pro 领跑 Video-MME（75.0/81.3），GPT-4o 拿下 Video-MMMU 61.2、MMVU 67.4、LongVideoBench 66.7。

**关键结论**：72B 模型在长视频与时序定位任务上全面超越同级别闭源模型，验证了绝对时间戳编码与多模态 RoPE 对小时级视频理解/接地（grounding）的有效性；3B→7B→72B 性能单调提升，体现良好可扩展性。

**链路作用**：作为视频能力主评测表，与静态图像、OCR 评测共同支撑"原生统一 VL 模型覆盖长视频、文档、定位"这一核心技术主张。

### Table 9 (p.15) ⭐深度解读
![[assets/crops/qwen2-5-vl-technical-report-tab09.png]]
> [!quote] caption
> Performance of Qwen2.5-VL and other models on GUI Agent benchmarks.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**核心对象与数据**：表9对比GPT-4o、Gemini 2.0、Claude、Aguvis-72B、Qwen2-VL-72B、Qwen2.5-VL-72B六款VLM在7项GUI Agent基准上的表现，分离线定位（ScreenSpot/Pro、Android Control High/Low EM）与在线成功率（AndroidWorld、MobileMiniWob++、OSWorld）两类。Qwen2.5-VL-72B在ScreenSpot Pro（43.6 vs 次优Aguvis 23.6）、Android Control Low（93.7 vs 84.4）、AndroidWorld（35%）、MobileMiniWob++（68%）上居首。

**关键结论**：证明其原生屏幕坐标定位能力——在AndroidWorld、MobileMiniWob++上**无需SoM**即超越依赖SoM的GPT-4o、Gemini、Claude；相对Qwen2-VL-72B代际跃升明显（ScreenSpot Pro 1.6→43.6，OSWorld 2.42→8.83）。

**论文作用**：作为"视觉识别→界面操作"能力升级的核心实验证据，与视觉定位、长视频理解等表共同支撑Qwen2.5-VL的GUI Agent卖点。

## 相关论文

- [[qwen3-vl-technical-report]] — Qwen3-VL Technical Report
- [[kimi-vl-technical-report]] — KIMI-VL TECHNICAL REPORT
- [[kimi-k2-5-visual-agentic-intelligence]] — KIMI K2.5: VISUAL AGENTIC INTELLIGENCE
- [[deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms]] — DeepStack: Deeply Stacking Visual Tokens is Surprisingly Simple and Effective for LMMs
- [[efficiently-serving-large-multimodal-models-using-epd-disaggregation]] — Efficiently Serving Large Multimodal Models Using EPD Disaggregation

## 技术点深读（DEEP）

![[deep/qwen2-5-vl-technical-report]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/qwen2-5-vl-technical-report.txt`（91584 字符）供引用检索。