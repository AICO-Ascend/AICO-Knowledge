# High-Dimensional Tensor Parallelism

> 仓 `mindspeed-llm` · 路径 `docs/en/pytorch/features/mcore/tensor_parallel_2d.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-llm/docs/en/pytorch/features/mcore/tensor_parallel_2d.md

# High-Dimensional Tensor Parallelism (二维张量并行) 文档深度解读

## 【定位】

本文档描述了 MindSpeed-LLM 中"高维张量并行"（具体为 2D Tensor Parallelism）特性的启用方式与约束，面向大集群规模 + 大 TP 域（TP domain）的超大规模 LLM 训练场景（如 Llama-3-405B on A3、TP=16）。

## 【技术要点】

1. **2D TP 开启开关**：在训练脚本中加入 `--tp-2d`，并通过 `--tp-x N1` 与 `--tp-y N2` 指定二维切分尺寸，要求 `tp = N1 * N2`，且 `N1 > 1` 且 `N2 > 1`。
2. **推荐配置示例**：当 `TP=16` 时，推荐 `tp-x=8`、`tp-y=2`（用于 Llama-3-405B on A3）。
3. **前向通信隐藏**（三选一）：
   - `--enable-overlap-ag-with-matmul`：将 all-gather 通信隐藏在 linear 层前向 matmul 之后；
   - `--enable-overlap-matmul-with-rs`：将 matmul 计算隐藏在 reduce-scatter 通信之后；
   - `--coc-fused-kernel`：算子级融合 matmul + all-gather + reduce-scatter，依赖 ATB 加速库。
4. **反向通信隐藏**：`--enable-backward-overlap-ag-with-matmul` 在 linear 层反向求梯度时将 all-gather 隐藏在 matmul 之后，同样依赖 ATB 加速库。
5. **互斥与依赖**：上述三个前向优化参数**互斥**（同时只能开启一个）；后向 overlap 优化与 `--coc-fused-kernel` 均依赖 ATB 库。
6. **使用约束**：
   - 与 `--sequence-parallel`、`--use-fused-rmsnorm` **不兼容**，需先关闭；
   - 暂不支持 MoE 模型及相关特性；
   - 仅推荐用于超大规模 dense 模型 + 大 TP 域场景，小模型/小 TP 可能反而降低性能；
   - 融合算子要求 **CANN 8.0.1.B020+**，且需安装 CANN-NNAL 并执行额外集成步骤；
   - 融合算子场景当前仅支持 `micro-batch-size=1`。

## 【关键机制与数据】

- **二维切分原理（原文）**：将传统一维 TP 在 x 轴和 y 轴上同时切分张量，使总 TP 规模可放大到 `N1 * N2`；要求 `N1 > 1` 且 `N2 > 1`，否则退化为普通 1D TP。
- **典型数据点（原文）**：训练 Llama-3-405B on A3 时使用 `TP=16`，对应 `tp-x=8`、`tp-y=2`。
- **通信模式（原文）**：linear 层前向涉及 `all-gather` 与 `reduce-scatter` 两类集合通信；反向涉及与 all-gather 关联的梯度计算。
- **三层优化策略（原文）**：
  1. 算子级融合（`--coc-fused-kernel`）—— 算子层面把 matmul、AG、RS 融合，依赖 ATB 加速库；
  2. 流水线式 overlap（`--enable-overlap-ag-with-matmul` / `--enable-overlap-matmul-with-rs`）—— 通过调度将通信与计算时间重叠；
  3. 反向 overlap（`--enable-backward-overlap-ag-with-matmul`）—— 同样依赖 ATB。
- **性能权衡（原文）**：文档明确指出 "smaller models and smaller TP settings may reduce performance"，并强调 `tp-x` / `tp-y` 需要根据 compute efficiency 与 communication group partitioning 做调优。

## 【表格解读】

原文无表格。

## 【公式解读】

原文唯一可视为"关系式"的约束为：

$$tp = N_1 \times N_2, \quad N_1 > 1, \quad N_2 > 1$$

- `tp`：总张量并行度（即常规参数 `--tensor-model-parallel-size` 的值）。
- `N1`：x 轴切分尺寸，由 `--tp-x` 指定。
- `N2`：y 轴切分尺寸，由 `--tp-y` 指定。
- 该式的作用：将一维 TP 分解为二维 (N1, N2) 的笛卡尔积网格；只有当两个维度都 > 1 时才真正形成 2D 切分拓扑，否则退化为普通 TP。

## 【关联】

- **同类特性冲突**：与 `--sequence-parallel`（序列并行）、`--use-fused-rmsnorm`（融合 RMSNorm）**互斥**，需先关闭。
- **依赖特性 / 库**：
  - `--coc-fused-kernel`、`--enable-backward-overlap-ag-with-matmul` 依赖 **ATB 加速库**；
  - `--coc-fused-kernel` 额外依赖 **CANN ≥ 8.0.1.B020** 以及 **CANN-NNAL** 组件及其"额外集成步骤"。
- **不兼容特性**：MoE 模型及 MoE 相关特性（文档明确指出尚未支持）。
- **上游说明**：文档开头引用了 [High-Dimensional Tensor Parallelism 中文介绍](https://gitcode.com/Ascend/MindSpeed/blob/master/docs/zh/features/tensor-parallel-2d.md) 作为更详细的概念性参考；本文档的英文版聚焦于**用法与约束**，不重复原理。
- **典型下游模型 / 硬件组合**：Llama-3-405B（dense 模型）+ A3 集群 + TP=16 场景。

## 【使用方法】

启用 2D TP 的最小脚本片段（原文示例）：

```bash
--tensor-model-parallel-size 16 \
--tp-2d \
--tp-x 8 \
--tp-y 2 \
```

完整参数清单（原文逐项摘录）：

| 参数 | 作用 | 备注 |
|---|---|---|
| `--tp-2d` | 启用 2D 张量并行 | 基础开关 |
| `--tp-x N1` | 设置 x 轴切分尺寸 | `N1 > 1` |
| `--tp-y N2` | 设置 y 轴切分尺寸 | `N2 > 1` |
| `--enable-overlap-ag-with-matmul` | 前向：AG 隐藏在 matmul 之后 | 与下面两个前向优化互斥 |
| `--enable-overlap-matmul-with-rs` | 前向：matmul 隐藏在 RS 之后 | 与另外两个前向优化互斥 |
| `--coc-fused-kernel` | 前向：算子级融合 matmul+AG+RS | 与前两项互斥；依赖 ATB；需 CANN ≥ 8.0.1.B020；仅支持 `micro-batch-size=1` |
| `--enable-backward-overlap-ag-with-matmul` | 反向：AG 隐藏在 matmul 之后 | 依赖 ATB 加速库 |

> 互斥规则（原文 Note）：`--enable-overlap-ag-with-matmul`、`--enable-overlap-matmul-with-rs`、`--coc-fused-kernel` 三者**同时只能启用一个**。

启用前需确认的关闭项（原文）：`--sequence-parallel`、`--use-fused-rmsnorm`，以及确认模型不是 MoE。
