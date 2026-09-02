# QAD 量化感知蒸馏

> 仓 `mindspeed` · 路径 `docs/zh/features/qad.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed/docs/zh/features/qad.md

# QAD 量化感知蒸馏 —— 一体化深度解读

---

## 【定位】

本文档描述了 mindspeed 昇腾大模型加速库中 **QAD（Quantization-Aware Distillation，量化感知蒸馏）** 特性：针对大语言模型量化到 4-bit（MXFP4/NVFP4）后精度显著退化、且传统 QAT 交叉熵训练会破坏输出分布（对 RL 训练模型影响严重）的问题，提供一套基于 BF16 全精度教师模型 + KL 散度损失的蒸馏式低精度训练方案。

---

## 【技术要点】

1. **核心范式**：BF16 全精度教师模型（固定参数、不可训练）作为稳定目标分布源，引导 MXFP4 W4A4 量化感知训练的学生模型，二者通过 KL 散度损失对齐 logits 分布。
2. **损失函数**：仅使用 KL 散度损失 `L_total = α · KL(p_teacher ‖ p_student)`；交叉熵（CE）损失仅用于日志监控，**不参与梯度计算**，从而忠实保留原始分布，避免传统 QAT 改变输出分布的副作用。
3. **关键超参**：KL 损失权重 α 默认 1.0，温度参数 T 默认 1.0；KL 损失归约方式默认为 `"mean"`（亦支持 `"sum"`）。
4. **使用限制（启用时会强制参数校验，不满足即报错终止）**：
   - **仅支持 Dense 模型**：不支持 MoE；启用 QAD 时若设置 `--num-experts` 会报错。
   - **不支持流水线并行**：要求 `--pipeline-model-parallel-size 1`；KL 损失计算需要每个 rank 上有完整 logits，而 PP 会把层划分到不同 stage，仅最后一个 stage 产生 logits，且批次缓存重放逻辑假设每个 micro-batch 单次前向，与 PP 多 stage 调度冲突。
5. **核心代码组件**（5 个）：`QADConfig`（配置数据类）、`TeacherModelManager`（教师模型生命周期管理）、`LogitsKLLoss`（KL 散度损失计算）、`QADQuantEngineFeature`（特性注册与参数校验）、`QADForwardStepPatch`（训练流水线补丁）。
6. **典型训练配置示例**：`--tensor-model-parallel-size 8` 配合 `--pipeline-model-parallel-size 1`，体现 TP>1、PP=1 的并行拓扑要求。

---

## 【关键机制与数据】

- **工作原理**：教师-学生双模型结构。教师模型为 BF16 全精度且参数冻结，提供稳定目标分布 `p_teacher`；学生模型为 MXFP4 W4A4 量化感知训练且可微调，产生分布 `p_student`。训练时通过 KL 散度损失将学生 logits 向教师 logits 对齐，梯度只更新学生模型。
- **数据流**：教师与学生共享输入 → 各自前向得到 logits → `LogitsKLLoss` 计算 KL 散度 → 加权求和（α=1.0 默认）得到总损失 → 反向传播仅作用于学生模型。
- **温度与权重**：温度 T=1.0、KL 损失权重 α=1.0、归约方式 `"mean"`（原文给出的默认值）。
- **并行拓扑约束**：TP=8、PP=1 为示例配置（原文示例），PP 必须为 1。
- **关于 RL 训练的特别说明**（原文）：传统 QAT 改变输出分布，对 RL 训练模型影响严重；QAD 通过 KL 蒸馏保留原始分布，缓解此问题（原文定性描述，无具体数据）。
- **原文未涉及**：未给出性能数据、加速比、精度恢复具体数字、未给出支持的模型规模/参数量等。

---

## 【表格解读】

### 表格 1：核心组件

| 组件 | 路径 | 说明 |
|------|------|------|
| QADConfig | `mindspeed/core/distill/config.py` | 配置数据类 |
| TeacherModelManager | `mindspeed/core/distill/teacher_model_manager.py` | 教师模型生命周期管理 |
| LogitsKLLoss | `mindspeed/core/distill/logits_kl_loss.py` | KL 散度损失计算 |
| QADQuantEngineFeature | `mindspeed/features_manager/qad/qad_quant_engine.py` | 特性注册与参数校验 |
| QADForwardStepPatch | `mindspeed/core/distill/qad_adapter.py` | 训练流水线补丁 |

**逐行解读**：

- `QADConfig`：位于 `distill/config.py`，负责统一管理 QAD 相关参数（如 `--qad-enable`、`--qad-teacher-load`、`--kl-temperature`、`--kl-loss-weight`、`--kl-loss-reduction`）的解析与封装，是特性配置入口。
- `TeacherModelManager`：位于 `distill/teacher_model_manager.py`，负责 BF16 教师模型加载、初始化与生命周期管理；教师参数固定，需要在训练前从指定 checkpoint 加载（由 `--qad-teacher-load` 指定）。
- `LogitsKLLoss`：位于 `distill/logits_kl_loss.py`，实现 KL 散度损失的计算模块，支持温度参数与归约方式（mean/sum）。
- `QADQuantEngineFeature`：位于 `features_manager/qad/qad_quant_engine.py`，承担特性注册与**参数校验**职责——这与文档"使用限制"小节中提到的"启用时会进行参数校验，不满足条件将报错终止"对应。
- `QADForwardStepPatch`：位于 `distill/qad_adapter.py`，作为训练流水线补丁介入 forward step 流程，串接教师-学生前向与 KL 损失计算。

### 表格 2：使用限制

| 限制项 | 说明 |
|--------|------|
| **仅支持 Dense 模型** | 不支持 MoE（Mixture of Experts）模型。教师与学生前向路径假设单一 GPTModel logits 输出，MoE 路由拓扑不满足此假设。启用 QAD 时若设置了 `--num-experts` 将报错。 |
| **不支持流水线并行（PP）** | 不支持 `pipeline-model-parallel-size > 1`。KL 损失计算要求每个 rank 上有完整 logits，但 PP 将层划分到不同 stage，仅最后一个 stage 产生 logits。此外，批次缓存重放逻辑假设每个 micro-batch 单次前向，与 PP 多 stage 调度冲突。请设置 `--pipeline-model-parallel-size 1`。 |

**逐行解读**：

- **仅支持 Dense 模型**：架构层面硬性约束。原因有两层：(1) QAD 假设教师与学生均为单一 GPTModel logits 输出；(2) MoE 的路由拓扑会破坏该假设——即 logits 来源不是单一路径，KL 对齐前提不成立。启用 QAD 时若传入 `--num-experts` 会触发 `QADQuantEngineFeature` 的校验报错。
- **不支持 PP>1**：并行拓扑层面硬性约束。原因有三层：(1) KL 损失需要在每个 rank 上有完整 logits；(2) PP 会把 Transformer 层切分到不同 stage，仅最后 stage 输出 logits，其他 rank 没有 logits 参与 KL 计算；(3) 内部还存在"批次缓存重放"逻辑——假设每个 micro-batch 单次前向，而 PP 的多 stage 调度会触发多次前向，与此假设冲突。强制要求 `--pipeline-model-parallel-size 1`。

### 表格 3：参数说明

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--qad-enable` | False | 启用 QAD |
| `--qad-teacher-load` | "" | 教师模型检查点路径（启用时必填） |
| `--kl-temperature` | 1.0 | KL 散度温度参数 |
| `--kl-loss-weight` | 1.0 | KL 损失权重 α |
| `--kl-loss-reduction` | "mean" | KL 损失归约方式（mean/sum） |

**逐行解读**：

- `--qad-enable`：布尔开关，默认 `False`；设为 True 才进入 QAD 路径。
- `--qad-teacher-load`：字符串路径，默认空串；启用 QAD 后该字段成为必填项，由 `TeacherModelManager` 据此加载 BF16 教师模型 checkpoint。
- `--kl-temperature`：浮点数，默认 `1.0`；用于控制 KL 散度计算中的 logits 缩放（温度 T）。
- `--kl-loss-weight`：浮点数，默认 `1.0`；即损失公式中的权重系数 α。
- `--kl-loss-reduction`：字符串，默认 `"mean"`；KL 损失的归约方式，可选 `"sum"`，与 PyTorch 常见 loss 归约语义一致。

---

## 【公式解读】

原文给出 1 个损失公式（文字伪代码形式）：

```text
L_total = α · KL(p_teacher ‖ p_student)
```

**符号含义**：

- `L_total`：总训练损失，是反向传播的唯一来源（因 CE 损失不参与梯度计算）。
- `α`：KL 损失权重，对应命令行参数 `--kl-loss-weight`，默认 `1.0`。
- `KL(· ‖ ·)`：KL 散度（Kullback-Leibler divergence）算子；`p_teacher ‖ p_student` 表示以教师分布为参考、衡量学生分布相对偏离程度的方向性度量。
- `p_teacher`：BF16 全精度教师模型的输出概率分布，由冻结参数的教师模型前向产生，提供"稳定目标分布"。
- `p_student`：MXFP4 W4A4 量化感知训练学生模型的输出概率分布，是被优化对象。

**作用**：该公式将原本的多目标优化（CE + 量化）简化为"以教师 logits 为软标签的 KL 蒸馏"，避开了交叉熵对输出分布的扰动，从而在保留 RL 训练兼容性的同时，实现低精度量化下的精度恢复。

文档同时声明**温度参数 T=1**（即 `--kl-temperature 1.0`）以及 **CE 损失仅用于日志监控，不参与梯度计算**——这两个设定是上述公式成立的前提条件。

---

## 【关联】

原文未提供内部链接，但根据文档内容可识别以下关联关系：

- **量化方案**：与 MXFP4 / NVFP4（4-bit 量化格式）直接耦合；学生模型训练模式为 **W4A4（Weight 4-bit、Activation 4-bit）量化感知训练**，这意味着 QAD 依赖底层量化引擎（昇腾上 MXFP4/NVFP4 的实现）。
- **训练流水线**：通过 `QADForwardStepPatch`（`mindspeed/core/distill/qad_adapter.py`）介入 `pretrain_gpt.py` 训练流水线，因此与 mindspeed 的 GPT 训练入口/forward step 框架紧耦合。
- **模型架构限制**：依赖单一 GPTModel logits 输出假设，因此与 **MoE 路由模块不兼容**；若使用 MoE 路径则需绕开 QAD。
- **并行拓扑**：与 **张量并行（TP）兼容**（示例中 TP=8），但与 **流水线并行（PP）互斥**（必须 PP=1）。
- **特性注册机制**：通过 `QADQuantEngineFeature` 走 mindspeed 的 features_manager 注册/校验链路，与库内其他 feature（如其他量化引擎 feature）的启用方式一致。

---

## 【使用方法】

### 启用命令（原文示例，逐字保留）

```bash
python pretrain_gpt.py \
    --qad-enable \
    --qad-teacher-load /path/to/bf16_teacher_checkpoint \
    --kl-temperature 1.0 \
    --kl-loss-weight 1.0 \
    --tensor-model-parallel-size 8 \
    --pipeline-model-parallel-size 1 \
    ... (其他标准训练参数)
```

### 关键配置项（原文参数表汇总）

| 类别 | 配置 |
|------|------|
| 启用开关 | `--qad-enable`（默认 `False`，设为 True） |
| 教师模型 | `--qad-teacher-load /path/to/bf16_teacher_checkpoint`（启用时**必填**，默认空串） |
| KL 温度 | `--kl-temperature 1.0`（默认 1.0） |
| KL 权重 | `--kl-loss-weight 1.0`（即 α，默认 1.0） |
| KL 归约 | `--kl-loss-reduction "mean"`（默认 `"mean"`，可填 `"sum"`） |
| 并行拓扑 | `--tensor-model-parallel-size 8`、`--pipeline-model-parallel-size 1`（**PP 必须为 1**） |
| 模型类型 | Dense 模型（**禁用 MoE**，启用 QAD 时设置 `--num-experts` 会报错） |

> 原文未涉及：未给出 BF16 教师模型的具体模型规格（如参数量、是否与学生同构）、未给出推荐数据集/批次大小/学习率、未给出断点续训/恢复时的特殊说明、未给出与 RL 训练 pipeline 的具体对接步骤。
