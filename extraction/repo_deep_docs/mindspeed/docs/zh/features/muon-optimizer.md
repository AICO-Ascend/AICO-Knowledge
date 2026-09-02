# Muon 优化器

> 仓 `mindspeed` · 路径 `docs/zh/features/muon-optimizer.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed/docs/zh/features/muon-optimizer.md

# Muon 优化器 深度解读

## 【定位】

本文档系统描述 MindSpeed（昇腾大模型加速库）如何将 **Muon 矩阵优化器**集成到 Megatron 的训练流程中，使其能在开启 TP / MoE / ZeRO 等并行能力的生产级大模型训练场景下与 Adam 等标量优化器协同工作，并解决矩阵正交化在分布式环境下的若干工程难题。

---

## 【技术要点】

1. **矩阵 vs 标量参数双优化器并存架构**：Muon 仅作用于二维矩阵权重（典型为 Transformer 线性层参数）；embedding、输出层、bias、norm 等一维/非矩阵参数仍由 Adam（默认）或 Lion（通过 `--muon-scalar-optimizer`）负责。MindSpeed 通过 optimizer feature patch 接管 Megatron 的 optimizer 构建入口，完成参数分类、打标、Muon 构建、标量优化器构建和 wrapper 封装。

2. **Newton-Schulz 正交化作为核心机制**：对进入 Muon 的参数，先维护类似 SGD 的 `momentum_buffer`（动量系数由 `--muon-momentum` 控制，默认 `0.95`），可选 Nesterov 形式（`--muon-nesterov`），随后对更新矩阵做 Newton-Schulz 迭代以获得近似正交化的更新方向。迭代配置三件套为 `--muon-num-ns-steps`（默认 `5`）、`--muon-coefficient-type`（默认 `quintic`）、`--muon-scale-mode`（默认 `spectral`，可选 `unit_rms_norm` 或 `shape_scaling`），另可通过 `--muon-extra-scale-factor`（默认 `1.0`）额外缩放。

3. **TP 分片矩阵正交化与重复参数过滤**：通过 `TensorParallelMuon` 感知参数的 `partition_dim`，按 TP group size 还原全局矩阵形状以正确计算缩放因子；patch `param_is_not_tensor_parallel_duplicate` 以支持显式 `tp_group` 传入，从而在梯度范数/裁剪/zero count 统计中过滤 TP 重复视图。QKV 融合权重通过 `is_qkv` 标记按 Q/K/V 结构拆分再分别正交化（可通过 `--muon-no-split-qkv` 关闭）。TP 下的计算模式由 `--muon-tp-mode` 控制（默认 `blockwise`，可选 `duplicated`、`distributed`）。

4. **Dense/Expert 通信组区分**：通过 `expert_tp` 属性标记 expert tensor parallel 参数，使其在梯度统计和 TP duplicate filter 时使用 expert TP group，而非普通 TP group。

5. **bf16 master param 自定义属性继承**：bf16 训练会创建 fp32 master param；MindSpeed 扩展了 tensor-parallel 属性复制流程，将 `expert_tp` 与 `is_qkv` 从原始参数同步到 master param，避免后续 optimizer step 中 TP group 选择和 QKV split 失效。

6. **Layer-wise Distributed Optimizer（ZeRO 兼容路径）**：当 `--use-distributed-optimizer` 开启时，Muon 不沿用 Megatron 原生连续 buffer 切分，而是按"完整参数"为单位分配 owner rank：参数按规模排序后，在 DP/EP DP rank 间 ping-pong 分配；step 后通过 `torch.distributed.all_gather` 收集**不等长** flat tensor，再 unflatten 回模型参数；torch checkpoint 按 DP rank 额外保存/恢复各自 optimizer state。可叠加重叠优化：`--overlap-grad-reduce` + `--overlap-param-gather`，把参数同步挂到 DDP bucket，由 forward pre-hook 异步触发。

---

## 【关键机制与数据】

### Muon 单步更新数据流

1. 维护 `momentum_buffer`，当前梯度更新动量；
2. 根据是否开启 Nesterov 得到本轮更新矩阵；
3. 对更新矩阵执行 Newton-Schulz 迭代得到近似正交化方向；
4. 按 TP 切分维度乘以 TP group size 恢复全局形状语义后计算缩放因子；
5. 对 `is_qkv` 参数先按 Q/K/V 拆分 → 分别正交化 → 拼回原形状；
6. 对 dense/expert 参数分别走对应 wrapper 的 `grad_stats_parallel_group` 与 `tp_group`。

### Layer-wise Distributed Optimizer 数据流

- 排序：所有参数按参数规模排序；
- 分配：DP/EP DP rank 间 ping-pong 分配 owner rank 以均衡参数量；
- 梯度同步：仍由 DDP 完成，每个 rank 可获得完整参数对应的梯度；
- 本地更新：每个 rank 的本地 optimizer 仅更新自己拥有的参数；
- 参数同步：step 后用 `torch.distributed.all_gather` 收集**不等长** flat tensor，再按各 rank 参数列表 unflatten 复制回模型参数；
- checkpoint：按 DP rank 额外保存 optimizer state 文件，恢复时各 rank 加载各自对应 state。

> 原文：未给出具体性能数据（如加速比、显存节省百分比等数字），仅描述了功能行为与适用场景。

---

## 【表格解读】

### 原文参数表（逐字还原）

| 参数 | 默认值 | 说明 |
| --- | --- | --- |
| `--optimizer` | `adam` | 指定优化器类型。设置为 `muon` 时启用 Muon 优化器。 |
| `--use-distributed-optimizer` | 关闭 | 与 Muon 同时使用时，启用 layer-wise distributed optimizer 路径。 |
| `--overlap-grad-reduce` | 关闭 | 开启梯度 reduce 与反向计算重叠；使用 `--overlap-param-gather` 时需要同时开启。 |
| `--overlap-param-gather` | 关闭 | 在 layer-wise distributed optimizer 路径中，将参数同步延迟到 DDP forward pre-hook，通过 bucket 触发异步 gather。 |
| `--overlap-param-gather-with-optimizer-step` | 关闭 | 当前 Muon 路径暂不支持该开关。 |
| `--muon-momentum` | `0.95` | Muon 内部动量系数，用于更新 `momentum_buffer`。 |
| `--muon-nesterov` | 关闭 | 是否在 Muon 内部动量更新中使用 Nesterov 形式。 |
| `--muon-scale-mode` | `spectral` | Muon 更新矩阵的缩放方式，支持 `spectral`、`unit_rms_norm`、`shape_scaling`。 |
| `--muon-fp32-matmul-prec` | `medium` | Newton-Schulz 迭代中 fp32 matmul 的精度配置。 |
| `--muon-coefficient-type` | `quintic` | Newton-Schulz 迭代使用的 coefficient 类型。 |
| `--muon-num-ns-steps` | `5` | Newton-Schulz 迭代步数。 |
| `--muon-tp-mode` | `blockwise` | TP 场景下 Newton-Schulz 的计算方式，支持 `blockwise`、`duplicated`、`distributed`。 |
| `--muon-extra-scale-factor` | `1.0` | Muon 更新额外乘上的缩放系数。 |
| `--muon-scalar-optimizer` | `adam` | 非矩阵参数使用的标量优化器，支持 `adam`、`lion`。 |
| `--muon-no-split-qkv` | 默认开启 QKV split | 关闭 QKV 融合权重拆分处理。 |
| `--apply-wd-to-qk-layernorm` | 关闭 | 对 Q/K layernorm 保留 weight decay；开启后其他一维参数和 bias 仍默认跳过 weight decay。 |

### 逐行解读

- **`--optimizer`**：总开关，设为 `muon` 即触发 MindSpeed 的 optimizer feature patch 接管构建流程。
- **`--use-distributed-optimizer`**：与 Muon 同时使用时不是走 Megatron 原生分布式 optimizer，而是 layer-wise distributed optimizer。
- **`--overlap-grad-reduce` / `--overlap-param-gather`**：两者需同时开启才能在 Muon 路径下生效，目的是减少参数同步对训练 step 的阻塞；后者把同步动作挂到 DDP bucket，由 forward pre-hook 触发。
- **`--overlap-param-gather-with-optimizer-step`**：原文明确写明当前 Muon 路径**暂不支持**该开关。
- **`--muon-momentum`**：控制 SGD 类动量系数，与 Nesterov 配合可调整更新方向的光滑度。
- **`--muon-scale-mode`**：决定正交化后更新矩阵如何被缩放回参数空间，三种模式对应不同的谱范数假设。
- **`--muon-fp32-matmul-prec`**：Newton-Schulz 迭代中 fp32 matmul 的精度（昇腾侧 `medium` 等档位），影响数值稳定性与性能。
- **`--muon-coefficient-type` / `--muon-num-ns-steps`**：分别配置 Newton-Schulz 多项式系数族与迭代步数，默认 `quintic` + `5` 步。
- **`--muon-tp-mode`**：TP 场景下 Newton-Schulz 的三种计算模式——`blockwise`（按分片块计算，默认）、`duplicated`（各 TP rank 重复计算完整矩阵）、`distributed`（跨 rank 分布式计算）。
- **`--muon-extra-scale-factor`**：在 Muon 标准缩放之外再乘一个缩放因子，调参旋钮。
- **`--muon-scalar-optimizer`**：选择非矩阵参数使用的优化器，默认 Adam；选 Lion 时需要外部提供 Lion 实现。
- **`--muon-no-split-qkv`**：默认是开启 QKV 拆分的，加此参数关闭——意味着关闭后 Muon 会直接对融合大矩阵做正交化。
- **`--apply-wd-to-qk-layernorm`**：仅对 Q/K layernorm 这一特定一维参数保留 weight decay，其余一维参数与 bias 仍默认跳过 weight decay。

---

## 【公式解读】

原文无公式。

（文档用文字描述了 Newton-Schulz 迭代、Nesterov 更新与 TP 缩放因子的行为，但未给出任何 LaTeX 或伪代码形式的数学公式。）

---

## 【关联】

文档内部虽未提供 markdown 链接，但明确提及的上下游模块/特性关系如下：

- **Megatron optimizer 构建流程**：Muon 通过 optimizer feature patch 接入，替换/扩展其参数分类与 wrapper 封装路径。
- **Adam / Lion**：作为非矩阵参数的标量优化器，与 Muon 并存；Lion 需外部实现。
- **TP（张量并行）**：核心适配对象之一，触发 `TensorParallelMuon`、TP duplicate filter、`partition_dim` 缩放、`is_qkv` 拆分等子机制。
- **MoE / Expert Parallel**：通过 `expert_tp` 属性区分 dense 与 expert 参数的通信组。
- **ZeRO / `--use-distributed-optimizer`**：触发 layer-wise distributed optimizer 路径，依赖 DDP 完成梯度同步。
- **DDP / `torch.distributed.all_gather`**：梯度同步与 step 后不等长参数 all-gather 的基础。
- **torch checkpoint**：按 DP rank 拆分保存/恢复 optimizer state。
- **FSDP / torch FSDP2**：原文明确指出 Muon 路径**不支持**与 MindSpeed 自定义 FSDP 或 torch FSDP2 同时使用。
- **fp16**：原文明确指出 Muon 路径**不支持** fp16，仅支持 bf16 与 fp32。
- **Megatron 原生 distributed optimizer 连续 buffer 切分**：被 layer-wise distributed optimizer 显式替代，不再沿用。

---

## 【使用方法】

### 基础启用

```bash
--optimizer muon \
--bf16
```

### 启用 Layer-wise Distributed Optimizer（ZeRO 类分片场景）

```bash
--optimizer muon \
--bf16 \
--use-distributed-optimizer
```

### 在 Layer-wise 路径下叠加重叠优化

```bash
--optimizer muon \
--bf16 \
--use-distributed-optimizer \
--overlap-grad-reduce \
--overlap-param-gather
```

### 关闭 QKV 融合权重拆分

```bash
--muon-no-split-qkv
```

### 常用可选参数（原文汇总）

```bash
--muon-momentum 0.95
--muon-nesterov
--muon-scale-mode spectral
--muon-fp32-matmul-prec medium
--muon-coefficient-type quintic
--muon-num-ns-steps 5
--muon-tp-mode blockwise
--muon-extra-scale-factor 1.0
--muon-scalar-optimizer adam
--apply-wd-to-qk-layernorm
```

### 注意事项（原文明示的约束）

- 不支持 fp16，请使用 bf16 或 fp32；
- 不支持与 MindSpeed 自定义 FSDP 或 torch FSDP2 同时使用；
- 与 `--use-distributed-optimizer` 同时使用即走 layer-wise distributed optimizer 路径；
- `--overlap-param-gather` 需同时开启 `--use-distributed-optimizer` 和 `--overlap-grad-reduce`；
- 暂不支持 `--overlap-param-gather-with-optimizer-step`；
- layer-wise all-gather 依赖 `torch.distributed.all_gather` 支持不等长 tensor，建议在目标集群上验证 DP>1、EP>1、MoE 与 checkpoint 恢复场景；
- 若配置 `--muon-scalar-optimizer lion`，需额外提供 Lion 实现。
