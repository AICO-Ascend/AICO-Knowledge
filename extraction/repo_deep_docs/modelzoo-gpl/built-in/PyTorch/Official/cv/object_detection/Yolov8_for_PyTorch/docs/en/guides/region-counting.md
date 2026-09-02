# Object Counting in Different Regions using Ultralytics YOLOv8 🚀

> 仓 `modelzoo-gpl` · 路径 `built-in/PyTorch/Official/cv/object_detection/Yolov8_for_PyTorch/docs/en/guides/region-counting.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-gpl/built-in/PyTorch/Official/cv/object_detection/Yolov8_for_PyTorch/docs/en/guides/region-counting.md

# 一体化深度解读:Ultralytics YOLOv8 区域目标计数 Guide

## 【定位】

这篇文档解决的是**如何在指定的矩形/多边形区域 (region) 内对 YOLOv8 检测到的目标进行计数**的问题,描述了 Ultralytics YOLOv8 通过计算机视觉对划定区域内目标进行精确计数的工程能力,并以 `yolov8_region_counter.py` 示例脚本为载体,提供从安装、推理、参数调节到交互式移动区域 (movable region) 的完整使用流程。

---

## 【技术要点】

1. **基于 YOLOv8 检测 + 区域几何判定 + 目标跟踪的计数管线**:利用 YOLOv8 的检测能力识别目标,结合追踪 (tracking) 算法为每个目标生成持续 ID,再通过判断目标点 (如底部中心点) 是否落入用户划定的 region 来决定是否纳入计数。
2. **示例代码路径固定**:脚本位于 `ultralytics/examples/YOLOv8-Region-Counter/yolov8_region_counter.py`,需先 `git clone` 再 `cd` 进入该目录运行。
3. **命令行参数体系完备**:提供 `--source`、`--weights`、`--save-img`、`--device cpu`、`--classes`、`--view-img`、`--line_thickness`、`--region-thickness`、`--track-thickness` 等开关,默认模型权重为 `yolov8n.pt`。
4. **交互式 movable region**:在视频播放过程中,可使用鼠标左键点击并拖拽 (click and drag) 来实时移动 region 框,适应动态场景。
5. **多类支持与可选类别过滤**:通过 `--classes 0 2` 形式 (空格分隔) 仅检测指定类别 (例如第 0 类和第 2 类),默认检测全部类别。
6. **可视化与可保存性**:默认不保存结果 (`--save-img` 默认 `False`),可通过 `--view-img` 在屏幕上实时查看,也可通过 `--save-img` 将带标注的视频/图像落盘。

---

## 【关键机制与数据】

- **工作原理 (原文流程)**:
  1. 克隆 `https://github.com/ultralytics/ultralytics` 仓库;
  2. 进入 `ultralytics/examples/YOLOv8-Region-Counter` 目录;
  3. 运行 `python yolov8_region_counter.py --source "path/to/video.mp4"` 触发推理与计数。
- **数据流 (原文表述隐含)**:输入 (`--source` 视频文件路径,或 webcam 0) → YOLOv8 检测 + 跟踪 → 区域判定 (region 几何包含) → 输出带标注的视频流,可选择落盘。
- **交互机制 (原文)**:"During video playback, you can interactively move the region within the video by clicking and dragging using the left mouse button." —— 即 region 在运行时可被鼠标左键拖动。
- **性能数据**:原文未给出 FPS、mAP、计数精度等量化指标,亦未给出具体硬件基准 (原文:"原文未涉及"对应数值)。

---

## 【表格解读】

### 表格 A — Real World Applications (原文表格,逐字还原)

| Retail | Market Streets |
| :---: | :---: |
| ![People Counting in Different Region using Ultralytics YOLOv8](https://github.com/ultralytics/docs/releases/download/0/people-counting-different-region-ultralytics-yolov8.avif) | ![Crowd Counting in Different Region using Ultralytics YOLOv8](https://github.com/ultralytics/docs/releases/download/0/crowd-counting-different-region-ultralytics-yolov8.avif) |
| People Counting in Different Region using Ultralytics YOLOv8 | Crowd Counting in Different Region using Ultralytics YOLOv8 |

**逐行解读**:
- 第一行是**表头**,以两列分别标注应用场景——**Retail (零售)** 与 **Market Streets (商业街区)**。
- 第二行是**视觉示例行**:左列展示零售门店中"YOLOv8 在不同区域中进行人数统计 (People Counting)"的效果图;右列展示商业街区场景下"在多个区域中进行人群密度统计 (Crowd Counting)"的效果图。两张图均为 Ultralytics 官方文档发布的 `.avif` 演示素材。
- 第三行是**图注行 (Caption)**:左图对应 "People Counting in Different Region using Ultralytics YOLOv8",右图对应 "Crowd Counting in Different Region using Ultralytics YOLOv8",与上一行的图像一一对应。
- 整张表通过对比**室内零售**与**室外街区**两种典型应用,展示同一 region counting 技术在不同场景的可移植性。

### 表格 B — Optional Arguments (原文表格,逐字还原)

| Name                 | Type   | Default      | Description                                                                 |
| -------------------- | ------ | ------------ | --------------------------------------------------------------------------- |
| `--source`           | `str`  | `None`       | Path to video file, for webcam 0                                            |
| `--line_thickness`   | `int`  | `2`          | [Bounding Box](https://www.ultralytics.com/glossary/bounding-box) thickness |
| `--save-img`         | `bool` | `False`      | Save the predicted video/image                                              |
| `--weights`          | `str`  | `yolov8n.pt` | Weights file path                                                           |
| `--classes`          | `list` | `None`       | Detect specific classes i.e. --classes 0 2                                  |
| `--region-thickness` | `int`  | `2`          | Region Box thickness                                                        |
| `--track-thickness`  | `int`  | `2`          | Tracking line thickness                                                     |

**逐行解读**:
- `--source` (str, 默认 `None`):视频文件路径;若使用摄像头则填 `0`,对应原文"Path to video file, for webcam 0"。
- `--line_thickness` (int, 默认 `2`):**检测框 (Bounding Box)** 的线条粗细,文档通过超链接指向 Ultralytics glossary 的 bounding-box 词条,默认为 2 像素。
- `--save-img` (bool, 默认 `False`):是否保存带预测标注的视频/图像;默认关闭,需显式开启才会落盘。
- `--weights` (str, 默认 `yolov8n.pt`):模型权重文件路径,默认使用轻量级 Nano 模型,可通过该参数切换到 `yolov8s/m/l/x.pt` 或自定义权重。
- `--classes` (list, 默认 `None`):仅检测指定的类别索引,例如 `--classes 0 2` 表示只检测第 0 类和第 2 类;默认 `None` 即检测全部类别。
- `--region-thickness` (int, 默认 `2`):用户划定的 **Region Box (区域框)** 的线条粗细,默认 2 像素。
- `--track-thickness` (int, 默认 `2`):**跟踪线 (tracking line)** 的线条粗细,用于在可视化中表现目标移动轨迹的线条宽度,默认 2 像素。

---

## 【公式解读】

原文无公式 (无 LaTeX 或伪代码形式的数学表达式)。

---

## 【关联】

- **与 `../guides/object-counting.md` 的关系**:文档首段直接以链接形式引用"Object counting"基础文档 `[Object counting](../guides/object-counting.md)`,表明**区域计数 (region counting)** 是**通用对象计数**的功能增强版——前者多了"地理围栏 / 区域限制"这一维度。该链接是文档唯一的内部链接,反映出本指南是对象计数模块下的"区域化分支"专题。
- **与 Ultralytics 生态的关联**:文档反复引用 `https://github.com/ultralytics/ultralytics` 主仓库与 `https://www.ultralytics.com/glossary/*` 词条 (precision、accuracy、bounding-box、computer-vision-cv),说明本能力构建在 Ultralytics 主框架之上,术语定义与全局 glossary 保持一致。
- **与示例脚本的关系**:本指南是 `examples/YOLOv8-Region-Counter/yolov8_region_counter.py` 的官方使用说明,文档与脚本是"说明 ↔ 实现"的对应关系。
- **FAQ 内部锚点关联**:FAQ 中通过锚链接回引到 `#steps-to-run`、`#advantages-of-object-counting-in-regions`、`#step-2-run-region-counting-using-ultralytics-yolov8`、`#real-world-applications` 等文档内部章节,形成自包含的导航闭环。

---

## 【使用方法】

### 安装与定位 (原文 Step 1)
```bash
# Clone Ultralytics repo
git clone https://github.com/ultralytics/ultralytics

# Navigate to the local directory
cd ultralytics/examples/YOLOv8-Region-Counter
```

### 推理命令 (原文 Step 2)
```bash
# 保存结果
python yolov8_region_counter.py --source "path/to/video.mp4" --save-img

# 在 CPU 上运行
python yolov8_region_counter.py --source "path/to/video.mp4" --device cpu

# 更换模型权重
python yolov8_region_counter.py --source "path/to/video.mp4" --weights "path/to/model.pt"

# 仅检测指定类别 (例如第 0、2 类)
python yolov8_region_counter.py --source "path/to/video.mp4" --classes 0 2

# 仅查看结果, 不保存
python yolov8_region_counter.py --source "path/to/video.mp4" --view-img
```

### 交互式移动区域 (原文 Tip)
视频播放过程中,可使用鼠标左键 **点击并拖拽** 来移动 region 框。

### 配置项总览 (原文 Optional Arguments 表)
共 7 个开关:`--source`、`--line_thickness`(默认 2)、`--save-img`(默认 False)、`--weights`(默认 `yolov8n.pt`)、`--classes`(默认 None)、`--region-thickness`(默认 2)、`--track-thickness`(默认 2)。详细类型与含义见上方"表格 B"逐行解读。
