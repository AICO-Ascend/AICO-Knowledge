# INDUCTOR_ASCEND_COSTMODEL_RATIO

> 仓 `pytorch` · 路径 `torch_npu/_inductor/docs/feature/costmodel/INDUCTOR_ASCEND_COSTMODEL_RATIO.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/pytorch/torch_npu/_inductor/docs/feature/costmodel/INDUCTOR_ASCEND_COSTMODEL_RATIO.md

# INDUCTOR_ASCEND_COSTMODEL_RATIO 一体化深度解读

---

## 【定位】

本文档描述了 Inductor-Ascend 后端中用于控制 **CostModel 预筛选阶段保留候选 config 比例** 的环境变量 `INDUCTOR_ASCEND_COSTMODEL_RATIO`，通过该比例在「筛选激进程度」与「首次编译开销」之间提供可调旋钮，以在保证不遗漏最优 config 的前提下降低首次编译成本。

---

## 【技术要点】

1. **核心作用**：在 CostModel 启用后，Inductor-Ascend 会根据 CostModel 返回的 **预测耗时** 对候选 config 排序，并按 `INDUCTOR_ASCEND_COSTMODEL_RATIO` 指定的比例 **仅保留预测耗时较短的一部分 config** 进入后续 precompile 流程。
2. **取值范围**：合法范围为 `(0, 1]`；当取值 `≤ 0` 或 `> 1` 时，**回退到默认值 `0.25`**。
3. **边界语义**：
   - 取值 = `1`：等价于 **关闭 CostModel 预筛选**，全部候选 config 都进入 precompile。
   - 取值未设置：使用默认 `0.25`，即仅保留前约 25% 的"快"config。
   - 取值 ∈ `(0, 1)`：按比例截断 CostModel 排序结果。
4. **生效前提**：仅在 `INDUCTOR_ASCEND_ENABLE_COSTMODEL=1` 时该变量才有意义，否则不生效。
5. **兜底机制**：若被 CostModel 筛选保留的 config **全部无法编译通过**，Inductor-Ascend 会回退使用 **被 CostModel 筛掉的 config** 进行兜底编译，避免编译流程因筛选失败而中断。
6. **支持型号**：当前仅在 <term>Atlas A5 系列产品</term> 上提供该能力（原文仅列出此一项）。

---

## 【关键机制与数据】

**工作原理（原文描述）：**

1. **筛选阶段**：启用 CostModel 后，Inductor-Ascend 调用 CostModel 对所有候选 config 进行 **预测耗时估算**。
2. **排序与截断**：依据预测耗时对候选 config 升序排序，并按 `INDUCTOR_ASCEND_COSTMODEL_RATIO` 给定的比例保留前若干个。
3. **后续流程**：被保留的 config 进入 **precompile 流程**（含实际编译与 profiling），由真实运行结果决定最终选择。
4. **兜底分支**：当保留下来的所有 config 都编译失败时，触发 fallback，使用 **被筛掉的候选** 继续编译，确保不出现空集。

**性能权衡（原文要点，原文未给出具体性能数字）：**

- **保留比例越小** → 进入 precompile 的 config 越少 → **首次编译开销越低** → 但 **可能错过实际最优 config**（因为预测耗时与真实耗时不完全一致）。
- **保留比例越大**（接近 1）→ 更多候选进入实测 → 首次编译开销升高 → 找到最优 config 的概率提升。

> 原文未给出实测编译耗时、miss rate 等量化性能数据。

---

## 【表格解读】

**原文表格逐字还原：**

| 值 | 说明 |
|---|---|
| 未设置 | 使用默认值0.25 |
| (0, 1) | 按比例保留CostModel预测结果中耗时较短的config |
| 1 | 不进行CostModel预筛选 |

**逐行解读：**

| 行 | 取值 | 解读 |
|---|---|---|
| 1 | `未设置` | 环境变量未导出时，Inductor-Ascend **默认使用 0.25**，即只保留约四分之一的候选 config 进入 precompile，作为保守而常用的折中默认值。 |
| 2 | `(0, 1)` | 合法工作区间，CostModel 按该比例 **截断预测耗时升序结果**，仅保留"较优"部分，比例越小筛选越激进，编译开销越低。 |
| 3 | `1` | 退化为 **不做 CostModel 预筛选**，等价于关闭筛选功能，所有候选 config 都进入 precompile，保证不会因 CostModel 预测偏差而丢解，但首次编译成本最高。 |

> 表格未给出 `0` 与 `>1` 的独立行；但正文已说明这两种非法值会回退到默认值 `0.25`。

---

## 【公式解读】

**原文无公式。**

> 说明：文档以"按比例保留"的方式描述筛选过程，未给出形如 `keep_count = total_count × ratio` 之类的显式数学表达式，故按要求不进行臆造。

---

## 【关联】

本特性作为 CostModel 流程的 **调参旋钮**，与以下上下文存在紧密耦合关系（基于原文表述）：

- **上游开关**：`INDUCTOR_ASCEND_ENABLE_COSTMODEL` —— `INDUCTOR_ASCEND_COSTMODEL_RATIO` 仅在其置为 `1` 时才生效，是其严格前提。
- **筛选目标对象**：候选 **config**（即 Inductor 在 autotuning 阶段为算子生成的多种编译方案），与 Inductor-Ascend 的 **precompile** 流程直接衔接。
- **兜底路径**：当筛选结果"全军覆没"时，会回退到 **未通过 CostModel 筛选的 config 集合**，这意味着筛选与真实编译之间存在容错链路，但兜底本身会引入额外编译成本。
- **支持范围**：受限于 <term>Atlas A5 系列产品</term>，在其他昇腾型号上的可用性原文未列出。

> 文末未提供内部链接，故不做外部链接跳转解读。

---

## 【使用方法】

**启用方式（原文配置示例）：**

```shell
export INDUCTOR_ASCEND_ENABLE_COSTMODEL=1
export INDUCTOR_ASCEND_COSTMODEL_RATIO=0.25
```

**配置项速查：**

| 环境变量 | 取值 | 含义 |
|---|---|---|
| `INDUCTOR_ASCEND_ENABLE_COSTMODEL` | `1` | 启用 CostModel（本变量的前置条件） |
| `INDUCTOR_ASCEND_COSTMODEL_RATIO` | 未设置 | 使用默认值 `0.25` |
| `INDUCTOR_ASCEND_COSTMODEL_RATIO` | `(0, 1)` | 按比例保留预测耗时较短的 config |
| `INDUCTOR_ASCEND_COSTMODEL_RATIO` | `1` | 不进行 CostModel 预筛选 |
| `INDUCTOR_ASCEND_COSTMODEL_RATIO` | `≤0` 或 `>1` | 非法值，回退到默认值 `0.25` |

**调优建议（基于原文约束）：**

- 希望 **降低首次编译开销**：调小 ratio（如 0.1），但需接受可能错过最优 config 的风险。
- 希望 **最大化命中最优 config**：将 ratio 调大或设为 `1`，代价是首次编译开销上升。
- 若筛选后所有 config 都编译失败：无需手动操作，Inductor-Ascend 会自动使用被筛掉集合进行兜底编译。
