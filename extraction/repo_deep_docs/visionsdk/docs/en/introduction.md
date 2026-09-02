# Introduction

> 仓 `visionsdk` · 路径 `docs/en/introduction.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/visionsdk/docs/en/introduction.md

# Vision SDK 介绍文档一体化深度解读

## 【定位】

本篇文档是 Vision SDK 的总览性介绍文档，定位为"产品入门手册"——通过阐述产品背景、定义、价值、软件架构（含四大核心模块）以及支持的硬件/操作系统清单，帮助开发者快速建立对 Vision SDK 的整体认知，并为后续按 API 开发或流程编排两种方式深入学习提供导航。

---

## 【技术要点】

1. **两种开发范式**：文档明确提出 Vision SDK 提供两条开发路径——（a）**API 开发**：通过调用原生推理 API 与算子加速库构建 CV 应用；（b）**流程编排**：以模块化插件方式连接各功能模块快速构建服务，并支持自定义插件。
2. **产品价值定位**：聚焦两大核心收益——（a）通过 **NPU 加速** 显著提升算力并降低成本；（b）将 NPU 算法加速能力封装为可直接调用的能力，降低在 **Ascend 芯片** 上开发推理服务的门槛。
3. **软件架构四层模块**：原文用 Figure 1 配 Table 1 明确划分四个核心模块：`mxStream`、`mxPlugins`、`mxBase`、`mxTools`，承担从流管理、插件能力、基础算子到工具链的完整栈。
4. **mxStream 的双组件**：流管理层拆分为 `StreamManager`（构建/销毁流并提供数据收发接口）与 `StreamServer`（基于 Vision SDK 提供的 **RESTful 接口** 推理服务）。
5. **mxPlugins 四类基础插件**：`MpDataSource`（流拉取/数据加载/序列化/导出）、`MpDataProcess`（视频编解码、图像编解码、抠图、缩放、叠加、旋转）、`MpModelInfer`（模型推理）、`MpPostProc`（模型后处理）。
6. **mxBase 五大子库**：`MbCV`（基础图像处理：加减、抠图、缩放、通道拼接/分离）、`ModelInfer`（推理+后处理）、`Basic algorithm`（NMS、仿射变换、**匈牙利算法**、**卡尔曼滤波**）、`Resource Manager`（资源初始化/反初始化、异步流程控制、设备/内存管理）、`Utils`（日志/错误码/文件/字符串处理）。
8. **mxTools 五件套**：`PluginToolkit`（插件开发 API）、`SdkInfoCollector`（一键收集日志/芯片日志/资源利用率等用于问题定位）、`Uninstaller`（卸载工具）、`TestToolkit`（单插件测试工具）、`PluginInspector`（插件信息收集工具）。
9. **硬件/OS 兼容矩阵**：覆盖 **Atlas 200I/500 A2、Atlas 系列（推理产品）、Atlas A2 推理产品** 三大类；操作系统（**仅 64 位**）涵盖 Ubuntu、CentOS、EulerOS、openEuler、CTyunOS、BCLinux、KylinOS、UOS 等多发行版。

---

## 【关键机制与数据】

- **产品定位链路（原文）**：Vision SDK 属于 **MindSDK** 中面向图像/视频视觉分析的 SDK，对外暴露"基础智能分析能力 + 编程框架"两层价值。
- **工作流（原文）**：典型业务流是 `数据接入（MxDataSource 拉流/解码） → 数据处理（MpDataProcess 编解码/抠图/缩放/叠加/旋转） → 模型推理（MpModelInfer） → 后处理（MpPostProc）`，整个流程可通过 mxStream 的 StreamManager 串接运行，并通过 mxTools 中的 TestToolkit / PluginInspector 进行独立测试与诊断。
- **服务化路径（原文）**：mxStream.StreamServer 作为对外服务层，通过 **RESTful 接口** 提供视觉推理服务，无需业务侧自行实现 HTTP 服务框架。
- **性能机制（原文）**：通过将传统视频/图像处理下沉到 **NPU（Ascend 芯片）**，以"算法 + 算子加速库"的组合显著提升计算性能、降低成本。
- **算法能力（原文）**：mxBase.Basic algorithm 内置 **NMS、仿射变换、匈牙利算法、卡尔曼滤波** 四类经典 CV 算法。
- **运维能力（原文）**：SdkInfoCollector 一键收集 Vision SDK 日志、Ascend 芯片日志、资源利用率，用于故障定位。
- **数字阈值（原文）**：仅 64 位 OS 受支持；其余性能/容量类数值（吞吐、时延、内存占用等）原文未给出。

---

## 【表格解读】

### 表格 1：Modules in the architecture diagram（架构图中的模块）

| Module     | Description |
|------------|-------------|
| mxStream   | Used to manage service streams in process orchestration. <li>StreamManager: responsible for building and destroying streams. It also provides interfaces for sending data to streams and obtaining results.</li><li>StreamServer: an inference server built on Vision SDK that provides visual inference services through RESTful interfaces.</li> |
| mxPlugins  | Basic feature plugins, such as model inference plugins, model post-processing plugins, video codec plugins, and image decoding plugins. They provide the basic capabilities needed to quickly build applications through process orchestration. <li>MpDataSource: responsible for stream pulling, data loading, data serialization, and data export.</li><li>MpDataProcess: responsible for data processing, such as video encoding and decoding, image encoding and decoding, image matting, resizing, image overlay, and rotation.</li><li>MpModelInfer: responsible for model inference-related functions.</li><li>MpPostProc: responsible for model post-processing-related functions.</li> |
| mxBase     | The foundational library of Ascend chip capabilities. It includes image decoding, cropping and resizing, model inference, and operator acceleration libraries. It underpins Vision SDK and exposes some APIs for custom application development. <li>MbCV: responsible for common basic image processing functions, such as addition, subtraction, matting, resizing, channel concatenation, and channel splitting.</li><li>ModelInfer: responsible for model inference and model post-processing functions.</li><li>Basic algorithm: responsible for NMS, affine transformation, the Hungarian algorithm, and Kalman filtering.</li><li>Resource Manager: responsible for resource initialization and deinitialization, asynchronous process control, device management, memory management, and other functions.</li><li>Utils: responsible for logging, error codes, file handling, string handling, and related functions.</li> |
| mxTools    | Provides SDK-related tools. <li>PluginToolkit: APIs for plugin development.</li><li>SdkInfoCollector: a one-click information collection tool. It mainly collects Vision SDK logs, Ascend chip logs, resource utilization, and other information for troubleshooting.</li><li>Uninstaller: Vision SDK uninstallation tool.</li><li>TestToolkit: a single-plugin testing tool.</li><li>PluginInspector: a plugin information collection tool. It collects information about plugins available in the environment.</li> |

**逐行解读**：
- `mxStream`：流管理层核心，扮演"调度中枢"角色。`StreamManager` 是程序化入口，提供流的 build/destroy 与数据 I/O 接口；`StreamServer` 是服务化入口，把 Vision SDK 推理能力以 **RESTful 接口** 形式对外暴露，便于集成到外部业务系统。
- `mxPlugins`：流程编排范式下的能力积木，由四类基础插件组成——`MpDataSource` 解决"输入侧"问题（拉流/加载/序列化/导出），`MpDataProcess` 解决"预处理侧"问题（编解码、抠图、缩放、叠加、旋转），`MpModelInfer` 解决"模型侧"问题，`MpPostProc` 解决"结果侧"问题。组合起来恰好覆盖一条端到端推理管道。
- `mxBase`：Ascend 芯片能力的底层基座，向 Vision SDK 自身提供算子/推理支撑，同时对外开放部分 API 给自定义应用，使高级用户可在更底层做定制开发。其内部又分为 `MbCV`（基础图像算子）、`ModelInfer`（推理+后处理）、`Basic algorithm`（NMS、仿射变换、**匈牙利算法**、**卡尔曼滤波** 四大经典 CV 算法，多用于跟踪/匹配/后处理）、`Resource Manager`（资源/设备/内存/异步流程的统一治理）、`Utils`（日志/错误码/文件/字符串等横切能力）。
- `mxTools`：面向"开发与运维"的工具集。`PluginToolkit` 是插件开发者的 SDK；`SdkInfoCollector` 是排障利器（一键收集 Vision SDK 日志、Ascend 芯片日志、资源利用率）；`Uninstaller` 处理卸载；`TestToolkit` 允许对单个插件做单元式测试；`PluginInspector` 用于枚举当前环境可用插件。

### 表格 2：Supported product forms（支持的产品形态）

| Product Series | Product Model | OSs (64-bit Only) |
|----------------|---------------|-------------------|
| Atlas 200I/500 A2 inference products | Atlas 500 A2 edge station | EulerOS 2.11；Ubuntu 22.04；openEuler 22.03；openEuler 24.03 |
| Atlas inference products | Atlas 300I Pro inference card | Ubuntu 18.04.1；Ubuntu 18.04.5；Ubuntu 22.04；Ubuntu 24.04；CentOS 7.6；EulerOS 2.12；EulerOS 2.15；CTyunOS 23.01；openEuler 24.03；openEuler 24.03 LTS SP1；KylinOS V10 SP3 2403；KylinOS V11 |
| Atlas inference products | Atlas 300I Duo inference card | Ubuntu 18.04.1；Ubuntu 18.04.5；Ubuntu 22.04；Ubuntu 24.04；CentOS 7.6；BCLinux 21.10；EulerOS 2.12；EulerOS 2.15；CTyunOS 23.01；openEuler 24.03；openEuler 24.03 LTS SP1；KylinOS V10 SP3 2403；KylinOS V11 |
| Atlas inference products | Atlas 300V video analysis card | Ubuntu 18.04.1；Ubuntu 18.04.5；CentOS 7.6；EulerOS 2.12 |
| Atlas inference products | Atlas 300V Pro video analysis card | Ubuntu 18.04.1；Ubuntu 18.04.5；Ubuntu 24.04；UOS V20；CentOS 7.6；EulerOS 2.12；EulerOS 2.15；CTyunOS 23.01；openEuler 24.03；openEuler 24.03 LTS SP1；KylinOS V10 SP3 2403；KylinOS V11 |
| Atlas inference products | Atlas 200I SoC A1 core board | CentOS 7.6；EulerOS 2.12 |
| Atlas A2 inference products | Atlas 800I A2 inference server | Ubuntu 22.04；Ubuntu 24.04 LTS；openEuler 24.03；BCLinux 21.10 U4；KylinOS V10 SP3 2403；KylinOS V11 |

**逐行解读**：
- **Atlas 200I/500 A2 推理产品（Atlas 500 A2 边缘站）**：仅支持 4 款 OS（EulerOS 2.11、Ubuntu 22.04、openEuler 22.03、openEuler 24.03），是边缘场景的轻量化部署目标。
- **Atlas 推理产品 - Atlas 300I Pro 推理卡**：OS 兼容性最广（12 款），覆盖 Ubuntu 18.04.1/18.04.5/22.04/24.04、CentOS 7.6、EulerOS 2.12/2.15、CTyunOS 23.01、openEuler 24.03 及其 LTS SP1、KylinOS V10 SP3 2403/V11，是数据中心/服务器的主力卡型。
- **Atlas 推理产品 - Atlas 300I Duo 推理卡**：相比 300I Pro 多支持 **BCLinux 21.10**，其余 OS 列表几乎一致，适合双芯高密度推理场景。
- **Atlas 推理产品 - Atlas 300V 视频分析卡**：仅 4 款 OS（Ubuntu 18.04.1/18.04.5、CentOS 7.6、EulerOS 2.12），是专用视频分析卡，OS 选择较少。
- **Atlas 推理产品 - Atlas 300V Pro 视频分析卡**：在 300V 基础上大幅扩展 OS 矩阵，新增 Ubuntu 24.04、UOS V20、EulerOS 2.15、CTyunOS 23.01、openEuler 24.03 及 LTS SP1、KylinOS V10 SP3 2403/V11 等 11 款，是面向视频分析的主力升级卡型。
- **Atlas 推理产品 - Atlas 200I SoC A1 核心板**：仅支持 2 款 OS（CentOS 7.6、EulerOS 2.12），是嵌入式 SoC 形态，OS 选择最窄。
- **Atlas A2 推理产品 - Atlas 800I A2 推理服务器**：服务器级形态，支持 Ubuntu 22.04/24.04 LTS、openEuler 24.03、BCLinux 21.10 U4、KylinOS V10 SP3 2403/V11，主要面向数据中心部署。

**整体规律**：从 `OSs (64-bit Only)` 列可知，所有型号仅接受 64 位 OS；Atlas 推理卡/Atlas A2 服务器的兼容性最宽，边缘/嵌入式形态（500A2、200I SoC A1）的 OS 列表最窄。

> 注：原文档在两个表格处都使用了 "Table 1" 编号（"Modules in the architecture diagram" 与 "Supported product forms"），属于原文档自身的编号瑕疵，本解读已忠实保留并分别命名为表格 1 / 表格 2 以便区分。

---

## 【公式解读】

原文无公式。

---

## 【关联】

文末内部链接仅有 **1 条**：

- `./quick_start.md`（[Quick Start](./quick_start.md)）：用于介绍两种开发方式（API 开发与流程编排）的"风格与特点"，帮助读者根据实际业务场景与学习偏好选择合适路径，再进入对应章节学习。本 introduction 文档自身不展开任何代码/插件编写细节，所有具体开发步骤都通过该链接外延至 Quick Start 章节。

文档内部其他关系（架构图 Figure 1 ↔ 模块表 Table 1 ↔ 硬件/OS 表 Table 1）通过锚点 `fig17403112314618` 与 `table126112418111` 在原文档内自洽引用，外部无其他章节链接。

---

## 【使用方法】

原文未涉及具体的启用方式（命令、配置项、API 调用代码等）。仅在 Usage Guide 一节中给出**导航性指引**：

- 通过本用户指南可学到：
  - Vision SDK 的**软件架构、基本概念**、两种开发方式各自的**使用流程**；
  - 如何使用 **Vision SDK API** 进行应用开发，以及如何通过**流程编排插件**实现应用。
- **入门建议**：首次使用建议先学习每种开发方式的具体流程，再参见 [Quick Start](./quick_start.md) 了解两种开发方式的风格与特点，选择最贴合自身业务场景与学习偏好的开发路径，再进入对应章节进行学习与开发。
- **读者画像**：具备 **C/C++ 与 Python 开发技能**，并对**推理应用开发**有一定了解的开发者将更易理解本产品。

具体的安装命令、环境变量、API 签名、插件配置文件等"如何启用"细节，原文未涉及，需进入 Quick Start 及后续章节获取。
