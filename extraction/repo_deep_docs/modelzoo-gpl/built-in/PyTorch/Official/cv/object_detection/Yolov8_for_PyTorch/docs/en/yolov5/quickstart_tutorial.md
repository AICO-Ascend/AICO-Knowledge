# YOLOv5 Quickstart 🚀

> 仓 `modelzoo-gpl` · 路径 `built-in/PyTorch/Official/cv/object_detection/Yolov8_for_PyTorch/docs/en/yolov5/quickstart_tutorial.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-gpl/built-in/PyTorch/Official/cv/object_detection/Yolov8_for_PyTorch/docs/en/yolov5/quickstart_tutorial.md

【定位】
本文档是 YOLOv5 的官方 Quickstart 入门指南，旨在帮助用户快速完成 YOLOv5 实时目标检测项目的环境搭建、推理验证与训练复现，是从零开始使用 YOLOv5 的"一站式起点"文档。

【技术要点】
- 环境要求：**Python>=3.8.0** 且 **PyTorch>=1.8**，通过克隆官方仓库并执行 `pip install -r requirements.txt` 安装依赖。
- 推理方式 ①：**PyTorch Hub** 加载模型，使用 `torch.hub.load("ultralytics/yolov5", "yolov5s")`，模型可选范围 `'yolov5n'` 到 `'yolov5x6'`，支持 `'custom'` 自定义权重；输入 `img` 支持文件路径、PIL、OpenCV、numpy 或图片列表等多种形式。
- 推理方式 ②：**`detect.py`** 命令行推理，支持 webcam、image.jpg、video.mp4、screenshot、目录、list.txt、list.streams、`'path/*.jpg'` glob、YouTube URL、RTSP/RTMP/HTTP 流共 10 种 source 类型。
- 训练配置：基于 **COCO** 数据集复现 benchmark，`python train.py --data coco.yaml --epochs 300 --weights '' --cfg yolov5n.yaml`，并可通过 `--batch-size -1` 启用 **AutoBatch** 自动寻找最优 batch。
- 多卡训练：原文注明 Multi-GPU 训练更快（链接到 `multi_gpu_training.md`）。
- 模型规格：yolov5n/s/m/l/x 在 **V100 GPU** 上的训练耗时分别为 **1/2/4/6/8 天**。

【关键机制与数据】
- 工作原理（原文）：文档未深入展开 YOLOv5 内部网络结构/数据流；通过 PyTorch Hub 加载模型 → 输入图像 → `model(img)` 执行推理 → `results.print()/.show()/.save()/.crop()/.pandas()` 进行结果展示与后处理。
- `detect.py` 自动从最新 YOLOv5 release 拉取权重文件（原文："automatically fetches models from the latest YOLOv5 release"）。
- 训练模型与权重文件同样从 latest release 拉取（原文："models and datasets are pulled directly from the latest YOLOv5 release"）。
- 性能数据（原文）：
  - V100 GPU 上训练耗时：n/s/m/l/x = **1/2/4/6/8 days**
  - V100-16GB 推荐 batch-size：n=**128**，s=**64**，m=**40**，l=**24**，x=**16**
  - 训练 epoch 数：**300**

【表格解读】
原文无表格。但训练命令段落中存在一个对齐排版的"配置对照表"，现用 markdown 表格逐字还原如下：

| 模型 (--cfg) | --batch-size | 训练耗时（V100，days） |
|---|---|---|
| yolov5n.yaml | 128 | 1 |
| yolov5s.yaml | 64 | 2 |
| yolov5m.yaml | 40 | 4 |
| yolov5l.yaml | 24 | 6 |
| yolov5x.yaml | 16 | 8 |

逐行解读：
- `yolov5n.yaml`：最小模型，V100-16GB 上 batch-size 取 **128**，单卡训练约 **1 天** 即可完成 300 epoch。
- `yolov5s.yaml`：小型模型，batch-size **64**，训练约 **2 天**。
- `yolov5m.yaml`：中型模型，batch-size **40**，训练约 **4 天**。
- `yolov5l.yaml`：大型模型，batch-size **24**（受显存限制下降），训练约 **6 天**。
- `yolov5x.yaml`：最大模型，batch-size 最小为 **16**，训练约 **8 天**。
- 共性参数：所有配置共享 `--data coco.yaml`、`--epochs 300`、`--weights ''`（从零训练，不加载预训练权重）。

【公式解读】
原文无公式。

【关联】
- `./tutorials/pytorch_hub_model_loading.md`：在"Inference with PyTorch Hub"小节中被链接，用于详细说明如何通过 `torch.hub.load` 加载 YOLOv5 预训练或自定义模型，是本文 PyTorch Hub 推理方式的深入教程。
- `./tutorials/multi_gpu_training.md`：在"Training"小节中被链接，原文指出 Multi-GPU 部署比单卡"work faster"，该教程负责展开多卡训练的命令与配置方法。
- 外部链接关联：
  - Ultralytics 词汇表（glossary）页：object-detection、pytorch、machine-learning-ml、batch-size — 提供术语解释。
  - GitHub 资源：requirements.txt、models/、data/、releases、COCO 脚本（`get_coco.sh`）— 指向仓库源码与数据准备脚本。
  - AutoBatch PR（#5092）— `--batch-size -1` 功能的实现出处。

【使用方法】
- 安装与运行（原文命令，保留原文格式）：
  ```bash
  git clone https://github.com/ultralytics/yolov5  # clone repository
  cd yolov5
  pip install -r requirements.txt  # install dependencies
  ```
- PyTorch Hub 推理（原文 Python 代码，保留原文格式）：
  ```python
  import torch
  model = torch.hub.load("ultralytics/yolov5", "yolov5s")  # Can be 'yolov5n' - 'yolov5x6', or 'custom'
  img = "https://ultralytics.com/images/zidane.jpg"  # Can be a file, Path, PIL, OpenCV, numpy, or list of images
  results = model(img)
  results.print()  # Other options: .show(), .save(), .crop(), .pandas(), etc.
  ```
- `detect.py` 推理（原文命令格式）：
  ```bash
  python detect.py --weights yolov5s.pt --source 0                               # webcam
                                                 image.jpg                       # image
                                                 video.mp4                       # video
                                                 screen                          # screenshot
                                                 path/                           # directory
                                                 list.txt                        # list of images
                                                 list.streams                    # list of streams
                                                 'path/*.jpg'                    # glob
                                                 'https://youtu.be/LNwODJXcvt4'  # YouTube
                                                 'rtsp://example.com/media.mp4'  # RTSP, RTMP, HTTP stream
  ```
- 训练（原文命令格式，按模型替换 `--cfg` 与 `--batch-size`）：
  ```bash
  python train.py --data coco.yaml --epochs 300 --weights '' --cfg yolov5n.yaml  --batch-size 128
                                                               yolov5s                64
                                                               yolov5m                40
                                                               yolov5l                24
                                                               yolov5x                16
  ```
- 配置项说明（原文）：
  - `--weights ''`：从零训练（不加载预训练权重）。
  - `--batch-size -1`：启用 **AutoBatch**，由系统自动搜索最优 batch-size。
  - `--data coco.yaml`：使用 COCO 数据集配置。
  - `--epochs 300`：训练轮数固定 300。
  - 训练建议（原文）："Maximize performance by using the highest possible `--batch-size`"，即在显存允许下尽量取最大 batch-size 以提升性能。
