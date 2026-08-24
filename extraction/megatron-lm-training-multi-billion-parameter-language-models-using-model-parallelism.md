---
paper_num: "49"
title: "Megatron-LM: Training Multi-Billion Parameter Language Models Using Model Parallelism"
authors: "Model Parallelism Mohammad Shoeybi 1 2 Mostofa Patwary 1 2 Raul Puri 1 2 Patrick LeGresley 2 Jared Casper 2 Bryan Catanzaro 2"
date: "2026/1/4"
arxiv: "https://arxiv.org/abs/1909.08053"
pdf: "papers/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism.pdf"
slug: "megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism"
tags: [training]
---

# Megatron-LM: Training Multi-Billion Parameter Language Models Using Model Parallelism

> [!abstract] 摘要（原文）
> 1\. 🚀 Megatron-LM 提出了一种简单高效的层内模型并行方法，通过在原生 PyTorch 中少量修改即可训练数十亿参数的 Transformer 模型。 2. 📈 该方法成功地将 Transformer 模型扩展到 8.3 亿参数，使用 512 个 GPU 实现了 15.1 PetaFLOPs 的可持续性能和 76% 的扩展效率，并与流水线并行互补。 3. 💡 研究还发现 BERT 模型中 Layer Normalization 的放置对模型扩展至关重要，并用 GPT-2 和 BERT 模型在 WikiText103、LAMBADA 和 RACE 等数据集上取得了 SOTA 结果。

## 元信息
- **发表日期**: 2026/1/4
- **作者**: Model Parallelism Mohammad Shoeybi 1 2 Mostofa Patwary 1 2 Raul Puri 1 2 Patrick LeGresley 2 Jared Casper 2 Bryan Catanzaro 2
- **arXiv**: https://arxiv.org/abs/1909.08053
- **本地 PDF**: `papers/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism.pdf`
- **页数**: 15

## 图表（原文 caption + 页码）

### Figure 1 (p.2) ⭐深度解读
![[assets/crops/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-fig01.png]]
*整页渲染: ![[assets/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-p02.png]]*
> [!quote] caption
> Model (blue) and model+data (green) parallel FLOPS as a function of number of GPUs. Model parallel (blue): up to 8-way model parallel weak scaling with approximately 1 billion parameters per GPU (e.g. 2 billion for 2 GPUs and 4 billion for 4 GPUs). Model+data parallel (green): similar conﬁguration as model parallel combined with 64-way data parallel. a baseline by training a model of 1.2 billion p

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图1为对数-对数坐标下 PetaFLOPs/s 随 GPU 数的变化：蓝色模型并行（1–8 卡，≈0.04→0.23 PFLOPs/s）；绿色模型+数据并行（64–512 卡，≈2.5→16 PFLOPs/s），两段曲线均紧贴灰色"线性"虚线参考。结论：纯模型并行与"模型+数据"混合并行均实现近似线性的弱扩展效率，512 卡达到 ~16 PFLOPs/s。作用：在论文主体提出 transformer 层内 MLP/Attention 切分优化之前，先以实测 FLOPS 证明并行框架具备近线性可扩展性，为后续大模型训练方案奠定可行性基础。

### Figure 2 (p.3) ⭐深度解读
![[assets/crops/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-fig02.png]]
*整页渲染: ![[assets/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-p03.png]]*
> [!quote] caption
> Transformer Architecture. Purple blocks correspond to fully connected layers. Each blue block represents a single trans- former layer that is replicated N times. and compute efﬁciency. The original transformer formula- tion was designed as a machine translation architecture that transforms an input sequence into another output sequence using two parts, an Encoder and Decoder. However, recent work 

> [!tip] 技术解读（多模态）
> 【图文联合解读】该图展示Transformer单层数据流：输入嵌入→Layer Norm→Attention子层（Self-Attention+Dropout+残差Add）→Layer Norm→MLP子层（H→4H经GeLU激活后4H→H，含Dropout与残差Add），整个块重复x L次后接输出层。紫色块为全连接层，MLP含4倍维度扩展。原文以此论证Transformer结构高度规整且MLP参数占比巨大，为后续按注意力头和MLP维度进行张量切分的模型并行方案提供结构基础，是实现千亿参数高效训练的关键依据。

### Figure 3 (p.4) ⭐深度解读
![[assets/crops/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-fig03.png]]
*整页渲染: ![[assets/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-p04.png]]*
> [!quote] caption
> Blocks of Transformer with Model Parallelism. f and g are conjugate. f is an identity operator in the forward pass and all reduce in the backward pass while g is an all reduce in the forward pass and identity in the backward pass.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

**1) 核心对象与结构：** 图示 Transformer 块的两个子模块——(a) MLP 和 (b) Self-Attention——沿纵向切分至 2 个 GPU。MLP 中 X 经 f 算子分为 A₁、A₂ 两路并行计算后由 g 合并；Self-Attention 中 X 经 f 分为两组注意力头（Q₁/Q₂、K₁/K₂、V₁/V₂），并行 Softmax+Dropout 后拼接输出。

**2) 关键技术结论：** f 与 g 是**共轭算子**——f 在前向为恒等、反向为 all-reduce；g 在前向为 all-reduce、反向为恒等。即一次通信在前向与反向间复用，避免冗余同步，仅在子模块边界处通信即可完成跨 GPU 计算。

**3) 在论文中的作用：** 该图是 Megatron-LM 模型并行的基本构建块，论证了 MLP 列切分与 Attention 头切分均无需额外参数同步即可正确反向传播，为后续训练 83 亿/175 亿参数模型提供了核心并行原语与通信正确性保证。

### Figure 4 (p.5) ⭐深度解读
![[assets/crops/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-fig04.png]]
*整页渲染: ![[assets/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-p05.png]]*
> [!quote] caption
> Communication operations in a transformer layer. There are 4 total communication operations in the forward and backward pass of a single model parallel transformer layer. contains a portion of the embedding table, an all-reduce (g operator) is required after the input embedding. For the output embedding, one approach is to perform the parallel GEMM [Y1, Y2] = [XE1, XE2] to obtain the logits, add a

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

1) **核心对象与结构**：图示单个模型并行 Transformer 层。流水线为 X → LayerNorm → Self-Attention(Q/K/V Linear + 输出 Linear) → Dropout → 残差⊕ → LayerNorm → MLP(Linear → GeLU → Linear) → Dropout → 残差⊕ → Y。其中 Self-Attention 与 MLP 两块以虚框标注为"Model Parallel"（各占一份权重分片），LayerNorm/Dropout/⊕在每卡本地复制。**每层共 4 次 all-reduce**：两块各在 fwd+bwd 中各 1 次（每个 Model Parallel 块对应 "2 All-Reduces"）。

2) **原文论证的关键结论**：在列并行 GEMM Y_i = X A_i 下，每块前向需 1 次 all-reduce 聚合 Y；反向梯度 ∂X 需另 1 次 all-reduce。故单层前向+反向共 4 次集合通信，**与层数线性、与数据并行组解耦**，通信量可控。

3) **整体方法链作用**：这是 Megatron 张量并行的"通信账本"基础——证明仅靠列并行+行并行（无参数服务器、无额外同步）即可扩展到数十亿参数，为后续 PTD-P（与流水并行/Pipeline 组合）及在 8/16 卡 DGX 上训练 GPT-3 8.3B/22.4B 提供通信开销量化的理论依据。

### Figure 5 (p.6) ⭐深度解读
![[assets/crops/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-fig05.png]]
*整页渲染: ![[assets/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-p06.png]]*
> [!quote] caption
> Model and model + data parallel weak scaling efﬁciency as a function of the number of GPUs. done by scaling the batch-size, however, this approach does not address training large models that do not ﬁt on a single GPU and it leads to training convergence degradation for large batch sizes. In contrast, here we use weak scaling to train larger models that were not possible otherwise. The baseline for

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图5图文联合解读：**

图5展示两类并行的弱扩展效率：模型并行（1→8 GPU）由100%降至77%；模型+数据并行（64→512 GPU）由96%缓降至74%。原文借此论证：扩展至512卡时效率仍保持74%以上，证明模型并行及与数据并行结合可有效训练超大模型，突破单卡显存限制并保持高利用率，为论文核心实验提供关键支撑。

### Figure 6 (p.7) ⭐深度解读
![[assets/crops/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-fig06.png]]
*整页渲染: ![[assets/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-p07.png]]*
> [!quote] caption
> Validation set perplexity. All language models are trained for 300k iterations. Larger language models converge notice- ably faster and converge to lower validation perplexities than their smaller counterparts.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图示核心：** 横轴为训练迭代次数（0–300k），纵轴为验证集 LM 困惑度（8–24）。三条曲线分别对应 355M（蓝，收敛于 ~15）、2.5B（红，~11）、8.3B（黄，~9）三个 GPT-2 模型，均训练 300k 迭代。

**关键结论：** 在相同迭代预算下，模型规模越大，下降越陡、收敛越快、终值困惑度越低，明确证实了参数规模与收敛性能的扩展效应（scaling effect）。

**论文作用：** 该图直接服务于核心论点——即所提出的模型并行方案可成功训练出数十亿参数 Transformer 并获得更优下游能力。它以收敛曲线为关键实证，回击了对超大模型训练可行性的质疑，支撑后文 8.3B 模型质量评估的合理性。

### Figure 7 (p.8) ⭐深度解读
![[assets/crops/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-fig07.png]]
*整页渲染: ![[assets/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-p08.png]]*
> [!quote] caption
> Training loss for BERT model using the original architec- ture (a) and the rearranged architecture (b). Left ﬁgure shows the training loss for 336M and 752M BERT model. While the original architecture performs well on the 336M model, the modiﬁcations in (b) enable stable training with lower training loss.

> [!tip] 技术解读（多模态）
> 【图文联合解读】图左半对比Transformer块：(a)原始结构为LN→Self-Attn+残差→LN→MLP+残差；(b)将LN置于残差之后、调整其位置。右半为训练loss曲线（0–500k次迭代，纵轴0–8）：752M模型采用(a)时在约230k iter处loss骤升至~7（训练发散），336M用(a)与752M用(b)均稳定下降至~1.0–1.3。

**核心结论**：原始架构在752M规模出现训练不稳定/发散，而调整LN放置位置的(b)架构可实现稳定收敛并取得更低loss。

**论文作用**：为模型并行扩展至数十亿参数所必需的Transformer架构改造（LN-残差顺序调整）提供了直接实验验证，是支撑后续GPT类大规模模型训练的稳定性基础。

### Figure 8 (p.12) ⭐深度解读
![[assets/crops/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-fig08.png]]
*整页渲染: ![[assets/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-p12.png]]*
> [!quote] caption
> Grouping of GPUs for hybrid model and data parallelism with 8-way model parallel and 64-way data parallel. C. Text Samples

> [!tip] 技术解读（多模态）
> 【图文联合解读】图示512块GPU的两级组织：纵向64个**model parallel group**，每组8卡（GPU-1~8…505~512），承担Transformer层张量切分；横向8个**data parallel group**跨各模型组按对应位置GPU互连（如各组第k卡聚合），构成64路数据并行维度。

**论证结论**：8路模型并行与64路数据并行可正交组合，既缓解单卡显存瓶颈，又通过batch维扩展吞吐。

**论文作用**：作为方法部分混合并行（hybrid parallelism）方案的拓扑实例，与Figure 7互补，支撑"在512卡集群上高效训练多百亿参数模型"这一核心可扩展性论断。

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.6) ⭐深度解读
![[assets/crops/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-tab01.png]]
> [!quote] caption
> Parameters used for scaling studies. Hidden size per atten-

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 1 图文联合解读**

该表列出四档弱扩展实验配置：hidden size 1536/1920/2304/3072，注意力头16/20/24/32（每头固定96维），层数40/54/64/72，模型规模1.2B/2.5B/4.2B/8.3B参；模型并行度由1→8卡，配以64×数据并行可扩至512卡。配合下方柱状图，模型并行效率从100%降至77%，模型+数据并行从96%降至74%，论证了：8路张量切片+64路数据并行的组合可在512卡上高效训练8.3B模型，弱扩展效率维持74%以上，验证该并行策略可线性逼近万卡级大规模训练。该表为后续端到端GPT类训练实验提供了模型规格基线，是论文"证明模型并行可行性"实验链路的核心配置依据。

### Table 2 (p.7) ⭐深度解读
![[assets/crops/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-tab02.png]]
> [!quote] caption
> Model conﬁgurations used for GPT-2.

> [!tip] 表格解读（多模态）
> 【图文联合解读】Table 2 列出 GPT-2 三种规模的模型配置：355M（24 层/h=1024/16 头/64 维/64 卡/0.86 天）、2.5B（54 层/h=1920/20 头/96 维/128 卡/2.27 天）、8.3B（72 层/h=3072/24 头/128 维/512 卡/2.10 天）。量化揭示两点：(1) 模型沿"加深（层数）+加宽（隐藏维与头数）"双轴同步扩展；(2) 8.3B 模型在 512 卡仅 2.10 天/epoch，并行效率反优于 2.5B 在 128 卡上的 2.27 天。该表作为实验链路的核心量化证据，证明模型并行可将 GPT 风格 Transformer 扩展至十亿参数级且保持训练效率，是论文"scaling up billion-parameter language models"主张的关键支撑。

### Table 3 (p.7) ⭐深度解读
![[assets/crops/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-tab03.png]]
> [!quote] caption
> Zero-shot results. SOTA are from ( Khandelwal et al. ,

> [!tip] 表格解读（多模态）
> 【图文联合解读】**核心对象与数据**：表 3 展示 355M / 2.5B / 8.3B 三档参数模型在零样本任务上的表现——Wikitext103 困惑度依次为 19.31 → 12.76 → **10.81**，LAMBADA 准确率依次为 45.18% → 61.73% → **66.51%**，并与 Previous SOTA（15.79 / 63.24%）横向对照。

**关键结论**：参数规模与零样本能力呈强正相关，8.3B 模型在两项指标上均刷新 SOTA，验证了借助模型并行训练出的大模型具备更强的泛化能力，并非仅靠记忆训练分布。

**论文链路作用**：作为整篇的"效果落点"，与 Figure 3（模型并行切分方案）首尾呼应——前者证明"能做"，本表证明"做大且更好"，闭环论证模型并行路线的可行性。

### Table 6 (p.11) ⭐深度解读
![[assets/crops/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-tab06.png]]
> [!quote] caption
> Hyperparameters for ﬁnetuning BERT model on down-

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 6 图文联合解读：**

1) **核心结构与数据**：表列出 336M / 1.3B / 3.8B 三档 BERT 模型在 MNLI、QQP、SQuAD 1.1、SQuAD 2.0、RACE 五个下游任务上的微调超参。Batch size 在 16–256 之间（如 QQP 用 256，RACE 仅用 16–32）；学习率集中于 1e-5 至 5e-5；训练轮数随任务差异显著（MNLI=10，QQP=12，SQuAD=2，RACE=3）。

2) **论证结论**（注：引用段落实际论述的是 Figure 6 的 GPT-2 验证困惑度曲线，而非本表）：作者通过为每任务、每模型规模**单独调优**超参（而非沿用统一设置），保证大规模 BERT 的下游评估公平、可复现，为"更大模型在 GLUE/SQuAD/RACE 上取得更优结果"提供可信的实验支撑。

3) **论文链路作用**：该表处于"下游任务评估"环节，与 Figure 5、Table 5 的零样本/单样本结果互补，共同构成 Megatron-LM 证明"模型并行 + 更大参数 = 更强泛化"的完整证据链。

### Table 7 (p.15) ⭐深度解读
![[assets/crops/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-tab07.png]]
> [!quote] caption
> Effect of number of attention heads on scaling on 8.3

> [!tip] 表格解读（多模态）
> 【图文联合解读】**表7图文联合解读**

表7展示在8.3B参数、8-way模型并行下，三种attention head配置对scaling efficiency的影响：16头×192维/82%、24头×128维/80%、32头×96维/77%。

数据呈现明显单调趋势：头数越多、单头维度越小，扩展效率反而下降，最多相差5个百分点。原文借此论证：在固定总隐藏维度的前提下，attention head并非越多越好——**少头+大维度**的设计更有利于大规模模型并行下的计算与通信平衡，扩展性更优。

该表属于论文方法验证链路的关键一环，与Table 6（model parallelism扩展）共同支撑"简化架构+张量并行"的可行性，为后续更大规模（数十B参数）模型并行训练的head配置选择提供实证依据。

### Table 8 (p.15) ⭐深度解读
![[assets/crops/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-tab08.png]]
> [!quote] caption
> Speedup obtained for the 1.2 billion parameters model

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 8 图文联合解读**

1) **核心对象与结构**：表格展示 1.2B 参数模型在 8-way 模型并行下的扩展效率（Scaling Efficiency），对比三种注意力头配置：(16 头×192 维)、(24 头×128 维)、(32 头×96 维)，对应效率分别为 **82%、80%、77%**，总隐藏维度均保持 3072。

2) **关键技术结论**：头数越少、单头维度越大，并行加速效果越好（16 头最高 82%）；但即使采用 32 头最细粒度划分，效率仍维持在 77% 以上，证明 **8-way 模型并行在不同注意力划分方案下均具备良好的可扩展性**，且无明显通信瓶颈。

3) **在论文中的作用**：作为 Figure 8（GPU 分组拓扑图）的量化补充，Table 8 用具体数字验证了混合并行方案在 1.2B 规模下的实际收益（>75% 效率），与论文主体"模型并行近乎线性扩展"的核心主张相互支撑，构成对方法有效性的关键实验证据。

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
Y = \textrm{GeLU}(XA)
$$

$$
X = [X_1, X_2], \ A=\begin{bmatrix} A_1 \\ A_2 \end{bmatrix}.
$$

$$
[Y_1, Y_2]= [\textrm{GeLU}(XA_1), \textrm{GeLU}(XA_2)]
$$

$$
PPL= \exp({-\frac{1}{T_o}\sum_{t}^{T} \text{log} P(t|0:t-1))}
$$

## 相关论文

- [[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]] — Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM
- [[zero-memory-optimizations-toward-training-trillion-parameter-models]] — ZeRO: Memory Optimizations Toward Training Trillion Parameter Models
- [[scalable-training-of-mixture-of-experts-models-with-megatron-core]] — Scalable Training of Mixture-of-Experts Models with Megatron Core
- [[gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints]] — GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints
- [[efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey]] — Efficient Training of Large Language Models on Distributed Infrastructures: A Survey
- [[megascale-scaling-large-language-model-training-to-more-than-10000-gpus]] — MegaScale: Scaling Large Language Model Training to More Than 10,000 GPUs

## 技术点深读（DEEP）

![[deep/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism.txt`（68294 字符）供引用检索。