# 长序列并行

> 仓 `mindspeed-rl` · 路径 `docs/zh/features/context_parallel.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-rl/docs/zh/features/context_parallel.md

# 长序列并行 (Context Parallel) 深度解读

## 【定位】
本篇文档系统介绍了 mindspeed-rl 仓库中**长序列并行（Context Parallel, CP）能力**——通过 Ulysses 与 Ring Attention 两种分布式并行方案，将输入序列在序列维度上切分到多个计算设备，以解决长序列训练场景下的激活显存溢出（OOM）问题。

---

## 【技术要点】

1. **两种并行算法并列提供**：Ulysses（All-to-All 通信）与 Ring Attention（环形通信）作为可选方案，通过 `context_parallel_algo` 字段切换，**默认取 ulysses_cp_algo**。

2. **Ulysses 的硬性约束**：模型 `num_attention_heads % (CP*TP) = 0` 必须满足，否则无法使用 ulysses_cp_algo。

3. **Ring Attention 的灵活性优势**：相较 Ulysses，Ring Attention 的 `cp_size` **无模型 num_attention_heads 的限制**，即不必被 CP×TP 整除。

4. **attention_mask_type 区分**：Ulysses 配置示例使用 **general**；Ring Attention 默认使用 **causal**。

5. **与 remove_padding 协同使用的三个开关**：必须将 `use_remove_padding`、`reset_attention_mask`、`no_pad_to_seq_lengths` **全部设置为 true** 才能叠加生效。

6. **Ring Attention 计算/通信掩盖条件**：理论上需满足 **c ≥ F/B**（c 为每个计算块分到的序列长度，F 为每个 device 的 FLOPS，B 为每个 device 间的带宽），实践中需保证 c 足够大以较好掩盖通信开销。

---

## 【关键机制与数据】

### Ulysses 工作流（原文逐字描述）
- **第一步**：将各个样本在序列维度上分割给参与的计算设备；
- **第二步**：在 attention 计算之前，对已分割的 Q、K、V 执行 **All-to-All 通信**，使每个设备接收**完整序列但仅注意力头的非重叠子集**，从而并行计算不同注意力头；
- **第三步**：使用**另一个 All-to-All** 在注意力头上收集结果，同时重新在序列维度上分区。

### Ring Attention 工作流（原文逐字描述）
- **环状通信结构**：在进程之间构建 attention 计算块的 Ring，每个进程持有一个切分后的本地 QKV 块；
- **遍历计算**：计算完本地 attention 后，**向后发送、向前获取 KV 块**，遍历进程设备环，以**逐块**方式进行 attention 和 FFN 计算；
- **掩盖效果**：本地 attention 计算与 KV 块通信**理想情况下可互相掩盖**，消除额外通信开销。

### 关键数据/参数
| 参数 | Ulysses | Ring Attention |
|------|---------|----------------|
| 约束条件 | num_attention_heads % (CP×TP)=0 | 无 num_attention_heads 限制 |
| attention_mask_type | general（示例） | causal（默认） |
| 通信原语 | 两次 All-to-All | Ring 状 send/recv |
| 算法标识符 | ulysses_cp_algo | megatron_cp_algo |

原文未提供具体性能 benchmark 数据（如吞吐量、加速比、显存节省比例等），仅给出了理论掩盖公式 c≥F/B。

---

## 【表格解读】

**原文无表格**。原文以 YAML 代码块形式给出配置示例，未以表格形式列出参数对照或性能对比。

---

## 【公式解读】

原文给出 **1 个** 关键约束式（非 LaTeX 形式，按原文逐字保留）：

$$c \geq F / B$$

**符号含义（依据原文解释）：**
- **c**：每个计算块分到的序列长度（sequence length per chunk）；
- **F**：每个 device 的 **FLOPS**（算力上限）；
- **B**：每个 device 间的**带宽**（通信上限）。

**作用**：该式是 Ring Attention 实现"本地 attention 计算与 KV 块通信互相掩盖"的**理论下限条件**——只有当单个计算块承担的序列长度 c 足够大（≥ 算力除以带宽），其计算时间才能盖过通信时间，从而消除通信开销。原文指出"具体推导过程参见原文"（即 Ring Attention 原论文 arxiv 2310.01889）。

---

## 【关联】

1. **与 remove_padding 特性的关系**：长序列并行在使用时**强依赖 remove-padding 协同**——必须开启 `use_remove_padding: true`（在 `rl_config` 中）以及 `reset_attention_mask: true`、`no_pad_to_seq_lengths: true`（在 `megatron_training` 中），否则变长样本的 padding 会破坏序列维度的切分语义。文中明确点出此为"叠加使能"配置。

2. **与 DPO 算法的关系**：Ulysses 配置小节单独给出了**直接偏好对齐（DPO）算法**的 CP 配置入口——需写在 `megatron_training` 段下，并设置 `no_pad_to_seq_lengths: true`、`context_parallel_size: 2`、`context_parallel_algo: ulysses_cp_algo`。

3. **与 Megatron 训练框架的关系**：CP 算法标识符 `megatron_cp_algo` 表明 Ring Attention 方案对接的是 Megatron 原生的 CP 实现路径，而 Ulysses 由本仓库独立实现（标识符 `ulysses_cp_algo`），二者通过统一的 `context_parallel_algo` 字段对外暴露。

4. **上下游依赖**：CP 处于 actor 的并行拓扑层，受 TP（Tensor Parallel）配置影响（因 Ulysses 约束公式中含 CP×TP 项）；与序列并行（SP）在注意力层互补——SP 在序列维度切分激活，CP 在更长序列维度上扩展显存边界。

---

## 【使用方法】

### 启用 Ulysses（原文摘录）
```yaml
actor_config:
   context_parallel_size: 2
   context_parallel_algo: ulysses_cp_algo
   attention_mask_type: general

# 与remove-padding特性一起使用
rl_config:
  use_remove_padding: true

megatron_training:
   reset_attention_mask: true
   no_pad_to_seq_lengths: true
```

### 启用 Ulysses + DPO（原文摘录）
```yaml
# 填写在megatron_training
megatron_training:
   no_pad_to_seq_lengths: true
   context_parallel_size: 2
   context_parallel_algo: ulysses_cp_algo
```

### 启用 Ring Attention（原文摘录）
```yaml
actor_config:
   context_parallel_size: 2
   context_parallel_algo: megatron_cp_algo
   attention_mask_type: causal

# 与remove-padding特性一起使用
rl_config:
  use_remove_padding: true

megatron_training:
   no_pad_to_seq_lengths: true
   reset_attention_mask: true
```

### 关键配置项语义（原文）
- **`context_parallel_size`**：CP 并行数（即参与序列维度切分的设备数）。
- **`context_parallel_algo`**：选用的长序列并行方法，可选 `ulysses_cp_algo`（默认）或 `megatron_cp_algo`；不配置则默认 `ulysses_cp_algo`。
- **`attention_mask_type`**：attention mask 类型，Ring Attention 默认 **causal**。
- **Ulysses 校验**：必须满足 `num_attention_heads % (CP*TP) = 0`。
- **Ring Attention 叠加 remove-padding**：除三开关均 true 外，需明确指出"否则这些配置都不要配，默认 false"——即若不启用 remove-padding，则 `reset_attention_mask` 与 `no_pad_to_seq_lengths` 保持默认 false。

原文未涉及具体的命令行启动方式、环境变量或 docker 镜像配置。
