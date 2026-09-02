# Confirm Guide (C-confirm)

> 仓 `agent-skills` · 路径 `official/PyTorch/op-adaptation/references/guides/confirm-guide.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/agent-skills/official/PyTorch/op-adaptation/references/guides/confirm-guide.md

# Confirm Guide (C-confirm) 深度解读

## 【定位】
本指南是 agent-skills 仓库「PyTorch op-adaptation」流程中 C-confirm 环节的标准操作文档，解决的是**在算子适配过程中，如何与用户进行结构化确认（冲突处理、版本分析、标准问询）以避免单方面决策导致信息遗漏的问题**。

---

## 【技术要点】

1. **冲突确认必须先行 (FIRST)**：在询问任何标准问题之前，必须先提交 CHECKLIST.md "Conflict Confirmation" 表中所有 ⚠️ 项；用户须显式回复 ✅ Include 或 ❌ Exclude，禁止代为决策。
2. **典型冲突示例**：原文明示 "_def.cpp has `group_index` parameter but .md does not mention it"，即 `_def.cpp` 与 `.md` 文档间的参数缺失/不一致。
3. **默认值冲突的处理方式**：当 `_def.cpp` 与 `.md` 默认值不一致时，须按原问句模板提问 "Use _def.cpp value ({X}) or .md value ({Y})?"。
4. **CHECKLIST.md 持续更新**：每次冲突解决后立即更新 CHECKLIST.md。
5. **V2 版本深度分析触发条件**：当 C-parse 自检项 5 检测到 V2 特有属性时，需向用户呈现属性列表并请求是否实现 V2 实现 (并要求用户提供 V2 aclnn signature 文档)。
6. **算子类型驱动的 Autograd 反向问询**：根据 C-parse 自动识别的算子类型 (backward/grad vs forward)，切换不同的 autograd 关联问询路径；forward 与 backward 算子均需注册至 C-yaml，绑定添加至 C-derivatives。

---

## 【关键机制与数据】

**工作原理 / 数据流** (基于原文梳理):

- **C-confirm 的输入来源**：上游 C-parse 阶段产出的 CHECKLIST.md (含 ⚠️ 冲突项、V2 属性自检结果、自动识别的算子类型) 决定 C-confirm 需要展示的内容。
- **C-confirm 的输出目的地**：用户答复被记录到 CHECKLIST.md 的 "Information Required from User" 区域，作为后续环节的依据。
- **V2 版本深度分析的示例数据 (原文)**：
  - `group_list_type` (Int, default: 0)
  - `dst_type` (Int, default: DT_INT8)
  - 分析结论原文："Output DataType variant analysis: V2 extends output support to INT4"
  - 推荐实现 V2 的理由原文："V2 attributes are common in quantization operators (cumsum/count mode, multi-precision output)"
- **典型 SoC 变体 (原文)**：Ascend950
- **典型 CANN 版本变体 (原文)**：V2 / V3 / V5
- **典型 torch_npu 函数变体 (原文)**：`_asymmetric`、`_v0`
- **典型特殊数据格式 (原文)**：mxfp4
- **性能数据**：原文无任何性能数据。

---

## 【表格解读】

原文无表格 (CHECKLIST.md 中的 "Conflict Confirmation" 表与 "Information Required from User" 区域均被引用但未在本 guide 内展示)。

---

## 【公式解读】

原文无公式。

---

## 【关联】

依据原文 C-confirm 在工作流中扮演的角色，可关联到的上下游环节如下 (均为原文出现或隐含关系):

- **上游：C-parse**
  - 触发 V2 深度分析："When C-parse found V2-specific attributes (self-check item 5)" —— C-confirm 的 V2 展示依赖于 C-parse 自检项 5。
  - 触发 Autograd 分支问询："based on auto-detected operator type from C-parse" —— backward/forward 算子类型由 C-parse 自动判定。
  - 输出冲突数据源：CHECKLIST.md 中的 ⚠️ 项来自 C-parse。

- **下游 (隐含)**：
  - **C-yaml**：原文提及 "Both forward and backward operators need to be registered in C-yaml" —— C-confirm 的注册信息收集后用于 C-yaml 注册环节。
  - **C-derivatives**：原文提及 "the binding added in C-derivatives" —— 反向绑定由 C-confirm 收集的 autograd 信息驱动。

- **辅助文件**：CHECKLIST.md 是 C-confirm 阶段的核心读写对象 (Conflict Confirmation 表、Information Required from User 区域)。

- **内部链接**：原文末尾无内部链接。

---

## 【使用方法】

原文未提供独立的启用命令或配置项 (本 guide 是流程文档而非代码模块)，其「使用方法」即执行流程本身：

1. **步骤 1 — Conflict Confirmation (FIRST)**：遍历 CHECKLIST.md 中所有 ⚠️ 项 → 按原问句模板提问 → 等待用户显式 Include/Exclude 答复 → 立即更新 CHECKLIST.md。
2. **步骤 2 — Version Depth Analysis** (条件性)：若 C-parse 自检项 5 检出 V2 属性 → 呈现属性清单与推荐理由 → 提问 "Do you want to implement V2? (If yes, please provide the V2 aclnn signature documentation.)"。
3. **步骤 3 — Standard Questions**：逐项询问 CANN 版本分发、SoC 分发、`.List` 重载、torch_npu 函数变体、`internal_format_opapi`、特殊数据格式、Autograd 需求；同时邀请用户补充未列出的信息。
4. **步骤 4 — 记录**：将所有答复写入 CHECKLIST.md "Information Required from User" 区域。
5. **Troubleshooting**：原文标注 "(Accumulate from cases.)"，表示该章节将随案例积累持续补充，**当前无可用排查条目**。
