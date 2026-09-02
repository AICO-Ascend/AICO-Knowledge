# Model Architecture Report Template

> 仓 `agent-skills` · 路径 `official/Common/ascend-profiling-anomaly/references/architecture_report_template.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/agent-skills/official/Common/ascend-profiling-anomaly/references/architecture_report_template.md

# 「Model Architecture Report Template」一体化深度解读

---

## 【定位】

**这篇文档定义了一套标准化的"模型架构报告"模板与产出方法论，用于在昇腾 NPU profiling 数据之上逆向重建被测模型的完整执行架构（层数、层类型、并行策略、通信流水线），使不熟悉该模型的读者能够从 profiling 痕迹中读出"它是什么模型、它如何执行"。**

---

## 【技术要点】

1. **报告定位为独立 Markdown 产物**：与"异常报告"分工明确——异常报告回答"什么看起来不自然"，架构报告回答"这是什么模型、它如何执行"；两者配套产出但内容互不重叠。
2. **FIA 作为首要结构标记**：使用 `FusedInferAttentionScore (FIA)` 调用次数与时长作为层数与阶段划分的主证据——prefill FIA 时长 > 10ms，decode FIA 时长 < 1ms，据此切分阶段并计算每 pass 层数。
3. **强制 10 节固定结构**：Configuration Context → Architecture Determination → Forward Pass Boundaries → Layer Classification → Cross-Verification → Per-Layer Sub-Structure → Decode Phase Analysis → Communication Pipeline → Layer-to-Layer Variation → Architecture Summary，顺序不可变。
4. **三类典型层模式**：Dense（无 MoE 路由，attention→projection→norm→FFN 直接 MatMul）、MoE+DFC（中间层用 DispatchFFNCombine 融合专家路由+计算）、MoE+GMM（最后一层用 GroupedMatmul 替代 DFC，并承担 output head、sampling、decode prep）。
5. **缩进树状 kernel 序列**：对每种层类型用 ASCII 缩进树展示算子精确执行顺序，并标注 wall time、stream、dominant op、share、anomaly（如 layer 0 的 warm-up overhead）。
6. **流-流水线重叠可视化**：用 ASCII 流水线图展示 `reduce_scatter` / `allgather` 等通信算子与下一层 FIA 的 stream 重叠，并量化 `kernel_sum >> wall_ms` 的原因（多 stream 隐藏）。

---

## 【关键机制与数据】

### 工作原理

**报告生成流程**：以 profiling 目录名为种子（如 `0313_dp2_tp8_ep_100k_1k_bs10` 表明 DP2×TP8+EP、prefill 100K、decode 1K、bs10），从目录名+profiling metadata 抽取并行配置、序列长度、batch size、capture span；再以 kernel trace 重建执行时间线。

**FIA 计数驱动的层数推导**（原文 4.2）：
- 步骤 1：count total FIA invocations
- 步骤 2：按时长二分（>10ms 归 prefill，<1ms 归 decode）
- 步骤 3：相除得到 layers/pass 与 passes/capture
- 步骤 4：通过 timestamp gap 定位 prefill→decode 相变点
- 步骤 5：evidence chain 表（Evidence | Value | Interpretation）

**层类型判定机制**：通过检查每层 kernel 序列中是否出现 `DispatchFFNCombine` / `GroupedMatmul` / `MoeGatingTopK` / `alltoallv` 等特征算子来归类（原文 4.4 末）。

**Decode 阶段成本翻转**：原文 4.7 显式给出 FIA 从 28ms 骤降至 0.2ms（数值直接出现在示例文本中），成本主体由 all-to-all 通信接管（EP 模型），原文解释为"latency-bound vs bandwidth-bound"导致 profile 差异。

**通信-计算重叠**：原文示例 ASCII 图显示 `Layer N` 的 FIA 28.5ms / post-FIA 12ms 与 `Layer N+1` 的 FIA 在 stream 82 上的 `reduce_scatter 29.9ms` 重叠，导致 kernel 时间总和远大于 wall time。

### 性能数据（原文出现）

| 数据点 | 数值 | 出处 |
|---|---|---|
| Prefill FIA 时长阈值 | > 10ms | 原文 4.2 |
| Decode FIA 时长阈值 | < 1ms | 原文 4.2 |
| FIA 时长跳变示例 | 28ms → 0.2ms | 原文 4.7 |
| 跨层 DFC 时长方差示例 | 5.4ms – 14.8ms | 原文 4.9 |
| Reduce-scatter 时长示例 | 29.9ms on stream 82 | 原文 4.8 |
| 目录名示例 | `dp2_tp8_ep_100k_1k_bs10` | 原文 §2 |

### 数据流

`profiling_dir_name` → 解析并行/序列/bs → kernel trace (timestamps + stream id + op name + dur) → FIA 二分切分 → 每层 kernel 序列聚合 → 层类型分类 → 跨验证 → ASCII 可视化。

---

## 【表格解读】

### 表 1：层类型分类模板（原文 4.4）

| Layer Type | Layers | Count | Characteristics |
|---|---|---|---|
| Dense | 0–N | K | No MoE routing; attention → projection → norm → FFN (direct MatMul) |
| MoE+DFC | N+1–M | J | Full MoE layers with DispatchFFNCombine for fused expert routing+compute |
| MoE+GMM | M+1 (last) | 1 | MoE with GroupedMatmul instead of DFC; includes output head, sampling, decode prep |

**逐行解读**：
- **Dense 行**：表示模型前若干层为稠密层（索引 `0–N`，共 K 层）；特征是**无 MoE 路由**，FFN 走直接 MatMul 而非专家分发；这类层主要承担模型早期特征提取。
- **MoE+DFC 行**：表示模型中间层 `N+1–M` 共 J 层为 MoE 层，使用 `DispatchFFNCombine` 这一融合算子（同时完成专家路由 dispatch + FFN 计算 + combine），是 DeepSeek 类 MoE 模型的典型实现。
- **MoE+GMM 行**：模型最后一层（索引 `M+1`）单独用 `GroupedMatmul` 替代 DFC，并**额外承担** output head、sampling、decode 准备三项职责；因此该层结构特殊，需单独详述。

### 表 2：跨验证表模板（原文 4.5）

| Op | Per Pass Count | Interpretation |
|---|---|---|
| FIA (prefill) | 93 | 1 per layer |
| DispatchFFNCombine | 89 | Layers 3–91 only (MoE layers) |
| GroupedMatmul | 4 | 2 in transition layer + 2 in decode |
| MoeGatingTopK | 91 | 89 prefill MoE + 2 decode |
| split_qkv_rmsnorm_rope | N | Present in layers with next-layer prep |
| ReshapeAndCache | N+1 | KV cache updates |

**逐行解读**：
- **FIA (prefill) = 93**：每 pass 93 次 prefill FIA，正好对应 93 个 transformer 层（即"1 per layer"），是层数结论的最直接证据。
- **DispatchFFNCombine = 89**：仅出现在 layer 3–91（即中间 MoE 层），与"前 3 层 Dense + 中间 89 层 MoE+DFC + 1 层 Transition"的分类一致；该 op 数是分类正确性的交叉验证。
- **GroupedMatmul = 4**：其中 2 次在 transition 层（last layer 用 GMM 替代 DFC），2 次在 decode 阶段（decode 层也走 GMM+alltoallv），说明 GMM 是 decode/transition 层的标志算子。
- **MoeGatingTopK = 91**：89 次 prefill MoE + 2 次 decode，对应"每个 MoE 层（含 decode）都需做 gating"；该数与 DFC 数 89 的差值（91-89=2）正好等于 decode 中 2 次 gating，验证 decode 也走 MoE 路径。
- **split_qkv_rmsnorm_rope = N**：在"带 next-layer prep"的层出现，说明 QKV 分割、RMSNorm、RoPE 融合是层间预计算的标志。
- **ReshapeAndCache = N+1**：KV cache 写入次数为层数+1，因为最后一层之后还有一次额外的 cache 准备；N+1 这个 +1 是 KV cache 流水线尾部的特征。

### 表 3：层间变异性对比表（原文 4.9）

| Metric | Dense (0–2) | MoE+DFC (3–91) | Transition (92) | Decode |
|---|---|---|---|---|
| Wall time | X ms | Y ms (avg) | Z ms | W ms |
| FIA share | A% | B% | C% | D% |
| DFC cost | 0 | V ms | 0 | 0 |
| Post-FIA compute | ... | ... | ... | ... |
| Kernels per layer | ... | ... | ... | ... |

**逐行解读**：
- **Wall time 行**：四种层类型的墙钟时间，Dense 一般最短，MoE+DFC 中等，Transition 因合并 output head 最长，Decode 因每 token 算 latency-bound 又有不同分布。
- **FIA share 行**：FIA 占层总耗时的百分比；Dense 层 FIA 占比通常较高（无 MoE 开销），MoE+DFC 层被 DFC 稀释后占比下降，Decode 层 FIA 占比极低（0.2ms 量级，详见原文 4.7）。
- **DFC cost 行**：仅 MoE+DFC 行有非零值 V ms，Dense 与 Transition 行均为 0；这是层类型最干净的二值判别特征。
- **Post-FIA compute 行**：FIA 之后的剩余计算（MoE routing / dispatch / FFN / allGather 等），四种层类型差异显著。
- **Kernels per layer 行**：每层算子数；Decode 通常 kernel 数远多于 prefill decode prep（含 embedding、position encoding、KV cache 准备）。

---

## 【公式解读】

**原文无独立数学公式**（无 LaTeX、无 `$...$` 表达式）。

但存在若干**伪代码 / 结构化标记**值得保留并解释：

### 伪代码 1：层 kernel 序列树（原文 4.6）

```
FIA ({duration}ms)
├─ Attention projection: TensorMove×2 → MatMulV3 ({dur}ms)
├─ TP communication: hcom_reduceScatter ({dur}ms) → allgather_AICPU
├─ MoE routing: AddRmsNormBias → Cast → MatMulV2 → MoeGatingTopK
├─ Expert dispatch: DispatchFFNCombine ({dur}ms)
├─ Expert FFN:
│   DynamicQuant → QuantBatchMatmulV3 → SwiGlu → QuantBatchMatmulV3
├─ Post-MoE: AddRmsNormQuant → hcom_allGather
├─ Next-layer prep:
│   reduce_scatter_AICPU ({dur}ms, stream {N}, overlapped)
│   QuantBatchMatmulV3 → split_qkv_rmsnorm_rope → ReshapeAndCache
```

**符号与作用说明**：
- `FIA ({duration}ms)` — 根节点，整个层的注意力融合算子，括号内为该次调用实测时长。
- `├─ / └─` — ASCII 树形缩进符，描述算子**执行先后顺序**（非调用关系）。
- `TensorMove×2 → MatMulV3` — QKV 投影阶段，`×2` 表示出现 2 次。
- `hcom_reduceScatter → allgather_AICPU` — TP（张量并行）通信对，先 reduce-scatter 再 allgather 是典型的 2 段式 TP 同步模式。
- `AddRmsNormBias → Cast → MatMulV2 → MoeGatingTopK` — MoE 路由链：RMSNorm+加 bias → 类型转换 → 门控 logits 矩阵乘 → TopK 选专家。
- `DispatchFFNCombine ({dur}ms)` — 融合算子，同时完成专家 dispatch + FFN 计算 + combine，单次调用。
- `DynamicQuant → QuantBatchMatmulV3 → SwiGlu → QuantBatchMatmulV3` — 量化版专家 FFN：动态量化 → 量化 batch matmul（gate 投影）→ SwiGLU 激活 → 量化 batch matmul（up 投影）。
- `AddRmsNormQuant → hcom_allGather` — MoE 后的归一化+量化，再做 TP allgather。
- `reduce_scatter_AICPU ({dur}ms, stream {N}, overlapped)` — AICPU 上的 reduce-scatter，标注 stream 编号与"overlapped"标志（表示与下一层 FIA 并行）。
- `split_qkv_rmsnorm_rope → ReshapeAndCache` — 为下一层准备的 QKV 分割+RMSNorm+RoPE 融合，以及当前层 KV 写 cache。

### 伪代码 2：通信-计算重叠流水线（原文 4.8）

```
Layer N: [FIA 28.5ms][post-FIA 12ms]
Layer N comm:          [reduce_scatter 29.9ms on stream 82]
                       ↕ overlaps with ↕
Layer N+1: ............[FIA 28.5ms][post-FIA 12ms]
```

**符号与作用说明**：
- `[FIA 28.5ms]` / `[post-FIA 12ms]` — 时间轴上的方括号，宽度表示该阶段墙钟时长。
- `Layer N comm:` 与 `Layer N+1:` 上下对齐 — 表示**同一物理时间窗口内**，不同 stream 上的算子在并行执行。
- `↕ overlaps with ↕` — 显式标注垂直方向的两条时间线存在时间交叠。
- `............`（点序列）— 表示 Layer N+1 在 Layer N 还没结束时就已经启动，量化了"流水深度"。
- `stream 82` — AICPU 上的通信专用 stream 编号，区分于 NPU compute stream。
- 关键不变量：`kernel_sum (FIA+comm+...) >> wall_ms`，差值即被多 stream 重叠隐藏的通信成本。

### 伪代码 3：ASCII 模型总体图（原文 4.10）

```
┌─────────────────────────────────────────────────┐
│  MoE Transformer Model — N Layers               │
│  DP=X, TP=Y, EP                                 │
│  Sequence: {prefill}K prefill + {decode} decode  │
├─────────────────────────────────────────────────┤
│  Layer 0:  Dense Attention + Dense FFN           │
│  ...                                             │
│  Layer K:  Attention + MoE FFN (DFC)      ──┐   │
│  ...                                     M MoE  │
│  Layer K+M: Attention + MoE FFN + Sample ───┘   │
│  Layer last: MoE (GMM+alltoallv) + Output Head  │
├─────────────────────────────────────────────────┤
│  Decode Phase (L layers per pass):               │
│  Decode 0: Attention + MoE (GMM+alltoallv)      │
│  ...                                             │
└─────────────────────────────────────────────────┘
```

**符号与作用说明**：
- `{N}` `{X}` `{Y}` `{prefill}` `{decode}` — 占位符，由真实数据填入。
- `─┐` `─┘` — 框线符号，标注 MoE 块的范围（K 到 K+M 共 M 个 MoE 层）。
- 顶层三段式结构：**模型头（配置）→ Prefill 主体（按层类型分组）→ Decode 主体**。
- `Layer last: MoE (GMM+alltoallv) + Output Head` — 显式标注最后一层与中间 MoE 层的实现差异（GMM vs DFC）以及承担的额外职责（Output Head）。

### 伪代码 4：Per-pass 执行时间线（原文 4.10）

```
0ms        1000ms     2000ms     3000ms     3800ms
|──────────|──────────|──────────|──────────|
[Layer0][Layer1]...[Layer91][L92=87ms][D0=15ms][D1=14ms]
 33ms   33ms        45ms
  └── 9
```

**符号与作用说明**：
- `|──────────|` 段分隔线 + 顶部时间刻度 — 全局时间轴。
- `[Layer0][Layer1]...` — 每一层一个方括号，宽度与该层 wall time 成正比。
- `33ms 33ms ... 45ms` — 对应层下方标注其实测 wall time。
- `L92=87ms` — transition layer 92 因合并 output head 而耗时异常（87ms 远高于其他层 33ms），是异常信号点。
- `D0=15ms` `D1=14ms` — decode 层耗时显著低于 prefill MoE 层（45ms vs 14–15ms），呈现 decode 的轻量特性。
- `└── 9` — 不完整的下划线（疑似模板截断），可能本意是"warm-up 前 9 层"的标注。

---

## 【关联】

**原文未提供任何内部链接（`内部链接: (无)`），且文档本身是"模板/方法论文档"而非可执行模块，因此与其他特性的关联主要体现在以下结构性引用关系上**：

1. **与异常报告的姊妹关系**（原文 §1）：架构报告与异常报告配套产出，前者回答"模型是什么、如何执行"，后者回答"什么看起来不自然"。两者共享同一份 profiling 数据源，但产出物独立。
2. **与 `ascend-profiling-anomaly` skill 主体的关系**：本文件位于 `official/Common/ascend-profiling-anomaly/references/`，作为该 skill 的参考模板被引用——skill 主体负责"发现异常"，本模板负责"描述被分析的模型"。
3. **依赖的 profiling 算子词汇表**：`FusedInferAttentionScore (FIA)`、`DispatchFFNCombine`、`GroupedMatmul`、`MoeGatingTopK`、`alltoallv`、`split_qkv_rmsnorm_rope`、`ReshapeAndCache`、`DynamicQuant`、`QuantBatchMatmulV3`、`SwiGlu`、`MatMulV3`、`hcom_reduceScatter`、`allgather_AICPU`、`reduce_scatter_AICPU` 等算子名是昇腾 CANN/AICPU 体系下的命名，模板对其语义有明确假设。
4. **与并行策略的强耦合**：模板字段 `DP{X} × TP{Y} [with EP if expert parallelism detected]`、`stream_count`、`prefill_FIA_count` / `decode_FIA_count` 表明输出格式专为昇腾多 stream + DP/TP/EP 混合并行场景设计。
5. **目录命名约定的上游约定**：依赖 profiling 目录名遵循 `<日期>_dp<DP>_tp<TP>[_ep]_<prefill>K_<decode>K_bs<N>` 模式（见 §2 示例），目录名是配置抽取的唯一入口。

---

## 【使用方法】

**原文未直接给出"启用方式/配置项/命令"**，因为本文档是报告生成方法论的描述而非可执行工具。但以下调用约定可直接复用：

| 项目 | 原文规定 |
|---|---|
| **报告文件名** | `model_architecture_report_<profiling_dir_name>.md` |
| **示例** | `model_architecture_report_0313_dp2_tp8_ep_100k_1k_bs10.md` |
| **存放位置** | profiling 目录内，或 working output 目录 |
| **章节数量** | 10 节，**强制顺序** |
| **配置抽取入口** | profiling 目录名 + profiling metadata |
| **结构标记** | FusedInferAttentionScore (FIA) 调用次数与时长 |
| **Prefill/Decode 切分阈值** | FIA duration > 10ms → prefill；< 1ms → decode |
| **算子判别标志** | `DispatchFFNCombine` / `GroupedMatmul` / `MoeGatingTopK` / `alltoallv` 出现与否 |
| **章节展开工具** | 缩进 ASCII 树（kernel 序列）、ASCII 流水线图（通信重叠）、ASCII 模型框图（总览） |
| **必填节标题清单** | Configuration Context / Architecture Determination / Forward Pass Boundaries / Layer Classification / Cross-Verification / Per-Layer Sub-Structure / Decode Phase Analysis / Communication Pipeline / Layer-to-Layer Variation / Architecture Summary |

> 注：原文未涉及 CLI 命令、环境变量、API endpoint 等"启用方式"，仅给出模板结构与字段语义。
