# 教程 2: 自定义数据集

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/autonoumous_driving/BEVDet_for_PyTorch/docs/zh_cn/tutorials/customize_dataset.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/autonoumous_driving/BEVDet_for_PyTorch/docs/zh_cn/tutorials/customize_dataset.md

# 一体化深度解读：MMDetection3D 自定义数据集教程

## 【定位】

这篇文档系统性地介绍在 MMDetection3D（BEVDet 的依赖框架之一）中**支持新的数据格式与自定义数据集**的多种方法，覆盖离线格式转换、中间 pickle 中间格式、以及数据集包装器三大路径，从而让用户能够复用既有模型来训练和评估非标准数据集。

---

## 【技术要点】

1. **离线转换优先原则**：对于不便于在线读取的数据（如 Waymo、ScanNet），建议在训练前通过数据转换器离线将其转换为 KITTI 数据集风格的标注格式，转换完成后仅需修改配置文件中标注路径与类别即可。

2. **pickle 中间格式**：MMDetection3D 将所支持的所有数据集统一转换成 pickle 文件，每个 pickle 实质是一个**字典列表**，每个字典描述一帧数据，必须包含 `image`、`point_cloud`、`calib`、`annos` 等关键字段；只要模型能从这些字段直接读取数据，原始数据的物理组织方式可以与现有组织方式不同。

3. **Custom3DDataset 继承机制**：用户可在 `mmdet3d/datasets/my_dataset.py` 中继承 `Custom3DDataset` 并通过 `@DATASETS.register_module()` 注册，重载 `get_ann_info(index)` 等方法，便可复用框架的 pipeline、评估、调度逻辑。

4. **KITTI 中间表示的字段约束**：以 KITTI 风格为例，每一帧的字典必须支持 `image`（含 `image_idx`、`image_path`、`image_shape`）、`point_cloud`（含 `num_features`、`velodyne_path`）、`calib`（含 `P0`、`P1`、`P2`、`P3`、`R0_rect`、`Tr_velo_to_cam`、`Tr_imu_to_velo`）、`annos`（含 `name`、`truncated`、`occluded`、`alpha`、`bbox`、`dimensions`、`location`、`rotation_y`、`score`、`index`、`group_ids`、`difficulty`、`num_points_in_gt`）等字段。

5. **三种数据集包装器**：MMDetection3D 提供 `RepeatDataset`（整体重复）、`ClassBalancedDataset`（基于类别频率的重复，需配合 `self.get_cat_ids(idx)`）、`ConcatDataset`（多数据集拼接）三种 wrapper，统一通过配置文件中的 `type=` 字段调用。

6. **类别平衡采样的阈值参数**：`ClassBalancedDataset` 通过 `oversample_thr=1e-3` 这类阈值参数控制哪些稀有类别需要被重复采样，实现数据集层面的均衡。

---

## 【关键机制与数据】

### 工作原理（数据流）

**路径 A：转换为现有数据格式（KITTI 路线）**
原始新数据集 → 数据转换器（重组织数据格式 + 标注格式化为 KITTI 风格）→ 修改配置文件（标注路径 + 类别字段）→ 调用现有 KITTI 数据集类训练。

**路径 B：转换为 pickle 中间格式路线**
原始新数据集 → 离线/在线转换为统一的 pickle 字典列表 → 继承 `Custom3DDataset` → 通过 `get_ann_info(index)` 从 `self.data_infos[index]` 字典中取标注 → 转换为 `DepthInstance3DBoxes` 等结构 → 返回 `anns_results`。

**路径 C：包装器路线**
在配置文件层面将原始数据集类嵌套到 `RepeatDataset` / `ClassBalancedDataset` / `ConcatDataset` 之中，复用 pipeline 与采样逻辑。

### 原文给出的具体数据示例（逐字段摘录）

**KITTI 风格字典示例的字段值（原文）：**

| 字段子项 | 原文字面数值 |
|---|---|
| `image_shape` | `array([370, 1224], dtype=int32)` |
| `num_features`（point_cloud） | `4` |
| `P0[0][2]`、`P0[1][2]` | `604.0814`、`180.5066` |
| `bbox`（annos） | `array([[712.4, 143., 810.73, 307.92]])` |
| `dimensions`（annos） | `array([[1.2, 1.89, 0.48]])` |
| `location`（annos） | `array([[1.84, 1.47, 8.41]])` |
| `rotation_y`（annos） | `array([0.01])` |
| `num_points_in_gt` | `array([377])` |

**ScanNet 风格 MyDataset 示例的字段值（原文）：**

| 字段子项 | 原文数值 |
|---|---|
| `num_features`（point_cloud） | `6` |
| `lidar_idx` | `'scene0000_00'` |
| `gt_num` | `27` |
| `class`（两条） | `array([6, 6])`（dtype=int32） |
| `gt_boxes_upright_depth` 形状 | `k, 6`（6 维：x, y, z, dx, dy, dz，原文坐标形式） |
| `box_dim` | `gt_bboxes_3d.shape[-1]` |
| `origin` | `(0.5, 0.5, 0.5)` |
| `with_yaw` | `False` |

**MyDataset 类别定义（原文 18 个类别，完整列示）：**
`'cabinet', 'bed', 'chair', 'sofa', 'table', 'door', 'window', 'bookshelf', 'picture', 'counter', 'desk', 'curtain', 'refrigerator', 'showercurtrain', 'toilet', 'sink', 'bathtub', 'garbagebin'`

### 性能数据
原文未涉及任何训练/推理性能指标或基准数据。

---

## 【表格解读】

**原文无表格**（文档以代码块配置示例和文字描述为主，未出现 markdown 表格结构）。

---

## 【公式解读】

**原文无公式**（文档未出现 LaTeX 数学公式或伪代码公式；仅以字典字面量、Python 类定义、配置文件 dict 的形式给出数据结构与配置形式）。

---

## 【关联】

文档显式提到的关联模块与外部资源：

1. **上游数据格式参考对象**：KITTI 数据集（作为离线转换的目标格式以及 pickle 中间格式的标准字段示例）、Lyft、nuScenes（作为与现有格式相似的"直接复用"代表）。

2. **基类与参考数据集实现**：
   - [`Custom3DDataset`](https://github.com/open-mmlab/mmdetection3d/blob/master/mmdet3d/datasets/custom_3d.py)：用户继承的对象。
   - [`KITTI 数据集`](https://github.com/open-mmlab/mmdetection3d/blob/master/mmdet3d/datasets/kitti_dataset.py)：作为离线转换目标的范例。
   - [`ScanNet 数据集`](https://github.com/open-mmlab/mmdetection3d/blob/master/mmdet3d/datasets/scannet_dataset.py)：作为继承式自定义的范例。

3. **下游配置文件层**：所有自定义均通过修改 `mmdet3d/configs/` 中的配置 dict（`dataset_A_train = dict(...)`）来激活，包括 `ann_file`、`pipeline` 等字段。

4. **与 MMDetection 共享的包装器**：文档明确指出 "与 MMDetection 类似"，并外链 [`mmdet/datasets/dataset_wrappers.py`](https://github.com/open-mmlab/mmdetection/blob/master/mmdet/datasets/dataset_wrappers.py) 源码，进一步印证数据集包装器是从 MMDetection 复用而来的。

5. **与其他教程的衔接**：文档内链 [如何将 Waymo 转换为 KITTI 风格并训练模型的例子](https://mmdetection3d.readthedocs.io/zh_CN/latest/2_new_data_model.html)，属于"教程"系列中的扩展篇。

6. **核心 bbox 结构体依赖**：`DepthInstance3DBoxes`（来自 `mmdet3d.core.bbox`），通过 `.convert_to(self.box_mode_3d)` 与训练时的 box 模式对齐，这是与下游模型检测头的衔接点。

7. **评估钩子接口**：`get_ann_info(index)` 注释指出 "**evalhook 也能够通过此接口来获取标注信息**"，即该接口同时服务于训练与推理评估流程。

---

## 【使用方法】

### 1) 用户级自定义数据集的标准流程（原文整合）

**步骤一**：将原始数据组织为 pickle 字典列表，每个帧含 `point_cloud`、`pts_path`、`pts_instance_mask_path`、`pts_semantic_mask_path`、`annos` 等关键字段，原文 ScanNet 样例给出了一个真实的 `annotation.pkl` 字段布局。

**步骤二**：在 `mmdet3d/datasets/my_dataset.py` 中实现自定义数据集类，需包含：
- `CLASSES` 元组定义全部类别（原文给出 18 类示例）。
- `__init__` 方法透传 `data_root`、`ann_file`、`pipeline`、`classes`、`modality`、`box_type_3d`、`filter_empty_gt`、`test_mode` 给父类。
- `@DATASETS.register_module()` 装饰器。
- 重载 `get_ann_info(index)`，从 `self.data_infos[index]['annos']` 取出 `gt_bboxes_3d`、`gt_labels_3d`，并在 `gt_num != 0` 时将 `gt_boxes_upright_depth` 转为 `np.float32`、`class` 转为 `np.int64`；否则返回空数组 `(0, 6)` 和 `(0,)`；最后用 `DepthInstance3DBoxes(..., box_dim=gt_bboxes_3d.shape[-1], with_yaw=False, origin=(0.5, 0.5, 0.5)).convert_to(self.box_mode_3d)` 转换为目标结构。

**步骤三**：在配置文件中以 dict 形式注册：
```python
dataset_A_train = dict(
    type='MyDataset',
    ann_file='annotation.pkl',
    pipeline=train_pipeline
)
```

### 2) 数据集包装器的启用方式（原文配置示例）

- **RepeatDataset**：`times=N`，并在外层 `dataset=dict(...)` 嵌套原数据集配置。
- **ClassBalancedDataset**：`oversample_thr=1e-3`，并要求被包装的数据集实例化 `self.get_cat_ids(idx)`。
- **ConcatDataset**：原文给出三种拼接情形，文中前两种情形展示了配置文件用法（原文在 `type='Dataset_A'`、`ann_file=['anno_fi...` 处被截断，剩余内容**原文未涉及**）。

### 3) 离线转换为 KITTI 风格
原文以 Waymo → KITTI 为例，给出外链 https://mmdetection3d.readthedocs.io/zh_CN/latest/2_new_data_model.html ，具体脚本与命令细节**原文未涉及**，需参见该链接。
