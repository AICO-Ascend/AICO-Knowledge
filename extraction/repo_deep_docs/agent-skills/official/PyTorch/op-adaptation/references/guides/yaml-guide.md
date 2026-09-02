# YAML Configuration Guide

> 仓 `agent-skills` · 路径 `official/PyTorch/op-adaptation/references/guides/yaml-guide.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/agent-skills/official/PyTorch/op-adaptation/references/guides/yaml-guide.md

# YAML Configuration Guide 深度解读

## 【定位】
本指南面向昇腾（Ascend）社区 `op_plugin` 中 `op_plugin_functions.yaml` 配置文件的编写规范，系统性描述如何在 PyTorch 算子适配（op-adaptation）流程中以 YAML 声明注册自定义（`custom`）/官方（`official`）/SymInt 类型算子，覆盖版本范围、参数位置、特殊 schema 要求与输出推断函数引用等核心配置维度。

---

## 【技术要点】

1. **三段顶层分类（official / custom / symint）**：分别对应 PyTorch 原生算子、前缀为 `npu_` 的自定义算子，以及支持 `SymInt` 类型参数的算子；其中 `symint` 必须与 `custom`（或 `official`）共存（dual registration）。

2. **字段语义分工**：
   - `func`：算子 schema，形如 `name(parameter_list) -> return_type`；
   - `op_api`：支持 aclnn 调用的版本区间（如 `[v2.1, newest]`）；
   - `exposed`：对外商用版本区间，**仅前向算子**设置，反向/内部辅助算子不设；
   - `internal_format_opapi`：Ascend NZ 格式调度的白名单字段，默认走 `acl_op`，显式声明后改走 `op_api`。

3. **版本区间三选一**：`op_api: all_version`（全版本通用）、`op_api: [v2.1, newest]`（自 v2.1 起新增，**新自定义算子默认**）、`op_api: v2.7`（仅单一特定版本）。`all_version` 是关键字而非独立字段。

4. **SymInt 双注册 + `_symint` 后缀 + 版本门控**：YAML 必须在 `custom`（或 `official`）与 `symint` 两段同步登记；C++ 函数命名带 `_symint` 后缀，第一个 SymInt 参数映射为 `c10::SymIntArrayRef` 或 `c10::SymInt`；C++ 实现必须用 `#if VERSION_BETWEEN(V2R1, VERSION_NEWEST)` / `#endif` 包夹，因 SymInt 仅 PyTorch v2.1+ 支持。

5. **参数位置硬性规则（不随默认值变化）**：由 `_def.cpp` 中 `AttrType` 决定 —— `REQUIRED` 一律在 `*` 前，`OPTIONAL` 一律在 `*` 后；即便 `_def.cpp` 给 `REQUIRED` 参数提供了 `Attr(default_value)`，YAML 中也必须写在 `*` 前。

6. **特殊 schema 必填字段**（缺失会触发 torchgen 构建错误）：
   - `dispatch: CompositeExplicitAutograd`：函数名以 `new_` 开头、以 `_like` 结尾，或含 `tensor_options` 参数且无 Tensor 输入；
   - `tags: nondeterministic_seeded`：函数名含 `rand` / `dropout`，或含 `generator` 输入参数。

7. **版本化算子与 `.List` 重载的工程要求**：
   - 版本变体（如 `_v2`）视作独立算子 —— 需独立 YAML 条目、C++ 实现文件（`{Name}V2KernelNpuOpApi.cpp`）、Meta 注册、测试文件；
   - `.List` 重载（`Tensor?` → `int[]?`）共享同一 C++ 实现（两个重载函数），但仍需独立 YAML 条目和 Meta 注册，测试可共用一份。

---

## 【关键机制与数据】

- **配置文件落点**（原文）：`op_plugin/config/op_plugin_functions.yaml`。
- **SymInt 支持起讫版本**（原文）：PyTorch v2.1+，门控宏 `VERSION_BETWEEN(V2R1, VERSION_NEWEST)`。
- **SymInt 参数到 C++ 类型的映射**（原文）：第一个 SymInt 参数 → `c10::SymIntArrayRef` 或 `c10::SymInt`。
- **特殊触发条件**（原文）：
  - `CompositeExplicitAutograd` 触发 —— 名字以 `new_` 开头、以 `_like` 结尾、含 `tensor_options` 但无 Tensor 输入；
  - `nondeterministic_seeded` 触发 —— 名字含 `rand` / `dropout`、含 `generator` 输入。
- **NZ 格式默认行为**（原文）：Ascend-native 格式输入默认 dispatch 到 `acl_op`；添加 `internal_format_opapi` 字段后改为 dispatch 到 `op_api`。
- **输出推断函数引用目标**（原文）：`size:` → `op_plugin/utils/KernelNpuOutputSize.h`；`dtype:` → `op_plugin/utils/KernelNpuOutputDtype.h`；声明在 `.h`，定义在同名 `.cpp`。
- **版本变体文件命名**（原文）：`{Name}V2KernelNpuOpApi.cpp`。
- **`exposed` 适用范围**（原文）：**仅前向算子**设置；反向算子、内部辅助、非对外算子省略。
- **`op_api: all_version` 的语义**（原文）：代表"所有当前支持的 PyTorch 版本"，是关键字值而非独立 YAML 字段。
- **构建失败来源**（原文）：未在必须时包含 `dispatch: CompositeExplicitAutograd` 或 `tags: nondeterministic_seeded` 会导致 **torchgen** 报构建错误。

---

## 【表格解读】

### 表 1：Configuration Fields（配置字段说明表）

| Field | Description |
|-------|-------------|
| `official` | PyTorch native operators |
| `custom` | Custom operators (prefixed with npu_) |
| `symint` | Operators supporting SymInt type parameters, must be configured together with custom |
| `func` | Operator schema: `name(parameter_list) -> return_type` |
| `op_api` | Version range supporting aclnn calls |
| `exposed` | Version range for commercial (externally exposed) operators. **Only set for forward operators**; omit for backward operators, internal helpers, or operators not intended for external use. |
| `internal_format_opapi` | Whitelist field for Ascend NZ format dispatch. By default, operators with Ascend-native format inputs dispatch to acl_op; adding this field enables dispatch to op_api instead. |

**逐行解读：**
- `official`：PyTorch 原生算子入口，使用原生（非 `npu_` 前缀）算子名。
- `custom`：自定义算子入口，**所有自定义算子名必须以 `npu_` 前缀**。
- `symint`：SymInt 类型算子入口，**强制要求**与 `custom`（或 `official`）**共同配置**，不能单独出现。
- `func`：算子的"签名骨架"，决定参数列表与返回类型，是 PyTorch 注册机制识别的核心。
- `op_api`：声明该算子在哪些 PyTorch 版本区间内可走 aclnn 调用接口；用于版本兼容控制。
- `exposed`：**仅前向算子**填写，控制"对外商用"暴露的版本范围；反向算子、内部辅助、纯内部算子**必须省略**。
- `internal_format_opapi`：Ascend NZ 格式调度的开关 —— 默认走 `acl_op`，添加此字段后改走 `op_api`，属于白名单机制。

### 表 2：Parameter Position Rules（参数位置规则表）

| AttrType | Has default | YAML position | Example |
|----------|-------------|---------------|---------|
| REQUIRED | Yes | Before `*` | `float scale_value=1.0` before `*` |
| REQUIRED | No | Before `*` | `Tensor input` before `*` |
| OPTIONAL | Yes | After `*` | `int? mode=0` after `*` |
| OPTIONAL | No | After `*` | `Tensor? mask=None` after `*` |

**逐行解读：**
- `REQUIRED + 有默认值`：仍放在 `*` 前。默认值来自 `_def.cpp` 的 `Attr(default_value)`，但 **AttrType 才是 YAML 位置的唯一判据**。
- `REQUIRED + 无默认值`：放在 `*` 前，标准位置参数语义。
- `OPTIONAL + 有默认值`：放在 `*` 后，作为 keyword-only 参数。
- `OPTIONAL + 无默认值`：放在 `*` 后，作为 keyword-only 参数。
- **核心结论**：表格右侧列项合并后只剩两条规则 —— `REQUIRED` 一律在 `*` 前、`OPTIONAL` 一律在 `*` 后，与是否存在默认值无关，对齐 Python `def func(a, b=1, *, c=None)` 语义。

---

## 【公式解读】

### 公式 1：基础 func schema（伪签名）

```
custom:
  - func: npu_operator_name(Tensor input, *, Tensor? optional=None, int attr=1) -> (Tensor, Tensor)
    op_api: [v2.1, newest]
    exposed: [v2.1, newest]
```

- **`npu_operator_name`**：算子注册名（自定义算子须以 `npu_` 前缀）。
- **`Tensor input`**：必填输入张量，位置在 `*` 之前，对应 `AttrType=REQUIRED`。
- **`*`**：位置参数 / 关键字参数分隔符；左侧为位置参数，右侧为 keyword-only。
- **`Tensor? optional=None`**：`?` 表示 `OPTIONAL` 类型，`None` 为默认占位；位于 `*` 之后。
- **`int attr=1`**：`OPTIONAL + 有默认值`，keyword-only 关键字参数。
- **`-> (Tensor, Tensor)`**：返回类型为两个 `Tensor` 元组，PyTorch 注册时按此元数派发。
- **`op_api: [v2.1, newest]`**：声明 aclnn 调用支持的版本区间为 v2.1 至当前最新。
- **`exposed: [v2.1, newest]`**：声明对外商用暴露的版本区间为 v2.1 至当前最新（仅前向算子使用）。

### 公式 2：Type Rules 混合签名

```
func: npu_op(Tensor input, int dim, *, Tensor? mask=None, int? mode=None, str layout="BSH") -> Tensor
```

- **`Tensor input`、`int dim`**：均为 `REQUIRED`（无 `?`、无默认），位于 `*` 前。
- **`*`**：分隔符。
- **`Tensor? mask=None`、`int? mode=None`**：`OPTIONAL + 有默认值`，keyword-only。
- **`str layout="BSH"`**：`OPTIONAL + 有默认值`，keyword-only，且字符串默认 `"BSH"`。
- **`-> Tensor`**：单 `Tensor` 返回。

### 公式 3：SymInt 双注册 schema

```
custom:
  - func: npu_op(Tensor input, SymInt[] sizes) -> Tensor
    op_api: [v2.1, newest]
symint:
  - func: npu_op(Tensor input, SymInt[] sizes) -> Tensor
    op_api: [v2.1, newest]
```

- **`SymInt[] sizes`**：SymInt 数组参数；与 C++ 端 `c10::SymIntArrayRef` 对应。
- **`custom` + `symint` 双段**：必须完全相同的 `func` 签名，缺失任一段将无法在 v2.1+ 路径上正确派发。

### 公式 4：C++ SymInt 实现门控模板

```cpp
#if VERSION_BETWEEN(V2R1, VERSION_NEWEST)
at::Tensor npu_op_symint(const at::Tensor& input, c10::SymIntArrayRef sizes) {
    // ...
}
#endif
```

- **`#if VERSION_BETWEEN(V2R1, VERSION_NEWEST)`**：版本门控宏，限定 SymInt 实现仅在 PyTorch v2.1 至最新版本之间编译生效。
- **`npu_op_symint`**：函数命名 **必须带 `_symint` 后缀**，与 YAML 中 `symint:` 段对应。
- **`const at::Tensor& input`**：普通 `Tensor` 输入参数类型。
- **`c10::SymIntArrayRef sizes`**：第一个 SymInt 参数的 C++ 映射类型（数组形式）；若为标量则用 `c10::SymInt`。
- **`#endif`**：闭合版本门控。

### 公式 5：特殊 schema — `CompositeExplicitAutograd`

```yaml
- func: empty_with_format(int[] size, *, ScalarType? dtype=None, int acl_format=2) -> Tensor
  dispatch:
    CompositeExplicitAutograd: empty_with_format
```

- **`int[] size`**：位置参数，整型数组输入。
- **`ScalarType? dtype=None`**：keyword-only，`OPTIONAL`。
- **`int acl_format=2`**：keyword-only，`OPTIONAL + 有默认值`。
- **`dispatch.CompositeExplicitAutograd: empty_with_format`**：声明 CompositeExplicitAutograd 派发键，键值为函数名本身；满足触发条件之一（无 Tensor 输入 + 含 `tensor_options` 形态的参数）。

### 公式 6：特殊 schema — `nondeterministic_seeded`

```yaml
- func: dropout_with_byte_mask(Tensor self, float p, bool train) -> Tensor
  tags: nondeterministic_seeded
```

- **`Tensor self`**：`REQUIRED` 位置参数。
- **`float p`、`bool train`**：`REQUIRED` 位置参数（`AttrType` 决定在 `*` 前）。
- **`tags: nondeterministic_seeded`**：语义标签，声明算子涉及非确定性随机性（满足函数名含 `dropout` 的触发条件）。

### 公式 7：版本区间写法对照

```yaml
op_api: all_version        # Use for operators available in all supported versions
op_api: [v2.1, newest]     # Use for operators added since v2.1 (most common for new ops)
op_api: v2.7               # Use for operators only in a specific version
```

- **`all_version`**：关键字值，代表所有当前支持的 PyTorch 版本集合，用于覆盖全版本。
- **`[v2.1, newest]`**：自 v2.1 起新增算子的标准写法（含起点和终点）。
- **`v2.7`**：单一版本号写法，仅在该版本可用。

### 公式 8：参数位置 — 错误 vs 正确对照

```yaml
# Incorrect — scale_value is REQUIRED in _def.cpp, should NOT be after *
func: npu_op(Tensor input, *, float scale_value=1.0) -> Tensor

# Correct — scale_value is REQUIRED → before *, regardless of default
func: npu_op(Tensor input, float scale_value, *, Tensor? mask=None) -> Tensor
```

- **错误式**：`scale_value=1.0` 写在 `*` 后，但 `_def.cpp` 中其 `AttrType=REQUIRED`；尽管有默认值，仍违反 `REQUIRED → *` 前 的规则。
- **正确式**：将 `scale_value`（不带默认值）放在 `*` 前，与 `_def.cpp` 的 `AttrType` 对齐；`mask=None` 作为 `OPTIONAL` 留在 `*` 后。

### 公式 9：输出 size / dtype 推断函数引用

```yaml
# size: references a custom function declared in KernelNpuOutputSize.h
size: npu_operator_out_size(input, param)

# dtype: references a custom function declared in KernelNpuOutputDtype.h
dtype: infer_dtype(input, param)
```

- **`size: npu_operator_out_size(input, param)`**：声明 YAML `size:` 字段引用 `KernelNpuOutputSize.h` 中声明的同名 C++ 函数，参数 `input` / `param` 与 YAML 参数对齐。
- **`dtype: infer_dtype(input, param)`**：声明 YAML `dtype:` 字段引用 `KernelNpuOutputDtype.h` 中声明的 C++ 函数。

---

## 【关联】

本指南作为 `op_plugin` 注册机制的"配置侧"规范，与以下上下游/兄弟模块存在明确耦合：

- **C++ 实现侧（强耦合）**：
  - `_def.cpp` —— 算子 `AttrType` 的事实来源，决定 YAML 参数位置（REQUIRED/OPTIONAL 与 `*` 的关系）。指南要求 YAML `func` 签名必须先与 `_def.cpp` 对齐，再进入 C++ 编写（Best Practices 节）。
  - `op_plugin/utils/KernelNpuOutputSize.h` / `KernelNpuOutputDtype.h` —— `size:` / `dtype:` YAML 字段的声明容器；同名 `.cpp` 提供定义。
  - `{Name}V2KernelNpuOpApi.cpp`（版本变体）、`_symint` 后缀 C++ 函数 —— 与 YAML 版本段、`symint:` 段一一对应。
- **Meta 注册侧（强耦合）**：每个 YAML `func` 条目（含版本变体与 `.List` 重载）都需要独立的 Meta 注册。
- **测试侧**：版本变体需独立测试文件；`.List` 重载可共用测试文件。
- **PyTorch 工具链**：
  - **torchgen** —— 构建期 schema 验证器；未在必须时填写 `dispatch: CompositeExplicitAutograd` 或 `tags: nondeterministic_seeded` 会触发构建错误。
  - PyTorch 版本门控宏 —— `VERSION_BETWEEN(V2R1, VERSION_NEWEST)` 等用于 SymInt 等特性的条件编译。
- **下游文档**：指南在"Output Size/Dtype Functions"节显式链接 `references/guides/cpp-guide.md` 的 "Output Size Functions" 节，提示读者需要参考该节获取 C++ 函数模板。
- **配置载体**：`op_plugin/config/op_plugin_functions.yaml` 是所有上述机制的唯一落地文件。

---

## 【使用方法】

> 原文提供以下可直接采用的启用方式 / 配置项 / 命令：

**1. 添加新算子到配置文件**（原文 Basic Structure 节）：
```yaml
custom:
  - func: npu_operator_name(Tensor input, *, Tensor? optional=None, int attr=1) -> (Tensor, Tensor)
    op_api: [v2.1, newest]
    exposed: [v2.1, newest]
```
落点文件：`op_plugin/config/op_plugin_functions.yaml`。

**2. 版本区间选择规则**（原文 Version Range Selection 节）：
- 通用算子：`op_api: all_version`
- 新自定义算子（默认推荐）：`op_api: [v2.1, newest]`
- 单一版本专属：`op_api: v2.7`
- `exposed` 字段同样支持上述写法，但 **仅前向算子填写**。

**3. SymInt 算子启用流程**（原文 SymInt Operators 节）：
- YAML：在 `custom:` 与 `symint:` 两段同时声明同一 `func` 签名，`op_api: [v2.1, newest]`；
- C++：函数名带 `_symint` 后缀，第一个 SymInt 参数使用 `c10::SymIntArrayRef`（数组）或 `c10::SymInt`（标量）类型；
- 版本门控：用 `#if VERSION_BETWEEN(V2R1, VERSION_NEWEST)` / `#endif` 包夹实现体。

**4. 输出推断函数挂接**（原文 Output Size/Dtype Functions 节）：
```yaml
size: npu_operator_out_size(input, param)     # 声明于 KernelNpuOutputSize.h
dtype: infer_dtype(input, param)              # 声明于 KernelNpuOutputDtype.h
```
C++ 模板需参见 `references/guides/cpp-guide.md` "Output Size Functions" 节。

**5. 特殊 schema 必填字段**（原文 Special Schema Requirements 节）：
```yaml
# 触发条件之一：name 以 new_ 开头 / 以 _like 结尾 / 含 tensor_options 但无 Tensor 输入
- func: empty_with_format(int[] size, *, ScalarType? dtype=None, int acl_format=2) -> Tensor
  dispatch:
    CompositeExplicitAutograd: empty_with_format

# 触发条件之一：name 含 rand / dropout / 含 generator 参数
- func: dropout_with_byte_mask(Tensor self, float p, bool train) -> Tensor
  tags: nondeterministic_seeded
```

**6. 启用 NZ 格式走 op_api 路径**（原文 Configuration Fields 节）：
在 YAML 条目中添加 `internal_format_opapi` 字段，使原本默认 dispatch 到 `acl_op` 的算子改走 `op_api`。

**7. 最佳实践命令**（原文 Best Practices 节）：
> 在进入 C++ 编写前，先比对 YAML `func:` 签名与 `_def.cpp`、`.md` 文档的一致性 —— 早期捕获签名不匹配。

**8. 故障排查**：
原文 Troubleshooting 节为占位段（标注"Accumulate from cases"），**未涉及**具体命令或修复步骤。
