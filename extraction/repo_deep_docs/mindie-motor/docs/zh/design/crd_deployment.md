# CRD 方式部署设计文档（MindIE Motor）

> 仓 `mindie-motor` · 路径 `docs/zh/design/crd_deployment.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-motor/docs/zh/design/crd_deployment.md

# CRD 方式部署设计文档 — 深度解读

## 【定位】

本文档描述 MindIE Motor 基于 `InferServiceSet` CRD（`mindcluster.huawei.com/v1`）的部署方式设计与实现，解决"如何用一个 CRD 资源统一拉起 controller / coordinator / prefill / decode / union 全套推理角色 Pod，并替代传统的多 yaml Deployment 方式"这一核心问题，同时给出与旧 `multi_deployment` 模式并存的切换约束与扩缩容/刷新策略。

---

## 【技术要点】

1. **CRD 统一拉起机制**：默认部署模式为 `infer_service_set`，通过单个 `infer_service.yaml`（内含 RBAC + `InferServiceSet`）由 CRD controller（MindCluster infer-operator）统一创建 controller、coordinator、prefill、decode（PD 分离）或 union（PD 混部）等 Pod。
2. **模板实例化**：`infer_service_init.yaml` 作为多文档 YAML 模板（ServiceAccount → ClusterRole → ClusterRoleBinding → InferServiceSet），由 `deploy.py` 的 `generate_yaml_infer_service_set` 根据 `user_config.json` 实例化，生成可 apply 的 `infer_service.yaml`。
3. **Replicas 双层映射**：每个 role 有两个 `replicas` 字段——
   - `role.replicas` = 实例数（controller/coordinator 固定为 1；prefill 取 `p_instances_num`；decode 取 `d_instances_num`；PD 混部时 union 取 `hybrid_instances_num`，prefill/decode 置 0）
   - `role.spec.replicas` = 单实例内的 Pod 数（主备时 controller/coordinator 为 2；prefill 取 `single_p_instance_pod_num`；decode 取 `single_d_instance_pod_num`；union 取 `single_hybrid_instance_pod_num`）
4. **JOB_NAME 动态刷新公式**：deploy.py 初始设为 `{namespace}-{InferServiceSet.metadata.name}`，pod 启动后由 CRD 注入 `INFER_SERVICE_INDEX`、`INSTANCE_INDEX`，boot.sh 据此刷新为 `{namespace}-{InferServiceSet_name}-{INFER_SERVICE_INDEX}-p/d{INSTANCE_INDEX}`（p/d 由 role 决定）。
5. **部署模式防漂移**：扩缩容 (`--update_instance_num`) 与刷新 ConfigMap (`--update_config`) 时，均以集群 ConfigMap baseline 中的 `deploy_mode` 为准；`user_config.json` 若与 baseline 不一致则报错，禁止在 update 场景下切换部署方式。
6. **共享 ConfigMap**：`infer_service_set` 与 `multi_deployment` 复用同一 `create_motor_config_configmap` 逻辑，将 `user_config.json`、boot.sh、probe 等写入 `motor-config` ConfigMap 供所有 Pod 挂载。

---

## 【关键机制与数据】

### 工作原理 — 首次部署（infer_service_set 模式）

**原文:** 读取 `user_config.json` → 根据 `infer_service_init.yaml` 与 user_config 生成 `infer_service.yaml` → `exec_all_kubectl_multi` 内先创建 ConfigMap `motor-config`，再对 `infer_service.yaml` 执行 `kubectl apply`（包含 RBAC + InferServiceSet）→ CRD controller 根据 InferServiceSet 拉起各角色 Pod。

### 工作原理 — 扩缩容（--update_instance_num）

**原文:** 从集群 ConfigMap 读取 baseline（不存在则报错）→ 校验"仅实例数变更"（`validate_only_instance_changed`，仅允许改 `p_instances_num`、`d_instances_num`、`hybrid_instances_num`）→ 重新生成 `infer_service.yaml`（PD 分离改 prefill/decode replicas；PD 混部改 union replicas）→ 用当前 user_config 刷新 ConfigMap → `kubectl apply` 后由 CRD controller 扩缩 Pod。

### 工作原理 — ConfigMap 与 Pod 挂载

**原文:** `create_motor_config_configmap` 将 `user_config.json`、boot.sh、probe 等写入 `motor-config` ConfigMap；扩缩容/CM 刷新时同时读取 baseline，确保模式与参数一致。

### 工作原理 — RBAC 字段注入

**原文:** deploy.py 会将 ServiceAccount 的 `metadata.namespace`、ClusterRoleBinding 的 `metadata.namespace` 及 `subjects[].namespace` 更新为部署 namespace（即 `motor_deploy_config.job_id`）。

### NPU 与硬件亲和性

**原文:** NPU 资源根据 `p_pod_npu_num`、`d_pod_npu_num` 配置；`nodeSelector` 根据 `hardware_type`（`800I_A2` / `800I_A3`）选择节点。

---

## 【表格解读】

### 表 1：部署模式对照

| 模式 | motor_deploy_config.deploy_mode | 说明 |
|------|--------------------------------|------|
| infer_service_set | `infer_service_set`（默认，可省略） | 仅生成并 apply `infer_service.yaml`，内含 RBAC + InferServiceSet；由 CRD controller 拉起 pod |
| multi_deployment | `multi_deployment` | 生成 controller、coordinator、engine_*、kv_pool 等多个独立 yaml，分别 apply |

**逐行解读：**
- 第一行（默认模式）：用户无需显式声明 `deploy_mode`，默认走 CRD 路线，由 MindCluster infer-operator 接管 pod 生命周期。
- 第二行（兼容模式）：保留传统多 yaml 方式，无 CRD 依赖，便于不支持 infer-operator 的环境部署。

### 表 2：典型场景与预期

| 场景 | 步骤 | 预期 |
|------|------|------|
| 首次部署（infer_service_set） | `motor_deploy_config` 中不配置或配置 `"deploy_mode": "infer_service_set"`，执行 `python3 deploy.py` | 成功；生成 `output/deployment/infer_service.yaml`；RBAC 与 InferServiceSet 被 apply；ConfigMap motor-config 存在；CRD controller 拉起 controller/coordinator/prefill/decode pod；服务能正常推理 |
| 首次部署（multi_deployment） | `motor_deploy_config` 中配置 `"deploy_mode": "multi_deployment"`，执行 `python3 deploy.py` | 成功；生成 controller、coordinator、engine_*、kv_pool 等多个 yaml；分别 apply；各 Deployment 拉起对应 pod；服务可以正常推理 |
| infer_service_set 扩容 | 调大 `p_instances_num` 或 `d_instances_num`，执行 `python3 deploy.py --update_instance_num` | 成功；重新生成 infer_service.yaml；apply 后 CRD controller 扩展 prefill/decode pod |
| infer_service_set 缩容 | 调小实例数，执行 `python3 deploy.py --update_instance_num` | 成功；InferServiceSet 中 replicas 减小；apply 后 CRD controller 回收多余 pod |
| PD 混部 CRD 扩容 | `hybrid_instances_num` 调大，执行 `python3 deploy.py --update_instance_num` | 成功；union `role.replicas` 增加；apply 后 CRD controller 扩展 union pod |
| PD 混部 CRD 缩容 | `hybrid_instances_num` 调小，执行 `python3 deploy.py --update_instance_num` | 成功；union replicas 减小；CRD controller 回收多余 union pod |
| 无 infer_service_init | 删除或移走 infer_service_init.yaml，执行 infer_service_set 模式部署 | 报错：InferServiceSet init yaml not found |
| 修改 deploy_mode 后仅刷新 CM | 首次 infer_service_set 部署后，将 user_config 中 `deploy_mode` 改为 `multi_deployment` 并执行 `--update_config` | 报错：deploy_mode 不能通过刷新 ConfigMap 修改，需重新部署 |
| 修改 deploy_mode 后扩缩容 | 首次 infer_service_set 部署后，将 user_config 中 `deploy_mode` 改为 `multi_deployment` 并执行 `--update_instance_num` | 报错：仅允许修改 p_instances_num/d_instances_num，deploy_mode 变更视为非法 |

**逐行解读：**
- 第 1–2 行：两种模式均通过 `python3 deploy.py` 触发，但产物与执行对象不同——前者 1 个 yaml，后者多 yaml。
- 第 3–4 行：PD 分离下的扩缩容针对 `p_instances_num` / `d_instances_num`，动作由 CRD controller 完成。
- 第 5–6 行：PD 混部下扩缩容作用于 union 的 `role.replicas`，即 `hybrid_instances_num`。
- 第 7 行：模板缺失时报"InferServiceSet init yaml not found"——强模板依赖。
- 第 8–9 行：明确禁止"通过 update 路径静默切换部署模式"，强制要求重新完整部署以避免状态不一致。

### 表 3：两种模式多维度对比

| 维度 | infer_service_set 模式 | multi_deployment 模式 |
|------|------------------------|------------------------|
| 输出文件 | 单个 infer_service.yaml（含 RBAC + InferServiceSet） | 多个：controller、coordinator、engine_p0～pn、engine_d0～dn、kv_pool |
| apply 对象 | RBAC + InferServiceSet | 各 Deployment、Service、RBAC 等 |
| pod 创建方 | CRD controller | kubectl apply 直接创建 Deployment |
| 扩缩容 | 更新 InferServiceSet 内 prefill/decode 各 role 的 replicas（实例数）并 apply | 对新增/删除的 engine yaml 做 apply/delete |
| 前置依赖 | 集群需安装 MindCluster infer-operator | 无 infer-operator 依赖 |

**逐行解读：**
- 输出文件维度：CRD 模式收口为 1 个 yaml，运维面更收敛；多 yaml 模式逐 engine 输出，文件数随实例数线性增长（engine_p0～pn、engine_d0～dn）。
- apply 对象维度：CRD 模式仅 apply 一个复合资源；多 yaml 模式需逐个 apply Deployment/Service/RBAC。
- pod 创建方维度：这是两种模式最核心的差异——CRD 模式 pod 生命周期由 controller 调谐，多 yaml 模式由 kubectl 直接创建。
- 扩缩容维度：CRD 模式改 spec 中 replicas 即可；多 yaml 模式需按 engine 维度 apply/delete。
- 前置依赖维度：CRD 模式有强依赖（infer-operator 必须先装），多 yaml 模式无此依赖，可作为兜底方案。

---

## 【公式解读】

**原文公式 1**（JOB_NAME 初值，deploy.py 设置）：

```
JOB_NAME = {namespace} - {InferServiceSet.metadata.name}
```

- `{namespace}`：取自 `motor_deploy_config.job_id`
- `{InferServiceSet.metadata.name}`：CRD 资源名，模板渲染时填充
- **作用**：作为 pod 启动前的初始环境变量。

**原文公式 2**（pod 启动后由 boot.sh 刷新）：

```
JOB_NAME = {namespace} - {InferServiceSet_name} - {INFER_SERVICE_INDEX} - p/d {INSTANCE_INDEX}
```

- `{namespace}`：同上
- `{InferServiceSet_name}`：CRD 资源名
- `{INFER_SERVICE_INDEX}`：CRD 注入的环境变量，表示 role 实例序号
- `p` / `d`：分别表示 prefill / decode 角色（p 取自 prefill，d 取自 decode）
- `{INSTANCE_INDEX}`：CRD 注入的环境变量，表示单实例内的 Pod 序号
- **作用**：用于服务域名构建、JOB_NAME 基等，作为推理服务在 K8s 中的唯一标识。

**原文无其他数学公式。**

---

## 【关联】

文档中明确涉及的关联模块与上下游：

1. **MindCluster infer-operator**：CRD 模式的硬性前置依赖，负责 InferServiceSet 的调谐与 pod 拉起；`multi_deployment` 模式无此依赖，可作兜底。
2. **MindIE Motor 各角色 Pod**：controller、coordinator、prefill、decode、union（PD 混部时取代 prefill/decode），均由同一 InferServiceSet 通过 role 区分。
3. **ConfigMap `motor-config`**：两种模式共用的"配置总线"，承载 `user_config.json`、boot.sh、probe；扩缩容时还需以其中 baseline 的 `deploy_mode` 为权威。
4. **RBAC 三件套**：ServiceAccount `mindie-motor-controller`、ClusterRole `mindie-controller-role`（configmaps/nodes 的 get/list/watch）、ClusterRoleBinding `mindie-controller-binding`，均在 CRD 模式下与 InferServiceSet 一同 apply。
5. **env 变量集**：`ROLE`、`JOB_NAME`、`CONTROLLER_SERVICE`、`COORDINATOR_SERVICE` 等用于 Pod 间服务发现，由 CRD controller 与 boot.sh 协同注入/刷新。
6. **multi_deployment 模式**：作为兼容路径存在，与 infer_service_set 共用 ConfigMap 与大部分 deploy.py 逻辑，但产物多 yaml、无 CRD 依赖。

> 注：原文文末标注"内部链接: (无)"，故无内部交叉链接可解析；以上关联均基于原文显式提及的模块与字段。

---

## 【使用方法】

### 启用方式

- **默认即 CRD 模式**：无需在 `user_config.json` 中显式配置 `motor_deploy_config.deploy_mode`。
- **切换到 multi_deployment**：在 `user_config.json` 的 `motor_deploy_config.deploy_mode` 中配置 `"multi_deployment"`。
- **前置条件**：集群需已安装 MindCluster infer-operator（仅 CRD 模式要求）；`examples/deployer/yaml_template/` 下 infer_service 相关模板存在且格式正确。

### 配置项（节选自原文 user_config.json 字段）

| 字段 | 取值/作用 |
|------|-----------|
| `motor_deploy_config.deploy_mode` | `infer_service_set`（默认）/ `multi_deployment` |
| `motor_deploy_config.job_id` | 作为 namespace 与 JOB_NAME 基 |
| `motor_deploy_config.image_name` | 填充 image 字段 |
| `p_instances_num` / `d_instances_num` | PD 分离时 prefill/decode 的实例数 |
| `hybrid_instances_num` | PD 混部时 union 的实例数 |
| `single_p_instance_pod_num` / `single_d_instance_pod_num` / `single_hybrid_instance_pod_num` | 单实例内 Pod 数 |
| `p_pod_npu_num` / `d_pod_npu_num` | NPU 资源配置 |
| `hardware_type` | `800I_A2` / `800I_A3`（用于 nodeSelector） |

### 命令

| 命令 | 用途 |
|------|------|
| `python3 deploy.py` | 首次部署，按 `deploy_mode` 生成并 apply yaml |
| `python3 deploy.py --update_instance_num` | 扩缩容（仅允许改实例数字段）；从 ConfigMap baseline 读取当前 `deploy_mode` |
| `python3 deploy.py --update_config` | 刷新 ConfigMap（禁止同时修改 `deploy_mode`） |

### 校验与报错（原文摘录）

- **模板缺失**：`InferServiceSet init yaml not found`
- **update 场景改 deploy_mode**：`deploy_mode` 不能通过刷新 ConfigMap 修改，需重新部署；或报"仅允许修改 p_instances_num/d_instances_num"
- **baseline 不一致**：`--update_instance_num` 通过 `validate_only_instance_changed` 校验，禁止除实例数外的修改。
