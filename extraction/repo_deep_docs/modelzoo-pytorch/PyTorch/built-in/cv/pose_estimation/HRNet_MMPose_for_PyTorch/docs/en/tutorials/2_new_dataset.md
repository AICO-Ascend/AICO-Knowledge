# Tutorial 2: Adding New Dataset

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/cv/pose_estimation/HRNet_MMPose_for_PyTorch/docs/en/tutorials/2_new_dataset.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/cv/pose_estimation/HRNet_MMPose_for_PyTorch/docs/en/tutorials/2_new_dataset.md

# 深度解读:Tutorial 2: Adding New Dataset

## 【定位】

本文档是 MMPose(HRNet_MMPose_for_PyTorch)中面向开发者的**自定义数据集接入教程**,解决"如何将自有数据集接入 MMPose 训练/评估流程"这一工程问题,通过 COCO 标注格式 + 配置文件 + 数据集类三步法,实现对新数据集的最小侵入式适配。

---

## 【技术要点】

1. **COCO 标注格式归一化(三条核心键)**:`images`(含 `file_name`/`height`/`width`/`id`)、`annotations`(实例级标注)、`categories`(类别名与 ID)。
2. **`dataset_info` 配置文件结构**:放置于 `configs/_base_/datasets/custom.py`,由 `keypoint_info`、`skeleton_info`、`joint_weights`、`sigmas` 四大字段组成。
3. **`keypoint_info` 五要素**:① `name`(全局唯一关键点名)、② `id`、③ `color`(BGR 顺序,可视化用)、④ `type`(`'upper'` 或 `'lower'`,数据增强用)、⑤ `swap`(水平翻转配对名)。
4. **Registry 模式注册数据集类**:在包目录下用 `@DATASETS.register_module(name='MyCustomDataset')` 装饰自定义类,需同步更新两级 `__init__.py`,否则会抛 `KeyError: 'XXXXX is not in the dataset registry'`。
5. **训练配置 `data` 字典**:通过 `dataset_type = 'MyCustomDataset'` 绑定数据集类,再在 `train`/`val` 子字典中分别指定 `ann_file` 与 `img_prefix`。
6. **OKS 评估机制**:依赖 `sigmas` 数组计算 OKS(Object Keypoint Similarity),原文给出外部链接 https://cocodataset.org/#keypoints-eval 作为原理参考。

---

## 【关键机制与数据】

- **数据流**:用户标注 → 转换为 COCO JSON → 编写 `dataset_info` 描述关键点拓扑与权重 → 注册自定义 Dataset 类 → 在 `configs/my_custom_config.py` 中通过 `dataset_type` 引用 → 训练/评估管线消费。
- **关键点分组语义**(原文):`type='upper'` 用于上半身关键点(头/眼/耳/肩/肘/腕),`type='lower'` 用于下半身关键点(髋/膝/踝),在数据增强阶段据此区分处理策略。
- **关键点损失权重差异**(原文,`joint_weights`):
  - 肘部(`left_elbow`/`right_elbow`,id 7–8):权重 **1.2**
  - 腕部(`left_wrist`/`right_wrist`,id 9–10):权重 **1.5**
  - 膝部(`left_knee`/`right_knee`,id 13–14):权重 **1.2**
  - 踝部(`left_ankle`/`right_ankle`,id 15–16):权重 **1.5**
  - 其余关键点(头面部、肩、髋):权重 **1.0**
- **OKS 尺度参数 sigma**(原文):取值范围 **0.025 ~ 0.107**,眼/耳/鼻最小(0.025–0.035),髋部最大(0.107),与人体部位尺度对应。
- **颜色编码**(原文 BGR):面部/头颈连接用 `[51, 153, 255]`(蓝色系),左侧肢体用 `[0, 255, 0]`(绿色),右侧肢体用 `[255, 128, 0]`(橙色)。
- **COCO annotation 实例字段**(原文示例值):`num_keypoints=10`、`area=3894.5826`、`iscrowd=0`、`bbox=[402.34, 205.02, 65.26, 88.45]`、`category_id=1`、`image_id=1268`。

---

## 【表格解读】

> 注:原文以 Python dict / JSON 代码块呈现,以下用 markdown 表格**逐字还原**其结构化数据。

### 表 1:`keypoint_info` — 17 个 COCO 人体关键点

| id | name | color (BGR) | type | swap |
|----|------|-------------|------|------|
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

**逐行解读**:关键点命名按部位+左/右(left/right)构成唯一标识;`swap` 形成 8 对左右镜像(nose 无 swap,因其为正中);`color` 与 `skeleton_info` 一致——面部连接用蓝色,左侧肢体绿色,右侧肢体橙色,便于可视化时区分左右。

### 表 2:`skeleton_info` — 19 条骨架连接(用于可视化)

| id | link | color (BGR) | 部位归属 |
|----|------|-------------|----------|
| 0 | (left_ankle, left_knee) | [0, 255, 0] | 左下肢 |
| 1 | (left_knee, left_hip) | [0, 255, 0] | 左下肢 |
| 2 | (right_ankle, right_knee) | [255, 128, 0] | 右下肢 |
| 3 | (right_knee, right_hip) | [255, 128, 0] | 右下肢 |
| 4 | (left_hip, right_hip) | [51, 153, 255] | 躯干横连 |
| 5 | (left_shoulder, left_hip) | [51, 153, 255] | 左躯干 |
| 6 | (right_shoulder, right_hip) | [51, 153, 255] | 右躯干 |
| 7 | (left_shoulder, right_shoulder) | [51, 153, 255] | 肩部横连 |
| 8 | (left_shoulder, left_elbow) | [0, 255, 0] | 左上肢 |
| 9 | (right_shoulder, right_elbow) | [255, 128, 0] | 右上肢 |
| 10 | (left_elbow, left_wrist) | [0, 255, 0] | 左上肢 |
| 11 | (right_elbow, right_wrist) | [255, 128, 0] | 右上肢 |
| 12 | (left_eye, right_eye) | [51, 153, 255] | 面部 |
| 13 | (nose, left_eye) | [51, 153, 255] | 面部 |
| 14 | (nose, right_eye) | [51, 153, 255] | 面部 |
| 15 | (left_eye, left_ear) | [51, 153, 255] | 面部 |
| 16 | (right_eye, right_ear) | [51, 153, 255] | 面部 |
| 17 | (left_ear, left_shoulder) | [51, 153, 255] | 头颈左 |
| 18 | (right_ear, right_shoulder) | [51, 153, 255] | 头颈右 |

**逐行解读**:骨骼连线共 19 条,连接关系严格基于 COCO 17 关键点定义,`color` 与对应关键点保持一致——下肢/上肢按左右着色,躯干/面部统一蓝色,保证渲染时的人体结构可读性。

### 表 3:`joint_weights` 与 `sigmas`(逐关键点对齐)

| 关键点 id | name | joint_weights | sigmas |
|-----------|------|---------------|--------|
| 0 | nose | 1.0 | 0.026 |
| 1 | left_eye | 1.0 | 0.025 |
| 2 | right_eye | 1.0 | 0.025 |
| 3 | left_ear | 1.0 | 0.035 |
| 4 | right_ear | 1.0 | 0.035 |
| 5 | left_shoulder | 1.0 | 0.079 |
| 6 | right_shoulder | 1.0 | 0.079 |
| 7 | left_elbow | 1.2 | 0.072 |
| 8 | right_elbow | 1.2 | 0.072 |
| 9 | left_wrist | 1.5 | 0.062 |
| 10 | right_wrist | 1.5 | 0.062 |
| 11 | left_hip | 1.0 | 0.107 |
| 12 | right_hip | 1.0 | 0.107 |
| 13 | left_knee | 1.2 | 0.087 |
| 14 | right_knee | 1.2 | 0.087 |
| 15 | left_ankle | 1.5 | 0.089 |
| 16 | right_ankle | 1.5 | 0.089 |

**逐行解读**:`joint_weights` 显示越靠近肢端(腕/踝权重 1.5,肘/膝 1.2)的关节在损失中获得更高占比——原因为肢端定位更难、更需要关注;`sigmas` 则反映该部位在评估时的"允许偏差尺度",髋部最大(0.107)说明其标注不确定度最大,眼/鼻最小(0.025–0.026)代表标注最稳定。

---

## 【公式解读】

原文无公式。

(注:文中提及 OKS 评分依赖 `sigmas`,但未给出 OKS 的数学表达式,仅以链接 https://cocodataset.org/#keypoints-eval 指向 COCO 官方说明。)

---

## 【关联】

- **上游/外部依赖**:
  - COCO 数据集官方规范(标注格式、`keypoints-eval` 评估协议)→ 通过 https://cocodataset.org/#keypoints-eval 提供 OKS 计算依据。
  - COCO 2014 论文(Lin et al., "Microsoft COCO: Common Objects in Context")→ 在 `paper_info` 字段中以元数据形式记录作者、标题、会议、年份与首页。
- **下游/框架组件**:
  - **MMPose Registry 系统**(`@DATASETS.register_module`)→ 是数据类被训练管线识别的唯一入口,缺失注册或 `__init__.py` 未导入均会触发 `KeyError`。
  - **数据增强模块** → 消费 `keypoint_info.type='upper'/'lower'` 字段决定增强策略。
  - **可视化模块** → 消费 `keypoint_info.color` 与 `skeleton_info`。
  - **损失函数** → 消费 `joint_weights`。
  - **评估模块** → 消费 `sigmas` 计算 OKS。
- **配置层关系**:`configs/_base_/datasets/custom.py`(数据集元信息)被 `configs/my_custom_config.py`(训练配置)通过 `dataset_type` 字符串引用,后者又被 HRNet 主配置继承。
- **同系列教程**:本文为 "Tutorial 2",由命名推断属于 MMPose tutorials 系列,通常前序教程会涉及环境准备与模型运行(原文未列出该系列链接)。
- **代码模块路径**:`mmpose/datasets/datasets/` 为数据集类包的物理位置,需在该目录下新建子包并更新两级 `__init__.py`。

---

## 【使用方法】

原文给出的具体启用步骤与配置示例(逐字摘录):

### 1. 标注转换(将自定义数据集转为 COCO JSON)

JSON 中 `images` / `annotations` / `categories` 三个键为必备,其余可选字段(如 `iscrowd`、`area`、`num_keypoints`)按需填写。

### 2. 创建数据集信息配置

文件路径:**`configs/_base_/datasets/custom.py`**

需定义 `dataset_info` 字典,至少包含 `dataset_name`、`keypoint_info`、`skeleton_info`、`joint_weights`、`sigmas`。

### 3. 创建自定义数据集类

步骤:
1. 在 **`mmpose/datasets/datasets/`** 下新建子包(目录)。
2. 在子包内编写类定义,并通过装饰器注册:
   ```python
   @DATASETS.register_module(name='MyCustomDataset')
   class MyCustomDataset(SomeOtherBaseClassAsPerYourNeed):
   ```
3. 更新子包目录的 `__init__.py`(导入该类)。
4. 更新 `mmpose/datasets/datasets/` 父包目录的 `__init__.py`(使其被发现)。

### 4. 创建自定义训练配置

文件路径:**`configs/my_custom_config.py`**(可基于现有 config 修改)

```python
...
# dataset settings
dataset_type = 'MyCustomDataset'
...
data = dict(
    samples_per_gpu=2,
    workers_per_gpu=2,
    train=dict(
        type=dataset_type,
        ann_file='path/to/your/train/json',
        img_prefix='path/to/your/train/img',
        ...),
    val=dict(
        type=dataset_type,
        ann_file='path/to/your/val/json',
        img_prefix='path/to/your/val/img',
        ...),
    tes
```

> ⚠️ **重要提示**:原文末尾的代码块在 `tes` 处被截断(`tes` 推测应为 `test=dict(...)` 的开头),**测试集配置与后续命令(如训练启动命令)原文未完整给出**,实际启用需参考 MMPose 通用训练入口或同系列其他教程。
