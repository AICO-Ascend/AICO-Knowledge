# Deployment

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/dev/cv/image_classification/SlowFast_ID0646_for_PyTorch/detectron2/docs/tutorials/deployment.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/dev/cv/image_classification/SlowFast_ID0646_for_PyTorch/detectron2/docs/tutorials/deployment.md

# 一体化深度解读:Deployment 文档

## 【定位】

这篇文档系统阐述 detectron2 中"Python 模型 → 可部署产物"的导出(Export)流程,定义"导出方法(Export Method)/格式(Format)/运行时(Runtime)"三个核心概念,并给出 **tracing / scripting / caffe2_tracing** 三条具体部署路径的覆盖范围、依赖约束与使用方法,以及一个第三方 TensorFlow 转换路径,目的是为模型出库部署提供选型参考与操作指引。

## 【技术要点】

1. **三要素模型**:导出方法(how to serialize)≠ 格式(file 描述)≠ 运行时(执行引擎),三者解耦但运行时往往绑定格式(PyTorch↔TorchScript,Caffe2↔protobuf)。
2. **三种导出方法**:① `tracing`——基于一次样本 trace 出图;② `scripting`——直接用 TorchScript 编译器解析 Python 代码;③ `caffe2_tracing`——先用 Caffe2 op 替换模型子图,再 trace,可输出 Caffe2 / TorchScript / ONNX 三种格式。
3. **关键版本约束**:Tracing/Scripting 路径要求 **PyTorch ≥ 1.8**;Caffe2-tracing 路径要求 **1.9 > ONNX ≥ 1.6**。
4. **批量处理差异**:tracing 下 batch size 须**固定(Constant)**;scripting 支持**动态(Dynamic)** batch;caffe2_tracing **不支持 batch 推理**。
5. **后处理边界**——caffe2_tracing 导出的模型**不包含**把 raw layer output 转成格式化的 post-processing 操作(原文举例如 28×28 mask raw 输出),留给上层应用自行实现。
6. **C++/Python 推理**:三条路径都支持;但 caffe2_tracing 路径下模型额外依赖 Caffe2 ops(原文称"usually already included in PyTorch")。

## 【关键机制与数据】

- **工作原理**:
  - **tracing**:对输入样本跑一遍前向,把执行路径记录为 TorchScript IR,适合无控制流的子图;控制流不可变 → batch size 必须 fixed。
  - **scripting**:由 TorchScript 编译器解析 Python 源码生成 IR,保留控制流 → batch size 可动态。
  - **caffe2_tracing**:先做算子替换(把模型中 PyTorch 算子置换成 Caffe2 实现)以获得更小、更可移植的图,然后再 trace 导出到多种格式。
- **数据流差异**:caffe2_tracing 路径下模型取特殊输入格式(由 Caffe2Tracer 文档描述),输出为 raw feature maps(原文:"28x28 masks"),不做 NMS/ROI 后处理;Caffe2Model.__call__ 的 Python wrapper 则在内部补全 pre/post-processing,接口对齐 PyTorch 版模型。
- **性能定位**(原文):caffe2_tracing 转换的模型对 **CPU & mobile 推理有 runtime 优化**,但**对 GPU 推理未做优化**。
- **可移植性**:TorchScript 输出无需 detectron2 依赖即可加载(tracing/scripting 路径);caffe2_tracing 输出无需 detectron2/torchvision 依赖即可加载。

## 【表格解读】

原文表格用 `eval_rst` RST 指令写出,我用 markdown **逐字还原**:

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

**逐行解读**:
- **行 1 Formats / 行 2 Runtime**:三种导出方法产生的文件格式与可执行引擎不完全等价——caffe2_tracing 一条方法可同时产出 3 种格式、跑在 2 种 runtime 上,是覆盖最广的一条路径。
- **行 C++/Python inference**:三条路径都允许脱离 Python 训练栈做 C++ 或 Python 推理,意味着可落地到生产环境。
- **行 Dynamic resolution**:三种方法都支持变输入分辨率(即不同尺寸图像可送入同一模型),不会因分辨率变化而失效。
- **行 Batch size requirement**:**最关键的差异点**——tracing 因记录固定执行轨迹,batch size 必须固定;scripting 因保留控制流,batch size 可动态;caffe2_tracing 当前不支持 batch 推理(只能单张或固定 batch=1)。
- **行 Extra runtime deps**:tracing/scripting 都额外依赖 torchvision(用于其中部分自定义算子);caffe2_tracing 依赖 Caffe2 ops,原文指出该依赖"通常已包含在 PyTorch 中",所以引入成本低。
- **行 Faster/Mask/Keypoint R-CNN**:三种通用检测模型在三种方法下全部 ✅,是部署覆盖最完整的模型族。
- **行 RetinaNet**:同上一致,RetinaNet 在三种方法下也全部 ✅。
- **行 PointRend R-CNN**:只能通过 tracing 导出;scripting 与 caffe2_tracing 均 ❌,部署 PointRend 模型时**必须**走 tracing 路径。

## 【公式解读】

原文无公式。

## 【关联】

- **导出主入口模块**:文档反复引用 [`../modules/export.html`](../modules/export.html),该模块承载所有 export 能力。
- **Tracing 路径**:依赖 [`TracingAdapter`](../modules/export.html#detectron2.export.TracingAdapter) 作为主 API,示例参考 [`../../tests/test_export_torchscript.py`](../../tests/test_export_torchscript.py) 中的 `TestScripting` / `TestTracing`。
- **Scripting 路径**:依赖 [`scripting_with_instances`](../modules/export.html#detectron2.export.scripting_with_instances),与 tracing 共享示例代码。
- **Caffe2-tracing 路径**:以 [`Caffe2Tracer`](../modules/export.html#detectron2.export.Caffe2Tracer) 为核心,负责算子替换与多格式导出;[**export_model.py**](../../tools/deploy/) 给出标准模型转换示例(用户可基于它添加自定义模型/数据集);[**C++ examples**](../../tools/deploy/) 提供 Mask R-CNN 的 C++ 部署参考。
- **Python 侧使用**:[`Caffe2Model.__call__`](../modules/export.html#detectron2.export.Caffe2Model.__call__) 给出 Python wrapper,其接口与 [PyTorch 版模型](./models.md) 一致,内部补齐 pre/post-processing,可作为 Caffe2 Python API 与生产级后处理实现范式。
- **TensorFlow 转换**(第三方):链接到 [tensorpack Faster R-CNN](https://github.com/tensorpack/tensorpack/tree/master/examples/FasterRCNN/convert_d2),通过翻译 config + weights 实现,**仅支持**若干标准 R-CNN 模型,与上述三条原生路径并行但不在 detectron2 主线维护内。
- **PyTorch 官方知识依赖**:tracing/scripting 的语义细节指向 [Intro_to_TorchScript_tutorial](https://pytorch.org/tutorials/beginner/Intro_to_TorchScript_tutorial.html),是阅读本篇的前置知识。

## 【使用方法】

1. **选型**:
   - 想纯 PyTorch 生态部署 → tracing / scripting;
   - 想发到 CPU/mobile、追求更小依赖、或需要 ONNX 输出 → caffe2_tracing;
   - 部署 PointRend → **必须** tracing;
   - 需要动态 batch → **必须** scripting;
   - 部署到 TensorFlow → 用第三方 tensorpack 脚本(仅限少数 R-CNN 模型)。
2. **Tracing/Scripting 调用路径**(原文指引):
   - 主 API:`TracingAdapter`、`scripting_with_instances`;
   - 示例:看 `test_export_torchscript.py` 的 `TestScripting` / `TestTracing`、以及 `tools/deploy` 目录下的 deployment example;
   - 跑通示例后再按你的模型改动;
   - 限制:可能需要针对模型做 workaround,文档预告未来会提供更高层 API。
3. **Caffe2-tracing 调用路径**(原文指引):
   - 入口类:`Caffe2Tracer`;
   - 完整示例脚本:`tools/deploy/export_model.py`(可在此加入自定义模型/数据集);
   - C++ 加载:参考 `tools/deploy/` 下 Mask R-CNN 的 C++ example,该示例已处理 caffe2_tracing 模型的特殊输入格式;
   - 注意:模型**不含** post-processing(例:只产出 28×28 mask 原图,不做 ROI align 后处理),需在部署侧自行实现;
   - Python 侧可使用 `Caffe2Model.__call__` wrapper,其接口对齐 PyTorch 模型,可作为后处理实现的参考样板。
5. **未涉及项**:
   - 原文未给出具体 CLI 命令或 yaml 配置项;
   - 原文未给出具体安装 Caffe2 ops / torchvision C++ 库的步骤;
   - 原文未涉及量化、TensorRT 直接集成、性能 benchmark 数字。
   - 原文亦未直接给出"应当使用何种 batch size、输入分辨率范围"的具体数值,仅以 ✅ / ❌ 与 Constant/Dynamic 表述能力差异。
