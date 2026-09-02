# Ulysses长序列并行

> 仓 `mindspeed` · 路径 `docs/zh/features/ulysses-context-parallel.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed/docs/zh/features/ulysses-context-parallel.md

# Ulysses长序列并行 — 深度解读

## 【定位】
本文档系统性介绍 **Ulysses 长序列并行（Context Parallel, CP）** 能力：一种面向超长序列训练场景（万~数十万 token 量级）的分布式并行方案，用以突破传统数据/张量/流水线并行在序列维度上扩展性不足、显存受限与通信开销大的瓶颈。

---

## 【技术要点】

1. **核心机制——序列维切分 + 两阶段 All-to-All**：Ulysses 将各样本沿 **序列维度** 切分到不同计算设备；在 **attention 计算之前** 对 Q/K/V 做一次 all-to-all，使每卡获得 **完整的序列** 但仅持有 **非重叠的 attention-head 子集**；attention 计算完成后，**再做一次 all-to-all** 在 head 维度收集结果并 **重新在序列维度分区** 输出。
2. **算法归属与参考文献**：方案细节引自论文 *DeepSpeed Ulysses: System Optimizations for Enabling Training of Extreme Long Sequence Transformer Models*（arxiv 2309.14509），属于长序列并行的三种可选算法之一。
3. **启用开关**：`--context-parallel-algo` 提供三种算法选项——`ulysses_cp_algo`（Ulysses）、`hybrid_cp_algo`（Hybrid）、`megatron_cp_algo`（Ring Attention），默认值为 `megatron_cp_algo`。
4. **使用约束（整除关系）**：`--num-attention-heads` 必须能被 `tensor-model-parallel-size × context-parallel-size` 整除，这是 Ulysses 能正确切分 head 的前提。
5. **GQA 额外约束**：对 Group Query Attention 模型，还需保证 `num_attention_heads` 能被 `num_query_groups` 整除。
6. **场景推荐**：**非 GQA、序列长度 32k 以下** 的场景推荐开启 Ulysses 长序列并行（"原文: 非--group-query-attention 32k以下场景推荐开启Ulysses长序列并行"）。

---

## 【关键机制与数据】

**工作原理（原文还原的算法流程）：**

1. **序列维切分**：Ulysses 首先把每个样本在 **序列维度** 上分割到参与的计算设备。
2. **第一次 All-to-All（Q/K/V）**：在 attention 计算前，对已切分的 Q、K、V 执行 all-to-all 通信，使每个设备获得 **完整的序列**，但 **仅包含 attention-heads 的一个非重叠子集**。
3. **并行 Attention 计算**：各设备在所分配到的 head 子集上 **并行计算注意力**，互不重叠。
4. **第二次 All-to-All（结果收集）**：在 head 维度收集注意力输出结果，同时 **重新在序列维度分区**，完成一轮 CP 通信。

**性能结论（原文）：**
> "利用多个计算设备对输入序列进行并行切分，降低单设备的内存消耗。相比不开启序列并行，单步耗时增加，但相比重计算，计算效率得到提升。"

即：开启 CP **单步耗时相对不开序列并行会增加**；但相比 **重计算（recomputation/gradient checkpointing）** 计算效率更优；同时 **显著降低单设备显存占用**。

**图示说明**：原文配有 "**图1 Ulysses 切分原理**"（`../figures/ulysses.png`），用于直观展示两次 all-to-all 与 head/序列维度的切换过程。

---

## 【表格解读】

下表**逐字还原**原文 "使用方法" 节中的参数表，并逐行解读：

| 重要参数 | 参数说明 | 是否必选 | 默认值 |
|---|---|---|---|
| `--context-parallel-size [int]` | 设置长序列并行大小，根据用户需求配置。 | 否 | 1 |
| `--context-parallel-algo` | 长序列并行算法选项：<ul><li>**ulysses_cp_algo**：开启Ulysses长序列并行</li><li>hybrid_cp_algo：开启Hybrid长序列并行</li><li>megatron_cp_algo：开启Ring Attention长序列并行</li></ul> | 否 | `megatron_cp_algo` |

**逐行解读：**

- **`--context-parallel-size [int]`**：上下文并行的进程数（即参与 CP 的设备/卡数）。整除约束要求 `num-attention-heads % (tensor-model-parallel-size × context-parallel-size) == 0`；不开启 CP 时取默认值 `1`（即不切序列）。
- **`--context-parallel-algo`**：算法选择开关。同一参数位可切换三种长序列并行策略——Ulysses（本文主角）、Hybrid、Ring Attention（Megatron CP 默认）。三者适用于不同序列长度与硬件拓扑，开启 Ulysses 时需显式置为 `ulysses_cp_algo`。

---

## 【公式解读】

**原文无公式。**

文档未给出任何 LaTeX 公式或伪代码表达式；Ulysses 的数学流程通过文字描述与 `ulysses.png` 示意图呈现。

---

## 【关联】

文档明文提到的关联项如下：

- **三种长序列并行算法的并列关系**：`--context-parallel-algo` 之下并列存在 `ulysses_cp_algo`（Ulysses）、`hybrid_cp_algo`（Hybrid）、`megatron_cp_algo`（Ring Attention），三者互为同位替代方案，默认采用 Ring Attention；本文聚焦 Ulysses，Hybrid 与 Ring Attention 应有独立文档。
- **与张量并行的耦合**：约束 `num-attention-heads % (tensor-model-parallel-size × context-parallel-size) == 0` 表明 Ulysses 需与 `--tensor-model-parallel-size` 联合配置，二者共同决定 head 在 TP×CP 网格中的分布。
- **与 GQA 注意力变体的兼容性**：通过 Group Query Attention 的整除约束，`num_attention_heads % num_query_groups == 0`，体现 CP 对现代注意力变体的兼容要求。
- **与重计算（recomputation）的对比**：原文将 Ulysses 性能与"重计算"对照，表明该特性在功能/性能层面是 **重计算的替代或互补手段**——开启 CP 后单步耗时相对"不开序列并行"会上升，但优于重计算。
- **参考文献**：指向 DeepSpeed Ulysses 原论文（arxiv 2309.14509），作为算法细节与理论依据的上游来源。

> 文末"内部链接: (无)"——本文档未在末尾提供任何内部链接，因此上述关联均基于文中正文显式提及推导。

---

## 【使用方法】

原文给出的可配置项与启用命令如下：

1. **启用 Ulysses 长序列并行**（三选一的关键开关）：
   - 将 `--context-parallel-algo` 设为 **`ulysses_cp_algo`**。
2. **设置上下文并行规模**：
   - `--context-parallel-size [int]`，根据用户需求配置，默认值 `1`（即关闭）。
3. **联合配置约束**：
   - 满足 `num-attention-heads` 能被 `tensor-model-parallel-size × context-parallel-size` 整除。
   - GQA 模型额外满足 `num_attention_heads` 能被 `num_query_groups` 整除。

原文未提供完整启动命令样例（如具体脚本片段、`--num-attention-heads`、`--tensor-model-parallel-size`、`--sequence-parallel` 等参数的标准组合），仅以参数表形式列出 `context-parallel-size` 与 `context-parallel-algo` 两个 CP 相关核心开关。
