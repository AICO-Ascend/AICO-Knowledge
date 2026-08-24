---
paper_num: "17"
title: "SARATHI: Efficient LLM Inference by Piggybacking Decodes with Chunked Prefills"
authors: "Amey Agrawal*2, Ashish Panwar1, Jayashree Mohan1, Nipun Kwatra1, Bhargav S. Gulavani1, and Ramachandran Ramjee1 1Microsoft Research India 2Georgia Institute of Technology"
date: "2023/8/31"
arxiv: "https://arxiv.org/abs/2308.16369"
pdf: "papers/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills.pdf"
slug: "sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills"
tags: [disaggregated-serving]
---

# SARATHI: Efficient LLM Inference by Piggybacking Decodes with Chunked Prefills

> [!abstract] 摘要（原文）
> 1\. 💡 SARATHI通过引入\`chunked-prefills\`和\`decode-maximal batching\`技术，解决了\`LLM\`推理中\`decode\`阶段\`GPU\`利用率低以及\`pipeline parallelism\`中由于\`prefill\`和\`decode\`时间差异导致的\`pipeline bubbles\`问题。 2. 🚀 \`decode-maximal batching\`使\`decode\`请求能够“\`piggyback\`”于\`prefill\`块，将内存密集型\`decode\`操作转变为计算密集型，并创建了计算负载均匀的\`hybrid batches\`，显著减少了\`pipeline bubbles\`。 3. 📈 SARATHI在\`LLaMA-13B\`模型上将\`decode throughput\`提高了高达10倍，\`end-to-end throughput\`提高了1.33倍；在\`GPT-3\`的\`pipeline parallelism\`中，它将\`bubbles\`减少了6.29倍，实现了1.91倍的\`end-to-end throughput\`提升。

## 元信息
- **发表日期**: 2023/8/31
- **作者**: Amey Agrawal*2, Ashish Panwar1, Jayashree Mohan1, Nipun Kwatra1, Bhargav S. Gulavani1, and Ramachandran Ramjee1 1Microsoft Research India 2Georgia Institute of Technology
- **arXiv**: https://arxiv.org/abs/2308.16369
- **本地 PDF**: `papers/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills.pdf`
- **页数**: 16

## 图表（原文 caption + 页码）

### Figure 1 (p.1) ⭐深度解读
![[assets/crops/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-fig01.png]]
*整页渲染: ![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p01.png]]*
> [!quote] caption
> Example two-stage pipeline parallel schedule. (a)

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

1）**核心结构**：图(a)展示Orca的两级PP调度——4个请求A/B/C/D以完整prefill块(A_p, B_p, C_p, D_p)串行执行，decode小条(A_d1, B_d1…)稀疏插入，GPU1出现两段明显Bubble；图(b)展示SARATHI——prefill被切分为A_p1/A_p2、B_p1-B_p3、C_p1/C_p2、D_p1/D_p2等小块，与decode token密集交错，GPU1与GPU2均无空泡。

2）**关键结论**：原文借此论证三点——(i)完整prefill长度不一导致pipeline bubble；(ii)decode单token开销比prefill高一个数量级却独占调度；(iii)SARATHI通过"chunked prefill + decode-maximal batching"将decode"搭车"piggyback到prefill chunk上，消除bubble并摊薄decode成本。

3）**论文作用**：作为开篇Figure 1，承担problem statement与solution teaser双重职能，为后文chunk size分析、stall-free调度及decode-maximal batching策略提供视觉锚点。

### Figure 2 (p.3) ⭐深度解读
![[assets/crops/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-fig02.png]]
*整页渲染: ![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p03.png]]*
> [!quote] caption
> High-level architecture of a decoder block. sequence length of each request (i.e., the number of input tokens in the given query), and H is the model’s embedding size (e.g., 5120 for LLaMA-13B).

> [!tip] 技术解读（多模态）
> 【图文联合解读】**(a) Decoder Block**：两层子模块堆叠，每层均为「LayerNorm → 子模块 → Add残差」结构；下层为Attention，上层为FFN。

**(b) Attention**：输入经 `W_{Q,K,V}`（`H→3H`）线性投影拆分为 Q/K/V，送入 Self-Attention，结果 Concat 后再经 `W_O`（`3H→H`）与 Dropout 还原到 H 维。

**(c) FFN**：经 `W（H→H2）→GeLU→W（H2→H）` 双层线性变换加 Dropout，维度先扩后缩。

**作用**：该图量化了decoder每token的算子构成，为文中对比 prefill 与 decode 每token耗时（Table 2）提供结构依据——即 prefill 是 compute-bound（`H→3H` 大矩阵乘），decode 是 memory-bound。这正是 Sarathi 提出 "chunked prefill piggyback decodes" 的前提：通过切分长 prompt 为与 decode token 尺寸匹配的 chunk，把 compute-heavy 的 prefill 塞进 decode batch 的空闲槽，从而提升 GPU 利用率。

### Figure 3 (p.4) ⭐深度解读
![[assets/crops/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-fig03.png]]
*整页渲染: ![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p04.png]]*
> [!quote] caption
> Per-token prefill and decode time with different batch sizes (sequence length = 1024) for LLaMa-13B on A6000 GPU. Prefill saturates GPU compute even at batch size of 1 and results in almost constant per-token time across batch sizes. Decode under-utilizes GPU compute and costs as much as 200× prefill for batch size 1. The incremental cost of linear operators for decode is almost zero as batch size

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图示左为 Prefill（batch 1–18，per-token 时间稳定在 ≈0.23–0.25 ms）、右为 Decode（batch=1 时 ≈46 ms，batch=18 时 ≈3 ms）的堆叠柱图，按 preproj / attn / postproj / ffn_ln1 / ffn_ln2 / others 分解。Prefill 在 batch=1 即饱和 GPU，耗时近乎恒定；Decode 受内存带宽限制，其中 attention 几乎不随 batch 摊薄，而线性算子可摊薄——batch=1 时 decode ≈200× prefill。

该图揭示 **prefill 与 decode 的算力–带宽不对称**，是论文核心动机：证明将 decode 请求"挂靠"到饱和算力的 chunked prefill 上、填补 decode 未利用 GPU 算力的必要性，即 Sarathi 合并调度方案的设计前提。

### Figure 4 (p.4) ⭐深度解读
![[assets/crops/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-fig04.png]]
*整页渲染: ![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p04.png]]*
> [!quote] caption
> Impact of the arithmetic intensity (bottom) on the throughput (top) of prefills and decodes for LLaMA-13B on A6000 GPU. operations. Figure 4b shows the arithmetic intensity of each operation separately for prefill (left) and decode phases (right).

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

**(a)** LLaMA-13B/A6000 上 Prefill（1K 序列）在 batch=1 时即达 ~180 tokens/ms，吞吐随 batch 几乎饱和，曲线平坦；而 Decode 在 batch<32 时吞吐极低（<20 tokens/ms），仅在大 batch（≥256）且短序列（64）下才升至 ~100 tokens/ms。

**(b)** Prefill 算术强度随 batch 增长（≈800→2750），呈计算密集型；Decode 算术强度长期 <10，batch=256 时才跃升至 ~125–240，呈典型访存密集型。

**论证结论：** Prefill 与 Decode 的算术强度存在数量级差异（计算 vs 访存瓶颈不同），这是两者无法在同 batch 中高效并发的根因。论文由此提出将 Prefill 分块"挂载"（piggyback）在 Decode batch 上，将短 Prompt 切碎以拉高 Decode 的 batch size 从而提升其算术强度，实现二者吞吐同时增益——这是 Sarathi 调度策略的核心动机。

### Figure 5 (p.5) ⭐深度解读
![[assets/crops/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-fig05.png]]
*整页渲染: ![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p05.png]]*
> [!quote] caption
> Pipeline bubbles in LLM inference A 2-way PP iteration-level schedule [48] across 4 requests (A,B,C,D) shows the existence of pipeline bubbles due to non-uniform batch execution times. set of layers; compared to TP which shards each layer across the participating GPUs. As discussed in §2.3, compared to TP, PP has a much better compute-communication ratio and does not require expensive interconnect

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

**① 图示内容：** 2路PP跨GPU1/GPU2处理4个请求(A,B,C,D)的时间线。GPU1先依次完成Aₚ/Bₚ/Cₚ/Dₚ四个prefill块，随后出现PB₁、PB₂、PB₃三段虚线"气泡"，再处理Aᵈ1Bᵈ1、Cᵈ1Dᵈ1、Aᵈ2Bᵈ2等decode批次；GPU2延迟一个iteration启动，同样跑完prefill后衔接decode，未见明显空闲。

**② 论证结论：** 由于同一batch内prefill与decode耗时差异显著（非均匀执行时间），标准iteration级PP调度会在GPU上产生pipeline气泡，造成算力浪费。

**③ 论文作用：** 作为动机图，引出Sarathi的核心方案——将prefill切分为chunk与decode混合批处理，用decode"piggyback"填充气泡，提升吞吐。

### Figure 6 (p.6) ⭐深度解读
![[assets/crops/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-fig06.png]]
*整页渲染: ![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p06.png]]*
> [!quote] caption
> Example of how attention mask is set across dif- ferent chunk prefill iterations in SARATHI (q and k represent “query" and “key" tokens, respectively). The attention mask for v (“values") is set similarly.

> [!tip] 技术解读（多模态）
> 【图文联合解读】## Figure 6 深度解读

**1) 核心对象与结构**
该图为第三个 chunk prefill 迭代的注意力掩码矩阵。横轴为 12 个 key token（k0–k11），按 chunk_size=4 分为三组；纵轴为 4 个 query（q8–q11）。绿色区（k0–k7）全为 1，表示对历史 chunk 的注意力可复用预计算的 K/V；橙色区（k8–k11）呈下三角掩码——q8 仅关注 k0–k8，q9 关注 k0–k9，q10 至 k0–k10，q11 全关注，体现新 chunk 内部的标准因果掩码。

**2) 原文论证的关键技术结论**
证明 chunked prefill 中，**旧 chunk 的 query（q8）只需与本 chunk 及之前 key 计算注意力**，无需重算；**新 chunk 的 query（q9–q11）仅需对当前及之前 token 做因果掩码**。即不同位置 query 所需注意力范围不同，为"非对称计算"和 piggybacking decode 提供了形式化依据。

**3) 在论文方法链路中的作用**
该图是 SARATHI 混合批处理（prefill + decode 同 batch）可行性的**核心可视化证据**：它解释为何可将 decode 的 query 拼接到 prefill chunk 后，无需重算全部注意力，从而支撑论文关于吞吐提升与流水线效率的核心论点。

### Figure 7 (p.7) ⭐深度解读
![[assets/crops/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-fig07.png]]
*整页渲染: ![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p07.png]]*
> [!quote] caption
> The effect of tile quantization on the runtime of one iteration of LLaMA-13B on A6000 GPU. maximal batching with that of the baseline scheme that com- putes prefill and decode iterations separately. With baseline batching, a decode-only iteration spends 12.49 milliseconds per token. In contrast, per-token decode time is only 1.2 mil- liseconds with decode-maximal batching. This shows that pig- gyb

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读（Figure 7）**

**1）核心对象与结构**：图将 LLaMA-13B 在 A6000 上单次 transformer 迭代拆为 preproj、postproj、ffn、total compute 四条曲线，横轴为序列长度 0–1024，纵轴为耗时（ms）。preproj 缓慢从约 10ms 升至约 60ms；postproj 最小，全程 ≤20ms；ffn 主导耗时，从约 30ms 阶梯式跃升至约 150ms；total compute 从约 45ms 增至约 270ms。**关键特征**是 ffn 与 total compute 呈明显"楼梯状"跳变，突变点集中在 128、256、512、640、768、896 等处——这正是 GPU 矩阵乘 tile 尺寸边界，即 tile quantization 效应的可视化证据。

**2）原文论证结论**：prefill 计算量并非随长度连续线性增长，而是按 tile 大小离散跳变；非 tile 对齐的请求会浪费碎片化算力。这是 Sarathi 采用"chunked-prefill、将 chunk 设为 tile 边界倍数"策略的硬件层动因。

**3）在论文链路中的作用**：与前文 decode-maximal batching 对比呼应，作为 Sarathi-Serve 调度设计的实验支撑——证明以 tile 对齐 chunk 切分预填充，可显著降低单步延迟、消除碎片开销。

### Figure 8 (p.9) ⭐深度解读
![[assets/crops/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-fig08.png]]
*整页渲染: ![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p09.png]]*
> [!quote] caption
> Decode-only speedup with SARATHI on an A6000 GPU with LLaMA-13B (chunk size = 256).

> [!tip] 技术解读（多模态）
> 【图文联合解读】**Figure 8 图文联合解读**

**1) 核心对象与数据**：横轴为 Batch Size（2–18），纵轴为 Decode-only 阶段加速比（0–10×），三组序列长度：1K（橙色）、2K（灰斜纹）、3K（绿网格）。1K 序列覆盖全部 batch；2K 止于 batch=8（最高≈5.8×，batch=2）；3K 仅至 batch=6（最高≈4.4×，batch=2）。随 batch 增大加速比单调下降：1K 由 ~9.8× 降至 ~2.7×；序列越长，可承载的 batch 越小，加速比也越低。

**2) 关键结论**：即便排除 piggyback prefill 的收益，仅 decode 阶段 SARATHI 仍带来显著加速（最高近 10×），证明 chunked prefill 通过提高 GPU 利用率与改善 kernel 调度，正面惠及纯 decode 路径，而非仅来自混合 prefill 的分摊。

**3) 在论文中的作用**：作为单独剥离 decode 的 ablation，排除"加速源于把 prefill 摊到 decode 上"的混淆，从机制层面夯实 SARATHI 在混合负载下整体吞吐提升的根基。

### Figure 9 (p.10) ⭐深度解读
![[assets/crops/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-fig09.png]]
*整页渲染: ![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p10.png]]*
> [!quote] caption
> Normalized throughput (tokens/ms) for LLaMa 13B on A6000 GPU with different sequence lengths, P:D ratios, and chunk sizes. 2 4 6 8 10 12 14 16 18

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

该图展示 LLaMa 13B 在 A6000 上、三种序列长度（1K/2K/3K，对应批大小 18/10/6）下，三档 chunk size（128/256/512）的归一化吞吐随 Prefill/Decode（P:D）比的变化曲线。

**核心数据：** 各曲线均在低 P:D 处达到峰值后单调下降；1K 时 chunk=256 峰值最高（≈1.27，P:D≈15），3K 时 chunk=512 峰值最高（≈1.20，P:D≈60），chunk=128 在所有场景下均最差（峰值≈1.13）。

**论证结论：** 存在最优 P:D 比，且最优 chunk size 随序列长度增大而增大（短序列宜小 chunk，长序列宜大 chunk），Sarathi 相对纯 decode 基线最高可获 ~27% 吞吐增益。

**论文作用：** 为 Sarathi 在实际部署中根据序列长度自适应选择 chunk size 与调度 P:D 比提供量化依据，支撑"分块 prefill 搭车 decode"通用性论点。

### Figure 10 (p.10) ⭐深度解读
![[assets/crops/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-fig10.png]]
*整页渲染: ![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p10.png]]*
> [!quote] caption
> Breakdown of total time spent on different operations for LLaMa 13B on A6000 GPU with varying sequence lengths and batch sizes, using prefill chunk sizes of 256 (top half) and 512 (bottom half). Orange and blue bars represent baseline and SARATHI, respectively. for sequence length of 1K as shown in Figure 9a. Using the chunk size of 512 for sequence length=1K at batch size of 18 also provides sign

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图10以2×3堆叠柱阵展示LLaMa-13B在A6000上的算子级耗时分解，蓝色（SARATHI）柱普遍低于橙色（baseline），且差距随batch增大而扩大。例如seq_len=1K、chunk=256时，bs=18下baseline≈8.6s而SARATHI≈6.8s，节约约20%；seq_len=3K、bs=6下由≈8.4s降至≈6.8s。各分量中ffn占比最大、attn次之，preproj/postproj较小，且SARATHI主要压缩ffn与attn段，pre/postproj几近持平。chunk=512整体比256更优（如bs=18、1K时由6.8s再降至≈5.2s）。

**论证结论：** chunked-prefill与decode piggybacking通过提升kernel利用率，使ffn（GEMM-heavy）受益最显著，且随batch放大收益递增；减小chunk size会部分抵消优势。

**论文链路作用：** 与端到端加速比互补，作为微观算子级归因证据，支撑"SARATHI消除prefill/decode失衡、提升GPU利用率"的核心主张。

### Figure 11 (p.11) ⭐深度解读
![[assets/crops/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-fig11.png]]
*整页渲染: ![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p11.png]]*
> [!quote] caption
> Comparison with iteration-level scheduler Orca for LLaMa 13B on A6000 GPU. configuration of sequence length and chunk size, we show the effect of varying batch sizes. Further, for each run, we also show the runtime across different operations i.e., preproj, attention, postproj, and ffn.

> [!tip] 技术解读（多模态）
> 【图文联合解读】图(b)展示在序列长度1K、batch size=18下，SARATHI三种chunk尺寸（128/256/512）与Orca best-case随Prefill/Decode比（0–100%）变化的归一化吞吐曲线。SARATHI在低P:D区间（5–30%）出现峰值：chunk=256在P:D≈15%达1.26×，chunk=512在≈30%达1.23×，chunk=128在≈5%达1.14×；Orca best-case最高仅约1.10×。该图与子图(a)共同论证：SARATHI的chunked prefill合并策略在多种负载下均稳定优于Orca迭代级调度，是验证"Splitwise+chunked"设计优于纯迭代调度的关键消融证据。

### Figure 12 (p.12) ⭐深度解读
![[assets/crops/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-fig12.png]]
*整页渲染: ![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p12.png]]*
> [!quote] caption
> Impact of SARATHI on pipeline bubbles (top) and request completion times (bottom) for GPT-3 deployed on DGX A100(s) in simulation. the effect of variable sequence lengths on request latencies.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读（Figure 12b）**

**核心对象与数据**：图(b)展示GPT-3在DGX A100上仿真部署下，三种调度策略处理0–10000请求时的端到端完成时间。在10000请求时，SARATHI（蓝色虚线）约1900s，TP+PP（橙色实线）约3700s，TP(8 replicas)（绿色点划线）约2900s，三者近似线性增长但斜率差异显著。

**关键技术结论**：通过将decode与chunked prefill混合调度消除pipeline bubble，SARATHI相较TP+PP将请求完成时间降低近50%，相较TP(8 replicas)亦快约35%，验证了混合流水策略的端到端优越性。

**论文整体作用**：与图(a)的pipeline bubble分析呼应，从微观（气泡占比）到宏观（用户可见延迟）共同构成SARATHI有效性的完整证据链。

### Figure 13 (p.13) ⭐深度解读
![[assets/crops/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-fig13.png]]
*整页渲染: ![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p13.png]]*
> [!quote] caption
> Ablation study: Effect of varying the chunk size on different components of the system for LLaMa 13B on A6000 GPU. measure the time to compute the prefill phase for various se- quence lengths using the full sequence at once - this represents our baseline prefill performance. For each long sequence, we then compute the prefill with chunked-prefills and compare its end-to-end runtime with the baseli

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

**1) 核心对象与数据**：Figure 13 包含三组柱状图，实验对象为 LLaMa-13B on A6000，序列长度取 1K/2K/3K，每组 8 根柱对应 chunk size 64–512。(a) 纯 self-attention 加速比：随 chunk 增大由 ~0.27（64@1K）升至 ~0.88–0.90（256–512@3K）；(b) chunked-prefill vs. full prefill 端到端加速比：1K 时 64 仅 ~0.2、512 达 ~0.95，长序列在 256 后基本饱和；(c) 整 batch 端到端加速比（chunked-prefill + decode-maximal）：各 chunk 下均 >1，1K 时峰值 ~1.28（256/512），3K 仍 ~1.22。

**2) 关键结论**：单独 chunked-prefill（b）在小 chunk 下甚至慢于全序列 prefill；但一旦与 decode 批处理联合调度（c），系统整体获得 20%+ 加速，验证了"decode piggyback"才是收益主因，而非单纯切分。

**3) 在论文中的作用**：作为消融实验，剥离自注意力开销与整批吞吐量两个层面，量化证明 Sarathi "chunked-prefills × decode co-batching" 的设计必要性——为方法核心的 piggyback 调度策略提供实证支撑。

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.3) ⭐深度解读
![[assets/crops/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-tab01.png]]
> [!quote] caption
> shows the shapes of input, output, and weight ten- sors of the various operations. Each transformer block first computes self-attention on a given input X . Typically, multi- head attention is used, but we consider only one head for simplicity of exposition. A linear transformation preproj over X (u

> [!tip] 表格解读（多模态）
> 【图文联合解读】**说明：所提供图片为 Table 1 周围的说明性正文段落，并非表格本体。**

**联合解读（基于原文推断）：**

该表列示 transformer 各操作在 **prefill**（X∈[B·L,H]、W∈[H,3H]、Q/K/V∈[B·L,H]、attn 输出∈[B·L,H]）与 **decode**（X∈[B,H]、Q/K/V∈[B,H]、attn 输出∈[B,H]）两阶段输入/输出/权重张量形状及对应 FLOPs。

**关键结论**：attention 算力为 O(L²)，prefill 平摊至 L 个 token，而 decode 每步仅服务 1 token，致使 **decode 每 token 成本高出一个数量级**，这是其低效根源。

**论文作用**：该表量化"decode 低效"这一核心痛点，为 SARATHI 提出 **chunked-prefill + piggyback decode**（统一 batch 形状、摊薄 attention 开销）提供数据支撑与理论动机。

### Table 2 (p.7) ⭐深度解读
![[assets/crops/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-tab02.png]]
> [!quote] caption
> Per-token prefill and decode time (in ms) For LLaMA-13B on A6000 GPU, the rows show operation times for 1) prefill-only requests of prompt size 1024 of batch size 4, 2) decode-only batch size of 4 with sequence length 1024, and c) a mixed batch of a single 1021 prefills and 3 decodes. Decode-maximal

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读（基于可见caption与正文）**：

Table 2量化展示LLaMA-13B在A6000上三种场景的per-token耗时：①batch=4的纯prefill（prompt=1024）；②batch=4的纯decode（seq=1024）；③混合batch（1个1021-token prefill + 3个decode）。数据本身在当前图片裁剪中未呈现，但caption明确给出核心结论：**Decode-maximal batching使decode per-token时间降低约一个数量级**。

**论证作用**：与下方batch size公式 B=⌊(M_G−M_S)/(L·m_kv)⌋ 呼应，揭示传统调度中decode受限于KV-cache显存、batch极小，因而GPU算力严重浪费——这正是Sarathi提出"将decode piggyback到chunked-prefill上联合批处理"的实证动机，为全文方法奠定量化基础。

### Table 3 (p.8) ⭐深度解读
![[assets/crops/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-tab03.png]]
> [!quote] caption
> Models, GPUs, and mode of evaluation.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 3 解读：**

**① 核心内容：** 列三组评估配置——LLaMA-13B/A6000(1卡,48GB)、LLaMA-33B/A100(1卡,80GB)采用真实部署；GPT-3/A100(64卡,80GB)采用模拟。

**② 论证结论（结合 Figure 3）：** Figure 3 表明 prefill 计算密集（batch=1 即饱和 A6000），decode 访存密集（小 batch 单 token 时延可达 prefill 的 200×）。Table 3 以不同算力/显存/规模（13B–175B、单卡–64卡、部署–模拟）覆盖这些极端差异，证明 Sarathi 的 "chunked-prefill 携带 decode" 共批策略在跨规模场景下均适用。

**③ 链路作用：** 作为方法验证的硬件与模型基准，串联微观算子特性（Fig 3）与宏观吞吐评估（Fig 4 等），保证结论从单卡部署到大规模集群均可推广。

### Table 4 (p.9) ⭐深度解读
![[assets/crops/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-tab04.png]]
> [!quote] caption
> Peak throughput gains with S ARATHI for different se- quence lengths with two different model-GPU combinations (chunk size = 256).

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 4 图文联合解读**

该表在 chunk size=256 条件下，对比 LLaMA-13B(A6000) 与 LLaMA-33B(A100) 两组模型-GPU 组合在 1K/2K/3K 序列长度下的峰值吞吐：批大小分别为 6/6/6 与 10/5/3，P:D 比从 28:1 到 127:1，解码加速达 2.51×–5.45×，整体吞吐增益 1.14×–1.33×。

原文借此论证：Sarathi 通过"分块预填充搭便车解码"，在不同模型规模、硬件平台与序列长度下均稳定获得 >1.14× 的吞吐提升，且序列越短、批越大增益越显著。

该表是实验链路的核心验证节点，证明 Sarathi 调度策略在多样负载下的通用性与有效性，支撑论文"统一调度 prefills 与 decodes"的核心主张。

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
B = \lfloor \left(\frac{M_G - M_S}{L*m_{kv}}\right) \rfloor
$$

## 相关论文

- [[taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve]] — Taming Throughput-Latency Tradeoff in LLM Inference with Sarathi-Serve
- [[sglang-efficient-execution-of-structured-language-model-programs]] — SGLang: Efficient Execution of Structured Language Model Programs
- [[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]] — Mooncake: A KVCache-centric Disaggregated Architecture for LLM Serving
- [[efficiently-serving-large-multimodal-models-using-epd-disaggregation]] — Efficiently Serving Large Multimodal Models Using EPD Disaggregation

## 技术点深读（DEEP）

![[deep/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills.txt`（76688 字符）供引用检索。