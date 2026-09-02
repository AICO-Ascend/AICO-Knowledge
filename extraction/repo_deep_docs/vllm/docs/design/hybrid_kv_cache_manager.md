# Hybrid KV Cache Manager

> 仓 `vllm` · 路径 `docs/design/hybrid_kv_cache_manager.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm/docs/design/hybrid_kv_cache_manager.md

# Hybrid KV Cache Manager 设计文档深度解读

## 【定位】

本文档解决 vLLM 在服务"混合注意力（hybrid attention）"大语言模型时如何**统一分配多类型 KV Cache 物理页**以及**对不同注意力层施加差异化前缀缓存与逐出规则**的问题，使单一 `KVCacheManager` 能同时支持滑动窗口 / 全注意力 / Mamba / 局部分块等混合架构。

---

## 【技术要点】

1. **混合注意力模型分类**：原文列出四类典型混合架构——
   - 滑动窗口 + 全注意力：gpt-oss、Gemma 2/3、Ministral、cohere；
   - Mamba + 全注意力：Bamba、Jamba、Minimax；
   - 局部分块 + 全注意力：Llama4。
2. **差异化分配规则**：全注意力层需为请求中**全部 token** 预留 slot；滑动窗口层仅保留最近 **`sliding_window_size`** 个 token 的 slot。
3. **差异化前缀缓存命中规则**：全注意力要求前缀命中需**所有 token** 仍在 KV Cache 中；滑动窗口只要求最近 **`sliding_window_size`** 个 token 仍在 KV Cache 中。
4. **统一物理页大小（page size）**：所有层必须共享同一 page size；通过"KV Cache Group"将相同注意力类型、相同 slot 数量的层合并为一组，组内共享 `block_ids`。
5. **分配分桶算法演进**：Case 1（玩具）→ Case 2（理想比例）→ Case 3（无规律比例，按 `min(各类型层数)` 分组并容忍 padding）→ Case 4（不同 `kv_hidden_size`，靠放大 `block_size` 调和）→ Case 5（KV sharing，跳过共享层）。
6. **Gemma-3-27b 实例数据**：52 个滑动窗口层 + 10 个全注意力层 → 以 `min(52,10)=10` 为组大小，划分 5 个滑动窗口组（每组 10 层）+ 1 个全注意力组（10 层）+ 1 个 2 层滑动窗口组（补 8 个 padding 层）。
7. **前缀缓存的 Group 化索引**：块池字典采用 `tuple(block_hash, group_id) -> block` 结构，**同一 token 序列在不同 group 中独立缓存与逐出**，最终取各 group 命中前缀的**交集**作为请求级命中前缀。

---

## 【关键机制与数据】

### 1. 内存池与块划分（原文）

> "We use a single memory pool for all layer types. The memory pool is split into multiple blocks with the same page size."

单一物理内存池，按统一 page size 切分为多个 block；不同层类型按需分配不同数量的 block。

### 2. 关键示例数据（原文 Case 2）

- 模型规模：20 个滑动窗口层 + 10 个全注意力层，`kv_hidden_size` 相同；
- `block_size = 16`，`sliding_window_size = 32`，请求长度 = 112；
- 实际分配 **11 个 block**：block 0–6 给全注意力组、block 7–8 给滑动窗口组 1、block 9–10 给滑动窗口组 2；
- 滑动窗口层对早期 token 标记为"/"（"no block needed"）。

### 3. Group 划分规则（原文）

KV Cache Group 须同时满足：
1. **组内注意力类型一致**——同一组只含同类层，所需 block 数相同，故 `block_ids` 可共享；
2. **跨组 page size 一致**——因为内存池仅支持单一 page size。

### 4. Case 4 关于 `block_size` 的警告（原文）

> "This can lead to more than 400 `block_size` for attention layers, which is too large."

当 `state_size_mamba` 远大于 `kv_hidden_size_att` 时，仅靠放大 `block_size` 调和两种 hidden size 会导致 attention 层 block_size 超过 400 token/block，开销过大；为此提出替代策略（在公式解读中详述）。

### 5. 前缀缓存 key 设计（原文）

> "The block pool uses a dict similar to `tuple(block_hash, group_id) -> block`"

Group 之间独立缓存独立驱逐；请求级命中前缀为各 group 命中前缀的**交集**。

### 6. 文档时间戳（原文）

> "This document was written based on commit `458e74`"

属于早期阶段，行为可能变动。

---

## 【表格解读】

**原文无表格**（文档中仅含图片引用 `figures/basic_grouping_example.png` 与多组数学公式，未提供 markdown 表格）。

如需可视化对照，可参考 Case 2 中描述的 block 分配：

| Block 编号 | 所属 KV Cache Group | 层覆盖 | 用途 |
|---|---|---|---|
| 0–6 | Group 0（full） | full.0 – full.9 | 全 112 个 token 的 KV（10×16=160 slot 余量） |
| 7–8 | Group 1（sw） | sw.0 – sw.9 | 仅最近 32 个 token（"/" 表示早期 token 无 block） |
| 9–10 | Group 2（sw） | sw.10 – sw.19 | 同上 |

（此表为根据 Case 2 原文叙述整理，原文以图示呈现。）

---

## 【公式解读】

### 公式 1：通用 page size 定义

$$
\text{page\_size} = \text{num\_layers} \times \text{block\_size} \times \text{kv\_hidden\_size}
$$

- `num_layers`：当前上下文中涉及的层数（**不一定是模型总层数**）；
- `block_size`：一个 block 容纳的 token 数；
- `kv_hidden_size`：单层单 token 的 KV cache 字节数。

> 原文明确指出："`num_layers` doesn't mean the total number of layers in the model. The exact number depends on the context in this doc."

### 公式 2：代码中的 `KVCacheSpec.page_size_bytes`

$$
\text{block\_size} \times \text{kv\_hidden\_size}
$$

为**单层**一个 block 的字节数；与公式 1 的区别在于不含层数因子。

### 公式 3：纯全注意力模型 page size

$$
\text{page\_size} = \text{block\_size} \times \text{num\_hidden\_layers} \times \text{kv\_hidden\_size}
$$

此时 `num_layers = num_hidden_layers`，可直接整模型统一。

### 公式 4：Case 2 混合模型 page size

$$
10 \times \text{kv\_hidden\_size} \times \text{block\_size}
$$

针对"20 sw + 10 full、相同 `kv_hidden_size`、2 sw : 1 full 比例"模型：以 10 层为一组（1 个 full + 2 个 sw 组各 10 层），page size 为 `10 × kv_hidden_size × block_size`，三个 group 共享同一 page size。

### 公式 5：Case 4 调和 Mamba 的 block_size 下界

$$
\text{block\_size} \times \text{kv\_hidden\_size}_{\text{att}} \ge \text{state\_size}_{\text{mamba}}
$$

放大 attention 层的 `block_size`，使得单 block 字节数 ≥ Mamba 单 token 状态大小；后续对 Mamba 每层做 padding 到相同字节数。

### 公式 6：Case 4 的 Mamba 状态 padding 目标

$$
\text{block\_size} \times \text{kv\_hidden\_size}_{\text{att}}
$$

每个 Mamba 层状态被填充到与放大后的 attention block 等大。

### 公式 7：Case 4 替代 padding 策略

$$
\text{block\_size} \times \text{kv\_hidden\_size}_{\text{att}} \times \text{num\_attn\_layers} \ge \text{state\_size}_{\text{mamba}}
$$

不再逐 token 对齐，而是以**整组 attn 层 × block** 为单位匹配 Mamba 状态；原文标注 "still a work in progress"。

---

## 【关联】

- **`KVCacheManager`（`vllm.v1.core.kv_cache_manager.KVCacheManager`）**：本文档主体讨论对象，所有分配、prefix cache 命中逻辑均通过该类实现；Case 5 中明确提到对其在"忽略 KV 共享层"上的修改。
- **`KVCacheSpec.page_size_bytes`**：与文档 `page_size` 概念相关但定义域不同（不含层数因子）。
- **Prefix Caching（`prefix_caching.md`）**：Case 0（纯全注意力前缀缓存）以及全文 dict 索引设计均建立在该基础能力之上。
- **Model Runner**：Case 5 指出，"some patches are made in model runner to apply the allocation result to kv sharing layers"——KV 共享层的最终 slot 复用由 model runner 配合完成。
- **Eagle Speculative Decoding**：Case 3 提及"models in case 2 but with eagle speculative decoding which introduce one full attention layer"，说明投机解码会在原本整齐比例的模型上**额外引入一层全注意力**，破坏原有 group 结构。
- **代表性下游模型**：Gemma-2、Gemma-3 系列、Llama 4、Bamba、Jamba、Minimax、gpt-oss、Ministral、cohere、gemma-3n 均为该设计的实际适用对象。

---

## 【使用方法】

原文未提供启用方式 / 配置项 / 命令行说明（文档定位为设计说明，且文首标注 "This feature is still in its early stage and things may change"）。仅可从原文推断以下隐含触发条件：

- 加载支持 hybrid attention 的模型架构（gpt-oss、Gemma 2/3、Ministral、cohere、Llama 4、Bamba、Jamba、Minimax 等）时，vLLM v1 的 `KVCacheManager` 会自动应用本文档所述分配策略；
- 分配行为受模型配置中的 `sliding_window_size`、`num_hidden_layers`、`kv_hidden_size` 等参数驱动，但具体配置项 / CLI flag 需查阅 `prefix_caching.md` 与 `KVCacheManager` 源码。

> 原文无表格、无启用命令、无配置文件示例；如需精确配置接口，建议参考 commit `458e74` 对应版本的 `vllm/v1/core/kv_cache_manager.py`。

## 图文联合解读

- `basic_grouping_example.png`: **图示解读**

1. **图内容**：表格按 token 区间（每块 16 token）展示三组 layer 的 block 分配。Group 0（full.0–full.9，全注意力层）所有区间都有 block（0–6）；Group 1（sw.0–sw.9）与 Group 2（sw.10–sw.19，滑动窗口层）仅在最右侧两个区间（80–95、96–111）分配 block（7–8 与 9–10），其余标斜杠表示未分配。

2. **技术结论**：full 层对全部 112 个 token 都预留 KV 槽位；sliding window 层只保留最近 `sliding_window_size` 对应的 token 槽位，实现按层类型差异化分配。

3. **与文档论点对应**：直接论证文档第 1 条需求——"Full attention 层为全部 token 预留槽位，sliding window 层仅保留最近 sliding_window_size 个 token 的槽位"，证明 Hybrid KVCacheManager 对混合模型做了层感知的内存分配。
- `full_attn.png`: **图文联合解读：**

1) **图示内容**：一条横向 token 序列（0–14），其中 0–6 标记为蓝色，7–14 为白色未着色。

2) **技术结论**：在滑动窗口注意力层中，仅为最近的 `sliding_window_size`（此处=7）个 token 保留 KV 缓存槽位；早于窗口的 token 槽位被释放/不分配。

3) **与文档论点对应**：直观印证"Hybrid KV Cache Manager"第一条——不同层类型分配不同槽位：full 层预留全部 token，sw 层仅预留最近窗口 token，从而支撑 hybrid 模型的差异化缓存策略。
- `sw_attn.png`: **图文联合解读：**

**1) 图中内容：** 横向排列15个编号token槽位(0-14)，蓝色块(2-5、8-9、11-13)表示已分配的有效KV缓存，白色块(0-1、6-7、10、14)表示空闲可回收槽位。

**2) 技术结论：** 滑窗注意力只需保留最近`sliding_window_size`个token的KV，因此一个block内会出现"碎片化"的占用模式——新旧请求可复用同一block的不同区间，提升内存利用率。

**3) 与文档关系：** 图示直观验证了文档第二条论点——滑动窗口层无需为所有token预留slot，只需缓存窗口内token即可，空闲槽位可被其他请求复用，区别于全注意力层必须为全部token预留空间的策略。
- `overview.png`: **图文联合解读：**

1）**结构**：类层级图。顶层 `KVCacheManager` 派生三种 Coordinator（`UnitaryKVCacheCoordinator` / `HybridKVCacheCoordinator` / `KVCacheCoordinatorNoPrefixCache`）；`HybridKVCacheCoordinator` 再按 attention 类型聚合多个 `SingleTypeKVCacheManager`（`FullAttentionManager`、`SlidingWindowManager`×1、`MambaManager`×2、……），箭头旁"×1""×2"标注该类型对应的实例/层组数量。

2）**技术结论**：混合模型不能沿用单一管理器，必须为不同 attention 类型各设独立子管理器，由 Hybrid Coordinator 统一调度异构 KV 缓存，实现模块化解耦。

3）**与文档关系**：直接呼应文档论点——"为不同层类型分配不同 slot、支持层特定 prefix-cache 规则"，通过组合模式分层落地。
- `memory_layout.png`: **图文联合解读：**

图示多个 KVCacheTensor 按层类型分配 block：full 层（黄）独占前段较多 block 以保留全部 token；sw 层（绿）仅占少量 block（对应 sliding window）；同窗口的 sw 层（如 sw.0–9、sw.10–19）共享 block；尾部为未分配空间。

论证：同一物理 tensor 内可按注意力类型差异化分配内存，sw 层无需为全 token 预留空间，实现内存高效利用。

与文档关系：直观呈现文档论点 1——"为不同层类型分配不同 slot"的设计思想。
