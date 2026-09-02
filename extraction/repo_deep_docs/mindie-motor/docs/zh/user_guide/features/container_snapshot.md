# 容器快照

> 仓 `mindie-motor` · 路径 `docs/zh/user_guide/features/container_snapshot.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-motor/docs/zh/user_guide/features/container_snapshot.md

# 容器快照特性深度解读

## 【定位】
本篇文档描述 mindie-motor 的**容器快照（Container Snapshot）特性**：将实例节点容器的运行状态（Device 快照 + 运行时模型权重）持久化为可恢复快照，用于在实例重调度等场景下快速恢复推理服务，避免冷启动开销。

---

## 【技术要点】

1. **组成结构（二元一体）**
   - 运行时模型权重：落盘至宿主机挂载路径。
   - 容器 Host 快照镜像：包含 Device 快照状态。

2. **职责分工**
   - 推理引擎：负责 Device 侧 suspend / resume、保存 Device 快照。
   - Motor 服务框架：负责刷新控制面状态（Controller 域名、`job_name`、`pod_ip`）、准备快照元数据、通过引擎状态感知保存/恢复进度。
   - MindCluster 或用户：负责对实例节点容器执行 Host 侧 checkpoint。

3. **稳态点判定（二选一）**
   - MindCluster 实例重调度场景：通过 Node Manager 的 `/readiness` 返回 `200` 判断。
   - 用户自定义场景：通过 `/node-manager/status` 返回 `200 {"status": true}` 判断。
   - 仅当本节点**全部原生引擎 Endpoint** 完成 suspend 后才视为到达稳态点。

4. **快照制作 4 步流程**
   - 冷启动 → 健康 → 引擎 Device 侧 suspend（锁定 Device、写权重至 `model_save_path`）→ 到达稳态点 → grus 执行 checkpoint → 元数据 `checkpoint` 字段更新为 `"done"` → 引擎自行解锁 Device。
   - 制作阶段 Node Manager **不触发显存快照保存**。

5. **快照恢复 4 步流程**
   - 从 Host 快照镜像恢复容器 → 挂载运行时权重与元数据 → Node Manager 读取 `job_name` / `namespace`、刷新 Pod IP 与 Controller DNS、向 Controller 重新注册 → Controller 下发启动命令 → Node Manager 更新 `model_load_path` 与 `data_parallel_master_ip` → 引擎 resume → 全部 Endpoint 健康后进入就绪。

6. **关键行为约束**
   - 处于 checkpoint 过程中的实例**无法提供推理服务**。
   - 到达稳态点但 `checkpoint` 尚未完成时，Node Manager **暂停向 Controller 上报正常心跳**。
   - 元数据字段值均为字符串，`enable_snapshot` 缺省 `false`（为 `false` 时其余字段均不生效），`snapshot_metadata_path` 缺省空字符串（空 → MindCluster 默认场景；非空 → 用户自定义场景，文件须预先创建并挂载）。

---

## 【关键机制与数据】

**环境约束（原文）：**
- 操作系统：EulerOS R15C10 / HCE 3.0
- 依赖：CRIU 3.19、grus
- 容器运行时：仅支持 containerd
- 推理引擎：必须提供 suspend / resume 接口

**数据流（快照制作）：**
```
冷启动 → 引擎 Device suspend ──┬──→ Device 快照（容器 Host 快照镜像内）
                              └──→ model_save_path（宿主机挂载路径，运行时权重）
            ↓
Node Manager 准备 snapshot_metadata.json（不触发显存快照）
            ↓
全部 Endpoint suspend 完成 → 稳态点（/readiness=200 或 /node-manager/status=200）
            ↓
MindCluster/用户 + grus → 容器 Host checkpoint
            ↓
checkpoint 字段置为 "done" → 引擎解锁 Device → 实例恢复推理
```

**数据流（快照恢复）：**
```
Host 快照镜像 + 运行时权重 + snapshot_metadata.json
            ↓
Node Manager 读 job_name / namespace → 刷 Pod IP / Controller DNS → 重新注册
            ↓
Controller 下发启动命令 → Node Manager 写 model_load_path / data_parallel_master_ip
            ↓
引擎读元数据 → resume → 全部 Endpoint 健康 → 就绪
```

**性能相关参数（原文 YAML）：**
- Readiness Probe：`periodSeconds: 5`、`timeoutSeconds: 4`、`failureThreshold: 12`
- `terminationGracePeriodSeconds: 30`
- `CRIU_LOG_LEVEL: "3"`
- 资源 requests：`memory: 64Gi`、`cpu: 16`、`huawei.com/Ascend910: 1`
- 资源 limits：`memory: 256Gi`、`cpu: 64`、`huawei.com/Ascend910: 1`

**规模约束（原文）：** MindCluster 仅为同种实例保存一份容器 Host 快照镜像，例如 2P1D 场景下，仅为首个 P 实例保存。

---

## 【表格解读】

### 快照元数据字段表（逐字还原）

| 字段 | 使用阶段 | 准备要求 | 说明 |
|------|----------|----------|------|
| `model_save_path` | 快照制作 | 制作容器快照前必须准备 | 运行时模型权重的落盘路径，必须是宿主机挂载路径 |
| `model_load_path` | 快照恢复 | 从容器快照恢复前必须准备 | 运行时模型权重的加载路径，必须是宿主机挂载路径 |
| `job_name` | 快照恢复 | 从容器快照恢复前必须准备 | 推理实例的唯一标识，恢复后注册时用于更新 Node Manager 的任务名 |
| `namespace` | 快照恢复 | Controller 使用集群内 `.svc.cluster.local` DNS 时必须准备 | 推理服务所属 namespace，用于更新 Controller DNS；非集群 DNS 场景可不配置 |
| `data_parallel_master_ip` | 快照恢复 | 可不预先配置 | 实例 Master DP 所在 Pod 的 IP；优先使用文件中的值，未配置时由 Node Manager 写入 Controller 下发值 |
| `checkpoint` | 快照制作 | Host 侧 checkpoint 完成后写入 | 更新为 `"done"` 后，引擎解锁 Device，冷启动实例恢复推理服务 |

**逐行解读：**
- **`model_save_path`**：快照制作阶段唯一必须预先准备的字段，决定运行时权重的宿主机落盘位置；该字段缺失则制作流程无法落地权重。
- **`model_load_path`**：快照恢复阶段必填，与制作时的 `model_save_path` 配套使用，构成"权重读写对"。
- **`job_name`**：快照恢复阶段必填，是 Node Manager 重新注册时使用的实例唯一标识；若缺失，恢复后的实例无法在 Controller 上正确归属。
- **`namespace`**：仅在使用集群内 `*.svc.cluster.local` Controller DNS 时必填；若使用非集群 DNS，可省略，体现了对外部 DNS 方案的兼容性。
- **`data_parallel_master_ip`**：DP 通信的 Master IP，可后置由 Node Manager 在收到 Controller 下发值后写入；体现"先尝试读文件、未配置时回退到下发值"的两段式优先级。
- **`checkpoint`**：唯一的运行时状态字段，由外部（MindCluster 或用户）在 Host 侧 checkpoint 完成后写入 `"done"`，作为引擎解锁 Device 的信号；该字段是 Device 状态机与 Host 进程状态机之间的同步桥梁。

---

## 【公式解读】

原文无公式。

---

## 【关联】

本特性处于一个**三方协作链路**中，上下游关系如下：

- **上游 / 编排层**：
  - **MindCluster**：默认应用场景的协作方，负责通过 ConfigMap 挂载快照元数据、查询稳态点（经由 `/readiness`）、执行容器 checkpoint、保存 Host 快照镜像。该特性默认即面向 MindCluster 实例重调度设计。
  - **用户自定义场景**：用户取代 MindCluster 的角色，自行挂载元数据、查询稳态点（经由 `/node-manager/status`）、执行 checkpoint、管理 Host 镜像与运行时权重。

- **下游 / 引擎层**：
  - **推理引擎**：必须实现 Device 侧 suspend / resume、保存/恢复 Device 快照；通过 `checkpoint` 字段从 `"done"` 感知 Host 侧 checkpoint 完成，从而解锁 Device。

- **横向依赖**：
  - **CRIU 3.19 + grus**：Host 侧容器 checkpoint 的底层工具，缺一不可。
  - **containerd**：唯一受支持的容器运行时。
  - **Controller**：快照恢复时的控制面入口；Node Manager 通过刷新 Controller DNS 与 Pod IP 后重新注册并接收启动命令。
  - **ConfigMap / 共享存储**：默认场景下 MindCluster 借由 ConfigMap 挂载元数据，Host 快照镜像必须落在集群共享存储路径下以便管理。

- **与其他特性的协同点**：
  - `infer_service_template.yaml` 中的 Readiness Probe 是与 MindCluster 协作的关键开关，未启用则 MindCluster 无法探测稳态点。
  - `seccompProfile.type: Unconfined` 是因 CRIU/grus 跨架构 syscall 兼容性要求而被禁用 seccomp 过滤的特殊设置（仅在确有需要时启用）。
  - 容器挂载需"取消宿主机落盘挂载"（如 `/data`、`/dev/shm`、`/var/coredump`、`plog-path`），并新增 `snapshot-weight`、`dcmi`、`ascend-driver` 等快照恢复所必需的路径（原文 YAML 在 `mountPropagation` 处被截断，后续挂载字段未给出）。

- **外部链接**：原文指向 MindCluster 仓库的 [容器快照部署及使用文档](https://gitcode.com/Ascend/mind-cluster/blob/master/docs/zh/scheduling/04_usage/09_infer_operator_best_practice/06_container_snapshot_usage.md)，用于 MindCluster 侧的环境要求、组件部署与使用流程（mindie-motor 仓库内无内部链接）。

---

## 【使用方法】

### 启用容器快照（Motor 侧）

在 `user_config.json` 中新增配置组：

```json
"motor_container_snapshot_config": {
    "enable_snapshot": true,
    "snapshot_metadata_path": "/path/to/snapshot_metadata.json"
}
```

- `enable_snapshot`：总开关，`true` 启用快照制作与恢复能力。
- `snapshot_metadata_path`：留空或缺省 → 进入 **MindCluster 默认场景**（元数据由 MindCluster 通过 ConfigMap 挂载，Node Manager 复制到 `/snapshot/snapshot_metadata.json`）；非空 → 进入 **用户自定义场景**（用户需预先创建并挂载该文件）。

### 实例重调度场景额外配置（Motor 侧）

1. `user_config.json`：
```json
"motor_container_snapshot_config": {
    "enable_snapshot": true
}
```

2. `infer_service_template.yaml`（Union 实例示例）需做以下改动（原文共 6 处 TODO，原文 YAML 在挂载段被截断）：

| TODO | 改动点 | 关键内容 |
|------|--------|----------|
| TODO 1 | `metadata.labels` | `infer.huawei.com/container-snapshot: 'true'` |
| TODO 2 | `spec.podManagementPolicy` | `Parallel`（并行启动） |
| TODO 3 | 容器 `readinessProbe` | `bash -c "$CONFIGMAP_PATH/probe.sh readiness"`，`periodSeconds: 5`，`timeoutSeconds: 4`，`failureThreshold: 12` |
| TODO 4 | 环境变量 `host_snapshot_dir_path` | 共享存储路径，且不能在容器内挂载 |
| TODO 5 | 取消宿主机落盘挂载 | 注释掉 `data`、`dshm`、`coredump`、`plog-path` 等挂载 |
| TODO 6 | 新增挂载路径 | `snapshot-weight` → `/snapshot/weight`、`dcmi` → `/usr/local/dcmi`、`ascend-driver` → `/usr/local/Ascend/driver`（原文在 `mountPropagation` 处被截断） |

### 元数据准备清单

- 用户自定义场景**制作前**必填：`model_save_path`
- 用户自定义场景**恢复前**必填：`model_load_path`、`job_name`
- 使用集群内 Controller DNS 时**恢复前**还需：`namespace`
- `data_parallel_master_ip` 可由 Node Manager 在收到 Controller 下发值后回填
- `checkpoint` 由外部在 Host checkpoint 完成后写入 `"done"`

### 实例重调度场景的额外约束（原文）

- MindCluster 仅支持 **CRD 部署方式**保存 Host 快照镜像。
- 同种实例**仅保存一份** Host 快照镜像（如 2P1D 仅首个 P 实例保存）。
- Host 快照镜像必须保存在**集群共享存储路径**下。

### MindCluster 侧

原文未在 mindie-motor 仓库内详述；具体环境要求、组件部署与使用流程需参见外部文档：<https://gitcode.com/Ascend/mind-cluster/blob/master/docs/zh/scheduling/04_usage/09_infer_operator_best_practice/06_container_snapshot_usage.md>。
