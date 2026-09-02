# Cluster Scheduling Component NodeD

> 仓 `mind-cluster` · 路径 `docker/noded/OVERVIEW.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mind-cluster/docker/noded/OVERVIEW.md

# NodeD Overview 文档深度解读

## 【定位】

本篇文档描述了 MindCluster 集群调度组件 **NodeD** 的能力与使用方式：它部署在计算节点上，通过 IPMI 采集节点的 CPU、内存、磁盘故障信息，并将异常上报给上层调度服务 ClusterD，从而在节点故障时让训练任务快速退出、阻止新任务调度到故障节点。

---

## 【技术要点】

1. **节点故障采集与上报**：NodeD 通过 IPMI 检索计算节点的 CPU、内存、磁盘故障信息，并周期性地将节点故障信息上报给上层资源调度服务（ClusterD）。
2. **部署位置**：以容器方式部署在 Kubernetes 集群的 compute nodes 上（管理节点部署 ClusterD）。
3. **镜像版本与基础 OS**：
   - v26.1.0 起 tag 格式为 `<version>-<os>`，支持 `ubuntu22.04` 与 `openeuler24.03` 两种基础镜像。
   - v26.0.0 及更早版本 tag 仅含 `<version>`，基础镜像为 Ubuntu 22.04。
4. **软件依赖**：
   - Kubernetes 支持版本范围 1.17.x ~ 1.34.x，**推荐 1.19.x 及以上**。
   - ClusterD 必须与 NodeD 版本一致，部署在管理节点。
   - UMDK 软件包为 Atlas 850、Atlas 950 SuperPod 产品的必备依赖。
5. **硬件资源占用**：CPU **0.5 cores**、Memory **0.3 GB**。
6. **本地构建约束（v26.1.0+）**：Docker 需启用 BuildKit 才能读取 `TARGETPLATFORM` 内置变量；Docker 版本低于 18.09 或未手动启用 BuildKit 时需执行 `export DOCKER_BUILDKIT=1`，否则镜像构建失败。

---

## 【关键机制与数据】

**数据流（原文）**：

> Retrieves CPU, memory, and disk fault information of compute nodes from IPMI.
> Reports CPU, memory, and disk fault information of compute nodes to ClusterD.

即 NodeD 的工作机制是一条线性数据通路：

```
IPMI (CPU/Mem/Disk 故障信息) → NodeD (compute node 上) → ClusterD (management node 上) → 上层资源调度服务
```

**触发与上报时机（原文）**：
- "Periodically sends node fault information to the upper-level resource scheduling service." —— 周期性地把节点故障信息推送给上层，文档未给出具体周期数值。
- "detects abnormal node states" —— 检测节点异常状态后介入。

**性能 / 资源数据（原文）**：
- CPU 占用：0.5 cores
- 内存占用：0.3 GB

---

## 【表格解读】

### 表 1：Tag Convention（v26.1.0+ 起）

| Field     | Example       | Description                       |
|-----------|---------------|-----------------------------------|
| `version` | `v26.1.0`     | Version Number of NodeD           |
| `os`      | `ubuntu22.04` | Operating System for NodeD Images |

**解读**：从 v26.1.0 起，镜像 tag 必须同时包含版本号与操作系统名，做到"一镜像一 OS"显式声明，方便异构 OS 集群同时部署。

### 表 2：NodeD 26.1.0 镜像与 Dockerfile 链接

| Tag                      | Dockerfile                                                                                                            | Image Content                               |
|--------------------------|-----------------------------------------------------------------------------------------------------------------------|---------------------------------------------|
| `v26.1.0-ubuntu22.04`    | [Dockerfile.ubuntu](https://gitcode.com/Ascend/mind-cluster/blob/master/docker/noded/v26.1.0/Dockerfile.ubuntu)       | NodeD v26.1.0 (Base Image: Ubuntu 22.04)    |
| `v26.1.0-openeuler24.03` | [Dockerfile.openeuler](https://gitcode.com/Ascend/mind-cluster/blob/master/docker/noded/v26.1.0/Dockerfile.openeuler) | NodeD v26.1.0 (Base Image: openEuler 24.03) |

**解读**：同一版本提供两种 OS 基础镜像，Dockerfile 分别存放于 `docker/noded/v26.1.0/` 目录下，文件名按 OS 区分。

### 表 3：v26.0.0 及更早 tag 字段

| Field     | Example   | Description             |
|-----------|-----------|-------------------------|
| `version` | `v26.0.0` | Version Number of NodeD |

**解读**：旧版本 tag 仅含版本号，OS 信息隐含。

### 表 4：NodeD 26.0.0 镜像与 Dockerfile 链接

| Tag       | Dockerfile                                                                                          | Image Content                            |
|-----------|-----------------------------------------------------------------------------------------------------|------------------------------------------|
| `v26.0.0` | [Dockerfile](https://gitcode.com/Ascend/mind-cluster/blob/v26.0.0/component/noded/build/Dockerfile) | NodeD v26.0.0 (Base Image: Ubuntu 22.04) |

**解读**：旧版本 Dockerfile 路径在 `component/noded/build/` 下，与新版本 `docker/noded/<version>/` 路径布局不同。

### 表 5：软件依赖

| Software              | Supported Versions                          | Installation Location | Description                                                                 |
|-----------------------|---------------------------------------------|-----------------------|-----------------------------------------------------------------------------|
| Kubernetes            | 1.17.x~1.34.x (1.19.x or later recommended) | All nodes             | See [Kubernetes Documentation](https://kubernetes.io/docs/)                 |
| ClusterD              | Same version as NodeD                       | Management nodes      | Fault information reported by NodeD is aggregated and processed by ClusterD |
| UMDK software package | See version compatibility table             | Compute nodes         | Necessary for Atlas 850、Atlas 950 SuperPod Products                         |

**解读**：
- Kubernetes 是 NodeD 运行的容器编排底座，覆盖范围较广但推荐使用 1.19.x+；
- ClusterD **必须版本对齐**才能正确聚合处理故障数据；
- UMDK 仅在特定 Atlas 硬件产品（Atlas 850、Atlas 950 SuperPod）上为必需依赖，常规部署可按兼容性表决定是否安装。

### 表 6：硬件资源需求

| Resource | Requirement |
|----------|-------------|
| CPU      | 0.5 cores   |
| Memory   | 0.3 GB      |

**解读**：NodeD 自身资源占用极轻，属轻量级常驻 Agent；这与其"周期性采集 + 上报"的轻负载特性相符。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **上游（数据来源）**：**IPMI**。NodeD 通过 IPMI 检索 CPU、内存、磁盘的故障事件，是 NodeD 的唯一数据采集通道。
- **下游（数据去向）**：**ClusterD**（集群调度组件）。ClusterD 聚合 NodeD 上报的故障信息并交由上层资源调度服务处理，文档明文标注 ClusterD 必须与 NodeD "same version"。
- **运行底座**：**Kubernetes**（1.17.x ~ 1.34.x，推荐 1.19.x+）。NodeD 以 Pod 形式通过 `kubectl apply` 部署在 compute nodes 上，节点需打标签 `workerselector=dls-worker-node` 以便集群调度匹配。
- **配套组件**：**UMDK 软件包**，仅在 Atlas 850 / Atlas 950 SuperPod 产品上为必需依赖。
- **镜像 / 源码仓库**：[Ascend/mind-cluster](https://gitcode.com/Ascend/mind-cluster)，NodeD 26.1.0 的 Dockerfile 位于 `docker/noded/v26.1.0/` 目录下。
- **同级社区文档**：[MindCluster Atlas Community](https://www.hiascend.com/document/detail/zh/mindcluster/latest/clustersched/dlug/docs/zh/scheduling/01_introduction/00_overview.md)。
- **本地化版本**：文末内部链接 `./OVERVIEW.zh.md` 提供中文版 OVERVIEW。

---

## 【使用方法】

### 1. 获取镜像（在线拉取）

```bash
docker pull swr.cn-south-1.myhuaweicloud.com/ascendhub/noded:{tag}
docker tag swr.cn-south-1.myhuaweicloud.com/ascendhub/noded:{tag} noded:{tag}
```

### 2. 本地构建

**v26.1.0 及之后**：从 `docker/noded/v26.1.0/` 目录下载对应 `Dockerfile.ubuntu` 或 `Dockerfile.openeuler`，然后：

```bash
docker build --no-cache -t noded:v26.1.0 ./ -f Dockerfile.ubuntu
```

> 若 Docker < 18.09 或未启用 BuildKit，需先 `export DOCKER_BUILDKIT=1`，否则因无法读取 `TARGETPLATFORM` 而构建失败。

**v26.0.0 及之前**：下载官方发布包、解压后用包内 Dockerfile 构建：

```bash
wget https://gitcode.com/Ascend/mind-cluster/releases/download/v26.0.0/Ascend-mindxdl-noded_26.0.0_linux-aarch64.zip
unzip Ascend-mindxdl-noded_26.0.0_linux-aarch64.zip -d Ascend-mindxdl-noded_26.0.0_linux-aarch64
cd Ascend-mindxdl-noded_26.0.0_linux-aarch64
docker build --no-cache -t noded:v26.0.0 ./ -f Dockerfile
```

### 3. 部署到 Kubernetes

```bash
# 给目标节点打标签
kubectl label nodes <node-name> workerselector=dls-worker-node

# 替换 YAML 中的 {tag} 后部署
kubectl apply -f noded-{version}.yaml
```

### 4. 验证部署

```bash
kubectl get pods -A | grep noded
```

预期：相应命名空间下 NodeD 相关 Pod 处于 Running 状态。
