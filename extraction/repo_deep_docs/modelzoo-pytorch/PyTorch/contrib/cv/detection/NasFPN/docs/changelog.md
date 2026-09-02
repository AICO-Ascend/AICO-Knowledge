# changelog

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/NasFPN/docs/changelog.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/NasFPN/docs/changelog.md

# 代码仓「modelzoo-pytorch」NasFPN/docs/changelog.md 深度解读

## 【定位】

本文档是 OpenMMLab **MMDetection v2.5.0 → v2.9.0** 的版本演进日志（changelog），用于逐版记录检测框架支持的新模型/新特性、Bug 修复、性能改进及不向后兼容的破坏性变更，是用户升级、迁移、选型时追溯变更来源的核心参考。

---

## 【技术要点】

1. **新检测模型/方法持续引入**：v2.5.0 引入 YOLACT、CentripetalNet；v2.6.0 引入 VarifocalNet (VarifocalNet: An IoU-aware Dense Object Detector, arXiv:2008.13367)；v2.7.0 引入 DETR (arXiv:2005.12872)、ResNeSt (arXiv:2004.08955)、Faster R-CNN DC5；v2.8.0 引入 Cascade RPN (arXiv:1909.06720)、TridentNet (arXiv:1901.01892)；v2.9.0 引入 SCNet (arXiv:2012.10150)、Sparse R-CNN (arXiv:2011.12450)。
2. **配置结构重构（v2.9.0）**：将 `train_cfg` 与 `test_cfg` 从配置顶层移入 model（PR #4347、#4489），是配置结构的破坏性变更。
3. **ONNX 导出能力扩展**：v2.7.0 起支持 YOLO、Mask R-CNN、Cascade R-CNN 模型导出 ONNX；v2.9.0 在 `pytorch2onnx.py` 中新增 `onnx_simplify` 选项（PR #4468）。
4. **类别/标签语义统一（v2.5.0 破坏性变更，PR #3221）**：所有模型统一采用 `[0, N-1]` 表示前景类、`N` 表示背景类；RPN 背景标签由 0 改为 N，并删除 `dense_heads.self.background_labels`，改用 `self.num_classes` 推断背景索引。
5. **FP16 接口迁移（v2.5.0 破坏性变更，PR #3766、#3822）**：`mmdet.core.fp16` 中 `force_fp32`、`auto_fp16`、`wrap_fp16_model`、`Fp16OptimizerHook` 移至 `mmcv.runner`，旧路径仅做废弃告警，**计划在 V2.10.0 完全移除**。
6. **可视化与评估增强**：v2.9.0 新增按预测质量可视化（PR #4441）、多 IoU 评估 mAP（PR #4398）、测试时拼接数据集（PR #4452）；`imshow_det_bboxes` 后端由 OpenCV 切换至 Matplotlib（PR #4389）。

---

## 【关键机制与数据】

- **数据集过滤语义重写（v2.5.0, PR #3695）**：`get_subset_by_classes` 仅在 `test_mode=True` 且 `self.filter_empty_gt=True` 时被调用。若 `filter_empty_gt=False`，无论初始化时是否指定 classes，都使用全部标注图像；若 `filter_empty_gt=True` 且 `test_mode=True`，无论是否指定 classes，都会调用 `get_subset_by_classes` 检查并过滤掉不含 GT 的图像。
- **Head/DataSet 类数兼容钩子（v2.9.0, PR #4508）**：新增 hook 用于检查 head 与数据集的类别数兼容性，避免类别数不匹配导致的静默错误。
- **训练优化**：v2.5.0 在 PAA 中避免 `num_pos=0` 时的除零（PR #3938）；v2.6.0 在 CPU 推理中使用 mmcv 实现的 RoIAlign（PR #3930）；v2.6.0 加速 PAA 训练速度（PR #3985）；v2.7.0 在 SSD 上支持混合精度训练搭配其他 backbone（PR #4081）；v2.9.0 发布 R50/R101 PAA 多尺度 3x 训练计划预训练权重（PR #4495）。
- **ONNX 导出 API 重构（v2.6.0, PR #3857、#3912）**：将 `pytorch2onnx` API 重构进 `mmdet.core.export`，统一通过 `generate_inputs_and_wrap_model` 生成包装模型。
- **Sparse R-CNN 支撑性重构（v2.8.0, PR #4259）**：重构 Hungarian Assigner，使其在 Sparse R-CNN 中更通用。
- **多节点/分布式容错（v2.8.0, PR #4257）**：修复数据集过小时分布式采样器异常。

> 原文未给出可量化的 mAP/FPS 数值或基准测试结果（除 `imshow_det_bboxes` 视觉后端切换、模型权重发布等定性描述外），故不杜撰具体性能数据。

---

## 【表格解读】

**原文无表格**。全文为分类列表式变更记录，未出现参数表、性能对比表或配置项表格。

---

## 【公式解读】

**原文无公式**。本文档为变更日志，不涉及任何数学表达式或伪代码公式。

---

## 【关联】

依据用户提供的内部链接信息，本文与下列模块/文档存在引用关系：

- **`model_zoo.md#comparison-with-detectron2`**：模型动物园文档中与 Detectron2 性能对比章节对应——版本中持续引入的新 backbone（如 ResNeSt）、新检测头（如 VarifocalNet、Sparse R-CNN、SCNet、Cascade RPN、TridentNet）以及预训练权重的更新（如 v2.9.0 发布的 R50/R101 PAA 多尺度 3x 权重、PR #4495；v2.8.0 更新的 COCO 子集训练的 faster_rcnn 预训练权重、PR #4307）均会反映到 model zoo 的对比表中。
- **`compatibility.md#training-hyperparameters`**：兼容性文档中的训练超参数章节对应——v2.5.0 的 `dense_heads.self.background_labels` 删除、`self.num_classes` 取代、RPN 背景标签从 0 改为 N（PR #3221）以及 FP16 接口从 `mmdet.core.fp16` 迁至 `mmcv.runner`（PR #3766、#3822）会直接影响训练超参数配置与依赖兼容矩阵。
- **`compatibility.md`**：通用兼容性文档——v2.9.0 的 `train_cfg/test_cfg` 移入 model（PR #4347、#4489）、v2.6.0 的 `pytorch2onnx` API 重构进 `mmdet.core.export`（PR #3857、#3912）、v2.8.0 移除废弃的 `mmdet.ops`（PR #4325）以及 v2.7.0 修复的 PyTorch 1.7 不兼容问题（PR #4103）均属于兼容性范畴。

与其他模块的上下游关系：
- **NasFPN 自身**：v2.9.0（PR #4264）记录了为 FPN 参数新增废弃警告文档，与 NasFPN 这类基于 FPN 的多尺度特征融合结构相关。
- **Backbone 升级**：v2.8.0 修复 `resnext` backbone 中 empirical attention bug（PR #4300）、更新 ATSS 以适配 PyTorch 1.6+（PR #4359）。
- **数据集扩展**：v2.9.0（PR #4382）支持 LVIS 数据集自定义类别，影响所有使用该数据集的下游模型。

---

## 【使用方法】

原文未直接给出启动/启用命令，但下列配置项与启用方式可从变更条目中提炼：

- **ONNX 简化选项（v2.9.0, PR #4468）**：在 `tools/pytorch2onnx.py` 中使用新增的 `onnx_simplify` 选项。
- **多 IoU 评估 mAP（v2.9.0, PR #4398）**：调用 eval 工具时启用多 IoU 评估。
- **预测质量可视化（v2.9.0, PR #4441）**：推理结果可视化时按 prediction quality 排序展示。
- **类数兼容性检查 hook（v2.9.0, PR #4508）**：注册相应 hook 以在 head 与数据集类别数不一致时抛出告警。
- **配置覆盖（v2.7.0, PR #4175）**：`inference.py` 支持通过命令行选项覆盖 config。
- **稀疏 R-CNN Hungarian Assigner（v2.8.0, PR #4259）**：Sparse R-CNN 配置文件使用重构后的 Hungarian Assigner。
- **混合精度训练 SSD（v2.7.0, PR #4081）**：SSD 检测器启用 mixed precision 时支持自定义 backbone。
- **批量推理（v2.9.0, PR #4408）**：参考文档中已废弃 `ImageToTensor` 的批量推理替代写法（PR #4400）。
- **ONNX 导出（v2.7.0, PR #4087、#4083）**：YOLO / Mask R-CNN / Cascade R-CNN 使用 `tools/pytorch2onnx.py` 导出（v2.6.0 重构后入口位于 `mmdet.core.export`，PR #3857、#3912）。
- **分布式训练 GPU 指定（v2.7.0, PR #4163）**：修复 `gpu_id` 在分布式模式下的配置错误，按修复后方式指定。

> 关于"`train_cfg/test_cfg` 移入 model"这一破坏性变更后的具体配置写法、"Faster R-CNN DC5" 训练启动命令等，原文未给出，需查阅 `compatibility.md` 与 `model_zoo.md` 中对应章节。
