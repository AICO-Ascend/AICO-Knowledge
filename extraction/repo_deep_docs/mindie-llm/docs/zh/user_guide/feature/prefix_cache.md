# Prefix Cache

> 仓 `mindie-llm` · 路径 `docs/zh/user_guide/feature/prefix_cache.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-llm/docs/zh/user_guide/feature/prefix_cache.md

# Prefix Cache 特性文档深度解读

## 【定位】

本文档描述了 mindie-llm（昇腾自研大模型推理引擎）中 **Prefix Cache 特性**——通过哈希表保留 session 结束后的 KV Cache，使新 session 请求能够复用跨 session 的公共前缀 Token 对应的 KV Cache，从而缩短 prefill 时间并提升显存利用率的跨请求缓存复用能力。

---

## 【技术要点】

1. **核心机制——哈希表 KV Cache 复用**：session 结束后其 KV Cache 被保留在哈希表中；新 session 请求在哈希表中查找是否存在相同的 Token 序列，命中后即可复用之前计算好的 KV Cache，实现跨 session 复用。
2. **复用粒度——Block 单位**：Prefix Cache 以 **blocksize 的倍数** 储存 KV Cache，只有跨 session 公共前缀 Token 数 **≥ block size** 时才会进行 KV Cache 复用。原文示例中第一轮 prompt token 数为 164、blocksize 为 128，实际复用部分只有前 128 token。
3. **两大优势**：
   - **更短的 prefill 时间**：减少公共前缀 Token 的 KV Cache 计算时间。
   - **更高效的显存使用**：正在处理的 sessions 间存在公共前缀时，公共前缀部分的 KV Cache 可共用，不必重复占用多份显存。
4. **硬件与模型支持**：仅 Atlas 800I A2 推理服务器、Atlas 300I Duo 推理卡、Atlas 800I A3 超节点服务器支持；模型支持 Qwen2 系列、Qwen2.5 系列、Qwen3 系列、DeepSeek-R1、DeepSeek-V3/V3.1。
5. **量化兼容性**：支持的量化特性包括 **W4A8 量化、W8A8 量化、PDMIX 量化、稀疏量化** 以及 **C8 量化**（在可叠加清单中）；其他量化特性不支持。
6. **可叠加特性**：可与 **PD 分离、并行解码、MTP、kvcache 池化、异步调度、SplitFuse、context parallel + sequence parallel、C8 量化** 同时使用；但 **不能与 Multi-LoRA 同时使用**，且 **不支持 prefix cache + context parallel + sequence parallel + function call(multiturn) 叠加**，**不支持 prefix cache + splitfuse + 数据并行叠加**。

---

## 【关键机制与数据】

- **工作原理（原文）**：Prefix Cache 通过哈希表保留 session 结束后的 KV Cache，新的 session 请求在哈希表中查找是否存在相同的 Token 序列，即可复用之前计算好的 KV Cache，从而实现跨 session 的 KV Cache 复用。
- **PD 分离场景约束（原文）**：PD 分离场景下，仅 P 节点需要开启该特性。
- **复用边界（原文）**：由于 cache 实现以 block 为单位，Prefix Cache 以 blocksize 的倍数储存；如第一轮问题 prompt 的 token 数量为 164，当 blocksize 为 128 时，实际复用部分只有前 128 token。
- **常见使用场景（原文）**：多轮对话和 few-shot 学习等。
- **使用建议（原文）**：前缀复用率低或者没有复用的情况下，不建议开启该特性。
- **性能数据**：原文未提供具体性能数据（如加速比、显存节省比例等）。

---

## 【表格解读】

### 表 1：ModelDeployConfig 中的 ModelConfig 参数

|配置项|取值类型|取值范围|配置说明|
|--|--|--|--|
|plugin_params|std::string|`"{\"plugin_type\":\"prefix_cache\"}"`|设置为 `"{\"plugin_type\":\"prefix_cache\"}"` 表示执行 Prefix Cache；不需要生效任何插件功能时，请删除该配置项字段。|

**逐行解读**：
- **配置项 plugin_params**：核心开关。通过在 `ModelConfig` 数组的某个 model 实例下设置此字段，启用 Prefix Cache 插件。
- **取值类型 std::string**：以 JSON 字符串形式传入插件类型。
- **取值范围**：`"{\"plugin_type\":\"prefix_cache\"}"`——必须填写的固定字符串。**叠加使用时**需用英文逗号分隔特性名称，例如 `"plugin_type":"mtp,prefix_cache"`，并附带 `"num_speculative_tokens": 1`（MTP 的 speculative tokens 数量）。
- **配置说明**：删除该字段则不启用任何插件功能。

### 表 2：ScheduleConfig 的参数

|配置项|取值类型|取值范围|配置说明|
|--|--|--|--|
|enablePrefixCache|-|-|该字段已无需配置，目前版本按老版本方式配置无影响。<br>该字段预计下线时间：2026 年 Q1 版本。|

**逐行解读**：
- **enablePrefixCache**：旧版本中 ScheduleConfig 下用于启用 Prefix Cache 的字段，**当前版本无需再配置**，保留旧配置无副作用但预计 2026 Q1 下线。

### 表 3：ModelConfig 中的 models 参数

|配置项|取值类型|取值范围|配置说明|
|--|--|--|--|
|**deepseekv2**|-|-|-|
|**kv_cache_option**|-|-|-|
|enable_nz|bool|<ul><li>true</li><li>false</li></ul>|是否开启 KV Cache NZ 格式。<br><ul><li>仅 DeepSeek-R1、DeepSeek-V3 和 DeepSeek-V3.1 模型支持此特性。FA3 量化场景下自动使能 NZ 格式。</li><li>DeepSeek-R1、DeepSeek-V3 和 DeepSeek-V3.1 模型**必须开启**此开关，其余模型关闭。</li><li>默认值：false</li></ul>|

**逐行解读**：
- **嵌套层级**：在 `models.deepseekv2.kv_cache_options` 路径下配置。
- **enable_nz**：控制 KV Cache 是否采用 NZ 格式（昇腾 NPU 上的特定张量排布格式）。
  - 取值 `true` / `false`，默认 `false`。
  - 仅 DeepSeek-R1 / DeepSeek-V3 / DeepSeek-V3.1 支持；FA3 量化场景会自动使能。
  - DeepSeek-R1 / DeepSeek-V3 / DeepSeek-V3.1 必须开启；其他模型必须关闭。
  - 原文示例配置 `{"enable_nz": true}` 即对应 DeepSeek-R1 模型必开要求。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **服务化参数配置总册**：文中多次指向 `../user_manual/service_parameter_configuration.md`（即《配置参数说明（服务化）》章节），该章节是 `config.json` 中 `ModelDeployConfig`、`ModelConfig`、`models`、`ScheduleConfig` 等完整字段定义与默认值的权威来源；本文档的表 1~表 3 仅列出 Prefix Cache 相关的补充参数。
- **可叠加特性生态**（按文中列举）：
  - **PD 分离**（Prefill-Decode 分离）—— Prefix Cache 仅在 P 节点开启。
  - **并行解码**（推测解码）、**MTP**（Multi-Token Prediction，通过 `num_speculative_tokens` 参数配合 plugin_type 叠加）。
  - **kvcache 池化**、**异步调度**、**SplitFuse**、**context parallel + sequence parallel**。
  - **C8 量化**——可叠加使用。
- **互斥/不叠加特性**：**Multi-LoRA**（完全互斥）、**function call(multiturn)** 与 CP+SP 同时叠加时不支持、**数据并行**与 SplitFuse 同时使用时不支持。
- **量化分支**：W4A8 / W8A8 / PDMIX / 稀疏量化均属 Prefix Cache 支持的量化路径；C8 量化路径独立列出在叠加清单中。

---

## 【使用方法】

### 启用步骤（原文）

**1）修改 Server 的 `config.json`**：
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

**2）在 `ModelDeployConfig.ModelConfig` 下添加 Prefix Cache 相关参数**（DeepSeek-R1 模型、只开启 Prefix Cache 特性的示例）：
```json
"ModelDeployConfig" :
{
   "maxSeqLen" : 2560,
   "maxInputTokenLen" : 2048,
   "truncation" : 0,
   "ModelConfig" : [
     {
         "plugin_params": "{\"plugin_type\":\"prefix_cache\"}",
         "modelInstanceType" : "Standard",
         "modelName" : "DeepSeek-R1_w8a8",
         "modelWeightPath" : "/data/weights/DeepSeek-R1_w8a8",
         "worldSize" : 8,
         "cpuMemSize" : 5,
         "npuMemSize" : -1,
         "backendType" : "atb",
         "trustRemoteCode" : false,
         "models": {
             "deepseekv2": {
                 "kv_cache_options": {"enable_nz": true}
             }
         }
     }
   ]
}
```

**特性叠加写法示例**（Prefix Cache + MTP）：
```json
"plugin_params": "{\"plugin_type\":\"mtp,prefix_cache\",\"num_speculative_tokens\": 1}"
```

**3）启动服务**：
- whl 包安装方式：
  ```bash
  mindie_llm_server
  ```
- run 包安装方式：
  ```bash
  ./bin/mindieservice_daemon
  ```

**4）发送请求验证**——通过 HTTPS 在 `https://127.0.0.1:1025/generate` 端点使用 `curl` 发起两轮请求：
- 第一次请求 prompt 为第一轮问题（如带 4 选项的多选题）。
- 第二次请求 prompt 为「第一轮问题 + 第一轮答案 + 第二轮问题」，第一轮问题即作为可复用的公共前缀。
- 请求均带 `Content-Type: application/json`、`--cacert ca.pem --cert client.pem --key client.key.pem` 进行 TLS 认证；`parameters` 中设置 `"max_new_tokens": 512`。
