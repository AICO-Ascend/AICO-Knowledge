# Muon Optimizer

> 仓 `mindspeed-llm` · 路径 `docs/en/pytorch/features/mcore/muon.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-llm/docs/en/pytorch/features/mcore/muon.md

# Muon Optimizer 文档深度解读

## 【定位】

这篇文档描述 mindspeed-llm 框架中 **Muon 优化器**（Momentum + Orthogonalization Update）的启用方法与配置参数——一种通过 Newton-Schulz 迭代对动量梯度进行正交化，从而在相同算力预算下追求比 Adam 更高收敛效率的 LLM 预训练优化器。

---

## 【技术要点】

1. **核心机制**：Muon 的核心思想是**通过 Newton-Schulz 迭代对动量梯度进行正交化**，使得最终的参数更新矩阵近似正交（approximately orthogonal），区别于 Adam 的逐元素更新方式。
2. **内部优化器**：Muon 内部使用一个 SGD（带 momentum/Nesterov）来生成待正交化的梯度。
3. **默认启用 Blockwise 模式**：默认开启按块（blockwise）的 Newton-Schulz 正交化，并通过 `--muon-no-split-qkv` 控制是否对 QKV 参数独立正交化（默认 True 即"不分块独立正交化"）。
4. **关键默认参数**：`--muon-momentum=0.9`、`--muon-num-ns-steps=5`、`--muon-fp32-matmul-prec=medium`、`--muon-scale-mode=spectral`、`--muon-tp-mode=blockwise`、`--muon-extra-scale-factor=1.0`。
5. **兼容性约束**：Muon 与四种特性互斥，不能同时启用——梯度归约/参数收集 overlap、Distributed optimizer、Torch FSDP2。
6. **适用场景定位**：原文明确指其"suit training tasks that seek better convergence efficiency than Adam under the same compute budget"，即算力预算固定时追求更优收敛的训练任务。

---

## 【关键机制与数据】

**原文机制描述**：Muon 的核心流程为——取动量梯度 → 通过 Newton-Schulz 迭代做正交化 → 乘以缩放因子（spectral 模式等）→ 得到近似正交的参数更新矩阵 ΔW。由于更新矩阵近似正交，原文表述其为 "approximately orthogonal"，从而改善 LLM 预训练收敛效率。

**与算力/稳定性的权衡**（原文）：`--muon-ns-steps` 更多步数能提升正交化精度（more steps produce more accurate orthogonalization），但同时增加计算开销（increase compute cost）；`--muon-fp32-matmul-prec` 影响 NS 迭代中正交化的数值稳定性。

**Blockwise 默认行为**（原文）：默认 blockwise 模式开启，QKV 默认**不**独立正交化（通过 `--muon-no-split-qkv` 控制，参数说明为"Disables independent orthogonalization of QKV parameters in blockwise mode"）。

> 原文未提供具体的性能数字（如训练 step/收敛时间/吞吐等），故不补充臆测数据。

---

## 【表格解读】

### 表 1：Basic Parameters

| Parameter | Type | Default Value | Description |
|------|------|--------|------|
| --optimizer muon | str | — | Enables the Muon optimizer. |
| --muon-momentum | float | 0.9 | Momentum coefficient for the internal SGD used by Muon. |
| --muon-use-nesterov | flag | False | Enables Nesterov momentum in the internal SGD. |
| --muon-no-split-qkv | flag | True | Disables independent orthogonalization of QKV parameters in blockwise mode. Blockwise mode is enabled by default. |
| --muon-extra-scale-factor | float | 1.0 | Applies an additional global scaling factor to the Muon update. |

**逐行解读**：
- **`--optimizer muon`**：入口开关，必须设置才能启用 Muon。
- **`--muon-momentum 0.9`**：Muon 内部 SGD 使用的动量系数，0.9 是 SGD 系列的常见默认值。
- **`--muon-use-nesterov`**：默认关闭，开启后可让内部 SGD 使用 Nesterov 动量形式。
- **`--muon-no-split-qkv`**：注意虽然默认值字段显示 True，但其语义是"禁用 QKV 独立正交化"，因此在 Blockwise 模式下 QKV 默认是合并处理而非独立正交化——这一点容易与"Flag=True=启用"直觉混淆。
- **`--muon-extra-scale-factor 1.0`**：在 Muon 更新之上叠加的全局缩放因子，默认 1.0 表示无额外缩放，可用于调参控制更新幅度。

### 表 2：Newton-Schulz Iteration Parameters

| Parameter | Type | Default Value | Description |
|------|------|--------|------|
| --muon-num-ns-steps | int | 5 | Number of Newton-Schulz iteration steps. More steps produce more accurate orthogonalization, but increase compute cost. |
| --muon-fp32-matmul-prec | str | medium | FP32 matrix-multiplication precision in NS iterations. This affects the numerical stability of orthogonalization. |
| --muon-scale-mode | str | spectral | Scaling mode for the update after orthogonalization. |

**逐行解读**：
- **`--muon-num-ns-steps=5`**：NS 迭代步数，控制正交化精度与算力的折中——步数越多正交化越精确，但计算开销越大。
- **`--muon-fp32-matmul-prec=medium`**：NS 迭代中 FP32 矩阵乘法的精度档位，影响正交化过程的数值稳定性。
- **`--muon-scale-mode=spectral`**：正交化后对更新矩阵的缩放方式采用 spectral 模式（按谱范数/谱缩放）。

### 表 3：Tensor Parallel Mode Parameters

| Parameter | Type | Default Value | Description |
|------|------|--------|------|
| --muon-tp-mode | str | blockwise | How Newton-Schulz orthogonalization for tensor-parallel weights is calculated. |

**逐行解读**：
- **`--muon-tp-mode=blockwise`**：在张量并行（TP）切分场景下，权重如何进行 Newton-Schulz 正交化——采用 blockwise 方式。

### 表 4：Usage Constraints（互斥特性表）

| Incompatible Feature | Corresponding Parameter |
|------------|----------|
| Gradient reduction overlap | --overlap-grad-reduce |
| Parameter gather overlap | --overlap-param-gather |
| Distributed optimizer | --use-distributed-optimizer |
| Torch FSDP2 | --use-torch-fsdp2 |

**逐行解读**：
- **Gradient reduction overlap / Parameter gather overlap**：Muon 与梯度归约、参数收集的 overlap 优化不兼容——说明 Muon 的梯度/参数通信时序与 overlap 策略冲突。
- **Distributed optimizer**：与分布式优化器（将优化状态分片以节省显存）不兼容，推测与 Muon 内部对全量参数做正交化更新的方式冲突。
- **Torch FSDP2**：与 PyTorch 原生 FSDP2 不兼容，同样可能因正交化要求完整参数矩阵而与分片存储矛盾。

---

## 【公式解读】

**原文无公式**。文档中既未给出 Newton-Schulz 迭代的 LaTeX 表达式，也未给出 Muon 更新规则的伪代码或数学定义，只在文字层面描述了 "orthogonalize momentum gradients through Newton-Schulz iteration" 与 "parameter update matrix is approximately orthogonal"。因此不作无根据推导。

---

## 【关联】

**文末内部链接**：原文未提供任何内部链接（标注为"无"）。

**从正文推断的关联关系**：
- 与 **Tensor Parallel（TP）** 强相关：专门提供 `--muon-tp-mode` 参数以控制 TP 切分场景下的正交化计算方式。
- 与 **分布式优化器** 互斥：与 `--use-distributed-optimizer` 不兼容，表明 Muon 不支持优化状态分片。
- 与 **FSDP2** 互斥：与 PyTorch FSDP2 不能同时启用，暗示 Muon 需要完整（非分片）的参数矩阵才能进行正交化。
- 与 **通信 overlap 机制** 互斥：与梯度归约/参数收集 overlap 不兼容，说明 Muon 对通信与计算的重叠有特定时序要求。
- 与 **QKV 参数结构** 关联：通过 `--muon-no-split-qkv` 控制 QKV 是否在 Blockwise 模式下被独立正交化。

---

## 【使用方法】

**启用方式**：在训练脚本中将优化器参数设为 `--optimizer muon` 即可启用 Muon 优化器。

**核心配置项**（按表分组）：
- **基础**：`--muon-momentum 0.9`、`--muon-use-nesterov`、`--muon-no-split-qkv`、`--muon-extra-scale-factor 1.0`
- **NS 迭代**：`--muon-num-ns-steps 5`、`--muon-fp32-matmul-prec medium`、`--muon-scale-mode spectral`
- **TP 模式**：`--muon-tp-mode blockwise`

**必须规避的并发配置**（互斥项）：`--overlap-grad-reduce`、`--overlap-param-gather`、`--use-distributed-optimizer`、`--use-torch-fsdp2`——使用 Muon 时**不得**同时开启上述四项。

> 原文未提供具体训练脚本片段或端到端启动命令示例，仅以 `--optimizer muon` 这一命令行参数形式给出启用方式。
