# Freeze

> 仓 `modelzoo-gpl` · 路径 `built-in/PyTorch/Official/cv/object_detection/Yolov8_for_PyTorch/docs/en/yolov5/tutorials/transfer_learning_with_frozen_layers.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-gpl/built-in/PyTorch/Official/cv/object_detection/Yolov8_for_PyTorch/docs/en/yolov5/tutorials/transfer_learning_with_frozen_layers.md

# YOLOv5 冻结层迁移学习指南 —— 一体化深度解读

---

## 【定位】

本文档阐述在使用 YOLOv5 进行迁移学习 (transfer learning) 时如何通过**冻结网络层**来降低训练资源开销、加速训练收敛,同时以小幅最终精度损失为代价。

---

## 【技术要点】

1. **冻结的本质机制**:迁移学习不是重新训练整个网络,而是将部分初始权重"冻结"在原地,仅让剩余权重参与损失计算与优化器更新。原文:"part of the initial weights are frozen in place, and the rest of the weights are used to compute loss and are updated by the optimizer"。
2. **冻结的实现方式**:在 `train.py` 中维护一个 `freeze` 列表(由前缀字符串构成,如 `"model.0."`),遍历 `model.named_parameters()`,对名称中匹配列表前缀的参数设置 `v.requires_grad = False`,从而在反向传播时屏蔽其梯度更新。
3. **YOLOv5 v6.0 架构的层索引**:Backbone 由 `model.0` ~ `model.9` 共 10 层组成(对应 `Conv→C3→Conv→C3→Conv→C3→Conv→C3→SPPF` 的 P1/2 ~ P5/32 特征金字塔下采样);Head 从 `model.10` 一直延伸到 `model.24`,其中 `model.24` 为最终的 `Detect([17,20,23])` 多尺度检测头。
4. **冻结 Backbone 命令**:`python train.py --freeze 10` —— 匹配 `model.0.` ~ `model.9.` 前缀的所有层被冻结,只有 head 部分参与训练。
5. **冻结全部层(保留 Detect 输出)命令**:`python train.py --freeze 24` —— 匹配 `model.0.` ~ `model.23.` 前缀的所有层被冻结,仅最终 `Detect()` 中的输出卷积层可训练。
6. **对比训练基线**:以未冻结的默认模型作对照,三者均基于 `--weights yolov5m.pt`(COCO 预训练权重)在 VOC 数据集上训练,命令为 `train.py --batch 48 --weights yolov5m.pt --data voc.yaml --epochs 50 --cache --img 512 --hyp hyp.finetune.yaml`。

---

## 【关键机制与数据】

### 工作原理(数据流)

- **冻结前向/反向**:冻结并不删除参数,也不改变前向传播的计算图;它仅通过 `requires_grad=False` 告知 PyTorch 优化器"不要对这些参数的 `.grad` 进行累加与 step 更新"。
- **匹配策略**:原文采用前缀模糊匹配 `any(x in k for x in freeze)`,而非精确索引,因此一个参数名只要包含 `freeze` 列表中任一字符串(如 `"model.10."`)即被冻结。这种方式使得 `freeze` 列表的数值语义是"前 N 个模块"(因为命名按层序递增)。
- **梯度归零 vs requires_grad**:原文代码先将所有参数设为 `v.requires_grad = True`(默认状态),再对冻结列表中的参数覆盖设为 `False`;这与"梯度清零"是两个不同概念——前者永久阻断梯度流,后者仅在每次迭代前清空累积。

### 性能与资源数据(原文表述)

- **精度方面**(原文):"freezing speeds up training, but reduces final accuracy slightly"(冻结加快训练但轻微降低最终精度,具体数值以图片表格形式给出,原文未提供可读取的 mAP 数字)。
- **GPU 资源方面**(原文):"the more modules are frozen the less GPU memory is required to train, and the lower GPU utilization"(冻结模块越多,训练所需 GPU 显存越少,GPU 利用率也越低)。
- **由此衍生的工程建议**(原文):"larger models, or models trained at larger --image-size may benefit from freezing in order to train faster"(更大的模型或使用更大 `--image-size` 训练的模型,可受益于冻结以更快训练)。

---

## 【表格解读】

**原文无表格**。

> 说明:文档在 "Accuracy Comparison" 章节引用了一张 `<img>` 形式的表格截图(`table-results.avif`)以及两张 mAP 曲线图(`freezing-training-map50-results.avif` 与 `freezing-training-map50-results-95.avif`),但原文 Markdown 中**未给出任何可读的表格行/列数据**(既无 mAP 数值,也无 epoch/loss 数值),因此本节只能如实标注"原文无表格"。同理,"GPU Utilization Comparison" 一节的显存占用率、利用率曲线也只有图片链接,无文本数值。

---

## 【公式解读】

**原文无公式**。

---

## 【关联】

文档与上下游内容通过以下内部链接形成完整的使用链路:

| 内部链接路径 | 作用与上下游关系 |
|---|---|
| `../environments/google_cloud_quickstart_tutorial.md` | **上游/部署前置**:提供在 GCP 上搭建 YOLOv5 训练环境(CUDA/CUDNN/Python/PyTorch)的步骤,本文的 `--freeze` 命令需在已配置好的云端环境中运行。 |
| `../environments/aws_quickstart_tutorial.md` | **上游/部署前置**:AWS 云端环境快速开始指南,与 GCP 文档并列,共同支撑本文"Supported Environments"中提到的多云训练场景。 |
| `../environments/azureml_quickstart_tutorial.md` | **上游/部署前置**:Azure 机器学习云环境配置指南,与上面两个文档并列。 |
| `../environments/docker_image_quickstart_tutorial.md` | **上游/部署前置**:Docker 镜像方式快速部署,与云端方案并列,提供容器化训练环境。 |

此外,文档还引用了 Ultralytics 官方仓库中的 `train.py`、`val.py`、`detect.py`、`export.py`、`benchmarks.py` 以及 `requirements.txt`、`models/`、`data/` 目录,共同构成"环境 → 训练 → 冻结 → 评估"的完整链路;CI 徽章部分表明这些脚本在 macOS/Windows/Ubuntu 三平台上每 24 小时自动验证一次。

---

## 【使用方法】

### 一、前置环境(原文 Before You Start)

```bash
git clone https://github.com/ultralytics/yolov5   # clone
cd yolov5
pip install -r requirements.txt                  # install
```

要求:**Python>=3.8.0**、**PyTorch>=1.8**;模型与数据集从 YOLOv5 最新 release 自动下载。

### 二、核心训练命令(原文给出)

**冻结 Backbone(0-9 层)**:
```bash
python train.py --freeze 10
```

**冻结全部层(0-23 层),仅 Detect 输出可训练**:
```bash
python train.py --freeze 24
```

**对比实验基线(不冻结)**:
```bash
train.py --batch 48 --weights yolov5m.pt --data voc.yaml --epochs 50 --cache --img 512 --hyp hyp.finetune.yaml
```

### 三、关键配置项说明(原文呈现)

| 配置项 | 取值/含义 | 原文出处 |
|---|---|---|
| `--freeze` | 整数值 N,冻结 `model.0.` ~ `model.(N-1).` 前缀对应的所有层 | "Freeze Backbone" / "Freeze All Layers" |
| `--weights` | 预训练权重路径,实验使用 `yolov5m.pt`(COCO 预训练) | "Results" |
| `--data` | 数据集配置,实验使用 `voc.yaml` | "Results" |
| `--batch` | 批大小,实验取 `48` | "Results" |
| `--epochs` | 训练轮数,实验取 `50` | "Results" |
| `--img` | 输入图像尺寸,实验取 `512` | "Results" |
| `--hyp` | 超参数配置,实验使用微调专用 `hyp.finetune.yaml` | "Results" |
| `--cache` | 启用数据缓存以加速 I/O | "Results" |

### 四、查看可冻结层名称(辅助命令,原文提供)

```python
for k, v in model.named_parameters():
    print(k)
```
输出示例(原文摘录):`model.0.conv.conv.weight`、`model.0.conv.bn.weight`、`model.0.conv.bn.bias` …… `model.24.m.0.weight`、`model.24.m.0.bias`、`model.24.m.1.weight`、`model.24.m.1.bias`、`model.24.m.2.weight`、`model.24.m.2.bias`,从中可清晰看到 backbone 占 `model.0` ~ `model.9`,head 占 `model.10` ~ `model.24`(其中 `model.24` 为 Detect 头)。
