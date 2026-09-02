# Tutorial 3: Adding New Dataset

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/video/R(2+1)D/docs/tutorials/3_new_dataset.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/video/R(2+1)D/docs/tutorials/3_new_dataset.md

# 深度解读:Tutorial 3: Adding New Dataset

## 【定位】
这篇文档是 mmaction2 (本仓库为 R(2+1)D 视频分类模型) 的第三篇教程,介绍如何将**自定义数据集接入训练流程**的两种路径——按已有标注格式"重整数据",以及通过"复用+包裹"方式在训练时**混合/重复数据集**。

---

## 【技术要点】

1. **三种已有标注格式**:
   - **rawframe annotation**:文本文件,每行 `frame_directory total_frames label`,空格分隔。
   - **video annotation**:文本文件,每行 `filepath label`,空格分隔。
   - **ActivityNet annotation**:json 文件,key 为视频名,value 含 `duration_second`、`duration_frame`、`annotations` (含 `segment`、`label`)、`feature_frame`、`fps`、`rfps` 等字段。

2. **两种接入方式**:
   - **online conversion**:继承 [BaseDataset](/mmaction/datasets/base.py),覆写 `load_annotations(self)`、`evaluate(self, results, metrics, logger)`、`dump_results(self, results, out)` 三个方法。可参考 [RawframeDataset](/mmaction/datasets/rawframe_dataset.py)、[VideoDataset](/mmaction/datasets/video_dataset.py) 或 [ActivityNetDataset](/mmaction/datasets/activitynet_dataset.py)。
   - **offline conversion**:把标注预处理成 pickle 或 json,直接使用 `RawframeDataset`、`VideoDataset` 或 `ActivityNetDataset`。

3. **Rawframe 配置示例** (`configs/task/method/my_custom_config.py`):
   - `dataset_type = 'RawframeDataset'`
   - `data_root = 'path/to/your/root'`
   - `data_root_val = 'path/to/your/root_val'`
   - `ann_file_train = 'data/custom/custom_train_list.txt'`
   - `ann_file_val = 'data/custom/custom_val_list.txt'`
   - `ann_file_test = 'data/custom/custom_val_list.txt'`
   - `videos_per_gpu=32`、`workers_per_gpu=4`
   - 在 `data` dict 中分别给 `train/val/test` 三项指定 `type=dataset_type` 与对应 `ann_file`。

4. **自定义数据集类 `MyDataset`** (放于 `mmaction/datasets/my_dataset.py`):
   - 继承 `BaseDataset`,用 `@DATASETS.register_module()` 注册。
   - 构造参数:`ann_file, pipeline, data_prefix=None, test_mode=False, filename_tmpl='img_{:05}.jpg'`。
   - `load_annotations()` 跳过首行表头 (`directory,total frames,class`),按逗号切分 `frame_dir, total_frames, label`,若 `data_prefix` 非空则用 `osp.join` 拼接前缀。
   - `prepare_train_frames(idx)` 与 `prepare_test_frames(idx)` 均复制 `self.video_infos[idx]`,注入 `filename_tmpl`,再交给 `self.pipeline`。
   - `evaluate(self, results, metrics='top_k_accuracy', topk=(1, 5), logger=None)` 在示例中以 `pass` 占位。
   - 配置调用:`dataset_A_train = dict(type='MyDataset', ann_file=ann_file_train, pipeline=train_pipeline)`。

5. **数据集混合:RepeatDataset**:
   - 用 `RepeatDataset` 作为外层 wrapper,通过 `times=N` 控制重复次数。
   - 原始数据集配置嵌套在 `dataset=dict(...)` 中,`pipeline=train_pipeline` 等参数继续保留。

6. **自定义数据原始标注示例** (`annotation.txt`,逗号分隔,带表头):
   ```
   directory,total frames,class
   D32_1gwq35E,299,66
   -G-5CJ0JkKY,249,254
   T4h1bvOd9DA,299,33
   4uZ27ivBl00,299,341
   0LfESFkfBSw,249,186
   -YIsNpBEx6c,299,169
   ```

---

## 【关键机制与数据】

- **数据流 (offline + rawframe)**:用户先把原始数据组织成 rawframe 标注 → 在 config 中以 `RawframeDataset` 类型加载 `ann_file_*` → `DataLoader` 按 `videos_per_gpu=32`、`workers_per_gpu=4` 取样 → 走 `train_pipeline` 进行解码、增强与模型前向。
- **数据流 (online 自定义)**:用户实现 `MyDataset` → 在 config 中 `type='MyDataset'` → 训练时 `__getitem__` 触发 `prepare_train_frames` → `pipeline` 拿到含 `frame_dir / total_frames / label / filename_tmpl` 的 dict 完成后续处理。
- **ActivityNet 字段语义** (原文给出两个例子):
  - video1:`duration_second=211.53`、`duration_frame=6337`、`feature_frame=6336`、`fps=30.0`、`rfps=29.9579255898`;segment ≈ [30.03, 205.23],label="Rock climbing"。
  - video2:`duration_second=26.75`、`duration_frame=647`、`feature_frame=624`、`fps=24.0`、`rfps=24.1869158879`;segment ≈ [2.58, 24.91],label="Drinking beer"。
- **混合数据集机制**:`RepeatDataset` 仅在采样层把同一索引重复 `times` 次,因此下游 pipeline 不感知"重复",可与单数据集训练共用同一套 `train_pipeline`。

---

## 【表格解读】

原文无表格。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- 文档显式引用 [BaseDataset](/mmaction/datasets/base.py) 作为**所有自定义数据集的基类**,`MyDataset` 通过 `from .base import BaseDataset` 直接继承,沿用其 `ann_file / pipeline / test_mode` 初始化约定,并依赖 `self.video_infos` 与 `self.pipeline` 完成取样与预处理。
- 文档将 [RawframeDataset](/mmaction/datasets/rawframe_dataset.py)、[VideoDataset](/mmaction/datasets/video_dataset.py)、[ActivityNetDataset](/mmaction/datasets/activitynet_dataset.py) 三个类作为**在线/离线接入的参考实现**,分别对应 rawframe、video、ActivityNet 三种标注格式。`MyDataset` 示例的写法 (`load_annotations` 返回 `frame_dir / total_frames / label` 的 `video_infos` 列表、`prepare_train_frames` 注入 `filename_tmpl`) 与 `RawframeDataset` 的数据契约高度一致,表明它是 rawframe 路径下的最小可改造模板。
- **`RepeatDataset`** 未在链接列表中给出源码路径,但文档说明它是上层 wrapper,内嵌 `dataset=dict(...)` 复用原始数据集配置,可与上述任一 `Dataset` 组合,从而实现"重复采样"。

---

## 【使用方法】

- **离线复用 RawframeDataset**:
  ```python
  dataset_type = 'RawframeDataset'
  data_root = 'path/to/your/root'
  data_root_val = 'path/to/your/root_val'
  ann_file_train = 'data/custom/custom_train_list.txt'
  ann_file_val = 'data/custom/custom_val_list.txt'
  ann_file_test = 'data/custom/custom_val_list.txt'

  data = dict(
      videos_per_gpu=32,
      workers_per_gpu=4,
      train=dict(type=dataset_type, ann_file=ann_file_train, ...),
      val=dict(type=dataset_type, ann_file=ann_file_val, ...),
      test=dict(type=dataset_type, ann_file=ann_file_test, ...))
  ```

- **在线自定义 (逗号分隔 + `img_{:05}.jpg` 文件名模板)**:
  - 在 `mmaction/datasets/my_dataset.py` 中按原文给出的 `MyDataset` 实现(继承 `BaseDataset`,注册 `@DATASETS.register_module()`)。
  - 在 config 中:
    ```python
    dataset_A_train = dict(
        type='MyDataset',
        ann_file=ann_file_train,
        pipeline=train_pipeline
    )
    ```

- **重复数据集** (以 `Dataset_A` 为例,重复 N 次):
  ```python
  dataset_A_train = dict(
      type='RepeatDataset',
      times=N,
      dataset=dict(
          type='Dataset_A',
          ...,
          pipeline=train_pipeline
      )
  )
  ```

> 注:具体的 config 完整字段、数据预处理细节、文件命名约定与最终注册生效方式(如 `custom_imports` / `setup.py`)在原文中未涉及,需参考仓库其他文档/代码。
