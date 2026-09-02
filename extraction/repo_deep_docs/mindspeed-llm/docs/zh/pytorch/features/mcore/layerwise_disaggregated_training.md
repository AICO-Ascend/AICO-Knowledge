# 边云协同分布式安全训练

> 仓 `mindspeed-llm` · 路径 `docs/zh/pytorch/features/mcore/layerwise_disaggregated_training.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-llm/docs/zh/pytorch/features/mcore/layerwise_disaggregated_training.md

# 一体化深度解读：边云协同分布式安全训练（Layerwise Disaggregated Training）

---

## 【定位】

这篇文档描述的是 mindspeed-llm 在"边云协同"算力租赁场景下，提供一种**让原始训练样本不出企业本地（边侧）、同时利用云端（运营商侧）算力**完成大模型微调的分布式安全训练能力——其核心是**PP 并行的 U-shape 切分 + 不对称 TP/DP + 跨域流水编排优化**。

---

## 【技术要点】

1. **U-shape PP 切分**：在 PP 并行下，将模型的"首层 + 尾层"同时部署在第一级流水线（即边侧），中间隐藏层部署在云侧。边侧仅需少量算力负责首尾层处理，原始样本无需上传。
2. **边侧四步处理**：每个 microbatch 在边侧需执行 FS（ForwardStart，首层前向）→ FE（ForwardEnd，尾层前向）→ BS（BackwardStart，尾层反向）→ BE（BackwardEnd，首层反向）四个动作。
3. **流水编排优化**：第一级流水线被拆为两级逻辑流水（首层流水线 + 尾层流水线），按 1F1B schedule 编排后再合并，合并冲突时按 **FS-FE-BS-BE** 顺序重排以拉长可容忍的边云通信时延。
4. **非对称 TP（Asymmetric TP）**：边侧 TP 可小于云侧 TP，跨 PP 通信采用"TP 组内编号最小卡 P2P → 接收后 broadcast 到全 TP 组"两步法，规避不对称 P2P 的多对多通信。
5. **非对称 DP（Asymmetric DP）**：边侧通过**时分复用**（time-division multiplexing）顺序处理多个 DP 域数据，分别与云侧通信；rank 组初始化采用"先对称 DP 分组 → 边侧重计算合并 → 云侧 rank 整体偏移边侧卡数"策略。
6. **模型与并行约束**：当前支持 Qwen2.5/Qwen3 系列的 32B/72B；不支持 MoE、LoRA、`--num-virtual-stages-per-pipeline-rank` 必须传 `2`，非对称 TP 与非对称 DP 同时开启时要求 TP 为偶数且满足"边侧 TP 可被云侧 TP 整除"。

---

## 【关键机制与数据】

### 数据流（原文：方案原理）

- **前向（边）**：边侧读取原始样本 → 模型首层处理 → 激活值发往云侧。
- **前向（云）**：云侧完成中间隐藏层 → 结果回送边侧。
- **前向（边）+ Loss**：边侧完成模型尾层并计算 loss。
- **反向**：流程对称（边侧→云侧→边侧）。
- **效果（原文）**：边侧向云侧只发送**激活值（前向）** 和**梯度（反向）**，原始样本不出园。

### 流水编排（原文：跨域协同训练性能优化）

- 在 U-shape 切分下，第一级流水线相比常规 PP 额外承担了 FE、BS 两个动作；通过拆分为两级逻辑流水（首层、尾层）再合并的方式做编排。
- 合并冲突时的重排依据（原文）："以样本 3 的前向传播通信为例，其通信时间可以由样本 5 的前向计算时间掩盖，提升了可容忍通信时延"。
- **效果（原文）**："当边云通信时延小于 tf（边侧单个 microbatch 的前向计算时间）时，稳态运行阶段无额外空泡（warmup/cooldown 阶段有少量额外空泡）"。

### 非对称 TP 通信（原文：非对称 TP）

- 对称 TP P2P 示例（PP=2, TP=8）：`0->8, 1->9, 2->10, ...`（卡与同组相邻卡通信）。
- 非对称 TP P2P 两步法：
  1. 当前 TP 组内编号最小的卡 → 下一 TP 组内编号最小的卡；
  2. 接收方通过 broadcast 把数据共享给其所在 TP 组的全部卡。
- **效果（原文）**："megatron 现有逻辑会提前在 TP 组内完成 AR 通信，因此仅通过单卡进行通信即可将完整的数据传递给下一级 PP"。

### 非对称 DP 通信（原文：非对称 DP）

- 边侧通过**时分复用**方式顺序处理多 DP 域数据，分别与云侧通信。
- rank 组生成：先按对称 DP 场景把边云分开生成 rank 组；再将边侧的 rank 组重计算合并；最后云侧 rank 组整体偏移边侧卡数。
- 梯度处理（原文）："megatron 现有逻辑在时分复用处理多个 DP 域的数据计算梯度时，默认会累加梯度，相当于边侧默认对梯度已经做了 AR 操作，只需要在最后对累加的总梯度求平均即可"。
- 数据处理与通信顺序（原文）："按照 PP 组内（不同的 PP 组处理不同DP域的数据）Ranks 的顺序进行"。

### 性能/容量数据

- 原文仅给出**机制层面**的定性表述（"稳态无额外空泡"等），未给出实测 TFLOPS、吞吐、加速比等具体性能数字，故不在此处臆造。

---

## 【表格解读】

### 表 1：边侧流水编排规则（原文逐字还原）

| 阶段 | 操作 | 次数 | 案例计算结果 |
|---|---|---|---|
| warmup | FS | PP+1 | 4 |
| steady state 1 | FEBS | floor((PP-1)*2/3 - 1/2 + 2) | 2 |
| steady state 2 | FS-FE-BS-BE | mbn - floor((PP-1)*2/3 - 1/2 + 2) | 2 |
| cooldown | BE | floor((PP-1)*2/3 - 1/2 + 2) | 2 |

**逐行解读：**

- **warmup | FS | PP+1 = 4**：在 warmup 阶段边侧只跑"首层前向"动作 FS，次数等于 `PP+1`，案例 `PP=3` 故为 4 次。其作用是把流水线"喂满"，让云侧各级流水线都有可消费/可生产的 microbatch。
- **steady state 1 | FEBS | floor((PP-1)*2/3 - 1/2 + 2) = 2**：进入稳态第一段，边侧按 **F→E→B→S** 顺序执行单个 microbatch 的尾层前向 + 首层反向，循环 2 次。这是把"尾层流水线"和"首层流水线"按 1F1B 风格分别运行后再合并的关键段。
- **steady state 2 | FS-FE-BS-BE | mbn - floor(...) = 2**：稳态第二段是把首尾两层流水线合并后执行的"四步合一"循环，每个循环覆盖一个 microbatch 的全部四步（FS、FE、BS、BE）。次数 = `mbn - 上一段次数 = 4 - 2 = 2`，正好把剩余 microbatch 处理完。
- **cooldown | BE | floor(...) = 2**：排空阶段边侧只跑"首层反向"BE，次数与 steady state 1 对称（2 次），负责把残留的 microbatch 反向传播收尾。

> 案例条件：原文给出的案例是 `PP=3, mbn=4`，整张表对应到该案例的具体取值已写入"案例计算结果"列。

### 表 2：重要参数（原文逐字还原）

| 重要参数 | 参数说明 |
|---|---|
| --layerwise-disaggregated-training | 开启边云协同分布式安全训练 |
| --num-layer-list [str] | 配置非均匀 PP 切分，传参为各级流水的隐藏层数 `L0,...,LPP`，其中 L0 和 LPP 表示首尾隐藏层数，分别传参。 |
| --num-virtual-stages-per-pipeline-rank [int] | 配置虚拟 Pipeline Stage 数，必须配置为 `2`。 |

**逐行解读：**

- `--layerwise-disaggregated-training`：特性开关，传值即启用边云协同训练（文档未指定取值形式，结合惯例应为 flag / store_true 类型）。
- `--num-layer-list`：由于 U-shape 切分需要让第一级流水线同时承载"首层"和"尾层"，模型层数是非均匀划分的——`L0` 与 `LPP` 分别为首、尾隐藏层数（注意"分别传参"指首尾需要独立给出）。
- `--num-virtual-stages-per-pipeline-rank`：固定为 `2`，含义是把第一级流水线"逻辑上"拆成两个 virtual stage（首层、尾层），与上文"拆分为两级逻辑流水"的设计严格对应。

### 表 3：模型范围（原文逐字还原）

| 模型类型 | 具体模型 |
|---|---|
| LLM | Qwen3-32B, Qwen2.5-32B, Qwen2.5-72B |

**逐行解读：**

- 仅支持 Dense LLM 中的 Qwen2.5/Qwen3 三个规模（32B、32B、72B）。
- 文档同段明确写出**暂不支持 MoE 模型**，故其他模型架构（GPT、LLaMA、其他家族、MoE）不在当前支持矩阵内。

---

## 【公式解读】

**原文无独立公式章节**，但流水编排表中的"次数"列里出现一个带 `floor` 的表达式，应作为公式逐字保留并解读：

$$\text{steps}_{\text{steady1/cooldown}} = \left\lfloor \frac{(PP-1)\times 2}{3} - \frac{1}{2} + 2 \right\rfloor$$

**符号含义：**

| 符号 | 含义 |
|---|---|
| $PP$ | Pipeline Parallelism 流水线并行度（即模型被切分的 stage 数 / 流水线级数） |
| $(PP-1)\times 2$ | 来自"两级逻辑流水"思路下，对 1F1B warmup/cooldown 长度的二次放大（前缀项） |
| $2$ | 平移常数，对齐到 PP=3 时的设计预期 |
| $\frac{1}{2}$ | 微调项（half-step 偏移），保证 floor 后与稳态分段边界对齐 |
| $\lfloor\cdot\rfloor$ | 向下取整，确保操作次数为整数 |

**作用：**

- 用于计算 **steady state 1** 与 **cooldown** 两个阶段边侧需要执行的循环次数（即连续执行 FEBS 或 BE 的次数）。
- **steady state 2** 的次数则由 `mbn - 上式` 得到——这是流水编排"前后两段拼出总 mbn"的恒等关系（`warmup + steady1 + steady2 + cooldown` 恰好覆盖 `mbn` 个 microbatch 的全部边侧动作）。
- 案例代入（PP=3, mbn=4）：`(3-1)*2/3 - 1/2 + 2 = 4/3 + 3/2 = 17/6 ≈ 2.833 → floor = 2`，与表中"2"严格一致。

---

## 【关联】

- **下游使用文档**：[`../../training/finetune/mcore/layerwise_disaggregated_training.md`](../../training/finetune/mcore/layerwise_disaggregated_training.md) —— 文末"使用方法"段明确指向该文件，本文档只描述能力与原理，具体启动步骤、配置脚本、提交流程需跳转阅读。
- **依赖的并行原语**：
  - **PP（Pipeline Parallel）**：U-shape 切分建立在 PP 并行之上，复用 Megatron 的流水线 stage 抽象。
  - **TP（Tensor Parallel）**：非对称 TP 复用 Megatron TP 组内的 AR（All-Reduce）通信，再叠加 P2P 跨 stage 通信。
  - **DP（Data Parallel）**：非对称 DP 复用 Megatron rank 组生成逻辑（`ldt_vdp_gen_ranks.png` 中明确"复用现有 megatron 生成 rank 组的逻辑"）。
  - **VPP（Virtual Pipeline Parallel）**：`--num-virtual-stages-per-pipeline-rank=2` 即虚拟流水 stage 数——文档同时指出"暂不支持常规 VPP 并行"，说明本特性的 VPP=2 是其特殊形态，并非通用 VPP。
- **所引用图示（位于 `docs/zh/figures/ldt_sft/`）**：
  - `layerwise_disaggregated_training_stage.png`：边/云侧 stage 切分示意图。
  - `pipeline_chart.png`：图1（两级逻辑流水）+ 图2（合并重排后最终方案）。
  - `ldt_tp.png` / `ldt_vtp.png`：对称 TP / 非对称 TP 的 P2P 通信对比。
  - `ldt_dp.png` / `ldt_vdp.png`：对称 DP / 非对称 DP 数据-卡映射对比。
  - `ldt_vdp_gen_ranks.png`：非对称 DP 下 rank 组生成与合并流程。
- **未在本特性中覆盖、但与上下游相关的项**：MoE、LoRA、常规 VPP（`num-virtual-stages-per-pipeline-rank != 2`）——均显式标注为不支持，与原 Megatron-Core 的对应能力形成互斥。

---

## 【使用方法】

- **启用特性**：通过启动参数 `--layerwise-disaggregated-training` 开启。
- **配置非均匀 PP 切分**：通过 `--num-layer-list [str]` 传入各级流水的隐藏层数 `L0,...,LPP`（首层与尾层分别独立给出）。
- **配置虚拟流水 Stage 数**：通过 `--num-virtual-stages-per-pipeline-rank [int]`，**必须传 `2`**。
- **详细启动脚本、参数组合示例、提交作业步骤**：原文指向 [`../../training/finetune/mcore/layerwise_disaggregated_training.md`](../../training/finetune/mcore/layerwise_disaggregated_training.md)，本文档未给出具体 shell/命令。

**原文已显式给出的硬约束（启用前需对齐）：**

| 约束项 | 取值 |
|---|---|
| 支持模型 | Qwen3-32B / Qwen2.5-32B / Qwen2.5-72B |
| MoE | 暂不支持 |
| LoRA | 暂不支持 |
| `--num-virtual-stages-per-pipeline-rank` | 必须为 `2` |
| 非对称 TP 场景 | 仅支持 DP=1 |
| 非对称 DP 场景 | 仅支持边侧 DP=1 |
| 非对称 TP + 非对称 DP 同时开启 | TP 须为偶数，且边侧 TP 可被云侧 TP 整除 |

## 图文联合解读

- `layerwise_disaggregated_training_stage.png`: 图示U-shape切分架构：边侧1卡部署模型首尾层（1-4、64-61），云侧4卡承载中间层（5-60），经企业专线互联。数据流：原始样本→边侧首层→激活值上云→云侧→边侧尾层→Loss；反向仅传梯度。论证"原始样本不出园、边侧仅需少量算力"的技术结论，呼应文档"边云协同安全训练"核心论点。
- `pipeline_chart.png`: **图1**：将边侧首层与尾层拆为两级逻辑流水，加上云侧PP=1/2，共4行按常规1F1B编排；红框标出合并处首尾层任务时序冲突。

**图2**：将两级逻辑流水合并为边侧PP=0、云侧PP=1/2的3行流水线，按FS-FE-BS-BE重排（红框内由原1、1重排为5、3、3），形成含warmup、steady_state、cooldown的稳态操作单元。

**论证结论**：拆分—合并—重排两步流水编排可消除U-shape切分下边侧首尾层任务冲突，实现跨域1F1B高效训练，支撑文档"计算通信掩盖提升跨域算效"的论点。
- `ldt_tp.png`: **图文联合解读：**

图示：左右两个灰色区域分别标注"TP=8"，各含8个绿色矩形节点（代表GPU卡），绿色虚线箭头一对一连接两侧矩形，表示边侧与云侧间的P2P（点对点）通信路径。

技术结论：展示了TP对等（各8卡）场景下，边云之间所有卡两两建立P2P通信链路的拓扑结构，验证了该通信模式可扩展至TP不对等场景（即"边云卡数不一致"的基础拓扑）。

与文档关系：直接对应文档"边云卡数不一致：支持TP不对等的P2P通信模式"论点，是该通信能力在TP对等情形下的可视化基础示意。
- `ldt_vtp.png`: **图文联合解读：**

1) **图示内容**：左侧为前向传播（Forward），右侧为反向传播（Backward）。每侧包含两组设备集群：边侧TP=4（4卡）与云侧TP=8（8卡），卡数不对称。前向时边侧4张卡汇聚输出后经dashed箭头传递至云侧，再通过"broadcast"散射到云侧8张卡；反向时云侧8张卡广播结果至边侧4张卡。

2) **技术结论**：证明在TP不对等（边4卡vs云8卡）场景下，可通过聚合-广播模式实现p2p通信，无需TP组大小匹配，突破传统TP必须等卡数的限制。

3) **与文档论点关系**：直接支撑"边云卡数不一致：支持TP不对等的p2p通信模式"这一特性论点，说明边侧少卡、云侧多卡的非对称部署在通信层是可行的，是U-shape切分落地的关键使能技术。
- `ldt_dp.png`: **图示内容**：两条平行数据流（DP1蓝、DP2橙），每条左侧为"边侧智能计算服务器"（1卡），右侧为"云侧智能计算服务器"（2卡），中间箭头携带激活值小方块跨域传输，最左侧的样本小方块仅存在于边侧。

**技术论证**：
1. **U-shape切分**：模型首尾层落在边侧单卡，云侧双卡仅处理中间层；
2. **TP不对等**：边云卡数1:2，通过p2p通信仍可协同；
3. **数据不出园**：原始样本（左侧小方块）始终留在边侧，跨域仅传激活/梯度。

**与文档关系**：直观佐证"原始样本不上云""边云卡数不一致的p2p通信""跨域协同训练"三大特性，体现"本地微算力+数据隐私"的双重保障。
- `ldt_vdp.png`: **1) 图示内容**：左侧为边侧智能计算服务器（单个黑框），接收多组蓝/橙小方块（原始样本/激活）；右侧为云侧智能计算服务器，包含两个虚线框组 DP1（蓝色）和 DP2（橙色），各含两个计算单元。蓝/橙箭头分别从边侧指向 DP1 和 DP2。注释说明"通过时分复用顺序处理多个 DP 域数据"。

**2) 技术结论**：单个边侧节点（少卡）通过时分复用机制，可轮流为云侧多个 DP 域提供模型首尾层计算服务，实现边云算力异构下的协同训练。

**3) 与文档关系**：对应文档中"边云卡数不一致"特性，证实边侧小算力可服务云侧多 DP 域，原始样本不出边侧，仅激活值/梯度跨域传输。
- `ldt_vdp_gen_ranks.png`: **图文联合解读：**

1) **图示内容**：左右对比边云两侧的TP×CP×DP×PP切分网格。左图边侧8卡（0-7）承载首尾层（0,1,4,5），云侧16卡承载中间层（8-15）；右图边侧仍为8卡（含虚线副本），云侧扩至20卡（4-19）。橙色弧标注"Module by the edge device count"（TP维度由边侧卡数决定），绿色弧标注"Accumulate the edge device count"（云侧PP随边侧累加扩展）。

2) **技术结论**：TP维度恒等于边侧卡数，云侧PP随边侧扩卡而递增，边云卡数可不对等且动态伸缩。

3) **与文档论点对应**：直接支撑"边云卡数不一致——支持TP不对等的p2p通信"以及"少量算力处理首尾层"的方案，证明边侧扩容时云侧可灵活扩展。
