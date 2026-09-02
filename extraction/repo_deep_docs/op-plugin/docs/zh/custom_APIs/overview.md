# 概述

> 仓 `op-plugin` · 路径 `docs/zh/custom_APIs/overview.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/op-plugin/docs/zh/custom_APIs/overview.md

# 「op-plugin」文档深度解读 —— `docs/zh/custom_APIs/overview.md`

---

## 【定位】

本文档是 TorchNPU 自定义 API 模块的总纲性说明，向用户告知该模块的功能定位、接口规范约束、与 PyTorch 的对接方式、开发语言边界、beta 接口风险以及版本兼容策略，作为后续逐 API 详细页面的导读与约束声明。

---

## 【技术要点】

1. **文档内容范围**：涵盖 TorchNPU 自定义 API 的功能说明、函数原型、参数说明及调用示例，是后续具体 API 文档的总入口。
2. **接口规范遵循**：所有 TorchNPU 接口遵循 [PyTorch 社区公开接口规范](https://github.com/pytorch/pytorch/wiki/Public-API-definition-and-documentation)；文档所列仅为对外公开接口，内部接口后续版本可能被修改或删除。
3. **对接机制**：TorchNPU 使用 **monkey-patch** 方式与 PyTorch 接口对接，即把 TorchNPU 部分接口**动态替换**至 PyTorch 接口中，从而让用户在昇腾 NPU 上继续使用熟悉的 PyTorch 接口。
4. **开发语言边界**：项目采用 **C++ 与 Python 联合开发**；当前正式对外接口**仅包括 Python 接口**，C++ 接口为内部使用接口，**不建议用户使用**。
5. **beta 接口风险**：部分接口被标记为 **beta 类接口**（实验性接口），部分场景下可能异常，需谨慎使用；后续可能根据需要进行改动（含参数变更、名称变更、移除）。
6. **版本兼容策略**：所有自定义 API **默认支持 TorchNPU 版本匹配的全量 PyTorch 版本**；若非全量支持，会在各 API 的约束说明中单独标注。
7. **环境变量补充说明**：TorchNPU 部分功能可通过环境变量实现，参见《环境变量》文档。

---

## 【关键机制与数据】

- **monkey-patch 对接原理**（原文）：TorchNPU 将自身部分接口动态替换至 PyTorch 接口中，使用户在昇腾 NPU 上能够继续沿用 PyTorch 既有接口。这是整个自定义 API 模块能够"无缝接入"PyTorch 编程体验的核心机制，不改变用户层的接口调用形式，仅在底层把算子/行为指向昇腾 NPU 实现。
- **接口稳定性分层**（原文）：分为"对外公开接口"与"内部接口"两层；前者稳定，后者可能在后续版本中被修改或删除，若必须使用需在昇腾社区提交 issue 获取支持。
- **语言分层**（原文）：Python 为对外正式接口，C++ 为内部接口；这是显式的语言层 ABI 边界声明。
- **beta 演进路径**（原文）：beta 接口目标是被纳入稳定接口，但纳入前可能发生参数、名称变更甚至移除，提示用户在生产场景需自担风险。
- **版本对齐默认行为**（原文）：TorchNPU 与 PyTorch 版本"默认全量支持"——即不写特别说明的 API，默认跨 TorchNPU 对应版本所支持的 PyTorch 全版本可用。

> 原文未提供具体性能数据、benchmark 数字或量化指标；本文档属于"概述/规范声明"性质文档。

---

## 【表格解读】

原文无表格。

---

## 【公式解读】

原文无公式。

---

## 【关联】

本文档为总纲性说明，未在文末给出具体的内部 API 链接清单；文中提及的外部/上下文档关系如下：

- **PyTorch 社区公开接口规范**：作为 TorchNPU 自定义 API 必须遵守的规范来源，约束接口命名、签名、行为契约。
- **昇腾社区 issue 入口（[Ascend/pytorch issues](https://gitcode.com/ascend/pytorch/issues)）**：当用户必须使用内部接口时获取官方支持的渠道。
- **环境变量文档**（`docs/zh/api/environment_variable/env_variable_list.md`）：部分功能的开关/调优需要通过环境变量实现，与本文档并列属于 TorchNPU 的功能配置手段。
- **各 API 约束说明页**：当某 API 并非默认支持全量 PyTorch 版本时，会在该具体 API 的页面单独标注——本文档作为顶层声明，具体例外细节下沉到子页面。
- **beta → 稳定 接口演进关系**：beta 接口是稳定接口的"前身/候选"，两者属于同一接口生命周期中的不同阶段。

> 文末链接区段标注为"(无)"，本文档未直接挂载内部 API 子页链接，所有子 API 详细说明在仓库其他文件展开。

---

## 【使用方法】

本文档为概述性内容，原文未给出具体启用命令、配置项或 API 调用方式；用户需使用 TorchNPU 自定义 API 时，按以下思路进行：

- **调用方式**：直接在 Python 代码中沿用 PyTorch 习惯接口调用方式即可，无需手动 import 切换——TorchNPU 通过 monkey-patch 已将相关接口动态注入至 PyTorch 接口体系。
- **环境变量配置**：若需通过环境变量控制部分功能，参见《环境变量》文档（`docs/zh/api/environment_variable/env_variable_list.md`）的具体配置项说明。
- **版本兼容性核验**：在使用前查阅具体 API 的约束说明页，确认其是否对 PyTorch 版本有非默认的限制。
- **beta 接口使用**：生产环境需谨慎使用；如必须使用内部 C++ 接口或 beta 接口遇到问题，前往昇腾社区 issue 入口提交求助。

> 原文未涉及具体的 import 语句、环境变量名、编译开关或硬件配置命令。
