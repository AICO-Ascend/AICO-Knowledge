# Cluster Scheduling Component ClusterD

> 仓 `mind-cluster` · 路径 `docker/clusterd/OVERVIEW.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mind-cluster/docker/clusterd/OVERVIEW.md

# ClusterD OVERVIEW.md 深度解读

## 【定位】

这篇文档是 MindCluster 集群调度组件 **ClusterD** 的总览说明,旨在向使用者/部署者介绍 ClusterD 作为部署在管理节点上的集群级故障与资源汇聚服务的核心能力——统一采集、汇聚、分析全集群的作业/资源/故障信息并确定故障处理等级与策略,同时给出镜像拉取/本地构建/部署上线的快速上手指引。

---

## 【技术要点】

1. **部署位置与定位**:ClusterD 是 MindCluster 集群调度组件之一,部署在**管理节点**上,作用于集群维度而非单节点维度,解决"单机多故障各自独立处理导致作业同时被多种恢复策略作用"的协调难题。

2. **三大数据汇聚源**(故障上下文采集):
   - 从 **Atlas Device Plugin** 获取芯片信息
   - 从 **NodeD** 获取 CPU/内存/磁盘健康状态、DPC 共享存储故障、灵衢(Lingqu)网络故障信息
   - 从 **ConfigMap 或 gRPC** 获取公共故障信息

3. **三维度统计分析**:ClusterD 从 **jobs(作业)、chips(芯片)、faults(故障)** 三个维度进行统计分析,统一确定故障处理**等级(level)与策略(policy)**。

4. **下游交互对象**(4 条):
   - 汇聚全集群资源信息后上报给 **Ascend-volcano-plugin**
   - 监控集群作业信息并向 **CCAE** 上报作业状态、资源使用情况
   - 与训练容器内进程建立连接,控制训练进程执行**重计算(recomputation)**动作
   - 与**带外(out-of-band)服务**交互以传递作业信息

5. **镜像标签规范**:自 **v26.1.0** 起标签格式改为 `<version>-<os>`(如 `v26.1.0-ubuntu22.04`、`v26.1.0-openeuler24.03`);v26.0.0 及更早版本使用纯版本号格式 `<version>`。

6. **软硬件约束**:Kubernetes 支持范围 **1.17.x ~ 1.34.x(推荐 1.19.x 及以上)**;Atlas Device Plugin 与 NodeD 需与 ClusterD **同版本**部署在**计算节点**上;管理节点资源随集群规模线性增长(100/500/1000 节点对应不同 CPU 与内存需求)。

---

## 【关键机制与数据】

**工作原理/数据流**(基于原文 Features 与 Upstream and Downstream Dependencies):

- **上行汇聚(原文)**:"Obtains chip, node, and network information from Atlas Device Plugin and NodeD components, and retrieves public fault information from ConfigMap or gRPC."——ClusterD 从三类上游(Atlas Device Plugin / NodeD / ConfigMap 或 gRPC)汇聚故障与资源原始数据。
- **核心处理(原文)**:"Aggregates the above fault information for upper-level cluster scheduling services to query."——聚合后供上层集群调度服务查询。
- **执行控制(原文)**:"Establishes connections with training containers to control training processes for recomputation actions."——对训练容器建立连接以触发重计算。
- **带外通信(原文)**:"Interacts with out-of-band services to transmit job information."——与带外服务传递作业信息。

**性能/容量数据**(原文表格提供):

| 集群规模 | CPU | 内存 |
|---|---|---|
| Up to 100 Nodes | 1 core | 1 GB |
| 500 Nodes | 2 cores | 2 GB |
| 1000 Nodes | 4 cores | 8 GB |

原文未给出吞吐量、延迟等运行时性能指标;以上为部署侧硬件要求。

---

## 【表格解读】

### 表 1:Tag Convention(v26.1.0 起)

| Field | Example | Description |
|-------|---------|-------------|
| `version` | `v26.1.0` | Version Number of ClusterD |
| `os` | `ubuntu22.04` | Operating System for ClusterD Images |

**解读**:自 v26.1.0 起,镜像标签由"纯版本号"扩展为"版本号 + 操作系统"双段式,以适配多 OS 镜像分发;`version` 指 ClusterD 软件版本,`os` 标识基础镜像操作系统(已支持 ubuntu22.04、openEuler 24.03)。

### 表 2:ClusterD 26.1.0 镜像列表

| Tag | Dockerfile | Image Content |
|-----|------------|---------------|
| `v26.1.0-ubuntu22.04` | [Dockerfile.ubuntu](https://gitcode.com/Ascend/mind-cluster/blob/master/docker/clusterd/v26.1.0/Dockerfile.ubuntu) | ClusterD v26.1.0 (Base Image: Ubuntu 22.04) |
| `v26.1.0-openeuler24.03` | [Dockerfile.openeuler](https://gitcode.com/Ascend/mind-cluster/blob/master/docker/clusterd/v26.1.0/Dockerfile.openeuler) | ClusterD v26.1.0 (Base Image: openEuler 24.03) |

**解读**:v26.1.0 提供两个官方镜像,均基于 ClusterD v26.1.0 软件,基础镜像分别选择 Ubuntu 22.04 与 openEuler 24.03,两条 Dockerfile 链接位于 `docker/clusterd/v26.1.0/` 目录下,源码在 `master` 分支。

### 表 3:Tag Convention(v26.0.0 及更早版本)

| Field | Example | Description |
|-------|---------|-------------|
| `version` | `v26.0.0` | Version Number of ClusterD |

**解读**:旧版标签仅含 `version` 一段,无 OS 标识;原文中以 v26.0.0 为示例。

### 表 4:ClusterD 26.0.0 镜像列表

| Tag | Dockerfile | Image Content |
|-----|------------|---------------|
| `v26.0.0` | [Dockerfile](https://gitcode.com/Ascend/mind-cluster/blob/v26.0.0/component/clusterd/build/Dockerfile) | ClusterD v26.0.0 (Base Image: Ubuntu 22.04) |

**解读**:v26.0.0 单一官方镜像,基础镜像固定为 Ubuntu 22.04;Dockerfile 路径位于 `component/clusterd/build/Dockerfile`,源码在 `v26.0.0` 分支。注意:v26.0.0 与 v26.1.0 的 Dockerfile 路径与分支策略不同,体现了目录重构(从 `component/clusterd/build/` 迁移到 `docker/clusterd/v26.1.0/`)。

### 表 5:软件依赖(Software Dependencies)

| Software | Supported Versions | Installation Location | Description |
|----------|--------------------|-----------------------|-------------|
| Kubernetes | 1.17.x~1.34.x (1.19.x or later recommended) | All nodes | See Kubernetes Documentation |
| Atlas Device Plugin | Same version as ClusterD | Compute nodes | ClusterD depends on Atlas Device Plugin to report chip information |
| NodeD | Same version as ClusterD | Compute nodes | ClusterD depends on NodeD to report node fault information |

**解读**:三件依赖中,Kubernetes 是基础设施层(覆盖范围最广,支持跨度从 1.17.x 到 1.34.x,推荐 1.19.x 及以上以获得更好兼容性);Atlas Device Plugin 与 NodeD 是同源组件层面的强耦合依赖——必须与 ClusterD **严格同版本**,部署在**计算节点**(而非管理节点)。两者作用分别为上报芯片信息与上报节点故障信息。

### 表 6:硬件要求(Hardware Requirements)

| Resource | Up to 100 Nodes | 500 Nodes | 1000 Nodes |
|----------|-----------------|-----------|------------|
| CPU | 1 core | 2 cores | 4 cores |
| Memory | 1 GB | 2 GB | 8 GB |

**解读**:管理节点资源需求随集群规模增长呈非线性——100 节点仅需 1 core/1 GB(轻量级),500 节点需 2 cores/2 GB(线性翻倍),1000 节点需 4 cores/8 GB(**内存增长 4 倍**,说明 ClusterD 在大规模集群下的内存消耗主要来自汇聚的全量故障与资源状态信息)。此表为部署 Capacity Planning 的核心参考。

---

## 【公式解读】

原文无公式。

---

## 【关联】

依据文末内部链接 `./OVERVIEW.zh.md`,本英文版 OVERVIEW 与其中文版本一一对应,二者内容结构同构,中文版面向中文用户。

此外,ClusterD 在 MindCluster 生态中处于**汇聚层中枢**位置,上下游关联关系如下(均来自原文 Upstream and Downstream Dependencies):

- **上游数据源**:
  - **Atlas Device Plugin**(每个计算节点)→ 提供芯片信息
  - **NodeD**(每个计算节点)→ 提供 CPU/内存/磁盘健康状态、DPC 共享存储故障、灵衢网络故障
  - **ConfigMap / gRPC**→ 提供公共故障信息

- **下游消费方**:
  - **Ascend-volcano-plugin**→ 接收 ClusterD 聚合的全集群资源信息
  - **CCAE**→ 接收 ClusterD 上报的作业状态与资源使用
  - **训练容器内进程**→ 接收 ClusterD 的重计算(recomputation)控制指令
  - **带外服务(Out-of-band services)**→ 与 ClusterD 互传作业信息

- **镜像/代码关联**:
  - `v26.1.0` 源码路径:`docker/clusterd/v26.1.0/`(master 分支)
  - `v26.0.0` 源码路径:`component/clusterd/build/`(v26.0.0 分支)
  - 支持硬件清单需参考 `docs/zh/scheduling/01_introduction/03_supported_product_models_and_os.md`

- **辅助社区/支持通道**:MindCluster 仓、MindCluster Atlas 社区、Issue Tracker(均见 Quick Reference)。

---

## 【使用方法】

### 1. 拉取官方镜像(原文:Obtain ClusterD Image Online)

```bash
docker pull swr.cn-south-1.myhuaweicloud.com/ascendhub/clusterd:{tag}
docker tag swr.cn-south-1.myhuaweicloud.com/ascendhub/clusterd:{tag} clusterd:{tag}
```

### 2. 本地构建(v26.1.0+,原文:Local Build Steps for v26.1.0 and Later Versions)

```bash
docker build --no-cache -t clusterd:v26.1.0 ./ -f Dockerfile.ubuntu
```
> 重要前置(原文):Docker < 18.09 或未启用 BuildKit 时需先执行 `export DOCKER_BUILDKIT=1`,否则 `TARGETPLATFORM` 变量无法读取,镜像构建失败。

### 3. 本地构建(v26.0.0 及更早版本,原文:Local Build Steps for v26.0.0 and Earlier Versions)

```bash
wget https://gitcode.com/Ascend/mind-cluster/releases/download/v26.0.0/Ascend-mindxdl-clusterd_26.0.0_linux-aarch64.zip
unzip Ascend-mindxdl-clusterd_26.0.0_linux-aarch64.zip -d Ascend-mindxdl-clusterd_26.0.0_linux-aarch64
cd Ascend-mindxdl-clusterd_26.0.0_linux-aarch64
docker build --no-cache -t clusterd:v26.0.0 ./ -f Dockerfile
```

### 4. 部署与验证(原文:Deploy ClusterD)

```bash
kubectl apply -f clusterd-{version}.yaml
kubectl get pods -A | grep clusterd
```
> 部署前需将 YAML 中 `{tag}` 替换为实际镜像版本;验证通过条件:对应 namespace 中 clusterd 相关 Pod 处于 Running 状态。

### 5. 配置项

原文未涉及具体的 ConfigMap/参数配置文件内容;仅提到从 ConfigMap 或 gRPC 拉取**公共故障信息**作为数据源,但未给出 ConfigMap 的字段定义或样例。

### 6. 启用前置条件(原文:Prerequisites)

- Kubernetes 1.17.x ~ 1.34.x(推荐 1.19.x+)
- Atlas Device Plugin 与 NodeD 须与 ClusterD **同版本**、部署于**计算节点**
- 管理节点资源按集群规模参考 Hardware Requirements 表
