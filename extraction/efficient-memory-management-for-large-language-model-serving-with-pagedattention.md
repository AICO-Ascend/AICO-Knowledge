---
paper_num: "52"
title: "Efficient Memory Management for Large Language Model Serving with PagedAttention"
authors: "Model Serving with PagedAttention Woosuk Kwon1,∗Zhuohan Li1,∗Siyuan Zhuang1 Ying Sheng1,2 Lianmin Zheng1 Cody Hao Yu3 Joseph E. Gonzalez1 Hao Zhang4 Ion Stoica1 1UC Berkeley 2Stanford University 3Independent Researcher 4"
date: "2023/9/13"
arxiv: "https://arxiv.org/abs/2309.06180"
pdf: "papers/efficient-memory-management-for-large-language-model-serving-with-pagedattention.pdf"
slug: "efficient-memory-management-for-large-language-model-serving-with-pagedattention"
tags: []
---

# Efficient Memory Management for Large Language Model Serving with PagedAttention

> [!abstract] 摘要（原文）
> 1. High throughput serving of large language models (LLMs) requires batching sufficiently many requests at a time. How- ever, existing systems struggle because the key-value cache (KV cache) memory for each request is huge and grows and shrinks dynamically. When managed inefficiently, this memory can be significantly wasted by fragmentation and redundant duplication, limiting the

## 元信息
- **发表日期**: 2023/9/13
- **作者**: Model Serving with PagedAttention Woosuk Kwon1,∗Zhuohan Li1,∗Siyuan Zhuang1 Ying Sheng1,2 Lianmin Zheng1 Cody Hao Yu3 Joseph E. Gonzalez1 Hao Zhang4 Ion Stoica1 1UC Berkeley 2Stanford University 3Independent Researcher 4
- **arXiv**: https://arxiv.org/abs/2309.06180
- **本地 PDF**: `papers/efficient-memory-management-for-large-language-model-serving-with-pagedattention.pdf`
- **页数**: 16

## 图表（原文 caption + 页码）

### Figure 1 (p.1) ⭐深度解读
![[assets/crops/efficient-memory-management-for-large-language-model-serving-with-pagedattention-fig01.png]]
*整页渲染: ![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p01.png]]*
> [!quote] caption
> Left: Memory layout when serving an LLM with 13B parameters on NVIDIA A100. The parameters (gray) persist in GPU memory throughout serving. The memory for the KV cache (red) is (de)allocated per serving request. A small amount of memory (yellow) is used ephemerally for activation. Right: vLLM smooths out the rapid growth curve of KV cache memory seen in existing systems [31, 60], leading to a nota

> [!tip] 技术解读（多模态）
> 【图文联合解读】左图量化展示 A100 40GB 显存分配：参数 26GB(65%) 常驻，KV Cache >30% 按请求动态分配，激活仅小片。右图双曲线对比：现有系统(橙)batch≈8 即显存触顶 39GB、吞吐仅 ~0.3k tok/s；vLLM(蓝)线性缓增、batch=40 仍可服务，吞吐稳 ~0.9k tok/s。作用：开篇动机图，揭示传统 KV 连续分配引致内部碎片严重、batch 受限，锚定 PagedAttention 分页方案——碎片降至 sub-block 量级、吞吐提升 2–4×，为全文方法与实验铺垫论证基础。

### Figure 2 (p.2) ⭐深度解读
![[assets/crops/efficient-memory-management-for-large-language-model-serving-with-pagedattention-fig02.png]]
*整页渲染: ![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p02.png]]*
> [!quote] caption
> Average percentage of memory wastes in different LLM serving systems during the experiment in §6.2. percentage of memory is used for other data, including ac- tivations – the ephemeral tensors created when evaluating the LLM. Since the model weights are constant and the ac- tivations only occupy a small fraction of the GPU memory, the way the KV cache is managed is critical in determining the maxi

> [!tip] 技术解读（多模态）
> 【图文联合解读】该图以堆叠柱状图对比四个系统的KV缓存利用率构成：Orca(Max)仅20.4%用于token states，57.3%被内部碎片吞噬；Orca(Pow2)、Orca(Oracle)虽改善分配，但仍因外部碎片（41.6%、36.6%）与过度预留（17.9%、25.2%）浪费大半；vLLM则将有效token states占比提升至96.3%，几乎消除各类碎片。数据直观证明：现有LLM服务系统因KV cache采用连续预分配策略，浪费了60–80%的宝贵显存。该量化基线为论文核心——PagedAttention以非连续分页机制消除KV cache碎片——提供了不可或缺的问题动机与对照基准。

### Figure 3 (p.4) ⭐深度解读
![[assets/crops/efficient-memory-management-for-large-language-model-serving-with-pagedattention-fig03.png]]
*整页渲染: ![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p04.png]]*
> [!quote] caption
> KV cache memory management in existing systems. Three types of memory wastes – reserved, internal fragmentation, and external fragmentation – exist that prevent other requests from fitting into the memory. The token in each memory slot represents its KV cache. Note the same tokens can have different KV cache when at different positions. 3

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

该图以一条水平连续内存条展示两段请求的KV cache分配：请求A占用7个prompt token槽("Four…fathers")+1个已生成token槽，并预留2个reserved槽，但其后留有**2038个从未使用的内部碎片**；请求B仅用3个prompt token槽+1个reserved槽，留有**507个内部碎片**；两段间的灰色间隙标注为**外部碎片(External fragmentation)**。

原文借此论证：现有系统因按最大序列长度**连续预分配**，同时产生reserved、internal fragmentation、external fragmentation三类浪费，使显存无法容纳更多并发请求。该图作为**动机图**，直接引出PagedAttention的核心思想——将KV cache拆为固定大小非连续"页"，借助块表映射消除碎片，从而在方法链路中奠定"页式显存管理"必要性的视觉证据基础。

### Figure 4 (p.5) ⭐深度解读
![[assets/crops/efficient-memory-management-for-large-language-model-serving-with-pagedattention-fig04.png]]
*整页渲染: ![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p05.png]]*
> [!quote] caption
> vLLM system overview.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图4联合解读（vLLM系统架构）**

1) **核心对象与结构**：图示含三类组件——中央**Scheduler**（调度器）通过有向边连接**KV Cache Manager**（内含两张Block tables网格）与N个并行**Worker**（每个Worker含Cache Engine+Model Shard+GPU）；KV Cache Manager下接**CPU/GPU Block Allocator**两个分配器。

2) **关键技术结论**：Scheduler集中管控请求调度；KV Cache Manager以Block Table为元数据，将GPU显存按"页"粒度（类OS虚拟内存）分配；CPU Block Allocator支持阻塞序列的溢出管理，证明PagedAttention可消除KV Cache碎片。

3) **论文整体作用**：此图是vLLM的系统总览，对应后续§4 PagedAttention算法的硬件落地——Scheduler+Block Manager实现"以页为单位的注意力计算"，是连接内存管理理论与实际GPU serving系统的桥梁，支撑了§5实验中高吞吐量的结果。

### Figure 5 (p.5) ⭐深度解读
![[assets/crops/efficient-memory-management-for-large-language-model-serving-with-pagedattention-fig05.png]]
*整页渲染: ![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p05.png]]*
> [!quote] caption
> Illustration of the PagedAttention algorithm, where the attention key and values vectors are stored as non-contiguous blocks in the memory. block size (𝐵). Denote the key block 𝐾𝑗= (𝑘(𝑗−1)𝐵+1, . . . ,𝑘𝑗𝐵) and value block 𝑉𝑗= (𝑣(𝑗−1)𝐵+1, . . . , 𝑣𝑗𝐵). The attention com- putation in Eq. 4 can be transformed into the following block- wise computation: 𝐴𝑖𝑗= exp(𝑞⊤ 𝑖𝐾𝑗/ √ 𝑑) Í⌈𝑖/𝐵⌉ 𝑡=1 exp(𝑞⊤ 𝑖𝐾𝑡1/ √ 𝑑

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图示：左侧查询向量"forth"与右侧3个非连续KV块（块大小B=4）通过箭头建立注意力计算关系。Block1存"years/ago/our/fathers"，Block2存"brought/forth"（未填满），Block0存"Four/score/and/seven"；逻辑序列为0→1→2，但物理上分散、不相邻。

论证结论：原文给出分块注意力公式A_ij=exp(qᵢᵀK_j/√d)/Σ，证明softmax注意力可按固定大小块独立计算，KV向量无需在显存中连续存储，从而彻底解耦逻辑序列顺序与物理内存布局。

论文作用：作为PagedAttention算法的标志性图示，为后续block table虚实块映射机制、显存分页管理及高吞吐LLM serving的系统实现奠定直观基础。

### Figure 6 (p.6) ⭐深度解读
![[assets/crops/efficient-memory-management-for-large-language-model-serving-with-pagedattention-fig06.png]]
*整页渲染: ![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p06.png]]*
> [!quote] caption
> Block table translation in vLLM. divides it into physical KV blocks (this is also done on CPU RAM for swapping; see §4.5). The KV block manager also maintains block tables—the mapping between logical and physical KV blocks of each request. Each block table entry records the corresponding physical blocks of a logical block and the number of filled positions. Separating logical and physical KV block

> [!tip] 技术解读（多模态）
> 【图文联合解读】**1) 核心结构（具体/量化）**：图示 Request A 的 KV 分页映射。4 个逻辑 KV 块（Block 0–3，每块容量 4 token）通过 Block Table 指向 GPU DRAM 上的物理块 **7、1、3**（序号非连续），表项含 "Physical block number" 与 "# filled"；新生成的 *fathers*、*brought* 使逻辑块 1 由 3→4、逻辑块 2 由 0→1，以黄色高亮。

**2) 论证的技术结论**：①逻辑–物理块解耦，物理块可非连续分配，消除外部碎片；②块内按 token 增量填充，`# filled` 追踪部分占用，避免预分配造成的内部浪费，并支持流式解码时原位追加。

**3) 在论文链路中的作用**：本图是 PagedAttention 的机制示意——把 OS 虚拟内存分页思想移植到 LLM 的 KV cache 管理，是后续显存高效利用、近零浪费以及请求间物理块共享等实验结论的方法论基础。

### Figure 7 (p.6) ⭐深度解读
![[assets/crops/efficient-memory-management-for-large-language-model-serving-with-pagedattention-fig07.png]]
*整页渲染: ![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p06.png]]*
> [!quote] caption
> Storing the KV cache of two requests at the same time in vLLM. requests and the latest tokens for generation phase requests) as one sequence and feeds it into the LLM. During LLM’s computation, vLLM uses the PagedAttention kernel to access the previous KV cache stored in the form of logical KV blocks and saves the newly generated KV cache into the physical KV blocks. Storing multiple tokens within

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图7 图文联合解读**

图示两并发请求（A："Four score and seven…"；B："It was the best of…"）的逻辑KV块经各自块表映射至共享的9块物理KV池（每块4 token）。物理分配**非连续且跨请求交错**：A 的逻辑块 0→物理 7、块 1→物理 1、块 2→物理 3；B 的逻辑块 1→物理 2；橙色高亮为 A 生成阶段新增 token，绿色为 B 的块。

**核心结论**：PagedAttention 通过逻辑–物理块映射的"类虚拟内存"机制，消除连续分配导致的内存碎片与浪费，支持多请求并发下的块级独立调度与跨请求内存共享（如公共前缀可共用物理块）。

**论文作用**：该图是 PagedAttention 核心机制最直观的设计级证据，为后续吞吐量、显存利用率等系统级实验提供方法基础，论证 vLLM 服务框架的可行性。

### Figure 8 (p.7) ⭐深度解读
![[assets/crops/efficient-memory-management-for-large-language-model-serving-with-pagedattention-fig08.png]]
*整页渲染: ![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p07.png]]*
> [!quote] caption
> Parallel sampling example. generates a single sequence. In the remainder of this paper, we assume the more general case in which a request gener- ates multiple sequences. In parallel sampling, one request includes multiple samples sharing the same input prompt, allowing the KV cache of the prompt to be shared as well. Via its PagedAttention and paged memory management, vLLM can realize this sharin

> [!tip] 技术解读（多模态）
> 【图文联合解读】该图展示两样本 A1、A2 并行采样的内存视图：二者 Logical Block 0（prompt "Four score and seven"）通过块表映射到同一 Physical Block 7，**Ref count=2**；当 A2 写"mothers"触发 Copy-on-write，原共享块被复制出新 Block 3（"fathers"），Ref count 由 2→1，两样本写入互不影响。原文借此论证：PagedAttention 的块级内存管理可在 prompt 共享 KV cache 的同时，仅在输出分歧处按块复制，兼顾显存节约与样本独立性，是 vLLM 高吞吐、低显存的关键设计支撑。

### Figure 9 (p.7) ⭐深度解读
![[assets/crops/efficient-memory-management-for-large-language-model-serving-with-pagedattention-fig09.png]]
*整页渲染: ![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p07.png]]*
> [!quote] caption
> Beam search example. sample space. The algorithm relies on the beam width pa- rameter 𝑘, which determines the number of top candidates retained at every step. During decoding, beam search ex- pands each candidate sequence in the beam by considering all possible tokens, computes their respective probabilities us- ing the LLM, and retains the top-𝑘most probable sequences out of 𝑘· |𝑉| candidates, wh

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图9 — Beam Search下的Paged KV缓存布局**

图示4条beam候选在block级KV缓存上的分配：**Block 0、Block 1**为全部beam共享的前缀块；候选0/1在**Block 3**处分叉，候选2/3在**Block 2**处分叉；带"×"标记的**Block 5、Block 2、Block 4、Block 8**代表其所属beam在后续步被剪枝，对应物理块随即被回收，复用为**Block 9–12**。

**原文论证的关键结论**：相较传统连续分配因beam间前缀重复和动态剪枝造成的严重碎片与显存浪费，paged block机制可同时实现①跨beam前缀KV共享与②被剪枝beam内存的即时释放，从而显著提升beam search场景下的显存利用率与批吞吐。

**在论文中的作用**：该图是PagedAttention针对beam decoding提出的内存管理方案的直观示例，与shared-prefix（Figure 7）、parallel sampling（Figure 8）共同构成"复杂采样场景"图示组，支撑全文核心论点——vLLM在多样化解码策略下均能逼近最优显存效率。

### Figure 10 (p.8) ⭐深度解读
![[assets/crops/efficient-memory-management-for-large-language-model-serving-with-pagedattention-fig10.png]]
*整页渲染: ![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p08.png]]*
> [!quote] caption
> Shared prompt example for machine translation.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**Figure 10 图文联合解读**

**1) 核心对象与结构**
图中展示两个并行翻译请求（Sequence A 与 B）的三段式结构：
- **Shared prefix**（黄色共享段，~50 token）：两序列完全相同，含指令"Translate English to French:"及三个示例对（sea otter→loutre de mer / peppermint→menthe poivrée / plush giraffe→girafe en peluche）。
- **Task input**（绿色私有段）：A 为 `"cheese" =>`，B 为 `I love you =>`。
- **Task output**（蓝色私有段）：A 输出 `fromage`，B 输出 `Je t'aime`。

**2) 原文论证的技术结论**
两请求的 prefix 完全一致，意味着 LLM serving 中该部分会产生重复的 prefill 计算与 KV cache 存储；这正是 PagedAttention 引入 **block-level KV cache sharing** 的现实驱动力——共享前缀的物理页只需分配一次，多请求复用，节省显存并避免冗余计算。

**3) 在论文整体中的作用**
作为 vLLM 共享前缀优化（如 Copy-on-Write、块表复用）的典型用例图，证明 few-shot prompting 与 system prompt 场景下 prefix 共享具有普遍性，为后续性能收益（显存节省、吞吐提升）提供具体应用背景。

### Figure 11 (p.9) ⭐深度解读
![[assets/crops/efficient-memory-management-for-large-language-model-serving-with-pagedattention-fig11.png]]
*整页渲染: ![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p09.png]]*
> [!quote] caption
> Input and output length distributions of the (a)

> [!tip] 技术解读（多模态）
> 【图文联合解读】## 图文联合解读

**1. 核心对象与数据**
图(a) ShareGPT：输入长度均值 161.31 tokens，输出均值 337.99 tokens，分布跨度大，输出长尾延伸至 ~2000 tokens；图(b) Alpaca：输入均值仅 19.31，输出均值 58.45，两者均高度集中在 0–100 tokens 区间，密度峰值约 7–8×10⁻²。两个数据集的输入/输出长度均呈现**高度异构、长尾分布**特征，且输出长度方差显著大于输入。

**2. 关键论证结论**
请求长度（尤其是输出）不可预测且差异巨大，传统基于"最长预估长度预分配连续 KV cache"的方案会造成严重内部碎片与内存浪费；这正是 PagedAttention 提出**按页非连续分配、动态拼接**的动机——以分页机制应对任意长度的生成请求。

**3. 在论文链路中的作用**
位于评估章节开头，作为实验场景的真实数据画像：ShareGPT 代表长对话、长输出压力场景，Alpaca 代表短指令场景。两者互补地验证了 vLLM/PagedAttention 在**不同负载特征**下均能维持高吞吐，证明分页 KV 缓存机制具有通用性与鲁棒性。

### Figure 12 (p.10) ⭐深度解读
![[assets/crops/efficient-memory-management-for-large-language-model-serving-with-pagedattention-fig12.png]]
*整页渲染: ![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p10.png]]*
> [!quote] caption
> Single sequence generation with OPT models on the ShareGPT and Alpaca dataset

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读**

该图以归一化延迟（s/token）对请求率（req/s）作图，对比 FasterTransformer、Orca(Max/Pow2/Oracle) 与 vLLM 在 OPT-13B/66B/175B 三种规模、ShareGPT 与 Alpaca 两个数据集共 6 种配置下的吞吐上限。数据上 vLLM 在 ShareGPT 上 OPT-13B/66B/175B 分别可承载约 1.9/1.0/2.4 req/s，远超 Orca-Oracle（约 1.0/0.45/1.6），更远超 FasterTransformer；Alpaca 上 vLLM 同样领先（OPT-175B ≈21 vs Orca-Oracle≈16 req/s）。

原文借此论证：PagedAttention 通过分页式 KV cache 消除了碎片，使单序列生成场景下 vLLM 相比 Orca 基线吞吐显著提升（长序列 ShareGPT 增益更大）。

该图属于端到端服务实验的核心证据链，与 Figure 11 的批处理吞吐共同支撑"vLLM 在所有模型规模与负载下均最优"的方法结论。

### Figure 13 (p.10) ⭐深度解读
![[assets/crops/efficient-memory-management-for-large-language-model-serving-with-pagedattention-fig13.png]]
*整页渲染: ![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p10.png]]*
> [!quote] caption
> Average number of batched requests when serv- ing OPT-13B for the ShareGPT (2 reqs/s) and Alpaca (30 reqs/s) traces.

> [!tip] 技术解读（多模态）
> 【图文联合解读】图13展示OPT-13B在ShareGPT(2 reqs/s)与Alpaca(30 reqs/s)两种负载下的平均批处理请求数对比。ShareGPT子图：vLLM=30.42，Orca(Oracle/Pow2/Max)依次为13.62/9.81/7.00，vLLM约为Orca最优的2.2倍；Alpaca子图：vLLM=132.44，Orca依次为72.75/43.24/7.00，约为Oracle的1.8倍。该图论证PagedAttention通过消除KV cache碎片化与显存浪费，使系统可同时承载更多并发请求，有效批大小显著超越传统连续批处理方案。在论文实验链路中，它与吞吐量、延迟指标互补，直接量化vLLM"更高吞吐"的核心优势，为方法有效性提供关键实证。

### Figure 14 (p.11) ⭐深度解读
![[assets/crops/efficient-memory-management-for-large-language-model-serving-with-pagedattention-fig14.png]]
*整页渲染: ![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p11.png]]*
> [!quote] caption
> Parallel generation and beam search with OPT-13B on the Alpaca dataset.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图14展示OPT-13B在Alpaca数据集上四种负载（并行生成size=2/4、束搜索width=2/4）下，vLLM（蓝/绿线）与Orca-Max、Orca-Power（红叉/橙三角）的归一化延迟（s/token）随请求速率（req/s）变化曲线。图中显示vLLM蓝色曲线在请求速率达到约15-18 req/s时延迟才开始急剧上升，而Orca-Max仅在约2 req/s、Orca-Power在约8 req/s即饱和。

**关键结论：** 在并行采样与束搜索等需要共享前缀或管理多个序列的工作负载下，vLLM凭借PagedAttention的分页KV缓存管理，将吞吐量较Orca-Max提升约7-8倍，较Orca-Power提升约2倍。

**论文作用：** 该图扩展了Figure 13的实验维度，证明PagedAttention不仅在普通自回归生成中有效，在更复杂的解码策略（并行生成、束搜索）中同样显著降低内存碎片、提升服务吞吐，巩固了vLLM方法的核心技术优势。

### Figure 15 (p.11) ⭐深度解读
![[assets/crops/efficient-memory-management-for-large-language-model-serving-with-pagedattention-fig15.png]]
*整页渲染: ![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p11.png]]*
> [!quote] caption
> Average amount of memory saving from sharing KV blocks, when serving OPT-13B for the Alpaca trace.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图(a)(b)分别量化OPT-13B服务Alpaca负载时，并行采样（输出序列数2/4/6）与束搜索（束宽2/4/6）下KV块共享带来的显存节省。并行采样节省由6.09%升至9.79%；束搜索节省则达37.56%→53.13%→55.16%，幅度与绝对值均显著更高。论文借此实证块共享对公共前缀密集的解码场景（尤以束搜索为甚）收益突出，支撑PagedAttention通过共享KV块提升显存利用率这一核心机制的有效性，是其系统级显存高效性实验论证链中的关键一环。

### Figure 16 (p.12) ⭐深度解读
![[assets/crops/efficient-memory-management-for-large-language-model-serving-with-pagedattention-fig16.png]]
*整页渲染: ![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p12.png]]*
> [!quote] caption
> Translation workload where the input prompts share a common prefix. The prefix includes (a) 1 example with 80 tokens or (b) 5 examples with 341 tokens.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图中两子图对比了翻译场景下共享前缀请求时，vLLM与Orca(Oracle)的归一化延迟(s/token)随请求速率(req/s)的变化。(a) 1-shot前缀（80 tokens）：Oracle约在30 req/s处急剧上升至~0.4，而vLLM在~48 req/s才升至~0.52；(b) 5-shot前缀（341 tokens）：Oracle仅在~10 req/s即爆发至~0.4，vLLM仍维持至~45 req/s后才升至~0.62。

**关键技术结论：** 前缀越长，Oracle基线因无法高效共享KV cache而越早饱和（30→10 req/s）；vLLM凭借PagedAttention的物理块共享机制，将饱和点保持在45–48 req/s，证明其在共享前缀场景下显著优于不可达的Oracle上限。

**论文链路作用：** 此图为端到端Serving性能验证，与Figure 13–15（吞吐、调度策略）形成完整实验链，并通过"前缀共享"压力测试，凸显vLLM内存管理在真实多请求并发场景中的核心优势。

### Figure 17 (p.12) ⭐深度解读
![[assets/crops/efficient-memory-management-for-large-language-model-serving-with-pagedattention-fig17.png]]
*整页渲染: ![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p12.png]]*
> [!quote] caption
> Performance on chatbot workload.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图17展示在聊天机器人负载下四种调度策略的归一化延迟（×token）随请求率（req/s，0–0.9）变化曲线。三种Orca变体（Max/Pow2/Oracle）在请求率达到约0.5–0.6 req/s时延迟即急剧飙升至1.0，而vLLM在约0.8 req/s仍保持低延迟（≈0.2），直至0.85 req/s才升至≈0.4。

原文借此论证：在细粒度、输入输出长度不固定的真实聊天负载下，vLLM（PagedAttention）相较Orca基线可将有效服务吞吐提升约**40–60%**。该图作为论文实验链路中端到端"真实负载验证"的关键一环，与合成长迹（Figure 15–16）共同支撑"分页式KV缓存在实际部署中显著优于连续分配"的核心结论。

### Figure 18 (p.12) ⭐深度解读
![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p12.png]]
> [!quote] caption
> Ablation experiments. handle the long prompts, as PagedAttention resolves the problem of memory fragmentation and reservation. 7

> [!tip] 技术解读（多模态）
> **Main Figure Description (Figure 18 — Ablation Experiments):**

The figure contains two subplots:

- **(a) Kernel latency (μs) vs. context length (64→256):** Compares four lines — vLLM (bs=8/32) and FasterTransformer (bs=8/32). vLLM shows 20–26% higher per-kernel latency than FT, but still wins end-to-end.
- **(b) Normalized latency (s/token) vs. block size (1→256):** Two traces (ShareGPT, Alpaca). Both form a U-shape; best region around block size 16–32. Alpaca degrades sharply beyond 32 because short sequences suffer fragmentation, while ShareGPT tolerates larger blocks.

**Data flow narrative:** tokens → PagedAttention block table → GPU KV-cache reads → attention kernel → output latency.

**Key takeaway:** PagedAttention adds ~20–26% kernel overhead over FasterTransformer, yet vLLM still outperforms it end-to-end, and a block size of 16 is the sweet spot — large enough to saturate GPU parallelism, small enough to keep internal fragmentation low.

**Caption (verbatim):** "Figure 18. Ablation experiments."

### Figure 19 (p.13) ⭐深度解读
![[assets/crops/efficient-memory-management-for-large-language-model-serving-with-pagedattention-fig19.png]]
*整页渲染: ![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p13.png]]*
> [!quote] caption
> (a) Overhead of recomputation and swapping for different block sizes. (b) Performance when serving OPT-13B with the ShareGPT traces at the same request rate.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

**(a) 微基准**：随 block size 从 1→256，Swap in、Swap out 及 Swap in+out 的耗时由 ~135/80/57 ms 急剧下降至 ~40/17/17 ms；而 Recompute 几乎与块大小无关，维持在 ~33–40 ms。二者约在 **block=16** 处发生交叉——块越大，swap 越划算。

**(b) 端到端（OPT-13B + ShareGPT）**：归一化延迟在 block=16–64 时达到最低（约 0.1 s/token）；过小（1–4）受 swap 开销主导，过大（256）则因块粒度粗、内部碎片与 KV 块复用率下降，两端均回升至 0.7–1.1 s/token。

**论文作用**：该图为 PagedAttention 选取 block size=16 提供了量化依据——必须足够大以让 swap 优于 recompute，又不能过大以避免浪费，并通过端到端实验闭环验证了这一权衡在真实负载下并非仅是微基准层面成立。

## 表格（裁剪图 + caption，可直接插入报告）

### Table 1 (p.9) ⭐深度解读
![[assets/crops/efficient-memory-management-for-large-language-model-serving-with-pagedattention-tab01.png]]
> [!quote] caption
> Model sizes and server configurations.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**图文联合解读：**

**1）表核心数据：** 三个模型规模（13B/66B/175B）对应不同硬件配置（1×A100-40G / 4×A100 / 8×A100-80G），显存总量分别为 40/160/640 GB；参数常驻占 65%（26/132/346 GB）；KV cache 可用内存 12/21/**264** GB，对应最大并发槽位 15.7K / 9.7K / **60.1K** 个。

**2）论证结论：** 参数约占显存 ⅔ 且常驻不可动（对应图1灰色区），KV cache 是剩余动态内存主体，且随 batch 激增（呼应图1右侧"现有系统 KV 暴增"曲线）——尤其是 175B 模型 KV 容量高达 264 GB，传统连续张量分配必然产生严重碎片，**直接论证 PagedAttention 分页管理 KV cache 的必要性**。

**3）论文作用：** 作为实验 baseline 配置表，贯穿后续吞吐量/批大小基准测试，证明 PagedAttention 在不同参数规模与显存预算下均能逼近理论 batch 上限，是评估方法有效性的硬件锚点。

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
P(x) = P(x_1) \cdot P(x_2\mid x_1) \cdots P(x_n \mid x_1, \ldots, x_{n-1}).
$$

$$
q_i = W_q x_i, \ k_i = W_k x_i, \ v_i = W_v x_i.
$$

$$
a_{ij} = \frac{\exp(q_i^\top k_j / \sqrt{d})}{\sum_{t=1}^{i}\exp(q_i^\top k_t / \sqrt{d})}, \ o_i = \sum_{j=1}^{i} a_{ij} v_j.
$$

$$
A_{ij} = \frac{\exp(q_i^\top K_j / \sqrt{d})}{\sum_{t=1}^{\lceil i/B \rceil}\exp(q_i^\top K_t\mathbf{1} / \sqrt{d})}, \ o_i = \sum_{j=1}^{\lceil i/B \rceil} V_j A_{ij}^\top,
$$

## 技术点深读（DEEP）

![[deep/efficient-memory-management-for-large-language-model-serving-with-pagedattention]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/efficient-memory-management-for-large-language-model-serving-with-pagedattention.txt`（82023 字符）供引用检索。