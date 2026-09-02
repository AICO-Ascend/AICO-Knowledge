# 集群调度组件 Infer Operator

> 仓 `mind-cluster` · 路径 `docker/infer-operator/OVERVIEW.zh.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mind-cluster/docker/infer-operator/OVERVIEW.zh.md

# 「mind-cluster / docker/infer-operator / OVERVIEW.zh.md」深度解读

---

## 【定位】

本文档是 MindCluster 集群调度组件 **Infer Operator** 的中文总览，介绍其作为部署在管理节点上的 Kubernetes Operator，如何通过三种 CRD（InferServiceSet/InferService/InstanceSet）声明并管理多角色协作的推理任务，同时给出镜像 Tag 规范、版本兼容矩阵、软硬件前置要求、镜像拉取/本地构建与 `kubectl apply` 部署流程，作为用户使用该组件的入门级参考资料。

---

## 【技术要点】

1. **组件定位**：Infer Operator 部署在**管理节点**上，本质是一个 Kubernetes Operator，用于"部署和管理多角色合作的推理任务"。
2. **三种 CRD 与控制器**：定义了 **InferServiceSet、InferService、InstanceSet** 三种 CRD，并为每种资源实现了对应的控制器进行状态调谐。
3. **核心能力**：① 创建推理实例 Workload 与 Service；② 推理实例的手动扩缩容（原文：*"推理实例的手动扩缩容"*）。
4. **上游/下游依赖链路（3 步）**：
   - ① 基于用户配置的任务 YAML 创建推理实例 Workload；
   - ② Workload Controller 创建 Pod 后，由 **Volcano** 进行资源的最终选定；
   - ③ 若 Workload 申请占用 **NPU 卡**，由 **Ascend Device Plugin** 获取 NPU 信息并完成设备挂载。
5. **Tag 规范**：自 **v26.1.0** 起 Tag 格式为 `<版本>-<操作系统>`（例如 `v26.1.0-ubuntu22.04`）；**v26.0.0 及以前**为 `<版本>` 单段格式（例如 `v26.0.0`）。
6. **软件版本兼容**：Kubernetes **1.17.x ~ 1.34.x**（**推荐 1.19.x 及以上**）；Volcano 需与 K8s 版本配套；Ascend Device Plugin 需与 Infer Operator **同版本**。

---

## 【关键机制与数据】

### 工作原理 / 数据流（原文："组件上下游依赖"）

原文以三步描述 Infer Operator 的请求下发与设备绑定流程：

1. **YAML → Workload**：用户提交的任务 YAML（包含推理服务的实例配置）经由 Infer Operator 翻译为底层推理实例 **Workload**。
2. **Workload Controller → Pod → Volcano 调度**：Workload Controller 创建 Pod 后，**Volcano**（集群调度器）介入并完成资源最终选定——即 Infer Operator 仅负责资源建模，**真正的资源调度由 Volcano 完成**。
3. **NPU 资源绑定**：若该 Workload 声明占用 NPU，则 **Ascend Device Plugin** 介入，获取 NPU 信息并将设备挂载到 Pod 上。

> 注：原文未给出具体的性能数据（如 QPS、时延、并发上限等），本节亦无性能数字可摘。

### 镜像 Tag 与版本数据（原文：Tag 规范章节）

- 当前主推版本：**v26.1.0**，支持两种基础镜像 OS：**Ubuntu 22.04** 与 **openEuler 24.03**。
- 历史版本：**v26.0.0**，仅单一基础镜像（Ubuntu 22.04）。

---

## 【表格解读】

原文共包含 6 张表格，逐字还原如下。

### 表 1：v26.1.0+ Tag 字段说明

| 字段     | 示例值           | 说明                    |
|--------|---------------|-----------------------|
| `版本`   | `v26.1.0`     | Infer Operator 版本号    |
| `操作系统` | `ubuntu22.04` | Infer Operator 镜像操作系统 |

**解读**：自 v26.1.0 起，镜像 Tag 从单一版本号扩展为"版本-操作系统"双段，目的是在同一组件下分发面向不同 OS 用户的镜像（Ubuntu vs openEuler）。原文中示例值 `ubuntu22.04` 即 Ubuntu 22.04 LTS，是 LTS 长期支持版本。

---

### 表 2：Infer Operator 26.1.0 支持的镜像与 Dockerfile

| Tag                      | Dockerfile                                                                                                                     | 镜像内容                                          |
|--------------------------|--------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------|
| `v26.1.0-ubuntu22.04`    | [Dockerfile.ubuntu](https://gitcode.com/Ascend/mind-cluster/blob/master/docker/infer-operator/v26.1.0/Dockerfile.ubuntu)       | Infer Operator v26.1.0 (基础镜像 Ubuntu 22.04)    |
| `v26.1.0-openeuler24.03` | [Dockerfile.openeuler](https://gitcode.com/Ascend/mind-cluster/blob/master/docker/infer-operator/v26.1.0/Dockerfile.openeuler) | Infer Operator v26.1.0 (基础镜像 openEuler 24.03) |

**解读**：同一组件版本（v26.1.0）通过两个 Dockerfile 文件分别面向 Ubuntu 22.04 与 openEuler 24.03（openEuler 是华为开源的服务器操作系统）两个生态。两个 Dockerfile 路径分别挂载在仓库的 `docker/infer-operator/v26.1.0/` 目录下，结构清晰。

---

### 表 3：v26.0.0 及以前 Tag 字段说明

| 字段   | 示例值       | 说明                 |
|------|-----------|--------------------|
| `版本` | `v26.0.0` | Infer Operator组件版本 |

**解读**：旧版 Tag 仅含版本号一项，原因是当时只有一个 OS 变体（Ubuntu 22.04）。该格式在 v26.0.0 及之前一直沿用，自 v26.1.0 起被双段格式取代。

---

### 表 4：Infer Operator 26.0.0 镜像与 Dockerfile

| Tag       | Dockerfile                                                                                                   | 镜像内容                                       |
|-----------|--------------------------------------------------------------------------------------------------------------|--------------------------------------------|
| `v26.0.0` | [Dockerfile](https://gitcode.com/Ascend/mind-cluster/blob/v26.0.0/component/infer-operator/build/Dockerfile) | Infer Operator v26.0.0 (基础镜像 Ubuntu 22.04) |

**解读**：v26.0.0 的 Dockerfile 路径位于 `component/infer-operator/build/Dockerfile`（即旧版本仓内组件布局），与 v26.1.0 之后迁移到 `docker/infer-operator/` 的新布局不同，反映了仓库结构的演进。

---

### 表 5：软件依赖

| 软件名称                 | 支持的版本                                                                                                                    | 安装位置 | 说明                                                               |
|----------------------|--------------------------------------------------------------------------------------------------------------------------|------|------------------------------------------------------------------|
| Kubernetes           | 1.17.x~1.34.x（推荐使用1.19.x及以上版本）                                                                                           | 所有节点 | 了解 K8s 的使用请参见 [Kubernetes 文档](https://kubernetes.io/zh-cn/docs/) |
| Volcano              | 请参见 [Volcano 官网中对应的 Kubernetes 版本](https://github.com/volcano-sh/volcano/blob/master/README.md#kubernetes-compatibility) | 管理节点 | Infer Operator 依赖 Volcano 进行资源调度                                 |
| Ascend Device Plugin | 与 Infer Operator 同版本                                                                                                     | 计算节点 | 推理任务占用 NPU 时需要                                                   |

**解读**：表格揭示了三层依赖关系——
- **Kubernetes** 是底座，版本范围很宽（1.17→1.34），最低门槛低（1.17.x），但**官方推荐 1.19.x 及以上**，原因是 1.19 之后部分 CRD/Operator SDK API 行为更稳定；
- **Volcano** 负责 Pod 调度，与 K8s 版本必须配套（链接到 Volcano 官方兼容性矩阵）；
- **Ascend Device Plugin** 必须与 Infer Operator 同版本——这是为了避免 NPU 设备发现协议不一致导致 Workload 卡在调度阶段。

---

### 表 6：硬件规格要求

| 名称  | 要求  |
|-----|-----|
| CPU | 2核  |
| 内存  | 2GB |

**解读**：这是 Infer Operator 自身运行所需的最小硬件资源（**管理节点**），2 核 / 2 GB 表明它非常轻量——这符合 Operator 仅做"资源建模与控制循环"的设计，不需要承担计算负载。实际推理压力由计算节点承担。

---

## 【公式解读】

**原文无公式**。

---

## 【关联】

- **仓库层**：文档由 **MindCluster 代码仓**（https://gitcode.com/Ascend/mind-cluster ）统一维护，自身位于 `docker/infer-operator/OVERVIEW.zh.md`。其与英文版 `./OVERVIEW.md` 形成中英双语对照（文末提供内部链接 `./OVERVIEW.md`）。
- **同仓其他组件**：
  - **Volcano**：Infer Operator 的下游依赖，负责最终 Pod 资源调度；与本文档在同一集群调度域内协同。
  - **Ascend Device Plugin**：与 Infer Operator **同版本配套**，负责 NPU 设备的发现与挂载，是推理任务得以落到 NPU 上的关键桥梁。
- **文档/社区入口**：
  - 昇腾社区的《MindCluster 集群调度》总览（`https://www.hiascend.com/document/detail/zh/mindcluster/latest/clustersched/dlug/docs/zh/scheduling/01_introduction/00_overview.md`）；
  - 问题反馈通道（`https://gitcode.com/Ascend/mind-cluster/issues`）；
  - **支持的产品形态和 OS 清单**（`docs/zh/scheduling/01_introduction/03_supported_product_models_and_os.md`）由本文档"支持的硬件"小节直接链接，用于查询当前版本所适配的具体昇腾硬件型号。
- **许可证层**：文末链接至昇腾软件许可证总览（`https://www.hiascend.com/zh/legal/softlicense`），并提示容器内预装的 Python、系统库等还有各自的第三方许可。
- **版本演进方向**：v26.0.0 → v26.1.0 完成了 Tag 格式（单段→双段）、OS 支持（单一 Ubuntu → Ubuntu + openEuler）、仓库目录布局（`component/` → `docker/`）三方面的演进，本文是该演进后的对外说明。

---

## 【使用方法】

> 以下命令均**逐字摘自原文**。

### 1. 在线获取镜像

```bash
docker pull swr.cn-south-1.myhuaweicloud.com/ascendhub/infer-operator:{tag}
```

```bash
docker tag swr.cn-south-1.myhuaweicloud.com/ascendhub/infer-operator:{tag} infer-operator:{tag}
```

### 2. v26.1.0+ 本地构建（linux-aarch64 / Ubuntu 22.04 场景）

- 从 `docker/infer-operator/v26.1.0/Dockerfile.ubuntu` 取得 Dockerfile；
- 构建命令：

```bash
docker build --no-cache -t infer-operator:v26.1.0 ./ -f Dockerfile.ubuntu
```

- 若 Docker < 18.09 或未启用 BuildKit，需显式开启：

```bash
export DOCKER_BUILDKIT=1
```

（否则无法读取 `TARGETPLATFORM`（BuildKit 内置变量，用于识别 `linux/amd64`、`linux/arm64` 等目标平台）而导致构建失败。）

### 3. v26.0.0 及更早版本本地构建

```shell
wget https://gitcode.com/Ascend/mind-cluster/releases/download/v26.0.0/Ascend-mindxdl-infer-operator_26.0.0_linux-aarch64.zip
```

```shell
unzip Ascend-mindxdl-infer-operator_26.0.0_linux-aarch64.zip -d Ascend-mindxdl-infer-operator_26.0.0_linux-aarch64
```

```shell
cd Ascend-mindxdl-infer-operator_26.0.0_linux-aarch64
```

```bash
docker build --no-cache -t infer-operator:v26.0.0 ./ -f Dockerfile
```

### 4. 部署

```bash
kubectl apply -f infer-operator-{version}.yaml
```

> 需将 yaml 文件中镜像字段的 `{tag}` 替换为实际版本号。

### 5. 验证部署

```bash
kubectl get pods -A | grep infer-operator
```

预期结果：对应命名空间下的 infer-operator Pod 状态为 **Running**。

### 6. 启用前置条件（汇总自原文"前置要求"小节）

- **软件**：Kubernetes 1.17.x~1.34.x（推荐 ≥1.19.x）；Volcano（与 K8s 版本配套）；Ascend Device Plugin（与 Infer Operator 同版本）。
- **硬件**：管理节点 ≥ 2 核 CPU、≥ 2 GB 内存。
- **运行时依赖**：必须在 Kubernetes 集群内**已部署 Volcano 与 Ascend Device Plugin**，否则 Infer Operator 创建的 Workload 无法完成最终调度与 NPU 挂载。
