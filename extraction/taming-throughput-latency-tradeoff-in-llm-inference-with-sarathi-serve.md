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
> 【图文联合解读】图1a为0~350s生成token数曲线：Sarathi-Serve平滑升至约30K tokens，vLLM呈阶梯状，在200~220s出现明显"Generation stall"（插图标注）。图1b为P99 token间隔柱状图，在QPS=0.55/0.7/1.0下vLLM从约0.5s飙升至约1.4s（负载越高恶化越剧），Sarathi-Serve稳定在约0.3~0.35s。该图作为开篇动机图，定量揭示vLLM在高并发下存在秒级生成停顿与尾部延迟膨胀两大缺陷，为Sarathi-Serve以chunked-prefill+stall-free调度兼顾吞吐上限与消除停顿的核心论点提供直接实证依据，并奠定后文调度设计与实验评估的必要性。

### Figure 2 (p.2) ⭐深度解读
![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-fig02.png]]
*整页渲染: ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p02.png]]*
> [!quote] caption
> Current LLM serving systems involve a tradeoff be- tween throughput and latency depending on their scheduling policy. Prioritizing prefills optimizes throughput but sacrifices TBT (time-between-tokens) tail latency whereas prioritizing decodes has the opposite effect. Sarathi-Serve serves high throughput with low TBT latency via stall-free batching. (The figure is illustrative and actual values wi

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图2解读：**

**1) 结构与数据**：二维定性定位图，纵轴为Throughput（越高越好），横轴为TBT Latency（越右越差）。四个系统坐标分别为：FasterTransformer（红圆，左下——decode优先，吞吐与TBT均低）、Orca（紫圆，中部偏右——prefill优先）、vLLM（蓝圆，右上——prefill优先，吞吐高但TBT尾延迟高）；三者由灰色虚线串联，标注"迭代级批处理→Paged Attention"，构成既有方法的帕累托前沿。Sarathi-Serve（绿色星标）独立位于左上象限——高吞吐、低TBT延迟，旁注"Stall-free batching"。

**2) 关键结论**：现有系统受调度策略制约，prefill优先换高吞吐却牺牲TBT，decode优先反之，沿虚线呈此消彼长；Sarathi-Serve通过无停顿批处理跳出该曲线，**同时实现高吞吐与低TBT**，打破throughput–TBT权衡。

**3) 论文作用**：图位于第2页，作为问题动机图，先建立tradeoff认知、再预告方法定位，为后续chunked prefill、stall-free调度等机制设计与实验评估提供论证锚点。

### Figure 3 (p.5) ⭐深度解读
![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-fig03.png]]
*整页渲染: ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p05.png]]*
> [!quote] caption
> Throughput of the prefill and decode phases with different batch sizes for Mistral-7B running on a single A100 GPU. We use prompt length of 1024 for both prefill and decode experiments. Note that different y-axis, showing pre- fills are much more efficient than decode. Further, note that batching boosts decode throughput almost linearly but has a marginal effect on prefill throughput.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图3联合解读：**

该图含左右两子图（Mistral-7B / 单卡A100，prompt长度1024）：
- **Prefill**：批大小 1/2/4/8，吞吐约 4.5k→5.4k→5.2k→4.8k tokens/s，BS≥2 即饱和甚至略降；
- **Decode**：批大小 1/8/16/32/64，吞吐约 10→110→220→420→810 tokens/s，随批大小近似线性增长。两图纵轴相差近一个数量级。

**论证结论**：prefill 计算密集，单请求即吃满算力，batching 边际收益小；decode 访存密集，受制于单 token 访存开销，batching 能近乎线性放大吞吐。

**论文作用**：揭示两阶段算力–访存特性失衡这一根因，为 Sarathi-Serve 提出"分块 prefill + decode 共批（stall-free batching）"以提升整体吞吐、压低时延提供直接动机。

### Figure 4 (p.5) ⭐深度解读
![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-fig04.png]]
*整页渲染: ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p05.png]]*
> [!quote] caption
> Prefill and decode time with different input sizes for Mistral-7B running on single A100 GPU. Linear layers contribute to the majority of runtime in both prefill and decode phases. Due to the low arithmetic intensity in decode batches, the cost of linear operation for 1 decode token is nearly same as 128 prefill tokens. into linear, attention and others, and shows their individual contributions. F

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图4解读：**

**1）核心数据：** 左图为Mistral-7B在A100上的Prefill耗时（序列长度128→2k），从约33ms单调上升至约143ms，其中linear层（青色斜纹）始终占主体（2k时约120ms），attention与others占比小。右图为Decode耗时（batch size 1→64），全程几乎持平于18–23ms，linear仍为主，attention可忽略。

**2）关键结论：** Prefill与Decode均以linear层为瓶颈；因decode算术强度低，**1个decode token的linear开销≈128个prefill token**，且增加batch几乎不放大延迟，说明decode是访存受限。

**3）在论文中的作用：** 该图是Sarathi-Serve提出"chunked prefill+decode共批"（splitwise）的核心动机——证明把prefill小块塞进decode batch可被现有GPU带宽"免费"吸收，从而打破throughput–latency权衡，同时解释了为何大batch下throughput仍受限。

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
> 【图文联合解读】图7沿时间轴横向对比四种调度的迭代块序列：vLLM在A_d、B_d之后串入C_p、D_p两个全prefill，导致A、B的decode发生stall（标注"TBT with prefill interference"）；Orca以C_p/D_p/A_d/B_d混合批处理，但因长prompt执行时长仍高，无法消除A、B的stall；FasterTransformer则反复多轮A_d/B_d直至A、B退出才调度C_p、D_p，虽无decode stall但新请求prefill却停滞；Sarathi-Serve将C、D的prefill各切分为p1、p2两chunk，在A_d、B_d的decode间隙交叉插入，实现全程"No stalls"。

该图是论文核心可视化论据，定量证明仅靠"混合批"或"优先级极端倾斜"都无法双赢——唯有**chunked prefill与decode交错**才能兼顾吞吐与延迟，直接引出Sarathi-Serve"分块+交错调度"的核心方法论，并为后续Figure 8的stall-free时间线与正文throughput–latency tradeoff论证提供基础。

### Figure 8 (p.7) ⭐深度解读
![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-fig08.png]]
*整页渲染: ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p07.png]]*
> [!quote] caption
> A 2-way pipeline parallel iteration-level schedule in Orca across 4 requests (A,B,C,D) shows the existence of pipeline bubbles due to non-uniform batch execution times.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图8 联合解读**

图8对比两套2路PP调度（GPU0+GPU1×4请求A-D）时间线：
① **Orca（上行）**：两GPU错位执行，标出两类灰色气泡——prefill长度差异（A_p/B_p vs C_p/D_p耗时不同）及prefill/decode相互干扰（解码等待下一个prefill完成），出现明显空档；
② **Sarathi-Serve（下行）**：将每请求切分为A_p1/A_p2/A_d1/A_d2等定长块，两GPU锁步执行，标注"Minimal Bubbles"，气泡几乎不可见。

原文借此论证：变长prefill与prefill-decode共存是Orca流水线气泡的两大根源，而uniform-compute批次（分块prefill）能基本消除之。该图是Sarathi-Serve核心设计——**chunked-prefill+uniform batch**——的关键动机图，为后续吞吐-时延权衡实验奠定理论依据。

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
> 【图文联合解读】**图文联合解读**

图11含(a)(b)两子图，对比 Orca、vLLM、Sarathi-Serve 三种调度器在 LLaMA2-70B 与 Falcon-180B（均采用流水线并行 PP）下的最大容量（Max Capacity），分别在严格 SLO-S 与宽松 SLO-R 下评估。(a) openchat_sharegpt4 上 Sarathi 相对 vLLM 提升 **5.54–6.31×**；(b) arxiv_summarization 上严格 SLO 下为 **4.20–4.69×**，宽松 SLO 下为 **2.75–3.00×**。

**关键结论**：Sarathi-Serve 在满足时延 SLO 的同时显著提高吞吐，且严格 SLO 下优势更突出，验证其 chunked-prefill + decode-fusion 调度对流水线并行大模型同样有效。该实验将论证从单 GPU 张量并行场景扩展到多节点 PP 场景，补强了全文的方法—实验论证链。

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
> 【图文联合解读】**图13联合解读**

图13以Falcon-180B为对象，对比跨节点并行策略。(a)P50 TBT条形图：batch 8→128时，纯跨节点TP8从~0.19s升至~0.36s，而TP4:PP2（节点内TP+跨节点PP）稳定在0.08–0.15s，batch=128时差距达2.4×。(b)容量图：SLO-S下Sarathi-Serve TP4:PP2达~0.6，是vLLM TP8（~0.13）与vLLM TP4:PP2（~0.15）的~4.6×与4×；SLO-R下亦达~0.75。

该图论证两点：①跨节点TP因通信开销大导致TBT膨胀、扩展性差，应以PP替代；②在混合并行配置下，Sarathi-Serve的chunked-prefill与融合调度显著放大吞吐。它在论文中作为核心方法（延迟-吞吐权衡调度）面向跨节点超大模型场景的关键实验支撑，验证"避免跨节点TP + 采用Sarathi调度"是同时满足SLO与高吞吐的必要组合。

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
> 【图文联合解读】**图表联合解读：**

该表枚举 4 个模型(Mistral-7B、Yi-34B、LLaMA2-70B、Falcon-180B)的实验配置：注意力机制上仅 Mistral-7B 采用 GQA-SW，其余均为 GQA；GPU 配置覆盖 1 卡 A100 到 4×2 节点、TP2 至 TP4-PP2 四种并行拓扑，单卡显存 80 GB(A100)或 48 GB(A40)，总显存从 80 GB 扩展至 640 GB。

论文以该表作为**统一实验基准**，配合图 1 中 Yi-34B(A100×2)在 vLLM 中出现数秒级 generation stall 的现象，论证 Sarathi-Serve 在**不同模型规模与并行拓扑**下均能消除停顿、提升吞吐，从而支撑其"chunked-prefill + 紧致调度方案对从 7B 到 180B 的 LLM 推理通用有效"的核心结论。

### Table 2 (p.10) ⭐深度解读
![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-tab02.png]]
> [!quote] caption
> Datasets used for evaluation.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

1) **核心数据**：表 2 列出两个评估数据集的 prompt/output token 长度分布。*openchat_sharegpt4*（对话类）prompt 中位数 1730、P90 5696、Std 2088；output 中位数 415、P90 834、Std 101。*arxiv_summarization*（长文摘要）prompt 中位数 7059、P90 12985、Std 3638；output 中位数 208、P90 371、Std 265。

2) **原文引用说明**：所引段落实际讨论的是 Figure 2（吞吐-延迟权衡示意），并未直接论述表 2。表 2 的作用由其内容本身体现：两份数据集在 prompt 长度上差异悬殊（短对话 vs 长摘要），恰好对应 Sarathi-Serve 所要处理的 prefill 主导与 decode 主导混合负载场景。

3) **实验链路作用**：作为评测 workload 的形式化刻画，为后续 stall-free batching 在异构输入/输出长度下保持低 TBT 与高吞吐的实验结论提供分布依据。

### Table 3 (p.10) ⭐深度解读
![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-tab03.png]]
> [!quote] caption
> SLOs for different model configurations.

> [!tip] 表格解读（多模态）
> 【图文联合解读】Table 3 定义了四种模型（Mistral-7B、Yi-34B、LLaMA2-70B、Falcon-180B）在 relaxed 与 strict 两种 SLO 下的 P99 TBT 阈值，分别为 0.5/0.1s、1/0.2s、5/1s、5/1s。可见 SLO 随模型规模放宽（参数越大，prefill/decode 单步越慢），且 strict 恰为 relaxed 的 1/5。该表为 Sarathi-Serve 实验设定量化成功门槛，用以回答 §5.4.1 chunked-prefills 自身开销及 §5.4.2 其与 stall-free batching 单独/联合效果两个关键问题，是衡量系统在吞吐–延迟权衡下能否达标的核心依据。

### Table 4 (p.13) ⭐深度解读
![[assets/crops/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-tab04.png]]
> [!quote] caption
> TTFT and TBT latency measured in seconds for hybrid-batching and chunked-prefills used in isolation as well as when they are used in tandem, evaluated over 128 requests for Yi-34B running on two A100s with a token budget of 1024. By using both hybrid-batching and chunked-prefills , Sarathi-Serve is 

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

1) **表结构与数据**：Table 4 比较三种调度策略在 Yi-34B（2×A100，128 请求，token 预算 1024）下，对 openchat_sharegpt4 与 arxiv_summarization 两个数据集的 P50 TTFT 与 P99 TBT（秒）。hybrid-batching-only TTFT 最低（0.53/3.78）但 TBT 最高（0.68/1.38）；chunked-prefills-only 反之，TTFT 最高（1.04/5.38）但 TBT 低（0.17/0.20）；Sarathi-Serve 联合使用时 TBT 最低（0.14/0.17），TTFT 仅小幅上升（0.76/3.90）。

2) **关键结论**：单独使用任一技术都无法同时压低 TTFT 与 TBT，二者存在此消彼长；唯有 hybrid-batching 与 chunked-prefills 协同（Sarathi-Serve），才能在两个维度同时取得最优或近优，验证了"组合即优势"的核心设计主张。

3) **论文作用**：该表是方法有效性实验的核心证据，支撑 throughput–latency 权衡可被同时优化的关键论断，直接印证 Sarathi-Serve 系统设计的合理性。（注：题目所引 Figure 4 论述 prefill/decode 线性层耗时，与本表内容无直接对应。）

## 相关论文

- [[sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills]] — SARATHI: Efficient LLM Inference by Piggybacking Decodes with Chunked Prefills
- [[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]] — Mooncake: A KVCache-centric Disaggregated Architecture for LLM Serving
- [[sglang-efficient-execution-of-structured-language-model-programs]] — SGLang: Efficient Execution of Structured Language Model Programs
- [[efficiently-serving-large-multimodal-models-using-epd-disaggregation]] — Efficiently Serving Large Multimodal Models Using EPD Disaggregation

## 技术点深读（DEEP）

![[deep/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve.txt`（82501 字符）供引用检索。