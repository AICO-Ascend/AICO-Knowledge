# Quick Start

> 仓 `recsdk` · 路径 `docs/en/tensorflow/tf_rec_v1/quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/recsdk/docs/en/tensorflow/tf_rec_v1/quick_start.md

# 一体化深度解读:RecSDK TensorFlow quick_start.md

## 【定位】

这篇文档面向 **RecSDK TensorFlow (tf_rec_v1)** 的入门用户,以仓库内置示例工程 `little-demo` 为蓝本,逐文件、逐接口地说明**基于 `tf.Session` 风格**进行推荐模型训练所需要完成的代码改造与关键接口调用流程;文档本身不提供具体可训练模型,仅承担"接口适配参考模板"的职责。

---

## 【技术要点】

1. **范围与定位**:文档基于 `little-demo` (位于 gitcode Ascend/RecSDK 的 `develop_examples_and_tools/examples/demo` 分支) 演示 `tf.Session` 训练范式下的接口衔接;并明确 **不支持** `train_and_evaluate` 场景下的**多轮评估**(multi-round evaluation)。
2. **接口调用七步流程**(在 `main.py` / `model.py` / `optimizer.py` 间分工):
   - **Step 1 框架初始化** — 调用 `init(max_steps, train_steps, eval_steps, save_steps, use_dynamic, use_dynamic_expansion)`;注释提示 `nbatch` 函数需配合 `prefetch` 且 `host_vocabulary_size != 0` 使用。
   - **Step 2 数据集定义** — 调用 `get_asc_insert_func(tgt_key_specs=feature_spec_list, is_training=is_training, dump_graph=dump_graph)`,经 `dataset.map(insert_fn)` → `dataset.prefetch(100)` → `make_initializable_iterator()` → `iterator.get_next()`。
   - **Step 3 优化器定义** — 在 `optimizer.py` 中通过 `get_use_dynamic_expansion()` 判定后,二选一使用 `create_hash_optimizer_by_address` 或 `create_hash_optimizer`;稠密侧用 `tf.compat.v1.train.AdamOptimizer`。
   - **Step 4 创建稀疏表** — 调用 `create_table` 建立 `user_hashtable` 与 `item_hashtable` 两个哈希表,`key_dtype=tf.int64`,`device_vocabulary_size = cfg.user_vocab_size * 10`(item 表同理),`host_vocabulary_size=0`。
   - **Step 5 构建计算图** — `model_forward` 中按 `(feature, hash_table, send_count)` 三元组循环调用 `sparse_lookup`,并以 `tf.reduce_sum(embedding, axis=1, keepdims=False)` 聚合,再交给 `MyModel()`。
   - **Step 6 梯度与优化** — 通过 `get_dense_and_sparse_variable()` 拆分稠密/稀疏变量,分别在对应优化器上做训练;并分别构建 `train_iterator/train_model` 与 `eval_iterator/eval_model`。
   - **Step 7 启动数据通路** — 依据配置项 `MODIFY_GRAPH_FLAG` 二选一:`modify_graph_and_start_emb_cache(dump_graph=True)`(图改写模式)或 `start_asc_pipeline()`(非图改写模式);随后在 `tf.compat.v1.Session(config=sess_config(dump_data=False))` 内完成初始化、Saver 恢复/保存,并进入训练循环 `range(1, 201)`(共 **200 步**),每 `TRAIN_INTERVAL` 步累加 `EPOCH`;捕获 `tf.errors.OutOfRangeError` 用于终止。

---

## 【关键机制与数据】

- **图改写模式开关**:`MODIFY_GRAPH_FLAG` 在配置文件中决定是否走 `modify_graph_and_start_emb_cache` 分支;为 True 时 `sess.run(get_initializer(True))`,为 False 时 `sess.run(train_iterator.initializer)`。(原文:Step 7 代码段)
- **prefetch 缓冲**:`dataset.prefetch(100)`,表示数据通路预取 batch 数固定为 100。(原文:Step 2)
- **设备/Host 词表容量**:两个稀疏表均设置 `device_vocabulary_size = cfg.xxx_vocab_size * 10`、`host_vocabulary_size = 0`;注释中给出另一种配置 `cfg.user_vocab_size * 100`,用于 **h2d (host-to-device) 测试**。(原文:Step 4)
- **优化器分支**:`use_dynamic_expansion=True` → `create_hash_optimizer_by_address` (日志:"optimizer lazy_adam_by_addr");`False` → `create_hash_optimizer` (日志:"optimizer lazy_adam")。(原文:Step 3)
- **训练循环规模**:`for i in range(1, 201)` — 共 **200 个训练步**;`TRAIN_INTERVAL` 控制 `EPOCH` 自增节奏。(原文:Step 7)
- **Checkpoint 路径模板**:`./saved-model/model-{rank_id}` 与 `./saved-model/sparse-model-{rank_id}-%d`,结合 `saver.restore` / `saver.save(global_step=0)` 使用 `rank_id` 区分 rank。(原文:Step 7)
- **损失/异常**:训练入口执行 `sess.run([train_ops, train_model.loss_list])`;捕获 `tf.errors.OutOfRangeError` 终止当前 epoch。(原文:Step 7)
- **多轮评估限制**:`train_and_evaluate` 场景**不支持 multi-round evaluation**。(原文:Before You Start 顶部 NOTE)

---

## 【表格解读】

|File|Description|
|--|--|
|config.py|Model-related configurations|
|dataset.py|Dataset preprocessing|
|deterministic_loss|Example for deterministic loss calculation|
|main.py|Entry point for model training|
|model.py|Model construction|
|op_impl_mode.ini|Operator configuration file|
|optimizer.py|Optimizer|
|random_data_generator.py|Random dataset generation|
|README.md|Instructions for running the demo model|
|run_deterministic.sh|Script for running deterministic calculation|
|run_model.py|Encapsulation of training and inference processes|
|run.sh|Startup script for model training|
|utils.py|Accuracy detection tool|

**逐行解读**:

- `config.py`:集中存放模型超参与运行开关(如 `learning_rate`、`user/item_vocab_size`、`batch_number`、`MODIFY_GRAPH_FLAG` 等),被 `main.py` 等模块 `import cfg`。
- `dataset.py`:负责 dataset 预处理,对应 Step 2 中 `get_asc_insert_func` 的调用方。
- `deterministic_loss`:确定性(loss) 损失计算的示例模块,服务于 `run_deterministic.sh` 复现脚本。
- `main.py`:模型训练入口;Step 1/2/4/6/7 的接口调用均发生在此文件中。
- `model.py`:模型结构定义,Step 5 中 `MyModel`、`sparse_lookup` 嵌入汇聚逻辑在此实现。
- `op_impl_mode.ini`:算子配置文件,用于指定 RecSDK 算子实现模式(operator implementation mode),是 SDK 层面的环境/算子开关。
- `optimizer.py`:Step 3 中稠密/稀疏优化器(`AdamOptimizer` + `lazy_adam[_by_addr]`)的定义位置。
- `random_data_generator.py`:在无真实数据时生成随机数据,便于 demo 跑通。
- `README.md`:demo 工程的运行说明。
- `run_deterministic.sh`:执行确定性计算的脚本入口(配合 `deterministic_loss`)。
- `run_model.py`:把训练与推理流程二次封装,便于 `run.sh` 调用。
- `run.sh`:训练启动脚本。
- `utils.py`:精度检测工具(accuracy detection tool),用于评估/对比。

---

## 【公式解读】

**原文无公式**(文中仅包含 Python 函数调用、参数赋值与控制流代码,未出现 LaTeX 数学公式或伪代码形式的数学表达式)。

---

## 【关联】

依据文末内部链接,本 quick start 与下列 RecSDK tf_rec_v1 文档存在直接耦合:

- **框架初始化/去初始化**
  - [`init`](./api/initialization_and_deinitialization_of_the_training_framework.md#init) — Step 1 框架初始化接口说明,与 `max_steps/train_steps/eval_steps/save_steps/use_dynamic/use_dynamic_expansion` 参数对应。
  - [`terminate_config_initializer`](./api/initialization_and_deinitialization_of_the_training_framework.md#terminate_config_initializer) — 与 init 配对的去初始化/终止配置接口(用于训练结束或异常退出时回收资源)。
- **数据侧 API**
  - [`get_asc_insert_func`](./api/data_apis.md#get_asc_insert_func) — Step 2 dataset 预处理接口,负责将 RecSDK 数据通路插入到 `tf.data` 流水线中。
  - [`modify_graph_and_start_emb_cache`](./api/data_apis.md#modify_graph_and_start_emb_cache) — Step 7 图改写模式下的 emb cache 启动接口。
- **优化器 API**
  - [Optimizers](./api/optimizers_apis.md) — Step 3 中支持的优化器类型与参数说明,涵盖 `lazy_adam` / `lazy_adam_by_addr` 等哈希优化器。
- **模型侧 API**
  - [`create_table`](./api/model_apis.md#create_table) — Step 4 稀疏表(`user_hashtable`、`item_hashtable`)创建接口,定义 `key_dtype/dim/name/emb_initializer/device_vocabulary_size/host_vocabulary_size`。
  - [`sparse_lookup`](./api/model_apis.md#sparse_lookup) — Step 5 嵌入查找与误差计算接口,支持 `access_and_evict_config` 访问/驱逐策略。
  - [`get_dense_and_sparse_variable`](./api/model_apis.md#get_dense_and_sparse_variable) — Step 6 拆分稠密/稀疏变量接口。
- **环境配置**
  - [recsdk_tf_installation_guide.md#configuring-environment-variables](./recsdk_tf_installation_guide.md#configuring-environment-variables) — 在执行 `little-demo` 之前需完成的环境变量配置(出现两次,均指向安装指南的同一节)。

**与上下游模块的关系**:本指南处于"使用层",向下串联 `recsdk_tf_installation_guide.md`(环境准备),向上串联 `model_apis.md` / `data_apis.md` / `optimizers_apis.md` / `initialization_and_deinitialization_of_the_training_framework.md` 四个 API 参考文档。`little-demo` 自身作为一个参考模板,文档明确声明其 **仅供学习**,**不支持** 在其基础上适配自有模型。

---

## 【使用方法】

- **接口启用方式(原文已涉及)**:
  - 在 `main.py` 中调用 `init(...)` 完成框架初始化(Step 1)。
  - 在 `main.py` 中调用 `get_asc_insert_func(...)` 并把结果 `insert_fn` 经 `dataset.map` 串入数据流;随后 `prefetch(100)` 与 `make_initializable_iterator()` 取得 batch(Step 2)。
  - 在 `optimizer.py` 中通过 `get_dense_and_sparse_optimizer(cfg)` 同时返回稠密与稀疏优化器(Step 3)。
  - 在 `main.py` 中调用 `create_table(...)` 多次以构建多个稀疏表;每个表显式传入 `device_vocabulary_size` 与 `host_vocabulary_size`(Step 4)。
  - 在 `model.py` 中实现 `model_forward`,循环调用 `sparse_lookup(hash_table, feature, send_count, is_train=..., access_and_evict_config=..., name=..., modify_graph=..., batch=...)`,并以 `tf.reduce_sum(..., axis=1, keepdims=False)` 汇聚(Step 5)。
  - 在 `main.py` 中分别对 train / eval 构造 `iterator` 与 `model`,并通过 `get_dense_and_sparse_variable()` 获取稠密/稀疏变量以做梯度计算(Step 6)。
  - 在 `main.py` 中根据 `MODIFY_GRAPH_FLAG` 二选一调用 `modify_graph_and_start_emb_cache(dump_graph=True)` 或 `start_asc_pipeline()`,随后 `with tf.compat.v1.Session(config=sess_config(dump_data=False)) as sess` 启动训练循环 `range(1, 201)`;按 `TRAIN_INTERVAL` 自增 `EPOCH`,遇 `tf.errors.OutOfRangeError` 即跳出当前 epoch(Step 7)。
- **关键配置项(原文已涉及)**:
  - `MODIFY_GRAPH_FLAG`:控制是否启用图改写模式(True → `modify_graph_and_start_emb_cache`,False → `start_asc_pipeline`)。
  - `use_dynamic` / `use_dynamic_expansion`:传入 `init`,并影响 Step 3 中选择 `create_hash_optimizer_by_address` 还是 `create_hash_optimizer`。
  - `host_vocabulary_size`:Step 4 稀疏表参数;原文 demo 中置 0,注释提示另可设为 `cfg.user_vocab_size * 100` 用于 **h2d 测试**。
  - `device_vocabulary_size`:Step 4 设为 `cfg.xxx_vocab_size * 10`。
  - `prefetch(100)`:`dataset.prefetch(100)` 固定预取 batch 数。
  - `TRAIN_INTERVAL`:控制 epoch 自增节奏。
  - `rank_id`:Checkpoint 路径模板变量,影响 `./saved-model/model-{rank_id}` 与 `./saved-model/sparse-model-{rank_id}-%d` 的实际路径。
  - `op_impl_mode.ini`:算子实现模式配置文件,与代码工程同级管理。
- **运行环境(原文指向未展开)**:`recsdk_tf_installation_guide.md#configuring-environment-variables`(环境变量配置)需在使用前完成;`little-demo` 源码位于 [gitcode Ascend/RecSDK `develop_examples_and_tools/examples/demo`](https://gitcode.com/Ascend/RecSDK/tree/develop_examples_and_tools/examples/demo)。

## 图文联合解读

- `6-1-quick-start.png`: **图文联合解读：**

图示为Rec SDK `little-demo`基于`tf.Session`接口调用的三段式流程图：**Model adaptation**（init→数据集→优化器→创建稀疏表→构建计算图→梯度定义→启动数据管道）、**Training startup**（Session计算/启动训练任务）、**Training completion**（查看结果/关闭流），每步标注对应API（如`create_table`、`sparse_lookup`）。**技术结论：** 呈现了Sparse参数全生命周期管理接口的标准化调用顺序。**与文档关系：** 将文字描述的"关键接口适配"具象为可视化流程，便于开发者按图索骥完成模型迁移。
- `8-3-5-video-decoding.png`: **1) 图示内容**：五级纵向流程图，自上而下为：获取Rec SDK镜像→创建容器→修改SSH配置并启动服务→配置物理机免密登录→配置little_demo→在主节点启动训练任务，箭头串联，结构清晰。

**2) 技术结论**：展示了基于`little-demo`运行前的环境准备全流程，属于环境搭建类操作序列。

**3) 与文档关系**：图与下文"接口调用介绍"步骤1（初始化框架）衔接，将Quick Start中准备工作具象化，为后续`tf.Session`模型训练铺垫环境前提。
