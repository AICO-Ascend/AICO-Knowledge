# generative_recommendation_design

> 仓 `xllm` · 路径 `docs/src/content/docs/zh/design/generative_recommendation_design.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/xllm/docs/src/content/docs/zh/design/generative_recommendation_design.md

# xLLM 生成式推荐设计文档 深度解读

---

## 【定位】

本文档系统性阐述 xLLM 在 `backend=rec` 场景下,如何围绕"长 prompt + 短输出 + 固定多轮 decode + 大候选池 beam search"的生成式推荐 workload,通过**固定调度 + 整图执行 + xAttention + beam search 系统化处理**的协同设计,实现在推荐场景下的高效推理。

---

## 【技术要点】

1. **双引擎分层接入架构**:推荐模型被切成两类子图——输入适配层(离散 ID/连续值/序列/多模态内容统一映射为 embedding)由 `predictor` 侧传统 CTR 推理承接,LLM 主体(Encoder+Decoder 或 Decoder-only)由 xLLM 承接;接入方式分 **RPC 接入**(当前营销等在线召回场景主要方式,边界清晰但有额外开销)和**动态库(.so)接入**(xLLM 作为 predictor 内部独立推理引擎,省掉 RPC 往返,适合低延迟业务)两种。

2. **固定步数调度 `fixed_steps_scheduler`**:与通用 LLM 推理的 `continuous batching` 不同,生成式推荐采用固定调度,因请求在约定好的几步内完成、多个候选需同步推进;**三大好处**——①更适合 beam search(同一请求下多个 beam 在固定窗口齐头并进,避免每步 batch 重组、sequence 压缩、索引重排);②执行形态更稳定(buffer 可提前分配、workspace 可复用、cache 访问模式更规整,便于 profiling 和容量规划);③减少与模型计算无关的损耗(sequence 重排、batch 重组、元数据更新、索引搬运等"非算子但必须付出"的成本被削减)。**代价**:新请求等待时间变长,缓解方向是引入 `multi-stream` 解耦大批固定窗口请求与小批新接入请求。

3. **整图执行 `multi_step_pipeline`**:第一步启动时一次性准备好后续若干步所需空间、索引、数据结构,让 device 侧连续向前推进,host 不必每步做 D2H 判断"H2D 准备下轮输入";收益包括减少 D2H/H2D 往返、减少 launch 和控制开销、让中间数据停留在 device 侧提高复用、把整段执行变成连续流水线;同时为定制算子创造更好的运行条件。

4. **`xAttention` KV Cache 二分存储**:将 KV Cache 拆成两类——**Shared KV**(prefill 阶段生成的 prompt KV,所有 beam 共享同一份物理存储)与 **Unshared KV**(decode 阶段每条 beam 新生成 token 的 KV,按 token 粒度管理),从根本上避免 beam 分叉与重排触发的 block copy 和显存浪费。

5. **`xAttention` 三阶段 Attention 计算**:为避免将 Shared 与 Unshared KV 拼接为逻辑长序列带来的访存与拷贝,一次 attention 被拆为——**shared stage**(仅对 Shared KV 计算局部 softmax 统计量与部分输出)→ **unshared stage**(仅对 Unshared KV 计算局部统计量与部分输出)→ **merge stage**(用 OnlineSoftmax 稳定合并两段结果);并行化层面将三阶段分配到不同执行单元和队列形成流水线,让 Shared 与 Unshared 计算尽量重叠、压缩同步点。

6. **Beam Search 系统化处理**:围绕大候选池下避免无效比较和无谓排序,核心手段包括——尽早终止不必要排序、在 item 空间约束下尽早过滤无效路径、复用已有数据结构避免每轮反复创建/销毁候选容器;强调 beam search 在生成式推荐中**不是附属成本,而是 decode 主成本的一部分**,必须与 fixed-step 调度、multi-step 执行、KV cache 组织一起系统性考虑。

---

## 【关键机制与数据】

**推理流程工作原理**:
- 一次 prefill(输入为长序列,即用户历史上下文)→ `decode_step` 次 decode(每步生成 1 个 token,最终组合为 item id)
- (原文:`decode_step` 是已知的小常数,例如 3)

**单步候选池规模**:
- (原文:例如当 `beam_width=512`、`top_k=512` 时,单步候选池大小达到 262144,约 2.6×10^5);最终从全局候选池 `beam_width × top_k` 上选择新的 beam 集合,大小仍保持为 `beam_width`

**两类核心瓶颈**:
1. **Attention 冗余带宽消耗**:所有 beam 共享同一段长 prompt,但通用实现以"每条 beam 一条完整序列"组织 KV,Shared KV 在 beam 维度被重复加载,attention kernel 有效算术强度下降,受限于 HBM 带宽。
2. **KV Cache 复制与碎片**:beam search 频繁 fork 与 retire、触发 beam 重排;基于 block 的 KV 管理(如 PagedAttention)"重排 + block 对齐"意味着 block copy、碎片化、额外空间浪费,显存和带宽均被放大。

**xAttention 解决路径**:Shared KV 在显存层面只存一份;Unshared KV 只存 decode 新增 token,避免 block copy;三阶段流水线计算避免物理拼接长序列。

---

## 【表格解读】

原文无表格。

---

## 【公式解读】

原文无公式。

---

## 【关联】

本文档涉及的多模块/特性关联如下(基于文档内文提到的引用与上下游关系):

- **上游/对接系统**:`predictor` 侧——负责稀疏特征处理、样本组织、在线服务集成;xLLM 通过 `.so` 动态库或 RPC 两种方式接入。
- **模型对象**:**OneRec**(用于召回的生成式推荐模型,论文配套图见 `figures/generative_recommendation_model_onerec.png`)与 **OneTrans**(用于精排的生成式推荐模型,图见 `figures/generative_recommendation_model_onetrans.png`)。
- **外部参考**:**Orca 论文**《Orca: A Distributed Serving System for Transformer-Based Generative Models》——作为 `continuous batching` 背景的对照,说明生成式推荐为何转向 `fixed_steps_scheduler`(原图见 `figures/fixed_steps_scheduler_orca.png`)。
- **技术对标**:**PagedAttention**——作为通用 LLM 推理的 KV Cache block 管理方案,本文档指出其"重排 + block 对齐"在 beam 分叉场景下会产生 block copy 与碎片,作为 xAttention 设计的动机(对比图见 `figures/paged_attention_comparison.png`)。
- **xLLM 内核组件**:`fixed_steps_scheduler`(调度层)、`multi_step_pipeline`(执行层)、`xAttention`(算子层,含 OnlineSoftmax merge)、`multi-stream`(并发层)——四层协同构成生成式推荐推理的完整技术栈。
- **关键图示清单**:`generative_recommendation_overview.png`(整体背景)、`generative_recommendation_beam_search.png`(beam search 作用)、`generative_recommendation_integration_architecture.jpg`(接入架构)、`xattention_kv_layout.png`(KV 布局)、`xattention_three_stage_pipeline.png`(三阶段流水线)。

---

## 【使用方法】

原文未涉及具体启用命令或配置项。文档仅以场景标识 `backend=rec` 作为生成式推荐推理的入口,并说明两种接入方式(RPC / .so 动态库)的选择依据;具体启用步骤、配置参数与命令需参考 xLLM 的部署文档及 predictor 侧接入文档。

## 图文联合解读

- `generative_recommendation_overview.png`: **图示内容**：上图(a)判别式推荐采用级联架构（召回~百万→粗排~千→精排~十几→评分列表）；下图(b)生成式推荐以用户历史序列直接输入Transformer/LLM，经Beam Search同时解码多条候选（Item D/E/F），取最高分输出。

**技术结论**：生成式推荐用单一生成模型替代多级级联管线，无需独立打分器即可端到端产出候选；Beam Search的多路并行解码验证了文档中"多候选同步比较、固定步数推进"的工作负载特征。

**与文档关系**：图(a)对应传统推荐链路，图(b)对应`backend=rec`推理链路；Self-Attention+FFN映射到xLLM的LLM主体，Beam Search多分支候选验证了"xAttention+beam search围绕显存与执行效率协同优化"的设计前提。
- `generative_recommendation_beam_search.png`: **图示内容**：以 Beam Width=5、Top-k=2 为例，展示从空序列 `[]` 经三步展开的搜索树。Time step 1 从 A-E 中选 B、C；Time step 2 由 B 路径得 AB 选 D，C 路径得 CE 选 E；Time step 3 最终输出 ABD 和 CED 两路候选（蓝圈标记每步选中节点，虚线连接跨步结果）。

**技术结论**：Beam search 每轮在固定宽度内同步扩展 Top-k 候选，3 步后产出 2 条高质量序列，体现"固定步数、多候选并行比较"的执行形态。

**与文档关系**：直观印证"固定调度+整图执行"的必要性——既然轮数和候选宽度均固定，调度层无须动态插队，可整体编译优化显存与算子，契合 xLLM 对推荐场景的工程假设。
- `generative_recommendation_model_onerec.png`: **图示解读（150字内）**

1) **画面内容**：左下 Context Processor 将用户静态/短期/长期三类特征通路分别经 Linear + RMS Norm 融合成统一 Context，并产出**全层共享的 K、V**（无 wk、wv 投影）；右侧 Lazy Decoder 堆叠 N_layer 层，每层依次为 Lazy Cross-Attention（复用 Context 的 K/V）、Causal Self-Attention 和 FFN，最终由 Output Linear Layer 预测下一个 item 的 Semantic IDs（S¹→S²→S³）。

2) **技术结论**：解码器每层省去 K/V 投影矩阵，Context 一次生成、跨层复用，大幅降低参数量与显存；decoder-only 结构高度规整，固化后非常适合整图执行。

3) **与文档关系**：呼应文档"推荐场景更适合固定调度和整图执行"——规则化的 decoder 栈与层共享 K/V 使计算图形态稳定，利于 xAttention 与 beam search 在显存与执行效率上协同优化。
- `generative_recommendation_model_onetrans.png`: **1) 图示内容**
(a) OneTrans 整体框架：S（蓝）与 NS（橙）特征分别 tokenize，用 [SEP] 拼接后送入 OneTrans 金字塔块，逐层压缩 token 数至 NS 数量，最后经 Task Tower 输出。
(b) Block 内部：causal pre-norm，含 RMSNorm、Mix Causal Attention、Mix FFN，引入 Pos Emb。
(c) 混合参数化：S token 共享 QKV/FFN 权重，每个 NS token 拥有独立权重。

**2) 技术结论**
OneTrans 以金字塔结构统一处理异构特征，高频 S token 共享权重降开销，低频 NS token 独立权重保留表达。

**3) 与文档论点关系**
图中 Mix Causal Attention / Mix FFN 即文档"定制算子"的对象，为 backend=rec 下固定调度与整图执行提供模型结构基础。
- `generative_recommendation_integration_architecture.jpg`: **1) 图示内容**：推荐系统in-predictor整体架构，自上而下分五条链路：① 接口API；② Preprocessor（item特征预处理/特征初始化/特征查询缓存/item功能引擎含增删索引）；③ Inference（推理引擎含Tensorflow/XLA/**xLLM**，后端覆盖CPU/GPU/NPU及MKL/cuDNN/CANN等算子；推荐引擎含Embedding查询适配器/LRU cache/PSS Clist/sharding&merge/特征存储；Postprocessor含Task选择与特征dump）；④ 参数查询客户端（参数Push/并行查询/LRU cache）；⑤ 基础服务组件（版本控制/ModelManager/AutoUpdateDict/OFS/brpc/JSF/jimdb/告警监控）。

**2) 技术结论**：xLLM作为推理引擎的一种后端被并列集成，Embedding检索、特征缓存、参数推送、服务治理均由predictor侧承担，LLM推理能力与推荐既有工程栈解耦复用。

**3) 与文档论点关系**：直观印证文档"保留predictor侧稀疏特征与在线服务、xLLM仅承担LLM主体推理"的分工论述。
- `fixed_steps_scheduler_orca.png`: **图解：**

1. **画面内容**：两条同输入长度的请求 x₁（"I think…"→"this/is/great"）和 x₂（"I love you"→"is/great"）经 4 轮迭代并行推进，x₁ 在 iter2 输出 `<EOS>` 提前结束，x₂ 继续推进至 iter4；"-" 表示因调度对齐产生的额外空计算。

2. **技术结论**：通用 LLM 推理在连续批处理下，即便输入长度一致，因各请求结束时刻不同，调度器必须补齐计算（padding 式空跑），造成显存与算力浪费。

3. **与文档关系**：文档指出推荐场景天然"固定步数 + 多候选同步"，正好规避了图中所述的错位提前结束问题，因此更适合固定调度与整图执行，而非通用 LLM 的连续批处理调度。
- `paged_attention_comparison.png`: **图意解读：**

1. **画面内容**：展示两个请求（A、B）的 KV cache 显存布局，标注三类浪费——预留槽位（reserved，如"fathers"、"only"前后各留空槽）、内部碎片（internal fragmentation，如 2038/507 个未用槽）、外部碎片（external fragmentation，请求间灰色空块）。

2. **技术结论**：现有系统的 KV cache 按**固定块大小预分配**显存，导致三类浪费叠加，使显存利用率低下，阻碍新请求调度。

3. **与文档关系**：该图论证生成式推荐中 beam search 多候选并行推进时，**显存效率是关键瓶颈**，为文档后续引入 xAttention 通过固定调度+整图执行来压缩 KV cache、提升多 beam 并发能力提供问题动机。
- `xattention_kv_layout.png`: **图文联合解读：**

1）**画面内容**：图2展示KV Cache拆分机制。左上"Shared Cache"存储beam间共享的公共前缀token（如o,a,e,k,f等）；右上"Unshared Cache"在TID₀→TID₁→TID₂三轮decode中逐步累积各beam私有token（数值1–7）。下方树状图描绘prefill后从根节点分叉出a/b/c/d候选，每轮向右扩展，红色节点为最终保留的高分beam。

2）**技术结论**：beam search中前缀token的KV可被多条候选复用，仅差分部分需独立存储；通过Shared/Unshared分离可显著降低冗余显存占用，同时保留各beam独立decode的能力。

3）**与文档关联**：呼应文档"xAttention与beam search围绕显存和执行效率协同优化"——Shared KV降低多候选显存放大，Unshared KV支撑固定步数推进与多候选同步比较，是"有限几轮内稳定扩展候选"这一设计目标的工程落地。
- `xattention_three_stage_pipeline.png`: **1) 图内容**：四个计算组 CG₀–CG₃ 按三阶段分层——Shared Stage（CG₀、CG₁，复用注意力统计）、Unshared Stage（CG₂，独立统计）、Merging Stage（CG₃，用 OnlineSoftmax 替代标准 Softmax 并做 Post-processing 合并），每组由 MCU（BatchMatmul）和 VCU（Softmax/OnlineSoftmax）组成。

**2) 技术结论**：Shared 与 Unshared 段可并行独立统计部分 softmax 分母与最大值，Merging 阶段通过 OnlineSoftmax 流式合并，避免全量重算和显存冗余。

**3) 与文档关系**：对应文档"xAttention 围绕显存与执行效率协同优化"论点，体现生成式推荐在固定步数、整图执行形态下，通过分段+流式合并降低 attention 中间状态开销。
