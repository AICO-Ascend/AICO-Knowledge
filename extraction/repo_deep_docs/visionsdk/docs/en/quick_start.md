# Quick Start

> 仓 `visionsdk` · 路径 `docs/en/quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/visionsdk/docs/en/quick_start.md

# Vision SDK Quick Start 文档深度解读

## 【定位】

这篇文档是一份面向 **Vision SDK C++ API** 的入门实践指南，核心目标是：以 **YoloV3（TensorFlow 框架）** 目标检测模型为示例，演示如何在 **Atlas inference 系列 / Atlas 200I/500 A2** 推理产品上完成"图像预处理 → 模型推理 → 后处理 → 可视化"的端到端应用开发闭环，作为开发者快速跑通 SDK 的最小完整工程样例。

---

## 【技术要点】

1. **目标硬件与产品线**：仅适用于 **Atlas inference 系列** 和 **Atlas 200I/500 A2 推理产品**（样例基于 Atlas inference 系列）。

2. **完整四步流水线**：工程结构 `YoloV3Infer`（含 `model/`、`main.cpp`、`CMakeLists.txt`、`run.sh`、`test.jpg`），代码按 **初始化 → 预处理 → 推理 → 后处理 + OpenCV 可视化** 四段组织。

3. **关键软件依赖（强约束版本）**：
   - **CANN development kit**：`8.1.RC1`
   - **npu-driver**：`Ascend HDK 25.0.RC1`
   - **npu-firmware**：`Ascend HDK 25.0.RC1`
   - **numpy**：`1.25.2`（安装命令：`pip3 install numpy==1.25.2`）

4. **关键图像处理参数**：
   - 图像缩放尺寸：`YOLOV3_RESIZE = 416`（即 416×416）
   - 解码输出格式：`ImageFormat::YUV_SP_420`
   - 缩放插值方式：`MxBase::Interpolation::HUAWEI_HIGH_ORDER_FILTER`
   - 后处理缩放类型：`MxBase::RESIZER_STRETCHING`
   - 推理设备 ID：`deviceId = 0`

5. **后处理模块**：`MxBase::Yolov3PostProcess`，通过 `postConfig` map 注入 `postProcessConfigPath` 与 `labelPath`，完成对模型输出 `yoloV3Outputs` 的目标检测框 + 类别解析，再交由 **OpenCV** 在原图上绘制文本与矩形框。

6. **脚本前置操作**：`run.sh` 在执行前需用 `dos2unix run.sh` 进行格式转换；同时 `.om` 模型由 `run.sh` 自动生成，并存放于 `./model` 目录下。

---

## 【关键机制与数据】

**原文（工作原理/数据流）：**

> 「Decode the image by path → Perform resizing → Encode the resized image and output it to the specified path → Convert the Image object to a Tensor → Set the device ID that hosts the Tensor → Construct the input batch Tensor for the Infer interface → Run model inference」

数据流可概括为：

```
test.jpg
   │  (Decode, YUV_SP_420)
   ▼
MxBase::Image decodedImage
   │  (Resize → 416×416, HUAWEI_HIGH_ORDER_FILTER)
   ▼
MxBase::Image resizeImage  ──►  ./resized_yolov3_416.jpg  (中间可视化产物)
   │  (ConvertToTensor + ToDevice(deviceId=0))
   ▼
MxBase::Tensor tensorImg
   │  (yoloV3.Infer)
   ▼
std::vector<MxBase::Tensor> yoloV3Outputs
   │  (Yolov3PostProcess.Process)
   ▼
vector<vector<MxBase::ObjectInfo>> objectInfos
   │  (cv::putText + cv::rectangle)
   ▼
带检测框与类别标签的可视化结果图
```

性能/吞吐类数字（如 FPS、时延）在原文中均未给出，**原文未涉及**性能基准数据。

---

## 【表格解读】

**Table 1  Software dependencies for the environment**（逐字还原）：

| Software Dependency | Recommended Version | Download Link |
|---|---|---|
| OS | See [Supported Hardware and OSs](introduction.md#supported-hardware-and-oss) | - |
| System dependency | - | [Ubuntu](installation_guide.md#ubuntu) or [CentOS](installation_guide.md#centos) |
| CANN development kit package | 8.1.RC1 | CANN [download link](https://www.hiascend.com/developer/download/commercial/result?module=cann) |
| npu-driver driver package | Ascend HDK 25.0.RC1 | Click the [download link](https://www.hiascend.com/developer/download/commercial/result?module=cann), configure the package in the "Edit resource selection" area for the supporting resources on the left, filter the matching software packages, and obtain the required packages after you confirm the version information. For the corresponding guidance, see the [driver and firmware installation and upgrade guide](https://support.huawei.com/enterprise/en/ascend-computing/ascend-hdk-pid-252764743) for each hardware product. |
| npu-firmware firmware package | Ascend HDK 25.0.RC1 | - |
| numpy | 1.25.2 | `pip3 install numpy==1.25.2` |

**逐行解读：**

- **OS**：不固定具体版本，需跳转至 `introduction.md#supported-hardware-and-oss` 章节查看硬件/OS 支持矩阵。
- **System dependency**：指向 `installation_guide.md#ubuntu` 与 `installation_guide.md#centos` 两套系统依赖说明，代表 SDK 至少覆盖 Ubuntu 与 CentOS 两条发行版路线。
- **CANN development kit package**：版本严格锁定为 **8.1.RC1**；下载需从 Ascend 官方商业版开发者中心获取。
- **npu-driver driver package**：版本为 **Ascend HDK 25.0.RC1**；强调需要在"Edit resource selection"区按硬件筛选对应驱动包，并提供 driver & firmware 安装升级指南外链。
- **npu-firmware firmware package**：与 driver 同版本 **Ascend HDK 25.0.RC1**，表示 driver/firmware 需配套同套 HDK 版本。
- **numpy**：版本 **1.25.2**，提供明确的 `pip3 install numpy==1.25.2` 命令；该版本应与 CANN 8.1.RC1 + Atlas 推理环境存在兼容性绑定。

---

## 【公式解读】

原文无公式。

---

## 【关联】

文档通过内部链接与正文交叉引用形成如下依赖图谱：

```
quick_start.md (本文)
   │
   ├──► introduction.md#supported-hardware-and-oss
   │      └─ 软件依赖表第 1 行（OS 选型依据）
   │
   ├──► installation_guide.md#ubuntu
   │      └─ 软件依赖表第 2 行（Ubuntu 系统依赖说明）
   │
   ├──► installation_guide.md#centos
   │      └─ 软件依赖表第 2 行（CentOS 系统依赖说明）
   │
   ├──► faq.md#system-commands-yum-and-cmake-become-unavailable
   │      └─ 文中 NOTE：openEuler 上 cmake 缺失时的解决方法
   │
   ├──► appendix.md#installing-python-dependencies
   │      └─ Python 依赖（numpy）的标准安装流程补充
   │
   └──► YoloV3Infer.zip 外部资源包
          └─ 主流程样例源码（含 README.md、model/、run.sh 等）
```

模块关系上的隐含串联：
- 文档中使用的 **`MxBase` 命名空间**（`MxBase::MxInit`、`MxBase::ImageProcessor`、`MxBase::Model`、`MxBase::Yolov3PostProcess`、`MxBase::Tensor`、`MxBase::ObjectInfo`）表明 Vision SDK 的 C++ 接口统一收敛在 `MxBase` 模块之下。
- 后处理 `YoloV3PostProcess` 与 `yolov3_tf_bs1_fp16.cfg` 配置、`yolov3.names` 标签文件三者需协同加载，是 SDK 内"模型 + 配置 + 标签"三元组的标准用法。
- 样例还依赖 **OpenCV**（`cv::putText`、`cv::rectangle`），但 OpenCV 不在 Table 1 内，属于开发机既有依赖。

---

## 【使用方法】

**原文给出的启用/操作步骤：**

1. **安装前置**：先完成 Vision SDK 安装与部署（指向 `installation_guide.md`）。
2. **下载样例**：
   ```bash
   # 从 https://mindx.sdk-6e12.obs.cn-north-4.myhuaweicloud.com/mindxsdk-referenceapps%20/mxVision/YoloV3Infer/YoloV3Infer.zip 下载
   unzip YoloV3Infer.zip
   cd YoloV3Infer
   ```
3. **脚本格式化**（运行前必须）：
   ```bash
   dos2unix run.sh
   ```
4. **模型准备**：参照解压后目录中 `README.md` 的 "Prepare the Model" 章节，准备 `yolov3_tf.pb`；执行 `run.sh` 会自动生成 `.om` 模型（路径：`./model/yolov3_tf_bs1_fp16.om`）。
5. **测试图像**：自备图片，重命名为 `test.jpg`。
6. **执行运行**：通过 `run.sh` 启动样例。

**核心配置项（C++ 代码侧）：**

| 配置项 | 取值/路径 | 作用 |
|---|---|---|
| `v2Param.deviceId` | `0` | 指定运行设备 |
| `v2Param.modelPath` | `./model/yolov3_tf_bs1_fp16.om` | OM 模型路径 |
| `v2Param.configPath` | `./model/yolov3_tf_bs1_fp16.cfg` | 后处理配置 |
| `v2Param.labelPath` | `./model/yolov3.names` | 后处理标签 |
| `YOLOV3_RESIZE` | `416` | 缩放目标尺寸 |
| 解码格式 | `ImageFormat::YUV_SP_420` | 图像解码输出格式 |
| 插值方式 | `HUAWEI_HIGH_ORDER_FILTER` | 缩放插值算法 |
| 缩放类型 | `MxBase::RESIZER_STRETCHING` | 后处理缩放类型 |

**openEuler 特殊说明**：原文 NOTE 提到，若 `cmake` 在 openEuler 上不可用，需参见 `faq.md#system-commands-yum-and-cmake-become-unavailable` 解决。

## 图文联合解读

- `test-jpg.jpg`: ## 图文联合解读

**1) 图里画了什么：**
图中实际显示的是一只**白色贵宾犬（poodle）的侧面肖像照**，黑色背景，犬只毛发蓬松、面部朝左，与"流程图"或"技术示意图"完全无关。

**2) 与文档论点的关系——存在严重错配：**
文档 Figure 1 明确标注为 "Inference process flowchart of the object detection model"，应展示 YoloV3 模型的推理流水线（输入→预处理→模型推理→后处理→输出框），但配图却是一张犬类照片。**这是一处明显的图文错配（image-doc mismatch）**，可能是文档仓库中图片占位错误、引用路径错误或图片上传失误。

**3) 结论：**
该配图**无法论证**任何与 Vision SDK C++ 对象检测开发、YoloV3 推理流程或 Atlas 推理产品相关技术内容；建议修复 `figures/7-1-...png` 文件，重新上传真正的推理流程图，以匹配 Quick Start 的技术叙事。
- `result-jpg-file.jpg`: **图文联合解读：**

图为一白色贵宾犬侧像，黑色背景，绿色矩形检测框完整包围狗身，左上角标注类别"dog"——这是目标检测模型的推理输出结果图，而非文档文字所述的"推理流程图"，存在图题错配。

该图直观论证了YoloV3模型经Vision SDK C++接口在Atlas推理产品上的可部署性：成功输出精准边界框与类别标签，模型端到端推理有效。

与文档论点关系：作为Quick Start示例的最终运行结果佐证，呼应"如何开发目标检测应用"的可执行闭环，使抽象的推理流程具象化为可视化输出。
- `test-jpg-0.jpg`: ## 图文联合解读

**⚠️ 图文不符说明**：文档上下文标注此图为"Figure 1 物体检测模型推理流程图"，但实际配图并非流程图，而是一张**白色贵宾犬（poodle）的侧身特写照片**（纯黑背景）。这是该 Quick Start 示例（YoloV3 目标检测）的**典型输入样本图像**，常用于演示端到端检测效果。

### 1) 图里画了什么
非流程图，而是一张高对比度样本照片：黑色背景中央偏右是一只白色卷毛贵宾犬侧脸（轮廓清晰、毛发蓬松、面部朝左），无任何文字、箭头或结构标注。

### 2) 论证了什么技术结论
该图本身**未呈现推理流程结构**，无法作为流程图的论据。若按样本用途解读，它体现的是输入图像——Vision SDK C++ 接口可对自然图像（宠物）完成检测，输出应包含狗的类别、置信度与边界框。

### 3) 与文档论点的关系
**图文失配**：文档声称此图为推理流程图（应展示预处理→模型推理→后处理→输出检测结果的链路），实际图像为输入样例。这削弱了"图证流程论点"的支撑作用，建议替换为真实的流程框图，以匹配"API Development (C++) Quick Start"的讲解意图。
- `result-png-file.png`: **图文解读：**

1. **图的内容**：黑色背景下的白色标准贵宾犬侧写照，左上角标注 "Standard Poodle: 0.99"，即分类标签与置信度。

2. **技术结论**：这是图像**分类**（Classification）模型的推理输出示例，证明模型以 0.99 的高置信度正确识别了犬种类别，属于典型的"输入图→模型→Top-1 类别与置信度"单标签分类流程展示。

3. **与文档论点的关系**：**图文不符**。文档 Figure 1 文字说明为「目标检测模型推理流程图」（基于 YoloV3），应呈现如"图片→预处理→模型推理→后处理→检测框"的框图与数据流向，而非分类输出结果图。当前图片无法论证目标检测的推理流水线，建议替换为文档原引用的 `7-1-inference-process-flowchart-of-the-object-detection-model.png`。
- `typical-sample-image.jpg`: # 图文联合解读

**图示内容**：图中并非文档所述的"推理流程图"，而是一张白色背景下比格犬（Beagle）的实物照片——属于目标检测常见的测试/示例输入图，并非技术流程图。

**技术结论**：该图本身无法论证任何技术结论（无结构、数据流或关键标注）。它仅作为 YoloV3 目标检测模型的 **样例输入图像**使用，即被检测的目标物体（狗）样本。

**与文档关系**：与文档"图1 推理流程图"标题严重不符，存在**图片错配问题**。正确配图应为推理流程图（涵盖预处理→模型推理→后处理→结果输出等环节），而此图仅可作示例输入素材展示。
