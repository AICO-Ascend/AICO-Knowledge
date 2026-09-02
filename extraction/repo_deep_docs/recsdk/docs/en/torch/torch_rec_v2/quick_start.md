# Quick Start

> 仓 `recsdk` · 路径 `docs/en/torch/torch_rec_v2/quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/recsdk/docs/en/torch/torch_rec_v2/quick_start.md

# 文档深度解读: Rec SDK Torch Quick Start

## 【定位】

本文档是 Rec SDK Torch (v2) 的快速入门指南,通过一个基于 MovieLens-1M 数据集、依托动态稀疏表 (Dynamic Sparse Table) 的小规模示例 (little_demo),端到端展示从数据解析、分布式环境初始化、模型构建、分片规划、分布式封装到模型保存/加载与训练启动的完整最小化路径,帮助开发者在容器环境中快速跑通一个分布式推荐训练流程。

---

## 【技术要点】

- **示例仓库**: 完整代码位于 `develop_examples_and_tools/torch_rec_v2_examples/little_demo`,核心入口是 `main.py`,`run.sh` 自动设置 `PYTHONPATH` 并启动训练。
- **数据格式**: 自定义 `Dataset` 通过 `collate_fn` 把原始稀疏特征转换为 TorchRec 要求的 `KeyedJaggedTensor (KJT)` 格式,即 `keys / values / lengths` 三元组。
- **分布式后端**: 使用 `backend="hccl"`(华为集合通信库)初始化 `dist.init_process_group`,通过 `local_rank` 绑定 `torch.npu.set_device`,设备形如 `npu:{local_rank}`。
- **模型结构**: 自定义 `MovieLensModel(nn.Module)` 包含一个 `EmbeddingCollection` 用于嵌入抽取,`over_arch` 为上层 MLP。
- **分片器配置**: `DynamicEmbeddingCollectionSharder` 配合 `fused_params` 字典传入 `optimizer / learning_rate` 等融合优化器参数,并启用 `use_index_dedup=True`。
- **自动分片规划**: `DynamicEmbeddingShardingPlanner` 接收 `eb_configs / topology / constraints / batch_size / enumerator` 自动生成分布式分片计划,需调用 `planner.collective_plan(model, [sharder], dist.GroupMember.WORLD)`。
- **分布式封装**: 通过 `DistributedModelParallel(module, device, sharders, plan)` 包装原始模型。
- **存盘/加载**: 使用专用 API `DynamicEmbDump(save_dir, model, optim=True)` 与 `DynamicEmbLoad(save_dir, model, optim=True)`,分别用于保存稠密权重 + 动态嵌入以及加载时恢复优化器状态。
- **运行命令**: `torchrun --rdzv-backend=c10d --rdzv-endpoint=localhost:6000 --nnodes=1 --nproc-per-node=1 main.py --train "$@"`,带 `--load --dump` 时进入训练-保存-加载-推理的端到端验证流程。

---

## 【关键机制与数据】

**数据流** (原文按 7 步顺序描述):

1. **数据预处理**: 原始数据 → 自定义 `Dataset` → `collate_fn` → `KeyedJaggedTensor(keys, values, lengths)` → 通过 `DataLoader` 进入训练循环。
2. **分布式初始化**: `hccl` 后端 → `dist.init_process_group` → 获取 `local_rank` 与 `world_size` → `torch.npu.set_device(local_rank)` → 绑定 `npu` 设备。
3. **模型构建**: `EmbeddingCollection` → `over_arch` (MLP) → 接收 KJT → 输出 `prediction`。
4. **分片器 (Sharder)**: 注入 `fused_params` (含 `optimizer / learning_rate`) → 启用 `use_index_dedup` 去重索引。
5. **分片规划 (Planner)**: 输入 `eb_configs / topology / constraints / batch_size / enumerator` → 输出集合通信级别的分片方案。
6. **分布式封装**: `planner.collective_plan(model, [sharder], dist.GroupMember.WORLD)` → `DistributedModelParallel` 完成 DMP 包装。
7. **持久化**: `DynamicEmbDump` 同时保存稠密模型权重、稀疏权重及优化器状态;`DynamicEmbLoad` 对应恢复。

**运行环境数据** (原文):
- 容器内 Python 虚拟环境路径: `/opt/buildtools/torch_v2_pt2.7.1/bin/activate` (对应 torch 2.7.1)
- CANN 版本设置命令: `bash /usr/local/set_cann_env.sh A5`
- 示例代码路径: `/RecSDK/torch_rec_v2_examples/little_demo`
- 数据集: `ml-1m.zip`, 默认数据路径 `./ml-1m`,可通过 `--data_path` 覆盖
- 启动入口: `bash run.sh`,内部调用 `torchrun --rdzv-backend=c10d --rdzv-endpoint=localhost:6000 --nnodes=1 --nproc-per-node=1 main.py`

**性能数据**: 原文未涉及具体性能指标 (吞吐、QPS、加速比等)。

---

## 【表格解读】

**Table 1 — little-demo file description** (原文逐字还原):

| File        | Description                                              |
|-------------|----------------------------------------------------------|
| main.py     | Entry point for model training                           |
| dataset.py  | Dataset parsing and KeyedJaggedTensor data construction  |
| model.py    | Model file                                               |
| run.sh      | Startup script                                           |
| logger.py   | Log module definition                                    |
| README.md   | Dataset download and demo model running instructions     |

**逐行解读**:

- **main.py** — 训练入口文件。负责装配 `DataLoader`、初始化 `hccl` 分布式环境,以及调用 `apply_dmp` 把模型转换为 `DistributedModelParallel`,并驱动 `--train / --load / --dump` 等 CLI 参数对应的执行分支。
- **dataset.py** — 数据解析与 KJT 构建模块。负责原始 MovieLens-1M 数据的字段映射,通过 `collate_fn` 把一个 batch 的稀疏特征拼接成 `KeyedJaggedTensor`,并把 label 打包为 `torch.float` 张量。
- **model.py** — 模型与分布式组件定义文件。包含 `MovieLensModel` 网络结构、`get_sharder` (构造 `DynamicEmbeddingCollectionSharder` 与 `fused_params`)、`get_planner` (构造 `DynamicEmbeddingShardingPlanner`) 与 `apply_dmp` (执行 `collective_plan` 并返回 DMP) 四个核心函数。
- **run.sh** — 启动脚本。设置 `PYTHONPATH` 与分布式环境变量,通过 `torchrun` 调用 `main.py`,并在参数上透传 `"$@"`,即把脚本收到的 CLI 参数原样转发给训练主程序。
- **logger.py** — 日志模块定义文件。集中封装日志格式、级别与输出流,被 `main.py` 与 `model.py` 复用,保持示例代码中日志风格的一致性。
- **README.md** — 数据集下载与示例运行说明文档。提供 MovieLens-1M 下载地址、解压路径与示例运行步骤,作为用户复现 little_demo 的第一手参考。

---

## 【公式解读】

原文无公式。

(本 Quick Start 示例未引入任何损失函数推导、Embedding 计算或并行分片的数学公式;核心机制完全由 API 调用与参数配置驱动。)

---

## 【关联】

本文档在功能链路上同时依赖前置基础与同模块的姊妹文档:

- **容器启动前置文档** — 链接 `../../../../docker/OVERVIEW.zh.md`:Quick Start 的"Option 1: Starting Model Training Using an Existing Container Image" 的第 1 步明确指向该 OVERVIEW,用于指导用户如何获取预构建运行时镜像、启动容器并进入。这是用户复用 little_demo 的前提 (容器内才有 `/opt/buildtools/torch_v2_pt2.7.1` 与 `/usr/local/set_cann_env.sh` 等环境)。
- **手动安装文档** — 链接 `./recsdk_torch_installation_guide.md#section182972951211`:Quick Start 的"Option 2: Manually Preparing the Running Environment and Starting Model Training" 的第 1 步直接跳到该 section,说明用户如果不使用预构建镜像,需要按安装指南自行准备容器环境。两条路径最终都收敛到 little_demo 的 `bash run.sh` 启动。
- **示例代码仓库** — 链接 `https://gitcode.com/Ascend/RecSDK/tree/develop_examples_and_tools/torch_rec_v2_examples/little_demo`:贯穿全篇,无论是"完整代码"还是"下载示例代码"都指向此处,本文档本质是该示例的导览式导读。
- **上游组件 (TorchRec)** — `KeyedJaggedTensor`、`EmbeddingCollection`、`DistributedModelParallel`、`EmbeddingShardingPlanner` 等接口名称均来自上游 Facebook TorchRec,本文档展示的是 Rec SDK Torch 在昇腾 NPU + HCCL 后端上对 TorchRec 的适配与扩展 (尤其是 `DynamicEmbeddingCollectionSharder` / `DynamicEmbeddingShardingPlanner` / `DynamicEmbDump` / `DynamicEmbLoad` 这四个新增动态稀疏表专用 API)。
- **下游产物 (训练-推理端到端)** — `--dump` + `--load` 组合启动的是训练 → 保存 → 加载 → 推理的全链路验证,意味着本 Quick Start 同时是稀疏权重持久化方案的最小验证用例,与 Rec SDK 中其他动态稀疏表训练/推理教程形成上下游衔接。

**启用方式**:
- 选项 1 (推荐):通过 OVERVIEW 启动预构建容器 → `source /opt/buildtools/torch_v2_pt2.7.1/bin/activate` → `bash /usr/local/set_cann_env.sh A5` → `cd /RecSDK/torch_rec_v2_examples/little_demo` → `bash run.sh`。
- 选项 2 (手动):按 recsdk_torch_installation_guide 的 section 准备运行环境 → 下载示例代码 → 与选项 1 同样的训练步骤。

**配置项/命令** (原文):
- CLI 参数: `--train`(启动训练)、`--load`(加载)、`--dump`(保存)、`--data_path`(覆盖数据路径,默认 `./ml-1m`)。
- torchrun 启动模板: `--rdzv-backend=c10d --rdzv-endpoint=localhost:6000 --nnodes=1 --nproc-per-node=1 main.py`。
- 分布式后端参数: `backend="hccl"`、`local_rank`、`world_size`、`torch.npu.set_device(local_rank)`。
- Sharder 参数: `fused_params={"optimizer": optimizer_type, "learning_rate": learning_rate, ...}`、`use_index_dedup=True`。
- Planner 参数: `eb_configs`、`topology`、`constraints=dict_const`、`batch_size`、`enumerator`。
- DMP 参数: `module=model, device=device, sharders=[sharder], plan=plan`。
- 存盘/加载 API: `DynamicEmbDump(save_dir, model, optim=True)` / `DynamicEmbLoad(save_dir, model, optim=True)`。
