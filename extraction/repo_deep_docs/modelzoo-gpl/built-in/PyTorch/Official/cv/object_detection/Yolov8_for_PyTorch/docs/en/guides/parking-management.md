# Parking Management using Ultralytics YOLO11 🚀

> 仓 `modelzoo-gpl` · 路径 `built-in/PyTorch/Official/cv/object_detection/Yolov8_for_PyTorch/docs/en/guides/parking-management.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-gpl/built-in/PyTorch/Official/cv/object_detection/Yolov8_for_PyTorch/docs/en/guides/parking-management.md

# 停车管理 (Parking Management) 文档深度解读

## 【定位】
这篇文档介绍如何基于 Ultralytics YOLO11 构建实时停车场管理系统,核心能力是**车辆检测 + 车位区域多边形标注 + 视频流逐帧车位占用判定**,配套提供点选标注 GUI 工具与可编程视频处理管线。

---

## 【技术要点】

1. **整体工作流分两步**: 先用 `solutions.ParkingPtsSelection()` 在图像上手动画多边形选车位并保存为 JSON; 再用 `solutions.ParkingManagement` 类把视频逐帧送入模型做车位占用判定。
2. **点选工具上限**: 原文明确 "Max Image Size of **1920 * 1080** supported",超过此分辨率的图像不被支持。
3. **核心 API**: 标注工具入口 `solutions.ParkingPtsSelection()`; 处理类 `solutions.ParkingManagement(model=..., json_file=...)`,默认模型为 `yolo11n.pt`。
4. **视频读写约定**: 使用 OpenCV `cv2.VideoCapture` 读取、`cv2.VideoWriter` 写出,编码 `cv2.VideoWriter_fourcc(*"mp4v")`,分辨率与帧率均沿用源视频 (`w, h, fps` 由 `cv2.CAP_PROP_FRAME_WIDTH/HEIGHT/FPS` 获取),输出文件名为 `"parking management.avi"`。
5. **逐帧处理循环**: `while cap.isOpened()` 内 `ret, im0 = cap.read()` → `im0 = parking_manager.process_data(im0)` → `video_writer.write(im0)`,读不到帧即 `break`。
6. **可选参数表只列两项**: `model` (str, 默认 `None`, 含义 "Path to the YOLO11 model")、`json_file` (str, 默认 `None`, 含义 "Path to the JSON file, that have all parking coordinates data");其他可调项通过 `model.track` 的宏文档 `track-args.md` 提供 (该文档以外部 include 形式引入)。

---

## 【关键机制与数据】

**工作原理 (原文措辞整合)**:
- 原文: "Parking management with Ultralytics YOLO11 ensures efficient and safe parking by organizing spaces and monitoring availability."
- 原文: "YOLO11 can improve parking lot management through real-time vehicle detection, and insights into parking occupancy."
- 原文点选工具说明: "Capture a frame from the video or camera stream where you want to manage the parking lot." → 启动 GUI 选图 → "start outlining parking regions by mouse click to create polygons" → "click `save` to store a JSON file with the data in your working directory."
- 原文 FAQ 中关于车位定义的步骤: "1. Capture a frame from a video or camera stream. 2. Use the provided code to launch a GUI for selecting an image and drawing polygons to define parking spaces. 3. Save the labeled data in JSON format for further processing."
- 原文 FAQ 中关于可定制项的说明: "You can adjust parameters such as the **occupied and available region colors**, margins for text display, and much more." (说明 `ParkingManagement` 类支持自定义区域颜色、文字边距等,但具体参数键未在本文档列出。)

**性能/数据**: 原文未给出 mAP、推理时延、显存占用等量化指标,也无 benchmark 数字。

---

## 【表格解读】

### 表 1: Real World Applications (原文表格)

| Parking Management System | Parking Management System |
| :---: | :---: |
| ![Parking lots Analytics Using Ultralytics YOLO11](https://github.com/ultralytics/docs/releases/download/0/parking-management-aerial-view-ultralytics-yolov8.avif) | ![Parking management top view using Ultralytics YOLO11](https://github.com/ultralytics/docs/releases/download/0/parking-management-top-view-ultralytics-yolov8.avif) |
| Parking management Aerial View using Ultralytics YOLO11 | Parking management Top View using Ultralytics YOLO11 |

**逐行解读**:
- 这是 1×2 的图片示意表 (并非参数表),通过两幅真实场景图展示系统输出效果。
- 第一列:航拍视角 (Aerial View) 的停车场,用于体现大面积俯瞰下车位级检测的可行性。
- 第二列:近俯视/顶视 (Top View) 视角,体现单层或小区域车位占用判定的精度。
- 图像资源托管在 `github.com/ultralytics/docs/releases/download/0/...`,文件名带 `yolov8` 字样 (尽管文档标题用 YOLO11),是历史素材复用。

### 表 2: Optional Arguments `ParkingManagement`

| Name | Type | Default | Description |
| --- | --- | --- | --- |
| `model` | `str` | `None` | Path to the YOLO11 model. |
| `json_file` | `str` | `None` | Path to the JSON file, that have all parking coordinates data. |

**逐行解读**:
- `model`: 字符串类型,默认 `None`,传入 YOLO11 权重文件路径 (示例代码中传 `"yolo11n.pt"`,即最小的 nano 版)。
- `json_file`: 字符串类型,默认 `None`,传入由点选工具生成的坐标 JSON (示例代码中传 `"bounding_boxes.json"`,即上一步 `ParkingPtsSelection()` 保存出的车位多边形数据)。
- 原文在 FAQ 中提到可调整 "occupied and available region colors"、"margins for text display" 等,但**这些参数并未在此表中列出**,表明它们要么是 `model.track` 宏 (`track-args.md`) 里的通用追踪参数,要么是 `ParkingManagement` 类内未文档化的扩展项。

### 表 3: `model.track` Arguments
原文: `{% include "macros/track-args.md" %}`,即通过模板宏复用追踪通用参数表,本文档未直接渲染该表内容。

---

## 【公式解读】

原文无公式。

---

## 【关联】

文档内部存在多处**锚点自引用** (即文中锚链跳转到本文档自身的其他小节),梳理如下:

- 视频代码示例章节: `#python-code-for-parking-management` ← 被 FAQ 中"How does Ultralytics YOLO11 enhance parking management systems?"引用。
- 优势章节: `#advantages-of-parking-management-system` ← 被 FAQ 中"What are the benefits of using Ultralytics YOLO11 for smart parking?"引用。
- 点选章节: `#selection-of-points` ← 被 FAQ 中"How can I define parking spaces using Ultralytics YOLO11?"引用。
- 可选参数章节: `#optional-arguments-parkingmanagement` ← 被 FAQ 中"Can I customize the YOLO11 model for specific parking management needs?"引用。
- 应用场景章节: `#real-world-applications` ← 被 FAQ 中"What are some real-world applications..."引用。

外部关联:
- 上游能力: 依赖 Ultralytics 主仓库的 `ultralytics.solutions` 子模块 (`solutions.ParkingPtsSelection` / `solutions.ParkingManagement` 类)。
- 横向依赖: OpenCV (`cv2.VideoCapture`、`cv2.VideoWriter`),用于视频 I/O。
- 模型依赖: YOLO11 权重文件 (`yolo11n.pt`),由 Ultralytics 模型库提供。
- 复用宏: `track-args.md` 来自 `_includes/macros/`,提供追踪通用参数 (如 `tracker`, `persist` 等),该文档本身未渲染。

---

## 【使用方法】

**1. 启用方式 — 点选车位 (Selection of Points)**

```python
from ultralytics import solutions
solutions.ParkingPtsSelection()
```
- 会弹出 GUI;用户先选图,再用鼠标点击勾勒车位多边形,最后 `save` 将多边形坐标写入**当前工作目录**下的 JSON。
- 输入图像分辨率上限: 1920 × 1080。

**2. 启用方式 — 视频级处理 (Python Code)**

最小可用脚本 (原文示例):

```python
import cv2
from ultralytics import solutions

cap = cv2.VideoCapture("Path/to/video/file.mp4")
assert cap.isOpened(), "Error reading video file"
w, h, fps = (int(cap.get(x)) for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))

video_writer = cv2.VideoWriter("parking management.avi", cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))

parking_manager = solutions.ParkingManagement(
    model="yolo11n.pt",           # path to model file
    json_file="bounding_boxes.json",  # path to parking annotations file
)

while cap.isOpened():
    ret, im0 = cap.read()
    if not ret:
        break
    im0 = parking_manager.process_data(im0)
    video_writer.write(im0)

cap.release()
video_writer.release()
cv2.destroyAllWindows()
```

**3. 必填配置项**

| 参数 | 必填性 | 取值 | 作用 |
| --- | --- | --- | --- |
| `model` | 必填 (示例传 `"yolo11n.pt"`) | YOLO11 权重路径 | 用于车辆检测 |
| `json_file` | 必填 (示例传 `"bounding_boxes.json"`) | 上一步点选保存的 JSON | 提供车位多边形坐标 |

**4. 资源释放**: 处理循环结束后必须 `cap.release()` + `video_writer.release()` + `cv2.destroyAllWindows()`,原文代码已给出完整范式。

**5. 进阶可调**: 原文 FAQ 提示可通过 `ParkingManagement` 类的 optional arguments 调整占用/空闲区域颜色、文字边距等可视化样式,但**具体键名未在本文档中给出**;如需追踪相关参数,需查阅被 include 引入的 `track-args.md` 宏文档。
