# model_ensembling

> 仓 `modelzoo-gpl` · 路径 `built-in/PyTorch/Official/cv/object_detection/Yolov8_for_PyTorch/docs/en/yolov5/tutorials/model_ensembling.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-gpl/built-in/PyTorch/Official/cv/object_detection/Yolov8_for_PyTorch/docs/en/yolov5/tutorials/model_ensembling.md

# YOLOv5 Model Ensembling 文档深度解读

---

## 【定位】

本指南描述了 YOLOv5 在测试（val.py）与推理（detect.py）阶段如何通过 **模型集成（Model Ensembling）** 聚合多个预训练模型的预测结果，以提升 mAP 与 Recall，得到比单一模型更准确的检测输出。

---

## 【技术要点】

1. **集成机制**：通过在 `--weights` 参数后追加多个 `.pt` 模型文件（如 `yolov5x.pt yolov5l6.pt`），`val.py` 与 `detect.py` 会自动创建集成（`Ensemble created with [...]`）并聚合多模型的推理结果。
2. **环境前置**：需要 `Python>=3.8.0`、`PyTorch>=1.8`，并 `git clone` ultralytics/yolov5 仓库后 `pip install -r requirements.txt`；模型与数据集自动从最新 YOLOv5 release 下载。
3. **基线测试（单模型）**：使用 `yolov5x.pt`（最大、最准确模型）在 COCO val2017、`img=640`、`--half`（FP16 推理）下进行单模型基线评测，命令为 `python val.py --weights yolov5x.pt --data coco.yaml --img 640 --half`。
4. **集成测试**：以 `yolov5x.pt + yolov5l6.pt` 双模型组合为例，命令为 `python val.py --weights yolov5x.pt yolov5l6.pt --data coco.yaml --img 640 --half`，通过对比展示集成收益。
5. **集成推理**：命令为 `python detect.py --weights yolov5x.pt yolov5l6.pt --img 640 --source data/images`，对 `bus.jpg` 检出 4 persons、1 bus、1 tie，对 `zidane.jpg` 检出 3 persons、2 ties。
6. **多尺度模型选择**：可选用 `yolov5s/m/l/x.pt` 及自定义 `./weights/best.pt`，不同尺寸/架构模型组合即"多样化（diverse and independent）"以提高集成效果，来源为 Wikipedia Ensemble_learning 词条引用。

---

## 【关键机制与数据】

### 工作原理
- **集成创建**：检测到 `--weights` 含多个模型时，框架逐个加载并执行 `Fusing layers... Model Summary: ...`（如 yolov5x：476 层、87730285 参数；yolov5l6：501 层、77218620 参数），最后打印 `Ensemble created with [...]`。
- **推理聚合**：在测试时对 5000 张 val2017 图像、36335 个标签进行 FP16 推理；推理时 NMS（Non-Maximum Suppression）对多模型输出做合并，文中给出的 NMS 耗时从 1.4ms/image（基线）→2.0ms/image（集成）。
- **数据流**：单模型 → 单次前向 → NMS；集成 → 多模型前向 → 结果聚合 → NMS → 最终预测。

### 原文性能数据（YOLOv5 v5.0-267-g6a3ee7c，torch 1.9.0+cu102，Tesla P100-PCIE-16GB，COCO val2017，imgsz=640，FP16）

**原文（基线 `yolov5x.pt` 单独）：**
- 总体 P=0.746 / R=0.626 / mAP@0.5=0.68 / mAP@0.5:0.95=0.49（val.py 行输出）
- AP@[IoU=0.50:0.95, all, maxDets=100] = **0.504**（原文标 `<--- baseline mAP`）
- AR@[IoU=0.50:0.95, all, maxDets=100] = **0.681**（原文标 `<--- baseline mAR`）
- Speed: 0.1ms pre-process, **22.4ms inference**, 1.4ms NMS/image at shape (32, 3, 640, 640)

**原文（集成 `yolov5x.pt + yolov5l6.pt`）：**
- 总体 P=0.747 / R=0.637 / mAP@0.5=0.692 / mAP@0.5:0.95=0.502
- AP@[IoU=0.50:0.95, all, maxDets=100] = **0.515**（原文标 `<--- ensemble mAP`）
- AR@[IoU=0.50:0.95, all, maxDets=100] = **0.689**（原文标 `<--- ensemble mAR`）
- Speed: 0.1ms pre-process, **39.5ms inference**, 2.0ms NMS/image at shape (32, 3, 640, 640)
- 注意：`iou_thres` 在集成测试中从基线的 0.65 变为 **0.6**（来自 `val:` 输出行原文）

**对比原文标注**：基线 mAP 0.504 → 集成 mAP 0.515（+0.011）；基线 mAR 0.681 → 集成 mAR 0.689（+0.008）；代价是推理耗时从 22.4ms 增至 39.5ms（约 1.76 倍）。

---

## 【表格解读】

**原文无表格**。文档以 `val.py` / `pycocotools` 文本输出形式呈现指标。为便于逐项对比，将原文 COCO 评测输出逐字还原为下表（仅原文出现的行/值）：

| 指标 (Metric) | 基线 `yolov5x.pt` | 集成 `yolov5x.pt + yolov5l6.pt` |
|---|---|---|
| P (val.py 行) | 0.746 | 0.747 |
| R (val.py 行) | 0.626 | 0.637 |
| mAP@0.5 (val.py 行) | 0.68 | 0.692 |
| mAP@0.5:0.95 (val.py 行) | 0.49 | 0.502 |
| AP @ IoU=0.50:0.95, all, maxDets=100 | 0.504（baseline mAP） | 0.515（ensemble mAP） |
| AP @ IoU=0.50, all, maxDets=100 | 0.688 | 0.699 |
| AP @ IoU=0.75, all, maxDets=100 | 0.546 | 0.557 |
| AP @ IoU=0.50:0.95, small, maxDets=100 | 0.351 | 0.356 |
| AP @ IoU=0.50:0.95, medium, maxDets=100 | 0.551 | 0.563 |
| AP @ IoU=0.50:0.95, large, maxDets=100 | 0.644 | 0.668 |
| AR @ IoU=0.50:0.95, all, maxDets=1 | 0.382 | 0.387 |
| AR @ IoU=0.50:0.95, all, maxDets=10 | 0.628 | 0.638 |
| AR @ IoU=0.50:0.95, all, maxDets=100 | 0.681（baseline mAR） | 0.689（ensemble mAR） |
| AR @ IoU=0.50:0.95, small, maxDets=100 | 0.524 | 0.526 |
| AR @ IoU=0.50:0.95, medium, maxDets=100 | 0.735 | 0.743 |
| AR @ IoU=0.50:0.95, large, maxDets=100 | 0.826 | 0.844 |
| pre-process 速度 | 0.1ms/image | 0.1ms/image |
| inference 速度 | 22.4ms/image | 39.5ms/image |
| NMS 速度 | 1.4ms/image | 2.0ms/image |
| 输入 shape | (32, 3, 640, 640) | (32, 3, 640, 640) |

**逐行解读**：
- **mAP（mean Average Precision）行**：从 0.49/0.504 提升至 0.502/0.515，主指标在 IoU 0.5:0.95 全类平均下提升约 1.1 个百分点，符合集成模型减少泛化误差的预期。
- **mAR（mean Average Recall）行**：从 0.681 提升至 0.689（maxDets=100），小目标仅 +0.002、中目标 +0.008、大目标 +0.018，集成在大物体上收益更明显。
- **AP@0.5 vs AP@0.75**：在低 IoU 阈值上绝对值更高（0.688→0.699），但提升幅度在高 IoU（0.75）下也保持（0.546→0.557），说明集成对定位精度有正向作用。
- **速度行**：推理耗时从 22.4ms 升至 39.5ms（约 +76%），NMS 从 1.4ms 升至 2.0ms，二者相加即集成多模型前向 + 合并 NMS 的总成本；前处理阶段未受影响（0.1ms 不变）。

---

## 【公式解读】

**原文无公式**。文档中涉及的指标名（mAP、Recall、P、R、IoU、NMS 等）来自 pycocotools 与 YOLOv5 val 流程的标准定义，原文未给出任何 LaTeX 或伪代码公式。

---

## 【关联】

- **上游/环境依赖**：文档开头 "Before You Start" 部分要求克隆 ultralytics/yolov5 仓库与安装 requirements.txt，并要求 `Python>=3.8.0`、`PyTorch>=1.8`，链接到 GitHub 仓库的 `requirements.txt`、`models/`、`data/` 目录与 `release` 页。这是执行本文所有 `val.py` / `detect.py` 命令的前提。
- **预训练模型来源**：单模型基线与集成均依赖 YOLOv5 官方预训练权重（`yolov5s/m/l/x.pt`、`yolov5l6.pt` 等），文档指向 README 中的 [Pretrained Checkpoints table](https://github.com/ultralytics/yolov5#pretrained-checkpoints) 与 `models/` 目录。
- **数据集与评测脚本**：评测数据来自 COCO val2017（5000 张、36335 标签、48 missing），评测通过 `pycocotools mAP` 进行，输出 JSON 保存到 `runs/val/exp*/yolov5x_predictions.json`。
- **推理流水线**：集成推理的输出结构（4 persons, 1 bus, 1 tie / 3 persons, 2 ties）与 `detect.py` 默认结果保存路径 `runs/detect/exp2` 与 YOLOv5 通用推理教程保持一致。
- **下游运行环境（来自 Supported Environments 与文末内部链接）**：
  - [Google Cloud Quickstart Tutorial](../environments/google_cloud_quickstart_tutorial.md) — 在 GCP 上运行 YOLOv5 集成评测
  - [AWS Quickstart Tutorial](../environments/aws_quickstart_tutorial.md) — 在 AWS 上部署
  - [AzureML Quickstart Tutorial](../environments/azureml_quickstart_tutorial.md) — 在 Azure 机器学习平台上运行
  - [Docker Image Quickstart Tutorial](../environments/docker_image_quickstart_tutorial.md) — 通过官方 Docker 镜像启动带 CUDA/CUDNN/Python/PyTorch 的容器
- **术语外链**：mAP / Recall 等术语指向 Ultralytics glossary，Wikipedia Ensemble_learning 提供核心理论背景。

---

## 【使用方法】

### 1. 准备环境（原文命令）

```bash
git clone https://github.com/ultralytics/yolov5  # clone
cd yolov5
pip install -r requirements.txt  # install
```

要求：`Python>=3.8.0`、`PyTorch>=1.8`。

### 2. 单模型基线测试（原文命令）

```bash
python val.py --weights yolov5x.pt --data coco.yaml --img 640 --half
```
- 关键参数：`--weights` 单权重；`--data coco.yaml`；`--img 640`；`--half`（FP16）。
- 可选模型：`yolov5s.pt`、`yolov5m.pt`、`yolov5l.pt`、`yolov5x.pt`，或自定义 `./weights/best.pt`。

### 3. 多模型集成测试（原文命令）

```bash
python val.py --weights yolov5x.pt yolov5l6.pt --data coco.yaml --img 640 --half
```
- 用法：在 `--weights` 后空格追加更多 `.pt` 文件即可启用集成（`val.py` 自动创建 `Ensemble created with [...]`）。

### 4. 多模型集成推理（原文命令）

```bash
python detect.py --weights yolov5x.pt yolov5l6.pt --img 640 --source data/images
```
- 输出默认保存到 `runs/detect/exp*`。

### 5. 运行平台（原文 Supported Environments）

- 免费 GPU Notebook：Gradient、Colab、Kaggle
- 云平台与容器（通过文末内部链接）：Google Cloud、AWS、AzureML、Docker Image（均预装 CUDA/CUDNN/Python/PyTorch）

> 原文未涉及：集成模型数量上限、各模型输出层融合策略（如加权/投票的具体实现）、自定义 NMS 参数在集成下的生效方式、CIoU/DIoU 等回归损失端的集成方案。这些均为用户需自行验证的部分。
