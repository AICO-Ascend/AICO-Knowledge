# Deployment

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/RetinaNet/docs/tutorials/deployment.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/RetinaNet/docs/tutorials/deployment.md

# 一体化深度解读:PyTorch/contrib/cv/detection/RetinaNet/docs/tutorials/deployment.md

---

## 【定位】
本文档描述 detectron2 模型通过 ONNX 转换为 Caffe2 格式的部署流程,使转换后的模型可在脱离 detectron2 依赖的 Python 或 C++ 环境中运行,适用于 CPU 与移动端推理场景。

---

## 【技术要点】

1. **转换路径**:基于 ONNX 中转,将 detectron2 模型转换为 Caffe2 格式;转换要求 **PyTorch ≥ 1.4 且 ONNX ≥ 1.6**。
2. **支持的元架构(meta architectures)**:共 3 种——`GeneralizedRCNN`、`RetinaNet`、`PanopticFPN`,涵盖大部分官方模型;通过注册机制添加的自定义扩展(如 backbone、head)只要不含控制流或 Caffe2 不支持的算子(如可变形卷积),也能直接支持。
3. **转换工具**:`tools/deploy/caffe2_converter.py`,需要有效的权重与样本输入用于 trace,因此必须先准备数据集(如 COCO)。
4. **输出产物**:`caffe2_model/` 目录下两个 `.pb` 文件——`model.pb`(网络结构)与 `model_init.pb`(网络参数);另外生成 `model.svg` 用于可视化。
5. **输入张量约定**:转换后模型接受两个输入——`data`(NCHW 图像)与 `im_info`(N×3 张量,每行为 (height, width, 1.0));`data` 实际尺寸可能因 padding 而大于 `im_info` 所描述的尺寸。
6. **后处理策略**:转换后的模型不包含将原始网络输出转为格式化预测的后处理操作,留给用户在部署侧自行实现轻量化的定制逻辑。

---

## 【关键机制与数据】

- **推理优化目标**:Caffe2 运行时针对 **CPU 与 mobile 推理做了优化,GPU 推理并未优化**(原文:"It has a runtime optimized for CPU & mobile inference, but not for GPU inference.")。
- **精度差异**:通过 `--run-eval` 校验时,转换后的 Caffe2 模型与 PyTorch 模型的精度差异通常在 **0.1 AP 以内**(原文:"within 0.1 AP")。
- **数据流**:PyTorch detectron2 模型 → trace(需数据集提供样本输入)→ ONNX → Caffe2 `.pb` 文件 → 由 Caffe2 Python/C++ API 加载;Python 侧通过 `Caffe2Model.__call__` 封装,自动应用 pre/post-processing 以匹配 PyTorch 版 models 的接口。
- **不支持的内容**:包含控制流或 Caffe2 不可用算子(原文举例:可变形卷积 deformable convolution)的自定义模块无法直接转换。
- **C++ 构建依赖**(原文):PyTorch 内嵌 caffe2、gflags、glog、opencv、与 caffe2 版本匹配的 protobuf headers;若 caffe2 用 MKL 构建则需 MKL headers。
- **可执行命令**(原文):`./caffe2_mask_rcnn --predict_net=./model.pb --init_net=./model_init.pb --input=input.jpg`。

---

## 【表格解读】
**原文无表格。** 该文档以命令、列表、说明文字为主,未包含参数表、性能对比表或配置项表格。

---

## 【公式解读】
**原文无公式。** 全文未出现 LaTeX 或伪代码形式的数学公式。

---

## 【关联】

本文档是 detectron2 模型 **部署(Tutorial)** 链路的一环,与以下模块/特性紧密耦合:

| 关联模块 | 关系说明 |
|---|---|
| `../modules/export` | 转换 API 的权威文档,本文档中的 `caffe2_converter.py` 即基于这些 API 实现 |
| `builtin_datasets.md` | 转换前必须先按此文档准备数据集(如 COCO)以提供 trace 所需的样本输入 |
| `../../MODEL_ZOO.md` | 提供可选的预训练权重来源(原文示例:Mask R-CNN R50-FPN 3x) |
| `../../tools/deploy/` | 包含 C++ 示例 `caffe2_mask_rcnn.cpp` 与转换脚本 `caffe2_converter.py` |
| `../../docker/` | C++ 示例推荐在官方 detectron2 docker 内构建,以避免环境差异 |
| `../modules/export.html#detectron2.export.Caffe2Model.__call__` | Python 侧加载转换后模型的封装方法,接口与 PyTorch 版 models 一致 |
| `./models.md` | `Caffe2Model.__call__` 的接口对标对象,二者接口保持一致以便用户复用 |

---

## 【使用方法】

### 1. Python 侧转换(原文命令)

```bash
cd tools/deploy/ && ./caffe2_converter.py \
    --config-file ../../configs/COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml \
    --output ./caffe2_model \
    --run-eval \
    MODEL.WEIGHTS detectron2://COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x/137849600/model_final_f10217.pkl \
    MODEL.DEVICE cpu
```

**关键参数**:
- `--config-file`:detectron2 配置文件路径
- `--output`:转换产物输出目录
- `--run-eval`:启用后会在转换后立即评估精度(误差应 ≤ 0.1 AP)
- `MODEL.WEIGHTS`:权重来源,可为 detectron2:// 协议 URL 或本地路径
- `MODEL.DEVICE`:trace 时使用的设备(示例为 `cpu`)

### 2. C++ 侧构建(原文命令,在官方 docker 内执行)

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

### 3. C++ 侧推理(原文命令)

```bash
./caffe2_mask_rcnn --predict_net=./model.pb --init_net=./model_init.pb --input=input.jpg
```

### 4. Python 侧推理(原文描述)
通过 `Caffe2Model.__call__` 调用,接口与 PyTorch 版 models 一致,内部自动完成 pre/post-processing,无需用户手动实现;若需自定义后处理,需参考此封装自行在原始网络输出(例如 28×28 masks)上扩展。
