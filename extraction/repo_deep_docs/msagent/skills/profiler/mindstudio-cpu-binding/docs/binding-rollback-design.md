# 自动绑核执行与回滚设计

> 仓 `msagent` · 路径 `skills/profiler/mindstudio-cpu-binding/docs/binding-rollback-design.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msagent/skills/profiler/mindstudio-cpu-binding/docs/binding-rollback-design.md

# 《自动绑核执行与回滚设计》一体化深度解读

---

## 【定位】

本文档为 `mindstudio-cpu-binding` Skill 定义**执行后端适配、回滚状态保存、进程存活校验与回滚语义统一管理**的完整设计框架，解决"如何把内部绑核脚本安全接入诊断流程，并在执行前后保证可回滚、可审计、可验证"的问题。

---

## 【技术要点】

1. **双后端适配架构**：`taskset`（直接 `taskset -cp <cpu-list> <pid>`，实验验证用）与 `internal-script`（内部成熟绑核脚本，生产前验证用），统一通过 `BindingExecutor` 封装为 `TasksetExecutor` 与 `InternalScriptExecutor` 两种实现。
2. **内部脚本接口契约**：最低要求 5 项——可对指定 PID 设 affinity、返回成功/失败退出码、失败输出可读错误、不隐式 kill/restart、不修改 cgroup/IRQ affinity/CPU governor/kernel 参数等中高风险系统配置；接口形式为 `internal-bind --apply/--rollback/--query`。
3. **执行前置 7 步强制流程**：读取当前 affinity → 校验 PID 存在 → 校验目标 CPU 在 `cpuset_cpus_effective` 内 → 保存 `rollback-state.json` → 展示 current→target diff → 用户确认 → 调用执行后端（后接重新读取 affinity 验证与日志记录）。
5. **回滚前置 6 步校验流程**：读 `rollback-state.json` → 检查 `action.status == applied` → 检查 PID 存在 → 可选检查 `process_start_time`（来自 `/proc/<pid>/stat` starttime 防 PID 复用）→ 读当前 affinity → 展示 current→original diff 后用户确认。
6. **多 PID 不承诺原子性**：第一版采取"顺序执行，任一失败停止后续；已成功 action 保留可回滚；最终由用户确认是否回滚"的策略，状态字段支持 `pending` / `applied` / `failed` / `rolled_back` / `rollback_failed` 五态。

---

## 【关键机制与数据】

### 1. 状态文件结构（原文: rollback-state.json 示例）

执行回滚的核心依据是 `before.cpus_allowed_list`（原始 affinity），示例结构关键字段如下：

- `schema_version`: "0.1.0"
- `executor_backend`: "taskset"
- `snapshot_ref`: "snapshot.json"（关联前置快照）
- `plan_ref`: "plan.json"（关联绑核计划）
- `actions[].before.cpus_allowed_list`: "0-127"（原文示例，128 核系统原始 affinity）
- `actions[].target.cpus_allowed_list`: "0-31"（原文示例，目标 affinity）
- `actions[].apply_command`: "taskset -cp 0-31 12345"
- `actions[].rollback_command`: "taskset -cp 0-127 12345"
- `actions[].status`: "pending" → "applied" → "rolled_back"（或 `rollback_failed` / `failed`）

### 2. 数据流（执行侧）

```
读取当前 affinity
  -> 校验 PID 仍存在
  -> 校验目标 CPU 在 cpuset_cpus_effective 内
  -> 保存 rollback-state.json
  -> 展示 current -> target diff
  -> 用户确认
  -> 调用执行后端
  -> 重新读取 affinity 验证结果
  -> 记录执行日志
```

执行完成后 `after.cpus_allowed_list` 由 `null`（pending 态）填入实际读取值作为执行证据。

### 3. 数据流（回滚侧）

```
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

### 4. 边界行为（原文: 显式定义）

- **PID 已退出**：不执行回滚；标记为 `no_target`，提示原进程已不存在。
- **PID 复用且 `process_start_time` 不一致**：不执行回滚；标记为 `pid_reused`，提示需要人工确认。
- **多 PID 部分失败**：失败 action 之后的动作停止；已 applied 的 action 保留可回滚状态；第一版**不自动回滚**，由用户确认。

### 5. 性能数据

原文未涉及性能基准、耗时或吞吐数据。

---

## 【表格解读】

### 表 1：执行后端对比（原文第 2 节）

| 后端 | 说明 | 推荐用途 |
|------|------|----------|
| `taskset` | 直接调用系统 `taskset -cp <cpu-list> <pid>` | 简单临时绑核、实验验证 |
| `internal-script` | 调用内部成熟绑核脚本 | 团队标准化绑核流程、生产前验证 |

**解读**：表格将第一版支持的执行后端划分为两类——`taskset` 是 Linux 系统原生工具，无外部依赖，适合实验验证；`internal-script` 是团队内部封装，承担生产前标准化绑核流程。两类后端共享同一套 `rollback-state.json` 与回滚流程（原文第 9 节验收标准第 4 条明确要求）。Skill 层不硬编码任何脚本逻辑，仅通过适配器接入。

### 表 2：rollback-state.json 关键字段说明（原文第 5 节）

| 字段 | 说明 |
|------|------|
| `pid` | 原目标 PID。 |
| `process_start_time` | 可选，用于避免 PID 复用误回滚。Linux 可来自 `/proc/<pid>/stat` starttime。 |
| `before.cpus_allowed_list` | 执行前原始 affinity，回滚核心依据。 |
| `target.cpus_allowed_list` | 计划应用的 affinity。 |
| `after.cpus_allowed_list` | 执行后重新读取到的 affinity。 |
| `status` | `pending` / `applied` / `failed` / `rolled_back` / `rollback_failed`。 |

**解读**：此表是状态文件的字段语义字典。设计上重点保护三个字段：`process_start_time` 防 PID 复用误回滚（对应回滚流程第 3 步）、`before.cpus_allowed_list` 作为回滚输入（对应 `rollback_command` 的 `--cpu-list <original-cpu-list>`）、`after.cpus_allowed_list` 作为执行结果证据。`status` 五态完整覆盖"未执行 / 已执行 / 失败 / 已回滚 / 回滚失败"生命周期，与第 6 节边界行为（`no_target` / `pid_reused` 标记）共同支撑审计追溯。

---

## 【公式解读】

### 公式 1：内部脚本契约接口（原文: bash 代码块）

```bash
internal-bind --apply --pid <pid> --cpu-list <cpu-list> [--reason <text>]
internal-bind --rollback --pid <pid> --cpu-list <original-cpu-list> [--state <rollback-state.json>]
internal-bind --query --pid <pid>
```

符号与作用说明：
- `<pid>`：目标进程 PID，绑定操作的对象。
- `<cpu-list>`：要应用的 CPU 亲和性列表（如 "0-31"）。
- `<original-cpu-list>`：回滚用的**原始**亲和性，来自状态文件 `before.cpus_allowed_list`。
- `<text>`：可选调用原因，写入审计/日志。
- `<rollback-state.json>`：可选状态文件，便于脚本读取更多上下文。
- `--apply` / `--rollback` / `--query`：三种子命令，分别对应"应用"、"回滚"、"查询当前 affinity"。

### 公式 2：`BindingExecutor` 类层级（原文: 文本结构图）

```text
BindingExecutor
├── TasksetExecutor
└── InternalScriptExecutor
```

符号与作用说明：`BindingExecutor` 为抽象基类，封装所有执行前必须经过的前置流程（读 affinity → 校验 → 保存状态 → 展示 diff → 用户确认）。两个子类分别实现 `taskset -cp` 调用与对内部脚本 `internal-bind --apply` 的调用，对外表现一致。

### 公式 3：执行前置流程（原文: 伪代码）

```text
读取当前 affinity
  -> 校验 PID 仍存在
  -> 校验目标 CPU 在 cpuset_cpus_effective 内
  -> 保存 rollback-state.json
  -> 展示 current -> target diff
  -> 用户确认
  -> 调用执行后端
  -> 重新读取 affinity 验证结果
  -> 记录执行日志
```

符号与作用说明：箭头 `->` 代表强制顺序步骤，`cpuset_cpus_effective` 是 cgroup v1/v2 暴露的有效 CPU 集合，决定该 PID 实际可被绑定的范围。`current -> target diff` 是用户确认环节的展示内容。流程终点为日志记录——保证任何执行动作都有审计痕迹。

### 公式 4：回滚前置流程（原文: 伪代码）

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

符号与作用说明：`action.status == applied` 过滤出"真正已生效的回滚对象"；`process_start_time` 一致性是 PID 复用防护闸口；展示的是 current→original diff（即当前 affinity 偏离原始 affinity 的程度），供用户确认回滚方向。

### 公式 5：边界行为断言（原文: 条件语句）

```text
如果 PID 已退出:
    不执行回滚；标记为 no_target，并提示原进程已不存在。

如果 PID 被复用且 process_start_time 不一致:
    不执行回滚；标记为 pid_reused，并提示需要人工确认。
```

符号与作用说明：两条断言把回滚失败区分为"原对象消失"（`no_target`）和"对象错位"（`pid_reused`），避免回滚命令误作用到无关进程——对应验收标准第 2 条。

---

## 【关联】

文档处于 `skills/profiler/mindstudio-cpu-binding/` 子目录下，作为该 Skill 的**执行层设计文档**。涉及的上下游关系：

- **上游**：`snapshot.json`（进程快照，通过 `snapshot_ref` 字段被 `rollback-state.json` 引用，承载执行前的全局状态）与 `plan.json`（绑核计划，通过 `plan_ref` 字段被引用，承载目标 affinity 设计）——两者在执行前由诊断流程生成，作为状态文件的前置输入。
- **同层**：`BindingExecutor` 抽象层下挂 `TasksetExecutor`（直接 `taskset -cp <cpu-list> <pid>`）与 `InternalScriptExecutor`（调用 `internal-bind --apply/--rollback/--query`），二者共享同一套状态文件与回滚流程（验收标准第 4 条）。
- **下游 / 输出**：
  - 执行日志（流程终点）——审计追溯。
  - HTML 报告（验收标准第 5 条）——展示执行后端、当前状态、应用命令、回滚命令与实验风险，供用户查看。
  - 多 PID 报告——明确区分"已应用 / 失败 / 未执行"三类 PID（第 7 节第 4 条要求）。
- **隐含约束**：诊断规则（原文第 2 节明确要求 "Skill 不应把内部脚本逻辑硬编码到诊断规则中"）只通过适配器与后端解耦，保证执行后端可替换。
- **权限边界**：内部脚本接口最低要求第 5 条单独划出"cgroup、IRQ affinity、CPU governor、kernel 参数"等中高风险系统配置，暗示后续可能存在独立的权限边界设计文档。

文末内部链接信息为"无"。

---

## 【使用方法】

本文档为**设计规范文档**，原文未提供用户侧的启用命令、配置项或 CLI 开关。可提取的接口形态如下：

- **执行后端选择**：通过 `rollback-state.json.executor_backend` 字段区分（取值 `"taskset"` 或 `"internal-script"`），由 `BindingExecutor` 根据该字段派发到 `TasksetExecutor` 或 `InternalScriptExecutor`。
- **内部脚本调用形式**（原文给出建议接口）：
  ```bash
  internal-bind --apply --pid <pid> --cpu-list <cpu-list> [--reason <text>]
  internal-bind --rollback --pid <pid> --cpu-list <original-cpu-list> [--state <rollback-state.json>]
  internal-bind --query --pid <pid>
  ```
- **taskset 调用形式**（原文给出）：
  ```bash
  taskset -cp <cpu-list> <pid>
  ```
  示例：`taskset -cp 0-31 12345`（应用）、`taskset -cp 0-127 12345`（回滚）。
- **状态文件路径**：`rollback-state.json` 由 Skill 在执行前自动生成，与 `snapshot.json`、`plan.json` 通过 `*_ref` 字段关联。
- **回滚触发条件**：仅在 `action.status == applied` 且 PID 仍存在（且 `process_start_time` 一致，若提供）时才进入实际回滚流程。

原文未涉及配置文件（如 YAML/INI）、环境变量、CLI flag 等通用启用方式；第 8 节给出的 5 个实验计划需在 Linux 环境单独验证。
