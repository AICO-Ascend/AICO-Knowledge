# changelog

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/cv/detection/YoloV3_ID1790_for_PyTorch/docs/changelog.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/cv/detection/YoloV3_ID1790_for_PyTorch/docs/changelog.md

# YoloV3_ID1790_for_PyTorch 仓库存档文档深度解读

---

## 【定位】

该文档是 **mmdetection 框架的版本变更日志 (Changelog)**，记录了从 v2.4.0 (2020/9/5) 至 v2.7.0 (2020/11/30) 共四个版本的**新特性、破坏性变更、Bug 修复与改进**，覆盖了 YOLOv3 集成版本所在框架的演进过程，用于帮助使用者追踪 API/行为变更以适配不同版本的训练与部署。

---

## 【技术要点】

1. **YOLOv3 集成于 v2.4.0（2020/9/5）**：作为该框架在 v2.4.0 引入的新方法之一被显式列入"Highlights"，对应论文 https://arxiv.org/abs/1804.02767。这是本文档与本仓库路径直接相关的核心条目。
2. **破坏性变更 —— 前景/背景标签索引统一（v2.5.0，#3221）**：`[0, N-1]` 表示前景类，`N` 表示背景类；RPN 与其他 head 的背景标签行为由原本不一致（RPN 用 0、其他用 N）改为统一，对带 RPN head 的两阶段检测器中 softmax 类别顺序有影响，但**对 v2.x model zoo 中的预训练模型无影响**。
3. **FP16 相关方法从 mmdet 迁移至 mmcv（v2.5.0，#3766, #3822）**：`mmdet.core.fp16` 中的 `force_fp32`、`auto_fp16`、`wrap_fp16_model`、`Fp16OptimizerHook` 被移动到 `mmcv.runner`；旧路径会触发 deprecation warning，最终将在 **V2.8.0** 被移除。
4. **批量推理（Batch Inference）支持（v2.4.0，#3564, #3686, #3705）**：自 v2.4.0 起可在单 GPU 上对**多张图像**进行模型推理，影响所有 test API；通过 `replace_ImageToTensor`（#3686）在 dataset 初始化时转换旧版 test data pipeline 以辅助迁移。
5. **数据集过滤行为重构（v2.5.0，#3695）**：`get_subset_by_classes` 仅在 `test_mode=True` 且 `self.filter_empty_gt=True` 时被调用；`filter_empty_gt=False` 时无论是否指定 classes 都使用全部标注图像；用户需自行负责测试集的数据过滤与清洗。
6. **COCO/LVIS 数据集后端替换（v2.4.0，#3727）**：从原生 `pycocotools` 与 `lvis` 包迁移到 `mmlvis` 与 `mmpycocotools`，API 完全兼容；用户需先卸载原包再安装新包。

> 附：在 v2.7.0 中也支持了 YOLO 系列（含 YOLOv3）的 **ONNX 导出**（#4087, #4083）。

---

## 【关键机制与数据】

- **v2.4.0 模型权重托管迁移**（原文）："Switch model zoo to download.openmmlab.com"——意味着 v2.4.0 之前与之后发布的模型权重 URL 域名发生变化。
- **PyPI 发布起点**（原文）："Start to publish `mmdet` package to PyPI since v2.3.0"——表明自 v2.3.0 起 `mmdet` 可通过 pip 直接安装。
- **随机翻转方向扩展**（v2.4.0，#3608）（原文）：自 v2.4.0 起支持 horizontal/vertical/diagonal 方向的 `RandomFlip`，作用于 bbox、mask、image 的增强及回投映射流程。
- **deprecation 时间表**（原文）：FP16 工具在 v2.5.0 起 deprecate，"will be finally removed in V2.8.0"。
- **类索引顺序变化**（原文）：两阶段检测器中带 softmax 的 RPN head，其类别顺序在 v2.5.0 后被改变。
- **数据增强新增项**（v2.5.0，原文）：`Shear`、`Rotate`、`Translate` 几何增强（#3656, #3619, #3687）以及 image-only 变换 `Constrast`、`Equalize`、`Color`、`Brightness`（#3643）。

> 注：原文为变更日志，未提供任何基准性能/精度数据；本文档不存在性能对比数字。

---

## 【表格解读】

**原文无表格。** 该 changelog 仅以项目符号列表组织内容，未包含任何参数表、性能对比表或配置项表。

---

## 【公式解读】

**原文无公式。** 该 changelog 不包含任何 LaTeX 或伪代码形式的数学公式。

---

## 【关联】

根据文档中提及的特性/模块与文末提供的内部链接，推断关联关系如下：

| 文档条目 | 关联到的内部文档章节 | 关联性质 |
|---|---|---|
| v2.4.0 新增方法 SABL、YOLOv3、PAA Assign；模型权重托管迁移到 download.openmmlab.com | `model_zoo.md#comparison-with-detectron2` | 性能/能力横向对照（mmdet vs Detectron2），受版本演进影响 |
| v2.5.0 FP16 工具迁移到 mmcv（背景训练超参如 fp16/optimizer 等） | `compatibility.md#training-hyperparameters` | 训练超参数兼容性，FP16 钩子位置变化直接影响训练配置 |
| v2.4.0 批量推理（影响 test pipeline 与下游）、v2.5.0 数据集 `get_subset_by_classes` 重构、v2.6.0 重构 pytorch2onnx 到 `mmdet.core.export` | `compatibility.md` | 通用兼容性说明，受 API 行为/位置变化影响 |
| v2.4.0 `mmlvis`/`mmpycocotools` 替换、随机翻转方向扩展 | `compatibility.md#training-hyperparameters` | 数据增强与数据集后端替换影响训练超参配置 |
| v2.6.0 ONNX API 重构（`generate_inputs_and_wrap_model`）、v2.7.0 ONNX 导出支持扩展 | `compatibility.md` | 模型导出/部署接口受 API 重构影响 |

---

## 【使用方法】

> 原文未直接给出启用方式/配置项/命令，但根据 changelog 描述可提取以下关键使用注意点（均为原文事实陈述，非臆造）：

- **检测 ONNX 导出是否可用**（v2.7.0，#4087, #4083）：YOLO、Mask R-CNN、Cascade R-CNN 自 v2.7.0 起支持导出至 ONNX；v2.6.0（#3857, #3912）已将 pytorch2onnx API 重构至 `mmdet.core.export` 并使用 `generate_inputs_and_wrap_model`。
- **迁移 FP16 训练代码**（v2.5.0）：将 `from mmdet.core.fp16 import ...` 改为 `from mmcv.runner import ...`；v2.8.0 前旧导入仍可用但会触发 deprecation warning。
- **迁移到批量推理**（v2.4.0，#3686）：使用 `replace_ImageToTensor` 在 dataset 初始化阶段转换旧 test pipeline 以适配新的 test API。
- **迁移数据集后端**（v2.4.0，#3727）：先卸载原 `pycocotools` 与 `lvis` 包，再安装 `mmlvis` 与 `mmpycocotools`。
- **安装 MMCV**（v2.5.0，#3840）：原文 Bug Fix 条目中建议使用 `https://download.openmmlab.com/mmcv/dist/index.html` 作为 MMCV 安装源。
- **GPU 安装问题排查**（v2.7.0，#4176）：原文 Improvements 中提到在 30 系列 GPU 上添加了安装问题解决方案（具体方案文档未给出完整命令）。
- **PyTorch 版本适配**：v2.5.0（#3905）支持 PyTorch 1.6（docker），v2.7.0（#4103）修复 PyTorch 1.7 兼容性问题。
- **训练时链接最佳 checkpoint**（v2.7.0，#3773）：自 v2.7.0 起可在训练中链接最佳 checkpoint。
- **推理时通过选项覆盖 config**（v2.7.0，#4175）：自 v2.7.0 起 `inference.py` 支持通过命令行选项覆盖 config。
