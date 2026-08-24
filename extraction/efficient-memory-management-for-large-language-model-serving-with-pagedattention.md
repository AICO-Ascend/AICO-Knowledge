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
> 【图文联合解读】**图文联合解读：**

**核心对象与数据**：左图展示13B参数LLM在NVIDIA A100（40GB）上的内存布局——参数占26GB（65%，灰色）、KV Cache超30%（红色）、少量为激活等开销（黄色）。右图上为不同批量下的内存占用：现有系统（橙）增长陡峭，约8请求即触顶40GB；vLLM（蓝）线性缓增，约40请求才达上限。下图为吞吐量对比，vLLM在大批量下吞吐显著领先。

**关键结论**：传统系统因KV Cache按连续块预分配，内存迅速耗尽，限制批大小；vLLM通过分页化管理将内存利用率与吞吐同步拉高。

**论文作用**：Figure 1在首页定量化揭示KV Cache浪费问题，作为引入PagedAttention动机，与Table 1配置及后续消融实验共同构成"问题—方法—验证"叙事链。

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

图3以两并发请求的KV cache物理布局为例，展示了现有系统的三内存浪费：**①预留浪费**——每个请求按最大序列长度预先分配槽位（如请求A为"forth"、`<eos>`预留2槽，请求B为"once`预留1槽）；**②内部碎片**——请求A预分配后实际未用2038槽，请求B未用507槽；**③外部碎片**——两请求内存块之间的空隙无法被新请求利用。

原文借此论证：传统按"最长序列"连续预分配的方式，使显存大部分被浪费而非服务真实请求，严重限制了批处理并发度。这是PagedAttention提出"虚拟内存+非连续分页"方案的核心动机——通过将KV cache按固定page分页管理，消除三类碎片，从而提升显存利用率与系统吞吐，构成论文方法（vLLM）部分的关键问题陈述。

### Figure 4 (p.5) ⭐深度解读
![[assets/crops/efficient-memory-management-for-large-language-model-serving-with-pagedattention-fig04.png]]
*整页渲染: ![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p05.png]]*
> [!quote] caption
> vLLM system overview.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

1) **核心对象与结构**：左半图展示 vLLM 系统由三类组件构成——顶部 **Scheduler**（调度器）单向分发给 N 个 **Worker**（Worker 0…N-1），每个 Worker 内含 **Cache Engine** 与对应 GPU 上的 **Model Shard**；左侧 **KV Cache Manager** 维护两张 **Block tables**，下接 **CPU Block Allocator** 与 **GPU Block Allocator**，分别管理两种物理显存。

2) **论证的关键结论**：Scheduler 集中调度、Worker 并行执行的分层架构，使 KV Cache 逻辑块与物理块解耦——Block tables 完成"逻辑序列→物理页"的映射，从而在 GPU 显存中以非连续、固定大小的页块存储注意力 Key/Value 向量，规避传统连续预分配造成的内部碎片与浪费。

3) **论文链路中的作用**：该图给出 PagedAttention（图右）的运行底座——只有在此 Scheduler/Allocator/Block table 三层协同下，逻辑连续、KV 物理分散的分页注意力才能落地，是后续吞吐量实验（如共享 prefix、beam search 场景）实现 2–4× 提升的架构前提。

### Figure 5 (p.5) ⭐深度解读
![[assets/crops/efficient-memory-management-for-large-language-model-serving-with-pagedattention-fig05.png]]
*整页渲染: ![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p05.png]]*
> [!quote] caption
> Illustration of the PagedAttention algorithm, where the attention key and values vectors are stored as non-contiguous blocks in the memory. block size (𝐵). Denote the key block 𝐾𝑗= (𝑘(𝑗−1)𝐵+1, . . . ,𝑘𝑗𝐵) and value block 𝑉𝑗= (𝑣(𝑗−1)𝐵+1, . . . , 𝑣𝑗𝐵). The attention com- putation in Eq. 4 can be transformed into the following block- wise computation: 𝐴𝑖𝑗= exp(𝑞⊤ 𝑖𝐾𝑗/ √ 𝑑) Í⌈𝑖/𝐵⌉ 𝑡=1 exp(𝑞⊤ 𝑖𝐾𝑡1/ √ 𝑑

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

1）**核心对象与结构**：图左侧展示分布式推理架构——Scheduler 调度请求，KV Cache Manager 通过 Block tables 管理物理块，分配给 N 个 Worker（每个含 Cache Engine + Model Shard，部署于 GPU）。右侧展示 PagedAttention 核心：将一条序列 "Four score and seven years ago our fathers brought forth" 的 KV 向量切成定长 Block（Block 0/1/2），各块在内存中非连续存储，但通过块表逻辑映射；给定 Query "forth"，按需读取 Block 0（含 "Four score and seven"）和 Block 2（含 "brought forth"）参与计算。

2）**关键技术结论**：KV 缓存可像操作系统虚拟内存分页一样按块（size=B）非连续存放，分块式注意力计算（按 Kⱼ、Vⱼ 分块累加）仍然数学等价，从而彻底消除显存碎片与重复分配。

3）**论文作用**：作为方法总览图，把"分页 KV 缓存 + 块表管理 + 多 Worker 并行"链路一次性呈现，是后续块共享、Copy-on-Write 等优化的前提。

### Figure 6 (p.6) ⭐深度解读
![[assets/crops/efficient-memory-management-for-large-language-model-serving-with-pagedattention-fig06.png]]
*整页渲染: ![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p06.png]]*
> [!quote] caption
> Block table translation in vLLM. divides it into physical KV blocks (this is also done on CPU RAM for swapping; see §4.5). The KV block manager also maintains block tables—the mapping between logical and physical KV blocks of each request. Each block table entry records the corresponding physical blocks of a logical block and the number of filled positions. Separating logical and physical KV block

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读（Figure 6 — Block table translation in vLLM）：**

1) **核心对象与结构**：图左侧展示 Request A 的 Logical KV blocks（Block 0–3，存 "Four score and seven"、"years ago our fathers"、"brought" 等 token）通过 Block Table 映射到 GPU DRAM 上的 Physical KV blocks（Block 7、1、3），表项含「物理块号」与「# filled 计数」（如 4、4、1），实现非连续分配与按需填充。

2) **论证结论**：PagedAttention 打破了 KV cache 必须连续预分配的假设——逻辑块顺序固定，但物理块可分散、按需分配，避免碎片与浪费，为同前缀请求复用物理块（如图右侧 Figure 7 中 Request B 共享 Block 4、5）提供基础。

3) **链路作用**：作为 vLLM 内存管理层核心数据结构，是后续 §4.5 CPU RAM 交换、近零显存浪费与高吞吐实验结论的机制前提。

### Figure 7 (p.6) ⭐深度解读
![[assets/crops/efficient-memory-management-for-large-language-model-serving-with-pagedattention-fig07.png]]
*整页渲染: ![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p06.png]]*
> [!quote] caption
> Storing the KV cache of two requests at the same time in vLLM. requests and the latest tokens for generation phase requests) as one sequence and feeds it into the LLM. During LLM’s computation, vLLM uses the PagedAttention kernel to access the previous KV cache stored in the form of logical KV blocks and saves the newly generated KV cache into the physical KV blocks. Storing multiple tokens within

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图7图文联合解读**

①**核心对象与结构**：左图为单请求A的KV缓存——4个逻辑KV块（每块4 token，含①②③①位置编号）经Block Table（物理块号+#filled列）映射至8个非连续物理KV块（例：逻辑Block0→物理Block7、Block1→物理Block4、Block2→物理Block3）；右图为请求A、B同时存储于同一9块物理池——两者各持独立逻辑块表（A:4块，B:3块），分别指向共享物理块（Block1/7归A，Block2/5归B），实现同池共存。

②**技术结论**：Block Table解耦逻辑视图与物理布局，多请求可共享物理显存池，按需动态分配、无须预留连续空间，显存利用率逼近理论最优。

③**文中作用**：与Figure 8（parallel sampling）、beam decoding共同构成"复杂解码场景"图示组，支撑vLLM在多请求场景下保持近最优显存效率的核心论点。

### Figure 8 (p.7) ⭐深度解读
![[assets/crops/efficient-memory-management-for-large-language-model-serving-with-pagedattention-fig08.png]]
*整页渲染: ![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p07.png]]*
> [!quote] caption
> Parallel sampling example. generates a single sequence. In the remainder of this paper, we assume the more general case in which a request gener- ates multiple sequences. In parallel sampling, one request includes multiple samples sharing the same input prompt, allowing the KV cache of the prompt to be shared as well. Via its PagedAttention and paged memory management, vLLM can realize this sharin

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读（Figure 8 Parallel sampling）**

**1) 核心对象与结构**
图8展示Parallel Sampling场景：同一请求A派生出两个样本A1、A2，二者共享同一prompt前缀"Four score and seven years ago our"（逻辑Block 0–1）。分叉后A1生成"fathers"、A2生成"mothers"。中间为物理KV块表（Block 0–8），其中Block 7为原始共享前缀页，Block 2、3为分叉后各自独占页；红色"Ref count: 2→1"标注与Copy-on-write弧线显式指示：分叉触发时仅复制被修改页，前缀页引用计数递减。

**2) 关键技术结论**
PagedAttention借助分页式内存管理与Copy-on-write机制，使多输出序列的prompt前缀KV cache实现**零冗余共享**——引用计数跟踪共享块、被写时再按页复制，从而逼近显存利用的理论最优。

**3) 在论文整体中的作用**
与Figure 7（shared prefix）、Figure 9（beam search）共同构成"复杂解码策略"图示组，支撑全文核心论点：vLLM在parallel sampling、beam search等多样化解码下均能实现近最优显存效率，论证PagedAttention方案的通用性。

### Figure 9 (p.7) ⭐深度解读
![[assets/crops/efficient-memory-management-for-large-language-model-serving-with-pagedattention-fig09.png]]
*整页渲染: ![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p07.png]]*
> [!quote] caption
> Beam search example. sample space. The algorithm relies on the beam width pa- rameter 𝑘, which determines the number of top candidates retained at every step. During decoding, beam search ex- pands each candidate sequence in the beam by considering all possible tokens, computes their respective probabilities us- ing the LLM, and retains the top-𝑘most probable sequences out of 𝑘· |𝑉| candidates, wh

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图9 — Beam Search下的Paged KV缓存布局**

**核心对象与结构（量化）**：
- **左侧（Copy-on-write机制）**：样本A1与A2共享前缀逻辑块（"Four score and seven years ago our"），分叉点触发CoW——物理Block 1的引用计数由2→1（仅A2独占"mothers"），新物理Block 3独立承载A1的"fathers"分支；Block 7亦被两样本共享。
- **右侧（Beam候选块链管理）**：4个候选通过块链表组织，候选1与候选2共享Block 0→1→3的前缀链；候选2分叉后接Block 7→11；候选0与候选3因被剪枝（叉号标记Block 5/2/4/8）所占块被回收，腾出供新扩展（如Block 9/10/11/12）复用。

**关键技术结论**：Copy-on-write + 引用计数 + 块级共享，使Beam Search中多条候选序列的公共前缀无需物理重复存储，从根本上消除前缀冗余造成的内存浪费。

**在论文中的作用**：证明PagedAttention不仅适用于basic decoding（Figure 4–6），还可泛化至beam search等含前缀共享与动态剪枝的复杂解码场景，是其通用性的关键证据之一。

### Figure 10 (p.8) ⭐深度解读
![[assets/crops/efficient-memory-management-for-large-language-model-serving-with-pagedattention-fig10.png]]
*整页渲染: ![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p08.png]]*
> [!quote] caption
> Shared prompt example for machine translation.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图10展示机器翻译的共享提示（shared prompt）结构：序列A与序列B共用同一长前缀——包含"Translate English to French:"指令及三个少样本示例（"sea otter"→"loutre de mer"、"peppermint"→"menthe poivrée"、"plush giraffe"→"girafe en peluche"），仅任务输入（"cheese" vs "I love you"）与LLM输出（"fromage" vs "Je t'amie"）不同。

该图用以论证：在真实LLM服务中，多条请求常共享长前缀，少样本提示场景尤为典型；PagedAttention支持按块粒度共享前缀的KV缓存，从而显著节省显存、提升吞吐。

在论文整体链路中，它作为典型用例，支撑第4节"Sharing for Shared Prompt"等共享前缀优化机制的设计动机，与并行解码、beam search等场景并列，共同展示PagedAttention在实际工作负载下的普适价值。

### Figure 11 (p.9) ⭐深度解读
![[assets/crops/efficient-memory-management-for-large-language-model-serving-with-pagedattention-fig11.png]]
*整页渲染: ![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p09.png]]*
> [!quote] caption
> Input and output length distributions of the (a)

> [!tip] 技术解读（多模态）
> 【图文联合解读】图(a) ShareGPT：输入均值161.31 tokens，集中于近0处（峰≈1.75×10⁻²）；输出均值337.99 tokens，长尾延伸至≈2000。图(b) Alpaca：输入均值19.31 tokens（峰≈7×10⁻²），输出均值58.45 tokens。两数据集均呈"输入短、输出长且高变异"的长尾分布。

原文用以论证：请求长度方差大、输入输出长度悬殊，使KV缓存必须弹性管理，凸显PagedAttention按页分配机制的必要性。

链路作用：作为端到端服务实验的前置动机证据，与批处理吞吐结果共同支撑"vLLM在各模型规模与负载下均最优"的核心方法结论。

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
> 【图文联合解读】**图文联合解读（Figure 13）**

**(1) 核心对象与数据：** 图中含两个柱状图，对比在 OPT-13B 下四种调度方案的平均批大小。ShareGPT 轨迹（2 req/s）：Orca(Max)=7.00、Orca(Pow2)=9.81、Orca(Oracle)=13.62、vLLM=30.42；Alpaca 轨迹（30 req/s）：分别为 7.00、43.24、72.75、132.44。

**(2) 关键结论：** vLLM 的平均批处理请求数是 Orca(Max) 的 4 倍以上（ShareGPT 约 4.3×，Alpaca 约 18.9×），即便对比拥有"最优预知"的 Orca(Oracle)，vLLM 仍可承载 2–4× 的并发请求，凸显其更强的批处理吞吐能力。

**(3) 论文整体作用：** 该图在 Figure 12（延迟-请求率曲线）基础上，从"批大小"维度解释 vLLM 为何能显著拓展请求率上限：得益于 PagedAttention 的高效显存管理（消除碎片、提升 KV cache 利用率），vLLM 能容纳更大并发批，从而直接转化为更高的服务吞吐，构成方法有效性论证链的关键一环。

### Figure 14 (p.11) ⭐深度解读
![[assets/crops/efficient-memory-management-for-large-language-model-serving-with-pagedattention-fig14.png]]
*整页渲染: ![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p11.png]]*
> [!quote] caption
> Parallel generation and beam search with OPT-13B on the Alpaca dataset.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读（Figure 14）**

该图以2×3子图展示OPT-13B在Alpaca上的6组对照：上排为并行生成（size=2/4/6），下排为束搜索（width=2/4/6），横纵轴分别为请求率与归一化延迟，对比Orca三档策略与vLLM。关键量化结果：vLLM在所有配置下饱和请求率均最高，例如size=2时可达~17 req/s，显著超过Orca(Pow2)≈9与Oracle≈12；width=6时仍达~7 req/s，约为Oracle的2倍。

原文论证结论：PagedAttention通过页式KV cache实现序列间灵活共享，缓解了并行采样/束搜索造成的内存浪费，使vLLM在高资源竞争场景下依旧保持领先。

论文作用：补充第5节单序列基准实验，验证vLLM对多种并行解码策略的通用性与鲁棒性，强化"内存效率→吞吐增益"的核心论点。

### Figure 15 (p.11) ⭐深度解读
![[assets/crops/efficient-memory-management-for-large-language-model-serving-with-pagedattention-fig15.png]]
*整页渲染: ![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p11.png]]*
> [!quote] caption
> Average amount of memory saving from sharing KV blocks, when serving OPT-13B for the Alpaca trace.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图15联合解读：**

图15以两组柱状图量化KV块共享带来的内存节省：(a)并行采样下，输出序列数为2/4/6时分别节省6.09%/8.53%/9.79%；(b)束搜索下，束宽为2/4/6时分别节省37.56%/53.13%/55.16%。

数据表明束搜索场景的节省（峰值55.16%）远高于并行采样（峰值9.79%），因为beam内序列共享大量前缀token，KV块复用率高；而并行采样各序列前缀重叠有限。该结果直接验证了PagedAttention的块级共享机制在真实输入输出长度异质、请求结构复杂的Alpaca负载下仍可大幅压缩KV缓存占用。论文借此支撑核心结论——相比Orca基线，在真实聊天场景中可提升服务吞吐40–60%，构成从合成benchmark（Figure 13–14）到真实trace验证链路中的关键实证环节。

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
> 【图文联合解读】**Table 1 联合解读**

1) **核心数据**：表内列出 13B/66B/175B 三种模型的服务器配置。参数占内存分别为 26/132/346 GB；分配给 KV cache 的内存仅 12/21/264 GB，可用 KV cache slots 上限为 15.7K / 9.7K / 60.1K，呈"模型越大、每 GPU 可服务并发越少"的非线性下降。

2) **论证结论**：参数静态占用绝大部分显存，留给 KV cache 的空间极其受限；尤其 13B 模型 40 GB 显存中仅 12 GB 可作 KV cache，说明 KV cache 管理是吞吐瓶颈，必须消除碎片化。

3) **作用**：为 PagedAttention 提供量化基线——证明传统连续分配策略浪费严重，进而引出 vLLm 通过分页机制提升 KV cache slot 利用率的核心实验动机。

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