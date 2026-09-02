# 快速入门<a name="ZH-CN_TOPIC_0000001580166524"></a>

> 仓 `recsdk` · 路径 `docs/zh/tensorflow/tf_rec_v2/03_quick_start/quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/recsdk/docs/zh/tensorflow/tf_rec_v2/03_quick_start/quick_start.md

# 文档深度解读：Rec SDK TensorFlow 快速入门

## 【定位】
这篇文档作为 Rec SDK TensorFlow（基于 tf.Session 编程范式）的快速入门指南，指导用户通过官方 little-demo 样例理解一个完整的模型训练任务所需要的文件结构、关键接口调用顺序以及训练启动方式，定位是"上手示例 + 接口串联导读"，而非可直接复用的训练工程。

---

## 【技术要点】

1. **little-demo 定位与边界**：文档明确指出 little-demo **只是一个代码示例**，用于演示调用接口的逻辑，不包含具体模型、不实现具体功能，**不支持用户在 little-demo 上适配自己的模型**。
2. **训练编程范式**：使用经典 `tf.Session`（tf.compat.v1 兼容模式），整个流程涉及 6 个关键接口：`init`、`get_embedding_table`、`embedding_lookup`、`get_sparse_embedding`、`EmbeddingTableSaver`，以及优化器 `AdamWOptimizer`。
3. **稀疏表（Embedding Table）建立**：示例中创建两张稀疏表 `user_table` 与 `item_table`，使用 `tf.truncated_normal_initializer(-0.01, 0.01, Config.random_seed)` 作为初始化器；表名、维度（`dimension`）、设备词表大小（`device_vocabulary_size`）均通过 `Config` 传入。
4. **前向计算图构建**：通过 `mxrec.embedding_lookup(table, ids)` 取 embedding 后使用 `tf.reduce_sum(embedding, axis=1, keepdims=False)` 在 axis=1 上做求和聚合，构造 `embedding_list` 后送入 `Model`。
5. **双优化器并存策略**：
   - 稠密参数：使用 `tf.compat.v1.train.AdamOptimizer(learning_rate=Config.learning_rate)`，从 `GraphKeys.TRAINABLE_VARIABLES` 集合取出。
   - 稀疏参数：使用 `mxrec.AdamWOptimizer(learning_rate=Config.learning_rate)`，通过 `mxrec.get_sparse_embedding()` 取得参数后用 `tf.gradients(train_model.loss, sparse_embeddings)` 求梯度。
6. **多卡梯度聚合**：当 `Config.rank_size > 1` 时，对每个稠密梯度调用 `hccl_ops.allreduce(grad, "sum")`（aggregation 方式为 `"sum"`），未传 `avg_grads.append` 的 None 梯度被跳过。
7. **训练与保存循环**：使用 `tf.compat.v1.train.Saver` 保存稠密 checkpoint，使用 `mxrec.EmbeddingTableSaver(mxrec.get_existing_tables())` 保存稀疏表；当 `(i + 1) % self._train_interval == 0` 时执行评估并保存模型。

---

## 【关键机制与数据】

### 数据流 / 调用顺序（原文信息汇总）
- 入口 `main.py` → `mxrec.init(params.path)` 初始化框架（参数路径指向 `demo.toml`）。
- `runner.py` → `mxrec.get_embedding_table` 建立稀疏网络层 → `mxrec.embedding_lookup` 查询特征 → 自定义 `Model` 类进行前向计算与 loss 计算。
- 训练循环内同时进行：
  - 稠密优化：`compute_gradients` → `hccl_ops.allreduce`（仅当 `Config.rank_size > 1`） → `apply_gradients`。
  - 稀疏优化：`mxrec.get_sparse_embedding()` → `tf.gradients` → `sparse_optimizer.apply_gradients`。
- 训练前需依次执行：`mxrec.get_init_hashtable_op()` → `train_iterator.initializer` → `tf.compat.v1.global_variables_initializer()`。
- 保存路径：`tf_save_path = os.path.join(saved_path, Config.ckpt_name)`；EmbeddingTableSaver 接收 `saved_path` 与 step `i + 1`。

### 性能 / 配置相关数据（原文有的部分）
- 训练步数：`for i in range(self._train_steps)`，**原文未给出 `_train_steps` 的具体数值**。
- 评估与保存触发：`(i + 1) % self._train_interval == 0`，**原文未给出 `_train_interval` 具体数值**。
- 训练结束标志：打印 `Demo done.` 字样。

### 异常处理（原文）
- `tf.errors.OutOfRangeError` 触发时打印 `"Encounter the end of Sequence for training."` 并 `break` 跳出训练循环。

---

## 【表格解读】

> **表 1 little-demo 文件说明**（逐字还原）

| 文件名              | 说明                             |
|------------------|--------------------------------|
| config.py        | 训练相关配置。                        |
| dataset.py       | 数据集生成。                         |
| main.py          | 模型训练入口。                        |
| model.py         | 模型搭建。                          |
| op_precision.ini | 算子配置文件。                        |
| runner.py        | 训练、推理流程封装。                     |
| logger.py        | 日志封装。                          |
| demo.toml        | Rec SDK TensorFlow训练框架和模型配置文件。 |
| run.sh           | 模型训练启动脚本。                      |

**逐行解读：**

| 文件名 | 解读 |
|---|---|
| `config.py` | 集中存放训练超参与结构参数（如 `user_hashtable_dim`、`item_hashtable_dim`、`user_vocab_size`、`item_vocab_size`、`learning_rate`、`rank_size`、`ckpt_name`、`random_seed`、`label_0`、`label_1`、`user_ids`、`item_ids` 等），是 `demo.toml` 与代码之间的桥梁。 |
| `dataset.py` | 负责训练样本的生成与封装，从文档接口调用看，它需要提供 `user_ids`、`item_ids`、`label_0`、`label_1` 四个字段对应的特征数据。 |
| `main.py` | 模型训练入口，唯一职责是调用 `mxrec.init(params.path)` 把 `demo.toml` 路径传给框架完成初始化。 |
| `model.py` | 模型搭建文件，定义 `Model` 类，接收 `embedding_list` 与两个 label，输出 `train_model.loss`（即前向 loss），是稠密网络部分的主要载体。 |
| `op_precision.ini` | 算子配置文件，控制 Rec SDK 算子（主要是 sparse 算子）的运行精度策略。 |
| `runner.py` | 整个 demo 的核心，封装了"稀疏表创建 → embedding_lookup → 前向图构建 → 优化器定义 → 梯度计算（含多卡 allreduce） → Session 训练与评估 → EmbeddingTableSaver/ Saver 保存"的全流程。 |
| `logger.py` | 日志封装模块，统一 `logger.info` 的日志格式（如 `"Training loss: %s."`、`"The saved path: %s."`）。 |
| `demo.toml` | Rec SDK TensorFlow 训练框架 + 模型的配置文件，被 `mxrec.init` 加载，决定框架运行行为与模型结构配置。 |
| `run.sh` | 训练启动脚本，负责设置环境变量（单机单卡 / 单机多卡所需的环境变量），再调用 `bash run.sh` 启动训练。 |

---

## 【公式解读】

**原文无公式。**

本文档以 Python 代码片段 + 表格 + 启动命令说明为主，未出现任何 LaTeX 数学公式或伪代码形式的数学表达式。涉及"求和/聚合"的语义通过 `tf.reduce_sum(embedding, axis=1, keepdims=False)` 这一 TensorFlow API 调用体现，并非形式化公式。

---

## 【关联】

本文档作为"调用串联导读"，把 6 个核心接口与 1 个配置文件章节串联起来，对应内部链接如下：

| 接口 / 章节 | 对应内部链接 | 在本文档中的位置 |
|---|---|---|
| `init`（框架初始化） | `../05_api/02_initialization_of_the_training_framework.md#init` | 第 1 步：`mxrec.init(params.path)` |
| `get_embedding_table`（建立稀疏表） | `../05_api/03_model_apis.md#get_embedding_table` | 第 2 步：建立 `user_table` / `item_table` |
| `embedding_lookup`（特征查询） | `../05_api/03_model_apis.md#embedding_lookup` | 第 3 步：前向计算图构建 |
| 优化器接口（`AdamWOptimizer` 等） | `../05_api/04_optimizers_apis.md` | 第 4 步：定义稀疏优化器 |
| `get_sparse_embedding`（取稀疏参数） | `../05_api/03_model_apis.md#get_sparse_embedding` | 第 5 步：稀疏梯度计算 |
| `EmbeddingTableSaver`（保存稀疏表） | `../05_api/03_model_apis.md#embeddingtablesaver` | 第 6 步：训练中保存模型 |
| 环境变量配置（单机单卡 / 单机多卡） | `../02_tf_installation_guide/recsdk_tf_installation_guide.md#配置环境变量` | 启动训练小节前提条件 |

**上下游关系：**
- 上游（依赖）：安装章节 → 环境变量配置 → `demo.toml` 准备 → `mxrec.init`。
- 中游（建模）：`get_embedding_table` → `embedding_lookup` → `Model` 前向 → `compute_gradients / tf.gradients`。
- 下游（产出）：`Saver` + `EmbeddingTableSaver` → checkpoint + 稀疏表文件；评估在训练循环内周期性触发。

---

## 【使用方法】

### 启动方式（原文）
- 在 little-demo 目录下执行：
  ```bash
  bash run.sh
  ```
- 训练结束标志：日志打印 `Demo done.` 字样。

### 环境变量（原文表述）
- 原文**未在本节列出具体的环境变量名与取值**，仅给出两类指引：
  1. 详细的环境变量配置方法参考 [little-demo 的启动脚本](https://gitcode.com/Ascend/RecSDK/blob/develop_examples_and_tools/tf_rec_v2_examples/little_demo/run.sh)。
  2. 环境变量的说明参见 [配置环境变量](../02_tf_installation_guide/recsdk_tf_installation_guide.md#配置环境变量)。

### 配置项（原文有则写）
- 训练框架与模型配置：通过 `demo.toml` 文件提供，由 `mxrec.init(params.path)` 加载（**原文未列出 `demo.toml` 的具体字段**）。
- 训练超参与结构参数：通过 `config.py` 提供，包括但不限于：`user_hashtable_dim`、`item_hashtable_dim`、`user_vocab_size`、`item_vocab_size`、`learning_rate`、`rank_size`、`ckpt_name`、`random_seed`（**具体数值未在原文给出**）。
- 算子精度配置：通过 `op_precision.ini` 文件提供（**原文未列出具体算子精度项**）。
