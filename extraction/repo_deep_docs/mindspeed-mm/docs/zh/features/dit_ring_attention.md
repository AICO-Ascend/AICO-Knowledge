# DiT Ring Attention序列并行

> 仓 `mindspeed-mm` · 路径 `docs/zh/features/dit_ring_attention.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-mm/docs/zh/features/dit_ring_attention.md

# DiT Ring Attention序列并行 — 一体化深度解读

## 【定位】

本文档描述 mindspeed-mm 中面向 DiT 长序列训练场景的 **Ring Attention 序列并行（Context Parallel, CP）特性**，通过在序列维度切分张量计算，解决因序列长度 S 增长带来的 $O(S^2)$ 自注意力显存/算力开销问题。

---

## 【技术要点】

1. **问题驱动**：当序列长度 S 增长时，自注意力显存与算力开销以 $O(S^2)$ 速度增长，原有的数据并行、张量并行、流水线并行均无法在序列维度切分。
2. **基础方案**：引入 Ring Attention（参考 arxiv 2310.01889），将序列切块在多设备间环形流转，使设备显存占用与单卡序列长度成线性关系而非平方关系。
3. **增强方案**：进一步支持 Double Ring Attention（参考 LoongTrain, arxiv 2406.18485），通过设置 `--cp-window-size > 1` 启用双层 Ring 调度，提升通信-计算重叠度。
4. **关键参数 `--cp-window-size [int]`**：表示 Double Ring Attention 的内层窗口大小；**缺省值 1** 等价于单层 Ring Attention，**大于 1** 时切换为 Double Ring Attention；要求 `cp_size` 能被该值整除。
5. **数据布局 `--megatron-cp-in-bnsd`**：默认 `fa_layout` 为 "sbh"，开启后切换至 `[B, N, S, D]`（BNSD）格式以提升性能。
6. **通信-计算重叠 `--use-cp-send-recv-overlap`**：启用 send/recv overlap，建议开启以隐藏跨设备 KV 通信开销。

---

## 【关键机制与数据】

- **机制原理（原文）**：长序列沿 S 维度被切分为 `context-parallel-size = CP = 8` 份，分布在多张昇腾设备上。注意力计算时，各卡持有本地 Q，通过环形通信按块依次获取对端 KV 块并立即计算局部 attention，避免一次性加载全部 KV；Double Ring Attention 在此基础上引入内外双层窗口，进一步调度通信顺序。
- **复杂度（原文）**：训练内存/算力随序列维度按 $O(S^2)$ 增长；序列并行通过切分将该增长分摊到 `CP` 个设备。
- **性能权衡（原文）**：相比不开启序列并行，**单步耗时增加**；相比重计算（activation checkpointing）方案，**计算效率提升**。原文未给出具体百分比/加速比数字。
- **性能拐点（原文）**：在 8k 序列长度下，CP 切分后 send/recv 通信时间**长于**计算时间，造成性能下降；建议 `seq-length / context-parallel-size > 8k` 以获得最佳效果。
- **判定公式（原文）**：$S / (T\alpha) \geq 1 / (W\beta)$，其中 $S$ = seq-length / context-parallel-size（单卡承载序列长度），$T$ = 芯片理论算力，$\alpha$ = 计算效率，$W$ = 理论通信带宽，$\beta$ = 带宽利用率。该不等式用于判断 CP 切分是否带来净收益——当单卡计算量相对通信开销足够大时，CP 才"划算"。
- **窗口参数效应（原文）**：`--cp-window-size` 增大时，通信与计算并发程度更高，但并发阶段会因片上内存带宽被通信与计算争夺而出现整体效率下降，需结合实际场景调参。

---

## 【表格解读】

**原文无表格**。原文以 shell 变量与命令行参数形式给出配置，未以表格形式列举参数。

---

## 【公式解读】

原文包含两处数学表述，逐字保留并解释：

1. **序列维度复杂度**：
$$O(S^2)$$
   - $O$：渐近复杂度记号。
   - $S$：序列长度（sequence length）。
   - 作用：刻画标准 Transformer 自注意力计算量/显存随序列的平方增长关系，是本特性要消除的瓶颈来源。

2. **CP 启用判据**：
$$\frac{S}{T\alpha} \geq \frac{1}{W\beta}$$
   - $S$：**单卡**实际承载的序列长度 = `seq-length / context-parallel-size`。
   - $T$：昇腾芯片的理论算力（如 FLOPS）。
   - $\alpha$：计算效率（实际算力 / 理论算力）。
   - $W$：设备间的理论通信带宽。
   - $\beta$：带宽利用率（实际带宽 / 理论带宽）。
   - 作用：左边 $S/(T\alpha)$ 表示单卡完成其分片计算所需时间（含效率折扣），右边 $1/(W\beta)$ 表示一次通信块传输所需时间（含带宽折扣）；当"计算时间 ≥ 通信时间"时，通信可被计算充分掩盖，CP 才带来净收益。这与文档给出的经验阈值 "`seq-length / context-parallel-size > 8k`" 在物理含义上自洽。

---

## 【关联】

- **依赖特性**：Flash Attention —— 文档明确指出"开启 Context Parallel 时需要同时开启 Flash Attention 特性，否则特性不支持"，二者存在硬性依赖。
- **算法后端**：通过 `--context-parallel-algo megatron_cp_algo` 复用 Megatron-LM 的 context parallel 实现，表明 mindspeed-mm 的 CP 方案在算法骨架上与 Megatron 的 CP 体系一致。
- **上游算法引用**：
  - Ring Attention with Blockwise Transformers for Near-Infinite Context（arxiv 2310.01889）—— 原始 Ring Attention 设计。
  - LoongTrain: Efficient Training of Long-Sequence LLMs with Head-Context Parallelism（arxiv 2406.18485）—— Double Ring Attention 的双窗口调度思想来源。
- **触发场景**：与"视频分辨率/帧数很大"的视频生成场景耦合，属于多模态生成链路中 DiT 训练阶段的扩展能力。
- **替代/对比方案**：文档将 CP 与"不开启序列并行（单卡 OOM/算力瓶颈）"以及"重计算（activation recomputation）"做对比：CP 在长序列场景用通信换显存，比重计算更高效，但会带来单步耗时增量。
- **内部链接**：原文文末无内部链接列表，本节关系均基于文中正文交叉引用梳理。

---

## 【使用方法】

**使用场景**：视频分辨率/帧数设置很大、单卡无法完成 DiT 计算时启用。

**启动方式**：在 `pretrain.sh` 中配置如下变量（原文示例，CP=8）：

```shell
CP=8

GPT_ARGS="
    --context-parallel-size ${CP} \
    --context-parallel-algo megatron_cp_algo \
    --use-cp-send-recv-overlap \
    --cp-window-size [int] \
    --megatron-cp-in-bnsd \
    --attention-mask-type [str] \
...
"
```

**参数说明（原文逐条）**：

| 参数 | 必选/可选 | 行为 |
|---|---|---|
| `--context-parallel-size ${CP}` | 必选 | CP 切分数（示例 8） |
| `--context-parallel-algo megatron_cp_algo` | 必选 | 选用 Megatron CP 算法 |
| `--use-cp-send-recv-overlap` | **可选，建议开启** | 启用 send/recv overlap |
| `--cp-window-size [int]` | **可选**，缺省 1 | 1=原始 Ring Attention；>1=Double Ring Attention；须满足 `cp_size % window_size == 0` |
| `--megatron-cp-in-bnsd` | **可选，建议开启** | 切换至 `[B,N,S,D]` 格式以提升性能（默认 `fa_layout` 为 "sbh"） |
| `--attention-mask-type [str]` | 必选 | `general`=全 attention；`causal`=causal attention |

**注意事项（原文）**：
1. 必须同时开启 Flash Attention。
2. `seq-length / context-parallel-size > 8k` 才建议启用 CP，否则通信占比过大反而劣化性能。
3. `--cp-window-size` 增大虽提升并发度，但片上内存带宽被通信与计算抢占，需实测调优。
