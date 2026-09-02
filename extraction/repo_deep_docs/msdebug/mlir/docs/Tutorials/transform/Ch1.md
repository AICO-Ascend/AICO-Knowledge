# Chapter 1: Combining Existing Transformations

> 仓 `msdebug` · 路径 `mlir/docs/Tutorials/transform/Ch1.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msdebug/mlir/docs/Tutorials/transform/Ch1.md

# 深度解读: MLIR Transform Dialect — Chapter 1: Combining Existing Transformations

## 【定位】

这篇文档是 MLIR Transform dialect 教程的第一章,解决"如何将已有变换组合成可精确靶向、可链式执行、可被独立解释器驱动"的变换序列问题——即用 Transform IR 自身作为"变换语言"来描述对 payload IR(如 linalg.matmul)的串行改造流程。

## 【技术要点】

1. **IR 二元划分**: Transform IR(承载变换操作)与 payload IR(被变换的 IR)分离;变换操作的值通过 handle(操作/值)或 parameter(属性)与 payload 实体关联。

2. **顶层入口约定**: 使用 `transform.named_sequence @__transform_main`,类比 C 语言 `main` 入口;第一个参数(`!transform.any_op`)绑定到 pass 应用对象的顶层 payload 操作,且**仅在使用 interpreter pass 时强制要求**,通过 `applyTransforms` 或 `applyNamedSequence` 程序化调用时无此要求。

3. **Handle 类型约束**: 顶层序列的后续入口参数可选,用于关联特定 payload 实体,如 `!transform.op<"linalg.matmul">` 仅接受 `linalg.matmul` 类型操作、`!transform.op<"linalg.elemwise_binary">` 仅接受 elemwise_binary 操作;约束在 `applyTransforms` 早期创建关联时被验证,失败会产出诊断信息。

4. **模块级触发属性**: 整个 sequence 必须包裹在带 `transform.with_named_sequence` 属性的 module 中,以便在存在多个 named sequence 时触发必要的验证。

5. **失败传播双模式**: 通过未命名 `transform.sequence` 的强制属性 `failures(...)` 指定:
   - **propagate**: 任一嵌套变换失败 → 整个序列失败;
   - **suppress**: 失败被吞掉,序列成功,**但不执行后续变换**——允许外层脚本在内部错误"可恢复"时继续。

6. **调试机制**: `transform.debug.emit_remark_at <handle>, "label" : <handle_type>` 能在 handle 关联的 payload 操作位置打印带定位的 remark 及对应操作内容,用于检查序列与关联是否正确。

7. **解释器免编译路径**: 使用 `transform-interpreter` pass,无需重编译编译器即可应用 transform sequence;通过 `debug-bind-trailing-args=linalg.matmul,linalg.elemwise_binary` 将额外顶层参数分别绑定到所有 `linalg.matmul` 与 `linalg.elemwise_binary` payload 操作上。

## 【关键机制与数据】

**工作原理(原文):** "The Transform dialect allows one to precisely target transformations at specific operations in the IR and to chain them, that is to apply a transformation to operations produced by the previous transformation."

**数据流(原文):** 同一个 `sequence.mlir` 文件**同时**包含 payload IR `func.func @fc_relu` 和嵌套的 transform IR `module`;interpreter pass 对该 module 内的 `@__transform_main` named sequence 进行解释,把它应用到 pass 的 anchor operation 上,并通过 `debug-bind-trailing-args` 把额外参数绑定到对应类型的 payload 操作集合上,关键结果:

```text
sequence.mlir:7:13:  remark: matmul
sequence.mlir:10:13: remark: elemwise_binaries
sequence.mlir:14:13: remark: elemwise_binaries
```

**关键事实(原文):** "%arg2 is associated with both elementwise payload operations. Any handle is associated with a list of entities."——单个 handle 可同时关联多个 payload 操作(即原 `func` 中行 10 的 add 与行 14 的 max_signed 两个 `linalg.elemwise_binary` 共用 `%arg2`)。

**示例算子规模(原文):** 示例 `fc_relu` 使用 `tensor<512x512xf32>`,即 512×512 浮点张量上的矩阵乘法 + 元素级加法 + 元素级 max(0)——即典型的"全连接 + bias + ReLU"。

## 【表格解读】

**原文无表格。**

## 【公式解读】

**原文无公式。**

## 【关联】

- **C++ 编程接口**: 文档以 C++ API 中的 `applyTransforms` 函数作为变换应用的入口,并指出通过它或 `applyNamedSequence` 程序化调用时可绕过 `@__transform_main` 的命名约束(`!transform.any_op` 第一个参数、`__transform_main` 名称均非必需)。
- **上下游文档**: 本章显式提及"in the next chapter, it is possible to define custom passes or even integrate the transform interpreter into a larger pass"——下一章将展开自定义 pass 与将 interpreter 嵌入更大 pipeline。
- **被变换对象**: Linalg dialect 的 `linalg.matmul`(矩阵乘)与 `linalg.elemwise_binary`(带 `fun = #linalg.binary_fn<add>` 与 `#linalg.binary_fn<max_signed>` 的两种元素级二元操作)。
- **arith dialect 依赖**: ReLU 路径中通过 `arith.constant 0.0 : f32` 生成零常量作为第二个操作的输入。
- **调试操作族**: `transform.debug.emit_remark_at` 属于 `transform.debug` 操作族,用于诊断 handle 关联。
- **变换应用机制**: `transform.interpreter` pass 与 MLIR 的 `builtin.module` pass-pipeline 机制(`--pass-pipeline="builtin.module(transform-interpreter{...})"`)集成。

## 【使用方法】

**(原文涉及的)配置项与命令:**

- **模块属性**: `transform.with_named_sequence`,添加到包裹 named sequence 的 `module` 上以触发验证。
- **顶层序列固定名**: `transform.named_sequence @__transform_main`,作为 interpreter pass 的入口。
- **入口参数类型**:
  - `!transform.any_op` —— 任意 payload 操作;
  - `!transform.op<"linalg.matmul">`、`!transform.op<"linalg.elemwise_binary">` —— 受限到具体操作种类。
- **失败传播属性**: `transform.sequence failures(propagate)` 或 `transform.sequence failures(suppress)`;教程示例明确选择 `propagate`,以便在脚本构建期暴露未应用的变换。
- **调试操作**: `transform.debug.emit_remark_at %handle, "label" : !transform.op<"X">` 在指定 handle 的 payload 操作位置输出 remark,并附 "see current operation: <op>" 注解。
- **执行命令**(原文示例,完整保留):
  ```sh
  $ mlir-opt sequence.mlir --pass-pipeline="
      builtin.module(transform-interpreter{
          debug-bind-trailing-args=linalg.matmul,linalg.elemwise_binary})"
  ```
  其中 `debug-bind-trailing-args=linalg.matmul,linalg.elemwise_binary` 用于把额外顶层参数分别绑定到所有 `linalg.matmul` 和 `linalg.elemwise_binary` payload 操作。
- **C++ API 入口函数**: `applyTransforms`(顶层操作传入该函数);文档未给出函数签名细节。

> 备注: 原文末尾以 `// The actual tiling transformation takes tile sizes as attribute` 注释截断,tiling 与融合的具体写法属后续章节内容,**原文未涉及**。
