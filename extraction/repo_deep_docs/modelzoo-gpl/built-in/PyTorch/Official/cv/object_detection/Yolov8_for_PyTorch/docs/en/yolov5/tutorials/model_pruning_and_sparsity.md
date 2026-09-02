# model_pruning_and_sparsity

> 仓 `modelzoo-gpl` · 路径 `built-in/PyTorch/Official/cv/object_detection/Yolov8_for_PyTorch/docs/en/yolov5/tutorials/model_pruning_and_sparsity.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-gpl/built-in/PyTorch/Official/cv/object_detection/Yolov8_for_PyTorch/docs/en/yolov5/tutorials/model_pruning_and_sparsity.md

# 一体化深度解读：YOLOv5 模型剪枝与稀疏化指南

## 【定位】

这篇文档解决"如何在 YOLOv5 模型上应用 **sparsity-based pruning**（稀疏化剪枝）以压缩 nn.Conv2d 层的权重参数"的问题，并通过对 YOLOv5x 在 COCO val2017 上 0.3 稀疏度前后的对照测试，量化展示了该剪枝对精度与推理速度的影响。

---

## 【技术要点】

1. **环境前提**：Python >= 3.8.0、PyTorch >= 1.8；通过 `git clone https://github.com/ultralytics/yolov5` 与 `pip install -r requirements.txt` 完成仓库克隆与依赖安装，模型与数据集自动从最新 YOLOv5 release 下载。
2. **基线测试命令**：`python val.py --weights yolov5x.pt --data coco.yaml --img 640 --half`，在 COCO val2017、图像尺寸 640 像素下评估 YOLOv5x（最准最大模型，另可选 yolov5s/m/l 或自训 checkpoint）。
3. **剪枝方式**：通过仓库内置的 `torch_utils.prune()` 函数，将 YOLOv5x 设为 **0.3 global sparsity**（全局 30% 稀疏度），并对应修改 `val.py`；剪枝对象是 `nn.Conv2d` 层的权重参数。
4. **指标体系**：精度同时给出 PyCOCOTools 的 mAP（AP@[.5:.95]、AP@.5、AP@.75，以及 small/medium/large 三个尺度）和 val.py 内置的 P/R/mAP@.5/mAP@.5:.95；速度分别报告 pre-process、inference、NMS 三段时延。
5. **核心结论**：30% 稀疏度下 inference time **基本不变**（pre-process 0.1 ms、inference 5.2 ms、NMS 1.7 ms），但 AP 与 AR 出现轻微下降（base mAP 0.507 → prune mAP 0.489）。
6. **运行环境**：提供 Paperspace/Colab/Kaggle 免费 GPU、Google Cloud、AWS、Azure、Docker 等已预装 CUDA/CUDNN/Python/PyTorch 的开箱即用环境。

---

## 【关键机制与数据】

**工作原理**：YOLOv5 的 `torch_utils.prune()` 对 `nn.Conv2d` 层按全局比例将若干权重直接置零，从而引入 **结构化/非结构化稀疏**（文中强调"30% of the model's weight parameters in `nn.Conv2d` layers are equal to 0"）。由于参数张量并未被真正减小（Model Summary 仍是 444 层、86705005 参数），这是一种 **weight-level sparsity**——理论上为后续稀疏矩阵加速库留出加速空间，但在本测试的稠密推理路径上**推理时延未见变化**。

**数据流**：

```
yolov5x.pt (pretrained)
    │
    ├─ 路径 A：val.py 直接推理  ──► runs/val/exp
    │       ↓
    │     base mAP / base speed
    │
    └─ 路径 B：torch_utils.prune() 设为 0.3 sparsity → val.py
            ↓
          runs/val/exp3
            ↓
          prune mAP（精度略降，speed 不变）
```

**性能数据（原文实测）**：

> **原文：基线 YOLOv5x (val2017, 640 px, half)**
> - Model Summary：444 layers, 86 705 005 parameters, 0 gradients
> - P=0.732, R=0.628, mAP@.5=0.683, mAP@.5:.95=0.496
> - **base speed**：0.1 ms pre-process, 5.2 ms inference, 1.7 ms NMS per image at shape (32, 3, 640, 640)
> - **base mAP** (AP@[.5:.95, all, maxDets=100]) = **0.507**

> **原文：剪枝后 YOLOv5x (0.3 global sparsity)**
> - Model Summary：444 layers, 86 705 005 parameters, 0 gradients（参数总量未变）
> - P=0.724, R=0.614, mAP@.5=0.671, mAP@.5:.95=0.478
> - **prune speed**：0.1 ms pre-process, 5.2 ms inference, 1.7 ms NMS per image at shape (32, 3, 640, 640)（**与基线一致**）
> - **prune mAP** (AP@[.5:.95, all, maxDets=100]) = **0.489**（较基线下降 0.018）

---

## 【表格解读】

原文未给出显式的 markdown 表格，但先后给出了 **基线**与 **0.3 sparsity 剪枝**两组同名指标。下面将两组数据并排"逐字还原"成一张对照表，方便横向阅读。

### 表 1：YOLOv5x / COCO val2017 / 640 px — 剪枝前 vs 0.3 稀疏度

| 指标 | 基线（原文 `base`） | 0.3 sparsity（原文 `prune`） |
|---|---|---|
| **模型规格** | YOLOv5x, 444 layers, 86 705 005 parameters, 0 gradients | YOLOv5x, 444 layers, 86 705 005 parameters, 0 gradients |
| **稀疏度说明** | — | Pruning model... 0.3 global sparsity |
| **P** | 0.732 | 0.724 |
| **R** | 0.628 | 0.614 |
| **mAP@.5** | 0.683 | 0.671 |
| **mAP@.5:.95** | 0.496 | 0.478 |
| **Speed — pre-process** | 0.1 ms | 0.1 ms |
| **Speed — inference** | 5.2 ms | 5.2 ms |
| **Speed — NMS** | 1.7 ms | 1.7 ms |
| **Speed — batch shape** | (32, 3, 640, 640) | (32, 3, 640, 640) |
| **AP @[ IoU=0.50:0.95 \| area=all \| maxDets=100 ]** | 0.507 | 0.489 |
| **AP @[ IoU=0.50 \| area=all \| maxDets=100 ]** | 0.689 | 0.677 |
| **AP @[ IoU=0.75 \| area=all \| maxDets=100 ]** | 0.552 | 0.537 |
| **AP @[ IoU=0.50:0.95 \| area=small \| maxDets=100 ]** | 0.345 | 0.334 |
| **AP @[ IoU=0.50:0.95 \| area=medium \| maxDets=100 ]** | 0.559 | 0.542 |
| **AP @[ IoU=0.50:0.95 \| area=large \| maxDets=100 ]** | 0.652 | 0.635 |
| **AR @[ IoU=0.50:0.95 \| area=all \| maxDets=1 ]** | 0.381 | 0.370 |
| **AR @[ IoU=0.50:0.95 \| area=all \| maxDets=10 ]** | 0.630 | 0.612 |
| **AR @[ IoU=0.50:0.95 \| area=all \| maxDets=100 ]** | 0.682 | 0.664 |
| **AR @[ IoU=0.50:0.95 \| area=small \| maxDets=100 ]** | 0.526 | 0.496 |
| **AR @[ IoU=0.50:0.95 \| area=medium \| maxDets=100 ]** | 0.731 | 0.722 |
| **AR @[ IoU=0.50:0.95 \| area=large \| maxDets=100 ]** | 0.829 | 0.803 |

**逐行解读**：
- **模型规格**：剪枝未改变 `parameters` 总数（仍 86 705 005），印证剪枝是 *置零* 而非 *删除通道*；参数统计按惯例仍报告全量。
- **稀疏度说明**：剪枝输出中明确打印 `0.3 global sparsity`，说明剪枝比例是全局统一的，未对不同层做差异化处理。
- **P / R / mAP@.5 / mAP@.5:.95**：四项指标均小幅下降，分别 −0.008 / −0.014 / −0.012 / −0.018，跌幅约 1% 量级。
- **Speed**：pre-process / inference / NMS 三段时间在两份输出里完全一致，呼应原文"**Inference time is essentially unchanged**"。
- **AP 子项**：IoU=.50:.95 下降幅度最大（−0.018），IoU=.50、IoU=.75 也各降约 0.012–0.015；small / medium / large 三尺度均下降，**large 下降 0.017** 最明显。
- **AR 子项**：AR@maxDets=100（综合检索能力）从 0.682 → 0.664；各尺度 AR 同样下滑，small 从 0.526 → 0.496 是相对降幅较大的一个。
- **整体结论**：在 0.3 sparsity 下模型出现轻微但普遍性的精度回退，速度却未获益——按原文措辞，本测试主要演示了 **如何做稀疏化**，而非保证稠密推理下提速。

---

## 【公式解读】

原文无显式公式 / LaTeX / 伪代码。

- 没有给出 sparsity 的数学定义，仅以"30% of the model's weight parameters in `nn.Conv2d` layers are equal to 0"做自然语言描述，可理解为全局权重稀疏比例。
- 没有给出 mAP、AP、AR 的具体计算式，文中仅以 COCO/PyCOCOTools 标准输出格式罗列数值。

故：**原文无公式**。

---

## 【关联】

依据文末"Supported Environments"段，本指南与以下 4 份**上游/平行教程**存在显式相对路径链接，构成一条"本地 → 云端 → 容器"的环境支撑链：

1. **[`../environments/google_cloud_quickstart_tutorial.md`](../environments/google_cloud_quickstart_tutorial.md)** — Google Cloud (GCP) 快速上手教程。本指南所演示的剪枝测试可在 GCP 环境复现；上文中"GCP Quickstart Guide"指代此文。
2. **[`../environments/aws_quickstart_tutorial.md`](../environments/aws_quickstart_tutorial.md)** — AWS 快速上手教程。本指南剪枝命令可在 AWS 提供的 GPU 实例上执行；上文中"Amazon"一栏对应此文。
3. **[`../environments/azureml_quickstart_tutorial.md`](../environments/azureml_quickstart_tutorial.md)** — AzureML 快速上手教程。本指南的 `val.py` + `torch_utils.prune()` 流程可在 Azure ML 上运行；上文中"Azure"一栏对应此文。
4. **[`../environments/docker_image_quickstart_tutorial.md`](../environments/docker_image_quickstart_tutorial.md)** — Docker 镜像快速上手教程。本指南依赖的 CUDA/CUDNN/Python/PyTorch 可通过 Ultralytics 官方 Docker 镜像一次性获得；上文中"Docker Quickstart Guide"对应此文。

**上下游脚本关系**（依据文末 CI Project Status 段提及的仓库脚本）：
- [`train.py`](https://github.com/ultralytics/yolov5/blob/master/train.py) — 训练入口；剪枝可作用于自训 checkpoint（`./weights/best.pt`）。
- [`val.py`](https://github.com/ultralytics/yolov5/blob/master/val.py) — 评估入口；本指南在 `val.py` 中嵌入 `torch_utils.prune()` 来触发稀疏化推理。
- [`detect.py`](https://github.com/ultralytics/yolov5/blob/master/detect.py) — 推理入口；与本指南无直接引用，但同属 CI 覆盖。
- [`export.py`](https://github.com/ultralytics/yolov5/blob/master/export.py) — 模型导出；稀疏模型可经此导出至 ONNX/TorchScript 等格式。
- [`benchmarks.py`](https://github.com/ultralytics/yolov5/blob/master/benchmarks.py) — 基准测试；可被用于对比稀疏前后的吞吐/时延（但本指南未实际使用）。

**横向功能关系**：与 README 中的 [pretrained checkpoints 表](https://github.com/ultralytics/yolov5#pretrained-checkpoints) 配合，给出 yolov5s/m/l/x 的尺寸—精度—速度基线，本指南即以"最大最准"的 yolov5x 作为剪枝对象。

---

## 【使用方法】

> 以下命令/参数均**原文逐字保留**，未补充未提及字段。

**1. 准备环境**
```bash
git clone https://github.com/ultralytics/yolov5  # clone
cd yolov5
pip install -r requirements.txt  # install
```
要求 Python >= 3.8.0、PyTorch >= 1.8。

**2. 跑基线（未剪枝）**
```bash
python val.py --weights yolov5x.pt --data coco.yaml --img 640 --half
```
可选权重：`yolov5s.pt`、`yolov5m.pt`、`yolov5l.pt`、`yolov5x.pt`（最大最准），或自定义 `./weights/best.pt`。

**3. 跑剪枝（0.3 global sparsity）**
- 通过 `torch_utils.prune()` 命令触发；
- 需要 **更新 `val.py`** 以调用该剪枝函数，目标 0.3 sparsity；
- 推理时打印一行：`Pruning model... 0.3 global sparsity`。
- 命令本身原文以代码修改点（截图）形式给出，未给出完整命令行；可参照 val.py 基线命令、保留相同 `--weights yolov5x.pt --data coco.yaml --img 640` 等参数，并在脚本内启用 prune。

**4. 关键配置项说明（原文有）**
- `sparsity` = **0.3**：全局稀疏度，对应 30% 的 `nn.Conv2d` 权重被置零。
- `--half`：基线命令中的 FP16 推理开关。
- `--img 640`：输入图像尺寸。
- `--data coco.yaml`：数据集配置。

**5. 结果落盘位置（原文有）**
- 基线：`Results saved to runs/val/exp`
- 剪枝：`Results saved to runs/val/exp3`
- 中间 JSON：`runs/val/exp2/yolov5x_predictions.json`（基线）、`runs/val/exp3/yolov5x_predictions.json`（剪枝）。

**6. 运行环境选择（原文有）**
通过 Supported Environments 列出的 Paperspace / Colab / Kaggle 免费 GPU，或 GCP / AWS / Azure / Docker 任一环境跑通以上两条 `val.py` 命令即可完整复现本文基线—剪枝对照测试。
