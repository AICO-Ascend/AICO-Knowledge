# 历史案例索引（API 一致性工作流）

> 仓 `agent-skills` · 路径 `official/PyTorch/api-consistency/knowledge/history.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/agent-skills/official/PyTorch/api-consistency/knowledge/history.md

# 深度解读：官方 PyTorch API 一致性工作流——历史案例索引

---

## 【定位】

本文件是 API 一致性工作流 **Step 3 定位阶段**的"精简索引 + 高频根因速查"，帮助助手在面对 API 一致性问题时，按"结论类型 / 高频根因 / DTS 单号 / 症状关键词"四个维度提示用户自行对照 `case-library.md` 与 `dts-reproduce-cases.md`，避免自动抓取内网表或编造命中行。

---

## 【技术要点】

1. **A2/A3/A5 纪律合规约束**：助手在 Step 3 **不自动抓取**内网表、**不编造**命中行（"原文中明确写入"用法说明，行为硬约束）。
2. **结论类型 8 类分桶**（§一）：环境/链路/调度、功能/拦截/逻辑、真精度、单算子（去重后 aclnn=1）、组合类精度（aclnn>1）、确定性、分布式/通信（分支 B）、无法复现。
3. **高频根因 8 类**（§二）：含测试用例输入不一致（~25 例）、ReduceSum 归约精度（~15 例）、小算子拼接误差（~10 例）、Inplace+确定性（~6 例）、ACLNN 算子版本/缺失（~8 例）、PTA 适配 Bug（~10 例）、ATK 工具 Bug（~6 例）、通信/分布式配置（~8 例）。
4. **DTS 单号索引表**（§三）：3 条已收录案例（`DTS2026042118463` / `DTS2026042061660` / issue-5 端到端范例），各列包含 Gate 0 分支、结论大类、外部链接。
5. **症状关键词检索表**（§四）：8 类症状关键词 → 优先 Skill / reference + 已收录案例。
6. **新增案例 6 项必填字段**：DTS 单号 + Gate 0 分支 + API 名、表象与证据签名、根因、结论类型、关键命令（含 `-mt/-to/-sd` 若适用）、产物路径。
7. **flow 衔接 4 阶段**（§六）：flow-atk 一屏决策卡壳 / analyze-functional 归类犹豫 / analyze-precision 定位 / report 5.end 历史参考段。

---

## 【关键机制与数据】

- **历史结论分布**（原文：约 130 例，来自 `case-library §一`）：
  - 非问题 ~25
  - 用例/测试问题 ~30
  - 算子问题（转第三方）~18
  - PTA 代码修复 ~25
  - 精度标准/配置问题 ~12
  - CANN 修复 ~8
  - ATK 工具问题 ~6
  - 环境/版本问题 ~5

- **工作流位置**：Step 3 定位阶段 → 助手提示用户自查 → 用户粘贴/确认 → report 5.end 写"DTS 单号 + 本节链接"。
- **Gate 0 分支**：ATK（A）/ 非 ATK（B），影响后续 `reproduce -mt/-to`、`torchrun-functional` 等命令选型。
- **去重后 aclnn 计数**：决定走 `single-op early-stop → report`（aclnn=1）还是 `precision Dump`（aclnn>1）。
- **历史案例库规模**：`case-library.md` 收纳约 130 条；原 a2a3 712 行案例库整编。
- **DTS 工作流验证**：经 DTS 流程验证的"现代案例"沉淀于 `dts-reproduce-cases.md`。

---

## 【表格解读】

### 表格 1：§一 结论类型速查（原文逐字还原）

| 结论类型 | 典型特征 | API-consistency 出口 |
|---------|---------|---------------------|
| 环境 / 链路 / 调度 | xlsx `FAILED` + 连接/timeout/OOM；`-mt/-to` 后 SUCCESS | functional / reproduce；批次见 batch_summary |
| 功能 / 拦截 / 逻辑 | `运行结果=FAILED` + aclnn/断言/NotImplemented | functional → 单算子 or 组合 |
| 真精度 | `SUCCESS` + `*精度通过=false` | analyze-precision → Dump / UT |
| 单算子（转第三方） | 去重后 aclnn **= 1**（正或反独立） | single-op early-stop → report |
| 组合类精度 | 去重后 aclnn **> 1** | precision Dump |
| 确定性 | 50 次循环不一致 / 工单 `-p` 确定性脚本 Fail | determinism_check + 结单专段 |
| 分布式 / 通信（分支 B） | HCCL / timeout / SOC 探测 / stderr 退出码 | torchrun-functional 四源 |
| 无法复现 | ≤3 轮熔断或用户确认环境不可对齐 | report 待办 + 环境侧条目 |

**逐行解读**：
- **环境/链路/调度**：以 xlsx `FAILED` 为入口信号，伴随连接/timeout/OOM，重跑命令 `-mt/-to` 后转 SUCCESS 即可确认；出口为 `functional` 或 `reproduce`，批量场景汇总到 `batch_summary`。
- **功能/拦截/逻辑**：表现为 `运行结果=FAILED` 并伴随 aclnn/断言/NotImplemented，需进一步拆解到单算子或组合。
- **真精度**：xlsx 显示 `SUCCESS` 但 `*精度通过=false`，需进入 `analyze-precision` 流程并 Dump 或 UT。
- **单算子（转第三方）**：去重后 aclnn 计数恰为 1，无论正向或反向独立成立都走 single-op 早停。
- **组合类精度**：aclnn 计数 > 1，进入 precision Dump 以定位多个算子中具体出错的环节。
- **确定性**：以 50 次循环结果不一致或工单 `-p` 确定性脚本 Fail 为识别符，需 `determinism_check` + 结单专段。
- **分布式/通信（分支 B）**：涉及 HCCL、timeout、SOC 探测、stderr 退出码，走 `torchrun-functional` 四源链路。
- **无法复现**：≤3 轮熔断或用户确认环境不可对齐，落到 report 待办 + 环境侧条目。

---

### 表格 2：§二 高频根因模式（原文逐字还原）

| # | 模式 | 特征 | 解决 | 影响面 |
|---|------|------|------|--------|
| 3.1 | **测试用例输入不一致**（最常见，~25 例） | GPU 与 NPU 独立生成输入，md5/二进制不同 | 加 `-sd` 同步输入，或改用统一输入生成逻辑 | 精度 / 确定性 / 分布式 |
| 3.2 | **ReduceSum / 归约精度**（~15 例） | 反向 broadcast 触发 reduce_sum，CPU/NPU 浮点归约实现差异致二进制不一致 | 改双标杆或 `cv_fused_double_benchmark` | Tensor.add/div/fill_、where 等反向 |
| 3.3 | **小算子拼接累计误差**（~10 例） | API 由多个小算子拼接，fp16/bf16 误差逐步累积 | 已有结论，按 Float16/Bfloat 精度泛化处理 | sin / rsqrt / pow 等反向 |
| 3.4 | **Inplace + 确定性冲突**（~6 例） | `inplace=True` 修改输入，多轮执行结果不一致 | 用例避免原地修改，或 ATK clone 输入 | leaky_relu / logit_ / embedding / ctc_loss |
| 3.5 | **ACLNN 算子版本/缺失**（~8 例） | CANN 包未含对应 aclnn 算子或版本不匹配走错路径 | 更新 CANN 版本或等待算子合入 | chunk_cat / TripletMarginLoss / cdist |
| 3.6 | **PTA 适配代码 Bug**（~10 例） | meta 注册 / 参数透传 / 校验逻辑 / shape 推导有误 | 改 op-plugin 或 pytorch 仓代码 | grouped_matmul / fusion_attention / LSTM / histc / linear |
| 3.7 | **ATK 工具 Bug**（~6 例） | ATK 在确定性测试中处理 inplace / 梯度累计 / 输入读取有缺陷 | 更新 ATK 或 workaround | logit_ / stack 反向 / amp_update_scale |
| 3.8 | **通信/分布式用例配置**（~8 例） | node.yaml 卡数不一致 / 通信组不释放 / GPU/NPU 输入差异 | 修正配置、加 `-sd`、改测试脚本 | all_reduce / reduce_scatter / distribute_tensor |

**逐行解读**：
- **3.1 输入不一致**：最常见根因（~25 例）。GPU/NPU 各自生成输入导致 md5/二进制差异；通用解法是加 `-sd` 同步输入或改造为统一输入生成逻辑；波及精度、确定性、分布式三类。
- **3.2 归约精度**：反向 broadcast 触发 reduce_sum，CPU/NPU 浮点归约实现差异导致二进制不一致；通过双标杆或 `cv_fused_double_benchmark` 处理；影响 Tensor.add/div/fill_、where 等反向。
- **3.3 小算子拼接误差**：API 由多个小算子拼接，fp16/bf16 误差逐步累积；按 Float16/Bfloat 精度泛化处理（"已有结论"）；影响 sin/rsqrt/pow 等反向。
- **3.4 Inplace 确定性冲突**：`inplace=True` 修改输入使多轮结果不一致；用例侧避免原地修改或 ATK clone 输入；影响 leaky_relu/logit_/embedding/ctc_loss。
- **3.5 ACLNN 算子版本/缺失**：CANN 包缺失或版本不匹配走错路径；解法为更新 CANN 或等算子合入；波及 chunk_cat/TripletMarginLoss/cdist。
- **3.6 PTA 适配 Bug**：meta 注册、参数透传、校验、shape 推导有误；改 op-plugin 或 pytorch 仓代码；涉及 grouped_matmul/fusion_attention/LSTM/histc/linear。
- **3.7 ATK 工具 Bug**：确定性测试中 ATK 处理 inplace/梯度累计/输入读取有缺陷；更新 ATK 或 workaround；涉及 logit_/stack 反向/amp_update_scale。
- **3.8 通信/分布式配置**：node.yaml 卡数不一致、通信组不释放、GPU/NPU 输入差异；通过修正配置、`-sd`、改测试脚本；影响 all_reduce/reduce_scatter/distribute_tensor。

---

### 表格 3：§三 本仓库已收录案例（按 DTS）（原文逐字还原）

| DTS 单号 | API / 场景 | Gate 0 | 结论大类 | 详解 |
|---------|-----------|--------|---------|------|
| DTS2026042118463 | `torch.outer_backward` / 批跑 | **A · ATK** | 环境/链路（非数值精度） | [examples §2.1](../examples/dts-reproduce-cases.md#21-dts2026042118463atk--torchouter_backward) · [批跑范本](../examples/dts-reproduce-cases.md#atk-a5-batch-network-heaven-mismatch) |
| DTS2026042061660 | `torch.distributed.all_gather` | **B · 非 ATK** | 通信 + SOC/版本错配 | [examples §2.2](../examples/dts-reproduce-cases.md#22-dts2026042061660torchrun--torchdistributedall_gather) |
| —（issue-5 端到端范例） | `binary_cross_entropy_with_logits` | A · ATK | 内存一致性 + 算子 | [`examples/issue-5/`](../examples/issue-5/workdir/issue-5-binary_cross_entropy_with_logits/step5_conclusion.md)（step1 内存 / step2 定位 / step5 结论全产物） |

**逐行解读**：
- **DTS2026042118463**：`torch.outer_backward` 在批跑场景下，Gate 0 为 A · ATK，结论归类为"环境/链路（非数值精度）"；链接到 `examples §2.1` 和批跑范本。
- **DTS2026042061660**：`torch.distributed.all_gather` 走 Gate 0 的 B · 非 ATK 分支，结论为"通信 + SOC/版本错配"；链接到 `examples §2.2`。
- **issue-5 端到端范例**：`binary_cross_entropy_with_logits` 走 Gate 0 A · ATK，结论为"内存一致性 + 算子"；沉淀在 `examples/issue-5/` 目录下，包含 step1 内存、step2 定位、step5 结论全产物。

---

### 表格 4：§四 按症状检索（原文逐字还原）

| 症状关键词 | 优先 Skill / reference | 已收录案例 |
|-----------|------------------------|-----------|
| `RemoteDisconnected` / `Connection aborted` / Heaven accuracy 话术 | reproduce `-mt/-to` · functional · [gotchas §9](gotchas.md#9-批跑-failed-误判为精度-buga5--连接类) | DTS2026042118463 |
| `HCCL` / `all_gather` / SOC / `GetSocVersion` | flow-torchrun · torchrun-functional | DTS2026042061660 |
| 批跑 FAIL + 单跑 PASS | single-op 内存踩踏 · ATK#655（用户粘贴要点） | — |
| `SUCCESS` + 精度列 false | analyze-precision · [dump-analysis](../references/dump-analysis.md) | case-library §2.2 |
| ReduceSum / 反向归约二进制不一致 | 双标杆 · [a2a3-precision-tools](../references/a2a3-precision-tools.md) | case-library §2.2（add/div/fill_/where 反向） |
| 小算子拼接 fp16/bf16 误差 | 精度泛化（不解决） | case-library §2.2（sin/rsqrt/pow 反向） |
| inplace 确定性飘 | determinism_check · [gotchas §3](gotchas.md#3-inplace-操作破坏确定性验证) | case-library §2.3 |
| 内存一致性 >5% | [a2a3-memory-analysis](../references/a2a3-memory-analysis.md) | case-library §2.4 · issue-5 |

**逐行解读**：
- **连接类话术**：`RemoteDisconnected`/`Connection aborted`/Heaven accuracy 话术优先用 `reproduce -mt/-to` · `functional`，并查 gotchas §9；已收录案例为 DTS2026042118463。
- **HCCL/分布式类**：含 `HCCL`、`all_gather`、SOC、`GetSocVersion` 关键词走 `flow-torchrun` · `torchrun-functional`；已收录案例为 DTS2026042061660。
- **批跑 FAIL + 单跑 PASS**：怀疑 single-op 内存踩踏或 ATK#655；原文未列已收录案例（"—"）。
- **SUCCESS + 精度 false**：走 `analyze-precision` 并参考 `dump-analysis`；对应 case-library §2.2。
- **ReduceSum/反向归约**：使用双标杆或 `a2a3-precision-tools`；对应 case-library §2.2 的 add/div/fill_/where 反向。
- **小算子拼接误差**：走精度泛化（"不解决"）；对应 case-library §2.2 的 sin/rsqrt/pow 反向。
- **inplace 确定性飘**：用 `determinism_check` + gotchas §3；对应 case-library §2.3。
- **内存一致性 >5%**：使用 `a2a3-memory-analysis`；对应 case-library §2.4 与 issue-5。

---

### 表格 5：§六 与 flow 的衔接（原文逐字还原）

| 阶段 | 如何使用本索引 |
|------|---------------|
| flow-atk 一屏决策卡壳 | 给用户 **建议检索词**（API + 症状列） |
| analyze-functional 归类犹豫 | 指向 §四 症状 → 已收录案例 |
| analyze-precision / dump 定界 | 先查 §二 ReduceSum / 小算子拼接 / 内存模式是否命中 |
| report 5.end | 「历史参考」段写 **DTS 单号 + 本节链接**，不写「表中第 N 行命中」除非用户粘贴 |

**逐行解读**：
- **flow-atk 一屏决策卡壳**：助手给用户提供建议检索词（API + 症状列关键词），由用户自行对照。
- **analyze-functional 归类犹豫**：通过 §四 症状表 → 已收录案例的映射协助归类。
- **analyze-precision / dump 定界**：先查 §二 的 ReduceSum / 小算子拼接 / 内存模式是否命中，以加速定界。
- **report 5.end**：在"历史参考"段写 DTS 单号 + 本节链接；除非用户粘贴，否则不写"表中第 N 行命中"。

---

## 【公式解读】

原文无公式。

---

## 【关联】

| 上游 / 下游 | 文件 / 模块 | 关系 |
|------------|-------------|------|
| 上游纪律 | `a2-a3-a5-discipline.md` | 约束助手"不自动抓取内网表、不编造命中行" |
| 详情沉淀 | `examples/case-library.md` | 约 130 条历史 API 根因/结论详情（原 a2a3 712 行案例库整编）；§一 结论分类总览、§二 高频根因、§2.2 精度、§2.3 确定性、§2.4 内存 |
| 现代案例 | `examples/dts-reproduce-cases.md` | DTS 工作流验证案例库；§2.1 `torch.outer_backward`、§2.2 `torch.distributed.all_gather`、批跑范本 |
| 端到端范例 | `examples/issue-5/` | `binary_cross_entropy_with_logits` 的 step1 内存 / step2 定位 / step5 结论全产物 |
| 配套参考 | `references/a2a3-precision-tools.md` | 双标杆、归约精度处理工具 |
| 配套参考 | `references/dump-analysis.md` | `analyze-precision` 阶段的 Dump 分析 |
| 配套参考 | `references/a2a3-memory-analysis.md` | 内存一致性 >5% 的分析参考 |
| 配套 Gotchas | `gotchas.md#3` | inplace 操作破坏确定性验证 |
| 配套 Gotchas | `gotchas.md#9` | 批跑 FAILED 误判为精度 Bug（A5 · 连接类） |

---

## 【使用方法】

**Step 3 定位阶段使用流程**：

1. **结论类型对齐**：用户给到 xlsx/Heaven 输出后，按 §一 8 类结论类型判定出口（`functional` / `reproduce` / `analyze-precision` / `single-op early-stop` / `precision Dump` / `determinism_check` / `torchrun-functional` / `report 待办`）。
2. **高频根因速查**：用 §二 8 类根因模式 + §四 8 类症状关键词交叉验证是否命中已收录案例。
3. **DTS 单号索引**：从 §三 表格查 3 条已收录案例（DTS2026042118463 / DTS2026042061660 / issue-5）对应的链接与详解。
4. **新增案例追加**（团队维护）：在 `examples/dts-reproduce-cases.md` 追加 6 项必填字段（DTS 单号 + Gate 0 + API 名 / 表象与证据签名 / 根因 / 结论类型 / 关键命令 / 产物路径），随后在本文件 §三 表格增一行链接；`knowledge/` 不重复粘贴长命令块。
5. **关键命令参数**（原文涉及）：
   - `-mt / -to`：reproduce 命令中用于 timeout/重试参数（命中 §一 环境/链路/调度、§四 连接类）
   - `-sd`：同步输入参数（命中 §二 3.1、3.8、§四 ReduceSum/分布式配置）
   - `-p`：确定性脚本参数（命中 §一 确定性）
   - `reproduce -mt -to`：§四 首选 reproduce 命令
6. **flow 衔接**：按 §六 四阶段（flow-atk / analyze-functional / analyze-precision / report 5.end）分别使用本索引。
7. **纪律硬约束**：**不自动抓取**内网表、**不编造**命中行；如未命中已收录案例，写"未命中历史索引"而非猜测。
