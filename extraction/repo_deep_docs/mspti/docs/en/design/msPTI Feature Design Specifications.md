# msPTI Feature Design Specifications

> 仓 `mspti` · 路径 `docs/en/design/msPTI Feature Design Specifications.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mspti/docs/en/design/msPTI Feature Design Specifications.md

# msPTI Feature Design Specifications 深度解读

## 【定位】

本文档定义了 **msPTI（MindStudio Profiling Tools Interface）对 CANN Runtime APIs 采集能力的扩展设计规格**：通过新增 `msptiActivityEnable(msptiActivityKind kind)` 接口，使 msPTI 能够采集 CANN Runtime 层 API 的调用与耗时统计，从而辅助用户对 host-bound 服务类进程进行 CANN API 性能分析。

---

## 【技术要点】

1. **msPTI 定位与能力**：msPTI 是 MindStudio 面向 Ascend 设备提供的 profiling 通用 API，能力覆盖两类——**Tracing**（采集 CANN 活动的时间戳与附加信息，如 CANN APIs、Kernels、Memory Copy）与 **Profiling**（采集一个或一组 Kernel 的 NPU 性能指标）。基于其开发的 profiling 工具可复用于推理与训练场景下的多种框架。

2. **本次扩展目标**：在 msPTI 已有外置 API 采集基础上，新增 **CANN Runtime APIs 采集能力**，由 `msptiActivityEnable(msptiActivityKind kind)` 启用 runtime API 数据采集，再通过 **callback API** 拉取 runtime API 数据。

3. **目标版本与归属**：Target Version 为 **MindStudio 26.0.0**；SIG group 为 **mstt-sig**；设计者 chenhao；文档日期 2026.01.21；遵循 CC BY-SA 4.0 开源许可。

5. **硬件支持矩阵**（原文 2.3.1 节）：
   - Ascend 950PR&950DT：√
   - Ascend A3：√
   - Ascend A2：√
   - Ascend 310B：√
   - Ascend 310P：×
   - Ascend 910：×

6. **软件约束**（原文 2.3.2 节）：操作系统 **Linux**；编程语言 **C / Python**。

7. **Profiling 总体方案**（原文 3.2 节）：系统侧对关键函数、关键算子与通信进行耗时测量→数据落盘→离线解析→可视化呈现。

8. **DFX 关键设计**：
   - **性能影响**：仅做 API 类型启用与获取，运行时 API 数量可控，性能影响有限（原文 4.6.1）。
   - **资源管理**：开启的 runtime API 使用**用户传入的内存**，用户可控制申请内存大小；msPTI 数据在内存中统一管理，**磁盘 I/O 是用户消费数据后的后处理**，需考虑消费频率（原文 4.6.4）。
   - **升级/裁剪/安全**：均明确"不涉及"或"无影响"（原文 4.6.2、4.6.5、4.6.7）。

---

## 【关键机制与数据】

- **工作原理（原文 4.1、4.5）**：msPTI 通过调用 `msptiActivityEnable(msptiActivityKind kind)` 启用 runtime API 数据采集能力；通过 **callback API** 取得 runtime API 数据。整体上属于"启用开关 → 回调拉取"的轻量级接入模式。
- **场景触发条件（原文 2.2）**：针对 **host-bound 服务进程**，当用户需要分析 CANN Runtime 侧 API 性能、获取并分析 API 耗时。
- **性能影响数据**：原文未给出具体数字；定性描述为"影响有限，仅做启用与获取，运行时 API 数量可控"。
- **资源管理机制**：内存由用户侧控制容量大小，msPTI 侧统一管理内存中的数据；磁盘写盘延后到用户消费数据之后进行——属于"先内存缓冲、后异步落盘"的解耦设计。

---

## 【表格解读】

### 表格 1：Feature Requirement List（原文 §1.2）

| Requirement No. | Requirement | Feature Description | Remarks |
|---|---|---|---|
| 1 | Supports the collection capability of CANN Runtime APIs. | Collects statistics on API calls and time consumption at the runtime level. | （空） |

**逐行解读**：本表仅列一条需求——支持 CANN Runtime APIs 的采集能力（需求编号 1），其功能描述聚焦于"Runtime 层 API 调用与耗时统计"，Remarks 列空。该表是整篇 design 唯一的需求基线，后续 §4 的"Supports the collection capability of CANN Runtime APIs"即对应此条需求的具体实现。

### 表格 2：Hardware Restrictions（原文 §2.3.1）

| Product Type | Supported |
|---|:---:|
| Ascend 950PR&950DT Products | √ |
| Ascend A3 Products | √ |
| Ascend A2 Products | √ |
| Ascend 310B Products | √ |
| Ascend 310P Products | × |
| Ascend 910 Products | × |

**逐行解读**：
- **Ascend 950PR&950DT**：支持，覆盖最新一代训练/推理产品；
- **Ascend A3**：支持，覆盖 Atlas A3 系列；
- **Ascend A2**：支持，覆盖 Atlas A2 系列；
- **Ascend 310B**：支持，覆盖 Atlas 300I 推理卡；
- **Ascend 310P**：**不支持**；
- **Ascend 910**：**不支持**，意味着早期训练主力芯片不在本次扩展的覆盖范围内。
该矩阵是用户判断能否在自有硬件上启用该特性的依据。

### 表格 3：Security Design Confirmation Checklist（原文 §4.6.7.1）

| Security Attribute | Check Item | Description | Involved or Not |
|---|---|---|---|
| Access channel control | Whether any listening port is added | 若新增监听端口，更新通信矩阵 | No |
| Access channel control | Whether any process or inter-component communication method is added | 若新增进程或组件间通信方式，更新通信矩阵 | No |
| Access channel control | Whether any authentication mode is added | 若新增认证方式，更新通信矩阵与产品文档 | No |
| Permission control | Whether any file or directory needs to be created | 若需新建文件/目录，明确访问权限 | No |
| Permission control | Whether the account permission meets the principle of least privilege | 按最小权限分配账号 | No |
| Permission control | Whether user privilege escalation exists | 禁止用户提权 | No |
| Undisclosed interface | Whether any GUC parameter is added | 若新增 GUC 参数，更新产品文档 | No |
| Undisclosed interface | Whether any function, view, or system table is added or modified | 若新增/修改，需更新文档与权限策略 | No |
| Undisclosed interface | Whether any SQL syntax is added | 若新增 SQL 语法，更新文档并加入审计日志 | No |
| Undisclosed interface | Whether …（原文末尾被截断）| — | — |

**逐行解读**：此为安全设计 Checklist 确认表。每条 Check Item 的"Description"列说明若命中应执行的安全动作（更新通信矩阵、文档、权限或审计）。本特性在所有已列出检查项上 **Involved = No**，意味着本次扩展**未引入新的监听端口、进程间通信、认证方式、文件/目录、提权路径、GUC 参数、函数/视图/系统表、SQL 语法**等，安全面无新增暴露点。最后一行原文被截断，仅保留 "Whet" 字段头，无法进一步解读。

---

## 【公式解读】

**原文无公式**。

---

## 【关联】

原文未提供内部链接（文档结尾未列出任何跨章节或跨模块链接）。从内容上下文可推断以下关系：

- **Tracing 能力（§1.1）** ←→ **本次 Runtime API 扩展（§4）**：本次扩展是 msPTI Tracing 能力矩阵中 CANN Runtime APIs 一项的实现落地，依赖 `msptiActivityEnable` 与 callback API 这套已有 Tracing 接口机制。
- **Activity APIs / Callback APIs（§1.1）** ←→ **`msptiActivityEnable(msptiActivityKind kind)`（§4.4）**：本次新增的 kind 参数是 Activity API 体系的扩展点，callback API 是数据消费通道。
- **Profiling 总体方案（§3.2）** ←→ **DFX 资源管理（§4.6.4）**：§3.2 描述的"测量 → 落盘 → 离线解析 → 可视化"流程中，落盘动作受 §4.6.4 的"内存缓冲 + 用户消费后异步 I/O"策略约束。
- **硬件支持矩阵（§2.3.1）** ←→ **软件约束（§2.3.2）**：硬件层决定可用性（Ascend 910/310P 不可用），OS/语言层决定可编程性（仅 Linux + C/Python）。

---

## 【使用方法】

- **启用入口**：调用 **`msptiActivityEnable(msptiActivityKind kind)`** 启用 CANN Runtime API 数据采集（原文 §4.1、§4.4、§4.5）。
- **数据获取**：通过 **callback API** 取得 runtime API 数据（原文 §4.1、§4.5）。
- **前置条件**：
  - 操作系统须为 Linux（原文 §2.3.2）；
  - 应用须运行于支持的 Ascend 产品（950PR/950DT、A3、A2、310B，原文 §2.3.1）；
  - 编程语言限于 C / Python（原文 §2.3.2）。
- **资源配置**：用户自行控制申请内存大小，msPTI 在该内存中统一管理采集数据；磁盘落盘于用户消费数据之后进行，可调节消费频率（原文 §4.6.4）。
- **典型使用流程**（按原文 §2.2、§3.2 综合）：在 host-bound 服务进程中识别待分析的 CANN Runtime API → 启用采集并注册回调 → 程序运行期间收集耗时 → 消费内存中的数据 → 离线解析与可视化展示。

> 原文未涉及具体的 CLI 命令、配置项清单、参数取值表或 API 完整签名，启用方式以上述原则性描述为准。
