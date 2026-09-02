# Design Document: TensorCast New Model Adaptation Efficiency

> 仓 `msmodeling` · 路径 `docs/design/model_adaptation_efficiency_design.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msmodeling/docs/design/model_adaptation_efficiency_design.md

【定位】
本文档针对 TensorCast 模型适配当前依赖人工反复调研（审阅 HuggingFace 源码、推断 `ModelProfile` 字段、排查运行时不兼容、映射算子、构造回归证据）成本高、不可追溯、不可复用的痛点，定义一套结合「确定性适配程序 + 大模型 Skill」的端到端可复用适配工作流，使得新模型适配仅需「TensorCast 仿真命令 + MindStudio Insight 原始 profiling 导出」两份输入即可产出可审查、可回归、可盲放回的 doctor report 与 ST guardrail case。

---

【技术要点】
1. **两输入极简入口**：用户仅需提供 TensorCast 仿真命令和匹配的 MindStudio Insight 原始 profiling 导出（可选追加 hints），即可触发 doctor engine 输出报告。
2. **确定优先 + Skill 受限辅助**：程序化解析、校验、验证在前；大模型 Skill 仅在源码语义推理、patch 方法编写、不确定算子映射复审等确定性分析不足之处给出"可复审草稿"，不替代确定性子系统。
3. **五项目标与对应成功信号**：减输入（两份输入即可出报告）、可追溯（每个产物引用其证据源）、提正确（AI 草稿必经验证、dry-run、验证器三道关）、可回归（已验证证据转 ST guardrail）、可盲放回（隐藏既有 profile 重放仍能发现预期 Qwen3-VL 结构与 patch 需求）。
4. **九大组件职责与反目标**：Adaptation Context（解析归一化参数，不臆造 workload）、Raw Insight Importer（归一化 kernel 摘要与前向总时延，不让用户手写证据）、Structure Inspector（扫描安装模型树中 attention/MoE/MLA/MTP/VL 事实，不据模型名猜字段）、Profile Candidate Materializer（最小可复审候选，未经校验不标 verified）、Profile Validator（类型/必填/默认省略/patch 可调用校验，不证运行时语义等价）、Patch Discovery（分类 dry-run/smoke 失败并产出受限 AI 任务，不直接生成模型特异 patch 代码）、Evidence Builder（融合原始 profiling、归一命令、实际摘要与 hints，不隐藏低置信度映射）、Evidence Verifier（比对预期与实际并分类不匹配，不把所有不匹配当通用失败）、ST Case Generator（仅基于已验证证据生成回归 case，不从未验证证据产出 verified case）。
5. **4+1 架构视图分审**：逻辑视图（不变量证据与可复审草稿、profile 只能经多重门禁向 verified 推进）、过程视图（确定性先收窄未知，明确检查点处才引入人工与 AI）、开发视图（源模块依赖方向）、物理视图（本地运行时/外部产物/可选 AI 助手）、场景视图（代表性模型接入与盲放回）。
6. **流程闭环**：Intake → Doctor → Review（接受/转 AI Task）→ Register → 回到 Doctor（含 Evidence）→ Evidence Review → Verification → 通过则生成 ST Case，分类失败回到 Iterate 形成闭环。

---

【关键机制与数据】
- **工作原理**（原文：System Context / Process View）：CLI 是公开入口；doctor engine 协调确定性子系统；Skill 仅作为接收结构化证据并产出可复审草稿的受限助手。流程呈迭代控制环——「Doctor 出候选 → Human Review → 接受则 Register；或转 AI Task → Register → 回到 Doctor 跑出 Evidence → Evidence Review → Verification → 通过/可接受偏差则生成 ST Case；分类失败则回到 Iterate」。
- **逻辑视图数据对象**（原文：Logical View mermaid）：`Simulation Command → AdaptationContext`、`Raw Insight Export + Hints Ledger → Evidence Draft`、`ModelStructureFacts → ProfileCandidate → ModelProfile`、`ProfileCandidate/Profile/EvidenceDraft 均并入 DoctorReport`，`DoctorReport → Evidence YAML → VerificationReport`。
- **关键性能/可观察信号**（原文：Goals 与 Success Signal 行）：期望两份输入即可产出 doctor report；每个产物必须能溯源到证据源；AI 生成的 profile/patch/evidence 必须经过 validation、dry-run、verifier 三层门禁；盲放回模式要能发现预期的 Qwen3-VL 结构与 patch 需求。文档未给出吞吐、延迟、显存等具体数值。

---

【表格解读】

**1. Revision History（原文逐字还原）**

| Date | Version | Change Description | Author | RFC Document |
| --- | --- | --- | --- | --- |
| 2026-06-03 | 1.0 | Initial design for the model adaptation efficiency workflow | kai1949, codex | N/A |

解读：版本 1.0 初稿，作者 kai1949 与 codex，无 RFC 文档号；记录了本次设计首次成文的时间。该表是文档元信息，无功能性含义。

**2. Primary Goals（原文逐字还原）**

| Goal | Design Direction | Success Signal |
| --- | --- | --- |
| Reduce required user input | Require only a TensorCast simulation command and matching MindStudio Insight raw profiling export | Doctor report can be produced from the two inputs |
| Make adaptation traceable | Preserve normalized command, raw profiling provenance, hints, profile candidates, and verification reports | Every generated artifact references its evidence source |
| Improve correctness | Gate AI-generated profile, patch, and evidence drafts through validation, dry-run, and verifier checks | Failures are classified with actionable next steps |
| Enable reusable regression | Convert verified evidence into ST guardrail cases | Adapted models have repeatable count and latency checks |
| Support blind replay | Validate the workflow by re-adapting an already supported model while hiding its existing profile | Replay discovers the expected Qwen3-VL structure and patch needs |

解读：
- "减输入"：把输入收敛为"TensorCast 仿真命令 + Insight 原始 profiling"两份，验收标准是 doctor report 能从这两份输入产出。
- "可追溯"：归一命令、原始 profiling、hints、profile 候选、验证报告全部入保留产物；验收标准是每个产物都能反向指回证据源。
- "提正确"：AI 草稿必经 validation、dry-run、verifier 三关；验收标准是失败被分类并产出可执行的下一步动作（而非笼统报错）。
- "可回归"：已验证证据转为 ST guardrail；验收标准是已适配模型有可重复的 count 与 latency 校验。
- "可盲放回"：对已支持模型在隐藏其既有 profile 的前提下重放全流程；验收标准是仍能发现预期的 Qwen3-VL 结构与 patch 需求——用 Qwen3-VL 作为代表性盲放回目标。

**3. Design Principles（原文逐字还原）**

| Principle | Meaning |
| --- | --- |
| Deterministic first | Programmatic inspection, validation, parsing, and verification run before AI reasoning is accepted. |
| Minimal human checkpoint | When uncertainty remains, the system asks for the smallest confirmed fact instead of asking the user to explain a full model. |
| Provenance preserving | Reports retain the raw command, raw profiling source, hints, candidate fields, and confidence values. |
| Replayable by design | Existing profiles may be ignored only in replay or audit mode, so the process can be tested without reading the known answer. |

解读：
- 确定优先：所有程序化检测/校验/解析/验证先于 AI 推理被接受——AI 永远不是第一道闸。
- 最小人工检查点：不确定时只问最小可确认事实，而不是让用户讲一遍整个模型——降低人工负担。
- 保留来源：报告必须留 raw command、原始 profiling 源、hints、candidate fields、confidence values——支撑可追溯目标。
- 可放回设计：仅在 replay 或 audit 模式下允许忽略既有 profile，使流程可被盲测。

**4. Component Responsibilities（原文逐字还原）**

| Component | Responsibility | Non-Goal |
| --- | --- | --- |
| Adaptation Context | Parse a TensorCast simulation command into normalized model, workload, device, parallelism, quantization, and multimodal parameters | Guess a workload that was not supplied |
| Raw Insight Importer | Convert Insight raw export rows into normalized kernel summaries and total forward timing | Require the user to hand-write evidence |
| Structure Inspector | Scan the installed model tree for attention, MoE, MLA, MTP, and VL facts | Infer fields from model names alone |
| Profile Candidate Materializer | Create a minimal `ModelProfile` candidate with review-friendly fields | Mark a profile as verified before validation and runtime checks |
| Profile Validator | Check profile field type, required fields, default elision, and callable patch methods | Prove runtime semantic equivalence |
| Patch Discovery | Classify dry-run or smoke failures and produce bounded AI assistance tasks | Generate model-specific patch code directly |
| Evidence Builder | Merge raw profiling, normalized command, actual summaries, and hints into an evidence draft | Hide low-confidence mappings |
| Evidence Verifier | Compare expected evidence with actual TensorCast summaries and classify mismatches | Treat all mismatches as generic failures |
| ST Case Generator | Convert verified reports into regression guardrail case drafts or verified cases | Generate verified cases from unverified evidence |

解读：每个组件"做什么/不做什么"成对定义，构成可问责的契约边界。要点：
- Context 不臆造 workload（输入缺则断流，不补）。
- Importer 不让用户手写证据（原始 profiling 必须机器化归一化）。
- Inspector 仅基于已安装模型结构扫描，不据模型名猜字段（避免命名流派误导）。
- Materializer 不越过验证标 verified——把"已生成"与"已验证"严格区分。
- Validator 只做静态层面的形态校验，不证明运行时语义等价（语义等价由运行/验证器层负责）。
- Patch Discovery 只生成受限 AI 任务，不直接产出模型特异 patch 代码（避免 AI 越权产出未审查代码）。
- Evidence Builder 不隐藏低置信度映射（透明度高于美观）。
- Verifier 必须分类不匹配而非笼统失败（与"提正确"目标对齐）。
- ST Case Generator 仅接受已验证证据，避免未验证证据污染回归库。

**5. 4+1 Architecture Views（原文逐字还原）**

| View | Design Focus | Main Stakeholder | Key Artifact |
| --- | --- | --- | --- |
| Logical view | Domain abstractions, report schema, profile/evidence model | Adapter author, reviewer | Data model and UML class diagrams |
| Process view | Runtime workflow, iteration states, AI handoff boundaries | Adapter author, test owner | Sequence and state diagrams |
| Development view | Source modules and dependency direction | Maintainer | Component/module dependency diagram |
| Physical view | Local runtime, external artifacts, optional AI assistant | Tooling owner | Deployment diagram |
| Scenario view | Representative model onboarding and replay/audit cases | Reviewer, acceptance owner | Usage case and test scenarios |

解读：五视图分而审之——
- 逻辑视图聚焦领域抽象与产物 schema；产出数据模型与 UML 类图。
- 过程视图聚焦运行时工作流与 AI 交接边界；产出序列图与状态图。
- 开发视图聚焦源码模块组织与依赖方向；产出组件依赖图，关心维护者。
- 物理视图聚焦本地运行时、外部产物、可选 AI 助手；产出部署图。
- 场景视图聚焦代表型接入与盲放回；产出用例与测试场景图。
此 4+1 切分与左侧 Logical/Process 视图对应的 mermaid 图互相印证——视图之间通过统一数据对象（DoctorReport/Evidence YAML/VerificationReport 等）串联。

---

【公式解读】
原文无公式。

---

【关联】
- **上游 / 输入侧**：
  - `User`（Adapter Author）提供 TensorCast 仿真命令、MindStudio Insight 原始 profiling 导出、可选 hints。
  - `Insight`（MindStudio Insight 原始导出）作为 Raw Insight Importer 的输入。
  - `HF`（已安装 Transformers 源码）供 Structure Inspector 扫描 attention/MoE/MLA/MTP/VL 等结构事实。
- **中心协调**：`Doctor`（Doctor Engine）协调上述子系统，串联 Context/Inspector/Materializer/Validator/Builder 全链。
- **下游 / 输出侧**：
  - `Registry`（`ModelProfile` Registry）承接最终验收的 profile。
  - `Evidence` 落 YAML，再交 `Verifier` 出分类结果；通过后交 `ST`（ST Guardrail Case）做回归。
  - `Skill`（大模型 Skill）作为受限助手，仅产出可复审 patch 或算子映射草稿回给用户，最终仍以人工 review 结果为准回写 Registry。
- **配套文档**：用户面操作（详细命令、输入格式、结果复核步骤）见 `docs/en/user_guide/msmodeling_tensor_cast_new_model_adaptation_user_guide.md`；设计面与本 design 文档互补。
- **内部链接**：原文文末未提供其他内部链接列表。

---

【使用方法】
原文未直接列出 CLI 命令或配置项；明确指出"详细命令、输入格式与输出复核步骤"被剥离到用户指南 `docs/en/user_guide/msmodeling_tensor_cast_new_model_adaptation_user_guide.md`。文档范围内可启用的工作机制仅以原文中提到的入口与触发条件形式存在：
- 通过 `model_adapter CLI`（public entry point）提交"simulation command + raw profiling export（+ optional hints）"即可触发 doctor engine。
- 仅在 replay/audit 模式下允许忽略既有 profile 以做盲放回验证。
如需启用命令、具体参数或配置项，请参阅上述用户指南文档。
