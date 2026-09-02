# generative_recommendation_design

> 仓 `xllm` · 路径 `docs/src/content/docs/en/design/generative_recommendation_design.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/xllm/docs/src/content/docs/en/design/generative_recommendation_design.md

# xLLM「Generative Recommendation Design Document」一体化深度解读

> ⚠️ **重要说明**: 本次解析的原文在 §2.2.1 "RPC Integration" 一段末尾被截断(原句停留在 "while the downs"), 因此下文涉及 §2.2.2 shared library 集成、固定调度 / whole-graph multi-step 执行细节、`xAttention` 与 beam search 协同机制、以及代码位置 (rec 相关代码在仓库中的位置) 等小节的描述, 仅能基于已给出的内容做解读, 不会臆造原文缺失的部分。

---

## 【定位】

这篇文档系统阐述 xLLM 如何通过 `backend=rec` 路径为「LLM 驱动的生成式推荐 (Generative Recommendation, GR)」提供推理能力, 并解释为何该路径在控制层采用 **fixed scheduling**、在执行层采用 **whole-graph multi-step execution**, 以及围绕 `xAttention` 与 `beam search` 进行协同优化, 同时澄清 xLLM 与传统推荐 `predictor` 之间的职责边界。

---

## 【技术要点】

| # | 核心机制 (按原文出现顺序) | 关键术语 / 参数 |
|---|--------------------------|-----------------|
| 1 | **生成式推荐的双边职责切分**: LLM body 由 xLLM 执行; sparse feature 处理 / sample 构造 / online serving 由传统 `predictor` 侧承担, 双方通过 shared library `.so` 接口集成 | `backend=rec`、`.so` 共享库 |
| 2 | **优化目标差异**: 通用 LLM 推理关心"逐 token 交互质量 (TTFT、token interval、动态插入 / 结束)", 而 GR 关心"在固定解码轮数内对多个候选的高质量排序", 典型指标如 `CTR` | `CTR`、`beam search` |
| 3 | **Beam search 在 GR 中的语义**: "每轮解码保留多个高分候选分支, 在后续轮次继续展开并比较", 目的是在少量解码轮次内"覆盖更多高质量候选"而非生成更长文本 | `beam_width`、`top_k` |
| 4 | **工作负载画像**: GR 呈 "long prompt + short output"——prompt 因携带用户历史 / 上下文 / 推荐侧信号而较长, 输出为固定长度的 item token 序列, 解码轮数"固定且通常较小"; 与通用 LLM 的 "short prompt + long output" 鲜明对比 | 固定解码轮数、固定长度输出 |
| 5 | **GR 自然衍生的两条特性**: (a) **fixed-step decoding**; (b) **synchronized comparison of multiple candidates**, 直接驱动后续控制层固定调度 + 执行层 whole-graph multi-step 的设计抉择 | fixed-step、whole-graph |
| 6 | **模型族与端到端结构**: 重点描述两类已规模化部署的模型——`OneRec` (用于召回) 和 `OneTrans` (用于排序); 输入适配层将离散 ID / 连续值 / 序列 / 多模态内容等异构信号映射为 embedding, 模型主体仍为 `Encoder+Decoder` 或 `Decoder-only` LLM 结构; 输入适配层归 `predictor`, LLM body 归 xLLM | `OneRec`、`OneTrans`、input adaptation layer、Encoder+Decoder、Decoder-only |
| 7 | **三大核心挑战**: (a) 长度虽短并不等于 decode 便宜——shared-prefix 复用、跨 beam 的重复 KV 访问、beam 相关的 block 搬运会显著放大; (b) `beam_search` 在 GR 中不仅是算法问题, 排序 / 过滤 / valid-item 校验 / 候选留存 / 数据结构复用都升级为系统级关注点; (c) 在严格在线延迟与高并发下, host 在每一步反复回主控准备下一输入并下发, host-device 协同本身成为延迟预算的重要组成部分 | beam 相关 block movement、host-device cooperation |

> 关于 `xAttention`、`fixed scheduling`、`whole-graph multi-step execution` 三者在执行形态、内存与执行效率上如何具体协作——由于原文 RPC Integration 小节被截断, 此处的细节描述**未能提供**。

---

## 【关键机制与数据】

### 1. 路径入口与职责边界

- 原文: "xLLM provides generative recommendation inference through the `backend=rec` path."
- 原文: "the LLM body is executed by xLLM, while the traditional recommendation system continues to handle feature preparation and online integration."
- 原文: "the `predictor` side continues to handle sparse feature processing, sample construction, and online service integration; the `xLLM` side is responsible for the LLM-related inference computation."

可复用能力包括 (原文): operators、KV cache management、multi-backend execution、scheduling——即 xLLM 的基础设施被复用到了 GR 路径。

### 2. 优化目标差异 (原文要点提炼)

| 维度 | 通用 LLM 推理 | 生成式推荐 (GR) |
|------|----------------|------------------|
| 关注点 | token-by-token 交互质量: 首 token 延迟、生成 token 间隔、动态插入 / 结束 | 总请求延迟、固定轮数内的候选质量 |
| 输出形态 | 开放式长文本 | 固定长度 item token 序列 |
| 比较方式 | 单序列推进 | 多候选同步比较 |
| 调度倾向 | 支持动态插入 / 结束 | 固定步数、固定调度 |
| 典型下游指标 | 用户阅读 / 对话质量 | `CTR`、候选召回质量 |

### 3. 数据流 (按原文描述重建)

1. **特征 / 样本准备**: 由 `predictor` 侧完成稀疏特征处理、样本构造, 形成 prompt;
2. **输入适配**: 通过 input adaptation layer 把离散 ID、连续值、序列、多模态内容等异构推荐信号映射为 embedding;
3. **LLM 主干推理**: 由 xLLM 在 `backend=rec` 路径下执行 Encoder+Decoder / Decoder-only 结构;
4. **Beam search 解码**: 每轮保留 `beam_width × top_k` 量级的高分候选, 在固定轮数内多分支同步展开;
5. **候选比较与输出**: 在固定轮次末对各 beam 候选做对比, 输出最佳候选。

> 注: 上述步骤 2 与 3 之间的具体接口契约 (memory layout / embedding format) 以及步骤 5 的对比策略, 在已给出的原文片段中**未进一步细化**, 不予臆造。

### 4. 性能 / 系统代价相关原文论述

- 原文: "the number of decode rounds is fixed and usually small"
- 原文: "each decode round is still expensive because candidate expansion is often combined with a large `beam_width` and `top_k`"
- 原文: "the system is not amortizing them over a long free-form generation"——意指 short output 使得 shared-prefix 复用 / 跨 beam KV 访问 / block 搬移的摊销窗口很短, 反而显著放大。
- 原文: "the host-side control path itself becomes a major part of the latency budget"——host-device 协同开销是核心瓶颈之一。
- 原文未给出具体的 P50 / P99 延迟、QPS、显存峰值、beam_width 默认值等量化指标, 因此**不进行具体数字补全**。

---

## 【表格解读】

**原文无表格**。文档中仅有通过 markdown 图片 (`figures/generative_recommendation_overview.png`、`figures/generative_recommendation_beam_search.png`、`figures/generative_recommendation_model_onerec.png`、`figures/generative_recommendation_model_onetrans.png`) 呈现的结构示意, 没有任何 markdown 表格形式的参数表 / 性能对比 / 配置项定义。

---

## 【公式解读】

**原文无公式**。文档未呈现任何 LaTeX 数学公式或伪代码公式, 仅以定性叙述方式描述机制。

---

## 【关联】

原文使用前言 + 内部锚点的小节标题构建自身的逻辑关联, 但**未在文末提供站内的其他文档链接** (内部链接字段标注为 "无")。基于原文已展示的内容, 可以归纳出以下模块 / 上下游关系:

### 上游 (xLLM 提供给 GR 的能力)

- **算子库 (operators)**: GR 中 attention / embedding / KV 相关算子由 xLLM 统一提供。
- **KV cache 管理**: 因 `beam_width` × 多轮展开导致 KV 复用与搬移成本放大, GR 对 KV cache 管理提出更高要求。
- **多后端执行 (multi-backend execution)**: xLLM 的多硬件后端能力被 GR 直接复用。
- **调度 (scheduling)**: GR 倾向"固定调度"形态, 与通用 LLM 的动态调度策略不同。
- **`xAttention`**: 原文明确提及 xAttention 与 beam search 在"memory efficiency 与 execution efficiency"上存在协同, 但具体协同机制因原文被截断而**未能详细展开**。

### 平行模块 (与 GR 平行的能力)

- **通用 LLM 推理 (`backend=llm` 或类似路径)**: 文档反复对比二者的优化目标差异, GR 是其"针对推荐场景的特化分支", 二者共享 xLLM 底层基础设施。

### 下游 (xLLM 服务的业务集成方)

- **`predictor` 侧**: 在 RPC 集成模式下, xLLM 与 predictor 通过 RPC 协作 (主要用于"营销与在线召回" 场景, 原文); 在 shared library (`.so`) 集成模式下, xLLM 与 predictor 在同一进程内通过动态库接口协作。原文此处因截断而缺少 `.so` 模式的细节。
- **OneRec (召回业务)**: 模型族之一, 与 xLLM 的 LLM body 执行路径对接。
- **OneTrans (排序业务)**: 模型族之一, 同样复用 xLLM 的 LLM body 执行路径。

### 关联但原文未明示的内容

- fixed scheduling、whole-graph multi-step execution、custom kernel 三者之间的逐层关系——文档声称 "clarify the relation" 但具体澄清内容因截断而缺失。
- rec 相关核心代码在当前分支中的位置——文档将 "where the core REC-related code is located in the current branch" 列为要阐述的 topic, 但具体路径因截断而缺失。

---

## 【使用方法】

> 启用方式 / 配置项 / 命令相关原文:

- **后端选择开关**: 原文给出 "`backend=rec`" 作为启用 GR 推理路径的配置形式 (本质上是 backend 选择参数的一个取值)。
- **集成模式**: 原文明确 GR 提供两种集成方式——`RPC Integration` 与 `shared library (.so) integration`。
  - `RPC Integration`: 原文明确 "The current marketing and online recall scenarios mainly use the RPC-based integration mode", 强调其优势是 "clean service boundary", 但优势细节及具体 RPC 调用协议因原文截断 (停留在 "while the downs") 而**缺失**。
  - `shared library (.so) integration`: 文档声称存在该模式, 因原文截断, **具体配置项、so 文件名、链接方式、API 签名均未给出**。
- **解码参数**: 涉及 `beam_width`、`top_k`、`fixed-step decode rounds`——文档明确它们在 GR 中以"较大 `beam_width`、`top_k`"和"固定且通常较小"的轮数形式出现, 但具体的默认值 / 推荐值 / CLI flag 名称因原文未提供而**不能臆造**。
- **编译 / 启动命令 / 配置文件示例 / 环境变量**: 原文均**未涉及**, 不予补全。

---

**总结**: 本文档在已给出的篇幅内, 已清晰地确定了"GR 不是另一个 attention 模型"的立场, 并完成了"背景 → 负载画像 → 三大挑战 → 模型结构 → 推理集成架构"的前半段叙述; 但后半段 (fixed scheduling、whole-graph multi-step execution、`xAttention` × `beam_search` 协同细节、`.so` 集成、代码位置) 因原文截断而缺失, 解读严格止步于已呈现内容, 未做任何机制外推。

## 图文联合解读

- `generative_recommendation_overview.png`: **图示内容**：(a) 判别式推荐为级联架构，召回(百万)→粗排(千)→精排(几十)输出打分列表；(b) 生成式推荐为统一架构，用户历史序列经 Transformer(Self-Attention+FFN) 主体，再由 Beam Search 解码出下一物品。

**技术结论**：生成式推荐以单一生成模型替代多级级联管线，依赖 Self-Attention 建模序列依赖、Beam Search 兼顾多候选与效率。

**与文档关联**：论证 xLLM `backend=rec` 复用 LLM 推理引擎（Transformer 主体+Beam Search）的合理性，为其选择固定调度与整图多步执行提供架构动机。
- `generative_recommendation_beam_search.png`: **1) 图中内容**：展示 Beam Width=5、Top-k=2 的束搜索过程。时间步1从`[]`扩展出5个候选(A–E)，保留Top-2(A、C)；时间步2各自再扩展5个候选并保留Top-2，得`AB`、`CE`；时间步3同理得到`ABD`、`CED`。蓝圈高亮每步被选中的token。

**2) 技术结论**：束搜索每步都将候选池宽度限制为固定常量(B=5)，再裁剪至Top-k，因此候选状态空间有上界、可预测，便于算子展开为固定计算图。

**3) 与文档关系**：呼应文档"REC路径倾向固定调度与全图多步执行"的论点——束搜索的候选宽度恒定，为多步整图调度、xAttention显存优化及自定义kernel提供了前置条件，是`backend=rec`工程取舍的关键依据。
- `generative_recommendation_model_onerec.png`: **图示内容**：左下Context Processor将用户静态/短期/长期三路异构特征经线性层与RMSNorm融合为统一上下文，作为共享KV；右侧Lazy Decoder以BOS+语义ID序列经Embedding→RMSNorm→无wk/wv的Lazy Cross-Attention（GQA）→因果自注意力→FFN，堆叠N层后经输出线性层预测下一item的语义ID，并配合beam search输出S¹/S²/S³。

**论证结论**：跨层共享KV且省去交叉注意力的key/value投影，显著节省显存并利于GQA；固定调度+整图多步推理使其与xAttention、beam search在显存与执行效率上自然契合。

**与文档关联**：直接支撑"backend=rec复用LLM推理引擎"的设计目标，以及固定调度、多步执行与自定义核协同的核心论点。
- `generative_recommendation_model_onetrans.png`: **图文联合解读**：

图(a)：S(蓝)与NS(橙)特征分别tokenize后插入[SEP]，送入OneTrans金字塔堆叠块逐层收缩至NS长度，再接Task Tower输出；(b) OneTrans块由×N次RMSNorm+混合因果注意力+混合FFN组成的pre-norm Transformer块；(c) 混合参数化：S token共享一套QKV/FFN权重，NS token各持专属权重。

**结论**：论证"统一LLM骨干+推荐侧稀疏定制"——LLM推理能力处理用户行为序列(共享权重批推理高效)，NS独享参数承载传统推荐稀疏特征(保留表达力)，印证文档"复用LLM引擎、保留推荐侧稀疏处理与在线能力"的rec路径设计。
- `fixed_steps_scheduler_orca.png`: **图文解读：**

1) 图示：两条请求 x₁="I think this is great"、x₂="I love you" 输入等长但 x₂ 在 iter 2 就输出 `<EOS>` 提前结束，后续 iter 3、4 中 x₂ 只能以 "-" 占位继续跑空计算。

2) 技术结论：在 batched 自回归解码中，输出长度不齐会导致已结束请求产生显著的冗余算力开销（"-" 槽位的额外计算），降低吞吐效率。

3) 与文档论点呼应：正因为 REC 路径输出长度可预测、固定，所以文档主张 **fixed scheduling + whole-graph multi-step** 的执行模式，避免上图所示的填充浪费，从而在推荐场景下兼顾内存与执行效率。
- `paged_attention_comparison.png`: **图示解读：**
1) 图中展示了两个请求（A和B）的KV cache内存布局，含三类浪费：reserved（为未来token预占，如RequestA的2 slots）、internal fragmentation（内部碎片，如RequestA的2038 slots和RequestB的507 slots从未使用）、external fragmentation（请求间空隙）。
2) 论证传统KV cache内存管理效率低下，预留与碎片导致显存浪费，阻碍其他请求调度。
3) 与文档"为何REC路径偏好固定调度与整图多步执行"的论点呼应——正是这些内存浪费促使xLLM设计固定调度策略，通过xAttention压缩冗余KV、beam search控制序列长度，在复用LLM推理引擎的同时降低REC场景的内存碎片开销。
