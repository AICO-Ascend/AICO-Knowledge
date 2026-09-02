# 性能概述

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/docs/zh/performance_tuning/performance_overview.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/docs/zh/performance_tuning/performance_overview.md

# 「性能概述」一体化深度解读

---

## 【定位】

本篇文档系统定义了在 GPU / NPU（昇腾）等 AI 加速平台上,基于 PyTorch 完成一次端到端模型训练所涉及的性能概念、组成拆解与性能指标体系,为后续的「性能调优」「算子调优」「通信调优」「流水并行调优」等子专题提供统一的衡量基准和分析口径。

---

## 【技术要点】

1. **性能定义与单 batch 时间组成**
   - 性能 = 在指定模型与输入数据下,完成 **一个 batch** 端到端训练所花费的时间。
   - **单 batch 总时间 = 数据加载时间 + 模型前向和反向时间 + 优化器时间 + 模型后处理时间 + 通信时间 + 调度时间**。

2. **性能指标优先级排序**(从高到低):
   吞吐率 > 单步迭代时间 > 线性度 > 内存占用 > 带宽占比 > 训练效率 > 浮点计算次数每秒 > 算力利用率。

3. **吞吐率(Throughput)**
   - 单位时间(默认 1s)内可处理的最大训练样本数;**NLP 以 tokens/s、CV 以 samples/s** 为单位。
   - **最佳 batch size 经验法则:达到昇腾处理器对该数据类型的内存上限**;推荐用**二分搜索**寻找。
   - **默认 batch size 取 16 的倍数**,因为它会影响重计算、Pipeline 并行、Tensor 并行以及 micro batch 的配比。
   - **吞吐率公式**:Throughput = BS × N / step_time。
   - **tokens/s = samples/s × seq_len**;原文示例:GLM10B 25 samples/s × 1024 seq_len = **25600 tokens/s**。

4. **线性度(Linearity / 加速比)**
   - 单卡→多卡、单节点→集群的扩展效率,取值 **0~1**,**越接近 1 越好**。
   - 当线性度 **< 0.8** 时(排除数据 IO / CPU 因素后),可判定分布式通信存在瓶颈。

5. **算力利用率(Computing Power Utilization)**
   - = 实际消耗算力 / 集群标称算力。
   - 针对 GPT 类 Transformer 模型,给出每个 layer FLOPs 的逐项分解(详见公式解读)。
   - 重计算(activation recomputation)会增加一次额外的前向 FLOPs。
   - 算力利用率为 1 时,理想 step_time = F / (C × N)。

6. **通信性能指标**
   - **wait_ratio 慢节点识别**:max_wait_ratio − min_wait_ratio 与 **wait_ratio_threshold = 0.2** 比较;差值 > 0.2 时认为出现慢节点,慢节点为 min_wait_ratio(等待时间短)对应的卡。
   - **DMA 类型**:RDMA(跨节点)+ SDMA(节点内);通信带宽 = data / transit_time。

---

## 【关键机制与数据】

### 性能概念
- 原文明确"性能"是指**站在模型角度**,完成**单步训练过程**的时间,排除了 epoch 与数据总量级别的差异干扰。
- 单 batch 时间的六个组成部分是后续所有性能调优(数据加载优化、计算图优化、通信掩盖、调度加速)的对标维度。
- 端到端训练链路在文档中被显式拆解为:**CPU 侧数据预处理 → 加载到 device → Forward → Backward → Optimizer → 后处理 → 同步**,各阶段均对应可优化空间。

### 性能指标优先级机制
- 原文按业务影响力排序,吞吐率与单步迭代时间作为最高优先级指标;算力利用率位列最后但与吞吐率成正比,用于纵向反映性能问题。

### 吞吐率(原文数据)
- 原文示例:GLM10B 模型,吞吐率 25 samples/s × 1024 = **25600 tokens/s**(≈每秒 2 万多 tokens)。

### 算力利用率中的计算量分解(原文逐项)
- K/Q/V 变换:**6Bsh²**
- Attention 矩阵计算:**2Bs²h**
- 对 V 做 Attention 计算:**2Bs²h**
- Attention 后线性投影:**2Bsh²**
- FFN(放大到 4h,再缩小到 h):**16Bsh²**
- 每层前向合计:**24Bsh² + 4Bs²h**
- 反向 = 2× 前向;使用重计算需在反向前再加一次前向。

### 通信指标阈值(原文)
- **wait_ratio_threshold = 0.2**(当前设定值)。

---

## 【表格解读】

**原文无表格**。原文中所有公式与指标对比均通过 `figures/*.png` 图片承载,未出现 markdown 表格结构。

---

## 【公式解读】

> 说明:原文中所有公式均以 PNG 图片形式嵌入,以下公式按原文文字描述逐字还原(LaTeX / 伪代码形式)。

### ① 单 batch 总时间组成

$$
T_{\text{batch}} = T_{\text{data}} + T_{\text{fwd/bwd}} + T_{\text{opt}} + T_{\text{post}} + T_{\text{comm}} + T_{\text{sched}}
$$

| 符号 | 含义 |
|---|---|
| $T_{\text{batch}}$ | 单 batch 总时间 |
| $T_{\text{data}}$ | 数据加载时间(含读盘、CPU 预处理、跨卡广播) |
| $T_{\text{fwd/bwd}}$ | 模型前向 + 反向时间 |
| $T_{\text{opt}}$ | 优化器参数更新时间 |
| $T_{\text{post}}$ | 模型后处理 / 必要同步时间 |
| $T_{\text{comm}}$ | 未被计算掩盖的通信时间 |
| $T_{\text{sched}}$ | CPU 指令调度到 NPU Kernel 的时间 |

---

### ② 吞吐率(throughput_metrics_fig_01)

$$
\text{Throughput} = \frac{BS \times N}{\text{step\_time}}
$$

| 符号 | 含义 |
|---|---|
| $BS$ | batch size per DP,每个数据并行维度的 batch size |
| $N$ | 集群中数据并行维度的大小 |
| $\text{step\_time}$ | 分布式集群中执行完一个 total batch 的时间(单位 s) |

---

### ③ tokens/s 换算(throughput_metrics_fig_02)

$$
\text{tokens/s} = \text{samples/s} \times \text{seq\_len}
$$

| 符号 | 含义 |
|---|---|
| $\text{seq\_len}$ | NLP 任务的最大序列长度 |

---

### ④ 线性度定义(linearity_metrics_fig_01 / fig_02 / fig_03)

$$
\text{linearity\_fig01} = \text{单机多卡总吞吐率}
$$

$$
\text{linearity} = \frac{\text{集群总吞吐率}}{\text{单机性能} \times \text{集群规模}}
$$

$$
\text{linearity\_fig03} = \text{fig\_01 与 fig\_02 变换后的等价表达}
$$

> 原文:取值 0~1,越接近 1 越好;< 0.8 时(排除数据 IO 与 CPU 因素)可判定分布式通信存在瓶颈。

---

### ⑤ Transformer 每层 FLOPs(逐项汇总)

前向:

$$
F_{\text{layer, fwd}} = \underbrace{6Bsh^2}_{\text{K/Q/V}} + \underbrace{2Bs^2h}_{\text{Attn matmul}} + \underbrace{2Bs^2h}_{\text{Attn on V}} + \underbrace{2Bsh^2}_{\text{Proj}} + \underbrace{16Bsh^2}_{\text{FFN}} = 24Bsh^2 + 4Bs^2h
$$

反向(2× 前向):

$$
F_{\text{layer, bwd}} = 2 \times (24Bsh^2 + 4Bs^2h) = 48Bsh^2 + 8Bs^2h
$$

启用重计算(再附加一次前向):

$$
F_{\text{layer, total}} = F_{\text{layer, fwd}} + F_{\text{layer, bwd}} + F_{\text{layer, fwd}} = 3F_{\text{fwd}} + 2F_{\text{fwd}} = 5 \times (24Bsh^2 + 4Bs^2h)
$$

> 原文:此 FLOPs 为真实统计的下界(lower bound),实际还包含少量 vector 算力与 padding 带来的额外算力。

---

### ⑥ I 层 GPT 的 iteration 总 FLOPs(computing_power_utilization_metric_fig_03)

$$
F = I \times \bigl(F_{\text{layer, fwd}} + F_{\text{layer, recompute}} + F_{\text{layer, bwd}}\bigr)
$$

| 符号 | 含义 |
|---|---|
| $I$ | Transformer 层数 |
| $F$ | 一个 iteration 消耗的计算量(FLOPs,lower bound) |
| $B$ | batch size |
| $s$ | sequence length |
| $h$ | hidden size |
| $V$ | vocabulary size(图公式中通常也包含词表相关项,如 lm_head 的 2Bsh·V) |

---

### ⑦ 集群算力利用率(computing_power_utilization_metric_fig_04)

$$
\text{Util} = \frac{F}{C \times N \times \text{step\_time}}
$$

| 符号 | 含义 |
|---|---|
| $F$ | 单 iteration 真实消耗的 FLOPs |
| $C$ | 每块 AI 处理器的标称算力(FLOPS) |
| $N$ | 集群中 AI 处理器个数 |
| $\text{step\_time}$ | 单 iteration 时间 |
| $\text{Util}$ | 算力利用率,越接近 1 越理想 |

---

### ⑧ 通信带宽(communication_performance_metrics_fig_02 / fig_03)

$$
\text{BW}_{\text{sdma}} = \frac{\text{sdma\_data}}{\text{sdma\_transit\_time}}
$$

$$
\text{BW}_{\text{rdma}} = \frac{\text{rdma\_data}}{\text{rdma\_transit\_time}}
$$

| 符号 | 含义 |
|---|---|
| $\text{sdma\_data}$ / $\text{rdma\_data}$ | 节点内 / 跨节点传输的数据量 |
| $\text{sdma\_transit\_time}$ / $\text{rdma\_transit\_time}$ | 节点内 / 跨节点的传输耗时 |

---

### ⑨ 慢节点判定(通信)

$$
\max(\text{wait\_ratio}) - \min(\text{wait\_ratio}) > \text{wait\_ratio\_threshold} = 0.2
$$

成立时判定存在慢节点,**慢节点为 min_wait_ratio 对应的卡**(等待时间短、自身耗时长)。

---

## 【关联】

- 本篇是「**性能调优**」专题的入口 overview,后续子文档应围绕六大组成时间(数据加载 / 前向反向 / 优化器 / 后处理 / 通信 / 调度)展开。
- 算力利用率章节明确指向 **Transformer 类大模型**(GPT、GLM 等),与 modelzoo 中 LLM 模型构成直接对应关系。
- 线性度公式与「集群规模」「数据并行维度」绑定,自然衔接下游「分布式训练 / 流水并行 / 张量并行」调优章节。
- 通信性能指标中的 wait_ratio 阈值、RDMA/SDMA 概念,是后续「通信算子调优」「集合通信库(CCL)调优」的分析依据。
- 吞吐率公式中的 `BS`(batch size per DP)和「micro batch」措辞,呼应「流水并行调优」中 micro batch size 的概念。
- 文末注明「(无)」内部链接,意味着 overview 自身不直接交叉引用,但其指标体系被其他性能子文档引用。

---

## 【使用方法】

原文未涉及。

(本篇为概念定义与指标体系文档,不涉及具体启用方式、配置项或命令;具体的调优开关、配置参数、环境变量请见后续性能调优子专题文档。)

## 图文联合解读

- `throughput_metrics_fig_01.png`: # 图文联合解读

## 1) 图中内容
图像呈现**严重模糊**状态，依稀可辨若干数学公式片段——包含变量字符（如 M、BS、Time 等）、等号"="与除号横杠，以及右上角"÷"号结构，整体应为**吞吐率计算公式**的公式排版示意图（疑似 `Throughput = BS × 训练轮次样本数 / 总训练时间`）。

## 2) 论证结论
原本应论证：**通过给定最佳 batch size，用"样本处理量 ÷ 单位时间"即可量化 AI 集群的实际吞吐率**，强调公式中分子（批量大小）与分母（单步时间）的反比/正比关系。

## 3) 与文档论点的关系
该公式是文档中**"吞吐率"作为最高优先级性能指标**的核心量化工具——前文定义吞吐率为"单位时间内处理的最大训练样本数"，此处公式即为其工程化落点。

⚠️ **备注**：图片因模糊无法精确识读具体公式形式，建议替换为清晰版公式渲染图（如 LaTeX 输出）。
- `throughput_metrics_fig_02.png`: # 图文联合解读

## 1) 图中内容
图示为一个**吞吐率计算公式**，呈现"左边项 = 中间项 × 右边项"的结构：

- **左侧**：`tokens/s`（每秒钟处理的token数）
- **中间**：`sample/s`（每秒钟处理的样本数）
- **右侧**：`seq_len`（单样本序列长度）

三部分之间通过等号"="和乘号"×"连接，整体表示三者之间的乘法关系。

## 2) 论证的技术结论
该公式论证了**吞吐率的三要素分解关系**：模型训练吞吐率（tokens/s）等于单位时间处理的样本数（sample/s）乘以每个样本包含的token数量（seq_len）。即在固定batch size下，序列长度越长，每秒可处理的token总数越高，硬件算力被越充分地"喂"饱。

## 3) 与文档论点的关系
文档在"性能指标介绍"中明确将**吞吐率列为最高优先级指标**，并指出其定义是"单位时间内处理的最大训练样本数"。该公式正是这一概念的**量化实现**：

- 文档先论述了吞吐率定义（基于样本数），公式进一步把它**扩展到token级**度量；
- 与上文"单batch总时间"分解呼应：吞吐率是各组成时间（数据加载、前向反向、优化器等）的**倒数表征**；
- 为后文"最佳batch size""二分搜索""memory限制"等调优方法提供**量化基础**，说明seq_len作为公式中的关键变量，是实际调优时需要关注的维度之一。
- `linearity_metrics_fig_01.png`: **图文不一致警示：图片与文档内容不匹配**

1) **图中内容**：并非技术示意图，而是传统中文木刻印刷字样（疑似古籍文字）被排版成"左式 = 右式（上/下）"的分数公式外形，文字模糊难辨具体内容，**无任何标注、无数据流、无技术元素**。

2) **技术结论**：**无法论证任何技术结论**。图中无吞吐量公式、无batch size、无时间/样本量单位、无坐标系或流程箭头。

3) **与文档论点关系**：文档"吞吐率"小节明确给出计算公式应为：

$$\text{Throughput} = \frac{\text{BS}_{\text{total}} \times \text{iterations}}{\text{total time}}$$

涉及总批量、迭代次数、训练总时间等量化变量。而当前图片是古籍文字伪装的分数图，**与吞吐率公式无任何对应关系**。

**建议**：检查figures目录，应为带"BS_total / total time"等数学符号的吞吐率公式示意图，而非当前古籍文字图。请核实图源。
- `linearity_metrics_fig_02.png`: **图文联合解读：**

1）**图示内容**：公式表达"集群训练吞吐量 = 多机多卡总吞吐率 ÷ (单卡吞吐率 × 卡数 × 集群机器数量)"，分母体现单卡、卡数、机器数量三级扩展因子的乘积。

2）**技术结论**：衡量集群并行扩展时，总吞吐率相对理论上限（单卡能力 × 硬件规模）的衰减程度，反映分布式训练的并行效率与通信/调度开销损耗。

3）**与文档关系**：呼应"性能概念"中端到端单batch时间的拆解（通信、调度等组件均会损耗吞吐），支撑"吞吐率"作为最高优先级性能指标的定义，为多机多卡场景下的训练效率评估提供量化基线。
- `linearity_metrics_fig_03.png`: **图文联合解读：**

1）图中内容：公式"集群线性度 = 多机多卡总吞吐率 /（单机单卡吞吐率 × 集群机器数量）"，以分数形式定义集群线性度这一性能指标。

2）技术结论：该公式通过对比多机多卡总吞吐率与单卡吞吐率按机器数线性扩展的理论值，衡量分布式训练随节点扩展时性能是否接近理想线性增长，反映并行扩展效率。

3）与文档关系：文档将"线性度"列为优先性能指标之一，并强调吞吐率与batch size相关；本图正是为该指标给出量化定义，与前文吞吐率概念互补，共同构成集群训练性能评估的核心公式。
- `computing_power_utilization_metric_fig_02.png`: # 图文解读

**1) 图中内容**：旋转90°后可见吞吐量计算公式 `T = (1s × BS) / N`，即单位时间(1秒)内处理的batch样本数(BS)除以实际步数(N)再转换为吞吐率，右侧椭圆形可能表示时间维度。

**2) 技术结论**：论证了吞吐率（samples/s）= batch size × 步频，强调在已确定最佳batch size的前提下，通过测量单位时间步数即可换算实际吞吐量。

**3) 与文档关系**：直接对应"性能指标—吞吐率"章节给出的"实际吞吐量计算"公式，是该章节量化计算的核心示意图。
- `computing_power_utilization_metric_fig_03.png`: # 图文联合解读

**1) 图中内容：** 该图为吞吐率（Throughput）的计算公式，显示为 `P = (BS×N)/T × S/(BS×N)`，其中包含 BS（Batch Size）、N（节点/设备数）、T（单步时间）、S（总样本数）等关键参数标注。

**2) 技术结论：** 公式将吞吐率 P 分解为「单位时间处理批次量 (BS×N)/T」与「样本分布系数 S/(BS×N)」的乘积，揭示了吞吐率随 batch size、节点规模线性增长、随总样本数收敛的量化关系。

**3) 与文档论点关系：** 该图直接支撑"性能指标优先级中吞吐率最高"的论点，配合前文论述——通过二分搜索找到最佳 batch size 后，可用此公式精确测量 AI 集群每秒处理的训练样本数，是文档"如何在确定 BS 后计算实际吞吐量"这一论述的核心可视化依据。
- `computing_power_utilization_metric_fig_04.png`: **图文联合解读：**

1) **图示内容**：图中呈现的是一个性能公式的模糊渲染图像。顶部有"1"或"T"等符号，中部为等号/分式条，下方为分子分母结构，整体呈现典型的训练吞吐率计算公式样式：Throughput = Batch Size × 设备数 / 单步迭代时间。

2) **技术结论**：公式论证了吞吐率与batch size、并行设备数成正比，与单步迭代时间成反比，是衡量AI集群单位时间处理样本量的核心量化表达。

3) **与文档关系**：该图承接上文"确定最佳batch size后计算实际吞吐率"的论述，将吞吐率从概念转化为可计算的工程公式，与文档强调"吞吐率优先于单步迭代时间"的性能指标排序相呼应，为后续优化提供数学依据。
- `communication_performance_metrics_fig_01.png`: **图示解读：**

**1) 图中内容：** 展示Wait ratio（等待率）的公式——分子为Wait time（等待时间），分母为Wait time + Transit time（等待时间+传输时间），呈分数式排版。

**2) 技术结论：** 该比值衡量计算单元在数据传输过程中处于空闲等待的比例。值越高，说明硬件空闲等待数据的时间占比越大，实际数据传输效率越低，是带宽瓶颈的直观体现。

**3) 与文档关系：** 呼应文档"性能指标"中"带宽占比"和"通信时间"章节——Wait time对应通信中未被计算掩盖的部分，是评估吞吐率瓶颈、辅助调优的关键量化指标。
- `communication_performance_metrics_fig_02.png`: ## 图文联合解读

**1) 图中内容**：展示吞吐率计算公式——**SDMA（每秒样本数）= sample data（样本数）/ sample transit time（传输时间）**，以分数形式呈现，分子为"sample data"，分母为"sample transit time"。

**2) 技术结论**：吞吐率等于单位时间（1秒）内网络处理的训练样本总量，反映模型在最优batch size下的并行处理能力上限。

**3) 与文档论点的关系**：呼应"性能指标"中吞吐率作为**最高优先级指标**的定义——在确定最佳batch size后，通过此公式量化实际吞吐量，支撑"数据并行越充分，吞吐越优"的核心性能优化方向。
- `communication_performance_metrics_fig_03.png`: # 图文联合解读

**1) 图中内容：** 图像展示了一个吞吐量计算公式的可视化：左侧标注"RDMA Bandwidth"（RDMA带宽），右上角为"Training data"（训练数据量），右下角为"Training Transit Time"（训练传输时间），中间用除号连接，整体构图呈现"训练数据 ÷ 训练传输时间"的公式结构。

**2) 技术结论：** 图示论证了吞吐率（Throughput）的本质定义——即单位时间内可处理的训练样本数量，等价于训练数据总量除以数据传输时间，同时强调RDMA作为高速网络通信机制在集群训练中对吞吐率提升的关键作用。

**3) 与文档论点关系：** 该图直接服务于"性能指标介绍"中"吞吐率"章节，配合文档给出的吞吐量计算公式图片，将抽象的"最佳batch size下1秒内处理的样本数"概念具象化为数据传输效率的数学表达，支撑"吞吐率为最高优先级性能指标"的核心论点。
