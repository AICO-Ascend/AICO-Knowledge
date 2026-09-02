# Workouts Monitoring using Ultralytics YOLO11

> 仓 `modelzoo-gpl` · 路径 `built-in/PyTorch/Official/cv/object_detection/Yolov8_for_PyTorch/docs/en/guides/workouts-monitoring.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-gpl/built-in/PyTorch/Official/cv/object_detection/Yolov8_for_PyTorch/docs/en/guides/workouts-monitoring.md

# 一体化深度解读：Workouts Monitoring using Ultralytics YOLO11

---

## 【定位】

本文档描述了如何利用 **Ultralytics YOLO11** 的姿态估计（Pose Estimation）能力，对俯卧撑、引体向上、仰卧起坐等健身动作进行实时关键点追踪、动作计数与姿态评估，从而为用户和教练提供关于动作形式与训练指标的即时反馈。

---

## 【技术要点】

1. **核心类：`solutions.AIGym`** —— 文档中所有功能均封装在 `ultralytics.solutions.AIGym` 类中，通过其 `monitor(im0)` 方法逐帧处理视频。
2. **关键点索引 `kpts=[6, 8, 10]`** —— 原文中两个示例代码均使用此关键点三元组，对应 KeyPoints Map 中的肩膀、手肘、手腕，用于构成"上/下"姿态判定所需的角度。
3. **模型权重：`yolo11n-pose.pt`** —— 第一个示例显式传入轻量级姿态模型；第二个示例未传 `model` 参数（依赖类内部默认值）。
4. **角度阈值参数**：`up_angle` 默认 `145.0`、`down_angle` 默认 `90.0`，分别用于判定动作到达"上"位与"下"位的角度阈值。
5. **绘制线宽 `line_width=2`**、实时显示开关 `show=True`，二者共同控制可视化输出。
6. **视频 I/O 流程**：使用 `cv2.VideoCapture` 读帧 → `cv2.CAP_PROP_FRAME_WIDTH/HEIGHT/FPS` 取分辨率与帧率 → 可选用 `cv2.VideoWriter`（编码 `"mp4v"`）保存输出。

---

## 【关键机制与数据】

- **工作原理**（原文）：基于 YOLO11 的姿态估计，实时追踪身体关键点和关节（"accurately tracking key body landmarks and joints in real-time"），通过对 `kpts` 所指定的关键点构成的关节角度与 `up_angle`、`down_angle` 阈值比较，判定一次完整动作的"上—下—上"循环，进而实现重复次数计数与形式反馈。
- **数据流**（原文）：
  1. `cv2.VideoCapture("path/to/video/file.mp4")` 打开视频并断言 `cap.isOpened()`；
  2. 一次性读取 `(w, h, fps)` 三个视频属性；
  3. 在 `while cap.isOpened()` 循环中逐帧调用 `gym.monitor(im0)`；
  4. 若需保存，再通过 `cv2.VideoWriter` 以原始 `(w, h)` 和 `fps` 写出 `workouts.avi`。
- **支持的动作类型**（原文 FAQ 段）：`AIGym` 类支持 `"pushup"`、`"pullup"`、`"abworkout"` 三种预设姿态类型。
- **性能数据**：原文未提供具体的 mAP、FPS、延迟等量化指标，仅在 FAQ 中以定性语言称 "highly accurate" 和 "state-of-the-art pose estimation capabilities"，未给出可验证的数字。

---

## 【表格解读】

### 表格 1：Real World Applications（应用展示）

| Workouts Monitoring | Workouts Monitoring |
| :---: | :---: |
| PushUps Counting | PullUps Counting |

**逐行解读**：
- 该表为左右两列的应用场景对照展示。
- 左列：图片 `pushups-counting.avif`，标题 "PushUps Counting"——展示 `AIGym` 对俯卧撑动作的计数效果。
- 右列：图片 `pullups-counting.avif`，标题 "PullUps Counting"——展示对引体向上的计数效果。
- 两幅图作为"真实应用"的视觉佐证，文档未在表格中给出量化指标。

### 表格 2：Arguments `AIGym`（参数表，逐字还原）

| Name         | Type    | Default | Description                                                                            |
| ------------ | ------- | ------- | -------------------------------------------------------------------------------------- |
| `kpts`       | `list`  | `None`  | List of three keypoints index, for counting specific workout, followed by keypoint Map |
| `line_width` | `int`   | `2`     | Thickness of the lines drawn.                                                          |
| `show`       | `bool`  | `False` | Flag to display the image.                                                             |
| `up_angle`   | `float` | `145.0` | Angle threshold for the 'up' pose.                                                     |
| `down_angle` | `float` | `90.0`  | Angle threshold for the 'down' pose.                                                   |
| `model`      | `str`   | `None`  | Path to Ultralytics YOLO Pose Model File                                               |

**逐行解读**：
- `kpts`：list 类型，默认 `None`。必须传入**三个**关键点索引（结合 KeyPoints Map 使用），用于定位某个特定动作涉及的关节点，从而计算关节角度以驱动计数逻辑。
- `line_width`：int 类型，默认 `2`。控制 `AIGym` 在画面上绘制骨架连线、角度标注等元素的线宽。
- `show`：bool 类型，默认 `False`。是否在处理过程中实时弹出显示图像。
- `up_angle`：float 类型，默认 `145.0`（度）。判定动作达到"上"位姿态的角度阈值；当由 `kpts` 计算出的角度大于等于该值时，认为处于"上"位。
- `down_angle`：float 类型，默认 `90.0`（度）。判定动作达到"下"位姿态的角度阈值；与 `up_angle` 共同形成一次完整动作循环的角度区间。
- `model`：str 类型，默认 `None`。指向 Ultralytics YOLO Pose 模型的权重文件路径；若不显式传入，依赖类内部默认加载逻辑（原文未指明具体默认值）。

> 注：文档另以 Jinja 宏 `{% include "macros/predict-args.md" %}` 和 `{% include "macros/track-args.md" %}` 引入 `model.predict` 与 `model.track` 的参数表，**宏内容未在原文档内展开**，因此无法逐字还原。

---

## 【公式解读】

原文无公式（无 LaTeX、无伪代码形式的数学表达式）。

文档中可被视为"伪阈值规则"的描述仅以自然语言出现在参数表与 FAQ 中：
- "Angle threshold for the 'up' pose" → `up_angle = 145.0`
- "Angle threshold for the 'down' pose" → `down_angle = 90.0`

但原文并未给出形如 `if angle ≥ up_angle: state = 'up'` 之类的显式公式，因此按要求标注为**原文无公式**。

---

## 【关联】

- **上游模型**：依赖 Ultralytics **YOLO11** 系列中的姿态估计模型（示例中显式使用 `yolo11n-pose.pt`），属于 Ultralytics YOLO 生态。
- **关键点参考**：文档链接到 KeyPoints Map 图 `keypoints-order-ultralytics-yolov8-pose.avif`，与 `AIGym` 的 `kpts` 参数强耦合——必须依此图选取索引（例如 `[6, 8, 10]` 对应肩膀—手肘—手腕）。
- **可调用方法**：与同包内的其他 `solutions`（如 `solutions.AIGym` 自身的 `monitor(im0)`）并列于 `ultralytics.solutions` 命名空间。
- **外链资源**：YouTube 演示视频 `https://www.youtube.com/embed/LGGxqLZtvuw`，展示 Pushups / Pullups / Ab Workouts 效果；以及 Ultralytics 词条页 `precision` 用于 FAQ 中的术语解释。
- **文档用户提供的关联信息**：原文无内部链接（用户提供："(无)"）。

---

## 【使用方法】

以下为原文明确给出的启用与配置方式：

### 1. 最小可运行示例（实时显示，不保存）

```python
import cv2

from ultralytics import solutions

cap = cv2.VideoCapture("path/to/video/file.mp4")
assert cap.isOpened(), "Error reading video file"
w, h, fps = (int(cap.get(x)) for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))

gym = solutions.AIGym(
    model="yolo11n-pose.pt",
    show=True,
    kpts=[6, 8, 10],
)

while cap.isOpened():
    success, im0 = cap.read()
    if not success:
        print("Video frame is empty or video processing has been successfully completed.")
        break
    im0 = gym.monitor(im0)

cv2.destroyAllWindows()
```

### 2. 保存输出到 `workouts.avi` 的示例

```python
import cv2

from ultralytics import solutions

cap = cv2.VideoCapture("path/to/video/file.mp4")
assert cap.isOpened(), "Error reading video file"
w, h, fps = (int(cap.get(x)) for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))

video_writer = cv2.VideoWriter("workouts.avi", cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))

gym = solutions.AIGym(
    show=True,
    kpts=[6, 8, 10],
)

while cap.isOpened():
    success, im0 = cap.read()
    if not success:
        print("Video frame is empty or video processing has been successfully completed.")
        break
    im0 = gym.monitor(im0)
    video_writer.write(im0)

cv2.destroyAllWindows()
video_writer.release()
```

### 3. FAQ 中给出的另一精简示例

```python
from ultralytics import solutions

gym = solutions.AIGym(
    line_width=2,
    show=True,
    kpts=[6, 8, 10],
)
```

### 4. 配置项（`AIGym` 类参数）

- `kpts`：list，三关键点索引。
- `line_width`：int，默认 `2`，绘制线宽。
- `show`：bool，默认 `False`，是否实时显示。
- `up_angle`：float，默认 `145.0`，"上"位角度阈值。
- `down_angle`：float，默认 `90.0`，"下"位角度阈值。
- `model`：str，默认 `None`，YOLO Pose 模型权重路径。

### 5. 命令行 / CLI

原文未涉及命令行调用方式（如 `yolo solutions ...` 之类），仅提供 Python API 用法。
