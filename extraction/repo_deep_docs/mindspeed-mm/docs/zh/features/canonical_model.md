# 标准等价模型

> 仓 `mindspeed-mm` · 路径 `docs/zh/features/canonical_model.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-mm/docs/zh/features/canonical_model.md

# 「标准等价模型 (Canonical Model)」深度解读

---

## 【定位】

这篇文档解决的问题是：**在 Megatron 分布式训练框架下, 由于其对模型模块(如 QKV、MLP)进行了融合与重排优化, 导致与 HuggingFace Transformers 标准实现在计算逻辑、参数排列和 LoRA 权重上存在不兼容, 造成跨框架模型迁移和 LoRA 微调困难。** 标准等价模型这一特性即为解决该差异而设计的"还原标准实现"模式。

---

## 【技术要点】

1. **三大设计目标**: 计算等价(同一输入下与 Transformers 原生输出数学一致, 允许浮点精度误差)、权重兼容(可直接与 Transformers 原生权重互相转换, 无需拆分/合并/重排)、LoRA 兼容(适配器权重在两框架间可直接通用)。

2. **核心机制——还原分层独立结构**: 在 Megatron 内取消 `linear_qkv`、`linear_fc1` 等融合层, 还原为 Transformers 标准的独立 `q_proj`/`k_proj`/`v_proj` 与 `gate_proj`/`up_proj`/`down_proj` 分层结构, 使 `hidden_states` 直接进入各独立线性层, 避免拆分-重排操作。

3. **关键差异点——QKV 计算**: Transformers 标准实现将 `hidden_states` 分别输入三个独立线性层; Megatron 实现则将三者融合为单层 `linear_qkv`, 输出后需拆分重排才能得到 q、k、v。

4. **关键差异点——MLP FC1 计算**: Megatron 将 `gate_proj` 和 `up_proj` 两层融合为 `linear_fc1` 单层, 与标准分层实现不一致, 影响权重跨框架转换。

5. **LoRA 参数规模差异**: 因融合操作, Megatron 下 qkv 层的 LoRA-A 矩阵参数量仅为标准实现的 **1/3**, 造成算法逻辑层面的不等价, 跨框架 LoRA 权重无法直接使用。

6. **当前支持范围**: 仅 `Qwen2.5-VL` 模型(文档明示); 更多模型的支持状态以文末 [特性列表](feature_list.md) 为准。

---

## 【关键机制与数据】

**工作原理:**

- **Attention QKV 路径对比**:
  - Transformers 路径: `hidden_states` → 独立 `q_proj` / `k_proj` / `v_proj` → 直接得到 q、k、v。
  - Megatron 路径: `hidden_states` → 融合 `linear_qkv` → 输出融合 qkv 张量 → 拆分 + 重排 → q、k、v。
  - 影响: 融合层的参数排列与标准不同; 前向计算结果可能存在微小数值差异; 权重转换需额外拆分/合并操作。

- **MLP FC1 路径对比**:
  - Transformers 路径: 独立 `gate_proj` 与 `up_proj` 两层。
  - Megatron 路径: 融合为单一 `linear_fc1` 层。
  - 影响: 融合层参数排列不同, 影响跨框架权重转换。

- **LoRA 场景差异路径**:
  - Megatron 下 qkv 层 LoRA-A 矩阵参数量 **仅为标准实现的 1/3**(原文明确数字)。
  - 后果: 微调精度受影响、跨框架 LoRA 权重不可直接使用、不同框架训练的 LoRA 效果可能存在差异。

- **性能权衡**(原文):
  - 启用 `canonical_model` 后, 模型结构与 Transformers 标准实现一致, 但**可能略微影响训练性能**;
  - 反之, Megatron 融合实现因融合算子**性能略优**, 在无跨框架需求时可不启用。

- **方案特点**(原文):
  - 保持与 Transformers 标准实现完全等价的计算逻辑;
  - 支持 LoRA 微调场景下的跨框架权重兼容;
  - **无需修改模型权重, 仅需在配置中启用**。

- **数据流图示**:
  - `sources/images/canonical_model/img.png` —— Megatron 下 QKV 计算实现差异示意图;
  - `sources/images/canonical_model/img_1.png` —— Megatron LoRA 场景下 QKV 计算实现差异示意图。

> 注: 原文未提供具体的训练吞吐/精度数值数据, 仅以"性能略优""可能略微影响训练性能"作定性描述。

---

## 【表格解读】

### 表 1: 三种模型实现对比(原文逐字还原)

| 维度 | 原生 HuggingFace 模型 | 标准等价模型(Canonical Model) | Megatron 融合模型(非标准等价) |
|------|----------------------|-------------------------------|-------------------------------|
| 运行框架 | Transformers(单卡/DDP) | Megatron(TP/PP/CP/DP 分布式) | Megatron(TP/PP/CP/DP 分布式) |
| 参数结构 | 分层独立(如 `q_proj`/`k_proj`/`v_proj`) | 分层独立, 与 HuggingFace 完全一致 | 融合层(如 `linear_qkv`), 参数经过重排 |
| 权重格式 | HuggingFace 标准格式 | HuggingFace 标准格式 | Megatron 融合格式, 需转换 |
| LoRA 兼容 | 原生支持 | 与 HuggingFace LoRA 权重完全兼容 | LoRA 参数规模不一致, 无法跨框架使用 |
| 训练性能 | 单卡性能有限 | 分布式训练, 性能接近融合模型 | 分布式训练, 融合算子性能略优 |
| 跨框架迁移 | — | 直接加载 HuggingFace 权重 | 需通过 mm-convert 转换 |

**逐行解读:**

- **运行框架行**: 原生 HuggingFace 仅支持单卡/DDP; 标准等价与 Megatron 融合模型都运行于 TP/PP/CP/DP 全套分布式并行, 表明标准等价模型并非性能阉割版, 而是分布式能力保留版。
- **参数结构行**: 核心差异 —— 标准等价模型"还原"为分层独立, 与 HuggingFace 完全一致; Megatron 融合模型则为 `linear_qkv` 等融合形态, 经重排。
- **权重格式行**: 标准等价模型使用 HuggingFace 标准格式, 这是其能"直接加载 HuggingFace 权重"的基础; Megatron 融合模型必须经 `mm-convert` 转换。
- **LoRA 兼容行**: 原生 HuggingFace 与标准等价模型 LoRA 完全兼容; Megatron 融合模型因参数规模(1/3 LoRA-A)不一致而无法跨框架使用 —— 这是该特性最重要的应用动机。
- **训练性能行**: 标准等价模型"性能接近融合模型", 即不显著牺牲速度, 但仍略低于纯融合模型; Megatron 融合模型因融合算子优化性能略优。
- **跨框架迁移行**: 标准等价模型可直接加载 HuggingFace 权重, 无需任何转换工具 —— 这是使用门槛上的关键优势。

### 表 2: canonical_model 配置项说明(原文逐字还原)

| 配置项 | 位置 | 说明 |
|--------|------|------|
| `canonical_model` | `vision_encoder` | 启用视觉编码器的标准等价实现 |
| `canonical_model` | `text_decoder` | 启用文本解码器的标准等价实现 |

**逐行解读:**

- **vision_encoder 行**: 在视觉编码器(Vision Transformer)子树中放置 `canonical_model` 开关, 用于启用 ViT 部分的标准等价实现, 可对图像编码路径生效。
- **text_decoder 行**: 在文本解码器(Language Model)子树中放置 `canonical_model` 开关, 启用 LLM 部分的标准等价实现, 对文本路径生效。
- **共同特征**: 两处均为布尔型开关(`true` 启用), 文档用法示例中均设为 `true`, 表明典型场景下视觉与文本两部分需同时启用, 而非局部启用。

---

## 【公式解读】

**原文无公式。**

> 文档全部以文字描述与示意图(`img.png`、`img_1.png`)呈现机制差异, 未给出任何 LaTeX 或伪代码形式的数学表达式。

---

## 【关联】

依据文末明确给出的内部链接 `feature_list.md`:

- **与 feature_list.md 的关系**: 文末注明"更多模型的标准等价支持正在开发中, 请关注 [特性列表](feature_list.md)"。即 `feature_list.md` 是该特性支持范围的**权威注册表**, 当前文档明确仅 `Qwen2.5-VL` 已支持, 其他多模态模型(Qwen-VL 系列其他成员、LLaVA、InternVL 等)是否纳入支持矩阵需查阅 feature_list.md 的最新状态。
- **与 mm-convert 转换工具的关联**: 文档在对比表中提及 Megatron 融合模型"需通过 mm-convert 转换", 说明仓库内还存在独立的权重转换工具 `mm-convert`, 标准等价模型可绕过该工具, 直接加载 HuggingFace 原生权重。
- **与 LoRA 微调特性上下游关系**: 文档将 LoRA 兼容性作为标准等价模型三大目标之一, 且在最佳实践中将 LoRA 微调列为"强烈建议启用", 表明该特性与仓库内的 LoRA 微调能力直接耦合, 两者需配合使用才能实现跨框架 LoRA 权重通用。
- **与 Megatron 分布式并行能力(TP/PP/CP/DP)的关系**: 标准等价模型运行于完整分布式并行栈之上, 说明其并未改变并行拓扑, 而是在并行框架内替换了融合算子的实现方式, 属于"算子级"而非"并行策略级"的改造。

---

## 【使用方法】

### 启用方式(原文给出)

在 `model_xxb.json` 中, 分别在 `vision_encoder` 与 `text_decoder` 子树添加 `"canonical_model": true`:

```json
{
  "model_id": "qwen2_5vl",
  "img_context_token_id": 151655,
  "vision_start_token_id": 151652,
  "image_encoder": {
    "vision_encoder": {
      "model_id": "qwen2vit",
      "canonical_model": true,
      ...
    },
  },
  ...
  "text_decoder": {
    "model_id": "qwen2lm",
    "canonical_model": true,
    ...
  }
}
```

### 配置项(原文给出)

| 配置项 | 位置 | 作用 |
|--------|------|------|
| `canonical_model` | `vision_encoder` | 启用视觉编码器的标准等价实现 |
| `canonical_model` | `text_decoder` | 启用文本解码器的标准等价实现 |

### 最佳实践(原文给出)

1. **LoRA 微调场景**: 强烈建议启用 `canonical_model`, 确保 LoRA 权重与 Transformers 标准实现兼容。
2. **跨框架迁移**: 如需在 Megatron 和 Transformers 之间切换训练, **必须**启用此特性。
3. **预训练场景**: 如无跨框架需求, 可不启用(Megatron 融合实现在性能上可能更优)。
4. **精度验证**: 启用后建议对比验证训练 loss 和模型输出是否与标准实现一致。

### 注意事项(原文给出)

- 启用 `canonical_model` 后, 模型结构将与 Transformers 标准实现一致, 但可能略微影响训练性能;
- 已有的非标准等价模型权重需要重新转换后才能与标准等价模式配合使用;
- 更多模型的标准等价支持正在开发中, 请关注 [特性列表](feature_list.md)。

### 命令行 / 环境变量 / 其他开关

原文未涉及任何命令行参数、环境变量或额外的开关命令, 全部启用方式均通过 JSON 配置中的 `canonical_model` 布尔字段完成。

## 图文联合解读

- `img.png`: **图文联合解读：**

1）图示对比 Transformers 与 Megatron 的 QKV 计算：左侧 Transformers 保持独立的 q_proj/k_proj/v_proj 三个分支；右侧 Megatron 将三者融合为 linear_qkv 并交织排列为 mixed_qkv，箭头标注 merge（合并）与 split（拆分）方向。

2）论证 Megatron 通过融合+交织重排提升性能，但破坏了参数的分层独立性，导致权重无法与 Transformers 直接互转。

3）支撑文档论点：正因为原生 Megatron 融合层结构不一致，才需要"标准等价模型"在 Megatron 内还原 Transformers 的独立分层结构，实现权重与 LoRA 跨框架兼容。
- `img_1.png`: ## 图文联合解读

**1) 图中内容**
左图为 Transformers 实现：hidden_states（n×d）经三个独立投影 `q_proj`(d×q)、`k_proj`(d×k)、`v_proj`(d×v)，每路各自配 LoRA 对（`*_loraA`+`*_loraB`），分别输出 q/k/v 后进入 attention。

右图为 Megatron 实现：相同输入送入融合层 `linear_qkv`(d×(q+k+v))，配单一 LoRA 对 `qkv_loraA`+`qkv_loraB`，得到 `mixed_qkv` 后再切分为 q/k/v。

**2) 技术结论**
Megatron 将三路 QKV 投影及其 LoRA 融合为单一矩阵，导致 LoRA 参数规模与排列与 Transformers 不一致，无法跨框架通用。

**3) 与文档论点的关系**
直观印证文档所述"Megatron 对核心模块做了融合及交织重排"，是 LoRA 不兼容与权重不能直通的根因，凸显标准等价模型拆分还原独立 q/k/v 的必要性。
