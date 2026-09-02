# FSDP2 Muon优化器

> 仓 `mindspeed-mm` · 路径 `docs/zh/features/fsdp2_muon_optimizer.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-mm/docs/zh/features/fsdp2_muon_optimizer.md

# FSDP2 Muon 优化器 — 一体化深度解读

## 【定位】
本文档描述 mindspeed-mm 在 FSDP2 后端下对 Muon（Momentum Orthogonalized by Newton-Schulz）优化器的适配能力：面向二维矩阵参数做 Newton-Schulz 正交化更新的替代优化器，同时处理 DTensor 分片在正交化前后的聚合与重新分片问题，并与 AdamW 形成参数级自动回退。

---

## 【技术要点】

1. **优化器定位**：Muon 是一类面向**矩阵参数**的优化器，对二维权重矩阵的更新方向做正交化处理；文档明确将之定位为 AdamW 之外的替代选择，而非通用优化器。
2. **参数分流规则**：满足"二维矩阵"且参数名不以 `.bias` 结尾、不含 `embedding`、不含 `output_layer` 的参数走 Muon；其余参数自动回退 AdamW；原有的 lr / weight_decay / no-decay 分组配置保留。
3. **Muon 三步更新流程**：(a) 对 Muon 参数用 SGD momentum 累积梯度方向；(b) 将更新方向转 bfloat16 后用 Newton-Schulz 迭代做近似正交化；(c) 对权重执行 weight decay 并应用正交化更新。
4. **FSDP2 DTensor 适配**：计算正交化前将分片参数的更新方向聚合为 replicate 形态；计算完成后按原始 DTensor placements 重新分片，保证优化器状态与 FSDP2 参数布局一致。
5. **关键超参默认值**：`matched_adamw_rms=0.2`、`muon_momentum=0.95`、`ns_steps=5`；启用方式为 `training.optimizer: muon`。
6. **工程参考来源**：实现参考 MoonshotAI/Moonlight 与 KellerJordan/Muon，并在其基础上新增 FSDP2 后端的 DTensor 分片聚合与重新分片适配。

---

## 【关键机制与数据】

### 工作原理（更新方向处理链路）

Muon 利用神经网络隐藏层权重的矩阵结构，对 momentum 累积得到的更新方向施加正交化约束，使二维权重矩阵的更新方向更接近良条件的谱范数更新。文档原文表述为："对 momentum 更新方向做正交化约束，使二维权重矩阵的更新方向更接近良条件的谱范数更新。"

整条链路：原始梯度 → **SGD momentum 累积** → **转 bfloat16** → **Newton-Schulz 迭代近似正交化** → **weight decay 应用** → 最终更新。

### FSDP2 DTensor 数据流

原文："在 FSDP2 场景下，参数可能是 DTensor 分片。Muon 在计算正交化更新前，会将分片参数的更新方向聚合为 replicate 形态；计算完成后，再按原始 DTensor placements 重新分片，保证优化器更新和 FSDP2 参数布局保持一致。"

即在正交化计算这个**必须看到完整矩阵**的环节临时 replicate，出计算后还原为分片布局，因此带来额外通信开销（原文注意事项第 2 点确认："会带来额外通信和计算开销"）。

### 经验性收益与不确定性的原文声明

原文："在部分公开实验中，Muon 表现出更好的样本效率和计算效率，即用更少训练时间或 FLOPs 达到相近 loss；但实际收益仍依赖模型结构、batch size、学习率和训练阶段，需要结合业务任务验证。"

文档没有给出具体 loss 数字或加速比，凡收益均限定为"部分公开实验"+"需要结合业务任务验证"。

### 公开使用案例（原文）

- **Kimi K2**：原文："在 1T MoE 规模上使用 Muon/MuonClip 训练"。
- **HunyuanVideo-1.5**：原文："使用 Muon 优化器训练，并建议继续训练或 LoRA 微调时使用 Muon"。
- **NVIDIA NeMo-RL**：原文："给出了在 Qwen3-235B-A22B SFT 和 Qwen2.5-7B DAPO 场景中使用 Muon 的示例"。

---

## 【表格解读】

原文在「参数详解」一节以条目列表给出 6 个配置项。下面**逐字还原**为 markdown 表格，再逐行解读。

| 参数名 | 描述 | 取值/默认值 | 说明 |
|---|---|---|---|
| `optimizer` | 选择优化器类型 | 取值：`adamw` 或 `muon` | — |
| `matched_adamw_rms` | 控制 Muon 更新量级与 AdamW 更新 RMS 的匹配程度 | 默认值：`0.2` | — |
| `muon_momentum` | Muon 内部 SGD momentum 的动量系数 | 默认值：`0.95` | — |
| `ns_steps` | Newton-Schulz 正交化迭代步数 | 默认值：`5` | 步数越大，正交化计算越充分，但开销也会增加 |
| `lr` | 基础学习率 | — | Muon 参数会在基础学习率上结合 `matched_adamw_rms` 和矩阵形状做更新幅度调整 |
| `weight_decay` | 权重衰减系数 | — | — |

### 逐行解读

- **`optimizer`**：唯一的"开关"型参数；只有取 `muon` 时才进入本文档描述的 Muon 流程，取 `adamw` 即回到常规 AdamW 路径。
- **`matched_adamw_rms=0.2`**：桥接 Muon 与 AdamW 更新量纲的关键缩放因子；将 Muon 正交化后更新的 RMS 校准到与 AdamW 同量级，从而保证与 `lr` 组合后的步长语义可迁移；注意事项原文明确："修改学习率时建议同步观察该参数对收敛的影响"。
- **`muon_momentum=0.95`**：momentum 系数偏高，符合文献中"长记忆 SGD momentum"的常见取值（仅文献常识，原文未给对比）。
- **`ns_steps=5`**：Newton-Schulz 迭代步数，控制正交化的近似精度；文档给出明确的工程建议（见使用方法注意事项）："短跑通可使用较小值，正式训练建议结合 loss 曲线和吞吐表现验证"。
- **`lr`**：与 AdamW 不同，Muon 的最终更新幅度还会受 `matched_adamw_rms` 与矩阵形状（典型为 √(fan_out) 类缩放，原文未展开公式，仅文字描述"结合 matched_adamw_rms 和矩阵形状做更新幅度调整"）的联合调制，因此 `lr` 不直接等于 AdamW 的学习率。
- **`weight_decay`**：在 Muon 路径中作为第 3 步（正交化后）施加到权重上，作用时机晚于正交化。

> **注**：原文"注意事项"第 1 点隐含了一个表格未单列的事实——Muon 与 AdamW 在**参数级别共存**（按名称/形状自动分流），因此无需手动为不同参数组分别配置优化器。

---

## 【公式解读】

原文**未给出显式数学公式**（无 LaTeX、无伪代码表达式）。原文中唯一与"公式/数学过程"相关的表述是文字描述的 Newton-Schulz 迭代与 SGD momentum 累积步骤，属于流程描述而非公式定义。

**原文无公式。**

为便于理解，将原文中"被公式化"的核心过程以伪代码形式重写如下（非原文，仅作辅助理解）：

```
# 对每个 Muon 参数 W（二维矩阵）
g          ← 当前 batch 梯度                          # 原始梯度
m          ← muon_momentum * m + g                    # SGD momentum 累积（muon_momentum=0.95）
u_bf16     ← to_bfloat16(m)                           # 转 bfloat16
u_orth     ← Newton_Schulz_5(u_bf16)                  # ns_steps=5 步近似正交化
W          ← (1 - lr*weight_decay) * W
            - lr * scale(u_orth, matched_adamw_rms, shape(W))   # 应用正交化更新
```

其中 `Newton_Schulz_5(·)` 表示 5 步 Newton-Schulz 迭代；`scale(·)` 的具体形式原文未展开，仅以"结合 matched_adamw_rms 和矩阵形状做更新幅度调整"概括。

---

## 【关联】

文档主要建立以下关联（均基于原文显式表述）：

- **vs. AdamW**：作为"之外的优化选择"；同一模型中按参数名/形状**自动共存**——Muon 管二维矩阵，AdamW 管其余参数（bias、embedding、output_layer 等）。
- **FSDP2 后端**：本文档描述的 Muon 是 **FSDP2 专属实现**，与仓库中通用 Muon 的差异在于 DTensor 分片聚合与重新分片；启用入口在 FSDP2 YAML 配置中。
- **DTensor 分片机制**：正交化计算需要完整矩阵视图，因此与 FSDP2 的 DTensor placements 形成"聚合-计算-重新分片"的耦合。
- **Newton-Schulz 迭代**：作为 Muon 的数学内核，原文以"近似正交化"指代，由 `ns_steps` 控制精度。
- **上游实现参考**：MoonshotAI/Moonlight 示例版 Muon、KellerJordan/Muon，本文在其实现思路上**新增** DTensor 分片适配。
- **外部公开案例**：Kimi K2（1T MoE，Muon/MuonClip）、HunyuanVideo-1.5、NVIDIA NeMo-RL（Qwen3-235B-A22B SFT、Qwen2.5-7B DAPO）——这些是文档用来佐证 Muon 工程可用性的外部用例，但不构成 mindspeed-mm 自身的性能承诺。
- **训练阶段延续性**：HunyuanVideo-1.5 的实践被原文引用为"继续训练或 LoRA 微调时使用 Muon"的依据，提示 Muon 与持续训练流程的兼容性。

---

## 【使用方法】

### 启用方式（原文）

在 FSDP2 YAML 配置中，将 `training.optimizer` 设置为 `muon` 即可启用。

### 配置示例（原文 YAML，逐字保留）

```yaml
training:
  lr: 1.0e-5
  weight_decay: 0
  optimizer: muon
  matched_adamw_rms: 0.2
  muon_momentum: 0.95
  ns_steps: 5
```

### 调参建议（原文"注意事项"逐字摘录）

1. Muon 只会作用于满足条件的二维矩阵参数，其余参数会自动使用 AdamW 回退逻辑，不需要手动拆分参数。
2. FSDP2 分片参数会在 Muon 正交化计算前临时聚合，计算后重新分片；该过程会带来额外通信和计算开销。
3. `ns_steps` 可根据训练稳定性和性能需求调整。短跑通可使用较小值，正式训练建议结合 loss 曲线和吞吐表现验证。
4. `matched_adamw_rms` 会影响 Muon 更新量级，修改学习率时建议同步观察该参数对收敛的影响。
