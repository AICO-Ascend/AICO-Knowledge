# Deployment

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/CascadedMaskRCNN/docs/tutorials/deployment.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/CascadedMaskRCNN/docs/tutorials/deployment.md

# 一体化深度解读:CascadedMaskRCNN 部署文档

## 【定位】
这篇文档描述如何通过 ONNX 将 detectron2 训练好的模型转换为 Caffe2 格式,并在脱离 detectron2 依赖的环境下完成模型的可移植推理与精度验证流程。

## 【技术要点】

1. **依赖版本门槛**:Caffe2 转换要求 PyTorch ≥ 1.4 且 ONNX ≥ 1.6(原文:"Caffe2 conversion requires PyTorch ≥ 1.4 and ONNX ≥ 1.6")。
2. **支持的元架构**:仅支持三种 — `GeneralizedRCNN`、`RetinaNet`、`PanopticFPN`,以及它们下的大部分官方模型;通过 registration 注册的自定义扩展(自定义 backbone、head 等)只要不含控制流或 Caffe2 不支持算子(如 deformable convolution)即可被支持。
3. **转换依赖**:转换过程必须提供**有效的权重**与**样本输入**以 trace 模型,因此脚本强制要求数据集(可通过修改脚本用其他方式产生样本输入)。
4. **精度损失**:原文给出 — "within 0.1 AP",即转换后模型与 PyTorch 的精度差异通常在 0.1 AP 之内,源于不同实现间的数值精度差异,因此推荐始终使用 `--run-eval` 验证。
5. **部署产物**:目录 `caffe2_model/` 内含 `model.pb`(网络结构)与 `model_init.pb`(网络参数)两个必要文件;附带 `model.svg` 可视化图,可使用 netron 加载 `model.pb`。
6. **C++ 构建依赖**:PyTorch(内置 caffe2)、gflags、glog、opencv、与 caffe2 版本匹配的 protobuf headers;若 caffe2 用 MKL 构建则还需 MKL headers。

## 【关键机制与数据】

- **工作原理(原文)**:通过 ONNX 将 detectron2 模型转换为 Caffe2 格式,转换后的 Caffe2 模型可在 Python 或 C++ 中运行,无需 detectron2 依赖;其运行时针对 CPU 与移动端推理进行了优化,但**未针对 GPU 推理进行优化**。
- **数据流(原文)**:
  - C++ 示例执行 CPU/GPU 推理(`./caffe2_mask_rcnn --predict_net=./model.pb --init_net=./model_init.pb --input=input.jpg`)。
  - 输入张量:`"data"` 为 NCHW 图像;`"im_info"` 为 Nx3 张量,每个元素为 `(height, width, 1.0)`;`"data"` 的形状可能大于 `"im_info"`(因 padding 引起)。
  - 输出:**不含后处理** — 例如 Mask R-CNN 只输出 28x28 的原始 mask,不转换为最终预测格式,留给用户自定义轻量化后处理。
- **Python 封装**:通过 `Caffe2Model.__call__` 方法包装,接口与 PyTorch 版模型完全一致(参见 `./models.md`),内部自动执行 pre/post-processing 以匹配输出格式,可作为 Caffe2 Python API 的参考,也可作为实际部署中 pre/post-processing 的实现范例。

## 【表格解读】

原文无表格。

## 【公式解读】

原文无公式。

## 【关联】

- **`../modules/export`(API 文档)**:转换 API 的官方文档,`caffe2_converter.py` 即基于这些 API 实现。
- **`builtin_datasets.md`**:转换 Mask R-CNN 所需 COCO 数据集的准备说明(`caffe2_converter.py` 需要数据集以生成 trace 用的样本输入)。
- **`../../MODEL_ZOO.md`**:选择预训练权重来源;示例命令中使用 `detectron2://COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x/137849600/model_final_f10217.pkl`。
- **`../../tools/deploy/`**:`caffe2_converter.py`(转换脚本)与 `caffe2_mask_rcnn.cpp`(C++ 推理示例)所在目录。
- **`../../docker/`**:官方 detectron2 docker 镜像;C++ 示例的编译命令均在此镜像中运行。
- **`../modules/export.html#detectron2.export.Caffe2Model.__call__`**:Python 包装入口,提供与 PyTorch 模型一致的调用接口,内部自动处理 pre/post-processing。
- **`./models.md`**:PyTorch 版模型接口;`Caffe2Model.__call__` 故意对齐该接口,方便迁移。

## 【使用方法】

**原文命令 1 — 模型转换**(示例为 Mask R-CNN on COCO):
```
cd tools/deploy/ && ./caffe2_converter.py --config-file ../../configs/COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml \
	--output ./caffe2_model --run-eval \
	MODEL.WEIGHTS detectron2://COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x/137849600/model_final_f10217.pkl \
	MODEL.DEVICE cpu
```
关键参数:`--config-file`(模型配置)、`--output`(输出目录)、`--run-eval`(转换后评估精度)、`MODEL.WEIGHTS`(权重)、`MODEL.DEVICE cpu`(运行设备)。

**原文命令 2 — C++ 示例编译**(在官方 detectron2 docker 内):
```
sudo apt update && sudo apt install libgflags-dev libgoogle-glog-dev libopencv-dev
pip install mkl-include
wget https://github.com/protocolbuffers/protobuf/releases/download/v3.6.1/protobuf-cpp-3.6.1.tar.gz
tar xf protobuf-cpp-3.6.1.tar.gz
export CPATH=$(readlink -f ./protobuf-3.6.1/src/):$HOME/.local/include
export CMAKE_PREFIX_PATH=$HOME/.local/lib/python3.6/site-packages/torch/
mkdir build && cd build
cmake -DTORCH_CUDA_ARCH_LIST=$TORCH_CUDA_ARCH_LIST .. && make

# To run:
./caffe2_mask_rcnn --predict_net=./model.pb --init_net=./model_init.pb --input=input.jpg
```
关键参数:`--predict_net`(网络结构文件)、`--init_net`(初始化权重文件)、`--input`(待推理图像);`TORCH_CUDA_ARCH_LIST` 沿用 docker 内环境变量。

**Python 调用方式**:通过 `Caffe2Model.__call__` 方法加载并推理;接口与 PyTorch 版模型一致,详见 `../modules/export.html#detectron2.export.Caffe2Model.__call__`。
