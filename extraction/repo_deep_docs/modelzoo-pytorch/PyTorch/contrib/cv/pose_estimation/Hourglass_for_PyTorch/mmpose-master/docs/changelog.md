# Changelog

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/pose_estimation/Hourglass_for_PyTorch/mmpose-master/docs/changelog.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/pose_estimation/Hourglass_for_PyTorch/mmpose-master/docs/changelog.md

# mmpose Changelog 深度解读

---

## 【定位】

本文件是 mmpose 项目 v0.5.0 → v0.8.0 四个版本的版本变更日志（Changelog），系统记录每个版本的新特性（New Features）、Bug 修复与改进项（Improvements），重点反映 mmpose 在 **数据集覆盖范围**、**骨干网络扩展**、**任务类型增加（2D 人体 / 手部 / 全身 / 3D 人体形状恢复）** 及 **训练推理能力增强** 上的迭代轨迹，是理解该开源姿态估计库演进的核心文档。

---

## 【技术要点】

以下要点按版本顺序梳理，**所有 PR 号与版本日期均逐字保留自原文**：

### v0.8.0（31/10/2020）
1. **新增 3 个数据集**：CrowdPose（PR #195）、PoseTrack18（PR #220）、InterHand2.6M（PR #202）。
2. **新增对抗训练（adversarial training）用于 3D human shape recovery**（PR #192）。
3. **新增多阶段损失（multi-stage losses）**（PR #204）。
4. **新增 MPII demo**（PR #216）。
5. **支持返回 heatmaps 与 backbone features**（PR #196、#212）。
6. **支持 mmdetection 模型的不同返回格式**（PR #217）。

### v0.7.0（30/9/2020）
1. **新增 HMR 任务**——支持 3D human shape recovery（PR #157、#160、#161、#162）。
2. **新增 COCO-WholeBody 全身姿态估计数据集**（PR #133）。
3. **新增 Frei-hand、CMU Panoptic HandDB 2D 手部关键点数据集**（PR #125、#144）。
4. **新增 H36M 数据集**（PR #159）。
5. **新增 ShuffleNetv2 骨干网络**（PR #139）。
6. **支持基于关键指标的 best model 保存**（PR #127）。
7. **新增 hand demo 与 whole-body demo**（PR #115、#163）。

### v0.6.0（31/8/2020）
1. **新增 6 类骨干网络**：ResNext、SEResNet、ResNetV1D、MobileNetv2、ShuffleNetv1、CPM（Convolutional Pose Machine，PR #26、#56）。
2. **新增 4 个数据集**：AIChallenger（PR #87）、MPII（PR #55）、MPII-TRB（PR #19、#47、#48）、OCHuman（PR #70）。
3. **新增 OneHand10K 数据集，支持 2D 手部关键点估计**（PR #52）。
4. **新增 bottom-up inference**（PR #69）。
5. **支持 CPU 训练/验证/demo**（PR #34）。
6. **新增 Dockerfile**（PR #44）。
7. **修复 configs 中缺失 `test_pipeline` 的 Bug**（PR #14）。

### v0.5.0（21/7/2020）
1. **MMPose 正式发布（Initial Release）**。
2. 同时支持 **top-down 与 bottom-up 姿态估计**两条技术路线。
3. 宣称训练效率与精度 **高于 AlphaPose、HRNet 等其他主流代码库**（原文表述）。
4. 初始骨干网络支持：ResNet、HRNet、SCNet、**Hourglass**、HigherHRNet。

---

## 【关键机制与数据】

原文无性能数值（mAP/FLOPs 等均未给出），机制性信息均为**功能开关/能力声明**，逐条标注如下：

- **多阶段损失（multi-stage losses）**：原文仅声明「Support」，未给出损失函数形式、加权方式或 stage 数量等具体细节（v0.8.0）。
- **对抗训练（adversarial training）**：原文声明用于 3D human shape recovery（v0.8.0），未说明对抗样本生成方式或判别器结构。
- **bottom-up 推理**：v0.6.0 引入（PR #69），用于关键点关联，无需检测器先定位人体，是与 top-down 并列的另一条推断范式。
- **基于关键指标保存 best model**（PR #127）：v0.7.0 引入，原文未说明监控的具体指标名。
- **支持 mmdetection 不同返回格式**（PR #217）：v0.8.0 提供与 mmdet 推理结果格式的兼容能力，未说明具体格式映射规则。
- **宣称精度对比**：v0.5.0 Highlights 原文称「higher accuracy than other popular codebases (e.g. AlphaPose, HRNet)」——原文未提供实测数据支撑，属定性声明。

---

## 【表格解读】

**原文无表格**。本 Changelog 完全以版本为单位、按「Highlights / New Features / Bug Fixes / Improvements」四类标题组织成纯文本列表，无任何 markdown 表格、参数表或性能对比表。

---

## 【公式解读】

**原文无公式**。文档中未出现任何数学公式或伪代码。

---

## 【关联】

虽然 Changelog 本身未提供内部交叉链接，但文档通过外部链接与项目其他模块形成关联，整理如下：

| 关联对象 | 类型 | 关联版本 | 用途 |
|---|---|---|---|
| [modelzoo](https://mmpose.readthedocs.io/en/latest/model_zoo.html) | 项目内部文档（modelzoo 页） | v0.6.0、v0.7.0 | 多次「Enrich the modelzoo」声明指向该页，是骨干/数据集扩展能力的对外展示窗口 |
| CrowdPose、PoseTrack18、InterHand2.6M、COCO-WholeBody、Frei-hand、CMU Panoptic HandDB、H36M、OneHand10K、AIChallenger、MPII、MPII-TRB、OCHuman | 外部数据集仓库 | v0.6.0 → v0.8.0 | 数据接入上游，决定 mmpose 可训练任务的范围 |
| ResNext、SEResNet、ResNetV1D、MobileNetv2、ShuffleNetv1/v2、HRNet、SCNet、Hourglass、HigherHRNet、CPM | 骨干网络实现 | v0.5.0 → v0.7.0 | modelzoo 骨干扩展的下游依赖 |
| AlphaPose、HRNet | 同类开源代码库 | v0.5.0 | 性能对标对象 |
| mmcv、mmdetection | 同体系上游库 | v0.7.0、v0.8.0 | 「Reuse mmcv utility function」（PR #135、#137）、「Support different return formats of mmdetection models」（PR #217）体现 mmpose 对 OpenMMLab 生态的复用 |

此外，PR 编号贯穿全文，可通过 GitHub PR 链接追溯每个特性对应的具体代码变更，形成文档→代码→测试的完整追溯链。

---

## 【使用方法】

原文未涉及具体启用方式/配置项/启动命令（changelog 性质所致）。以下为**原文声明中可直接观察到的能力开关**：

- **数据集启用**：通过 PR 号对应的 config 文件接入（如 CrowdPose #195、PoseTrack18 #220、MPII #55 等）。
- **backbone 选用**：v0.6.0 起在 configs 中可选 ResNext / SEResNet / ResNetV1D / MobileNetv2 / ShuffleNetv1 / CPM；v0.7.0 增加 ShuffleNetv2（PR #139）。
- **CPU 训练/验证/demo**：v0.6.0 起支持（PR #34）。
- **Dockerfile 使用**：v0.6.0 提供（PR #44），具体构建命令原文未给出。
- **best model 保存**：v0.7.0 起基于关键指标自动保存（PR #127），具体监控指标原文未列。
- **bottom-up 推理**：v0.6.0 起支持（PR #69），对应 bottom-up demo（PR #69）。
- **返回 heatmaps 与 backbone features**：v0.8.0 起可通过配置开启（PR #196、#212）。
- **mmdetection 返回格式兼容**：v0.8.0 起支持（PR #217）。

具体命令行、配置文件字段、参数取值原文未涉及，需查阅各 PR 或后续版本用户文档。
