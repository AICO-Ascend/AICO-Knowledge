# MindSpeed-MM 推理框架使用指南

> 仓 `mindspeed-mm` · 路径 `docs/zh/guides/development/inference_guide.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-mm/docs/zh/guides/development/inference_guide.md

# MindSpeed-MM 推理框架使用指南 深度解读

---

## 【定位】

这篇文档系统描述了 MindSpeed-MM 基于 **PyTorch FSDP2 后端**的推理框架使用方式,涵盖以 Qwen3.5 MoE 为示例的完整推理流程(数据准备 → 启动脚本 → YAML 配置 → 启动推理 → 输出解读)、当前已适配模型范围,以及**新增模型接入推理框架的标准适配流程**(适配器继承、注册、字段绑定)。

---

## 【技术要点】

### 1. 后端架构与并行策略
- 推理框架基于 **PyTorch FSDP2 后端**,采用 `fully_shard_parallel_size: auto` 自动决定 FSDP 切分组大小。
- 通过 `fsdp_plan` 显式指定需要分片/hook 的子模块(如 `model.visual`、`model.language_model.layers.{*}.mlp.experts`、`lm_head`、`mtp` 等),`param_dtype=bf16`、`reduce_dtype=fp32`、`reshard_after_forward=true`、`num_to_forward_prefetch=1`、`cpu_offload=false`。
- MoE 部分通过 `expert_parallel_size: 1` + `ep_plan` + `dispatcher: alltoall` 实现专家并行,`use_grouped_expert_matmul: true` 启用分组 expert matmul。

### 2. 环境变量(Ascend 专用)
启动脚本中显式 export 了一组关键环境变量:
- `NON_MEGATRON=true`
- `MULTI_STREAM_MEMORY_REUSE=2`
- `TASK_QUEUE_ENABLE=2`
- `ASCEND_LAUNCH_BLOCKING=0`
- `ACLNN_CACHE_LIMIT=100000`
- `CPU_AFFINITY_CONF=1`
- `PYTORCH_NPU_ALLOC_CONF=expandable_segments:True`

并在运行前需 `source /usr/local/Ascend/cann/set_env.sh`。

### 3. 启动方式
- 使用 `torchrun` 启动 `mindspeed_mm/fsdp/inference/inference_runner.py`,以 `NPUS_PER_NODE=8`、`NNODES=1` 为单机多卡示例,日志通过 `tee` 写入 `logs/infer_<日期>_<时间>.log`。
- 在仓库根目录执行 `bash examples/qwen3_5/qwen3_5_moe_inference.sh`。

### 4. 配置三段结构
配置文件划分为三大段:
- `parallel`(并行策略:`fsdp_plan`、`ulysses_parallel_size`、`expert_parallel_size`、`ep_plan`)
- `model`(模型属性:`model_id`、`model_name_or_path`、`attn_implementation=flash_attention_2`、`gdn_implementation=eager`、`causal_conv1d_implementation=eager`)
- `inference`(推理控制:`load`、`load_format`、`seed=42`、`init_model_with_meta_device=true`、`adapter=qwen3_5_moe`、`processor_path`、`enable_thinking=false`、`data_path`、`generation`、`plugin`)

### 5. 生成参数
`generation` 子字段含:`max_new_tokens=256`、`do_sample=false`、`repetition_penalty=1.0`、`use_cache=true`(贪心解码,最大 256 token,关闭重复惩罚)。

### 6. 模型适配(ModelAdapter 模式)
新增适配器需:
- 在 `mindspeed_mm/fsdp/inference/adapters/<adapter_name>.py` 继承 `ModelAdapter`,实现 `preprocess`(必须返回 `input_ids`)、`generate`(多 rank 同步)、`decode`(剥离 prompt token)三个方法。
- 在 `adapters/__init__.py` 中导入类并写入 `MODEL_ADAPTERS` 字典(`key` 与 YAML 的 `inference.adapter` 对应)。

---

## 【关键机制与数据】

### 推理框架工作流(原文 mermaid 时序图所示)
1. `User` 读取 YAML 并启动 `InferenceRunner`;
2. `Runner` 导入 `plugin`,向 `ModelHub` 请求 `build(model, features, training)` 得到模型实例;
3. `Runner` 通过 `ParallelApplier` 应用切分计划(FSDP2 分片 + 专家并行);
4. `Checkpointer` 按 `load_format`(HF/DCP/auto)向 FSDP2 模型写入权重;
5. 对每个输入样本:调用 `Adapter.preprocess(messages)` → `Model.generate(**inputs, **generation)` → `Adapter.decode(inputs, outputs)`;
6. 最终在 rank 0 输出文本、耗时与速度统计。

### 原文实测性能数据(基于 Qwen3.5 MoE 推理 3 个样本)

| 样本 | 输入 token | 输出 token | 耗时(s) | 速率(tokens/s) |
|---|---|---|---|---|
| 文本(自我介绍) | 17 | 48 | 33.6503 | 1.43 |
| 图像(2389 输入 token) | 2389 | 256 | 125.0047 | 2.05 |
| 视频(12181 输入 token) | 12181 | 138 | 74.7064 | 1.85 |
| **总计/平均** | **3 samples** | — | **233.3613** | **1.77** |

> 原文:"rank 0 会打印每个样本的输入/输出 token 数、生成耗时、token/s 和解码文本,任务结束后会统计样本总数、总生成耗时和平均生成速率。"

---

## 【表格解读】

### 表 1 — `inference` 配置段参数说明(原文逐字还原)

| 参数 | 类型 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- |
| `load` | str | `null` | HF 或 DCP 权重路径。 |
| `load_format` | str | `hf` | 指定权重格式,可选 `hf`、`dcp` 或 `auto`。`auto` 会根据 `load` 目录特征自动判断加载权重格式。 |
| `seed` | int | `42` | 随机种子,主要影响采样生成及其他随机处理。 |
| `use_deter_comp` | bool | `false` | 是否启用确定性计算。有利于复现结果,但可能影响部分算子性能。 |
| `init_model_with_meta_device` | bool | `false` | 是否先在 meta device 构建空模型,再由 checkpointer 加载权重。 |
| `plugin` | List[str] | `[]` | 模型插件路径列表。构建模型前会递归导入插件目录,触发模型注册。 |
| `adapter` | str | `qwen3_5` | 负责输入预处理、生成和解码的模型 adapter。须与 `MODEL_ADAPTERS` 中注册的 key 一致。 |
| `processor_path` | str | — | tokenizer/processor 文件路径。 |
| `enable_thinking` | bool | `false` | 是否启用 processor chat template 的 thinking 模式。 |
| `data_path` | str | `null` | 输入 JSON 文件路径。 |
| `generation` | dict | — | 文本生成配置,控制最大生成长度、采样策略、重复惩罚和 KV cache 等生成行为。 |

**逐行解读:**
- `load`/`load_format` 共同决定权重装载源与格式,`auto` 模式下框架会自动嗅探目录特征。
- `seed` 默认为 42,主要影响采样类生成,贪心解码时影响较小。
- `use_deter_comp=false`(默认):优先性能;若需复现可设为 `true`,但会牺牲部分算子性能。
- `init_model_with_meta_device=true`(示例配置覆盖默认 `false`):先在 meta device 占位再 load,可显著降低大模型初始化时的显存占用。
- `plugin` 是列表,运行时递归 import,**触发模型注册**(类比 Megatron 中的 MODEL_REGISTRY)。
- `adapter` 是推理流程的关键桥梁,`qwen3_5`(默认)与示例中使用的 `qwen3_5_moe` 都需在 `MODEL_ADAPTERS` 注册。
- `processor_path` 在示例中用 YAML 锚点复用 `*HF_MODEL_LOAD_PATH`。
- `enable_thinking=false`:对应 Qwen3.5 系列 processor chat template 的 thinking 模式开关。
- `generation` 子 dict 控制解码行为(greedy/采样、长度、重复惩罚、KV cache)。

### 表 2 — 已适配与验证的模型列表(原文逐字还原)

| 后端 | 模型 | 输入数据类型 | 权重格式 |
| :--- | :--- | :--- | :--- |
| FSDP2 | Qwen3.5 Dense | 文本、图像、视频 | HF、DCP |
| FSDP2 | Qwen3.5 MoE | 文本、图像、视频 | HF、DCP |

**逐行解读:**
- 当前适配范围仅限 Qwen3.5 系列(Dense + MoE 两种架构)。
- 输入端覆盖纯文本、图像、视频三种模态(对应 JSON 中 `text`、`image`、`videos` 字段)。
- 权重格式支持 HF(HuggingFace)与 DCP(Distributed Checkpoint)两种,且通过 `load_format=auto` 可自动识别。
- 表格未列出的模型需按"模型适配"流程自行接入。

---

## 【公式解读】

**原文无公式。**

---

## 【关联】

文档内部通过一段 mermaid 时序图描绘了推理框架全流程,涉及以下模块/组件的协同关系(无内部链接,基于文中引用还原):

- **InferenceRunner**:总入口,负责读取 YAML、串联各组件;
- **Plugin / 注册表**:由 `inference.plugin` 配置触发递归 import,实现模型与适配器的运行时注册;
- **ModelHub**:依据 `model` 段 `model_id` 构建模型实例,文中示例为 `qwen3_5_moe`;
- **ParallelApplier**:根据 `parallel.fsdp_plan` / `parallel.ep_plan` 应用 FSDP2 分片与专家并行;
- **Checkpointer**:依据 `inference.load` 与 `inference.load_format` 写入模型权重(支持 `init_model_with_meta_device` 流程);
- **ModelAdapter**:由 `inference.adapter` 选中(`MODEL_ADAPTERS` 中注册),承担 `preprocess → generate → decode` 三段;
- **FSDP2 模型**:实际承载推理的最终分片模型。

上下游关系(基于文中上下文推断):
- 上游:**模型训练侧**(Megatron 等训练后端)→ 产出 HF/DCP 权重 → 被本推理框架加载;
- 下游:**线上部署系统**(注意事项中提示"线上部署场景建议替换为专业推理加速库")。

---

## 【使用方法】

### 启用方式(三步走)

1. **环境准备**:按照所用模型 README 完成环境配置;启动脚本中需 `source /usr/local/Ascend/cann/set_env.sh`,并 export 一组 Ascend 专用环境变量(`NON_MEGATRON=true`、`MULTI_STREAM_MEMORY_REUSE=2`、`TASK_QUEUE_ENABLE=2`、`ASCEND_LAUNCH_BLOCKING=0`、`ACLNN_CACHE_LIMIT=100000`、`CPU_AFFINITY_CONF=1`、`PYTORCH_NPU_ALLOC_CONF=expandable_segments:True`)。

2. **准备三件套**:
   - **输入数据**:`data/qwen3_5_moe_infer.json`,支持三种条目形态(纯文本 `text`、图像 `image`、视频 `videos`);
   - **启动脚本**:`examples/qwen3_5/qwen3_5_moe_inference.sh`,修改 `config_path` 与 `NPUS_PER_NODE` 等分布式参数;
   - **配置文件**:`examples/qwen3_5/qwen3_5_moe_inference.yaml`,将 `model_name_or_path`、`inference.load`、`inference.processor_path`、`inference.data_path`、`inference.plugin` 替换为实际路径。

3. **启动命令**:
   ```bash
   bash examples/qwen3_5/qwen3_5_moe_inference.sh
   ```

### 关键配置项(YAML 原文示例,逐项)

- **并行策略**:
  - `parallel.fully_shard_parallel_size: auto`
  - `parallel.fsdp_plan.apply_modules`(白名单覆盖视觉、文本、专家、lm_head、mtp)
  - `parallel.fsdp_plan.hook_modules: model.language_model.layers.{*}`
  - `parallel.fsdp_plan.param_dtype: bf16` / `reduce_dtype: fp32` / `reshard_after_forward: true`
  - `parallel.fsdp_plan.num_to_forward_prefetch: 1` / `num_to_backward_prefetch: 0`
  - `parallel.fsdp_plan.cpu_offload: false`
  - `parallel.ulysses_parallel_size: 1`
  - `parallel.expert_parallel_size: 1`
  - `parallel.ep_plan.apply_modules: model.language_model.layers.{*}.mlp.experts`
  - `parallel.ep_plan.dispatcher: alltoall`

- **模型属性**:
  - `model.model_id: qwen3_5_moe`
  - `model.model_name_or_path`(YAML 锚点 `&HF_MODEL_LOAD_PATH`,复用至 `inference.processor_path`)
  - `model.trust_remote_code: true`
  - `model.attn_implementation: flash_attention_2`
  - `model.gdn_implementation: eager`
  - `model.causal_conv1d_implementation: eager`
  - `model.use_grouped_expert_matmul: true`

- **推理控制**:
  - `inference.load`(HF 或 DCP 权重路径)
  - `inference.load_format: auto`
  - `inference.init_model_with_meta_device: true`
  - `inference.seed: 42`
  - `inference.use_deter_comp: false`
  - `inference.adapter: qwen3_5_moe`
  - `inference.processor_path: *HF_MODEL_LOAD_PATH`
  - `inference.enable_thinking: false`
  - `inference.data_path: ./data/qwen3_5_moe_infer.json`
  - `inference.generation.max_new_tokens: 256` / `do_sample: false` / `repetition_penalty: 1.0` / `use_cache: true`
  - `inference.plugin: [mindspeed_mm/fsdp/models/qwen3_5_moe]`

### 新增模型适配流程(原文)

1. 在 `mindspeed_mm/fsdp/inference/adapters/<adapter_name>.py` 新建类并继承 `ModelAdapter`,实现 `__init__`、`preprocess`(必须返回含 `input_ids` 的 dict)、`generate`(多 rank 同步)、`decode`(剥离 prompt token)四个方法;
2. 在 `mindspeed_mm/fsdp/inference/adapters/__init__.py` 中 `from .adapter_name import NewModelAdapter`,并写入 `MODEL_ADAPTERS = {..., "new_model": NewModelAdapter}`;
3. 在 YAML 中设置 `inference.adapter: new_model`,使其与 `MODEL_ADAPTERS` 注册的 key 一致。

### 使用限制(原文注意事项)

- 原文:"本推理流程仅适用于模型训练阶段的效果验证与结果比对,未针对线上部署场景做性能优化。若业务场景存在性能加速需求,建议替换并使用专业的推理加速库及对应优化组件开展部署工作。"

> 即该框架定位为**训练-验证对齐**用途,而非生产级高性能推理引擎。
