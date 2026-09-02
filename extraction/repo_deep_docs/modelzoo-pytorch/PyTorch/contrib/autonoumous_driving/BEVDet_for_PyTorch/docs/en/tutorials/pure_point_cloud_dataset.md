# Tutorial 9: Use Pure Point Cloud Dataset

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/autonoumous_driving/BEVDet_for_PyTorch/docs/en/tutorials/pure_point_cloud_dataset.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/autonoumous_driving/BEVDet_for_PyTorch/docs/en/tutorials/pure_point_cloud_dataset.md

# Tutorial 9: Use Pure Point Cloud Dataset — 一体化深度解读

---

## 【定位】

这篇文档解决的是 **MMDetection3D / BEVDet 框架下使用纯点云（Pure Point Cloud）数据进行 3D 检测任务时的数据准备与自定义扩展问题**，具体涵盖：点云格式转换、点云标注工具推荐、新数据格式的接入策略、以及如何基于 `Custom3DDataset` 编写自定义数据集类。

---

## 【技术要点】

1. **点云格式约束**：MMDetection3D 当前只支持 **bin 格式**的点云用于训练和推理（"we only support bin format point cloud training and inference"）；其他格式（如 pcd、las）需先转换为 bin。

2. **格式转换链路**：
   - pcd → bin：使用 [Tools_RosBag2KITTI](https://github.com/leofansq/Tools_RosBag2KITTI)
   - las → bin：路径为 **las → pcd → bin**，las→pcd 使用 [semantic-segmentation-editor](https://github.com/Hitachi-Automotive-And-Industry-Lab/semantic-segmentation-editor)

3. **点云标注工具**：MMDetection3D 不自带标注功能，文档推荐：
   - [SUSTechPOINTS](https://github.com/naurril/SUSTechPOINTS)
   - [LATTE](https://github.com/bernwang/latte)（团队对此做过改进，参考 [arXiv:2011.10174](https://arxiv.org/abs/2011.10174)）

4. **支持新数据格式的两种策略**：
   - **离线重组到已有格式**：将自有数据集整理为包含必要 key 的 annotation 后，仅需修改 `config` 中的 `data annotation paths` 与 `classes`。
   - **重组到中间格式（pickle 文件）**：所有支持的数据集最终都被转换为 pickle 文件，结构为 list of dict，每 dict 对应一帧。

5. **中间格式关键字段**：`sample_idx`、`lidar_points`（含 `lidar_path`）、`annos`（含 `box_type_3d: 'LiDAR/Camera/Depth'`、`gt_bboxes_3d: <np.ndarray> (n, 7)`、`gt_names: [list]`）、`calib`、`images`。

6. **自定义数据集类**：若 pkl 仅含必要 key，可直接用 `Custom3DDataset`；否则需新建继承自 `Custom3DDataset` 的类，并重写 `get_ann_info` 方法（参考 KittiDataset / ScanNetDataset）。

---

## 【关键机制与数据】

### 工作原理 / 数据流

1. **离线转换路径**（推荐）：用户点云 → bin 格式 → 重组为 basic format annotation（list of dict，含 sample_idx / lidar_points / annos / calib / images）→ pickle 文件 → `Custom3DDataset` 加载 → 进入训练 pipeline。
   > 原文："we recommend converting it into basic format as above and do the conversion offline, thus you only need to modify the config's data annotation paths and classes after the conversion."

2. **在线转换路径**：对于与现有数据集格式相近的数据（如 Lyft ≈ nuScenes），可继承现有 dataset 类，新增一个 data converter 与 dataset class 来转换和加载数据，复用已有代码。

3. **中间格式设计动机**：pickle 文件中一帧包含 `image`、`point_cloud`、`calib`、`annos` 四类信息，只要能按这些 key 直接读取数据，原始数据的组织方式可以与现有数据集不同——这为自定义数据组织提供了灵活性。
   > 原文："As long as we could directly read data according to these information, the organization of raw data could also be different from existing ones."

4. **KITTI 实例关键数值**（原文有，逐字保留示例）：
   - `num_features: 4`（x, y, z, intensity）
   - `image_shape: array([370, 1224], dtype=int32)`
   - `P0, P1, P2, P3`：4×4 投影矩阵，主焦距约 **707.0493**，主点约 **(604.0814, 180.5066)**
   - `R0_rect`：4×4 修正旋转矩阵
   - `Tr_velo_to_cam`：4×4 雷达到相机外参
   - `Tr_imu_to_velo`：4×4 IMU 到雷达外参
   - 标注示例：`name='Pedestrian'`、`dimensions=[1.2, 1.89, 0.48]`、`location=[1.84, 1.47, 8.41]`、`rotation_y=0.01`、`num_points_in_gt=377`

5. **自定义 pkl 标注示例数值**（原文有）：
   - `sample_idx=120`，`lidar_path='training/000004.bin'`
   - 两类目标：car（`bbox=[1.48..., 3.52..., 1.85..., 1.74..., 0.23..., 0.57..., -0.25525]`，即 x, y, z, dx, dy, dz, yaw，共 7 维）、pedestrian（`bbox=[2.90..., -3.48..., 1.52..., 0.66..., 0.17..., 0.67..., 2.23145]`）。

> 注：原文中标注示例代码块存在 `bbox_type_3d`（应为 `box_type_3d` 的笔误）和维度 (n, 7) 的设计——7 维对应中心 (x,y,z) + 尺寸 (dx,dy,dz) + 朝向 yaw。

### 性能数据

原文未涉及任何训练/推理性能数据。

---

## 【表格解读】

**原文无表格**。

不过原文中以代码块形式给出了两段"结构化数据表"（本质是数据 schema），逐字还原如下：

### 表 A：Basic annotation format（离线转换目标格式）

| 层级 | Key | 取值 / 类型 | 说明（原文标注） |
|---|---|---|---|
| 外层 | `sample_idx` | — | 样本索引 |
| 外层 | `lidar_points` | dict | 包含 `lidar_path: velodyne_path` |
| 外层 | `annos` | dict | 见下 |
| annos | `box_type_3d` | `(str)` | `'LiDAR/Camera/Depth'` |
| annos | `gt_bboxes_3d` | `<np.ndarray>` | 形状 `(n, 7)` |
| annos | `gt_names` | `[list]` | 类别名列表 |
| 外层 | `calib` | dict | 标定信息 |
| 外层 | `images` | dict | 图像信息 |

> 解读：这是离线重组时的最小必要 schema。若数据不含 calib，可整体省略 `calib`；反之必须保留。从 `gt_bboxes_3d` 的 `(n, 7)` 形状可确认 BEVDet 3D 检测使用的是 **中心 + 尺寸 + yaw** 的 7 维 box 表示。

### 表 B：KITTI 中间格式（pickle）— 一帧示例字段

| 字段 | Key | 类型 / 示例 | 说明 |
|---|---|---|---|
| image | `image_idx` | `0` | 图像编号 |
| image | `image_path` | `'training/image_2/000000.png'` | 图像路径 |
| image | `image_shape` | `array([370, 1224], dtype=int32)` | (H, W) |
| point_cloud | `num_features` | `4` | 每点特征数（x,y,z,intensity） |
| point_cloud | `velodyne_path` | `'training/velodyne/000000.bin'` | 点云路径 |
| calib | `P0`, `P1`, `P2`, `P3` | 4×4 ndarray | 相机投影矩阵 |
| calib | `R0_rect` | 4×4 ndarray | 图像平面修正旋转 |
| calib | `Tr_velo_to_cam` | 4×4 ndarray | 雷达到相机外参 |
| calib | `Tr_imu_to_velo` | 4×4 ndarray | IMU 到雷达外参 |
| annos | `name` | `array(['Pedestrian'], dtype='<U10')` | 类别名 |
| annos | `truncated` | `array([0.])` | 截断程度 |
| annos | `occluded` | `array([0])` | 遮挡 |
| annos | `alpha` | `array([-0.2])` | 观测角 |
| annos | `bbox` | `array([[712.4, 143., 810.73, 307.92]])` | 2D 框 (x1,y1,x2,y2) |
| annos | `dimensions` | `array([[1.2, 1.89, 0.48]])` | (h, w, l) |
| annos | `location` | `array([[1.84, 1.47, 8.41]])` | 底面中心 3D 位置 |
| annos | `rotation_y` | `array([0.01])` | Y 轴旋转 |
| annos | `score`, `index`, `group_ids`, `difficulty`, `num_points_in_gt` | ndarray | 评分 / 索引 / 组 ID / 难度 / GT 内点数 |

> 解读：这是 KITTI 完整一帧 pickle 数据的标准组织形式。对纯点云用户而言，可只保留 `point_cloud` 与 `annos` 两个子字段，把 `image` 与 `calib` 置空即可（前提是后续 pipeline 不依赖它们）。

---

## 【公式解读】

**原文无公式**。文档涉及的仅是数据 schema（dict/list/ndarray 的嵌套结构），不存在数学公式或伪代码算法。

---

## 【关联】

1. **上游 / 数据准备层**：
   - 工具库 [Tools_RosBag2KITTI](https://github.com/leofansq/Tools_RosBag2KITTI)、[semantic-segmentation-editor](https://github.com/Hitachi-Automotive-And-Industry-Lab/semantic-segmentation-editor) —— 完成原始点云到 bin 的格式转换。
   - 标注工具 [SUSTechPOINTS](https://github.com/naurril/SUSTechPOINTS)、[LATTE](https://github.com/bernwang/latte)（含团队改进版 [arXiv:2011.10174](https://arxiv.org/abs/2011.10174)）—— 提供 3D bbox 标注能力。
   
2. **下游 / 数据加载层**：
   - `Custom3DDataset`（`mmdet3d/datasets/custom_3d.py`）—— 当 pkl 只含必要 key 时直接复用。
   - `KittiDataset`（`mmdet3d/datasets/kitti_dataset.py`）—— 作为复杂数据集的参考实现，可继承。
   - `ScanNetDataset`（`mmdet3d/datasets/scannet_dataset.py`）—— 同上，作为另一参考实现。
   
3. **配置层**：用户自定义数据集通过 `dataset_A_train = dict(type='Custom3DDataset', ann_file='annotation.pkl', pipeline=train_pipeline)` 注入训练 config。

4. **方法重写接口**：`get_ann_info(index)` 是 eval hook 与数据加载共用的关键 API，新数据集类应基于 `self.data_infos[index]` 实现它，并处理 `info['annos']['gt_num'] == 0` 的边界情况（返回 `(0, 6)` 的空数组占位）。

5. **可能的 Tutorial 关联**：本文档标题为 "Tutorial 9"，暗示这是系列教程的第 9 篇，但原文未给出其他 tutorial 的内部跳转链接（文末内部链接信息标注为"无"）。

---

## 【使用方法】

### 启用方式（原文有）

**1. 离线转换已有数据为 bin + basic format annotation**

```python
# 离线重组后的 annotation.pkl 结构（纯点云版本，示例）
{
    'sample_idx': 120,
    'lidar_points': {'lidar_path': 'training/000004.bin'},
    'annos': {
        'box_type_3d': 'LiDAR',           # 原文写 'bbox_type_3d'（疑似笔误）
        'gt_bboxes_3d': array([[x, y, z, dx, dy, dz, yaw], ...]),  # (n, 7)
        'gt_names': ['car', 'pedestrian']
    }
}
```

**2. 在 config 中直接启用 `Custom3DDataset`**（pkl 仅含必要 key 时）

```python
dataset_A_train = dict(
    type='Custom3DDataset',
    ann_file='annotation.pkl',
    pipeline=train_pipeline
)
```

**3. 自定义 Dataset 类**（pkl 含额外字段或需自定义读取时）—— 需在 `mmdet3d/datasets/my_dataset.py` 实现并通过 `@DATASETS.register_module()` 注册，继承 `Custom3DDataset` 并重写 `get_ann_info`：

```python
@DATASETS.register_module()
class MyDataset(Custom3DDataset):
    CLASSES = ('cabinet', 'bed', 'chair', 'sofa', 'table', 'door', 'window',
               'bookshelf', 'picture', 'counter', 'desk', 'curtain',
               'refrigerator', 'showercurtrain', 'toilet', 'sink', 'bathtub',
               'garbagebin')

    def __init__(self, data_root, ann_file, pipeline=None, classes=None,
                 modality=None, box_type_3d='Depth',
                 filter_empty_gt=True, test_mode=False):
        super().__init__(
            data_root=data_root, ann_file=ann_file,
            pipeline=pipeline, classes=classes,
            modality=modality, box_type_3d=box_type_3d,
            filter_empty_gt=filter_empty_gt, test_mode=test_mode)

    def get_ann_info(self, index):
        info = self.data_infos[index]
        if info['annos']['gt_num'] != 0:
            gt_bboxes_3d = info['annos']['gt_boxes_upright_depth'].astype(np.float32)  # k, 6
            gt_labels_3d = info['annos']['class'].astype(np.int64)
        else:
            gt_bboxes_3d = np.zeros((0, 6), dtype=np.float32)
            gt_la...    # 原文截断
```

### 配置项 / 命令

- `ann_file`：指向 annotation pickle 文件路径。
- `pipeline`：传入 `train_pipeline`（来自 configs 中的 pipeline 定义）。
- `box_type_3d`：可选 `'LiDAR' / 'Camera' / 'Depth'`，控制 3D box 的坐标系。
- `filter_empty_gt`：是否过滤无 GT 的样本，默认 `True`。
- `modality`：用于声明模态（如 `'use_lidar'`），决定下游是否读取点云字段。

### 命令行 / 启动脚本

**原文未涉及**训练启动命令、推理命令或具体 shell 命令的写法；只描述了数据准备与 dataset 类注册的方法。
