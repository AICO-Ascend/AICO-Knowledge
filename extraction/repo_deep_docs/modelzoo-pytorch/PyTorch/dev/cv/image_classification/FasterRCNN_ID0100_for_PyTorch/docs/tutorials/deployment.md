# Deployment

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/dev/cv/image_classification/FasterRCNN_ID0100_for_PyTorch/docs/tutorials/deployment.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/dev/cv/image_classification/FasterRCNN_ID0100_for_PyTorch/docs/tutorials/deployment.md

# 深度解读:FasterRCNN_ID0100_for_PyTorch — Deployment Guide

---

## 【定位】

本文档系统描述了如何将 detectron2 训练的 PyTorch 模型通过 ONNX 转换为 Caffe2 格式,从而脱离 detectron2 依赖,在 CPU/移动端(非 GPU 优化)做 Python 或 C++ 推理的完整端到端流程——含 API、命令行转换脚本、C++ 构建运行、输入输出约定,以及不带后处理的"原始层输出"语义说明。

---

## 【技术要点】

1. **转换路径**:detectron2 → ONNX → Caffe2,转换后的模型可独立运行,**不依赖 detectron2**;运行时针对 **CPU 与移动端做了优化,未对 GPU 做优化**。
2. **版本基线**:Caffe2 转换要求 **PyTorch ≥ 1.4** 且 **ONNX ≥ 1.6**(原文明确数字)。
3. **覆盖范围**:支持 3 种 meta 架构 —— `GeneralizedRCNN`、`RetinaNet`、`PanopticFPN`,及其下大多数官方模型;通过注册机制加入的自定义扩展(自定义 backbone/head)通常"开箱即用",但**不可包含控制流或 Caffe2 中不可用的算子**(原文示例:deformable convolution)。
4. **转换触发条件**:转换需要 **有效权重 + 样本输入(sample inputs)** 来 trace 模型,所以脚本要求传入数据集;可通过修改脚本换其他来源的样本输入。
5. **精度核验**:使用 `--run-eval` 标志会评估转换后模型精度,与 PyTorch 的偏差通常 **"within 0.1 AP"**(原文数字),由不同实现的数值精度差异引起;**建议始终做精度核验**以防转换失败。
6. **输入约定与"无后处理"语义**:所有转换后 `.pb` 模型接受两个输入张量——`data`(NCHW 图像)与 `im_info`(Nx3 张量,每行 `(height, width, 1.0)`,`data` 形状可能因 padding 大于 `im_info`);**转换后模型不含**把原始层输出格式化为最终预测的后处理(例如教程命令仅输出 28×28 mask 的原始层输出,后处理交由应用方实现)。

---

## 【关键机制与数据】

- **工作原理(数据流)**:`caffe2_converter.py` 读取 YAML 配置 + 权重,加载数据集以获取样本输入 → 经 `export` API 走 ONNX trace → 落地为 `caffe2_model/` 目录下的两张 protobuf:
  - `model.pb`:网络结构(predict_net)
  - `model_init.pb`:网络参数(init_net)
  原文:"Two files `model.pb` and `model_init.pb` that contain network structure and network parameters are necessary for deployment."
- **可视化产物**:脚本会生成 `model.svg`(网络结构可视化),`model.pb` 也可用 netron 进一步可视化(原文给出 netron 的 GitHub 链接)。
- **C++ 部署依赖(原文)**:PyTorch(内含 caffe2)、gflags、glog、opencv、与 caffe2 版本匹配的 protobuf headers;若 caffe2 用 MKL 构建则需 MKL headers。
- **Python 端包装**:`Caffe2Model.__call__` 方法内部应用 pre/post-processing,**接口与 PyTorch 版 `./models.md` 完全一致**——既可作为 caffe2 Python API 使用参考,也可作为"如何在部署中实现 pre/post-processing"的范例。
- **性能/精度数据(原文)**:**仅**给出 AP 偏差阈值"within 0.1 AP";**未给出**吞吐、延迟等数值。

---

## 【表格解读】

**原文无表格。** 全文仅以叙述 + 命令块形式给出配置项(如 `MODEL.WEIGHTS`、`MODEL.DEVICE`、`--run-eval`、`--config-file`、`--output`)与输入张量语义,未以表格列出参数或性能对比。

---

## 【公式解读】

**原文无公式。** 全文不包含任何 LaTeX 或伪代码形式的数学公式;仅有形如 `(height, width, 1.0)` 的张量形状描述与 "28x28 masks" 这类尺寸说明,均以自然语言给出。

---

## 【关联】

按文中锚定的内部链接梳理依赖与上下游:

| 内部链接 | 关系定位 |
|---|---|
| `../modules/export` | **上游/核心 API**:转换 API 的官方文档,`caffe2_converter.py` 即基于此实现。 |
| `builtin_datasets.md` | **前置条件**:转换需要样本输入,因此需先按此文档准备 COCO 数据集。 |
| `../../MODEL_ZOO.md` | **权重来源**:从 Model Zoo 中挑选预训练权重(示例取 `mask_rcnn_R_50_FPN_3x/137849600/model_final_f10217.pkl`)。 |
| `../../tools/deploy/` | **下游/部署示例**:C++ 推理示例 `caffe2_mask_rcnn.cpp` 的存放路径(本文使用 `caffe2_mask_rcnn` 进行 CPU/GPU 推理)。 |
| `../../docker/` | **构建环境**:官方 detectron2 docker 镜像,C++ 示例在该镜像内编译构建。 |
| `../modules/export.html#detectron2.export.Caffe2Model.__call__` | **下游/Python 接口**:`Caffe2Model.__call__` 包装,提供与 PyTorch 版一致的调用语义。 |
| `./models.md` | **对等参考**:Python 端 `Caffe2Model.__call__` 与此处 PyTorch 版模型接口"identical",用于行为对照。 |

整体链路:**MODEL_ZOO(权重) + builtin_datasets(样本输入) → export API / caffe2_converter.py(转换) → model.pb & model_init.pb(产物) → C++ 示例 tools/deploy 或 Python Caffe2Model.__call__(消费方)**,docker 提供构建宿主。

---

## 【使用方法】

### 1. Python 端转换(Mask R-CNN on COCO 示例)
```
cd tools/deploy/ && ./caffe2_converter.py --config-file ../../configs/COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml \
    --output ./caffe2_model --run-eval \
    MODEL.WEIGHTS detectron2://COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x/137849600/model_final_f10217.pkl \
    MODEL.DEVICE cpu
```
- 关键开关:`--run-eval`(核验精度)、`MODEL.DEVICE cpu`(转换设备)、`MODEL.WEIGHTS detectron2://...`(权重 URL,支持 detectron2 协议下载)。

### 2. C++ 端构建(在官方 detectron2 docker 内)
```
sudo apt update && sudo apt install libgflags-dev libgoogle-glog-dev libopencv-dev
pip install mkl-include
wget https://github.com/protocolbuffers/protobuf/releases/download/v3.6.1/protobuf-cpp-3.6.1.tar.gz
tar xf protobuf-cpp-3.6.1.tar.gz
export CPATH=$(readlink -f ./protobuf-3.6.1/src/):$HOME/.local/include
export CMAKE_PREFIX_PATH=$HOME/.local/lib/python3.6/site-packages/torch/
mkdir build && cd build
cmake -DTORCH_CUDA_ARCH_LIST=$TORCH_CUDA_ARCH_LIST .. && make
```
**原文指定的 protobuf 版本为 v3.6.1**。

### 3. C++ 端推理
```
./caffe2_mask_rcnn --predict_net=./model.pb --init_net=./model_init.pb --input=input.jpg
```
- 必传项:`--predict_net`(网络结构)、`--init_net`(参数)、`--input`(输入图像)。

### 4. 输入张量规范(运行时契约)
- `data`:NCHW 图像张量。
- `im_info`:Nx3 张量,每行为 `(height, width, 1.0)`;因 padding,`data` 的形状可大于 `im_info`。

### 6. 精度核验流程
使用 `--run-eval` 让脚本自动比对 PyTorch 与转换后 Caffe2 模型的 AP,偏差容忍度 "within 0.1 AP";**超出该范围视为转换可能未成功**(原文建议:always verify the accuracy)。
