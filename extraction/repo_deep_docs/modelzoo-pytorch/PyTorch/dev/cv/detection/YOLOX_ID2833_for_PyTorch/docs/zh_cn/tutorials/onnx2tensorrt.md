# 教程 9: ONNX 到 TensorRT 的模型转换（实验性支持）

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/dev/cv/detection/YOLOX_ID2833_for_PyTorch/docs/zh_cn/tutorials/onnx2tensorrt.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/dev/cv/detection/YOLOX_ID2833_for_PyTorch/docs/zh_cn/tutorials/onnx2tensorrt.md

# 一体化深度解读：MMDetection ONNX → TensorRT 转换指南

---

## 【定位】

这篇文档描述 MMDetection（在本仓具体为 `YOLOX_ID2833_for_PyTorch` 这条路径上的 MMDet 派生生态）将"已经导出的 ONNX 模型"再进一步转换为 NVIDIA TensorRT 推理引擎的实验性流程，涵盖前置依赖、转换命令、参数含义、评估方法与已验证可支持的模型清单。

---

## 【技术要点】

1. **三步式部署链**：先 `mmcv + mmdetection` 源码安装 → 再安装带 `ONNXRuntime 自定义操作` 与 `TensorRT 插件` 的 `mmcv-full` → 再用 `pytorch2onnx.py` 把 PyTorch 模型落盘成 ONNX，最后才进入本文档的 ONNX→TensorRT 转换。
2. **核心转换脚本**：`python tools/deployment/onnx2tensorrt.py`，必备四个位置参数 `${CONFIG}`（模型配置）、`${MODEL}`（ONNX 文件路径），并通过 `--trt-file` 指定输出 TensorRT 引擎路径。
3. **动态 Shape 三元组**：通过 `--shape`、`--min-shape`、`--max-shape` 三个开关同时给"固定尺寸 / 最小尺寸 / 最大尺寸"；缺省时 `--shape` 默认为 `400 600`，`--min-shape`、`--max-shape` 默认与 `--shape` 相同（即退化为静态 shape）。
4. **TensorRT 引擎构建参数**：`--workspace-size` 设置 GPU 工作空间大小，单位为 GiB，未指定时默认 `1` GiB。
5. **结果验证与可视化开关**：`--show`（展示模型输出，默认 `False`）、`--verify`（在 ONNXRuntime 与 TensorRT 之间交叉验证模型正确性，默认 `False`）、`--verbose`（打印日志消息，默认 `False`）三个调试/校验开关。
6. **已验证软硬件版本**（原文标注）："以上所有模型通过 Pytorch==1.6.0, onnx==1.7.0 与 TensorRT-7.2.1.6.Ubuntu-16.04.x86_64-gnu.cuda-10.2.cudnn8.0 测试"。

---

## 【关键机制与数据】

- **工作原理（原文描述）**：
  - 输入一张样本图（默认 `demo/demo.jpg`）用于"追踪（tracing）"与转换，模型在该图上被采样得到输入尺寸并喂给 TensorRT builder。
  - `min-shape`/`shape`/`max-shape` 三个值共同决定了 TensorRT 引擎的输入张量 profile，决定是否启用 dynamic shape 与允许的尺寸区间。
  - `--verify` 触发同一 ONNX 模型在 ONNXRuntime 与 TensorRT 两侧跑同一输入图并比较数值，从而核验转换正确性。
- **性能/规模相关数字（原文给出）**：
  - 输入 shape 默认 `400 600`（H W）。
  - workspace 默认 `1` GiB。
  - TRT 输出文件缺省名 `tmp.trt`（即未指定 `--trt-file` 时的回退值）。
- **数据流（原文可推导）**：`PyTorch .pth` →（经 `pytorch2onnx.py`，**不在本文档内**）→ `*.onnx` →（本文档 `onnx2tensorrt.py`）→ `*.trt` 引擎 →（`tools/deplopyment/test.py`，**评估章节引用**）→ 在 COCO 等数据集上做精度/速度评估。
- **生态警示（原文）**：该功能是实验性的，会快速变化；列表外模型不在官方支持范围，需自行调试。

---

## 【表格解读】

原文表格（逐字还原）：

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

注意（原文紧跟表格后）:

- *以上所有模型通过 Pytorch==1.6.0, onnx==1.7.0 与 TensorRT-7.2.1.6.Ubuntu-16.04.x86_64-gnu.cuda-10.2.cudnn8.0 测试*

逐行解读：

- **列含义**：`Model` 是检测器名；`Config` 是仓库内对应训练/推理配置文件的相对路径；`Dynamic Shape` 与 `Batch Inference` 两列均为 `Y`，意味着这十个模型都已在官方测试矩阵里同时通过"动态输入尺寸"与"批推理（batch > 1）"两项 TensorRT 适配验证；`Note` 列在本表中全部留空，表示官方未就这些模型追加额外注意点。
- **逐行细节**：
  1. **SSD** — 单阶段检测器，对应 `configs/ssd/ssd300_coco.py`，是表中唯一非 FPN 架构的 anchor-based 单阶段模型。
  2. **FSAF — `configs/fsaf/fsaf_r50_fpn_1x_coco.py`**：Feature Selective Anchor-Free，基于 ResNet-50 + FPN 的无锚单阶段模型。
  3. **FCOS — `configs/fcos/fcos_r50_caffe_fpn_4x4_1x_coco.py`**：典型无锚单阶段检测器，`caffe` 前缀暗示沿用 Caffe-style 预训练权重的预处理。
  4. **YOLOv3 — `configs/yolo/yolov3_d53_mstrain-608_273e_coco.py`**：`608` 为推理边长，`273e` 为 273 个 epoch 的多尺度训练配置。
  5. **RetinaNet — `configs/retinanet/retinanet_r50_fpn_1x_coco.py`**：Focal Loss 单阶段检测器，是文档"用法示例"中唯一被演示完整命令的模型。
  6. **Faster R-CNN — `configs/faster_rcnn/faster_rcnn_r50_fpn_1x_coco.py`**：经典两阶段 anchor-based 检测器。
  7. **Cascade R-CNN — `configs/cascade_rcnn/cascade_rcnn_r50_fpn_1x_coco.py`**：多阶段级联检测器，验证了多 RPNHead/H-head 的串联在 TensorRT 上可构建。
  8. **Mask R-CNN — `configs/mask_rcnn/mask_rcnn_r50_fpn_1x_coco.py`**：在 Faster R-CNN 上叠加实例分割分支，证明分割 head 也能通过 TensorRT 插件路径转换。
  9. **Cascade Mask R-CNN — `configs/cascade_rcnn/cascade_mask_rcnn_r50_fpn_1x_coco.py`**：级联检测 + 实例分割，是表中结构最重的模型。
  10. **PointRend — `configs/point_rend/point_rend_r50_caffe_fpn_mstrain_1x_coco.py`**：基于点采样的精细分割/检测模型，验证了非规则的"点采样 + 插值"算子已被 TensorRT 插件覆盖。
- **底部"注意"行**：原文用斜体给出唯一一组实测版本号组合，作为"复用本文表格结论"的硬性环境约束——PyTorch 1.6.0、ONNX 1.7.0、TensorRT 7.2.1.6（Ubuntu 16.04、CUDA 10.2、cuDNN 8.0）。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **上游依赖** — 本文档假设 ONNX 模型已经存在，因此强依赖：
  - [pytorch2onnx.md#how-to-evaluate-the-exported-models](pytorch2onnx.md#how-to-evaluate-the-exported-models)：用于把 PyTorch `.pth` 转为 `.onnx` 的前序脚本（**先决条件第 3 条明确引用**）；同时"如何评估导出的模型"一节直接指向该链接，说明 TRT 模型评估流程与 ONNX 模型评估流程共用同一个 `tools/deplopyment/test.py`。
  - [pytorch2onnx.md#results-and-models](pytorch2onnx.md#results-and-models)：本文档的"评估导出的模型"章节第二个内部链接指向该锚点，用以查阅各检测器导出后可达到的精度/速度基线，从而判断 TRT 转换后是否出现明显精度回退。
- **替代方案** — 文档开头以引用块形式推荐 [`MMDeploy`](https://mmdeploy.readthedocs.io/) 作为"新"的部署方案，可视为本文档所述流程的官方长期替代品。
- **底层依赖** — "先决条件"中链接的 `ONNXRuntime in mmcv` 与 `TensorRT plugin in mmcv` 决定了 ONNX 端的自定义算子与 TRT 端的自定义算子都能被同一套 MMDet 模型使用；这两条 mmcv 文档也是本文档转换脚本能跑通的"算子库"前提。
- **横向工具** — "如何评估导出的模型"小节提到评估入口 `tools/deplopyment/test.py`（原文写作 `tools/deplolyment/test.py`，疑似 typo），是与本文 `onnx2tensorrt.py` 平级的另一部署工具脚本，作用是对最终 `.trt` 引擎在 COCO 等数据集上做精度/吞吐评估。

---

## 【使用方法】

原文给出两条可直接执行的命令，参数含义已在"技术要点"中列出，此处仅按原文复述：

**通用调用模板**：

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

**RetinaNet 完整示例**：

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

**配置项默认值汇总（原文给出）**：

| 配置项 | 缺省值 / 行为 |
| :--- | :--- |
| `config` | 模型配置文件路径（必填） |
| `model` | ONNX 模型文件路径（必填） |
| `--trt-file` | 未指定 → `tmp.trt` |
| `--input-img` | 未指定 → `demo/demo.jpg` |
| `--shape` | 未指定 → `400 600`（H W） |
| `--min-shape` | 未指定 → 与 `--shape` 相同 |
| `--max-shape` | 未指定 → 与 `--shape` 相同 |
| `--workspace-size` | 未指定 → `1` GiB |
| `--show` | 未指定 → `False` |
| `--verify` | 未指定 → `False` |
| `--verbose` | 未指定 → `False` |

**启用与评估流程**：

1. 准备阶段：源码安装 `mmcv` + `mmdetection`，安装带 ONNXRuntime/TensorRT 插件的 `mmcv-full`，并先跑通 `pytorch2onnx.py` 得到 `.onnx`。
2. 转换阶段：按"通用调用模板"或"RetinaNet 示例"执行 `onnx2tensorrt.py`，得到 `.trt` 引擎文件。
3. 评估阶段：使用 `tools/deplopyment/test.py`（原文写法）评估 TRT 引擎，参考 [pytorch2onnx.md#how-to-evaluate-the-exported-models](pytorch2onnx.md#how-to-evaluate-the-exported-models) 的调用方式，并以 [pytorch2onnx.md#results-and-models](pytorch2onnx.md#results-and-models) 给出的精度/速度作为对照基线。
