# Tutorial 9: ONNX to TensorRT (Experimental)

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/dev/cv/detection/YOLOX_ID2833_for_PyTorch/docs/en/tutorials/onnx2tensorrt.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/dev/cv/detection/YOLOX_ID2833_for_PyTorch/docs/en/tutorials/onnx2tensorrt.md

# 一体化深度解读: ONNX to TensorRT (Experimental) 教程

---

## 【定位】

本文档是 MMDetection 部署教程系列的第 9 篇, 解决**如何将已经通过 `pytorch2onnx` 导出的 ONNX 检测模型进一步转换为 NVIDIA TensorRT 引擎文件**, 并提供导出后模型的精度验证方法以及受支持模型的清单, 同时提醒该功能仍处于 Experimental 阶段。

---

## 【技术要点】

1. **三阶段依赖链**: 整个 ONNX→TensorRT 流水线需要三步前置准备 ——
   - 源码安装 MMCV 与 MMDetection (见 `get_started.md`);
   - 安装带 ONNXRuntime custom ops 与 TensorRT plugins 的 `mmcv-full`;
   - 先用 `pytorch2onnx` 工具将 PyTorch 模型导出为 ONNX。

2. **核心转换脚本**: `python tools/deployment/onnx2tensorrt.py` 接受 `${CONFIG}` 与 `${MODEL}` 两个位置参数, 加上若干可选开关完成 ONNX→TensorRT 的转换与可选的精度校验、可视化。

3. **关键参数与默认值** (原文):
   - `--trt-file`: 输出 TensorRT engine 路径, 默认 `tmp.trt`;
   - `--input-img`: 追踪与转换用的输入图像, 默认 `demo/demo.jpg`;
   - `--shape`: 模型输入高×宽, 默认 `400 600`;
   - `--min-shape` / `--max-shape`: 动态 shape 上下界, 默认同 `--shape`;
   - `--workspace-size`: TensorRT 构建期 GPU workspace 大小 (单位 GiB), 默认 `1` GiB;
   - `--show`: 是否可视化输出, 默认 `False`;
   - `--verify`: 是否在 ONNXRuntime 与 TensorRT 间做精度对比, 默认 `False`;
   - `--verbose`: 是否打印日志, 默认 `False`。

4. **导出后评估工具**: `tools/deplopyment/test.py` 用于评估 TensorRT 模型, 详细用法通过内部链接指向 `pytorch2onnx.md` 中的 "How to evaluate the exported models" 与 "Results and Models" 两节 (注意原文工具路径中 `deplopyment` 为拼写错误, 但原文如此)。

5. **支持矩阵**: 共有 10 个检测模型被保证可成功转换, 全部支持 Dynamic Shape 与 Batch Inference (清单见下节表格)。

6. **版本基线与平台**: 全部模型均在原文注明的环境中测试通过 ——
   - PyTorch 1.6.0
   - onnx 1.7.0
   - TensorRT-7.2.1.6.Ubuntu-16.04.x86_64-gnu.cuda-10.2.cudnn8.0

---

## 【关键机制与数据】

**工作原理 (数据流)**

整条数据流为 `PyTorch model → ONNX (pytorch2onnx) → TensorRT Engine (onnx2tensorrt) → Inference/Verification`:

1. 用户先用 `pytorch2onnx.py` 配合一张样例图像 (`--input-img`) 追踪模型并产出 `.onnx`;
2. `onnx2tensorrt.py` 读取该 `.onnx` 与对应 config, 调用 TensorRT 的 Builder/Network 解析器, 按 `--shape` 或 `--min-shape/--max-shape` 设定输入尺寸范围, 在 `--workspace-size` GiB 的 GPU 显存内完成 engine 优化与序列化, 写出 `--trt-file`;
3. `--verify` 开启时, 会同时跑 ONNXRuntime 与 TensorRT 两路推理, 对结果做对比, 用以确认转换无精度损失。

**动态 Shape 与 Batch Inference**

对表中 10 个模型, **Dynamic Shape** 与 **Batch Inference** 两列均为 Y, 表明通过 `--min-shape` / `--max-shape` 可启用动态尺寸推理, 同时 batch 维度也可变; 若不显式给出上下界, 则退化为固定 shape (即 `--shape` 单一值)。

**性能 / 显存相关参数 (原文)**

原文未给出实测 FPS、mAP 或延迟等数字; 唯一与性能/显存直接相关的参数是 `--workspace-size`, 单位 GiB, 默认 `1`, 该值决定 TensorRT 在构建 engine 时可申请的临时显存上限。

---

## 【表格解读】

原文提供了一张受支持模型的清单, 逐字还原如下:

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
| Cascade Mask R-CNN |   `configs/cascade_rcnn/cascade_mask_rrcnn_r50_fpn_1x_coco.py`   |       Y       |        Y        |      |
|     PointRend      | `configs/point_rend/point_rend_r50_caffe_fpn_mstrain_1x_coco.py` |       Y       |        Y        |      |

**逐行解读:**

- **Model 列**列出 10 个检测模型, 覆盖 one-stage (SSD、RetinaNet、FCOS、FSAF、YOLOv3)、two-stage (Faster R-CNN、Cascade R-CNN、Mask R-CNN、Cascade Mask R-CNN) 以及 instance segmentation/特殊头 (PointRend) 三大类别。
- **Config 列**给出每个模型在仓库中的具体 config 路径, 是 `onnx2tensorrt.py` 第一个位置参数 `${CONFIG}` 的取值参考。
- **Dynamic Shape 列**全部为 `Y`, 说明所有 10 个模型都已验证在 TensorRT 动态 shape 下可构建 engine, 可结合 `--min-shape` / `--max-shape` 使用。
- **Batch Inference 列**全部为 `Y`, 说明这些模型都支持 batch 维度可变的推理。
- **Note 列**在原表中全部为空, 没有任何附加注释。
- **Notes (表下注释)**: 表格正下方注明上述全部模型均在 `Pytorch==1.6.0, onnx==1.7.0, TensorRT-7.2.1.6.Ubuntu-16.04.x86_64-gnu.cuda-10.2.cudnn8.0` 的固定环境下测试通过, 该环境锁定了使用者在自验时需对齐的版本基线。

---

## 【公式解读】

原文无公式。

---

## 【关联】

**与上游教程 (PyTorch → ONNX) 的衔接:**

- 整条链路的 **上游** 是 `pytorch2onnx.md`: 必须先用 `tools/deployment/pytorch2onnx.py` 将 PyTorch 模型导出为 ONNX, 本文文档才可读取并继续转换。文末内部链接 `pytorch2onnx.md#how-to-evaluate-the-exported-models` 与 `pytorch2onnx.md#results-and-models`, 指向评估流程与模型精度/速度结果列表 — 本文并未自建评估文档, 而是复用 pytorch2onnx 教程的对应小节。

**与底层运行时的依赖:**

- `mmcv-full` 必须同时具备 ONNXRuntime custom ops 与 TensorRT plugins, 因此文档明确指向 [ONNXRuntime in mmcv](https://mmcv.readthedocs.io/en/latest/deployment/onnxruntime_op.html) 与 [TensorRT plugin in mmcv](https://github.com/open-mmlab/mmcv/blob/master/docs/en/deployment/tensorrt_plugin.md/) 两个外部子文档。

**与替代/更高级部署方案的并列关系:**

- 文档顶部横幅推荐 [MMDeploy](https://mmdeploy.readthedocs.io/) 作为新的统一部署方案, 表明本文所描述的 `onnx2tensorrt.py` 是 "Experimental" 的临时路径, 最终用户被建议迁移到 MMDeploy。

**与基础安装的关联:**

- 安装阶段指向 `get_started.md` (源码安装 MMCV 与 MMDetection), 这是阅读本文的前置条件之一。

**与 `tools/deployment/` 目录其他脚本的关系:**

- `tools/deployment/onnx2tensorrt.py` (本文主角) ↔ `tools/deployment/pytorch2onnx.py` (上游) ↔ `tools/deplopyment/test.py` (下游评估) 三者共同构成 MMDetection 的部署脚本套件。

---

## 【使用方法】

**完整转换命令模板 (原文):**

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
    --verify
```

**原文给出的可直接运行的示例 (以 RetinaNet 为例):**

```bash
python tools/deployment/onnx2tensorrt.py \
    configs/retinanet/retinanet_r50_fpn_1x_coco.py \
    checkpoints/retinanet_r50_fpn_1x_coco.onnx \
    --trt-file checkpoints/retinanet_r50_fpn_1x_coco.trt \
    --input-img demo/demo.jpg \
    --shape 400 600 \
    --show \
    --verify
```

**导出后评估 (原文):**

使用 `tools/deplopyment/test.py` 评估生成的 TensorRT 模型; 详细用法请跳转至 `pytorch2onnx.md` 的 "How to evaluate the exported models" 与 "Results and Models" 两节 (原文未在本文件内重复参数说明)。

**环境与版本锁定 (原文):**

文档强调由于该功能仍为 Experimental, 推荐始终使用最新版本的 `mmcv` 与 `mmdetection`; 而表中所有模型均在 `Pytorch==1.6.0, onnx==1.7.0, TensorRT-7.2.1.6.Ubuntu-16.04.x86_64-gnu.cuda-10.2.cudnn8.0` 这一固定组合下验证通过, 偏离此基线可能出现未覆盖问题。
