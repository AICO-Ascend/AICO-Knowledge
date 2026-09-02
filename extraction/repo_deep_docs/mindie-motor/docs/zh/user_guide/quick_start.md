# 快速入门

> 仓 `mindie-motor` · 路径 `docs/zh/user_guide/quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-motor/docs/zh/user_guide/quick_start.md

# MindIE Motor 快速入门文档深度解读

## 【定位】

本文档是 MindIE Motor 框架的**PD（Prefill-Decode）分离推理服务快速部署入门指南**，以 Atlas 800I A2 推理服务器 + Qwen3-8B 模型 + P/D 各 1 实例为最小化场景，端到端演示从环境准备、镜像获取、配置编辑、K8s 部署到 curl 推理验证的完整闭环流程。

---

## 【技术要点】

1. **PD 分离部署架构**：将 Prefill 与 Decode 两个推理阶段分别实例化到不同硬件资源上，通过 KV Cache 传输实现协作推理，性能优于单阶段串行执行。
2. **硬件支持范围**：明确支持 Atlas 800I A2 推理服务器、Atlas 800I A3 超节点服务器和 Atlas 850 超节点服务器三类昇腾硬件。
3. **镜像获取双路径**：方式一是从昇腾官方镜像仓库（AscendHub）按设备型号下载 `motor` 镜像；方式二是基于 vllm-ascend 自制 MindIE Motor 镜像（参考 build_motor_image_from_vllm_ascend）。
4. **配置文件双重来源**：① 典配模式——`examples/infer_engines/vllm/models/<模型名>/<硬件型号>/` 已预设 `user_config.json` 与 `env.json`，仅需少量字段适配；② 自动生成——`deploy.py --mode general_config --deploy-scenario separate --hardware-type A2` 将 vllm-ascend 社区脚本一键转换为 Motor 配置。
5. **关键并行参数**：Prefill/Decode 实例均配置 `tensor_parallel_size=2`、`pipeline_parallel_size=1`、`data_parallel_size=1`、`p_pod_npu_num=4`、`d_pod_npu_num=4`，即每个 Pod 使用 4 张 NPU 卡，张量并行度为 2。
6. **KV Cache 跨实例传输**：通过 `MooncakeConnectorV1` 连接器（`kv_connector`）、NPU 设备缓冲（`kv_buffer_device: "npu"`）实现 P→D 的 KV 传输，角色分别为 `kv_producer`（P 端产出）和 `kv_consumer`（D 端消费），通信端口为 `30001`。
7. **K8s 命名空间约束**：`kubectl create ns` 创建的 namespace 名称必须与 `user_config.json` 的 `job_id` 字段一致（默认 `mindie-motor`），这是部署器强校验逻辑。
8. **服务生命周期管理**：部署用 `python3 deploy.py --config_dir ../infer_engines/vllm`；停止用 `bash delete.sh <namespace>`；日志收集用 `vim log_collect/log_config.ini` 改 namespace 后 `bash show_log.sh`。

---

## 【关键机制与数据】

### 工作原理：PD 分离 + KV 跨实例传输

**原文**："模型推理的 Prefill 阶段和 Decode 阶段分别实例化部署在不同的硬件资源上进行推理，提升推理性能"

**数据流路径**：
1. **请求入口**：客户端通过 `http://127.0.0.1:31015/v1/chat/completions`（K8s NodePort 端口 31015）发送 OpenAI 格式的 chat completion 请求。
2. **Prefill 实例**（`motor_engine_prefill_config`）：接收 prompt，执行全量 prefill 计算，将产生的 KV Cache 通过 `MooncakeConnectorV1` 以 `kv_producer` 角色写入共享缓冲（`kv_buffer_device: "npu"`，端口 30001）。
3. **Decode 实例**（`motor_engine_decode_config`）：以 `kv_consumer` 角色从相同端口 30001 拉取 KV Cache，执行增量 decode 推理，逐 token 流式返回。
4. **协调层**：原文中 `motor_controller_config` 与 `motor_coordinator_config` 在 Qwen3-8B 示例下配置为空 `{}`，表明轻量场景下由默认行为驱动调度；典型输出端到端流式 token（如 `<think>`、`\n`、`Okay` 等）。

### 性能/规模数据（原文显式数字）

| 类别 | 原文数字 | 含义 |
|---|---|---|
| 实例规模 | `p_instances_num: 1`, `d_instances_num: 1` | 最小 P/D 各 1 实例演示 |
| NPU 分配 | `p_pod_npu_num: 4`, `d_pod_npu_num: 4` | 每个 Pod 占用 4 张 NPU |
| 张量并行 | `tensor_parallel_size: 2` | 模型按 2 路 TP 切分 |
| 数据并行 | `data_parallel_size: 1` | 不启用 DP |
| 流水线并行 | `pipeline_parallel_size: 1` | 不启用 PP |
| 最大序列长度 | `max_model_len: 2048` | 上下文+生成长度上限 2048 |
| GPU 显存利用率 | `gpu_memory_utilization: 0.9` | KV Cache 预留 90% 显存 |
| KV 端口 | `kv_port: "30001"` | P/D 间 KV 传输端口 |
| HCCL 缓冲区 | `HCCL_BUFFSIZE: 200` | 集合通信 buffer 大小 200（单位由 HCCL 解释） |
| OMP 线程数 | `OMP_NUM_THREADS: 100` | OpenMP 线程数上限 |
| 推理端口 | 31015 | K8s 暴露给客户端的 chat API 端口 |
| 演示响应 | `max_tokens: 36` | curl 测试最大生成 36 token |

---

## 【表格解读】

**原文无表格**（文档以 JSON 配置块和命令为主，无 markdown 表格）。

但从 `user_config.json` 中可抽取一份等效的**关键配置参数表**（按功能模块整理，原文字段逐字保留）：

| 配置块 | 关键字段 | 原文字面值 | 作用 |
|---|---|---|---|
| `motor_deploy_config` | `p_instances_num` | `1` | Prefill 实例数量 |
| `motor_deploy_config` | `d_instances_num` | `1` | Decode 实例数量 |
| `motor_deploy_config` | `single_p_instance_pod_num` | `1` | 每个 P 实例的 Pod 数 |
| `motor_deploy_config` | `single_d_instance_pod_num` | `1` | 每个 D 实例的 Pod 数 |
| `motor_deploy_config` | `p_pod_npu_num` | `4` | P Pod 使用的 NPU 数 |
| `motor_deploy_config` | `d_pod_npu_num` | `4` | D Pod 使用的 NPU 数 |
| `motor_deploy_config` | `image_name` | `mindie-motor-vllm:dev-26.1.0.B050-800I-A2-py311-Ubuntu24.04-lts-aarch64`（示例） | K8s 拉取的镜像全名 |
| `motor_deploy_config` | `job_id` | `mindie-motor` | K8s namespace 名 |
| `motor_deploy_config` | `hardware_type` | `800I_A2`（A2 推理服务器） | 硬件标识枚举 |
| `motor_deploy_config` | `weight_mount_path` | `/mnt/weight/qwen3_8B`（示例） | 权重文件挂载路径 |
| `motor_engine_prefill_config.engine_type` | — | `vllm` | 推理引擎选 vLLM |
| `motor_engine_prefill_config.engine_config` | `served_model_name` | `qwen3-8B` | API 暴露的模型名 |
| 同上 | `gpu_memory_utilization` | `0.9` | KV/P 权重显存占比 |
| 同上 | `tensor_parallel_size` | `2` | TP 切分路数 |
| 同上 | `pipeline_parallel_size` | `1` | PP 切分层数 |
| 同上 | `data_parallel_size` | `1` | DP 副本数 |
| 同上 | `data_parallel_rpc_port` | `9000` | DP 协调 RPC 端口 |
| 同上 | `enable_expert_parallel` | `false` | MoE 专家并行开关 |
| 同上 | `enforce-eager` | `true`（仅 P 端） | 强制 eager 模式 |
| 同上 | `max_model_len` | `2048` | 最大序列长度 |
| `kv_transfer_config` | `kv_connector` | `MooncakeConnectorV1` | KV 传输连接器 |
| `kv_transfer_config` | `kv_buffer_device` | `npu` | KV buffer 放 NPU |
| `kv_transfer_config` | `kv_role` | `kv_producer`（P）/ `kv_consumer`（D） | P/D 端 KV 角色 |
| `kv_transfer_config` | `kv_parallel_size` | `1` | KV 传输并行度 |
| `kv_transfer_config` | `kv_port` | `30001` | KV 传输 TCP 端口 |
| `kv_transfer_config` | `engine_id` | `0` | 引擎实例编号 |
| `kv_transfer_config` | `kv_rank` | `0` | 当前进程在 KV 传输中的 rank |

`env.json` 中的环境变量表：

| 变量 | 值 | 作用域 | 作用 |
|---|---|---|---|
| `CANN_INSTALL_PATH` | `/usr/local/Ascend` | `motor_common_env` | CANN 昇腾计算栈安装路径 |
| `MOTOR_LOG_ROOT_PATH` | `/root/ascend/log` | `motor_common_env` | Motor 业务日志根目录 |
| `HCCL_BUFFSIZE` | `200` | P/D 引擎 | 集合通信（HCCL）缓冲区大小 |
| `PYTORCH_NPU_ALLOC_CONF` | `expandable_segments:True` | P/D 引擎 | NPU 显存分配策略：启用可扩展段 |
| `HCCL_OP_EXPANSION_MODE` | `AIV` | P/D 引擎 | HCCL 算子下发模式选 AIV |
| `OMP_PROC_BIND` | `false` | P/D 引擎 | OpenMP 进程绑定关闭 |
| `OMP_NUM_THREADS` | `100` | P/D 引擎 | OpenMP 线程数上限 100 |
| `ASCEND_BUFFER_POOL` | `0:0` | P/D 引擎 | 昇腾 buffer pool 设备绑定 |

典配模型目录（原文已列举）：`deepseek_v3.1` / `deepseek_v4_flash` / `deepseek_v4_pro` / `glm_5` / `glm_5.1` / `qwen_235b`，硬件子目录为 `A2` / `A3` / `A5`（以实际目录为准）。

---

## 【公式解读】

**原文无公式**（文档不涉及数学公式或伪代码算法，仅包含 Shell/Python/JSON 命令与配置）。

---

## 【关联】

本文档作为 quick start，是 MindIE Motor 文档体系的**总入口**，与以下模块/文档存在明确上下游关系：

| 关联文档 | 关联性质 | 关系描述 |
|---|---|---|
| `./deployment/k8s/pd_disaggregation_deployment.md` | **下游详细手册** | 本文开篇即指向它"如需详细的 PD 分离部署指导，请参考"——本文档是该详细手册的最小化前置体验版 |
| `./features/pd_disaggregation.md` | **特性原理文档** | "什么是 PD 分离？"一节直接跳转，补充 Prefill/Decode 解耦的原理与价值 |
| `./environment_preparation.md` | **前置依赖文档** | "环境要求"中"已完成环境准备的服务器"作为最低门槛条件 |
| `./maintenance/build_motor_image_from_vllm_ascend.md` | **镜像自制文档** | "镜像准备"方式二的自制流程详细说明 |
| `../../../examples/infer_engines/vllm/models/README.md` | **配置自动生成详细指导** | "自动生成"配置路径下挂载，展开 deploy.py config_tool 的完整步骤 |
| `./configuration/config_reference.md` | **全量参数字典** | `user_config.json` 5 项 `xxxxxx` 字段含义的总参考，被原文用"如需了解各字段含义可参考"明确指向 |
| `../../../examples/deployer/README.md` | **部署工具说明** | "启动与终止服务"中 `deploy.py` 更多参数与用法的文档化入口 |

**架构关联图（基于原文行文路径推断）**：

```
[昇腾镜像仓库 AscendHub / 自制 build] → MindIE Motor 镜像
                                              ↓
[环境准备 environment_preparation] → 硬件服务器（Atlas 800I A2/A3/A5）
                                              ↓
[examples/deployer/deploy.py] ← user_config.json + env.json
        ↓                          ↑
[典配 models/<模型>/<硬件>/]   [config_tool 自动生成]
        ↓
kubectl apply → K8s namespace(job_id) → P Pod + D Pod
        ↓                              ↑
[KV 30001: kv_producer → kv_consumer via MooncakeConnectorV1]
        ↓
curl :31015/v1/chat/completions → 流式响应
```

---

## 【使用方法】

> 以下命令/参数均直接摘自原文，按部署流程顺序组织。

### 1. 模型准备（原文有）

```bash
chmod -R 755 /mnt/weight
```

### 2. 镜像拷贝（原文有）

```bash
IMAGE="<镜像名或镜像ID>"
cid=$(docker create "$IMAGE")
docker cp "$cid:/tmp/motor/examples" ./examples
docker rm "$cid"
```

### 3. 配置生成三条路径（原文有）

- **典配**：`examples/infer_engines/vllm/models/<模型名>/<硬件型号>/` 直接取 `user_config.json` + `env.json`
- **自动生成**：
  ```bash
  python3 deploy.py --mode general_config --deploy-scenario separate --hardware-type A2
  ```
  输出在 `examples/deployer/config_tool/output_config/`
- **手工编辑**：进入 `examples/deployer/`，分别 `vim ../infer_engines/vllm/user_config.json` 和 `vim ../infer_engines/vllm/env.json`

### 4. 必改字段（原文标 "xxxxxx"）

`user_config.json` 中 5 项必须修改：
- `motor_deploy_config.image_name`（镜像全名）
- `motor_deploy_config.hardware_type`（`800I_A2` / `800I_A3`）
- `motor_deploy_config.weight_mount_path`（如 `/mnt/weight/qwen3_8B`）
- `motor_engine_prefill_config.engine_config.model`（如 `/mnt/weight/qwen3_8B`）
- `motor_engine_decode_config.engine_config.model`（同上）

### 5. 创建 namespace（原文有）

```bash
kubectl create ns mindie-motor
```
> 必须与 `user_config.json` 中 `job_id` 一致。

### 6. 部署 / 停止（原文有）

```bash
cd examples/deployer
python3 deploy.py --config_dir ../infer_engines/vllm
```
停止：
```bash
bash delete.sh mindie-motor
```

### 7. 日志收集（原文有）

```bash
vim log_collect/log_config.ini   # 把 name_space 改为 mindie-motor
bash show_log.sh
```
> 日志落盘至 `examples/deployer/log_collect/log`，持续刷新。

### 8. 推理验证（原文有）

```bash
curl -X POST http://127.0.0.1:31015/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d '{
        "model": "qwen3-8B",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "who are you?"}
        ],
        "max_tokens": 36,
        "stream": true
    }'
```
> 出现 `{"detail":"Service is not available"}` 表示未就绪，需等待；回显 `data: {...}` 流式 JSON 并以 `data: [DONE]` 结尾表示就绪。

### 9. 原始未涉及项

- **TLS / HTTPS 配置**：原文未涉及
- **多机多卡（超过 1 台服务器）配置**：原文未涉及
- **Metrics / Prometheus 接入**：原文未涉及
- **灰度升级 / 滚动更新策略**：原文未涉及
- **CANN 版本兼容矩阵**：原文未涉及（仅在示例镜像 tag 中体现 `B050` 等版本字段）
