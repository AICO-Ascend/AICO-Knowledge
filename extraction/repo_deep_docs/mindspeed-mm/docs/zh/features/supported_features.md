# 特性列表

> 仓 `mindspeed-mm` · 路径 `docs/zh/features/supported_features.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-mm/docs/zh/features/supported_features.md

# 一体化深度解读：mindspeed-mm 特性列表文档

---

## 【定位】

这篇文档以一张兼容性矩阵表的形式，集中列出 MindSpeed MM 当前版本已发布的全部特性，并标注每个特性对 **FSDP2** 与 **MCORE（Megatron）** 两种训练后端的支持情况（✓ 支持 / × 不支持），目的是让用户在选型与组合训练方案时能快速判断"哪些特性可在哪个后端上跑"。

---

## 【技术要点】

1. **双后端并行架构**：MindSpeed MM 同时维护 FSDP2 与 MCORE（Megatron）两套训练后端，所有特性都需要分别标注对两者的兼容状态，反映其作为多模态大模型套件对 PyTorch 原生与 Megatron-Core 两种技术路线的并行支持。

2. **特性四类划分**：所有特性归入 4 个一级大类——**并行特性**（6 项）、**显存优化**（2 项）、**优化特性**（2 项）、**训练模式**（4 项），合计 14 项。

3. **FSDP2 独占特性**：Chunk Loss、SeqPack、LoRA 微调（基于 FSDP 后端）仅在 FSDP2 后端可用；FSDP2 自身作为并行策略也仅在该后端生效。

4. **MCORE 独占特性**：DiT Ring Attention、DiT USP、Hetero Parallel、tensor-parallel、Online Data Rearrange、LoRA 微调（基于 Mcore 训练后端）仅在 MCORE 后端可用。

5. **跨后端通用特性**：Unaligned Ulysses CP、Async Activation Offload、VLM Model Loss Calculate Type、Deterministic Computing 在 FSDP2 与 MCORE 两端均得到支持。

6. **不支持项统计**：在 14 项特性 × 2 个后端 = 28 个支持位点中，有 9 个标记为 ×（不支持），其中绝大部分集中在 MCORE 端（× 共 6 处：FSDP2 自身、DiT Ring Attention、DiT USP、Hetero Parallel、tensor-parallel、Online Data Rearrange 均在该列标 ×），其余 3 处 × 分布在 FSDP2 端的 DiT Ring Attention、DiT USP、Hetero Parallel、tensor-parallel、Online Data Rearrange、LoRA（基于 Mcore 训练后端）上——这一统计反映 MCORE 在多模态/扩散类并行策略（DiT 系列、异构并行、张量并行）与负载均衡方面仍承担主路径，而 FSDP2 则在数据侧优化（SeqPack）与 loss 计算优化（Chunk Loss）上承担主路径。

---

## 【关键机制与数据】

原文无独立的"工作原理/数据流/性能数据"段落，整个文件即一张静态兼容性矩阵。唯一可量化的信息是 ✓/× 矩阵的分布：14 项特性中，**双端均支持的有 4 项**（Unaligned Ulysses CP、Async Activation Offload、VLM Model Loss Calculate Type、Deterministic Computing），**FSDP2 独占 3 项**（Chunk Loss、SeqPack、LoRA 微调（FSDP 后端）），**MCORE 独占 6 项**（DiT Ring Attention、DiT USP、Hetero Parallel、tensor-parallel、Online Data Rearrange、LoRA 微调（Mcore 后端）），**FSDP2 自身作为基础特性仅在 FSDP2 后端存在**（表中与 FSDP2 特性行对应位置为 ✓/×）。

文档未提供任何吞吐量、显存占用、加速比或训练精度类性能数据。

---

## 【表格解读】

### 原文表格逐字还原

| 特性大类 | 特性子类 | 特性名称 | FSDP2 | MCORE |
|---|---|---|:---:|:---:|
| **并行特性**（rowspan=6） | FSDP2 | [FSDP2](fsdp2.md) | ✓ | × |
| | **序列并行**（rowspan=3） | [Unaligned Ulysses CP](unaligned_ulysses_cp.md) | ✓ | ✓ |
| | | [DiT Ring Attention](dit_ring_attention.md) | × | ✓ |
| | | [DiT USP](dit_usp.md) | × | ✓ |
| | 异构并行 | [Hetero Parallel](hetero_parallel.md) | × | ✓ |
| | 张量并行 | [tensor-parallel](https://gitcode.com/Ascend/MindSpeed/blob/master/docs/zh/features/tensor-parallel.md) | × | ✓ |
| **显存优化**（rowspan=2） | Offload | [Async Activation Offload](async_activation_offload.md) | ✓ | ✓ |
| | 负载均衡 | [Online Data Rearrange](online_data_rearrange.md) | × | ✓ |
| **优化特性**（rowspan=2） | **loss 优化**（rowspan=2） | [Chunk Loss](chunkloss.md) | ✓ | × |
| | | [VLM Model Loss Calculate Type](vlm_model_loss_calculate_type.md) | ✓ | ✓ |
| **训练模式**（rowspan=4） | **高效微调**（rowspan=2） | [LoRA 微调（基于 Mcore 训练后端）](lora_finetune.md) | × | ✓ |
| | | [LoRA 微调（基于 FSDP 后端）](lora_finetune_fsdp2.md) | ✓ | × |
| | 数据处理 | [SeqPack](seqpack.md) | ✓ | × |
| | 确定性计算 | [Deterministic Computing](deterministic_computing.md) | ✓ | ✓ |

### 逐行解读

**第 1 行 · 并行特性 / FSDP2**：FSDP2 自身作为一项独立并行策略在表中被列出，仅 FSDP2 后端 ✓，MCORE 后端 ×——这从结构上印证了"FSDP2 后端必须配合 FSDP2 并行策略"的耦合关系。

**第 2 行 · 并行特性 / 序列并行 / Unaligned Ulysses CP**：是序列并行（Context Parallel）方向上**两端都支持**的代表性特性，针对非对齐场景做了适配。

**第 3 行 · 并行特性 / 序列并行 / DiT Ring Attention**：仅 MCORE 支持，针对 DiT（Diffusion Transformer）架构的环形注意力机制，属于扩散生成路径上的关键并行优化。

**第 4 行 · 并行特性 / 序列并行 / DiT USP**：同样仅 MCORE 支持，与上一项同属 DiT 系列，是 DiT 的 USP（Ulysses Sequence Parallel）变体。

**第 5 行 · 并行特性 / 异构并行 / Hetero Parallel**：仅 MCORE 支持，对应异构集群（如不同型号 NPU 混部）下的并行策略，是面向硬件异构的高级能力。

**第 6 行 · 并行特性 / 张量并行 / tensor-parallel**：仅 MCORE 支持，且链接指向 Megatron 主仓（MindSpeed/docs/zh/features/tensor-parallel.md），说明张量并行能力继承自上游 Megatron/MindSpeed 而非 MindSpeed-MM 自研。

**第 7 行 · 显存优化 / Offload / Async Activation Offload**：双端支持，针对激活值做异步卸载以节省显存，是较为通用的显存优化手段。

**第 8 行 · 显存优化 / 负载均衡 / Online Data Rearrange**：仅 MCORE 支持，对数据做在线重排以均衡负载，更适合大规模分布式训练场景。

**第 9 行 · 优化特性 / loss 优化 / Chunk Loss**：仅 FSDP2 支持，将 loss 计算分块处理以节省显存/提升效率，是 FSDP2 路线独有的优化。

**第 10 行 · 优化特性 / loss 优化 / VLM Model Loss Calculate Type**：双端支持，针对视觉语言模型（VLM）的 loss 计算类型做适配。

**第 11 行 · 训练模式 / 高效微调 / LoRA 微调（基于 Mcore 训练后端）**：仅 MCORE 支持，是面向 Megatron 训练链路的 LoRA 微调实现。

**第 12 行 · 训练模式 / 高效微调 / LoRA 微调（基于 FSDP 后端）**：仅 FSDP2 支持，与上一行对称，覆盖 FSDP2 训练链路的 LoRA 微调。

**第 13 行 · 训练模式 / 数据处理 / SeqPack**：仅 FSDP2 支持，序列打包（Sequence Packing）以提升训练吞吐。

**第 14 行 · 训练模式 / 确定性计算 / Deterministic Computing**：双端支持，用于保证训练可复现。

---

## 【公式解读】

原文无公式。

---

## 【关联】

虽然文档标注为"内部链接: (无)"，但原文表格本身嵌入了 13 个超链接，指向仓库内其他特性说明文档，构成一份"特性索引页"。可识别出的关联节点如下：

- **后端基础特性**：[fsdp2.md](fsdp2.md)（FSDP2 自身）、[tensor-parallel](https://gitcode.com/Ascend/MindSpeed/blob/master/docs/zh/features/tensor-parallel.md)（继承自上游 MindSpeed/Megatron 主仓）。
- **序列并行分支**：[unaligned_ulysses_cp.md](unaligned_ulysses_cp.md)（Ulysses CP 的非对齐变体）、[dit_ring_attention.md](dit_ring_attention.md) 与 [dit_usp.md](dit_usp.md)（二者并列，是 DiT 架构下的两种序列并行实现，互为替代关系）。
- **异构与负载**：[hetero_parallel.md](hetero_parallel.md)（异构并行）、[online_data_rearrange.md](online_data_rearrange.md)（数据负载均衡），二者均挂在 MCORE 后端，可视为大规模分布式训练场景下的组合配套。
- **显存与 loss 优化**：[async_activation_offload.md](async_activation_offload.md)（双端通用 Offload）、[chunkloss.md](chunkloss.md)（FSDP2 专用）、[vlm_model_loss_calculate_type.md](vlm_model_loss_calculate_type.md)（双端 VLM loss）。
- **微调与数据/确定性**：[lora_finetune.md](lora_finetune.md)（MCORE 端 LoRA）、[lora_finetune_fsdp2.md](lora_finetune_fsdp2.md)（FSDP2 端 LoRA，二者对称）、[seqpack.md](seqpack.md)（FSDP2 专用数据处理）、[deterministic_computing.md](deterministic_computing.md)（双端通用）。

整体上，本文档是 MindSpeed MM 特性集合的**总目录页**，与各子特性文档形成一对多引用关系，同时向上承接 Ascend/MindSpeed 主仓的 tensor-parallel 实现。

---

## 【使用方法】

原文未涉及具体启用方式、配置项或命令。本文件作为特性列表/支持矩阵，仅提供 ✓/× 的能力声明；具体的开关、参数与启动命令需在各子特性文档（如 fsdp2.md、chunkloss.md、lora_finetune_fsdp2.md 等）中查阅。
