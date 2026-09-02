# Tutorial 2: Customize Datasets

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/autonoumous_driving/BEVDet_for_PyTorch/docs/en/tutorials/customize_dataset.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/autonoumous_driving/BEVDet_for_PyTorch/docs/en/tutorials/customize_dataset.md

# 一体化深度解读：MMDetection3D 教程 2 - 自定义数据集

---

## 【定位】

本文档解决 **MMDetection3D 中如何支持新的点云/图像数据集格式** 的问题，描述了两种核心能力：① 将新数据重整为已有格式（如 KITTI）以复用现有数据加载管线；② 将新数据转换为中间格式（pickle 文件 + 列表/字典结构）并通过继承 `Custom3DDataset` 实现自定义数据集类，从而接入训练流程。

> 原文："To support a new data format, you can either convert them to existing formats or directly convert them to the middle format."

---

## 【技术要点】

1. **两条主要路径**：① "Reorganize new data formats to existing format"（推荐 KITTI，离线转换）；② "Reorganize new data format to middle format"（pickle 离线保存）。
2. **离线 vs 在线转换**：原文建议"对于不便在线直接读取的数据，转换为 KITTI 格式并离线完成转换，之后只需修改 config 中的数据标注路径和类别"；而对格式与已有数据集相似的数据（如 Lyft 与 nuScenes），"推荐直接实现数据转换器和数据集类"，可考虑继承以减少工作量。
3. **中间格式数据结构**：所有支持的数据集都被转换为 pickle 文件，**标注是一个 dict 列表**，每个 dict 对应**一帧**，关键键包括 `image`、`point_cloud`、`calib`、`annos`（KITTI 示例所示）。
4. **基础类与可参考实现**：自定义数据集应继承 `Custom3DDataset`，可参考 `KittiDataset`、`ScanNetDataset`。
5. **典型工作流**：编写数据转换器重组原始数据 → 编写新数据集类继承已有类处理差异 → 修改 config 文件指向新数据集。
6. **示例数据集字段（KITTI 风格中间格式）**：每帧含 `image.image_idx`、`image.image_shape (array([370, 1224], dtype=int32))`、`point_cloud.num_features=4`、`calib.P0/P1/P2/P3/R0_rect/Tr_velo_to_cam/Tr_imu_to_velo`、`annos.name/truncated/occluded/alpha/bbox/dimensions/location/rotation_y/score/index/group_ids/difficulty/num_points_in_gt` 等。

---

## 【关键机制与数据】

### 工作原理

- **核心抽象**：标注 = list[dict]，**每个 dict = 一个帧**。只要能按照这些信息直接读取数据，原始数据的组织方式可以与已有数据集不同。
- **离线预转换**：先用一个独立脚本把数据转换为 pickle 文件（中间格式）或 KITTI 风格原始文件；训练时数据集类只负责读取这些已转换好的文件。
- **继承机制**：自定义类通过继承 `Custom3DDataset` 并按需重写方法（如 `get_ann_info`），复用加载管线、评估钩子（evalhook）等基础设施。
- **Bounding Box 转换**：示例中读出的 `gt_boxes_upright_depth`（k×6 数组）通过 `DepthInstance3DBoxes(... with_yaw=False, origin=(0.5, 0.5, 0.5)).convert_to(self.box_mode_3d)` 转为目标 3D 框结构。

### 数据流（基于 KITTI 中间格式示例）

每帧 dict 结构如下（原文值已保留）：

- `image`:
  - `image_idx`: 0
  - `image_path`: `training/image_2/000000.png`
  - `image_shape`: `array([370, 1224], dtype=int32)`
- `point_cloud`:
  - `num_features`: 4
  - `velodyne_path`: `training/velodyne/000000.bin`
- `calib`: 7 个 4×4 矩阵（P0、P1、P2、P3、R0_rect、Tr_velo_to_cam、Tr_imu_to_velo），原文给出了具体数值（部分节选）：
  - P0 第 1 行：`[707.0493, 0., 604.0814, 0.]`
  - P1 第 1 行：`[707.0493, 0., 604.0814, -379.7842]`
  - P2 第 1 行：`[7.070493e+02, 0., 6.040814e+02, 4.575831e+01]`
  - P3 第 1 行：`[7.070493e+02, 0., 6.040814e+02, -3.341081e+02]`
  - `R0_rect`（3×3 + 齐次行）：对角线元素 `0.9999128 / 0.9999406 / 0.9999556`
  - `Tr_velo_to_cam`：齐次变换矩阵，将 velodyne 坐标系转到相机坐标系
  - `Tr_imu_to_velo`：齐次变换矩阵，将 IMU 转到 velodyne
- `annos`:
  - `name`: `array(['Pedestrian'], dtype='<U10')`
  - `truncated`: `array([0.])`
  - `occluded`: `array([0])`
  - `alpha`: `array([-0.2])`
  - `bbox`: `array([[712.4, 143., 810.73, 307.92]])`
  - `dimensions`: `array([[1.2, 1.89, 0.48]])` （长/宽/高）
  - `location`: `array([[1.84, 1.47, 8.41]])` （相机坐标系下位置）
  - `rotation_y`: `array([0.01])`
  - `score`: `array([0.])`
  - `index`: `array([0], dtype=int32)`
  - `group_ids`: `array([0], dtype=int32)`
  - `difficulty`: `array([0], dtype=int32)`
  - `num_points_in_gt`: `array([377], dtype=int32)`

> 原文标注：上述是"a basic example (used in KITTI)"，用以展示一帧应有的关键字段。

### 性能数据

- 原文**未提供**任何训练/推理性能数据、速度或精度指标。

---

## 【表格解读】

**原文无表格**。文中信息以代码块（list-of-dict 形式）和代码片段（数据集类定义）呈现，但**没有任何 markdown 表格或等价结构化表格**。因此本节如实标注"原文无表格"，转而列出文档中出现的关键数据结构样例（KITTI 中间格式与自定义 ScanNet 风格示例）供参照：

| 类别 | 字段 | 样例值（原文） |
|---|---|---|
| image | image_idx | 0 |
| image | image_path | training/image_2/000000.png |
| image | image_shape | array([370, 1224], dtype=int32) |
| point_cloud | num_features | 4 |
| point_cloud | velodyne_path | training/velodyne/000000.bin |
| calib | P0/P1/P2/P3/R0_rect/Tr_velo_to_cam/Tr_imu_to_velo | 4×4 矩阵（原文已给出数值） |
| annos | name | array(['Pedestrian'], dtype='<U10') |
| annos | bbox | array([[712.4, 143., 810.73, 307.92]]) |
| annos | dimensions | array([[1.2, 1.89, 0.48]]) |
| annos | location | array([[1.84, 1.47, 8.41]]) |
| annos | rotation_y | array([0.01]) |
| annos | num_points_in_gt | array([377], dtype=int32) |

> 说明：以上为我整理自原文代码块的字段汇总表，方便阅读；**原文本身并没有显式表格**。

---

## 【公式解读】

**原文无公式**（无 LaTeX、也无伪代码公式）。文中出现的均为**数据结构示例**和**代码定义**，不属于数学公式范畴。

---

## 【关联】

- **上游/底层框架**：MMDetection3D（基于 `mmdet3d` 和 `mmdet`）。
- **核心基类**：`Custom3DDataset`（位于 `mmdet3d/datasets/custom_3d.py`，文中被引用以派生自定义类）。
- **可参考实现**：
  - `KittiDataset`（`mmdet3d/datasets/kitti_dataset.py`）
  - `ScanNetDataset`（`mmdet3d/datasets/scannet_dataset.py`）
- **注册与工具**：
  - `mmdet.datasets.DATASETS.register_module`（通过 `@DATASETS.register_module()` 注册新数据集）
  - `mmdet3d.core.bbox.DepthInstance3DBoxes`（3D 框数据结构，文中用于将原始 k×6 数组转为带 box_mode 的 3D 框）
  - `mmdet3d.core.show_result`（导入但示例代码未实际调用）
- **关联教程/扩展阅读**：
  - [Tutorial 2: 训练自定义数据集](https://mmdetection3d.readthedocs.io/en/latest/2_new_data_model.html) — 文档中提到 "An example training predefined models on Waymo dataset by converting it into KITTI style can be taken for reference"。
- **内部链接**：原文**未提供任何内部链接**（文末标注"内部链接: (无)"）。所有引用均为外部链接（mmdetection3d 文档站与 GitHub 仓库）。
- **自定义数据集建议存放路径**：`mmdet3d/datasets/my_dataset.py`。

---

## 【使用方法】

### 启用方式（自定义数据集的标准流程，原文示例）

1. **重组标注为 list-of-dict 并存为 pickle**：参照 ScanNet 风格，确保每帧包含 `point_cloud`、`pts_path`、`pts_instance_mask_path`、`pts_semantic_mask_path`、`annos`（含 `gt_num`、`name`、`location`、`dimensions`、`gt_boxes_upright_depth`、`index`、`class`）。
2. **新建数据集类**：在 `mmdet3d/datasets/my_dataset.py` 中：
   - 使用 `@DATASETS.register_module()` 装饰类。
   - 继承 `Custom3DDataset`。
   - 定义 `CLASSES` 元组（示例共 18 类：cabinet/bed/chair/sofa/table/door/window/bookshelf/picture/counter/desk/curtain/refrigerator/showercurtrain/toilet/sink/bathtub/garbagebin）。
   - `__init__` 透传 `data_root, ann_file, pipeline, classes, modality, box_type_3d, filter_empty_gt, test_mode` 给父类；默认 `box_type_3d='Depth'`，`filter_empty_gt=True`。
   - 实现 `get_ann_info(self, index)`：从 `self.data_infos[index]` 取标注，若 `gt_num != 0` 则取 `gt_boxes_upright_depth`（k×6，float32）与 `class`（int64）；否则用零占位。随后用 `DepthInstance3DBoxes(..., with_yaw=False, origin=(0.5, 0.5, 0.5)).convert_to(self.box_mode_3d)` 转框结构，并构造 `pts_instance_mask_path`、`pts_semantic_mask_path`（通过 `osp.join(self.data_root, info[...])`）。
3. **修改 config 文件**：使用新数据集后，只需在 config 中指向新的标注路径与类别即可训练。
4. **KITTI 风格离线转换路径**：对不便在线读取的数据，先用转换脚本把原始数据转为 KITTI 风格；之后只需修改 config 的 `data annotation paths` 与 `classes`。
5. **类似格式路径**：对格式与已有数据集相似的数据（如 Lyft 与 nuScenes），可直接实现数据转换器与数据集类，并考虑继承以减少实现工作量。

> 注意：原文示例代码在 `pts_` 之后被截断（"Document truncated"），故 `pts_instance_mask_path` 之后的 `anns_results` 字典构造未在原文中给出完整代码；但根据前文模式与字典前缀可推断其结构（`pts_instance_mask_path`、`pts_semantic_mask_path` 等键），本解读未臆测未给出的具体代码行。

### 配置项 / 命令

- 原文**未给出**具体命令行、config YAML 模板或脚本调用方式；示例仅展示了 Python 类层面的实现。完整 config 修改与训练命令需参考上文提到的外部链接 [mmdetection3d.readthedocs.io/.../2_new_data_model.html](https://mmdetection3d.readthedocs.io/en/latest/2_new_data_model.html)（以原文指向为准）。
