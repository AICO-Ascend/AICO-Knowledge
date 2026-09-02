# Quick Start Guide: Raspberry Pi with Ultralytics YOLO11

> 仓 `modelzoo-gpl` · 路径 `built-in/PyTorch/Official/cv/object_detection/Yolov8_for_PyTorch/docs/en/guides/raspberry-pi.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-gpl/built-in/PyTorch/Official/cv/object_detection/Yolov8_for_PyTorch/docs/en/guides/raspberry-pi.md

# 深度解读:Raspberry Pi with Ultralytics YOLO11 Guide

> ⚠️ **文件路径与内容不一致说明**:原文所在路径为 `built-in/PyTorch/Official/cv/object_detection/Yolov8_for_PyTorch/docs/en/guides/raspberry-pi.md`,但文档实际内容是 **Ultralytics YOLO11**(而非 Yolov8)在 Raspberry Pi 上的部署指南。该指南源自 Ultralytics 官方 docs(以 YOLO11 为主体),属于代码仓内并存的官方文档资产。下文解读严格基于原文内容,不补全缺失内容。

---

## 【定位】

本文档是一篇 **端到端快速上手指南**,解决"如何在 Raspberry Pi 上部署并运行 Ultralytics YOLO11 进行目标检测"的问题,涵盖设备选型参考、操作系统准备、Ultralytics 安装(Docker 与裸装两种路径)、NCNN 模型导出与推理、以及 YOLO11n 与 YOLO11s 在 Raspberry Pi 5 上的 9 种模型格式性能基准对比。

---

## 【技术要点】

1. **适配设备与系统**:已实测可在 **Raspberry Pi 4** 与 **Raspberry Pi 5** 上运行,系统要求为最新版 **Raspberry Pi OS Bookworm (Debian 12)**;原文标注 Pi 3 等旧设备只要安装同样的 Bookworm 也应可工作。
2. **两种安装路径**:① **Docker 方式** —— 拉取 `ultralytics/ultralytics:latest-arm64` 镜像(基于 `arm64v8/debian`,内含 Debian 12 Bookworm + Python3);② **裸装方式** —— `apt update` → `apt install python3-pip` → `pip install ultralytics[export]` → `sudo reboot`。
3. **推荐推理后端 — NCNN**:Ultralytics 支持的所有导出格式中,**NCNN 因针对 ARM 架构的移动/嵌入式平台做了高度优化**,在 Raspberry Pi 上推理性能最佳,被原文明确推荐。
4. **导出与推理流程**:`YOLO("yolo11n.pt")` → `model.export(format="ncnn")` 生成 `yolo11n_ncnn_model` 目录 → 重新以 `YOLO("yolo11n_ncnn_model")` 加载 → 对图像/URL 推理;CLI 对应 `yolo export model=yolo11n.pt format=ncnn` 与 `yolo predict model='yolo11n_ncnn_model' source=...`。
5. **基准测试条件**:在 **Raspberry Pi 5** 上以 **FP32 精度**、默认输入尺寸 **640** 对 9 种格式(PyTorch、TorchScript、ONNX、OpenVINO、TF SavedModel、TF GraphDef、TF Lite、PaddlePaddle、NCNN)做测速与精度测量,指标为 `mAP50-95(B)` 与 `Inference time (ms/im)`。
6. **基准测试覆盖范围**:仅纳入 **YOLO11n** 与 **YOLO11s**,原文给出原因 —— 其它尺寸的模型在 Raspberry Pi 上"太大,无法运行且无法提供体面性能"。

---

## 【关键机制与数据】

### 工作原理 / 数据流

- **Docker 路径**:以 `arm64v8/debian` 镜像为基础 → 容器内已预装 Ultralytics → `docker run -it --ipc=host` 启动后可直接跳到 NCNN 推理环节。`--ipc=host` 用于共享主机 IPC 命名空间,便于 PyTorch 多进程/共享内存正常工作。
- **裸装路径**:`apt` 装 pip → `pip install -U pip` 升级 → `pip install ultralytics[export]` 拉取 Ultralytics 主包及可选导出依赖 → 重启使系统环境生效。
- **NCNN 导出机制**:PyTorch `.pt` → 调用 `export(format="ncnn")` → 产出 `yolo11n_ncnn_model`(目录,内含 NCNN 所需的 `.param` / `.bin` 等文件) → 用同一个 `YOLO` 类再次加载该目录即可推理。导出格式的更多参数被指向 `docs.ultralytics.com/guides/model-deployment-options/`。

### 性能数据(原文:Raspberry Pi 5, FP32, image size 640)

原文仅给到 **YOLO11n** 部分行的明确数值,其它行在原文中已被截断。已确认的数据点:

- YOLO11n / PyTorch:✅,**5.4 MB**,mAP50-95(B)=**0.61**,Inference time=**524.828 ms/im**
- YOLO11n / TorchScript:✅,**10.5 MB**,mAP50-95(B)=**0.6082**,Inference time=**666.874 ms/im**
- YOLO11n / ONNX:✅ (其余列在原文中被截断,数值未给出)

YOLO11s 的数据、其它 6 种格式的数据、对比图(`rpi-yolo11-benchmarks.avif`)中蕴含的 NCNN/OpenVINO 等数值,原文未保留 → 不得臆造。

---

## 【表格解读】

### 表 1:Raspberry Pi Series Comparison(逐字还原)

|                   | Raspberry Pi 3                         | Raspberry Pi 4                         | Raspberry Pi 5                         |
| ----------------- | -------------------------------------- | -------------------------------------- | -------------------------------------- |
| CPU               | Broadcom BCM2837, Cortex-A53 64Bit SoC | Broadcom BCM2711, Cortex-A72 64Bit SoC | Broadcom BCM2712, Cortex-A76 64Bit SoC |
| CPU Max Frequency | 1.4GHz                                 | 1.8GHz                                 | 2.4GHz                                 |
| GPU               | Videocore IV                           | Videocore VI                           | VideoCore VII                          |
| GPU Max Frequency | 400Mhz                                 | 500Mhz                                 | 800Mhz                                 |
| Memory            | 1GB LPDDR2 SDRAM                       | 1GB, 2GB, 4GB, 8GB LPDDR4-3200 SDRAM   | 4GB, 8GB LPDDR4X-4267 SDRAM            |
| PCIe              | N/A                                    | N/A                                    | 1xPCIe 2.0 Interface                   |
| Max Power Draw    | 2.5A@5V                                | 3A@5V                                  | 5A@5V (PD enabled)                     |

**逐行解读**:
- **CPU**:Pi 3/4/5 分别使用 Broadcom BCM2837/BCM2711/BCM2712,核心从 Cortex-A53 → A72 → A76,微架构代际跃升明显,是 NCNN 推理加速的硬件底座。
- **CPU Max Frequency**:1.4 → 1.8 → 2.4 GHz,Pi 5 单核频率提升 ~71% 相对 Pi 3,是其推理速度优于前代的关键之一。
- **GPU**:VideoCore IV → VI → VII,频率 400 → 500 → 800 MHz;原文未涉及 GPU 推理路径,这里主要做硬件代际参考。
- **Memory**:Pi 3 仅 1GB LPDDR2;Pi 4 提供 1/2/4/8GB LPDDR4-3200;Pi 5 起步 4GB、最高 8GB LPDDR4X-4267,带宽更大,有助于减少 CPU↔内存往返造成的推理瓶颈。
- **PCIe**:仅 Pi 5 提供 **1×PCIe 2.0**,为后续通过 PCIe 设备(如 Hailo 加速器、NVMe SSD)扩展留出空间 —— 原文未直接展开,但属于 Pi 5 相对前代的关键差异。
- **Max Power Draw**:2.5A@5V → 3A@5V → **5A@5V (PD enabled)**,Pi 5 支持 USB-PD 协议取电,功率裕度更大,便于在满负载推理下保持稳定。

### 表 2:YOLO11n Detailed Comparison(原文已被截断,仅逐字还原保留部分)

| Format        | Status | Size on disk (MB) | mAP50-95(B) | Inference time (ms/im) |
|---------------|--------|-------------------|-------------|------------------------|
| PyTorch       | ✅      | 5.4               | 0.61        | 524.828                |
| TorchScript   | ✅      | 10.5              | 0.6082      | 666.874                |
| ONNX          | ✅      | (原文截断,未给出) | (原文截断,未给出) | (原文截断,未给出) |

**逐行解读(基于已给出的行)**:
- **PyTorch 行**:✅ 状态可用;磁盘 **5.4 MB** 是各格式中最小的之一;mAP50-95(B)=**0.61** 是基准精度;**524.828 ms/im**(≈1.9 FPS)说明纯 PyTorch 即便在 Pi 5 上也偏慢,提示需要导出到优化格式。
- **TorchScript 行**:✅ 状态可用;磁盘 **10.5 MB**(几乎是 PyTorch 的两倍,但精度仅微降到 **0.6082**,差 0.0018);推理时间反而上升到 **666.874 ms/im**,提示 TorchScript 在 ARM 上的优化路径对该模型并未带来加速收益。
- **ONNX 行**:仅给到状态 ✅,其余列在原文档流中被截断;因此**关于 ONNX 的磁盘占用、mAP、推理时间均不得臆造**,需结合官方网页或外部基准表对照。
- **(未给出的 YOLO11s 表与剩余 6 个格式行)**:原文在同一 section 内只展示了标题与表头,YOLO11s 表及 NCNN/OpenVINO/TF Lite 等关键数据**在原文中并未保留**,不补全。

---

## 【公式解读】

**原文无公式**(无 LaTeX 表达式,无伪代码公式块)。文档中只包含命令、Python 代码片段与表格数据,未给出任何数学公式或推导式。

---

## 【关联】

原文提及并在文末出现的内部相对链接有:
- **`../modes/export.md`**(出现两次):指向 Ultralytics 的导出模式文档。本指南中"导出 NCNN 并推理"的核心代码块正是这一章节的下游落地;Python/CLI 中的 `model.export(format="ncnn")`、`yolo export model=... format=ncnn` 命令的所有可选参数(`imgsz`、`half`、`int8`、`device` 等)在该导出页中描述。
- **`../index.md`**:指向 Ultralytics 文档总索引;本指南属于"guides/(部署类)"分类下的子页,通常与 Jetson、Rockchip、Seeed Studio reTerminal 等边缘设备部署指南并列。

此外,文中多次跳转到 **Ultralytics 官方域名 `docs.ultralytics.com`** 的外部链接(NCNN 集成页、模型部署选项页)以及 **Raspberry Pi 官方文档站**(Getting Started、Operating Systems 页),这些**不属于本仓的相对内部链接**,因此不计入"内部关联"。

---

## 【使用方法】

### 启用方式 A:Start with Docker(原文给出完整命令)

```bash
t=ultralytics/ultralytics:latest-arm64 && sudo docker pull $t && sudo docker run -it --ipc=host $t
```

### 启用方式 B:Start without Docker(原文给出分步命令)

```bash
sudo apt update
sudo apt install python3-pip -y
pip install -U pip
pip install ultralytics[export]
sudo reboot
```

### 模型导出与推理(原文给出 Python 与 CLI 两套)

Python:
```python
from ultralytics import YOLO
model = YOLO("yolo11n.pt")
model.export(format="ncnn")          # 生成 'yolo11n_ncnn_model'
ncnn_model = YOLO("yolo11n_ncnn_model")
results = ncnn_model("https://ultralytics.com/images/bus.jpg")
```

CLI:
```bash
yolo export model=yolo11n.pt format=ncnn
yolo predict model='yolo11n_ncnn_model' source='https://ultralytics.com/images/bus.jpg'
```

### 关键配置项(原文有提到)
- `format="ncnn"`:导出目标格式选择,是 Pi 上推理性能最优选项。
- 默认输入尺寸 **640**,FP32 **精度** —— 基准测试与示例推理均沿用此默认。
- 设备能力门槛:Pi 4/5 + Raspberry Pi OS Bookworm(Debian 12)。

### 原文未涉及
- 启用 **摄像头实时推理** 的具体命令(原文仅以静态图片 URL 演示)。
- **GPIO/传感器联动** 的范例代码(虽然 Raspberry Pi 简介段提及 GPIO,但正文未给出样例)。
- **加速器(如 Hailo)** 通过 Pi 5 的 PCIe 接口接入的步骤(原文表格列出 1×PCIe 2.0 但未展开)。
- **ONNX、OpenVINO、TF Lite 等格式**在 Pi 上的具体导出参数,这些需跳转至 `docs.ultralytics.com/guides/model-deployment-options/` 获取。
