# ChunkMBS

> 仓 `mindspeed-mm` · 路径 `docs/zh/features/chunkmbs.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-mm/docs/zh/features/chunkmbs.md

# ChunkMBS 文档深度解读

## 【定位】

本文档描述 **ChunkMBS** 特性——在 FSDP2 大模型训练中，通过在单次参数 Unshard 完成后对 Batch 维度做细粒度切分（Micro-chunk），结合异步激活 Offload 流水线，压缩单次 Unshard 后的显存占用、减少重复 Unshard 通信次数，从而提升整体训练吞吐。

---

## 【技术要点】

1. **问题根源**：FSDP2 每个 Block 计算前都要做整块参数 Unshard（异步 Copy-in + 异步通信 + 同步 Copy-out），通信开销大且同步 Copy-out 占比高，与计算抢占总线带宽。
2. **前置依赖**：方案建立在**重计算（Recomputation）** 与 **异步激活卸载（Async Activation Offload）** 两大基础特性之上——前向仅保留 Layer 入口激活值，并异步卸载至 Host 内存。
3. **核心机制**：单次参数 Unshard 完成后，将当前 Layer 输入沿 Batch 维度切成多个 Micro-chunks，依次做前反向；计算间隙异步 offload 激活，反向时按需 D2H 迁回对应微块激活，完成后立即触发下一微块加载与计算。
4. **显存收益**：整体激活显存峰值压缩至**单个微块量级**，解耦显存占用与计算规模，可通过增加切块数适配更大计算规模。
5. **吞吐收益**：原 GBS 固定下，将 `micro_batch_size` 由 `MBS` 提到 `GBS`、梯度累积降为 1，配合 `chunk_mbs = GBS/MBS`，每个 Block 每步只做一次参数 Unshard，省去梯度累积步内的重复 Unshard 通信。
6. **配套使用约束**：开启 ChunkMBS 的 module 必须**同时**开启 activation offload 与 recompute，且 `apply_modules` 须被二者的 `apply_modules` 覆盖。

---

## 【关键机制与数据】

**工作原理（原文摘录与组织）**：

- Device 侧显存构成：
  - **静态显存**：模型参数 + 梯度 + 优化器经 Sharding 后的占用。
  - **动态显存**：反向重计算阶段，单个 Block 对应单个 Micro-batch 所需的全部激活显存。
- 流水线时序：
  1. Layer 输入沿 Batch 切分为多个 Micro-chunks；
  2. 计算间隙异步 offload 激活至 Host；
  3. 反向阶段按需 D2H 迁回对应微块的激活；
  4. 完成该微块前反向后立即触发下一微块加载与计算。
- 等价改写：将"每个梯度累积步都对 Block 做 Unshard"压缩为"每个 Block 每步只做一次 Unshard"。

**性能数据（原文）**：
- Qwen3.5 35B 模型上实测**整网收益约 5%**。

---

## 【表格解读】

**原文无表格**。

---

## 【公式解读】

**原文无公式**。

（注：原文中所有数值关系均为文字描述，例如"原来的 `micro_batch_size` 为 8，切成 4 份，每份的大小为 2，则该字段配置为 2"、"`GBS/MBS`"等，但未以公式形式给出。）

---

## 【关联】

依据文末内部链接信息：

- **[Async Activation Offload](async_activation_offload.md)**：ChunkMBS 是建立在 Async Activation Offload 之上的上层特性——异步 Offload/D2H 流水线正是 ChunkMBS 显存压缩的"搬运"载体。本文明确要求 `enable_activation_offload: true` 且 `activation_offload_plan.apply_modules` 覆盖与 ChunkMBS 相同的 modules。
- **重计算（Recomputation）**：与 Async Activation Offload 并列为两大基础依赖。ChunkMBS 假设前向只保留 Layer 入口处的激活值，因此反向靠重计算恢复——配置上要求 `recompute: true` 且 `recompute_plan.apply_modules` 覆盖相同 modules。
- **FSDP2 / 静态显存分片**：ChunkMBS 解决的是 FSDP2 Unshard 流程（异步 Copy-in、异步通信、同步 Copy-out）带来的通信与总线带宽抢占问题，其上游为 FSDP2 分布式训练框架，下游消费方为 `model.visual.blocks.{*}`、`model.language_model.layers.{*}` 等 Decoder Layer 类模块。

---

## 【使用方法】

> 注意：以下配置均为原文给出的 YAML 片段。

**完整配置示例**：

```yaml
# 重计算配置
recompute: true
recompute_plan:
    apply_modules:
     - model.visual.blocks.{*}
     - model.language_model.layers.{*}
     
# activation offload 配置
enable_activation_offload: true
activation_offload_plan:
    apply_modules:
     - model.visual.blocks.{*}
     - model.language_model.layers.{*}
     
# chunkmbs配置
enable_chunk_mbs: true
chunkmbs_plan:
    apply_modules:
     - model.language_model.layers.{*}
    chunk_mbs: 2                  # chunk之后的micro batchsize
    batch_dim: 0
    chunk_arg_indexs: [0]
    chunk_kwarg_names: ["position_embeddings", "position_ids", "rope_deltas", "attention_mask"]
```

**超参说明（逐字整理自原文）**：

| 超参 | 含义 |
|---|---|
| `enable_chunk_mbs` | 是否开启 chunkmbs 特性，`true` 表示开启，`false` 表示不开启 |
| `apply_modules` | 需要开启该特性的 module，使用正则表达式匹配；**须被包含在 `recompute` 与 `activation_offload` 特性的 `apply_modules` 中** |
| `chunk_mbs` | chunk 之后的 mbs。例：原 `micro_batch_size=8`，切成 4 份，每份大小为 2，则该字段配置为 `2` |
| `batch_dim` | batchsize 所在维度。Layer 输入 layout 为 `[b, s, h]` 则配置为 `0`；为 `[s, b, h]` 则配置为 `1` |
| `chunk_arg_indexs` | 以 `args` 形式传入且需要在 batch 维度切分的入参下标列表 |
| `chunk_kwarg_names` | 以 `kwargs` 形式传入且需要在 batch 维度切分的入参名列表 |

**切分入参示例（原文 Python 伪调用）**：

```python
hidden_states = decoder_layer(
    hidden_states,                       # args[0]，需切分
    position_embeddings=position_embeddings,   # kwargs，需切分
    attention_mask=layer_mask,                 # kwargs，需切分
    position_ids=text_position_ids,           # kwargs，需切分
    rope_deltas=rope_deltas,                   # kwargs，需切分（原文列入切分集合）
    past_key_values=past_key_values,           # 不切分
    use_cache=use_cache,                       # 不切分
    cache_position=cache_position,             # 不切分
    **kwargs,
)
```

原文对应配置逻辑：`hidden_states`（`args` 形式）由 `chunk_arg_indexs: [0]` 指定；`position_embeddings`、`attention_mask`、`position_ids`、`rope_deltas`（`kwargs` 形式）由 `chunk_kwarg_names` 指定；其余入参不参与切分。
