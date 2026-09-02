# causal_conv1d 算子设计文档

> 仓 `tilelang-ascend` · 路径 `examples/causal_conv1d/design.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/tilelang-ascend/examples/causal_conv1d/design.md

# causal_conv1d 算子设计文档 深度解读

---

## 【定位】

这篇文档描述了 **TileLang-Ascend 框架下 `causal_conv1d` 因果一维卷积算子的完整实现设计**，用于线性注意力机制（Mamba、RWKV 等）中隐藏状态的递推计算，重点解决"如何在 Ascend NPU 上通过 Vector 核 + Pipeline 双缓冲 + Token 批处理实现高效因果卷积"的问题，覆盖 Prefill（FN VARLEN）和 Decode（UPDATE）两种推理模式。

---

## 【技术要点】

1. **算子本质与计算特征**：纯 Vector element-wise 计算（mul → add → silu），无 GEMM/Cube 核参与，复杂度等级中等，关键挑战在于历史 buffer 管理与状态递推。当前实现仅支持 **width=4**。

2. **编程模式选型：Expert（手动优化）**：放弃自动并行化原因在于需手动控制双缓冲 `set_flag/wait_flag` 同步、调用 `T.tile.mul_add_dst`/`T.tile.silu` 融合原语、显式分配 UB buffer。

3. **Pass 配置三件套**：
   - `TL_ASCEND_AUTO_CV_COMBINE: True`（自动 CV 分离）
   - `TL_ASCEND_AUTO_SYNC: False`（关闭自动同步，由开发者手动编排同步点）
   - `TL_ASCEND_MEMORY_PLANNING: True`（开启内存规划）

4. **Pipeline 双缓冲 + Token 批处理**：`STAGES=2`（双缓冲 stage 数）、`BATCH_TOKENS=4`（每次处理 4 个 token），通过 `set_flag/wait_flag` 在 `mte2`/`v`/`mte3` 三个队列之间编排同步。

5. **典型配置参数**：`num_batches=2`, `total_tokens=2048`, `dim=2048`, `width=4`, `state_len=3`, `CORE_NUM=24`, `BATCH_TOKENS=4`, `STAGES=2`。

6. **UB 容量规划**：典型配置下 UB 总占用 ≈ **30.5KB**（x_buf 8KB + y_buf 8KB + state/hist/w/save 各 3~4KB），远低于 128KB~256KB 上限，buffer 设计有充足余量。

---

## 【关键机制与数据】

### 工作原理

算子实现因果卷积的滑动窗口递推。每个 token `t` 的处理流程为：
1. 取出历史 `hist = [x[t-width+1], ..., x[t-1]]`
2. 计算加权累加 `acc = Σ weight[i] * history[i] + weight[width-1] * x[t]`
3. 激活 `y[t] = silu(acc)`
4. 滑动窗口：history 队列向前推进，新 `x[t]` 补入队尾

### 数据流（GM ↔ UB）

- **加载阶段**：通过 `T.copy(weight[i, d_offset], w*_ub)` 从 GM 加载 weight 到 UB；通过 `T.copy(x[hist_global_idx, d_offset], hist*_ub)` 加载历史 token；通过 `T.copy(conv_state[cache_line, h, d_offset], hist*_ub)` 加载初始状态。
- **计算阶段**：使用 `T.tile.mul_add_dst(acc, x, w)` 融合 mul+add，使用 `T.tile.silu(y, acc)` 融合激活。
- **写回阶段**：`T.copy(y_buf[cur, i, :], y[out_base + i, d_offset])` 输出到 GM；`T.copy(save*_ub, conv_state[cache_line, h, d_offset])` 保存最终状态。

### 性能数据

原文未提供实测性能数据或吞吐量数字，仅给出 UB 容量估算与配置参数。

---

## 【表格解读】

### 表 1：1.3 计算特征分析（原文逐字还原）

| 维度 | 分析结果 |
|------|---------|
| **计算类型** | Vector element-wise（无 GEMM） |
| **复杂度级别** | 中等（mul → add → mul → add ... → silu，历史 buffer 管理） |
| **动态 shape** | Prefill: B、T 为符号维度，支持变长（cu_seqlens） |
| **核间协作** | 纯 Vector 核计算，无 Cube 核 |
| **优化重点** | Pipeline 双缓冲、Token 批处理、融合计算 |

**解读**：此表刻画算子的"形状"——纯 Vector 流水，无矩阵乘积，使优化策略完全聚焦在 element-wise 融合与访存掩盖上。变长 shape 通过 `cu_seqlens` 实现，提示后续 Tiling 需按 batch item 边界处理。

---

### 表 2：1.4 典型配置示例（原文逐字还原）

| 参数 | Prefill (FN) | 说明 |
|------|-------------|------|
| num_batches | 2 | batch 数量 |
| total_tokens | 2048 | 总 token 数 |
| dim | 2048 | hidden dimension |
| width | 4 | 卷积核大小 |
| state_len | 3 | 状态长度 (= width-1) |
| CORE_NUM | 24 | 核数量（dim 维度并行） |
| BATCH_TOKENS | 4 | 每次处理 token 数 |
| STAGES | 2 | 双缓冲 stage 数 |

**解读**：dim=2048 与 CORE_NUM=24 决定每核处理 base_dim=2048/24≈85 维（实际 base_dim 取 512 表明 dim 维度按 512 分块，与 24 核正交展开）。state_len=3=width-1 对应历史队列长度。

---

### 表 3：2.2 选型理由（原文逐字还原）

| 因素 | 分析 |
|------|------|
| **Pipeline 优化** | 需要手动控制双缓冲、set_flag/wait_flag 同步 |
| **融合计算** | 使用 `T.tile.mul_add_dst`、`T.tile.silu` 减少内存访问 |
| **Token 批处理** | 手动展开 4 个 token 的计算以隐藏延迟 |
| **内存规划** | 显式分配 x_buf/y_buf 用于 Pipeline |

**解读**：四个因素共同指向"自动优化能力不足"——元素级流水对编译器的自动融合/同步不可控，故必须降级到 Expert 模式换取对硬件流水线的精确编排。

---

### 表 4：3.1 核心计算步骤 → TileLang API 映射（原文逐字还原）

| 计算步骤 | PyTorch 参考 | TileLang API |
|---------|-------------|--------------|
| 加载 weight | `weight[0:width, d_offset]` | `T.copy(weight[i, d_offset], w*_ub)` |
| 加载历史 token | `x[hist_idx, d_offset]` | `T.copy(x[hist_global_idx, d_offset], hist*_ub)` |
| 加载初始状态 | `conv_state[ci, h, d_offset]` | `T.copy(conv_state[cache_line, h, d_offset], hist*_ub)` |
| 加载当前 token | `x[t, d_offset]` | `T.copy(x[global_start, d_offset], x_buf[cur, 0, :])` |
| **融合 mul + add** | `acc = w * x + acc` | `T.tile.mul_add_dst(acc, x, w)` |
| **silu activation** | `y = acc / (1 + exp(-acc))` | `T.tile.silu(y, acc)` |
| **状态递推计算** | 多步 mul/add | `T.tile.mul` + `T.tile.add` |
| 存储输出 | `y[t] = out` | `T.copy(y_buf[cur, i, :], y[out_base + i, d_offset])` |
| 加载最终状态 | `x[last_hist_idx, d_offset]` | `T.copy(x[seq_end - i, d_offset], save*_ub)` |
| 存储最终状态 | `conv_state[ci, h, d_offset]` | `T.copy(save*_ub, conv_state[cache_line, h, d_offset])` |

**解读**：此表为"语义等价翻译表"——左列是 PyTorch 直觉写法，右列是 TileLang 显式访存/计算原语。注意 `mul_add_dst` 与 `silu` 是**融合原语**，单次调用替代多条标量指令，这是性能的关键来源。

---

### 表 5：4.1 Prefill 模式输入张量（原文逐字还原）

| 张量 | Shape | Dtype | 说明 |
|------|-------|-------|------|
| x | `[symbol_total_len, symbol_dim]` | float16 | packed layout，所有序列拼接 |
| weight | `[width, symbol_dim]` | float16 | 卷积核 |
| conv_state | `[symbol_cache_lines, symbol_state_len, symbol_dim]` | float16 | 缓存状态 |
| cu_seqlens | `[num_batches + 1]` | int32 | 变长序列边界 |
| cache_indices | `[num_batches]` | int32 | 缓存索引 |
| initial_state_mode | `[num_batches]` | int32 | 初始状态标志 |

**解读**：x 使用 packed layout（所有序列拼接成一维），靠 `cu_seqlens` 索引分隔每个 batch，节省 padding 浪费。`conv_state` 三维结构 `[缓存行数, state_len, dim]` 表明 KV/状态按 cache line 组织。

---

### 表 6：4.2 Prefill 模式输出张量（原文逐字还原）

| 张量 | Shape | Dtype | 说明 |
|------|-------|-------|------|
| y | `[symbol_total_len, symbol_dim]` | float16 | 卷积输出 |
| conv_state | `[symbol_cache_lines, symbol_state_len, symbol_dim]` | float16 | 更新后状态 |

**解读**：输出 y 与输入 x 同形（packed）；`conv_state` 是 in-place 更新，prefill 末尾把每个 batch 的最后 `state_len` 个 token 写入对应 cache line，供 Decode 阶段复用。

---

### 表 7：5.1 Prefill Block 划分（原文逐字还原）

| 维度 | 策略 | 说明 |
|------|------|------|
| **Grid** | `num_batches * dim_num` | 按 batch 和 dim 二维分块 |
| **batch 分块** | 每个 batch item 独立处理 | |
| **dim 分块** | `dim_num = CORE_NUM = 24` | 每核处理 dim / 24 维度 |
| **token 批处理** | `BATCH_TOKENS = 4` | 每次处理 4 个 token |
| **双缓冲** | `STAGES = 2` | 2-stage pipeline |

**解读**：Grid 二维划分使 batch 维与 dim 维正交并行；每个核再内层做 token 维的 batched 迭代，构成 "batch × dim × token_ceil" 的三阶并行结构。

---

### 表 8：5.3 Tile Shape 设计（原文逐字还原）

| Buffer | Shape | 说明 |
|--------|-------|------|
| x_buf | `[STAGES, BATCH_TOKENS, base_dim]` | 输入双缓冲 |
| y_buf | `[STAGES, BATCH_TOKENS, base_dim]` | 输出双缓冲 |
| w* | `[base_dim]` | 权重 |
| hist* | `[base_dim]` | 历史 |
| state* | `[base_dim]` | 累加器 |

**解读**：所有 buffer 均以 `base_dim` 为最内维，方便沿 dim 维做向量化；x_buf/y_buf 多出 `STAGES × BATCH_TOKENS` 两维以承载流水线与批处理。

---

## 【公式解读】

### 公式 1：因果卷积递推定义（原文逐字保留）

```
对于每个 token t:
  1. hist = [x[t-width+1], x[t-width+2], ..., x[t-1]]  (历史 tokens)
  2. acc = weight[0] * hist[0] + weight[1] * hist[1] + ... + weight[width-2] * hist[width-2] + weight[width-1] * x[t]
  3. y[t] = silu(acc) = acc / (1 + exp(-acc))
  4. hist 更新: 移动窗口，添加 x[t]
```

**符号含义与作用**：

| 符号 | 含义 | 作用 |
|------|------|------|
| `t` | 当前 token 的时间步索引 | 遍历序列的所有位置 |
| `width` | 卷积核大小 | 决定"看到多少历史" |
| `hist` | 长度为 `width-1` 的历史 token 向量队列 | 滑动窗口的物理载体 |
| `x[t]` | 当前 token 在 dim 维上的向量（shape `[dim]`） | 当前输入 |
| `weight[i]` | 第 i 个卷积核权重（shape `[dim]`） | 学习到的滤波器参数 |
| `acc` | 累加器（shape `[dim]`） | 暂存加权求和结果 |
| `silu(·)` | Sigmoid Linear Unit 激活函数 | 非线性激活 |
| `y[t]` | 当前 token 的输出向量 | 写入 GM 供下游使用 |

**物理意义**：公式本质上是"将过去 `width-1` 步输入与当前步输入加权求和，再过 silu 激活"。因果性体现在：`y[t]` 只依赖 `x[≤t]`，不依赖未来，符合自回归生成需求。

### 公式 2：silu 激活定义（原文逐字保留）

$$y = \text{silu}(acc) = \frac{acc}{1 + \exp(-acc)}$$

**符号含义**：`acc` 为加权累加结果，`exp(-acc)` 是 sigmoid 的等价形式，分母 `1+exp(-acc)` 等价于 `sigmoid(-acc)` 的倒数（实际为 `1/sigmoid(acc)` 的等价变换）。整式为 Sigmoid Linear Unit，输出在负值附近轻微抑制、正值附近近似线性。

---

## 【关联】

### 与其他算子/模块的上下游关系

- **上游调用方**：线性注意力机制（Mamba、RWKV 等），算子位于 SSM（State Space Model）/线性注意力的"输入投影后、状态递推前"环节，是隐藏状态预计算的关键步骤。
- **同仓其他算子**：`tilelang-ascend` 仓中可能有 `causal_conv1d_update`（Decode 模式）、`selective_scan`（SSM 主算子）、`rms_norm` 等同框架算子。文档第 1.1 节提到"支持 Prefill（FN VARLEN）和 Decode（UPDATE）两种模式"，暗示 Decode 模式由配套算子实现。
- **硬件抽象层**：依赖 TileLang 提供的 `T.alloc_ub`/`T.copy`/`T.tile.*` API 与 Ascend NPU 的 MTE2/V/MTE3 三级流水线（`set_flag/wait_flag` 中出现的 `"mte2"/"v"/"mte3"` 即对应硬件队列）。
- **优化基线**：Pass 配置 `TL_ASCEND_AUTO_CV_COMBINE`、`TL_ASCEND_AUTO_SYNC`、`TL_ASCEND_MEMORY_PLANNING` 是框架级开关，与仓内其他 Expert 模式算子共享配置语义。

### 文档内部章节依赖

- 第 1.3 节定义计算特征 → 第 2 节选 Expert 模式的依据；
- 第 4 节内存规划 → 第 5 节 Tile Shape 设计的尺寸来源；
- 第 6 节 Kernel 代码中的 `cache_indices[0]`/`cache_indices[1]` 取值逻辑源自第 4.1 节的输入约定；
- 第 6.1 节 `block_end >= seqlen` 的 last-block 判断依赖第 5.1 节的 batch 划分策略。

---

## 【使用方法】

### 启用方式（原文已给出）

通过 `@tilelang.jit(out_idx=[-1], pass_configs=pass_configs_config)` 装饰器编译 kernel：

```python
pass_configs_config = {
    tilelang.PassConfigKey.TL_ASCEND_AUTO_CV_COMBINE: True,
    tilelang.PassConfigKey.TL_ASCEND_AUTO_SYNC: False,
    tilelang.PassConfigKey.TL_ASCEND_MEMORY_PLANNING: True,
}

@tilelang.jit(out_idx=[-1], pass_configs=pass_configs_config)
def _build_kernel(width, dim_num, num_batches, base_dim, dtype_str="float16"):
    ...
```

### Kernel 调用签名（原文第 6.1 节给出）

```python
kernel_func(
    x: T.Tensor((symbol_total_len, symbol_dim), dtype_str),
    weight: T.Tensor((width, symbol_dim), dtype_str),
    conv_state: T.Tensor((symbol_cache_lines, symbol_state_len, symbol_dim), dtype_str),
    cu_seqlens: T.Tensor((num_batches + 1,), "int32"),
    cache_indices: T.Tensor((num_batches,), "int32"),
    initial_state_mode: T.Tensor((num_batches,), "int32"),
    y: T.Tensor((symbol_total_len, symbol_dim), dtype_str),
)
```

### 配置项（原文涉及）

- **`width`**：卷积核大小，当前仅支持 `4`
- **`dim_num`**：dim 维并行分块数，等于 `CORE_NUM=24`
- **`num_batches`**：批次数
- **`base_dim`**：每个核实际处理的 dim 段大小（典型值 512）
- **`dtype_str`**：数据类型，默认 `"float16"`
- **`STAGES` / `BATCH_TOKENS`**：Pipeline 阶段数与 token 批大小（在文档中出现于配置示例与代码注释，但具体取值方式未在原文显式给出其来源定义）

### 原文未涉及部分

- 文档第 6.1 节末尾被截断（UB buffer 分配后即中止），完整的 kernel 主循环、Pipeline 同步序列、性能测试结果、Decode (UPDATE) 模式的完整实现，**原文未给出**。
- 性能数据（吞吐量、加速比）、错误处理、与其他框架算子的对接示例，**原文未涉及**。
