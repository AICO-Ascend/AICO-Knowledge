# VLM 模型 Loss 计算类型

> 仓 `mindspeed-mm` · 路径 `docs/zh/features/vlm_model_loss_calculate_type.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-mm/docs/zh/features/vlm_model_loss_calculate_type.md

# VLM 模型 Loss 计算类型 — 一体化深度解读

---

## 【定位】

本文档描述 MindSpeed MM 在 VLM（视觉语言模型）训练中，针对"相同 global batch size 但不同 micro_batch_size / grad_acc_steps 组合会导致 loss 曲线和最终值不一致"这一业界已知问题，提供的 **三种 Loss 计算粒度（默认 / 按样本 / 按 Token）方案及其在 Megatron 与 FSDP2 两种后端的启用方式**。

---

## 【技术要点】

1. **问题根因**：当 global batch size 固定时，不同 `(micro_batch_size, grad_acc_steps)` 组合（如原文示例 `micro_batch_size=32, grad_acc_steps=2` vs `micro_batch_size=16, grad_acc_steps=4`），在 Hugging Face Transformers 的 VLM 实现中会产生不同的 loss 曲线与最终数值；Qwen2.5-VL、Qwen3-VL 等模型因传参错误或显式不计算 `num_token_in_batch` 至今仍受影响。
2. **三种 Loss 计算方式**：
   - **默认方式**：微批次维均值 → 梯度累积维均值 → DP 域均值。
   - **按样本粒度（Calculate Per Sample Loss）**：样本内 token 维均值 → 微批次维均值 → 梯度累积维均值 → DP 域均值。
   - **按 Token 粒度（Calculate Per Token Loss）**：全局批次所有有效 token CE 损失累加，除以全局有效 token 总数。
3. **Megatron 后端使能**：入口为 `pretrain_vlm.py`，通过命令行参数 `--calculate-per-sample-loss` 或 `--calculate-per-token-loss` 启用；二者互斥，不可同时使用。
4. **FSDP2 后端使能**：通过 `loss_cfg.loss_type` 字段配置，可选值 `default` / `per_sample_loss` / `per_token_loss`，原生 FSDP2（推荐）写在 YAML 的 `features.loss_cfg` 段，megatron-FSDP2（过渡态、标注"将退出"）写在 `model.json` 的 `loss_cfg` 字段。
5. **样本分布敏感性的副作用**：原文警告，若训练样本 response 长度极不均衡（从单 token 到很长），按 token 粒度计算会让长 response（target token 多）的样本权重更大，引入样本间不平衡。
6. **辅助参考资源**：文档引用了 unsloth 博客 `https://unsloth.ai/blog/gradient` 作为该问题的社区讨论来源（属外部链接，非仓内文档链接）。

---

## 【关键机制与数据】

**工作原理（Loss 聚合层次）**

原文假设训练配置为 `micro_batch_size=2`、`grad_acc_steps=2`、双卡训练（DP=2），以此展开三种聚合层次的对比：

- **默认方式**：三阶均值——先在 micro_batch 内对有效 token CE 求均值（步骤 1），再在梯度累积维求均值（步骤 2），最后在 DP 域求均值（步骤 3）。这与 Transformers 默认行为一致。
- **按样本粒度**：四阶均值——在每个样本内部对有效 token 求均值（步骤 1，**比默认方式多一层"样本内均值"**），后续与默认方式相同的 micro-batch、grad_acc、DP 三层均值。
- **按 Token 粒度**：单步归约——**直接累加**全局所有有效 token 的 CE 损失，再除以**全局有效 token 总数**。这是聚合层次最浅、对 global batch size 变化最稳定的方式。

**数据流（原文）**：
> 步骤 1：微批次维度有效 token CE 均值 → 步骤 2：梯度累积维度均值 → 步骤 3：DP 域均值（默认方式）
> 步骤 1：样本内有效 token CE 均值 → 步骤 2：微批次均值 → 步骤 3：梯度累积均值 → 步骤 4：DP 域均值（按样本）
> 直接累加全局有效 token CE → 除以全局有效 token 总数（按 Token）

**性能数据**：原文未提供 benchmark、吞吐量或精度对比数字，故此处不臆造。

---

## 【表格解读】

**原文无表格**。文中三种方式的对比通过"步骤 1/2/3/4"列表形式给出，未以表格组织；参数使能方式通过代码块（shell / yaml / json）给出，亦未以表格形式聚合。

---

## 【公式解读】

**原文无公式**（无 LaTeX 或伪代码形式的显式公式）。Loss 聚合逻辑以自然语言"步骤 N"和"求均值 / 累加 / 除以总数"等动词描述，未给出符号化表达式。可解读的隐含算子含义如下：

- "**对有效 token 的交叉熵损失求均值**"：在某一聚合维度上，对该维度内所有有效（非 padding / 非 mask）的 token CE 取算术平均。
- "**直接累加…除以全局有效 token 总数**"：等价于 `loss = Σ_i CE_i / N_total`，其中 `N_total` 是 global batch 内所有有效 token 之和，而非局部 batch 内的均值。

---

## 【关联】

- **上游问题域**：与 Hugging Face Transformers 的 VLM loss 计算实现直接相关，文档明确指出 Transformers 已在部分模型修复但 Qwen2.5-VL、Qwen3-VL 仍受影响（原因：传参错误 / 显式不计算 `num_token_in_batch`）。
- **后端分支**：本文档同时覆盖 **Megatron 后端**（入口 `pretrain_vlm.py`）与 **FSDP2 后端**（又细分为 **原生 FSDP2** 与 **megatron-FSDP2** 两条线）；其中 megatron-FSDP2 标注为"过渡态、将退出"。
- **下游影响**：原文"注意事项"明确指出，loss 计算方式选择不当会**对下游任务评测产生较大影响**，并给出具体的样本分布失衡场景作为风险说明。
- **外部参考**：唯一给出的关联链接是 unsloth 博客 `https://unsloth.ai/blog/gradient`，属于社区讨论性质的外部资源。
- **仓内链接**：文档文末未提供任何仓内内部链接（与其他特性 / 模块 / 上下游文档的交叉引用）。

---

## 【使用方法】

**Megatron 后端**（入口 `pretrain_vlm.py`）：

- **默认计算方式**：不启用 `--calculate-per-sample-loss` 也不启用 `--calculate-per-token-loss`。
- **按样本粒度**：在 `GPT_ARGS` 中追加 `--calculate-per-sample-loss \`。
- **按 Token 粒度**：在 `GPT_ARGS` 中追加 `--calculate-per-token-loss \`。
- **互斥约束**：`--calculate-per-sample-loss` 与 `--calculate-per-token-loss` 不可同时使用。

**FSDP2 后端**（两种配置方式的 `loss_type` 取值完全一致）：

| 启用方式 | 取值 |
|---|---|
| 默认方式 | `default` |
| 按样本粒度 | `per_sample_loss` |
| 按 Token 粒度 | `per_token_loss` |

- **原生 FSDP2（推荐）**：在模型 YAML 配置文件的 `features.loss_cfg` 段设置 `loss_type` 字段。
- **megatron-FSDP2（过渡态、标注"将退出"，入口 `pretrain_transformers.py`）**：在 `model.json` 中添加 `"loss_cfg": { "loss_type": "..." }` 字段。

**注意事项**（原文明确给出）：

1. Megatron 后端两参数互斥。
2. 需根据训练数据集样本 response 长度分布选择合适方式——若样本长度极不均衡，按 token 粒度会让长 response 样本被训练得更充分，引入样本间不平衡。

## 图文联合解读

- `default.png`: 1) **图里画了什么**：图绘 DP=2 双卡（rank0/rank1）下两次梯度累积的微批次，绿色方格标注有效 token 的逐 token 交叉熵 loss（0.01–0.32），虚线格为 padding；箭头逐级汇聚：先微批次内对有效 token 求均值（loss_0_1=0.05、loss_1_1=0.135 等），再经梯度累积（×0.5）与 DP 域平均，最终得 loss=0.1725。

2) **论证结论**：默认方式沿"微批次→梯度累积→DP"三层独立对各 rank 内有效 token 求均值，padding 在每微批次内被局部剔除。

3) **与文档关系**：对应文档"默认方式"流程，与按样本/按 token 方案形成对比，凸显 padding 剔除粒度随 micro_batch_size 与 grad_acc_steps 组合而变，从而引发相同 global batch 下 loss 曲线不一致的问题。
- `sample_level.png`: **图文联合解读：**

1）图示：rank 0/1 各有两个微批次（grad_acc_step=2），每个微批次含不同数量的有效 token（4、5、3、5）与 padding；箭头标注了三级聚合——微批次内对有效 token 求均值（红色数字为 token 数）、再对 grad_acc 求均值、最后在 DP=2 域求均值，最终 loss=0.17125。

2）技术结论：默认方式先按"微批次 token 数"归一、再按"梯度步数"归一，使得当不同微批次有效 token 数不等时（如 4 vs 5、3 vs 5），loss 数值会随 micro_batch_size、grad_acc_steps 的拆分组合而漂移，相同 global batch size 下无法复现。

3）对应文档论点：这正是文档开篇指出的 Transformers 缺陷在 Qwen2.5-VL 等模型上的表现，故需切换为按样本或按 token 粒度计算以保证收敛一致性。
- `token_level.png`: **图文联合解读：**

1) **图示内容**：展示"按Token粒度计算Loss"流程。横轴为两个数据并行卡（rank 0、rank 1），纵轴为两次梯度累积。每个微批次以矩阵表示，绿色格为有效token（含数值0.01–0.32），白色"padding"格被排除；每卡每步先按token求和（得loss_0_1=0.45、loss_1_1=1.08、loss_0_2=1.72、loss_1_2=2.03），最终 loss = (0.45+1.08+1.72+2.03)/32 = 0.165。

2) **技术结论**：累加全局所有有效token的交叉熵，再除以有效token总数（total_num_token=32），padding不参与分母。

3) **与文档关系**：对应文档第三种方案，按token粒度归一化，使loss仅取决于有效token数量，与micro_batch_size和grad_acc_steps的具体组合解耦，保证全局batch一致时收敛结果稳定，规避了Transformers在Qwen-VL上的偏差问题。
