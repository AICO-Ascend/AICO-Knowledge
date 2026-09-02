# Instance Segmentation and Tracking using Ultralytics YOLO11 🚀

> 仓 `modelzoo-gpl` · 路径 `built-in/PyTorch/Official/cv/object_detection/Yolov8_for_PyTorch/docs/en/guides/instance-segmentation-and-tracking.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-gpl/built-in/PyTorch/Official/cv/object_detection/Yolov8_for_PyTorch/docs/en/guides/instance-segmentation-and-tracking.md

# 一体化深度解读：Instance Segmentation and Tracking using Ultralytics YOLO11

---

## 【定位】

这篇文档是 Ultralytics YOLO11 的「实例分割 + 目标跟踪」能力的使用指南，阐述如何利用 YOLO11 的分割模型（`yolo11n-seg.pt`）对视频帧中的每个目标进行像素级轮廓勾勒，并提供"按类别着色"与"按轨迹 ID 着色"两种可视化范式的完整可运行 Python 代码样例。

---

## 【技术要点】

1. **两种范式**：文档明确定义了 Ultralytics 包中可用的两种实例分割跟踪方式——① *Instance Segmentation with Class Objects*（按 class 着色，相同类别同色），② *Instance Segmentation with Object Tracks*（按 track 着色，相同轨迹同色）。
2. **分割模型加载**：使用 `YOLO("yolo11n-seg.pt")` 加载 YOLO11 的分割权重（即文件名后缀 `-seg`）。
3. **推理接口差异**：
   - 纯分割：调用 `model.predict(im0)`
   - 分割 + 跟踪：调用 `model.track(im0, persist=True)`（`persist=True` 用于在帧间维持 track 状态）。
4. **结果对象字段**：返回 `Results` 对象的 `results[0]` 上：
   - `results[0].boxes.cls.cpu().tolist()` → 类别 id 列表
   - `results[0].masks.xy` → 每实例的分割轮廓坐标
   - `results[0].boxes.id.int().cpu().tolist()` → 仅跟踪模式下存在的 track id 列表
5. **绘制工具**：使用 `ultralytics.utils.plotting.Annotator` 与 `colors(int(idx), True)` 生成一致颜色，配合 `annotator.seg_bbox(mask, mask_color, label, txt_color)` 在视频帧上叠加分割多边形与标签。
6. **视频 I/O 与退出**：使用 OpenCV `cv2.VideoCapture` 读帧、`cv2.VideoWriter(..., cv2.VideoWriter_fourcc(*"MJPG"), fps, (w, h))` 写入 MJPG 编码 `.avi`，按 `cv2.waitKey(1) & 0xFF == ord("q")` 终止。

---

## 【关键机制与数据】

**数据流（纯分割范式，原文代码）**：
1. `cap = cv2.VideoCapture("path/to/video/file.mp4")` 读取视频。
2. 通过 `(cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS)` 三元组一次性获取 `w, h, fps`。
3. `model.predict(im0)` → `results`；`results[0].masks is not None` 判定有无分割结果。
4. 遍历 `zip(masks, clss)`，对每个 mask 用 `colors(int(cls), True)` 取色，调用 `annotator.seg_bbox(mask, mask_color=color, label=names[int(cls)], txt_color=txt_color)`。
5. 写帧到 `instance-segmentation.avi` 并 `cv2.imshow` 显示。

**数据流（分割 + 跟踪范式，原文代码）**：
1. `track_history = defaultdict(lambda: [])`（声明但在本段代码中**未实际用于绘制**）。
2. `model.track(im0, persist=True)` 同时输出 `boxes.id` 与 `masks`。
3. 仅当 `results[0].boxes.id is not None and results[0].masks is not None` 时进入绘制循环。
4. 按 `track_id` 取色 `colors(int(track_id), True)`，标签写为 `str(track_id)`。
5. 写帧到 `instance-segmentation-object-tracking.avi`。

**原文标注的关键事实**：
- 模型文件名为 **`yolo11n-seg.pt`**（YOLO11 nano 分割权重，原文示例）。
- 视频编码：MJPG fourcc，容器 `.avi`。
- 注释线宽：`Annotator(im0, line_width=2)`。
- 视频帧读完时打印：`"Video frame is empty or video processing has been successfully completed."`
- 终止键：`ord("q")`。

**注意**：文档未给出 mAP、FPS、模型参数量、显存占用等任何性能数据，亦未给出训练 / 验证指令，因此本节只描述上述数据流，不臆造性能数字。

---

## 【表格解读】

### 表 1：Samples（视觉对比表，原文逐字还原）

| Instance Segmentation | Instance Segmentation + Object Tracking |
|:---:|:---:|
| ![Ultralytics Instance Segmentation](https://github.com/ultralytics/docs/releases/download/0/ultralytics-instance-segmentation.avif) | ![Ultralytics Instance Segmentation with Object Tracking](https://github.com/ultralytics/docs/releases/download/0/ultralytics-instance-segmentation-object-tracking.avif) |
| Ultralytics Instance Segmentation 😍 | Ultralytics Instance Segmentation with Object Tracking 🔥 |

**解读**：该表为图文对比表，左列为"纯实例分割"效果——每个目标按所属类别统一着色（class-based coloring）；右列为"实例分割 + 目标跟踪"效果——每个目标按其跨帧 track id 着色（track-based coloring）。表本身不携带任何数值参数，仅用于直观对比两种范式的输出差异。

### 表 2：`seg_bbox` Arguments（原文字段逐字还原）

| Name         | Type    | Default         | Description                                  |
| ------------ | ------- | --------------- | -------------------------------------------- |
| `mask`       | `array` | `None`          | Segmentation mask coordinates                |
| `mask_color` | `RGB`   | `(255, 0, 255)` | Mask color for every segmented box           |
| `label`      | `str`   | `None`          | Label for segmented object                   |
| `txt_color`  | `RGB`   | `None`          | Label color for segmented and tracked object |

**逐行解读**：
- `mask`（`array`，默认 `None`）：传入分割多边形的坐标数组，对应代码中 `results[0].masks.xy` 列表中的单个元素。
- `mask_color`（`RGB`，默认 `(255, 0, 255)`，即品红）：用于描画分割掩码/框的颜色；调用时实际通过 `colors(int(cls_or_track_id), True)` 动态生成，因此默认值仅在不传时被使用。
- `label`（`str`，默认 `None`）：叠加在分割框旁的文本标签——纯分割模式下写类别名 `names[int(cls)]`，跟踪模式下写 `str(track_id)`。
- `txt_color`（`RGB`，默认 `None`）：文本字色，由 `annotator.get_txt_color(color)` 根据底色自动选择对比色（黑/白），无需手动指定。

---

## 【公式解读】

**原文无公式。** 文档涉及的核心运算是逐像素掩码绘制与 IoU-based 跟踪，但这些机制在文中**未以任何数学形式或伪代码形式呈现**。`seg_bbox` 的函数语义通过参数表与代码样例表达，未给出闭式表达或 LaTeX 公式，故本节按要求声明"原文无公式"。

---

## 【关联】

- **概念层链接**：文档反复引用 Ultralytics Glossary，对比了三种语义——
  - [Instance Segmentation](https://www.ultralytics.com/glossary/instance-segmentation)（本文主题）
  - [Semantic Segmentation](https://www.ultralytics.com/glossary/semantic-segmentation)（仅按类别不区分个体）
  - [Object Detection](https://www.ultralytics.com/glossary/object-detection)（仅框无掩码）
  明确点出实例分割的独特价值在于"对每个独立目标做独特标记与精确勾勒"，并强调其在目标检测、医学影像中的关键作用。
- **代码模块依赖**：
  - `ultralytics.YOLO` — 模型加载与推理入口；
  - `ultralytics.utils.plotting.Annotator` — 通用可视化绘制器；
  - `ultralytics.utils.plotting.colors` — 一致性调色板（与 `int` 索引一一对应）；
  - `cv2` — 视频读写与显示；
  - `collections.defaultdict` — 跟踪历史容器（声明于跟踪示例，但当前绘制循环未消费其内容）。
- **上下游能力衔接**：与 YOLO11 的 detection / classification / pose estimation 共用同一 `YOLO` 入口，仅通过权重后缀（如 `-seg`）切换任务；`track(persist=True)` 是 detection 与 segmentation 共用的跟踪接口，文档未单独阐述跟踪算法细节（如 BoT-SORT / ByteTrack），仅展示了使用方式。
- **支持渠道**：文末指向 [Ultralytics Issue Section](https://github.com/ultralytics/ultralytics/issues/new/choose) 及 discussion section 作为答疑通道，构成"使用 → 反馈"的闭环。
- **内部链接**：文档 prompt 给出的"内部链接"清单为 *无*，因此本节仅基于文中实际嵌入的外部超链接做关联。

---

## 【使用方法】

**启用方式（原文示例直接复用）**：

1. 准备 YOLO11 分割权重文件 `yolo11n-seg.pt`（位于项目工作目录或可解析路径）。
2. 准备一段本地视频，将其路径替换 `"path/to/video/file.mp4"`。
3. 按需选择两种示例之一运行：
   - **纯分割**：`YOLO("yolo11n-seg.pt")` + `model.predict(im0)`，输出 `instance-segmentation.avi`，标签为类别名。
   - **分割 + 跟踪**：`YOLO("yolo11n-seg.pt")` + `model.track(im0, persist=True)`，输出 `instance-segmentation-object-tracking.avi`，标签为 `track_id`。
4. 在播放窗口按 **`q`** 键优雅退出（`cv2.waitKey(1) & 0xFF == ord("q")`）。

**关键配置项（原文出现的可调参数）**：
- `Annotator(im0, line_width=2)` — 注释线宽（原文固定为 2）。
- `cv2.VideoWriter_fourcc(*"MJPG")` — 视频编码（原文固定为 MJPG）。
- `colors(int(idx), True)` — 第二个参数 `True` 表示使用 bgr-safe 的确定性格子（原文固定）。
- `seg_bbox` 参数：`mask`、`mask_color`(默认 `(255, 0, 255)`)、`label`、`txt_color`（见上文参数表）。

**未在原文出现的配置项**（按要求不臆造，仅声明）：模型尺寸选择（`yolo11s/m/l/x-seg.pt`）、推理分辨率 `imgsz`、置信度阈值 `conf`、IoU 阈值 `iou`、设备选择 `device=`、是否半精度 `half=`、批处理 `batch=`、跟踪器类型 `tracker=` 等参数，原文**未涉及**，故不在此展开。
