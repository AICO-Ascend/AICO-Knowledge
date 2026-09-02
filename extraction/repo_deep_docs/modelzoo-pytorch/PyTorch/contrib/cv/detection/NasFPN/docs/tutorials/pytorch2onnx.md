# Tutorial 8: Pytorch to ONNX (Experimental)

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/NasFPN/docs/tutorials/pytorch2onnx.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/NasFPN/docs/tutorials/pytorch2onnx.md

# 深度解读：Pytorch to ONNX (Experimental)

## 【定位】
本文档是 MMDetection (位于 NasFPN 目录下) 的第 8 篇教程,旨在指导用户如何将基于 PyTorch 训练的 MMDetection 检测模型转换为 ONNX 格式,以便在 ONNX Runtime 等推理引擎上部署运行;文档同时明确标注该功能处于"Experimental (实验性)"阶段。

## 【技术要点】

1. **环境准备**: 需先按照 `get_started.md` 安装 MMCV 与 MMDetection,再通过 `pip install onnx onnxruntime` 安装 ONNX 与 ONNX Runtime 两套依赖库。

2. **核心转换工具**: 使用仓库自带的 `tools/deployment/pytorch2onnx.py` 脚本,通过 PyTorch 自带的 tracing (追踪) 机制导出 ONNX 模型。

3. **关键命令行参数默认值** (原文明确给出,逐项保留):
   - `--output-file` 默认 `tmp.onnx`
   - `--input-img` 默认 `tests/data/color.jpg`
   - `--shape` 默认 `800 1216` (高 × 宽)
   - `--mean` 默认 `123.675 116.28 103.53`
   - `--std` 默认 `58.395 57.12 57.375`
   - `--dataset` 默认 `coco`
   - `--test-img` 默认 `None` (未指定时复用 `--input-img`)
   - `--opset-version` 默认 `11`
   - `--show` 默认 `False`
   - `--verify` 默认 `False`
   - 此外还有 `--simplify` 选项,默认 `False`

4. **模型验证机制**: 通过 `--verify` 选项触发导出前后 PyTorch 模型与 ONNX 模型输出的一致性比对;`--test-img` 提供用于验证的图像,默认复用 `--input-img`。

5. **支持导出的模型清单**: SSD、YOLOv3、FSAF、RetinaNet、Faster-RCNN 共 5 种检测器,均基于 ResNet-50 + FPN 骨干 (YOLOv3 除外,使用 DarkNet-53)。

6. **测试基线版本**: 原文明确标注"所有上述模型均使用 Pytorch==1.6.0 进行测试"。

## 【关键机制与数据】

- **工作原理 (原文)**: 通过 `pytorch2onnx.py` 读取 `${CONFIG_FILE}` 与 `${CHECKPOINT_FILE}`,以一张 `--input-img` 作为追踪输入,按 `--shape` 张量化图像、按照 `--mean/--std` 归一化,再调用 PyTorch 的 ONNX 导出接口生成 ONNX 图,使用 `--opset-version` (默认 11) 作为算子集版本。
- **数据流 (原文)**: 输入图像 → 形状归一化 (`--shape`) → 通道均值方差归一化 (`--mean`/`--std`) → 骨干网络 → 检测头 → 模型输出。
- **性能/约束数据 (原文)**:
  - 文档未提供 ONNX 模型推理速度、显存占用、精度 (mAP) 等量化数据。
  - 仅给出"全部模型使用 Pytorch==1.6.0 测试"这一基线说明。
  - 文档未给出 onnx/onnxruntime 的具体版本号要求,仅要求"Install onnx and onnxruntime"。

## 【表格解读】

原文包含 1 张关键表格,**逐字还原**如下:

|    Model    |                        Config                        | Note  |
| :---------: | :--------------------------------------------------: | :---: |
|     SSD     |             `configs/ssd/ssd300_coco.py`             |       |
|   YOLOv3    |  `configs/yolo/yolov3_d53_mstrain-608_273e_coco.py`  |       |
|    FSAF     |        `configs/fsaf/fsaf_r50_fpn_1x_coco.py`        |       |
|  RetinaNet  |   `configs/retinanet/retinanet_r50_fpn_1x_coco.py`   |       |
| Faster-RCNN | `configs/faster_rcnn/faster_rcnn_r50_fpn_1x_coco.py` |       |

**逐行解读**:
- **表格范围**: 该表格为 "List of supported models exportable to ONNX",列出"保证可导出 ONNX 并在 ONNX Runtime 中运行"的模型。
- **SSD 行**: 配置路径为 `configs/ssd/ssd300_coco.py`,输入尺寸 300×300,单阶段检测器。
- **YOLOv3 行**: 配置路径为 `configs/yolo/yolov3_d53_mstrain-608_273e_coco.py`,骨干为 DarkNet-53,输入尺寸 608×608,采用 273 epoch 多尺度训练策略。
- **FSAF 行**: 配置路径为 `configs/fsaf/fsaf_r50_fpn_1x_coco.py`,采用 ResNet-50 + FPN 骨干,Feature Selective Anchor-Free 检测器。
- **RetinaNet 行**: 配置路径为 `configs/retinanet/retinanet_r50_fpn_1x_coco.py`,ResNet-50 + FPN 骨干,Focal Loss 单阶段检测器。
- **Faster-RCNN 行**: 配置路径为 `configs/faster_rcnn/faster_rcnn_r50_fpn_1x_coco.py`,两阶段检测器,ResNet-50 + FPN 骨干。
- **Note 列**: 原文表格中所有 Note 列均为空,无附加说明。
- **表后注释**: 表格下方单独列出"*All models above are tested with Pytorch==1.6.0*",对所有 5 个模型给出统一基线说明。

## 【公式解读】

原文无公式。文档仅以命令行参数 `mean`/`std`/`shape` 等数值形式给出图像预处理超参,未出现任何 LaTeX 公式或伪代码形式的数学表达式。

## 【关联】

- **上游依赖 — [get_started.md](../get_started.md)**: 文档 Prerequisite 第 1 条明确要求先参考此文件完成 MMCV 与 MMDetection 的安装,是使用本教程的前置条件。
- **配套库 — `mmcv`**: 文档 Reminders 中两次提及:
  - 当模型包含 `RoIAlign` 等自定义算子时,需从源码构建带 ONNXRuntime 支持的 `mmcv` (链接指向 `mmcv.readthedocs.io/.../onnxruntime_op.html`)。
  - `mmcv.onnx.simplify` 功能基于 `onnx-simplifier` (链接指向 `github.com/daquexian/onnx-simplifier`),简化功能文档指向 `mmcv.readthedocs.io/.../onnx.html`。
- **推理后端 — ONNX Runtime**: 文档验证 (verify) 流程与运行时均依赖 ONNX Runtime,是导出后的目标推理引擎。
- **模型生态**: 表格中 5 个支持导出的模型 (SSD/YOLOv3/FSAF/RetinaNet/Faster-RCNN) 与 MMDetection 的检测器实现一一对应,需配合对应 `configs/` 下的配置文件使用。
- **教程体系**: 作为 Tutorial 8,与其他教程 (例如部署、优化相关) 共同构成 MMDetection 的端到端使用文档。

## 【使用方法】

**最小可用命令** (来自原文 Usage 段落):

```bash
python tools/deployment/pytorch2onnx.py \
    ${CONFIG_FILE} \
    ${CHECKPOINT_FILE} \
    --output-file ${OUTPUT_FILE} \
    --input-img ${INPUT_IMAGE_PATH} \
    --shape ${IMAGE_SHAPE} \
    --mean ${IMAGE_MEAN} \
    --std ${IMAGE_STD} \
    --dataset ${DATASET_NAME} \
    --test-img ${TEST_IMAGE_PATH} \
    --opset-version ${OPSET_VERSION} \
    --show \
    --verify \
```

**完整示例** (原文 Example 段落,以 YOLOv3 为例):

```bash
python tools/deployment/pytorch2onnx.py \
    configs/yolo/yolov3_d53_mstrain-608_273e_coco.py \
    checkpoints/yolo/yolov3_d53_mstrain-608_273e_coco.pth \
    --output-file checkpoints/yolo/yolov3_d53_mstrain-608_273e_coco.onnx \
    --input-img demo/demo.jpg \
    --test-img tests/data/color.jpg \
    --shape 608 608 \
    --mean 0 0 0 \
    --std 255 255 255 \
    --show \
    --verify \
```

**典型配置项取值 (原文表格 Example 已覆盖)**:
- 单阶段输入: `--shape 608 608`,配合 `--mean 0 0 0 --std 255 255 255`(即不做均值方差归一化,直接 /255)。
- 两阶段/默认输入: `--shape 800 1216`,配合 `--mean 123.675 116.28 103.53 --std 58.395 57.12 57.375`(ImageNet 统计量)。

**注意事项 (原文 Reminders 提炼)**:
- 含 `RoIAlign` 等自定义算子时,需源码构建带 ONNXRuntime 支持的 `mmcv`。
- `--simplify` 依赖 `onnx-simplifier`,详细用法参考 mmcv 官方文档对应条目。
- 该功能仍为实验性,建议始终使用最新 `mmcv` 与 `mmdetection`。
- 列表外的模型需用户自行调试。
