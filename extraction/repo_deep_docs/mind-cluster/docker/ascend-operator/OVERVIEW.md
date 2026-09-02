# Cluster Scheduling Component Atlas Operator

> 仓 `mind-cluster` · 路径 `docker/ascend-operator/OVERVIEW.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mind-cluster/docker/ascend-operator/OVERVIEW.md

# Atlas Operator Overview 深度解读

## 【定位】

这篇文档描述 **Atlas Operator** —— MindCluster 集群调度组件之一, 部署在 Kubernetes 管理节点上, 通过 CRD 机制定义 AscendJob 任务, 为基于 MindSpore/PyTorch 的分布式训练自动注入 collective communication 参数并生成/挂载 RankTable 文件, 从而让用户只需配置 YAML 即可在 Kubernetes 上完成分布式训练。

---

## 【技术要点】

1. **CRD 抽象层**: 通过 Custom Resource Definition 定义 AscendJob, 用户通过 YAML 配置即可触发分布式训练 (原文: "Through the CRD (Custom Resource Definition) mechanism, AscendJob tasks are defined, allowing users to easily implement distributed training by simply configuring YAML files.").
2. **环境变量注入**: 创建 Pod 时将 collective communication 参数作为环境变量写入容器, 内容包括 master 进程 IP、RankTable 信息、当前 Pod 的 rankId。
3. **RankTable 分发机制**: 创建 RankTable 文件后, 通过 **shared storage 或 ConfigMap** 两种方式挂载到容器, 原文明确指出该机制用于"optimizing collective communication link establishment performance"(优化集合通信链路建立性能)。
4. **资源调度两阶段协作**: 第一阶段由 Atlas Operator 透过 Volcano 感知资源是否满足; 第二阶段在 Pod 创建完成后由 Volcano 执行最终资源选择。
5. **设备信息聚合**: 从 Atlas Device Plugin 获取 chip ID、IP、rankId 三类信息, 聚合后生成 collective communication 文件再挂载。
6. **镜像标签演进**: 自 **v26.1.0** 起标签格式从 `<version>` 演变为 `<version>-<os>` (如 `v26.1.0-ubuntu22.04`、`v26.1.0-openeuler24.03`), 以支持多操作系统分发。

---

## 【关键机制与数据】

### 工作流(原文五步上下游依赖, 完整数据流链路)

| 步骤 | 执行主体 | 关键动作 |
|---|---|---|
| 1 | Atlas Operator → Volcano | 感知当前 Job 所需资源是否被满足 |
| 2 | Atlas Operator | 资源满足后创建对应 Pod, 并将 collective communication 参数以环境变量形式注入 |
| 3 | Volcano | Pod 创建后执行最终资源选择 (final resource selection) |
| 4 | Atlas Operator + Atlas Device Plugin | 从 Device Plugin 取得 chip ID、IP、rankId, 聚合后生成 collective communication 文件 |
| 5 | Atlas Operator | 通过 shared storage 或 ConfigMap 将 collective communication 文件挂载进容器 |

### 原文给出的关键数据/参数

- **Kubernetes 版本范围**: `1.17.x ~ 1.34.x`, 原文推荐 `1.19.x or later`。
- **Volcano 安装位置**: Management nodes (管理节点)。
- **硬件最低需求**: CPU `2 cores`, Memory `2.5 GB`。
- **镜像仓库地址**: `swr.cn-south-1.myhuaweicloud.com/ascendhub/ascend-operator:{tag}`。
- **本地构建示例架构**: `linux-aarch64`(v26.1.0 Ubuntu 22.04 / v26.0.0 Ubuntu 22.04)。
- **Docker BuildKit 兼容门槛**: "If your Docker version is earlier than 18.09 or BuildKit is not manually enabled, the TARGETPLATFORM variable cannot be read during image building, which will cause the image build to fail." —— 可通过 `export DOCKER_BUILDKIT=1` 临时启用。
- **TARGETPLATFORM 示例值**: `linux/amd64`, `linux/arm64`。
- **验证命令**: `kubectl get pods -A | grep ascend-operator`, 预期 "Running" 状态。

---

## 【表格解读】

### 表 1: v26.1.0+ 标签约定 (Tag Convention)

| Field | Example | Description |
|---|---|---|
| `version` | `v26.1.0` | Version Number of Atlas Operator |
| `os` | `ubuntu22.04` | Operating System for Atlas Operator Images |

**解读**: 标签由两段构成——版本号 + OS, 支持按操作系统分发镜像; `os` 字段示例仅列出 `ubuntu22.04`, 实际可用值需对照镜像表(见下)。

---

### 表 2: Atlas Operator 26.1.0 镜像清单

| Tag | Dockerfile | Image Content |
|---|---|---|
| `v26.1.0-ubuntu22.04` | [Dockerfile.ubuntu](https://gitcode.com/Ascend/mind-cluster/blob/master/docker/ascend-operator/v26.1.0/Dockerfile.ubuntu) | Atlas Operator v26.1.0 (Base Image: Ubuntu 22.04) |
| `v26.1.0-openeuler24.03` | [Dockerfile.openeuler](https://gitcode.com/Ascend/mind-cluster/blob/master/docker/ascend-operator/v26.1.0/Dockerfile.openeuler) | Atlas Operator v26.1.0 (Base Image: openEuler 24.03) |

**解读**: v26.1.0 同时提供 Ubuntu 22.04 与 openEuler 24.03 两个底座镜像, Dockerfile 路径独立, 仓库目录由旧版 `component/ascend-operator/build/` 迁移至 `docker/ascend-operator/v26.1.0/`, 体现容器化目录结构的重组。

---

### 表 3: v26.0.0 及之前标签约定

| Field | Example | Description |
|---|---|---|
| `version` | `v26.0.0` | Version Number of Atlas Operator |

**解读**: 旧版仅有版本号字段, 不区分 OS; 配套安装方式也不同(走 wget 下载 release zip 包而非 git 拉取 Dockerfile)。

---

### 表 4: Atlas Operator 26.0.0 镜像清单

| Tag | Dockerfile | Image Content |
|---|---|---|
| `v26.0.0` | [Dockerfile](https://gitcode.com/Ascend/mind-cluster/blob/v26.0.0/component/ascend-operator/build/Dockerfile) | Atlas Operator v26.0.0 (Ubuntu 22.04) |

**解读**: v26.0.0 单一镜像、单一 OS (Ubuntu 22.04), Dockerfile 仍位于旧路径 `component/ascend-operator/build/`。

---

### 表 5: 软件依赖 (Software Dependencies)

| Software | Supported Versions | Installation Location | Description |
|---|---|---|---|
| Kubernetes | 1.17.x~1.34.x (1.19.x or later recommended) | All nodes | See [Kubernetes Documentation](https://kubernetes.io/docs/) |
| Volcano | See [Volcano Kubernetes compatibility](https://github.com/volcano-sh/volcano/blob/master/README.md#kubernetes-compatibility) | Management nodes | Atlas Operator depends on Volcano for resource scheduling |

**解读**: Kubernetes 覆盖集群全节点, 范围跨度极大 (1.17~1.34, 17 个 minor 版本); Volcano 仅装在管理节点, 与 Atlas Operator 同层——印证工作流中两者紧密协作的关系。

---

### 表 6: 硬件需求 (Hardware Requirements)

| Resource | Requirement |
|---|---|
| CPU | 2 cores |
| Memory | 2.5 GB |

**解读**: 这是 Atlas Operator 自身的资源配额要求, 体量轻量 (管理面组件, 不参与训练计算); 训练实际所需的 NPU/显存资源不在此文档范围内。

---

## 【公式解读】

**原文无公式**。

---

## 【关联】

### 上下游模块关系(基于原文"Upstream and Downstream Dependencies")

- **上游调度器 — Volcano**: 负责 (a) 资源满足性判断、(b) Pod 创建后最终资源选择。Atlas Operator 不能脱离 Volcano 独立运行(原文表格中也注明"Atlas Operator depends on Volcano for resource scheduling")。
- **下游设备信息来源 — Atlas Device Plugin**: 提供 chip ID、IP、rankId 三类原始数据, Atlas Operator 仅做"聚合 + 生成 RankTable"。
- **下游消费者 — 训练 Pod (AscendJob)**: 通过 env vars 接收 collective communication 参数, 通过共享存储/ConfigMap 接收 RankTable 文件。
- **镜像分发渠道 — AscendHub**: 部署在 `swr.cn-south-1.myhuaweicloud.com` 区域仓库。

### 文档内/仓库内交叉链接

- `./OVERVIEW.zh.md` — 中文版 Overview(本文档的中文镜像)。
- `https://gitcode.com/Ascend/mind-cluster` — 仓库主页与 Issue Tracker。
- `https://www.hiascend.com/document/detail/zh/mindcluster/latest/clustersched/dlug/docs/zh/scheduling/01_introduction/00_overview.md` — MindCluster Atlas 社区文档(对应 MindCluster 整体的 Overview)。
- `https://gitcode.com/Ascend/mind-cluster/blob/master/docs/zh/scheduling/01_introduction/03_supported_product_models_and_os.md` — Atlas 硬件形态与 OS 兼容性清单(Supported Hardware 一节跳转目标)。
- `https://github.com/volcano-sh/volcano/blob/master/README.md#kubernetes-compatibility` — Volcano 与 Kubernetes 版本兼容矩阵。
- `https://www.hiascend.com/en/legal/softlicense` — Mind 系列软件许可证信息。

---

## 【使用方法】

### 1. 在线获取镜像

```bash
docker pull swr.cn-south-1.myhuaweicloud.com/ascendhub/ascend-operator:{tag}
docker tag swr.cn-south-1.myhuaweicloud.com/ascendhub/ascend-operator:{tag} ascend-operator:{tag}
```

### 2. 本地构建 (v26.1.0+, 原文示例为 linux-aarch64 + Ubuntu 22.04)

```bash
docker build --no-cache -t ascend-operator:v26.1.0 ./ -f Dockerfile.ubuntu
```

> 原文提示: 若 Docker < 18.09 或未启用 BuildKit, 需先 `export DOCKER_BUILDKIT=1`, 否则 `TARGETPLATFORM` 变量无法解析导致构建失败。

### 3. 本地构建 (v26.0.0 及之前)

```shell
wget https://gitcode.com/Ascend/mind-cluster/releases/download/v26.0.0/Ascend-mindxdl-ascend-operator_26.0.0_linux-aarch64.zip
unzip Ascend-mindxdl-ascend-operator_26.0.0_linux-aarch64.zip -d Ascend-mindxdl-ascend-operator_26.0.0_linux-aarch64
cd Ascend-mindxdl-ascend-operator_26.0.0_linux-aarch64
docker build --no-cache -t ascend-operator:v26.0.0 ./ -f Dockerfile
```

### 4. 部署

```bash
kubectl apply -f ascend-operator-{version}.yaml
```

> 部署前需将 YAML 中的 `{tag}` 替换为实际版本号(原文未给出 YAML 内部可配置项, 原文未涉及详细配置字段)。

### 5. 验证部署

```bash
kubectl get pods -A | grep ascend-operator
```

预期结果: 对应命名空间下 ascend-operator 相关 Pod 处于 Running 状态。

### 6. 启用前的环境前提(从 Prerequisites 汇总)

- Kubernetes 1.17.x~1.34.x(推荐 1.19.x+)已部署于 All nodes;
- Volcano 已部署于 Management nodes, 版本参考 Volcano 官方兼容矩阵;
- 管理节点预留 ≥ 2 cores CPU、≥ 2.5 GB Memory。
