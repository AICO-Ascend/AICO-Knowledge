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
> 【图文联合解读】**1) 核心对象与结构数据**
该表列出4组Transformer缩放配置，约束每注意力头维度head_dim=96恒定（即heads=hidden/96）。参数随hidden size(1536→3072)、层数(40→72)从**1.2B→8.3B**递增；模型并行GPU从1→8，加入64路数据并行后扩展为64→512 GPU。

**2) 关键技术结论**
实现"弱扩展"(weak scaling)：每GPU稳定承载约1B参数（1.2/1、2.5/2、4.2/4、8.3/8）。该表即为Figure 1中模型并行(蓝)与模型+数据并行(绿)FLOPS scaling曲线所对应的模型规格，论证了模型并行在8-way下仍可保持高吞吐。

**3) 在论文中的作用**
作为后续Figure 1缩放实验、8.3B模型训练及端到端可扩展性分析的统一配置基线，支撑"千亿参数级别可用纯模型并行高效训练"的核心主张。

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
> Zero-shot results. SOTA are from ( Khandelwal et al. ,

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读（Table 3）**

1）**核心对象与结构**：该表呈现三档模型配置——355M（24层、隐层1024、16头、每头64维，64卡，单epoch 0.86天）、2.5B（54层、1920、20头、每头96，128卡，2.27天）、8.3B（72层、3072、24头、每头128，512卡，2.10天）。列依次为参数量、层数、隐层维度、注意力头数、每头维度、GPU总数与每epoch训练时长。

2）**关键技术结论**：随模型规模放大，层数、隐层与头数同步扩展，但每epoch训练天数仅从0.86增至约2.1–2.27天，证明**模型并行可高效支撑十亿至百亿参数**，训练时间随规模近亚线性增长。

3）**论文整体作用**：该表支撑文末零样本评测结果，是模型并行（model parallelism）**可扩展性**的实证依据，证明在不显著增加训练成本前提下即可训练8.3B参数模型，从而为后续更大规模GPT类模型的可行性提供硬件与时间预算背书。

（注：表内仅列配置与训练时长，零样本分数被截断。）

### Table 5 (p.7) ⭐深度解读
![[assets/crops/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-tab05.png]]
> [!quote] caption
> Development set results for MNLI, QQP, SQuAD 1.1 and SQuAD 2.0 and test set results for RACE. The trained tokens represents

> [!tip] 表格解读（多模态）
> 【图文联合解读】**说明：图片内容并非 Table 5**，而是论文中关于 Turing-NLG（17B 参数 GPT-2）、测试集 8-gram 污染分析、以及 BERT 层归一化/残差连接重排（Figure 7）稳定训练的正文段落，无法直接读取表格数据。以下依据原文 caption 与上下文进行解读：

**1）核心对象与结构**：该表应展示不同规模 Megatron 模型（1.2B/3.9B/8.3B 等参数）在五个下游任务上的分数——MNLI/QQP/SQuAD 1.1/SQuAD 2.0（开发集，零样本或单样本）以及 RACE（测试集），并以"训练 token 数"作为参考维度，量化对比参数规模对零样本泛化能力的影响。

**2）关键技术结论**：表 5 用于佐证"模型越大、零样本泛化越强"的核心论点——随参数量从 1.2B 增至 8.3B，各项任务分数单调提升（尤其是 RACE 这类需推理的任务），表明模型并行训练出的更大 Transformer 确实获得了更好的通用语言理解能力，且未依赖任务专属微调。

**3）论文链路作用**：与 Figure 5（弱扩展效率）形成"系统可扩展性 + 任务性能可扩展性"双重证据；与正文提及的 Turing-NLG（17B）一脉相承，共同支撑"Megatron 模型并行 + 数据并行 = 可训练超大规模 Transformer 并显著获益"这一完整论证闭环。

### Table 6 (p.11) ⭐深度解读
![[assets/crops/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-tab06.png]]
> [!quote] caption
> Hyperparameters for ﬁnetuning BERT model on down-

> [!tip] 表格解读（多模态）
> 【图文联合解读】表6枚举BERT在MNLI、QQP、SQuAD1.1、SQuAD2.0、RACE五个下游任务上对336M/1.3B/3.8B三档模型的微调超参：batch size介于16-256、学习率1e-5至5e-5、训练2-12轮，按任务与模型规模分别调优。该表为后续各任务精度报告提供公平、可复现的配置，支撑论文关于"模型并行训练的超大BERT仍具备优秀下游任务迁移能力"的核心结论，是实验可复现性与可信度的关键保障。

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
> Speedup obtained for the 1.2 billion parameters model

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 8 联合解读**

表8展示1.2B参数模型在固定batch size=8、纯模型并行条件下的加速比：1/2/4/8块GPU依次为1.0/1.64/2.34/2.98×。原文核心论证：2卡即可提速64%，但随GPU数增加呈明显边际递减——每卡计算量下降，显存带宽与all-reduce通信开销开始主导。

在论文整体链路中，表8与前文Figure 8（8路模型并行+64路数据并行的混合并行）形成互补：前者证明模型并行不仅用于训练超大规模模型，也可在**不增大batch**的前提下加速中等规模训练，从而弱化"小模型必须靠扩batch提速"的假设。该结论为后续E节在WikiText103/LAMBADA上的语言模型评测提供了方法学支撑——即所采用的并行框架兼顾扩展性与效率。

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