# Tutorial 8: Pytorch to ONNX (Experimental)

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/cv/detection/RetinaNet_for_PyTorch/docs/tutorials/pytorch2onnx.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/cv/detection/RetinaNet_for_PyTorch/docs/tutorials/pytorch2onnx.md

【定位】
本教程面向 MMDetection 用户,介绍如何将 PyTorch 训练好的检测模型导出为 ONNX 格式以便在 ONNX Runtime 等推理后端运行,文档性质为实验性 (Experimental) 功能说明。

【技术要点】
- 依赖准备:需先安装 MMCV 与 MMDetection (参考 `get_started.md`),再额外 `pip install onnx onnxruntime`。
- 转换入口脚本: `tools/deployment/pytorch2onnx.py`,通过若干 CLI 参数控制 config、checkpoint、输入图片、shape、mean/std、dataset、test-img、opset-version、show、verify、simplify 等。
- 默认参数 (原文给出):输出文件 `tmp.onnx`、输入图 `tests/data/color.jpg`、shape `800 1216`、mean `123.675 116.28 103.53`、std `58.395 57.12 57.375`、dataset `coco`、test-img `None` (即用 input-img 验证)、opset-version `11`、show/verify/simplify 均为 `False`。
- 支持模型范围 (官方保证可导出 + 可在 ONNX Runtime 运行):SSD、YOLOv3、FSAF、RetinaNet、Faster R-CNN 共 5 个;测试环境 PyTorch==1.6.0。
- 自定义算子处理:若模型含 `RoIAlign` 等自定义算子,验证 ONNX 时需要从源码编译带 ONNXRuntime 的 mmcv。
- 模型简化能力:`mmcv.onnx.simplify` 基于 onnx-simplifier (daquexian/onnx-simplifier),属于 mmcv 的 onnx 工具链。
- 实验性提醒:作者明确指出该特性是 experimental,可能会快速变化,建议始终使用最新的 mmcv 和 mmdetection。

【关键机制与数据】
- 工作原理:用 `tools/deployment/pytorch2onnx.py` 以一张示例图 (`--input-img`, 默认 `tests/data/color.jpg`) 进行 trace,把 PyTorch 模型转成 ONNX 图,输出到 `--output-file`。
- 数据流:trace → 导出 ONNX → (可选) `--show` 打印导出模型结构 → (可选) `--test-img` 加载另一张图,使用 `--verify` 在 ONNX Runtime 上前向推理,对比 PyTorch 与 ONNX 输出以验证正确性;`--simplify` 调用 `mmcv.onnx.simplify` 进行图简化。
- 形状约束:输入张量 shape 由 `--shape` 指定 (高、宽两个整数,默认 `800 1216`);Example 中用 `608 608` 适配 YOLOv3。
- 归一化参数:mean/std 由用户传入,Example 中 YOLOv3 用 `0 0 0` 与 `255 255 255` (即不做减均值除方差,等价把 [0,255] 原值送入);默认值 `123.675 116.28 103.53` / `58.395 57.12 57.375` 为 MMDetection 在 COCO 评估时的常用 ImageNet 风格归一化。
- 验证机制:`--verify` 时若模型使用自定义 op (如 RoIAlign),需要带 ONNXRuntime 的 mmcv 才能在 Python 端复现算子进行数值对齐。
- 性能数据:原文未给出任何吞吐/精度/时延数据,仅声明「在 PyTorch==1.6.0 下测试可导出 + 可运行」。

【表格解读】

|    Model    |                        Config                        |  Note  |
| :---------: | :--------------------------------------------------: | :----: |
|     SSD     |             `configs/ssd/ssd300_coco.py`             |        |
|   YOLOv3    |  `configs/yolo/yolov3_d53_mstrain-608_273e_coco.py`  |        |
|    FSAF     |        `configs/fsaf/fsaf_r50_fpn_1x_coco.py`        |        |
|  RetinaNet  |   `configs/retinanet/retinanet_r50_fpn_1x_coco.py`   |        |
| Faster-RCNN | `configs/faster_rcnn/faster_rcnn_r50_fpn_1x_coco.py` |        |

Notes:
- *All models above are tested with Pytorch==1.6.0*

逐行解读:
- **SSD**:`configs/ssd/ssd300_coco.py`,单阶段检测器,Note 列空,表示无额外导出注意事项。
- **YOLOv3**:`configs/yolo/yolov3_d53_mstrain-608_273e_coco.py`,DarkNet-53 主干 + 多尺度训练 608 输入,Note 列空;文档 Example 正是用该配置演示,shape 设为 `608 608`。
- **FSAF**:`configs/fsaf/fsaf_r50_fpn_1x_coco.py`,ResNet-50 + FPN 的 FSAF,Note 列空。
- **RetinaNet**:`configs/retinanet/retinanet_r50_fpn_1x_coco.py`,ResNet-50 + FPN 的 Focal Loss 单阶段检测器,Note 列空。
- **Faster-RCNN**:`configs/faster_rcnn/faster_rcnn_r50_fpn_1x_coco.py`,两阶段检测器,含 RoIAlign 等自定义算子,在 `--verify` 时需要带 ONNXRuntime 的 mmcv 才能完整对齐。
- **Note**:所有上述模型均在 PyTorch==1.6.0 下做过导出 + 运行验证,其它 PyTorch 版本未在表中保证。

【公式解读】
原文无公式。

【关联】
- 与安装文档的关联:本文 Prerequisite 第 1 条引用 `../get_started.md` (内部链接指向 MMDetection 安装说明) 用于安装 MMCV 与 MMDetection。
- 与 mmcv 的关联:`Reminders` 节指出 `mmcv.onnx.simplify` (基于 onnx-simplifier)、`mmcv` 中 ONNX 相关 op 编译 (`RoIAlign` 等) 是该导出流程的下游依赖,可通过 `https://mmcv.readthedocs.io/en/latest/onnx.html` 与 `https://mmcv.readthedocs.io/en/latest/onnxruntime_op.html` 获取更多说明 (原文给出的外部链接,不属于仓内 internal link)。
- 与所支持模型检测器的关联:所列 5 个模型 (SSD/YOLOv3/FSAF/RetinaNet/Faster R-CNN) 分别对应仓内 `configs/` 子目录中的一份标准 config;YOLOv3 config 在 Example 中被直接调用,说明本文与 `tools/deployment/pytorch2onnx.py`、各模型 config 文件是「文档 ↔ 脚本 ↔ 模型配置」三者配套关系。
- 上下游关系:上游是 PyTorch 训练产物 (`.pth` checkpoint + config),下游是 ONNX Runtime 等推理引擎;本文描述的是这一中间转换环节。

【使用方法】
- 安装前置依赖 (原文命令):
  ```shell
  pip install onnx onnxruntime
  ```
- 通用转换命令 (原文给出模板,占位符 `${...}` 需替换):
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
- 实际 Example (原文给出,以 YOLOv3 为例):
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
- 可选配置项 (原文 `Description of all arguments` 一节):
  - `--simplify`:是否简化导出的 ONNX 模型 (默认 `False`)。
  - `--opset-version`:ONNX opset 版本 (默认 `11`)。
  - `--show`:是否打印导出模型结构 (默认 `False`)。
  - `--verify`:是否校验导出模型正确性 (默认 `False`)。
- 注意事项 (原文 `Reminders`):
  - 含 `RoIAlign` 等自定义算子的模型在 `--verify` 时,需要从源码编译带 ONNXRuntime 的 mmcv。
  - 简化功能依赖 `mmcv.onnx.simplify`,其底层为 onnx-simplifier。
  - 该功能为 experimental,建议使用最新 mmcv 与 mmdetection;未在表中列出的模型若出问题需自行排查。
