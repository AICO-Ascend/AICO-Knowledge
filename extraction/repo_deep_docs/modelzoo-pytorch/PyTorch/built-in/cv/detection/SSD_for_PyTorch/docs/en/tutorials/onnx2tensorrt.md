# Tutorial 9: ONNX to TensorRT (Experimental)

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/cv/detection/SSD_for_PyTorch/docs/en/tutorials/onnx2tensorrt.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/cv/detection/SSD_for_PyTorch/docs/en/tutorials/onnx2tensorrt.md

【定位】
本文是 MMDetection 部署工具链中的「ONNX → TensorRT」转换教程 (Tutorial 9), 解决如何把已经导出的 ONNX 检测模型进一步转换为 TensorRT 推理引擎, 并在 TensorRT 上做精度/推理验证的工程问题。

【技术要点】

1. **转换链路**: PyTorch → ONNX → TensorRT 是三段式, 本文聚焦于第二段; 第一段需要先用 `pytorch2onnx` 工具产出 ONNX 文件, 第三段 (验证/评测) 通过 `tools/deployment/test.py` 完成。
2. **入口脚本**: `tools/deployment/onnx2tensorrt.py`, 通过传入 `${CONFIG}` 与 `${MODEL}` (ONNX 文件) 完成转换。
3. **依赖前置**: 必须安装 `mmcv-full` (而非 `mmcv`), 并且该 `mmcv-full` 需要同时包含 ONNXRuntime custom ops 与 TensorRT plugins; MMCV/MMDetection 推荐源码安装。
4. **动态 shape 支持**: 通过 `--shape`、`--min-shape`、`--max-shape` 三个选项控制; 若不指定 `--min-shape`/`--max-shape`, 则与 `--shape` 相同, 即退化为静态 shape。
5. **TensorRT 引擎构建资源**: 通过 `--workspace-size` 控制构建引擎所需的 GPU 显存, 单位 GiB, 默认 1 GiB。
6. **结果验证开关**: `--verify` 会在同一输入下对比 ONNXRuntime 与 TensorRT 的输出, 用于核对转换正确性; `--show` 可视化输出; `--verbose` 打印调试日志。
7. **官方推荐替代方案**: 文档顶部醒目提示用户改用 MMDeploy (`https://mmdeploy.readthedocs.io/`) 进行部署, 说明该 onnx2tensorrt 工具属于过渡期的实验性能力。

【关键机制与数据】

- **工作原理 (原文)**: 把已导出的 ONNX 模型作为输入, 通过 `onnx2tensorrt.py` 调用 TensorRT 的 builder/builder 进行序列化, 生成 `.trt` 引擎文件 (`--trt-file`, 默认 `tmp.trt`); `--input-img` (默认 `demo/demo.jpg`) 用于 tracing/转换时的样例输入。
- **关键默认值 (原文)**:
  - `--shape` 默认 `400 600` (高 宽)
  - `--workspace-size` 默认 `1` GiB
  - `--trt-file` 默认 `tmp.trt`
  - `--input-img` 默认 `demo/demo.jpg`
  - `--show`/`--verify`/`--verbose` 默认均为 `False`
  - `--min-shape`/`--max-shape` 默认与 `--shape` 相同
- **验证机制 (原文)**: `--verify` 决定是否在 ONNXRuntime 与 TensorRT 之间做模型正确性比对 (correctness verification)。
- **测试环境 (原文)**: "All models above are tested with Pytorch==1.6.0, onnx==1.7.0 and TensorRT-7.2.1.6.Ubuntu-16.04.x86_64-gnu.cuda-10.2.cudnn8.0"
- **示例 (原文)**: 以 `retinanet_r50_fpn_1x_coco` 为例, 配置文件 `configs/retinanet/retinanet_r50_fpn_1x_coco.py`, ONNX 文件 `checkpoints/retinanet_r50_fpn_1x_coco.onnx`, 产物 `checkpoints/retinanet_r50_fpn_1x_coco.trt`, shape `400 600`, 开启 `--show` 与 `--verify`。
- **风险提示 (原文)**: 该能力标注 "Experimental", 可能快速变动, 建议始终使用最新 `mmcv` 与 `mmdetection`; 同时建议迁移到 MMDeploy。

【表格解读】

原文表格 (逐字还原):

|       Model        |                              Config                              | Dynamic Shape | Batch Inference | Note |
| :----------------: | :--------------------------------------------------------------: | :-----------: | :-------------: | :--: |
|        SSD         |                   `configs/ssd/ssd300_coco.py`                   |       Y       |        Y        |      |
|        FSAF        |              `configs/fsaf/fsaf_r50_fpn_1x_coco.py`              |       Y       |        Y        |      |
|        FCOS        |         `configs/fcos/fcos_r50_caffe_fpn_4x4_1x_coco.py`         |       Y       |        Y        |      |
|       YOLOv3       |        `configs/yolo/yolov3_d53_mstrain-608_273e_coco.py`        |       Y       |        Y        |      |
|     RetinaNet      |         `configs/retinanet/retinanet_r50_fpn_1x_coco.py`         |       Y       |        Y        |      |
|    Faster R-CNN    |       `configs/faster_rcnn/faster_rcnn_r50_fpn_1x_coco.py`       |       Y       |        Y        |      |
|   Cascade R-CNN    |      `configs/cascade_rcnn/cascade_rcnn_r50_fpn_1x_coco.py`      |       Y       |        Y        |      |
|     Mask R-CNN     |         `configs/mask_rcnn/mask_rcnn_r50_fpn_1x_coco.py`         |       Y       |        Y        |      |
| Cascade Mask R-CNN |   `configs/cascade_rcnn/cascade_mask_rcnn_r50_fpn_1x_coco.py`    |       Y       |        Y        |      |
|     PointRend      | `configs/point_rend/point_rend_r50_caffe_fpn_mstrain_1x_coco.py` |       Y       |        Y        |      |

逐行解读:

- **SSD**: 配置 `configs/ssd/ssd300_coco.py`, 支持动态 shape (Y) 与 batch 推理 (Y), Note 列无附加说明。
- **FSAF**: 配置 `configs/fsaf/fsaf_r50_fpn_1x_coco.py`, 动态 shape 与 batch 推理均 Y, Note 留空。
- **FCOS**: 配置 `configs/fcos/fcos_r50_caffe_fpn_4x4_1x_coco.py`, 动态 shape 与 batch 推理均 Y, Note 留空。
- **YOLOv3**: 配置 `configs/yolo/yolov3_d53_mstrain-608_273e_coco.py`, 动态 shape 与 batch 推理均 Y, Note 留空。
- **RetinaNet**: 配置 `configs/retinanet/retinanet_r50_fpn_1x_coco.py`, 动态 shape 与 batch 推理均 Y, Note 留空 (这也是 "Usage" 示例所选用的模型)。
- **Faster R-CNN**: 配置 `configs/faster_rcnn/faster_rcnn_r50_fpn_1x_coco.py`, 动态 shape 与 batch 推理均 Y, Note 留空。
- **Cascade R-CNN**: 配置 `configs/cascade_rcnn/cascade_rcnn_r50_fpn_1x_coco.py`, 动态 shape 与 batch 推理均 Y, Note 留空。
- **Mask R-CNN**: 配置 `configs/mask_rcnn/mask_rcnn_r50_fpn_1x_coco.py`, 动态 shape 与 batch 推理均 Y, Note 留空。
- **Cascade Mask R-CNN**: 配置 `configs/cascade_rcnn/cascade_mask_rcnn_r50_fpn_1x_coco.py`, 动态 shape 与 batch 推理均 Y, Note 留空。
- **PointRend**: 配置 `configs/point_rend/point_rend_r50_caffe_fpn_mstrain_1x_coco.py`, 动态 shape 与 batch 推理均 Y, Note 留空。

表格下方 Note: 测试环境锁定在 PyTorch 1.6.0 + onnx 1.7.0 + TensorRT-7.2.1.6 (Ubuntu 16.04, CUDA 10.2, cuDNN 8.0)。

【公式解读】
原文无公式。

【关联】

- **上游 (PyTorch → ONNX)**: 必须先经过 [pytorch2onnx.html](https://mmdetection.readthedocs.io/en/latest/tutorials/pytorch2onnx.html) 把检测模型导出为 ONNX, 这是本文 ONNX 输入文件的来源。
- **运行时后端**: 依赖 MMCV 中实现的 ONNXRuntime 自定义算子 (`mmcv-full` + ONNXRuntime custom ops) 与 TensorRT 插件 (`TensorRT plugin in mmcv`), 文档外链分别指向 `https://mmcv.readthedocs.io/en/latest/deployment/onnxruntime_op.html` 与 `https://github.com/open-mmlab/mmcv/blob/master/docs/en/deployment/tensorrt_plugin.md/`。
- **下游 (TensorRT 模型评测)**: 评测流程引用自姊妹文档 `pytorch2onnx.md` 的两个锚点:
  - `pytorch2onnx.md#how-to-evaluate-the-exported-models`: 说明如何用 `tools/deplopyment/test.py` (原文笔误, 实际应为 `tools/deployment/test.py`) 评测导出的 TensorRT 模型。
  - `pytorch2onnx.md#results-and-models`: 各模型导出/转换后的精度与速度结果汇总。
- **替代方案**: 文档顶端直接推荐 [MMDeploy](https://mmdeploy.readthedocs.io/) 作为该实验性流程的官方替代。
- **安装前置**: 关联 `get_started.md` (`https://mmdetection.readthedocs.io/en/latest/get_started.html`), 文中要求按其步骤源码安装 MMCV 与 MMDetection。

【使用方法】

启用方式与命令 (原文给出):

1. 准备 ONNX 模型文件 (通过 `pytorch2onnx` 工具导出)。
2. 执行转换:

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

完整参数说明 (原文):

- `config`: 模型配置文件路径
- `model`: ONNX 模型文件路径
- `--trt-file`: 输出 TensorRT 引擎文件路径, 默认 `tmp.trt`
- `--input-img`: 用于 tracing/转换的输入图像路径, 默认 `demo/demo.jpg`
- `--shape`: 模型输入的 高 宽, 默认 `400 600`
- `--min-shape`: 模型输入最小 高 宽, 默认同 `--shape`
- `--max-shape`: 模型输入最大 高 宽, 默认同 `--shape`
- `--workspace-size`: 构建 TensorRT 引擎所需的 GPU workspace 大小 (GiB), 默认 `1` GiB
- `--show`: 是否可视化模型输出, 默认 `False`
- `--verify`: 是否在 ONNXRuntime 与 TensorRT 间做正确性校验, 默认 `False`
- `--verbose`: 是否打印日志 (调试用), 默认 `False`

完整示例 (原文, 以 RetinaNet 为例):

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

导出后评测: 使用 `tools/deplopyment/test.py` (原文如此), 具体步骤详见 `pytorch2onnx.md#how-to-evaluate-the-exported-models` 与 `pytorch2onnx.md#results-and-models`。
