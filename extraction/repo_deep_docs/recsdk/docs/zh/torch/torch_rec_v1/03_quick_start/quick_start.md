# 快速入门<a name="ZH-CN_TOPIC_0000002302229552"></a>

> 仓 `recsdk` · 路径 `docs/zh/torch/torch_rec_v1/03_quick_start/quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/recsdk/docs/zh/torch/torch_rec_v1/03_quick_start/quick_start.md

# Rec SDK Torch 快速入门 深度解读

## 【定位】

本篇文档为 Rec SDK Torch（基于昇腾 NPU 的推荐 SDK）提供"从零搭建并跑通一个最小推荐模型"的端到端上手指南，覆盖**基础镜像选型 → 容器启动 → 环境变量激活 → 环境可用性验证 → 完整模型代码骨架**五个阶段，使开发者在最短时间内完成分布式稀疏推荐模型（DDP + 行级分片）的闭环验证。

---

## 【技术要点】

1. **镜像版本门槛**：必须使用 **26.0.0*** 及之后版本的昇腾运行镜像，**26.0.0 无 Python 虚拟环境，26.1.0 及之后内置 Python 虚拟环境**（`/opt/buildtools/torch_v1_pt2.6.0/bin/activate`），激活前 Rec SDK Torch 及依赖已默认装好。
2. **容器运行参数**：以**非特权模式**启动，关键参数为 `--shm-size="300g"`、`-m 300g`、`-e ASCEND_VISIBLE_DEVICES="${free_devices}"`；通过 `npu-smi info | grep 'No running processes found in NPU'` 自动侦测空闲 NPU 卡号并按需挂载，避免多卡争用。
3. **CANN 环境变量**：执行 `source /usr/local/Ascend/cann/set_env.sh` 使能 CANN；若 26.1.0+ 镜像需额外激活虚拟环境；退出虚拟环境用 `deactivate`。
4. **环境可用性校验**：执行 `npu-smi info`，若正常回显 NPU 卡信息则环境可用；若报 `dcmi model initialized failed, because the device is used. ret is -8020`，属于**非特权容器 NPU 资源占用冲突**，需参考 `OVERVIEW.zh.md#non_privileged_container_npu_resource_conflict` 处理。
5. **模型搭建四件套 API**：`HashEmbeddingBagConfig`（稀疏表配置）→ `HashEmbeddingBagCollection`（创建稀疏表）→ `get_default_hybrid_sharders`（获取分布式分表策略）→ `HybridTrainPipelineSparseDist`（pipeline 训练），四者构成完整的 Rec SDK Torch 编程模型。
6. **示例模型规模**：2 张稀疏表（`product`、`user`）、3 个特征（`phone`、`clothes`、`user`）、`EMBEDDING_DIMS=[1024, 1024]`、`NUM_EMBEDDINGS=[10240, 10240]`、`ID_RANGES=[1024, 1024, 1024]`、`BATCH_SIZE=32`、`BATCH_NUM=20`；分布策略为 **行级分片 (`row_wise`) + fused 计算内核**，集合通信后端为 **HCCL**，ShardingEnv 进程组后端为 **gloo**。

---

## 【关键机制与数据】

**工作原理（数据流 / 模型构建流，按原文流程编号）：**

- **Batch 定义**（代码注释 1）：`Batch` 继承 `torchrec.streamable.Pipelineable`，封装 `KeyedJaggedTensor`（稀疏特征）与 `torch.Tensor`（label），实现 `to(device)`、`record_stream()`、`pin_memory()`，使其可在 NPU 流与 pinned 内存上正确迁移，是 pipeline 训练的基础数据单元。
- **Dataset 定义**（注释 2）：`RandomRecDataset` 继承 `IterableDataset`，按 `BATCH_NUM=20` 预先生成 20 个 batch；每条特征通过 `torch.randint(0, id_range, (batch_size,))` 生成 ID，`lengths` 全 1 表示每样本 1 个 ID，用 `KeyedJaggedTensor.from_jt_dict` 拼装为 KJT，label 为二值随机张量。
- **分布式环境初始化**（注释 3）：`set_distribute_env()` 读取 `LOCAL_RANK` 设置 NPU 设备，写死 `MASTER_ADDR=127.0.0.1`、`MASTER_PORT=6000`，`GLOO_SOCKET_IFNAME=lo` 强制走 lo 回环接口，集合通信后端为 `hccl`。
- **模型定义**（注释 4）：`TestModel` 按 `TABLE_NAMES / FEAT_NAMES / EMBEDDING_DIMS / NUM_EMBEDDINGS` 逐表生成 `HashEmbeddingBagConfig`，聚合格式为 `PoolingType.SUM`；`HashEmbeddingBagCollection(device="npu", tables=table_configs)` 在 NPU 上实例化 EBC；后接 `torch.nn.Linear(self.input_dim, self.input_dim)`（`input_dim = sum(len(f)*d)`）作为 dense 头。`loss = result.sum()` 仅用于 demo。
- **DDP 包装**（`create_ddp`）：新建 `gloo` 进程组 → `ShardingEnv(world_size, rank, pg=host_gp)` → `get_default_hybrid_sharders(host_env)` 选取分片器 → 为每张表施加 `ParameterConstraints(sharding_types=["row_wise"], compute_kernels=["fused"])` 约束 → `EmbeddingShardingPlanner` 以 `Topology(compute_device="npu")` 调 `collective_plan(test_model, hybrid_sharder, dist.GroupMember.WORLD)` 计算分片计划 → `DistributedModelParallel(test_model, device="npu", plan=plan, sharders=hybrid_sharder)` 包装为 DDP 模型。

**性能 / 数据参数（原文：）：**
- 软件版本配套表（PyTorch 2.6.0 / TorchNPU 2.6.0 / torchrec 1.1.0+npu / fbgemm_gpu 1.1.0 / hybrid_torchrec 1.1.0 / torchrec_embcache 1.1.0）。
- 容器内存上限 `-m 300g`、共享内存 `--shm-size="300g"`。
- 示例数据：`BATCH_SIZE=32`，`BATCH_NUM=20`，`NUM_EMBEDDINGS=[10240, 10240]`，`EMBEDDING_DIMS=[1024, 1024]`。
- 报错码：`-8020`（dcmi device busy）。

> 注：原文**未提供训练吞吐 / QPS / 加速比等性能数据**，亦未给出 loss 曲线或基准对比，故不臆造。

---

## 【表格解读】

### 表格 1：基础镜像中软件配套版本表（原文逐字还原）

| 软件名称    | PyTorch | TorchNPU | torchrec    | fbgemm_gpu | hybrid_torchrec | torchrec_embcache |
|---------|---------|----------|-------------|------------|-----------------|-------------------|
| 配套版本  | 2.6.0   | 2.6.0    | 1.1.0+npu   | 1.1.0      | 1.1.0           | 1.1.0             |

**逐行解读：**
- **PyTorch 2.6.0 / TorchNPU 2.6.0**：基础深度学习框架与 NPU 适配层版本严格对齐到 2.6.0，PyTorch 与 TorchNPU 必须**同版本号**才能保证算子注册与算子融合链路完整。
- **torchrec 1.1.0+npu**：Meta 开源推荐系统库 torchrec 的 NPU 适配发行版，"`+npu`" 后缀表明已 patch NPU 相关分布式原语（`DistributedModelParallel`、`EmbeddingShardingPlanner` 等），不可与官方上游 1.1.0 混用。
- **fbgemm_gpu 1.1.0**：Meta 的稀疏算子库（含 Split/IndexSelect/Embedding 优化），本镜像固定到 1.1.0，需与 torchrec 1.1.0 协同。
- **hybrid_torchrec 1.1.0**：Rec SDK Torch 自研的 hybrid 适配层（即本指南主用包），提供 `HashEmbeddingBagConfig`、`HashEmbeddingBagCollection`、`HybridTrainPipelineSparseDist`、`get_default_hybrid_sharders` 等 NPU 专用 API，版本必须为 1.1.0。
- **torchrec_embcache 1.1.0**：Rec SDK Torch 自研的 EmbeddingCache（旁路缓存）层，与 hybrid_torchrec 协同以降低 NPU HBM 压力，版本同样锁 1.1.0。

**横向关系**：6 个组件构成"上层接口（hybrid_torchrec / torchrec_embcache）→ 中层分布式与算子（torchrec / fbgemm_gpu）→ 底层框架（PyTorch + TorchNPU）"的金字塔依赖；任意一个组件错配版本都会导致分片或算子链路报错。

---

### 表格 2：Rec SDK Torch 关键接口表（原文逐字还原）

| 接口名称 | 接口功能描述 |
|--|--|
| [HashEmbeddingBagConfig](../05_api/02_table_creation_apis.md#hashembeddingbagconfig) | 稀疏表配置，配置稀疏表大小，维度等 |
| [HashEmbeddingBagCollection](../05_api/02_table_creation_apis.md#hashembeddingbagcollection) | 创建稀疏表，根据配置信息创建稀疏表 |
| [get_default_hybrid_sharders](../05_api/05_subtable_apis.md#get_default_hybrid_sharders) | 获取分表器，用于获取稀疏表在分布式训练场景下的分表策略 |
| [HybridTrainPipelineSparseDist](../05_api/06_pipeline_apis.md#hybridtrainpipelinesparsedist) | 创建 pipeline，通过 pipeline 迭代数据集并进行训练 |

**逐行解读：**
- **HashEmbeddingBagConfig**：单张稀疏表的元数据描述对象，输入参数为 `name / embedding_dim / num_embeddings / feature_names / pooling`，对应 `TestModel` 中循环构造的 `config`，是稀疏表的"声明"层。
- **HashEmbeddingBagCollection**：稀疏表的"实例化"层，接收一组 `HashEmbeddingBagConfig` 后在 `device="npu"` 上实际分配 embedding 内存并注册到 `nn.Module`，提供 `forward(kjt) -> JaggedTensor` 接口；对应 `self.ebc = HashEmbeddingBagCollection(...)` 与 `result = self.ebc(batch.sparse_features)`。
- **get_default_hybrid_sharders**：根据 `ShardingEnv`（含 world_size / rank / pg）返回一套**默认 hybrid 分片器**（HybridSharder），覆盖 EBC / EB 等算子；其在 `create_ddp` 中被传入 `DistributedModelParallel(sharders=hybrid_sharder)` 与 `planner.collective_plan(..., hybrid_sharder, ...)`。
- **HybridTrainPipelineSparseDist**：将数据加载、特征迁移、模型前向、反向、optimizer.step 串成**流水线**，使 NPU 计算与 H2D / 特征拷贝 overlap；这是 Rec SDK Torch 区别于裸 torchrec 的性能关键组件（原文 `invoke_main` 中尚未展开调用，但已留出接口）。

---

## 【公式解读】

原文无公式。

---

## 【关联】

依据文末内部链接清单，本文档处于 Rec SDK Torch 文档树中的"快速入门"层级，其上下游与并行模块关系如下：

1. **前置 / 环境层依赖**：
   - 链接 `../../../../../docker/OVERVIEW.zh.md#non_privileged_container_npu_resource_conflict`：本指南的环境可用性小节明确指向该章节处理"`npu-smi info` 报 `-8020`"的冲突，说明本指南**依赖**该 Docker 章节作为排障出口，本章节是它的**触发入口**。

2. **API 详细参考（下游延伸阅读）**：本指南的"模型搭建"流程是抽象骨架，落到具体 API 参数时全部跳转至 05_api 章节：
   - `HashEmbeddingBagConfig` → `../05_api/02_table_creation_apis.md#hashembeddingbagconfig`：查询稀疏表配置项（如 `num_embeddings`、`embedding_dim`、`feature_names`、`pooling`、`weight_initializer` 等）。
   - `HashEmbeddingBagCollection` → `../05_api/02_table_creation_apis.md#hashembeddingbagcollection`：查询 EBC 实例化参数（如 `device`、`tables`、`output_dtypes`、`compute_kernel`）。
   - `get_default_hybrid_sharders` → `../05_api/05_subtable_apis.md#get_default_hybrid_sharders`：查询分片器集合覆盖的算子范围与 `host_env` 入参语义。
   - `HybridTrainPipelineSparseDist` → `../05_api/06_pipeline_apis.md#hybridtrainpipelinesparsedist`：查询 pipeline 阶段切分、H2D overlap、checkpoint 等行为。

3. **API 总览入口**：链接 `../05_api/01_api_description.md` 是整个 05_api 章节的索引页，本指南未直接引用其内容，但属于隐含推荐路径——读者读完本指南后通常会由此页进入完整 API 手册。

4. **同层（quick_start 目录内）关系**：本指南作为 `03_quick_start` 下的第一篇，给出**完整可跑通的最小骨架**；同目录其他章节（如进阶示例、混合并行、性能调优）通常以本篇为基础向外扩展，例如更复杂的 sharding 策略、更换 `HashEmbeddingBagCollection` 为多模态 EBC、或引入 `HybridTrainPipelineSparseDist` 做端到端流水训练。

5. **跨产品关系**：本指南不直接调用，但通过 `torchrec`（`KeyedJaggedTensor`、`JaggedTensor`、`PoolingType`、`DistributedModelParallel`、`EmbeddingShardingPlanner`、`Topology`、`ParameterConstraints`、`ShardingEnv`、`CombinedOptimizer`、`KeyedOptimizerWrapper`、`in_backward_optimizer_filter`、`apply_optimizer_in_backward`、`Pipelineable`）以及 `hybrid_torchrec`、`torch_npu` 串联起 PyTorch + TorchNPU + torchrec + fbgemm_gpu + hybrid_torchrec + torchrec_embcache 六大组件，体现了 Rec SDK Torch 在**昇腾生态下对 Meta TorchRec 工具链的端到端替换**。

---

## 【使用方法】

> 以下内容均为原文显式给出：

**1. 启动容器（创建 `run_docker.sh` 后执行）：**
```shell
bash run_docker.sh 容器名 镜像名称
```
其中"镜像名称"格式为 `REPOSITORY:TAG`，例如 26.0.0 x86 镜像：
`swr.cn-south-1.myhuaweicloud.com/ascendhub/rec_sdk-torch:26.0.0_debian12-x86`

**2. 刷新容器内环境变量（按镜像版本二选一）：**
```shell
# 26.0.0：无虚拟环境，只需使能 CANN
source /usr/local/Ascend/cann/set_env.sh

# 26.1.0+：先使能 CANN，再激活内置 Python 虚拟环境
[ -f /opt/buildtools/torch_v1_pt2.6.0/bin/activate ] && source /opt/buildtools/torch_v1_pt2.6.0/bin/activate
# 退出虚拟环境：deactivate
```

**3. 环境可用性验证：**
```shell
npu-smi info
```
若报 `dcmi model initialized failed, because the device is used. ret is -8020`，参见 `docker/OVERVIEW.zh.md#non_privileged_container_npu_resource_conflict`。

**4. 跑通示例模型（原文步骤）：**
- 创建 `main.py`，按代码注释 1→4 依次定义 `Batch` → `RandomRecDataset` → `set_distribute_env()` → `TestModel` → `create_ddp()`；
- 调用方式（原文 `invoke_main()` 起头部分给出）：`set_distribute_env()` → `device = torch.device("npu")` → 构造 `dataset = RandomRecDataset(BATCH_SIZE, BATCH_NUM, FEAT_NAMES, ID_RANGES)` → `data_loader = DataLoader(dataset, batch_size=None, batch_sampler=None, …)`（原文此行后被截断，下游 DDP / optimizer / pipeline 调用未给出）。

**5. 关键配置项 / 参数（原文给出）：**
- 容器层：`ASCEND_VISIBLE_DEVICES`（环境变量，按空闲卡自动填充）、`--shm-size="300g"`、`-m 300g`、镜像仓库挂载点 `/etc/localtime`、`/etc/ascend_install.info`、`/usr/local/Ascend/driver`（均 `:ro`）。
- 分布式层：`MASTER_ADDR=127.0.0.1`、`MASTER_PORT=6000`、`GLOO_SOCKET_IFNAME=lo`、集合通信后端 `hccl`、ShardingEnv 进程组后端 `gloo`、`Topology(world_size, compute_device="npu")`。
- 分片约束：`sharding_types=["row_wise"]`、`compute_kernels=["fused"]`（每张表相同约束）。
- 模型层：`HashEmbeddingBagConfig(name, embedding_dim, num_embeddings, feature_names, pooling=PoolingType.SUM)`；`HashEmbeddingBagCollection(device="npu", tables=table_configs)`。
- 数据层：`FEAT_NAMES=[["phone","clothes"], ["user"]]`、`TABLE_NAMES=["product","user"]`、`EMBEDDING_DIMS=[1024,1024]`、`NUM_EMBEDDINGS=[10240,10240]`、`ID_RANGES=[1024,1024,1024]`、`BATCH_SIZE=32`、`BATCH_NUM=20`、随机种子 `torch.manual_seed(1)`、label 范围 `torch.randint(0, 2, (batch_size,))`。

**6. 启用流程总览：** 拉取 26.0.0*/26.1.0+ 镜像 → 写 `run_docker.sh` 自动挂空闲 NPU → 启动容器 → `source` CANN env（必要时激活 venv）→ `npu-smi info` 校验 → 创建 `main.py` 并按 4 步骨架填充 → 调用 `invoke_main()` 跑通端到端 demo。

---

> **⚠ 文档截断提示**：原文 `main.py` 片段止于 `DataLoader(dataset, batch_size=None, batch_sampler=None,` 一行，`invoke_main()` 的 DDP 包装、`optimizer` 注册、`HybridTrainPipelineSparseDist` 启动等关键尾部逻辑**未在原文给出**；如需完整可跑通的脚本，请结合 `../05_api/06_pipeline_apis.md#hybridtrainpipelinesparsedist` 与 `../05_api/05_subtable_apis.md#get_default_hybrid_sharders` 的 API 说明自行补全，或参阅同目录下进阶示例文档。本解读严格基于现有原文，未补造截断之后的代码与参数。

## 图文联合解读

- `模型创建流程.png`: **图文联合解读：**

图示为推荐模型搭建流程图，自顶向下分四阶段：①**定义数据集**（定义Batch→创建数据集）；②**分布式环境初始化**；③**定义模型**（创建模型→定义稀疏表优化器→稀疏表分表→整合优化器→创建pipeline）；④**使用pipeline完成训练**。

论证结论：基于Rec SDK Torch构建推荐模型需遵循"数据→分布式→模型(含稀疏表分片与pipeline)→训练"的标准化流程，其中**稀疏表分表**与**pipeline创建**是核心环节。

与文档关系：呼应"使用前说明"中"基于Rec SDK Torch快速搭建推荐模型"的主张，为用户补充环境准备后的代码实现路径提供可视化导航。
