# Distance Calculation using Ultralytics YOLO11

> 仓 `modelzoo-gpl` · 路径 `built-in/PyTorch/Official/cv/object_detection/Yolov8_for_PyTorch/docs/en/guides/distance-calculation.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-gpl/built-in/PyTorch/Official/cv/object_detection/Yolov8_for_PyTorch/docs/en/guides/distance-calculation.md

# 一体化深度解读:Yolov8_for_PyTorch — distance-calculation.md

## 【定位】

这篇文档介绍 Ultralytics YOLO11 中基于边界框(bounding box)质心(centroid)进行**两点距离测算**的能力,提供交互式取点方式(鼠标左键选框、右键清点)与视频流实时测距的 Python 实现,用于目标空间定位、尺寸估计与场景理解。

---

## 【技术要点】

1. **质心驱动测距**:以 YOLO11 检测输出的 bounding box 质心为基准,在用户选中的两个边界框之间计算距离。
2. **交互式取点机制**:
   - **左键单击**:在任意两个 bounding box 上点击,触发距离测算并绘制连线/标注。
   - **右键单击**:清除已绘制的所有点。
3. **二维数据本质**:距离是基于 2D 图像数据估算的,缺乏物体深度信息,因此官方明确标注"Distance is Estimate",数值非完全精确。
4. **初始化核心类**:`solutions.DistanceCalculation(model="yolo11n.pt", show=True)`,默认使用 `yolo11n.pt` 模型。
5. **三类配置参数**(下表逐字还原):`model`(str,默认 `None`)、`line_width`(int,默认 `2`)、`show`(bool,默认 `False`)。
6. **视频流处理流程**:OpenCV 读帧 → `distance.calculate(im0)` 逐帧测距 → `cv2.VideoWriter` 输出 `distance_calculation.avi`(fourcc 为 `mp4v`,FPS 与分辨率继承自源视频)。

---

## 【关键机制与数据】

- **工作原理**:文档未公开内部算法推导或计算公式,仅描述"以 bounding box 质心进行测距"。原文明确指出距离是基于 2D 像素坐标计算得到的欧氏距离近似值。
- **数据流(原文示例代码)**:
  1. `cv2.VideoCapture("Path/to/video/file.mp4")` 打开视频;
  2. 通过 `(cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FRAME_FPS)` 读取 `w, h, fps`;
  3. `cv2.VideoWriter("distance_calculation.avi", cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))` 初始化写盘;
  4. `distance.calculate(im0)` 逐帧处理并叠加可视化;
  5. `cap.release()` / `video_writer.release()` / `cv2.destroyAllWindows()` 收尾。
- **性能数据**:原文未提供任何量化指标(无 FPS 基准、无精度数值、无误差范围)。
- **三大优势(原文)**:
  - **Localization Precision**:增强空间定位精度;
  - **Size Estimation**:辅助物体尺寸估计;
  - **Scene Understanding**(FAQ 中补充):增强 3D 场景理解,服务于自动驾驶、监控等场景。

---

## 【表格解读】

**原文表格 — `DistanceCalculation()` 初始化参数(逐字还原):**

| `Name`       | `Type` | `Default` | Description                                          |
| ------------ | ------ | --------- | ---------------------------------------------------- |
| `model`      | `str`  | `None`    | Path to Ultralytics YOLO Model File                  |
| `line_width` | `int`  | `2`       | Line thickness for bounding boxes.                   |
| `show`       | `bool` | `False`   | Flag to control whether to display the video stream. |

**逐行解读:**

- **`model`(`str`,默认 `None`)** — Ultralytics YOLO 模型权重路径字符串。在示例代码中显式传入 `"yolo11n.pt"`,即 YOLO11 的 nano 轻量模型,适合实时视频流测距。
- **`line_width`(`int`,默认 `2`)** — bounding box 边界及测距连线的绘制线宽(像素)。调大可使标注在远景/小目标场景下更醒目。
- **`show`(`bool`,默认 `False`)** — 是否实时显示视频流的开关。示例中置 `True` 以便在屏幕上观察取点、连线效果。

> 此外,文档引用宏 `{% include "macros/track-args.md" %}` 间接引入 `model.track` 参数(原文未展开其内容,本仓目录无该宏实体),故本节不臆测其参数表。

---

## 【公式解读】

原文无公式。

文档未给出质心坐标提取公式、欧氏距离表达式或任何投影变换公式,仅以自然语言说明"bounding box centroid is employed to calculate the distance"。

---

## 【关联】

- **上游依赖 — Ultralytics YOLO11**:测距能力建立在 YOLO11 的目标检测/跟踪输出(边界框)之上,继承 `ultralytics` 库的 `solutions` 子模块。
- **依赖模块 — OpenCV**:负责视频捕获(`cv2.VideoCapture`)、帧写入(`cv2.VideoWriter`)、窗口销毁(`cv2.destroyAllWindows`),不参与距离计算本身。
- **同源能力关联**(文档 FAQ 与术语提示):
  - **Object Detection / Object Tracking**:测距以检测得到的 bounding box 为输入;
  - **Precision(精度)**:文档将"Localization Precision"列为优势之一,链接至 Ultralytics glossary;
  - **Computer Vision**:将测距定位于通用 CV 任务;
  - **Bounding Box**:作为输入与质心提取的载体。
- **应用场景关联(原文 FAQ 提及)**:自动驾驶(autonomous driving)与监控(surveillance)。
- **本仓库结构**:文档位于 `built-in/PyTorch/Official/cv/object_detection/Yolov8_for_PyTorch/docs/en/guides/distance-calculation.md`,属于 Ultralytics 官方 guide 集合的本地镜像,本仓目录未提供可点击的内部链接。

---

## 【使用方法】

**1. 安装与导入**(原文示例):
```python
import cv2
from ultralytics import solutions
```

**2. 视频流测距完整流程**(原文逐字保留):
```python
cap = cv2.VideoCapture("Path/to/video/file.mp4")
assert cap.isOpened(), "Error reading video file"
w, h, fps = (int(cap.get(x)) for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))

# Video writer
video_writer = cv2.VideoWriter("distance_calculation.avi", cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))

# Init distance-calculation obj
distance = solutions.DistanceCalculation(model="yolo11n.pt", show=True)

while cap.isOpened():
    success, im0 = cap.read()
    if not success:
        print("Video frame is empty or video processing has been successfully completed.")
        break
    im0 = distance.calculate(im0)
    video_writer.write(im0)

cap.release()
video_writer.release()
cv2.destroyAllWindows()
```

**3. 交互操作(原文):**
- **左键单击** bounding box — 选点并测算两点距离;
- **右键单击** — 清除所有已绘制的点。

**4. 关键配置项:**
| 参数 | 默认值 | 作用 |
| --- | --- | --- |
| `model` | `None` | 指向 YOLO11 权重文件(示例用 `yolo11n.pt`) |
| `line_width` | `2` | 边框/连线绘制线宽 |
| `show` | `False` | 是否实时显示画面 |

**5. 注意事项(原文):**
- 距离仅是基于 2D 数据的**估算值**,不包含深度信息,可能不精确;
- 输出文件名固定为 `distance_calculation.avi`,fourcc 为 `mp4v`;
- `model.track` 参数通过 `macros/track-args.md` 引入,本仓目录未提供该宏原文,故具体字段以 Ultralytics 官方文档为准。

> **原文未涉及**的内容:CLI 命令行调用方式、Docker/昇腾 NPU 适配开关、性能调优参数(如 conf、iou 阈值,虽通过 track-args 宏引入但本仓未展开)。
