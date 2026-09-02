# Quick Start

> 仓 `recsdk` · 路径 `docs/en/tensorflow/tf_rec_v2/quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/recsdk/docs/en/tensorflow/tf_rec_v2/quick_start.md

# 深度解读: docs/en/tensorflow/tf_rec_v2/quick_start.md

## 【定位】

本篇文档是 RecSDK TensorFlow (`tf_rec_v2`) 推荐 SDK 的**快速入门指南**, 通过 `little-demo` 代码样例, 系统化讲解基于 `tf.Session` 范式进行推荐模型训练所需的工程结构、关键接口调用链、环境变量前置条件与启动方式, 帮助开发者理解"如何用 SDK 串起稀疏表 → 前向图 → 优化器 → Session 保存"的端到端训练流程。

---

## 【技术要点】

1. **框架初始化**: 在 `main.py` 调用 `mxrec.init(params.path)`, 通过 TOML 配置路径完成训练框架初始化。
2. **稀疏表创建**: 在 `runner.py` 调用 `mxrec.get_embedding_table`, 可创建多个 (如 `user_table`、`item_table`), 关键参数包括 `name`、`dimension`、`device_vocabulary_size`、初始化器; 初始化器使用 `tf.truncated_normal_initializer(-0.01, 0.01, Config.random_seed)`。
3. **前向计算图**: 用 `mxrec.embedding_lookup(table, ids)` 做特征查表, 再通过 `tf.reduce_sum(embedding, axis=1, keepdims=False)` 在 `axis=1` 上聚合 embedding, 并将多个表的聚合结果汇入 `Model`。
4. **优化器**: 稀疏侧使用 `mxrec.AdamWOptimizer(learning_rate=Config.learning_rate)`; 稠密侧使用 `tf.compat.v1.train.AdamOptimizer`, 多卡场景下通过 `hccl_ops.allreduce(grad, "sum")` 做集合通信求和。
5. **梯度计算**: 稀疏梯度通过 `sparse_grads = tf.gradients(train_model.loss, sparse_embeddings)` 获得, 参数由 `mxrec.get_sparse_embedding()` 提供, 再交给 `sparse_optimizer.apply_gradients`。
7. **Session 与持久化**: 训练流中调用 `mxrec.get_init_hashtable_op()` 初始化哈希表, 然后通过 `tf.compat.v1.train.Saver()` 持久化稠密变量, 通过 `mxrec.EmbeddingTableSaver(mxrec.get_existing_tables())` 持久化稀疏 embedding 表。

---

## 【关键机制与数据】

- **工作原理 (流程)**: 原文给出的 6 步调用链:
  1. `mxrec.init` → 2. `mxrec.get_embedding_table` ×N → 3. `mxrec.embedding_lookup` + 自定义 Model → 4. 优化器定义 (稀疏 + 稠密) → 5. `mxrec.get_sparse_embedding` + `tf.gradients` + `apply_gradients` → 6. `EmbeddingTableSaver` 启动 Session 并保存。
- **稠密/稀疏分离优化机制**: 原文 `_get_train_ops` 显示稀疏优化与稠密优化并行存在, 二者共用同一个 `train_model.loss`; 多卡时稠密梯度经 `hccl_ops.allreduce` 求和 (`Config.rank_size > 1` 为门控条件)。
- **数据流**: `dataset.py` 生成数据 → `main.py` 经 `mxrec.init` 初始化框架 → `runner.py` 中构建两路迭代器 (`train_iterator`、`eval_iterator`)、两套模型 (`train_model`、`eval_model`) → `_train_and_evaluate` 内每 `self._train_interval` 步做一次评估并保存 checkpoint 与 embedding 表。
- **Session 启动顺序 (原文)**: 
  - `mxrec.get_init_hashtable_op()` → 初始化哈希表
  - `train_iterator.initializer` → 数据迭代器
  - `tf.compat.v1.global_variables_initializer()` → 全局变量
- **训练循环日志**: 每个 step 输出 `Training loss: %s.`, 达到训练末尾触发 `tf.errors.OutOfRangeError` 后退出循环。
- **性能数据**: 原文未给出任何数字化性能指标 (如吞吐、QPS、加速比), 仅给出训练流程本身; 评估指标数字也未在文档中量化。
- **环境变量**: 原文要求配置环境变量但未在此文档中列出具体变量名 (指引到 `recsdk_tf_installation_guide.md#configuring-environment-variables`)。

---

## 【表格解读】

**Table 1 — little-demo file description (原文逐字还原)**

| File             | Description                            |
|------------------|--------------------------------|
| config.py        | Training-related configurations                       |
| dataset.py       | Dataset generation                        |
| main.py          | Entry point for model training                       |
| model.py         | Model construction                         |
| op_precision.ini | Operator configuration file                       |
| runner.py        | Encapsulation of training and inference processes                    |
| logger.py        | Log encapsulation                         |
| demo.toml        | Rec SDK TensorFlow training framework and model configuration file|
| run.sh           | Startup script for model training                     |

**逐行解读**:
- `config.py`: 集中存放训练相关超参 (例如 `user_hashtable_dim`、`item_hashtable_dim`、`user_vocab_size`、`item_vocab_size`、`learning_rate`、`rank_size`、`ckpt_name`、`random_seed`), 是其它模块读取配置的唯一来源。
- `dataset.py`: 生成训练/评估数据, 提供 `batch.get(...)` 形式的特征与标签 (如 `Config.user_ids`、`Config.item_ids`、`Config.label_0`、`Config.label_1`)。
- `main.py`: 训练流程入口, 负责调用 `mxrec.init(params.path)` 加载 `demo.toml` 并启动训练框架。
- `model.py`: 封装 `Model` 类的 `__call__`, 接收 embedding 列表与标签, 输出 `loss` 等前向计算结果。
- `op_precision.ini`: 算子精度配置文件, 与昇腾 NPU 算子精度设定相关 (文档未给出条目细节)。
- `runner.py`: 训练与推理流程的封装核心, 包含本指南 6 步接口调用中的第 2–6 步, 是真正的"骨架代码"。
- `logger.py`: 日志封装, 在训练循环、评估、保存路径处统一调用 `logger.info`。
- `demo.toml`: RecSDK TensorFlow 训练框架与模型配置文件, 通过 `mxrec.init(params.path)` 加载。
- `run.sh`: 启动脚本, 同时也是环境变量配置范例 (链接到 gitcode 的 `run.sh`)。

---

## 【公式解读】

原文无数学公式, 也未给出任何伪代码/算式表达式。核心逻辑全部以 Python API 调用片段形式给出。  
→ **原文无公式**

---

## 【关联】

文档在 6 步接口介绍中分别交叉引用了以下内部链接, 形成 SDK 内部的方法依赖图:

- `./api/initialization_of_the_training_framework.md` ← 对应第 1 步 `mxrec.init` 的参数手册, 与 `main.py`/`demo.toml` 的加载机制关联。
- `./api/model_apis.md#get_embedding_table` ← 对应第 2 步 `mxrec.get_embedding_table` (稀疏表/稀疏网络层创建)。
- `./api/model_apis.md#embedding_lookup` ← 对应第 3 步 `mxrec.embedding_lookup` (稀疏查表与误差计算)。
- `./api/optimizers_apis.md` ← 对应第 4 步 `mxrec.AdamWOptimizer` 的优化器种类与参数说明。
- `./api/model_apis.md#get_sparse_embedding` ← 对应第 5 步 `mxrec.get_sparse_embedding` (取出稀疏参数用于计算梯度)。
- `./api/model_apis.md#embeddingtablesaver` ← 对应第 6 步 `mxrec.EmbeddingTableSaver` (稀疏表持久化)。
- `recsdk_tf_installation_guide.md#configuring-environment-variables` ← 单机单卡/单机多卡章节的前置条件指向, 与训练启动入口 (run.sh) 强耦合。

**上下游关系**: 本文档位于"使用层", 上游依赖 `installation_guide` 的环境变量配置, 下游覆盖 `tf.Session` 范式下从初始化→查表→优化→保存的完整训练生命周期, 是用户从零起步到能跑通 `little-demo` 的最短路径。

---

## 【使用方法】

**启用与启动 (原文整理)**:

1. **环境变量前置条件**: 必须先设置若干环境变量 (具体变量名未在本文档列出, 见 `recsdk_tf_installation_guide.md#configuring-environment-variables`); 文档给出的参考入口是 `https://gitcode.com/Ascend/RecSDK/blob/develop_examples_and_tools/tf_rec_v2_examples/little_demo/run.sh`。
2. **启动命令**: 在 `little-demo` 根目录下执行  
   ```bash
   bash run.sh
   ```
   训练完成后终端会显示 `Demo done.`。
3. **配置项**:
   - `demo.toml`: 训练框架与模型配置, 由 `mxrec.init(params.path)` 加载。
   - `op_precision.ini`: 算子精度配置。
   - `config.py`: Python 层超参, 包括 `user_hashtable_dim`、`item_hashtable_dim`、`user_vocab_size`、`item_vocab_size`、`learning_rate`、`rank_size`、`random_seed`、`ckpt_name`、特征字段名 (`user_ids`、`item_ids`、`label_0`、`label_1`) 等。
   - `mxrec.init` 的关键参数: `params.path` (指向 `demo.toml`)。
   - `mxrec.get_embedding_table` 关键参数: `name`、`dimension`、`device_vocabulary_size`、`initializer`。
   - `mxrec.AdamWOptimizer` 关键参数: `learning_rate`。
   - 多卡门控: `Config.rank_size > 1` 时启用 `hccl_ops.allreduce`。
   - 评估/保存频率: `self._train_interval`; 训练总步数: `self._train_steps`。
