# 专家并行动态负载均衡（数参互寻）

> 仓 `mindspeed` · 路径 `docs/zh/features/balanced_moe.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed/docs/zh/features/balanced_moe.md

# 专家并行动态负载均衡（数参互寻）— 深度解读

---

## 【定位】

本文档描述的是昇腾大模型加速库 mindspeed 中面向 MoE（混合专家）模型的**专家并行动态负载均衡特性**，核心解决专家并行（EP）训练中因令牌路由不均导致的"热专家过载、冷专家闲置"问题，通过"数据找计算 + 计算找数据"双向寻优机制实现负载再平衡，从而提升端到端训练吞吐量。

---

## 【技术要点】

1. **三大启动参数（命令原文）**：`--balanced-moe-experts --balanced-moe-hot-expert-num N --trans-hot-expert-group-num M`，三者缺一不可。
2. **热专家数量 N 约束（原文）**：`N` 默认值为 `3`，建议设置范围 `3-8`；必须满足 `N ≤ num_local_experts = num_experts / expert_model_parallel_size`。当总专家数 64、EP=8 时，`N` 最大为 8。
3. **传输分组数 M 约束（原文）**：默认值为 `3`，必须满足 `1 ≤ M ≤ N`，用于控制热专家参数广播的并发度。
4. **强依赖特性（原文）**：必须同时启用 `--moe-fb-overlap` 与 `--moe-grouped-gemm`；分发器仅支持 `--moe-token-dispatcher-type=alltoall`。
5. **并行与模型限制（原文）**：必须设置 `--expert-tensor-parallel-size=1`、关闭 `--overlap-grad-reduce`；仅支持 `--moe-zero-memory=level0`、不支持 `moe-zero-memory-num-layers`、需为 Mcore 架构（关闭 `--use_legacy_models`）、仅支持 Dropless 模式（不支持 Token Drop & Pad）、不建议同时启用 `--swap-attention`。
6. **虚拟流水线并行（VPP）约束（原文）**：必须满足 `GBS > 1 × DP × PP × MBS`；若使用 noop layers，需置于模型尾部最后一个 VPP 阶段。
7. **冲突特性（原文不可同启）**：`--moe-alltoall-overlap-comm`、`--moe-hierarchical-alltoallv`、`--recompute-in-advance`、`--recompute-in-bubble`。
8. **推荐场景（原文）**：EP ≥ 32 且负载显著不均；不推荐场景包括 EP ≤ 8、需严格确定性训练、DeepSeek-V3 减层 4 机 Atlas A3 场景（loss 误差小于 1%，小尺寸模型梯度累加误差可能放大）。

---

## 【关键机制与数据】

**"数参互寻"工作原理（原文五步）：**

- **步骤 1 实时监控**：在前向传播过程中，通过路由器获取全局令牌分布信息——这是后续决策的数据基础。
- **步骤 2 热专家识别**：基于全局负载信息，动态选出负载最重的 `N` 个专家作为"热专家"，这 `N` 是用户通过 `--balanced-moe-hot-expert-num` 指定的。
- **步骤 3 参数广播**：通过跨节点广播，让所有 EP Rank 都持有这 `N` 个热专家的**最新参数副本**，从而实现"计算找数据"——即任一节点都具备本地计算热专家的能力。
- **步骤 4 令牌重分发**：将原本要发送至**远端热专家**的令牌改为**本地计算**，从源头削减 All-to-All 通信量。
- **步骤 5 通信掩盖**：在流水线并行中精细调度不同 Micro-batch 的前向/反向阶段，把参数广播等新增通信"藏"在计算之下，做到通信开销的完全掩盖。

**性能收益的定性描述（原文）：** 在 EP ≥ 32 且负载不均显著的条件下，可"显著降低 All-to-All 通信的数据量"、"有效提高系统吞吐量"、"提升硬件资源利用率"。原文**未给出**任何具体的百分比、加速比、吞吐数字或基准测试数据，所有收益表述均为定性。

**非确定性说明（原文关键点）：** 文档明确指出本特性**不是二进制对齐**——其原因是 (a) 正向传播路径改变、梯度累加顺序改变、(b) 浮点加法不具结合律，即使设置 `--npu-deterministic`，同一训练多次运行也不会产生比特级完全一致的结果。这是一项功能层面而非缺陷层面的设计取舍。

---

## 【表格解读】

**原文无表格。** 原文中的所有参数信息均以项目符号列表形式呈现，无表格化结构。

---

## 【公式解读】

**原文无公式（无 LaTeX 表达、无伪代码形式的数学公式）。**

文档中出现的唯一具有"公式形态"的表达式是一个本地专家数计算说明（嵌入在参数说明段落中）：

```
num_local_experts = num_experts / expert_model_parallel_size
```

该表达式符号含义：
- `num_local_experts`：每个 EP Rank 上的本地专家数（亦即 `--balanced-moe-hot-expert-num` 的上限约束值）；
- `num_experts`：模型总专家数（全局）；
- `expert_model_parallel_size`：专家并行度（EP 大小）。

作用：作为参数 `--balanced-moe-hot-expert-num` 的合法性校验依据——给定总专家数与 EP 度后，可直接算出每个 Rank 上最多可维护多少个本地热专家。此外，原文还给出了一组数值示例：总专家 64、EP=8 → 每 Rank 8 个本地专家 → `--balanced-moe-hot-expert-num` 最大 8。

---

## 【关联】

文末提供的**内部链接信息为"无"**，因此严格依据原文无法建立本文与 mindspeed 其他特性/模块的官方交叉引用。但基于**原文正文内提及**的强依赖与冲突项，可梳理出本文与 mindspeed 中以下模块/特性的隐式上下游关系（均为原文显式提到，非臆造）：

- **强依赖（必须同启）**：
  - `--moe-fb-overlap`：前向反向重叠机制，是流水线通信掩盖的基础；
  - `--moe-grouped-gemm`：GroupedMatmul 算子，是热专家本地计算的核心算子；
  - `--moe-token-dispatcher-type=alltoall`：令牌分发器，是动态决策依赖的路由通路。
- **互斥（不可同启）**：
  - `--moe-alltoall-overlap-comm`：与本特性的通信掩盖机制路径冲突；
  - `--moe-hierarchical-alltoallv`：与本特性的 All-to-All 优化路径冲突；
  - `--recompute-in-advance` / `--recompute-in-bubble`：重计算调度与本特性的 Micro-batch 调度冲突。
- **隐含架构关联**：
  - 流水线并行（PP）/ 虚拟流水线并行（VPP）：本特性依赖其 Micro-batch 调度机制实现通信掩盖；
  - 数据并行（DP）：通过 GBS 与 DP×PP×MBS 的约束间接关联；
  - Mcore 架构模型：本文仅在 Mcore 下可用，与 `--use_legacy_models`（旧模型路径）对立。

---

## 【使用方法】

**启用命令（原文）：**

```bash
--balanced-moe-experts --balanced-moe-hot-expert-num N --trans-hot-expert-group-num M
```

**三个参数的角色（原文参数说明）：**

| 参数 | 作用 | 默认值 | 关键约束 |
|---|---|---|---|
| `--balanced-moe-experts` | 总开关，启用动态负载均衡算法 | 无（开关型） | 不设则整个特性不生效 |
| `--balanced-moe-hot-expert-num <N>` | 指定每层动态维护的热专家数量 N | `3` | `N ≤ num_experts / expert_model_parallel_size`；建议 3–8 |
| `--trans-hot-expert-group-num <M>` | 热专家参数广播的分组数量（控制广播并发度） | `3` | `1 ≤ M ≤ N` |

**正确启用本特性的最小必要配置清单（综合原文"使用限制"章节）：**

1. 启动参数：三参数同启（`--balanced-moe-experts`、`--balanced-moe-hot-expert-num N`、`--trans-hot-expert-group-num M`）；
2. 基础依赖：必须启用 `--moe-fb-overlap`、`--moe-grouped-gemm`、`--moe-token-dispatcher-type=alltoall`；
3. 并行配置：设置 `--expert-tensor-parallel-size=1`；关闭 `--overlap-grad-reduce`；
4. 内存与模型：`--moe-zero-memory=level0`；Mcore 架构（关闭 `--use_legacy_models`）；不使用 `moe-zero-memory-num-layers`；
5. MoE 模式：Dropless（不启用 Token Drop & Pad）；不建议同启 `--swap-attention`；
6. 冲突项规避：不要同时启用 `--moe-alltoall-overlap-comm`、`--moe-hierarchical-alltoallv`、`--recompute-in-advance`、`--recompute-in-bubble`；
7. 流水线约束：若使用 VPP，需满足 `GBS > 1 × DP × PP × MBS`；noop layers 必须置于模型尾部最后一个 VPP 阶段；
8. 场景适用：建议在 **EP ≥ 32 且负载显著不均**的训练场景下使用，其他场景（含严格确定性训练需求）不推荐。

原文未提供具体的 yaml/JSON 配置示例、benchmark 复现脚本或端到端性能数字，使用前需自行在目标模型与 EP 配置下进行收益验证。
