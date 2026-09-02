# CCLoRA

> 仓 `mindspeed-llm` · 路径 `docs/en/pytorch/features/mcore/cc_lora.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-llm/docs/en/pytorch/features/mcore/cc_lora.md

# CCLoRA 深度解读

## 【定位】
本文档描述 mindspeed-llm 在 LoRA 微调场景下的一种通信–计算融合加速能力 (CCLoRA)，通过把"冻结预训练权重"与"低秩增量更新"两条分支解耦为双流水线、并基于数学等价变换合并/省略冗余通信，从而降低分布式训练中的通信开销并提升吞吐。

---

## 【技术要点】

1. **双流水线 (Dual Pipeline) 替代单流水线**：将原本串行的「冻结预训练分支 (前向+反向)」与「低秩更新分支 (前向+反向)」解耦成两条独立的流水线，使预训练分支和更新分支可异步执行，重叠通信与计算。
2. **基于数学等价合并通信 (SP + Row 场景)**：当 $B$ 是标准线性层且各设备上参数一致时，把 `all_gather(grad_y * B)` 等价改写为 `all_gather(grad_y) * B`，并复用 MC2 计算中已产生的 `all_gather(grad_y)` 来同时计算 `grad_x`，从而省略一次 `all_gather` 通信。
3. **基于输入维度大小的等价缩放 (Scaling) 优化**：LoRA 增量项 $\lambda BAx$ 视 $BS$ 与 $H$ 的相对大小，与主项 $Wx$ 选择不同的融合形式，以降低中间张量内存与计算量。
4. **入口开关 `--lora-fusion`**：启用 CCLoRA 加速（对应 RC2 及之后版本）。
5. **兼容性范围**：与 PP、VPP、分布式优化器 (distributed optimizers) 等场景兼容。
6. **互斥约束**：与 `--overlap-param-gather` 特性冲突，禁止同时开启。

---

## 【关键机制与数据】

**工作原理（原文）：**
- LoRA 微调中，预训练权重冻结，仅训练低秩矩阵 $A$、$B$；冻结分支与低秩分支独立，但默认串行执行前向/反向，在分布式场景下产生冗余通信。
- 解决方案是把单流水线改成"通信 + 计算"双流水线，使两条分支异步推进；并利用数学等价变换，在 SP (Sequence Parallel) + Row 切分场景下合并掉一次 `all_gather(grad_y * B)`，同时让 `grad_x` 复用 `all_gather(grad_y)`。
- 缩放逻辑等价变换的判定条件由 batch×seq ($BS$) 与隐层维度 $H$ 的大小关系决定，从而在两条分支之间选择更优的算子融合顺序。

**性能数据（原文：Atlas 900 A2 PODc 集群，1×8 规模）：**
- Llama-2-7B (dynamic, TP=8, PP=1, SP=√)：基线 9.72 → CCLoRA+ 13.64，提升 40.3%。
- Llama-2-7B (pack, TP=8, PP=1, SP=√)：基线 5.97 → CCLoRA+ 6.65，提升 11.5%。
- Mixtral-7*8B (dynamic, TP=1, PP=4, SP=×)：基线 13.97 → CCLoRA+ 20.55，提升 47.1%。
- Llama-2-70B (dynamic, TP=1, PP=4, SP=×)：基线 13.50 → CCLoRA+ 14.75，提升 9.3%。

---

## 【表格解读】

**原文表格逐字还原：**

| Model | NPU | TP | PP | SP | Baseline Throughput | CCLoRA+ Throughput | Performance Gain |
| :---: | :--: | :--: | :--: | :--: | :------: | :---------: | :------: |
| Llama-2-7B dynamic | 8 | 8 | 1 | √ | 9.72 | 13.64 | 40.3% |
| Llama-2-7B pack | 8 | 8 | 1 | √ | 5.97 | 6.65 | 11.5% |
| Mixtral-7*8B dynamic | 8 | 1 | 4 | × | 13.97 | 20.55 | 47.1% |
| Llama-2-70B dynamic | 8 | 1 | 4 | × | 13.50 | 14.75 | 9.3% |

**逐行解读：**

- **硬件/规模**：所有 4 组实验均在 Atlas 900 A2 PODc 集群的 1×8 (8 卡) 配置下测得。
- **第 1 行 Llama-2-7B dynamic**：TP=8、PP=1、开启 SP。CCLoRA+ 吞吐由 9.72 提升到 13.64，相对增益 **40.3%**——这是 SP 场景下"双流水线 + `all_gather` 合并"双重优化的叠加效果，因此收益最大。
- **第 2 行 Llama-2-7B pack**：与第 1 行同配置，但采用 pack (样本打包) 序列组织。吞吐从 5.97 → 6.65，增益 **11.5%**。同模型下增益明显低于 dynamic 组，说明 packing 改变了样本时间结构，原本可被双流水线掩盖的通信暴露比例变小。
- **第 3 行 Mixtral-7*8B dynamic**：TP=1、PP=4、关闭 SP。吞吐 13.97 → 20.55，增益 **47.1%**——为表中最高绝对提升。在无 SP、仅 PP 的场景下，仍能通过"双流水线异步 + 缩放等价融合"取得最大收益，说明异步双流水线本身是 CCLoRA 的核心收益来源。
- **第 4 行 Llama-2-70B dynamic**：TP=1、PP=4、关闭 SP，模型更大。吞吐 13.50 → 14.75，增益 **9.3%**——为表中最低。可能因为 70B 模型本身通信/计算比发生变化，PP 阶段内流水线气泡成为主导瓶颈，CCLoRA 的优化空间相对被压缩。

**总结观察（原文：）**：Mixtral-7*8B 在 PP-only 配置下取得最高增益 (47.1%)；Llama-2-7B 在 SP 场景 (TP=8) 下也获得显著增益 (40.3%)；而 70B 大模型在同 PP-only 配置下增益最低 (9.3%)。

---

## 【公式解读】

**公式 1（A 矩阵梯度等价变换，原文）：**

$$
\mathrm{grad}_a = all\_gather(\mathrm{grad}_y * B) = all\_gather(\mathrm{grad}_y) * B
$$

- $\mathrm{grad}_y$：上游传回的输出侧梯度张量。
- $B$：LoRA 的下行低秩矩阵，在 SP+Row 场景下各设备参数相同 (identical on each device)。
- `*`：逐元素乘法。
- `all_gather`：跨设备集合通信，将各分片汇聚成完整张量。
- **作用**：利用 $B$ 在各设备一致的特性，把 `all_gather` 从"乘之后"挪到"乘之前"，等价但通信量与中间张量更可控，为下一步合并奠定基础。

**公式 2（X 梯度复用，原文）：**

$$
\mathrm{grad}_x = all\_gather(\mathrm{grad}_y) * X
$$

- $X$：对应算子输入张量。
- **作用**：MC2 (Matmul + Communication 融合算子) 计算中已经产生过 `all_gather(grad_y)`，这里直接复用该结果计算输入梯度，避免重复通信。

**公式 3（被省略的通信，原文）：**

$$
all\_gather(\mathrm{grad}_y * B)
$$

- **作用**：经公式 1、2 等价变换后，该次集合通信可被完全省略 (omit)。

**公式 4（缩放逻辑等价变换，原文）：**

$$
\text{Input: } x\in\mathbb{R}^{B\times S\times H},\quad \text{Output: } Y = Wx + \lambda BAx = \begin{cases}
Y=Wx+B(\lambda A)x, & \text{if } BS < H \\
Y=(W+B\lambda A)x, & \text{if } BS\geq H
\end{cases}
$$

- $x$：输入张量，维度为 (Batch, Sequence, Hidden)。
- $W$：预训练主权重 (frozen)。
- $A$、$B$：LoRA 低秩矩阵；输出增量项为 $\lambda BAx$，其中 $\lambda$ 为 LoRA 缩放系数。
- 符号含义：
  - **当 $BS < H$**：先在 token 维 ($BS$) 上做小矩阵乘 $\lambda A x$ (降维到秩 $r$)，再做 $B(\cdot)$ 还原到 $H$ 维，与 $Wx$ 相加——等价于把低秩乘放在 token 侧，减少沿 $H$ 维的中间张量。
  - **当 $BS \geq H$**：先把 $B\lambda A$ 与 $W$ 合并为单矩阵 $(W+B\lambda A)$，再做一次大矩阵乘——等价于把低秩乘"吸收进主权重"，避免沿 token 维展开低秩中间张量。
- **作用**：根据 $BS$ 与 $H$ 的相对大小动态选择更省内存/算力的算子融合顺序，属于 LoRA 缩放层面的数学等价优化。

---

## 【关联】

- **LoRA 微调（上游）**：CCLoRA 是 LoRA 微调在分布式 (昇腾 + MC2) 场景下的通信–计算融合加速，依赖 LoRA 的"低秩增量 + 主权重冻结"结构。
- **MC2 (Matmul + Communication 融合) 算子**：公式 2 中复用的 `all_gather(grad_y)` 来自 MC2 计算过程；CCLoRA 把 MC2 已经做过的集合通信结果二次用于梯度计算。
- **SP (Sequence Parallel) 与 Row 切分**：公式 1、2 的等价变换以"SP 场景下 $B$ 矩阵在每卡参数一致"为前提，因此 CCLoRA 的通信合并收益与 SP 配置强相关。
- **PP / VPP / 分布式优化器**：文档明确指出 CCLoRA 与 PP、VPP、分布式优化器兼容，意味着双流水线异步可以叠加在已有流水线并行之上。
- **冲突特性 `--overlap-param-gather`**：与 CCLoRA 不兼容，禁止同时开启——提示二者都对"参数聚合通信"做了重排，存在资源/时序竞争。
- **架构示意**：原文引用 `figures/cc_lora.png`（双流水线架构图），用于直观展示"通信 + 计算"双流水线相对于单流水线的结构差异。

---

## 【使用方法】

**启用方式（原文）：**
```bash
--lora-fusion
```

**版本要求（原文）：** RC2 及以后版本。

**兼容场景（原文）：** PP、VPP、分布式优化器 (distributed optimizers) 等。

**互斥约束（原文）：** 与 `--overlap-param-gather` 冲突，禁止同时使用。

**验证环境（原文）：** Atlas 900 A2 PODc 集群，1×8 规模。

## 图文联合解读

- `cc_lora.png`: **图文联合解读：**

图示对比两种LoRA前向执行模式：上方"no pipe"为冻结预训练分支（g→Pretrained Weight→ḡ）与可训练低秩分支（W_A→f→W_B）**串行**执行，时间线呈Compute–Communication交替结构；下方"2 pipes"将两分支**并行**，通信与计算时间块错位重叠（出现空闲槽位被对方通信/计算填充）。底部虚线框标注SP&Column用allgather、SP&Row用reduce_scatter的场景映射。

**结论**：双管道异步执行可使通信开销被计算隐藏。**呼应文档**Solution 1"单流水线→双流水线"优化论点的核心证据。
