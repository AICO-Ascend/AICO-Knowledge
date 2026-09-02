# Derivatives Configuration Guide

> 仓 `agent-skills` · 路径 `official/PyTorch/op-adaptation/references/guides/derivatives-guide.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/agent-skills/official/PyTorch/op-adaptation/references/guides/derivatives-guide.md

# Derivatives Configuration Guide 深度解读

---

## 【定位】

这篇文档是昇腾 PyTorch op-adaptation 体系中 **`derivatives.yaml` 的配置指南**,解决的是"如何在前向算子与其反向梯度算子之间建立正确的绑定关系,以使 autograd 能正确调度反向计算"这一核心问题。

---

## 【技术要点】

1. **绑定文件结构**: `derivatives.yaml` 在 `all_version` 下通过 `backward` 列表组织条目;每条目的 `name:` 必须与 `op_plugin_functions.yaml` 中 forward 的 `func:` 行精确一致,`version:` 必须落在 forward 的 `op_api` 版本范围内。
2. **多输出可微性控制**: 通过 `output_differentiability: [true, false, true]` 数组声明哪些 forward 输出参与 autograd;非可微输出不会出现在 `grads[]` 中;省略时全部默认可微。
3. **占位符体系**: 包括 `grad`(下游来的梯度)、`result0/1/...`(forward 返回值)、`grads[0]/[1]/...`(多输出梯度分量)、`<param_name>`、`<param>.sym_sizes()`、`<param>.sym_size(N).expect_int()`、`<param>.scalar_type()`、`non_differentiable`、`auto_linear` 共 9 类。
4. **两种 Rebind 模式**: Pattern A(同名异参——简单替换函数名)、Pattern B(老接口用 Tensor 传元数据,新接口改用标量——需要在 derivatives.yaml 内联提取表达式),以及 Rebind 的三种跳过场景。
5. **生成清单 6 步法**: 验证 backward 注册 → 匹配 forward 签名 → 正确占位符 → 匹配版本范围 → 按字母序插入 → 用 FakeTensor C-test 验证 dispatch。
6. **标量提取规则**: 用 `sym_size(N)`(而非 `size(N)`)以兼容动态 shape;用 `.expect_int()` 把 `c10::SymInt` 解包为 `int64_t`;用 `.scalar_type()` 取得 `ScalarType`;含 `?`、`:`、空格的公式需用双引号整段包裹。

---

## 【关键机制与数据】

**1. 工作原理(原文)**

- 文档明确定义: "`derivatives.yaml` binds forward operators to their backward gradient formulas. Each entry maps a forward operator's input parameters to backward operator calls."
- 双文件协同: `op_plugin_functions.yaml` 注册算子**接口**(`func:`),`derivatives.yaml` 告诉 autograd **调用哪个** backward 算子来计算哪个输入的梯度。
- **互依关系**(原文):
  - "Backward op registered in yaml but no derivatives binding → autograd won't call it"
  - "Derivatives references an unregistered backward op → runtime error"

**2. 数据流(原文,基于 `_npu_dropout` 模板)**

```
forward: _npu_dropout(Tensor self, float p) -> (Tensor, Tensor)
                  ↓ 保存
       result0 = 输出 Tensor, result1 = mask Tensor
                  ↓ autograd 调度
backward formula: npu_dropout_backward(grad, result1, p)
                  ↑
        grad ← 下游层流入的反向梯度
```

**3. 性能/内存数据(原文)**

- 原文有数据点:**"avoiding the backward kernel from holding full Tensor references, saving memory"**——指 Pattern B 通过把 Tensor 替换为标量后,反向 kernel 不再持有整张 Tensor,从而节省显存。

**4. 验证机制(原文)**

- "Test with FakeTensor: Verify the binding works in C-test (op-test) — FakeTensor mode exercises the derivatives dispatch path"
- Rebind Pattern A 验证步骤: "`forward → backward → assert grad is not None and shape matches`"

---

## 【表格解读】

### 表格 1: 文件角色对比(原文逐字还原)

| File | Role |
|------|------|
| `op_plugin_functions.yaml` | Registers forward AND backward operator **interfaces** (both need `func:` entries) |
| `derivatives.yaml` | Binds forward ↔ backward — tells autograd WHICH backward op to call for each forward input gradient |

**逐行解读**:
- 第一行:`op_plugin_functions.yaml` 负责"接口注册"——即算子的函数原型声明,forward 与 backward 算子都需要 `func:` 条目。
- 第二行:`derivatives.yaml` 负责"绑定关系"——仅描述 forward 与 backward 之间的对应,不声明接口本身。
- 两文件必须**同时存在**,autograd 才能工作(见下方"互依关系"小节)。

### 表格 2: 占位符参考(原文逐字还原)

| Placeholder | Meaning | Example |
|-------------|---------|---------|
| `grad` | Incoming gradient from downstream layers | Always available |
| `result0`, `result1`, ... | N-th return value of the forward operator | `result1` = second output Tensor |
| `grads[0]`, `grads[1]`, ... | N-th gradient component from multi-output returns | Used with `-> (Tensor, Tensor)` |
| `<param_name>` | Forward input parameter, referenced by name | `self`, `alpha`, `dim` |
| `<param>.sym_sizes()` | Symbolic sizes of a Tensor input | Used when backward needs shape info |
| `<param>.sym_size(N).expect_int()` | N-th dimension value as int | Used when backward needs a specific dim |
| `<param>.scalar_type()` | dtype of a Tensor input | Used when backward output dtype matches input |
| `non_differentiable` | Marks a parameter that doesn't need gradient | `index: non_differentiable` |
| `auto_linear` | PyTorch handles the gradient automatically | `result: auto_linear` |

**逐行解读**:
- `grad`:在 backward 表达式中**总是可用**,表示上游传下来的梯度。
- `result0/1/...`:索引从 0 开始,对应 forward 返回值列表;`_npu_dropout` 中 `result1` 就是 mask。
- `grads[0]/[1]/...`:仅用于 forward 返回 `-> (Tensor, Tensor, ...)` 的多输出场景,按位取不同分量的梯度。
- `<param_name>`:直接以 forward 形参名引用输入(如 `self`、`alpha`、`dim`),多参数共享同一反向时可逗号并列(如 `self, gtboxes:`)。
- `sym_sizes()` 与 `sym_size(N).expect_int()`:用于在 backward 中获取动态 shape,后者额外把 `SymInt` 拆成普通 int64。
- `scalar_type()`:获取 dtype,通常用于 backward 输出 dtype 需与输入对齐的场景(如 Pattern B 中的 `tokens.scalar_type()`)。
- `non_differentiable`:该输入不需要梯度,如 `gather` 中的 `index`。
- `auto_linear`:让 PyTorch 自动处理(线性算子),无需自定义 backward,如 `result: auto_linear`。

### 表格 3: Rebind 触发场景(原文逐字还原)

| Scenario | Action |
|----------|--------|
| Adding backward variant whose forward already has a derivatives binding | **Rebind** — update formula to call new variant |
| Adding forward variant | **New binding** — see Entry Templates above |
| Adding standalone variant (not in autograd chain) | **Skip** |
| Operator has no derivatives binding | **Skip** |

**逐行解读**:
- 第 1 行:如果已有 derivatives 绑定又新增 backward 变体,**必须** Rebind,把公式指向新变体。
- 第 2 行:新增 forward 变体走"新绑定"流程,使用 Entry Templates。
- 第 3 行:standalone 变体(不在 autograd 链路中)直接跳过。
- 第 4 行:原算子本就没有 derivatives 绑定的,也不需要 Rebind。

### 表格 4: Pattern 选择(原文逐字还原)

| Old vs New | Pattern |
|------------|---------|
| Same parameter list, different function name | **Pattern A: Simple Replacement** |
| Old uses Tensor for metadata, new uses scalar instead | **Pattern B: Tensor→Scalar Replacement** |

**逐行解读**:
- Pattern A 适用于"参数完全一致、只是函数名变了"的纯改名场景。
- Pattern B 适用于"老接口用 Tensor 传 shape/dtype/dim 等元数据,新接口改用标量"的场景,需要在 derivatives.yaml 公式里内联提取表达式。

### 表格 5: Tensor→Scalar 提取映射(原文逐字还原)

| Old param | New param | Extraction expression |
|-----------|-----------|----------------------|
| `tokens` (Tensor) | `size_0` (int) | `tokens.sym_size(0).expect_int()` |
| `tokens` (Tensor) | `dtype` (ScalarType) | `tokens.scalar_type()` |
| `indices` (Tensor) | `topK` (int) | `(indices.dim() == 1) ? 1 : indices.sym_size(1).expect_int()` |

**逐行解读**:
- `tokens` → `size_0`:用 `sym_size(0)` 取第 0 维再 `expect_int()` 转 int64。
- `tokens` → `dtype`:直接 `scalar_type()` 提取 dtype。
- `indices` → `topK`:当 `indices` 是 1 维时取 1,否则取 `sym_size(1)` 的 int 值——典型的三目表达式,展示了动态 shape + 条件分支的复合用法。

---

## 【公式解读】

### 公式 1:单输出单可微输入(原文)

```yaml
- name: fast_gelu(Tensor self) -> Tensor
  self: npu_fast_gelu_backward(grad, self)
  version: [v2.1, newest]
```

**符号含义**:
- `name:` 前向算子 schema,必须与 `op_plugin_functions.yaml` 中 `func:` 一致。
- `self:` 表示对前向输入 `self` 计算梯度,左键是参数名,右键是反向调用表达式。
- `npu_fast_gelu_backward(grad, self)` 中的 `grad` 占位下游传入梯度,`self` 直接引用前向输入张量。
- `version: [v2.1, newest]` 表示从 v2.1 到最新版本都启用。

### 公式 2:多输出 + 使用 forward 中间结果(原文)

```yaml
- name: _npu_dropout(Tensor self, float p) -> (Tensor, Tensor)
  self: npu_dropout_backward(grad, result1, p)
  version: [v2.1, newest]
```

**符号含义**:
- `-> (Tensor, Tensor)` 双输出,`result0` 是输出 Tensor,`result1` 是 dropout 所需的 mask Tensor。
- `p` 是普通标量参数,直接透传。
- 文档解释:`result1` is the mask Tensor from forward's second output — used because it carries the dropout pattern.

### 公式 3:多输入可微(原文)

```yaml
- name: _npu_ciou(Tensor self, Tensor gtboxes, bool trans=False, int mode=0) -> (Tensor, Tensor)
  self, gtboxes: npu_ciou_backward(grad, self, gtboxes, result1, trans, mode)
  version: [v2.1, newest]
```

**符号含义**:
- 左侧 `self, gtboxes:` 用逗号并列,表示这两个输入**共享同一个反向调用**。
- 右侧表达式按新接口的**位置参数**顺序排布:`grad` → `self` → `gtboxes` → `result1`(forward 第二输出)→ `trans` → `mode`。
- 默认值 `=False`、`=0` 不需要在 derivatives 表达式中重复出现,直接透传。

### 公式 4:从 Tensor 提取标量元数据(原文)

```yaml
- name: npu_moe_token_permute(Tensor tokens, Tensor indices, ...) -> (Tensor, Tensor)
  tokens: "npu_moe_token_permute_grad_v2(grad, result1, tokens.sym_size(0).expect_int(), tokens.scalar_type(), (indices.dim() == 1) ? 1 : indices.sym_size(1).expect_int(), padded_mode)"
  version: [v2.1, newest]
```

**符号含义**(逐项):
- `grad` → 第一实参(对应新接口的 `grad`)。
- `result1` → 第二实参(对应新接口的 `result1`)。
- `tokens.sym_size(0).expect_int()` → 第三实参(int 类型的 `size_0`,从 tokens 第 0 维提取)。
- `tokens.scalar_type()` → 第四实参(ScalarType 类型的 `dtype`)。
- `(indices.dim() == 1) ? 1 : indices.sym_size(1).expect_int()` → 第五实参(int 类型的 `topK`,1 维时为 1,否则取第 1 维)。
- `padded_mode` → 第六实参(布尔透传)。
- 整段用 `"..."` 双引号包裹,因为表达式含 `?`、`,` 和空格。
- 文档解释:This pattern extracts `tokens.shape[0]`, `tokens.dtype`, and `indices.shape[1]` as scalar arguments — avoiding the backward kernel from holding full Tensor references, saving memory.

### 公式 5:多输出梯度分量(原文)

```yaml
- name: some_op(...) -> (Tensor, Tensor, Tensor)
  input1, input2: backward_op(grads[0], grads[1], input1, input2)
  version: [v2.1, newest]
```

**符号含义**:
- `grads[0]`、`grads[1]` 分别引用 forward 多输出对应的**两个梯度分量**。
- `input1, input2` 共享同一反向调用,二者都要算梯度。
- 文档解释:`grads[0]` and `grads[1]` reference the different gradient components from the forward's multi-output return.

### 公式 6:含 `output_differentiability` 的多输出(原文)

```yaml
- name: npu_multi_output_op(Tensor x1, Tensor x2) -> (Tensor, Tensor, Tensor)
  output_differentiability: [true, false, true]   # Outputs 0 and 2 are differentiable
  x1, x2: npu_multi_output_backward(grads[0], x1, x2, grads[2])
  version: all_version
```

**符号含义**:
- `output_differentiability: [true, false, true]` 声明 3 个输出中,**输出 0 与 2 参与 autograd,输出 1 不参与**。
- 后续 `grads[]` 数组因此**只有 grads[0] 与 grads[2]** 两个分量,没有 grads[1]——非可微的输出 1 不进入梯度数组。
- 文档原文三条要点:
  - `[true, false, true]` → outputs 0 and 2 are differentiable, output 1 is not
  - Non-differentiable outputs are excluded from the `grads[]` array in the backward expression
  - If omitted, all outputs default to differentiable

### 公式 7:非可微参数(原文)

```yaml
- name: gather(Tensor self, int dim, Tensor index, bool sparse_grad=False) -> Tensor
  self: npu_gather_backward(grad, self.sym_sizes(), dim, index, sparse_grad)
  index: non_differentiable
  version: all_version
```

**符号含义**:
- `self` 行:正常反向表达式,其中 `self.sym_sizes()` 把 self 的形状作为参数传入 backward。
- `index: non_differentiable` 声明 `index` 参数不参与梯度计算,不进入反向调用。
- `sparse_grad=False`、`dim`、`index` 透传作为 backward 的位置参数。

---

## 【关联】

文档中显式提及的上下游模块与特性:

1. **`op_plugin_functions.yaml`**(上游/平级):
   - 提供 forward 与 backward 算子的 `func:` 接口定义。
   - `derivatives.yaml` 的 `name:` 必须与其中 forward 的 `func:` 精确匹配。
   - 两文件协同才能使 autograd 生效(详见"互依关系")。

2. **backward operator variants(如 `_grad_v2`)**(下游):
   - 触发 Rebind 流程,需更新 forward 的 derivatives 公式以调用新变体。
   - 文档给出 Pattern A(简单替换)与 Pattern B(Tensor→Scalar 替换)两类处理路径。

3. **`op_api:` 字段**(版本范围):
   - `version:` 必须匹配 forward 算子的 `op_api:` 范围。

4. **`FakeTensor` 模式 / C-test (op-test)**(验证链路):
   - "FakeTensor mode exercises the derivatives dispatch path"——用于验证 binding 是否正确触发 dispatch。

5. **PyTorch 原生机制**:
   - `auto_linear`:借助 PyTorch 的自动求导处理线性算子,无需自定义 backward。
   - `c10::SymInt`:通过 `.expect_int()` 解包为 `int64_t`。
   - 动态 shape 支持:用 `sym_size` 而非 `size`。

6. **文档内部的章节间关联**:
   - "Generation Checklist" 是新增条目的标准流程。
   - "Rebind" 是修改既有条目的标准流程。
   - "Placeholder Reference" 是 Expression 中所有符号的总词典。
   - "Entry Templates" 提供 6 类典型 yaml 模板,直接复用。

7. **内部链接**:原文文末标注"内部链接: (无)"——本指南不依赖其他指南文档的跳转。

---

## 【使用方法】

### 1. 新增条目流程(原文 Generation Checklist 6 步)

1. **Verify backward op is registered**: 确认 backward 算子(`npu_xxx_grad`)已在 `op_plugin_functions.yaml` 中有 `func:` 条目。
2. **Match forward signature**: `name:` 字段必须与 `op_plugin_functions.yaml` 中的 `func:` 行完全一致(参数名、类型、顺序)。
3. **Use correct placeholders**: 用 `grad` 引用下游梯度,用 `result0/1` 引用 forward 输出。
4. **Match version range**: `version:` 必须与 forward 算子的 `op_api:` 范围一致。
5. **Sort alphabetically**: 在 `backward:` 列表中按字母序插入。
6. **Test with FakeTensor**: 用 C-test(op-test)中的 FakeTensor 模式验证 dispatch 通路。

### 2. Rebind Pattern A(原文 4 步)

1. Read current binding — `grep forward operator name in derivatives.yaml`
2. Replace function name — 例 `npu_xxx_grad(...)` → `npu_xxx_grad_v2(...)`
3. Present diff and confirm
4. Verify after build — `forward → backward → assert grad is not None and shape matches`

### 3. Rebind Pattern B(原文 5 步)

1. **Read Current Binding**: `grep forward operator name in derivatives.yaml` 找到现有公式。
2. **Identify Tensor→Scalar Map**: 对比新旧签名,把每个被删的 Tensor 映射到新标量(详见原文 `npu_moe_token_permute_grad` → `_v2` 的映射例子)。
3. **Generate Extraction Expressions**: 按规则生成提取表达式:
   - 用 `sym_size(N)`(而非 `size(N)`)以兼容动态 shape。
   - 用 `.expect_int()` 解包 `c10::SymInt → int64_t`。
   - 用 `.scalar_type()` 取 `ScalarType`。
   - 条件表达式用 `(condition) ? value_if_true : value_if_false`。
4. **Build New Formula**: 按新变体 `func:` 签名的位置顺序拼接;含 `?`、`,` 或空格时整段用双引号包裹。
5. **Present Diff and Confirm**(原文在此处截断,以 `Side-by-side diff. User e` 结束——后续内容原文未给出)。

### 4. 配置项清单(原文涉及)

- `all_version: [v2.1, v2.2, ...]` — 文件级适用版本。
- `name:` — forward 算子 schema,必匹配 `op_plugin_functions.yaml` 的 `func:`。
- `output_differentiability:` — 多输出场景下声明可微输出数组。
- `version: [v2.1, newest]` / `version: all_version` — 条目级版本范围。
- `non_differentiable`、`auto_linear` — 参数级 / 输出级标记。

### 5. 命令与工具(原文涉及)

- `grep forward operator name in derivatives.yaml` — 查找既有绑定。
- "Verify after build — `forward → backward → assert grad is not None and shape matches`" — 验证流程。
- C-test(op-test)中的 FakeTensor 模式 — 自动化验证 dispatch 链路。

---

> **说明**:文档最后一段在 "Side-by-step diff. User e" 处被截断,因此 Pattern B 第 5 步"Present Diff and Confirm"的完整细节**原文未涉及**,以上解读仅基于已给出的内容,未做臆测。
