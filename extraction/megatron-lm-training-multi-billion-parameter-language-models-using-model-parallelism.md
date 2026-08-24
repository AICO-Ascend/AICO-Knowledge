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
> 【图文联合解读】图1以log-log坐标展示PetaFLOPs/秒随GPU数的变化：蓝线（纯模型并行，1–8 GPU）由~0.04增至~0.24；绿线（模型+64路数据并行，64–512 GPU）由~2.5增至~14 PFLOPs/s；两条曲线均紧贴灰色虚线（理想线性）。结论：两种并行策略均接近理想弱扩展，验证Megatron高效可扩展。作用：作为开篇性能证据，为后续训练3B、8.3B乃至83B参数模型的可扩展性提供关键支撑。

### Figure 2 (p.3) ⭐深度解读
![[assets/crops/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-fig02.png]]
*整页渲染: ![[assets/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-p03.png]]*
> [!quote] caption
> Transformer Architecture. Purple blocks correspond to fully connected layers. Each blue block represents a single trans- former layer that is replicated N times. and compute efﬁciency. The original transformer formula- tion was designed as a machine translation architecture that transforms an input sequence into another output sequence using two parts, an Encoder and Decoder. However, recent work 

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图2展示了GPT-2风格解码器Transformer架构。核心结构为：底部输入嵌入(带Dropout)→Layer Norm→橙色Attention块(内含Self Attention、Attention Dropout、Layer Norm)→Add残差→Layer Norm→橙色MLP块(内含MLP H→4H扩展、GeLU、MLP 4H→H压缩、Dropout)→Add残差→顶部Output/Heads/Loss。紫色MLP为全连接层，整个蓝色Transformer Layer重复N次。该图是论文模型并行切分策略的基础依据：论文论证的关键结论在于，Transformer每一层中包含两个超大紫色MLP全连接层（H×4H维度，占该层参数主要部分），而注意力头计算量虽大但参数较少，因此适合对MLP做张量并行、对Attention做流水线并行，从而支撑83亿参数规模GPT-2训练。

### Figure 3 (p.4) ⭐深度解读
![[assets/crops/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-fig03.png]]
*整页渲染: ![[assets/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-p04.png]]*
> [!quote] caption
> Blocks of Transformer with Model Parallelism. f and g are conjugate. f is an identity operator in the forward pass and all reduce in the backward pass while g is an all reduce in the forward pass and identity in the backward pass.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

该图展示Transformer块（MLP与Self-Attention）在模型并行下的具体结构：(a)MLP中权重A按行切分为[A₁,A₂]，X沿列切分，经GeLU得Y₁,Y₂后再合并；(b)Self-Attention将多头Q/K/V拆分为[Q₁,Q₂]/[K₁,K₂]/[V₁,V₂]。两条并行路径间通过共轭算子**f**（前向恒等、反向all-reduce）与**g**（前向all-reduce、反向恒等）衔接。

原文借此论证核心结论：仅插入f、g两个同步原语，即可在不重写编译器/代码的前提下实现Transformer的模型并行，是Megatron-LM方法的关键机制基础，为后续千亿/万亿参数规模训练的可扩展性提供理论与工程支撑。

### Figure 4 (p.5) ⭐深度解读
![[assets/crops/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-fig04.png]]
*整页渲染: ![[assets/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-p05.png]]*
> [!quote] caption
> Communication operations in a transformer layer. There are 4 total communication operations in the forward and backward pass of a single model parallel transformer layer. contains a portion of the embedding table, an all-reduce (g operator) is required after the input embedding. For the output embedding, one approach is to perform the parallel GEMM [Y1, Y2] = [XE1, XE2] to obtain the logits, add a

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读**

图示单Transformer层的模型并行结构：输入X经LayerNorm进入**第一个Model Parallel块**（Self-Attention+Linear(f)），残差叠加后再经LayerNorm进入**第二个Model Parallel块**（Linear→GeLU→Linear）。每个并行块正反向各需1次All-Reduce，故单层共计**4次通信操作**。

论文借此论证：(1) 列切分使attention与MLP中的并行GEMM仅需All-Reduce，无需all-gather/reduce-scatter，通信开销最小且与batch/序列长度解耦；(2) 通信量可精确预测（4次/层），不随张量大小爆炸。

该图是支撑Megatron-LM核心方案的关键：证明仅靠简单的张量切分+All-Reduce即可在不引入额外调度复杂度的前提下训练8.3B参数模型，为后续GPU集群规模扩展的通信成本分析提供基础。

### Figure 5 (p.6) ⭐深度解读
![[assets/crops/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-fig05.png]]
*整页渲染: ![[assets/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-p06.png]]*
> [!quote] caption
> Model and model + data parallel weak scaling efﬁciency as a function of the number of GPUs. done by scaling the batch-size, however, this approach does not address training large models that do not ﬁt on a single GPU and it leads to training convergence degradation for large batch sizes. In contrast, here we use weak scaling to train larger models that were not possible otherwise. The baseline for

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

该图由 **Table 1** 与柱状图组成。表1列出4组模型配置：参数从1.2B→8.3B，层数40→72，隐藏维度1536→3072，模型并行GPU为1/2/4/8，分别叠加数据并行至64/128/256/512 GPU。柱状图展示弱扩展效率——**纯模型并行**在1/2/4/8 GPU上分别为100%/95%/82%/77%；**模型+数据并行**在64/128/256/512 GPU上为96%/83%/79%/74%。

**技术结论**：原文借此证明 Megatron-LM 的张量并行方案随 GPU 增加效率衰减可控（8卡仍达77%），且与数据并行叠加后扩展至512卡仍保持74%，验证了模型并行可训练超过单卡显存的大模型。

**论文作用**：作为"系统可扩展性"证据，处于性能论证链路前端，为后续证明更大参数模型在下游任务上泛化更强（Figure 5/Table 5）提供工程可行性基础。

### Figure 6 (p.7) ⭐深度解读
![[assets/crops/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-fig06.png]]
*整页渲染: ![[assets/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-p07.png]]*
> [!quote] caption
> Validation set perplexity. All language models are trained for 300k iterations. Larger language models converge notice- ably faster and converge to lower validation perplexities than their smaller counterparts.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图6展示355M/2.5B/8.3B三档GPT-2模型（对应Table 2配置：层数24/54/72，隐层1024/1920/3072）在300k迭代内的验证困惑度曲线。三条曲线在训练初期快速下降后趋于平稳，最终分别收敛至约15、10.5、9，8.3B模型始终最低且下降最陡。

论文以此曲线量化论证"模型规模越大，收敛越快、终值困惑度越低"的关键结论，作为支撑模型并行（model parallelism）有效性的核心实验证据，回应"能否高效训练十亿参数模型"的中心问题，从而串联起Table 2（配置）→图6（效果）→Table 3（下游零样本评测）的完整扩展性论证链。

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
> 【图文联合解读】**表1 + 柱状图联合解读**

**① 表1结构/数据**：列4组扩展配置——参数量1.2B→2.5B→4.2B→8.3B，隐藏维度1536→1920→2304→3072，层数40→54→64→72，注意头16→20→24→32（每头维度恒定96）；模型并行GPU为1/2/4/8，对应叠加数据并行至64/128/256/512 GPU，保持约1B参数/GPU。

**② 柱状图效率**：纯模型并行1→8 GPU弱扩展效率100%→95%→82%→77%；模型+数据并行64→512 GPU为96%→83%→79%→74%。

**③ 关键论证**：8.3B参数模型在512卡上仍保持74%弱扩展效率，证明张量并行（TP）与数据并行（DP）可高效叠加。

**④ 论文作用**：作为图1缩放实验的配置基线，是支撑"TP+DP混合并行可扩展至多B参数"这一核心方法论的关键实验锚点，为后续8.3B模型训练提供可行性依据。

### Table 2 (p.7) ⭐深度解读
![[assets/crops/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-tab02.png]]
> [!quote] caption
> Model conﬁgurations used for GPT-2.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

**1) 表格内容**：Table 2 列出了三种 GPT-2 模型配置，参数规模分别为 355M、2.5B、8.3B，对应层数 24/54/72、隐藏维度 1024/1920/3072、注意力头数 16/20/24、每头维度 64/96/128；总 GPU 数分别为 64、128、512，每个 epoch 训练时间 0.86、2.27、2.10 天。

**2) 关键结论**：随着参数规模扩大 23 倍（355M→8.3B），GPU 增至 512，但单 epoch 时间反而从 2.27 天降至 2.10 天，证明模型并行策略在大规模下仍保持高效训练。

**3) 论文作用**：该表是实验规模的标定基础，用于支撑 Megatron 在 Transformer 解耦式模型并行下可有效训练十亿级语言模型的核心论断，为后续零样本评估（zero-shot）提供算力可行性依据。

### Table 3 (p.7) ⭐深度解读
![[assets/crops/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-tab03.png]]
> [!quote] caption
> Zero-shot results. SOTA are from (Khandelwal et al. 2019) for Wikitext103 and (Radford et al. 2019) for LAMBADA.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 3 图文联合解读**

**核心对象与数据：** 表3展示三个模型规模（355M / 2.5B / 8.3B）在两个零样本基准上的表现。Wikitext103 困惑度由 19.31 → 12.76 → 10.81（↓），8.3B 超过前 SOTA 15.79；LAMBADA 准确率由 45.18% → 61.73% → 66.51%（↑），8.3B 亦超 SOTA 63.24%。

**技术结论：** 参数规模扩大带来零样本性能**单调提升**，且 8.3B 模型在两项任务上**全面刷新 SOTA**，定量证明模型并行可有效训练十亿参数 Transformer 并具备真实泛化优势。

**链路作用：** 作为扩展性论证的最终落点——承接 Table 2（配置）与训练收敛曲线，以真实下游基准结果闭合"能否高效训练十亿参数模型"这一中心问题，完成配置→收敛→下游评估的完整证据链。

### Table 5 (p.8) ⭐深度解读
![[assets/crops/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-tab05.png]]
> [!quote] caption
> Development set results for MNLI, QQP, SQuAD 1.1 and SQuAD 2.0 and test set results for RACE. The trained tokens represents consumed tokens during model pretraining (proportional to batch size times number of iterations) normalized by consumed tokens during model pretraining for our 336M model.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**表5核心**：对比336M/1.3B/3.9B三个Megatron模型与RoBERTa、ALBERT、XLNet在5个下游任务（MNLI、QQP、SQuAD1.1/2.0、RACE）的成绩，参数与训练token量均以336M模型为基准归一化。

**关键结论**：在仅用1×训练token量下，**Megatron-3.9B全面领先**——MNLI 91.4/91.4、SQuAD2.0 91.2/88.5、RACE 89.5均超RoBERTa、XLNet与ALBERT；3.9B单模型即逼近ALBERT ensemble水平，3.9B ensemble在SQuAD2.0（91.7/89.0）、RACE（90.9）刷新最优。证明**模型规模扩大即带来下游泛化提升**。

**论文作用**：承接Figure 5弱扩展性——证明分布式并行训练工程可行后，本表给出大规模模型在标准基准上的实证收益，论证"模型并行→更大模型→更强性能"完整链路，为方法有效性收尾。

### Table 6 (p.11) ⭐深度解读
![[assets/crops/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-tab06.png]]
> [!quote] caption
> Hyperparameters for ﬁnetuning BERT model on down-

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图像无法辨认为 Table 6**：所提供图片实为论文参考文献页（Devlin、Radford、Raffel 等条目），并非 Table 6（BERT 微调超参数表）。以下仅依据原文 caption 解读：

1) **核心对象与结构**：Table 6 列出在 SQuAD 等下游任务上微调 BERT 的超参数（如 batch size、学习率、训练 epoch 等），是模型并行训练大模型后迁移验证的配置清单。

2) **论证的关键结论**：该表说明作者将十亿参数级预训练模型高效迁移到下游 BERT 微调任务中，提供可复现的实验设定，支撑"模型并行可扩展且实用"的结论。

3) **链路作用**：与 Figure 6（预训练收敛性）、Table 3（零样本评测）共同构成"配置→训练→迁移"完整证据链，证明大规模 Transformer 兼具预训练优势与下游任务实用性。

（注：原文引文讨论的是 Figure 6 而非 Table 6，存疑请核对。）

### Table 7 (p.15) ⭐深度解读
![[assets/crops/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-tab07.png]]
> [!quote] caption
> Effect of number of attention heads on scaling on 8.3

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 7 图文联合解读：**

表7考察8.3B参数模型在8路模型并行下，注意力头数对扩展效率（Scaling Efficiency）的影响。控制总隐层维度恒为3072不变，仅改变"头数×单头维度"组合：16头×192→**82%**、24头×128→**80%**、32头×96→**77%**。

**关键结论**：头数越多、单头维度越小，扩展效率单调下降（5个百分点差距）。论文借此论证，大模型并行训练时不宜过度细分注意力头，应在头数与单头维度间取得平衡，以保障并行扩展效率。该表作为支撑性实验证据，为Megatron-LM的整体架构设计准则（即在固定总参数下选择适度头数）提供了量化依据。

### Table 8 (p.15) ⭐深度解读
![[assets/crops/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-tab08.png]]
> [!quote] caption
> Speedup obtained for the 1.2 billion parameters model using model parallelism while keeping the batch size constant.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 8 联合解读：**

该表展示 1.2B 参数模型在 **固定 batch size** 条件下，纯模型并行的加速比：1 / 2 / 4 / 8 块 GPU 分别获得 **1.0× / 1.64× / 2.34× / 2.98×** 的加速。

**关键论证：** ①模型并行确实可扩展（弱可线性扩展）；②但效率递减明显——8 卡仅 2.98×（并行效率约 37%），远低于理想值，证明张量切分存在通信与同步开销。

**论文链路作用：** 该表承上启下。前半部分已证明模型并行的可行性，此处量化其扩展瓶颈（难以靠纯模型并行支撑更大模型），从而为后续 8.3B 模型必须采用 **"模型并行 + 数据并行" 混合策略**（对应 Figure 8 的 8 路模型并行 × 64 路数据并行方案）提供关键的实验依据。

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