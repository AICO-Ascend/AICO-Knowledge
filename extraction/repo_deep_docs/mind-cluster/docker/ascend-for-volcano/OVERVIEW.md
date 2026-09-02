# Cluster Scheduling Component Atlas for Volcano

> 仓 `mind-cluster` · 路径 `docker/ascend-for-volcano/OVERVIEW.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mind-cluster/docker/ascend-for-volcano/OVERVIEW.md

# mind-cluster · docker/ascend-for-volcano/OVERVIEW.md 一体化深度解读

---

## 【定位】

**这篇文档解决什么问题**：介绍"Atlas for Volcano"（Atlas 集群调度组件 for Volcano）这一基于开源 Volcano 调度插件机制扩展而来的、面向 Atlas AI 处理器（NPU）的集群调度组件，阐明其能力边界（亲和调度、故障重调度、多级资源调度等）、镜像构成、Tag 命名规则与容器镜像/Dockerfile 链接，便于使用者快速选型、定位构建产物与获取帮助。

---

## 【技术要点】

1. **组件定位**：基于开源 Volcano 的调度插件机制增强，新增 **Atlas AI 处理器（NPU）亲和调度**与**虚拟设备（vDevice）调度**，以管理面（management node）形态部署；其调度插件产物为 `volcano-npu_*.so`，随 `volcano-scheduler` 镜像发布。

2. **核心能力（Features，原文逐条对应）**：
   - **Available Device Calculation**：根据下层集群调度组件上报的故障/节点信息计算集群可用设备；`self-maintain-available-card` **默认启用**；关闭时由下层组件提供可用设备信息。
   - **Optimal Resource Allocation**：从 Kubernetes Job 对象读取用户期望资源数，按集群设备**数量/类型/网络拓扑**选取最优分配。
   - **Fault Rescheduling**：当作业资源遇故障时触发重调度。
   - **NPU Affinity Scheduling**：依据互联拓扑优先级——**同卡内 优先 → HCCS 互联 优先 → PCIe 互联 兜底**，降低碎片与网络拥塞。
   - **Switch Affinity Scheduling**：基于交换机下挂网络配置 + 参数面（parameter plane）网络配置实现最优节点利用，支持 **Spine-Leaf 双层互联、单层交换机互联** 等拓扑。
   - **Logical Super Node Affinity Scheduling**：按划分策略把物理超节点切成逻辑超节点，追求最优节点利用率。
   - **Multi-level Scheduling Strategy**：把集群资源按 NPU 网络拓扑层级抽象成多级结构，通过 `resource-level-config` 参数配置。
   - **Multiple Scheduling Modes**：支持**整卡调度（whole-card）/ 静态 vNPU 调度 / 动态 vNPU 调度 / 软分（soft-partition）调度** 四种。

3. **亲和策略优先级（Priority Order，原文逐条）**：基于 Atlas 910 AI 处理器特征与资源利用规则
   1. **HCCS Affinity Scheduling Principle**：所请求的 Atlas 910 必须在**同一 HCCS ring** 内，并优先选剩余可用处理器最匹配数量的 HCCS；
   2. **Fill-First Scheduling Principle**：优先复用**已分配有 Atlas 910 的 AI server**，减少碎片；
   3. **Even-Remaining Priority Principle**：在满足前两条的 HCCS 中，优先选剩余处理器数为**偶数**的 HCCS。

4. **上下游依赖关系（Upstream/Downstream，原文 3 条）**：
   - 上游：**ClusterD**（默认情况下）上报信息 → 用于计算集群资源；
   - 输入：接收第三方作业启动配置 + 集群资源信息 → 选出最优节点资源；
   - 下游：把资源选型结果传给**计算节点的 Atlas Device Plugin** 完成挂载。

5. **镜像构成**：组件由两张镜像组成——
   - `volcano-scheduler`：Volcano scheduler 镜像，内置 **Atlas NPU 亲和调度插件 `volcano-npu_*.so`**；
   - `volcano-controller`：Volcano controller 镜像。

6. **Tag 命名约定（自 v26.1.0 起生效）**：`<component-version>-<ascend-scheduling-plugin-version>-<os>`，三段含义分别为 Volcano 组件版本（如 `v1.7.0` / `v1.12.0` / `v1.9.0`）、Atlas NPU Scheduler Plugin 版本（`v26.1.0`）、基础 OS（`alpinelatest` / `openeuler24.03`）。

---

## 【关键机制与数据】

**关键机制（工作原理 / 数据流）**：

- **数据采集 → 算可用 → 选资源 → 挂载** 的闭环链路：
  1. 计算节点侧的**下层集群调度组件**（默认是 ClusterD）将**故障信息 + 节点信息**上报；
  2. Atlas for Volcano（管理面）依据上述信息**计算集群可用设备**（`self-maintain-available-card` 默认开启时为本地自维护，否则采用下层结果）；
  3. 第三方提交 K8s Job，调度器读取 Job 中期望资源数，按"设备数 / 设备类型 / 网络拓扑"和**多级调度策略（`resource-level-config`）**选出最优节点集合；
  4. 把具体资源选择信息下发给**计算节点的 Atlas Device Plugin** 完成设备挂载。

- **多级亲和兜底顺序**：**卡内 → HCCS 互联 → PCIe 互联** —— 同卡最优；卡间优先选同一 HCCS ring；再退化为 PCIe。这与 NPU 间高速互联带宽由高到低的物理现实一致，目的是降低碎片与网络拥塞。

- **Topology-aware Switch 调度**：在交换机维度，按 Spine-Leaf 双层 / 单层交换机两种物理形态，结合参数面网络配置做分配，并在 **Logical Super Node** 上叠加逻辑划分策略。

- **故障感知重调度**：作业已分配的 NPU 出现故障时触发 Fault Rescheduling，从可用资源池中再选节点。

**性能/规模类数字（原文无明确吞吐/时延/SLO 数据）**：
- 原文只给出**镜像版本号**与**Tag 段位数**，未列出任何 TPS / 延迟 / 吞吐 / 故障率等性能数字。`原文：未提供性能数据。`

---

## 【表格解读】

### 表 1 · Tag Convention（标签格式说明，原文逐字还原）

| 字段 | 示例值 | 说明 |
|---|---|---|
| `component-version` | `v1.7.0` | Version Number of Volcano component |
| `ascend-scheduling-plugin-version` | `v26.1.0` | Version Number of Atlas NPU Scheduler Plugin |
| `os` | `alpinelatest` | Operating System for Volcano Images |

解读：该表是自 **Atlas NPU Scheduler Plugin v26.1.0** 起启用的 Tag 三段式命名约定——
- `component-version`：指 Volcano 上游组件的版本号，决定 Scheduler/Controller 走 v1.12.0 还是 v1.9.0 等支线。
- `ascend-scheduling-plugin-version`：本仓库独有的 Atlas NPU 调度插件版本号；同一组件可对应多种插件版本组合。
- `os`：基础操作系统，本文中可见两种 —— `alpinelatest`（Alpine latest）与 `openeuler24.03`（openEuler 24.03 LTS）。

### 表 2 · Atlas for Volcano 26.1.0（Volcano v1.12.0，原文逐字还原）

| Tag | Dockerfile | Image Content |
|---|---|---|
| `v1.12.0-v26.1.0-alpinelatest` | [Dockerfile-scheduler.alpine](https://gitcode.com/Ascend/mind-cluster/blob/master/docker/ascend-for-volcano/volcano-v1.12.0/v26.1.0/Dockerfile-scheduler.alpine) | Volcano Scheduler v26.1.0 Image (Including Atlas NPU Scheduler Plugin, based on Volcano v1.12.0, Base Image: Alpine latest) |
| `v1.12.0-v26.1.0-alpinelatest` | [Dockerfile-controller.alpine](https://gitcode.com/Ascend/mind-cluster/blob/master/docker/ascend-for-volcano/volcano-v1.12.0/v26.1.0/Dockerfile-controller.alpine) | Volcano Controller v26.1.0 Image (based on Volcano v1.12.0, Base Image: Alpine latest) |
| `v1.12.0-v26.1.0-openeuler24.03` | [Dockerfile-scheduler.openeuler](https://gitcode.com/Ascend/mind-cluster/blob/master/docker/ascend-for-volcano/volcano-v1.12.0/v26.1.0/Dockerfile-scheduler.openeuler) | Volcano Scheduler v26.1.0 Image (Including Atlas NPU Scheduler Plugin, based on Volcano v1.12.0, Base Image: openEuler 24.03) |
| `v1.12.0-v26.1.0-openeuler24.03` | [Dockerfile-controller.openeuler](https://gitcode.com/Ascend/mind-cluster/blob/master/docker/ascend-for-volcano/volcano-v1.12.0/v26.1.0/Dockerfile-controller.openeuler) | Volcano Controller v26.1.0 Image (based on Volcano v1.12.0, Base Image: openEuler 24.03) |

解读：这一组镜像同时绑定两个版本维度——
- **Volcano 上游版本固定 v1.12.0**（更上游的 Volcano 主版本）；
- **Atlas NPU 调度插件版本固定 v26.1.0**（Atlas 自家插件版本）；
- **OS 维度**按 `alpinelatest` / `openeuler24.03` 切两组，每组各对应 scheduler 与 controller 各一张镜像，因此共 4 个 Tag × Dockerfile 组合。注意前两行与后两行 Tag 字段文字完全相同，是因为 scheduler 和 controller 共用同一 Tag —— 使用者需要按 Image Content（"Scheduler/Controller"）来区分功能，同一 Tag 下两个镜像各司其职。

### 表 3 · Atlas for Volcano 26.1.0（Volcano v1.9.0，原文逐字还原，文档截断处依旧保留可见部分）

| Tag | Dockerfile | Image Content |
|---|---|---|
| `v1.9.0-v26.1.0-alpinelatest` | [Dockerfile-scheduler.alpine](https://gitcode.com/Ascend/mind-cluster/blob/master/docker/ascend-for-volcano/volcano-v1.9.0/v26.1.0/Dockerfile-scheduler.alpine) | Volcano Scheduler v26.1.0 Image (Including Atlas NPU Scheduler Plugin, based on Volcano v1.9.0, Base Image: Alpine latest) |
| `v1.9.0-v26.1.0-alpinelatest` | [Dockerfile-controller.alpine](https://gitcode.com/Ascend/mind-cluster/blob/master/docker/ascend-for-volcano/volcano-v1.9.0/v26.1.0/Dockerfile-controller.alpine) | Volcano Controller v26.1.0 Image (based on Volcano v1.9.0, Base Image: Alpine latest) |
| `v1.9.0-v26.1.0-openeuler24.03` | [Dockerfile-scheduler.openeuler](https://gitcode.com/Ascend/mind-cluster/blob/master/docker/ascend-for-volcano/volcano-v1.9.0/v26.1.0/Dockerfile-sched…（原文截断） | Volcano Scheduler v26.1.0 Image (Including Atlas NPU Scheduler Plugin, based on Volcano v1.9.0, Base Image: openEuler 24.03) |

解读：与表 2 同结构但**上游 Volcano 版本锁定 v1.9.0**（老支线，用于需要兼容既有 Volcano 部署的场景）。可见 Tag 命名严格遵守 `<component-version>-<ascend-scheduling-plugin-version>-<os>` 三段式：第一个字段从 `v1.12.0` 变成 `v1.9.0`，其余字段保持与表 2 完全一致，证明 Tag 三段之间是**正交的版本维度**。受原文截断影响，本表第 4 行未在原始 OVERVIEW.md 中给出（原文出现 `00_introduction/00_overview.md` 类似渲染问题而截断），故不臆造。

---

## 【公式解读】

**原文无公式**。原文以自然语言枚举亲和优先级与镜像产物，**没有出现 LaTeX 数学式、伪代码或带运算符的公式**。

---

## 【关联】

**上游 → 本组件 → 下游**：

- **上游（数据源）**：[ClusterD](https://gitcode.com/Ascend/mind-cluster)（默认情况下）。ClusterD 把节点与故障信息推送给 Atlas for Volcano，用于"可用设备计算"；当 `self-maintain-available-card` 被关闭时，Atlas for Volcano 直接采用下层（ClusterD 或类似下层集群调度组件）的可用设备结果。
- **平级/输入**：Kubernetes Job / 第三方客户端——提交的资源请求与启动配置被 Atlas for Volcano 消费，用于驱动"最优资源分配"与"故障重调度"。
- **下游（落地执行）**：**Atlas Device Plugin**（运行在计算节点上）—— 接收资源选择信息并在节点侧完成 NPU 设备挂载。
- **组件身份**：本仓库 `mind-cluster` 中的 **Atlas for Volcano 镜像组**——`volcano-scheduler` 内置 `volcano-npu_*.so` 插件；`volcano-controller` 提供 Volcano 控制面。
- **代码仓定位**：本组件由 **MindCluster Repository** 维护，可通过文末 issue tracker 与中文社区（MindCluster Atlas Community）获取帮助；内部链接 `./OVERVIEW.zh.md` 给到同一文档的中文镜像。
- **平行能力**：与本仓库中其他 MindCluster 组件并列——例如以 ClusterD 为代表的"下层集群调度组件"承担数据上报与维护工作，而 Atlas for Volcano 与 Atlas Device Plugin 共同把"亲和调度 + 设备挂载"串成端到端的 NPU 集群调度链路。

---

## 【使用方法】

**原文未直接给出"启用命令 / 部署 YAML / Helm values"。** 仅给出的可操作信息按原文照录如下：

- **镜像 Tag 选择**（依据表 1 ~ 表 3）：
  - 选 **Volcano v1.12.0 + Atlas Plugin v26.1.0**：`v1.12.0-v26.1.0-alpinelatest` 或 `v1.12.0-v26.1.0-openeuler24.03`（scheduler / controller 各一张镜像）。
  - 选 **Volcano v1.9.0 + Atlas Plugin v26.1.0**：`v1.9.0-v26.1.0-alpinelatest` 或 `v1.9.0-v26.1.0-openeuler24.03`。
- **关键开关 / 参数（原文明确提到）**：
  - `self-maintain-available-card`：可用设备信息自维护开关，**默认启用**；关闭后由下层组件提供。
  - `resource-level-config`：多级调度策略的层级结构配置参数，依据 NPU 网络拓扑层级把集群资源抽象成多级。
- **能力开关（通过 Job / 设备插件配合实现，原文未给出具体字段名）**：整卡调度、静态 vNPU、动态 vNPU、软分（soft-partition）四种调度模式；具体开关字段与配置示例 `原文未涉及`。
- **获取帮助**（原文 Quick Reference）：
  - MindCluster Repository：[https://gitcode.com/Ascend/mind-cluster](https://gitcode.com/Ascend/mind-cluster)
  - Issue Tracker：[https://gitcode.com/Ascend/mind-cluster/issues](https://gitcode.com/Ascend/mind-cluster/issues)
  - MindCluster Atlas Community 文档：原文在 Quick Reference 给出链接（中文路径 `clustersched/dlug/docs/zh/scheduling/01_introduction/00_overview.md`）。
