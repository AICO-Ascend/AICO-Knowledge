# Norm重计算

> 仓 `mindspeed-rl` · 路径 `docs/zh/features/norm_recompute.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-rl/docs/zh/features/norm_recompute.md

# mindspeed-rl · Norm重计算 深度解读

---

## 【定位】

本文档描述了 mindspeed-rl（昇腾强化学习加速库）中 **Norm 层重计算（Norm Recomputation）特性**——一种通过重计算 Norm（RMSNorm/LayerNorm）层的输出来节省激活显存的技术手段,用于缓解大模型训练中的显存瓶颈,属于激活重计算家族的细粒度扩展。

---

## 【技术要点】

1. **机制来源**:Norm 重计算复用激活函数重计算中的 **checkpoint 机制**对 Norm 层进行处理,本质是在反向传播时重新前向计算 Norm 层,以换取不保存其输出激活。
2. **两条启动参数**:
   - `--recompute-norm` —— 开关参数,开启 Norm 重计算
   - `--recompute-norm-num-layers ${num}` —— 指定 Norm 重计算的层数 `num`
3. **分支限制**:仅支持 **mcore 分支**,即必须配合 `--use-mcore-models` 使用,**不支持 legacy 分支**。
4. **与其他重计算组合约束**:可与"激活函数重计算"和"全重计算"同时开启,但必须将 `--recompute-method` 设为 **`block`**。
5. **互斥分摊规则**:同时开启时,按照各自指定的层数做对应类型的重计算,**同一层不会被既做全重计算又做 Norm 重计算**(即层集合互斥切分)。
6. **执行优先级**:**先计算全重计算层,后计算 Norm 重计算层**(优先级明确)。

---

## 【关键机制与数据】

| 数据点 | 原文表述 |
|---|---|
| 节省对象 | RMSNorm/LayerNorm 层的**输出激活**内存 |
| 性能影响 | Norm 计算速度较快,重计算后**对整体性能影响较小**(原文定性描述,未给出具体百分比) |
| 效果边界 | 开启 TP 及 SP 的场景下,该激活内存在 TP 域内已切分,开启后**效果不明显** |
| 推荐场景 | **未使用 TP 及 SP 的模型**可考虑使用(原文) |
| 学术依据 | 引用 ATC24 论文 *Accelerating the Training of Large Language Models using Efficient Activation Rematerialization and Optimal Hybrid Parallelism*(原文参考文献链接) |

**工作原理(数据流层面)**:Norm 重计算沿用激活重计算的 checkpoint 思路——前向时不持久化 Norm 层输出,在反向传播需要该输出时,触发一次局部的 Norm 前向重算。Norm 本身计算量小,因此以重算换显存的收益比较合算。

---

## 【表格解读】

**原文无表格。** 文档为说明性文字,未提供参数表、性能对比表或配置项表格;仅有的两条命令以行内代码块形式给出。

---

## 【公式解读】

**原文无公式。** 文档不涉及任何数学公式或伪代码;机制描述完全通过自然语言加命令行参数表达。

---

## 【关联】

文档内部未提供交叉链接,但通过内容可梳理出以下与其他特性的上下游关系:

| 关联特性 / 模块 | 关系 |
|---|---|
| **激活函数重计算(Activation Recomputation)** | 机制上游——Norm 重计算**复用其 checkpoint 机制**;两者可同时开启 |
| **全重计算(Full Recomputation)** | 可与 Norm 重计算**同时开启**,组合时 `--recompute-method` 必须为 `block`,且层集合互斥 |
| **`--use-mcore-models`(mcore 模型分支)** | **前置依赖**——不开启则 Norm 重计算不可用 |
| **TP(Tensor Parallel)/SP(Sequence Parallel)** | **效果边界**——开启 TP/SP 后 Norm 输出激活已被切分,Norm 重计算的显存收益下降 |
| **参考文献 ATC24 / Yuan et al.** | 学术背景——本文实现思路对应于该工作提出的 *Hybrid Parallelism + Activation Rematerialization* 框架 |

---

## 【使用方法】

**启用方式(原文):** 在训练脚本中加入以下两条参数:

```bash
--recompute-norm                            # 开启Norm重计算
--recompute-norm-num-layers ${num}          # num表示Norm重计算的层数
```

**附加约束(原文):**

- 必须同时开启 `--use-mcore-models`,否则该特性不可用;
- 若同时启用激活函数重计算或全重计算,需设置 `--recompute-method block`;
- 全重计算层与 Norm 重计算层的执行顺序为:**先全重计算,后 Norm 重计算**,且同一层不会被重复重计算;
- 建议在**未开启 TP / SP 的模型**上使用以获得较明显的显存收益。
