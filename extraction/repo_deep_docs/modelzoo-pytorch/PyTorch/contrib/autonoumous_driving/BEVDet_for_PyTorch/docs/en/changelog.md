# changelog

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/autonoumous_driving/BEVDet_for_PyTorch/docs/en/changelog.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/autonoumous_driving/BEVDet_for_PyTorch/docs/en/changelog.md

# 一体化深度解读：mmdetection3d Changelog

---

## 【定位】

这篇文档是 **mmdetection3d v1.0.0rc1 → v1.0.0rc4 四个候选发布版本（2022 年 1 月–8 月）的累积变更日志**，按版本倒序记录每个版本的 Highlights、新特性、改进、Bug 修复与贡献者清单，用于追踪 3D 目标检测/分割框架在此期间围绕**坐标系重构、算子迁移、Sparse Conv 后端、视图变换器、多模态数据加载、CI/CD 文档体系**的演进轨迹。

> 注：路径 `BEVDet_for_PyTorch/docs/en/changelog.md` 与 mmdetection3d 的官方 changelog 内容一致，属于同一份上游文档被复刻到 BEVDet 仓库内作为参考。

---

## 【技术要点】

1. **稀疏卷积后端双轨制**：rc2 引入 [spconv 2.0](https://github.com/traveller59/spconv)（CUDA 9.0 下仍可用 spconv 1.x 但显存更大，权重兼容），rc4 修复 spconv 2.0 的模型加载 bug（#1699）；rc3 中 PartA2 配置同时兼容 spconv 2.0（#1538）。
2. **视图变换器 (View Transformer) 多样化**：rc4 新增 lift-splat-shoot view transformer（#1598）与多相机 3D 目标检测的变换管道（#1580），覆盖 BEV 视角的多视图融合路径。
3. **无 anchor / 单阶段 3D 检测器扩容**：rc4 支持 [FCAF3D](https://arxiv.org/pdf/2112.00322.pdf)（#1547）；rc3 支持 [SA-SSD](https://openaccess.thecvf.com/content_CVPR_2020/papers/He_Structure_Aware_Single-Stage_3D_Object_Detection_From_Point_Cloud_CVPR_2020_paper.pdf)（#1337）。
4. **IoU / NMS 算子下沉到 BEV 统一接口**：rc2 用一组鸟瞰图（BEV）旋转框算子替换 `mmcv.iou3d`（#1403, #1418），统一旋转框操作；rc3 修复 `box3d_nms` 中因 #1403 引入的 `order` 选择缺失（#1479）。
5. **坐标系重构带来的兼容性矩阵**：rc1 对 18 个检测/分割模型逐项标注 checkpoint 更新状态（Fully Updated / Partially Updated / In Progress / No Influence），其中 PointPillars / SECOND / 3SSD 为"部分更新"，CenterPoint 为"进行中"。
6. **数据加载与基础设施**：rc1 加入 ScanNet 实例分割数据集（含指标，#1230）、Ceph 远程标注加载（#1325）、并行 Waymo 数据转换（#1327）、自动从最新 checkpoint 恢复训练（#1329）、Windows CI（#1345）；rc3 支持 S3DIS 完整 ceph 训练（#1542）。

---

## 【关键机制与数据】

- **坐标系重构（rc1）**：原文 "To fix the imprecise timestamp and optimize its saving method, we reformat the point cloud data during Waymo data conversion." 并行处理显著缩短数据转换时间；若使用旧 KITTI 格式 Waymo 数据需要**重新生成**。详见 [compatibility.md](https://github.com/open-mmlab/mmdetection3d/blob/master/docs/en/compatibility.md)。
- **mmcv 算子迁移（rc1, #1240/#1286/#1290/#1333）**：原文 "We migrate all the mmdet3d ops to mmcv and do not need to compile them when installing mmdet3d." 安装 mmdet3d 时不再需要编译算子。
- **Registry 作用域区分（rc2, #1412/#1443 + rc3 #1466/#1536）**：用于解决 pipeline 组合与 CocoDataset 中潜在的注册表冲突（原文："Fix the potential problems caused by the registry scope update when composing pipelines"）。
- **文档渲染管线切换（rc2 #1414 → rc3 #1488/#1489）**：从 `recommonmark` 切换到 `myst_parser`，并用 `mdformat` 替代 `markdownlint`（避免安装 Ruby），`myst-parser` 解析 anchor tag。
- **贡献者规模**：rc1—rc4 分别为 (原文截断)、11、13、7 名开发者（rc4 标题写 "7" 但列出 9 个 handle，可能含合并/历史账号）。
- **PR 编号范围**：从 #1230（ScanNet 实例分割，rc1）跨越到 #1699（spconv2.0 模型加载 bug，rc4），覆盖约 470 个 PR 的演进。

> 性能数字、吞吐量、精度 mAP 等具体数值在 changelog 原文均**未给出**，故不臆造。

---

## 【表格解读】

原文 v1.0.0rc1 的 Compatibility 段落中包含一张模型 checkpoint 更新状态表，逐字还原如下：

|               | Fully Updated | Partially Updated | In Progress | No Influcence |
| ------------- | :-----------: | :---------------: | :---------: | :-----------: |
| SECOND        |               |         ✓         |             |               |
| PointPillars  |               |         ✓         |             |               |
| FreeAnchor    |       ✓       |                   |             |               |
| VoteNet       |       ✓       |                   |             |               |
| H3DNet        |       ✓       |                   |             |               |
| 3DSSD         |               |         ✓         |             |               |
| Part-A2       |       ✓       |                   |             |               |
| MVXNet        |       ✓       |                   |             |               |
| CenterPoint   |               |                   |      ✓      |               |
| SSN           |       ✓       |                   |             |               |
| ImVoteNet     |       ✓       |                   |             |               |
| FCOS3D        |               |                   |             |       ✓       |
| PointNet++    |               |                   |             |       ✓       |
| Group-Free-3D |               |                   |             |       ✓       |
| ImVoxelNet    |       ✓       |                   |             |               |
| PAConv        |               |                   |             |       ✓       |
| DGCNN         |               |                   |             |       ✓       |
| SMOKE         |               |                   |             |       ✓       |
| PGD           |               |                   |             |       ✓       |
| MonoFlex      |               |                   |             |       ✓       |

**逐行解读**：
- **表头四列**：Fully Updated（已完全更新）、Partially Updated（部分更新）、In Progress（处理中）、No Influence（不受影响，原文拼写为 "Influcence"）。
- **"Partially Updated"（3 个）**：SECOND、PointPillars、3DSSD — LiDAR 单/双阶段点云检测器，因坐标系重构仅完成部分 checkpoint 重训。
- **"In Progress"（1 个）**：CenterPoint — 是 rc3 中更新 pretrained models 的对象（#1450），rc1 时尚在进行。
- **"Fully Updated"（7 个）**：FreeAnchor、VoteNet、H3DNet、Part-A2、MVXNet、SSN、ImVoxelNet — 全部已发新权重。
- **"No Influence"（9 个）**：FCOS3D、PointNet++、Group-Free-3D、PAConv、DGCNN、SMOKE、PGD、MonoFlex 等 — 多为单目/纯点云 backbone/分割类模型，坐标系重构未影响其权重。

**结构性结论**：3 个 "Partially Updated" + 1 个 "In Progress" + 9 个 "No Influence" + 7 个 "Fully Updated" = 20 行（核对正确）。原文明确提示 "Please stay tuned for the release of the remaining model checkpoints"，即后续 checkpoint 需关注 SECOND/PointPillars/3DSSD/CenterPoint 这 4 个。

---

## 【公式解读】

**原文无公式。** 本篇 changelog 全部由 Highlights / New Features / Improvements / Bug Fixes / Contributors 五类文字条目与一张兼容性表格组成，不含任何 LaTeX 公式或伪代码表达式。

---

## 【关联】

由于本文档是 changelog，**关联关系**主要体现在各条目的 PR 编号串接与跨版本呼应：

- **算子迁移链**：rc1 的"migrate all mmdet3d ops to mmcv"（#1240/#1286/#1290/#1333）→ rc2 的"Update Registry to distinguish scope of building functions"（#1412/#1443）→ rc3 的"Fix incorrect registry name when building RoI extractors"（#1460）、"Fix potential problems caused by the registry scope update"（#1466, #1536），是一组**强耦合的演进序列**。
- **坐标系重构链**：rc1 列出兼容性矩阵 + "incorrect yaw" bug 修复（rc2 #1407）→ rc3 "Update CenterPoint pretrained models that are compatible with refactored coordinate systems"（#1450）。
- **spconv 后端链**：rc2 引入 spconv 2.0（#1421）→ rc3 更新 PartA2 配置兼容 spconv 2.0（#1538）→ rc4 修复 spconv2.0 model loading bug（#1699）。
- **数据后端链**：rc1 Ceph 标注加载（#1325）→ rc3 S3DIS full ceph training（#1542）。
- **文档工具链**：rc2 recommonmark → myst_parser（#1414）→ rc3 myst_parser 解析 anchor tag（#1488）+ mdformat 替代 markdownlint（#1489）。
- **上下游模块引用**：`box3d_nms`、`browse_dataset.py`、`BasePoints`、`NaiveSyncBatchNorm1d/2d`、`DepthInstance3DBoxes.overlaps`、`Custom3DDataset`、`getting_started.md`、`README.md`、`compatibility.md` 等模块/文档被多次交叉引用，提示这是一份与**整个 mmdetection3d 1.0 主干重构**同步推进的版本记录。

> 文档内部链接字段标注为 (无)，因此本节关联全部基于正文 PR 编号与模块名推导。

---

## 【使用方法】

本文档为 changelog，本身**不提供安装/训练/推理命令**。若需启用文中提到的任一特性，按原文提示的入口如下：

1. **新检测器启用**：FCAF3D（rc4, #1547）、SA-SSD（rc3, #1337）、MinkowskiEngine + MinkResNet（rc2, #1422）—— 需在 `configs/` 下选择对应配置文件，按 mmdetection3d 标准训练流程使用 `tools/train.py` 启动。
2. **稀疏卷积后端切换**：rc2（#1421）原文："Users can still use spconv 1.x in MMCV with CUDA 9.0 (only cost more memory) without losing the compatibility of model weights between two versions." 即安装 `spconv` 2.0 包后即可自动启用，无需改代码。
3. **多相机 3D 检测 / lift-splat-shoot view transformer**：rc4 #1580、#1598，原文未给出具体 CLI，需配合 BEVDet 等多相机 pipeline 配置使用。
4. **Waymo 数据并行转换**：rc1 #1327，原文："support parallel processing … the data conversion time is also optimized significantly." 需使用配套转换脚本。
5. **Ceph 标注加载**：rc1 #1325、rc3 #1542（S3DIS ceph 训练），原文未给出 Ceph endpoint 配置语法，需参考 mmdetection3d 通用 Ceph 接入文档。
6. **从最新 checkpoint 自动恢复**：rc1 #1329，原文："Support resuming from the latest checkpoint automatically"，启动训练脚本即可生效。
7. **Windows CI / Circle CI**：rc1 #1345 + rc4 #1647，仅影响仓库维护者的持续集成配置，普通用户无需操作。

> 除上述条目外，**具体命令行参数、配置项 key、依赖版本号**原文均未给出，请参见上游 mmdetection3d 对应 PR/配置文件获取细节。
