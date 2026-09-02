# 集群调度组件 ClusterD

> 仓 `mind-cluster` · 路径 `docker/clusterd/OVERVIEW.zh.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mind-cluster/docker/clusterd/OVERVIEW.zh.md

# ClusterD Overview 文档深度解读

---

## 【定位】

这篇文档面向运维/部署工程师，系统性说明 ClusterD（MindCluster 集群调度组件）是什么、解决什么问题、依赖哪些上下游组件、对应哪些版本镜像与 Dockerfile、如何拉取/构建/部署，以及对软件与硬件的前置要求，是 ClusterD 在 Kubernetes 集群中落地的"部署参考手册"。

---

## 【技术要点】

1. **部署形态**：ClusterD 是 MindCluster 集群调度组件之一，**部署在管理节点**（非计算节点），与 Ascend Device Plugin、NodeD 计算节点组件协同工作，自身不直接获取芯片侧细节数据。

2. **核心职责——故障协调**：解决"一个节点可能发生多个故障，若各节点自发处理会造成任务同时处于多种恢复策略"的冲突，通过**统一汇总、统一判定**故障处理级别和策略来协调整个集群的处理行为。

3. **数据采集三路来源**：
   - 来自 **Ascend Device Plugin**：芯片信息；
   - 来自 **NodeD**：计算节点的 CPU、内存、硬盘健康状态、节点 DPC 共享存储故障、灵衢网络故障；
   - 来自 **ConfigMap 或 gRPC**：公共故障信息。

4. **数据上报与控制两条输出**：
   - 上报给 **Ascend-volcano-plugin**（资源汇总）；
   - 上报给 **CCAE**（任务状态与资源使用情况）；
   - 与训练容器内部建立连接，**控制训练进程执行重计算动作**；
   - 与带外服务交互传输任务信息。

5. **镜像 Tag 双规范**：
   - v26.1.0 起：`<版本>-<操作系统>`（如 `v26.1.0-ubuntu22.04`、`v26.1.0-openeuler24.03`），Dockerfile 拆分为 `Dockerfile.ubuntu` 与 `Dockerfile.openeuler`；
   - v26.0.0 及以前：仅 `<版本>`（如 `v26.0.0`），单一 `Dockerfile`，基础镜像仅 Ubuntu 22.04。

6. **构建依赖 BuildKit 与 `TARGETPLATFORM`**：v26.1.0+ 的 Dockerfile 使用 BuildKit 内置变量 `TARGETPLATFORM` 识别 `linux/amd64`、`linux/arm64`；Docker < 18.09 或未开启 BuildKit 的环境会失败，需 `export DOCKER_BUILDKIT=1` 临时启用。

---

## 【关键机制与数据】

### 工作原理（数据流，汇总自"组件功能"与"组件上下游依赖"两条原文）

- **采集（入向）**：ClusterD 监听/调用计算节点侧 Ascend Device Plugin → 芯片信息；调用 NodeD → CPU/内存/硬盘健康状态、DPC 共享存储故障、灵衢网络故障；读取 ConfigMap 或通过 gRPC → 公共故障信息。
- **聚合（中向）**：从任务、芯片、故障三个维度做统计分析，统一判定故障处理级别与策略。
- **下发/上报（出向）**：将集群资源汇总 → 上报 Ascend-volcano-plugin；将任务状态与资源使用 → 上报 CCAE；通过容器内连接 → 触发训练进程"重计算"；与带外服务 → 互传任务信息。

### 性能/规模数据（原文）

> 原文："硬件规格要求"

| 规模    | CPU | 内存  |
|-------|----|-----|
| 100 节点以内 | 1 核 | 1 GB |
| 500 节点   | 2 核 | 2 GB |
| 1000 节点  | 4 核 | 8 GB |

> 注：原文仅给出管理节点自身的资源需求，与具体吞吐/时延/QPS 等性能指标无关；文档未提供性能基准数据。

### 兼容性约束（原文）

> 原文："Kubernetes 1.17.x~1.34.x（推荐使用 1.19.x 及以上版本）"；Ascend Device Plugin 与 NodeD 均需与 ClusterD **同版本**对齐。

---

## 【表格解读】

### 表 1：Tag 规范（v26.1.0+）

> 原文：

| 字段     | 示例值           | 说明              |
|--------|---------------|-----------------|
| `版本`   | `v26.1.0`     | ClusterD 版本号    |
| `操作系统` | `ubuntu22.04` | ClusterD 镜像操作系统 |

**逐行解读**：
- `版本`（`v26.1.0`）：ClusterD 自身的语义化版本号，决定功能与 API 行为；
- `操作系统`（`ubuntu22.04`）：基础镜像操作系统，决定运行时的 glibc、系统库、systemd 行为。当前支持的 OS 取值见下一表，仅 `ubuntu22.04` 与 `openeuler24.03` 两种。

---

### 表 2：ClusterD 26.1.0 镜像与 Dockerfile

> 原文：

| Tag                      | Dockerfile                                                                                                               | 镜像内容                                    |
|--------------------------|--------------------------------------------------------------------------------------------------------------------------|-----------------------------------------|
| `v26.1.0-ubuntu22.04`    | [Dockerfile.ubuntu](https://gitcode.com/Ascend/mind-cluster/blob/master/docker/clusterd/v26.1.0/Dockerfile.ubuntu)       | ClusterD v26.1.0 (基础镜像 Ubuntu 22.04)    |
| `v26.1.0-openeuler24.03` | [Dockerfile.openeuler](https://gitcode.com/Ascend/mind-cluster/blob/master/docker/clusterd/v26.1.0/Dockerfile.openeuler) | ClusterD v26.1.0 (基础镜像 openEuler 24.03) |

**逐行解读**：
- `v26.1.0-ubuntu22.04`：面向 Ubuntu 22.04 宿主/集群环境，Dockerfile 路径 `docker/clusterd/v26.1.0/Dockerfile.ubuntu`；
- `v26.1.0-openeuler24.03`：面向 openEuler 24.03 宿主/集群环境，Dockerfile 路径 `docker/clusterd/v26.1.0/Dockerfile.openeuler`。两份 Dockerfile 对应同一 ClusterD 版本（26.1.0），仅基础镜像不同，体现自 v26.1.0 起"版本+OS"解耦的发布策略。

---

### 表 3：Tag 规范（v26.0.0 及以前）

> 原文：

| 字段   | 示例值       | 说明           |
|------|-----------|--------------|
| `版本` | `v26.0.0` | ClusterD 版本号 |

**逐行解读**：仅含 `版本` 一项，说明在 v26.0.0 及以前 Tag 语义仅为版本号，OS 维度未对外暴露（实际基础镜像固定为 Ubuntu 22.04，见下表）。

---

### 表 4：ClusterD 26.0.0 镜像与 Dockerfile

> 原文：

| Tag       | Dockerfile                                                                                             | 镜像内容                                 |
|-----------|--------------------------------------------------------------------------------------------------------|--------------------------------------|
| `v26.0.0` | [Dockerfile](https://gitcode.com/Ascend/mind-cluster/blob/v26.0.0/component/clusterd/build/Dockerfile) | ClusterD v26.0.0 (基础镜像 Ubuntu 22.04) |

**逐行解读**：v26.0.0 仅发布一个 Tag、单一 Dockerfile（位于 `component/clusterd/build/Dockerfile`，相对于新版路径 `docker/clusterd/...` 较旧），基础镜像固定为 Ubuntu 22.04；构建流程与新版不同（需先下载 release zip 包再构建，见"使用方法"）。

---

### 表 5：软件依赖

> 原文：

| 软件名称                 | 支持的版本                          | 安装位置 | 说明                                                               |
|----------------------|--------------------------------|------|------------------------------------------------------------------|
| Kubernetes           | 1.17.x~1.34.x（推荐使用1.19.x及以上版本） | 所有节点 | 了解 K8s 的使用请参见 [Kubernetes 文档](https://kubernetes.io/zh-cn/docs/) |
| Ascend Device Plugin | 与 ClusterD 同版本                 | 计算节点 | ClusterD 依赖 Ascend Device Plugin 上报芯片信息                          |
| NodeD                | 与 ClusterD 同版本                 | 计算节点 | ClusterD 依赖 NodeD 上报节点故障信息                                       |

**逐行解读**：
- **Kubernetes**：版本范围 1.17.x–1.34.x（推荐 ≥ 1.19.x），覆盖全部节点；这是 ClusterD 运行的承载平台，决定其以 Pod/Deployment 形态部署并通过 API 与集群交互；
- **Ascend Device Plugin**：必须与 ClusterD **同版本**，部署在**计算节点**，负责上报芯片信息，构成 ClusterD 任务/芯片维度的数据源；
- **NodeD**：必须与 ClusterD **同版本**，同样部署在**计算节点**，负责上报节点健康状态与网络故障，构成 ClusterD 节点/故障维度的数据源。**版本号强一致**是关键约束，混版本会导致接口/数据格式不匹配。

---

### 表 6：硬件规格要求（管理节点）

> 原文：

| 名称  | 100节点以内 | 500节点 | 1000节点 |
|-----|---------|-------|--------|
| CPU | 1核      | 2核    | 4核     |
| 内存  | 1GB     | 2GB   | 8GB    |

**逐行解读**：这是**管理节点**自身（不是计算节点）的最低规格随集群规模线性增长的经验值：
- 100 节点以内：1 核 / 1 GB；
- 500 节点：2 核 / 2 GB；
- 1000 节点：4 核 / 8 GB。
增长曲线**非线性**——节点数扩大 10 倍（100→1000）时，CPU 仅扩 4 倍，内存扩 8 倍，反映出管理面聚合操作（汇总、上报）在更大规模下的内存开销增长更显著；文档未给出 1000 节点以上的规格建议。

---

## 【公式解读】

原文无公式。

---

## 【关联】

ClusterD 在 MindCluster 集群调度体系中处于"**管理面核心**"位置，文档显式给出以下关联关系：

- **上游数据来源**（ClusterD 从中读取）：
  - **Ascend Device Plugin**（计算节点）→ 提供芯片信息，构成"芯片维度"；
  - **NodeD**（计算节点）→ 提供 CPU/内存/硬盘健康状态、DPC 共享存储故障、灵衢网络故障，构成"节点/故障维度"；
  - **ConfigMap 或 gRPC** → 提供公共故障信息；
  - **训练容器内部进程** → 通过容器内连接接受 ClusterD 触发的"重计算"动作。

- **下游消费方**（ClusterD 将聚合结果上报给）：
  - **Ascend-volcano-plugin** → 消费集群资源汇总；
  - **CCAE**（Cloud Center AI Engine，云端 AI 引擎）→ 消费任务状态与资源使用情况；
  - **带外服务** → 任务信息交互。

- **横向关系**：
  - 与 **NodeD**、**Ascend Device Plugin** **必须保持同版本**，三者是 MindCluster 在"集群调度"域的协同组件；
  - 与 **Ascend-volcano-plugin**、**CCAE** 通过 K8s/集群调度上层 API 解耦，是数据消费方而非强版本绑定。

- **文档链**：本文档为中文版，对应英文版 `./OVERVIEW.md`（已在内部链接中标注）；版本相关的 Dockerfile 链接全部锚定在 `Ascend/mind-cluster` 仓库的 `master` 或带版本号 tag 的分支（如 `v26.0.0`）；硬件支持范围另见 `docs/zh/scheduling/01_introduction/03_supported_product_models_and_os.md`。

---

## 【使用方法】

> 以下命令/配置均出自原文。

### 1. 在线获取镜像

```bash
docker pull swr.cn-south-1.myhuaweicloud.com/ascendhub/clusterd:{tag}
docker tag swr.cn-south-1.myhuaweicloud.com/ascendhub/clusterd:{tag} clusterd:{tag}
```

### 2. 本地构建（可选）

**v26.1.0+ 流程**（示例：linux-aarch64、v26.1.0、Ubuntu 22.04）：

```bash
docker build --no-cache -t clusterd:v26.1.0 ./ -f Dockerfile.ubuntu
export DOCKER_BUILDKIT=1   # 旧版 Docker 或未启用 BuildKit 时必须
```

**v26.0.0 及更早流程**：

```bash
wget https://gitcode.com/Ascend/mind-cluster/releases/download/v26.0.0/Ascend-mindxdl-clusterd_26.0.0_linux-aarch64.zip
unzip Ascend-mindxdl-clusterd_26.0.0_linux-aarch64.zip -d Ascend-mindxdl-clusterd_26.0.0_linux-aarch64
cd Ascend-mindxdl-clusterd_26.0.0_linux-aarch64
docker build --no-cache -t clusterd:v26.0.0 ./ -f Dockerfile
```

### 3. 部署

将 YAML 文件内的 `{tag}` 替换为实际版本号后：

```bash
kubectl apply -f clusterd-{version}.yaml
kubectl get pods -A | grep clusterd   # 验证：Pod 状态应为 Running
```

### 4. 关键配置项/前置条件（原文）

- Kubernetes：1.17.x~1.34.x（推荐 ≥ 1.19.x）；
- Ascend Device Plugin / NodeD：与 ClusterD **同版本**；
- 管理节点硬件（按集群规模）：100 / 500 / 1000 节点分别对应 1 核·1 GB / 2 核·2 GB / 4 核·8 GB。

> 原文未涉及具体的 ConfigMap 字段、YAML 中 ClusterD 参数（如上报间隔、判定阈值等）以及环境变量配置方式；如需了解请进一步查阅仓库内具体 YAML 与代码。
