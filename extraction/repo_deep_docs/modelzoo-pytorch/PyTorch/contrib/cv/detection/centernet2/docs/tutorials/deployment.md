# Deployment

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/centernet2/docs/tutorials/deployment.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/centernet2/docs/tutorials/deployment.md

# 一体化深度解读:Centernet2 Deployment Guide

## 【定位】

本文档解决 **"如何将 detectron2 中用 Python 写的训练模型导出 (export) 为可部署 (deployable) 的产物"** 这一问题,系统性地描述了 export 方法、序列化格式、运行时三者之间的组合关系,以及它们在 tracing/scripting 和 caffe2_tracing 两条路径下的能力、限制与使用方式,使模型可以脱离 detectron2 依赖运行在 C++/Python 或 ONNX/Caffe2 等不同运行时上。

---

## 【技术要点】

1. **三种 Export Method**:tracing(依赖 PyTorch tracing 机制)、scripting(依赖 PyTorch scripting 机制)、`caffe2_tracing`(先用 Caffe2 ops 替换模型部分子结构,再走 tracing)。
2. **三种 Format**:TorchScript、Caffe2 protobuf、ONNX;分别对应 PyTorch、Caffe2、onnxruntime/TensorRT 等 runtime。
3. **元架构支持范围**:`GeneralizedRCNN`、`RetinaNet` 同时被 tracing/scripting/caffe2_tracing 三种方式支持;`PointRend` 仅 tracing;`PanopticFPN` 仅 caffe2_tracing;**Cascade R-CNN 不被任何方式支持**。
4. **环境约束**:tracing/scripting 路径要求 **PyTorch ≥ 1.8**;caffe2_tracing 路径要求 **ONNX ≥ 1.6**;exported model 通常需要 **torchvision**(或 torchvision 的 C++ 库)以支持某些 custom ops。
5. **关键 API 与示例文件**:TracingAdapter 与 `scripting_with_instances`(tracing/scripting 主入口)、`Caffe2Tracer`(caffe2_tracing 主入口);示例集中在 `tests/test_export_torchscript.py`(TestScripting、TestTracing)与 `tools/deploy/`。
6. **C++ 部署注意事项**:caffe2_tracing 导出的模型使用一种**特殊输入格式**(需参考 `Caffe2Tracer` 文档);**导出模型不含 post-processing**(例如 28×28 mask 仅是原始 layer 输出,需要用户自行加轻量后处理)。

---

## 【关键机制与数据】

**工作原理(三层抽象)**:
- **Export Method**:决定"如何把 Python 模型完整序列化为可部署形态"。
- **Format**:决定"序列化模型以什么形式写盘",TorchScript 由 PyTorch 直接读取,Caffe2 需要 protobuf,ONNX 由 onnxruntime/TensorRT 加载。
- **Runtime**:决定"加载序列化模型并执行推理的引擎";通常 runtime 与 format 强绑定(PyTorch↔TorchScript,Caffe2↔protobuf)。
- 原文明确表示 **"We don't plan to work on additional support for other formats/runtime, but contributions are welcome."**——即官方不主动扩展更多组合,但接受贡献。

**Tracing 与 Scripting 的关键差异**(原文):
- 动态分辨率:tracing ✅ / scripting ✅(都支持);
- batch size 要求:tracing 要求 **constant batch size**(batch size 需固定),scripting 支持 **dynamic batch size**;
- C++/Python 推理:tracing ✅ / scripting ❌(WIP_,原文链接指向 PyTorch issue #46944);
- extra runtime deps:两者都依赖 **torchvision**。

**Caffe2-tracing 关键特性**(原文):
- 替换部分模型为 Caffe2 ops 后导出;
- 可在 **C++ 或 Python** 中运行,**不依赖 detectron2/torchvision**;
- runtime 针对 **CPU 与 mobile 推理做了优化**,但**不针对 GPU 推理做优化**;
- 支持导出格式:Caffe2、**TorchScript、ONNX**(三种);
- 支持的 runtime:**Caffe2、PyTorch**;
- **batch inference 暂不支持**;
- 用户通过 register 添加的自定义扩展,只要**不包含控制流或 Caffe2 不可用的算子**(如 deformable convolution)即可支持,例如 custom backbones/heads 通常开箱即用。

**Post-processing 处理原则**(原文):
- 转换后的模型 **不包含** 把原始 layer 输出转换为格式化预测的 post-processing;
- 例如 C++ example 只产出 final layer 的 28×28 原始 mask,不做 post-process;
- 实际部署中应用常需自定义轻量后处理,因此**该步骤留给用户自行实现**;
- `Caffe2Model.__call__` 提供了一个 Python wrapper,接口与 PyTorch 版模型一致,内部执行 pre/post-processing 以匹配格式,可作为 Caffe2 Python API 使用 / 实现 pre/post-processing 的参考实现。

**外部转换路径**(原文):
- Conversion to TensorFlow 由 **tensorpack Faster R-CNN** 提供脚本支持(`https://github.com/tensorpack/tensorpack/tree/master/examples/FasterRCNN/convert_d2`);
- 通过**翻译 config 与权重**实现,故**只支持少数标准 R-CNN 模型**。

---

## 【表格解读】

> 原文为 RST 渲染表格,以下用 markdown 逐字还原:

| Export Method | tracing | scripting | caffe2_tracing |
|---|---|---|---|
| **Formats** | TorchScript | TorchScript | Caffe2, TorchScript, ONNX |
| **Runtime** | PyTorch | PyTorch | Caffe2, PyTorch |
| C++/Python inference | ✅ | ❌ (WIP_) | ✅ |
| Dynamic resolution | ✅ | ✅ | ✅ |
| Batch size requirement | Constant | Dynamic | Batch inference unsupported |
| Extra runtime deps | torchvision | torchvision | Caffe2 ops (usually already included in PyTorch) |
| Faster/Mask/Keypoint R-CNN | ✅ | ✅ | ✅ |
| RetinaNet | ✅ | ✅ | ✅ |
| PointRend R-CNN | ✅ | ❌ | ❌ |

(WIP_ 链接:`https://github.com/pytorch/pytorch/issues/46944`)

**逐行解读**:

- **Formats 行**:tracing 与 scripting 都只产出 **TorchScript**;`caffe2_tracing` 能力最强,可同时输出 **Caffe2 protobuf、TorchScript、ONNX** 三种格式——这使得同一份导出模型能在不同 runtime 间迁移。
- **Runtime 行**:tracing/scripting 都依赖 **PyTorch runtime**;`caffe2_tracing` 同时支持 **Caffe2 与 PyTorch**——这是因为它导出格式涵盖 Caffe2 protobuf 与 TorchScript。
- **C++/Python inference 行**:**tracing 与 caffe2_tracing 都可直接在 C++ 与 Python 上推理**;**scripting 目前在 C++ 推理上仍为 WIP**(对应 PyTorch issue #46944)。
- **Dynamic resolution 行**:三种方法**都支持**动态输入分辨率。
- **Batch size requirement 行**:**tracing 要求 batch size 固定 (Constant)**;**scripting 支持动态 batch size**;**caffe2_tracing 直接不支持 batch inference**——这是部署时必须关心的差异。
- **Extra runtime deps 行**:tracing/scripting 都需 **torchvision**(因含 custom ops);caffe2_tracing 仅需 **Caffe2 ops**,而这些 ops **通常已经包含在 PyTorch 中**,因此实际依赖极轻。
- **Faster/Mask/Keypoint R-CNN 行**:三类主流检测模型在**三种方法下都 ✅**,是最稳的支持集合。
- **RetinaNet 行**:与 Faster/Mask/Keypoint R-CNN 一致,**三种方法均 ✅**。
- **PointRend R-CNN 行**:**仅 tracing 支持**,scripting 与 caffe2_tracing 都 ❌——这一行直接约束了 PointRend 的部署路径。

---

## 【公式解读】

**原文无公式**。本文档为概念性 + 表格 + API 使用说明,未涉及数学公式或伪代码推导。

---

## 【关联】

本文档位于 deployment 教程入口,内部链接所揭示的上下游关系如下:

- **`../modules/export.html#detectron2.export.TracingAdapter`**(TracingAdapter 类):tracing 路径的**主 API**,负责把 detectron2 模型包装成可被 torch.jit.trace 跟踪的形态。
- **`../modules/export.html#detectron2.export.scripting_with_instances`**(`scripting_with_instances` 函数):scripting 路径的**主 API**,把 Instances 等动态结构转为 scripting 兼容形式。
- **`../../tests/test_export_torchscript.py`**(test_export_torchscript.py,含 `TestScripting` 与 `TestTracing`):tracing/scripting 用法的**真实示例**,文档明确推荐先让示例跑通再修改。
- **`../../tools/deploy`**(deployment example 目录):tracing/scripting 部署的**示例集合**。
- **`../modules/export.html#detectron2.export.Caffe2Tracer`**(Caffe2Tracer 类):caffe2_tracing 路径的**核心引擎**,负责算子替换与导出;同时其文档页还描述了 caffe2_tracing 模型的**特殊输入格式**。
- **`../modules/export`**:caffe2_tracing 相关 API 的**索引页**(`detectron2.export` 模块文档),含 `export_model.py` 等脚本调用入口。
- **`../../tools/deploy/`**:`export_model.py` 所在目录,作为 caffe2_tracing 的**官方示例脚本**;同时该目录下还有 **C++ examples for Mask R-CNN**,作为 C++ 端加载 caffe2_tracing 模型的参考实现。
- **`../modules/export.html#detectron2.export.Caffe2Model.__call__`**(`Caffe2Model.__call__` 方法):caffe2_tracing 模型的**Python wrapper**,提供与 PyTorch 版模型一致的接口(内部已封装 pre/post-processing),可作为"如何在 Python 中使用 Caffe2 转换模型"以及"如何实现 pre/post-processing"的参考模板。
- **`./models.md`**(pytorch versions of models):`Caffe2Model.__call__` 接口所对齐的 PyTorch 原生模型 API,理解这一点是阅读 wrapper 源码的前提。

整体上,本文档把"高层概念/支持矩阵(本文) → 主 API(`detectron2.export.*`)→ 示例(`tools/deploy/`, `tests/test_export_torchscript.py`)→ 后处理参考(`Caffe2Model.__call__`)"这条链路组织得非常清晰。

---

## 【使用方法】

> 原文未给出可直接复制运行的 shell 命令,而是**以 API 入口与示例文件作为"使用方法"**,以下按原文逐条还原:

- **tracing 导出主 API**:`TracingAdapter`(详见 `../modules/export.html#detectron2.export.TracingAdapter`)。
- **scripting 导出主 API**:`scripting_with_instances`(详见 `../modules/export.html#detectron2.export.scripting_with_instances`)。
- **caffe2_tracing 导出主 API**:`Caffe2Tracer`(详见 `../modules/export.html#detectron2.export.Caffe2Tracer`),它会替换模型部分为 Caffe2 ops,然后导出为 Caffe2 / TorchScript / ONNX。
- **tracing/scripting 示例文件**:
  - `../../tests/test_export_torchscript.py` 中的 `TestScripting` 与 `TestTracing` 类;
  - `../../tools/deploy` 部署示例。
  - 原文用法提示:"**Please check that these examples can run, and then modify for your use cases.**" 即先确保示例能跑通,再基于示例修改。
- **caffe2_tracing 示例文件**:
  - `../../tools/deploy/` 下的 `export_model.py`(原文:"we provide `export_model.py` as an example that uses these APIs to convert a standard model. For custom models/datasets, you can add them to this script.");
  - 对自定义模型/数据集,需要把相应配置加入该脚本。
- **C++/Python 加载模型**:
  - 可使用 **Caffe2 或 PyTorch runtime**;
  - `../../tools/deploy/` 下提供 **C++ examples for Mask R-CNN** 作为参考;
  - `caffe2_tracing` 导出模型使用**特殊输入格式**(参见 `Caffe2Tracer` 文档,C++ example 已处理);
  - 导出模型**不含 post-processing**(如 28×28 mask 原始输出),由用户在部署时自行添加。
- **Python wrapper 使用**:`Caffe2Model.__call__`(详见 `../modules/export.html#detectron2.export.Caffe2Model.__call__`),接口与 PyTorch 版模型一致,内部封装 pre/post-processing,既可直接用,也可作为 Caffe2 Python API / pre-post-processing 的实现参考。
- **TensorFlow 转换**:使用 tensorpack 提供的脚本(`https://github.com/tensorpack/tensorpack/tree/master/examples/FasterRCNN/convert_d2`),通过翻译 config 与权重实现,**仅支持少数标准 R-CNN 模型**。
- **版本要求**:
  - tracing/scripting 路径:**PyTorch ≥ 1.8**;
  - caffe2_tracing 路径:**ONNX ≥ 1.6**;
  - 依赖提示:exported model 通常需要 **torchvision**(或 torchvision 的 C++ 库)用于 custom ops;caffe2_tracing 模型**不依赖 detectron2/torchvision**,但可能用到 **Caffe2 ops(通常已随 PyTorch 自带)**。

**注**:文档明确承认 **"The usage now requires some user effort and necessary knowledge for each model to workaround the limitation of scripting and tracing. In the future we plan to wrap these under simpler APIs to lower the bar to use them."** 即当前 tracing/scripting 用法门槛较高,需用户针对每个模型手工绕开 scripting/tracing 的限制,未来计划封装更简单的 API。
