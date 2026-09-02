# Cluster Scheduling Component NPU Exporter

> 仓 `mind-cluster` · 路径 `docker/npu-exporter/OVERVIEW.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mind-cluster/docker/npu-exporter/OVERVIEW.md

# NPU Exporter Overview 深度解读

## 【定位】

本文档是 MindCluster 集群调度组件中 **NPU Exporter** 的产品总览，定位是说明该组件作为部署在计算节点上的"芯片数据指标上报告警代理"，向 Prometheus / Telegraf 等标准监控系统暴露 Atlas AI 处理器的运行指标（利用率、温度、电压、显存、vNPU、AI Core 等），并提供镜像构建、Kubernetes 部署、版本与硬件兼容等运维所需的全部信息。

---

## 【技术要点】

1. **组件归属与部署位置**：NPU Exporter 是 MindCluster 集群调度组件之一，**部署在计算节点上**，负责上报告警芯片相关指标数据。
2. **两种监控集成方式**：适配 **Prometheus** 与 **Telegraf** 两套 hook 函数，分别为二者提供标准调用接口（即标准的 metrics 拉取接口）。
3. **数据采集三层链路**：
   - 从驱动读取芯片与网络信息 → 写入本地缓存；
   - 从 Kubernetes 标准 **CRI** 接口读取容器信息 → 写入本地缓存；
   - 对外实现 Prometheus / Telegraf 接口，由它们周期性拉取缓存中的指标。
4. **监控指标范围**：
   - Atlas AI 处理器利用率、温度、电压、显存等实时数据；
   - vNPU 的 AI Core 利用率、总显存、已用显存。
5. **支持自定义指标扩展**：用户可参照官方提供的 demo 开发自定义指标插件。
6. **镜像 Tag 规范**：自 **v26.1.0** 起 Tag 改为 `<version>-<os>` 形式（如 `v26.1.0-ubuntu22.04`）；v26.0.0 及更早版本使用纯 `<version>` 形式。
7. **指标暴露端口**：NPU Exporter 通过 **HTTP 8082** 端口的 `/metrics` 路径对外暴露指标。
8. **构建前置条件**：本地构建需要 Docker ≥ 18.09 或显式开启 BuildKit（否则 `TARGETPLATFORM` 全局变量无法解析），可通过 `export DOCKER_BUILDKIT=1` 临时开启。

---

## 【关键机制与数据】

原文给出的工作机制（数据流）可概括为：

```
[Atlas 驱动 / 固件 / UMDK]  →  NPU Exporter 本地缓存  ←  [K8s CRI 容器信息]
                                    │
                                    ▼
                  Prometheus / Telegraf 周期性拉取
                                    │
                                    ▼
                       http://<pod-ip>:8082/metrics
```

- **原文：** "Retrieves chip and network information from the driver and stores it in a local cache."
- **原文：** "Retrieves container information from the Kubernetes standard CRI interface and stores it in a local cache."
- **原文：** "Implements Prometheus or Telegraf interfaces for them to periodically retrieve cached data metrics."
- **原文：** "Access monitoring metrics: `curl http://<pod-ip>:8082/metrics`"

性能/容量数据方面，原文仅在 Hardware Requirements 中给出了最小资源需求（**CPU 1 core、Memory 1 GB**），并未提供吞吐、时延或采样率等性能数据。

---

## 【表格解读】

### 表 1：Tag 命名规范（v26.1.0 起）

| Field     | Example       | Description                              |
|-----------|---------------|------------------------------------------|
| `version` | `v26.1.0`     | Version Number of NPU Exporter           |
| `os`      | `ubuntu22.04` | Operating System for NPU Exporter Images |

**解读：** 自 v26.1.0 起 Tag 改为 `<version>-<os>` 双段式，`<os>` 字段明确区分基础镜像操作系统（Ubuntu 22.04 / openEuler 24.03），便于在不同 OS 的计算节点上选择匹配的镜像。

### 表 2：NPU Exporter 26.1.0 镜像列表

| Tag                      | Dockerfile                                                                                                                   | Image Content                                      |
|--------------------------|------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------|
| `v26.1.0-ubuntu22.04`    | [Dockerfile.ubuntu](https://gitcode.com/Ascend/mind-cluster/blob/master/docker/npu-exporter/v26.1.0/Dockerfile.ubuntu)       | NPU Exporter v26.1.0 (Base Image: Ubuntu 22.04)    |
| `v26.1.0-openeuler24.03` | [Dockerfile.openeuler](https://gitcode.com/Ascend/mind-cluster/blob/master/docker/npu-exporter/v26.1.0/Dockerfile.openeuler) | NPU Exporter v26.1.0 (Base Image: openEuler 24.03) |

**解读：** v26.1.0 同时发布 Ubuntu 22.04 与 openEuler 24.03 两种基础镜像版本，Dockerfile 路径位于 `docker/npu-exporter/v26.1.0/` 目录下的两个分支文件。

### 表 3：v26.0.0 及更早 Tag 命名规范

| Field     | Example   | Description                    |
|-----------|-----------|--------------------------------|
| `version` | `v26.0.0` | Version Number of NPU Exporter |

**解读：** 早期版本 Tag 仅含 version 字段，不区分操作系统（因为底层均基于 Ubuntu 22.04）。

### 表 4：NPU Exporter 26.0.0 镜像列表

| Tag       | Dockerfile                                                                                                 | Image Content                                   |
|-----------|------------------------------------------------------------------------------------------------------------|-------------------------------------------------|
| `v26.0.0` | [Dockerfile](https://gitcode.com/Ascend/mind-cluster/blob/v26.0.0/component/npu-exporter/build/Dockerfile) | NPU Exporter v26.0.0 (Base Image: Ubuntu 22.04) |

**解读：** v26.0.0 Dockerfile 路径位于仓库旧结构 `component/npu-exporter/build/Dockerfile`，与新版本（`docker/npu-exporter/`）路径布局不同。

### 表 5：软件依赖（Software Dependencies）

| Software                               | Supported Versions                          | Installation Location | Description                                                                      |
|----------------------------------------|---------------------------------------------|-----------------------|----------------------------------------------------------------------------------|
| Kubernetes                             | 1.17.x~1.34.x (1.19.x or later recommended) | All nodes             | See [Kubernetes Documentation](https://kubernetes.io/docs/)                      |
| Prometheus                             | Latest stable version recommended           | Monitoring nodes      | NPU Exporter adapts Prometheus hook functions to provide monitoring data         |
| Atlas AI Processor Driver and Firmware | See version compatibility table             | Compute nodes         | See "Installing NPU Driver and Firmware" in the CANN Software Installation Guide |
| UMDK software package                  | See version compatibility table             | Compute nodes         | Necessary for Atlas 850、Atlas 950 SuperPod Products                              |

**解读：**
- K8s 支持范围为 1.17.x ~ 1.34.x，但 **推荐使用 1.19.x 及以后版本**；
- Prometheus 仅安装在监控节点即可（计算节点上 NPU Exporter 自适应其 hook 函数）；
- 驱动/固件需严格匹配 CANN 兼容性矩阵；
- **UMDK 是 Atlas 850 与 Atlas 950 SuperPod 产品的硬性前置**，普通节点无需。

### 表 6：硬件需求（Hardware Requirements）

| Resource | Requirement |
|----------|-------------|
| CPU      | 1 core      |
| Memory   | 1 GB        |

**解读：** NPU Exporter 本身为轻量级指标中转代理，对宿主资源占用极低，单核 1GB 即可满足最小部署要求。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **集群调度体系上游组件**：NPU Exporter 属于 MindCluster 集群调度组件，文档头标注仓库为 [MindCluster Repository](https://gitcode.com/Ascend/mind-cluster)，与其他 MindCluster 子组件（如 Volcano、Scheduler 插件等）共同构成集群调度栈。
- **监控下游**：通过 Prometheus / Telegraf 暴露指标，对接上层监控系统。
- **数据来源上游**：
  - **Atlas AI 处理器驱动与固件**（CANN 体系）—— 提供芯片级指标；
  - **UMDK** —— 仅 Atlas 850 / Atlas 950 SuperPod 产品所需；
  - **Kubernetes 标准 CRI 接口** —— 提供容器维度信息。
- **节点调度协同**：部署前需对 K8s 节点打标签 `workerselector=dls-worker-node`，说明 NPU Exporter 与 dls-worker 调度选择器配套使用。
- **版本谱系**：v26.0.0 Dockerfile 路径在 `component/npu-exporter/build/`，v26.1.0 迁移至 `docker/npu-exporter/v26.1.0/`，反映仓库目录结构升级。
- **多语言版本**：文末内部链接 `./OVERVIEW.zh.md` 为本文中文版本。
- **社区/帮助渠道**：
  - [MindCluster Atlas Community](https://www.hiascend.com/document/detail/zh/mindcluster/latest/clustersched/dlug/docs/zh/scheduling/01_introduction/00_overview.md)
  - [Issue Tracker](https://gitcode.com/Ascend/mind-cluster/issues)
- **自定义扩展**：支持用户基于提供的 demo 开发自定义指标插件，构成与官方特性的可扩展关系。

---

## 【使用方法】

### 1. 在线拉取镜像

```bash
# 拉取
docker pull swr.cn-south-1.myhuaweicloud.com/ascendhub/npu-exporter:{tag}
# 重打本地 Tag
docker tag swr.cn-south-1.myhuaweicloud.com/ascendhub/npu-exporter:{tag} npu-exporter:{tag}
```

### 2. 本地构建（v26.1.0 及之后）

```bash
# 临时启用 BuildKit（Docker < 18.09 或未默认启用时必需）
export DOCKER_BUILDKIT=1
# 构建（linux-aarch64 / Ubuntu 22.04 / v26.1.0 示例）
docker build --no-cache -t npu-exporter:v26.1.0 ./ -f Dockerfile.ubuntu
```

### 3. 本地构建（v26.0.0 及之前）

```bash
wget https://gitcode.com/Ascend/mind-cluster/releases/download/v26.0.0/Ascend-mindxdl-npu-exporter_26.0.0_linux-aarch64.zip
unzip Ascend-mindxdl-npu-exporter_26.0.0_linux-aarch64.zip -d Ascend-mindxdl-npu-exporter_26.0.0_linux-aarch64
cd Ascend-mindxdl-npu-exporter_26.0.0_linux-aarch64
docker build --no-cache -t npu-exporter:v26.0.0 ./ -f Dockerfile
```

### 4. 部署到 Kubernetes

```bash
# 打节点标签（用于集群调度匹配）
kubectl label nodes <node-name> workerselector=dls-worker-node

# 启动（需先将 YAML 中 {tag} 替换为实际版本）
kubectl apply -f npu-exporter-{version}.yaml

# 验证 Pod 状态
kubectl get pods -A | grep npu-exporter
# 预期：对应命名空间下 npu-exporter 相关 Pod 处于 Running
```

### 5. 访问监控指标

```bash
curl http://<pod-ip>:8082/metrics
```

> 原文未涉及的：未给出 NPU Exporter YAML 文件的具体字段内容（如 env、volume mount、resource limit 等），也未提供 Prometheus 端 scrape 配置示例；这些需要查阅 `docker/npu-exporter/v26.1.0/` 目录下的 yaml 与具体组件文档。
