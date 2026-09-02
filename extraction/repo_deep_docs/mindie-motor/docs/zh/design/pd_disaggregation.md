# PD 分离（特性说明）

> 仓 `mindie-motor` · 路径 `docs/zh/design/pd_disaggregation.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-motor/docs/zh/design/pd_disaggregation.md

# PD 分离特性说明 — 一体化深度解读

## 【定位】

本文档描述 mindie-motor 中 **Prefill / Decode (PD) 分离** 的协同调度机制: 如何基于实例角色与引擎 Connector 能力自动选择路由 (Router) 与派发计划 (Dispatch Plan), 并区分 vLLM (handoff / trigger) 与 SGLang (bootstrap) 两套原生协议的 P/D 协同语义, 使 Coordinator 能在不解码推理细节的前提下, 完成跨实例 KV 传输编排。

---

## 【技术要点】

1. **拓扑自动识别 (role-driven router selection)**: Coordinator 弃用 `motor_coordinator_config.scheduler_config.deploy_mode`, 改在 `motor/coordinator/router/dispatch.py` 处根据当前可用实例角色 (prefill / decode / union) 动态选择 `UnifiedPDRouter` 或 `PDHybridRouter`; `motor_deploy_config.deploy_mode` 仅保留用于选择 `infer_service_set` / `multi_deployment` / `single_container` 等部署形态, 不参与推理行为选择。

2. **Connector → Capability 推导**: NodeManager 从 vLLM 的 `kv_transfer_config.kv_connector` 或显式 `dispatch_profile` 推导 `dispatch_capabilities`; SGLang 则自动上报 `concurrent_engine_sync`。Capability 决定 dispatch plan (`concurrent_engine_sync` 或 `prefill_handoff_decode`), Coordinator 按 `engine_type` 选协议 Adapter 并对 P/D 两端兼容元数据做保护性校验。

3. **vLLM Connector 白名单 (大小写不敏感)**: 内置识别 `MooncakeConnectorV1` / `MooncakeHybridConnector` / `NixlConnector` → `prefill_handoff_decode`; `MooncakeLayerwiseConnector` → `concurrent_engine_sync`; `MultiConnector` 取 `kv_connector_extra_config.connectors[0]` 递归判定 (传输层连接器, 要求至少 2 个)。不在白名单且 `connectors[0]` 不可识别 → `unknown` 且**不产生 capability**。

4. **fail-closed 兜底**: 原生 vLLM P/D 启动只接受 `handoff` 或 `trigger` 语义, 未知或不兼容 Connector 会在 NodeManager 构造启动命令时**直接失败**, 不把错误推迟到 KV 传输阶段; 同一集群内 `handoff` 与 `trigger` 实例**不可混部**, Coordinator 返回 503。

5. **Worker Metaserver (Trigger/Layerwise 通路)**: 由 `motor_coordinator_config.inference_workers_config.worker_metaserver_base_port` 控制 (默认 `12000`), 每个 Inference Worker 在独立端口 `base+worker_index` 上监听 `POST /v1/metaserver`, 与推理口 `SO_REUSEPORT` **不共用**; 设为 `0` 可关闭; Decode 引擎回调时**不携带 API Key 且不走推理面 TLS**; 端口冲突或启动失败仅禁用该 Worker 的 Trigger (请求 503), 不拖垮推理口。

6. **dispatch_profile 显式声明**: 对白名单外的自定义 connector, 需在 `motor_engine_prefill_config` / `motor_engine_decode_config` **顶层** (与 `engine_type` 同级, 非 `engine_config` 内部) 设置 `dispatch_profile`: `handoff` → `prefill_handoff_decode`, `trigger` → `concurrent_engine_sync`; P/D 两端**必须一致**且与 Connector 协同语义匹配。

7. **SGLang Bootstrap 协议**: SGLang 不复用 vLLM 的 `kv_transfer_params`, NodeManager 从 `engine_config.disaggregation_bootstrap_port` (兼容 `disaggregation-bootstrap-port`) 派生每个 Pod 的 `bootstrap_port` 并在 endpoint 元数据中上报; Coordinator SGLang Adapter 将 Prefill endpoint 的 `bootstrap_host` / `bootstrap_port` 与稳定 `bootstrap_room` 注入 Prefill/Decode 请求, `business_port` 仍作推理 HTTP 服务端口。

---

## 【关键机制与数据】

### 1. 工作原理 (三段式)

**(a) 入口派发**
Client → Coordinator → `dispatch.py` 探查可用实例角色 → 按"角色组合 → Router"映射表分流; 同时存在 `prefill`+`decode` 时走 `UnifiedPDRouter` (双角色 P/D 协同), 仅 `union` 或降级到只有 `prefill` 时走 `PDHybridRouter`。其他组合返回 503。

**(b) 能力推导**
- vLLM 路径: NodeManager 优先读 `kv_transfer_config.kv_connector`; 命中白名单 → 固定 capability; 命中 `MultiConnector` → 取 `connectors[0]` 递归判断; 都未命中 → 若用户已显式设置 `dispatch_profile` 则按 `handoff`/`trigger` 推导, 否则报 `unknown` (启动 fail-closed)。
- SGLang 路径: 自动上报 `concurrent_engine_sync`, 由 SGLang Adapter 用自家 bootstrap 协议串接, Coordinator 不介入 KV 编排细节。

**(c) Metaserver 协调 (Trigger)**
Decode 引擎先启动, 经 Worker metaserver (`POST /v1/metaserver?attempt=N`, 地址优先 `POD_IP`, 否则 `coordinator_api_host`) 触发 Prefill; Prefill 按层将 KV 回推到 Decode, Decode 聚合后向 Client 流式吐 token。Worker metaserver 是 Trigger 模式必有的"旁路", 与推理口**端口隔离**, 监听地址不绑 loopback 以便跨节点回调。

### 2. 关键参数 (原文)

| 参数 | 默认值 / 取值 | 作用 |
|------|--------------|------|
| `worker_metaserver_base_port` | `12000` | Worker metaserver 起始端口 (worker_index 偏移) |
| `worker_metaserver_base_port = 0` | 关闭 | 整体禁用 metaserver → Trigger 模式不可用 |
| Trigger 端口冲突 / 启动失败 | — | 仅禁该 Worker 的 Trigger, 返回 503, 不影响推理口 |
| `handoff` vs `trigger` 混部 | — | Coordinator 返回 503 |
| KV 池类连接器 (`AscendStoreConnector`、`MooncakeConnectorStoreV1`、`UCMConnector`、`LMCacheAscendConnector`) | — | 仅作 `connectors[1]` 后端, **不**参与 capability 判定 |

### 3. 性能数据 / 计时
原文未给出任何吞吐、时延、P99 等量化指标; 只有逻辑层面的 fail-closed、超时降级 (返回 503) 等控制行为。

---

## 【表格解读】

### 表 1: 可用角色 → Router (原文逐字还原)

| 可用角色 | Router |
|----------|--------|
| 同时存在 `prefill` 和 `decode` | `UnifiedPDRouter` |
| 存在 `union` | `PDHybridRouter` |
| 仅存在 `prefill` | `PDHybridRouter`, 用于 PD 降级 |
| 其他组合 | 返回 503 |

**解读**: 此表定义了 Coordinator 的 role-to-router 派发策略。前两行体现"理想态": 双角色齐备则启用统一 PD 路由, 实现完整 Prefill→Decode 串行; 存在 `union` 或降级到只有 `prefill` 时切换到 `PDHybridRouter`, 把 Decode 任务合并回 Prefill 节点兜底执行 (降级时不真正分离, 避免服务中断)。第三行专为"只有 Prefill 实例"的异常场景设计兜底路由, 防止无可用 Decode 时业务雪崩。第四行是 fail-closed 兜底: 任何"既无 prefill+decode, 又无 union"的不合规部署直接 503, 不静默放行。

---

### 表 2: Connector 能力 → Dispatch plan (原文逐字还原)

| Connector 能力 | Dispatch plan |
|----------------|---------------|
| `concurrent_engine_sync` | P/D 并发执行, 由引擎同步 KV |
| `prefill_handoff_decode` | Prefill 完成后将结果交给 Decode |

**解读**: 这是 capability 到调度行为的总映射。"并发执行 / 引擎自同步 KV" 对应 trigger / layerwise 模式 (如 `MooncakeLayerwiseConnector`): Decode 先起跑再触发 Prefill, 按层流式回推 KV; "P 完成后移交 D" 对应 handoff 模式 (如 Mooncake / NixlConnector): Prefill 算完再调度 Decode, 实现松耦合串行。Coordinator 不关心内部传输细节, 只根据 capability 选择上述两种 dispatch plan 之一。

---

### 表 3: vLLM `kv_connector` 白名单 (原文逐字还原)

| `kv_connector` | 推导出的 capability |
|----------------|---------------------|
| `MooncakeConnectorV1` | `prefill_handoff_decode` |
| `MooncakeHybridConnector` | `prefill_handoff_decode` |
| `NixlConnector` | `prefill_handoff_decode` |
| `MooncakeLayerwiseConnector` | `concurrent_engine_sync` |
| `MultiConnector` | 取 `kv_connector_extra_config.connectors[0]` (传输连接器, 要求至少 2 个) 递归判定 |

**解读**: 这是 vLLM 路径的 capability 推导白名单。大小写不敏感, 命中前三项的统一切到 handoff 模式 (即"先 Prefill 再 Decode"的传统异步迁移语义); `MooncakeLayerwiseConnector` 例外, 因为它的协议本身就是引擎层同步 (`MooncakeLayerwiseConnector` 推导为 `trigger`), 需要 Decode 先跑起来按层取 KV; `MultiConnector` 是一个"递归探测"层 — 因为它本身只是包装器, 真正决定 capability 的是它串的第一个传输连接器 (`connectors[0]`), 所以必须配置至少 2 个 connector 才合理。原文同时强调: KV 池 / 存储类连接器 (`AscendStoreConnector`、`MooncakeConnectorStoreV1`、`UCMConnector`、`LMCacheAscendConnector`) 一般作为 `connectors[1]` 后端使用, **不**参与 capability 判定, 因此不需要进白名单。

---

### 表 4: 显式 `dispatch_profile` → capability (原文逐字还原)

| `dispatch_profile` | 推导出的 capability | 协同行为 |
|--------------------|---------------------|----------|
| `handoff` | `prefill_handoff_decode` | Prefill 完成后交给 Decode |
| `trigger` | `concurrent_engine_sync` | Decode 先启动, 经 Worker metaserver 触发 Prefill; 引擎按层同步 KV |

**解读**: 这是"未被白名单识别 connector"的逃生口。`handoff` 等同于"先 P 再 D"的传统 Mooncake/Nixl 语义, 与上述白名单前 3 项 capability 一致; `trigger` 等同于 layerwise 协同 (与 `MooncakeLayerwiseConnector` 推导一致), 但由用户显式声明, 适合自定义 connector 实现 trigger 语义时强制启用。原文强调: 原生 vLLM P/D 同时支持 `handoff` 与 `trigger`, **同一集群内不可混部** (Coordinator 返 503); SGLang 仍用自家 bootstrap 协议, 不进入此表。

---

## 【公式解读】

**原文无公式**。文档以表格 + 状态机 / 配置示例的形式描述, 未给出数学公式或 LaTeX 表达式。

---

## 【关联】

- **`../user_guide/deployment/k8s/pd_disaggregation_deployment.md`**: 部署实施手册, 涵盖 `infer_service_set` / `multi_deployment` / `single_container` 等部署形态的具体 yaml 与 pod 配置; 与本文档"拓扑自动识别"章节耦合 — `motor_deploy_config.deploy_mode` 仅在此处生效。
- **`../user_guide/configuration/config_reference.md#dispatch_profile`**: `dispatch_profile` 字段全量参数说明, 涵盖 `engine_config` 嵌套层级、与 `engine_type` 同级的写法约束、以及 P/D 两端取值一致性校验规则 — 是本文"自定义 connector 配置示例"和"fail-closed"段的字段级权威定义。
- **上下游模块**:
  - **上游**: vLLM / SGLang 引擎原生 P/D 协议 (`kv_transfer_config`、bootstrap 端口) — 提供原始 connector 名称和元数据。
  - **下游**: NodeManager (Connector capability 上报 + 启动命令构造)、Inference Worker (metaserver 监听 + DO remote prefill)、Prefill / Decode 引擎实例 (KV 传输执行体)。
  - **同层**: Coordinator Adapter 层 (vLLM 原生协议 vs SGLang bootstrap 协议)、UnifiedPDRouter / PDHybridRouter (role-driven 派发)。

---

## 【使用方法】

**(a) 标准 vLLM PD (handoff) — 使用白名单内 connector**
无需任何额外字段, 直接配置 `kv_transfer_config.kv_connector` 为 `MooncakeConnectorV1` / `MooncakeHybridConnector` / `NixlConnector` 即可, capability 自动推导为 `prefill_handoff_decode`。

**(b) Layerwise / Trigger 模式 — vLLM**
方法 1: 直接配 `kv_connector = "MooncakeLayerwiseConnector"`, 自动推导 `concurrent_engine_sync`。
方法 2: 自定义 connector 时, 在 `motor_engine_prefill_config` 与 `motor_engine_decode_config` **顶层**显式写 `"dispatch_profile": "trigger"` (与 `engine_type` 同级, 非 `engine_config` 内部)。
同时需保证 `worker_metaserver_base_port` ≠ 0 (默认 `12000`); 跨节点场景下保证 `POD_IP` 可达或 `coordinator_api_host` 已配置 (不绑 loopback)。

**(c) 自定义 connector 不在白名单 — 显式 `dispatch_profile`**
原文给出完整 JSON 模板:

```json
"motor_engine_prefill_config": {
  "engine_type": "vllm",
  "dispatch_profile": "handoff",
  "engine_config": {
    "kv_transfer_config": {
      "kv_connector": "YourCustomConnector",
      "kv_role": "kv_producer"
    }
  }
},
"motor_engine_decode_config": {
  "engine_type": "vllm",
  "dispatch_profile": "handoff",
  "engine_config": {
    "kv_transfer_config": {
      "kv_connector": "YourCustomConnector",
      "kv_role": "kv_consumer"
    }
  }
}
```
约束: P/D 两端 `dispatch_profile` 必须一致; handoff 与 trigger 实例**不可同集群混部**; `dispatch_profile` 不可写入 `engine_config` 内部。

**(d) SGLang Bootstrap 模式**
在 SGLang 引擎配置中设置 `engine_config.disaggregation_bootstrap_port` (兼容 `disaggregation-bootstrap-port`), NodeManager 自动派生每个 Pod 的 `bootstrap_port`, 上报到 Coordinator endpoint 元数据; 后续无需任何 trigger / handoff 配置, SGLang Adapter 会自动注入 `bootstrap_host` / `bootstrap_port` / `bootstrap_room` 到请求。

**(e) Kill Switch**
`worker_metaserver_base_port = 0` 关闭 Worker metaserver → trigger/layerwise 模式整体不可用 (请求 503), 但不影响 handoff 与推理口。

**(f) 完整参数定义**
详见内链 `../user_guide/configuration/config_reference.md#dispatch_profile`。
