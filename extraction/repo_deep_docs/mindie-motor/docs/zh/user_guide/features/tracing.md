# Tracing能力部署

> 仓 `mindie-motor` · 路径 `docs/zh/user_guide/features/tracing.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-motor/docs/zh/user_guide/features/tracing.md

# MindIE Motor Tracing 能力部署 — 深度解读

## 【定位】

这篇文档解决如何在 MindIE Motor 推理集群管理框架中开启基于 OpenTelemetry 的分布式链路追踪（Tracing）能力，覆盖从环境变量配置、追踪采样参数配置、引擎端点配置，到 Jaeger 后端部署与可视化展示的完整流程。

---

## 【技术要点】

1. **基于 OpenTelemetry 协议**：Tracing 能力依赖第三方组件 `opentelemetry`，遵循 OTLP（OpenTelemetry Protocol）标准上报 trace 数据，可对接任意兼容 OTLP 的后端（如 Jaeger）。
2. **三模块启用**：Tracing 需在 `motor_coordinator_env`、`motor_engine_prefill_env`、`motor_engine_decode_env` 三个配置项下同时新增 3 个 OTEL 环境变量；`motor_controller_env` 和 `motor_kv_cache_store_env` 未涉及。
3. **必填环境变量**：`OTEL_SERVICE_NAME`（服务名，coordinator 为 `mindie-motor`，prefill 为 `vllm-server-p`，decode 为 `vllm-server-d`）、`OTEL_EXPORTER_OTLP_TRACES_INSECURE`（非安全协议开关，生产建议 `false`）、`OTEL_EXPORTER_OTLP_TRACES_PROTOCOL`（可选 `grpc` 或 `http/protobuf`）。
4. **协调端采样配置**：`motor_coordinator_config` 下新增 `tracer_config`，其中 `endpoint` 为**必填**；并提供 5 个采样率参数（`root_sampling_rate`、`remote_parent_sampled`、`remote_parent_not_sampled`、`local_parent_sampled`、`local_parent_not_sampled`），示例均设为 `1`（全采样）。
5. **引擎端端点配置**：vLLM prefill 与 decode 引擎的 `engine_config` 中新增 `otlp-traces-endpoint`，协议与端口需与 env.json 中 `OTEL_EXPORTER_OTLP_TRACES_PROTOCOL` 保持一致；HTTP 协议使用 `http://xx.xx.xx.xx:4318/v1/traces`，gRPC 协议使用 `grpc://xx.xx.xx.xx:4317`。
6. **配套部署 Jaeger**：通过 Jaeger 内置 OTLP receiver 接收 trace 数据（HTTP 4318、gRPC 4317），UI 通过 16686 端口访问；可执行文件启动或 Docker 容器两种方式。

---

## 【关键机制与数据】

**工作原理**：

- MindIE Motor 各组件在启动时读取 env.json 与 user_config.json 中与 OpenTelemetry 相关的配置，初始化 OTLP exporter。
- coordinator 内部依据 `tracer_config` 决定 span 的采样行为（5 个采样率参数组合形成完整采样策略），并通过 `endpoint` 将采样后的 trace 数据上报到外部 collector/后端。
- prefill/decode 引擎（vLLM）通过其 `otlp-traces-endpoint` 直接将推理请求链路 trace 导出到同一个 endpoint，实现跨组件（协调层 + 推理引擎层）的 trace 串联。
- Jaeger 通过 OTLP receiver 接收 HTTP（4318）与 gRPC（4317）两种协议的 trace 数据，存入后端存储并通过 16686 端口提供 Web UI 查询。

**端口数据（原文）**：
- OTLP HTTP：4318
- OTLP gRPC：4317
- Jaeger UI：16686

**采样率数据（原文）**：示例配置中 5 个采样参数均为 `1`，即对所有 span 进行采样。

---

## 【表格解读】

**原文无表格**。

> 备注：原文中 OTEL 环境变量与 `tracer_config` 参数以列表/JSON 形式给出，未使用 markdown 表格结构。下面以表格形式**逐字还原**这些关键配置项以便对照（内容完全来自原文，不作扩展）：

### 表 1：OTEL 环境变量（来自 env.json 示例）

| 环境变量名 | 示例取值（coordinator） | 示例取值（prefill） | 示例取值（decode） | 原文含义 |
|---|---|---|---|---|
| `OTEL_SERVICE_NAME` | `mindie-motor` | `vllm-server-p` | `vllm-server-d` | 上报数据的服务名称，根据模块名称定义 |
| `OTEL_EXPORTER_OTLP_TRACES_INSECURE` | `true` | `true` | `true` | 是否开启非安全协议，生产环境建议 `false` |
| `OTEL_EXPORTER_OTLP_TRACES_PROTOCOL` | `http/protobuf` | `http/protobuf` | `http/protobuf` | 上报协议，可选 `grpc` 或 `http/protobuf` |

### 表 2：tracer_config 参数（来自 user_config.json 示例）

| 参数 | 取值 | 含义（原文/由原文推断） |
|---|---|---|
| `endpoint` | `http://xx.xx.xx.xx:4318/v1/traces` | 必填，OTLP 上报地址；与 `OTEL_EXPORTER_OTLP_TRACES_PROTOCOL` 对应（HTTP 协议用 4318，gRPC 协议用 4317） |
| `root_sampling_rate` | `1` | 根 span 采样率（原文未给出文字说明，示例为 1） |
| `remote_parent_sampled` | `1` | 远端父 span 已被采样时的策略（原文未给出文字说明，示例为 1） |
| `remote_parent_not_sampled` | `1` | 远端父 span 未被采样时的策略（原文未给出文字说明，示例为 1） |
| `local_parent_sampled` | `1` | 本地父 span 已被采样时的策略（原文未给出文字说明，示例为 1） |
| `local_parent_not_sampled` | `1` | 本地父 span 未被采样时的策略（原文未给出文字说明，示例为 1） |

### 表 3：引擎端 otlp-traces-endpoint 配置（来自 user_config.json 示例）

| 配置项 | prefill 示例 | decode 示例 | 原文含义 |
|---|---|---|---|
| `otlp-traces-endpoint` | `http://xx.xx.xx.xx:4318/v1/traces` | `http://xx.xx.xx.xx:4318/v1/traces` | vLLM 引擎 OTLP 上报地址，填写方法同 coordinator 的 `endpoint` |

### 表 4：推理引擎部署关键参数（来自 user_config.json 示例，原文已给出）

| 参数 | prefill 取值 | decode 取值 |
|---|---|---|
| `engine_type` | `vllm` | `vllm` |
| `served_model_name` | `qwen3-8B` | `qwen3-8B` |
| `model` | `/mnt/weight/qwen3_8B` | `/mnt/weight/qwen3_8B` |
| `gpu_memory_utilization` | `0.9` | `0.9` |
| `data_parallel_size` | `2` | `2` |
| `tensor_parallel_size` | `2` | `2` |
| `pipeline_parallel_size` | `1` | `1` |
| `enable_expert_parallel` | `false` | `false` |
| `data_parallel_rpc_port` | `9000` | `9000` |
| `kv_role` | `kv_producer` | `kv_consumer` |

> 说明：上述表 1-4 中除"原文含义"列中由原文文字直接转述的部分以外，其余细节说明保持原文表述，未做超出原文档范围的解释。

---

## 【公式解读】

**原文无公式**。

---

## 【关联】

- **快速开始指南**：`../quick_start.md`（文档中引用 2 次）——本文中 env.json 与 user_config.json 的完整配置示例均以"快速开始"文档中的实例作为基线，新增 OTEL 相关字段，因此两份文档在配置结构上保持一致，仅在本特性下增量新增字段。
- **OpenTelemetry 官方文档**：作为底层能力来源，本文未对其内部机制做展开，仅作为外部参考。
- **Jaeger**：作为可选的 trace 后端可视化组件，与 OTLP 协议对接，端口固定（HTTP 4318、gRPC 4317、UI 16686）。
- **下游模块**：本特性涉及三个核心模块 `motor_coordinator`、`motor_engine_prefill`、`motor_engine_decode`，通过 trace 串联实现端到端请求链路观测；`motor_controller`、`motor_kv_cache_store` 未在本文档启用范围内。
- **推理引擎**：vLLM prefill（kv_producer）与 decode（kv_consumer）通过 `otlp-traces-endpoint` 将 span 上报到同一 collector，可在 Jaeger 中查看跨 KV cache 传输链路的 trace。

---

## 【使用方法】

### 启用方式（步骤化，原文给出）

1. **修改 env.json**：在 `motor_coordinator_env`、`motor_engine_prefill_env`、`motor_engine_decode_env` 下分别新增 `OTEL_SERVICE_NAME`、`OTEL_EXPORTER_OTLP_TRACES_INSECURE`、`OTEL_EXPORTER_OTLP_TRACES_PROTOCOL` 三个环境变量（参考"表 1"）。
2. **修改 user_config.json**：
   - 在 `motor_coordinator_config` 下新增 `tracer_config`（参考"表 2"），其中 `endpoint` **必填**。
   - 在 `motor_engine_prefill_config` 与 `motor_engine_decode_config` 的 `engine_config` 下新增 `otlp-traces-endpoint`（参考"表 3"）。
3. **执行 deploy.py 部署服务**：

```bash
cd examples/deployer
# 方式一：指定配置目录（推荐）
python deploy.py --config_dir ../infer_engines/vllm

# 方式二：单独指定配置文件
python deploy.py --user_config_path ../infer_engines/vllm/user_config.json --env_config_path ../infer_engines/vllm/env.json
```

4. **部署 Jaeger 后端**（用于可视化 trace）：

```bash
./jaeger --set receivers.otlp.protocols.http.endpoint=0.0.0.0:4318 --set receivers.otlp.protocols.grpc.endpoint=0.0.0.0:4317 &
```

也可使用 Docker 方式部署 Jaeger（原文指引参考官网，未给出具体命令）。

5. **查看 trace**：浏览器访问对应 IP 的 **16686** 端口打开 Jaeger UI。

### 关键配置项（汇总）

- **env.json**：`OTEL_SERVICE_NAME`、`OTEL_EXPORTER_OTLP_TRACES_INSECURE`、`OTEL_EXPORTER_OTLP_TRACES_PROTOCOL`
- **user_config.json coordinator**：`tracer_config.endpoint`（必填）、`root_sampling_rate`、`remote_parent_sampled`、`remote_parent_not_sampled`、`local_parent_sampled`、`local_parent_not_sampled`
- **user_config.json engine**：`otlp-traces-endpoint`
- **协议与端口对应关系**（原文给出）：
  - `http/protobuf` → `http://xx.xx.xx.xx:4318/v1/traces`
  - `grpc` → `grpc://xx.xx.xx.xx:4317`

## 图文联合解读

- `Snipaste_2026-03-31_20-59-16.jpg`: ## 图文联合解读

**1) 图中内容**
Jaeger UI 搜索界面：左侧筛选 `Service=mindie-motor`、`Operation=all`、Tag `http.status_code=200 error=true`、Limit 1500；顶部为按时间分布的耗时散点图（3.3s–10.5s）；列表显示 **1500 条** `mindie-motor: CDP_Decode_stream` 链路，每条均含 `4 Spans`：`mindie-motor(2)` + `vllm-server-d(1)` + `vllm-server-p(1)`，耗时约 6.5–6.7s。

**2) 技术结论**
OTel 链路打通成功：单次请求在 coordinator、prefill 引擎、decode 引擎三个服务间形成完整 Span，且能按 TraceID 聚合、按服务名区分，证明 OTLP 上报链路通畅。

**3) 与文档论点的关系**
可视化印证 env.json 中为 `motor_coordinator_env` / `motor_engine_prefill_env` / `motor_engine_decode_env` 配置的 `OTEL_SERVICE_NAME`（mindie-motor / vllm-server-p / vllm-server-d）已生效，端到端 Tracing 能力部署验证完成。
- `Snipaste_2026-03-31_20-59-24.jpg`: 图示解读:
1. **图中内容**:Jaeger UI展示了一次流式请求的调用链trace,mindie-motor(协调器)为根span,嵌套vllm-server-d(decode)和vllm-server-p(prefill)两个子span;Tags记录TTFT=2005ms、`stream=true`、`server.path=v1/chat/completions`;SDK为opentelemetry-python 1.39.1。
2. **技术结论**:配置生效后,3个服务、4个span、3层调用深度被完整采集,验证了跨模块追踪链路打通。
3. **与文档关系**:佐证env.json注入的`OTEL_SERVICE_NAME`、`OTEL_EXPORTER_OTLP_TRACES_PROTOCOL`参数使PD分离架构中coordinator/prefill/decode三端可观测。
