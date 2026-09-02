# What is MindCluster

> 仓 `mind-cluster` · 路径 `docs/en/overview.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mind-cluster/docs/en/overview.md

# MindCluster Overview 文档深度解读

## 【定位】

本文档是「mind-cluster」代码仓的总览性介绍 (`docs/en/overview.md`)，系统性地阐述 MindCluster 作为面向昇腾 NPU 的 AI 集群软件栈的整体定位、能力边界与组件构成，旨在帮助读者建立对该组件仓的宏观认知框架。

---

## 【技术要点】

- **栈定位**：MindCluster 是面向 NPUs (Ascend AI Processors) 的「deep learning for an AI cluster」，专为训练与推理任务提供**集群级 (cluster-level)** 解决方案，使深度学习平台开发者无需自行处理底层资源调度，即可快速搭建平台。
- **四大核心能力域**：① Installation and deployment（安装部署）、② Performance testing（性能测试）、③ Fault Diagnosis（故障诊断）、④ Cluster Scheduling（集群调度）。
- **生命周期声明**：Resilience Controller 与 Elastic Agent 组件**已停止开发并被移除**；其中 Resilience Controller 相关内容将在 **2026 年 9 月 30 日**发布的版本中下线，Elastic Agent 相关内容将在 **2026 年 12 月 30 日**发布的版本中下线（提示：这两个组件在 Table 4 中仍以列出形式存在，但处于待废弃状态）。
- **三层组件结构**：工具层 (ToolBox: DMI、Cert) → 诊断层 (FaultDiag) → 调度层 (Docker Runtime、Device Plugin、NPU Exporter、Volcano、ClusterD、Ascend Operator、NodeD、TaskD、MindIO ACP/TFT、Container Manager、Infer Operator)。
- **关键基础设施依赖**：Kubernetes device plugin 机制（用于 Ascend Device Plugin）、开源 Volcano 调度插件（用于亲和性/容错调度）。
- **加速训练配套能力**：MindIO ACP 利用训练服务器内存作为大模型 checkpoint 缓存；MindIO TFT 提供 TTP、UCE、ARF 三类功能；Resilience Controller（已废弃）曾提供「硬件故障时剔除硬件并继续训练」的弹性缩容能力。

---

## 【关键机制与数据】

> 原文未给出具体性能数据、时延数字或吞吐基准。以下只归纳原文可读的机制描述。

- **架构示意**：「Figure 1 MindCluster Stack Diagram」给出栈结构图，原文仅引用图片标题，未在正文中展开分层说明（仅依赖图示与表格推断层级）。
- **集群调度数据流（推断自组件职责）**：
  - 资源发现层：Ascend Device Plugin 上报 Ascend AI Processor 资源 → Kubernetes；
  - 监控层：NPU Exporter 实时采集 utilization / temperature / voltage；NodeD 上报节点健康 / CPU / 内存；
  - 调度层：Volcano 在开源插件基础上叠加 NPU 亲和性调度与故障重调度；
  - 任务编排层：Ascend Operator 注入分布式训练所需环境变量并生成 collective communication 配置；TaskD 提供训练/推理任务的**状态监控与状态控制**；Infer Operator 管理推理服务生命周期并支持实例级扩缩容与 task role 扩展；
  - 容错层（部分废弃）：ClusterD 跨任务、芯片、故障三维度聚合资源/故障影响面；Resilience Controller（已废弃）触发弹性缩容；Elastic Agent（已废弃）保存 dying gasp checkpoint。
- **诊断数据流**：MindCluster Ascend FaultDiag 执行「**日志清洗 → 关键信息抽取 → 全集群节点关键信息汇聚 → 根因节点与故障事件分析**」四级链路，定位训练/推理失败的根因。
- **ToolBox 数据流**：Ascend DMI 输出兼容性、带宽、算力、功耗、诊断压测五类结果；Ascend Cert 完成软件包数字签名验证与 CRL 更新。

---

## 【表格解读】

### 表格 A：MindCluster Feature Overview（特性总览）

| Key Feature | Introduction | Reference |
|---|---|---|
| Installation and deployment | Provides online download, installation, and signature verification for Ascend software and its dependencies. | [Installation and Deployment](https://gitcode.com/Ascend/ascend-deployer/blob/dev/docs/en/introduction.md) |
| Performance testing | Provides functions such as Atlas hardware compatibility check, performance testing, and fault diagnosis. | [Performance Testing](https://www.hiascend.com/document/detail/en/mindcluster/2600/toolbox/toolboxug/toolboxug_0002.html) |
| Fault Diagnosis | Provides log cleaning and fault diagnosis functions for training and inference tasks, and locates the root cause of failures. | [Fault Diagnosis](./faultdiag/introduction.md) |
| Cluster Scheduling | Provides functions such as NPU resource scheduling and management, configuration generation for distributed training collective communication, and resumable training. | [Cluster Scheduling](./scheduling/introduction/00_overview.md) |

**逐行解读**：
- **Installation and deployment**：聚焦**在线获取→安装→签名校验**一条链路，对应组件 MindCluster Ascend Deployer。
- **Performance testing**：覆盖 Atlas 硬件**兼容性 + 性能 + 故障诊断**三类动作，由 ToolBox (DMI/Cert) 提供。
- **Fault Diagnosis**：面向训练与推理的**日志清洗 + 故障诊断 + 根因定位**，由 MindCluster Ascend FaultDiag 承担。
- **Cluster Scheduling**：四大子能力 — NPU 资源调度/管理、分布式训练 collective communication 配置生成、**可恢复训练 (resumable training)**；链接指向 `./scheduling/introduction/00_overview.md`。

### 表格 B：Table 1 Installation and deployment

| Component | Feature Overview |
|---|---|
| MindCluster Ascend Deployer | Supports automatic download and one-click installation of Ascend software and its dependencies, and provides functions such as parameter plane network configuration. |

**逐行解读**：该组件做两件事——① 昇腾软件与依赖的**自动下载 + 一键安装**；② **参数面 (parameter plane) 网络配置**（注意是参数面网络，非业务数据面）。

### 表格 C：Table 2 ToolBox

| Component | Feature Overview |
|---|---|
| Ascend DMI | Provides functions such as compatibility check, bandwidth test, computing power test, power consumption test, and diagnostic stress test for Atlas hardware products. |
| Ascend Cert | Provides functions such as software package digital signature verification and CRL update to ensure the security of software packages and the validity of CRL files. |

**逐行解读**：
- **Ascend DMI**：五大测试——**兼容性 / 带宽 / 算力 / 功耗 / 诊断压测**，面向 Atlas 硬件产品族。
- **Ascend Cert**：保障**软件包安全**（数字签名验证）与 **CRL (Certificate Revocation List) 有效性**。

### 表格 D：Table 3 Fault diagnosis

| Component | Feature Overview |
|---|---|
| MindCluster Ascend FaultDiag | Provides log cleaning and fault diagnosis functions, extracts key information from logs related to training and inference processes, and analyzes the root cause node and fault event based on the cleaned key information from all cluster nodes. |

**逐行解读**：处理流程为 **日志清洗 → 关键信息抽取 → 跨集群节点聚合 → 根因节点 + 故障事件分析**，强调「**全集群节点关键信息**」是定位根因的输入。

### 表格 E：Table 4 Cluster scheduling

| Component | Feature Overview |
|---|---|
| Ascend Docker Runtime | Provides containerization support for training and inference tasks, automatically mounting required files and device dependencies. |
| Ascend Device Plugin | Based on the Kubernetes device plugin mechanism, provides device discovery, allocation, and health status reporting capabilities for Ascend AI Processors, enabling Kubernetes to manage Ascend AI Processor resources. |
| NPU Exporter | Monitors resource metrics of Ascend AI Processors in real time, obtaining information such as utilization, temperature, and voltage of Ascend AI Processors. |
| Volcano | Based on the open-source Volcano scheduling plugin mechanism, adds features such as affinity scheduling and fault rescheduling for Ascend AI Processors to maximize their computing performance. |
| ClusterD | Provides cluster-level available resource information and collects cluster task information, resource information, fault information, and impact scope, performing statistical analysis from task, chip, and fault dimensions. |
| Ascend Operator | Provides lifecycle management for training tasks, supplying corresponding environment variables for distributed training tasks of different AI frameworks and generating necessary collective communication configuration. |
| NodeD | Reports node status and fault information such as node health status, CPU, and memory. |
| Resilience Controller | Provides elastic scaling-down training service. When the hardware used by a training task fails, it removes the hardware and continues training. |
| Elastic Agent | Provides the capability to save a dying gasp checkpoint at the moment of a training task failure. |
| TaskD | Provides status monitoring and status control capabilities for training and inference tasks on Ascend devices. |
| MindIO ACP | Uses the training server memory as a cache to accelerate the saving and loading of checkpoints during large model training. |
| MindIO TFT | Provides functions such as TTP, UCE, and ARF. |
| Container Manager | Provides service container recovery capability in non-Kubernetes scenarios, mainly used an appliance. |
| Infer Operator | Manages the lifecycle of inference services based on their configuration, supporting instance-level scaling and task role expansion. |

**逐行解读**：
- **Ascend Docker Runtime**：训练/推理容器化，自动挂载文件与设备依赖。
- **Ascend Device Plugin**：基于 K8s device plugin，提供**设备发现、分配、健康上报**三能力，使 K8s 能纳管 NPU。
- **NPU Exporter**：实时采集 utilization / temperature / voltage（Exporter 模式通常用于 Prometheus 抓取）。
- **Volcano**：基于开源 Volcano 插件，叠加**亲和性调度 + 故障重调度**，目标是最大化算力。
- **ClusterD**：集群级资源聚合与**任务/芯片/故障三维统计**。
- **Ascend Operator**：训练任务生命周期管理；为不同 AI 框架注入对应环境变量；生成 collective communication 配置（HCCL 等）。
- **NodeD**：节点健康 + CPU + 内存上报。
- **Resilience Controller（已停用/待下线）**：训练服务的**硬件级弹性缩容**——故障时剔除硬件、训练继续。
- **Elastic Agent（已停用/待下线）**：在训练任务失败瞬间保存 **dying gasp checkpoint**。
- **TaskD**：训练/推理任务的**状态监控 + 状态控制**。
- **MindIO ACP**：用**训练服务器内存**做大模型 checkpoint 读写的缓存加速。
- **MindIO TFT**：提供 **TTP、UCE、ARF** 三类功能（原文未展开缩写含义）。
- **Container Manager**：**非 K8s 场景**下的服务容器恢复，主要作为 appliance 使用。
- **Infer Operator**：基于配置管理推理服务生命周期，支持**实例级扩缩容**与 **task role 扩展**。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **Fault Diagnosis ↔ Cluster Scheduling**：Table 4 中 NodeD、ClusterD、Resilience Controller、Elastic Agent 共同构成容错闭环，而 Table 3 的 FaultDiag 通过日志清洗与根因分析为该闭环提供事后定位能力，二者通过「**故障信息 + 关键日志**」双向耦合。
- **Cluster Scheduling ↔ Installation and deployment**：Table 1 的 Ascend Deployer 负责参数面网络配置与软件一键安装，为后续 K8s + Volcano 调度栈提供基础环境。
- **Cluster Scheduling ↔ Performance testing**：ToolBox 的 Ascend DMI 在硬件上线前提供兼容性 / 算力 / 带宽 / 功耗验证，是调度栈投入生产的前置质量门。
- **MindIO ACP/TFT ↔ Ascend Operator**：Operator 负责训练任务生命周期，MindIO 系列提供 checkpoint I/O 加速与容错训练协议（TTP/UCE/ARF），形成「大模型训练 I/O 子系统」配套关系。
- **废弃链路**：Resilience Controller 与 Elastic Agent 在 Feature Overview 与 Table 4 中仍可见，但依据文档顶部 NOTE，二者已停止开发并将在 **2026-09-30 / 2026-12-30** 两个版本节点分别从文档中移除，对应能力可视为由 ClusterD + TaskD + FaultDiag + MindIO TFT 替代承接。
- **文末内部链接指向**：
  - `./faultdiag/introduction.md` → 展开 Fault Diagnosis 特性；
  - `./scheduling/introduction/00_overview.md` → 展开 Cluster Scheduling 特性（含 Ascend Operator、Volcano、Device Plugin 等子模块细节）。

---

## 【使用方法】

原文未涉及具体的启用命令、配置项、API 调用或部署参数。文档仅给出组件级职责描述与外链索引（Installation and Deployment / Performance Testing 的官方文档链接），实际启用方式需参考以下资源：

- 安装部署：[Installation and Deployment](https://gitcode.com/Ascend/ascend-deployer/blob/dev/docs/en/introduction.md)
- 性能测试：[Performance Testing](https://www.hiascend.com/document/detail/en/mindcluster/2600/toolbox/toolboxug/toolboxug_0002.html)
- 故障诊断：本文档内链 `./faultdiag/introduction.md`
- 集群调度：本文档内链 `./scheduling/introduction/00_overview.md`

## 图文联合解读

- `mindcluster-arch.png`: **图文联合解读：**

**1) 图示内容：** 三层堆栈结构。上层为第三方深度学习平台（数据标注、训练、部署等）；中层为 MindCluster，包含安装部署（Ascend Deployer/Cert）、性能测试（DMI）、故障诊断（FaultDiag）和集群调度（Docker/Volcano/Device Plugin 等十余个插件）；底层为 Kubernetes + CANN + 计算/管理节点。

**2) 技术结论：** MindCluster 居于第三方平台与 K8s 异构硬件之间，通过插件化方式屏蔽 NPU 资源调度、监控、检查点等底层复杂度。

**3) 与文档论点呼应：** 图直观论证了"让平台开发者最小化底层资源调度开发"这一核心定位——上层只需对接 MindCluster，即可获得完整的集群级训练/推理能力。
