# 教程 3：如何增加新数据集

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/video/R(2+1)D/docs_zh_CN/tutorials/3_new_dataset.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/video/R(2+1)D/docs_zh_CN/tutorials/3_new_dataset.md

# 教程 3：如何增加新数据集 — 一体化深度解读

## 【定位】

本教程解决**"如何把自定义视频/帧数据集接入 MMAction2 训练框架"**的问题——分别给出按已有三种标注格式重组数据（在线继承 / 本地转换两条路径），以及通过 `RepeatDataset` 包装器组合已有数据集两种方案，使新数据可在不修改核心 pipeline 的前提下投入训练与评测。

## 【技术要点】

1. **三种受支持的标注格式**——分别对应 `RawframeDataset`、`VideoDataset`、`ActivityNetDataset`：帧标注每行 `帧相对文件夹 总帧数 标签`；视频标注每行 `文件相对路径 标签`；ActivityNet 为键值化 JSON（含 `duration_second`、`duration_frame`、`annotations[].segment`、`label`、`feature_frame`、`fps`、`rfps` 字段）。
2. **两条接入路径**——「在线转换」需继承 [`BaseDataset`](/mmaction/datasets/base.py) 并重写三个抽象方法 `load_annotations(self)`、`evaluate(self, results, metrics, logger)`、`dump_results(self, results, out)`；「本地转换」则把标注文件转存为 pickle/json 后直接喂给上述三类数据集。
3. **数据集类的样板实现**——自定义 `MyDataset` 需通过 `@DATASETS.register_module()` 注册，`__init__` 中调用 `super().__init__(ann_file, pipeline, test_mode)`，并在 `load_annotations` 里按行解析 `annotation.txt`（示例格式：`文件夹,总帧数,类别`，图名模板 `img_{:05}.jpg`）。
4. **配置文件的注入点**——顶层声明 `dataset_type='RawframeDataset'`、`data_root`、`data_root_val`、`ann_file_train/val/test`（分别指向 `data/custom/custom_train_list.txt`、`data/custom/custom_val_list.txt`），再在 `data=dict(...)` 内为 `train/val/test` 三个子项各自指定 `type=dataset_type`。
5. **训练用 dataloader 关键超参**——原文档示例配置中 `videos_per_gpu=32`、`workers_per_gpu=4`，是新数据集配置中可直接保留的默认项。
6. **组合数据集的包装器**——`RepeatDataset` 通过 `times=N` 决定重复次数，内嵌 `dataset=dict(type='Dataset_A', ..., pipeline=train_pipeline)` 形成"包装 → 内层"两层配置结构。

## 【关键机制与数据】

- **数据流（在线转换）**：`annotation.txt` → `load_annotations()` 读取并解析为 `video_infos`（list of dict，含 `frame_dir` / `total_frames` / `label`）→ `prepare_train_frames(idx)` / `prepare_test_frames(idx)` 拷贝条目并注入 `filename_tmpl` → `self.pipeline(results)` 触发下游增强与采样。
- **数据流（本地转换）**：用户侧把任意格式转换为 `RawframeDataset` / `VideoDataset` / `ActivityNetDataset` 期望的 pickle/json 标注文件 → 直接复用现成 Dataset 类，无需自定义子类。
- **数据流（RepeatDataset）**：`RepeatDataset` 包装原数据集，在每个 epoch 内把 `dataset` 重复 `times` 次，从而放大单 epoch 样本数。
- **ActivityNet JSON 字段含义**（原文样例中的 `video1`）：`duration_second=211.53`、`duration_frame=6337`、`annotations[0].segment=[30.025882995319815, 205.2318595943838]`、`annotations[0].label="Rock climbing"`、`feature_frame=6336`、`fps=30.0`、`rfps=29.9579255898`；`video2` 同构，对应 `duration_second=26.75`、`duration_frame=647`、片段 `[2.578755070202808, 24.914101404056165]`、标签 `"Drinking beer"`、`feature_frame=624`、`fps=24.0`、`rfps=24.1869158879`。
- **性能/数值指标**：原文未提供任何训练/推理性能或精度数据。

## 【表格解读】

**原文无表格**。原文中出现的"帧标注示例""视频标注示例""ActivityNet 标注示例""`annotation.txt` 示例"以及两段配置/类定义代码块均为**代码块形式的配置/数据片段**，不构成 markdown 意义上的表格。

## 【公式解读】

**原文无公式**。文档未给出任何数学表达式或伪代码算法式。

## 【关联】

文档中显式链接了 MMAction2 数据集层的四个核心模块，构成本教程的"上游基类 + 三个现成实现"参照系：

- [`/mmaction/datasets/base.py`](/mmaction/datasets/base.py)：**BaseDataset 基类**，是自定义数据集和现有数据集类的共同父类，定义了 `__init__(ann_file, pipeline, test_mode)`、`video_infos`、`pipeline` 等共享状态，以及本教程要求重写的三个抽象方法 `load_annotations` / `evaluate` / `dump_results`。
- [`/mmaction/datasets/rawframe_dataset.py`](/mmaction/datasets/rawframe_dataset.py)：**RawframeDataset**，对应"帧标注（rawframe annotation）"格式；本文的"在线转换"和"自定义数据集示例（MyDataset）"都参照它实现，并且示例配置最终仍指向 `dataset_type='RawframeDataset'`。
- [`/mmaction/datasets/video_dataset.py`](/mmaction/datasets/video_dataset.py)：**VideoDataset**，对应"视频标注（video annotation）"格式，是本地转换路径下可直接复用的现成类。
- [`/mmaction/datasets/activitynet_dataset.py`](/mmaction/datasets/activitynet_dataset.py)：**ActivityNetDataset**，对应"ActivityNet 标注"JSON 格式，用于时序动作定位任务；同上，是本地转换路径下可直接复用的现成类。

此外，文档暗含与下游模块的关联：自定义 `MyDataset` 通过 `pipeline=train_pipeline` 接入既有数据增强流水线；配置中的 `videos_per_gpu=32`、`workers_per_gpu=4` 会被下游 dataloader 构建器消费；`RepeatDataset` 则作为"组合已有数据集"维度的横向扩展，与上述纵向的"继承 BaseDataset"路径正交。

## 【使用方法】

1. **按已有格式重组数据**：把自定义数据整理成帧/视频/ActivityNet 三种标注文件之一，每行（JSON 每键）格式严格遵循上文示例。
2. **在线转换（自定义类）**：
   - 在 `mmaction/datasets/my_dataset.py` 中新建继承 `BaseDataset` 的类，用 `@DATASETS.register_module()` 注册。
   - 实现 `load_annotations()` 解析 `ann_file`，返回 `video_infos`；实现 `prepare_train_frames(idx)` / `prepare_test_frames(idx)` 注入 `filename_tmpl` 等字段并调用 `self.pipeline(results)`；实现 `evaluate(results, metrics='top_k_accuracy', topk=(1, 5), logger=None)`。
   - 在配置中以 `dataset_A_train = dict(type='MyDataset', ann_file=ann_file_train, pipeline=train_pipeline)` 引用。
3. **本地转换**：将标注转储为 pickle/json，直接在配置中沿用 `RawframeDataset` / `VideoDataset` / `ActivityNetDataset` 三种现成 `dataset_type`。
4. **修改配置文件 `configs/task/method/my_custom_config.py`**：声明 `dataset_type='RawframeDataset'`、`data_root` / `data_root_val`、`ann_file_train` / `ann_file_val` / `ann_file_test`，并在 `data=dict(videos_per_gpu=32, workers_per_gpu=4, train=dict(type=dataset_type, ann_file=ann_file_train, ...), val=..., test=...)` 中挂载。
5. **重复数据集**：在配置中用 `dataset_A_train = dict(type='RepeatDataset', times=N, dataset=dict(type='Dataset_A', ..., pipeline=train_pipeline))`，将原数据集在每个 epoch 重复 `N` 次。
