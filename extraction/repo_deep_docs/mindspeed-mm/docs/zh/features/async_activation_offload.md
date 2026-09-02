# Async Activation Offload

> 仓 `mindspeed-mm` · 路径 `docs/zh/features/async_activation_offload.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-mm/docs/zh/features/async_activation_offload.md

# Async Activation Offload 文档深度解读

## 【定位】

本文档介绍多模态大模型训练中应对激活值显存瓶颈的**异步激活值卸载（Async Activation Offload）**特性：通过将激活张量异步地从 device 侧卸载到 host 侧、并在反向传播时按需预取回来，从而在不显著增加端到端耗时的前提下降低训练峰值显存占用。

---

## 【技术要点】

1. **显存优化的新路径**：跳出"重计算 + 序列并行"两大传统方案的局限，转向 D2H/H2D 卸载来直接释放 device 显存，规避重计算带来的冗余计算。
2. **多流异步机制**：通过 `h2d_stream`（Host-to-Device 流）与 `d2h_stream`（Device-to-Host 流）两条独立流，将拷贝任务与计算流解耦，使拷贝过程被计算掩盖。
3. **基于 block 的张量生命周期管理**：以"块（block）"为单位组织激活值生命周期，配合 `block_idx`（当前 block 编号）与 `depth`（模型总层数）参数实现灵活分块控制。
4. **反向预取（prefetch）机制**：反向过程中提前加载后续需要的张量，隐藏 H2D 加载延迟。
5. **自定义筛选函数 `custom_check_fn`**：仅对校验返回 True 的激活值执行 offload——显存收益与拷贝开销需要权衡，否则 H2D/D2H 开销过大难以被计算掩盖。
6. **与重计算策略互补**：文档明确指出应当"激活值参数量大、计算耗时短的进行重计算；激活值参数量小、计算耗时长的进行 offload"，两种策略按激活值特征组合使用。

---

## 【关键机制与数据】

### 工作原理

1. **显存维度（offload 路径）**
   - 原文：在前向传播阶段，将激活值张量从 device 侧卸载至 host 侧，"显著降低峰值显存占用"。
   - 数据流：`Tensor (Device) → D2H copy → Host Memory`；反向需要时再走 `Host Memory → H2D copy → Tensor (Device)`。

2. **时间维度（异步 + 预取）**
   - 原文：利用多流机制使卸载（D2H）和加载（H2D）异步，"使拷贝过程被计算掩盖"；反向过程中通过 `prefetch` 机制提前加载后续张量，"隐藏加载延迟"。
   - 关键约束（原文）：建议"全局单独新建一条流单独用来执行 H2D 和 D2H 任务"，确保与计算流无资源争抢。

3. **筛选维度（`custom_check_fn` 的取舍逻辑）**
   - 原文：建议"根据实际情况筛选出计算量大，激活值参数量小的部分"进行 offload，将"激活值参数量大，计算耗时短的"留给重计算。
   - 反向警示（原文）：若不满足上述筛选条件，"H2D 和 D2H 的开销过大，难以被计算掩盖"。

### 性能数据（原文明确给出）

| 场景 | 典型收益（原文） |
|---|---|
| 多模态模型长序列场景（卸载 self attention 前向激活值 + 跳过重计算） | "端到端性能收益 **20% 以上**" |
| FSDP2 分布式短序列场景（卸载重计算入口激活值以扩大 micro batch / 序列长度） | "端到端性能收益 **60% 以上**" |

> 性能收益的成立前提（原文）：自注意力的计算量随序列长度呈"平方关系增长"，因此卸载 self attention 的激活值后可以跳过其重计算；FSDP2 在短序列下"计算耗时无法掩盖通信耗时"，卸载节省的显存被用来放大计算量以提高"计算比例"。

---

## 【表格解读】

**原文无表格。** 文档中既无参数表、性能对比表，也无配置项表格，仅以列表 + 代码示例形式描述接口与场景。如需配置矩阵，需依据代码仓库内 `async_save_on_cpu` 实现另行梳理。

---

## 【公式解读】

**原文无公式。** 文档未给出任何 LaTeX 或伪代码形式的数学公式。唯一接近"伪代码"的是 `async_save_on_cpu` 的 `with` 语句上下文管理器示例，仅作为调用方式示意，不构成算法公式：

```
with async_save_on_cpu(
    h2d_stream=h2d_stream,
    d2h_stream=d2h_stream,
    block_idx=block_idx,
    depth=depth,
    custom_check_fn=your_check_fn
):
    output = layer(input)
```

其中各参数含义在【使用方法】节给出。

---

## 【关联】

文档为独立 feature 说明，未在文末提供内部链接，因此只能基于文中上下文梳理其与上下游特性的关系：

1. **与重计算技术的关联**：Async Activation Offload 不是替代重计算，而是**互补**——文档明确建议二者按激活值特征组合使用（参数量大/耗时短 → 重计算；参数量小/耗时长 → offload）。多模态长序列场景的案例正是将"卸载 self attention 激活值 + 跳过 self attention 重计算"组合使用，从而获得 20% 以上收益。

2. **与序列并行技术的关联**：文档将序列并行列为对比对象，指出其"频繁的跨设备通信可能难以被有效掩盖"的瓶颈，Async Activation Offload 通过"本地 D2H/H2D + 多流异步"绕开了跨设备通信掩盖问题。

3. **与 FSDP2 分布式策略的关联**：在 FSDP2 短序列场景下，本特性通过卸载重计算入口的激活值释放显存，进而支持**放大 micro batch size 或序列长度**来提升"计算:通信"比例，构成对 FSDP2 通信瓶颈的间接弥补。

4. **与多模态长序列场景的关联**：self attention 的计算量随序列长度平方增长，因此卸载其激活值具有最高的"省显存/低开销"性价比，是该特性最契合的应用形态。

5. **与计算流的关系**：`h2d_stream` / `d2h_stream` 必须独立于计算流，三者构成多流并行体系；文档强调"全局单独新建一条流单独用来执行 H2D 和 D2H 任务"以保证异步有效性。

---

## 【使用方法】

### 启用方式

通过 `async_save_on_cpu` 上下文管理器按 block 粒度启用，包裹模型某一 block 的前向计算代码：

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

### 配置项（原文逐条还原）

| 参数 | 作用 | 原文约束 |
|---|---|---|
| `h2d_stream` | H2D（Host→Device）拷贝流 | "建议全局单独新建一条流单独用来执行 H2D …任务，实现和计算流异步的效果" |
| `d2h_stream` | D2H（Device→Host）拷贝流 | 同上，"执行 … D2H 任务，实现和计算流异步的效果" |
| `block_idx` | 当前 block 在模型中的编号 | 用于 block 粒度的张量生命周期管理 |
| `depth` | 模型的总层数 | 用于 block 粒度的张量生命周期管理 |
| `custom_check_fn` | 自定义校验函数 | 仅返回 True 的激活值才会被 offload；建议按"计算量大、激活值参数量小"特征筛选，并与重计算互补使用 |

### 组合策略（原文明确给出的实践经验）

- **多模态长序列场景**：卸载 self attention 前向激活值，并在重计算时跳过 self attention 的重计算。
- **FSDP2 短序列场景**：卸载重计算入口的激活值，腾出显存后增大 micro batch size 或序列长度。

> 文档未涉及具体的命令行开关、环境变量或 YAML 配置项；启用流程以代码层 `with async_save_on_cpu(...)` 调用为准。
