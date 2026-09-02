# Test Design Checker — param_def.json 交叉验证

> 仓 `model-agent` · 路径 `skills/optimization/ascendc-whitebox-design/references/prompts/test-design-checker.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/model-agent/skills/optimization/ascendc-whitebox-design/references/prompts/test-design-checker.md

# model-agent · ascendc-whitebox-design · test-design-checker.md 一体化深度解读

---

## 【定位】

这篇文档定义了一个**独立的交叉验证员 Prompt** —— 它以"不相信分析者报告"为底层立场，从源码出发对 `param_def.json` 与 `test_design.md` 进行 11 项 Gate 检查并产出 `verification_report.json`，作为白盒算子测试设计流程中的"独立审核环节"存在。

---

## 【技术要点】

1. **角色边界**：明确定位为"独立交叉验证员"，强调"没有参与 param_def.json 的生成，需要从源码独立验证"，与上游分析者（生成者）解耦，避免利益冲突。
2. **11 项 Gate 检查全部硬性**：`任一项 fail → 整体 fail → 回 Step 2 修正`、`任一项 warn → 整体 pass_with_warnings → 可以继续但需记录`——存在 warn 时可通过但必须留痕。
3. **四项输入契约**：`param_def.json`（参数定义）、`test_design.md`（测试设计）、`path_list.json`（Agent A 的路径清单 + 源码约束表）、算子源码路径（独立验证的权威依据）。
4. **11 个检查 ID**：`thresholds_traceable`、`groups_coverage`、`dimension_values_complete`、`constraints_correct`、`numeric_ranges_match`、`platform_consistency`、`execution_mode_coverage`、`path_dimension_coverage`、`constraint_source_match`、`completeness_check`、`attribute_coverage`。
5. **6 条禁止行为（核心 反"流于表面"守则）**：禁止"看起来合理就 pass"、禁止跳过 constraints 检查、禁止只看 test_design.md 不看 param_def.json（其余三条"不要/不要/不要"陷阱类）。
6. **输出 schema 固定为三段 JSON**：`status`（`pass|fail|pass_with_warnings`）、`checks[]`（每项含 `id/status/detail`，detail 必须"包含源码行号引用"）、`issues[]`（仅 fail/warn 时填充）。

---

## 【关键机制与数据】

### 工作原理（按检查项 #1 → #11 的 Gate 流水线）

- **#1 阈值可追溯性**：对用了阈值定义（threshold）的维度，逐项到源码中比对 `value`/`type`，并校验 `source` 引用是否真实存在（非阈值类——例如枚举列表——豁免）。
- **#2 分支覆盖**：人工扫读源码的 `if/switch/策略选择`，看 `param_def.json.groups` 是否覆盖主要风险场景（不要求"一条 group 对一条代码路径"）。
- **#3 枚举完整性**：枚举值集合需 = 源码有效范围，**离散白名单是否完整**也要查。
- **#4 约束正确性**：同时校验单 group 内（`if/then`、`requires` 结构化约束）和跨 group 一致性，还要反查"被遗漏的约束应当被写出"。
- **#5 数值范围匹配**：`min/max`、`alignment`、**派生维度换算**三类要一致（特别强调"阈值作用于派生变量而非输入维度"的换算陷阱）。
- **#6 平台一致性**：四要点齐备：`platform` 字段、`platform_cores` 字段、所有维度值来自该平台、dtype 组合属于该平台 binary 注册、阈值常量是目标平台值。
- **#7 执行模式覆盖**：以 `test_design.md` 中的"执行模式分析"节为入口，校验**三种轴**的覆盖阈值——分核轴以 `platform_cores` 为 `branch_split` 阈值且覆盖 `< coreNum / = coreNum / > coreNum` 三档、UB 切分轴要足够大以触发多轮 UB loop、指令对齐轴以 BLOCK_ELEM / VL 为 alignment 阈值。`axis_role` 标注还需与源码实际分核/UB/指令逻辑吻合。
- **#8 path_dimension_coverage**：对照 `path_list.json` 的每条路径 → 取其 `group` 字段 → 取该 group 的 `params.keys` → 校验是否覆盖了路径的 `input_variables` 列表；任意 `input_variable` 缺失即 fail。该检查被点名为"独立复核"——即使 Agent D 已做，本员也要**重做一遍**。
- **#9 constraint_source_match**：对照 `path_list.json.source_constraints` 与 `param_def.json` 中的每条约束——更严 = fail、更松 = fail、完全一致 = pass。
- **#10 completeness_check**：对照 `path_list.json.completeness_checklist` 中的 `api_variants / format_variants / mode_variants / quant_variants / optional_input_combos` 五类，对每项 `status=missing` 反查 `param_def.json` 是否已处理。
- **#11 attribute_coverage**：对照参数推导阶段输出的 `attribute_diff` 列表，凡 `status=missing` 必 fail，`mapped` 或 `excluded`（有理由）才可通过。

### 数据流（无具体数字性能）

- 无任何量化性能数据（这是一份 **prompt / 流程规范**文档，不涉及运行时性能）；
- 唯一可被视作"数据载体"的是 `verification_report.json` schema 本身，它就是该 Gate 的**产物结构**。

---

## 【表格解读】

**原文无表格**。

（文档中所有结构化信息均以"列表项 + JSON 字段 + 代码块示例"形式呈现，无 `<table>`、无 markdown 表格、无 KV 矩阵。）

> 说明：`✅/❌ 判断示例`区虽成对出现，却是**代码块内的示例**，而不是可还原为 markdown 表格的结构化数据，故归类为示例而非表格。

---

## 【公式解读】

**原文无公式**。

（既无 LaTeX 行内公式，也无独立列出的伪代码公式。文档中的 `if (outDimy_ > 5120)` 出现在 `✅/❌ 判断示例`中，作为**示例代码片段**而非公式定义存在——它是阈值的示例，不是数学表达式。）

---

## 【关联】

> **内部链接：(无)** —— 原文未提供任何文末链接或交叉引用。

虽然**原文未出现内部链接**，但基于该 Prompt 在 ascendc-whitebox-design 流水线中的角色定位，可以从文档自身体系**结构性地**反推以下上下游关系：

- **上游**：
  - **分析者（生成 `param_def.json`）**：文档反复以"分析者可能遗漏分支、过度归纳、或误读源码"作为不可信任对象，其产物即为本员审核目标。
  - **Agent A（路径清单生成）**：产出 `path_list.json`（含 `group`、`input_variables`、`source_constraints` 字段、5 类 variants、completeness_checklist），是 #8 #9 #10 三项检查的输入源。
  - **参数推导阶段**：产出 `attribute_diff` 列表，是 #11 attribute_coverage 的输入源。
  - **上游文档**（基于仓库命名规则推断，但**原文未明确写出**）：`skills/optimization/ascendc-whitebox-design/references/prompts/` 目录下其他 prompt（如 `test-design-generator` 等）应为生成 `param_def.json` / `test_design.md` 的 prompt，本员是它们的"独立审核"侧。
- **下游**：
  - **Step 2 修正环节**：任一项 fail 时必须"回 Step 2 修正"——隐含此 prompt 是被**循环调用的审核环节**，修正后再回本员重审。
  - **白盒设计的引擎过滤层**：检查 #4 constraints_correct 与"禁止跳过 constraints"明示"这是引擎过滤的依据"——即本员的产物会影响后续白盒生成引擎对合法参数组合的筛选。
- **同目录/同流程兄弟节点**（基于仓库结构命名推断，**原文未明确点名**）：其它 `prompts/` 子文件（如生成器类 prompt）是其协同对象。

**重要边界**：以上关联关系除"上游分析者 / `path_list.json` / 参数推导阶段 / Step 2 修正 / 引擎过滤层"5 项确凿见于原文外，其余属位置命名推断，已标注「推断」。

---

## 【使用方法】

### 启用方式

- 作为 `prompt` 模板加载：路径 `skills/optimization/ascendc-whitebox-design/references/prompts/test-design-checker.md`
- **触发时机**：上游分析者完成 `param_def.json` 与 `test_design.md` 后调用——文档明示 `任一项 fail → 整体 fail → 回 Step 2 修正`，说明启用点是 **Step 1（生成）之后、Step 2（落地）之前** 的审核节点。

### 必备输入（4 份）

1. `param_def.json` —— 待验证的参数定义
2. `test_design.md` —— 待验证的测试设计文档
3. `path_list.json` —— Agent A 的路径清单 + 源码约束表
4. **算子源码路径** —— 用于独立验证（这是权威依据）

### 配置项 / 命令

- **原文未涉及**任何配置项、CLI 命令、运行时开关、环境变量。

### 输出契约

- 产物路径：**`verification_report.json`**
- 三段 schema：
  - `status` ∈ `{pass, fail, pass_with_warnings}`
  - `checks[]`：每项 `id` / `status ∈ {pass, fail, warn}` / `detail`（**detail 必须含源码行号引用**）
  - `issues[]`：仅在 fail/warn 时填充

### 6 条操作守则（红线）

- 禁止"看起来合理就 pass" —— 每一项都需要源码证据
- 禁止跳过 constraints 检查 —— 它是引擎过滤的依据
- 禁止只看 `test_design.md` 不看 `param_def.json` —— 两个都要验证
- 禁止因为 `test_design.md` 写得详细就默认它是对的
- 禁止因为 `param_def.json` 格式正确就跳过内容检查
- 禁止因为阈值标注了 source 就不去验证那个 source

### 11 项 Gate ID 速查

`thresholds_traceable` · `groups_coverage` · `dimension_values_complete` · `constraints_correct` · `numeric_ranges_match` · `platform_consistency` · `execution_mode_coverage` · `path_dimension_coverage` · `constraint_source_match` · `completeness_check` · `attribute_coverage`
