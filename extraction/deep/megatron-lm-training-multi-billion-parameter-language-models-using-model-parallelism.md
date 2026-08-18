# Megatron-LM — 技术点深读（DEEP 2026-08-18）
> 全要素深读笔记。独立文件，extract_phase1 重跑不丢。
> 论文：Megatron-LM: Training Multi-Billion Parameter Language Models Using Model Parallelism · arXiv:1909.08053v4 (13 Mar 2020) · Shoeybi, Patwary, Puri, LeGresley, Casper, Catanzaro (NVIDIA)

## 核心问题

大 Transformer 语言模型（BERT/GPT-2 类）参数量逼近数十亿，单卡显存装不下；而既有 model parallelism 方案要么需要重写模型 + 自定义编译器（GPipe 的 pipeline 框架逻辑、Mesh-TensorFlow 的专用 DSL+编译器），要么引入 pipeline bubble / 优化器改动影响精度（§2.3）。论文要回答的核心问题分两层：

1. **系统层**：能否在原生 PyTorch 中、零自定义 C++/编译器的前提下，仅插入少量 communication primitive 就实现高效的 intra-layer（层内/tensor）模型并行，并把 Transformer 扩到 8.3B 参数、512 GPU、15.1 PetaFLOPs？
2. **模型层**：BERT 直接放大到 BERT-Large(336M) 以上时出现 *unexpected model degradation*（先验观察，Lan et al. 2019 ALBERT 报告）。能否不靠 parameter sharing，而是通过架构重排让 BERT 在 336M→1.3B→3.9B 上单调提升下游精度，并在 WikiText103 / LAMBADA / RACE 上刷 SOTA？

约束条件明确：weak scaling 的语义被刻意重定义为「按参数量放大模型本身」而非「放大 batch」，因为大 batch 会损害收敛（§5.1）。

## 关键创新点

1. **Column-parallel → Row-parallel GEMM 融合，消除中间同步点（§3, Figure 3a）**
   机制：MLP 第一个 GEMM `Y = GeLU(XA)`。若按行切 A（`A=[A1;A2]`，对应切 X 的列），则 `Y = GeLU(X1·A1 + X2·A2)`，因 GeLU 非线性，必须在 GeLU 前 all-reduce 同步——多一个同步点。论文改用 **按列切** `A = [A1, A2]`，得到 `[Y1,Y2] = [GeLU(XA1), GeLU(XA2)]`（公式 3），GeLU 可独立施加于每个分片，**消除同步点**。第二个 GEMM 沿行切，直接吃 GeLU 输出无需通信。整层 MLP 只需前向 1 次 all-reduce（g 算子）、反向 1 次 all-reduce（f 算子）。f/g 互为共轭：f 前向 identity / 反向 all-reduce；g 前向 all-reduce / 反向 identity（Code 1）。

2. **Multi-head attention 按 head 切分（§3, Figure 3b）**
   机制：Q/K/V 的 GEMM 按 column-parallel 切分，使得**每个 attention head 的矩阵乘完全本地化在一个 GPU 上**，self-attention 内部无需通信。输出线性层按 row-parallel，直接吃并行 attention 输出。与 MLP 同构，同样 f/g 共轭。
   净效果：单 transformer 层前向 2 次 all-reduce + 反向 2 次 all-reduce，共 4 次通信（Figure 4）。

3. **Vocabulary-parallel embedding + 跨熵通信压缩（§3）**
   机制：输入/输出 embedding 共享权重 `E∈R^{H×v}`，沿 vocab 维 column-parallel `E=[E1,E2]`。输入 embedding 后接 all-reduce（g）。输出 embedding 的朴素做法是 all-gather logits，通信量 `b×s×v`（v≈50257，巨大）。论文**将 parallel GEMM 输出与 cross-entropy loss 融合**，只通信标量 loss，通信维度从 `b×s×v` 压到 `b×s`，大幅降低通信。为使 per-GPU vocab 是 128 的倍数（高效 GEMM），将 vocab 从 50,257 pad 到 51,200（`128×8×50`，§5.1）。

4. **Duplicate-redundant 计算 vs 通信的取舍（§3）**
   原则：layer norm / dropout / residual 的参数与计算在所有 model-parallel GPU 上**复制冗余**，而非拆分广播——刻意用算力换通信，保持 GPU compute-bound。每个 model-parallel worker 独立优化自己那份参数；因为值要么 local 要么 duplicated，**优化器无需通信参数更新**。

5. **f/g 算子的 PyTorch autograd 原生实现（Code 1）**
   `f` 即 `torch.autograd.Function`：forward identity、backward all-reduce。整层并行只需几行 Python+NCCL，无编译器。这是「simple/efficient」口号的落点。

6. **Hybrid model+data parallel 的分组拓扑（§B.1, Figure 8）**
   规则：同一 server 内 GPU 组成 model-parallel group（如 1–8 号）；跨 server、各组中**同位置** GPU（1,9,...,505）组成 data-parallel group。反向时多个 data-parallel 的 gradient all-reduce **并行**执行。总 GPU 数 = `MP × DP`；8.3B 用 8-way MP × 64-way DP = 512 GPU。全程 NCCL。

7. **Dropout RNG 的双轨种子策略（§B.2）**
   residual 前、非 model-parallel 区的 dropout：所有 MP worker **同种子**，保证 dropout pattern 一致（因为这些算子是 duplicated 的）。model-parallel 区内的 dropout（self-attention 内）：每 worker **独立种子**，保证跨 worker 的随机性。两套 RNG 分别维护。

8. **BERT 架构重排：pre-LN + 残差位置调整（§5.3, Figure 7）**
   这是模型层最关键发现。原始 BERT（post-LN 式残差排布，Figure 7a）在 336M 训练正常，放大到 752M 出现不稳定/loss 更高。重排为 Figure 7b（把 layer norm 和 residual connection 移到 transformer 层的输入侧，即 pre-LN 范式）后，**消除不稳定、训练 loss 更低**，使 1.3B、3.9B 单调提升。论文自称「to the best of our knowledge, first to report such a change enables training larger BERT models」。注意：GPT-2 本就已是 pre-LN 式（§2.2 指出 GPT-2/BERT 把 LN 放在 attention/FFN **输入**侧，区别于原始 transformer 的输出侧）——本文的 BERT 重排实质是把 BERT 的残差/LN 结构向 GPT-2 风格对齐。

9. **训练配方（§4.2）**
   mixed precision + dynamic loss scaling（V100 Tensor Cores）；权重 `N(0,0.02)`，残差层前按 `1/√(2N)` 缩放（N=transformer 层数）；Adam + decoupled weight decay λ=0.01；gradient norm clip 1.0；dropout 0.1；每层后 activation checkpointing。GPT-2：seq 1024、batch 512、300k iter、lr 1.5e-4（3k warmup + cosine decay 到 1e-5）。BERT：vocab 30,522、batch 1024、lr 1.0e-4（10k warmup + linear decay over 2M iter），用 sentence order prediction 替代 NSP + whole-word n-gram masking。

## 表格（原文结构化）

**Table 1 — Scaling study 配置（GPT-2，per-attention-head hidden=96 恒定）**

| Hidden | Attn heads | Layers | 参数量(B) | MP GPUs | MP+DP GPUs |
|---|---|---|---|---|---|
| 1536 | 16 | 40 | 1.2 | 1 | 64 |
| 1920 | 20 | 54 | 2.5 | 2 | 128 |
| 2304 | 24 | 64 | 4.2 | 4 | 256 |
| 3072 | 32 | 72 | 8.3 | 8 | 512 |

Baseline：1.2B 单卡 = 39 TeraFLOPs = 单 V100(DGX-2H) 峰值的 30%（强基线）。

**Table 2 — GPT-2 训练配置**

| 参数量 | Layers | Hidden | Attn heads | Head/GPUs | Time/epoch (days) |
|---|---|---|---|---|---|
| 355M | 24 | 1024 | 16 | 64 | 0.86 |
| 2.5B | 54 | 1920 | 20 | 96/128 | 2.27 |
| 8.3B | 72 | 3072 | 24 | 128/512 | 2.10 |

（1 epoch = 68,507 iterations；355M 等价 BERT-Large 规模。）

**Table 3 — Zero-shot 结果（GPT-2）**

| Model | WikiText103 PPL ↓ | LAMBADA Acc ↑ |
|---|---|---|
| 355M | 19.31 | 45.18% |
| 2.5B | 12.76 | 61.73% |
| 8.3B | **10.81** | **66.51%** |
| Previous SOTA | 15.79 | 63.24% |

**Table 4 — BERT 配置（per-head hidden=64 恒定）**

| 参数量 | Layers | Hidden | Attn heads | Total GPUs |
|---|---|---|---|---|
| 336M | 24 | 1024 | 16 | 128 |
| 1.3B | 24 | 2048 | 32 | 256 |
| 3.9B | 48 | 2560 | 40 | 512 |

**Table 5 — BERT 下游（dev set；RACE 为 test set）。trained tokens ratio 相对 336M 归一化。**

| Model | tokens× | MNLI m/mm | QQP | SQuAD1.1 F1/EM | SQuAD2.0 F1/EM | RACE m/h (test) |
|---|---|---|---|---|---|---|
| RoBERTa | 2 | 90.2/90.2 | 92.2 | 94.6/88.9 | 89.4/86.5 | 83.2 (86.5/81.8) |
| ALBERT | 3 | 90.8 | 92.2 | 94.8/89.3 | 90.2/87.4 | 86.5 (89.0/85.5) |
| XLNet | 2 | 90.8/90.8 | 92.3 | 95.1/89.7 | 90.6/87.9 | 85.4 (88.6/84.0) |
| Megatron-336M | 1 | 89.7/90.0 | 92.3 | 94.2/88.0 | 88.1/84.8 | 83.0 (86.9/81.5) |
| Megatron-1.3B | 1 | 90.9/91.0 | 92.6 | 94.9/89.1 | 90.2/87.1 | 87.3 (90.4/86.1) |
| Megatron-3.9B | 1 | 91.4/91.4 | 92.7 | 95.5/90.0 | 91.2/88.5 | **89.5 (91.8/88.6)** |
| ALBERT ensemble | — | — | — | 95.5/90.1 | 91.4/88.9 | 89.4 (91.2/88.6) |
| Megatron-3.9B ensemble | — | — | — | 95.8/90.5 | 91.7/89.0 | **90.9 (93.1/90.0)** |

注意：Megatron-3.9B 用 *1×* tokens ratio 即追平/超过 RoBERTa(2×)/ALBERT(3×)，说明收益主要来自架构+规模而非过量数据。

**Table 7 — Attention heads 对 8.3B/8-way MP scaling 的影响（§D.1）**

| Attn heads | Hidden/head | Scaling Eff. |
|---|---|---|
| 16 | 192 | 82% |
| 24 | 128 | 80% |
| 32 | 96 | 77% |

heads↑ → self-attention 内 GEMM 变小、softmax 元素增多 → scaling 略降。

**Table 8 — Strong scaling（1.2B 固定，batch=8）**

| GPUs | 1 | 2 | 4 | 8 |
|---|---|---|---|---|
| Speedup | 1.0 | 1.64 | 2.34 | 2.98 |

>2 GPU 后收益递减——per-GPU 计算下降，memory bandwidth + 通信开销开始主导。

**Figure 5 弱扩展效率总表（提取自图）**

| GPUs | MP only | MP+DP |
|---|---|---|
| 1 | 100% | 96% |
| 2 | 95% | 83% |
| 4 | 82% | 79% |
| 8 | 77% | 74% |

8.3B/8-way MP = 77% linear scaling；8.3B/512 GPU(MP+DP) = 74%。峰值 15.1 PetaFLOPs sustained。

## 与同类对比

- **vs GPipe（pipeline parallelism, Huang et al. 2018）**：GPipe 把层组分到不同 device、有 pipeline bubble、需要额外 pipelining 逻辑、改优化器影响精度。Megatron 的 intra-layer TP **正交且互补**于 pipeline（§1/§2.3 原话），可与 GPipe 叠加。GPipe 需重写模型；Megatron 仅插几个 all-reduce。
- **vs Mesh-TensorFlow（Shazeer et al. 2018）**：同样是 distributed tensor computation 思路（按维度切 tensor op），但 MTF 是一套 **DSL + 编译器**，需用户指定并行维度、编译生成 collective graph。Megatron「utilize similar insights」但**不做框架/编译器**，直接在 PyTorch 里改 transformer 实现——简单、无新依赖。思路同源，工程形态相反。
- **vs FlexFlow（Jia et al. 2018）**：FlexFlow 搜索最优并行策略（含 DP+MP+混合），是通用框架。Megatron 专注 transformer 结构、手工利用 attention-head / GEMM 的天然可分性，不做策略搜索。
- **vs Data parallelism + activation checkpointing（Chen et al. 2016）**：DP+ckpt 仍受限于「模型须放进单卡」。Megatron 的 TP 直接把模型切开，突破单卡显存墙；二者可叠加（论文确实叠了 64-way DP + activation checkpointing）。
- **vs ALBERT（Lan et al. 2019）**：ALBERT 用 parameter sharing 缓解 BERT 放大的退化问题，但限制了模型容量。Megatron 走另一条路——**架构重排（pre-LN 式）**——不共享参数即可让 BERT 单调放大到 3.9B，且 1× tokens 即超 ALBERT(3×)。
- **vs Parameter-server pipeline（Harlap PipeDream, Chen 2018）**：PS 方案有一致性问题。Megatron 全同步、无 PS。

## 跨论文关系（→ MOC 谱系）

Megatron-LM 是 **training-systems / model-parallelism 谱系的根节点**：

- → [[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]：本文的分布式训练 follow-up，把 MP+DP+inter-node 推到更大集群，是 Megatron 的「scale-out 续作」。
- → [[megascale-scaling-large-language-model-training-to-more-than-10000-gpus]]：万卡级 LLM 训练，直接继承 Megatron 的 TP/PP/DP 混合并行思想并进一步优化（通信-计算 overlap、bubble 压缩等），是规模上限的延伸。
- → [[zero-memory-optimizations-toward-training-trillion-parameter-models]]（ZeRO）：与 Megatron TP **正交**。ZeRO 切 optimizer state/gradient/参数到 DP 维度降显存；可与 Megatron TP 叠加（后续 Megatron-DeepSpeed 即如此）。本文只切参数到 MP 维度，未触及 optimizer state 分片。
- → [[scalable-training-of-mixture-of-experts-models-with-megatron-core]]（Megatron-Core MoE）：本文 TP 之上的 MoE 扩展，expert 维度并行建立在本文的 MP/DP 拓扑之上。
- → [[muon-is-scalable-for-llm-training]]（Distributed Muon）：现代 Muon 优化器的分布式实现，**built on Megatron 的 TP/PP/EP/DP 栈**——本文定义的 f/g 共轭算子与 hybrid 分组是其基础设施。
- 谱系定位：本文 = **tensor parallelism 原始论文**（column-parallel linear → row-parallel linear, one all-reduce）+ pipeline 并行性的正交声明。后续所有 Megatron 系（Megatron-LM v2/v3、Megatron-Core、Megatron-DeepSpeed）均以此为基础增量。

显式提及但未独立成篇的相关：GPipe、Mesh-TensorFlow、FlexFlow、PipeDream、ALBERT、RoBERTa、XLNet、Turing-NLG（Microsoft 17B GPT-2，用 Megatron 训练，§5.2 末尾提及，证明可外推到更大）。

## 局限与边界

- **单 DGX-2H 内显存墙**：§6 明确——>16B 参数会超出 16 GPU 的 DGX-2H 单机显存，需要 hybrid intra+inter-layer MP + inter-node MP。本文只验证到 8.3B，跨节点 MP 未实现，是明确的未完成项。
- **Pipeline 并行未被本文实现**：只声明「orthogonal and complementary」，并未真正在代码里叠 pipeline。pipeline bubble、调度问题留待后续。
- **弱扩展效率随 GPU 数下降明显**：MP+DP 从 1→512 GPU 效率从 96% 降到 74%（Figure 5）。DP 维度的 gradient all-reduce 是主要损失源（§5.1.1「requires further communication of gradients … drop slightly」）。
- **Strong scaling 收益递减**：1.2B 固定模型，>2 GPU 后 memory bandwidth + 通信主导（Table 8，8 GPU 仅 2.98×）。说明 TP 对小模型不是免费午餐，主要价值在「放得下」而非「跑得快」。
- **Attention heads 数是隐式超参约束**：heads↑ 会降 scaling efficiency（Table 7, 16→32 heads 效率 82%→77%）。设计大模型时须在 speed 与 accuracy 间手工平衡，论文未给出自动选择方法。
- **Vocabulary padding**：为 GEMM 效率把 vocab 从 50,257 pad 到 51,200，引入死参数，虽小但是工程妥协。
- **BERT 架构发现是经验性的**：pre-LN 重排的根因（为何 post-LN 在大模型上不稳）论文未做理论分析，仅经验归因。后续工作（如 ON-LayerNorm 分析）补上了解释。
- **数据泄漏检查依赖 n-gram overlap**：WikiText103 test 8-gram overlap 10.8%（其中 9.09% 本就来自 WikiText103 自身训练集，§5.2），LAMBADA 1.4%。虽「consistent with previous work」，但 overlap 非零，SOTA 的纯净性有保留。
- **仅验证 GPT-2(decoder) 与 BERT(encoder)**：未覆盖 T5/XLNet 等其它模型族（§6 future work 明列）。MoE、长上下文等均未触及。
- **混合精度 + 大模型稳定性**：用 dynamic loss scaling，但 BERT 752M post-LN 仍不稳定，说明混合精度本身不足以兜底大模型训练稳定性，架构层面的 pre-LN 是必要条件。
