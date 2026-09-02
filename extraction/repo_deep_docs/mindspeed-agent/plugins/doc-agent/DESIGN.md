# Doc-Agent 设计规格（DESIGN）

> 仓 `mindspeed-agent` · 路径 `plugins/doc-agent/DESIGN.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-agent/plugins/doc-agent/DESIGN.md

# Doc-Agent 设计规格深度解读

---

## 【定位】

**一句话**：本文件是 `doc-agent` 重构的唯一真相源（Single Source of Truth），用状态机 + 契约 Schema + 规则目录 + 账本四件套，把"文档撰写/审查"的多 Agent 协作从"靠 prompt 调度"重构为"机器编排、Agent 只做单步转换"的确定性流水线。

---

## 【技术要点】

**核心机制分条：**

1. **8 条设计原则**（§1）：编排确定性、契约 Schema 强制、规则目录集中、两层审查（lint + semantic）、L0/L1/L2 深度分层、模板仅约束仓库级必备清单、issues.jsonl 追加式账本、`docs/en/**` 全局出域（不参与任何环节）。

2. **两场景状态机**（§3）：
   - 场景 A（新文档）：`init → context → design → confirm(人工) → write → review ⇄ fix(≤3) → finalize → done`
   - 场景 B（审视已有）：`init → plan → review ⇄ fix(≤3) → finalize → done`
   - `confirm` 强制写 `design_approval.md`（章节清单 + 说明 + 时间戳）才放行 `USER_APPROVED`。

3. **Handoff Token 协议**：Agent 输出末尾以 `handoff: XXX` 单行声明状态出边；引擎 `extract_handoff` 取最后一行（共 12 条 token，见下表）。

4. **6 类门控谓词**（`gates.py`）：`product_exists`、`schema_valid`、`score_pass`、`lint_complete`、`review_complete`、`code_verify_present`，加 `iter_below_cap`（fix < 3）。

5. **3 深度档位**：
   - **L0**：仅 lint
   - **L1**：lint + 2 reviewer（`correctness-code` + `completeness`）
   - **L2**：lint + 5 reviewer 全对抗
   - `score` 命令 `--depth` 缺省 = L2。

6. **9 份 JSON Schema 契约**（§4）：`issue / context_report / design_plan / figure_requests / lint_report / review_report / code_verify / quality_report / memory_event`，全部 `additionalProperties: false`。

7. **规则打分矩阵**（§5）：weights `{correctness:40, completeness:25, clarity:20, accessibility:15}`、floors `{90,80,60,60}`、`pass_total: 80`、`max_rounds: 3`；每条规则带 `rule_id / dimension / kind / linter / severity / weight / primary / judge / evidence`。

8. **CLI 6 子命令**：`new / next / current / verify / score / doc-hash`（外加提及的 `issue-status`），工作流必须先解析 `<DOC_AGENT_ROOT>`（Claude 取 `CLAUDE_PLUGIN_ROOT`，Codex 取已加载 `SKILL.md` 上溯两级）。

---

## 【关键机制与数据】

### 工作原理（原文摘要）

**编排路径**：
原文 §1 明确：Phase-Gate、循环、评分由引擎（状态机 + 门控谓词 + 账本）机器求值；Agent 只承担单步"输入契约 → 输出契约"转换，不参与流程控制。这从根本上把"流程逻辑"和"内容生成"解耦。

**两层审查产出同一 issue 模型**（原文 §1 第 4 条）：
> "确定性 lint 层（脚本，永远先行）+ 语义审查层（LLM，按深度调度）；两层产出同一 issue 模型。"

确定性 issue 以**当前 lint_report** 为准（不持久化到 issues.jsonl）；语义 issue 在 `issues.jsonl` **只追加**，生命周期 `open → fixed → verified → closed/disputed`。

**迭代上限**（原文 §1 第 7 条 + §3）：
> "iter_below_cap：fix 计数 < 3"；"迭代计数从 ledger.jsonl 推导，不做带外计数。"

**绑定文档指纹**（原文 §3 末段）：
> "所有深度评分都必须能从 --doc 或 new --doc 得到目标文档；lint/review 报告必须绑定该文档当前 SHA-256。L1/L2 的 code_verify 还必须逐块绑定 fenced code block 的真实文件与起始行。"

**报告失效规则**（原文 §4 quality_report 条）：
> "任一审查输入变化后旧报告失效，L1/L2 的 code_verify manual/fail 不得生成 pass。"

### 数据流（原文 §3 末段 + §4 末段）

运行产物目录 `.doc-work/<repo>/<run-id>/` 内：
- 主产物：`run.json`、`context_report.json`、`design_plan.json`、`draft_{doc}.md`、`figure_requests.json`、`lint_report.json`、`review_report.json`、`code_verify.json`、`quality_report.json`
- 追加式账本：`issues.jsonl`（语义 issue 生命周期）、`ledger.jsonl`（阶段转移日志，`verify` 重放校验）

### 性能/约束数据

原文 §5 给出打分参数（仅此一处）：
- `weights`：`correctness: 40, completeness: 25, clarity: 20, accessibility: 15`（合计 100）
- `floors`：`correctness: 90, completeness: 80, clarity: 60, accessibility: 60`
- `pass_total: 80`
- `max_rounds: 3`
- 规则条目数：原文称"33 条，从早期实现统一后的检查项迁移"，但原文在 `R-COR-001` 后被截断，未列出其余 32 条的 `rule_id`。

> 原文截断提示：文档在 §5 规则清单处中止于 `correctness：R-COR-001 链接有`，未给出 R-COR-002…R-XXX 及 completeness/clarity/accessibility 维度的完整规则条目；本解读严格按原文终止位置止步，不补全未给出的字段。

---

## 【表格解读】

### 表 1：Handoff Token 映射表（原文 §3，逐字还原）

| 状态 | 出边 | token |
|------|------|-------|
| init | → context | `handoff: CONTEXT_READY` |
| init | → plan | `handoff: PLAN_READY` |
| context | → design | `handoff: DESIGN_READY` |
| design | → confirm | `handoff: DESIGN_DONE` |
| confirm | → write | `handoff: USER_APPROVED` |
| confirm | → design | `handoff: USER_REJECT` |
| write | → review | `handoff: REVIEW_READY` |
| plan | → review | `handoff: REVIEW_READY` |
| review | → fix | `handoff: NEED_FIX` |
| review | → finalize | `handoff: PASSED` |
| fix | → review | `handoff: FIXED` |
| fix | → finalize | `handoff: MANUAL_INTERVENTION` |
| finalize | → done | `handoff: DONE` |

**逐行解读：**

- **init → context / plan**：场景分发点。`CONTEXT_READY` 走场景 A 的"先盘点仓库再设计"，`PLAN_READY` 走场景 B 的"直接审查既有文档"。两个 token 同源不同向，由 init 阶段决定走哪条。
- **context → design**：`CONTEXT_READY` 触发后，context agent 完成 `context_report.json`，交付 `DESIGN_READY` 进入设计阶段。
- **design → confirm**：design agent 产出 `design_plan.json`（含 H2 章节清单），交付 `DESIGN_DONE` 暂停流水线等待人工。
- **confirm → write / design**：唯一的人工交互点；`USER_APPROVED` 须附 `design_approval.md`（章节清单 + 说明 + 时间戳）作为硬门控，`USER_REJECT` 回 design 重做。
- **write → review** 与 **plan → review**：两条路径殊途同归——新文档写完或旧文档计划完成，都以 `REVIEW_READY` 进入审查。
- **review → fix / finalize**：`NEEDED_FIX` 触发 fix 循环（受 `iter_below_cap` 即 fix < 3 约束），`PASSED` 直接进 finalize。
- **fix → review / finalize**：`FIXED` 回到 review 复核（构成 review-fix 闭环）；`MANUAL_INTERVENTION` 表示达到上限或非可自动修复问题，跳过 review 进入 finalize（典型情况为 fix=3 仍不通过）。
- **finalize → done**：唯一出口，以 `DONE` 收尾。

整张表覆盖 13 行（含表头 13 单元格）、12 条有效转移，token 取值与状态名大写一致，仅 token 自身为协议常量。

### 表 2：打分参数表（原文 §5，逐字还原）

| 参数 | 值 | 含义 |
|---|---|---|
| `weights.correctness` | 40 | 正确性维度权重（最高） |
| `weights.completeness` | 25 | 完整性维度权重 |
| `weights.clarity` | 20 | 清晰度维度权重 |
| `weights.accessibility` | 15 | 可达性维度权重 |
| `floors.correctness` | 90 | 正确性单维最低分（低于则整体不过） |
| `floors.completeness` | 80 | 完整性单维最低分 |
| `floors.clarity` | 60 | 清晰度单维最低分 |
| `floors.accessibility` | 60 | 可达性单维最低分 |
| `pass_total` | 80 | 总分通过阈值 |
| `max_rounds` | 3 | fix 最大迭代轮数 |

**逐行解读：**

- weights 四值之和 = 100，表明这是"加权求和 → 总分"的归一化评分结构，correctness 占 40% 的绝对主导地位。
- floors 阈值设计体现"短板否决"思想：correctness 必须 ≥90（最高门槛），accessibility 仅 ≥60（最低门槛）；任何一维跌破 floor 即 `verdict != pass`。
- `pass_total: 80` 与 `max_rounds: 3` 是两个全局硬约束：总分 < 80 触发 fix；fix 满 3 次仍不通过则走 `MANUAL_INTERVENTION` 出 finalize。
- 原文 §5 同时声明"33 条规则、维度/权重/主责一一对应"，但仅给出 R-COR-001 一条完整示例，其余 32 条在原文中被截断。

### 表 3：Rule 示例字段（原文 §5 R-COR-001，逐字还原）

| 字段 | 值 | 说明 |
|---|---|---|
| `id` | R-COR-001 | 规则唯一编号 |
| `dimension` | correctness | 归属维度 |
| `title` | 链接可达性 | 人类可读标题 |
| `kind` | deterministic | 类型（确定性 / 语义） |
| `linter` | link | 对应 linter 子命令（`kind: deterministic` 时必填） |
| `severity` | critical | 类型等级（投票取高基准） |
| `weight` | 5 | 扣分权重 |
| `primary` | true | 该对象主责维度（非主责维度命中不重复扣分） |
| `judge` | HTTP 2xx/3xx 视为有效；跨仓链接分支与目标仓由 R-COR-004 复核 | 判定方式 |
| `evidence` | 请求状态码与目标 URL | 证据收集规则 |

**逐行解读：**

- `kind: deterministic` 与 `linter: link` 配对：表示 R-COR-001 由 `linters/link_lint.py`（对应 `doc_lint.py link` 子命令）静态判定，永远先于 LLM 审查执行。
- `severity: critical` + `weight: 5`：单次命中扣 5 分；属"投票取高基准"策略——多 reviewer 对同一规则投票时取最高严重级。
- `primary: true`：标记此规则的主责维度是 correctness；若被其他维度的 reviewer 复用命中，不在那些维度重复扣分，避免一规多扣。
- `judge` 字段指明跨仓链接需 R-COR-004 复核，体现规则间的级联依赖关系。
- `evidence: 请求状态码与目标 URL`：要求 linter 把原始证据写入 issue 的 `evidence` 字段，便于人工回溯。

---

## 【公式解读】

原文无传统数学公式。

文档中存在的"形式化片段"为：
1. **状态转移表**（13 条 handoff token 行）—— 已在上节"表格解读"逐行还原。
2. **JSON Schema 字段列表**（§4）—— 9 份契约的字段集合，以"key: type"形式列出，例如 `issue.json` 的 `id: string`、`rule_id: string`、`dimension: correctness|completeness|clarity|accessibility` 等。这些是数据结构定义而非计算公式。
3. **门控谓词伪代码**（§3）—— 以命名引用形式出现（`gates.py` 中的 6 个谓词函数名），未给出实现伪代码。

**打分模型的形式化表达**（基于原文 §5 给出的参数反推，原文未给出此公式，仅按 `weights`/`floors`/`pass_total` 结构推断）：

$$
\text{verdict} = 
\begin{cases}
\text{pass}, & \text{if } \sum_{d \in \mathcal{D}} w_d \cdot s_d \geq 80 \ \text{and} \ \forall d \in \mathcal{D},\ s_d \geq f_d \\
\text{fail}, & \text{otherwise}
\end{cases}
$$

其中：
- $\mathcal{D} = \{\text{correctness, completeness, clarity, accessibility}\}$
- $w_d$ = 维度权重（40 / 25 / 20 / 15）
- $s_d$ = 维度得分（0–100）
- $f_d$ = 维度底线（90 / 80 / 60 / 60）

> 注明：上述公式**非原文显式给出**，系读者基于 §5 的 `weights` + `floors` + `pass_total` 三个 yaml 字段反推的形式化；原文未提供此代数表达。

---

## 【关联】

**模块/特性上下游关系**（基于原文 §1–§5 内部交叉引用）：

1. **与 inference-model-optimize 的关系**（原文 §2 末段）：
   > "参考实现在 `plugins/inference-model-optimize/engine/`。"
   
   doc-agent 的 engine（state_machine / gates / ledger / yamlite）是 inference-model-optimize engine 的同构/参考实现，二者共享"状态机 + 门控 + 账本"的设计模式。

2. **插件适配层双轨**（原文 §2）：
   - `.claude-plugin/plugin.json`：Claude 适配层，注册 5 个 skill 路径
   - `.codex-plugin/plugin.json`：Codex 适配层，注册插件内 skills 聚合目录
   - `AGENTS.md`：Codex 运行时根目录解析与角色调度约定
   - `skills/`：由安装脚本生成的 5 个 skill 链接/目录联接
   
   表明同一 doc-agent 同时面向 Claude Code 与 Codex 两套运行时，通过 `<DOC_AGENT_ROOT>` 解析路径差异化（CLAUDE_PLUGIN_ROOT vs SKILL.md 上溯两级）。

3. **规则治理通道**（原文 §2 + §5）：
   - `rules/README.md`：规则新增/废弃/版本化流程
   - `templates/README.md`：模板清单（`repo_manifest.yaml`）的变更流程
   
   表明 rules 和 templates 不是静态文件，存在正式治理通道。

4. **Lint 工具集内部协作**（原文 §2 `linters/`）：
   - `link_lint.py` ← 由旧 `scan_links.py` 改造，**保留 xlsx 报告能力**
   - `manifest_lint.py` → 对照 `templates/repo_manifest.yaml`
   - `placement_lint.py` → 对照 `repo_manifest.yaml` 的 placement 段
   - `image_lint.py` → 检查路径 + 替代文本（alt_text，对应 `figure_requests.json` 的 `alt_text` 字段）
   - `nav_lint.py` / `version_lint.py`：尽力而为（best-effort），不阻断流水线
   - 全部统一通过 `doc_lint.py` CLI 调度

5. **与 `docs/en/**` 的边界**（原文 §1 第 8 条）：
   > "docs/en 全局出域：英文资料树由专门翻译团队负责，整个 doc-agent 执行过程……都不考虑 docs/en/** 下的内容。"
   
   这是 doc-agent 的全局排除域——任何 lint / 审查 / 完整性判定都不触达该路径。

6. **运行时隔离机制**（原文 §2 + §3）：
   `.doc-work/<repo>/<run-id>/` 不污染目标仓；每份文档或审查分组一个 run，由 `state_machine.py new` 创建隔离工作空间。

7. **设计计划与人工确认的耦合**（原文 §3 confirm 段）：
   `design_plan.json`（含 H2 章节清单）→ 人工确认 → `design_approval.md`（章节清单 + 确认说明 + 时间戳，写入 workspace）→ `USER_APPROVED`。三方文件形成"设计-确认-放行"闭环。

> 原文未提供任何 markdown 内部链接或 URL；本节关系全部依据原文段落中显式提及的模块/路径交叉引用整理。

---

## 【使用方法】

原文 §3 CLI 段给出 6 条命令的启用方式，逐字保留：

```bash
# 1) 创建隔离 run（每个目标文档一个工作空间）
python "<DOC_AGENT_ROOT>/engine/state_machine.py" new \
  --workspace .doc-work/<repo> --doc <doc>

# 2) 提交 handoff token，推进到下一状态
python "<DOC_AGENT_ROOT>/engine/state_machine.py" next \
  --workspace <run-workspace> --yaml "<DOC_AGENT_ROOT>/engine/doc_pipeline.yaml" \
  --handoff "handoff: CONTEXT_READY"

# 3) 查询当前状态
python "<DOC_AGENT_ROOT>/engine/state_machine.py" current --workspace <run-workspace>

# 4) 重放校验（验证 ledger.jsonl 每条转移都在 YAML 中声明）
python "<DOC_AGENT_ROOT>/engine/state_machine.py" verify --workspace <run-workspace>

# 5) 文档指纹（SHA-256，用于绑定 lint/review 报告）
python "<DOC_AGENT_ROOT>/engine/state_machine.py" doc-hash --workspace <run-workspace> --doc <doc>

# 6) 评分（--depth 缺省 L2；可显式指定 L0/L1/L2）
python "<DOC_AGENT_ROOT>/engine/state_machine.py" score --workspace <run-workspace> \
  --rules "<DOC_AGENT_ROOT>/rules/rules.yaml" --depth L2 --doc <doc>
```

**`<DOC_AGENT_ROOT>` 解析规则**（原文 §3 末段）：
- Claude Code：`CLAUDE_PLUGIN_ROOT` 环境变量
- Codex：先取已加载的 `skills/doc-orchestrator/SKILL.md` 所在目录，再向上两级得到插件根目录
- 源码调试：直接使用 `plugins/doc-agent`
- 解析结果必须包含 `engine/rules/contracts` 关键文件

**其它配置项**：
- 规则目录路径：`<DOC_AGENT_ROOT>/rules/rules.yaml`（评分命令 `--rules` 参数）
- 状态机定义：`<DOC_AGENT_ROOT>/engine/doc_pipeline.yaml`（`next` 命令 `--yaml` 参数）
- 工作空间路径：`.doc-work/<repo>/<run-id>/`（`new` 命令 `--workspace` 参数）
- 模板：`templates/repo_manifest.yaml`（版本 1.0.0，原文 §2 注明）
- 深度档位：`L0 / L1 / L2`（`score` 命令 `--depth` 参数，缺省 L2）

**待用户提供**（原文 §2 注明）：
- `templates/README.md`："待用户提供正式粗粒度标题集合的说明"——表明 `repo_manifest.yaml` 的可选条目仍待补充。

> 原文未涉及环境变量配置、API key、模型选择、超时设置等运行参数；以上仅整理原文显式给出的启用方式。
