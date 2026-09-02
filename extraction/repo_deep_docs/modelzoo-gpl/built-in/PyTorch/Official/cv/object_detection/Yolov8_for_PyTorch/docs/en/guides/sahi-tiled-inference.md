# Ultralytics Docs: Using YOLO11 with SAHI for Sliced Inference

> 仓 `modelzoo-gpl` · 路径 `built-in/PyTorch/Official/cv/object_detection/Yolov8_for_PyTorch/docs/en/guides/sahi-tiled-inference.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-gpl/built-in/PyTorch/Official/cv/object_detection/Yolov8_for_PyTorch/docs/en/guides/sahi-tiled-inference.md

# 一体化深度解读:YOLO11 + SAHI 切片推理指南

---

## 【定位】

本文档是 Ultralytics 官方针对 **YOLO11 模型结合 SAHI(Slicing Aided Hyper Inference)切片辅助超推理框架** 的集成使用指南,核心解决**在高分辨率/大尺寸图像上对小目标进行目标检测时显存不足、检测质量下降**的问题,通过将大图切分为多个重叠子片分别推理再融合的方式,在保持精度的同时降低计算与显存开销。

---

## 【技术要点】

1. **SAHI 核心机制 = 切分 → 单片推理 → 拼接融合**:先把大图切成多个子片(slices),在每片上独立跑 YOLO 检测,再通过智能算法合并重叠区域的检测框(原文:"SAHI maintains the detection accuracy by employing smart algorithms to merge overlapping detection boxes during the stitching process")。

2. **默认切片参数**:切片尺寸 `slice_height=256`、`slice_width=256`,重叠率 `overlap_height_ratio=0.2`、`overlap_width_ratio=0.2`(原文代码块逐字给出,无歧义)。

3. **模型接入层抽象**:`sahi.AutoDetectionModel.from_pretrained(...)` 封装了底层 YOLO 加载过程,关键参数包括 `model_type="yolov8"`(SAHI 内部仍以 `yolov8` 标识,与 YOLO11 兼容)、`confidence_threshold=0.3`(标准推理)或 `0.4`(批量推理)、`device="cpu" | "cuda:0"`。

4. **三种调用入口**:① `get_prediction(...)` 走标准全图推理;② `get_sliced_prediction(...)` 走单图切片推理;③ `sahi.predict.predict(...)` 走目录级批量切片推理。

5. **结果对象多格式导出**:`PredictionResult` 支持 `to_coco_annotations()`、`to_coco_predictions(image_id=...)`、`to_imantics_annotations()`、`to_fiftyone_detections()` 四种标注格式,以及 `export_visuals(export_dir=...)` 导出可视化 PNG。

6. **依赖与资源**:`pip install -U ultralytics sahi`;内置 `download_yolov8s_model("models/yolo11s.pt")` 下载 YOLO11s 模型;内置 `download_from_url(...)` 下载 SAHI 官方 demo 图 `small-vehicles1.jpeg` 和 `terrain2.png`。

---

## 【关键机制与数据】

- **工作原理(原文描述)**:Sliced Inference 是把"大图/高分辨率图"切成多个小段 → 在每段上做检测 → 再把每段的检测结果重编译回原图坐标系下,适用于计算资源受限或图像分辨率高到直接处理会内存爆炸的场景。

- **三条收益(原文)**:① Reduced Computational Burden(切片更小、显存更省、跑在低端硬件上更顺);② Preserved Detection Quality(每片独立处理,只要切片足够大到能包住目标,质量不下降);③ Enhanced Scalability(可方便扩展到不同分辨率图像,从卫星图到医学诊断都适用)。

- **三点核心特征(原文)**:① Seamless Integration(与 YOLO 无缝集成,改动少);② Resource Efficiency(分片降低显存);③ High Accuracy(通过合并重叠检测框保持精度)。

- **SAHI 论文出处(原文)**:Akyon, Altinuc, Temizel 于 *2022 IEEE ICIP*, 论文标题 *"Slicing Aided Hyper Inference and Fine-tuning for Small Object Detection"*, DOI `10.1109/ICIP46576.2022.9897990`, pp. 966-970。

- **资源链接(原文)**:SAHI GitHub 仓库 `https://github.com/obss/sahi`;演示图 `https://raw.githubusercontent.com/obss/sahi/main/demo/demo_data/small-vehicles1.jpeg` 与 `terrain2.png`;可视化对比图 `yolov8-without-sahi.avif` 与 `yolov8-with-sahi.avif`。

- **性能数据**:原文未提供任何具体 mAP、APs、推理耗时、显存占用等定量数字,只放了两张定性可视化对比图(有 SAHI 检出更多小目标车辆,无 SAHI 漏检明显)。

---

## 【表格解读】

原文包含一个表格,但并非"参数表/性能对比/配置项"型数据表,而是**双栏可视化对比表**(用图片展示效果差异)。按原文结构逐字还原:

| 列 1 | 列 2 |
|---|---|
| **YOLO11 without SAHI** | **YOLO11 with SAHI** |
| `<img src="https://github.com/ultralytics/docs/releases/download/0/yolov8-without-sahi.avif" alt="YOLO11 without SAHI" width="640">` | `<img src="https://github.com/ultralytics/docs/releases/download/0/yolov8-with-sahi.avif" alt="YOLO11 with SAHI" width="640">` |

**逐行解读**:
- 表头第一行是并列的两组实验:左为"仅用 YOLO11",右为"YOLO11 + SAHI 切片推理",其他条件相同。
- 表头第二行分别是各自的定性可视化截图(都是 `.avif`,宽 640)。文档未提供任何定量指标(无 mAP/APs/latency/GPU mem 等数字),因此这张表只能说明"加 SAHI 后能多检测出更多小目标"这一**定性结论**,而不能用作性能基准。

> 原文无参数表、性能对比表或配置项表。

---

## 【公式解读】

原文无任何 LaTeX 数学公式或伪代码公式。全文只有 Python `pip install` 命令、Python API 调用代码片段(`from_pretrained`、`get_prediction`、`get_sliced_prediction`、`predict` 等),并未给出 SAHI 切分坐标计算、重叠区域合并 NMS 等数学表达。

> 原文无公式。

---

## 【关联】

文档位于 `built-in/PyTorch/Official/cv/object_detection/Yolov8_for_PyTorch/docs/en/guides/sahi-tiled-inference.md`,从内容归属看是 **Ultralytics 官方文档(英文)** 在该仓库下的镜像/移植版本(尽管仓内目录名为 Yolov8,文档正文讲的是 YOLO11,这是因为 Ultralytics 的 YOLO11 推理后端在 SAHI 的 `model_type` 中仍以 `"yolov8"` 标识)。

文中提到/链接的相关生态组件:

- **SAHI 库本体**(`https://github.com/obss/sahi`):切片推理核心依赖;切片尺寸、重叠率、合并逻辑都由它实现。
- **Ultralytics `ultralytics` 包**:YOLO11 模型加载与推理引擎,被 `AutoDetectionModel` 包装。
- **下游结果处理工具**:`imantics`(实例分割标注转换)、`fiftyone`(数据集可视化工具)、**COCO annotation/prediction 格式**(标准目标检测评测格式)。
- **上游训练/论文**:SAHI 原始论文(Akyon et al., ICIP 2022)既覆盖 inference,也覆盖 fine-tuning,本文档只展示了 inference 部分。
- **横向场景对照**:卫星遥感(satellite imagery)、医学诊断(medical diagnostics)——原文作为"应用场景示例"提及,但未给出这些场景的代码或数据。

> 本文档片段未提供文末"内部链接"(`(无)`),所以无法基于链接枚举站内跳转。

---

## 【使用方法】

按原文操作顺序整理如下(命令/参数均逐字保留):

**Step 1. 安装**
```bash
pip install -U ultralytics sahi
```

**Step 2. 准备模型与测试图**
```python
from sahi.utils.file import download_from_url
from sahi.utils.yolov8 import download_yolov8s_model

model_path = "models/yolo11s.pt"
download_yolov8s_model(model_path)

download_from_url(
    "https://raw.githubusercontent.com/obss/sahi/main/demo/demo_data/small-vehicles1.jpeg",
    "demo_data/small-vehicles1.jpeg",
)
download_from_url(
    "https://raw.githubusercontent.com/obss/sahi/main/demo/demo_data/terrain2.png",
    "demo_data/terrain2.png",
)
```

**Step 3. 装载模型(原文参数:conf=0.3, device=cpu/cuda:0)**
```python
from sahi import AutoDetectionModel

detection_model = AutoDetectionModel.from_pretrained(
    model_type="yolov8",
    model_path=yolov8_model_path,
    confidence_threshold=0.3,
    device="cpu",  # or 'cuda:0'
)
```

**Step 4a. 标准推理(原文)**
```python
from sahi.predict import get_prediction
result = get_prediction("demo_data/small-vehicles1.jpeg", detection_model)
# 或 numpy 图像: get_prediction(read_image(...), detection_model)
result.export_visuals(export_dir="demo_data/")
Image("demo_data/prediction_visual.png")
```

**Step 4b. 切片推理(原文核心 API,默认参数)**
```python
from sahi.predict import get_sliced_prediction

result = get_sliced_prediction(
    "demo_data/small-vehicles1.jpeg",
    detection_model,
    slice_height=256,
    slice_width=256,
    overlap_height_ratio=0.2,
    overlap_width_ratio=0.2,
)
```

**Step 5. 结果导出(原文)**
```python
object_prediction_list = result.object_prediction_list
result.to_coco_annotations()[:3]
result.to_coco_predictions(image_id=1)[:3]
result.to_imantics_annotations()[:3]
result.to_fiftyone_detections()[:3]
```

**Step 6. 目录级批量切片推理(原文,conf=0.4)**
```python
from sahi.predict import predict

predict(
    model_type="yolov8",
    model_path="path/to/yolo11n.pt",
    model_device="cpu",  # or 'cuda:0'
    model_confidence_threshold=0.4,
    source="path/to/dir",
    slice_height=256,
    slice_width=256,
    overlap_height_ratio=0.2,
    overlap_width_ratio=0.2,
)
```

**补充说明**:
- 原文未提供 CLI 命令(如 `yolo predict ...` 形式),仅给出 Python API 形式。
- 原文未涉及 SAHI 训练/微调(fine-tuning)、未涉及自定义数据集配置、未涉及性能基准数据。
- 原文 FAQ 部分在所提供片段中被截断(`download_from_url(...)` 后戛然而止),其余 FAQ 内容原文未涉及。
