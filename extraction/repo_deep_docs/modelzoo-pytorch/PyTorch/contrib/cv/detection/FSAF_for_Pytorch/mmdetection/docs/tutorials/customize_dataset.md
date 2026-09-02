# Tutorial 2: Customize Datasets

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/FSAF_for_Pytorch/mmdetection/docs/tutorials/customize_dataset.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/FSAF_for_Pytorch/mmdetection/docs/tutorials/customize_dataset.md

# 深度解读:Tutorial 2: Customize Datasets

## 【定位】

本文是 MMDetection 自定义数据集的官方教程,系统化地描述了当用户拥有**非标准格式数据集**(既不是 COCO 也不是 PASCAL VOC)时,如何将其接入 MMDetection 训练管线进行目标检测/实例分割训练的完整能力。

---

## 【技术要点】

1. **两种数据接入路径**(原文明确给出):(a) 把新数据**重整(reorganize)为已有格式**(COCO 或 PASCAL VOC);(b) 把新数据**重整为 MMDetection 的中间格式(middle format)**,通过自定义 `Dataset` 类或离线转换脚本实现。
2. **COCO 格式 JSON 的三个必备键**:`images`(含 `file_name`/`height`/`width`/`id`)、`annotations`(每张实例标注)、`categories`(类别名 + ID)。原文对每个字段都给出了真实示例值。
3. **配置文件双重覆盖**(原文给出具体配置块):(i) 在 `data.train` / `data.val` / `data.test` 中**显式**添加 `classes` 字段;(ii) 在 `model.roi_head.bbox_head`、`model.roi_head.mask_head` 等**显式**覆盖 `num_classes`(原文示例从 COCO 默认 **80** 覆盖为 **5**)。
4. **MMDetection 中间格式**:数据集标注是 `list[dict]`,每个 dict 对应一张图,字段包括 `filename`(相对路径)、`width`、`height`,训练时额外需要 `ann` 字典(含 `bboxes` shape `(n,4)` float32 与 `labels` shape `(n,)` int64);还有 `bboxes_ignore` 与 `labels_ignore` 用于处理 crowd/difficult/ignored 框。
5. **两种自定义实现方式**:在线转换(`CustomDataset` 子类,覆写 `load_annotations` 和 `get_ann_info`,参考 `CocoDataset`/`VOCDataset`);离线转换(把标注转成 pickle/json,直接用 `CustomDataset`)。
6. **三类一致性校验**(原文强制要求):`categories` 长度 = 配置中 `classes` 元组长度;`categories[].name` 与配置 `classes` 元素**完全一致**;`annotations[].category_id` 必须全部落在 `categories[].id` 集合内。MMDetection 会自动把 `categories` 中**不连续**的 id 映射为**连续**的 label 索引,因此 `name` 的字符串顺序决定 label 索引顺序,也决定可视化时 bbox 上的类别文本。

---

## 【关键机制与数据】

**工作原理 — 标注 ID 到 label 索引的映射**:MMDetection 内部按 `categories[].name` 在原 JSON 中出现的字符串顺序分配 0-based 连续索引(原文:"MMDetection automatically maps the uncontinuous `id` to the continuous label indices")。因此即使原标注 `id` 是离散值(如示例中 `1, 3, 4, 16, 17`),模型实际训练的类别编号依然按 `name` 出现顺序排成 `a→0, b→1, c→2, d→3, e→4`。可视化的类别文本同样来自 config 中 `classes` 的字符串顺序。

**数据流(以 COCO 重整路径为例)**:
1. 离线脚本将原始标注 → COCO 格式 JSON;
2. 在 config 中通过 `_base_` 继承基础配置(如 `cascade_mask_rcnn_r50_fpn_1x_coco.py`),仅覆写 `dataset_type='CocoDataset'`、`classes` 元组以及 `train/val/test` 的 `ann_file`、`img_prefix`;
3. 通过 `model.roi_head.bbox_head[i].num_classes` 与 `model.roi_head.mask_head.num_classes` 同步覆盖到自定义类别数(示例 5);
4. 训练时数据加载器读取 COCO JSON → 内部 `CocoDataset` 按 `classes` 顺序重映射 `category_id` → 连续 label → 送入检测/分割 head。

**原文给出的具体数据值**:
- bbox 示例:`[192.81, 224.8, 74.73, 33.43]`,area `1035.749`,image_id `1268`,annotation_id `42986`,category_id `16`;
- 类别总数:**5**(从默认 COCO **80** 覆盖);
- 中间格式图像示例:`width=1280, height=720`;
- 自定义文本标注示例中,`000001.jpg` 包含 2 个目标,`000002.jpg` 包含 3 个目标,每行 `x y w h class_id`。

**性能/精度数据**:原文未给出任何指标数字。

---

## 【表格解读】

原文无表格。

---

## 【公式解读】

原文无公式。

---

## 【关联】

**官方代码/文档引用(原文给出的外部链接)**:
- `mmdet/datasets/coco.py`(`CocoDataset` 实现,作为在线转换的范例)
- `mmdet/datasets/voc.py`(`VOCDataset` 实现)
- `tools/dataset_converters/cityscapes.py`(CityScapes 转 COCO 的离线脚本)
- `configs/cityscapes`(CityScapes 的微调配置)
- `tools/dataset_converters/pascal_voc.py`(PASCAL VOC 转中间格式的离线范例)
- `mmdet/datasets/custom.py`(`CustomDataset` 基类,供用户继承)

**内部链接指向**:
- `../../mmdet/datasets/dataset_wrappers.py` —— 该文件位于 `mmdet/datasets/` 目录下,与 `custom.py`、`coco.py`、`voc.py` 同模块,提供 `ConcatDataset`、`RepeatDataset` 等数据集包装器。该教程当前主要讲解**单个 dataset 类**层面的定制,数据集包装/级联(`ConcatDataset` 等)是训练时**对多个 dataset 进行组合**的上游机制,与本文描述的"自定义单个数据集"是正交但相关的下游使用方式。

**与本仓库上下文的关系**:本教程位于 `FSAF_for_Pytorch/mmdetection/docs/tutorials/`,是 FSAF 仓库内嵌的 MMDetection 文档副本;其中提到的 `CascadeMaskRCNN` 与 `Shared2FCBBoxHead` 是**示例用**的检测器,与 FSAF 的 anchor-free 检测 head 不同,仅用于演示 config 覆写流程。

---

## 【使用方法】

**启用方式(COCO 格式重整路径) — 原文步骤**:

1. 修改 config(以 `configs/my_custom_config.py` 为例),关键代码:
   ```python
   _base_ = './cascade_mask_rcnn_r50_fpn_1x_coco.py'
   dataset_type = 'CocoDataset'
   classes = ('a', 'b', 'c', 'd', 'e')
   data = dict(
       samples_per_gpu=2,
       workers_per_gpu=2,
       train=dict(type=dataset_type, classes=classes,
                  ann_file='path/to/your/train/annotation_data',
                  img_prefix='path/to/your/train/image_data'),
       val=dict(type=dataset_type, classes=classes,
                ann_file='path/to/your/val/annotation_data',
                img_prefix='path/to/your/val/image_data'),
       test=dict(type=dataset_type, classes=classes,
                 ann_file='path/to/your/test/annotation_data',
                 img_prefix='path/to/your/test/image_data'))
   model = dict(
       roi_head=dict(
           bbox_head=[
               dict(type='Shared2FCBBoxHead', num_classes=5),
               dict(type='Shared2FCBBoxHead', num_classes=5),
               dict(type='Shared2FCBBoxHead', num_classes=5)],
           mask_head=dict(num_classes=5)))
   ```
2. 校验标注 JSON:`categories` 长度等于 `len(classes)`、`name` 顺序与 config `classes` 一致、`category_id` 全部合法。

**启用方式(自定义 Dataset 类路径)** — 原文示例开头:
```python
import mmcv
import numpy as np
from .builder import DATASETS
from .custom import CustomDataset

@DATASETS.register_module()
class MyDataset(CustomDataset):
    CLASSES = ('person', 'bicycle', 'car', 'mot  # 原文此处被截断
```
(注册后即可在 config 中通过 `dataset_type='MyDataset'` 使用;后续 `load_annotations` / `get_ann_info` / `evaluate` 的实现细节原文因截断未给出。)

**配置项/命令**:
- `samples_per_gpu=2`、`workers_per_gpu=2`(原文示例值)
- `ann_file`、`img_prefix` 分别指定标注路径与图像前缀路径(三个 split 均需设置)
- `num_classes`:必须在**所有**分类 head 中显式覆盖,包括 `bbox_head` 列表的每一项和 `mask_head`

**注意事项(原文 Note)**:
1. 实例分割目前**仅支持对 COCO 格式的 mask AP 进行评测**;
2. 官方**推荐**离线转换为 COCO 格式后训练,这样可以直接复用 `CocoDataset`,只需修改 `ann_file` 与 `classes`。
