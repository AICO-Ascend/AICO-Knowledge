# Advanced [Data Visualization](https://www.ultralytics.com/glossary/data-visualization): Heatmaps using Ultralytics YOLO11 🚀

> 仓 `modelzoo-gpl` · 路径 `built-in/PyTorch/Official/cv/object_detection/Yolov8_for_PyTorch/docs/en/guides/heatmaps.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-gpl/built-in/PyTorch/Official/cv/object_detection/Yolov8_for_PyTorch/docs/en/guides/heatmaps.md

# 一体化深度解读:Yolov8_for_PyTorch Heatmaps Guide

## 【定位】

本文档是 Ultralytics YOLO11 在视频帧上生成物体密度热力图(Heatmap)的能力说明与编程示例,面向「将目标检测结果按位置累积叠加为可视化热力矩阵」这一场景,提供从纯热图、线计数、多边形计数、区域计数到指定类别共 5 种典型用法的可运行 Python 代码骨架。

---

## 【技术要点】

1. **核心入口类**:`ultralytics.solutions.Heatmap`,通过 `heatmap.generate_heatmap(im0)` 对单帧图像逐帧处理并就地返回叠加热图后的图像。
2. **模型权重**:示例统一使用 `model="yolo11n.pt"`(YOLO11 Nano 版本,作为轻量级检测器驱动热图位置来源)。
3. **色彩映射**:`colormap=cv2.COLORMAP_PARULA`,使用 OpenCV 的 Parula 色板将累积强度映射为颜色(暖色=高强度,冷色=低值)。
4. **可视化开关**:`show=True`,运行时弹窗实时显示热图叠加结果。
5. **三类空间约束(可选)**:
   - **Line Counting**:`region=[(20, 400), (1080, 404)]`,两点定义一条直线,仅对该线区域累积。
   - **Polygon Counting**:`region=[(20, 400), (1080, 404), (1080, 360), (20, 360), (20, 400)]`,5 个点闭合多边形。
   - **Region Counting**:`region=[(20, 400), (1080, 404), (1080, 360), (20, 360)]`,4 个点构成矩形(未首尾闭合)。
6. **类别过滤**:通过 `classes=[0, 2]` 选择性仅对指定检测类别进行热图累积(示例中省略了 `colormap`,保留默认)。
7. **I/O 管线**:
   - 读:`cv2.VideoCapture("Path/to/video/file.mp4")`,通过 `cv2.CAP_PROP_FRAME_WIDTH/HEIGHT/FPS` 取三参数。
   - 写:`cv2.VideoWriter("heatmap_output.avi", cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))`,输出容器为 AVI、编码 `mp4v`。
8. **迭代终止判断**:`cap.read()` 返回 `success=False` 时打印 `"Video frame is empty or video processing has been successfully completed."` 并跳出循环。

---

## 【关键机制与数据】

- **数据流**(原文通过代码呈现):视频帧 → `cap.read()` → `Heatmap.generate_heatmap(im0)`(内部用 YOLO11 检测 + 位置累积) → `video_writer.write(im0)` → 循环直至帧空。
- **典型坐标**(原文):
  - 线: `(20, 400)` ↔ `(1080, 404)`
  - 矩形区: `(20, 400) (1080, 404) (1080, 360) (20, 360)`
  - 多边形:在矩形基础上加闭合点 `(20, 400)`,共 5 点
- **示例视频帧宽高/FPS**:直接取自原视频(代码中是变量 `w, h, fps`,未给出固定值)。
- **应用领域**(原文):Transportation、Retail(以图片示意,无量化数据)。
- 原文未涉及热图算法细节(如核密度带宽、衰减系数、累积窗口长度等),也未给出性能/精度数据。

---

## 【表格解读】

### 1. 真实应用图示表(原文)

| Transportation | Retail |
| :---: | :---: |
| Ultralytics YOLO11 Transportation Heatmap | Ultralytics YOLO11 Retail Heatmap |
| ![Transportation Heatmap](https://github.com/ultralytics/docs/releases/download/0/ultralytics-yolov8-transportation-heatmap.avif) | ![Retail Heatmap](https://github.com/ultralytics/docs/releases/download/0/ultralytics-yolov8-retail-heatmap.avif) |

**逐行解读**:
- 此表为**双列对比**,行高由图片驱动,无表头数值列,仅作为「典型应用场景图例」展示。
- 左列展示交通场景下车辆/行人密度在道路上的颜色分布;右列展示零售场景下顾客在货架/通道的密度分布。
- 两者均使用同一 `Heatmap` solution,只是 `region`/视频输入不同,体现同一接口的跨场景复用性。

### 2. `Heatmap()` 参数表(原文,被截断)

| Name | Type | Default | Description |
| --- | --- | --- | --- |
| *(以下内容在提供的原文片段中已被截断,字段未能完整保留)* | | | |

**逐行解读**:
- 原文以 Markdown 表格形式给出 `solutions.Heatmap()` 构造函数的参数定义,但在「`Default`」列与「Description」列交接处被截断,后续行(推测包含 `model`、`colormap`、`show`、`region`、`classes` 等字段的默认值与说明)未在本次原文片段中给出。
- 因此仅能确认:存在一个以 `Name / Type / Default / Description` 四列构成的 API 参数参考表,具体每个参数的实际取值与语义须以官方文档完整版本为准,本文不做臆测。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **同仓相邻文档(由内部链接 `../modes/track.md` 可知)**:本指南与「`modes/track.md`」(跟踪模式)处于同级文档树,均属于 YOLO11 的下游应用能力。Heatmap 与 Tracking 都建立在「目标检测 → 逐帧轨迹/位置累积」这一共同范式之上:Tracking 关注「个体轨迹」,Heatmap 关注「群体密度」,两者共享同一检测器推理结果作为上游输入。
- **能力维度对比**(原文 5 个示例):
  - **Heatmap**(无 `region`):全画面累积。
  - **Line Counting**(两点 `region`):用于跨线统计。
  - **Polygon Counting**(5 点闭合 `region`):用于任意多边形区域内累积与计数。
  - **Region Counting**(4 点非闭合 `region`):用于矩形区域内的累积与计数。
  - **Specific Classes**(`classes=[0,2]`):在上述任一空间约束下进一步按类别筛选,只对所选类别的目标位置进行累积。
- 5 种用法共享同一 `Heatmap.generate_heatmap(im0)` 处理管线,差别仅在构造参数,这构成文档的「接口一致性」主线。

---

## 【使用方法】

### 启用方式(原文给出)

```python
from ultralytics import solutions
heatmap = solutions.Heatmap(show=True, model="yolo11n.pt", colormap=cv2.COLORMAP_PARULA)
im0 = heatmap.generate_heatmap(im0)
```

### 可配置项(原文代码中实际出现过)

| 配置项 | 取值(原文示例) | 作用 |
| --- | --- | --- |
| `show` | `True` | 是否实时弹窗显示 |
| `model` | `"yolo11n.pt"` | 检测器权重 |
| `colormap` | `cv2.COLORMAP_PARULA` | 累积强度→颜色映射 |
| `region` | 两点 / 4 点 / 5 点坐标列表 | 限定计数区域(线/矩形/多边形) |
| `classes` | `[0, 2]` | 仅对指定检测类别进行热图累积 |

### 命令(原文未涉及)

原文未提供 CLI 命令(如 `yolo solutions heatmap ...`),仅给出 Python API 调用方式。

---

> **完整性说明**:原文片段在 `### Arguments Heatmap()` 表格的表头之后即被截断,因此参数表中各字段的 `Default` 与 `Description` 具体内容未在本次解读中给出,以上参数表解读严格遵循「原文有则写、原文无则不臆造」的原则。
