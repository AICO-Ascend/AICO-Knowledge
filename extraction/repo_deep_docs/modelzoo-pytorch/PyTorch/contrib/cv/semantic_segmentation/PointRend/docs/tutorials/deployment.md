# Deployment

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/semantic_segmentation/PointRend/docs/tutorials/deployment.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/semantic_segmentation/PointRend/docs/tutorials/deployment.md

# 深度解读:PointRend Deployment Guide

## 【定位】

本文档系统描述 detectron2(及本文所属的 PointRend 实例分割模型)如何将 Python 训练模型通过**导出(export)**过程转换为可在 C++/Python 端独立运行的部署产物的能力,覆盖三种导出方法(tracing、scripting、caffe2_tracing)、对应格式(TorchScript、Caffe2 protobuf、ONNX)与运行时(PyTorch、Caffe2)的支持矩阵及限制。

---

## 【技术要点】

1. **三层概念划分**:导出方法(Export Method,如何把 Python 模型序列化为可部署形态)→ 文件格式(Format,序列化后的描述形式)→ 运行时(Runtime,加载并执行序列化模型的引擎),三者常强绑定(如 PyTorch 需 TorchScript、Caffe2 需 protobuf)。
2. **三种导出方法**:`tracing`(基于 PyTorch Tracing)、`scripting`(基于 PyTorch Scripting)、`caffe2_tracing`(先用 Caffe2 算子替换部分模型,再 tracing),其中只有 `caffe2_tracing` 能产出 Caffe2/ONNX 格式。
3. **动态分辨率与批大小差异**:tracing 支持动态输入分辨率但要求批大小固定;scripting 支持动态批大小;caffe2_tracing 不支持批推理(batch inference unsupported)。
4. **运行时依赖**:tracing/scripting 均需 torchvision(或其 C++ 库)用于部分自定义算子;caffe2_tracing 需 Caffe2 ops(通常已包含在 PyTorch 中)。
5. **PointRend 的导出限制**:PointRend R-CNN 仅 `tracing` 方式支持(`scripting` 与 `caffe2_tracing` 均标记 ❌),这是本文档所在目录(PointRend)需要特别注意的硬约束。
6. **后处理不在导出产物中**:caffe2_tracing 转换后的模型只包含最终层原始输出(如 28x28 masks),不包含将原始输出转换为结构化预测结果的后处理逻辑,需用户自行实现。

---

## 【关键机制与数据】

- **导出基本流程(原文)**:"Models written in Python need to go through an export process to become a deployable artifact."
- **TorchScript 路径(原文)**:"Models can be exported to TorchScript format, by either tracing or scripting ... The output model file can be loaded without detectron2 dependency in either Python or C++. The exported model often requires torchvision (or its C++ library) dependency for some custom ops."
- **版本门槛(原文)**:"This feature requires PyTorch ≥ 1.8 (or latest on github before 1.8 is released)."(指 tracing/scripting)
- **ONNX 版本门槛(原文)**:"This feature requires 1.9 > ONNX ≥ 1.6."(指 caffe2_tracing)
- **meta architecture 覆盖范围(原文)**:tracing/scripting 支持 `GeneralizedRCNN`、`RetinaNet`,Cascade R-CNN 不支持,PointRend 仅 tracing 支持;caffe2_tracing 在 `GeneralizedRCNN`、`RetinaNet`、`PanopticFPN` 三种 meta architecture 下覆盖大多数官方模型,Batch inference 不支持。
- **caffe2_tracing 的运行特性(原文)**:"It has a runtime optimized for CPU & mobile inference, but not optimized for GPU inference."——即擅长 CPU/移动端推理,不擅长 GPU 推理。
- **Caffe2Tracer 机制(原文)**:"It replaces parts of the model with Caffe2 operators, and then export the model into Caffe2, TorchScript or ONNX format."
- **C++ 部署输入格式特殊(原文)**:"Models exported with `caffe2_tracing` method take a special input format described in [documentation](../modules/export.html#detectron2.export.Caffe2Tracer). This was taken care of in the C++ example."
- **Python 包装器(原文)**:`Caffe2Model.__call__` 提供与 PyTorch 版模型接口一致的 Python wrapper,内部完成 pre/post-processing,可用作 Caffe2 Python API 的参考实现。
- **外部 TF 转换(原文)**:`tensorpack Faster R-CNN` 提供将部分 detectron2 R-CNN 模型转换为 TensorFlow pb 格式的脚本,通过翻译 config 与权重实现,故"only support a few models"。

---

## 【表格解读】

下表逐字还原原文的导出支持矩阵:

| Export Method | tracing | scripting | caffe2_tracing |
|---|---|---|---|
| **Formats** | TorchScript | TorchScript | Caffe2, TorchScript, ONNX |
| **Runtime** | PyTorch | PyTorch | Caffe2, PyTorch |
| C++/Python inference | ✅ | ✅ | ✅ |
| Dynamic resolution | ✅ | ✅ | ✅ |
| Batch size requirement | Constant | Dynamic | Batch inference unsupported |
| Extra runtime deps | torchvision | torchvision | Caffe2 ops (usually already included in PyTorch) |
| Faster/Mask/Keypoint R-CNN | ✅ | ✅ | ✅ |
| RetinaNet | ✅ | ✅ | ✅ |
| PointRend R-CNN | ✅ | ❌ | ❌ |

逐行解读:
- **行 1 Formats**:tracing 与 scripting 仅产出 TorchScript;caffe2_tracing 是唯一能产出 Caffe2 与 ONNX 的路径,也是跨生态互操作的唯一桥梁。
- **行 2 Runtime**:tracing/scripting 只能跑在 PyTorch 运行时;caffe2_tracing 可同时跑在 Caffe2 与 PyTorch,体现其"以 Caffe2 算子替换"的天然兼容性。
- **行 3 C++/Python inference**:三种方式均支持 C++ 与 Python 推理,这是 detectron2 部署栈的基础保证。
- **行 4 Dynamic resolution**:三者均支持动态输入分辨率(图像 H×W 可变),但批大小约束见下一行。
- **行 5 Batch size requirement**:差异显著——tracing 必须固定 batch size,scripting 动态 batch,caffe2_tracing 直接不支持 batch 推理,只能单样本推理,这是部署时选型最关键的权衡点。
- **行 6 Extra runtime deps**:tracing/scripting 都需 torchvision 支撑自定义算子;caffe2_tracing 依赖 Caffe2 ops(原文注明通常已含在 PyTorch 中),所以实际引入代价最低。
- **行 7–8 经典模型**:Faster/Mask/Keypoint R-CNN 与 RetinaNet 在三种方法下全部 ✅,说明这些是 export pipeline 优先覆盖的"主力"模型。
- **行 9 PointRend R-CNN(本仓库目录所对应的模型)**:仅 tracing 支持,scripting 与 caffe2_tracing 均 ❌。这意味着 PointRend 部署只能走 tracing 这一条路径,且无法用 caffe2_tracing 获得 CPU/移动端优化与 ONNX 输出,这是本文档最重要的工程含义。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- 与 **`detectron2.export.TracingAdapter`**(`../modules/export.html#detectron2.export.TracingAdapter`)关联:tracing 路径的主导出 API,负责包装模型以处理 instances 等非 Tensor 输入,使 tracing 能正确序列化。
- 与 **`detectron2.export.scripting_with_instances`**(`../modules/export.html#detectron2.export.scripting_with_instances`)关联:scripting 路径的主导出 API,处理 instances 类型输入的 scripting 转换。
- 与 **`tests/test_export_torchscript.py`**(`../../tests/test_export_torchscript.py`)关联:提供 `TestScripting` 与 `TestTracing` 两个测试用例,是上述两个 API 的实际使用示例。
- 与 **`tools/deploy`**(`../../tools/deploy`)关联:同时承载两种用途——一是 tracing/scripting 的"deployment example",二是 caffe2_tracing 的 `export_model.py` 与 C++ 推理示例(原文用 `../../tools/deploy/` 链接),是端到端使用参考。
- 与 **`detectron2.export.Caffe2Tracer`**(`../modules/export.html#detectron2.export.Caffe2Tracer`)关联:caffe2_tracing 的核心类,负责替换算子并产出 Caffe2/TorchScript/ONNX;同时记录了 caffe2_tracing 模型的**特殊输入格式**说明。
- 与 **`detectron2.export`**(`../modules/export`)模块整体关联:API 文档总入口,覆盖所有 export 相关符号。
- 与 **`detectron2.export.Caffe2Model.__call__`**(`../modules/export.html#detectron2.export.Caffe2Model.__call__)关联:Python 侧加载 Caffe2 转换后模型的包装方法,接口与 PyTorch 版模型一致,内部完成 pre/post-processing,可作为自定义部署前/后处理实现的参考。
- 与 **`./models.md`** 关联:`Caffe2Model.__call__` 的接口对齐对象,即 PyTorch 版 detectron2 模型接口。
- 与**外部 `tensorpack Faster R-CNN`** 关联:提供 detectron2 → TensorFlow pb 的有限转换能力,但仅支持少数标准 R-CNN 模型。

---

## 【使用方法】

原文给出的使用方式(分两类导出路径):

1. **Tracing / Scripting 路径**
   - 主 API:参考 [`TracingAdapter`](../modules/export.html#detectron2.export.TracingAdapter) 与 [`scripting_with_instances`](../modules/export.html#detectron2.export.scripting_with_instances)。
   - 示例代码:参考 [`tests/test_export_torchscript.py`](../../tests/test_export_torchscript.py) 中的 `TestScripting` 与 `TestTracing` 测试用例。
   - 端到端示例:参考 [`tools/deploy`](../../tools/deploy) 中的 deployment example,先确认这些示例可运行,再按需修改为自己的用例。
   - 版本要求:PyTorch ≥ 1.8(或 1.8 发布前最新的 GitHub 版本)。
   - 用户负担:原文明确指出"The usage now requires some user effort and necessary knowledge for each model to workaround the limitation of scripting and tracing",未来计划提供更简易的封装 API。

2. **Caffe2-tracing 路径**
   - 核心 API:`detectron2.export.Caffe2Tracer`(`../modules/export.html#detectron2.export.Caffe2Tracer`),完整 API 见 [`modules/export`](../modules/export)。
   - 示例脚本:[`tools/deploy/`](../../tools/deploy/) 下的 `export_model.py`,展示如何把标准模型转换为 Caffe2/TorchScript/ONNX;自定义模型/数据集可在此脚本基础上扩展。
   - 版本要求:1.9 > ONNX ≥ 1.6。
   - 覆盖范围:支持 `GeneralizedRCNN`、`RetinaNet`、`PanopticFPN` 三种 meta architecture,不支持 Cascade R-CNN 与 batch inference。
   - C++/Python 使用方式:见 [`tools/deploy/`](../../tools/deploy/) 下的 C++ 示例(Mask R-CNN);注意 caffe2_tracing 模型有特殊输入格式(见 `Caffe2Tracer` 文档,C++ 示例已处理);模型仅产出最终层原始输出(如 28x28 masks),不包含后处理;Python 侧可通过 `Caffe2Model.__call__`(`../modules/export.html#detectron2.export.Caffe2Model.__call__`)以与 PyTorch 模型一致的接口调用,内部自动完成 pre/post-processing,可作为生产部署前后处理的实现参考。

3. **TensorFlow 转换(原文)**
   - 使用外部项目 `tensorpack Faster R-CNN`,通过翻译 configs 与 weights 将少数标准 detectron2 R-CNN 模型转为 TF pb 格式;仅支持少量模型,detectron2 本身"don't plan to work on additional support for other formats/runtime, but contributions are welcome"。

> **针对本仓库 PointRend 路径的关键约束(综合自表格与覆盖范围章节)**:PointRend R-CNN 仅 `tracing` 方式可导出,`scripting` 与 `caffe2_tracing` 不可用,因此部署方案应优先采用 tracing → TorchScript → PyTorch Runtime 路径。
