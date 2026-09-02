# 总体介绍

> 仓 `msmonitor` · 路径 `docs/zh/overview.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msmonitor/docs/zh/overview.md

# msMonitor 总体介绍文档 深度解读

---

## 【定位】

本文档是 msMonitor（MindStudio-Monitor）工具链的**总体介绍**，用以说明该工具的定位、核心组件、适用昇腾产品型号以及所提供的三大功能（`npu-monitor`/`nputrace`/`Monitor API`），是用户进入后续各子功能文档的总入口。

---

## 【技术要点】

- **工具定位**：msMonitor 是面向**昇腾集群场景**的**在线性能监测与动态采集**工具，基于 [dynolog](https://github.com/facebookincubator/dynolog)（Meta CPU-GPU 监控系统）与 [msPTI](https://gitcode.com/Ascend/mspti/blob/master/docs/zh/quick_start/mspti_quick_start.md)（MindStudio Profiler Tools Interface）构建。
- **核心组件三件套**：
  - `Dynolog daemon`：服务端守护进程，接收 `dyno` 请求并触发监测与采集。
  - `Dyno CLI`：客户端命令行入口，用于下发 `npu-monitor` 与 `nputrace` 命令。
  - `msPTI Monitor`：基于 msPTI 的采集模块，负责获取并上报性能数据。
- **三大功能能力**：
  - `npu-monitor`：轻量常驻后台，持续监测关键算子耗时。
  - `nputrace`：动态触发框架、CANN 与 Device 侧性能数据采集与解析，**无需中断任务运行**。
  - `Monitor API`：提供 Python 接口，覆盖计算类算子、通信类算子、API、Runtime API、Mstx 等性能数据。
- **框架联动**：支持 `Ascend PyTorch Profiler` 与 `MindSpore Profiler` 两种框架 Profiler 工具。
- **互斥约束**：`npu-monitor` 与 `nputrace` **不能同时开启**（受底层资源限制）。
- **产品支持**：覆盖昇腾 950PR&950DT、A3、A2、310B 系列；**不支持** 310P 与 910 系列。

---

## 【关键机制与数据】

- **工作原理（基于原文推断的架构）**：
  - 客户端 `Dyno CLI` → 通过 `dyno` 命令向服务端 `Dynolog daemon` 下发请求 → 服务端触发采集动作 → 由 `msPTI Monitor` 模块（基于 msPTI 接口）从框架/CANN/Device 侧获取性能数据 → 上报至监控端。
  - 原文图示（`figures/msMonitor.png`）描述了这一三组件协作结构，原文明确："msMonitor 核心组件如下"。
- **支持的采集层级**（来自功能介绍原文）：
  - 框架侧（Framework）：通过 `nputrace` 与 `Monitor API` 动态采集。
  - CANN 侧（异构计算架构）：通过 `nputrace` 触发采集。
  - Device 侧（昇腾 NPU 硬件）：通过 `nputrace` 触发采集。
  - 关键算子耗时：通过 `npu-monitor` 持续监测。
  - 计算类/通信类算子、API、Runtime API、Mstx：通过 `Monitor API` 采集。
- **关键事实**（原文）：
  - 原文："`npu-monitor`与`nputrace`不能同时开启"——这是**资源互斥**约束，非功能性建议。
  - 原文：`nputrace` "无需中断任务运行"——即**动态在线采集**能力。
  - 原文：`npu-monitor` 特征为 "轻量常驻后台"、"持续监测关键算子耗时"、"适合在线观察性能波动"。

> 说明：原文未给出任何具体性能数据（如采样频率、延迟、吞吐等）、资源占用数字或量化指标，故本节无具体数字。

---

## 【表格解读】

### 表格 1：msMonitor 核心组件表（原文逐字还原）

| 组件             | 作用                                                      | 文档                                        |
| ---------------- | --------------------------------------------------------- | ------------------------------------------- |
| `Dynolog daemon` | 服务端守护进程，负责接收dyno请求并触发监测与采集。        | [dynolog](./user_guide/dynolog_instruct.md) |
| `Dyno CLI`       | 客户端命令行入口，用于下发`npu-monitor`和`nputrace`命令。 | [dyno](./user_guide/dyno_instruct.md)       |
| `msPTI Monitor`  | 基于msPTI的采集模块，负责获取并上报性能数据。             | -                                           |

**逐行解读**：

- **`Dynolog daemon`**：作为**服务端**常驻进程，承担两个动作——**接收**（来自客户端的 `dyno` 请求）和**触发**（监测与采集动作）。该组件直接对接 Meta 开源的 dynolog 框架，并通过自有链接 `./user_guide/dynolog_instruct.md` 提供详细文档。
- **`Dyno CLI`**：定位为**客户端命令行入口**，动作是**下发命令**；可下发的命令集合为 `{npu-monitor, nputrace}` 两个，与文档表 2 中的功能一一对应。其详细文档指向 `./user_guide/dyno_instruct.md`。
- **`msPTI Monitor`**：定位为**采集执行模块**，依赖 msPTI（MindStudio Profiler Tools Interface）这一 MindStudio 自研接口实现，职责是**获取并上报**性能数据。原文此行"文档"列为 `-`，说明该组件在本文档层面**未提供独立使用文档**，需通过 msPTI 自身文档或 Monitor API 文档间接获取。

---

### 表格 2：产品支持情况表（原文逐字还原）

| 产品类型                                    | 是否支持 |
| ------------------------------------------- | :------: |
| 昇腾950PR&950DT系列产品                            |    √     |
| 昇腾A3系列产品 |    √     |
| 昇腾A2系列产品 |    √     |
| 昇腾310B系列产品 |    √     |
| 昇腾310P系列产品 |    ×     |
| 昇腾910系列产品 |    ×     |

**逐行解读**：

- **昇腾950PR&950DT系列产品**（√）：支持 msMonitor，是文档列出的**最新一代**支持产品。
- **昇腾A3系列产品**（√）：支持。
- **昇腾A2系列产品**（√）：支持。
- **昇腾310B系列产品**（√）：支持。
- **昇腾310P系列产品**（×）：**不支持**。用户在 310P 硬件上无法使用 msMonitor，需注意工具链兼容性问题。
- **昇腾910系列产品**（×）：**不支持**。这是早期昇腾训练主力芯片但不在 msMonitor 支持矩阵内，意味着 910 系列用户需使用其他监控手段。

> 原文以"说明"形式提示：昇腾产品的具体型号请参见《昇腾产品形态说明》外链，本文不展开。

---

### 表格 3：msMonitor 核心功能表（原文逐字还原）

| 功能名称        | 功能简介                                                     | 文档                                                  |
| --------------- | ------------------------------------------------------------ | ----------------------------------------------------- |
| **npu-monitor** | 轻量常驻后台，持续监测关键算子耗时，适合在线观察性能波动。   | [npu-monitor](./user_guide/npumonitor_instruct.md)    |
| **nputrace**    | 动态触发框架、CANN和Device侧性能数据采集与解析，无需中断任务运行。 | [nputrace](./user_guide/nputrace_instruct.md)         |
| **Monitor API** | 提供Python接口，采集计算类算子、通信类算子、API、Runtime API、Mstx等性能数据。 | [Monitor API](./advanced_features/monitor_feature.md) |

**逐行解读**：

- **`npu-monitor`**：定位为**持续性、轻量级**监控手段，"常驻后台"说明其进程模型是**长期运行**；监测对象是**关键算子耗时**；典型场景是**在线观察性能波动**（即趋势监控而非深度剖析）。详细文档位于 `./user_guide/npumonitor_instruct.md`。
- **`nputrace`**：定位为**动态、按需**触发型采集，覆盖**三层数据源**——框架（Framework）、CANN（昇腾异构计算架构）、Device（昇腾 NPU 设备硬件）；关键特性是**无需中断任务运行**，即可完成采集与解析（即**在线采集**）。详细文档位于 `./user_guide/nputrace_instruct.md`。
- **`Monitor API`**：定位为**编程式接入**，形态是 **Python 接口**；可采集的指标范围最广，覆盖：①**计算类算子**、②**通信类算子**、③**API**（一般指算子调用接口）、④**Runtime API**（运行时接口）、⑤**Mstx**（MindSpore Training Extensions，性能标注工具）。详细文档位于 `./advanced_features/monitor_feature.md`，归类于"advanced_features"目录下，区别于"user_guide"目录中的另两项，体现其属于高级用法。

---

## 【公式解读】

**原文无公式**。

---

## 【关联】

文档位于 `docs/zh/overview.md`，作为总入口文档，通过表格"文档"列建立了清晰的**功能 → 文档**导航关系；同时表格中也通过"组件 → 文档"建立了**架构 → 实现**映射。以下是文档内/外关联的全景：

### 上游依赖（外部项目）

- **[dynolog](https://github.com/facebookincubator/dynolog)**：Meta 开源的 CPU-GPU 监控系统，是 `Dynolog daemon` 与 `Dyno CLI` 的**直接上游**——msMonitor 的服务端-客户端架构、命名（`dyno`）均直接复用 dynolog 的范式。
- **[msPTI](https://gitcode.com/Ascend/mspti/blob/master/docs/zh/quick_start/mspti_quick_start.md)**：MindStudio Profiler Tools Interface，是 `msPTI Monitor` 组件与 `Monitor API` 性能数据采集能力的**底层接口依赖**。

### 框架层联动（下游框架 Profiler）

- **[Ascend PyTorch Profiler](https://gitcode.com/Ascend/pytorch/blob/master/docs/zh/developer_notes/ascend_pytorch_profiler_user_guide.md)**：在 PyTorch 框架下与 msMonitor 配合使用的 Profiler。
- **[MindSpore Profiler](https://gitcode.com/Ascend/docs/blob/master/MindStudio/master/zh/menu/mindspore_profiler_user_guide.md)**：在 MindSpore 框架下与 msMonitor 配合使用的 Profiler。

> 原文通过"支持的框架Profiler工具"段落建立了 msMonitor ↔ 框架 Profiler 的**上下游协作关系**：框架 Profiler 通常消费 msMonitor 采集到的 trace/profile 数据，进行可视化分析。

### 内部子文档（本文档的下一级跳转目标）

- `./user_guide/dynolog_instruct.md` → 对应 **Dynolog daemon 服务端**详细用法。
- `./user_guide/dyno_instruct.md` → 对应 **Dyno CLI 客户端**详细用法。
- `./user_guide/npumonitor_instruct.md` → 对应 **npu-monitor 功能**详细用法（持续监测）。
- `./user_guide/nputrace_instruct.md` → 对应 **nputrace 功能**详细用法（动态采集）。
- `./advanced_features/monitor_feature.md` → 对应 **Monitor API 功能**详细用法（Python 接口采集）。

### 功能之间的关联（互斥约束）

- `npu-monitor` ⇄ `nputrace`：**互斥**，不能同时启用（受底层资源限制，原文 NOTE 明确说明）。
- `npu-monitor` / `nputrace` ⇄ `Monitor API`：原文**未明确**关系，但从组件视角，`Monitor API` 走 msPTI Monitor 独立通道，与 `Dyno` 下发的两条命令可能独立使用，亦可能共享底层资源，原文未给出约束说明。

### 硬件平台关联

- msMonitor 与昇腾产品形态强相关，详情需参见外链《昇腾产品形态说明》。本文档通过表格 2 明确了支持/不支持的产品系列，作为软硬件配套依据。
- 不支持的产品（310P/910）用户**无法使用** msMonitor，需考虑替代方案——原文未涉及替代方案，需用户自行查阅其他工具链。

### 图片资源

- `figures/msMonitor.png`：原文配图，描绘 msMonitor 整体架构（`Dynolog daemon` / `Dyno CLI` / `msPTI Monitor` 三组件与外部 Profiler 的协作关系），是本文档核心视觉资源。

---

## 【使用方法】

**原文未涉及具体启用方式、配置项或命令**。

本文档仅作为**总体介绍**，仅在表格"文档"列中通过链接指向以下详细使用文档：

| 详细文档路径                          | 适用对象                                |
| ------------------------------------- | --------------------------------------- |
| `./user_guide/dynolog_instruct.md`    | Dynolog daemon 服务端的使用与配置       |
| `./user_guide/dyno_instruct.md`       | Dyno CLI 客户端命令的使用               |
| `./user_guide/npumonitor_instruct.md` | `npu-monitor` 功能的使用方法            |
| `./user_guide/nputrace_instruct.md`   | `nputrace` 功能的使用方法               |
| `./advanced_features/monitor_feature.md` | `Monitor API`（Python 接口）的使用方法   |

> 用户如需了解**如何安装、启动、配置 msMonitor 或其各子功能**，需跳转至上述对应子文档。本文**未涉及**命令行示例、配置参数、环境变量、启动脚本等内容。

## 图文联合解读

- `msMonitor.png`: **图文联合解读：**

图示msMonitor多节点集群架构：Node X的Dyno CLI经RPC下发至Dynolog daemon，daemon通过Ctrl IPC控制各节点Train/InferProcess，并经Ctrl触发MSPTI Monitor；Process将trace dump写入本地/NFS存储，daemon汇聚Data IPC后以Metric log对接Prometheus/TensorBoard等Consumer。

**与文档关系**：论证"控制-数据分离、多节点协同"的设计结论，呼应文档对Dynolog daemon（服务端）、Dyno CLI（客户端）、msPTI Monitor（采集模块）三组件职责的划分。
