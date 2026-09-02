# Data Parallel

> 仓 `mindie-llm` · 路径 `docs/zh/user_guide/feature/data_parallel.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-llm/docs/zh/user_guide/feature/data_parallel.md

# Data Parallel 特性文档深度解读

## 【定位】

这篇文档描述了 MindIE-LLM 推理引擎中**数据并行（Data Parallel, DP）**特性：通过将推理请求划分为多个批次并分配到不同设备并行处理、最终合并结果，在显存充足时提升系统吞吐；文档同时给出该特性与张量并行（TP）、上下文并行（CP）、序列并行（SP）叠加使用时的参数约束关系及具体配置/启动方法。

## 【技术要点】

1. **并行机制**：将推理请求划分为多个批次（batch），每个批次分配给不同设备并行处理，处理完成后合并结果，属于**请求级 batch 维度的并行**。
2. **硬件适配**：仅在 **Atlas 800I A2 推理服务器** 与 **Atlas 800I A3 超节点服务器** 上支持。
3. **模块覆盖**：所有模型的 **Attention 模块** 与 **MLP 模块** 均支持数据并行；且**数据并行可与张量并行（TP）在同一模块上叠加使用**。
4. **约束关系**（核心数字规则，必须严格满足）：
   - `tp * dp = worldSize`（tp 与 dp 配合使用）；
   - `dp * tp * cp = worldSize`，且 **dp 必须为 1**（dp 与 cp、sp 联合使用时）；
   - **sp 必须等于 tp**（sp 与 tp 配合使用时）；
   - dp 默认值 **-1**（表示不执行数据并行），tp 默认值等于 worldSize，cp/sp 默认值 **1**。
5. **默认行为**：不配置补充参数时，推理过程中默认使用 `tp` 与 `moe_tp` 并行方式。
6. **显存优化前置条件**：示例配置中 8 卡部署开启 dp=8 时，`cpuMemSize: 5`、`npuMemSize: 1`，并通过环境变量 `PYTORCH_NPU_ALLOC_CONF=expandable_segments:True` 与 `ATB_WORKSPACE_MEM_ALLOC_ALG_TYPE=3` 优化显存分配。

## 【关键机制与数据】

- **工作原理（原文）**：Data Parallel 将推理请求划分为多个批次，并将每个批次分配给不同的设备进行并行处理，每个设备都并行处理不同批次的数据，然后将结果合并。
- **启用前提（原文）**：在显存足够时，均可开启数据并行特性，以提高吞吐。
- **叠加使用（原文）**：数据并行支持同张量并行在同一模块上叠加使用。
- **典型部署（原文示例）**：使用 8 卡推理时，`worldSize: 8`，Attention 模块使用数据并行（`dp: 8`），MoE 模型使用张量并行（隐含于 `tp: 1`，结合"默认使用 moe_tp"的备注，即 MoE 部分走 moe_tp）。
- **约束示例（原文）**：
  - worldSize=8，dp 配置为 2，则 tp 的值只能配置为 4；
  - worldSize=16，tp=8、sp=8，则 dp 只能为 1，cp 只能为 2；
  - worldSize=16，tp=8、dp=2，则 sp 只能为 8。
- **环境变量（原文）**：
  ```
  export PYTORCH_NPU_ALLOC_CONF=expandable_segments:True
  export ATB_WORKSPACE_MEM_ALLOC_ALG_TYPE=3
  ```

## 【表格解读】

> 原文表格逐字还原：

**表 1**  数据并行特性补充参数：**ModelDeployConfig中的ModelConfig参数**

| 配置项 | 取值类型 | 取值范围 | 配置说明 |
|---|---|---|---|
| tp | int32_t | <ul><li>未配置dp或dp值为-1时：取值为worldSize参数值。</li><li>与dp配合使用时：tp*dp的值必须等于worldSize参数值。</li></ul><br>例：若worldSize为8，dp配置为2，则tp的值只能配置为4。 | 整网张量并行数。<br>选填，默认值为设置的worldSize参数值。 |
| dp | int32_t | <ul><li>不执行该并行方式时：-1</li><li>与tp配合使用时：dp*tp的值必须等于worldSize参数值。</li></ul><br>例：若worldSize为8，tp配置为4，则dp的值只能配置为2。 | Attention模块中的数据并行数。<br>选填，默认值：-1，表示不执行数据并行。 |
| cp | int32_t | <ul><li>不执行该并行方式时：1</li><li>与sp配合使用时：dp\*tp\*cp的值必须等于worldSize参数值，且dp必须为1。</li></ul><br>例：若worldSize为16，tp配置为8，sp配置为8，dp的值只能配置为1，cp的值只能配置为2。 | 选填，默认值：1，表示不执行上下文并行。<br>Attention模块中的上下文并行数。 |
| sp | int32_t | <ul><li>不执行该并行方式时：1</li><li>与tp配合使用时：sp的值必须等于tp的参数值。</li></ul><br>例：若worldSize为16，tp配置为8，dp配置为2，sp的值只能配置为8。 | 选填，默认值：1，表示不执行序列并行。<br>Attention模块中的序列并行数。 |

**逐行解读**：

- **tp（整网张量并行数）**：取值类型 `int32_t`；当用户不配置 dp 或 dp=-1 时，tp 默认等于 `worldSize`（即全卡张量并行）；一旦启用 dp，则必须满足 `tp × dp = worldSize`；例如 worldSize=8、dp=2 时，tp 被锁死为 4。属于整网级别的张量切分维度。
- **dp（Attention 模块中的数据并行数）**：取值类型 `int32_t`；**默认值 -1 表示不启用数据并行**（这是判断是否开启 DP 特性的开关）；与 tp 联合时受 `dp × tp = worldSize` 约束，例如 worldSize=8、tp=4 时 dp 只能为 2。注意：dp 的作用域被限定为 **Attention 模块**。
- **cp（Attention 模块中的上下文并行数）**：取值类型 `int32_t`；默认 1 表示不执行上下文并行；与 sp 联合时强约束 `dp × tp × cp = worldSize`，且 **dp 必须为 1**，意味着上下文并行启用时不能再叠 DP；例如 worldSize=16、tp=8、sp=8 时 dp=1、cp=2。作用域同样限定在 **Attention 模块**。
- **sp（Attention 模块中的序列并行数）**：取值类型 `int32_t`；默认 1 表示不执行序列并行；与 tp 配合时 **sp 必须等于 tp**（sp 被钉死为 tp 的镜像）；例如 worldSize=16、tp=8、dp=2 时 sp 只能为 8。作用域限定在 **Attention 模块**。

整体观察：cp 与 sp 的作用域描述均显式写明"Attention 模块中的…并行数"，而 dp 的描述也限定为 Attention 模块；这与"使用场景"中"在显存足够时开启 DP 以提高吞吐"以及"DP 支持同张量并行在同一模块上叠加使用"形成闭环——DP 是叠加在 Attention 模块张量并行之外的**额外批次并行维度**。

## 【公式解读】

原文并未以独立公式块形式给出数学表达式，但其约束关系以**伪代码/规则说明**形式贯穿表格，可逐字提取如下并解释符号含义：

**公式 1（tp 与 dp 联合约束）**

$$
\text{tp} \times \text{dp} = \text{worldSize}
$$

- **tp**：整网张量并行数（int32_t）；
- **dp**：Attention 模块中的数据并行数（int32_t，默认 -1）；
- **worldSize**：参与推理的总卡数（由外部 ModelConfig 给出，示例中取 8 或 16）；
- **作用**：保证张量并行维度与数据并行维度的笛卡尔积恰好覆盖全部 NPU 卡，避免卡数浪费或越界。
- **触发条件**：仅当 dp 被显式配置（非 -1）时该约束生效；否则 tp 默认取 worldSize。

**公式 2（dp / tp / cp / sp 四者联合约束）**

$$
\text{dp} \times \text{tp} \times \text{cp} = \text{worldSize}, \quad \text{且 } \text{dp} = 1
$$

- **cp**：Attention 模块中的上下文并行数（int32_t，默认 1）；
- 作用：在启用上下文并行（cp>1）时，**数据并行维度必须让位**（dp 强制为 1），三者的乘积仍须等于 worldSize。
- 原文示例：worldSize=16，tp=8，sp=8，则 dp=1、cp=2 → 1×8×2=16 ✓。

**公式 3（sp 与 tp 联合约束）**

$$
\text{sp} = \text{tp}
$$

- **sp**：Attention 模块中的序列并行数（int32_t，默认 1）；
- 作用：序列并行是张量并行的"伴随维度"，二者必须保持 1:1 镜像关系；sp 不能独立选择数值。
- 原文示例：worldSize=16，tp=8，dp=2，则 sp 只能为 8（注意此时 cp 默认 1，不触发公式 2）。

**默认值汇总（隐含公式）**

$$
\text{dp}_{\text{default}} = -1,\quad \text{tp}_{\text{default}} = \text{worldSize},\quad \text{cp}_{\text{default}} = 1,\quad \text{sp}_{\text{default}} = 1
$$

- 作用：四个开关全部关闭时，Attention 模块走"整网张量并行"，不引入任何额外并行维度。

## 【关联】

- **服务化参数说明（内部链接）**：本文档第 3 步明确指引读者查阅 [`../user_manual/service_parameter_configuration.md`](../user_manual/service_parameter_configuration.md) 了解 `config.json` 中 ModelConfig 全部服务化参数的语义，本文档只聚焦补充的 `tp / dp / cp / sp` 四个开关。
- **张量并行（TP）**：与 DP 构成"批次维 vs. 张量维"的正交互补，二者乘积恒等于 worldSize；示例中 `tp: 1, dp: 8, worldSize: 8` 即"Attention 内全部走数据并行、张量维度退化为 1"的典型配置。
- **上下文并行（CP）/ 序列并行（SP）**：均限定在 Attention 模块；CP 与 DP 互斥（CP 开启时强制 dp=1），SP 与 TP 镜像（sp 必须等于 tp）。
- **MoE 张量并行（moe_tp）**：文末 NOTE 提到"不配置以上补充参数时，推理过程中默认使用 tp 和 moe_tp 并行方式"，说明 MoE 专家并行的开关独立于本表四参数之外；示例配置 `tp: 1, dp: 8` 即隐含 MoE 部分走 moe_tp（由模型默认行为接管）。
- **Attention / MLP 模块覆盖**：限制与约束章节给出"所有模型的 Attention 模块、MLP 模块均支持"，且 DP 与 TP 可在同一模块上叠加，意味着该特性并不局限在 Attention——但表格中 `dp / cp / sp` 的"配置说明"列仅写明 Attention 模块作用域，原文未给出 MLP 模块的 DP 数值配置入口与作用域细节。
- **MindIE Motor / 调度器**：第 5 步发送推理请求时需参考《MindIE Motor 开发指南》中"集群管理组件 > 调度器（Coordinator） > RESTful接口API > OpenAI推理接口"章节，DP 开启后多卡并发请求会由调度器按批次分发到不同设备。

## 【使用方法】

**前置条件（原文）**：需先在环境上安装 CANN 与 MindIE（详见《MindIE 安装指南》）。

**Step 1 — 设置显存优化环境变量（原文）**：

```bash
export PYTORCH_NPU_ALLOC_CONF=expandable_segments:True
export ATB_WORKSPACE_MEM_ALLOC_ALG_TYPE=3
```

**Step 2 — 打开 Server 的 config.json（原文）**：

- whl 包：`cd {MindIE安装目录}/mindie_llm/ && vi conf/config.json`
- run 包：`cd {MindIE安装目录}/latest/mindie-service && vi conf/config.json`

**Step 3 — 在 config.json 的 ModelConfig 中按表 1 添加参数（原文示例，逐字保留）**：

```json
"ModelConfig" : [
    {
        "modelInstanceType" : "Standard",
        "modelName" : "deepseekv2",
        "modelWeightPath" : "/home/data/DeepSeek-V2-Chat-W8A8-BF16/",
        "worldSize" : 8,
        "cpuMemSize" : 5,
        "npuMemSize" : 1,
        "backendType" : "atb",
        "trustRemoteCode" : false,
        "tp": 1,
        "dp": 8,
        "cp": 1,
        "sp": 1
    }
]
```

该示例含义：8 卡推理，Attention 模块使用数据并行（dp=8），MoE 模型使用张量并行（tp=1 由 moe_tp 默认接管）。完整服务化参数语义需参见 [`../user_manual/service_parameter_configuration.md`](../user_manual/service_parameter_configuration.md)。

**Step 4 — 启动服务（原文命令）**：

- whl 包：`mindie_llm_server`
- run 包：`./bin/mindieservice_daemon`

**Step 5 — 发送推理请求（原文）**：参考《MindIE Motor 开发指南》"集群管理组件 > 调度器（Coordinator） > RESTful接口API > 用户侧接口 > OpenAI推理接口"章节。

> **关键合规校验（操作时务必自检，原文给出的硬约束）**：
> 1. 当配置 dp（≠-1）时，必须满足 `tp × dp = worldSize`；
> 2. 当配置 cp（>1）联合 sp 时，必须满足 `dp × tp × cp = worldSize` 且 `dp = 1`；
> 3. 当配置 sp 时，必须满足 `sp = tp`；
> 4. 若未配置任何补充参数，系统默认走 `tp` + `moe_tp`，不会启用 DP。
