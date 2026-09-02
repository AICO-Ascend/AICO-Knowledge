# Recomputation

> 仓 `mindspeed-llm` · 路径 `docs/en/pytorch/features/mcore/recompute_relative.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-llm/docs/en/pytorch/features/mcore/recompute_relative.md

# MindSpeed LLM Recomputation Feature 深度解读

## 【定位】

这篇文档描述 MindSpeed LLM（昇腾 LLM 分布式训练框架）中**重计算（Recomputation / Gradient Checkpointing）能力**，解决 LLM 训练过程中 NPU 显存占用过高的问题，通过以"额外计算换显存"的策略，让用户在三种重计算粒度间按显存压力和性能诉求灵活取舍。

---

## 【技术要点】

1. **Full Recomputation（整段重计算）**：面向"显存极度紧张"的场景，仅保留 Transformer 层或层组的输入 activation，其余全部在反向时重算。开启条件：同时设置 `--recompute-granularity full` 与 `--recompute-method` 二选一。
2. **Uniform 方法**：`--recompute-method uniform` 时生效；将 Transformer 层划分为大小相等的若干层组，每组大小由 `--recompute-num-layers` 指定，每组只保存组入口的 input 和 activation。
3. **Block 方法**：`--recompute-method block` 时生效；仅对**最前** `--recompute-num-layers` 个 Transformer 层执行重计算，其余层不参与重计算。
4. **Selective Recomputation（选择性重计算，文档明确标注"recommended"）**：仅重计算 Transformer 中的 `core attention` 部分，保留"占用显存小但重算代价高"的 activation、重算"占用显存大但重算便宜"的 activation；通过 `--recompute-granularity selective` 启用。
5. **Activation Function Recomputation（激活函数重计算）**：通过 `--recompute-activation-function` 启用；并可通过 `--recompute-activation-function-num-layers ${num}` 限定参与重计算的层数。
6. **与 Full Recomputation 组合约束**：两者同时启用时，**仅支持 `--recompute-method block`**；同一层不能既参与 Full 又参与 Activation Function 重计算；执行优先级为"先算 Full 重计算层，再算 Activation Function 重计算层"；在**关闭流水线并行**的前提下，Full 层数 + Activation Function 层数应等于总层数。

---

## 【关键机制与数据】

- **工作原理（重计算的本质）**：文档给出的是 Megatron 系重计算的标准思路——前向时丢弃中间 activation，只保留少量 checkpoint；反向到对应层时再以一次额外的前向重新生成这些 activation，从而降低峰值显存。原文："full recomputation saves only the input activations for Transformer layers or layer groups, and it recomputes everything else."
- **数据流 / 划分逻辑**：
  - Uniform：按等分规则把层切成多个组（组大小 = `--recompute-num-layers`），**每组各保留一份 input + activation**（原文："Divides Transformer layers into groups of the equal size, with each group size set by `--recompute-num-layers`, and stores the input and activation values for each group"）。
  - Block：**只对最前 N 层**做重计算，剩余层按常规方式保存所有 activation（原文："Applies recomputation to the first `--recompute-num-layers` Transformer layers. The remaining layers do not participate in recomputation."）。
  - Selective：以 Transformer block 内**算子级粒度**区分，**只对 `core attention` 做重算**，其余 activation 保留（原文："It recomputes only the `core attention` part of the Transformer."）。
  - Activation Function Recomputation：以**激活函数算子**为粒度进行重算，可独立于上述两种粒度使用。
- **组合策略的优先级与互斥**：
  - Full + Activation 同时启用 → 同一层不能重复参与两类重计算（原文："no layer performs both full recomputation and activation function recomputation"）。
  - 执行顺序：Full 层 → Activation Function 层（原文："The execution priority is to compute the full recomputation layers first and then the activation function recomputation layers."）。
  - 在 **pipeline parallelism disabled** 时，两者层数之和应 = 总层数（原文："the sum of the full recomputation layer count and the activation function recomputation layer count should equal the total number of layers"）。
- **性能/显存数据**：原文未提供具体数字、benchmark 或显存节省百分比等量化指标。原文涉及"memory"与"expensive to recompute"的定性描述，但未给出数值。

---

## 【表格解读】

原文无表格。

---

## 【公式解读】

原文无公式。

---

## 【关联】

文档涉及以下外部关联资源（原文均以链接形式给出）：

1. **算法原理出处——Megatron Recomputation 论文**：<https://arxiv.org/abs/2205.05198>，文档将其作为 Full / Selective 重计算的"算法原理"参考来源，属于上游方法论。
2. **同仓库的 Activation Function Recomputation 专题**：<https://gitcode.com/Ascend/MindSpeed/blob/master/docs/zh/features/activation-function-recompute.md>，提供更详细的激活函数重计算说明，本文档作为入口/索引指向它。
3. **与 Pipeline Parallelism 的耦合**：文档中"关闭流水线并行时层数加和等于总层数"的约束说明，Recomputation 策略与流水线并行存在交互，需联合规划切分层数。
4. **与训练主流程的关系**：Recomputation 作用于 Transformer block 内部的 activation 生命周期，与分布式训练（TP/PP/DP）、优化器状态 offload、ZeRO 等显存优化手段处于**互补**位置，但本文档未展开互操作细节。

> 注：本文档内部未提供其他同文档站内的导航链接（即"内部链接: (无)"）。

---

## 【使用方法】

| 启用方式 | 命令 / 参数 | 关键行为 |
|---|---|---|
| 启用 Full Recomputation | `--recompute-granularity full` + `--recompute-method {uniform \| block}` | 二选一决定均匀分组或仅对前 N 层 |
| Uniform 模式下指定组大小 | `--recompute-num-layers` | 每组包含的 Transformer 层数 |
| Block 模式下指定参与层数 | `--recompute-num-layers` | 仅对最前 N 层做重计算 |
| 启用 Selective Recomputation（推荐） | `--recompute-granularity selective` | 仅重算 `core attention` |
| 启用 Activation Function Recomputation | `--recompute-activation-function` | 针对激活函数粒度重算 |
| 指定激活函数重计算的层数 | `--recompute-activation-function-num-layers ${num}` | 限定参与重算的层数 |
| Full + Activation 组合 | 上述两者同时开启 + `--recompute-method block` | 同一层不可重复参与；Full 层先执行、Activation 层后执行；非流水线并行时层数之和 = 总层数 |

原文未涉及 YAML/JSON 配置文件路径、环境变量、或者具体的启动脚本样例；启用方式仅以命令行参数（CLI flag）形式给出。
