# changelog

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/FSAF_for_Pytorch/mmdetection/docs/changelog.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/FSAF_for_Pytorch/mmdetection/docs/changelog.md

# mmdetection Changelog 深度解读 (v2.5.0 – v2.10.0)

## 【定位】

本文件是 mmdetection 目标检测框架 2020-10 至 2021-03 期间 v2.5.0 至 v2.10.0 共 6 个版本的发布日志 (changelog), 记录每个版本**新增方法/特性 (New Features)**、**缺陷修复 (Bug Fixes)** 与**改进项 (Improvements)**, 是代码升级兼容性、迁移指南与功能演进的权威参考。

---

## 【技术要点】

1. **新检测器集成 (Highlights)** —— 在 6 个 release 中陆续引入 FPG、SCNet、Sparse R-CNN、Cascade RPN、TridentNet、DETR、ResNeSt、VarifocalNet、YOLACT、CentripetalNet、Faster R-CNN DC5 等方法, 每个均给出 arXiv 链接与 PR 号。
2. **ONNX / TensorRT 部署链路打通** —— v2.7.0 支持 YOLO、Mask R-CNN、Cascade R-CNN 导出 ONNX; v2.10.0 将 ONNX2TensorRT 拓展到 **SSD、FSAF、FCOS、YOLOv3、Faster R-CNN** (#4569)。
3. **配置 (cfg) 结构调整** —— v2.9.0 起将 `train_cfg` 与 `test_cfg` 由独立文件移入 model (#4347, #4489); v2.6.0 重构 pytorch2onnx API 至 `mmdet.core.export`, 并新增 `generate_inputs_and_wrap_model` (#3857, #3912)。
4. **FP16 接口迁移** —— v2.5.0 起将混合精度训练工具 `force_fp32`、`auto_fp16`、`wrap_fp16_model`、`Fp16OptimizerHook` 从 `mmdet.core.fp16` 迁至 `mmcv.runner`, 并声明"最终将于 v2.10.0 完全移除" (#3766, #3822)。
5. **可视化与后处理增强** —— v2.9.0 支持**多 IoU 评估 mAP** (#4398)、**按预测质量可视化** (#4441)、可视化后端由 OpenCV 切到 Matplotlib (#4389); v2.10.0 支持 NMS 返回保留框索引 (#4251)。
6. **训练基础设施** —— v2.10.0 支持 `EvalHook` 中 BN buffer 同步 (#4582)、sampler 种子选项 (#4665)、自定义 runner 类型 (#4570, #4669); v2.7.0 链接最佳 checkpoint (#3773); v2.6.0 支持 `batch_size > 1` 验证 (#3966)。

---

## 【关键机制与数据】

### (1) ONNX / TensorRT 推理链 (v2.7.0 → v2.10.0)
- 原文 (v2.7.0): "Support YOLO, Mask R-CNN, and Cascade R-CNN models exportable to ONNX (#4087, #4083)."
- 原文 (v2.10.0): "Support ONNX2TensorRT for SSD, FSAF, FCOS, YOLOv3, and Faster R-CNN (#4569)."
- 原文 (v2.9.0): "Add ONNX simplify option to Pytorch2ONNX script (#4468)."

### (2) FP16 接口迁移路径 (v2.5.0 → v2.10.0)
- 原文 (v2.5.0): "Mixed precision training utils in `mmdet.core.fp16` are moved to `mmcv.runner`, including `force_fp32`, `auto_fp16`, `wrap_fp16_model`, and `Fp16OptimizerHook`. A deprecation warning will be raised if users attempt to import those methods from `mmdet.core.fp16`, and will be finally removed in V2.10.0."
- 原文 (v2.10.0): "Clean deprecated FP16 API (#4571)." —— 即按计划在 v2.10.0 完成移除。

### (3) 配置体系重构
- 原文 (v2.9.0): "Move `train_cfg`/`test_cfg` into model (#4347, #4489)."
- 原文 (v2.10.0): "Get loading pipeline by checking the class directly rather than through config strings (#4619)."
- 原文 (v2.10.0): "Refactor nms config (#4636)."

### (4) 性能/训练改进
- 原文 (v2.8.0): "Avoid zero or too small value for beta in Dynamic R-CNN (#4303)."
- 原文 (v2.6.0): "Accelerate PAA training speed (#3985)."
- 原文 (v2.7.0): "Speed up expanding large images (#4089)."
- 原文 (v2.8.0): "Release pre-trained R50 and R101 PAA detectors with multi-scale 3x training schedules" (注: 此条出自 v2.9.0 #4495, 文中亦提及"3x 训练调度")
- 原文 (v2.7.0): "Support mixed precision training of SSD detector with other backbones (#4081)."

### (5) 数据集 / 评估
- 原文 (v2.9.0): "Support evaluate mAP by multiple IoUs (#4398)."
- 原文 (v2.9.0): "Support concatenate dataset for testing (#4452)."
- 原文 (v2.9.0): "Allow to customize classes in LVIS dataset (#4382)."
- 原文 (v2.6.0): "Use RoIAlign implemented in MMCV for inference in CPU mode (#3930)."

> 原文未提供具体数值 (mAP、fps 等性能数据) —— 性能数字仅以 PR 号与"加速/修复"措辞形式给出, 不含可量化的 benchmark 结果。

---

## 【表格解读】

**原文无表格**。整篇文档采用版本号 + 分类标题 (Highlights / New Features / Bug Fixes / Improvements) 的纯列表结构, 未出现任何 markdown/HTML 表格、参数对照表或性能对比表。

---

## 【公式解读】

**原文无公式**。文档是 changelog, 不包含数学公式、LaTeX 表达式或伪代码; 所有机制均以自然语言 + PR 号描述。

---

## 【关联】

依据文末提供的内部链接及文档上下文, 本文件与以下文档存在关联:

| 链接锚点 | 与本 changelog 的关联内容 |
|---|---|
| `model_zoo.md#comparison-with-detectron2` | 本文件 v2.7.0 起多次引入新模型 (DETR、Sparse R-CNN、Cascade RPN 等) 的预训练权重 (如 #4495 "Release pre-trained R50 and R101 PAA detectors with multi-scale 3x training schedules"), 这些权重的指标会汇总至 model_zoo 并与 Detectron2 对比。 |
| `compatibility.md#training-hyperparameters` | v2.5.0/v2.7.0 中涉及混合精度 (FP16) 从 `mmdet.core.fp16` 迁至 `mmcv.runner`、batch_size>1 验证、sampler 种子选项 (#4665)、runner 类型自定义 (#4570, #4669) 等, 均属训练超参数兼容性范畴。 |
| `compatibility.md` | v2.9.0 将 `train_cfg`/`test_cfg` 移入 model (#4347, #4489)、v2.7.0 对 PyTorch 1.7 兼容性 (#4103)、v2.8.0 删除 `mmdet.ops` (#4325) 等, 都是破坏性/兼容性变更, 应在 compatibility.md 中查阅迁移说明。 |

**版本之间的纵向关联**:
- v2.5.0 宣布 FP16 迁移 → v2.10.0 完成清理 (#4571)
- v2.6.0 重构 pytorch2onnx → v2.7.0 增加更多导出器 → v2.10.0 增加 ONNX2TensorRT
- v2.7.0 引入 Faster R-CNN DC5 → v2.8.0 修复 FCOS-HRNet 的 `img_norm_cfg` 性能 (#4250)
- v2.8.0 重构 Hungarian Assigner (#4259) 为 v2.9.0 Sparse R-CNN (#4219) 做准备

---

## 【使用方法】

原文未给出完整的"启用方式/配置项"清单, 但散见以下可操作信息:

1. **命令行参数 (CLI flags)**:
   - 原文 (v2.9.0): "Fix the error that the window data is not destroyed when `out_file is not None` and `show==False` (#4442)" —— 提示 `out_file` 与 `show` 参数。
   - 原文 (v2.6.0): "Fix `--show-dir` option in test script (#4025)" —— 提示 `test.py --show-dir` 选项。
   - 原文 (v2.7.0): "Support to override config through options in `inference.py` (#4175)" —— 推理脚本支持命令行覆盖 config。

2. **接口签名 / API**:
   - 原文 (v2.10.0): "Support batch inference in the inference API (#4462, #4526)"。
   - 原文 (v2.6.0): 重构后的导出路径为 `mmdet.core.export` + `generate_inputs_and_wrap_model` (#3857, #3912)。
   - 原文 (v2.5.0 → v2.10.0): `force_fp32` / `auto_fp16` / `wrap_fp16_model` / `Fp16OptimizerHook` 应从 **`mmcv.runner`** 而非 `mmdet.core.fp16` 导入。

3. **Hook / Runner 自定义**:
   - 原文 (v2.10.0): "Support to customize type of runner (#4570, #4669)"; "Support synchronizing BN buffer in `EvalHook` (#4582)"。

4. **可视化脚本**:
   - 原文 (v2.10.0): "Support video demo (#4420)"; "Add script for GIF demo (#4573)"。
   - 原文 (v2.9.0): "Deprecate `ImageToTensor` in `image_demo.py` (#4400)" —— 提示该函数已被弃用。

5. **遗留 / 待补充说明**: 原文在 v2.5.0 末尾以 `"[0, N-1] r"` 截断, **未提供完整的 Backwards Incompatible Changes 段落**, 本解读无法覆盖该处信息。
