# Megatron MoE TP拓展EP

> 仓 `mindspeed` · 路径 `docs/zh/features/megatron_moe/megatron-moe-tp-extend-ep.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed/docs/zh/features/megatron_moe/megatron-moe-tp-extend-ep.md

# Megatron MoE TP拓展EP — 深度解读

## 【定位】
这篇文档描述了一种面向**细粒度小专家 MoE 场景**的并行策略：当 TP+EP 同时开启、TP 组按常规方式切分专家参数会导致 GMM（Grouped GEMM）算子效率严重下降时，**让专家层的 TP 组不切分专家参数、改为切分专家数量**，从而恢复小专家场景下 GMM 的计算效率，提升整体训练性能。

---

## 【技术要点】

1. **问题背景**：原文："开启TP+EP后，专家层TP组切分专家参数，MoE细粒度小专家场景TP切分后GMM算子效率下降严重。" —— 即 TP 在每个专家内部继续切分权重/参数。
2. **核心解决方案**：原文："专家层TP组不切分专家参数，切分专家数量。" —— 即将原本属于 EP 的"专家数量维度"切分能力由 TP 组来承担，等价于把 EP 做了扩展（"TP extend EP" 的命名由来）。
3. **目标模型架构**：原文："细粒度小专家，类DeepSeek-V2模型，每个专家的参数量较小。" —— 典型代表为 DeepSeek-V2 风格的万亿参数 MoE。
4. **启用开关**：通过 CLI 参数 `--moe-tp-extend-ep` 开启该功能。
5. **必选配套参数**：
   - `--moe-permutation-async-comm`
   - `--moe-grouped-gemm`（原文限定："目前仅支持Grouped MLP"）
6. **配置约束（整除关系）**：原文："需要确保 `--num-experts` 能被 `--tensor-model-parallel-size` 与 `--expert-model-parallel-size` 的乘积整除。" 即：
   $$N_{\text{experts}} \;\big|\; (TP \times EP)$$
7. **功能限制**：
   - 原文："当前该特性不支持MoE Token drop and pad模式，即 `--moe-expert-capacity-factor` 需要为 None。"
   - 原文："当前仅支持 alltoall_seq dispatcher。"

---

## 【关键机制与数据】

### 工作机制（数据流角度）
- **常规 TP+EP**：TP 在 expert 维度内对每个专家的参数矩阵（W1/W2/W3）再做一次切分（行切/列切），单专家被拆到多张 NPU 上；EP 再在专家数量上分配给小专家集合。两者叠加后，**每个 rank 上的 expert 矩阵被进一步切碎**。
- **本文方案（TP extend EP）**：专家层关闭"切参数"路径，转为"在 expert 数量维度上由 TP 组与 EP 组联合分配"。等价于每个 TP rank 持有**完整的若干个小专家**，而不是每个小专家被切碎。
- **性能收益来源**：GMM（Grouped GEMM）算子在被切碎的 weight 上调用时 shape 过小（细粒度小专家原本参数就少，再被 TP 切分后单 rank 上的 GEMM 形状更小），GEMM/TensorCore 利用率严重不足；改为按专家数量切分后，每个专家矩阵 shape 恢复到 TP 切分前的水平，GMM 调度友好。

### 性能数据（原文标注）
- **原文**："通过避免TP切分专家参数，提高小专家场景GMM算子效率，从而提高模型整体训练性能，在**类DeepSeek-V2万亿参数级别的MoE模型**下，并且为**细粒度小专家**，**性能最高提升10%以上**。"
- 注：原文仅给出"最高提升10%以上"这一**总体加速幅度上限**，未给出 step time / throughput / MFU 等细分指标；不存在的指标本文不臆造。

### 限制条件（原文标注）
- 不支持 `--moe-expert-capacity-factor`（即 Token drop and pad 模式）。
- Dispatcher 仅支持 `alltoall_seq`。

---

## 【表格解读】
原文无表格。

---

## 【公式解读】
原文无公式。

（注：原文在"使用方法"中给出了整除约束 `--num-experts` 能被 `TP × EP` 整除，但并未以数学公式形式显式呈现，因此不在此处当作公式还原，仅在【技术要点】中以伪代码形式注明。）

---

## 【关联】

文末"内部链接: 无"表明该文档未在文档站内部显式链接其他特性。但根据文档上下文，可归纳如下上下游/相关特性关系：

- **并行原语层**
  - `--tensor-model-parallel-size`（TP）与 `--expert-model-parallel-size`（EP）共同决定总并行维度；本特性改变了"TP 在专家层做什么"，而非新增或替换这两个原语。
  - 与 GMM（Grouped GEMM）算子实现紧耦合：开启 `--moe-grouped-gemm`（仅 Grouped MLP）是该特性生效的前提。

- **MoE 调度层**
  - Dispatcher：仅支持 `alltoall_seq`，意味着该特性依赖 `alltoall_seq` 形式的 token→expert 分发路径；其他 dispatcher 形态（如 allgather / alltoall-all）不在支持范围内。
  - Token drop and pad：因 `--moe-expert-capacity-factor` 必须为 None，所以该特性不与"容量因子截断/补零"路径互通。

- **通信层**
  - `--moe-permutation-async-comm` 是必选配套项，说明本特性依赖**异步 permutation 通信**来掩盖 TP×EP 扩展后的额外调度开销，二者共同启用才能保证收益成立。

- **典型模型参考**
  - DeepSeek-V2（细粒度小专家，万亿参数 MoE）是文中点名的代表模型；特性设计与此类架构的"专家多、单专家小"特征直接相关。

- **拓展功能命名含义**
  - "TP 拓展 EP"——本质上让 TP 组在专家层获得"切分专家数量"的能力，相当于把 EP 的部分切分职责吸收到 TP 组中，因此参数名取自 `--moe-tp-extend-ep`。

---

## 【使用方法】

原文已给出完整启用步骤，原文摘录如下（按原文逐条保留）：

- **开启特性**：添加 `--moe-tp-extend-ep` 启用该功能。
- **必选配套参数**（必须同时开启）：
  - `--moe-permutation-async-comm`
  - `--moe-grouped-gemm`（注意：目前仅支持 Grouped MLP）
- **配置约束**：需要确保 `--num-experts` 能被 `--tensor-model-parallel-size` 与 `--expert-model-parallel-size` 的乘积整除。
- **不兼容项**：
  - 不支持 MoE Token drop and pad 模式 → `--moe-expert-capacity-factor` 须为 `None`。
  - Dispatcher 仅支持 `alltoall_seq`。
