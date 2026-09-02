# Train/val/test sets as 1) dir: path/to/imgs, 2) file: path/to/imgs.txt, or 3) list: [path/to/imgs1, path/to/imgs2, ..]

> 仓 `modelzoo-gpl` · 路径 `built-in/PyTorch/Official/cv/object_detection/Yolov8_for_PyTorch/docs/en/yolov5/tutorials/train_custom_data.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-gpl/built-in/PyTorch/Official/cv/object_detection/Yolov8_for_PyTorch/docs/en/yolov5/tutorials/train_custom_data.md

# 一体化深度解读：YOLOv5 自定义数据集训练指南

---

## 【定位】

这篇文档解决「如何在自定义数据集上端到端训练 YOLOv5 模型」的问题，完整描述了从环境准备、数据集构建（Roboflow 半自动 / 手动标注两种路线）、YAML 配置组织、预训练模型选择，到启动训练的工程化流程。

---

## 【技术要点】

1. **环境依赖约束**：要求 Python ≥ 3.8.0、PyTorch ≥ 1.8，通过 `git clone` + `pip install -r requirements.txt` 完成安装；模型与数据集自动从最新 YOLOv5 release 下载。

2. **两种数据准备路径**：
   - **路径一（Roboflow）**：收集图像 → 用 Roboflow Annotate 在线标注 → 在 Roboflow 中转换为 YOLOv5 PyTorch 格式 → 导出。
   - **路径二（手动）**：自行标注 → 导出 YOLO 格式 `*.txt` → 按 `dataset.yaml` + 目录约定组织。

3. **YOLO 标签文件规范**：`*.txt` 每行一个目标，格式为 `class x_center y_center width height`，**坐标必须归一化到 0–1**（像素值需除以图像宽/高），类别号**从 0 开始**。

4. **dataset.yaml 配置**：YAML 内定义三项关键字段——数据集根目录 `path`、`train / val / test` 图像目录相对路径或 `*.txt` 文件列表、类别 `names` 字典。

5. **目录自动寻标机制**：YOLOv5 **自动**根据图像路径定位标签——把路径中最后一次出现的 `/images/` 替换为 `/labels/` 即可，无需在 YAML 中声明 labels 路径。约定 `/coco128` 位于 `/yolov5` 的**同级** `/datasets` 目录内。

6. **预处理策略**：YOLOv5 在训练时自带 online augmentation，**不建议**在 Roboflow 中再额外做增强，但推荐两项预处理——`Auto-Orient`（剥离 EXIF 方向）、`Resize (Stretch)` 至 **640×640**（YOLOv5 默认输入尺寸）。

7. **训练启动参数**：通过指定 dataset、batch-size、image size 加 `--weights yolov5s.pt`（推荐，使用预训练权重）或 `--weights '' --cfg yolov5s.yaml`（从零随机初始化）启动训练。

---

## 【关键机制与数据】

- **迭代闭环工作流**（原文 "Train On Custom Data" 段）：自定义建模是一个**迭代循环**——「采集并组织图像 → 标注感兴趣对象 → 训练模型 → 部署预测 → 用部署模型回采 edge case 样本 → 重复迭代改进」。这是 YOLOv5 与 active learning 闭环结合的核心机制。

- **数据流（手工路线）**：图像经标注后导出 → 按 `dataset.yaml` 声明的 `path` 根目录组织 → train/val 同目录（如 coco128 案例，128 张图同时用于训练和验证，用于验证 pipeline 能否过拟合）→ labels 由路径替换规则自动匹配。

- **路径替换算法**（原文 2.3 节）：`../datasets/coco128/images/im0.jpg` → `../datasets/coco128/labels/im0.txt`。该机制降低 YAML 配置复杂度，无需显式声明 label 路径。

- **Roboflow 流水线机制**：上传到 `Public` workspace → 标注未标注图像 → 生成 version 快照（snapshot，可对比未来训练 run）→ 以 `YOLOv5 Pytorch` 格式导出 → 复制下载 snippet 到训练脚本/Notebook 中导入。

- **小样本验证数据集 COCO128**（原文 2.1 节）：取自 COCO train2017 的**前 128 张图像**，train 与 val 共用同一组 128 张，专门用于**验证训练 pipeline 能否过拟合**——是 sanity-check 性质的 pipeline 验证数据集，非生产训练数据集。

- **模型选择基线**：原文示例选择 **YOLOv5s**——"the second-smallest and fastest model available"，完整模型对比在 README 的 pretrained checkpoints 表中。

- **训练命令（原文 4 节，文档在 `…yolov5s.yaml` 处被截断）**：原文未给出完整命令，但明确给出关键参数维度——`dataset, batch-size, image size`、权重来源 `--weights yolov5s.pt`（推荐）或随机初始化组合 `--weights '' --cfg yolov5s.yaml`。

- **性能数据**：原文未给出 mAP、推理速度等量化性能数字，完整模型性能对比在 README 表格中（本节文档未内嵌）。

---

## 【表格解读】

**原文无表格**。

文档主体未内嵌参数表或性能对比表。仅以图片形式呈现了模型对比（`yolov5-model-comparison.avif`）和数据集结构（`yolov5-dataset-structure.avif`），完整模型对比被外链到 README 的 `pretrained-checkpoints` 表，不在本文档正文范围内。YAML 代码块（coco128.yaml）是配置示例，不属于表格。

---

## 【公式解读】

**原文无公式**。

文档涉及坐标归一化的文字说明（"divide `x_center` and `width` by image width, and `y_center` and `height` by image height"），但**未给出显式公式**。如要还原该归一化操作的数学表达，应为：

$$x_{\text{norm}} = \frac{x_{\text{pixel}}}{W_{\text{img}}}, \quad y_{\text{norm}} = \frac{y_{\text{pixel}}}{H_{\text{img}}}, \quad w_{\text{norm}} = \frac{w_{\text{pixel}}}{W_{\text{img}}}, \quad h_{\text{norm}} = \frac{h_{\text{pixel}}}{H_{\text{img}}}$$

但此式为根据文字描述推导，**原文本身未写出该等式**，故按要求标注"原文无公式"。

---

## 【关联】

文档与下列内部模块/教程存在上下游或并列关系（依据文末内部链接信息）：

1. **./comet_logging_integration.md** — Comet 实验日志集成。训练过程中可视化 loss/mAP 等指标的实验管理工具，本文未内嵌但属典型训练配套。

2. **./clearml_logging_integration.md** — ClearML 实验日志集成。功能对位 Comet，是另一个常见的训练过程追踪方案。

3. **./pytorch_hub_model_loading.md** — PyTorch Hub 模型加载方式。与本文「Select a Model」一节呼应：用户既可通过 `train.py --weights yolov5s.pt` 启动，也可通过 PyTorch Hub 直接 `torch.hub.load` 获取模型做推理/inference。

4. **./model_export.md** — 模型导出指南。处于本文「4. Train」之后的「Deploy」环节，对应文档开头的迭代闭环「部署到野外做预测」——导出为 ONNX / CoreML / TFLite 等格式用于生产。

5. **./hyperparameter_evolution.md** — 超参演化（遗传超参搜索）。与本文训练命令并列，用于在训练前/训练中自动搜索最优超参（lr、augmentation 强度等），是同一训练流程的增强模块。

6. **../environments/google_cloud_quickstart_tutorial.md** — GCP 快速上手教程。属于「Train On Custom Data」的环境扩展：在 GCP 上启动训练任务。

7. **../environments/aws_quickstart_tutorial.md** — AWS 快速上手教程。环境扩展：在 AWS 上启动训练任务。

8. **../environments/azureml_quickstart_tutorial.md** — AzureML 快速上手教程。环境扩展：在 Azure ML 上启动训练任务。

9. **../environments/docker_image_quickstart_tutorial.md** — Docker 镜像快速上手教程。环境扩展：用官方 Docker 镜像容器化训练流程。

**上下游逻辑链**：
- **上游**（环境准备）：GCP/AWS/AzureML/Docker 四种云或容器化环境教程 → 本文「Before You Start」环境要求。
- **并行**（训练增强）：Comet/ClearML 日志 + Hyperparameter Evolution 超参搜索。
- **下游**（部署）：Model Export 导出 → PyTorch Hub 加载做推理 → 进入新一轮「active learning 闭环回采」。

---

## 【使用方法】

### 环境准备命令（原文 "Before You Start" 节）

```bash
git clone https://github.com/ultralytics/yolov5  # clone
cd yolov5
pip install -r requirements.txt  # install
```

环境约束：**Python >= 3.8.0**、**PyTorch >= 1.8**。

### 数据集配置示例（原文 coco128.yaml 节）

```yaml
path: ../datasets/coco128   # dataset root dir
train: images/train2017     # train images (relative to 'path') 128 images
val: images/train2017       # val images (relative to 'path') 128 images
test:                       # test images (optional)

# Classes (80 COCO classes)
names:
    0: person
    1: bicycle
    2: car
    # ...
    77: teddy bear
    78: hair drier
    79: toothbrush
```

### 目录组织约定（原文 2.3 节）

```bash
../datasets/coco128/images/im0.jpg  # image
../datasets/coco128/labels/im0.txt  # label
```

`/datasets` 与 `/yolov5` 同级，标签路径由 `/images/` → `/labels/` 自动替换。

### 训练启动参数（原文 4 节，文档在此处截断）

可确认的参数维度：
- **dataset**：通过 `--data dataset.yaml` 指定（原文未在截断片段中写出该 flag，但通过语义明确）
- **batch-size**：命令行参数
- **image size**：命令行参数（默认 640×640）
- **权重来源**：
  - 推荐——`--weights yolov5s.pt`（使用预训练权重）
  - 从零训练——`--weights '' --cfg yolov5s.yaml`（随机初始化 + 模型结构配置）

**注**：原文 4 节命令在 `--weights '' --cfg yolov5s.yaml` 之后被截断，完整的 `train.py` 调用形式、epochs、device、cache 等其他参数在本文档内不可见——**原文未涉及**这些细节。
