# Context Parallel

> 仓 `mindie-llm` · 路径 `docs/zh/user_guide/feature/context_parallel.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-llm/docs/zh/user_guide/feature/context_parallel.md

# Context Parallel（CP，上下文并行） 文档深度解读

## 【定位】

本文档描述 MindIE LLM 中 **Context Parallel（CP，上下文并行）特性**：在 Self-attention 模块的 sequence 维度上对长序列进行切分、跨设备并行计算，从而降低首 token 响应时间（TTFT）的并行策略。它面向大模型推理中因序列过长而带来的 attention 计算瓶颈。

## 【技术要点】

1. **并行维度**：在 Self-attention 的 sequence（上下文）维度进行切分，而非 head 或 batch 维度；目标是减少长序列首 token 时延，而非提升吞吐。
2. **通信拓扑**：采用 **ring-attention 风格的环形 KV 传递**——每张设备先计算本地 attention 分块，再通过环形拓扑在设备间传递 KV，完成跨设备分块结果汇总。
3. **内核算法**：在分块 attention 运算中使用 **Flash-Attention 2**，并在最后对分块结果进行**修正（correction）**，以保证跨设备拼接后的数值正确性。
4. **硬约束**：CP **不能单独开启**，必须与 **SP（Sequence Parallel）同时开启**；BF16 不支持；当前仅在 Atlas 800I A2 / Atlas 800I A3 推理服务器上可用。
5. **模型支持范围**：当前仅 DeepSeek-R1（W8A8 / W4A8）、DeepSeek-V3（W4A8）、DeepSeek-V3.1（W4A8）量化模型支持。
6. **并行度耦合约束**：DP 必须等于 1，SP 必须等于 TP，且 **CP × DP × TP = Worldsize**；PD 混部场景下还需满足 CP、SP、TP 三者同时启用。

## 【关键机制与数据】

- **原理概述（原文）**：
  - "各个设备计算各自的 attention，设备之间用 ring 的方式传递 KV 值来获得分块运算的结果，整体原理类似 ring-attention。"
  - "用 Flash-attention 2 算法进行分块运算，最后对分块结果进行修正。"
- **性能目标（原文）**："减少首 token 响应时间"——本文档未给出具体延迟/加速比等量化性能数据。
- **配置示例中的数值（原文）**：worldSize=16，dp=1，cp=2，sp=8，tp=8，moe_ep=16，moe_tp=1。可验证约束 CP×DP×TP = 2×1×8 = 16 = Worldsize，SP=TP=8，DP=1。
- **场景叠加（原文）**：CP 可与 MTP（PD 分离下泛指 MTP；PD 混部下仅 MTP=1）、异步调度、Prefix Cache 同时使用。

## 【表格解读】

**表 1  ModelDeployConfig 中的 ModelConfig 参数（原文逐字还原）**

| 配置项 | 取值类型 | 取值范围 | 配置说明 |
|---|---|---|---|
| cp | int | [1, 2] | 将一个输入序列切分后得到的份数。<br>1：不开启 CP 特性。<br>2：输入序列切分成 2 份。<br>目前开启 CP 特性，切分的份数仅支持"2"。 |

逐行解读：

- **配置项 cp**：引入的新字段，专门控制上下文并行是否开启以及切分粒度。文档中**只新增 `cp` 一项**，未列出 SP/TP/DP 等其他字段（这些属于通用并行参数，在链接的 `service_parameter_configuration.md` 中描述）。
- **取值类型 int**：离散整数，与取值范围闭合区间 `[1, 2]` 一致。
- **取值范围 [1, 2]**：当前 CP 仅暴露两档——关闭（1）与二切分（2）。
- **配置说明**：
  - "1：不开启 CP 特性"——`cp=1` 是默认/降级选项，相当于无 CP。
  - "2：输入序列切分成 2 份"——`cp=2` 启动环形 KV 传递 + Flash-Attention 2 分块计算。
  - "目前开启 CP 特性，切分的份数仅支持'2'"——明确表示未来扩展到 N 份的接口已留好（`int` 类型、范围上限 2），但当前版本功能层面只验证过 2 份切分。

## 【公式解读】

原文无公式。

> 说明：原文中虽描述了 ring-attention 的并行机制（涉及注意力分块、K/V 跨设备传递、结果修正），但并未给出任何 LaTeX 公式、伪代码或数学表达，仅有定性文字描述与一个 int 型配置项 `cp`，因此本节按要求标注"原文无公式"。

## 【关联】

- **../user_manual/service_parameter_configuration.md**：本文档在「执行推理」步骤 2 中明确将该链接定位为 **服务化参数的完整说明**，因此本文档所涉及的 `maxSeqLen`、`maxInputTokenLen`、`worldSize`、`dp`、`cp`、`sp`、`tp`、`moe_ep`、`moe_tp` 等参数项的完整语义、默认值与校验规则，以该章节为准；本文档只补充 CP 独有的 `cp` 字段及 CP 特定的约束（DP=1、SP=TP、CP×DP×TP=Worldsize）。
- **SP（Sequence Parallel）**：CP 的强制依赖。文档「限制与约束」明确"开启 CP 需要同时开启 SP"，二者协同覆盖 sequence 维度的不同切分职责。
- **TP（Tensor Parallel）/ DP（Data Parallel）**：CP 与之构成乘积关系约束（CP×DP×TP=Worldsize），属于同层并行维度的资源分配契约。
- **MTP（Multi-Token Prediction）/ 异步调度 / Prefix Cache**：作为可叠加特性，在 PD 分离与 PD 混部两种部署形态下同时被 CP 支持（PD 混部仅限 MTP=1）。
- **PD 分离 / PD 混部**：两种部署形态对 CP 的可用位置不同——PD 分离下 CP 仅在 P 节点启用，PD 混部下 CP 与 SP/TP 同时使用。
- **Atlas 800I A2 / Atlas 800I A3 推理服务器**：硬件底座依赖，CP 的环形通信与 Flash-Attention 2 分块需该硬件的互联能力支撑。
- **DeepSeek 系列 W8A8 / W4A8 量化模型**：当前唯一支持 CP 的模型族，反映 CP 实现与特定量化内核/算子的紧耦合。

## 【使用方法】

1. **打开配置文件**（whl 包）：
   ```bash
   cd {MindIE安装目录}/mindie_llm/
   vi conf/config.json
   ```
   或 run 包：
   ```bash
   cd {MindIE安装目录}/latest/mindie-service
   vi conf/config.json
   ```

2. **在 `ModelDeployConfig.ModelConfig` 中添加 `cp` 字段**（示例节选，原文加粗项即 `cp`）：
   ```json
   "ModelDeployConfig" : {
       "maxSeqLen" : 2560,
       "maxInputTokenLen" : 2048,
       "truncation" : 0,
       "ModelConfig" : [
           {
               "modelInstanceType" : "Standard",
               "modelName" : "DeepSeek-R1_w8a8",
               "modelWeightPath" : "/data/weights/DeepSeek-R1_w8a8",
               "worldSize" : 16,
               "cpuMemSize" : 5,
               "npuMemSize" : -1,
               "backendType" : "atb",
               "trustRemoteCode" : false,
               "dp": 1,
               "cp": 2,
               "sp": 8,
               "tp": 8,
               "moe_ep": 16,
               "moe_tp": 1
           }
       ]
   }
   ```

3. **启动服务**（whl 包）：
   ```bash
   mindie_llm_server
   ```
   或 run 包：
   ```bash
   ./bin/mindieservice_daemon
   ```

4. **约束自检清单**（配置时需同时满足，源自「限制与约束」章节）：
   - `cp ∈ {1, 2}`；启用 CP 时 `cp` 必须为 2。
   - 启用 CP 时必须同时启用 SP（即 `sp > 1`）。
   - `dp = 1`，且 `sp = tp`。
   - `cp × dp × tp = worldSize`。
   - PD 分离场景：CP 仅在 P 节点开启；PD 混部场景：CP 需与 SP、TP 同时启用，且叠加特性时 MTP 仅允许取 1。
   - 硬件：Atlas 800I A2 或 Atlas 800I A3 推理服务器；模型：DeepSeek-R1 W8A8 / W4A8、DeepSeek-V3 W4A8、DeepSeek-V3.1 W4A8；不支持 BF16。

> 注：原文未提供关闭 CP 的回滚步骤、动态开关命令、健康检查/日志关键字或性能基准数据；这些内容在本文档范围内未涉及。
