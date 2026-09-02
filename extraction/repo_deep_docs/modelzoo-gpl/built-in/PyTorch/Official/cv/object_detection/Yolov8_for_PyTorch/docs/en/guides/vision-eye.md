# VisionEye View Object Mapping using Ultralytics YOLO11 🚀

> 仓 `modelzoo-gpl` · 路径 `built-in/PyTorch/Official/cv/object_detection/Yolov8_for_PyTorch/docs/en/guides/vision-eye.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-gpl/built-in/PyTorch/Official/cv/object_detection/Yolov8_for_PyTorch/docs/en/guides/vision-eye.md

# VisionEye View Object Mapping using Ultralytics YOLO11 —— 一体化深度解读

---

## 【定位】

这篇文档介绍 **Ultralytics YOLO11 中的 VisionEye（视觉之眼）对象映射能力** —— 一种让计算机模拟人眼观察精度来识别、定位、跟踪并测量画面中目标对象位置与距离的功能,并给出三种典型应用(基础定位、目标跟踪、距离估算)的 Python 示例代码。

---

## 【技术要点】

1. **核心能力定义**:VisionEye 使计算机能够像人眼一样从某一观察视角识别并聚焦于特定目标对象(原文:"simulating the observational precision of the human eye")。
2. **三种典型用例**:
   - 基础对象映射(`model.predict(im0)` + `annotator.visioneye(box, center_point)`)
   - 对象映射 + 目标跟踪(`model.track(im0, persist=True)` 配合 `track_ids`)
   - 对象映射 + 距离计算(在跟踪基础上叠加像素→米的换算与文本标注)
3. **关键 API**:`ultralytics.utils.plotting.Annotator` 中的 `visioneye(box, center_point)` 方法,从 `center_point`(参考视点)向目标边界框绘制"视线/钉点"视觉标记。
4. **关键参数**:
   - `center_point`:前两个示例为 `(-10, h)`(画面外左下角附近),距离示例为 `(0, h)`(画面左下角);
   - `pixel_per_meter = 10`(原文给定值,用于像素到米的换算系数);
   - `line_width=2`(Annotator 画线宽度);
   - `MJPG` 四字符编码输出视频(`cv2.VideoWriter_fourcc(*"MJPG")`);
   - 文本颜色 `txt_color=(0,0,0)`、背景 `txt_background=(255,255,255)`、bbox 颜色 `bbox_clr=(255,0,255)`;
   - 字体 `cv2.FONT_HERSHEY_SIMPLEX`,字号 `1.2`,线宽 `3`。
5. **`visioneye` 函数可配置参数(原文表格给出)**: `color=(235,219,11)`(线与目标中心颜色)、`pin_color=(255,0,255)`(钉点颜色),均为 `tuple` 类型。
6. **交互退出机制**:`cv2.waitKey(1) & 0xFF == ord("q")` 按 'q' 退出循环。

---

## 【关键机制与数据】

**工作原理(原文:"What is VisionEye Object Mapping?"):**
- 检测 → 从检测/跟踪结果中拿到每帧的目标 `boxes`(xyxy 格式)与 `clss` / `track_id` → 通过 `Annotator` 先画标准 bbox + 类别/ID 标签 → 再调用 `annotator.visioneye(box, center_point)` 绘制从参考点 `center_point` 到目标框的几何连线(模拟人眼视线)。
- 三种示例的数据流差异:
  1. **基础版**:`model.predict(im0)` → `boxes` + `clss` → 以类别名作为标签。
  2. **跟踪版**:`model.track(im0, persist=True)` → 多了 `track_ids = results[0].boxes.id.int().cpu().tolist()`,并对 `track_id` 取模查 `colors` 得到标签颜色。
  3. **距离版**:在跟踪版基础上,先取边界框中心 `(x1,y1) = ((box[0]+box[2])//2, (box[1]+box[3])//2)`,然后与 `center_point` 做欧氏距离,再除以 `pixel_per_meter` 得到米,并用 `cv2.putText` 在目标中心上方叠加 `Distance: xx.xx m` 文本与白色背景矩形。

**性能/基准数据**:原文未给出 FPS、精度、显存、模型大小等任何具体数字。

**输入/输出参数**(原文给出):
- 输入视频:`path/to/video/file.mp4` / `Path/to/video/file.mp4`
- 输出视频:
  - 基础与跟踪版:`visioneye-pinpoint.avi`
  - 距离版:`visioneye-distance-calculation.avi`

**异常处理**:`cap.read()` 返回 `ret=False` 时打印 `"Video frame is empty or video processing has been successfully completed."` 并 `break`。

---

## 【表格解读】

### 表格 1:三种示例样图对照(原文逐字还原)

| VisionEye View | VisionEye View With Object Tracking | VisionEye View With Distance Calculation |
| :---: | :---: | :---: |
| ![VisionEye View Object Mapping using Ultralytics YOLO11](https://github.com/ultralytics/docs/releases/download/0/visioneye-view-object-mapping-yolov8.avif) | ![VisionEye View Object Mapping with Object Tracking using Ultralytics YOLO11](https://github.com/ultralytics/docs/releases/download/0/visioneye-object-mapping-with-tracking.avif) | ![VisionEye View with Distance Calculation using Ultralytics YOLO11](https://github.com/ultralytics/docs/releases/download/0/visioneye-distance-calculation-yolov8.avif) |
| VisionEye View Object Mapping using Ultralytics YOLO11 | VisionEye View Object Mapping with Object Tracking using Ultralytics YOLO11 | VisionEye View with Distance Calculation using Ultralytics YOLO11 |

**逐行解读**:该表用三列并排展示 VisionEye 的能力演进 —— 左列是**纯对象映射**(检测 + 视线连线)、中列是**映射 + 跟踪**(每个目标带有持久化 ID)、右列是**映射 + 距离计算**(在跟踪基础上叠加米制距离标签),三张图像资源均托管在 `github.com/ultralytics/docs/releases/download/0/` 下,对应 README 中三种 Python 示例代码(`model.predict` → `model.track(persist=True)` → `model.track(persist=True)` + 距离公式)。

### 表格 2:`visioneye` 函数参数(原文逐字还原)

| Name        | Type    | Default          | Description                    |
| ----------- | ------- | ---------------- | ------------------------------ |
| `color`     | `tuple` | `(235, 219, 11)` | Line and object centroid color |
| `pin_color` | `tuple` | `(255, 0, 255)`  | VisionEye pinpoint color       |

**逐行解读**:
- `color`:类型 `tuple`,默认值 `(235, 219, 11)`(亮黄色,RGB),用于绘制从 `center_point` 到目标的**连线**以及**目标中心点**的颜色。
- `pin_color`:类型 `tuple`,默认值 `(255, 0, 255)`(品红/洋红,RGB),用于绘制 VisionEye **钉点**(pinpoint)标记的颜色,与距离示例中 `bbox_clr` 的取值一致。

---

## 【公式解读】

原文(距离计算示例)给出的距离公式逐字保留:

```python
distance = (math.sqrt((x1 - center_point[0]) ** 2 + (y1 - center_point[1]) ** 2)) / pixel_per_meter
```

也可写成 LaTeX:

$$d = \frac{\sqrt{(x_1 - c_x)^2 + (y_1 - c_y)^2}}{\text{pixel\_per\_meter}}$$

**符号说明**:
- $x_1,\ y_1$:**目标边界框的质心坐标**,由 `int((box[0] + box[2]) // 2)` 与 `int((box[1] + box[3]) // 2)` 计算得到(即 xyxy 边界框上下/左右边界的整数平均),原文注释为 `"# Bounding box centroid"`。
- $c_x,\ c_y$:**参考视点坐标**,即 `center_point[0]` 与 `center_point[1]`;距离示例中设为 `(0, h)`(画面左下角)。
- $\sqrt{(\cdot)^2 + (\cdot)^2}$:**欧氏距离**(Euclidean distance),计算质心到参考视点的像素距离。
- `pixel_per_meter`:**像素到米的换算系数**,原文硬编码为 `10`(每 10 像素代表 1 米)。
- 最终输出 `distance`:**以米为单位的近似距离**,以 `f"Distance: {distance:.2f} m"` 格式(保留 2 位小数)叠加在画面上。

---

## 【关联】

**与文中提到的其他特性的关系**:
- **Ultralytics YOLO11 检测流水线**:VisionEye 建立在 `YOLO("yolo11n.pt")` 的标准 `predict` / `track` 调用之上,直接复用 `results[0].boxes.xyxy / cls / id` 的张量输出。
- **Annotator 绘图工具**:与 `ultralytics.utils.plotting` 中的 `Annotator` 及其方法 `box_label`、`visioneye` 紧密耦合;`colors(...)` 用于按类别/ID 生成不同颜色。
- **OpenCV 视频管线**:依赖 `cv2.VideoCapture` 读取、`cv2.VideoWriter`(MJPG 编码)写出、`cv2.imshow` 显示以及 `cv2.putText` / `cv2.rectangle` 自定义文本叠加。
- **目标跟踪**:`model.track(im0, persist=True)` 中的 `persist=True` 表示跨帧维持 ID,使 `visioneye` 配合距离示例可在视频序列中持续跟踪同一对象。
- **支持/反馈渠道**:文末指向 Ultralytics Issue Section 作为问题反馈入口(原文链接:`https://github.com/ultralytics/ultralytics/issues/new/choose`)。

**内部链接**:原文未提供任何内部跳转链接(已注明 "无")。

---

## 【使用方法】

**启用方式**(原文有):
1. 安装 Ultralytics 包(原文 FAQ 开头提示通过 pip 安装,具体命令未在本文档正文中完整给出,仅提到"install the Ultralytics YOLO package via pip")。
2. 下载权重文件:`YOLO("yolo11n.pt")`(YOLO11 nano 模型)。
3. 准备输入视频,修改代码中的 `cv2.VideoCapture("path/to/video/file.mp4")` 为实际路径。
4. 直接运行本文档"Samples"部分提供的三段 Python 示例之一,按 'q' 退出。

**关键配置项**:
- `model`:模型权重路径(如 `"yolo11n.pt"`)。
- `center_point`:视点参考位置,基础/跟踪版 `(-10, h)`,距离版 `(0, h)`。
- `pixel_per_meter = 10`:像素→米的换算系数。
- `line_width=2`:Annotator 画线宽度。
- `visioneye(box, center_point)` 的可选 `color`/`pin_color`(见上文表格 2)。
- 视频输出:`cv2.VideoWriter_fourcc(*"MJPG")`、文件名分别为 `visioneye-pinpoint.avi` / `visioneye-distance-calculation.avi`。
- 文本样式:`cv2.FONT_HERSHEY_SIMPLEX`、字号 `1.2`、线宽 `3`,距离文本背景 `txt_background=(255,255,255)` 填充矩形、文字色 `txt_color=(0,0,0)`。

**命令行**:原文未提供 CLI 命令(全部为 Python API 形式)。
