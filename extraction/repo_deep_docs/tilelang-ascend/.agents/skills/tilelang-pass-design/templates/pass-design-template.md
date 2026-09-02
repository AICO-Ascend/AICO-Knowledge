# {Pass 名称} Pass 设计文档

> 仓 `tilelang-ascend` · 路径 `.agents/skills/tilelang-pass-design/templates/pass-design-template.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/tilelang-ascend/.agents/skills/tilelang-pass-design/templates/pass-design-template.md

【定位】

这是一份尚未绑定具体 Pass 的标准化设计模板，用于描述一个 Pass 从阶段选择、IR 变换、C++/Python 实现、Pipeline 集成到测试交付的完整设计与落地流程。

【技术要点】

1. **先确定 Pass 的基本属性**：需要填写 Pass 名称、功能、解决问题，并从 `{修改 IR / 收集信息 / 验证 IR}`、`{平台无关 / Ascend 特定}` 以及 `{Lowering / 合法化 / 内存 / 流水线 / 同步 / 信息收集 / 其他}` 中明确类型；这些内容在原文中均为占位符，尚未形成最终选型。

2. **按阶段和 Pipeline 位置选型**：Pass 只能归属 **Phase 1: LowerAndLegalize** 或 **Phase 2: OptimizeForTarget**。模板给出的 Phase 2 示例位于 `AscendStorageRewrite(is_npu)`（步骤 13）之后、`tir.transform.UnrollLoop`（步骤 14）之前；Phase 1 示例位于 `LowerTileOp`（步骤 9）和 `LegalizeVectorizedLoop`（步骤 10）之间，实际步骤号为 `{步骤 X}`。

3. **以 PrimFunc 属性的上下游契约组织数据流**：上游可以从 PrimFunc 的 attrs 读取 `{buffer scope}`、`{buffer_shapess}`、`{address_map}` 等数据，例如：
   - `{buffer scope}` 来自 `AscendInferBufferScope`，Phase 1 步骤 1，通过 `f->GetAttr<Map<...>>(...)` 获取。
   - `{buffer_shapess}` 来自 `CollectBufferShapes`，Phase 1 步骤 8。
   - `{address_map}` 来自 `AscendMemoryPlanning`，Phase 2 步骤 20。  
   变换后可通过 `f->attrs[...]` 或 `WithAttrs` 向下游提供 `{output_attr}` 等结果；具体类型和 PassA 均未确定。

4. **核心变换遵循“遍历—匹配—变换—写回”链路**：伪代码规定依次调用 `VisitStmt_()`、`MatchPattern()`、`TransformStmt()` 和 `UpdateAttrs()`；遍历特定 IR 节点，检查 buffer scope、op type 等条件，生成新语句或收集信息，最后将结果放回 `PrimFunc f` 的 attrs 中。

5. **实现上以 PrimFunc Pass 和可选配置为中心**：
   - 修改 IR 时可继承 `IRMutatorWithAnalyzer`。
   - 只收集信息、不修改 IR 时可使用 `StmtExprVisitor`。
   - 简单变换可使用 `StmtExprMutator`。  
   实际父类尚未选择。
   - Pass 通过 `CreatePrimFuncPass` 注册，示例优先级为 `0`，名称形式为 `"tl.{Pass名称}"`。
   - Python 层通过 `_ffi_api.{Pass名称}()` 返回注册后的 Pass。

6. **质量和交付要求完整**：需要覆盖功能、依赖、边界和性能测试，并处理 attrs 缺失、IR 结构不符及 Pass 冲突；实现顺序共列出 7 项，当前只有设计文档标记为完成，C++、Wrapper、配置、Pipeline 和测试仍待完成。

【关键机制与数据】

- **原文:** 整体机制是先分析 Pass 的功能归属、数据依赖、输出供给和语义范围，再决定它属于 Phase 1 还是 Phase 2。输出如果供 Ascend 同步、内存规划等后续 Pass 使用，则其属性类型和生成时机必须与下游契约一致。

- 原文数据流图为：

```text
Phase 1 / Phase 2 前序 Pass
    ↓
    输出: {数据A}, {数据B}
    ↓
[{Pass名称}] ← 本 Pass
    ↓
    输出: {数据C}, {数据D}
    ↓
Phase X 后续 Pass
```

该图表示：Pass 接收前置阶段产生的 `{数据A}`、`{数据B}`，完成变换后输出 `{数据C}`、`{数据D}`，再交给后续 Pass。图中所有 Pass 名称、属性名和阶段名都是占位符，没有给出真实数据内容或类型。

- **原文:** 建议的函数级入口为：

```cpp
static PrimFunc Substitute(PrimFunc f, PassContext ctx)
```

它读取 `f` 上可能存在的输入属性，创建变换器并执行 `MutateFunc(f)`；如需输出，则使用：

```cpp
new_f = new_f.WithAttrs({{"output_attr", output_data}});
```

最终返回变换后的 `PrimFunc`。这意味着设计重点是单个函数属性的读写和函数体内 IR 的变换，而不是在模板中直接操作 `IRModule`。

- **原文:** Pass 注册回调的形式为：

```cpp
auto pass_func = [=](PrimFunc f, IRModule m, PassContext ctx) {
  return {类名}::Substitute(std::move(f), ctx);
};
```

其中 `m` 被注册接口接收，但在所示 `Substitute` 调用中没有被继续使用；这说明该模板面向 `PrimFunc` 级 Pass，`IRModule` 仅作为 TVM Pass 回调签名的一部分出现。

- **原文:** 可选配置键为：

```cpp
tl.{pass_name}
```

读取方式为：

```cpp
ctx->GetConfig<Bool>(k{Pass名称}Config, Bool(false)).value();
```

当值为 `false` 时执行：

```cpp
if (!config_enabled) {
  return f;  // 配置为 false 时跳过该 Pass
}
```

因此原文描述的默认行为是关闭 Pass，而不是默认启用；`true` 时具体执行什么变换仍需由类实现决定。

- **原文:** 性能部分没有给出任何实测编译时间、吞吐量、延迟或加速比。`{时间阈值}`、`{吞吐量/延迟}` 以及 5.4 节整张性能测试表都只是待填写项，不能视为已有性能结论。

【表格解读】

以下按原文逐字还原所有关键表格；其中 `{...}`、`...` 均为模板占位符，不代表最终选型或真实数据。

### 1.4 Pass 类型

| 类型 | 说明 |
|------|------|
| **IR 变换类型** | {修改 IR / 收集信息 / 验证 IR} |
| **平台范围** | {平台无关 / Ascend 特定} |
| **优化类别** | {Lowering / 合法化 / 内存 / 流水线 / 同步 / 信息收集 / 其他} |

逐行解读：

- **IR 变换类型**：需要在“修改 IR”“收集信息”“验证 IR”中选择其一，模板未指定实际类型。
- **平台范围**：需要判断是平台无关 Pass 还是 Ascend 特定 Pass，目前未选。
- **优化类别**：可从 Lowering、合法化、内存、流水线、同步、信息收集或其他中选择，目前未选。

### 2.2 选型理由

| 原则 | 分析结果 |
|------|----------|
| **功能归属** | {如：属于硬件优化，应放在 Phase 2} |
| **数据依赖** | {如：需要 buffer_shapess（来自 Phase 1），可放在 Phase 2} |
| **输出供给** | {如：产生 address_map，供 AscendSyncInsert 使用，必须在 Phase 2} |
| **语义范围** | {如：Ascend 特定优化，放在 Phase 2} |

逐行解读：

- **功能归属**：判断 Pass 的主要作用是否属于目标硬件优化；示例倾向于硬件优化进入 Phase 2，但非最终结论。
- **数据依赖**：如果依赖 Phase 1 产生的 `buffer_shapess`，通常应安排在对应生产 Pass 之后。
- **输出供给**：如果输出 `address_map` 并供 `AscendSyncInsert` 使用，则必须位于该下游 Pass 之前。
- **语义范围**：Ascend 特有语义通常与 Phase 2 的目标优化阶段相符，但实际仍需填写具体分析。

### 2.4 上游依赖

| 数据名称 | 产生 Pass | 阶段 | 获取方式 |
|----------|-----------|------|----------|
| {buffer scope} | `AscendInferBufferScope` | Phase 1 步骤 1 | `f->GetAttr<Map<...>>(...)` |
| {buffer_shapess} | `CollectBufferShapes` | Phase 1 步骤 8 | `f->GetAttr<Map<Var, Array<PrimExpr>>>(...)` |
| {address_map} | `AscendMemoryPlanning` | Phase 2 步骤 20 | `f->GetAttr<Map<...>>(...)` |
| ... | ... | ... | ... |

逐行解读：

- `{buffer scope}`：由 `AscendInferBufferScope` 在 Phase 1 步骤 1 产生，通过 `f->GetAttr<Map<...>>(...)` 从 PrimFunc 属性读取；具体 Map 类型尚未给出。
- `{buffer_shapess}`：由 `CollectBufferShapes` 在 Phase 1 步骤 8 产生，模板展示其类型为 `Map<Var, Array<PrimExpr>>`。
- `{address_map}`：由 `AscendMemoryPlanning` 在 Phase 2 步骤 20 产生，同样通过 PrimFunc 的 Map 属性读取。
- `...`：表示还可以继续增加依赖项，不是实际数据。

### 2.4 下游供给

| 数据名称 | 使用 Pass | 阶段 | 传递方式 |
|----------|-----------|------|----------|
| {output_attr} | {PassA} | Phase X | `f->attrs[...]` |
| ... | ... | ... | ... |

逐行解读：

- `{output_attr}`：由当前 Pass 产生，交给占位符 `{PassA}` 在 `{Phase X}` 使用，通过 `f->attrs[...]` 传递。
- `...`：表示允许继续声明其他输出依赖，不代表已有下游 Pass。

### 4.1 父类选择

| 父类 | 适用场景 | 本 Pass 选择 |
|------|----------|--------------|
| `IRMutatorWithAnalyzer` | 修改 IR 结构 | {选择理由} |
| `StmtExprVisitor` | 收集信息、不修改 IR | {选择理由} |
| `StmtExprMutator` | 简单 IR 变换 | {选择理由} |

逐行解读：

- `IRMutatorWithAnalyzer`：适用于需要修改 IR 结构的 Pass；当前选择理由未填写。
- `StmtExprVisitor`：适用于只遍历并收集信息、不修改 IR 的 Pass；当前选择理由未填写。
- `StmtExprMutator`：适用于较简单的 IR 变换；当前选择理由未填写。

### 4.2 核心方法

| 方法名 | 功能 | 关键逻辑 |
|--------|------|----------|
| `Substitute()` | Pass 入口 | 读取 attrs → 执行变换 → 返回 PrimFunc |
| `VisitStmt_(NodeType)` | 处理特定节点 | {匹配 → 变换逻辑} |
| `MatchPattern()` | 模式匹配 | {检查条件} |
| `TransformStmt()` | 执行变换 | {生成新 IR} |
| `UpdateAttrs()` | 更新 attrs | {设置输出数据} |

逐行解读：

- `Substitute()`：作为 Pass 入口，依次读取属性、执行变换并返回新的 `PrimFunc`。
- `VisitStmt_(NodeType)`：负责访问特定 `NodeType`；具体节点类型和匹配、变换规则尚未确定。
- `MatchPattern()`：检查目标 IR 模式是否成立；条件尚未填写。
- `TransformStmt()`：在模式匹配成功后执行变换并生成新 IR。
- `UpdateAttrs()`：用于设置供后续 Pass 使用的输出属性，输出数据尚未定义。

### 5.1 功能测试

| 测试项 | 测试内容 | 验证方法 |
|--------|----------|----------|
| {基础功能} | {变换后的 IR 是否正确} | {检查 attrs / IR 结构} |
| {输入依赖} | {能否正确读取上游 attrs} | {设置 mock attrs 测试} |
| {输出供给} | {能否正确设置下游 attrs} | {检查 attrs 是否可被后续 Pass 读取} |

逐行解读：

- 基础功能：检查变换后的 attrs 或 IR 结构是否符合预期。
- 输入依赖：构造 mock attrs，确认 Pass 能读取上游属性。
- 输出供给：确认 Pass 设置的属性可以被后续 Pass 正确读取。

### 5.2 依赖测试

| 测试项 | 测试内容 |
|--------|----------|
| **上游缺失** | 当上游 attrs 缺失时，Pass 是否正确处理（报错 / 跳过） |
| **顺序错误** | 当 Pass 执行顺序错误时，编译是否失败 |

逐行解读：

- **上游缺失**：验证缺少必要属性时应报错还是跳过，具体策略未确定。
- **顺序错误**：验证当前 Pass 被放到依赖 Pass 之前时，编译流程能否暴露顺序错误。

### 5.3 边界测试

| 测试项 | 测试内容 |
|----------|----------|
| **空 IR** | 当 IR 为空或无目标节点时，Pass 是否正确处理 |
| **极端数据** | 当 attrs 包含极端值（空 map、超大 size）时，Pass 是否正确处理 |

逐行解读：

- **空 IR**：验证没有目标节点时，Pass 应采用何种行为尚未确定。
- **极端数据**：检查空 map 和超大 `size` 的处理方式，原文没有规定阈值或预期结果。

### 5.4 性能测试

| 测试项 | 测试内容 | 指标 |
|--------|----------|------|
| {编译时间} | Pass 是否显著增加编译时间 | {时间阈值} |
| {生成代码性能} | Pass 是否改善生成代码性能 | {吞吐量/延迟} |

逐行解读：

- 编译时间：计划判断 Pass 是否显著增加编译时间，但阈值未给出。
- 生成代码性能：计划检查优化效果，但原文没有基线、目标值或实测吞吐量/延迟。
- 因而该表是测试计划，不是性能对比结果。

### 6.2 常见错误

| 错误 | 触发场景 | 影响 | 解决方案 |
|------|----------|------|----------|
| {attrs 缺失} | {上游 Pass 未执行} | {编译失败} | {检查 Pass 顺序} |
| {IR 结构不符} | {输入 IR 不符合预期} | {变换失败} | {添加前置检查} |
| ... | ... | ... | ... |

逐行解读：

- attrs 缺失：上游 Pass 未执行时可能导致编译失败，建议检查 Pass 顺序；实际错误策略未确定。
- IR 结构不符：输入不符合预期模式时可能导致变换失败，建议增加前置检查。
- `
