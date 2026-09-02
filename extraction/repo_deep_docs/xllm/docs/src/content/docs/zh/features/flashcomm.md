# flashcomm

> 仓 `xllm` · 路径 `docs/src/content/docs/zh/features/flashcomm.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/xllm/docs/src/content/docs/zh/features/flashcomm.md

# FlashComm 文档深度解读

## 【定位】

这篇文档介绍 xLLM 在 NPU Tensor Parallel 推理场景下 prefill 阶段的通信优化特性 FlashComm，目标是通过序列维度分片与 Matmul+ReduceScatter 融合算子两种手段，降低长输入 prefill 阶段 row-parallel 线性层后的通信开销与 kernel launch 成本。

---

## 【技术要点】

1. **两层优化能力**：核心层是序列维度分片（在 prefill 阶段按 TP rank 切分 token 序列，将 row-parallel 层后的 `all_reduce` 替换为 `reduce_scatter`，在边界处再 gather 还原）；增量层是 MMRS 融合算子（使用 torch_npu 的 `npu_mm_reduce_scatter_base`）。
2. **作用范围**：序列分片对所有 dtype（BF16 与各类量化）都生效；MMRS 融合当前覆盖 **BF16** 和 **w8a8_dynamic（int8 动态量化）** 两条路径。
3. **默认关闭与触发条件**：FlashComm 默认关闭，由 `--enable_flashcomm1` 总开关控制；运行时需满足 prefill 阶段、token 数 ≥ `flashcomm1_min_prefill_tokens`（默认 `8192`）、`cp=1` 三项条件才真正启用。
4. **回退机制**：当 MMRS 不适用（dtype 未接入融合内核、shape/bias 不满足、通信上下文缺失等）时，回退到普通 matmul + reduce_scatter，数值保持一致但失去 kernel 融合。
5. **适用场景**：NPU 后端；长输入 prefill（如 `8K/128`、`32K/1K` 等）；prefill 占端到端时延比例较高的场景。收益有限或不适用的场景包括 decode 阶段、短输入（低于阈值）、高 decode 占比场景、`cp>1` 场景。
6. **MMRS 通信模式与依赖**：MMRS 默认 `mmrs_comm_mode=aiv`，可切换为 `ai_cpu`；使用 `aiv` 时需加载包含 MMRS AIV 修复的 ops-transformers 9.1.0 或更高版本算子库。

---

## 【关键机制与数据】

**工作原理（执行流程，原文）**：
1. 请求进入 prefill 阶段后，运行时根据 token 数、并行配置和开关构造 FlashComm 上下文。
2. 当上下文生效时，输入 hidden states 会按序列维度切分到不同 TP rank。
3. 在 row-parallel 线性层后，将通信从 `all_reduce` 改为 `reduce_scatter`；若该层 dtype 支持 MMRS，则优先尝试 `npu_mm_reduce_scatter_base` 融合路径。
4. 如果 MMRS 不适用（例如 dtype 未接入融合内核、shape/bias 不满足、或通信上下文缺失），则回退到普通 matmul + reduce_scatter，功能与数值保持一致，只是少了 kernel 融合。
5. 在需要完整 hidden states 的边界处（如 attention 的 q_a/kv 投影、MoE 输入），再通过 gather 恢复完整序列。

**性能数据（原文，DeepSeek-V4-Flash W8A8C16，A3，EP16 / dp4 / tp4，ais-bench gsm8k 8K 输入，并发 32）**：
- baseline：TTFT **10211.2 ms**，TPOT **49.6 ms**
- `+ enable_flashcomm1`（并显式开启 MMRS）：TTFT **8840.9 ms**，TPOT **46.7 ms**
- FlashComm 带来约 **−13.4% TTFT**，其中序列分片贡献主要部分（约 **−11.8%**），MMRS 融合再贡献约 **−1.8%**。
- TPOT 的小幅改善来自 prefill 阶段更快带来的整体调度收益。

**关键算子（原文）**：`npu_mm_reduce_scatter_base`（来自 torch_npu），BF16 对应直接入口，w8a8_dynamic 对应 int8 融合入口；xLLM 侧只保留薄封装（输入校验、HCCL group 获取、`comm_mode` 选择、量化 scale 传递、日志记录）。

---

## 【表格解读】

### 表格 1：参数说明表（原文逐字还原）

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `enable_flashcomm1` | `false` | FlashComm 总开关 |
| `enable_mmrs_fusion` | `false` | 是否启用 Matmul + ReduceScatter 融合算子（仅在 `enable_flashcomm1=true` 时生效）。当前默认关闭，融合内核在部分 shape 上可能失败 |
| `flashcomm1_min_prefill_tokens` | `8192` | prefill token 数达到该阈值后才允许启用 FlashComm |
| `mmrs_comm_mode` | `aiv` | torch_npu MMRS 通信模式，可选 `aiv`、`ai_cpu`、`none` |

**逐行解读**：
- **`enable_flashcomm1` / `false` / FlashComm 总开关**：整篇特性的主控开关。关闭时所有 FlashComm 路径不进入；开启后还需运行时进一步判断 token 数与并行配置是否满足条件才会真正生效。
- **`enable_mmrs_fusion` / `false` / 是否启用 Matmul + ReduceScatter 融合算子**：是 `enable_flashcomm1` 之上的二级开关；只有在一级开关打开时才会被读取。当前默认关闭，原因是融合内核在部分 shape 上仍可能失败；问题修复后会考虑默认开启。
- **`flashcomm1_min_prefill_tokens` / `8192` / prefill token 数达到该阈值后才允许启用 FlashComm**：用于过滤短输入场景。原文指出默认值 `8192` 是偏保守的通用起点，不同模型的 FC1 收益拐点不同，建议在部署文档中给出经过验证的推荐值。
- **`mmrs_comm_mode` / `aiv` / torch_npu MMRS 通信模式，可选 `aiv`、`ai_cpu`、`none`**：控制 MMRS 底层通信实现方式；通常建议 `aiv`；若 AIV 路径在某些 shape 上出现 AICore 异常，可临时切换为 `ai_cpu` 规避。

### 表格 2：性能对比表（原文逐字还原）

| 配置 | TTFT (ms) | TPOT (ms) |
|------|-----------|-----------|
| baseline | 10211.2 | 49.6 |
| `+ enable_flashcomm1`（并显式开启 MMRS） | 8840.9 | 46.7 |

**逐行解读**：
- **baseline / 10211.2 / 49.6**：未启用 FlashComm 与 MMRS 的基线测量值，对应 DeepSeek-V4-Flash W8A8C16、A3、EP16/dp4/tp4、ais-bench gsm8k 8K 输入、并发 32 的设定。
- **`+ enable_flashcomm1`（并显式开启 MMRS）/ 8840.9 / 46.7**：同时开启序列分片与 MMRS 融合后的测量值。TTFT 较 baseline 下降约 13.4%，TPOT 下降 2.9 ms（小幅改善）。原文将 TTFT 改善拆分归因为：序列分片约 −11.8%，MMRS 融合再贡献约 −1.8%。

---

## 【公式解读】

原文无公式。

---

## 【关联】

文末未提供内部链接。文档中提及的关联点（仅基于原文叙述）：

- **NPU 后端 / torch_npu**：FlashComm 依赖 torch_npu 的 `npu_mm_reduce_scatter_base` 融合算子；MMRS `aiv` 路径需 ops-transformers 9.1.0 或更高版本算子库支持。
- **并行配置**：与 Tensor Parallel（TP）、Expert Parallel（EP）、Data Parallel（DP）、Context Parallel（CP）耦合；性能数据明确标注 EP16 / dp4 / tp4；`cp>1` 当前不启用 FlashComm。
- **其他层类型（用于边界 gather）**：在需要完整 hidden states 的边界处（attention 的 q_a/kv 投影、MoE 输入）需要 gather 还原完整序列。
- **上游/下游模块**：运行时根据 token 数、并行配置、开关构造 FlashComm 上下文；MMRS 路径需要 HCCL group 与量化 scale 传递。

---

## 【使用方法】

**启用方式（原文有）**：

最小启用（仅获得序列分片 + reduce_scatter 收益）：
```bash
--enable_flashcomm1=true
```

完整启用（包含 MMRS 融合增量收益）：
```bash
--enable_flashcomm1=true \
--enable_mmrs_fusion=true
```

**MMRS 通信模式临时切换（原文有）**：若某些 shape 在 AIV 路径出现 AICore 异常，可临时切换：
```bash
--mmrs_comm_mode=ai_cpu
```

**参数配置（原文有）**：详见上方「表格解读」中参数说明表的 4 项参数；其中 `flashcomm1_min_prefill_tokens` 默认 `8192`，原文建议在各模型部署文档中给出经过验证的推荐配置，而非依赖单一默认值。

**验证建议（原文有）**：
1. 对比 `enable_flashcomm1=false` 与 `enable_flashcomm1=true`；需评估 MMRS 增量时再额外加 `--enable_mmrs_fusion=true`。
2. 使用相同模型、相同并行配置、相同输入输出长度与相同并发。
3. 记录 TTFT、TPOT、prompt throughput、decode throughput、request throughput 与 latency。
4. 对长输入场景额外采集 profiling，确认 MMRS 路径命中（无 `FC1 MMRS skipped` 告警）。
5. 做小规模数值一致性检查，确认开启和关闭 FlashComm 的输出一致。
