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
> 【图文联合解读】图1展示Qwen2.5‑VL的统一多模态链路：视觉编码器以窗口划分、3D卷积（2×14×14）及窗口/全注意力处理原生分辨率图像/视频，将视觉Token与文本Token送入Qwen2.5 LM解码器。1092×8204、224×28、1260×700图像分别产生11427、8、1125 Token；644×392视频随动态FPS产生644/1288/2576 Token。该图说明尺寸和帧率可弹性转为变长序列，是多模态训练与评测的输入基础。

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.4) ⭐深度解读
![[assets/crops/qwen2-5-vl-technical-report-tab01.png]]
> [!quote] caption
> Configuration of Qwen2.5-VL.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读（≤220字）**

表1给出Qwen2.5-VL的3B/7B/72B三档配置，分**ViT**、**视觉-语言Merger**、**LLM**三模块。ViT在三档间**完全统一**：隐藏维1280、32层、patch 14、窗口112、全注意力块固定为{7,15,23,31}，体现"窗口注意力+稀疏全注意力"的可复用视觉骨干。Merger的Out Channel（2048/3584/8192）严格对齐LLM Hidden Size，保证跨模态表征贯通。LLM层数36/28/80呈非单调分布（72B最深80层），KV头2/4/8，仅3B启用Embedding Tying，词表151646、三档统一训练4.1T token。该表佐证Figure 1所述"原生分辨率+动态FPS"由统一ViT配合窗口注意力实现，并锁定了视觉通道与语言模型对齐的架构基线，为后续多模态实验提供可比对照。

### Table 2 (p.8) ⭐深度解读
![[assets/crops/qwen2-5-vl-technical-report-tab02.png]]
> [!quote] caption
> Training data volume and composition across different stages.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 2 联合解读：**

该表呈现 Qwen2.5-VL 三个训练阶段的数据配置：①OCR 阶段 1.5T tokens、序列长 8192、仅训 ViT；②VQA/Video Grounding/Agent 阶段 2T tokens、序列长 8192、ViT 与 LLM 联合训练；③Long Agent/Long Document 阶段 0.6T tokens、序列长跃升至 32768、仍为 ViT 与 LLM 联合训练。

论文借此论证：(a) 训练采用**渐进式数据扩增与能力递进**策略，从纯视觉编码器预训练逐步过渡到多模态联合训练；(b) 第三阶段将上下文窗口扩至 4 倍（8192→32768），专门强化长文档与 Agent 长程任务能力。

在全篇方法链中，该表是**训练配方的总览**，与后续各阶段的能力评测（如 OCR、VQA、视频、长上下文基准）形成"数据-能力"对应关系，支撑模型多阶段能力涌现的叙事。

### Table 3 (p.11) ⭐深度解读
![[assets/crops/qwen2-5-vl-technical-report-tab03.png]]
> [!quote] caption
> Performance of Qwen2.5-VL and State-of-the-art.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

该表在4大类共19个基准上，将Qwen2.5-VL（3B/7B/72B）与Qwen2-VL-72B及Claude-3.5、GPT-4o、InternVL2.5-78B、此前开源SoTA进行横向对比。量化结果显示：Qwen2.5-VL-72B在多数任务上达到领先水平，如MathVista 74.8、MMStar 70.8、CRPE 79.2、MMVet⁺ᵗᵘʳᵇᵒ 76.2，并刷新MathVerse(57.6)、MMBench-CN(87.9)、MMEsum(2448)等开源SoTA。

原文借此论证两点关键结论：①Qwen2.5-VL-72B已能与闭源旗舰在通用VQA、数学推理与大学级问题上比肩甚至超越；②其3B/7B小尺寸仍保持强竞争力，体现架构与训练优化带来的高效扩展性。

该表作为第11页核心实验总览，是论文整体方法链路的事实检验环节：将视觉编码器、MLP融合及动态分辨率等设计在多任务综合基准上落地为可量化的性能声明，为后续消融与下游应用讨论提供基线支撑。

### Table 4 (p.12) ⭐深度解读
![[assets/crops/qwen2-5-vl-technical-report-tab04.png]]
> [!quote] caption
> Performance on pure text tasks of the 70B+ Instruct models and Qwen2.5-VL.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 4 图文联合解读**

**1) 核心数据**：该表对比 Llama-3.1-70B/405B、Qwen2-72B、Qwen2.5-72B 与 Qwen2.5-VL-72B 在四大类共9个纯文本基准上的得分。Qwen2.5-VL-72B 在 LiveBench-0831（**57.0** vs 53.2）、MultiPL-E（**79.5** vs 75.1）、IFEval（**86.3** vs 86.0）三项领先；MMLU-Pro（71.2）、MATH（83.0）与 Qwen2.5-72B 基本持平；MMLU-redux（85.9）、GSM8K（95.3）、HumanEval（87.8）略低 0.1–1.4 分。

**2) 关键结论**：加入视觉模态后，Qwen2.5-VL-72B 相对 Qwen2.5-72B 未出现文本能力退化，部分指标反超，且综合表现优于 Llama-3.1-70B、与 Llama-3.1-405B 可比，证明多模态扩展未牺牲纯文本能力。

**3) 链路作用**：作为消融/能力保持证据，支撑论文"统一视觉-语言架构不损害 LLM 基础能力"的核心主张，为后续视觉理解、文档解析等任务的优越表现提供合法性背书。

### Table 5 (p.13) ⭐深度解读
![[assets/crops/qwen2-5-vl-technical-report-tab05.png]]
> [!quote] caption
> Performance of Qwen2.5-VL and other models on OCR, chart, and document understanding benchmarks.

> [!tip] 表格解读（多模态）
> 【图文联合解读】Table 5以7列×15行结构对比Qwen2.5-VL（72B/7B/3B）与Claude-3.5、Gemini 1.5 Pro、GPT-4o、InternVL2.5-78B。**关键数据**：72B版在CC-OCR(79.8)、DocVQA(96.4)、InfoVQA(87.3)、OCRBench(885)、OCRBench_v2 en/zh(61.5/63.7)共5项居首；7B版于VCR_En-Hard-EM(80.5)夺冠；3B版OmniDocBench_edit(0.409/0.543)亦优于多数对手。原文借此论证Qwen2.5-VL文档/OCR能力全面超越三大闭源VLM，形成72B→7B→3B全尺度能力阶梯。该表是论文实验链路核心验证环节，以标准化基准坐实"通用视觉-文档理解"能力主张，为后续agent、定位、长视频等任务的能力跃升提供底层依据。

### Table 6 (p.14) ⭐深度解读
![[assets/crops/qwen2-5-vl-technical-report-tab06.png]]
> [!quote] caption
> Performance of Qwen2.5-VL and other models on grounding.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**核心对象与数据**
Table 6 对比 Qwen2.5-VL（3B/7B/72B）与 Gemini 1.5 Pro、Grounding DINO、Molmo 72B、InternVL2.5-78B 在 5 类 grounding 基准上的表现。Qwen2.5-VL-72B 在 Refcoco val/testA/testB 达 92.7/94.6/89.7，逼近 InternVL2.5-78B 最高值（95.6），显著高于 Gemini（72-77）；ODINW 上 72B 为 43.1，仅次于专用 Grounding DINO（55.0），却超过 InternVL2.5（31.7）；PointGrounding 67.5，与 Molmo-72B 的 69.2 接近；3B→72B 在各基准上大体单调提升。

**关键结论**
证明 Qwen2.5-VL 无需外挂检测器即具备原生强 grounding 能力，可与专用定位/同规模开源模型正面对抗，并在开放域 ODINW 上展现优于通用多模态基线的跨场景泛化。

**在论文中的作用**
与文档理解、视频、OCR、Object365 等评测并列，构成 Qwen2.5-VL"全能视觉大模型"定位的多维证据链，凸显其在 grounding 这一细粒度感知任务上的竞争力。

### Table 7 (p.14) ⭐深度解读
![[assets/crops/qwen2-5-vl-technical-report-tab07.png]]
> [!quote] caption
> Performance of Qwen2.5-VL and other models on counting.

> [!tip] 表格解读（多模态）
> 【图文联合解读】Table 7对比Qwen2.5-VL（72B/7B/3B）与Gemini 1.5 Pro、Grounding DINO、Molmo 72B、InternVL2.5 78B在Refcoco系列、ODinW、PointGrounding共12项定位/指代表（注：caption误标为counting）上的得分。关键结论：① 72B全面接近InternVL2.5-78B，如Refcoco+testB 83.7 vs 86.9、Refcoco_testA 94.6 vs 95.6；② 7B/3B大幅优于Gemini（Refcoco_val 90.0/89.1 vs 73.2）；③ PointGrounding上72B达67.5，逼近专用模型Molmo 72B（69.2），远超InternVL2.5；④ ODinW中Grounding DINO仍领先（55.0），但Qwen2.5-VL-72B（43.1）显著超过Gemini与InternVL2.5。该表证明Qwen2.5-VL具备与SOTA相当的细粒度视觉定位能力，并具强尺寸可扩展性，是论文视觉感知/接地能力评估链路的核心证据。

### Table 8 (p.14) ⭐深度解读
![[assets/crops/qwen2-5-vl-technical-report-tab08.png]]
> [!quote] caption
> Performance of Qwen2.5-VL and other models on video benchmarks.

> [!tip] 表格解读（多模态）
> 【图文联合解读】Table 8 对比5模型在12项视频任务。Qwen2.5-VL-72B夺8项魁：MVBench 70.4、LVBench 47.3、EgoSchema 76.2、MLVU 74.6、TempCompass 74.8、Charades-STA 50.9等；Gemini 1.5-Pro领跑Video-MME（75.0/81.3），GPT-4o拿下Video-MMMU 61.2、MMVU 67.4、LongVideoBench 66.7。论文借此论证Qwen2.5-VL-72B视频理解与时序定位整体超越GPT-4o与Gemini 1.5-Pro，确立开源SOTA；该表与图像、OCR、Agent基准互补，构成全模态评测链路核心证据，支撑"统一视觉语言大模型"主张。

### Table 9 (p.15) ⭐深度解读
![[assets/crops/qwen2-5-vl-technical-report-tab09.png]]
> [!quote] caption
> Performance of Qwen2.5-VL and other models on GUI Agent benchmarks.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 9 图文联合解读**

**1) 核心结构与数据**：表横向对比 6 个模型（GPT-4o、Gemini 2.0、Claude、Aguvis-72B、Qwen2-VL-72B、Qwen2.5-VL-72B），纵向覆盖 7 项 GUI Agent 基准。Qwen2.5-VL-72B 在 6 项中取得最佳：ScreenSpot Pro 43.6（vs Claude 17.1）、Android Control High 67.36（vs Aguvis 66.4）、Low 93.7（vs Aguvis 84.4）、AndroidWorld_SR 35%（vs GPT-4o 34.5%）、MobileMiniWob++_SR 68%（vs Aguvis 66%）；仅 ScreenSpot（87.1 vs Aguvis 89.2）与 OSWorld（8.83 vs Claude 14.90）未居首。

**2) 关键结论**：Qwen2.5-VL-72B 在通用 GUI 任务上同时超越开源（Aguvis）与闭源旗舰（GPT-4o、Gemini 2.0、Claude），相对前代 Qwen2-VL-72B 取得大幅跃升，证明新一代模型在屏幕理解与操作定位上的实质进步。

**3) 论文中的作用**：作为应用层实验的核心证据，验证模型在真实 GUI Agent 场景的可用性，与文档/视频/OCR 基准共同构成对"通用视觉-语言-动作"能力的全方位论证。

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