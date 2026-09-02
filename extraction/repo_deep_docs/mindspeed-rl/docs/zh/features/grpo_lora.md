# GRPO-LoRA

> 仓 `mindspeed-rl` · 路径 `docs/zh/features/grpo_lora.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-rl/docs/zh/features/grpo_lora.md

# GRPO-LoRA 文档深度解读

---

## 【定位】

这篇文档描述的是 mindspeed-rl 中 **GRPO-LoRA** 特性——一种将组相对策略优化（GRPO）与低秩适应（LoRA）结合的大模型对齐训练方案，旨在解决大模型 RLHF/对齐训练中显存与通信开销高昂的痛点，同时满足部署侧"单基座多业务（multi-LoRA）"推理的实际需求。

---

## 【技术要点】

1. **LoRA 参数配置**：`lora_r=128`（低秩维度，一般取 32/64/128）、`lora_alpha=128`（缩放系数，一般为 `lora_r` 的 1 或 2 倍）。当 r=128 时训练曲线与全参数微调基本一致。
2. **目标模块范围**：`lora_target_modules: ["linear_qkv", "linear_proj", "linear_fc1", "linear_fc1", "linear_fc2"]`（即 attention 的 QKV/Proj 与 MLP 的 FC1/FC2）。
3. **CCLoRA 通信掩盖**：通过 `lora_fusion: true` 启用 CCLoRA 算法，利用计算与通信掩盖提升性能。
4. **LoRA 权重按需保存**：`lora_filter: true`——只保存 LoRA Adapter 参数，避免每次 checkpoint 都保存巨大 Backbone。
5. **Share Backbone**：`share_backbone: True`——Actor 与 Reference Model 共享同一份 Backbone 权重，避免重复加载开销。原文特别强调该机制**仅支持 Integrated Worker 架构**，对 DAPO 这类天然无需 Reference 的算法会在初始化阶段阻断。
6. **vLLM 权重动态转换**：进入 Rollout 前自动识别训练 TP/PP 与 vLLM TP/PP 的差异，重新切分 LoRA 权重并 `add` 到 Backbone 后再加载推理——既规避 vLLM 对 LoRA 算子的额外开销，又不侵入 vLLM 源码。

---

## 【关键机制与数据】

### 工作原理

**LoRA 模块构造**（原文：）
> "模型在 `get_model_provider` 阶段通过构造 MindSpeed LLM 框架内置的 LoRA 模块完成初始化。"

即 LoRA Adapter 的注入是在模型 provider 阶段完成的，继承自 MindSpeed-LLM 框架。

**Share Backbone 三层机制**（原文：）
1. **逻辑复用代替物理拷贝**：Actor 与 Reference 共享同一份 Backbone 权重，省去重复加载大型权重的装卸时间。
2. **动态上下文切换**：Actor 前向正常累加 LoRA Adapter 输出；Reference 前向通过 `with self.model.disable_adapter()` 上下文管理器临时屏蔽 LoRA 分支，仅计算 Backbone 输出。
3. **适用范围约束**：仅支持 Integrated Worker 架构；DAPO 等无需 Reference 的算法会被系统阻断。

**vLLM 推理集成两步**（原文：）
1. **权重转换**：系统自动识别训练 TP/PP 与 vLLM TP/PP 差异，将分布在不同节点上的 LoRA 权重按 Rollout 分布式结构重新切分重组。
2. **合并与推理**：将转换后的 LoRA 权重 **add** 到对应 Backbone 权重中，vLLM 直接加载合并后的完整模型——既规避 vLLM 对 LoRA 算子的额外开销，又保证推理引擎纯净性与升级兼容性。

### 资源效率数据（原文：）
> "对于 qwen2.5-32b，使用 4k 上下文训练数据，仅需 16x 32GB NPUs 即可稳定训练。"

### 效果对齐数据（原文：）
> "在 DeepScaler 数据集上进行验证，当 LoRA Rank 设置为 128 时，GRPO-LoRA 在 Reward 增长趋势和 Loss 收敛曲线上与全参数微调（Full Fine-tuning）基本保持一致。"

---

## 【表格解读】

原文"对照试验基本配置"表格（逐字还原）：

| | 硬件配置 | 学习率 | gbs | n_sample | mbs | lora_alpha | lora_r |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **全参数** | 32x 32GB NPUs | 2e-6 | 32 | 8 | 32 | 不涉及 | 不涉及 |
| **lora** | 16x 32GB NPUs | 3e-5 | 32 | 8 | 32 | 128 | 128 |

**逐行解读：**

- **全参数行**：32x 32GB NPUs 硬件配置，学习率 2e-6，global batch size=32，每个 prompt 采样数 n_sample=8，micro batch size=32，lora_alpha 与 lora_r 均为"不涉及"（因为是全参数微调）。

- **lora 行**：硬件直接**减半**为 16x 32GB NPUs，学习率上调一个数量级至 3e-6（注意原文就是 3e-5），gbs/n_sample/mbs 与全参数保持一致（32/8/32），lora_alpha=128、lora_r=128（即 α/r=1，符合文档"一般为 1 或 2 倍"的建议下限）。

**表格传递的核心信息**：在 batch 配置完全一致的前提下，LoRA 方案以**一半的硬件资源**（16 vs 32 卡）达到了与全参数微调可比的训练效果——这是 GRPO-LoRA 价值主张的关键定量支撑。

---

## 【公式解读】

**原文无公式**。

文档中未出现任何 LaTeX 公式或伪代码表达式。LoRA 的核心数学形式（$W' = W + \frac{\alpha}{r} B A$）未在原文中显式写出，因此不做引申。

---

## 【关联】

### 上游依赖（基础能力来源）
- **MindSpeed-LLM 框架**：`get_model_provider` 阶段的内置 LoRA 模块构造继承自 MindSpeed-LLM。原文给出官方文档链接：`https://gitcode.com/Ascend/MindSpeed-LLM/blob/master/docs/zh/pytorch/training/finetune/mcore/lora_finetune.md`，涉及低秩矩阵分解原理、权重转换（mg2hf）脚本等更基础的细节。
- **Integrated Worker 架构**：`share_backbone` 机制的前提条件。

### 下游配套（验证与配置）
- **配置文件**：`../../../configs/grpo_lora_qwen25_32b_A2.yaml`——文末指向的具体 yaml 配置文件，是启用该特性的实操入口。
- **训练数据**：DeepScaler 数据集——效果对齐验证的基准数据集。

### 横向对比（适用/不适用算法）
- **适用的算法范式**：需要 Reference Model 的 RL 算法（如标准 GRPO）。
- **不适用的算法**：DAPO——因其天然无需 Reference Model，Share Backbone 机制会在初始化阶段被系统阻断，原文未给出 DAPO 使用 LoRA 的细节。

### 推理侧关联
- **vLLM 引擎**：Rollout 阶段的推理引擎；通过权重 add-merge 方式保持 vLLM 纯净，避免侵入其源码，保证升级兼容性。

---

## 【使用方法】

### 启用配置（原文 YAML 块完整保留）

```yaml
megatron_config:
  lora_r: 128       # LoRA rank，表示低秩矩阵的维度，该值越大表示可学习的参数越多，一般为32，64，128
  lora_alpha: 128      # LoRA 的缩放系数，表示低秩矩阵对主干的影响，一般为lora_r的1或2倍
  lora_fusion: true     # 是否启用CCLoRA算法，该算法通过计算通信掩盖提高性能
  lora_target_modules: ["linear_qkv", "linear_proj", "linear_fc1", "linear_fc2"] # 选择需要添加 LoRA 的模块
  lora_filter: true    # 是否只保存LoRA模块

rl_config:
  share_backbone: True       # 是否开启 Actor 与 Reference 模型共享主干
```

### 推荐起步配置（原文："资源效率"章节）
- **模型**：qwen2.5-32b
- **上下文**：4k 训练数据
- **硬件**：16x 32GB NPUs
- **数据格式与启动命令**：原文未涉及（指向外部 yaml 配置文件 `grpo_lora_qwen25_32b_A2.yaml`），需结合该 yaml 与 mindspeed-rl 通用启动流程使用。
