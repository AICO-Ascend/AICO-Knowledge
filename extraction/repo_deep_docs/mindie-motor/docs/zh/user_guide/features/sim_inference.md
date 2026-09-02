# 虚推健康探测

> 仓 `mindie-motor` · 路径 `docs/zh/user_guide/features/sim_inference.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-motor/docs/zh/user_guide/features/sim_inference.md

# 「虚推健康探测」feature 文档深度解读

## 【定位】

这篇文档描述了 mindie-motor 在业务低负载时通过主动向推理面发送轻量推理请求、并结合 NPU AI Cube 利用率来检测推理引擎「静默故障」（引擎进程存活、`/health` 正常但实际无法推理）的能力，统一定义其启用条件、动态探测间隔、异常判定逻辑及配置项。

---

## 【技术要点】

1. **能力范围与边界**：虚推（virtual inference）**仅支持 vLLM**，通过 `POST /v1/completions`（`prompt:"1"`、`max_tokens:1`，`X-Request-Id: {timestamp}_virtual`）发往推理面；**SGLang 不参与 Motor 虚推**，SGLang 由自身在 `/health` 中执行生成式健康检查（通过 NodeManager 拉起时显式写入 `SGLANG_ENABLE_HEALTH_ENDPOINT_GENERATION=true` 强制开启）。

2. **执行路径**：在 Native Launch 路径下，由 **Node Manager** 直接执行（`motor/node_manager/core/services/native_engine/virtual_inference/`），不再依赖 Engine Server 的 mgmt 面；每个 NodeManager 实例仅维护**单个**虚推 monitor，仅绑定有效 DP0 target；首次观察到该 target `READY` 后**幂等启动**虚推循环。

3. **HDK 版本硬约束**：仅支持 **HDK 26.0.RC1** 及以后版本（`npu-smi info watch -s u` 提供 AI Cube Usage 指标）；不支持时自动关闭虚推。

4. **双超时设计**：warmup（首次）请求固定 **180 秒**（独立于配置），周期性请求使用 `health_check_config.virtual_inference_timeout`（默认 **5 秒**），**仅对 vLLM 生效**。

5. **动态探测间隔**：依据 5 秒采样窗口内 AI Cube 利用率峰值分档——`≥80%` → 20 秒；`< npu_usage_threshold` → 5 秒（默认）；`[npu_usage_threshold, 80%)` → 保持当前间隔不变。

6. **异常判定与状态降级**：vLLM 在 AI Cube 峰值 `< npu_usage_threshold` 且虚推失败时累计连续失败次数；达到 `max_failure_count`（默认 6）后，endpoint 状态由 `READY` 降为 `UNHEALTHY`，心跳上报 `ABNORMAL`，虚推循环停止，**不杀进程、不重启引擎**；AI Cube ≥ threshold 时视为繁忙不累计；采样不可用也不累计；监控循环自身异常仅记日志退避重试，**不判定引擎异常**。

---

## 【关键机制与数据】

**原文：状态上报与自杀重调度语义**：`HeartbeatManager` 保持现有状态映射与连续异常恢复语义——**连续 5 次上报 abnormal 后触发节点自杀重调度**。虚推仅改变状态上报，不触发进程重启或 Pod 级恢复。

**原文：拉起时 AI Cube 支持检测**：启动时通过 `npu-smi info watch -h` 校验 HDK 是否支持 AI Cube Usage；不支持则自动关闭虚推。

**原文：vLLM 引擎启动环境门禁**：NodeManager 在 `pull` 时由 `NativeEngineService` 先走 `should_enable_vllm_virtual_inference`，**仅对原本 eligible 的 vLLM target** 再读最终引擎启动环境 `launch_spec.command.env` 的 `ASCEND_GLOBAL_LOG_LEVEL`——不是 NodeManager 自身的 `os.environ`，也不是 deploy 侧改写的 `user_config`。未设置/`None`/空字符串/纯空白视为默认 ERROR 并允许；`str(...).strip()` 后等于 `"3"` 允许；其它显式值不创建 vLLM monitor、打印 warning、不杀/不重启已成功拉起的引擎，经 `reconcile(None)` 清理旧 monitor。该限制仅约束 Motor vLLM 虚推，不影响 SGLang 原生生成式 `GET /health`。

**原文：vLLM layerwise decode 与 handoff decode 的差异**：`dispatch_profile=trigger`（layerwise decode）的虚推请求额外携带 `kv_transfer_params.do_virtual: true` 及 PD 分离相关字段；handoff decode 与 Prefill/Union 角色发送**普通 completion 请求**。

**原文：监控循环自身异常处理**：出现未预期异常时，仅记录日志并退避重试，不据此判定引擎异常（不累计失败次数、不降级 `UNHEALTHY`）。

**原文：指标保留行为**：vLLM 虚推请求保留 `_virtual` 请求 ID 标识；**不执行** vLLM per-request 指标过滤（`patch_vllm_metrics` 未迁移），Engine Server 侧旧逻辑将在其整体删除时移除。

**原文：NPU 负载采样**：使用 `npu-smi info watch -s u` 采集 AI Cube 利用率（5 秒采样窗口内取峰值）。

---

## 【表格解读】

### 表格 1：动态探测间隔（原文逐字还原）

| AI Cube 利用率峰值（5 秒采样窗口） | 下一轮间隔 |
|-----------------------------------|------------|
| ≥ 80% | 20 秒 |
| < `npu_usage_threshold` | 5 秒（默认） |
| `[npu_usage_threshold, 80%)` | 保持当前间隔不变 |

**逐行解读**：
- **≥ 80%**：引擎处于高负载，下一轮探测间隔放大到 **20 秒**，避免在重负载期间叠加轻量请求造成干扰，体现"业务优先"原则。
- **< `npu_usage_threshold`**（默认 3%）：引擎理论上"应该空闲但仍失败"，说明很可能是静默故障；按 **5 秒**（默认值）紧密探测，尽快暴露故障。
- **`[npu_usage_threshold, 80%)`**：中等负载区间，**保持当前间隔不变**（不退避也不加紧），避免在波动负载下频繁调整探测节奏。

---

### 表格 2：health_check_config 配置项（原文逐字还原）

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| enable_virtual_inference | bool | `false` | Motor 主动虚推开关。**仅关闭/开启 vLLM 的 Motor 虚推**；`false` **不会**关闭 SGLang 原生生成式 `/health`（拉起时 env 恒为 `true`）。仅 DP rank 0、非 headless 的 vLLM endpoint 生效。另需最终引擎环境 `ASCEND_GLOBAL_LOG_LEVEL` 为 ERROR（未设置默认 ERROR）；显式非 ERROR 时 NodeManager 不创建 monitor 并 warning |
| npu_usage_threshold | int | `3` | AI Cube 利用率阈值（%）；仅 vLLM Motor 虚推使用 |
| max_failure_count | int | `6` | 连续虚推失败次数上限；仅 vLLM Motor 虚推使用 |
| virtual_inference_timeout | float | `5.0` | **周期性**主动虚推请求的客户端超时（秒），必须为正数，**仅对 vLLM Motor 虚推生效**；首次 warmup 请求固定 180 秒，不受此配置影响。配置保留兼容，SGLang 忽略该字段 |
| health_collector_timeout | int | `5` | 推理面 `GET /health` 探测超时（秒）；vLLM 与 SGLang 心跳均使用 |
| health_collector_timeout_retry_attempts | int | `3` | 推理面 `GET /health` 超时重试次数（含首次，仅超时触发）；vLLM 与 SGLang 心跳均使用 |

**逐行解读**：
- **enable_virtual_inference**：主开关，默认关闭。该开关仅控制 vLLM 的 Motor 虚推，**与 SGLang 的生成式 `/health` 完全解耦**——SGLang 的 `SGLANG_ENABLE_HEALTH_ENDPOINT_GENERATION` 在 NodeManager 拉起时被强制写入并恒为 `true`，不受 `enable_virtual_inference` 影响，也不受容器外部同名环境变量影响。生效范围进一步收窄到 **DP rank 0 且非 headless** 的 vLLM endpoint；同时受最终引擎环境 `ASCEND_GLOBAL_LOG_LEVEL` 是否为 ERROR 的门禁控制。
- **npu_usage_threshold**：判定"AI Cube 利用率是否过低"的关键阈值，单位为百分比，默认 **3%**——非常敏感，意味着只要 5 秒采样窗口内峰值低于 3% 就认为引擎空闲、虚推请求应当被认真对待。
- **max_failure_count**：连续失败累计上限，默认 **6** 次；达到后只做状态降级与心跳上报，**不做进程级恢复动作**。
- **virtual_inference_timeout**：周期性虚推的客户端超时（秒），默认 **5.0 秒**，必须为正数；首次 warmup 请求硬编码 180 秒，不受此配置影响；SGLang 忽略该字段（仅保留兼容性）。
- **health_collector_timeout**：`GET /health` 心跳探测超时（秒），默认 5 秒；vLLM 与 SGLang **共用**该参数。
- **health_collector_timeout_retry_attempts**：`GET /health` 超时重试次数（含首次），默认 3 次；**仅在超时时触发**重试；同样由 vLLM 与 SGLang 共用。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **`health_check_config` 配置块**：虚推全部可调参数均落在 `user_config` 中 `motor_engine_prefill_config` / `motor_engine_decode_config` 的 `health_check_config` 子块；字段详细说明参见文末内部链接 **`../configuration/config_reference.md#health_check_config`**。

- **`HeartbeatManager` 状态机**：虚推触发的 `UNHEALTHY/ABNORMAL` 状态最终由 `HeartbeatManager` 上报；连续 5 次 abnormal 会触发节点自杀与重调度，构成"虚推 → 心跳异常 → 节点重调度"这条故障传播链。

- **Native Engine Service 与 Node Manager**：执行路径位于 `motor/node_manager/core/services/native_engine/virtual_inference/`，由 `NativeEngineService` 在创建 vLLM monitor 前判定 `should_enable_vllm_virtual_inference`，并在 `runtime_state()` 中合并原生 `/health` 与虚推状态——意味着虚推是 Node Manager 原生路径下的内建能力，**不再依赖 Engine Server 的 mgmt 面**。

- **SGLang 健康检查机制**：通过 `SGLANG_ENABLE_HEALTH_ENDPOINT_GENERATION` 与 Motor 虚推形成平行但独立的能力——SGLang 的生成式 `/health` 由 SGLang 自身提供，Motor 仅做心跳；Motor 的虚推只面向 vLLM。两者共用 `health_collector_timeout` / `health_collector_timeout_retry_attempts` 这两个心跳参数。

- **HDK / npu-smi**：AI Cube 利用率指标依赖 `npu-smi info watch -s u`，要求 **HDK 26.0.RC1+**；启动时还通过 `npu-smi info watch -h` 校验可用性——将虚推能力与底层驱动/HW 版本强绑定。

- **vLLM 内部机制**：`patch_vllm_metrics`（per-request 指标过滤）在 Engine Server 旧路径中存在，但虚推路径下未迁移——说明虚推是脱离 Engine Server 的新实现路径，旧指标过滤逻辑将在 Engine Server 整体删除时一并移除。

---

## 【使用方法】

**原文：在 PD 分离部署的 `user_config.json` 中，将 Prefill 与 Decode 引擎配置的 `health_check_config.enable_virtual_inference` 设为 `true`，并按业务调整 `npu_usage_threshold`、`max_failure_count`。原生拉起路径下虚推由 Node Manager 执行，无需（也不依赖）Engine Server 参与。**

启用流程：
1. 编辑 `user_config.json`，在 `motor_engine_prefill_config` 与 `motor_engine_decode_config` 下配置 `health_check_config`：
   ```json
   "health_check_config": {
     "enable_virtual_inference": true,
     "npu_usage_threshold": 3,
     "max_failure_count": 6,
     "virtual_inference_timeout": 5.0,
     "health_collector_timeout": 5,
     "health_collector_timeout_retry_attempts": 3
   }
   ```
2. 确保部署环境为 **HDK 26.0.RC1+**（提供 `npu-smi info watch -s u` 的 AI Cube Usage 指标）。
3. 确认引擎环境 `ASCEND_GLOBAL_LOG_LEVEL` 为 ERROR（未设置/`None`/空/纯空白均视为默认 ERROR 允许；显式非 ERROR 则 NodeManager 不创建 monitor 并打印 warning）。
5. 生效范围自动收窄：**仅 DP rank 0、非 headless 的 vLLM endpoint** 会真正执行虚推；其他角色/引擎类型自动关闭。
