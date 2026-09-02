# 支持的推理引擎

> 仓 `mindie-motor` · 路径 `docs/zh/user_guide/features/supported_inference_engines.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-motor/docs/zh/user_guide/features/supported_inference_engines.md

# 「支持的推理引擎」feature 文档深度解读

---

## 【定位】

本文档描述 MindIE Motor 的推理引擎对接能力——即控制面（Controller/Coordinator）与数据面（推理引擎）解耦架构下，当前支持哪些底层推理引擎（vLLM、SGLang）以及如何通过 `engine_type` 进行选型与配置。

---

## 【技术要点】

1. **控制面/数据面解耦架构**：MindIE Motor 采用 Controller/Coordinator（控制面）与推理引擎（数据面）解耦的设计，可对接多种大模型推理引擎。
2. **支持的引擎清单**（原文表格）：vLLM（已支持，**推荐**）配合 `vllm-ascend` 使用；SGLang（已支持，POC）通过 `engine_type: sglang` 部署。
3. **引擎选型入口字段**：在 `user_config.json` 的 `motor_engine_prefill_config` / `motor_engine_decode_config`（混部场景使用 `motor_engine_union_config`）中通过 `engine_type` 字段选择底层引擎。
4. **参数映射机制**：`engine_config` 子字段与各引擎自身的启动命令参数一一对应，具体转换方法详见 [user_config 全量参数说明](../configuration/config_reference.md)。
5. **SGLang 适用场景**：在多轮对话、Agent 搜索、Few-shot 等依赖前缀复用的场景中，利用 RadixAttention 等机制可获得较好效果。
6. **SGLang PD 分离的 bootstrap 端口机制**：`engine_config.disaggregation_bootstrap_port`（同时兼容原生 CLI 风格 `disaggregation-bootstrap-port`）作为 Pod/NodeManager 维度的端口；NodeManager 将其作为 `bootstrap_port` 元数据注册，由 Coordinator 的 SGLang Adapter 用于 Prefill/Decode 对接；该端口与推理业务端口 `endpoint_config.service_ports` 是**不同端口**；未配置时不生成 bootstrap 元数据。

---

## 【关键机制与数据】

### 工作原理

- **架构分层**：控制面（Controller/Coordinator）负责调度/协调，数据面（vLLM/SGLang）负责实际推理，二者通过 `engine_type` 与 `engine_config` 解耦。
- **引擎选型路径**：`user_config.json` → `motor_engine_prefill_config`/`motor_engine_decode_config`/`motor_engine_union_config` → `engine_type`（取值 `"vllm"` 或 `"sglang"`）→ `engine_config`（透传至引擎启动命令）。
- **SGLang PD 分离数据流**：
  1. 用户在 `engine_config` 指定 `disaggregation_bootstrap_port`（或 CLI 风格 `disaggregation-bootstrap-port`）；
  2. NodeManager 把该端口包装为 `bootstrap_port` 元数据并注册；
  3. Coordinator 通过 SGLang Adapter 利用该元数据完成 Prefill/Decode 实例之间的对接；
  4. 该 bootstrap 端口独立于 `endpoint_config.service_ports` 中的推理业务端口；
  5. 若用户未配置 `disaggregation_bootstrap_port`，则不会生成 bootstrap 元数据（即不启用 PD 分离的握手通道）。

> 原文未提供具体的性能数据（如吞吐、时延、显存占用等数字）。

---

## 【表格解读】

**原文表格**（引擎一览）：

| 推理引擎 | 支持状态 | 说明 |
| --- | --- | --- |
| **vLLM** | 已支持（推荐） | 配合 `vllm-ascend` 使用；文档与示例最完整，为当前主推引擎。 |
| **SGLang** | 已支持（POC） | 可通过 `engine_type: sglang` 部署。部分高级能力与 vLLM 的覆盖范围可能不同，以对应特性文档与示例为准。 |

**逐行解读**：

- **vLLM 行**：状态为"已支持（推荐）"，意味着文档推荐用户优先选择此引擎；它依赖 `vllm-ascend`（即昇腾适配版的 vLLM）运行，并强调"文档与示例最完整"，暗示其在 MindIE Motor 中的集成度与可参考资料最高。
- **SGLang 行**：状态为"已支持（POC）"，表明仍处于概念验证阶段，能力覆盖"可能与 vLLM 不同"——这是一个**重要的选型提示**：如果用户依赖某些高级特性（如 RadixAttention 加速的前缀复用、Agent 搜索、Few-shot 等），需要查阅对应特性文档与示例确认该引擎在该场景下的覆盖度，避免假设能力等价。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **[user_config 全量参数说明（../configuration/config_reference.md）]**：本文档中两次引用——
  1. 第一次用于说明 `engine_type` 字段设置方式及其与 `motor_engine_prefill_config` / `motor_engine_decode_config` / `motor_engine_union_config` 的关系；
  2. 第二次用于解释 `engine_config` 与各引擎启动命令参数的转换方法（即 config_reference.md 给出 vLLM/SGLang CLI 参数与 JSON 字段之间的完整映射规则）。
  - 也就是说，本特性页是 `user_config.json` 中引擎相关字段的**概念性入口**，而 config_reference.md 才是字段级别的**权威参考**，二者构成"特性说明 → 参数详表"的下钻关系。
- **上游（本特性页是入口）**：被 MindIE Motor 的部署/特性文档树通过 `docs/zh/user_guide/features/` 路径汇聚，可视为推理引擎对接特性的"门面"文档。
- **下游（本文档指向）**：config_reference.md 给出完整参数表；各引擎自身的官方文档（vLLM-ascend、SGLang）通过 `vllm-ascend`、`engine_type` 等字眼间接触达。

---

## 【使用方法】

### 启用方式——vLLM

在 `user_config.json` 中设置：

```json
"motor_engine_prefill_config": {
  "engine_type": "vllm",
  "engine_config": {
    "served_model_name": "qwen3-8B",
    "model": "/mnt/weight/qwen3_8B",
    "tensor_parallel_size": 2,
    ...
  }
}
```

### 启用方式——SGLang

```json
"motor_engine_prefill_config": {
  "engine_type": "sglang",
  "engine_config": {
    "served-model-name": "qwen3-8B",
    "model-path": "/mnt/weight/Qwen3-8B",
    "tp-size": 2,
    ...
  }
}
```

### SGLang PD 分离的端口配置项

- 字段：`engine_config.disaggregation_bootstrap_port`
- 兼容写法：`disaggregation-bootstrap-port`（原生 CLI 风格）
- 作用域：Pod/NodeManager 维度
- 元数据名：注册为 `bootstrap_port`，由 Coordinator 的 SGLang Adapter 消费
- 注意：与 `endpoint_config.service_ports`（推理业务端口）**不是同一端口**
- 缺省行为：未配置该字段时**不生成 bootstrap 元数据**

> 其他配置项（如 `tensor_parallel_size` / `tp-size`、混部场景的 `motor_engine_union_config`、`endpoint_config.service_ports` 等）原文未做完整展开，详见 [user_config 全量参数说明](../configuration/config_reference.md)。
