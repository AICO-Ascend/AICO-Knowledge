# 教程 3: 自定义数据预处理流程

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/autonoumous_driving/BEVDet_for_PyTorch/docs/zh_cn/tutorials/data_pipeline.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/autonoumous_driving/BEVDet_for_PyTorch/docs/zh_cn/tutorials/data_pipeline.md

# 一体化深度解读: 教程 3: 自定义数据预处理流程

---

## 【定位】

本文档是 BEVDet/PointPillars 系列教程的第 3 篇, 系统阐述如何在 OpenMMLab 体系下设计与扩展 3D 目标检测的数据预处理 (Data Pipeline) 流程, 通过将"数据集"与"预处理流程"解耦, 并提供基于 PointPillars 的 train/test pipeline 完整示例以及自定义 Pipeline 扩展的三步流程, 让用户能够按需插入新的数据变换节点。

---

## 【技术要点】

1. **数据加载基座**: 使用 PyTorch 的 `Dataset` + `DataLoader` 进行多进程加载; 由于 3D 检测中数据尺寸可变 (点云点数、bbox 尺寸等), 引入 MMCV 的 `DataContainer` 类型来收集/分发不同尺寸的数据。
2. **Pipeline 与 Dataset 解耦**: 数据集负责处理标注信息, 预处理流程负责生成送入模型前向传播的字典 (dict) 数据项; 流程中每个操作接收一个字典, 输出一个新字典, 串联形成 pipeline。
3. **Pipeline 操作四分类**: 数据加载 (Load*) / 预处理 (Pre-processing) / 格式化 (Format) / 测试时的数据增强 (Test-time augmentation), 蓝色框表示操作节点, 绿色键表示新添加, 橙色键表示更新。
4. **PointPillars 训练 pipeline 关键参数**: `LoadPointsFromFile` 的 `load_dim=5, use_dim=5`; `LoadPointsFromMultiSweeps` 的 `sweeps_num=10`; `GlobalRotScaleTrans` 的 `rot_range=[-0.3925, 0.3925]`、`scale_ratio_range=[0.95, 1.05]`、`translation_std=[0, 0, 0]`; `RandomFlip3D` 的 `flip_ratio_bev_horizontal=0.5`。
5. **PointPillars 测试 pipeline 关键参数**: 包裹在 `MultiScaleFlipAug` 中的 `img_scale=(1333, 800)`、`pts_scale_ratio=1.0`、三种 `flip` 标志默认全 False, 内部 transforms 中 `GlobalRotScaleTrans` 的 `rot_range=[0, 0]`、`scale_ratio_range=[1., 1.]` 表示测试时不施加随机旋转与缩放。
6. **自定义 Pipeline 扩展三步法**: ① 在任意文件中以 `@PIPELINES.register_module()` 装饰器注册新变换类 (`__call__(self, results)` 接受并返回字典); ② 在构建处 `from .my_pipeline import MyTransform` 导入; ③ 在配置文件的 `train_pipeline` 列表中以 `dict(type='MyTransform')` 插入新节点, 插入位置示例为 `ObjectNameFilter` 与 `PointShuffle` 之间。

---

## 【关键机制与数据】

### 工作原理与数据流

- **字典 (dict) 数据流模型**: 整个 pipeline 由若干顺序执行的操作组成, 每个操作以字典为输入/输出, 沿数据流累积/更新键值。文档原图 `resources/data_pipeline.png` 展示了这一经典流程 (蓝色框=操作, 绿色键=新增, 橙色键=更新)。
- **训练流程逐节点 I/O** (原文给出):
  - `LoadPointsFromFile` → 添加 `points`
  - `LoadPointsFromMultiSweeps` → 更新 `points` (累计多帧扫描)
  - `LoadAnnotations3D` → 添加 `gt_bboxes_3d, gt_labels_3d, gt_bboxes, gt_labels, pts_instance_mask, pts_semantic_mask, bbox3d_fields, pts_mask_fields, pts_seg_fields` (`with_bbox_3d=True, with_label_3d=True`)
  - `GlobalRotScaleTrans` → 添加 `pcd_trans, pcd_rotation, pcd_scale_factor`, 更新 `points, *bbox3d_fields`
  - `RandomFlip3D` → 添加 `flip, pcd_horizontal_flip, pcd_vertical_flip`, 更新 `points, *bbox3d_fields`
  - `PointsRangeFilter` → 更新 `points` (按 `point_cloud_range` 裁剪)
  - `ObjectRangeFilter` → 更新 `gt_bboxes_3d, gt_labels_3d`
  - `ObjectNameFilter` → 更新 `gt_bboxes_3d, gt_labels_3d` (按 `classes=class_names` 过滤)
  - `PointShuffle` → 更新 `points` (打乱顺序)
  - `DefaultFormatBundle3D` → 更新 `points, gt_bboxes_3d, gt_labels_3d, gt_bboxes, gt_labels` (转换为统一张量/数组格式)
  - `Collect3D` → 添加 `img_meta` (由 `meta_keys` 指定的键值聚合而成), 移除除 `keys=['points', 'gt_bboxes_3d', 'gt_labels_3d']` 之外的所有键值
- **测试流程逐节点 I/O** (原文给出):
  - 测试时主体加载阶段与训练一致 (同样调用 `LoadPointsFromFile`、`LoadPointsFromMultiSweeps`), 随后由 `MultiScaleFlipAug` 包裹一组确定性 (`rot_range=[0,0]`, `scale_ratio_range=[1., 1.]`) 的 transforms, 其更新 `scale, pcd_scale_factor, flip, flip_direction, pcd_horizontal_flip, pcd_vertical_flip` 等与增强参数对应的数据列表。

### 性能/数值数据

- 原文未提供任何吞吐量、mAP、时延等性能基准数字; 仅给出 **配置型参数** (上述技术要点 4、5 中所列的旋转范围、缩放比、扫描帧数、BEV 翻转概率、图像尺度等), 均为示例配置而非性能数据。

---

## 【表格解读】

**原文无表格**。原文以 Python 字典列表 (`train_pipeline` / `test_pipeline`) 形式给出 pipeline 配置, 并以文字形式列举每项操作对字典键的增/改/删影响, 未使用任何 markdown 表格。

---

## 【公式解读】

**原文无公式**。文档未出现任何 LaTeX 公式或伪代码公式; 数据增强参数以 Python 列表/元组形式直接给出 (如 `rot_range=[-0.3925, 0.3925]`、`scale_ratio_range=[0.95, 1.05]`、`translation_std=[0, 0, 0]`、`img_scale=(1333, 800)`、`pts_scale_ratio=1.0`), 这些是配置常量而非符号化公式。

---

## 【关联】

- **DataContainer (上游基础组件)**: 文档第 1 段即指出 `DataContainer` 是 MMCV 中为解决 3D 检测数据尺寸不一而引入的容器类型, 用于在多进程 DataLoader 中收集和分发不同尺寸的数据; 详细实现参见文末提供的外部链接 `https://github.com/open-mmlab/mmcv/blob/master/mmcv/parallel/data_container.py`。
- **Dataset 模块**: 文档强调 pipeline 与 Dataset 的解耦关系 —— Dataset 负责标注信息的处理, pipeline 负责生成模型前向所需的字典; 二者共同构成 3D 检测训练的数据入口。
- **模型前向传播**: pipeline 最终输出的字典 (主要由 `Collect3D` 收束为 `points, gt_bboxes_3d, gt_labels_3d, img_meta`) 直接作为模型 forward 的输入参数来源。
- **配置文件体系**: 自定义 pipeline 的接入点在配置文件 (`train_pipeline` 列表), 通过 `dict(type='MyTransform')` 形式与配置驱动的训练框架衔接; 训练与测试 pipeline 共用同一组 `Load*` 操作, 但测试流程额外以 `MultiScaleFlipAug` 包裹确定性 transforms。
- **mmdet.datasets.PIPELINES 注册器**: 自定义变换类通过 `@PIPELINES.register_module()` 装饰器接入, 依赖 mmdet 的注册器机制识别 `type='MyTransform'` 字符串。

> 备注: 用户提供的元信息中标注"内部链接: (无)", 即本文档未包含仓库内部的相互引用链接, 仅有一个指向 MMCV 仓库的外部链接。

---

## 【使用方法】

### 扩展自定义 Pipeline 操作 (原文给出的三步流程)

1. **编写变换类**: 在任意文件 (如 `my_pipeline.py`) 中定义输入/输出均为字典的类, 并用 `@PIPELINES.register_module()` 注册:

   ```python
   from mmdet.datasets import PIPELINES

   @PIPELINES.register_module()
   class MyTransform:
       def __call__(self, results):
           results['dummy'] = True
           return results
   ```

2. **导入类**: 在构建 pipeline 的文件中导入, `from .my_pipeline import MyTransform`。

3. **在配置文件中插入**: 在 `train_pipeline` 列表中以 `dict(type='MyTransform')` 的形式加入, 插入位置示例为 `ObjectNameFilter` 之后、`PointShuffle` 之前:

   ```python
   train_pipeline = [
       dict(type='LoadPointsFromFile', load_dim=5, use_dim=5, file_client_args=file_client_args),
       dict(type='LoadPointsFromMultiSweeps', sweeps_num=10, file_client_args=file_client_args),
       dict(type='LoadAnnotations3D', with_bbox_3d=True, with_label_3d=True),
       dict(type='GlobalRotScaleTrans',
            rot_range=[-0.3925, 0.3925],
            scale_ratio_range=[0.95, 1.05],
            translation_std=[0, 0, 0]),
       dict(type='RandomFlip3D', flip_ratio_bev_horizontal=0.5),
       dict(type='PointsRangeFilter', point_cloud_range=point_cloud_range),
       dict(type='ObjectRangeFilter', point_cloud_range=point_cloud_range),
       dict(type='ObjectNameFilter', classes=class_names),
       dict(type='MyTransform'),       # ← 插入的自定义节点
       dict(type='PointShuffle'),
       dict(type='DefaultFormatBundle3D', class_names=class_names),
       dict(type='Collect3D', keys=['points', 'gt_bboxes_3d', 'gt_labels_3d'])
   ]
   ```

### 启用 / 运行命令

- 原文未给出具体的命令行启动方式 (如 `python tools/train.py ...` 等); 文档聚焦于 pipeline 的设计与扩展方法本身, 启动与训练细节属于上层教程内容, 本文中 **原文未涉及**。
