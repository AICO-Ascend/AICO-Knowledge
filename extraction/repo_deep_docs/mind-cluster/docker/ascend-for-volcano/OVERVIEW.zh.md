# 集群调度组件 Ascend for Volcano

> 仓 `mind-cluster` · 路径 `docker/ascend-for-volcano/OVERVIEW.zh.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mind-cluster/docker/ascend-for-volcano/OVERVIEW.zh.md

# 一体化深度解读：Ascend for Volcano 集群调度组件 Overview

---

## 【定位】

本文档描述了 **Ascend for Volcano**——一个基于开源 Volcano 调度框架、面向昇腾 AI 处理器（NPU）的插件式调度组件，其核心能力是感知 NPU 互联拓扑（HCCS / PCIe / 同一卡内）并实现亲和性调度、最优资源分配与故障重调度，从而在 K8s 集群中最大化昇腾 AI 处理器的计算性能与网络利用率。

---

## 【技术要点】

1. **插件机制定位**：Ascend for Volcano 基于 Volcano 调度框架的插件机制实现，部署在**管理节点**上，包含两个镜像——`volcano-scheduler`（含昇腾 NPU 调度插件 `volcano-npu_*.so`）与 `volcano-controller`。
2. **可用设备计算开关**：通过参数 `self-maintain-available-card` 控制，默认开启时由本组件自行计算可用设备信息；关闭时改为从集群调度底层组件获取可用设备信息。
3. **三级拓扑亲和性优先级**：NPU 亲和性调度按"同一卡内 > HCCS 互联 > PCIe 互联"的顺序降级选择，目标是减少资源碎片与网络拥塞。
4. **三级亲和性策略（昇腾 910，按优先级排列）**：
   - HCCS 亲和性调度原则：申请的处理器必须在同一 HCCS 环内，优先选剩余可用处理器数量最匹配的 HCCS；
   - 优先占满调度原则：优先分配已经分配过昇腾 910 的 AI 服务器，减少碎片；
   - 剩余偶数优先原则：满足上述后，优先选剩余处理器数量为偶数的 HCCS。
5. **多种组网与调度模式**：支持 Spine-Leaf 双层互联、单层交换机互联；调度模式支持整卡调度、静态 vNPU 调度、动态 vNPU 调度、软切分调度。
6. **多级调度资源抽象**：通过参数 `resource-level-config` 将集群资源按 NPU 网络拓扑层级抽象为多层级结构，并支持对物理超节点按切分策略划分出**逻辑超节点**。

---

## 【关键机制与数据】

**工作原理 / 数据流（原文信息汇总）：**

- **资源信息来源（上游）**：默认场景下，组件根据 `ClusterD` 上报的信息计算集群资源信息。
- **任务拉起配置（输入）**：组件接收第三方下发的任务拉起配置，从 K8s 的任务对象中获取用户期望的资源数量。
- **资源选择逻辑**：结合集群的设备数量、设备类型与设备组网方式，选择最优资源分配给任务。
- **资源下发（下游）**：向计算节点的 **Ascend Device Plugin** 传递具体的资源选中信息，完成设备挂载。
- **故障重调度机制**：当任务资源故障时，组件触发重新调度任务。
- **可选可用设备计算模式**：`self-maintain-available-card` 默认开启——根据集群调度底层组件上报的故障信息及节点信息计算可用设备；关闭时从底层组件直接获取。

**性能/版本数据（原文有的才写）：**

- 原文 Tag 规范起始版本：**昇腾 NPU 调度插件 v26.1.0**（自此版本起 Tag 格式升级为含操作系统字段）。
- 昇腾 NPU 调度插件 **v26.0.0 及以前版本**使用旧式 Tag 格式（仅含组件版本与插件版本两段）。
- 文档涉及的 Volcano 组件版本：`v1.7.0`、`v1.9.0`、`v1.12.0`。
- 昇腾 NPU 调度插件版本：`v26.0.0`、`v26.1.0`。
- 支持的基础镜像操作系统：`alpinelatest`、`openeuler24.03`。
- 旧版安装包命名示例：`Ascend-mindxdl-volcano_26.0.0_linux-aarch64.zip`（架构为 linux-aarch64）。

---

## 【表格解读】

### 表 1：Tag 规范字段表（v26.1.0 起新格式）

| 字段 | 示例值 | 说明 |
|---|---|---|
| `组件版本` | `v1.7.0` | Volcano 组件版本 |
| `昇腾调度插件版本` | `v26.1.0` | 昇腾NPU调度插件版本 |
| `操作系统` | `alpinelatest` | Volcano镜像操作系统 |

**解读**：自 v26.1.0 起，Tag 由两段扩为三段，新增了**操作系统维度**，意味着同一组件版本、同一插件版本可针对不同 OS 基础镜像分别发布。该字段是镜像拉取与运维识别的关键。

---

### 表 2：Tag 规范字段表（v26.0.0 及以前旧格式）

| 字段 | 示例值 | 说明 |
|---|---|---|
| `组件版本` | `v1.7.0` | Volcano 组件版本 |
| `昇腾调度插件版本` | `v26.0.0` | 昇腾NPU调度插件版本 |

**解读**：旧版 Tag 仅包含组件版本与插件版本，未暴露基础镜像类型，OS 信息隐含在构建产物（典型为 Alpine）。

---

### 表 3：Ascend for Volcano 26.1.0（Volcano v1.12.0）镜像清单

| Tag | Dockerfile | 镜像内容 |
|---|---|---|
| `v1.12.0-v26.1.0-alpinelatest` | [Dockerfile-scheduler.alpine](https://gitcode.com/Ascend/mind-cluster/blob/master/docker/ascend-for-volcano/volcano-v1.12.0/v26.1.0/Dockerfile-scheduler.alpine) | Volcano调度器v26.1.0版本镜像（含昇腾NPU调度插件，基于Volcano v1.12.0，基础镜像 Alpine latest） |
| `v1.12.0-v26.1.0-alpinelatest` | [Dockerfile-controller.alpine](https://gitcode.com/Ascend/mind-cluster/blob/master/docker/ascend-for-volcano/volcano-v1.12.0/v26.1.0/Dockerfile-controller.alpine) | Volcano控制器v26.1.0版本镜像（基于Volcano v1.12.0，基础镜像 Alpine latest） |
| `v1.12.0-v26.1.0-openeuler24.03` | [Dockerfile-scheduler.openeuler](https://gitcode.com/Ascend/mind-cluster/blob/master/docker/ascend-for-volcano/volcano-v1.12.0/v26.1.0/Dockerfile-scheduler.openeuler) | Volcano调度器v26.1.0版本镜像（含昇腾NPU调度插件，基于Volcano v1.12.0，基础镜像 openEuler 24.03） |
| `v1.12.0-v26.1.0-openeuler24.03` | [Dockerfile-controller.openeuler](https://gitcode.com/Ascend/mind-cluster/blob/master/docker/ascend-for-volcano/volcano-v1.12.0/v26.1.0/Dockerfile-controller.openeuler) | Volcano控制器v26.1.0版本镜像（基于Volcano v1.12.0，基础镜像 openEuler 24.03） |

**解读**：每个 Volcano 主版本号下，针对 scheduler / controller 两种角色分别构建 Alpine 与 openEuler 24.03 两个 OS 变体，Tag 完全相同靠 OS 字段区分（原文表格中 Tag 文字重复，按原文照录）。

---

### 表 4：Ascend for Volcano 26.1.0（Volcano v1.9.0）镜像清单

| Tag | Dockerfile | 镜像内容 |
|---|---|---|
| `v1.9.0-v26.1.0-alpinelatest` | [Dockerfile-scheduler.alpine](https://gitcode.com/Ascend/mind-cluster/blob/master/docker/ascend-for-volcano/volcano-v1.9.0/v26.1.0/Dockerfile-scheduler.alpine) | Volcano调度器v26.1.0版本镜像（含昇腾NPU调度插件，基于Volcano v1.9.0，基础镜像 Alpine latest） |
| `v1.9.0-v26.1.0-alpinelatest` | [Dockerfile-controller.alpine](https://gitcode.com/Ascend/mind-cluster/blob/master/docker/ascend-for-volcano/volcano-v1.9.0/v26.1.0/Dockerfile-controller.alpine) | Volcano控制器v26.1.0版本镜像（基于Volcano v1.9.0，基础镜像 Alpine latest） |
| `v1.9.0-v26.1.0-openeuler24.03` | [Dockerfile-scheduler.openeuler](https://gitcode.com/Ascend/mind-cluster/blob/master/docker/ascend-for-volcano/volcano-v1.9.0/v26.1.0/Dockerfile-scheduler.openeuler) | Volcano调度器v26.1.0版本镜像（含昇腾NPU调度插件，基于Volcano v1.9.0，基础镜像 openEuler 24.03） |
| `v1.9.0-v26.1.0-openeuler24.03` | [Dockerfile-controller.openeuler](https://gitcode.com/Ascend/mind-cluster/blob/master/docker/ascend-for-volcano/volcano-v1.9.0/v26.1.0/Dockerfile-controller.openeuler) | Volcano控制器v26.1.0版本镜像（基于Volcano v1.9.0，基础镜像 openEuler 24.03） |

**解读**：v1.9.0 上游基线，NPU 插件 v26.1.0 是同一插件对更早 Volcano 主版本的回填构建。

---

### 表 5：Ascend for Volcano 26.1.0（Volcano v1.7.0）镜像清单

| Tag | Dockerfile | 镜像内容 |
|---|---|---|
| `v1.7.0-v26.1.0-alpinelatest` | [Dockerfile-scheduler.alpine](https://gitcode.com/Ascend/mind-cluster/blob/master/docker/ascend-for-volcano/volcano-v1.7.0/v26.1.0/Dockerfile-scheduler.alpine) | Volcano调度器v26.1.0版本镜像（含昇腾NPU调度插件，基于Volcano v1.7.0，基础镜像 Alpine latest） |
| `v1.7.0-v26.1.0-alpinelatest` | [Dockerfile-controller.alpine](https://gitcode.com/Ascend/mind-cluster/blob/master/docker/ascend-for-volcano/volcano-v1.7.0/v26.1.0/Dockerfile-controller.alpine) | Volcano控制器v26.1.0版本镜像（基于Volcano v1.7.0，基础镜像 Alpine latest） |
| `v1.7.0-v26.1.0-openeuler24.03` | [Dockerfile-scheduler.openeuler](https://gitcode.com/Ascend/mind-cluster/blob/master/docker/ascend-for-volcano/volcano-v1.7.0/v26.1.0/Dockerfile-scheduler.openeuler) | Volcano调度器v26.1.0版本镜像（含昇腾NPU调度插件，基于Volcano v1.7.0，基础镜像 openEuler 24.03） |
| `v1.7.0-v26.1.0-openeuler24.03` | [Dockerfile-controller.openeuler](https://gitcode.com/Ascend/mind-cluster/blob/master/docker/ascend-for-volcano/volcano-v1.7.0/v26.1.0/Dockerfile-controller.openeuler) | Volcano控制器v26.1.0版本镜像（基于Volcano v1.7.0，基础镜像 openEuler 24.03） |

**解读**：v1.7.0 是支持的最低 Volcano 基线，与 v1.9.0 / v1.12.0 共同覆盖三类主流 K8s + Volcano 上游版本组合。

---

### 表 6：Ascend for Volcano 26.0.0（Volcano v1.9.0）镜像清单（旧格式）

| Tag | Dockerfile(安装包内文件路径) | 镜像内容 |
|---|---|---|
| `v1.9.0-v26.0.0` | volcano-v1.9.0/Dockerfile-scheduler | Volcano调度器v26.0.0版本镜像（含昇腾NPU调度插件，基于Volcano v1.9.0，基础镜像 Alpine latest） |
| `v1.9.0-v26.0.0` | volcano-v1.9.0/Dockerfile-controller | Volcano控制器v26.0.0版本镜像（基于Volcano v1.9.0，基础镜像 Alpine latest） |

**解读**：旧版本不再以容器镜像 Tag 直接发布到公开仓库，而是以 `Ascend-mindxdl-volcano_26.0.0_linux-aarch64.zip` 安装包形式提供，Dockerfile 路径位于安装包内部；Tag 仅有组件版本与插件版本两段，无 OS 字段。

---

### 表 7：Ascend for Volcano 26.0.0（Volcano v1.7.0）镜像清单（旧格式）

> 原文在表格末被截断（`|---------------------------------|` 之后没有内容）。原文实际未给出本表中的具体 Tag/Dockerfile/镜像内容行，因此**严格按原文如实说明**：原文此表内容不完整，仅保留标题"### Ascend for Volcano 26.0.0（Volcano v1.7.0）"、前置说明"以 linux-aarch64 架构为例：…[Ascend-mindxdl-volcano_26.0.0_linux-aarch64.zip](https://gitcode.com/Ascend/mind-cluster/releases/download/v26.0.0/Ascend-mindxdl-volcano_26.0.0_linux-aarch64.zip)"及表头 "Tag | Dockerfile(安装包内文件路径) | 镜像内容"，表格正文行缺失。

---

## 【公式解读】

原文无数学公式。

文档中以代码块形式给出的仅为 **Tag 命名模板**，本质是字符串模板而非计算公式：

```text
<组件版本>-<昇腾调度插件版本>-<操作系统>
```

```shell
<组件版本>-<昇腾调度插件版本>
```

各占位符含义：
- `<组件版本>`：上游 Volcano 组件的版本号（如 `v1.7.0`、`v1.9.0`、`v1.12.0`）。
- `<昇腾调度插件版本>`：昇腾 NPU 调度插件版本号（如 `v26.0.0`、`v26.1.0`）。
- `<操作系统>`：v26.1.0 起新增的基础镜像 OS 标识（取值 `alpinelatest` 或 `openeuler24.03`）。

---

## 【关联】

**与上下游模块 / 其他特性的关系（综合原文"组件上下游依赖""快速参考"与镜像说明）：**

1. **上游：ClusterD（集群调度底层组件）**
   - Ascend for Volcano 默认基于 ClusterD 上报的故障信息及节点信息计算集群资源信息。
   - 当 `self-maintain-available-card` 关闭时，从 ClusterD 直接获取可用设备信息。
   - ClusterD 是资源状态的"事实源"，Ascend for Volcano 处于其消费侧。

2. **下游：Ascend Device Plugin（部署在计算节点）**
   - 组件将选中的具体资源（设备 ID / 网络位置等选中信息）传递给计算节点上的 Ascend Device Plugin，由后者完成设备挂载到容器。
   - 形成"管理节点决策 → 计算节点挂载"的端到端链路。

3. **横向：第三方任务下发方**
   - 组件接收第三方下发的"任务拉起配置"，结合 K8s 任务对象解析用户期望资源量，再做最优节点选择。
   - 即该组件是 K8s 调度链路上对 Volcano 的昇腾增强点，对上层任务系统是透明的。

4. **横向：Volcano 上游框架**
   - 组件以 Volcano 插件机制工作：`volcano-scheduler` 镜像内置 `volcano-npu_*.so` 插件；`volcano-controller` 提供控制器侧能力。
   - 与上游 Volcano 版本有强绑定关系（文档列出 v1.7.0 / v1.9.0 / v1.12.0 三套主版本）。

5. **同级：MindCluster 代码仓其他组件**
   - 文档明确由 [MindCluster 代码仓](https://gitcode.com/Ascend/mind-cluster) 维护，并指向 [MindCluster 昇腾社区文档](https://www.hiascend.com/document/detail/zh/mindcluster/latest/clustersched/dlug/docs/zh/scheduling/01_introduction/00_overview.md) 与 [问题反馈](https://gitcode.com/Ascend/mind-cluster/issues)。
   - 本文档与同目录的英文版 `./OVERVIEW.md` 互为翻译镜像（页面顶部语言切换链接）。

6. **依赖资源（运行时支撑）**
   - 资源拓扑感知依赖昇腾 NPU 互联结构（HCCS 环内 / HCCS 互联 / PCIe 互联三层），以及交换机参数面网络配置（Spine-Leaf 双层、单层）。
   - 物理超节点之上的"逻辑超节点"切分策略也由该组件实现。

---

## 【使用方法】

**镜像启用方式（基于原文 Tag / Dockerfile 信息推导，原文未给出 yaml/命令行示例）：**

- **v26.1.0 起新格式镜像**（按 OS 拉取）：
  - Alpine：`v<组件版本>-v26.1.0-alpinelatest`
  - openEuler 24.03：`v<组件版本>-v26.1.0-openeuler24.03`
  - 支持的组件版本组合：`v1.12.0`、`v1.9.0`、`v1.7.0`。
  - 需分别拉取两个角色镜像：`volcano-scheduler` 与 `volcano-controller`。
  - 部署位置：管理节点（原文"部署在管理节点上"）。

- **v26.0.0 及以前旧格式镜像**：
  - Tag 格式：`v<组件版本>-v26.0.0`（如 `v1.9.0-v26.0.0`、`v1.7.0-v26.0.0`）。
  - 以安装包形式分发：`Ascend-mindxdl-volcano_26.0.0_linux-aarch64.zip`（[下载链接](https://gitcode.com/Ascend/mind-cluster/releases/download/v26.0.0/Ascend-mindxdl-volcano_26.0.0_linux-aarch64.zip)），Dockerfile 位于安装包内 `volcano-v<版本>/Dockerfile-scheduler` / `volcano-v<版本>/Dockerfile-controller`。
  - 基础镜像：Alpine latest。

**关键配置项（原文明确提及的参数名）：**

| 参数 | 默认值 | 作用 |
|---|---|---|
| `self-maintain-available-card` | 默认开启 | 控制可用设备信息的来源——开启则本组件自行计算；关闭则从集群调度底层组件获取 |
| `resource-level-config` | 原文未给默认值 | 配置多级调度策略的层级结构（基于 NPU 网络拓扑层级关系将集群资源抽象为多层级） |

**调度模式选择（功能开关，启用方式原文未涉及具体配置语法）：**
- 整卡调度 / 静态 vNPU 调度 / 动态 vNPU 调度 / 软切分调度 四种模式由用户任务侧启用，原文未列出对应的 K8s / Volcano 字段名。

**调度策略选择（昇腾 910，按优先级自动应用，启用方式原文未涉及具体配置语法）：**
- HCCS 亲和性调度原则 → 优先占满调度原则 → 剩余偶数优先原则 三级策略按优先级自动叠加。

**运维与帮助入口：**
- 代码仓：[https://gitcode.com/Ascend/mind-cluster](https://gitcode.com/Ascend/mind-cluster)
- 社区文档：[MindCluster 昇腾社区调度概述](https://www.hiascend.com/document/detail/zh/mindcluster/latest/clustersched/dlug/docs/zh/scheduling/01_introduction/00_overview.md)
- 问题反馈：[https://gitcode.com/Ascend/mind-cluster/issues](https://gitcode.com/Ascend/mind-cluster/issues)
