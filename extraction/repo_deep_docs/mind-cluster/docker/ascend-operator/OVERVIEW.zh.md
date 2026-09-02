# 集群调度组件 Ascend Operator

> 仓 `mind-cluster` · 路径 `docker/ascend-operator/OVERVIEW.zh.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mind-cluster/docker/ascend-operator/OVERVIEW.zh.md

# Ascend Operator 组件 Overview 文档深度解读

---

## 【定位】

**一句话**: 本文是 MindCluster 集群调度组件 Ascend Operator 的中文总览文档,系统说明该组件在 Kubernetes 上为 MindSpore / PyTorch 提供分布式训练调度能力的角色定位、组件功能、上下游依赖、镜像 Tag 规范、本地构建与在线部署流程,以及软硬件前置条件。

---

## 【技术要点】

1. **组件定位与部署形态**: Ascend Operator 是 MindCluster 集群调度组件之一,部署在**管理节点**上,通过 CRD(Custom Resource Definition)定义 **AscendJob** 任务,用户只需配置 YAML 即可发起分布式训练。
2. **支持的 AI 框架**: 支持 **MindSpore** 与 **PyTorch** 两个 AI 框架在 Kubernetes 上进行分布式训练。
3. **核心功能**:
   - 创建 Pod,并将集合通信参数按**环境变量**方式注入。
   - 创建 **RankTable** 文件,通过**共享存储或 ConfigMap** 挂载到容器,优化集合通信建链性能。
4. **调度依赖**: 通过 **Volcano** 进行资源感知与最终资源选定;通过 **Ascend Device Plugin** 获取芯片编号、IP、rankId 等信息,汇总生成集合通信文件。
5. **Tag 规范(版本分界)**: 自 **v26.1.0** 起,Tag 格式为 `<版本>-<操作系统>`(如 `v26.1.0-ubuntu22.04`、`v26.1.0-openeuler24.03`);**v26.0.0 及以前**版本 Tag 格式仅为 `<版本>`(如 `v26.0.0`)。
6. **软硬件前置要求**: Kubernetes **1.17.x ~ 1.34.x**(推荐 **1.19.x 及以上**);依赖 **Volcano**(版本需与 K8s 版本匹配);硬件最低 **2 核 CPU + 2.5GB 内存**。

---

## 【关键机制与数据】

### 工作流(组件上下游依赖,原文)

原文以 5 步描述 Ascend Operator 在一次分布式训练任务中的协同流程:

1. 通过 **Volcano** 感知当前任务所需资源是否满足。
2. 资源满足后,针对任务创建对应的 **Pod** 并注入集合通信参数的环境变量。
3. Pod 创建完成后,**Volcano** 进行资源的最终选定。
4. 从 **Ascend Device Plugin** 获取任务的芯片编号、IP、rankId 信息,汇总后生成集合通信文件。
5. 通过**共享存储或 ConfigMap**,将集合通信文件挂载到容器内。

### 数据流涉及的关键参数(原文)

- 输入:主进程 IP、静态组网集合通信所需的 **RankTable** 信息、当前 Pod 的 **rankId**。
- 输出/挂载对象:容器内可访问的 RankTable 文件(共享存储或 ConfigMap 形式)、集合通信环境变量。
- 镜像源: `swr.cn-south-1.myhuaweicloud.com/ascendhub/ascend-operator:{tag}`。

### 性能/版本数据(原文)

- 当前文档列出的最高组件版本为 **v26.1.0**(基础镜像可选 **Ubuntu 22.04** 与 **openEuler 24.03**),更早可追溯至 **v26.0.0**(仅 **Ubuntu 22.04** 基础镜像)。
- 文档未提供性能基准数据(如建链时延、吞吐等),仅定性表述 RankTable 挂载方式"优化集合通信建链性能"。

### 构建命令(原文,关键命令逐字保留)

- v26.1.0+ 构建(禁用缓存):
  ```
  docker build --no-cache -t ascend-operator:v26.1.0 ./ -f Dockerfile.ubuntu
  ```
- v26.0.0- 构建(基于官方安装包):
  ```
  wget https://gitcode.com/Ascend/mind-cluster/releases/download/v26.0.0/Ascend-mindxdl-ascend-operator_26.0.0_linux-aarch64.zip
  unzip Ascend-mindxdl-ascend-operator_26.0.0_linux-aarch64.zip -d Ascend-mindxdl-ascend-operator_26.0.0_linux-aarch64
  cd Ascend-mindxdl-ascend-operator_26.0.0_linux-aarch64
  docker build --no-cache -t ascend-operator:v26.0.0 ./ -f Dockerfile
  ```
- 在线拉取:
  ```
  docker pull swr.cn-south-1.myhuaweicloud.com/ascendhub/ascend-operator:{tag}
  docker tag swr.cn-south-1.myhuaweicloud.com/ascendhub/ascend-operator:{tag} ascend-operator:{tag}
  ```
- 部署与验证:
  ```
  kubectl apply -f ascend-operator-{version}.yaml
  kubectl get pods -A | grep ascend-operator
  ```

### BuildKit 注意事项(原文)

- `TARGETPLATFORM` 为 Docker **BuildKit** 内置全局变量,用于识别构建目标平台(如 `linux/amd64`、`linux/arm64`)。
- Docker 版本低于 **18.09** 或未启用 BuildKit 的环境,**无法读取** `TARGETPLATFORM` 变量,会导致镜像构建失败。
- 临时开启方式:
  ```
  export DOCKER_BUILDKIT=1
  ```

---

## 【表格解读】

### 表 1:Tag 字段说明(v26.1.0+ 规范)

| 字段     | 示例值           | 说明                     |
|--------|---------------|------------------------|
| `版本`   | `v26.1.0`     | Ascend Operator 版本号    |
| `操作系统` | `ubuntu22.04` | Ascend Operator 镜像操作系统 |

**解读**: 自 v26.1.0 起,镜像 Tag 由"纯版本"扩展为"版本 + 操作系统"二元组,以兼容 Ubuntu 22.04 与 openEuler 24.03 两种主流 OS 发行版;`操作系统`字段决定 Dockerfile 的选择(Dockerfile.ubuntu 或 Dockerfile.openeuler)。

### 表 2:Ascend Operator 26.1.0 Tag 与 Dockerfile

| Tag                      | Dockerfile                                                                                                                      | 镜像内容                                           |
|--------------------------|---------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------|
| `v26.1.0-ubuntu22.04`    | [Dockerfile.ubuntu](https://gitcode.com/Ascend/mind-cluster/blob/master/docker/ascend-operator/v26.1.0/Dockerfile.ubuntu)       | Ascend Operator v26.1.0 (基础镜像 Ubuntu 22.04)    |
| `v26.1.0-openeuler24.03` | [Dockerfile.openeuler](https://gitcode.com/Ascend/mind-cluster/blob/master/docker/ascend-operator/v26.1.0/Dockerfile.openeuler) | Ascend Operator v26.1.0 (基础镜像 openEuler 24.03) |

**解读**: v26.1.0 同时提供 Ubuntu 与 openEuler 两个官方 Dockerfile,镜像源指向 gitcode 仓库的 master 分支;两条 Tag 共享同一组件版本号,仅 OS 不同,用户按宿主 OS 选取对应 Dockerfile。

### 表 3:Tag 字段说明(v26.0.0 及以前规范)

| 字段   | 示例值       | 说明                  |
|------|-----------|---------------------|
| `版本` | `v26.0.0` | Ascend Operator 版本号 |

**解读**: 老版本仅以版本号作为 Tag,基础镜像默认为 Ubuntu 22.04(见下表),不再区分 OS 后缀。

### 表 4:Ascend Operator 26.0.0 Tag 与 Dockerfile

| Tag       | Dockerfile                                                                                                    | 镜像内容                                        |
|-----------|---------------------------------------------------------------------------------------------------------------|---------------------------------------------|
| `v26.0.0` | [Dockerfile](https://gitcode.com/Ascend/mind-cluster/blob/v26.0.0/component/ascend-operator/build/Dockerfile) | Ascend Operator v26.0.0 (基础镜像 Ubuntu 22.04) |

**解读**: v26.0.0 的 Dockerfile 位于 `v26.0.0` 分支的 `component/ascend-operator/build/` 路径,与 v26.1.0+ 的 `docker/ascend-operator/` 目录结构不同,反映该版本走的是传统的"组件构建"目录布局而非新版"Docker 镜像独立目录"布局。

### 表 5:软件依赖

| 软件名称       | 支持的版本                                                                                                                    | 安装位置 | 说明                                                               |
|------------|--------------------------------------------------------------------------------------------------------------------------|------|------------------------------------------------------------------|
| Kubernetes | 1.17.x~1.34.x(推荐使用1.19.x及以上版本)                                                                                           | 所有节点 | 了解 K8s 的使用请参见 [Kubernetes 文档](https://kubernetes.io/zh-cn/docs/) |
| Volcano    | 请参见 [Volcano 官网中对应的 Kubernetes 版本](https://github.com/volcano-sh/volcano/blob/master/README.md#kubernetes-compatibility) | 管理节点 | Ascend Operator 依赖 Volcano 进行资源调度                                |

**解读**: K8s 跨度从 1.17.x 到 1.34.x(共支持 18 个 minor 版本),但推荐起点为 1.19.x;Volcano 版本需与 K8s 版本严格对齐(由 Volcano 自身兼容性矩阵决定),且必须部署在管理节点(与 Ascend Operator 同节点)。

### 表 6:硬件规格要求

| 名称  | 要求    |
|-----|-------|
| CPU | 2核    |
| 内存  | 2.5GB |

**解读**: 该规格仅为 Ascend Operator 组件本身的最低运行门槛(管理节点),不包含 AI 训练工作负载(Worker Pod)的资源需求;说明该组件是轻量级控制面组件。

---

## 【公式解读】

原文无公式。

---

## 【关联】

本文处于 MindCluster 集群调度体系的**最上层入口文档**,通过引用与外部依赖建立了如下关系:

### 内部模块关联(同仓或同组件生态)

- **Ascend Device Plugin**:与 Ascend Operator 紧密耦合,Operator 通过它获取芯片编号、IP、rankId,以生成 RankTable(见"组件上下游依赖"步骤 4)。属于 MindCluster 同仓的另一组件。
- **Volcano**:调度层依赖,负责资源感知与最终资源选定(见步骤 1、3),不在本仓但通过 Kubernetes API 与 Operator 交互。
- **CRD / AscendJob**:Operator 注册到 K8s 的自定义资源,用户通过 YAML 与之交互,是 Operator 的"对外 API"。
- **MindSpore / PyTorch 训练框架**:Operator 服务的两个目标 AI 框架,通过环境变量注入与 RankTable 挂载为其分布式训练提供底层集合通信参数。

### 文档间关联(链接与跳转)

- **多语言版本**:`./OVERVIEW.md`(英文版,与本文档为同路径姊妹文件),由文首 `English | 中文` 切换。
- **上游帮助入口**:
  - [MindCluster 代码仓](https://gitcode.com/Ascend/mind-cluster)(主仓,所有组件 Dockerfile 与源码在此)
  - [MindCluster 昇腾社区文档](https://www.hiascend.com/document/detail/zh/mindcluster/latest/clustersched/dlug/docs/zh/scheduling/01_introduction/00_overview.md)(集群调度用户指南总览)
  - [问题反馈 Issues](https://gitcode.com/Ascend/mind-cluster/issues)
- **配套文档**:
  - [Kubernetes 文档](https://kubernetes.io/zh-cn/docs/)(K8s 使用基础)
  - [Volcano K8s 兼容性矩阵](https://github.com/volcano-sh/volcano/blob/master/README.md#kubernetes-compatibility)(选型 Volcano 版本)
  - [支持的产品形态和 OS 清单](https://gitcode.com/Ascend/mind-cluster/blob/master/docs/zh/scheduling/01_introduction/03_supported_product_models_and_os.md)(硬件型号支持范围)
  - [Mind 系列软件许可证信息](https://www.hiascend.com/zh/legal/softlicense)(法律合规)
- **Dockerfile 关联**:每个 Tag 都链回 gitcode 仓库对应 Dockerfile(v26.1.0 走 `master` 分支新路径,v26.0.0 走 `v26.0.0` tag 老路径),体现仓库目录结构在两个版本之间的迁移。

---

## 【使用方法】

### 1. 获取镜像(三种途径)

**(a) 在线拉取官方镜像(推荐)** —— 原文:
```
docker pull swr.cn-south-1.myhuaweicloud.com/ascendhub/ascend-operator:{tag}
docker tag swr.cn-south-1.myhuaweicloud.com/ascendhub/ascend-operator:{tag} ascend-operator:{tag}
```
替换 `{tag}` 为实际版本(如 `v26.1.0-ubuntu22.04`)。

**(b) v26.1.0+ 本地源码构建** —— 原文:
1. 从 `docker/ascend-operator/v26.1.0/` 获取 `Dockerfile.ubuntu`(或 `Dockerfile.openeuler`),保存到 aarch64 环境本地目录。
2. 执行:
   ```
   docker build --no-cache -t ascend-operator:v26.1.0 ./ -f Dockerfile.ubuntu
   ```
   若 Docker < 18.09 或 BuildKit 未启用,需先 `export DOCKER_BUILDKIT=1`。

**(c) v26.0.0 及更早版本本地构建** —— 原文:
1. `wget` 下载官方 `Ascend-mindxdl-ascend-operator_*.zip` 安装包。
2. `unzip` 解压至自定义目录。
3. `cd` 进入解压目录。
4. 执行:
   ```
   docker build --no-cache -t ascend-operator:v26.0.0 ./ -f Dockerfile
   ```

### 2. 部署 Operator(原文)

部署前需将 YAML 中的 `{tag}` 替换为实际镜像版本:
```
kubectl apply -f ascend-operator-{version}.yaml
```

### 3. 验证部署(原文)

```
kubectl get pods -A | grep ascend-operator
```
预期结果:对应命名空间下的 `ascend-operator` 相关 Pod 状态为 **Running**。

### 4. 前置检查项(原文)

- K8s 集群版本在 **1.17.x ~ 1.34.x** 区间(推荐 1.19.x+),且所有节点已就绪。
- Volcano 已部署且版本与 K8s 兼容,部署位置为**管理节点**。
- 管理节点满足最低硬件规格:**2 核 CPU + 2.5GB 内存**。
- 宿主机 OS 需为本文档所列镜像支持的系统(Ubuntu 22.04 / openEuler 24.03 等),具体清单见文末"支持的硬件"章节链接的"支持的产品形态和 OS 清单"文档。

### 5. YAML 训练任务配置

原文未给出具体的 AscendJob YAML 模板(仅说明"用户只需配置 YAML 文件,即可轻松实现分布式训练"),详细字段需参考 MindCluster 昇腾社区文档中关于 CRD/AscendJob 的定义文档。**原文未涉及具体 YAML 字段示例**。
