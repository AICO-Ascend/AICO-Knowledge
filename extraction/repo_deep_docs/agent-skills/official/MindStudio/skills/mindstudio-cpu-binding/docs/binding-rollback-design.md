# 自动绑核执行与回滚设计

> 仓 `agent-skills` · 路径 `official/MindStudio/skills/mindstudio-cpu-binding/docs/binding-rollback-design.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/agent-skills/official/MindStudio/skills/mindstudio-cpu-binding/docs/binding-rollback-design.md

# 深度解读：自动绑核执行与回滚设计

## 【定位】

本文档定义了 `mindstudio-cpu-binding` 在昇腾 AI 研发场景中如何统一管理 CPU 绑核操作的执行前校验、执行后状态保存、审计记录与回滚语义，解决"绑核后可恢复、可验证、可审计"的核心问题，确保不同执行后端（`taskset` / 内部脚本）共享一致的回滚契约。

---

## 【技术要点】

1. **双执行后端架构**：第一版支持两类后端——`taskset`（直接调用系统 `taskset -cp <cpu-list> <pid>`，用于简单临时绑核、实验验证）与 `internal-script`（调用内部成熟绑核脚本，用于团队标准化绑核流程、生产前验证）。Skill 不应把内部脚本逻辑硬编码到诊断规则中，而应通过执行适配器接入。

2. **统一前置流程**：无论使用哪种后端，必须经过相同的 8 步流程：`读取当前 affinity → 校验 PID 仍存在 → 校验目标 CPU 在 cpuset_cpus_effective 内 → 保存 rollback-state.json → 展示 current→target diff → 用户确认 → 调用执行后端 → 重新读取 affinity 验证结果 → 记录执行日志`。

3. **内部脚本接入最低要求**：必须具备 apply/rollback 或 apply/query 能力，能对指定 PID 应用 CPU affinity、返回成功/失败退出码、失败时输出可读错误信息；**不得隐式 kill/restart 进程，不得修改 cgroup、IRQ affinity、CPU governor、kernel 参数等中高风险系统配置**（除非后续单独设计权限边界）。

4. **rollback-state.json 状态机**：`status` 字段包含 5 种取值：`pending` / `applied` / `failed` / `rolled_back` / `rollback_failed`，配套有 `before`（执行前原始 affinity）、`target`（计划 affinity）、`after`（执行后实测 affinity）三段快照。

5. **PID 复用防护**：通过 `process_start_time` 字段（可选，来源于 Linux `/proc/<pid>/stat` starttime）避免 PID 复用导致误回滚；PID 已退出时标记 `no_target`，PID 复用且 starttime 不一致时标记 `pid_reused`。

6. **多 PID 非原子性策略**：第一版**不承诺跨 PID 原子性**；策略为顺序执行、任一失败即停止后续动作、已成功 action 保留可回滚状态，报告中明确区分已应用 / 失败 / 未执行三类 PID。

---

## 【关键机制与数据】

### 工作原理（执行适配器分层）

原文：通过 `BindingExecutor` 统一封装执行，采用组合模式：

```text
BindingExecutor
├── TasksetExecutor
└── InternalScriptExecutor
```

`BindingExecutor` 是抽象入口，两个子类分别实现不同后端，但共享相同的"前置校验 → 状态保存 → 确认 → 执行 → 后置验证 → 日志"流水线。原文强调这是**替换性设计**——后端可替换，但前置/状态/审计/回滚语义由 Skill 统一管理。

### 数据流（执行链路）

原文 8 步前置流程节点：

| 步骤 | 动作 | 关键校验点 |
|------|------|----------|
| 1 | 读取当前 affinity | 来源 `/proc/<pid>/status` Cpus_allowed_list |
| 2 | 校验 PID 仍存在 | kill -0 或 /proc 检查 |
| 3 | 校验目标 CPU 在 cpuset_cpus_effective 内 | 避免越界绑核 |
| 4 | 保存 rollback-state.json | 含 before/target 快照 |
| 5 | 展示 current → target diff | 人工核对 |
| 6 | 用户确认 | 交互门控 |
| 7 | 调用执行后端 | taskset 或 internal-bind |
| 8 | 重新读取 affinity 验证结果 | 写后读 |

### 回滚数据流

原文：回滚必须先验证当前对象仍是原进程：

```text
读取 rollback-state.json
  -> 检查 action.status 是否为 applied
  -> 检查 PID 是否存在
  -> 可选检查 process_start_time 是否一致
  -> 读取当前 affinity
  -> 展示 current -> original diff
  -> 用户确认
  -> 调用回滚后端
  -> 重新读取 affinity 验证结果
  -> 更新 rollback-state.json 状态
```

性能数据：原文未给出具体性能基准数字，仅描述实验计划中的行为期望。

### 实验计划覆盖的关键边界

原文定义了 5 个实验：单 PID apply/rollback、PID 退出（期望 `no_target`）、PID 复用（期望拒绝回滚）、多 PID 部分失败（第一个 `applied`、第二个 `failed`、后续停止）、内部脚本后端（状态文件与实际 affinity 一致）。

---

## 【表格解读】

### 表格 1：执行后端类型（原文第 2 节）

| 后端 | 说明 | 推荐用途 |
|------|------|----------|
| `taskset` | 直接调用系统 `taskset -cp <cpu-list> <pid>` | 简单临时绑核、实验验证 |
| `internal-script` | 调用内部成熟绑核脚本 | 团队标准化绑核流程、生产前验证 |

**逐行解读**：
- **`taskset` 行**：作为最简实现路径，直接复用 Linux `taskset` 命令，适合实验验证或临时调试；推荐用途限定在"简单临时"场景，不进入生产主线。
- **`internal-script` 行**：通过 `internal-bind` 接口封装团队内部成熟绑核脚本，用于生产前验证；隐含了"脚本需经过内部验证"的先决条件。

### 表格 2：rollback-state.json 字段说明（原文第 5 节）

| 字段 | 说明 |
|------|------|
| `pid` | 原目标 PID。 |
| `process_start_time` | 可选，用于避免 PID 复用误回滚。Linux 可来自 `/proc/<pid>/stat` starttime。 |
| `before.cpus_allowed_list` | 执行前原始 affinity，回滚核心依据。 |
| `target.cpus_allowed_list` | 计划应用的 affinity。 |
| `after.cpus_allowed_list` | 执行后重新读取到的 affinity。 |
| `status` | `pending` / `applied` / `failed` / `rolled_back` / `rollback_failed`。 |

**逐行解读**：
- **`pid` 字段**：仅记录 PID 不足以唯一定位进程（PID 可被复用），因此需配合 `process_start_time`。
- **`process_start_time` 字段**：标注为"可选"，但在 PID 复用防护场景中是核心判据；数据源是 Linux `/proc/<pid>/stat` 中的 starttime 字段（系统启动后的 tick 数）。
- **`before.cpus_allowed_list` 字段**：被原文明确为"回滚核心依据"，即回滚动作的目标亲和性 = `before`。
- **`target.cpus_allowed_list` 字段**：是计划应用值而非最终值；最终值由 `after` 字段实证。
- **`after.cpus_allowed_list` 字段**：用于验证执行是否真正生效；若 `after` 与 `target` 不一致，标记 `failed`。
- **`status` 字段**：5 个取值覆盖完整生命周期：`pending`（待执行）→ `applied`（已应用）→ `rolled_back`（已回滚）/ `rollback_failed`（回滚失败）；`failed` 表示 apply 阶段失败但未回滚。

### 表格 3：rollback-state.json 完整结构（原文第 5 节 JSON 示例，逐字还原）

```json
{
  "schema_version": "0.1.0",
  "created_at": "2026-06-01T10:30:00+08:00",
  "executor_backend": "taskset",
  "snapshot_ref": "snapshot.json",
  "plan_ref": "plan.json",
  "actions": [
    {
      "action_id": "bind-pid-12345",
      "pid": 12345,
      "process_start_time": "optional-proc-starttime-or-null",
      "command": "python train.py --local_rank=0",
      "before": {
        "cpus_allowed_list": "0-127",
        "mems_allowed_list": "0-1"
      },
      "target": {
        "cpus_allowed_list": "0-31"
      },
      "after": {
        "cpus_allowed_list": null
      },
      "status": "pending",
      "apply_command": "taskset -cp 0-31 12345",
      "rollback_command": "taskset -cp 0-127 12345"
    }
  ]
}
```

**结构解读**（原文未给出表格形式，但属于状态文件核心结构，逐项说明）：
- **`schema_version: "0.1.0"`**：状态文件 schema 版本，便于后续兼容性演进。
- **`created_at: "2026-06-01T10:30:00+08:00"`**：ISO 8601 含时区时间戳。
- **`executor_backend: "taskset"`**：记录实际使用的执行后端，用于回滚时选择适配器。
- **`snapshot_ref` / `plan_ref`**：通过引用外部 `snapshot.json` 与 `plan.json` 避免状态文件膨胀，保留溯源链路。
- **`actions[]`**：数组形式支持多 PID 场景（与第 7 节多 PID 非原子性对应）。
- **单 action 示例关键数字**：原始 affinity `0-127`（128 个 CPU），目标 `0-31`（32 个 CPU），`mems_allowed_list: "0-1"`（2 个 NUMA 节点）；apply 命令 `taskset -cp 0-31 12345`，rollback 命令 `taskset -cp 0-127 12345`，严格对称。
- **`after.cpus_allowed_list: null`**：表示执行后尚未回填（状态仍为 `pending`）；apply 成功后应回填实际读取值。
- **`status: "pending"`**：初始态；执行完成后应更新为 `applied` / `failed`。

---

## 【公式解读】

原文无数学公式或伪代码算法式表达。

文档中出现的代码块（`internal-bind` 命令行接口、JSON 状态文件、流程伪代码如 `读取当前 affinity -> 校验...`）均为命令规约或流程步骤而非数学公式，已分别在【技术要点】与【关键机制与数据】中还原解读。

---

## 【关联】

根据原文内容，本设计在仓库内的定位与关联如下（原文未提供内部链接，下述关系基于文档自身语义）：

### 上游依赖
- **`snapshot.json` / `plan.json`**：在 rollback-state.json 中以 `snapshot_ref` / `plan_ref` 引用，说明本设计依赖上游规划模块产出的 affinity 计划文件；本设计是**执行层**，不负责亲和性规划。
- **`cpuset_cpus_effective`**：前置流程第 3 步校验项，说明与 cgroup v1/v2 cpuset 子系统有依赖关系。

### 下游约束
- **HTML 报告**：第 9 节验收标准第 5 条明确"HTML 报告能展示执行后端、当前状态、应用命令、回滚命令和实验风险"，说明本设计的状态结构直接驱动下游报告模块的字段渲染。
- **审计日志**：前置流程最后一步"记录执行日志"，回滚流程最后一步"更新 rollback-state.json 状态"，二者共同支撑可审计性。

### 横向并列
- **`TasksetExecutor` 与 `InternalScriptExecutor`**：作为 `BindingExecutor` 的两个并列子模块，互为替换关系但共享同一契约。

### 未来扩展点
- 第 7 节末尾提到"后续可以实验是否支持失败自动回滚已成功动作"——这是一个明确留待后续版本的特性扩展点，本版明确**不支持**，由用户确认后手动回滚。
- 第 3 节"除非后续单独设计权限边界"——cgroup/IRQ affinity/CPU governor/kernel 参数修改被列为后续独立设计项。

### 内部链接说明
原文无内部链接引用，仓库路径 `official/MindStudio/skills/mindstudio-cpu-binding/docs/binding-rollback-design.md` 为相对定位。

---

## 【使用方法】

### 启用方式

根据原文第 2 节，本能力由 `mindstudio-cpu-binding` Skill 通过 `BindingExecutor` 统一封装调用；选择后端即启用对应执行链路。

### 配置项

| 配置维度 | 原文取值 |
|----------|----------|
| 执行后端选择 | `taskset` 或 `internal-script`（通过 `executor_backend` 字段记录） |
| 状态文件 schema 版本 | `"0.1.0"` |
| 内部脚本接口（建议） | `--apply` / `--rollback` / `--query` 三种子命令 |
| 状态字段 status 取值 | `pending` / `applied` / `failed` / `rolled_back` / `rollback_failed` |
| PID 退出场景标记 | `no_target` |
| PID 复用场景标记 | `pid_reused` |

### 命令（原文逐字保留）

**后端 1：`taskset`**

```bash
taskset -cp <cpu-list> <pid>
```

**后端 2：内部脚本（建议接口）**

```bash
internal-bind --apply --pid <pid> --cpu-list <cpu-list> [--reason <text>]
internal-bind --rollback --pid <pid> --cpu-list <original-cpu-list> [--state <rollback-state.json>]
internal-bind --query --pid <pid>
```

**回滚命令生成规则（基于状态文件）**

原文 rollback-state.json 示例中：
- Apply 命令：`taskset -cp 0-31 12345`（目标 affinity + 原 PID）
- Rollback 命令：`taskset -cp 0-127 12345`（原始 affinity + 原 PID）

### 内部脚本最低要求清单（逐字）

原文第 3 节明确列出 5 条最低要求：
1. 能对指定 PID 应用 CPU affinity。
2. 能返回成功/失败退出码。
3. 失败时输出可读错误信息。
4. 不隐式 kill 或 restart 进程。
5. 不修改 cgroup、IRQ affinity、CPU governor、kernel 参数等中高风险系统配置，除非后续单独设计权限边界。

### 实验验证（原文第 8 节）

需要 Linux 环境；包含 5 个实验：单 PID taskset 应用和回滚、PID 退出、PID 复用保护、多 PID 部分失败、内部脚本后端，每个实验均给出"准备 → 操作 → 期望结果"三段式步骤。

### 验收标准（原文第 9 节）

1. 任意执行动作前都能保存完整 rollback-state。
2. 回滚不会误作用到已退出或 PID 复用后的其他进程。
3. 执行失败不会丢失已成功 action 的回滚信息。
4. taskset 后端和内部脚本后端共享同一套状态文件与回滚流程。
5. HTML 报告能展示执行后端、当前状态、应用命令、回滚命令和实验风险。
