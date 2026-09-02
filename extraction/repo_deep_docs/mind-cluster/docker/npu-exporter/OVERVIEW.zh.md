# 集群调度组件 NPU Exporter

> 仓 `mind-cluster` · 路径 `docker/npu-exporter/OVERVIEW.zh.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mind-cluster/docker/npu-exporter/OVERVIEW.zh.md

# NPU Exporter Overview 文档深度解读

---

## 【定位】

本文档是 MindCluster 集群调度组件中 **NPU Exporter** 的中文总览文档，旨在帮助用户理解 NPU Exporter 的组件定位、功能特性、上下游依赖关系、镜像 Tag 规范、软硬件要求，并指导用户完成镜像获取、本地构建和 Kubernetes 部署，从而在昇腾计算节点上采集并上报昇腾 AI 处理器（及 vNPU）的网络与算力使用数据，供 Prometheus/Telegraf 监控系统消费以定位任务运行性能瓶颈。

---

## 【技术要点】

1. **组件定位**：NPU Exporter 是 MindCluster 集群调度组件之一，**部署在计算节点上**，核心职责是"从驱动取数据，向监控系统吐数据"——支持 **Prometheus** 和 **Telegraf** 两种监控集成方式。

2. **监测数据范围**：
   - 昇腾 AI 处理器：**利用率、温度、电压、内存**等数据实时监测。
   - 虚拟 NPU（vNPU）：**AI Core 利用率、vNPU 总内存、vNPU 使用中内存**。
   - 网络数据：芯片及网络相关信息。
   - 支持**自定义指标开发**（用户可参考 demo 插件）。

3. **上下游数据流**（三段式）：
   - **上游采集**：从**驱动**获取芯片及网络信息 → 放入本地缓存；从 **K8s 标准化接口 CRI** 获取容器信息 → 放入本地缓存。
   - **下游暴露**：实现 **Prometheus / Telegraf 钩子函数**，由二者周期性拉取本地缓存数据。

4. **Tag 规范（v26.1.0 起）**：格式为 `<版本>-<操作系统>`，如 `v26.1.0-ubuntu22.04`、`v26.1.0-openeuler24.03`；v26.0.0 及以前仅以 `<版本>` 形式（如 `v26.0.0`）。

5. **软件依赖**：Kubernetes **1.17.x ~ 1.34.x**（推荐 1.19.x 及以上）；Prometheus 建议最新稳定版；昇腾 AI 处理器驱动和固件、UMDK 软件包需参见版本配套表，其中 UMDK 专门用于 **Atlas 850 系列硬件产品**与 **Atlas 950 SuperPod 产品**的镜像构建。

6. **硬件规格要求**：CPU **1 核**，内存 **1 GB**（极轻量级资源占用）。

---

## 【关键机制与数据】

### 数据流工作原理

原文描述的 NPU Exporter 数据流为典型的"**采集—缓存—暴露**"三段式：

```
[驱动] ──芯片/网络数据──┐
                        ├─→ [本地缓存] ──→ Prometheus / Telegraf 周期性拉取
[K8s CRI] ──容器信息────┘
```

- **数据来源端（原文）**：①从驱动中获取芯片以及网络信息；②从 K8s 标准化接口 CRI 中获取容器信息；两项均放入本地缓存。
- **数据消费端（原文）**：实现 Prometheus 或者 Telegraf 的接口，供二者周期性获取缓存中的数据信息。
- **指标覆盖（原文）**：适配 Prometheus 钩子函数与 Telegraf 钩子函数各提供一套标准接口；用户可通过 demo 自定义指标插件扩展。

### 关键性能/资源参数（原文）

| 项目 | 取值（原文） |
|---|---|
| 监控服务端口 | `8082`（访问路径 `/metrics`） |
| CPU 最低要求 | 1 核 |
| 内存最低要求 | 1 GB |
| K8s 节点标签 | `workerselector=dls-worker-node` |
| Prometheus 拉取命令 | `curl http://<pod-ip>:8082/metrics` |

> 注：原文未提供 QPS、采集频率、采样周期等性能数据，故不臆造。

### 关键构建注意事项（原文）

- 构建镜像时必须开启 Docker **BuildKit**，否则无法读取 `TARGETPLATFORM` 内置全局变量（用于识别 `linux/amd64`、`linux/arm64`）。
- Docker 版本需 ≥ **18.09**，否则需手动 `export DOCKER_BUILDKIT=1` 临时开启。
- 构建命令均使用 `--no-cache` 以保证构建纯净度。

---

## 【表格解读】

### 表 1：v26.1.0 起 Tag 规范字段说明

| 字段 | 示例值 | 说明 |
|---|---|---|
| `版本` | `v26.1.0` | NPU Exporter 版本号 |
| `操作系统` | `ubuntu22.04` | NPU Exporter 镜像操作系统 |

**解读**：自 v26.1.0 起，单一版本号不再足以定位镜像，必须同时指定底层操作系统，以适配昇腾多 OS 交付场景。

---

### 表 2：NPU Exporter 26.1.0 镜像清单

| Tag | Dockerfile | 镜像内容 |
|---|---|---|
| `v26.1.0-ubuntu22.04` | [Dockerfile.ubuntu](https://gitcode.com/Ascend/mind-cluster/blob/master/docker/npu-exporter/v26.1.0/Dockerfile.ubuntu) | NPU Exporter v26.1.0 (基础镜像 Ubuntu 22.04) |
| `v26.1.0-openeuler24.03` | [Dockerfile.openeuler](https://gitcode.com/Ascend/mind-cluster/blob/master/docker/npu-exporter/v26.1.0/Dockerfile.openeuler) | NPU Exporter v26.1.0 (基础镜像 openEuler 24.03) |

**解读**：v26.1.0 提供两种 OS 基础镜像——**Ubuntu 22.04** 与 **openEuler 24.03**——分别对应异构算力集群中两种主流服务器操作系统；Dockerfile 路径放在 `docker/npu-exporter/v26.1.0/` 目录下，与组件目录解耦。

---

### 表 3：v26.0.0 及以前 Tag 规范字段说明

| 字段 | 示例值 | 说明 |
|---|---|---|
| `版本` | `v26.0.0` | NPU Exporter 版本号 |

**解读**：旧版 Tag 仅含版本号，意味着该版本所有 OS 共用一个 Tag，镜像仅默认基于 Ubuntu 22.04。

---

### 表 4：NPU Exporter 26.0.0 镜像清单

| Tag | Dockerfile | 镜像内容 |
|---|---|---|
| `v26.0.0` | [Dockerfile](https://gitcode.com/Ascend/mind-cluster/blob/v26.0.0/component/npu-exporter/build/Dockerfile) | NPU Exporter v26.0.0 (基础镜像 Ubuntu 22.04) |

**解读**：旧版 Dockerfile 位于 `component/npu-exporter/build/` 路径下，结构与新版 `docker/npu-exporter/<版本>/` 不同，反映了项目目录重构。

---

### 表 5：软件依赖

| 软件名称 | 支持的版本 | 安装位置 | 说明 |
|---|---|---|---|
| Kubernetes | 1.17.x~1.34.x（推荐使用 1.19.x 及以上版本） | 所有节点 | 了解 K8s 的使用请参见 Kubernetes 文档 |
| Prometheus | 建议使用最新稳定版本 | 监控节点 | NPU Exporter 适配 Prometheus 钩子函数提供监控数据 |
| 昇腾 AI 处理器驱动和固件 | 请参见版本配套表 | 计算节点 | 请参见《CANN 软件安装指南》中"安装 NPU 驱动和固件"章节 |
| UMDK 软件包 | 请参见版本配套表 | 计算节点 | 针对 **Atlas 850 系列硬件产品**、**Atlas 950 SuperPod 产品**，在构建镜像时需要 |

**解读**：依赖分两类——集群/监控侧依赖（K8s + Prometheus）和昇腾侧依赖（驱动/固件/UMDK）。K8s 版本跨度极大（1.17~1.34，共 18 个 minor 版本），兼容性覆盖广；UMDK 仅在特定 Atlas 硬件平台（850 / 950 SuperPod）的镜像构建阶段才需要，是构建期而非运行期依赖。

---

### 表 6：硬件规格要求

| 名称 | 要求 |
|---|---|
| CPU | 1 核 |
| 内存 | 1 GB |

**解读**：NPU Exporter 是轻量级导出器，只承担数据缓存和接口暴露，无需重计算，故单核 1GB 即可满足运行需求。

---

## 【公式解读】

**原文无公式**。

文档未涉及任何数学公式、伪代码或量化模型；工作机制以文字描述和命令/表格为主。

---

## 【关联】

本文档与其他组件/模块的关系如下：

### 1. 与 MindCluster 主代码仓的关系
- **仓库归属**：NPU Exporter 由 [MindCluster 代码仓](https://gitcode.com/Ascend/mind-cluster) 统一维护，源代码与 Docker 镜像构建文件均托管在同一仓库下。
- **目录分布**：
  - 新版（v26.1.0+）Dockerfile 位于 `docker/npu-exporter/<版本>/Dockerfile.{ubuntu|openeuler}`。
  - 旧版（v26.0.0）Dockerfile 位于 `component/npu-exporter/build/Dockerfile`。
- **版本发布**：旧版通过 `Ascend-mindxdl-npu-exporter_<版本>_linux-aarch64.zip` 安装包分发，新版以容器镜像（`swr.cn-south-1.myhuaweicloud.com/ascendhub/npu-exporter`）方式分发。

### 2. 与集群调度主流程的关系
- NPU Exporter 是 **MindCluster 集群调度组件**的一部分，与 MindCluster 文档入口 [MindCluster 昇腾社区](https://www.hiascend.com/document/detail/zh/mindcluster/latest/clustersched/dlug/docs/zh/scheduling/01_introduction/00_overview.md) 所述调度能力形成上下游。
- 上游：依赖昇腾 AI 处理器**驱动**和**固件**（运行期）以及 **UMDK**（构建期，特定 Atlas 平台）。
- 下游：被 **Prometheus** 或 **Telegraf** 通过钩子函数周期性拉取。
- 节点层：通过 K8s 节点标签 `workerselector=dls-worker-node` 接入调度匹配。

### 3. 与文档系统的关联
- **支持的产品形态与 OS 清单**：链接到 `docs/zh/scheduling/01_introduction/03_supported_product_models_and_os.md`，明确支持哪些昇腾硬件型号与操作系统组合。
- **许可证**：指向 [Mind 系列软件许可证](https://www.hiascend.com/zh/legal/softlicense)，并提示预装的 Python、系统库等受各自许可证约束。

### 4. 文末内部链接
- `./OVERVIEW.md`：本文档对应的英文版（English overview），双语互链方便国际化用户查阅。

---

## 【使用方法】

### 一、在线获取镜像

```bash
# 1. 拉取官方镜像（{tag} 替换为实际版本号，如 v26.1.0-ubuntu22.04）
docker pull swr.cn-south-1.myhuaweicloud.com/ascendhub/npu-exporter:{tag}

# 2. 修改镜像标签（统一本地命名规范）
docker tag swr.cn-south-1.myhuaweicloud.com/ascendhub/npu-exporter:{tag} npu-exporter:{tag}
```

### 二、本地构建（可选）

#### v26.1.0+ 构建流程

1. 从 GitCode 仓库 `docker/npu-exporter/v26.1.0/` 获取 `Dockerfile.ubuntu`（或 `Dockerfile.openeuler`）至 aarch64 本地目录。
2. 构建（需 BuildKit）：
   ```bash
   export DOCKER_BUILDKIT=1   # 必要时手动开启
   docker build --no-cache -t npu-exporter:v26.1.0 ./ -f Dockerfile.ubuntu
   ```

#### v26.0.0 及更早版本构建流程

1. `wget` 下载官方安装包：`Ascend-mindxdl-npu-exporter_26.0.0_linux-aarch64.zip`。
2. `unzip` 解压至自定义目录。
3. `cd` 进入工作目录。
4. `docker build --no-cache -t npu-exporter:v26.0.0 ./ -f Dockerfile`。

### 三、部署到 Kubernetes

| 步骤 | 命令/操作 | 备注 |
|---|---|---|
| 1. 节点打标 | `kubectl label nodes <node-name> workerselector=dls-worker-node` | 用于集群调度匹配计算节点 |
| 2. 部署组件 | `kubectl apply -f npu-exporter-{version}.yaml` | 部署前需将 YAML 中 `{tag}` 替换为实际镜像版本 |
| 3. 验证部署 | `kubectl get pods -A \| grep npu-exporter` | 预期 Pod 状态为 **Running** |
| 4. 访问监控指标 | `curl http://<pod-ip>:8082/metrics` | 通过 Pod IP 与 **8082** 端口的 `/metrics` 路径获取 Prometheus 格式指标 |

### 四、关键配置项

| 配置项 | 取值 | 说明 |
|---|---|---|
| K8s 节点标签 | `workerselector=dls-worker-node` | 标记可被调度的计算节点 |
| 监控服务端口 | `8082` | Prometheus/Telegraf 拉取端口 |
| 指标路径 | `/metrics` | Prometheus 标准路径 |
| 构建时平台变量 | `TARGETPLATFORM`（如 `linux/amd64`、`linux/arm64`） | 由 Docker BuildKit 自动注入，需 BuildKit 启用 |

> 原文未涉及更细粒度的运行时配置项（如采集间隔、白名单指标、认证凭证等），这些属于 `npu-exporter-{version}.yaml` 内部字段，本文不展开。
