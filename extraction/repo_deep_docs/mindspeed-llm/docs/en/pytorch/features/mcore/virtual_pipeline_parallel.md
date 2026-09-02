# Virtual Pipeline Parallelism

> 仓 `mindspeed-llm` · 路径 `docs/en/pytorch/features/mcore/virtual_pipeline_parallel.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-llm/docs/en/pytorch/features/mcore/virtual_pipeline_parallel.md

# Virtual Pipeline Parallelism 文档深度解读

## 【定位】
本篇文档描述 Megatron 风格的**虚拟流水线并行 (Virtual Pipeline Parallelism, VPP)** 能力,用于解决 PipeDream 流水线并行因 chunk 过大而残留较多 pipeline bubble、计算资源利用率偏低的问题,通过在不增加物理设备的前提下进一步切分流水线 stage, 以更多通信开销换取更低的 bubble 比例。

---

## 【技术要点】
1. **核心矛盾**: PipeDream 流水线并行中 chunk 过大 → 执行过程中残留大量 pipeline bubble → 计算资源仍有提升空间。
2. **解决思路**: 在**设备数不变**的前提下, 将每个 pipeline stage 进一步细分为多个"虚拟 stage", 用更多的跨 stage 通信换得更低的 bubble ratio。
3. **Stage 切分规则**: 总虚拟 stage 数 = `pipeline_parallel_size × virtual_pipeline_parallel_size`; 每个 stage 的层数 = `总层数 / (PP × VPP)`,因此要求 `总层数 % (PP × VPP) == 0`,亦即文档中给出的 `L % N == 0`。
4. **示例配置**: 16 层模型, `TP=1`, `PP=4`, `VPP=2` → 总共 `4×2=8` 个 stage, 每 stage `16/8=2` 层。
5. **Layer 分配 (原文):**
   - Device 0: `[1, 2]` `[9, 10]`
   - Device 1: `[3, 4]` `[11, 12]`
   - Device 2: `[5, 6]` `[13, 14]`
   - Device 3: `[7, 8]` `[15, 16]`
6. **Forward 顺序 (原文):** `device 0 → device 1 → device 2 → device 3 → device 0 → device 1 → device 2 → device 3`, 即同一物理设备上的多个虚拟 stage 按序串接, 数据需要回到对应物理 device 上继续计算。

---

## 【关键机制与数据】
- **工作原理 (原文)**: 在不改变物理设备数的情况下, 把工作负载切分成比 PP 规模更多的 pipeline stage, 以"额外通信"换"更低的 bubble ratio"。本质是把原来较粗的 chunk 切成多个细粒度 stage, 让流水线更细、更均匀, 减少空闲等待。
- **数据流 (原文)**: 以前述 16 层、`PP=4`、`VPP=2` 为例, 数据沿 `device 0→1→2→3→0→1→2→3` 的顺序穿过所有 8 个虚拟 stage。可以看到 forward 会两次回到 device 0 / 1 / 2 / 3, 这就是 VPP 引入的"额外跨 stage 通信"的来源。
- **性能数据**: 原文未给出具体的 bubble ratio 数值、性能百分比、吞吐或加速比等量化指标, 仅定性说明"bubble ratio decreases further (原文)"。

---

## 【表格解读】
原文无表格。

---

## 【公式解读】
原文无公式。

文档中存在两个可视为约束的表达式, 逐字保留并解释:
- `总 stage 数 = pipeline_parallel_size × virtual_pipeline_parallel_size = 4 × 2 = 8`
  - 含义: 物理 PP 大小与虚拟 PP 大小相乘得到逻辑上的 stage 总数。
- `每 stage 层数 = 总层数 / 总 stage 数 = 16 / 8 = 2`
  - 含义: 模型层被均分到所有虚拟 stage 上。
- 使用约束: `L % N == 0`, 即总层数 `L` 必须能被每虚拟 stage 的层数 `N` 整除, 否则无法均分。

---

## 【关联】
- 与 **PipeDream pipeline parallelism** 直接对照: 文档指出 PipeDream 的 chunk 过大, VPP 是对其的改进方向, 沿用其流水线并行基础但做了更细粒度切分。
- 与 **Megatron-LM Tensor Parallel** 的耦合点: 示例中设置 `tensor parallel size = 1`, 说明 VPP 与 TP 在层/设备划分上是正交关系; VPP 只在 PP 维度进一步切层, 不影响 TP 的张量切分。
- 与**权重保存/加载**的耦合: 原文 Notes 明确指出 "Megatron virtual pipeline parallelism (VPP) affects the weight sharding scheme (原文)", 因此 VPP 配置一致性是 checkpoint 正确加载的前置条件。
- 原始论文出处: `https://people.eecs.berkeley.edu/~matei/papers/2021/sc_megatron_lm.pdf` (Megatron-LM 论文, 与本框架 VPP 实现对齐)。

文末无内部链接。

---

## 【使用方法】
- **启用命令 (原文)**: `--num-layers-per-virtual-pipeline-stage N`
  - 该参数指定每个虚拟 pipeline stage 包含的层数 `N`。
  - 必须满足的约束 (原文): `L % N == 0`, 即模型总层数 `L` 必须能被 `N` 整除。
- **配套配置**: 与 `pipeline-parallel-size` 一起使用 (以原文示例而言, `PP=4`, `VPP=2` 才能形成 8 个 stage、每 stage 2 层)。
- **权重相关注意事项 (原文)**: 保存/加载权重时, VPP 配置必须保持一致, 否则权重无法正确加载。

## 图文联合解读

- `virtual-pipeline.png`: **图文联合解读：**

1) **图中内容**：4个Device的时间轴调度甘特图。蓝色方块为Forward Pass，浅绿色为Backward Pass，灰色为bubble/通信，编号1–16代表microbatch。垂直黑线将调度对称分为两半，呈现交错执行模式——同一device先做stage1再回做stage2，形成"循环交错"1F1B调度。

2) **论证结论**：通过将4个物理stage拆为8个虚拟stage（VPP=2），每个device先后处理两个不连续层段，使前后向计算在时序上更紧密交错，灰色气泡区域相比标准PP明显减少。

3) **与文档关系**：直观印证文档"Further subdivide the computation to reduce bubbles"的核心论点，即用额外通信换更低气泡率，提升计算资源利用率。
