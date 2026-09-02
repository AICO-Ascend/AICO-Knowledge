# Speed Estimation using Ultralytics YOLO11 🚀

> 仓 `modelzoo-gpl` · 路径 `built-in/PyTorch/Official/cv/object_detection/Yolov8_for_PyTorch/docs/en/guides/speed-estimation.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-gpl/built-in/PyTorch/Official/cv/object_detection/Yolov8_for_PyTorch/docs/en/guides/speed-estimation.md

# 一体化深度解读:Yolov8_for_PyTorch/docs/en/guides/speed-estimation.md

---

## 【定位】

这篇文档介绍如何利用 Ultralytics YOLO11 通过目标跟踪 (object tracking) 结合距离与时间数据来估算视频中目标的移动速度,服务于交通管控、自主导航与安防监控等需要实时感知运动状态的应用场景。

---

## 【技术要点】

1. **能力定位**:基于 `object tracking` + 距离/时间数据,在给定上下文内计算目标的运动速率,直接服务于实时决策与智能系统。
2. **核心入口**:`from ultralytics import solutions` → `solutions.SpeedEstimator(...)`,主调用方法为 `speed_obj.estimate_speed(im0)`(对每一帧图像进行速度估算)。
3. **示例模型**:使用 `yolo11n.pt` 作为默认检测/跟踪模型权重。
4. **运行模式**:OpenCV 视频管道 (`cv2.VideoCapture` → `cv2.VideoWriter`),把估算结果叠加写回视频帧;按 `q` 键退出 (`cv2.waitKey(1) & 0xFF == ord("q")`)。
5. **可配置区域**:通过 `region` 参数传入多边形点列表来定义测速区域(示例 `[(20, 400), (1080, 404), (1080, 360), (20, 360)]`)。
6. **输出约束**:文档明确指出"Speed is Estimate",速度是估算值,可能不完全准确,且估算结果会随 GPU 速度波动而变化。

---

## 【关键机制与数据】

**工作原理**(按文档 FAQ 描述还原):

1. 对视频每帧使用 YOLO11 模型做 **目标检测 (object detection)**。
2. 在帧间对目标进行 **跟踪 (tracking)**,建立时序关联。
3. 依据目标在两帧之间的 **位移距离** 与 **视频帧率 (FPS)** 计算目标移动速率。
4. 通过 `solutions.SpeedEstimator.estimate_speed(im0)` 把速度结果叠加到视频帧并写出。

**数据流**(以第一个代码示例为依据):

- **输入**:`cv2.VideoCapture("Path/to/video/file.mp4")` 打开的视频文件。
- **中间参数**:`w, h, fps = (int(cap.get(x)) for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))`,从视频头获取宽度、高度、帧率。
- **处理**:`speed = solutions.SpeedEstimator(model="yolo11n.pt", region=speed_region, show=True)`,在每帧循环内 `out = speed.estimate_speed(im0)`。
- **输出**:`cv2.VideoWriter("speed_management.avi", cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))` 把 `im0` 写出为 mp4v 编码的 AVI 文件。
- **可视化**:当 `show=True` 时弹窗实时显示。
- **退出**:`cv2.waitKey(1) & 0xFF == ord("q")` 时跳出循环,释放摄像头与窗口。

**准确性依赖**(原文):测速精度取决于目标跟踪质量、视频分辨率与帧率,以及环境变量;由于帧处理速度差异与遮挡,结果**可能不是 100% 准确**。

**框架互操作**:`yolo export --weights yolo11n.pt --include onnx` 可导出为 ONNX,文档称同样支持 TensorRT、CoreML 等格式(以利于跨框架部署)。

---

## 【表格解读】

### 表格 1 — Real World Applications

原文是一个 2 列 × 1 行的展示型表格,内容为两张示例图片,无参数列。逐字还原如下:

| Transportation | Transportation |
| :---: | :---: |
| ![Speed Estimation on Road using Ultralytics YOLO11](https://github.com/ultralytics/docs/releases/download/0/speed-estimation-on-road-using-ultralytics-yolov8.avif) | ![Speed Estimation on Bridge using Ultralytics YOLO11](https://github.com/ultralytics/docs/releases/download/0/speed-estimation-on-bridge-using-ultralytics-yolov8.avif) |
| Speed Estimation on Road using Ultralytics YOLO11 | Speed Estimation on Bridge using Ultralytics YOLO11 |

**逐行解读**:

- 此表用以**视觉化呈现速度估算的两种典型交通场景**:道路场景与桥梁场景。表格本身**不包含数值参数或对比数据**,其作用是替代文字描述,直观展示测速功能在现实交通监控中的可应用形态。资源托管在 `github.com/ultralytics/docs/releases/download/0/` 下,文件名为 `speed-estimation-on-road-using-ultralytics-yolov8.avif` 与 `speed-estimation-on-bridge-using-ultralytics-yolov8.avif`(注意:虽然是 YOLOv8 仓库路径下的文档,图片资源仍沿用旧名)。

### 表格 2 — `SpeedEstimator` Arguments

逐字还原如下:

| Name         | Type   | Default                    | Description                                          |
| ------------ | ------ | -------------------------- | ---------------------------------------------------- |
| `model`      | `str`  | `None`                     | Path to Ultralytics YOLO Model File                  |
| `region`     | `list` | `[(20, 400), (1260, 400)]` | List of points defining the counting region.         |
| `line_width` | `int`  | `2`                        | Line thickness for bounding boxes.                   |
| `show`       | `bool` | `False`                    | Flag to control whether to display the video stream. |

**逐行解读**:

- `model`: 字符串类型,默认 `None`,描述为"Ultralytics YOLO 模型文件的路径"。两个代码示例都显式传入 `"yolo11n.pt"` 覆盖默认,说明此参数必须实际指向一个权重文件才能工作。
- `region`: 列表类型,默认 `[(20, 400), (1260, 400)]`,即一条从 `(20, 400)` 到 `(1260, 400)` 的水平线段(两点)。描述写的是"counting region",与本文档"speed estimation region"在功能上一致——都是定义要落入统计/测算的多边形(或线)区域。示例代码里也演示了 4 点 `[(20, 400), (1080, 404), (1080, 360), (20, 360)]` 这种近似矩形的形态。
- `line_width`: 整数,默认 `2`,控制绘制边界框 (bounding boxes) 时的线宽,影响可视化粗细。
- `show`: 布尔,默认 `False`,决定是否弹窗显示视频流;示例代码均设为 `True`,便于人工观察测速叠加效果。

> **注意**:表格下方还有 `### Arguments model.track`,原文以 `{% include "macros/track-args.md" %}` 形式引用了另一个宏文件,本文档中**未展开其内容**,因此该部分参数无法在此处逐字还原。

---

## 【公式解读】

原文无公式。

文档从语义层给出的是**速度估算的隐含公式**:**速度 ∝ 位移距离 / 时间间隔**,其中:
- "位移距离"由帧间跟踪得到的坐标差提供;
- "时间间隔"由视频帧率 (`cv2.CAP_PROP_FPS`) 提供。

但**该公式并未在原文中以 LaTeX、伪代码或文本形式显式列出**,故遵从"原文无公式"的要求,不做还原。

---

## 【关联】

依据文中出现的链接与模块引用,本文档与以下特性/模块相关:

1. **[`../modes/track.md`](../modes/track.md)** — 文档核心机制依赖目标跟踪 (object tracking),并通过 `{% include "macros/track-args.md" %}` 引入 `model.track` 的参数说明;速度估算本质上是"跟踪 + 距离/时间"的延伸。
2. **[`../modes/export.md`](../modes/export.md)** — FAQ 中将测速模型导出 (ONNX/TensorRT/CoreML) 指向该导出指南,说明速度估算能力需要在模型可部署/可互操作的导出链路中工作。
3. **[`../models/yolov8.md`](../models/yolov8.md)** — 文末内部链接列表中显式给出的 YOLOv8 模型说明页;虽然本文档标题与示例均使用 YOLO11,但仍指向该模型页,体现"系列兼容性 / 模型选择"的关联(原仓库路径 `Yolov8_for_PyTorch` 也印证这一点)。
4. **跨模块依赖**:
   - `ultralytics.solutions.SpeedEstimator` 是 `solutions` 模块下的解决方案类。
   - 测速精度受上游 `object tracking` 质量影响(参见 FAQ 关于"accuracy depends on several factors, including the quality of the object tracking"的表述)。
   - 与 `object detection` 概念相连(见 FAQ 首段"detect objects in each frame using the YOLO11 model")。
5. **外部资源**:
   - 官方博客:[Ultralytics YOLO11 for Speed Estimation in Computer Vision Projects](https://www.ultralytics.com/blog/ultralov8-yolov8-for-speed-estimation-in-computer-vision-projects) — 提供更深入的解读。
   - 术语库:文中链接到 `computer-vision-cv`、`object-detection`、`accuracy`、`tensorflow`、`pytorch` 等术语条目。

---

## 【使用方法】

**启用方式**(Python):

```python
from ultralytics import solutions
speed = solutions.SpeedEstimator(model="yolo11n.pt", region=speed_region, show=True)
out = speed.estimate_speed(im0)
```

**关键配置项**(来自原文 `SpeedEstimator` Arguments 表格):

| 参数 | 类型 | 默认 | 说明 |
|---|---|---|---|
| `model` | `str` | `None` | YOLO 模型权重路径 |
| `region` | `list` | `[(20, 400), (1260, 400)]` | 测速/计数区域多边形点列表 |
| `line_width` | `int` | `2` | 边界框线宽 |
| `show` | `bool` | `False` | 是否实时弹窗显示 |

**完整最小流水线**(原文已给出两版,综合为一份):

```python
import cv2
from ultralytics import solutions

cap = cv2.VideoCapture("path/to/video/file.mp4")
w, h, fps = (int(cap.get(x)) for x in (
    cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))

video_writer = cv2.VideoWriter(
    "speed_estimation.avi",
    cv2.VideoWriter_fourcc(*"mp4v"),
    fps, (w, h))

speed_obj = solutions.SpeedEstimator(
    region=[(0, 360), (1280, 360)],
    model="yolo11n.pt",
    show=True,
)

while cap.isOpened():
    success, im0 = cap.read()
    if not success:
        break
    im0 = speed_obj.estimate_speed(im0)
    video_writer.write(im0)

cap.release()
video_writer.release()
cv2.destroyAllWindows()
```

**模型导出命令**(原文 FAQ 提供):

```bash
yolo export --weights yolo11n.pt --include onnx
```

**退出控制**:在带显示的循环中可由用户按 `q` 退出 (`cv2.waitKey(1) & 0xFF == ord("q")`)。

**额外约束(原文明确说明)**:
- 速度为估算值,可能不准确。
- 估算结果会因 **GPU 速度**不同而出现差异(部署时应固定硬件或做相对比较)。
- 测速精度受目标跟踪质量、视频分辨率/帧率与环境变量共同影响。
