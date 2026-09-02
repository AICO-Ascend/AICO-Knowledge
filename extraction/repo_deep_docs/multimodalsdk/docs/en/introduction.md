# Introduction

> 仓 `multimodalsdk` · 路径 `docs/en/introduction.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/multimodalsdk/docs/en/introduction.md

# MultimodalSDK · Introduction 深度解读

---

## 【定位】

这篇文档是 MultimodalSDK 的总览介绍,定位为:面向 Ascend 设备加速 LLM 多模态预处理的 SDK 的能力说明与导览入口,告诉用户它能解决"在昇腾(Ascend)上跑多模态大模型推理时预处理开销大"的问题,并指引用户按场景选择后续文档。

---

## 【技术要点】

1. **核心目标**:为 Ascend 设备上的 LLM 多模态推理工作流提供高性能预处理加速接口,聚焦"加速 LLM preprocessing"。
2. **内置的预处理操作**:覆盖图片与视频的加载(loading)、解码(decoding)、尺寸调整(resizing)、裁剪(cropping)等常见算子。
3. **数据结构互转**:支持"多种开源数据结构"与"加速库数据结构"之间的相互转换,以便易用、快速迁移(quick to port)。
4. **vLLM 框架预处理插件**:作为上层入口,在使用 vLLM 做 LLM 推理时提供加速;针对具体模型已落地的有:
   - **Qwen2-VL**:在 vLLM 中加速图片与视频预处理,官方表述"与 Transformers 中的预处理相比,延迟大幅降低"。
   - **InternVL2**:在 vLLM 中加速图片与视频预处理。
5. **加速库(Acceleration library)**:提供一套高性能的 image 与 tensor 处理接口,是插件下层的算力底座。
6. **运行环境约束(硬件/OS)**:当前仅在 **Atlas 800I A2 推理服务器(Atlas A2 推理产品系列) + Ubuntu 22.04** 上受支持。

---

## 【关键机制与数据】

- **整体机制**:用户的多模态推理工作流 → 经过 MultimodalSDK 提供的高速预处理接口(加载/解码/缩放/裁剪/数据结构转换) → 喂给 LLM;在 vLLM 路径下,SDK 以"vLLM 框架预处理插件"形式嵌入,针对具体多模态模型(Qwen2-VL、InternVL2)替换原 Transformers 实现。
- **数据流层级**:由文档给出的架构分层为「vLLM framework preprocessing plugin(上层,按模型分发) → Acceleration library(下层,image/tensor 处理接口)」。
- **性能数据**:原文仅有一条量化或半量化描述——
  - 原文:"Qwen2-VL: Provides accelerated image and video preprocessing when you use the Qwen2-VL model. **Compared with preprocessing in Transformers, latency is greatly reduced.**"(未给出具体倍数/百分比)。
- **部署时间预期**:原文:"Docker quick experience (about 5 minutes)"。

> 除上述两条外,原文未给出吞吐、显存、batch size、具体延迟数字等其它量化指标;凡涉及具体数字均不臆造。

---

## 【表格解读】

原文共含 **3 个表格**,逐字还原并逐行解读如下。

### 表 1 · User Guide 导览表(逐字还原)

| Scenario | Document |
| -- | -- |
| Docker quick experience (about 5 minutes) | [Quick Start](./quickstart.md) |
| Native installation on host | [Installation Guide](./installation_guide.md) |
| Already installed, check API | [Python API Reference](./api/README.md) |

**逐行解读**:
- **第 1 行**:面向"想 5 分钟内通过 Docker 快速体验"的用户,跳转到 `./quickstart.md`;这里隐含一个体验门槛——容器化部署、约 5 分钟即可跑通。
- **第 2 行**:面向"要在物理机/裸金属上原生安装"的用户,跳转到 `./installation_guide.md`;与第一行形成"轻体验 vs 生产级安装"的二元路径。
- **第 3 行**:面向"已经装好,只想查接口"的开发者,跳转到 `./api/README.md` 的 Python API 参考;这是纯查询入口,不涉及安装步骤。

### 表 2 · 架构模块说明表(Table 1)(逐字还原)

| Module | Description |
| -- | -- |
| vLLM framework preprocessing plugin | Provides acceleration when you use vLLM for LLM inference. <ul><li>Qwen2-VL: Provides accelerated image and video preprocessing when you use the Qwen2-VL model. Compared with preprocessing in Transformers, latency is greatly reduced.</li><li>InternVL2: Provides accelerated image and video preprocessing when you use the InternVL2 model.</li></ul> |
| Acceleration library | Provides a set of high-performance image and tensor processing interfaces. |

**逐行解读**:
- **第 1 行(vLLM framework preprocessing plugin)**:该模块在用户使用 **vLLM 做 LLM 推理**时生效,作用是提供预处理加速;其内部又按多模态模型细分:
  - **Qwen2-VL 子项**:在 vLLM 下为 Qwen2-VL 提供图/视频预处理加速;原文强调"与 Transformers 的预处理相比,延迟大幅降低"。
  - **InternVL2 子项**:在 vLLM 下为 InternVL2 提供图/视频预处理加速(原文未给延迟对比描述)。
- **第 2 行(Acceleration library)**:底层加速库,提供高性能 **image 与 tensor** 处理接口,是上层 vLLM 插件依赖的算子基础。

### 表 3 · Supported Hardware and OSs(逐字还原)

| Product Series | Product Model | OS Version |
| -- | -- | -- |
| Atlas A2 inference products | Atlas 800I A2 inference server | Ubuntu 22.04 |

**逐行解读**:
- 唯一一行:仅支持 **Atlas A2 系列** 的 **Atlas 800I A2 推理服务器**,操作系统锁定 **Ubuntu 22.04**。这意味着其它 Atlas 系列或其它 OS 当前不在官方支持矩阵内,选型/部署前需要确认硬件与 OS 匹配。

---

## 【公式解读】

**原文无公式**。

(文档仅含架构图与文字描述,未出现任何 LaTeX 数学公式或伪代码算式。)

---

## 【关联】

依据文档正文与文末内部链接,可梳理出以下关联关系:

1. **文档自身的层级关系**:本文档 (`docs/en/introduction.md`) 是入口型 overview,自身不展开安装或 API 细节,而是把读者分流到三类子文档:
   - **入门体验线** → `./quickstart.md`(Docker 5 分钟快速体验,面向首次使用者)。
   - **生产部署线** → `./installation_guide.md`(主机/裸金属原生安装,面向正式环境部署)。
   - **接口查询线** → `./api/README.md`(Python API 参考,面向已部署、需要查接口的开发者)。
   - 三条线在用户路径上互斥前置条件:体验线(无需安装) → 部署线(需安装) → 接口线(已安装)。

2. **模块间的上下游关系**(基于 Table 1 与 Figure 1 文字说明):
   - **vLLM framework preprocessing plugin(上层)** ⟶ 依赖 ⟶ **Acceleration library(下层)**:插件分发到具体模型(Qwen2-VL / InternVL2),具体算子(image/tensor 处理)由加速库提供。
   - **Acceleration library** 自身不直接面向 vLLM,而是作为"算子 + 数据结构(开源 ↔ 加速库)转换"的基础底座。

3. **与外部生态的关联**:
   - 插件端以 **vLLM** 作为 LLM 推理引擎的挂载点;
   - 模型端与 **Qwen2-VL、InternVL2** 这两个开源多模态模型耦合(原文当前只点名这两个);
   - 与 **Transformers** 形成对比基线(原文仅在 Qwen2-VL 行提到 "Compared with preprocessing in Transformers")。

4. **硬件/OS 的硬约束关联**:本文档给出的支持矩阵(Atlas 800I A2 + Ubuntu 22.04)是该 SDK 在 vLLM 插件、加速库所有路径上的运行环境前置条件;若不匹配,后文 `./quickstart.md` 与 `./installation_guide.md` 的步骤可能不适用。

---

## 【使用方法】

原文本身是 overview,**未直接给出 API 调用代码、CLI 命令或配置文件示例**,但给出三种"启用/进入"路径,均通过文末表格(表 1)中的链接跳转,具体如下(完全来自原文措辞,不做扩展):

- **Docker 快速体验(约 5 分钟)**:见 [Quick Start](./quickstart.md)。
- **主机原生安装**:见 [Installation Guide](./installation_guide.md)。
- **已安装后查看 API**:见 [Python API Reference](./api/README.md)。

> 具体的接口签名、参数、调用示例、`pip`/`apt` 命令、配置文件项、环境变量等,原文未涉及;需查阅上述三份子文档获取。

## 图文联合解读

- `Multimodal-SDK-software-architecture.png`: **图文联合解读:**

图示呈现两层分层架构：上层为 Multimodal SDK 主体，含 vLLM 推理预处理插件，集成 Qwen2-VL 与 InternVL2 两大模型接口；下层为加速库，封装图像/视频解码、resize、to tensor、crop、normalize 等算子。

该结构论证了"插件-加速库"解耦的技术结论：上层面向模型提供差异化接入，下层提供可复用的硬件加速原语，二者通过统一接口衔接。

与文档论点呼应：精准对应"针对 Ascend 设备的高性能接口""通用预处理操作""支持开源与加速库数据结构转换"三项核心主张，体现从通用算子到模型插件的完整数据流。
