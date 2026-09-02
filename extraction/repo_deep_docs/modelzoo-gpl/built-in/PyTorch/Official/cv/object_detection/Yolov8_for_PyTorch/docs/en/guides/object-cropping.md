# Object Cropping using Ultralytics YOLO11

> 仓 `modelzoo-gpl` · 路径 `built-in/PyTorch/Official/cv/object_detection/Yolov8_for_PyTorch/docs/en/guides/object-cropping.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-gpl/built-in/PyTorch/Official/cv/object_detection/Yolov8_for_PyTorch/docs/en/guides/object-cropping.md

# 深度解读:Object Cropping using Ultralytics YOLO11

## 【定位】

本文档描述 Ultralytics YOLO11 的"目标裁剪(Object Cropping)"能力,即利用 YOLO11 检测模型从图像或视频中精准定位并提取出特定目标区域,以用于聚焦分析、数据缩减与下游处理。

---

## 【技术要点】

1. **核心思路**:基于 YOLO11 目标检测得到的边界框(bounding box),从原图 `im0` 中按坐标切片裁剪出每个目标区域并单独保存。
2. **模型加载**:示例中加载 `yolo11n.pt`(YOLO11 nano 模型权重文件)。
3. **检测接口**:调用 `model.predict(im0, show=False)` 对每一帧进行推理,从 `results[0].boxes` 中读取 `xyxy`(像素坐标格式)与 `cls`(类别索引)。
4. **裁剪坐标映射**:对每个 box 用 NumPy 切片语法 `im0[int(box[1]):int(box[3]), int(box[0]):int(box[2])]` 得到目标区域 `crop_obj`,其中 `box[0..3]` 对应 `x1, y1, x2, y2`。
5. **可视化与持久化**:使用 `Annotator` 在 `im0` 上绘制带颜色与类别名的边框;裁剪结果以 `str(idx) + ".png"` 命名顺序写入 `ultralytics_crop/` 目录;同时用 `cv2.VideoWriter` 输出 `object_cropping_output.avi`(编码器 `mp4v`,分辨率与原视频一致,帧率沿用 `cv2.CAP_PROP_FPS`)。
6. **视频流参数**:从 `cv2.VideoCapture` 读取视频宽 `w`、高 `h`、帧率 `fps` 三个属性;通过 `cv2.waitKey(1) & 0xFF == ord("q")` 实现交互式退出。

---

## 【关键机制与数据】

- **工作原理(原文)**:"The YOLO11 model capabilities are utilized to accurately identify and delineate objects, enabling precise cropping for further analysis or manipulation."(YOLO11 用于精确识别并勾画目标轮廓,从而实现精准裁剪)
- **三大优势(原文)**:
  - Focused Analysis:对场景中单个目标进行深入检查或处理;
  - Reduced Data Volume:仅提取相关目标以减小数据体量,便于存储、传输与后续计算;
  - Enhanced Precision:YOLO11 的检测精度保证裁剪后目标的空间关系得以保持,视觉信息完整性不受破坏。
- **数据流(原文代码所体现)**:视频帧 → `model.predict` → `results[0].boxes.xyxy.cpu().tolist()` 与 `cls` → 逐框 `im0` 切片 → `cv2.imwrite` 落盘 PNG → `cv2.VideoWriter` 写出带标注的视频帧 → `cv2.imshow` 显示。模型输出从 GPU 经 `.cpu().tolist()` 转回 CPU 列表。
- **FAQ 中提及的硬件信息(原文)**:YOLO11 同时适配 CPU 与 GPU;实时或高吞吐推理推荐独立 GPU(如 NVIDIA Tesla、RTX 系列);iOS 部署可选 CoreML,Android 部署可选 TFLite。
- **原文未提供**任何具体性能数字(如 FPS、mAP、延迟、吞吐),文档不涉及可量化的 benchmark 数据。

---

## 【表格解读】

原文包含一张 Visuals 图片说明表格,逐字还原如下:

|                                                                                Airport Luggage                                                                                 |
| :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------: |
| ![Conveyor Belt at Airport Suitcases Cropping using Ultralytics YOLO11](https://github.com/ultralytics/docs/releases/download/0/suitcases-cropping-airport-conveyor-belt.avif) |
|                                                      Suitcases Cropping at airport conveyor belt using Ultralytics YOLO11                                                      |

**逐行解读**:
- 标题行 `Airport Luggage`:给出该可视示例的主题场景——机场行李。
- 图片行:指向一张 `.avif` 格式图片,内容为"机场传送带行李箱被 YOLO11 裁剪"的示例图,用于直观展示目标裁剪效果。
- 描述行:`Suitcases Cropping at airport conveyor belt using Ultralytics YOLO11`,即"使用 YOLO11 对机场传送带上的行李箱进行裁剪"。
- 该表格仅作为可视化说明,不属于参数表、性能对比表或配置项表。

此外,代码块上方通过 `{% include "macros/predict-args.md" %}` 引用了 `model.predict` 参数文档宏(原文以 include 宏形式引入,实际参数表内容未在本 md 中展开)。

---

## 【公式解读】

原文无公式。

(代码中出现的 NumPy 切片表达式 `im0[int(box[1]):int(box[3]), int(box[0]):int(box[2])]` 是编程语法而非数学公式,不属于本节范畴。)

---

## 【关联】

文档通过 FAQ 与正文链接,与以下上游/下游模块建立关联:

1. **[Model Export 指南](../modes/export.md)**:FAQ 指出 YOLO11 可无缝集成 OpenVINO、TensorRT 等导出/部署工具,以满足实时与硬件优化需求——属于裁剪工作流的**下游部署**环节。
2. **[Quickstart](../quickstart.md)**:FAQ 指引用户通过 Quickstart 学习 YOLO11 训练与推理全流程,以此实现"训练→检测→裁剪"的完整链路——属于**上游入门**文档。
3. **[Predict Modes](../modes/predict.md)**:FAQ 提到 tracking 与 prediction 模式可用于实时视频处理与裁剪——属于**核心能力来源**(本示例代码即基于 `model.predict`)。
4. **[Model Deployment Options](../guides/model-deployment-options.md)**:FAQ 在硬件相关问题中引导至该文档,介绍 CoreML(iOS)、TFLite(Android) 等轻量设备部署方案——属于裁剪能力的**跨平台下游扩展**。

文档自身还嵌入对 ultralytics 主仓库(`https://github.com/ultralytics/ultralytics/`)以及 glossary 中 "object-detection"、"accuracy"、"precision" 条目的外链引用,构成与术语体系的关联。

---

## 【使用方法】

以下内容均直接源自原文代码示例与 FAQ:

- **启用方式(原文代码路径)**:
  1. 安装并导入:`from ultralytics import YOLO`;配合 `cv2`、`os`、`ultralytics.utils.plotting.Annotator` 与 `colors`。
  2. 加载模型:`model = YOLO("yolo11n.pt")`;取类别名 `names = model.names`。
  3. 打开视频:`cap = cv2.VideoCapture("path/to/video/file.mp4")`,并以 `assert cap.isOpened()` 校验。
  4. 创建裁剪输出目录:`ultralytics_crop`(若不存在则 `os.mkdir`)。
  5. 实例化 `cv2.VideoWriter("object_cropping_output.avi", cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))`。
- **关键配置项(原文所列)**:
  - `model.predict(im0, show=False)` 中的参数集由外部宏 `predict-args.md` 引入(原文未在本 md 中逐项展开)。
  - `Annotator(im0, line_width=2, example=names)`,边框线宽 `2`。
  - `colors(int(cls), True)` 按类别索引生成边框颜色。
- **交互退出命令**:按 `q` 键(`cv2.waitKey(1) & 0xFF == ord("q")`)中断循环。
- **释放资源(原文)**:`cap.release()`、`video_writer.release()`、`cv2.destroyAllWindows()`。
- **针对图像的批处理 / 命令行 CLI 用法**:原文未涉及(示例仅展示 Python API 视频处理)。
