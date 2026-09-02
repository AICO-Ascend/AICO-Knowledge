# 故障场景重调度

> 仓 `mindie-motor` · 路径 `docs/zh/user_guide/features/fault_tolerance/rescheduler.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-motor/docs/zh/user_guide/features/fault_tolerance/rescheduler.md

# 故障场景重调度功能深度解读

## 【定位】
这篇文档描述 `mindie-motor` 中 `Coordinator` 在推理节点故障或断链导致推理中断时，将推理请求自动重调度到其他健康节点的容错能力，并给出其配置开关、重试策略与内存开销评估方法。

## 【技术要点】

1. **触发条件（双重故障场景）**：推理节点本身发生故障 **或** `Coordinator` 与推理节点之间异常断链，导致推理过程异常中断。
2. **开关参数**：`exception_config.reschedule_config.enable`，默认 `false`，即功能默认关闭；设为 `true` 时启用重调度。
3. **重调度次数配置**：优先读取 `transport_max_retry`；当 `transport_max_retry` 为空（`null`）时，回退使用 `max_retry`。原文示例中 `transport_max_retry: null`，`max_retry: 5`。
4. **重调度间隔算法**：使用 `retry_delay`（浮点秒数）作为基础等待时间；**第一次**故障等待 `retry_delay` 秒后进行重调度，**后续每次**重调度间隔是上一次重调度间隔的 **2 倍**（指数退避）。
5. **缓存对象与生命周期**：启用后，`Coordinator` 会缓存**流式请求**的 `prompt_tokens` 以及流式响应的 `tokens`，直至该推理任务结束才释放内存。
6. **内存评估口径**：原文给出经验系数——**1M token 约占用 3~6M 内存**，并按极端情况取**系数 6**进行上限估算；基于此推导出 `Coordinator` 总内存上限需预留 **`128G`**。

## 【关键机制与数据】

- **工作原理**：故障/断链 → `Coordinator` 判定推理中断 → 按 `retry_delay` 的指数退避策略（首等待 `retry_delay`，之后每次 ×2）将请求重新路由到其他正常推理节点 → 重试上限由 `transport_max_retry`（或 `max_retry`）控制。
- **数据流/缓存对象**：流式请求的 `prompt_tokens` + 流式响应的 `tokens`，全量驻留 `Coordinator` 内存直到推理任务结束。
- **内存数据（原文：10000 并发 + 1M 上下文 + 1M 长报文 极端场景）**：
  - 故障重调度功能内存占用上限 ≈ **60G**（`10000 × 1M × 系数6`）
  - 请求体缓存内存占用上限 ≈ **60G**（`10000 × 1M × 系数6`）
  - 合计下限 **> 120G**，实际建议设置 **128G**
- **基础资源示例（原文）**：`requests: memory "4Gi" / cpu "16"`，`limits: memory "128Gi" / cpu "64"`。

## 【表格解读】

原文无表格。文档中仅包含两段代码示例（`user_config.json` JSON 片段、`resources` YAML 片段），不属于表格。

## 【公式解读】

原文以伪公式形式给出两段内存估算式（未使用 LaTeX），逐字保留如下：

**公式一（故障重调度功能内存占用上限）**

```
故障重调度功能的内存占用上限 ≈ 并发数 × 上下文长度 × 系数6
```

- `并发数`：最大并发推理请求数（对应 `max_requests`）；
- `上下文长度`：单个请求的上下文 token 数；
- `系数6`：经验极端系数（1M token ≈ 3~6M 内存 的上限取值）；
- 作用：估算启用重调度后，为缓存流式请求的 `prompt_tokens` 与流式响应的 `tokens` 所需内存。
- 代入示例：`≈ 10000 × 1M × 6 ≈ 60G`。

**公式二（请求体缓存内存占用上限）**

```
请求体缓存的内存占用上限 ≈ 并发数 × 报文长度 × 系数6
```

- `并发数`：同上；
- `报文长度`：单个请求体的字节长度（原文以 1M 长报文作为极端场景代入）；
- `系数6`：同上；
- 作用：估算长报文请求体的缓存内存开销。
- 代入示例：`≈ 10000 × 1M × 6 ≈ 60G`。

**合计与建议**：总占用 `> 60G + 60G = 120G`，加 `Coordinator` 基础内存与其他功能开销，建议 `limits.memory = "128Gi"`。

## 【关联】

- **`user_config.json` 配置参考**：本功能的全部参数（`reschedule_config.enable`、`max_retry`、`transport_max_retry`、`retry_delay`、`max_requests`）均位于 `motor_coordinator_config` 段，详见内部链接 `../../configuration/config_reference.md#motor_coordinator_config`。
- **YAML 部署模板**：内存上限需要修改部署 yaml 中 `coordinator` 容器的 `resources.limits.memory`，涉及两种部署模式：
  - CRD 模式 → `examples/deployer/yaml_template/infer_service_template.yaml`
  - Multi 模式 → `examples/deployer/yaml_template/coordinator_template.yaml`
- **上游功能关联**：依赖 `exception_config`（异常处理配置）与 `transport`（传输层）语义；`transport_max_retry` 即位于 `exception_config` 段，表明重调度与传输层重试共享同一参数体系。
- **下游影响**：开启该功能会显著拉高 `Coordinator` 内存上限（文中案例从基础 `4Gi` 提升到 `128Gi`），属于典型的"以内存换可用性"设计权衡。

## 【使用方法】

**启用方式（JSON 配置原文）：**

```json
{
  "motor_coordinator_config": {
    "exception_config": {
      "reschedule_config": {
        "enable": true
      },
      "max_retry": 5,
      "transport_max_retry": null,
      "retry_delay": 0.2
    }
  }
}
```

**配置项说明（原文有则写）：**

| 配置项 | 取值/类型 | 含义 |
|---|---|---|
| `exception_config.reschedule_config.enable` | `false` / `true`，默认 `false` | 故障场景重调度功能开关 |
| `exception_config.transport_max_retry` | 整数，为空时回退 | 重调度次数；为空则使用 `max_retry` |
| `exception_config.max_retry` | 整数（如 `5`） | `transport_max_retry` 为空时的回退重试次数 |
| `exception_config.retry_delay` | 浮点秒数（如 `0.2`） | 首次重调度等待时间，后续每次翻倍 |
| `max_requests`（同 `motor_coordinator_config`） | 整数 | 最大并发数，用于内存公式代入 |
| `resources.limits.memory`（YAML，`coordinator` 容器） | 如 `"128Gi"` | `Coordinator` 内存上限，按公式估算后设置 |

**调优流程（基于原文）：** 先按业务 `最大并发数` 与 `上下文长度` 套用 `并发数 × 上下文长度 × 6` 估算重调度内存，再叠加 `并发数 × 报文长度 × 6` 的请求体缓存，最后加上 `Coordinator` 基础开销与其它功能占用，得到 `limits.memory` 建议值。
