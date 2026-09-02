# Introduction<a name="ZH-CN_TOPIC_0000001722295433"></a>

> 仓 `mef` · 路径 `docs/en/user_guide/introduction.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mef/docs/en/user_guide/introduction.md

# MEF 介绍文档一体化深度解读

## 【定位】

本文档是 MEF（轻量化端边云协同使能框架）的总览型介绍文档，旨在从背景动因、产品定义、产品价值、系统架构、应用场景、集成流程及软硬件兼容性等维度，向系统管理员与集成开发者阐明 MEF 是什么、解决什么边云协同管理问题、以及如何纳入既有 ISV 业务体系。

---

## 【技术要点】

1. **产品定位**：MEF 是面向集成的轻量化端边云协同使能框架，隶属 Ascend 推理解决方案，专用于智能边缘设备使能，提供边缘节点管理与智能推理服务（容器化应用）管理两大能力。
2. **两段式部署**：
   - **MEF Center**：部署于通用服务器，负责边缘节点的批量管理、服务部署和系统监控，对外提供 RESTful 接口。
   - **MEF Edge**：部署于智能边缘设备，负责与中心网管系统对接、完成容器化推理服务的部署与管理、为算法应用提供服务。
3. **架构底座依赖**：MEF 依托开源系统 **KubeEdge** 建立并管理 MEF Center 与 MEF Edge 之间的控制链路；MEF Center 模块包含 APIG（API Gateway）、edge-manager、cert-manager、alarm-manager；MEF Edge 模块包含 edge-om、edge-main、EdgeCore（KubeEdge 的边缘侧组件）、Device-Plugin（昇腾 NPU 设备发现插件）。
4. **边云协同与北向集成**：通过 MEF Edge 与 MEF Center 集成实现边云协同；通过北向接口与 ISV 业务平台对接，进行边缘节点与容器化应用管理。
5. **离线自治能力**：当 MEF Edge 所在边缘节点与 MEF Center 所在中心节点之间的链路中断时，边缘节点上的推理服务不会被中断；若边缘节点重启，重启完成后推理服务可自动恢复。
6. **集成与对接流程**：云边协同流程主要包括三步——安装 MEF（分为 MEF Center 与 MEF Edge 的准备与安装）、MEF 二次开发与集成、通过 ISV 业务平台对边缘节点和容器化应用进行管理。

---

## 【关键机制与数据】

**控制链路机制（原文）**：MEF relies on the open-source system KubeEdge to establish and manage the control link between MEF Center and MEF Edge.
- 即：中心–边缘控制链路由 KubeEdge 提供，MEF 自身只负责业务层封装。

**北向接口机制（原文）**：MEF Center provides RESTful interfaces for users, which can be integrated and called by other third-party applications.
- 即：第三方通过调用 MEF Center 的 RESTful 接口来访问服务。

**MEF Edge 消息流（原文）**：MEF Edge primarily receives messages from MEF Center and collects and forwards relevant information to MEF Center, enabling functions such as software installation and upgrade, and full lifecycle management of containerized applications.
- 即：边到云是「消息接收 + 本地信息采集上行」，云到边是「指令下发驱动安装/升级」。

**离线自治机制（原文）**：When the link between the edge node where MEF Edge resides and the central node where MEF Center resides is interrupted, the inference service on the edge node is not interrupted; if the edge node restarts, the inference service can automatically recover after the edge node restart is complete.
- 即：链路中断不影响在边推理；边缘重启后推理服务可自恢复。

**应用形态（原文）**：User applications are published as container images, and MEF manages these containerized application images, covering functions such as adding, deleting, modifying, and querying containerized applications.
- 即：用户应用以容器镜像方式发布，MEF 全生命周期管理。

> 注：原文无任何具体性能数据（如时延、吞吐、并发上限等数字）出现于本总览文档中。

---

## 【表格解读】

### 表 1：产品价值（Product Value）

| Plane | Product Value |
|--|--|
| Service Plane | MEF features an open ecosystem and full-stack enablement, facilitating integration and lowering the barrier to entry for users. |
| Management Plane | MEF is extremely simple and easy to use, secure, and reliable. |

**解读**：
- **Service Plane（业务面）**：强调 MEF 走开放生态 + 全栈使能路线，目的是降低用户集成与接入门槛。
- **Management Plane（管理面）**：强调运维侧体验——简洁易用、安全可靠。
- 两行分别对应"对外赋能"与"对内管控"两条价值主张，构成产品对外宣传的双轴定位。

---

### 表 2：MEF Center 模块说明（MEF Center module description）

| Module | Module Function |
|--|--|
| APIG (API Gateway) | Provides bidirectional authentication and RESTful interfaces for ISV business platforms. Used by ISV business platforms to invoke and use services provided by MEF Center. |
| edge-manager | Edge node management module and containerized application management module. Manages edge node access and containerized applications running on nodes. |
| cert-manager | Certificate management module. Used for unified management of internal and external certificates used by MEF. |
| alarm-manager | Alarm management module. Used to manage alarms and events for MEF Edge and MEF Center. |

**解读**：
- **APIG**：唯一面向 ISV 的入口组件，承担双向认证 + RESTful 接口暴露，是北向集成的"门面"。
- **edge-manager**：核心业务模块，同时管"节点"和"节点上的容器化应用"，对应产品定义中两大主能力。
- **cert-manager**：统一管理 MEF 内部与外部证书，配合 APIG 的双向认证，支撑管理面"安全可靠"价值。
- **alarm-manager**：统一汇总 MEF Edge 与 MEF Center 自身的告警与事件，是管理面"易用、可观测"的实现。

---

### 表 3：MEF Edge 模块说明（MEF Edge module description）

| Module | Module Function |
|--|--|
| edge-om | Main process module, including the upgrade module, etc. |
| edge-main | Process module for interfacing MEF Edge and MEF Center. |
| EdgeCore | The edge-side component of the open-source system KubeEdge. Responsible for container lifecycle management on edge nodes. |
| Device-Plugin | Device discovery plugin for NPU (Ascend AI Processor). |

**解读**：
- **edge-om**：MEF Edge 的主进程，承载升级等本地管理能力。
- **edge-main**：专责 MEF Edge ↔ MEF Center 对接的进程模块，相当于边端"通信代理"。
- **EdgeCore**：来自 KubeEdge 的边缘侧组件，负责边缘节点上容器的生命周期管理——MEF 将容器管理委托给 KubeEdge 体系。
- **Device-Plugin**：NPU（昇腾 AI 处理器）设备发现插件，使容器化推理应用能够识别/使用昇腾 NPU 算力，呼应"Ascend 推理解决方案"定位。

---

### 表 4：MEF Edge 与 MEF Center 集成模式支持的产品列表（原文表格被截断）

> 以下按原文 HTML 表头结构逐字还原，原文提供的内容在第一行数据行被截断：

| Installation Node | Software | Product Form | Software Architecture | OS |
|--|--|--|--|--|
| Management Node | MEF Center | Gener…（原文此处被截断，未提供完整内容）| （原文未提供）| （原文未提供）|

**解读**：
- 表格本身是兼容性矩阵，5 列分别约束：**安装节点类型**、**软件名**、**产品形态**、**软件架构**、**操作系统**。
- 已知首行 Installation Node 为「Management Node」、Software 为「MEF Center」，Product Form 以「Gener」开头（推测对应 "General-purpose server"，与上文"M 部署在通用服务器"一致），但因原文被截断，其余列以及后续 Edge 节点行均不可见，**本总览文档未提供完整兼容清单**。读者需另行查阅详细的 MEF 兼容性列表文档以获取完整信息。

---

## 【公式解读】

原文无公式。

---

## 【关联】

依据文档内容梳理的关系链（原文无内部链接，因此以下关联均来自文档正文中明文提及的模块/系统/方案）：

- **上游/底座依赖**：
  - **KubeEdge（开源）**：MEF 控制链路的实现底座；MEF Edge 中 `EdgeCore` 模块即为 KubeEdge 的边缘侧组件，负责容器生命周期管理。
- **同源方案归属**：
  - **Ascend 推理解决方案**：MEF 是其下属"智能边缘设备使能"组成部分，并通过 `Device-Plugin` 适配 Ascend NPU。
- **内部组件协同**：
  - MEF Center 的 `APIG` ↔ MEF Edge 的 `edge-main`：分别承担北向接口暴露与南北对端通信。
  - MEF Center 的 `edge-manager`：同时管理"边缘节点"和其上的"容器化应用"，与"Application Scenario"中两类主用例直接对应。
  - MEF Center 的 `cert-manager` ↔ `APIG`：证书统一管理与双向认证相互配合，闭环安全能力。
  - MEF Center 的 `alarm-manager`：覆盖 MEF Edge 与 MEF Center 自身的告警/事件，闭环可观测性。
- **下游/外部对接**：
  - **ISV 业务平台**：通过 MEF Center 的 RESTful 北向接口对接，间接驱动 MEF Edge 完成边缘节点纳管与容器化应用全生命周期管理。
  - **用户应用（容器镜像）**：以容器镜像形式发布，由 MEF 进行增删改查与生命周期管理。
- **场景链路**：
  - "Application Scenario" → "Procedure of Connecting MEF Edge to MEF Center" 构成一条端到端叙事线：安装 MEF → 二次开发与集成 → 通过 ISV 平台纳管节点与应用 → 借助 MEF Edge ↔ MEF Center 实现云边协同。

---

## 【使用方法】

> 本总览文档未给出具体的安装命令、配置文件路径、API 端点、端口、参数等启用细节，仅提供高层流程性描述：

- **启用方式（原文层级）**：
  1. **安装 MEF**：分为"MEF Center 的准备与安装"与"MEF Edge 的准备与安装"两个子步骤（原文未在本文给出具体命令与介质）。
  2. **二次开发与集成**：用户进行定制化修改后，将 MEF 与开发者平台集成；内部实现 MEF Center 与 MEF Edge 的云边集成，对外通过北向接口对接 ISV 业务平台。
  3. **业务侧管理**：通过 ISV 业务平台对边缘节点和容器化应用进行管理。
- **关键集成能力（原文提及）**：
  - 通过 MEF Center 的 RESTful 接口被 ISV 业务平台调用；
  - 通过 MEF Edge `Device-Plugin` 接入昇腾 NPU，使容器化推理应用可使用 NPU 算力；
  - 利用 MEF Edge 离线自治能力保障链路中断期间推理服务不中断、重启后自恢复。

原文未涉及具体的 CLI 命令、yaml/ini 配置项、端口/路径/账号等运维级参数；如需获取这些信息，须查阅本文档所属仓库中更下层级的安装/集成/运维文档。

## 图文联合解读

- `MEF-architecture.png`: **图示内容**：分层架构——上层"通用服务器"含ISV服务平台（用户/软件/镜像库，蓝色）与MEF Center（API Gateway、edge/cert/alarm-manager，紫）+ K8s/KubeEdge（灰）；下层"智能边缘设备"含MEF Edge（edge-main、edge-om、EdgeCore、Device-Plugin，紫）运行于Docker（灰）；虚线箭头连接云边。按华为/ISV/开源三方分色。

**技术结论**：MEF采用云端Center+边缘Edge的清晰组件分工，依托开源K8s+KubeEdge+Docker构建可集成底座，边缘侧轻量、仅保留必要模块。

**与文档关系**：图解文档所提"轻量化设备-边-云协同框架"，印证"MEF Center+MEF Edge"分工实现边缘节点与容器化推理服务管理的产品定义。
- `MEF-integration-mode.png`: 图示MEF Edge（部署于Atlas AI边缘设备）与MEF Center（通用服务器）双向对接，Center再下接ISV服务平台。色块区分"MEF提供"与"ISV提供"两层职责，论证边端管理—云端调度—应用服务的分层解耦架构，与文档"轻量化边云协同使能框架"的产品定位及边缘节点与推理服务管理论点一致。
- `cloud-edge-collaboration-between-MEF-Edge-and-MEF-Center.png`: # 图文联合解读

## 1) 图中内容
该图为MEF框架使用流程图，从"Start"到"End"纵向串联五个主节点：**MindEdge Framework installation**（安装MEF Center/MEF Edge）→ **ISV service platform preparation**（用户管理平台、软件仓库、镜像仓库准备）→ **Secondary development and integration**（MEF Center与ISV平台及MEF Edge对接，含二级子分支）→ **Application scenarios**（边缘节点管理：节点/信息/分组管理 + 容器化应用管理）。

## 2) 技术结论
图示证明MEF是一套**层次化、全生命周期**的边云协同落地路径：先搭建组件，再准备集成资源，再完成对接，最后支撑业务场景，体现了"中心—边—ISV三方协同"架构。

## 3) 与文档论点关系
文档定义MEF为"轻量化边云协同集成框架"，提供边缘节点管理与容器化应用管理功能。该流程图正是对这一产品定位的**实施路径具象化**，论证了MEF通过安装→集成→场景化三阶段实现批量边缘设备与AI推理服务的统一管控，直击文档所强调的"大规模边缘设备管理与应用部署"核心痛点。
