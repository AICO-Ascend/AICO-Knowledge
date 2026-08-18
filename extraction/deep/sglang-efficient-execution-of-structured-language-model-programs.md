# SGLang: Efficient Execution of Structured Language Model Programs — 技术点深读（DEEP 2026-08-18）

> 独立文件：全要素深读笔记（文本 + 图表 + 公式 + 表格交织分析），保留跨论文 wikilinks 与 MOC 谱系定位。extract_phase1 重跑不丢。
> 论文：SGLang: Efficient Execution of Structured Language Model Programs · arXiv:2312.07104v2 (6 Jun 2024) · Stanford / UC Berkeley / SJTU

## 核心问题

LLM 应用正从"单轮聊天"转向"程序化多调用"——即 LM Programs：多次 generation call 交织控制流，并消费/产出结构化输入输出（§1）。这类工作负载（agent control、tree-of-thought、self-consistency、JSON mode、multi-turn chat、RAG pipeline）有两个本质属性：(1) 含多次相互依赖的 LLM 调用；(2) 需结构化输入输出以利组合（§1）。

现有系统两重低效：
- **编程侧**：手写字符串操纵、脆弱输出解析、手工并行控制——等价 OpenAI API 程序需 2.1× 行数（§2 running example）。
- **执行侧**：vLLM/TGI/TensorRT-LLM 按"单请求"优化、不感知多调用结构——KV cache 用完即弃（重复 prefill）、约束解码逐 token、共享前缀无法系统复用（§1, §3）。

**核心思路**（Figure 1, p.2）：系统化利用 LM Program 的多调用结构做前后端协同优化——前端 DSL 简化编程 + 后端 SGLang Runtime (SRT) 三项创新（RadixAttention / Compressed FSM / API Speculative Execution）加速执行。M3 解读 Fig.1：Python 嵌入式前端把原语 extend/gen/select/fork/join 提交为异步流，runtime 据依赖调度、批独立操作重叠执行藏延迟；RadixAttention 用 LRU 基数树缓存 KV 跨请求自动复用。前后端可独立工作，但协同（frontend hint）带来额外收益。

## 关键创新点

### 1. RadixAttention（核心，§3）——把 KV cache 当 radix tree LRU cache

- **机制**：请求的 KV cache 不再用完即弃，按 token 序列存入 radix tree 边；新请求先 prefix-match 复用已有 KV，未命中段追加为新节点。KV 张量存于**非连续、分页布局**（page = 1 token），与 PagedAttention 兼容。树存于 CPU，维护开销线性且小。节点带引用计数，运行批次在用的不驱逐；**驱逐策略 = 优先赶 LRU 叶子**（叶子被赶后祖先变叶子再赶），使公共前缀尽可能久存活（§3）。
- **共享内存池**：不预分配固定 cache 池，缓存与运行请求**共享同一内存池**——队列积压时宁可赶光缓存换更大 batch size（§3, Alg.1）。
- **四级共享模式**（Figure 9, p.14，M3 解读）：few-shot examples 跨 prompt 完全相同（蓝）；self-consistency 同 prompt 多采样；multi-turn chat 累积历史；tree-of-thought 树状分支共享 search history。M3 明确指出：现有系统（vLLM 仅 basic prefix sharing）无法全部自动处理，RadixAttention 在运行时统一覆盖这四类不规则 sharing pattern。
- **9 时间点演化**（Figure 3, p.5，M3）：节点颜色编码 绿=新加 / 蓝=命中 / 红=驱逐。step(1) 空树→(2) "Hello/Hi" 合并单边→(3) 新轮复用前缀→(4) 节点分裂共享系统提示→(5) 内存压力驱逐节点 c→(6) few-shot 查询根分裂→(7) 批量 few-shot 分裂共享→(8) 第二会话消息驱逐 g/h→(9) self-consistency 采样驱逐 i/k/l。直观演示动态树形共享 + LRU，正是线性 prefix 系统无法处理的场景。
- **cache-aware 调度**：等待队列按"已匹配前缀长度"排序（longest-shared-prefix-first ≡ DFS 序）。**Theorem 3.1**（§3, 证明见 A.3）：设 C 为该批请求的总 prefill 计算量，则任意调度的下界为

$$
C \geq \sum_{e \in \text{edges}(T)} |e|.
$$

当 cache size ≥ 最长请求长度（即 radix tree 最长路径）时，DFS 序恰使每条边 KV 恰计算一次，达到该下界：

$$
C = \sum_{e \in \text{edges}(T)} |e|.
$$

其中 T 为请求的 radix tree，edges(T) 为其边集，|e| 为边 e 对应 token 序列长度（formulas.json LaTeX 权威源；fulltext §A.3 line 1169-1185 逐字一致；M3 caption p14 双源校验——M3 明确"cache size ≥ 最大请求长度时 DFS / longest-shared-prefix-first 序遍历 radix tree 可获最优 cache 命中率"，与 LaTeX 下界结论一致）。在线情形 DFS 序被新到请求扰动，但 longest-prefix 序仍近似 augmented radix tree 上的 DFS（A.3 归纳证明）。

- **cache 命中率定义**：batch R 中已命中（复用）的 prefill token 数占总 prefill token 数之比（formulas.json LaTeX 权威源；fulltext §A.3 line 1188-1196 逐字一致）：

$$
\frac{\sum_{r\in R}\text{number of cached prefill tokens in } r}{\sum_{r\in R}\text{number of prefill tokens in } r}.
$$

Theorem 3.1 的最优性即指上式取上界——DFS 序下 C 达下界 ⇒ 全部 prefill token 均被缓存复用 ⇒ 命中率趋于 1。
- **Frontend Hint**：fork 时 interpreter 先发前缀作 hint，runtime 提前插树、简化调度匹配——前后端协同设计的实例（§3）。
- **效果**：cache 命中率 50%–99%（§6.2，Figure 13 p.19）；cache-aware 调度达**最优命中率 96% 均值**（§6.2）。Figure 13 (M3) 显示 MMLU/ReAct/ToT/SoT/HellaSwag/JSON/DSPy RAG 实际命中率逼近最优（差<5%），短板在 Multi-Turn Chat（short ~50% vs 最优 ~60%、long ~55% vs ~75%，约 20% 空间）。无命中场景开销 <0.3%（ShareGPT 100 请求 74.3s，树管理仅 0.2s，§6.3）→ 可默认开启。生产部署 Chatbot Arena：Vicuna-33B 命中 74.1%、首 token 延迟均降 1.7×；LLaVA-NeXT-34B 命中 52.4%（§6.2）。
- **分布式扩展**：tensor parallelism 每 GPU 维护分片 KV，树操作相同无需额外同步；data parallelism 由 router 维护 meta-tree 跟踪各 worker 子树，按 affinity（共享前缀长度）派发，弱一致性设计，4 worker 线性扩展（A.4）。

### 2. Compressed FSM（§4 + Appendix B）——约束解码多 token 一次前向

- **背景**（Figure 10, p.17，M3）：正则→字符级 FSM；解码时维护 FSM 状态、取下一状态合法字符集、对 token 词表求交集生成 logits mask（交集内保留、外置 −∞）。M3 用 Harry Potter JSON 示例：状态 0→1→2→3→4→5→6→7 线性骨架对应 `"age": "`，状态 6 带 [0-9] 自环。两轮快照：生成 `{"name":"Harry",` 后合法下一 token 为 `age ✓`（`Age ✗` 大小写被拒、`hou ✗` 结构不闭合）；生成 `...,"age":` 后合法为 `0/1 ✓`（`fir ✗`）。
- **机制**（B.1）：定义 **singular transition edge**（源节点唯一后继 + 唯一可接受字符）与 **compressed edge**（递归合并连续 singular 边，文本拼接）。从字符级 FSM 递归压缩直至不可压。
- **Figure 4 对比**（p.6，M3）：(a) Normal FSM 对 `{"summary":_` 有 14 个状态、每边单字符；(b) Compressed FSM 仅 2 状态、整串压成单边；(c) Normal 解码需 4 次 LLM 前向（`{"`→`summary`→`"`→`:`→`_` 每步一次）；(d) Compressed 仅 1 次 LLM 前向，确定性段直接放行、仅歧义处调模型。**这是与 Guidance/Outlines 等 logits-mask 逐 token 解码的本质区别**——后者即使 FSM 完全确定仍触发完整 Transformer 前向。
- **Jump Forward + Retokenization**（B.2, Figure 11 p.18，M3）：compressed 边很长时预读后续解码串一次性注入输出流，仅对真正自由 token（如 `Harry`/`15`/`Gryffindor`）调模型。Figure 11 (M3) 直观对比：Compressed FSM 上半部为绿色 Prefill + 大块橙色 Jump-Forward + 少量蓝色 Decode；Normal FSM 下半部全为密集蓝色逐 token Decode；右侧 Generated JSON 完全一致——语义不变。tokenization 错位（如 `summary` 不能被切成 `summa`+`ry`）靠原 tokenizer retokenize 对齐，开销小。
- **效果**（§6.3）：JSON 解码吞吐 **×1.6**；FSM 预处理必须跨请求复用，否则 per-request 重做反而**慢 ×2.4**。

### 3. API Speculative Execution（§5）——黑盒 API 模型多调用优化

第一次 `gen` 忽略 stop 条件多生成几 token，interpreter 保留输出并与后续 primitive 匹配复用，省一次 API 调用的延迟 + 输入 token 费用。示例：`context + "name:" + gen("name", stop="\n") + "job:" + gen("job", stop="\n")` 原本两次 API 调用（context 输入费付两次），开 speculative 后一次调用即可。GPT-3.5 抽三字段 few-shot prompting 下精度高，**输入 token 费约降 3×**（§6.2）。

### 4. 前端-后端协同设计（§2 + §6.3 ablation）

interpreter 把 prompt 当异步流提交原语（extend/gen/select/fork/join），非阻塞调用允许 Python 继续（类比异步 CUDA kernel），每 prompt 由后台线程的 stream executor 管理实现 intra-program 并行；取结果时阻塞同步。**frontend hint**（fork 先发前缀提示）与**frontend parallelism** 在 Figure 8(c) ablation 中均被证明必需——关掉任一都掉性能，印证前后端协同设计的价值。

### 5. Compiler Mode（Appendix D）

SGLang 程序可 trace 成计算图 IR，节点类型 ConstantText/Argument/Gen/Select/Variable/Fork/GetForkItem/Join，两类依赖：intra-stream（流内 `+=` 顺序）与 inter-stream（跨流取值同步）。图执行器消除重解释、支持图重写。Figure 14 (p.20, M3)：Skeleton-of-Thought 程序编译为 3 条 stream（主函数 + 两次 expand），Stream 2/3 结构对称且无依赖→可并行，二者 prompt 模板一致仅 tip 变量不同→构成 KV cache 共享机会。

**Case study: Code Movement**（D.2）：用 GPT-4 重排图节点把常量挪到前缀以增共享前缀（把 LLM 当编译器优化器）。20 模板，5 训练 + 15 测试，**15 中 12 成功**，平均**增 60 token 共享前缀**；失败因 GPT-4 过度激进将所有常量前置破坏语义。局限：tracing 不支持数据依赖控制流。

## 表格

### Table 1（§2, p.4）：LMQL / Guidance / SGLang 对比
| 系统 | 语法 | 语言原语 | Runtime 后端 |
|---|---|---|---|
| LMQL | 自定义 | extend, gen, select | HF Transformers, llama.cpp, OpenAI |
| Guidance | Python | extend, gen, select, image | HF Transformers, llama.cpp, OpenAI |
| **SGLang** | Python | extend, gen, select, image, video, **fork, join** | **SGLang Runtime (SRT)**, OpenAI |

SGLang 原语最全（独有 fork/join/video），是唯一带自研 runtime 的低层系统；高层语言（DSPy）可编译到 SGLang 获运行时收益（§2, §6 已验证）。

### Table 2（§6.2, p.8）：多模态 LLaVA 吞吐
| 模型 | 作者原实现 | SGLang | 加速 |
|---|---|---|---|
| LLaVA-v1.5-7B (image) | 0.18 image/s | **1.15 image/s** | ~6.4× |
| LLaVA-NeXT-34B (video) | 0.02 frame/s | **0.10 frame/s** | ~5× |

多模态 KV 复用：对输入图像算 hash 作 radix tree key，同图多问复用 image token KV（§6.2）。baseline 用作者原 HF 实现（其他系统不支持好），客观比较受限。

### Figure 5/6/7/12 端到端结果（归一化，SGLang=1.0）
- Figure 5 (p.7, M3)：Llama-7B 吞吐，4 系统对比 11 workload。MMLU vLLM≈0.15/Guidance≈0.10；Generative Agents vLLM≈0.9；Multi-Turn Chat(long) vLLM≈0.97（最接近）；ToT/SoT/LLM Judge/HellaSwag/JSON 上 Guidance/LMQL 几乎为 0。负载越"程序化"领先越显著。
- Figure 6 (p.8, M3)：Llama-7B 归一化延迟（lower better），SGLang 前 8 项显著低于三基线；后 3 项 vLLM 接近。
- Figure 7 (p.8, M3)：Mixtral-8x7B + TP，仅 SGLang vs vLLM，HellaSwag/JSON/DSPy RAG 上 vLLM 接近 0。
- Figure 12 (p.19, M3)：Llama-2-70B + TP，SGLang 全面显著优于 vLLM，ReAct/MMLU/JSON/Multi-Turn(long) 差距悬殊。
- **总览**（§6.2）：吞吐最高 **6.4×**，延迟最低 **3.7×**。加速来源：KV cache 复用 + 单程序内并行 + 压缩 FSM。

### Figure 8 ablation（§6.3, p.9, M3）
- (a) cache hit rate ↑ → batch size 20→40+、throughput 0.4k→1.2k tokens/s。
- (b) cache hit rate ↑ → total latency ~400→~100s、first token latency ~20→~10s。
- (c) RadixAttention 组件消融（4 基准 LLM Judge/ToT/MMLU/Multi-Turn short, 7 配置）：No Cache / No Tree Structure / FCFS Schedule / Random Schedule / No Frontend Parallelism / No Frontend Hint / Full Optimization。**每个组件都必需**——Full Optimization 在所有基准近 1.0，No Cache 几乎贴 0；禁用并行/hint 也掉性能，印证前后端协同。

### Figure 13（§6.2, p.19, M3）：achieved vs optimal cache hit rate
MMLU/ReAct/ToT/SoT/HellaSwag/JSON/DSPy RAG 实际逼近最优（<5%）；LLM Judge 几乎 100% 达最优；Multi-Turn Chat(short/long) 差距约 20%——长前缀拼接/上下文碎片化是未来方向。

### 超参/实验设置（§6.1）
- 模型：Llama-2 7B/70B、Mixtral-8x7B、LLaVA-v1.5-7B (image)、LLaVA-NeXT-34B (video)、GPT-3.5；float16；7B–70B 参数。
- 硬件：AWS G5 (A10G 24GB)，7B 单卡，70B 4×A100G(80GB) TP；Mixtral 8×A10G TP。
- Baseline 版本：Guidance v0.1.8 (llama.cpp)、vLLM v0.2.5（注：RadixAttention 后被部分集成进 vLLM 为实验特性，故对比用更早版本）、LMQL v0.7.3 (HF Transformers)。
- Workloads：5-shot MMLU、20-shot HellaSwag、ReAct/generative agents (trace replay)、ToT (GSM-8K)、SoT (tip gen)、LLM Judge (branch-solve-merge)、JSON decoding (regex schema)、Multi-turn chat 4 轮 (输入 256-512 token；short 输出 4-8 token / long 256-512)、DSPy RAG。
- 实现：PyTorch + FlashInfer CUDA kernels + Triton。

## 与同类对比

- **vs vLLM/Guidance/LMQL**（Table 1, Figure 5-7/12）：SGLang 原语最全（独有 fork/join/video），自带 runtime；端到端吞吐最高 **6.4×**、延迟最低 3.7×。LMQL 慢在 token 级处理 + 未优化后端；Guidance 缺批处理/并行——故后五项基准被排除。
- **vs vLLM PagedAttention**：vLLM 分页 KV 是奠基，但只做 basic prefix sharing（如系统提示），无多级树结构 + LRU + cache-aware 调度；RadixAttention 把"简单系统提示共享"升级为"多级树结构 LRU 自动复用 + 四级 sharing pattern 全覆盖"。
- **vs PromptCache**：PromptCache 模块化复用非前缀 KV，但精度可掉 **43%**；RadixAttention 严格前缀复用，精度无损。
- **vs ChunkedAttention / HydraGen / FlashInfer**：聚焦 CUDA kernel 优化，无 LRU cache 概念；正交可叠加。
- **vs API Serve / LLM-SQL**：研究特定应用（API 交错、关系数据库）的 KV 复用，无 radix tree 或 cache-aware 调度。

## 跨论文关系（→ MOC 谱系, wikilinks [[slug]]）

- **继承/改进 vLLM PagedAttention**：[[vllm-efficient-memory-management-for-large-language-model-serving]] 分页 KV 是奠基，SGLang RadixAttention 升级为多级树结构 LRU 自动复用 + cache-aware DFS 调度 + 前后端协同 hint。vLLM 后续将 RadixAttention 部分集成为实验特性（脚注 3）。
- **互补 Sarathi / Sarathi-Serve**：SGLang 做"多调用间前缀复用"，Sarathi 做"prefill-decode 混合调度"——正交可叠加。
- **互补 Mooncake**：SGLang 是同机多调用复用，[[mooncake]] 是跨节点 disagg + 分层 KV 迁移（GPU/CPU/DRAM/SSD）；SGLang future direction 明确提到扩展到多级内存层次（DRAM/Disk）。
- **互补 Preble**：[[preble-efficient-distributed-prompt-scheduling-for-llm-serving]] 基于 SGLang 早期版本研究 data-parallel 调度（A.4 提及 concurrent work）。
- **互补 IndexCache / 层间索引复用**：正交于 SGLang 前缀复用。
- **演进 Prefill-as-a-Service**：Mooncake 跨节点思想进一步跨数据中心规模化。
- **编程系统谱系**：高层（LangChain/DSPy）可编译到低层（SGLang）；论文已验证 DSPy 以 SGLang 为 backend 获运行时收益。

## 局限与边界

- **cache-aware 贪心调度可能饥饿**：未集成公平调度，列为 future（§3, §8）。Figure 13 显示 Multi-Turn Chat 短/长输出命中率与最优差约 20%，长前缀拼接/上下文碎片化是真实痛点。
- **长输出场景几乎无加速**：解码时间主导、会话间共享少，Multi-Turn Chat(long) 上 vLLM 已逼近 SGLang（Figure 5, §6.2）。
- **Compressed FSM 概率扭曲**（B.3）：broad 选项（如 `Excellent|Above Average|Fair|Below Average`）映射可能错位（A 误映到 Above Average），因 LLM 不识别选项全集；需逐选项求所有等价 token 序列概率和，开销大。workaround 是把 choices/regex 放进 prefill 提示，但未根治。
- **Compiler mode 不支持数据依赖控制流**：tracing 法受限，列为 future（D.1）。
- **多模态 baseline 客观性受限**：用作者原 HF 实现（其他系统不支持好），非完全同等条件对比（§6.2）。
- **Theorem 3.1 最优性前提**：要求 cache size ≥ 最长请求长度，且实际输出 token 数不可预测会导致 KV 重算（脚注 2），故实践中并非严格达到下界。
- **Code Movement 激进优化不保语义**：GPT-4 重排 15 中 3 失败（过度前置常量破坏语义），可靠性待提升（D.2）。
