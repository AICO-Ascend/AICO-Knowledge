# 产品简介<a name="ZH-CN_TOPIC_0000001722295433"></a>

> 仓 `mef` · 路径 `docs/zh/user_guide/introduction.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mef/docs/zh/user_guide/introduction.md

# 一体化深度解读：MEF 产品简介

## 【定位】

本篇文档是 MEF 框架的**产品入门级概览（Product Introduction / Overview）**，目标读者为系统管理人员、集成商（ISV）及边缘方案架构师。它解决的核心问题是：**在 AI 行业智能化转型背景下，如何集中、批量、可信地管理海量边缘节点与边缘侧容器推理应用，并对外提供可被集成的端边云协同能力**。文档围绕"为什么需要 MEF → MEF 是什么 → MEF 怎么架构 → 在哪些场景用 → 部署形态如何支持"这一逻辑链展开，是后续安装、二次开发与运维文档的总纲。

---

## 【技术要点】

1. **产品定位（被集成的轻量化端边云协同使能框架）**：MEF 不直接面向终端用户，而是作为昇腾推理解决方案的**一部分**，以"被集成"姿态嵌入 ISV 业务平台；用户通过二次开发对接 ISV 平台来完成业务闭环。
2. **双向组成：MEF Edge + MEF Center**
   - **MEF Edge**：部署在智能边缘设备（Atlas 200I A2 加速模块 / Atlas 200I DK A2 / Atlas 500 Pro 服务器等）上，负责与中心网管对接、容器应用部署与生命周期管理。
   - **MEF Center**：部署在通用服务器（AArch64 / x86_64）上，提供节点批量管理、业务部署与系统监测。
3. **底层控制链路基于开源 KubeEdge**：MEF Center 与 MEF Edge 之间控制链路的建立和管理依托 KubeEdge 完成；MEF Edge 侧的 `EdgeCore` 模块即为 KubeEdge 的边侧组件，承担容器生命周期管理。
4. **对外接口形态：RESTful + 双向认证**：MEF Center 通过 `APIG（API Gateway）`模块对外提供与 ISV 业务平台之间的双向认证和 RESTful 接口，便于第三方集成调用。
5. **离线自治能力**：原文明确"当 MEF Edge 所在边缘节点与 MEF Center 所在中心节点链路中断后，边缘节点推理业务不中断；边缘节点发生重启，推理业务可以在边缘节点重启完成之后自行恢复。"——这是边缘侧可用性的关键设计。
6. **NPU 设备发现**：MEF Edge 中包含 `Device-Plugin`，用于**昇腾 AI 处理器（NPU）**的设备发现，配合 KubeEdge 调度模型使容器应用可识别并使用昇腾算力。
7. **支持的产品形态与 OS 矩阵**（保留原文关键数字/参数）：
   - 管理节点（MEF Center）：通用服务器，**AArch64** 和 **x86_64**，OS：**Ubuntu 20.04** / **openEuler 22.03**。
   - 计算节点（MEF Edge）：三类硬件形态
     - Atlas 200I A2 加速模块、Atlas 200I DK A2 开发者套件 → AArch64 → openEuler 22.03 / Ubuntu 22.04
     - Atlas 500 Pro 智能边缘服务器（型号 3000，插 Atlas 300I Pro 推理卡）→ AArch64 → openEuler 22.03

---

## 【关键机制与数据】

- **工作原理（云边协同）**：MEF Edge 接收 MEF Center 下发的消息并把相关信息收集、转发回 MEF Center，由 Center 侧完成"安装升级 + 容器应用全生命周期管理"指令的下达；Edge 侧则执行安装/升级/容器调度等动作，并通过 `EdgeCore`（KubeEdge 边侧部分）完成容器生命周期管理。
- **数据流方向（原文: "MEF Edge主要通过接收MEF Center消息并将相关信息收集、转发到MEF Center"）**：MEF Center → 控制指令下发 → MEF Edge；MEF Edge → 状态/告警/事件收集 → MEF Center。
- **自治机制（原文: "MEF具备离线自治能力"）**：
  1. 链路中断时 → 边缘推理业务不中断；
  2. 边缘节点重启完成 → 推理业务自行恢复。
- **业务对接层次（原文: "对外通过北向接口对接ISV业务平台"）**：MEF Center 对上提供北向 RESTful 接口，对内通过 KubeEdge 控制面与 MEF Edge 互通，形成"ISV 平台 ← 北向接口 → MEF Center ← KubeEdge → MEF Edge"的云边协同链路。
- **告警/证书统一管理**：MEF Center 内置 `alarm-manager`（告警/事件）和 `cert-manager`（内外部证书统一管理），MEF Edge 与 MEF Center 的告警和事件均由 `alarm-manager` 统一管理，证书由 `cert-manager` 统一治理——这是"安全可信"价值的实现基础。
- **性能/量化数据**：原文未提供具体性能数字（如时延、吞吐、并发数等），故此处不臆造。

---

## 【表格解读】

### 表 A：产品价值说明（原文"表 1"）

| 使用层面 | 产品价值 |
| -- | -- |
| 业务面 | MEF 生态开放，全栈使能，便于集成，降低用户的使用门槛。 |
| 管理面 | MEF 极简易用，安全可信。 |

**逐行解读：**
- **业务面行**：强调 MEF 不做封闭烟囱，而是以"生态开放 + 全栈使能"姿态降低 ISV 的对接成本——这与产品定义中"被集成的轻量化端边云协同使能框架"形成呼应。
- **管理面行**：前半句"极简易用"对应 `edge-manager` 统一纳管、容器增删改查的体验；后半句"安全可信"对应 `cert-manager`（证书统一管理）+ `APIG`（双向认证）的安全设计。

### 表 B：MEF Center 模块说明（原文"表 1"，架构章节内）

| 模块名称 | 模块功能定位 |
| -- | -- |
| APIG（API Gateway） | 对外提供 ISV 业务平台的双向认证和 RESTful 接口。用于 ISV 业务平台调用并使用 MEF Center 提供的服务。 |
| edge-manager | 边缘节点管理模块及容器应用管理模块。实现对边缘节点接入和节点上运行容器应用的管理。 |
| cert-manager | 证书管理模块。用于对 MEF 使用的内外部证书实施统一管理。 |
| alarm-manager | 告警管理模块。用于管理 MEF Edge 和 MEF Center 的告警和事件。 |

**逐行解读：**
- **APIG**：MEF 对 ISV 的唯一北向入口，承载双向认证与 RESTful 接口，是"业务面价值（便于集成）"的直接落点。
- **edge-manager**：Center 侧的核心业务模块，把"边缘节点接入"与"容器应用管理"两类原子能力合并封装，对应"应用场景"章节中"纳管、查询、修改、删除"以及"容器应用增删改查"的能力声明。
- **cert-manager**：MEF 信任链的根，"安全可信"的具体落点之一，管理 MEF 内部证书 + 外部证书。
- **alarm-manager**：覆盖 Edge + Center 两侧的告警/事件聚合，是"管理面极简易用"在可观测性维度的体现。

### 表 C：MEF Edge 模块说明（原文"表 2"，架构章节内）

| 模块名称 | 模块功能定位 |
| -- | -- |
| edge-om | 主进程模块，包括升级模块等。 |
| edge-main | 对接 MEF Edge 和 MEF Center 的进程模块。 |
| EdgeCore | 开源系统 KubeEdge 的边侧部分。负责边缘节点容器生命周期管理。 |
| Device-Plugin | NPU（昇腾 AI 处理器）的设备发现插件。 |

**逐行解读：**
- **edge-om**：Edge 侧主进程，承担升级能力，对应"完成相关软件的安装升级"的功能描述。
- **edge-main**：MEF Edge 与 MEF Center 对接的消息通道，对应原文"MEF Edge 主要通过接收 MEF Center 消息……"这条数据流。
- **EdgeCore**：KubeEdge 在边缘的运行时组件，承载容器化应用的真正调度与生命周期。
- **Device-Plugin**：将昇腾 NPU 暴露给 Kubernetes/KubeEdge 调度体系，使容器可申请并使用昇腾算力——这是 MEF 与"昇腾推理解决方案"绑定的硬件使能点。

### 表 D：MEF Edge 对接 MEF Center 方式支持的产品列表（原文 HTML 表格，已用 markdown 逐字还原）

| 安装节点 | 软件 | 产品形态 | 软件架构 | 操作系统 |
| -- | -- | -- | -- | -- |
| 管理节点 | MEF Center | 通用服务器 | AArch64 和 x86_64 | Ubuntu 20.04；openEuler 22.03 |
| 计算节点 | MEF Edge | Atlas 200I A2 加速模块；Atlas 200I DK A2 开发者套件 | AArch64 | openEuler 22.03；Ubuntu 22.04 |
| 计算节点 | MEF Edge | Atlas 500 Pro 智能边缘服务器（型号 3000）（插 Atlas 300I Pro 推理卡） | AArch64 | openEuler 22.03 |

**逐行解读：**
- **第 1 行（管理节点）**：MEF Center 是 Center 端唯一部署形态——**通用服务器**，CPU 架构支持 **AArch64 + x86_64** 两种，意味着既可部署在鲲鹏/昇腾通用服务器，也可部署在传统 x86 通用服务器；OS 限定为 **Ubuntu 20.04** 与 **openEuler 22.03** 两个 LTS 级别发行版。
- **第 2 行（计算节点·开发者套件/加速模块档）**：Edge 端支持两类轻量硬件（**Atlas 200I A2 加速模块**与 **Atlas 200I DK A2 开发者套件**），统一 **AArch64** 架构，OS 组合为 **openEuler 22.03** 与 **Ubuntu 22.04**——这是开发与小规模部署的典型配置。
- **第 3 行（计算节点·边缘服务器档）**：Edge 端另支持 **Atlas 500 Pro 智能边缘服务器（型号 3000）**，需搭配 **Atlas 300I Pro 推理卡**，同样 **AArch64**，OS 限定 **openEuler 22.03**——这是面向生产级边缘站点的更高算力配置。
- **整体观察**：
  1. Edge 侧仅支持 AArch64，未列 x86_64——意味着 MEF Edge 与昇腾硬件深度绑定；
  2. OS 均为 LTS 版本，发行版生态在 openEuler 与 Ubuntu 两侧收敛；
  3. Center 与 Edge 的 OS 并不完全对称（Center 无 Ubuntu 22.04，Edge 无 Ubuntu 20.04 与 x86_64），部署时需按节点类型匹配。

---

## 【公式解读】

原文无公式。

---

## 【关联】

文档在结构上以"为什么 → 是什么 → 怎么架构 → 在哪些场景用 → 支持哪些部署形态"递进，并为后续深度文档留下清晰的承接点：

- **产品定义 ↔ MEF 架构**："MEF Edge + MEF Center"这一对组件在架构章节中以表格（表 B、表 C）展开为具体模块（APIG / edge-manager / cert-manager / alarm-manager / edge-om / edge-main / EdgeCore / Device-Plugin），构成对"产品定义"的可执行映射。
- **架构 ↔ 应用场景**：架构中的 `edge-manager` 直接对应"应用场景"中"边缘节点纳管、查询、修改、删除"与"容器应用增删改查"两类能力声明。
- **架构 ↔ 离线自治**：Edge 侧 `edge-om + EdgeCore + Device-Plugin` 的组合，加上 `edge-main` 与 Center 的对接链路，是"链路中断业务不中断 / 重启后业务自行恢复"这一离线自治能力的技术承载。
- **架构 ↔ 部署形态**：表 D 中所有支持的产品形态（Atlas 200I A2 加速模块、Atlas 200I DK A2、Atlas 500 Pro 服务器+Atlas 300I Pro 推理卡、通用服务器）共同决定了架构中各模块的实际运行环境，特别是 `Device-Plugin` 必须工作在带 NPU 的 AArch64 Edge 节点上。
- **应用流程 ↔ 全篇**：文末"安装MEF → 二次开发集成 → 管理边缘节点及容器应用"三段式流程（对应图 2）把产品定义、架构、应用场景与部署形态串联成一条端到端用户旅程，是 introduction 章节向后续"安装指南 / 二次开发指南 / 用户指南"过渡的总索引。
- **依赖上游**：明确指出 MEF **依托开源系统 KubeEdge** 完成 Center 与 Edge 之间控制链路的建立和管理——任何对控制面行为的深度解读都需要回到 KubeEdge 的 EdgeCore / CloudCore 机制。

---

## 【使用方法】

原文未涉及具体启用命令、配置项或 API 调用方法。本节仅复述**文档给出的高层流程性指引**（原文："MEF Edge 对接 MEF Center 进行云边协同的应用流程主要包括安装MEF，二次开发集成MEF和管理边缘节点及容器应用三部分"）：

1. **安装 MEF**：分别完成 MEF Center（管理节点 / 通用服务器）与 MEF Edge（计算节点 / Atlas 系列）的准备与安装；安装前提须满足表 D 的"软件架构 + 操作系统"组合约束。
2. **二次开发集成 MEF**：用户完成定制化修改后，将 MEF 集成进自有开发者平台，对外通过 MEF Center 的北向 RESTful 接口（由 `APIG` 模块承载，支持双向认证）对接 ISV 业务平台；对内实现 MEF Center 与 MEF Edge 的云边对接（依托 KubeEdge）。
3. **管理边缘节点及容器应用**：通过 ISV 业务平台下发指令，由 `edge-manager` 完成"节点纳管 / 节点组 / 容器应用增删改查"全生命周期管理，由 `alarm-manager` 统一汇聚 Edge + Center 告警/事件。

> 原文未提供具体 CLI 命令、RESTful 端点、参数或 YAML 配置样例；这些细节需查阅后续安装/二次开发/用户指南文档。

## 图文联合解读

- `MEF架构图.png`: 图分云端（ISV业务平台+MEF Center，含API Gateway、edge/cert/alarm-manager，基于K8s+KubeEdge CloudCore）与设备端（MEF Edge，含edge-main、edge-om、EdgeCore、Device-Plugin+Docker）两层，虚线表云边协同。色块标注提供方，论证"被集成"分层使能架构：MEF聚焦核心、ISV提供业务、开源提供底座，KubeEdge打通云边——印证"轻量化端边云协同使能框架"及业务面开放、管理面简易的产品价值。
- `MEF对接方式.png`: 图示解读：
①画面呈现三层架构：Atlas 200I A2/500 Pro边缘设备部署MEF Edge，通用服务器部署MEF Center，二者通过虚线控制链路对接；MEF Center再对接ISV业务平台。颜色区分集成边界（紫色MEF提供，浅蓝ISV提供）。

②论证结论：MEF采用"云—边—端"分层架构，Center居中调度，Edge下沉到昇腾硬件，形成清晰的被集成边界。

③与文档呼应：印证产品定义中"Edge部署在智能边缘设备、Center部署在通用服务器"以及"被集成、轻量化端边云协同框架"的定位，体现MEF负责框架层、ISV负责业务层的解耦设计。
- `MEF-Edge和MEF-Center云边协同应用流程.png`: **图文联合解读：**

1）**图示内容**：纵向流程图描绘MEF使用全生命周期，自上而下分四阶段：安装MEF（含Center/Edge）→ 准备ISV业务平台（用户管理平台、软件仓、镜像仓）→ 二次开发集成（对接Center+ISV平台、Center+Edge）→ 产品应用场景（纳管节点、管理容器应用）。旁支细分关键动作。

2）**技术结论**：论证MEF落地路径清晰闭环，呈"平台准备→集成对接→运行管理"三段式，验证"被集成的轻量化框架"定位。

3）**与文档呼应**：支撑"业务面生态开放、全栈使能，便于集成，降低门槛"与"管理面极简易用"两大价值主张，将抽象架构转化为可落地操作步骤。
