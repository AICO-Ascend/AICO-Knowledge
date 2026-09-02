# 教程 2: 自定义数据集

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/dev/cv/detection/YOLOX_ID2833_for_PyTorch/docs/zh_cn/tutorials/customize_dataset.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/dev/cv/detection/YOLOX_ID2833_for_PyTorch/docs/zh_cn/tutorials/customize_dataset.md

# 一体化深度解读:MMDetection 自定义数据集教程

## 【定位】

这篇文档面向**将自有数据集接入 MMDetection 训练框架**的用户,系统化讲解"如何支持新的数据格式"以及"如何用数据集包装器(Repeat/ClassBalanced/Concat)对数据集进行组合与重采样",核心思路是:**优先将数据离线转换为 COCO 格式并修改配置即可;若需保留自有标注格式,可走 CustomDataset 在线/离线转换两条路径**。

---

## 【技术要点】

1. **推荐的接入路径是"离线转 COCO + 改配置"**——MMDetection 建议把新数据转换成 COCO(或 PASCAL VOC)格式,转换完成后只需修改配置文件中标注路径与类别即可,无需改代码。
2. **COCO JSON 标注文件包含三个必备顶层键**:`images`(含 `file_name`、`height`、`width`、`id`)、`annotations`(含 `bbox`、`category_id`、`image_id` 等)、`categories`(含 `id` 与 `name`)。示例字段:`bbox: [192.81, 224.8, 74.73, 33.43]`、`area: 1035.749`、`iscrowd: 0`、`category_id: 16`、`id: 42986`、`image_id: 1268`。
3. **配置修改涉及两个层面**:`data` 段的 `train/val/test` 都需加入 `classes` 元组;`model.roi_head.bbox_head` 列表(以及 `mask_head`)中的 `num_classes` 需由默认 **COCO 的 80** 改为自定义类别数(示例为 **5**)。示例模型为 **Cascade Mask R-CNN R50-FPN**,`bbox_head` 含 3 个 `Shared2FCBBoxHead`,每个均需设置 `num_classes=5`。
4. **自定义标注合法性三条**——`categories` 长度 == `classes` 元组长度;`classes` 与 `categories[].name` 元素及顺序一致;`annotations[].category_id` 必须属于 `categories[].id` 的合法值(原文示例给出 `id` 为 1、3、4、16、17 的非连续 ID,文档明示 MMDetection 会自动将其映射成连续索引)。
5. **中间格式数据结构**——`data_infos` 为 list[dict],每项含 `filename`、`width`、`height`、`ann`,其中 `ann` 是包含 `bboxes`(np.float32, shape `(n,4)`)、`labels`(np.int64, shape `(n,)`)以及可选 `bboxes_ignore`/`labels_ignore` 的字典。
6. **CustomDataset 的两条接入路径**——在线转换:继承 `CustomDataset` 并重写 `load_annotations(self, ann_file)` 与 `get_ann_info(self, idx)`(参考 `CocoDataset`/`VOCDataset`);离线转换:转成 pickle 或 json 后直接用 `CustomDataset`(参考 `pascal_voc.py`)。
7. **三类数据集包装器**:`RepeatDataset`(设 `times=N` 整体重复)、`ClassBalancedDataset`(设 `oversample_thr=1e-3`,需数据集实现 `self.get_cat_ids(idx)`)、`ConcatDataset`(支持同类型多 `ann_file` 列表或不同数据集组合,可通过 `separate_eval=False` 让合并集作为一个整体参与评估)。
8. **实例分割的限制**——MMDetection 目前**只支持评估 COCO 格式的 mask AP**(原文明确注释)。

---

## 【关键机制与数据】

> 以下均来自原文,无臆造。

- **类别 ID 自动连续化机制**:原文:"MMDetection 会自动将 `categories` 中不连续的 `id` 映射成连续的索引,因此 `categories` 下的 `name` 的字符串顺序会影响标签的索引。同时,配置文件中的 `classes` 的字符串顺序也会影响到预测框可视化时的标签。"
- **数据流**(自定义标注 → 训练)的两步走:① 在 `mmdet/datasets/my_dataset.py` 中以 `@DATASETS.register_module()` 注册继承自 `CustomDataset` 的 `MyDataset`;② 在配置文件中以 `type='MyDataset'`、`ann_file='image_list.txt'`、`pipeline=train_pipeline` 引用。
- **示例自定义标注格式**(`annotation.txt`):以 `#` 分隔每张图,后跟 `文件名`、`宽 高`、`bbox 数量 N`,再跟 N 行 `x1 y1 x2 y2 class_id` 形式的数据;示例中类别 ID 取 1、2、3。
- **超参与阈值(原文出现)**:`oversample_thr=1e-3`(类平衡采样阈值);`separate_eval=False`(合并集统一评估开关);`samples_per_gpu=2`、`workers_per_gpu=2`(示例 `data` 段值)。
- **性能/精度数据**:原文未给出具体的 mAP/速度等数值。

---

## 【表格解读】

**原文无表格**。文中所有结构化信息均以 Python 代码块、JSON 字典或 `tuple/list` 字面量形式呈现(例如 `classes = ('a', 'b', 'c', 'd', 'e')`、COCO `bbox: [192.81, 224.8, 74.73, 33.43]` 等),未出现任何 markdown 表格或 HTML 表格结构。

---

## 【公式解读】

**原文无公式**。文档未出现任何 LaTeX 数学公式、伪代码表达式或带等号/不等号推导式;性能指标(如 AP、IoU 等)仅以文字陈述,无数学定义。

---

## 【关联】

- **上游基础配置**:`_base_ = './cascade_mask_rcnn_r50_fpn_1x_coco.py'`——文档中的所有自定义都以该基线配置为起点,继承其数据增强、训练 schedule、模型骨架等设定。
- **同系列参考实现**:
  - 在线转换参考实现:`mmdet/datasets/coco.py`(`CocoDataset`)、`mmdet/datasets/voc.py`(`VOCDataset`),二者均通过重写 `load_annotations` / `get_ann_info` 完成格式适配。
  - 离线转换参考实现:`tools/dataset_converters/pascal_voc.py`(转 VOC → 中间格式并存 pickle/json)。
  - 新格式支持样板:`tools/dataset_converters/cityscapes.py` + `configs/cityscapes/`,作为"按本文方式接入新数据集"的完整范例。
- **数据集包装器源码**:文末内部链接 `../../mmdet/datasets/dataset_wrappers.py` 对应 `RepeatDataset`、`ClassBalancedDataset`、`ConcatDataset` 三个包装类的源码,文档明示"更多细节请参考源码"——即三类包装器的行为(重复次数、类别均衡阈值 `oversample_thr`、合并策略及分别评估)在该文件中定义。
- **注册与构建链路**:`@DATASETS.register_module()` 装饰器配合 `from .builder import DATASETS` 与 `from .custom import CustomDataset`,使自定义数据集可被 `cfg` 中的 `type` 字段直接解析调用。
- **下游消费方**:`pipeline=train_pipeline` 表示该数据集将接入数据流水线(数据增强/批采样/分布式采样),与 `data.samples_per_gpu`、`data.workers_per_gpu` 共同决定 batch size 与 DataLoader worker 数。

---

## 【使用方法】

> 以下配置项/命令均摘录自原文,未做扩展。

- **离线转换 → COCO 的最小改动**(以 Cascade Mask R-CNN R50-FPN、5 类为例):
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
  ——关键开关:`classes` 元组(决定标签索引与可视化名)、`num_classes`(COCO 默认 80 → 自定义 5)。

- **在线自定义数据集注册**(以 `mmdet/datasets/my_dataset.py` 为例):
  ```python
  from .builder import DATASETS
  from .custom import CustomDataset

  @DATASETS.register_module()
  class MyDataset(CustomDataset):
      CLASSES = ('person', 'bicycle', 'car', 'motorcycle')
      def load_annotations(self, ann_file): ...
      def get_ann_info(self, idx): ...
  ```
  配置中引用:
  ```python
  dataset_A_train = dict(
      type='MyDataset',
      ann_file='image_list.txt',
      pipeline=train_pipeline)
  ```

- **RepeatDataset 启用**:
  ```python
  dataset_A_train = dict(
      type='RepeatDataset', times=N,
      dataset=dict(type='Dataset_A', ..., pipeline=train_pipeline))
  ```

- **ClassBalancedDataset 启用**(需数据集实现 `self.get_cat_ids(idx)`):
  ```python
  dataset_A_train = dict(
      type='ClassBalancedDataset', oversample_thr=1e-3,
      dataset=dict(type='Dataset_A', ..., pipeline=train_pipeline))
  ```

- **ConcatDataset 启用**(三种方式,原文示例):
  1. 同类多标注文件:
     ```python
     dataset_A_train = dict(
         type='Dataset_A',
         ann_file=['anno_file_1', 'anno_file_2'],
         pipeline=train_pipeline)
     ```
  2. 同上但作为整体评估:`separate_eval=False`。
  3. 不同数据集组合(`dataset_A_val`、`dataset_B_val` 各为独立 dict,挂到 `data` 段——**原文此处被截断,完整写法未在文档中给出**,建议参看 `dataset_wrappers.py`)。

- **启用/运行命令**:原文未涉及具体的启动命令(如 `tools/train.py`、CUDA/分布式参数),仅在配置层面给出 `type=...` 字段切换方式。

> 注:原文第 41 行附近被截断(`data = dict(imgs_per_gpu=2, workers_per_g...`),"ConcatDataset 不同数据集合并"小节的最后一组配置样例未完整呈现,实际使用应以官方仓库 `dataset_wrappers.py` 与 `data` 段配置惯例为准。
