# 教程 2: 增加新的数据集

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/cv/pose_estimation/HRNet_MMPose_for_PyTorch/docs/zh_cn/tutorials/2_new_dataset.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/cv/pose_estimation/HRNet_MMPose_for_PyTorch/docs/zh_cn/tutorials/2_new_dataset.md

# HRNet_MMPose_for_PyTorch 教程 2：增加新的数据集 — 深度解读

---

## 【定位】

这篇文档解决"如何在 MMPose 姿态估计框架（HRNet 实现）中接入一个非内置的自定义关键点检测数据集"的问题——通过"标注格式转换 → 数据集元信息配置 → 自定义数据集类注册 → 训练配置改写"四步流程，让用户将自己的数据集以最小侵入方式融入 MMPose 训练/评测流水线。

---

## 【技术要点】

1. **COCO 格式转换**：自定义数据集的标注 json 必须包含三个顶层关键字 `images`、`annotations`、`categories`，对应"图片元信息"、"实例标注"、"类别定义"。其中 `annotations` 中关键点以 `[x, y, v]` 三元组扁平数组存储（v 是可见性标志，0 表示未标注、1 表示已标注但不可见、2 表示已标注且可见）。
3. **数据集元信息配置**：在 `configs/_base_/datasets/custom.py` 中创建 `dataset_info`，由四个子结构组成——`keypoint_info`（每个关键点的 5 字段定义）、`skeleton_info`（关键点骨架连接）、`joint_weights`（每关键点损失权重，长度 17）、`sigmas`（OKS 计算用，长度 17）。
5. **关键点元信息 5 字段**：`name`（唯一名称）、`id`（标识号）、`color`（BGR 可视化颜色）、`type`（'upper' / 'lower'，用于数据增强）、`swap`（水平镜像对称关键点名称）。
7. **数据集类注册**：在 `mmpose/datasets/datasets/custom/` 下建立子包，使用 `@DATASETS.register_module(name='MyCustomDataset')` 装饰类定义，并通过 `__init__.py` 暴露，同时更新 `mmpose/datasets/__init__.py`。
9. **训练配置改写**：在 `configs/my_custom_config.py` 中设置 `dataset_type = 'MyCustomDataset'`，并在 `data` dict 的 `train/val/test` 三个子项中分别指定 `type`、`ann_file`（json 路径）、`img_prefix`（图片目录）。默认 `samples_per_gpu=2`、`workers_per_gpu=2`。

---

## 【关键机制与数据】

**工作原理（数据流）**：

原始自定义数据集 → 用户脚本转换为 COCO 风格 json + 图像目录 → 在 `configs/_base_/datasets/custom.py` 中声明该数据集的关键点拓扑与权重 → 在 `mmpose/datasets/datasets/custom/` 下实现一个继承自合适基类的 Dataset 类并通过注册器暴露 → 在训练配置中通过 `dataset_type` 字符串引用 → MMPose 训练时通过 `ann_file` + `img_prefix` 加载样本，按 `keypoint_info` 完成数据增强（如 `type='upper'/'lower'` 区分上下半身用于对称增强）、按 `joint_weights` 计算每关键点损失、按 `sigmas` 在评估阶段计算 OKS。

**原文中的关键数值**（来自 `dataset_info` 示例配置）：
- `joint_weights`（17 个标量）：`[1., 1., 1., 1., 1., 1., 1., 1.2, 1.2, 1.5, 1.5, 1., 1., 1.2, 1.2, 1.5, 1.5]`——可观察到"肘/膝 = 1.2"、"腕/踝 = 1.5"等远端关键点权重被调高。
- `sigmas`（17 个标量）：`[0.026, 0.025, 0.025, 0.035, 0.035, 0.079, 0.079, 0.072, 0.072, 0.062, 0.062, 0.107, 0.107, 0.087, 0.087, 0.089, 0.089]`——按关键点归一化尺度因子，用于 OKS 评估。
- `keypoint_info` 共定义 17 个关键点（鼻子 1 + 双眼 2 + 双耳 2 + 双肩 2 + 双肘 2 + 双腕 2 + 双髋 2 + 双膝 2 + 双踝 2 = 17）。
- `skeleton_info` 共定义 19 条骨架边。

**类型增强机制**：`type='upper'` / `type='lower'` 的二分类用于在数据增强阶段区分上下半身，配合 `swap` 字段实现"左右镜像翻转"时同步交换左右关键点标签。

**OKS 机制**：`sigmas` 字段参与 Object Keypoint Similarity 计算（原文链接到 [cocodataset.org/#keypoints-eval](https://cocodataset.org/#keypoints-eval)），用以衡量预测关键点与真值关键点的相似度，是 COCO 关键点评估的核心指标。

---

## 【表格解读】

> 原文无独立的 markdown 表格。但 `dataset_info` 代码块本身就是一份"配置项字典"，可视为一张结构化表格。下方按"keypoint_info / skeleton_info / joint_weights / sigmas"四张子表逐字还原并解读。

### 表 A：`keypoint_info`（17 个关键点定义，原文逐字）

| id | name | color (BGR) | type | swap |
|---|---|---|---|---|
| 0 | nose | [51, 153, 255] | upper | '' |
| 1 | left_eye | [51, 153, 255] | upper | right_eye |
| 2 | right_eye | [51, 153, 255] | upper | left_eye |
| 3 | left_ear | [51, 153, 255] | upper | right_ear |
| 4 | right_ear | [51, 153, 255] | upper | left_ear |
| 5 | left_shoulder | [0, 255, 0] | upper | right_shoulder |
| 6 | right_shoulder | [255, 128, 0] | upper | left_shoulder |
| 7 | left_elbow | [0, 255, 0] | upper | right_elbow |
| 8 | right_elbow | [255, 128, 0] | upper | left_elbow |
| 9 | left_wrist | [0, 255, 0] | upper | right_wrist |
| 10 | right_wrist | [255, 128, 0] | upper | left_wrist |
| 11 | left_hip | [0, 255, 0] | lower | right_hip |
| 12 | right_hip | [255, 128, 0] | lower | left_hip |
| 13 | left_knee | [0, 255, 0] | lower | right_knee |
| 14 | right_knee | [255, 128, 0] | lower | left_knee |
| 15 | left_ankle | [0, 255, 0] | lower | right_ankle |
| 16 | right_ankle | [255, 128, 0] | lower | left_ankle |

**解读**：颜色编码体现三类语义——头部用 `[51,153,255]`（蓝色调）、身体左侧肢体用 `[0,255,0]`（绿色）、身体右侧肢体用 `[255,128,0]`（橙色），左右严格区分以方便可视化辨识；`type` 列显示躯干分割：上半身含 nose/eye/ear/shoulder/elbow/wrist，下半身含 hip/knee/ankle；`swap` 列成对镜像对称（如 `left_shoulder ↔ right_shoulder`），用于水平翻转增强时同步重命名。

### 表 B：`skeleton_info`（19 条骨架边，原文逐字）

| id | link | color (BGR) |
|---|---|---|
| 0 | (left_ankle, left_knee) | [0, 255, 0] |
| 1 | (left_knee, left_hip) | [0, 255, 0] |
| 2 | (right_ankle, right_knee) | [255, 128, 0] |
| 3 | (right_knee, right_hip) | [255, 128, 0] |
| 4 | (left_hip, right_hip) | [51, 153, 255] |
| 5 | (left_shoulder, left_hip) | [51, 153, 255] |
| 6 | (right_shoulder, right_hip) | [51, 153, 255] |
| 7 | (left_shoulder, right_shoulder) | [51, 153, 255] |
| 8 | (left_shoulder, left_elbow) | [0, 255, 0] |
| 9 | (right_shoulder, right_elbow) | [255, 128, 0] |
| 10 | (left_elbow, left_wrist) | [0, 255, 0] |
| 11 | (right_elbow, right_wrist) | [255, 128, 0] |
| 12 | (left_eye, right_eye) | [51, 153, 255] |
| 13 | (nose, left_eye) | [51, 153, 255] |
| 14 | (nose, right_eye) | [51, 153, 255] |
| 15 | (left_eye, left_ear) | [51, 153, 255] |
| 16 | (right_eye, right_ear) | [51, 153, 255] |
| 17 | (left_ear, left_shoulder) | [51, 153, 255] |
| 18 | (right_ear, right_shoulder) | [51, 153, 255] |

**解读**：19 条边分为三类颜色——四肢（绿色/橙色，按左右区分）、躯干与头部（蓝色 `[51,153,255]`）；可见这是一个无向骨架（边由两端点命名构成元组），涵盖腿（2 条）、髋部横连、躯干（4 条）、手臂（4 条）、头部（7 条：双眼横连、双鼻眼、双眼耳、双耳肩）。

### 表 C：`joint_weights`（17 个标量，原文逐字）

| 索引→权重 |
|---|
| 0→1.0, 1→1.0, 2→1.0, 3→1.0, 4→1.0, 5→1.0, 6→1.0, 7→1.2, 8→1.2, 9→1.5, 10→1.5, 11→1.0, 12→1.0, 13→1.2, 14→1.2, 15→1.5, 16→1.5 |

**解读**：权重排序遵循"越远离躯干、训练难度越大 → 权重越高"的策略——躯干（nose/eye/ear/shoulder/hip）= 1.0，中间关节（elbow/knee）= 1.2，末端（wrist/ankle）= 1.5，用于在多任务 MSE 损失中放大难关键点的梯度。

### 表 D：`sigmas`（17 个标量，原文逐字）

| 索引→sigma |
|---|
| 0→0.026, 1→0.025, 2→0.025, 3→0.035, 4→0.035, 5→0.079, 6→0.079, 7→0.072, 8→0.072, 9→0.062, 10→0.062, 11→0.107, 12→0.107, 13→0.087, 14→0.087, 15→0.089, 16→0.089 |

**解读**：sigma 越大表示该关键点评估时允许的偏差越大（人眼/耳/髋 ≈ 0.1 较宽松，nose/eye ≈ 0.026 较严格），反映"小且精确部位更难定位"的先验。

---

## 【公式解读】

原文无显式数学公式。但文档提及"OKS 得分"并链向 [keypoints-eval](https://cocodataset.org/#keypoints-eval)，其参考定义为：

$$
\mathrm{OKS} = \frac{\sum_i \exp\!\left(-\frac{d_i^{2}}{2 s^{2} \sigma_i^{2}}\right) \delta(v_i > 0)}{\sum_i \delta(v_i > 0)}
$$

符号含义（原文未直接给出，但属 OKS 通用定义）：
- $d_i$：第 $i$ 个关键点预测与真值的欧氏距离。
- $s$：目标检测框面积（或等价尺度因子）。
- $\sigma_i$：即文档中 `sigmas` 列表的第 $i$ 个值——控制第 $i$ 个关键点的"容差半径"。
- $v_i$：第 $i$ 个关键点的可见性标志（来自 `keypoints` 数组第 3 元组位）。
- $\delta(v_i>0)$：指示函数，仅对已标注关键点计入分子分母。

> 注：上述公式为 COOK 官方原文未显式给出的通用定义，仅供理解 `sigmas` 的作用；本文档**未出现该公式文字**。

---

## 【关联】

文档文末给出的"内部链接信息"为**（无）**。但从文档自身描述可识别出以下隐含上下游关系：

- **上游（数据层）**：用户原始标注 → COCO json + 图像目录（即本文档第 1 节）。
- **本层（元信息层）**：`configs/_base_/datasets/custom.py` 中的 `dataset_info`，被 MMPose 训练循环中的**数据增强模块**（消费 `type`/`swap`）、**损失函数**（消费 `joint_weights`）、**评估模块**（消费 `sigmas` 计算 OKS）共同调用。
- **下游（数据加载层）**：`mmpose/datasets/datasets/custom/MyCustomDataset.py` + 注册器，被 `configs/my_custom_config.py` 中的 `dataset_type='MyCustomDataset'` 字符串引用。
- **与 MMPose 标准数据集的并行关系**：本流程与 COCO / MPII / AIC 等内置数据集走同一条 pipeline，区别仅在于 (a) `dataset_info` 需自定义、(b) Dataset 类需继承并暴露自定义基类。

---

## 【使用方法】

原文显式涉及的使用方式如下：

1. **启用方式（条件）**：用户必须准备好"图像目录 + 转换为 COCO 格式的 json 标注文件"两件套。
2. **配置项**：
   - `configs/_base_/datasets/custom.py`：放置 `dataset_info`。
   - `mmpose/datasets/datasets/custom/__init__.py`：暴露自定义数据集类。
   - `mmpose/datasets/__init__.py`：注册新包。
   - `configs/my_custom_config.py`：设置 `dataset_type='MyCustomDataset'`、`ann_file`、`img_prefix` 三处。
3. **训练配置片段**（原文逐字）：
   ```python
   dataset_type = 'MyCustomDataset'
   data = dict(
       samples_per_gpu=2,
       workers_per_gpu=2,
       train=dict(type=dataset_type, ann_file='path/to/your/train/json', img_prefix='path/to/your/train/img', ...),
       val=dict(type=dataset_type, ann_file='path/to/your/val/json', img_prefix='path/to/your/val/img', ...),
       test=dict(type=dataset_type, ann_file='path/to/your/test/json', img_prefix='path/to/your/test/img', ...))
   ```
4. **注册命令**（原文逐字）：
   ```python
   @DATASETS.register_module(name='MyCustomDataset')
   class MyCustomDataset(SomeOtherBaseClassAsPerYourNeed):
       ...
   ```
5. **启动命令**：原文未涉及训练启动命令本身（无 `python tools/train.py` 等调用示例）。
