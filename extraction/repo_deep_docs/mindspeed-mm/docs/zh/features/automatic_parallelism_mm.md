# Automatic Parallelism For Multi-Modal

> 仓 `mindspeed-mm` · 路径 `docs/zh/features/automatic_parallelism_mm.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-mm/docs/zh/features/automatic_parallelism_mm.md

# 多模态自动并行(Automatic Parallelism For Multi-Modal) 深度解读

## 【定位】

这篇文档面向多模态大模型(以 Qwen2VL-72B 为代表)在昇腾集群上的分布式训练,提供一种**自动化的并行策略调优能力**——通过子图级黑盒 Profiling、白盒内存/时延建模、以及整数规划求解,在 PP/TP/DP/MBS 与 PP 非均匀层切分的高维组合空间中,自动搜索出端到端时间最短的并行配置,取代以往依赖专家经验、需要"数天甚至数周"的人工调优过程。

---

## 【技术要点】

1. **问题驱动与适用范围**:多模态大模型训练涉及 TP/PP/DP/CP/VPP 等多种并行方法,搜索空间随并行维度丰富而爆炸式增长;且"相似模型或同一模型的不同训练阶段,最优并行配置也不相同",因此人工调优不可持续。
2. **三步式解决方案**:
   - **采样性能**:按多模态模型原有训练调用逻辑进行**网络切分 + 子图归并**,在少量资源上做 **block 级别黑盒 Profiling 采样**,兼顾子图外推灵活性与采样低开销。
   - **端到端建模**:基于采样得到的**子图性能、内存数据**,用白盒建模得到**网络峰值内存**与**仿真的单步迭代时间**。
   - **并行策略调优**:构建全量并行策略搜索空间,针对每种策略将 **PP 非均匀层最优切分转化为整数规划问题**,联合考虑 **PP 流水调度、内存限制、重计算策略**,目标函数为端到端时间最短;遍历所有可行策略后给出最优方案。
3. **能力边界(原文:)**:"当前已支持多模态理解模型 **PP/TP/DP/MBS 维度**以及 **PP 非均匀层切分维度**的最优搜索"。
4. **依赖版本**:适配 **MindSpeed-Core branch: `core_r0.8.0`**。
5. **启动约束**:必须以 **`bash` 作为脚本启动器,并在所有节点上拉起脚本**,同时配置文档列出的环境变量(如 `ASCEND_SLOG_PRINT_TO_STDOUT=0`、`TASK_QUEUE_ENABLE=2`、`COMBINED_ENABLE=1`、`CPU_AFFINITY_CONF=2`、`HCCL_CONNECT_TIMEOUT=1200`、`NPU_ASD_ENABLE=0`、`ASCEND_LAUNCH_BLOCKING=0`、`HOST_CACHE_CAPACITY=20`、`ACLNN_CACHE_LIMIT=100000`、`MULTI_STREAM_MEMORY_REUSE=2`、`PYTORCH_NPU_ALLOC_CONF="expandable_segments:True"` 等)。
6. **结果输出**:调优结果写入执行目录下的 **`auto_parallel_search_optimal_config.json`**,包含 `parallel_config`、`layer_placement`(ViT 与 LLM 的 PP 层切分)、`layer_recompute`(ViT 与 LLM 的细粒度重计算层数)、`e2e_time`(仿真端到端时间)、`throughput`(仿真吞吐率)。

---

## 【关键机制与数据】

### 工作原理(原文)
- 多模态模型结构丰富、训练阶段多样,因此方案先**网络切分 + 子图归并**降低搜索粒度,再**block 级黑盒 Profiling**采样少量资源,获得子图性能与内存数据。
- 用白盒建模把采样数据升格为**全网峰值内存**与**单步迭代时间仿真**。
- 在并行策略搜索空间中,对每种 PP 策略,把"非均匀层切分"建模为**整数规划**,与流水调度、内存上限、重计算联合优化,以**端到端时间最短**为目标遍历得到最优配置。

### 数据流(原文)
1. 用户在脚本中声明**采样集群**(`--nnodes / --nproc-per-node / --master-addr / --master-port / --node-rank`)与**待训练集群**(`--simulated-nnodes / --simulated-nproc-per-node`)。
2. 在采样集群上对模型子图做 Profiling → 得到子图性能 + 内存。
3. 白盒建模 → 得到峰值内存与单步时间仿真值。
4. 整数规划 + 全策略遍历 → 输出 `auto_parallel_search_optimal_config.json`。

### 性能/调优数据(原文:Qwen2VL-72B 搜索结果)
- `parallel_config`:`PP=8, TP=2, DP=4, MBS=1`
- `layer_placement`:
  - `vit_layer_placement`: `[32, 0, 0, 0, 0, 0, 0, 0]`(即 ViT 32 层全部落在第 1 个 PP stage)
  - `llm_layer_placement`: `[5, 11, 11, 11, 11, 11, 11, 9]`(LLM 80 层非均匀切分到 8 个 PP stage)
- `layer_recompute`:
  - `vit_layer_recompute`: `[0, 0, 0, 0, 0, 0, 0]`(ViT 端未做重计算)
  - `llm_layer_recompute`: `[0, 10, 9, 9, 9, 7, 4]`(LLM 端做细粒度重计算,首 stage 为 0)
- `e2e_time`: **`8992.0`**
- `throughput`: **`761.58192090395477`**

> 注:原文未给出其它基准模型或绝对加速比数字,故不做超出来源的对比。

---

## 【表格解读】

### 表 1 — 多维自动并行特性参数表(原文逐字还原)

| 参数名                      | 参数含义                                            |
| --------------------------- | -------------------------------------------------- |
| --auto-parallel-mm          | 多维自动并行特性总开关                               |
| --nnodes                    | 采样集群中节点的个数                                 |
| --nproc-per-node            | 采样集群中每个节点计算设备的个数                     |
| --master-addr               | 采样集群中主节点的IP地址                             |
| --master-port               | 采样集群用于通信的端口号，各节点需要配置相同的端口    |
| --node-rank                 | 采样集群中节点的rank，主节点为0，其他节点为1,2,······ |
| --simulated-nnodes          | 待训练集群的节点个数                                 |
| --simulated-nproc-per-node  | 待训练集群每个节点的设备数                           |

**逐行解读:**
- `--auto-parallel-mm` 是特性**总开关**,缺省即关闭多维自动并行。
- `--nnodes / --nproc-per-node / --master-addr / --master-port / --node-rank` 五项共同描述**采样集群**形态:用于实际拉起 Profiling 采样的子集群拓扑;`master-port` 在所有节点上必须一致,`node-rank` 主节点为 0、其余递增。
- `--simulated-nnodes / --simulated-nproc-per-node` 描述**目标(待训练)集群**形态:搜索得到的并行配置将按此规模落地,可在采样集群较小的情况下模拟大规模集群的最优切分。

### 表 2 — 搜索结果文件字段说明表(原文逐字还原)

| 参数名                      | 参数含义                                            |
| --------------------------- | -------------------------------------------------- |
| parallel_config             | 并行配置，包含PP/TP/DP/MBS维度                      |
| layer_placement             | 层切分配置，其中包含ViT及LLM的PP层切分策略           |
| layer_recompute             | 细粒度重计算层数，包含ViT及LLM的重计算层数           |
| e2e_time                    | 仿真的端到端时间                                    |
| throughput                  | 仿真的模型吞吐率                                    |

**逐行解读:**
- `parallel_config`:汇总 PP/TP/DP/MBS 四个维度的标量配置,是搜索算法在策略空间中的离散坐标。
- `layer_placement`:在已定 PP 维度下,给出 **ViT 与 LLM 各自**的逐 stage 层数分配,反映"非均匀层切分"的结果。
- `layer_recompute`:在已定 PP 维度下,给出 **ViT 与 LLM 各自**每 stage 的细粒度重计算层数,反映内存-时延权衡结果。
- `e2e_time` 与 `throughput`:均为**仿真**值,而非实测值,用于在不同并行策略间比较。

---

## 【公式解读】

**原文无显式数学公式。** 与方案语义相关的两个推导式可在示例脚本中读出:

- 派生 DP(分布式并行度):
  - `DP = WORLD_SIZE / TP / PP / CP`
  - 符号:`WORLD_SIZE = NPUS_PER_NODE × NNODES`(节点数 × 每节点 NPU 数),`TP` 张量并行度,`PP` 流水并行度,`CP` 上下文并行度。作用:在已知总 NPU 数与三种并行度后,反推数据并行维数。
- 派生 GBS(全局批大小):
  - `GBS = MBS × GRAD_ACC_STEP × DP`
  - 符号:`MBS` 微批大小,`GRAD_ACC_STEP` 梯度累积步数,`DP` 数据并行度。作用:确保所有并行度下的全局批大小一致,便于对比调优目标。

> 注:整数规划"PP 非均匀层切分"的目标函数与约束在原文中**未以公式形式给出**,仅以文字"端到端时间最短 + 内存约束 + 流水调度 + 重计算策略"概括。

---

## 【关联】

- **与多模态理解模型的耦合**:当前搜索能力声明"已支持**多模态理解模型** PP/TP/DP/MBS 维度以及 PP 非均匀层切分维度的最优搜索",即直接覆盖文档示例中的 **Qwen2VL-72B** 多模态理解模型。ViT 与 LLM 两段子图被**分别切分、分别归并**,因此搜索结果同时包含 `vit_*` 与 `llm_*` 字段,印证了多模态结构的拆分处理。
- **与多模态生成的关系**:原文"问题分析"段虽未显式列出"多模态生成"字样,但仓库定位为"支撑多模态生成、多模态理解",而本文当前明确能力为**多模态理解**模型,未声明对多模态生成(如扩散类)模型的并行搜索支持。
- **与 MindSpeed-Core 的依赖关系**:特性绑定的算子/通信后端来自 **MindSpeed-Core `core_r0.8.0`** 分支,这是 Profiling、内存建模与并行执行面的依赖基线。
- **与示例脚本的耦合**:脚本入口为 `pretrain_vlm.py`,数据/模型/工具配置分别指向 `./examples/qwen2vl/data_72b.json`、`./examples/qwen2vl/model_72b.json`、`./mindspeed_mm/tools/tools.json`,说明该特性属于 `mindspeed-mm` 仓内的多模态 VLM 训练入口链。
- **与 TP/PP/DP/CP/VPP 并行原语的关系**:搜索空间的维度即为这些基础并行原语的组合;`CP` 在示例中取 1,而 `PP` 在最优解中达到 8,显示该方案在大规模 PP 场景下尤其具备自动切分价值。
- **与其他自动特性**:原文未提供内部链接,未交叉引用其他 feature 文档,故"与其他特性的显式上下游关系"在原文中**未涉及**。

---

## 【使用方法】

### 启动方式(原文)
- 必须使用 **bash 作为脚本启动器**,在**所有节点上拉起脚本**,并配置多维自动并行相关参数。

### 环境变量(原文示例,逐字列出)
```
ASCEND_SLOG_PRINT_TO_STDOUT=0
ASCEND_GLOBAL_LOG_LEVEL=3
TASK_QUEUE_ENABLE=2
COMBINED_ENABLE=1
CPU_AFFINITY_CONF=2
HCCL_CONNECT_TIMEOUT=1200
NPU_ASD_ENABLE=0
ASCEND_LAUNCH_BLOCKING=0
HOST_CACHE_CAPACITY=20
ACLNN_CACHE_LIMIT=100000
MULTI_STREAM_MEMORY_REUSE=2
PYTORCH_NPU_ALLOC_CONF="expandable_segments:True"
```

### 关键配置(原文:Qwen2VL-72B)
- 节点与设备:`NPUS_PER_NODE=8`、`NNODES=1`、`MASTER_ADDR=localhost`、`MASTER_PORT=6010`、`NODE_RANK=0`,由 `WORLD_SIZE = NPUS_PER_NODE * NNODES` 推导。
- 并行与批量:`TP=4`、`PP=2`、`CP=1`、`MBS=1`、`GRAD_ACC_STEP=32`,据此派生 `DP = WORLD_SIZE/TP/PP/CP`、`GBS = MBS*GRAD_ACC_STEP*DP`。
- 多模态数据/模型/工具:`MM_DATA="./examples/qwen2vl/data_72b.json"`、`MM_MODEL="./examples/qwen2vl/model_72b.json"`、`MM_TOOL="./mindspeed_mm/tools/tools.json"`。
- 加载与保存:`LOAD_PATH="ckpt/Qwen2-VL-72B-Instruct"`、`SAVE_PATH="save_dir"`。
- 多维自动并行开关与采样/模拟集群参数(原文 SEARCH_ARGS):
```
--auto-parallel-mm \
--nnodes $NNODES \
--nproc-per-node $NPUS_PER_NODE \
--master-addr $MASTER_ADDR \
--master-port $MASTER_PORT \
--node-rank $NODE_RANK \
--simulated-nnodes 8 \
--simulated-nproc-per-node 16
```
含义:在 `1×8` 的**采样集群**上做 Profiling,但按 **`8 节点 × 16 卡 = 128 卡`** 的**待训练集群**规模搜索最优配置。

### 启动命令(原文)
```
python pretrain_vlm.py \
    $GPT_ARGS \
    $MM_ARGS \
    $OUTPUT_ARGS \
    $SEARCH_ARGS \
    --distributed-backend nccl \
    | tee logs/train_${logfile}.log 2>&1
```

### 调优结果查看
- 在执行目录下读取 **`auto_parallel_search_optimal_config.json`**,其字段含义见表 2。
- Qwen2VL-72B 示例最优配置(原文):
  - `parallel_config`: `{PP:8, TP:2, DP:4, MBS:1}`
  - `vit_layer_placement`: `[32, 0, 0, 0, 0, 0, 0, 0]`
  - `llm_layer_placement`: `[5, 11, 11, 11, 11, 11, 11, 9]`
  - `vit_layer_recompute`: `[0, 0, 0, 0, 0, 0, 0]`
  - `llm_layer_recompute`: `[0, 10, 9, 9, 9, 7, 4]`
  - `e2e_time`: `8992.0`
  - `throughput`: `761.58192090395477`

> 注:**日志权限处理**(`chmod 440 logs/...`、`find $SAVE_PATH -type d -exec chmod 750 {} \;`、`find $SAVE_PATH -type f -exec chmod 640 {} \;`)为原文脚本末尾给出的副作用命令,属使用流程的一部分,亦逐字保留。

## 图文联合解读

- `auto_parallel_mm_1.png`: **图文联合解读：**

图示展示了多模态自动并行的三阶段流水线：①**模型性能采样**——根据集群信息和并行能力构建搜索空间，通过Block Profiling分块采集计算/内存数据；②**端到端建模**——白盒建模获取峰值内存，并基于并行调度仿真单步迭代时间；③**并行策略优化**——联合PP层切分与重计算排除OOM，将策略搜索建模为规划问题高效求解。

图示论证了"**采样→建模→优化**"闭环技术路线，验证文档"低开销采样+白盒建模+整数规划求解"方案的系统化与可行性，支撑"自动化得出最优并行配置"的核心论点。
- `auto_parallel_mm_2.png`: ## 图文联合解读

**1) 图中内容**：表格对比三种多模态模型（InternVL2-8b、InternVL2-76b、Qwen2VL-72b）在"基线"（人工调优）与"最优并行策略"（自动并行输出）下的并行配置，并给出加速增益列。其中 PTDM 表示 TP×PP×CP×VPP 乘积，ViT/LLM/LLM_ReC 列表为各 PP 阶段非均匀层数切分。

**2) 技术结论**：自动并行在三类模型上均取得正向加速（3.2%–9.2%），增益随模型规模增大而提升；其优势体现在三处：① 非均匀 PP 层切分（如 Qwen2VL-72b 第四种配置 LLM 从 [1,5,5,…] 改为 [5,11,11,…]，缩短流水气泡）；② LLM_ReC 重计算层数按内存约束重分配；③ TP/CP 配置动态调整（如 InternVL2-76b 将 ViT 部分层从 12 拆为 11+1）。

**3) 与文档论点关系**：实证验证"整数规划求解非均匀 PP 切分"和"遍历全量并行策略搜索空间"方案的有效性，佐证了自动化调优可替代人工调优的核心主张。
