# Tutorial 9: ONNX to TensorRT (Experimental)

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/dev/perf/CascadeMaskRCNN_iflytek_for_PyTorch/docs/tutorials/onnx2tensorrt.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/dev/perf/CascadeMaskRCNN_iflytek_for_PyTorch/docs/tutorials/onnx2tensorrt.md

# 一体化深度解读:ONNX to TensorRT 教程

---

## 【定位】

本文档是 MMCV/MMDetection 工具链中 **Tutorial 9** 的一篇实验性指南,聚焦于 **将已导出的 ONNX 模型进一步转换为 TensorRT 引擎文件(`.trt`)**,从而获得推理加速;同时提供模型支持矩阵与对导出后模型的评估入口。

---

## 【技术要点】

1. **转换流程定位**:本文档假设读者已完成 PyTorch→ONNX 的转换(`pytorch2onnx` 工具),本文只负责 **ONNX→TensorRT** 这一下游环节。
2. **核心命令**:`python tools/deployment/onnx2tensorrt.py ${MODEL} --trt-file ${TRT_FILE} --input-img ... --shape ...` 等 13 个参数。
3. **前置依赖(三层)**:① 源码安装 MMCV 与 MMDetection(参见 `get_started.html`);② 在 `mmcv-full` 中启用 **ONNXRuntime custom ops** 与 **TensorRT plugins**;③ 先用 `pytorch2onnx` 工具产生 ONNX 文件。
4. **关键默认值(原文)**:`--shape` 默认 `400 600`;`--mean` 默认 `123.675 116.28 103.53`;`--std` 默认 `58.395 57.12 57.375`;`--dataset` 默认 `coco`;`--workspace-size` 默认 `1` GiB;`--trt-file` 默认 `tmp.trt`;`--input-img` 默认 `demo/demo.jpg`;`--to-rgb` 默认 `True`。
5. **两个开关行为参数**:`--show`(可视化输出,默认 `False`)与 `--verify`(在 ONNXRuntime 与 TensorRT 之间做一致性比对,默认 `False`)。
6. **支持矩阵边界**:表中 7 个模型在 **Pytorch==1.6.0、onnx==1.7.0、TensorRT-7.2.1.6.Ubuntu-16.04.x86_64-gnu.cuda-10.2.cudnn8.0** 环境下被验证;文档明确标注该功能为 **Experimental**,需始终使用最新的 `mmcv` 与 `mmdetection`。

---

## 【关键机制与数据】

- **工作原理**(原文描述):通过 `tools/deployment/onnx2tensorrt.py` 加载一个 ONNX 模型文件,使用一张样例图像(`--input-img`)对模型进行 tracing/转换,并结合 `--shape`/`--max-shape`/`--mean`/`--std`/`--workspace-size` 等参数构建 TensorRT 引擎,最终将引擎序列化到 `--trt-file` 指定的路径(默认 `tmp.trt`)。
- **动态形状机制**:`--max-shape` 若未指定则与 `--shape` 相同,说明 TensorRT 引擎默认按固定 shape 编译;显式给出更大 `--max-shape` 才会启用 Dynamic Shape。
- **数据流(以 Example 为例,原文)**:
  `checkpoints/retinanet_r50_fpn_1x_coco.onnx` → 输入图 `demo/demo.jpg` → shape `400 600` → mean/std 与默认值一致 → 输出 `checkpoints/retinanet_r50_fpn_1x_coco.trt`,并启用 `--show` 与 `--verify`。
- **正确性校验**:`--verify=True` 时在 ONNXRuntime 与 TensorRT 之间做一致性比对(原文未给出容差阈值)。
- **评估入口**:使用 `tools/deplopyment/test.py`(原文拼写为 `deplopyment`)对导出的 TensorRT 模型进行评测,详细说明跳转至 `pytorch2onnx.md`。
- **性能数据**:原文未给出具体的 FPS/时延/显存数字;支持的 7 个模型都支持 Dynamic Shape 与 Batch Inference(表格中均为 `Y`)。

---

## 【表格解读】

原文表格(逐字还原):

|    Model     |                        Config                        | Dynamic Shape | Batch Inference | Note  |
| :----------: | :--------------------------------------------------: | :-----------: | :-------------: | :---: |
|     SSD      |             `configs/ssd/ssd300_coco.py`             |       Y       |        Y        |       |
|     FSAF     |        `configs/fsaf/fsaf_r50_fpn_1x_coco.py`        |       Y       |        Y        |       |
|     FCOS     |   `configs/fcos/fcos_r50_caffe_fpn_4x4_1x_coco.py`   |       Y       |        Y        |       |
|    YOLOv3    |  `configs/yolo/yolov3_d53_mstrain-608_273e_coco.py`  |       Y       |        Y        |       |
|  RetinaNet   |   `configs/retinanet/retinanet_r50_fpn_1x_coco.py`   |       Y       |        Y        |       |
| Faster R-CNN | `configs/faster_rcnn/faster_rcnn_r50_fpn_1x_coco.py` |       Y       |        Y        |       |
|  Mask R-CNN  |   `configs/mask_rcnn/mask_rcnn_r50_fpn_1x_coco.py`   |       Y       |        Y        |       |

Notes(原文):*All models above are tested with Pytorch==1.6.0, onnx==1.7.0 and TensorRT-7.2.1.6.Ubuntu-16.04.x86_64-gnu.cuda-10.2.cudnn8.0*

逐行解读:

| 行 | 解读 |
|---|---|
| SSD | 单阶段检测器,配置文件 `ssd300_coco.py`;Dynamic Shape = Y、Batch Inference = Y;Note 列为空,表示无附加说明。 |
| FSAF | 无锚框(Anchor-Free)单阶段检测器,`fsaf_r50_fpn_1x_coco.py`;两项能力均支持;无附加说明。 |
| FCOS | 另一种 Anchor-Free 检测器,`fcos_r50_caffe_fpn_4x4_1x_coco.py`(使用了 caffe 风格预训练与 4x4 步距配置);两项能力均支持;无附加说明。 |
| YOLOv3 | 单阶段检测器,`yolov3_d53_mstrain-608_273e_coco.py`(输入 608、多尺度训练 273 epoch);两项能力均支持;无附加说明。 |
| RetinaNet | 单阶段检测器(带 Focal Loss),`retinanet_r50_fpn_1x_coco.py`,也是 Example 中所用的模型;两项能力均支持;无附加说明。 |
| Faster R-CNN | 两阶段检测器,`faster_rcnn_r50_fpn_1x_coco.py`;两项能力均支持;无附加说明。 |
| Mask R-CNN | 两阶段实例分割模型,`mask_rcnn_r50_fpn_1x_coco.py`;两项能力均支持;无附加说明。 |
| Notes | 声明上述 7 个模型的测试基线版本:Pytorch 1.6.0 + onnx 1.7.0 + TensorRT 7.2.1.6(Ubuntu 16.04、CUDA 10.2、cuDNN 8.0)。 |

---

## 【公式解读】

原文无数学公式。命令行调用形式如下,可视作"伪公式"以说明参数结构:

$$
\text{python tools/deployment/onnx2tensorrt.py } \underbrace{MODEL}_{\text{必填,ONNX 路径}} \; \underbrace{--trt-file\;TRT\_FILE}_{\text{输出引擎,默认 tmp.trt}} \; \underbrace{--input-img\;INPUT\_IMAGE\_PATH}_{\text{默认 demo/demo.jpg}} \; \underbrace{--shape\;IMAGE\_SHAPE}_{H\;W,\text{默认 }400\;600} \; \underbrace{--max-shape\;MAX\_IMAGE\_SHAPE}_{\text{默认同 --shape}}
$$

$$
\ldots\; \underbrace{--mean\;IMAGE\_MEAN}_{默认\;123.675\;116.28\;103.53} \; \underbrace{--std\;IMAGE\_STD}_{默认\;58.395\;57.12\;57.375} \; \underbrace{--dataset\;DATASET\_NAME}_{默认\;coco} \; \underbrace{--workspace-size\;WORKSPACE\_SIZE}_{默认\;1\;\text{GiB}} \; \underbrace{[--show]}_{默认\;False} \; \underbrace{[--verify]}_{默认\;False}
$$

符号含义:
- `MODEL`:必填项,指向一个 ONNX 模型文件路径。
- `--trt-file`:输出 `.trt` 引擎文件的保存路径。
- `--input-img`:`tracing` 时使用的样例图像路径,需与 `--shape` 尺寸一致。
- `--shape` / `--max-shape`:模型输入 H×W;`--max-shape` 控制 Dynamic Shape 上限。
- `--mean` / `--std`:三通道图像归一化的均值与标准差(按 BGR 通道顺序,与文档默认值一致)。
- `--dataset`:输入模型的训练数据集名称(默认 `coco`)。
- `--workspace-size`:构建 TensorRT 引擎时可用的 GPU 工作空间,单位 GiB。
- `--show` / `--verify`:开关型参数,分别控制"是否可视化"与"是否做 ONNX↔TensorRT 一致性验证"。

---

## 【关联】

- **前置工具**:`pytorch2onnx`(将 PyTorch 模型导出为 ONNX),是本文档的输入来源;若未先生成 ONNX,本文档的 `--trt-file` 转换无法启动。
- **依赖组件**:`mmcv-full` 中的 **ONNXRuntime custom ops** 与 **TensorRT plugins**,缺失将导致转换失败。
- **上游模型集合(支持矩阵)**:本文档表格列出的 7 个检测/分割模型(`SSD`/`FSAF`/`FCOS`/`YOLOv3`/`RetinaNet`/`Faster R-CNN`/`Mask R-CNN`),与仓库 `configs/` 下的同名配置文件一一对应。
- **下游评估(本文档链接)**:
  - [`pytorch2onnx.md#how-to-evaluate-the-exported-models`](pytorch2onnx.md#how-to-evaluate-the-exported-models):提供导出模型的精度评估方法。
  - [`pytorch2onnx.md#results-and-models`](pytorch2onnx.md#results-and-models):汇总了导出模型的精度/性能结果。
- **部署工具**:`tools/deplopyment/test.py`(原文拼写)用于评测转换后的 TensorRT 模型,实际精度/FPS 结果需跳转至 `pytorch2onnx.md` 查看。
- **版本耦合**:与 `Pytorch==1.6.0`、`onnx==1.7.0`、`TensorRT-7.2.1.6` 三个版本强耦合,环境不一致可能导致支持矩阵失效。

---

## 【使用方法】

**启用步骤(原文)**:

1. 源码安装 MMCV 与 MMDetection(参见 `get_started.html`)。
2. 安装带 **ONNXRuntime custom ops** 与 **TensorRT plugins** 的 `mmcv-full`。
3. 先用 `pytorch2onnx` 工具将 PyTorch 模型导出为 ONNX。
4. 调用 `tools/deployment/onnx2tensorrt.py` 完成 ONNX→TensorRT 转换。

**关键配置项(原文)**:

| 参数 | 默认值 | 作用 |
|---|---|---|
| `--trt-file` | `tmp.trt` | TensorRT 引擎输出路径 |
| `--input-img` | `demo/demo.jpg` | 用于 tracing 的输入图 |
| `--shape` | `400 600` | 输入 H×W |
| `--max-shape` | 同 `--shape` | Dynamic Shape 上限 |
| `--mean` | `123.675 116.28 103.53` | 输入归一化均值 |
| `--std` | `58.395 57.12 57.375` | 输入归一化标准差 |
| `--dataset` | `coco` | 数据集名称 |
| `--workspace-size` | `1` GiB | TensorRT 构建工作空间 |
| `--show` | `False` | 是否可视化模型输出 |
| `--verify` | `False` | 是否做 ONNXRuntime↔TensorRT 一致性验证 |
| `--to-rgb` | `True` | 是否将输入图转为 RGB |
| `--verbose` | `False` | 是否打印日志(调试用) |

**典型命令(原文 Example)**:

```bash
python tools/deployment/onnx2tensorrt.py \
    checkpoints/retinanet_r50_fpn_1x_coco.onnx \
    --trt-file checkpoints/retinanet_r50_fpn_1x_coco.trt \
    --input-img demo/demo.jpg \
    --shape 400 600 \
    --mean 123.675 116.28 103.53 \
    --std 58.395 57.12 57.375 \
    --show \
    --verify
```

**注意事项(原文)**:此功能为实验性,可能快速变动,需始终使用最新 `mmcv` 与 `mmdetection`;支持矩阵之外的模型不在文档服务范围内。
