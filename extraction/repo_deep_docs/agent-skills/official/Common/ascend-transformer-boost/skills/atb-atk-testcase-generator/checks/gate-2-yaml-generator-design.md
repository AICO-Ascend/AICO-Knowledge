# Gate 2 YAML 与 Generator 设计

> 仓 `agent-skills` · 路径 `official/Common/ascend-transformer-boost/skills/atb-atk-testcase-generator/checks/gate-2-yaml-generator-design.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/agent-skills/official/Common/ascend-transformer-boost/skills/atb-atk-testcase-generator/checks/gate-2-yaml-generator-design.md

# 一体化深度解读：Gate 2 YAML 与 Generator 设计

---

## 【定位】

本篇是 **atb-atk-testcase-generator 流水线中 Gate 2（第二道闸门）的设计规范**，定义在 Gate 1 通过后，如何为目标算子生成 ATB 测试所需的四类产物文件（`ATB_<OpName>_gen.yaml`、`generator_<op>.py`、`node.yaml`、`node_perf.yaml`），并规定这些产物之间必须满足的一致性约束与后端覆盖规则，以确保下游 ATK 调度能够正确进入 ATB 侧的精度/性能验证路径。

---

## 【技术要点】

1. **四类必需产物**：Gate 2 通过的判定标准即生成四个文件——算子级 YAML（`ATB_<OpName>_gen.yaml`）、算子级 Python 生成器（`generator_<op>.py`）、执行节点配置（`node.yaml`）、性能节点配置（`node_perf.yaml`）。
2. **一致性对齐三角**：
   - `api_type` ↔ `@register(...)` 装饰器须一致；
   - `generate` 函数 ↔ `@GENERATOR_REGISTRY.register(...)` 须一致；
   - YAML 中 `name` ↔ `Operations.cpp` 中注册名须一致；
   - 且 YAML 必须含 `in_formats` 与 `op_param` 字段。
3. **后端路由硬约束**：ATK 调度时仅 `backend: atb` 的节点进入 ATB 侧精度/性能路径；`backend: cpu` 等其它后端不覆盖 ATB 逻辑验证，故 `node.yaml` 与 `node_perf.yaml` 各自**至少须含一条** `backend: atb`。
4. **任务类型约定**：`node.yaml`（精度任务）常用 `task: ['accuracy']`；`node_perf.yaml`（设备性能）常用 `task: ['performance_device']`；两类 YAML 可与 `backend: cpu` 等节点并存（如对照路径）。
5. **覆盖度 Checklist（7 项）**：dtype 组合完整、shape 边界合理、op_param 字段完整、node 配置可执行、`node.yaml` 含至少一条 `backend: atb`、`node_perf.yaml` 含至少一条 `backend: atb`（需跑 ATB 性能时）、用户确认 Gate 2 通过。
6. **失败回流四路径**：一致性字段不匹配→修复命名重试；shape/参数覆盖不足→补约束后重试；缺 `backend: atb`→补节点再试；用户未确认→**停在 Gate 2**，待确认后再入 Gate 3。

---

## 【关键机制与数据】

**工作原理（原文视角）**：

Gate 2 处于流水线第二关，其上游产物是 Gate 1 的通过结果与三类输入来源（设计文档 / 已有 YAML / 用户参数），并叠加目标算子的 dtype/shape/op_param 约束。Gate 2 不运行算子执行，而是以**文件生成 + 一致性静态检查**为主：依次产出 4 个文件，并在产出过程中维护跨文件的命名与字段对齐。

**数据流（原文视角）**：

```
Gate 1 通过 + 设计文档/YAML/用户参数 + dtype/shape/op_param 约束
        │
        ▼
   Gate 2 文件生成
        │
        ├──> ATB_<OpName>_gen.yaml    （api_type / name / in_formats / op_param）
        ├──> generator_<op>.py        （@register + generate 函数 + @GENERATOR_REGISTRY.register）
        ├──> node.yaml                （精度任务，至少一条 backend: atb）
        └──> node_perf.yaml           （设备性能任务，至少一条 backend: atb）
        │
        ▼
  跨文件一致性 + 后端覆盖 + 7 项 Checklist
        │
        ├── 全部通过 → 进入 Gate 3
        └── 任一失败 → 按"失败回流"四分支处置
```

**性能数据**：原文无性能数据（Gate 2 本身是文件生成/检查阶段，不涉及运行时性能）。

---

## 【表格解读】

**原文无表格**。原文中出现的结构化片段均为 YAML 代码块与 Markdown checkbox 列表，已分别在【技术要点】与【使用方法】中逐字还原并解读，未发现参数表、性能对比表或配置项表格。

---

## 【公式解读】

**原文无公式**。文档不涉及任何数学公式或伪代码表达式，仅包含 YAML 最小片段示例与命令注释。

---

## 【关联】

原文未提供文末内部链接（"无"），故无法从链接锚点反推上下游模块。但依据原文出现的实体名称，可梳理出以下**逻辑上下游关系**：

- **上游 Gate 1**：Gate 2 的输入之一是"Gate 1 通过结果"，表明 Gate 1 是更前置的校验关卡（推测为算子/接口层面的预校验，但原文未给出 Gate 1 细节）。
- **下游 Gate 3**：失败回流分支明确"等待确认后再进入 Gate 3"，说明流水线上至少存在 Gate 3 阶段，原文未给出 Gate 3 的具体职责。
- **横向协同模块**：
  - `Operations.cpp`（算子 C++ 注册实现）——YAML 中 `name` 字段须与之对齐；
  - `@register(...)` 装饰器与 `@GENERATOR_REGISTRY.register(...)` 装饰器——分别约束 `api_type` 与 `generate` 函数命名；
  - **ATK 调度器**——是 `node.yaml` / `node_perf.yaml` 的实际消费方，依据 `backend` 字段决定是否进入 ATB 侧精度/性能路径；
  - **knowledge 侧约定**——原文最小片段示例注明"与 knowledge 侧约定一致"，暗示存在另一份 knowledge 文档提供 YAML 片段模板。
- **对照路径节点**：原文允许 `backend: cpu` 与 `backend: atb` 共存（如对照路径），表明 ATK 支持多后端并行调度以做交叉验证。

---

## 【使用方法】

**启用方式（原文按项目脚本或手工生成）**：

```bash
# 1) 生成 ATB_<OpName>_gen.yaml
# 2) 生成 generator_<op>.py
# 3) 生成 node.yaml / node_perf.yaml
```

**最小 YAML 片段配置项（原文逐字还原）**：

```yaml
# node.yaml（精度）
nodes:
   - backend: atb
     task: ['accuracy']
     devices: [0]
```

```yaml
# node_perf.yaml（性能）
nodes:
   - backend: atb
     task: ['performance_device']
     devices: [1]
```

**配置项逐项说明（基于原文）**：

| 配置项 | 取值/约束 | 来源 |
|---|---|---|
| `backend` | `node.yaml` 与 `node_perf.yaml` 各自**至少包含一条** `atb`，可与 `cpu` 等并存 | 原文"后端约束"段 |
| `task` | 精度任务用 `['accuracy']`；设备性能用 `['performance_device']` | 原文"常用约定"段 |
| `devices` | 示例中分别为 `[0]`（精度）与 `[1]`（性能） | 原文最小片段示例 |
| `api_type` | 与 `@register(...)` 一致 | 原文"一致性约束"段 |
| `name` | 与 `Operations.cpp` 注册名一致 | 原文"一致性约束"段 |
| `in_formats` | 必须包含 | 原文"一致性约束"段 |
| `op_param` | 必须包含且字段完整 | 原文"一致性约束"段 + Checklist |

**Checklist 启用流程（原文逐字还原）**：

- [ ] dtype 组合覆盖完整
- [ ] shape 边界合理
- [ ] op_param 字段完整
- [ ] node 配置可执行
- [ ] `node.yaml` 至少包含一条 `backend: atb`
- [ ] `node_perf.yaml` 至少包含一条 `backend: atb`（需要跑 ATB 性能时）
- [ ] 用户确认 Gate 2 通过

**说明**：原文未涉及具体的 Python/Shell 调用命令、CI/CD 钩子或项目脚本路径，仅以注释形式给出"按项目脚本或手工生成"的指导。
