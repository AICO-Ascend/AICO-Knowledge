# Introduction

> 仓 `mind-cluster` · 路径 `docs/en/faultdiag/introduction.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mind-cluster/docs/en/faultdiag/introduction.md

# MindCluster Ascend FaultDiag Introduction 深度解读

## 【定位】

本文档是 MindCluster Ascend FaultDiag 智能故障诊断特性的总览(Overview)文档,系统介绍其面向 AI 集群训练/推理任务的**日志清洗(Log Cleaning)与故障诊断(Fault Diagnosis)能力**,明确功能边界(诊断 vs. 采集)、目标用户、典型应用场景及端到端使用流程,是后续各 user_guide 章节(日志采集/清洗/诊断)的入口说明。

---

## 【技术要点】

1. **两大核心功能**:Log Cleaning + Fault Diagnosis;前者从原始训练/推理日志中过滤提取关键信息,后者跨节点聚合分析并定位根因。
2. **清洗覆盖的数据源**:用户训练/推理日志、CANN App 日志、Host 侧资源信息、NPU 网口资源信息,以及监控指标(metrics)。
3. **诊断覆盖的两类故障**:
   - **训练/推理任务异常退出**:根因节点分析(基于 HCCL 报错信息定位根因节点) + 故障事件分析(基于故障知识图谱的故障模式匹配设备根因错误)。
   - **训练/推理性能下降**:设备资源分析(算力降频、CPU 资源抢占) + 网络拥塞分析(Spine + Leaf 组网下分析 NPU 网口监控指标,定位节点链路拥塞)。
4. **重要 NOTE 约束**:性能下降类诊断**仅在任务未异常退出时**才会触发。
5. **端到端使用流程 4 步**:Log collection → Log cleaning → Cleaning result dumping → Fault diagnosis;前两步和第 3 步不是 FaultDiag 自身提供的能力,文档只提供操作指导。
6. **两类应用场景**:Full-Process(企业/政府/事业单位级 AI 集群 O&M 平台,采集内容复杂,含 host 侧资源、硬件相关数据)与 Basic(个人用户,仅需训练/推理 + CANN 日志)。
7. **可扩展能力**:支持用户在 CANN App 日志中自定义故障实体或对 ERROR 消息进行屏蔽(masking)。

---

## 【关键机制与数据】

- **根因节点定位机制(原文)**:基于集群通信 HCCL 报错信息,定位触发错误的根因节点(Root cause node)。
- **故障事件分析机制(原文)**:基于故障知识图谱(fault knowledge graph)中包含的故障模式,分析根因节点所在设备的根因错误。
- **设备资源分析方法(原文)**:通过分析用户采集的设备相关 metric 文件,定位算力降频(computing frequency reduction)和 CPU 资源抢占(CPU resource contention)等问题。
- **网络拥塞分析方法(原文)**:通过分析用户采集的 NPU 网口监控 metric 文件,分析节点链路是否存在网络拥塞异常,**典型场景为 Spine + Leaf 组网**。
- **跨节点聚合机制(原文)**:清洗结果从所有训练/推理设备转储(dump)并聚合并存储到一台训练设备或通用设备上,按预定义结构存储,供诊断模块使用。
- **清洗输出(原文)**:清洗结果与原始信息一同 dump 到同一路径,Original logs + metric info + cleaning results 三类数据共存于 O&M 平台。
- **性能数据**:原文未给出具体的吞吐量、延迟、采样率或诊断准确率等量化指标。

---

## 【表格解读】

### 表格 1:Fault Classification(诊断分类)

**原文逐字还原:**

| Fault Classification | Diagnostic Content |
|--|--|
| Abnormal exit of training and inference tasks | <ul><li>Root cause node analysis: Based on the HCCL error message of cluster communication, locate the root cause node that triggered the error.</li><li>Fault event analysis: Analyze the root cause error of the device where the root cause node resides based on the fault patterns contained in the fault knowledge graph.</li></ul> |
| Performance degradation during training and inference | <ul><li>Device resource analysis for device resource status: By analyzing the device-related metric files collected by the user, locate issues such as computing frequency reduction and CPU resource contention.</li><li>Network congestion analysis: Analyze the network status between nodes, typically used to locate network issues in Spine + Leaf networking scenarios. By analyzing the NPU network port's monitoring metric files collected by the user, it analyzes whether network congestion anomalies occur on node links.</li></ul> |

**逐行解读:**
- **第 1 行(异常退出类)**:左侧为触发条件——训练/推理任务异常退出;右侧包含两种诊断维度:**① 根因节点分析**,依托 HCCL 集群通信报错作为触发源,目标是找到"谁先报错";**② 故障事件分析**,在已确定根因节点后,通过故障知识图谱匹配该节点所在设备的根因错误(即"为什么是这个设备")。
- **第 2 行(性能下降类)**:左侧为触发条件——训练/推理性能下降(任务未异常退出,见 NOTE);右侧同样包含两种维度:**① 设备资源分析**,通过对用户提供的 device metric 文件做离线分析,定位"算力降频"和"CPU 抢占"两类常见问题;**② 网络拥塞分析**,分析 NPU 网口 metric,典型目标场景是数据中心级 Spine + Leaf 架构,目的是发现"节点间链路"是否拥塞。

### 表格 2:Usage Process(使用流程)

**原文逐字还原:**

| Step | Description | Reference |
|--|--|--|
| Log collection | <p>When a training or inference task fails or becomes abnormal, collect logs from each training or inference device and store them according to a predefined structure.</p><p>For details about the logs to be collected, see the "Table. Training and inference task log and metric information" in [Application Scenarios and Solutions](#application-scenarios-and-solutions).</p> | For details, see the [Log Collection](./user_guide/03_collecting_logs.md) section. |
| Log cleaning | After log collection is complete, use the cleaning function of MindCluster Ascend FaultDiag on each training or inference device to clean the collected raw logs and metric data, filtering and extracting valid information. | For details, see [Log Cleaning and Dumping](./user_guide/06_cleaning_and_dumping_logs.md). |
| Cleaning result dumping | After log cleaning is complete, dump and aggregate the cleaning results from each training or inference device to a single training device or general-purpose device, and store them according to a predefined structure. | For details, see [Log Cleaning and Dumping](./user_guide/06_cleaning_and_dumping_logs.md). |
| Fault diagnosis | Based on the aggregated cleaning results, use the diagnosis function of MindCluster Ascend FaultDiag to analyze the root cause of the training or inference task failure or abnormality. | For details, see [Fault Diagnosis](./user_guide/07_diagnosing_faults.md). |

**逐行解读:**
- **Step 1 - Log collection**:日志采集。**触发时机**是训练/推理任务失败或异常时;**操作主体**是"每台训练/推理设备",**存储约束**是"按预定义结构"(predefined structure);采集内容范围参见 Application Scenarios 中的"Training and inference task log and metric information"表。指向 `./user_guide/03_collecting_logs.md`。
- **Step 2 - Log cleaning**:日志清洗。FaultDiag 自带能力,在**每台设备本地**对原始日志和 metric 做过滤与有效信息提取。指向 `./user_guide/06_cleaning_and_dumping_logs.md`。
- **Step 3 - Cleaning result dumping**:清洗结果转储与聚合。将各设备清洗结果**汇聚到一台训练设备或通用设备**(general-purpose device),按预定义结构存储。指向 `./user_guide/06_cleaning_and_dumping_logs.md`(与上一步同一文档)。
- **Step 4 - Fault diagnosis**:故障诊断。在聚合后的结果之上,由 FaultDiag 诊断模块给出训练/推理任务失败或异常的根因。指向 `./user_guide/07_diagnosing_faults.md`。

### 表格 3:Application Scenarios(应用场景)

**原文逐字还原:**

| Scenario | User | Task Type | Characteristics |
|--|--|--|--|
| [Full-Process Application Scenario](#section1511514596338) | Enterprises, governments, public institutions, etc. (with AI cluster O&M platform capabilities) | Training and inference tasks | The collection content is relatively complex, due to its dependency on training and inference logs, CANN, host-side resources, and hardware-related data. This scenario is suitable for AI cluster O&M platform users performing complex task diagnosis. |
| [Basic Application Scenario](#section587911381388) | Individuals | Training and inference tasks | The collection content and method are simple, because only the training and inference logs, CANN logs are required. This scenario is suitable for individual users performing basic task diagnosis. |

**逐行解读:**
- **第 1 行(Full-Process)**:面向企业/政府/事业单位等**具备 AI 集群 O&M 平台能力**的用户;任务类型覆盖训练与推理;特点是**采集内容复杂**,依赖训练/推理日志、CANN、host 侧资源及硬件相关数据,适合做**复杂任务诊断**的集群平台用户。
- **第 2 行(Basic)**:面向个人用户(Individuals);同样覆盖训练与推理;特点是**采集内容和方法简单**,只需训练/推理日志 + CANN 日志,适合个人用户做**基础任务诊断**。

---

## 【公式解读】

原文无公式。

---

## 【关联】

根据文末给出的内部链接,本文档与以下 user_guide 章节构成上下游关系:

- **[Log Collection - `./user_guide/03_collecting_logs.md`](./user_guide/03_collecting_logs.md)**:本 overview 中"Step 1 Log collection"指向该文档,负责介绍训练/推理任务异常时各设备日志如何按预定义结构采集(注:该能力并非 FaultDiag 自身提供)。
- **[Log Cleaning and Dumping - `./user_guide/06_cleaning_and_dumping_logs.md`](./user_guide/06_cleaning_and_dumping_logs.md)**:本文档中"Step 2 Log cleaning"与"Step 3 Cleaning result dumping"均指向该文档,介绍 FaultDiag 在每台设备上清洗原始日志/metric,以及把清洗结果跨设备汇聚到一台训练/通用设备的过程。
- **[Fault Diagnosis - `./user_guide/07_diagnosing_faults.md`](./user_guide/07_diagnosing_faults.md)**:本文档中"Step 4 Fault diagnosis"指向该文档,基于聚合后的清洗结果执行根因节点定位、故障事件分析、设备资源分析、网络拥塞分析。

**模块自洽关系**:本文档中明确指出"Log collection"和"Cleaning result dumping"**不是 MindCluster Ascend FaultDiag 提供的功能**,本文仅提供操作指导,真正的能力边界仅覆盖"Log cleaning"与"Fault diagnosis"。下游章节的依赖顺序为:`03_collecting_logs` → `06_cleaning_and_dumping_logs` → `07_diagnosing_faults`,而本文档是其共同入口。

---

## 【使用方法】

**端到端使用流程(原文流程表):**

1. **Log collection(日志采集)**:任务失败或异常时,按预定义结构采集每台训练/推理设备的日志与 metric;详见 `./user_guide/03_collecting_logs.md`。
2. **Log cleaning(日志清洗)**:在每台训练/推理设备上调用 FaultDiag 的清洗功能,对原始日志与 metric 做过滤与有效信息提取;详见 `./user_guide/06_cleaning_and_dumping_logs.md`。
3. **Cleaning result dumping(清洗结果转储)**:将各设备的清洗结果 dump 并聚合到一台训练设备或通用设备上,按预定义结构存储;详见 `./user_guide/06_cleaning_and_dumping_logs.md`。
4. **Fault diagnosis(故障诊断)**:基于聚合后的清洗结果,调用 FaultDiag 的诊断功能分析训练/推理任务失败或异常的根因;详见 `./user_guide/07_diagnosing_faults.md`。

**关键约束(原文 NOTE 复述):**
- 性能下降类问题(算力降频、CPU 抢占、网络拥塞)只在任务**未异常退出**时才会被诊断。
- 日志采集与清洗结果转储**不是 FaultDiag 自身功能**,仅提供操作指导。
- 输入数据须由用户保证不含敏感信息或个人数据(免责声明)。
- 支持用户在 CANN App 日志中**自定义故障实体**或**对 ERROR 消息做屏蔽**。

原文未涉及具体的 CLI 命令、配置文件路径、YAML/JSON schema、参数项或 API 调用示例(这些细节应分别在 `./user_guide/03_collecting_logs.md`、`./user_guide/06_cleaning_and_dumping_logs.md`、`./user_guide/07_diagnosing_faults.md` 中查阅)。
