# Megatron 重计算

> 仓 `mindspeed` · 路径 `docs/zh/features/recomputation.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed/docs/zh/features/recomputation.md

# 「Megatron 重计算」Feature 文档深度解读

## 【定位】

本文档系统性介绍了 Megatron（mindspeed 昇腾大模型加速库中）**重计算（Recomputation / Gradient Checkpointing）特性**——一种通过在前向传播时主动释放激活值、反向传播时按需重算来降低显存占用的训练优化手段，并给出选择性重计算与完全重计算两种启用方式及配套命令行参数。

---

## 【技术要点】

1. **核心思想：以时间换空间**——前向阶段即时释放不再需要的激活值内存，反向阶段按需重算，将激活值生命周期从"全程驻留显存"压缩到"窗口期内临时存在"，从而缓解激活值随模型深度线性增长带来的显存压力。

2. **两种重计算粒度（二选一）**：
   - **选择性重计算（推荐，`--recompute-activations`）**：仅对 Transformer 内 **`core_attention` 组件**实施重算；保留"占用小但重算贵"的激活，重算"占用大但重算便宜"的激活。
   - **完全重计算（`--recompute-granularity full`）**：除输入数据外，所有激活值在反向时全部重算，适用于显存极度受限场景。

3. **完全重计算的两种切分策略（`--recompute-method`）**：
   - **`uniform`**：将 Transformer 层均匀划分为若干组，每组大小由 `--recompute-num-layers` 指定，按组存储输入与激活值。
   - **`block`**：仅对**前 `--recompute-num-layers` 个 Transformer 层**做重计算，剩余层不进行重计算。

4. **优先级与互斥规则**：
   - 同时配置 `--recompute-activations` 与 `--recompute-granularity full` 时，**选择性重计算优先级更高**。
   - **legacy 分支**下，开启 `--use-flash-attn` 将**无法使用选择性重计算**。

5. **与流水线并行的协同配置（vpp 场景）**：当 `--recompute-method block`、`--recompute-granularity full`、`--num-layers-per-virtual-pipeline-stage N` 同时配置时，`--recompute-num-layers N` 的语义是**每个 vpp stage 做 N 层重计算**；另可通过 `--enable-recompute-layers-per-pp-rank` 修改语义为**无视 vpp，按每个 pp stage 来配置重计算层数**。

6. **使用约束**：重计算会引入**额外计算成本、降低训练吞吐**，需在显存节省与性能损失之间做权衡。

---

## 【关键机制与数据】

- **问题根源（原文）**："传统的实践要求存储前向传播阶段产生的激活值，以供后续反向传播过程中的梯度计算使用。这一需求导致了激活值保存数量随模型深度线性增长的现象，显著加剧了对硬件内存资源的压力。"
- **工作机制（原文）**："在前向传播与损失函数计算阶段，即时释放不再需要的激活值内存空间，仅在反向传播时根据需要重新计算激活值。此方法通过有效缩短激活值的生命周期……"
- **选择性重计算的设计原则（原文）**："保留了那些占用较小内存空间但重计算成本较高的激活值，同时，对占用较大内存但重计算成本相对较低的激活值执行激活重计算。"
- **完全重计算的边界条件（原文）**："除了保存输入数据外，所有激活值均在需要时重新计算。"
- **uniform 分组语义（原文）**："将 Transformer 层均匀划分组（每组大小 `--recompute-num-layers`），按组存储输入和激活值。"
- **block 切分语义（原文）**："将前 `--recompute-num-layers` 个 Transformer 层重计算，剩余层不进行重计算。"
- **使用效果（原文）**："通过避免长时间保留大量中间计算结果，大幅降低了对内存的需求。""重计算激活值会带来额外的计算成本，降低性能。"

> 原文未给出具体显存节省比例、吞吐下降百分比等量化性能数据。

---

## 【表格解读】

**原文无表格**。

（文档仅以条目形式列出使用方式与注意事项，未提供参数对照表或性能对比表。）

---

## 【公式解读】

**原文无公式**。

（文档未涉及任何数学表达式或伪代码形式的公式。）

---

## 【关联】

本文档聚焦 Megatron 重计算单一特性，**文末未提供内部链接**。但根据文档自身引用的参数与上下文，可推断以下关联关系：

- **核心注意力组件 `core_attention`**：选择性重计算的目标对象，与 Transformer 注意力实现耦合；与 **`--use-flash-attn`** 存在互斥关系（legacy 分支下开启 FlashAttention 时无法启用选择性重计算）。
- **流水线并行（PP / VPP）**：`--recompute-num-layers` 与 `--num-layers-per-virtual-pipeline-stage`、`--enable-recompute-layers-per-pp-rank` 共同作用，揭示该特性在 Megatron 流水线并行框架下的分层调度逻辑。
- **上游背景**：本文所述方案是 Megatron-LM 的经典重计算策略在 mindspeed（昇腾加速库）中的实现与说明，属于大模型训练**显存优化**范畴，与 ZeRO、Offload、混合精度等其他显存优化手段形成互补关系（但本文档未展开对比）。

---

## 【使用方法】

**选择性重计算（推荐）：**
```bash
--recompute-activations   # 开启选择性重计算
```

**完全重计算：**
```bash
--recompute-granularity full          # 开启完全重计算
--recompute-method uniform/block      # 选择重计算方式（必填，二选一）
--recompute-num-layers N              # uniform：每组层数；block：前 N 层重计算
```

**`--recompute-method` 参数二选一说明：**
- `uniform`：Transformer 层均匀分组，按组存输入与激活。
- `block`：仅对前 N 层做重计算，剩余层不重计算。

**注意事项（原文 NOTE 摘录）：**
- 同时配置 `--recompute-activations` 与 `--recompute-granularity full` 时，选择性重计算优先级更高。
- vpp 场景下（`--recompute-method block` + `--recompute-granularity full` + `--num-layers-per-virtual-pipeline-stage N`）：`--recompute-num-layers N` 默认为**每个 vpp stage 做 N 层重计算**；加 `--enable-recompute-layers-per-pp-rank` 后语义变为**按每个 pp stage 配置重计算层数（无视 vpp）**。
- legacy 分支下，开启 `--use-flash-attn` 将无法使用选择性重计算。
