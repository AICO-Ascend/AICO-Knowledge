# 算子替换设计文档生成 playbook

> 仓 `agent-skills` · 路径 `official/Common/ascend-transformer-boost/skills/atb-aclnn-operator-replacement-designer/references/replacement-design-playbook.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/agent-skills/official/Common/ascend-transformer-boost/skills/atb-aclnn-operator-replacement-designer/references/replacement-design-playbook.md

# 一体化深度解读：算子替换设计文档生成 playbook

---

## 【定位】

这篇文档为 `atb-aclnn-operator-replacement-designer` 技能的「延伸阅读」手册，**解决如何按规模分级（轻量 4 节 vs 完整 7 章）生成「ATB OPS 算子 → ACLNN 算子」替换设计文档**的问题，强制覆盖规模检测、路径校验、WebFetch 阻断规则、工作流、用户确认检查点等执行约束。

---

## 【技术要点】

1. **规模分级二元判定**：调用时必须先用 `find <ATB_REPO_PATH>/src/ops/ops_infer/<op_type>/ -name '*_aclnn_runner.{h,cpp}'` 检测目标算子的 ACLNN Runner 文件是否存在；若 `*_aclnn_runner.cpp` 已存在且已通过 `REG_RUNNER_TYPE` 注册 → 轻量模板（4 节），否则 → 完整模板（7 章）。
2. **强制路径约束**：执行前必须从用户处获取 `<CANN_PATH>`（如 `/usr/local/Ascend/ascend-toolkit/latest`，校验 `set_env.sh`）与 `<ATB_REPO_PATH>`（如 `{your working path}ascend-transformer-boost`，校验目录存在），任一无效即 `exit 1`。
3. **WebFetch 失败阻断规则**：ATB 与 ACLNN 两个接口文档 URL 任一访问失败（404/403/超时）必须立即停止并打断用户；ACLNN Runner 代码存在不可替代官方文档，禁止从 `*_aclnn_runner.cpp` 或 `infer_op_params.h` 反推接口。
4. **四级参数映射分类**：直接映射 / 计算映射（如 `beginNormAxis → normalizedShape`）/ 废弃参数 / 新增参数；轻量版仅保留「文档信息 + 需求简述 + 参数映射 + 约束 + 风险」4 节，跳过完整版的需求详情、规格说明（DFX）、开发自测、实现方案、结论章节。
5. **Human-in-the-Loop 检查点**：设计文档生成后必须保存至 `{WORKING_DIR}/{op_type}_replacement_design.md`（op_type 小写，如 `swigluquant`、`layernorm`），并走 5 项确认表（完整版）/ 3 项确认表（轻量版），未拿到 "确认通过" 禁止进入 `atb-csv-testcase-generator` 阶段。
6. **标准 ACLNN Runner 模式**：所有 runner 继承 `AclnnRunner` 基类，必须实现 `BuildAclnnVariantPack` / `SetAclNNWorkspaceExecutor` / `LaunchAclnnKernel` / `LoadMethod` 四方法，并用 `REG_RUNNER_TYPE` 宏注册；参考实现见 `references/softmax_aclnn_runner_reference.md`。

---

## 【关键机制与数据】

- **工作流链路（原文）**：`规模检测（是否存在 *_aclnn_runner.cpp）→ 接口文档分析 → 参数映射建立 → 按模板等级生成文档`。每阶段完成后需对照「执行结果」章节的检查点表确认状态。
- **轻量模板章节裁剪规则（原文）**：轻量版只保留 4 节，跳过完整版的「需求详情、规格说明（DFX）、开发自测、实现方案、结论」；文档仍保存至 `{WORKING_DIR}/{op_type}_replacement_design.md`，但标注为轻量版。
- **完整模板 7 章结构（原文）**：需求详情 / 算子IR与参数配置 / 规格说明（DFX、规格约束、功能冲突）/ 开发自测（功能测试、反例测试、性能测试）/ 实现方案 / 风险评估与应对策略 / 结论。
- **风险评估示例条目（原文轻量版）**：设备检测逻辑错误（低 → 参考 Gather/Split/Repeat 分发模式）/ 变体路由错误（中 → 在 CreateRunner 加严格 layerType/quantType 过滤）/ 非目标设备回归（低 → 非 910B/950 设备保持 OPS 路径不变）。
- **设备适配策略（原文）**：替换目标设备为 **910B / 950**，非 910B/950 设备保持 OPS 路径不变；950 上仅支持「受支持的变体」。
- **性能数据**：原文未提供具体性能数字。
- **代码结构路径（原文）**：`src/ops/ops_infer/{op_type}/{op_type}_aclnn_runner.h/cpp`，其中 `{op_type}` 为算子类型小写。

---

## 【表格解读】

### 表 1：分级标准表（原文）

| 场景 | 判断条件 | 模板等级 | 说明 |
|------|---------|---------|------|
| **已有 Runner 接入** | `*_aclnn_runner.cpp` 已存在且已注册 `REG_RUNNER_TYPE` | **轻量模板** (4 节) | 仅需参数映射 + 约束 + 风险 |
| **全新迁移** | `*_aclnn_runner.cpp` 不存在 | **完整模板** (7 章) | 需要完整设计文档 |

**逐行解读**：
- 第 1 行「已有 Runner 接入」：判定条件双重约束 — 文件物理存在 + 已通过 `REG_RUNNER_TYPE` 宏注册，触发 4 节轻量流程；工作目标是参数映射、约束提取、风险评估三件事即可。
- 第 2 行「全新迁移」：当 runner 文件不存在时，走 7 章完整模板，覆盖需求 → IR → 规格 → 测试 → 实现 → 风险 → 结论全生命周期。

### 表 2：规模检测报告话术表（原文伪表，嵌入代码块）

| 项目 | 值（占位） |
|------|-----------|
| 算子 | {OpType} |
| ATB 仓库 | <ATB_REPO_PATH> |
| 检测 | {op_type}_aclnn_runner.{h,cpp} [✅ 已存在 / 不存在] |
| 结论 | 使用 [轻量模板 / 完整模板] 生成设计文档。预计生成 [4 节 / 7 章] 文档。 |

**逐行解读**：这是统一向上汇报的「标准话术」模板，向用户透明披露检测过程与模板选择依据，避免黑盒决策。

### 表 3：轻量版参数映射表骨架（原文）

| ATB参数 | ACLNN参数 | 映射类型 | 说明 |
|---------|-----------|----------|------|
| [从已有 runner 代码提取] | [从已有 runner 代码提取] | [直接/计算] | |

**逐行解读**：表头已固定为「ATB→ACLNN 双向 + 映射类型 + 说明」四列，列值需人工从已有 runner 与官方文档中提取填充；映射类型枚举限定为「直接 / 计算」两类（轻量版不引入废弃/新增分类）。

### 表 4：WebFetch 失败行为规则表（原文）

| 场景 | 行为 |
|------|------|
| WebFetch 两个 URL 均成功 | 继续分析 |
| WebFetch 任一 URL 失败 | **立即停止，打断用户** |
| WebFetch 返回 404/403/超时 | **立即停止，打断用户** |
| ACLNN Runner 已存在于代码仓 | **仍需文档成功** — 代码不能替代官方文档 |

**逐行解读**：
- 第 1 行：双 URL 全成功是唯一进入下一步的绿灯。
- 第 2-3 行：任何形式的访问失败都触发硬阻断，强制用户介入。
- 第 4 行（最关键的「禁止行为」）：即便代码仓已有 runner 实现，也不得以本地代码替代官方接口文档，禁止从 `*_aclnn_runner.cpp` 反推参数、禁止从 `infer_op_params.h` 推断约束。

### 表 5：参数映射类型处理方式表（原文）

| 映射类型 | 处理方式 |
|---------|----------|
| 直接映射 | 参数名和含义完全一致，直接映射 |
| 计算映射 | 根据公式或规则进行转换（如beginNormAxis → normalizedShape） |
| 废弃参数 | 识别不再需要的参数并说明 |
| 新增参数 | 识别新增参数并说明默认值或计算方式 |

**逐行解读**：四类映射完整覆盖迁移场景。文档特别举例「计算映射」的典型转换 `beginNormAxis → normalizedShape`，这是 ATB 与 ACLNN 范式差异的代表性案例（轴向偏移 vs 标准化形状）。

### 表 6：轻量版确认检查表（原文）

| 检查项 | 说明 | 用户确认 |
|--------|------|----------|
| 参数映射关系正确 | ATB→ACLNN 映射准确 | [ ] |
| 规格约束清晰 | 数据类型、参数约束完整 | [ ] |
| 风险评估完整 | 风险项和应对策略充分 | [ ] |

**逐行解读**：轻量版仅 3 项；它假定 runner 已存在、规格已固化，因此省略「测试用例设计」「实现方案可行性」等较重的确认项。

### 表 7：完整版确认检查表（原文）

| 检查项 | 说明 | 用户确认 |
|--------|------|----------|
| 参数映射关系正确 | 第 2.3 节参数映射表准确反映了 ATB→ACLNN 的映射关系 | [ ] |
| 风险评估合理 | 第 6 章识别的风险项和应对策略完整 | [ ] |
| 实现方案可行 | 第 5 章实现方案符合 ATB ACLNN Runner 标准模式 | [ ] |
| 测试用例设计可行 | 第 4 章测试用例覆盖全面，可进入 CSV 设计阶段 | [ ] |
| 规格约束清晰 | 第 3 章规格约束明确，便于编写反例测试 | [ ] |

**逐行解读**：完整版扩展到 5 项，对应完整模板的「参数映射 / 风险 / 实现 / 测试 / 规格」五章节。检查表末尾强约束「未拿到用户确认前禁止进入 CSV 用例设计阶段」，确保 Human-in-the-Loop。

---

## 【公式解读】

**原文无数学公式**。文档包含的命令式伪代码片段如下，保留原式逐字解读：

**伪代码片段 ①：规模检测命令**

```bash
find <ATB_REPO_PATH>/src/ops/ops_infer/<op_type>/ -name '*_aclnn_runner.cpp' -type f 2>/dev/null
find <ATB_REPO_PATH>/src/ops/ops_infer/<op_type>/ -name '*_aclnn_runner.h' -type f 2>/dev/null
```

- 符号解读：`<ATB_REPO_PATH>` 为仓库根路径占位符；`<op_type>` 为算子类型目录占位符（如 `softmax`）；通配符 `*_aclnn_runner.{cpp,h}` 匹配同名 runner 实现；`2>/dev/null` 抑制 `find` 的权限错误输出。
- 作用：在 `ops_infer` 推理算子目录下递归查找目标算子的 ACLNN Runner 头/源文件，决定走轻量模板还是完整模板。

**伪代码片段 ②：路径校验脚本**

```bash
if [ -z "$CANN_PATH" ] || [ ! -f "$CANN_PATH/set_env.sh" ]; then
    echo "ERROR: CANN_PATH 未设置或无效，请用户提供。"
    exit 1
fi
if [ -z "$ATB_REPO_PATH" ] || [ ! -d "$ATB_REPO_PATH" ]; then
    echo "ERROR: ATB_REPO_PATH 未设置或无效，请用户提供。"
    exit 1
fi
```

- 符号解读：`$CANN_PATH` 为 CANN Toolkit 安装路径（必检 `set_env.sh` 环境脚本存在性）；`$ATB_REPO_PATH` 为 ATB 源码仓库路径（必检为目录）。
- 作用：双路径前置校验，确保两者均有效才允许继续；任一缺失即以 `exit 1` 终止。这不是数学公式，是强制性 shell 守卫。

---

## 【关联】

- **下游技能**：`atb-csv-testcase-generator` — 文档明确「确认通过后，将进入 Phase 2: CSV 用例设计阶段」「下一步调用: atb-csv-testcase-generator」，定位为算子替换流水线的 Phase 2。
- **参考实现文件**：`references/softmax_aclnn_runner_reference.md` — 提供 `softmax_aclnn_runner` 完整头/源文件实现，作为新 ACLNN Runner 编码的范本。
- **基类与宏**：依赖基类 `AclnnRunner`，注册宏 `REG_RUNNER_TYPE`，四方法契约 `BuildAclnnVariantPack` / `SetAclNNWorkspaceExecutor` / `LaunchAclnnKernel` / `LoadMethod`。
- **上游技能**：`atb-aclnn-operator-replacement-designer` — 本文档是其延伸阅读，描述该技能的执行约束。
- **同级参考算子**：`Gather` / `Split` / `Repeat`（轻量版风险评估明确「参考已有 runner 的分发模式」作为基线参考实现）。
- **CANN 安装目录**：`$ASCEND_TOOLKIT_HOME/opp/*/op_proto/` — WebFetch 失败时用户可提供的备选文档来源（算子 protobuf 定义）。
- **样板生成目录**：所有设计文档统一沉淀至 `{WORKING_DIR}/{op_type}_replacement_design.md`，形成可追溯的 working_files 存档。

---

## 【使用方法】

**原文有的启用流程**：
1. 用户调用 `atb-aclnn-operator-replacement-designer` 技能 → 系统首先执行规模检测（`find` 命令）确定模板等级。
2. 用户必须提供两项路径：`<CANN_PATH>`（指向 CANN 安装根目录，必须含 `set_env.sh`）、`<ATB_REPO_PATH>`（指向 ATB 仓库根）。
3. 用户必须提供两项接口文档 URL：ATB 算子接口文档链接、ACLNN 算子接口文档链接；可选提供算子类型名称（如 LayerNorm）。
4. WebFetch 抓取两个 URL；任一失败立即中断用户并请求人工提供文档。
5. 按已选模板生成文档（4 节或 7 章），存入 `{WORKING_DIR}/{op_type}_replacement_design.md`。
6. 走确认检查表（轻量 3 项 / 完整 5 项）；用户回复"确认通过"后，才可调用 `atb-csv-testcase-generator` 进入 Phase 2。

**配置项 / 命令（原文摘录）**：
- 检测命令：`find <ATB_REPO_PATH>/src/ops/ops_infer/<op_type>/ -name '*_aclnn_runner.{cpp,h}' -type f 2>/dev/null`
- 路径校验：`if [ -z "$CANN_PATH" ] || [ ! -f "$CANN_PATH/set_env.sh" ]` / `if [ -z "$ATB_REPO_PATH" ] || [ ! -d "$ATB_REPO_PATH" ]`
- 输出路径：`{WORKING_DIR}/{op_type}_replacement_design.md`（`op_type` 小写）
- 工具集成：`WebFetch`（抓文档）、`Read`（读源码）、`Write`（生成文档）、`Edit`（微调文档）。
