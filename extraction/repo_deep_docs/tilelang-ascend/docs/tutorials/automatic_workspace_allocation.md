# Tilelang-Ascend Workspace Auto-Allocation Feature

> 仓 `tilelang-ascend` · 路径 `docs/tutorials/automatic_workspace_allocation.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/tilelang-ascend/docs/tutorials/automatic_workspace_allocation.md

# Tilelang-Ascend 自动 Workspace 分配功能深度解读

## 【定位】
这篇文档介绍了 tilelang-ascend 框架的 **Workspace 自动内存管理能力**，解决算子开发中临时缓冲区需要手工申请/释放、易出错且对用户不透明的问题，使算子作者只需声明 workspace 形参位置和形状，运行时自动完成分配与回收。

## 【技术要点】

1. **两层角色分离**：算子开发者通过装饰器声明 workspace 形参位置；调用方只关心业务输入/输出，对 workspace 完全无感。
2. **装饰器参数 `workspace_idx`**：在 `@tilelang.jit` 装饰器中以列表形式声明若干参数下标为 workspace，**0-based 索引**，且**支持负数从尾部计数**（原文："(0-based indexing, negative values count from the end)"）。
3. **形参仍需显式声明**：函数签名中 workspace 张量的形状与 dtype 必须显式写出，框架据此自动分配内存（原文："workspace parameters and their types should be declared in the function definition. The framework handles the memory allocation based on your declared shapes automatically"）。
4. **与 `out_idx` 并列**：输出由 `out_idx` 独立标注（示例中 `out_idx=[3]` 表示第 4 个形参为输出），workspace 由 `workspace_idx` 独立标注，两者互不干扰。
5. **后端受限**：该特性当前**仅在 Cython Backend 下完全支持**，`ctypes` 等其他后端尚未支持（原文："Currently, the workspace auto-management feature is only available in the following execution backend: **Cython Backend**: Fully supported"）。
6. **示例算子**：以 `sparse_attention_fwd` 为示范算子，使用了 **5 个** workspace 张量（原文示例 `workspace_1` ~ `workspace_5`，下标 4–8）。

## 【关键机制与数据】

### 工作原理（数据流）—— 原文梳理

1. **算子开发阶段**：作者在 `@tilelang.jit` 中写 `workspace_idx=[4, 5, 6, 7]`（或更广区间，例如示例中实际声明了 5 个 workspace，对应下标 4–8），并在 `T.prim_func` 的形参列表里把对应下标位置的形参声明为 `T.Tensor(shape, dtype)`，注明其形状与 dtype，但**无需为其手动分配存储**。
2. **调用阶段**：用户调用 `sparse_attention_op(q, kv, indices)`，**只需传入业务输入**张量，不需要传入 workspace；运行时（runtime）会根据开发者声明的形状与 dtype 自动申请连续的 workspace 缓冲，在算子执行结束后自动释放。
3. **可观测性**：输出张量由 `out_idx` 标记自动返回；workspace 张量对调用方**完全透明**（原文："Workspace is completely transparent to users"）。

### 性能/开销数据
**原文未涉及** 任何性能数字、内存开销统计、加速比或基准测试结果。

## 【表格解读】

**原文无表格**。原文仅给出代码示例（Python 装饰器与 `T.prim_func` 函数签名），未提供诸如 "参数对照表 / 后端支持矩阵 / 性能对比表" 之类的结构化表格。

如需还原核心声明示例，可视为下表（仅复述原文示例，非原文表格）：

| 项目 | 装饰器声明 | 形参位置（0-based） | 形状（原文示例） | dtype（原文示例） | 角色 |
|---|---|---|---|---|---|
| Q | — | 0 | `q_shape` | `dtype` | 输入 |
| KV | — | 1 | `kv_shape` | `dtype` | 输入 |
| Indices | — | 2 | `indices_shape` | `indices_dtype` | 输入 |
| Output | `out_idx=[3]` | 3 | `o_shape` | `dtype` | 自动输出 |
| workspace_1 | `workspace_idx=[4,…,8]` | 4 | `[block_num, BI, D]` | `dtype` | 自动 workspace |
| workspace_2 | 同上 | 5 | `[block_num, BI, D_tail]` | `dtype` | 自动 workspace |
| workspace_3 | 同上 | 6 | `[block_num, H_per_block, BI]` | `accum_dtype` | 自动 workspace |
| workspace_4 | 同上 | 7 | `[block_num, H_per_block, BI]` | `dtype` | 自动 workspace |
| workspace_5 | 同上 | 8 | `[block_num, H_per_block, D]` | `accum_dtype` | 自动 workspace |

> 注：上表仅基于原文代码示例复述，原文本身**并未以表格形式呈现**。

## 【公式解读】

**原文无公式**。全文未出现任何 LaTeX 或伪代码形式的公式。

## 【关联】

原文**未提供任何内部链接**（内部链接字段在题目中标注为"(无)"），也未交叉引用仓库中的其他特性/模块/文件。仅在文中暗示其与以下概念同处 tilelang-ascend 体系：
- `@tilelang.jit` 装饰器及其已有的 `out_idx` 参数（与 `workspace_idx` 并列设计）；
- 算子开发范式 `T.prim_func` 与 `T.Tensor` 类型标注；
- 执行后端矩阵（本特性绑定 Cython Backend，并明确排除 `ctypes` 等）。

## 【使用方法】

原文明确给出的启用方式与配置项如下：

1. **装饰器声明（开发者侧）**
   ```python
   @tilelang.jit(out_idx=[3], workspace_idx=[4, 5, 6, 7])
   def sparse_attention_fwd(...):
       @T.prim_func
       def main(..., workspace_1: T.Tensor([block_num, BI, D], dtype), ...):
           ...
   ```
2. **`out_idx`**：标注输出形参在函数签名中的位置下标（0-based，可负数）。
3. **`workspace_idx`**：以列表标注一个或多个形参下标为 workspace（0-based，可负数）。
4. **形参声明**：workspace 张量的 `T.Tensor(shape, dtype)` 必须完整写出，作为运行时分配内存的依据（运行时使用 Cython 后端）。
5. **用户调用（用户侧）**
   ```python
   q = ...; kv = ...; indices = ...
   output = sparse_attention_op(q, kv, indices)   # 无需传 workspace
   ```
6. **环境前置条件**：使用前需将执行后端切换为 Cython Backend；其他后端（`ctypes` 等）**当前不被支持**。
