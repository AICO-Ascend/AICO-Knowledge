# changelog

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/semantic_segmentation/DeeplabV3_for_Pytorch/docs/changelog.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/semantic_segmentation/DeeplabV3_for_Pytorch/docs/changelog.md

# 一体化深度解读：mmsegmentation Changelog（V0.9 → V0.15）

## 【定位】

本文档记录了开源语义分割框架 **mmsegmentation** 自 V0.9（2020/11/30）至 V0.15（2021/07/04）共七个版本的迭代变更，以"亮点（Highlights）+ Bug 修复 + 新特性 + 改进"四维结构逐版本罗列每次发布的编号化 PR（注：文档虽位于 `DeeplabV3_for_Pytorch/docs/` 路径下，但实际内容为 mmsegmentation 项目官方 changelog）。

---

## 【技术要点】

| 版本 | 日期 | 核心新增能力 |
|------|------|--------------|
| V0.15 | 2021/07/04 | 支持 ViT / SETR / Swin-Transformer；新增中文文档；统一参数初始化；DeiT 权重加载；FastSCNN 精度提升 |
| V0.14 | 2021/06/02 | ONNX→TensorRT 转换；MIM（OpenMMLab 模型管理工具）支持 |
| V0.13 | 2021/05/05 | Pascal Context 59 类数据集；Visual Transformer Backbone；mFscore 指标；torchscript 导出；ONNX 动态导出 |
| V0.12 | 2021/04/03 | FCN-Dilated6；Dice Loss；mIoU 加速；plot logs 工具 |
| V0.11 | 2021/02/02 | memory efficient test；更多 UNet 基准；Lovasz Loss |
| V0.10 | 2021/01/01 | MobileNetV3；DMNet；APCNet；ResNet18V1b/V1c、ResNet50V1b |
| V0.9 | 2020/11/30 | 4 类医学数据集；UNet；CGNet；RandomRotate / RGB2Gray / Rerange 变换 |

---

## 【关键机制与数据】

以下机制均直接来源于原文 PR 描述，未做引申：

- **统一参数初始化**（V0.15，#567）：原文仅给出"Unified parameter initialization"这一描述，未披露具体初始化分布/方差等数值。
- **ONNX→TensorRT**（V0.14，#542、#547）：原文仅描述"Support ONNX to TensorRT"，未给出延迟/吞吐等基准数字。
- **Memory efficient test**（V0.11，#330）：原文仅描述"Support memory efficient test"，未给出显存节省比例。
- **Persistent dataloader worker**（V0.15，#646）：提升 DataLoader 效率，原文未给出具体加速比。
- **数据集与指标扩展**：
  - Pascal Context **Class-59**（V0.13，#459）—— 原文明确写为 "Pascal Context Class-59 dataset"，注意区分于后续 #488 修复的 "Pascal Context 60-class"。
  - mFscore 指标（V0.13，#509）。
- **数据流改动**（V0.13，#514）：原文 "Replace data_dict calling 'img' key to support MMDet3D"——将数据字典中的 `'img'` 键重构以兼容 MMDet3D。
- **Meta 文件字段更新**（V0.15，#661、#664）：原文未列举字段名变化。

> 原文为纯变更日志，不含训练曲线、mIoU 数值、推理时延等性能数据，故无量化对比可解读。

---

## 【表格解读】

**原文无表格**（仅含条目式列表，已在【技术要点】中以 markdown 表格形式结构化呈现）。

---

## 【公式解读】

**原文无公式**。

---

## 【关联】

文档内部无交叉链接（文末"内部链接: (无)"）。从内容主题可梳理以下模块关联（均依据原文 PR 编号）：

- **Backbone 系列**：ViT (#520/#635)、SETR (#531/#635)、Swin-Transformer (#511)、MobileNetV3 (#268)、ResNet18V1b/V1c、ResNet50V1b (#316)、DeiT (#538)。
- **Head/Neck**：UperHead (#520)、UpSample Neck (#512)、FCN-Dilated6。
- **Loss**：Dice Loss (#396/#417)、Lovasz Loss (#351)，并支持从文件读取 `class_weight` (#513)。
- **数据变换**：RandomRotate (#215/#260)、RGB2Gray (#227)、Rerange (#228)、PhotoMetricDistortion (#388)。
- **部署链路**：pytorch2onnx 动态导出 (#463)、torchscript 导出 (#469/#499)、ONNX 测试工具 (#498)、ONNX→TensorRT (#542)。
- **上下游生态**：MIM (#549)、MMCV MODEL_REGISTRY (#515)、MMCV EvalHook (#438)、MMOCR / MMGeneration 链接 (#501/#506)、MMDet3D 兼容 (#514)。
- **指标**：mIoU 加速 (#430)、mFscore (#509)、class-level metrics 入日志 (#445)。
- **CI/DevOps**：CUDA 与 CPU 分离 CI (#602)、MMSeg 与 MMCV 兼容表 (#558)、Dockerfile 修复 (#607)。

---

## 【使用方法】

原文未涉及。changelog 仅记录版本变更，不含启用方式、配置项或命令行示例。具体的配置文件路径（如 `configs/`）、训练命令等需查阅仓库内其他文档。
