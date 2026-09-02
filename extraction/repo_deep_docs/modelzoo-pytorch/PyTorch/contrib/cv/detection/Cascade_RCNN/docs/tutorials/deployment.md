# Deployment

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/Cascade_RCNN/docs/tutorials/deployment.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/Cascade_RCNN/docs/tutorials/deployment.md

# 深度解读:Cascade_RCNN 部署指南(deployment.md)

## 【定位】

本文档解决 detectron2 框架下将训练好的 PyTorch 检测模型(以 Cascade R-CNN 体系为代表)转换为 Caffe2 格式并完成跨语言(C++/Python)离线部署的问题,描述其支持范围、转换工具、精度验证以及 C++/Python 端推理接口使用方式。

## 【技术要点】

1. **转换路径**:通过 ONNX 中转,将 detectron2 模型转换为 Caffe2 格式,转换产物可脱离 detectron2 依赖,在 Python 或 C++ 中独立运行。
2. **硬件适配**:Caffe2 运行时针对 **CPU 与移动端推理**做了优化,**未针对 GPU 推理**做优化。
3. **版本依赖**:`PyTorch ≥ 1.4` 且 `ONNX ≥ 1.6`。
4. **覆盖范围**:支持三类元架构 `GeneralizedRCNN`、`RetinaNet`、`PanopticFPN` 及其下的官方模型;通过注册机制加入的自定义扩展(无控制流、不含 Caffe2 不支持算子,如可变形卷积)也可一并转换。
5. **转换工具**:提供 `tools/deploy/caffe2_converter.py` 脚本,通过 `--config-file` 指定配置、`--output` 指定输出目录、`--run-eval` 触发精度校验,转换时必须提供有效权重与样本输入用于 trace。
6. **输入约定**:转换后的模型接收两个输入张量——`data`(NCHW 图像)与 `im_info`(N×3 张量,每行为 `(height, width, 1.0)`,`data` 可能因 padding 大于 `im_info` 的形状)。
7. **Python 调用接口**:`Caffe2Model.__call__` 方法接口与 PyTorch 版模型保持一致,内部自动完成 pre/post-processing,使输出格式与 PyTorch 模型对齐。

## 【关键机制与数据】

- **转换-评估闭环**:`--run-eval` 标志会让脚本同时运行转换后模型的推理评估,验证转换是否成功。原文给出量化精度指标:**转换后精度与 PyTorch 版本的差异通常在 0.1 AP 以内**(因不同实现间的数值精度差异)。
- **产物构成**:转换结果落到 `--output` 指定的 `caffe2_model/` 目录下,**两个关键文件**——`model.pb`(网络结构)与 `model_init.pb`(网络参数)是部署所必需;同时生成 `model.svg` 网络结构可视化。
- **后处理剥离机制**:转换出的 `.pb` 模型**不包含**将原始网络输出转换为格式化预测的后处理步骤;以示例 Mask R-CNN 为例,最终层只输出原始 28×28 masks 而不进行格式化——留给用户在部署应用侧自行实现轻量后处理。
- **C++ 构建依赖清单**:PyTorch(内置 caffe2)、`gflags`、`glog`、`opencv`、与 caffe2 版本匹配的 `protobuf` 头文件、若 caffe2 启用 MKL 则需 `MKL` 头文件。
- **Docker 内具体编译步骤**(原文):使用 `libgflags-dev`、`libgoogle-glog-dev`、`libopencv-dev`、`mkl-include`,下载 `protobuf-cpp-3.6.1.tar.gz`,设置 `CPATH` 与 `CMAKE_PREFIX_PATH` 指向 `torch/` 安装目录,以 cmake/make 编译,并通过 `./caffe2_mask_rcnn --predict_net=./model.pb --init_net=./model_init.pb --input=input.jpg` 执行推理。
- **不支持特性**(原文):包含控制流或 Caffe2 中不可用算子(如可变形卷积 `deformable convolution`)的自定义扩展无法转换。

## 【表格解读】

原文无表格。

## 【公式解读】

原文无公式。

## 【关联】

文档通过以下内部链接与上下游模块/工具形成完整部署链路:

- **API 文档层**:`../modules/export` 与 `../modules/export.html#detectron2.export.Caffe2Model.__call__` —— 定义转换 API 与 `Caffe2Model.__call__` Python 包装方法;后者为部署侧提供与 PyTorch 版模型同构的调用接口,是 pre/post-processing 在 Caffe2 端对齐的关键入口。
- **数据准备层**:`builtin_datasets.md` —— 转换脚本需要样本输入用于 trace,因此依赖数据集准备流程(示例中需准备 COCO 数据集)。
- **模型来源层**:`../../MODEL_ZOO.md` —— 提供预训练权重(示例命令通过 `detectron2://COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x/137849600/model_final_f10217.pkl` 拉取官方 Mask R-CNN 权重)。
- **部署工具与示例层**:`../../tools/deploy/` —— 包含转换脚本 `caffe2_converter.py` 与 C++ 推理示例 `caffe2_mask_rcnn.cpp`。
- **运行环境层**:`../../docker/` —— 提供官方 detectron2 Docker 镜像,作为编译 C++ 示例的推荐环境(原型为 cmake/make 编译 + CPU/GPU 推理)。
- **同目录姊妹文档**:`./models.md` —— 描述 PyTorch 版原生模型的定义方式,作为 `Caffe2Model.__call__` 接口对齐的对照参考。

整体关系链为:**MODEL_ZOO(权重) → builtin_datasets(样本输入) → caffe2_converter.py + export API(转换) → caffe2_mask_rcnn.cpp / Caffe2Model.__call__(C++/Python 端推理)**。

## 【使用方法】

原文涉及的具体启用方式与命令如下:

**1. 环境前置条件(原文):**
```
PyTorch ≥ 1.4
ONNX ≥ 1.6
```

**2. 以 COCO Mask R-CNN 为例执行转换(原文命令):**
```
cd tools/deploy/ && ./caffe2_converter.py --config-file ../../configs/COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml \
	--output ./caffe2_model --run-eval \
	MODEL.WEIGHTS detectron2://COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x/137849600/model_final_f10217.pkl \
	MODEL.DEVICE cpu
```

关键配置项:
- `--config-file`:模型对应的 detectron2 YAML 配置。
- `--output`:转换产物输出目录(生成 `model.pb` / `model_init.pb` / `model.svg`)。
- `--run-eval`:启用精度验证(输出与 PyTorch 相比应在 0.1 AP 以内)。
- `MODEL.WEIGHTS`:权重文件路径或 `detectron2://` URI。
- `MODEL.DEVICE`:转换所用的设备(示例为 `cpu`)。

**3. 在官方 Docker 中编译并运行 C++ 示例(原文):**
```
sudo apt update && sudo apt install libgflags-dev libgoogle-glog-dev libopencv-dev
pip install mkl-include
wget https://github.com/protocolbuffers/protobuf/releases/download/v3.6.1/protobuf-cpp-3.6.1.tar.gz
tar xf protobuf-cpp-3.6.1.tar.gz
export CPATH=$(readlink -f ./protobuf-3.6.1/src/):$HOME/.local/include
export CMAKE_PREFIX_PATH=$HOME/.local/lib/python3.6/site-packages/torch/
mkdir build && cd build
cmake -DTORCH_CUDA_ARCH_LIST=$TORCH_CUDA_ARCH_LIST .. && make

# 运行:
./caffe2_mask_rcnn --predict_net=./model.pb --init_net=./model_init.pb --input=input.jpg
```

C++ 推理命令参数:
- `--predict_net`:网络结构文件(`model.pb`)。
- `--init_net`:网络参数文件(`model_init.pb`)。
- `--input`:待推理图像路径。

**4. Python 端调用方式(原文):**
通过 `Caffe2Model.__call__` 方法调用转换后的模型,接口与 PyTorch 版模型一致,内部自动完成 pre/post-processing,使输出格式与 PyTorch 模型对齐——可作为 Caffe2 Python API 的参考实现。

**5. 输入张量约定(原文):**
- `data`:NCHW 图像张量。
- `im_info`:N×3 张量,每行为 `(height, width, 1.0)`;`data` 可能因 padding 而大于 `im_info` 对应形状。
