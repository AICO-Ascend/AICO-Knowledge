# Cluster Scheduling Component Atlas Device Plugin

> 仓 `mind-cluster` · 路径 `docker/ascend-device-plugin/OVERVIEW.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mind-cluster/docker/ascend-device-plugin/OVERVIEW.md

# Atlas Device Plugin OVERVIEW 文档深度解读

---

## 【定位】

这篇文档是 MindCluster 集群调度套件核心组件 **Atlas Device Plugin** 的总览介绍, 旨在说明该组件如何作为 Kubernetes Device Plugin 在计算节点上为 Atlas NPU 设备提供资源发现、健康上报、设备挂载与故障处理能力, 并给出镜像标签约定、版本兼容表与本地构建/在线拉取的入门指引。

---

## 【技术要点】

1. **组件定位与部署位置**: Atlas Device Plugin 是 MindCluster 集群调度套件的核心组件之一, **部署在 Kubernetes 集群的计算节点 (compute node) 上**, 专门为 Atlas 设备提供资源发现 (Device Discovery) 与上报 (Reporting) 策略。

2. **Device Plugin 自定义资源机制**: Kubernetes 的 Device Plugin 机制允许用户**在 CPU/内存之外定义自定义资源类型**并自定义发现与上报策略; 本组件即为 Atlas 设备适配此机制的具体实现。

3. **虚拟设备 (vNPU) 支持**: 支持从物理设备切分出**虚拟设备**并将其上报到 Kubernetes 系统; 虚拟设备的健康状态由其来源的物理设备决定。

4. **故障分级与升级机制**: 支持**配置故障处理等级 (fault handling levels)**, 且当故障**反复出现或长时间持续时能升级处理等级**; 对空闲且重启后可恢复的故障芯片执行 **chip 热复位 (hot reset)**。

5. **网络故障监控 (Lingqu/灵衢)**: 订阅灵衢 (Lingqu) 驱动的网络故障信息, 同时向 kubelet 与上层调度服务上报网络状态及具体故障明细。

6. **资源挂载链路**: 在资源挂载阶段, 组件**读取集群调度器选定的芯片信息**, 通过**环境变量**传递给 **Atlas Docker Runtime** 完成挂载。

7. **镜像标签与平台约束**: 自 **v26.1.0** 起标签格式改为 `<version>-<os>` (例如 `v26.1.0-ubuntu22.04`、`v26.1.0-openeuler24.03`); 基础镜像同时支持 **Ubuntu 22.04** 与 **openEuler 24.03**。v26.0.0 及更早版本仅以 `<version>` 形式标记。

---

## 【关键机制与数据】

### 工作原理 (五项核心特性)

| # | 特性 | 数据流 / 行为 (原文摘录) |
|---|------|---------------------------|
| 1 | **Device Discovery (设备发现)** | 从驱动获取芯片类型与型号信息 → 上报 kubelet 与上层 **ClusterD** 服务; 支持发现 Atlas 设备驱动报告的设备数; 支持上报物理设备切分出的虚拟设备 |
| 2 | **Health Check (健康检查)** | 订阅驱动的芯片故障信息 → 上报芯片状态到 kubelet; 同时上报芯片状态与具体故障细节到上层调度服务; 异常设备被自动从可用列表移除 |
| 3 | **Device Allocation (设备分配)** | 支持在 Kubernetes 中分配 Atlas 设备; 支持 NPU 设备重调度——设备故障时自动启动新容器、挂载健康设备、重建训练任务; 通过环境变量向 Atlas Docker Runtime 传递芯片信息 |
| 4 | **Fault Handling (故障处理)** | 可配置故障处理等级; 故障复发/持续时升级等级; 对可恢复的空闲故障芯片执行热复位 |
| 5 | **Network Fault Monitoring (网络故障监控)** | 订阅灵衢 (Lingqu) 驱动的网络故障信息 → 上报网络状态到 kubelet; 同时上报灵衢网络状态与具体故障细节到上层调度服务 |

### 性能 / 资源数据 (原文: 硬件需求)

| 资源 | 原文要求 |
|------|---------|
| CPU | **0.5 cores** |
| 内存 | **0.5 GB** |

---

## 【表格解读】

### 表 1: Tag Convention (v26.1.0 及之后)

**逐字还原:**

| Field     | Example       | Description                                     |
|-----------|---------------|-------------------------------------------------|
| `version` | `v26.1.0`     | Version Number of Atlas Device Plugin           |
| `os`      | `ubuntu22.04` | Operating System for Atlas Device Plugin Images |

**解读:** 自 v26.1.0 起, 镜像 tag 由"单一版本号"演化为"**版本号-操作系统**"复合结构, 允许同一组件版本基于不同 OS 出多份镜像, 满足 Ubuntu 与 openEuler 等多 OS 客户环境分发需求。

### 表 2: Atlas Device Plugin 26.1.0 镜像清单

**逐字还原:**

| Tag                      | Dockerfile                                                                                                                           | Image Content                                             |
|--------------------------|--------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------|
| `v26.1.0-ubuntu22.04`    | [Dockerfile.ubuntu](https://gitcode.com/Ascend/mind-cluster/blob/master/docker/ascend-device-plugin/v26.1.0/Dockerfile.ubuntu)       | Atlas Device Plugin v26.1.0 (Base Image: Ubuntu 22.04)    |
| `v26.1.0-openeuler24.03` | [Dockerfile.openeuler](https://gitcode.com/Ascend/mind-cluster/blob/master/docker/ascend-device-plugin/v26.1.0/Dockerfile.openeuler) | Atlas Device Plugin v26.1.0 (Base Image: openEuler 24.03) |

**解读:** v26.1.0 同版本提供**两份基础镜像**——一份基于 Ubuntu 22.04 (Debian 系), 一份基于 openEuler 24.03 (openEuler 系), 分别对应不同的 Dockerfile; 选择镜像时需依据目标节点的 OS 类型, 否则运行期可能出现 glibc/库依赖问题。

### 表 3: Tag Convention (v26.0.0 及之前)

**逐字还原:**

| Field     | Example   | Description                           |
|-----------|-----------|---------------------------------------|
| `version` | `v26.0.0` | Version Number of Atlas Device Plugin |

**解读:** 旧版镜像仅用 `<version>` 一个字段作为 tag, 没有 OS 维度信息, 通常默认基于 Ubuntu 22.04 构建。**该格式自 v26.1.0 起被新格式取代**, 存量用户升级时需注意 tag 命名差异。

### 表 4: Atlas Device Plugin 26.0.0 镜像清单

**逐字还原:**

| Tag       | Dockerfile                                                                                                         | Image Content                                          |
|-----------|--------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------|
| `v26.0.0` | [Dockerfile](https://gitcode.com/Ascend/mind-cluster/blob/v26.0.0/component/ascend-device-plugin/build/Dockerfile) | Atlas Device Plugin v26.0.0 (Base Image: Ubuntu 22.04) |

**解读:** v26.0.0 只有 Ubuntu 22.04 一种基础镜像, Dockerfile 位于历史路径 `component/ascend-device-plugin/build/Dockerfile` (注意路径不同于 v26.1.0 的 `docker/ascend-device-plugin/v26.1.0/`), 表明仓库目录结构在 26.1.0 时发生过迁移。

### 表 5: Software Dependencies (软件依赖)

**逐字还原:**

| Software                               | Supported Versions                          | Installation Location | Description                                                                      |
|----------------------------------------|---------------------------------------------|-----------------------|----------------------------------------------------------------------------------|
| Kubernetes                             | 1.17.x~1.34.x (1.19.x or later recommended) | All nodes             | See [Kubernetes Documentation](https://kubernetes.io/docs/)                      |
| Docker                                 | 18.09.x~28.5.1                              | All nodes             | Available from [Docker](https://docs.docker.com/engine/install/)                 |
| Containerd                             | 1.4.x~2.1.4 (1.6.x recommended)             | All nodes             | Available from [Containerd](https://containerd.io/downloads/)                    |
| Atlas AI Processor Driver and Firmware | See version compatibility table             | Compute nodes         | See "Installing NPU Driver and Firmware" in the CANN Software Installation Guide |
| UMDK software package                  | See version compatibility table             | Compute nodes         | Necessary for Atlas 850、Atlas 950 SuperPod Products                              |

**解读:**

- **Kubernetes 1.17.x~1.34.x** 为兼容范围, **推荐 1.19.x 及以上**——原因是 Device Plugin API 在早期版本功能有限, 1.19 起才有更稳定的注册/上报机制。
- **Docker 18.09.x~28.5.1** 为较宽版本窗口, 但因下文构建章节要求 BuildKit (Docker ≥ 18.09 默认启用), 升级到较新版本可规避 `TARGETPLATFORM` 变量缺失问题。
- **Containerd 1.6.x 推荐**, 是因为与 Kubernetes 1.19+ 默认 CRI 配套更稳定。
- **Atlas AI Processor Driver and Firmware** 与 **UMDK** 是**仅在计算节点**需要的硬件/平台软件, 版本需查"版本兼容表" (本文未给出, 需跳转 CANN 安装指南)。
- **UMDK 仅在 Atlas 850 / Atlas 950 SuperPod 产品**上必须, 普通推理卡无需安装, 这是产品矩阵差异的关键。

### 表 6: Hardware Requirements (硬件需求)

**逐字还原:**

| Resource | Requirement |
|----------|-------------|
| CPU      | 0.5 cores   |
| Memory   | 0.5 GB      |

**解读:** Device Plugin 自身是**轻量级 DaemonSet 代理**, 仅需 0.5 核 CPU 与 0.5 GB 内存, 几乎不挤占业务配额; 实际 NPU 资源由 Atlas 物理卡提供, 在此只是"控制平面开销"。

---

## 【公式解读】

**原文无公式**。

文档中出现的唯一形似公式的内容为镜像标签命名格式的伪代码块, 严格意义属于**字符串模板**:

```text
<version>-<os>
```

```text
<version>
```

**含义说明:**

- `<version>` —— Atlas Device Plugin 的语义化版本号 (SemVer), 例 `v26.1.0`、`v26.0.0`。
- `<os>` —— 操作系统标识, 例 `ubuntu22.04`、`openeuler24.03`, 表述"OS 名称 + 主版本号"的组合形式。

**作用:** 这两段模板定义的是**镜像 tag 的拼接规则**, 用于从源码构建或在线拉取时生成符合规范的 tag 字符串, 不是数值计算公式。

---

## 【关联】

根据文档内文与文末链接, Atlas Device Plugin 在 MindCluster 生态中的上下游关系如下:

| 关系对象 | 角色 / 交互 |
|----------|-------------|
| **Kubernetes / kubelet** | Device Plugin 上游标准 API 消费者; 接收自定义资源 (Atlas NPU) 的注册、列表、健康状态, 并据此调度 Pod |
| **ClusterD (上层调度服务)** | Device Plugin 将发现的芯片信息、健康状态、网络状态、故障细节同时上报给 ClusterD, 是 Atlas Device Plugin 与上层调度决策的关键桥梁 |
| **Atlas AI Processor Driver / Firmware** | 运行于宿主机, 为 Device Plugin 提供芯片型号、设备数、故障信息等底层数据 |
| **Lingqu (灵衢) 驱动** | 专用于 Atlas 950 SuperPod 等场景的**网络子系统**, 向 Device Plugin 推送网络故障事件 |
| **Atlas Docker Runtime** | Device Plugin 在挂载阶段通过**环境变量**将芯片信息交付给该 Runtime, 由其完成容器内 NPU 挂载 |
| **UMDK 软件包** | 仅在 Atlas 850 / Atlas 950 SuperPod 产品上必需, 是网络互联 (灵衢) 的平台依赖 |
| **CANN 安装指南** | 提供驱动/固件版本兼容表与安装步骤, 是前置条件 |
| **MindCluster Repository** | 本组件源码与镜像构建的归属仓库; Issue Tracker 也设在此处 |
| **MindCluster Atlas Community** | 官方文档站, 包含组件总览与调度指南 |
| **内部链接 `./OVERVIEW.zh.md`** | 同篇文档的中文版, 用于中文用户对照阅读 |

---

## 【使用方法】

### 一、启用前置条件 (Prerequisites)

- 在**所有节点**安装 Kubernetes (1.17.x~1.34.x, 推荐 1.19.x+)、Docker (18.09.x~28.5.1)、Containerd (1.4.x~2.1.4, 推荐 1.6.x)。
- 在**计算节点**安装 **Atlas AI Processor Driver and Firmware** (查 CANN 安装指南获取版本兼容表); 若为 **Atlas 850 / Atlas 950 SuperPod**, 还需额外安装 **UMDK 软件包**。
- Device Plugin 自身只需 **0.5 核 CPU + 0.5 GB 内存**。

### 二、在线拉取官方镜像 (推荐方式)

1. **拉取镜像** (把 `{tag}` 替换为实际版本, 例如 `v26.1.0-ubuntu22.04`):

   ```bash
   docker pull swr.cn-south-1.myhuaweicloud.com/ascendhub/ascend-k8sdeviceplugin:{tag}
   ```

2. **重打本地标签** (统一命名, 便于后续运维):

   ```bash
   docker tag swr.cn-south-1.myhuaweicloud.com/ascendhub/ascend-k8sdeviceplugin:{tag} ascend-k8sdeviceplugin:{tag}
   ```

### 三、本地构建 (可选)

针对 **v26.1.0 及以后**版本, 示例为在 aarch64 环境下基于 Ubuntu 22.04 构建 `v26.1.0`:

1. 从「Supported Tags and Dockerfile Links」章节打开对应的 `Dockerfile.ubuntu` 链接, 保存到本地 aarch64 环境的目录。
2. **禁用缓存构建** (保证清洁构建):

   ```bash
   docker build --no-cache -t ascend-k8sdeviceplugin:v26.1.0 ./ -f Dockerfile.ubuntu
   ```

### 四、关键注意事项 (原文标注 Important Notes)

- 若 Docker 版本**早于 18.09** 或 **未手动启用 BuildKit**, 构建过程中将**无法读取 `TARGETPLATFORM` 变量**, 导致镜像构建失败。
- `TARGETPLATFORM` 是 **Docker BuildKit 的内建全局变量**, 用于识别目标构建平台 (如 `linux/amd64`、`linux/arm64`), **仅在启用 BuildKit 后才会被自动注入**。
- 旧版 (legacy) Docker 或默认禁用 BuildKit 的环境下不可用。
- **(原文末尾被截断, 第 3 条命令 `Run the f...` 不完整, 原文未涉及完整内容)**

> 说明: 原文档在「Build Locally」章节末尾存在截断 (`3. Run the f...`), 后续步骤未在所提供的原文范围内, 故无法基于原文给出更多命令。
