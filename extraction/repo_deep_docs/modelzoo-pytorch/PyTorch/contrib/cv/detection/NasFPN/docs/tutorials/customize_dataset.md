# Tutorial 2: Customize Datasets

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/NasFPN/docs/tutorials/customize_dataset.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/NasFPN/docs/tutorials/customize_dataset.md

# 一体化深度解读:NasFPN 自定义数据集教程

---

## 【定位】

本文档是 MMDetection 系列教程中的 **Tutorial 2: Customize Datasets**,聚焦于**如何让 MMDetection 框架支持新的数据格式或新的标注格式**,给出了离线转换与在线转换两条核心路径,以及配置文件中必须修改的字段(类别名 `classes` 与 `num_classes`)的对应规则。

---

## 【技术要点】

1. **三种数据准备路径**(原文核心机制):
   - 离线转换为 COCO / PASCAL VOC 等已有格式(推荐);
   - 离线转换为 MMDetection 自定义的 **middle format**(list-of-dict);
   - 在线转换:继承 `CustomDataset` 并重写 `load_annotations` 与 `get_ann_info`。

2. **COCO 标注 JSON 三大必备键**:`images`(含 `file_name`、`height`、`width`、`id`)、`annotations`(实例标注)、`categories`(类别名与 ID)。

3. **Config 文件两处必改**:
   - `data.train / data.val / data.test` 中显式增加 `classes` 字段;
   - `model.roi_head.bbox_head`(列表中每个 `Shared2FCBBoxHead`)与 `model.roi_head.mask_head` 的 `num_classes` 全部从默认 **80(COCO)** 覆盖为目标类别数(原文示例为 **5**)。

4. **类别一致性三约束**(否则会出错):
   - `categories` 长度 == config 中 `classes` 元组长度(例:5);
   - `classes` 元素顺序与 `categories[*].name` 完全一致(MMDetection 会把不连续的 `id` 自动映射为连续 label 索引,顺序决定可视化与索引映射);
   - `annotations[*].category_id` 必须落在 `categories[*].id` 集合内。

5. **Middle Format 内存数据结构**(list of dict,每个 dict 对应一张图):
   - 训练/测试公共字段:`filename`(相对路径)、`width`、`height`;
   - 训练额外字段 `ann`,内含 `bboxes`(numpy float32,shape `(n, 4)`)、`labels`(numpy int64,shape `(n,)`),以及可选的 `bboxes_ignore`(float32 `(k, 4)`)和 `labels_ignore`(int64 `(k,)`)以覆盖 crowd/difficult/ignored 框。

6. **实例分割评估的硬约束**:原文明确指出 **MMDetection 当前只支持 COCO 格式的 mask AP 评估**,自定义数据集如需 mask AP 评估应离线转 COCO。

---

## 【关键机制与数据】

### 数据流与工作原理(均源自原文)

- **离线 COCO 路径**:用户提供 COCO 风格 JSON → 修改 config 的 `classes` 和 `num_classes` → 直接使用 `CocoDataset` 训练,无需重写 Dataset 类。原文:"recommand to convert the data into COCO formats and do the conversion offline"。
- **在线转换路径**:用户继承 `CustomDataset`,重写 `load_annotations(self, ann_file)`(读取标注文件)与 `get_ann_info(self, idx)`(按索引返回标注),参考 `CocoDataset` / `VOCDataset` 实现。
- **离线 middle-format 路径**:通过 `pascal_voc.py` 之类脚本把标注转成 middle-format 并存为 pickle/json,随后直接用 `CustomDataset`。
- **Label 映射机制**(原文):MMDetection 会把 `categories` 中**不连续**的 `id`(示例中给出 `1, 3, 4, 16, 17`)自动映射为**连续**的 label 索引;`name` 字符串顺序决定 label 索引顺序,`classes` 字符串顺序决定预测框可视化时的标签文本。
- **COCO bbox 表示**:原文示例为 `[192.81, 224.8, 74.73, 33.43]`,即 COCO 标准的 `(x, y, w, h)`。
- **cityscapes 范例**(原文):官方用同一思路在 `tools/dataset_converters/cityscapes.py` 中实现,并提供对应的 finetuning configs。

### 性能/数值数据(原文仅有)
- 原文中出现的具体数值仅有:COCO 默认类别数 **80**,示例自定义类别数 **5**,一张示例图的 `area = 1035.749`,`image_id = 1268`,`bbox = [192.81, 224.8, 74.73, 33.43]`,`category_id = 16`,`id = 42986`,`iscrowd = 0`;以及 middle-format 示例图的 `width=1280, height=720`。

> 注:原文示例代码在 `class MyDataset(CustomDataset):` 之后被截断,后续 `CLASSES = ...` 的完整赋值与 `load_annotations` / `get_ann_info` 实现**不在原文中**,本文不臆测其内容。

---

## 【表格解读】

**原文无表格**。文档中没有以表格形式呈现的参数表/性能对比/配置项矩阵;类别数量、bbox 数值等均散落在 Python 代码块和正文中。

---

## 【公式解读】

**原文无公式**。文档未给出任何 LaTeX 数学公式或伪代码公式;仅有一处 COCO 风格的 bbox 数值序列 `[192.81, 224.8, 74.73, 33.43]`,其语义遵循 COCO 标准 `(x, y, w, h)`,但原文未将其表达为公式形式。

---

## 【关联】

### 与上下文的串联
- **目录位置**:本文档位于 `PyTorch/contrib/cv/detection/NasFPN/docs/tutorials/customize_dataset.md`,属于 NasFPN 仓库内 MMDetection 教程系列(Tutorial 2)。NasFPN 是 detection 方向的网络结构,本教程说明的是该框架在自定义数据上的接入方式。
- **本文所引用 / 依赖的其他模块(原文链接)**:
  - `CocoDataset`:`../../mmdet/datasets/coco.py`
  - `VOCDataset`:`../../mmdet/datasets/voc.py`
  - `CustomDataset`:`../../mmdet/datasets/custom.py`(原文代码 `from .custom import CustomDataset`)
  - Dataset 注册器:`../../mmdet/datasets/builder.py`(`from .builder import DATASETS`、`@DATASETS.register_module()`)
  - 数据转换脚本:`tools/dataset_converters/cityscapes.py`、`tools/dataset_converters/pascal_voc.py`
  - cityscapes finetuning configs:`configs/cityscapes`
- **唯一内部链接**:`../../mmdet/datasets/dataset_wrappers.py`
  - 该文件是 MMDetection 的 **dataset wrappers**(数据集包装器,用于 `ConcatDataset`、`RepeatDataset` 等组合策略)。它在本文档中虽未被直接引用,但属于"自定义数据集"的紧密上游——当用户把多份自定义数据集通过 `dataset_wrappers` 进行拼接/重复采样时,本文档产出的 `MyDataset` 类就会作为被包装的子数据集传入。

---

## 【使用方法】

### 路径 A:复用已有格式(COCO 为例,原文给出的完整步骤)

1. **修改 config**,继承 base config(如 `cascade_mask_rcnn_r50_fpn_1x_coco.py`),在 `data.train / data.val / data.test` 中显式写入 `classes = ('a','b','c','d','e')`,并设置 `ann_file` 与 `img_prefix`。
2. **覆盖 `num_classes`**:在 `model.roi_head.bbox_head` 的三个 `Shared2FCBBoxHead` 上以及 `model.roi_head.mask_head` 上,逐个把 `num_classes` 从默认 80 改为 5(原文逐处注释强调"explicitly over-write")。
3. **校验标注**:`categories` 长度 == 5;`categories[*].name` 与 config `classes` 元素顺序完全一致;`annotations[*].category_id` 全部落在 `categories[*].id` 集合内。

### 路径 B:使用 middle format(原文说明)

- 离线转换:用类似 `pascal_voc.py` 的脚本生成 middle-format 的 pickle/json,直接使用 `CustomDataset`。
- 在线转换:在 `mmdet/datasets/my_dataset.py` 中定义
  ```python
  @DATASETS.register_module()
  class MyDataset(CustomDataset):
      CLASSES = ...
  ```
  并重写 `load_annotations(self, ann_file)` 与 `get_ann_info(self, idx)`(具体实现原文因截断未给出)。

### 关键配置/参数(原文逐字摘录)

- `dataset_type = 'CocoDataset'`
- `classes = ('a', 'b', 'c', 'd', 'e')`
- `samples_per_gpu = 2`、`workers_per_gpu = 2`(示例设置)
- `num_classes = 5`(对 `bbox_head` 列表中**每个** `Shared2FCBBoxHead` 以及 `mask_head` 都要显式覆盖)
- middle-format 数组 dtype:`bboxes` → `np.float32`,`labels` → `np.int64`,`bboxes_ignore` → `np.float32`,`labels_ignore` → `np.int64`

### 注意事项(原文 Note 段)
- 实例分割的 mask AP 评估**仅支持 COCO 格式**;
- 推荐**离线**完成格式转换,以复用 `CocoDataset`。

### 适用命令 / API 入口
- 注册装饰器:`@DATASETS.register_module()`
- 父类:`CustomDataset`
- 注册表来源:`from .builder import DATASETS`(原文代码所示);训练启动等具体 CLI 命令**原文未涉及**。
