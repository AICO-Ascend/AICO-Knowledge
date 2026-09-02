# Dynamo概述

> 仓 `pytorch` · 路径 `docs/zh/user_guide/torch_compile/core_concepts/dynamo_overview.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/pytorch/docs/zh/user_guide/torch_compile/core_concepts/dynamo_overview.md

# Dynamo 概述 深度解读

## 【定位】
本文档介绍 TorchDynamo（简称 Dynamo）的核心定位与底层工作原理——一个通过挂钩 CPython frame 求值 API、动态修改 Python 字节码、把 PyTorch 操作序列抽取为 FX 图并交给可定制后端编译的 Python 级 JIT 编译器，是 `torch.compile` 加速未修改 PyTorch 程序能力的核心实现机制。

## 【技术要点】

1. **挂钩层与字节码改写**：Dynamo 挂接到 CPython 的 frame 求值 API（[PEP 523](https://peps.python.org/pep-0523/)），在 Python 字节码执行前对其动态修改，并把 PyTorch 操作序列抽取到 FX 图中。

2. **一行式入口**：Dynamo 通过单行装饰器 `torch._dynamo.optimize()` 启用；`torch.compile()` 是其便捷封装，使用形式为 `@torch.compile(backend=my_compiler)`。

3. **支持的后端——TorchInductor**：作为受支持后端之一，将 Dynamo 图转换为：NPU 上对应 [Triton](https://github.com/triton-lang/triton)、CPU 上对应 [C++/OpenMP](https://www.openmp.org/)。

4. **Guard 特化与重捕获机制**：以即时（JIT）方式运行，按动态属性对图进行特化；若 guard 失败，则触发重新捕获并编译新图。

5. **`check_tensor` 检查项**：被 guard 用以检查 `torch.Tensor` 的属性——Python 类、dtype、device、requires_grad、dispatch_key（含 thread-local includes/excludes）、ndim、sizes\*、strides\*。

6. **图断裂与恢复**：通过生成 continuation 函数 `__resume_at_<offset>_<n>` 在字节码偏移点恢复 Python frame 执行，并在首次到达时递归触发 Dynamo 重新捕获；`ORIGINAL BYTECODE` 显示的偏移量 `30` 和 `38` 即是 `toy_example` 中两个图断裂点。

7. **调试与反编译工具链**：环境变量 `TORCH_LOGS="+dynamo,guards,bytecode"` 启用日志；[depyf](https://github.com/youkaichao/depyf) 通过 `import depyf; depyf.install()` 注册反编译 hook；API `torch._dynamo.eval_frame._debug_get_cache_entry_list` 用于检查编译缓存。

## 【关键机制与数据】

**工作原理（原文："Dynamo 挂接到 CPython 的 frame 求值 API... 在 Python 字节码执行前动态修改它。它重写 Python 字节码，将 PyTorch 操作序列提取到 FX 图中，再由可自定义后端编译"）**：

1. **字节码分析与图构建**：Dynamo 通过字节码分析将 PyTorch 操作抽取成 FX 图，形成 `__compiled_fn_0` 这类编译产物，并把 Python 执行与编译后端相结合。

2. **动态特化与 Guard**：完全特化模式允许后端编译器假设计算图完全静态；未启用动态形状模式时，返回动态形状的算子会触发图断裂（原文："完全特化模式允许后端编译器假设计算图完全静态。遗憾的是，大多数后端都要求如此。未启用动态形状模式时，返回动态形状的算子会触发图断裂。"）。

3. **生成产物与闭包**（原文输出节选）：
   - 已编译函数：`__compiled_fn_0`、`__resume_at_30_1`、`__resume_at_38_2`；
   - guard 闭包变量（`guard.__code__.co_freevars`）：`___guarded_code`、`___is_grad_enabled`、`___are_deterministic_algorithms_enabled`、`___is_torch_function_enabled`、`utils_device`、`___check_tensors`、`tensor_check_names`；
   - `guard` 函数的参数 `L` 是结构为 `{'a': value_a, 'b': value_b}` 的 `dict`。

4. **数据流（按文档示例 `toy_example` 顺序）**：
   - 输入：`a, b` 两个 `torch.float32`、`size=[10]`、`stride=[1]` 的 CPU Tensor；
   - 第一段图计算 `x = a / (torch.abs(a) + 1)` 并计算 `b.sum() < 0`；
   - 根据条件选择进入 `__resume_at_30_1`（执行 `b = b * -1`）或 `__resume_at_38_2`，最终做 `x * b`。

5. **性能数据**：原文仅提供索引入口"训练性能看板"链接（https://hud.pytorch.org/benchmark/compilers），文档自身未列任何具体性能数字。

## 【表格解读】

### 表 1：第一个图的 guard 条件（原文逐字还原）

| 序号 | guard 表达式 |
|------|--------------|
| 1 | `hasattr(L['a'], '_dynamo_dynamic_indices') == False` |
| 2 | `hasattr(L['b'], '_dynamo_dynamic_indices') == False` |
| 3 | `utils_device.CURRENT_DEVICE == None` |
| 4 | `___skip_backend_check() or ___current_backend() == ___lookup_backend(140355900538256)` |
| 5 | `check_tensor(L['a'], Tensor, DispatchKeySet(CPU, BackendSelect, ADInplaceOrView, AutogradCPU), torch.float32, device=None, requires_grad=False, size=[10], stride=[1])` |
| 6 | `check_tensor(L['b'], Tensor, DispatchKeySet(CPU, BackendSelect, ADInplaceOrView, AutogradCPU), torch.float32, device=None, requires_grad=False, size=[10], stride=[1])` |

**逐行解读**：
- 第 1–2 行检查输入 Tensor 是否具有 `_dynamo_dynamic_indices` 属性（即标记动态形状），要求为 `False` 即要求静态形状。
- 第 3 行检查当前 device 上下文是否为 `None`（表示无自定义设备切换）。
- 第 4 行确认当前调用栈上的后端是否与 `_lookup_backend(140355900538256)`（编译时缓存的 backend id）匹配；`___skip_backend_check()` 提供了跳过该检查的开关。
- 第 5–6 行检查 `a`、`b` 的张量属性：`Tensor` 类（无子类）、dispatch_key 集合为 `CPU` + BackendSelect + ADInplaceOrView + AutogradCPU、`torch.float32`、device=None、`requires_grad=False`、`size=[10]`、`stride=[1]`。任一不满足则触发重捕获。

### 表 2：FX 图（`__compiled_fn_0 <eval_with_key>.1`）（原文逐字还原）

| opcode | name | target | args | kwargs |
|--------|------|--------|------|--------|
| `placeholder` | `a` | `a` | `()` | `{}` |
| `placeholder` | `b` | `b` | `()` | `{}` |
| `call_function` | `abs_1` | `<built-in method abs of type object at 0x7f9ca082f8a0>` | `(a,)` | `{}` |
| `call_function` | `add` | `<built-in function add>` | `(abs_1, 1)` | `{}` |
| `call_function` | `truediv` | `<built-in function truediv>` | `(a, add)` | `{}` |
| `call_method` | `sum_1` | `sum` | `(b,)` | `{}` |
| `call_function` | `lt` | `<built-in function lt>` | `(sum_1, 0)` | `{}` |
| `output` | `output` | `output` | `((truediv, lt),)` | `{}` |

**逐行解读**：
- 两个 `placeholder` 节点 `a`、`b` 是图输入。
- `abs_1 = abs(a)`、`add = abs_1 + 1`、`truediv = a / add` 对应源码 `x = a / (torch.abs(a) + 1)`。
- `sum_1 = b.sum()`、`lt = sum_1 < 0` 对应源码 `if b.sum() < 0` 的判定条件；这两个值的元组作为 `output` 输出，把 Python 控制流留到图外执行——这正是图断裂点。
- `a / (|a| + 1)` 这一段能被完全特化并静态捕获，所以构成 Dynamo 的第一段 FX 图；分支选择则在 Python 解释器中完成。

### 表 3：ORIGINAL BYTECODE（`toy_example`，example.py line 12，原文逐字还原）

| 源码行 | 偏移 | 操作码 | 参数 | 含义 |
|--------|------|--------|------|------|
| 14 | 0 | `LOAD_FAST` | 0 (a) | 取 `a` |
| 14 | 2 | `LOAD_GLOBAL` | 0 (torch) | 取全局 `torch` |
| 14 | 4 | `LOAD_METHOD` | 1 (abs) | 加载方法 `abs` |
| 14 | 6 | `LOAD_FAST` | 0 (a) | 取 `a` |
| 14 | 8 | `CALL_METHOD` | 1 | 调用 `torch.abs(a)` |
| 14 | 10 | `LOAD_CONST` | 1 (1) | 推入常量 1 |
| 14 | 12 | `BINARY_ADD` | | `abs(a) + 1` |
| 14 | 14 | `BINARY_TRUE_DIVIDE` | | `a / (abs(a)+1)` |
| 14 | 16 | `STORE_FAST` | 2 (x) | 存为 `x` |
| 15 | 18 | `LOAD_FAST` | 1 (b) | 取 `b` |
| 15 | 20 | `LOAD_METHOD` | 2 (sum) | 加载方法 `sum` |
| 15 | 22 | `CALL_METHOD` | 0 | 调用 `b.sum()` |
| 15 | 24 | `LOAD_CONST` | 2 (0) | 推入常量 0 |
| 15 | 26 | `COMPARE_OP` | 0 (<) | `b.sum() < 0` |
| 15 | 28 | `POP_JUMP_IF_FALSE` | 19 (to 38) | 若为假，跳到偏移 38 |
| 16 | 30 | `LOAD_FAST` | 1 (b) | 取 `b`（条件为真分支） |
| 16 | 32 | `LOAD_CONST` | 3 (-1) | 推入 -1 |
| 16 | 34 | `BINARY_MULTIPLY` | | `b * -1` |
| 16 | 36 | `STORE_FAST` | 1 (b) | 存回 `b` |
| 17 | 38 | `LOAD_FAST` | 2 (x) | 取 `x` |
| 17 | 40 | `LOAD_FAST` | 1 (b) | 取 `b` |
| 17 | 42 | `BINARY_MULTIPLY` | | `x * b` |
| 17 | 44 | `RETURN_VALUE` | | 返回 |

**解读**：原始字节码呈现 `toy_example` 的逐条 CPython 指令；偏移 30 是 `b = b * -1` 的入口，偏移 38 是两条分支汇合后 `x * b` 的入口——这两个偏移正是后续 `__resume_at_30_1` 与 `__resume_at_38_2` 的来源。

### 表 4：MODIFIED BYTECODE（原文逐字还原）

| 偏移 | 操作码 | 参数 | 含义 |
|------|--------|------|------|
| 0 | `LOAD_GLOBAL` | 3 (`__compiled_fn_0`) | 加载编译图 |
| 2 | `LOAD_FAST` | 0 (a) | 推 `a` |
| 4 | `LOAD_FAST` | 1 (b) | 推 `b` |
| 6 | `CALL_FUNCTION` | 2 | 调用 `__compiled_fn_0(a, b)` |
| 8 | `UNPACK_SEQUENCE` | 2 | 解包为 `(x, cond)` |
| 10 | `STORE_FAST` | 2 (x) | 存 `x` |
| 12 | `POP_JUMP_IF_FALSE` | 12 (to 24) | 条件为假跳到 24 |
| 14 | `LOAD_GLOBAL` | 4 (`__resume_at_30_1`) | 加载 continuation 1 |
| 16 | `LOAD_FAST` | 1 (b) | 推 `b` |
| 18 | `LOAD_FAST` | 2 (x) | 推 `x` |
| 20 | `CALL_FUNCTION` | 2 | 调用 continuation 1 |
| 22 | `RETURN_VALUE` | | 返回 |
| 24 | `LOAD_GLOBAL` | 5 (`__resume_at_38_2`) | 加载 continuation 2 |
| 26 | `LOAD_FAST` | 1 (b) | 推 `b` |
| 28 | `LOAD_FAST` | 2 (x) | 推 `x` |
| 30 | `CALL_FUNCTION` | 2 | 调用 continuation 2 |
| 32 | `RETURN_VALUE` | | 返回 |

**解读**：修改后字节码将 `a / (|a|+1)` 与 `b.sum() < 0` 的整段计算交给 `__compiled_fn_0`，并把控制流切换为根据 `cond` 选择调用 `__resume_at_30_1`（执行 `b = b * -1` 然后 `x*b`）或 `__resume_at_38_2`（直接 `x*b`），从而把可静态化的部分编入图、动态分支留在 Python 中。

### 表 5：通过 `guard.code_parts` 取出的 guard 条件（原文逐字还原）

| 序号 | 条件 |
|------|------|
| 1 | `___guarded_code.valid` |
| 2 | `___check_global_state()` |
| 3 | `hasattr(L['a'], '_dynamo_dynamic_indices') == False` |
| 4 | `hasattr(L['b'], '_dynamo_dynamic_indices') == False` |
| 5 | `utils_device.CURRENT_DEVICE == None` |
| 6 | `___skip_backend_check() or ___current_backend() == ___lookup_backend(140215810860528)` |
| 7 | `___check_tensors(L['a'], L['b'], tensor_check_names=tensor_check_names)` |

**解读**：与表 1 相比，这里使用了高层 helper（`___check_global_state()`、`___check_tensors()`）来压缩多条原始 guard；只有全部条件成立才会执行编译产物；同一图编译后不同次运行 `_lookup_backend` 的 id 可能不同（如表中 140215810860528 与表 1 中的 140355900538256 不同），属于缓存标识，不影响语义。

## 【公式解读】

原文无数学公式（无 LaTeX 表达式、无伪代码形式的算法描述）。

## 【关联】

- **上游/入口**：与 `../_menu_torch_compile.md`（即 `torch.compiler` 总菜单）形成从属关系——本文明确要求"阅读本节之前，请先阅读 torch.compiler"，定位为该菜单下"Dynamo 概述"子节。
- **核心依赖**：[FX 图](https://pytorch.org/docs/stable/fx.html) 是 Dynamo 的输出 IR；`torch.fx.GraphModule`、`gm.graph.print_tabular()` 是直接相关的 API。
- **后端**：[TorchInductor](https://dev-discuss.pytorch.org/t/torchinductor-a-pytorch-native-compiler-with-define-by-run-ir-and-symbolic-shapes/747) 把 Dynamo 图分别编译为 [Triton](https://github.com/triton-lang/triton)（NPU）与 [C++/OpenMP](https://www.openmp.org/)（CPU）；性能对比参见 [训练性能看板](https://hud.pytorch.org/benchmark/compilers)。
- **Python 运行时挂钩**：CPython [PEP 523](https://peps.python.org/pep-0523/) frame 求值 API，是 Dynamo 字节码改写能力的基础。
- **调试工具**：[depyf](https://github.com/youkaichao/depyf) 提供字节码反编译为可读 Python 源码的能力，是分析 Dynamo 行为的辅助工具。
- **学习资源**：[Dynamo 深度解析视频](https://www.youtube.com/watch?v=egZB5Uxki0I) 与 [dev-discuss 主题](https://dev-discuss.pytorch.org/search?q=TorchDynamo%20order%3Alatest) 提供深入材料。

## 【使用方法】

1. **启用方式**：
   - 装饰器形式：`@torch.compile(backend=my_compiler)`；
   - 底层 API：`torch._dynamo.optimize()`。
2. **自定义后端签名**：后端函数接收 `(gm: torch.fx.GraphModule, example_inputs: List[torch.Tensor])`，返回 Python 可调用对象（典型为 `gm.forward`）。
3. **调试日志**：
   ```bash
   TORCH_LOGS="+dynamo,guards,bytecode"
   ```
4. **反编译 hook**：
   ```bash
   pip install depyf
   ```
   ```python
   import depyf
   depyf.install()
   ```
5. **检查编译缓存**：
   ```python
   from torch._dynamo.eval_frame import _debug_get_cache_entry_list, innermost_fn
   cache_entries = _debug_get_cache_entry_list(innermost_fn(toy_example))
   cache_entry = cache_entries[0]
   guard, code = cache_entry.check_fn, cache_entry.code
   ```
6. **遍历 guard 条件**：
   ```python
   for code_part in guard.code_parts:
       print(code_part)
   ```
7. **反编译已编译代码**：
   ```python
   from depyf import decompile
   print(decompile(code))
   ```
8. **运行时配置项/动态形状开关**：原文未涉及具体配置项的命令形式；只在"完全特化模式"段落中说明"未启用动态形状模式时，返回动态形状的算子会触发图断裂"。

> 说明：原文末尾示例 `print(innermost_fn(__compiled_fn_0).__self__.c` 被截断，对应内容原文未给出，无法进一步解读。

## 图文联合解读

- `TorchDynamo.png`: **1) 图中内容：**
左右对比两幅流程图。左侧"Default Python Behavior"：`foo(...)` → `PyFrameObject` ↔ `PyCodeObject` → `_PyEval_EvalFrameDefault()`，为标准Python字节码求值流程。右侧"TorchDynamo Behavior"：在`PyFrameObject`到`_PyEval_EvalFrameDefault()`之间插入`Guards`（守卫）和`Patched PyFrameObject`；虚线框"Cached"内，`PyCodeObject`经"dynamic bytecode analysis + transform"分离为`FX Graphs (torch.* bits)`和`Transformed PyCodeObject (non-torch.* bits)`，前者送入`User-defined Compiler`生成`Compiled Function`，最终由`call`调用。

**2) 技术结论：**
Dynamo通过PEP 523 frame求值API挂接CPython，对字节码做动态分析与改写，将torch算子抽取为FX图编译、非torch部分回退至Python执行，并由guards保障特化正确性。

**3) 与文档论点的关系：**
图示直观支撑文档"Dynamo重写字节码→提取FX图→后端编译→结合Python执行兼顾易用性与性能"的核心论述，揭示了`torch.compile()`一键加速背后的拦截—转换—缓存—调用机制。
- `flowchart.png`: **图文联合解读：**

1) **图示内容**：左上"User Code"含被`@torch.compile`装饰的`toy_example`函数，按代码段颜色（红/蓝/黄）拆分为三个SubGraph Functions（`__compiled_fn_0`、`__resume_at_30_1`、`__resume_at_38_2`），送入右侧"Backend Compiler"编译，最终生成左下"Optimized Code"，中间由"Guard Function"（盾牌图标）守护调用合法性。

2) **技术结论**：Dynamo通过字节码分析将Python函数切分为多个子图，各子图独立编译后回填到原函数中，由guard保证特化条件成立时复用编译结果。

3) **与文档论点关系**：直观印证"Dynamo重写Python字节码、提取FX图、可自定义后端编译"的核心机制。
