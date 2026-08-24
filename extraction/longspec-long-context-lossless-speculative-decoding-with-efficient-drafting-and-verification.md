---
paper_num: "59"
title: "LongSpec: Long-Context Lossless Speculative Decoding with Efficient Drafting and Verification"
authors: "with Efficient Drafting and Verification Penghui Yang2*, Cunxiao Du1*, Fengzhuo Zhang3, Haonan Wang3, Tianyu Pang1, Chao Du1, Bo An2 1 Sea AI Lab, 2 Nanyang Technological University, 3 National University of Singapore ph"
date: "2025/2/24"
arxiv: "https://arxiv.org/abs/2502.17421"
pdf: "papers/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification.pdf"
slug: "longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification"
tags: [speculative, long-context]
---

# LongSpec: Long-Context Lossless Speculative Decoding with Efficient Drafting and Verification

> [!abstract] 摘要（原文）
> As Large Language Models (LLMs) can now process extremely long contexts, efficient inference over these extended inputs has become increasingly important, especially for emerging applications like LLM agents that highly depend on this capability. Speculative decoding (SD) offers a promising lossless acceleration technique compared to lossy alternatives such as quantization and model cascades. However, most state-of-the-art SD methods are trained on short texts (typically fewer than 4k tokens), making them unsuitable for long-context scenarios. Specifically, adapting these methods to long contexts presents three key challenges: (1) the excessive memory demands posed by draft models due to large Key-Value (KV) cache; (2) performance degradation resulting from the mismatch between short-context training and long-context inference; and (3) inefficiencies in tree attention mechanisms when managing long token sequences. This work introduces LongSpec, a framework that addresses these challenges through three core innovations: a memory-efficient draft model with a constant-sized KV cache; novel position indices that mitigate the training-inference mismatch; and an attention aggregation strategy that combines fast prefix computation with standard tree attention to enable efficient decoding. Experimental results confirm the effectiveness of LongSpec, achieving up to a 3.26x speedup over strong Flash Attention baselines across five long-context understanding datasets, as well as a 2.25x reduction in wall-clock time on the AIME24 long reasoning task with the QwQ model, demonstrating significant latency improvements for long-context applications. The code is available at this https URL.

## 元信息
- **发表日期**: 2025/2/24
- **作者**: with Efficient Drafting and Verification Penghui Yang2*, Cunxiao Du1*, Fengzhuo Zhang3, Haonan Wang3, Tianyu Pang1, Chao Du1, Bo An2 1 Sea AI Lab, 2 Nanyang Technological University, 3 National University of Singapore ph
- **arXiv**: https://arxiv.org/abs/2502.17421
- **本地 PDF**: `papers/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification.pdf`
- **页数**: 19

## 图表（原文 caption + 页码）

### Figure 1 (p.1) ⭐深度解读
![[assets/crops/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-fig01.png]]
*整页渲染: ![[assets/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-p01.png]]*
> [!quote] caption
> The SoTA SD method, EAGLE, has a training context length of 2048, which is significantly shorter than the context lengths of modern LLMs. 2023), and their ability to handle extensive con- texts is becoming crucial for emerging applications such as LLM agents and long reasoning tasks (Tan et al., 2025; Guo et al., 2025), which now oper- ate over context windows extending to millions of tokens (Team

> [!tip] 技术解读（多模态）
> 【图文联合解读】**1) 核心对象与数据**
对数刻度柱状图（y 轴 2k→10M），对比 7 个前沿 LLM 的上下文窗口：DeepSeek-V3、Qwen3-235B-A22B 约 128k；Claude 3.7 Sonnet 约 200k；Grok 3、GPT-4.1、Gemini 2.5 Pro 约 1M；Llama 4 Scout 约 10M（最高）。红色虚线标 2k，为 EAGLE 训练上下文长度。

**2) 关键结论**
现代 LLM 实际上下文窗口为 EAGLE 训练长度的 **64×~5000×**，EAGLE 根本无法覆盖真实长上下文场景，直接迁移将失效。

**3) 论文作用**
作为核心动机图，揭示 SOTA 推测解码方法在长上下文下的根本局限，为 LongSpec（长上下文无损推测解码）的研究必要性提供直观量化依据。

### Figure 2 (p.4) ⭐深度解读
![[assets/crops/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-fig02.png]]
*整页渲染: ![[assets/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-p04.png]]*
> [!quote] caption
> Illustration of the memory-efficient draft model, the Anchor-Offset Indices, and the Hybrid Tree Attention. (a) We use a sliding window self-attention layer to capture the local context information and a cross-attention layer to gather long-context information. (b) The differences between the vanilla indexing and the Anchor-Offset

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图(a)展示内存高效草稿模型：对输入"deep"用定长3-token窗口（gaunt/with/deep）做局部自注意力，再通过交叉注意力读取Target LLM的历史KV缓存，最终经LM Head预测"wrinkles"，实现以小内存消费长上下文。图(b)对比Vanilla索引（大间隔如0,1,2,803）与Anchor-Offset索引（锚点0-3+偏移段如10204-11221、30004-30055），证明后者能将短文本训练的位置分布拉近长文本训练，显著缩小能力Gap。图(c)将Flash Attention（全✓的prefix快路径）与Mask Attention（按speculative tree掩码的灵活路径）合并为Hybrid Attention。三组件分别解决草稿建模内存、训练分布对齐、树形验证效率问题，共同支撑LongSpec在长上下文下的无损推测解码。

### Figure 3 (p.7) ⭐深度解读
![[assets/crops/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-fig03.png]]
*整页渲染: ![[assets/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-p07.png]]*
> [!quote] caption
> Decoding speed (tokens/s) across different models and settings. All results are computed at T = 1. The letters G, Q, M, L, and R on the horizontal axis represent the datasets GovReport, QMSum, Multi-News, LCC, and

> [!tip] 技术解读（多模态）
> 【图文联合解读】图3以5子图×5数据集（G/Q/M/L/R）柱状对比LongSpec（深蓝）与MagicDec（浅蓝）在T=1下的解码速度（tokens/s），覆盖Vicuna-7B/13B、LongChat-7B/13B与LLaMA-3.1-8B。LongSpec在所有25组组合中均显著领先：7B/8B模型实现约2.4–2.5×加速（如LongChat-7B在LCC：51→124 tokens/s，Vicuna-7B在LCC：50→119），13B模型约2×加速（如LongChat-13B在LCC：37→93）。该图证明其高效草稿生成与验证机制在跨模型、跨长文任务下稳定有效，是论文实验链路中支撑"长上下文无损加速"结论的核心证据。

### Figure 4 (p.8) ⭐深度解读
![[assets/crops/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-fig04.png]]
*整页渲染: ![[assets/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-p08.png]]*
> [!quote] caption
> Training loss curves on long-context data.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图中展示长上下文训练过程中两条Loss曲线（横轴Steps 0–1200）：红色为启用了Anchor-Offset Indices的预训练模型，初始Loss约4.2并快速收敛至~3.5；蓝色为未启用版本，初始Loss高达~6.3，需经约1200步才降至同等水平。红色箭头标注"3.93×"，定量说明无Anchor-Offset需多花近4倍训练步数才能追上。

该图作为训练阶段的实证依据，证明Anchor-Offset位置编码策略在长上下文建模中具备显著更优的起点Loss与收敛效率，为后续投机解码中Draft模型对超长位置信息的准确预测提供了关键的模型质量前提，从而支撑Table 4中更高的平均接受长度τ与解码加速结论。

### Figure 5 (p.8) ⭐深度解读
![[assets/crops/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-fig05.png]]
*整页渲染: ![[assets/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-p08.png]]*
> [!quote] caption
> Latency breakdown for a single speculative decoding loop comparing the EAGLE implementation and the proposed Hybrid Tree Attention. Significant latency reduction is observed in the target model’s at- tention layer (the yellow part) using our approach.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**核心对象与量化数据**

Figure 5 以水平堆叠条形图分解单次投机解码循环的延迟，对比 **EAGLE（~78 ms）** 与 **Hybrid Tree Attention（~40 ms）**，分四段：draft model forward、target model attention、target model FFN、verification。EAGLE 中 target attention 约 50 ms（占绝对主体）；Hybrid 将其压缩至 ~12 ms（约 4× 加速），draft、FFN、verification 三段基本不变，总耗时近乎减半。

**关键技术结论**

该图量化佐证 caption 论述：Hybrid Tree Attention 的收益**集中体现在目标模型注意力层**，直接缓解长上下文验证阶段的注意力计算瓶颈，验证了作者"目标模型 attention 层显著降低"的论断。

**在论文整体链路中的作用**

作为 LongSpec 核心效率实证证据，支撑其"长上下文无损 + 高效"的设计主张；与吞吐、接受率等实验数据相互呼应，证明优化并非以牺牲无损性为代价。

### Figure 6 (p.9) ⭐深度解读
![[assets/crops/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-fig06.png]]
*整页渲染: ![[assets/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-p09.png]]*
> [!quote] caption
> Throughput comparison of Vanilla, MagicDec, and LONGSPEC. not suitable for such long-output scenarios because the initial inference stage of the long reasoning task is not the same as the traditional long-context task. In long reasoning tasks, where the prefix is relatively short, the draft model in MagicDec will completely degrade into the target model, failing to achieve acceleration.

> [!tip] 技术解读（多模态）
> 【图文联合解读】图6展示Vanilla、MagicDec、LongSpec在批大小1–8下的吞吐量。LongSpec全面领先——批大小8时达约560，是Vanilla(~290)与MagicDec(~312)的近2倍；而MagicDec与Vanilla曲线几乎重合，差距<10%。原文据此论证：在长输出推理场景中，前缀较短使MagicDec的草稿模型退化为目标模型而失效；LongSpec通过高效草稿与验证机制突破了这一瓶颈，是支撑"无损推测解码可应用于长上下文/长输出"这一核心结论的关键实验证据。

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.6) ⭐深度解读
![[assets/crops/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-tab01.png]]
> [!quote] caption
> and Figure 3 show the decoding speeds and average acceptance lengths across the five evalu- ated datasets at T = 0 and T = 1 , where T denotes the temperature used in LLM sampling. Our pro- posed method significantly outperforms all other approaches on both summarization tasks and code completion ta

> [!tip] 表格解读（多模态）
> 【图文联合解读】**说明：** 所提供图片实为论文 §4.2 "Main Results" 正文页（对 Table 1 的文字论述），并非 Table 1 表格本体，故依据原文进行解读。

---

**1) 核心对象与数据：** Table 1 展示 LongSpec 在 5 个评测数据集（含摘要与代码补全两类长文本任务）上，于 T=0 与 T=1 两种采样温度下的解码速度（speedup）与平均接受长度。T=0 时，摘要任务接受长度约 3.5、加速比最高 2.67×；代码补全任务接受长度约 4、加速比最高 3.26×。T=1 时仍保持约 2.5× 加速，持续领先 MagicDec。

**2) 关键结论：** 证明 LongSpec 在长文本生成场景下兼具高接受率与显著加速，且对温度鲁棒，方法具备通用性与稳健性。

**3) 论文作用：** 作为主实验核心定量证据，支撑"长上下文无损推测解码"在摘要、代码两类典型长序列任务上的 SOTA 主张，与图3互补，回应引言中 EAGLE 训练上下文仅 2k 的痛点。

### Table 2 (p.8) ⭐深度解读
![[assets/crops/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-tab02.png]]
> [!quote] caption
> Performance comparison with and with- out Anchor-Offset Indices on the Multi-News and RepoBench-P datasets. Models with Anchor-Offset In- dices achieve higher output speed and larger acceptance length, highlighting their efficiency and effectiveness.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 2 图文联合解读**

该表在 Multi-News（摘要）与 RepoBench-P（代码）两个长文本基准上，对比启用/不启用 Anchor-Offset Indices 时的接受长度 τ 与吞吐量 Tokens/s。

具体数据：Multi-News 上 τ 由 3.20 升至 3.36（+5.0%），Tokens/s 由 85.98 升至 91.11（+6.0%）；RepoBench-P 上 τ 由 3.26 升至 3.39（+4.0%），Tokens/s 由 85.21 升至 91.28（+7.1%）。两数据集两指标同步提升，且吞吐量增益（6–7%）略高于 τ 增益。

原文借此论证：Anchor-Offset Indices 是 LongSpec 长上下文无损投机解码的核心工程优化——它弥补了朴素索引在长序列下压缩率与检索精度的双重损失，使轻量草稿模型更准确地预测目标 token，从而在 lossless 前提下同时提升接受长度与端到端解码速度。

在论文链路中，本表属组件消融环节，紧承 Figure 2(b) 索引机制示意图，为后续端到端长文评测中 LongSpec 的速度优势提供单变量因果证据。

### Table 3 (p.8) ⭐深度解读
![[assets/crops/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-tab03.png]]
> [!quote] caption
> Performance of our method on the QwQ-32B model on four math reasoning datasets, using a maxi- mum output length of 32k tokens. The table shows the tokens generated per second and the mean number of accepted tokens τ , where our approach achieves about 2.34 × higher speed compared to the baseline on 

> [!tip] 表格解读（多模态）
> 【图文联合解读】Table 3展示QwQ-32B在AIME24/AMC/Minerva/MATH500四个数学推理集（32k最大输出）上的性能：Vanilla tokens/s仅18.92–19.59，LongSpec提升至42.63–48.36，加速比2.25–2.47×；τ由1.00升至3.65–3.95（平均3.81）。原文据此论证：LongSpec在长输出思维链场景下仍能无损地实现平均2.34×加速，验证其n-gram+动态树草稿机制对长链路CoT的有效性。该表与Figure 3（摘要/代码等短输出场景）互补，证明方法在不同任务、不同输出长度下均稳定加速，支撑论文"无损长上下文推测解码"的核心结论。

### Table 4 (p.16) ⭐深度解读
![[assets/crops/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-tab04.png]]
> [!quote] caption
> Average acceptance length τ and decoding speed (tokens/s) across different models and settings. Specifically, “Vanilla HF” refers to HuggingFace’s PyTorch-based attention implementation, while “Vanilla FA” employs Flash

> [!tip] 表格解读（多模态）
> 【图文联合解读】**1) 核心对象与数据**
表4对比V-7B与LC-7B两个模型在GovReport、QMSum、MultiNews、LCC、RB-P五个长文数据集上,Vanilla HF/FA、TR、EAGLE、LongSpec五种设置的接受长度τ与解码速度(tokens/s)。LongSpec在所有数据集均取得最高τ(V-7B:3.14–3.86;LC-7B:3.06–4.21)与最快速度(85.23–122.30 tok/s),全面领先;EAGLE τ≈1.91–2.10,但tokens/s仅26–40;TR速度近LongSpec(64.96–100.41)但τ偏低(2.13–3.05)。

**2) 关键结论**
LongSpec同时实现更长接受长度与更高吞吐量,体现高效draft+verify机制的优越性;EAGLE速度慢表明短文训练的draft在长上下文失效;TR速度可但验证开销大。

**3) 论文作用**
与图4训练曲线协同,作为核心实验结论表,支撑"长上下文无损推测解码"的整体主张。

### Table 5 (p.16) ⭐深度解读
![[assets/crops/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-tab05.png]]
> [!quote] caption
> A detailed breakdown of performance as the prefill length increases, with LongChat-7B on GovReport.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

表格对比 **V-7B** 与 **LC-7B** 两模型在 GovReport、QMSum、MultiNews、LCC、RB-P 五个长文数据集上，Vanilla HF、Vanilla FA、TR、EAGLE、LongSpec 五种方法的接受长度 τ 与生成吞吐量 Tokens/s。

**关键结论：** LongSpec 在所有数据集上 τ 最高（3.06–4.21），Tokens/s 较 Vanilla HF 提速约 **4×**（如 LC-7B LCC：122.30 vs 25.27）；而 EAGLE 在长文下 Tokens/s（29.75–40.64）反低于 Vanilla FA（42.69–54.17），暴露其长上下文退化。

**实验链路作用：** 以多模型×多数据集的横向基准，定量证明 LongSpec 相对 TR/EAGLE 在长上下文场景具备稳定无损加速优势，构成论文核心实验证据。

（注：原文表格 caption 与正文实际内容存在轻微出入——caption 仅提 GovReport，但表中实为五数据集联合对比。）

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\mathrm{LSE}_{\mathrm{merge}} = \log\Bigl(\exp\bigl(\mathrm{LSE}_{\mathrm{cache}}\bigr) \;+\; \exp\bigl(\mathrm{LSE}_{\mathrm{specs}}\bigr)\Bigr),
$$

$$
o_{\mathrm{merge}} = &o_{\mathrm{cache}} \cdot \exp\bigl(\mathrm{LSE}_{\mathrm{cache}} - \mathrm{LSE}_{\mathrm{merge}}\bigr) \\+& o_{\mathrm{specs}} \cdot\exp\bigl(\mathrm{LSE}_{\mathrm{specs}} - \mathrm{LSE}_{\mathrm{merge}}\bigr).
$$

$$
o_{\mathrm{merge}} &= \mha\left(q, K_{\mathrm{merge}}, V_{\mathrm{merge}}\right) \\&= \sm\left( qK_{\mathrm{merge}}^\top/\sqrt{d_{qk}} \right) V_{\mathrm{merge}}.
$$

$$
q K_{\mathrm{merge}}^\top / \sqrt{d_{qk}} = \texttt{concat}\Bigl(& \underbrace{ q \, K_{\mathrm{cache}}^\top / \sqrt{d_{qk}} }_{\mathrm{sub-logits\ for\ history}} \;, \\& \underbrace{ q \, K_{\mathrm{specs}}^\top / \sqrt{d_{qk}} }_{\mathrm{sub-logits\ for\ new}} \Bigr).
$$

$$
Z_{\mathrm{cache}} \;&=\; q \,K_{\mathrm{cache}}^\top / \sqrt{d_{qk}} ,\;\\ Z_{\mathrm{specs}} \;&=\; q \, K_{\mathrm{specs}}^\top / \sqrt{d_{qk}}.
$$

$$
\mathrm{LSE}_{\mathrm{cache}} &= \log\left(\sum\nolimits_{j=1}^{N} \exp\left(Z_{\mathrm{cache}}^{(j)}\right)\right),\nonumber\\ \; \mathrm{LSE}_{\mathrm{specs}} &= \log\left(\sum\nolimits_{j=1}^{M} \exp\left(Z_{\mathrm{specs}}^{(j)}\right)\right), \,
$$

$$
o_{\mathrm{cache}} &= \frac{\sum_{j=1}^{N} \exp\left(Z_{\mathrm{cache}}^{(j)}\right) V_{\mathrm{cache}}^{(j)}}{\exp\left(\mathrm{LSE}_{\mathrm{cache}}\right)}, \nonumber\\ o_{\mathrm{specs}} &= \frac{\sum_{j=1}^{M} \exp\left(Z_{\mathrm{specs}}^{(j)}\right) V_{\mathrm{specs}}^{(j)}}{\exp\left(\mathrm{LSE}_{\mathrm{specs}}\right)}.
$$

$$
N_{\mathrm{num}} &= \sum_{j=1}^{N} \exp\bigl(Z_{\mathrm{cache}}^{(j)}\bigr) V_{\mathrm{cache}}^{(j)}\nonumber\\ &+ \sum_{j=1}^{M} \exp\bigl(Z_{\mathrm{specs}}^{(j)}\bigr) V_{\mathrm{specs}}^{(j)}, \nonumber\\[0.5em] D_{\mathrm{den}} &= \exp\bigl(\mathrm{LSE}_{\mathrm{cache}}\bigr) + \exp\bigl(\mathrm{LSE}_{\mathrm{specs}}\bigr), \nonumber\\[0.5em] o_{\mathrm{merge}} &= \frac{N_{\mathrm{num}}}{D_{\mathrm{den}}}.
$$

$$
o_{\mathrm{merge}} =& o_{\mathrm{cache}} \cdot\exp\bigl(\mathrm{LSE}_{\mathrm{cache}} - \mathrm{LSE}_{\mathrm{merge}}\bigr) \nonumber\\+& o_{\mathrm{specs}} \cdot \exp\bigl(\mathrm{LSE}_{\mathrm{specs}} - \mathrm{LSE}_{\mathrm{merge}}\bigr).
$$

$$
O_{\geq j} = \att \bigl(Q_{\geq j}, \,K_{< l-j}, \,V_{< l-j}\bigr).
$$

$$
\begin{aligned} \mathrm{LSE}_{\mathrm{merge}} &= \log\Bigl(\exp\bigl(\mathrm{LSE}_{\mathrm{cache}}\bigr) + \exp\bigl(\mathrm{LSE}_{\mathrm{specs}}\bigr)\Bigr), \end{aligned}
$$

$$
\begin{aligned} O_{\mathrm{merge}} =\; &O_{\mathrm{cache}} \cdot \exp\bigl(\mathrm{LSE}_{\mathrm{cache}} - \mathrm{LSE}_{\mathrm{merge}}\bigr)\\ +\; &O_{\mathrm{specs}} \cdot \exp\bigl(\mathrm{LSE}_{\mathrm{specs}} - \mathrm{LSE}_{\mathrm{merge}}\bigr). \end{aligned}
$$

## 相关论文

- [[jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting]] — JETSPEC: Breaking the Scaling Ceiling of Speculative Decoding with Parallel Tree Drafting
- [[dspark-confidence-scheduled-speculative-decoding-with-semi-autoregressive-generation]] — DSpark: Confidence-Scheduled Speculative Decoding with Semi-Autoregressive Generation
- [[specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences]] — SpecExtend: A Drop-in Enhancement for Speculative Decoding of Long Sequences
- [[dflash-block-diffusion-for-flash-speculative-decoding]] — DFlash: Block Diffusion for Flash Speculative Decoding
- [[deepseek-v4-towards-highly-efficient-million-token-context-intelligence]] — DeepSeek-V4: Towards Highly Efficient Million-Token Context Intelligence
- [[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]] — MEDUSA: Simple LLM Inference Acceleration Framework with Multiple Decoding Heads

## 技术点深读（DEEP）

![[deep/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification.txt`（76029 字符）供引用检索。