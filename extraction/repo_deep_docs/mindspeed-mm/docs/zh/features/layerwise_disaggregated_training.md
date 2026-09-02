# 边云协同分布式安全训练

> 仓 `mindspeed-mm` · 路径 `docs/zh/features/layerwise_disaggregated_training.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-mm/docs/zh/features/layerwise_disaggregated_training.md

# 边云协同分布式安全训练 — 一体化深度解读

---

## 【定位】

这篇文档描述 mindspeed-mm 面向「数据不出园」合规场景的边云协同分布式安全训练能力：在 PP 并行的基础上引入 U-shape 切分，将模型首尾层同时下沉到企业本地（边侧），中间层部署在运营商云侧，原始样本全程不离开边侧，从而兼顾「本地微算力」与「算力租赁」两种诉求。

---

## 【技术要点】

1. **U-shape 模型切分（核心）**：在 PP 并行的基础上，将模型第一级流水线同时承载模型首层（FS/BE）与模型尾层（FE/BS），中间若干级流水线部署在云侧；前向时边侧先做 FS→传激活到云侧→云侧中间层→回传到边侧做 FE+loss，反向类似。原文：每个样本在边侧需完成 FS / FE / BS / BE 四步处理。
2. **跨域流水编排（4 阶段 schedule）**：边侧流水线分为 warmup（FS，PP+1 次）→ steady state 1（FEBS）→ steady state 2（FS-FE-BS-BE）→ cooldown（BE），通过将第一级逻辑流水线拆分为「首层」「尾层」两级再合并优化，并以 FS-FE-BS-BE 的执行顺序增大可容忍边云通信时延（原文案例：PP=3、mbn=4）。
3. **稳态无空泡条件**：当边云通信时延 < tf（边侧单个 microbatch 的前向计算时间）时，稳态阶段不引入额外空泡；原文：warmup/cooldown 阶段仍有少量额外空泡。
4. **非对称 TP（P2P + broadcast）**：当边侧 TP < 云侧 TP 时，P2P 通信改为「下一 TP 组内编号最小卡接收→组内 broadcast 共享给全 TP 组」；原文：依赖 megatron 现有逻辑在 P2P 通信前先在 TP 组内完成 AR 通信，仅通过单卡即可传递完整数据。
5. **非对称 DP（时分复用）**：当边侧 DP < 云侧 DP 时，边侧通过时分复用处理多个 DP 域数据并分别与云侧通信；rank 组生成采用「先按对称 DP 分别生成边/云 rank 组，再合并边侧 rank 组、云侧整体偏移边侧卡数」的策略；原文：megatron 现有逻辑在时分复用下会累加梯度，相当于边侧已做了 AR，最后只需对总梯度求平均。
6. **权重转换与启动约束**：以 Qwen2.5VL-32B 为例，PP=5、边 TP=2/云 TP=4、DP=1/2；启动微调时 `--virtual-pipeline-model-parallel-size` 原文要求必须为 3（使能首尾层共部署）；patch 开关 `"layerwise_disaggregated_training": true`。

---

## 【关键机制与数据】

**U-shape 前向/反向数据流**（原文）：
- 前向（边）：边侧读原始样本 → 模型首层 → 激活值传至云侧。
- 前向（云）：云侧处理中间隐藏层 → 结果回传边侧。
- 前向（边）：边侧完成模型尾层 + loss 计算。
- 反向传播流程类似。
- 边侧向云侧仅传递「激活值（前向）+ 梯度（反向）」，原始样本无需上云。

**流水编排案例数据**（原文 PP=3，mbn=4）：
- 上图：步骤 1 生成的两级逻辑流水；下图：步骤 2 合并并优化任务执行顺序后的最终方案。
- 优化依据：FS-FE-BS-BE 顺序让样本 3 的前向传播通信时间可由样本 5 的前向计算时间掩盖，提升可容忍通信时延，从而在拉远收敛场景下减小算效损失。

**空泡相关数据**（原文）：稳态运行阶段不引入额外空泡的前提是「边云通信时延 < tf（边侧单个 microbatch 的前向计算时间）」；warmup/cooldown 阶段有少量额外空泡。

**非对称 TP 数据流**（原文 PP=2、TP=8 对称 vs TP=4/TP=8 非对称）：
- 对称 TP P2P（前向）：0→8, 1→9, 2→10, …
- 非对称 TP：步骤 1——当前 TP 组编号最小卡把数据传给下一 TP 组编号最小卡；步骤 2——下一 TP 组编号最小卡收到后 broadcast 给组内全部卡。

**非对称 DP 案例**（原文 PP=3、TP=8，DP=2 对称 vs DP=1/DP=2 非对称）：
- rank 组生成：先按对称 DP 在边侧、云侧分别生成 rank 组；再合并边侧 rank 组；云侧 rank 组整体偏移边侧卡数。
- 梯度处理：megatron 现有逻辑在时分复用多 DP 域时默认累加梯度，相当于边侧已做 AR，仅需对总梯度求平均。
- 数据处理和通信顺序：统一按 PP 组内（不同 PP 组处理不同 DP 域数据）的 Ranks 顺序。

**当前支持范围**（原文）：Qwen2.5VL 32B 模型；暂不支持 MoE、LoRA、PP=1、常规 VPP（VPP 必须=3）；非对称 TP 仅 DP=1；非对称 DP 仅边侧 DP=1；非对称 TP+DP 同时开启时，TP 必须为偶数且边侧 TP 可被云侧 TP 整除。

---

## 【表格解读】

### 表 1：边侧流水编排规则表（原文逐字还原）

| 阶段 | 操作 | 次数 | 案例计算结果 |
| --- | --- | --- | --- |
| warmup | FS | PP+1 | 4 |
| steady state 1 | FEBS | floor((PP-1)*2/3 - 1/2 + 2) | 2 |
| steady state 2 | FS-FE-BS-BE | mbn - floor((PP-1)*2/3 - 1/2 + 2) | 2 |
| cooldown | BE | floor((PP-1)*2/3 - 1/2 + 2) | 2 |

逐行解读：
- **warmup（FS）**：执行次数为 PP+1。在常规 PP 的 1F1B schedule 中首级流水一般执行 PP 次 warmup（FS）；此处原文写为 PP+1，是因为 U-shape 切分后首级流水线同时承担首尾层，需要多 1 个 FS 来给尾层（FE）让出启动空间。案例 PP=3 时计算结果为 4。
- **steady state 1（FEBS）**：循环执行 FE→BS，原文公式 `floor((PP-1)*2/3 - 1/2 + 2)` 控制执行次数。该值在 PP=3 时为 `floor(2*2/3 - 1/2 + 2) = floor(4/3 + 3/2) = floor(17/6) = 2`，与原文「案例计算结果 2」一致。
- **steady state 2（FS-FE-BS-BE）**：按 FS-FE-BS-BE 顺序重排后的稳态 2，执行次数为 `mbn - steady state 1 次数`。原文强调该顺序的作用是「样本 3 的前向通信可被样本 5 的前向计算掩盖」，从而在拉远收敛场景下提高可容忍边云通信时延。PP=3、mbn=4 时计算结果为 4-2=2，与原文一致。
- **cooldown（BE）**：与 steady state 1 同次数 `floor((PP-1)*2/3 - 1/2 + 2)`，用于收尾尾层的反向计算，案例结果 2。

### 表 2：权重转换参数解析表（原文逐字还原）

| 参数 | 说明 | 必填 |
| --- | --- | --- |
| `--cfg.mm_dir` | Megatron 权重保存路径 | 是 |
| `--cfg.hf_config.hf_dir` | 原始 HF 模型权重路径 | 是 |
| `--cfg.parallel_config.llm_pp_layers` | LLM 模块 PP 切分每张卡上切分几层（required, type: list[Annotated[int, Ge(ge=0)]]） | 是 |
| `--cfg.parallel_config.vit_pp_layers` | VIT 模块 PP 切分每张卡上切分几层（required, type: list[Annotated[int, Ge(ge=0)]]） | 是 |
| `--cfg.parallel_config.tp_size` | TP 切分大小 | 是 |

逐行解读：
- `--cfg.mm_dir`：分别保存边侧（`-edge`）和云侧（`-cloud`）的 Megatron-Mcore 权重路径。
- `--cfg.hf_config.hf_dir`：原文指向 `./ckpt/hf_path/Qwen2.5-VL-32B-Instruct`。
- `--cfg.parallel_config.llm_pp_layers`：原文示例为 `[[0,0,0,0,0],[0,16,16,16,16],[0,0,0,0,0]]`，文档明确「两个子列表中的首个元素表示流水线头尾上部署的 llm 隐藏层数，实际部署时会部署在同一张卡」，即 VPP0（首个外层列表）与 VPP2（末个外层列表）的首元素共同构成 U-shape 的首尾层共部署；中间 VPP1 的 5 个流水线分别承载 16 层 LLM 隐藏层。
- `--cfg.parallel_config.vit_pp_layers`：原文示例 `[[3,7,7,7,7],[1,0,0,0,0],[0,0,0,0,0]]`，含义是 VPP0 上 5 级流水线分别部署 3/7/7/7/7 层 VIT，VPP1 的首级流水部署 1 层 VIT（VIT 尾层与 LLM embedding 共卡），VPP2 全 0。
- `--cfg.parallel_config.tp_size`：原文边侧传 2、云侧传 4，分别对应各自的 TP 切分大小。

---

## 【公式解读】

**公式 1**：steady state 1 / cooldown 阶段执行次数公式（来自原文表格）：

$$
N_{\text{steady1}} \;=\; N_{\text{cooldown}} \;=\; \left\lfloor \frac{(PP-1)\times 2}{3} - \frac{1}{2} + 2 \right\rfloor
$$

- **PP**：流水线并行度（pipeline parallel size），即模型被切为多少级流水线，文档示例 PP=5（权重转换示例）和 PP=3（流水编排示例）。
- **含义**：该公式控制 U-shape 切分下边侧尾层（FEBS）在稳态阶段需要循环的次数，文档称这一次数来自「将第一级逻辑流水线拆分为两级、再合并优化」后的调度推导。
- **作用**：原文用 PP=3 验证，`floor((3-1)*2/3 - 1/2 + 2) = floor(4/3 + 3/2) = floor(17/6) = 2`，与表格「案例计算结果 2」一致；当 PP 取其他值时，原文未给出更多示例。
- **额外说明**：原文公式写法 `floor((PP-1)*2/3 - 1/2 + 2)` 等价于 `floor((2PP + 5)/3)`（代数化简后，行为一致），但原文采用原始写法，本节按原文保留。

**公式 2**：steady state 2 阶段执行次数公式（来自原文表格）：

$$
N_{\text{steady2}} \;=\; \text{mbn} - N_{\text{steady1}}
$$

- **mbn**：microbatch number，一个训练 step 中划分的 micro-batch 总数，原文示例 mbn=4。
- **N_steady1**：见公式 1。
- **作用**：保证全部 mbn 个 micro-batch 在稳态阶段恰好完成 FS-FE-BS-BE 一次完整循环；原文 PP=3、mbn=4 时 N_steady2 = 4 - 2 = 2，与表格一致。

**公式 3**：warmup 阶段执行次数公式（来自原文表格）：

$$
N_{\text{warmup}} \;=\; PP + 1
$$

- **PP**：流水线并行度。
- **作用**：U-shape 下首级流水线需多承担 1 个 FS（给尾层让出启动窗口）；原文 PP=3 时为 4，与表格「案例计算结果 4」一致。

---

## 【关联】

- **依赖基础设施/安装指南**：[`../pytorch/install_guide.md`](../pytorch/install_guide.md)：文档第 1 步要求用户参考该文档完成 MindSpeed MM 环境安装。
- **示例启动脚本**：[`../../../examples/qwen2.5vl/finetune_qwen2_5_vl_32b.sh`](../../../examples/qwen2.5vl/finetune_qwen2_5_vl_32b.sh)：文档第 5 步要求用户参考该脚本配置微调命令，并在其中追加 `--virtual-pipeline-model-parallel-size 3` 启用首尾层共部署；最终通过 `bash examples/qwen2.5vl/finetune_qwen2_5_vl_32b.sh` 启动训练。
- **上游模块关联**：文中涉及 Megatron-Mcore（权重转换目标格式 `hf_to_mm_ldt`、Qwen2_5_VLConverter）、Megatron 现有 P2P/AR 通信逻辑（原文：「megatron 现有逻辑会提前在 TP 组内完成 AR 通信」、「megatron 现有逻辑在时分复用处理多个 DP 域的数据计算梯度时，默认会累加梯度」）、多模态模型 Qwen2.5-VL（VIT 32 层 + LLM 64 层），均属于 mindspeed-mm 在 Megatron 体系上的扩展点。
- **下游约束关联**：文档「使用约束」一节明确该特性仅与 Qwen2.5VL 32B 模型路径打通，且依赖 `--virtual-pipeline-model-parallel-size 3` 这一 VPP 配置生效——与上文启动脚本、模型配置文件 `examples/qwen2.5vl/model_32b.json` 中的 patch 配置形成闭环。

---

## 【使用方法】

**1. 环境安装**：参考 [MindSpeed MM 安装指导](../pytorch/install_guide.md) 完成环境准备（原文步骤 1）。

**2. 下载 HF 模型权重**：从 Hugging Face 下载 `Qwen/Qwen2.5-VL-32B-Instruct` 至 `./ckpt/hf_path`；若无法访问 HuggingFace 推荐去 ModelScope 下载（原文步骤 2）。

**3. 权重转换（开启边云特性后边侧 TP = 边侧卡数）**：以边侧 2 卡、云侧 32 卡、PP=5、边 TP=2/DP=1、云 TP=4/DP=2 为例（原文步骤 3）：
- **边侧**：`tp_size=2`，mm_dir 末尾 `-edge`。
- **云侧**：`tp_size=4`，mm_dir 末尾 `-cloud`。
- 两者共用相同的 `llm_pp_layers [[0,0,0,0,0],[0,16,16,16,16],[0,0,0,0,0]]` 与 `vit_pp_layers [[3,7,7,7,7],[1,0,0,0,0],[0,0,0,0,0]]`。

**4. 数据准备**：下载 COCO2017 数据集至 `./data/COCO2017`，下载 LLaVA-Instruct-150K 描述文件至 `./data/`，运行 `python mindspeed_mm/fsdp/tools/data_tool/llava_instruct_2_mllm_demo_format.py` 转换（原文步骤 4）。

**5. 模型配置文件 `examples/qwen2.5vl/model_32b.json` 修改**（原文步骤 5）：
- 在 `patch` 中开启特性：`"layerwise_disaggregated_training": true`。
- 配置非均匀 PP：`vision_encoder.pipeline_num_layers = [[3,7,7,7,7],[1,0,0,0,0],[0,0,0,0,0]]`，`text_decoder.pipeline_num_layers = [[0,0,0,0,0],[0,16,16,16,16],[0,0,0,0,0]]`（VPP0 部署 VIT；VPP1 首级流水线部署 VIT 尾层 + LLM embedding + LLM unembedding；VPP1 其余流水线部署 LLM 中间隐藏层各 16 层）。

**6. 训练脚本参数**：参考 [Qwen2.5VL-32B 微调脚本](../../../examples/qwen2.5vl/finetune_qwen2_5_vl_32b.sh)，开启边云特性时需追加：`--virtual-pipeline-model-parallel-size 3`（原文强制为 3，以使能首尾层共部署）。

**7. 启动训练**（原文步骤 5 末尾）：`bash examples/qwen2.5vl/finetune_qwen2_5_vl_32b.sh`。

**约束提醒**（原文「使用约束」一节）：训练参数的并行配置（TP/PP）需与权重转换时保持一致；当前仅 Qwen2.5VL 32B 模型支持；不支持 PP=1、MoE、LoRA；VPP 强制为 3；非对称 TP 仅 DP=1；非对称 DP 仅边侧 DP=1；非对称 TP+DP 同时开启时 TP 必须为偶数且边侧 TP 能被云侧 TP 整除。

## 图文联合解读

- `layerwise_disaggregated_training.png`: ## 图文联合解读

**画面内容**：上半部分为物理部署——企业园区（边）部署1台智算服务器、智算中心（云）部署4台服务器，两者通过广域网/企业专线连接；下半部分为U-shape模型切分与数据流：边侧承载模型首尾层（层1-4与61-64）并完成loss计算，云侧承载中间层（5-60）。数据流标注三步：①原始样本仅由边侧输入；②前向激活值 边→云；③反向梯度值 云→边。

**技术结论**：U-shape切分使原始样本局限于企业园区边界，跨广域网仅传输激活值与梯度，实现"数据不出园"；同时支持边云卡数不对等（1 vs 4），验证了TP不对等p2p通信方案的可行性。

**与文档论点关系**：该图直观支撑"原始样本不上云"和"边云算力解耦"两大核心论点。
- `pipeline_chart.png`: **图1**：边侧拆为"首层流水"与"尾层流水"两级逻辑流水，按常规1F1B规则编排（PP=3，mbn=4），蓝绿分别代表前向/反向，红框标出两级边侧流水在样本1-4处的任务冲突。

**图2**：合并两级流水并按FS-FE-BS-BE重排（红框处），形成warmup→steady_state 1→操作单元→steady_state 2→cooldown的最终调度；云侧保持常规PP顺序。

**技术结论**：FS-FE-BS-BE顺序使样本3前向通信时间可被样本5前向计算掩盖，从而**增大可容忍边云通信时延**，减小拉远场景的算效损失。

**与文档论点关系**：直接论证"跨域协同训练性能优化"——通过流水编排与计算通信掩盖实现边云高效训练，是"数据不出园"方案下兼顾算效的关键设计依据。
- `ldt_tp.png`: **图解读**：

1）图示内容：左侧灰色框（边侧，TP=8）包含若干绿色模型层块，首尾层集中部署；右侧灰色框（云侧，TP=8）承载中间隐藏层。两箱之间通过8条绿色虚线箭头相连，表示p2p跨域通信（前向传激活、反向传梯度）。

2）技术结论：可视化"U-shape"切分——边侧同时持有模型首尾层、云侧仅持有中间层，并通过TP等价的p2p连接实现跨域数据流。这是"原始样本不上云"的物理基础。

3）文档关系：呼应"边云协同分布式安全训练"中"边侧仅向云侧发送激活值/梯度"的隐私隔离机制，并为后续"TP不对等p2p"功能提供基础架构示意。
- `ldt_vtp.png`: 1) 图示Forward/Backward两阶段，左侧TP=4（边侧）与右侧TP=8（云侧）通过绿色虚线箭头实现跨域broadcast通信，完成TP不对等卡数的P2P数据交互。

2) 论证了边侧4卡与云侧8卡可通过broadcast模式完成激活值（前向）与梯度（反向）的跨域传输。

3) 对应文档"边云卡数不一致"功能点，说明TP不等条件下边云仍可正常通信，是U-shape切分下数据不出云、算力跨域协同的关键通信支撑。
- `ldt_dp.png`: 图示边云协同U-shape切分：每条DP流水线（DP1蓝、DP2橙）边侧仅1个模型块承担首尾层，云侧含2个模型块承担中间隐藏层，箭头标注边云间激活/梯度跨域传输。论证了"模型首尾下沉边侧、原始样本仅在边侧读取"的数据流闭合性，以及边云TP不对等（一卡vs两卡）的可行性，**直接支撑文档"原始样本不上云"与"边云卡数不一致"两大核心论点**。
- `ldt_vdp.png`: 图示**边云架构**：左侧边侧算力服务器（单卡，处理模型首尾层）按时分复用方式依次服务右侧云侧DP1、DP2两个数据并行域。蓝、橙token表示不同样本：边侧读取样本→转激活值送云侧中间层→结果回传边侧算loss。

**论证结论**：单一边侧算力可通过时分复用对接多组云侧DP，实现"边云卡数不对等"部署，使U-shape切分下边侧仅承担首尾层、原始样本不流出本地的方案具备可扩展性。

**与文档对应**：直观支撑"边云卡数不一致（TP不对等p2p通信）"及"数据不出园"两项特性论点。
- `ldt_vdp_gen_ranks.png`: **图文解读：**

1）图示内容：左侧为初始布局，右侧为重排后的布局；均以蓝色竖线分隔"边侧/云侧"，方块按TP×DP×PP三维网格编号（0-19），PC维度（紫色虚线圈）标注同号副本对。顶部两条弧形箭头标明跨域映射规则：黄色"求余 % 左边侧卡数"用于TP对齐，绿色"累加 边侧卡数"用于PP衔接，右侧用虚线框标出边侧复制的尾层张量。

2）技术结论：在边云TP卡数不对等场景下，通过"TP取模 + PP累加"的p2p通信映射，同一张量的两端可正确配对通信，实现U-shape切分下跨域张量并行通信。

3）与文档关系：直接对应特性第三点"支持TP不对等的p2p通信模式"，为边云卡数不一致场景提供通信配对方案。
