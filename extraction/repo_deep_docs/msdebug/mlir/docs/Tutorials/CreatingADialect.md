# Creating a Dialect

> 仓 `msdebug` · 路径 `mlir/docs/Tutorials/CreatingADialect.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msdebug/mlir/docs/Tutorials/CreatingADialect.md

# 一体化深度解读:Creating a Dialect

## 【定位】
本文档解决"如何在 MLIR 项目中规范地创建、构建一个公开方言(Dialect)及其转换库"的工程化问题,描述了从目录结构、TableGen 声明、CMake 库目标到跨方言转换(Dialect Conversion)的完整脚手架规范与最佳实践。

## 【技术要点】

1. **目录分层约定**:公开方言至少分 3 个目录——`mlir/include/mlir/Dialect/Foo`(公共头)、`mlir/lib/Dialect/Foo/IR`(操作实现)、`mlir/lib/Dialect/Foo/Transforms`(变换规则),加上源码目录 `mlir/lib/Dialect/Foo` 与 `mlir/test/Dialect/Foo`(测试)。

2. **ODS + TableGen 自动生成**:include 目录中的 `FooOps.td` 以 ODS 格式描述操作,可生成 4 类产物——`FooOps.h.inc`(操作声明)、`FooOps.cpp.inc`(操作定义)、`FooOpsInterfaces.h.inc`(接口声明)、`FooOpsInterfaces.cpp.inc`(接口定义)。`FooDialect.cpp` 中通过 `#include "FooOps.cpp.inc"` 与 `#include "FooOpsInterfaces.h.inc"` 接入这些生成代码。

3. **两个核心 TableGen CMake 宏**:
   - `add_mlir_dialect(FooOps foo)` 用于声明 dialect 核心,并配合 `add_mlir_dialect_library` 产生 `MLIRFooOpsIncGen` 依赖目标;
   - 对变换使用 `set(LLVM_TARGET_DEFINITIONS FooTransforms.td)` + `mlir_tablegen(FooTransforms.h.inc -gen-rewriters)` + `add_public_tablegen_target(MLIRFooTransformsIncGen)`。

4. **方言库构建宏 `add_mlir_dialect_library()`**:它是 `add_llvm_library()` 的薄包装,把全部 dialect 库收集到一个全局列表。该列表被链入 `libMLIR.so`,并供 `mlir-opt` 这类工具链接所有方言。可通过 `get_property(dialect_libs GLOBAL PROPERTY MLIR_DIALECT_LIBS)` 取出。链接描述符有强制分工——LLVM 库用 `LINK_COMPONENTS`(如 `Core`),MLIR 库用 `LINK_LIBS PUBLIC`(如 `MLIRBar`)。

5. **命名规范**:dialect 名字通常**不以 "Ops" 结尾**,但仅与该 dialect 操作相关的文件(如 `FooOps.cpp`)可以。

6. **跨方言转换的三处布局**:`mlir/include/mlir/Conversion/XToY`、`mlir/lib/Conversion/XToY`、`mlir/test/Conversion/XToY`。默认文件名省略 "Convert",如 `lib/VectorToLLVM/VectorToLLVM.cpp`。Pass 头独立放 `include/mlir/VectorToLLVM/VectorToLLVMPass.h`。跨方言公共代码可放 `mlir/lib/Conversion/XCommon`(如 `GPUCommon`)。

7. **转换库宏 `add_mlir_conversion_library()`**:同样是 `add_llvm_library()` 的薄包装,把全部转换库收集进全局属性 `MLIR_CONVERSION_LIBS`,同样链入 `libMLIR.so`。只需对源/目标 dialect 设 `LINK_LIBS PUBLIC` 依赖,不需显式依赖其 `IncGen` 目标。

## 【关键机制与数据】

- **机制(TableGen 增量构建链)**:ODS `.td` 文件 → `mlir-tblgen` → 生成 4 个 `.inc` 文件 → 由 `add_mlir_dialect_library(DEPENDS MLIRFooOpsIncGen MLIRFooTransformsIncGen)` 表达构建期依赖 → 编译器把 `.inc` 视为源代码纳入 dialect 库。

- **机制(全局属性聚合)**:每一次调用 `add_mlir_dialect_library` / `add_mlir_conversion_library`,都会把当前库名追加到全局 property(分别为 `MLIR_DIALECT_LIBS`、`MLIR_CONVERSION_LIBS`)。下游消费者(如 `mlir-opt`、`libMLIR.so`)据此一次性拿到"全部方言/全部转换",避免手工维护列表。

- **机制(依赖最小化原则)**:**原文:**"it is not necessary to explicitly depend on the corresponding IncGen targets. The PUBLIC link dependency is sufficient."——即 PUBLIC 链接依赖本身即可传递表头依赖,不需额外 `add_dependencies`。

- **数据/特殊场景(原文)**:"dialects that depend on LLVM IR may need to depend on the LLVM 'intrinsics_gen' target to ensure that tablegen'd LLVM header files have been generated."——直接包含 LLVM IR 头的方言/转换需显式依赖 `intrinsics_gen` 目标。

- **机制(共享库兼容)**:**原文:**"This allows cmake infrastructure to generate new library targets with correct linkage, in particular, when `BUILD_SHARED_LIBS=on` or `LLVM_LINK_LLVM_DYLIB=on` are specified."——`LINK_COMPONENTS`/`LINK_LIBS` 的分离描述,是为了在两种共享库构建模式下仍能正确处理链接。

- **机制(避免显式 `add_dependencies`)**:**原文:**"we avoid using add_dependencies explicitly, since the dependencies need to be available to the underlying add_llvm_library() call, allowing it to correctly create new targets with the same sources."——直接依赖会绕开 `add_llvm_library` 的源复用逻辑。

## 【表格解读】
**原文无表格。**(文中仅有代码块形式的 CMake 片段与目录布局文字列表。)

## 【公式解读】
**原文无公式。**(文档为工程规范说明,未包含任何数学或伪代码公式。)

## 【关联】

- **../DefiningDialects/Operations.md(ODS 格式)**:本文核心依赖项。`FooOps.td` 即按 ODS 语法编写,该链接定义了操作/接口的声明语法及生成规则——决定了 `.h.inc` / `.cpp.inc` 产物长什么样。文中两处引用:① include 目录放 ODS TableGen 文件用于生成 `FooOps.h.inc`、`FooOps.cpp.inc`;② 通过 `add_mlir_dialect(FooOps foo)` 触发 ODS 编译流水线。

- **../DeclarativeRewrites.md(DDR 格式)**:本文中提及 Transform 目录下的 TableGen 文件"以 DDR 格式描述变换规则"。也就是说,`FooTransforms.td` 的具体语法(`-gen-rewriters` 生成的 `FooTransforms.h.inc`)由 DDR 文档规范。

- **上下游模块**:
  - 上游:**LLVM CMake**(`add_llvm_library`、`LLVM_TARGET_DEFINITIONS`、`add_public_tablegen_target`、全局属性机制)是 MLIR 这两个包装宏的底层。
  - 下游消费者:`mlir-opt`、共享库 `libMLIR.so` 通过 `MLIR_DIALECT_LIBS` / `MLIR_CONVERSION_LIBS` 一次性链接所有方言与转换。
  - 同级依赖:示例中的 `MLIRBar`(被 `MLIRFoo` PUBLIC 链接),以及转换示例中的 `MLIRFunc`(被 `MLIRBarToFoo` 链接)展示了方言之间的解耦/组合方式。
  - 旁支:依赖 LLVM IR 的方言/转换需穿透到 LLVM 的 `intrinsics_gen` 目标——桥接到 LLVM 本体。

## 【使用方法】

1. **创建方言的目录骨架**(原文):为名为 `Foo` 的方言建立至少 5 个目录——`mlir/include/mlir/Dialect/Foo`、`mlir/lib/Dialect/Foo`、`mlir/lib/Dialect/Foo/IR`、`mlir/lib/Dialect/Foo/Transforms`、`mlir/test/Dialect/Foo`。

2. **声明 ODS 文件**:在 include 目录下放 `FooOps.td`(ODS 格式),在 `IR` 目录下放 `FooDialect.cpp`,后者 `#include` 生成的 `FooOps.cpp.inc` 与 `FooOpsInterfaces.h.inc`。

3. **注册 TableGen 目标**(原文 CMake):
   ```cmake
   add_mlir_dialect(FooOps foo)
   add_mlir_doc(FooOps FooDialect Dialects/ -gen-dialect-doc)
   ```
   第一个声明 dialect 核心并生成 `MLIRFooOpsIncGen`;第二个为该 dialect 生成文档。

4. **声明变换 TableGen**(原文 CMake):
   ```cmake
   set(LLVM_TARGET_DEFINITIONS FooTransforms.td)
   mlir_tablegen(FooTransforms.h.inc -gen-rewriters)
   add_public_tablegen_target(MLIRFooTransformsIncGen)
   ```

5. **构建方言库**(原文 CMake):
   ```cmake
   add_mlir_dialect_library(MLIRFoo
           DEPENDS MLIRFooOpsIncGen MLIRFooTransformsIncGen
           LINK_COMPONENTS Core
           LINK_LIBS PUBLIC MLIRBar <some-other-library>)
   ```

6. **读取方言库聚合列表**:`get_property(dialect_libs GLOBAL PROPERTY MLIR_DIALECT_LIBS)`,供 `mlir-opt` 等工具使用。

7. **创建跨方言转换**(原文 CMake):建立 `mlir/include/mlir/Conversion/BarToFoo`、`mlir/lib/Conversion/BarToFoo`、`mlir/test/Conversion/BarToFoo` 三处目录,默认文件名省 "Convert";Pass 头放 `include/mlir/BarToFoo/BarToFooPass.h`,通用代码可放 `mlir/lib/Conversion/BarCommon`。CMake 写法:
   ```cmake
   add_mlir_conversion_library(MLIRBarToFoo
           BarToFoo.cpp
           ADDITIONAL_HEADER_DIRS ${MLIR_MAIN_INCLUDE_DIR}/mlir/Conversion/BarToFoo
           LINK_LIBS PUBLIC MLIRBar MLIRFoo)
   ```
   列表读取:`get_property(dialect_libs GLOBAL PROPERTY MLIR_CONVERSION_LIBS)`。

8. **配置项/兼容开关**(原文):构建语义受 `BUILD_SHARED_LIBS=on` 与 `LLVM_LINK_LLVM_DYLIB=on` 影响——本文约定的 `LINK_COMPONENTS`/`LINK_LIBS PUBLIC` 分工正是为这两种构建模式下的链接正确性而设计。原文未给出其他配置项的具体取值。
