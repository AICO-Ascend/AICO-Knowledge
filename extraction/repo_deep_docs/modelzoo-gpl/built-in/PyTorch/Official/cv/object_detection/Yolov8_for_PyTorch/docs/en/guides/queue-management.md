# Queue Management using Ultralytics YOLO11 🚀

> 仓 `modelzoo-gpl` · 路径 `built-in/PyTorch/Official/cv/object_detection/Yolov8_for_PyTorch/docs/en/guides/queue-management.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-gpl/built-in/PyTorch/Official/cv/object_detection/Yolov8_for_PyTorch/docs/en/guides/queue-management.md

# 一体化深度解读:Queue Management using Ultralytics YOLO11

## 【定位】
这篇文档介绍如何利用 Ultralytics YOLO11 对排队场景(人或车辆队列)进行组织与控制,核心目标是**减少等待时间、提升运营效率**,适用于零售、银行、机场、医疗等场景下的队列监测与智能调度。

---

## 【技术要点】

1. **核心解决方案类**:使用 `ultralytics.solutions.QueueManager`,通过 `process_queue(im0)` 对每帧图像执行队列分析。
2. **模型加载**:默认使用 `model="yolo11n.pt"`(YOLO11 系列的 nano 轻量模型),通过 `YOLO(...)` 与 `QueueManager(...)` 两个入口传入。
3. **区域(ROI)定义**:用 `region` 参数定义四边形队列监测区;文档示例为 `[(20, 400), (1080, 404), (1080, 360), (20, 360)]`,默认值为 `[(20, 400), (1260, 400)]`。
4. **可视化与绘制**:通过 `line_width`(默认 `2`)控制边界框/分隔线粗细;`show`(默认 `False`)控制是否实时弹窗显示。
6. **类别过滤**:支持 `classes` 参数(示例 `classes=3`),只对指定类别进行计数与队列管理,避免误检干扰。
7. **视频读写**:采用 OpenCV `cv2.VideoCapture` 读流、`cv2.VideoWriter` 写流,输出文件名为 `queue_management.avi`,编码器 `mp4v`,宽高与 fps 与输入一致。
8. **退出与循环控制**:主循环内通过 `cv2.waitKey(1) & 0xFF == ord("q")` 触发退出,帧空时打印 `Video frame is empty or video processing has been successfully completed.`。

---

## 【关键机制与数据】

**工作原理(原文):**
- 文档将 YOLO11 的**目标检测能力**与 **solutions 模块的 QueueManager** 组合:先检测画面中的人/物,再结合 `region` 定义的 ROI 区域判断队列长度与分布。
- `model.track` 调用底层跟踪(多目标追踪),通过 `{% include "macros/track-args.md" %}` 宏注入追踪参数(原文档此处以宏引用形式给出,未列出具体字段)。
- `process_queue(im0)` 是核心方法:接收单帧图像 → 在 ROI 内完成检测+追踪+队列计数 → 返回(示例中变量 `out` 被赋值但未进一步使用,绘制结果在原 `im0` 上)。

**性能/数据(原文未给出):**
- 文档未提供 FPS、推理时延、队列计数准确率等基准数据。
- 文档未给出具体 ROI 像素与实际相机分辨率的换算关系(仅以示例坐标呈现)。

---

## 【表格解读】

### 表 1:Real World Applications(应用场景对照表)

| Logistics | Retail |
| :---: | :---: |
| ![Queue management at airport ticket counter using Ultralytics YOLO11](https://github.com/ultralytics/docs/releases/download/0/queue-management-airport-ticket-counter-ultralytics-yolov8.avif) | ![Queue monitoring in crowd using Ultralytics YOLO11](https://github.com/ultralytics/docs/releases/download/0/queue-monitoring-crowd-ultralytics-yolov8.avif) |
| Queue management at airport ticket counter Using Ultralytics YOLO11 | Queue monitoring in crowd Ultralytics YOLO11 |

**逐行解读:**
- **Logistics 列**:展示机场票务柜台的队列监测场景,YOLO11 在该列负责识别柜台前排队人员,体现"基础设施类高客流量场所"的适用性。
- **Retail 列**:展示人群中的队列监控,说明同一方案可直接复用至零售场景。
- 两列共用同一模型(`yolo11n.pt`)与同一 `QueueManager` 类,差异主要在 ROI 设置和业务阈值。

---

### 表 2:Arguments `QueueManager`(类参数表)

| Name | Type | Default | Description |
| ------------ | ------ | -------------------------- | ---------------------------------------------------- |
| `model` | `str` | `None` | Path to Ultralytics YOLO Model File |
| `region` | `list` | `[(20, 400), (1260, 400)]` | List of points defining the queue region. |
| `line_width` | `int` | `2` | Line thickness for bounding boxes. |
| `show` | `bool` | `False` | Flag to control whether to display the video stream. |

**逐行解读:**
- **`model`**:必传,YOLO 模型权重路径;示例统一使用 `yolo11n.pt`(轻量,适合实时)。
- **`region`**:定义监测区的折点列表;示例用四点构成四边形,默认两点构成一条水平线(用于"过线计数"风格场景)。
- **`line_width`**:控制边界框/分隔线像素粗细,默认 `2`;FAQ 示例中调为 `3` 以更醒目。
- **`show`**:是否开启 OpenCV 实时弹窗;默认 `False`(通常写入视频文件而非弹窗)。

---

### 表 3:Arguments `model.track`(追踪参数表)

> 原文以宏 `{% include "macros/track-args.md" %}` 引用,**未在本页展开具体字段**;此处仅保留占位说明。

---

## 【公式解读】

**原文无公式。**

(整篇文档基于工程参数与代码示例展开,未出现 LaTeX 公式或伪代码形式的数学表达式。)

---

## 【关联】

- **与 Ultralytics HUB 的关系**:FAQ 中提到 HUB 提供"用户友好的部署与管理平台",可简化 `QueueManager` 的工程化落地。
- **与 `solutions` 模块的关系**:`QueueManager` 是 `ultralytics.solutions` 命名空间下的方案类之一,与其它 solutions 类(文档未在本页展开)共享相似的 `process_*` 调用约定。
- **与 `model.track` 的关系**:底层的对象跟踪能力由 `model.track` 提供(`track-args.md` 宏),`QueueManager` 在此基础上做队列计数/区域判定。
- **与同类框架的关系**:FAQ 中将 YOLO11 与 **TensorFlow**、**Detectron2** 进行对比,定位 YOLO11 在实时性、易用性、预训练模型、社区支持上的优势。
- **参考文档链接(原文给出)**:
  - `https://docs.ultralytics.com/reference/solutions/queue_management/`(Queue Management API 参考)
  - `https://docs.ultralytics.com/hub/`(Ultralytics HUB)
  - `https://docs.ultralytics.com/quickstart/`(快速上手)
  - `https://www.ultralytics.com/glossary/tensorflow`(TensorFlow 术语词条)
- **本仓内链接**:原文未提供仓库内部链接(无内部交叉引用)。

---

## 【使用方法】

### 启用方式(原文给出):
1. 安装 Ultralytics 包并准备 YOLO11 权重(示例 `yolo11n.pt`)。
2. 通过 OpenCV 读取视频流(`cv2.VideoCapture("Path/to/video/file.mp4")`)。
3. 定义 `queue_region`(折点列表)。
4. 实例化 `solutions.QueueManager(model=..., region=..., classes=..., line_width=...)`。
5. 在循环内调用 `queue.process_queue(im0)`,将结果写入 `cv2.VideoWriter` 输出文件 `queue_management.avi`(编码 `mp4v`)。
6. 可选:若 `show=True` 或手动 `cv2.imshow("Queue Management", im0)`,按 `q` 退出。

### 关键配置项汇总(原文):
| 配置项 | 取值示例 | 来源段落 |
| --- | --- | --- |
| `model` | `"yolo11n.pt"` | Queue Manager / Specific Classes 示例 |
| `region` | `[(20, 400), (1080, 404), (1080, 360), (20, 360)]` | Queue Manager 示例 |
| `region`(默认) | `[(20, 400), (1260, 400)]` | Arguments 表 |
| `line_width` | `2`(默认)/ `3`(FAQ 示例) | Arguments 表 / FAQ 示例 |
| `show` | `False`(默认) | Arguments 表 |
| `classes` | `3`(Specific Classes 示例) | Specific Classes 示例 |
| 输出文件 | `queue_management.avi` | Queue Manager 示例 |
| 视频编码 | `mp4v` | Queue Manager 示例 |
| 退出键 | `ord("q")` | 主循环 |

> 注:`model.track` 的详细参数未在本页展开,需查阅 `macros/track-args.md`(原文未列出具体字段)。
