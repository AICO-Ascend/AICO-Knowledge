---
paper_num: "6"
title: "BLOCK DIFFUSION: INTERPOLATING BETWEEN AUTOREGRESSIVE AND DIFFUSION LANGUAGE MODELS"
authors: ""
date: "2025/3/12"
arxiv: "https://arxiv.org/abs/2503.09573"
pdf: "papers/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models.pdf"
slug: "block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models"
tags: [speculative]
---

# BLOCK DIFFUSION: INTERPOLATING BETWEEN AUTOREGRESSIVE AND DIFFUSION LANGUAGE MODELS

> [!abstract] 摘要（原文）
> 1\. 🚀 本文提出了块扩散语言模型（BD3-LMs），通过在离散去噪扩散和自回归模型之间进行插值，成功解决了传统离散扩散模型在处理任意长度生成和推理效率上的限制。 2. 💡 研究人员开发了一种高效的训练算法及数据驱动的噪声调度策略，通过显著降低梯度方差，有效弥补了扩散模型与自回归模型在困惑度（Perplexity）上的性能差距。 3. 📈 实验结果表明，BD3-LMs 在多个语言建模基准测试中达到了离散扩散模型的新前沿水平，并支持长序列的高质量、并行化生成，同时提升了推理效率。

## 元信息
- **发表日期**: 2025/3/12
- **作者**: —
- **arXiv**: https://arxiv.org/abs/2503.09573
- **本地 PDF**: `papers/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models.pdf`
- **页数**: 28

## 图表（原文 caption + 页码）

### Figure 1 (p.2) ⭐深度解读
![[assets/crops/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-fig01.png]]
*整页渲染: ![[assets/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-p02.png]]*
> [!quote] caption
> Block diffusion sequentially generates blocks of tokens by performing diffusion within each block and conditioning on previous blocks. By combining strength from autoregressive and diffusion models, block diffusion overcomes the limitations of both approaches by supporting variable-length, higher-quality generation and improving inference efficiency with KV caching and parallel sampling. network a

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图1核心内容**：以三行对照呈现三种语言生成范式——自回归（arbitrary-length、✓KV caching、✗Not Parallelizable）、全扩散（fixed-length、✗No KV caching、✓Parallelizable）、块扩散（arbitrary-length、✓KV caching、✓Parallelizable），并用"continue to reduce the deficit"等生成示例直观展示块内并行去噪过程。

**论证的技术结论**：块扩散融合两类模型优势，兼具变长生成、KV缓存与块内并行采样，同时克服自回归不可并行、纯扩散不可缓存的固有缺陷。

**论文整体作用**：作为方法总览图，在引言/方法章节开篇建立"块内扩散+块间自回归"的混合范式概念框架，为后续训练损失推导、噪声调度设计与推理效率实验提供直觉锚点。

### Figure 2 (p.6) ⭐深度解读
![[assets/crops/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-fig02.png]]
*整页渲染: ![[assets/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-p06.png]]*
> [!quote] caption
> Train NLLs for modeling the per-token likelihood on LM1B. Models are trained on 16B tokens. Training under the discrete diffusion NELBO, where half of the tokens in a batch are masked on average, has similar training variance to an AR model with a random batch size. so that Et∼U[0,1]q(xℓ t = m|xℓ) = 0.5. Thus, training on the diffusion objective involves estimating loss gradients with 2x fewer tok

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读**

图示LM1B（16B token训练）单token训练NLL曲线，横轴约150k–250k步，包含：红色曲线（块扩散/扩散，方差最大、存在明显尖峰）、橙色AR曲线（最平滑低方差）、绿色AR随机batch曲线（方差居中）等多条线对比。

论文借此论证关键结论：平均50%掩码的离散扩散NELBO训练方差，与随机batch的AR相当，意味着每batch有效token近似翻倍（≈2×），扩散目标并无显著梯度劣势。

该图为块扩散作为AR与扩散LM之间插值框架的可行性提供经验背书，回应"扩散训练方差大、不易优化"的潜在质疑，是后续block size与调度实验的方法论前提。

### Figure 3 (p.21) ⭐深度解读
![[assets/crops/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-fig03.png]]
*整页渲染: ![[assets/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-p21.png]]*
> [!quote] caption
> x1 t x2 t x3 t x1 x2 x3 x1 t x2 t x3 t x1 x2 x3

> [!tip] 技术解读（多模态）
> 【图文联合解读】**Figure 3 图文联合解读**

**1）核心对象与结构：** 图示一个专门化的注意力掩码（Specialized Attention Mask），按L=3个块（如x¹、x²、x³）排列，图中可见三色分区——**Block Diagonal (M_BD)**（块对角，每个块内独立）、**Offset Block Causal (M_OBC)**（偏移块因果，跨块时仅关注先前块）、**Block Causal (M_BC)**（块内因果，同块内token依次关注前者）。结合上下文规则：块内采用因果掩码更新x^b；块间跨注意力条件化于x^<b。

**2）关键技术结论：** 该掩码为块扩散模型构造了一种"块级稀疏因果+跨块条件化"的混合注意力模式：块内保持自回归因果性，块间以偏移因果避免信息泄露，同时通过M_BD实现并行去噪。原文Figure 4进一步证明，将其改写为FlexAttention兼容的稀疏掩码后，在L=1024、B=16、A5000上相比PyTorch原生实现可获**约5倍加速**与显著内存节省。

**3）在论文中的作用：** 该图是块扩散方法的核心算法图示，奠定了"块级半自回归"训练/采样范式，并为后续高效推理实现提供视觉依据，连接理论框架与系统优化。

### Figure 4 (p.22) ⭐深度解读
![[assets/crops/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-fig04.png]]
*整页渲染: ![[assets/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-p22.png]]*
> [!quote] caption
> We can adapt the masking strategy from Fig. 3 to a FlexAttention compatible sparse masking function as above. This enables the creation of a customized JIT attention operation that uses significantly less memory with up to ≈5X speedup over the naive native scaled_dot_product_attention implementation in PyTorch (≥2.5) on a A5000 GPU with L = 1024 and batch size B = 16. 22

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图4展示了将图3的掩码策略改写为FlexAttention兼容的稀疏掩码函数（约30行PyTorch代码）。核心结构是合成三种掩码：①块内自注意（block_causal）、②跨块条件上下文（block_causal_BC）、③偏移块因果（M_OBC），通过`q//block_size`取整、`xt_flag`/`x0_flag`标识（0/1）控制q/kv关系，以按位XOR与AND逐元素组合，得到稀疏的`M_OBC`偏移因果掩码。

该代码论证了：基于PyTorch≥2.5的FlexAttention/JIT定制算子，在A5000、L=1024、B=16条件下，**显存显著降低且加速≈5倍**，相较朴素的`scaled_dot_product_attention`优势明显。

在论文链路中，此图属于工程实现层，为Block Diffusion模型的关键创新——半自回归+扩散混合的块稀疏注意力——提供高效GPU实现支撑，是模型可扩展训练/推理的底层保障。

### Figure 5 (p.23) ⭐深度解读
![[assets/crops/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-fig05.png]]
*整页渲染: ![[assets/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-p23.png]]*
> [!quote] caption
> Attention computation using FlexAttention with our proposed custom mask.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图5以代码片段展示核心实现：顶部调用 `torch.compile(fullgraph=True, mode="max-autotune-no-cudagraphs")` 进行全图编译加速；下方定义 `single_pass_block_diff_attn(q, k, v, block_mask)` 函数，内部通过 `flex_attention(q, k, v, block_mask=block_mask)` 完成一次前向注意力计算。

该图论证的关键技术结论：块扩散语言模型利用 PyTorch FlexAttention 接口，将自定义的块级因果掩码（block_mask）直接传入底层注意力内核，无需重写 CUDA/Triton 内核即可在通用硬件上高效实现"块内双向、块间因果"的混合注意力模式。

在全论文中的作用：它是连接理论掩码设计（Section）与高效训练推理的工程桥梁——通过 `flex_attention` 把块式注意力模式硬件化，使大语言规模下的块扩散训练成为可能，是模型可扩展性的核心实现支撑。

### Figure 6 (p.26) ⭐深度解读
![[assets/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-p26.png]]
> [!quote] caption
> Sample from MDLM (Sahoo et al., 2024a) of length L = 1024 and T = 5K diffusion steps.

> [!tip] 技术解读（多模态）
> ## Description

This figure is **not an architecture diagram** but rather a **qualitative sample** illustrating the output of MDLM (Sahoo et al., 2024a), a masked diffusion language model. There is no architecture, component, or data-flow schematic — the "figure" is simply a rendered block of generated text wrapped between `<lendoftext>` sentinel tokens.

**Reading the output:** The generated passage (~1024 tokens, produced over 5K diffusion steps) is a topical mishmash blending multiple domains — art criticism (Paolo Capacotti, Giuliano/Angiolo/Leonetto Romei/Fiastri family), a museum crime anecdote (Franco Belzina's life, the broken candle, statue restoration), WWII history (Canadian/Italian POWs, statues removed from Cooper–Paris), and music industry references (record labels, festivals). **Key takeaway:** despite MDLM achieving competitive perplexity, the 1024-token sample exhibits topic drift, entity hallucination, and incoherent transitions — a common failure mode where diffusion-style generation lacks the autoregressive consistency that maintains long-range coherence in causal LMs.

## Caption (verbatim)

> **Figure 6:** Sample from MDLM (Sahoo et al., 2024a) of length *L* = 1024 and *T* = 5K diffusion steps. The generative perplexity of this sample under GPT2-Large is 69.26 and its entropy is 5.6.

### Figure 7 (p.27) ⭐深度解读
![[assets/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-p27.png]]
> [!quote] caption
> Sample from BD3-LM for block size L′ = 16 of length L = 2031 under T = 5K diffusion steps (trained with a context length of L = 1024). The generative perplexity of this sample under GPT2-Large is 24.3, and its entropy is 5.5. 27

> [!tip] 技术解读（多模态）
> **Figure description:** This figure is not an architecture diagram but a *sample generation* from BD3-LM, a block-wise discrete diffusion language model. It displays a single block of continuous narrative text (≈2,031 tokens) bounded by `<lendoftext>` end-of-document markers. The content is a coherent, multi-paragraph story about a girl traveling to Mexico, her mother being detained at a Bangkok airport on the way home, and broader commentary on Calais refugees — demonstrating that the model produces long, fluent, topic-consistent passages.

**Key technical takeaway:** Despite being trained with a context length of only L = 1,024, BD3-LM generates sequences of length L = 2,031 (nearly 2× the training window) using only T = 5K diffusion steps with block size L' = 16, yielding coherent text with GPT2-Large generative perplexity 24.3 and entropy 5.5 — showing block diffusion can extrapolate beyond training context.

**Caption (verbatim):**
> Figure 7: Sample from BD3-LM for block size L' = 16 of length L = 2031 under T = 5K diffusion steps (trained with a context length of L = 1024). The generative perplexity of this sample under GPT2-Large is 24.3, and its entropy is 5.5.

### Figure 8 (p.28) ⭐深度解读
![[assets/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-p28.png]]
> [!quote] caption
> Sample from an AR model (Sahoo et al., 2024a) with length L = 2003 (trained with a context length of L = 1024). The generative perplexity of this sample under GPT2-Large is 10.6 and its entropy is 5.5. 28

> [!tip] 技术解读（多模态）
> **Description**

This is not a traditional architecture diagram — it is a qualitative-output figure. The figure consists of a single boxed block of generated English text flanked by `<lendofftext>` sentinel tokens. The text is one long, unsegmented passage (~2,000 tokens) produced by an autoregressive language model; it drifts incoherently across multiple unrelated topics (an NFL game recap, a personal dispute over a tree in "Charlotte Gardens," architectural commentary on a building, and assorted trivia), with frequent name/topic confusions, fabricated quotes, and hallucinated entities. There are no labeled components, arrows, or data-flow stages — the "architecture" is implicit (AR transformer with context length 1024 producing a 2003-token sample, benchmarked against GPT2-Large, achieving perplexity 10.6 and entropy 5.5).

**Key takeaway:** The sample illustrates that even a long-context AR model (L=1024) trained to generate beyond its context (L=2003) still produces locally fluent but globally incoherent, topic-drifting text — demonstrating that long-context AR pretraining alone does not guarantee coherent long-form generation.

**Caption (verbatim):**
Figure 8: Sample from an AR model (Sahoo et al., 2024a) with length L = 2003 (trained with a context length of L = 1024). The generative perplexity of this sample under GPT2-Large is 10.6 and its entropy is 5.5.

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.5) ⭐深度解读
![[assets/crops/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-tab01.png]]
> [!quote] caption
> Test perplexities for single- token generation (PPL; ↓ ) across 16B tokens on LM1B.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 1 图文联合解读：**

1）**核心对象与数据**：该表展示在 LM1B 数据集、16B tokens 训练量下的单 token 测试困惑度（PPL，↓）。对比四组：AR 基线为 22.88；AR 改用随机 batch size 后退化为 24.37；BD3-LM（块长 L'=1）PPL ≤25.56，相较 AR 高约 2.7 点；引入 tuned schedule 后 BD3-LM PPL 降至 22.88，与 AR 完全持平。

2）**关键技术结论**：在 L'=1 极限下，块扩散目标理论上与自回归 NLL 期望等价，但实证仍存在两点的 PPL 差距。原文指出该差距并非来自建模偏差，而是源于训练方差——AR 对 L 个 token 计算交叉熵，而 BD3-LM 仅对掩码 token 计算，导致收敛困难；通过 schedule 调优即可彻底消除差距。

3）**在论文中的作用**：该表是连接理论与实践的关键实验证据，验证了块扩散可"插值"至自回归端点的理论声明，并定位了主要瓶颈为训练方差而非建模本身，从而为后续大块长（更高推理效率）研究提供了性能可比、可复现的基线支撑。

### Table 2 (p.7) ⭐深度解读
![[assets/crops/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-tab02.png]]
> [!quote] caption
> Perplexities (PPLs; ↓ ) and variances of the NELBO Var X ,t [ L BD ( X ; θ )] (Var. NELBO; ↓ ). Models are trained on LM1B using a linear schedule for 65B tokens, then finetuned for 10B tokens.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**注：** 所提供图片仅含论文 5.3 节正文及 Table 2 的 caption，未呈现表格具体数值，故仅依据原文解读：

**1) 核心对象与结构：** Table 2 展示 LM1B 数据集、不同 block size $L'\in\{4,16,128\}$ 下各模型的测试困惑度 (PPL↓) 与扩散 NELBO 方差 $\mathrm{Var}_{\mathbf{X},t}[\mathcal{L}_{\mathrm{BD}}]$ (Var. NELBO↓)。训练采用 linear schedule，先训 65B tokens、再 fine-tune 10B tokens。

**2) 关键技术结论：** 原文论证"扩散 NELBO 方差与 test PPL 正相关"——在 clipped 噪声率分布族中，每个 block size 都对应一个**唯一最优分布**同时最小化方差与困惑度；这验证了把 NELBO 方差作为梯度估计方差代理来优化超参 $\beta,\omega$ 的合理性。

**3) 在论文链路中的作用：** 直接支撑 5.3 节"data-driven clipped schedules"——通过训练中定期 grid search 学习最优 $\beta,\omega$，将 Kingma et al.(2021) 的方差最小化策略适配到 Block Diffusion 中"随机 batch + 随机 $t_b$"的双重随机场景，从而弥合扩散与 AR 之间的训练稳定性差距。

### Table 3 (p.7) ⭐深度解读
![[assets/crops/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-tab03.png]]
> [!quote] caption
> Test perplexities (PPL; ↓ ) of mod- els trained for 65B tokens on LM1B. Best diffusion value is bolded.

> [!tip] 表格解读（多模态）
> 【图文联合解读】表3比较在LM1B上均训练65B token的测试PPL（越低越好）：自回归模型为23.5和22.83；扩散模型D3PM、SEDD、MDLM分别为≤82.34、≤32.68、≤31.78，其中MDLM最佳。统一训练量下，掩码扩散显著优于经典D3PM，但仍落后自回归基线。该表用于定位现有扩散模型的质量差距，支撑块扩散在局部自回归与全局扩散间插值的必要性，并作为后续实验的质量基线。

### Table 4 (p.8) ⭐深度解读
![[assets/crops/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-tab04.png]]
> [!quote] caption
> Test perplexities (PPL; ↓ ) on OWT for models trained for 524B to- kens. Best diffusion value is bolded.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 4 图文联合解读**

该表报告在 OWT 上训练 524B tokens 后的测试 PPL（↓）：AR=17.54（参考），扩散类 SEDD≤24.10、MDLM≤22.98；BD3-LMs 随块长 L' 减小 PPL 单调下降——L'=16：≤22.27，L'=8：≤21.68，L'=4：≤**20.73**（最佳扩散值，加粗）。

原文用此论证两点：(1) BD3-LMs 在 OWT 大规模数据上同样优于既有扩散方法（较 MDLM 最高约 13% 改进），与 LM1B（Table 3）趋势一致；(2) 块长越小越逼近 AR，PPL 单调降低，验证"块扩散在 AR 与全扩散间插值"策略的可扩展性与正向收益。在论文实验链路中，本表是 Table 3 的数据规模扩展，与 Table 5 零样本泛化评估一起，共同构成 BD3-LMs 性能优越性的完整实证链。

### Table 5 (p.8) ⭐深度解读
![[assets/crops/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-tab05.png]]
> [!quote] caption
> Zero-shot validation perplexities ( ↓ ) of models trained for 524B tokens on OWT. All perplexities for diffusion models are upper bounds.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 5 联合解读**

**1）核心对象与数据**：该表呈现 OWT 上训练 524B tokens 后各模型的零样本验证困惑度（PPL↓）。具体值：AR 为 17.54；扩散基线 SEDD ≤24.10、MDLM ≤22.98；BD3-LM 随块长 L′ 缩短，PPL 从 ≤22.27（L′=16）降至 ≤21.68（L′=8），L′=4 时取得 ≤20.73（粗体，扩散模型最佳）。扩散模型 PPL 均为上界。

**2）关键结论**：减小块长度显著改善 BD3-LM 零样本泛化性；作为扩散模型，其上界已逼近 AR 基线，并在 Pubmed 上超越 AR，Wikitext/LM1B/AG News 上为扩散模型最佳。

**3）论文作用**：该表是论文证明 BD3-LM 在"块长度—生成质量"权衡上优于现有离散扩散语言模型的关键实验证据，强化了块扩散方法可作为 AR 与纯扩散间有效插值这一核心论点。

### Table 6 (p.8) ⭐深度解读
![[assets/crops/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-tab06.png]]
> [!quote] caption
> Generation length statistics from sampling 500 documents from models trained on OWT.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 6 图文联合解读：**

Table 6 对比 **AR**、**SEDD**、**MDLM**、**BD3-LM (L'=4)** 四种模型在 PTB、WikiText、LM1B、Lambada、AG News、Pubmed、Arxiv 共 7 个数据集上，从 OWT 训练后各采样 500 篇文档的**生成长度统计**。AR 行整体加粗作参照基线；MDLM 在 Lambada、Arxiv 两列加粗（最佳），BD3-LM 在 Pubmed 列加粗（最佳）。

原文 6.2 节借此论证核心结论：SEDD、MDLM 等传统扩散 LM 受限于训练时的固定上下文长度，**无法生成超过该长度的完整序列**，是其相较 AR 的固有缺陷；而 BD3-LM 通过**块扩散（block diffusion）**机制，可在块内并行去噪、块间自回归地拼接，从而实现可变长度生成，弥补此缺陷。

该表位于"Sample Quality and Variable-Length Sequence Generation"小节，是支撑"块扩散介于自回归与扩散之间"这一**方法定位**的关键实验证据，证明 BD3-LM 同时具备 AR 的长度灵活性与扩散模型的并行采样优势。

### Table 7 (p.9) ⭐深度解读
![[assets/crops/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-tab07.png]]
> [!quote] caption
> Generative perplexity (Gen. PPL; ↓ ) and number of function evaluations (NFEs; ↓ ) of 300 samples of lengths L = 1024 , 2048 . All models are trained on OWT. AR, SEDD, MDLM, BD3-LMs use 110M parameters and are trained on 524B tokens, while SSD-LM uses 400M parameters and is pre-trained on 122B token

> [!tip] 表格解读（多模态）
> 【图文联合解读】表7在OWT上用300个L=1024/2048样本比较Gen PPL↓/NFE↓。AR为14.1/13.2（1K/2K）；BD3-LM（L′=4）为25.7/23.6（1K/2K），优于MDLM（46.8/41.3）和SSD-LM（37.2/35.3），而SSD需40K/80K。L′=16的281.3/281.9疑漏小数点。图7的L=2031、5K步样本作定性佐证；本表证明缩块可改善质量，定位BD3的质量—效率折中。

### Table 8 (p.9) ⭐深度解读
![[assets/crops/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-tab08.png]]
> [!quote] caption
> Effect of the noise schedule on like- lihood estimation. We finetune BD3-LMs on 3B tokens from LM1B and evaluate on a linear schedule. For clipped schedules, we compare optimal clipping for L ′ = 4 , 16 .

> [!tip] 表格解读（多模态）
> 【图文联合解读】**表8图文联合解读**

表8对比LM1B上微调3B token的BD3-LM在不同噪声调度下的PPL与变分NELBO。L'=4时裁剪U[0.45, 0.95]最优（PPL 29.21, NELBO 6.24），L'=16时U[0.3, 0.8]略胜（31.12 vs 31.42），二者均显著优于线性、对数、平方根、平方、余弦等标准调度。原文据此论证"裁剪掩码"为BD3-LM最佳选择：块越小应偏重掩码，块越大则偏轻。该表作为噪声调度的消融实验，为主方法中分段可调的掩码策略提供量化依据。

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
\M_{\text{full}} = \begin{bmatrix} \M_{BD} & \M_{OBC} \\ \mathbf{0} & \M_{BC} \end{bmatrix}
$$

$$
\log p_\theta(\x) = \sum_{\ell=1}^L \log p_\theta(\xl \mid \x^{<\ell}),
$$

$$
p_\theta(\x_s \mid \x_t) = \prod_{\ell=1}^L p_\theta(\xl_s \mid \x_t) = \sum_{\x} \left[\prod_{\ell=1}^L q(\xl_s \mid \xl_t, \xl) p_\theta(\xl \mid \x_t)\right],
$$

$$
\mathcal{L}(\x; \theta) = \E_q\Bigg[- \log p_\theta( \x | \x_{t(1)}) + \sum_{j=1}^T \KL[q(\x_{s(j)} | \x_{t(j)}, \x) \| p_\theta(\x_{s(j)} | \x_{t(j)})] + \KL[q(\x_{t(T)} | \x) \| p_\theta(\x_{t(T)})] \Bigg]
$$

$$
\log p_\theta(\x) &= \sum_{b = 1}^{B} \log p_\theta(\x^{b} \mid \x^{<b}),
$$

$$
p_\theta(\x_s^b \mid \x_t^b, \x^{<b}) = \sum_{\x^b} q(\x_s^b \mid \x_t^b, \x^b)p_\theta(\x^b\mid \x^b_t,\x^{<b})
$$

$$
- \log p_\theta(\x) \leq \mathcal{L}_\text{BD}(\x; \theta) := \sum_{b=1}^{B} \mathcal{L}(\x^b, \x^{<b}; \theta),
$$

$$
\x_\text{logits}^b, \mathbf{K}^b, \mathbf{V}^b \gets \x^b_\theta(\x^b_t, \mathbf{K}^{1:b-1}, \mathbf{V}^{1:b-1}) := \x^b_\theta(\x^b_t, \x^{<b}),
$$

$$
\mathcal{L}_\text{BD}(\mathbf{X}; \theta) := l(\mathbf{X}; \theta) = \frac{1}{K} \sum_{k=1}^K \sum_{b=1}^B \frac{\alpha_{t(k, b)}'}{1-\alpha_{t(k,b)}} \log p_\theta \left( \x^{(k),b} \mid \x_{t(k,b)}^{(k),b}, \x^{(k), <b} \right)
$$

$$
\text{Var}_{\mathbf{X}, t}\left[ \nabla_\theta l (\mathbf{X}; \theta) \right] &\approx \frac{1}{M-1} \sum_{m=1}^M \left\lVert \nabla_\theta l (\mathbf{X}^m; \theta) - \frac{1}{M} \sum_{m=1}^M \nabla_\theta l(\mathbf{X}^m; \theta) \right\rVert^2_2
$$

$$
[Q_t]_{ij} = \begin{cases} 1 & \text{if } i = j = m \\ \at & \text{if } i = j \neq m \\ 1-\at & \text{if } j = m, i \neq m \end{cases}
$$

$$
[Q_{t|s}]_{ij} = \begin{cases} 1 & \text{if } i = j = m \\ \ats & \text{if } i = j \neq m \\ 1-\ats & \text{if } j = m, i \neq m \end{cases}
$$

$$
q(\xl_t | \xl) = \text{Cat} \left( \xl_t; \overline{Q}_t \xl \right), \quad \text{with} \quad \overline{Q}_{t(i)} = Q_{t(1)} Q_{t(2)} \dots Q_{t(i)}
$$

$$
q(\xl_{s} | \xl_t, \xl) = \frac{q(\xl_t | \xl_{s}, \xl) q(\xl_{s} | \xl)}{q(\xl_t | \xl)} = \text{Cat} \left( \xl_{s}; \frac{Q_{t|s} \xl_t \odot Q_s^\top \xl}{{(\xl_t)}^\top Q_t^\top \xl} \right)
$$

$$
\mathcal{L}_{\text{diffusion}} &= \sum_{b=1}^{B} \mathbb{E}_{t \sim [0, 1]} \mathbb{E}_{q} \left[ \frac{\at'}{1-\at} \log p_\theta(\x^b \mid \x_t^b, \x^{<b}) \right]
$$

$$
\mathcal{L}_{\text{recons}} &= - \mathbb{E}_q \log \p (\x^b | \x_{t(1)}^b, \x^{<b}) \nonumber \\ &= - \log \p (\x^b | \x_{t(1)}^b = \x^b, \x^{<b}) \nonumber \\ &= 0
$$

$$
\mathcal{L}_{\text{BD}} (\x; \theta) &= \sum_{b=1}^{B} \mathbb{E}_{t \sim [0, 1]} \mathbb{E}_{q} \left[ \frac{\at'}{1-\at} \log p_\theta(\x^b \mid \x_t^b, \x^{<b}) \right]
$$

$$
-\log \p(\x) &\leq - \sum_{b=1}^{L} \mathbb{E}_{t \sim [0, 1]} \frac{1}{t} q(\x_t^b = \m | \x^b) \log p_\theta(\x^b \mid \x_t^b = \m,\x^{<b}) \nonumber \\ & \text{\footnotesize{ $\because q(\x^b_t = \m | \x^b) = t$, we get:}} \nonumber \\ &= - \sum_{b=1}^{L} \mathbb{E}_{t \sim [0, 1]} \log p_\theta(\x^b \mid \x_t^b = \m,\x^{<b}) \nonumber \\ &= - \sum_{b=1}^{L} \log p_\theta(\x^b \mid \m, \x^{<b})
$$

$$
\mathcal{L}_1 &= \sum_{b=1}^{L} \log \mathbb{E}_{t \sim [0, 1]} \mathbb{E}_q \frac{\at'}{1-\at} p_\theta(\x^b \mid \x_t^b,\x^{<b}) \nonumber \\ &= - \sum_{b=1}^{L} \log p_\theta(\x^b \mid \m,\x^{<b})
$$

$$
\mathcal{L}_2 = \sum_{b=1}^{L/2} \log \mathbb{E}_{t \sim [0, 1]} \mathbb{E}_q \frac{\at'}{1-\at} p_\theta(\x^b \mid \x_t^b, \x^{<b})
$$

## 相关论文

- [[dflash-block-diffusion-for-flash-speculative-decoding]] — DFlash: Block Diffusion for Flash Speculative Decoding
- [[eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees]] — EAGLE-2: Faster Inference of Language Models with Dynamic Draft Trees
- [[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]] — EAGLE-3: Scaling up Inference Acceleration of Large Language Models via Training-Time Test
- [[dspark-confidence-scheduled-speculative-decoding-with-semi-autoregressive-generation]] — DSpark: Confidence-Scheduled Speculative Decoding with Semi-Autoregressive Generation
- [[longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification]] — LongSpec: Long-Context Lossless Speculative Decoding with Efficient Drafting and Verification
- [[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]] — MEDUSA: Simple LLM Inference Acceleration Framework with Multiple Decoding Heads

## 技术点深读（DEEP）

![[deep/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models.txt`（98874 字符）供引用检索。