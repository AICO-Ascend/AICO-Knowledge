# Tutorial 2: Customize Datasets

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/dev/cv/detection/YOLOX_ID2833_for_PyTorch/docs/en/tutorials/customize_dataset.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/dev/cv/detection/YOLOX_ID2833_for_PyTorch/docs/en/tutorials/customize_dataset.md

# 深度解读：Tutorial 2: Customize Datasets

## 【定位】
本文档是 MMDetection 框架下的"自定义数据集"教程（Tutorial 2），旨在指导用户将自有格式的数据集接入 MMDetection 训练流程，覆盖"转换为 COCO/PASCAL 现有格式"、"转换为 middle format 中间格式"以及"在线/离线转换"三种主要路径，并以 5 类 Cascade Mask R-CNN R50-FPN 为实例给出端到端的配置与标注校验方法。

---

## 【技术要点】

1. **三条接入路径**：① 离线转换为 COCO 或 PASCAL VOC 既有格式（推荐）；② 离线或在线转换为 MMDetection 自定义的 middle format；③ 继承 `CustomDataset` 在训练时做在线转换。

2. **COCO JSON 三件套键**：`images`（含 `file_name`/`height`/`width`/`id`）、`annotations`（实例标注列表）、`categories`（类别名+ID）。三者缺一不可。

3. **配置文件的两个关键改动**（以 5 类 COCO 自定义集为例）：
   - 在 `data.train / data.val / data.test` 三个子字典中显式加入 `classes = ('a','b','c','d','e')`；
   - 将 `model.roi_head.bbox_head` 三个 `Shared2FCBBoxHead` 以及 `model.roi_head.mask_head` 的 `num_classes` 由默认的 80（原文标注值）显式覆盖为 `5`。
   训练超参示例：`samples_per_gpu=2`，`workers_per_gpu=2`。

4. **标注一致性三项校验**：
   ① `categories` 列表长度 == 配置中 `classes` 元组长度；② 配置 `classes` 与 `categories[*].name` 元素及顺序完全一致；③ `annotations[*].category_id` 全部属于 `categories[*].id` 集合。
   MMDetection 会自动将 `categories` 中"非连续 id"映射为连续的 label indices，映射顺序由 `categories` 中的 `name` 字符串顺序决定，进而影响可视化标签文本。

5. **Middle Format 数据结构**：每张图对应一个 dict，含 `filename`（相对路径）、`width`、`height`，训练时附加 `ann`（dict，含 `bboxes: ndarray (n,4) float32`、`labels: ndarray (n,) int64`，可选 `bboxes_ignore` / `labels_ignore`）。

6. **在线 vs 离线转换**：在线方式需继承 `CustomDataset` 并覆写 `load_annotations(self, ann_file)` 与 `get_ann_info(self, idx)`（参考 `CocoDataset`/`VOCDataset`）；离线方式则将 middle format 序列化为 pickle/json 后直接用 `CustomDataset` 加载（参考 `pascal_voc.py`）。

> 说明：原文末尾 "An example of customized dataset" 一节的代码片段 `CLASSES = ('person', 'bicycle', 'car', 'mot` 被截断（缺少右括号与后续字段），本解读不再外推其未展示部分。

---

## 【关键机制与数据】

**数据流（推荐路径：离线转 COCO → 修改 config → 训练）**

1. 用户将自有标注离线转成 COCO JSON（含 `images`/`annotations`/`categories`）。
2. 新建 `configs/my_custom_config.py`，`_base_` 继承 `cascade_mask_rcnn_r50_fpn_1x_coco.py`，覆盖：
   - `dataset_type = 'CocoDataset'`，新增 `classes` 元组并写入三段 `data.*`；
   - `model.roi_head.bbox_head`（3 个 `Shared2FCBBoxHead`）与 `model.roi_head.mask_head` 的 `num_classes`，由 80 改写为 5。
3. 训练前对 JSON 做"长度、顺序、ID 合法性"三项校验。

**性能/规模数据（原文）**
- 原文标注：默认 `num_classes = 80`（COCO），本例覆盖为 `5`。
- 原文标注：示例 `samples_per_gpu=2`、`workers_per_gpu=2`。
- 原文标注的样例标注数值：`bbox = [192.81, 224.8, 74.73, 33.43]`，`area = 1035.749`，`iscrowd = 0`，`image_id = 1268`，`category_id = 16`，`id = 42986`，图像 `height=427, width=640`。
- 原文标注的非连续 id 类别示例：`{'id': 1, 'name': 'a'}, {'id': 3, 'name': 'b'}, {'id': 4, 'name': 'c'}, {'id': 16, 'name': 'd'}, {'id': 17, 'name': 'e'}` —— 用于说明 MMDetection 的连续化映射。

**实例分割的硬约束（原文 Note）**
> "MMDetection only supports evaluating mask AP of dataset in COCO format for now."
即当前仅对 COCO 格式数据集评估 mask AP。

---

## 【表格解读】

**原文无正式表格**。但原文以"代码块"形式给出了两个具有表格语义的结构化样例，逐字还原如下：

### 结构 A：COCO annotations + categories 合法样例

| 字段 | 取值（原文） |
|---|---|
| segmentation | `[[192.81, 247.09, ..., 219.03, 249.06]]`（若存在 mask 标签时） |
| area | `1035.749` |
| iscrowd | `0` |
| image_id | `1268` |
| bbox | `[192.81, 224.8, 74.73, 33.43]` |
| category_id | `16` |
| id | `42986` |
| categories[0] | `{'id': 1, 'name': 'a'}` |
| categories[1] | `{'id': 3, 'name': 'b'}` |
| categories[2] | `{'id': 4, 'name': 'c'}` |
| categories[3] | `{'id': 16, 'name': 'd'}` |
| categories[4] | `{'id': 17, 'name': 'e'}` |

**逐行解读**：
- 单个标注至少需要 5 个字段：`area / iscrowd / image_id / bbox / category_id`；当含分割 mask 时补 `segmentation`，并用 `id` 作为标注自身的全局唯一编号。
- `categories` 中 id 不要求从 0 开始、也不要求连续；`id` 与 `name` 必须一一对应。`name` 的顺序决定 MMDetection 将其映射为连续 label indices 的顺序。

### 结构 B：middle format 单样本示例

| 字段 | 类型/形状（原文） |
|---|---|
| filename | `'a.jpg'`（相对路径） |
| width | `1280` |
| height | `720` |
| ann.bboxes | `<np.ndarray, float32>`，形状 `(n, 4)` |
| ann.labels | `<np.ndarray, int64>`，形状 `(n,)` |
| ann.bboxes_ignore | `<np.ndarray, float32>`，形状 `(k, 4)` |
| ann.labels_ignore | `<np.ndarray, int64>`，形状 `(k,)`（可选） |

**逐行解读**：
- 测试阶段仅需 `filename / width / height` 三字段；训练阶段必须再带 `ann`。
- `bboxes_ignore / labels_ignore` 用于标注 crowd、difficult 或需要忽略的目标，与 `bboxes / labels` 配对使用，二者 dtype 与形状必须一致。

### 结构 C：自定义文本标注 `annotation.txt` 解析约定

原文以一段缩进行文本展示了字段顺序约定（非表格，但等价于解析规则表）：

```
#                ← 图像分隔符
000001.jpg       ← filename
1280 720         ← width height
2                ← 该图目标数 N
10 20 40 60 1    ← bbox(x1 y1 x2 y2) + class_id
20 40 50 60 2
#
000002.jpg
1280 720
3
50 20 40 60 2
20 40 30 45 2
30 40 50 60 3
```

**解读**：以 `#` 分块；每块首行为文件名、第二行为宽高、第三行为目标数 N，随后 N 行每行 5 列（x1 y1 x2 y2 class_id），与 middle format 一一对应。

---

## 【公式解读】

**原文无公式**（无 LaTeX、无伪代码形式的数学表达式）。涉及到的仅是数据结构定义和坐标几何，bbox 采用 `[x1, y1, x2, y2]` 直接存储，无额外数学公式需要展开。

---

## 【关联】

文档显式引用了 MMDetection 生态中的若干模块/脚本作为参考实现（均为外部 GitHub 链接，未提供仓库内相对路径，故归为"上下文引用"而非本文内的内部链接）：

- **数据集基类 / 内置数据集实现**
  - `mmdet/datasets/custom.py`：`CustomDataset` 基类（middle format 与在线转换的承载点）。
  - `mmdet/datasets/coco.py`：`CocoDataset`，在线转换 `load_annotations` / `get_ann_info` 的参考实现。
  - `mmdet/datasets/voc.py`：`VOCDataset`，同上，VOC 路径的参考实现。
  - `mmdet/datasets/builder.py`：通过 `@DATASETS.register_module()` 注册自定义数据集类（见示例 `MyDataset(CustomDataset)`）。

- **离线转换脚本（tools/dataset_converters）**
  - `cityscapes.py`：将 CityScapes 转 COCO 的离线脚本；与之配套有 `configs/cityscapes` 的微调配置。
  - `pascal_voc.py`：将 PASCAL VOC 转 middle format 并落盘 pickle/json 的离线脚本。

- **上下游教程**（来自标题"Tutorial 2"暗示存在 Tutorial 1/3+ 的序列）
  - 上游：通常是 MMDetection 入门/配置基础（如 config 结构、数据管线 `data.train/val/test`、评估器等）。
  - 下游：自定义模型、自定义损失/Head、自定义评测指标等教程。

- **与 config 体系的关系**：本文示例 `_base_ = './cascade_mask_rcnn_r50_fpn_1x_coco.py'`，表明用户自定义 config 通过"继承 + 局部覆盖"机制复用基类的所有训练/测试流程，仅替换数据相关与 `num_classes` 相关字段即可最小化改动。

---

## 【使用方法】

**启用方式（按文档原文整理）**

1. **准备标注**：将自有数据集离线转为 COCO JSON（含 `images / annotations / categories` 三键），或转为 middle format 列表（每图一个 dict）。

2. **新建自定义 config**（如 `configs/my_custom_config.py`）：
   - `_base_ = './cascade_mask_rcnn_r50_fpn_1x_coco.py'`（继承基配置，原文示例）；
   - 设置 `dataset_type = 'CocoDataset'`，定义 `classes = ('a','b','c','d','e')`（原文示例，5 类）；
   - 在 `data = dict(train=..., val=..., test=...)` 三段分别填入 `type / classes / ann_file / img_prefix`，并按需设置 `samples_per_gpu / workers_per_gpu`（原文示例值均为 `2`）；
   - 在 `model.roi_head.bbox_head = [dict(type='Shared2FCBBoxHead', num_classes=5), ...]` 与 `model.roi_head.mask_head = dict(num_classes=5)` 中将 `num_classes` 由默认 `80` 改为你的类别数 `5`（原文示例）。

3. **标注一致性校验**（原文三项硬性要求）：
   - `len(categories) == len(classes)`；
   - 配置 `classes` 与 `categories[*].name` 元素及顺序一致；
   - 所有 `annotations[*].category_id ∈ {categories[*].id}`。

4. **在线转换路径**：在 `mmdet/datasets/my_dataset.py` 中定义：
   ```python
   @DATASETS.register_module()
   class MyDataset(CustomDataset):
       CLASSES = (...)
       def load_annotations(self, ann_file): ...
       def get_ann_info(self, idx): ...
   ```
   （原文此处示例因原文截断，完整尾部未给出，本节仅复述原文已展示的字段。）

5. **离线转换路径**：参考 `tools/dataset_converters/pascal_voc.py`，把标注序列化为 middle format 的 pickle/json，再以 `CustomDataset` 加载。

**未涉及的内容**：原文未给出具体的训练启动命令（如 `tools/train.py` 调用方式、GPU 数量 `--gpus`、学习率 schedule 等），也未给出 PASCAL VOC 路径的 `num_classes` 改写示例（仅给出了 COCO 路径）。如需启动训练，请结合同仓库的 `tools/train.py` 使用说明进行调用。
