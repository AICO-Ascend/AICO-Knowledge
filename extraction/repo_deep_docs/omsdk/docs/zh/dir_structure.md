# 全量目录层级

> 仓 `omsdk` · 路径 `docs/zh/dir_structure.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/omsdk/docs/zh/dir_structure.md

# omsdk 仓库 `docs/zh/dir_structure.md` 深度解读

## 【定位】

本文档系统描述了 **om-sdk 项目仓库的全量目录层级结构**,以树状图形式呈现项目根目录与各子目录、模块、子仓的从属关系,作为开发者理解项目布局与代码组织方式的导航性参考。

## 【技术要点】

- **三层顶层结构**:项目根目录下设三大主目录 ——`build`(构建相关)、`docs`(文档,内含 `zh` 中文文档子目录)、`src`(源码)。
- **双组件源码主线**:`src/` 下分为两条组件分支 ——`om`(OM SDK 组件代码)与 `om-web`(OM Web 前端组件代码),二者并列独立。
- **OM SDK 子模块划分**:`src/om/` 内含 `build`、`config`、`doc`、`output`、`platform`、`src/app`、`test/python` 共 7 个子目录,覆盖构建、配置、文档、输出、平台、应用、测试全流程。
- **平台模块双轨制**:`src/om/platform/` 下同时存在 `cpp`(C++ 平台代码)与 `MindXOM_SDK`(MindXOM SDK 子仓)两个子模块,体现 C++ 原生平台与 MindX 平台抽象的并存。
- **OM Web 前端结构**:`src/om-web/` 下含 `build`、`public`(含 `config` 与 `WhiteboxConfig` 白盒配置)、`src`(含 `api`、`assets`、`components`、`router`、`utils`、`views` 共 6 个子目录)、`test`(含 `DT`、`reports`、`src` 共 3 个子目录)。
- **测试分层组织**:OM SDK 的测试以 Python 为主(`test/python`),OM Web 的测试细分为 DT 测试、测试报告、测试源码三类。

## 【关键机制与数据】

原文为描述性目录结构说明,**未涉及工作原理、数据流、性能数据、运行参数或量化指标**。

原文给出的组织范式可概括为:「**根目录 → 三大子目录(build / docs / src)→ 源码按 om 与 om-web 两条主线展开 → 各主线内部按 功能维度(build/config/doc/output/platform/src/test)横向切分**」。

## 【表格解读】

原文无 markdown 表格。原文以 ` ```text ` 代码块形式呈现一棵 ASCII 目录树(非表格结构),完整罗列了从 `om-sdk` 根目录到最深层子目录的层级路径与注释。该代码块作为纯文本可视化,不构成表格行列语义。

## 【公式解读】

原文无公式。

## 【关联】

根据目录结构可推断的模块关联:

- **`src/om/`** 与 **`src/om-web/`** 为并列关系:前者为 OM SDK 核心组件(后端/平台层),后者为 OM Web 前端组件,二者共同构成完整的边缘 AI 业务管理与边云协同框架。
- **`src/om/platform/MindXOM_SDK`** 以独立子仓形式存在,表明 MindXOM 平台能力通过子仓方式集成,可能由独立仓库管理并以子模块方式引入。
- **`src/om/src/app`** 作为应用程序目录,是 OM SDK 能力的实际承载入口;`src/om-web/src/api` 作为 API 接口目录,应承担与 OM SDK 后端对接的职责。
- **`docs/zh/`** 与 **`src/om/doc/`** 各自独立维护文档,前者为仓库级说明文档,后者为 SDK 组件内部文档。

原文未提供内部链接信息。

## 【使用方法】

原文未涉及。本文为目录结构说明文档,不含启用方式、配置项、命令或调用示例。
