# flashcomm

> 仓 `xllm` · 路径 `docs/src/content/docs/en/features/flashcomm.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/xllm/docs/src/content/docs/en/features/flashcomm.md

# FlashComm 文档深度解读

## 【定位】

本文档描述 xLLM 在 NPU Tensor Parallel (TP) 推理中、面向 **prefill 阶段** 的通信优化方案 **FlashComm** —— 通过把 token 序列按 sequence 维度切分到各 TP rank, 用 `reduce_scatter` 替代 row-parallel 层后的 `all_reduce`, 并在支持的 dtype 上进一步以 Matmul + ReduceScatter (MMRS) 融合算子降低 kernel launch 与调度开销, 从而削减长输入 prefill 的通信成本、降低 TTFT。

---

## 【技术要点】

1. **两层叠加架构**: FlashComm 由"sequence-dim 切分(核心层)"与"MMRS 融合算子(增量层)"两层组成。核心层**覆盖所有 dtype**(BF16 与全部量化路径), 是提速的主来源; MMRS 增量层目前仅覆盖 **BF16** 与 **w8a8_dynamic (int8 dynamic)** 两种 dtype。
2. **all_reduce → reduce_scatter 替换**: 在 row-parallel linear 层后, 把聚合通信从 `all_reduce` 切换为 `reduce_scatter`, 仅在真正需要完整 hidden states 的边界(如 attention q_a/kv projection、MoE input)通过 `gather` 把全序列拼回, 避免每次都做全局聚合。
3. **MMRS 融合算子**: 在支持的 row-parallel 层用 `torch_npu.npu_mm_reduce_scatter_base` 把 matmul 与 reduce_scatter 融合为单次 launch; xLLM 端**仅保留薄壳**(输入校验、HCCL group 获取、`comm_mode` 选择、quant-scale 透传、日志), 不重写 kernel。
4. **运行门槛**: 默认关闭, 由 `--enable_flashcomm1` 主开关统一启用, 仅当"prefill 阶段 & token 数 ≥ `flashcomm1_min_prefill_tokens`(默认 **8192**) & `cp=1`"三个运行时条件**同时满足**时才激活, 否则回退到原始执行路径。
5. **MMRS 增量开关**: `enable_mmrs_fusion` 仅在 `enable_flashcomm1=true` 时才被读取, **默认关闭**(因融合 kernel 在某些 shape 上仍可能失败)。在已验证稳定 shape 上可显式开启以获得额外 ~−1.8% 的 TTFT 收益。
6. **回退策略明确**: MMRS 不适用时(无对应融合 kernel、shape/bias 不支持、缺少通信上下文等)回退到"普通 matmul + reduce_scatter", 数值上与原路径一致, 仅缺少 kernel 融合带来的额外开销削减。

---

## 【关键机制与数据】

### 工作原理(数据流)

1. 请求进入 prefill → 运行时根据 **token 数 + 并行配置 + 开关** 构建 FlashComm context;
2. context 激活时, input hidden states 沿 **sequence 维度**切分到 TP 各 rank;
3. 每次 row-parallel linear 后, 通信从 `all_reduce` 改为 `reduce_scatter`; 若 layer dtype 支持 MMRS, 优先尝试 `npu_mm_reduce_scatter_base` 融合路径;
4. 若 MMRS 不适用 → 回退到 matmul + reduce_scatter(功能与数值等价, 仅失去 fusion);
5. 在需要完整 hidden states 的边界(原文: "e.g. attention q_a/kv projections, MoE input"), 通过 gather 恢复全序列。

### 性能数据(原文: 引用性能表)

测试配置(原文):
- 模型: DeepSeek-V4-Flash W8A8C16
- 硬件/拓扑: A3, EP16 / dp4 / tp4
- 基准: ais-bench gsm8k 8K input
- 并发: 32

| 配置 | TTFT (ms) | TPOT (ms) |
|---|---|---|
| baseline | 10211.2 | 49.6 |
| + enable_flashcomm1 (with MMRS 显式开启) | 8840.9 | 46.7 |

原文给出的归因:
- **TTFT 整体下降 ~ −13.4%**
- 其中 sequence sharding(核心层)贡献 ~**−11.8%** (占绝大部分)
- MMRS fusion(增量层)在核心层之上额外贡献 ~**−1.8%**
- TPOT 的小幅下降归因于 prefill 加速改善整体调度, 而非 FlashComm 直接优化 decode

---

## 【表格解读】

### 表 1: 参数配置表(原文逐字还原)

| Parameter | Default | Description |
|---|---|---|
| `enable_flashcomm1` | `false` | FlashComm master switch |
| `enable_mmrs_fusion` | `false` | Enables the Matmul + ReduceScatter fused operator (only read when `enable_flashcomm1=true`). Off by default because the fused kernel can fail on some shapes |
| `flashcomm1_min_prefill_tokens` | `8192` | Minimum prefill token count before FlashComm activates |
| `mmrs_comm_mode` | `aiv` | torch_npu MMRS communication mode: `aiv`, `ai_cpu`, or `none` |

**逐行解读:**

- **`enable_flashcomm1` (默认 `false`)**: FlashComm 总开关, 也是启用核心层(sequence 切分 + `reduce_scatter` 替换)的唯一入口。该开关关闭时, 不论后续子开关取值如何, FlashComm 都不参与执行。
- **`enable_mmrs_fusion` (默认 `false`)**: MMRS 增量融合开关, **仅在 `enable_flashcomm1=true` 时才被读取**; 默认关闭, 因为融合 kernel 在部分 shape 上仍可能失败。原文提示应在"已验证稳定 shape"上显式开启以获取额外增益。
- **`flashcomm1_min_prefill_tokens` (默认 `8192`)**: FlashComm 激活的最小 prefill token 数阈值。低于该阈值时 FlashComm 完全不会触发(从而避免短输入下"切分/gather/调度"开销抵消通信收益)。原文明确指出该阈值的 FC1 盈亏点随模型参数量变化, 默认 8192 是保守通用起点, 建议在各模型部署文档中给出经过验证的推荐配置。
- **`mmrs_comm_mode` (默认 `aiv`)**: torch_npu MMRS 的通信模式, 可选 `aiv` / `ai_cpu` / `none`。原文建议一般保持 `aiv`, 若 AIV 路径在某些 shape 触发 AICore 错误可临时切到 `ai_cpu`; 启用 AIV 路径要求 **ops-transformers ≥ 9.1.0** 的算子库(含 MMRS AIV 修复)。

### 表 2: 参考性能表(原文逐字还原)

| Config | TTFT (ms) | TPOT (ms) |
|---|---|---|
| baseline | 10211.2 | 49.6 |
| `+ enable_flashcomm1` (with MMRS explicitly enabled) | 8840.9 | 46.7 |

**逐行解读:**

- **baseline 行**: 未启用 FlashComm 时, 10211.2 ms TTFT / 49.6 ms TPOT, 作为对比基线。
- **`+ enable_flashcomm1` (with MMRS explicitly enabled) 行**: 同时打开主开关与 MMRS 融合开关后的全量收益, TTFT 降到 8840.9 ms、TPOT 降到 46.7 ms。结合文档文字, 整体 −13.4% TTFT 中约 −11.8% 来自 sequence sharding 核心层, 约 −1.8% 来自 MMRS 增量层。

---

## 【公式解读】

原文无公式。

---

## 【关联】

原文未给出内部交叉链接(本文档"内部链接"标注为"无")。基于文档自身语义可识别的依赖与上下游如下:

- **上游/前提**: 
  - **TP (Tensor Parallel) 推理**: FlashComm 直接修改 TP 下 row-parallel linear 之后的通信模式, 没有 TP 部署就没有 row-parallel layer。
  - **NPU 后端 + torch_npu**: MMRS 融合依赖 `torch_npu.npu_mm_reduce_scatter_base` 算子库, 要求 **ops-transformers ≥ 9.1.0**。
  - **Attention / MoE 子模块**: 文档明确指出 sequence 切分后的全序列 `gather` 边界出现在 attention 的 `q_a/kv projection` 与 `MoE input` 等需要完整 hidden states 的位置。
- **平行/同类**: 
  - 与 **Context Parallel (cp)** 互斥: 文档明确"`cp > 1` 时当前未启用", 即 FlashComm 不在 cp>1 拓扑下生效。
  - 与 **量化路径**: 核心层与"BF16 + 所有量化路径"兼容, MMRS 增量层仅覆盖 BF16 与 w8a8_dynamic(int8 dynamic)两条路径, 其他量化 dtype 只能享受核心层收益。
- **不作用的下游**: 
  - **Decode 阶段 / TPOT**: 文档明确 FlashComm 只优化 prefill, decode 不是其目标, 长输出/重 decode 场景下端到端收益有限。
- **配置耦合**: `enable_mmrs_fusion` 在语义上依赖于 `enable_flashcomm1=true` 才生效, 二者构成"主开关 + 增量开关"的两层配置关系。

---

## 【使用方法】

### 启用方式(原文给出)

1. **只启用核心层(sequence 切分 + reduce_scatter 替换)**:
   ```bash
   --enable_flashcomm1=true
   ```
2. **在核心层之上叠加 MMRS 融合(增量)**:
   ```bash
   --enable_flashcomm1=true \
   --enable_mmrs_fusion=true
   ```

### 配置项与默认(原文)

| 参数 | 默认值 | 说明 |
|---|---|---|
| `enable_flashcomm1` | `false` | FlashComm 总开关 |
| `enable_mmrs_fusion` | `false` | MMRS 融合算子开关(仅在主开关开启时被读取) |
| `flashcomm1_min_prefill_tokens` | `8192` | FlashComm 激活的最小 prefill token 数阈值 |
| `mmrs_comm_mode` | `aiv` | MMRS 通信模式: `aiv` / `ai_cpu` / `none` |

### 选型与调优建议(原文要点)

- **适用场景**: NPU 后端、长输入 prefill(≥ 默认 8192 token)、prefill 在端到端占比大的场景(如 8K/128、32K/1K 长 prompt)。
- **不建议场景**: Decode 阶段、短输入、decode-heavy 长输出、`cp > 1`。
- **`flashcomm1_min_prefill_tokens`**: 默认 8192 为保守通用值, 实际最佳阈值随模型参数量变化, 建议参考各模型部署文档中的已验证推荐配置, 而不是使用单一全局默认值。
- **`mmrs_comm_mode`**: 一般保持 `aiv`; 若 AIV 路径在某 shape 报 AICore 错误, 可临时切到 `ai_cpu` 绕开。`aiv` 路径依赖 ops-transformers ≥ 9.1.0 的算子库(含 MMRS AIV 修复)。

### 验证流程(原文给出 Validation checklist)

1. 对比 `enable_flashcomm1=false` 与 `enable_flashcomm1=true`; 若要评估 MMRS 增量, 进一步加 `--enable_mmrs_fusion=true` 做第三组对比。
2. 控制变量: 同一模型、同一并行配置、同一输入/输出长度、同一并发。
3. 记录指标: TTFT、TPOT、prompt throughput、decode throughput、request throughput、latency。
4. 长输入场景需采集 profiling, 确认 MMRS 路径被命中(无 `FC1 MMRS skipped` 警告)。
5. 跑一次小规模数值一致性校验, 确认 FlashComm 开/关前后输出一致。
