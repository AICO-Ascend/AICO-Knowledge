# Changelog

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/cv/pose_estimation/HRNet_MMPose_for_PyTorch/docs/en/changelog.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/cv/pose_estimation/HRNet_MMPose_for_PyTorch/docs/en/changelog.md

# modelzoo-pytorch · HRNet_MMPose · docs/en/changelog.md 深度解读

---

## 【定位】

本文档是 mmpose 项目（被 modelzoo-pytorch 仓库以 `HRNet_MMPose_for_PyTorch` 目录形式纳管）在 **v0.26.0 → v0.29.0** 四个版本窗口（2022-05-05 至 2022-10-14）内的 **changelog**，用于记录 MMPose 在该时间段引入的新算法/主干、改进项、Bug 修复及配套 demo/API 能力，起到"特性索引 + 兼容性变更清单"的作用。

---

## 【技术要点】

1. **新算法/主干持续扩充**（五个版本段共引入 5 类骨干/算法）：RLE（Residual Log-likelihood Estimation, ICCV'2021）、Swin Transformer（ICCV'2021）、PVT / PVTv2（ICCV'2021 / CVMJ'2022）、TCFormer（CVPR'2022）、DEKR（CVPR'2021）、CID（CVPR'2022）。
2. **手势识别能力首次落地（v0.27.0）**：新增 MTUT 论文算法（CVPR'2019）+ NVGesture 数据集（CVPR'2016）链路，配 I3D backbone 配置；通过 [`/demo/docs/gesture_recognition_demo.md`](demo/docs/gesture_recognition_demo.md) 提供 demo 入口。
3. **Webcam API 大改版（v0.27.0 起，v0.28.0 完善）**：v0.27.0 完成 API 主升级并补全中英文教程（[`/docs/en/tutorials/7_webcam_api.md`](docs/en/tutorials/7_webcam_api.md)、[`/docs/zh_cn/tutorials/7_webcam_api.md`](docs/zh_cn/tutorials/7_webcam_api.md)、[`/demo/docs/webcam_demo.md`](demo/docs/webcam_demo.md)）；v0.28.0 修复死锁（#1430）并新增"终端命令快速设置设备"（#1466）。
4. **3D 姿态估计 demo 能力升级（v0.29.0）**：支持视点（viewpoint）与身高（height）控制，并扩充输入格式（#1481、#1490）；同时改进 3D 视频姿态平滑（#1479）。
5. **训练侧优化器与依赖管理**：v0.28.0 引入 layer decay 优化器构造器与 LR decay 优化器构造器（#1423），v0.29.0 改进依赖管理以"更顺滑的安装"（#1491）。
6. **多类 Bug 修复覆盖关键算子/数据**：包括 `fliplr_joints` 对浮点可见性 keypoint 的报错（#1589）、`hsigmoid` 默认参数（#1575）、UDP 解码（#1565）、RLE 配置中缺失的数据变换（#1632）、Webcam 死锁（#1430）等。

---

## 【关键机制与数据】

> 说明：原文是一份 changelog，不含性能数值/数据流图；以下机制描述均**严格来自原文条目**，未做推测。

- **RLE 路线推进路径**：v0.26.0 首次引入 [RLE](https://arxiv.org/abs/2107.11291) 算法（#1259，ICCV'2021）→ v0.28.0 在 COCO 数据集上新增 RLE 模型（#1424）→ v0.29.0 修复 RLE 配置中缺失的数据变换问题（#1632）。
- **Swin / TCFormer / PVT 主干并存**：v0.26.0 加入 Swin（#1300）、PVT / PVTv2（#1343）；v0.28.0 加入 TCFormer（#1447、#1452）并对 Swin 模型做性能更新（#1467，PR 链接内显示为 #1434）。
- **DEKR / CID（v0.29.0 新增）**：DEKR（CVPR'2021）对应论文 [2104.02300](https://arxiv.org/abs/2104.02300)（#1693）；CID（CVPR'2022）（#1604）由 `kennethwdk` 等贡献。
- **手势识别（v0.27.0）**：算法 MTUT（CVPR'2019）+ 数据集 NVGesture（CVPR'2016），由 #1380（@Ben-Louis）合入，配套实验配置 [`/configs/hand/gesture_sview_rgbd_vid/mtut/nvgesture/i3d_nvgesture.md`](configs/hand/gesture_sview_rgbd_vid/mtut/nvgesture/i3d_nvgesture.md) 采用 I3D backbone。
- **mmcv 兼容性（v0.28.1）**：该小版本目的是修复与最新 mmcv v1.6.1 的兼容性。
- **推理加速（v0.26.0）**：通过优化预处理流水线加速推理并降低 CPU 占用（#1320），相关性能汇总另见 [`/docs/en/inference_speed_summary.md`](docs/en/inference_speed_summary.md)。
- **构建/文档工具链**：v0.27.0 将 CI 中的 markdownlint 替换为 mdformat（#1382）以去除 ruby 依赖；v0.27.0 修复文档编译的 myst 设置（#1381）。

---

## 【表格解读】

**原文无表格**。该 changelog 由 `## 版本号 (日期)` + `**Highlights / New Features / Improvements / Bug Fixes**` 三段式列表组成，每条目形式为「功能简述 + PR 编号 + 贡献者 @mention」，未出现任何 markdown 表格/参数表/性能对比表。

---

## 【公式解读】

**原文无公式**。changelog 不涉及数学公式或伪代码。

---

## 【关联】

| 类别 | 关联对象 | 在文档中的角色 |
|---|---|---|
| Demo 入口 | [`/demo/docs/gesture_recognition_demo.md`](demo/docs/gesture_recognition_demo.md) | v0.27.0 手势识别功能的用户入口 |
| 算法说明 | [`/docs/en/papers/algorithms/mtut.md`](docs/en/papers/algorithms/mtut.md) | MTUT 算法（CVPR'2019）的论文导读 |
| 数据集说明 | [`/docs/en/papers/datasets/nvgesture.md`](docs/en/papers/datasets/nvgesture.md) | NVGesture 数据集（CVPR'2016）的论文导读 |
| 实验结果 | [`/configs/hand/gesture_sview_rgbd_vid/mtut/nvgesture/i3d_nvgesture.md`](configs/hand/gesture_sview_rgbd_vid/mtut/nvgesture/i3d_nvgesture.md) | I3D-NVGesture 实验结果/配置说明 |
| 教程 | [`/docs/en/tutorials/7_webcam_api.md`](docs/en/tutorials/7_webcam_api.md) 、[`/docs/zh_cn/tutorials/7_webcam_api.md`](docs/zh_cn/tutorials/7_webcam_api.md) | Webcam API 中英文教程（v0.27.0/0.28.0） |
| Demo | [`/demo/docs/webcam_demo.md`](demo/docs/webcam_demo.md) | Webcam demo 文档 |
| 上游贡献 | [@PINTO0309](https://github.com/open-mmlab/mmpose/pull/1242) | 通过 #1242 关联的 PR 贡献者（任务内部链接中给出） |
| 性能数据 | [`/docs/en/inference_speed_summary.md`](docs/en/inference_speed_summary.md) | 推理速度基准说明（与 v0.26.0 #1320 预处理优化呼应） |

模块间**上下游关系**：

```
v0.26.0 预处理加速 (#1320) ──► inference_speed_summary.md
v0.27.0 MTUT + NVGesture  (#1380) ──► gesture_recognition_demo.md
                                       ├─► papers/algorithms/mtut.md
                                       ├─► papers/datasets/nvgesture.md
                                       └─► configs/.../i3d_nvgesture.md
v0.27.0 Webcam API 主升级 (#1393/#1404/#1413) ──► 7_webcam_api.md (EN/zh_CN)
                                                  └─► webcam_demo.md
v0.28.0 RLE on COCO (#1424) ──► v0.29.0 RLE config 修复 (#1632)
v0.26.0 Swin (#1300) ──► v0.28.0 Swin 性能更新 (#1467)
v0.28.1 mmcv v1.6.1 兼容 ──► v0.29.0 依赖管理改进 (#1491)
```

---

## 【使用方法】

> 原文为 changelog，仅以条目形式罗列变更，**未给出任何启用命令/配置项/环境变量**。其"使用方法"需结合下文链接文档共同完成：

- **启用 Webcam API**：参考 [`/docs/en/tutorials/7_webcam_api.md`](docs/en/tutorials/7_webcam_api.md) 或 [`/docs/zh_cn/tutorials/7_webcam_api.md`](docs/zh_cn/tutorials/7_webcam_api.md)，配套 demo 见 [`/demo/docs/webcam_demo.md`](demo/docs/webcam_demo.md)。v0.28.0 起支持"在终端命令中快速设置设备"（#1466）。
- **体验手势识别 demo**：参考 [`/demo/docs/gesture_recognition_demo.md`](demo/docs/gesture_recognition_demo.md)；算法/数据集/实验结果分别对应 [`/docs/en/papers/algorithms/mtut.md`](docs/en/papers/algorithms/mtut.md)、[`/docs/en/papers/datasets/nvgesture.md`](docs/en/papers/datasets/nvgesture.md)、[`/configs/hand/gesture_sview_rgbd_vid/mtut/nvgesture/i3d_nvgesture.md`](configs/hand/gesture_sview_rgbd_vid/mtut/nvgesture/i3d_nvgesture.md)。
- **安装方式变更（v0.28.0）**：支持通过 [mim](https://github.com/open-mmlab/mim) 安装（#1425）。
- **3D 姿态估计 demo**：v0.29.0 起支持视点/身高控制与更多输入格式（#1481、#1490）；3D 视频姿态使用更平滑的滤波（#1479）。
- **训练优化器（v0.28.0）**：支持 layer decay 优化器构造器与 LR decay 优化器构造器（#1423）；自定义 hook 配置项已从 `custom_hooks_config` 重命名为 `custom_hooks`（#1427）。
- **推理性能数据**：参见 [`/docs/en/inference_speed_summary.md`](docs/en/inference_speed_summary.md)。
- **升级提示**：v0.28.1 为兼容性修复版，与 mmcv v1.6.1 配套；从更早版本升级需关注 RLE 配置补全数据变换（#1632）、`custom_hooks` 字段重命名（#1427）等破坏性变更。

---

> 备注：原文在 v0.26.0 的 **New Features** 段被截断（结尾为 "Support [RLE (Residual Log-likelihood Estimation)](https://arxiv.org/abs/2107.11291), "），本解读基于该文档实际可见内容完成，未补全缺失条目，也未引入文档未提供的数字或机制。
