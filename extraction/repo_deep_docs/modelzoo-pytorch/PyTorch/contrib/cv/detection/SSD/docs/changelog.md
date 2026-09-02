# changelog

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/SSD/docs/changelog.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/SSD/docs/changelog.md

# modelzoo-pytorch / SSD / docs / changelog.md 解读

> ⚠️ **路径说明**: 虽然路径位于 `PyTorch/contrib/cv/detection/SSD/docs/changelog.md`, 但正文实际是 **mmdetection (v2.3.0 – v2.6.0)** 的版本日志,**而非 SSD 专用日志**。下文按原文如实解读。

---

## 【定位】
本篇是 **mmdetection 目标检测工具箱** 自 v2.3.0 至 v2.6.0 的版本变更日志 (changelog), 系统记录新方法支持 (YOLACT / CentripetalNet / VarifocalNet / SABL / YOLOv3 / PAA / CornerNet 等)、破坏性变更、bug 修复、性能/文档改进, 用于向下游开发者同步版本演进与迁移指南。

---

## 【技术要点】

1. **新方法持续接入**: 四个版本先后支持 VarifocalNet (#3666, #4024)、YOLACT (#3456)、CentripetalNet (#3390)、SABL (#3603)、YOLOv3 (#3083)、PAA assign (#3547)、CornerNet, 表明项目以"算法库"形态快速吸纳 SOTA 检测器。
2. **破坏性变更 — FP16 迁移至 mmcv** (v2.5.0, #3766/#3822): `mmdet.core.fp16` 中的 `force_fp32 / auto_fp16 / wrap_fp16_model / Fp16OptimizerHook` 全部移至 `mmcv.runner`, 并预告 **v2.8.0 彻底移除** mmdet 内的导入路径。
3. **破坏性变更 — 类别索引统一** (v2.5.0, #3221): **RPN 的背景标签由 0 改为 N**, 与其它 head 保持一致; 删除 `dense_heads` 中的 `self.background_labels`, 改用 `self.num_classes` 表示背景索引——会影响 RPN 使用 softmax 的两阶段检测器类别顺序,但 **不影响 v2.x 预训练模型**。
4. **破坏性变更 — 批量推理** (v2.4.0, #3564/#3686/#3705): 单张/多张推理统一, 通过 `replace_ImageToTensor` 在数据集初始化时转换 legacy test pipeline, 影响所有 test API 与下游代码库。
5. **破坏性变更 — dataset 子集过滤策略** (v2.5.0, #3695): `get_subset_by_classes` 仅在 `test_mode=True && filter_empty_gt=True` 时触发; 由用户负责测试集的数据清洗。
6. **算子下移 mmcv** (v2.3.0): CUDA/C++ 算子迁入 `mmcv.ops`, 保留 `mmdet.ops` 作为 wrapper 以维持向后兼容;同时迁移到 `mmlvis / mmpycocotools` (#3727) 替代 `lvis / pycocotools`。
7. **GIoU / DIoU / CIoU loss**: v2.6.0 在 `BboxOverlaps2D` 中新增 GIoU 并以 `bbox_overlaps` 重写 `giou_loss` (#3936);v2.3.0 引入 DIoU/CIoU loss。
8. **新增强策略 (v2.5.0–v2.4.0)**: `Shear / Rotate / Translate` 几何增强;`Constrast / Equalize / Color / Brightness` 图像增强;`Cutout` (#3521);`RandomFlip` 支持 **horizontal / vertical / diagonal** (#3608);CPU 模式随机采样 (#3948)。
9. **ONNX 导出重构** (v2.6.0, #3857/#3912): `pytorch2onnx` API 重构至 `mmdet.core.export`, 使用 `generate_inputs_and_wrap_model` 包裹模型。
10. **稳定性修复**: 修复 `num_pos=0` 时的除零 (PAA head #3938、Focal Loss #3702)、Mask R-CNN 无 positive roi 卡死 (#3713)、分布式训练 FPN 未分配 bbox 报错 (#3670) 等多类边界 case。

---

## 【关键机制与数据】

- **发布日期 (原文)**: v2.6.0 → **1/11/2020**; v2.5.0 → **5/10/2020**; v2.4.0 → **5/9/2020**; v2.3.0 → **5/8/2020**。
- **里程碑概览 (原文)**:
  - v2.6.0 支持 VarifocalNet + 文档重构
  - v2.5.0 新增 YOLACT、CentripetalNet + 大量文档
  - v2.4.0 新增 SABL / YOLOv3 / PAA assign + Batch Inference + 自 v2.3.0 起发布 `mmdet` 到 PyPI + 模型仓库切换到 `download.openmmlab.com`
  - v2.3.0 CUDA/C++ 算子下沉 mmcv + 新增 CornerNet / DIoU / CIoU loss / LVIS V1 + 文档/colab 教程完善
- **背景标签机制 (v2.5.0 行为, 原文)**: "`[0, N-1]` represents foreground classes and N indicates background classes for all models" — 旧实现中 RPN 的 background=0、其他 head 的 background=N, 新版本统一为 N;`self.background_labels` 被删除。
- **MMCV URL (原文)**: `https://download.openmmlab.com/mmcv/dist/index.html` (#3840) 用于安装 MMCV。
- **PyTorch 支持**: v2.5.0 起支持 PyTorch 1.6 (docker #3905);v2.6.0 修复 PyTorch 1.6.0 的 NMS nonzero 问题 (#3867)。
- **CI/包发布**: v2.4.0 开始通过 github-action 发布到 PyPI (#3510);CI 配置加入 PyTorch 1.6 (#3532)。

> 性能/精度数字 (mAP/FPS) **未在原文中出现**, 故此处不臆造。

---

## 【表格解读】

**原文无表格。**

全文采用 markdown 列表 (按 New Features / Bug Fixes / Improvements / Backwards Incompatible Changes 分组) 与少量加粗说明, 无结构化表格数据可还原。

---

## 【公式解读】

**原文无公式。**

无 LaTeX 或伪代码形式的数学公式;仅有文字性规则描述 (如类别索引、过滤条件)。

---

## 【关联】

文末给出的内部链接指向:

| 链接锚点 | 指向文档 | 关联内容 (来自原文上下文) |
|---|---|---|
| `model_zoo.md#comparison-with-detectron2` | model_zoo.md | 与 Detectron2 的性能/能力对比 — v2.4.0 起模型仓库切换到 `download.openmmlab.com`,模型文件命名变更 (#3795),增加 ATSS ResNet-101 入口 (#3639)。 |
| `compatibility.md#training-hyperparameters` | compatibility.md | 训练超参兼容性 — v2.5.0 RPN background label 调整会影响所有 RPN head 训练,需查阅 compatibility 文档确认 batch size / 学习率/标签索引等是否需调整;v2.6.0 起 validation 支持 `batch_size > 1` (#3966)。 |
| `compatibility.md` | compatibility.md | 综合兼容性指南 — 同时承接 v2.4.0 的 Batch Inference (#3564/#3686/#3705) 与 RandomFlip 升级 (#3608),以及 v2.5.0 的 dataset filter (`filter_empty_gt` & `test_mode`) 语义变更。 |

**模块/上下游关联**:
- 依赖 **mmcv**: v2.5.0 起 FP16 utils、env 收集 (`mmcv.utils.collect_env` #3779)、算子 (`mmcv.ops`, 含 `Conv2d`, v2.3.0 起) 均从 mmcv 引入;MMCV 安装源已固定到 `download.openmmlab.com`。
- 依赖 **mmlvis / mmpycocotools** (v2.4.0, #3727) 替代 `lvis / pycocotools`。
- **RPN ↔ dense_heads ↔ base detector** 链路: 类别索引统一 (#3221) + `RPNTestMixin` 改用 `self.rpn_head.test_cfg` (#3808) + Cascade R-CNN 中 SABL 验证 bug 修复 (#3913/#3849)。
- **导出链路**: `pytorch2onnx → mmdet.core.export → generate_inputs_and_wrap_model` (#3857/#3912);onnx 默认 mean/std 修复 (#3491)。
- **下游测试链**: 修复 multi-node testing 临时目录错误 (#4034/#4017) 与 `--show-dir` 行为 (#4025)。

---

## 【使用方法】

> 以下命令/配置项均为**原文中明确出现**的内容,未出现的部分标 "原文未涉及"。

- **GPU/CPU 模式选择**: v2.5.0 起 CPU 模式随机采样 (#3948);v2.6.0 推理在 CPU 模式下使用 **MMCV 实现的 RoIAlign** (#3930)。
- **测试脚本选项**: `--show-dir` 选项修复 (#4025) 用于结果可视化输出。
- **ONNX 导出 API**: 调用 `mmdet.core.export.generate_inputs_and_wrap_model` 完成模型包装并导出 (#3857/#3912)。
- **FP16 迁移 (v2.5.0)**:
  - 老路径 `mmdet.core.fp16.force_fp32 / auto_fp16 / wrap_fp16_model / Fp16OptimizerHook` 将发出去弃警告, **v2.8.0** 完全移除。
  - 新路径统一从 `mmcv.runner` 导入。
- **Dataset 过滤 (v2.5.0)**:
  - `filter_empty_gt=False` → 使用全部标注图片。
  - `filter_empty_gt=True && test_mode=True` → 调用 `get_subset_by_classes` 过滤无 GT 图。
  - **测试集的清洗由用户负责**。
- **RandomFlip 方向 (v2.4.0)**: 支持 horizontal / vertical / diagonal,影响 bbox、mask、image 三类变换。
- **Batch Inference (v2.4.0)**: 数据集初始化阶段自动调用 `replace_ImageToTensor` 转换 legacy pipeline (#3686)。
- **mmcv 安装**: 使用 `https://download.openmmlab.com/mmcv/dist/index.html` (#3840)。
- **Docker / PyTorch**: v2.5.0 起 docker 支持 PyTorch 1.6 (#3905)。
- **训练监控**: v2.5.0 起可在训练中显示实验名 (#3764)。
- **env 收集**: 使用 `mmcv.utils.collect_env` (#3779) 替代重复代码。
- **MTP/PyPI 发布**: 自 v2.3.0 起通过 github-action 发布 `mmdet` 到 PyPI (#3510)。
- **eval 选项**: v2.4.0 起 evaluation hook 增加 `init_eval` (#3550) 与 `eval-option` flag (#3537)。
- **ClassBalancedDataset**: 新增 `include_bkg` 参数 (#3577)。

> 完整运行命令 (训练/测试脚本的逐行 CLI 用法) **原文未涉及**, 需参考 `compatibility.md` 或 `model_zoo.md`。
