# list of images in local filesystem

> 仓 `modelzoo-gpl` · 路径 `built-in/PyTorch/Official/cv/object_detection/Yolov8_for_PyTorch/docs/en/yolov5/tutorials/neural_magic_pruning_quantization.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-gpl/built-in/PyTorch/Official/cv/object_detection/Yolov8_for_PyTorch/docs/en/yolov5/tutorials/neural_magic_pruning_quantization.md

# YOLOv5 × Neural Magic DeepSparse 部署指南 — 一体化深度解读

---

## 【定位】

这篇文档解决**"如何在 CPU 上以 GPU 级性能部署 YOLOv5"**的问题:它系统介绍 Neural Magic 公司推出的 DeepSparse 推理运行时,展示其如何借助模型稀疏化(剪枝 + 量化)在不依赖硬件加速器的情况下,为 YOLOv5 带来相对 ONNX Runtime 的 5.8× 吞吐加速,同时给出 Python API、HTTP Server、Annotate CLI 三种部署/标注方式以及基准测试流程。

---

## 【技术要点】

1. **核心加速手段 — 稀疏化 (Sparsification)**
   - 通过 pruning(剪枝)+ quantization(量化)实现模型稀疏化,可获得"数量级"的大小和计算量缩减,同时保持高精度。
   - DeepSparse 是 sparsity-aware 的,推理时跳过被置零的参数,从而降低前向计算量。

2. **计算范式 — Tensor Columns**
   - 稀疏计算变成 memory-bound,DeepSparse 采用按网络 depth-wise 执行,把问题切成 Tensor Columns —— 即"竖直条纹状"的、能装进 cache 的计算块。

3. **生态组件**
   - **SparseZoo**:开源预稀疏化模型仓库,内置 YOLOv5 各规模预剪枝/量化 checkpoint。
   - **SparseML**:与 Ultralytics 集成,可通过单条 CLI 命令把稀疏 checkpoint 微调到自有数据上。

4. **部署入口**
   - 安装:`pip install "deepsparse[server,yolo,onnxruntime]"`。
   - 模型可接受 SparseZoo stub 或本地 ONNX 路径。
   - 官方文档示例使用的两个 stub:
     - dense 基线:`zoo:cv/detection/yolov5-s/pytorch/ultralytics/coco/base-none`
     - pruned + quantized:`zoo:cv/detection/yolov5-s/pytorch/ultralytics/coco/pruned65_quant-none`

5. **三种使用方式**
   - **Python API**:`Pipeline.create(task="yolo", model_path=...)`,直接处理原始图像,输出 boxes/classes。
   - **HTTP Server**:基于 FastAPI + Uvicorn,CLI 一行起服务,端点 `/predict/from_files` 接受图像、返回 JSON boxes/labels。
   - **Annotate CLI**:本地直接生成带框标注图,支持 `--source 0`(实时摄像头)。

6. **基准测试数据(Batch Size = 32,AWS `c6i.8xlarge`,16 cores)**
   - ONNX Runtime(dense 原始):41.9025 items/sec(≈ 42 images/sec)。
   - DeepSparse(dense 原始):69.5546 items/sec,**1.7× over ORT**。
   - DeepSparse(pruned65_quant 稀疏):**241 images/sec**,**5.8× over ORT**(原文中 batch 32 命令段被截断)。

---

## 【关键机制与数据】

**工作原理(原文):**"Sparsification through pruning and quantization is a broadly studied technique, allowing order-of-magnitude reductions in the size and compute needed to execute a network, while maintaining high accuracy. DeepSparse is sparsity-aware, meaning it skips the zeroed out parameters, shrinking amount of compute in a forward pass."

- 即剪枝 + 量化 → 把权重中大量元素置零 → 推理时跳过零 → 计算量减少。
- 关键性能增益来自于:**"稀疏计算 now memory bound"**;内存带宽而非算力成为瓶颈,因此 DeepSparse 选用"depth-wise + Tensor Columns"策略,把每列 stripe 放进 cache,使内存访问局部化,大幅提升吞吐。

**性能数据流(原文截取的吞吐量对比,单位 items/sec,Batch Size = 32,AWS c6i.8xlarge 16 cores):**

| 方案 | 模型 | 吞吐 (items/sec) | 相对 ORT 加速比 |
|------|------|------------------|-----------------|
| ONNX Runtime | YOLOv5s base-none (dense) | 41.9025 (≈ 42) | 1.0×(baseline) |
| DeepSparse | YOLOv5s base-none (dense) | 69.5546 (≈ 70) | 1.7× |
| DeepSparse | YOLOv5s pruned65_quant-none | 241 | 5.8× |

(原文第 6 段宣传语:"compared to the ONNX Runtime baseline, DeepSparse offers a 5.8x speed-up for YOLOv5s, running on the same machine!",与上表最后一行一致。)

**部署特性(原文三条要点):**
- Flexible Deployments — cloud、data center、edge 一致执行;支持 Intel / AMD / ARM。
- Infinite Scalability — 纵向扩到 100s 核;横向用标准 Kubernetes;或完全抽象的 Serverless。
- Easy Integration — 提供干净的 API 与生产监控。

---

## 【表格解读】

原文无表格(性能对比只在正文中以文字 + 命令输出形式给出)。

> 备注:文中虽含 `>` 格式的命令输出块(如 `> Throughput (items/sec): 41.9025`),但这些是 CLI 截图片段,并非结构化 markdown 表格,故按"原文无表格"处理。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **上游/依赖**:
  - **SparseZoo** — 文中出现两次:`zoo:cv/detection/yolov5-s/pytorch/ultralytics/coco/base-none`、`zoo:cv/detection/yolov5-s/pytorch/ultralytics/coco/pruned65_quant-none`,作为 DeepSparse 推理及 benchmark 使用的模型源。
  - **SparseML** — "integrated with Ultralytics",负责在用户自有数据上微调 SparseZoo 中的稀疏 checkpoint。
  - **Ultralytics** — DeepSparse 通过 Ultralytics 集成,YOLOv5 的训练/导出生态直接对接。
  - **ONNX / ONNX Runtime** — DeepSparse 接受 ONNX 模型,benchmark 章节以 ONNX Runtime 为对照基线。
  - **FastAPI + Uvicorn** — DeepSparse Server 的 HTTP 服务底座。
  - **OpenCV(libGL.so.1)** — Python API 在云端运行时可能因缺 `libGL.so.1` 报错,需 `apt-get install libgl1`。

- **下游/输出**:文档链接到 Neural Magic 官方 YOLOv5 文档 `https://docs.neuralmagic.com/computer-vision/object-detection/`,供进一步阅读。

- **能力外延**(原文提到的关键能力):
  - 实时标注(`--source 0` 走摄像头)。
  - 多场景部署:cloud / data center / edge。
  - Kubernetes 与 Serverless 两种扩展路径。

---

## 【使用方法】

### 1. 安装
```bash
pip install "deepsparse[server,yolo,onnxruntime]"
```

### 2. 准备样本图
```bash
wget -O basilica.jpg https://raw.githubusercontent.com/neuralmagic/deepsparse/main/src/deepsparse/yolo/sample_images/basilica.jpg
```

### 3. Python API 推理(关键配置项)
```python
from deepsparse import Pipeline

images = ["basilica.jpg"]
yolo_pipeline = Pipeline.create(
    task="yolo",
    model_path="zoo:cv/detection/yolov5-s/pytorch/ultralytics/coco/pruned65_quant-none",
)
pipeline_outputs = yolo_pipeline(images=images, iou_thres=0.6, conf_thres=0.001)
```
- 配置项:`task="yolo"`、`model_path`(SparseZoo stub 或本地 ONNX 路径)、`iou_thres`、`conf_thres`。

### 4. HTTP Server(CLI)
```bash
deepsparse.server \
    --task yolo \
    --model_path zoo:cv/detection/yolov5-s/pytorch/ultralytics/coco/pruned65_quant-none
```
- 客户端请求端点:`POST http://0.0.0.0:5543/predict/from_files`,files 字段传图像;响应 JSON 中取 `boxes`、`labels` 字段。

### 5. Annotate CLI(本地标注)
```bash
deepsparse.object_detection.annotate \
    --model_filepath zoo:cv/detection/yolov5-s/pytorch/ultralytics/coco/pruned65_quant-none \
    --source basilica.jpg
```
- `--source 0` 切换为实时摄像头流;默认输出到 `annotation-results/` 目录。

### 6. Benchmark 命令(Batch 32 案例)
```bash
# ONNX Runtime 基线
deepsparse.benchmark zoo:cv/detection/yolov5-s/pytorch/ultralytics/coco/base-none \
    -s sync -b 32 -nstreams 1 -e onnxruntime

# DeepSparse(dense)
deepsparse.benchmark zoo:cv/detection/yolov5-s/pytorch/ultralytics/coco/base-none \
    -s sync -b 32 -nstreams 1

# DeepSparse(pruned + quantized) — 原文此处命令被截断,需按同样 -s sync -b 32 -nstreams 1 模式补充完整
```

### 7. 环境小坑
- 云端 opencv 缺 `libGL.so.1` 时:`apt-get install libgl1`。

---

> 备注:原文最末一行的 benchmark 命令(`deepsparse.benchmark zoo:cv/detection/yolov5-s/pytorch/ul...`)在提供的片段里被截断,因此 pruned65_quant 模型对应的完整 CLI 行未在原文中给出,以上仅按已有命令风格补全,具体参数建议参考 DeepSparse 官方文档。
