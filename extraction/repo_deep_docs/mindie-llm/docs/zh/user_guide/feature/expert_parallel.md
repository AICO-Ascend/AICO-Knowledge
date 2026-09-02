# Expert Parallel

> 仓 `mindie-llm` · 路径 `docs/zh/user_guide/feature/expert_parallel.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-llm/docs/zh/user_guide/feature/expert_parallel.md

# Expert Parallel 特性文档深度解读

## 【定位】

这篇文档描述的是 **mindie-llm 推理引擎中 MoE（Mixture of Experts）模型的专家并行（Expert Parallel, EP）能力**，详细说明了将不同专家部署到不同设备上实现专家级并行计算的两种实现方式（基于 AllGather 通信 vs 基于 AllToAll+通算融合）、适用模型、约束条件、配置参数及使用方法。

---

## 【技术要点】

1. **两种 EP 实现形式**：
   - `"ep_level": 1` — 基于 **AllGather 通信**的 EP 并行
   - `"ep_level": 2` — 基于 **AllToAll + 通算融合**的 EP 并行

2. **适用模型范围**：仅支持 **DeepSeek-V2、DeepSeek-V3、DeepSeek-R1** 三类模型。

3. **Grouped Matmul 自动使能条件**：当专家并行数 **超过 32** 时，**DeepSeek-V3、DeepSeek-R1 自动使能 Grouped MatMul 融合算子** 以提升计算性能。

4. **双机部署硬性约束**：当 `"ep_level"=2` 且为双机部署场景时，两台服务器 **必须通过交换机连接**，否则服务拉起失败。

5. **ep_level=1 长序列显存优化**：通过 `enable_init_routing_cutoff=true` + `topk_scaling_factor` 配合，对每台设备 hidden_states 的后段无效数据进行截断，以 **减小显存开销**。

6. **ep_level=2 buffer 精细管理**：通过 `alltoall_ep_buffer_scale_factors` 按序列长度分段配置 buffer 系数，实现显存精细化管理；该参数在 ep_level=1 时 **配置不生效**。

---

## 【关键机制与数据】

### 工作原理

- **ep_level=1（AllGather 方式）**：每台设备均保存所有专家的全量权重（或通过 AllGather 通信汇集所需专家），路由后每台设备的 hidden_states **后段部分为无效数据**（因 topk 截断），可通过 `topk_scaling_factor` 减小显存开销。
- **ep_level=2（AllToAll + 通算融合方式）**：专家分散部署在不同设备上，通过 AllToAll 通信将 token 路由到对应专家所在设备，并融合通信与计算过程；需配合 buffer 系数管理 AllToAll 通信 buffer 大小。

### 关键数据（原文）

- 原文：`"ep_level"=2` 时默认 buffer 系数样例 — `[[1048576, 1.32], [524288, 1.4], [262144, 1.53], [131072, 1.8], [32768, 3.0], [8192, 5.2], [0, 8.0]]`，按序列长度降序排列，序列长度越小对应 buffer 系数越大。
- 原文：`ep_level=1` 长序列场景示例使用 `topk_scaling_factor=0.25`，`maxSeqLen=66000`，`maxInputTokenLen=65000`。
- 原文：示例中 `worldSize=8`，`moe_ep=8`（专家并行度=8）。

---

## 【表格解读】

**表 1  Expert Parallel 特性补充参数：ModelConfig 中的 models 参数**（逐字还原）

| 配置项 | 取值类型 | 取值范围 | 配置说明 |
|---|---|---|---|
| deepseekv2 | | | |
| ep_level | int | [1,2] | 专家并行的实现形式。<br>1：表示基于 AllGather 通信的 EP 并行<br>2：表示基于 AllToAll 和通算融合的 EP 并行<br>双机部署场景下且 "ep_level" 设置为 "2" 时，两台服务器必须通过交换机连接，否则拉起服务会失败。 |
| enable_init_routing_cutoff | bool | true / false | 是否允许 topk 截断。<br>默认值：false（关闭）<br>"ep_level"="1" 时，可配置该参数。 |
| topk_scaling_factor | float | (0,1] | topk 截断参数。<br>"ep_level"="1" 时，每台设备的 hidden_states 后段部分为无效数据，可设置截断参数减小显存开销。<br>需同时配置 "enable_init_routing_cutoff"="true"。 |
| alltoall_ep_buffer_scale_factors | list[list[int, float]] | 列表每个成员包含两个数：第一个数为非负整数，第二个数为大于 0 的浮点数。排列顺序按照第一个数的大小降序排列。 | AllToAll 通信 buffer 大小，第二层 list 包含两个元素，第一个数为序列长度、第二个数为 buffer 系数。序列长度是判断 buffer 系数的选择条件。示例：<br>`[[1048576, 1.32], [524288, 1.4], [262144, 1.53], [131072, 1.8], [32768, 3.0], [8192, 5.2], [0, 8.0]]`<br>"ep_level"="2" 时，且用户需要精细化地管理显存的时候建议配置该项。<br>"ep_level"="1" 时该参数配置不生效。 |

**逐行解读**：

- **ep_level 行**：是 EP 特性的核心开关，取值 1 或 2 对应两种完全不同的通信与计算融合路径；特别注意双机部署时 ep_level=2 对硬件连接（交换机）的硬性要求，这是部署成败的硬约束。
- **enable_init_routing_cutoff 行**：仅在 ep_level=1 时可用的子开关，默认关闭；与 topk_scaling_factor 配合使用，构成"是否启用截断 + 截断比例"的组合控制。
- **topk_scaling_factor 行**：值域 (0,1]，典型用法为 0.25 等小数值；本质是对 hidden_states 后段无效部分的截断比例，依赖 enable_init_routing_cutoff=true 才生效。
- **alltoall_ep_buffer_scale_factors 行**：仅 ep_level=2 生效的精细化显存管理参数；按序列长度阈值降序排列，buffer 系数随序列长度减小而显著增大（如 0→8.0 vs 1048576→1.32），意味着短序列场景需要预留更大的 buffer 系数以容纳 AllToAll 通信 buffer。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **服务化参数配置**：文档明确指出"该特性需配合 MindIE Motor 使用"，并通过内部链接 `../user_manual/service_parameter_configuration.md` 关联到《配置参数说明（服务化）》章节，所有 EP 参数（如 `ep_level`、`moe_ep` 等）最终都需写入服务化 `config.json` 文件中。
- **MindIE Motor 启动流程**：通过外部链接 `https://gitcode.com/Ascend/MindIE-Motor/blob/dev/docs/zh/user_guide/quick_start.md` 关联到 MindIE Motor 的"快速入门 > 启动服务"章节，构成"参数配置 → 服务启动"的完整使用链路。
- **模型权重量化变体**：示例中使用的模型名为 `DeepSeek-R1_w8a8`（w8a8 量化），说明 EP 特性需与量化模型协同工作，但本文档未展开量化相关参数细节。
- **moe_ep 与 worldSize 关系**：示例中 `worldSize=8`、`moe_ep=8`，表明专家并行度可与张量并行等其他并行度组合（此处 worldSize 等于 moe_ep），但本文档未深入展开多并行维度的协同机制。

---

## 【使用方法】

### 启用方式

在服务化 `config.json` 文件的 `ModelConfig` 中通过 `models.deepseekv2` 字段配置相关参数。

### 配置项（ep_level=2 示例）

```json
"ModelDeployConfig": {
   "maxSeqLen": 2560,
   "maxInputTokenLen": 2048,
   "truncation": 0,
   "ModelConfig": [{
      "modelInstanceType": "Standard",
      "modelName": "DeepSeek-R1_w8a8",
      "modelWeightPath": "/data/weights/DeepSeek-R1_w8a8",
      "worldSize": 8,
      "cpuMemSize": 5,
      "npuMemSize": -1,
      "backendType": "atb",
      "trustRemoteCode": false,
      "moe_ep": 8,
      "models": {
          "deepseekv2": {
              "ep_level": 2,
              "alltoall_ep_buffer_scale_factors": [[1048576, 1.32], [524288, 1.4], [262144, 1.53], [131072, 1.8], [32768, 3.0], [8192, 5.2], [0, 8.0]]
          }
      }
   }]
}
```

### 配置项（ep_level=1 长序列示例）

```json
"ModelDeployConfig": {
   "maxSeqLen": 66000,
   "maxInputTokenLen": 65000,
   "truncation": 0,
   "ModelConfig": [{
      "modelInstanceType": "Standard",
      "modelName": "DeepSeek-R1_w8a8",
      "modelWeightPath": "/data/weights/DeepSeek-R1_w8a8",
      "worldSize": 8,
      "cpuMemSize": 5,
      "npuMemSize": -1,
      "backendType": "atb",
      "trustRemoteCode": false,
      "moe_ep": 8,
      "models": {
          "deepseekv2": {
              "ep_level": 1,
              "enable_init_routing_cutoff": true,
              "topk_scaling_factor": 0.25
          }
      }
   }]
}
```

### 关键命令 / 操作步骤

1. 配置服务化参数：在 `config.json` 中按本文档"参数说明"添加 EP 相关参数。
2. 启动服务：参考《MindIE Motor 开发指南》"快速入门 > 启动服务"章节拉起服务。

### 注意事项（原文 NOTE）

> 一般情况下不建议添加 `alltoall_ep_buffer_scale_factors`——即默认配置即可满足大多数场景，仅在需要精细化显存管理时才建议显式配置该参数。
