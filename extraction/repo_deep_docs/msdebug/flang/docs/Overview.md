# Overview of Compiler Phases

> 仓 `msdebug` · 路径 `flang/docs/Overview.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msdebug/flang/docs/Overview.md

# Flang 编译器阶段总览 —— 一体化深度解读

---

## 【定位】

这篇文档勾勒了 Flang 编译器从 Fortran 源码到可执行文件的端到端编译流水线，定义了**三大高层阶段（analysis / lowering / code generation & linking）**及其下属的若干**细粒度阶段**，并给出每一阶段的输入、输出、入口函数（`Entry point`）与调试命令。

---

## 【技术要点】

1. **三大高层阶段** —— ① 分析（将 Fortran 源码 → 装饰过的 parse tree 与 symbol table，并完成用户程序全部错误检测）；② 降级（将装饰过的 parse tree + symbol table → FIR，即 MLIR 的一种方言，再经若干 passes → LLVM IR）；③ 代码生成与链接（沿用 LLVM 既有基础设施生成目标文件并调用链接器产出可执行文件）。

2. **分析阶段的三条细粒度子阶段**
   - **Prescan and Preprocess**：入口 `parser::Parsing::Prescan`，输出"cooked"字符流与 provenance（出处）映射。
   - **Parsing**：入口 `parser::Parsing::Parse`，针对每个 program unit 生成以 program unit 为根的 parse tree。
   - **Semantic processing**：入口 `semantics::Semantics::Perform`，同时消费 parse tree、cooked 字符流与 provenance，产出 symbol table、改造后的 parse tree、module files、内建过程表（intrinsic procedure table）、目标特性（target characteristics）以及运行时派生类型表（runtime derived type tables）。

3. **降级阶段的三条细粒度子阶段**
   - **Create the lowering bridge**：入口 `lower::LoweringBridge::create`，输入包含 parse tree、symbol table、内建类型默认 KIND、内建过程表、目标特性、cooked 字符流、target triple 以及 Fortran KIND ↔ FIR KIND 映射。
   - **Initial lowering**：入口 `lower::LoweringBridge::lower`，先把信息组织成 pre-FIR tree（PFT），再遍历 PFT 产出 FIR。
   - **Transformation passes**：入口 `mlir::PassManager::run`，依次执行 verification pass → 若干 transformation/opt 优化 pass → 最终生成 LLVM IR 的 pass。

4. **关键调试/转储命令**（原文逐条列出）：
   - `flang-new -fc1 -E src.f90` —— 导出 cooked 字符流
   - `flang-new -fc1 -fdebug-dump-provenance src.f90` —— 导出 provenance
   - `flang-new -fc1 -fdebug-dump-parse-tree-no-sema src.f90` —— 导出 parse tree
   - `flang-new -fc1 -fdebug-unparse src.f90` —— 将 parse tree 反解为 normalized Fortran
   - `flang-new -fc1 -fdebug-dump-parsing-log src.f90` —— 输出插桩后的 parse log
   - `flang-new -fc1 -fdebug-measure-parse-tree src.f90` —— 测量 parse tree
   - `flang-new -fc1 -fdebug-dump-parse-tree src.f90` —— 导出语义分析后的 parse tree
   - `flang-new -fc1 -fdebug-dump-symbols src.f90` —— 导出 symbol table
   - `flang-new -fc1 -fdebug-dump-all src.f90` —— 同时导出 parse tree 与 symbol table
   - `flang-new -fc1 -fdebug-dump-pft src.f90` —— 导出 PFT
   - `flang-new -fc1 -emit-mlir src.f90` —— 把 FIR dump 到 `src.mlir`
   - `flang-new -mmlir --mlir-print-ir-after-all -S src.f90` —— 每个 MLIR pass 之后把 FIR 打印到 stderr
   - `flang-new -fc1 -emit-llvm src.f90` —— 把 LLVM IR dump 到 `src.ll`

5. **语义分析承担的任务清单**（原文逐条列举）：
   校验 labels；规范化 DO 循环；规范化 OpenACC 与 OpenMP 代码；解析名称并构造 scopes 与 symbols 树；在需要时重写 parse tree 以纠正 parsing 阶段含糊之处；检查声明合法性；分析与检查表达式、语句并按需报错；若源码包含 modules 则生成 module files。

6. **错误与终止语义**：原文明确"Each detailed phase produces either correct output or fatal errors."——亦即每个细粒度阶段只能成功产出或直接 fatal，不存在中间态。

---

## 【关键机制与数据】

- **数据流总览（原文逐句复述）**：
  - 源码 → cooked 字符流 + provenance → parse tree → parse tree 装饰 + symbol table + 内建过程表 + 目标特性 + 模块文件 → lowering bridge → PFT → FIR → LLVM IR → object code → 可执行文件。
  
- **PFT 的内部层次（原文描述）**：PFT 是 programs 与 modules 的列表；programs/modules 内含 function-like units 的列表；function-like units 内含 evaluations 的列表；所有这些节点都"contain pointers back into the parse tree"，编译器通过遍历 PFT 来生成 FIR。

- **Provenance 信息（原文："This includes error messages, optimization reports, and debugging information"）**：用于在后续阶段需要"源码位置"时定位每一字符的出处。

- **cooked 字符流的归一化操作（原文）**：删除多余的空白与注释（被禁用的非指令注释同样会移除）；大小写归一化；directives 处理；宏展开。语义分析也"folds constant expressions"——常量折叠被列为语义分析的子动作之一。

- **性能数据**：原文未给出任何 benchmark 数字或时间/内存指标；无性能表可引用。

---

## 【表格解读】

**原文无表格**。所有阶段信息都以"分节标题 + 输入/输出/Entry point/Commands 四段式"展开，没有使用任何参数表或配置表。

---

## 【公式解读】

**原文无公式**。文档通篇为流程性描述，不含 LaTeX 表达式、伪代码或数学公式。

---

## 【关联】

文档以阶段为单位，链接出若干下游细节文档，构成"FIR/LLVM IR 之前的全编译流水线"的整体视图：

- **[Preprocessing.md](Preprocessing.md)** — `Prescan and Preprocess` 子阶段的深入展开，对应入口 `parser::Parsing::Prescan`。
- **[Parsing.md](Parsing.md)** & **[ParserCombinators.md](ParserCombinators.md)** — `Parsing` 子阶段的深入展开，对应入口 `parser::Parsing::Parse`；后者进一步说明 parser combinator 风格。
- **[Semantics.md](Semantics.md)** — `Semantic processing` 的细节，对应入口 `semantics::Semantics::Perform`。
- **[LabelResolution.md](LabelResolution.md)** — 语义分析中"validates labels"任务的展开。
- **[ModFiles.md](ModFiles.md)** — 出现两次：① 作为语义分析的输出（"module files, see: ModFiles.md"）；② 作为语义分析子任务"creates module files if the source code contains modules"的展开。是语义阶段 → 模块编译产物的中间产物。
- **[RuntimeTypeInfo.md](RuntimeTypeInfo.md)** — 语义分析输出之一"the runtime derived type derived type tables"的展开。

文档未提及的上下游关系（如代码生成与链接阶段、LLVM 后端等）原文只以"flang driver invokes LLVM's existing infrastructure"一句话带过，无内部链接。

---

## 【使用方法】

原文未涉及任何"启用/配置"语义。所有 `-fc1 -<flag>`、`-emit-mlir`、`-emit-llvm` 等命令都属于**调试/转储各阶段产物**的方式，而非启用某项功能。配置项方面，原文只在"Create the lowering bridge"的输入里提到一处可选来源：

- 原文（Create the lowering bridge 输入条目）："The default KINDs for intrinsic types (specified by default **or** command line option)"。

也即：内建类型默认 KIND 既可以走默认值，也可以由命令行选项指定——原文未给出具体选项名。除此之外，本文档未提供更多配置项说明。
