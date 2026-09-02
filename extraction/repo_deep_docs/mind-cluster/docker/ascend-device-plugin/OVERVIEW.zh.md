# 集群调度组件 Ascend Device Plugin

> 仓 `mind-cluster` · 路径 `docker/ascend-device-plugin/OVERVIEW.zh.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mind-cluster/docker/ascend-device-plugin/OVERVIEW.zh.md

# Ascend Device Plugin OVERVIEW.zh.md 一体化深度解读

---

## 【定位】

这篇文档描述 MindCluster 集群调度组件中的 **Ascend Device Plugin** —— 一个部署在 Kubernetes 计算节点上的核心插件，用于在 Kubernetes 体系中提供**昇腾 NPU 设备的资源发现、上报、健康检查、分配与故障处理**能力，使 Kubernetes 能够感知并调度昇腾 AI 处理器（而非仅感知 CPU/内存）。

---

## 【技术要点】

1. **遵循 Kubernetes Device Plugin 机制自定义资源类型**：Kubernetes 原生只感知 CPU/内存，Ascend Device Plugin 通过 K8s 设备插件机制向 kubelet 注册新的资源类型（`huawei.com/Ascend*`），使昇腾设备可被调度。
2. **核心五大功能**：①设备发现（物理/虚拟设备个数与型号上报 kubelet + ClusterD）②健康检查（订阅芯片故障、剔除不健康设备）③设备分配（环境变量传给 Ascend Docker Runtime 挂载，支持故障后 NPU 重调度）④故障处理（可配置处理级别，长时间/反复故障升级；空闲且热复位可恢复时执行热复位）⑤灵衢网络故障监控（订阅网络故障并上报 kubelet 与上层）。
3. **Tag 规范分两阶段**：v26.1.0 起采用 `<版本>-<操作系统>` 格式（如 `v26.1.0-ubuntu22.04`）；v26.0.0 及以前为单一 `<版本>` 格式。
4. **环境约束**：硬件只需 CPU 0.5 核 / 内存 0.5GB；Kubernetes 支持 1.17.x~1.34.x（推荐 1.19.x+）、Docker 18.09.x~28.5.1、Containerd 1.4.x~2.1.4（推荐 1.6.x）。
5. **节点标签机制**：通过 `kubectl label nodes <node-name> accelerator=huawei-Ascend910` 等标签匹配设备型号以供调度。
6. **构建要求**：使用 BuildKit 注入的 `TARGETPLATFORM` 全局变量构建多架构镜像；Docker < 18.09 或未开启 BuildKit 会导致镜像构建失败，可通过 `export DOCKER_BUILDKIT=1` 临时启用。

---

## 【关键机制与数据】

**工作原理（数据流）**：
- **资源发现与上报**：Ascend Device Plugin 从昇腾驱动获取芯片类型、型号、设备个数 → 上报给 **kubelet** 与上层资源调度服务 **ClusterD**。虚拟设备由物理设备拆分得到，其个数同样上报 K8s。
- **健康检查**：插件从驱动订阅芯片故障信息 → 上报芯片状态给 kubelet，并将状态与具体故障信息上报 ClusterD；K8s 自动从可用列表中剔除不健康设备；**虚拟设备的健康状态由其来源的物理设备决定**。
- **设备分配**：集群调度选中芯片 → 插件通过**环境变量**将芯片信息传给 Ascend Docker Runtime 完成挂载；支持 NPU 重调度，故障后拉起新容器并挂载健康设备、重建训练任务。
- **故障处理分级**：可配置故障处理级别；当故障反复发生或长时间持续时会**自动升级**故障处理级别；空闲状态下热复位可恢复时执行热复位。
- **灵衢网络监控**：从灵衢驱动订阅网络故障 → 上报网络状态给 kubelet，并上报状态与故障详情给上层服务。

**性能/容量数据（原文）**：
- 硬件最小规格：CPU 0.5 核、内存 0.5GB。
- 软件版本范围：Kubernetes 1.17.x~1.34.x、Docker 18.09.x~28.5.1、Containerd 1.4.x~2.1.4。

---

## 【表格解读】

### 表 1：Tag 字段说明（v26.1.0 起）

| 字段     | 示例值           | 说明                         |
|--------|---------------|----------------------------|
| `版本`   | `v26.1.0`     | Ascend Device Plugin 版本号   |
| `操作系统` | `ubuntu22.04` | Ascend Device Plugin镜像操作系统 |

**解读**：自 v26.1.0 起镜像标签从单一版本号升级为"版本-操作系统"二元组，方便在多 OS 环境（Ubuntu、openEuler）共存场景下精确选用镜像。

### 表 2：Ascend Device Plugin 26.1.0 镜像清单

| Tag                      | Dockerfile                                                                                                                           | 镜像内容                                               |
|--------------------------|--------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------|
| `v26.1.0-ubuntu22.04`    | [Dockerfile.ubuntu](https://gitcode.com/Ascend/mind-cluster/blob/master/docker/ascend-device-plugin/v26.1.0/Dockerfile.ubuntu)       | Ascend Device Plugin v26.1.0 (基础镜像Ubuntu 22.04)    |
| `v26.1.0-openeuler24.03` | [Dockerfile.openeuler](https://gitcode.com/Ascend/mind-cluster/blob/master/docker/ascend-device-plugin/v26.1.0/Dockerfile.openeuler) | Ascend Device Plugin v26.1.0 (基础镜像openEuler 24.03) |

**解读**：同一 v26.1.0 版本提供两个 OS 底座的镜像，对应两条 Dockerfile 路径，分别使用 `Dockerfile.ubuntu` 和 `Dockerfile.openeuler` 作为构建入口。

### 表 3：Tag 字段说明（v26.0.0 及以前）

| 字段   | 示例值       | 说明                       |
|------|-----------|--------------------------|
| `版本` | `v26.0.0` | Ascend Device Plugin 版本号 |

**解读**：旧版 Tag 仅含版本号，不区分操作系统，与新规范形成对照，说明格式演进的目的。

### 表 4：Ascend Device Plugin 26.0.0 镜像清单

| Tag       | Dockerfile                                                                                                         | 镜像内容                                            |
|-----------|--------------------------------------------------------------------------------------------------------------------|-------------------------------------------------|
| `v26.0.0` | [Dockerfile](https://gitcode.com/Ascend/mind-cluster/blob/v26.0.0/component/ascend-device-plugin/build/Dockerfile) | Ascend Device Plugin v26.0.0 (基础镜像Ubuntu 22.04) |

**解读**：v26.0.0 Dockerfile 路径位于 `component/ascend-device-plugin/build/Dockerfile`，而 v26.1.0 已迁移到 `docker/ascend-device-plugin/v26.1.0/` 目录下，说明仓库组织结构也随版本发生了调整。

### 表 5：软件依赖

| 软件名称         | 支持的版本                          | 安装位置 | 说明                                                               |
|--------------|--------------------------------|------|------------------------------------------------------------------|
| Kubernetes   | 1.17.x~1.34.x（推荐使用1.19.x及以上版本） | 所有节点 | 了解 K8s 的使用请参见 [Kubernetes 文档](https://kubernetes.io/zh-cn/docs/) |
| Docker       | 18.09.x~28.5.1                 | 所有节点 | 可从 [Docker 社区或官网](https://docs.docker.com/engine/install/) 获取    |
| Containerd   | 1.4.x~2.1.4（推荐使用1.6.x版本）       | 所有节点 | 可从 Containerd 的 [官网](https://containerd.io/downloads/) 获取        |
| 昇腾AI处理器驱动和固件 | 请参见版本配套表                       | 计算节点 | 请参见《CANN 软件安装指南》中的"安装NPU驱动和固件"章节                                 |
| UMDK软件包      | 请参见版本配套表                       | 计算节点 | 针对Atlas 850 系列硬件产品、Atlas 950 SuperPod产品，在构建镜像时需要                 |

**解读**：K8s/Docker/Containerd 三者为所有节点共享依赖；驱动固件与 UMDK 仅计算节点需要；UMDK 的引入条件明确指向 Atlas 850 与 Atlas 950 SuperPod 这两类特定硬件产品。

### 表 6：硬件规格要求

| 名称  | 要求    |
|-----|-------|
| CPU | 0.5核  |
| 内存  | 0.5GB |

**解读**：插件本身极轻量（0.5 核 / 0.5GB），重负载在于它所管理的 NPU 设备而非插件进程本身，这也符合 Device Plugin 作为 Kubelet 扩展的标准资源占用量级。

---

## 【公式解读】

原文无公式。

---

## 【关联】

Ascend Device Plugin 在 MindCluster 集群调度体系中处于**设备资源抽象层**，向上对接 **Kubernetes/kubelet** 与上层资源调度服务 **ClusterD**，向下对接**昇腾设备驱动**与**灵衢网络驱动**，横向与 **Ascend Docker Runtime**（负责实际挂载）、**Volcano**（可选调度器）协作。完整关系如下：

- **kubelet ↔ Ascend Device Plugin**：插件通过 K8s Device Plugin 标准机制向 kubelet 注册和上报 `huawei.com/Ascend*` 自定义资源，并在故障时让 kubelet 将不健康设备从可用资源中剔除。
- **Ascend Device Plugin ↔ ClusterD**：设备发现（型号、个数）、健康状态、故障信息、灵衢网络状态都同时上报给 ClusterD，作为上层调度决策依据。
- **Ascend Device Plugin → Ascend Docker Runtime**：设备分配阶段通过**环境变量**把芯片信息透传给 Ascend Docker Runtime，由其完成最终挂载。
- **Ascend Device Plugin ↔ 昇腾设备驱动**：设备发现与故障订阅的数据源；芯片故障 → 插件触发剔除/热复位/重调度。
- **Ascend Device Plugin ↔ 灵衢驱动**：单独的网络故障订阅通道，用于将灵衢（华为自研高性能网络）状态纳入 K8s 资源视图。
- **Ascend Device Plugin ↔ Volcano（可选）**：除 Atlas 200I SoC A1 核心板之外的产品，可选用 Volcano 配置文件 `device-plugin-volcano-{version}.yaml` 部署，对接 Volcano 调度器。
- **依赖关系（构建/运行）**：驱动与固件为计算节点前置；UMDK 仅在 Atlas 850、Atlas 950 SuperPod 构建镜像时引入。

---

## 【使用方法】

### 在线获取与重打标签

```bash
# 1. 拉取官方镜像（{tag} 替换为实际版本，如 v26.1.0-ubuntu22.04）
docker pull swr.cn-south-1.myhuaweicloud.com/ascendhub/ascend-k8sdeviceplugin:{tag}

# 2. 重打本地标签
docker tag swr.cn-south-1.myhuaweicloud.com/ascendhub/ascend-k8sdeviceplugin:{tag} ascend-k8sdeviceplugin:{tag}
```

### 本地构建（v26.1.0+，以 linux-aarch64 + Ubuntu 22.04 为例）

```bash
docker build --no-cache -t ascend-k8sdeviceplugin:v26.1.0 ./ -f Dockerfile.ubuntu
```

> 注意：若 Docker < 18.09 或未启用 BuildKit，需先执行 `export DOCKER_BUILDKIT=1`，否则 `TARGETPLATFORM` 变量无法注入导致构建失败。

### 本地构建（v26.0.0 及更早版本）

```bash
wget https://gitcode.com/Ascend/mind-cluster/releases/download/v26.0.0/Ascend-mindxdl-device-plugin_26.0.0_linux-aarch64.zip
unzip Ascend-mindxdl-device-plugin_26.0.0_linux-aarch64.zip -d Ascend-mindxdl-device-plugin_26.0.0_linux-aarch64
cd Ascend-mindxdl-device-plugin_26.0.0_linux-aarch64
docker build --no-cache -t ascend-k8sdeviceplugin:v26.0.0 ./ -f Dockerfile
```

### 部署步骤

1. **打节点标签**（按处理器型号匹配）：
   ```bash
   kubectl label nodes <node-name> accelerator=huawei-Ascend910
   ```
2. **应用 YAML**（先替换文件中 `{tag}` 为实际版本）：
   ```bash
   # 不使用 Volcano（除 Atlas 200I SoC A1 核心板之外的产品）
   kubectl apply -f device-plugin-{version}.yaml
   # 使用 Volcano（除 Atlas 200I SoC A1 核心板之外的产品）
   kubectl apply -f device-plugin-volcano-{version}.yaml
   ```
3. **验证 Pod 运行**：
   ```bash
   kubectl get pods -A | grep device-plugin
   ```
   预期：相关 Pod 状态为 Running。
4. **检查节点资源是否上报**：
   ```bash
   kubectl describe node <npu-node-name> | grep "huawei.com/Ascend"
   ```
   预期：可见 `huawei.com/Ascend` 资源容量与可分配数值。

### 关键配置项（原文提及）

- **故障处理级别**：可配置；故障反复或长时间连续存在时会自动升级（具体可配置项原文未列出）。
- **节点标签**：`accelerator=huawei-Ascend910`（示例，按实际型号填写）。
- **镜像 Tag**：v26.1.0 起必须包含操作系统后缀，旧版仅含版本号。
