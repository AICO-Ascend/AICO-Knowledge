# vLLM Hook Tracing 特性详细设计

> 仓 `msserviceprofiler` · 路径 `docs/design/vLLM_Hook_Tracing_Detailed_Design.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msserviceprofiler/docs/design/vLLM_Hook_Tracing_Detailed_Design.md

# vLLM Hook Tracing 特性详细设计 — 一体化深度解读

## 【定位】
本文档定义 msserviceprofiler 在 **vLLM/vLLM-Ascend 已开启 OpenTelemetry 原生 Tracing** 的前提下，通过复用 vLLM 全局 `TracerProvider` 的方式补充业务级 Hook Span（request/scheduler/model/output），并旁路输出到 Jaeger（必经）与 Perfetto（可选）的能力边界、模块边界、接口与回滚策略。

---

## 【技术要点】

1. **必须前置依赖**：`vllm serve` 启动时必须携带 `--otlp-traces-endpoint`（如 `http://127.0.0.1:4318/v1/traces`），由 vLLM 初始化全局 `TracerProvider`；msServiceProfiler **不**调用 `set_tracer_provider()`、不创建、不替换、不关闭 Provider，也不读取 OTLP endpoint 自建 Provider。
2. **运行时开关**：单一环境变量 `MS_TRACE_ENABLE=1`；关闭时**不**访问 Provider、**不**创建 Span。Provider 缺失或不支持 `add_span_processor` 时，Hook tracing 自动降级为 **no-op**，推理继续（fail-open）。
3. **Hook 组合顺序**：`调用方 → tracing around → profiling handler（可选）→ 原业务函数`；同一符号在 YAML 中只能有一个有效 `trace` 配置（重复项记录告警并忽略后项），业务函数只执行一次；异常透传，tracing 后处理失败返回已缓存业务结果。
5. **双 Socket 严格隔离**：
   - `OTLP_SOCKET` — 原 MindIE C++ Trace 的二进制 OTLP 通道，行为不变。
   - `MSP_PERFETTO_SOCKET` — 仅接收 msServiceProfiler Hook Span 的规范化事件包。
6. **Perfetto 旁路**：`PerfettoSpanProcessor` 仅筛选 instrumentation scope 以 `ms_service_profiler.hook` 开头的 Span，因此输出的 Chrome Trace JSON 不含 vLLM 原生 Span 与旧 C++ OTLP；发送走后台线程 + 有界队列，推理线程不执行文件 I/O。
7. **硬约束**：当前及后续版本均**不**修改 vLLM/vLLM-Ascend 源码或 IPC，也**不**导入 `vllm.tracing` 私有接口；不允许"vLLM 未开启原生 Tracing 而 msServiceProfiler 单独创建 Trace"的兼容模式。

---

## 【关键机制与数据】

### 工作原理（基于原文架构图）
```
YAML ──► 现有 Hook Framework ──► Tracing around Adapter
                                    │
                                    ▼
                            HookTraceRuntime
                                    │
                                    ▼
                        OpenTelemetryHookBackend
                                    │
                    ┌───────────────┴───────────────┐
                    ▼                               ▼
        vLLM 全局 TracerProvider        可选 PerfettoSpanProcessor
                    │                               │
                    ▼                               ▼
        vLLM 原生 OTLP Processor             MSP_PERFETTO_SOCKET
                    │                               │
                    ▼                               ▼
            Jaeger / OTLP Collector       PerfettoForwarderService
                                                    │
                                                    ▼
                                          Chrome Trace JSON

并行支路（不变）：MindIE C++ Tracer ──► OTLP_SOCKET ──► 原 OTLPForwarderService
```

### 请求上下文关联规则（原文）
- 优先从 vLLM 请求参数/对象读取 `request_id` 和 `trace_headers`。
- 用 W3C `traceparent` 提取真实上下文，并按 `request_id` 暂存。
- scheduler/model/output Span 通过 OTel `Link` 关联已知请求上下文。
- 不根据 request ID 伪造 trace ID；进程内拿不到真实上下文时仅保留 `request.ids` 属性。
- 跨进程 `trace_headers` 的可获得性完全取决于当前 vLLM 已公开数据；后续版本只允许通过版本适配层选择性读取公共接口，**不**要求 vLLM 为本工具增加字段、消息或反向依赖。

### 性能与安全约束（原文）
- request context 表、Link 数量、属性数量与长度**均有限制**。
- **不**记录 prompt 正文。
- Perfetto 输出路径检查：普通文件、属主、软链接、`.json` 扩展名。
- tracing + profiling 同时开启时，Span 含少量 profiling handler 处理开销（已接受）。
- 所有 tracing 异常 fail-open；业务异常保持原类型与对象，**不**触发业务函数重复执行。

### 性能数据
**原文未提供**具体数字（吞吐量、延迟、队列容量上限等均未给出）。

---

## 【表格解读】

### 表 1：文档信息

| 项目 | 内容 |
|---|---|
| 特性 | vLLM/vLLM-Ascend Hook Tracing |
| 仓库 | msserviceprofiler |
| 版本 | 26.0.0 |
| 日期 | 2026-08-15 |
| 状态 | 开发验证 |

**逐行解读**：
- **特性**：明确本设计针对 vLLM 与 vLLM-Ascend 两个发行版对象，二者均假定具备原生 Tracing 能力。
- **仓库**：实现位于 msserviceprofiler 内，**不**侵入 vLLM 仓库。
- **版本**：26.0.0 — 与仓库版本号对齐，表明这是面向未来发布版的能力。
- **日期**：2026-08-15 — 设计落地时间点。
- **状态**：开发验证 — 尚未完成正式发布验收，处于真实 NPU 环境回归阶段（对应第 12 节验证设计）。

---

### 表 2：关键模块职责与边界

| 模块 | 职责 | 边界 |
|---|---|---|
| `patcher/core/module_hook.py` | 提供一个可选 `around_hook_factory` 扩展点 | 原 context hook 和 profiling handler 逻辑不变 |
| `patcher/core/config_loader.py` | 从同一份 YAML 解析 profiling 与 `trace` | 同一解析后符号只允许一个有效 trace |
| `patcher/core/trace_hook.py` | 参数/返回值语义提取和 Span 包围逻辑 | 不进入原 profiling context hook 生命周期 |
| `tracer/hook_runtime.py` | request context 表、Links 和 Span 公共属性 | 不创建重复 request 根 Span |
| `tracer/otel_hook.py` | 通过 OTel 公共 API 复用全局 Provider | 不创建、不替换、不关闭 Provider |
| `tracer/perfetto_socket.py` | 过滤并异步发送 Hook Span | 不发送 vLLM 原生 Span，不编码 OTLP protobuf |
| `tracer/perfetto_forward_service.py` | 独立接收 Hook 包并写 JSON | 不复用或修改原 OTLP Scheduler |
| `tracer/perfetto_exporter.py` | Hook 事件包转 Chrome Trace Event | 拒绝旧二进制 OTLP 数据 |
| `tracer/otlp_forward_service.py` | 原 MindIE Trace 转发 | 保持原实现，不参与 vLLM Hook Tracing |

**逐行解读**：
- **`module_hook.py`** — 整个新能力在共享 Hook 框架中**唯一**新增的扩展点即 `around_hook_factory`；它不修改原 context hook 与 profiling handler，保证 profiling 行为完全不变（呼应非目标"不改变 profiling 的 enable.json、采集、CSV/DB/timeline 和 parse 流程"）。
- **`config_loader.py`** — 同一份 YAML 承载 profiling 与 trace 两个独立能力；解析阶段做去重，避免重复 trace 项生成重复 Hook Span。
- **`trace_hook.py`** — 负责参数/返回值语义提取（如将 `request_id`、`trace_headers` 转成 Span 属性与 Links），但其生命周期独立于 profiling context hook，避免互相嵌套影响。
- **`hook_runtime.py`** — 维护 request_id → traceparent 的暂存表与公共属性；明确规定"不创建重复 request 根 Span"，这是与 vLLM 原生根 Span 区分的关键边界。
- **`otel_hook.py`** — 通过 OTel 公共 API（`trace.get_tracer_provider()`）获取 Provider，然后调用 `add_span_processor`；**不**调用任何 setter 或 close 方法。
- **`perfetto_socket.py`** — 客户端：本地进程内将过滤后的 Hook Span 异步塞入有界队列，由后台线程写入 socket；明确**不**做 OTLP protobuf 编码，因为 Perfetto 走的是 Chrome Trace Event 协议。
- **`perfetto_forward_service.py`** — 服务端：独立进程，独立 Socket，独立 JSON 写文件路径；不复用 OTLP Scheduler。
- **`perfetto_exporter.py`** — 把 Hook 事件包（来自 socket 的规范化事件，不是 OTLP）转换为 Chrome Trace Event（Complete/Flow）；遇到旧二进制 OTLP 数据即拒绝，保证两条通道不混淆。
- **`otlp_forward_service.py`** — 这是**保留行**，明确表示原 MindIE Trace 的转发链路**不**被新特性触碰，行为完全不变。

---

### 表 3：用户接口（配置项）

| 配置 | 来源 | 是否新增 | 作用 |
|---|---|---:|---|
| `MS_TRACE_ENABLE=1` | msServiceProfiler 既有 Trace 开关 | 否 | 开启 Hook tracing |
| `PROFILING_SYMBOLS_PATH` | 既有环境变量 | 否 | 可选覆盖同一份 Hook YAML |
| `--otlp-traces-endpoint` | vLLM 原生命令参数 | 否 | **必选**，初始化 Provider 并配置 OTLP 输出 |
| `OTEL_EXPORTER_OTLP_TRACES_PROTOCOL` | OTel 标准环境变量 | 否 | 配置 vLLM exporter 协议 |
| `--perfetto-output` | 本特性 CLI 参数 | 是 | 可选增加 Chrome Trace JSON 输出 |

**逐行解读**：
- **`MS_TRACE_ENABLE=1`** — 唯一的新特性开关；关闭时整套 Hook tracing 跳过，零开销。
- **`PROFILING_SYMBOLS_PATH`** — 复用既有变量，避免引入新变量；用户 YAML 既能覆盖 profiling 也能覆盖 trace。
- **`--otlp-traces-endpoint`** — 强前置；若缺失，全局 Provider 不存在，Hook tracing 自动 no-op。这是"必须 vLLM 开启原生 Tracing"的具体落地形式。
- **`OTEL_EXPORTER_OTLP_TRACES_PROTOCOL`** — 由 vLLM 解释，典型取值如 `http/protobuf`；本表只关心"协议配置由谁负责"（vLLM，不是 msServiceProfile）。
- **`--perfetto-output`** — 本特性**唯一新增**的配置项，传入 `python -m ms_service_profiler.trace` 启动接收端；不传则只走 Jaeger。
- **设计原则**：没有独立 tracing YAML、没有新增 backend 选择环境变量，最大化复用既有 surface。

---

### 表 4：兼容性与隔离矩阵

| 场景 | 行为 |
|---|---|
| vLLM 支持并开启原生 tracing | 正常创建 Hook Span |
| vLLM 不支持或未开启原生 tracing | Hook tracing no-op，**不属于支持场景** |
| vLLM tracing 私有 API 变化 | 不受影响；实现只使用 OTel 公共 API |
| YAML 部分符号不存在 | SymbolWatcher 跳过，其他 Hook 继续 |
| 新 msServiceProfiler + 旧 vLLM-Ascend | 使用包内 default YAML，存在的符号正常 Hook |
| 旧 `libms_service_profiler.so` | 可用；本特性无新增 C/C++ ABI |
| profiling 与 tracing 同时开启 | tracing 包裹 profiling；业务函数执行一次 |
| Jaeger 不可用 | vLLM exporter 按自身策略处理；Hook fail-open |
| Perfetto Forwarder 不可用 | 不注册旁路 Processor；Jaeger 不受影响 |

**逐行解读**：
- **第 1/2 行** — 直接对应"目标 vs 非目标"第 1 条：vLLM 无原生 Tracing 时本特性不试图兜底。
- **第 3 行** — 通过只用 OTel 公共 API 解耦 vLLM 私有 API 演进风险，与第 2 节硬约束呼应。
- **第 4 行** — 复用既有 SymbolWatcher 跳过机制，与非目标"不保证 YAML 中已删除或改名的业务符号仍可 Hook"一致。
- **第 5 行** — 兼容旧版 vLLM-Ascend **仅**指 YAML/符号层面；不等价于支持无原生 Tracing 的旧核心（见第 10 节末尾"注脚"）。
- **第 6 行** — 强调本特性为纯 Python/Java 层面，无新增 C/C++ ABI，旧二进制 so 文件可直接复用。
- **第 7 行** — 与第 6.2 节 `TrackableOriginalFunc` 机制一致，业务函数单次执行是硬保证。
- **第 8/9 行** — 双输出通道完全独立：Jaeger 故障不影响 Perfetto，反之亦然；两者同时故障也不阻塞推理。

---

## 【公式解读】

**原文无公式**（文档无 LaTeX 或伪代码形式的数学公式；仅有调用链伪代码 `调用方 -> tracing around -> profiling handler（可选）-> 原业务函数`，已在上节工作原理中覆盖）。

---

## 【关联】

本文档（与上下文）通过以下边界与 msserviceprofiler 内既有模块/特性建立联系：

- **既有 Hook Framework（`patcher/core/module_hook.py`）**：新特性只引入一个**可选**扩展点 `around_hook_factory`，原 context hook 流程不变；这是整套设计的最小侵入切入口。
- **既有 profiling 机制**：通过同一份 YAML 的 `handler` 与 `trace` 两个字段并存实现；trace 包裹 profiling，业务函数仍由 `TrackableOriginalFunc` 守护单次执行。YAML 重复 trace 项会被解析器去重。
- **vLLM 原生 OpenTelemetry Tracing（外部依赖）**：vLLM 通过 `--otlp-traces-endpoint` 初始化全局 `TracerProvider`；Hook Span 复用同一 Provider、采样策略、上下文与 OTLP exporter。这是 **能力边界**而非内部模块。
- **Jaeger / OTLP Collector（外部）**：必经输出；由 vLLM 原生 OTLP Processor 推送。
- **Perfetto / Chrome Trace JSON（外部）**：可选旁路输出；通过新增的 `MSP_PERFETTO_SOCKET` 与 `PerfettoForwarderService` 独立通道。
- **MindIE C++ Tracer（`tracer/otlp_forward_service.py` + `OTLP_SOCKET`）**：原二进制 OTLP 转发链路；本文档明确声明"保持原实现，不参与 vLLM Hook Tracing"，即隔离基线。
- **回滚链（第 14 节）**：运行时回滚靠 `unset MS_TRACE_ENABLE`；代码回滚分两步：先移除 YAML `trace` 字段，再移除 Python OTel Backend 与独立 Perfetto 旁路；C++ Tracer、`OTLP_SOCKET`、OTLP Forwarder 与 profiling **不**在回滚链上。
- **内部链接**：原文文末标注"内部链接: (无)"，本仓库**未提供**交叉引用关系，本节关联完全基于正文文本归纳。

---

## 【使用方法】

### 模式 A：仅 Jaeger 输出（原文第 8.1 节）
```bash
export MS_TRACE_ENABLE=1
export OTEL_SERVICE_NAME=vllm-server
export OTEL_EXPORTER_OTLP_TRACES_PROTOCOL=http/protobuf

vllm serve MODEL \
  --otlp-traces-endpoint http://127.0.0.1:4318/v1/traces
```
vLLM 原生 Span 与 Hook Span 共用 Provider 直发 Jaeger/Collector；**不**需要运行 `python -m ms_service_profiler.trace`。

### 模式 B：Jaeger + Perfetto 双输出（原文第 8.2 节）
```bash
# 1) 启动 Perfetto 接收端（后台）
python -m ms_service_profiler.trace \
  --perfetto-output /tmp/hook_tracing.json &

# 2) 启动 vLLM
export MS_TRACE_ENABLE=1
export OTEL_SERVICE_NAME=vllm-server
export OTEL_EXPORTER_OTLP_TRACES_PROTOCOL=http/protobuf

vllm serve MODEL \
  --otlp-traces-endpoint http://127.0.0.1:4318/v1/traces
```
`PerfettoSpanProcessor` 只筛选 instrumentation scope 以 `ms_service_profiler.hook` 开头的 Span，因此 `/tmp/hook_tracing.json` **只**包含 Hook Span；Jaeger 仍同时接收原生 Span 与 Hook Span。

### 模式 C：不被支持的"伪 Perfetto-only"（原文第 8.3 节）
```bash
python -m ms_service_profiler.trace --perfetto-output /tmp/hook_tracing.json
```
该命令**只**启动文件接收端，不能自行创建 Span。若 vLLM 未配置 `--otlp-traces-endpoint`，不存在可复用 Provider，Perfetto JSON 将保持空数组。原文明确指出"这不是 Perfetto-only 模式"。

### YAML trace 字段示例（原文第 6.3 节）
```yaml
- symbol: vllm.v1.core.sched.scheduler:Scheduler.schedule
  handler: ms_service_profiler.patcher.vllm.handlers.v1.scheduler_handlers:schedule
  trace:
    name: vllm.scheduler.schedule
    domain: Schedule
    adapter: schedule
```
同一符号只能有一个有效 `trace` 配置；重复项告警并忽略后项。

### 用户 YAML 覆盖（原文第 9 节）
默认 YAML 位于 msServiceProfiler 内；用户可通过既有环境变量 `PROFILING_SYMBOLS_PATH` 覆盖**同一份** Hook YAML 中的 profiling 与 trace 字段。

### 关闭 / 回滚（原文第 14 节）
- **运行时关闭**：`unset MS_TRACE_ENABLE` 即可关闭 Hook tracing，零代码改动。
- **代码回滚顺序**：① 移除 YAML `trace` 字段 → ② 移除 Python OTel Backend 与独立 Perfetto 旁路；原 C++ Tracer、`OTLP_SOCKET`、OTLP Forwarder、profiling **不**参与回滚。
