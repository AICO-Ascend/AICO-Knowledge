# Chapter 2: Adding a Simple New Transformation Operation

> 仓 `msdebug` · 路径 `mlir/docs/Tutorials/transform/Ch2.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msdebug/mlir/docs/Tutorials/transform/Ch2.md

【定位】
这篇文档是 MLIR Transform dialect 教程的第 2 章,讲解如何通过 **dialect extension 机制** 向 Transform dialect 注入一个新的变换操作(Transformation Operation),从而在不必修改 Transform dialect 本体的情况下,为 out-of-tree dialect 或自定义场景添加可被 dialect interpreter 调度的变换算子。

【技术要点】

1. **Dialect Extension 机制(CRTP 模板)**:通过 `mlir::transform::TransformDialectExtension<MyExtension>` 派生类(使用 CRTP 惯用法)注册到 MLIR Context,跟随 Transform dialect 一同加载。必须显式继承 `Base::Base` 构造函数,并在 `init()` 中完成注册。

2. **两类 dialect 区分**(原文明确命名):
   - `declareDependentDialect<>()`:由变换操作 **使用** 属性/类型的 dialect,会随 extension 一起被加载;
   - `declareGeneratedDialect<>()`:**变换执行过程中可能产生** 但原 payload IR 中没有的 dialect。文中给出的示例是 `SCFDialect` 和 `FuncDialect`,作为 generated dialect 声明。

3. **必备接口(Operation 必须实现)**:
   - `TransformOpInterface`(目前只要求实现 `apply` 方法);
   - `MemoryEffectsOpInterface`,用于声明 operand 是被 consume 还是只 read。

4. **三态变换结果(`apply` 返回值)**:
   - `success`:变换成功;
   - `definite failure`:失败且后续变换无法继续,通常在失败前已 emit 诊断;
   - `silenceable failure`:失败但后续变换仍可应用,通常意味着前置条件不满足,payload IR 未被修改(原文在末尾被截断,标注"silen")。

5. **ODS 操作定义要点**:
   - 命名约定:扩展前缀(`my.`) + 操作名(`change_call_target`) → 最终名 `transform.my.change_call_target`;
   - 参数包括 `TransformHandleTypeInterface:$call` 与 `StrAttr:$new_target`;
   - 结果为空(`let results = (outs);`);
   - 自定义 assembly format:`"$call `,` $new_target attr-dict `:` type($call)"`。

【关键机制与数据】

**工作原理 / 数据流**

1. **Extension 注册路径**(原文代码 `MyExtension.cpp`):
   - `init()` 内调用 `declareGeneratedDialect<SCFDialect>()` 和 `declareGeneratedDialect<FuncDialect>()`;
   - 再调用 `registerTransformOps<...>()`(列表通过 `#define GET_OP_LIST` + `#include "MyExtension.cpp.inc"` 展开)。

2. **Tablegen 生成链**(原文 `CMakeLists.txt next to MyExtension.td`):
   - `set(LLVM_TARGET_DEFINITIONS MyExtension.td)` 指明输入;
   - `mlir_tablegen(... -gen-op-decls)` 生成声明;
   - `mlir_tablegen(... -gen-op-defs)` 生成定义;
   - `add_public_tablegen_target(MyExtensionIncGen)` 作为依赖目标;
   - `add_mlir_doc(MyExtension MyExtension Dialects/ -gen-op-doc)` 自动产出 `Dialects/MyExtension.md` 文档。

3. **编译时强制接口检查**(原文注释):`registerTransformOps<...>()` 在调用时会 **断言操作已实现 transform 与 memory effect 接口**,否则编译期失败。

5. **ODS 包含路径**(原文 `MyExtension.td`):
   - `TransformDialect.td`、`TransformInterfaces.td`、`OpBase.td`、`SideEffectInterfaces.td`。

7. **库依赖**(原文 CMake 片段 `LINK_LIBS PUBLIC`):
   - `MLIRTransformDialect`、`MLIRFuncDialect`、`MLIRSCFDialect`。

8. **变换实现原则**(原文段落):`apply` 方法体应仅操控 Transform dialect 构造,真正的变换逻辑实现为独立函数(类似 rewrite pattern),所有 IR 修改必须通过提供的 `rewriter` 完成。

【表格解读】
原文无表格(全文由叙述段落、ODS/C++/CMake/sh 代码块构成,无 markdown 表格)。

【公式解读】
原文无公式(无 LaTeX 或伪代码公式;唯一类似"公式"的是 ODS 中的 assembly format 字符串 `"$call `,` $new_target attr-dict `:` type($call)"`,属于 MLIR 自有的操作语法格式声明,符号含义:`$call` / `$new_target` 引用参数,`` `,` `` 字面量逗号,`attr-dict` 属性字典,`` `:` `` 字面冒号,`type($call)` 输出 `$call` 的类型)。

【关联】

- **章节关系**:本文为 Chapter 2,其上下文是教程系列;原文 init() 注释中提到 "In the following chapter, we will be add operations that generate function calls and structured control flow operations",因此 Chapter 3 会扩展出产生 `func.call` 与 SCF 操作的变换(这也是本章提前把 `SCFDialect`、`FuncDialect` 声明为 generated dialect 的原因)。
- **与 Transform dialect 关系**:本文通过 `TransformDialectExtension` 把新算子挂接到 Transform dialect,**不修改** dialect 本体;操作必须继承 `Transform_Dialect` 父类并实现两个接口才能被 dialect interpreter 调度。
- **与 rewriter / pattern 体系关系**:`apply` 推荐风格(独立函数 + rewriter)与 MLIR 传统 DRR/GCC-style pattern 体系保持一致,便于复用。
- **依赖的 ODS 文件**:依赖 Transform dialect 的接口表(`TransformInterfaces.td`)与副作用表(`SideEffectInterfaces.td`)。

【使用方法】
原文涉及的具体配置/命令步骤(按出现顺序整理):

1. **Extension 类骨架**:派生 `transform::TransformDialectExtension<MyExtension>`,使用 `Base::Base` 构造函数,声明 `void init();`。

2. **`init()` 内调用**:
   - `declareDependentDialect<...>()` / `declareGeneratedDialect<...>()`(示例:`SCFDialect`、`FuncDialect`)。
   - `registerTransformOps<...>()` 模板参数为 `#define GET_OP_LIST` + `#include "MyExtension.cpp.inc"`。

3. **ODS 操作定义文件**:`MyExtension.td` 中用 `Op<Transform_Dialect, "my.<name>", [...]>` 定义算子,补 `summary` / `description` / `arguments` / `results` / `assemblyFormat`。

4. **头/实现文件包含**:
   - `MyExtension.h` 中 `#define GET_OP_CLASSES` + `#include "MyExtension.h.inc"`;
   - `MyExtension.cpp` 中 `#define GET_OP_CLASSES` + `#include "MyExtension.cpp.inc"`。

5. **CMake(.td 侧)**:`set(LLVM_TARGET_DEFINITIONS MyExtension.td)` → `mlir_tablegen` 生成 decls/defs → `add_public_tablegen_target(MyExtensionIncGen)` → `add_mlir_doc(... Dialects/ -gen-op-doc)`。

6. **CMake(.cpp 侧)**:`add_mlir_library(MyExtension MyExtension.cpp DEPENDS MyExtensionIncGen LINK_LIBS PUBLIC MLIRTransformDialect MLIRFuncDialect MLIRSCFDialect)`。

7. **运行时接入**:Extension 实例需在 Context 加载 Transform dialect 时一并注册(原文未列出具体注册调用代码,属于上下文相关步骤,标注"原文未涉及")。

> 注:原文在 `apply` 返回值解释段落末尾被截断(以 "The silen" 中断),silenceable failure 的完整语义未给出,以上解读仅基于文档当前可读内容,未做补充。
