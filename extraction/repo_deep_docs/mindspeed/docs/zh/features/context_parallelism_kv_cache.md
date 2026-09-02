# Context Parallelism特性中的KV缓存优化

> 仓 `mindspeed` · 路径 `docs/zh/features/context_parallelism_kv_cache.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed/docs/zh/features/context_parallelism_kv_cache.md

# Context Parallelism KV缓存优化 — 一体化深度解读

## 【定位】

本文档针对大模型长序列并行（Context Parallelism, CP）训练中存在的两类核心问题——**Ring Attention在短序列场景下通信时间难以被计算时间掩盖**、**Ulysses CP在GQA单head场景下因KV repeat带来的内存非连续/OOM**——分别给出KV缓存（Ring）与AllGather KV + All2All Q（Ulysses）的优化方案及灵活配置策略。

---

## 【技术要点】

1. **Ring Attention加入KV缓存**：在前向attention计算的send/recv过程中，将每轮从其他rank接收到的K、V保留至反向计算阶段。反向只需重传dK、dV（不再传K、V），使Ring反向通信量从"K/V/dK/dV四块"减半为"dK/dV两块"。

2. **Ulysses GQA单head场景替换通信方案**：在GQA模型且TP开启后每个rank仅1个head的条件下，用 **AllGather KV + All2All Q** 替换原 **Repeat-All2All KV**，规避对h维repeat导致的地址不连续和transpose开销。

3. **Ulysses KV缓存**：对Repeat-All2All或AllGather通信**前**的KV进行缓存带到反向，反向再重新做一遍Repeat-All2All或AllGather通信以做梯度计算；All2All方案仅在已做Repeat的前提下可开启KV缓存。

4. **分层缓存（interval参数）**：通过`--context-parallel-cache-interval`控制缓存的layer间隔，`interval=1`则缓存layer 0、2、4…；范围0 ≤ interval < rank上的layer数，默认值为0（每层都缓存）。

5. **K-only缓存（half策略）**：`--context-parallel-kv-cache-policy`支持`full`（缓存K和V）和`half`（只缓存K），默认`full`；`half`与`interval`可同时开启，效果叠加。

6. **Ring启用收益的量化条件**：原文给出 `c < F/B`，其中 `c` 是每个计算块分到的序列长度，`F` 是每个device的FLOPS，`B` 是device间带宽——即通信开销相对计算开销更显著时KV缓存才带来加速。

---

## 【关键机制与数据】

### Ring方案数据流

- **切分方式**：序列在sequence维度被切成CP份，每张rank持有1/CP的Q、K、V。
- **前向通信**：每张rank执行CP-1次send/recv后，每段Q均能"关注"到全局KV；当前默认实现中，前向计算完成后KV被丢弃，反向需再send/recv一次KV。
- **反向通信**：rank间需发送K、V、dK、dV四类数据块，共发送CP-1次。
- **缓存优化收益**：在前向将K、V缓存后，反向通信仅剩dK、dV，通信时间减半。
- **原文示例（rank0的收发关系）**：`rank0`将自己的K0/V0和K7/V7发送给"下游"rank，同时接收"上游"rank发来的K3/V3和K4/V4，每张卡重复执行相同的动作CP-1次。

### Ulysses方案数据流

- **默认通信**：Q、K、V均通过All2All交换KV头，KV头数少于CP world size时触发repeat。
- **内存放大**：做repeat后传入attention反向的K/V相较repeat前在内存上扩大CP倍，易OOM。
- **AllGather KV方案**：仅在KV仅1个head时（KV通信量与AllGather通信量等价时），用AllGather直接对s维（地址连续）操作KV，Q仍走All2All，避免repeat和transpose。

### 性能特征（原文定性表述，无具体数字）

- **原文（Ring）**："开启KV缓存特性会使得训练时间变短，提升训练性能，但会导致内存增加。"
- **原文（Ulysses AllGather）**："在允许的场景下，会使得训练时间变短，提升训练性能。"
- **原文（Ulysses KV缓存）**：
  - Repeat-All2All做了Repeat的情况下，"内存使用会减少，但会导致性能下降"；
  - AllGather KV情况下，"内存使用会减少，但相比不开启缓存的AllGather方案，性能可能会有所下降"。

> 注：原文未给出具体加速比、显存节省数字、序列长度等实测数据。

---

## 【表格解读】

| 重要参数 | 参数说明 |
|---|---|
| `--context-parallel-kv-cache-policy [full/half]` | 开启CP前向计算过程缓存KV及其级别，默认full缓存K和V，half仅缓存K |
| `--context-parallel-cache-interval [int]` | 设定执行CP前向计算过程缓存KV的layer间隔层数，默认为0，即每一个layer都需要缓存，根据用户需求配置。 |
| `--use-ulysses-allgather-kv` | 设定Ulysses Attention启用AllGather方案，默认为False，不启用。 |

**逐行解读**：

1. **`--context-parallel-kv-cache-policy [full/half]`**
   - **类型**：枚举字符串，`full` / `half`。
   - **作用域**：CP前向计算过程，控制KV缓存的"级别"（缓存K和V，还是只缓存K）。
   - **默认值**：`full`（缓存K和V）。
   - **设计动机**：在CP比较大时缓存全部K、V对内存压力增大，因此提供"只缓存K"折中选项，因K与V size相同，少缓存一份可省一半KV缓存内存。
   - **注意**：原文注意事项第1条——该参数必须与Context Parallel同时开启，否则特性不支持。

2. **`--context-parallel-cache-interval [int]`**
   - **类型**：整型，表示layer间隔。
   - **作用域**：CP前向缓存KV的频度。
   - **默认值**：`0`（即每层layer都缓存）。
   - **示例**：`interval=1` 表示缓存编号为0、2、4…的layer。
   - **取值范围**：原文表述"从0开始，不超过rank上的layer数量"，即需满足 `0 ≤ interval < rank上的layer数`。
   - **注意**：原文注意事项第2条——必须同时开启`--context-parallel-kv-cache-policy`，且`interval < layer的数量`（此处"小于layer数量"与上文"不超过rank上的layer数量"含义一致，但严格来说`interval < layer_num`才保证不越界），否则特性不支持。

3. **`--use-ulysses-allgather-kv`**
   - **类型**：布尔型开关。
   - **作用域**：Ulysses Attention的通信方案选择。
   - **默认值**：`False`（不启用）。
   - **效果**：启用后Ulysses Attention改用 **AllGather KV + All2All Q** 替换原 Repeat-All2All KV。
   - **前置条件**：原文注意事项第3条——必须同时满足以下4点：
     1. 开启Context Parallel；
     2. 设置`--context-parallel-algo ulysses_cp_algo`；
     3. 开启`--group-query-attention`；
     4. KV每个rank的head数量为1。

---

## 【公式解读】

**原文条件式**：

> "理论上需要确保每个计算块分到的序列长度 `c < F/B`。其中 `F` 是每个device的FLOPS，`B` 是每个device间的带宽。"

**逐符号解释**：

- `c`：每个计算块（chunk）分到的序列长度。原文中对应Ring Attention将序列切成CP份后，每份在每轮send/recv里的子段长度——决定该块attention的算量。
- `F`：每个device的FLOPS（每秒浮点运算次数），代表该device的**算力上限**。
- `B`：每个device间的带宽，代表rank间send/recv的**通信通道吞吐**。
- `F/B`：算力与带宽之比，单位为时间，可视为"每FLOP所对应的通信时间"，或反过来说**计算每块c长度序列所需时间是否短于传输该块所需时间**。
- **`c < F/B` 的物理含义**：当单块序列长度较短，使得"计算该块的时间 < 传输该块的通信时间"时，Ring中通信无法被计算掩盖，开启KV缓存才有收益。原文表述："在Ring Attention中想要使用KV缓存获得收益，需要使得计算时间小于通信时间"。该式即为该条件的代数化表达。

> 注：原文未给出其它公式（如attention、内存放大倍数等），故不另列。

---

## 【关联】

> 文末标注"内部链接: (无)"——文档未提供跳转链接，但文中明确提及以下关联模块/特性，构成上下游/共生关系：

1. **Context Parallelism（CP，长序列并行）**：本文所有特性都以"已开启CP"为前提，是父特性。
2. **Ring Attention** 与 **Ulysses Attention**：本文两类优化分别落在两种CP实现上：
   - Ring Attention → KV缓存（针对send/recv的通信优化）。
   - Ulysses Attention → AllGather KV + All2All Q（针对All2All KV的通信优化），以及KV缓存。
3. **`--context-parallel-algo`**：必须设为 `ulysses_cp_algo` 时才能使用Ulysses类优化（`--use-ulysses-allgather-kv`与`--context-parallel-kv-cache-policy`在Ulysses下都有前置依赖）。
4. **FlashAttention**：使用场景明确指出"目前已默认开启FlashAttention"，是attention计算依赖。
5. **GQA（Grouped Query Attention）**：AllGather KV方案与Ulysses KV缓存的KV Repeat条件都依赖GQA开启，且需满足"Query head数可被KV head数整除"。
6. **TP（Tensor Parallel，张并行）**：文中指出"GQA模型下开启TP后，每个rank通常只有一个head"，即AllGather KV获益的场景源于TP+GQA组合。
7. **`--group-query-attention`开关**：作为`--use-ulysses-allgather-kv`的前置开关，与GQA模型启用直接挂钩。
8. **`--context-parallel-kv-cache-policy` 与 `--context-parallel-cache-interval`**：两者是耦合关系——`interval`必须搭配`policy`才能生效，且效果可叠加（按layer间隔缓存 × 仅缓存K）。
9. **算子效率层**：原文指出对h维做repeat时"地址不连续，会导致算子存在效率问题，并且需要插入transpose等操作"——表明与底层NPU算子（涉及transpose、AllGather、All2All kernel）的效率耦合。

---

## 【使用方法】

### 启用条件

1. 已开启 **Context Parallel**。
2. 已默认开启 **FlashAttention**。
3. （Ulysses相关特性）`--context-parallel-algo` 设为 `ulysses_cp_algo`，并视特性开启 `--group-query-attention`。

### 配置命令

```bash
# Ring 或 Ulysses CP KV缓存（可选 full/half，默认 full）
--context-parallel-kv-cache-policy [full/half]

# 分层缓存间隔（默认 0，每层都缓存；需 < rank上的layer数）
--context-parallel-cache-interval [int]

# Ulysses AllGather KV方案开关（默认 False）
--use-ulysses-allgather-kv
```

### 启用前置约束（原文注意事项，原文有则写）

1. `--context-parallel-kv-cache-policy` 需同时开启 Context Parallel，否则不支持。
2. `--context-parallel-cache-interval` 需同时开启 `--context-parallel-kv-cache-policy`，且 `interval` 小于 layer 数，否则不支持。
3. `--use-ulysses-allgather-kv` 需同时满足：开启Context Parallel、`--context-parallel-algo ulysses_cp_algo`、开启 `--group-query-attention`、每个rank的KV head数为1。
4. `--context-parallel-kv-cache-policy` 配合 `--context-parallel-algo ulysses_cp_algo` 时需满足KV Repeat条件（KV head数 < CP world size 且 Query head数可被KV head数整除；GQA时通常自动满足），否则不支持。All2All方案只能在已做Repeat的情况下开启KV缓存。

### 推荐启用场景（原文"使用场景"）

- **Ring Attention**：需满足 `c < F/B`，即短序列、算力高/带宽相对低、通信难以被计算掩盖的场景。
- **Ulysses Attention + AllGather KV**：GQA模型且KV每个rank仅1个head（通信量等价前提下）的场景。
- **Ulysses Attention + KV缓存**：Repeat-All2All方案在已做Repeat的场景；AllGather方案则在开启CP后即可。
