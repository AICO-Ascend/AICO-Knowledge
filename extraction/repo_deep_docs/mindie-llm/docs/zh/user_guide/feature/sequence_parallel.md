# Sequence Parallel

> 仓 `mindie-llm` · 路径 `docs/zh/user_guide/feature/sequence_parallel.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-llm/docs/zh/user_guide/feature/sequence_parallel.md

# Sequence Parallel (SP, 序列并行) 深度解读

## 【定位】

这篇文档描述的是 MindIE LLM 推理引擎中的**序列并行（Sequence Parallel, SP）特性**——通过对 KV Cache 在多个 rank 上进行切分，使每个 sp rank 只保存部分 KV Cache，从而达到节省显存、支持更长序列推理的目的。

---

## 【技术要点】

1. **核心机制**：对 KV Cache 进行切分，每个 sp rank 各自保存不同的 KV Cache 片段，从而降低单卡显存占用，支持更长序列。
2. **硬件与模型约束**：
   - 硬件：仅 **Atlas 800I A2 推理服务器**和 **Atlas 800I A3 超节点服务器**支持。
   - 模型：仅 **DeepSeek-R1 的 W8A8、W4A8 量化模型**、**DeepSeek-V3 的 W4A8 量化模型**和 **DeepSeek-V3.1 的 W4A8 量化模型**支持。
   - 精度：**不支持 BF16**。
3. **关键约束 — `SP == TP`**：KV Cache 切分份数必须与张量并行度相等。
4. **PD 混部场景并行关系**：可与 `DP×TP=WorldSize` 或 `CP×TP=WorldSize` 同时使用；可叠加 `MTP=1`、异步调度、Prefix Cache。
5. **PD 分离场景并行关系**：仅在 **P 节点**开启 SP，可与 `DP×TP=WorldSize` 或 `CP×TP=WorldSize` 同时使用；可叠加 MTP、异步调度、Prefix Cache。
6. **配置入口**：在 Server 端 `config.json` 的 `ModelDeployConfig.ModelConfig` 中添加 `"sp"` 字段（int 类型）。

---

## 【关键机制与数据】

**工作原理（原文）：**

> "Sequence Parallel（SP，序列并行）通过对 KV Cache 进行切分，使得每个 sp rank 保存的 KV Cache 各不相同，达到节省显存，支持长序列的功能。"

即 SP 本质上不是对激活值或权重做切分，而是**专门针对推理过程中的 KV Cache** 做切分，与 TP（权重切分）从不同维度减少单卡显存压力。

**并行关系约束（原文摘录）：**

- `sp = tp`（强制约束）
- PD 混部：`dp × tp = WorldSize` 或 `cp × tp = WorldSize`
- PD 分离：`dp × tp = WorldSize` 或 `cp × tp = WorldSize`（仅在 P 节点）

**配置示例中的数据（原文 config.json）：**

```
worldSize = 16
dp = 2
sp = 8
tp = 8
moe_ep = 16
moe_tp = 1
maxSeqLen = 2560
maxInputTokenLen = 2048
cpuMemSize = 5
npuMemSize = -1
```

可以验证 `sp == tp == 8`，且 `dp × tp = 2 × 8 = 16 = worldSize`，完全符合文档约束。

---

## 【表格解读】

**表 1 SP 特性补充参数：ModelDeployConfig 中的 ModelConfig 参数**

| 配置项 | 取值类型 | 取值范围 | 配置说明 |
|--------|----------|----------|----------|
| sp | int | sp=tp | KV Cache 切分得到的份数。 |

**逐行解读：**

- **配置项 `sp`**：在 `ModelConfig` 数组元素中新增的字段，用于声明序列并行的 rank 数（即 KV Cache 被切成几份）。
- **取值类型 `int`**：整数类型，与 TP、DP、CP 等并行度字段一致。
- **取值范围 `sp=tp`**：硬约束，SP 必须与 TP 完全相等；不等则不满足启用条件。
- **配置说明**："KV Cache 切分得到的份数"——这是 SP 的全部语义，即 SP rank 数等于 KV Cache 在序列维度被切分的份数，每个 rank 持有其中一份。

> 原文无其他表格，配置文件示例为 JSON 代码块而非表格形式，因此仅还原表 1。

---

## 【公式解读】

原文无 LaTeX 或显式公式。但文档中包含若干**约束性算式**，原文表述如下：

1. **`sp = tp`** —— SP 与 TP 相等。
2. **`dp × tp = WorldSize`** —— DP 与 TP 的乘积等于总进程数（PD 混部与 PD 分离均适用）。
3. **`cp × tp = WorldSize`** —— CP 与 TP 的乘积等于总进程数（PD 混部与 PD 分离均适用）。

**符号含义：**

- `sp`：序列并行度（KV Cache 切分份数）。
- `tp`：张量并行度（权重切分份数）。
- `dp`：数据并行度。
- `cp`：上下文并行度（context parallel）。
- `WorldSize`：总进程/卡数。

**作用**：这些等式是并行拓扑划分的约束条件，决定了在给定硬件规模下如何组合多种并行策略而不发生资源冲突或冗余。

---

## 【关联】

文档通过场景与特性把 SP 与推理系统中的多个模块串联起来：

1. **PD 分离场景** → 仅在 **P 节点**（Prefill 节点）开启 SP，与 DP/TP/MTP 或 CP/TP/MTP 组合使用。详细部署参见《MindIE Motor 开发指南》中"集群服务部署 > PD 分离服务部署"章节（文档中以外部指引形式引用，未提供内部链接）。
2. **PD 混部场景** → 与 DP/TP/MTP、CP/TP/MTP、异步调度、Prefix Cache 叠加；详细部署参见《MindIE 安装指南》中"配置 MindIE > 配置 Server > 多机推理"章节（同样以外部指引引用）。
3. **与 TP 的关系**：`sp = tp` 是硬性绑定，意味着 SP 的拓扑结构完全复用 TP 的 rank 划分。
4. **与 CP 的关系**：PD 场景下可与 CP 叠加使用，约束为 `cp × tp = WorldSize`。
5. **与 MTP 的关系**：PD 混部时限定为 `MTP=1`；PD 分离时不限定 MTP 取值。
6. **与 Prefix Cache、异步调度的关系**：两种部署场景下均可叠加，属于正交特性。
7. **与 DP、MoE 专家并行（`moe_ep`、`moe_tp`）的关系**：配置示例中可见 `moe_ep=16, moe_tp=1`，表明 SP 启用时 MoE 专家并行可独立配置，但需保证整体并行拓扑一致。

---

## 【使用方法】

**启用步骤（原文）：**

1. **打开 Server 的 config.json 文件**：
   - whl 包安装方式：
     ```bash
     cd {MindIE安装目录}/mindie_llm/
     vi conf/config.json
     ```
   - run 包安装方式：
     ```bash
     cd {MindIE安装目录}/latest/mindie-service
     vi conf/config.json
     ```

2. **添加 `sp` 字段**，示例（原文提供的 config.json 片段）：

   ```json
   "ModelDeployConfig" :
   {
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
               "dp": 2,
               "sp": 8,
               "tp": 8,
               "moe_ep": 16,
               "moe_tp": 1
           }
       ]
   }
   ```

   该示例同时演示了 `dp=2`、`sp=8`、`tp=8`、`worldSize=16` 的合法组合（满足 `sp=tp`、`dp×tp=WorldSize`）。

3. **启动服务**：
   - whl 包安装方式：`mindie_llm_server`
   - run 包安装方式：`./bin/mindieservice_daemon`

**关键配置项说明（原文）：**

- `sp`：int 类型，取值 `sp=tp`，表示 KV Cache 切分得到的份数。

**使用前置条件（汇总）：**

- 硬件须为 Atlas 800I A2 或 Atlas 800I A3 超节点服务器。
- 模型须为 DeepSeek-R1 W8A8、DeepSeek-R1 W4A8、DeepSeek-V3 W4A8 或 DeepSeek-V3.1 W4A8 量化模型之一。
- 不得使用 BF16 精度。
- PD 分离时仅在 P 节点配置 `sp`。

> 文档未涉及 CLI 启动参数、环境变量、性能调优开关等更细粒度的启用方式，原文均未给出。
