# Mamba-CP

> 仓 `mindspeed-llm` · 路径 `docs/en/pytorch/features/mcore/mamba_context_parallel.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-llm/docs/en/pytorch/features/mcore/mamba_context_parallel.md

# Mamba-CP 文档深度解读

---

## 【定位】

这篇文档描述 Mamba 架构在昇腾 LLM 分布式训练框架 mindspeed-llm 中新增的 **Mamba-CP（Mamba + Context Parallelism，上下文并行）**能力，解决"外部开源 Mamba 框架不支持 CP、传统 CP 在 Mamba 递归 SSM 计算上因时序依赖产生 rank 间空等"这两个问题，从而在超长序列训练场景下降低 activation 显存压力并提升吞吐。

---

## 【技术要点】

1. **目标对象**：Mamba（SSM 类）模型，而非 Transformer。Mamba 的 SSM 递推步在时间维度上存在数据依赖，与 Transformer 的 attention 计算模式不同。
2. **传统 CP 的瓶颈**：传统 CP 必须等待上一个 CP rank 完成计算并将 state 结果传给下一个 CP rank 才能执行下一步，造成"流水线气泡"式的空等；Mamba-2 论文 Figure 5 即展示了这种传统 CP 设计。
3. **本文核心解法**：对**具有时序依赖的 state transfer 部分**，在各 CP rank 之间对 `local_decay` 与 `local_state` 做 **AllGather**，使**所有 CP rank 可以并发地执行 state transfer 计算**。
4. **通信-计算重叠**：在 forward 的 AllGather 阶段、backward 的 ReduceScatter 阶段，将集合通信与计算做 overlap，进一步隐藏通信开销。
5. **与 TP/SP 的关系**：CP 与 TP、SP **正交（orthogonal）**，可以在 TP 之上叠加 CP；TP 存在 `n_groups` 整除性约束，但 CP 没有。
6. **与重计算的取舍**：重计算（recomputation）通常带来约 **30% 的运行时增加**；在长序列显存受限场景下，CP 比重计算节省更多显存（原文注：先启用 CP，再叠加 recomputation）。

---

## 【关键机制与数据】

**工作原理（原文整合描述）**：

Mamba 的 SSM 递推在数学上是沿序列方向对隐藏 state 的迭代更新，因此天然存在时间依赖。传统 CP 会把序列切分到不同 rank 上串行推进（rank k 必须等 rank k-1 算完并把局部 state 传过来），从而在 rank 间形成串行依赖链。

本文方案的核心动作有两步：
1. **AllGather(`local_decay`, `local_state`)**：把所有 CP rank 上的 `local_decay` 和 `local_state` 收集到每个 rank 上，使每个 rank 都拥有"全局可见"的状态转移所需输入。
2. **并发 state transfer + 通信计算 overlap**：拿到全局 `decay`/`state` 后，每个 rank 独立完成本 rank 对应序列段的 state transfer 计算，因此**所有 rank 是并发的**，不再形成流水线气泡；同时 forward AllGather、backward ReduceScatter 与计算流水重叠。

**性能数据（原文）**：
- 32K 序列长度下，TP4CP1 → TP4CP2：显存由 **56129 MB 降至 32613 MB**，显存优化 **42%**；性能由 **3761.1 ms 变为 3862.3 ms**，变化 **-2.69%**。
- 在"同等 30 GB 显存"目标下：TP4CP1 + full recomputation 用时 **4728.8 ms**；TP4CP2 用时 **3862.3 ms**，对应 **+22.43%** 的 speedup。
- 原文定性结论：相比传统 CP，Mamba-CP 带来"substantial performance gains"；CP 在显存节省上优于单纯 recomputation。

---

## 【表格解读】

### 表 1：Memory optimization and performance before and after enabling CP

> 原文逐字还原：

| Sequence Length | Parallel Configuration | Memory Usage | Memory Optimization | Performance | Performance Change |
| --------------- | ---------------------- | ------------ | ------------------- | ----------- | ------------------ |
| 32K             | TP4CP1                 | 56129 MB     | N/A                 | 3761.1 ms   | N/A                |
| 32K             | TP4CP2                 | 32613 MB     | 42%                 | 3862.3 ms   | -2.69%             |

**逐行解读**：
- **行 1（基线 TP4CP1）**：32K 序列 + Tensor Parallelism=4 + Context Parallelism=1（即关闭 CP）的 baseline，显存 56129 MB，单步性能 3761.1 ms，作为参考点。
- **行 2（TP4CP2）**：在 TP4 基础上叠加 CP=2，显存降至 32613 MB，相对 TP4CP1 **节省 42%**；单步时间 3862.3 ms，性能变化 **-2.69%**（即耗时略微增加约 2.69%）。这条对比说明：开启 CP2 换来了近一半的显存下降，代价是极小的性能回退（约 2.69%）。

### 表 2：Comparison of memory reduction and performance between CP and recomputation

> 原文逐字还原：

| Sequence Length | Parallel Configuration      | Memory Usage         | Performance | Speedup |
| --------------- | --------------------------- | -------------------- | ----------- | ------- |
| 32K             | TP4CP1 + full recomputation | Same memory as 30 GB | 4728.8 ms   | N/A     |
| 32K             | TP4CP2                      | Same memory as 30 GB | 3862.3 ms   | +22.43% |

**逐行解读**：
- **行 1（TP4CP1 + full recomputation）**：通过 full recomputation 把显存压到与 30 GB 同档，单步耗时 4728.8 ms，作为"同显存约束下的重计算方案"基线。
- **行 2（TP4CP2）**：在相同 30 GB 显存预算下，用 TP4CP2 替代重计算，单步耗时 3862.3 ms，相对上一行获得 **+22.43%** 的 speedup。这条对比是文档的核心论据：**在同显存预算下，CP 方案比 full recomputation 快约 22.43%**，而原文又提到 recomputation 通常带来约 30% 的额外运行时开销，二者互相印证。

---

## 【公式解读】

原文无公式（无 LaTeX 或伪代码形式的数学表达式）。文档仅以文字 + 集合通信原语（AllGather / ReduceScatter）描述方案，未给出 SSM 递推、显存估算或加速比的显式数学形式。

---

## 【关联】

文档中明确点名了以下与之相关的特性/模块/上下文（依据文末"无内部链接"说明，下面均为正文文本中直接提及的关联项）：

1. **TP（Tensor Parallelism，张量并行）**：Mamba-CP 与 TP 正交，可叠加；TP 受 `n_groups` 整除性约束，而 CP 不受该约束，因此当序列长度让 TP 维度切分受限时，CP 可作为额外切分轴。
2. **SP（Sequence Parallelism，序列并行）**：文档将 CP 与 SP 并列为可与 TP 共存的并行维度，强调 CP 是在它们之上的进一步切分。
3. **Recomputation（重计算）**：与 CP 并列的显存节省手段。文档给出量化关系：recomputation 通常带来约 30% 额外 runtime；同显存预算下 TP4CP2 比 TP4CP1 + full recomputation 快 +22.43%。Notes 中给出叠加顺序建议："先 CP，后 recomputation"。
4. **传统 CP / Ulysses CP**：原文将 `--context-parallel-algo` 的默认值设为 `ulysses_cp_algo`，新算法 `mamba_cp_algo` 是在该参数框架下的一个选项实现，说明 Mamba-CP 是 CP 算法族中的一个分支，与既有 Ulysses CP 共享同一参数入口。
5. **外部参考文献：Mamba-2 论文 Figure 5**：被引用作为传统 CP 在 SSM 上的设计示意，是本文 Mamba-CP 设计的对比对象（外部链接，非仓内链接）。

---

## 【使用方法】

**启用命令（原文 How to Use 表格）**：

| 关键参数 | 描述 |
| --- | --- |
| `--context-parallel-algo mamba_cp_algo` | 长序列并行算法选项；默认值为 `ulysses_cp_algo`，设置为 `mamba_cp_algo` 即启用 Mamba-CP。 |
| `--context-parallel-size [int]` | 启用 CP 时使用的 rank 数量；默认值为 `1`，按需配置。 |

**叠加建议（原文 Notes）**：
- 在 Mamba-CP 场景下需要进一步节省显存时，**先启用 CP，再启用 recomputation**。

原文未涉及具体的 Python API 调用方式、YAML 配置文件示例或环境变量名称；以上即为原文中给出的全部启用/配置手段。
