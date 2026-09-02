# Mamba-CP

> 仓 `mindspeed-llm` · 路径 `docs/zh/pytorch/features/mcore/mamba_context_parallel.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-llm/docs/zh/pytorch/features/mcore/mamba_context_parallel.md

# Mamba-CP 特性文档深度解读

---

## 【定位】

这篇文档描述了 mindspeed-llm 框架中面向 **Mamba 架构长序列训练**的 **Context Parallel（CP, 上下文并行）优化方案 Mamba-CP**——通过将 SSM 状态传递部分改造为全 rank 并发执行，并以计算-通信掩盖缓解传统 CP 的串行等待，从而在超长序列场景下显著降低显存并提升训练吞吐。

---

## 【技术要点】

1. **核心动机**：Mamba 解决了 Transformer 序列长度的平方复杂度问题，但随着序列长度增加，激活值带来的显存压力仍急剧上升；当前外部 Mamba 开源框架在 CP 支持上仍属空白。
2. **传统 CP 的瓶颈**：Mamba 的 SSM 递归步骤天然存在时间依赖——上一 CP rank 运算结束后才能把结果传到下一 rank 才能继续，导致空闲等待。
3. **核心优化机制**：对各 CP rank 上的 `local_decay` 与 `local_state` 做 **AllGather**，使所有 rank 拿到全局信息后 **并发** 执行状态传递计算；同时对 **前向 AllGather** 与 **反向 ReduceScatter** 做 **计算-通信掩盖（overlap）**。
4. **与传统 CP 的关系**：相对传统串行 CP（可参考 Mamba-2 paper Figure 5），性能大幅提升。
5. **与 TP/SP 的关系**：与 TP、SP 完全正交，可在已开启 TP 的基础上继续叠加 CP；CP 相比 TP 没有 `n_groups` 整除性限制。
6. **省显存优先级**：在显存吃紧场景，应优先开启 CP，再叠加重计算（recomputation），因为重计算会引入额外约 **30%** 的耗时。

---

## 【关键机制与数据】

### 工作原理

- **问题根源**：SSM 递归运算步骤之间存在严格的时间依赖（temporal dependency），传统 CP 实现必须在 rank 间串行接力（rank N+1 等待 rank N 的中间状态），引入了空闲等待气泡。
- **核心思路**：将"具有时间依赖的状态传递"部分解耦——通过 **AllGather（`local_decay`, `local_state`）** 让每个 CP rank 都拥有完整的状态信息，从而消除 rank 间串行依赖，使所有 rank 可以 **并发** 执行状态传递。
- **通信掩盖**：在前向传播中用 AllGather 与计算 overlap，在反向传播中用 ReduceScatter 与计算 overlap，进一步隐藏通信开销。
- **参考依据**：原文标注"传统 CP 可参考 [Mamba-2 paper](https://arxiv.org/abs/2405.21060) Figure 5"。

### 性能数据（原文标注 "原文:"）

- 原文（重计算开销）：重计算是常见省显存手段，但会引入 **额外 30% 耗时**。
- 原文（CP 开启前后对比，32K 序列）：
  - TP4CP1 → 56129MB / 3761.1ms
  - TP4CP2 → 32613MB / 3862.3ms（**显存优化 42%**，性能仅 -2.69%）
- 原文（同等显存下 CP vs 重计算，32K 序列、目标显存约 30GB）：
  - TP4CP1 + 全重计算 → 4728.8ms
  - TP4CP2 → 3862.3ms，**加速比例 +22.43%**

---

## 【表格解读】

### 表 1：重要参数表（原文逐字还原）

| 重要参数 | 参数说明 |
|---|---|
| `--context-parallel-algo mamba_cp_algo` | 长序列并行算法选项，默认项为 `ulysses_cp_algo`，当设置为 `mamba_cp_algo` 时开启 Mamba-CP。 |
| `--context-parallel-size [int]` | 开启 CP 对应的数量，默认为 1，根据用户需求配置。 |

**逐行解读：**
- **第一行**：算法选择开关。`ulysses_cp_algo` 是默认的 Ulysses 风格 CP 算法；切换为 `mamba_cp_algo` 即激活本文所述的 Mamba 专用 CP 实现。
- **第二行**：CP 并行度（rank 数），默认为 1（即关闭），用户按需配置；表中 32K 序列下开启 CP2 的实验即对应将该值设为 2。

### 表 2：CP 开启前后显存优化及性能变化（原文逐字还原）

| 序列长度 | 并行配置 | 显存占用 | 显存优化 | 性能 | 性能变化 |
|---|---|---|---|---|---|
| 32K | TP4CP1 | 56129MB | - | 3761.1ms | - |
| 32K | TP4CP2 | 32613MB | 42% | 3862.3ms | -2.69% |

**逐行解读：**
- **第 1 行（TP4CP1 基线）**：32K 序列下，TP=4、CP=1 作为参照，显存占用 56129MB，单步耗时 3761.1ms。
- **第 2 行（TP4CP2）**：在 TP=4 基础上将 CP 切到 2，显存降至 32613MB，**显存优化 42%**；性能开销仅 **2.69%**，几乎可忽略。说明 Mamba-CP 在 32K 序列上以极小性能代价换得近一半显存节省。

### 表 3：CP 与重计算缩减显存和性能对比（原文逐字还原）

| 序列长度 | 并行配置 | 显存占用 | 性能 | 加速比例 |
|---|---|---|---|---|
| 32K | TP4CP1 + 全重计算 | 同等显存 30GB | 4728.8ms | - |
| 32K | TP4CP2 | 同等显存 30GB | 3862.3ms | +22.43% |

**逐行解读：**
- **第 1 行（重计算基线）**：在 TP4CP1 基础上叠加全重计算，将显存压到约 30GB，但耗时上升到 4728.8ms。
- **第 2 行（Mamba-CP）**：在 TP4CP2 配置下达到同等 ~30GB 显存，耗时 3862.3ms，相对重计算基线取得 **+22.43%** 的加速。说明在"显存相同"的约束下，CP 是比全重计算更优的性能选择。

---

## 【公式解读】

**原文无公式。** 文档未给出任何数学公式或伪代码公式，仅描述了机制层面的 AllGather / ReduceScatter 与计算掩盖策略。

---

## 【关联】

原文提供的内部链接标注为 **(无)**，因此本节仅基于文档自身交叉引用做梳理：

- **算法选项并列**：与默认 CP 算法 `ulysses_cp_algo` 同属 `--context-parallel-algo` 的可选值，二者通过该参数互斥切换；Mamba-CP 是专为 Mamba SSM 递归特性定制的变体。
- **并行维度叠加关系**：与 **TP（Tensor Parallel）**、**SP（Sequence Parallel）** 维度正交，可在 TP 之上继续叠加 CP 以进一步降显存；CP 相比 TP 额外解除了 `n_groups` 整除性约束。
- **显存优化手段**：与 **重计算（Recomputation / activation checkpointing）** 属于同一问题域的替代/补充方案；文档明确给出"在同显存条件下 CP 优于全重计算（+22.43%）"，并给出"优先 CP，再加重计算"的组合策略。
- **外部参考**：传统 CP 实现可参照 [Mamba-2 paper](https://arxiv.org/abs/2405.21060) Figure 5，文档将其作为对比基线引用。

---

## 【使用方法】

- **启用算法**：`--context-parallel-algo mamba_cp_algo`（默认 `ulysses_cp_algo`，切换为该值即开启 Mamba-CP）。
- **设置 CP 数量**：`--context-parallel-size [int]`（默认 1，按需配置；表中 32K 实验取值为 2）。
- **组合配置示例**（来自原文性能数据）：TP=4、CP=2（`TP4CP2`），适用于 32K 长序列显存吃紧场景。
- **建议顺序**（原文注意事项）：省显存场景下，**优先开启 CP，再叠加重计算**。

> 注：原文未涉及其他启用前置条件、依赖安装步骤或与其他并行开关的组合命令行示例。
