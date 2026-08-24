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
> 【图文联合解读】**图文联合解读**

图示SGLang三层架构：**前端**(SGLang Client，含Sec.2语言原语extend/gen/fork) → **Interpreter**(黄色调度器) → **后端Runtime**(蓝色，集成Sec.3 RadixAttention、Sec.4 压缩FSM、Sec.5 API推测执行)。

该图论证的核心结论：以**嵌入式DSL前端+流式Interpreter+优化Runtime**的分层设计，将原语依赖解析、KV缓存复用、状态机压缩统一抽象；Interpreter记录数据依赖使独立原语并行批执行，前缀自动命中RadixAttention。

作为论文方法链路总纲图(Fig.1)，它在Sec.1结尾铺垫后三章技术细节(§2原语→§3缓存→§4 FSM→§5推测)，并支撑§6实验：在HumanEval/MTBench等基准上较vLLM/Guidance/LMQL实现最高6.4×加速。

### Figure 2 (p.3) ⭐深度解读
![[assets/crops/sglang-efficient-execution-of-structured-language-model-programs-fig02.png]]
*整页渲染: ![[assets/sglang-efficient-execution-of-structured-language-model-programs-p03.png]]*
> [!quote] caption
> The implementation of a multi-dimensional essay judge in SGLang utilizes the branch-solve-merge prompting technique [40]. Primitives provided by SGLang are shown in red. 2

> [!tip] 技术解读（多模态）
> 【图文联合解读】# Figure 2 图文联合解读

**1) 核心对象与结构**

该图为代码注释图，展示 SGLang 中多维作文评判器（multi-dimensional essay judge）的完整实现，调用 `gen`、`select`、`fork` 等原语（红色高亮），由右侧黄色箭头逐行标注功能：
- **入口**：`run` 函数——运行 SGLang 程序，支持 chat 模板与多模态输入；
- **分支（branch）**：`fork()` 并行触发多个 `gen` 调用，按"dimension"逐项评判；
- **求解（solve）**：单维度调用采用 **KV Cache Reuse**（Sec. 3）复用前文 prompt；用 `select` 从候选选项中选最高概率答案；
- **合并（merge）**：汇总各维度 JSON 结果，并采用 **快速约束解码**（Sec. 4，正则 `[ABCD][+-]?\s`）与 **API 投机执行**（Sec. 5）输出最终字母等级与摘要。

**2) 关键论证结论**

图示证明：仅用 7 个原语即可将论文 [40] 的 branch-solve-merge 提示范式实现为高效程序，且 SGLang 的三类运行时优化（KV cache 复用、约束解码、投机执行）可无缝嵌入。

**3) 在论文链路中的作用**

该图作为"方法示例"，承上（Sec. 2 编程模型）启下（Sec. 3–5 各项优化），直观体现 SGLang 用高层原语 + 自动优化替代手工工程，是后续性能基准（Figure 3）与消融实验的应用载体。

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
> 【图文联合解读】**图(a)**：Normal FSM为regex `{"summary":_`构建**12状态(0-11)**线性结构，每个状态对应单个字符`{ " s u m m a r y " : _`；**(c)**：解码过程显示FSM校验与LLM前向频繁交替——每token（`{"`、`summary`、`":`、`_`）均触发**独立LLM调用**，调度粒度过细。

**关键结论**：原文借助Normal FSM对照Compressed FSM论证——后者通过合并具有相同未来转移的等价状态节点，把逐字符校验压缩为多 token批量匹配，从而**单次LLM解码可同时校验多字符**，显著降低调度与前向开销。

**作用**：作为第3节"压缩FSM等价性"(Theorem 3.1)的可视化证据，与算法1的cache-aware调度共同构成"问题刻画→压缩优化→延迟基准"方法链路中的核心论据，支撑sglang高效结构化生成的性能优势。

### Figure 5 (p.7) ⭐深度解读
![[assets/crops/sglang-efficient-execution-of-structured-language-model-programs-fig05.png]]
*整页渲染: ![[assets/sglang-efficient-execution-of-structured-language-model-programs-p07.png]]*
> [!quote] caption
> Normalized throughput on Llama-7B models. Higher is better. pattern: s += context + "name:" + gen("name", stop="\n") + "job:" + gen("job", stop="\n"). Naively, the two gen primitives correspond to two API calls, meaning that the user needs to pay for the input token fee on the context twice. In SGLang, we can enable speculative execution on the first call and let it continue the generation of a fe

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

1) 图为 Llama-7B 上 6 个结构化生成任务（LLM Judge、HellaSwag、JSON Decoding、Multi-Turn Chat 短/长、DSPy RAG）的归一化吞吐条形对比。橙色条（SGLang）在全部任务上柱高均显著领先蓝色（Guidance）与绿色（LMQL）基线；LLM Judge 与 DSPy RAG 上领先幅度最大（近 4–5 倍），Multi-Turn Chat(long) 上三者差距最小。

2) 原文以此论证：含两次 `gen` 的 pattern 中，朴素做法需对同一 `context` 重复支付输入 token 费用；而 SGLang 借助推测执行复用首次调用的 prefix 并继续生成，从而在跨任务场景下稳定获得高吞吐增益。

3) 该图是论文核心实验证据，将运行时优化（推测执行、前缀共享/RadixAttention）与真实结构化 LM 程序效率挂钩，支撑"DSL 前端 + 高效执行后端"整套方法的有效性结论。

### Figure 6 (p.8) ⭐深度解读
![[assets/crops/sglang-efficient-execution-of-structured-language-model-programs-fig06.png]]
*整页渲染: ![[assets/sglang-efficient-execution-of-structured-language-model-programs-p08.png]]*
> [!quote] caption
> Normalized latency on Llama-7B models. Lower is better. MMLU

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

1）**核心对象与结构**：横轴为 6 个 Llama-7B 工作负载（LM Judge、HellaSwag、JSON Decoding、Multi-Turn Chat 短/长、DSPy Pipeline RAG），纵轴为归一化延迟。橙色（SGLang）、蓝色（Guidance）、灰色（LMQL）、绿色（另一基线）四组柱状对比，前两项三项齐全，后四项 Guidance/LMQL 因不支持批处理与并行而被剔除。

2）**关键结论**：在 LM Judge 与 HellaSwag 上，LMQL 延迟达 SGLang 的约 2.5–3 倍；Multi-Turn Chat（短/长）与 DSPy Pipeline 上，绿色基线延迟也明显高于 SGLang。SGLang 在全部 6 项基准中延迟最低。

3）**论文作用**：该图作为性能收尾证据，配合 Figure 7（Mixtral-8x7B）证明 SGLang 的 RadixAttention 与前端优化在分类、Agent、CoT、结构化输出、多轮对话、RAG 等典型结构化 LLM 程序场景下均具备跨负载、跨模型规模的稳定加速优势。

### Figure 7 (p.8) ⭐深度解读
![[assets/crops/sglang-efficient-execution-of-structured-language-model-programs-fig07.png]]
*整页渲染: ![[assets/sglang-efficient-execution-of-structured-language-model-programs-p08.png]]*
> [!quote] caption
> Normalized throughput on Mixtral-8x7B models with tensor parallelism. Higher is better. result from KV cache reuse, the exploitation of parallelism within a single program, and faster constrained decoding. Next, we explain the reasons for the speedup in each benchmark.

> [!tip] 技术解读（多模态）
> 【图文联合解读】该图展示 Mixtral-8x7B 启用张量并行后，SGLang 在 5 类基准（MMLU、ReAct Agents、Generative Agents、Tree of Thought、Skeleton of Thought）上的归一化吞吐：SGLang 均归一为 1.0；对手在 MMLU≈0.12、ReAct Agents≈0.10 落后最显著，Tree of Thought≈0.25 差距明显，Generative Agents 与 Skeleton of Thought≈0.72 差距最小。

原文借此论证：SGLang 的前端优化与运行时协同在 MoE + 张量并行场景下仍稳定胜出，优势在含控制流、多轮交互的 Agent 与 CoT 负载上尤为突出。

作用：补充 Figure 6（Llama-7B），证明吞吐优势可跨模型规模与并行策略复现，强化方法在大模型场景下的通用性结论。

### Figure 8 (p.9) ⭐深度解读
![[assets/crops/sglang-efficient-execution-of-structured-language-model-programs-fig08.png]]
*整页渲染: ![[assets/sglang-efficient-execution-of-structured-language-model-programs-p09.png]]*
> [!quote] caption
> (a)(b) Cache hit rate ablation study. (c) RadixAttention ablation study.

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图文联合解读：**

图8(c)为RadixAttention消融实验的柱状图，横轴为四个基准负载（LLM Judge、Tree of Thought、MMLU、Multi-Turn Chat短对话），纵轴为归一化性能（0–1），对比七种配置：无缓存、无树结构、FCFS调度、随机调度、无前端并行、无前端提示、全优化（Full Optimization，橙色）。

**关键结论**：全优化方案在四个负载上均接近1.0归一化值，显著优于任一单一组件关闭情形；其中"无缓存"在LLM Judge与MMLU上退化最严重（约0.15–0.40），"无前端并行/提示"在Tree of Thought上影响明显（约0.35），证实radix缓存、树状调度、前端并行与提示各自独立贡献性能。

**论文作用**：该消融图支撑SGLang核心设计——RadixAttention缓存+前端DSL优化是端到端加速的必要组成部分，缺一不可，为整体性能优势提供分项归因证据。

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
> 【图文联合解读】**图文联合解读：**

图上部分给出一个 JSON 结构化正则（含 `name:[\w\d\s]+`、`age:[0-9]+`、`house` 为 Gryffindor/Slytherin/Ravenclaw/Hufflepuff 四选一枚举）；下部分"Decoding Status"列出对"填 Harry Potter 信息"提示符的候选下一 token：仅小写 "age" ✓ 被接受，而 "Age" 因大小写不符被 ✗、"hou" 因当前路径无法延伸到合法 token 被 ✗；箭头 "Decode + FSM" 指向右侧 "Constrained Decoding" 输出。

**技术结论：** 原文借此论证——regex 经自动编译为 FSM 后，在每一步解码通过对 logit 施加掩码屏蔽与模式不符的 token，使生成结果严格匹配 JSON 字段名、字符集与枚举约束，无需后处理重解析。

**链路作用：** 该图位于"regex→FSM→约束解码"方法链路可视化末端，为后续 JSON/HTML/SQL 等结构化输出基准的正确性与吞吐实验提供直观原理支撑，强调 FSM 路径相对逐 token 语法校验的效率优势。

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

该图为 Llama-2-70B + TP 配置下 SGLang（橙色，归一化为 1.0）与另一基线系统（绿色，图例被裁切）于 5 种典型 LLM 程序上的吞吐对比。绿色条读数大致为：MMLU≈0.12、ReAct Agents≈0.10、Generative Agents≈0.60、Tree of Thought≈0.30、Skeleton-of-Thought≈0.80，呈现"简单 prompt 差距悬殊、复杂多调用场景差距收窄"的梯度。

原文借此论证：在张量并行的大模型上，SGLang 的 RadixAttention 与 API 级批调度对含多轮/分支调用的结构化生成（Agents、ToT、SoT）带来 1.2×–10× 的吞吐加速，证实其前端语言模型程序与后端 KV 缓存协同设计的端到端效率优势，构成实验链路中"真实工作负载可扩展性"的关键证据。

### Figure 13 (p.19) ⭐深度解读
![[assets/crops/sglang-efficient-execution-of-structured-language-model-programs-fig13.png]]
*整页渲染: ![[assets/sglang-efficient-execution-of-structured-language-model-programs-p19.png]]*
> [!quote] caption
> Achieved cache hit rate and optimal cache hit rate on various benchmarks. opportunities for more compilation optimizations, as we can rewrite the graph and perform more static planning. D.1

> [!tip] 技术解读（多模态）
> 【图文联合解读】**图13联合解读**

图13以并列条形图对比"SGLang"（橙）与"Optimal cache hit rate"（浅蓝）在6个基准上的命中率——LLM Judge、HellaSwag、JSON Decoding、Multi-Turn Chat (short/long)、DSPy RAG Pipeline。除Multi-Turn Chat两类外，SGLang柱高均接近甚至贴合Optimal柱；Multi-Turn Chat (short) 与 (long) 出现明显落差。论文借此论证：SGLang的缓存复用已接近理论最优，但多轮对话场景仍有提升空间，由此引出附录D.1中"重写计算图与更多静态规划"这一未来优化方向。

### Figure 14 (p.20) ⭐深度解读
![[assets/crops/sglang-efficient-execution-of-structured-language-model-programs-fig14.png]]
*整页渲染: ![[assets/sglang-efficient-execution-of-structured-language-model-programs-p20.png]]*
> [!quote] caption
> An SGLang program and its corresponding dataflow graph.

> [!tip] 技术解读（多模态）
> 【图文联合解读】## Figure 14(b) 图文联合解读

**1) 核心结构与数据：**
图中展示一个计算图，按列分为三条 Stream（对应三次函数调用）。Stream 1 主链含 18 个节点（ConstantText×10、Argument×1、Gen×3、Variable×2）；Stream 2 与 Stream 3 各含 4 个节点。跨流边将 Stream 1 中 Gen("tip_1") 的输出分别送入 Stream 2、3 的 Variable("tip_1") 节点；Gen("tip_2") 输出则同时被 Stream 2 的 Variable("paragraph") 引用，呈现典型的 fan-out 数据依赖。

**2) 关键技术结论：**
通过把 SGLang DSL 程序编译成显式数据流图，可揭示 Stream 1 内 Gen("tip_1") 与 Gen("tip_2") 之间、乃至三条 Stream 之间的并行机会——LM 生成调用可被调度器批量/乱序执行，而非受源代码顺序约束。

**3) 在论文中的作用：**
该图作为 runtime scheduler 的**动机示例**，论证 SGLang 将命令式 LLM 程序提升为数据流图后，能够自动发现并利用生成调用间的并行性，从而支撑论文核心主张——结构化语言模型程序的高效执行。

## 表格（裁剪图 + caption，可直接插入报告）

### Table 2 (p.9) ⭐深度解读
![[assets/crops/sglang-efficient-execution-of-structured-language-model-programs-tab02.png]]
> [!quote] caption
> Throughput comparison on multi-modal LLaVA image and video models.

> [!tip] 表格解读（多模态）
> 【图文联合解读】Table 2：SGLang使LLaVA-v1.5-7B图像吞吐从0.18→1.15 image/s（约6.4×），LLaVA-NeXT-34B视频从0.02→0.10 frame/s（5×）。子图(a)(b)显示缓存命中率上升带来batch size与吞吐增长、首token延迟与总延迟同步下降；子图(c)消融表明Full Optimization在LLM Judge、ToT、MMLU、Chat四项任务归一化吞吐均≈1，缺任一原语（无缓存、无树结构、无FCFS、无前端并行、无前端提示）均显著退化。

论证：RadixAttention、前端并行与调度协同在多模态场景同样实现数量级加速，将SGLang效率优势从纯语言模型推广至多模态LM程序，强化论文"结构化LM程序普适高效"的核心结论。

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