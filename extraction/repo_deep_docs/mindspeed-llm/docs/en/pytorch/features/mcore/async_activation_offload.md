# Async Activation Offload

> 仓 `mindspeed-llm` · 路径 `docs/en/pytorch/features/mcore/async_activation_offload.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-llm/docs/en/pytorch/features/mcore/async_activation_offload.md

# 一体化深度解读：Async Activation Offload

## 【定位】

这篇文档解决大模型训练中**激活值显存峰值过高**的问题，介绍 mindspeed-llm 中通过**异步机制将激活值从 device (NPU) 卸载到 host (CPU)，并在反向阶段提前 prefetch** 的能力，目标是替代或补充传统激活重计算 (recomputation) 与序列并行 (SP) 在长序列/FSDP2 等场景下的不足。

---

## 【技术要点】

1. **显存优化核心**：把前向产生的 activation tensor 从 device 侧 offload 到 host 侧 (D2H)，把反向阶段需要的 tensor 再 H2D 加载回来，以"显存换带宽"，显著降低峰值显存。
2. **多流异步机制**：使用独立的 `h2d_stream` 与 `d2h_stream` 与计算流解耦，使 D2H/H2D 的拷贝与前向/反向计算**时间上 overlap**，隐藏 copy 开销。
3. **早期预取 (prefetch)**：在 backward 阶段，**提前**把下一步需要的 tensor 加载到 device，从而隐藏 H2D 的延迟。
4. **按 block 组织生命周期**：通过 `async_save_on_cpu` 上下文管理器，将激活值的管理粒度下沉到模型 block (`block_idx`, `depth`)，支持细粒度策略选择。
5. **可定制校验函数 `custom_check_fn`**：只对返回 `True` 的 tensor 做 offload，**只 offload "算力重、激活 footprint 小" 的部分**，"激活 footprint 大、算力时间短" 的部分仍走 recomputation，避免 H2D/D2H 开销无法被掩盖的情况。
6. **性能收益（典型场景）**：长序列 (self-attention) 端到端 **>20%**，FSDP2 场景端到端 **>60%**。

---

## 【关键机制与数据】

### 工作原理 / 数据流

- **前向 (forward)**：进入 `async_save_on_cpu` 上下文后，模型 block 的 forward 输出 `output = layer(input)` 时，**激活值沿着 `d2h_stream` 异步写入 host 内存**，主计算流不阻塞。
- **反向 (backward)**：进入该 block 反向阶段时，依赖的激活值通过 `h2d_stream` **提前 prefetch 回 device**，与反向计算 overlap，避免同步等待。
- **三流并行拓扑**：`compute_stream`（默认流）、`d2h_stream`（offload）、`h2d_stream`（prefetch）三流并发，目标是让 **D2H 隐藏在 forward 中，H2D 隐藏在 backward 中**。
- **策略判定（原文给出的判定准则）**：
  - 小 activation footprint + 长 compute time → **offload**（copy 时间能被计算掩盖）
  - 大 activation footprint + 短 compute time → **recomputation**（copy 开销过大，难以隐藏）
  - 实际场景应**与 recomputation 组合使用**，而非全量 offload。

### 性能数据（原文明确给出的两条）

| 场景 | 收益 |
|---|---|
| 长序列（self-attention 激活 offload，跳过 recompute） | 端到端 **>20%** |
| FSDP2（短序列、计算无法掩盖通信；offload 释放显存后增大 micro-batch / seq len） | 端到端 **>60%** |

原文标注"in typical scenarios"，即**典型场景**而非普适保证。

---

## 【表格解读】

**原文无表格**。原文中所有参数信息均以列表 + 代码片段形式给出，未出现 markdown/HTML 表格结构。

---

## 【公式解读】

**原文无公式**。文档未给出任何 LaTeX 公式或伪代码数学表达式，仅有 Python 上下文管理器的伪代码示例：

```python
with async_save_on_cpu(
    h2d_stream=h2d_stream,
    d2h_stream=d2h_stream,
    block_idx=block_idx,
    depth=depth,
    custom_check_fn=your_check_fn
):
    output = layer(input)
```

该伪代码展示的是 API 调用形态，非数学公式。

---

## 【关联】

原文未提供内部链接，但根据文中语义可识别出以下**与本特性互为补充/上下游**的模块：

1. **激活重计算 (Activation Recomputation)**：上游/并列技术。文档明确指出本特性是 recomputation 的**替代或组合**，应按 `custom_check_fn` 的判定准则择优选用。
2. **序列并行 (Sequence Parallelism)**：上游对比基线。文档指其"频繁的跨设备通信难以有效隐藏"是本特性要解决的瓶颈之一。
3. **FSDP2 分布式策略**：上游触发场景。FSDP2 下参数分片/聚集引入额外通信，本特性在 recompute 入口处 offload 释放显存，**为后续增大 micro-batch 或 sequence length、提升算通信比创造条件**。
4. **self-attention 计算**：典型受益模块，因 self-attention 算力随序列长度**二次方**增长，是长序列场景下首选 offload 目标。
5. **多流机制 (CUDA/Ascend streams)**：底层依赖。`h2d_stream` / `d2h_stream` 为本特性的运行时载体，原文建议"创建专用的全局流"以保证与计算流异步。

---

## 【使用方法】

### 启用方式（API 层）

通过上下文管理器 `async_save_on_cpu` 包住**模型每个 block 的 forward 段**：

```python
with async_save_on_cpu(
    h2d_stream=h2d_stream,
    d2h_stream=d2h_stream,
    block_idx=block_idx,
    depth=depth,
    custom_check_fn=your_check_fn
):
    output = layer(input)
```

### 配置项 / 参数说明

| 参数 | 含义 | 建议 |
|---|---|---|
| `h2d_stream` | host→device 加载流 | 建议创建**专用全局流**，与计算流异步 |
| `d2h_stream` | device→host offload 流 | 同上，独立于 `h2d_stream` 与计算流 |
| `block_idx` | 当前 block 在模型中的索引 | 用于定位本 block 的激活 |
| `depth` | 模型总层数 / block 总数 | 用于全局调度/窗口决策 |
| `custom_check_fn` | 自定义校验函数 | 返回 `True` 的 tensor 才被 offload；按 "小 footprint + 长 compute → offload；大 footprint + 短 compute → recompute" 准则选择 |

### 调优准则（原文给出）

- **必须**与 recomputation **组合使用**，而非全量 offload。
- 推荐 offload 目标：self-attention 前向激活（长序列场景）、recomputation 入口处的激活（FSDP2 短序列场景）。
- 提升内存释放后，可通过**增大 micro-batch size 或 sequence length** 来提高算通信比。

> 原文未涉及具体的命令行开关、环境变量、yaml 配置项或 MindSpeed 启动参数层面的开启方式，仅描述了 Python API 层的调用形态。
