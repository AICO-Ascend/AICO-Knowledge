# Quick Start

> 仓 `recsdk` · 路径 `docs/en/torch/torch_rec_v1/quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/recsdk/docs/en/torch/torch_rec_v1/quick_start.md

# RecSDK Torch Quick Start 文档深度解读

## 【定位】

本篇文档是 Rec SDK Torch (torch_rec_v1) 的入门级 Quick Start 指南,旨在通过一个名为 "little_demo" 的最小可运行示例,引导用户在昇腾 NPU 平台上完成从**数据集定义 → 分布式稀疏表分片 → 流水线训练**的端到端推荐模型构建全流程。

---

## 【技术要点】

1. **示例代码位置**: 完整代码托管在 `https://gitcode.com/Ascend/RecSDK/tree/develop_examples_and_tools/torch_examples/little_demo`,共 5 个文件(原文 Table 1)。
2. **Batch 数据结构**: 需继承 `Pipelineable`,并实现 `to()`、`pin_memory()`、`record_stream()` 三个方法(对应 PyTorch 张量设备迁移与异步流同步语义)。
3. **分布式初始化关键配置**: 后端使用 `backend="hccl"`(昇腾集合通信库)进行 NPU 间通信,另起一个 `backend="gloo"` 的 host group 用于 host 侧协调,并封装为 `ShardingEnv(world_size, rank, pg)`。
4. **稀疏表优化器**: 使用 `torch.optim.Adagrad`,参数 `lr=0.001`、`eps=0.1`,通过 `apply_optimizer_in_backward` 把优化器逻辑绑定到反向传播阶段,避免显式 step 调用。
5. **分片策略**: 通过 `get_default_hybrid_sharders(host_env=host_env)` 拿到混合分片器,再以 `EmbeddingShardingPlanner.collective_plan()` 收集全集群分片计划,最后用 `DistributedModelParallel` 包装模型。
6. **混合优化器组装**: 用 `in_backward_optimizer_filter` 过滤出稠密参数,经 `KeyedOptimizerWrapper` 包裹后,与 `ddp_model.fused_optimizer` 通过 `CombinedOptimizer` 合并。
7. **训练流水线**: 使用 `HybridTrainPipelineSparseDist` 类,关键参数 `execute_all_batches=True`,每轮迭代调用 `pipeline.progress(batched_iterator)`。
8. **启动命令**: 容器启动后依次执行 `git clone … -b develop_examples_and_tools` → `cd torch_examples/little_demo` → `export ASCEND_RT_VISIBLE_DEVICES=0,1` → `bash bash.sh`。

---

## 【关键机制与数据】

**工作流(对应 Figure 1 的接口调用流程)**:
原文以编号 1~9 的步骤串起完整链路:

1. **数据契约层** — 把训练所需的全部特征字段打包进自定义 `Batch` 类(`@dataclass`,继承 `Pipelineable`),保证后续流水线能统一处理设备迁移、内存锁定、流同步。
2. **数据源层** — `RandomRecDataset` 实现为 `IterableDataset[Batch]`,与 `Batch` 类型契约对齐。
3. **通信环境层** — 在 NPU 间建立 `hccl` 进程组,在 host 侧建立 `gloo` 进程组,封装为 `ShardingEnv`,这是后续稀疏表分片的前置条件。
4. **模型层** — `TestModel` 将 `HashEmbeddingBagCollection(device="npu", tables=table_configs)` 稀疏表层与稠密层组合,`forward` 必须返回 `(loss, result)`。
5. **稀疏优化器预绑定** — `apply_optimizer_in_backward` 把 `Adagrad` 绑定到 embedding 参数上,使其在反向传播时自动更新。
6. **分布式分片层** — `EmbeddingShardingPlanner.collective_plan(...)` 进行集体规划,`DistributedModelParallel` 按 plan 切分 embedding 表。
7. **优化器合并** — 稠密/稀疏参数分流后,统一封装为 `CombinedOptimizer`。
8. **流水线编排** — `HybridTrainPipelineSparseDist(ddp_model, optimizer, device, execute_all_batches=True)` 把模型、优化器、训练逻辑打包为一步到位的 `progress()` 调用。
9. **训练循环** — `pipeline.progress(batched_iterator)` 是单步训练的统一入口。

**性能/规模数据**: 原文未给出具体性能指标或吞吐量数据。

---

## 【表格解读】

**Table 1  little-demo file description**(原文逐字还原):

| File        | Description                          |
|-------------|--------------------------------------|
| main.py     | Entry point for model training       |
| dataset.py  | Dataset generation                   |
| model.py    | Model file                           |
| bash.sh     | Startup script                       |
| README.md   | Demo model running instructions      |

逐行解读:
- **main.py**: 训练入口脚本,负责串联 Step 3~9 的整体训练流程。
- **dataset.py**: 实现 `RandomRecDataset(IterableDataset[Batch])`,负责生成与 `Batch` 契约对齐的训练样本流。
- **model.py**: 定义 `TestModel(nn.Module)`,内含 `HashEmbeddingBagCollection`,并对外暴露 `forward(batch) → (loss, result)` 接口。
- **bash.sh**: 一键启动脚本,封装环境变量(例如 `ASCEND_RT_VISIBLE_DEVICES=0,1`)与 Python 训练命令的调用。
- **README.md**: 示例运行说明文档,补充 demo 的运行步骤与注意事项。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **示例代码仓库**: 全文核心示例 [Rec SDK Torch Little Demo Sample](https://gitcode.com/Ascend/RecSDK/tree/develop_examples_and_tools/torch_examples/little_examples),文档中所有 `......` 省略号的具体实现都在此处。
- **运行环境准备**: 文中 Option 2 明确链接到 `./recsdk_torch_installation_guide.md#installing-rec-sdk-torch`,即"安装 Rec SDK Torch"章节——说明 Quick Start 是安装指南的下游/配套文档,假设环境已就绪(或使用现成镜像)后即可按本文 9 步流程开发。
- **昇腾镜像下载**: Option 1 引用的镜像页面是另一条外部依赖入口(https://www.hiascend.com/developer/ascendhub/detail/9faeb4847b3e419f81b78a4d0ed574b5),提供 `develop_examples_and_tools` 分支可运行的预构建容器。
- **上下游模块**: 文档显式涉及的模块包括分布式通信(`dist`/`hccl`/`gloo`)、稀疏表(`HashEmbeddingBagCollection`)、分片(`EmbeddingShardingPlanner`、`DistributedModelParallel`)、优化器(`Adagrad`、`CombinedOptimizer`、`KeyedOptimizerWrapper`)、流水线(`HybridTrainPipelineSparseDist`)——这些均属于 Rec SDK Torch 的核心 API,本文是这些 API 的"最小可调用样例"。

---

## 【使用方法】

**环境启动**(两条等价路径):

- **Option 1(推荐/快速路径)**: 从昇腾 hub 拉取预构建镜像 → 按 "Image Overview > Container Startup Commands" 启动并进入容器。
- **Option 2(手动路径)**: 参考 [Install Rec SDK Torch](./recsdk_torch_installation_guide.md#installing-rec-sdk-torch) 自建环境 → 启动并进入容器。

**训练启动命令**(两种路径共用):

```bash
git clone https://gitcode.com/Ascend/RecSDK.git -b develop_examples_and_tools
cd RecSDK/torch_examples/little_demo
export ASCEND_RT_VISIBLE_DEVICES=0,1
bash bash.sh
```

**关键配置项**:
- `ASCEND_RT_VISIBLE_DEVICES=0,1`:指定本进程可见的 NPU 卡为 0 号和 1 号卡(对应两卡分布式训练场景)。
- `device = torch.device("npu")`:所有张量与模型需落在 NPU 上。
- `dist.init_process_group(backend="hccl")`:NPU 间集合通信后端。
- `dist.new_group(backend="gloo")`:host 侧 gloo 通信组,用于分片规划阶段。
- `embedding_optimizer = torch.optim.Adagrad` + `optimizer_kwargs = {"lr": 0.001, "eps": 0.1}`:稀疏表优化器参数。
- `execute_all_batches=True`:`HybridTrainPipelineSparseDist` 构造参数,指示流水线在 `progress()` 内部执行该批次全部子阶段(前向、反向、优化、稀疏表更新、跨设备同步)。
- `dense_optimizer = KeyedOptimizerWrapper(..., lambda params: torch.optim.Adagrad(params, lr=0.1))`:稠密参数优化器学习率 `lr=0.1`(与稀疏表 `lr=0.001` 不同)。

**原文未涉及**的内容:未给出具体的 batch size、训练步数、world_size/rank 数值、性能基准或评估指标;具体模型结构与表配置在 little_demo 仓库 `model.py` 的省略号内。

## 图文联合解读

- `interface-call-process.png`: **图文联合解读**：

1) **图示内容**：垂直流程图，标注"Interface call process"，自上而下分四个分组（Dataset definition → Distributed environment init → Model definition → Training completion），共8个步骤，含Start/End节点。

2) **技术结论**：Rec SDK Torch推荐接口调用遵循"数据→环境→模型(含稀疏表优化、分片、流水线、合并优化器)→训练"的固定顺序。

3) **与文档关系**：图1作为"Interface Call Introduction"的总览，与正文步骤1-3（Batch/Dataset/分布式初始化）一一对应，引导读者按序实现little_demo。
