# 激活函数重计算

> 仓 `mindspeed` · 路径 `docs/zh/features/activation-function-recompute.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed/docs/zh/features/activation-function-recompute.md

【定位】
本文档描述的是 mindspeed（昇腾大模型加速库）中**「激活函数重计算」**特性——一种针对大模型训练中激活函数输出占用内存过大的内存优化方案，通过将重计算流程从反向调度中解耦，实现灵活的、按需的激活函数重计算。

---

【技术要点】

1. **核心问题**：传统重计算与反向计算绑定调度，对于 GELU 这类"计算量小但输出占用内存大"的激活函数，传统重计算无法省掉其输出激活值（因为下游模块 A 的反向早于 GELU 重计算触发，必须先保留 GELU 输出）。
2. **解决方案**：重新实现一套重计算框架，将重计算灵活插入到反向计算之前的任意位置，使激活函数的输出能在前向结束后即被释放，反向时再通过重计算恢复。
3. **关键机制**：`CheckpointWithoutOutput` 类 + `tensor.register_hook` 机制——前向完成后 `discard_output()` 丢弃物理存储保留逻辑视图，反向前由 `register_hook` 回调触发 `recompute` 重算。
4. **启用命令**：`--recompute-activation-function` 开启；`--recompute-activation-function-num-layers ${num}` 指定层数。
5. **兼容约束**：可与全重计算同时开启，但仅支持 `--recompute-method=block`；全重计算层与激活函数重计算层互不重叠（按层数各自执行，优先级为"先全重计算、后激活函数重计算"）；暂不兼容自适应重计算；非流水线并行时两类重计算层数之和应等于总层数。
6. **扩展能力**：`CheckpointWithoutOutput` 是通用模块，可对任意自定义函数灵活实现"丢弃输出 → 重计算恢复"流程。

---

【关键机制与数据】

**工作原理与数据流**（以 MLP 中 GELU 为例，原文图 1/图 2 描述）：

- **传统绑定流程**（图 1）：反向顺序为 `模块 A 的反向（需 GELU 输出的激活值）→ GELU 反向（与重计算绑定）`。由于模块 A 的反向早于 GELU 重计算触发，前向必须保留 GELU 的输出 `c`，节省内存失败。
- **新解耦流程**（图 2）：反向顺序变为 `GELU 函数重计算 → 模块 A 的反向`。前向 `4h→h` 计算完毕后立即将 `c` 释放（保留逻辑视图），在 `4h→h` 反向（grad）前，通过给 `d` 打 `tensor_hook` 的方式将 GELU 重计算插入到合适时机。
- **数据规模**（原文）：`b` 和 `c` 的 shape 为 `(batch, seq, 4*hidden_size)`，是激活函数重计算的主要节省对象。
- **收益特征**（原文）：GELU 等激活函数"计算量很小"，故重计算引入的性能损耗极小，但节省的内存可观。

**性能/内存数据**（原文：Llama-2-7b 场景下）：

| 配置 | 内存收益 |
|---|---|
| seq-length=12288、micro-batch-size=2、TP=4、DP=2（8卡单机） | 8.05 GB |
| seq-length=8096、micro-batch-size=2、TP=4、DP=2（8卡单机） | 5.31 GB |
| seq-length=16384、micro-batch-size=2、TP=4、DP=2（8卡单机） | 12.49 GB |
| seq-length=12288、micro-batch-size=1、TP=4、DP=2（8卡单机） | 4.04 GB |
| seq-length=12288、micro-batch-size=2、TP=8、DP=1（8卡单机） | 4.02 GB |

（原文未给出性能（吞吐/时延）下降的量化数字，仅定性表述"训练性能只会略微下降"。）

---

【表格解读】

**原文表格（逐字还原）**：

| 模型参数 | 设备数 | 内存收益 |
|---|---|---|
| seq-length=12288、micro-batch-size=2、TP=4、DP=2 | 8卡（单机） | 8.05GB |
| seq-length=8096、micro-batch-size=2、TP=4、DP=2 | 8卡（单机） | 5.31GB |
| seq-length=16384、micro-batch-size=2、TP=4、DP=2 | 8卡（单机） | 12.49GB |
| seq-length=12288、micro-batch-size=1、TP=4、DP=2 | 8卡（单机） | 4.04GB |
| seq-length=12288、micro-batch-size=2、TP=8、DP=1 | 8卡（单机） | 4.02GB |

**逐行解读**：

- **第 1 行（基准，bs=2, seq=12288, TP=4, DP=2）**：作为后续行对比的基准，节省 8.05 GB。
- **第 2 行（seq 降至 8096）**：相比第 1 行，序列长度减少约 1/3，内存收益下降到 5.31 GB——表明序列长度与内存节省近似正相关。
- **第 3 行（seq 增至 16384）**：序列长度比基准增加约 1/3，内存收益上升到 12.49 GB——进一步验证序列长度与节省内存近似线性关系。
- **第 4 行（bs 减半为 1，其他同基准）**：相比第 1 行，batch size 减半，内存收益下降到 4.04 GB（约一半）——表明 batch size 与节省内存也近似线性相关。
- **第 5 行（TP 由 4 改为 8，DP 由 2 改为 1）**：总设备数仍为 8，但张量并行度提高、数据并行度降低；内存收益下降到 4.02 GB，相比基准几近减半——说明该特性节省的主要是激活（与 micro-batch 内 seq×batch 相关）而非权重，TP 切分后单卡持有的激活张量更小，从而可节省的激活内存也减少。

整体规律（原文未直接给出，仅从表格推断）：节省内存量与 `seq-length × micro-batch-size` 强相关，TP 度提高会显著降低单卡可节省量。

---

【公式解读】

原文无数学公式。文档使用文字 + 流程图（伪代码形式）描述机制，核心逻辑可表述为：

```
传统反向:  backward(A)  →  recompute(GELU)  →  backward(GELU)
新框架反向: recompute(GELU) → backward(A)  →  backward(GELU)
```

对应原文 `CheckpointWithoutOutput` 的使用伪代码（保留原文符号含义）：

- `self.activation_checkpoint_manager = CheckpointWithoutOutput()`：实例化重计算管理器。
- `function_output = self.activation_checkpoint_manager.checkpoint(self.custom_function, False, function_input1, function_input2, ...)`：`checkpoint` 包裹自定义函数 `custom_function`，得到 `function_output`；参数 `False` 含义未在文档中明确说明（原文未注明）。
- `...(after used output)`：消费输出。
- `self.activation_checkpoint_manager.discard_output()`：丢弃输出的物理存储，保留逻辑视图。
- `module_output.register_hook(self.activation_checkpoint_manager.recompute)`：对下游张量注册 hook，反向传播时在合适时机触发 `recompute` 重新计算恢复张量。

文档明确提示："如要使用 `register_hook`，需要确保张量有梯度"。

---

【关联】

文档未提供文末内部链接，但基于内容可梳理以下关联关系：

- **全重计算（`--recompute-method`）**：可与本特性同时开启，但仅 `block` 方式兼容；二者在同一模型中按层互斥划分，全重计算层与激活函数重计算层不重叠。
- **流水线并行**：文档特别提示"在流水线并行未开启的情况下，全重计算层数和激活函数重计算层数之和应该等于总层数"，说明二者存在与流水线并行的交互约束。
- **自适应重计算**：明确"暂不兼容自适应重计算特性"，二者互斥。
- **`tensor_parallel.random` 模块**：`CheckpointWithoutOutput` 类位于 `mindspeed.core.tensor_parallel.random`，表明该特性复用了张量并行模块下的随机/重计算基础设施。
- **混合精度训练**：文档开篇提及"混合精度训练已成为标准实践"，本特性是在此背景下的内存优化手段之一。
- **`register_hook`（PyTorch 原生机制）**：作为反向插入重计算的底层技术依赖。

---

【使用方法】

**启用方式（原文有）**：

1. 脚本中添加 `--recompute-activation-function` 即可开启激活函数重计算。
2. 添加 `--recompute-activation-function-num-layers ${num}` 可指定激活函数重计算的层数。

**与全重计算同时开启的约束（原文有）**：

- 仅支持 `--recompute-method` 为 `block`。
- 全重计算层与激活函数重计算层互不重叠。
- 执行优先级：先全重计算层，后激活函数重计算层。
- 非流水线并行时，二者层数之和应等于总层数。
- 暂不兼容自适应重计算特性。

**扩展使用（原文有）**：

通过导入 `from mindspeed.core.tensor_parallel.random import CheckpointWithoutOutput`，可对自定义模块灵活实现"丢弃输出 + 反向 hook 重计算"流程。使用时须确保 `register_hook` 的张量 `requires_grad`（即有梯度），完整调用模式为：`checkpoint(func, flag, *inputs)` → 消费输出 → `discard_output()` → `module_output.register_hook(recompute)`。具体 `checkpoint` 第二个参数（如示例中的 `False`）的语义原文未明确说明。

## 图文联合解读

- `activation_function_a.png`: **图文联合解读：**

图示现有重计算框架MLP数据流：前向为h-4h→gelu→4h->h，反向为4h->h grad→gelu grad→h-4h grad，a/b/c/d分别为各模块输入输出张量。

**论证结论**：传统框架下重计算与反向绑定调度，反向时4h->h grad需先消费c，前向被迫保留gelu输出c（shape为batch×seq×4h的大张量），导致对gelu做重计算无法节省内存。

**与文档关系**：本图作为"图1 现有框架"与文档"挑战"段呼应，揭示重计算绑定的局限性；为"图2 灵活插入重计算"方案——通过tensor_hook将gelu重计算前置于4h->h grad之前、提前释放c——提供对比铺垫。
- `activation_function_b.png`: **图意**：左侧前向流为 a→h-4h→b→gelu→c→4h->h→d；右侧反向流为 4h->h grad→gelu grad→h-4h grad；中间的 gelu 节点表示重计算，由 b 触发、输出供 4h->h grad 使用。

**结论**：传统框架下重计算 gelu 被绑定在 gelu grad 附近，无法前移到 4h->h grad 之前，因此 c 必须在前向阶段保留，无法释放内存。

**与文档关系**：对应"图1 重计算与反向绑定"，论证传统调度灵活性受限，反衬出新框架通过 tensor_hook 灵活插入重计算的必要性。
