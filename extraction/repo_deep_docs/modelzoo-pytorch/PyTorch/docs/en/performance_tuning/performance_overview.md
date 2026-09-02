# Performance Overview

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/docs/en/performance_tuning/performance_overview.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/docs/en/performance_tuning/performance_overview.md

# 一体化深度解读:Performance Overview

---

## 【定位】

这篇文档是 modelzoo-pytorch 性能调优知识库的**顶层概览文档**,它在一篇文档内同时完成两件事:(1) 给出"性能"在 Ascend NPU/GPU 训练语境下的统一定义——单批次端到端训练时间,以及(2) 建立一套**按优先级排序的评估指标体系**(Throughput → 单步迭代时间 → Linearity → 内存占用 → 带宽利用率 → 训练效率 → FLOPS → 算力利用率),作为后续各项调优手段(recompute、pipeline/tensor/data 并行、通信优化等)的度量基线。

---

## 【技术要点】

1. **性能定义**: 文档明确将"性能"定义为完成**一个 batch 的端到端训练**所需时间(含一次 forward + backward + optimizer + post-processing),而非整个训练任务的 epoch 时间;这一选择是为了**屏蔽不同模型在数据量/epoch 数上的差异**,使性能指标具备可比性。
2. **单批次时间分解(6 段)**:
   `Total single-batch time = Data loading + Model forward/backward + Optimizer + Model post-processing + Communication + Scheduling`
   其中 Communication 在 PyTorch 特定重叠机制下只计入**未被计算掩盖的部分**,Scheduling 特指 CPU 向 NPU 分发指令调用 kernel 的开销。
3. **指标优先级(原文排序)**: Throughput > Single-step iteration time > Linearity > Memory usage > Bandwidth utilization > Training efficiency > FLOPS > Computing power utilization(此排序决定了调优时**先看 throughput、再看单步时间**的取舍逻辑)。
4. **最优 batch size 选取**: 通过二分搜索逼近 Ascend NPU 的内存上限(填满 memory);默认值建议为 **16 的倍数**——这一选择关系到 recomputation、pipeline/tensor 并行与 micro-batch 比例的整除性。
5. **Throughput 公式**: `Throughput = (BS × N) / step_time`,其中 `BS` 为每个 data-parallel 维度的 batch size,`N` 为集群中 data-parallel 维度规模,`step_time` 为分布式集群完成一个总 batch 的秒数。
6. **Token 维度换算(原文示例 GLM-10B)**: 25 samples/s × max_seq_len=1024 = **25600 tokens/s**;NLP 定形任务用 `seq_len` 把 samples/s 折算为 tokens/s。
7. **Linearity(线性度)取值区间 0–1**: 越接近 1 越好;**低于 0.8**(排除数据 I/O 和 CPU 自身因素后)即可判定分布式训练存在**通信瓶颈**,此时再去堆通信带宽对整体性能**提升有限**。
8. **Transformer 单层 FLOPS 估算**: 单层 forward = `24Bsh² + 4Bs²h` FLOPS(attention 的 Q/K/V 变换 6Bsh² + attention 矩阵 2Bs²h + attention over values 2Bs²h + post-attention 线性投影 2Bsh² + FFN 16Bsh²),backward 约为 forward 的 **2 倍**(需对 input 与 weight 张量同时求梯度)。

---

## 【关键机制与数据】

### 工作原理与数据流

- **End-to-end 单步训练 = 单次 iteration**: 从 CPU dispatch kernel、读数据、做 forward、做 backward、做 optimizer.step、做 post-processing、跨设备同步——所有这些**累加在一起**才构成"一次迭代"。
- **数据流(从冷端到热端)**: 硬件存储 → CPU 读取 → CPU 预处理(编解码等) → 传至 device(NPU/GPU);在多设备分片场景下,还需把数据从加载所在设备**广播**到其他设备,这部分广播耗时也归入 "Data loading time"。
- **通信与计算的重叠**: PyTorch 允许 communication 与 computation 在时间轴上 overlap,因此 communication time 在文档定义中**专指"未被计算掩盖"的通信耗时**;反之若 communication 被 compute 完全 hide,则这部分通信不计入性能瓶颈。
- **Linearity 的物理含义**: 等于 `多机/多卡总吞吐 ÷ (单机/单卡吞吐 × 卡数)`,本质是衡量 scaling 效率;接近 1 表示通信不构成瓶颈。
- **算力利用率**: `实际每秒 FLOPS ÷ 标称 FLOPS`;文档以 Transformer 为典型大模型 workload,给出 `F = forward FLOPS` 作为**实际 FLOPS 的下界**(vector op 与 padding 引入的少量额外计算未计入,占比极小)。

### 关键数字(原文)

- **batch size 默认建议**: 16 的倍数(原文:"a default batch size that is a multiple of 16 is more reasonable")。
- **Linearity 阈值**: < 0.8 视为存在通信瓶颈(原文:"when linearity is low, for example, less than 0.8…")。
- **GLM-10B 样例吞吐**: 25 samples/s × 1024 = **25600 tokens/s**(原文:"can process over 20,000 tokens per second",此处 "over 20,000" 是因为 25600 > 20000,文档用 ">20,000 tokens/s" 表述)。
- **Transformer backward / forward FLOPS 比**: 2:1(原文:"The backward pass requires twice this number of FLOPS")。
- **指标优先级文字**: Throughput > Single-step iteration time > Linearity > Memory usage > Bandwidth utilization > Training efficiency > Floating-point operations per second > Computing power utilization(逐字保留)。

---

## 【表格解读】

**原文无表格**(文中只有通过 `![](../figures/...)` 引用的 PNG 图片形式的公式图,没有 markdown 表格)。

---

## 【公式解读】

### 公式 1: 单批次总时间分解

```
Total single-batch time = Data loading time + Model forward and backward time 
                          + Optimizer time + Model post-processing time 
                          + Communication time + Scheduling time
```

- **Data loading time**: 从硬件存储→CPU 读取→CPU 预处理(编解码)→传到 device;多设备分片时还含**数据广播**时间。
- **Model forward and backward time**: forward 计算 + backward 对输入与权重求导。
- **Optimizer time**: 参数更新(`optimizer.step()` 之类)。
- **Model post-processing time**: optimizer 之后的轻量后处理或**必要的同步操作**,通常与具体模型强相关。
- **Communication time**: **节点内 + 节点间**通信耗时,但**只计未被计算掩盖的部分**(PyTorch 重叠机制所致)。
- **Scheduling time**: CPU 把指令 dispatch 到 NPU 上调用 kernel 的耗时(主机端开销,不发生在 device 内部)。

---

### 公式 2: Throughput(对应 `throughput_metrics_fig_01.png`)

$$
\text{Throughput} = \frac{BS \times N}{\text{step\_time}}
$$

- `BS`: **每个 data-parallel 维度的 batch size**,即 DP 内每张卡处理的样本数。
- `N`: **集群中 data-parallel 维度规模**,即参与数据并行的卡/节点数。
- `step_time`: 在分布式集群上执行**一个总 batch size** 所用的秒数(秒)。
- 物理含义: **单位时间内整个集群能处理的训练样本总数**;`BS × N` 是全局 batch size。

---

### 公式 3: NLP tokens/s 换算(对应 `throughput_metrics_fig_02.png`)

$$
\text{Throughput}_{\text{tokens/s}} = \text{Throughput}_{\text{samples/s}} \times \text{seq\_len}
$$

- 适用于 NLP 任务**定形(fixed-shape)**输入;CV 任务不适用此换算,仍用 samples/s。
- 原文例子: GLM-10B, throughput = 25 samples/s, max seq_len = 1024 → 25 × 1024 = **25600 tokens/s**。

---

### 公式 4: Linearity 定义(对应 `linearity_metrics_fig_01.PNG`)

$$
\text{Linearity} = \frac{\text{Total throughput of multi-device / multi-node setup}}{\text{(Single-device throughput)} \times (\text{Number of devices})}
$$

- 即**实测 scaling 总吞吐 / 理想线性 scaling 总吞吐**,取值 0–1。
- 越接近 1 表示 scaling 越高效、通信不是瓶颈;低于 0.8 提示通信瓶颈(原文)。

---

### 公式 5: Linearity 单位(对应 `linearity_metrics_fig_02.PNG`)

- NLP 模型: tokens/s 为基本单位。
- CV 模型: samples/s 为基本单位。

---

### 公式 6: Linearity 变换式(对应 `linearity_metrics_fig_03.PNG`)

$$
\text{Linearity} = \frac{\text{Total throughput (multi-device)}}{\text{Single-device throughput} \times \text{Device count}}
$$

- 与公式 4 等价,**逐项重排**得到;分子分母位置不变,这是从"speedup 视角"对 linearity 的等价表述。

---

### 公式 7: Transformer 单层 FLOPS 估算(原文文字式,逐字保留)

- **单次矩阵乘** $A_{m\times k} \times X_{k \times n}$: 需要 `2mnk` 浮点运算(multiply-add 算 2 次操作)。
- **Attention 模块** 各部分 FLOPS:
  - K/Q/V 变换: `6Bsh²`
  - attention 矩阵计算: `2Bs²h`
  - attention over values: `2Bs²h`
  - post-attention 线性投影: `2Bsh²`
- **FFN(2 层前馈网络)**: hidden 扩展 `h → 4h`,再压缩 `4h → h`,共 `16Bsh²` FLOPS。
- **单 Transformer 层 forward 总 FLOPS**:

$$
F_{\text{layer, fwd}} = 24Bsh^2 + 4Bs^2 h
$$

- **Backward FLOPS**(对输入和权重都求梯度):

$$
F_{\text{layer, bwd}} = 2 \times F_{\text{layer, fwd}}
$$

- 符号定义(原文): `B` = batch size,`s` = sequence length,`I` = Transformer 层数,`h` = hidden size,`V` = vocabulary size。
- **整体 workload 备注**: `F` 表示一次 iteration 的 FLOPS,作为**实际 FLOPS 的下界**(下界),vector op 与 padding 引入的少量额外计算未计入。

> 注: 原文在介绍 `F` 时还提及"if we use activation recomputation, this requires an ad…"(文档在该处被截断,recompute 引入的额外 FLOPS 倍数在所提供的原文中未给出完整公式,本文不臆造)。

---

## 【关联】

本文档是性能调优知识树的**根节点**,定义了 6 段时间分解与 8 级指标优先级,为下游所有具体调优页面提供度量基准。从文末信息看(原文档末尾被截断),后续内容应与下列模块/特性直接对接:

- **Data loading time** ↔ 数据加载/数据预处理/dataparallel 数据广播 相关页面;
- **Model forward and backward time** ↔ 算子融合、自动微分、activation recomputation 相关页面;
- **Optimizer time** ↔ 优化器并行、ZeRO/梯度分片 相关页面;
- **Communication time** ↔ 集合通信库( HCCL 等)、通信-计算 overlap、tensor/pipeline/expert 并行 相关页面;
- **Scheduling time** ↔ host 侧 dispatch、kernel launch 优化、图编译(graph engine) 相关页面;
- **Throughput 公式中的 BS / N** ↔ data parallel、tensor parallel、pipeline parallel 维度规划与 micro-batch 配置;
- **Linearity < 0.8 的判定** ↔ 通信瓶颈定位与带宽/拓扑优化;
- **Transformer FLOPS 估算** ↔ 大模型 workload 的 MFU/算力利用率 profiling 与 recompute 开关决策。

由于文末"内部链接"信息在原文标注为**(无)**,以上关联是基于文档自身段落主题的下游映射,非直接引用原文档链接。

---

## 【使用方法】

**原文未涉及具体的启用命令、环境变量或 API 配置项。**

本文档为概念性/定义性 overview,不含 `torchrun`/`python -m`/`msrun`/`export …=` 等具体启动命令,也不含任何 yaml/JSON 配置字段。要把文档中的指标落地,需要参考该知识库后续的具体调优页面(如 recompute 启用、并行配置、通信 overlap 设置等),并在 PyTorch 训练脚本中:

1. 用**计时工具**(如 `torch.cuda.Event`、profiler 或 NPU 对应 profiler)分别测量 Data loading / Forward+Backward / Optimizer / Post-processing / Communication / Scheduling 6 段,验证它们对应到文档的时间分解;
2. 在 Ascend NPU 上**二分搜索最优 batch size 至显存上限**,且保证为 **16 的倍数**(原文建议);
3. 在选定的最优 BS 下,按公式 2 计算 throughput,再按公式 3 在 NLP 场景换算为 tokens/s(例如 GLM-10B 的 25600 tokens/s 级别);
4. 跑多机/多卡对照实验,用公式 4 计算 linearity:**> 0.8 视为通信不构成瓶颈**,< 0.8 即进入通信优化分支;
5. 用公式 7 估算 Transformer 单层/整网 FLOPS,除以标称 FLOPS 得到算力利用率,作为高优调优对象的筛选依据。

## 图文联合解读

- `throughput_metrics_fig_01.png`: **图文联合解读：**

1) **图像内容**：手绘公式草图，含两侧对等的多项式符号（形如 Σx 的项）、中央等号"="、左右两侧下方各一组波浪/求和类表达式，整体呈"左项 = 右项"的等式结构。

2) **论证结论**：单批次训练总耗时可分解为多个独立且可叠加的子耗时之和，各项之间为线性相加而非嵌套依赖。

3) **与文档关系**：直接对应文档中"Total single-batch time = Data loading + Forward/Backward + Optimizer + Post-processing + Communication + Scheduling"的公式，将文本描述的耗时拆解结论以可视化等式呈现，强化"分阶段测量与优化"的论点。
- `throughput_metrics_fig_02.png`: **图文联合解读：**

**1）图中所画：** 并非技术结构图，而是以书法/笔触风格艺术化渲染的文本公式 "tokens ÷ sample × seq_len"，含"="和"×"符号，无数据流、节点或标注。

**2）论证结论：** 严格来说此图未呈现技术论证。若按字面解读，公式表达的是 token 数、样本数与序列长度的换算关系（即每样本 token 数 = seq_len，或总 tokens = samples × seq_len）。

**3）与文档关系：** 文档论证单 batch 训练时间由数据加载、前后向、优化器、后处理、通信、调度六部分组成。该公式可辅助估算**数据加载时间**所涉的数据量规模，但作为配图未能直观说明任一时间分量的占比或瓶颈，与正文论点缺乏直接对应；更像是装饰性标题图或渲染异常的占位图。
- `linearity_metrics_fig_01.PNG`: 1) **图示内容**：公式定义"单节点线性度"=（单节点/多设备总吞吐）÷（单设备吞吐×设备数），分式结构直观呈现"实际值/理论理想值"的比值关系。

2) **技术结论**：衡量多设备并行训练的扩展效率。线性度=1为理想线性扩展；<1说明存在通信、同步等开销导致加速比未达预期。

3) **与文档关系**：呼应前文将"通信时间"列为单批次耗时组成部分的论点，该公式将抽象的时间开销量化为可计算的扩展效率指标，为性能评估提供度量基准。
- `linearity_metrics_fig_02.PNG`: **图文联合解读：**

1）图中展示了一个分数式公式：**Cluster linearity = 多节点多设备总吞吐 / (单设备吞吐 × 设备数 × 集群节点数)**。

2）论证了分布式训练扩展效率的量化方法：用实际多机多卡总吞吐与"理想线性扩展"的理论值之比，来衡量集群并行训练的可扩展性，比值越接近1则扩展效率越好。

3）与文档论点呼应：文档将单batch耗时拆解为数据加载、前后向、优化器、通信等多部分（强调"通信时间"对多设备场景影响显著），而本图给出了在多节点多设备层级上评估这些开销综合效果的宏观指标——集群线性度，是单batch耗时拆解在分布式维度的总评估标尺。
- `linearity_metrics_fig_03.PNG`: **图文联合解读：**

1）图示内容：展示"集群线性度（Cluster linearity）"的公式定义，即多节点多设备总吞吐量除以单设备吞吐量与集群节点数之积。

2）技术结论：该公式用于量化分布式训练的扩展效率，理想值为1.0，表示线性扩展；小于1则说明多机并行存在通信或调度开销损失。

3）与文档关系：呼应文档对"性能即单批次训练时间"的定义，将单设备基线与多节点并行场景关联，为评估端到端训练中"通信时间+调度时间"占比提供量化指标。
- `computing_power_utilization_metric_fig_02.png`: # 图文联合解读

## 1) 图中内容
图中呈现一张手绘风格的流程示意图（图像较模糊），可辨识出一个由箭头串联的纵向处理管线，包含若干椭圆形节点与文字标注，整体勾勒出"数据输入→多级处理→输出"的串行链路结构。

## 2) 技术结论
该图论证：单批次训练耗时并非单一环节决定，而是由**数据加载、前向/反向、优化器、后处理、通信、调度**等多个串行子过程累加构成；任一节点都可能成为端到端瓶颈。

## 3) 与文档关系
该图作为文档"Performance Concepts"章节的视觉锚点，将公式 **Total = Data loading + FWD/BWD + Optimizer + Post-processing + Communication + Scheduling** 具象化为可读的流水线示意图，呼应文中"性能需从模型视角、按单 batch 测量"的论点。
- `computing_power_utilization_metric_fig_03.png`: # 图文联合解读

**1) 图中内容**
图示为一个数学公式（图像倾斜），形如 *T = T_obs · (s / T_op) · T_s*，其中 T 为总时间，T_obs 为观测项，T_op 为操作时间项，s 为缩放因子，T_s 为步长时间，整体呈分数嵌套结构。

**2) 论证结论**
该公式将单批次总耗时分解为多个可独立测量项的乘积关系，论证"端到端单步训练耗时可由各子环节耗时按比例叠加/相乘得到"——即性能具有**可分解性与可测量性**。

**3) 与文档论点关系**
直接对应文档给出的 **Total single-batch time = Data loading + Forward/Backward + Optimizer + Post-processing + Communication + Scheduling**，以公式形式量化呈现"性能 = 各阶段耗时之和"的核心论断，为后续性能优化提供数学建模基础。
- `computing_power_utilization_metric_fig_04.png`: **图文联合解读：**

1）图示内容：图像呈现一个单批次训练时序/流程图，自上而下串联多个标注模块（含"Epoch"等训练阶段标签），中间以渐变色条串联，左侧为组件入口，箭头与连线指示时间先后与数据流向。

2）技术结论：将"单批次总时间"分解为数据加载、前向反向、优化器、后处理、通信、调度等独立子阶段，并以时序图形式呈现各阶段累积与串并联关系。

3）文档关系：图示与文末公式（Total time = Data loading + Forward/Backward + Optimizer + Post-process + Communication + Scheduling）一一对应，把抽象文字定义可视化为可定位、可测量的时间线段，支撑"以单批次为粒度、端到端评估性能"的核心论点。
- `communication_performance_metrics_fig_01.png`: **图文联合解读：**

1）图示内容：图为一个公式图，定义了 **Wait ratio = Wait time / (Wait time + Transit time)**，其中 Wait time（等待时间）在分子，Transit time（传输时间）与 Wait time 之和在分母。

2）技术结论：该比值用于衡量通信开销在总耗时中的占比。Wait time 反映计算与通信未充分重叠的"空闲等待"段，Transit time 为真实通信耗时；比值越低，说明计算/通信重叠越好、通信效率越高。

3）与文档关系：呼应文档"Communication time"是单 batch 总耗时的组成之一。该图为评估通信调度效率提供了量化指标，佐证了文档关于端到端训练时间由多部分构成、性能优化需关注各阶段（包括通信）开销的论点。
- `communication_performance_metrics_fig_02.png`: **图文联合解读：**

1) 图中呈现一个公式结构：左侧标注"SDMA Communication"，右侧以除号拆分为分子"small data"与分母"small transit time"，即 **SDMA通信 = 小数据量 / 小传输时间**。

2) 该图论证了SDMA通信的性能特征：当数据量小且传输时延短时，SDMA模式具有高效的传输效率，适合作为衡量通信开销的基准模型。

3) 与文档呼应：文档将"通信时间"列为单batch总耗时的关键组成项之一，此图正是对"通信时间"维度的量化刻画，为后续性能剖析与优化提供理论公式支撑。
- `communication_performance_metrics_fig_03.png`: **图文联合解读：**

1) **画面结构**——以中央横向时间轴为主线，左侧标注"RDMA"，右上方为"Training data"，右下方依次标注"Training time"与"Transfer time"，配以刻度分段，呈现数据加载—传输—训练的时间分配关系。

2) **技术结论**——RDMA 技术通过旁路 CPU 直接内存访问，可压缩数据传输耗时，使单 batch 时间内更多预算留给模型训练，提升端到端效率。

3) **与文档论点关系**——图示对应文档中"Data loading time"与"Communication time"环节的可视化补充，呼应"Total single-batch time"分解公式，强调优化传输路径对整体性能的关键作用。
