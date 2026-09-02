# getting_started

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/contrib/cv/semantic_segmentation/PointRend/docs/tutorials/getting_started.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/contrib/cv/semantic_segmentation/PointRend/docs/tutorials/getting_started.md

# 深度解读:PointRend/docs/tutorials/getting_started.md

> ⚠️ **路径与内容错位提示**:此文档位于 `PointRend/docs/tutorials/` 路径下,但其内容实为 **Detectron2 框架的通用入门指南**(原文标题为"Getting Started with Detectron2"),并非 PointRend 专题教程。在解读时需忠实于原文,不作越界推测。

---

## 【定位】

这篇文档提供 Detectron2 内置命令行工具(demo / train / eval)的使用入门,覆盖 **预训练模型推理演示**、**命令行训练与评估**、**API 编程调用** 三种典型场景的最小可运行路径。

---

## 【技术要点】

1. **预训练模型推理演示**:从 `MODEL_ZOO.md` 选择模型与 config(原文示例 `mask_rcnn_R_50_FPN_3x.yaml`),通过 `demo.py` 加载 `MODEL.WEIGHTS` 指向的 model zoo 权重进行推理并可视化。
2. **三类常见推理输入模式**:`--input <files>`(图片)、`--webcam`(摄像头)、`--video-input video.mp4`(视频),输出可用 `--output` 落到目录(图片)或文件(视频/摄像头)。
3. **CPU 推理开关**:通过 `--opts MODEL.DEVICE cpu` 覆盖默认设备(原文未给出默认设备型号)。
4. **两个训练脚本定位**: `tools/train_net.py` 支持更多默认特性(原文未列具体项),`tools/plain_train_net.py` 抽象更少、便于加入自定义逻辑(原文表述:"supports fewer default features"、"fewer abstraction, therefore is easier to add custom logic")。
5. **多卡→单卡训练参数换算**:config 默认按 8 卡训练设计,迁到 1 卡时按原文给出的命令显式降 batch 与学习率:`SOLVER.IMS_PER_BATCH 2`、`SOLVER.BASE_LR 0.0025`(原文同时给出参考论文 https://arxiv.org/abs/1706.02677,但未直接复刻其公式)。
6. **仅评估模式**:在同一 `train_net.py` 中加 `--eval-only` 并指向本地权重文件 `/path/to/checkpoint_file` 即可复现/评测已有 checkpoint。

---

## 【关键机制与数据】

- **原文:配置与权重的分离语义**——`MODEL.WEIGHTS` 默认值是训练初始化,而 demo 时必须显式指向 model zoo 的预训练 checkpoint,否则跑的是未训练初始化权重;示例 URL:`detectron2://COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x/137849600/model_final_f10217.pkl`(其中 `137849600` 与 `f10217` 为原文给出的权重标识,保留原样)。
- **原文:可视化后端**——demo 的可视化通过 OpenCV 窗口呈现(原文:"show visualizations in an OpenCV window")。
- **原文:命令行参数查看方式**——更多 demo 选项通过 `demo.py -h` 或查看源码;训练选项通过 `./train_net.py -h`。
- **原文:单卡训练的反推依据**——原文将"8 卡→1 卡"的换算指向一篇引用文献(https://arxiv.org/abs/1706.02677),文档本身并未给出推导公式或缩放曲线。
- 原文未出现任何精度/AP/FPS/吞吐量 等性能数据。

---

## 【表格解读】

**原文无表格**。原文涉及的关键配置/命令已在上文【技术要点】中以原文形式逐字保留。

---

## 【公式解读】

**原文无公式**。文档仅以引用链接形式给出 1 篇外部论文(https://arxiv.org/abs/1706.02677,用于多卡→单卡学习率换算),并未在文档内嵌 LaTeX/伪代码公式,故不作虚构展开。

---

## 【关联】

- **MODEL_ZOO.md**:在"推理演示"第一步中作为模型与 config 的选择入口被引用(`Pick a model and its config file from model zoo`)。它是本文档获取预训练权重的唯一上游来源。
- **./datasets/README.md**:在"命令行训练与评估"章节被引用,作为执行 `train_net.py` 之前的**前置步骤**(`first setup the corresponding datasets following datasets/README.md`)。它在流程上位于训练脚本之前。
- **外部 Colab Notebook** (https://colab.research.google.com/drive/16jcaJoc6bCFAQ96jDe2HwtXj7BMD_-m5):作为"使用 Detectron2 API 编程"的替代/补充教学资源,与本文的命令行路径形成 API vs CLI 的两条平行入口。
- **detectron2/projects** (https://github.com/facebookresearch/detron2/tree/master/projects):作为"在自己的项目中基于 detectron2 构建"的更上层示例集合,与本文档的入门级使用是上下游/进阶关系。
- **与 PointRend 的实际关系**:此文档虽然是 PointRend 目录下的教程,但内容是 Detectron2 的通用入门;PointRend 自身的模型/数据集/训练细节本文档**未涉及**。

---

## 【使用方法】

以下命令均为原文给出的可逐字复用的入口:

### 1. 推理 Demo(原文命令)
```
cd demo/
python demo.py --config-file ../configs/COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml \
  --input input1.jpg input2.jpg \
  [--other-options]
  --opts MODEL.WEIGHTS detectron2://COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x/137849600/model_final_f10217.pkl
```
常用替换(原文):
- 摄像头 → `--webcam`
- 视频 → `--video-input video.mp4`
- CPU → `--opts MODEL.DEVICE cpu`
- 落盘 → `--output <dir or file>`

### 2. 多卡训练(原文命令,8 卡)
```
cd tools/
./train_net.py --num-gpus 8 \
  --config-file ../configs/COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_1x.yaml
```

### 3. 单卡训练(原文命令,1 卡)
```
./train_net.py \
  --config-file ../configs/COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_1x.yaml \
  --num-gpus 1 SOLVER.IMS_PER_BATCH 2 SOLVER.BASE_LR 0.0025
```

### 4. 仅评估(原文命令)
```
./train_net.py \
  --config-file ../configs/COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_1x.yaml \
  --eval-only MODEL.WEIGHTS /path/to/checkpoint_file
```

### 5. 编程调用
原文未给出具体代码,转指 Colab Notebook(https://colab.research.google.com/drive/16jcaJoc6bCFAQ96jDe2HwtXj7BMD_-m5) 与 detectron2/projects,以学习 (a) 用现有模型推理、(b) 用自定义数据集训练内置模型。

> 备注:训练前的数据集准备不在本文档范围,详见 `./datasets/README.md`(原文链接)。
