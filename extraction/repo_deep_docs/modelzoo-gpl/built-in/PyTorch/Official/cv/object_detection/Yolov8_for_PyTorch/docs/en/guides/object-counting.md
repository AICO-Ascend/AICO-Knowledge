# Object Counting using Ultralytics YOLO11

> 仓 `modelzoo-gpl` · 路径 `built-in/PyTorch/Official/cv/object_detection/Yolov8_for_PyTorch/docs/en/guides/object-counting.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-gpl/built-in/PyTorch/Official/cv/object_detection/Yolov8_for_PyTorch/docs/en/guides/object-counting.md

# 一体化深度解读：Object Counting using Ultralytics YOLO11

## 【定位】

这篇文档介绍了如何使用 Ultralytics YOLO11 在视频与摄像头流中**实时识别并计数特定目标对象**，覆盖人群分析、安防监控、传送带包装计数、水产养殖等场景，是面向 `solutions.ObjectCounter` 的多模式（区域/线/多边形/OBB/指定类别）实战指南。

---

## 【技术要点】

1. **核心类与入口**：使用 `from ultralytics import solutions`，实例化 `solutions.ObjectCounter(show=True, region=…, model=…)`，调用 `counter.count(im0)` 对每帧执行计数。
2. **支持的计数几何模式**（原文给出 5 段独立示例）：
   - **Count in Region**：四边形区域 `[(20, 400), (1080, 404), (1080, 360), (20, 360)]`，模型 `yolo11n.pt`。
   - **OBB Object Counting**（有向框）：模型切换为 `yolo11n-obb.pt`，`region` 改为 `line_points=[(20, 400), (1080, 400)]`。
   - **Count in Polygon**：闭合多边形 `[(20, 400), (1080, 404), (1080, 360), (20, 360), (20, 400)]`（末点与首点重合以闭合）。
   - **Count in Line**：单线段 `[(20, 400), (1080, 400)]`。
   - **Specific Classes**：通过 `classes=[0, 1]` 仅对指定类目（原文示例中被截断，参数列表可读到 `model="yolo11n.pt"` 与 `classes=[0, 1]`）。
3. **视频 I/O 参数**：输出文件 `object_counting_output.avi`，编解码 `cv2.VideoWriter_fourcc(*"mp4v")`，分辨率与帧率从 `cv2.CAP_PROP_FRAME_WIDTH / FRAME_HEIGHT / FPS` 读取后回传给 VideoWriter，保证与输入一致。
4. **循环处理流程**：`cap.isOpened()` 判断打开 → `cap.read()` 取帧 → 失败打印 `"Video frame is empty or video processing has been successfully completed."` 并 `break` → `counter.count(im0)` → `video_writer.write(im0)` → 结束统一 `cap.release() / video_writer.release() / cv2.destroyAllWindows()`。
5. **断言与异常信息**：`assert cap.isOpened(), "Error reading video file"`；空帧/完成时统一输出固定字符串提示。
6. **算法优势定位**（原文用语）：强调 *state-of-the-art algorithms* 与 *deep learning capabilities* 带来的实时性与精度，用于 crowd analysis、surveillance 等。

---

## 【关键机制与数据】

- **工作原理（原文描述）**：YOLO11 先检测出对象，再通过区域/线/多边形/OBB 等几何规则判定对象是否"进入"或"穿越"计数区，从而累计数量（原文未给出具体的跨线判定公式与计数阈值，原文亦无帧率、mAP、显存等性能数字）。
- **数据流**：`cv2.VideoCapture` 读取 → `counter.count(im0)` 处理 → `cv2.VideoWriter` 写出 `object_counting_output.avi`，旁路可设 `show=True` 直接弹窗可视化。
- **多模式差异**（原文用代码区分，并未给出参数表）：
  - `model="yolo11n.pt"`：标准检测框，配合 `region` 多边形用于 Region/Polygon。
  - `model="yolo11n-obb.pt"`：OBB 旋转框，配合线段 `line_points` 使用。
  - `classes=[0, 1]`：限定参与计数的类别索引（原文未说明 0/1 对应 COCO 哪一类）。
- **性能数据**：原文未提供任何精度/速度基准数字。

---

## 【表格解读】

### 表格 1：文档开头的双视频嵌入表（原文逐字还原）

| 单元格 1（视频卡片） | 单元格 2（视频卡片） |
|---|---|
| `<iframe loading="lazy" width="720" height="405" src="https://www.youtube.com/embed/Ag2e-5_NpS0" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>`<br>**Watch:** Object Counting using Ultralytics YOLO11 | `<iframe loading="lazy" width="720" height="405" src="https://www.youtube.com/embed/Fj9TStNBVoY" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>`<br>**Watch:** Class-wise Object Counting using Ultralytics YOLO11 |

逐行解读：
- 两个单元格各自内嵌一支 YouTube 演示视频（`720×405`），属性 `loading="lazy"` 表示懒加载，`allow` 全集全开（自动播放、画中画、全屏等）。
- 左侧视频主题：**通用对象计数**（不分类别）；右侧视频主题：**类对象计数（Class-wise）**，对应文档下文 `classes=[0, 1]` 的示例。

### 表格 2：Real World Applications（原文逐字还原）

| Logistics | Aquaculture |
| :---: | :---: |
| ![Conveyor Belt Packets Counting Using Ultralytics YOLO11](https://github.com/ultralytics/docs/releases/download/0/conveyor-belt-packets-counting.avif) | ![Fish Counting in Sea using Ultralytics YOLO11](https://github.com/ultralytics/docs/releases/download/0/fish-counting-in-sea-using-ultralytics-yolov8.avif) |
| **Conveyor Belt Packets Counting Using Ultralytics YOLO11** | **Fish Counting in Sea using Ultralytics YOLO11** |

逐行解读：
- **Logistics（物流）**：用 YOLO11 在传送带上计数包裹/包装件，是"资源优化（Resource Optimization）"优势的典型落地——> 原文将其对应到 *inventory management* 类应用。
- **Aquaculture（水产养殖）**：在海面/水下计数鱼群，呼应"信息决策（Informed Decision-Making）"中关于渔业资源管理的潜在用法（原文未直接点名，但列在该栏）。
- 注意：右侧鱼群示例图片文件名仍含 `yolov8`，是历史素材，文档主体已统一到 YOLO11 措辞。

---

## 【公式解读】

原文无公式。（文档仅以代码示例呈现几何坐标与类索引，没有给出数学表达式。）

---

## 【关联】

- **上游框架**：文中所有示例都基于 `from ultralytics import solutions` 的高层 `solutions.ObjectCounter`，并显式链接到 [Ultralytics YOLO11](https://github.com/ultralytics/ultralytics/) 项目仓库，以及 [deep learning](https://www.ultralytics.com/glossary/deep-learning-dl) 术语页。
- **与本仓其他 docs 的关联**：本仓是 `modelzoo-gpl`，该指南位于 `Yolov8_for_PyTorch/docs/en/guides/object-counting.md` 路径下，说明它是 Ultralytics 官方文档在 GPL 仓库的镜像；文档自身未提供文末"内部链接"清单（任务输入已注明 *内部链接: (无)*）。
- **与同类指南的关系**：从 "Object Counting → Class-wise Object Counting" 的视频标题可以推断，类对象计数是该能力的一个子集，与 `classes` 参数的过滤功能相对应。

---

## 【使用方法】

1. **环境与导入**：`from ultralytics import solutions`；同时需要 `cv2`（OpenCV）。
2. **视频读取**：`cv2.VideoCapture("path/to/video/file.mp4")` + `assert cap.isOpened(), "Error reading video file"`；分辨率与 fps 用 `cv2.CAP_PROP_FRAME_WIDTH / FRAME_HEIGHT / FPS` 读取。
3. **定义几何**（按场景择一）：
   - 区域/多边形：`region_points = [(20, 400), (1080, 404), (1080, 360), (20, 360)]`（多边形模式再追加首点闭合）。
   - 线/OBB：`line_points = [(20, 400), (1080, 400)]`。
4. **初始化计数器**：`solutions.ObjectCounter(show=True, region=…, model="yolo11n.pt" | "yolo11n-obb.pt", classes=[0, 1] …)`；`show=True` 实时弹窗。
5. **视频写出**：`cv2.VideoWriter("object_counting_output.avi", cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))`，与输入分辨率/fps 保持一致。
6. **主循环**：`while cap.isOpened(): success, im0 = cap.read(); … im0 = counter.count(im0); video_writer.write(im0)`；结束统一 `release()` + `cv2.destroyAllWindows()`。
7. **CLI/配置项**（命令行调用、超参数 yaml 等）：原文未涉及。
