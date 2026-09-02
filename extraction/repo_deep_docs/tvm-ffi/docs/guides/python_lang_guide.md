# Python Guide

> 仓 `tvm-ffi` · 路径 `docs/guides/python_lang_guide.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/tvm-ffi/docs/guides/python_lang_guide.md

# TVM FFI Python Guide 深度解读

## 【定位】

这篇文档是 TVM FFI 的 **Python 语言指南**，系统介绍 `tvm_ffi` Python 包所提供的三大能力——以 Pythonic 形式表达 TVM FFI Any ABI 中的值、调用 TVM FFI ABI 兼容函数、以及 Python 值与 `tvm_ffi` 值之间的双向转换——并配套可运行的代码示例，是 Python 用户使用 TVM FFI 的官方入门与参考手册。

---

## 【技术要点】

1. **三件核心能力**: `tvm_ffi` 包提供 (1) TVM FFI Any ABI 值的 Pythonic 类表示；(2) 调用 TVM FFI ABI 兼容函数的机制；(3) Python 值与 `tvm_ffi` 值的相互转换。
2. **模块加载与函数调用**: 通过 `tvm_ffi.load_module("build/add_one_cpu.so")` 加载已编译动态库，返回 `tvm_ffi.Module` 对象，通过属性方式访问导出函数（如 `mod.add_one_cpu(x, y)`）。
3. **Tensor 与 DLPack 互操作**: `tvm_ffi` 提供 managed DLPack-compatible Tensor，可通过 `tvm_ffi.from_dlpack(np_data)` 与 `np.from_dlpack(tvm_array)` 实现与 NumPy 的零拷贝互换；同时支持 `torch.Tensor` 与 `numpy.ndarray` 自动转换为 `tvm_ffi.Tensor`。
4. **函数与回调**: `tvm_ffi.Function` 对应 C++ `ffi::Function`，通过 `tvm_ffi.get_global_func("name")` 获取全局注册函数；Python 函数（lambda / 普通函数）可作为回调参数传入 FFI 函数，内部由 `tvm_ffi.convert` 包装为 `tvm_ffi.Function`；通过装饰器 `@tvm_ffi.register_global_func("name")` 可将 Python 函数注册为全局 FFI 函数。
5. **参数转换协议 (7 种 dunder 协议)**: `__tvm_ffi_object__`、`__tvm_ffi_value__`、`__tvm_ffi_opaque_ptr__`、`__tvm_ffi_int__`、`__tvm_ffi_float__`、`__tvm_ffi_env_stream__`、`__cuda_stream__`，需定义在类上（非单实例动态安装），以便派发可按类型缓存；其中 `__cuda_stream__` 是按 NVIDIA CUDA 外部协议识别的。
6. **四（五）类容器**: 分为 **immutable**（copy-on-write）与 **mutable**（shared reference）两组——`tvm_ffi.Array` / `tvm_ffi.List` / `tvm_ffi.Map` / `tvm_ffi.Dict`；Python list/tuple 默认转换为 `Array`，dict 默认转换为 `Map`，二者均为只读；`List.append` 与 `List[i] = v` 等可变操作对所有共享同一 `ListObj` 的句柄立即可见。
7. **第三方类的旁路处理**: 当第三方类无法定义或 monkey-patch 协议时，可在应用启动期向 `tvm_ffi.core._OPAQUE_PTR_HANDLERS[ForeignWorkspace] = lambda obj: obj.address` 注册精确类处理器；该映射在 FFI 调用运行时应只读，按精确类匹配派发，类自身的 `__tvm_ffi_opaque_ptr__` 优先于该映射。

---

## 【关键机制与数据】

### 工作原理 / 数据流

- **Load 流程**: `tvm_ffi.load_module("build/add_one_cpu.so")` → 加载 `.so` → 返回 `tvm_ffi.Module` 实例 → 通过属性访问（如 `mod.add_one_cpu`）取得导出函数句柄 → 调用时参数按 `Any` 调用约定逐个转换。
- **Argument Conversion 流程**: Python 调用 `tvm_ffi.Function` 时，每个参数先被尝试匹配**内置直接转换**（`int`/`float`/`str`/`bytes`/`list`/`tuple`/`dict`/callable/`tvm_ffi.Object`/`tvm_ffi.Tensor`/DLPack tensor/exception）；若不匹配则按**协议**派发（7 种 dunder）→ 最终转入 `Any` 调用约定。对 DLPack 兼容对象遵循 [DLPack protocol](https://dmlc.github.io/dlpack/latest/)。
- **Callback 流程**: Python 函数作为参数传入 → `tvm_ffi.convert` 将其包装为 `tvm_ffi.Function` → 在 C++ 端作为 `ffi::Function` 被执行 → 可回调到 Python 侧；装饰器 `@tvm_ffi.register_global_func("example.add_one")` 路径相反——将 Python 函数注册为可在 FFI 全局查找到的 `Function`。
- **Container 转换**: Python `list` / `tuple` 进入 FFI 时被转换为 `tvm_ffi.Array`（immutable, copy-on-write）；Python `dict` 被转换为 `tvm_ffi.Map`（immutable, copy-on-write）；`List` 与 `Dict` 需用 `tvm_ffi.List([...])` / `tvm_ffi.Dict({...})` 显式构造，是 **shared reference**——即对同一底层 `ListObj` 的所有 Python 句柄都能立即观察 mutation。

### 原文给出的具体例子与可观察值

- 原文: `mod.add_one_cpu(x, y)` 接受 `np.array([1, 2, 3, 4, 5], dtype=np.float32)` 与同形状 `np.empty_like(x)`。
- 原文: `fecho = tvm_ffi.get_global_func("testing.echo")`，对应 C++ 实现 `[](ffi::Any x) { return x; }`，验证 `assert fecho(1) == 1`。
- 原文: `fapply = tvm_ffi.get_global_func("testing.apply")`，对应 C++ 实现 `[](ffi::Function f, ffi::Any val) { return f(x); }`，验证 `assert fapply(lambda x: x + 1, 1) == 2`。
- 原文: `@tvm_ffi.register_global_func("example.add_one")` 注册后 `assert tvm_ffi.get_global_func("example.add_one")(1) == 2`。
- 原文: `Workspace` 示例使用 `ctypes.c_uint8 * size` 分配 `4096` 字节缓冲，通过 `__tvm_ffi_opaque_ptr__` 返回 `ctypes.addressof(self.buffer)`。
- 原文: `tvm_ffi.List([1, 2, 3])` 经 `lst.append(4)` 后 `len(lst) == 4`；`lst[0] = 10` 后 `lst[0] == 10`。

> 文档未给出性能/吞吐数据。

---

## 【表格解读】

### 表格 1：Argument Conversion Protocols（参数转换协议）

| Protocol | Expected return | Behavior |
| -------- | --------------- | -------- |
| `__tvm_ffi_object__(self)` | A `tvm_ffi.Object` instance | Passes the returned FFI object handle directly. Use this for wrapper classes that own or expose an existing FFI object. |
| `__tvm_ffi_value__(self)` | Another Python value | Recursively converts the returned value. This is useful for lightweight wrappers around values such as strings, arrays, maps, objects, or scalars. Conversion detects recursive cycles and reports them as conversion/type errors. |
| `__tvm_ffi_opaque_ptr__(self)` | An integer pointer value | Passes the value as an opaque pointer. This is for low-level interop with raw memory structs. |
| `__tvm_ffi_int__(self)` | An integer | Passes the value as an FFI integer. |
| `__tvm_ffi_float__(self)` | A float | Passes the value as an FFI float. |
| `__tvm_ffi_env_stream__(self)` | An integer stream handle | Used with non-CPU tensor inputs that expose DLPack. The stream is recorded in the FFI call context so the callee can observe the producer framework's current stream. |
| `__cuda_stream__(self)` | A [CUDA stream protocol](https://nvidia.github.io/cuda-python/cuda-core/latest/interoperability.html) value | Passes the stream as an opaque pointer. |

**逐行解读**:
- `__tvm_ffi_object__` 是"直传 Object 句柄"通道，用于那些**自己持有或暴露 FFI 对象**的包装类（典型场景：DSL 编译器的对象包装），绕过对象重建。
- `__tvm_ffi_value__` 是"递归转换"通道，适合**轻量值包装器**（字符串、数组、Map、Object、标量）；并具备**递归循环检测**——发生环引用时会被报告为 conversion/type error，不会无限递归。
- `__tvm_ffi_opaque_ptr__` 是"不透明指针"通道，专门给**底层互操作**用，例如把一个 `ctypes` 缓冲区地址传给 C++ 端；典型场景是编译器 workspace。
- `__tvm_ffi_int__` / `__tvm_ffi_float__` 把对象"坍缩"为 FFI 的整型/浮点标量；当 Python 类表示一个数值但又不是原生 `int`/`float` 时使用。
- `__tvm_ffi_env_stream__` 与 `__cuda_stream__` 是**流协议**：前者由 TVM FFI 内部定义，记录到 FFI 调用上下文，使被调函数可以观察"产生方框架的当前流"；后者识别外部 [CUDA stream protocol](https://nvidia.github.io/cuda-python/cuda-core/latest/interoperability.html)，以 opaque pointer 形式传入。
- 关键约束：协议**必须定义在类上**，不要在单实例上动态安装——转换器对大多数协议**按类型查表**派发，便于缓存。

### 表格 2：Container Types（容器类型）

| Type | Mutability | Python ABC | Semantics |
| ------ | ----------- | ------------ | ----------- |
| `tvm_ffi.Array` | Immutable | `Sequence[T]` | Homogeneous sequence (copy-on-write) |
| `tvm_ffi.List` | Mutable | `MutableSequence[T]` | Homogeneous sequence (shared reference) |
| `tvm_ffi.Map` | Immutable | `Mapping[K, V]` | Homogeneous mapping (copy-on-write) |
| `tvm_ffi.Dict` | Mutable | `MutableMapping[K, V]` | Homogeneous mapping (shared reference) |

**逐行解读**:
- 表格列出 **4 个**容器，但正文导语写的是 "five container types"。原文未列出第 5 个；此处忠实按表格呈现。
- **Array (Immutable, CoW)**：Python `list` / `tuple` 跨 FFI 边界时的默认去向；`Sequence[T]` ABC；支持索引与迭代但**不支持赋值**——原文 `arr[0] = 10` 会抛 `TypeError`。
- **List (Mutable, Shared)**：`MutableSequence[T]` ABC；`append` / `__setitem__` 等 mutation 对**所有共享同一底层 `ListObj`** 的句柄立即可见——这是与 `Array` 最关键的行为分野。
- **Map (Immutable, CoW)**：Python `dict` 进入 FFI 时被转换为 `tvm_ffi.Map`；只读。
- **Dict (Mutable, Shared)**：`MutableMapping[K, V]` ABC；语义与 `List` 一致——共享引用，mutation 全局可见。
- "Homogeneous" 指键/值类型在同一容器内一致；"copy-on-write" 与 "shared reference" 决定了跨语言边界时的拷贝时机。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **`../get_started/quickstart.rst`**（[quickstart guide]）：本文 "Load and Run Module" 一节明确指向 quickstart 指南，用于了解如何构建 `build/add_one_cpu.so` 这类动态库——也就是说，Python 指南假设读者已通过 quickstart 完成 C++ 端"注册函数 + 编译 `.so`"的工作，再回到本指南用 `tvm_ffi.load_module` 加载并调用。
- **`../concepts/containers.rst`**（[Containers concept page]）：本文 "Container Types" 一节明确指向该概念页，用于"detailed overview"——即本指南只给出 Python 侧的最少示例（`Array` 只读、`List` 可变等），更系统的 CoW vs shared-reference 设计原理、`ListObj` 引用计数等概念由该页承载。
- **上下游 / 横向关联**（基于原文内容）：
  - 与 **C++ 端** `ffi::Function`、`ffi::Any` 直接对应：`tvm_ffi.Function` ↔ `ffi::Function`；`get_global_func("testing.echo")` 等示例展示 Python 与 C++ 共享同一全局函数命名空间。
  - 与 **DLPack 生态**对齐：通过 `__tvm_ffi_env_stream__` / `__cuda_stream__` 协议，把 PyTorch / CUDA Python 等 producer 框架的当前流暴露给 FFI 上下文，使被调 C++ 端能正确观察 producer stream。
  - 与 **第三方封装**：通过 `tvm_ffi.core._OPAQUE_PTR_HANDLERS` 把无法修改源码的类接入 FFI opaque pointer 通道，是该指南支持的唯一"官方逃生口"。

---

## 【使用方法】

### 启用 / 加载模块

```python
import tvm_ffi
mod = tvm_ffi.load_module("build/add_one_cpu.so")  # 加载已编译 .so
mod.add_one_cpu(x, y)                              # 按函数名访问并调用
```

### Tensor / NumPy 互操作

```python
tvm_array = tvm_ffi.from_dlpack(np_data)           # NumPy -> TVM FFI Tensor
np_result = np.from_dlpack(tvm_array)              # TVM FFI Tensor -> NumPy
```
也可直接传入 `torch.Tensor` / `numpy.ndarray`，无需显式包装。

### 获取全局函数 / 注册 Python 回调

```python
fecho = tvm_ffi.get_global_func("testing.echo")    # 取出已注册函数
fapply(lambda x: x + 1, 1)                         # Python 函数作为回调传入

@tvm_ffi.register_global_func("example.add_one")  # 把 Python 函数注册为全局 FFI 函数
def add_one(a):
    return a + 1
```

### 为第三方类注册 Opaque Pointer 处理器

```python
tvmffi.core._OPAQUE_PTR_HANDLERS[ForeignWorkspace] = lambda workspace: workspace.address
```
> 配置时点：必须在该类实例**进入 FFI 调用之前**完成；运行期视作只读；匹配按精确类（不含子类）；类自身的 `__tvm_ffi_opaque_ptr__` 优先。

### 容器构造

```python
tvm_ffi.convert([1, 2, 3, 4])    # list/tuple -> Array (immutable)
tvm_ffi.List([1, 2, 3])          # 显式可变共享列表
# dict -> Map (immutable)
```

> 原文未涉及：编译选项、环境变量、`pip install` 之外的额外配置项。
