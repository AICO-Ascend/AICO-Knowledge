# TFLite, ONNX, CoreML, TensorRT Export

> 仓 `modelzoo-gpl` · 路径 `built-in/PyTorch/Official/cv/object_detection/Yolov8_for_PyTorch/docs/en/yolov5/tutorials/model_export.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-gpl/built-in/PyTorch/Official/cv/object_detection/Yolov8_for_PyTorch/docs/en/yolov5/tutorials/model_export.md

# YOLOv5 模型导出指南深度解读

## 【定位】

本指南解决如何将训练好的 YOLOv5 PyTorch 模型导出为 11 种主流推理格式（TorchScript、ONNX、OpenVINO、TensorRT、CoreML、TensorFlow 家族、PaddlePaddle 等）的问题，旨在为不同部署硬件（CPU/GPU/移动端/边缘 TPU/浏览器）匹配最优模型表示，从而突破原始 PyTorch 模型的部署环境限制。

---

## 【技术要点】

1. **导出方式**：通过 `python export.py --weights <model> --include <formats>` 命令一键生成目标格式，默认输出与源 `.pt` 文件并列存放。
2. **11 种支持格式**及对应 `--include` 关键字见下方表格，包括 `torchscript`、`onnx`、`engine`（TensorRT）、`coreml`、`tflite`、`edgetpu`、`tfjs`、`paddle`、`openvino`、`pb`、`saved_model`。
3. **环境前置条件**：Python >= 3.8.0、PyTorch >= 1.8，需 `git clone yolov5` 后 `pip install -r requirements.txt`，模型和数据集自动从最新 YOLOv5 release 下载。
4. **性能基线数字（原文 ProTip）**：导出到 ONNX 或 OpenVINO 可获最高 3x CPU 加速；导出到 TensorRT 可获最高 5x GPU 加速。
5. **导出可选参数**：`--half`（FP16 半精度以缩小文件体积）、`opset=12`（ONNX opset 版本）、`topk_per_class=100`、`topk_all=100`、`iou_thres=0.45`、`conf_thres=0.25`（推理后处理参数）。
6. **模型输出形状固定**：`yolov5s` 导出后输出张量形状为 `(1, 25200, 85)`，对应 640x640 输入下的锚框数和 (4+1+80) 类别配置。

---

## 【关键机制与数据】

原文：导出流程由 `export.py` 驱动，典型执行日志显示 PyTorch 模型先经 `Fusing layers...` 层融合优化（YOLOv5s 共 213 层、7225885 参数），再依次导出各格式并报告耗时：`TorchScript: export success ✅ 1.7s, saved as yolov5s.torchscript (28.1 MB)`；`ONNX: export success ✅ 2.3s, saved as yolov5s.onnx (28.0 MB)`；整个 `Export complete (5.5s)`。

原文：模型尺寸对比——`yolov5s.pt` PyTorch 14.1 MB；导出为 TorchScript 28.1 MB、ONNX 28.0 MB（TorchScript/ONNX 文件约为 PyTorch 的 2 倍，原文未解释原因）。

原文：GPU 推理性能（Colab Pro V100、imgsz=640、batch_size=1）：PyTorch 10.19 ms → TensorRT 1.89 ms（≈5.4x 加速）；TorchScript 6.85 ms；ONNX 14.63 ms；TensorFlow SavedModel 21.28 ms；TensorFlow GraphDef 21.22 ms；OpenVINO/CoreML/TFLite/EdgeTPU/TFJS 均为 NaN（V100 GPU 上不适用）。

原文：CPU 推理性能（Colab Pro CPU、imgsz=640、batch_size=1）：PyTorch 127.61 ms → OpenVINO 66.52 ms（≈1.92x）、ONNX 69.34 ms（≈1.84x）；TorchScript 131.23 ms（最慢，与 PyTorch 接近）；TensorFlow Lite 316.61 ms（CPU 上比 PyTorch 慢约 2.5x）；TensorRT/CoreML/EdgeTPU/TFJS 为 NaN（CPU 上不适用）。

原文：模型系列：`yolov5n.pt` / `yolov5s.pt` / `yolov5m.pt` / `yolov5l.pt` / `yolov5x.pt` 五档；P6 系列如 `yolov5s6.pt`；自定义训练产物 `runs/exp/weights/best.pt`。

---

## 【表格解读】

### 表 1：11 种导出格式与对应参数

| Format | `export.py --include` | Model |
| :--- | :--- | :--- |
| PyTorch | - | `yolov5s.pt` |
| TorchScript | `torchscript` | `yolov5s.torchscript` |
| ONNX | `onnx` | `yolov5s.onnx` |
| OpenVINO | `openvino` | `yolov5s_openvino_model/` |
| TensorRT | `engine` | `yolov5s.engine` |
| CoreML | `coreml` | `yolov5s.mlmodel` |
| TensorFlow SavedModel | `saved_model` | `yolov5s_saved_model/` |
| TensorFlow GraphDef | `pb` | `yolov5s.pb` |
| TensorFlow Lite | `tflite` | `yolov5s.tflite` |
| TensorFlow Edge TPU | `edgetpu` | `yolov5s_edgetpu.tflite` |
| TensorFlow.js | `tfjs` | `yolov5s_web_model/` |
| PaddlePaddle | `paddle` | `yolov5s_paddle_model/` |

**逐行解读**：第 1 行 PyTorch 是源格式，本身已是 `.pt` 无需 `--include`，代表"导出基准"；第 2-3 行 TorchScript 与 ONNX 是通用跨平台格式，分别面向 PyTorch JIT 与开放神经网络交换生态；第 4 行 OpenVINO 面向 Intel CPU/GPU/VPU 推理，产物是一个目录；第 5 行 TensorRT 面向 NVIDIA GPU（`engine`），配合下方 benchmark 可获 ~5x 加速；第 6 行 CoreML 面向 Apple 设备（macOS/iOS）；第 7-10 行都是 TensorFlow 家族产物，覆盖服务器（SavedModel/GraphDef）、移动（TF Lite）、Google Edge TPU 硬件（专用的 `.tflite` 变体）和浏览器端 JS 推理（产物为 `web_model` 目录）；第 12 行 PaddlePaddle 是国内百度飞桨生态，面向部署到支持 Paddle 的推理引擎。

### 表 2：Colab Pro V100 GPU 基准

| | Format | mAP@0.5:0.95 | Inference time (ms) |
| :--- | :--- | :--- | :--- |
| 0 | PyTorch | 0.4623 | 10.19 |
| 1 | TorchScript | 0.4623 | 6.85 |
| 2 | ONNX | 0.4623 | 14.63 |
| 3 | OpenVINO | NaN | NaN |
| 4 | TensorRT | 0.4617 | 1.89 |
| 5 | CoreML | NaN | NaN |
| 6 | TensorFlow SavedModel | 0.4623 | 21.28 |
| 7 | TensorFlow GraphDef | 0.4623 | 21.22 |
| 8 | TensorFlow Lite | NaN | NaN |
| 9 | TensorFlow Edge TPU | NaN | NaN |
| 10 | TensorFlow.js | NaN | NaN |

**逐行解读**：PyTorch 行作为基线 10.19 ms；TorchScript 6.85 ms 比 PyTorch 快约 1.5x；ONNX 反而比 PyTorch 慢（14.63 ms，原文未加 GPU 优化）；TensorRT 行 mAP=0.4617 比 PyTorch 仅低 0.0006 但延迟 1.89 ms，提速约 5.4x，是 GPU 部署最优选；TensorFlow 家族两种格式都在 ~21 ms，比 PyTorch 慢；OpenVINO/CoreML/TFLite/EdgeTPU/TFJS 在 V100 上为 NaN（不支持或不适用）。

### 表 3：Colab Pro CPU 基准

| | Format | mAP@0.5:0.95 | Inference time (ms) |
| :--- | :--- | :--- | :--- |
| 0 | PyTorch | 0.4623 | 127.61 |
| 1 | TorchScript | 0.4623 | 131.23 |
| 2 | ONNX | 0.4623 | 69.34 |
| 3 | OpenVINO | 0.4623 | 66.52 |
| 4 | TensorRT | NaN | NaN |
| 5 | CoreML | NaN | NaN |
| 6 | TensorFlow SavedModel | 0.4623 | 123.79 |
| 7 | TensorFlow GraphDef | 0.4623 | 121.57 |
| 8 | TensorFlow Lite | 0.4623 | 316.61 |
| 9 | TensorFlow Edge TPU | NaN | NaN |
| 10 | TensorFlow.js | NaN | NaN |

**逐行解读**：PyTorch 行作为 CPU 基线 127.61 ms；ONNX 69.34 ms 与 OpenVINO 66.52 ms 几乎相同，提速约 1.85x，是 CPU 部署推荐选项；TorchScript 在 CPU 上反而略慢于 PyTorch（131.23 ms），不适合 CPU 部署；TensorFlow Lite 在 x86 CPU 上劣化明显（316.61 ms，原文未说明原因，推测与其为 ARM/移动优化有关）；TensorRT/CoreML/EdgeTPU/TFJS 在 CPU 环境为 NaN。

---

## 【公式解读】

原文无公式。

---

## 【关联】

本文档位于 `built-in/PyTorch/Official/cv/object_detection/Yolov8_for_PyTorch/docs/en/yolov5/tutorials/model_export.md`，是 YOLOv5 上游官方教程体系中的一篇导出指南。

**文中实际提及的关联资源（原文链接）**：
- 训练后推理调用 `python detect.py --weights yolov5s.onnx`
- 精度评测 `python val.py --weights yolov5s.onnx`
- PyTorch Hub 加载 `torch.hub.load('ultralytics/yolov5', 'custom', 'yolov5s.onnx')`
- Netron 可视化：https://github.com/lutzroeder/netron
- TensorRT 导出示例见 Colab 教程 notebook
- 预训练模型列表见 YOLOv5 README
- CPU 加速参考 PR #6613，GPU 加速参考 PR #6963
- 基准测试脚本：`benchmarks.py`

**文末内部链接**（`../environments/google_cloud_quickstart_tutorial.md`、`../environments/aws_quickstart_tutorial.md`、`../environments/azureml_quickstart_tutorial.md`、`../environments/docker_image_quickstart_tutorial.md`）这些是云平台/Docker 部署教程，与本文档内容不直接交叉引用；本文档不涉及 GPU 云实例选型，但这些教程可作为"得到 .pt 模型后做云端推理服务部署"的下游使用场景参考。

---

## 【使用方法】

**1. 克隆与安装（原文 Before You Start）**

```bash
git clone https://github.com/ultralytics/yolov5
cd yolov5
pip install -r requirements.txt
```

环境要求：Python >= 3.8.0、PyTorch >= 1.8。

**2. 导出命令（原文 Export a Trained YOLOv5 Model）**

```bash
python export.py --weights yolov5s.pt --include torchscript onnx
```

可选模型清单：`yolov5n.pt` / `yolov5s.pt` / `yolov5m.pt` / `yolov5l.pt` / `yolov5x.pt` 及 P6 系列 `yolov5s6.pt` 等；自定义训练结果路径 `runs/exp/weights/best.pt`。

**3. 半精度导出（原文 ProTip）**

```bash
python export.py --weights yolov5s.pt --include torchscript onnx --half
```

导出时加 `--half` 得 FP16 模型，文件更小。

**4. 导出后推理使用（原文输出日志末尾）**

```bash
python detect.py --weights yolov5s.onnx       # 目标检测推理
python val.py --weights yolov5s.onnx          # 精度校验
```

PyTorch Hub 加载：

```python
model = torch.hub.load('ultralytics/yolov5', 'custom', 'yolov5s.onnx')
```

可视化使用 Netron Viewer（https://netron.app/ ）打开导出的 `.onnx` / `.torchscript` / `.engine` 等文件查看网络结构。

**5. 复现基准测试（原文 Benchmarks）**

```bash
python benchmarks.py --weights yolov5s.pt --imgsz 640 --device 0   # GPU
python benchmarks.py --weights yolov5s.pt --imgsz 640 --device cpu # CPU
```

原文未涉及 TensorRT 导出的命令行调用，仅指引到 Colab tutorial notebook 的 appendix section。
