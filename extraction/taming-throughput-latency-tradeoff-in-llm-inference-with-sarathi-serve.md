---
paper_num: "18"
title: "Taming Throughput-Latency Tradeoff in LLM Inference with Sarathi-Serve"
authors: "Amey Agrawal*2, Nitin Kedia1, Ashish Panwar1, Jayashree Mohan1, Nipun Kwatra1, Bhargav S. Gulavani1, Alexey Tumanov2, and Ramachandran Ramjee1 1Microsoft Research India 2Georgia Institute of Technology"
date: "2024/3/4"
arxiv: "https://arxiv.org/abs/2403.02310"
pdf: "papers/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve.pdf"
slug: "taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve"
tags: [disaggregated-serving]
---

# Taming Throughput-Latency Tradeoff in LLM Inference with Sarathi-Serve

> [!abstract] 摘要（原文）
> 1\. 💡 针对大型语言模型（LLM）推理中吞吐量与延迟的权衡问题，现有调度器因预填充和解码阶段的特性差异，常导致生成停顿和流水线气泡。 2. 🧠 Sarathi-Serve通过引入“分块预填充”将大型预填充请求拆分为计算量相等的块，并采用“无停顿调度”将新请求的预填充块与现有解码操作合并，以确保批处理计算均匀。 3. 🚀 实验结果显示，Sarathi-Serve在维持低尾延迟的同时显著提高了LLM服务容量，例如在不同模型和硬件上实现高达5.6倍的端到端服务容量增益。

## 元信息
- **发表日期**: 2024/3/4
- **作者**: Amey Agrawal*2, Nitin Kedia1, Ashish Panwar1, Jayashree Mohan1, Nipun Kwatra1, Bhargav S. Gulavani1, Alexey Tumanov2, and Ramachandran Ramjee1 1Microsoft Research India 2Georgia Institute of Technology
- **arXiv**: https://arxiv.org/abs/2403.02310
- **本地 PDF**: `papers/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve.pdf`
- **页数**: 18

## 图表（原文 caption + 页码）

### Figure 1 (p.1) ⭐深度解读
![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-fig01.png]]
*整页渲染: ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p01.png]]*
> [!quote] caption
> Yi-34B running on two A100 GPUs serving 128 requests from arxiv-summarisation trace. 1a highlights one of the many generation stalls lasting over several seconds in vLLM [53]. 1b shows the impact of increasing load on tail latency. Sarathi-Serve improves throughput while eliminating generation stalls. 1

> [!tip] 技术解读（多模态）
> 【图文联合解读】图1双子图：(a) Yi-34B双A100服务arxiv 128请求下"Tokens生成-时间"曲线，Sarathi-Serve(蓝)持续平滑上升，vLLM(橙)在200–220s区间出现数秒水平的"generation stall"平台；(b) P99 token间隔随QPS(0.55/0.7/1.0)柱图，vLLM由约0.5s升至1.35s，Sarathi-Serve稳定在≈0.3s。原文论证：负载升高时vLLM尾延迟急剧恶化且decode阶段存在阻塞，Sarathi-Serve通过chunked预填充与stall-free调度，兼顾高吞吐与低尾延迟。该图作为开篇动机图，直观揭示vLLM缺陷，为Table1所示模型/硬件配置下的系统设计与后续性能对比实验铺垫核心理由。

### Figure 2 (p.2) ⭐深度解读
![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-fig02.png]]
*整页渲染: ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p02.png]]*
> [!quote] caption
> Current LLM serving systems involve a tradeoff be- tween throughput and latency depending on their scheduling policy. Prioritizing prefills optimizes throughput but sacrifices TBT (time-between-tokens) tail latency whereas prioritizing decodes has the opposite effect. Sarathi-Serve serves high throughput with low TBT latency via stall-free batching. (The figure is illustrative and actual values wi

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图示二维空间（纵轴 Throughput，横轴 TBT Latency）中四系统的相对定位：FasterTransformer（红点，左下，Decode prioritizing）、Orca（紫点，中部，Prefill prioritizing + iteration-level batching）、vLLM（蓝点，右上，Prefill prioritizing + Paged Attention）沿虚线箭头由左下向右上推进，呈现传统"高吞吐 ↔ 低 TBT 不可兼得"的折中曲线。Sarathi-Serve（绿星，左上区）凭借 **stall-free batching** 跳出该曲线，同时占据高吞吐与低 TBT 时延象限。

原文借此论证：**通过调度策略改进可在不牺牲 TBT 尾延迟的前提下显著提升吞吐**，即折中是可打破的而非本质约束。

该图位于 p.2 开篇位置，作为全文**动机图（motivational figure）**，为后续 chunked-prefill 调度、stall-free batching 设计以及 Table 2 实验评估（optimum range、alpaca、sharegpt 等数据集下的端到端基准对比）提供问题陈述与目标锚点。

### Figure 3 (p.5) ⭐深度解读
![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-fig03.png]]
*整页渲染: ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p05.png]]*
> [!quote] caption
> Throughput of the prefill and decode phases with different batch sizes for Mistral-7B running on a single A100 GPU. We use prompt length of 1024 for both prefill and decode experiments. Note that different y-axis, showing pre- fills are much more efficient than decode. Further, note that batching boosts decode throughput almost linearly but has a marginal effect on prefill throughput.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**核心对象与数据**：左两图为Prefill/Decode吞吐量对比——Prefill在batch 1–8范围内吞吐稳定在~4.5K–5.5K tokens/s（batch=2时峰值），随batch增大几乎无提升；Decode从batch=1的~20 tokens/s近乎线性增长至batch=64的~820 tokens/s；二者y轴量级差约10倍，直观显示Prefill效率远高于Decode。右两图补充延迟分解：Prefill延迟随序列长度128→2K由~30ms增至~145ms，attention占比明显；Decode延迟几乎与batch无关，稳定在~15–20ms，线性层占主导。

**关键结论**：Prefill属compute-bound，batching边际增益小；Decode属memory-bound，batching带来近线性吞吐提升。该差异正是Sarathi-Serve需要协同调度两类阶段的根本动机。

**在论文中的作用**：该图是动机实验，定量揭示Prefill/Decode的负载特性差异，为后续提出chunked prefill与splitwise batching以调和throughput–latency tradeoff提供实证依据。

### Figure 4 (p.5) ⭐深度解读
![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-fig04.png]]
*整页渲染: ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p05.png]]*
> [!quote] caption
> Prefill and decode time with different input sizes for Mistral-7B running on single A100 GPU. Linear layers contribute to the majority of runtime in both prefill and decode phases. Due to the low arithmetic intensity in decode batches, the cost of linear operation for 1 decode token is nearly same as 128 prefill tokens. into linear, attention and others, and shows their individual contributions. F

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

1）图中左子图为 Prefill 阶段随序列长度（128/256/512/1k/2k）的耗时，总时间近似线性增长（~32→145ms），其中 linear 层始终占主导（2k 时约 120ms）；右子图为 Decode 阶段随 batch size（1/8/16/32/64）的耗时，全程几乎平坦在 ~18–22ms，linear 仍为最大分量（约 12–15ms），attention 与 others 占比极小。

2）关键结论：两阶段均以 linear 计算为瓶颈；由于 decode 算术强度低，**单 token decode 的 linear 耗时（~13ms）已接近 128 token prefill 的 linear 耗时（~17ms）**，验证 decode 属 memory-bandwidth bound、prefill 属 compute-bound。

3）方法论作用：该图为 Sarathi-Serve 提供动机——prefill 重、decode 轻且对 batch 不敏感，故可将两者放入同一 hybrid batch 并对 prefill 分块（chunked-prefills），在隐藏 prefill 延迟的同时维持低 TBT，从而打破吞吐–延迟权衡。

### Figure 5 (p.6) ⭐深度解读
![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-fig05.png]]
*整页渲染: ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p06.png]]*
> [!quote] caption
> Arithmetic intensity trend for LLaMA2-70B lin- ear operations with different number of token running on four A100s. Decode batches have low arithmetic intensity i.e., they are bottlenecked by memory fetch time, leading to low compute utilization. Prefill batches are compute bound with sub-optimal bandwidth utilization. Sarathi-Serve forms balanced batches by combining decodes and prefill chunks to

> [!tip] 技术解读（多模态）
> 【图文联合解读】【对象】LLaMA2-70B 线性运算在 4×A100 上的算术强度（FLOPs/bytes）随 token 数变化曲线：Decode（~30 token, ~50）位于红色 Memory Bound（Low MFU）区，Prefill（~1000 token, ~800）位于绿色 Compute Bound（Low MBU）区，Sarathi-Serve 平衡点（~600 token, ~500）恰落在两虚线交点——鞍点。

【结论】Decode 算术强度低，访存受限→MFU 低；Prefill 计算密集→MBU 低；二者单独执行均欠佳。Sarathi-Serve 将 prefill chunk 与 decode 混合，把工作点钉在鞍点附近，从而同时提升 MBU 与 MFU。

【作用】为论文核心调度策略（chunked prefill + 混合批）提供硬件层量化动机，是吞吐–时延权衡取舍设计的理论锚点。

### Figure 6 (p.6) ⭐深度解读
![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-fig06.png]]
*整页渲染: ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p06.png]]*
> [!quote] caption
> Linear layer execution time as function of number of tokens in a batch for LLaMA2-70B on A100(s) with different tensor parallel degrees. When the number of tokens is small, execution time is dictated by the cost of fetching weights from HBM memory. Hence, execution time is largely stagnant in the 128-512 tokens range, especially for higher tensor parallel degrees. Once the number of tokens in the 

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读**

图6展示LLaMA2-70B在A100上线性层执行时间随batch token数（128–4096，对数轴）的变化，对比TP-2（蓝）与TP-4（橙）两条曲线，呈阶梯状增长。具体数据：128 token时TP-2约60 ms、TP-4约30 ms；2048 token时升至约450 ms / 300 ms；4096 token时TP-2约1000 ms、TP-4约520 ms。在128–512区间两曲线均近水平平坦，TP-4始终低于TP-2。

原文借此论证：小batch时执行时间受HBM权重读取带宽主导而非算力，故线性层在小token区间呈"停滞"；越过拐点后计算主导，时间随token近似线性增长，TP-4因权重切片更小更优。

该图为Sarathi-Serve的核心论据之一：揭示线性层存在内存带宽受限的"空闲区间"，从而支撑其"chunked prefill + decode共batch"策略——利用停滞区填入prefill片段以提高吞吐，而不会显著增加延迟，从而同时优化throughput–latency权衡。

### Figure 7 (p.6) ⭐深度解读
![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-fig07.png]]
*整页渲染: ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p06.png]]*
> [!quote] caption
> A generation stall occurs when one or more prefills are scheduled in between consecutive decode iterations of a request. A, B, C and D represent different requests. Sub- script d represents a decode iteration, p represents a full prefill and p0, p1 represent two chunked prefills of a given prompt. vLLM induces generation stalls by scheduling as many pre- fills as possible before resuming ongoing d

> [!tip] 技术解读（多模态）
> 【图文联合解读】该图以时间线对比四种调度策略：vLLM与Orca将C、D完整prefill（p）打包执行，A、B的decode迭代被迫停滞；FasterTransformer仅调度decode（A退出→B退出），C、D的prefill被迫等待；Sarathi-Serve把prefill拆为p0、p1两个chunk与A_d、B_d交错执行，全程无stall。该图揭示了前三类系统在prefill–decode串行化上的结构性缺陷——或损失decode时效、或损失prefill吞吐——论证分块prefill+decode交叉调度是实现stall-free的核心机制，为§6后续SLO与吞吐实验提供关键动机基础。

### Figure 8 (p.7) ⭐深度解读
![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-fig08.png]]
*整页渲染: ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p07.png]]*
> [!quote] caption
> A 2-way pipeline parallel iteration-level schedule in Orca across 4 requests (A,B,C,D) shows the existence of pipeline bubbles due to non-uniform batch execution times.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图8对比了Orca与Sarathi-Serve在2路流水线并行、4请求（A,B,C,D）下的迭代级调度时序。Orca（上图）GPU0与GPU1上先后执行ApBp→CpDp→Ad1Bd1→Cd1Dd1，由于prefill长度差异（Ap/Bp与Cp/Dp不同）及prefill与decode（d1）混合计算时长不均，分别产生"长度变化气泡"和"prefill-decode干扰气泡"，GPU1还出现空闲等待。

Sarathi-Serve（下图）通过将prefill切分为等大小token块（如Ap1、Bp1、Ap2…）与decode请求组合，形成**等计算量批次**（Ap1Bp1Cp1D…），两卡时序几乎对齐，仅存极小气泡。

原文借此论证核心结论：iteration-level调度的pipeline bubble根因是batch计算量不均匀，Sarathi-Serve以uniform-compute batching（即chunked-prefill + decode同批）为关键设计消除气泡。

该图是论文方法动机—核心机制链路的关键证据，支撑"stall-free batching + 良好throughput/latency tradeoff"的主论点。

### Figure 9 (p.8) ⭐深度解读
![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-fig09.png]]
*整页渲染: ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p08.png]]*
> [!quote] caption
> The incremental cost of coalescing prefills with decode batches. We consider two batching schemes – (i) Decode +

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图9以2×3柱状图，对比三种批处理策略在Mistral-7B（单A100，预算256）与LLaMA2-70B（4×A100，预算512）上的batch time，扫描上下文{1024, 2048, 4096}与batch size{1, 32, 64}。数据表明：Decode+Full Prefill开销随上下文急剧放大（如70B在ctx=4096、batch=1时达28.3×），而Decode+Chunked Prefill开销稳定可控（多数情形≤3.7×，且随batch增大而衰减）。

该图论证关键结论：Orca式完整prefill混合会严重阻塞decodes、破坏SLO；而分块prefill将代价封顶于token预算内。论文以此实验支撑Sarathi-Serve的核心设计——chunked prefill是实现throughput–latency可控权衡的必要性前提，而非可选优化。

### Figure 10 (p.11) ⭐深度解读
![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-fig10.png]]
*整页渲染: ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p11.png]]*
> [!quote] caption
> Capacity (in queries per second) of Mistral-7B and

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图10以双子图形式展示两种数据集下（(a) openchat_sharegpt4；(b) arxiv_summarization），Orca、vLLM、Sarathi-Serve 三种调度器在 Mistral-7B 与 Yi-34B 上的最大吞吐（QPS），分 SLO-S（严格）和 SLO-R（宽松）两档。关键定量结果：Mistral-7B 在 openchat 上 Sarathi 达 ~2.05/2.25 QPS（标注 2.78×/2.15×）；Yi-34B 在 SLO-S 下获 **4.00×**（最强增益）；arxiv 跨模型亦保持 1.69×–1.97× 的稳定领先。

**论证结论**：Sarathi-Serve 在满足 SLO 的前提下，吞吐量在所有 (模型×数据集×SLO) 组合上均高于 Orca 与 vLLM，且大模型/长输入场景优势更显著，证明 chunked-prefill 与 decode 协同调度对吞吐–延迟权衡的"驯服"是普适的。

**论文作用**：与 Fig.7–9 共同构成 §6 评估核心，从端到端时延、首 token 延迟到最大承接容量逐级收敛，最终锁定"显著扩容 + 不破 SLO"的方法优势。

### Figure 11 (p.11) ⭐深度解读
![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-fig11.png]]
*整页渲染: ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p11.png]]*
> [!quote] caption
> Capacity of LLaMA2-70B and Falcon-180B (mod- els with pipeline parallelism) with different schedulers under strict (SLO-S) and relaxed (SLO-R) latency SLOs.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图11 图文联合解读**

图11对比三种调度器（Orca、vLLM、Sarathi-Serve）在两类pipeline并行大模型（LLaMA2-70B、Falcon-180B）与两类SLO下的最大服务容量：(a) openchat_sharegpt4上，Sarathi-Serve相对Orca提速4.69x–6.31x（LLaMA2-70B SLO-R达0.83 vs Orca 0.13）；(b) arxiv_summarization上提速2.75x–4.60x。在所有模型×SLO×数据集组合中，Sarathi-Serve均显著领先vLLM与Orca。

该图论证：pipeline并行场景下，Sarathi-Serve的chunked-prefill与分阶段调度同样能显著突破吞吐-时延折中，释放更多请求容量。

在论文链路中，图11将实验结论从单卡评估延伸至多卡分布式大模型部署，证明方法在更大规模场景中依旧有效，巩固整体方法优势。

### Figure 12 (p.12) ⭐深度解读
![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-fig12.png]]
*整页渲染: ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p12.png]]*
> [!quote] caption
> Latency – Throughput tradeoff in vLLM and

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图含两子图：上图为 Mistral-7B（P99 TBT SLO 范围 0.1–0.5s），下图为 Yi-34B（0.2–1.0s），纵轴均为最大吞吐量（Max Capacity）。对比 vLLM 三档 batch（32/64/128）与 Sarathi-Serve 两档 token budget（SS-512、SS-2048）。

**关键数据**：Mistral-7B 上 SS 稳定在 2.0–2.3 之间，vLLM 仅 0.78–1.57；Yi-34B 上 SS 维持 1.14–1.28，vLLM 不及 0.8。SS-2048 在严格 SLO 下起点较低（Mistral 0.5、Yi-34B 0.2），随 SLO 放宽迅速反超 vLLM 并趋平。

**论证结论**：在任意延迟约束下，Sarathi-Serve 均显著优于 vLLM，模型越大优势越明显，验证了分块预填充 + token budget 对吞吐–延迟权衡的优化效果，是论文核心实验支撑。

### Figure 13 (p.12) ⭐深度解读
![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-fig13.png]]
*整页渲染: ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p12.png]]*
> [!quote] caption
> TP scales poorly across nodes. (a) Median TBT for decode-only batches: cross node TP increases median TBT by more than 2× compared to a 4-way TP within node and PP across nodes. (b) Capacity under strict (SLO-S) and re- laxed (SLO-R) latency SLOs: Sarathi-Serve increases Falcon- 180B’s serving capacity by 4.3× and 3.6× over vLLM’s TP- only and hybrid-parallel configurations under strict SLOs.

> [!tip] 技术解读（多模态）
> 【图文联合解读】图13基于Falcon-180B对比跨节点TP8与节点内TP4+跨节点PP2的并行策略。**(a)** P50 TBT随batch从8增至128，TP8由0.19s升至0.37s，TP4:PP2仅由0.085s升至0.15s，batch=128时差距>2×，直接量化跨节点TP的扩展性劣势。**(b)** SLO-S下Sarathi-Serve TP4:PP2容量≈0.62，较vLLM TP8(0.14)、vLLM TP4:PP2(0.18)分别提升4.3×与3.6×；SLO-R下优势同样显著(0.75 vs 0.15/0.50)。该图为论文"TP+PP混合并行+分块调度"方案提供关键容量证据，论证在严格时延约束下混合并行与Sarathi调度协同带来的吞吐-时延权衡最优解。

### Figure 14 (p.13) ⭐深度解读
![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-fig14.png]]
*整页渲染: ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p13.png]]*
> [!quote] caption
> Overhead of chunked-prefills in prefill computation for Yi-34B (TP-2) normalized to the cost of no-chunking, shown for various prompt lengths using chunk lengths of 512, 1024 and 2048.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图示内容**：Yi-34B(TP-2)上chunked-prefills相对no-chunking的prefill开销归一化柱状图。横轴为prompt长度2K/4K/8K，三色柱对应chunk=512/1024/2048。读数：chunk=2048时开销≈1.00、1.00、0.97（几无额外成本）；chunk=1024约1.18–1.23；chunk=512约1.28–1.35，随prefill长度变化趋于稳定。

**技术结论**：chunked-prefills并非零代价，chunk越小overload越高（小至512时引入20%–35%额外计算），而chunk≥2048基本消除开销。

**论文作用**：量化分块预填充的计算代价，为Sarathi-Serve选用2048 chunk粒度（兼顾decode共批与prefill开销）的设计决策提供实验依据，支撑"分块几乎不损prefill效率"的核心论点。

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.10) ⭐深度解读
![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-tab01.png]]
> [!quote] caption
> Models and GPU configurations (GQA: grouped- query attention, SW: sliding window).

> [!tip] 表格解读（多模态）
> 【图文联合解读】**表1核心数据**：列出4组模型-GPU部署配置——Mistral-7B（1×A100，GQA-SW，80GB）、Yi-34B（2×A100 TP2，GQA）、LLaMA2-70B（8×A40 TP4-PP2，GQA，48GB）、Falcon-180B（2节点4×A100 TP4-PP2，GQA，80GB），参数跨度7B–180B，涵盖滑动窗口GQA与标准GQA、纯TP及TP+PP混合并行。

**论证结论**：支撑Sarathi-Serve核心主张——分块预填充与无停顿调度在不同模型规模、注意力机制及并行拓扑下均能消除生成停顿，优化吞吐-延迟权衡。

**论文作用**：作为实验基座，为后续吞吐/延迟对比提供统一硬件参照，验证方法在从单卡小模型到跨节点大模型的异构部署中具备可推广性。

### Table 2 (p.10) ⭐深度解读
![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-tab02.png]]
> [!quote] caption
> Datasets used for evaluation.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 2 图文联合解读：**

该表呈现两类评估数据集的 token 长度分布：**openchat_sharegpt4**（对话场景，prompt 中位 1730、P90=5696、Std=2088，output 中位 415、P90=834）属"短输入—中等输出"均衡型负载；**arxiv_summarization**（长文档摘要，prompt 中位 7059、P90=12985、Std=3638，output 中位 208）属典型 **prefill 主导型**长输入负载。

原文借此论证：Sarathi-Serve 的 **chunked prefill + stall-free batching** 策略在两类截然不同的负载上均能兼顾吞吐与 TBT——前者验证低 TBT 尾部延迟，后者验证对超长 prompt 分块带来的高吞吐收益。

其在论文中的作用：为后续吞吐–延迟权衡实验提供具代表性的 workload 基准，支撑"调度策略效果高度依赖负载特征"这一核心结论。

### Table 3 (p.10) ⭐深度解读
![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-tab03.png]]
> [!quote] caption
> SLOs for different model configurations.

> [!tip] 表格解读（多模态）
> 【图文联合解读】表3列出四款模型（Mistral-7B/Yi-34B/LLaMA2-70B/Falcon-180B）的P99 token-by-token延迟服务等级目标，分relaxed与strict两档：Mistral-7B为0.5/0.1s，Yi-34B为1/0.2s，LLaMA2-70B与Falcon-180B同为5/1s，模型越大SLO越宽松。原文据此在不同规模模型上分别评估Sarathi-Serve，验证chunked-prefills与stall-free batching在严格/宽松延迟约束下均能维持高吞吐。该表为后续§5.4中吞吐量-延迟权衡与消融实验确立服务质量门槛，是证明Sarathi方案跨模型通用性的关键基线。

### Table 4 (p.13) ⭐深度解读
![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-tab04.png]]
> [!quote] caption
> TTFT and TBT latency measured in seconds for hybrid-batching and chunked-prefills used in isolation as well as when they are used in tandem, evaluated over 128 requests for Yi-34B running on two A100s with a token budget of 1024. By using both hybrid-batching and chunked-prefills , Sarathi-Serve is 

> [!tip] 表格解读（多模态）
> 【图文联合解读】**1) 表格内容与结构**
Table 4 对比三种调度器在 Yi-34B（2×A100，token 预算 1024，128 请求）下、两个数据集（openchat_sharegpt4 / arxiv_summarization）的 P50 TTFT 与 P99 TBT（秒）：hybrid-batching-only TTFT 低（0.53 / 3.78）但 TBT 高（0.68 / 1.38）；chunked-prefills-only TBT 低（0.17 / 0.20）但 TTFT 高（1.04 / 5.38）；Sarathi-Serve（combined）TTFT 居中（0.76 / 3.90）却取得最低 TBT（0.14 / 0.17）。

**2) 关键结论**
单独任一技术均存在明显短板（一个保 TTFT、一个保 TBT），二者协同使用可同时压低首 token 延迟与 token 间延迟。

**3) 在论文中的作用**
作为消融实验，定量证明 Sarathi-Serve 的两大核心技术——混合批处理（hybrid-batching）与分块 prefill（chunked-prefills）——必须协同使用，缺一不可，从而支撑全文"兼顾吞吐与延迟"的核心方法论主张。

## 相关论文

- [[sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills]] — SARATHI: Efficient LLM Inference by Piggybacking Decodes with Chunked Prefills
- [[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]] — Mooncake: A KVCache-centric Disaggregated Architecture for LLM Serving
- [[sglang-efficient-execution-of-structured-language-model-programs]] — SGLang: Efficient Execution of Structured Language Model Programs
- [[efficiently-serving-large-multimodal-models-using-epd-disaggregation]] — Efficiently Serving Large Multimodal Models Using EPD Disaggregation

## 技术点深读（DEEP）

![[deep/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve.txt`（82501 字符）供引用检索。