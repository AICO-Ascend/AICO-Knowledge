# ChunkLoss

> 仓 `mindspeed-llm` · 路径 `docs/zh/pytorch/features/mcore/chunk_loss.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-llm/docs/zh/pytorch/features/mcore/chunk_loss.md

# ChunkLoss 文档深度解读

## 【定位】

这篇文档描述的是在大词汇表（`vocab_size ≫ hidden_size`）LLM 训练场景下，通过**对序列维度做分块（chunking）+ 立即反传**的方式来避免在显存中同时驻留整段 `[bs, seq, vocab_size]` logits 的 ChunkLoss 能力，是 FSDP2 训练路径下降低 loss 计算显存尖峰的工程方案。

---

## 【技术要点】

1. **问题驱动**：在 FSDP2 训练下，`lm_head` 输出维度 `vocab_size` 远大于 `hidden_size`，传统做法会显式构造 `[bs, seq, vocab_size]` 的 logits 张量，造成显著显存尖刺。
2. **核心机制 —— 序列分块**：将序列维度切分为多个长度为 `sub_seq` 的子段（chunk），每个子段独立完成"前向 → 立即反向"，从而任意时刻显存中至多只需缓存长度为 `sub_seq` 的 logits。
3. **LMHead 重写为 `nn.Linear` 子类**：保留线性投影能力（`F.linear(hidden_states, w, b)`），但新增 `loss_ctx` 入参；当提供 `loss_ctx` 时**不返回 logits**，而是把 loss 计算委托给 `loss_ctx(hidden_states, w, b)` 执行，从而走 chunked loss 路径。
4. **DTensor 兼容处理**：因 FSDP2 下权重/偏置通常是 DTensor，进入计算前需 `.to_local()` 转成 local tensor；若 `weight` 是 DTensor 而 `bias` 不是 DTensor，则直接 `raise TypeError`，保证一致性。
5. **三步启用流程**：① 重写 LMHead ② 在模型 `forward` 里加 `loss_ctx` 入参并做使能判断 ③ 在启动脚本加 `--loss-compute-mode chunk --loss-chunk-size 1024`。
6. **模型适配扩展点**：不同的 `loss` 计算方式需在 `Trainer._build_chunk_loss` 中适配修改（链接定位 `trainer.py#L86`）。

---

## 【关键机制与数据】

- **工作原理（数据流）**：
  - 原始路径：`hidden_states → lm_head(Linear) → logits[bs, seq, vocab_size] → loss`，整个 logits 全量驻留显存。
  - ChunkLoss 路径：`hidden_states → chunk(seq, sub_seq) → 对每个 chunk：lm_head(local) + loss → 立即 backward → 释放该 chunk 的 logits`，形成"小段生产—立刻消费—立刻回收"的显存流水线。
- **显存收益来源**：任意时刻 logits 占用上限从 `vocab_size × seq` 量级降到 `vocab_size × sub_seq` 量级（原文未给出具体倍数，仅定性描述"显著降低"）。
- **数值等价性（原文）**：「通过合理设置 `chunk_size`，可在显著降低显存峰值的同时**保持相同的损失曲线**」——即算法与全量等价，不引入近似误差。
- **现有参考实现**：文档指向 `Qwen3ForCausalLM` 的 FSDP2 实现作为模板。

---

## 【表格解读】

**原文无表格。**

---

## 【公式解读】

**原文无公式。**（整篇为工程实现说明，未给出 LaTeX 公式或伪代码数学表达式。涉及"分块"的概念性说明仅以自然语言描述 `sub_seq`、`vocab_size`、`hidden_size` 等符号，无显式公式。）

---

## 【关联】

- **下游特性/依赖**：
  - **FSDP2** 训练路径（分布式张量 DTensor）：LMHead 的重写里专门处理 `DTensor.to_local()`，说明 ChunkLoss 是 FSDP2 路线下的能力。
  - **`vocab_size` 较大的 LLM**：典型如 Qwen3 等大词表模型，文档给出 `Qwen3ForCausalLM FSDP2` 作为参考实现。
- **代码扩展点（内部链接信息）**：
  - 模型侧参考：`mindspeed_llm/fsdp2/models/qwen3/qwen3.py`（Qwen3ForCausalLM 的 FSDP2 实现，示范如何把 `loss_ctx` 接入 `forward`）。
  - 框架侧适配：`mindspeed_llm/fsdp2/train/trainer.py` 的 `Trainer._build_chunk_loss` 方法（用于适配不同 loss 计算方式，如需新增 loss 类型，应在此修改）。
- **上下游关系**：
  - 上游：用户提供 `hidden_states`（来自 backbone 的输出）。
  - 中游：LMHead + loss_ctx（即 ChunkLoss 模块）。
  - 下游：标准 PyTorch autograd，按 chunk 立即反传。

---

## 【使用方法】

文档给出了完整的三步启用方式：

### 第 1 步：替换 `lm_head`（`output_layer`）实现

原实现为 `nn.Linear`，改为自定义 `LMHead(nn.Linear)` 子类（无 bias），核心逻辑：

| 条件 | 行为 |
|------|------|
| `self.weight` 是 `DTensor` | 先 `.to_local()` 转为 local tensor；`bias` 若存在也必须为 `DTensor` 并转 local，否则抛 `TypeError` |
| `self.weight` 不是 `DTensor` | 直接使用原 `weight`、`bias` |
| `loss_ctx is None` | 走原路径：`F.linear(hidden_states, w, b)` 返回 logits（与普通 LMHead 等价，便于回退） |
| `loss_ctx is not None` | **不返回 logits**，改为 `return None, loss_ctx(hidden_states, w, b)`，把 loss 计算委托给 chunked loss 上下文 |

### 第 2 步：在模型 `forward` 中接入 `loss_ctx`

- 参考实现：`mindspeed_llm/fsdp2/models/qwen3/qwen3.py`（`Qwen3ForCausalLM` 的 FSDP2 版本）。
- 在 `forward` 函数里添加 `loss_ctx` 入参，并在实现内做使能判断（`loss_ctx is None` 走普通 logits 路径，否则走 chunked loss 路径）。
- 若模型有特定 loss 计算方式，需在 `Trainer._build_chunk_loss`（`trainer.py#L86`）里适配。

### 第 3 步：启动脚本添加使能参数

```shell
--loss-compute-mode chunk \
--loss-chunk-size 1024 \
```

- `--loss-compute-mode chunk`：启用 chunked loss 计算模式。
- `--loss-chunk-size 1024`：设置每个 chunk 的序列长度 `sub_seq = 1024`（即一次前向+反传处理的 token 数）。

### 预期效果

原文：「启用 ChunkLoss 特性后，通过合理设置 `chunk_size`，可在**显著降低显存峰值**的同时**保持相同的损失曲线**。」
