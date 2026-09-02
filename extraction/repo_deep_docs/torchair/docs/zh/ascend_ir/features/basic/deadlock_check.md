# 多流并发死锁检测功能

> 仓 `torchair` · 路径 `docs/zh/ascend_ir/features/basic/deadlock_check.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/torchair/docs/zh/ascend_ir/features/basic/deadlock_check.md

# 多流并发死锁检测功能 — 深度解读

## 【定位】

本文档描述 TorchAir 中针对多流并发场景下通信算子争抢 AIV 核心资源的死锁风险进行**自动化静态检测**的能力：当多个流上的通信算子同时就绪，其请求的 vector 核心数总和超过硬件可用上限时，调度器无法满足任何一方，从而形成死锁——本功能即在图编译阶段（而非运行时）提前暴露此类风险。

---

## 【技术要点】

1. **检测对象**：多流（multi-stream）并发场景下、进入就绪状态的通信类算子（communication operators）。
2. **触发条件**：多个通信算子同时就绪，且它们请求的 **AIV（AI Vector）核心数量总和 > 硬件总可用 AIV 核心数**。
3. **死锁本质**：每个任务都在等待其他任务释放核心资源，但没有任务能拿到足够资源开始运行——一种"互相等待、谁也无法推进"的状态。
4. **配置开关**：通过 `torchair.CompilerConfig` 的 `config.debug.deadlock_check`（bool）启用，默认 `False`。
5. **使用约束**：不支持动态图（`dynamic=True`），即该功能仅适用于静态图编译场景。
6. **检测产物**：脚本同级目录生成 3 个 JSON 文件，并在打屏日志中逐对列出冲突算子。

---

## 【关键机制与数据】

**死锁形成原理（原文）：**
> "当多个流上的通信类算子同时进入就绪状态，且它们所请求的 AIV 核心数量总和超过了硬件的总可用数，NPU 调度器将无法同时满足所有任务的资源分配需求，从而形成死锁——即每个任务都在等待其他任务释放核心资源，但没有任何任务能够获得足够的资源以开始运行。"

**关键数据（原文示例日志）：**
- 检测报告死锁对数量：「56 conflicting pair(s)」
- 单个算子占用 AIVEC 示例：`aiv_all_gather_bfloat16_t` 占 32 个 vector 核；`MoeDistributeDispatchV2` 占 24 个 vector 核；`MoeDistributeCombineV2` 占 24 个 vector 核。
- 判定阈值示例：`sum=56 > 48`，即该设备总可用 vector 核心数为 **48**。
- 标识维度：流 ID（stream316 / stream317）+ TaskId（如 4、5、9、17、20）。

**产物链路（原文）：**
1. `debug_output_graph_0_timestamp*_pid_*.json` —— 原始 dump 的 IR 图 JSON；
2. `debug_output_graph_0_timestamp*_pid_*_filtered.json` —— 过滤掉计算算子后仅保留通信相关算子的 JSON；
3. `debug_output_graph_0_timestamp*_pid_*_filtered_deadlock_check.json` —— 死锁检测结果 JSON（最终判定报告）。

文件命名中 `timestamp20260414141935_pid_494263` 为示意示例，分别对应时间戳与进程 PID。

---

## 【表格解读】

**表 1 参数说明（原文逐字还原）：**

| 参数名 | 参数说明 |
|---|---|
| deadlock_check | 是否开启死锁检测功能，bool类型。False（默认值）：不开启死锁检测。True：开启死锁检测。 |

**逐行解读：**
- 该表是功能唯一的可配置项，作用于 `torchair.CompilerConfig().debug` 命名空间下。
- 字段类型为 Python `bool`，语义为「死锁检测开关」，无中间态/枚举值。
- 默认 `False`，表示该检测默认关闭，仅在用户主动开启时才会执行额外的图分析并产出 JSON 与日志。
- 开启后才会触发后述的产物生成流程与打屏日志，因此这是用户控制该功能的**唯一入口**。

---

## 【公式解读】

原文无显式公式，但隐含判定条件（按原文表述还原为数学形式）：

$$
\sum_{i \in \text{ready communication ops}} \text{AIVEC}(op_i) \;>\; \text{AIVEC}_{\text{total}}
$$

**符号含义：**
- $\text{AIVEC}(op_i)$：第 $i$ 个同时就绪的通信算子所请求的 AIV（vector）核心数量。
- $\text{AIVEC}_{\text{total}}$：当前 NPU 设备可用的 AIV 核心总数（在原文示例中为 48）。
- 求和范围：处于 ready 状态、跨多个 stream 的全部通信算子。
- 判定：若求和结果严格大于硬件上限，则标记为存在死锁风险，并在日志中列出所有"两两冲突"的对（pair），其冲突度量即为 `sum > total` 的差值。

原文示例即对应：`32 + 24 = 56`，而 `56 > 48`，故报为冲突。

---

## 【关联】

- **上游特性 — 多流并发（multi_stream）**：本文档的检测场景完全限定在多流并发中，文末链接 `../advanced/multi_stream.md` 指向多流特性文档。死锁风险只有在用户使用多流并发能力、且不同流上同时承载通信算子时才会暴露，因此本功能是多流特性的"安全网/编译期校验器"。
- **下游产物 — IR/图分析**：检测以 IR 图（过滤掉计算算子后的通信子图）作为输入，输出仍是 JSON 形式的图数据，属于图编译阶段（graph-mode）分析任务，不涉及运行时插桩。
- **运行时边界**：功能不依赖、不影响运行时调度行为，仅在编译期给用户反馈；因此与 dynamic 模式不兼容（动态图缺乏静态可分析的 IR 形态）。

---

## 【使用方法】

启用方式（原文给出）：

```python
import torchair
config = torchair.CompilerConfig()
config = CompilerConfig()
config.debug.deadlock_check = True
```

**执行后行为（原文）：**
- 若存在死锁风险：脚本同级目录生成 3 个 JSON（原始 dump → 过滤通信算子 → 死锁检测结果），同时在终端打屏输出 `[RESULT] Deadlock risk detected! N conflicting pair(s):` 并逐行列出每对冲突算子的流 ID、TaskId、算子名、AIVEC 数量及 `sum > total` 判定。
- 若无死锁风险：原文未涉及具体表现（即不会打印 `[RESULT] Deadlock risk detected!` 日志，产物 JSON 是否仍生成原文未明确说明）。

**约束（原文）：**
- 不支持 `dynamic=True` 的动态图场景。
