# MindCluster是什么

> 仓 `mind-cluster` · 路径 `docs/zh/overview.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mind-cluster/docs/zh/overview.md

# MindCluster overview.md 深度解读

## 【定位】

本文档是 MindCluster（AI 集群系统软件）的总览性介绍文档，核心回答的问题是：**MindCluster 是一个什么级别的软件组件、它为昇腾 NPU 深度学习训练/推理任务提供哪些集群级能力，以及它由哪些子模块构成。** 面向"深度学习平台开发厂商"这一读者群，告诉他们 MindCluster 已经把底层资源调度、故障诊断、安装部署等共性能力做好了，合作伙伴可以基于它快速构建深度学习平台，而无需重复造轮子。

---

## 【技术要点】

1. **组件定位**：MindCluster 是"支持 NPU（昇腾 AI 处理器）构建的深度学习系统组件"，**专门服务于训练和推理任务**，提供的是"集群级解决方案"，而非单机能力。
2. **四大关键特性（原文"关键特性"表）**：
   - 安装部署（在线下载、安装、签名校验）
   - 性能测试（兼容性检查、性能测试、故障诊断）
   - 故障诊断（日志诊断 + 链路诊断）
   - 集群调度（NPU 资源调度与管理、集合通信配置生成、断点续训）
3. **组件构成**：按四大特性划分为 4 张组件表，共涉及 15 个子组件（MindCluster Ascend Deployer、Ascend DMI、Ascend Cert、MindCluster Ascend FaultDiag、Ascend Docker Runtime、Ascend Device Plugin、NPU Exporter、Volcano、ClusterD、Ascend Operator、NodeD、Resilience Controller、Elastic Agent、TaskD、MindIO ACP、MindIO TFT、Container Manager、Infer Operator、K8s RDMA Shared Dev Plugin）。
4. **重要产品生命周期声明**：Resilience Controller 和 Elastic Agent 组件已"日落"——前者相关内容将于 **2026 年 9 月 30 日**的版本删除，后者将于 **2026 年 12 月 30 日**的版本删除。
5. **生态对接**：深度集成 Kubernetes（通过 Ascend Device Plugin、NPU RDMA Shared Dev Plugin）与开源 Volcano 调度器；面向"无 K8s 场景"还提供 Container Manager（一体机场景）。
6. **安全机制**：通过 Ascend Cert 提供软件包数字签名校验与 CRL 证书吊销列表更新，保证软件包安全性与 CRL 文件有效性。

---

## 【关键机制与数据】

本文档是 overview 级别，**未涉及具体性能数据、调用链路、时延数字**。可从原文中提取的"事实性数据/信息"如下：

- **原文：Resilience Controller 相关内容将于 2026 年 9 月 30 日的版本删除**——这是组件级别的 EOL（End of Life）时间锚点。
- **原文：Elastic Agent 相关内容将于 2026 年 12 月 30 日的版本删除**——同上。
- **原文：组件"故障诊断"功能** = "日志诊断 + 链路诊断"，前者"对训练或推理集群节点日志进行清洗，定位故障根因节点与事件"，后者"结合服务器、交换机、BMC 等多维信息，实现集群链路故障定位"——这是 FaultDiag 的双引擎机制描述。
- **原文：Ascend Device Plugin** 基于 Kubernetes 设备插件机制，提供"设备发现、分配和健康状态上报"——这是 NPU 在 K8s 中纳管的标准 kubelet device plugin 模式。
- **原文：NPU Exporter** 监测的指标包括"利用率、温度、电压"——这些是 Prometheus Exporter 上报的最小指标集。
- **原文：Volcano** 增加的能力是"亲和性调度、故障重调度"——即在开源 Volcano 之上做了昇腾特性增强。
- **原文：ClusterD** 的统计维度为"任务、芯片、故障"三维度——这是其数据聚合的维度切分。
- **原文：K8s RDMA Shared Dev Plugin** 基于"开源组件"做共享方式提供"华为 UB RDMA DPU 设备的发现和故障检测"——共享模式而非独占模式。

> 性能数字、时延、吞吐等量化数据**原文未提供**。

---

## 【表格解读】

### 表 A：MindCluster 关键特性说明（原文逐字还原）

| 关键特性 | 特性介绍 | 链接 |
|--|--|--|
| 安装部署 | 提供昇腾软件和其依赖软件的在线下载、安装和签名校验。 | [安装部署](https://gitcode.com/Ascend/ascend-deployer/blob/dev/docs/zh/01_introduction/01_introduction.md) |
| 性能测试 | 提供 Atlas 硬件产品兼容性检查、性能测试、故障诊断等功能。 | [性能测试](https://www.hiascend.com/document/detail/zh/mindcluster/2610/toolbox/toolboxug/toolboxug_0002.html) |
| 故障诊断 | 提供日志诊断和链路诊断功能。定位训练或推理任务失败根因和集群链路故障。 | [故障诊断](./faultdiag/ascend-faultdiag/01_introduction/01_overview.md) |
| 集群调度 | 提供 NPU 资源调度和管理、生成分式训练集合通信配置、断点续训等功能。 | [集群调度](./scheduling/01_introduction/00_overview.md) |

**逐行解读**：
- **安装部署**：定位是软件分发层，特点是"在线下载+签名校验"，对应表 1 中 MindCluster Ascend Deployer 组件；其链接指向独立的 ascend-deployer 仓，意味着部署器本身就是单独仓管理。
- **性能测试**：注意原文将"故障诊断"也归在性能测试特性下，但实际上表 3 又将 FaultDiag 作为独立特性——**原文存在一定的功能归类重叠**：性能测试中的"故障诊断"侧重硬件层（Ascend DMI 的诊断压测），而特性表"故障诊断"侧重日志/链路（FaultDiag）。
- **故障诊断**：双能力=日志诊断+链路诊断；链接为相对路径 `./faultdiag/ascend-faultdiag/01_introduction/01_overview.md`，指向仓库内 FaultDiag 子模块的 overview。
- **集群调度**：三件事——资源调度管理、集合通信配置生成、断点续训；其中"断点续训"依赖 MindIO ACP 缓存 + Elastic Agent 临终 Checkpoint（即将日落），链接指向仓库内 scheduling 子模块的 overview。

### 表 B：表 1 安装部署组件说明（原文逐字还原）

| 组件 | 功能介绍 |
|--|--|
| MindCluster Ascend Deployer | 提供昇腾软件和其依赖软件的自动下载及一键式安装，支持参数面网络配置等功能。 |

**解读**：与表 A"安装部署"特性一一对应；补充细节——支持"参数面网络配置"（即除业务面外的参数面网络/IP 配置能力）。

### 表 C：表 2 ToolBox 组件说明（原文逐字还原）

| 组件 | 功能介绍 |
|--|--|
| Ascend DMI | 提供 Atlas 硬件产品的兼容性检查、带宽测试、算力测试、功耗测试、诊断压测等功能。 |
| Ascend Cert | 提供软件包数字签名校验和更新 CRL 证书吊销列表等功能，保证软件包的安全性和 CRL 文件的有效性。 |

**逐行解读**：
- **Ascend DMI**（Diagnostics & Management Interface）：覆盖 5 类硬件测试——兼容性、带宽、算力、功耗、诊断压测，是 Atlas 硬件"体检"工具集，对应表 A 中"性能测试"特性。
- **Ascend Cert**：安全组件，与表 1 的"签名校验"特性形成闭环——Deployer 下载包，Cert 验签。

### 表 D：表 3 故障诊断组件说明（原文逐字还原）

| 组件 | 功能介绍 |
|--|--|
| MindCluster Ascend FaultDiag | 提供日志诊断与链路诊断功能，前者通过对训练或推理集群节点日志进行清洗，定位故障根因节点与事件；后者结合服务器、交换机、BMC 等多维信息，实现集群链路故障定位。 |

**解读**：与表 A 的"故障诊断"特性一一对应。两个能力：
- **日志诊断**——清洗节点日志 → 定位**根因节点与事件**（输出粒度：节点+事件）。
- **链路诊断**——融合**服务器+交换机+BMC**三维数据（典型场景：RoCE/RDMA 链路、PCIe 链路故障定位）。

### 表 E：表 4 集群调度组件说明（原文逐字还原）

| 组件 | 功能介绍 |
|--|--|
| Ascend Docker Runtime | 为训推任务提供容器化支持，自动挂载所需文件和设备依赖。 |
| Ascend Device Plugin | 基于 Kubernetes 设备插件机制，提供昇腾 AI 处理器的设备发现、分配和健康状态上报功能，启动 Kubernetes 管理昇腾 AI 处理器资源。 |
| NPU Exporter | 实时监测昇腾 AI 处理器的资源指标，获取如昇腾 AI 处理器的利用率、温度、电压等信息。 |
| Volcano | 基于开源 Volcano 调度插件机制，增加昇腾 AI 处理器的亲和性调度、故障重调度等特性，最大化发挥昇腾 AI 处理器计算性能。 |
| ClusterD | 提供集群级别的可用资源信息。收集集群任务信息、资源信息和故障信息及影响范围，从任务、芯片和故障维度统计分析。 |
| Ascend Operator | 提供训练任务生命周期管理，为不同 AI 框架的分布式训练任务提供相应的环境变量、生成分布式训练任务依赖的集合通讯配置。 |
| NodeD | 提供节点状态上报功能，上报如节点健康状态、CPU 和内存等故障信息。 |
| Resilience Controller | 提供弹性缩容训练服务。在训练任务使用的硬件发生故障时，剔除该硬件并继续训练。 |
| Elastic Agent | 提供训练任务故障时刻保存临终 Checkpoint 能力。 |
| TaskD | 提供昇腾设备上训练及推理任务的状态监测和状态控制能力。 |
| MindIO ACP | 在大模型训练中，使用训练服务器内存作为缓存，对 Checkpoint 的保存及加载进行加速。 |
| MindIO TFT | 提供 TTP、UCE 和 ARF 等功能。 |
| Container Manager | 提供无 K8s 场景下的业务容器恢复能力，主要用于一体机。 |
| Infer Operator | 根据推理服务的配置，管理推理服务生命周期，支持实例级扩缩容以及任务角色扩展。 |
| K8s RDMA Shared Dev Plugin | 基于开源组件的功能，以共享的方式提供华为 UB RDMA DPU 设备的发现和故障检测功能。 |

**逐行解读**（按职能分组）：
- **容器与设备纳管**（3 个）：Ascend Docker Runtime（容器运行时，挂载设备/文件）、Ascend Device Plugin（K8s 设备插件，纳管 NPU）、K8s RDMA Shared Dev Plugin（共享模式纳管华为 UB RDMA DPU）。
- **可观测性**（3 个）：NPU Exporter（指标：利用率/温度/电压）、NodeD（节点级：健康状态/CPU/内存）、ClusterD（集群级：任务/芯片/故障三维统计）。
- **调度**（1 个）：Volcano——基于开源 Volcano 加 NPU 亲和性 + 故障重调度。
- **任务编排与生命周期**（4 个）：Ascend Operator（训练，生成集合通信配置）、TaskD（设备级状态监测/控制）、Infer Operator（推理服务生命周期，支持实例级扩缩容 + 任务角色扩展）、Container Manager（**无 K8s 场景**，专供一体机的容器恢复）。
- **容错与韧性**（2 个，**均日落**）：Resilience Controller（弹性缩容，故障硬件剔除）、Elastic Agent（临终 Checkpoint）。
- **训练加速与可靠性**（2 个）：MindIO ACP（用 host 内存做 Checkpoint 缓存加速）、MindIO TFT（提供 TTP、UCE、ARF 三项功能——**原文未展开说明这三项的具体含义**）。

---

## 【公式解读】

**原文无公式**。文档为产品总览性质，未涉及任何数学公式、伪代码或算法描述。

---

## 【关联】

本文档处于 MindCluster 仓库的"入口总览"位置，向下游子模块导流，可构建如下关联视图：

- **本文档 → ./faultdiag/ascend-faultdiag/01_introduction/01_overview.md**
  - 触发位置：表 A "故障诊断"特性行的链接列。
  - 关系：本文档将"故障诊断"列为四大特性之一，并把读者导流到 FaultDiag 子模块的独立 overview（即表 D 中的 MindCluster Ascend FaultDiag 组件详解）。
- **本文档 → ./scheduling/01_introduction/00_overview.md**
  - 触发位置：表 A "集群调度"特性行的链接列。
  - 关系：本文档将"集群调度"列为四大特性之一，并把读者导流到 scheduling 子模块的 overview；该子模块对应表 E 中除 Container Manager 外的全部 14 个组件（Container Manager 是无 K8s 场景，与 scheduling 的 K8s 主路径相对）。
- **本文档 → 外部 ascend-deployer 仓（安装部署特性的独立仓）**
  - 表 A 中"安装部署"特性链接指向 gitcode 上的 `Ascend/ascend-deployer` 独立仓库，意味着 MindCluster 主仓与 ascend-deployer 仓**是分离维护**的，MindCluster 主仓只做引用。
- **本文档 → 外部性能测试手册（hiascend.com）**
  - 表 A 中"性能测试"特性链接指向华为云昇腾文档站点的 ToolBox 用户手册，说明性能测试功能由独立文档体系承载。
- **跨子模块的内部依赖**（基于组件名推断，原文未显式说明）：
  - Ascend Operator 生成集合通信配置 → 供 Volcano 调度/Ascend Docker Runtime 启动训练任务时挂载。
  - NPU Exporter 输出的利用率/温度/电压指标 → ClusterD 集群级统计的输入。
  - MindIO ACP + Elastic Agent（即将日落）→ 共同支撑表 A 中提到的"断点续训"能力。
  - Container Manager 与 K8s 调度路径（Volcano+Ascend Device Plugin+Ascend Operator）**互斥**——前者用于无 K8s 一体机，后者用于 K8s 集群。
- **生命周期联动**：Resilience Controller 与 Elastic Agent 在本文档中明确标注为"日落"，意味着下游 scheduling 子模块 overview 中的相关章节将在 2026 年 9 月 30 日 / 2026 年 12 月 30 日被删除。

---

## 【使用方法】

本文档是 overview 级，**未直接提供启用命令、YAML 配置项、参数开关或环境变量**。原文涉及的使用相关内容如下：

- **官方部署/安装路径**：通过 MindCluster Ascend Deployer 组件实现"一键式安装"，详细步骤指向外部 ascend-deployer 仓的 `01_introduction.md`（原文链接：https://gitcode.com/Ascend/ascend-deployer/blob/dev/docs/zh/01_introduction/01_introduction.md）。
- **性能测试工具入口**：通过 ToolBox（含 Ascend DMI、Ascend Cert）调用，详情指向华为云昇腾文档（原文链接：https://www.hiascend.com/document/detail/zh/mindcluster/2610/toolbox/toolboxug/toolboxug_0002.html）。
- **故障诊断使用**：通过 MindCluster Ascend FaultDiag 组件，详见仓库内 `./faultdiag/ascend-faultdiag/01_introduction/01_overview.md`。
- **集群调度使用**：通过 Volcano + Ascend Device Plugin + Ascend Operator 等组件组合，详见仓库内 `./scheduling/01_introduction/00_overview.md`。

具体的参数面网络配置命令、YAML 示例、环境变量列表、Pod Spec 模板、kubectl apply 步骤等，**本文档均未涉及**——这些内容在链接出去的下游子模块文档中展开。

## 图文联合解读

- `MindCluster堆栈图.png`: **图文联合解读**

图分三层：上层第三方DL平台（数据标注/训练/部署等）；中层MindCluster四模块——安装部署（Ascend Deployer、Cert）、性能测试（Ascend DMI）、故障诊断（Ascend FaultDiag）、集群调度（含Volcano、Ascend Device Plugin、ClusterD、MindIO等十余插件）；底层Kubernetes+CANN+计算/管理节点。

论证：MindCluster作为中间件层，以插件化方式接入K8s生态，对NPU资源做集群级调度、断点续训、集合通信及监控，向上屏蔽底层调度细节。

关系：直接支撑文档核心论点——"让深度学习平台厂商减少底层资源调度相关软件开发工作量，快速基于MindCluster构建平台"，图示清晰呈现其桥接上层AI业务与下层基础环境（K8s+CANN+节点）的分层解耦定位。
