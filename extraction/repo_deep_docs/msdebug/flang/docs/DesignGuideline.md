# Design Guideline

> 仓 `msdebug` · 路径 `flang/docs/DesignGuideline.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msdebug/flang/docs/DesignGuideline.md

# Flang DesignGuideline.md 一体化深度解读

## 【定位】

本文档是 Flang（前 LLVM Fortran 编译器）项目的**设计文档撰写规范与新特性设计方法论指南**，规定在为 Flang 添加新特性时如何组织、提交、审阅设计文档，并为设计者提供从标准研读到实现路径规划的完整思考步骤。

---

## 【技术要点】

1. **设计文档四段式结构**：原文明确要求按 `1) Problem description / 2) Proposed solution / 3) Implementation details overview / 4) Testing plan` 组织，并要求在第 2 段简要描述被否决的备选方案。
2. **Phabricator 审阅作为提交前置条件**："Its approval on Phabricator is the pre-requisite to submitting patches implementing new features."
3. **Discourse RFC 流程**：可在 https://discourse.llvm.org 先发起 RFC，但最终必须产出设计文档；未先发起 RFC 的，需在送审 Phabricator 时同步在 discourse 发布简短公告附上 Phabricator 链接。
4. **跨项目影响走 LLVM 通用流程**：涉及 OpenMP、OpenACC 等超出 flang 树范围的特性，必须遵循 LLVM DeveloperPolicy 的 general process；只要解决方案对 flang 有显著影响（如 parse-tree 到 OpenMP/FIR dialect 的 lowering 非直接映射），仍需 flang 设计文档。
5. **Fortran 2018 标准作为术语与引用基准**：原文两处明确要求 "References should currently be given against the Fortran 2018 standard version"，术语定义见标准 Section 3。
6. **设计文档样式约束**：篇幅不必长，鼓励使用 Fortran 代码片段；lowering 相关问题需附 FIR 与 LLVM IR 代码片段；插图不要求可运行，聚焦特性即可，细节可后续补充或以 LIT 测试形式呈现。

---

## 【关键机制与数据】

**工作原理 / 数据流（内联代码 lowering 路径，原文:）**

> "For inlined code, consider what should happen when generating the FIR, what should happen in the FIR transformation passes (FIR to FIR), and what should happen when lowering the FIR to LLVM IR."

即内联代码的实现路径为 **parse-tree → FIR → FIR-to-FIR transformation → LLVM IR**。

**实现方案变更机制（原文:）**

> "When doing a significant change to the implementation solution for a feature, the related design document should be updated so that it will justify the new solution."

即特性实现方案发生重大变更时，必须同步更新设计文档以论证新方案的合理性。

**二进制兼容性基线（原文:）**

> "F77 libraries compiled with other Fortran compilers (at least gfortran) should link with flang compiled code and vice-versa."

即 F77 层面的二进制兼容性目标至少覆盖 **gfortran**。

**新 FIR 操作判定原则（原文:）**

> "For inlined ops, look at how the existing dialects can be reused. If new FIR operations are required, justify their purpose."

即新增 FIR op 需证明现有 dialect 不可复用，并论证新 op 的存在目的。

---

## 【表格解读】

**原文无表格。**

---

## 【公式解读】

**原文无公式。**

---

## 【关联】

本文档作为元规范（meta-guideline），将 Flang 的设计活动与以下外部/内部资源串联：

| 关联对象 | 关联性质 | 原文出处 |
|---|---|---|
| Flang features to be implemented (GitHub Project #12) | 新特性需求来源 | "new features that need support in flang are listed in llvm github project [Flang features to be implemented]" |
| LLVM Testing Guide | 测试方案参考 | "what aspects will be tested with LLVM unit test tools (see LLVM Testing Guide)" |
| LLVM DeveloperPolicy | 跨子项目重大变更流程 | "should follow the general LLVM process" |
| Phabricator | 设计文档审阅与代码提交前必经 | "Its approval on Phabricator is the pre-requisite" |
| discourse.llvm.org | RFC 讨论与公告平台 | "An RFC on flang https://discourse.llvm.org can first be made" |
| Fortran 2018 标准 Section 3 | 术语定义与约束编号来源 | "definitions of these terms can be found in Section 3 of Fortran 2018 standard" |
| gfortran | 二进制兼容性对照编译器 | "at least gfortran should link with flang compiled code" |
| FIR（Flang IR） | 中间表示层，承载 lowering 输出与转换 | "illustrate lowering output with a few FIR and LLVM IR code snippets" |
| Semantics 模块（parse tree / Symbol / evaluate::Expr） | 设计时需考察的语义表示 | "Look at the related representation in Semantics (e.g., is some information from the parse tree, the Symbol or evaluate::Expr required?)" |
| Fortran runtime | 可选委派实现路径 | "delegating part of the work to the Fortran runtime may be a solution" |

---

## 【使用方法】

**启用方式 / 配置项 / 命令（原文整理）：**

1. **设计文档存放位置**：原文："The design document should be added to the `docs` folder as a markdown document, ideally using the name of the feature as the document name."
   - 路径：`flang/docs/`
   - 命名：建议以特性名作为文档名
2. **提交前置**：Phabricator 设计文档审阅通过后，方可提交实现该特性的代码补丁。
3. **标准引用基准**：使用 Fortran 2018 标准的章节号与约束编号（Cxxx）作为精确引用。
4. **跨项目特性**：涉及 OpenMP / OpenACC 等需触及其他 LLVM 子项目的，按 LLVM DeveloperPolicy 的 "Making a Major Change" 流程执行。
5. **设计思考步骤**（原文给出的 7 步法）：
   - 识别标准中相关章节与约束
   - 编写使用该特性的 Fortran 程序并用现有编译器验证预期
   - 检查约束是否已被语义检查强制；如未强制，可先补语义检查（无需设计文档）
   - 识别与其他 Fortran 编译器的兼容性影响及未来不可逆性
   - 识别相关特性或上下文（内部过程、模块、block 等）
   - 考虑是否将部分工作委派给 Fortran runtime
   - 分别考虑 FIR 生成、FIR-to-FIR 变换、FIR 到 LLVM IR 的 lowering 三个阶段，以及现有 dialect 的复用与新 FIR op 的论证
6. **测试方案说明**：简要说明使用 LLVM 单元测试工具覆盖的方面，以及可复用的端到端测试套件或应用。
