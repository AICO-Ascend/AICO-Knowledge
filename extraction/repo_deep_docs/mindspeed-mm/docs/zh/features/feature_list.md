# 特性列表

> 仓 `mindspeed-mm` · 路径 `docs/zh/features/feature_list.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-mm/docs/zh/features/feature_list.md

# 深度解读：mindspeed-mm 特性列表 (feature_list.md)

## 【定位】

本篇文档是 MindSpeed MM 商用版本特性的**索引型总览**，以分类表格的形式枚举套件当前已发布、可供用户启用的全部能力，覆盖并行策略、显存优化、训练优化、训练模式、训练范式、数据处理、模型转换、确定性计算与评估九大类别，共 31 项子特性，每项均通过相对链接（除 RLHF 外）指向独立的特性详细说明文档，作为整本用户手册的"导航目录"使用。

---

## 【技术要点】

1. **并行策略覆盖完整**：表格第一大类"并行特性"涵盖 10 项特性，覆盖数据/张量/流水/序列等多种并行维度，包括 FSDP2（完全分片数据并行 v2）、张量并行 (TP，链接指向 MindSpeed 主仓)、Virtual Pipeline Parallel (VPP)、动态 PP / Dynamic DPCP、异构并行 (Hetero Parallel)、自动并行 (Automatic Parallelism)，以及面向 DiT 架构的 Unaligned Ulysses CP / DiT Ring Attention / DiT USP / Unaligned Sequence Parallel。
2. **显存优化与负载均衡**：第二大类包含 4 项：Async Activation Offload（异步激活卸载）、Online Data Rearrange（在线数据重排）、Encoder DP Balance（编码器数据并行均衡）、Bucket Reordering（梯度桶重排），分别从 offload、负载均衡、通信调度三个角度缓解显存/吞吐瓶颈。
3. **优化特性分两类**：(a) **损失优化**——Chunk Loss（分块损失）、VLM Model Loss Calculate Type（视觉语言模型损失计算类型）；(b) **性能优化**——FPDT、Dummy Optimizer、Parameter LR/WD Tuning（参数级学习率/权重衰减调优）。
4. **训练模式 5 项 + 训练范式 1 项**：包含预训练 (Pretrain)、LoRA Finetune、LoRA Finetune with FSDP2、Agentic SFT（智能体监督微调）、Layerwise Disaggregated Training（分层解耦训练），以及 RLHF（强化学习人类反馈，链接为空)。
5. **数据 / 模型 / 确定性 / 评估支持**：Multimodal Dataset（多模态数据集）与 SeqPack（序列打包）构成数据处理子模块；MM Convert 与 Canonical Model 提供模型转换能力；Deterministic Computing 保证位级一致；VBench Evaluate 提供视频生成质量评测。
6. **目录结构隐含的工程依赖**：特性分类颗粒度（"特性大类 → 特性子类 → 特性名称"三层）暗示上游算法 → 下游并行/显存/优化 → 应用模式的分层抽象，便于按需组合。

---

## 【关键机制与数据】

本文档为索引型总览，**原文未提供任何具体的工作原理、数据流图、性能数据或训练吞吐指标**。表格仅以"特性名称 + 相对链接"形式呈现，每条链接指向独立的特性文档以承载机制描述。
- 原文出现的关键术语：FSDP2、DPCP（Dynamic Pipeline Parallel Communication Pattern，原文未展开定义）、VPP、Ulysses CP、Ring Attention、USP（Unified Sequence Parallel）、Hetero Parallel、Automatic Parallelism、Chunk Loss、FPDT、Dummy Optimizer、Agentic SFT、Layerwise Disaggregated Training、SeqPack、Canonical Model——这些均为链接锚点，原文未展开其实现细节。
- 原文无数据流描述、无伪代码、无性能基准数字。

---

## 【表格解读】

原文包含一张主表格（HTML 表格），列宽分别约 167/158/187 px，按"特性大类 / 特性子类 / 特性名称"三列组织，并大量使用 `rowspan` 合并单元格以呈现子类归属。下面用 markdown 表格逐字还原（保持合并语义）：

| 特性大类 | 特性子类 | 特性名称 |
| --- | --- | --- |
| 并行特性 | FSDP2 | [FSDP2](fsdp2.md) |
| 并行特性 | PP 并行 | [动态 PP / Dynamic DPCP](dynamic_dpcp.md) |
| 并行特性 | PP 并行 | [Virtual Pipeline Parallel](virtual_pipeline_parallel.md) |
| 并行特性 | 序列并行 | [Unaligned Ulysses CP](unaligned_ulysses_cp.md) |
| 并行特性 | 序列并行 | [DiT Ring Attention](dit_ring_attention.md) |
| 并行特性 | 序列并行 | [DiT USP](dit_usp.md) |
| 并行特性 | 序列并行 | [Unaligned Sequence Parallel](unaligned_sequence_parallel.md) |
| 并行特性 | 异构并行 | [Hetero Parallel](hetero_parallel.md) |
| 并行特性 | 自动并行 | [Automatic Parallelism](automatic_parallelism_mm.md) |
| 并行特性 | 张量并行 | [tensor-parallel](https://gitcode.com/Ascend/MindSpeed/blob/master/docs/zh/features/tensor-parallel.md) |
| 显存优化 | Offload | [Async Activation Offload](async_activation_offload.md) |
| 显存优化 | 负载均衡 | [Online Data Rearrange](online_data_rearrange.md) |
| 显存优化 | 负载均衡 | [Encoder DP Balance](encoder_dp_balance.md) |
| 显存优化 | Bucket Reordering | [Bucket Reordering](bucket_reordering.md) |
| 优化特性 | 损失优化 | [Chunk Loss](chunkloss.md) |
| 优化特性 | 损失优化 | [VLM Model Loss Calculate Type](vlm_model_loss_calculate_type.md) |
| 优化特性 | 性能优化 | [FPDT](fpdt.md) |
| 优化特性 | 性能优化 | [Dummy Optimizer](dummy_optimizer.md) |
| 优化特性 | 性能优化 | [Parameter LR/WD Tuning](parameter_lr_wd_tuning.md) |
| 训练模式 | 预训练 | [Pretrain](pretrain.md) |
| 训练模式 | 高效微调 | [LoRA Finetune](lora_finetune.md) |
| 训练模式 | 高效微调 | [LoRA Finetune with FSDP2](lora_finetune_fsdp2.md) |
| 训练模式 | 高效微调 | [Agentic SFT](agentic_sft.md) |
| 训练模式 | Layerwise Training | [Layerwise Disaggregated Training](layerwise_disaggregated_training.md) |
| 训练范式 | RL | [RLHF]() *(链接为空)* |
| 数据处理 | 数据集 | [Multimodal Dataset](multimodal_dataset.md) |
| 数据处理 | SeqPack | [SeqPack](seqpack.md) |
| 模型转换 | 模型转换 | [MM Convert](mm_convert.md) |
| 模型转换 | Canonical Model | [Canonical Model](canonical_model.md) |
| 确定性计算 | Deterministic | [Deterministic Computing](deterministic_computing.md) |
| 评估工具 | VBench | [VBench Evaluate](vbench-evaluate.md) |

**逐行/逐簇解读**：

- **并行特性（共10条）**：其中 PP 并行 2 条（动态 DPCP + VPP）、序列并行 4 条（Ulysses / Ring Attention / USP 三个变体 + Unaligned SP）占主导，反映 MindSpeed MM 在多模态生成场景（典型为 DiT 架构、长序列）上对序列维度并行的投入；FSDP2、异构并行、自动并行、张量并行则补充通用扩展能力，张量并行一项以**外链**指向 MindSpeed 主仓，提示该能力由主仓继承而非本仓独立实现。
- **显存优化（4 条）**：以 Async Activation Offload 为代表的异步卸载，与 Encoder DP Balance（编码器端 DP 均衡）和 Online Data Rearrange（在线重排）共同构成"显存压力 → 数据/调度缓解"组合，Bucket Reordering 单独成子类，强调其作为通信调度原语的独立地位。
- **优化特性（5 条）**：损失侧 2 条（Chunk Loss + VLM 专用损失类型）解决多模态/长序列梯度计算问题；性能侧 3 条（FPDT、Dummy Optimizer、Parameter LR/WD Tuning）属于显存/优化器状态/调度微调类工程技巧。
- **训练模式（5 条）**：覆盖从全量预训练到 LoRA 高效微调（含 FSDP2 变体）、再到面向智能体的 Agentic SFT 与 Layerwise Disaggregated Training，体现"全量—参数高效—解耦分层"的渐进训练栈。
- **训练范式（1 条）**：RLHF 链接为空（`href=""`），原文保留条目但未挂接文档，暗示该能力尚在规划/未公开发布阶段。
- **数据处理（2 条）**：Multimodal Dataset（数据接入）+ SeqPack（序列打包以提升吞吐），是与多模态生成强相关的两条管线。
- **模型转换（2 条）**：MM Convert 提供工程级权重/格式转换；Canonical Model 提供规范化模型表达。
- **确定性计算（1 条）**：Deterministic Computing 单独成大类，强调可复现性，与训练模式并行排列。
- **评估工具（1 条）**：仅 VBench Evaluate，对应视频生成质量评估，契合多模态生成场景。

整张表格共计 **31 条**特性条目（其中 RLHF 链接为空，剩余 30 条指向具体文档），且与正文宣称的"商用版本中已发布的特性"互为对照——RLHF 链接缺失可能表示该条目尚未正式发布。

---

## 【公式解读】

原文无公式（无 LaTeX、无伪代码、无数学表达式），仅含一段 HTML/CSS 样式定义和一张 HTML 表格。

---

## 【关联】

由于本文档是索引总览，"关联"主要体现在**跨大类、跨特性子类的组合使用模式**以及**与外部文档的链接关系**：

1. **并行 ↔ 显存优化的耦合**：FSDP2（并行特性）与 LoRA Finetune with FSDP2（训练模式）通过相同 FSDP2 技术串联；Bucket Reordering（显存优化）和 FPDT（优化特性）通常作为大规模分布式训练通信栈的组成部分，与 FSDP2/Pipeline Parallel 协同使用。
2. **DiT 系列并行 ↔ 多模态数据 ↔ 视频评估**：DiT Ring Attention / DiT USP / Unaligned Ulysses CP（并行特性）面向扩散 Transformer（DiT），与 Multimodal Dataset、SeqPack（数据处理）共同支撑视频/图像生成训练，最终通过 VBench Evaluate（评估工具）完成端到端评估链路。
3. **训练模式 ↔ 训练范式**：Pretrain → LoRA Finetune / Agentic SFT → RLHF（训练范式）形成"基础预训练—监督微调—强化学习"的级联范式；RLHF 链接为空意味着该级联末端当前未在文档中闭环。
4. **模型转换 ↔ 上游权重 ↔ 评估**：MM Convert 与 Canonical Model（模型转换）常作为模型接入 MindSpeed MM 训练框架的前置步骤，与下游的 Pretrain / LoRA / 评估管线衔接。
5. **确定性计算 ↔ 训练模式**：Deterministic Computing 与各类训练模式（Pretrain / LoRA / Layerwise Training）正交叠加，用于复现训练。
6. **外部链接**：tensor-parallel 一项指向 MindSpeed 主仓 `https://gitcode.com/Ascend/MindSpeed/blob/master/docs/zh/features/tensor-parallel.md`，是本仓与主仓**特性复用**的唯一显式跨仓依赖。

---

## 【使用方法】

本文档作为索引，**原文未涉及任何具体的启用方式、配置项或命令行**。所有具体使用方法（如环境变量、参数开关、启动命令）需跳转至各特性链接指向的独立特性文档获取，例如：

- 启用 FSDP2 → 参见 `fsdp2.md`（原文未给出）。
- 启用 LoRA Finetune → 参见 `lora_finetune.md`（原文未给出）。
- 启用 RLHF → 原文链接为空，**无法从本文档获取使用方式**。

如需获取特性启用细节，请按本表中的相对链接逐项查阅对应特性文档。
