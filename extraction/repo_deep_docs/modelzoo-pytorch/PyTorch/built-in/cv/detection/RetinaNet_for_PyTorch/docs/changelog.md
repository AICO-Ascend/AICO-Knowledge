# changelog

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/cv/detection/RetinaNet_for_PyTorch/docs/changelog.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/cv/detection/RetinaNet_for_PyTorch/docs/changelog.md

# 一体化深度解读:RetinaNet_for_PyTorch docs/changelog.md

## 【定位】

本篇文档是 MMDetection 框架 v2.5.0 至 v2.9.0 的版本变更日志,记录了该开源目标检测库在 2020-10 至 2021-01 期间的方法支持、特性新增、Bug 修复、API 重构与文档完善等所有变更条目,作为 RetinaNet_for_PyTorch 等下游模型仓所依赖的底层框架演进追踪依据。

---

## 【技术要点】

1. **新检测方法支持**:在 v2.5.0~v2.9.0 期间陆续引入 YOLACT、CentripetalNet、VarifocalNet、DETR、ResNeSt、Cascade RPN、TridentNet、SCNet、Sparse R-CNN 等新算法,每项均附 arXiv 论文链接与对应 PR 号。

2. **配置结构重构**:`train_cfg` 与 `test_cfg` 从独立文件移入模型配置内(#4347, #4489),便于集中管理训练/推理参数;同时在配置层支持通过命令行选项 override(#4175)。

3. **FP16 相关 API 迁移**:#3766、#3822 将 `mmdet.core.fp16` 中的 `force_fp32`、`auto_fp16`、`wrap_fp16_model`、`Fp16OptimizerHook` 迁移到 `mmcv.runner`,v2.5.0 起触发 deprecation 警告,并计划于 V2.10.0 彻底移除。

4. **类别标签统一**:#3221 规定 `[0, N-1]` 表示前景类、`N` 表示背景类,RPN 与其他 head 行为一致;移除 `dense_heads` 中的 `self.background_labels`,统一改用 `self.num_classes` 指示背景索引。

5. **ONNX 导出能力扩展**:v2.7.0 起 YOLO、Mask R-CNN、Cascade R-CNN 支持 ONNX 导出(#4087, #4083);v2.9.0 新增 ONNX simplify 选项(#4468);v2.6.0 重构 pytorch2onnx API 至 `mmdet.core.export`。

6. **可视化与评估增强**:支持按预测质量可视化(#4441)、多 IoU 计算 mAP(#4398)、测试时拼接数据集(#4452);`imshow_det_bboxes` 后端由 OpenCV 切换为 Matplotlib(#4389)。

---

## 【关键机制与数据】

**FP16 迁移机制**(原文 v2.5.0):
- 原位置:`mmdet.core.fp16`
- 新位置:`mmcv.runner`
- 涉及函数:`force_fp32`、`auto_fp16`、`wrap_fp16_model`、`Fp16OptimizerHook`
- 兼容策略:旧路径触发 deprecation warning,计划 V2.10.0 完全移除

**类别标签索引变更**(原文 v2.5.0):
- 旧:RPN 的背景标签为 0,其他 head 的背景标签为 N
- 新:RPN 与其他 head 一致——`[0, N-1]` 为前景,`N` 为背景
- 实现变化:`self.background_labels` 字段被移除,统一改用 `self.num_classes` 指示背景类索引
- 影响范围:所有 RPN head 训练;使用 softmax 的二阶段检测器 RPN 受类别顺序变化影响
- 预训练模型:v2.x model zoo 中的预训练权重不受影响

**可视化后端切换**(原文 v2.9.0):
- 原后端:OpenCV
- 新后端:Matplotlib
- PR:#4389

**NMS `score_factor` 顺序修复**(原文 v2.9.0):
- Bug 现象:YOLOv3 性能下降
- 修复 PR:#4473

**PAA 头部零除保护**(原文 v2.6.0):
- 触发条件:`num_pos=0` 时
- 修复 PR:#3938

---

## 【表格解读】

**原文无表格**

(文档为纯 changelog 列表结构,未出现参数表、性能对比表或配置项表格)

---

## 【公式解读】

**原文无公式**

(文档为版本变更说明,未包含任何 LaTeX 公式或伪代码公式)

---

## 【关联】

本文档作为版本变更记录,与以下内部模块/特性存在显式交叉引用关系:

- **`train_cfg`/`test_cfg` 内移**(#4347, #4489)与 `compatibility.md#training-hyperparameters` 直接相关——超参数配置入口从独立文件迁移至模型配置后,训练超参数(学习率、优化器、调度器等)需要在新的配置结构下查阅。

- **方法支持条目**与 `model_zoo.md#comparison-with-detectron2` 关联——changelog 中提及的 Cascade RPN、TridentNet、SCNet、Sparse R-CNN、DETR、VarifocalNet 等新方法,其与 Detectron2 的性能对比、模型下载链接在 model_zoo 中给出。

- **ONNX 导出**(YOLO/Mask R-CNN/Cascade R-CNN)与 `compatibility.md` 的兼容性矩阵相关——导出能力受 PyTorch 版本、MMCV 版本、算子支持情况约束。

- **`mmdet.core.fp16` → `mmcv.runner` 迁移**直接关联 `compatibility.md`——属于破坏性变更,需在兼容性文档中查找替代导入路径。

- **PAA 多尺度 3x 训练发布**(原文:Release pre-trained R50 and R101 PAA detectors with multi-scale 3x training schedules, #4495)与 model_zoo 性能指标相关。

---

## 【使用方法】

原文未涉及具体的启用命令或配置文件示例。

(作为 changelog 文档,仅记录变更内容,实际启用方式需结合 `model_zoo.md`、`compatibility.md` 与各模型的 config 文件查阅。文档末尾提供的三个内部链接 `model_zoo.md#comparison-with-detectron2`、`compatibility.md#training-hyperparameters`、`compatibility.md` 即为使用者获取启用细节的入口。)
