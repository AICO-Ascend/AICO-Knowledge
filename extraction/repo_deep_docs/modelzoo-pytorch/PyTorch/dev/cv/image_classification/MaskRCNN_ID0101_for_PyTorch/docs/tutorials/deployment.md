# Deployment

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/dev/cv/image_classification/MaskRCNN_ID0101_for_PyTorch/docs/tutorials/deployment.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/dev/cv/image_classification/MaskRCNN_ID0101_for_PyTorch/docs/tutorials/deployment.md

# 深度解读：detectron2 Caffe2 部署指南

---

## 【定位】

这篇文档描述了如何将 detectron2 训练的 PyTorch 模型（以 COCO 上的 Mask R-CNN 为例）通过 ONNX 转换为 Caffe2 格式，使其脱离 detectron2 依赖、在 CPU/移动端以 C++ 或 Python 方式独立运行的能力。

---

## 【技术要点】

1. **转换路径与依赖**：通过 ONNX 作为中间格式完成 PyTorch → Caffe2 的转换，要求 **PyTorch ≥ 1.4** 且 **ONNX ≥ 1.6**。
2. **支持的元架构**：明确支持三种最常见的 meta architectures——`GeneralizedRCNN`、`RetinaNet`、`PanopticFPN`，以及它们下属的大多数官方模型。
3. **自定义扩展支持**：通过 registration 注册的自定义扩展（如 custom backbones / heads）只要不包含控制流或 Caffe2 不支持的算子（典型反例：deformable convolution），即可开箱即用。
4. **转换 + 评估工具链**：`tools/deploy/caffe2_converter.py` 同时完成模型转换（输出 `model.pb` + `model_init.pb` 与可视化 `model.svg`）与精度校验（通过 `--run-eval` 触发），典型精度损失为 PyTorch 的 **0.1 AP 以内**。
5. **C++ 推理依赖**：构建示例 `caffe2_mask_rcnn.cpp` 需要 PyTorch 内置 caffe2、`gflags`、`glog`、`opencv`、`protobuf headers`（需与 caffe2 版本匹配）；若 caffe2 启用 MKL，还需 `MKL headers`。
6. **模型接口契约**：转换后的模型接收两个输入张量——`"data"`（NCHW 图像）与 `"im_info"`（Nx3 张量，每行为 `(height, width, 1.0)`），并**不包含**将原始输出转换为最终预测的后处理逻辑，应用方需自行实现。

---

## 【关键机制与数据】

### 工作原理（原文梳理）

- **转换链路**：PyTorch 模型 → ONNX → Caffe2 模型。转换需要**有效权重**与**样本输入**用于 trace 模型，这也是脚本强制要求数据集的原因。
- **输出三件套**：
  - `model.pb`：网络结构（predict_net）
  - `model_init.pb`：网络参数（init_net）
  - `model.svg`：网络可视化图（也可用 netron 加载 `model.pb` 查看）
- **运行机制**：Caffe2 运行时针对 **CPU & mobile 推理优化**，而非 GPU 推理。模型可被独立加载到 C++ 或 Python 进程中，**不再依赖 detectron2**。
- **数据流（输入）**：`"data"` 为 NCHW 图像张量，其形状可能因 padding 大于 `"im_info"` 中声明的真实高宽；`"im_info"` 携带每张图的高度、宽度与常数 `1.0`。
- **数据流（输出）**：原文示例指出仅产出 28×28 的 raw masks，**不包含**将 raw 输出格式化为最终预测的后处理——这是有意为之，因为部署时应用常需自定义轻量后处理。

### 性能数据

- 原文：**"The accuracy is typically slightly different (within 0.1 AP) from PyTorch due to numerical precisions between different implementations."**
  - 即转换后精度与 PyTorch 实现的差距通常在 **0.1 AP** 以内，差异来源于不同实现的数值精度。
- 原文强调：**"It's recommended to always verify the accuracy in case the conversion is not successful."** —— 建议始终通过 `--run-eval` 验证。

---

## 【表格解读】

**原文无表格**。原文以命令、配置项和列表形式描述部署流程，未提供参数表或性能对比表。

---

## 【公式解读】

**原文无公式**。文档以命令行、配置项与接口契约为主，未出现任何数学公式或伪代码。

---

## 【关联】

文档通过内嵌链接构建了完整的部署工作流生态：

| 链接 | 角色与上下游关系 |
|---|---|
| [`../modules/export`](../modules/export) | **转换 API 上游**：提供 `Caffe2Model`、`caffe2_converter.py` 调用的底层 ONNX → Caffe2 转换接口 |
| [`builtin_datasets.md`](builtin_datasets.md) | **数据准备前置**：转换脚本需要数据集以提供 trace 用的样本输入，必须先完成 COCO 数据集配置 |
| [`../../MODEL_ZOO.md`](../../MODEL_ZOO.md) | **模型选择入口**：从中挑选待转换的预训练权重（如示例中的 `mask_rcnn_R_50_FPN_3x`） |
| [`../../tools/deploy/`](../../tools/deploy/) | **C++ 推理实现下游**：存放 `caffe2_converter.py`（转换脚本）与 `caffe2_mask_rcnn.cpp`（C++ 推理示例），构成 Python→C++ 的桥梁 |
| [`../../docker/`](../../docker/) | **构建环境容器**：C++ 示例推荐在官方 detectron2 docker 内编译，规避依赖版本不一致 |
| [`../modules/export.html#detectron2.export.Caffe22Model.__call__`](../modules/export.html#detectron2.export.Caffe2Model.__call__) | **Python 部署入口**：提供与 PyTorch 模型**接口一致**的 Python 包装方法，自动注入 pre/post-processing，可作为 C++ 端自行实现后处理的参考 |
| [`./models.md`](./models.md) | **接口对齐对象**：`Caffe2Model.__call__` 的接口被设计成与 PyTorch 版本模型完全相同，便于迁移 |

**关联闭环**：数据准备（builtin_datasets）→ 模型选择（MODEL_ZOO）→ 转换 API（export）→ 转换脚本（tools/deploy/caffe2_converter.py）→ 产物（`model.pb` / `model_init.pb`）→ C++ 部署（tools/deploy + docker）或 Python 部署（Caffe2Model.__call__）→ 与原始 PyTorch 模型接口保持一致（models.md）。

---

## 【使用方法】

### 一、模型转换（Python 端）

进入转换脚本目录后，使用以下命令将 COCO 上训练好的官方 Mask R-CNN 转换为 Caffe2 模型：

```bash
cd tools/deploy/ && ./caffe2_converter.py --config-file ../../configs/COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml \
    --output ./caffe2_model --run-eval \
    MODEL.WEIGHTS detectron2://COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x/137849600/model_final_f10217.pkl \
    MODEL.DEVICE cpu
```

**关键配置项**：
- `--config-file`：指定模型配置文件（`mask_rcnn_R_50_FPN_3x.yaml`）。
- `--output`：转换产物输出目录（`./caffe2_model`）。
- `--run-eval`：转换后立即评估精度，推荐始终开启。
- `MODEL.WEIGHTS`：权重来源，使用 `detectron2://` 协议从 Model Zoo 自动下载。
- `MODEL.DEVICE cpu`：在 CPU 上 trace 模型。

**注意**：可修改脚本以其他方式获取样本输入，因为 trace 仅需"有效权重 + 样本输入"。

### 二、C++ 部署构建（推荐在官方 docker 内执行）

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

**构建依赖清单**：
1. PyTorch with caffe2 inside
2. `gflags`、`glog`、`opencv`（通过 apt 安装）
3. `protobuf headers`，版本需与 caffe2 匹配（示例下载 `protobuf-cpp-3.6.1`）
4. `MKL headers`（当 caffe2 启用 MKL 时必需）

### 三、C++ 推理运行

```bash
./caffe2_mask_rcnn --predict_net=./model.pb --init_net=./model_init.pb --input=input.jpg
```

- `--predict_net`：网络结构文件路径（对应 `model.pb`）。
- `--init_net`：网络参数文件路径（对应 `model_init.pb`）。
- `--input`：待推理的图像文件。

### 四、Python 端调用

通过 `Caffe2Model.__call__` 方法直接调用，接口与 PyTorch 版 detectron2 模型一致，内部自动完成 pre/post-processing，可作为 C++ 端实现自定义后处理的参考模板。
