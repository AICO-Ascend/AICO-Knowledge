# changelog

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/dev/perf/CascadeMaskRCNN_iflytek_for_PyTorch/docs/changelog.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/dev/perf/CascadeMaskRCNN_iflytek_for_PyTorch/docs/changelog.md

## 【定位】

本文通过记录 MMDetection 从 **v2.10.0（01/03/2021）** 到 **v2.13.0（01/6/2021）** 的方法、训练、评测及 ONNX/TensorRT 支持变化，说明 Cascade Mask R-CNN 所依赖的检测框架如何在算法扩展、批量/动态推理、统一初始化与注册、掩码评测及兼容性修复方面持续演进。

## 【技术要点】

1. **版本演进脉络清晰**：文档依次覆盖 v2.10.0、v2.11.0、v2.12.0 和 v2.13.0；其中 v2.12.0 开启了一轮预计持续到 **v2.15.0（maybe longer）** 的大规模重构，并引入多项不向后兼容的变更。

2. **算法与骨干网络持续扩展**：v2.10.0 增加 FPG；v2.11.0 增加 Localization Distillation；v2.12.0 增加 AutoAssign、YOLOF、Deformable DETR；v2.13.0 增加 CenterNet、Seesaw Loss，以及 MobileNetV2 和其 **inverted residual block**。同时支持 MIM，并发布或更新 FPG、YOLOv3、DetectoRS ResNet-101、混合精度 DCN Mask R-CNN 等模型权重。

3. **v2.12.0 是基础设施兼容性拐点**：依赖升级到 **MMCV 1.3.3**，原因是其中包含统一的 `BaseModule`、模型注册表以及 Deformable DETR 使用的 CUDA 算子 `MultiScaleDeformableAttn`；原文明确建议跳过存在已知问题的 MMCV 1.3.2，但同时说明其在多数情况下或许可以工作。

4. **批量与动态形状推理分阶段完善**：v2.10.0 支持 SSD、FSAF、FCOS、YOLOv3、Faster R-CNN 的 ONNX2TensorRT；v2.11.0 开始支持 Faster R-CNN 和主流单阶段检测器的 Pytorch2ONNX 批量推理及动态形状；v2.12.0 将稳定支持扩展到 SSD、FSAF、FCOS、YOLOv3、RetinaNet、Faster R-CNN、Mask R-CNN；v2.13.0 又为 CornerNet 增加动态形状 ONNX 导出，并重构两阶段检测器导出逻辑、更新 RoI extractor。

5. **训练与评测机制发生结构性调整**：统一初始化由 `BaseModule` 接收 `init_cfg`，训练代码必须显式调用 `model.init_weights()`；统一注册表迁移到 MMCV 后，符合条件的其他 OpenMMLab 项目骨干网络可直接通过配置使用，无需复制代码。掩码 AP 计算改为使用真实掩码面积，并通过 `mask_soft` 允许非二元掩码。

6. **稳定性修复覆盖多种推理边界**：包括空 GT、零长度 `det_bboxes`、空 RoI、零尺寸 RoI、单类别数据集、FP16 训练、Python 3.8 下 DETR 迭代以及 ONNX Runtime 性能回退等问题。性能描述仅有“节省内存并保持速度”“更高性能”等定性结论，没有给出具体指标。

## 【关键机制与数据】

1. **统一初始化链路**  
   **原文：** `BaseModule` 接受 `init_cfg`，以灵活、统一的方式初始化模块参数；过去由 detector 自动处理的初始化，现在要求训练脚本显式调用 `model.init_weights()`。相关模型已重新评测以确保准确率。  
   这意味着下游训练代码不能只替换检测器模型，还必须同步调整初始化入口；v2.12.0 原文也明确要求下游项目据此更新代码。

2. **跨项目骨干网络复用**  
   **原文：** MMDetection 迁移到继承自 MMCV 的模型注册表；只要某个 OpenMMLab 项目支持相应 backbone，并且该项目同样使用 MMCV registry，MMDetection 就可以仅修改配置使用它，而不需要复制 backbone 代码。  
   该机制使 MobileNetV2 等跨项目骨干的接入方式从代码移植转向配置选择；Deformable DETR 则进一步依赖 MMCV 提供的 `MultiScaleDeformableAttn` CUDA 算子。

3. **部署能力的数据流演进**  
   **原文：** 可串联为“PyTorch 模型 → 支持批量输入与动态形状的 ONNX → 部分指定模型的 TensorRT”。v2.10.0 的 ONNX2TensorRT 覆盖五种模型，v2.12.0 的稳定动态形状 ONNX 覆盖七种模型，v2.13.0 又增加 CornerNet。  
   这些列表的覆盖范围并不完全相同，因此不能据此推断文档已经为所有 ONNX 模型统一提供 TensorRT 支持。

4. **掩码生成与面积评测**  
   **原文：** `mask_soft` 用于允许非二元 masks；旧版本在计算小、中、大实例的 mask AP 时使用边界框面积，v2.12.0 在计算 mask AP 时弹出 `bbox` 键，改为使用掩码面积。  
   原文明确说明，这一变化不影响整体 mask AP 评测结果，但会使小、中、大实例的统计更准确，并与 Detectron2 等项目中相似模型的 mask AP 保持一致。

5. **空数据与异常输入处理**  
   **原文：** Cascade RPN 支持空 GT 训练；VFNet、GFL、FCOS 通过调整 `reduce_mean` 修复空 GT 训练挂起；Cascade R-CNN TTA 修复 `det_bboxes` 长度为 0 时的测试错误；CARAFE 修复 `mask_head` 空 bbox 错误；RoI Heads 支持空 RoI 测试。  
   这些改动共同扩大了框架在空标注、空预测和无有效候选区域场景下的稳定性，但没有提供异常样本比例或修复前后的吞吐数据。

6. **性能数据边界**  
   **原文：** FP16 的 `bbox_overlaps` IoU 计算被描述为“save memory and keep speed”；YOLOv3 head 使用更好的参数初始化以获得“higher performance”；Faster R-CNN 修复了 ONNX Runtime 性能下降。  
   文档没有提供准确率、AP、延迟、吞吐量、显存占用、训练时间或模型对比数值，因此不能从这些定性描述推导具体提升幅度。括号中的 `#4750`、`#4898`、`#5039` 等是问题追踪编号，不是性能指标。

## 【表格解读】

原文无表格。

## 【公式解读】

原文无公式。

## 【关联】

- **`model_zoo.md#comparison-with-detectron2`**：v2.12.0 的 mask AP 计算改用真实掩码面积，并明确与 Detectron2 中相似模型的 mask AP 对齐；统一初始化后模型又经过重新评测。此外，文档将 `pycocotools` 替换为 `mmpycocotools` 的问题处理为改用 `pycococotools`，使 Detectron2 与 MMDetection 可以在同一环境中共存。这些内容直接关联 Detectron2 兼容性及模型表现比较。

- **`compatibility.md#training-hyperparameters`**：v2.12.0 引入 MMCV 版本、`BaseModule` 初始化、显式 `model.init_weights()` 等训练接口变化，下游项目必须同步更新。`init_cfg`、sampler 的 seed option、runner 类型自定义以及同步 BN buffer 等训练相关能力，也属于下游项目核对依赖和训练配置兼容性的范围。

- **`compatibility.md`**：ONNX2TensorRT、Pytorch2ONNX、动态形状和批量推理的支持范围随版本扩大。v2.12.0 对 MMCV 1.3.3 的依赖以及 v2.13.0 对 CornerNet、两阶段检测器和 RoI extractor 的导出调整，意味着下游部署代码需要按具体模型和版本核对能力，不能把单个模型的支持状态外推到整个模型集合。

- **框架内部关系**：CenterNet、Seesaw Loss、AutoAssign、YOLOF、Deformable DETR 等新方法依赖统一的模型注册、参数初始化和组件算子；Mask R-CNN、Cascade R-CNN、YOLOv3、RetinaNet 等模型的 ONNX 支持又共同依赖 RoI extractor、bbox coder、检测头批量处理和导出流程的逐步完善。v2.13.0 中支持的 MIM 也位于这一统一组件管理体系的上层，但原文没有给出 MIM 的具体调用命令。

## 【
