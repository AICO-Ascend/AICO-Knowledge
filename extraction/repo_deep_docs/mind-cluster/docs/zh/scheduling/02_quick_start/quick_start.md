# 快速入门<a name="ZH-CN_TOPIC_0000002511346939"></a>

> 仓 `mind-cluster` · 路径 `docs/zh/scheduling/02_quick_start/quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mind-cluster/docs/zh/scheduling/02_quick_start/quick_start.md

## 【定位】

本文面向初学者和训练业务开发者，提供“10 分钟快速验证普通 Pod 调度 NPU”和“基于完整 MindCluster 组件栈下发 PyTorch 训练任务”两条 Ascend NPU 集群调度入门路径。

## 【技术要点】

1. **双路径设计**  
   - `10分钟快速入门`仅部署 Ascend Device Plugin、Ascend Docker Runtime，使用 Kubernetes 原生调度器和普通 Pod 验证 NPU 资源调度。
   - `训练业务快速入门`部署 NodeD、Ascend Device Plugin、Ascend Docker Runtime、Volcano、ClusterD、Ascend Operator，以 PyTorch 训练任务体验端到端流程和整卡调度特性。

2. **环境与版本边界**  
   - Kubernetes 支持 `1.17.x~1.36.x`；安装 Volcano 时要求 Kubernetes `1.19.x` 及以上。
   - Docker 支持 `18.09.x~28.5.1`。
   - 快速安装示例基于一台 `Atlas 800T A2` 训练服务器和 `AArch64` CPU 架构。
   - 所有节点还需安装配套固件、驱动，并确认 `npu-smi`、`hccn_tool` 可正常运行。
   - 镜像和安装包下载依赖可用网络；离线环境需自行准备离线镜像包和组件安装包。

3. **节点标签与组件识别**  
   10 分钟路径通过下述命令标记 NPU 计算节点：  
   `kubectl label nodes --all workerselector=dls-worker-node`  
   原文说明该标签供 NodeD、Ascend Device Plugin 等组件识别和管理 NPU 资源。训练路径还为示例节点 `worker01` 设置：
   `node-role.kubernetes.io/worker=worker`、`workerselector=dls-worker-node` 和 `masterselector=dls-master-node`。

4. **组件安装与资源上报**  
   - 快速路径以 `VERSION=26.1.0` 为例，先安装 Ascend Docker Runtime，再拉取并本地标记 Device Plugin 镜像，最后部署其 DaemonSet。
   - Device Plugin 负责 NPU 设备发现与资源上报，Ascend Docker Runtime 负责 NPU 设备等资源挂载。
   - 低于 `26.1.0` 的版本使用 `device-plugin-910-v${VERSION}.yaml`；示例版本使用 `device-plugin-v${VERSION}.yaml`。
   - 可通过 `kubectl describe node -A | grep "huawei.com/Ascend910"` 检查上报的 NPU 资源。

5. **原生调度与容器内验证**  
   普通 Pod 请求 `huawei.com/Ascend910: 1`，使用 `ubuntu:22.04` 运行 `sleep 3600`，由 Kubernetes 原生调度器完成调度。Pod 进入 `Running` 后，通过 `kubectl exec -it np
