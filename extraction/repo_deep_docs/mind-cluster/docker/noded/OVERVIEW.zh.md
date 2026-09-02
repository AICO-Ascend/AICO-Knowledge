# 集群调度组件 NodeD

> 仓 `mind-cluster` · 路径 `docker/noded/OVERVIEW.zh.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mind-cluster/docker/noded/OVERVIEW.zh.md

# NodeD 组件 Overview 文档深度解读

## 【定位】

**一句话**：本文档描述 MindCluster 集群调度体系中**部署在计算节点侧的故障检测组件 NodeD**——它从 IPMI 获取节点的 CPU/内存/硬盘硬件故障信息并定时上报给上层调度组件 ClusterD，用于在训练任务失败时让任务快速退出并防止新任务调度到故障节点上。

---

## 【技术要点】

- **节点级故障检测定位**：NodeD 部署在**计算节点**上（非管理节点），运行时从节点 BMC/IPMI 接口拉取本机硬件健康状态，覆盖 **CPU、内存、硬盘**三类故障。
- **上行链路单一**：故障信息统一上报给 **ClusterD**（管理节点侧的集群调度组件），由 ClusterD 完成汇总与调度决策；NodeD 不直接与 Kubernetes Scheduler 通信。
- **定时推送机制**：组件具备"**定时发送节点故障信息给资源调度的上层服务**"的能力，因此采集/上报是周期性而非事件触发式。
- **Tag 命名规范双轨制**：
  - 自 **v26.1.0** 起：`<版本>-<操作系统>`（例 `v26.1.0-ubuntu22.04`、`v26.1.0-openeuler24.03`）
  - **v26.0.0 及以前**：仅 `<版本>`（例 `v26.0.0`）
- **Kubernetes 节点标签绑定**：部署前必须给目标节点打 `workerselector=dls-worker-node` 标签，以匹配 NodeD 调度约束。
- **硬件资源极轻量**：单实例仅需 **CPU 0.5 核 + 内存 0.3GB**。
- **镜像构建依赖**：默认依赖 **Docker BuildKit**（注入 `TARGETPLATFORM` 内置变量），Docker 版本需 ≥ **18.09**，否则需手动 `export DOCKER_BUILDKIT=1`。
- **特殊硬件构建条件**：针对 **Atlas 850 系列**与 **Atlas 950 SuperPod** 产品，构建镜像时必须安装 UMDK 软件包。

---

## 【关键机制与数据】

### 工作原理 / 数据流（原文提炼）

```
[IPMI 硬件监控接口] 
        ↓ (采集 CPU / 内存 / 硬盘故障信息)
     [NodeD 组件]   ← 部署在计算节点，周期轮询
        ↓ (定时上报)
   [ClusterD]      ← 部署在管理节点，汇总处理
        ↓
[资源调度上层服务]  ← 触发训练任务快速退出 / 排除故障节点
```

原文摘录要点：
- 原文："NodeD 是 MindCluster 集群调度组件之一，**部署在计算节点上**，用于检测节点的异常状态，从 IPMI 获取计算节点的 CPU、内存、硬盘的故障信息，并上报给 ClusterD。"
- 原文："定时发送节点故障信息给资源调度的上层服务。"
- 原文："NodeD 上报的故障信息由 ClusterD 汇总处理"（来自 ClusterD 依赖说明列）。

### 性能/资源数据

| 维度 | 数值 | 来源 |
|---|---|---|
| NodeD CPU 占用 | **0.5 核** | 原文"硬件规格要求"表 |
| NodeD 内存占用 | **0.3 GB** | 原文"硬件规格要求"表 |
| Kubernetes 版本区间 | **1.17.x ~ 1.34.x**（推荐 ≥ 1.19.x） | 原文"软件依赖"表 |
| Docker 构建最低版本 | **18.09** | 原文"重要注意事项" |
| 支持的 OS 基础镜像 | **Ubuntu 22.04**、**openEuler 24.03** | 原文 NodeD 26.1.0 镜像表 |

---

## 【表格解读】

### 表 1：v26.1.0+ Tag 规范

| 字段 | 示例值 | 说明 |
|---|---|---|
| `版本` | `v26.1.0` | NodeD 版本号 |
| `操作系统` | `ubuntu22.04` | NodeD 镜像操作系统 |

**解读**：自 v26.1.0 开始，Tag 格式由单一版本号升级为"版本+操作系统"双段式，目的是区分多 OS 基础镜像（Ubuntu 与 openEuler）的并行发布，运维方可按节点 OS 选镜像。

### 表 2：NodeD 26.1.0 支持的镜像

| Tag | Dockerfile | 镜像内容 |
|---|---|---|
| `v26.1.0-ubuntu22.04` | [Dockerfile.ubuntu](https://gitcode.com/Ascend/mind-cluster/blob/master/docker/noded/v26.1.0/Dockerfile.ubuntu) | NodeD v26.1.0 (基础镜像 Ubuntu 22.04) |
| `v26.1.0-openeuler24.03` | [Dockerfile.openeuler](https://gitcode.com/Ascend/mind-cluster/blob/master/docker/noded/v26.1.0/Dockerfile.openeuler) | NodeD v26.1.0 (基础镜像 openEuler 24.03) |

**解读**：同一 NodeD 版本提供两个 OS 变体；Dockerfile 路径从旧版的 `component/noded/build/`（v26.0.0）迁移到 `docker/noded/v26.1.0/`（v26.1.0），体现仓内目录重构。

### 表 3：v26.0.0 及以前 Tag 规范

| 字段 | 示例值 | 说明 |
|---|---|---|
| `版本` | `v26.0.0` | NodeD 版本号 |

**解读**：单段版本号格式，仅一种基础镜像（Ubuntu 22.04），无 OS 区分。

### 表 4：NodeD 26.0.0 镜像

| Tag | Dockerfile | 镜像内容 |
|---|---|---|
| `v26.0.0` | [Dockerfile](https://gitcode.com/Ascend/mind-cluster/blob/v26.0.0/component/noded/build/Dockerfile) | NodeD v26.0.0 (基础镜像 Ubuntu 22.04) |

**解读**：通过发布包方式分发，路径在旧版仓目录 `component/noded/build/Dockerfile`；本地构建需先 `wget` 安装包并 `unzip` 解压，再 `docker build`。

### 表 5：软件依赖

| 软件名称 | 支持的版本 | 安装位置 | 说明 |
|---|---|---|---|
| Kubernetes | 1.17.x~1.34.x（推荐使用1.19.x及以上版本） | 所有节点 | 了解 K8s 的使用请参见 [Kubernetes 文档](https://kubernetes.io/zh-cn/docs/) |
| ClusterD | 与 NodeD 同版本 | 管理节点 | NodeD 上报的故障信息由 ClusterD 汇总处理 |
| UMDK软件包 | 请参见版本配套表 | 计算节点 | 针对Atlas 850 系列硬件产品、Atlas 950 SuperPod产品，在构建镜像时需要 |

**解读**：
- **Kubernetes** 是 NodeD 的载体（以 Pod 形式部署），版本跨度较大（1.17.x~1.34.x）但官方推荐 ≥ 1.19.x；
- **ClusterD** 与 NodeD 必须**严格同版本**部署，避免协议/数据格式不兼容；
- **UMDK** 为可选条件依赖，仅在 Atlas 850 / Atlas 950 SuperPod 这两类特定昇腾硬件的镜像构建中需要。

### 表 6：硬件规格要求

| 名称 | 要求 |
|---|---|
| CPU | 0.5核 |
| 内存 | 0.3GB |

**解读**：NodeD 资源占用极低（亚核级别 + 亚 GB 内存），适合在每台计算节点以 DaemonSet/Kubernetes 节点部署形态常驻，不会挤占训练任务的算力资源。

---

## 【公式解读】

**原文无公式**。

---

## 【关联】

依据文末及正文中的链接与术语，NodeD 的关联拓扑如下：

- **上游数据源：[IPMI](https://www.hiascend.com/document/detail/zh/mindcluster/latest/clustersched/dlug/docs/zh/scheduling/01_introduction/00_overview.md)**（BMC 硬件管理接口）—— NodeD 的唯一故障数据来源。
- **下游汇聚方：ClusterD**—— NodeD 故障信息的上报对象，部署于管理节点，与 NodeD 同版本；进一步衔接 MindCluster 资源调度上层服务。
- **承载平台：Kubernetes**（1.17.x~1.34.x）—— NodeD 以容器化 Pod 形式运行；通过 `workerselector=dls-worker-node` 标签完成节点选择。
- **构建链路依赖**：
  - v26.1.0+：`docker/noded/v26.1.0/Dockerfile.ubuntu` 或 `Dockerfile.openeuler`，依赖 Docker BuildKit（≥18.09）。
  - v26.0.0 及以前：仓内 `component/noded/build/Dockerfile`，需先从 Release 下载安装包 `Ascend-mindxdl-noded_<ver>_linux-aarch64.zip`。
- **特殊硬件配套：[UMDK 软件包](https://gitcode.com/Ascend/mind-cluster/blob/master/docs/zh/scheduling/01_introduction/03_supported_product_models_and_os.md)** —— 仅在 Atlas 850 系列、Atlas 950 SuperPod 产品的镜像构建阶段需要。
- **同仓姊妹组件**：本文位于 `docker/noded/`，与 `docker/clusterd/`（推测）等其他调度组件镜像同仓维护；仓根入口见 [MindCluster 代码仓](https://gitcode.com/Ascend/mind-cluster)。
- **内部链接**：`./OVERVIEW.md`（英文版），内容与本文镜像对齐。
- **支撑文档链路**：[支持的产品形态和OS清单](https://gitcode.com/Ascend/mind-cluster/blob/master/docs/zh/scheduling/01_introduction/03_supported_product_models_and_os.md) 决定 NodeD 可适配的昇腾硬件型号。

---

## 【使用方法】

### 1. 在线获取镜像

```bash
docker pull swr.cn-south-1.myhuaweicloud.com/ascendhub/noded:{tag}
docker tag swr.cn-south-1.myhuaweicloud.com/ascendhub/noded:{tag} noded:{tag}
```

### 2. 本地构建（v26.1.0+，Ubuntu 示例）

```bash
# 先 export DOCKER_BUILDKIT=1（如 Docker < 18.09）
docker build --no-cache -t noded:v26.1.0 ./ -f Dockerfile.ubuntu
```

### 3. 本地构建（v26.0.0 及以前）

```bash
wget https://gitcode.com/Ascend/mind-cluster/releases/download/v26.0.0/Ascend-mindxdl-noded_26.0.0_linux-aarch64.zip
unzip Ascend-mindxdl-noded_26.0.0_linux-aarch64.zip -d Ascend-mindxdl-noded_26.0.0_linux-aarch64
cd Ascend-mindxdl-noded_26.0.0_linux-aarch64
docker build --no-cache -t noded:v26.0.0 ./ -f Dockerfile
```

### 4. 部署到 Kubernetes

```bash
# (1) 给目标计算节点打标签
kubectl label nodes <node-name> workerselector=dls-worker-node

# (2) 替换 YAML 内的 {tag} 为实际版本号后应用
kubectl apply -f noded-{version}.yaml

# (3) 验证 Pod 状态
kubectl get pods -A | grep noded
# 预期：noded 相关 Pod 状态为 Running
```

### 5. 关键配置/约束项

- **节点标签**：`workerselector=dls-worker-node`（必须）
- **Kubernetes 版本**：1.17.x~1.34.x（推荐 ≥ 1.19.x）
- **ClusterD 版本**：必须与 NodeD 同版本，部署于管理节点
- **Docker 版本**：≥ 18.09；老版本需启用 BuildKit 以解析 `TARGETPLATFORM` 变量
- **UMDK 软件包**：仅 Atlas 850 / Atlas 950 SuperPod 镜像构建时需要
- **资源限额**：每实例 CPU 0.5 核 / 内存 0.3 GB

原文未涉及 NodeD 自身的细粒度配置项（如上报周期、阈值阈值、IPMI 轮询频率等），这些需参考组件内部文档或源码。
