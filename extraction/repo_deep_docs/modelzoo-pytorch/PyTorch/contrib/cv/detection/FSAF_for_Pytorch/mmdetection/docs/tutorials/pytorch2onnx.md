# Tutorial 8: Pytorch to ONNX (Experimental)

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/FSAF_for_Pytorch/mmdetection/docs/tutorials/pytorch2onnx.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/FSAF_for_Pytorch/mmdetection/docs/tutorials/pytorch2onnx.md

# 深度解读: mmdetection Pytorch → ONNX 教程文档

---

## 【定位】

本文档是 mmdetection 框架的 **"Tutorial 8: Pytorch to ONNX (Experimental)"**,定位为一份**实验性**的模型导出工具教程,系统性描述如何通过 `tools/deployment/pytorch2onnx.py` 脚本把 mmdetection 中训练好的 PyTorch 检测模型转换为 ONNX 格式,并给出可导出的模型清单及常见注意事项。

---

## 【技术要点】

1. **前置依赖**: 必须先按 [get_started.md](../get_started.md) 安装 MMCV 与 MMDetection,再通过 `pip install onnx onnxruntime` 安装 ONNX 与 ONNX Runtime 两个运行时依赖。
2. **入口脚本**: 核心转换工具为 `tools/deployment/pytorch2onnx.py`,通过命令行接收配置文件 (`CONFIG_FILE`)、权重文件 (`CHECKPOINT_FILE`) 以及多个可选参数完成导出。
3. **关键参数默认值体系**: 默认输入图像为 `tests/data/color.jpg`、输入张量 shape 默认 `800 1216`、图像均值默认 `123.675 116.28 103.53`、标准差默认 `58.395 57.12 57.375`、数据集默认 `coco`、ONNX opset 默认 `11`、输出文件默认 `tmp.onnx`,以及 `--show`、`--verify`、`--simplify` 默认均为 `False`。
4. **支持模型清单 (原文表格保证可导出)**: 涵盖 SSD、YOLOv3、FSAF、RetinaNet、Faster-RCNN 共 5 个检测模型,且全部在 **PyTorch==1.6.0** 下经过测试。
5. **自定义算子兼容性**: 当模型包含 `RoIAlign` 等自定义算子并希望 `--verify` 时,必须**从源码**构建带有 ONNXRuntime 支持的 `mmcv`(参考 `mmcv` 的 onnxruntime_op 文档)。
6. **模型简化能力**: `mmcv.onnx.simplify` 基于 `onnx-simplifier` 项目实现,可对导出模型做简化处理,简化能力与 ONNX Runtime 自定义算子文档共同提供进阶能力。

---

## 【关键机制与数据】

**工作机制 (数据流)**: 整个流程本质上是 PyTorch 的 **tracing 模式导出** —— 脚本以一张静态图像 (`--input-img`,默认 `tests/data/color.jpg`) 作为 tracing 输入,根据用户提供的 `--shape` (默认 `800 1216`) 构造输入张量,并使用 `--mean` 与 `--std` 对图像做归一化预处理;随后调用 `torch.onnx.export` 将模型结构与权重固化为单一 ONNX 文件 (默认输出到 `tmp.onnx`)。

**验证机制 (原文)**: 启用 `--verify` 后,脚本会用 `--test-img` (若未指定则复用 `--input-img`) 在 PyTorch 原模型与 ONNX Runtime 模型上分别推理,逐项比对输出结果以确认导出正确性;启用 `--show` 则会打印导出后 ONNX 模型的计算图架构。

**性能/版本数据 (原文)**: 文档明确指出支持的 5 个模型均在 **PyTorch==1.6.0** 下测试通过,**ONNX opset 版本默认为 11**,该功能被标注为 **experimental**,可能快速演进,因此建议始终搭配最新版的 `mmcv` 与 `mmdetection` 使用。

---

## 【表格解读】

**原文表格 (Supported Models exportable to ONNX):**

| Model | Config | Note |
| :---: | :---: | :---: |
| SSD | `configs/ssd/ssd300_coco.py` | |
| YOLOv3 | `configs/yolo/yolov3_d53_mstrain-608_273e_coco.py` | |
| FSAF | `configs/fsaf/fsaf_r50_fpn_1x_coco.py` | |
| RetinaNet | `configs/retinanet/retinanet_r50_fpn_1x_coco.py` | |
| Faster-RCNN | `configs/faster_rcnn/faster_rcnn_r50_fpn_1x_coco.py` | |

**表格逐行解读:**

- **表头**: 三列分别为 Model (模型名称)、Config (对应配置文件路径)、Note (备注)。Note 列在当前文档中均为空,但表头存在说明后续模型若有特殊说明会写在该列。
- **SSD**: 对应单阶段检测器 SSD 的 300 输入分辨率 COCO 配置 `ssd300_coco.py`,是表中唯一一个 `shape` 固定为 300×300 的轻量级模型示例。
- **YOLOv3**: 对应 Darknet-53 backbone、608 输入尺寸、在 COCO 上训练 273 epoch 的多尺度训练配置 `yolov3_d53_mstrain-608_273e_coco.py`,与下文 Usage 示例脚本中演示的导出对象**完全一致**,所以该模型兼具"被支持 + 被示例"的双重身份。
- **FSAF**: 对应 ResNet-50 + FPN 主干、`1x` 训练计划 (即 12 epoch) 的 COCO 配置 `fsaf_r50_fpn_1x_coco.py`,这是 mmdetection 提出的 **Feature Selective Anchor-Free** 模块的官方实现,锚框自由是该模型被收录的关键。
- **RetinaNet**: 对应 Focal Loss 单阶段检测器 RetinaNet 的 ResNet-50 + FPN、`1x` 训练 COCO 配置 `retinanet_r50_fpn_1x_coco.py`,常作为单阶段检测器的性能 baseline。
- **Faster-RCNN**: 对应两阶段检测器 Faster-RCNN 的 ResNet-50 + FPN、`1x` 训练 COCO 配置 `faster_rcnn_r50_fpn_1x_coco.py`,是表中**唯一**的两阶段检测模型,其内部使用了 `RoIAlign` 自定义算子,因此导出时尤其需要关注 Reminders 中关于源码构建 mmcv 的提醒。
- **表格下方备注 (Notes)**: 仅一条 —— "*All models above are tested with Pytorch==1.6.0*",说明此兼容性清单的测试基线严格绑定 PyTorch 1.6.0 版本,实际使用中若 PyTorch 版本发生变化需自行验证。

---

## 【公式解读】

**原文无公式。** 全文未出现任何 LaTeX 公式、伪代码或数学表达式;转换机制仅以命令行参数与默认值描述,未涉及形式化的张量变换方程。

---

## 【关联】

文档通过一条内部链接与其他教程产生关联:

- **[../get_started.md](../get_started.md)**: 在 Prerequisite 章节中被引用,要求用户在执行本文档的任何转换操作之前,先按照 `get_started.md` 完成 MMCV 与 MMDetection 的安装。这一关联意味着本教程处于"基础安装 → 模型训练 → 模型导出 (本文)"这条流水线中**依赖前序环境准备**的环节。

文档在外部还关联了 mmcv 项目内的若干能力模块(以链接形式指向 mmcv 官方文档):

- **mmcv ONNXRuntime 自定义算子**: 当被导出模型包含 `RoIAlign` 等自定义算子并启用 `--verify` 时,需源码构建带 ONNXRuntime 算子支持的 mmcv;这是导出流程与 mmcv 运行时扩展之间的关键耦合点。
- **mmcv.onnx 模块**: 提供 `simplify` 等高层 API,文档建议查阅其 `onnx.html` 与 `onnxruntime_op.html` 两个子页了解 `onnx-simplifier` 的集成方式。
- **上游**: 本教程的实现位于 mmdetection 仓库 `tools/deployment/pytorch2onnx.py`,其内部依赖 mmdetection 的 `build_detector` API(基于 config 与 checkpoint 重建模型)以及 mmcv 提供的 ONNX 工具链。
- **下游**: 导出的 `.onnx` 文件可被 ONNX Runtime、TensorRT (经 onnx2trt) 等推理后端加载,因此本教程也是 mmdetection 模型**跨平台部署**链路上的中转节点。

---

## 【使用方法】

**安装 (原文):**
```shell
pip install onnx onnxruntime
```

**标准导出命令 (原文完整 CLI):**
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
    --verify
```

**带实际取值的完整示例 (原文,以 YOLOv3 为例):**
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
    --verify
```

**关键配置项速查 (原文默认值):**

| 参数 | 默认值 | 作用 |
|---|---|---|
| `--output-file` | `tmp.onnx` | 导出 ONNX 模型保存路径 |
| `--input-img` | `tests/data/color.jpg` | tracing 与转换的输入图像 |
| `--shape` | `800 1216` | 输入张量 H × W |
| `--mean` | `123.675 116.28 103.53` | 图像三通道均值 |
| `--std` | `58.395 57.12 57.375` | 图像三通道标准差 |
| `--dataset` | `coco` | 数据集名称 |
| `--test-img` | `None` (即用 `--input-img`) | 验证用图像 |
| `--opset-version` | `11` | ONNX opset 版本 |
| `--show` | `False` | 是否打印导出模型架构 |
| `--verify` | `False` | 是否做正确性校验 |
| `--simplify` | `False` | 是否简化导出模型 |

**额外启用方式 (原文未涉及的具体调用,如 API 直接调用、自定义模型导出流程):** 原文未涉及,文档仅给出命令行调用方式。
