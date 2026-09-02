# HTML 报告设计

> 仓 `msagent` · 路径 `skills/profiler/mindstudio-cpu-binding/docs/html-report-design.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msagent/skills/profiler/mindstudio-cpu-binding/docs/html-report-design.md

# 一体化深度解读：mindstudio-cpu-binding HTML 报告设计

---

## 【定位】

这篇文档定义 `mindstudio-cpu-binding` 技能输出的 HTML 报告的页面结构、内容布局、配色语义、信息缺口处理与文件可移植性约束，用于在 Linux 节点生成一个**单文件、离线可看、结论优先**的 CPU 绑核诊断报告。

---

## 【技术要点】

1. **报告形态约束（原文 §1、§13）**：输出单一自包含 HTML 文件；CSS 内联于 `<style>`、JavaScript 内联于 `<script>`、Snapshot 数据可内嵌为 JSON script block；不引用外部 CDN、字体、图片、JS 包，不引用本地绝对路径；命名建议 `mindstudio-cpu-binding-report-<timestamp>.html`，跨 Linux/Windows 浏览器可直接打开。

2. **结论优先的摘要卡片（原文 §3）**：页面顶部用一张卡片回答四个核心问题——「当前状态（明显不合理 / 部分不合理 / 基本合理 / 信息不足）」「最高风险（高 / 中 / 低 / 信息）」「主要问题（未绑核、跨 NUMA、线程池过载、CPU range 重叠）」「推荐动作」「是否可自动执行」，避免报告变成复杂 dashboard。

3. **基于 Snapshot 的拓扑展示（原文 §5）**：报告**不在生成阶段重新执行 `lscpu` 或 `npu-smi`**，而是直接消费 Snapshot 中的 `npu_topology.devices`、`npu_topology.devices[*].numa_node`、`numa_topology.nodes` 等字段；缺失则必须显示信息缺口而非猜测。拓扑用「轻量内联 SVG（展示 Server→NUMA→NPU 与 HCCS / PIX / PXB / PHB / SYS 链路）」+「NUMA 关系卡片（CPU range / 本地 NPU / 目标 PID-rank-worker / 当前-有效-推荐 CPU range / 跨 NUMA 状态）」两层呈现，借鉴原 `topology_visualizer.py` 配色与链路语义，但不依赖 pyvis / networkx / 外部 JS / CDN。

4. **逻辑 CPU 网格 + 颜色语义（原文 §6）**：每个逻辑 CPU 一个方块，按 NUMA 分块排布，状态由颜色与边框表达——普通 CPU 浅灰、当前 allowed CPU 蓝色、推荐 CPU 绿色、二者交集青色、Top CPU 线程所在 CPU 深色边框、跨 NUMA 或冲突红色、cgroup 不允许 CPU 灰色斜纹/降透明度、SMT sibling 虚线边框/同 core 标记、信息缺失用灰色说明卡。交互仅用 `title` tooltip（CPU / NUMA / Core / SMT siblings / Used by）。

5. **进程/线程分类与卡片化问题（原文 §7、§8）**：从 `snapshot.key_processes` 中区分六类对象——主调度进程、Ascend SQ 线程（`devN_sq_task`）、NPU 固定线程、HCCL 等通信线程、PyTorch DataLoader worker、Top CPU 线程；每个问题独立卡片、按 `[R001]` 编号、按 high → medium → low → info 严重程度排序，包含「严重程度 / 影响 / 证据 / 判断 / 建议 / 验证」六段。

6. **双方案推荐 + 自动执行门禁 + 回滚（原文 §9、§10）**：保守方案用 `taskset` 或内部脚本临时调整目标 PID、可立即回滚、不修改系统级配置；进阶方案涉及 `numactl`、启动命令、PyTorch / OpenMP / DataLoader 配置，第一版**只生成建议不自动执行**。自动执行门禁判定条件示例：推荐 CPU range 超出 `cgroup cpuset_cpus_effective` 时显示「不可自动执行」；通过时需展示执行后端（taskset / internal-script）、当前与目标 affinity、`rollback-state.json`、回滚命令（`taskset -cp <原affinity> <PID>`）。

---

## 【关键机制与数据】

**数据流（原文）：** Snapshot（包含 `npu_topology.devices`、`npu_topology.devices[*].numa_node`、`numa_topology.nodes`、`snapshot.key_processes` 等）→ 直接驱动 HTML 报告生成 → 不在报告生成阶段调用 `lscpu` / `npu-smi`（原文 §5）。

**页面骨架（原文 §2）：** 报告包含 0–9 共十个 section——摘要卡片、当前绑核状态、CPU/NPU/NUMA 拓扑、CPU/NUMA 逻辑网格、关键进程与线程、问题发现、推荐优化方案、自动绑核与回滚、验证计划、信息缺口。

**诊断结论语义（原文 §3）：** 当前状态四档（明显不合理 / 部分不合理 / 基本合理 / 信息不足）、风险四档（高 / 中 / 低 / 信息）、问题类型四类（未绑核、跨 NUMA、线程池过载、CPU range 重叠）。

**问题卡片样例数据（原文 §8）：** `[R001] 进程未绑定 CPU`，严重程度高，影响稳定性/时延，证据 `PID 12345 Cpus_allowed_list=0-127，机器 NUMA 节点数=2`，判断进程允许在全机 CPU 上运行、可能带来跨 NUMA 调度和 CPU migration，建议将 rank0 绑定到 NPU0 本地 NUMA 的 CPU 子集，验证观察 CPU migration、step time p99、NPU utilization 波动。

**NUMA 关系卡片样例数据（原文 §5）：** NUMA 0 — CPU Range `0-31,64-95`、physical core=32、logical core=64；本地 NPU 0 / PCI `0000:81:00.0` / Local CPU `0-31,64-95` / Health ok；PID 12345 / rank0 / NPU 0、当前 CPU `0-127`、有效 CPU `0-63`、推荐 CPU `0-31`、状态跨 NUMA。

**验证对比维度（原文 §11）：** Throughput / QPS、Step time / p99 latency、NPU utilization、Host CPU utilization、Context switch、CPU migration 六项，每项记录优化前 / 优化后 / 变化 / 是否符合预期。

**tooltip 样例（原文 §6）：** CPU 48，NUMA 1，Core socket1-core16，SMT siblings 48,112，Used by PID 12345 / TID 12345。

**文件名约定（原文 §13）：** `mindstudio-cpu-binding-report-<timestamp>.html`。

---

## 【表格解读】

### 表 1 — 当前绑核状态字段（原文 §4）

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

解读：该表定义「按进程和线程展示当前绑核状态」的列结构。三档 CPU range（当前、cgroup 有效、推荐）的并列便于一眼对比亲和范围与 cgroup 授权范围的差异；「是否跨 NUMA」显式引入「信息不足」第三态，与摘要卡片的「信息不足」语义保持一致。原文 §4 注明线程很多时只展示 Top CPU 线程和异常线程。

---

### 表 2 — CPU 网格颜色/样式语义（原文 §6）

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

解读：该表定义逻辑 CPU 方块的视觉编码。普通 CPU 用浅灰作底色，「当前 allowed 蓝色」与「推荐 绿色」的交集使用「青色」突出两者一致——这是颜色语义中唯一的「合取」项；冲突/跨 NUMA 红色与 cgroup 不允许的灰色斜纹形成「问题态/受限态」双重信号；SMT sibling 用虚线/同 core 标记而非填色，保留与底层硬件关系的可识别性；信息缺失以整张灰色说明卡替代方块，避免空白被误读为「正常」。

---

### 表 3 — 关键进程与线程分类（原文 §7）

| 类别 | 说明 |
|------|------|
| 主调度进程 | 目标 PID、rank 主线程或模型服务入口进程。 |
| SQ 线程 | Ascend `devN_sq_task` 等固定运行时线程。 |
| NPU 固定线程 | 与特定 NPU 亲和或运行时绑定的线程。 |
| 通信线程 | HCCL、通信 worker 等线程。 |
| DataLoader 线程 | PyTorch DataLoader worker 或相关线程。 |
| Top CPU 线程 | 采样窗口内 CPU 使用率最高的关键线程。 |

解读：六类对象覆盖训练/推理场景下对 Host CPU 绑核诊断最具影响力的线程。`devN_sq_task` 是 Ascend 设备固定运行时线程，SQ 线程与 NPU 固定线程共同构成「与硬件绑死的亲和约束」，是绑核方案不能破坏的硬约束；通信线程（HCCl/worker）与 DataLoader 线程是业务侧可调节对象；Top CPU 线程提供采样窗口的实证依据。原文 §7 强调若 `key_processes` 缺失必须显示信息缺口，不能把普通线程列表误当作关键线程。

---

### 表 4 — 保守方案展示字段（原文 §9）

| 对象 | 当前 CPU Range | 推荐 CPU Range | 命令 | 回滚命令 | 风险 |
|------|----------------|----------------|------|----------|------|

解读：六列结构完整覆盖「变更对象—变更前状态—变更后状态—操作—撤销—风险」决策六要素；命令列对应 `taskset -cp <推荐range> <PID>` 或内部脚本，回滚命令对应 `taskset -cp <原range> <PID>`，原文 §10 给出样例 `taskset -cp 0-127 12345`。风险列为用户提供变更副作用的预期。

---

### 表 5 — 进阶方案展示字段（原文 §9）

| 对象 | 推荐配置 | 原因 | 风险 | 验证指标 |
|------|----------|------|------|----------|

解读：进阶方案因涉及启动命令、`numactl`、PyTorch / OpenMP / DataLoader 配置而需要重启业务，原文 §9 明确「第一版只生成建议，不自动执行」。验证指标列与表 6 的六项指标（Throughput / Step time / NPU utilization / Host CPU utilization / Context switch / CPU migration）形成「方案—验证」闭环。

---

### 表 6 — 验证计划 before/after 对比（原文 §11）

| 指标 | 优化前 | 优化后 | 变化 | 是否符合预期 |
|------|--------|--------|------|--------------|
| Throughput / QPS |  |  |  |  |
| Step time / p99 latency |  |  |  |  |
| NPU utilization |  |  |  |  |
| Host CPU utilization |  |  |  |  |
| Context switch |  |  |  |  |
| CPU migration |  |  |  |  |

解读：六项指标覆盖吞吐、时延、硬件利用率、调度开销四个维度——Context switch 与 CPU migration 直接反映绑核效果（绑核通常降低这两项），Step time p99 反映长尾时延，NPU utilization 反映 host 调度对加速器的影响。表格刻意留空，等用户实测后填写，与原文 §11「展示 before/after 对比表」的措辞一致。

---

## 【公式解读】

原文无公式。

---

## 【关联】

原文 §5 明确报告消费 Snapshot 中的 `npu_topology.devices`、`npu_topology.devices[*].numa_node`、`numa_topology.nodes` 字段，§7 消费 `snapshot.key_processes`，§10 引用 `cpuset_cpus_effective`、§8 问题编号 `[R001]` 与 §10 `rollback-state.json`、§13 文件名 `mindstudio-cpu-binding-report-<timestamp>.html`——这些字段与文件均属于 `mindstudio-cpu-binding` 技能的上下游数据契约，文档强调缺失时必须显示「信息缺口」而非猜测。原文 §5 还提及与原 `topology_visualizer.py` 在节点配色与链路语义（HCCS / PIX / PXB / PHB / SYS）上的借鉴关系，但解耦于 pyvis / networkx / 外部 JS / CDN，便于离线分发。

---

## 【使用方法】

原文未涉及启用方式或运行命令。该文档是 HTML 报告的**设计规范**，描述的是**被生成的报告本身**的形态约束、页面结构、配色语义、信息缺口处理与可移植性要求，而不是「如何运行 mindstudio-cpu-binding」。可执行产物的形态约束见原文 §13：文件名建议 `mindstudio-cpu-binding-report-<timestamp>.html`，Linux 节点生成，跨 Linux/Windows 浏览器直接打开。
