# 教程 6: 坐标系

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/autonoumous_driving/BEVDet_for_PyTorch/docs/zh_cn/tutorials/coord_sys_tutorial.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/autonoumous_driving/BEVDet_for_PyTorch/docs/zh_cn/tutorials/coord_sys_tutorial.md

# 深度解读：MMDetection3D 坐标系教程

---

## 【定位】

本文系统定义并规范化 MMDetection3D 在 3D 目标检测中使用的三种坐标系（相机 / 激光雷达 / 深度坐标系），统一框参数 `(x, y, z, dx, dy, dz, r)` 中尺寸与 yaw 角的语义，并给出坐标系间（含 KITTI、Waymo、NuScenes、Lyft、ScanNet、SUN RGB-D、S3DIS 等支持数据集）的转换规则与旋转/鸟瞰图投影等关键操作的实现依据。

---

## 【技术要点】

1. **三种坐标系的轴向定义**（右手系，重力轴分别指向 y 负 / z 正 / z 正）：
   - **相机坐标系**：x 轴→右、y 轴→下、z 轴→前；
   - **激光雷达坐标系**：x 轴→前、y 轴→左、z 轴→上；
   - **深度坐标系**（VoteNet、H3DNet）：x 轴→右、y 轴→前、z 轴→上。

2. **统一框参数格式** `(x, y, z, dx, dy, dz, r)`：在三个坐标系下，dx / dy / dz 始终对应 x / y / z 三个轴方向上的框尺寸（前提是 yaw=0 时框方向与 x 轴正方向平行），yaw `r` 的参考方向固定为 x 轴正方向。

3. **yaw 旋转方向约定**：所有坐标系都是右手系，从重力轴的负方向（轴正方向指向人眼）看向平面 Π 时，yaw 逆时针增加；例：x 轴正方向的 yaw=0，y 轴正方向的 yaw=π/2。

4. **相机 → 激光雷达 的转换公式**（点、尺寸、yaw 各自不同映射）：
   - 点：`x_LiDAR = z_camera`，`y_LiDAR = -x_camera`，`z_LiDAR = -y_camera`；
   - 尺寸：`dx_LiDAR = dx_camera`，`dy_LiDAR = dz_camera`，`dz_LiDAR = dy_camera`；
   - yaw：`r_LiDAR = -π/2 − r_camera`。

5. **相机坐标系下的鸟瞰图投影**：`(x, z, dx, dz, -r)`，yaw 取负的原因是相机坐标系 y 轴正方向指向地面（重力轴正向指向地面）。

6. **框旋转规则**：旋转设置为绕重力轴逆时针旋转 → 即在原中心基础上将 yaw 加上旋转角度。

7. **算子与坐标系耦合**（原文 FAQ）：
   - RoI-Aware Pooling（`mmcv/ops/roiaware_pool3d.py`）只适用于深度 / 激光雷达坐标系下的框；
   - KITTI 评估函数（`mmdet3d/core/evaluation/kitti_utils.py`）只适用于相机坐标系下的框（因俯视下旋转方向为顺时针）；
   - 每个框相关算子都标注了其适用的框类型。

8. **yaw 的 2π / π 相位差影响**：2π 相位差对 IoU 与角度预测评估均无影响；π 相位差对 IoU 无影响但对角度预测是"完全相反方向"，对前后无差别的类别（障碍物）不影响分数。

---

## 【关键机制与数据】

### 工作原理 / 数据流

1. **坐标系选择动机**（原文："早期工作如 SECOND、VoteNet 将原始数据转换为另一种格式，形成了一些后续工作也遵循的约定，使得不同坐标系之间的转换变得更加复杂"）：本文统一定义后，使 MMDetection3D 内部表示与各家数据集原始表示解耦。

2. **数据流（以 KITTI 为例）**：
   - KITTI 原始标注在**相机坐标系**下（详见 `tools/data_converter/kitti_data_utils.py::get_label_anno`）；
   - 训练基于激光雷达的模型时，由 `mmdet3d/datasets/kitti_dataset.py::get_ann_info` 将数据从相机坐标系**转换到激光雷达坐标系**；
   - 训练基于视觉的模型时，数据**保持在相机坐标系**不变。

3. **维度解释的额外维度**：原文关键表述"我们的坐标系不仅仅是定义三个轴"，对于 `(x, y, z, dx, dy, dz, r)` 形式，坐标系同时还规定了 `(dx, dy, dz)` 与 yaw `r` 的几何语义（即 dx 对应 x 轴方向长度，yaw=0 时方向与 x 轴正方向平行）。

4. **Waymo 复用 KITTI 坐标系**：原文："我们使用 Waymo 数据集的 KITTI 格式数据。因此在我们的实现中 KITTI 和 Waymo 也共用相同的坐标系。"

5. **NuScenes 与激光雷达坐标系的差异**：`Box` 坐标系前两个尺寸元素为 `(dy, dx)` 或 `(w, l)`，与本框架 `(dx, dy)` 顺序相反。

6. **ScanNet / S3DIS 特殊性**：框标注是轴对齐的，yaw 恒为 0，因此深度坐标系下 yaw 方向定义对其无影响（S3DIS 还仅用于分割，没有坐标系敏感的标注）。

7. **SUN RGB-D**：原始为 RGB-D 图像 → 反投影得到深度坐标系下点云 → 但原始标注不在该系统 → 需转换（详见 `tools/data_converter/sunrgbd_data_utils.py`）。

> 性能数据：原文未涉及任何基准/性能数据。

---

## 【表格解读】

原文无表格。

---

## 【公式解读】

原文共有以下显式公式（逐字保留原 LaTeX 表达）：

### F1. 框参数统一表示
`$$`(x, y, z, dx, dy, dz, r)`$$`

- **x, y, z**：框中心点在对应坐标系中的坐标；
- **dx, dy, dz**：框在 x、y、z 三个轴方向上的尺寸（当 yaw=0 时）；
- **r**：框的 yaw 转向角，参考方向为 x 轴正方向。

### F2. 框尺寸的语义
`$$`(dx, dy, dz)`$$`

- 当框的方向（heading）与 x 轴正方向平行时，dx 是其沿 x 轴的长度；dx 边始终与框的方向平行。

### F3. 重力轴上方视角下 y 轴正方向 yaw
`$$`\frac{\pi}{2}`$$`

- 解释：在右手系中，从重力轴负方向（轴正方向指向人眼）俯视，逆时针为 yaw 增加方向；x 轴正方向的 yaw=0，故 y 轴正方向的 yaw=π/2。

### F4. 相机 → 激光雷达 点坐标转换
`$$`x_{LiDAR}=z_{camera}`$$`
`$$`y_{LiDAR}=-x_{camera}`$$`
`$$`z_{LiDAR}=-y_{camera}`$$`

- x_LiDAR = z_camera：相机前（z 前）对应激光雷达前（x 前）；
- y_LiDAR = −x_camera：激光雷达左（y 左）对应相机右的反方向；
- z_LiDAR = −y_camera：激光雷达上（z 上）对应相机下（y 下）的反方向。

### F5. 相机 → 激光雷达 框尺寸转换
`$$`dx_{LiDAR}=dx_{camera}`$$`
`$$`dy_{LiDAR}=dz_{camera}`$$`
`$$`dz_{LiDAR}=dy_{camera}`$$`

- 因 x_LiDAR 对应 z_camera，故 dx_LiDAR=dx_camera 直接复用；
- 因 y_LiDAR 对应 −x_camera 而尺寸为绝对值，故 dy_LiDAR = dz_camera；
- 因 z_LiDAR 对应 −y_camera 而尺寸为绝对值，故 dz_LiDAR = dy_camera。

### F6. 相机 → 激光雷达 yaw 转换
`$$`r_{LiDAR}=-\frac{\pi}{2}-r_{camera}`$$`

- 即在原始 r_camera 基础上取反并旋转 −π/2，使其与 x_LiDAR 方向对齐（右手系 + 参考方向为 x 轴正方向）。

### F7. 相机坐标系下 3D 框到鸟瞰图的投影
`$$`(x, z, dx, dz, -r)`$$`

- 因相机 y 正方向指向地面（重力轴正方向向下），俯视即在 y=0 平面看 → 使用 x、z 平面坐标；
- 因 y 轴向下，yaw 取负以保持视觉上与 LiDAR/深度坐标系下一致的逆时针定义。

### F8. yaw 等价的两种相位表示

`$$`2\pi`$$` 与 `$$`\pi`$$` 的相位差方程（语义性）：

- IoU 计算时：`r` 与 `r+2π` 等价、`r` 与 `r+π` 等价（同样的旋转角对应同一方框）；
- 角度预测评估时：`r` 与 `r+2π` 在评估前被归一化为等价；`r` 与 `r+π` 表示"完全相反方向"（如汽车前后颠倒），仅对前/后无区别的类别不影响分数。

---

## 【关联】

本文是 MMDetection3D 几何与数据流层的基础规范文档，与以下模块/特性强耦合：

1. **数据转换器（上游）**
   - `tools/data_converter/kitti_data_utils.py::get_label_anno` —— KITTI 相机坐标系原始标注解析；
   - `tools/data_converter/sunrgbd_data_utils.py` —— SUN RGB-D 转深度坐标系；
   - `mmdet3d/datasets/kitti_dataset.py::get_ann_info` —— KITTI 相机 → LiDAR 坐标系转换。

2. **框结构与转换算子（核心实现）**
   - `mmdet3d/core/bbox/structures/box_3d_mode.py` —— 相机/LiDAR/深度坐标系框互转（含本文 F4–F6 公式）；
   - `mmdet3d/core/bbox/structures/cam_box3d.py` —— 相机框鸟瞰图投影（F7）与旋转（绕重力轴逆时针）。

3. **评估与算子（下游，强耦合坐标系）**
   - `mmdet3d/core/evaluation/kitti_utils.py` —— 仅适用于相机坐标系下的框；
   - `mmcv/ops/roiaware_pool3d.py`（RoI-Aware Pooling）—— 仅适用于深度 / 激光雷达坐标系；
   - NuScenes 评估：NDS 指标对 yaw 进行归一化处理，受 2π 相位差不影响结论，但受 π 相位差影响方向（前后无差别类别除外）；
   - KITTI AOS 指标：同样先做角度归一化。

4. **支持的数据集与坐标系映射**
   - 相机坐标系：KITTI（基于视觉的模型）、KITTI 评估代码；
   - 激光雷达坐标系：KITTI（基于激光雷达的模型）、Waymo；
   - 深度坐标系：VoteNet / H3DNet 等模型、ScanNet、S3DIS、SUN RGB-D（经转换后）；
   - NuScenes / Lyft：`Box` 系统的 `(dy, dx)` 表示与本文的 `(dx, dy)` 相反。

5. **可视化**：通过本文统一的坐标约定，使得三个坐标系的图示（`resources/coord_sys_all.png` 上三张 3D 图、下三张鸟瞰图）可直接对照。

---

## 【使用方法】

> 原文未提供显式的启用命令或配置项。但相关隐含约束如下：

- **新增加载数据集**：需按本文定义的轴向，将原始标注归一化到本文三套坐标系之一（相机 / 激光雷达 / 深度）；
- **调用框相关算子**：需确保框类型（相机 / 激光雷达 / 深度）与算子适用范围匹配——例如 RoI-Aware Pooling 仅用于深度 / LiDAR 框；KITTI 评估仅用于相机框；
- **相机坐标系训练视觉模型 / 训练激光雷达模型**：分别保持相机坐标系或先调用 `box_3d_mode.py` 转换到 LiDAR 坐标系；
- **实现自定义旋转或鸟瞰图投影**：参考 `cam_box3d.py`，遵循"绕重力轴逆时针旋转"与"相机系鸟瞰图取负 yaw"的规则；
- **NuScenes / Lyft**：由于 `Box` 系统的尺寸顺序与本文相反，使用前需参考 NuScenes 教程完成 `(w, l) → (dx, dy)` 顺序对齐。

## 图文联合解读

- `coord_sys_all.png`: **图文联合解读：**

1) 图含三列（Depth/LiDAR/Camera），上排为3D坐标轴定义，下排为鸟瞰图，展示红色检测框的尺寸（dx/dy/dz）、box dir方向箭头及yaw角（Ψ>0或Ψ<0）的正负约定。

2) 论证三种坐标系在轴向、尺寸语义和转向角符号上规则各异：Depth以+x为前、Ψ>0；LiDAR以+x为前但+y向左、Ψ<0；Camera的鸟瞰面在x-z平面，框尺寸对应dx/dz。

3) 对应文档"三套坐标系定义不仅定轴，还定义框参数解释"的论点，图为后续yaw/box参数转换提供视觉基准。
- `kittibox.png`: **图文解读：**

图示展示了3D目标检测框的偏航角(yaw)定义——长方体表示物体包围盒，倾斜放置以说明绕重力轴(向下)的旋转角度θ。

**论证结论：** yaw角定义了物体朝向，是7维框参数(x,y,z,dx,dy,dz,r)中的关键一维。

**与文档关系：** 配合相机/激光雷达/深度坐标系定义，阐明三个坐标系下yaw轴对应的旋转语义，统一不同数据集的朝向标注规范。
