# Chapter 3: More than Simple Transform Operations

> 仓 `msdebug` · 路径 `mlir/docs/Tutorials/transform/Ch3.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msdebug/mlir/docs/Tutorials/transform/Ch3.md

# 深度解读: MLIR Transform Dialect 教程 Chapter 3

## 【定位】

本篇文档是 MLIR Transform Dialect 教程系列第 3 章,解决**"如何在 Transform Dialect 扩展中超越简单操作定义、引入更精细的类型约束、可复用的 ApplyEach 骨架以及自定义 Transform 类型"**的问题,并演示**操作数消费(operand consumption)**这一生成新 payload 句柄的高级模式。

---

## 【技术要点】

1. **用 Transform_ConcreteOp 类型缩窄操作数类型约束**
   - 将原本宽泛的 `TransformHandleTypeInterface` 替换为 `Transform_ConcreteOpType<"func.call">`,把"任何 op 句柄"收紧为"必须是 `func.call` 的句柄"。
   - 通过 `transform.cast` 在 IR 层面把 `!transform.any_op` 转换为更具体的类型。

2. **用 TransformEachOpTrait 复用 apply 实现骨架**
   - Op 定义中标注 `[TransformOpInterface, TransformEachOpTrait, DeclareOpInterfaceMethods<MemoryEffectsOpInterface>]`。
   - 骨架自动完成: verification、遍历 payload、把每个 `applyToOne` 的结果拼接成结果列表;用户只需提供对**单个** payload 操作生效的 `applyToOne` 方法。
   - `applyToOne` 签名固定为 `applyToOne(TransformRewriter&, CallOp/CallOpInterface, ApplyToEachResultList&, TransformState&)`。

3. **在扩展中自定义 Transform 类型**
   - 用 `TypeDef<Transform_Dialect, "CallOpInterfaceHandle", [DeclareTypeInterfaceMethods<TransformHandleTypeInterface>]` 定义。
   - mnemonic 为 `"my.call_op_interface"`,assembly format 留空(`""`)。
   - 必须实现 `checkPayload(loc, payload)` 三态校验方法,对不实现 `CallOpInterface` 的 payload 用 `emitSilenceableError` 并 `attachNote` 标注 offending operation。
   - 在扩展 `init()` 中通过 `registerTypes<...>` 配合 `GET_TYPEDEF_LIST` 宏注册。

4. **consume-then-produce 模式(操作数消费)**
   - 新 op `CallToOp` 的 `arguments` 是 `CallOpInterfaceHandle:$call`,`results` 是 `TransformHandleTypeInterface:$transformed`——输入句柄被消费,产出新句柄。
   - `applyToOne` 中调用 `rewriteToOp(call)` 得到新 op;若返回 null,因为 IR 已被不可逆修改,使用 `emitDefiniteError()` 产生 **definite failure**(而非 silenceable failure)。

5. **失败语义区分**
   - 校验类失败(precondition)→ `DiagnosedSilenceableFailure` + `emitSilenceableError`。
   - 重写后部分失败、IR 已破坏 → `DefiniteFailure` + `emitDefiniteError`。
   - 全部成功 → `DiagnosedSilenceableFailure::success()`。

6. **参数与格式约定**
   - `assemblyFormat` 示例 1: `"$call `,` $new_target attr-dict `:` type($call)"`(仅输入句柄时使用 `type(...)`)。
   - `assemblyFormat` 示例 2: `"$call attr-dict `:` functional-type(inputs, outputs)"`(有输入输出句柄时使用 functional-type 语法)。
   - 新 op 命名遵循 `<dialect_ext_name>.<op_name>` 前缀,完整名再被 `transform.` 前缀。

---

## 【关键机制与数据】

**工作原理 / 数据流(按原文梳理):**

1. **约束收紧流程** — 原文:操作定义 `ChangeCallTargetOp` 的 argument 列表中 `Transform_ConcreteOpType<"func.call">:$call` 把句柄类型由"任意 op"缩窄到 `func.call`;验证阶段 trait 会自动确保关联的 payload op 满足此约束。

2. **ApplyEach trait 的循环抽象** — 原文:`TransformEachOpTrait` 提供 `apply` 方法的骨架实现,自动完成 verification、迭代 payload、结果拼接;用户代码只描述"对一个 payload 操作做什么"。原文中 `applyToOne` 函数体仅两行有效代码:`updateCallee(call, getNewTarget());` 与 `return DiagnosedSilenceableFailure::success();`。

3. **自定义类型的 checkPayload 三态校验** — 原文:`checkPayload(loc, payload)` 遍历 `payload`,逐个用 `llvm::isa<mlir::CallOpInterface>(op)` 检查;任一不满足则 `emitSilenceableError(loc) << "expected the payload operation to implement CallOpInterface"`,并 `diag.attachNote(op->getLoc()) << "offending operation"`;全部满足返回 `DiagnosedSilenceableFailure::success()`。

4. **注册流程** — 原文:扩展的 `init()` 中通过 `registerTypes<...>` + `GET_TYPEDEF_LIST` + `#include "MyExtensionTypes.cpp.inc"` 把生成出来的 TypeDef 列表注入 Transform dialect。

5. **Cast 与新类型在 IR 层的可用性** — 原文:`transform.cast %call : !transform.any_op to !transform.my.call_op_interface` 把宽句柄收窄为新句柄;紧接着 `transform.my.change_call_target %casted, "microkernel" : !transform.my.call_op_interface` 使用之。

6. **consume-then-produce 的失败语义** — 原文:`CallToOp::applyToOne` 调用 `rewriteToOp(call)`,若返回 `nullptr` 则 `emitDefiniteError() << "failed to rewrite`(原文此处被截断),因为 IR 已不可逆修改所以是 definite failure。

**性能数据:原文未涉及。**

---

## 【表格解读】

原文无表格。文档中的内容均为 Tablegen 定义、C++ 实现代码、MLIR IR 片段(以 fenced code block 形式给出),不构成参数表/性能对比表/配置项表格。

---

## 【公式解读】

原文无公式。文档未出现 LaTeX 数学公式或伪代码公式;相关类型与约束均以 Tablegen DSL(`Transform_ConcreteOpType<"func.call">`、`StrAttr`、`TypeDef<Transform_Dialect, "CallOpInterfaceHandle", [...]>` 等)和 MLIR 类型字符串(`!transform.any_op`、`!transform.my.call_op_interface`)表达。

---

## 【关联】

文末提供的内部链接为"(无)"。文档内部存在的隐式上下游关系如下(全部基于原文描述):

- **与前两章(Chapter 1/2)的关系** — 原文描述"如上所述"(As we have seen above),表明 Chapter 3 建立在前面章节已介绍的"基础 transform op 定义"和"`apply` 循环实现"之上;Chapter 3 是用更高级的工具(`TransformEachOpTrait`、自定义 Transform 类型)替代前一章手写的循环与宽泛句柄类型。
- **与 Transform Dialect 主体的关系** — 新 op、新类型都是 Transform dialect 的**扩展(extension)**,通过 `Transform_Dialect` 在 ODS 层注入;`registerTypes<>` 与 `init()` 表明它们走扩展注册路径。
- **与 Func Dialect 的关系** — `func.call`、`func::CallOp`、`CallOpInterface` 都来自 Func dialect;扩展引入的 `CallOpInterfaceHandle` 是把 Func dialect 的接口抽象接入 Transform dialect 的类型系统。
- **与 `TransformOpInterface` / `MemoryEffectsOpInterface` 的关系** — 每个新 op 仍需同时实现这两个接口;`TransformEachOpTrait` 只是替用户实现了 `TransformOpInterface` 要求的 `apply` 方法骨架,`MemoryEffectsOpInterface` 的方法(`getEffects`)仍由 `DeclareOpInterfaceMethods` 要求用户实现(本教程未展开)。
- **与 `transform.cast` 内建操作的关系** — `CallOpInterfaceHandle` 类型必须经过 `transform.cast` 才能把宽句柄收窄到自定义句柄,这是文档给出的唯一使用入口。
- **与 `DiagnosedSilenceableFailure` / `DefiniteFailure` 的关系** — 校验路径走 silenceable 失败(可被上层捕获并继续),重写已修改 IR 后的失败走 definite 失败(必须中止 transform pipeline)。

---

## 【使用方法】

**启用方式 / 配置项 / 命令(原文给出的可执行项):**

1. **ODS 中定义新 op** —— 在 `MyExtension.td` 中,以 `def XxxOp : Op<Transform_Dialect, "my.xxx", [TransformOpInterface, TransformEachOpTrait, DeclareOpInterfaceMethods<MemoryEffectsOpInterface>]> { ... }` 形式声明,并按需填 `summary` / `description` / `arguments` / `results` / `assemblyFormat` / `extraClassDeclaration`。

2. **C++ 中实现 `applyToOne`** —— 文件 `MyExtension.cpp`,函数签名为
   ```c++
   ::mlir::DiagnosedSilenceableFailure XxxOp::applyToOne(
       ::mlir::transform::TransformRewriter &rewriter,
       /* payload op type */ call,
       ::mlir::transform::ApplyToEachResultList &results,
       ::mlir::transform::TransformState &state);
   ```
   内部对单个 payload 做变换,返回 `DiagnosedSilenceableFailure::success()`。

3. **ODS 中定义新 Transform 类型** —— `def XxxHandle : TypeDef<Transform_Dialect, "XxxHandle", [DeclareTypeInterfaceMethods<TransformHandleTypeInterface>]> { let mnemonic = "my.xxx"; let assemblyFormat = ""; }`。

4. **C++ 中实现 `checkPayload`** —— 在 `MyExtension.cpp` 实现
   ```c++
   mlir::DiagnosedSilenceableFailure
   mlir::transform::XxxHandleType::checkPayload(
       mlir::Location loc,
       llvm::ArrayRef<mlir::Operation *> payload) const;
   ```
   对不满足约束者 `emitSilenceableError` + `attachNote`,全部满足返回 `success()`。

5. **在扩展 `init()` 中注册类型** —— 原文:
   ```c++
   void MyExtension::init() {
     // ...
     registerTypes<
   #define GET_TYPEDEF_LIST
   #include "MyExtensionTypes.cpp.inc"
     >();
   }
   ```

6. **IR 中使用新句柄类型** —— 通过 `transform.cast` 收窄后,再使用自定义 op:
   ```mlir
   %casted = transform.cast %call : !transform.any_op to !transform.my.call_op_interface
   transform.my.change_call_target %casted, "microkernel" : !transform.my.call_op_interface
   ```

7. **consume-then-produce 的 IR 用法** —— `CallToOp` 的 assemblyFormat 使用 functional-type:
   ```mlir
   transform.my.call_to_op %call : !transform.my.call_op_interface -> !transform.op<"func.func">
   ```
   (原文给出的是 format 模式 `"$call attr-dict `:` functional-type(inputs, outputs)"`,具体 IR 形态原文未给出示例,本条为基于原文格式串的合理示意。)

**注意**:原文末尾的 `CallToOp::applyToOne` 实现被截断(`return emitDefiniteError() << "failed to rewrite` 之后内容缺失),所以关于"definite failure 失败消息的完整措辞以及后续如何处理新生成句柄"原文未涉及。
