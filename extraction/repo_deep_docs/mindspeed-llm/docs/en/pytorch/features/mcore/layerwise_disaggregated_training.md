# Edge-Cloud Collaborative Distributed Secure Training

> 仓 `mindspeed-llm` · 路径 `docs/en/pytorch/features/mcore/layerwise_disaggregated_training.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-llm/docs/en/pytorch/features/mcore/layerwise_disaggregated_training.md

# 边云协同分布式安全训练 (Edge-Cloud Collaborative Distributed Secure Training) 深度解读

## 【定位】

本文档描述 mindspeed-llm 面向"运营商算力租赁 + 企业数据不出域"场景所提供的一种分布式微调能力——通过 U 形 PP 切分把模型首尾层部署在企业本地 (edge)、中间层部署在云端 (cloud),使原始样本无需上传云端即可完成 LLM 微调。

---

## 【技术要点】

1. **U 形 PP 切分 (U-shaped partitioning)**: 在传统 PP 基础上,首个 pipeline stage 同时承载模型的"第一层"和"最后一层",部署在 edge;中间若干层部署在 cloud。原始样本仅在 edge 上读取,云端只接收 activation / gradient。
2. **跨域流水调度优化**: edge 端需要顺序完成四个步骤 `FS → FE → BS → BE` (分别对应首层 forward、末层 forward、末层 backward、首层 backward),其调度按 warmup / steady state 1 / steady state 2 / cooldown 四阶段展开,通过将首阶段逻辑拆分为"两个逻辑阶段"再合并并重排任务,使 forward 通信可被后续样本的 forward 计算隐藏。
3. **稳态无额外 bubble 条件**: 当 edge-cloud 通信时延小于 edge 端单个 microbatch 的 forward 计算时间 `tf` 时,稳态不引入额外 bubble;warmup 与 cooldown 仅有少量额外 bubble。
4. **Asymmetric TP (非对称张量并行)**: edge TP size < cloud TP size,通过 P2P 通信模式实现——由当前 TP group 中最小 index 设备向下一 TP group 中最小 index 设备发送数据,接收端再广播至本 TP group 所有设备;正确性依赖 Megatron 原有 All-Reduce 已预先在 TP group 内完成。
5. **Asymmetric DP (非对称数据并行)**: edge DP size < cloud DP size,edge 通过时分复用 (time-division multiplexing) 处理多个 DP domain 的数据,并按 domain 分别与 cloud 通信;通信组初始化复用 Megatron rank-group 生成逻辑,先按对称 DP 生成 edge / cloud 各自的 rank group,再对 edge rank group 重计算并合并,cloud rank group 按 edge 设备数 offset。
6. **四阶段调度计数公式**: warmup 阶段 `FS` 数为 `PP + 1`;steady state 1 `FEBS` 数为 `floor((PP-1)*2/3 - 1/2 + 2)`;steady state 2 `FS-FE-BS-BE` 数为 `mbn - floor((PP-1)*2/3 - 1/2 + 2)`;cooldown `BE` 数为 `floor((PP-1)*2/3 - 1/2 + 2)`。

---

## 【关键机制与数据】

### 数据流 (单个样本)

> **原文**: 训练过程中,单个样本的处理流程如下:  
> – Forward pass on the edge: edge 读取原始样本,经模型首层处理为 activation,发往 cloud。  
> – Forward pass on the cloud: cloud 接收 activation 后处理中间隐藏层,结果回传 edge。  
> – Forward pass on the edge: edge 处理模型最后一层并计算 loss,前向结束。  
> – 反向传播流程类似。  
> **原文**: "在整个训练过程中,edge 在前向只发送 activation、在反向只发送 gradient 给 cloud,因此原始样本无需上传 cloud。"

### Edge 端四个子步骤

> **原文**: "U 形切分下,每个样本必须在 edge 上完成四步:首层前向 (`FS`)、末层前向 (`FE`)、末层反向 (`BS`)、首层反向 (`BE`)。"

### Pipeline 调度设计 (两步法)

> **原文**:  
> – Step 1: 将首个 pipeline stage 拆为两个逻辑 pipeline stage (一个承载第一层、一个承载最后一层),按常规 PP 的 `1F1B` 完成调度。  
> – Step 2: 合并两个逻辑 pipeline stage;若任务队列冲突则优化执行顺序。  
> 例: `PP = 3`, `mbn = 4`。  
> **原文**: "Step 2 合并时若出现任务冲突,按 `FS-FE-BS-BE` 顺序重排。该优化的依据是:该执行顺序可提升 edge-cloud 通信时延容忍度——例如 sample 3 的前向通信可被 sample 5 的前向计算时间所隐藏。"

### Asymmetric TP P2P 通信模式

> **原文**:  
> – Step 1: 当前 TP group 中最小 index 设备将数据发往下一 TP group 中最小 index 设备。  
> – Step 2: 下一 TP group 最小 index 设备接收数据后,广播共享给 TP group 内全部设备。  
> 例: 对称 TP `PP = 2`, `TP = 8` 时前向通信模式为 `0->8`, `1->9`, `2->10` 等。  
> **原文**: "由于 Megatron 既有逻辑在 P2P 通信前已预先完成 TP group 内的 All-Reduce,故仅通过单设备通信仍可把完整数据传递到下一 PP stage。"

### Asymmetric DP 通信组初始化与梯度处理

> **原文**: 通信组初始化复用 Megatron rank-group 生成逻辑——先按对称 DP 分别为 edge 与 cloud 生成 rank group,再对 edge rank group 重计算并合并,cloud rank group 按 edge 设备数做 offset。  
> **原文**: "Megatron 既有逻辑在 edge 通过时分复用处理多 DP domain 数据时,默认会累加梯度,即 edge 实质上执行了一次 All-Reduce……" (原文在 `o` 处截断)

---

## 【表格解读】

| Stage | Operation | Count | Result in the Example |
| --- | --- | --- | --- |
| warmup | FS | `PP + 1` | 4 |
| steady state 1 | FEBS | `floor((PP-1)*2/3 - 1/2 + 2)` | 2 |
| steady state 2 | FS-FE-BS-BE | `mbn - floor((PP-1)*2/3 - 1/2 + 2)` | 2 |
| cooldown | BE | `floor((PP-1)*2/3 - 1/2 + 2)` | 2 |

**逐行解读**:

- **warmup / FS / `PP + 1` / 4**: edge 端预热阶段只跑首层前向 (`FS`);计数等于 `PP + 1`,这是常规 PP 1F1B 调度中 warmup 阶段所需的最少 microbatch 数,确保所有后续 stage 都被填入 pipeline。示例 `PP=3` 时结果为 4,与表中一致。
- **steady state 1 / FEBS / `floor((PP-1)*2/3 - 1/2 + 2)` / 2**: 进入稳态后第一段,edge 端同一 microbatch 上连续执行 `FE → BS` (即末层前向 + 末层反向),把"云端中间层→edge"的回传通信与"edge→云端中间层"的反向通信配对;公式取整保证 `PP=3` 时结果为 2。
- **steady state 2 / FS-FE-BS-BE / `mbn - floor((PP-1)*2/3 - 1/2 + 2)` / 2**: 剩余 microbatch 在 edge 上严格按 `FS-FE-BS-BE` 顺序串行执行,目的是让 sample N 的前向通信被 sample N+2 的前向计算所掩盖;其数量 = 总 microbatch 数 `mbn` 减去 steady state 1 已消耗数。示例 `mbn=4` 时为 2。
- **cooldown / BE / `floor((PP-1)*2/3 - 1/2 + 2)` / 2**: 排空阶段,edge 仅执行首层反向 (`BE`),与 steady state 1 数量对称,共同确保所有 cloud 中间层的反向计算得以完成。`PP=3` 时为 2。

---

## 【公式解读】

### 公式 1 — steady state 1 / cooldown 计数

$$
\text{Count} = \left\lfloor \frac{(PP-1) \times 2}{3} - \frac{1}{2} + 2 \right\rfloor
$$

- **符号含义**:
  - `PP`: pipeline 并行度,即模型被切分的 stage 数。
  - `⌊ · ⌋`: 向下取整,保证 microbatch 数为整数。
  - 整体含义:在 U 形 PP 下,edge 端稳态 1 与 cooldown 阶段所需的 microbatch 数随 `PP` 增长近似线性增长 (系数 ≈ 2/3),并额外保留 2 个 microbatch 余量。
- **代入示例**: `PP=3` → `⌊ (2×2)/3 − 1/2 + 2 ⌋ = ⌊ 4/3 − 1/2 + 2 ⌋ = ⌊ 1.333 − 0.5 + 2 ⌋ = ⌊ 2.833 ⌋ = 2`,与表中 "Result in the Example" 一致。

### 公式 2 — steady state 2 计数

$$
\text{Count} = mbn - \left\lfloor \frac{(PP-1) \times 2}{3} - \frac{1}{2} + 2 \right\rfloor
$$

- **符号含义**:
  - `mbn`: microbatch number,一个训练 step 内 edge 端需要处理的总 microbatch 数。
  - 其余符号同公式 1。
- **作用**:从总 microbatch 中扣除稳态 1 已消耗部分,得到需要在 edge 上串行执行 `FS-FE-BS-BE` 的 microbatch 数;该段是引入通信隐藏的核心调度窗口。
- **代入示例**: `mbn=4`, `PP=3` → `4 − 2 = 2`,与表中一致。

### 公式 3 — 稳态无额外 bubble 条件 (隐含公式)

$$
t_{\text{comm}}^{\text{edge-cloud}} < t_f
$$

- **符号含义**:
  - $t_{\text{comm}}^{\text{edge-cloud}}$: edge↔cloud 单向通信时延 (原文未明确量纲,语境为单次 activation 传输耗时)。
  - $t_f$: edge 端单个 microbatch 的 forward 计算时间。
- **作用**:当通信时延严格小于 edge 前向计算时间时,forward 通信可被下一个 microbatch 的前向计算完全隐藏,稳态不引入额外 bubble;若超过此阈值,则稳态出现 bubble,训练效率下降。

---

## 【关联】

- **内部链接**: `../../training/finetune/mcore/layerwise_disaggregated_training.md` — 指向 `docs/zh/training/finetune/mcore/` 下的同名训练/微调使用文档,与本 feature 文档构成"能力描述 + 启用方法"的关系:本文档聚焦**原理、设计、调度公式与通信模式**,而该链接文档应提供**实际的微调启动命令、配置开关与脚本示例**,二者互为上下游 (feature ↔ usage)。
- **基础依赖**: 本特性构建于 Megatron 既有 `1F1B` 流水线调度、TP P2P 通信、TP group 内 All-Reduce、DP rank-group 生成逻辑之上,属于对其调度与通信模式的扩展而非替代。
- **能力组合**: U 形 PP 切分、Asymmetric TP、Asymmetric DP 三者正交组合,共同支撑"edge 算力受限 + edge/cloud GPU 数量不对等 + edge 节点数不对等"的实际部署约束。

---

## 【使用方法】

原文未涉及。  
本文档仅描述功能原理、调度设计与通信模式,具体的配置项、启动命令、参数开关 (如 edge/cloud rank 划分、PP/TP/DP 拓扑指定、microbatch 数设置等) 应参见文末内部链接 `../../training/finetune/mcore/layerwise_disaggregated_training.md` 所对应的训练/微调使用文档。

## 图文联合解读

- `layerwise_disaggregated_training_stage.png`: **图示内容：** 左侧企业园区（边缘）部署1台AI服务器，承载模型首末层（1-4、61-64），输入原始样本并计算损失；右侧AI算力中心（云端）部署4台服务器，承载中间层（5-8↔57-60）；两端通过广域网/企业专线连接，仅交互前向激活值与反向梯度。

**技术结论：** 基于PP的层间切分实现算力-数据解耦，原始数据不出域，敏感层在边缘，密集计算在云端。

**与文档关系：** 图示印证"少量首末层留企、多数中间层上云"的分层方案，兼顾算力租赁与数据合规。
- `pipeline_chart.png`: **图1/图2联合解读（≤150字）:**

**图1**: 边缘侧拆为首/末两个逻辑流水线阶段，叠加云端PP=1/2，按常规1F1B排程；红框标出首末层同一时段占用冲突（争用同一边缘设备）。

**图2**: 将首末层合并为单一PP=0阶段，并交换微批次顺序（红框内"5 3"置换为"3 5"），形成warmup–steady_state–cooldown三段式、循环的稳态operation unit，云端仍按1F1B推进。

**技术结论**: 通过合并边缘逻辑阶段+重排微批，可在保留边缘仅承载首末层这一隐私边界的前提下，消除任务冲突并获得稳定的周期性调度。

**与文档关系**: 论证"边云分层PP"——边缘只跑少量首末层（原始数据不出域），云端跑中间层（大算力），且调度可收敛，证明该方案兼具**数据驻留合规**与**流水线高效性**。
- `ldt_tp.png`: **图文联合解读：**

1) **图示内容**：左右两个灰色矩形框（均标注"TP=8"），内各含8个浅绿色方块，由8条绿色虚线箭头一对一横向连接，对应边端与云端内部的张量并行切分及中间结果传输。

2) **技术结论**：边端与云端各自独立采用TP=8张量并行，模型块在两侧按TP副本一一对应，通过点对点链路交换切分后的中间张量，无需传输原始样本。

3) **与论点呼应**：直观印证文档所述"少量模型块跑在边缘（处理首尾层）、大量模型块跑在云端（处理中间层）"的边云协同划分方案——边缘只需承担8个TP副本中处理原始数据的少数副本，云端承担其余大部分，安全且算力分配合理。
- `ldt_vtp.png`: **图文联合解读：**

1）图示内容：左右两幅分别展示 Forward 与 Backward 过程；每幅含两组模型块，分别标注 TP=4（少块，代表边缘端）与 TP=8（多块，代表云端）。绿色虚线箭头表示单向"broadcast"——前向时 TP=4 的输出广播至 TP=8 的全部 8 块，反向时 TP=8 的梯度广播回 TP=4。

2）技术结论：边缘与云端可采用不同 TP 度（4 vs 8），通过 broadcast 机制桥接异构并行配置，实现非对称张量并行下的前向/反向贯通，验证跨端训练的技术可行性。

3）与文档论点呼应：图中 TP=4 边缘块处理原始样本、TP=8 云端块承担主体计算，直观印证"边缘只需少量算力、首尾层本地化、数据不上云"的核心设计。
- `ldt_dp.png`: **图文联合解读：**

**1) 图示内容：** 横向两行（DP1蓝、DP2橙），每行左侧"边缘智算服务器"含1个方块（处理首尾层），右侧"云端智算服务器"含2个方块（处理中间层）；两端通过箭头传输中间结果，左端外侧小方框代表企业侧的原始样本。

**2) 技术结论：** 演示了"层间解耦"部署——边缘仅部署少量首尾模型块，云端部署大量中间块，原始数据不出边缘，传输的仅为中间特征/梯度。

**3) 与文档论点的呼应：** 图示直观佐证了文档核心主张——通过PP式切分使企业侧算力需求小、且原始样本不上云，从而兼顾"有限边缘算力"与"数据驻留合规"两大约束。
- `ldt_vdp.png`: **1) 图示内容**
左：边缘智能算力服务器接收原始样本（橙/蓝小方块），处理后向右侧发送中间激活（小方块）。右：云端智能算力服务器分为 DP1（蓝虚线框）和 DP2（橙虚线框）两个域，每域含两个模型块。箭头从边缘分别指向两域，标注"通过时分复用串行处理多 DP 域数据"。

**2) 技术结论**
采用层间解耦的 PP 切分：少量处理原始样本的首尾块留在本地，主体模型块下沉云端；边缘仅传出中间激活而非原始数据；单一边缘节点可时分复用串行服务多个 DP 域。

**3) 与文档论点的关系**
图示直观印证"边云协同 + 数据驻留"：边缘承担小算力首尾层保隐私，云端承接大规模中间层计算，并以时分复用提升边缘资源利用率，呼应"兼顾有限算力与合规"的论点。
- `ldt_vdp_gen_ranks.png`: **图文联合解读：**

图示对比边缘-云端两阶段扩展（箭头前后）。左：边缘侧TP×DP=2×2的8层（编号0–7），云端承担中间层（8–15）。右：边缘设备增加后，边缘模块按比例扩展（橙色箭头"Module by the edge device count"），云端同步累积（绿色箭头"Accumulate the edge device count"），新增层以虚线框标注。论证了"边缘按设备数线性扩容、云端对应累积"的可扩展性结论：仅需少量边缘算力处理模型首尾层处理原始数据，云端运行中间层处理中间结果，从而在满足数据驻留合规的同时实现算力弹性扩展，与"边侧首尾+云侧中段"的隐私与算力兼顾论点直接呼应。
