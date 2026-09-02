# 简介<a name="ZH-CN_TOPIC_0000002302229580"></a>

> 仓 `recsdk` · 路径 `docs/zh/torch/torch_rec_v2/01_introduction/introduction.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/recsdk/docs/zh/torch/torch_rec_v2/01_introduction/introduction.md

# Rec SDK Torch 简介 深度解读

---

## 【定位】

本文档是 Rec SDK Torch（基于 TorchRec 的昇腾适配推荐训练 SDK）的总览性 introduction 文档，用于向读者一次性说明 Rec SDK Torch 在昇腾 AI 处理器上的软件分层、核心功能特性以及典型用法入口，覆盖动态稀疏表的分片、缓存、淘汰策略、checkpoint 与增量导出等推荐训练关键能力。

---

## 【技术要点】

1. **架构分层（5 层）**：Rec SDK Torch 由「推荐接口层 → 推荐功能层 → 推荐加速层 → 推荐存储层 → TorchRec-npu 昇腾适配层」构成，自上而下分别为业务接入、核心功能、性能加速、稀疏表分布式存储与原生 TorchRec 的昇腾适配。
2. **两类嵌入模块兼容**：通过 `DynamicEmbeddingCollectionSharder` 适配 `EmbeddingCollection`（Sequence Embedding，`pooling_mode=NONE`），通过 `DynamicEmbeddingBagCollectionSharder` 适配 `EmbeddingBagBagCollection`（Pooled Embedding，sum/mean 池化）。
3. **Row-wise 分布式分片**：所有动态表均通过 `DynamicEmbeddingShardingPlanner` + `DistributedModelParallel` 完成 Row-wise 分片；`DynamicEmbeddingCollectionSharder` 额外支持 `use_index_dedup` 索引去重。
4. **两级缓存（caching）**：在 `DynamicEmbTableOptions` 中设置 `caching=True` 开启「HBM 热数据层（`KeyValueTable`）+ 全量 Storage 冷数据层（HKV / 自定义 `external_storage`）」，需要预留 `local_hbm_for_values` 字节给 Cache；启用前会自动 flush、可用 `reset_cache_states()` 清空。
5. **4 种 score_strategy**：枚举值分别为 `TIMESTAMP=0`、`STEP=1`、`CUSTOMIZED=2`、`LFU=3`，分别映射到 HKV 的 LRU / CUSTOMIZED / CUSTOMIZED / LFU 淘汰策略；`CUSTOMIZED` 是唯一需要业务显式调用 `set_score` 的策略，要求 score 单调递增且非零。
6. **双轨持久化**：全量保存走 `DynamicEmbDump / DynamicEmbLoad`（写入文件系统、含 keys/values/scores 二进制 + meta JSON，可选优化器状态），增量保存走 `incremental_dump(score_threshold=...)`（返回 host 侧 keys/values + 更新后的 score），前者面向 checkpoint 与断点续训，后者面向训练中周期性导出增量特征。
7. **能力限制**：原文明确指出 Caching 与 Prefetch **仅支持** `EmbeddingCollection`（`pooling_mode=NONE`），`EmbeddingBagCollection` 不支持 caching。

---

## 【关键机制与数据】

- **数据流（开启缓存时）**：
  - 训练前向 lookup：先查 Cache（HBM 上的 `KeyValueTable`）→ miss 则回源 Storage 查表或初始化 → 结果回填 Cache。
  - 训练反向更新：优先在 Cache 更新梯度；Cache miss 的 key 回写 Storage。
  - Cache 满时：按淘汰策略驱逐条目，被驱逐的 key/value 自动写入 Storage，保证数据不丢失。
  - 保存前：自动 flush Cache 至 Storage（原文：原文 §多级缓存）。
- **score_strategy 工作原理**：
  - **TIMESTAMP**：调用 NPU `GetSystemCycle` 获取时间戳作为 score；底层 kLru 由 HKV 内部 LRU 处理；dump/load 时对 score 做时间戳变换以持久化。
  - **STEP / CUSTOMIZED**：find/insert 时向 HKV 传入显式 score，按 score 大小决定淘汰顺序；CUSTOMIZED 需用户每次前向训练前手动 `set_score`。
  - **LFU**：每次访问传入增量 score（=1），HKV 在 key 维度累加访问频率，淘汰频率最低的条目。
- **全量保存数据流（原文）**：识别 DMP 封装模型中的 `ShardedDynamicEmbeddingCollection` / `ShardedDynamicEmbeddingBagCollection` → 各 rank 分片数据并行写入文件系统 → 每张表生成 keys/values/scores 二进制文件及 meta JSON（rank 0 写入优化器参数与 evict_strategy）→ 可选保存优化器状态 → 启用 caching 时保存前自动 flush。
- **增量保存数据流（原文）**：以 `get_score()` 返回值作为 `score_threshold` 调用 `incremental_dump` → 返回 host 侧 keys/values + 更新后的 score → 多卡场景下各 rank 匹配结果通过集合通信汇总 → 启用 caching 时合并 Cache 与 Storage 中的数据。
- **性能/吞吐说明**：原文仅定性表述 "提供更优性能"、"训练吞吐" 与 "易用性"，**未给出任何具体性能数字（如 QPS、加速比、时延）**。
- **缓存容量示例（原文数值）**：`max_capacity=1024 * 1024`，`local_hbm_for_values=100 * 1024 * 1024`（即 100 MB）。

---

## 【表格解读】

### 表 1  结构图模块介绍（原文逐字还原）

| Rec SDK Torch模块 | 说明 |
| -- | -- |
| 推荐接口层 | 提供易用性接口、简化用户接入和迁移成本。支持用户规模化上量。 |
| 推荐功能层 | 核心功能实现层，满足用户的使用要求。 |
| 推荐加速层 | 性能竞争力核心组件，为整机系统提供更优性能。 |
| 推荐存储层 | 支持稀疏表的分布式存储。 |
| TorchRec-npu | 开源TorchRec的昇腾适配层。 |

**逐行解读**：
- **推荐接口层**：最靠近业务的一层，目标是降低用户在昇腾上做推荐训练的接入/迁移门槛，方便规模化上量。
- **推荐功能层**：承载具体业务能力（嵌入、稀疏表访问、淘汰、保存等）的实现层。
- **推荐加速层**：性能竞争力核心组件，对整机系统给出更优的训练吞吐与时延。
- **推荐存储层**：负责稀疏 embedding 表在多卡/多节点下的分布式存储，对接 HKV 等后端。
- **TorchRec-npu**：将开源 TorchRec 的关键流程（sharder、planner、DMP 等）适配到昇腾 NPU 上，是上层动态稀疏表能力得以运行的基础适配层。

### 表 2  嵌入模块与分片器对应关系（原文逐字还原）

| TorchRec 模块 | 分片器 | Sharded 模块 | 适用场景 |
| -- | -- | -- | -- |
| EmbeddingCollection | DynamicEmbeddingCollectionSharder | ShardedDynamicEmbeddingCollection | Sequence Embedding，输出变长序列embedding（pooling_mode=NONE） |
| EmbeddingBagCollection | DynamicEmbeddingBagCollectionSharder | ShardedDynamicEmbeddingBagCollection | Pooled Embedding，对特征内 ID 做sum/mean等池化后输出固定维度向量 |

**逐行解读**：
- **EmbeddingCollection 行**：对应序列特征场景，每个 ID 都需保留独立 embedding 向量（`pooling_mode=NONE`），分片器 `DynamicEmbeddingCollectionSharder` 额外支持 `use_index_dedup=True` 以做索引去重；得到的 Sharded 模块是 `ShardedDynamicEmbeddingCollection`。
- **EmbeddingBagCollection 行**：对应 CTR/召回等池化后送入 DNN 的场景，分片器走 `RwPooledDynamicEmbeddingSharding` 接入 `BatchedDynamicEmbeddingBag` 完成 row-wise 分片下的分布式 pooled lookup，Sharded 模块是 `ShardedDynamicEmbeddingBagCollection`。

### 多级缓存配置项表（原文逐字还原）

| 配置项 | 说明 |
| -- | -- |
| caching | 是否启用两级存储，默认False |
| local_hbm_for_values | Cache可用 HBM 大小（字节），Planner中通常按设备内存自动推断 |
| external_storage | 可选，自定义Storage类；未指定时使用HKV作为Storage |

**逐行解读**：
- **caching**：两级缓存的总开关；必须设为 `True` 才能让 HBM 上的 Cache 与外部 Storage 协同工作；默认 `False`。
- **local_hbm_for_values**：在 NPU HBM 中预留给 Cache 的字节数；通常 Planner 会按设备内存自动推断，业务也可显式指定（如原文示例的 `100 * 1024 * 1024`，即 100 MB）。
- **external_storage**：可选的自定义 Storage 后端（如内存字典等）；未指定时底层默认使用 HKV；启用该选项的前提是 `caching=True`。

### 表 3  score_strategy 策略说明（原文逐字还原）

| 策略 | 枚举值 | Score 来源 | 用户是否需set_score | 映射evict_strategy | 典型场景 |
| -- | -- | -- | -- | -- | -- |
| TIMESTAMP | 0 | NPU 设备时间戳，每次前向训练自动更新 | 否 | LRU | 默认策略，零配置近似LRU |
| STEP | 1 | 每前向训练一次，表级step+1，同batch内所有key共用 | 否 | CUSTOMIZED | 按训练步数淘汰；配合Prefetch时score需单调递增 |
| CUSTOMIZED | 2 | 用户自定义，每次前向训练前手动设置 | 是 | CUSTOMIZED | 增量保存、自定义淘汰逻辑 |
| LFU | 3 | 每次前向训练传入score=1，HKV累加访问频率 | 否 | LFU | 最少使用优先淘汰 |

**逐行解读**：
- **TIMESTAMP**：默认策略，由 NPU `GetSystemCycle` 取时间戳作为 score，无需用户介入；映射到 HKV 的 LRU 淘汰策略，等价于"零配置近似 LRU"；dump/load 时会做时间戳变换以保证持久化语义正确。
- **STEP**：表级计数器，前向训练一次 step+1，同 batch 内所有 key 共享同一个 score；映射到 CUSTOMIZED 淘汰策略；配合 Prefetch 使用时要求 score 单调递增。
- **CUSTOMIZED**：唯一需要用户显式调 `set_score` 的策略，业务可在每次前向训练前为每张表自定义 score；映射 CUSTOMIZED；是增量保存（incremental_dump）依赖的基础。
- **LFU**：每次前向传入增量 score=1，由 HKV 在 key 维度累加访问频率；映射 HKV 的 LFU 淘汰策略，淘汰频率最低的条目。

### 表 4  全量保存与增量保存对比（原文逐字还原）

| 维度 | 全量保存 | 增量保存 |
| -- | -- | -- |
| 入口 API | DynamicEmbDump / DynamicEmbLoad | incremental_dump + set_score / get_score |
| 输出 | 写入文件系统 | 返回内存中的 (keys, values) 张量，需业务自行持久化 |
| 保存范围 | 表中全部key-value | score ≥ 阈值的条目（自上次保存以来新增/更新） |
| 典型场景 | checkpoint、断点续训、异卡加载 | 训练中周期性导出增量特征 |

**逐行解读**：
- **入口 API**：全量保存走 `dynamic_emb.DynamicEmbDump / DynamicEmbLoad` 一对接口；增量保存则是 `get_score()` 取阈值 + `incremental_dump(...)` 导出 + `set_score` 回填更新后的阈值，组合使用。
- **输出形态**：全量保存直接落盘到文件系统（含 keys/values/scores 二进制 + meta JSON）；增量保存只返回 host 内存里的 `(keys, values)` 张量，由业务自行决定持久化方式。
- **保存范围**：全量保存覆盖表中所有 key-value；增量保存仅导出 `score ≥ threshold` 的条目（自上次保存以来的新增/更新）。
- **典型场景**：全量保存用于 checkpoint、断点续训、异卡加载；增量保存用于训练过程中周期性导出新增/更新的特征向量。

---

## 【公式解读】

**原文无公式**（文档中未出现 LaTeX 或伪代码形式的数学公式，配置项以枚举值与代码示例呈现，未给出数学表达式）。

---

## 【关联】

- **`../05_api/00_README.md`**（接口说明）：四类核心功能特性的接口细节均指向此处，包括 `EmbeddingCollection/EmbeddingBagCollection`、`DynamicEmbTableOptions`、缓存 API、score 相关 API、dump/load API。
- **`../04_migration_and_training/migration_and_training.md`**（迁移与训练）：与"接口说明"并列，是用户将现有模型迁移到 Rec SDK Torch 并完成训练流程的参考文档。
- **`../05_api/05_dump_load_apis.md#ZH-CN_TOPIC_0000002430202770`**：`set_score / get_score` 的接口细节出处（属于保存与加载 API 文档下的 `set_score` 小节锚点）。
- **`../05_api/05_dump_load_apis.md`**（保存与加载接口）：`DynamicEmbDump / DynamicEmbLoad` 与 `incremental_dump` 的完整接口说明所在。

**模块间上下游关系（原文表述）**：
- **存储层 → 加速层**：底层 HKV（Hierarchical Key-Value）高性能存储库为 `dynamic_emb_extensions` 自定义算子与两级缓存提供存储支撑。
- **功能层 → 接口层**：核心淘汰、缓存、dump/load 能力通过 `DynamicEmbTableOptions`、`set_score / get_score`、`DynamicEmbDump / DynamicEmbLoad`、`incremental_dump` 等 API 暴露给业务。
- **接口层 ↔ TorchRec-npu**：上层 API 通过 `DynamicEmbeddingCollectionSharder / DynamicEmbeddingBagCollectionSharder` 桥接到原生 TorchRec 的 `EmbeddingCollection / EmbeddingBagCollection`，复用其 Planner 与 `DistributedModelParallel` 完成分布式分片。
- **迁移训练 ↔ API**：迁移与训练文档配套 API 文档，给出用户从标准 TorchRec 迁移到昇腾适配版的步骤。

---

## 【使用方法】

### 1. 启用 `EmbeddingCollection` / `EmbeddingBagCollection`（原文代码示例）

```python
from torchrec.modules.embedding_modules import EmbeddingCollection, EmbeddingBagCollection
from dynamic_emb import (
    DynamicEmbeddingCollectionSharder,
    DynamicEmbeddingBagCollectionSharder,
    DynamicEmbTableOptions,
    DynamicEmbScoreStrategy
)

# Sequence Embedding
ec = EmbeddingCollection(tables=table_configs, device="npu")
ec_sharder = DynamicEmbeddingCollectionSharder(fused_params=fused_params, use_index_dedup=True)

# Pooled Embedding
ebc = EmbeddingBagCollection(tables=embedding_bag_configs, device="npu")
ebc_sharder = DynamicEmbeddingBagCollectionSharder(fused_params=fused_params)

table_options = DynamicEmbTableOptions(
    max_capacity=max_capacity,
    score_strategy=DynamicEmbScoreStrategy.TIMESTAMP,
    caching=False,
)
```

### 2. 启用多级缓存（原文代码示例）

```python
table_options = DynamicEmbTableOptions(
    max_capacity=1024 * 1024,
    caching=True,
    local_hbm_for_values=100 * 1024 * 1024,  # 为 Cache 预留 100MB HBM
    score_strategy=DynamicEmbScoreStrategy.TIMESTAMP,
)
```

- 强制约束：`external_storage` 仅在 `caching=True` 时可用。
- 配套操作：保存前自动 flush Cache 至 Storage；`reset_cache_states()` 清空 Cache 热数据。
- **限制**：仅 `EmbeddingCollection`（`pooling_mode=NONE`）支持 caching 与 Prefetch；`EmbeddingBagCollection` 不支持 caching（原文 §多级缓存 限制条目）。

### 3. score 的获取与设置（原文代码示例）

```python
from dynamic_emb import set_score, get_score

# 获取当前各表 score
score_info = get_score(model)

# 设置当前各表 score
set_score(model, {"model.embedding": {"user_table": 200}})
```

- `set_score` 仅支持 `CUSTOMIZED` 策略（score_strategy 枚举值 = 2）。
- **约束**：传入 score 不能为 0，建议单调递增；新 score 小于旧 score 时会发出告警。

### 4. 全量保存（原文代码示例）

```python
from dynamic_emb import DynamicEmbDump, DynamicEmbLoad

DynamicEmbDump(save_dir, model, optim=True, allow_overwrite=False)
DynamicEmbLoad(save_dir, model, optim=True)
```

- `save_dir`：保存目录；`optim` 控制是否保存优化器状态；`allow_overwrite` 控制是否允许覆盖已有文件。
- 启用 caching 时，保存前自动 flush Cache 至 Storage。

### 5. 增量保存（原文代码示例）

```python
from dynamic_emb import set_score, get_score
from dynamic_emb.distributed.incremental_dump import incremental_dump

undump_score = get_score(model)["model.embedding"]
ret_tensors, ret_scores = incremental_dump(
    model,
    score_threshold={"model.embedding": undump_score},
    pg=pg,
)
undump_score = ret_scores["model.embedding"]
```

- 关键参数：`score_threshold` 以表为单位给出，导出 `score ≥ threshold` 的条目；`pg` 为多卡集合通信进程组。
- 返回：`(ret_tensors, ret_scores)`，其中 `ret_scores` 应回写给 `undump_score`，作为下次增量导出的新阈值。
- 启用 caching 时会合并 Cache 与 Storage 中的数据。

## 图文联合解读

- `软件架构图.png`: **图文联合解读：**

1）**图中内容**：呈现两层堆叠式分层架构。上层"Rec SDK Torch"由四层自顶向下构成：推荐接口层→推荐功能层→推荐加速层→推荐存储层；下层为基础栈：TorchRec-npu→Pytorch→CANN→NPU驱动与固件。右侧图例用四种颜色区分Rec SDK Torch、TorchRec-npu、深度学习框架、运行环境。

2）**技术结论**：体现"自上而下分层封装、自下而上依赖支撑"的栈式设计——上层SDK通过TorchRec-npu适配层调用PyTorch深度学习框架，再经CANN编译加速落到NPU硬件，实现昇腾原生的高性能推荐训练链路。

3）**与文档论点关系**：与表1中五层模块介绍逐项对应，验证"易用接口→核心功能→性能加速→稀疏存储→昇腾适配"这一论点，佐证SDK对TorchRec的开源兼容及对Ascend NPU的端到端赋能。
