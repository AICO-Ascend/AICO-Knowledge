# ChunkLoss

> 仓 `mindspeed-llm` · 路径 `docs/en/pytorch/features/mcore/chunk_loss.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-llm/docs/en/pytorch/features/mcore/chunk_loss.md

# ChunkLoss 文档深度解读

---

## 【定位】

本文档描述了 ChunkLoss（分块损失计算）特性，针对 FSDP2 分布式训练场景下 `lm_head` 输出 logits 张量引发的显存峰值过高问题，通过将序列维度切分为 `sub_seq` 长度的子序列并即时执行 forward-backward，将同时驻留显存的 logits 量级从全序列压缩到 `sub_seq`，在保持 loss 曲线不变的前提下显著降低峰值显存占用。

---

## 【技术要点】

1. **问题根源**：FSDP2 训练中 `lm_head`（即 `output_layer`）的输出维度 `vocab_size` 通常远大于模型的 `hidden_size`，传统 loss 计算需要显式构造形状为 `[bs, seq, vocab_size]` 的 logits 张量，造成显著的显存尖峰，降低显存利用率。

2. **核心机制——序列分块 + 即时反向**：沿序列维度将 loss 计算拆分为长度为 `sub_seq` 的若干子序列，逐子序列执行：每个子序列完成 forward 后立即运行对应的 backward，从而避免同时保留整条序列的 logits。任何时刻显存中只需缓存最多 `sub_seq` 个 token 对应的 logits。

3. **`LMHead` 实现替换**：将模型原有的 `nn.Linear` 实现的 `lm_head` 替换为自定义 `LMHead`（继承自 `nn.Linear`）。该类 `forward` 接口新增 `loss_ctx: callable = None` 参数：当 `loss_ctx is None` 时回退到普通 `F.linear` 计算并返回 logits；当传入 `loss_ctx` 时不返回 logits（`return None`），而是委托 `loss_ctx(hidden_states, w, b)` 执行 chunked loss 计算。

4. **DTensor 权重/偏置本地化处理**：`LMHead.forward` 中检测 `self.weight` 是否为 `DTensor`；若是则通过 `to_local()` 转为本地张量，对 `self.bias` 做同样校验与转换（非 DTensor 偏置会抛出 `TypeError`），确保分布式张量在 chunked loss 计算路径下能正确使用。

5. **模型层接入点**：需在模型的 `forward` 函数中新增 `loss_ctx` 参数并加入使能检查。具体参考 FSDP2 的 `Qwen3ForCausalLM` 实现（`mindspeed_llm/fsdp2/models/qwen3/qwen3.py`）；若引入新的 loss 计算方式，需相应适配 Trainer 的 `_build_chunk_loss` 逻辑（修改位置 `mindspeed_llm/fsdp2/train/trainer.py#L86`）。

6. **启动参数**：通过启动脚本追加两条参数启用该特性：`--loss-compute-mode chunk` 与 `--loss-chunk-size 1024`（即 `sub_seq = 1024`）。ChunkLoss 启用后只需合理设置 `chunk_size` 即可显著降低峰值显存，且不改变 loss 曲线。

---

## 【关键机制与数据】

**工作原理与数据流**

- **传统链路**：`hidden_states` → `lm_head` (全量 `nn.Linear`) → 构造完整 logits `[bs, seq, vocab_size]` → 计算 loss。该链路在 loss 计算中间环节必须同时持有完整的 logits 张量，是显存尖峰的来源。

- **ChunkLoss 链路**：`hidden_states` 按序列维度切成 `seq / sub_seq` 个子序列 → 每个子序列进入 `LMHead.forward(hidden_states, loss_ctx=...)` → 委托给 `loss_ctx(hidden_states, w, b)` 完成该子段的 loss 与即时 backward → 进入下一子序列。显存峰值由“全序列 logits”降为“单个子序列 logits”，缩减比例约为 `seq / sub_seq`。

- **DTensor 兼容**：`weight`/`bias` 在进入 `F.linear` 之前统一转换为本地张量，保证 ChunkLoss 在 FSDP2 张量并行场景下不会因 DTensor 类型不匹配而失败。

**性能/显存数据**

- 原文仅给出定性结论：“significantly lowers peak memory use”（显著降低峰值显存）与 “keeping the same loss curve”（保持相同的 loss 曲线），未给出具体的显存节省比例、吞吐数字或基准配置。

> 原文："significantly reduce peak memory use while keeping the same loss curve."

---

## 【表格解读】

原文无表格。

---

## 【公式解读】

原文无公式。

（注：文中出现 `logits` 张量形状描述 `[bs, seq, vocab_size]`，以及分块子序列长度 `sub_seq` / `chunk_size`，但未以公式形式给出。）

---

## 【关联】

- **FSDP2 模型实现**：`Qwen3ForCausalLM`（路径 `mindspeed_llm/fsdp2/models/qwen3/qwen3.py`）作为 ChunkLoss 接入的参考实现，展示了如何在模型 `forward` 中传递 `loss_ctx`。
- **Trainer 编排层**：Trainer 的 `_build_chunk_loss` 方法（路径 `mindspeed_llm/fsdp2/train/trainer.py#L86`）负责构造 `loss_ctx` 函数；任何新增的 loss 计算方式都需要在该方法中适配，否则 ChunkLoss 路径无法被正确启用。
- **基础并行框架**：依赖 FSDP2（Fully Sharded Data Parallel v2）作为分布式训练底座，是触发本特性动机（`vocab_size` 显著大于 `hidden_size` 时 logits 显存尖峰）的运行前提。
- **`lm_head` 语义映射**：文档将 `lm_head` 与 `output_layer` 等同对待，表明该特性作用于模型末端输出层，而与具体 backbone 结构解耦。

---

## 【使用方法**

**Step 1 — 替换 `lm_head` 实现**

将模型中原有的 `nn.Linear` 形式的 `lm_head`/`output_layer` 替换为本文档给出的自定义 `LMHead`（继承自 `nn.Linear`，内部支持 DTensor → 本地张量转换，并根据 `loss_ctx` 是否提供切换为普通 logits 计算或 chunked loss 路径）。

**Step 2 — 模型 forward 接入**

在模型 `forward` 中新增 `loss_ctx` 参数并加入使能检查；参照 FSDP2 的 `Qwen3ForCausalLM` 实现。若引入新的 loss 计算方式，需同步修改 Trainer 的 `_build_chunk_loss`（位置 `mindspeed_llm/fsdp2/train/trainer.py#L86`）。

**Step 3 — 启动脚本追加参数**

```shell
   --loss-compute-mode  chunk \
   --loss-chunk-size 1024 \
```

**预期效果**

原文："significantly reduce peak memory use while keeping the same loss curve."
