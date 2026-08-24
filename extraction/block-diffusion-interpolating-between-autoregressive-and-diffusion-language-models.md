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
> 【图文联合解读】图横向对比三范式，各以4属性(质量/长度/KV缓存/并行性)+逐token/逐块文例呈现：**自回归**高质量/可变长/有KV缓存但不可并行，逐token生成 "There are three categories of the average → rate → rate of…"；**扩散**质量较低/固定长/无KV缓存但可并行，整块同步去噪 "Repeal the reusability cuts…reduce the deficit"；**块扩散(本文)**四项均✓，块内并行扩散+块间以先前块为条件自回归式接续生成 "On September 17, 2016, we will be giving the beta-release of the…to our server testing"。

**论证结论**：BD 通过分块机制同时消除 AR 的不可并行性与扩散的固定长度/无KV缓存痛点，兼取两类模型之长。

**论文作用**：作为开篇 Figure 1 (p.2) 动机图，在 Method 概述前直观确立方法价值前提；与后续 Table 1 (p.5) 在 LM1B 16B token 上的困惑度实证形成"概念动机—实验验证"闭环，支撑全篇 "插值式框架" 的叙事。

### Figure 2 (p.6) ⭐深度解读
![[assets/crops/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-fig02.png]]
*整页渲染: ![[assets/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-p06.png]]*
> [!quote] caption
> Train NLLs for modeling the per-token likelihood on LM1B. Models are trained on 16B tokens. Training under the discrete diffusion NELBO, where half of the tokens in a batch are masked on average, has similar training variance to an AR model with a random batch size. so that Et∼U[0,1]q(xℓ t = m|xℓ) = 0.5. Thus, training on the diffusion objective involves estimating loss gradients with 2x fewer tok

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图2解读（LM1B，250k步训练NLL曲线）**

1）展示LM1B上四模型训练负对数似然：BD3-LM(NELBO)（棕红）、BD3-LM(调优调度)（紫）、AR（橙）、AR(随机batch)（绿）。NELBO曲线全程剧烈震荡，调优调度后与AR均平滑收敛至≈3.1–3.15。

2）论证NELBO训练方差≈随机batch的AR：因平均mask约一半token，仅半数贡献梯度，等效batch减半，故方差水平相当。

3）在论文链路中作为block-diffusion训练稳定性问题的实证起点，引出后续"调优调度→消除方差→比肩AR"的方案，与Table 2的PPL/方差量化呼应。

### Figure 3 (p.21) ⭐深度解读
![[assets/crops/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-fig03.png]]
*整页渲染: ![[assets/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-p21.png]]*
> [!quote] caption
> x1 t x2 t x3 t x1 x2 x3 x1 t x2 t x3 t x1 x2 x3

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图3 联合解读**

图3展示 L=6、块大小 L′=2 下的专用注意力掩码可视化。坐标轴分两半：上方 3 行为带噪待去噪 token x_t¹~x_t³，下方 3 行为已生成的干净 token x¹~x³。三色区域对应三类掩码：橙色"块对角 M_BD"实现同块内待去噪 token 的双向自注意力；蓝色"偏置块因果 M_OBC"使待去噪块只能关注其前序已生成块（条件上下文）；黄色"块因果 M_BC"保证生成新干净块时仅看前序干净块。

该图核心论证：**块扩散**通过组合三种掩码，使块内可并行去噪（类扩散）、块间保持严格因果（类自回归），从而插值连接 AR 与纯扩散模型。它是全文方法基石，并直接支撑 Figure 4 将其映射为 FlexAttention 稀疏掩码，在 A5000、L=1024、B=16 下取得约 5× 加速与显著显存节省。

### Figure 4 (p.22) ⭐深度解读
![[assets/crops/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-fig04.png]]
*整页渲染: ![[assets/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-p22.png]]*
> [!quote] caption
> We can adapt the masking strategy from Fig. 3 to a FlexAttention compatible sparse masking function as above. This enables the creation of a customized JIT attention operation that uses significantly less memory with up to ≈5X speedup over the naive native scaled_dot_product_attention implementation in PyTorch (≥2.5) on a A5000 GPU with L = 1024 and batch size B = 16. 22

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图4解读：**

图4展示`block_diff_mask`函数：将block diffusion注意力mask分解为三个布尔子掩码——M_BD（块对角，对应x_t块内自注意力）、M_OBC（偏移块因果，对应x_t对x_0的条件跨注意力）、M_BC（块因果，对应x_0更新），通过OR合并为FlexAttention兼容的稀疏掩码。

原文用它论证：在A5000 GPU、L=1024、B=16条件下，自定义JIT注意力较PyTorch≥2.5原生scaled_dot_product_attention实现可达≈5倍加速并显著降显存。

该实现是把Fig.3理论掩码落地的关键工程模块，使AR–扩散混合架构在长序列上具备实际可训练性与可推理性，是论文方法链路中的效率支撑点。

### Figure 5 (p.23) ⭐深度解读
![[assets/crops/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-fig05.png]]
*整页渲染: ![[assets/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-p23.png]]*
> [!quote] caption
> Attention computation using FlexAttention with our proposed custom mask.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**注意：图片内容与原文段落存在明显错配。** 图片实际是代码片段（PyTorch FlexAttention 调用），而原文段落描述的应是某张 OWT 数据上的 PPL 结果表/图，非本图。以下仅基于真实图片内容解读：

## 1) 核心对象与结构
图片是一段 ≤20 行的 PyTorch 代码，实现基于 `torch.nn.attention.flex_attention` 的块扩散注意力计算：(a) 用 `partial` 绑定 `block_diff_mask` 的 `seq_len` 与 `block_size` 参数；(b) 调用 `create_block_mask` 生成 `seq_len*2 × seq_len*2` 的稀疏块掩码（2× 对应扩散去噪的"噪声输入+干净目标"拼接）；(c) 用 `@torch.compile(fullgraph=True, mode="max-autotune-no-cudagraphs")` 编译加速；(d) 封装 `single_pass_block_diff_attn(q,k,v,block_mask)` 单次前向函数。

## 2) 论证的技术结论
该代码证明 BD3-LMs 的核心算子——**块大小可调的分块因果注意力**——可在 PyTorch 原生 `FlexAttention` 框架下以 **稀疏掩码 + 编译优化** 方式高效实现，无需手写 CUDA kernel，为"块长越小越逼近 AR"的插值策略（block_size 控制因果粒度）提供了可落地的工程支撑。

## 3) 在论文链路中的作用
此图属**方法实现层**（Methods/Implementation），与 Table 3、Table 5 等**实验结论层**互补：前者证明想法可行，后者证明想法有效。两者共同构成"理论→高效实现→规模验证"的完整论证链。

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
> 【图文联合解读】**Table 1 图文联合解读**

**1) 表格数据（LM1B、16B tokens、单 token 生成 PPL）：**
- AR（基线自回归）：**22.88**
- AR + random batch size（仅控制有效 token 数）：24.37
- BD3-LM L′=1：≤ 25.56（与 AR 存在约 2.7 点差距）
- BD3-LM L′=1 + tuned schedule（调优噪声调度后）：**22.88**

**2) 关键技术结论：** 表格用于支撑原文"block diffusion 参数化在 L′=1 极限下与 AR 的 NLL 期望等价"的理论声明。实验显示，尽管两者目标在期望上等价，BD3-LM 仍出现约 2 点的 PPL 差距，但该差距并非方法本身缺陷，而是训练方差所致——AR 对全部 L 个 token 算交叉熵，而 BD L′=1 仅对掩码 token 计算，导致方差更大；通过"随机 batch size"的对照实验（AR 同样缩减有效 token 后 PPL 升到 24.37）以及**调优噪声调度**，差距被完全闭合，BD3-LM L′=1 达到与 AR 完全相同的 22.88。

**3) 在论文链路中的作用：** 该表是论文核心主张"block diffusion 在 AR 与纯扩散之间有效插值、且不牺牲生成质量"的**经验锚点**；它把抽象的理论等价性转化为可验证的数值结果，为后续展示 KV 缓存与并行采样带来的推理加速收益提供了"质量无损"前提。

### Table 2 (p.7) ⭐深度解读
![[assets/crops/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-tab02.png]]
> [!quote] caption
> Perplexities (PPLs; ↓) and variances of the NELBO Var𝐗,t​[ℒBD​(𝐗,θ)] (Var. NELBO; ↓). Models are trained on LM1B using a linear schedule for 65B tokens, then finetuned for 10B tokens.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 2 图文联合解读：**

该表呈现 3 个训练阶段（以验证损失 L*=31.72/31.27/29.23 表示模型从差到好）×4 种块大小调度 L*∈{[0,0.5], [.3,.8], [-.5,1], [0,1]} 下，块扩散的 PPL 与 NELBO 梯度方差。定量规律：① 随训练推进 PPL 逐行下降（如 [0,0.5] 从 1.03→7.90→32.68）；② 全扩散调度 [0,1] 的 Var. NELBO 在 L*=31.72 时高达 **128**，而任一含较小块的调度稳定在 **≈31** 量级，降低近 4×；③ L*=29.23 时 [0,1] 方差仍为 4，而分块方案仅 ≈29。

论文借此论证：块扩散通过分块在 AR（低方差）与全扩散（高方差）之间插值，使 NELBO 方差量级与 AR 可比，验证了"块大小可调即可在两极限间平滑权衡"的方法核心主张，是论证其作为插值框架可行性的关键实验支点。

### Table 3 (p.7) ⭐深度解读
![[assets/crops/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-tab03.png]]
> [!quote] caption
> Test perplexities (PPL; ↓ ) of mod- els trained for 65B tokens on LM1B. Best diffusion value is bolded.

> [!tip] 表格解读（多模态）
> 【图文联合解读】1）表3比较BD3-LM在LM1B训练65B token后的测试：块长 \(L'=128/16/4\)，掩码分布取 \(\mathcal U[0,.5]\)、\([.3,.8]\)、\([.5,1]\)或\([0,1]\)，指标为PPL与Var. NELBO。  
2）\(L'=4,\mathcal U[.5,1]\)以29.16获最低PPL，方差8.28；\(L'=128,\mathcal U[0,.5]\)以1.03获最低方差，但PPL为31.72。  
3）该消融连接掩码设计与FlexAttention稀疏实现（正文称A5000上最高约5×加速），用于确定质量—稳定性折中配置。

### Table 4 (p.8) ⭐深度解读
![[assets/crops/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-tab04.png]]
> [!quote] caption
> Test perplexities (PPL; ↓ ) on OWT for models trained for 524B to- kens. Best diffusion value is bolded.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 4 图文联合解读：**

表4展示在 OpenWebText（OWT）上训练524B tokens后各模型的测试困惑度（PPL）：自回归基线 AR 为 17.54；先前的扩散方法 SEDD ≤24.10、MDLM ≤22.98；BD3-LMs 随块长 L' 减小而性能提升，L'=16/8/4 分别达到 ≤22.27 / 21.68 / 20.73，其中 L'=4 加粗为最佳扩散结果。

原文借此论证两点核心结论：①BD3-LMs 在 OWT 上同样全面优于既有扩散语言模型（SEDD、MDLM），延续了 LM1B 上的趋势；②L' 越小越逼近 AR 的生成质量，直观体现"块扩散在自回归与纯扩散之间插值"的方法论思想。

该表是论文主实验链中的关键节点：先用 Table 3/4 确立 BD3-LMs 在分布内基准（PPL）上的最优扩散地位，再以 Table 5 展示零样本泛化能力，从而完整支撑"块扩散兼具 AR 高质量与扩散并行灵活性"的核心主张。

### Table 5 (p.8) ⭐深度解读
![[assets/crops/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-tab05.png]]
> [!quote] caption
> Zero-shot validation perplexities ( ↓ ) of models trained for 524B tokens on OWT. All perplexities for diffusion models are upper bounds.

> [!tip] 表格解读（多模态）
> 【图文联合解读】Table 5 列出在 OWT 上训练 524B tokens 后模型的零样本验证困惑度（PPL↓，扩散值为上界），共 6 行：AR 基线 17.54；扩散基线 SEDD ≤24.10、MDLM ≤22.98；BD3-LMs 在 L'=16/8/4 时依次为 ≤22.27/21.68/20.73，L'=4（加粗）为扩散类最佳。

技术结论：① BD3-LMs 较 MDLM 最高约 9.8%、较 SEDD 约 13.9% 改进，与 Table 3 LM1B 趋势一致；② 块长缩短、PPL 单调下降（22.27→20.73），证实"块扩散在 AR 与全扩散间插值"在大规模训练上仍正向、可扩展。

链路作用：作为 Table 3 的数据规模扩展（LM1B→OWT 524B），与零样本泛化结果一起，是 BD3-LMs 性能优越性实证链关键一环。

### Table 6 (p.8) ⭐深度解读
![[assets/crops/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-tab06.png]]
> [!quote] caption
> Generation length statistics from sampling 500 documents from models trained on OWT.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读**

**说明**：图片正文中呈现的表格内容为各模型（AR、SEDD、MDLM、BD3-LM L′=4）在 PTB/Wikitext/LM1B/Lambada/AG News/Pubmed/Arxiv 七个数据集上的生成困惑度（gPPL，越低越好，加粗为最优），AR 在 4 个数据集上最优（81.07/25.32/51.14/52.11），MDLM 在 Lambada（48.29）和 Arxiv（37.89）最优，BD3-LM L′=4 在 Pubmed（42.52）最优。**这与所给 Table 6 caption（"采样 500 篇文档的生成长度统计"）不符——表中数值为困惑度而非长度，疑似 caption 与表格错配或截取有误，下文按实际所见内容解读。**

**①核心对象**：对比 AR 与三类扩散 LM（SEDD、MDLM、BD3-LM）在零样本 gPPL 上的表现，AR 整体领先，BD3-LM L′=4 在多数数据集上接近甚至优于 SEDD/MDLM。

**②技术结论**：作为对 §6.2"可变长度序列生成"章节的支撑证据，说明 BD3-LM 在保持扩散框架可变长生成能力的同时，样本质量已具竞争力，并非以牺牲质量换长度。

**③论文链路作用**：承接前述 MAUVE/perplexity 评估，体现"块扩散插值"在保 AR-级别质量的同时突破固定上下文限制，是论文"质量+灵活长度"双优论点的关键拼图。

### Table 7 (p.9) ⭐深度解读
![[assets/crops/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-tab07.png]]
> [!quote] caption
> Generative perplexity (Gen. PPL; ↓ ) and number of function evaluations (NFEs; ↓ ) of 300 samples of lengths L = 1024 , 2048 . All models are trained on OWT. AR, SEDD, MDLM, BD3-LMs use 110M parameters and are trained on 524B tokens, while SSD-LM uses 400M parameters and is pre-trained on 122B token

> [!tip] 表格解读（多模态）
> 【图文联合解读】【对象与数据】表列OWT上L=1024/2048各模型Gen.PPL(↓)与NFE(↓)。AR基线14.1/13.2,NFE 1K-2K;纯扩散SEDD 52.0、MDLM 46.8/41.3(NFE同量级但PPL高);SSD-LM L'=25达37.2/35.3却需40K-80K NFE;BD3-LMs L'=16:281.3/281.9(扩散步不足导致质量崩溃)、L'=8:33.4/31.5、**L'=4:30.4/28.2**(最优扩散值,加粗),NFE仅1K-2K。

【关键结论与作用】BD3-LMs以与AR同量级NFE取得扩散方法中最佳PPL,显著优于纯扩散(SEDD/MDLM)及高开销的SSD-LM,块越小质量越优。此表定量证明块扩散在效率-质量权衡上成功插值AR与扩散,既保留AR的逐块一致性又具块内并行,是论文方法有效性的核心实验证据。

### Table 8 (p.9) ⭐深度解读
![[assets/crops/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-tab08.png]]
> [!quote] caption
> Effect of the noise schedule on like- lihood estimation. We finetune BD3-LMs on 3B tokens from LM1B and evaluate on a linear schedule. For clipped schedules, we compare optimal clipping for L ′ = 4 , 16 .

> [!tip] 表格解读（多模态）
> 【图文联合解读】Table 8在LM1B 3B tokens上微调BD3-LM，比较各噪声调度在L′=4与L′=16下的PPL与Var. NELBO。L′=4时clipped U[0.45,0.95]最优（PPL 29.21，NELBO 6.24）；L′=16时clipped U[0.3,0.8]最优（PPL 31.12，NELBO 3.58），均显著优于linear、log、sqrt、cosine等标准调度。

原文借此论证两点：(1) clipped masking全面优于标准噪声调度；(2) 最优掩码强度与块大小耦合——小块宜重掩码，大块宜轻掩码。该表为块扩散模型的噪声调度选择提供消融依据，支撑likelihood评估与超参设计，是方法链路中关键的消融实验。

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