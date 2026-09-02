# MindIE Motor 可观测性栈 · 服务拉起与停止指导

> 仓 `mindie-motor` · 路径 `examples/features/observability/stack/SERVICE_GUIDE.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-motor/examples/features/observability/stack/SERVICE_GUIDE.md

# MindIE Motor 可观测性栈 · 服务拉起与停止指导 深度解读

## 【定位】
这篇文档解决**在已部署 MindIE Motor 的节点上,如何完整地拉起、验收、停止由 Prometheus + Grafana + Tempo + OTel Collector + Loki 组成的可观测性栈**,并明确指出需要事先在 MindIE Motor 侧(Coordinator/Engine)做的配套配置,使各看板(Tempo 链路、引擎性能剖析、KV 缓存指标等)能产出数据。

---

## 【技术要点】

1. **栈模式与拓扑**:默认 `full` 模式(对应 Compose `--profile full`)拉起 Grafana + Prometheus + Tempo + OTel Collector + Loki + node-exporter + cadvisor;可切换 `--minimal` 仅拉 Grafana/Prometheus/Tempo/OTel Collector;可选 `--profile npu` 追加 Ascend `npu-exporter`;无 Docker 时用 `--native` 走原生二进制。
2. **拉镜像策略**:`start.sh` 默认执行 `docker compose up -d --pull missing --no-build`,通过 `OBS_COMPOSE_PULL`(`missing`/`never`/`always`)与 `OBS_COMPOSE_BUILD`(`0`/`1`)覆盖。
3. **核心版本号(原文默认 tag)**:`grafana/grafana:11.3.0`、`prom/prometheus:v2.55.1`、`grafana/tempo:2.6.1`、`otel/opentelemetry-collector-contrib:0.115.1`;额外 full 模式:`grafana/loki`、`prom/node-exporter`、`gcr.io/cadvisor/cadvisor`。
4. **Tracing 接入(4318 端口)**:在 MindIE Motor 侧 `env.json` 注入 `OTEL_SERVICE_NAME`、`OTEL_EXPORTER_OTLP_TRACES_PROTOCOL=http/protobuf`、`OTEL_EXPORTER_OTLP_TRACES_INSECURE=true`;`user_config.json` 将 Coordinator `tracer_config.endpoint` 与引擎 `engine_config.otlp-traces-endpoint` 指向 `http://<obs-host>:4318/v1/traces`。
5. **Profiling 接入**:依赖 `ms_service_metric`(Python≥3.10 + pyyaml + prometheus-client + posix_ipc),vLLM 通过 `entry_points` 自动适配;Engine 启动前需设 `PROMETHEUS_MULTIPROC_DIR=/dev/shm/vllm_metrics`,ready 后用 `ms-service-metric on/off/restart/status` 控制。
6. **三阶段代理分工**:`kubectl`/`discover-targets.py` 阶段**关代理**(脚本 `_kubectl_env()` 会剔除);`docker pull`/`compose pull` 阶段**当前 shell 需开** `HTTP_PROXY`;容器内 Grafana/Prometheus/Tempo 互访**已禁用代理**,Compose 已清空 Grafana 的 `HTTP_PROXY` 并设置 `NO_PROXY=prometheus,tempo`。Native runtime 另设 `PROXY_SH`(dotenv 文件路径)用于下载二进制,**不影响 Docker 与 kubectl**。

---

## 【关键机制与数据】

- **整体流程(原文):** `前提条件检查 → 准备镜像(联网拉取) → 拉起服务(launch.sh) → 验收 → 停止服务(stop.sh)`。
- **网络可达性(原文):** 观测机到 Coordinator/Engine 的 **NodePort**,或经主机端口转发的 **PodIP** 可达。
- **Pod 就绪条件(原文):** 目标 namespace 内 Coordinator、Engine(含 `vllm-p0` / `vllm-d0` 等命名)Pod 已处于 Running。
- **状态文件(原文):** `generated/discovered.env`,切换 `mindie-*` 等不同环境时必须先 `./stop.sh` 再 `./launch.sh`,否则会复用旧 namespace 的 discovered.env。
- **Controller metrics 不使用(原文):** 当前方案**不使用 Controller 的 metrics 接口**,`observability_enable`、`1027` 端口等无需配置。
- **OTLP HTTP 端口(原文):** `4318` 为栈内 OTel Collector 的 OTLP HTTP 端口。
- **主机端口转发(原文):** `MOTOR_PORT_FORWARD_BASE` 默认 `19000`,Docker 模式下用于 PodIP 桥接转发时的主机起始端口。
- **Grafana 管理员默认(原文):** `GF_SECURITY_ADMIN_USER=motor`、`GF_SECURITY_ADMIN_PASSWORD=motor`。
- **代理日志(原文):** Native 模式启动日志 `[native] loaded proxy config: ...` 表示 `PROXY_SH` 已加载;路径不存在或为空则跳过。
- **Discover-targets(原文):** 镜像拉取脚本为 `scripts/discover-targets.py`,需 `python3`;`_kubectl_env()` 会主动剔除代理环境变量。

> 文档本身**未给出**性能数据(采集频率、采样率、QPS、存储保留期等),也**未给出** Grafana 看板的具体指标列表——后者指向 `GRAFANA_GUIDE.md`。

---

## 【表格解读】

### 表 1:运行环境要求(原文 §1.1)

| 项 | 要求 |
|----|------|
| 工作目录 | 进入仓库内 `examples/features/observability/stack` |
| Python | 已安装 `python3`(用于运行 `scripts/discover-targets.py`) |
| Kubernetes | 能访问目标集群 API,`kubectl get pods -n <namespace>` 可正常返回 |
| Docker(推荐) | 安装 Docker,且支持 Docker Compose **v2**(`docker compose version` 可用);无 Docker 时可用 `--native` 走原生二进制 |
| 网络 | 观测机到 MindIE Motor Coordinator / Engine 的 **NodePort**,或经主机端口转发的 **PodIP** 可达 |

**解读:** 这是拉起栈之前机器与集群侧的硬性前提。其中 Docker Compose **v2**(不是 `docker-compose` v1)是硬门槛;Python 仅需 `python3` 用于目标发现脚本;网络一项强调两种可达方式(NodePort 直连或 PodIP 主机端口转发),二者择一即可。

### 表 2:.env 主要变量(原文 §1.3)

| 变量 | 说明 |
|------|------|
| `REGISTRY_PREFIX` | 镜像前缀,与内网 Harbor 一致;留空则从 Docker Hub 拉取 |
| `GRAFANA_VERSION` / `PROMETHEUS_VERSION` / `TEMPO_VERSION` / `OTEL_COLLECTOR_VERSION` / `LOKI_VERSION` | 各组件镜像版本 |
| `OBS_STACK_MODE` | 栈模式,默认 `full`;也可在命令行用 `--minimal` / `--full` 覆盖 |
| `GF_SECURITY_ADMIN_USER` / `GF_SECURITY_ADMIN_PASSWORD` | Grafana 管理员账号 / 密码(默认 `motor` / `motor`) |
| `GRAFANA_PORT` / `PROMETHEUS_PORT` / `TEMPO_QUERY_PORT` / `OTEL_GRPC_PORT` / `OTEL_HTTP_PORT` / `LOKI_PORT` | 主机侧服务端口 |
| `MOTOR_PORT_FORWARD_BASE` | Docker 需要 PodIP 桥接转发时使用的起始主机端口(默认 `19000`) |
| `PROXY_SH` | **可选**。Native runtime 从 GitHub / Grafana CDN 下载二进制时使用的代理配置文件路径;留空则不加载 |

**解读:** `.env` 控制镜像源、版本、栈模式、暴露端口与代理。`OBS_STACK_MODE` 默认 `full`,命令行 `--minimal/--full` 可临时覆盖;`PROXY_SH` 仅作用于 native runtime,**不会**影响 `docker pull` 或 `kubectl`,后者必须直接对 shell 设 `HTTP_PROXY`。

### 表 3:能力与前置配置(原文 §1.4)

| 观测能力 | 是否需改 MindIE Motor 配置 | 需要的配置 |
|----------|--------------------------|-----------|
| Coordinator 基础指标(指标总览 / KV 缓存的请求数、KV、吞吐、延迟等) | **否** | Coordinator 默认在管理端口暴露 `/metrics`、`/instance/metrics`,无需额外配置;只需保证该端口可被观测机或主机端口转发访问 |
| Engine / vLLM 指标 | **否**(默认开启) | 原生引擎在业务端口暴露 `/metrics`;Coordinator 使用 `infer_tls_config` 直接采集,需保证业务端口可达 |
| Tracing(Tempo 链路) | **是** | 见 §1.4.1 |
| 引擎性能剖析(`vllm_profiling_*`) | **是** | 需安装并开启 `ms_service_metric`,见 §1.4.2 |

**解读:** 默认 4 项能力中,**只有 Tracing 与 Profiling 需要改 MindIE Motor 配置**;其余(Coordinator、Engine/vLLM 指标)开箱即用,但需要**端口可达**(管理端口 + 业务端口)。Controller metrics 接口(1027 端口)在本方案中**被显式忽略**。

### 表 4:Compose 镜像拉取策略(原文 §2)

| 变量 | 取值 | 含义 |
|------|------|------|
| `OBS_COMPOSE_PULL` | `missing`(默认) | 缺镜像才拉取 |
| | `never` | 禁止拉取(离线 / 镜像已齐全) |
| | `always` | 每次启动都尝试拉取 |
| `OBS_COMPOSE_BUILD` | `0`(默认) | 不本地 build Grafana |
| | `1` | 允许 `compose up --build` |

**解读:** 默认行为"缺啥拉啥,不本地 build",适合初次拉取;离线环境用 `never`,CI/升级用 `always`;`OBS_COMPOSE_BUILD=1` 用于需要二次打包 Grafana 镜像(如带自定义 dashboard)的场景。

### 表 5:minimal 模式核心镜像(原文 §2.1)

| 镜像(默认 tag) | 用途 |
|----------------|------|
| `grafana/grafana:11.3.0` | Grafana 看板 |
| `prom/prometheus:v2.55.1` | 指标存储与查询 |
| `grafana/tempo:2.6.1` | Trace 存储 |
| `otel/opentelemetry-collector-contrib:0.115.1` | OTLP 接入 |

**解读:** minimal 即"指标 + Trace 接入 + 展示"四件套,不包含 Loki(node-exporter/cadvisor)。full 在此基础上再加 Loki 与主机指标采集;`--profile npu` 再叠加 Ascend NPU 专用 exporter。

### 表 6:代理阶段分工(原文 §2.2)

| 阶段 | 主机 `HTTP_PROXY` | 说明 |
|------|-------------------|------|
| `kubectl` / `discover-targets.py` | **建议关闭** | 发现脚本内 `_kubectl_env()` 会剔除代理,避免 API Server 经代理超时;也可先 `unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY` |
| `docker pull` / `compose pull` / `up --pull missing` | **需要时开启** | 拉镜像时 Docker 客户端继承**当前 shell** 代理 |
| Grafana / Prometheus 等容器内 | **已禁用** | Compose 已为 Grafana 清空 `HTTP_PROXY`,`NO_PROXY` 含 `prometheus,tempo`,访问栈内数据源不走外网代理 |

**解读:** 文档**反复强调**代理必须分阶段管理:**拉镜像开 → 发现阶段关 → 容器内已内置禁用**。这是最常见的踩坑来源(kubectl 走代理导致超时、Grafana 访问 Prometheus 走代理导致 504),所以单独列了一节(§2.4)说明。

### 表 7:三阶段代理速查(原文 §2.4.1)

| 阶段 | 配置方式 | 是否建议开代理 |
|------|----------|----------------|
| **目标发现**(`discover-targets.py` / `kubectl`) | 关闭 shell 代理;脚本内已对 kubectl 剔除代理变量 | **否** |
| **Docker 拉镜像**(`docker compose pull` / `launch.sh` → `start.sh`) | 在**启动前**对当前 shell `source` 代理脚本或 `export HTTP_PROXY=...` | **需要外网 registry 时是** |
| **Native 下载二进制**(`start-native.sh` / `launch.sh --native`) | `.env` 中设置 `PROXY_SH`,或启动前 export 同名环境变量 | **需要访问 GitHub / dl.grafana.com 时是** |
| **容器内访问 Prometheus / Tempo** | 无需配置;Compose 已清空 Grafana 的 `HTTP_PROXY` 并设置 `NO_PROXY` | **否**(已内置) |

**解读:** 与表 6 互补,本表显式把"Native 下载二进制"列为第三个独立阶段——它**只能用 `PROXY_SH`**(dotenv 文件路径),**不能**复用 shell 的 `HTTP_PROXY` 自动继承。

---

## 【公式解读】

**原文无公式。** 文档涉及的是运维流程而非算法/数学模型,未出现 LaTeX 或伪代码形式的公式。

---

## 【关联】

- **[GRAFANA_GUIDE.md](GRAFANA_GUIDE.md)**(文末/开篇"配套文档"):负责 Grafana 页面设计与看板指标扩展,与本文档**前后接续**——本文档负责把栈拉起来并确保数据源连通,`GRAFANA_GUIDE.md` 负责告诉用户看板看什么、指标语义、新增/裁剪看板的方法。
- **MindIE Motor Coordinator / Engine(上游)**:Coordinator 的 `/metrics`、`/instance/metrics` 与引擎 `/metrics` 是默认指标来源;Tracing 需要 Coordinator `motor_coordinator_config.tracer_config.endpoint` 与引擎 `engine_config.otlp-traces-endpoint` 指向 OTel Collector(`http://<obs-host>:4318/v1/traces`)。
- **ms_service_metric(上游工具)**:`vllm_profiling_*` 指标来源,文档指向 `https://gitcode.com/Ascend/msserviceprofiler/tree/master/ms_service_metric`;Engine 侧依赖 `PROMETHEUS_MULTIPROC_DIR=/dev/shm/vllm_metrics` 开启多进程采集。
- **MindIE Motor Controller**(被排除):本文档**显式不依赖** Controller metrics 接口(`observability_enable`、`1027` 端口可忽略),与 MindIE Motor 整体可观测性体系刻意解耦。
- **Kubernetes 集群与 Docker Compose v2**(底层运行时):栈以 Compose 编排容器,Pod 发现靠 `kubectl` + `discover-targets.py`;原生模式(`--native`)作为无 Docker 的备选。
- **.env / .env.example / launch.sh / stop.sh / start.sh / start-native.sh**(同目录脚本):本文档是这些脚本的使用说明书,§1.3 描述的变量均由这些脚本读取。

---

## 【使用方法】

### 拉起流程(原文)
```bash
# 1) 进入工作目录
cd examples/features/observability/stack

# 2) 准备配置(.env,如不存在会自动从 .env.example 复制)
cp -n .env.example .env
# 按需编辑 .env:REGISTRY_PREFIX、组件版本、端口、PROXY_SH 等

# 3) 首次拉镜像(联网代理环境)
source /path/to/your-proxy.sh   # 或 export HTTP_PROXY / HTTPS_PROXY
docker compose pull             # 仅需一次;本地已有可跳
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY   # 发现前关代理

# 4) 拉起服务
MOTOR_NAMESPACE=<namespace> ./launch.sh --minimal    # 或 --full(默认)
# Native 模式(无 Docker):MOTOR_NAMESPACE=<namespace> ./launch.sh --native
```

### 停止流程(原文)
切换 `mindie-*` 环境或结束观测时:
```bash
cd examples/features/observability/stack
./stop.sh
```

### 离线场景(原文)
```bash
export OBS_COMPOSE_PULL=never
MOTOR_NAMESPACE=<namespace> ./launch.sh --minimal
```

### 启用 Profiling 看板(原文)
```bash
# Engine 端
pip install ms_service_metric
export PROMETHEUS_MULTIPROC_DIR=/dev/shm/vllm_metrics && mkdir -p "$PROMETHEUS_MULTIPROC_DIR"
# 启动 vLLM/Engine ...
# Engine ready 后:
ms-service-metric on      # 开启指标采集
ms-service-metric status  # 查看状态
ms-service-metric off     # 关闭
ms-service-metric restart # 重启
```

### 启用 Tracing 看板(原文,需重新 `deploy.py`)
修改 `env.json` 与 `user_config.json`,关键字段:
- `env.json` → `motor_coordinator_env` / `motor_engine_prefill_env` / `motor_engine_decode_env` 下新增 `OTEL_SERVICE_NAME`、`OTEL_EXPORTER_OTLP_TRACES_PROTOCOL=http/protobuf`、`OTEL_EXPORTER_OTLP_TRACES_INSECURE=true`
- `user_config.json` → `motor_coordinator_config.tracer_config.endpoint = http://<obs-host>:4318/v1/traces`
- `user_config.json` → `motor_engine_prefill_config.engine_config.otlp-traces-endpoint` 与 `motor_engine_decode_config.engine_config.otlp-traces-endpoint` 同样指向 `http://<obs-host>:4318/v1/traces`

> 关于"`launch.sh` 接受哪些参数、每个参数的语义、停止顺序是否需要先 unset 代理、验收脚本细节"等,文档**未涉及**(仅给出流程示意 `前提条件检查 → 准备镜像 → 拉起服务 → 验收 → 停止服务`),需结合同目录脚本源码确认。
