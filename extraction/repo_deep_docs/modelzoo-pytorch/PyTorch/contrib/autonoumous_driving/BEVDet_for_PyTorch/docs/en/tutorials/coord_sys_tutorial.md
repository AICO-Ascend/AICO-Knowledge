# Tutorial 6: Coordinate System

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/autonoumous_driving/BEVDet_for_PyTorch/docs/en/tutorials/coord_sys_tutorial.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/autonoumous_driving/BEVDet_for_PyTorch/docs/en/tutorials/coord_sys_tutorial.md

# 深度解读：MMDetection3D 坐标系教程 (Tutorial 6: Coordinate System)

## 【定位】

本文档系统性地阐述了 MMDetection3D 在 3D 目标检测任务中所采用的**三类坐标系（Camera / LiDAR / Depth）的统一规范定义**，包括坐标轴朝向、yaw 角参考方向、3D 边界框尺寸与轴的对应关系，并说明其与 KITTI、Waymo、NuScenes、Lyft、ScanNet 等数据集原始坐标系之间的差异与转换约定，目的是解决由于不同采集设备（LiDAR、深度相机等）和不同数据集惯例（如 SECOND、VoteNet）造成的坐标系混乱问题。

---

## 【技术要点】

1. **三类坐标系的核心约定**：
   - **Camera 系**：y 轴正方向指向地面（down），x 轴正方向指向右（right），z 轴正方向指向前（front）。
   - **LiDAR 系**：z 轴正方向指向上（up），x 轴正方向指向前（front），y 轴正方向指向左（left）。
   - **Depth 系**：z 轴正方向指向上（up），x 轴正方向指向右（right），y 轴正方向指向前（front）。被 VoteNet、H3DNet 等采用。

2. **统一的右手法则**：MMDetection3D 中三类坐标系均为右手系，因此 yaw 角的递增方向在沿重力轴负方向（指向观察者眼睛的方向）观察时为**逆时针**。

3. **Yaw 角定义规范**：在三类坐标系中，**参考方向始终是 x 轴正方向**；当 box 方向与 x 轴平行时其 yaw 角为 0；x 轴正方向对应的 yaw 角为 0，y 轴正方向对应的 yaw 角为 π/2。box 方向总是与边 `dx` 平行。

4. **Box 维度格式**：3D 框表示为 `(x, y, z, dx, dy, dz, r)`，其中 x、y、z 是位置，dx、dy、dz 是各轴对应的尺寸，r 是 yaw 角。**注：所有支持数据集的标注只包含 yaw 角，不含 pitch 和 roll**。

5. **与数据集原始坐标系的差异**：
   - **KITTI**：原始标注为 camera 系；训练 LiDAR-based 模型时需通过 `get_ann_info` 转为 LiDAR 系；训练 vision-based 模型则保持 camera 系。MMDetection3D 的 LiDAR 系相对 SECOND 的定义做了两点改动——yaw 角从左手系改为右手系，box 尺寸从 `(w, l, h)` 改为 `(l, w, h)`。
   - **Waymo**：使用 KITTI 格式数据，因此与 KITTI 共享同一坐标系。
   - **NuScenes**：box 尺寸前两维对应 `(dy, dx)` 即 `(w, l)`，与 MMDetection3D 的 LiDAR 系相反。
   - **Lyft**：坐标系与 NuScenes 一致。
   - **ScanNet**：原始数据为 mesh，采样点云在 Depth 系下；检测任务 box 标注为轴对齐（axis-aligned），yaw 角恒为 0。

6. **图示说明**：文档提供了每个坐标系的轴向示意图，以及 yaw=0、yaw=π/2、yaw=π 时 box 方向的对比图，并通过 `coord_sys_all.png` 总览三种坐标系的 3D 视图与鸟瞰图（BEV）。

---

## 【关键机制与数据】

- **工作原理**：由于 LiDAR、深度相机等 3D 采集设备坐标系各异，且不同数据集遵循不同惯例（如 SECOND、VoteNet 各自定义了不同的 box 表示），导致坐标系转换复杂。MMDetection3D 通过将所有数据统一到 Camera / LiDAR / Depth 三大坐标系之一（均右手系），并固定参考方向为 x 轴正方向，使 yaw 计算和 box 重叠（IoU）评估具有一致的语义。
- **数据流（KITTI 为例）**：
  - 原始标注在 camera 系 → 通过 `tools/data_converter/kitti_data_utils.py` 的 `get_label_anno` 读取。
  - LiDAR-based 模型训练 → 通过 `mmdet3d/datasets/kitti_dataset.py` 的 `get_ann_info` 将 camera 系转换为 LiDAR 系。
  - Vision-based 模型训练 → 数据保持在 camera 系。
- **关键参数（原文）**：
  - Yaw=0.5*π = π/2 对应 y 轴正方向。
  - Yaw=π 对应 x 轴负方向（即 left 方向）。
  - Box 方向与 `dx` 边始终平行。

---

## 【表格解读】

**原文无表格**。文中通过 ASCII 示意图和 PNG 图片（`coord_sys_all.png`、`kittibox.png`）展示三类坐标系的轴向、yaw 角取值以及 box 维度与轴的对应关系，并未使用表格形式归纳。

---

## 【公式解读】

**原文无独立公式块**，但在文中以行内 LaTeX 形式给出了以下关键数学表达：

| 原式 | 符号含义 |
|------|---------|
| `(x, y, z, dx, dy, dz, r)` | 3D 边界框的统一表示形式：x, y, z 为框中心点在对应坐标轴上的位置；dx, dy, dz 为沿 x、y、z 轴方向的尺寸；r 为 yaw 角（绕重力轴的旋转角）。 |
| `(w, l, h)` | KITTI 原始（SECOND 定义）的 box 尺寸，其中 w 对应 `dy`，l 对应 `dx`，h 对应 `dz`。 |
| `(l, w, h)` | MMDetection3D LiDAR 系下的 box 尺寸，将 SECOND 的 w 和 l 顺序对调，与 `(dx, dy, dz)` 的轴对应关系一致。 |
| `(dy, dx)` 或 `(w, l)` | NuScenes `Box` 实例中尺寸前两维的顺序，与 MMDetection3D 的 LiDAR 系相反。 |
| `r` | 边界框的 yaw 角，取值范围通常为 [−π, π]。 |
| `\Pi` | 与重力轴垂直的平面，所有 yaw 角的取值在该平面内定义。 |
| `\frac{\pi}{2}` | 当 box 方向与 y 轴正方向平行时对应的 yaw 角。 |

---

## 【关联】

- **核心模块**：本文是 MMDetection3D 的基础教程之一，定义了 Camera / LiDAR / Depth 三大坐标系，是所有 3D 检测器（LiDAR-based、Vision-based）的数据预处理与评估基准。
- **数据转换工具**：与 `tools/data_converter/kitti_data_utils.py`（`get_label_anno`）以及 `mmdet3d/datasets/kitti_dataset.py`（`get_ann_info`）直接关联。
- **上游历史工作**：与 SECOND 的 LiDAR 系（`https://github.com/traveller59/second.pytorch`）和 VoteNet / H3DNet 的 Depth 系存在约定差异，文档明确说明了修改点。
- **下游数据集支持**：覆盖 KITTI、Waymo（KITTI 格式）、NuScenes、Lyft、ScanNet 五大数据集的坐标系约定，并引用了 NuScenes devkit 的 `Box` 定义（`data_classes.py`）与评估实现（`evaluate.py`）。
- **关联教程**：与 NuScenes 数据集教程（`docs/en/datasets/nuscenes_det.md#notes`）相互引用。

---

## 【使用方法】

原文未给出显式的启用命令或配置项，但其使用约定可归纳如下：

1. **数据格式统一**：在 MMDetection3D 中，所有数据集的标注需先转换到 Camera / LiDAR / Depth 三类坐标系之一，且遵循 `(x, y, z, dx, dy, dz, r)` 的 box 表示格式。
2. **KITTI 数据处理**：
   - 读取原始标注：`get_label_anno`（位于 `tools/data_converter/kitti_data_utils.py`）。
   - 转换为 LiDAR 系用于 LiDAR-based 模型训练：`get_ann_info`（位于 `mmdet3d/datasets/kitti_dataset.py`）。
   - 用于 vision-based 模型时，保持 camera 系不变。
3. **NuScenes 数据处理**：注意 box 尺寸顺序为 `(w, l)` 而非 `(l, w)`，可通过 NuScenes 官方 devkit 进行评估。
4. **ScanNet 数据处理**：采样点云已处于 Depth 系；检测任务中 box 始终 axis-aligned，yaw 角固定为 0，无需进行 yaw 相关的旋转处理。

> 注：原文未涉及具体的配置文件路径、命令行参数或 API 调用示例，相关配置需结合 MMDetection3D 的 config 体系另行查阅。

## 图文联合解读

- `coord_sys_all.png`: # 图文联合解读

**1) 图中内容：** 图分三列（Depth/LiDAR/Camera），每列上半部分展示三维坐标系轴向定义（z轴方向各异），下半部分为俯视/侧视示意图，用红色矩形框表示检测框，标注尺寸(dx/dy/dz)、朝向(box dir)和偏航角Ψ的正负取值。

**2) 技术结论：** 不同传感器坐标系下，同一物体框的"长边dx"对应轴不同（Depth/LiDAR中沿x，CAMERA中沿x），且偏航角Ψ的正负约定也不同——Depth取Ψ>0，LiDAR与Camera取Ψ<0，即存在90°旋转换算关系。

**3) 与文档关系：** 该图直观印证了文档论点"三种坐标系不一致"的复杂性，呼应了"LiDAR与Camera坐标系转换繁琐"这一核心议题，为后续坐标系转换提供视觉参考。
- `kittibox.png`: **图文解读：**

1）图示：一个倾斜放置的3D长方体（包围盒），顶面标注了两个θ角（偏航角yaw），内部含汽车图标，表示物体在3D空间中可绕垂直轴旋转。

2）技术结论：3D目标包围盒需用yaw角参数化朝向，而非简单轴对齐，说明3D检测中物体姿态描述与2D差异显著。

3）文档关系：呼应"三种坐标系并存需转换"的论点——yaw角是LiDAR与相机坐标系间旋转矩阵的核心分量，决定了同一物体在不同坐标系下的角度表示与转换方式。
