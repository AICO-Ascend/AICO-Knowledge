# Analytics using Ultralytics YOLO11

> 仓 `modelzoo-gpl` · 路径 `built-in/PyTorch/Official/cv/object_detection/Yolov8_for_PyTorch/docs/en/guides/analytics.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-gpl/built-in/PyTorch/Official/cv/object_detection/Yolov8_for_PyTorch/docs/en/guides/analytics.md

# 深度解读：Analytics using Ultralytics YOLO11

---

## 【定位】

这篇文档是 Ultralytics YOLO11（原仓库路径为 `built-in/PyTorch/Official/cv/object_detection/Yolov8_for_PyTorch/docs/en/guides/analytics.md`）中关于**视频分析可视化能力**的使用指南，专门解决"如何在视频流处理过程中，实时叠加/更新折线图、柱状图、面积图、饼图等数据分析图表"的问题，提供基于 `solutions.Analytics` 类的端到端代码示例。

---

## 【技术要点】

1. **核心类与导入**：通过 `from ultralytics import solutions` 引入 `solutions.Analytics` 类，使用 `cv2.VideoCapture` 读取视频、`cv2.VideoWriter` 写入视频，是典型的 OpenCV + Ultralytics solutions 子系统集成模式。
2. **四类图表类型**：通过 `analytics_type` 参数切换 `"line"`、`"bar"`、`"area"`、`"pie"` 四种可视化形式，文档为每种都给出独立且结构完全一致的代码片段。
3. **输出视频固定规格**：所有示例均使用 `cv2.VideoWriter_fourcc(*"MJPG")` 编码器，并以注释明示**`(1920, 1080)` 固定输出分辨率**（原文：`# This is fixed`），fps 从输入视频读取。
4. **帧级更新机制**：通过 `frame_count += 1` 自增计数器，并在循环中调用 `analytics.process_data(im0, frame_count)`（注释：`update analytics graph every frame`），实现"每帧推进一次图表"的时间序列更新。
5. **参数对象**：`Analytics` 类共暴露 4 个参数：`analytics_type`、`model`、`line_width`、`show`；其中 `model` 用于指向 YOLO 模型文件，`line_width=2` 控制框线粗细。
6. **关联到跟踪模块**：在 `Arguments model.track` 一节中通过宏 `{% include "macros/track-args.md" %}` 引入 track 参数，说明 analytics 在底层与 `model.track`（目标跟踪）的对象统计结果绑定。

---

## 【关键机制与数据】

**工作原理与数据流（基于原文代码逻辑还原）：**

1. 原文：`cap = cv2.VideoCapture("Path/to/video/file.mp4")` → 打开视频源。
2. 原文：`assert cap.isOpened(), "Error reading video file"` → 视频源校验。
3. 原文：`w, h, fps = (int(cap.get(x)) for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))` → 读取原始宽/高/帧率。
4. 原文：`out = cv2.VideoWriter("ultralytics_analytics.avi", cv2.VideoWriter_fourcc(*"MJPG"), fps, (1920, 1080))` → 以 MJPG 编码、固定 1920×1080 写出 avi。
5. 原文：`analytics = solutions.Analytics(analytics_type="line"/"bar"/"area"/"pie", show=True)` → 构造分析器。
6. 原文：`im0 = analytics.process_data(im0, frame_count)` → 逐帧调用 `process_data`，传入当前帧 `im0` 与帧号 `frame_count`，方法内对画面叠加可视化图表后返回。
7. 原文：`out.write(im0)` → 写回输出文件。
8. 原文：`cap.release(); out.release(); cv2.destroyAllWindows()` → 释放资源。

**性能数据**：原文未提供任何 fps 基准、延迟或吞吐量数字；唯一"硬"数字是输出分辨率 `(1920, 1080)`、编码 `"MJPG"` 与 `line_width` 默认 `2`。

**为什么需要图表（原文叙述）：**
- 折线图：跟踪短期/长期变化，比较同一时段内多个组的变化。
- 柱状图：跨类别数量对比，展示类别与其数值关系。
- 饼图：展示各类别占比，呈现"部分与整体"关系。

---

## 【表格解读】

### 表格 1：Visual Samples（视觉样例）

| Line Graph | Bar Plot | Pie Chart |
| :---: | :---: | :---: |
| ![Line Graph](https://github.com/ultralytics/docs/releases/download/0/line-graph.avif) | ![Bar Plot](https://github.com/ultralytics/docs/releases/download/0/bar-plot.avif) | ![Pie Chart](https://github.com/ultralytics/docs/releases/download/0/pie-chart.avif) |

**逐行解读**：该表为视觉预览表，无文字参数，仅用三张图像分别展示折线图、柱状图、饼图的渲染效果，便于读者在阅读代码前先建立直观印象。链接均为 Ultralytics docs 仓库中的 `.avif` 静态资源。

### 表格 2：`Analytics` 参数表（原文逐字还原）

| Name             | Type   | Default | Description                                          |
| ---------------- | ------ | ------- | ---------------------------------------------------- |
| `analytics_type` | `str`  | `line`  | Type of graph i.e "line", "bar", "area", "pie"       |
| `model`          | `str`  | `None`  | Path to Ultralytics YOLO Model File                  |
| `line_width`     | `int`  | `2`     | Line thickness for bounding boxes.                   |
| `show`           | `bool` | `False` | Flag to control whether to display the video stream. |

**逐行解读：**
- **`analytics_type` (str, 默认 `"line"`)**：决定可视化形态，可选 `"line"/"bar"/"area"/"pie"` 四种；示例代码正是通过切换该字段触发不同渲染逻辑。
- **`model` (str, 默认 `None`)**：指向 YOLO 模型文件路径；该字段是 analytics 与 `model.track` 关联的入口，使分析数据可来自模型检测/跟踪结果。
- **`line_width` (int, 默认 `2`)**：边框线宽（绑定框线粗细），用于图表或检测框的视觉强调程度。
- **`show` (bool, 默认 `False`)**：是否实时弹窗显示视频流；示例中均设为 `True`，方便调试，正式写入文件时通常保持默认或仅依靠 `out.write`。

---

## 【公式解读】

原文无公式。文档为应用层使用指南，全部"计算"均以 Python 代码片段呈现（如 `frame_count += 1`），未给出任何 LaTeX 数学公式或算法伪代码。

---

## 【关联】

文档主要通过以下路径与 Ultralytics 其他模块产生联系：

- **`{% include "macros/track-args.md" %}` 宏引用**：在 *Arguments `model.track`* 一节中，原文以宏包含方式引入 `model.track` 的参数文档（这通常意味着 track 模块的所有 `tracker`、`persist`、`classes`、`iou` 等参数同样适用于 analytics 场景，因为 analytics 在底层依赖 `model.track` 拿到带轨迹 ID 的检测结果，再据此聚合统计量）。
- **内部链接 `../modes/track.md`**（题目给定）：与 `model.track` 模式相关，说明 analytics 是建立在跟踪模式之上的"分析层"——它消费跟踪输出，而非直接消费原始检测结果。
- **`solutions` 子系统**：作为 Ultralytics Solutions 套件之一，与同级的 `solutions.BlobTracking`、`solutions.Heatmap`、`solutions.QueueManager` 等共享同一 import 路径（`from ultralytics import solutions`），属于 solutions 体系下的"通用分析仪表盘"。
- **与 YOLO 模型关系**：通过 `model` 参数显式接收模型路径，是 `YOLO(model).track(...)` → `Analytics.process_data(...)` 数据流的关键节点。

---

## 【使用方法】

**启用方式（原文代码示例直接给出）：**

1. **安装与导入**：使用 `from ultralytics import solutions` 引入 `Analytics`；视频读写依赖 OpenCV（`import cv2`）。
2. **构造分析器（关键调用）**：

```python
analytics = solutions.Analytics(
    analytics_type="line",   # 或 "bar" / "area" / "pie"
    show=True,
)
```

3. **关键参数说明（原文表格已列出）：**

| 配置项 | 类型 | 默认 | 作用 |
| --- | --- | --- | --- |
| `analytics_type` | str | `line` | 图表类型 |
| `model` | str | `None` | YOLO 模型路径 |
| `line_width` | int | `2` | 边框线宽 |
| `show` | bool | `False` | 是否实时显示视频流 |

4. **运行命令**：原文未涉及 CLI 命令（如 `yolo track ...`）；所有使用方式均以 Python 脚本呈现。

5. **输出文件**：默认生成 `ultralytics_analytics.avi`，编码 `MJPG`，分辨率固定 `1920×1080`（原文：`# This is fixed`）。

6. **底层跟踪参数**：通过 `{% include "macros/track-args.md" %}` 复用 track 模式参数，原文未在该文档内逐条列出，需跳转至 `../modes/track.md` 查看完整选项。
