---
paper_num: "43"
title: "SGLang: Efficient Execution of Structured Language Model Programs"
authors: "Structured Language Model Programs Lianmin Zheng2∗ Liangsheng Yin3 Zhiqiang Xie1 Chuyue Sun1 Jeff Huang4 Cody Hao Yu5 Shiyi Cao2 Christos Kozyrakis1 Ion Stoica2 Joseph E. Gonzalez2 Clark Barrett1 Ying Sheng1∗ 1 Stanford "
date: "2026/1/4"
arxiv: "https://arxiv.org/abs/2312.07104"
pdf: "papers/sglang-efficient-execution-of-structured-language-model-programs.pdf"
slug: "sglang-efficient-execution-of-structured-language-model-programs"
tags: [disaggregated-serving]
---

# SGLang: Efficient Execution of Structured Language Model Programs

> [!abstract] 摘要（原文）
> 1\. 🚀 SGLang是一个用于高效编程和执行复杂Language Model Programs (LM Programs) 的系统，其前端语言通过提供生成和并行控制的Primitives简化了多调用结构。 2. ⚡️ 其运行时引入了RadixAttention以自动复用KV cache、Compressed Finite State Machine以加速结构化输出解码，以及API speculative execution以优化API-only模型。 3. 📈 实验结果表明，SGLang在多种LLM应用和模型上实现了高达6.4倍的吞吐量提升和3.7倍的延迟降低，超越了现有的推理系统。

## 元信息
- **发表日期**: 2026/1/4
- **作者**: Structured Language Model Programs Lianmin Zheng2∗ Liangsheng Yin3 Zhiqiang Xie1 Chuyue Sun1 Jeff Huang4 Cody Hao Yu5 Shiyi Cao2 Christos Kozyrakis1 Ion Stoica2 Joseph E. Gonzalez2 Clark Barrett1 Ying Sheng1∗ 1 Stanford 
- **arXiv**: https://arxiv.org/abs/2312.07104
- **本地 PDF**: `papers/sglang-efficient-execution-of-structured-language-model-programs.pdf`
- **页数**: 20

## 图表（原文 caption + 页码）

### Figure 1 (p.2) ⭐深度解读
![[assets/sglang-efficient-execution-of-structured-language-model-programs-p02.png]]
> [!quote] caption
> System architecture: An interpreter executes language primitives with optimized runtime.

> [!tip] 技术解读（多模态）
> 【MiniMax 解读】SGLang 系统架构(Fig.1)：Python 嵌入式前端+高性能 runtime，流式 interpreter 提交原语(extend/gen/fork)异步执行并保留依赖。RadixAttention 用 LRU 基数树缓存 KV，跨请求共享前缀自动复用中间注意力态。Frontiers&Dependencies 跟踪就绪原语+数据依赖→批独立操作、重叠执行藏延迟。DSL+radix-cache+依赖调度统一，比 vLLM/Guidance/LMQL 快至 6.4x。架构核心图。

### Figure 2 (p.3) ⭐深度解读
![[assets/sglang-efficient-execution-of-structured-language-model-programs-p03.png]]
> [!quote] caption
> The implementation of a multi-dimensional essay judge in SGLang utilizes the branch-solve-merge prompting technique [40]. Primitives provided by SGLang are shown in red. 2

> [!tip] 技术解读（多模态）
> 这张图展示了一段使用SGLang实现多维度文章评判器的Python代码示例，通过分支-求解-合并（branch-solve-merge）提示技术来评估一篇关于图像的文章，从清晰度、原创性和证据性等多个维度并行评判，并附有关于编程模型、语言原语和执行模式的文字说明。

### Figure 3 (p.5) ⭐深度解读
![[assets/sglang-efficient-execution-of-structured-language-model-programs-p05.png]]
> [!quote] caption
> Examples of RadixAttention operations with an LRU eviction policy, illustrated across nine time points. The figure demonstrates the dynamic evolution of the radix tree in response to various requests. These requests include two chat sessions, a batch of few-shot learning inquiries, and a self-consistency sampling. Each tree edge carries a label denoting a substring or a sequence of tokens. The nod

> [!tip] 技术解读（多模态）
> **图3 (Figure 3) 概览**

这张图展示了 **RadixAttention** 操作在 9 个时间点的示例，使用 **LRU (最近最少使用) 淘汰策略**。

**节点颜色编码：**
- 🟢 **绿色**：新添加的节点
- 🔵 **蓝色**：该时间点访问的缓存节点
- 🔴 **红色**：已被淘汰的节点

**9个时间点的演化过程：**
1. **步骤 (1)**：radix 树初始为空
2. **步骤 (2)**：处理用户消息 "Hello"，系统提示 + 对话被合并到树的单个边
3. **步骤 (3)**：新提示到达，复用前缀的 KV 缓存
4. **步骤 (4)**：新聊天会话开始，节点 "b" 被分裂以共享系统提示
5. **步骤 (5)**：因内存限制，节点 "c" 被淘汰
6. **步骤 (6)**：few-shot 学习查询到达，根节点被分裂
7. **步骤 (7)**：批量 few-shot 查询，节点 "e" 被分裂以支持共享
8. **步骤 (8)**：第二个聊天会话的消息到达，其中节点 "g" 和 "h" 被淘汰
9. **步骤 (9)**：采样更多答案（自一致性提示），节点 "i"、"k"、"l" 被淘汰

**关键概念：**
- **Radix 树**结构用于动态管理 KV 缓存
- **前缀匹配**实现缓存复用
- **Frontend-Runtime 协同设计**：前端解释器发送完整提示，运行时执行前缀匹配和复用

---

### Figure 4 (p.6) ⭐深度解读
![[assets/sglang-efficient-execution-of-structured-language-model-programs-p06.png]]
> [!quote] caption
> The decoding process of normal and compressed FSMs (the underscore _ means a space). requests by matched prefix length and prioritize requests with longer matched prefixes instead of using a first-come, first-served schedule. Alg. 1 (Appendix) shows the pseudo-code for cache-aware scheduling with contiguous batching. The algorithm uses longest-shared-prefix-first order. In more latency-sensitive s

> [!tip] 技术解读（多模态）
> **图4 深度解读**

**1) 图类型**
**架构/机制对比图** —— 展示 SGLang 提出的**压缩有限状态机（Compressed FSM）**相对于传统 FSM 的解码机制差异。属于算法/系统设计图，而非性能数据图。**

**2) 核心内容**

**图例符号系统：**
- 🔵 蓝色方块/圆 = **FSM state**（状态节点）
- 🟠 橙色方块 = **Token**（已确定的 token）
- 🟢 绿色六边形 = **LLM decode**（一次模型前向调用）

**四个子图的对比：**

| 子图 | 内容 | 状态数 | 解码调用次数 |
|------|------|--------|-------------|
| **(a) Normal FSM** | 14 个状态 (0→13)，每条边对应**单一字符** `{`, `"`, `s`, `u`, `m`, `m`, `a`, `r`, `y`, `"`, `:`, `_` | 14 | — |
| **(b) Compressed FSM** | 仅 2 个状态 (0→1)，整个字符串 `{"summary":_` 被**压缩为单条边** | 2 | — |
| **(c) Normal 解码流程** | `{" → LLM → summary → LLM → " → LLM → : → LLM → "_ → LLM` | — | **4 次 LLM 前向** |
| **(d) Compressed 解码流程** | `{" → summary → ":_ → LLM`（确定性 token 直接放行，仅歧义处调用模型） | — | **1 次 LLM 前向** |

**关键数据流逻辑：**
- (c) 中每生成一个字符级 token 都需一次完整 LLM 前向传播，即使后续字符在 FSM 中**完全确定**。
- (d) 利用 FSM 分析，识别出**单例转移边（singular-transition edges）**——即当前状态下只有唯一合法 token 的边——将其压缩为单边，从而在该位置**跳过 LLM 调用**，直接放行 token。仅在必须由模型采样歧义 token 时才触发前向传播。

**3) 一个关键技术要点**

**核心创新：Singular-Transition 压缩** —— 将 FSM 中那些**没有分支的链式转移**（如 `s→u→m→m→a→r→y` 这一必然序列）合并为单一跳变，使确定性输出段**完全绕过 LLM 前向计算**。这与现有的 logits-mask 式逐 token 解码（如 Guidance、Outlines）形成本质区别：后者即使在 FSM 状态完全确定时仍会触发一次完整的 Transformer 前向，造成巨大浪费。对长确定性前缀（如 JSON schema、代码骨架）场景，加速比可与确定性 token 数线性成正比。**

**4) Caption 逐字转录**

> **Figure 4:** The decoding process of normal and compressed FSMs (the underscore `_` means a space).
>
> 子图标注：
> - (a) Normal FSM for regex `{"summary":_`
> - (b) Compressed FSM for regex `{"summary":_`
> - (c) Decoding process with normal FSM
> - (d) Decoding process with compressed FSM
>
> （脚注 2）：In practice, the computation is not the same as what is described in the proof of Theorem 3.1 because the unpredictable number of output tokens can cause the recomputation of the KV cache.

### Figure 5 (p.7) ⭐深度解读
![[assets/sglang-efficient-execution-of-structured-language-model-programs-p07.png]]
> [!quote] caption
> Normalized throughput on Llama-7B models. Higher is better. pattern: s += context + "name:" + gen("name", stop="\n") + "job:" + gen("job", stop="\n"). Naively, the two gen primitives correspond to two API calls, meaning that the user needs to pay for the input token fee on the context twice. In SGLang, we can enable speculative execution on the first call and let it continue the generation of a fe

> [!tip] 技术解读（多模态）
> **SGLang论文 Figure 5 深度解读**

**1) 图类型**
**结果对比型柱状图（Bar Chart）**——属于端到端性能评估（End-to-End Performance）章节的标准基准对比图，用于展示 SGLang 与多个基线系统在多种 LLM 工作负载下的吞吐量对比。**

**2) 核心内容**

**组件与对比对象（共4个系统）**
| 系统 | 角色 | 颜色 |
|---|---|---|
| **SGLang** | 本文系统 | 橙色 |
| **vLLM** | 高吞吐推理引擎基线 | 绿色 |
| **Guidance** | 受控生成 DSL 基线 | 蓝色 |
| **LMQL** | 查询语言基线 | 灰色 |

**实验设置**
- **模型**：Llama-7B（开源权重，float16 精度）
- **归一化方式**：以 SGLang 为基准（SGLang 在所有 workload 上均为 1.0）
- **Y 轴**：Normalized Throughput（0.0 ~ 1.0）

**11 个测试 Workload**
MMLU、ReAct Agents、Generative Agents、Tree of Thought、Skeleton of Thought、LLM Judge、HellaSwag、JSON Decoding、Multi-Turn Chat (short)、Multi-Turn Chat (long)、DSPy RAG Pipeline

**关键数字（视觉读数）**
- **MMLU**：vLLM ≈ 0.15, Guidance ≈ 0.10（基线系统几乎"趴底"）
- **Generative Agents**：vLLM ≈ 0.9, Guidance ≈ 0.7（差距较小但仍明显）
- **Multi-Turn Chat (long)**：vLLM ≈ 0.97（最接近 SGLang）
- **Tree of Thought / Skeleton of Thought / LLM Judge / HellaSwag / JSON Decoding**：除 vLLM 有部分产出外，Guidance 和 LMQL 几乎为 0
- 跨所有负载，**SGLang 始终保持 1.0**（即最高吞吐）

**配套硬件与基线配置（正文上下文）**
- 硬件：AWS EC2 G5 实例，NVIDIA A10G（24GB）；7B 模型单卡 A10G，70B 模型用张量并行到多卡 A100 80GB
- 基线版本：Guidance v0.1.8（llama.cpp 后端），vLLM v0.2.5，LMQL v0.7.3（HF Transformers 后端）
- 指标：throughput（program instances/s）和 latency（平均延迟）

**3) 一个关键技术要点**

**SGLang 的"前端 DSL + 运行时协同设计"在结构化/多轮/Agent 工作负载上带来数量级提升**。**

具体而言，传统推理引擎（vLLM）虽然裸推理吞吐高，但**只把每个 `gen()` 调用当成一次独立 API 调用**，对结构化输出（如 JSON、select、LLM-as-judge）只能串行等待；对 Agent 类工作负载则无状态复用能力。SGLang 通过：

1. **RadixAttention**（基于前缀树的 KV cache 复用）——直接解释 Multi-Turn Chat 和 Agent 场景里反复出现的 system prompt / 上下文；
2. **推测式执行（speculative execution）**——在第一个 `gen()` 还没结束时继续吃后续 token，省一次 API 往返与输入 token 计费；
3. **结构化 primitive（`select`/`gen`+正则/regex constraint）**——避免 LMQL/Guidance 那种"先生成再校验再回滚"的浪费。

正如图中所示，**负载越"程序化"（含多 gen 调用、带约束、带分支），SGLang 相对 vLLM/Guidance/LMQL 的领先越显著**——Tree-of-Thought、JSON Decoding、LLM Judge 上 vLLM 都掉到 0.2 以下，而 SGLang 保持 1.0；最终体现为正文所述的 **最高 6.4× 吞吐提升、3.7× 延迟下降**。

**4) Caption 逐字转录**

> **Figure 5: Normalized throughput on Llama-7B models. Higher is better.**

### Figure 6 (p.8) ⭐深度解读
![[assets/sglang-efficient-execution-of-structured-language-model-programs-p08.png]]
> [!quote] caption
> Normalized latency on Llama-7B models. Lower is better. MMLU

> [!tip] 技术解读（多模态）
> **SGLang论文第8页深度解读**

**1) 图类型**

**结果对比图**（性能基准评测）——共两张柱状图，属于实验结果展示类，专注于延迟与吞吐的归一化对比。**

---

**2) 核心内容**

**Figure 6：Llama-7B 模型上的归一化延迟（Lower is Better）**

| 组件 | 内容 |
|------|------|
| **对比系统** | SGLang（橙）、vLLM（绿）、Guidance（蓝）、LMQL（灰） |
| **基准任务** | 11项：MMLU、ReAct Agents、Generate Agents、Tree of Thought、Skeleton of Thought、LLM Judge、HellaSwag、JSON Decoding、Multi-Turn Chat (short/long)、DSPy RAG Pipeline |
| **归一化基线** | LMQL 在大多数任务上作为 1.0 基准 |
| **关键观察** | SGLang 在前 8 项任务上延迟显著低于三个基线（柱高极矮）；在后 3 项（JSON、Multi-Turn Chat、DSPy RAG）中 vLLM 与 SGLang 接近（GUIDANCE/LMQL 被排除） |

**Figure 7：Mixtral-8x7B 模型上的归一化吞吐（Higher is Better）**

| 组件 | 内容 |
|------|------|
| **对比系统** | 仅 SGLang（橙）vs vLLM（绿） |
| **模型规模** | Mixtral-8x7B + 张量并行（TP） |
| **关键观察** | SGLang 在大多数基准上吞吐显著高于 vLLM；HellaSwag、JSON Decoding、DSPy RAG 上 vLLM 表现极低（柱高接近 0） |

**实验设置要点**

- **双模型规模**：Llama-7B（Figure 6）与 Mixtral-8x7B（Figure 7），后者引入张量并行
- **基准多样性**：覆盖分类（MMLU）、Agent（ReAct/Generate）、CoT（Tree/Skeleton-of-Thought）、结构化输出（JSON）、多轮对话、RAG 等典型 LLM 工作负载
- **排除项**：Guidance 和 LMQL 在后五项基准被排除——因 LMQL 慢在 token 级处理和后端未优化，Guidance 缺乏批处理与并行支持

---

**3) 关键技术要点**

**RadixAttention + 缓存感知调度实现 50%–99% 缓存命中率，平均达最优命中率的 96%**

这是 SGLang 最核心的创新。论文正文明确指出三大加速来源：

1. **KV cache 复用**：通过 Radix Tree 将请求的 prompt 分解为 token 序列，按前缀自动复用 KV cache（如 MMLU 复用 5-shot 示例、HellaSwag 复用 few-shot 示例与公共问题前缀、Agent 任务复用模板和历史调用）
2. **单程序内并行**：Tree-of-Thought、Skeleton-of-Thought 中的并行生成调用
3. **约束解码加速**：JSON 解码使用压缩有限状态机一次解码多个 token

> 文本中的关键数字：
> - 多模态基准吞吐提升 **最高 6×**
> - 生产环境（Chatbot Arena）：**单 worker 每秒处理 52.4 个请求**
> - RadixAttention 缓存命中率：**LLaVA-NeXT-34B 74.1%，LLaVA-Nextt-34B 52.4%**
> - Vicuna-33B 首 token 延迟平均降低 **1.7×**

---

**4) 图上 caption 逐字转录**

**Figure 6:**
> Figure 6: Normalized latency on Llama-7B models. Lower is better.

**Figure 7:**
> Figure 7: Normalized throughput on Mixtral-8x7B models with tensor parallelism. Higher is better.

---

**附加：图例标签（X 轴任务名）**

> MMLU | ReAct Agents | Generate Agents | Tree of Thought | Skeleton of Thought | LLM Judge | HellaSwag | JSON Decoding | Multi-Turn Chat (short) | Multi-Turn Chat (long) | DSPy RAG Pipeline

### Figure 7 (p.8) ⭐深度解读
![[assets/sglang-efficient-execution-of-structured-language-model-programs-p08.png]]
> [!quote] caption
> Normalized throughput on Mixtral-8x7B models with tensor parallelism. Higher is better. result from KV cache reuse, the exploitation of parallelism within a single program, and faster constrained decoding. Next, we explain the reasons for the speedup in each benchmark.

> [!tip] 技术解读（多模态）
> **SGLang论文第8页深度解读**

**1) 图类型**

**结果对比图**（性能基准评测）——共两张柱状图，属于实验结果展示类，专注于延迟与吞吐的归一化对比。**

---

**2) 核心内容**

**Figure 6：Llama-7B 模型上的归一化延迟（Lower is Better）**

| 组件 | 内容 |
|------|------|
| **对比系统** | SGLang（橙）、vLLM（绿）、Guidance（蓝）、LMQL（灰） |
| **基准任务** | 11项：MMLU、ReAct Agents、Generate Agents、Tree of Thought、Skeleton of Thought、LLM Judge、HellaSwag、JSON Decoding、Multi-Turn Chat (short/long)、DSPy RAG Pipeline |
| **归一化基线** | LMQL 在大多数任务上作为 1.0 基准 |
| **关键观察** | SGLang 在前 8 项任务上延迟显著低于三个基线（柱高极矮）；在后 3 项（JSON、Multi-Turn Chat、DSPy RAG）中 vLLM 与 SGLang 接近（GUIDANCE/LMQL 被排除） |

**Figure 7：Mixtral-8x7B 模型上的归一化吞吐（Higher is Better）**

| 组件 | 内容 |
|------|------|
| **对比系统** | 仅 SGLang（橙）vs vLLM（绿） |
| **模型规模** | Mixtral-8x7B + 张量并行（TP） |
| **关键观察** | SGLang 在大多数基准上吞吐显著高于 vLLM；HellaSwag、JSON Decoding、DSPy RAG 上 vLLM 表现极低（柱高接近 0） |

**实验设置要点**

- **双模型规模**：Llama-7B（Figure 6）与 Mixtral-8x7B（Figure 7），后者引入张量并行
- **基准多样性**：覆盖分类（MMLU）、Agent（ReAct/Generate）、CoT（Tree/Skeleton-of-Thought）、结构化输出（JSON）、多轮对话、RAG 等典型 LLM 工作负载
- **排除项**：Guidance 和 LMQL 在后五项基准被排除——因 LMQL 慢在 token 级处理和后端未优化，Guidance 缺乏批处理与并行支持

---

**3) 关键技术要点**

**RadixAttention + 缓存感知调度实现 50%–99% 缓存命中率，平均达最优命中率的 96%**

这是 SGLang 最核心的创新。论文正文明确指出三大加速来源：

1. **KV cache 复用**：通过 Radix Tree 将请求的 prompt 分解为 token 序列，按前缀自动复用 KV cache（如 MMLU 复用 5-shot 示例、HellaSwag 复用 few-shot 示例与公共问题前缀、Agent 任务复用模板和历史调用）
2. **单程序内并行**：Tree-of-Thought、Skeleton-of-Thought 中的并行生成调用
3. **约束解码加速**：JSON 解码使用压缩有限状态机一次解码多个 token

> 文本中的关键数字：
> - 多模态基准吞吐提升 **最高 6×**
> - 生产环境（Chatbot Arena）：**单 worker 每秒处理 52.4 个请求**
> - RadixAttention 缓存命中率：**LLaVA-NeXT-34B 74.1%，LLaVA-Nextt-34B 52.4%**
> - Vicuna-33B 首 token 延迟平均降低 **1.7×**

---

**4) 图上 caption 逐字转录**

**Figure 6:**
> Figure 6: Normalized latency on Llama-7B models. Lower is better.

**Figure 7:**
> Figure 7: Normalized throughput on Mixtral-8x7B models with tensor parallelism. Higher is better.

---

**附加：图例标签（X 轴任务名）**

> MMLU | ReAct Agents | Generate Agents | Tree of Thought | Skeleton of Thought | LLM Judge | HellaSwag | JSON Decoding | Multi-Turn Chat (short) | Multi-Turn Chat (long) | DSPy RAG Pipeline

### Figure 8 (p.9) ⭐深度解读
![[assets/sglang-efficient-execution-of-structured-language-model-programs-p09.png]]
> [!quote] caption
> (a)(b) Cache hit rate ablation study. (c) RadixAttention ablation study.

> [!tip] 技术解读（多模态）
> **SGLang论文第9页深度解读**

**1) 图类型**
**混合类型**：表格（Table 2，吞吐量对比）+ 三联子图（Figure 8，消融研究）。整体属于**消融实验 + 性能对比**页。**

**2) 核心内容**

**Table 2：多模态LLaVA吞吐量对比**
| Model | LLaVA-v1.5-7B (image) | LLaVA-NeXT-34B (video) |
|-------|---------------------|------------------------|
| Author's original implementation | 0.18 image/s | 0.02 frame/s |
| **SGLang** | **1.15 image/s** | **0.10 frame/s** |

→ 图像任务加速 **6.4×**，视频任务加速 **5×**

**Figure 8：三联消融图**
- **(a)** Cache Hit Rate vs Batch Size / Throughput（双Y轴折线）
  - 横轴：Cache Hit Rate 0–100%
  - 左轴（绿）：Batch Size 20→40+
  - 右轴（橙）：Throughput 0.4k→1.2k tokens/s
- **(b)** Cache Hit Rate vs Latency（双Y轴折线）
  - 红：Total Latency（s）从~400降到~100
  - 蓝：First Token Latency从~20降到~10
- **(c)** RadixAttention 组件消融柱状图（归一化吞吐量）
  - 4个基准：LLM Judge、Tree of Thought、MMLU、Multi-Turn Chat(short)
  - 7种配置：No Cache / No Tree Structure / FCFS Schedule / Random Schedule / No Frontend Parallelism / No Frontend Hint / **Full Optimization**

**3) 一个关键技术要点**

**RadixAttention 的"树结构 + LRU + 调度感知"三件套缺一不可。** Figure 8(c) 显示，禁用任何一个组件（缓存、树结构、调度策略、前端并行、前端hint）吞吐量都显著低于Full Optimization——尤其"Full Optimization"柱在所有基准上都接近1.0归一化值，而"No Cache"几乎贴近0。这印证了**前端语言（编程接口hint）与运行时共同设计**的重要性。**

附关键支撑数据：
- RadixAttention开销极低：管理数据结构仅0.2s/74.3s（**<0.3%**），可默认开启
- 压缩有限状态机使JSON解码吞吐量提升 **1.6×**，若不批量复用预处理反而会**降低2.4×**

**4) Caption逐字转录**

```
Table 2: Throughput comparison on multi-modal LLaVA image and video models.

Figure 8: (a)(b) Cache hit rate ablation study. (c) RadixAttention alation study.
```

（注：原图caption将"ablation"误拼为"alation"）

---

**附：6.3节消融结论摘要**
- **Cache命中率↑** → batch size↑、throughput↑、latency↓
- **RadixAttention各组件**：缓存、树结构、调度（cache-aware优于FCFS/Random）、前端并行、前端hint均为必需
- **运行时开销**：线性且微小（<0.3%）
- **压缩FSM**：批量复用是性能关键，per-request预处理会回退2.4×

### Figure 9 (p.14) ⭐深度解读
![[assets/sglang-efficient-execution-of-structured-language-model-programs-p14.png]]
> [!quote] caption
> KV cache sharing examples. Blue boxes represent shareable prompt parts, green boxes indicate non-shareable parts and yellow boxes mark non-shareable model outputs. Shareable elements include few-shot learning examples, questions in self-consistency [53], chat history in multi-turn chat, and search history in tree-of-thought [56]. A

> [!tip] 技术解读（多模态）
> **SGLang 论文页面深度解读**

**1) 图类型**

**架构/机制示意图（Mechanism Illustration）**：Figure 9 是**概念性/结构化的示意图**，用四种典型 LLM 编程模式（few-shot、self-consistency、multi-turn chat、tree-of-thought）展示 KV cache 的可共享结构。下文附录 A.1–A.3 包含**背景知识**（prefill/decoding/KV cache 定义）、**伪代码说明**和**定理证明**，整体属于论文方法论附录。**

---

**2) 核心内容**

**Figure 9 四个子图（颜色编码：蓝色=可共享 prompt 部分，绿色=不可共享部分，黄色=不可共享的模型输出）**

| 子图 | 模式 | 可共享结构（蓝） | 不可共享结构 |
|------|------|------------------|--------------|
| (a) Few-shot learning | 多个独立 Prompt 各自生成 | Few-shot examples（跨 Prompt 完全相同） | Question、Answer（每个 Prompt 不同） |
| (b) Self-consistency | 同一 Prompt 多次采样 | Question | Answer 1/2/3（多答案投票） |
| (c) Multi-turn chat | 对话多轮追加 | 累积的 Chat History | 当前轮的 Q/A |
| (d) Tree-of-thought | 树状推理分支 | 共享的 Search History 节点 | 各 Branch 状态 |

**关键概念**
- **KV Cache 定义**：自回归 Transformer 在 prefill 与 decoding 中产生的 key-value 对，仅依赖先前 token，因而**前缀相同则可复用**。
- **四种 sharing pattern**：现有系统（vLLM 仅支持 basic prefix sharing）**无法全部自动处理**，RadixAttention 能在运行时自动统一处理。
- **Theorem 3.1**（A.3）：当 cache size ≥ 最大请求长度时，**以 DFS（depth-first search）/ longest-shared-prefix-first 顺序遍历 radix tree，可获得最优 cache 命中率**。

---

**3) 一个关键技术要点**

> **RadixAttention 的核心机制**：将多请求的 prompt 视为一棵 radix tree，对共享前缀做 LRU 驱逐而非按请求驱逐，并以 DFS 顺序调度 batch，使得任意树形/分支/重复前缀结构都能在连续 batching 中复用 KV cache，从而在工程上实现"任意复杂度 prompt 程序"的自动 cache-aware 调度。Figure 9 直观地展示了它要覆盖的四类不规则 sharing pattern——正是 vLLM 等仅支持线性 prefix sharing 的系统无法处理的场景。

---

**4) 图上 caption 逐字转录**

> **Figure 9: KV cache sharing examples. Blue boxes represent shareable prompt parts, green boxes indicate non-shareable parts and yellow boxes mark non-shareable model outputs. Shareable elements include few-shot learning examples, questions in self-consistency [53], chat history in multi-turn chat, and search history in tree-of-thought [56].**

子图标签逐字转录：
- (a) Few-shot learning
- (b) Self-consistency
- (c) Multi-turn chat
- (d) Tree-of-thought

小框内文字逐字转录（按子图）：
- (a) Prompt 1 / Prompt 2 / Prompt 3；Few-shot examples；Question 1/2/3；Answer 1/2/3
- (b) Prompt → Question → {Answer 1, Answer 2, Answer 3}，分别对应 Generation 1/2/3
- (c) Turn 1 (Q/A) … Turn 4 (Q/A)；Chat History（每轮累积）
- (d) Question → Search History → Branch 1.1 / Branch 1.1.1 / Branch 1.1.1.1 / Branch 1.2 / Branch 1.2.1 / Branch 2 / Branch 2.1 / Branch 2.1.1 / Branch 2.2 / Branch 2.2.1

### Figure 10 (p.17) ⭐深度解读
![[assets/sglang-efficient-execution-of-structured-language-model-programs-p17.png]]
> [!quote] caption
> Example of how regex is converted into FSM and how FSM guides the decoding process.

> [!tip] 技术解读（多模态）
> **SGLang论文 Figure 10 深度解读**

**1) 图类型**
**架构/流程示意 + 案例演示图**。该图综合展示了**正则表达式 → FSM → 受约束解码**的完整工作流，并用两个Harry Potter信息填充实例演示FSM如何动态屏蔽非法token。**

**2) 核心内容**

**组件构成（从左到右、自上而下）**

**① Regular Expression（正则源）**：JSON Schema片段**
```json
"name": "[\w\d\s]+",
"age": "[0-9]+",
"house": "(Gryffindor|Slytherin|Ravenclaw|Hufflepuff)"
```
高亮部分是 `"age": "[0-9]+"`，对应右边的FSM子图。

**② Finite State Machine（有限状态机）**：8个状态节点（0–7），其中：**
- 状态0→1→2→3→4→5→6→7构成线性骨架，对应 `"age": "` 这段固定字符串
- 状态6带**[0-9]自环**，匹配一个或多个数字字符
- 边上的字符集标记是**token屏蔽的依据**

**③ Decoding Status（解码状态）**：两轮解码快照**
- **第1轮**：已生成 `{"name":"Harry",`，合法下一token为 `age ✓`；`Age ✗`（大小写敏感被拒）、`hou ✗`（无法闭合JSON结构）
- **第2轮**：已生成 `{"name":"Harry","age":`，合法下一token为 `0 ✓`、`1 ✓`；`fir ✗`（数字上下文屏蔽）

图例：`✓ allowed next token`，`✗ not allowed next token`。

**3) 关键技术要点**

**Logits Mask驱动的字符级约束解码**：FSM的每个状态维护一组**当前合法字符集**（accepting set）。解码时，SGLang将该集合与**token词表求交集**，生成logits mask——交集内的token logits保留，交集外token logits置为−∞。如此：**
- ✅ **保证结构合法性**：JSON括号、引号、字段名逐字符对齐，永不偏离schema
- ✅ **保证语义合法性**：`age`字段只能接数字字符，即使模型倾向于生成"Fifteen"也会被屏蔽
- ✅ **实现零重写**：无需重采样或后处理修改，结构化输出一次到位

**4) Caption逐字转录**

> **Figure 10**: Example of how regex is converted into FSM and how FSM guides the decoding process.

---

**补充：与下文B.1/B.2节的关联**

正文紧接着讨论**Compressed FSM**（B.1）与**Retokenization**（B.2）：
- **B.1**：将字符级FSM中"源节点出度唯一 + 边字符集单一"的边（singular transition edge）递归合并为一条compressed edge（文本拼接），例如 `"age": "` 这段8步线性路径可压缩为单边跳转，加速匹配。
- **B.2**：当compressed边很长时引入**Jump Forward**机制——预读后续解码字符串，但因LLM的token化粒度与字符级FSM不一致，仍需retokenization对齐，从而在保证正确性的同时获得加速。

### Figure 11 (p.18) ⭐深度解读
![[assets/sglang-efficient-execution-of-structured-language-model-programs-p18.png]]
> [!quote] caption
> Comparison of decoding using Compressed FSM versus normal FSM: The left subfigure depicts the decoding process per forward pass, while the right subfigure explains the origins of various result components. direct partitioning might alter the intended meaning [50]. For example, the compressed text in Fig. 2’s regex is {"summary": ", which can only be tokenized as {", summary, ": and _" according to

> [!tip] 技术解读（多模态）
> **SGLang论文 Figure 11 深度解读**

**1) 图类型**
**架构/流程对比图**（不是结果图）。属于"机制示意"类别：用 token 级别的展开图，对比两种 FSM-guided 解码方式在结构化生成中的执行路径差异。**

**2) 核心内容**

**组件构成**
- **左上图（Jump-Forward Decode With Compressed FSM）**：上半部为 Prefill（绿色块：`Please fill in the following information about Harry Potter.`），其后跟一连串橙色块（Jump-Forward 一次性跳过的 token 序列）和少量蓝色 Decode token。
- **左下图（Normal Decode With FSM）**：相同 Prefill 后，逐 token 展开的"密集蓝块"序列，每个结构化 token 都被独立解码。
- **右栏（Generated JSONs）**：两种方式最终输出的等价 JSON 内容：
  ```
  {
    "name": "Harry",
    "age": 15,
    "house": "Gryffindor"
  }
  ```

**关键 Token 流对比**
| 元素 | Compressed FSM（Jump-Forward） | Normal FSM |
|---|---|---|
| `{` `"name":"` `Harry` `"age":` `15` `"house":` `"Gryffindor"` `}` | 橙色块一次性 jump | 逐 token 蓝色解码 |
| 关键"内容 token" | 蓝色（`Har/ry/_Pot/ter/1/G/ryffindor`） | 全部蓝色 |
| 前向传播次数 | **显著减少** | 逐 token |

**图例（Legend）**
- 🟩 **Prefill**（绿色）：一次性前缀编码
- 🟦 **Decode**（蓝色）：常规自回归解码
- 🟧 **Jump-Forward**（橙色）：由 FSM 确定性"快进"跳过的 token

**3) 一个关键技术要点**

**Jump-Forward 解码的本质**：当 Compressed FSM 通过 regex/grammar 推断出某些 token 序列是**确定性必须出现**的（如空白 `_____`、引号 `"`、冒号 `:`、逗号 `,`、花括号 `{}`），无需 LLM 参与采样——直接在一次 forward pass 内将这些 token 整体"注入"到输出流，并只对真正的"自由 token"（如 `Harry`、`15`、`Gryffindor`）调用模型。**

**带来的收益**：**
- **减少 N 次 forward → 减少 N-1 次 decode step**，显著降低结构化输出（如 JSON、函数调用、regex-guided 文本）的端到端延迟；
- **不改变输出语义**：右侧 Generated JSONs 完全一致；
- **配合 B.2 节的 retokenization**：压缩 FSM 在跳进前会调用原 tokenizer 重对齐，避免"字符串↔token"边界错位（如 `summary` 不能被切成 `summa`+`ry`）。

这一机制是 SGLang 在结构化生成（JSON mode / regex / EBNF）场景下实现高吞吐的核心优化路径。

**4) Caption 逐字转录**

> **Figure 11**: Comparison of decoding using Compressed FSM versus normal FSM: The left subfigure depicts the decoding process per forward pass, while the right subfigure explains the origins of various result components.

**中文翻译**：**
> 图 11：使用 Compressed FSM 解码与使用普通 FSM 解码的对比：左侧子图描绘每次前向传播中的解码过程，右侧子图解释各输出结果的来源构成。

### Figure 12 (p.19) ⭐深度解读
![[assets/sglang-efficient-execution-of-structured-language-model-programs-p19.png]]
> [!quote] caption
> Normalized throughput on Llama-2-70B models with tensor parallelism. Higher is better. MMLU

> [!tip] 技术解读（多模态）
> **SGLang论文第19页深度解读**

**一、图类型判定**

本页包含**两张结果对比图** + **两节技术正文**，均为性能基准与编译器设计内容的组合。

---

**二、Figure 12: 吞吐量归一化对比（结果图）**

**核心内容：**
- **Y轴**：Throughput (Normalized)，范围0.0–1.0
- **X轴**：11个基准测试任务，覆盖推理（MMLU、HellaSwag）、智能体（ReAct Agents、Generative Agents、Tree of Thought、Skeleton of Thought、LLM Judge）、结构化输出（JSON Decoding）以及多轮对话（短/长Chat、DSPy RAG Pipeline）
- **对比对象**：SGLang（橙色）vs vLLM（绿色）
- **实验设置**：Llama-2-70B模型 + 张量并行（tensor parallelism）
- **关键数字**：SGLang在所有基准上均显著优于vLLM，部分场景吞吐量倍数达到约3–6倍（vLLM柱体高度仅0.1–0.4左右）。ReAct Agents、MMLU、JSON Decoding、Multi-Turn Chat(long) 差距尤为悬殊。

---

**三、Figure 13: 缓存命中率分析（结果图）**

**核心内容：**
- **Y轴**：Cache Hit Rate (%)
- **对比**：Achieved cache hit rate with SGLang（橙色）vs Optimal cache hit rate（浅蓝）
- **关键观察**：
  - 在MMLU、ReAct Agents、Tree of Thought、Skeleton of Thought、HellaSwag、JSON Decoding、DSPy RAG Pipeline等任务上，SGLang的**实际命中率已接近理论最优值**（差距通常<5%）
  - **短板任务**：Multi-Turn Chat(short)和Multi-Turn Chat(long)实际命中率明显低于最优（Multi-Turn Chat(short)约50% vs 最优约60%；Multi-Turn Chat(long)约55% vs 最优约75%），存在20%左右的优化空间
  - **LLM Judge**任务几乎100%达成最优

---

**四、一个关键技术要点：**RadixAttention前缀缓存的近似最优性**

这两张图联合验证了SGLang的核心创新——**基于Radix Tree的自动前缀缓存机制**：
1. Figure 12证明该机制带来的**端到端性能收益**：通过KV cache复用，吞吐量实现数倍提升
2. Figure 13证明该机制的**效率上限**：在实际工作负载上命中率逼近理论最优，说明缓存调度算法（自动radix树匹配 + LRU驱逐）设计精良
3. 多轮对话场景的命中率差距揭示了**未来优化方向**——需要处理长前缀拼接、上下文碎片化等真实场景问题

---

**五、正文关键技术：D.1 中间表示(IR)与D.2 编译器优化**

**D.1 Design and Implementation — IR图设计**
- **IR本质**：将SGLang程序表示为**计算图**，节点为原始算子，边为依赖关系
- **节点类型**：包括 `ConstantText`、`Argument`、`Gen`、`Select`、`Variable`、`Fork`、`GetForkItem`、`Join` 八种IR节点
- **两类依赖**：
  - **流内依赖**（intra-stream）：`+=` 操作必须等待流内所有前序操作完成
  - **流间依赖**（inter-stream）：跨流取值的同步需求，`fork`操作会引入此类依赖
- **构造方法**：**Tracing法**——用抽象参数运行程序动态构建图（受限于无数据依赖控制流的程序）
- **执行方式**：图构建后由**图执行器**执行，**流执行器**按拓扑序向各数据流派发IR节点

**D.2 Code Movement 优化案例**
- **优化目标**：通过**节点重排序**延长共享前缀长度，从而提升prefix sharing效率
- **激进优化性质**：不严格保持原始计算语义（aggressive optimization），属于非安全变换
- **典型例子**：将 `"Here is a question + {question}. Please act as a math expert and solve..."` 重排为 `"Please act as a math expert and solve the given question. Here is a question + {question}."` ——使公共指令前缀更长
- **创新点**：用GPT-4做**程序分析**（通过prompt + 若干SGLang IR示例），实现传统编译器技术难以自动完成的自然语言指令重排

---

**六、Caption逐字转录**

**Figure 12**: "Normalized throughput on Llama-2-70B models with tensor parallelism. Higher is better."**

**Figure 13**: "Achieved cache hit rate and optimal cache hit rate on various benchmarks."**

### Figure 13 (p.19) ⭐深度解读
![[assets/sglang-efficient-execution-of-structured-language-model-programs-p19.png]]
> [!quote] caption
> Achieved cache hit rate and optimal cache hit rate on various benchmarks. opportunities for more compilation optimizations, as we can rewrite the graph and perform more static planning. D.1

> [!tip] 技术解读（多模态）
> **SGLang论文第19页深度解读**

**一、图类型判定**

本页包含**两张结果对比图** + **两节技术正文**，均为性能基准与编译器设计内容的组合。

---

**二、Figure 12: 吞吐量归一化对比（结果图）**

**核心内容：**
- **Y轴**：Throughput (Normalized)，范围0.0–1.0
- **X轴**：11个基准测试任务，覆盖推理（MMLU、HellaSwag）、智能体（ReAct Agents、Generative Agents、Tree of Thought、Skeleton of Thought、LLM Judge）、结构化输出（JSON Decoding）以及多轮对话（短/长Chat、DSPy RAG Pipeline）
- **对比对象**：SGLang（橙色）vs vLLM（绿色）
- **实验设置**：Llama-2-70B模型 + 张量并行（tensor parallelism）
- **关键数字**：SGLang在所有基准上均显著优于vLLM，部分场景吞吐量倍数达到约3–6倍（vLLM柱体高度仅0.1–0.4左右）。ReAct Agents、MMLU、JSON Decoding、Multi-Turn Chat(long) 差距尤为悬殊。

---

**三、Figure 13: 缓存命中率分析（结果图）**

**核心内容：**
- **Y轴**：Cache Hit Rate (%)
- **对比**：Achieved cache hit rate with SGLang（橙色）vs Optimal cache hit rate（浅蓝）
- **关键观察**：
  - 在MMLU、ReAct Agents、Tree of Thought、Skeleton of Thought、HellaSwag、JSON Decoding、DSPy RAG Pipeline等任务上，SGLang的**实际命中率已接近理论最优值**（差距通常<5%）
  - **短板任务**：Multi-Turn Chat(short)和Multi-Turn Chat(long)实际命中率明显低于最优（Multi-Turn Chat(short)约50% vs 最优约60%；Multi-Turn Chat(long)约55% vs 最优约75%），存在20%左右的优化空间
  - **LLM Judge**任务几乎100%达成最优

---

**四、一个关键技术要点：**RadixAttention前缀缓存的近似最优性**

这两张图联合验证了SGLang的核心创新——**基于Radix Tree的自动前缀缓存机制**：
1. Figure 12证明该机制带来的**端到端性能收益**：通过KV cache复用，吞吐量实现数倍提升
2. Figure 13证明该机制的**效率上限**：在实际工作负载上命中率逼近理论最优，说明缓存调度算法（自动radix树匹配 + LRU驱逐）设计精良
3. 多轮对话场景的命中率差距揭示了**未来优化方向**——需要处理长前缀拼接、上下文碎片化等真实场景问题

---

**五、正文关键技术：D.1 中间表示(IR)与D.2 编译器优化**

**D.1 Design and Implementation — IR图设计**
- **IR本质**：将SGLang程序表示为**计算图**，节点为原始算子，边为依赖关系
- **节点类型**：包括 `ConstantText`、`Argument`、`Gen`、`Select`、`Variable`、`Fork`、`GetForkItem`、`Join` 八种IR节点
- **两类依赖**：
  - **流内依赖**（intra-stream）：`+=` 操作必须等待流内所有前序操作完成
  - **流间依赖**（inter-stream）：跨流取值的同步需求，`fork`操作会引入此类依赖
- **构造方法**：**Tracing法**——用抽象参数运行程序动态构建图（受限于无数据依赖控制流的程序）
- **执行方式**：图构建后由**图执行器**执行，**流执行器**按拓扑序向各数据流派发IR节点

**D.2 Code Movement 优化案例**
- **优化目标**：通过**节点重排序**延长共享前缀长度，从而提升prefix sharing效率
- **激进优化性质**：不严格保持原始计算语义（aggressive optimization），属于非安全变换
- **典型例子**：将 `"Here is a question + {question}. Please act as a math expert and solve..."` 重排为 `"Please act as a math expert and solve the given question. Here is a question + {question}."` ——使公共指令前缀更长
- **创新点**：用GPT-4做**程序分析**（通过prompt + 若干SGLang IR示例），实现传统编译器技术难以自动完成的自然语言指令重排

---

**六、Caption逐字转录**

**Figure 12**: "Normalized throughput on Llama-2-70B models with tensor parallelism. Higher is better."**

**Figure 13**: "Achieved cache hit rate and optimal cache hit rate on various benchmarks."**

### Figure 14 (p.20) ⭐深度解读
![[assets/sglang-efficient-execution-of-structured-language-model-programs-p20.png]]
> [!quote] caption
> An SGLang program and its corresponding dataflow graph.

> [!tip] 技术解读（多模态）
> **SGLang论文第20页深度解读**

**1) 图类型**

**类型：架构/示例图 + 数据流图（混合型说明图）**

本图为**Figure 14**，由两个子图组成：
- **(a) 代码示例**：展示SGLang程序源码（Python风格DSL），用以说明语言语法
- **(b) 数据流图**：将代码翻译为runtime计算图，展示执行时的并行机会

属于"**程序与数据流对照图**"，是论文用于向读者解释SGLang语义和执行模型的"教学型"插图。

---

**2) 核心内容**

**(a) SGLang程序结构**

程序实现 **Skeleton-of-Thought（SoT）提示范式** 的并行化：

```python
@function
def expand(s, tip):           # 将简短tip展开为详细段落
    s += "Please expand the following tip into a detailed paragraph: " + tip + "\n"
    s += gen("paragraph")

@function
def tip_suggestion(s, topic):
    s += "Here are 2 concise tips for " + topic + ".\n"
    # 1. 生成骨架（短tips）
    s += "1." + gen("tip_1", stop=["\n",":","."]) + "\n"
    s += "2." + gen("tip_2", stop=["\n",":","."]) + "\n"
    # 2. 并行展开
    detailed_tip1 = expand(tip=s["tip_1"])
    detailed_tip2 = expand(tip=s["tip_2"])
    # 3. 汇总
    s += "Tip 1: " + detailed_tip1["paragraph"] + "\n"
    s += "Tip 2: " + detailed_tip2["paragraph"] + "\n"
    s += "In summary" + gen("summary")
```

**关键技术语法**：**
- `@function` 装饰器：声明可复用子程序
- `gen(name, stop=...)`：调用LLM生成，`stop`参数控制生成边界
- `+=` 操作符：在共享state `s`上累积prompt
- `s["var"]`：从state中读取变量值

**(b) 数据流图**

三条**Stream**（流）对应三次函数调用：

| Stream | 角色 | 颜色 | 关键节点 |
|--------|------|------|----------|
| Stream 1 | tip_suggestion主函数 | 浅灰 | ConstantText, Argument(topic), Gen(tip_1/tip_2), Variable(paragraph), Gen(summary) |
| Stream 2 | expand(tip_1) | 黄色 | ConstantText("Please expand..."), Variable(tip_1), Gen(paragraph) |
| Stream 3 | expand(tip_2) | 蓝色 | ConstantText("Please expand..."), Variable(tip_1), Gen(paragraph) |

**数据依赖关系**：**
- Stream 1 的 `Gen("tip_1")` → Stream 1 的 `Variable("tip_1")` → 跨流边 → Stream 2 的 `Variable("tip_1")` → Stream 2 的 `Gen("paragraph")` → 跨流边 → Stream 1 的 `Variable("paragraph")`
- Stream 3 与 Stream 2 **结构对称**，二者之间无依赖 → **可并行执行**

**正文段落（评估结果）**

| 维度 | 数值/描述 |
|------|-----------|
| 收集prompt模板数 | 20 |
| 训练样本（few-shot） | 5 |
| 测试样本 | 15 |
| GPT-4成功重排序数 | 12 / 15 |
| 平均shareable prefix长度提升 | **+60 tokens** |
| 失败原因 | 过度激进地将所有常量前置，破坏语义 |
| 用途 | 探索GPT-4用于编译器优化 |

---

**3) 关键技术要点**

**🔑 核心：基于图结构的提示重排序（Prefix Merging / Reordering）**

SGLang允许用户以DSL表达LLM程序，runtime将其编译为**流式数据流图**。图中不同Stream的Gen节点**结构对称且互不依赖**，因此系统可将它们的前缀（包括常量prompt）合并成更长的**共享前缀（shareable prefix）**送入vLLM等引擎。

**该图揭示的本质**：SoT模式的两次expand调用，其prompt模板完全一致，仅输入的`tip`变量不同——这构成了**KV cache共享的机会**。通过GPT-4对图节点重排序，能将更多常量与可前缀共享的内容组织在一起，从而**延长KV cache复用的prefix长度，降低prefill冗余计算**。**

实验结果量化了此优化的有效性：**平均多共享60个token的prefix**，直接转化为吞吐量提升。

---

**4) 图上Caption逐字转录**

**Figure 14: An SGLang program and its corresponding dataflow graph.**

**子图caption (a)**：**
> The SGLang program for parallel tip suggestion with skeleton-of-thought prompting.

**子图caption (b)**：**
> A computational graph for the program in Fig. 14a. The three streams correspond to three function calls.

**节点标签（按出现顺序转录）**：**

*Stream 1*：
- ConstantText ("Here are ...")
- Argument (topic)
- ConstantText ("\n")
- ConstantText ("1.")
- Gen ("tip_1")
- ConstantText ("\n")
- ConstantText ("2.")
- Gen ("tip_2")
- ConstantText ("\n")
- ConstantText ("Tip 1:")
- Variable ("paragraph")
- ConstantText ("\n")
- ConstantText ("Tip 2:")
- Variable ("paragraph")
- ConstantText ("\n")
- ConstantText ("In summary")
- Gen (name="summary")

*Stream 2*（黄色）：
- ConstantText ("Please expand ...")
- Variable ("tip_1")
- ConstantText ("\n")
- Gen ("paragraph")

*Stream 3*（蓝色）：
- ConstantText ("Please expand ...")
- Variable ("tip_1")
- ConstantText ("\n")
- Gen ("paragraph")

## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）

$$
C \geq \sum_{e \in \text{edges}(T)} |e|.
$$

$$
C = \sum_{e \in \text{edges}(T)} |e|.
$$

$$
\frac{\sum_{r\in R}\text{number of cached prefill tokens in $r$}}{\sum_{r\in R}\text{number of prefill tokens in $r$}},
$$

## 相关论文

- [[sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills]] — SARATHI: Efficient LLM Inference by Piggybacking Decodes with Chunked Prefills
- [[taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve]] — Taming Throughput-Latency Tradeoff in LLM Inference with Sarathi-Serve
- [[efficiently-serving-large-multimodal-models-using-epd-disaggregation]] — Efficiently Serving Large Multimodal Models Using EPD Disaggregation
- [[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]] — Mooncake: A KVCache-centric Disaggregated Architecture for LLM Serving

## 技术点深读（DEEP）

![[deep/sglang-efficient-execution-of-structured-language-model-programs]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/sglang-efficient-execution-of-structured-language-model-programs.txt`（79774 字符）供引用检索。