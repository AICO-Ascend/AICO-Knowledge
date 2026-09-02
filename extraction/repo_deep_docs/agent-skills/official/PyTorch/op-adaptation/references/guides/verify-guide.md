# Verify Guide (C-verify)

> 仓 `agent-skills` · 路径 `official/PyTorch/op-adaptation/references/guides/verify-guide.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/agent-skills/official/PyTorch/op-adaptation/references/guides/verify-guide.md

```markdown
# verify-guide.md 一体化深度解读

## 【定位】
本文档是昇腾 PyTorch 算子适配流程中 C-verify（签名一致性校验）步骤的详细操作手册，解决"在 create/modify 模式下如何系统化核对 YAML、C++、Meta 注册、Schema JSON、Derivatives 之间的算子签名一致性以避免晦涩的构建/链接错误"的问题。

## 【技术要点】
1. **执行时机与范围**：在 build 之前完成；create 模式覆盖全量文件，modify 模式仅覆盖受影响文件（原文："Create mode: all files. Modify mode: affected files only."）。
2. **YAML ↔ C++ 签名核对**：从 `op_plugin_functions.yaml` 的 `func:` 行抽取参数列表，与 C++ 实现文件的函数签名比对，检查参数名、类型、顺序三者一致；不匹配则上报具体差异并拒绝继续（原文："Report specific mismatches and refuse to proceed until fixed"）。
3. **YAML ↔ Meta 注册签名核对**：从 `_meta_registrations.py` 中 `@impl` 函数抽取参数列表，校验其是否完整包含 YAML `func:` 行的全部参数，识别缺失/多余项。
4. **Schema JSON `func:` 条目预检（为 C-baseline 做准备）**：要求 Schema JSON 中 `func:` 签名与 YAML 完全一致，且明确禁止手动输入，要求直接从 YAML 复制（原文："No manual typing — copy directly from YAML"）。
5. **Derivatives 签名核对（条件触发）**：仅当已执行过 C-derivatives 时启用，校验 `name:` 字段等于 forward 算子在 `op_plugin_functions.yaml` 中的 `func:` 行；backward 表达式中每一个参数都必须在 forward 算子签名中存在；backward 算子名称必须存在已注册的 `func:` 条目。
6. **失败策略**：所有一致性检查的最终手段是"拒绝继续"，直至差异被修复，从源头阻断签名错位向 build/link 阶段传递。

## 【关键机制与数据】
- **工作原理**：C-verify 是一个静态、跨多文件的签名一致性比对过程，本身不修改代码，只在上游输入（YAML/Schema JSON/C++/Python Meta）与下游消费方（C++ 实现、`@impl`、derivatives 注册）之间做"一一对应"核查，充当 op-adaptation 流程中的质量门禁。
- **数据流（按检查顺序）**：
  1. YAML `op_plugin_functions.yaml` 的 `func:` 行 → 作为单一真源（single source of truth）；
  2. 流 ①：YAML ↔ C++ 实现文件（参数名/类型/顺序）；
  3. 流 ②：YAML ↔ `_meta_registrations.py` 的 `@impl` 函数（参数覆盖性）；
  4. 流 ③：YAML → Schema JSON 的 `func:` 条目（视为 C-baseline 的预览复制）；
  5. 流 ④：YAML forward `func:` → Derivatives 的 `name:`、表达式参数列表、`func:` 注册存在性（条件性）。
- **错误后果提示**（原文）：签名不一致会导致"obscure build/link errors"——即错位不会在签名校验阶段被立刻定位，而是在后续编译或链接时以隐晦形式暴露，故必须前置拦截。
- **性能/量化数据**：原文未给出任何数字指标、阈值或性能数据。

## 【表格解读】
原文无表格。

## 【公式解读】
原文无公式。

## 【关联】
- **与 C-verify 自身的关系**：本文档为 C-verify 在 create/modify 两种模式下的统一参考手册（原文："Reference this guide when executing C-verify in either create or modify mode."）。
- **上游关联**：
  - `op_plugin_functions.yaml` 的 `func:` 行是四条签名检查的共同基准（single source of truth）；
  - C++ 实现文件、`_meta_registrations.py` 的 `@impl` 函数、Schema JSON 的 `func:` 条目均依赖该 YAML；
  - C-derivatives 的执行结果是 Derivatives 签名检查的前置条件（"if C-derivatives was executed"）。
- **下游关联**：
  - Schema JSON 校验被定位为"C-baseline 的预览"，表明 C-baseline 步骤将消费同一份 `func:` 签名；
  - 全部签名核对通过后才会进入 build 阶段，避免"obscure build/link errors"；
  - Troubleshooting 一节标注"Accumulate from cases"，意味着本文档会持续吸收来自实际案例的故障条目作为下游反馈。
- **内部链接**：原文未提供任何内部链接。

## 【使用方法】
- **启用方式**：在 op-adaptation 流程中执行 C-verify 步骤时，按本文档"Signature Consistency Verification"四节顺序逐项核对；create 模式覆盖所有文件，modify 模式仅覆盖受影响文件。
- **配置项/命令**：原文未涉及任何具体开关、环境变量、CLI 命令或配置项；操作完全由检查项 1–4 的描述驱动。
- **失败处理**：任何一项不匹配都必须由开发者修复后重新校验，原文策略是"refuse to proceed until fixed"。
- **故障经验沉淀**：Troubleshooting 段注明以案例形式持续累积，原文未列举具体案例。
```
