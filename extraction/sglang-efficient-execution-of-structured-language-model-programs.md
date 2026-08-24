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
![[assets/crops/sglang-efficient-execution-of-structured-language-model-programs-fig01.png]]
*整页渲染: ![[assets/sglang-efficient-execution-of-structured-language-model-programs-p02.png]]*
> [!quote] caption
> System architecture: An interpreter executes language primitives with optimized runtime.

> [!tip] 技术解读（多模态）
> 【图文联合解读】图示三模块串联架构：①**前端客户端**封装语言原语（Sec.2）→②**黄色 Interpreter 模块**作为调度桥梁→③**蓝色 Runtime 后端**集成三项核心优化——RadixAttention（Sec.3）、压缩有限状态机（Sec.4）、API 推测执行（Sec.5）。各组件与后续章节一一锚定。

**技术结论**：该图论证 SGLang 通过"原语—解释器—优化运行时"的解耦分层，将高层结构化生成语义与底层 KV 缓存复用、状态机压缩、推测解码等系统级优化分离，使复杂 LLM 程序既可编程又可高效执行。

**链路作用**：作为§1→§5 方法总纲图，串联四大技术模块（§2 原语、§3 缓存、§4 FSM、§5 推测），并为§6 在 HumanEval/MTBench 基准上相较 vLLM、Guidance、LMQL 实现最高 **6.4×** 加速的实验结论提供架构层面的因果支撑。

### Figure 2 (p.3) ⭐深度解读
![[assets/crops/sglang-efficient-execution-of-structured-language-model-programs-fig02.png]]
*整页渲染: ![[assets/sglang-efficient-execution-of-structured-language-model-programs-p03.png]]*
> [!quote] caption
> The implementation of a multi-dimensional essay judge in SGLang utilizes the branch-solve-merge prompting technique [40]. Primitives provided by SGLang are shown in red. 2

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图2图文联合解读**

该图展示一个SGLang程序，使用branch-solve-merge提示技术实现多维度作文评分，定义了3个评分维度（Clarity、Originality、Evidence），代码含12处SGLang原语（红色，如`system/user/assistant/select/fork/gen/regex`）。流程为：①构造多模态对话（图像+作文）；②用`select`原语做"related"二分类判断并用Python控制流提前返回；③`s.fork(len(dimensions))`拆出3个并行分支，每路用`gen(stop="END")`独立评判；④join合并生成summary与grade；⑤用`regex=schema`约束输出JSON。

原文用它论证：SGLang原语既能表达复杂LM程序，又自动启用三类运行时优化——KV缓存复用（Sec.3，用于fork共享前缀）、快速约束解码（Sec.4，通过regex）、API推测执行（Sec.5）。

在论文整体链路中，该图作为核心示例，展示SGLang将"结构化LM程序"与"底层推理优化"统一于同一原语层，奠定后续性能实验的设计基础。

### Figure 3 (p.5) ⭐深度解读
![[assets/crops/sglang-efficient-execution-of-structured-language-model-programs-fig03.png]]
*整页渲染: ![[assets/sglang-efficient-execution-of-structured-language-model-programs-p05.png]]*
> [!quote] caption
> Examples of RadixAttention operations with an LRU eviction policy, illustrated across nine time points. The figure demonstrates the dynamic evolution of the radix tree in response to various requests. These requests include two chat sessions, a batch of few-shot learning inquiries, and a self-consistency sampling. Each tree edge carries a label denoting a substring or a sequence of tokens. The nod

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图示9个时间点RadixAttention基数树的演化：根节点出发，两类聊天分支共享系统提示"You are a helpful assistant."公共前缀；少样本链（Question1–Answer1…Question3）与自一致性多采样（"This is…/Let us…/We can…/To solve…"）依次挂载为子分支。节点c、j等在(5)(8)(9)经LRU驱逐（橙色×标记）。

**技术结论：** 基数树实现自动前缀共享KV缓存，无需手动提示管理；LRU策略保证热点prompt常驻、冷分支及时淘汰。

**论文作用：** 作为SGLang运行时核心机制的可视化证据，为后续提示复用吞吐量与延迟基准实验提供机制基础。

### Figure 4 (p.6) ⭐深度解读
![[assets/crops/sglang-efficient-execution-of-structured-language-model-programs-fig04.png]]
*整页渲染: ![[assets/sglang-efficient-execution-of-structured-language-model-programs-p06.png]]*
> [!quote] caption
> The decoding process of normal and compressed FSMs (the underscore _ means a space). requests by matched prefix length and prioritize requests with longer matched prefixes instead of using a first-come, first-served schedule. Alg. 1 (Appendix) shows the pseudo-code for cache-aware scheduling with contiguous batching. The algorithm uses longest-shared-prefix-first order. In more latency-sensitive s

> [!tip] 技术解读（多模态）
> 【图文联合解读】图(a)将正则`{"summary": "_"}`展开为14个FSM状态，解码需4次调用LLM；(b)把确定性序列压缩为2个状态，(c)(d)显示调用由4次降至2次，且`_`仍为空格。结论：压缩可跳过确定前缀，减少状态转移和模型调用，从而降低延迟、提升吞吐；该图连接FSM压缩原理与实际解码、缓存调度及后续性能验证。

### Figure 5 (p.7) ⭐深度解读
![[assets/crops/sglang-efficient-execution-of-structured-language-model-programs-fig05.png]]
*整页渲染: ![[assets/sglang-efficient-execution-of-structured-language-model-programs-p07.png]]*
> [!quote] caption
> Normalized throughput on Llama-7B models. Higher is better. pattern: s += context + "name:" + gen("name", stop="\n") + "job:" + gen("job", stop="\n"). Naively, the two gen primitives correspond to two API calls, meaning that the user needs to pay for the input token fee on the context twice. In SGLang, we can enable speculative execution on the first call and let it continue the generation of a fe

> [!tip] 技术解读（多模态）
> 【图文联合解读】该图横轴含11种结构化任务（MMLU、ReAct、Generative Agents、Tree/Skeleton of Thought、JSON Decoding、多轮对话、DSPy Pipeline等），纵轴为Llama-7B上的归一化吞吐，SGLang被归一为1.0基准，对比vLLM、Guidance、LMQL。SGLang全任务领先：Generative Agents下vLLM≈0.92、Guidance≈0.68；HellaSwag/DSPy下vLLM仅0.02–0.16，其他系统大多<0.5。

结合caption中"两次gen即两次重复计费context"的场景，论证SGLang通过RadixAttention与推测式调度有效复用共享前缀，显著优于vLLM前缀缓存及Guidance/LMQL的编译器式方案，是论文核心性能证据。

### Figure 6 (p.8) ⭐深度解读
![[assets/crops/sglang-efficient-execution-of-structured-language-model-programs-fig06.png]]
*整页渲染: ![[assets/sglang-efficient-execution-of-structured-language-model-programs-p08.png]]*
> [!quote] caption
> Normalized latency on Llama-7B models. Lower is better. MMLU

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

**核心对象与数据：** 在Llama-7B上对比SGLang、vLLM、Guidance、LMQL四系统在11个任务上的归一化延迟（多数任务以LMQL=1.0为基准，数值越低越好）。结构化生成类任务（MMLU、ReAct、Generative Agents、Tree-of-Thought、Skeleton-of-Thought、LLM Judge、HellaSwag）上，SGLang延迟普遍降至0.04–0.18，相对LMQL提速约5–25倍；JSON Decoding（~0.20）亦明显优于vLLM（~0.98）；而在Multi-Turn Chat、Multi-Turn Chat(long)、DSPy RAG等通用场景中，各系统延迟趋同（约0.7–1.0）。

**技术结论：** SGLang的加速效果并非Llama-7B单点现象，而是跨任务类型的系统性优势，尤其在多调用/结构约束场景中最为突出。

**论文链路作用：** 与Figure 5（Llama-7B主结果）形成补充，证明其吞吐优势可跨并行策略与任务结构稳健复现，强化"方法通用性"论证。

### Figure 7 (p.8) ⭐深度解读
![[assets/crops/sglang-efficient-execution-of-structured-language-model-programs-fig07.png]]
*整页渲染: ![[assets/sglang-efficient-execution-of-structured-language-model-programs-p08.png]]*
> [!quote] caption
> Normalized throughput on Mixtral-8x7B models with tensor parallelism. Higher is better. result from KV cache reuse, the exploitation of parallelism within a single program, and faster constrained decoding. Next, we explain the reasons for the speedup in each benchmark.

> [!tip] 技术解读（多模态）
> 【图文联合解读】【核心】图示 Mixtral-8x7B + TP 下，SGLang（橙）与 vLLM（绿）在 11 类基准上的归一化吞吐。SGLang 均归一为 1.0；vLLM 在 HellaSwag/MMLU/JSON Decoding/ReAct/DSPy RAG 仅 0.03–0.10，Tree-of-Thought/LLM Judge 约 0.25–0.30，Generative Agents/Skeleton-of-Thought 与 Multi-Turn Chat(long) 最高也仅 0.58–0.70。

【技术结论】证明 SGLang 在所有结构化 LLM 程序场景下均显著快于 vLLM，加速来源为 KV cache 复用、程序内并行挖掘与更快的受限解码。

【论文作用】作为性能收尾证据，与前图共同验证 RadixAttention 与前端优化跨负载、跨模型规模均提供稳定加速优势。

### Figure 8 (p.9) ⭐深度解读
![[assets/crops/sglang-efficient-execution-of-structured-language-model-programs-fig08.png]]
*整页渲染: ![[assets/sglang-efficient-execution-of-structured-language-model-programs-p09.png]]*
> [!quote] caption
> (a)(b) Cache hit rate ablation study. (c) RadixAttention ablation study.

> [!tip] 技术解读（多模态）
> 【图文联合解读】图8含三子图：(a)(b)显示缓存命中率0–100%时吞吐由~0.4k升至1.2k token/s、总延迟由400s降至~130s；(c)对比LLM Judge、ToT、MMLU、Multi-Turn Chat四类负载下七种配置（无缓存/无树/FCFS/随机/无前端并行/无前端提示/全优化）的归一化吞吐，全优化（橙色）均达到1.0，明显优于任一组件缺失。该图论证RadixAttention、前端并行与提示协同显著提升性能，是论文方法链路的消融实验核心，支撑SGLang端到端优化有效性的关键证据。

### Figure 9 (p.14) ⭐深度解读
![[assets/crops/sglang-efficient-execution-of-structured-language-model-programs-fig09.png]]
*整页渲染: ![[assets/sglang-efficient-execution-of-structured-language-model-programs-p14.png]]*
> [!quote] caption
> KV cache sharing examples. Blue boxes represent shareable prompt parts, green boxes indicate non-shareable parts and yellow boxes mark non-shareable model outputs. Shareable elements include few-shot learning examples, questions in self-consistency [53], chat history in multi-turn chat, and search history in tree-of-thought [56]. A

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图9图文联合解读**

该图以四种典型 LLM 编程模式展示 KV cache 共享结构：(a) Few-shot——三个 Prompt 共享相同的 "Few-shot examples" 前缀；(b) Self-consistency——同一 Question 派生出三条独立 Answer；(c) Multi-turn chat——Chat History 随轮次累积延长，每轮仅追加新的 Q/A；(d) Tree-of-thought——沿分支路径共享逐层 Search History。蓝/绿/黄三色分别标注可共享 prompt、非共享输入、非共享输出。

论文借此论证：在结构化 LM 程序中**存在大量相同前缀**（few-shot 示例、对话历史、搜索路径），KV cache 复用空间显著。该图为 SGLang 核心机制 **RadixAttention（前缀共享调度）** 提供具体应用场景的动机支撑，是连接"LM 程序结构特性"与"系统级缓存优化"的关键概念桥梁。

### Figure 10 (p.17) ⭐深度解读
![[assets/crops/sglang-efficient-execution-of-structured-language-model-programs-fig10.png]]
*整页渲染: ![[assets/sglang-efficient-execution-of-structured-language-model-programs-p17.png]]*
> [!quote] caption
> Example of how regex is converted into FSM and how FSM guides the decoding process.

> [!tip] 技术解读（多模态）
> 【图文联合解读】图示3类 JSON 正则（姓名、age `[0-9]+`、4学院枚举）编译为 FSM；age 路径含8个状态0–7：`"a"→"g"→"e"→":"→数字→逗号`，状态6对0–9自环。解码name后，FSM借logits掩码放行`age`、`0/1`，屏蔽`Age`、`hou`、`fif`。它说明SGLang以逐token合法转移保证JSON、减少回退；本图是机制示意，非性能实验。

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
![[assets/crops/sglang-efficient-execution-of-structured-language-model-programs-fig12.png]]
*整页渲染: ![[assets/sglang-efficient-execution-of-structured-language-model-programs-p19.png]]*
> [!quote] caption
> Normalized throughput on Llama-2-70B models with tensor parallelism. Higher is better. MMLU

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图对比 SGLang 与 vLLM 在 Llama-2-70B（张量并行）下 11 项结构化程序的归一化吞吐：SGLang 皆归一为 1.0；vLLM 跨度极大——HellaSwag 仅 ~0.03、Skeleton-of-Thought 最高 ~0.82；MMLU/ReAct/JSON/DSPy 约 0.12–0.18，多轮短/长聊天约 0.40/0.73。

**技术结论：** SGLang 在所有结构化程序负载上全面领先 vLLM，Agent/RAG/多轮等分支多调用工作流优势最为显著，定量验证 RadixAttention 跨调用前缀复用对复杂 LLM 程序的加速核心价值。

**论文作用：** 承担吞吐主实验基准，与前后图表共同构建"结构化程序×多后端×多模型"完整对比链，定量支撑 SGLang 系统级方法的有效性。

### Figure 13 (p.19) ⭐深度解读
![[assets/crops/sglang-efficient-execution-of-structured-language-model-programs-fig13.png]]
*整页渲染: ![[assets/sglang-efficient-execution-of-structured-language-model-programs-p19.png]]*
> [!quote] caption
> Achieved cache hit rate and optimal cache hit rate on various benchmarks. opportunities for more compilation optimizations, as we can rewrite the graph and perform more static planning. D.1

> [!tip] 技术解读（多模态）
> 【图文联合解读】图13以分组柱状图对比10个基准上SGLang实际缓存命中率（橙）与理论最优命中率（蓝）。多数任务命中率超85%，与最优仅差1-3%（Tree of Thought ~98%、HellaSwag ~99%、DSPy RAG ~92%），印证Cache调度接近最优。但**Multi-Turn Chat**差距显著：短对话~48% vs 60%、长对话~57% vs 73%，相差12-16个百分点。原文借此论证多轮场景中前缀复用模式更复杂，仍存图重写与静态规划优化空间，作为附录D.1"更多编译优化机会"的量化支撑。

### Figure 14 (p.20) ⭐深度解读
![[assets/crops/sglang-efficient-execution-of-structured-language-model-programs-fig14.png]]
*整页渲染: ![[assets/sglang-efficient-execution-of-structured-language-model-programs-p20.png]]*
> [!quote] caption
> An SGLang program and its corresponding dataflow graph.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

**1) 核心对象与结构：** 图(b)展示了对应Fig.14a程序的数据流图，共3条Stream（对应3次函数调用）。Stream 1约16个节点，依次为ConstantText("Here are…")、Argument(topic)、Gen("tip_1")、Gen("tip_2")、Gen("summary")等；Stream 2/3各4个节点，含Variable("tip_1")与Gen("paragraph")。关键边：Stream 1的Gen("tip_1")、Gen("tip_2")输出通过箭头指向Stream 2/3的Variable节点。

**2) 论证结论：** 证明SGLang程序可被自动编译为数据流图，显式表达变量依赖关系；运行时据此识别跨函数调用的中间结果复用与并行机会。

**3) 整体作用：** 该图是SGLang"前端编译→运行时调度"链路的核心可视化，支撑后续关于batch调度、并行执行与前缀复用优化的论述。

## 表格（裁剪图 + caption，可直接插入报告）

### Table 2 (p.9) ⭐深度解读
![[assets/crops/sglang-efficient-execution-of-structured-language-model-programs-tab02.png]]
> [!quote] caption
> Throughput comparison on multi-modal LLaVA image and video models.

> [!tip] 表格解读（多模态）
> 【图文联合解读】**Table 2 图文联合解读：**

该表对两种多模态 LLaVA 模型对比 SGLang 与作者原始实现的吞吐量：LLaVA-v1.5-7B（图像）从 0.18 → **1.15 image/s**（约 **6.4×** 加速），LLaVA-NeXT-34B（视频）从 0.02 → **0.10 frame/s**（**5×** 加速）。

结合图 2（基于 branch-solve-merge 的结构化 DSL 前端）与图 11（Compressed FSM 解码优化后端），Table 2 用作端到端效率实证：在多模态工作流中，前端编程原语与后端运行时协同优化仍带来数量级加速，证明 SGLang 的执行栈对不同模型规模与模态具备通用加速收益，而非仅限于纯文本结构化生成。

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