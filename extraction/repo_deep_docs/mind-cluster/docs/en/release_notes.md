# Release Notes

> 仓 `mind-cluster` · 路径 `docs/en/release_notes.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mind-cluster/docs/en/release_notes.md

# MindCluster 26.0.0 Release Notes 深度解读

## 【定位】

本文档是 **MindCluster 组件代码仓 26.0.0 版本** 的官方 Release Notes (changelog),集中描述该版本的版本映射、组件兼容性矩阵、新增能力、接口变更以及已修复问题,为运维/集成人员提供版本选型与升级依据。

---

## 【技术要点】

1. **MindIO ACP / TFT 新能力**:ACP (Async CheckPoint Persistence) 与 TFT (Training Fault Tolerance);TFT 额外支持"精度异常后按指定 checkpoint 步数进行在线恢复"以及"iFLYTEK HULK 框架下的 optimizer 差异化副本场景"。
2. **MindCluster Ascend FaultDiag 增强**:新增 `Ascend-faultdiag-toolkit` 工具,支持 NPU 掉线和基础设施链路诊断;支持 Atlas 350 PCIe 卡故障排查;故障模式库不再打包进二进制,改为直接开源。
3. **服务面网络支持 IPv6**:ClusterD 等基础组件的服务面网络新增 IPv6 协议栈支持。
4. **gRPC 心跳间隔调整**:ClusterD 的 gRPC 心跳检测间隔由默认 **5 分钟** 调整为 **5 秒**,显著提升故障感知实时性。
5. **硬/软划分调度**:新增 Atlas A2/A3 系列的软划分 (soft partitioning) 与硬划分 (hard partitioning) 调度能力;支持 MindIE MoE EP 任务的交换机亲和性 (switch affinity) 调度;新增多级网络拓扑配置与多级网络亲和性配置;新增适配 Atlas 9000 A3 SuperPoD 集群计算系统的"任意层级网络亲和性调度算法"。
6. **自愈与强隔离机制**:支持按任务维度配置自愈故障级别/具体故障码;支持自愈故障后处理与不可自愈故障的重调度;支持基于集群维度识别硬件故障并对反复出现的硬件故障进行自动强制隔离,避免任务反复中断;集群维度与节点维度的自动强制隔离均支持配置自动释放时间。
7. **Atlas 350 PCIe 卡适配**:支持亲和性调度、设备发现、RankTable 生成、故障重调度;Ascend Docker Runtime 支持该卡型;任务资源请求 `huawei.com/Ascend910` 变更为 `huawei.com/npu`;底层 DCMI 切换为 DCMI V2;NPU Exporter 支持该卡型指标上报。
8. **ClusterD 接口/服务增强**:故障通知服务支持通过域名注册;任务信息订阅接口新增唯一任务标识字段;新增 `SubscribeJobSummarySignalList` 接口,首次订阅可返回历史任务信息;新增任务调度失败原因查询接口与基于文件的自定义指标接口;新增 `ConfigMap` 用于展示任务调度失败原因,便于故障定位。
9. **NPU Exporter 重构**:通过单一接口获取全部 NPU 利用率指标,避免多接口数据不一致;支持通过配置文件监听并上报自定义指标。
10. **Infer Operator**:可通过自定义 CRD 管理推理任务。

---

## 【关键机制与数据】

- **gRPC 心跳间隔变更**(原文):"The gRPC heartbeat detection interval of ClusterD is adjusted from the default 5 minutes to 5 seconds." → 心跳探测频率提升 60 倍,用于更快发现 ClusterD 与 agent 之间的连接异常。
- **资源请求资源名变更**(原文):"The task resource request `huawei.com/Ascend910` is changed to `huawei.com/npu`." → Atlas 350 PCIe 卡不再使用旧的 `Ascend910` 资源名,而是统一使用 `npu` 资源名,与 K8s 标准扩展资源风格保持一致。
- **底层驱动升级**(原文):"The underlying DCMI is changed to the DCMI V2." → DCMI (Device Chip Management Interface) 由 V1 升级到 V2,带来更细粒度的芯片管理能力。
- **故障模式库交付方式变更**(原文):"No longer supports building the fault mode library into a binary; the fault mode library is now directly open-sourced." → 故障模式库不再以二进制形式发布,改为源码直接开源,便于第三方定制和审查。
- **版本规划**(原文):"MindCluster 26.0 version planning: MindCluster 26.0.0, MindCluster 26.1.0, MindCluster 26.2.0, and MindCluster 26.0.3.0" → 26.0 主版本规划 4 个迭代小版本。
- **TaskD Agent 退出机制**(原文):"When resources such as MindIO processor are released and the program crashes, TaskD Agent cannot exit. A fallback exit mechanism is added." → 资源释放路径上的崩溃场景新增 fallback 退出兜底,避免进程残留。
- **TaskD Worker double free**(原文):"After training ends, when TaskD Worker calls the `mspti_activity_flush_all` method, a `double free` error is reported." → MindSpore profiler 活动刷新函数二次释放问题已修复。
- **TaskD Manager 并发 map 读写崩溃**(原文):"Concurrent map read/write by TaskD Manager causes process crash" → TaskD Manager 内部 map 并发访问已加锁或改为并发安全结构。

---

## 【表格解读】

### 表 1:Product Version Information (产品版本信息表)

| Name | MindCluster |
|---|---|
| Version Number | 26.0.0 |
| Version Type | Release Version |

**解读**:该表来自 `zh-cn_topic_0000001935094108`,即"产品版本信息"小节,定位本 Release Notes 描述的对象——正式发行的 MindCluster 26.0.0 版本。

---

### 表 2:Product Version Mapping (产品版本映射表)

| Product Name | Version |
|---|---|
| Ascend HDK | Atlas 350 PCIe card: 1.0.RC1<br>Other products: 26.0.RC1 |
| CANN | 9.0.0 |

**解读**:该表给出 MindCluster 26.0.0 发布版本必须配套的底层依赖版本——CANN 9.0.0 是唯一适配版本;Ascend HDK 对 Atlas 350 PCIe 卡要求 1.0.RC1,其他产品要求 26.0.RC1。注意 Atlas 350 PCIe 卡的 HDK 版本号(1.0.RC1)与其他产品(26.0.RC1)走不同的版本号体系。

---

### 表 3:Software Version Compatibility (Table 1 — 软件版本兼容性表)

| MindCluster Software Version | MindCluster Version to Upgrade | CANN Version | Ascend HDK Version | FrameworkPTAdapter Version | MindSpore Version |
|---|---|---|---|---|---|
| MindCluster 26.0.0 | MindCluster 7.0.RC1 and patch version<br>MindCluster 7.1.RC1 and patch version<br>MindCluster 7.2.RC1 and patch version<br>MindCluster 7.3.0 and patch version | CANN 8.5.0 and patch version<br>CANN 9.0.0 and patch version | Ascend HDK 25.5.0 and patch version<br>Ascend HDK 26.0.RC1 and patch version<br>Ascend HDK 1.0.RC1 and patch version | FrameworkPTAdapter 7.3.0 and patch version<br>FrameworkPTAdapter 26.0.0 and patch version | MindSpore 2.7.2 and patch version<br>MindSpore 2.9.0 and patch version |

**解读**:这是升级兼容矩阵——将 7.x 系列的 4 个 MindCluster 版本升级到 26.0.0 时,CANN 兼容 8.5.0+/9.0.0+;Ascend HDK 兼容 25.5.0+/26.0.RC1+/1.0.RC1+(对应 Atlas 350);FrameworkPTAdapter 兼容 7.3.0+/26.0.0+;MindSpore 兼容 2.7.2+/2.9.0+。文档明确强调"MindCluster 组件必须配套使用,请勿混用不同版本的组件"。

---

### 表 4:New Features (新功能表,节选核心)

| Feature | Description |
|---|---|
| MindIO ACP | Supports Async CheckPoint Persistence (ACP) and Training Fault Tolerance (TFT). |
| MindIO TFT | ①Supports ACP and TFT.<br>②Supports online recovery at specified checkpoint steps after precision anomalies.<br>③Supports optimizer-differentiated replica scenarios for the iFLYTEK HULK framework. |
| MindCluster Ascend FaultDiag | ①Supports troubleshooting for the Atlas 350 PCIe card.<br>②Adds Ascend-faultdiag-toolkit tool to support NPU disconnection and infrastructure link diagnosis.<br>③No longer supports building the fault mode library into a binary; the fault mode library is now directly open-sourced. |
| MindCluster basic components | ①Service plane network newly supports IPv6.<br>②Supports configuring self-healing fault levels or specific fault codes based on task dimensions.<br>③Soft partitioning-based scheduling for Atlas A2/A3 series.<br>④Hard partitioning-based scheduling for Atlas A2/A3 series.<br>⑤MoE EP tasks based on MindIE support switch affinity scheduling.<br>⑥ClusterD's gRPC heartbeat detection interval adjusted from 5 minutes to 5 seconds.<br>⑦Support post-processing of self-healing faults and rescheduling of non-self-healing faults.<br>⑧Identify whether a fault is a hardware fault based on the cluster dimension; recurring hardware faults are automatically and forcibly isolated.<br>⑨Both cluster dimension and node dimension automatic forced isolation support configuring an automatic release time.<br>⑩Network affinity scheduling algorithm of any level, adapted to the Atlas 9000 A3 SuperPoD cluster computing system.<br>⑪New `SubscribeJobSummarySignalList` interface, supports returning historical task information on the first subscription.<br>⑫A `ConfigMap` is added to display the reason for task scheduling failures.<br>⑬NPU Exporter supports listening and reporting custom metrics through configuration files.<br>⑭NPU Exporter refactored to obtain all NPU utilization metrics through a single interface.<br>⑮ClusterD fault notification service supports registration via domain name.<br>⑯ClusterD job information subscription interface adds a unique job identifier field.<br>⑰NPU Exporter supports metric reporting for the Atlas 350 PCIe card.<br>⑱Ascend Docker Runtime supports the Atlas 350 PCIe card.<br>⑲Atlas 350 PCIe card supports affinity scheduling, device discovery, RankTable generation, and fault rescheduling.<br>⑳Infer Operator can manage inference tasks through custom CRD. |

**解读**:新功能覆盖三大组件族——MindIO 侧(训练容错)、Ascend FaultDiag 侧(故障诊断工具化)、基础组件侧(调度/自愈/Exporter/容器运行时)。其中第⑥项是直接影响运维感知速度的关键变更,第⑬⑭项是 NPU Exporter 架构重构,第③⑨⑩⑲项均涉及 Atlas 系列卡的扩展支持。

---

### 表 5:Service Interface Changes (服务接口变更表)

| Feature | Interface Change |
|---|---|
| MindIO ACP | None |
| MindIO TFT | New `tft_register_exception_handler` interface that registers an exception handler. |
| MindCluster Ascend FaultDiag | New interfaces related to Ascend-faultdiag-toolkit. For details, see [API Description](./faultdiag/ascend-faultdiag-toolkit/01_api_description.md). |
| MindCluster basic components | ①Configuration fields for self-healing fault level, fault code, and self-healing duration are added to the task creation interface.<br>②Configuration fields for soft partitioning mode, AICore percentage, and high-bandwidth memory size are added to the task creation interface.<br>③ClusterD supports configuring the startup switch, triggering frequency, and isolation duration for automatic forced fault isolation.<br>④Ascend Device Plugin adds an isolation duration configuration field for automatic forced isolation.<br>⑤Support multi-level network topology configuration and multi-level network affinity configuration for tasks.<br>⑥New task information subscription interface `SubscribeJobSummarySignalList`.<br>⑦New interface for querying the cause of task scheduling exceptions.<br>⑧New file-based custom metric interface.<br>⑨The calculation method of the NPU utilization interface is optimized for NPU Exporter.<br>⑩Basic device information, fault code, and chip name for the Atlas 350 PCIe card are added. |

**解读**:接口层面无破坏性变更(仅 MindIO ACP 标注 "None"),其他均为新增配置字段或新接口,与 New Features 表形成"功能 ↔ 接口"对应关系。

---

## 【公式解读】

原文无公式。

---

## 【关联】

本文档与代码仓其他章节的关联路径:

- **[`./faultdiag/ascend-faultdiag-toolkit/01_api_description.md`](./faultdiag/ascend-faultdiag-toolkit/01_api_description.md)** :在 "Service Interface Changes" 表中针对 Ascend FaultDiag 明确引用,该章节是 `Ascend-faultdiag-toolkit` 工具新增接口的 API 详细说明。本 Release Notes 仅在表层提及"新增相关接口",具体签名、参数、返回值等细节见该 API 描述文档。
- **[`./scheduling/introduction/00_overview.md`](./scheduling/introduction/00_overview.md)** :与本文档 "MindCluster basic components" 中的软/硬划分调度、MoE EP 交换机亲和性调度、多级网络亲和性调度、Atlas 9000 A3 SuperPoD 任意层级网络亲和性算法等特性紧密相关,概述性介绍应在该调度章节中给出。
- **[`./faultdiag/introduction.md`](./faultdiag/introduction.md)** :对应 MindCluster Ascend FaultDiag 总体介绍,本文档提到的故障模式库开源、Atlas 350 故障排查、基础设施链路诊断等能力应在该 introduction 中给出整体定位。

模块上下游视角:本文档涉及的 `MindIO ACP/TFT` 提供训练任务侧的 checkpoint 持久化与容错;`Ascend FaultDiag` 提供故障侧的工具化诊断;`MindCluster basic components` (含 ClusterD、TaskD、NPU Exporter、Ascend Device Plugin、Ascend Docker Runtime、Infer Operator) 是底座,提供调度、自愈、Exporter、设备插件、容器运行时等基础设施;三者组合形成 MindCluster 完整的"任务-调度-故障"闭环。

---

## 【使用方法】

本文档未涉及具体的启用命令或配置示例,仅在以下方面给出指引:

- **版本选型**:依据"Product Version Mapping"表选取配套的 CANN(9.0.0)与 Ascend HDK(Atlas 350 用 1.0.RC1,其他用 26.0.RC1)。
- **升级路径**:依据"Software Version Compatibility"表确认是否可从现有 7.0.RC1/7.1.RC1/7.2.RC1/7.3.0 升级到 26.0.0;同时确认 CANN/Ascend HDK/FrameworkPTAdapter/MindSpore 版本在兼容范围内。
- **API 调用方式**:对于新增的 `Ascend-faultdiag-toolkit` 接口,具体调用方法见 `./faultdiag/ascend-faultdiag-toolkit/01_api_description.md`。
- **版本使用注意事项**:"Version Usage Notes" 一节内容为 **None**——即没有特殊的强制使用限制。
