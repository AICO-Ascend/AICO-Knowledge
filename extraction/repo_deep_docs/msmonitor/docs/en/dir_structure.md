# Project Directory

> 仓 `msmonitor` · 路径 `docs/en/dir_structure.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msmonitor/docs/en/dir_structure.md

# msmonitor 项目目录结构文档一体化深度解读

---

## 【定位】

这篇文档解决的是 msmonitor 项目的**整体代码仓库布局与模块划分认知问题**——为开发者提供一张完整的"项目地图"，使其在不阅读源码的情况下即可了解项目的文档位置、核心代码模块（dynolog_npu、plugin）、构建/测试脚本组织、第三方依赖存放方式以及顶层元信息文件（LICENSE、README、第三方开源声明）的分布。

---

## 【技术要点】

1. **文档体系集中化**：所有文档（英文版）统一收纳在 `docs/en/` 下，覆盖目录结构、客户端/服务端使用说明、安装指南、FAQ、适配器说明、漏洞处理流程、公开 IP 描述、安全声明等共 **10 个文档条目**（不含 `figures` 资源目录）。
2. **双模块代码组织**：项目代码按功能划分为两个独立模块——`dynolog_npu`（对应动态日志/采集核心）与 `plugin`（插件机制，含 IPC 监控相关代码），二者各自拥有 `CMakeLists.txt` 与 `cmake/` 配置目录，可独立编译。
3. **dynolog_npu 子结构**：该模块包含 `cli/src`（dyno 客户端源码）、`dynolog/src`（dynolog 服务端源码）以及 `scripts/rpm/`（RPM 打包文件），呈现出**客户端-服务端双端 + 打包脚本**的三段式布局。
4. **plugin 子结构**：包含 `IPCMonitor`（Python 模块）、`ipc_monitor`（核心代码）、`stub`、`third_party`（第三方依赖库），体现出**Python 封装层 + C/C++ 核心层 + 桩函数 + 第三方库**的典型混合语言插件架构。
5. **脚本与测试分离**：`scripts/` 目录集中放置 5 个构建与维护脚本（`apply_dyno_patches.sh`、`build.sh`、`gen_dyno_patches.sh`、`run_st.sh`、`run_ut.sh`），而测试代码本身位于 `test/` 下，分为 `st/`（系统测试）与 `ut/`（单元测试）两级。
6. **第三方依赖隔离**：顶层 `third_party/` 仅依赖 `dynolog` 一个第三方项目；plugin 模块内部另有 `third_party` 子目录，说明**依赖管理采用就近原则**，避免污染全局。

---

## 【关键机制与数据】

原文为项目结构展示，未涉及运行时的工作原理、数据流或性能数据。本节仅能根据目录结构推断出的"组织机制"做以下标注：

- **原文：模块独立性** —— 两个核心模块（`dynolog_npu`、`plugin`）各自具备完整的 `CMakeLists.txt` + `cmake/` 配置，可独立构建，体现了 CMake 多子项目（subdirectory）的模块化机制。
- **原文：文档与代码解耦** —— 文档全部在 `docs/en/` 下，使用 .md 格式；代码模块在顶层平铺，便于文档版本与代码版本通过 Git 分开管理。
- **原文：RPM 打包链路** —— `dynolog_npu/scripts/rpm/` 表明项目支持通过 RPM 包形式发布，是昇腾/MindStudio 生态常见的部署形态。
- **原文：补丁机制** —— `scripts/` 下同时存在 `gen_dyno_patches.sh` 与 `apply_dyno_patches.sh`，说明 dyno 客户端可能通过补丁方式与上游 dynolog 项目对接，而非直接合并源码。

> 性能数据、运行时数据流、调用链等内容**原文未涉及**。

---

## 【表格解读】

原文无表格。

---

## 【公式解读】

原文无公式。

---

## 【关联】

根据文档中的目录命名，可推断出 msmonitor 项目内部存在以下文档/模块间的引用关系（原文以目录条目形式列出，未给出超链接，但目录名即线索）：

| 目录条目（原文） | 对应能力/上游下游关联 |
|---|---|
| `dyno_instruct.md` | `dynolog_npu/cli/src` 的客户端（dyno）使用说明 |
| `dynolog_instruct.md` | `dynolog_npu/dynolog/src` 的服务端（dynolog）使用说明 |
| `npumonitor_instruct.md` | NPU 监控工具使用说明（与 `plugin/` 中 NPU 相关监控模块相关） |
| `nputrace_instruct.md` | NPU trace 抓取工具说明 |
| `mindspore_adapter_instruct.md` | MindSpore 框架适配器使用说明（说明 msmonitor 提供 MindSpore 适配能力） |
| `install_guide.md` | 安装指南，对应 `scripts/build.sh` 的产物及 RPM 打包路径 |
| `faq.md` | 综合 FAQ，涵盖前述所有工具的常见问题 |
| `mindstudio_vulnerability_handling_procedure.md` | 漏洞处理流程，属于治理类文档 |
| `security_statement.md` | 安全声明，与 `LICENSE` 和 `Third_Party_Open_Source_Software_Notice` 共同构成合规体系 |
| `public_ip_address.md` | 描述外部可访问的 IP（部署相关） |
| `apply_dyno_patches.sh` / `gen_dyno_patches.sh` | 客户端与服务端之间的补丁同步机制 |
| `third_party/dynolog` | 外部 dynolog 项目，作为 dynolog_npu 的上游依赖 |

> 注：原文给出的"内部链接"字段标注为"(无)"，故上述关联全部基于**目录命名语义推断**，并非原文显式提供的链接。

---

## 【使用方法】

原文未涉及具体的启用方式、配置项或命令。本文档为**目录结构概览**，仅描述"仓库内有哪些文件/目录"，不包含任何运行、配置或调用命令。

如需获取具体使用方法，可按文档中列出的对应说明文件查阅，例如：

- 安装流程 → 参考 `docs/en/install_guide.md`
- 构建命令 → 原文中仅提及 `scripts/` 下存在 `build.sh`、`run_st.sh`、`run_ut.sh` 等脚本文件名，**具体命令参数原文未涉及**
- 客户端/服务端使用 → 参考 `dyno_instruct.md` 与 `dynolog_instruct.md`（原文未列出具体命令）
