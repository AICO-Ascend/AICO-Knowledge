# [算子名称] 设计文档

> 仓 `agent-skills` · 路径 `community/Op/shmem-ops-design/references/design-template.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/agent-skills/community/Op/shmem-ops-design/references/design-template.md

# 「Op/shmem-ops-design — design-template.md」一体化深度解读

---

## 【定位】

这篇文档是昇腾 SHMEM 自定义算子（custom op）研发流水线的**统一设计模板**，规定每个算子在进入代码生成（`shmem-ops-code-gen`）前必须产出的设计文档骨架与 Canonical DSL 字段约束，确保需求、接口、分核、正确性、性能基线六类信息以唯一结构化形式被下游 Agent 直接消费。

---

## 【技术要点】

1. **Canonical DSL 是唯一信息源**：第 2 节要求保留完整 fenced `yaml` block（`dsl_version: "0.3"`），后续 code-gen、走读、性能采集全部按 DSL 字段执行，禁止把同一信息散落到多节描述。

2. **算子四分类与构建模式双轴定位**：`op_kind` 限定为 `transport | collective | compute | fused_compute_comm` 四类；`build_mode` 限定为 `independent_project`（默认）或 `in_tree_example`（须 Phase 0 用户明确要求），二者共同决定编译入口与目录布局（`op_root`）。

3. **Core Allocation 五模式 + 三层 schedule 结构**：`core_partition.mode` 必须引用 `core-allocation.md` 中的 A（全员协作）/ B（按 PE 分组）/ C1（生产者消费者）/ C2（维度分组）/ CoC（通算融合）之一；schedule 按 `core_partition → tiling(tile/chunk/tail) → phases` 顺序设计，跨 PE 数据面接口强制使用 `aclshmem_* / aclshmemx_*` 系列。

4. **Capability Mapping 强制覆盖六大能力域**：lifecycle、memory、transport、sync、compute、scheduler；每行 `Classification` 仅可取 `可复用 / 需适配 / 需新实现`；若全为前两类，须在表后显式声明 `No known gap`。

5. **Design Review 11 条硬性门禁**：其中 6 条聚焦并发/分核真伪（包括"分核但 peer 串行"的假并发检测、单 PE 同时活跃链路数 × 单链路带宽与拓扑聚合带宽差距 > 50% 须给出估算推导、reduce-scatter/allreduce RS 必须使用 `SetAtomicAdd<T>()` 的 MTE 批量累加且仅在 MTE 不可用时才降级 SDMA fallback——参照 `atomic-add-pattern.md §12` 优先级 1）。

6. **性能门槛量化阈值**：性能 section 强制填写 `max_opt_rounds: 5`、`min_scale`（集合通信 ≥ 256MB、计算/通算融合 hidden size ≥ 1000）；`baseline_target` 在有 baseline 时约束为 `"current >= 80% baseline"`，无 baseline 时退化为 `metric_only`。

---

## 【关键机制与数据】

**工作原理（模板驱动的设计—生成流水线）：**
- **Phase 0 信息采集**：用户通过 `user_confirmations.op_name` 与 `dtype/dtypes` 表（原文 1.1）确认算子身份与数据类型；`docker_container` / `docker_workdir` / `docker_exec_required` 三字段联动决定后续 build/run/perf 是否进容器。
- **DSL 字段驱动下游**：第 2 节 YAML 中 `meta.performance_required=false` 决定跳过 Phase 6，`meta.performance_auto_optim=false` 决定 Phase 6.5 不自动触发；`meta.torch_required=false` 决定跳过 Phase 5.5（原文字段含义）。
- **schedule 三段式设计顺序**：原文在 YAML 注释中明确写明 "设计顺序：先分核 → 再 tiling → 最后 phases"，目的是保证并发模型先收敛、负载切分再细化、执行序列最后落定。
- **fused_compute_comm 双路径**：`compute.compute_path` 仅在 `fused_compute_comm` 时必填，优先 `device_catlass_coc`（推荐），`host_aclnn` 仅作过渡并须填写 `upgrade_plan` 升级条件，参考实现为 `examples/matmul_allreduce`。

**数据流（接口→语义→拓扑→内存→调度→正确性→性能）：**
DSL 字段顺序即数据流方向：`interface.inputs/outputs/attrs`（张量级契约）→ `semantics.local_compute/communication/finalize/result`（语义级分解）→ `topology.group/peer_model/addressing="symmetric_memory"`（物理拓扑投影）→ `memory.buffers/symmetric_layout/output_ownership`（地址布局）→ `schedule.core_partition/tiling/phases/compute`（执行调度）→ `correctness.oracle/tolerance/invariants/case_matrix`（验证约束）→ `performance.metric/baseline_search/baseline_target/target_cases/min_scale/profiling_method/max_opt_rounds=5`（性能契约）。

**性能数据：** 原文仅给出元阈值（256MB / hidden size 1000 / 80% baseline / 5 轮 max_opt_rounds / 50% 链路带宽差距红线），未给出具体算子的实测数字。

---

## 【表格解读】

### 表 1.1 用户确认项（原文逐字还原）

| 确认项 | 内容 | 确认状态 |
| --- | --- | --- |
| 算子名称 `op_name` | [用户确认的算子名称] | confirmed |
| 算子数据类型 `dtype/dtypes` | [逐项列出输入、输出、累加/中间 dtype] | confirmed |

**解读**：此表是 Phase 0 必须用户当面签字的"两要素"——算子身份与数据类型。`confirmed` 是模板默认占位，实际填写时必须替换为真实名称与逐项 dtype 清单（含输入/输出/累加中间 dtype），并对应回填到 `source.user_confirmations.op_name` 与 `interface.inputs/outputs.dtype`，保证 DSL 唯一信息源约束不破。

### 表 1.3 Assumptions 与 Open Questions（原文逐字还原）

| 类型 | 内容 | 是否阻塞代码生成 |
| --- | --- | --- |
| assumption | [可接受假设] | no |
| open question | [必须用户确认的问题] | yes/no |

**解读**：采用二值"是否阻塞"字段而非优先级评级，是为了把设计文档的代码生成门槛简化为二态——`assumption` 永远不阻塞，`open_question` 一旦 `yes` 则下游 `shmem-ops-code-gen` 必须等待用户答复后才能消费 DSL，符合"无阻塞 open question"作为 handoff 硬性条件的设计意图。

### 表 3 Capability Mapping & Gap Analysis（原文逐字还原）

| Requirement | SHMEM capability/source | Classification | Adaptation / Gap | Risk |
| --- | --- | --- | --- |
| [需求点] | [API/example/template/source path] | [可复用/需适配/需新实现] | [可复用：无；需适配：适配点；需新实现：gap 原因 + 设计方案 + 验证方式] | [正确性/性能风险] |

**解读**：六类需求（lifecycle、memory、transport、sync、compute、scheduler）每类必出一行；`Classification` 三态强制选一是为了下游 Agent 能用简单规则路由——`可复用` 直接生成调用代码，`需适配` 触发适配模板，`需新实现` 进入设计评审通道；`Adaptation/Gap` 列对 `需新实现` 行强制要求"原因+方案+验证"三段式，杜绝 gap 描述悬空。

### 表 4 实现边界（原文逐字还原）

| 位置 | 职责 |
| --- | --- |
| Device kernel | [通信、计算、搬运、同步等算子核心语义] |
| `main.cpp` | [单 PE Host 编排：参数、初始化、资源、读写、launch、cleanup] |
| Host helper `.cpp/.h` | [可选：运行时 shape/layout/tiling/route/payload/packing 计划] |
| Python scripts | [输入/golden/checker、测试用 route/payload、误差报告] |

**解读**：四条位置 + 一条约束（`main.cpp` 必须单进程单 PE，不 fork/spawn 多 PE）共同界定代码落点。`Host helper` 标"可选"是把复杂路由/打包逻辑从 `main.cpp` 抽离的合法出口，但约束"复杂 Host 逻辑必须拆到独立 `.cpp/.h`"反向说明 `main.cpp` 只能做编排，不能做计算；Python scripts 显式排除 golden 与 checker 进入 Host C++，是为了把测试资产与算子核心解耦。

### 表 5 Design Review Before Handoff（原文逐字还原）

| Check | Result | Fix or rationale |
| --- | --- | --- |
| 并发/分核思路是否在首版 correctness 交付中落地 | [pass/fail] | [说明] |
| 是否存在不必要的 Host/global barrier | [pass/fail] | [说明] |
| tile/chunk/tail 是否支持并发且不靠单核兜底 | [pass/fail] | [说明] |
| route/offset/prefix 计算是否避免明显 O(N²) 扫描 | [pass/fail] | [说明] |
| 是否避免多余 GM scratch 写读，或说明无法避免原因 | [pass/fail] | [说明] |
| 对于 reduce-scatter / allreduce RS 等多 source→同 destination 场景，累加路径是否使用 `SetAtomicAdd<T>()`（MTE 批量）而非串行 UB 累加（必须符合 `atomic-add-pattern.md §12` 优先级1；仅 MTE 不可用时允许降级为 SDMA fallback） | [pass/fail] | [说明] |
| 高性能传输路径、并发分核或 overlap 是否属于本轮实现范围 | [pass/fail] | [说明] |
| Capability Mapping compute 行是否引用了 `atomic-add-pattern.md` 评估累加方式（非仅列出 AscendC Add） | [pass/fail] | [说明] |
| **拓扑与并发匹配**：设计的并发模型是否能发挥目标拓扑的全部链路并行度？（如 full-mesh 8 卡有 7 条独立 HCCS 链路，设计中是否让多链路**同时**活跃而非串行遍历 peer？） | [pass/fail] | [给出同时活跃链路数 vs 拓扑总链路数] |
| **链路带宽利用**：每个通信 phase 中，单 PE 同时活跃链路数 × 单链路带宽是否接近拓扑理论聚合带宽？（差距 >50% 须解释原因） | [pass/fail] | [给出估算数据和推导] |
| **分核与通信并行度**：AIV 分组是否支撑了并发目标？是否存在"分核了但 peer 维度仍是串行"的假并发？ | [pass/fail] | [说明每个 group 内 AIV 的通信是否真并行] |
| **性能瓶颈预判**：根据上述分析，标注设计预期的性能瓶颈位置（链路串行 / peer 串行 / 分核不足 / 同步开销 / UB 容量等） | [pass/fail] | [列出瓶颈类型和位置] |

**解读**：13 条门禁可归并为五组审查意图——(1) 首版正确性 vs 高性能范围分离（第 1、7 条）；(2) 并发真伪检测（第 2、3、11 条，专门识别"分核但 peer 串行"的假并发）；(3) 性能模型自洽性（第 9、10 条量化拓扑并行度与带宽利用率，>50% 差距强制给出估算推导）；(4) 累加路径合规性（第 6、8 条强制引用 `atomic-add-pattern.md §12` 优先级 1 的 MTE 批量 `SetAtomicAdd<T>()`，仅 MTE 不可用才允许 SDMA fallback）；(5) 复杂度控制（第 4、5 条抑制 O(N²) 扫描与多余 GM scratch）。每条必须 `pass/fail` 二值化以适配 Agent 评审流水线。

### 表 6.1 Compile Contract（原文逐字还原）

| 字段 | 内容 |
| --- | --- |
| build_mode | **`independent_project`（默认）** 或 `in_tree_example`（须 Phase 0 用户明确要求） |
| cann_env | [用户指定的 CANN set_env.sh 路径；不得硬编码默认路径] |
| shmem_repo | [绝对路径；见 shmem-repo-resolution.md；与 meta.shmem_repo 一致] |
| op_dir | [`custom-ops/<op_name>/`（默认）或 `examples/<op_name>/`] |
| target | [binary/shared library] |
| command | independent: [custom-ops-entrypoints.md](../../shmem-ops-compile-debug/references/custom-ops-entrypoints.md) §1 编译；in-tree: 同文件 §0 + SHMEM build -examples |
| run_command | [custom-ops-entrypoints.md](../../shmem-ops-compile-debug/references/custom-ops-entrypoints.md) §2 运行 |
| matrix_command | [custom-ops-entrypoints.md](../../shmem-ops-compile-debug/references/custom-ops-entrypoints.md) §3 case matrix |
| perf_command | [perf-workflow.md](../../shmem-ops-performance-eval/references/perf-workflow.md) §1 阶段 B |
| torch_build_command | [custom-ops-entrypoints.md](../../shmem-ops-compile-debug/references/custom-ops-entrypoints.md) §4 Torch 编译 |
| required_flags | [-examples/-debug/-enable_rdma/-enable_ascendc_dump/-soc_type ...] |
| expected_outputs | [build/bin 或 build/lib 产物] |

**解读**：此表是"哪条命令跑哪个阶段"的契约单据。`command` 列在两种 `build_mode` 下分流（independent 走 §1、in-tree 走 §0+`SHMEM build -examples`），`cann_env` 字段"不得硬编码默认路径"是防止模板在不同用户环境失效的硬约束；`required_flags` 显式列举 `-enable_rdma`（RDMA 路径）与 `-enable_ascendc_dump`（调试 dump）作为常见必备 flag 提示。

### 表 6.2 Functional/Correctness Contract（原文逐字还原）

| 字段 | 内容 |
| --- | --- |
| command | [`scripts/run.sh`/checker 命令] |
| python_env | [python_cmd 或 conda/venv 激活命令；用于 gen_data.py、golden、check_result.py、baseline/profiler] |
| python_deps | [numpy/torch/torch_npu 或脚本实际 import 的依赖] |
| determinism | [seed、repeats、输出路径隔离] |

**解读**：此表与 DSL `correctness` 段职责互补——DSL 定义"对什么 oracle、用什么 tolerance、覆盖哪些 case"，本表定义"用什么 python 环境、装哪些依赖、如何保证可重复运行"。`determinism` 三件套（seed、repeats、输出路径隔离）是 Agent 复跑同一 case 矩阵的最小必要条件。

---

## 【公式解读】

**原文无公式**。全文未出现 LaTeX 数学表达式或伪代码公式；唯一接近形式化描述的是第 2 节 YAML schema 内的字段类型声明（如 `dtype: "fp16"`、`shape: "[n_pes, shard_elems]"`、`tile: "replace_me"`），均为占位字符串而非可计算公式。

---

## 【关联】

**与上下游模块/特性的关系图（基于文末链接 + 文中引用）：**

- **下游执行契约**（4 次引用同一文件）：
  - `../../shmem-ops-compile-debug/references/custom-ops-entrypoints.md` §0：in_tree_example 模式的预编译入口（`SHMEM build -examples`）
  - 同文件 §1：independent_project 模式的编译命令
  - 同文件 §2：单算子运行命令
  - 同文件 §3：case matrix 批量执行命令
  - 同文件 §4：Torch 扩展编译命令（受 `meta.torch_required=true` 触发）

- **性能评估契约**：
  - `../../shmem-ops-performance-eval/references/perf-workflow.md` §1 阶段 B：性能采集与基线对比流程（受 `meta.performance_required=true` 触发，进入 Phase 6）

- **同仓库内隐式引用（文档正文出现但未作为文末链接列出）**：
  - `core-allocation.md` — `schedule.core_partition.mode` 的五模式定义源（A/B/C1/C2/CoC）
  - `atomic-add-pattern.md §12` 优先级 1 — Design Review 第 6、8 条强制引用的累加路径规范
  - `shmem-repo-resolution.md` — `meta.shmem_repo` 与 Compile Contract `shmem_repo` 字段的解析规则
  - `examples/matmul_allreduce` — `compute.reference_examples` 的参考实现

- **上游输入**：本文档由 `shmem-ops-design` skill 产出，作为 `shmem-ops-code-gen` 的输入契约；输出物是第 7 节 handoff checklist 通过后的完整设计包。

- **平级协同**：第 4 节实现边界显式约束 `main.cpp` 不得 fork/spawn 多 PE，意味着本模板与 `shmem/examples` 目录下的多进程示例采用不同的多 PE 拓扑策略——前者依赖 SHMEM runtime 内建的多 PE 启动能力，后者由 Host 进程级编排。

---

## 【使用方法】

**启用方式**：在 `agent-skills` 仓库下调用 `shmem-ops-design` skill 时，以本文档为骨架生成具体算子的 design.md；文件名建议遵循 `custom-ops/<op_name>/design.md`（与 `op_root` 默认值一致）。

**配置项与约束（汇总自原文硬性条款）**：

1. **Phase 0 用户确认门槛**：必须先回填 1.1 表的 `op_name` 与 `dtype/dtypes`（状态列写 `confirmed`），并在 `source.user_confirmations` 同步记录，否则 handoff 第 2 项不通过。
2. **DSL `meta` 关键开关**：
   - `performance_required=true` 才执行 Phase 6 性能评估
   - `performance_auto_optim=true` 且未达标才自动触发 Phase 6.5
   - `torch_required=true` 才执行 Phase 5.5 Torch 编译
   - `docker_container` 非空时 `docker_exec_required=true`，所有 build/run/perf 自动进容器
3. **YAML 必填字段**：`dsl_version`（固定 `"0.3"`）、`meta.skills_root` 与 `meta.shmem_repo`（MUST）、`source.user_confirmations`、`interface.inputs/outputs/attrs`、`semantics` 四子段、`topology`、`memory`、`schedule.core_partition/tiling/phases`、`correctness.oracle/tolerance`、`performance.metric`（固定 5 项：`e2e_latency_us`、`kernel_latency_us`、`algo_bandwidth_GBps`、`e2e_bus_bandwidth_GBps`、`kernel_bus_bandwidth_GBps`）、`performance.max_opt_rounds=5`。
4. **强制引用条款**：
   - `schedule.core_partition.mode` 必须显式引用 `core-allocation.md` 五模式之一
   - Design Review 第 6、8 条必须引用 `atomic-add-pattern.md §12`
   - Compile Contract `command` / `run_command` / `matrix_command` / `torch_build_command` 必须引用 `custom-ops-entrypoints.md` 对应章节
   - Compile Contract `perf_command` 必须引用 `perf-workflow.md §1 阶段 B`
5. **门禁硬性条件（Handoff Checklist 7 条）**：Canonical DSL 完整且无阻塞 open question；Capability Mapping 覆盖六能力域且无 gap 悬空；`schedule.core_partition/tiling/phases` 可实现；`correctness.invariants` 每项有 `test_method` + `case`；`case_matrix` 含 stress/边界 case；`performance.baseline_search / baseline_target / min_scale` 已填。

**原文未涉及**：本文档为模板，未提供具体算子的 `op_name`、目标 shape、实测 `algo_bandwidth_GBps` 数字、case matrix 行项等实例化内容；亦未涉及 CI/CD 集成、版本发布流程、回归测试套件编排等下游流水线细节。
