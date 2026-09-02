# Compiler Integration

> 仓 `tvm-ffi` · 路径 `docs/guides/compiler_integration.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/tvm-ffi/docs/guides/compiler_integration.md

# docs/guides/compiler_integration.md 深度解读

## 【定位】

这篇文档描述 **TVM FFI 标准 ABI 如何与外部编译器（kernel 语言编译器与图编译器）对接**，让 Triton、TileLang、Mojo、cuteDSL、Helion、Hidet 等 DSL 编译器以及 ML 图编译器能将其生成的函数/模块以统一 ABI 暴露或调用，并说明编译器自身运行时/状态的推荐管理方式。

---

## 【技术要点】

1. **独立 ABI 定位**：TVM FFI 是 standalone 模块，与具体编译器或 IR 实现解耦，只规定 runtime ABI。
2. **Kernel 编译器三条接入路径**：
   - **LLVM 类 codegen**：导出符号 `__tvm_ffi_<func_name>`，可选导出 `__tvm_ffi__metadata_<func_name>` 用于反射。
   - **C++ host codegen**：使用 `TVM_FFI_DLL_EXPORT_TYPED_FUNC` 宏，在 `TVM_FFI_DLL_EXPORT_INCLUDE_METADATA=1` 时自动导出函数元数据。
   - **导出文档字符串**：使用 `TVM_FFI_DLL_EXPORT_TYPED_FUNC_DOC`，同样受 `TVM_FFI_DLL_EXPORT_INCLUDE_METADATA` 控制，用于 stub 生成与 IDE 提示。
3. **C ABI 函数签名（关键不变量）**：
   ```c
   int __tvm_ffi_<func_name>(void* handle, const TVMFFIAny* args, int32_t num_args, TVMFFIAny* result);
   ```
   返回值约定：**0 表示成功**，**-1 表示错误**；错误必须通过 `TVMFFIErrorSetRaisedFromCStr` 或 `TVMFFIErrorSetRaisedFromCStrParts` 设置。
4. **张量入参提取**：通过类型 tag `kTVMFFIDLTensorPtr`（直接指针）或 `kTVMFFITensor`（`DLTensor` 内嵌在 `TVMFFIObject` 之后，需做 `+sizeof(TVMFFIObject)` 偏移）来还原 `DLTensor*`。
5. **设备流获取**：调用 `TVMFFIEnvGetStream(x->device.device_type, x->device.device_id)` 取得当前 stream（CPU 场景不需要，文档保留作演示）。
6. **图编译器集成**：通过 `Op.call_tvm_ffi("my_func", *args)` 原语走 ABI；或用 Module API 加载/运行；AOT 场景使用 `TVMFFIFunctionCall` 调用 `tvm::ffi::Function`，或对暴露 C 符号的函数做直接调用。
7. **编译器运行时/状态管理**：推荐用一个独立共享库（如 `libmylang_runtime.so`）注册全局函数（如 `mylang.get_global_state`）拿到 singleton 指针；C++ 端用 `TVM_FFI_STATIC_INIT_BLOCK()` 注册，kernel 内通过 `GetGlobalRequired`（C++）或 `TVMFFIGetGlobalFunction`（C）取回。
8. **共同状态 vs 自定义状态**：`TVMFFIEnvGetStream` 等环境函数由 TVM FFI 自己管理 stream、allocator；编译器特有的 dynamic shape、workspace 等须自行按上述全局函数方案管理。

---

## 【关键机制与数据】

- **符号命名协议（原文）**：导出函数前缀 `__tvm_ffi_`；metadata 符号前缀 `__tvm_ffi__metadata_`。这是 codegen 必须复刻的"约定"而非 API。
- **元数据开关（原文）**：`TVM_FFI_DLL_EXPORT_INCLUDE_METADATA` 置 1 时，`TVM_FFI_DLL_EXPORT_TYPED_FUNC` 自动生成 metadata，`TVM_FFI_DLL_EXPORT_TYPED_FUNC_DOC` 同时导出 docstring。
- **C 端入参提取流程（原文代码解读）**：`ReadDLTensorPtr` 优先匹配 `kTVMFFIDLTensorPtr`（直接 `value->v_ptr` 强转为 `DLTensor*`）；否则要求 `type_index == kTVMFFITensor`，再以 `(char*)(value->v_obj) + sizeof(TVMFFIObject)` 偏移取出 `DLTensor*`。不匹配则调用 `TVMFFIErrorSetRaisedFromCStr("ValueError", "Expects a Tensor input")` 并返回 -1。
- **kernel 内执行流（原文）**：取出 `x`、`y` 两个 `DLTensor*` 后，调用 `TVMFFIEnvGetStream` 拿 stream（演示用，CPU 不必），再按 `x->shape[0]` 逐元素 `((float*)y->data)[i] = ((float*)x->data)[i] + 1`，返回 0。
- **运行时/状态分发机制（原文）**：把 runtime 打包为 Python/C++ package，用户在使用 kernel 前必须先 import/安装，确保多 kernel 共享同一份运行时状态。`TVM_FFI_STATIC_INIT_BLOCK()` 在静态初始化阶段把 `mylang.get_global_state` 注册为全局 `tvm::ffi::Function`，其返回 `void*`（singleton 指针）。
- **图编译器调用抽象（原文）**：`Op.call_tvm_ffi("my_func", *args)` 是高层原语；底层可走 `TVMFFIFunctionCall`（对 `tvm::ffi::Function`）或对导出 C 符号的 FFI 函数直接调用（AOT 路径）。
- **共同状态边界（原文）**：stream、memory allocator 等"通用"状态由 TVM FFI 通过环境函数提供，编译器不应自行管理；只有编译器特有的状态才走自定义全局函数方案。
- 原文未提供性能数据。

---

## 【表格解读】

**原文无表格。** 全文以列表、代码块和散文段落形式呈现，没有结构化的参数表或对比表。

---

## 【公式解读】

**原文无公式。** 文档不包含 LaTeX 数学公式或伪代码算法表达式；唯一的"形式化"内容是 C ABI 函数签名与一段示意 C 代码，均已在前文逐行解读。

---

## 【关联】

- **`../concepts/abi_overview.rst`**（文末显式链接）：被指引为"更完整的 ABI 指南"。本 guide 是面向编译器集成者的实践视角，而 abi_overview 给出 ABI 本身的整体规范——二者是"用法 vs 定义"的关系。
- **`../concepts/func_module.rst` 中的 `{ref}sec:custom-modules`**（seealso 块引用）：用于"包装平台特定驱动 API（如 `cuModuleLoad` 加载 PTX）"的自定义运行时模块构建，是本文"Distributing the Runtime / Custom Modules"思路的下游/配套章节——当全局函数方案不足以表达，需要更底层的模块封装时指向该处。
- **`quick_start example`**：文中 `__tvm_ffi_add_one_c` 代码明确指向 `examples/quick_start` 可运行示例，是该 ABI 规范的最小可执行参考。
- **DSLs/Kernel 语言生态**：Triton、TileLang、Mojo、cuteDSL、Helion、Hidet 被点名作为目标用户群体，说明本文是这些 DSL 的上游集成规范。
- **`{c:macro}` / `{cpp:func}` / `{cpp:class}` 交叉引用**：所有宏、函数、类都通过 Sphinx domain 交叉引用指向 API reference，本 guide 不展开实现，仅提供使用入口。

---

## 【使用方法】

以下条目均来自原文，列出"启用方式 / 配置项 / 命令"：

- **符号导出（codegen 方向）**：
  - 生成 C 符号 `__tvm_ffi_<func_name>`；可选生成 `__tvm_ffi__metadata_<func_name>` 提供反射。
- **C++ host 代码导出宏**：
  - `TVM_FFI_DLL_EXPORT_TYPED_FUNC`：自动导出函数。
  - `TVM_FFI_DLL_EXPORT_INCLUDE_METADATA=1`：开启自动 metadata 导出（同时控制 `TVM_FFI_DLL_EXPORT_TYPED_FUNC` 的 metadata 与 `TVM_FFI_DLL_EXPORT_TYPED_FUNC_DOC` 的 docstring 导出）。
  - `TVM_FFI_DLL_EXPORT_TYPED_FUNC_DOC`：在导出函数后单独调用，导出文档字符串以支持 stub/IDE tooltip。
- **kernel 内部约定**：
  - 入口前缀 `__tvm_ffi_`。
  - 拿当前 stream：`TVMFFIEnvGetStream(device_type, device_id)`。
  - 错误上报：`TVMFFIErrorSetRaisedFromCStr` 或 `TVMFFIErrorSetRaisedFromCStrParts`，随后返回 -1。
- **图编译器调用**：
  - `Op.call_tvm_ffi("my_func", *args)` 高层原语。
  - Module API 加载与运行；或查找已注册 global function 后调用。
  - AOT 路径：`TVMFFIFunctionCall` 调 `tvm::ffi::Function`；或对暴露 C 符号的函数直接调用。
- **编译器运行时/状态**：
  - 在独立共享库中定义 `GlobalState::Global()` 单例并 `new` 出指针。
  - 在 `TVM_FFI_STATIC_INIT_BLOCK()` 中用 `tvm::ffi::reflection::GlobalDef().def("mylang.get_global_state", ...)` 注册。
  - kernel 内 C++：`GetGlobalRequired("mylang.get_global_state")`；C 端：`TVMFFIGetGlobalFunction("mylang.get_global_state", ...)` 获取并调用。
- **运行时分发**：将 `libmylang_runtime.so`（或对应产物）打包进 Python/C++ package，用户在加载该编译器生成的任何 kernel 前必须先安装/导入该包，确保运行时与状态在多 kernel 间共享。
- 原文未涉及具体的编译命令、CMake 选项或环境变量名（如 `TVM_FFI_DLL_EXPORT_INCLUDE_METADATA` 之外的其他构建开关），亦未给出 quick_start 之外的端到端运行脚本。
