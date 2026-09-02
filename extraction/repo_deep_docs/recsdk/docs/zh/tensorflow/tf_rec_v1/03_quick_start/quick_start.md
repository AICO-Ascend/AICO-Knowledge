# 快速入门<a name="ZH-CN_TOPIC_0000001580166524"></a>

> 仓 `recsdk` · 路径 `docs/zh/tensorflow/tf_rec_v1/03_quick_start/quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/recsdk/docs/zh/tensorflow/tf_rec_v1/03_quick_start/quick_start.md

# 一体化深度解读：RecSDK TensorFlow 快速入门（little_demo）

## 【定位】
本篇文档面向初接触华为昇腾 MindX RecSDK TensorFlow 版本的开发者，以官方提供的 `little_demo` 样例为蓝本，串讲"使用一个 `tf.Session` 完成推荐模型训练"所需准备的全部文件结构与关键 SDK 接口调用顺序（初始化 → 数据 → 优化器 → 稀疏表 → 计算图 → 梯度/优化 → 训练循环 → 资源释放），并补充单机单卡 / 单机多卡场景下通过环境变量启动训练任务的说明，作为 RecSDK 训练框架的入门导览。

---

## 【技术要点】

1. **`little_demo` 的定位**：仅作为代码示例，演示"如何调用 RecSDK 接口把推荐训练流程串起来"，**不包含具体模型、不实现具体功能**，且文档明确"不支持在 little_demo 上适配用户自己的模型"；代码仓路径为 `gitcode.com/Ascend/RecSDK/tree/develop_examples_and_tools/examples/demo`。
2. **train_and_evaluate 场景限制**：在 `train_and_evaluate` 场景下**不支持多轮 eval**（原文 `[!NOTE]` 标注）。
3. **八步调用链（main.py 主线）**：
   - 步骤1：调用 `init(max_steps, train_steps, eval_steps, save_steps, use_dynamic, use_dynamic_expansion)` 完成框架初始化。
   - 步骤2：调用 `get_asc_insert_func(tgt_key_specs=feature_spec_list, is_training=..., dump_graph=...)`，再 `dataset.map(insert_fn)` → `dataset.prefetch(100)` → `dataset.make_initializable_iterator()`。
   - 步骤3：在 `optimizer.py` 中根据 `use_dynamic_expansion` 分支选择 `create_hash_optimizer_by_address`（`lazy_adam_by_addr`）或 `create_hash_optimizer`（`lazy_adam`）；密集侧固定使用 `tf.compat.v1.train.AdamOptimizer`。
   - 步骤4：调用 `create_table` 建立两张稀疏表 `user_hashtable` / `item_hashtable`，参数 `device_vocabulary_size=cfg.user_vocab_size * 10`，`host_vocabulary_size=0`（注释中保留 `cfg.user_vocab_size * 100` 作为 h2d 测试用例）。
   - 步骤5：`model_forward` 中按 `(feature, hash_table, send_count)` 三元组循环 `sparse_lookup`（传 `access_and_evict_config`、name、modify_graph、batch 等），再做 `tf.reduce_sum(embedding, axis=1, keepdims=False)`，最后交给 `MyModel`。
   - 步骤6：`build_graph` 同时构建 train / eval 两份图，再调用 `get_dense_and_sparse_variable()` 拆分密集 / 稀疏变量。
   - 步骤7：训练主循环：`tf.compat.v1.train.Saver` → `MODIFY_GRAPH_FLAG` 分支选 `modify_graph_and_start_emb_cache(dump_graph=True)` 或 `start_asc_pipeline()` → `tf.compat.v1.Session` → 改图模式 `sess.run(get_initializer(True))`，非改图模式 `sess.run(train_iterator.initializer)` → 条件 restore / save（路径 `./saved-model/sparse-model-{rank_id}-0` 与 `./saved-model/model-{rank_id}`） → 训练 1~200 步，按 `TRAIN_INTERVAL` 评估，按 `SAVING_INTERVAL` 落盘，最后再保存一次。
   - 步骤8：训练结束调用 `terminate_config_initializer()` 关闭数据流释放资源。
4. **数据集与流水线关键参数**：`prefetch(100)`、`MODIFY_GRAPH_FLAG`（配置文件控制）决定是否走改图模式；改图模式仅 dump_graph=True 时开启。
5. **稀疏表容量经验值**：`device_vocabulary_size = cfg.user_vocab_size * 10`、`host_vocabulary_size = 0`；当 `host_vocabulary_size != 0` 时需要与 `prefetch` 配套使用 `nbatch function`（注释中提示）。
7. **启动训练的环境变量（单机场景）**：`CM_CHIEF_IP={host_ip}`、`CM_CHIEF_PORT=60000`、`CM_CHIEF_DEVICE=0`、`CM_WORKER_IP={host_ip}`、`CM_WORKER_SIZE=8`；并要求 `local_rank_size` 与 `CM_WORKER_SIZE = local_rank_size * 训练节点数` 配合。
6. **little_demo 文件清单**：原文以"表 1"枚举 13 个文件（`config.py / dataset.py / deterministic_loss / main.py / model.py / op_impl_mode.ini / optimizer.py / random_data_generator.py / README.md / run_deterministic.sh / run_model.py / run.sh / utils.py`）。

---

## 【关键机制与数据】

- **工作原理（按文档给出的执行顺序）**：RecSDK 的 `tf.Session` 训练流程把"框架初始化 → 数据接入 → 优化器选择 → 稀疏表创建 → 计算图构建 → 变量拆分 → 训练循环（带评估与持久化）→ 资源释放"做成一个标准八步范式，并显式通过 `MODIFY_GRAPH_FLAG` 提供"改图模式"与"非改图模式"两条流水线启动路径。
- **数据流**：`tf.data.Dataset` → `get_asc_insert_func` 注入预处理（包含 Ascend 特征插入逻辑）→ `dataset.map(insert_fn)` → `prefetch(100)` → `make_initializable_iterator()` → `iterator.get_next()` 得到 `batch`；之后 `sparse_lookup(hash_table, feature, send_count, ..., batch=batch)` 完成 Embedding 查询 → `tf.reduce_sum(axis=1, keepdims=False)` → `MyModel(embedding_list, batch["label_0"], batch["label_1"])`。
- **变量持久化路径**：`./saved-model/sparse-model-{rank_id}-0` 用于判断是否已有可恢复的稀疏模型；恢复路径为 `./saved-model/model-{rank_id}-0`，保存路径为 `./saved-model/model-{rank_id}`，保存触发条件为 `global_step=0` 初始化保存、每 `SAVING_INTERVAL` 步保存、循环结束保存一次。
- **优化器分支机制（原文）**：`get_use_dynamic_expansion()` 返回 `True` 时使用按地址寻址的 `lazy_adam_by_addr`（`create_hash_optimizer_by_address`），否则使用 `lazy_adam`（`create_hash_optimizer`），二者均以 `cfg.learning_rate` 为学习率；密集优化器始终是 `tf.compat.v1.train.AdamOptimizer`。
- **启动训练的资源配置（原文）**：通过环境变量声明 Chief / Worker 的 IP 与端口，端口固定 `60000`，Chief device 固定 `0`，单进程 Worker 数量示例为 `8`；用户可自定义 `local_rank_size`，`CM_WORKER_SIZE = local_rank_size * 训练节点数`，并要求"自定义卡的数量 ≤ 容器（或进程）中可"（原文在此处被截断，剩余约束未给出）。

---

## 【表格解读】

**原文表 1：little_demo 文件说明**（逐字还原）

| 文件名 | 说明 |
|---|---|
| config.py | 模型相关配置。 |
| dataset.py | 数据集预处理。 |
| deterministic_loss | 确定性计算loss样例。 |
| main.py | 模型训练入口。 |
| model.py | 模型搭建。 |
| op_impl_mode.ini | 算子配置文件。 |
| optimizer.py | 优化器。 |
| random_data_generator.py | 数据集随机生成。 |
| README.md | demo模型运行说明。 |
| run_deterministic.sh | 运行确定性计算的脚本。 |
| run_model.py | 训练、推理流程封装。 |
| run.sh | 模型训练启动脚本。 |
| utils.py | 精度检测工具。 |

逐行解读：
- `config.py`：保存 `max_steps / TRAIN_STEPS / EVAL_STEPS / SAVE_STEPS / use_dynamic / use_dynamic_expansion / batch_number / learning_rate / user_vocab_size / item_vocab_size / user_hashtable_dim / item_hashtable_dim / ACCESS_AND_EVICT / MODIFY_GRAPH_FLAG` 等全部训练超参与开关。
- `dataset.py`：实现上文"步骤2"的 `get_asc_insert_func` 调用、`map(insert_fn)`、`prefetch(100)` 与 `make_initializable_iterator()`。
- `deterministic_loss`：确定性 loss 的实现样例，配合 `run_deterministic.sh` 使用，用于验证 Rec SDK 在确定性计算场景下的接口适配。
- `main.py`：八步调用链的承载文件，负责初始化框架、构建 train/eval 两份图、启动流水线、训练循环、Saver 持久化、`terminate_config_initializer()` 释放资源。
- `model.py`：承载 `MyModel`（前向网络），由 `model_forward` 在拿到 reduce 后的 embedding 后调用。
- `op_impl_mode.ini`：算子级配置文件，控制 Rec SDK / Ascend 相关算子运行模式。
- `optimizer.py`：实现 `get_dense_and_sparse_optimizer`，按 `use_dynamic_expansion` 二选一选择 `lazy_adam_by_addr` 或 `lazy_adam`，密集侧固定 AdamOptimizer。
- `random_data_generator.py`：当缺少真实数据时使用，随机生成训练样本。
- `README.md`：demo 的运行说明（不参与训练逻辑）。
- `run_deterministic.sh`：启动确定性计算 loss 的脚本入口。
- `run_model.py`：封装"训练 + 推理"完整流程，被 `main.py` / `run.sh` 调用。
- `run.sh`：模型训练启动脚本，文档环境变量章节明确"详细的配置环境变量的方法可参考 `little_demo/run.sh`"。
- `utils.py`：精度检测工具，用于评估 / 调试阶段的精度对齐。

---

## 【公式解读】

原文无 LaTeX / 伪代码公式。
（仅以代码片段形式给出参数化调用，例如 `init(max_steps, train_steps, eval_steps, save_steps, use_dynamic, use_dynamic_expansion)`，以及 `device_vocabulary_size = cfg.user_vocab_size * 10` 这类常量倍数设定，不属于"公式"范畴。）

---

## 【关联】

本篇文档处于"快速入门"位置，所有具体参数与行为都下钻到 `../05_api/` 目录的 API 参考；其内部链接构成上下游关系如下：

- **框架初始化 → 资源释放**：`init`（`../05_api/02_initialization_and_de_initialization_of_the_training_framework.md#init`，对应正文步骤 1）→ `terminate_config_initializer`（同目录 `#terminate_config_initializer`，对应正文步骤 8），构成"成对调用"。
- **数据流水线**：`get_asc_insert_func`（`../05_api/03_data_apis.md#get_asc_insert_func`，对应步骤 2）与 `modify_graph_and_start_emb_cache`（同目录 `#modify_graph_and_start_emb_cache`，对应步骤 7 的改图分支）属于同一数据 API 章节，分别承担"数据预处理"与"流水线启动"职责。
- **模型层（稀疏表 + Lookup）**：`create_table`、`sparse_lookup`、`get_dense_and_sparse_variable` 同属 `../05_api/04_model_apis.md`，分别对应步骤 4、5、6，是 RecSDK 推荐场景区别于普通 TF 训练的核心 API。
- **优化器**：`get_dense_and_sparse_optimizer` 中使用的 `create_hash_optimizer_by_address` / `create_hash_optimizer` 来自 `../05_api/07_optimizers_apis.md`，对应步骤 3。
- **改图模式**：`get_initializer`（`../05_api/05_automatic_graph_modification.md#get_initializer`）在步骤 7 改图分支被 `sess.run(get_initializer(True))` 调用，与 `modify_graph_and_start_emb_cache` 共同构成"自动图修改"能力。
- **模型持久化**：步骤 7 中使用的 `tf.compat.v1.train.Saver` 指向 `../05_api/10_tensorflow_apis.md#tfcompatv1trainsaversave`，属于 RecSDK 对原生 TF API 的兼容封装。

整体上，本篇文档是面向"`tf.Session` 风格训练"的总览入口；与之并列的还有面向 `Estimator` 风格的 `little_demo_estimator`（`run.sh` 链接中体现）。

---

## 【使用方法】

**启用方式 / 配置项 / 命令（仅基于原文整理）**

- **进入示例仓**：`https://gitcode.com/Ascend/RecSDK/tree/develop_examples_and_tools/examples/demo`（`little_demo` 存放路径）。
- **配置文件参考**：`https://gitcode.com/Ascend/RecSDK/blob/develop_examples_and_tools/examples/demo/little_demo_estimator/run.sh`（环境变量配置方法样例）。
- **环境变量（单机单卡 / 单机多卡启动训练，原文给出示例值）**：

  ```bash
  CM_CHIEF_IP={host_ip}
  CM_CHIEF_PORT=60000
  CM_CHIEF_DEVICE=0
  CM_WORKER_IP={host_ip}
  CM_WORKER_SIZE=8
  ```

- **多卡数量自定义（原文操作步骤 1）**：修改 `local_rank_size=`_自定义卡的数量_，并将 `CM_WORKER_SIZE = local_rank_size * 训练节点数`；并要求"自定义卡的数量 ≤ 容器（或进程）中可…"（原文此处被截断，剩余约束未给出）。
- **配置文件中关键开关**：通过 `MODIFY_GRAPH_FLAG` 切换"改图模式"与"非改图模式"。
- **训练主循环超参（来自 config.py）**：训练步数示例 `range(1, 201)`，评估触发 `TRAIN_INTERVAL`，模型保存触发 `SAVING_INTERVAL`。
- **保存 / 恢复路径模板**：`./saved-model/model-{rank_id}`（带 `global_step`）、存在性探测 `./saved-model/sparse-model-{rank_id}-0`。
- **确定性计算**：通过 `run_deterministic.sh` 配合 `determinetic_loss` 模块运行。
- **环境变量配置方法与说明**：参见 `../02_tf_installation_guide/recsdk_tf_installation_guide.md#配置环境变量`（由文档内部引用给出，原文未展开）。

> 注：原文"单机单卡和单机多卡训练"章节末尾在操作步骤 1 之后被截断，因此分布式多机训练、HCCL 集合通信配置、`rank_id` 来源、Estimator 风格 `little_demo_estimator` 的具体命令等，原文均未涉及。

## 图文联合解读

- `6-1快速入门.png`: **图解读：**

该流程图展示Rec SDK TensorFlow little_demo的三阶段调用链：①**适配模型**（init→get_asc_insert_func→create_hash_optimizer→create_table→sparse_lookup→get_dense_and_sparse_variable→start_asc_pipeline）；②**启动训练**（Session计算+启动任务）；③**完成训练**（查看结果→terminate_config_initializer释放资源）。

**技术结论：** 论证了稀疏推荐模型训练需按"框架初始化→数据集→优化器→稀疏表→计算图→稠密/稀疏变量→流水线"的固定顺序串联，且每步对应文档代码示例中的具体接口，末尾必须调用释放接口。

**与文档关系：** 图示与文档"接口调用介绍"一一对应，辅助读者理解main.py中各接口的调用先后与依赖关系。
- `8-3-5-视频解码.png`: # 图文联合解读

## 1) 图中内容
竖向流程图，5个蓝色矩形框自上而下用箭头串联：
①获取Rec SDK镜像并创建容器 → ②修改SSH配置并启动服务 → ③物理机配置免密登录 → ④配置little_demo → ⑤主节点拉起训练任务。

## 2) 技术结论
描绘了从环境准备到分布式训练启动的**完整部署链路**：先容器化交付，再构建SSH免密通信的多机互联基础，最后才进入代码配置与任务拉起阶段，强调前置环境依赖的严格顺序。

## 3) 与文档论点关系
文档主体聚焦 `little_demo` 的接口调用（init、get_asc_insert_func等），但该图补充了**运行前置条件**：分布式多机训练需完成镜像/容器、SSH免密等环境准备，是后续接口调用能正常运行的基础前提。
