# Release Notes

> 仓 `release-management` · 路径 `MindStudio/26.1.0/release_notes_en.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/release-management/MindStudio/26.1.0/release_notes_en.md

# MindStudio 26.1.0 Release Notes 一体化解读

## 【定位】

本文档是 MindStudio 26.1.0 版本（Ascend 面向 AI 开发者的全流程开发工具链）的英文版 Release Notes，定位是**向用户同步该版本的兼容性矩阵、新特性能力升级与工具链重构说明**，覆盖训练开发工具、推理开发工具、算子开发工具三大方向的核心改进。

---

## 【技术要点】

1. **版本对齐基线（核心数字）**：MindStudio 26.1.x 对应 CANN 9.1.0、TorchNPU 26.1.0、Ascend HDK 26.1.0（即四个组件同步大版本对齐）；同时仍向后兼容 CANN 8.5.0 与 9.0.0、TorchNPU 2.3.0 与 26.0.0、Ascend HDK 25.5.x 与 26.0.RC1/25.7.RC1。

2. **训练工具链三场景聚焦**：围绕**强化学习（reinforcement learning）、Agent 智能分析、HostBound 问题定位**三大场景，针对多核调度不均、训练-推理一致性、长时间训练异常检测、Host 侧瓶颈、复杂问题排查成本等痛点，实现端到端的训练精度/性能/显存问题定位能力。

3. **推理工具链四能力优化**：升级**精度数据采集、量化、仿真、建模**四个关键能力，缩短模型推理部署周期、降低手工调优与参数选择成本，缓解陡峭的学习曲线。

4. **算子工具链面向 Ascend 950 重构**：从**异常检测、问题调试、性能调优**三个维度重塑算子全流程工具链，解决新架构下调测门槛高、异常检测能力不完整、硬件性能调优耗时长的问题。

5. **msKPP 工程化增强**：新增 `compile.json` 生成能力（用于记录编译选项与依赖，支持性能分析与 CI 工具链集成）；统一构建入口脚本并适配新统一构建镜像；引入 `clang-tidy` 静态分析与 pre-commit 钩子；扩展核心模块单元测试；CI 流水线支持基于 tag 的发布版本号管理。

6. **msOpGen 安装/构建范式革新**：用 `entry_points` 方式替换旧的 `pip install` 模式以解决卸载残留问题（`msopst.ini` 配置文件迁移至标准配置目录）；将 `build.py` 提升为正式统一构建入口并加入子模块固定版本校验；安装阶段移除符号链接/文件属主/路径长度等安全校验以降低受限环境的部署门槛；quick start 适配 CANN 9.0.0 编译接口变化。

---

## 【关键机制与数据】

**原文工作机制说明**：

- **工具链定位机制**（原文 Section 1）：MindStudio 覆盖算子开发、精度调测、性能调优、可视化分析四大核心开发阶段，本版本"持续简化 Ascend AI 开发流程，降低开发门槛，提升量化效率，增强算子调优与问题定位效率"。

- **训练侧痛点→能力映射**（原文 Section 1）：痛点包括"多核调度不均、强化学习训练-推理不一致、长时间训练异常难以察觉、Host 侧瓶颈突出、复杂问题排查成本高"，对应能力是"端到端定位训练精度、性能、显存问题"。

- **推理侧痛点→能力映射**（原文 Section 1）：痛点包括"模型推理部署周期长、手工调优成本高、参数选择困难、学习曲线陡峭"，对应能力是"精度数据采集、量化、仿真、建模"四能力优化。

- **算子侧痛点→能力映射**（原文 Section 1）：痛点针对 Ascend 950 的"新架构调测门槛高、异常检测能力不完整、硬件性能调优分析耗时"，对应"异常检测、问题调试、性能调优"三维能力升级。

- **版本兼容符号约定**（原文 Section 3 NOTE）：`Y` 表示支持，`/` 表示不支持。

- **`compile.json` 集成机制**（原文 Section 4 msKPP 首条）："在构建过程中生成 compile.json，记录编译选项与依赖，支持与性能分析与 CI 工具链集成"。

- **统一构建镜像同步**（原文 Section 4 msKPP 第二条）："统一构建入口脚本以适配新统一构建镜像；UT 环境同步更新，提升构建稳定性与 CI 兼容性"。

- **msOpGen 安装残留修复**（原文 Section 4 msOpGen 第一条）："将传统 pip install 方式替换为基于 entry_points 的安装方式，解决 pip uninstall 后的残留文件问题；msopst.ini 配置文件迁移至标准配置目录；依赖旧路径的自定义脚本需相应更新"。

- **构建入口升级**（原文 Section 4 msOpGen 第二条）："将 build.py 提升为正式统一构建入口，加入固定版本的子模块检出，提升首次构建成功率与可用性，并适配新统一构建镜像"。

- **安全校验放宽**（原文 Section 4 msOpGen 第三条）："安装阶段移除符号链接校验、文件属主校验与路径长度限制"。

> 备注：原文 Section 4（New Features）表格在 `MindStudio branding & pre-commit` 行被截断，后续内容（如可能存在的 msProf、msTool、量化工具、算子调试等子模块特性）未在本次提供文本内出现。

---

## 【表格解读】

### 表 1：Section 2 — 本版本对齐基线（原文逐字还原）

| MindStudio | CANN | TorchNPU | Ascend HDK |
| ---- | ---- | ---- | ---- |
| 26.1.x | 9.1.0 | 26.1.0 | 26.1.0 |

**逐行解读**：
- 唯一一行表示 MindStudio 26.1.x 本版本所对齐的推荐基线：**CANN 9.1.0 + TorchNPU 26.1.0 + Ascend HDK 26.1.0**。这是该版本"四个组件同步大版本对齐"的核心数字证据，下文的兼容性矩阵必须围绕此基线展开。

---

### 表 2：Section 3 — MindStudio × CANN 兼容矩阵（原文逐字还原）

> 注：原文采用 HTML `<table>` 实现，列头使用 rowspan/colspan 合并。此处按业务语义用 markdown 表格等价还原。

| MindStudio \ CANN | 8.5.0 | 9.0.0 | 9.1.0 |
| ----------------- | ----- | ----- | ----- |
| 8.3.x             | Y     | /     | /     |
| 26.0.x            | Y     | Y     | /     |
| 26.1.x            | Y     | Y     | Y     |

**逐行解读**：
- **8.3.x 行**：仅兼容 CANN 8.5.0（即旧主版本基线），不兼容 CANN 9.0.0 与 9.1.0，属于"老 MindStudio + 老 CANN"封闭搭配。
- **26.0.x 行**：兼容 CANN 8.5.0 与 9.0.0，是上一个大版本的过渡兼容带，体现"向上跨一个 CANN 大版本"的兼容策略。
- **26.1.x 行（重点）**：同时兼容 CANN 8.5.0、9.0.0、9.1.0，**兼容跨度达到 3 个 CANN 版本**，这是本版本兼容性最重要的扩展点。

---

### 表 3：Section 3 — MindStudio × TorchNPU 兼容矩阵（原文逐字还原）

| MindStudio \ TorchNPU | 2.3.0 | 26.0.0 | 26.1.0 |
| --------------------- | ----- | ------ | ------ |
| 8.3.x                 | Y     | /      | /      |
| 26.0.x                | Y     | Y      | /      |
| 26.1.x                | Y     | Y      | Y      |

**逐行解读**：
- **8.3.x 行**：仅支持 TorchNPU 2.3.0。
- **26.0.x 行**：支持 TorchNPU 2.3.0 与 26.0.0，是 26 系列对老 TorchNPU 2.3.0 的过渡兼容。
- **26.1.x 行（重点）**：同时支持 TorchNPU 2.3.0、26.0.0、26.1.0，**首次在 TorchNPU 维度形成三版本兼容**，意味着本版 MindStudio 在 TorchNPU 升级路径上提供"老 → 新"平滑过渡。

---

### 表 4：Section 3 — MindStudio × Ascend HDK 兼容矩阵（原文逐字还原）

| MindStudio \ Ascend HDK | 25.5.x | 26.0.RC1 / 25.7.RC1 | 26.1.0 |
| ----------------------- | ------ | ------------------- | ------ |
| 8.3.x                   | Y      | /                   | /      |
| 26.0.x                  | Y      | Y                   | /      |
| 26.1.x                  | Y      | Y                   | Y      |

**逐行解读**：
- **8.3.x 行**：仅支持 Ascend HDK 25.5.x。
- **26.0.x 行**：支持 Ascend HDK 25.5.x 与 26.0.RC1/25.7.RC1（注意原文此列同时列出两个 RC 版本号，说明 Ascend HDK 在 26.0 阶段存在并行 RC 命名）。
- **26.1.x 行（重点）**：同时支持 Ascend HDK 25.5.x、26.0.RC1/25.7.RC1、26.1.0，**首次形成对三个 HDK 版本的兼容**，是"硬件驱动/固件升级路径"上的最大兼容跨度。

---

### 表 5：Section 4 — New Features（原文逐字还原，截至截断处）

| Tool              | Feature                                                      | Description                                                  |
| ----------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| msKPP             | compile.json generation                                      | Added support for generating compile.json during build to record compile options and dependencies, enabling integration with performance analysis and CI toolchains. |
| msKPP             | Unified build adaptation                                     | Unified the build entry script to work with the new unified build image; UT environments are synchronized accordingly, improving build stability and CI compatibility. |
| msKPP             | clang-tidy integration                                       | Introduced clang-tidy configuration and a pre-commit hook to enforce static analysis and clean code standards before each commit. |
| msKPP             | Unit test expansion                                          | Added new unit tests for the core msKPP modules, increasing test coverage and strengthening regression protection. |
| msKPP             | CI version tagging                                           | Enhanced CI pipelines to support release version numbering based on tags, ensuring package versions align with source code versions. |
| msOpGen           | Pip installation optimization                                | Replaced the legacy pip install approach with an entry_points-based installation to resolve residual file issues after pip uninstall. The msopst.ini configuration file is relocated to the standard configuration directory. Custom scripts relying on the old paths must be updated accordingly. |
| msOpGen           | Unified build promotion                                      | Elevated build.py as the formal unified build entry, with robust submodule checkout to pinned versions, improving first-time build success rates and usability. Also adapts to the new unified build image. |
| msOpGen           | Loosened security checks                                     | Removed symlink validation, file ownership checks, and path length restrictions during installation, lowering deployment barriers in constrained environments. |
| msOpGen           | Quick start updates                                          | Adapted to compilation interface changes in CANN 9.0.0; updates build commands and examples in quick start to ensure generated operator projects can be compiled properly under the latest CANN. |
| msOpGen           | MindStudio branding & pre-commit                             | Added support for MindStudio startu（原文此处被截断） |

**逐行解读**：
- **msKPP × compile.json generation**：构建期生成结构化元数据文件，作为性能分析/CI 工具链的"事实源"，是后续可观测性能力的基础。
- **msKPP × Unified build adaptation**：将构建入口与新统一构建镜像对齐，UT 环境同步更新，避免"本机可跑 CI 失败"的常见撕裂。
- **msKPP × clang-tidy integration**：在本地 pre-commit 阶段拦截静态分析问题，把代码质量门禁"左移"到开发侧。
- **msKPP × Unit test expansion**：核心模块增加单元测试覆盖率，强化回归保护。
- **msKPP × CI version tagging**：CI 通过 git tag 派生发布版本号，确保"包版本"与"代码版本"一一对应（避免手工维护导致漂移）。
- **msOpGen × Pip installation optimization**：以 `entry_points` 替代旧 `pip install`，解决卸载残留；同时 `msopst.ini` 路径迁移，**破坏性变更**——依赖旧路径的自定义脚本必须更新。
- **msOpGen × Unified build promotion**：`build.py` 成为正式统一构建入口，子模块 checkout 固定到 pinned 版本，提升首次构建成功率与可用性。
- **msOpGen × Loosened security checks**：安装时关闭符号链接/属主/路径长度三类安全校验，**降低受限环境（如容器、共享主机）的部署门槛**，但也意味着安全态势弱化，需用户自行补偿。
- **msOpGen × Quick start updates**：适配 CANN 9.0.0 编译接口变化，确保新生成算子项目能在最新 CANN 下正确编译（与兼容性矩阵中 26.1.x → CANN 9.1.0 的能力形成端到端闭环）。
- **msOpGen × MindStudio branding & pre-commit**（截断行）：仅可见前缀"Added support for MindStudio startu…"，后续完整内容未提供。

---

## 【公式解读】

**原文无公式**。本文档为版本说明性质文本，未包含任何 LaTeX 公式、伪代码公式或量化性能数学表达式。

---

## 【关联】

- **与 CANN 的依赖关系**：MindStudio 26.1.x 推荐基线为 CANN 9.1.0（见 Section 2 表 1），并向后兼容 9.0.0 与 8.5.0（见 Section 3 CANN 兼容矩阵）。msOpGen 的 Quick start 更新直接适配 "CANN 9.0.0 编译接口变化"，说明 CANN 升级是本版本算子工程链路的前置条件。

- **与 TorchNPU 的依赖关系**：MindStudio 26.1.x 推荐基线为 TorchNPU 26.1.0，并向后兼容 26.0.0 与 2.3.0（见 Section 3 TorchNPU 兼容矩阵），训练/推理场景的 PyTorch 适配器均受此矩阵约束。

- **与 Ascend HDK 的依赖关系**：MindStudio 26.1.x 推荐基线为 Ascend HDK 26.1.0，并向后兼容 26.0.RC1/25.7.RC1 与 25.5.x（见 Section 3 Ascend HDK 兼容矩阵）。HDK 决定固件/驱动版本，直接影响训练侧 HostBound、算子侧 Ascend 950 调测能力。

- **与 Ascend 950 硬件的关联**：Section 1 明示算子开发工具"为 Ascend 950 开发者重构算子全流程工具链"，从异常检测、问题调试、性能调优三维升级——这是本版本算子侧特性的最核心目标硬件。

- **msKPP ↔ msOpGen 的协同关系**：两个工具均围绕"统一构建入口 + 新统一构建镜像 + CI 版本号管理"形成同一工程化基线（见 Section 4 表格 msKPP 第 2、5 行与 msOpGen 第 2 行），意味着本版本在 CI/CD 流水线上对两类工具做了对齐改造。

- **训练工具 → 推理工具 → 算子工具的上下游串联**：训练侧聚焦强化学习、Agent 智能分析、HostBound 定位（输出待调优点）→ 推理侧四能力（精度采集/量化/仿真/建模）承接训练产出模型的部署诉求 → 算子侧（Ascend 950 三维升级）为前两者提供底层算子性能与正确性保障，形成"上层应用 → 中层部署 → 底层算子"的工具能力栈。

- **与"统一构建镜像"的内部关联**：msKPP 的"Unified build adaptation"与 msOpGen 的"Unified build promotion"均显式提及"新统一构建镜像"，表明本版本对外依赖一个统一的构建容器/镜像资产（具体名称未在本文档展开）。

> 备注：原文未提供文末内部链接清单（标注为"内部链接: (无)"），上述关联均基于文中显式出现的工具名、版本号、痛点描述推导。

---

## 【使用方法】

原文未给出面向最终用户的"启用命令/配置开关"形式的操作步骤。本版本涉及的是构建/安装/CI 流程改造，使用方式嵌入在工具行为变更中，主要可执行要点如下（均直接引自原文 Section 4 New Features 表格）：

- **生成 compile.json**：在 msKPP 构建过程中自动生成 `compile.json`，用于记录编译选项与依赖，可被性能分析工具链与 CI 工具链直接消费（无需用户手动启用，由构建脚本自动产出）。

- **接入统一构建入口**：使用 msOpGen 时以 `build.py` 作为正式统一构建入口（替代旧入口），子模块 checkout 自动固定到 pinned 版本；同步适配"新统一构建镜像"。

- **安装 msOpGen**：以 `entry_points` 方式安装（替代旧 `pip install`），安装前需注意 **自定义脚本中 `msopst.ini` 路径引用需更新为标准配置目录下的新路径**（破坏性变更）。

- **静态分析门禁**：msKPP 引入 `clang-tidy` 配置与 pre-commit 钩子，每次 commit 前自动执行静态分析；用户需在本地 git 仓库启用 pre-commit 框架以生效。

- **CI 版本号管理**：CI 流水线通过 git tag 派生发布版本号，确保"包版本"与"代码版本"一致（无需用户在 CI 脚本中手工指定版本号）。

- **受限环境部署**：msOpGen 安装阶段已关闭符号链接/文件属主/路径长度校验，可在受限容器/共享主机环境直接部署，无需手工绕过上述检查。

- **CANN 升级配合**：使用 msOpGen quick start 时，需确保 CANN 已升级至 9.0.0 及以上（对应编译接口），本版本完整推荐基线为 CANN 9.1.0。

- **快速定位兼容性**：参考 Section 3 三张兼容矩阵（MindStudio × CANN / TorchNPU / Ascend HDK）确认本机环境的组件组合是否在 `Y` 列内；`/` 表示不支持。

> 备注：原文未提供完整的 CLI 命令清单、环境变量清单或 YAML 配置示例（原文截断于 msOpGen 的 "MindStudio branding & pre-commit" 行，截断后续内容未提供），故无法列出更细粒度的启用命令。
