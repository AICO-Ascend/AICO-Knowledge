# 思考解析

> 仓 `mindie-llm` · 路径 `docs/zh/user_guide/feature/enable_reasoning.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-llm/docs/zh/user_guide/feature/enable_reasoning.md

# 深度解读：mindie-llm 思考解析（enable_reasoning）特性文档

---

## 【定位】

本文档描述了 MindIE LLM 推理引擎中的**"思考解析"（Thinking Parsing）特性**——针对部分大模型输出结果中包含的"思考过程"，引擎对其进行结构化解析，将推理过程中产生的内部思维链（think）与最终对外的回答（content）分离，并分别写入 `reasoning_content` 与 `content` 两个独立字段，从而让下游应用能够区分并按需消费模型的中间推理过程与最终结论。

---

## 【技术要点】

1. **核心字段语义**：`reasoning_content` 存储模型在生成回答前的"推理、分析、逻辑判断"等内部思维过程；`content` 存储模型"最终对外输出"的回答或决策结果——两者一一对应同一请求，但用途明确隔离。

2. **硬件支持范围**：仅在 Atlas 800I A2 推理服务器、Atlas 800I A3 超节点服务器和 Atlas 300I Duo 推理卡上支持；其他硬件不在本文档承诺范围内。

3. **模型支持范围**：当前仅 Qwen3-32B、Qwen3-235B-A22B、Qwen3-30B-A3B、DeepSeek-R1 和 DeepSeek-V3.1 五款模型支持该特性。

4. **DeepSeek-V3.1 的特殊启用条件**：开启思考解析时需在请求体中传入 `"chat_template_kwargs": {"enable_thinking": <bool>}`，或在 tokenizer_config.json 中添加 `"enable_thinking": <bool>`——这是 V3.1 区别于其他支持模型的开关机制。

5. **接口约束**：当前仅支持 OpenAI 推理接口；其他推理接口（如 TGI、自定义协议）不在本文档涉及范围内。

6. **核心配置项**：在 Server 配置 `config.json` 的 `ModelDeployConfig.ModelConfig.models` 子字段中，按不同模型传入不同 key（`qwen3` / `qwen3_moe` / `deepseekv2` / `deepseek_v32`），并设置 `"enable_reasoning": true`，默认值为 `false`，**必填**。

---

## 【关键机制与数据】

**工作原理（原文机制还原）**：

- **解析目标**：模型在一次生成调用中，可能先输出一段内部思维链（reasoning），再输出面向用户的最终回答（content）。MindIE 在服务化层面对这两段文本做**结构化分离**，分别写入响应的两个字段，从而实现"思维链可观测但不影响对外内容消费"。
- **配置生效路径**：用户通过修改 Server 的 `config.json` 中 `ModelDeployConfig → ModelConfig[i] → models[<model_key>].enable_reasoning` 来开启该能力；启动服务后，引擎在响应 OpenAI 推理接口请求时即按此开关决定是否进行思考解析。
- **模型差异化 key 设计**：不同模型在 `models` 字典中使用不同的子键名——
  - Qwen3-32B / Qwen3-235B-A22B 使用 `"qwen3"`
  - Qwen3-30B-A3B 使用 `"qwen3_moe"`（因其为 MoE 架构）
  - DeepSeek-R1 使用 `"deepseekv2"`，且需将权重文件 `model_type` 改为 `"deepseek_v3"`
  - DeepSeek-V3.2 使用 `"deepseek_v32"`
- **DeepSeek-V3.1 的双重开关**：除 `enable_reasoning` 外，还需在请求层或 tokenizer 配置层显式传入 `enable_thinking`，二者协同控制。

> 原文未给出任何性能数据（如延迟、吞吐、显存占用等数值），本文档也不臆造。

---

## 【表格解读】

**表 1　思考解析特性补充参数：ModelConfig 中的 models 参数**

| 配置项 | 取值类型 | 取值范围 | 配置说明 |
|---|---|---|---|
| enable_reasoning | bool | true<br>false | 是否开启模型思考解析，将输出分别解析为"reasoning_content"和"content"两个字段。false：关闭<br>true：开启<br>必填，默认值：false。 |

**逐行解读**：

- **第一列（配置项）`enable_reasoning`**：该参数名直接对应该特性的开关，嵌入在 `ModelConfig.models[<model_key>]` 字典中（如示例 `"qwen3": {"enable_reasoning": true}`）。
- **第二列（取值类型）`bool`**：仅接受布尔值，不接受字符串（如 `"true"`）或整数（如 `1`）。
- **第三列（取值范围）`true` / `false`**：二选一，分别对应"开启"与"关闭"两个互斥状态。
- **第四列（配置说明）**：
  - **功能描述**：开启后引擎执行"将模型输出拆分为 `reasoning_content` + `content` 两个字段"的结构化解析动作；关闭时不做该分离。
  - **默认值**：`false`——即**默认关闭**，需要用户主动打开才能享受该能力。
  - **必填性**：**必填**——若不显式给出该字段，行为退化为默认关闭，但配置语义上仍要求用户主动声明。

---

## 【公式解读】

原文无公式。

---

## 【关联】

本文档中提及的上下游/关联模块与文档如下：

1. **配置参数总纲：[`../user_manual/service_parameter_configuration.md`](../user_manual/service_parameter_configuration.md)**
   - 本文档的"参数说明"小节明确指向该章节作为"服务化参数说明"的入口；`enable_reasoning` 仅是 `ModelConfig.models` 维度下**该特性专属**的补充参数，而 `ModelDeployConfig` 下的其他通用参数（`maxSeqLen=2560`、`maxInputTokenLen=2048`、`truncation=0`、`worldSize=1`、`cpuMemSize=0`、`npuMemSize=-1`、`backendType="atb"`、`trustRemoteCode=false`、`async_scheduler_wait_time=120`、`kv_trans_timeout=10`、`kv_link_timeout=1080` 等）均归属该总纲文档定义。

2. **客户端请求协议：《MindIE Motor 开发指南》 → "集群管理组件 > 调度器（Coordinator） > RESTful 接口 API > 用户侧接口 > OpenAI 推理接口"**
   - 文档第 4 步"发送请求"将请求参数说明指向该章节，意味着 `reasoning_content` 字段的接收、消费方式遵循 OpenAI 兼容接口协议，由 MindIE Motor 的 OpenAI 推理接口文档统一约定。

3. **底层硬件/驱动层**
   - 文档将特性可用性约束在 Atlas 800I A2 / 800I A3 / 300I Duo 三类昇腾硬件上，间接表明该特性的结构化解析能力与昇腾后端（`backendType: "atb"`）的模型执行栈紧耦合，并非跨硬件通用的纯文本层处理。

4. **模型仓库侧的协同**
   - 对 DeepSeek-R1 而言，启用该特性还需修改权重文件中的 `model_type` 字段——意味着该特性与**模型权重元数据**存在隐式契约（仅有 `enable_reasoning` 配置不足以生效）。
   - 对 DeepSeek-V3.1 而言，`enable_thinking` 必须出现在 `chat_template_kwargs` 或 `tokenizer_config.json` 中——意味着该特性与**模型 tokenizer/chat template** 存在协同依赖。

---

## 【使用方法】

**步骤 1：打开 Server 的 config.json**

- **whl 包安装方式**：
  ```bash
  cd {MindIE安装目录}/mindie_llm/
  vi conf/config.json
  ```
- **run 包安装方式**：
  ```bash
  cd {MindIE安装目录}/latest/mindie-service
  vi conf/config.json
  ```

**步骤 2：在 `ModelDeployConfig.ModelConfig.models` 中按模型添加 `enable_reasoning` 字段**

以 Qwen3-32B 为例的完整 JSON 配置（原文示例，含全部上下文参数）：

```json
 "ModelDeployConfig" :
        {
            "maxSeqLen" : 2560,
            "maxInputTokenLen" : 2048,
            "truncation" : 0,
            "ModelConfig" : [
                {
                    "modelInstanceType" : "Standard",
                    "modelName" : "Qwen3-32B",
                    "modelWeightPath" : "/data/weight/Qwen3-32B",
                    "worldSize" : 1,
                    "cpuMemSize" : 0,
                    "npuMemSize" : -1,
                    "backendType" : "atb",
                    "trustRemoteCode" : false,
                    "async_scheduler_wait_time": 120,
                    "kv_trans_timeout": 10,
                    "kv_link_timeout": 1080,
                    "models": {
                            "qwen3": {"enable_reasoning": true}
                    }
                }
            ]
        },
```

**步骤 3：模型差异化配置（按模型替换 `models` 的 key，原文 NOTE 摘录）**

| 模型 | `models` 子键名 | 额外要求 |
|---|---|---|
| Qwen3-32B / Qwen3-235B-A22B | `"qwen3"` | 无 |
| Qwen3-30B-A3B | `"qwen3_moe"`（将 `qwen3` 改为 `qwen3_moe`） | 无 |
| DeepSeek-R1 | `"deepseekv2"`（将 `qwen3` 改为 `deepseekv2`） | 将 DeepSeek-R1 权重文件中 `model_type` 字段修改为 `"deepseek_v3"` |
| DeepSeek-V3.2 | `"deepseek_v32"`（将 `qwen3` 改为 `deepseek_v32`） | 无 |

> 原文 NOTE 中**未单独列出 Qwen3-235B-A22B 的 key 替换说明**——按 NOTE 与示例的对应逻辑，Qwen3-235B-A22B 沿用 `"qwen3"`（与 Qwen3-32B 同列）；但原文未对此差异作显式声明。

**步骤 4：启动服务**

- **whl 包安装方式**：
  ```bash
  mindie_llm_server
  ```
- **run 包安装方式**：
  ```bash
  ./bin/mindieservice_daemon
  ```

**步骤 5：发送请求并消费字段**

请求参数说明详见《MindIE Motor 开发指南》→"集群管理组件 > 调度器（Coordinator） > RESTful 接口 API > 用户侧接口 > **OpenAI 推理接口**"章节。响应中将出现 `reasoning_content`（思维过程）与 `content`（最终回答）两个字段。

**步骤 6（仅 DeepSeek-V3.1）：额外注入 `enable_thinking`**

- 方式 A（请求级）：在请求体中传入 `"chat_template_kwargs": {"enable_thinking": <bool>}`
- 方式 B（配置级）：在 `tokenizer_config.json` 中添加 `"enable_thinking": <bool>`

> 原文未涉及具体的 `<bool>` 取值建议（何时填 `true` / `false`）、未涉及回滚/关闭该特性的操作步骤、未提供验证 `reasoning_content` 字段已正确返回的样例响应。
