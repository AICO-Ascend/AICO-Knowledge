# 主备倒换特性

> 仓 `mindie-motor` · 路径 `docs/zh/user_guide/features/fault_tolerance/standby.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-motor/docs/zh/user_guide/features/fault_tolerance/standby.md

# 主备倒换特性文档深度解读

## 【定位】
本文档描述 mindie-motor 推理集群管理框架中基于 ETCD 分布式锁实现的高可用机制，覆盖 **Controller 主备倒换**与 **Coordinator 主备倒换**两类组件的主备选举、部署与配置全流程。

---

## 【技术要点】

1. **核心机制**：两个组件（Controller、Coordinator）均通过 ETCD 分布式锁实现主备身份选举，开启开关后初始化阶段拉起两个实例，备用实例在主实例故障后"在设定时间间隔后自动接管工作"。
2. **ETCD 服务端要求**（原文限制约束）：
   - ETCD 版本必须为 **v3.6**
   - 至少 **3 个副本**以保证可靠性
   - 默认端口 **2379**
   - 域名格式 `etcd.{namespace}.svc.cluster.local`
   - Controller 与 Coordinator 主备可**共用一套 ETCD**；多套大 EP 集群也可共用一套，通过 namespace 区分
3. **特性开关**：在 `user_config.json` 的 `motor_controller_config.standby_config.enable_master_standby` 中将值设为 `true` 开启，设为 `false` 关闭。
4. **节点布局约束**：主、备 Controller（或 Coordinator）节点**不建议部署在同一台节点**上。
5. **K8s 心跳调优（可选）**：将 kube-controller-manager 的 `node-monitor-grace-period` 参数修改为 **20s**，用于在硬件故障（如机器重启）场景下加快 Pod 状态感知、缩短业务恢复时间。
6. **TLS 安全（可选）**：依赖 ETCD 分布式锁时涉及 POD 间通信，建议使用 CA 证书做双向认证；可在 `tls_config.etcd_tls_config` 中通过 `enable_tls=true` 开启，并指定 `ca_file/cert_file/key_file/passwd_file/tls_crl` 路径；不开启则明文传输。

---

## 【关键机制与数据】

### Controller 主备选举数据流

- **初始化阶段**：开启 `enable_master_standby=true` 后，系统拉起两个 Controller 实例。
- **选举过程**：两个实例通过 ETCD 分布式锁竞争决定主备身份。
- **日志识别**：原文中用于判断主节点的日志关键字为 `"Role changed from standby to master"`。
- **健康度识别**：原文中通过 `kubectl get pod -A -owide` 查看，**有且仅有一个 Controller pod 的 READY 状态为 1/1**，该节点即为主 Controller 节点。

### Coordinator 主备选举数据流
机制与 Controller 相同：开启开关后初始化拉起两个 Coordinator，通过 ETCD 分布式锁竞争确认主备身份，原文未给出 Coordinator 专属的主节点识别日志关键字或 Pod READY 校验方式。

### TLS 证书配置数据

- 物理机证书生成路径（示例）：`/home/{用户名}/auto_gen_ms_cert`
- Controller 容器内挂载路径：`/usr/local/Ascend/pyMotor/conf/security/etcd`
- Coordinator 容器内挂载路径：`/usr/local/Ascend/pyMotor/conf/security/etcd`
- 配置项字段：`enable_tls`、`ca_file`、`cert_file`、`key_file`、`passwd_file`、`tls_crl`

### 业务访问入口

- **Controller 主节点方式**：`http://PodIP:1025`（仅 READY 1/1 的主节点可接收推理请求）
- **NodePort 方式**：物理机 IP + 31015，需与 `coordinator_template.yaml`（multi_deployment 场景）或 `infer_service_template.yaml`（CRD 场景）中的 `mindie-motor-coordinator-infer` 的 `nodePort` 端口一致

---

## 【表格解读】
**原文无表格。** 文档中涉及参数的地方均以 YAML/JSON 代码片段形式呈现，未提供独立的参数对照表。

---

## 【公式解读】
**原文无公式。** 文档中不包含任何数学公式或伪代码表达式。

---

## 【关联】

根据文末内部链接信息：

- **主备倒换特性设计文档**（`../../../design/fault_tolerance/standby.md`）：本文档在两处明确指向该设计文档（Controller 主备介绍处与 Coordinator 主备介绍处均写有"了解主备详细设计请参考"），用于展开选举算法的内部实现细节，本文作为面向用户的部署/使用指南存在。

文档内还通过锚链接引用了以下子章节（位于同一文档）：
- `#生成etcd安全证书-etcd集群部署可选`：CA 证书生成方法，Controller 与 Coordinator 两节均引用。
- `#部署etcd服务端`：ETCD 服务端部署方法，Controller 与 Coordinator 两节均引用。

可推断的上下游关系：
- 上游依赖：ETCD v3.6 集群（需自行部署并保证 3 副本）。
- 部署前置：`examples/deployer` 目录下的 vLLM 部署脚本（`deploy.py --config_dir`）。
- 关联模板：`deployment/controller_init.yaml`、`examples/deployer/yaml_template/coordinator_template.yaml`（multi_deployment 场景）、`examples/deployer/yaml_template/infer_service_template.yaml`（CRD 场景）。

---

## 【使用方法】

### 启用 Controller 主备倒换

1. **可选：生成 ETCD 安全证书**（用于双向认证 TLS），挂载至 Controller 容器：
   ```yaml
   volumeMounts:
     - name: controller-ca
       mountPath: /usr/local/Ascend/pyMotor/conf/security/etcd
   volumes:
     - name: controller-ca
       hostPath:
         path: /home/{用户名}/auto_gen_ms_cert
         type: Directory
   ```
2. **可选：开启 TLS**：在 `user_config.json` 设置 `tls_config.etcd_tls_config.enable_tls=true` 并配置 `ca_file/cert_file/key_file/passwd_file/tls_crl`。
3. **开启特性**（`user_config.json`）：
   ```json
   "motor_controller_config": {
     "standby_config": { "enable_master_standby": true }
   }
   ```
4. **可选：自定义 ETCD**：
   ```json
   "motor_controller_config": {
     "standby_config": { "enable_master_standby": true },
     "etcd_config": {
       "etcd_host": "etcd.default.svc.cluster.local",
       "etcd_port": 2379
     }
   }
   ```
5. **可选：调优 K8s 心跳**：编辑 `/etc/kubernetes/manifests/kube-controller-manager.yaml`，将 `--node-monitor-grace-period=20s` 加入 kube-controller-manager 启动参数，执行 `systemctl restart kubelet.service`，再通过 `kubectl describe pod ... | grep node-monitor-grace-period` 验证输出 `--node-monitor-grace-period=20s`。
6. **启动 vLLM**：
   ```bash
   cd examples/deployer
   python deploy.py --config_dir ../infer_engines/vllm
   ```
   或：
   ```bash
   python deploy.py --user_config_path ../infer_engines/vllm/user_config.json \
                    --env_config_path ../infer_engines/vllm/env.json
   ```
7. **主节点校验**：`kubectl get pod -A -owide` 中 READY 1/1 的 Controller Pod 即为主节点；日志中含 `"Role changed from standby to master"` 也可作为判定依据。

### 启用 Coordinator 主备倒换

1. **可选：生成 ETCD 安全证书**，挂载至 Coordinator 容器（在 `examples/deployer/yaml_template/coordinator_template.yaml` 中添加 `coordinator-ca` volume）：
   ```yaml
   volumeMounts:
     - name: coordinator-ca
       mountPath: /usr/local/Ascend/pyMotor/conf/security/etcd
   volumes:
     - name: coordinator-ca
       hostPath:
         path: /home/{用户名}/auto_gen_ms_cert
         type: Directory
   ```
2. **可选：K8s 心跳调优**步骤与 Controller 完全相同（修改 `node-monitor-grace-period=20s`）。
3. ETCD 部署、TLS 配置、`enable_master_standby=true` 开关等步骤与 Controller 一致，可共用同一套 ETCD 集群。

### 验证请求示例
```bash
#!/bin/bash
url="http://{物理机IP地址}:31015/v1/chat/completions"
data='{
    "model": "deepseek",
    "max_tokens": 10,
    "messages": [{"role": "user", "content": "你是谁"}]
}'
curl  $url -X POST  -d "$data"
```
成功响应中 `message.content` 字段将返回模型输出文本，表示服务启动成功。
