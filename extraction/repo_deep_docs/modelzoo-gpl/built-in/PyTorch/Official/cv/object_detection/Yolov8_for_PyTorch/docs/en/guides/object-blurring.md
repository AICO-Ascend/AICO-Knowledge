# Object Blurring using Ultralytics YOLO11 🚀

> 仓 `modelzoo-gpl` · 路径 `built-in/PyTorch/Official/cv/object_detection/Yolov8_for_PyTorch/docs/en/guides/object-blurring.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-gpl/built-in/PyTorch/Official/cv/object_detection/Yolov8_for_PyTorch/docs/en/guides/object-blurring.md

# 【定位】

这篇文档描述并示例化利用 **Ultralytics YOLO11** 在图像或视频中检测目标、对目标区域应用 OpenCV 模糊效果，从而实现隐私保护与选择性视觉隐藏的完整流程；但给定路径及部分外部链接仍带有 `Yolov8_for_PyTorch`/`yolov8` 字样，而正文、配置和示例实际均以 `YOLO11` 和 `yolo11n.pt` 为准。

# 【技术要点】

1. **目标检测与区域处理**
   - 加载模型：
     ```python
     model = YOLO("yolo11n.pt")
     ```
   - 视频逐帧推理：
     ```python
     results = model.predict(im0, show=False)
     ```
   - 从第一帧结果中提取边界框和类别：
     ```python
     boxes = results[0].boxes.xyxy.cpu().tolist()
     clss = results[0].boxes.cls.cpu().tolist()
     ```

2. **边界框切片**
   - 每个检测框依次作为图像 ROI：
     ```python
     obj = im0[int(box[1]):int(box[3]), int(box[0]):int(box[2])]
     ```
   - 按代码索引关系，`box[0]`、`box[1]`、`box[2]`、`box[3]`分别参与左、右、上、下边界切片；模糊后的 ROI 再写回原图相同位置：
     ```python
     im0[int(box[1]):int(box[3]), int(box[0]):int(box[2])] = blur_obj
     ```

3. **模糊参数与类别显示**
   - 模糊比例固定为：
     ```python
     blur_ratio = 50
     ```
   - 实际内核尺寸为 `(blur_ratio, blur_ratio)`，等价于示例中的 `(50, 50)`：
     ```python
     blur_obj = cv2.blur(obj, (blur_ratio, blur_ratio))
     ```
   - 类别用于生成标签文本和颜色，但主示例没有按类别筛选目标：
     ```python
     annotator.box_label(
         box,
         color=colors(int(cls), True),
         label=names[int(cls)]
     )
     ```
   - 因此，按示例的字面行为，检测到的所有目标类别都会进入模糊流程；“只处理特定类别”需要通过其他检测模型或额外的类别筛选实现。

4. **视频输入与输出**
   - 输入文件：
     ```python
     cap = cv2.VideoCapture("path/to/video/file.mp4")
     ```
   - 从输入视频读取宽度、高度和 FPS：
     ```python
     w, h, fps = (
         int(cap.get(x)) for x in (
             cv2.CAP_PROP_FRAME_WIDTH,
             cv2.CAP_PROP_FRAME_HEIGHT,
             cv2.CAP_PROP_FPS
         )
     )
     ```
   - 输出配置：
     ```python
     video_writer = cv2.VideoWriter(
         "object_blurring_output.avi",
         cv2.VideoWriter_fourcc(*"mp4v"),
         fps,
         (w, h)
     )
     ```

5. **交互与资源释放**
   - 当前帧同时显示并写入输出文件：
     ```python
     cv2.imshow("ultralytics", im0)
     video_writer.write(im0)
     ```
   - 按下 `q` 退出：
     ```python
     if cv2.waitKey(1) & 0xFF == ord("q"):
         break
     ```
   - 最后释放视频读取器和写入器并关闭窗口：
     ```python
     cap.release()
     video_writer.release()
     cv2.destroyAllWindows()
     ```

6. **文档宣称的能力边界**
   - 文档将应用价值概括为隐私保护、选择性聚焦和实时处理，但没有给出可核验的速度、延迟、吞吐量、准确率或隐私保护强度数据。
   - `Arguments model.predict` 部分只是对模板文件 `macros/predict-args.md` 的包含指令，原文没有展开具体参数表。

# 【关键机制与数据】

- **原文：**整体数据流是“加载 `yolo11n.pt` → 打开 MP4 → 读取 `w/h/fps` → 逐帧调用 `model.predict(..., show=False)` → 取得 `xyxy` 边界框和类别 → 截取每个目标 ROI → 用 `(50, 50)` 内核进行 `cv2.blur` → 将模糊 ROI 写回 → 显示并写入 AVI”。

- **原文：**处理对象来自 `results[0]`，即第一帧或当前批处理结果；边界框与类别分别由：
  ```python
  results[0].boxes.xyxy
  results[0].boxes.cls
  ```
  获得，再转换成 CPU 上的列表供 Python 循环使用。

- **原文：**类别名由 `model.names` 提供，类别索引通过 `int(cls)` 转换为标签文本；同一类别索引还传给：
  ```python
  colors(int(cls), True)
  ```
  用于为检测框和标签选择颜色。

- **原文：**文档称 YOLO11 的效率支持“real-time processing”，并称其架构针对快速推理进行了优化，因而适合动态环境中的即时隐私处理。

- **原文：**FAQ 仅以定性方式称 YOLO11 通常在速度方面优于 Faster R-CNN；没有提供两者的实测 FPS、延迟、加速比、精度或资源占用数据。

- **原文：**代码从视频读取 `fps`，并把该值传给 `cv2.VideoWriter`；这只是输出编码器使用的帧率配置，文档没有将其表示为实际处理性能。

- **原文：**虽然正文强调“选择性模糊”，主示例却没有使用类别条件，只遍历全部 `boxes`；FAQ 进一步说明，面部模糊需要使用能够识别面部目标的预训练模型或自行训练的模型，再复用 OpenCV 模糊流程。

# 【表格解读】

原文无表格。

`{% include "macros/predict-args.md" %}` 是模板包含指令，且原文没有给出该宏展开后的参数表，因此不存在可逐字还原的表格内容。

# 【公式解读】

原文无公式。

文档中的 `(50, 50)` 是 OpenCV 模糊内核尺寸，坐标切片是 NumPy/OpenCV ROI 操作，不属于数学公式。

# 【关联】

- **上游模型能力：**核心依赖是 Ultralytics YOLO11 的目标检测。文档链接到 Ultralytics 项目仓库和 YOLO11 文档，并引用了目标检测术语说明。
- **下游图像处理：**YOLO11 只负责产生目标位置和类别；区域裁剪、模糊、显示、视频编码和文件写入均由 OpenCV 完成。
- **Ultralytics 可视化辅助：**`Annotator` 来自 `ultralytics.utils.plotting`，`colors` 同样由 Ultralytics 提供，用于显示检测框、标签及类别颜色。
- **选择性能力来源：**文档将“Selective Focus”作为优势，并说明可通过专门的人脸检测模型进行人脸模糊；但当前代码没有类别过滤，因此它展示的是“模糊全部检测目标”的流程。
- **FAQ 扩展场景：**文档把人脸隐私保护作为扩展示例，要求检测模型本身能够识别面部；这不是当前 `yolo11n.pt` 示例中已经实现的专门人脸功能。
- **性能关系：**实时处理依赖“目标检测速度 + OpenCV ROI 模糊 + 视频编码/显示”的整条流水线；文档只评价 YOLO11 适合快速推理，没有拆分测量各阶段的性能。
- **链接信息：**给定信息中的文末内部链接为“无”；原文中仍有一个章节锚点 `#advantages-of-object-blurring`，以及指向 Ultralytics 仓库、object detection、OpenCV 和 YOLO11 文档的外部链接。
- **命名关系：**仓库路径和 FAQ 中的部分目标 URL 仍写有 `yolov8`，但文档标题、描述、模型配置、代码和 FAQ 主体均使用 YOLO11，不能仅凭路径将该示例视为 YOLOv8 专用实现。

# 【使用方法】

原文未涉及安装命令，也没有提供专门的启用函数；能力通过 Python 示例直接组合 `ultralytics.YOLO`、Ultralytics 绘图工具和 OpenCV 实现。

关键配置项包括：

| 配置 | 原文值 | 作用 |
|---|---:|---|
| 模型 | `yolo11n.pt` | 执行 YOLO11 目标检测 |
| 输入视频 | `path/to/video/file.mp4` | OpenCV 视频输入占位路径 |
| 模糊比例 | `50` | 生成 `(50, 50)` 的 `cv2.blur` 内核 |
| 输出视频 | `object_blurring_output.avi` | 保存处理后的视频 |
| 编码器 | `mp4v` | `VideoWriter_fourcc(*"mp4v")` |
| 标注线宽 | `2` | 传给 `Annotator(line_width=2, ...)` |
| 预测显示开关 | `show=False` | 推理过程不直接显示结果窗口 |
| 退出键 | `q` | 通过 `ord("q")` 检测退出 |

完整核心流程如下：

```python
import cv2

from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator, colors

model = YOLO("yolo11n.pt")
names = model.names

cap = cv2.VideoCapture("path/to/video/file.mp4")
assert cap.isOpened(), "Error reading video file"
w, h, fps = (
    int(cap.get(x)) for x in (
        cv2.CAP_PROP_FRAME_WIDTH,
        cv2.CAP_PROP_FRAME_HEIGHT,
        cv2.CAP_PROP_FPS
    )
)

# Blur ratio
blur_ratio = 50

# Video writer
video_writer = cv2.VideoWriter(
    "object_blurring_output.avi",
    cv2.VideoWriter_fourcc(*"mp4v"),
    fps,
    (w, h)
)

while cap.isOpened():
    success, im0 = cap.read()
    if not success:
        print(
            "Video frame is empty or video processing has been successfully completed."
        )
        break

    results = model.predict(im0, show=False)
    boxes = results[0].boxes.xyxy.cpu().tolist()
    clss = results[0].boxes.cls.cpu().tolist()
    annotator = Annotator(im0, line_width=2, example=names)

    if boxes is not None:
        for box, cls in zip(boxes, clss):
            annotator.box_label(
                box,
                color=colors(int(cls), True),
                label=names[int(cls)]
            )

            obj = im0[
                int(box[1]):int(box[3]),
                int(box[0]):int(box[2])
            ]
            blur_obj = cv2.blur(obj, (blur_ratio, blur_ratio))

            im0[
                int(box[1]):int(box[3]),
                int(box[0]):int(box[2])
            ] = blur_obj

    cv2.imshow("ultralytics", im0)
    video_writer.write(im0)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
video_writer.release()
cv2.destroyAllWindows()
```

该示例没有提供类别选择参数、置信度阈值、性能调优参数或仅保存视频而不显示的配置。
