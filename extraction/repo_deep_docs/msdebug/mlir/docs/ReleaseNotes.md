# MLIR Release Notes

> 仓 `msdebug` · 路径 `mlir/docs/ReleaseNotes.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msdebug/mlir/docs/ReleaseNotes.md

# MLIR Release Notes 深度解读

## 【定位】
本文档是 MLIR (Multi-Level IR) 在 LLVM 17 与 LLVM 18 两个版本中的官方变更说明（Changelog），按特性维度汇总每次发布的重大能力新增与机制演进，面向 MLIR 用户与方言（dialect）开发者说明升级带来的行为变化与迁移注意事项。

---

## 【技术要点】

1. **Bytecode 序列化（LLVM 17 新增）**：MLIR 引入 bytecode 序列化格式，具备版本兼容能力，支持 **双向兼容方案（2 ways compatibility scheme）**，并提供 **lazy-loading（按需懒加载）** 能力。原文链接：https://mlir.llvm.org/docs/BytecodeFormat/

2. **Properties: beyond attributes（LLVM 17 引入，LLVM 18 设为默认）**：一种用于操作存储的新机制，可在不使用 attributes 的情况下存储数据。在方言定义中使用 `let usePropertiesForAttributes = 1;` 即可为 ODS inherent attributes 启用 Properties。LLVM 18 起该选项成为默认，可设为 `0` 回退旧行为，且 **将在 LLVM 19 中移除该回退开关**。

3. **Action: Tracing and Debugging（LLVM 17 新增）**：将任意粒度的变换（transformation）封装为可被框架拦截的 "Action"，用于调试与追踪，并支持编程式跳过变换（类比 LLVM 的 "compiler fuel" 或 "debug counters"）。Action 的粒度示例包括"执行一个 pass"、"尝试一次 canonicalization pattern"、"tile 一个循环"。

4. **Transform Dialect（LLVM 17 新增）**：作为一项配套能力被引入，并配套提供 EuroLLVM 演讲与在线教程。

5. **Distinct Attributes（LLVM 17 新增）**：新增对 "distinct attributes" 的支持——一类具有唯一标识的属性。原文链接：https://mlir.llvm.org/docs/Dialects/Builtin/#distinctattribute

6. **Resources 与 Configuration 序列化（LLVM 17 新增）**："Resources"（一种在 MLIR Context 之外存储数据的方式）与 "configuration" 现在可与 IR 一同被序列化。

---

## 【关键机制与数据】

### Properties 机制工作原理（原文）
- **存储载体迁移**：原本由属性（attributes）承载的存储，转为由 Properties 承载，避免使用 attributes 带来的开销或语义耦合。
- **启用面**：作用于 **ODS（Operation Definition Specification）中的 inherent attributes**（即操作固有的属性），而非派生属性。
- **版本演进路径**（原文）：
  - LLVM 17：需通过 `let usePropertiesForAttributes = 1;` 显式 opt-in；
  - LLVM 18：默认开启；可用 `0` 显式回退到旧行为；
  - LLVM 19：回退开关将被移除（即强制使用 Properties）。

### Action 机制工作原理（原文）
- **统一抽象**：任何变换——无论粒度大小——都被封装为 Action 对象，框架可在执行 Action 前后进行拦截。
- **典型拦截用途**：调试（debugging）、追踪（tracing）、编程式跳过某次变换。
- **可类比对象**：LLVM 中的 "compiler fuel" 与 "debug counters"（原文明确提及）。

### Bytecode 兼容性方案（原文）
- 原文仅说明支持 "**2 ways compatibility scheme**"（双向兼容方案），并具备 lazy-loading capabilities。原文未提供更具体的版本号或兼容性矩阵数据。

### 性能/数据量化数据
- 原文未提供任何性能基准、内存占用、序列化压缩比等量化指标。

---

## 【表格解读】

**原文无表格。**

本文档为叙述型 Changelog，未包含参数表、性能对比表或配置项表格。所有特性均以条目形式配合外部链接说明。

---

## 【公式解读】

**原文无公式。**

本文档未出现任何数学公式、伪代码或 LaTeX 表达式。涉及机制描述时使用的是自然语言与配置语句（如 `let usePropertiesForAttributes = 1;`），不构成形式化公式。

---

## 【关联】

本节梳理文中特性之间的关联关系及上下游依赖（依据原文出现的链接与措辞）：

1. **Properties ↔ Action**：两者均为 LLVM 17 同一批引入的基础设施级新机制，但原文未说明二者存在直接调用关系，文档将它们作为两条独立特性并列展示。

2. **Properties（LLVM 17）→ LLVM 18 默认化 → LLVM 19 移除回退开关**：构成一条明确的 **三版本迁移路径**，原文以三段陈述串起这条链路。

3. **Action 机制 ↔ Transform Dialect**：Transform Dialect 在 LLVM 17 章节中以独立条目出现，配套 EuroLLVM 演讲与在线教程；Action 机制定位为"调试/追踪变换"的通用拦截层，二者处于同一时期的 MLIR 编译器基础设施演进中，但原文未直接建立二者接口绑定关系。

4. **Bytecode ↔ Resources/Configuration**：两者在 LLVM 17 中同期落地——Bytecode 提供整体 IR 序列化能力，Resources 与 Configuration 则明确了"哪些数据可随 IR 一同被序列化"。原文措辞"can now be serialized alongside the IR"暗示 Resources 与 Configuration 复用了同一序列化通道。

5. **外部引用关系**：
   - Bytecode → https://mlir.llvm.org/docs/BytecodeFormat/
   - Action → https://mlir.llvm.org/docs/ActionTracing/
   - Properties → https://mlir.llvm.org/OpenMeetings/2023-02-09-Properties.pdf
   - Action 演讲 → https://mlir.llvm.org/OpenMeetings/2023-02-23-Actions.pdf
   - Transform Dialect 教程 → https://mlir.llvm.org/docs/Tutorials/transform/
   - Distinct attributes → https://mlir.llvm.org/docs/Dialects/Builtin/#distinctattribute
   - 另指向通用 deprecations 页面 https://mlir.llvm.org/deprecation/

6. **LLVM 17 → LLVM 18 上下衔接**：文档开篇明确"See LLVM 17 notes below"承上启下，表明本文档按版本号倒序组织，且各版本变更说明之间存在显式引用关系。

---

## 【使用方法】

### Properties（启用方式，原文有）

**LLVM 17（opt-in）**：
```tablegen
let usePropertiesForAttributes = 1;
```
在方言（dialect）的 TableGen 定义中加入此语句，即可为该方言的 ODS inherent attributes 启用 Properties。

**LLVM 18（默认开启）**：无需显式声明，默认即生效；若希望回退旧行为：
```tablegen
let usePropertiesForAttributes = 0;
```
该回退开关 **将于 LLVM 19 移除**。

### Bytecode（原文未涉及具体启用命令）

原文仅给出文档链接（https://mlir.llvm.org/docs/BytecodeFormat/），未给出启用该序列化的具体命令或 flag，需查阅该独立文档获取使用方式。

### Action（原文未涉及具体启用命令）

原文仅提供概念说明与文档链接（https://mlir.llvm.org/docs/ActionTracing/），未给出 API 调用示例或编译器 flag。

### Distinct Attributes（原文未涉及具体使用方式）

原文仅给出概念链接（https://mlir.llvm.org/docs/Dialects/Builtin/#distinctattribute），未给出具体语法。

### Transform Dialect（原文未涉及具体启用命令）

原文配套提供在线教程（https://mlir.llvm.org/docs/Tutorials/transform/），未在本 Changelog 中给出具体命令。

### Resources / Configuration 序列化（原文未涉及具体启用命令）

原文仅说明"can now be serialized alongside the IR"，未给出触发该序列化的命令或配置项。

---

**整体小结**：本文档作为 MLIR 的版本演进快照，集中在 LLVM 17 一次性落地了四大基础设施级新机制（Bytecode、Properties、Action、Transform Dialect）及若干周边能力（Distinct Attributes、Resources 序列化），并在 LLVM 18 推进 Properties 的默认化与未来 LLVM 19 的回退开关移除，构成清晰的迁移路线图。文档风格为指向性概要，更详细的 API、命令、参数需经由各特性文档链接深入查阅。
