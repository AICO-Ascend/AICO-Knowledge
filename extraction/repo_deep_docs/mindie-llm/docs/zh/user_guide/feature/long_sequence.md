# 长序列

> 仓 `mindie-llm` · 路径 `docs/zh/user_guide/feature/long_sequence.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-llm/docs/zh/user_guide/feature/long_sequence.md

# 长序列 (Long Sequence) Feature 文档深度解读

---

## 【定位】

这篇文档描述 MindIE LLM 推理引擎在**超长文本输入场景**（超过 32K、可至 1M 级别）下，通过 KV Cache 优化与序列外推算法（NTK/YaRN 等），同时保障模型回答效果与推理性能的能力，并给出**纯模型推理**与**服务化推理**两类部署的使能方法。

---

## 【技术要点】

1. **长序列定义与核心挑战**：序列长度超过 32K 乃至达到 1M 级别时，Attention 与 KV Cache 的显存消耗呈快速倍增增长，因此 KV Cache 量化、KV 多头压缩、训短推长（NTK/YaRN）等是关键技术。
2. **两种训练-推理范式**：
   - **训长推长**：以长文本训练模型权重，使模型在推理阶段天然支持长序列（如 Glm-4-9B-Chat-1M）。
   - **训短推长**：基于 ALiBi、NTK、YaRN 等位置编码或序列压缩算法，使短序列训练模型获得长序列自扩张能力。
3. **原生仅支持短序列的模型无法保证长序列结果合理性**：若模型本身不具备训长推长或训短推长能力，MindIE LLM 不保证其长序列输出的合理性。
4. **NTK / YaRN 已实现的模型范围**：
   - 支持 NTK：Llama3
   - 支持 YaRN：底层运行 Qwen2 modeling 的模型（Qwen2、Qwen2.5、Qwen3）
5. **模型权重侧使能方式（以 Qwen2.5-72B-Instruct 为例）**：在 `config.json` 增加 `rope_scaling` 字段，`factor=4.0`、`original_max_position_embeddings=32768`、`type=yarn`。部分模型（如 LLaMA3.1-70B-Instruct）无需修改即可使能。
6. **服务化配置关键参数（Batch=1、输入 127K、输出 1K 示例）**：`maxInputTokenLen=130048`、`maxSeqLen=131072`、`maxBatchSize=1`、`maxIterTimes=1024`、`maxPrefillBatchSize=1`、`maxPrefillTokens=130048`。

---

## 【关键机制与数据】

### 工作原理

长序列能力的实现路径分为两条：

- **权重内禀型**：训长推长模型（如 Glm-4-9B-Chat-1M）的位置编码 / RoPE 等已针对长序列训练，MindIE LLM 在该路径下保证与开源一致的长序列推理效果。
- **运行时外推型**：训短推长模型通过在推理时启用 NTK / YaRN 等 RoPE scaling 技术，动态扩展可处理的位置范围。Qwen2.5-72B-Instruct 的 `rope_scaling` 配置即为该机制的典型使能点（`factor=4.0` 将 `original_max_position_embeddings=32768` 放大到 4 倍）。

### 显存瓶颈与硬件约束（原文数据）

- **原文**：64G Atlas 800I A2 推理服务器，8 卡运行 Glm4-9B-Chat 模型，**在显存允许的条件下能进行最长 1M 的长序列推理**。
- **原文**：长序列特性受限于两类因素——(1) 硬件显存规格与模型参数量；(2) 模型权重和结构本身对长序列能力的支持。

### 输入执行方式（原文命令）

```bash
cd ${ATB_SPEED_HOME_PATH}
torchrun --nproc_per_node [运行卡数] --master_port 20030 \
  -m examples.run_pa --model_path [模型权重路径] \
  --max_output_length [最大输出长度] \
  --max_input_length [最大输入长度] \
  --input_texts [输入文本，可支持文件或字符串]
```

> 原文建议长序列推理使用 `*.txt` 文本文件作为输入。

---

## 【表格解读】

**原文无表格**。文档中仅有若干 JSON 配置片段（`config.json` 的 `rope_scaling`、`mindie_llm/conf/config.json` 的 `BackendConfig` / `ScheduleConfig`），其作用是配置项示例而非结构化对比表。

---

## 【公式解读】

**原文无公式**。文档仅包含 JSON 配置代码片段，未给出任何 LaTeX 或伪代码形式的数学公式。

---

## 【关联】

- **模型支持清单**（链接 `../model_support_list.md`）：文档明确指出"各模型支持的序列长度"以及"NTK/YaRN 已实现的模型列表"均需以该清单的"大语言模型列表"为准；本文中提及的 Llama3、Qwen2/Qwen2.5/Qwen3、Glm4-9B-Chat、LLaMA3.1-70B-Instruct、Qwen2.5-72B-Instruct 等模型均依赖此清单确认能力边界。
- **ATB Models 纯模型推理**（链接 `../user_manual/offline_inference.md#atb-models纯模型使用`）：本文中 `torchrun … examples.run_pa` 的执行方式与该上游章节的"纯模型使用"流程绑定；模型权重使能长序列特性后，只需按正常推理流程传入长文本即可，复用同一执行入口而非引入新的推理脚本。
- **上下游关系**：长序列特性在 MindIE LLM 内部属于**模型权重使能 + 运行时配置**两层组合的 feature，下游对接纯模型推理与服务化推理两条部署链路；与 KV Cache 量化、KV 多头压缩同属显存优化技术族（KV Cache 显存是长序列的核心瓶颈）。

---

## 【使用方法】

### 1. 确认模型与硬件适配

- 查阅 [模型列表](../model_support_list.md) 中"大语言模型列表"，确认所选模型支持的最大序列长度与长序列特性（训长推长 / NTK / YaRN）。
- 结合硬件显存规格与模型参数量，确认是否能承载目标长度。

### 2. 使能模型权重（以 Qwen2.5-72B-Instruct 为例）

修改模型权重目录下 `config.json`，新增 `rope_scaling`（若不需要长序列特性请勿添加）：

```json
{
  "architectures": ["Qwen2ForCausalLM"],
  "vocab_size": 152064,
  "rope_scaling": {
    "factor": 4.0,
    "original_max_position_embeddings": 32768,
    "type": "yarn"
  }
}
```

> 原文指出 LLaMA3.1-70B-Instruct 等部分模型无需修改 config 也可支持长序列，具体使能方式需参考各模型的 README。

### 3. 纯模型推理

```bash
cd ${ATB_SPEED_HOME_PATH}
torchrun --nproc_per_node [运行卡数] --master_port 20030 \
  -m examples.run_pa --model_path [模型权重路径] \
  --max_output_length [最大输出长度] \
  --max_input_length [最大输入长度] \
  --input_texts [输入文本，可支持文件或字符串]
```

- 当 `--max_input_length` 大于 `original_max_position_embeddings` 时即触发长序列推理。
- 详细流程参考 [ATB Models 纯模型使用](../user_manual/offline_inference.md#atb-models纯模型使用)。

### 4. 服务化推理

在 `<site-packages>/mindie_llm/conf/config.json` 中配置长序列场景上下文长度（示例：Batch size=1、输入 127K、输出 1K）：

```json
{
  "BackendConfig": {
    "ModelDeployConfig": {
      "maxInputTokenLen": 130048,
      "maxSeqLen": 131072
    },
    "ScheduleConfig": {
      "maxBatchSize": 1,
      "maxIterTimes": 1024,
      "maxPrefillBatchSize": 1,
      "maxPrefillTokens": 130048
    }
  }
}
```

配置完成后启动服务，调用接口时通过 curl 发送包含长序列文本的请求体即可；实际部署需根据真实业务规格调整上述参数。
