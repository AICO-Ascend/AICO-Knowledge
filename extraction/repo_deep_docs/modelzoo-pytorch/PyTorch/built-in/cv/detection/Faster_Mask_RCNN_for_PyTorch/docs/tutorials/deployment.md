# Deployment

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/cv/detection/Faster_Mask_RCNN_for_PyTorch/docs/tutorials/deployment.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/cv/detection/Faster_Mask_RCNN_for_PyTorch/docs/tutorials/deployment.md

# 一体化深度解读:Caffe2 部署指南

---

## 【定位】

**这篇文档解决什么问题/描述什么能力:**

本文档描述了 detectron2 模型通过 ONNX 转换为 Caffe2 格式的部署能力,涵盖转换覆盖范围(3 种元架构)、转换工具使用(`caffe2_converter.py`)、转换后模型产物(`model.pb` / `model_init.pb`)、C++ 与 Python 两端的推理加载方式(以官方 Mask R-CNN 为示例),以及转换约束(PyTorch ≥ 1.4、ONNX ≥ 1.6、无 GPU 推理优化等)。

---

## 【技术要点】

### 1. 转换路径与版本约束

- **路径**:PyTorch detectron2 模型 → ONNX → Caffe2 格式
- **原文**:Caffe2 conversion requires PyTorch ≥ 1.4 and ONNX ≥ 1.6.

### 2. 三大元架构支持

- 支持的 3 种 meta architectures:`GeneralizedRCNN`、`RetinaNet`、`PanopticFPN`,以及这些架构下的大多数官方模型
- 自定义扩展(通过 registration 添加的)在不含控制流或 Caffe2 不可用算子(如 deformable convolution)时受支持;自定义 backbone 与 head 通常开箱即用

### 3. 转换工具与产物

- 转换脚本:`tools/deploy/caffe2_converter.py`
- 产物:`model.pb`(网络结构) + `model_init.pb`(网络参数)
- 可视化:`model.svg`(同时可用 netron 打开 `model.pb`)
- 评估验证:`--run-eval` 标志位会评估转换后模型精度,与 PyTorch 精度差异 **原文**:typically slightly different (within 0.1 AP) from PyTorch

### 4. 推理输入约束

- 转换后模型接受 2 个输入张量:
  - `data`:NCHW 图像
  - `im_info`:Nx3 张量,由 (height, width, 1.0) 构成;"data" 的实际尺寸可能因 padding 大于 "im_info" 标注尺寸
- **不包含后处理**:转换后模型不含将原始层输出转换为格式化预测的后处理操作(原文举例:Mask R-CNN 仅产出 28×28 的原始 mask,而非最终结果),留给用户在部署时实现自定义轻量级后处理

### 5. C++ 推理示例

- 示例文件:`tools/deploy/caffe2_mask_rcnn.cpp`(使用 `COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x` 做 CPU/GPU 推理)
- 构建依赖:
  - PyTorch 内置 caffe2
  - gflags、glog、opencv
  - 与 caffe2 版本匹配的 protobuf headers
  - caffe2 用 MKL 构建时需要 MKL headers

### 6. Python 包装

- 通过 [`Caffe2Model.__call__`](../modules/export.html#detectron2.export.Caffe2Model.__call__) 方法使用,其接口与 [PyTorch 版 models](./models.md) 一致,内部自动应用 pre/post-processing 以匹配格式

---

## 【关键机制与数据】

### 工作原理

**原文**:The conversion APIs are documented at [the API documentation](../modules/export).We provide a tool, `caffe2_converter.py` as an example that uses these APIs to convert a standard model.

**机制说明**(基于原文):
1. **trace 过程**:转换需要有效权重与样本输入来 trace 模型——这是为什么脚本需要数据集(原文:"The conversion needs valid weights & sample inputs to trace the model. That's why the script requires the dataset.")
2. **样本输入可替换**:可修改脚本以其他方式获取样本输入(原文:"You can modify the script to obtain sample inputs in other ways.")
3. **可视化机制**:`caffe2_converter.py` 生成 `model.svg` 文件,提供网络结构的可视化,也可通过 netron 加载 `model.pb`

### 精度差异数据

**原文**:The accuracy is typically slightly different (within 0.1 AP) from PyTorch due to numerical precisions between different implementations.

### 后处理留白机制

**原文**:The converted models do not contain post-processing operations that transform raw layer outputs into formatted predictions.For example, the command in this tutorial only produces raw outputs (28x28 masks) from the final layers that are not post-processed, because in actual deployment, an application often needs its custom lightweight post-processing, so this step is left for users.

---

## 【表格解读】

**原文无表格**

---

## 【公式解读】

**原文无公式**

---

## 【关联】

### 上下游模块关系(基于内部链接)

| 关联模块 | 关系性质 | 用途说明 |
|---------|---------|---------|
| [`../modules/export`](../modules/export) | 上游(API 定义) | 转换 API 的官方文档;`caffe2_converter.py` 是使用这些 API 的示例 |
| [`../modules/export.html#detectron2.export.Caffe2Model.__call__`](../modules/export.html#detectron2.export.Caffe2Model.__call__) | 上游(API 方法) | Python 端调用转换后模型的入口,接口与 PyTorch 版 models 一致 |
| [`./models.md`](./models.md) | 同级参考 | PyTorch 版模型的接口定义,`Caffe2Model.__call__` 与其保持接口一致 |
| [`builtin_datasets.md`](builtin_datasets.md) | 前置依赖 | 转换前需先准备的 COCO 数据集文档 |
| [`../../MODEL_ZOO.md`](../../MODEL_ZOO.md) | 前置依赖 | 选择要转换的官方模型(如 Mask R-CNN R50 FPN 3x) |
| [`../../tools/deploy/`](../../tools/deploy/) | 同级/同级目录 | 包含转换脚本 `caffe2_converter.py` 与 C++ 示例 `caffe2_mask_rcnn.cpp` |
| [`../../docker/`](../../docker/) | 构建环境 | 官方 detectron2 docker,作为 C++ 示例的推荐编译环境 |

### 流程串联

`builtin_datasets.md`(准备数据)→ `MODEL_ZOO.md`(选择权重)→ `tools/deploy/caffe2_converter.py`(转换)→ 产出 `model.pb` / `model_init.pb` / `model.svg` → `tools/deploy/caffe2_mask_rcnn.cpp`(C++ 推理)或 `Caffe2Model.__call__`(Python 推理) → 应用层自定义 post-processing(留白)

---

## 【使用方法】

### 完整转换命令(原文)

```bash
cd tools/deploy/ && ./caffe2_converter.py --config-file ../../configs/COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml \
	--output ./caffe2_model --run-eval \
	MODEL.WEIGHTS detectron2://COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x/137849600/model_final_f10217.pkl \
	MODEL.DEVICE cpu
```

### C++ 构建命令(原文)

```bash
sudo apt update && sudo apt install libgflags-dev libgoogle-glog-dev libopencv-dev
pip install mkl-include
wget https://github.com/protocolbuffers/protobuf/releases/download/v3.6.1/protobuf-cpp-3.6.1.tar.gz
tar xf protobuf-cpp-3.6.1.tar.gz
export CPATH=$(readlink -f ./protobuf-3.6.1/src/):$HOME/.local/include
export CMAKE_PREFIX_PATH=$HOME/.local/lib/python3.6/site-packages/torch/
mkdir build && cd build
cmake -DTORCH_CUDA_ARCH_LIST=$TORCH_CUDA_ARCH_LIST .. && make
```

### C++ 运行命令(原文)

```bash
./caffe2_mask_rcnn --predict_net=./model.pb --init_net=./model_init.pb --input=input.jpg
```

### 关键配置项(基于原文)

| 配置项 / 标志 | 作用 |
|--------------|------|
| `--config-file` | 指定 detectron2 模型配置文件路径(原文示例指向 `mask_rcnn_R_50_FPN_3x.yaml`) |
| `--output` | 指定转换产物输出目录(原文:`./caffe2_model`) |
| `--run-eval` | 转换后立即评估,验证精度损失是否在可接受范围 |
| `MODEL.WEIGHTS` | 模型权重文件路径(原文使用 `detectron2://` 协议从 model zoo 下载) |
| `MODEL.DEVICE` | 推理设备(原文示例为 `cpu`) |

### 输入张量规格(原文)

| 张量名 | 形状/类型 | 含义 |
|--------|----------|------|
| `data` | NCHW | 输入图像张量 |
| `im_info` | Nx3 | 每张图像的 (height, width, 1.0) 元信息;因 padding 原因,`data` 实际尺寸可能大于 `im_info` 标注值 |

### 性能特性(原文)

| 维度 | 特性 |
|------|------|
| CPU 推理 | 有运行时优化(runtime optimized) |
| Mobile 推理 | 有运行时优化(runtime optimized) |
| GPU 推理 | **未优化** (原文:"but not for GPU inference") |
| 精度损失 | 与 PyTorch 相比 typically within 0.1 AP |
| 后处理 | 转换模型不包含,留给用户实现 |
