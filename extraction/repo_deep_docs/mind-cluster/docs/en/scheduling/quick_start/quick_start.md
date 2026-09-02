# Quick Start<a name="ZH-CN_TOPIC_0000002511346939"></a>

> 仓 `mind-cluster` · 路径 `docs/en/scheduling/quick_start/quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mind-cluster/docs/en/scheduling/quick_start/quick_start.md

# 「Quick Start」文档深度解读

---

## 【定位】

本文档是 MindCluster 集群调度能力的**双路径快速上手指南**,面向两类用户:**入门用户**通过仅部署 Ascend Device Plugin + Kubernetes 原生调度器,在 10 分钟内验证 NPU 资源调度能力;**进阶用户**通过部署完整的集群调度组件栈(NodeD + Ascend Device Plugin + Ascend Docker Runtime + Volcano + ClusterD + Ascend Operator),以 PyTorch 训练任务为例走通端到端分布式训练流程。

---

## 【技术要点】

1. **两条路径分级部署**:文档提供"10-Minute Quick Start"(仅 Ascend Device Plugin + K8s 原生调度器 + 普通 Pod)与"E2E Training Service Quick Start"(完整六件套)两种入门路径,后者以两台 Atlas 800T A2(一台管理节点、一台计算节点)为例。
2. **环境基线版本约束**:Kubernetes 支持 1.17.x~1.34.x;若使用 Volcano 则需 1.19.x 及以上;Docker 支持 18.09.x~28.5.1。
3. **NPU 资源抽象与调度机制**:Device Plugin 上报的资源名为 `huawei.com/Ascend910`;通过 nodeSelector(`workerselector=dls-worker-node` + `accelerator=huawei-Ascend910`)与 `resources.limits/requests` 双重声明实现 NPU 绑定;挂载 hostPath `/usr/local/Ascend/driver` 供容器内 NPU 调用,容器内需追加 `LD_LIBRARY_PATH=/usr/local/Ascend/driver/lib64/common:/usr/local/Ascend/driver/lib64/driver`。
4. **镜像与软件包来源**:镜像从 `swr.cn-south-1.myhuaweicloud.com/ascendhub/ascend-k8sdeviceplugin:v26.0.0` 拉取并打本地 tag;配置文件包为 `Ascend-mindxdl-device-plugin_26.0.0_linux-aarch64.zip`,从 `gitcode.com/Ascend/mind-cluster/releases/download/v26.0.0/` 下载。
5. **驱动与固件版本查询命令**:`npu-smi info -t board -i NPU ID`,其中 `Software Version` 字段为驱动版本,`Firmware Version` 字段为固件版本。
6. **验证期望值**:示例节点 `worker01` 上报 8 个 `huawei.com/Ascend910` 资源(命令输出中出现两次,行格式如 `huawei.com/Ascend910:     8`);Pod `npu-test` 期望在 `STATUS=Running` 时被调度到 `worker01`。

---

## 【关键机制与数据】

- **资源发现机制**(原文:10-Minute Quick Start → "Verifying NPU Resources"):Ascend Device Plugin 以 DaemonSet 形式部署在 kube-system 命名空间(原文示例 `ascend-device-plugin-daemonset-d5ctz`,READY `1/1`、STATUS `Running`),通过 `kubectl describe node worker01` 查询可看到 `huawei.com/Ascend910: 8` 行,代表该节点可分配 8 张 Ascend910 芯片。
- **NPU 访问验证机制**(原文:"Verifying NPU Access"):容器内执行 `npu-smi info` 时,必须先设置 `LD_LIBRARY_PATH`,否则会因找不到 `.so` 而失败——这印证了 hostPath 挂载 `/usr/local/Ascend/driver` 仅提供二进制/库目录结构,运行时还需显式注入库搜索路径。
- **节点过滤机制**(原文:"Adding Labels to NPU Nodes"):通过 `workerselector=dls-worker-node`(业务标签)与 `accelerator=huawei-Ascend910`(加速器类型标签)两道标签实现调度候选集筛选,与 Pod 模板中的 `nodeSelector` 联动。
- **故障诊断链路**(原文:FAQs):Pod Pending 状态的根因定位走 `kubectl describe pod` + 节点标签校验路径;Device Plugin 启动失败的根因定位走 `/usr/local/Ascend/driver` 目录存在性校验路径。
- **组件协同关系**(原文:Table 1):E2E 路径中的安装与训练作业提交分别下钻到《Installation and Deployment》与《Basic Scheduling》两份文档,形成"安装 → 调度 → 训练"闭环。

---

## 【表格解读】

### 表 1:Environment Requirements(原文 10-Minute Quick Start → "Environment Requirements")

| Requirement | Description |
|------|-------------------|
| Compute node | Atlas 800T A2 training server (Arm64) as an example |
| Driver version | Ascend driver matching the server |

**逐行解读**:
- **Compute node**:限定示例硬件为 Atlas 800T A2 训练服务器,架构为 Arm64——这意味着所有二进制包(xxx_linux-aarch64)与镜像选择都基于 Arm64 架构,不能直接套用于 x86 环境。
- **Driver version**:要求驱动与服务器型号严格匹配,无具体版本号(由固件驱动配套指南给出),并暗示驱动是 NPU 调度的**前置硬依赖**,未安装则后续 Device Plugin 无法工作。

### 表 2:FAQs(原文 10-Minute Quick Start → "FAQs")

| Issue | Cause | Solution |
|------|------|---------|
| Pod remains in Pending state | Insufficient NPU resources or mismatched node labels | Check `kubectl describe pod` and node labels. |
| Ascend Device Plugin boot failure | Incorrect driver path | Check whether `/usr/local/Ascend/driver` exists. |

**逐行解读**:
- **Pending 状态**:根因为"资源不足"或"节点标签不匹配"——前者对应已无可分配 `Ascend910` 资源,后者对应 `nodeSelector` 与已打标签不吻合;排查手段是 `describe pod`(看 Events 中的 `FailedScheduling`)与节点标签复核。
- **Device Plugin 启动失败**:根因为驱动路径不正确——DaemonSet 容器内会校验 `/usr/local/Ascend/driver`,缺失则立即退出,导致 `kube-system` 中 DaemonSet Pod 无法 `Running`。

### 表 3:Key procedures(原文:E2E Training Service Quick Start → Procedure)

|Procedure|Description|For More Information|
|--|--|--|
|[Installing Components](#section1837511531098)|Using Atlas 800T A2 training servers as an example, this walks you through quickly installing cluster scheduling components on Ascend devices.| [Installation and Deployment](../developer_guide/installation_deployment/manual_installation/00_obtaining_software_packages.md)|
|[Delivering a Training Job](#section106493419399)|Using a simple PyTorch training job as an example, this helps you quickly understand the workflow for submitting a training job.| [Basic Scheduling](../usage/basic_scheduling/00_feature_description.md)|

**逐行解读**:
- **Installing Components**:本表流程的**前半段**,负责在 Ascend 设备上落地全部六件集群调度组件,详细参数与步骤跳转至《Installation and Deployment》(对应内部链接 `../developer_guide/installation_deployment/manual_installation/00_obtaining_software_packages.md`)。
- **Delivering a Training Job**:本表流程的**后半段**,以 PyTorch 训练任务为例演示训练作业提交流程,细节跳转至《Basic Scheduling》(对应内部链接 `../usage/basic_scheduling/00_feature_description.md`)。两者串联构成"先装组件,再跑业务"的完整闭环。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **上游前置依赖(环境准备章节)**:依赖 `npu-smi`、`hccn_tool` 主机工具;依赖 Atlas A2 硬件对应的固件驱动安装指南(EDOC1100568434、EDOC1100568421、EDOC1100568362);依赖《Ascend Training Solution Version Mapping》确认组件-固件-驱动的版本兼容矩阵。
- **横向组件协同(E2E 路径)**:NodeD(节点发现与状态上报)↔ Ascend Device Plugin(NPU 资源抽象)↔ Ascend Docker Runtime(容器运行时注入)↔ Volcano(批量/拓扑调度)↔ ClusterD(集群级调度决策)↔ Ascend Operator(K8s CRD 化训练作业)——六者形成完整的"节点-设备-容器-调度-作业"分层栈。
- **下游文档跳转**:
  - `../developer_guide/installation_deployment/manual_lementation/00_obtaining_software_packages.md` 提供六件组件的详细安装参数(被 Table 1 第一行引用)。
  - `../usage/basic_scheduling/00_feature_description.md` 提供基础调度特性说明与 PyTorch 训练作业示例(被 Table 1 第二行引用)。
  - `../api/ascend_operator.md` 定义 Ascend Operator 的 API/CRD 契约,为 E2E 路径中"Delivering a Training Job"提供作业模板规范。
- **同级配套文档**:本文未直接链接,但 10-Minute 路径中 `kubectl label nodes` 与 `huawei.com/Ascend910` 资源名的使用,暗示与"Feature Description""Scheduling Guide"存在引用关系。

---

## 【使用方法】

### 10-Minute Quick Start 启用流程

1. **环境校验**(原文:"Pre-check"):`npu-smi info` 应能输出芯片信息。
2. **打标签**(原文:"Adding Labels to NPU Nodes"):
   ```
   kubectl label nodes worker01 workerselector=dls-worker-node
   kubectl label nodes worker01 accelerator=huawei-Ascend910
   ```
3. **拉镜像**(原文:"Deploying Ascend Device Plugin → 1"):
   ```
   docker pull swr.cn-south-1.myhuaweicloud.com/ascendhub/ascend-k8sdeviceplugin:v26.0.0
   docker tag swr.cn-south-1.myhuaweicloud.com/ascendhub/ascend-k8sdeviceplugin:v26.0.0 ascend-k8sdeviceplugin:v26.0.0
   ```
4. **下载并部署配置**(原文:"2 Deploy Ascend Device Plugin"):
   ```
   mkdir /tmp/devicePlugin && cd /tmp/devicePlugin
   wget https://gitcode.com/Ascend/mind-cluster/releases/download/v26.0.0/Ascend-mindxdl-device-plugin_26.0.0_linux-aarch64.zip
   unzip Ascend-mindxdl-device-plugin_26.0.0_linux-aarch64.zip
   kubectl apply -f device-plugin-910-v26.0.0.yaml
   ```
   其中 `device-plugin-910-v26.0.0.yaml` 的 `910` 即原文占位符 `{xxx}` 取值(原文:In the following text, `{xxx}` takes the value `910` as the chip model)。
5. **验证资源**:`kubectl describe node worker01 | grep -A 10 "huawei.com/Ascend910"` 应出现 `huawei.com/Ascend910:     8`。
6. **测试 Pod**:应用 `npu-test-pod.yaml`(声明 `huawei.com/Ascend910: 1`、挂载 `/usr/local/Ascend/driver` 为主机路径),`kubectl get pods npu-test -o wide` 应见 `STATUS=Running`、NODE=`worker01`。
7. **验证 NPU 可用性**:`kubectl exec -it npu-test -- /bin/bash` 后,容器内 `export LD_LIBRARY_PATH=/usr/local/Ascend/driver/lib64/common:/usr/local/Ascend/driver/lib64/driver:${LD_LIBRARY_PATH}` 再 `npu-smi info`。
8. **清理**:删除测试 Pod 与 DaemonSet 配置。

### E2E Training Service Quick Start 启用流程

原文涉及。具体步骤需登录 compute 或 management 节点以 `root` 用户执行组件安装目录创建命令(原文给出示例目录 `/tmp/noded`、`/tmp/devicePlugin`、`mkdir` ——原文该段在 "mkdir" 处截断,具体后续步骤需跳转至 [Installation and Deployment](../developer_guide/installation_deployment/manual_installation/00_obtaining_software_packages.md) 与 [Basic Scheduling](../usage/basic_scheduling/00_feature_description.md) 获取完整命令)。
