# Deployment

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/dev/cv/detection/FasterRCNN-Resnet50-FPN_ID1552_for_PyTorch/docs/tutorials/deployment.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/dev/cv/detection/FasterRCNN-Resnet50-FPN_ID1552_for_PyTorch/docs/tutorials/deployment.md

# 部署文档深度解读：detectron2 模型导出至 Caffe2 格式

## 【定位】
本文档解决"如何将 detectron2 训练的 PyTorch 检测模型通过 Caffe2 格式导出,从而脱离 detectron2 依赖,在 CPU/移动端进行推理部署"的问题,描述了导出流程、转换工具、C++/Python 加载方式及限制说明。

---

## 【技术要点】

1. **导出路径**:detectron2 → ONNX → Caffe2 格式;导出后的 Caffe2 模型可在 Python 或 C++ 中运行,**无需 detectron2 依赖**;运行时针对 **CPU 与移动端推理优化**,**未针对 GPU 推理优化**。
2. **环境要求**:**PyTorch ≥ 1.4** 且 **ONNX ≥ 1.6**。
3. **覆盖架构(3 种 meta architectures)**:`GeneralizedRCNN`、`RetinaNet`、`PanopticFPN`,以及这三种架构下的大部分官方模型;通过注册机制加入的自定义扩展(只要不包含 Caffe2 不支持的控制流或算子,如可变形卷积)同样受支持,自定义 backbone 和 head 通常开箱即用。
4. **转换工具**:`tools/deploy/caffe2_converter.py`,封装了导出 API;需提供有效权重和样例输入用于模型 trace,因此脚本需要数据集。
5. **评估与精度**:`--run-eval` 标志可评估转换后模型的精度;因实现间数值精度差异,**精度差异通常在 0.1 AP 以内**,文档建议始终验证转换精度。
6. **输出文件**:`model.pb`(网络结构)与 `model_init.pb`(网络参数)两个文件为部署必需;同时生成 `model.svg` 可视化网络图,`model.pb` 可用 netron 可视化。

---

## 【关键机制与数据】

- **工作原理(原文)**:通过 ONNX 作为中间表示,将 detectron2 的 PyTorch 模型转换为 Caffe2 格式;转换时需要 trace,因此必须有有效权重和样例输入。
- **输入张量规格(原文)**:转换后的模型接受**两个**输入张量——
  - `"data"`:NCHW 格式图像;
  - `"im_info"`:N×3 张量,每张图由 `(height, width, 1.0)` 组成(由于 padding,`"data"` 的实际 shape 可能大于 `"im_info"` 中的尺寸)。
- **后处理策略(原文)**:转换后的模型**不包含**将原始层输出转换为格式化预测的后处理操作。例如,文档中的命令仅产生最终层的原始输出(28×28 masks),因为实际部署时应用常需自定义轻量级后处理,故保留给用户自行实现。
- **精度数据(原文)**:PyTorch 与 Caffe2 实现因数值精度差异,精度差通常**在 0.1 AP 以内**。
- **Python 包装器(原文)**:`Caffe2Model.__call__` 方法的接口与 PyTorch 版模型**完全一致**,内部自动应用 pre/post-processing 以匹配格式,可作为使用 Caffe2 Python API 及实现 pre/post-processing 的参考。
- **C++ 示例推理命令(原文)**:`./caffe2_mask_rcnn --predict_net=./model.pb --init_net=./model_init.pb --input=input.jpg`

---

## 【表格解读】

**原文无表格。** 文档主要以命令、列表和段落形式呈现,未出现参数表、性能对比表或配置项表格。

---

## 【公式解读】

**原文无公式。** 文档未包含任何 LaTeX 或伪代码形式的数学公式。

---

## 【关联】

文档通过以下内部链接建立了与 detectron2 项目其他模块的依赖与互补关系:

| 内部链接 | 关联作用 |
|---|---|
| `../modules/export` | **上游依赖**:导出 API 的官方文档,`caffe2_converter.py` 即基于这些 API 实现 |
| `../modules/export.html#detectron2.export.Caffe2Model.__call__` | **下游使用**:`Caffe2Model.__call__` Python 包装器,提供与 PyTorch 模型一致的接口并自动处理 pre/post-processing |
| `builtin_datasets.md` | **前置条件**:转换前需准备 COCO 数据集(因为 trace 需要样例输入) |
| `../../MODEL_ZOO.md` | **模型来源**:从 Model Zoo 选取待转换的官方模型权重 |
| `../../tools/deploy/` | **工具与示例**:`caffe2_converter.py` 与 C++ 示例 `caffe2_mask_rcnn.cpp` 所在目录 |
| `../../docker/` | **运行环境**:官方 detectron2 docker,用于编译 C++ 示例 |
| `./models.md` | **接口对比**:PyTorch 版模型接口文档,Python 包装器的接口以此为参照 |

模块间数据流关系:**`MODEL_ZOO.md` 提供权重 + `builtin_datasets.md` 提供样例输入 → `tools/deploy/caffe2_converter.py`(调用 `../modules/export` API)→ 生成 Caffe2 模型 → `tools/deploy/caffe2_mask_rcnn.cpp`(C++)或 `Caffe2Model.__call__`(Python)加载并推理,接口对齐 `./models.md`**。

---

## 【使用方法】

### 1. Python 模型转换(以官方 Mask R-CNN 为例)

```bash
cd tools/deploy/ && ./caffe2_converter.py --config-file ../../configs/COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml \
    --output ./caffe2_model --run-eval \
    MODEL.WEIGHTS detectron2://COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x/137849600/model_final_f10217.pkl \
    MODEL.DEVICE cpu
```

**关键配置项(原文)**:
- `--config-file`:模型配置文件路径;
- `--output`:转换后模型输出目录;
- `--run-eval`:启用后会在转换后运行评估验证精度(差异应在 0.1 AP 以内);
- `MODEL.WEIGHTS`:权重来源(支持 `detectron2://` 协议从 Model Zoo 下载);
- `MODEL.DEVICE`:trace 设备(此处设为 `cpu`)。

### 2. C++ 编译环境(原文)

编译 `caffe2_mask_rcnn.cpp` 需要:
- 内嵌 caffe2 的 PyTorch;
- gflags、glog、opencv;
- 与 caffe2 版本匹配的 protobuf headers;
- 若 caffe2 使用 MKL 构建,则需 MKL headers。

### 3. C++ 编译命令(原文,在官方 detectron2 docker 内执行)

```bash
sudo apt update && sudo apt install libgflags-dev libgoogle-glog-dev libopencv-dev
pip install mkl-include
wget https://github.com/protocolbuffers/protobuf/releases/download/v3.6.1/protobuf-cpp-3.6.1.tar.gz
tar xf protobuf-cpp-3.6.1.tar.gz
export CPATH=$(readlink -f ./protobuf-3.6.1/src/):$HOME/.local/include
export CMAKE_PREFIX_PATH=$HOME/.local/lib/python3.6/site-packages/torch/
mkdir build && cd build
cmake -DTORCH_CUDA_ARCH_LIST=$TORCH_CUDA_ARCH_LIST .. && make

# 运行推理
./caffe2_mask_rcnn --predict_net=./model.pb --init_net=./model_init.pb --input=input.jpg
```

### 4. Python 调用方式(原文)

使用 `detectron2.export.Caffe2Model.__call__` 方法调用,接口与 PyTorch 版模型一致,内部自动应用 pre/post-processing(详见 `../modules/export.html#detectron2.export.Caffe2Model.__call__`)。

### 5. 输入张量规范(原文)

所有转换后的模型接收两个输入张量:`"data"`(NCHW 图像)与 `"im_info"`(N×3,每行为 `(height, width, 1.0)`),且 `"data"` 的 shape 可能因 padding 大于 `"im_info"` 中的尺寸。
