# K8s RDMA Shared Device Plugin

> 仓 `mind-cluster` · 路径 `docker/k8s-rdma-shared-dev-plugin/OVERVIEW.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mind-cluster/docker/k8s-rdma-shared-dev-plugin/OVERVIEW.md

# K8s RDMA Shared Device Plugin — Overview 文档深度解读

---

## 【定位】

本文档系统描述了 K8s RDMA Shared Device Plugin（Kubernetes RDMA 共享设备插件）的能力、镜像标签、部署方式与配置参数，旨在为运行分布式训练或高性能计算工作负载的用户提供一套可在 Kubernetes 上**多容器共享 RDMA 设备**的高性能网络方案说明。

---

## 【技术要点】

1. **核心能力**：作为 Kubernetes 设备插件（device plugin）管理节点上的 RDMA 设备，并允许多个容器共享使用同一 RDMA 设备，以支撑分布式训练/HPC 场景的高性能网络需求。
2. **设备筛选维度**：支持基于 **vendor、device ID、driver、interface name** 以及 bus type / link type 的多维度设备选择，并可通过 `selectors.buses`（如 `"ub"`）启用 UB 设备。
3. **CDI 支持**：原生支持 **Container Device Interface (CDI)**，可与 Kubernetes 设备插件框架中的 CDI 机制对接。
4. **故障检测**：支持 **UB device fault detection**，并将故障检测信息以 **ConfigMap** 形式写入 Kubernetes；检测周期由 `faultDetectPeriod` 控制（默认 5 秒，最小 1 秒）。
5. **镜像标签**：遵循 `<version>-<os>` 格式；当前文档给出 `v26.1.0-ubuntu22.04` 与 `v26.1.0-openeuler24.03` 两种标签。
6. **资源命名约定**：资源名默认 `rdma`，资源前缀默认 `huawei.com`；单个节点可管理的 RDMA HCA 设备上限 `rdmaHcaMax` 为 **1000**。

---

## 【关键机制与数据】

依据原文，可梳理的工作原理与数据流如下（每一项标注"原文:"以区分原文与解读）：

- **原文: 注册流程** —— "Detects RDMA devices on compute nodes → Registers with Kubernetes kubelet device plugin framework → Reports device availability to Kubernetes scheduler"。
  - 即：插件先在计算节点上探测 RDMA 设备，再向 kubelet device plugin 框架注册（ListAndWatch / Allocate 流程），最后将可用设备上报给 Kubernetes 调度器用于 Pod 调度决策。

- **原文: 共享机制** —— "Supports device sharing among multiple containers"。配合 `selectors` 与 `devices` 列表对设备进行筛选后暴露给多 Pod 共用，而非一容器独占。

- **原文: 故障检测输出** —— "Write fault detection information to Kubernetes as a ConfigMap"；周期参数 `faultDetectPeriod` 默认 5 秒（最小可配 1 秒）。

- **原文: 硬件门槛** —— CPU **0.1 cores**，内存 **0.1 GB**；支持的 DPU 网卡类型为 **PCI 与 UB 类**。

- **原文: 软件兼容性** —— Kubernetes **1.17.x ~ 1.34.x**（推荐 **1.19.x** 及以上）；RDMA 驱动 **OFED 5.6 或更高版本**。

- **原文: 镜像仓库** —— `swr.cn-south-1.myhuaweicloud.com/ascendhub/k8s-rdma-shared-dev-plugin:{tag}`（由用户拉取后 retag）。

- **原文: 构建注意点** —— 当 Docker 版本 < 18.09 或 BuildKit 未启用时，`TARGETPLATFORM`（用于识别 `linux/amd64`、`linux/arm64` 等目标平台）无法被读取，将导致构建失败；可通过 `export DOCKER_BUILDKIT=1` 临时启用。

---

## 【表格解读】

### 表格 1：镜像标签格式说明

> 原文逐字还原：

| Field     | Example       | Description                                                         |
|-----------|---------------|---------------------------------------------------------------------|
| `version` | `v26.1.0`     | Version Number of K8s RDMA Shared Device Plugin Component           |
| `os`      | `ubuntu22.04` | Operating System for K8s RDMA Shared Device Plugin Component Images |

**逐行解读**：

- **`<version>`**：组件版本号字段，例如 `v26.1.0`，对应 K8s RDMA Shared Device Plugin 的版本。
- **`<os>`**：基础镜像操作系统字段，例如 `ubuntu22.04`，决定最终镜像所基于的 OS 发行版与版本。

### 表格 2：v26.1.0 镜像标签与 Dockerfile 链接

> 原文逐字还原：

| Tag                      | Dockerfile                                                                                                                                 | Image Content                                                       |
|--------------------------|--------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------|
| `v26.1.0-ubuntu22.04`    | [Dockerfile.ubuntu](https://gitcode.com/Ascend/mind-cluster/blob/master/docker/k8s-rdma-shared-dev-plugin/v26.1.0/Dockerfile.ubuntu)       | K8s RDMA Shared Device Plugin v26.1.0 (Base Image: Ubuntu 22.04)    |
| `v26.1.0-openeuler24.03` | [Dockerfile.openeuler](https://gitcode.com/Ascend/mind-cluster/blob/master/docker/k8s-rdma-shared-dev-plugin/v26.1.0/Dockerfile.openeuler) | K8s RDMA Shared Device Plugin v26.1.0 (Base Image: openEuler 24.03) |

**逐行解读**：

- **`v26.1.0-ubuntu22.04`**：以 Ubuntu 22.04 为基础镜像的 v26.1.0 版本；Dockerfile 来源链接 `Dockerfile.ubuntu` 指向 master 分支对应路径。
- **`v26.1.0-openeuler24.03`**：以 openEuler 24.03 为基础镜像的 v26.1.0 版本；Dockerfile 来源链接 `Dockerfile.openeuler`。
- 两行的**Image Content** 都明确指出是 **K8s RDMA Shared Device Plugin v26.1.0**，仅基础操作系统不同，便于在不同 OS 集群环境部署。

### 表格 3：软件依赖（Prerequisites）

> 原文逐字还原：

| Software     | Supported Versions                          | Installation Location | Description                                                 |
|--------------|---------------------------------------------|-----------------------|-------------------------------------------------------------|
| Kubernetes   | 1.17.x~1.34.x (1.19.x or later recommended) | All nodes             | See [Kubernetes Documentation](https://kubernetes.io/docs/) |
| RDMA Drivers | OFED 5.6 or later                           | Compute nodes         | RDMA device drivers                                         |

**逐行解读**：

- **Kubernetes**：版本支持范围 **1.17.x ~ 1.34.x**，推荐使用 **1.19.x 及以上**；安装于所有节点。
- **RDMA Drivers**：依赖 **OFED 5.6 或更高版本**；仅需在计算节点（Compute nodes）安装——与 device plugin 的运行位置一致。

### 表格 4：硬件需求（Hardware Requirements）

> 原文逐字还原：

| Resource | Requirement |
|----------|-------------|
| CPU      | 0.1 cores   |
| Memory   | 0.1 GB      |

**逐行解读**：

- **CPU**：插件对 CPU 资源占用极低，仅需 **0.1 cores**，作为 DaemonSet 部署对节点的压力几乎可忽略。
- **Memory**：内存开销约 **0.1 GB**，因此对宿主节点的资源预留非常小。

### 表格 5：配置参数表（Configuration）

> 原文逐字还原：

| Parameter                | Type   | Description                                                   | Default                        |
|--------------------------|--------|---------------------------------------------------------------|--------------------------------|
| `periodicUpdateInterval` | int    | Interval (seconds) for periodic device updates                | 0 (disabled)                   |
| `faultDetectPeriod`      | int    | Periodic fault detection interval (seconds)                   | 5 (minimum configuration is 1) |
| `configList`             | array  | List of device configurations                                 | []                             |
| `resourceName`           | string | Resource name for the device plugin                           | rdma                           |
| `resourcePrefix`         | string | Resource prefix                                               | huawei.com                     |
| `rdmaHcaMax`             | int    | Maximum number of RDMA HCA devices                            | 1000                           |
| `devices`                | array  | List of device names to include                               | []                             |
| `selectors.buses`        | array  | Bus types to filter devices (e.g., "ub" to enable UB devices) | []                             |
| `selectors.vendors`      | array  | Vendor IDs to filter devices                                  | []                             |
| `selectors.deviceIDs`    | array  | Device IDs to filter devices                                  | []                             |
| `selectors.drivers`      | array  | Driver names to filter devices                                | []                             |
| `selectors.ifNames`      | array  | Interface names to filter devices                             | []                             |
| `selectors.linkTypes`    | array  | Link types to filter devices                                  | []                             |

**逐行解读**：

- **`periodicUpdateInterval`**：设备周期性刷新间隔（秒）。默认 `0` 即**禁用**周期性刷新；启用后可让 device plugin 周期性重新扫描节点上的 RDMA 设备。
- **`faultDetectPeriod`**：故障检测周期（秒）。默认 `5`，**最小可配 1**。控制向 ConfigMap 写入设备故障状态的频率。
- **`configList`**：设备配置数组，默认空，承载一组可选的设备级配置项。
- **`resourceName`**：Kubernetes 中暴露的资源名，默认 **`rdma`**，Pod 中可通过 `huawei.com/rdma` 申请资源。
- **`resourcePrefix`**：资源前缀，默认 **`huawei.com`**，用于在 K8s ExtendedResource 中拼接完整资源名。
- **`rdmaHcaMax`**：单节点上最多可注册/管理的 RDMA HCA 设备数，默认 **1000**，影响规模上限。
- **`devices`**：显式纳入管理的设备名清单，默认空（空即按后续 selector 过滤）。
- **`selectors.buses`**：按总线类型过滤，例如填入 `"ub"` 以启用 UB 设备。
- **`selectors.vendors`**：按 Vendor ID 过滤。
- **`selectors.deviceIDs`**：按 Device ID 过滤。
- **`selectors.drivers`**：按驱动名过滤。
- **`selectors.ifNames`**：按网络接口名过滤。
- **`selectors.linkTypes`**：按链路类型过滤。

---

## 【公式解读】

**原文无公式**。

文档中仅出现命令示例（`docker build`、`docker pull`、`kubectl apply`、`kubectl get pods`、`export DOCKER_BUILDKIT=1` 等），不包含任何 LaTeX 数学公式或伪代码算法表达式。

---

## 【关联】

依据原文与文末内部链接信息，可梳理的上下游/模块关系如下：

- **所属代码仓**：组件归属于 [MindCluster Code Repository](https://gitcode.com/Ascend/mind-cluster)，属于 MindCluster 在容器化与集群调度方向上的子模块之一。
- **上下游流程依赖**（原文 Upstream and Downstream Dependencies 段已给出四步）：
  1. **Detects RDMA devices on compute nodes** — 上游：节点本地 RDMA 设备探测。
  2. **Registers with Kubernetes kubelet device plugin framework** — 与 kubelet device plugin 框架（ListAndWatch / Allocate）对接。
  3. **Reports device availability to Kubernetes scheduler** — 向下游 Kubernetes scheduler 上报可用资源，供调度器在 Pod 调度时使用。
  4. **Support UB device fault detection** — 故障检测结果以 **ConfigMap** 形式写入 Kubernetes，可被外部组件消费。
- **CDI（Container Device Interface）**：特性列表中明确支持 CDI，与 Kubernetes 设备插件框架的 CDI 规范联动，便于在容器运行时把设备映射到容器内。
- **镜像生态关联**：
  - `Dockerfile.ubuntu` → 链接指向 `master/docker/k8s-rdma-shared-dev-plugin/v26.1.0/Dockerfile.ubuntu`。
  - `Dockerfile.openeuler` → 链接指向 `master/docker/k8s-rdma-shared-dev-plugin/v26.1.0/Dockerfile.openeuler`。
  - 这两个 Dockerfile 是构建 v26.1.0 镜像的源头；构建时依赖 **BuildKit** 注入的 `TARGETPLATFORM` 变量来区分 `linux/amd64` / `linux/arm64`。
- **社区与支持链路**：
  - 帮助/Issue 入口：[MindCluster Code Repository](https://gitcode.com/Ascend/mind-cluster) → [Issue Tracker](https://gitcode.com/Ascend/mind-cluster/issues)。
  - 文档与社区：[MindCluster Atlas Community](https://www.hiascend.com/document/detail/zh/mindcluster/latest/clustersched/dlug/docs/zh/scheduling/01_introduction/00_overview.md)（中文文档与集群调度总览）。
- **多语言版本**：本文档提供中文版本链接 `./OVERVIEW.zh.md`（来自"English | [中文]"导航）。
- **上层使用场景关联**：与分布式训练、HPC 工作负载配合使用，使这些工作负载在 Kubernetes 上获得 RDMA 级别的高性能网络。

---

## 【使用方法】

> 以下命令均直接来自原文 Quick Start / Configuration 部分。

**1. 本地构建（可选，aarch64 + Ubuntu 22.04 示例）**

```bash
docker build --no-cache -t k8s-rdma-shared-dev-plugin:v26.1.0 ./ -f Dockerfile.ubuntu
```

前置操作（Docker < 18.09 或未启用 BuildKit 时必须执行）：

```bash
export DOCKER_BUILDKIT=1
```

**2. 拉取镜像**

```bash
docker pull swr.cn-south-1.myhuaweicloud.com/ascendhub/k8s-rdma-shared-dev-plugin:{tag}
```

**3. 重命名（retag）**

```bash
docker tag swr.cn-south-1.myhuaweicloud.com/ascendhub/k8s-rdma-shared-dev-plugin:{tag} k8s-rdma-shared-dev-plugin:{version}
```

**4. 创建配置**

原文：创建一份 **ConfigMap** 装载 device plugin 的配置（即上文 Configuration 表格中的 `periodicUpdateInterval`、`faultDetectPeriod`、`configList`、`resourceName`、`resourcePrefix`、`rdmaHcaMax`、`devices`、`selectors.*` 等参数）。

**5. 以 DaemonSet 部署**

```bash
kubectl apply -f k8s-rdma-shared-dev-plugin-{version}.yaml
```

**6. 验证部署**

```bash
kubectl get pods -A | grep k8s-rdma-shared-dev-plugin
```

**典型可调配置项（节选自 Configuration 表）**：

| 场景 | 推荐参数 | 原文默认值 |
|------|----------|------------|
| 启用周期性设备刷新 | `periodicUpdateInterval` > 0（单位秒） | `0 (disabled)` |
| 调整故障检测频率 | `faultDetectPeriod` ≥ 1（秒） | `5` |
| 启用 UB 设备 | `selectors.buses` 加入 `"ub"` | `[]` |
| 限制 RDMA HCA 规模 | `rdmaHcaMax` | `1000` |
| 自定义资源名/前缀 | `resourceName` / `resourcePrefix` | `rdma` / `huawei.com` |

> 备注：原文未给出具体 `k8s-rdma-shared-dev-plugin-{version}.yaml` 内容、ConfigMap YAML 示例，也未给出如何在 Pod 中通过 `huawei.com/rdma` 申请资源的 manifest 示例——这些"原文未涉及"的部分需参考对应版本的 `Dockerfile.ubuntu` / `Dockerfile.openeuler` 同目录文件或 MindCluster Atlas 社区文档。
