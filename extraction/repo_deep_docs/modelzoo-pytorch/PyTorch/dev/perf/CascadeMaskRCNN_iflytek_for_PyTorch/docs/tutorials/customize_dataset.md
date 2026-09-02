# Tutorial 2: Customize Datasets

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/dev/perf/CascadeMaskRCNN_iflytek_for_PyTorch/docs/tutorials/customize_dataset.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/dev/perf/CascadeMaskRCNN_iflytek_for_PyTorch/docs/tutorials/customize_dataset.md

# CascadeMaskRCNN 自定义数据集教程 · 深度解读

> ⚠️ 原文在 `MyDataset` 类定义处被截断（仅保留至 `CLASSES = ('person', 'bicycle', 'car', 'moto`），下文涉及 `MyDataset` 完整实现的部分将依据原文已透露的 API 进行解读，不再臆造后续内容。

---

## 【定位】

本教程属于 MMDetection 系列入门指南第 2 篇，**核心目的是教会用户如何让 MMDetection 支持新的数据格式**——通过将自有数据集**复用现有数据格式（COCO / PASCAL VOC）或转换为中间格式**两种路径，配合最小的代码改动完成自定义数据集的接入与训练。

---

## 【技术要点】

1. **两大接入路径**
   - 路径 A：**复用现有格式**（COCO 或 PASCAL VOC）。推荐做法是将自有数据离线转换为 COCO 格式，再仅修改 config 中的 `ann_file` / `img_prefix` / `classes`。
   - 路径 B：**转换为中间格式**（即 `CustomDataset` 接受的字典列表）。支持在线（继承 `CustomDataset`）与离线（导出为 pickle/json）两种方式。

2. **COCO JSON 三项必备键**
   - `images`：含 `file_name`、`height`、`width`、`id`。
   - `annotations`：含 `segmentation`、`area`、`iscrowd`、`image_id`、`bbox`、`category_id`、`id`。
   - `categories`：含 `id`、`name`。

3. **Config 修改的两处核心字段**
   - `data` 字段：需在 `train/val/test` 三处均显式写入 `classes = ('a','b','c','d','e')`。
   - `model` 字段：需将 `num_classes` 从 COCO 默认的 **80** 覆盖为目标类别数（示例中为 **5**）。
   - Cascade Mask RCNN 需同时覆盖 `roi_head.bbox_head`（三个 `Shared2FCBBoxHead`）以及 `mask_head` 的 `num_classes`，共 4 个点。

4. **类别一致性校验（三条硬约束）**
   - `categories` 列表长度 = `classes` 元组长度；
   - `classes` 元组元素顺序与 `categories[].name` 完全一致；
   - 所有 `category_id` 必须出现在 `categories[].id` 集合内。
   - MMDetection 会**自动把不连续的 `id` 映射为连续的 label indices**，映射顺序由 `categories[].name` 字符串顺序决定。

5. **中间格式数据结构**
   - 数据集是 `dict` 的 `list`，每个 dict 对应一张图。
   - 测试最少字段：`filename`、`width`、`height`。
   - 训练额外字段：`ann`，内含 `bboxes`（`(n, 4)` float32 ndarray）与 `labels`（`(n,)` int64 ndarray）。
   - 可选字段：`bboxes_ignore`、`labels_ignore`，用于 crowd / difficult / 忽略框。

6. **训练超参（示例值）**
   - `samples_per_gpu=2`、`workers_per_gpu=2`，与原 base config `_base_ = './cascade_mask_rcnn_r50_fpn_1x_coco.py'` 保持一致的 batch 设置。

---

## 【关键机制与数据】

### 数据流：配置继承 → 数据装载 → 模型 head 重写

1. **`_base_` 继承机制**
   原文：`In configs/my_custom_config.py: _base_ = './cascade_mask_rcnn_r50_fpn_1x_coco.py'`
   新 config 复用 base config 的全部训练策略（优化器、学习率、pipeline、模型骨架等），仅覆盖差异点（数据集类、类别数），符合 MMDetection "配置即代码 + 多层继承" 的设计哲学。

2. **`num_classes` 的 4 处覆盖（原文示例）**
   - `roi_head.bbox_head` 是一个长度为 **3** 的 list（Cascade 结构三阶段），每阶段都是 `Shared2FCBBoxHead`，每处都需 `num_classes=5`；
   - `mask_head.num_classes=5`；
   - 计数：3 + 1 = **4 处必改**。原文示例代码注释明确写了 4 句"explicitly over-write all the `num_classes` field from default 80 to 5"。

3. **类别 ID 映射（原文示例）**
   - 原文给出一个非连续 ID 示例：`categories = [{'id':1,'name':'a'},{'id':3,'name':'b'},{'id':4,'name':'c'},{'id':16,'name':'d'},{'id':17,'name':'e'}]`
   - 含义：MMDetection **不会**强制要求 `id` 从 0 或 1 连续排列；它会按照 `categories` 列表中 `name` 的出现顺序，将训练/推理阶段的标签索引映射为 `[0,1,2,3,4]`，对应的 `id` 列表是 `[1,3,4,16,17]`。

5. **bbox 字段格式（原文示例）**
   - `bbox': [192.81, 224.8, 74.73, 33.43]`，对应 **COCO 的 [x, y, w, h]**（左上角坐标 + 宽高），不是 [x1, y1, x2, y2]。

6. **实例分割标注（原文提示）**
   - 原文：*"MMDetection only supports evaluating mask AP of dataset in COCO format for now"*
   - 即 mask 评估路径仅对 COCO 格式开放；若使用中间格式，将无法获得 mask AP。

---

## 【表格解读】

**原文无表格**。文中所有结构化内容均以 Python 配置 / 字典 / 文本注解形式呈现，未出现 `<table>` 形式的参数表或性能对比表。可视为以**代码块替代表格**：

- COCO JSON 字段示例 → 等价于"必备字段定义表"；
- 配置文件 `data` / `model` 段 → 等价于"参数覆盖表"；
- 文本注解 `annotation.txt` 示例 → 等价于"自定义数据格式说明表"。

---

## 【公式解读】

**原文无公式**。文中不涉及任何 LaTeX 数学公式或数学符号推导，所有数值（如 `area=1035.749`、`bbox=[192.81,224.8,74.73,33.43]`）均为字段取值示例，而非数学表达。

---

## 【关联】

根据文末及正文中提及的内部/外部链接，梳理出以下模块依赖关系：

| 上游 / 下游模块 | 关系 | 链接 |
|---|---|---|
| `mmdet/datasets/dataset_wrappers.py`（题目给定内部链接） | 派生类与组合层级 | `../../mmdet/datasets/dataset_wrappers.py` |
| `CocoDataset`（`mmdet/datasets/coco.py`） | 路径 A 复用对象；`CustomDataset` 在线实现的范本 | github: `mmdet/datasets/coco.py` |
| `VOCDataset`（`mmdet/datasets/voc.py`） | `CustomDataset` 在线实现的另一范本 | github: `mmdet/datasets/voc.py` |
| `CustomDataset`（`mmdet/datasets/custom.py`，文中引用类名） | 路径 B 在线转换的基类；需重写 `load_annotations` 与 `get_ann_info` | （文中类名引用） |
| `tools/dataset_converters/cityscapes.py` | 路径 A 的离线转换参考脚本（CityScapes → COCO） | github: `tools/dataset_converters/cityscapes.py` |
| `configs/cityscapes` | 上述脚本对应的微调 config 集合 | github: `configs/cityscapes` |
| `tools/dataset_converters/pascal_voc.py` | 路径 B 离线转换范本（中间格式 → pickle/json） | github: `tools/dataset_converters/pascal_voc.py` |
| `builder.DATASETS` 注册器 | 自定义数据集类需 `@DATASETS.register_module()` 才可被 config 通过 `type=` 字段调用 | （`MyDataset` 示例 import） |
| base config `cascade_mask_rcnn_r50_fpn_1x_coco.py` | `_base_` 继承源；新 config 仅做差分覆盖 | （config 内部相对路径） |

**链路概览**：
- 路径 A：`my_custom_config.py` → `_base_` 继承 → `CocoDataset` 读取转换后的 COCO JSON → `CascadeMaskRCNN` 头。
- 路径 B 在线：自定义 `Dataset` 类继承 `CustomDataset` → 注册到 `DATASETS` → config 中 `dataset_type='MyDataset'` 调用。
- 路径 B 离线：原始数据 → `tools/dataset_converters/*` 脚本 → 中间格式文件 → `CustomDataset` 直接加载。

---

## 【使用方法】

### 路径 A：复用现有格式（以 COCO 为例）

1. **离线转换**自有标注为 COCO JSON（保证 `images` / `annotations` / `categories` 三个 key 完整）。
2. **新建 config 文件** `configs/my_custom_config.py`：
   - 写入 `_base_ = './cascade_mask_rcnn_r50_fpn_1x_coco.py'`；
   - 声明 `dataset_type = 'CocoDataset'` 与 `classes = ('a','b','c','d','e')`；
   - 在 `data.train / val / test` 三处填入 `classes=classes`、`ann_file`、`img_prefix`；
   - 在 `model.roi_head.bbox_head`（**list 中 3 项**）与 `model.roi_head.mask_head` 中覆盖 `num_classes=5`。
3. **校验**标注：`categories` 长度、`name` 顺序、`category_id` 范围三项一致。
5. **启动训练**：`python tools/train.py configs/my_custom_config.py`（原文未给出具体命令格式，仅描述流程）。

### 路径 B：使用中间格式

- **在线转换**：在 `mmdet/datasets/my_dataset.py` 定义 `MyDataset(CustomDataset)`，使用 `@DATASETS.register_module()`，**重写 `load_annotations(self, ann_file)` 与 `get_ann_info(self, idx)`** 两个方法（原文章节列出方法签名，**具体实现因原文截断未给出**），并设置 `CLASSES` 元组。
- **离线转换**：仿照 `tools/dataset_converters/pascal_voc.py` 写脚本，将原始标注导出为 `{filename, width, height, ann: {bboxes, labels[, bboxes_ignore, labels_ignore]}}` 结构的 pickle/json 文件，然后直接使用 `CustomDataset` 加载。

### 通用注意事项（原文 Notes）

- 实例分割任务若需评估 mask AP，**必须保留 COCO 格式**；
- 强烈建议**离线**完成格式转换，再以 `CocoDataset` + 仅修改路径与 `classes` 的方式接入，避免重复实现数据集类。

---

> 📌 **总览**：本教程用最少的代码示例，覆盖了 MMDetection 中"接入新数据集"的完整决策树——优先复用 COCO 格式 + config 差分覆盖，必要时退回中间格式 + `CustomDataset` 继承方案。核心约束集中在 **类别顺序一致性** 与 **`num_classes` 的级联覆盖**（Cascade 结构带来 4 处必须改点）。
