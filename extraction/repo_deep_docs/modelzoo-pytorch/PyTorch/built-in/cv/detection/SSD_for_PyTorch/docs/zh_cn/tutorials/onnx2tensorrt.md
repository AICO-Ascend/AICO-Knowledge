# 教程 9: ONNX 到 TensorRT 的模型转换（实验性支持）

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/cv/detection/SSD_for_PyTorch/docs/zh_cn/tutorials/onnx2tensorrt.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/cv/detection/SSD_for_PyTorch/docs/zh_cn/tutorials/onnx2tensorrt.md

# 一体化深度解读：ONNX 到 TensorRT 模型转换（实验性支持）

## 【定位】

这篇文档是 MMDetection 部署流水线中"ONNX → TensorRT"阶段的实验性转换教程，解决**如何将 PyTorch 训练得到的检测模型经 ONNX 序列化后，进一步通过 TensorRT 编译为可在 NVIDIA GPU 上高效推理的引擎文件（.trt）**，并提供转换、正确性验证与精度评估的完整操作指引。

## 【技术要点】

1. **三段式部署链路**：先从源码安装 `mmcv` 和 `MMDetection` → 安装带 ONNXRuntime 与 TensorRT 插件支持的 `mmcv-full` → 用 `pytorch2onnx` 工具生成 ONNX 中间产物，再使用 `onnx2tensorrt.py` 完成 TensorRT 转换。
2. **入口脚本**：`tools/deployment/onnx2tensorrt.py`，通过命令行传入 `${CONFIG}` 和 `${MODEL}` 两个位置参数（分别为配置文件路径、ONNX 模型文件路径）。
3. **关键可调参数**：包含输出引擎路径 `--trt-file`（默认 `tmp.trt`）、固定输入尺寸 `--shape`（默认 `400 600`）、动态尺寸 `--min-shape`/`--max-shape`（默认同 `--shape`）、GPU 工作空间 `--workspace-size`（默认 `1` GiB）、可视化开关 `--show`、正确性校验开关 `--verify`、调试日志开关 `--verbose`（后三者默认 `False`）。
4. **评估工具**：`tools/deplopyment/test.py`（原文笔误保留原拼写）用于评估转换后 TensorRT 引擎的精度与性能，相关使用细节指向 `pytorch2onnx.md` 的对应章节。
5. **支持矩阵**：表格列出 10 个模型（SSD、FSAF、FCOS、YOLOv3、RetinaNet、Faster R-CNN、Cascade R-CNN、Mask R-CNN、Cascade Mask R-CNN、PointRend），所有模型**同时**支持 Dynamic Shape 与 Batch Inference（两项均为 Y）。
6. **实验性声明**：文档明确强调功能实验性，强烈建议使用最新的 `mmcv` 和 `mmdetection`；遇到列表外模型可能无法得到官方支持。

## 【关键机制与数据】

- **转换机制**（原文）：通过 `onnx2tensorrt.py` 加载 `${CONFIG}` 指定的模型配置与 `.onnx` 文件，结合 `--input-img` 指定的图像作为追踪输入，按 `--shape`/`--min-shape`/`--max-shape` 维度构建 TensorRT 引擎，最终写出 `--trt-file` 指定的 `.trt` 引擎文件。
- **GPU 工作空间**（原文）：`--workspace-size` 以 GiB 为单位设置 TensorRT 构建阶段可用的显存上限，默认 `1` GiB，决定了引擎可用的算子融合与中间张量缓存空间。
- **正确性校验**（原文）：`--verify` 在 ONNXRuntime 与 TensorRT 之间做输出一致性比对，默认 `False`，启用后会进行端到端数值对比。
- **可视化**（原文）：`--show` 控制是否可视化模型输出，默认 `False`。
- **测试环境基线**（原文）：上述全部模型在 `Pytorch==1.6.0, onnx==1.7.0 与 TensorRT-7.2.1.6.Ubuntu-16.04.x86_64-gnu.cuda-10.2.cudnn8.0` 环境下验证通过；本教程未给出具体 mAP、AP50 或 FPS 等性能数字。
- **数据流**（原文）：`PyTorch 模型 → ONNX（经 pytorch2onnx）→ TensorRT 引擎（经 onnx2tensorrt.py）→ 推理/评估（经 tools/deplopyment/test.py）`；原文未给出推理时的 throughput、latency 等运行时性能数据。

## 【表格解读】

> 原文表格（逐字还原）：

| Model | Config | Dynamic Shape | Batch Inference | Note |
| :---: | :---: | :---: | :---: | :---: |
| SSD | `configs/ssd/ssd300_coco.py` | Y | Y |  |
| FSAF | `configs/fsaf/fsaf_r50_fpn_1x_coco.py` | Y | Y |  |
| FCOS | `configs/fcos/fcos_r50_caffe_fpn_4x4_1x_coco.py` | Y | Y |  |
| YOLOv3 | `configs/yolo/yolov3_d53_mstrain-608_273e_coco.py` | Y | Y |  |
| RetinaNet | `configs/retinanet/retinanet_r50_fpn_1x_coco.py` | Y | Y |  |
| Faster R-CNN | `configs/faster_rcnn/faster_rcnn_r50_fpn_1x_coco.py` | Y | Y |  |
| Cascade R-CNN | `configs/cascade_rcnn/cascade_rcnn_r50_fpn_1x_coco.py` | Y | Y |  |
| Mask R-CNN | `configs/mask_rcnn/mask_rcnn_r50_fpn_1x_coco.py` | Y | Y |  |
| Cascade Mask R-CNN | `configs/cascade_rcnn/cascade_mask_rcnn_r50_fpn_1x_coco.py` | Y | Y |  |
| PointRend | `configs/point_rend/point_rend_r50_caffe_fpn_mstrain_1x_coco.py` | Y | Y |  |

表格下方原文明示："*以上所有模型通过 Pytorch==1.6.0, onnx==1.7.0 与 TensorRT-7.2.1.6.Ubuntu-16.04.x86_64-gnu.cuda-10.2.cudnn8.0 测试*"

**逐行解读**：

| 行 | Model | Config 解读 | Dynamic Shape | Batch Inference | 含义 |
|---|-------|------------|---------------|-----------------|------|
| 1 | SSD | 单阶段多框检测器，对应 `ssd300_coco.py` | Y | Y | 既可处理可变输入尺寸，也可进行多图 batch 推理 |
| 2 | FSAF | 特征选择锚框自由检测器，主干 ResNet-50 + FPN，1x schedule，COCO 数据集 | Y | Y | 动态尺寸与 batch 推理均支持 |
| 3 | FCOS | 像素级单阶段检测器，使用 caffe 风格预训练主干 + FPN，4x4 训练 | Y | Y | 同上 |
| 4 | YOLOv3 | DarkNet-53 主干，多尺度训练 608 输入，273 epoch COCO 训练 | Y | Y | 同上 |
| 5 | RetinaNet | 经典 focal loss 单阶段检测器，ResNet-50 + FPN | Y | Y | 同上 |
| 6 | Faster R-CNN | 两阶段经典检测器，ResNet-50 + FPN | Y | Y | 同上 |
| 7 | Cascade R-CNN | 多阶段级联两阶段检测器，ResNet-50 + FPN | Y | Y | 同上 |
| 8 | Mask R-CNN | 在 Faster R-CNN 基础上增加实例分割分支 | Y | Y | 同时支持检测/分割双任务推理 |
| 9 | Cascade Mask R-CNN | Cascade R-CNN + 实例分割分支 | Y | Y | 同上 |
| 10 | PointRend | 引入点采样细化机制，caffe 主干 + 多尺度训练 | Y | Y | 同上 |

注：表中所有 Note 列原文均为空，未给出额外备注信息。

## 【公式解读】

原文无公式。

## 【关联】

- **上游（ONNX 生成）**：依赖 [`pytorch2onnx.md`](../pytorch2onnx.md) 工具完成 PyTorch 到 ONNX 的转换，是本教程的前置步骤。
- **评估路径**：本教程将"如何评估导出的模型"具体方法直接指向 [`pytorch2onnx.md#how-to-evaluate-the-exported-models`](../pytorch2onnx.md#how-to-evaluate-the-exported-models)，即与 ONNX 导出模型共用同一份评估流程；性能与模型数据参见 [`pytorch2onnx.md#results-and-models`](../pytorch2onnx.md#results-and-models)。
- **基础设施依赖**：
  - 安装基础：[`get_started.md`](https://mmdetection.readthedocs.io/en/latest/get_started.html) → 源码安装 `mmcv` 与 `MMDetection`。
  - `mmcv-full`：[ONNXRuntime in mmcv](https://mmcv.readthedocs.io/en/latest/deployment/onnxruntime_op.html) 与 [TensorRT plugin in mmcv](https://github.com/open-mmlab/mmcv/blob/master/docs/en/deployment/tensorrt_plugin.md/) 提供 ONNXRuntime 自定义算子与 TensorRT 算子插件支持。
- **下游迁移建议**：文档首部用引用块标注"尝试使用新的 MMDeploy 来部署你的模型"，并附 [MMDeploy](https://mmdeploy.readthedocs.io/) 链接，表明该实验性功能已被 MMDeploy 取代，本教程仅作历史/补充参考。
- **同类支持对比**：与 `pytorch2onnx` 教程相比，本教程专攻"后端推理引擎构建"，二者构成"前端导出 + 后端编译"的完整部署链路。

## 【使用方法】

**1. 安装前置**（原文）：
- 参考 [`get_started.md`](https://mmdetection.readthedocs.io/en/latest/get_started.html) 从源码安装 `mmcv` 和 `MMDetection`。
- 安装带 ONNXRuntime 自定义算子与 TensorRT 插件的 `mmcv-full`（参见 [ONNXRuntime in mmcv](https://mmcv.readthedocs.io/en/latest/deployment/onnxruntime_op.html) 与 [TensorRT plugin in mmcv](https://github.com/open-mmlab/mmcv/blob/master/docs/en/deployment/tensorrt_plugin.md/)）。
- 使用 [`pytorch2onnx`](https://mmdetection.readthedocs.io/en/latest/tutorials/pytorch2onnx.html) 工具将 PyTorch 模型转换为 ONNX。

**2. ONNX → TensorRT 转换命令**（原文逐字保留）：
```bash
python tools/deployment/onnx2tensorrt.py \
    ${CONFIG} \
    ${MODEL} \
    --trt-file ${TRT_FILE} \
    --input-img ${INPUT_IMAGE_PATH} \
    --shape ${INPUT_IMAGE_SHAPE} \
    --min-shape ${MIN_IMAGE_SHAPE} \
    --max-shape ${MAX_IMAGE_SHAPE} \
    --workspace-size {WORKSPACE_SIZE} \
    --show \
    --verify \
```

**3. 完整示例：以 RetinaNet 为例**（原文）：
```bash
python tools/deployment/onnx2tensorrt.py \
    configs/retinanet/retinanet_r50_fpn_1x_coco.py \
    checkpoints/retinanet_r50_fpn_1x_coco.onnx \
    --trt-file checkpoints/retinanet_r50_fpn_1x_coco.trt \
    --input-img demo/demo.jpg \
    --shape 400 600 \
    --show \
    --verify \
```

**4. 评估导出模型**（原文）：
使用 `tools/deplopyment/test.py`（原文拼写原样保留）评估 TensorRT 模型，详细方法参见 [pytorch2onnx.md#how-to-evaluate-the-exported-models](../pytorch2onnx.md#how-to-evaluate-the-exported-models)，结果与模型清单参见 [pytorch2onnx.md#results-and-models](../pytorch2onnx.md#results-and-models)。

**5. 注意事项**（原文）：
- 列表中模型如有问题，欢迎提 issue；列表外模型受限于资源，未必能提供官方支持，需自行调试。
- 由于该功能是实验性的且可能快速演进，请始终使用最新的 `mmcv` 与 `mmdetection`。
- "常见问题"小节原文明确标注为"空"。
