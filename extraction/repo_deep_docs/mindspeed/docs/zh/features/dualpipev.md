# DualPipeV

> 仓 `mindspeed` · 路径 `docs/zh/features/dualpipev.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed/docs/zh/features/dualpipev.md

# DualPipeV 特性文档深度解读

---

## 【定位】

本文档介绍昇腾大模型加速库 MindSpeed 中的 **DualPipeV 流水排布特性**，一种基于 DeepSeek DualPipe 改造的 V 形流水策略，用于在 MoE 模型训练场景中通过跨 microbatch 前反向通信掩盖降低 All2All 通信开销和优化显存，同时解决 DualPipe 的参数量冗余问题。

---

## 【技术要点】

1. **V 形流水排布**: DualPipeV 在流水上从 PP 维度截取 DualPipe 的一半，同时将模型在 PP 切分基础上进一步切分，流水呈 V 字形排布；算法启动规模只需 DualPipe 的一半。

2. **跨 microbatch 前反向通信掩盖**: 开启后可让 All2All 通信和 P2P 通信被无依赖关系的计算掩盖，依赖关联特性为 [MoE 跨 microbatch 前反向通信掩盖](megatron_moe/megatron-moe-fb-overlap.md)。

3. **cooldown 阶段 dw 分离 (可选)**: DualPipeV 中 PP 尾卡会连续计算 `PP_size` 个反向 stage，dw 计算完成前激活值不释放，会拉高 cooldown 阶段峰值内存；默认关闭以换性能降低重计算场景内存峰值，通过 `--dualpipev-dw-detach` 开启。

4. **气泡对比量化**: 以 PP4、10 个 microbatch 为例展示流水；与 1f1b、VPP 等方案相比，气泡表达式分别为 `(PP-1)*(F+B)`、`(PP-1)*(F+B)/v`、`(PP-1)*(F&B+B-W)-F`。

5. **Profiling 实测**: 在 DeepSeek-V3-671B 模型上采用 **PP8 TP2 EP32** DualPipeV 策略采集 PP 通信组 profiling 数据。

6. **兼容性与约束**: 模型层数应为 `PP*2` 的倍数；每个 PP 组的 micro batch 数至少为 `PP*2`；与 VPP、长序列并行、异步 DDP、swap-attention、tp_2d、`use_custom_fsdp` 不兼容。

---

## 【关键机制与数据】

### 工作原理（原文核心论述）

- **DualPipe 优势 → DualPipeV 改进路径**：DualPipe 流水可创造跨 microbatch 计算通信并行条件、实现稳定阶段 All2All 全掩盖，并在空泡比率、warmup 阶段激活显存上优于传统方案；DualPipeV 在此基础上从 PP 维度截取一半解决「每张卡上参数量翻倍」的冗余问题。原文：「DualPipeV 在流水上从 PP 维度截取 DualPipe 的一半，同时将模型在 PP 切分的基础上进行进一步地切分，流水呈 V 字形排布。它解决了 DualPipe 冗余参数的问题，算法启动规模也只需要 DualPipe 的一半。」

- **warmup/cooldown Zero Bubble 思想**：原文指出 DualPipe 在 warmup 和 cooldown 阶段都采用 Zero Bubble 思想中的 dw 分离来压缩气泡。

- **图示流程**：
  - 流水排布图（`figures/dualpipev.png`）：PP4、10 个 microbatch 场景下，0~9 与 10~19 代表同一张卡上的前向/反向 stage；绿色部分为不同 microbatch 的前反向并行区域。
  - dw 分离流水图（`figures/dualpipev_dw_detach.png`）：开启 dw 分离后的流水形态。
  - Profiling 图（`figures/dualpipev_profiling.png`）：PP 通信组实际采集的 profiling 视图。

### 性能数据

- 原文未提供具体加速比数字，仅通过公式表达气泡对比（见下节）。
- 原文定性结论：开启 DualPipeV + MoE 跨 microbatch 通信掩盖组合后「可对 MoE 的 All2All 通信进行掩盖，获得性能提升」；但「严重负载不均衡」场景下「可能会加剧 PP 负载不均，造成性能劣化」。
- 内存影响：开启 DualPipeV 可能造成内存峰值上升（因 output head 被分配到 PP rank0，静态+动态内存均上升）；但「设置模型后 N 层为空层」场景下尾 stage 在 PP rank0，峰值内存会降低。

---

## 【表格解读】

**原文表格：不同流水排布中 bubble 对比**

| 流水策略 | 气泡 |
| --- | --- |
| 1f1b | (PP-1)*(F+B) |
| VPP | (PP-1)*(F+B)/v |
| DualPipeV | (PP-1)*(F&B+B-W)-F |

**逐行解读：**

- **1f1b 行**：传统 1f1b 流水的气泡规模与 PP 规模、单个 microbatch 的「前向 (F) + 反向 (B)」计算量成正比，PP 越大气泡越严重。
- **VPP 行**：Virtual Pipeline Parallelism 通过将单个 stage 切分为 v 个虚拟 stage，将气泡缩小为原来的 1/v。
- **DualPipeV 行**：利用跨 microbatch 的「前反向并行（F&B）」能力，气泡表达式为 `(PP-1)*(F&B+B-W)-F`，其中 `B-W` 表示反向计算减去权重梯度 (dw) 部分，尾部的 `-F` 反映 V 形排布使首尾 stage 同卡带来的额外气泡压缩收益；这是三种策略中理论气泡最优的形式。

---

## 【公式解读】

原文气泡公式（采用 LaTeX 严格保留原符号形式）：

$$
\text{Bubble}_{\text{1f1b}} = (PP - 1) \times (F + B)
$$

$$
\text{Bubble}_{\text{VPP}} = \frac{(PP - 1) \times (F + B)}{v}
$$

$$
\text{Bubble}_{\text{DualPipeV}} = (PP - 1) \times (F \mathbin{\&} B + B - W) - F
$$

**符号含义：**

- `PP`：Pipeline Parallelism 规模（流水线并行度）。
- `F`：单个 microbatch 的前向计算耗时。
- `B`：单个 microbatch 的完整反向计算耗时。
- `B - W`：反向计算耗时减去其中「权重梯度 (dw) 计算」耗时，对应 Zero Bubble 思想中 dw 分离后被压缩的部分。
- `v`：VPP 虚拟 stage 数，将 1 个物理 stage 切为 v 段以摊薄气泡。
- `F & B`：跨 microbatch 前向与反向并行/重叠执行的等效时长，DualPipeV 借该并行能力缩小气泡。
- `-F`：V 形排布带来的末端 1 个 F 时长净收益，反映首尾 stage 同卡、流水首尾对齐带来的结构红利。

原文无其他独立公式；上述三式均出现在原文「不同流水排布中 bubble 对比」表格中。

---

## 【关联】

- **MoE 跨 microbatch 前反向通信掩盖**（`megatron_moe/megatron-moe-fb-overlap.md`）：本文档核心依赖特性。DualPipeV 的「绿色部分代表不同 microbatch 的前反向并行，开启跨 microbatch 前反向通信掩盖后，All2All 通信和 P2P 通信都可以被没有依赖关系的计算掩盖」直接依托该特性实现；启用 DualPipeV 时需通过 `--moe-fb-overlap` 同步开启。

- **DeepSeek DualPipe**（外部链接 `https://github.com/deepseek-ai/DualPipe`）：DualPipeV 的设计基线，本文描述其为「改进流水排布」，并继承其 Zero Bubble 思想（dw 分离）与「首尾 stage 同一张卡」带来的负载均衡可调性。

- **Zero Bubble 思想**：DualPipe 在 warmup/cooldown 阶段采用，DualPipeV 在 cooldown 阶段以可选项形式保留（`--dualpipev-dw-detach`）。

- **不兼容模块清单**：VPP、长序列并行、异步 DDP、swap-attention、tp_2d、`use_custom_fsdp` —— 均与 DualPipeV 存在兼容性冲突，使用时需规避。

- **MTP 模型结构**：原文提及「该流水排布天然亲和 MTP 模型结构」，说明 DualPipeV 在 MTP 类多 token 预测场景中有结构性优势，但未在文档中给出具体集成方式。

---

## 【使用方法】

原文「使用方法」章节明确给出以下启动脚本配置项：

1. **开启 DualPipeV 流水排布**：
   ```bash
   --schedules-method dualpipev
   ```

2. **开启 MoE 跨 microbatch 前反向通信掩盖**：
   ```bash
   --moe-fb-overlap
   ```

3. **开启 cooldown 阶段 dw 分离**（默认关闭，仅在愿意以性能换内存压缩时启用）：
   ```bash
   --dualpipev-dw-detach
   ```

4. **参数约束**：
   - 模型层数应设置为 `PP*2` 的倍数。
   - 每个 PP 组的 micro batch 数至少设置为 `PP*2`。

5. **不兼容声明**（原文 NOTE 与正文）：与 VPP、长序列并行、异步 DDP、swap-attention、tp_2d 暂不兼容；当前 `use_custom_fsdp` 与 `dualpipev` 不兼容。

## 图文联合解读

- `dualpipev.png`: **图文解读：**

1）图中展示了PP0-PP3四卡的V字形流水排布：PP0先做正向stage 0-9（橙色）后做反向（绿色），PP3倒置先做反向4F再做正向，中间PP1/PP2错位衔接，呈现V形对称结构；标注包括Forward、Backward、Backward for inputs/weights（dw分离）以及Forward&Backward overlap（绿底白字混合块）。

2）论证了DualPipeV通过V形排布创造跨microbatch的前反向并行条件（如14F+0B、0F+1B等重叠块），使All2All与P2P通信可被无依赖计算掩盖，且参数量仅为DualPipe的一半。

3）图直观对应文档"取DualPipe一半做V形排布"的论点，是其通信掩盖与内存优化优势的可视化依据。
- `dualpipev_dw_detach.png`: **图文联合解读：**

图示展示了PP4（PP0~PP3）下10个microbatch的V形流水时间线：PP0与PP3同卡分居首尾，PP1、PP2居中延迟启动，呈典型V字排布。每行方块表示该stage上的F/B/dw任务，绿色块（如"7F+13B"）代表跨microbatch的前反向并行，橙色块（16B~19B）为尾部纯反向段，白色为气泡；warmup阶段出现"10dw/11dw"等dw分离块。

该图论证了DualPipeV通过V形截取消除了DualPipe的冗余参数，同时绿色密集块证明跨microbatch前反向通信掩盖切实可行，首尾stage同卡也利于PP负载均衡，与文档"气泡更少、All2All全掩盖、亲和MTP"的论点一致。
- `dualpipev_profiling.png`: **图示解读：**

1）图中8行代表PP=8的8张卡，每行是时间轴上的流水调度，彩色块代表各microbatch的前向/反向stage，块大小不一（含标"hc/h/…"的大块代表含通信的较重计算），整体呈左收敛、右发散的"V字形"——左侧warmup阶段从两端卡向中间卡依次启动，右侧cooldown阶段对称反向退出，中间为稳态。

2）论证了DualPipeV的V形排布：首尾stage同卡，PP维度截取DualPipe一半即可实现跨microbatch前反向并行（绿/红块交错），从而掩盖All2All与P2P通信。

3）与文档论点对应——验证"DualPipeV解决DualPipe冗余参数、启动规模减半，同时保留All2All全掩盖与dw分离优化"的方案可行性。
