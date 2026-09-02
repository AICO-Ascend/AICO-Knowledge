# Compatibility Baseline Registration Guide

> 仓 `agent-skills` · 路径 `official/PyTorch/op-adaptation/references/guides/compatibility-guide.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/agent-skills/official/PyTorch/op-adaptation/references/guides/compatibility-guide.md

# 一体化深度解读：Compatibility Baseline Registration Guide

## 【定位】

这篇文档定义了在昇腾（Ascend）`op-adaptation` 体系中**新增算子后向兼容性基线（Compatibility Baseline）注册的标准化流程**，规定了在两个 JSON 追踪文件中如何登记算子签名（`op_api` 与 `func` 双层签名）、如何打版本标签、以及如何通过兼容性测试脚本进行验证，从而保证跨版本（v2.7 → v2.8 → newest）的 API 稳定性可被持续监控。

## 【技术要点】

1. **双文件、双签名的注册模型**：每个新算子必须同时在 `test/core_tests/torch_npu_OpApi_schema_all.json` 中登记两个签名——`op_api:`（Python 公开 API 层）与 `func:`（底层 C++/YAML 注册算子层）；并同步在 `test/allowlist_for_publicAPI.json` 中追加算子名到合适的版本列表，二者共同构成"兼容性基线"。

2. **三种版本标签语义**：`"v2.1"`/`"v2.5"`/… 等具体版本号锁定某一发布版本；`"newest"` 表示"最后一个具名编号标签之后的所有版本"；`"all_version"` 表示"全部版本"。版本标签以数组形式挂在签名条目下，例如 `"version": ["v2.7", "v2.8", "newest"]`。

3. **签名字符串的精确性要求**：`op_api` 条目须为可被 `inspect.signature(torch_npu.npu_{operator_name})` 还原的签名串；新版本可带显式类型注解如 `"torch_npu.npu_{operator_name}(Tensor x, *, int mode=0) -> Tensor"`。`func` 条目则须直接读取 `op_plugin/config/op_plugin_functions.yaml` 中该算子的 `func:` 行。签名错误将直接破坏兼容性比对。

4. **字母序插入位置约束**：在 `torch_npu_OpApi_schema_all.json` 中，`op_api:` 条目按字母序排列于所有 `op_api` 组内；`func:` 条目同样独立按字母序排列。在 `allowlist_for_publicAPI.json` 中，算子名追加至对应列表末尾（`all_version` 或 `v2.x`）。顺序错误不会触发测试失败但属于流程违规。

5. **版本列表选择规则**：新算子默认应归入 `allowlist_for_publicAPI.json` 的 `all_version` 列表（最常见）；仅当算子"仅在特定版本存在"时才放入 `v2.7`/`v2.8` 等具名版本列表，这是一条隐式但关键的语义分支。

6. **验证闭环机制**：注册完成后必须执行 `python test/core_tests/test_compatibility.py` 进行兼容性测试，并按 Checklist 将 6 项内容（两条签名条目、版本标签、allowlist 条目、字母序、结果报告到 `CHECKLIST.md`）逐条勾选，最终结果需回写到 `CHECKLIST.md`，形成可追溯的闭环。

## 【关键机制与数据】

**整体数据流**：

```
新增算子实现
    │
    ├──① Python 绑定层签名（inspect.signature 或 Python 绑定源）
    │     │
    │     └─→ 写入 op_api: 条目到 torch_npu_OpApi_schema_all.json
    │
    ├──② 底层 YAML 注册行（op_plugin/config/op_plugin_functions.yaml 中 func: 行）
    │     │
    │     └─→ 写入 func: 条目到 torch_npu_OpApi_schema_all.json
    │
    ├──③ 算子名追加到 allowlist_for_publicAPI.json 的对应版本列表
    │
    └──④ 运行 test/core_tests/test_compatibility.py 进行比对验证
              │
              └─→ 结果回写到 CHECKLIST.md
```

**关键工作原理**：兼容性测试 `test_compatibility.py` 通过读取这两个 JSON 文件，将"当前代码中实际存在的算子签名"与"基线文件中声明的签名及版本"进行差异比对。任何未登记的新算子、签名漂移（参数名/默认值/类型注解变更）、或版本标签缺失，都会被检测为兼容性破坏。`op_api` 与 `func` 的双签名机制使得测试既能感知 Python 层 API 表面（用户可见），又能感知底层算子注册表面（依赖实际调用）。

**示例算子的具体参数（原文以 `npu_swiglu_quant` 为完整样例）**：参数签名 `"Tensor x, *, Tensor? group_index=None, int dim=-1, float alpha=1.702, float limit=7.0, float bias=1.0, bool interleaved=True, ScalarType? dst_type=None"`，版本标签覆盖 `["v2.7", "v2.8", "newest"]`。原文未给出具体的兼容性测试阈值或性能数据。

## 【表格解读】

**原文表格（逐字还原）**：

| Tag | Meaning |
|-----|---------|
| `"v2.1"`, `"v2.5"`, etc. | Specific version |
| `"newest"` | All versions after the last numbered tag |
| `"all_version"` | All versions |

**逐行解读**：

- **第一行 `"v2.1"`, `"v2.5"`, etc. / Specific version**：表示一个具名、具编号的发布版本锚点（如 v2.1、v2.5）。示例中实际使用过的还有 `"v2.7"` 和 `"v2.8"`，说明基线目前覆盖到 v2.8 及其后续。此类标签的作用是"把签名钉死在某一具体版本上"，适合用于记录签名在该版本诞生时的初始形态。

- **第二行 `"newest"` / All versions after the last numbered tag**：表示"最后一个具名编号标签之后的所有版本"，这是一个**滚动锚点**。其语义依赖于"最后一个编号标签"这一上下文——基线维护者需自行保证列表中至少存在一个具名版本锚点，之后用 `"newest"` 兜底覆盖未来所有新版本，从而避免每发一个版本都要手动改基线。

- **第三行 `"all_version"` / All versions**：无差别覆盖全部版本（包括历史与未来），语义最"宽"。但此标签**主要出现在 `allowlist_for_publicAPI.json` 的版本列表键名中**（如 `"all_version": ["existing_op", ...]`），而非 `version` 数组中——这两个 JSON 文件对 `all_version` 的承载角色不同：前者作为版本维度键名，后者主要用于语义覆盖声明。文档未明确禁止在 `version` 数组中使用 `all_version`，但从上下文看，`version` 数组的标准用法是 `具名版本 + newest`。

## 【公式解读】

原文无公式（既无 LaTeX 公式也无伪代码公式）。JSON 条目的结构虽形似声明式数据定义，但不属于数学或算法公式范畴。

## 【关联】

文档未提供任何内部链接（文末内部链接字段为"无"）。但从文中提及的上下游可建立以下关联关系：

- **上游依赖**：`op_plugin/config/op_plugin_functions.yaml`（提供 `func:` 签名的唯一权威来源）—— 注册 `func` 条目前必须先确认该算子已在 op_plugin YAML 中注册。
- **测试执行链**：`test/core_tests/test_compatibility.py` 是验证节点，其读取两个 JSON 基线文件进行差异比对；测试结果需回写到 `CHECKLIST.md` 形成审计痕迹。
- **下游消费方**：算子的 Python 公开 API（`torch_npu.npu_*`）与底层 C++ 算子实现之间的契约通过基线文件被冻结。任何对 Python 绑定签名或 YAML func 行的修改都必须同步更新基线，否则 `test_compatibility.py` 会报错。
- **横向能力**：与"op-adaptation"仓库内其他算子开发流程（如算子注册、Python 绑定生成）配合——本指南不涉及算子实现本身，只负责"算子实现完成后向兼容性追踪体系登记"这一收尾环节。
- **与 SKILL 仓库定位的关系**：本指南属于 `official/PyTorch/op-adaptation/references/guides/` 下的一份参考指引（guide），是 AI Agent 在辅助完成昇腾 PyTorch 算子适配时所需的标准化知识之一。

## 【使用方法】

**启用方式 / 配置项 / 命令**（原文有则照录）：

1. **新增 `op_api:` 条目到** `test/core_tests/torch_npu_OpApi_schema_all.json`，按字母序插入 `op_api` 组：
   ```json
   "op_api: torch_npu.npu_{operator_name}(*args, **kwargs)": {
       "version": ["v2.7", "v2.8", "newest"]
   }
   ```
   带类型注解的新版本写法：
   ```json
   "op_api: torch_npu.npu_{operator_name}(Tensor x, *, int mode=0) -> Tensor": {
       "version": ["v2.8", "newest"]
   }
   ```

2. **新增 `func:` 条目**到同一文件，按字母序插入 `func` 组，签名直接抄自 `op_plugin/config/op_plugin_functions.yaml` 中该算子的 `func:` 行：
   ```json
   "func: npu_{operator_name}(Tensor x, *, ScalarType? dst_type=None) -> Tensor": {
       "version": ["v2.7", "v2.8", "newest"]
   }
   ```

3. **追加算子名到** `test/allowlist_for_publicAPI.json` 的 `torch_npu.all_version` 列表末尾（默认且最常用）；若算子仅特定版本存在，则追加至对应 `v2.x` 列表末尾：
   ```json
   {
     "torch_npu": {
       "all_version": ["existing_op", ..., "npu_{operator_name}"],
       ...
     }
   }
   ```

4. **获取签名的两条途径**：
   - `op_api:` —— 执行 `inspect.signature(torch_npu.npu_{operator_name})` 或查阅 Python 绑定源码。
   - `func:` —— 读取 `op_plugin/config/op_plugin_functions.yaml` 中该算子对应的 `func:` 行。

5. **验证命令**（注册完成后必跑）：
   ```bash
   python test/core_tests/test_compatibility.py
   ```

6. **Checklist 6 项必勾选**：
   - 已添加 `op_api:` 条目
   - 已添加 `func:` 条目
   - 两条目的版本标签正确
   - 已添加算子名到 `allowlist_for_publicAPI.json`（对应版本列表）
   - 条目已在各自组内按字母序排列
   - 验证结果已报告至 `CHECKLIST.md`

7. **故障排查**：原文仅以 "(Accumulate from cases.)" 一句占位，**原文未涉及**具体故障场景与处置方法——这是一份"活文档"，要求后续实践者将真实案例追加到 Troubleshooting 章节。
