# K8s RDMA 共享设备插件

> 仓 `mind-cluster` · 路径 `docker/k8s-rdma-shared-dev-plugin/OVERVIEW.zh.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mind-cluster/docker/k8s-rdma-shared-dev-plugin/OVERVIEW.zh.md

# K8s RDMA 共享设备插件 · 一体化深度解读

## 【定位】

这篇文档解决"如何在 Kubernetes 集群中以共享方式把 RDMA 设备暴露给多个容器使用"的问题，描述 K8s RDMA 共享设备插件的能力边界、构建/部署流程、配置参数与硬件支持范围。

---

## 【技术要点】

1. **设备共享语义**：插件将节点上的 RDMA 设备以**共享方式**注册到 kubelet 设备插件框架，多个容器可并发使用同一 RDMA 设备，面向分布式训练与高性能计算负载。
2. **多维度设备筛选**：通过 `selectors` 支持按 **总线类型（buses，含 `ub`）/ 供应商 ID（vendors）/ 设备 ID（deviceIDs）/ 驱动程序（drivers）/ 接口名称（ifNames）/ 链路类型（linkTypes）** 六类条件过滤设备。
3. **周期性故障检测**：默认 `faultDetectPeriod=5` 秒（最小 1 秒）执行周期性故障检测；检测结果以 **ConfigMap** 形式写入 Kubernetes。
4. **CDI 支持**：插件支持 **Container Device Interface（容器设备接口）**，使容器能够以标准化的方式感知设备。
5. **资源命名约定**：`resourceName` 默认 `rdma`、`resourcePrefix` 默认 `huawei.com`，最终上报给 Kubernetes 的资源标识遵循该前缀拼接规则。
6. **构建与部署约束**：镜像标签格式 `<版本>-<操作系统>`（如 `v26.1.0-ubuntu22.04`）；构建依赖 **Docker 18.09+ 且必须启用 BuildKit**，否则 `TARGETPLATFORM` 变量无法注入，镜像构建会失败。

---

## 【关键机制与数据】

- **上下游依赖链（原文，4 步）**：
  1. 检测计算节点上的 RDMA 设备，并执行周期性故障检测；
  2. 向 Kubernetes kubelet 设备插件框架注册；
  3. 向 Kubernetes 调度器报告设备可用性；
  4. 以 configMap 形式向 Kubernetes 写入故障检测信息。

- **资源规模上限（原文）**：`rdmaHcaMax` 默认 **1000**，即单节点可被该插件管理的 RDMA HCA 设备数量上限默认 1000。

- **定期更新行为（原文）**：`periodicUpdateInterval` 默认 **0（禁用）**，即默认不主动定时上报设备变更；非 0 时以秒为单位周期性更新。

- **故障检测周期（原文）**：`faultDetectPeriod` 默认 **5 秒，最小值 1 秒**。

- **硬件资源占用（原文）**：CPU **0.1 核**、内存 **0.1 GB**。

- **镜像分发源（原文）**：`swr.cn-south-1.myhuaweicloud.com/ascendhub/k8s-rdma-shared-dev-plugin`，部署后通过 `kubectl apply -f` 的 DaemonSet 形式下发，验证命令为 `kubectl get pods -A | grep k8s-rdma-shared-dev-plugin`。

---

## 【表格解读】

### 表格 1：标签约定字段说明（原文逐字还原）

| 字段 | 示例值 | 说明 |
|---|---|---|
| `版本` | `v26.1.0` | K8s RDMA 共享设备插件组件版本号 |
| `操作系统` | `ubuntu22.04` | K8s RDMA 共享设备插件组件镜像操作系统 |

**逐行解读**：
- `版本` 示例 `v26.1.0` 是该组件当前章节锚定的版本号，标签第一段用于在镜像仓库中区分功能/接口差异。
- `操作系统` 示例 `ubuntu22.04` 表明镜像基座选型；该字段同时直接映射到下表 Dockerfile 类型（`Dockerfile.ubuntu` 或 `Dockerfile.openeuler`）。

### 表格 2：K8s RDMA 共享设备插件 26.1.0 镜像清单（原文逐字还原）

| Tag | Dockerfile | 镜像内容 |
|---|---|---|
| `v26.1.0-ubuntu22.04` | [Dockerfile.ubuntu](https://gitcode.com/Ascend/mind-cluster/blob/master/docker/k8s-rdma-shared-dev-plugin/v26.1.0/Dockerfile.ubuntu) | K8s RDMA 共享设备插件 v26.1.0 (基础镜像 Ubuntu 22.04) |
| `v26.1.0-openeuler24.03` | [Dockerfile.openeuler](https://gitcode.com/Ascend/mind-cluster/blob/master/docker/k8s-rdma-shared-dev-plugin/v26.1.0/Dockerfile.openeuler) | K8s RDMA 共享设备插件 v26.1.0 (基础镜像 openEuler 24.03) |

**逐行解读**：
- 两个 Tag 都归属于同一组件版本 `v26.1.0`，仅更换了基础操作系统；`ubuntu22.04` 对应 Debian 系用户，`openeuler24.03` 对应欧拉系用户，二者 Dockerfile 路径相互独立，分别承载不同发行版的包管理与依赖安装差异。

### 表格 3：软件依赖（原文逐字还原）

| 软件 | 支持版本 | 安装位置 | 描述 |
|---|---|---|---|
| Kubernetes | 1.17.x~1.34.x（建议 1.19.x 或更高版本） | 所有节点 | 参见 [Kubernetes 文档](https://kubernetes.io/docs/) |
| RDMA 驱动 | OFED 5.6 或更高版本 | 计算节点 | RDMA 设备驱动 |

**逐行解读**：
- Kubernetes 支持范围横跨 1.17.x 至 1.34.x，但官方推荐 **1.19.x 或更高**，原因是设备插件注册、CDI 等能力在更低版本上可能不可用。
- RDMA 驱动最低门槛为 **OFED 5.6**，且必须安装在**计算节点**（而非控制面），因为 RDMA 设备仅在计算节点上物理存在。

### 表格 4：硬件要求（原文逐字还原）

| 资源 | 要求 |
|---|---|
| CPU | 0.1 核 |
| 内存 | 0.1 GB |

**逐行解读**：
- 由于插件本质上只做"检测 + 注册 + 周期性故障检测"四件事，资源占用极小；`0.1 核 / 0.1 GB` 仅为最小量级预留，对节点不会造成可见压力。

### 表格 5：配置参数（原文逐字还原）

| 参数 | 类型 | 描述 | 默认值 |
|---|---|---|---|
| `periodicUpdateInterval` | int | 定期设备更新间隔（秒） | 0（禁用） |
| `faultDetectPeriod` | int | 定期故障检测间隔（秒） | 5（最小配置为1） |
| `configList` | array | 设备配置列表 | [] |
| `resourceName` | string | 设备插件的资源名称 | rdma |
| `resourcePrefix` | string | 资源前缀 | huawei.com |
| `rdmaHcaMax` | int | RDMA HCA 设备的最大数量 | 1000 |
| `devices` | array | 要包含的设备名称列表 | [] |
| `selectors.buses` | array | 用于过滤设备的总线类型（例如，"ub" 用于启用 UB 设备） | [] |
| `selectors.vendors` | array | 用于过滤设备的供应商 ID | [] |
| `selectors.deviceIDs` | array | 用于过滤设备的设备 ID | [] |
| `selectors.drivers` | array | 用于过滤设备的驱动程序名称 | [] |
| `selectors.ifNames` | array | 用于过滤设备的接口名称 | [] |
| `selectors.linkTypes` | array | 用于过滤设备的链路类型 | [] |

**逐行解读**：
- **`periodicUpdateInterval`**：控制插件主动重新扫描节点 RDMA 拓扑的频率，默认 0 表示"按事件触发"，避免不必要的资源开销；非 0 时按秒轮询。
- **`faultDetectPeriod`**：故障检测心跳周期，**最小 1 秒**，默认 5 秒，权衡了检测灵敏度与 CPU 占用。
- **`configList` / `devices`**：均为数组，前者是**结构化设备配置列表**（通常包含 RDMA HCA 的更细粒度配置），后者是**白名单设备名称列表**。
- **`resourceName` / `resourcePrefix`**：共同决定上报到 Kubernetes 的 extended resource 名称，默认组合下 Pod 中可申请 `huawei.com/rdma`。
- **`rdmaHcaMax`**：防御性上限，防止异常环境下枚举到过多伪设备导致 API 注册阻塞。
- **`selectors.*`**：六维度筛选器按 **AND** 语义叠加；其中 `buses` 数组若传入 `"ub"`，可显式启用 UB（Unified Buffer / 用户态缓冲区）类型设备，这与"功能特性"中的"支持 UB 设备故障检测"相互呼应。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **英文版镜像**：[./OVERVIEW.md](./OVERVIEW.md) —— 本文档的中文镜像版本，结构与字段一致。
- **同仓组件（MindCluster 仓库内）**：
  - Dockerfile 源：[v26.1.0/Dockerfile.ubuntu](https://gitcode.com/Ascend/mind-cluster/blob/master/docker/k8s-rdma-shared-dev-plugin/v26.1.0/Dockerfile.ubuntu)
  - Dockerfile 源：[v26.1.0/Dockerfile.openeuler](https://gitcode.com/Ascend/mind-cluster/blob/master/docker/k8s-rdma-shared-dev-plugin/v26.1.0/Dockerfile.openeuler)
- **外部依赖（上游）**：
  - **Kubernetes kubelet 设备插件框架**：插件通过其注册与上报扩展资源，二者强耦合。
  - **Kubernetes 调度器**：消费 `resourceName/resourcePrefix` 上报的扩展资源做调度决策。
  - **OFED 5.6+ 驱动**：在计算节点上暴露 RDMA 设备给用户态。
- **同仓调度组件（下游/并行）**：
  - [MindCluster 昇腾社区调度介绍](https://www.hiascend.com/document/detail/zh/mindcluster/latest/clustersched/dlug/docs/zh/scheduling/01_introduction/00_overview.md) —— 描述该 RDMA 共享设备插件在 MindCluster 整体调度链路中的位置。
- **问题反馈渠道**：[Issue Tracker](https://gitcode.com/Ascend/mind-cluster/issues) —— 任何部署/运行异常均可在此追溯。
- **硬件分类关联**：文档"支持的硬件"为 **PCI 和 UB 类型的 DPU 网卡**，这与 `selectors.buses` 中 `"ub"` 取值相对应，UB 是该插件区分于通用 RDMA 插件的关键能力。

---

## 【使用方法】

### 1. 构建镜像（原文给出）

```bash
docker build --no-cache -t k8s-rdma-shared-dev-plugin:v26.1.0 ./ -f Dockerfile.ubuntu
```

> 构建前若 Docker < 18.09 或 BuildKit 未启用，必须先执行：
> ```bash
> export DOCKER_BUILDKIT=1
> ```

### 2. 部署插件（原文给出 5 步）

```bash
# ① 拉取镜像
docker pull swr.cn-south-1.myhuaweicloud.com/ascendhub/k8s-rdma-shared-dev-plugin:{tag}

# ② 重新打标签
docker tag swr.cn-south-1.myhuaweicloud.com/ascendhub/k8s-rdma-shared-dev-plugin:{tag} k8s-rdma-shared-dev-plugin:{version}

# ③ 创建 ConfigMap（按配置说明构造设备插件配置）

# ④ 以 DaemonSet 形式部署
kubectl apply -f k8s-rdma-shared-dev-plugin-{version}.yaml

# ⑤ 验证
kubectl get pods -A | grep k8s-rdma-shared-dev-plugin
```

### 3. 关键配置项（原文给出，可直接写入 ConfigMap）

- **启用故障检测**：设置 `faultDetectPeriod=5`（或更小，最小 1）。
- **上报资源名**：默认 `resourceName=rdma`、`resourcePrefix=huawei.com`，Pod 侧可申请 `huawei.com/rdma`。
- **启用 UB 设备**：在 `selectors.buses` 中加入 `"ub"`，并确保硬件为 UB 类型 DPU 网卡。
- **多维筛选组合**：`selectors.vendors / deviceIDs / drivers / ifNames / linkTypes` 任一非空即生效，多个键按 AND 关系叠加。
- **设备规模控制**：`rdmaHcaMax`（默认 1000）按节点实际物理 HCA 数量调整。

### 4. 启用前提（原文给出）

- Kubernetes **1.17.x ~ 1.34.x**（建议 1.19.x+）；
- 计算节点预装 **OFED 5.6+** RDMA 驱动；
- 节点上具备 **PCI 或 UB 类型 DPU 网卡**。
