# Micro Batch

> 仓 `mindie-llm` · 路径 `docs/zh/user_guide/feature/micro_batch.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-llm/docs/zh/user_guide/feature/micro_batch.md

# Micro Batch 文档深度解读

## 【定位】

这篇文档描述了 MindIE-LLM 中的 **Micro Batch（微批次）特性**：在 Prefill 阶段的批处理过程中，将一批数据拆分为两个更小粒度的子 batch，分别跑在两条数据流上，让其中一条做计算、另一条做通信，从而掩盖通信耗时、提高推理吞吐。

---

## 【技术要点】

1. **双流拆分机制**：在原有数据流之外额外创建一条数据流，把一个 batch 切成两个 batch，分别在两条流上执行；流 1 计算时流 2 通信，流 1 通信时流 2 计算（原文："通过额外创建一条数据流，将一批数据分成两个batch在两条数据流上执行"）。
2. **Event 同步防冲突**：两条流通过 Event 机制进行同步，"计算和通信任务间都相互不冲突，防止硬件资源抢占"。
3. **聚焦 Prefill 阶段**：因为 Prefill 阶段通信类算子耗时较长、且"通信类算子与计算类算子耗时占比更为均衡"，掩盖收益最明显；Decode 阶段并非该特性的主要应用场景（原文未给出明确的非 Prefill 数据，按原文保守表述）。
4. **掩盖率指标**：原文声称"在此实现下，计算和通信类算子掩盖率达 70%+"。
5. **显存代价与吞吐权衡**：开启后会带来额外显存占用，"服务化场景下，KV Cache 数量下降会影响调度导致吞吐降低"，因此显存受限的场景不建议开启。
6. **互斥与兼容性约束**：默认关闭；不能与"通信计算融合算子特性"同时开启；仅 Qwen2.5、Qwen3 稠密、DeepSeek-R1、DeepSeek-V3.1 支持。

---

## 【关键机制与数据】

**工作原理（原文：）**

> "通过额外创建一条数据流，将一批数据分成两个batch在两条数据流上执行。数据流1在执行计算时，数据流2可进行通信，计算和通信耗时被掩盖，使得硬件资源得以充分利用，以提高推理吞吐。"
> "数据流间通过Event机制进行同步，计算和通信任务间都相互不冲突，防止硬件资源抢占。"

**应用场景选择（原文：）**

> "此特性通常应用在Prefill阶段，因为Prefill阶段通信类算子耗时较长，且通信类算子与计算类算子耗时占比更为均衡。"

**性能数据（原文：）**

> "在此实现下，计算和通信类算子掩盖率达70%+。"

（原文未提供绝对吞吐提升百分比、不同模型/序列长度下的对照数据等其它量化指标；KV Cache 下降导致吞吐降低属于定性说明，无具体数值。）

---

## 【表格解读】

**表 1　Micro Batch特性补充参数：ModelConfig中的models参数**

| 配置项 | 取值类型 | 取值范围 | 配置说明 |
| --- | --- | --- | --- |
| stream_options | - | - | - |
| micro_batch | bool | <ul><li>true</li><li>false</li></ul> | 开启通信计算双流掩盖特性。<br>默认值：false（关闭） |

**逐行解读：**

- **stream_options 行**：作为 micro_batch 的父级配置容器，`取值类型`、`取值范围`、`配置说明` 三列在原文中均为 `-`（占位），表示它本身不需要单独赋值的标量字段，只是一个嵌套结构，用于承载后续子项（这里是 micro_batch）。它在 JSON 中以对象形式出现，作为模型配置 `models` 下的子层（参考后文配置示例：`"stream_options": { "micro_batch": true }`）。
- **micro_batch 行**：
  - `取值类型` 为 `bool`，即只能填布尔值。
  - `取值范围` 列出 `true` 与 `false` 两个选项。
  - `配置说明` 明确语义："开启通信计算双流掩盖特性"，并给出**默认值：false（关闭）**，与原文"此特性不默认开启"一致。注意表格里的字段实际位于 `ModelConfig.models` 路径下，文档正文示例也确认了 `models → qwen3 → stream_options → micro_batch` 的嵌套层级。

---

## 【公式解读】

原文无公式。（全文为机制描述、参数表与配置示例，没有数学公式或伪代码形式表达式。）

---

## 【关联】

**与其它特性的关系（原文：）**

- **互斥特性**："通信计算融合算子特性"——两者不能同时开启，因为二者都试图优化"计算-通信"关系，机制上会互相冲突。
- **Qwen 模型可叠加的特性**：并行解码、异步调度、SplitFuse、PrefixCache。
- **DeepSeek 模型可叠加的特性**：MTP（Multi-Token Prediction）。
- **受限模型范围**：仅 Qwen2.5 系列、Qwen3 稠密系列、DeepSeek-R1、DeepSeek-V3.1 支持此特性。

**模块/上下游关系：**

- 该特性在 `ModelConfig` → `models` → `<model_name>`（如 `qwen3`）→ `stream_options.micro_batch` 层级启用，作用于推理引擎内部的 Prefill 调度路径。
- 与 `ccl.enable_mc2`（配置示例中出现在同级 `ccl` 节点下）同属 `models.<model_name>` 下的并行/通信优化子配置，但二者功能不同（mc2 控制集合通信算法是否启用 MC2），非互斥。
- 文档末尾给出的内部链接 `../user_manual/service_parameter_configuration.md`（即"配置参数说明（服务化）"章节）负责解释服务化场景下 `ModelDeployConfig` 等上层字段（`maxSeqLen`、`maxInputTokenLen`、`worldSize`、`cpuMemSize`、`npuMemSize`、`backendType` 等）的含义，Micro Batch 文档中对这些字段仅做引用，不重复定义。
- 由于开启会减少可用 KV Cache 数量并影响调度，关联到服务化层调度器（文档未点名具体模块），因此显存受限场景被建议关闭。

---

## 【使用方法】

**启用方式（原文：）**

1. 编辑 Server 的 `config.json`：
   - **whl 包安装**：`vi {MindIE安装目录}/mindie_llm/conf/config.json`
   - **run 包安装**：`vi {MindIE安装目录}/latest/mindie-service/conf/config.json`
2. 在 `ModelDeployConfig.ModelConfig[].models.<model_name>` 下添加 `stream_options.micro_batch` 字段并置为 `true`（默认 `false`）。原文配置示例（节选）：
   ```json
   "ModelConfig" : [
     {
         "modelInstanceType" : "Standard",
         "modelName" : "Qwen3-14B",
         "modelWeightPath" : "/data/weights/Qwen3-14B",
         "worldSize" : 8,
         "cpuMemSize" : 5,
         "npuMemSize" : -1,
         "backendType" : "atb",
         "trustRemoteCode" : false,
         "models": {
            "qwen3": {
                "ccl": {
                    "enable_mc2": false,
                },
                "stream_options": {
                    "micro_batch": true,
                }
            }
         }
      }
   ]
   ```
   其中加粗部分即为本次新增的 micro_batch 配置；`maxSeqLen`、`maxInputTokenLen`、`truncation`、`worldSize`、`cpuMemSize`、`npuMemSize`、`backendType` 等服务化字段的详细含义见 `../user_manual/service_parameter_configuration.md`。
3. 启动服务：
   - **whl 包安装**：`mindie_llm_server`
   - **run 包安装**：`./bin/mindieservice_daemon`

**配置项（原文：）**——仅一项开关：`models.<model_name>.stream_options.micro_batch`，类型 `bool`，取值 `true` / `false`，默认 `false`。

**关闭方式（原文：）**——将该字段改回 `false`，或直接删除该字段（默认即关闭）。

**注意事项（原文：）**

- 不与"通信计算融合算子特性"同时开启。
- 仅 Qwen2.5、Qwen3 稠密、DeepSeek-R1、DeepSeek-V3.1 支持；其它模型配置该字段无效（原文未明确报错行为）。
- 显存受限场景不建议开启。

## 图文联合解读

- `micro_batch.png`: **图文联合解读：**

图中展示两条并行数据流（Stream 1 / Stream 2）分别执行 micro batch 1 和 micro batch 2，每个 batch 内部按"计算→通信"交替进行，且两流的计算与通信时段错峰重叠——Stream 1 计算时 Stream 2 通信，反之亦然。

该图论证了 Micro Batch 通过双流错峰调度实现计算与通信耗时相互掩盖的机制，与文档"计算和通信类算子掩盖率达70%+"以及"数据流间通过 Event 机制同步"的论点形成直观印证，说明 Prefill 阶段双流并行可显著提升推理吞吐。
