# SplitFuse

> 仓 `mindie-llm` · 路径 `docs/zh/user_guide/feature/split_fuse.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-llm/docs/zh/user_guide/feature/split_fuse.md

# SplitFuse 特性文档深度解读

## 【定位】

本文档系统描述了 MindIE-LLM 推理引擎中的 **SplitFuse** 特性：一种通过**将长 prompt 请求切分为更小 chunk 在多 forward step 中调度、并用短 prompt 填空以均衡每步计算量**的调度优化手段，旨在降低长 prompt 处理延迟、稳定所有请求的平均延迟、保持高吞吐。

---

## 【技术要点】

1. **核心机制（chunk 切分与组合调度）**：将长 prompt request 分解为更小的块分多轮 forward 执行，**仅最后一块完成后才开始生成**；同时将短 prompt request 组合起来精确填充 step 空隙，使每个 step 计算量基本相等，从而稳定平均延迟。
2. **PD 混部策略升级**：默认 PD 混部下 Prefill 与 Decode 请求**不组合到一个 batch**；开启 SplitFuse 后，**优先处理 Decode 请求**，并在 `batch < maxBatchSize` 时**将 Prefill 请求加入同一 batch**。
3. **切分触发条件**：当本轮 feedforward（处理量）**大于 `splitChunk tokens`** 时，SplitFuse 对其切分（原文未给出 `splitChunk` 的具体计算式，配套以三张公式图示）。
4. **token 构成**：Prefill 阶段 tokens = 输入 token 数量；Decode 阶段每个请求 = 1 token（原文以图示 `formula_3_splirfuse.png` 表达）。
5. **量化与模型范围**：仅支持 **W8A8** 量化；模型支持 **LLaMA3.1-70B 浮点、Qwen2 / Qwen2.5 / Qwen3 系列**；硬件为 **Atlas 800I A2 推理服务器** 和 **Atlas 800I A3 超节点服务器**。
6. **互斥与后处理兼容**：**不可与 Multi-LoRA、Function Call、并行解码、MTP、长序列** 同时使用；后处理参数支持 `n`、`best_of`、`use_beam_search`。
7. **调优关键参数**：`templateType`（"Mix"/"Standard"）、`prefillChunkSize`（固定切块）、`maxNumPartialPrefills`（默认 64）、`longPrefillTokenThreshold`（默认 1024）、`maxLongPartialPrefills`（默认 8）。

---

## 【关键机制与数据】

### 工作原理与数据流（综合原文）

- **触发入口**：用户开启 `plugin_params = "{\"plugin_type\":\"splitfuse\"}"` 并设置 `templateType = "Mix"`，MindIE 即进入 SplitFuse 调度。
- **调度优先级**：Decode 请求优先于 Prefill 请求被处理（原文明确表述）。
- **批组合条件**：仅当当前 `batch < maxBatchSize` 时，新 Prefill 请求被加入 Decode 所在 batch（原文明确表述）。
- **chunk 切分触发**：单次 feedforward 处理量 > `splitChunk tokens` 时即切分（原文表述，未给出 `splitChunk` 的具体公式）。
- **token 计费**：Prefill 阶段按输入 token 数计、Decode 阶段按 1 token/请求计（原文表述）。
- **生成时机**：原文强调"只有最后一块的 forward 完成后才开始这个 prompt request 的生成"——即长 prompt 切分后只在其最后一块 forward 结束才进入解码。

### 性能/对比性原文陈述（非数值）

- 原文未给出绝对 TPS / 时延数字，但定性陈述：
  - **响应速度**：长 prompt 处理延迟减少。
  - **效率**：短 prompt 合理组合，保持高吞吐。
  - **一致性**：统一前向传递大小，降低延迟波动，使生成频率稳定。
  - **相对 PD 混部**：原文明确"PD 混部策略产生更多调度空泡；而 SplitFuse 特性相对 PD 混部策略受调度空泡影响较少，所以相对 PD 混部策略的优势会增加"——并提示**输入问题长短不一的场景下 SplitFuse 优势更明显**。

> 原文未提供具体性能数据表或量化指标，仅给出**调优方向**（Step 5）：根据首 Token 时延和 Decode 时延（均值、P90）调整 `RequestRate` 与 ChunkSize。

---

## 【表格解读】

### 表 1：ModelDeployConfig.ModelConfig 参数

| 配置项 | 取值类型 | 取值范围 | 配置说明 |
|---|---|---|---|
| `plugin_params` | `std::string` | `"{\"plugin_type\":\"splitfuse\"}"` | 设置为 `"{\"plugin_type\":\"splitfuse\"}"` 表示执行 splitfuse；不需要生效任何插件功能时请删除该配置项字段。<br>**约束**：若 `templateType` 为 "Mix"，则此处必须开启为 splitfuse（特性不开启时非必填项）。 |

**逐行解读**：
- **配置项 `plugin_params`**：这是**开启 SplitFuse 特性本身的开关**，位于 `ModelConfig` 数组的每个 modelInstance 内。**唯一合法取值**为该 JSON 字符串，且字符串内的 `plugin_type` 固定为 `splitfuse`。
- **配置说明**：第一句是开启定义；第二句给出**反向操作**——不开启插件功能时不要保留该字段（避免误启用）。
- **约束**：揭示了"特性内部联动规则"——只要上层 `templateType`（见表 2）选了 `"Mix"`，`plugin_params` 就**必须**配为 splitfuse；否则（特性整体未开启时）该字段非必填。

### 表 2：ScheduleConfig 参数

| 配置项 | 取值类型 | 取值范围 | 配置说明 |
|---|---|---|---|
| `templateType` | `std::string` | `"Standard"` 或 `"Mix"` | `"Mix"`：混部推理场景，Prefill 和 Decode 可同时进行批处理；`"Standard"`：默认值（特性不开启时为必填项），表示 prefill 和 decode 各自分别组 batch。 |
| `prefillChunkSize` | `uint32_t` | `[1, maxPrefillTokens]` | 设置此值时表示开启对 prefill 请求的**固定长度切分**；不配置此值时将根据 `maxPrefillTokens` 和 prefill 请求数量计算当前切分长度，进行**动态切分**。 |
| `maxNumPartialPrefills` | `uint32_t` | `[1, maxBatchSize]` | 动态切分时使用，表示 batch 中可以被并行做 partial prefill 的最大请求数。**默认值：64**。 |
| `longPrefillTokenThreshold` | `uint32_t` | `[1, maxPrefillTokens]` | 动态切分时使用，表示被判定为长 prefill 请求的 token 数阈值；请求 prompt 长度大于此阈值且 batch 中长 prefill 请求个数超过 `maxLongPartialPrefills` 时，**超出部分将被延时调度以保障短序列的 TTFT 时延**。**默认值：1024**。 |
| `maxLongPartialPrefills` | `uint32_t` | `[1, maxBatchSize]` | 动态切分时使用，表示 batch 中允许容纳的长 prefill 请求个数。**默认值：8**。 |

**逐行解读**：
- **`templateType`**：SplitFuse 行为的**总开关二**。`"Mix"` 启用混部批处理（与 SplitFuse 配套）；`"Standard"` 是 PD 分离的传统模式。注意原文措辞"`"Standard"`：默认值（特性不开启时为必填项）"——表明在未启用 SplitFuse 时此字段也必须填 `"Standard"`。
- **`prefillChunkSize`**：**切分粒度控制**——固定切分与动态切分的切换点。设为合法值即开启固定 chunk；不设（或留空）则进入动态切分模式，由 `maxPrefillTokens` 与请求数动态决定。
- **`maxNumPartialPrefills`**：单 batch 中**并行 partial prefill 的请求数上限**，默认 64。值越大越能"塞满"每个 forward step 的空闲算力，但会增加显存/CPU 调度压力。
- **`longPrefillTokenThreshold`**：长 prefill 的判别阈值，默认 1024 token。结合下一项共同保护短序列 TTFT。
- **`maxLongPartialPrefills`**：每 batch 允许的**长 prefill 请求上限**，默认 8。超过此上限的长 prefill 请求会被**延时调度**，避免短序列被长 prompt 拖累——这是 SplitFuse"保护短序列 TTFT"的关键参数组合。

---

## 【公式解读】

原文共引用 3 张图片（`formula_1_splirfuse.png`、`formula_2_splirfuse.png`、`formula_3_splirfuse.png`），**文档原文未给出 LaTeX 或伪代码形式的公式正文**。下方根据原文上下文逐图重建其语义（不臆造具体符号表达式）：

### 公式 1（figures/formula_1_splirfuse.png）

- **原文位置**：处于"每一推理轮次中："之后，是 split 切分的**主公式**。
- **符号含义与作用**（基于上下文推断）：
  - 该公式表达**每一推理轮次（per-step）的总处理 token 数**等于"该 step 内所有请求的 Prefill tokens 之和 + Decode tokens 之和"。
  - 与原文"每一推理轮次中"以及公式 3 的 Prefill/Decode token 计费方式配合：Prefill 侧按请求输入 token 数累加，Decode 侧按 1 token/请求累加。
- **作用**：作为 split 触发判断（即与 `splitChunk tokens` 比较）的基准量。

### 公式 2（figures/formula_2_splirfuse.png）

- **原文位置**：紧跟公式 1，描述 split 切分的**约束或分块长度**。
- **符号含义与作用**（基于上下文推断）：
  - 该公式与"当该次处理的 feedforward 大于 splitChunk tokens 时，SplitFuse 会对其进行切分"配合，表达 `splitChunk tokens` 的取值上限/约束（典型为不超过 `maxPrefillTokens` 或受 `prefillChunkSize`/`prefillChunk` 动态值约束）。
- **作用**：限定单次 forward 的最大 token 数，使超长 prefill 被切成多个 ≤ `splitChunk tokens` 的块。

### 公式 3（figures/formula_3_splirfuse.png）

- **原文位置**：紧跟"Prefill 阶段的 tokens 为输入 token 数量，Decode 阶段每个请求为 1 token："之后。
- **符号含义与作用**：
  - 直接给出 **Prefill tokens 与 Decode tokens 的计费定义**：
    - Prefill tokens = 该请求的输入 token 数量（记作 `L_prompt` 或 `n_in`）。
    - Decode tokens = 1（每请求每 step 增量 1 token，记作 `1` 或 `Δ`）。
  - 是公式 1 中"Prefill 求和项"与"Decode 求和项"的具体取值规则。
- **作用**：统一 step 内 Prefill 与 Decode 的 token 计费口径，使两阶段可被同一切分公式处理。

> ⚠ 说明：上述三式在原文中**均为图片引用**，未提供可逐字保留的 LaTeX 或伪代码文本；故此处仅依据原文语句对各图所表达的功能角色进行解释，**未添加原文不存在的具体符号或数值**。

---

## 【关联】

文档内部链接揭示的上下游关联：

1. **服务化参数总表** — `../user_manual/service_parameter_configuration.md`
   - 在"执行推理"步骤中明确：SplitFuse 的 `plugin_params`、`templateType`、`prefillChunkSize` 等需要在 `Server/config.json` 中配置；而该章节"配置参数说明（服务化）"提供**完整的服务化参数语义说明**。两者是"特性用法"与"全局参数手册"的对应关系——本特性文档聚焦 SplitFuse 子集配置，全局/非 SplitFuse 字段（如 `maxSeqLen`、`maxBatchSize`、`cacheBlockSize` 等）需查阅服务化参数章节。

2. **性能测试入口** — `../quick_start/quick_start.md#性能测试`
   - "执行推理"步骤 4 指引用户使用 **AISBench** 工具进行性能测试，本链接指向快速入门中的"性能测试"章节，给出 AISBench 的标准测试流程与指标采集方法。
   - 步骤 5 的"调优方向"（首 Token 时延 / Decode 时延均值与 P90 vs RequestRate、ChunkSize 的取舍）即基于该性能测试得到的数据进行闭环调参。

3. **与 PD 混部策略的关系（文档内隐式关联）**
   - 原文将 SplitFuse 与"默认 PD 混部策略"作为对照基线：SplitFuse 通过 chunk 切分+空隙填充缓解 PD 混部在"输入长短不一"场景下的**调度空泡**问题；因此上游 PD 混部策略、调度器（ScheduleConfig）以及下游 W8A8 量化算子、Decode 路径共同决定 SplitFuse 的端到端收益。

4. **与互斥特性的关系**
   - 文档明确列举互斥特性：**Multi-LoRA、Function Call、并行解码、MTP、长序列**——这些特性在调度/算子层面与 SplitFuse 的 chunk 切分存在冲突，启用其一则不可同时启用 SplitFuse。

---

## 【使用方法】

### 启用步骤（原文 Step 1–3）

1. **打开 Server 的 config.json**
   - **whl 包**：`cd {MindIE安装目录}/mindie_llm/` 后 `vi conf/config.json`
   - **run 包**：`cd {MindIE安装目录}/latest/mindie-service` 后 `vi conf/config.json`

2. **配置关键参数**（按表 1、表 2）：
   - `ModelDeployConfig.ModelConfig[].plugin_params = "{\"plugin_type\":\"splitfuse\"}"`（**`templateType="Mix"` 时必填**）
   - `ScheduleConfig.templateType = "Mix"`（启用混部批处理）
   - 可选：`ScheduleConfig.prefillChunkSize`（**固定切分**；否则使用动态切分）
   - 动态切分参数（可选，未配取默认）：`maxNumPartialPrefills=64`、`longPrefillTokenThreshold=1024`、`maxLongPartialPrefills=8`

3. **启动服务**
   - **whl 包**：`mindie_llm_server`
   - **run 包**：`./bin/mindieservice_daemon`

### 配置示例（原文直接给出的 JSON 片段，关键字段）

```json
"ModelDeployConfig": {
    "maxSeqLen": 65536,
    "maxInputTokenLen": 65536,
    "ModelConfig": [{
        "modelInstanceType": "Standard",
        "modelName": "llama3-70b",
        "modelWeightPath": "/home/models/llama3-70b/",
        "worldSize": 8,
        "backendType": "atb",
        "plugin_params": "{\"plugin_type\":\"splitfuse\"}"
    }]
},
"ScheduleConfig": {
    "templateType": "Mix",
    "cacheBlockSize": 128,
    "maxPrefillBatchSize": 40,
    "maxPrefillTokens": 65536,
    "maxBatchSize": 256,
    "maxIterTimes": 512,
    "prefillChunkSize": 1024,
    "maxNumPartialPrefills": 64,
    "longPrefillTokenThreshold": 1024,
    "maxLongPartialPrefills": 8
}
```

### 性能调优（原文 Step 4–5）

1. **执行性能测试**：使用 **AISBench** 工具测试首 Token 时延与 Decode 时延，参见《快速入门》"性能测试"章节。
2. **调优策略**：
   - **首 Token 时延 & Decode 时延（均值、P90）均达标** → 加大 `RequestRate`。
   - **Decode 均值达标、TTFT 均值超标** → `RequestRate` 已超系统吞吐，应**降低 `RequestRate`**。
   - **均值达标、Decode P90 不达标** → **降低 ChunkSize（`prefillChunkSize`）** 减小切分；该操作可能影响吞吐。
   - **输入问题长短不一**场景：SplitFuse 相对 PD 混部受调度空泡影响更少，**优势更显著**。

## 图文联合解读

- `formula_1_splirfuse.png`: # 图文联合解读

**1) 图中内容**：纵向条形/波形图，多根高低不一的竖条按时间顺序排列，形成"高峰—低谷—高峰"的节奏分布。高峰代表长Prompt的前向计算，低谷由短Prompt填充补齐。

**2) 技术结论**：每个step（竖条）的计算量（即条高）大致均等；SplitFuse通过将长prompt切块（高峰拆分为多个中等条）、用短prompt填空（低谷抬升），使每个forward step的token负载基本一致。

**3) 与文档关系**：直观印证文档论点——"长prompt拆块、多步调度，短prompt组合填隙，每step计算量基本相等，延迟更稳定"，对应"提高响应速度/提升效率/增强一致性"三大优势。
- `formula_2_splirfuse.png`: **图文联合解读：**

1）**图示内容**：该图（formula_1/2_splirfuse）描绘了多个连续推理轮次（forward step）的时间轴调度。每一轮次展示"forward = splitChunk tokens"的均衡预算：长prompt被纵向切分为若干块（左侧深色柱），跨多轮逐步推进；短prompt则横向拼接填入剩余空隙（右侧浅色柱），形成"切块+填充"的两类请求混排结构。

2）**论证结论**：每个forward step的计算量（token数）大致恒定，避免了传统PD分离调度下"长请求独占一轮、短请求瞬时完成"的负载不均问题，从而拉齐所有请求的端到端延迟。

3）**与文档关系**：直观支撑文档所述两大关键行为——①长prompt拆块跨轮调度、仅末轮生成token；②短prompt切分填隙保计算饱和，对应"提高响应速度、提升效率、增强一致性"三大优势。
- `formula_3_splirfuse.png`: ## 图文联合解读

**1) 图中内容**
该图为SplitFuse调度时序示意图（formula_2_splirfuse.png），沿时间轴展示多轮forward step：纵向密集线条代表每步处理的token批次，中间灰色横条标示Prefill切分块，上下分布的细线为Decode请求tokens；可见长prompt被纵向切分为多个chunk，短prompt被横向填充至batch间隙，形成三组均衡的"波峰"。

**2) 技术结论**
证明SplitFuse能将Prefill与Decode在同一batch中交错调度，使每步feedforward接近splitChunk tokens上限，计算负载均衡。

**3) 与文档关系**
呼应文中"长prompts分解为小块、短prompts填补空隙、每步计算量基本相等"的论点，直观论证降低延迟波动的实现机制。
