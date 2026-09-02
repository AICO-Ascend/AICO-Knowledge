# Rust Guide

> 仓 `tvm-ffi` · 路径 `docs/guides/rust_lang_guide.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/tvm-ffi/docs/guides/rust_lang_guide.md

# TVM FFI Rust Guide 深度解读

## 【定位】

本指南解决**如何从 Rust 应用调用 TVM FFI** 的问题,描述了当前仍处于**实验阶段**的 Rust 语言绑定能力——围绕 `tvm-ffi` crate,涵盖了从安装、加载模块、操作 tensor,到全局函数、反射类型方法、借用值转换、类型擦除函数、结构化遍历 (Structural Walk/Visit) 等高级特性的完整使用方法。

---

## 【技术要点】

1. **依赖前置与安装**:Rust 支持依赖底层 C 库 `libtvm_ffi`;首先需以 `pip install -v -e .` 安装 `tvm-ffi` Python 包,通过 `tvm-ffi-config --libdir` 获取库路径;`Cargo.toml` 中以 path 或 `tvm-ffi = "0.1.0-alpha.0"` 版本方式引入。

2. **运行时环境变量**:`export LD_LIBRARY_PATH=$(tvm-ffi-config --libdir):$LD_LIBRARY_PATH` —— 需将 `libtvm_ffi` 所在目录注入链接路径,以便运行期动态定位。

3. **模块与函数调用**:`Module::load_from_file("build/add_one_cpu.so")?` 加载 `.so` 编译产物;`module.get_function("add_one_cpu")?` 按名取函数;`func.call_tuple((&input, &output))?` 以元组形式传参与调用。

4. **Tensor 构造**:`Tensor::from_slice(&data, &[2, 3])?` —— 接受 `&[f32]` 数据切片与形状数组,生成 TVM FFI 张量。

5. **反射类型方法查表**:基于 C++ `refl::ObjectDef<T>().def(...)` 注册的 API 存放在**每类型方法表**而非全局函数表中;需以 `Function::from_type_key_method("testing.TestIntPair", "__ffi_init__")` 按"类型键 + 方法名"解析,构造器统一以保留名 `__ffi_init__` 访问;`from_type_method(type_index, name)` 在类型索引已知时复用同一查表路径。

6. **借用值→`Any` 转换**:`Any::from(value)` 取得所有权;只有共享借用 (`&AddObj`) 时使用 `AnyCompatible::to_any()` —— 内部对 object-backed 值自增引用计数,**等价于 `Any::from(node.a.clone())` 但无需在调用点显式 clone**。

7. **类型擦除函数**:`Function::from_packed(|args: &[AnyView]| -> Result<Any> { ... })` 接受任意参数视图;`Function::from_typed(|x: i64, y: i64| -> Result<i64> { Ok(x + y) })` 提供静态类型签名的闭包。

8. **结构化遍历宏机制**:`#[dispatch(walk)]` 标注 `impl` 后,其 `walk_*` 方法变成类型化分派处理器;`structural_walk(root, visitor, WalkOrder::PreOrder)?` 返回 `Result<Option<VisitInterrupt>>`;`WalkResult` 三态为 `Advance` / `Skip` / `Interrupt`;`WalkResult::interrupt_with(payload)` 提前终止并把负载返回给调用者,表现为 `Ok(Some(interrupt))`。

9. **遍历回调组合**:Lambda 可单传,亦可按元组顺序尝试,**首个匹配的实参类型胜出**;扁平元组上限 **12** 个 lambda;元组本身视为 link,通过嵌套 `(a, b, (c, d, ...))` 链式扩展;`&VisitValue` lambda 为 catch-all,必须放在末位;Map/Dict 的 key 视为结构锚点 —— **只访问其 value,不把 key 传给处理器**,容器自身仍按常规被访问。

---

## 【关键机制与数据】

### 工作原理与数据流

1. **加载 → 取函数 → 调用 流水线** (原文: Basic Usage 全章)
   - `Module::load_from_file` → 解析 `.so` → 返回 `Module`
   - `module.get_function(name)` → 按名字查找 `Function`
   - `func.call_tuple((&input, &output))` → 通过 `?` 传播 `Result` 错误

2. **反射注册的两套表** (原文: Reflected Type Methods)
   - 全局函数表:`Function::get_global` 走之
   - 每类型方法表:`Function::from_type_key_method` / `from_type_method` 走之;构造器固定名 `__ffi_init__`;实例方法的第一个 packed 参数即为对象自身

3. **`to_any()` vs `Any::from` 的所有权差异** (原文: Converting Borrowed Values into `Any`)
   - `Any::from(value)`:夺取所有权,要求值可移动
   - `AnyCompatible::to_any()`:保留借用可继续使用;object-backed 值自动 `retain`(自增引用计数)
   - 等价关系:`to_any() ≡ Any::from(node.a.clone())` (无显式 clone)

4. **`#[dispatch(walk)]` 宏分发机制** (原文: Structural Walk and Visit)
   - 标注后,`impl` 中的 `walk_integer(i64)` / `walk_float(f64, DefRegionKind)` 等方法自动注册为类型化处理器
   - 每个 handler 返回 `WalkResult`(推进/跳过/中断)

5. **遍历的 Map/Dict 行为** (原文: Structural Walk and Visit)
   - 容器本身被访问; value 被访问;**key 不传给 handlers**

6. **回调链接(link)与匹配顺序** (原文: Structural Walk and Visit)
   - 扁平元组最长 12;超过则嵌套以"扁平左到右"顺序链接
   - 首个匹配实参类型的 lambda 胜出,后续不再调用
   - `&VisitValue` catch-all 必须位于最后

### 性能 / 量化数据

- **版本号**:发布版 `tvm-ffi = "0.1.0-alpha.0"`
- **元组上限**:**12** 个 lambda(超出需嵌套)
- **Tensor 示例形状**:`[2, 3]`(2×3)、`[4]`(1×4)
- **遍历断言结果**:`Array::new(vec![1,2,3])` → `probe.total == 6`,`(evens, objects) == (1, 1)`,`found == Some(2)`
- **Rust 支持状态**:**experimental**(原文 note 段)

---

## 【表格解读】

**原文无表格**

---

## 【公式解读】

**原文无公式**

---

## 【关联】

本指南作为 TVM FFI 多语言绑定系列文档之一,与以下上下游内容相互引用:

| 链接 | 路径类型 | 关系说明 |
|---|---|---|
| `../reference/rust/index.rst` | 上游/伴生 | Rust API 参考索引,提供与本指南对应的类型/函数详细签名 |
| `../get_started/quickstart.rst` | 上游 | 入门引导,通常先于本指南阅读以建立基本概念 |
| `./cpp_lang_guide.md` | 横向姊妹 | C++ 语言绑定指南;本指南中多处机制(`StructuralWalk` / `StructuralVisitor`、C++ 反射注册 `refl::ObjectDef<T>().def(...)`)为 C++ 端的对应实现,Rust 端是对其的镜像封装 |

**未提及**:`./python_lang_guide.md` 虽列入文末内部链接清单,但原文未展开与 Python 端的对比或互操作细节。

**模块依赖关系**(原文):Rust 绑定 → 底层 `libtvm_ffi`(C/C++ 共享库) → TVM FFI 反射注册体系;Rust 侧 `from_type_key_method` 与 C++ `refl::ObjectDef` 注册的类型键字符串必须严格一致(如 `"testing.TestIntPair"`)。

---

## 【使用方法】

### 启用方式

1. **构建/安装 `libtvm_ffi`** (前置)
   ```bash
   pip install -v -e .
   tvm-ffi-config --libdir          # 验证可执行
   ```

2. **加入 Rust 项目**
   ```toml
   [dependencies]
   tvm-ffi = { path = "path/to/tvm-ffi/rust/tvm-ffi" }
   # 或(发布版可用时)
   tvm-ffi = "0.1.0-alpha.0"
   ```

3. **运行时链接路径**
   ```bash
   export LD_LIBRARY_PATH=$(tvm-ffi-config --libdir):$LD_LIBRARY_PATH
   ```

### 关键 API 调用模式(原文列举的命令/调用一览)

| 类别 | API 调用 |
|---|---|
| 模块加载 | `Module::load_from_file("build/add_one_cpu.so")?` |
| 函数查找(全局) | `module.get_function("add_one_cpu")?` / `Function::get_global("my_function")?` |
| 函数查找(反射) | `Function::from_type_key_method("testing.TestIntPair", "__ffi_init__")?` / `Function::from_type_method(type_index, name)` |
| Tensor 构造 | `Tensor::from_slice(&data, &[2, 3])?` |
| 函数调用 | `func.call_tuple((&input, &output))?` / `ctor.call_tuple((1i64, 2i64))?` / `sum.call_packed(&[AnyView::from(&pair)])?` |
| 函数注册 | `Function::register_global("my_custom_func", my_func)?` |
| 类型擦除闭包 | `Function::from_packed(\|args: &[AnyView]\| -> Result<Any> { ... })` / `Function::from_typed(\|x: i64, y: i64\| -> Result<i64> { Ok(x + y) })` |
| 借用→Any | `AnyCompatible::to_any()`(配合 `node.a.to_any()`) |
| 错误构造 | `Error::new(VALUE_ERROR, "Value must be non-negative", "")` |
| 结构化遍历 | `structural_walk(&values, &mut probe, WalkOrder::PreOrder)?` |
| 中断遍历 | `WalkResult::interrupt_with(value)` |
| 遍历宏 | `#[dispatch(walk)]` 标注 `walk_integer` / `walk_float` 等 handler 方法 |

### 配置项 / 环境变量

- `LD_LIBRARY_PATH`:追加 `$(tvm-ffi-config --libdir)` 以定位 `libtvm_ffi`(原文)
- `tvm-ffi-config --libdir`:查询库路径的命令(原文)

> **注意**:原文末尾被截断于 "`structural_visit` accepts typed callbacks in additi…",`structural_visit` 的完整 API 形态**原文未给出**;另 `__ffi_init__` 作为构造器保留名(原文)等细节均按字面保留,未做推断扩展。
