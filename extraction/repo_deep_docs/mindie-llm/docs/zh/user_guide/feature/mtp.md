# MTP

> 仓 `mindie-llm` · 路径 `docs/zh/user_guide/feature/mtp.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-llm/docs/zh/user_guide/feature/mtp.md

# MTP 特性文档深度解读

## 【定位】

这篇文档描述 MindIE LLM 推理引擎中 **MTP（Multi-Token Prediction，多 Token 预测）** 这一并行解码特性的**能力定义、参数配置、特性叠加兼容性、限制约束以及服务化启用步骤**，核心目的是指导用户在 DeepSeek-R1/V3 系列模型上开启 MTP 加速并正确配置相关参数。

---

## 【技术要点】

1. **核心机制**：MTP 是源自 DeepSeek 的并行解码方法，模型在推理时不仅预测下一个 token，还会同时预测后续多个 token，从而显著提升生成速度。
2. **开关参数**：通过 `ModelDeployConfig.ModelConfig[*].plugin_params` 字段启用，配置格式为 JSON 字符串，关键键包括 `plugin_type`（固定为 `"mtp"`）与 `num_speculative_tokens`（取值 1 或 2）。
3. **场景化配置建议**：低时延场景可配置 `num_speculative_tokens` 为 1 或 2；高吞吐场景建议不超过 1。
4. **完整支持叠加**：prefix cache 与 kvcache 池化、异步调度、kv_cache_int8 量化、function call、思考解析、PD 分离（P/D 节点需同时配置）。
5. **部分场景叠加**：context_parallel、sequence_parallel（在 PD 混部叠加时仅 `num_speculative_tokens=1`；大 EP 场景叠加时仅 P 节点可开启）。
6. **硬性互斥**：不能与并行解码、Multi-LoRA、SplitFuse 同时使用；多序列后处理参数（`n`、`best_of`、`use_beam_search`、`logprobs`）暂不支持；惩罚类后处理仅支持重复惩罚。

---

## 【关键机制与数据】

**工作原理（原文描述）**：
> "MTP 并行解码的核心思想是在推理过程中，模型不仅预测下一个 token，而且会同时预测多个 token，从而显著提升模型生成速度。"

即通过一次前向计算额外预测后续 token，再经由验证/采纳机制获得多个输出 token，从而摊薄单步解码开销。文档未给出实测加速比、吞吐数据或时延数字，因此不作臆造。

**模型与硬件适配数据（原文罗列）**：
- 适用硬件：Atlas 800I A2 推理服务器、Atlas 800I A3 超节点服务器
- 适用模型：DeepSeek-R1、DeepSeek-V3 的 W8A8 量化模型；上述模型的 KV Cache int8 量化模型
- 量化支持：W4A8 量化

---

## 【表格解读】

**原文表 1：MTP 特性补充参数——ModelDeployConfig 中的 ModelConfig 参数**

| 配置项 | 取值类型 | 取值范围 | 配置说明 |
|---|---|---|---|
| `plugin_params` | `std::string` | `plugin_type: mtp`<br>`num_speculative_tokens: [1]` | <ul><li>**plugin_type** 设置为 "mtp"，表示选择 mtp 特性。</li><li>**num_speculative_tokens** 表示 MTP 的层数，可设置为 1 或 2。</li><li>不需要生效任何插件功能时，请删除该配置项字段。</li></ul><br>配置示例：`{"plugin_type":"mtp","num_speculative_tokens": 1}`<br>【注】`num_speculative_tokens` 配置建议：对于低时延场景，可配置使用 1 或 2，对于高吞吐场景，建议配置不超过 1 |

**逐行解读**：
- **配置项**：`plugin_params`——MTP 特性的入口开关，挂载在 `ModelConfig` 数组元素的字段上。
- **取值类型**：`std::string`，表示该字段是一个字符串，但内部承载的是 JSON 结构化数据，而非裸字符串标记。
- **取值范围**：`plugin_type` 必须为 `"mtp"`；`num_speculative_tokens` 文档列出的取值范围写为 `[1]`，但正文明确说明"可设置为 1 或 2"，两者存在表头与正文描述不完全一致的情况，实际生效范围应以正文为准。
- **配置说明**：
  - `plugin_type="mtp"` 为启用开关；
  - `num_speculative_tokens` 控制 MTP 的层数（即一次额外预测多少个后续 token）；
  - 不使用插件功能时应**整段删除** `plugin_params` 字段，而非置空；
  - 末尾的"建议"明确给出时延敏感与吞吐敏感两种场景的最优取值，体现 trade-off：层数越多单次预测越多（对低时延有利），但同时也会增加验证/计算成本（高吞吐场景下层数过多会拖累）。

---

## 【公式解读】

原文无公式。

---

## 【关联】

文档中明确涉及的内部链接与上下游关系：

- **../user_manual/service_parameter_configuration.md**：文档在"执行推理"步骤中明确指引用户参考该章节以了解 `config.json` 中所有服务化参数的完整含义，说明 MTP 的启用需要与整体服务化参数协同配置（如 `maxSeqLen`、`maxInputTokenLen`、`worldSize`、`backendType` 等），MTP 是嵌入在通用服务化配置框架内的一个 plugin 扩展点。
- **特性叠加关系**：MTP 与 prefix cache、kvcache 池化、异步调度、kv_cache_int8 量化、function call、思考解析、PD 分离同属可叠加特性；与并行解码、Multi-LoRA、SplitFuse 为互斥关系；与 context_parallel、sequence_parallel 为条件叠加关系。
- **模型/硬件依赖**：MTP 强绑定 DeepSeek-R1/V3 量化路径与 Atlas 800I A2/A3 硬件平台，属于 MindIE LLM 推理栈中**模型层 + 加速库层**的协同特性。

---

## 【使用方法】

1. **编辑 Server 配置文件** `conf/config.json`：
   - whl 包安装：`cd {MindIE安装目录}/mindie_llm/ && vi conf/config.json`
   - run 包安装：`cd {MindIE安装目录}/latest/mindie-service && vi conf/config.json`

2. **在 `ModelDeployConfig.ModelConfig` 数组中添加 `plugin_params` 字段**，示例配置（原文给出）：

   ```json
   "ModelDeployConfig" :
   {
      "maxSeqLen" : 2560,
      "maxInputTokenLen" : 2048,
      "truncation" : 0,
      "ModelConfig" : [
        {
            "plugin_params": "{\"plugin_type\":\"mtp\",\"num_speculative_tokens\": 1}",
            "modelInstanceType" : "Standard",
            "modelName" : "DeepSeek-R1_w8a8",
            "modelWeightPath" : "/data/weights/DeepSeek-R1_w8a8",
            "worldSize" : 8,
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

> 注：完整 `config.json` 服务化字段含义参见 [`../user_manual/service_parameter_configuration.md`](../user_manual/service_parameter_configuration.md)。
