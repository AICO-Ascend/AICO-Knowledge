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
> 【图文联合解读】**图1解读：**

**1）核心对象与结构：** 图展示两阶段（GPU1/GPU2）流水线并行时间线对比。上图(a)为Orca基线，4个请求A/B/C/D的长方形prefill块（Ap/Bp/Cp/Dp）后接多个极小条纹decode块，节点间存在明显"Bubble"空白；下图(b)为SARATHI方案，prefill被切分为多个等小块（如Ap1/Ap2/Bp1/Bp2/Bp3），并与decode按"Cp1Ad1""Dp1A_d2"形式组合填满每步调度，无bubble。

**2）论证结论：** decode单token开销远高于prefill，且不均衡时序产生大量流水线气泡；将prefill分块并与decode"搭便车"组合，可饱和GPU算力、消除气泡。

**3）论文作用：** 作为方法总览图，开篇直观对比基线缺陷与SARATHI的chunked-prefills+decode-maximal batching核心机制，引出后续调度与性能评估。

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
> 【图文联合解读】**图文联合解读（Figure 4）**

**(1) 核心对象与数据：** 图(a)横轴为batch size（1–512），纵轴为throughput (tokens/ms)。Prefill侧在batch≈4–16即饱和于170–185 tokens/ms，几乎不受序列长度影响；Decode侧从batch=1时的1–2 tokens/ms随batch单调上升，batch=256、seq=64时约100 tokens/ms。图(b)纵轴为算术强度：Prefill的preproj/attn/postproj/ffn四项随batch升至500–2750；Decode在batch≤8时普遍<10，至batch=256才跃至约240。

**(2) 关键结论：** 定量证实Prefill为compute-bound（高算术强度、吞吐早饱和），Decode为memory-bound（低强度、需大batch才能拉升吞吐），二者在硬件利用上严重不均衡。

**(3) 链路作用：** 作为连接微观算子特性（Fig 3）与系统级调度评估的桥梁，为Sarathi将decode"挂载"在chunked prefill上做同batch混合调度提供硬件层面的动机与基准支撑。

### Figure 5 (p.5) ⭐深度解读
![[assets/crops/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-fig05.png]]
*整页渲染: ![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p05.png]]*
> [!quote] caption
> Pipeline bubbles in LLM inference A 2-way PP iteration-level schedule [48] across 4 requests (A,B,C,D) shows the existence of pipeline bubbles due to non-uniform batch execution times. set of layers; compared to TP which shards each layer across the participating GPUs. As discussed in §2.3, compared to TP, PP has a much better compute-communication ratio and does not require expensive interconnect

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

1）**核心对象与结构**：图为2路Pipeline Parallelism（PP）在GPU1与GPU2上的迭代级时间线，处理4个请求（A/B/C/D）。每请求包含较长的Prefill块（Ap/Bp/Cp/Dp）与极短的Decode块（A_d1B_d1、C_d1D_d1、A_d2B_d2）；GPU2相对GPU1有错位的流水线延迟。图中标出PB_1、PB_2、PB_3三段灰色"Pipeline Bubble"，均出现在Decode阶段切换或GPU2等待GPU1输出时。

2）**论证结论**：Prefill（计算密集、耗时） 与 Decode（访存密集、极短） 长度严重不均，导致流水线各micro-batch执行时间不一致，空泡占据GPU有效时间，形成气泡型资源浪费。

3）**在论文中的作用**：作为Sarathi提出"chunked-prefill + decode piggyback"方案的动机图——通过将Prefill切片并与Decode共批执行，消除非均匀批执行引发气泡，从而提升LLM推理的GPU利用率。

### Figure 6 (p.6) ⭐深度解读
![[assets/crops/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-fig06.png]]
*整页渲染: ![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p06.png]]*
> [!quote] caption
> Example of how attention mask is set across dif- ferent chunk prefill iterations in SARATHI (q and k represent “query" and “key" tokens, respectively). The attention mask for v (“values") is set similarly.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图6图文联合解读：**

**核心对象**：三张注意力掩码矩阵，展示三次chunk prefill迭代的Q×K掩码模式。第一次：4 query (q0-q3) × 4 key (k0-k3)，呈下三角因果掩码（橙色）；第二次：4 query (q4-q7) × 8 key (k0-k7)，左侧4列对历史chunk全连接（绿色），右侧4列维持因果（橙色）；第三次：4 query (q8-q11) × 12 key (k0-k11)，前8列绿色全连、后4列橙色因果。

**技术结论**：SARATHI的piggybacking机制中，后续chunk的query可一次性关注此前所有chunk的全部key（绿色区域"1"密布），而当前chunk内部仍保持标准因果掩码（橙色下三角）。这种"跨chunk全连+块内因果"的组合掩码，在保证自回归语义正确性的前提下，使decode请求能与分块prefill共享一次前向传播。

**论文作用**：作为方法正确性的关键可视化证据，支撑"SARATHI可在不损失精度的前提下混合prefill与decode以提升吞吐"的论断，为后续实验（vLLM基线对比、延迟/吞吐收益）提供理论正当性。

### Figure 7 (p.7) ⭐深度解读
![[assets/crops/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-fig07.png]]
*整页渲染: ![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p07.png]]*
> [!quote] caption
> The effect of tile quantization on the runtime of one iteration of LLaMA-13B on A6000 GPU. maximal batching with that of the baseline scheme that com- putes prefill and decode iterations separately. With baseline batching, a decode-only iteration spends 12.49 milliseconds per token. In contrast, per-token decode time is only 1.2 mil- liseconds with decode-maximal batching. This shows that pig- gyb

> [!tip] 技术解读（多模态）
> 【图文联合解读】<think

### Figure 8 (p.9) ⭐深度解读
![[assets/crops/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-fig08.png]]
*整页渲染: ![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p09.png]]*
> [!quote] caption
> Decode-only speedup with SARATHI on an A6000 GPU with LLaMA-13B (chunk size = 256).

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图8联合解读：**

图8展示A6000+Llama-13B下SARATHI的decode-only提速曲线：横轴batch size 2–18，纵轴提速倍数，三色柱分别对应序列长度1K（橙实）、2K（灰斜纹）、3K（绿网格）。量化数据：1K序列在batch=2时达峰值~9.7×，随batch增大单调降至batch=18的~2.7×；2K/3K仅在batch≤8呈现数据，batch=2处分别约5.7×/4.3×。

**技术结论：** 通过chunked-prefill与decode的混合调度，SARATHI仅在decode阶段即获显著加速；提速随batch与序列长度增加而收敛，但仍稳定保持≥2.7×，验证重负载下方法鲁棒性。

**链路作用：** 作为decode维度的性能证据，与端到端吞吐实验互补，从"单卡峰值decode提速"延伸至"跨硬件跨模型方法外推"，完成论证闭环。

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
> 【图文联合解读】**图10解读：**

**1）核心对象与数据**：2×3 网格堆叠柱状图，对比 LLaMa-13B 在 A6000 上各操作（preproj/attn/postproj/ffn，单位秒）的耗时，橙=SARATHI 基线，青=SARATHI。上排 chunk=256、下排 chunk=512；列分别为 seq len 1K/2K/3K。量化读数：seq=1K、batch=18、chunk=256 时基线≈8.6s、SARATHI≈6.7s；同 batch=18 但 chunk=512 时基线≈6.5s、SARATHI≈5.2s；seq=3K、batch=6、chunk=256 时基线≈8.3s、SARATHI≈6.8s。ffn（实色段）为最大占比。

**2）论证结论**：增大 chunk（256→512）显著压缩总时延，且 SARATHI 在每个配置下均低于基线，收益主要来自 ffn 与 attn 段。

**3）作用**：作为 Figure 9 的操作级分解补充，从微观算子层面验证 chunked-prefill + decode piggyback 减开销的机制有效性。

### Figure 11 (p.11) ⭐深度解读
![[assets/crops/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-fig11.png]]
*整页渲染: ![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p11.png]]*
> [!quote] caption
> Comparison with iteration-level scheduler Orca for LLaMa 13B on A6000 GPU. configuration of sequence length and chunk size, we show the effect of varying batch sizes. Further, for each run, we also show the runtime across different operations i.e., preproj, attention, postproj, and ffn.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读**

图(a)：A6000+LLaMA13B，序列1K/2K/3K对应最大批18/10/6，chunk=256下SARATHI归一化吞吐稳定在1.22–1.27×；Orca最佳≈1.10×（仅1K下略高），最差与基线持平1.0×。

图(b)：序列1K、批18，P:D比0–100扫描中，SARATHI三种chunk（128/256/512）峰值依次≈1.13/1.26/1.23×，全程压制Orca最佳（≈1.10×，P:D>30后回落至≈1.05×）。

论证结论：chunked-prefill在不同序列长度与P:D负载下均稳定优于iteration级调度器Orca，chunk=256为最优甜点。

论文作用：作为核心ablation之一，量化"piggyback"策略相对Orca的稳定吞吐增益，支撑Sarathi在混合prefill/decode负载下的调度有效性。

### Figure 12 (p.12) ⭐深度解读
![[assets/crops/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-fig12.png]]
*整页渲染: ![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p12.png]]*
> [!quote] caption
> Impact of SARATHI on pipeline bubbles (top) and request completion times (bottom) for GPT-3 deployed on DGX A100(s) in simulation. the effect of variable sequence lengths on request latencies.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读**

**核心对象与数据**：图(a)为气泡时间CDF对比——SARATHI气泡集中在0–18s即达CDF=1.0，而TP+PP气泡散布于15–90s。图(b)为请求完成时间随请求数变化（0–10000条）：10000请求时SARATHI约1900s，显著低于TP+PP(约3700s)和TP×8副本(约2850s)。

**技术结论**：通过将chunked-prefill与decode混合调度（即"piggybacking"），SARATHI大幅消除pipeline气泡，同时端到端延迟较TP+PP降低近一半。

**论文作用**：作为论文模拟实验部分的关键证据，量化论证SARATHI方案在流水线利用率与吞吐上的核心优势，支撑其"混合调度消除气泡"的核心设计主张。

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
> Shapes of the input, weight, and output tensors in a transformer decoder block. B, L and H denote batch size, embedding (aka hidden) size and sequence length (L=1 during decode, except for attention).

> [!tip] 表格解读（多模态）
> 【图文联合解读】该表量化展示解码块5个算子（preproj、attn、postproj、ffn_ln1、ffn_ln2）的输入/权重/输出张量形状，统一以 [B,L,H]（B批大小、L序列长度、H隐藏维）表示；H₂为FFN中间维度，线性投影权重为 [H,H]，attn无权重项。

据此论证核心技术结论：除attn外其余均为线性投影，其访存受权重量H²支配、计算量随B·L扩展，decode阶段L=1使算术强度（∝L）极低，GPU利用率严重不足。

在论文中的作用：为Sarathi将decode"骑附"于chunked prefill以增大L、同步恢复线性层与注意力层吞吐的核心调度思路，提供张量形状维度的量化理论铺垫。

### Table 2 (p.7) ⭐深度解读
![[assets/crops/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-tab02.png]]
> [!quote] caption
> Per-token prefill and decode time (in ms) For LLaMA-13B on A6000 GPU, the rows show operation times for 1) prefill-only requests of prompt size 1024 of batch size 4, 2) decode-only batch size of 4 with sequence length 1024, and c) a mixed batch of a single 1021 prefills and 3 decodes. Decode-maximal

> [!tip] 表格解读（多模态）
> 【图文联合解读】图像仅含Table 2的caption与上下文段落（含B=⌊(M_G−M_S)/(L·m_kv)⌋公式），表格本体数值未呈现，故依caption与上下文解读。

1) **对象与结构**：LLaMA-13B在A6000上的per-token耗时(ms)三行对比——①prefill-only(prompt=1024, b=4)；②decode-only(b=4, seq=1024)；③混合批(1×预填1021+3×decode)。

2) **关键技术结论**：caption明示"decode-maximal batching可将decode每token耗时降低一个数量级"——混合批中decode搭便车prefill算力，单decode成本被摊薄近10×。

3) **在论文中的作用**：为Sarathi"chunked-prefill piggyback decode"调度提供motivation量化证据，揭示decode memory-bound、prefill compute-bound的本质差异，支撑长prompt切分、与decode同槽调度的核心策略。

### Table 3 (p.8) ⭐深度解读
![[assets/crops/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-tab03.png]]
> [!quote] caption
> Models, GPUs, and mode of evaluation.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 3 联合解读**

**1) 核心对象与数据**：表内列出三类模型的三种评测配置——LLaMA-13B（单 A6000，48 GB，**Deployment**）、LLaMA-33B（单 A100，80 GB，**Deployment**）、GPT-3（64×A100，80 GB/卡，**Simulation**）。

**2) 论证的关键结论**：由于 GPT-3 规模过大无法实部署，作者以仿真方式评估，而 LLaMA 系列做端到端真实部署；这与 Figure 3 揭示的 "prefill 算力饱和、decode 严重欠饱和（batch=1 时 per-token 时间可达 prefill 的 200×）" 相印证，说明 Sarathi 通过把 decode 与 chunked prefill 混合调度提升吞吐的策略在不同规模下均适用。

**3) 链路作用**：作为实验章节的总配置表，划定从单卡消费级（A6000）到单卡数据中心级（A100）再到大规模多卡（A100×64）的评测边界，为后续吞吐量/延迟对比提供一致参照。

### Table 4 (p.9) ⭐深度解读
![[assets/crops/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-tab04.png]]
> [!quote] caption
> Peak throughput gains with S ARATHI for different se- quence lengths with two different model-GPU combinations (chunk size = 256).

> [!tip] 表格解读（多模态）
> 【图文联合解读】该表量化展示 SARATHI 在两种模型-GPU 配置（LLaMA-13B/A6000 与 LLaMA-33B/A100）、序列长度 1K–3K、chunk=256 下的峰值吞吐增益：13B 在 1K 序列时达最高 1.33×（解码加速 5.45×，batch=6，P:D=50:1）；33B 在 1K 时为 1.25×（batch=10）。随序列长度增大，P:D 比升至 127:1，吞吐增益递减至 1.14×，说明越偏解码主导场景混合调度收益越有限。

原文借此论证：分块预填充 piggyback 解码可有效提升端到端吞吐，收益随负载结构变化可预测。

在论文链路中，该表位于 Figure 4（算术强度分析）之后、详细调度实验之前，充当系统级性能落点，验证前文机制分析的实际效果，支撑"混合调度普适有效"的核心结论。

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