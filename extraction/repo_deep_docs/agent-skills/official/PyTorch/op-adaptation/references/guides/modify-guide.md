# Modify Mode Guide

> 仓 `agent-skills` · 路径 `official/PyTorch/op-adaptation/references/guides/modify-guide.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/agent-skills/official/PyTorch/op-adaptation/references/guides/modify-guide.md

# Modify Mode Guide 深度解读

## 【定位】

本文档定义了「Modify Mode（修改模式）」的标准工作流,用于对 PyTorch op-adaptation 体系下**已存在的算子(op)**进行修改（增删变体 / 接口调整 / 反向绑定 / Bug 修复等）。通过 M-discover → M-scope → M-gate → M-execute 四阶段,确保改动范围受控、可追溯,与「Create Mode」形成互补。

## 【技术要点】

1. **M-discover(发现阶段)**: 通过 7 条 `grep` 命令在固定文件类别中检索算子名(`op_plugin_functions.yaml` / `derivatives.yaml` / `KernelNpuOutputSize.{cpp,h}` / `_meta_registrations.py` / `test_fake_tensor.py` / `torch_npu_OpApi_schema_all.json` / `allowlist_for_publicAPI.json` / `op_plugin/ops/opapi/`)——**不含版本后缀**(例如查 `npu_moe_token_permute_grad` 而非 `_v2`)。
2. **特殊处理**: 当 `derivatives.yaml` 被命中,必须额外输出「forward → backward」绑定方向,并以交互方式询问用户是否将新版反向变体绑定到 forward(决定是否进入影响范围)。
3. **M-scope(范围推导)**: 基于「修改描述 + grep 结果」对照「Change Type 表」推导受影响文件,并在 6 类变更类型(Add variant — forward / backward / standalone、Interface change、Backward supplement、Bug fix)中选择;**必须经用户确认**后再生成轻量 CHECKLIST。
4. **M-gate(门禁检查)**: 执行前必须运行 `git status --porcelain`;若存在未提交改动则告警「Working directory has uncommitted changes. Recommend committing or stashing before proceeding.」
5. **M-execute(执行阶段)**: 按「File → Step mapping」表将每个受影响文件映射到对应步骤(C-yaml / C-derivatives / C-cpp / C-meta / C-test / C-baseline / C-docs);无论影响范围如何,**始终执行** C-verify、C-build、C-summary 三个步骤。
6. **范围控制(Skip/扩展约束)**: Create Mode 专属步骤 C-parse、C-confirm、C-constraints 在 Modify Mode 下**全部跳过**;若执行过程中发现新依赖,**必须暂停并重新推导范围**——禁止自行扩大改动。

## 【关键机制与数据】

- **四阶段流水线**(原文): `M-discover(发现)` → `M-scope(范围推导)` → `M-gate(门禁)` → `M-execute(执行)`,全部以 `M-` 前缀命名,区别于 Create Mode 的 `C-` 步骤,体现「Modify」工作流的整体一致性。
- **检索的 8 类文件**:
  - `op_plugin/config/op_plugin_functions.yaml`
  - `op_plugin/config/derivatives.yaml`
  - `op_plugin/utils/KernelNpuOutputSize.cpp` / `.h`
  - `op_plugin/python/meta/_meta_registrations.py`
  - `test/core_tests/test_fake_tensor.py`
  - `test/core_tests/torch_npu_OpApi_schema_all.json`
  - `test/allowlist_for_publicAPI.json`
  - `op_plugin/ops/opapi/`(递归,`--include="*.cpp"`)
- **状态报告符号**: ✅ 表示命中;❌ 表示未找到(对 `allowlist_for_publicAPI.json` 而言反向算子"未出现是预期行为")。
- **示例改动**(原文): 接口从 `tokens Tensor` 改为 `tokens_size_0 int + tokens_dtype ScalarType`,波及 5 个文件(`op_plugin_functions.yaml`、`KernelNpuOutputSize.cpp/h`、`_meta_registrations.py`、`test_fake_tensor.py`、`torch_npu_OpApi_schema_all.json`)。
- **门禁命令**: `git status --porcelain`,原文称若「有未提交改动」则告警。

## 【表格解读】

### 表 1: Change Type → Files to modify(变更类型与受影响文件)

| Change type | Trigger | Files to modify |
|-------------|---------|-----------------|
| Add variant — forward | New forward op variant (`_v2`, `_v3`) | yaml(forward+backward) + meta + output_size + test + json + derivatives(new binding for new backward) |
| Add variant — backward | New backward op variant | yaml + meta + output_size + test + json + derivatives(rebind forward if confirmed in scope analysis) |
| Add variant — standalone | New variant not in autograd chain | yaml + meta + output_size + test + json |
| Interface change | Parameter types/count changes | yaml + meta + output_size + cpp(if hand-written) + test + json + derivatives(if bound) |
| Backward supplement | Add/modify backward binding | derivatives + yaml(if backward op not registered) + test + json |
| Bug fix | Logic correction, no interface change | cpp + test(possibly) |

逐行解读:
- **Add variant — forward**: 新增正向变体(如 `_v2`/`_v3`)时,既要注册新正向,也要连带处理其反向与反向绑定,改动范围最广。
- **Add variant — backward**: 仅新增反向变体,需要在 `derivatives.yaml` 中重新绑定 forward→backward(前提是用户在 M-scope 阶段确认)。
- **Add variant — standalone**: 新变体不在 autograd 链中(纯前向或工具函数),无需触碰 `derivatives.yaml`。
- **Interface change**: 参数类型或数量发生变化,需同步 C++ 实现(若手写)、yaml、meta、test、json 与(若已绑定)反向绑定。
- **Backward supplement**: 补全或修改反向绑定,可能同时需要在 yaml 中注册反向 op。
- **Bug fix**: 仅逻辑修正,不改接口,通常仅 C++ 与(必要时)test,改动面最小。

### 表 2: File → Step mapping(影响范围文件 → 执行步骤)

| Impact scope file | Execute Step |
|-------------------|-------------|
| `op_plugin_functions.yaml` | C-yaml |
| `derivatives.yaml` (new binding) | C-derivatives |
| `derivatives.yaml` (rebind, backward variant) | C-derivatives (rebind section) |
| `KernelNpuOutputSize.cpp/h` or `*KernelNpuOpApi.cpp` | C-cpp |
| `_meta_registrations.py` | C-meta |
| `test_fake_tensor.py` or new UT file | C-test |
| `torch_npu_OpApi_schema_all.json` / `allowlist_for_publicAPI.json` | C-baseline |
| Existing doc page changed | C-docs (remind manual update) |
| New variant (new operator name) | C-docs (op-apidoc for new page) |

逐行解读:
- `op_plugin_functions.yaml` 始终映射到 **C-yaml** 步骤。
- `derivatives.yaml` 在「新建绑定」与「rebind(反向变体场景)」时都走 C-derivatives,但前者是新增条目,后者使用专门的 Rebind 子节(对应 `derivatives-guide.md` 的 Rebind 部分)。
- C++ 类文件(`KernelNpuOutputSize.cpp/h` 或 `*KernelNpuOpApi.cpp`)统一映射到 **C-cpp**。
- Meta 注册文件 `_meta_registrations.py` 对应 **C-meta**。
- 测试文件 `test_fake_tensor.py` 或新建 UT 文件对应 **C-test**。
- 静态 schema 与白名单 JSON 文件对应 **C-baseline**。
- 已存在的文档页改动时,**C-docs 只需提醒手工更新**;若引入全新算子名,则需要新建文档页(op-apidoc)。

### 表 3: Mode-Specific Differences(Create Mode vs Modify Mode)

| Step | Create Mode | Modify Mode |
|------|-------------|-------------|
| C-parse, C-confirm | Parse .md+_def.cpp, confirm with user | **Skip** — replaced by M-discover~M-execute |
| C-yaml | New entry | Edit existing or append variant |
| C-derivatives | New binding | Update existing or add new |
| C-derivatives (rebind) | — | Rebind forward→backward when adding backward variant (see `derivatives-guide.md` Rebind section) |
| C-cpp | New .cpp file | Edit existing or add function (e.g., `_out_size` in `KernelNpuOutputSize.cpp`) |
| C-constraints | Constraint self-check | **Skip** (no .md parsing in modify mode) |
| C-meta | New @impl registration | Edit existing or append |
| C-test | New test file + class | Append methods to existing class |
| C-docs | New doc page | Remind manual update; if new variant → new page |
| C-baseline | New entries | Append new or update existing |

逐行解读:
- **C-parse / C-confirm**: 仅 Create Mode 需要解析 `.md` 与 `_def.cpp` 与用户确认;Modify Mode 由 M-discover~M-execute 取代。
- **C-yaml**: Create 是新建条目;Modify 是编辑既有条目或追加变体。
- **C-derivatives**: Create 新建绑定;Modify 更新既有或新增;rebind 子步骤为 Modify Mode 独有,需参考 `derivatives-guide.md`。
- **C-cpp**: Create 创建新 `.cpp` 文件;Modify 编辑现有或追加函数(如在 `KernelNpuOutputSize.cpp` 中添加 `_out_size`)。
- **C-constraints**: 仅 Create Mode 使用(对 `.md` 约束做自检);Modify Mode 因无 `.md` 解析,跳过。
- **C-meta**: Create 新建 `@impl` 注册;Modify 编辑既有或追加。
- **C-test**: Create 新建测试文件与类;Modify 仅向现有类中追加方法。
- **C-docs**: Create 新建文档页;Modify 仅提醒手工更新;若引入新变体则需新建页面。
- **C-baseline**: Create 添加新条目;Modify 追加新条目或更新既有。

## 【公式解读】

原文无公式。

## 【关联】

文档中显式引用了以下上下游资源(原文):

- **`references/templates/checklist-template.md`** 的 "Modify Mode" 章节 —— M-scope 用户确认后,基于此模板生成轻量 CHECKLIST。
- **`references/examples/README.md`** —— M-scope 阶段用于检索与本次变更类型或受影响文件匹配的案例,如有命中则向用户呈现关键决策与坑点作为参考(即使无匹配也正常推进工作流)。
- **`SKILL.md`** —— 每个 C-* 步骤的「模式相关说明」需查阅此文件(M-execute 末尾)。
- **`derivatives-guide.md`** 的 **Rebind 部分** —— Modify Mode 独有的 C-derivatives (rebind) 子步骤指向此处。
- **C-parse / C-confirm / C-constraints** —— 属于 Create Mode,在 Modify Mode 中被跳过。
- **always-required 三步骤** —— C-verify(签名校验)、C-build(重新编译)、C-summary(集成摘要)与具体影响范围解耦,无论改什么文件都必须执行。

## 【使用方法】

**Modify Mode 启用流程**(按原文顺序):

1. **M-discover**: 依次执行 7 条 grep 命令(去掉版本后缀),将结果整理成「operator_name status in codebase」表格呈现给用户;若 `derivatives.yaml` 被命中,额外输出绑定方向并以交互方式询问是否将新版反向变体绑定到 forward(此答案决定 M-scope 是否纳入 `derivatives.yaml`)。
2. **M-scope**: 基于修改描述与 grep 结果对照「Change Type 表」确定变更类型与受影响文件,向用户呈现具体清单(示例形式见原文 `Confirm scope? Any additions?` 段)等待确认;确认后生成轻量 CHECKLIST(`references/templates/checklist-template.md`),并尝试匹配 `references/examples/README.md` 中的同类案例作为参考。
3. **M-gate**: 执行 `git status --porcelain` 检查工作区是否干净;若有未提交改动,原文给出告警文案「Working directory has uncommitted changes. Recommend committing or stashing before proceeding.」。
4. **M-execute**: 按「File → Step mapping」表逐项映射到 C-* 步骤,在 Modify 模式下执行(编辑/追加);不论影响范围如何,**始终执行 C-verify、C-build、C-summary**;若过程中发现新依赖,**暂停并重新推导 M-scope**。

**模式差异要点**(配置/行为切换):

- C-parse、C-confirm、C-constraints 在 Modify Mode 中**被跳过**(由 M-discover~M-execute 取代,且无 `.md` 解析)。
- C-derivatives (rebind) 是 **Modify Mode 独有**子步骤(对应新增反向变体的 re-binding 场景)。
- 修改受限于已确认的 M-scope,**禁止擅自扩展**(原文:「Scope Control: ONLY modify files in the confirmed impact scope. Do NOT expand beyond what M-scope derived.」)。
