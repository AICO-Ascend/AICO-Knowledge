# Tutorial 9: ONNX to TensorRT (Experimental)

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/FSAF_for_Pytorch/mmdetection/docs/tutorials/onnx2tensorrt.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/FSAF_for_Pytorch/mmdetection/docs/tutorials/onnx2tensorrt.md

# 一体化深度解读: ONNX to TensorRT (Experimental) 教程

## 【定位】
这篇文档描述了 mmdetection 中将 ONNX 模型转换为 TensorRT 引擎的实验性能力, 是 PyTorch → ONNX → TensorRT 部署流程中的第二个环节 (承接 `pytorch2onnx` 工具的输出), 解决在 NVIDIA GPU 上加速推理的工程问题。

## 【技术要点】

1. **三步前置依赖链**: 需先按 `get_started.md` 从源码安装 MMCV 和 MMDetection; 再按 `ONNXRuntime in mmcv` 和 `TensorRT plugin in mmcv` 安装带 ONNXRuntime 自定义算子与 TensorRT 插件的 `mmcv-full`; 最后用 `pytorch2onnx` 工具完成 PyTorch 到 ONNX 的转换。三步顺序不可颠倒。

2. **核心转换入口**: 通过 `tools/deployment/onnx2tensorrt.py` 脚本执行 ONNX → TensorRT 转换, 需指定 ONNX 模型路径 (`${MODEL}`) 与输出 TensorRT 引擎路径 (`--trt-file`), 同时提供输入图片用于 tracing 与转换。

3. **关键参数默认值 (原文给出)**: 
   - `--shape` 默认 `400 600` (模型输入的 H × W)
   - `--mean` 默认 `123.675 116.28 103.53`
   - `--std` 默认 `58.395 57.12 57.375`
   - `--workspace-size` 默认 `1` GiB (构建 TensorRT 引擎所需 GPU workspace)
   - `--input-img` 默认 `demo/demo.jpg`
   - `--trt-file` 默认 `tmp.trt`
   - `--dataset` 默认 `coco`
   - `--show` / `--verify` 默认 `False`
   - `--to-rgb` 默认 `True`

4. **验证机制**: `--verify` 参数开启后会比对 ONNXRuntime 与 TensorRT 之间的模型输出正确性, `--show` 则可视化模型输出。

5. **官方已验证的测试环境**: Pytorch==1.6.0 + TensorRT-7.2.1.6.Ubuntu-16.04.x86_64-gnu.cuda-10.2.cudnn8.0。

## 【关键机制与数据】

**工作原理/数据流 (原文未给出详细内部流程描述, 以下基于原文命令推断标注)**:

- **数据流**: 转换管线为 PyTorch 模型 → (`pytorch2onnx`) → ONNX 文件 → (`onnx2tensorrt.py`) → TensorRT 引擎文件 (`.trt`)。
- **图片预处理**: 转换时需提供单张输入图片 (`--input-img`), TensorRT 构建过程中会以此图片为样本执行 tracing 并确定输入 shape; 同时图片按 `--mean` / `--std` / `--to-rgb` 进行归一化与通道顺序转换, 归一化参数与 `--shape` 共同决定 ONNX 图静态输入张量。
- **引擎构建**: TensorRT 在 GPU 上构建引擎时占用 `--workspace-size` 指定的显存作为构建期工作空间, 默认 1 GiB。
- **正确性比对 (--verify)**: 同一张输入图片分别跑 ONNXRuntime 与 TensorRT 推理, 比对输出, 但原文未给出容差阈值或具体比对实现。

**性能数据**: 原文未给出 FPS、吞吐量、加速比等任何性能数字。

## 【表格解读】

**表: List of supported models convertable to TensorRT**

|    Model    |                        Config                        | Status |
| :---------: | :--------------------------------------------------: | :----: |
|     SSD     |             `configs/ssd/ssd300_coco.py`             |   Y    |
|    FSAF     |        `configs/fsaf/fsaf_r50_fpn_1x_coco.py`        |   Y    |
|    FCOS     |   `configs/fcos/fcos_r50_caffe_fpn_4x4_1x_coco.py`   |   Y    |
|   YOLOv3    |  `configs/yolo/yolov3_d53_mstrain-608_273e_coco.py`  |   Y    |
|  RetinaNet  |   `configs/retinanet/retinanet_r50_fpn_1x_coco.py`   |   Y    |
| Faster-RCNN | `configs/faster_rcnn/faster_rcnn_r50_fpn_1x_coco.py` |   Y    |

逐行解读:
- **SSD** (`configs/ssd/ssd300_coco.py`): 单阶段检测器, 配置对应 SSD300 基础版, 支持转换 (Y)。
- **FSAF** (`configs/fsaf/fsaf_r50_fpn_1x_coco.py`): Feature Selective Anchor-Free 模块, 与本仓库路径同名, 支持转换 (Y)。
- **FCOS** (`configs/fcos/fcos_r50_caffe_fpn_4x4_1x_coco.py`): Anchor-Free 检测器 FCOS, caffe 风格预训练, 支持转换 (Y)。
- **YOLOv3** (`configs/yolo/yolov3_d53_mstrain-608_273e_coco.py`): DarkNet-53 骨干的多尺度训练 YOLOv3, 输入尺寸 608, 支持转换 (Y)。
- **RetinaNet** (`configs/retinanet/retinanet_r50_fpn_1x_coco.py`): 经典 Focal Loss 单阶段检测器, 支持转换 (Y)。
- **Faster-RCNN** (`configs/faster_rcnn/faster_rcnn_r50_fpn_1x_coco.py`): 两阶段检测器基线模型, 支持转换 (Y)。
- **表注**: 全部 Y 表示在 "Pytorch==1.6.0 和 TensorRT-7.2.1.6.Ubuntu-16.04.x86_64-gnu.cuda-10.2.cudnn8.0" 上验证通过; 未列入的模型不保证可转换。

## 【公式解读】

原文无公式。

## 【关联】

文档通过前置依赖与下游工序与其他模块形成明确的串联关系:

- **上游前置 — 安装**: 
  - [`get_started.md`](https://mmdetection.readthedocs.io/en/latest/get_started.html): 提供 MMCV 与 MMDetection 的源码安装流程, 是运行转换脚本的运行环境基线。
  - [`ONNXRuntime in mmcv`](https://mmcv.readthedocs.io/en/latest/onnxruntime_op.html): 提供 mmcv-full 中 ONNXRuntime 自定义算子的安装与说明, 保证 ONNX 模型可在 mmcv 算子下正确推理。
  - [`TensorRT plugin in mmcv`](https://github.com/open-mmlab/mmcv/blob/master/docs/tensorrt_plugin.md): 提供 mmcv-full 中 TensorRT 插件的安装与说明, 用于在 TensorRT 引擎中复现 mmcv 自定义算子。

- **上游前置 — 模型格式**: 
  - [`pytorch2onnx` 教程](https://mmdetection.readthedocs.io/en/latest/tutorials/pytorch2onnx.html): 在 ONNX → TensorRT 之前必须先用该工具产出 ONNX 文件, 本文档的 `${MODEL}` 即指该步骤的产物。

- **下游/横向关联**: 
  - "List of supported models" 表中每个 Config 都指向 `configs/` 下的具体配置文件, 与模型仓库的 config 体系直接对应; 在 Reminders 中, 文档要求始终使用 "latest `mmcv` and `mmdetection`", 说明本特性与 mmcv/mmdet 主线版本强耦合, 需随版本迭代更新。

## 【使用方法】

**启用方式 (命令行调用 `tools/deployment/onnx2tensorrt.py`)**:

基础调用模板 (原文给出):
```bash
python tools/deployment/onnx2tensorrt.py \
    ${MODEL} \
    --trt-file ${TRT_FILE} \
    --input-img ${INPUT_IMAGE_PATH} \
    --shape ${IMAGE_SHAPE} \
    --mean ${IMAGE_MEAN} \
    --std ${IMAGE_STD} \
    --dataset ${DATASET_NAME} \
    --workspace-size {WORKSPACE_SIZE} \
    --show \
    --verify \
```

**完整示例 (原文给出, 以 RetinaNet 为例)**:
```bash
python tools/deployment/onnx2tensorrt.py \
    checkpoints/retinanet_r50_fpn_1x_coco.onnx \
    --trt-file checkpoints/retinanet_r50_fpn_1x_coco.trt \
    --input-img demo/demo.jpg \
    --shape 400 600 \
    --mean 123.675 116.28 103.53 \
    --std 58.395 57.12 57.375 \
    --show \
    --verify \
```

**配置项说明 (原文逐条给出)**:
- `model`: ONNX 模型文件路径 (位置参数)。
- `--trt-file`: 输出 TensorRT 引擎文件路径, 默认 `tmp.trt`。
- `--input-img`: 用于 tracing 与转换的输入图片路径, 默认 `demo/demo.jpg`。
- `--shape`: 模型输入 H × W, 默认 `400 600`。
- `--mean`: 输入图片的三个均值, 默认 `123.675 116.28 103.53`。
- `--std`: 输入图片的三个标准差, 默认 `58.395 57.12 57.375`。
- `--dataset`: 输入模型对应的数据集名, 默认 `coco`。
- `--workspace-size`: 构建 TensorRT 引擎所需的 GPU workspace 大小 (单位 GiB), 默认 `1`。
- `--show`: 是否可视化模型输出, 默认 `False`。
- `--verify`: 是否比对 ONNXRuntime 与 TensorRT 模型正确性, 默认 `False`。
- `--to-rgb`: 是否将输入图片转换为 RGB 模式, 默认 `True`。

**注意事项 (原文 Reminders)**:
- 列出的模型如遇问题请提 issue; 未列出模型由于资源有限不保证支持。
- 此特性为实验性且迭代迅速, 务必使用最新的 `mmcv` 与 `mmdetection` 试用。
