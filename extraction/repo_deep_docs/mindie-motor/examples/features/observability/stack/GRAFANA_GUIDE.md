# MindIE Motor 可观测性栈 · Grafana 使用指导

> 仓 `mindie-motor` · 路径 `examples/features/observability/stack/GRAFANA_GUIDE.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-motor/examples/features/observability/stack/GRAFANA_GUIDE.md

# 一体化深度解读:GRAFANA_GUIDE.md

## 【定位】

本指南说明 MindIE Motor 可观测性栈中 Grafana 的页面设计、内置看板(指标总览、KV 缓存、引擎性能剖析)、三个预置数据源(Prometheus/Tempo/Loki)的配置与联动跳转机制,并给出"在看板中新增 metrics 指标"的两种可复现步骤(UI 编辑写回 JSON / 直接编辑 JSON)。

---

## 【技术要点】

1. **三个预置数据源**(全部由 `grafana/provisioning/datasources/datasources.yml` 自动注入,无需手动添加):
   - Prometheus(`prometheus` / `http://prometheus:9090`,默认数据源)
   - Tempo(`tempo` / `http://tempo:3200`,分布式追踪)
   - Loki(`loki` / `http://loki:3100`,仅 full 模式拉起,minimal 模式无)

2. **三源联动跳转配置**:Trace→Log 按 `service.name`/`x_request_id` 关联,时间窗口前后 5 分钟;Trace→Metrics 按 `service.name` 关联 Prometheus;Log→Trace 通过 Loki `derivedFields` 正则提取 `trace_id`/`x_request_id`。

3. **三个内置看板**(由 `dashboard-providers.yml` 自动加载,平铺无文件夹,`foldersFromFilesStructure: false`,`updateIntervalSeconds: 30`):
   - 指标总览 `motor-all-metrics`(集群概览、PD Role/Instance 分组、吞吐与延迟)
   - KV 缓存 `motor-kv-cache`(vLLM KV cache 使用率、prefix cache 命中率)
   - 引擎性能剖析 `motor-vllm-profiling`(`vllm_profiling_*` 指标,显存/forward/execute/scheduler 时延)

4. **看板模板变量**(8 个 query 类型变量,均基于 Prometheus 标签动态生成):`$cluster`、`$motor_metric_scope`、`$role`、`$pd_role`、`$dp_rank`、`$pod_ip`、`$instance_id`、`$model_name`;引擎性能剖析另有 `$source`、`$job`、`$phase`、`$dp`。

5. **Grafana 容器以只读方式挂载** `grafana/dashboards`,UI 上的临时修改不会落盘,持久化必须写回 JSON 源文件;provisioner 每 30s 重载。

6. **新增指标两种方式**:UI 编辑后写回 JSON(推荐,可入库)/ 直接编辑 JSON;**新组件需先在 `prometheus.yml` 加 scrape job**(自动发现产物为 `generated/prometheus.yml`),再 `./launch.sh` 或 `curl -X POST http://localhost:9090/-/reload` 热加载(已开 `--web.enable-lifecycle`)。

7. **Profiling 接入依赖**:Engine 侧安装 `ms_service_metric`(`pip install ms_service_metric`,Python ≥ 3.10,依赖 pyyaml/prometheus-client/posix_ipc),需设置 `PROMETHEUS_MULTIPROC_DIR=/dev/shm/vllm_metrics`,通过 `ms-service-metric on/off/restart/status` 控制。

---

## 【关键机制与数据】

- **观测栈工作流**:MindIE Motor Coordinator/Engine 通过 OTLP/HTTP(端口 `4318/v1/traces`)将 trace 发往 Tempo,指标经 `ms_service_metric` 多进程采集(`/dev/shm/vllm_metrics`)后被 Prometheus 抓取,日志由 Loki 收容;Grafana 通过预置的 `tracesToLogsV2` / `tracesToMetrics` / Loki `derivedFields` 实现跨源跳转(原文:Trace→Log 时间窗口前后 5 分钟,按 `service.name`/`x_request_id` 关联)。

- **看板 JSON 自动加载机制**(原文):`grafana/provisioning/dashboards/dashboard-providers.yml` 自动加载 `grafana/dashboards/` 下的 JSON,`updateIntervalSeconds: 30`;容器以**只读**方式挂载,因此 UI 改动刷新后丢失,需写回源文件。

- **看板变量查询的 PromQL 模式**(原文):
  - `$cluster`:`label_values({cluster!=""}, cluster)`
  - `$model_name`:`label_values(vllm:num_requests_running{cluster=~"$cluster"}, model_name)`(从具体指标标签取)
  - 其余变量统一采用 `label_values({cluster=~"$cluster", <label>!=""}, <label>)` 模式;建议 `allValue` 设为 `.*` 防止 No Data。

- **指标命名特性**(原文):Prometheus 已开启 `--enable-feature=utf8-names`,可支持冒号类指标如 `vllm:num_requests_waiting`、`vllm:num_requests_running`;新增面板 PromQL **务必带看板变量过滤**(`{cluster=~"$cluster", ...}`)。

- **Loki 模式区分**(原文):Loki 仅在 full 模式拉起,minimal 模式无 Loki 数据源。

- **性能数据**:原文未给出具体的性能数字(吞吐/延迟/容量),仅给出配置参数(端口、UID、间隔秒数),未涉及数字化的性能指标。

---

## 【表格解读】

### 表 1:登录与访问(原文 §1)

| 项 | 默认值 | 说明 |
|----|--------|------|
| 地址 | `http://localhost:3000` | 端口由 `.env` 的 `GRAFANA_PORT` 控制 |
| 账号 | `motor` | `.env` 的 `GF_SECURITY_ADMIN_USER` |
| 密码 | `motor` | `.env` 的 `GF_SECURITY_ADMIN_PASSWORD` |

**解读**:Grafana 通过 `.env` 中的三个环境变量控制暴露端口与凭据,默认绑定本地 3000 端口、默认管理员账号密码均为 `motor`;意味着部署到非本地环境时必须修改 `GF_SECURITY_ADMIN_USER/PASSWORD`,否则存在默认口令风险。

### 表 2:数据源(原文 §2.1)

| 数据源 | UID | 地址 | 用途 |
|--------|-----|------|------|
| **Prometheus** | `prometheus` | `http://prometheus:9090` | 指标查询(默认数据源) |
| **Tempo** | `tempo` | `http://tempo:3200` | 分布式追踪(Trace) |
| **Loki** | `loki` | `http://loki:3100` | 日志(minimal / full 均包含) |

**解读**:三源按"指标(Metrics)+ 追踪(Traces)+ 日志(Logs)"覆盖可观测性三大支柱;UID 命名规范固定为小写英文,与后续 JSON `datasource.uid` 必须严格匹配;地址均为容器内部 DNS,说明 Grafana 与三者同栈部署(docker network 内部访问)。表格"用途"列写 Loki"minimal/full 均包含",与§6"Loki 仅在 full 模式拉起"表述**存在措辞不一致**,以§6为准,Loki 仅 full 模式可用。

### 表 3:看板(原文 §2.2)

| 看板 | UID | 文件 | 内容 |
|------|-----|------|------|
| **MindIE Motor Metrics · 指标总览** | `motor-all-metrics` | `motor-all-metrics.json` | 集群概览、PD Role / Instance 分组、吞吐与延迟 |
| **KV 缓存** | `motor-kv-cache` | `motor-kv-cache.json` | vLLM KV cache 使用率、prefix cache 命中率 |
| **引擎性能剖析** | `motor-vllm-profiling` | `motor-vllm-profiling.json` | `vllm_profiling_*` 性能剖析(显存、forward/execute/scheduler 时延等) |

**解读**:三个看板按抽象层级递进——指标总览(集群宏观)→ KV 缓存(单实例 vLLM 内存子模块)→ 引擎剖析(单算子时延);UID 与文件名一一对应,持久化时按 UID 定位即可;`vllm_profiling_*` 来自 `ms_service_metric`,依赖 Engine 侧安装(见 §5.2)。

### 表 4:看板变量(原文 §2.3)

| 变量 | Label |
|------|-------|
| $cluster | Cluster |
| $motor_metric_scope | Metric Scope |
| $role | Role |
| $pd_role | PD Role |
| $dp_rank | DP Rank |
| $pod_ip | Pod IP |
| $instance_id | Instance ID |
| $model_name | Model Name |

**解读**:8 个变量形成从"集群→角色→实例→模型"的下钻维度链;`$pd_role` 为 MindIE 特有(预填充 Prefill/Decode)、`$dp_rank` 为分布式并行 rank,体现了推理集群的多维标签体系;新增面板**必须复用这些变量**做过滤,否则切换变量时面板不联动。

### 表 5:常见问题(原文 §6)

| 现象 | 处理建议 |
|------|----------|
| 看板变量下拉为空 | 对应标签未被任何指标暴露;先确认 Prometheus 已抓到带该标签的指标(第 3 节) |
| 新增面板 No Data | 检查 PromQL 是否带了看板变量过滤;变量 `allValue` 是否为 `.*`;指标名是否含冒号(如 `vllm:*`,本栈已开启 `--enable-feature=utf8-names`) |
| UI 改动刷新后丢失 | 容器只读挂载 `grafana/dashboards`,需将 JSON Model 写回源文件(第 4 节) |
| 看板报 500 / 504 | Grafana 容器经外网代理访问 `prometheus`/`tempo` 超时;确认容器内 `HTTP_PROXY` 为空(详见 [SERVICE_GUIDE.md](SERVICE_GUIDE.md) 第 6 节) |
| Loki 数据源不可用 | Loki 仅在 full 模式拉起,minimal 模式无 Loki |

**解读**:五个高频问题对应三类根因——① 标签/指标缺失(去 Prometheus 验证);② PromQL 语法/变量配置(`allValue=.*`、UTF-8 指标名);③ 容器化部署的副作用(只读挂载、HTTP_PROXY 环境变量污染、栈模式差异)。

---

## 【公式解读】

原文无 LaTeX 数学公式,但 §2.3 给出 8 个 label_values PromQL 查询表达式(可视为"变量定义公式"),以及 §4.1 给出一段示例 PromQL。逐字保留并解释如下:

**§2.3 看板变量定义(逐字保留)**:

```
label_values({cluster!=""}, cluster)
label_values({cluster=~"$cluster", motor_metric_scope!=""}, motor_metric_scope)
label_values({cluster=~"$cluster", role!=""}, role)
label_values({cluster=~"$cluster", pd_role!=""}, pd_role)
label_values({cluster=~"$cluster", dp_rank!=""}, dp_rank)
label_values({cluster=~"$cluster", pod_ip!=""}, pod_ip)
label_values({cluster=~"$cluster", instance_id!=""}, instance_id)
label_values(vllm:num_requests_running{cluster=~"$cluster"}, model_name)
```

**符号说明**:
- `label_values(metric_selector, label)`:Grafana 内置函数,从匹配指标的标签取值,生成下拉选项。
- `{cluster!=""}`:度量选择器,过滤掉 `cluster` 标签为空的样本(避免出现空字符串下拉项)。
- `{cluster=~"$cluster"}`:正则匹配操作符 `=~`,引用上层变量 `$cluster` 的当前选中值;由于 `allValue=.*`,未选中时等效于匹配全部。
- `<label>!=""`:对各自身标签做非空过滤,保证下拉只显示真实存在该标签的实例。
- 最后一行特殊:不返回所有 `model_name`,而是限定在 `vllm:num_requests_running` 这条具体指标上,避免列出从未上报过请求的模型。

**§4.1 示例 PromQL(逐字保留)**:

```promql
sum by (instance_id) (
  vllm:num_requests_waiting{cluster=~"$cluster", instance_id=~"$instance_id", pd_role=~"$pd_role"}
)
```

**符号说明**:
- `sum by (instance_id)`:聚合算子,按 `instance_id` 分组求和,产出每个实例一条时间序列。
- `vllm:num_requests_waiting`:指标名(冒号类指标,依赖 Prometheus `--enable-feature=utf8-names`)。
- `{...}` 内的 `=~"$var"`:正则匹配看板变量,实现下钻过滤;**注意 `$instance_id` 必须出现在过滤中**,否则跨实例求和会塌缩。
- 业务语义:每个实例当前排队等待推理引擎处理的请求数,用于发现调度热点。

---

## 【关联】

- **[SERVICE_GUIDE.md](SERVICE_GUIDE.md)**:本指南开头即声明"服务拉起/停止操作见 SERVICE_GUIDE.md",前提为"已按 SERVICE_GUIDE.md 拉起栈";§5 引用 [SERVICE_GUIDE.md §1.4](SERVICE_GUIDE.md) 给出 MindIE Motor 侧的完整配置清单(tracing OTLP endpoint、`ms_service_metric` 安装步骤);§6 引用 [SERVICE_GUIDE.md §6](SERVICE_GUIDE.md) 排查 500/504 错误(确认 `HTTP_PROXY` 为空)。
- **MindIE Motor Coordinator**:通过 `tracer_config.endpoint` 上报 trace 到 `http://<obs-host>:4318/v1/traces`,OTEL 服务名 `mindie-motor-coordinator`。
- **MindIE Motor Engine(vLLM)**:通过 `engine_config.otlp-traces-endpoint` 上报 trace,OTEL 服务名 `vllm-server-p` / `vllm-server-d`(对应 PD 分离角色);同时安装 `ms_service_metric` 输出 `vllm_profiling_*`。
- **ms_service_metric**(gitcode.com/Ascend/msserviceprofiler):Profiling 数据采集器,Engine ready 后通过 `ms-service-metric on` 开启,数据进入 Prometheus 后驱动 `motor-vllm-profiling` 看板。
- **Prometheus**:作为默认数据源 + scrape target,启用了 `--web.enable-lifecycle`(允许 `/-/reload` 热加载)与 `--enable-feature=utf8-names`(支持 `vllm:*` 命名)。
- **Tempo / Loki**:分别承载追踪与日志,通过 `tracesToLogsV2` / `tracesToMetrics` / Loki `derivedFields` 实现跨源跳转。
- **Provisioner 链路**:`grafana/provisioning/datasources/datasources.yml`(注入三源) + `grafana/provisioning/dashboards/dashboard-providers.yml`(加载 JSON,30s 间隔) + 只读挂载 `grafana/dashboards`(持久化约束)。

---

## 【使用方法】

### 1. 登录访问(原文 §1)
- 地址:`http://localhost:3000`(端口由 `.env` 的 `GRAFANA_PORT` 控制)
- 账号/密码:`motor / motor`(由 `.env` 的 `GF_SECURITY_ADMIN_USER` / `GF_SECURITY_ADMIN_PASSWORD` 控制)
- 入口:登录后 **Dashboards** 查看三个内置看板

### 2. 验证指标是否被采集(原文 §3)

```bash
# 列出指标名
curl -s http://localhost:9090/api/v1/label/__name__/values | tr ',' '\n' | grep -i <keyword>

# 查询指标当前值
curl -sG http://localhost:9090/api/v1/query --data-urlencode 'query=<metric_name>'

# 查看抓取目标状态
curl -s http://localhost:9090/api/v1/targets
```

亦可在 Grafana **Explore** → Prometheus 数据源中直接输入 PromQL 验证。

### 3. 新增面板 — 方式一:UI 编辑后写回 JSON(原文 §4.1)
1. 目标看板右上角 **Edit** → **Add → Visualization** → 数据源选 **Prometheus**
2. Query 中输入 PromQL(示例:每实例等待请求数 `sum by (instance_id) (vllm:num_requests_waiting{cluster=~"$cluster", instance_id=~"$instance_id", pd_role=~"$pd_role"})`)
3. 选可视化类型(Time series / Stat / Bar gauge / Pie chart)、设标题/单位/阈值
4. **Apply** → 调整布局 → 看板设置(齿轮)→ **JSON Model** → 复制 JSON → 覆盖写入:
   - `grafana/dashboards/motor-all-metrics.json`
   - `grafana/dashboards/motor-kv-cache.json`
   - `grafana/dashboards/motor-vllm-profiling.json`
5. 等 provisioner 30s 重载后刷新页面

### 4. 新增面板 — 方式二:直接编辑 JSON(原文 §4.2)
- 在 `grafana/dashboards/<dashboard>.json` 的 `panels` 数组中追加对象;`id` 看板内唯一,`gridPos` 控制布局(看板宽度 24 格,`x` 取 0–23);`datasource.uid` 固定 `prometheus`(`tempo`/`loki` 可选);`targets[].expr` PromQL 必须带看板变量过滤,`legendFormat` 用 `{{label}}` 渲染图例
- 保存后等 30s 自动重载,改动大可执行 `docker compose restart grafana` 强制重载

### 5. 新增需接入新组件的指标(原文 §4.3)
1. 在生成/模板 `prometheus.yml` 中新增 scrape job(自动发现产物 `generated/prometheus.yml`)
2. 重新执行 `./launch.sh` 或 `curl -X POST http://localhost:9090/-/reload` 触发 Prometheus 热加载(已开 `--web.enable-lifecycle`)
3. 确认 `targets` 为 UP、指标可查询后再按 4.1 / 4.2 加面板

### 6. 性能剖析看板自动生成(原文 §4.4)

```bash
cd examples/features/observability/stack
python3 grafana/scripts/build-profiling-dashboard.py \
  --prometheus-url http://localhost:9090 \
  --output grafana/dashboards/motor-vllm-profiling.json
```

适用于 Engine 暴露新 `vllm_profiling_*` 指标后批量刷新剖析看板(核心面板常开,明细面板默认折叠)。

### 7. Tracing 配置(原文 §5.1)
- Coordinator:`tracer_config.endpoint = http://<obs-host>:4318/v1/traces`
- Engine:`engine_config.otlp-traces-endpoint = http://<obs-host>:4318/v1/traces`
- `OTEL_SERVICE_NAME` 建议:`mindie-motor-coordinator`、`vllm-server-p`、`vllm-server-d`
- Grafana **Explore** 选 Tempo,默认 Query type 为 TraceQL;可切到 **Search** 或 TraceQL 输入 `{}` 后执行搜索
- 参考:`config/tracing.example.json`

### 8. Profiling 配置(原文 §5.2)
- 安装:`pip install ms_service_metric`(依赖 Python ≥ 3.10、pyyaml、prometheus-client、posix_ipc),仓库 gitcode.com/Ascend/msserviceprofiler
- Engine 启动前:
  ```bash
  export PROMETHEUS_MULTIPROC_DIR=/dev/shm/vllm_metrics && mkdir -p "$PROMETHEUS_MULTIPROC_DIR"
  # 可选:rm -rf $PROMETHEUS_MULTIPROC_DIR/*
  ```
- Engine ready 后:
  ```bash
  ms-service-metric on      # 开启
  ms-service-metric off     # 关闭
  ms-service-metric restart # 重启(重新加载配置)
  ms-service-metric status  # 查看状态
  ```
- 启用后 `vllm_profiling_*` 被 Prometheus 抓取,「引擎性能剖析」看板自动显示数据

### 9. 常见问题排查(原文 §6)
- 变量下拉为空 → 确认 Prometheus 已抓取带该标签的指标(回到第 3 节)
- No Data → 检查 PromQL 是否带变量过滤、`allValue` 是否 `.*`、是否含冒号指标名
- UI 改动丢失 → 写回源 JSON
- 500/504 → 检查容器内 `HTTP_PROXY` 是否为空
- Loki 不可用 → 确认用 full 模式拉起栈
