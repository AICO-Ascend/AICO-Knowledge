# Coral Edge TPU on a Raspberry Pi with Ultralytics YOLO11 🚀

> 仓 `modelzoo-gpl` · 路径 `built-in/PyTorch/Official/cv/object_detection/Yolov8_for_PyTorch/docs/en/guides/coral-edge-tpu-on-raspberry-pi.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-gpl/built-in/PyTorch/Official/cv/object_detection/Yolov8_for_PyTorch/docs/en/guides/coral-edge-tpu-on-raspberry-pi.md

# 深度解读:Coral Edge TPU on a Raspberry Pi with Ultralytics YOLO11

---

## 【定位】

本文档解决"如何在 Raspberry Pi 单板机上,通过 Google Coral Edge TPU 协处理器配合 Ultralytics YOLO11 模型获得低功耗、高性能 ML 推理"的问题——即针对 Coral 官方文档已过时(2021–2024 未更新)、官方运行时包与新版 TensorFlow Lite runtime 不兼容的现状,提供一套基于更新版 Edge TPU runtime + 最新 TFLite runtime 的端到端安装与部署指南。

---

## 【技术要点】

1. **硬件与系统前提**:Raspberry Pi 4B(推荐 2GB 以上)或 Raspberry Pi 5(推荐);系统需为 Raspberry Pi OS Bullseye/Bookworm 64-bit(desktop 版推荐);需要 Coral USB Accelerator;需要一个**非 ARM 平台**(x86_64 Linux / Google Colab / Ultralytics Docker / Ultralytics HUB)用于导出模型。
2. **Edge TPU runtime 安装方式**:从 `https://github.com/feranick/libedgetpu/releases` 下载对应 OS 的 `.deb` 包,然后执行 `sudo dpkg -i path/to/package.deb`;安装完成后需将 Edge TPU 插入 **USB 3.0** 端口以使新 udev 规则生效。若已安装旧版,需先用 `sudo apt remove libedgetpu1-std` 或 `sudo apt remove libedgetpu1-max` 卸载。
3. **模型导出**:在非 ARM 平台上通过 Ultralytics 的 export 接口,使用 `format="edgetpu"`(Python)或 `yolo export model=path/to/model.pt format=edgetpu`(CLI)将 PyTorch `.pt` 模型导出为兼容 Edge TPU 的 TFLite 模型;导出产物保存于 `<model_name>_saved_model/` 目录,文件名为 `<model_name>_full_integer_quant_edgetpu.tflite`(原文强调:必须以 `_edgetpu.tflite` 后缀结尾,否则 ultralytics 无法识别为 Edge TPU 模型)。
4. **推理运行环境准备**:若已安装 `tensorflow`,需先 `pip uninstall tensorflow tensorflow-aarch64` 卸载,然后 `pip install -U tflite-runtime` 安装/升级 TFLite runtime。
5. **推理调用方式**:Python 通过 `YOLO("path/to/<model_name>_full_integer_quant_edgetpu.tflite")` 加载,再调用 `model.predict("path/to/source.png")`;CLI 通过 `yolo predict model=path/to/<model_name>_full_integer_quant_edgetpu.tflite source=path/to/source.png` 执行。
6. **多 TPU 选择**:通过 `device="tpu:0"`、`device="tpu:1"` 指定具体 Edge TPU 设备(默认使用第一个)。

---

## 【关键机制与数据】

- **加速原理(原文)**:Coral Edge TPU 是"a compact device that adds an Edge TPU coprocessor to your system",使其能够以"low-power, high-performance"方式执行 TensorFlow Lite 模型的 ML 推理;用于解决 Raspberry Pi 等嵌入式设备在 ONNX、OpenVINO 等格式下"inference performance on these devices is usually poor"的问题,从而"accelerate inference performance greatly"。
- **为什么需要新版指南(原文)**:Coral 官方文档"is outdated",且"the current Coral Edge TPU runtime builds do not work with the current TensorFlow Lite runtime versions anymore";此外"Google seems to have completely abandoned the Coral project, and there have not been any updates between 2021 and 2024",所以本文采用第三方维护的更新版 runtime 包(`feranick/libedgetpu`)。
- **为什么导出必须用非 ARM 平台(原文)**:"the Edge TPU compiler is not available on ARM",因此模型编译/导出阶段必须在 x86_64 机器(或 Docker/Colab/HUB)完成,只在 Raspberry Pi 上做推理。
- **数据类型流**:`.pt`(PyTorch) →(非 ARM 平台 export, `format="edgetpu"`)→ `_saved_model/<model_name>_full_integer_quant_edgetpu.tflite`(全整数量化的 TFLite) →(在 Pi 上安装 libedgetpu runtime + tflite-runtime)→ `model.predict()` 走 Edge TPU 协处理器推理。
- **性能数据**:原文未给出具体的 FPS、延迟、功耗等数字,亦无 ONNX/OpenVINO vs Edge TPU 的对比数据。
- **硬件接口细节(原文)**:"plug in your Coral Edge TPU into a USB 3.0 port on your Raspberry Pi",需在安装 runtime 之后插拔以触发新 udev 规则。

---

## 【表格解读】

原文表格为"Raspberry Pi OS ↔ 高频模式 ↔ 应下载的 .deb 包"三列对照表,完整逐字还原:

| Raspberry Pi OS | High frequency mode | Version to download                        |
| --------------- | :-----------------: | ------------------------------------------ |
| Bullseye 32bit  |         No          | `libedgetpu1-std_ ... .bullseye_armhf.deb` |
| Bullseye 64bit  |         No          | `libedgetpu1-std_ ... .bullseye_arm64.deb` |
| Bullseye 32bit  |         Yes         | `libedgetpu1-max_ ... .bullseye_armhf.deb` |
| Bullseye 64bit  |         Yes         | `libedgetpu1-max_ ... .bullseye_arm64.deb` |
| Bookworm 32bit  |         No          | `libedgetpu1-std_ ... .bookworm_armhf.deb` |
| Bookworm 64bit  |         No          | `libedgetpu1-std_ ... .bookworm_arm64.deb` |
| Bookworm 32bit  |         Yes         | `libedgetpu1-max_ ... .bookworm_armhf.deb` |
| Bookworm 64bit  |         Yes         | `libedgetpu1-max_ ... .bookworm_arm64.deb` |

逐行解读:

- 表格把 8 种安装组合分成两个维度:**操作系统版本**(Bullseye / Bookworm)×**位宽**(32bit armhf / 64bit arm64)×**是否启用高频模式**(Yes / No)。
- 包名前缀规则:`libedgetpu1-std` 对应"否"(标准频率),`libedgetpu1-max` 对应"是"(高频模式,即 max 性能变体);后缀 `.bullseye_armhf / .bullseye_arm64 / .bookworm_armhf / .bookworm_arm64` 与 OS 版本和 CPU 架构一一对应。
- 实际下载链接在表格下方给出:`https://github.com/feranick/libedgetpu/releases`,即第三方维护的 `feranick/libedgetpu` 项目(因为原文指出 Google 官方包已不更新)。
- 安装命令统一为:`sudo dpkg -i path/to/package.deb`(原文命令,与表中具体包名无关)。
- 注意:表中 `...` 是原文占位符,表示该位置在不同 release 版本下会填充具体的版本号字符串,用户需自行从 release 页面复制完整文件名。

---

## 【公式解读】

原文无公式(无 LaTeX 或伪代码形式的数学/算法表达式)。所有可执行内容均为 shell 命令与 Python/CLI 代码片段,已在【技术要点】与【使用方法】中按原文逐字列出。

---

## 【关联】

按文档正文与文末内部链接指向,该指南与以下上下游模块/特性形成依赖或对比关系:

- **`../integrations/onnx.md`** —— 在 "Boost Raspberry Pi Model Performance" 一节被作为对比对象提及,原文指出"even when using formats like ONNX or OpenVINO" 在 Raspberry Pi 上推理性能仍较差,从而引出 Edge TPU 的价值。
- **`../integrations/openvino.md`** —— 同上,与 ONNX 并列作为 Edge TPU 的对比基线(嵌入式场景下表现不佳的格式代表)。
- **`../quickstart.md`** —— 在 "Installation Walkthrough" 开头要求先按 quickstart 安装 `ultralytics` 及其依赖,"To get ultralytics installed, visit the quickstart guide to get setup before continuing here."
- **`docker-quickstart.md`** —— 在 "Export your model" 一节被列为推荐的非 ARM 导出环境之一("using the official Ultralytics Docker container")。
- **`../hub/quickstart.md`** —— 同上,作为非 ARM 导出环境的另一种选择("or using Ultralytics HUB")。
- **`../modes/export.md`** —— 在 "Export your model" 一节被引用,用于说明 `format="edgetpu"` 这一参数所属的功能模式及可用参数("See the Export Mode for the available arguments")。
- **`../modes/predict.md`** —— 在 "Running the model" 一节末尾被引用,用于获取完整预测模式参数说明("Find comprehensive information on the Predict page for full prediction mode details")。

整体数据流上下游关系可总结为:`PyTorch 模型(.pt)` →(在非 ARM 环境通过 Ultralytics export,见 `modes/export.md`)→ `*_edtegeral_quant_edgetpu.tflite`(本文导出目标)→ 在 Pi 上由 `libedgetpu` runtime + `tflite-runtime` 加载,通过 `modes/predict.md` 接口调用 Edge TPU 推理;ONNX(`integrations/onnx.md`)与 OpenVINO(`integrations/openvino.md`)是被本文"扬弃"的替代路径,quickstart / Docker / HUB 三条则是导出阶段的前置依赖。

---

## 【使用方法】

以下命令均直接来自原文,逐字保留:

### A. 安装 Edge TPU runtime(Raspberry Pi 上执行)

1. 按【表格解读】中表格选择对应 `.deb` 包,从 `https://github.com/feranick/libedgetpu/releases` 下载。
2. 安装:
   ```bash
   sudo dpkg -i path/to/package.deb
   ```
3. 将 Coral Edge TPU 插入 Raspberry Pi 的 USB 3.0 端口。
4. 如已安装旧版,先卸载(原文):
   ```bash
   # 标准版
   sudo apt remove libedgetpu1-std
   # 高频版
   sudo apt remove libedgetpu1-max
   ```

### B. 导出模型为 Edge TPU 兼容格式(在非 ARM 平台执行)

Python:
```python
from ultralytics import YOLO

model = YOLO("path/to/model.pt")           # 加载官方或自定义模型
model.export(format="edgetpu")              # 导出
```

CLI:
```bash
yolo export model=path/to/model.pt format=edgetpu
```

导出结果路径:`<model_name>_saved_model/<model_name>_full_integer_quant_edgetpu.tflite`(原文强调必须以 `_edgetpu.tflite` 后缀结尾)。

### C. 在 Raspberry Pi 上准备推理 runtime

```bash
pip uninstall tensorflow tensorflow-aarch64   # 原文:如已安装则先卸载
pip install -U tflite-runtime                  # 原文:安装/升级 TFLite runtime
```

### D. 运行推理

Python:
```python
from ultralytics import YOLO

model = YOLO("path/to/<model_name>_full_integer_quant_edgetpu.tflite")
model.predict("path/to/source.png")
```

CLI:
```bash
yolo predict model=path/to/<model_name>_full_integer_quant_edgetpu.tflite source=path/to/source.png
```

### E. 多 TPU 选择(原文 note 章节)

```python
model.predict("path/to/source.png")                     # 默认使用第一个 TPU
model.predict("path/to/source.png", device="tpu:0")     # 显式指定第一个 TPU
model.predict("path/to/source.png", device="tpu:1")     # 显式指定第二个 TPU
```

### F. 前置条件

- 必须先按 `../quickstart.md` 安装好 `ultralytics` 及其依赖(原文:"This guide assumes that you already have a working Raspberry Pi OS install and have installed ultralytics and all dependencies")。
- 导出步骤必须在非 ARM 平台执行(原文:"the Edge TPU compiler is not available on ARM")。

原文未涉及的具体项包括:Edge TPU 推理的 FPS / 延迟基准数据、能耗数字、`format="edgetpu"` 之外的其它可用 export 参数细节(指向 `modes/export.md` 查阅)、`model.predict()` 的完整参数列表(指向 `modes/predict.md` 查阅)。
