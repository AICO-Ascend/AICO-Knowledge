# MindIE Motor架构

> 仓 `mindie-motor` · 路径 `docs/zh/architecture.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-motor/docs/zh/architecture.md

# MindIE Motor 架构文档深度解读

## 【定位】
这篇文档描述 **MindIE Motor**——昇腾自研推理集群管理框架的整体架构与核心能力，目的是阐明其作为**面向 LLM 分布式推理（尤其是 PD 分离推理）的请求调度框架**如何组织组件、调度请求并提供 RAS 能力。

---

## 【技术要点】

1. **核心定位与命名变更**：MindIE Motor 是一套面向大语言模型（LLM）分布式推理、专攻 **PD 分离推理**（Prefill 与 Decode 阶段分离）的请求调度框架。原 MindIE PyMotor 代码仓**自 3.1.0 版本起更名为 MindIE Motor**，软件定位与基本功能保持不变。

2. **两大核心能力**：
   - **PD 分离的请求调度**：将外部客户请求分发到负载最低的 Prefill/Decode 实例，起**负载均衡**作用。
   - **RAS（Reliability, Availability and Serviceability）**：增强 PD 分离服务的可靠性、可用性与可服务性。

3. **运行时引擎对接**：通过开放、可扩展的推理服务化平台架构对接以下两类原生运行时：
   - [vLLM-Ascend](https://github.com/vllm-project/vllm-ascend)（**当前主要以 vLLM-Ascend 为主**）
   - **SGLang**（原生运行时接入，支持范围以[支持的推理引擎](./user_guide/features/supported_inference_engines.md) 为准）

4. **核心组件划分**：采用 **Coordinator + Controller + Deployer + NodeManager** 四级组件分层：
   - Coordinator（统一入口 / 数据流枢纽）
   - Controller（状态管控器 / 决策大脑）
   - Deployer（基于 Kubernetes 的部署参考脚本）
   - NodeManager（节点级服务管理器）

5. **请求入口接口**：Coordinator 对外提供两类 RESTful 接口：
   - **业务面**：OpenAI 接口
   - **管理面**：健康探针、Metrics

6. **运维集成路径**：通过 **CCAEReporter** 将实例状态及 Metrics 同步至 [CCAE](https://www.hiascend.com/software/ccae) 华为算存网一体化运维可视化平台（**可选**）。

---

## 【关键机制与数据】

### 工作原理 / 数据流
> **原文**："Coordinator 作为用户推理请求的**统一入口**，负责接收高并发请求，执行请求调度、管理与转发，是整个集群的数据流枢纽。"

数据流主线（基于原文描述提取）：
1. **外部请求** → Coordinator（Endpoint RESTful 接口）→ Router 路由转发 → Scheduler 负载均衡调度。
2. **请求进入** → RequestManager 进行请求全局信息统计与管理；InstanceManager 同步实例健康状态、辅助负载均衡、**隔离故障实例**。
3. **PD 实例身份** 由 Controller 中的 **InsManager** 分配与动态调整（分配为 Prefill 或 Decode）。
4. **下层实例** 由 **NodeManager** 在每个节点拉起原生 vLLM 或 SGLang 进程，并向 Controller 上报**健康状态和心跳**。
5. **故障路径**：故障由 **FaultManager** 接收并执行**隔离、重启、自愈恢复**等操作。
6. **状态同步**：Controller 通过 **EventPusher** 把实例状态信息推送给 Coordinator。

### 性能/规模数据
**原文未涉及**任何具体的性能数字、TPS、延迟、QPS、吞吐、实例数等量化指标。文中未出现可定量衡量的数据。

---

## 【表格解读】

**原文无表格**。

（整篇文档为架构描述，未出现参数表、配置项表或性能对比表。）

---

## 【公式解读】

**原文无公式**。

（未出现任何 LaTeX 或伪代码形式的数学/算法公式。）

---

## 【关联】

依据文中引用与文末内部链接信息，MindIE Motor 与以下特性/模块/上下游系统存在显式关联：

| 关联对象 | 原文定位与作用 | 关联方式 |
|---|---|---|
| **[vLLM-Ascend](https://github.com/vllm-project/vllm-ascend)** | vLLM 加速引擎，提供**模型实例加速能力** | 作为原生运行时由 NodeManager 拉起；当前**主要接入引擎** |
| **SGLang** | 可通过 NodeManager 原生运行时接入的推理引擎 | **支持范围**见 [`./user_guide/features/supported_inference_engines.md`](./user_guide/features/supported_inference_engines.md)（文末提供的唯一内部链接） |
| **[MindCluster](https://gitcode.com/Ascend/mind-cluster)** | 昇腾集群使能组件，提供 Kubernetes 底层支持，**PD 分离 CRD 定义和配套 Operator** | 作为 Deployer 与 Kubernetes 之间的底层使能层 |
| **[CCAE](https://www.hiascend.com/software/ccae)**（**可选**） | 华为算存网一体化运维可视化平台 | Controller 的 CCAEReporter 将实例状态与 Metrics 上报至此 |
| **OpenAI 接口** | 业务面标准接口 | 由 Coordinator Endpoint 对外暴露 |
| **Kubernetes** | 容器编排与调度底座 | Deployer 基于其提供启动/停止/弹性伸缩能力；启用 [健康探针](https://kubernetes.io/zh-cn/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/) |

组件间上下游链路（按数据流方向）：
```
客户请求 → [Coordinator: Endpoint → Router → Scheduler → RequestManager/InstanceManager]
                                                       ↓
                                  NodeManager 拉起原生 vLLM/SGLang 进程
                                                       ↓
                                  [Controller: InsManager 分配 PD 身份 / FaultManager 故障处置]
                                                       ↓
                          EventPusher → Coordinator  │  CCAEReporter → CCAE
                                                       ↓
                            Deployer（K8s + MindCluster CRD/Operator）
```

---

## 【使用方法】

**原文未涉及**。

本文档为 **overview / 架构说明性质**，未出现具体的：
- 启用命令 / 启动指令
- 配置项 / 参数文件路径
- 环境变量 / 集群搭建步骤

实际启用方式、配置项与命令细节需参考文档所属仓中其他章节（如文末指向的 `user_guide/features/supported_inference_engines.md` 以及用户指南中部署、运维相关章节），本文不臆造。

## 图文联合解读

- `MindIE_Motor_Architecture.png`: 图示：OpenAI请求→Coordinator调度→Prefill/Decode；Controller/EventPusher回传实例/健康，NodeManager管理，EngineServer/vLLM执行，Mooncake传KV，Deployer部署。结论：支撑PD分离和RAS，契合文档定位。
