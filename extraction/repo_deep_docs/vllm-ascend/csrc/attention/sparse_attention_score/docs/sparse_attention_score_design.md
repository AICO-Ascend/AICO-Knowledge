# SparseAttentionScore Operator Design

> 仓 `vllm-ascend` · 路径 `csrc/attention/sparse_attention_score/docs/sparse_attention_score_design.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm-ascend/csrc/attention/sparse_attention_score/docs/sparse_attention_score_design.md

# SparseAttentionScore Operator Design —— 一体化深度解读

---

## 【定位】

本文档定义了 `SparseAttentionScore`(SASA)算子的设计与实现:面向 **Paged KV Cache + Top-K Block Selection** 的稀疏 Attention 算子,服务于 LLM **decode 阶段**及**小 batch prefill** 场景,使 Q 仅 attend 到预先筛选的 Top-K KV 物理块,从而实现稀疏注意力。

---

## 【技术要点】

1. **稀疏模式输入**:接收 `select_idx` + `select_num_idx`(已预算好的 Top-K block ID 列表),而非 2D 掩码,省去 mask-to-index 转换。
2. **Paged KV Cache 格式**:KV 存储为 `[num_blocks, block_size, kv_heads, D]`,`block_size` 固定为 **128**,通过 `block_table[batch, logical_id]` 完成 logical→physical 映射。
3. **TND Q 格式**:Q 形状为 `[T, N_q, D]`,输出 shape 与 Q 完全一致。
4. **GQA Group-head 优化**:每组 `groupSize = numHeads / kvHeads` 个 Q head 共享同一 `select_idx`(以 KV head 索引),一次 KV 加载服务 `groupSize` 个 Q head,KV 传输量降低 `groupSize` 倍。
5. **任务粒度**:每个 task 处理 **1 token × 1 KV head group**,并行度 `totalTaskNum = totalQTokens × kvHeads`,由 `blockDim = min(totalTaskNum, aicNum)` 控制。
6. **双核流水线**:**AIC(Cube)** 负责 QK/PV 矩阵乘并经 FixPipe 写入 UB,**AIV(Vector)** 负责 softmax 与 rescaleO,使用 `SetFlag/WaitFlag + PipeBarrier` 实现 PRE=2 的 Cube→Vector→Cube 流水。
7. **Online Softmax**:逐块处理 Top-K blocks,FP32 维护 `lastMax/lastSum/o_acc`,通过 `correction = exp(lastMax - nowMax)` 进行块间累加,最后 `o_acc / lastSum` 得到输出。
8. **尾块变长支持**:利用 `lastBlockTileSize = (historyLen + qTokenInBatch) % blockSize_ + 1` 计算 causal 末尾 block 的有效 token 数,通过 `kvSTileSizeAct = validTileSize[kvBlockIdx]` 传给 matmul 控制有效行数。

---

## 【关键机制与数据】

### 整体流水线(原文 Pipeline 图)

```
Per task: 1 token × groupSize heads × Top-K KV blocks
Load Q (once) ─► QK MMAD (Cube) ─► Softmax (Vector) ─┐
                                                      ▼
Load V (per blk) ─► PV MMAD (Cube) ─► RescaleO (Vector) ─► Store O
Pipeline: QK[i] → SM[i] → PV[i] → Rescale[i] (PRE=2)
```

### 任务分解(原文)

```cpp
qToken = taskIdx / kvHeads_;
kvHeadIdx = taskIdx % kvHeads_;
qHeadStart = kvHeadIdx * groupSize;
gmOffsetQ = qToken * strideQO + qHeadStart * embed_;  // groupSize 个连续 head
```

### Matmul 维度(原文)

```
QK: M=groupSize, N=kvBlockSize(<=128), K=headDim(128)
    Q[groupSize, D] × K[D, blockSize]^T → S[groupSize, blockSize]
PV: M=groupSize, N=headDim(128), K=kvBaseTile(<=128)
    P[groupSize, blockSize] × V[blockSize, D] → OTmp[groupSize, D]
```

### Paged KV 地址计算(原文)

```cpp
gmOffsetK = physicalBlockId * strideKVBlock + kvHeadIdx * embed_;
```

KV 存储按 `[physical_block_id, block_size, kv_heads, D]` 排列,`block_table` 把 `select_idx` 中的 logical_id 翻译为 physical_id。

### Online Softmax 块更新算法(原文)

```
对每个 KV block:
    S = Q × K^T                       (BF16 matmul)
    S_scaled = S * scale              (BF16)
    nowMax = row_max(S_scaled)        (per head)
    if not first: nowMax = max(nowMax, cast_bf16(lastMax))
    P = exp(S_scaled - nowMax)        (BF16)
    nowSum = reduce_sum(P)            (BF16)
    # FP32 状态更新
    correction = exp(lastMax - nowMax)
    lastSum = correction * lastSum + nowSum
    lastMax = nowMax
    PV = P × V                        (BF16, FP32 累加)
    o_acc = correction * o_acc + PV   (FP32)
output = cast_bf16(o_acc / lastSum)
```

### 性能相关参数(原文)

- Tile 大小:`qBaseTile = 128`,`kvBaseTile = 128`
- L1 matmul tiles:M/N/K 配置分别对应 MM1(QK) 与 MM2(PV)
- L0 buffer 数:`mm1L0ATotalStages = mL0Loop * (embed / L0_TILE_K)`,`mm2L0ATotalStages = mL0Loop * (kvBaseTile / L0_TILE_K)`,其中 `mL0Loop = ceil(groupSize / L0_TILE_M)`(`groupSize ≤ 16` 时为 1)
- QK 与 PV matmul 在 L0A/L0B 之间交替,`prefixSumL0AStages` 防止 buffer ID 冲突

> 注:文档未给出实测的性能数字(throughput/latency 等)。

---

## 【表格解读】

### 表 1: SASA vs BSA 整体对比(原文逐字还原)

| Dimension | SparseAttentionScore (SASA) | BlockSparseAttention (BSA) |
|---|---|---|
| **Sparse-pattern input** | `select_idx` + `select_num_idx` (a precomputed list of Top-K block IDs) | `block_sparse_mask` (a 2D binary mask converted to indices inside the kernel) |
| **KV storage format** | Paged KV Cache: `[num_physical_blocks, block_size, kv_heads, D]` | Contiguous KV: TND / BNSD / BSND |
| **Q format** | TND: `[total_tokens, num_heads, D]` | TND / BNSD / BSND |
| **Address mapping** | `block_table[batch, logical_id]` to `physical_id` | Direct contiguous access by sequence offset |
| **Task granularity** | 1 token x 1 KV head group after group-head optimization | 1 Q tile x 1 Q head |
| **GQA handling** | A group shares `select_idx`; one KV transfer serves `group_size` heads | Each Q head is an independent task; groups are not merged |
| **`block_size`** | Fixed at 128 for physical paged-cache blocks | Configurable through `blockShapeX` / `blockShapeY` |
| **Use cases** | vLLM decode and long-context sparse inference | General sparse attention for training and inference |
| **Workspace** | No mask-to-index conversion required | Requires workspace for `sparse_idx` and `sparse_count` |

**逐行解读**:
- **Sparse-pattern input**:SASA 上游预算好 Top-K block ID 列表,直接传入;BSA 传入 2D 掩码,需要在 kernel 内转换成 index,多一步开销。
- **KV storage format**:SASA 直接吃 vLLM 的 Paged KV Cache,可零拷贝复用;BSA 期待连续 KV(如 TND/BNSD/BSND),与 vLLM 的内存管理不天然契合。
- **Q format**:SASA 限定 TND 形式,与 decode 阶段 token-by-token 调度吻合。
- **Address mapping**:SASA 经 `block_table` 翻译;BSA 通过 sequence offset 直接寻址(连续地址假设)。
- **Task granularity**:SASA 借 GQA 把 `groupSize` 个 head 合并成一个 task,reduce 调度项;BSA 拆到 Q tile × Q head,调度更细但更冗余。
- **GQA handling**:SASA 一份 KV 服务组内全部 head;BSA 不合并 group。
- **`block_size`**:SASA 写死 128 匹配 paged-cache 物理块;BSA 可通过 `blockShapeX/blockShapeY` 配置,更灵活但需为不同 shape 重生成索引。
- **Use cases**:SASA 面向 **vLLM decode + 长上下文稀疏推理**;BSA 面向通用稀疏 attention(训练 + 推理)。
- **Workspace**:SASA 不需额外显存放 sparse_idx/sparse_count;BSA 需要。

---

### 表 2: 输入接口(原文逐字还原)

| Parameter | Shape | Description |
|---|---|---|
| `query` | `[T, N_q, D]` (TND) | Q tensor in BF16, FP16, or FP8 |
| `key` | `[num_blocks, block_size, N_kv, D]` | K tensor in the paged KV cache |
| `value` | `[num_blocks, block_size, N_kv, D]` | V tensor in the paged KV cache |
| `select_idx` | `[N_kv, max_q_seqlen, top_k]` | Top-K logical block IDs for every KV head and Q token |
| `block_table` | `[batch, max_blocks_per_batch]` | Logical-to-physical block mapping |
| `select_num_idx` | `[N_kv, max_q_seqlen]` | Actual number of valid blocks for each token |
| `actual_seq_lengths` | `[batch]` | Q sequence length for each batch item |
| `actual_seq_lengths_kv` | `[batch]` | KV sequence length for each batch item |

**逐行解读**:
- `query`:支持 BF16/FP16/FP8 三种精度,TND 布局;`T` 为所有 batch 的 token 总和。
- `key`/`value`:同一个 paged KV cache 物理块格式,只在 `select_idx` 决定读取哪些块。
- `select_idx`:**三轴**——每个 KV head、每个 Q token 都有独立的 Top-K 列表,粒度最细。
- `block_table`:vLLM paging 必备,完成 logical→physical 翻译。
- `select_num_idx`:Top-K 真实有效个数(因不同 Q token 的可用 KV 长度不同,实际需要的 block 数 < `top_k`)。
- `actual_seq_lengths`/`actual_seq_lengths_kv`:Q 与 KV 各自每条序列的真实长度,用于定位 `qToken` 在 batch 中的位置与对应 KV 历史长度。

---

### 表 3: Attributes(原文逐字还原)

| Attribute | Description |
|---|---|
| `num_key_value_heads` | Number of KV heads |
| `scale_value` | Softmax scale; defaults to `1 / sqrt(D)` |
| `block_size` | Paged KV cache block size (128) |
| `top_k` | Maximum number of selected blocks |
| `inner_precise` | Precision mode |

**逐行解读**:
- `num_key_value_heads`:KV head 数(配合 GQA)。
- `scale_value`:softmax 缩放因子,缺省按 head dim 自动取 `1/sqrt(D)`。
- `block_size`:paged 物理块大小,**写死 128**,与 vLLM 默认对齐。
- `top_k`:Top-K 上限,即每个 (KV head, Q token) 至多选多少个 block。
- `inner_precise`:精度模式(如 high-precision/HF32 等控制)。

---

### 表 4: Output(原文逐字还原)

| Parameter | Shape | Description |
|---|---|---|
| `output` | `[T, N_q, D]` (TND) | Attention output with the same shape as Q |

**逐行解读**:输出与 Q shape 完全一致(`[T, N_q, D]`),便于上层按 Q 序号回填。

---

### 表 5: KV 数据加载差异(原文逐字还原)

| | SASA | BSA |
|---|---|---|
| **K loading** | Loads each physical block independently after translating its address through `block_table` | Gathers contiguous sparse blocks using indices prepared in workspace |
| **Sparse arguments to `blockMmadQK`** | `gatheredKvSTileIdx=0, yBlockNum=1` (processes one block at a time) | `gatheredKvSTileIdx, yBlockNumRsvd` (gathers multiple blocks) |
| **V loading** | Same per-physical-block approach as K | Same sparse-gather approach as BSA K loading |

**逐行解读**:
- **K loading**:SASA 经 `block_table` 翻译成物理地址后**逐块独立加载**;BSA 假设连续 KV,在 workspace 内准备好 index 后**一次 gather 多块**。Paged 下 gather 逻辑被 SASA 完全绕开。
- **Sparse arguments**:SASA 调用 `blockMmadQK` 时传 `gatheredKvSTileIdx=0, yBlockNum=1`,一次只处理一个 KV block,逻辑最小化;BSA 传 `gatheredKvSTileIdx` 与 `yBlockNumRsvd` 一次性 gather 多块。
- **V loading**:K/V 在 SASA/BSA 中分别保持一致风格(SASA 逐块、BSA gather)。

---

### 表 6: Q/O 内存布局差异(原文截断,逐字还原可见部分)

| | SASA (after group-head optimization) | BSA |
|---|---|---|
| **Q GM stride** | `embed_` (heads are contiguous within a group) | `strideQO` (possibly `num_heads * D` or a BNSD stride) |
| **O GM stride** | `embed_` (same as Q) | `strideQO` (same as Q) |
| **`rowNum`** | `groupSize` (for example, 4 or 8) | (原文被截断) |

**逐行解读**:
- **Q GM stride**:SASA 利用 GQA 把同组 `groupSize` 个 head 排成连续 `embed_` 步长,只需一次 `gmOffsetQ = qToken * strideQO + qHeadStart * embed_` 就能取到整组 Q;BSA 沿用任意 `strideQO`。
- **O GM stride**:与 Q 同 stride,输出按相同模式回写。
- **`rowNum`**:SASA 用 `groupSize`(如 4 或 8)作为一次性处理的行数;BSA 在此单元格原文被截断,具体值不可考。

> 注:表格 6 在原文档处被截断(`rowNum` 行未完成),后续行(如 PV 矩阵相关、输出整体策略)未提供,**不臆造**。

---

## 【公式解读】

### 公式 1:核心 Attention 公式(原文)

```text
O = softmax(Q @ K^T / sqrt(d)) @ V
```

- `Q`:查询张量,形状 `[T, N_q, D]`(TND)。
- `K^T`:K 的转置,在 SASA 中 K 形状 `[num_blocks, block_size, N_kv, D]`,实际计算仅取 `select_idx` 指定的 Top-K block 子集。
- `sqrt(d)`:缩放因子 `d` 为 head dim(文中为 `D=128`),由 `scale_value` 控制。
- `softmax`:对 `S = Q @ K^T / sqrt(d)` 沿 KV 维(每行)做归一化;SASA 用 **online softmax** 逐块累加。
- `V`:与 K 同布局的 paged V 张量,按 Top-K 索引加载。
- `O`:输出,与 Q 同形状 `[T, N_q, D]`。

### 公式 2:QK Matmul 维度(原文)

```
QK: M=groupSize, N=kvBlockSize (<=128), K=headDim (128)
    Q[groupSize, D] x K[D, blockSize]^T -> S[groupSize, blockSize]
```

- `M = groupSize`:GQA 组内 Q head 数(如 4、8)。
- `N = kvBlockSize`:单个物理 KV 块的有效 token 数,常规为 128,尾块用 `kvSTileSizeAct` 缩减。
- `K = headDim = 128`:归约轴 = head dim。
- 含义:一次 QK 计算产出该 token 在本 block 上的注意力分数矩阵 `S[groupSize, blockSize]`。

### 公式 3:PV Matmul 维度(原文)

```
PV: M=groupSize, N=headDim (128), K=kvBlockSize (<=128)
    P[groupSize, blockSize] x V[blockSize, D] -> OTmp[groupSize, D]
```

- `M = groupSize`:同上。
- `N = headDim = 128`:输出 head dim,与 Q 一致。
- `K = kvBlockSize`:block 内 token 数,与 QK 的 N 对齐。
- 含义:`P = exp(S_scaled - nowMax)`,用 P 与 V 做一次 GEMM 得本块的 `OTmp`,后续与历史 `o_acc` 做 `correction` 累加。

### 公式 4:Online Softmax 状态更新(原文)

```
nowMax = row_max(S_scaled)
P = exp(S_scaled - nowMax)
nowSum = reduce_sum(P)

correction = exp(lastMax - nowMax)
lastSum = correction * lastSum + nowSum
lastMax = nowMax

o_acc = correction * o_acc + PV
output = cast_bf16(o_acc / lastSum)
```

- `S_scaled`:QK 输出经 `scale_value` 缩放后的分数,BF16。
- `nowMax` / `lastMax`:当前块与历史块的最大值,逐块取 max;`correction = exp(lastMax - nowMax)` 把历史 `Sum/o_acc` 按新最大值缩放。
- `P`:当前块的 softmax 分子,BF16。
- `nowSum` / `lastSum`:分母维护,FP32 保证数值稳定。
- `o_acc`:输出累加器,FP32 维持精度,每块 `correction * o_acc + PV`。
- `output`:末块以 FP32 `o_acc / lastSum` 后转回 BF16 写出。
- 该算式是 streaming attention 的标准 online softmax,允许 KV 任意长度且不需持久化中间 S。

---

## 【关联】

- **BlockSparseAttention (BSA)**:本文反复出现并对比的另一稀疏 Attention 算子。两者在 sparse-pattern 输入格式、KV 存储、Task 粒度、GQA 处理、Workspace 需求等多维度存在差异(见表 1、5、6)。SASA 可视为面向 **vLLM Paged KV Cache + decode 场景**的 BSA 替代实现。
- **vLLM**:作为目标上层。SASA 直接消费 vLLM 的 Paged KV Cache(`block_size=128`、`block_table` 翻译),服务于 vLLM 的 decode 与长上下文稀疏推理路径。
- **Ascend 硬件特性(Cube/AIV)**:依赖 AIC(AICore)矩阵乘 + AIV 向量核的协同,以及 L0A/L0B buffer 调度(`prefixSumL0AStages`)与 FixPipe 数据通路。这些都是与 Atlas/Ascend NPU 体系结构相关的底层能力。
- **GQA(Grouped Query Attention)**:复用了 GQA 的天然结构(每组 head 共享 KV)做 KV transfer 复用,`groupSize = numHeads / kvHeads`。
- **在线 softmax(streaming softmax)**:算法上游通用技术,SASA 将其适配到 Top-K block-by-block 流式场景。
- **文档内部章节串联**:§1 定义算子形态并对比 BSA;§2 明确 I/O 契约;§3 在 host 侧做任务切片并打包 tiling data;§4 落到 NPU kernel 的流水、matmul、寻址、softmax、尾块、Cube/Vector 协作与 L0 buffer 管理;§5 归纳与 BSA 的关键实现差异(KV 加载、Q/O stride、`rowNum`),实际是与 §1 的对比在实现层的细节回扣。
- 文档未提供其他外部 / 内部链接(文末"内部链接:(无)")。

---

## 【使用方法】

> **原文未涉及**具体的启用命令、配置文件路径或 API 调用示例。

文档仅以下列方式间接给出使用约束:

- **输入约束**(决定能否调用):
  - 必须先预算好 Top-K:**`select_idx`** 形状 `[N_kv, max_q_seqlen, top_k]`,每个 (KV head, Q token) 一份 Top-K logical block ID 列表。
  - 必须配套给出 **`select_num_idx`** 形状 `[N_kv, max_q_seqlen]`(各 Q token 实际有效 block 数,通常 ≤ `top_k`)。
  - 必须给出 **`block_table`** `[batch, max_blocks_per_batch]`(由 vLLM 的 paged KV 调度产生,完成 logical→physical 翻译)。
  - 必须给出每条序列的真实长度 **`actual_seq_lengths`** / **`actual_seq_lengths_kv`**。
- **属性设置**(原文 Attributes 表):
  - `num_key_value_heads` —— KV head 数。
  - `scale_value` —— 缺省 `1 / sqrt(D)`。
  - `block_size` —— 固定 **128**(与 vLLM paged-cache 物理块对齐)。
  - `top_k` —— 每个 (KV head, Q token) 至多选多少个 block。
  - `inner_precise` —— 精度模式。
- **支持的精度**:Q 支持 **BF16 / FP16 / FP8**;K、V 取自 paged KV cache(隐含 BF16/FP16,原文未明列 KV 精度)。
- **典型使用场景(原文 Use cases 表)**:vLLM decode、long-context sparse inference。

具体的调用方式(算子入口、绑定 Python API、ACLNN 调用名、配置文件开关等)原文未给出。
