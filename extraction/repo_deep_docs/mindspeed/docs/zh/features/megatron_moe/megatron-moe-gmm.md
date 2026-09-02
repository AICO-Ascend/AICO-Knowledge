# Megatron MoE Grouped GEMM (GMM)

> 仓 `mindspeed` · 路径 `docs/zh/features/megatron_moe/megatron-moe-gmm.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed/docs/zh/features/megatron_moe/megatron-moe-gmm.md

# Megatron MoE Grouped GEMM (GMM) — 一体化深度解读

---

## 【定位】

这篇文档描述了 mindspeed 面向 MoE 单卡多专家训练场景,通过调用 `npu_gmm` 融合算子将原本细碎的多个专家 GEMM 计算合并为一次 Grouped GEMM 调用,从而降低 kernel launch 与调度开销、提升训练吞吐的能力,以及其开关、典型收益场景与算子级输入输出约束。

---

## 【技术要点】

1. **能力定位**:通过 `Grouped GeMM`(Grouped General Matrix Multiplication)融合算子对 MoE 单卡多专家 GEMM 进行批量合并,缓解「专家计算细碎 + 通信频繁」带来的开销。
2. **启用开关**:通过命令行参数 `--moe-grouped-gemm` 开启;支持 MoE 三种 dispatcher:`allgather`、`alltoall`、`alltoall_seq`。
3. **底层算子**:开启后底层调用 `npu_gmm` 融合算子(签名见原文算子输入输出段)。
4. **Megatron 原生限制**:megatron 原生不支持 `--moe-grouped-gemm` 在同时开启 `--bf16` 的场景下使用(原文 NOTE 显式标注)。
5. **典型受益场景**:
   - EP 变小 → 单卡专家数量增大;
   - DeepSeek MoE 专家总数较多;
   - DeepSeek MoE fine-grained expert 单个专家较小、FFN 规模不大、TP 变大 → 单卡切分后计算量小、kernel 细碎。
6. **收益衰减规律**:随着 FFN 规模提升,单专家计算本身已足够大,Grouped GEMM 的「合并收益」变小。

---

## 【关键机制与数据】

**工作原理**:MoE 中 expert 计算本质上是多个规模相同(或相近)的 GEMM,在 dispatch/路由后单卡上要依次发起若干次矩阵乘;在 EP 较小或 TP 较大时,每次 GEMM 的计算量变小,kernel 数量变多,kernel launch 与调度/通信开销占比放大。`npu_gmm` 通过一次调用携带 `group_list` 把多组 GEMM 合并,在硬件层做 tiling/调度,从而摊薄细碎开销。

**数据流概览**(基于原文描述还原):
- 输入 token 经 dispatcher(`allgather` / `alltoall` / `alltoall_seq`)路由到本卡的若干专家;
- 多个专家的 GEMM:`y = x @ weight`(训练场景 `bias=None`)被合并为 `npu_gmm(x, weight, group_list=…, group_type=…)`;
- 输出 `y` 再经过 combine / unpermute 还原。

**性能数据(原文):**

- **Grok 模型**(表 1):在 `ffn_hidden_size = 32768 / 16384 / 8192 / 4096` 下,baseline 与 GEMM 的耗时对比及性能提升分别为 **-5.30% / 3.53% / 6.12% / 8.60%**,呈现「FFN 越小、收益越大」的单调趋势;当 `ffn_hidden_size = 32768` 时,Grouped GEMM 反而劣化约 5.30%,与原文「FFN 规模提升后收益变小甚至消失」一致。
- **Mixtral 8×7B 模型**(表 2):在 `tp4 ep2 16expert / tp4 ep2 8expert / tp2 ep4 16expert / tp2 ep4 8expert` 四种配置下,加速比为 **44.06% / 17.93% / 8.39% / -2.19%**,验证原文「TP 越大、EP 越小,收益越大」的结论;而 `tp2 ep4 8expert` 已出现负收益。

---

## 【表格解读】

### 表 1 — Grok 模型 FFN 大小与性能加速对比(原文逐字还原)

| ffn_hidden_size | 32768 | 16384 | 8192 | 4096 |
|---|---|---|---|---|
| baseline | 2280 | 1780 | 1537 | 1446 |
| GEMM | 2416 | 1719 | 1448 | 1331 |
| 性能提升 | -5.30% | 3.53% | 6.12% | 8.60% |

**逐行解读**:
- `ffn_hidden_size`:专家 FFN 隐藏维度,沿列从 32768 递减到 4096,代表单专家计算量从大变小。
- `baseline`:未启用 Grouped GEMM 时的耗时基准;数值随 FFN 缩小单调下降,符合「计算量变小 → 耗时变短」的一般规律。
- `GEMM`:启用 `npu_gmm` 后的耗时;在 FFN=32768 时高于 baseline,在 FFN≤16384 时均低于 baseline。
- `性能提升`:随 FFN 减小,提升幅度从负值逐步增大到 8.60%,印证原文「FFN 规模提升后 Grouped GEMM 收益变小」的反向表述——即 FFN 越小、专家计算越细碎,合并收益越显著;反之 FFN 已经足够大时,合并带来的收益不足以覆盖开销,出现 -5.30% 的劣化。

### 表 2 — Mixtral 8×7B 不同配置性能收益(原文逐字还原)

| 配置 | tp4 ep2 16expert | tp4 ep2 8expert | tp2 ep4 16expert | tp2 ep4 8expert |
|---|---|---|---|---|
| baseline | 27969 | 20127 | 11976 | 13981 |
| GEMM | 19415 | 17361 | 11049 | 14290 |
| 性能提升 | 44.06% | 17.93% | 8.39% | -2.19% |

**逐行解读**:
- `配置`:TP(张量并行度)与 EP(专家并行度)的组合,横向对比「TP 大 EP 小」与「TP 小 EP 大」两种倾向。
- `baseline` / `GEMM`:对应配置的耗时;GEMM 在前三列均低于 baseline,仅在最后一列 `tp2 ep4 8expert` 略高于 baseline。
- `性能提升`:从 44.06%(tp4 ep2 16expert,TP 大 EP 小)递减到 -2.19%(tp2 ep4 8expert,TP 小 EP 大),精确对应原文结论「TP 越大、EP 越小,收益更大」。最后一列负收益提示:在 TP=2、EP=4、专家数只有 8 的设置下,单卡专家数较少、单专家计算又已被 TP 切得较小,Grouped GEMM 的合并窗口不足以摊薄开销。

### 算子输入输出类型组合表(原文逐字还原)

| x        | weight   | bias    | group_list          | group_type | gemm_fusion | original_weight | y                                 |
|----------|----------|---------|---------------------|------------|-------------|-----------------|-----------------------------------|
| float16  | float16  | float16 | list[int64] 或 tensor | int64      | bool        | float16         | float16                           |
| bfloat16 | bfloat16 | float32 | list[int64] 或 tensor | int64      | bool        | bfloat16        | bfloat16                          |
| float32  | float32  | float32 | list[int64] 或 tensor | int64      | bool        | float32         | float32(仅 x、weight、y 都为单 tensor 场景支持) |

**逐行解读**:
- 该表为 `npu_gmm` 在非量化场景下支持的输入输出 dtype 组合白名单,任何超出该组合的调用可能导致算子报错。
- 第一行 `float16` 链:`x/weight/bias/original_weight/y` 全部为 `float16`,`group_list` 为 `list[int64]` 或 `tensor`,`group_type` 为 `int64`,`gemm_fusion` 为 `bool`。
- 第二行 `bfloat16` 链:与第一行类似,但 `bias` 例外地要求为 `float32`(原文如此标注)。
- 第三行 `float32` 链:所有张量均为 `float32`,且**仅在 x、weight、y 均为单 tensor 场景下支持**(原文括号内特别说明,这是相比 fp16/bf16 链更严格的限制)。

---

## 【公式解读】

原文无独立数学公式。仅在描述 `group_type` 参数时给出伪代码式语义约定,可视为一个符号说明,而非严格公式:

原文:

> 矩阵乘为 `C[m,n] = A[m,k] × B[k,n]`,则 `group_type` 取值 `-1`:不分组;`0`:`m` 轴分组;`1`:`n` 轴分组;`2`:`k` 轴分组,默认值为 `0`。

**符号含义解释**:
- `A[m,k]`、`B[k,n]`、`C[m,n]`:标准 GEMM 三元组,m=行数(M 维)、n=列数(N 维)、k=归约维(K 维)。
- `group_type = -1`:不分组,即按单次普通 GEMM 处理。
- `group_type = 0`:沿 M 维分组,等价于「按行方向把若干次 GEMM 拼接」,通常对应 MoE 中「不同 token 路由到不同 expert」后,沿 batch 维堆叠的形态。
- `group_type = 1`:沿 N 维分组,沿输出通道方向拼接。
- `group_type = 2`:沿 K 维分组,沿归约维拼接。
- 默认值 `0`:MoE 训练中最常见的分组方式。

---

## 【关联】

文档未提供文末内部链接(原文链接区段为「(无)」),但从内容描述中可识别出以下上下游关联:

- **上游 / 并行策略**:
  - **EP(Expert Parallel)**:EP 越小,单卡专家越多,Grouped GEMM 收益越大;直接受 MoE 并行配置控制。
  - **TP(Tensor Parallel)**:TP 越大,单卡分到的计算越小,Grouped GEMM 收益越大;与 EP 形成「TP↑、EP↓ → 收益↑」的耦合关系。
  - **三种 MoE dispatcher**:`allgather`、`alltoall`、`alltoall_seq`——`--moe-grouped-gemm` 需与 dispatcher 协同配合使用,文档明确该开关对三种 dispatcher 均支持。
- **下游 / 硬件算子**:
  - **`npu_gmm` 融合算子**:实际计算执行单元,接受 `x / weight / bias / group_list / group_type / gemm_fusion / original_weight` 等参数,反向累加梯度时可启用 `GMM+ADD` 融合(由 `gemm_fusion=True` 触发)。
- **框架约束**:
  - 与 megatron 原生 `--bf16` 选项存在互斥关系(原文 NOTE):二者同时开启不被支持,使用本特性时需注意精度配置。
- **模型侧适配**:
  - **DeepSeek MoE / Grok / Mixtral 8×7B**:文档以这三类典型模型举例,说明 fine-grained expert、专家数量、FFN 规模等因素对收益的影响。

---

## 【使用方法】

**启用方式(原文):**

- 在启动脚本中加入命令行参数:
  ```
  --moe-grouped-gemm
  ```
  表示开启 Grouped GEMM 计算;支持 MoE `allgather`、`alltoall`、`alltoall_seq` 三种 dispatcher。

**注意事项(原文 NOTE):**

- megatron 原生不支持 `--moe-grouped-gemm` 在开启 `--bf16` 的场景下使用。
- 通过 `--moe-grouped-gemm` 开启后,底层会调用 `npu_gmm` 融合算子。

**算子调用模板(原文):**

```python
y = npu_gmm(x, weight, bias=None, group_list=None, group_type=0, gemm_fusion=False, original_weight=None)
```

各参数类型与默认值已在原文「算子输入输出」一节逐字段给出,可参照上文【表格解读】中的 dtype 组合表确认合法输入形态;非法 dtype 组合可能导致算子报错并影响训练效率。
