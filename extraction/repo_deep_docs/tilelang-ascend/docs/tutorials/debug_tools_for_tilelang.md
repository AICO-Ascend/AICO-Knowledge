# Debugging Tile Language Programs

> 仓 `tilelang-ascend` · 路径 `docs/tutorials/debug_tools_for_tilelang.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/tilelang-ascend/docs/tutorials/debug_tools_for_tilelang.md

# 《Debugging Tile Language Programs》深度解读

## 【定位】
本文是 TileLang 调试工具指南,聚焦于解决 Tile Language 程序在"生成阶段失败"与"结果不正确"两类问题的诊断方法,提供基于 Python 层 IR 检视与运行时 `T.print` 的两路调试策略。

---

## 【技术要点】

1. **三阶段编译流程**:Tile Language 程序经过①用户编写 → ②多轮 Pass 转换/优化(lower 阶段,见 `tilelang/engine/lower.py`)生成中间表示(LLVM/C/CUDA 等)→ ③对应编译器(如 nvcc)生成可执行文件。
2. **三类问题分类**:①生成问题(lower 过程出错,无法产出可执行文件);②正确性问题(可运行但结果错误);③性能问题(性能显著低于理论上限,本文不展开)。
3. **渐进式 Lower 示例**:`T.copy` 先被展开为 `T.Parallel`(对应 Pass 为 `LowerTileOP`),再继续展开为可翻译为 CUDA C 的低级语句。
4. **IR 打印定位生成错误**:C++ 层在 `src/target/codegen_cuda.cc` 第 1257 行抛出 `ValueError: Check failed: lanes <= 4 (8 vs. 4) : Ramp of more than 4 lanes is not allowed.`——提示出现了不被支持的 8-lane 向量化 ramp,建议在 codegen 前用 `tir.transform.Filter(is_device_call)` 过滤并打印 IR。
5. **后处理回调机制**:在 `src/target/rt_mod_cuda.cc` 中,codegen 后通过 `Registry::Get("tilelang_callback_cuda_postproc")` 调用已注册的回调函数,允许用户拦截并修改最终 CUDA 源码。
6. **`T.print` 运行时调试原语**:内置 5 类用法——打印整 buffer、条件打印、打印 thread index/标量、打印 fragment(寄存器文件)、添加消息前缀;输出形如 `msg='hello world' BlockIdx=(0, 0, 0), ThreadIdx=(0, 0, 0): 0`。

---

## 【关键机制与数据】

- **工作机制(原文)**:"TileLang essentially performs *progressive lowering*"——逐层将高层 Tile OP 降级为底层语句,任何 Pass 阶段都可能引入新的向量化或访存模式,这是生成阶段错误的根源。
- **IR 检视流程(原文)**:当 lowering 报错时,不直接进入 C++ Pass 调试,而是先在 Python 中通过 `tir.transform.Filter(is_device_call)(mod)` 打印最终 IR,定位错误 IR 节点后再回溯 Pass 链。
- **回调注册流程(原文)**:通过 `from tilelang.engine.callback import register_cuda_postproc_callback` 注册名为 `tilelang_callback_cuda_postproc` 的 Python 函数,该函数签名接收 `(code, target)`,返回修改后的 CUDA 源码字符串。
- **GEMM 示例参数(原文)**:`matmul(1024, 1024, 1024, 128, 128, 32)`,对应 M=N=K=1024,block_M=block_N=128,block_K=32,dtype="float16",accum_dtype="float"。
- **`T.print` 输出格式(原文)**:包含自定义 msg 前缀、BlockIdx 三元组、ThreadIdx 三元组以及具体数值。
- **未来方向(原文)**:性能调优依赖 Nsight Compute、rocProf 等厂商工具,本文不涉及。

---

## 【表格解读】

**原文无表格。** 文中未出现任何参数表、性能对比表或配置项表格。

---

## 【公式解读】

**原文无公式。** 文中未出现 LaTeX 数学公式或伪代码形式的算式表达(代码示例不属于公式范畴)。

---

## 【关联】

- **上下游模块**:
  - 上游:用户编写的 Tile Language 程序(`@T.prim_func` 装饰器与 `T.copy`、`T.Parallel`、`T.print` 等原语)。
  - 中游:Pass 系统(`LowerTileOP` 等)与 IR 表示(由 `tir.transform.Filter(is_device_call)` 提取)。
  - 下游:`src/target/codegen_cuda.cc`(代码生成,可能抛错)与 `src/target/rt_mod_cuda.cc`(注册回调入口,调用 `tilelang_callback_cuda_postproc`)。
- **关联调试手段**:`tilelang/engine/lower.py` 是 lower 阶段的入口,与本文"先打印 IR 再排查 C++"的策略紧密相关;`tilelang.engine.callback` 模块提供 `register_cuda_postproc_callback` 接口,实现 Python 层的源码拦截。
- **未来扩展(原文)**:性能调优章节(Nsight Compute、rocProf 等)被作者标记为"will be addressed in future materials"。
- **内部链接**:文末标注 `(无)`,本文未提供其他文档交叉链接。

---

## 【使用方法】

- **启用 IR 打印定位生成问题(原文)**:
  ```python
  device_mod = tir.transform.Filter(is_device_call)(mod)
  ```
- **注册 CUDA 后处理回调(原文)**:
  ```python
  from tilelang.engine.callback import register_cuda_postproc_callback

  @register_cuda_postproc_callback
  def tilelang_callback_cuda_postproc(code, _):
      print(code)
      code = "// modified by tilelang_callback_cuda_postproc\n" + code
      return code

  kernel = tilelang.compile(matmul, target="cuda")
  kernel_source = kernel.get_kernel_source()
  print(kernel_source)
  ```
- **编译入口(原文)**:`tilelang.compile(matmul, target="cuda")` 返回带 `.get_kernel_source()` 方法的 kernel 对象。
- **运行时调试原语(原文)**:在 kernel 内调用 `T.print(...)`,提供 5 类模板:打印 buffer、条件打印、打印 thread index/标量、打印 fragment、添加 msg 前缀;**注意 GPU 并发与线程同步**。
- **GEMM 调用模板(原文)**:
  ```python
  func = matmul(1024, 1024, 1024, 128, 128, 32)
  ```
  参数顺序为 `(M, N, K, block_M, block_N, block_K)`,默认 `dtype="float16"`、`accum_dtype="float"`。
- **性能调优工具(原文)**:Nsight Compute、rocProf 及厂商特定 profiler——本文未给出具体配置命令,标记为未来材料。
