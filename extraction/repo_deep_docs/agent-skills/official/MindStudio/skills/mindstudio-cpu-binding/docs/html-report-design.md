# HTML 报告设计

> 仓 `agent-skills` · 路径 `official/MindStudio/skills/mindstudio-cpu-binding/docs/html-report-design.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/agent-skills/official/MindStudio/skills/mindstudio-cpu-binding/docs/html-report-design.md

# 一体化深度解读：HTML 报告设计（mindstudio-cpu-binding）

---

## 【定位】

这篇文档定义了 `mindstudio-cpu-binding` 技能生成的"HTML 诊断报告"的完整页面结构、数据呈现样式与可移植性约束，用于在一份**单文件、离线可看、无外部依赖**的 HTML 中，直观呈现当前 CPU 绑核状态、NUMA/NPU 拓扑、关键进程线程、问题发现、推荐优化方案、自动绑核/回滚、验证计划与信息缺口，从而把"绑核诊断"的结论与证据一次性交付给用户。

---

## 【技术要点】

1. **离线单文件交付**：报告必须输出为单个自包含 HTML 文件，CSS 内联在 `<style>`、JavaScript 内联在 `<script>`、Snapshot 摘要数据可内嵌为 JSON script block；不引用本地绝对路径、不引用外部网络资源（CDN、字体、图片、JS 包均不允许）。
2. **跨平台可读**：必须在 Linux 节点生成，但能在 Linux 与 Windows 浏览器中直接打开；文件名建议 `mindstudio-cpu-binding-report-<timestamp>.html`。
3. **10 段式固定页面骨架**：摘要卡片 → 当前绑核状态 → CPU/NPU/NUMA 拓扑 → 逻辑 CPU 网格 → 关键进程与线程 → 问题发现 → 推荐优化方案 → 自动绑核与回滚 → 验证计划 → 信息缺口。
4. **Snapshot 驱动拓扑**：拓扑展示**复用 Snapshot 数据**而非在生成时再执行 `lscpu` / `npu-smi`；轻量内联 SVG 仅承担"Server → NUMA → NPU + HCCS/PIX/PXB/PHB/SYS 链路"可视化，不依赖 pyvis、networkx、外部 JS 或 CDN；配色与链路语义借鉴原 `topology_visualizer.py`。
5. **缺字段即"信息缺口"，禁止猜测**：若 Snapshot 缺 `npu_topology.devices` / `npu_topology.devices[*].numa_node` / `numa_topology.nodes` / `key_processes` 等关键字段，必须显式渲染"信息缺口"，而不是推断或拿普通线程冒充关键线程。
6. **可自动执行的条件约束**：自动执行仅限"低风险 taskset"且需用户确认；若推荐 CPU range 超出 cgroup `cpuset_cpus_effective`，明确显示"不可自动执行"；进阶方案（改启动命令、`numactl`、PyTorch/OpenMP/DataLoader 配置）第一版**只生成建议，不自动执行**，且通常需要重启业务。

---

## 【关键机制与数据】

- **报告生成侧的数据源（原文：§5）**：拓扑关系优先来自 Snapshot 中的 `npu_topology.devices`、`npu_topology.devices[*].numa_node`、`numa_topology.nodes` 字段，报告生成阶段**不重跑** `lscpu` / `npu-smi`，避免重执行带来的非确定性。
- **可执行决策的四元判定（原文：§3 摘要卡片）**：当前状态（明显不合理 / 部分不合理 / 基本合理 / 信息不足）、最高风险（高 / 中 / 低 / 信息）、主要问题（未绑核、跨 NUMA、线程池过载、CPU range 重叠）、推荐动作（保守 taskset / 补充信息 / 保持现状并验证），以及是否可自动执行（仅低风险 taskset 需确认 / 否）。
- **关键进程分类（原文：§7）**：6 类——主调度进程、SQ 线程（如 Ascend `devN_sq_task`）、NPU 固定线程、通信线程（HCCL/通信 worker）、DataLoader 线程（PyTorch DataLoader worker）、Top CPU 线程；展示字段为 PID、TID、名称、NPU、CPU%、NUMA、分类来源。
- **风险分层（原文：§8）**：每个问题卡片按严重程度排序 high → medium → low → info；卡片必含证据（如 `Cpus_allowed_list=0-127`、NUMA 节点数=2 等具体观测值）作为判断依据。
- **NUMA 关系卡（原文：§5 示例）**：每张卡同时承载 CPU Range、Core 数（physical / logical）、本地 NPU（含 PCI BDF 与 local CPU range 与 Health）、进程 / Rank / Worker 的当前-有效-推荐 CPU range 三栏对照、跨 NUMA 状态；示例中给出 NUMA 0: `CPU Range 0-31,64-95`、`physical=32, logical=64`、NPU 0（PCI `0000:81:00.0`、local CPU `0-31,64-95`、Health ok）、PID 12345/rank0/NPU 0、当前 `0-127` / 有效 `0-63` / 推荐 `0-31`、状态"跨 NUMA"。
- **CPU 网格 tooltip（原文：§6）**：第一版不要求复杂交互，仅用 `title` tooltip 展示 CPU 编号、NUMA、Core（socket-core 形式）、SMT siblings、Used by（PID/TID）；示例 `CPU 48 / NUMA: 1 / Core: socket1-core16 / SMT siblings: 48,112 / Used by: PID 12345 / TID 12345`。
- **自动执行前置信息（原文：§10）**：必须展示执行后端（taskset / internal-script）、动作类型（低风险临时绑核）、确认要求、回滚状态文件 `rollback-state.json`、回滚命令（如 `taskset -cp 0-127 12345`）、风险提示（如 CPU range 过窄致线程竞争）。
- **信息缺口集中呈现（原文：§12）**：典型缺失项及其影响——缺 `npu_topology.devices[*].numa_node` 则无法判断 NPU locality；缺 `pytorch.dataloader.num_workers` 则无法判断 DataLoader 是否过载；缺 `baseline_metrics.training.step_time_ms_p99` 则无法量化优化收益。

---

## 【表格解读】

### 表 1　当前绑核状态字段（§4）

| 字段 | 说明 |
|------|------|
| PID | 目标进程。 |
| Rank / 实例 | 训练 rank 或推理实例。 |
| NPU | 对应 NPU。 |
| 当前 CPU Range | `Cpus_allowed_list`。 |
| cgroup 有效 CPU | `cpuset_cpus_effective`。 |
| 当前运行 NUMA | Top 线程所在 NUMA。 |
| 是否跨 NUMA | 是 / 否 / 信息不足。 |
| 推荐 CPU Range | 规则生成结果。 |

**逐行解读**：PID 把诊断锚定到具体进程；Rank/实例把多卡训练或推理实例与进程一一对应；NPU 列确立 CPU 与 NPU 的归属关系；当前 CPU Range 直接对应 Linux 的 `Cpus_allowed_list`，是 affinity 真相的权威来源；cgroup 有效 CPU 对应 `cpuset.cpus_effective`，反映容器/切片实际生效范围——这条比 `Cpus_allowed_list` 更"硬"，往往才是真实可用集合；当前运行 NUMA 用 Top 线程所在 NUMA 反映**实际**而非**声明**的 locality；是否跨 NUMA 是问题判定核心（是/否/信息不足三态）；推荐 CPU Range 是规则引擎产物，与前两栏形成"声明 / 实际 / 建议"的三栏对照。

### 表 2　CPU 网格颜色语义（§6）

| 状态 | 颜色/样式 |
|------|-----------|
| 普通 CPU | 浅灰色。 |
| 当前 allowed CPU | 蓝色。 |
| 推荐 CPU | 绿色。 |
| 当前 allowed 且推荐 | 青色。 |
| Top CPU 线程所在 CPU | 深色边框。 |
| 跨 NUMA 或冲突 CPU | 红色。 |
| cgroup 不允许 CPU | 灰色斜纹或降低透明度。 |
| SMT sibling | 虚线边框或同 core 标记。 |
| 信息缺失 | 灰色说明卡。 |

**逐行解读**：浅灰为基色，避免 CPU 海洋一片亮色造成视觉噪声；蓝色描出 affinity 当前生效范围，绿色描出建议范围，二者重叠部分用青色——这是网格最核心的视觉信号，让用户一眼看出"应做改动幅度与位置"；深色边框专标 Top CPU 线程所在 CPU，把"热点"从颜色海洋里挑出来；红色承担告警职能，覆盖跨 NUMA 与冲突两类问题；灰色斜纹/降透明度明确区分"理论上能跑、cgroup 不允许"的 CPU，避免把容器外 CPU 当成可用资源；虚线边框/同 core 标记呈现 SMT 兄弟关系，对超线程绑核决策至关重要；信息缺失直接用灰色说明卡表达"未知"，避免误判为正常。

### 表 3　关键进程与线程分类（§7）

| 类别 | 说明 |
|------|------|
| 主调度进程 | 目标 PID、rank 主线程或模型服务入口进程。 |
| SQ 线程 | Ascend `devN_sq_task` 等固定运行时线程。 |
| NPU 固定线程 | 与特定 NPU 亲和或运行时绑定的线程。 |
| 通信线程 | HCCL、通信 worker 等线程。 |
| DataLoader 线程 | PyTorch DataLoader worker 或相关线程。 |
| Top CPU 线程 | 采样窗口内 CPU 使用率最高的关键线程。 |

**逐行解读**：主调度进程是绑核生效的真正对象；SQ 线程（`devN_sq_task`）与 NPU 固定线程是 Ascend 运行时强绑的特殊线程，应避免被 taskset 误伤；通信线程（HCCL/通信 worker）跨 NUMA 时延敏感，是优化高优先级目标；DataLoader 线程对应 PyTorch DataLoader worker 数——过多会与主进程争核；Top CPU 线程反映采样窗口内真实热点，可能与上述分类重叠也可能独立存在，用于发现"未在分类里但实际吃 CPU"的线程。

### 表 4　保守方案展示字段（§9）

| 对象 | 当前 CPU Range | 推荐 CPU Range | 命令 | 回滚命令 | 风险 |
|------|----------------|----------------|------|----------|------|

**逐行解读**：6 字段形成"目标—现状—建议—执行—撤回—风险"的闭环。用户能看到该对象当前的 CPU range 与规则推荐的差异；命令列直接给出可粘贴执行的 `taskset` 或内部脚本命令；回滚命令保证误操作可逆，是保守方案的精髓；风险列（如 CPU range 过窄致线程竞争）给出预期副作用；表格形式天然适合"按对象"逐条审阅与勾选。

### 表 5　进阶方案展示字段（§9）

| 对象 | 推荐配置 | 原因 | 风险 | 验证指标 |
|------|----------|------|------|----------|

**逐行解读**：与保守方案不同，进阶方案不直接给"命令行"，而是给"配置项"（启动命令、`numactl`、PyTorch/OpenMP/DataLoader 参数）。原因列说明为什么这样配；风险列通常涉及重启、跨组件耦合；验证指标列把"是否达成预期"具象化（如 step time p99、NPU util 波动）。这一表格的设计暗含"先保守验证收益，再升级到进阶方案"的实施节奏。

### 表 6　验证计划 before/after 对比表（§11）

| 指标 | 优化前 | 优化后 | 变化 | 是否符合预期 |
|------|--------|--------|------|--------------|
| Throughput / QPS | | | | |
| Step time / p99 latency | | | | |
| NPU utilization | | | | |
| Host CPU utilization | | | | |
| Context switch | | | | |
| CPU migration | | | | |

**逐行解读**：6 个指标覆盖"业务侧—运行时侧—OS 调度侧"三层。Throughput/QPS 与 Step time/p99 latency 是业务效果金指标；NPU utilization 反映 NPU 是否被喂饱或喂不均；Host CPU utilization 看主机侧是否过载；Context switch 与 CPU migration 是绑核生效的直接证据——绑核后这两项通常应显著下降。表格留空"优化前/后"两栏是报告生成时的占位，用户跑验证后自行填充。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **上游数据源**：整份报告由 Snapshot 数据驱动——`npu_topology.devices`、`npu_topology.devices[*].numa_node`、`numa_topology.nodes`、`snapshot.key_processes`、`pytorch.dataloader.num_workers`、`baseline_metrics.training.step_time_ms_p99` 等字段共同决定各 section 能呈现多少内容；缺字段时统一落入 §12"信息缺口"。
- **既有可视化模块**：拓扑 SVG 的"节点配色与链路类型语义"借鉴自原 `topology_visualizer.py`，但本报告刻意剥离其对 pyvis/networkx/外部 JS/CDN 的依赖，转为"轻量内联 SVG"。
- **系统工具依赖**：报告**展示**会引用 `taskset -cp <range> <pid>`、`taskset -cp 0-127 12345`、`numactl`、`lscpu`、`npu-smi` 等命令的语义，但**执行**仅在自动绑核区使用 `taskset` 或 internal-script。
- **运行时关联对象**：HCCS / PIX / PXB / PHB / SYS 等 NPU interconnect 链路在 §5 SVG 中作为边类型呈现；`Cpus_allowed_list` 与 `cpuset.cpus_effective` 是 §4 当前绑核状态的两条核心事实来源。
- **回滚与状态文件**：§10 的 `rollback-state.json` 是自动绑核与回滚的状态锚点，与 §9 保守方案的"回滚命令"列共同构成可逆执行链路。
- **下游使用方式**：报告对"低风险 taskset"可自动执行（需确认），对进阶方案仅生成建议、不自动执行；用户通过 §11 验证计划自行判定效果。

> 文档内部链接：（无）。

---

## 【使用方法】

**启用方式 / 生成入口**（原文未涉及具体调用命令，仅给出产物形态与生成约束）：
- 在 Linux 节点上生成；
- 输出为单文件 HTML，文件名建议 `mindstudio-cpu-binding-report-<timestamp>.html`；
- 文件必须满足：CSS 内联于 `<style>`、JS 内联于 `<script>`、Snapshot 摘要可内嵌为 JSON script block、不引用本地绝对路径、不引用外部网络资源。

**配置项 / 命令**（原文示例中给出的具体命令）：
- 回滚命令示例：`taskset -cp 0-127 12345`；
- 自动执行后端二选一：`taskset` 或 `internal-script`；
- 进阶方案可能调整：`numactl`、启动命令、PyTorch / OpenMP / DataLoader 配置（第一版只生成建议，不自动执行，通常需重启业务）。

**交互**：
- 第一版仅支持 `title` tooltip（展示 CPU 编号、NUMA、Core、SMT siblings、Used by），不要求复杂交互。
