# 并行解码

> 仓 `mindie-llm` · 路径 `docs/zh/user_guide/feature/speculative_decoding.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-llm/docs/zh/user_guide/feature/speculative_decoding.md

# 「并行解码（Speculative Decoding）」特性文档深度解读

---

## 【定位】

本文档描述 MindIE LLM 推理引擎中的 **并行解码（Speculative Decoding）** 特性：通过借鉴处理器中的"Speculative Execution"思想，利用富余算力在每一步生成多个候选 token 并由主模型验证，从而提升 LLM 推理在"内存带宽受限、算力过剩"场景下的吞吐，解决传统 Auto-Regressive Decoding 因逐 token 串行生成导致并发性不足、硬件利用率低的问题。

---

## 【技术要点】

1. **核心思想 = 推测执行（Speculative Execution）**：在传统自回归逐 token 解码的间隙，利用额外算力提前生成一组候选 token，再由主模型一次性验证（verify），合格者一并采纳，从而减少 decode 步数、提升并发与算力利用率。原文表述："通过额外的计算资源完成推测执行，提升并发性"。
2. **两种候选 token 生成算法**（差异点）：
   - **memory_decoding**：利用 trie tree（前缀树）缓存模型历史的输入输出，从中获取候选 token，适用 **代码生成或检索类场景**。
   - **lookahead**：基于 **Jacobi 迭代**并辅以 Prompt 及输出结果生成候选 token，适用 **文本生成、对话系统及多样化查询回答**。
3. **收益来源**：原文点明——"通过验证 token 的比率会直接影响到并行解码的收益"，**贪婪（greedy）场景更能充分发挥效果**；采样或惩罚类操作会压缩收益空间。
4. **启用前提（3 条必须同时满足）**：
   - 并发数不高、属内存带宽受限、计算资源有冗余；
   - 有 **较长的输入** 作为猜测 token 的初步来源；
   - 需要 **一定长度的输出** 才能体现性能提升（因为增益来自"减少推理步数"）。
5. **首 token 时延代价**：开启并行解码后，会使用 Prompt 输入维护 **前缀树** 和 **草稿 token map**，对首 token 时延有影响。
6. **互斥特性**（不可与并行解码同开）：PD 分离、Multi-LoRA、SplitFuse、长序列、MTP、异步调度、多机推理。
7. **支持的模型与硬件**：
   - 硬件：Atlas 800I A2 推理服务器、Atlas 300I Duo 推理卡。
   - 模型：LLaMA3 系列、Qwen2 系列、Qwen2.5 系列、Qwen3-14B、Qwen3-32B。
   - 量化：仅 W8A8 量化与稀疏量化。

---

## 【关键机制与数据】

### 工作原理

- **传统 Auto-Regressive Decoding 慢的原因**（原文）：step-by-step 导致并发性不够；推理阶段属于"内存带宽受限而计算资源过剩"。
- **并行解码的做法**（原文）：采用"Speculative Execution"，通过额外的计算资源完成推测执行；利用 Prompt 输入维护前缀树和草稿 token map。
- **两种算法的核心差异**（原文表 1）：
  - memory_decoding = trie tree 历史缓存取候选；
  - lookahead = Jacobi 迭代 + Prompt + 输出结果 生成候选。
- **限制层面（原文逐条）**：
  - 不支持流式推理；
  - 不支持 HealthCheck；
  - 惩罚类后处理仅支持重复惩罚；
  - 不支持 n / best_of / use_beam_search / logprobs / top_logprobs 等多序列推理参数；
  - lookahead 与 memory_decoding 不可同时使能。

### 性能/收益相关定性描述（原文）

- "针对足够长度的输入输出或代码生成等场景的 **小 batch 推理**，并行解码特性可利用算力优势弥补访存带宽受限的影响，提升算力利用率。"——即收益场景 = **小 batch + 长输入 + 一定长度输出**。
- 收益与"验证 token 比率"正相关；贪婪采样 > 采样/惩罚。

> 注：原文未提供具体的 TPS、加速比、命中率等量化性能数据。

---

## 【表格解读】

### 表 1：并行解码算法（差异总览）

| 并行解码算法 | 候选 token 生成方式 | 适用场景 |
|---|---|---|
| memory_decoding | 利用 trie tree（前缀树）缓存模型历史的输入输出，从中获取候选 token。 | 代码生成或检索类场景。 |
| lookahead | 基于 Jacobi 迭代并辅以 Prompt 以及输出结果生成候选 token。 | 文本生成、对话系统及多样化查询回答。 |

**逐行解读**：
- memory_decoding 行：候选源是"历史的输入/输出"，依赖 trie tree 缓存复用，因此对 **重复出现的前缀**（代码补全、检索式问答）非常敏感，适合高频重复模式的场景。
- lookahead 行：候选源是"Jacobi 迭代 + 当前 Prompt + 已生成输出"，不需要历史缓存复用，更适合 **开放域文本生成**，但 Jacobi 迭代本身需要额外的 N/W/G 参数控制深度（见后文表 5、表 6）。

---

### 表 2：memory_decoding 补充参数 1 —— ModelDeployConfig 中的 ModelConfig 参数

| 配置项 | 取值类型 | 取值范围 | 配置说明 |
|---|---|---|---|
| plugin_params | std::string | plugin_type：memory_decoding<br>decoding_length：[1, 16]<br>dynamic_algo：true 或 false | <ul><li>plugin_type 配置 memory_decoding，表示当前选择 memory_decoding 并行解码。</li><li>decoding_length 为 memory_decoding 算法中的参数，表示候选 token 的最大长度，默认值 16。</li><li>dynamic_algo 为可选参数，配为 true 时表示开启动态自适应候选长度功能，默认值 False。</li><li>不需要生效任何插件功能时，请删除该配置项字段。</li><li>配置示例：{"plugin_type":"memory_decoding","decoding_length": 16,"dynamic_algo": true} 或 {"plugin_type":"memory_decoding","decoding_length": 16}</li></ul> |

**逐行解读**：
- `plugin_type = memory_decoding` 是开关标识。
- `decoding_length ∈ [1,16]` 控制 **候选 token 最大长度**，默认 16；该值直接决定一轮可推测多少 token。
- `dynamic_algo = true/false`（默认 False）开启 **动态自适应候选长度**，可根据实际情况自动调整猜测长度，从而在命中率波动时兼顾收益与开销。
- 不需要插件时需 **删除该字段**，而非留空，说明该字段存在即触发插件逻辑。

---

### 表 3：memory_decoding 补充参数 2 —— ModelDeployConfig 的参数

| 配置项 | 取值类型 | 取值范围 | 配置说明 |
|---|---|---|---|
| speculationGamma | uint32_t | 与 plugin 参数配置有关 | memory_decoding 时，该值配置应 **大于等于 decoding_length**。<br>建议值：等于 decoding_length。 |

**逐行解读**：
- `speculationGamma` 是推测步数 / 推测 gamma，决定一次并行解码过程中主模型验证阶段期望验证的候选 token 数量上限。
- 约束 `speculationGamma ≥ decoding_length` 意味着 **验证窗口 ≥ 一次推测产生的候选最大长度**，否则会被截断导致猜测浪费。

---

### 表 4：memory_decoding 补充参数 3 —— ScheduleConfig 的参数

| 配置项 | 取值类型 | 取值范围 | 配置说明 |
|---|---|---|---|
| maxIterTimes | uint32_t | 与 plugin 参数配置有关 | 如果 dynamic_algo 为 true，该值需 **大于等于期望输出的长度 + speculationGamma 的值**。<br>例：期望最大输出长度为 512，则该值需要配置 >= 512 + speculationGamma。 |

**逐行解读**：
- `maxIterTimes` 是调度侧的总迭代上限；当开启 `dynamic_algo` 时，必须预留足够的迭代次数来容纳**完整输出长度 + 推测验证所需步数**，否则在长输出场景下会被截断。
- 例：期望输出 512、`speculationGamma = 16`，则 `maxIterTimes ≥ 528`。

---

### 表 5：lookahead 补充参数 1 —— ModelDeployConfig 中的 ModelConfig 参数

| 配置项 | 取值类型 | 取值范围 | 配置说明 |
|---|---|---|---|
| plugin_params | std::string | plugin_type：la<br>level：[3, 16]<br>window：[1, 16]<br>guess_set_size：[1, 16] | plugin_type 配置 la，表示当前选择 lookahead 并行解码。<br>level/window/guess_set_size 为 lookahead 算法中的 N/W/G 参数，默认值为 4/5/5，且每个参数可配置的上限不超过 16。配置示例："{\"plugin_type\":\"la\",\"level\": 4,\"window\": 5,\"guess_set_size\": 5}" |

**逐行解读**：
- `plugin_type = la` 是 lookahead 开关。
- `level (N)` ∈ [3, 16]：Jacobi 迭代的深度/层数；默认 4。
- `window (W)` ∈ [1, 16]：每次 Jacobi 迭代向前看的窗口宽度；默认 5。
- `guess_set_size (G)` ∈ [1, 16]：从 Jacobi 迭代轨迹中挑选候选 token 的集合大小；默认 5。
- 三者上限均为 16，整体上限受 `speculationGamma ≥ (N-1)*(W+G)` 约束（见下）。

---

### 表 6：lookahead 补充参数 2 —— ModelDeployConfig 的参数

| 配置项 | 取值类型 | 取值范围 | 配置说明 |
|---|---|---|---|
| speculationGamma | uint32_t | 与 plugin 参数配置有关 | lookahead 中，配置值应 **大于等于 (N-1)*(W+G)**。<br>建议值：等于 (N-1)*(W+G)。 |

**逐行解读**：
- lookahead 中 `speculationGamma` 必须 **覆盖 Jacobi 迭代在 N-1 步中产生的窗口候选总数 (N-1)*(W+G)**，否则候选会被截断。
- 代入默认 N=4, W=5, G=5：最小 `speculationGamma = 3 * (5+5) = 30`——与正文 JSON 示例中 `speculationGamma: 30` 完全吻合。

---

## 【公式解读】

原文未给出显式 LaTeX 公式，但有三处关键约束关系（以伪代码形式逐字保留）：

**式 1（memory_decoding 推测窗口约束）**
$$
\text{speculationGamma} \geq \text{decoding\_length}
$$
- `speculationGamma`：主模型一次可验证的候选 token 数上限（uint32_t）。
- `decoding_length`：memory_decoding 算法一次产生的候选 token 最大长度，取值 [1, 16]。
- 作用：保证验证能力 ≥ 推测产出，避免候选被截断导致猜测浪费。

**式 2（lookahead 推测窗口约束）**
$$
\text{speculationGamma} \geq (N - 1) \times (W + G)
$$
- `N = level`：Jacobi 迭代深度/层数，取值 [3, 16]。
- `W = window`：每次迭代向前看的窗口宽度，取值 [1, 16]。
- `G = guess_set_size`：每次迭代可选的 guess set 大小，取值 [1, 16]。
- 作用：N-1 步 Jacobi 迭代累计可产出最多 (N-1)×(W+G) 个候选；`speculationGamma` 须 ≥ 此值才能完整覆盖。
- 默认 N=4, W=5, G=5 → 下界 30，与 JSON 示例中 `speculationGamma: 30` 一致。

**式 3（dynamic_algo 开启时的总迭代约束）**
$$
\text{maxIterTimes} \geq \text{期望输出长度} + \text{speculationGamma}
$$
- `maxIterTimes`：调度侧的总迭代次数上限（uint32_t）。
- `期望输出长度`：用户期望的最大生成长度。
- `speculationGamma`：见式 1/2。
- 作用：dynamic_algo=true 时，预留迭代次数必须足以容纳"完整生成 + 推测验证开销"，否则输出会被截断。例：期望输出 512、`speculationGamma=16` → `maxIterTimes ≥ 528`。

---

## 【关联】

- **上游特性约束（互斥/不可同开，原文"限制与约束"列出）**：PD 分离、Multi-LoRA、SplitFuse、长序列、MTP、异步调度、多机推理。意味着并行解码是一个 **独立的 decode 通路**，必须独占调度/内存管理路径。
- **量化路径**：仅与 W8A8 量化、稀疏量化兼容（其他量化暂不支持），说明该特性的算子实现对量化格式有特殊约束。
- **后处理能力限制**：与 n / best_of / use_beam_search / logprobs / top_logprobs 等 **多序列推理参数互斥**，也仅支持重复惩罚、不支持流式与 HealthCheck；说明并行解码当前定位是 **单序列、确定性、低开销** 的吞吐优化路径。
- **服务化参数联动**：原文将 plugin_params / speculationGamma / maxIterTimes 等都归到 `ModelDeployConfig` 与 `ScheduleConfig`，并显式指引读者参阅 [配置参数说明（服务化）](../user_manual/service_parameter_configuration.md) —— 表明并行解码并非独立子系统，而是 **嵌入到 MindIE 通用服务化参数体系** 中的可选插件。
- **算法内部关系**：lookahead 的 N/W/G 与 `speculationGamma` 强耦合，memory_decoding 的 `decoding_length` 与 `speculationGamma` 强耦合，调度侧 `maxIterTimes` 又在 dynamic_algo 路径下反向依赖 `speculationGamma`，形成 **算法层 → 部署层 → 调度层** 的三段式耦合链路。

---

## 【使用方法】

原文给出明确的 **配置 + 启动** 流程：

1. **编辑 Server 的 config.json**：
   - whl 包安装：`vi {MindIE安装目录}/mindie_llm/conf/config.json`
   - run 包安装：`vi {MindIE安装目录}/latest/mindie-service/conf/config.json`

2. **在 `ModelDeployConfig` 下按表 2~表 6 添加参数**（完整 JSON 示例原文已给出，逐字保留）：

   **memory_decoding 算法配置样例**：
   ```json
   "ModelDeployConfig" :
   {
       "maxSeqLen" : 2560,
       "maxInputTokenLen" : 2048,
       "truncation" : 0,
       "speculationGamma": 16,
       "ModelConfig" : [
           {
               "plugin_params":"{\"plugin_type\":\"memory_decoding\",\"decoding_length\":16,\"dynamic_algo\":true}",
               "modelInstanceType" : "Standard",
               "modelName" : "llama3-70b",
               "modelWeightPath" : "/data/weights/llama3-70b",
               "worldSize" : 4,
               "cpuMemSize" : 5,
               "npuMemSize" : -1,
               "backendType" : "atb",
               "trustRemoteCode" : false
           }
       ]
   }
   ```

   **lookahead 算法配置样例**：
   ```json
   "ModelDeployConfig" :
   {
       "maxSeqLen" : 2560,
       "maxInputTokenLen" : 2048,
       "truncation" : 0,
       "speculationGamma": 30,
       "ModelConfig" : [
           {
               "plugin_params":"{\"plugin_type\":\"la\",\"level\":4,\"window\":5,\"guess_set_size\":5}",
               "modelInstanceType" : "Standard",
               "modelName" : "Qwen2.5-7B-Instruct",
               "modelWeightPath" : "/data/weights/Qwen2.5-7B-Instruct",
               "worldSize" : 1,
               "cpuMemSize" : 5,
               "npuMemSize" : -1,
               "backendType" : "atb",
               "trustRemoteCode" : false
           }
       ]
   }
   ```

3. **启动服务**：
   - whl 包安装：`mindie_llm_server`
   - run 包安装：`./bin/mindieservice_daemon`

**关键配置要点（取自原文）**：
- 两算法**不可同时使能**（`plugin_type` 二选一）。
- memory_decoding：`plugin_type=memory_decoding`，`decoding_length ∈ [1,16]`（默认 16），`dynamic_algo` 默认 False；`speculationGamma ≥ decoding_length`。
- lookahead：`plugin_type=la`，`level ∈ [3,16]`、`window ∈ [1,16]`、`guess_set_size ∈ [1,16]`，默认 4/5/5；`speculationGamma ≥ (N-1)*(W+G)`。
- 若 `dynamic_algo=true`，还需在 `ScheduleConfig` 设置 `maxIterTimes ≥ 期望输出长度 + speculationGamma`。
- 完整服务化参数定义见 [配置参数说明（服务化）](../user_manual/service_parameter_configuration.md)。
