# SLO调度优化

> 仓 `mindie-llm` · 路径 `docs/zh/user_guide/feature/slo_aware_scheduling_optimization.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-llm/docs/zh/user_guide/feature/slo_aware_scheduling_optimization.md

# SLO 调度优化 — 一体化深度解读

## 【定位】

**这篇文档描述了 MindIE LLM 在高并发请求场景下，基于 SLO（服务级别目标）的两套调度优化机制（PD 阶段选择的 LLF 算法 + 动态 BatchSize 调整），用以在满足 TTFT/TPOT 时延目标的前提下提升系统吞吐量。**

---

## 【技术要点】

1. **两套并行的优化手段**：① 基于 TTFT/TPOT 时延预测 + Least Laxity First (LLF) 的 PD 阶段选择算法；② 基于实时 TPOT 感知的动态 BatchSize 调整算法。
2. **LLF 算法的核心逻辑**：通过采集当前 TTFT/TPOT 时延数据进行拟合建模，预测每次 Prefill 和 Decode 阶段的处理时间，再用 LLF 算法决定下一批 Batch 是执行 Prefill 还是 Decode；适用于对 TTFT/TPOT 均有严格要求的场景。
3. **动态 BatchSize 的核心逻辑**：持续监测系统当前 TPOT 时延，与 SLO 中设定的 Decode 时延目标比对，动态调整 `maxPrefillBatchSize` 和 `maxBatchSize`，避免所有请求都进入片上内存导致系统拥塞；适用于对 TPOT 有强要求的场景。
4. **硬件/模型/部署形态约束**：仅 Atlas 800I A2 推理服务器支持；DeepSeek-R1、DeepSeek-V3、Qwen 系列模型可对接；仅适用于 PD 混部场景，不能与 SplitFuse 同时打开。
5. **收益场景定位**：原文明确"此特性的收益场景主要在短输出（256 以下）场景，随着输出长度变长，吞吐收益会下降"。
6. **参数化可控**：通过 4 个配置项（`stageSelectPolicy`、`dynamicBatchSizeEnable`、`prefillExpectedTime`、`decodeExpectedTime`）控制算法启停与目标时延，整数取值范围 `[0,10000]`，默认值 `prefillExpectedTime=1500`、`decodeExpectedTime=50`、`stageSelectPolicy=0`、`dynamicBatchSizeEnable=false`。

---

## 【关键机制与数据】

### 机制一：LLF (Least Laxity First) PD 阶段选择
- **数据采集**：采集"当前"的 TTFT 和 TPOT 时延数据。
- **建模**：对采集数据进行"拟合建模"，从而**预测**每次 Prefill 与 Decode 阶段的处理时间（原文用词为"预测每次Prefill和Decode阶段的处理时间"）。
- **决策**：基于预测结果，用 LLF 算法决定"下一批 Batch"是执行 Prefill 还是 Decode——即在每个调度粒度上做 PD 选择。
- **适用语义**：对 TTFT 和 TPOT 均有严格要求。

### 机制二：动态 BatchSize 调整
- **监测对象**：系统当前的 TPOT 时延（实时波动，原文："由于TPOT采集存在实时波动"）。
- **比对基准**：SLO 中设定的 Decode 时延目标（对应参数 `decodeExpectedTime`）。
- **调整对象**：`maxPrefillBatchSize` 和 `maxBatchSize` 两个上限值。
- **目标**：避免所有请求都进入片上内存导致系统拥塞，影响吞吐。
- **优先级语义**：优先保障已进入片上内存请求的响应（即可被继续 Decode 的请求不被中断/降级）。
- **原文给出的精度数据**：实时时延与配置目标之间可能存在**约 10% 的偏差**。

### 部署与场景限定
- **PD 混部**：Prefill 与 Decode 共置运行（与 SplitFuse 即"分离部署"互斥）。
- **短输出**：256 token 以下场景收益最明显；输出变长后吞吐收益下降（原文未给出具体下降比例数值）。

---

## 【表格解读】

### 表 1：SLO 调度优化特性参数说明（逐字还原）

| 配置项 | 取值类型 | 取值范围 | 配置说明 |
|---|---|---|---|
| `stageSelectPolicy` | `uint32_t` | `[0,2]` | Prefill 和 Decode 选择策略。<ul><li>0：prefill 优先</li><li>1：吞吐优先</li><li>2：基于 TTFT/TPOT 时延预测和 LLF 算法的 PD 阶段选择算法</li></ul>选填，默认值：**0**。 |
| `dynamicBatchSizeEnable` | `bool` | <ul><li>true</li><li>false</li></ul> | 是否开启动态 BatchSize 调整算法。选填，默认值：**false**。 |
| `prefillExpectedTime` | `uint32_t` | `[0,10000]` | Prefill 阶段 Token 生成的 SLO 期望时延。选填，默认值：**1500**。 |
| `decodeExpectedTime` | `uint32_t` | `[0,10000]` | Decode 阶段 Token 生成的 SLO 期望时延。选填，默认值：**50**。 |

### 逐行解读

- **`stageSelectPolicy`（3 档枚举，0/1/2）**：决定"下一批 Batch 走 Prefill 还是 Decode"的策略层级。
  - `0` = prefill 优先：始终先做 Prefill，原生默认；
  - `1` = 吞吐优先：以吞吐量为目标的策略（文档未展开其内部算法）；
  - `2` = LLF 算法：本文档主推方案，需配合 TTFT/TPOT 时延预测。
  - 取值类型 `uint32_t`，范围被压缩到 `[0,2]`，说明该字段在协议层预留为枚举，扩展时只需放宽范围。
- **`dynamicBatchSizeEnable`（bool）**：机制二的开关。默认 `false`，意味着动态 BatchSize 是关闭的，避免对未做 SLO 评估的业务产生扰动。开启后，引擎会持续监测 TPOT 并动态调整两个上限。
- **`prefillExpectedTime`（默认 1500）**：Prefill 阶段单个（或某次调度内）Token 生成的 SLO 期望时延，单位未在原文标注，但结合 `decodeExpectedTime` 的典型量级（50）可推测为**毫秒级**（原文未明确单位，**不能臆造单位**）。取值上限 10000。文档示例取 1000，比默认更激进。
- **`decodeExpectedTime`（默认 50）**：Decode 阶段 Token 生成的 SLO 期望时延，是动态 BatchSize 算法对比的"目标值"。文档示例与默认值一致（50），说明解码时延目标通常被设定得很紧。

> **表格与示例配置对照**：示例 `stageSelectPolicy=2`、`dynamicBatchSizeEnable=true`、`prefillExpectedTime=1000`、`decodeExpectedTime=50`，即"机制一 LLF + 机制二动态 BatchSize"同时启用，prefill 目标比默认值更紧。

---

## 【公式解读】

**原文无公式。** 文中仅以自然语言描述了"拟合建模"、"预测处理时间"、"LLF 决定下一批 Batch"等过程，未给出任何 LaTeX 公式、伪代码或数学表达式，也未公开预测模型的形式、松弛度（Laxity）的定义式、BatchSize 调整规则等可被数学化的细节。

---

## 【关联】

文档中通过超链接与其他模块产生关联，主要包含两个出口：

1. **配置层 → 服务化参数说明**
   - 链接：`../user_manual/service_parameter_configuration.md`
   - 关系：本文档在"执行推理"步骤提示"服务化参数说明请参见《配置参数说明（服务化）》"，意味着 `stageSelectPolicy`、`dynamicBatchSizeEnable`、`prefillExpectedTime`、`decodeExpectedTime` 四个字段是写入 Server 的 `config.json` 的**服务化全局配置**，与用户级运行时配置互不重叠；本文档只覆盖这些参数在 SLO 场景下的语义，完整参数清单需跳转该章节。

2. **压测/评估层 → 性能测试章节**
   - 链接：`../quick_start/quick_start.md#性能测试`
   - 关系：文档第 4 步以 AISBench 工具 + GSM8K 数据集 + 并发 500 为例演示调优方式，详情跳转该性能测试章节。说明本特性没有自带的 benchmark 流程，而是借通用 AISBench 评测链路验证 SLO 达标与吞吐。

此外，从功能耦合角度看，本特性与以下概念存在隐含关联（原文未给链接，但语义上相关）：
- **PD 混部**：本文要求"仅适用于 PD 混部场景"，对应 MindIE LLM 中 Prefill/Decode 同进程同硬件的部署形态。
- **SplitFuse**：被本文明确**互斥**（"无法与 SplitFuse 特性同时打开"），两者在 PD 调度粒度上构成"互斥选项"。
- **片上内存（On-chip memory）**：原文用其解释动态 BatchSize 的触发条件——"避免所有请求都进入片上内存导致系统拥塞"，是动态 BatchSize 的容量上限物理基础。

---

## 【使用方法】

### 启用方式（基于原文）

**步骤 1**：打开 MindIE Motor 的 `config.json`：
- whl 包安装：`cd {MindIE安装目录}/mindie_llm/ && vi conf/config.json`
- run 包安装：`cd {MindIE安装目录}/latest/mindie-service && vi conf/config.json`

**步骤 2**：在 Server 的 `config.json` 中添加四个字段，**示例配置**（原文逐字给出）：

```json
"stageSelectPolicy" : 2,
"dynamicBatchSizeEnable" : true,
"prefillExpectedTime" : 1000,
"decodeExpectedTime" : 50
```

字段含义参见原文表 1，完整字段说明参见 `../user_manual/service_parameter_configuration.md`。

**步骤 3**：启动服务：
- whl 包安装：`mindie_llm_server`
- run 包安装：`./bin/mindieservice_daemon`

**步骤 4**：压测示例配置（原文逐字给出，AISBench + GSM8K + 并发 500，`max_out_len=64`，`batch_size=500`）：

```text
models = [
    dict(
        attr="service",
        type=VLLMCustomAPIChatStream,
        abbr='vllm-api-stream-chat',
        path="$ModelPath",
        model="$ModelName",
        request_rate = $1,
        retry = 2,
        host_ip = "{ipAddress}",
        host_port = "{port}",
        max_out_len = 64,
        batch_size= 500,
        trust_remote_code=False,
        generation_kwargs = dict(
            temperature = 0,
            ignore_eos = True
        ),
        pred_postprocessor=dict(type=extract_non_reasoning_content)
    )
]
```

### 关键配置项速查（综合原文）

| 字段 | 含义 | 启用 SLO 调度优化的推荐值（来自原文示例） |
|---|---|---|
| `stageSelectPolicy` | PD 阶段选择策略 | `2`（开启 LLF） |
| `dynamicBatchSizeEnable` | 是否动态调整 BatchSize | `true` |
| `prefillExpectedTime` | Prefill 期望时延 | `1000`（示例值，原默认 `1500`） |
| `decodeExpectedTime` | Decode 期望时延 | `50`（与默认值一致） |

### 硬件/兼容性约束（启用前必读）

- **硬件**：仅 Atlas 800I A2 推理服务器支持。
- **模型**：DeepSeek-R1、DeepSeek-V3、Qwen 系列模型可对接。
- **部署形态**：仅 PD 混部场景；**不能**与 SplitFuse 同时打开。
- **场景建议**：短输出（256 token 以下）收益最显著，长输出场景吞吐收益会下降。
