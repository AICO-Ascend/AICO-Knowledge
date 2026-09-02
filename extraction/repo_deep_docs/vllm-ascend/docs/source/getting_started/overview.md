# Getting Started

> 仓 `vllm-ascend` · 路径 `docs/source/getting_started/overview.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm-ascend/docs/source/getting_started/overview.md

# vllm-ascend 入门概览文档深度解读

## 【定位】

这篇文档是 vLLM Ascend 插件文档站"Getting Started（入门）"章节的**索引/导航页（hub page）**，解决"新用户如何从零开始使用 vLLM Ascend 插件"这一入口问题——即告诉读者后续在哪儿能找到环境搭建、首次推理、模型教程、高级特性与常见问题等子文档。

---

## 【技术要点】

由于原文是导航页而非技术细节页，技术性内容较为概括。可识别的核心要点如下：

1. **插件定位**：文档面向的是 **vLLM Ascend 插件**（vLLM Ascend plugin）的使用者。
2. **入门路径覆盖范围**：从**环境配置**（environment setup）一直延伸到**首次推理工作负载**（first inference workload）。
3. **快速上手方式**：支持使用**预构建镜像**（prebuilt image）跑通第一个模型。
4. **环境安装要素**：覆盖 **driver（驱动）**、**CANN**、**Python**、**Docker** 以及**源码安装**（source installation）等环境维度。
5. **进阶特性示例**：明确点名 **PD disaggregation**（Prefill-Decode 解耦）与 **context parallelism**（上下文并行）作为代表性高级特性。
6. **支持范围**：提供"特定模型部署说明"以及"常见部署与运行时问题排查"两个维度的文档。

---

## 【关键机制与数据】

> ⚠️ 本节说明：原文为导航型概述，**未给出任何具体性能数据、参数配置或数据流描述**。故无可写入的具体技术机制细节，仅做事实性摘录：

- **原文**：文档明确将 vLLM Ascend 描述为"vLLM 的插件（plugin）"形态，并将其入门流程定义为"从环境搭建到首次推理工作负载"。
- **原文**：进阶特性以列举方式给出两个具名条目——**PD disaggregation** 与 **context parallelism**——但未在本页展开其机制。
- **原文**：未给出任何量化指标（吞吐量、时延、显存占用、支持模型数量等），也无版本号、最低硬件要求等数字信息。

---

## 【表格解读】

**原文无表格**。

整篇文档仅由一段引言 + 一段无序列表（含 5 个 markdown 链接）构成，未出现任何 markdown 表格或对比表。

---

## 【公式解读】

**原文无公式**。

文档未包含任何 LaTeX 公式、伪代码、命令行片段、配置项块或示意图。

---

## 【关联】

本节依据文末给出的内部链接清单进行还原，呈现该概览页与文档站其他模块的"上下游/横向"关系：

| 上游/横向文档 | 关系性质 | 内容定位 |
|---|---|---|
| [Quick Start](quick_start.md) | **下游·首推入口** | 使用预构建镜像跑通第一个模型 |
| [Installation Guide](installation.md) | **下游·前置依赖** | 覆盖 driver / CANN / Python / Docker / 源码安装 5 类环境 |
| [Model Tutorials](../tutorials/models/index.md) | **横向·模型维度** | 提供具体模型的部署说明（index 页） |
| [Feature Tutorials](../tutorials/features/index.md) | **横向·特性维度** | 介绍 PD disaggregation、context parallelism 等高级特性 |
| [FAQ](../faqs.md) | **横向·支持维度** | 排查常见部署与运行时问题 |

**链路解读**：概览页位于文档站"入门"层级，向上承接站点根目录索引，向下分发到两类子文档——**操作型**（Quick Start、Installation）和**参考型**（Models、Features、FAQ）。对于一个新用户，**建议阅读顺序**为：Installation Guide → Quick Start → Model/Feature Tutorials → FAQ（与原文的列表顺序一致）。

---

## 【使用方法】

原文未涉及具体的启用命令、配置项或代码片段。**原文仅给出"去哪里找"而非"怎么用"**——例如：

- 它**提到**可以通过"预构建镜像（prebuilt image）"运行首个模型，但**未给出**任何 `docker pull`、`docker run` 或 `vllm serve` 命令。
- 它**提到**需要安装 driver / CANN / Python / Docker，但**未列出**具体版本号、安装命令或环境变量。
- 它**提及** PD disaggregation 与 context parallelism 两大特性，但**未给出**启用所需的配置开关或环境变量。

如需具体启用方式，请按文中指引进入 `installation.md`（环境侧）和 `quick_start.md`（运行侧）查阅。
