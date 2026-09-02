# 快速入门<a name="ZH-CN_TOPIC_0000002302229552"></a>

> 仓 `recsdk` · 路径 `docs/zh/torch/torch_rec_v2/03_quick_start/quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/recsdk/docs/zh/torch/torch_rec_v2/03_quick_start/quick_start.md

# 快速入门文档一体化深度解读

## 【定位】
本文档是 Rec SDK Torch 动态稀疏表方案的入门级实操指南,提供从数据集加载、分布式环境初始化、EmbeddingCollection 模型搭建、DynamicEmbeddingSharder 配置、自动分表规划(Planner)、DistributedModelParallel(DMP)包装到模型保存/加载的完整最小闭环样例(little-demo),并给出基于已有镜像与手动准备容器环境两条启动训练路径。

---

## 【技术要点】

1. **稀疏特征 KJT 化**:自定义 `collate_fn` 将 Sparse Features 拼接为 `KeyedJaggedTensor`(keys / values / lengths 三元组),通过 `DataLoader` 注入训练流水线。
2. **分布式后端与 NPU 设备亲和**:`dist.init_process_group(backend="hccl")` + `torch.npu.set_device(local_rank)` + `torch.device(f"npu:{local_rank}")`,绑定 HCCL 集合通信与本地 NPU 卡。
3. **EmbeddingCollection + Over-Arch 模型结构**:`MovieLensModel` 持有 `embedding_module`(EmbeddingCollection)与 `nn.Sequential` 形式的过塔(`over_arch`),前向接收 KJT,经稀疏查表后得到 prediction。
4. **DynamicEmbeddingCollectionSharder 融合优化器**:通过 `fused_params` 字典传入 `optimizer / learning_rate / ...` 等参数,并显式开启 `use_index_dedup=True`(索引去重)。
5. **DynamicEmbeddingShardingPlanner 自动规划**:基于 `eb_configs / topology / constraints / batch_size / enumerator` 生成切分计划,再以 `planner.collective_plan(model, [sharder], dist.GroupMember.WORLD)` 收集为集体计划。
6. **DMP 包装**:用 `DistributedModelParallel(module, device, sharders, plan)` 包装原模型以完成分布式并行。
7. **专用 Dump/Load 接口**:稀疏权重与优化器状态必须使用 `dynamic_emb.distributed.dump_load.DynamicEmbDump(save_dir, model, optim=True)` 与 `DynamicEmbLoad(save_dir, model, optim=True)`(`optim=True` 表示同时落盘优化器状态)。
8. **配套软件版本(Python)**:PyTorch 2.7.1 / TorchNPU 2.7.1 / TorchRec 1.2.0+npu / fbgemm_gpu 1.2.0 / dynamic_emb 25.09;配套 CANN 切换命令 `source /usr/local/set_cann_env.sh a5`(对应 Ascend 950 Toolkit);虚拟环境 `source /opt/buildtools/torch_v2_pt2.7.1/bin/activate`。
9. **训练/验证启动命令**:`torchrun --rdzv-backend=c10d --rdzv-endpoint=localhost:6000 --nnodes=1 --nproc-per-node=1 main.py --train "$@"` 与对应 `--load --dump` 版本(`run.sh` 内自动设置 `PYTHONPATH`)。
10. **数据路径约定**:默认 `./ml-1m`,可通过 `run.sh` 的 `--data_path` 参数覆盖;数据集源 `https://files.grouplens.org/datasets/movielens/ml-1m.zip`。

---

## 【关键机制与数据】

**数据流(原文隐含链路,按 little-demo 步骤串接)**:
原始数据 → `Dataset(collate_fn)` 解析 → `KeyedJaggedTensor(keys/values/lengths)` → `DataLoader` → `EmbeddingCollection`(经 DMP + Sharder 切分后落到各 rank 的 NPU 动态稀疏表)→ `over_arch` → prediction → loss/optimizer → `DynamicEmbDump / DynamicEmbLoad` 持久化。

**关键参数(原文)**:
- 原文:Sharder 关键开关 `use_index_dedup=True`(索引去重,降低动态表膨胀)。
- 原文:Planner 调用方式 `planner.collective_plan(model, [sharder], dist.GroupMember.WORLD)`(集体通信方式汇总 plan)。
- 原文:Dump/Load 默认带优化器状态 `optim=True`。
- 原文:分布式启动规模默认 `--nnodes=1 --nproc-per-node=1`(单节点单进程示例)。
- 原文:CANN 套件命令注释 `# 切换并生效 Ascend 950 配套Toolkit及相关环境变量`(绑定 a5 profile)。
- 原文:训练脚本完成标识 `"Demo done."`。

**性能数据**:原文无任何吞吐量/时延/QPS 等量化指标。

---

## 【表格解读】

### 表 1 — little-demo 文件说明(原文逐字还原)

| 文件名 | 说明 |
|--|--|
| main.py | 模型训练入口 |
| dataset.py | 数据集解析与 KeyedJaggedTensor 数据构建 |
| model.py | 模型文件 |
| run.sh | 启动脚本 |
| logger.py | 日志模块定义 |
| README.md | 数据集下载及 demo 模型运行说明 |

**逐行解读**:
- `main.py`:训练入口,负责 `DataLoader` 装配、分布式初始化、模型构建、训练/保存/加载流程编排。
- `dataset.py`:负责解析 MovieLens-1M 原始数据并构造 `KeyedJaggedTensor`(对应文档第 1 步),是稀疏特征进入 EmbeddingCollection 的唯一通道。
- `model.py`:承载模型结构、`get_sharder` / `get_planner` / `apply_dmp` 等关键函数(对应文档第 3-6 步)。
- `run.sh`:封装 `torchrun` 启动命令、`PYTHONPATH` 设置以及 `--data_path` 等参数入口。
- `logger.py`:统一日志模块,便于训练过程监控。
- `README.md`:数据集获取与运行说明的额外入口,与本指南互补。

### 表 2 — 容器镜像软件配套版本(原文逐字还原)

| 软件名称 | PyTorch | TorchNPU | TorchRec | fbgemm_gpu | dynamic_emb |
|--|--|--|--|--|--|
| 配套版本 | 2.7.1 | 2.7.1 | 1.2.0+npu | 1.2.0 | 25.09 |

**逐行解读**:
- 表头列名分别为五款软件;数据行"配套版本"给出各自版本号。
- `PyTorch 2.7.1` 与 `TorchNPU 2.7.1`:深度学习框架与 NPU 加速绑定版本,需保持主版本一致以保证 ABI 兼容。
- `TorchRec 1.2.0+npu`:TorchRec 的昇腾 NPU 适配分支(`+npu` 后缀即表示带 NPU 算子/通信后端实现)。
- `fbgemm_gpu 1.2.0`:Facebook 的 GPU 端高性能算子库,本仓中作为底层算子依赖(在 NPU 路径上由 TorchNPU 替代执行,fbgemm_gpu 主要用于参考实现/算子注册)。
- `dynamic_emb 25.09`:动态稀疏表核心库,本指南所有 Sharder / Planner / Dump / Load 均来自此模块,版本号采用年月式 `YY.MM` 命名(2025 年 9 月版)。

---

## 【公式解读】

**原文无公式**(文档以 Python 代码片段 + 命令行片段呈现,未出现任何 LaTeX/伪代码形式的公式)。

---

## 【关联】

1. **接口说明(下游依赖)**:文中每个步骤的"参数含义及约束"指向 `../05_api/00_README.md`,即 05_api 章节是本文档所有 `KeyedJaggedTensor`、`EmbeddingCollection`、`DynamicEmbeddingCollectionSharder`、`DynamicEmbeddingShardingPlanner`、`DistributedModelParallel`、`DynamicEmbDump / DynamicEmbLoad` 等接口的权威参数手册;本文档是 API 的"最小用例切片",而 05_api 给出完整签名/约束。
2. **容器镜像使用说明(横向配套)**:方案 1 中的"获取已有运行镜像并启动容器"指向 `../../../../../docker/OVERVIEW.zh.md`,本文档不重复镜像获取/启动细节,只引用该 OVERVIEW;两者形成"镜像准备(上层)↔ 本文档运行(下层)"的依赖链。
3. **安装手册(替代入口)**:方案 2 中的"容器环境准备"指向 `../02_torch_installation_guide/recsdk_torch_installation_guide.md#section182972951211`,与方案 1 互为备选路径——若用户不想用预制镜像,可走此节手动安装 TorchNPU + Rec SDK Torch;两个方案的差异仅在"环境准备",启动训练步骤复用同一份 `run.sh`。
4. **外部资源(数据/样例)**:
   - little-demo 仓库: `https://gitcode.com/Ascend/RecSDK/tree/develop_examples_and_tools/torch_rec_v2_examples/little_demo`(文档第 1-6 步省略的实现全部在此);
   - 数据集: `https://files.grouplens.org/datasets/movielens/ml-1m.zip`(MovieLens-1M,被 `run.sh` 通过 `--data_path` 指向)。
5. **跨章节方法学**:第 2 步的 HCCL 初始化与第 6 步的 `dist.GroupMember.WORLD` 集合通信,体现与"分布式训练"通用范式的对接;第 4 步的 `fused_params` 表明与"融合优化器(Optimizer Fusion)"特性的耦合;第 5 步的 `enumerator` 指向 `torchrec` 的分片枚举器(枚举切分候选),与 Planner 子模块联动。

---

## 【使用方法】

**容器/环境准备(原文方案 1)**:
- 进入容器后,执行 `source /usr/local/set_cann_env.sh a5`(切换 Ascend 950 Toolkit 环境变量)。
- 激活虚拟环境 `source /opt/buildtools/torch_v2_pt2.7.1/bin/activate`。
- 进入样例目录 `cd /RecSDK/torch_rec_v2_examples/little_demo`。

**数据准备(原文)**:
- 下载 MovieLens-1M(链接 `https://files.grouplens.org/datasets/movielens/ml-1m.zip`)并解压。
- 默认路径 `./ml-1m`;可通过 `run.sh` 的 `--data_path ./dataset/ml-1m` 自定义。

**训练/验证启动(原文)**:
- 一键运行:`bash run.sh`(`run.sh` 自动设置 `PYTHONPATH` 并拉起 `torchrun`)。
- 训练子命令:`torchrun --rdzv-backend=c10d --rdzv-endpoint=localhost:6000 --nnodes=1 --nproc-per-node=1 main.py --train "$@"`。
- 端到端(训练→保存→加载→推理):`torchrun --rdzv-backend=c10d --rdzv-endpoint=localhost:6000 --nnodes=1 --nproc-per-node=1 main.py --load --dump "$@"`。
- 成功标志:终端显示 `Demo done.`(原文)。

**手工路径(原文方案 2)**:按 `../02_torch_installation_guide/recsdk_torch_installation_guide.md#section182972951211` 完成环境安装 → 下载 little-demo 样例 → 启动训练步骤同方案 1(原文未涉及)。

**接口参数/约束**:详细可见 `../05_api/00_README.md`(原文);容器镜像获取与启动详见 `../../../../../docker/OVERVIEW.zh.md`(原文)。
