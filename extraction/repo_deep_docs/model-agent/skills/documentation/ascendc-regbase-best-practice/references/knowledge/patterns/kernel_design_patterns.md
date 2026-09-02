# Kernel Design Patterns

> 仓 `model-agent` · 路径 `skills/documentation/ascendc-regbase-best-practice/references/knowledge/patterns/kernel_design_patterns.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/model-agent/skills/documentation/ascendc-regbase-best-practice/references/knowledge/patterns/kernel_design_patterns.md

# Kernel Design Patterns 深度解读

---

## 【定位】

这篇文档是 Regbase-first Kernel 工程的**工作流模式手册**, 解决从设计意图到代码实现、再到审查与修复全过程中如何保持"分支决策、API 选择、骨架顺序、审查依据、修复边界"五者一致性的工程纪律问题, 确保 Regbase 路线不在中途悄悄回退到默认模板/Membase 假设。

---

## 【技术要点】

文档共归纳 **6 条工程模式**, 核心要点如下:

1. **Pattern 1 — Branch Packet Before Code(分支包先于代码)**
   - 设计包在编码前必须显式声明 6 类信息:
     - target platform and branch
     - mathematical route
     - shape abstraction and tiling route
     - reference-operator status: inspected reference vs greenfield
     - precision-sensitive stages
     - expected API families
   - 任一项缺失, 后续阶段都会"漂回"默认模板假设。

2. **Pattern 2 — Skeleton Before Logic(骨架先于逻辑)**
   - 实施顺序固定为 5 步:
     1. 从已 routing 的工程骨架出发, **先锁分支包**
     2. 让空工程可编译通过
     3. 加入 host tiling contract
     4. 加入 kernel compute path
     5. 加入 verification 与 edge-case checks
   - 目的: 把结构性错误与数学错误分离, 缩小修复闭环范围。

3. **Pattern 3 — API Semantic Verification Before Commitment(API 语义校验先于定型)**
   - 一个候选 API **直到通过以下 4 项才被视为"被选定"**:
     - API family 与 branch 和 dataflow 匹配
     - 名称出现在 regbase-facing API material 中
     - 语义与 alignment / repeat / synchronization 需求匹配
     - 设计未把 membase primitive 冒充为 regbase
   - 约束查询入口: `../api/index.md`(原文表述)

4. **Pattern 4 — Walkthrough Uses Pattern Evidence(串讲以模式证据为据)**
   - 串讲审查关注 5 个维度:
     - review the shape abstraction
     - challenge the branch route
     - verify reduction or broadcast selection
     - question precision boundaries
     - question reuse claims
   - 评论质量标准: 必须**指出具体模式不匹配点**(wrong branch / wrong split axis / unsupported reuse claim / precision-sensitive state dropped too early), 不接受"感觉不对"。

5. **Pattern 5 — Repair Preserves Branch Context(修复保留分支上下文)**
   - 审查失败时纪律:
     - 不随意切换 execution families
     - 在当前 regbase route 内修复, 除非 branch assumption 本身被证伪
     - 重写 compute code 前先复查 API whitelist 与 pattern choice
     - fusion 任务要区分"keep reused"与"rewrite for regbase"

6. **Pattern 6 — Minimal but Complete Test Boundaries(最小但完整的测试边界)**
   - 必须覆盖的 6 类边界:
     - compile viability
     - tail block and tail tile behavior
     - non-aligned copy boundaries
     - precision-sensitive shapes
     - branch-specific edge cases(例: split-load reduction, broadcast degenerating to scalar)
   - 定性: 这些是 **pattern tests**, 而非 example tests, 用来证明 route 而不只是证明样例输入。

---

## 【关键机制与数据】

> **原文无具体性能数据或数值参数。**

本文档是**工程流程/工作流类型**的知识卡(`topic_type: pattern`, `type: knowledge_card`, `depth: foundation`), 其机制是流程性而非数值性的:

- **数据流含义**: 不是描述数据在硬件中的搬运, 而是描述**信息(branch packet、API 决策、模式证据)**在设计 → 实现 → 串讲 → 修复各阶段之间的传递与约束关系。
- **核心机制 — "防止漂回默认模板"**:
  - Pattern 1 通过**前置声明**锁住分支;
  - Pattern 2 通过**编译可过 → 骨架 → 计算 → 验证**的顺序, 把错误分层;
  - Pattern 3 通过**4 项 API 校验**避免 membase 冒充 regbase;
  - Pattern 4 通过**模式证据型评审**让问题具体化;
  - Pattern 5 通过**修复范围限定**避免隐性重新设计;
  - Pattern 6 通过**模式级测试**验证 route 而非仅样例。
- **`verified: false`**(原文元数据): 文档本身尚未经过验证流程。
- **不适用范畴(原文 not_for)**: 不回答"确切 API 白名单问题"、不涉及"低层 VF 数学选型"。

---

## 【表格解读】

**原文无表格。**

全文以 6 条 Pattern + Related Documents 列表形式组织, 没有出现参数表/性能对比表/配置表。

---

## 【公式解读】

**原文无公式。**

文档为模式/流程类知识卡, 未出现任何 LaTeX 公式或伪代码表达式。

---

## 【关联】

文档处于 Regbase-first 工程的**流程治理层**, 与下游/平行模块的关系如下(基于文末 Related Documents + 元数据 next_reads):

| 关联类型 | 关联文档 | 关系性质 |
|---|---|---|
| **next_reads(优先后续阅读)** | `../regbase_development_guide.md` | Regbase 开发总指南, 本文档是其工作流子集 |
| **next_reads** | `../dev-experience/regbase_kernel_case_notes.md` | 案例笔记, 提供 Pattern 应用实例 |
| **next_reads** | `../pitfalls/common_traps.md` | 常见陷阱, 与 Pattern 4/5 审查与修复直接相关 |
| **Related(平行 Pattern 体系)** | `regbase_operator_patterns` | 算子级模式, 本文档提供流程外壳 |
| **Related** | `tiling_patterns` | 切分模式, 对应 Pattern 1 中的 "tiling route" |
| **Related** | `reduction_patterns` | 规约模式, 对应 Pattern 4 中 "verify reduction selection" |
| **Related** | `broadcast_patterns` | 广播模式, 对应 Pattern 4 中 "verify broadcast selection" |
| **Related** | `../api/index` | API 索引, 是 Pattern 3 语义校验的查询入口 |
| **Related(用户指定链接)** | [`../pitfalls/precision_guide.md`](../pitfalls/precision_guide.md) | 精度指南, 与 Pattern 1 中 "precision-sensitive stages"、Pattern 6 中 "precision-sensitive shapes" 直接对接 |
| **Related** | `../../reference-ops/open_source_operator_table` | 开源算子表, 提供 reference-operator status 的来源 |

**关系图谱(逻辑)**:
- 本文档是 **"流程骨架"**, `regbase_operator_patterns / tiling / reduction / broadcast` 是 **"内容填充"**;
- `../api/index.md` 是 Pattern 3 的**外部约束源**;
- `precision_guide.md` 与 `common_traps.md` 是 Pattern 4/5/6 的**反面参照**(precision + 陷阱);
- `regbase_development_guide.md` 与 `regbase_kernel_case_notes.md` 是**上层入口与案例层**。

---

## 【使用方法】

**原文未涉及**具体启用命令、配置项或 API 调用形式。

本文档的使用方式是**阅读 + 流程遵循**, 而非工具调用:

- **触发条件(原文 `read_when`)**:
  - 任务处于**从设计转入实现或评审**阶段时;
  - 需要把 **branch packets、walkthrough artifacts、repair loops** 三者保持对齐时。
- **元数据辅助**:
  - `keywords`: design packet / walkthrough / repair loop / semantic verification — 用于检索匹配。
  - `platform: common` — 不绑定特定硬件平台。
  - `depth: foundation` — 基础层模式, 其他上层模式应在其之上构建。
- **典型引用路径**: 在 Regbase 开发总指南、案例笔记中被引用(`next_reads` 已列出), 不作为直接被 import 的代码/配置模块使用。
