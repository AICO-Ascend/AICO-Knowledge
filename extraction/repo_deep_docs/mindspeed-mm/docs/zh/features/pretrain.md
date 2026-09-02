# 纯文本预训练

> 仓 `mindspeed-mm` · 路径 `docs/zh/features/pretrain.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-mm/docs/zh/features/pretrain.md

# 一体化深度解读：mindspeed-mm 纯文本预训练 (docs/zh/features/pretrain.md)

## 【定位】
本文档解决的是「在 mindspeed-mm 套件中如何为大语言模型（以 GPT 类自回归模型为代表）启用纯文本预训练流程」的问题，明确区分了**纯 FSDP2 后端**与**含 Megatron 后端**两种部署形态下预训练数据的差异配置，并给出关键参数（packing、cutoff_len）的取值含义。

## 【技术要点】

1. **双后端适配**：文档明确指出纯文本预训练支持「纯 FSDP2 后端」和「含 Megatron 后端」两类拓扑，二者**数据处理流程的配置项不同**，需按各自示例独立配置。
2. **FSDP2 后端配置入口**：在 `xx_config.yaml` 中通过 `basic_parameters.stage: pretrain` 触发预训练数据流；`attr` 下仅保留 `formatting: alpaca` 与 `prompt: text`，需注释/移除 SFT 场景的列映射配置以避免数据对齐失败；`collate_param` 设为 `collate_id: llm_pretrain`。
3. **Megatron 后端配置入口**：在 `data.json` 中通过 `attr` 内 `pretrain: true` 标记预训练模式（区别于 FSDP2 的 `stage` 字段），并用 `formatting: alpaca`、`prompt: text`，其余字段 (`system`/`images`/`videos`/`audios`/`query`/`response`/`history`) 显式置 `null`；`collate_param.model_name` 设为 `llm_pretrain`。
4. **packing 默认开启**：`basic_parameters.packing` 默认 `true`，将多个短文本样本拼接成 `cutoff_len` 长序列以提升显存利用率与训练效率；可显式设为 `false` 关闭。
5. **cutoff_len 长度上限**：FSDP2 后端下位于 `xx_config.yaml` 中的 `cutoff_len`；Megatron 后端下对应 `finetune_xx.sh` 中的 `SEQ_LEN`——同一参数在两套体系中通过不同字段名承载。
6. **数据样态**：原文给出三行 JSON 样例 `{"text": "..."}`，强调纯文本预训练数据无任务导向、无标注，仅含 `text` 字段。

## 【关键机制与数据】

- **自回归建模目标**（原文）："基于历史上下文预测下一个标记"——预训练通过反复优化这种预测能力，使模型学会语境理解、句子连贯性与更高层次语言结构，为下游任务提供通用语言表示。
- **数据流关键约束**：原文指出"packing 开启（默认）的场景下，数据预处理会在每个批次内拼接文本，并按 `cutoff_len` 切分为定长序列"。这是一个**隐含的硬约束**：每个预处理批次内**有效文本 token 总数 ≥ cutoff_len** 才能产出训练样本，否则该批次无样本可训。
- **批大小调优建议**（原文）：可通过「增大 `preprocessing_batch_size`」、「增加样本长度」、「减小 `cutoff_len`」三种手段解决批次内有效 token 不足问题。原文未给出推荐数值或性能基线数据。

## 【表格解读】

原文无表格。

## 【公式解读】

原文无公式。

## 【关联】

- **与 SFT 场景的关系**：原文 NOTE 反复提示「切换到预训练时，请将 `attr` 下原有的配置（如 SFT 场景的列映射配置）注释或移除」，说明 `attr` 配置在 SFT 与 Pretrain 之间是**互斥复用**关系，预训练要求仅保留 `formatting` 与 `prompt` 两项最小集。
- **统一格式协议**：两个后端均使用 `formatting: alpaca`，意味着尽管底层 collator 不同（`llm_pretrain` collator 在两侧复用同一命名），上层的 Alpaca 格式化模板保持一致。
- **Megatron 后端参数映射**：`SEQ_LEN` (shell 脚本) ↔ `cutoff_len` (yaml) 形成跨配置文件的同名异构关系，运维时需保持两端值一致。
- **文档自身结构关联**：本文档是 mindspeed-mm 多模态套件中"训练阶段"系列 feature 之一，与多模态理解/生成的微调（SFT）等文档构成训练流程闭环，但原文未提供内部超链接（"内部链接: (无)"）。

## 【使用方法】

原文已给出完整启用方式：

**FSDP2 后端**（`xx_config.yaml`）：
```yaml
data:
  dataset_param:
    attr:
      formatting: alpaca
      prompt: text
    basic_parameters:
      stage: pretrain
      template: default
  dataloader_param:
    collate_param:
      collator_id: llm_pretrain
```

**Megatron 后端**（`data.json`）：
```json
{
    "dataset_param": {
        "basic_parameters": {"template": "default"},
        "attr": {
            "formatting": "alpaca", "pretrain": true,
            "system": null, "images": null, "videos": null, "audios": null,
            "prompt": "text", "query": null, "response": null, "history": null
        }
    },
    "dataloader_param": {
        "collate_param": {"model_name": "llm_pretrain"}
    }
}
```

**关键参数对照**：

| 参数 | FSDP2 后端 | 含 Megatron 后端 | 取值/默认 |
|---|---|---|---|
| 数据阶段标记 | `basic_parameters.stage` | `attr.pretrain` | 必填 `pretrain` / `true` |
| collator | `collate_param.collator_id` | `collate_param.model_name` | 均设为 `llm_pretrain` |
| 序列拼接 | `basic_parameters.packing` | 同左 | 默认 `true`，可设 `false` |
| 最大序列长度 | `cutoff_len` (yaml) | `SEQ_LEN` (finetune_xx.sh) | 按模型与显存设定 |

**启用注意事项**：packing 默认开启时，必须保证每个 `preprocessing_batch_size` 批次内累计有效 token ≥ `cutoff_len`，否则该批次不会产出训练样本——可通过增大 `preprocessing_batch_size`、增大样本长度或减小 `cutoff_len` 三种方式规避。
