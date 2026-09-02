# Compatibility Notes

> 仓 `visionsdk` · 路径 `docs/en/release_notes.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/visionsdk/docs/en/release_notes.md

# visionsdk `docs/en/release_notes.md` 深度解读

## 【定位】

本文件是 Vision SDK（隶属 MindSDK 产品线、面向图片与视频视觉分析的 SDK）**26.0.0 版本（Release candidate）的发布说明/兼容性说明文档**，核心解决"该 RC 版本与哪些 Ascend HDK / CANN 版本兼容、可从哪些旧版本升级、是否引入新特性或破坏性变更"的问题。

---

## 【技术要点】

1. **版本身份**：本次发布为 MindSDK 26.0.0，**Version Type = Release candidate**，Maintenance 维护周期为 **3 个月**；并依赖 **Ascend HDK 26.0.RC1** 与 **CANN 9.0.0**（两个上游组件均为 RC/正式大版本）。
2. **版本兼容策略（升级路径）**：Vision SDK 本次"无兼容性问题"；升级路径起点为 **MindSDK 7.3.0**，覆盖 6.0.RC3、6.0.0、7.0.RC1、7.1.RC1、7.2.RC1、7.3.0 六大基线（每个基线均含 `.x` 补丁号），向下跨多个大版本兼容。
3. **依赖版本范围**：CANN 兼容矩阵覆盖 8.1.RC1、8.2.RC1、8.3.RC1、8.5.0；Ascend HDK 覆盖 25.0.RC1、25.2.0、25.3.RC1、25.5.0、26.0.RC1 ——说明 SDK 在 CANN 与 HDK 两条轴上同时允许多版本共存。
4. **变更粒度（本次为空更）**：New Features / Service Interface Changes / Key Feature Changes / Resolved Issues / Known Issues / Upgrade Impact / Vulnerability Fix List **全部为 "None" 或 "No … involved"**，即这是一个**功能性冻结、只做兼容性同步的 RC 版本**。
5. **硬件覆盖**：支持的 Product Models 列举 9 类 Atlas 产品（300I/3000、500 A2、300I Pro、300I Duo、300V、300V Pro、200I A1、800I A2），横跨推理卡、视频分析卡、Smart Station 与核心板。
6. **配套文档**：随包提供 *Vision SDK 26.0.0 User Guide*，提供 API 开发与流程编排两种使用方式的指引，并包含 API 参考。

---

## 【关键机制与数据】

- **原文：版本兼容定义**——"Software version compatibility means that when the product software version is upgraded, other related software does not need to be upgraded or patched at the same time, and existing functions remain supported."（即升级 MindSDK 时，上下游软件 CANN / HDK 无需同步升级或打补丁，已有功能保持可用）
- **原文：版本类型**——"Product Version: 26.0.0 / Version Type: Release candidate / Maintenance: 3 months"
- **原文：依赖基线**——"Ascend HDK: 26.0.RC1"、"CANN: 9.0.0"
- **原文：变更状态**——"Vision SDK: This release has no compatibility issues."、"No new features"、"No interface changes are involved."、"No key feature changes are involved."
- **原文：安检**——"Virus scan passed."
- **数据流/性能数据**：原文未提供工作原理描述、调用链路、性能指标或基准数据，本节仅做声明性陈述记录。

---

## 【表格解读】

### 表格 1：Product Version Information（产品版本信息）

| Item | Details |
| --- | --- |
| Product | MindSDK |
| Product Version | 26.0.0 |
| Version Type | Release candidate |
| Maintenance | 3 months |

**逐行解读**：标识本次发布所属的产品族（MindSDK）、大版本号（26.0.0）、发布阶段（RC 候选版本而非 GA）、官方维护窗口长度（3 个月）。表明该版本不是长期维护版，开发者需在 3 个月内评估是否升级到下一个正式版本。

### 表格 2：Related Product Versions（相关产品版本）

| Product | Version |
| --- | --- |
| Ascend HDK | 26.0.RC1 |
| CANN | 9.0.0 |

**逐行解读**：声明本 RC 版本必须搭配的两个上游组件版本——华为昇腾硬件开发套件 HDK 为 26.0.RC1（与本版本号同节奏的 RC），而 CANN 异构计算架构为 9.0.0（已是 8.x 之后的下一代主版本）。

### 表格 3：Software Version Compatibility Description（**Table 1**）

| MindSDK Software Version | MindSDK Version to Upgrade | CANN Version Compatibility | Ascend HDK Version Compatibility |
| --- | --- | --- | --- |
| MindSDK 7.3.0 | <li>MindSDK 6.0.RC3 and 6.0.RC3.x</li><li>MindSDK 6.0.0 and 6.0.0.x</li><li>MindSDK 7.0.RC1 and 7.0.RC1.x</li><li>MindSDK 7.1.RC1 and 7.1.RC1.x</li><li>MindSDK 7.2.RC1 and 7.2.RC1.x</li><li>MindSDK 7.3.0 and 7.3.0.x</li> | <li>CANN 8.1.RC1 and 8.1.RC1.x</li><li>CANN 8.2.RC1 and 8.2.RC1.x</li><li>CANN 8.3.RC1 and 8.3.RC1.x</li><li>CANN 8.5.0 and 8.5.x</li> | <li>Ascend HDK 25.0.RC1 and Ascend HDK 25.0.RC1.x</li><li>Ascend HDK 25.2.0 and Ascend HDK 25.2.0.x</li><li>Ascend HDK 25.3.RC1 and Ascend HDK 25.3.RC1.x</li><li>Ascend HDK 25.5.0 and Ascend HDK 25.5.0.x</li><li>Ascend HDK 26.0.RC1 and Ascend HDK 26.0.RC1.x</li> |

**逐行解读**：
- 第 1 列：本行为 MindSDK 当前发布基线（7.3.0，是文档中升级路径的"目标版本起点"）。
- 第 2 列（可升级源）：允许从 6.0.RC3、6.0.0、7.0.RC1、7.1.RC1、7.2.RC1、7.3.0 共 6 个 MindSDK 大版本及其 `.x` 补丁直接升至本版本，跨度达 3 个大版本号。
- 第 3 列（CANN 兼容集）：同时兼容 CANN 8.1.RC1、8.2.RC1、8.3.RC1 与 8.5.0 共 4 条主版本线，意味着 CANN 不需要随 MindSDK 一起联动升级。
- 第 4 列（Ascend HDK 兼容集）：同时兼容 HDK 25.0.RC1、25.2.0、25.3.RC1、25.5.0 与 26.0.RC1 共 5 条主版本线，覆盖 25.x 全系列与新一代 26.0.RC1。
- 综合效果：MindSDK 7.3.0 → 26.0.0 的升级可独立完成，对 CANN、HDK 是完全可选的版本组合，验证了文中"无兼容性问题"的论断。

### 表格 4：New Features（新特性）

| Feature | Description | Supported Product Models |
| --- | --- | --- |
| Vision SDK | No new features | <li>Atlas 300I inference card (Model 3010) (x86_64)</li><li>Atlas 300I inference card (Model 3000) (Arm)</li><li>Atlas 500 A2 Smart Station</li><li>Atlas 300I Pro inference card</li><li>Atlas 300I Duo inference card</li><li>Atlas 300V video analysis card</li><li>Atlas 300V Pro video analysis card</li><li>Atlas 200I SoC A1 core board</li><li>Atlas 800I A2 inference product</li> |

**逐行解读**：Description 列明 "No new features"，因此 Supported Product Models 列只是重申 SDK 当前**仍然继续支持**的 9 类 Atlas 硬件型号清单（涵盖 x86_64 与 Arm 两种服务器架构、A 系列推理服务器、视频分析卡、边缘 Smart Station 与 SoC 核心板），并不代表新增了对这些产品的支持。

### 表格 5：26.0.0 Documentation（26.0.0 配套文档）

| Document | Description | Update Notes |
| --- | --- | --- |
| *Vision SDK 26.0.0 User Guide* | Provides guidance for developers to implement functions such as object detection and image classification through Vision SDK API development method or process orchestration method based on existing models, and includes Vision SDK API references. | For changes, see [Vision SDK 26.0.0 User Guide](./introduction.md). |

**逐行解读**：本次仅随附一份 User Guide，覆盖**两种开发范式**——API 开发方式 与 流程编排方式（基于已有模型），典型任务为**目标检测与图像分类**，并提供完整的 API reference。Update Notes 列指向站内 `./introduction.md`，即本文唯一的内部链接。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **配套用户指南（唯一内部链接）**：`./introduction.md` → *Vision SDK 26.0.0 User Guide*。本文中"使用方法"段落所述的 API 开发与流程编排两条路径、目标检测/图像分类能力以及 API 参考，均在该链接对应的文档中展开，**本 release_notes 不重复方法细节**。
- **上游依赖关系**：MindSDK 26.0.0（RCS SDK）→ Ascend HDK 26.0.RC1（硬件驱动/固件层）、CANN 9.0.0（计算架构层）。三者形成 SDK ↔ 驱动 ↔ 算子栈的纵向依赖；Table 1 又横向说明了 MindSDK 在 CANN 8.1–8.5、HDK 25.0–26.0 之间是解耦可替换的。
- **横向硬件关系**：文档所列 9 类 Atlas 产品（300I 推理卡 x86_64/Arm、500 A2、300I Pro、300I Duo、300V、300V Pro、200I A1 核心板、800I A2 推理服务器）是 Vision SDK API 与流程编排运行时的承载平台，二者通过 CANN/HDK 桥接。
- **与本仓库其他模块的耦合**：本次发布 Service Interface / Key Feature 均为 None，意味着 `introduction.md` 中描述的 API 表面在本 RC 中**未发生接口级变更**，开发者可直接复用既有调用代码。

---

## 【使用方法】

原文未涉及启用方式、配置项或具体命令。**本文档仅声明兼容性矩阵与变更状态**，不提供 API 调用、环境变量、配置文件或命令行示例；具体使用方法请参见：

- [Vision SDK 26.0.0 User Guide](./introduction.md)（覆盖 API 开发方式、流程编排方式、目标检测/图像分类示例与 API reference）。
