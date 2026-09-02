# 简介<a name="ZH-CN_TOPIC_0000002302229580"></a>

> 仓 `recsdk` · 路径 `docs/zh/torch/torch_rec_v1/01_introduction/introduction.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/recsdk/docs/zh/torch/torch_rec_v1/01_introduction/introduction.md

# Rec SDK Torch 简介文档深度解读

---

## 【定位】

本文档是「Rec SDK Torch」（基于 PyTorch + TorchRec 的昇腾推荐训练框架）的总览性 introduction 文档，面向搜索/推荐/广告场景中的大规模稀疏 Embedding 分布式训练，旨在系统阐述其核心术语、软件架构、关键功能特性、训练模式（纯显存模式 / 多级缓存模式）以及所支持的昇腾硬件平台与操作系统，为后续 API 使用与功能特性深入提供前置语境。

---

## 【技术要点】

1. **基于栈与异构架构**：Rec SDK Torch 构建在 PyTorch + TorchRec 之上，依托昇腾 NPU + CANN 异构计算架构，承接稀疏 Embedding 表的分布式训练。
2. **两条主训练管线模式**：
   - **纯显存模式**：稀疏表全部驻留 NPU 显存，通过 `HybridTrainPipelineSparseDist` 作为 pipeline 训练。
   - **多级缓存模式**：稀疏表分布于 CPU 内存与 NPU 显存之间，通过 `EmbCacheTrainPipelineSparseDist` 作为 pipeline 训练，可支撑更大规模 Embedding 表。
3. **两类查表 API 形态**：
   - **EBC（EmbeddingBagCollection）**：带 Pooling（SUM / MEAN / NONE）的稀疏表；纯显存模式用 `HashEmbeddingBagCollection`，多级缓存模式用 `EmbCacheEmbeddingBagCollection`。
   - **EC（EmbeddingCollection）**：不带 Pooling 的稀疏表，查表后返回原始 Embedding 列表；多级缓存模式用 `EmbCacheEmbeddingCollection`。
4. **哈希映射**：替代 Torch 原生 `nn.Embedding`，直接将离散 ID 映射为 Embedding 表的行号，免去用户预先做 ID 转换。
5. **Row-wise 分表策略**：按行将 Embedding 切分到不同 NPU 卡，使用取余分桶策略按 ID 余数确定分桶位置；同时也支持 Data-parallel（每卡完整副本）。
6. **关键特性集合**：哈希映射、Row-wise 分表、EC/EBC 查表、流水线查表（通信/CPU/NPU 子任务并行）、查表融合算子（梯度计算+优化器融合）、多级缓存（Device Memory + Host Memory/DDR）。
7. **准入/淘汰机制**：Admit 控制新特征 ID 加入表（重复次数阈值或展示/点击分数阈值）；Evict 移除长时间未访问或低分特征以控制内存。
8. **meta 设备延迟分配**：创建稀疏表时指定 `"meta"` 先建模型结构，待 `DistributedModelParallel` 分表后再实际分配内存。

---

## 【关键机制与数据】

- **工作原理 / 数据流（原文）**：Rec SDK Torch 查表任务由「通信 + CPU + NPU 计算」三类子任务构成，通过**流水线查表**使子任务之间并行执行以充分发挥硬件算力；同时提供「梯度计算 + 优化器」融合的查表算子以优化查表性能。
- **存储分层（原文）**：稀疏表数据可全部放 NPU 显存（纯显存模式），也可采用「Device Memory + Host Memory（DDR）」结合的方式存储（多级缓存模式），从而支撑更大稀疏表规模。
- **分桶机制（原文）**：Row-wise 按行对 Embedding 分表，使用**取余分桶策略**，按 ID 取余的余数确定 Embedding 在表上的分桶位置。
- **Pooling 选项（原文）**：支持 SUM（求和）、MEAN（取平均）、NONE（不做 Pooling）。
- **性能/规模数据**：原文**未涉及**具体性能数字、benchmark、tps 等指标，本文不臆造。

---

## 【表格解读】

### 表格 1 — 核心术语表（原文逐字还原）

| 术语 | 说明 |
|------|------|
| NPU | Neural Processing Unit，神经网络处理器，昇腾 AI 处理器，用于执行深度学习相关的计算任务。 |
| CANN | Compute Architecture for Neural Networks，昇腾计算架构，是华为针对昇腾 AI 处理器开发的异构计算架构，为深度学习提供算子库和运行时支持。 |
| PyTorch | 一个开源的深度学习框架，提供动态计算图、自动微分和丰富的神经网络模块，广泛用于模型训练与推理。 |
| TorchRec | 基于 PyTorch 的推荐系统库，提供大规模稀疏特征 Embedding 表的分布式训练能力，包括稀疏表、优化器、流水线等核心组件。 |
| Embedding | 将离散型特征（如用户 ID、物品 ID）映射为低维稠密向量的技术，是推荐系统中表征特征语义的核心方法。 |
| 稀疏表（Embedding Table） | 用于存储大规模稀疏特征（如用户 ID、物品 ID）的 Embedding 向量的数据结构。 |
| embedding_dim | 稀疏表的列数，即每个特征的 Embedding 向量维度。 |
| num_embeddings | 稀疏表的行数，即最大特征数量。 |
| JaggedTensor | 持有稀疏 ID 和特征长度的数据结构，每个样本的特征 ID 数量可以不同。 |
| KeyedJaggedTensor | 在 JaggedTensor 基础上增加特征名称键（key），用于区分不同特征组。 |
| Pooling | 将同一特征的多个 Embedding 向量聚合为一个向量的操作，支持 SUM（求和）、MEAN（取平均）、NONE（不做 Pooling）。 |
| pipeline | 训练流水线，用于迭代数据集并进行训练。可将训练流程中部分不存在依赖关系的操作并行执行，提高训练效率。 |
| 纯显存模式 | 稀疏表数据全部存放在 NPU 显存中，通过 HybridTrainPipelineSparseDist 作为pipeline进行训练。 |
| 多级缓存模式 | 稀疏表数据分布在 CPU 内存和 NPU 显存之间，通过 EmbCacheTrainPipelineSparseDist 作为pipeline进行训练，支持更大规模的 Embedding 表。 |
| EBC（EmbeddingBagCollection） | 带 Pooling 的稀疏表，查表后自动对同一特征的多条 Embedding 做聚合。纯显存模式使用 HashEmbeddingBagCollection，多级缓存模式使用 EmbCacheEmbeddingBagCollection。 |
| EC（EmbeddingCollection） | 不带 Pooling 的稀疏表，查表后返回原始 Embedding 列表。多级缓存模式使用 EmbCacheEmbeddingCollection。 |
| Row-wise/row_wise | 按行分表策略，将稀疏表的不同行分配到不同 NPU 卡上。 |
| Data-parallel/data_parallel | 数据并行分表策略，每张 NPU 卡保留完整的稀疏表副本。 |
| meta 设备 | PyTorch 的虚拟设备类型，用于延迟实际内存分配。在创建稀疏表时指定 "meta" 可先构建模型结构，待 DistributedModelParallel 分表后再实际分配内存。 |
| 准入（Admit） | 控制新特征 ID 是否被加入到稀疏表中，可通过重复次数阈值或展示/点击分数阈值来过滤低频特征。 |
| 淘汰（Evict） | 将长时间未访问或分数较低的特征 ID 从稀疏表中移除，以控制表的内存占用。 |

**逐行解读**：
- 前 5 条（**NPU / CANN / PyTorch / TorchRec / Embedding**）定义框架依赖栈与基础概念。
- **embedding_dim / num_embeddings** 两条定义了稀疏表的关键形态参数——列数与行数（即最大特征量）。
- **JaggedTensor / KeyedJaggedTensor** 是 TorchRec 中处理"变长稀疏 ID"的核心数据结构，前者只持有 ID 与长度，后者加上 key 以区分多特征组。
- **Pooling** 给出三类聚合语义（SUM/MEAN/NONE），与 EBC 的"自动聚合"行为直接挂钩。
- **pipeline** 强调训练流水线可并行化无依赖子任务，是后续"流水线查表"与两类 `TrainPipelineSparseDist` 的概念前置。
- **纯显存模式 vs 多级缓存模式** 是核心选择：前者规模受限但访存最快，后者通过 CPU+GPU 分层突破规模。
- **EBC / EC** 对标原生 `nn.EmbeddingBag` 与 `nn.Embedding`，差异在是否自动 Pooling。
- **Row-wise vs Data-parallel** 给出两种分表/副本策略的取舍。
- **meta 设备** 解决"先构图再分表"流程中的显存占用问题。
- **Admit / Evict** 是稀疏表动态扩缩容的两端控制机制，分别负责准入与淘汰。

---

### 表格 2 — 结构图模块介绍（原文逐字还原）

|Rec SDK Torch模块|说明|
|--|--|
|推荐接口层|提供易用性接口、简化用户接入流程，降低迁移成本。支持用户规模化上量。|
|推荐功能层|核心功能实现层，满足用户的使用要求。|
|推荐加速层|性能竞争力核心组件，为整机系统提供更优性能。|
|推荐存储层|支持稀疏表的分布式存储。|
|TorchRec-npu|开源TorchRec的昇腾适配层。|

**逐行解读**：自顶向下 5 层构成软件栈：**接口层**面向用户简化接入；**功能层**承载哈希映射、EC/EBC、Row-wise、流水线等核心能力（对应文档"关键功能特性"一节）；**加速层**提供性能关键组件（对应"查表融合算子""流水线并行"等）；**存储层**负责稀疏表分布式存储（即"多级缓存模式""纯显存模式"的承载者）；最底层 **TorchRec-npu** 是将开源 TorchRec 适配到昇腾 NPU/CANN 的桥接层。

---

### 表格 3 — 支持的产品列表（原文逐字还原）

| 产品型号 | 产品架构 | 操作系统版本 |
|---|---|---|
| Atlas 800T A2 训练服务器<br>Atlas 200T A2 Box16 异构子框 | x86_64 | Debian版本：12<br>CentOS版本：7.6 |
| Atlas 800T A2 训练服务器<br>Atlas 200T A2 Box16 异构子框 | ARM | openEuler版本：22.03 |
| Atlas 800T A3 超节点服务器 | ARM | openEuler版本：22.03 |

**逐行解读**：原文表格将前两行产品合并（rowspan=2），这里按语义拆开呈现以便逐行解读：
- **第 1 行**：Atlas 800T A2 训练服务器 / Atlas 200T A2 Box16 异构子框 在 **x86_64** 架构下支持 **Debian 12** 与 **CentOS 7.6** 两套 OS。
- **第 2 行**：同一组产品在 **ARM** 架构下仅支持 **openEuler 22.03**。
- **第 3 行**：Atlas 800T A3 超节点服务器为 ARM 架构，仅支持 **openEuler 22.03**。
- 隐含结论：**A3 超节点仅支持 ARM + openEuler**；**A2 系列** 同时兼容 x86_64（Debian/CentOS）与 ARM（openEuler）。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **训练管线 → Pipeline API**：「纯显存模式」链接到 `../05_api/06_pipeline_apis.md#hybridtrainpipelinesparsedist`（`HybridTrainPipelineSparseDist`）；「多级缓存模式」链接到 `../05_api/06_pipeline_apis.md#embcachetrainpipelinesparsedist`（`EmbCacheTrainPipelineSparseDist`）。这两条链接把"训练模式"概念映射到具体的 `pipeline` 实现类。
- **稀疏表 → 表创建 API**：EBC 在纯显存模式下用 `HashEmbeddingBagCollection`（`../05_api/02_table_creation_apis.md#hashembeddingbagcollection`）；在多级缓存模式下用 `EmbCacheEmbeddingBagCollection`（`../05_api/02_table_creation_apis.md#embcacheembeddingbagcollection`）。EC 在多级缓存模式下用 `EmbCacheEmbeddingCollection`（`../05_api/02_table_creation_apis.md#embcacheembeddingcollection`）。即**模式选择直接决定用哪一张表的类**。
- **关键功能特性 → 迁移与训练章节**：「关键功能特性」一节末尾链接 `../04_migration_and_training/migration_and_training.md#functional_features_description`（功能特性介绍），是哈希映射 / Row-wise / EC-EBC / 流水线 / 融合算子 / 多级缓存 6 大特性的详细展开入口；本简介只给出"是什么"，细节实现与迁移方法需要跳转到该文档。
- **架构层级 ↔ 模块**：架构图中的「推荐加速层」对应"流水线查表 + 查表融合算子"；「推荐存储层」对应"纯显存/多级缓存两种模式与 Admit/Evict 控制"；「TorchRec-npu」适配层是上游 TorchRec 与昇腾 CANN 的桥接——上述要素在文档术语表中都已被命名。

---

## 【使用方法】

原文未涉及具体的启用命令、配置项或代码示例。本文档作为 overview 仅指出以下可选项（均无具体配置数值）：

- **选择训练模式**：纯显存模式（用 `HybridTrainPipelineSparseDist` + `HashEmbeddingBagCollection`）或多级缓存模式（用 `EmbCacheTrainPipelineSparseDist` + `EmbCacheEmbeddingBagCollection` / `EmbCacheEmbeddingCollection`）。
- **选择查表形态**：EBC（自动 Pooling：SUM/MEAN/NONE）或 EC（不 Pooling）。
- **选择分表策略**：Row-wise（取余分桶）或 Data-parallel。
- **稀疏表延迟分配**：创建时指定 `"meta"` 设备，待 `DistributedModelParallel` 分表后再实际分配。
- **容量控制**：通过 Admit（重复次数阈值 / 展示·点击分数阈值）与 Evict 控制表的准入与淘汰。
- **支持的硬件/OS** 见「表格 3」。

具体的 API 调用、参数取值、性能调优配置项需参见文档末链接的 [功能特性介绍](../04_migration_and_training/migration_and_training.md#functional_features_description) 与对应的 [Pipeline APIs](../05_api/06_pipeline_apis.md) / [表创建 APIs](../05_api/02_table_creation_apis.md)。

## 图文联合解读

- `软件架构图.png`: 图分上下两层：上层为Rec SDK Torch自身，含推荐接口层、功能层、加速层、存储层；下层为运行时栈，自上而下为TorchRec-npu、PyTorch、CANN、NPU驱动和固件。配色区分组件归属（蓝=TorchRec-npu、绿=深度框架、灰=运行环境）。该图论证了Rec SDK Torch以PyTorch和TorchRec为基、依托昇腾NPU与CANN异构栈的分层模块化架构，与文档"基于PyTorch和TorchRec构建，依托昇腾NPU和CANN"的论点完全对应。
