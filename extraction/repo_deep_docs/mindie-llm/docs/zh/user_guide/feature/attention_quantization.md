# Attention量化

> 仓 `mindie-llm` · 路径 `docs/zh/user_guide/feature/attention_quantization.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-llm/docs/zh/user_guide/feature/attention_quantization.md

# Attention量化 文档深度解读

## 【定位】
本文档阐述 MindIE LLM 在 Atlas 800I A2 推理服务器上对 LLaMA3.1-70B 的 self-attention 中 Q/K/V 张量进行 8bit 量化（FAQuant）的特性能力，目的是降低 KV Cache 显存占用并加速 decode 阶段 attention 算子以提升吞吐。

## 【技术要点】
- **量化对象**：将 self-attention 中的 `q_proj` / `k_proj` / `v_proj` 三个投影输出的 q、k、v 特征统一量化为 int8，输出再反量化为浮点。
- **强约束的硬件/模型/特性组合**：仅支持 Atlas 800I A2 推理服务器、必须与 W8A8 量化配套使用、当前仅支持 LLaMA3.1-70B、需与「长序列」特性以及 Function Call 联合启用。
- **配套量化方案**：以 W8A8（权重 8bit、激活 8bit）为前置条件；在 W8A8 量化产物的目录基础上新增 `fa_quant_type` 与 self_attn 相关字段。
- **量化产物文件**：权重文件 `quant_model_weight_w8a8.safetensors` + 权重描述文件 `quant_model_description.json`，其余为推理所需的 `config.json` / `tokenizer.*` 等配置文件。
- **新增描述字段语义**：`fa_quant_type=FAQuant` 标识启用 Attention 量化；`input_scale` 用于将 q/k/v 特征量化为 int8，`deq_scale` 用于将 q/k/v 输出反量化回浮点；`quant_bias`、`input_offset` 共同承担量化参数表达；`o_proj` 也按 W8A8 同步量化。
- **标量参数张量化**：q、k、v 的 scale 与 offset 分别按 head 维度展开（shape 与 head_num、head_dim 绑定），以便在 attention 计算中按 head 精度还原。

## 【关键机制与数据】
- **工作原理（原文表述）**：q/k/v 量化通过 `input_scale` 完成 int8 量化，经 attention 算子计算后再由 `deq_scale` 反量化回浮点，从而在保持 attention 计算精度可控的同时，把 decode 阶段 attention 算子输入/中间结果的显存占用降至 8bit 量级，减少 KV Cache 显存压力并提升算子吞吐。
- **数据流（原文图 1）**：在 W8A8 量化推理流程的基础上，自 `q_proj` / `k_proj` / `v_proj` 输出得到的 q、k、v 张量先按 head 级 scale/offset 量化为 int8，进入 attention 计算后由 deq_scale 还原为浮点，再与同样经过 W8A8 量化的 `o_proj` 衔接。
- **量化描述差异**：和纯 W8A8 权重相比，Attention 量化在 `quant_model_description.json` 中**新增** `fa_quant_type` 字段以及 `self_attn` 下的 q/k/v 量化字段；权重 dtype 不变，仍为 W8A8。
- **性能/吞吐收益（原文）**：原文未提供具体吞吐提升、时延或显存节省的数值，仅定性描述为「减少 KV Cache 显存占用 + 优化 decode 阶段 attention 算子速度 + 提升吞吐」。
- **典型模型 head 配置（依据表 1/表 2 推断）**：q 的 scale/offset shape 由 `q_head_num × head_dim` 决定，k、v 的 scale/offset shape 由 `kv_head_num × head_dim` 决定（原文字段名称直接给出此结构）。

## 【表格解读】

**表 1**（原文逐字还原）：

| Tensor信息 | dtype   | shape                    |
| ---------- | ------- | ------------------------ |
| q_scale    | float16 | [q_head_num, head_dim]   |
| q_offset   | float16 | [q_head_num, head_dim]   |
| k_scale    | float16 | [kv_head_num, head_dim]  |
| k_offset   | float16 | [kv_head_num, head_dim]  |
| v_scale    | float16 | [kv_head_num, head_dim]  |
| v_offset   | float16 | [kv_head_num, head_dim]  |

**逐行解读**：
- `q_scale` / `q_offset`：float16 精度，按 Query 的 head 维度展开为 `[q_head_num, head_dim]`，提供 q 在每个 head、每个 head_dim 通道上的量化缩放因子与零点偏移，用于把 q 特征量化为 int8。
- `k_scale` / `k_offset`：float16 精度，按 KV head 维度展开为 `[kv_head_num, head_dim]`（在 GQA/MQA 场景下 `kv_head_num` 通常小于 `q_head_num`），用于把 k 特征量化为 int8。
- `v_scale` / `v_offset`：float16 精度，shape 与 k 完全一致 `[kv_head_num, head_dim]`，用于把 v 特征量化为 int8。

**表 2**（原文逐字还原）：

| Tensor信息 | dtype    | shape                    |
| ---------- | -------- | ------------------------ |
| q_scale    | bfloat16 | [q_head_num, head_dim]   |
| q_offset   | bfloat16 | [q_head_num, head_dim]   |
| k_scale    | bfloat16 | [kv_head_num, head_dim]  |
| k_offset   | bfloat16 | [kv_head_num, head_dim]  |
| v_scale    | bfloat16 | [kv_head_num, head_dim]  |
| v_offset   | bfloat16 | [kv_head_num, head_dim]  |

**逐行解读**：
- 与表 1 的差异仅在于 dtype 由 float16 切换为 bfloat16，shape 规则保持不变。
- 表 1 与表 2 分别覆盖原始权重为 float16 / bfloat16 两种场景下的 Attention 量化参数 dtype 选择；shape 的 head 维度（`q_head_num`、`kv_head_num`）与原始权重 shape `[n, k]` 没有直接耦合，而是绑定到 attention head 结构。
- 两张表共同说明：scale/offset 始终按 head × head_dim 维度张量化存储，dtype 与原权重 dtype 保持一致，从而在量化/反量化时与上游 W8A8 路径对齐。

## 【公式解读】
原文无公式。

## 【关联】
- **W8A8 量化**：Attention 量化必须建立在 W8A8 量化的产物之上，目录结构与 `quant_model_description.json` 的字段命名（如 `W8A8`、`input_scale`、`input_offset`、`quant_bias`、`deq_scale`）均继承自 W8A8 流程，并在其上叠加 `fa_quant_type=FAQuant` 与 self_attn 下的 q/k/v 量化字段。
- **长序列特性**：原文明确 Attention 量化需「和长序列特性」配合使用，二者协同以在长上下文场景下缓解 KV Cache 显存压力。
- **Function Call**：原文明确 Attention 量化需「和 Function Call 配合使用」，表明该特性在 Function Call 推理链路中具有针对性收益。
- **模型支持**：当前链路唯一覆盖的目标模型为 LLaMA3.1-70B。
- **硬件支持**：唯一覆盖的推理硬件为 Atlas 800I A2 推理服务器。
- **推理主流程**：Attention 量化嵌于自注意力计算路径之中，上游承接 `q_proj` / `k_proj` / `v_proj`，下游连接 `o_proj`，与整体的 transformer layer 推理流程耦合。

## 【使用方法】
- **启用前置条件（原文）**：Atlas 800I A2 推理服务器；先完成 W8A8 量化；模型为 LLaMA3.1-70B；与「长序列」特性、Function Call 同时启用。
- **产物形态（原文）**：在 W8A8 量化产物目录下产出 `quant_model_weight_w8a8.safetensors`（权重）与 `quant_model_description.json`（权重描述，含 `fa_quant_type: FAQuant` 及 self_attn 下 q/k/v 的 `input_scale` / `input_offset` / `quant_bias` / `deq_scale` 字段）。
- **具体启动命令、CLI 参数、配置文件开关**：原文未涉及。

## 图文联合解读

- `attention_quantization.png`: ## 图文联合解读

**1) 图中内容：** 展示Attention量化的算子数据流。Q、K经ROPE后，Q/K/V各自执行①Hadamard Rotation（R，[d,d]）→ ②Quant（per-block对称量化）→ ③QKᵀ的INT8 Matmul → DQ → Softmax → ②P quant → ③PV的INT8 Matmul → DQ → ①R⁻¹反旋转 → Out proj。

**2) 技术结论：** 通过①Hadamard旋转抑制离群值使分布均匀化，②per-block对称量化将KV压为INT8，③两次INT8 Matmul减少显存与计算开销，验证了Attention端到端8bit量化的可行性。

**3) 与文档关系：** 图示精确对应文档所述"q/k/v量化为8bit以压缩KV Cache、优化decode速度、提升吞吐"的设计，并通过①②③标注呼应W8A8中A8的per-block对称量化实现。
