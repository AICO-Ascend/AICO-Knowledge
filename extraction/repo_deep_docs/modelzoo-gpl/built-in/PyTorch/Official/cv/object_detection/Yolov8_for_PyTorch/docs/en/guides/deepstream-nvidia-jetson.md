# Ultralytics YOLO11 on NVIDIA Jetson using DeepStream SDK and TensorRT

> 仓 `modelzoo-gpl` · 路径 `built-in/PyTorch/Official/cv/object_detection/Yolov8_for_PyTorch/docs/en/guides/deepstream-nvidia-jetson.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-gpl/built-in/PyTorch/Official/cv/object_detection/Yolov8_for_PyTorch/docs/en/guides/deepstream-nvidia-jetson.md

# Ultralytics YOLO11 on NVIDIA Jetson using DeepStream SDK and TensorRT — 深度解读

> ⚠️ **原文状态说明**：原文在 "### Ru" 处截断（INT8 Calibration 章节末尾的 "Run" 标题之后内容缺失），以下解读基于现有可见原文，未补全缺失段落。

---

## 【定位】

这篇文档是一份**部署实践指南**，详细说明如何将 Ultralytics YOLO11 目标检测模型部署到 **NVIDIA Jetson 系列边缘设备**上，借助 **NVIDIA DeepStream SDK + TensorRT** 构建 GStreamer 流式分析管线，以最大化 Jetson 平台上的推理性能。

---

## 【技术要点】

1. **测试平台（原文）**：
   - **Seeed Studio reComputer J4012**：基于 **NVIDIA Jetson Orin NX 16GB**，运行 **JetPack JP5.1.3**
   - **Seeed Studio reComputer J1020 v2**：基于 **NVIDIA Jetson Nano 4GB**，运行 **JetPack JP4.6.4**
   - 预期兼容整个 NVIDIA Jetson 硬件家族（最新与遗留版本）

2. **DeepStream 与 JetPack 版本对应（原文）**：
   - JetPack 4.6.4 → 安装 **DeepStream 6.0.1**
   - JetPack 5.1.3 → 安装 **DeepStream 6.3**

3. **依赖与仓库（原文）**：
   - Python 包：`pip install cmake`、`pip install onnxsim`
   - 第三方仓库：`https://github.com/marcoslucianops/DeepStream-Yolo`（提供 NVIDIA DeepStream 对 YOLO 模型的原生支持）
   - 演示模型：`yolov8s.pt`（v8.2.0 release）

4. **ONNX 导出关键参数（原文 export_yoloV8.py 参数）**：
   - 默认 **opset = 16**；DeepStream 6.0.1 需使用 **opset 12 或更低**（`--opset 12`）
   - 推理尺寸默认 **640**；可由 `-s SIZE` 或 `-s HEIGHT WIDTH` 调整，示例 `-s 1280` 或 `-s 1280 1280`
   - `--simplify`（DeepStream ≥ 6.0 适用）
   - `--dynamic`（DeepStream ≥ 6.1 适用，启用动态 batch）
   - `--batch 4`（静态 batch 示例 = 4）

5. **CUDA 版本变量（原文）**：
   - JetPack 4.6.4 → `export CUDA_VER=10.2`
   - JetPack 5.1.3 → `export CUDA_VER=11.4`
   - 编译命令：`make -C nvdsinfer_custom_impl_Yolo clean && make -C nvdsinfer_custom_impl_Yolo`

6. **精度模式切换（原文）**：
   - **FP32**：`model-engine-file=model_b1_gpu0_fp32.engine`，`network-mode=0`
   - **FP16**：`model-engine-file=model_b1_gpu0_fp16.engine`，`network-mode=2`
   - **INT8**：`model-engine-file=model_b1_gpu0_int8.engine`，`int8-calib-file=calib.table`，`network-mode=1`

7. **INT8 校准参数（原文）**：
   - 图像数量：NVIDIA 推荐 **≥ 500 张**，示例使用 **1000 张**（通过 `head -1000` 可调，如 2000 张即 `head -2000`）
   - 环境变量：`INT8_CALIB_IMG_PATH=calibration.txt`，`INT8_CALIB_BATCH_SIZE=1`
   - `INT8_CALIB_BATCH_SIZE` 越大 → 精度更高、校准更快，但占用更多 GPU 显存
   - 数据来源：**COCO val2017**（`http://images.cocodataset.org/zips/val2017.zip`）

---

## 【关键机制与数据】

### 工作流（原文描述的 Pipeline）

```
.pt 模型
  ↓ utils/export_yoloV8.py（导出 ONNX，可选 simplify / dynamic / batch）
.onnx 模型
  ↓ nvdsinfer_custom_impl_Yolo 编译 + CUDA_VER 环境变量
  ↓ config_infer_primary_yoloV8.txt（指定 onnx-file、num-detected-classes=80、network-mode）
  ↓ deepstream_app_config.txt（指定 [primary-gie] config-file、[source0] uri）
TensorRT Engine File（首次生成耗时较长）
  ↓ deepstream-app -c deepstream_app_config.txt
GStreamer 多路流推理管线（视频解码 → 推理 → 后处理 → 渲染/编码）
```

### 关键运行说明（原文）

- **原文**："It will take a long time to generate the TensorRT engine file before starting the inference. So please be patient." —— 首次运行需编译 TensorRT engine，需耐心等待。
- **原文**："NVIDIA recommends at least 500 images to get a good accuracy. On this example, 1000 images are chosen to get better accuracy (more images = more accuracy)." —— 校准图越多精度越好，但耗时更长。
- **原文**："Higher INT8_CALIB_BATCH_SIZE values will result in more accuracy and faster calibration speed. Set it according to you GPU memory." —— 批大小权衡精度/速度/显存。

### 演示视频源（原文）

- 默认视频：`uri=file:///opt/nvidia/deepstream/deepstream/samples/streams/sample_1080p_h264.mp4`

### DeepStream SDK 定位（原文）

> "NVIDIA's DeepStream SDK is a complete streaming analytics toolkit based on GStreamer for AI-based multi-sensor processing, video, audio, and image understanding." —— 基于 GStreamer 的完整流式分析工具包，专为 IVA（智能视频分析）应用而设计。

---

## 【表格解读】

**原文无表格**。原文中所有配置均以代码块（bash 片段）形式呈现，包括 `config_infer_primary_yoloV8.txt`、`deepstream_app_config.txt`、`make` 命令与 shell 循环等，未出现 markdown 表格结构。

为便于对照，下表为**笔者根据原文代码块汇总**的"配置项映射表"，并非原文表格：

| 配置项 / 文件 | 关键参数 | 取值 / 示例 | 含义（原文语境） |
|---|---|---|---|
| `export_yoloV8.py` | `--opset` | `12`（DS 6.0.1 必需）/ 默认 `16` | ONNX 算子集版本 |
| `export_yoloV8.py` | `-s / --size` | 默认 `640`；示例 `1280` 或 `1280 1280` | 推理输入尺寸（H 或 H W） |
| `export_yoloV8.py` | `--simplify` | DS ≥ 6.0 适用 | 简化 ONNX 图 |
| `export_yoloV8.py` | `--dynamic` | DS ≥ 6.1 适用 | 启用动态 batch 维度 |
| `export_yoloV8.py` | `--batch` | `4`（示例） | 静态 batch 大小 |
| 环境变量 | `CUDA_VER` | `10.2`（JP4.6.4）/ `11.4`（JP5.1.3） | 编译时 CUDA 版本 |
| `config_infer_primary_yoloV8.txt` | `onnx-file` | `yolov8s.onnx` | 推理 ONNX 模型路径 |
| `config_infer_primary_yoloV8.txt` | `num-detected-classes` | `80` | 类别数（COCO） |
| `config_infer_primary_yoloV8.txt` | `model-engine-file` | `..._fp32.engine` / `..._fp16.engine` / `..._int8.engine` | TensorRT engine 文件 |
| `config_infer_primary_yoloV8.txt` | `network-mode` | `0`=FP32 / `2`=FP16 / `1`=INT8 | 推理精度模式 |
| `config_infer_primary_yoloV8.txt` | `int8-calib-file` | `calib.table`（INT8 取消注释） | INT8 校准表 |
| `deepstream_app_config` | `[primary-gie]` → `config-file` | `config_infer_primary_yoloV8.txt` | 主检测器配置入口 |
| `deepstream_app_config` | `[source0]` → `uri` | `file:///opt/nvidia/.../sample_1080p_h264.mp4` | 视频源 |
| 校准环境 | `OPENCV` | `1` | 编译时启用 OpenCV（校准步骤需要） |
| 校准环境 | `INT8_CALIB_IMG_PATH` | `calibration.txt` | 校准图像清单 |
| 校准环境 | `INT8_CALIB_BATCH_SIZE` | `1`（示例） | 校准批大小 |

---

## 【公式解读】

**原文无公式**。文档未包含任何 LaTeX 数学公式或伪代码公式段；所有数值均为命令参数或配置键值。

---

## 【关联】

| 关联项 | 关系 | 出处 |
|---|---|---|
| **[nvidia-jetson.md](nvidia-jetson.md)** | **前置依赖**：原文 Prerequisites 步骤 1 显式要求先阅读此 Quick Start Guide，完成 Jetson 设备 + Ultralytics YOLO11 的基础环境搭建后，才能进行本指南的 DeepStream 部署 | Prerequisites 步骤 1 |
| **[nvidia-jetson.md](nvidia-jetson.md)**（元数据引用） | 文档标题/Front matter 中再次引用，作为同主题姊妹文档 | 文档头引用 |
| **[../modes/export.md](../modes/export.md)** | 在步骤 3 注记中提及"也可使用 custom trained YOLO11 model"，链接指向 Ultralytics 训练与导出文档，说明本指南的输入模型不限于官方 yolov8s.pt | 步骤 3 Note |
| **marcoslucianops/DeepStream-Yolo** | 第三方依赖仓库，提供 DeepStream 对 YOLO 模型的自定义推理实现层 `nvdsinfer_custom_impl_Yolo` | 步骤 2、6 |
| **TensorRT** | 推理引擎生成器（`model-engine-file`） | 全文 |
| **GStreamer** | DeepStream 底层流处理框架 | "What is NVIDIA DeepStream" 节 |
| **COCO val2017** | INT8 校准数据来源 | INT8 Calibration 步骤 3 |
| **JetPack SDK（JP4.6.4 / JP5.1.3）** | 系统级镜像，决定 CUDA 与 DeepStream 版本配套 | 全文 |

**上下游关系梳理**：

```
[Ultralytics 训练/导出 docs/modes/export.md]
        ↓ (产出 .pt 或 .onnx)
[Quick Start: nvidia-jetson.md — Jetson 基础环境]
        ↓ (本指南) — DeepStream SDK 安装 + ONNX 转换 + 配置 + 推理
[YOLO11 + DeepStream + TensorRT on Jetson 推理管线]
```

---

## 【使用方法】

### 一、基础部署流水线（原文完整列出）

```bash
# 1. 安装 Python 依赖
pip install cmake
pip install onnxsim

# 2. 克隆第三方仓库
git clone https://github.com/marcoslucianops/DeepStream-Yolo
cd DeepStream-Yolo

# 3. 下载模型（示例 yolov8s.pt）
wget https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8s.pt

# 4. 导出 ONNX
python3 utils/export_yoloV8.py -w yolov8s.pt

# 5. 根据 JetPack 设置 CUDA 版本
#    JP4.6.4: export CUDA_VER=10.2
#    JP5.1.3: export CUDA_VER=11.4

# 6. 编译自定义推理实现
make -C nvdsinfer_custom_impl_Yolo clean && make -C nvdsinfer_custom_impl_Yolo

# 7. 编辑 config_infer_primary_yoloV8.txt（设 onnx-file、num-detected-classes=80）
# 8. 编辑 deepstream_app_config.txt（设 [primary-gie] config-file、[source0] uri）
# 9. 运行推理
deepstream-app -c deepstream_app_config.txt
```

### 二、FP16 精度启用（原文 Tip）

在 `config_infer_primary_yoloV8.txt` 中设置：
```ini
model-engine-file=model_b1_gpu0_fp16.engine
network-mode=2
```

### 三、INT8 精度启用（原文完整步骤）

```bash
# 1. 启用 OpenCV 重新编译
export OPENCV=1
make -C nvdsinfer_custom_impl_Yolo clean && make -C nvdsinfer_custom_impl_Yolo

# 2. 下载 COCO val2017 并放入 DeepStream-Yolo 目录

# 3. 抽取 1000 张校准图（NVIDIA 建议 ≥500）
mkdir calibration
for jpg in $(ls -1 val2017/*.jpg | sort -R | head -1000); do \
    cp ${jpg} calibration/; \
done

# 4. 生成校准清单
realpath calibration/*jpg > calibration.txt

# 5. 设置环境变量
export INT8_CALIB_IMG_PATH=calibration.txt
export INT8_CALIB_BATCH_SIZE=1

# 6. 修改 config_infer_primary_yoloV8.txt：
#    model-engine-file=model_b1_gpu0_int8.engine
#    int8-calib-file=calib.table      # 取消注释
#    network-mode=1
```

### 四、ONNX 导出可选参数（原文 "Pass the below arguments" Note）

| 参数 | 取值示例 | 适用条件 | 用途 |
|---|---|---|---|
| `--opset` | `12` | DeepStream 6.0.1 | 降算子集版本以兼容旧 DS |
| `-s` / `--size` | `1280` / `1280 1280` | 任意 | 改推理分辨率（默认 640） |
| `--simplify` | — | DS ≥ 6.0 | 简化 ONNX 图 |
| `--dynamic` | — | DS ≥ 6.1 | 动态 batch |
| `--batch` | `4` | 任意 | 静态 batch |

### 五、原文未涉及

- **Docker 部署方式**：原文未涉及。
- **多模型/多路流配置详细示例**：原文仅提到 "How to Run Multiple Streams" 的 YouTube 视频，未给出配置细节。
- **具体 FPS / 推理时延 benchmark 数字**：原文未提供实测性能数据表。
- **模型量化精度对比表**：原文未提供。
- **结束部分被截断**：INT8 Calibration 节末尾 "### Ru" 之后内容缺失，`deepstream-app` 在 INT8 模式下的运行命令未在原文中给出。
