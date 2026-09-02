# 全量目录层级

> 仓 `mef` · 路径 `docs/zh/dir_structure.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mef/docs/zh/dir_structure.md

# 一体化深度解读：mef 项目「全量目录层级」文档

## 【定位】

本文档是 mef（边云协同平台）项目的**代码仓库全量目录结构导航图**，用于让开发者/使用者快速定位源码模块、文档位置与构建产物所在的物理路径，为后续阅读源码、构建项目、定位模块职责提供唯一的目录蓝图。

## 【技术要点】

- **顶层三目录划分**：项目根目录下仅包含 `build`（构建相关目录）、`docs`（文档目录）、`src`（源码目录）三个一级子目录，呈"构建/文档/源码"三段式布局。
- **`common-utils` 公共工具库聚合 20+ 子模块**：在 `src/common-utils` 下集中了 `backuputils`（备份）、`cache`（缓存）、`checker`（校验）、`cmsverify`（CMS 验证）、`database`（数据库）、`envutils`（环境变量）、`fileutils`（文件）、`httpsmgr`（HTTPS）、`hwlog`（日志）、`k8stool`（K8s）、`kmc`（KMC）、`limiter`（限流）、`logmgmt`（日志管理）、`modulemgr`（模块管理）、`rand`（随机数）、`terminal`（终端）、`test`（测试）、`tls`（TLS）、`utils`（通用工具）、`websocketmgr`（WebSocket）、`x509`、`xcrypto`（加密）等工具，覆盖基础设施、安全、网络、运行时管理多个维度。
- **三大业务组件并列**：`src` 下并列 `device-plugin`（设备插件组件）、`mef-center`（中心组件）、`mef-edge`（边缘组件），构成"中心—边缘—设备插件"的端边云三层架构物理映射。
- **`mef-center` 内部 8 个子模块**：包括 `alarm-manager`（告警）、`cert-manager`（证书）、`common`（公共）、`edge-manager`（边缘管理）、`mef-center-install`（安装）、`nginx-manager`（Nginx）、`opensource`（开源组件）、`platform`（平台模块）。
- **`mef-edge` 嵌套 6 个子模块**：`edge-installer` 下含 `build`（构建）、`cmd`（主程序入口）、`config`（配置）、`pkg`（主程序代码）、`script`（脚本）、`tool`（工具），其中 `cmd/pkg/config` 是典型 Go 语言项目布局。
- **`device-plugin` 极简三段式**：仅含 `build`（构建目录）、`doc`（文档）、`pkg`（主程序代码），结构精简。

## 【关键机制与数据】

本文档为纯静态目录树展示，**未涉及**任何工作原理、数据流、性能指标或运行时机制描述，因此无可标注的"原文: 数字/参数"。其唯一传达的信息是：**项目以源码中心化方式组织，工具能力下沉到 `common-utils`，业务能力按"中心 / 边缘 / 设备插件"三端物理隔离部署**。

## 【表格解读】

**原文无表格**。原文档全部内容为一个 `text` 代码块包裹的 ASCII 目录树，未呈现任何结构化表格（参数表/性能对比表/配置项表均不存在）。

## 【公式解读】

**原文无公式**。文档不涉及任何数学公式、算法伪代码或计算表达。

## 【关联】

由于文末内部链接信息标注为"（无）"，本节仅基于目录结构本身推断上下游/横向模块关系：

- **`common-utils` 与三大业务组件的横向依赖**：`common-utils` 下 20+ 工具子模块（如 `hwlog`、`x509`、`tls`、`xcrypto`、`k8stool`、`limiter`、`modulemgr`）按命名规律推断，会被 `mef-center`、`mef-edge`、`device-plugin` 三者共用，作为底座能力下沉层；其中 `mef-center` 自带 `common` 子模块，构成"项目级公共 + 中心级公共"的双层复用结构。
- **`mef-center` ↔ `mef-edge` 跨端协作**：`mef-center` 内含 `edge-manager`（边缘管理器），与 `src/mef-edge`（边缘组件代码）形成"中心管理边缘"的对应关系；`mef-center-install` 与 `mef-edge/edge-installer`（边缘组件目录）则分别为"中心安装器"与"边缘安装器"，构成两端各自的部署入口。
- **安全/证书链路贯穿**：`common-utils/cmsverify` + `common-utils/x509` + `common-utils/xcrypto` + `common-utils/tls` + `mef-center/cert-manager` 形成端到端的证书与加解密支撑链。
- **构建体系全覆盖**：根级 `build`、`src/common-utils/build`、`src/device-plugin/build`、`src/mef-center/build`、`src/mef-edge/build`、`src/mef-edge/edge-installer/build` 共 6 处 `build` 目录，对应"根构建 + 各组件独立构建 + 嵌套子组件构建"的分层构建矩阵。
- **文档体系集中化**：所有文档收敛在 `docs/` → `docs/zh/`（中文文档目录）下，`src/device-plugin/doc` 是唯一非 `docs/` 路径下的文档目录，构成"集中文档 + 组件就近文档"的双轨结构。

## 【使用方法】

**原文未涉及**。本文档仅展示目录树本身，未给出任何启用方式、配置项、命令、编译指令或部署步骤的说明。
