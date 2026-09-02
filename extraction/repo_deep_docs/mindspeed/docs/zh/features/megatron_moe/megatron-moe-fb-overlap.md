# MoE跨microbatch间AllToAll通信掩盖

> 仓 `mindspeed` · 路径 `docs/zh/features/megatron_moe/megatron-moe-fb-overlap.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed/docs/zh/features/megatron_moe/megatron-moe-fb-overlap.md

# MoE 跨 microbatch 间 AllToAll 通信掩盖 — 一体化深度解读

## 【定位】

本文档描述 MindSpeed（昇腾大模型加速库）在 MoE 模型训练中，通过跨 microbatch 间细粒度流水编排实现 AllToAll（A2A）通信掩盖的能力，重点解决 DeepSeek V3 等 MoE 大模型训练中 A2A 通信耗时高、难以在同 microbatch 内掩盖的关键瓶颈。

---

## 【技术要点】

1. **A2A 通信与计算依赖问题**：MoE 模型中 Expert 层的 Dispatch / Combine A2A 通信与计算存在顺序依赖，同 microbatch 内难以掩盖，是训练 MFU 的关键瓶颈。
2. **DeepSeek DualPipe 思路**：通过流水线两端同时输入 microbatch 并借鉴 ZeroBubble 思想进行 dw/dx 分离，缩减流水线 bubble；利用不同 microbatch 前反向无依赖的特性，双流编排计算与通信，实现 1F1B 阶段 A2A 通信全掩盖。
3. **单层前/反向阶段拆分**：前向拆为 Attention(F) → Dispatch(F) → MLP(F) → Combine(F)；反向拆为 Combine(B) → MLP(B) → Dispatch(B) → Attention(B)。通过跨 microbatch 编排，可形成 4 对相互掩盖组合（Attention(F)/Combine(B)、MLP(B)/Dispatch(F)、MLP(F)/Dispatch(B)、Attention(B)/Combine(F)）。
4. **SM 资源分配**：DeepSeek 团队为计算和通信分配固定 CUDA SM 数量，缓解资源抢占。MindSpeed 在昇腾上利用通信由 AICPU 下发、不消耗 cube 计算单元的特性，降低通信-计算并发的资源争抢影响。
5. **覆盖三阶段流水方案**：① 1F1B 阶段通过 dw/dx 分离实现 A2A **100%** 掩盖，并使用 Attention dw 掩盖 PP 通信；② Warmup/Cooldown 阶段通过共享专家与路由专家的层内自掩盖（共享专家正反向掩盖 Dispatch/Combine，路由专家 dw 掩盖 Dispatch）实现 A2A **50%** 掩盖；③ Megatron VPP 路径仅需在 warmup 阶段多做一个 warmup microbatch 即可实现跨 microbatch A2A 掩盖。
6. **端到端性能收益**：在 DeepSeek V3 上结合 DualPipeV，相比 MindSpeed 已有 `--moe-alltoall-overlap-comm` 特性，端到端性能提升 **10%**；1F1B 阶段 4 次 A2A 通信可被计算完全掩盖。

---

## 【关键机制与数据】

### 工作原理（1F1B 阶段跨 microbatch 编排）

- **原文**：单层前向 = Attention(F) → Dispatch(F) → MLP(F) → Combine(F)；反向 = Combine(B) → MLP(B) → Dispatch(B) → Attention(B)。
- **原文**：因正反向属于不同 microbatch，无顺序依赖，可形成掩盖对：Attention(F)⇔Combine(B)、MLP(B)⇔Dispatch(F)、MLP(F)⇔Dispatch(B)、Attention(B)⇔Combine(F)。
- **原文**：MindSpeed 在 1F1B 阶段通过分离调度 Expert 和 Attention 反向的 dw 与 dx 计算实现 A2A 全掩盖；同时利用 Attention 的 dw 计算掩盖 PP 通信，实现 1F1B 阶段通信全掩盖。

### Warmup / Cooldown 自掩盖

- **原文**：该阶段只有同 microbatch 的正/反向，无法跨 microbatch 掩盖，故启用层内自掩盖：
  - 正向：共享专家计算掩盖 Dispatch 通信
  - 反向：共享专家反向掩盖 Combine 通信
  - 路由专家的 dw 计算掩盖 Dispatch 通信

### VPP 路径

- **原文**：在传统 Megatron VPP 基础上，warmup 阶段比原始 VPP 多做一个 warmup microbatch，即可使中间红框部分进入跨 microbatch A2A 掩盖；相比 DualPipeV 实现更简单，A2A 掩盖效果相当。

### 性能数据

- **原文**：warmup/cooldown 阶段 A2A 通信 50% 掩盖；1F1B 阶段 A2A 通信 100% 掩盖。
- **原文**：在 DeepSeek V3 模型上结合 DualPipeV 相比 `--moe-alltoall-overlap-comm`，端到端性能提升 10%。
- **原文**：真实 DeepSeek-V3-671B 模型 profiling 显示，单层内 4 次 A2A 通信在 1F1B 阶段可被计算完全掩盖。
- **原文**：计算-通信并发对计算效率影响低（昇腾 AICPU 不占 cube 单元）。

### 硬件适配要点

- **原文**：MindSpeed 基于昇腾硬件特点设计实现；通信由 AICPU 下发，不消耗 cube 计算单元 → 并发对计算效率影响低。

---

## 【表格解读】

**原文无表格**。

（文档中涉及的参数与约束全部以 Markdown 列表 / 命令行形式给出，未提供表格形式的参数表或性能对比表。）

---

## 【公式解读】

**原文无公式**。

（文档以阶段命名（F/B × Attention/Dispatch/MLP/Combine）与"掩盖对"语义描述机制，未给出数学公式或伪代码形式的计算表达式。）

---

## 【关联】

- **../dualpipev.md**：本文档"基于 DualPipeV 和 Megatron VPP 的跨 microbatch 间 A2A 通信掩盖"小节显式链接到 DualPipeV 介绍文档，是该特性的上游/配套流水方案；同时本文 `--schedules-method dualpipev` 启动项也指向同一 DualPipeV 流水实现。
- **`--moe-alltoall-overlap-comm`**：MindSpeed 已有 A2A 掩盖特性，本特性是其深度演进（10% 端到端提升对比基线），并与之冲突、不能同时开启。
- **`--moe-hierarchical-alltoallv` / `--recompute-in-advance` / `--recompute-in-bubble` / `--swap-attention` / `--overlap-grad-reduce`**：均列为本文特性的冲突项或负面组合。
- **Megatron VPP（虚拟流水线并行）**：作为本文特性支持的另一条流水路径，与 DualPipeV 路径并列；要求配置 `--num-layers-per-virtual-pipeline-stage`、GBS > 1×DP×PP×MBS、noop layers 仅可置于最后一个 VPP stage 尾端等额外约束。
- **Expert/GroupedMatmul/MoE Dispatcher**：本文特性强依赖 `--moe-grouped-gemm`、强制 `--moe-token-dispatcher-type=alltoall`、仅支持 `--moe-zero-memory=level0`，并锁定 `--expert-tensor-parallel-size=1`，体现与底层 MoE 实现模块的紧密耦合。

---

## 【使用方法】

### 启动开关

- 加入 `--moe-fb-overlap` 启用本特性。
- 启用 DualPipeV 流水：加入 `--schedules-method dualpipev`。
- 启用 Megatron VPP 流水：在启动脚本中配置 `--num-layers-per-virtual-pipeline-stage`（如 `1` 或按模型结构调整）。
- 非 PP 场景：不配置 `--pipeline-model-parallel-size`，或设为 `--pipeline-model-parallel-size 1`。

### 可选性能/显存开关

- `--disable-fb-overlap-linear-dw-detach`：关闭普通 TP Linear 反向中的权重梯度分离；可节省显存但会带来性能损失。
- `--recompute-dense-mlp`：对 Dense 层 MLP 的 FC1 输出做激活重计算；降低激活显存占用，但增加一次 Dense FC1 前向计算。
- `--swap-dense-mlp`：将 Dense 层 MLP 的 FC1 输出异步换出到 CPU，反向前恢复到 NPU；与 `--recompute-dense-mlp` 互斥（不能同时使用）。

### 使用约束（强约束）

- **仅在 DeepSeek V3 场景验证**，其他 MoE 模型需进一步适配。
- 仅支持 `--moe-token-dispatcher-type=alltoall`（不支持 `allgather/alltoall_seq`）。
- 需设置 `--expert-tensor-parallel-size=1`（暂不支持专家 TP）。
- 暂不支持 Megatron MoE Token Drop&Pad；支持 Dropless 及 Drop 模式。
- 依赖 `--moe-grouped-gemm`（必须开启）。
- 仅支持 `--moe-zero-memory=level0`，不支持 `moe-zero-memory-num-layers`。
- 暂不支持异步 DP 通信掩盖，需关闭 `--overlap-grad-reduce`。
- 仅支持 Mcore Models，不能开启 `--use_legacy_models`。
- 不建议同时使用 `--swap-attention`（开启后性能劣化）。

### VPP 流水额外约束

- `GBS > 1 * DP * PP * MBS`。
- 若使用 noop layers，必须将其添加在模型尾部的最后一个 VPP stage。

### 冲突项（不能同时使用）

- `--moe-alltoall-overlap-comm`
- `--moe-hierarchical-alltoallv`
- `--recompute-in-advance`
- `--recompute-in-bubble`

## 图文联合解读

- `fb_overlap.png`: **图意解读**：上下双轨道展示单层流水编排，上轨道计算（112 SMs）按时序为MLP(B)→MLP(W)→MLP(F)→ATTN(B)→ATTN(W)→ATTN(F)，下轨道通信（20 SMs）依次为Dispatch(F→B)、Combine(F)、PP(F/B)、Combine(B)；交叉连线表示正反向chunk重叠，即ATTN(F)/ATTN(B)遮盖Combine(B/F)，MLP(B/F)遮盖Dispatch(F/B)，ATTN(W)遮盖PP通信。

**结论**：通过dw/dx分离与双流编排，1F1B阶段A2A通信实现100%掩盖，PP通信亦被遮盖。

**呼应论点**：直接佐证文档"MindSpeed 1F1B阶段A2A通信100%掩盖"的性能声明，并印证独立SM分配下计算通信几乎无资源争抢的硬件特性。
- `fb_overlap_npu.png`: 图示1F1B阶段单层内前反向细粒度流水排布：上行为计算（F前向、B反向、W权重梯度，含Attn、Perm、Unperm、RoutedExp的mm1/mm2及dw/dx分离），下行为A2A通信（disp/comb）及PP通信。

论证结论：通过双流编排实现通信与计算的时间对齐——A2A-comb(B)掩盖Unperm1-grad/Attn(F)，A2A-disp(F)掩盖RoutedExp，dw计算进一步隐藏A2A-disp(B)/comb(F)，Attn(W)掩盖PP通信，达成1F1B阶段A2A 100%掩盖。

对应文档"1F1B阶段A2A通信100%掩盖"的论断，是MindSpeed相对已有特性端到端提升10%的核心依据。
- `fb_overlap_profile.png`: **图文联合解读：**

1）图中内容：上方为计算时间轴，包含`a...`（前向）、`acl...`（计算kernel）、`aclnnGr...`（反向梯度）等密集小色块；下方为通信时间轴，三段`hcom_alltoallv_...`（蓝色、橙色、绿色）依次为Dispatch与Combine通信，与上方计算块在时间上交错。

2）技术结论：A2A通信与Attention/MLP正反向计算完全并发执行，验证了1F1B阶段A2A通信被计算全掩盖。

3）与文档关系：为"1F1B阶段A2A通信**100%**掩盖"提供DeepSeek-V3-671B真实profiling实证。
- `vpp_overlap.png`: **图文解读：**

1）图示为DualPipe双流调度时间线：4行代表4个PP阶段，蓝色为warmup、红色三角框内为1F1B阶段、绿/橄榄色为cooldown，每个数字cell表示一个microbatch的正/反向计算块；正反向microbatch交错排布，AllToAll通信被夹在对向计算单元间。

2）论证：双流编排实现1F1B阶段A2A通信100%掩盖。

3）对应文档论点：印证MindSpeed在昇腾上通过DualPipe式细粒度流水达成全掩盖的方案可行性。
