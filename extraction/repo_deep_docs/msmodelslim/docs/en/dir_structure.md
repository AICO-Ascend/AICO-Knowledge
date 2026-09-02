# Project Directory Structure Overview

> 仓 `msmodelslim` · 路径 `docs/en/dir_structure.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msmodelslim/docs/en/dir_structure.md

# msModelSlim 仓库结构文档深度解读

## 【定位】

这篇文档是 msModelSlim 项目（MindStudio 全流程工具链的模型量化压缩工具）的**项目目录结构总览（Project Directory Structure Overview）**，用于向读者呈现仓库从顶层到子目录 `msmodelslim/` 的层级布局，明确区分 **V0 框架**（legacy / 小模型）与 **V1 框架**（分层解耦的基座模型量化框架）所涉及的目录范围，并指出源码主入口位于 `msmodelslim/` 子目录下。

---

## 【技术要点】

1. **算法演进路径**：项目追踪了 AI 从小模型到基座模型（foundation models）的演进轨迹；初期支持剪枝（pruning）、蒸馏（distillation）、量化（quantization）三类压缩能力，后逐步转向基座模型量化。
2. **行业标准量化算法支持**：V1 框架支持 **Smooth Quant、GPTQ、HQQ** 三种基座模型量化算法。
3. **量化位宽目标**：随着模型架构复杂化，量化位宽降至 **4-bit 或更低（ultra-low bit-widths）**，单算法已难以同时满足性能与精度要求。
4. **复合策略（composite strategies）**：已成为标准实践，以应对精度+性能双重约束。
5. **V1 框架定位**：分层解耦（hierarchically decoupled）的基座模型量化框架；V0 框架承载遗留量化能力与小模型压缩。
6. **多代码库共存**：仓库目前**同时存在三套代码库**，尽量按目录隔离，后续会逐步合并；用户被建议使用 V1 框架。
7. **分层架构（V1）**：`cli`（接口层）→ `app`（应用层：快速量化、自动调优、量化分析）→ `core`/`processor`/`ir`（领域层）→ `infra`/`model`（基础设施层，含外部依赖与模型结构适配器），`utils` 提供日志/配置/校验/安全等通用模块。
8. **IR 与低比特模式**：`ir/` 目录定义核心中间表示与低比特模式（如 **W8A8 量化**）。

---

## 【关键机制与数据】

- **工作原理（V1 分层）**：自顶向下的调用关系为：CLI 命令行入口 → 应用层（`app/` 下 `naive_quantization`/`auto_tuning`/`analysis` 三个子模块）编排流程 → 领域层 `core/` 与 `processor/`（如 GPTQ 算法执行处理器）执行业务逻辑 → 基础设施层 `infra/` 与模型适配器 `model/`（DeepSeek、Qwen 等）对接外部依赖。
- **数据流形态（原文示例）**：`app/auto_tuning/` 下设六个基础设施接口文件：评估服务（`evaluation_service_infra.py`）、调优计划管理（`plan_manager_infra.py`）、量化配置精度缓存（`practice_accuracy_infra.py`）、调优历史（`practice_history_infra.py`）、实践管理（`practice_manager_infra.py`）、模型元数据接口（`model_info_interface.py`），形成"计划→执行→评估→历史"的闭环。
- **IR 覆盖的低比特模式（原文）**：W8A8 量化被显式列为 IR 已定义的低比特模式之一。
- **性能/效率指标（原文）**：文档提出对工具链的三项硬性要求——**更好的易用性（better tool usability）、更高的量化调优效率（higher quantization tuning efficiency）、更低的单模型处理时长（reduced single-model processing duration）**，但未给出具体数值。
- **原文未提供**：性能基准、精度数字、延迟数字、压缩率等量化数据。

---

## 【表格解读】

原文为目录结构清单（目录树形式），无传统二维参数/对比表。下表按原文逐字还原三处核心结构树，并就关键行做注释：

### 表 1 — 仓库顶层目录结构（完整 msmodelslim/）

| 路径 / 文件 | 原文标注 | 作用说明 |
|---|---|---|
| `ascend_utils/` | Base dependencies for small model compression including pruning, quantization, and distillation | 小模型压缩（剪枝/量化/蒸馏）的基础依赖 |
| `config/` | Global configuration directory (V1 framework) | 全局配置目录（仅 V1） |
| `docs/` | Project documentation including installation guides, quickstart guides, algorithm descriptions, feature guides, and case studies | 安装/快速上手/算法/特性/案例文档 |
| `example/` | Model quantization examples (primarily V0 scripts, alongside centralized V1 process FAQs) | 主要 V0 示例脚本 + V1 流程 FAQ |
| `lab_calib/` | Calibration dataset examples containing formats such as JSON, JSONL, and images (V1 framework) | 校准数据集示例（JSON/JSONL/图像），仅 V1 |
| `lab_practice/` | Best-practice quantization configurations for various models (V1 framework) | 各模型最佳实践量化配置，仅 V1 |
| `modelslim/` | Compatibility layer for the modelslim alias (V0 framework) | `modelslim` 别名兼容层，仅 V0 |
| `msmodelslim/` | Project source code | 项目源代码主入口 |
| `precision_tool/` | Fake-quantization accuracy evaluation tool (V0 framework) | 伪量化精度评估工具，仅 V0 |
| `security/` | Core security verification modules (V0 framework) | 核心安全验证模块，仅 V0 |
| `test/` | Test cases and test scripts | 测试用例与脚本 |
| `install.sh` | Installation script | 安装脚本 |
| `requirements.txt` | Third-party dependency list | 第三方依赖列表 |
| `pytest.ini` | Test configuration | 测试配置 |
| `README.md` | Project overview and usage guidelines | 项目概览与使用指南 |
| `LICENSE` | Open source license | 开源许可证 |
| `OWNERS` | Code ownership and approval configuration | 代码所有权与审批配置 |
| `setup.py` | Packaging and installation configuration script | 打包与安装配置脚本 |

### 表 2 — `msmodelslim/` 一级子目录（含 V0/V1 双标注）

| 子目录 | 标注 | 层级定位与职责 |
|---|---|---|
| `app/` | V1 框架；快速量化、自动调优、量化分析 | 应用层 |
| `cli/` | V1 框架；命令行接口与功能子命令 | 接口层 |
| `common/` | 框架无关压缩逻辑：知识蒸馏、低秩分解、剪枝（小模型） | 通用压缩（V0 / 小模型） |
| `core/` | V1 框架；量化的业务逻辑与功能模块 | 领域层 |
| `infra/` | V1 框架；外部依赖适配器 | 基础设施层 |
| `ir/` | V1 框架；核心中间表示与 W8A8 等低比特模式 | 领域层 |
| `mindspore/` | V0 + 小模型；MindSpore 框架适配与功能实现 | 框架适配 |
| `model/` | 基础设施层；DeepSeek、Qwen 等模型结构适配器 | 基础设施层 |
| `onnx/` | V0 + 小模型；ONNX 框架适配与功能实现 | 框架适配 |
| `processor/` | V1 框架；如 GPTQ 等量化执行处理器 | 领域层 |
| `pytorch/` | V0 + 小模型；PyTorch 框架适配与功能实现 | 框架适配 |
| `quant/` | V0 框架；多模态量化能力 | V0 专属 |
| `utils/` | V1 框架；日志、配置、校验、安全等通用模块 | 通用 |
| `Third_Party_Open_Source_Software_Notice` | — | 第三方开源软件声明 |
| `__init__.py` | — | Python 包初始化 |

### 表 3 — `app/` 目录结构（原文已提供部分）

| 子目录 / 文件 | 原文标注 | 职责 |
|---|---|---|
| `app/__init__.py` | — | 应用层包初始化 |
| `app/analysis/` | Quantization analysis application module | 量化分析应用模块 |
| `app/analysis/__init__.py` | — | 模块初始化 |
| `app/analysis/application.py` | Workflow and orchestration for quantization analysis | 量化分析的工作流编排 |
| `app/analysis/result_displayer_infra.py` | Infrastructure interface for result visualization | 结果可视化基础设施接口 |
| `app/auto_tuning/` | Automatic tuning application module | 自动调优应用模块 |
| `app/auto_tuning/__init__.py` | — | 模块初始化 |
| `app/auto_tuning/application.py` | Workflow and orchestration for automatic tuning | 自动调优的工作流编排 |
| `app/auto_tuning/evaluation_service_infra.py` | Infrastructure interface for evaluation services | 评估服务基础设施接口 |
| `app/auto_tuning/model_info_interface.py` | Model adaptation interface for retrieving model metadata | 模型元数据获取适配接口 |
| `app/auto_tuning/plan_manager_infra.py` | Infrastructure interface for tuning plan management | 调优计划管理基础设施接口 |
| `app/auto_tuning/practice_accuracy_infra.py` | Infrastructure interface for quantization configuration accuracy caching | 量化配置精度缓存基础设施接口 |
| `app/auto_tuning/practice_history_infra.py` | Infrastructure interface for tuning history management | 调优历史管理基础设施接口 |
| `app/auto_tuning/practice_manager_infra.py` | Infrastructure interface for practice management | 实践管理基础设施接口 |
| `app/naive_quantization/` | Quick quantization application module | 快速量化应用模块 |
| `app/naive_quantization/__init__.py` | — | 模块初始化 |
| `app/naive_quantization/application.py` | Workflow and orchestration for quick quantization | 快速量化的工作流编排 |
| `app/naive_quantization/model_info_interface.py` | Model adaptation interface for retrieving model metadata | 模型元数据获取适配接口 |

> **说明**：原文在 `app/naive_quantization/` 处被截断（末尾为未闭合的 `└─`），其后 `cli/`、`core/`、`infra/`、`ir/`、`processor/`、`utils/` 等目录的详细结构原文未提供，本次解读无法补充。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **V0 与 V1 框架的目录映射关系（原文显式给出）**：
  - V0 专属目录：`ascend_utils/`、`modelslim/`（兼容层）、`precision_tool/`、`security/`、`quant/`（多模态）。
  - V0 + 小模型目录：`mindspore/`、`onnx/`、`pytorch/`、`common/`（剪枝/蒸馏/低秩分解）。
  - V1 专属目录：`config/`、`lab_calib/`、`lab_practice/`、`app/`、`cli/`、`core/`、`infra/`、`ir/`、`processor/`、`utils/`。
  - 三方共属：`msmodelslim/`（源码根）、`docs/`、`example/`（以 V0 脚本为主，兼 V1 FAQ）、`test/`、根级构建/许可/安装文件。
- **应用层三个子模块与领域层/基础设施层的耦合**：
  - `app/auto_tuning/` 通过六个 `*_infra.py` 接口文件与 `infra/`、`core/` 对接；
  - `app/naive_quantization/` 与 `app/analysis/` 均依赖 `model/` 下的模型结构适配器（如 DeepSeek、Qwen）；
  - `processor/`（如 GPTQ）作为算法执行体被 `app/` 调用；
  - `ir/` 提供 W8A8 等低比特中间表示，被 `core/` 与 `processor/` 共用。
- **数据资产关联**：`lab_calib/` 提供校准数据样本（JSON/JSONL/图像），`lab_practice/` 提供验证过的最佳实践配置，二者共同支撑 `app/auto_tuning/` 的调优闭环。
- **上下游衔接**：`example/` 同时承载 V0 脚本与 V1 流程 FAQ，扮演"过渡桥梁"角色；遗留代码（legacy code）继续保留以补齐 V1 尚未封装的能力。
- **本文档在文档体系中的位置**：`docs/en/dir_structure.md` 与 `README.md`、`docs/`（安装/快速上手/算法/特性/案例）属同一文档树，是面向开发者的入口索引。
- **内部链接**：原文未提供内部超链接。

---

## 【使用方法】

原文未涉及具体启用方式、配置项或命令（本文档仅描述目录布局）。可推断的入口信息（仅基于原文标注）：

- 安装入口：`install.sh`（安装脚本）、`setup.py`（打包安装配置）、`requirements.txt`（第三方依赖）。
- 测试入口：`test/` 目录 + `pytest.ini`（测试配置）。
- V1 框架调用入口推断：`cli/`（命令行接口与功能子命令）。
- **原文未给出**：CLI 子命令列表、量化启动命令、配置项键值、环境变量、API 调用示例、参数说明。

> **文档截断提示**：原文在 `app/naive_quantization/` 列表末尾被截断（出现 `└─` 后无后续字符），本解读无法覆盖 `cli/`、`core/`、`infra/`、`ir/`、`processor/`、`utils/` 等 V1 关键子目录的下一层级细节，建议结合 `msmodelslim/<sub>/` 内的源码与 `docs/` 其他文档获取完整结构。
