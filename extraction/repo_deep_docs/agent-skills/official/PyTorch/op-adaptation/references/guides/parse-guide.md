# Parse Guide (C-parse)

> 仓 `agent-skills` · 路径 `official/PyTorch/op-adaptation/references/guides/parse-guide.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/agent-skills/official/PyTorch/op-adaptation/references/guides/parse-guide.md

# Parse Guide (C-parse) 深度解读

## 【定位】

本指南规范了 op-adaptation 流水线中 **C-parse（Parse 步骤）** 的执行流程——即从 `.md`（aclnn API 文档）与 `_def.cpp`（算子定义）两份输入文件中提取参数、判断算子类型、解决多源冲突、完成参数完整性自检，并落地为统一的 `CHECKLIST.md`，为下游 C-yaml、C-confirm 步骤提供"参数信息的单一事实源"。

---

## 【技术要点】

1. **双源解析输入**
   - 来自 `.md` 文件：aclnn 函数签名（`GetWorkspaceSize` 参数）、参数类型、input/output 标记、dtype/shape 约束。
   - 来自 `_def.cpp` 文件：`AttrType(REQUIRED/OPTIONAL)` 标记（决定 YAML 中参数位置）、`Attr(default_value)` 默认值、`.Version(V2/V3/...)` 版本变体指示器、SymInt 类型。

2. **既存绑定检索**
   - 使用 `grep` 在 `op_plugin/config/derivatives.yaml` 中检索前向算子名，判断是否已存在绑定；若存在则记录其公式以备参考（添加变体时可能需要更新）。

3. **算子类型自动检测**（基于名称模式匹配）
   - `npu_xxx_grad` / `aclnnXxxGrad` → Backward（梯度）→ C-yaml 注册该算子；**C-derivatives 不触发**；用户可能需要更新前向算子的 derivatives 绑定。
   - `npu_xxx`（无 `_grad` 后缀）→ Forward → C-yaml 注册；若 autograd，C-yaml 同时注册 backward，C-derivatives 添加绑定。

4. **参数来源优先级（4 级）**——从高到低：
   1. C-confirm 中用户明确指令（最高）
   2. `_def.cpp` 定义的参数（权威算子定义）
   3. `.md` 描述的参数（aclnn API 文档）
   4. 参考实现参数（**绝不自动包含**）

5. **冲突解决规则**
   - `_def.cpp` 有而 `.md` 无 → 保留，标 ⚠️ 并在 C-confirm 向用户确认。
   - `.md` 有而 `_def.cpp` 无 → 排除（`_def.cpp` 是权威）。
   - 两者都有 → 以 `_def.cpp` 的类型/可选性为权威。

6. **参数完整性自检（5 项检查）**
   1. 输入参数完整性（遍历 `this->Input("xxx")` 调用）；
   2. 禁用参数检测（"not enabled" 注释）；
   3. 默认值冲突解决（`_def.cpp` 优先；冲突记录为 ⚠️ "Awaiting user confirmation"，**禁止单方面决策**，在 C-confirm 中解决）；
   4. 约束逻辑提取（dtype/shape 推导规则、互斥/共存规则、场景分支）；
   5. 版本深度分析（`.Version(V2/V3/...)` 标记下的属性清单、Output DataType 数组的版本相关变体，例如 V1=DT_INT8 / V2=DT_INT4，生成 V2 vs V1 差异摘要）。

---

## 【关键机制与数据】

**工作原理 / 数据流：**

C-parse 处于 op-adaptation 流水线的入口环节，其执行链路如下：

1. **输入采集**：同时读取 `.md`（aclnn API 文档）与 `_def.cpp`（算子 C++ 定义）两份源文件。
2. **既存绑定扫描**：通过 `grep` 在 `op_plugin/config/derivatives.yaml` 中查询前向算子名是否已有绑定（命中后记录现有公式作为参考）。
3. **算子类型判定**：依据算子命名模式（`_grad` 后缀 / `Grad` 前缀）区分 Forward / Backward，决定下游是 C-yaml 还是 C-derivatives 触发。
4. **参数提取与冲突解决**：按 4 级优先级合并双源参数；遇到冲突按 3 条解决规则处理，并将未决项登记到 `CHECKLIST.md` 的 Conflict Confirmation 表，标注 ⚠️ "Awaiting user confirmation"。
5. **5 项自检**：覆盖输入完整性、禁用参数、默认值冲突、约束逻辑、版本深度——均把结果写入 `CHECKLIST.md`。
6. **校验报告输出**：按 Validation Report Template（原文 block 形式）输出参数处理状态（✅ Processed / ⚠️ Defined but missing / ⚠️ Default conflict 等）。
7. **产出物**：以 `references/templates/checklist-template.md` 为模板生成 `CHECKLIST.md`，其中"参数信息表"是跨步骤、跨子技能共享的 **单一事实源（single source of truth）**。

> 原文示例校验数据：`per_token_scale` 出现 ⚠️ "Defined in _def.cpp but not in YAML"；`group_type` 默认值冲突为 "-1 vs 0"。

**Scope Control 边界规则**（原文硬约束）：
- 仅实现输入文件显式包含的或用户确认的内容。
- **DO NOT add**：未在输入文件中出现的额外参数、未要求的函数变体、参考实现中的特性（即使参考实现中有，例如 `quant_mode`）。
- 当 `_def.cpp` 与 `.md` 冲突时，在 C-confirm 中向用户询问。

---

## 【表格解读】

### 表 1：算子类型自动检测模式表（原文逐字还原）

| Pattern | Type | Implication |
|---------|------|-------------|
| `npu_xxx_grad` / `aclnnXxxGrad` | Backward (gradient) | C-yaml registers this op; C-derivatives does NOT fire; user may need to update the forward op's derivatives binding |
| `npu_xxx` (no `_grad` suffix) | Forward | C-yaml registers this op; if autograd, C-yaml also registers the backward op, and C-derivatives adds the binding |

**逐行解读：**

- **第 1 行**：匹配 `npu_xxx_grad` 或 `aclnnXxxGrad` 命名的算子被识别为 **Backward（梯度算子）**。其下游影响是：C-yaml 负责注册该算子本身；**C-derivatives 不会触发**（因为它通常作用于前向算子的派生绑定注册）；若需要让该 backward 与对应 forward 的 derivatives 绑定协同，用户需主动更新前向算子的 derivatives 绑定——这是一个潜在的"用户需手动介入"的提示点。

- **第 2 行**：不携带 `_grad` 后缀的 `npu_xxx` 被识别为 **Forward 算子**。C-yaml 注册该前向算子；若该算子支持 autograd，C-yaml 会**同时**注册其 backward 算子，并由 C-derivatives 添加派生绑定。即 Forward 路径会同时驱动 backward 注册与 derivatives 绑定两条下游链路，而 Backward 路径只驱动 C-yaml 单条链路。

---

## 【公式解读】

原文无公式。

---

## 【关联】

文档内提到的上下游模块 / 引用关系：

- **`yaml-configuration-guide.md`**：被引用以解释 `AttrType(REQUIRED/OPTIONAL)` 标记如何决定 YAML 参数位置，属下游配置规范。
- **`references/templates/checklist-template.md`**：C-parse 步骤生成 `CHECKLIST.md` 所使用的模板文件；其中的"参数信息表"被明确为跨所有步骤与子技能共享的 **single source of truth**。
- **`op_plugin/config/derivatives.yaml`**：通过 `grep` 检索的既存绑定文件，决定是否需要复用 / 更新既有公式。
- **下游流水线节点**：
  - **C-yaml**：无论 Forward 还是 Backward 都触发，用于注册算子到 YAML。
  - **C-derivatives**：仅 Forward + autograd 路径触发，添加 derivatives 绑定。
  - **C-confirm**：所有 ⚠️ 未决项（冲突默认值、`_def.cpp` 独有的参数、版本差异摘要）都在此处由用户最终裁决；C-parse **禁止单方面决策**。
- **上游输入**：`.md`（aclnn 文档） + `_def.cpp`（算子 C++ 定义）。

---

## 【使用方法】

**启用方式 / 命令（原文有则摘录）：**

- 检索既存绑定：在 `op_plugin/config/derivatives.yaml` 中使用 `grep` 检索前向算子名。
- 解析完成后，使用 `references/templates/checklist-template.md` 模板生成 `CHECKLIST.md`。
- 解析结果与校验报告需登记到 `CHECKLIST.md` 的：Parse Results、Parameter Information Table（单一事实源）、Constraint Logic、Conflict Confirmation 表。
- 版本深度分析触发条件：`_def.cpp` 中检测到 `.Version(V2/V3/...)` 标记时执行；需列出全部带 `.Version()` 的属性（name/type/default），并分析 Output DataType 数组的版本变体（如 `DT_INT8 for V1, DT_INT4 for V2`）。
- 关键纪律：`_def.cpp` 与 `.md` 冲突时 → 不自行决定 → 写入 `CHECKLIST.md` 标记 ⚠️ → 在 C-confirm 中向用户确认。
