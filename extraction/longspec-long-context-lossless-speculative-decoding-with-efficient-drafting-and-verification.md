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
> 【图文联合解读】**图1联合解读（≤220字）**

该图以对数纵轴条形图对比7个现代LLM的上下文窗口：Llama 4 Scout约10M（最高），Grok 3、GPT-4.1、Gemini 2.5 Pro约1M，Claude 3.7 Sonnet约200k，DeepSeek-V3与Qwen3-235B-A22B约128k；底部红色虚线标注于2k处，对应SoTA推测解码方法EAGLE的训练上下文长度2048。

**原文论证结论**：EAGLE训练上下文（2k）相比现代LLM（128k–10M）存在**两个数量级到四个数量级**的巨大差距，传统SD方法无法直接迁移到长上下文场景。

**论文作用**：作为开篇**动机图**，直接引出LongSpec的核心必要性——必须为超长上下文重新设计草稿生成与验证机制，为后续方法设计与Table 1/Figure 3的实验评测铺垫问题背景。

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
> 【图文联合解读】该图上半为表格：Multi-News 与 RepoBench-P 上，无 Anchor-Offset 时 τ=3.20/3.26、Tokens/s≈85；引入后 τ 升至 3.36/3.39、Tokens/s 升至 91+。下半为 0–1200 步训练损失曲线，Anchor-Offset（红）初损约 4.2、终损约 3.5；无 Anchor-Offset（蓝）初损约 6.4，原文用红色箭头标注其达同等损失需多耗 3.93× 步数。结论：Anchor-Offset 索引在长上下文上同时降低训练初/终损失并大幅加速收敛，同时提升推理接受长度与吞吐。该图衔接训练消融与推理评测，闭环支撑 LongSpec "训练-推理协同" 的长上下文推测解码方案。

### Figure 5 (p.8) ⭐深度解读
![[assets/crops/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-fig05.png]]
*整页渲染: ![[assets/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-p08.png]]*
> [!quote] caption
> Latency breakdown for a single speculative decoding loop comparing the EAGLE implementation and the proposed Hybrid Tree Attention. Significant latency reduction is observed in the target model’s at- tention layer (the yellow part) using our approach.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图5图文联合解读**

图5以水平堆叠条形图分解单次投机解码循环延迟，对比EAGLE（≈76 ms）与Hybrid（≈37 ms），分四段：draft forward（红）、target attention（黄）、target FFN（绿）、verification（蓝）。EAGLE中target attention段约51 ms，占绝对主导；Hybrid将其压缩至约11 ms，约4–5×加速；其余三段近似不变，总延迟近乎减半。结论：Hybrid Tree Attention精准削减了长上下文下target attention的关键瓶颈。该图作为方法核心论据，以延迟分解直观证明改进集中于attention层，支撑LongSpec整体近2倍加速的实验结论。

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
> 【图文联合解读】**Table 1 图文联合解读**

**① 核心对象与结构数据**
表格针对目标模型 **QwQ-32B**，在 5 个长文本数据集（摘要、代码补全）上，比较目标模型、**PLD**（n-gram SD）、**MagicDec**（带/不带 Flash Attention）以及作者提出的 **LongSpec**，报告两个温度（T=0、T=1）下的 **walltime speedup** 与 **平均接受长度 τ**。例如 T=0 下摘要任务 τ≈3.5、加速达 2.67×；代码补全 τ≈4、加速达 3.26×；T=1 下整体保持 ~2.5× 加速。

**② 关键论证结论**
原文用此表证明：(a) LongSpec 在两类长文本任务上均**显著超越 PLD 与 MagicDec**；(b) 即便 MagicDec 使用 Flash Attention 仍落后 LongSpec，说明优势并非仅来自注意力实现；(c) 接受长度 τ 较高（3–4），验证 draft 模型在长上下文下仍能生成被目标 LLM 接受的 token 序列，体现方法的**无损性与鲁棒性**。

**③ 在论文链路中的作用**
Table 1 是 §4.2 "Main Results" 的**主实验证据表**，与 Figure 3 共同支撑 §1 中"EAGLE 等 SD 方法训练上下文仅 2048、难以适配现代 LLM 长窗口"的核心痛点主张，并为后续消融与长上下文数学推理实验（§4.3）提供基准性能参照。

### Table 2 (p.8) ⭐深度解读
![[assets/crops/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-tab02.png]]
> [!quote] caption
> Performance comparison with and with- out Anchor-Offset Indices on the Multi-News and RepoBench-P datasets. Models with Anchor-Offset In- dices achieve higher output speed and larger acceptance length, highlighting their efficiency and effectiveness.

> [!tip] 表格解读（多模态）
> 【图文联合解读】Table 2 在 Multi-News 与 RepoBench-P 两个长文数据集上，对比有无 Anchor-Offset 索引（锚点-偏移索引）的接受长度 τ 与生成速度 Tokens/s。

**核心数据**：无索引时，Multi-News 的 τ=3.20、85.98 tokens/s，RepoBench-P 的 τ=3.26、85.21 tokens/s；加入 Anchor-Offset 后分别提升至 3.36/91.11 与 3.39/91.28，速度增益约 6%–7%，接受长度提升约 4%–5%。

**论证结论**：Anchor-Offset 索引压缩了草稿模型的 KV Cache 索引而不损精度，同步提高草稿 token 被目标模型接受的概率与端到端生成吞吐，验证其高效性与有效性。

**论文作用**：作为消融实验，量化证实 LongSpec 三大核心组件之一的独立贡献，与 Figure 2(b) 索引机制图形成"机制说明—性能验证"的闭环。

### Table 3 (p.8) ⭐深度解读
![[assets/crops/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-tab03.png]]
> [!quote] caption
> Performance of our method on the QwQ-32B model on four math reasoning datasets, using a maxi- mum output length of 32k tokens. The table shows the tokens generated per second and the mean number of accepted tokens τ , where our approach achieves about 2.34 × higher speed compared to the baseline on 

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 3 图文联合解读**

**1）核心内容**：在 QwQ-32B 模型、32k 最大输出长度下，对 AIME24、AMC、Minerva、MATH500 四个数学推理数据集对比 Vanilla 与 LongSpec。平均接受长度 τ 从 1.00 提升至 3.65–3.95（均 3.81）；Tokens/s 从约 19 提升至 42.63–48.36，平均加速 2.34×（2.25×–2.47×）。

**2）关键结论**：LongSpec 在长输出数学推理中通过一次验证接受近 4 个 token，实现 lossless 推理的同时获得 2.34× 端到端加速。

**3）论文作用**：与 Figure 3（摘要/代码 5 类长文任务）、Table 1（综合对比）共同构成实验核心，证明 LongSpec 的长上下文投机解码在长输出推理场景下依然有效且无损。

### Table 4 (p.16) ⭐深度解读
![[assets/crops/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-tab04.png]]
> [!quote] caption
> Average acceptance length τ and decoding speed (tokens/s) across different models and settings. Specifically, “Vanilla HF” refers to HuggingFace’s PyTorch-based attention implementation, while “Vanilla FA” employs Flash

> [!tip] 表格解读（多模态）
> 【图文联合解读】表4（T=0）对比V-7B与LC-7B在GovReport、QMSum、MultiNews、LCC、RB-P五项长文任务的平均接受长度τ与解码速度（tokens/s），设置涵盖Vanilla HF/FA、TR、EAGLE、LongSpec。

数据要点：LongSpec τ=3.06–4.21、速度85–122；Vanilla τ=1、速度14–56；TR τ≈2.7–3.0但速度与LongSpec相近；EAGLE τ≈2且速度仅26–40。

结论与作用：LongSpec在τ与吞吐上同时超越基线与SOTA投机方法（TR/EAGLE），证明其无损长上下文投机解码的全面高效性，是论文支撑方法相对现有方案优势的核心效率证据表。

### Table 5 (p.16) ⭐深度解读
![[assets/crops/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-tab05.png]]
> [!quote] caption
> A detailed breakdown of performance as the prefill length increases, with LongChat-7B on GovReport.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 5 图文联合解读**

该表在 6 个 prefill 区间（0–5k 至 25k–32k）下，用 LongChat-7B 在 GovReport 上分解吞吐量 Tokens/s、平均接受长度 τ 及 Draft / Target / Verify 三段耗时。数据显示 τ 稳定在 4 左右，Draft（8.91→9.25 ms）与 Verify（6.18→6.28 ms）耗时近乎持平，而 Target 时间由 25.63 ms 单调增至 30.89 ms，是 25k–32k 段吞吐量由 ~115 跌至 103.68 tokens/s 的主导因素。

原文借此论证两点：(1) LongSpec 的接受长度对长 context 不敏感，drafting 阶段无退化；(2) 长上下文下真正的瓶颈集中在目标模型注意力层——直接呼应 Fig.5 中 HTA 显著削减该部分黄色延迟的结论，凸显该优化在整个 speculative decoding 链路中的必要性与有效性。

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