# Norm重计算

> 仓 `mindspeed` · 路径 `docs/zh/features/norm-recompute.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed/docs/zh/features/norm-recompute.md

# Norm重计算 — 深度解读

## 【定位】

本文档描述 mindspeed 中针对 **Norm 层（RMSNorm / LayerNorm）输出激活**进行重计算（recomputation）的特性，目的是在大模型训练场景中节省显存。

## 【技术要点】

1. **核心思想**：借鉴已有「激活函数重计算」的 checkpoint 机制，对 Norm 层的前向输出不保存，而是在反向阶段按需重算。
2. **控制开关**：通过 `--recompute-norm` 开启 Norm 重计算；通过 `--recompute-norm-num-layers ${num}` 指定参与重计算的 Norm 层数。
3. **分支限制**：仅支持 mcore 分支（`--use-mcore-models`），不支持 legacy 分支。
4. **组合约束**：可与激活函数重计算、全重计算同时开启；组合时仅支持 `--recompute-method=block`。
5. **互斥策略**：同一层不会既做全重计算又做 Norm 重计算，两类重计算按各自指定的层数独立进行。
6. **执行优先级**：先计算全重计算层，后计算 Norm 重计算层。

## 【关键机制与数据】

- **机制**：Norm 重计算复用激活函数重计算的 checkpoint 机制。具体 checkpoint 实现细节引用自论文 [Accelerating the Training of Large Language Models using Efficient Activation Rematerialization and Optimal Hybrid Parallelism](https://www.usenix.org/conference/atc24/presentation/yuan)。
- **作用对象**：RMSNorm 与 LayerNorm 层的输出激活。
- **显存收益场景**：原文指出，未开启 TP（张量并行）与 SP（序列并行）时收益较明显；开启 TP/SP 时，因 Norm 输出激活在 TP 域内已被切分，节省效果不明显。
- **性能影响**：原文提到 Norm 计算速度较快，重计算带来的整体性能损耗较小（原文未给出量化百分比）。
- **组合语义**：当 Norm 重计算 + 激活重计算/全重计算同时开启时，各自分别按指定层数执行；执行顺序为先全重计算、后 Norm 重计算。

## 【表格解读】

原文无表格。

## 【公式解读】

原文无公式。

## 【关联】

- **上游/复用机制**：依赖「激活函数重计算」的 checkpoint 机制（文档明确说明「运用激活函数重计算特性中的 checkpoint 机制」）。
- **可组合特性**：可与「激活函数重计算」和「全重计算」同时开启；组合时 `--recompute-method` 需设置为 `block`。
- **分支依赖**：仅在 mcore 分支（`--use-mcore-models`）下可用。
- **并行维度关系**：与 TP（张量并行）、SP（序列并行）相关——在 TP/SP 已对 Norm 输出激活进行切分的场景下，本特性收益有限。
- **执行顺序关系**：与全重计算存在先后优先级（全重计算 → Norm 重计算）。

## 【使用方法】

原文给出的开启方式：

```bash
--recompute-norm                        # 开启Norm重计算
--recompute-norm-num-layers ${num}      # num表示Norm重计算的层数
```

前置条件与注意事项（原文 NOTE 部分）：

1. 必须开启 `--use-mcore-models`，仅支持 mcore 分支。
2. 可与激活函数重计算、全重计算同时开启；组合时 `--recompute-method` 必须设为 `block`。
3. 同时开启时，按各自指定的层数分别执行重计算，单层不会被两种重计算同时覆盖。
4. 执行顺序：先全重计算层，后 Norm 重计算层。
