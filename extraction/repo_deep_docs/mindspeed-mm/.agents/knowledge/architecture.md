# Architecture Overview

> 仓 `mindspeed-mm` · 路径 `.agents/knowledge/architecture.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-mm/.agents/knowledge/architecture.md

# mindspeed-mm 架构总览文档 · 一体化深度解读

## 【定位】

这篇文档是一份面向 **AI 编码代理（coding agents）** 的仓库架构导航手册，旨在让代理在提出代码/文档/示例/测试改动之前，能够准确识别 mindspeed-mm 仓库的分层结构、两条主流训练后端的边界、入口路径与典型修改区域，从而做出正确的"在何处下笔"的决策。简言之：**它解决"在 mindspeed-mm 这个多模态训练仓库里，应该修改哪些路径、遵循哪条后端范式"的问题**。

---

## 【技术要点】

1. **仓库定位**：面向华为昇腾（Ascend）设备的多模态训练仓库，覆盖模型示例、训练流程、模型组件、检查点转换、评测、性能剖析（profiling）、优化工具集六大能力。
2. **七大仓库分层**：Examples / Megatron-style training / FSDP2 training / Models / Data / Tools / Tests，每一层都有明确的"主路径"与"Agent 关注点"（详见后文表格）。
3. **双后端并行架构**：同时支持 MindSpeed Core / Megatron（流水线并行+张量并行+数据并行）与 FSDP2（YAML 驱动 + 插件注册 + ModelHub + 显式并行计划）两条训练后端路线。
4. **Megatron 后端主入口**：`mindspeed_mm/training.py` 与 `mindspeed_mm/pretrain_*.py`，典型改动集中在 `pretrain_*.py`、model providers、data providers、forward steps、Megatron args 与 legacy examples。
5. **FSDP2 后端主入口**：`mindspeed_mm/fsdp/train/trainer.py`、`mindspeed_mm/config/config_manager.py`、`mindspeed_mm/fsdp/utils/register.py`，典型改动集中在 `mindspeed_mm/fsdp/models/`、`mindspeed_mm/fsdp/data/`、YAML 配置与 FSDP2 并行配置。
6. **兼容性约束**：FSDP2 示例可能仍包含 Megatron 风格的启动参数，以兼容既有的参数解析与启动惯例——这是双后端共存带来的混合现象。

---

## 【关键机制与数据】

**工作原理 / 数据流**

- 文档本身是"架构导航"性质，不描述具体训练算法或张量并行切分细节；其机制层面的核心信息是**两条后端的边界判定与启动路径选择**。
- Megatron 后端沿用 **provider 模式**：通过 model/data/forward provider 注入到共享训练循环（`mindspeed_mm/training.py`），并由 Megatron-style 参数解析驱动。
- FSDP2 后端沿用 **配置 + 注册模式**：YAML 配置经 `config_manager.py` 加载，模型通过 `ModelHub` 与 `register.py` 插件机制注册，并要求显式声明 FSDP2 并行计划（parallel plans）。
- 数据层为两条后端分别维护：通用 `mindspeed_mm/data/` 与 FSDP2 专用 `mindspeed_mm/fsdp/data/`（dataset 构造、collate 函数、多模态数据处理）。
- 工具层提供检查点转换、profiling、memory profiling 与 FLOPs 统计工具，横跨两条后端使用。

**性能数据**

原文未涉及具体性能数字、TPS、吞吐、显存占用等量化指标。该文档是架构总览而非性能报告。

---

## 【表格解读】

### 表 1 · Repository Layers（仓库分层）

**原文表格逐字还原**：

| Layer | Main Paths | Agent Focus |
| --- | --- | --- |
| Examples | `examples/` | Model-specific launch scripts, configs, README files, conversion commands, and performance settings. |
| Megatron-style training | `mindspeed_mm/pretrain_*.py`, `mindspeed_mm/training.py` | Shared training loop and model/data/forward provider flow. |
| FSDP2 training | `mindspeed_mm/fsdp/`, `mindspeed_mm/config/` | YAML-driven trainer, plugin registration, model hub, data builders, and parallel plans. |
| Models | `mindspeed_mm/models/`, `mindspeed_mm/fsdp/models/` | Model implementations, common modules, Transformers adapters, and FSDP2 wrappers. |
| Data | `mindspeed_mm/data/`, `mindspeed_mm/fsdp/data/` | Dataset construction, collators, and multimodal data handling. |
| Tools | `checkpoint/`, `mindspeed_mm/tools/`, `mindspeed_mm/fsdp/tools/` | Checkpoint conversion, profiling, memory profiling, and FLOPs tooling. |
| Tests | `tests/`, `ci/` | Unit tests, system tests, and CI entry points. |

**逐行解读**：

- **Examples（示例层）**：`examples/` 是用户视角的最高层入口，承载**模型专属**的启动脚本、配置文件、README、检查点转换命令以及性能设置。Agent 在此层的职责是"按模型找入口"。
- **Megatron-style training**：两条训练入口路径之一，**所有 `pretrain_*.py` 与 `training.py` 共同形成共享训练循环**；`provider` 机制（model/data/forward provider）是该层的核心抽象——意味着改训练逻辑要动 provider，而不是直接改训练循环。
- **FSDP2 training**：`mindspeed_mm/fsdp/` 与 `mindspeed_mm/config/` 协作，特点为 **YAML 驱动**（而非 provider 注入）、**插件注册**（plugin registration）、**ModelHub**（模型仓库抽象）、**显式 parallel plans**。这条路径强调声明式与可插拔。
- **Models**：模型实现层。**Megatron 路径**位于 `mindspeed_mm/models/`，包含模型实现、通用模块、Transformers 适配器；**FSDP2 路径**位于 `mindspeed_mm/fsdp/models/`，重点是 FSDP2 包装器（wrappers）。两层并存，互不替代。
- **Data**：与 Models 对偶——通用数据层 `mindspeed_mm/data/` 与 FSDP2 专属数据层 `mindspeed_mm/fsdp/data/`，分别服务两条后端，负责 dataset 构造、collate、多模态数据处理。
- **Tools**：横跨双后端的工具集，路径包括 `checkpoint/`、`mindspeed_mm/tools/`、`mindspeed_mm/fsdp/tools/`，提供检查点转换、profiling、memory profiling、FLOPs 统计。
- **Tests**：`tests/` 与 `ci/` 是单元测试、系统测试与 CI 入口。任何 Agent 改动都应回看本层是否有相应测试覆盖。

---

### 表 2 · Dual Backend Model（双后端模型对比）

**原文表格逐字还原**：

| Backend | Description | Primary Entries | Typical Change Areas |
| --- | --- | --- | --- |
| MindSpeed Core / Megatron | Megatron-style backend using Pipeline, Tensor, and Data parallelism through MindSpeed Core and Megatron adapters. | `mindspeed_mm/training.py`, `mindspeed_mm/pretrain_*.py`, `examples/*/*.sh` | `pretrain_*.py`, model providers, data providers, forward steps, Megatron args, legacy examples. |
| FSDP2 | FSDP2-oriented backend using YAML configuration, plugin registration, `ModelHub`, FSDP2 data builders, and explicit parallel plans. | `mindspeed_mm/fsdp/train/trainer.py`, `mindspeed_mm/config/config_manager.py`, `mindspeed_mm/fsdp/utils/register.py` | `mindspeed_mm/fsdp/models/`, `mindspeed_mm/fsdp/data/`, YAML configs, FSDP2 parallel configs. |

**逐行解读**：

- **Backend 列**：明确划分两条主线——`MindSpeed Core / Megatron` 与 `FSDP2`。
- **MindSpeed Core / Megatron 行**：
  - *Description*：基于 **MindSpeed Core 与 Megatron 适配器**，同时使用**流水线并行（PP）+ 张量并行（TP）+ 数据并行（DP）**三种并行范式——属于"经典三件套"组合。
  - *Primary Entries*：训练循环入口 `training.py`、各模型预训练入口 `pretrain_*.py`、启动脚本 `examples/*/*.sh`。
  - *Typical Change Areas*：典型改动集中在 `pretrain_*.py`、model providers、data providers、forward steps、Megatron args 与 legacy examples——这意味着该后端的修改是**过程式 / provider 注入式**的。
- **FSDP2 行**：
  - *Description*：FSDP2 后端通过 **YAML 配置、插件注册、`ModelHub`、FSDP2 数据构造器、显式 parallel plans** 工作——属于"声明式 + 注册式"组合。
  - *Primary Entries*：`mindspeed_mm/fsdp/train/trainer.py`（YAML 驱动的 trainer）、`mindspeed_mm/config/config_manager.py`（配置管理器）、`mindspeed_mm/fsdp/utils/register.py`（插件注册中心）。
  - *Typical Change Areas*：`mindspeed_mm/fsdp/models/`（FSDP2 模型包装器）、`mindspeed_mm/fsdp/data/`（FSDP2 数据构造）、YAML 配置、FSDP2 并行配置——修改方式以**配置与注册**为主，而非修改 provider。

---

## 【公式解读】

原文无公式。该文档为架构总览，未出现任何数学公式、LaTeX 表达式或伪代码算法块。

---

## 【关联】

文档给出的关联脉络如下：

- **后端 × 分层的正交关系**：仓库分层（表 1）中的 Megatron-style training、FSDP2 training、Models、Data、Tools 五个层都与表 2 中的两条后端**正交耦合**——每个层都有 Megatron 与 FSDP2 两个子路径（例如 Models 层下既有 `mindspeed_mm/models/` 又有 `mindspeed_mm/fsdp/models/`）。
- **Examples ↔ 双后端**：Examples 层通过 `examples/*/*.sh` 启动脚本**桥接**到 Megatron 后端；同时 FSDP2 示例仍包含 Megatron-style 启动参数——因此 Examples 层是双后端兼容性的"现实交汇点"。
- **Tools ↔ 双后端**：Tools 层提供**横跨双后端**的检查点转换、profiling、memory profiling、FLOPs 工具，意味着 Agent 在做性能或检查点相关改动时，可同时影响两条后端。
- **Tests ↔ 双后端**：`tests/` 与 `ci/` 是覆盖两条后端验证的统一切入点。
- **FSDP2 内部组件关系**：`ModelHub`（模型注册） ↔ `register.py`（插件注册中心） ↔ `config_manager.py`（YAML 加载） ↔ `trainer.py`（训练驱动）形成一条**声明式调用链**：YAML → 配置管理器 → 注册表 → ModelHub → trainer。
- **Megatron 内部组件关系**：`training.py`（共享循环） ← `pretrain_*.py`（provider 注入点） ← model/data/forward providers，构成**过程式调用链**。

文末标注"内部链接: (无)"，文档本身不提供额外的内部超链接跳转；但上述分层—后端的对照关系是文档内部最强的关联信息。

---

## 【使用方法】

**启用方式 / 配置项 / 命令**

原文本身并未给出可直接执行的命令、配置项清单或启用步骤。该文档定位为"导航手册"而非"操作手册"，明确说明其使用方式是：

> *"Use it to choose the correct backend and entry points before proposing code, documentation, example, or test changes."*
> —— 即：在 Agent 提议改动**之前**，用本文档来选定正确的**后端**与**入口路径**。

涉及可执行入口的事实性引用（仅来自原文表格，未做扩展）：

- Megatron 后端启动：`examples/*/*.sh`（具体命令需查阅各模型示例的 shell 脚本）。
- FSDP2 后端启动：通过 `mindspeed_mm/fsdp/train/trainer.py` 配合 `mindspeed_mm/config/config_manager.py` 加载的 YAML 配置驱动。

任何更具体的启动命令、配置项默认值、性能调优开关，原文均未涉及，需另行查阅 `examples/` 下各模型目录的 README 与启动脚本。
