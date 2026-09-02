# getting_started

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/detection/centernet2/docs/tutorials/getting_started.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/detection/centernet2/docs/tutorials/getting_started.md

# 一体化深度解读: Detectron2 Getting Started Guide

---

## 【定位】

这篇文档是 Detectron2 框架的入门级教程,系统性介绍其内置命令行工具(`demo.py`、`plain_train_net.py`、`train_net.py`)的使用方法,覆盖**预训练模型推理演示**、**模型训练与评估**、**API 代码级调用**三大核心场景,为用户在 CenterNet2 等下游项目中快速落地 Detectron2 提供端到端的工作流指引。

---

## 【技术要点】

1. **预训练模型推理流程**: 从 `MODEL_ZOO.md` 选定模型及对应 config(以 `mask_rcnn_R_50_FPN_3x.yaml` 为例),通过 `demo.py` 加载 `MODEL.WEIGHTS` 指向的 model zoo 权重(`detectron2://` 协议 URL,如 `model_final_f10217.pkl`)进行推理。

2. **多模态输入支持**: `demo.py` 原生支持三种输入模式 —— 图片列表(`--input input1.jpg input2.jpg`)、摄像头(`--webcam`)、视频文件(`--video-input video.mp4`),并可通过 `--output` 输出可视化结果到目录或文件。

3. **设备灵活切换**: 通过 `--opts MODEL.DEVICE cpu` 可强制 CPU 推理,无需修改代码即可在无 GPU 环境下运行。

4. **训练脚本分层**: 提供两个训练脚本 —— `tools/plain_train_net.py`(抽象少、易扩展自定义逻辑)与 `tools/train_net.py`(默认特性更完整),均能跑通所有内置 config。

5. **多卡/单卡训练参数切换**: 原 config 默认针对 **8 卡** 训练设计;切换到单卡时需配合调整关键超参:`SOLVER.IMS_PER_BATCH 2`(每 batch 图片数)、`SOLVER.BASE_LR 0.0025`(基础学习率),依据论文 `https://arxiv.org/abs/1706.02677` 的线性缩放规则。

6. **评估模式**: 在训练脚本中加入 `--eval-only` 标志并指定 `MODEL.WEIGHTS /path/to/checkpoint_file` 即可对已有 checkpoint 单独评估,无需启动训练循环。

---

## 【关键机制与数据】

**工作原理与数据流**(均严格基于原文):

- **推理机制**(原文): `demo.py` 接受 config 文件 + 输入路径,通过 `--opts` 覆盖默认参数(`MODEL.WEIGHTS`),模型权重以 `detectron2://` URL 协议自动从 model zoo 拉取。运行后通过 OpenCV 窗口实时显示可视化结果。
  - 原文命令示例:`python demo.py --config-file ../configs/COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml --input input1.jpg input2.jpg --opts MODEL.WEIGHTS detectron2://COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x/137849600/model_final_f10217.pkl`

- **训练数据流**(原文): 训练前需先按 `datasets/README.md` 配置数据集路径;`train_net.py` 读取 config 中的 8 卡训练配置,启动分布式训练循环。config 中的 `MODEL.WEIGHTS` 默认值用于训练初始化(若是预训练权重),而非评估。

- **单卡缩放规则**(原文): 单卡训练需手动将 batch size 降至 `2`、学习率降至 `0.0025`,依据 `https://arxiv.org/abs/1706.02677`(即 NVIDIA 的 "Accurate, Large Minibatch SGD" 论文,原文链接) 提到的 minibatch SGD 线性缩放原则。

- **评估流程**(原文): 复用同一训练脚本的 `--eval-only` 模式,跳过训练步骤,直接加载指定 checkpoint 在验证集上跑前向推理并计算指标。

- **性能数据**: 原文未提供任何 benchmark 数字(无 mAP、吞吐量、训练时长等具体数值)。

---

## 【表格解读】

**原文无表格**。

原文仅以代码块形式给出命令示例与参数值,未出现任何结构化表格(如超参对照表、性能对比表等)。

---

## 【公式解读】

**原文无公式**。

原文未出现 LaTeX 公式或伪代码形式公式。虽提及 `https://arxiv.org/abs/1706.02677` 的线性缩放规则,但未在文档中给出具体公式形式(如 `lr ∝ batch_size`),故不臆造。

---

## 【关联】

**与文中其他模块/上下游的关系**:

- **MODEL_ZOO.md** (内部链接): 推理 demo 的入口依赖,用户必须先从此处选取预训练模型 config 与权重,文档示例直接引用 `MODEL_ZOO.md` 作为第一步操作。
- **./datasets/README.md** (内部链接): 训练前置条件,详细说明如何注册/配置自定义数据集路径;`train_net.py` 启动前必须先完成此步骤。
- **Colab Notebook** (`https://colab.research.google.com/drive/16jcaJoc6bCFAQ96jDe2HwtXj7BMD_-m5`): 与本文互为补充 —— 本文侧重命令行工具,该 Notebook 侧重 API 级 Python 代码示例(用现有模型推理、在自定义数据集上训练内置模型)。
- **detectron2/projects** (`https://github.com/facebookresearch/detectron2/tree/master/projects`): 进阶项目示例库,提供更多项目级落地参考。
- **arxiv 论文 1706.02677**: 单卡参数调整的理论依据(线性缩放规则),非 Detectron2 自身代码,作为外部参考。
- **CenterNet2 项目关系**: 此文档位于 `centernet2/docs/tutorials/` 路径下,说明 CenterNet2 项目将 Detectron2 作为基础框架,本文档为其用户熟悉底层引擎的引导教程。

---

## 【使用方法】

**原文涵盖的启用方式/配置项/命令汇总**:

### 1. 推理 Demo
```bash
cd demo/
python demo.py --config-file ../configs/COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml \
  --input input1.jpg input2.jpg \
  --opts MODEL.WEIGHTS detectron2://COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x/137849600/model_final_f10217.pkl
```

**常用选项**:
| 选项 | 作用 |
|---|---|
| `--webcam` | 摄像头实时输入 |
| `--video-input video.mp4` | 视频文件输入 |
| `--opts MODEL.DEVICE cpu` | 切换 CPU 推理 |
| `--output` | 保存输出到目录(图片)或文件(视频/摄像头) |

### 2. 多卡训练(8 卡)
```bash
cd tools/
./train_net.py --num-gpus 8 \
  --config-file ../configs/COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_1x.yaml
```

### 3. 单卡训练(1 卡,已缩放参数)
```bash
./train_net.py \
  --config-file ../configs/COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_1x.yaml \
  --num-gpus 1 SOLVER.IMS_PER_BATCH 2 SOLVER.BASE_LR 0.0025
```

### 4. 评估模式
```bash
./train_net.py \
  --config-file ../configs/COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_1x.yaml \
  --eval-only MODEL.WEIGHTS /path/to/checkpoint_file
```

### 5. 更多选项
原文建议通过 `./train_net.py -h` 或 `demo.py -h` 查看完整命令行参数列表。
