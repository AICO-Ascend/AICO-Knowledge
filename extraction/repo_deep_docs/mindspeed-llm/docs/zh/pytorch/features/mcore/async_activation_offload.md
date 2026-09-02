# Async Activation Offload

> 仓 `mindspeed-llm` · 路径 `docs/zh/pytorch/features/mcore/async_activation_offload.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-llm/docs/zh/pytorch/features/mcore/async_activation_offload.md

# Async Activation Offload 一体化深度解读

---

## 【定位】

这篇文档描述了 mindspeed-llm 框架中"异步激活值卸载"（Async Activation Offload）能力的原理与使用方法，用于解决大模型训练中因参数规模和序列长度增长而导致的显存压力问题，并弥补传统重计算（冗余算力代价高）与序列并行（跨设备通信难以掩盖）两类显存优化方案的不足。

---

## 【技术要点】

- **显存卸载方向**：将激活值张量从 device 侧（GPU/NPU 显存）卸载到 host 侧（CPU 内存），目标为"显著降低峰值显存占用"。
- **异步执行机制**：借助多流（multi-stream）将 D2H（Device-to-Host，卸载）和 H2D（Host-to-Device，回载）操作与主计算流解耦，使拷贝过程可被前向/反向计算掩盖。
- **提前预取（prefetch）**：在反向传播过程中，按"块（block）"组织张量生命周期，提前加载后续所需张量，隐藏 H2D 加载延迟。
- **按 block 粒度的生命周期管理**：以 `async_save_on_cpu` 上下文管理器封装某个 block 的前向计算，由 `block_idx`（当前 block 编号）与 `depth`（模型总层数）共同决定张量卸载/预取策略。
- **选择性 offload 策略**：通过 `custom_check_fn` 自定义校验函数过滤激活值——"激活值参数量小、计算耗时长"的张量适合 offload；"激活值参数量大、计算耗时短"的张量更适合重计算，否则 H2D/D2H 开销难以被计算掩盖。
- **流隔离建议**：`h2d_stream` 与 `d2h_stream` 建议"全局单独新建一条流"专门执行 H2D 与 D2H 任务，避免与计算流竞争。

---

## 【关键机制与数据】

**整体数据流（基于原文推导）**

1. **前向阶段**：在 `async_save_on_cpu` 上下文内执行某 block 的前向计算（如 `output = layer(input)`），计算完成后通过 `d2h_stream` 将激活值张量异步卸载至 host 侧内存。
2. **反向阶段**：进入反向传播时，根据 `block_idx` 与 `depth` 推断后续需要的张量顺序，通过 `prefetch` 机制提前触发 H2D 加载，使 host 侧张量在真正被反向计算消费之前回到 device。
3. **异步掩盖**：H2D 与 D2H 拷贝分别在专用流上运行，与计算流并行，因此只要单层计算耗时 ≥ 拷贝耗时，拷贝开销即可被掩盖，整体几乎零额外时间成本。

**性能收益数据（原文）**

- **长序列场景**：self-attention 计算量与序列长度呈平方关系增长（原文："self-attention的计算量随序列长度呈平方关系增长"）。卸载 self-attention 前向激活值并**在重计算时跳过 self-attention 的重计算**——典型场景下**端到端性能收益 20% 以上**（原文："典型场景下端到端性能收益20%以上"）。
- **FSDP2 场景**：FSDP2 分布式策略对参数进行切分与聚合；较短序列长度下"计算耗时无法掩盖通信耗时"（原文）。将重计算入口的激活值卸载以腾出显存，进而**增大 micro-batch size 或序列长度以提高计算比例**——典型场景下**端到端性能收益 60% 以上**（原文："典型场景下端到端性能收益60%以上"）。

**与其他显存优化策略的耦合关系**

- 与重计算互补：offload 释放的显存可用于"跳过"部分算子的重计算，从而同时获得显存与计算双重收益（如 self-attention 案例）。
- 与 FSDP2 互补：offload 释放的显存可用于放大 micro-batch / 序列长度，使计算/通信比提高，间接缓解 FSDP2 通信瓶颈。

---

## 【表格解读】

原文无表格。

---

## 【公式解读】

原文无公式。

---

## 【关联】

依据文档正文逻辑，Async Activation Offload 与以下特性/模块存在上下游或互补关系：

- **重计算（Recomputation / Activation Checkpointing）**：传统显存优化手段，但存在冗余计算；Async Activation Offload 作为其替代/补充——可与重计算**联合使用**（原文："结合重计算策略"），按张量特性选择 offload 或重计算。
- **序列并行（Sequence Parallelism）**：传统显存优化手段，但"频繁的跨设备通信可能难以被有效掩盖"；Async Activation Offload 通过将显存压力卸载到 host 侧来缓解对序列并行的依赖。
- **FSDP2（Fully Sharded Data Parallel v2）**：分布式策略，涉及参数切分与聚合通信；在短序列场景下 offload 可腾出显存以放大 micro-batch/序列长度，"提高计算比例"以掩盖通信。
- **self-attention 模块**：长序列下计算量 O(L²) 增长，是 offload 重点目标张量；与"重计算跳过 self-attention"形成耦合收益。
- **多流（multi-stream）机制**：`h2d_stream` / `d2h_stream` 依赖底层多流调度实现异步掩盖，是该特性的底层支撑。
- **上下文管理器机制（`async_save_on_cpu`）**：以 block 为粒度包装前向计算，是特性的对外 API 入口。

---

## 【使用方法】

启用方式为 Python 上下文管理器 `async_save_on_cpu`，典型代码（原文）：

```python
with async_save_on_cpu(
    h2d_stream=h2d_stream,
    d2h_stream=d2h_stream,
    block_idx=block_idx,
    depth=depth,
    custom_check_fn=your_check_fn
):
    # 模型某个block的前向计算代码，此处仅作为示例
    output = layer(input)
```

**配置项说明（原文）**：

| 参数 | 含义 | 建议 |
|---|---|---|
| `h2d_stream` | H2D（Host→Device）专用流 | 全局单独新建一条流，专门执行 H2D 任务 |
| `d2h_stream` | D2H（Device→Host）专用流 | 全局单独新建一条流，专门执行 D2H 任务 |
| `block_idx` | 当前 block 在模型中的编号 | 用于推断预取/卸载顺序 |
| `depth` | 模型的总层数 | 与 `block_idx` 配合决定张量生命周期管理策略 |
| `custom_check_fn` | 自定义校验函数 | 仅对校验返回 True 的激活值执行 offload；建议按"激活值参数量小、计算耗时长"标准筛选，并结合重计算策略使用 |

**适用场景与收益总结（原文）**：

- 长序列 + self-attention 卸载 + 跳过 self-attention 重计算 → 端到端 **20%+** 性能收益。
- FSDP2 + 短序列 + 重计算入口激活值卸载 + 增大 micro-batch/序列长度 → 端到端 **60%+** 性能收益。
