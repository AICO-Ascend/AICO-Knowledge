# Cluster Scheduling Component Infer Operator

> 仓 `mind-cluster` · 路径 `docker/infer-operator/OVERVIEW.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mind-cluster/docker/infer-operator/OVERVIEW.md

# 深度解读：MindCluster Infer Operator Overview

## 【定位】

这篇文档描述 MindCluster 集群调度组件之一的 **Infer Operator**——一个部署在管理节点上的 Kubernetes Operator，用于基于推理服务实例配置来下发和管理多角色协作的推理任务，并通过对 InferServiceSet / InferService / InstanceSet 三类 CRD 的控制器实现状态调和（reconcile）与手动扩缩容。

---

## 【技术要点】

1. **三大 CRD 模型**：Infer Operator 定义了 `InferServiceSet`、`InferService`、`InstanceSet` 三种 CRD，并由对应控制器 reconcile 各资源的实例状态。
2. **核心能力**：创建推理实例的 Workload 与 Service；支持对推理实例进行**手动扩缩容**（manual scaling）。
3. **资源调度链路（依赖顺序）**：用户 YAML → Workload Controller 创建 Pods → **Volcano** 执行最终资源选择 → 若请求 NPU 卡，则 **Atlas Device Plugin** 获取 NPU 信息并完成挂载。
4. **镜像标签协议（v26.1.0 起）**：`<version>-<os>`，例：`v26.1.0-ubuntu22.04`、`v26.1.0-openeuler24.03`；v26.0.0 及之前仅用 `<version>`（如 `v26.0.0`）。
5. **官方镜像拉取与重标签**：从 `swr.cn-south-1.myhuaweicloud.com/ascendhub/infer-operator:{tag}` 拉取后用 `docker tag` 重命名为本地 `infer-operator:{tag}`。
6. **本地构建强约束**：v26.1.0+ 使用 Docker BuildKit，因 `TARGETPLATFORM` 只在 BuildKit 启用后才会被注入；Docker < 18.09 或未启用 BuildKit 会导致构建失败，可通过 `export DOCKER_BUILDKIT=1` 临时启用。

---

## 【关键机制与数据】

- **工作原理（原文：Upstream and Downstream Dependencies）**：
  1. 根据用户配置的 job YAML 创建推理实例 Workload；
  2. Workload Controller 创建 Pod 后，由 **Volcano** 做最终资源调度；
  3. 若 Workload 请求 NPU 卡，**Atlas Device Plugin** 提供 NPU 信息并完成设备挂载。

- **部署位置（原文）**：Infer Operator 部署在 **management nodes（管理节点）**；**Compute nodes（计算节点）** 上运行 Atlas Device Plugin。

- **硬件最低要求（原文表格）**：CPU 2 cores、Memory 2 GB。

- **支持的 Kubernetes 版本（原文）**：1.17.x ~ 1.34.x，**推荐 1.19.x 或更高**。

- **依赖版本对应关系（原文）**：Atlas Device Plugin **必须与 Infer Operator 同版本**；Volcano 需参考其官方与 Kubernetes 的兼容矩阵。

- **部署验证命令（原文）**：`kubectl get pods -A | grep infer-operator`，期望结果为 infer-operator 相关的 Pod 处于 Running 状态。

> 原文未提供性能数据（如吞吐、时延、QPS 等指标）。

---

## 【表格解读】

以下根据原文逐字还原关键表格并逐行解读。

### 表 1：Tag Convention（v26.1.0 起）

| Field     | Example       | Description                                |
|-----------|---------------|--------------------------------------------|
| `version` | `v26.1.0`     | Version Number of Infer Operator           |
| `os`      | `ubuntu22.04` | Operating System for Infer Operator Images |

**解读**：自 v26.1.0 起，镜像 tag 拆分为版本号与操作系统两段，便于多 OS 同版本并行发布。`version` 描述 Infer Operator 自身版本；`os` 指镜像基础操作系统（如 Ubuntu 22.04）。

---

### 表 2：Infer Operator 26.1.0 镜像清单

| Tag                      | Dockerfile                                                                                                                     | Image Content                                        |
|--------------------------|--------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------|
| `v26.1.0-ubuntu22.04`    | [Dockerfile.ubuntu](https://gitcode.com/Ascend/mind-cluster/blob/master/docker/infer-operator/v26.1.0/Dockerfile.ubuntu)       | Infer Operator v26.1.0 (Base Image: Ubuntu 22.04)    |
| `v26.1.0-openeuler24.03` | [Dockerfile.openeuler](https://gitcode.com/Ascend/mind-cluster/blob/master/docker/infer-operator/v26.1.0/Dockerfile.openeuler) | Infer Operator v26.1.0 (Base Image: openEuler 24.03) |

**解读**：同一 v26.1.0 版本提供 Ubuntu 22.04 与 openEuler 24.03 两个底包路径，Dockerfile 分别命名 `Dockerfile.ubuntu` / `Dockerfile.openeuler`，并存放在 `docker/infer-operator/v26.1.0/` 目录下，便于按宿主机 OS 选择对应构建文件。

---

### 表 3：Tag Convention（v26.0.0 及之前）

| Field     | Example   | Description                      |
|-----------|-----------|----------------------------------|
| `version` | `v26.0.0` | Version Number of Infer Operator |

**解读**：旧版镜像 tag 只有 `version` 单一字段，无 OS 区分。

---

### 表 4：Infer Operator 26.0.0 镜像清单

| Tag       | Dockerfile                                                                                                   | Image Content                                     |
|-----------|--------------------------------------------------------------------------------------------------------------|---------------------------------------------------|
| `v26.0.0` | [Dockerfile](https://gitcode.com/Ascend/mind-cluster/blob/v26.0.0/component/infer-operator/build/Dockerfile) | Infer Operator v26.0.0 (Base Image: Ubuntu 22.04) |

**解读**：v26.0.0 仅打包 Ubuntu 22.04 底包；Dockerfile 路径位于 `component/infer-operator/build/Dockerfile`，与新版 `docker/infer-operator/<version>/` 路径结构不同。

---

### 表 5：Software Dependencies（软件依赖）

| Software            | Supported Versions                                                                                                           | Installation Location | Description                                                 |
|---------------------|------------------------------------------------------------------------------------------------------------------------------|-----------------------|-------------------------------------------------------------|
| Kubernetes          | 1.17.x~1.34.x (1.19.x or later recommended)                                                                                  | All nodes             | See [Kubernetes Documentation](https://kubernetes.io/docs/) |
| Volcano             | See [Volcano Kubernetes compatibility](https://github.com/volcano-sh/volcano/blob/master/README.md#kubernetes-compatibility) | Management nodes      | Infer Operator depends on Volcano for resource scheduling   |
| Atlas Device Plugin | Same version as Infer Operator                                                                                               | Compute nodes         | Required when inference jobs use NPU resources              |

**解读**：
- **Kubernetes**：全部节点安装，覆盖 1.17.x–1.34.x 区间，1.19.x 起为推荐版本，表明 Infer Operator 兼容较宽的 K8s 版本范围但推荐使用较新版本。
- **Volcano**：仅管理节点安装，版本选择参考 Volcano 官方 K8s 兼容矩阵；其职责是 Infer Operator 创建 Pod 后的最终资源调度。
- **Atlas Device Plugin**：仅计算节点安装，**版本必须与 Infer Operator 严格对齐**；这是 NPU 设备供给的强耦合依赖。

---

### 表 6：Hardware Requirements（硬件最低要求）

| Resource | Requirement |
|----------|-------------|
| CPU      | 2 cores     |
| Memory   | 2 GB        |

**解读**：列出 Infer Operator 自身运行所需的最低硬件阈值（管理节点视角的最低规格），2 cores / 2 GB 表明组件本体较轻量，重负载在下游 Pod 与 NPU。

---

## 【公式解读】

原文无公式（无 LaTeX 数学式或伪代码公式）。

---

## 【关联】

- **CRD 之间的关系**：InferServiceSet、InferService、InstanceSet 三类 CRD 共同构成推理服务建模：InstanceSet 应对应实际的实例规格集合，InferService 描述推理服务，InferServiceSet 聚合多个 InferService 用于多角色协作；三者由 Infer Operator 中对应的 controllers 来 reconcile 状态。
- **上游 / 下游依赖链**（原文 Upstream and Downstream Dependencies 节）：
  - **上游**：用户配置的 job YAML——决定 Workload 的目标规格。
  - **下游（K8s 体系内）**：Workload Controller → Volcano 调度 → Atlas Device Plugin NPU 挂载。
- **横向组件关系**：Infer Operator 与 Volcano、Atlas Device Plugin 共同构成 MindCluster 推理调度栈，其中 Infer Operator 负责"声明 & 创建"，Volcano 负责"调度决策"，Atlas Device Plugin 负责"设备供给"。
- **镜像/构建依赖**：容器镜像 tag 由版本号与 OS 共同决定；v26.1.0+ 必须启用 Docker BuildKit 才能解析 `TARGETPLATFORM`。
- **文档内部链接**：文末提供 `./OVERVIEW.zh.md`（中文版）作为同源姊妹文档，内容与本篇对齐。
- **生态外链**：社区帮助指向 MindCluster Atlas Community 文档与 Issue Tracker；许可信息另见 HiAscend 软许可页。

---

## 【使用方法】

### 1. 拉取官方镜像（原文命令）

```bash
docker pull swr.cn-south-1.myhuaweicloud.com/ascendhub/infer-operator:{tag}
docker tag swr.cn-south-1.myhuaweicloud.com/ascendhub/infer-operator:{tag} infer-operator:{tag}
```

### 2. 本地构建

**v26.1.0+**（原文命令示例：linux-aarch64 + Ubuntu 22.04）：

```bash
export DOCKER_BUILDKIT=1   # 必须，否则 TARGETPLATFORM 无法读取
docker build --no-cache -t infer-operator:v26.1.0 ./ -f Dockerfile.ubuntu
```

**v26.0.0 及之前**（原文命令示例：linux-aarch64 + Ubuntu 22.04）：

```bash
wget https://gitcode.com/Ascend/mind-cluster/releases/download/v26.0.0/Ascend-mindxdl-infer-operator_26.0.0_linux-aarch64.zip
unzip Ascend-mindxdl-infer-operator_26.0.0_linux-aarch64.zip -d Ascend-mindxdl-infer-operator_26.0.0_linux-aarch64
cd Ascend-mindxdl-infer-operator_26.0.0_linux-aarch64
docker build --no-cache -t infer-operator:v26.0.0 ./ -f Dockerfile
```

### 3. 部署与验证（原文命令）

```bash
kubectl apply -f infer-operator-{version}.yaml
kubectl get pods -A | grep infer-operator   # 期望 infer-operator 相关 Pod 处于 Running
```

### 4. 关键配置/约束（原文中明确给出的）

- **Kubernetes 版本区间**：1.17.x ~ 1.34.x（推荐 1.19.x+）。
- **Atlas Device Plugin 版本**：与 Infer Operator **同版本**。
- **Volcano 安装位置**：管理节点；版本需见 Volcano K8s 兼容矩阵。
- **硬件最低**：CPU 2 cores / Memory 2 GB。
- **前置条件（Prerequisites）在原文中标记为 Optional**，即非强制，意味着上述依赖也可由外部已完成的环境复用。
