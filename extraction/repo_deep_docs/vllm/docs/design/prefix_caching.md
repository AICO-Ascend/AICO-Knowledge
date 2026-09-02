# Automatic Prefix Caching

> 仓 `vllm` · 路径 `docs/design/prefix_caching.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm/docs/design/prefix_caching.md

# vLLM Prefix Caching Design 文档深度解读

---

## 【定位】

本文档系统阐述 vLLM 在 v1 架构中如何实现 **Automatic Prefix Caching（自动前缀缓存）** —— 通过对已处理请求的 KV-cache blocks 进行哈希化缓存与复用，避免新请求对相同 prompt 前缀进行冗余计算，从而在"几乎无成本且不改变模型输出"的前提下提升 LLM 推理吞吐。

---

## 【技术要点】

1. **基于哈希的 Block 级缓存机制**：每个 KV-cache block 的 hash 由三部分组成 —— `parent hash value`（父 block 的哈希）、`block tokens`（当前 block 内的 token 元组，用于降低哈希碰撞）、`extra hashes`（LoRA IDs、多模态输入 hash、多租户环境下的 cache salt 等）。
2. **仅缓存完整 block（full blocks only）**：未填满的 block 不会被加入缓存，确保复用单元的语义完整性。
3. **默认哈希算法为 SHA-256（v0.11 起）**：提供四种可选算法 —— `sha256`（默认，Python pickle 序列化）、`sha256_cbor`（跨语言可复现）、`xxhash`（128 位非加密哈希，更快但理论碰撞风险更高）、`xxhash_cbor`（CBOR + xxHash 组合，可复现）。
4. **多模态前缀缓存支持**：以图片为例，前端图像处理器生成的 image hash 作为 extra hash 注入 block 哈希中，使 `[IMG]` 占位符（placeholder tokens, 示例中 41 个）与图像本身共同决定 block 唯一性。
5. **多租户缓存隔离（Cache Isolation）**：通过请求级 `cache_salt` 注入首 block 哈希，实现"信任组内可共享缓存、组外完全隔离"，防止基于时序的侧信道攻击。
6. **Block Pool + 双向链表 Free Queue 的 O(1) 数据结构**：在 KV cache manager 初始化时预分配全部 `KVCacheBlock`，并直接在 block 内嵌入 `prev_free_block` / `next_free_block` 指针以构建 free queue，避免 Python 对象创建开销与额外 deque 包装。

---

## 【关键机制与数据】

**核心工作原理（哈希构造）**：
原文：`hash(tuple[components])`，其中 components 包含三个字段。该 hash 必须能"唯一标识"该 block 的 KV 内容 —— Block 1 仅需 block tokens 即可识别；Block 3 则需要累积的前缀 tokens + 当前 block tokens 才能识别，因此引入"父 hash 链"机制以保证前缀感知（prefix-aware）。

**Block Hash 计算示例（多模态 + block size = 16，41 个 placeholder tokens）**（原文）：

| Block | Parent hash | Token IDs | Extra hash |
|---|---|---|---|
| Block 0 | None | 1, 3, 7493, 1681, 1294, 1593, 3937, 9551, \<p\>, ..., \<p\> | \<image hash\> |
| Block 1 | Block 0 hash | \<p\>, ..., \<p\> | \<image hash\> |
| Block 2 | Block 1 hash | \<p\>, ..., \<p\> | \<image hash\> |
| Block 3 | Block 2 hash | \<p\>, ..., \<p\>, 4 | \<image hash\> |

**KVCacheBlock 核心字段**（原文）：`block_id`（不可变）、`block_hash`（满 block 时赋值，evict 时重置）、`ref_cnt`（当前引用该 block 的请求数）、`prev_free_block` / `next_free_block`（构成双向链表）。

**四大组件**（原文，KV cache manager 初始化时形成，对应图 `figures/overview.png`）：
- **Block Pool**：`KVCacheBlock` 列表
- **Free Block Queue**：仅存储头/尾 block 指针用于操作
- **Cache blocks**：hash key → block IDs 的映射
- **Request blocks**：request ID → 已分配 block IDs 的映射

**Block Allocation 流程 —— 新请求**（原文）：
1. 调度器调用 `kv_cache_manager.get_computed_blocks()`，通过对 prompt tokens 哈希并查表 cache blocks 获取已计算 block 序列；
2. 调度器调用 `kv_cache_manager.allocate_slots()`，其内部依次执行：
   1. 计算所需新 block 数，若不足则直接返回；
   2. "Touch" 已计算 block（ref_cnt +1，若未被其他请求使用则从 free queue 移除，防止被驱逐）；
   3. 从 free queue 头部 pop 新 block（若 head 为已缓存 block，则同时"驱逐"该 block，使其他请求无法再复用）；
   4. 若新分配的 block 已被 token 填满，立即加入 cache block 映射，供同 batch 内其他请求复用。

---

## 【表格解读】

**原文无表格**（注：原文以 ASCII 文本示意图、代码块与列表形式呈现 hash 构造、Block 分配流程及多模态 hash 示例，未使用 markdown 表格元素；上述"关键机制与数据"中复现的 block 哈希表系基于原文文字描述整理，非原文表格）。

---

## 【公式解读**

原文给出了一个核心哈希构造的伪代码表达式：

$$ \text{block\_hash} = \text{hash}(\text{tuple}[\text{components}]) $$

其中 `components` 由三部分组成（原文文字说明）：
- **Parent hash value**：父级 block 的 hash 值 —— 形成哈希链，保证前缀敏感性（即 Block N 必须知道 Block 1…N-1 的全部内容才能正确哈希）；
- **Block tokens**：当前 block 内 token 组成的 tuple —— 直接使用 token 而非其 embedding，目的是"reduce potential hash value collision"，即降低哈希碰撞概率；
- **Extra hashes**：使 block 唯一所需的辅助值，包括 LoRA IDs、多模态输入哈希、cache salt 等 —— 用于在不同 LoRA 适配器、不同图像输入、不同租户间区分相同文本前缀的 KV 内容。

此外，原文隐含的 block 数量关系（基于多模态示例，block size = 16，41 个 placeholder tokens + 9 个普通 token + 1 个结束 token = 51 tokens，覆盖 Block 0–3 共 4 个 block）可推得：

$$ \text{num\_blocks} = \left\lceil \frac{\text{total\_tokens}}{\text{block\_size}} \right\rceil $$

但该公式在原文中**未被显式列出**，故仅作解读注释，不视为原文公式。

---

## 【关联】

根据文末标注"内部链接: (无)"，原文未提供指向其他设计文档的内部链接。但根据文档内容本身可推断的关联关系：

- **KV cache manager**：prefix caching 的实现载体，文档明确指出"The prefix caching in vLLM v1 is implemented in the KV cache manager"。
- **Scheduler（调度器）**：通过 `kv_cache_manager.get_computed_blocks()` 与 `allocate_slots()` 与 prefix caching 交互，是触发缓存查找与分配的上游组件。
- **LoRA**：作为 extra hash 的一部分注入 block hash，确保不同 LoRA adapter 下即使 prompt 相同也使用各自独立的 KV cache。
- **多模态输入管线（frontend image processor）**：生成 image hash 并作为 extra hash 传入，是 prefix caching 支持图像输入的关键前置依赖。
- **KV cache operators（allocate / append / free / eviction）**：文档预告将在后续章节介绍（"followed by the prefix caching workflow of major KV cache operators"），但原文因截断未给出。

---

## 【使用方法】

**1. 哈希算法选择**（`vllm serve` 启动时）：

```
--prefix-caching-hash-algo {sha256,sha256_cbor,xxhash,xxhash_cbor}
```

- `sha256`（默认）：pickle 序列化，跨 Python/vLLM 版本可能不可复现；
- `sha256_cbor`：CBOR 序列化，跨语言可复现，推荐用于跨环境确定性缓存；
- `xxhash`：pickle + xxHash（128 位），更快但**非加密安全**，多租户场景需评估安全风险；
- `xxhash_cbor`：CBOR + xxHash，可复现且更快，需安装 `xxhash` 包。

**2. 多租户缓存隔离（cache salt）**：

在请求 JSON 中添加 `cache_salt` 字段：

```json
{
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Here is a document with details about the world series: ..."},
    {"role": "user", "content": "Who won the world series in 2020?"}
  ],
  "cache_salt": "your-cache-salt"
}
```

该 salt 会被注入首个 block 的 hash 中，仅持有相同 salt 的请求可复用彼此的 KV block，从而在共享环境中隔离缓存。

**3. 启用条件**：prefix caching 是 vLLM 的默认行为，无需显式开启开关即可享受 block 级缓存复用；上述命令仅用于**调整哈希算法**或**启用缓存隔离**。

## 图文联合解读

- `overview.png`: ## 图文联合解读

**1) 图示内容**
图为vLLM `KVCacheManager`类继承层次结构图：顶层`KVCacheManager`（蓝），下接三个Coordinator（`Unitary`/`Hybrid`/`NoPrefixCache`），最底层是各注意力后端的具体Manager（`FullAttention`、`SlidingWindow`×2、`Mamba`等）。蓝色高亮路径：`KVCacheManager → HybridKVCacheCoordinator → FullAttentionManager(×1) + SlidingWindowManager(×2)`，标注×1/×2表示混合模型可包含多个同类缓存管理器。

**2) 论证结论**
KV缓存管理采用**Coordinator+Manager分层架构**：Coordinator统一调度前缀缓存与匹配逻辑，底层Manager专注存储各类注意力模式。Hybrid场景天然支持多cache组合复用。

**3) 与文档论点的关系**
文档聚焦"hash-based prefix caching如何用块+前缀唯一定位KV"，该图补充说明了prefix caching在整体cache体系中的**位置与角色**——它是Coordinator层的能力开关（如`KVCacheCoordinatorNoPrefixCache`所示），与底层attention实现解耦，使prefix cache成为"可插拔的几乎免费的午餐"，呼应文档核心论点。
- `free.png`: **图文解读：**

1) **图中内容**：上侧"Request 1"释放块号 2、3、4、8，经箭头进入下方双向链表。链表以哨兵节点（ID:N, Hash:None）为头，按 8→4→3→2 顺序串联，每个节点含 ID、Hash、Prev、Next 字段。

2) **技术结论**：vLLM 用双向链表管理空闲 KV-cache 块，请求结束后回收的块按释放顺序入链，可被后续请求按 LIFO 方式快速复用。

3) **与文档关系**：图示正是文中"hash-based prefix caching"的数据结构落地——空闲块链表与每块 hash 共同支撑前缀命中时的零拷贝块复用，体现"几乎免费午餐"的核心论点。
- `example-time-1.png`: **图文联合解读：**

1) 图示两个数据结构：上方"Request Blocks"字典存储请求的块（ID/Hash/Tokens），下方"Cache Blocks"字典实现 Hash→ID 映射；中间"Block Pool"为双向链表空闲块队列（Head/Tail，num_free_blocks=6）。

2) 论证哈希前缀缓存的两层机制：Hash→ID 字典实现命中查找（块 A-D、A-H、A-L 已缓存），双向链表维护空闲块以便分配/回收。

3) 图直观支撑文档论点——vLLM 采用 `hash(tuple[components])` 标识块：相同 Hash 即可命中复用 KV cache，免去重复前缀计算，实现"几乎免费午餐"的前缀缓存优化。
- `example-time-3.png`: 图中展示了vLLM前缀缓存的三类数据结构：

1) **Request Blocks字典**（顶部）：按ID 0–4存储请求各块，标注哈希(A-D/A-H/A-L/A-P/None)与对应tokens(ABCD…Q)；
2) **Cache Blocks字典**（左下）：建立Hash→ID映射(A-D→0, A-H→1, A-L→2, A-P→3)，用于查找复用；
3) **Block Pool双向链表**（右下）：维护空闲块(ID 5–9)，含FreeBlockQueueHead/Tail指针，num_free_blocks=5。

**技术结论**：哈希寻址+空闲块池实现"按需复用、零冗余分配"——相同前缀命中缓存复用ID，新增部分才从空闲池分配。

**与文档论点关系**：直观验证了文中"hash(tuple[components])唯一标识kv-cache块"的机制，是自动前缀缓存（A-P命中ID 3复用）的数据结构基础。
- `example-time-4.png`: **图文联合解读：**

**1) 图示结构：** 左侧"Request Blocks"展示两个请求的块序列（含ID、Hash、Tokens）；左下"Cache Blocks"为哈希→ID映射表；右侧"Block Pool"为双向链表的空闲块池（ID 7/8/9，num_free_blocks=3）。

**2) 技术结论：** 哈希机制可精准识别共享前缀——Request 0与Request 1共享A-D、A-H块（复用ID 0、1）；分歧块因哈希不同（A-J_kl vs A-L）分配新ID；空闲块由双向链表统一管理。

**3) 与文档关系：** 直观呈现"hash(块token+前缀token)"如何实现跨请求KV cache块复用，印证前缀缓存"近乎零开销"的设计论点。
- `example-time-5.png`: **图解：vLLM 前缀缓存数据结构**

**1) 图中内容**
- **Request Blocks**：将 prompt 按 block 切分，每 block 记录 ID、Hash（由块内 token + 前缀 token 共同决定）、Tokens。
- **Cache Blocks (dict)**：以 Hash→ID 索引已缓存块（如 A-D→0、A-J,kI→5）。
- **Block Pool（双向链表 FreeBlockQueue）**：num_free_blocks=6，含 ID 7、8、9、4（Hash=None 空闲块）与 ID 3、2（已缓存块 A-P、A-L），头尾指针分别为 ID 7 和 ID 2。

**2) 技术结论**
Hash 命中则复用 cache dict 中已存 KV 块，命中失败则从链表头部弹出空闲块写入新 Hash，淘汰时按 LRU 等策略从尾部回收，体现哈希查重 + 链表 O(1) 分配回收的组合效率。

**3) 与文档论点呼应**
印证"hash-based prefix caching"的实现细节：块唯一性 = 块 tokens + 前缀 tokens 的哈希，元数据存储与 FreeBlockQueue 解耦，使前缀复用"几乎是免费午餐"。
- `example-time-6.png`: **图文联合解读：**

1) **图示内容：** 左侧为 Request Blocks 字典（待处理请求）；中部 Cache Blocks 字典将前缀哈希（A-D、A-H、A-L 等）映射到 Block ID；右侧 Block Pool 是双向链表，含 10 个空闲块（含已被占用、Hash 已置值的 ID 0/1/5/6 与空闲块 ID 2/3/4/7/8/9），由 FreeBlockQueueHead/Tail 管理。

2) **技术结论：** vLLM 通过哈希索引实现 O(1) 前缀块查找：哈希命中则复用 Cache Blocks 中已缓存块，未命中则从 Block Pool 空闲链表分配新块，双向链表支持高效的块回收与分配。

3) **与文档关系：** 图示具体化了文档"基于哈希的前缀缓存"机制——Cache Blocks 即 hash(tuple[components]) 的查找结构，Block Pool 体现 KV 块物理存储管理，共同支撑"避免重复计算前缀"的论点。
- `example-time-7.png`: ## 图文联合解读

**1) 图中内容**：展示 vLLM 自动前缀缓存的三个核心数据结构——Request Blocks（按请求组织的块序列，含 cached/evicted 标记）、Cache Blocks（哈希→ID 字典，存可复用 KV 块）、Block Pool（双向链表作空闲块队列，含 head/tail 指针，num_free_blocks=2）。

**2) 技术结论**：哈希命中（ID 0-2）的块直接从缓存复用，未命中（ID 8-9）分配空闲块；淘汰块（A-P、A-J,kl）从 Cache 移入 Free Pool，供后续请求 FIFO 复用，实现零冗余前缀计算。

**3) 与文档关系**：印证文档"hash-based 方案"论点，具体落实哈希索引 + 空闲池双链表的工程实现，使 prefix caching 成为"几乎免费"的优化。
