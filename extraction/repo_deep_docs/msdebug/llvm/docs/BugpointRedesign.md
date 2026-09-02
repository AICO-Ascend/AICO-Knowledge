# Bugpoint Redesign

> 仓 `msdebug` · 路径 `llvm/docs/BugpointRedesign.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msdebug/llvm/docs/BugpointRedesign.md

# Bugpoint Redesign 文档深度解读

## 【定位】

这篇文档是一篇 **Draft 状态的设计提案**，针对 LLVM 既有 `bugpoint` 工具长期存在的"难用、慢、产出测试用例质量不稳定"等问题，提出将其重塑为一款**专注于 IR 测试用例最小化（delta reduction）**的窄聚焦工具，灵感来自 CReduce / Delta / Lithium 等同类 delta reduction 工具。

---

## 【技术要点】

1. **窄聚焦策略**：新设计将 bugpoint 的核心目标收敛到"让 IR 测试用例尽可能小，但仍保持原有的 interesting-ness 性质"；通过经典 delta debugging 加上 IR 特定的归约手段（替换 globals、删除未使用指令等）实现"更深入的最小化"（原文：*"obtain much smaller test cases that still have the same property as the original one"*）。
2. **CLI 极度精简**：原文提议把现有"数量繁多、行为令人困惑"的 bugpoint 选项削减到**仅两项**——`--test=<test_name>` 与 `--test_args=<test_arguments>`，对应类比对象为 `-compile-custom` 选项（原文：*"reduce the plethora of bugpoint's options to just two"*）。
3. **强制要求外部 test 脚本**：`--test` 不提供时程序直接退出；脚本以 **返回值 0 = 命中用户定义的行为**（如 clang 编译失败），**非 0 = 不命中**，将"什么算 interesting"的判定权完全下放给用户（原文：*"returns 0 when the IR achieves a user-defined behaviour"*）。
4. **输入文件作为脚本参数**：与 `-compile-custom` 一致，input ll/bc 文件将作为参数传递给 test 脚本；脚本自身的额外参数通过 `--test_args` 传入，未指定时按脚本原样运行。
5. **首版归约 Pass 列表（4 项）**：① 丢弃不影响 interesting-ness 的 functions / instructions / metadata；② 移除函数未使用参数；③ 消除未被访问到的条件分支；④ 将变量重命名为"a, b, c…"等更规则的命名（原文逐条列出）。
6. **可扩展的模块化结构**：归约器以"一组 pass"的形式组织，行为可模块化，便于后续添加更高级的归约（如**类型归约 type reduction**）以及代码维护（原文：*"modularize the tool's behavior, as well as making it easier to maintain and expand"*）。

---

## 【关键机制与数据】

**整体工作原理（基于原文推断/陈述）**：
- 用户预先编写一个判断脚本（shell 脚本等），用 `--test` 指定其名称，用 `--test_args` 传递除输入文件之外的额外参数。
- 工具读取待归约的 ll/bc IR 文件，将其**作为参数**调用 test 脚本：返回 0 → 当前 IR 仍"interesting"（保留），非 0 → 不 interesting（可继续裁剪）。
- 工具按顺序运行一组最小化 pass：先丢弃无影响 functions / instructions / metadata，再去掉函数未用参数，再清掉 unvisited 条件路径，最后做变量规范化重命名；每步都重新跑 test 脚本验证 interesting-ness 是否保持。
- 整体架构对标 **CReduce 的功能模型**——以"pass 列表驱动归约"的方式实现（原文：*"similar to CReduce's functionality in that it would have a list of passes that try to minimize the given test-case"*）。

**性能相关数据（原文）**：
- 关于旧 bugpoint 的运行开销，原文给出的定性描述是"**takes a long time**"，原因是会运行"**various strategies**"对 bug 进行分类，过程中多次执行优化器与编译 pass；并提到现有归约中存在"**a lot of unreachable blocks**"等次优 pass 行为（原文："*taking up a lot of time*"）。  
  **原文无任何具体数字、计时或量化性能数据**。

---

## 【表格解读】

**原文无表格**（全文未出现任何 markdown / 文本表格；所有规则均以散文与代码块形式表达）。

---

## 【公式解读】

**原文无公式**（全文未出现 LaTeX、伪代码或数学表达式；唯一的"代码块"是 CLI 选项示意 `--test=<test_name>` 与 `--test_args=<test_arguments>`，已在【技术要点】中按字面引用）。

---

## 【关联】

- **对标工具**：CReduce、Delta、Lithium——三者均为通用 delta reduction 工具，是本次重设计的灵感来源与功能对照对象（原文：*"similar to other delta reduction tools such as CReduce, Delta, and Lithium"*）。
- **对标既有选项**：新 `--test` 在语义上对应 bugpoint 现有的 `-compile-custom`，用以"运行用户自定义脚本"；输入 ll/bc 文件作为脚本参数的传递方式也沿用 `-compile-custom` 当前的行为（原文：*"this option is similar to bugpoint's current `-compile-custom` option"* / *"similar how `-compile-custom` currently operates"*）。
- **可扩展的上下游**：首版仅实现 4 项基础归约；文档明确将 **type reduction（类型归约）** 列为"more meaningful reductions"的下一步加入项，表明此重设计是一个面向长期迭代的平台，而非一次性产出（原文：*"Once these passes are implemented, more meaningful reductions (such as type reduction) would be added"*）。
- **对旧功能的兼容取舍**：若社区不接受该聚焦方案，遗留代码理论上可以保留，但需以"delta reduction"为文档与设计目标重新定位（原文：*"the legacy code could still be present in the tool, but with the caveat of still being documented and designed towards delta reduction"*）。
- **内部链接**：原文末尾无任何链接信息（标注"内部链接: (无)"）。

---

## 【使用方法】

按原文所述，新设计启用方式如下（**仅两条 CLI 标志**）：

| 标志 | 必选？ | 作用 |
|---|---|---|
| `--test=<test_name>` | **是**（未提供则程序直接退出） | 指定 interesting-ness 测试脚本名称；语义对应旧 `-compile-custom` |
| `--test_args=<test_arguments>` | 否（未指定则脚本按原样运行） | 传递给 test 脚本的额外参数（**不含**输入的 ll/bc 文件本身） |

**调用契约（原文规定）**：
- 输入的 ll/bc IR 文件作为 test 脚本的参数传入（与现有 `-compile-custom` 一致）。
- Test 脚本**返回值 0** ⇒ 当前 IR 仍"interesting"（保留该裁剪候选）；**返回非 0** ⇒ 不 interesting（可继续裁剪）。
- 用户自行定义"什么算 interesting"（如让 clang 编译失败作为判定条件）。

> 原文未涉及：构建选项、环境变量、配置文件路径、默认脚本模板或更多 flags（重设计的核心理念就是**砍掉其它一切 CLI**）。
