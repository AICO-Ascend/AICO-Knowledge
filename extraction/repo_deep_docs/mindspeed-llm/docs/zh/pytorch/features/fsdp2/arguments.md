# 全量参数说明

> 仓 `mindspeed-llm` · 路径 `docs/zh/pytorch/features/fsdp2/arguments.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-llm/docs/zh/pytorch/features/fsdp2/arguments.md

# 一体化深度解读：mindspeed-llm FSDP2 全量参数说明

## 【定位】

本文档是 mindspeed-llm 框架 FSDP2 后端的「全量配置参数参考手册」，系统罗列 `ModelArguments`（模型参数）与 `DataArguments`（数据参数）两大参数集合的全部字段、类型、默认值与语义说明，为使用 FSDP2 后端进行 LLM 训练/微调的用户提供单一权威的查表依据。

---

## 【技术要点】

1. **模型与分词器装载**：通过 `model_name_or_path`（必填）与 `tokenizer_name_or_path`、`cache_dir`、`model_revision` 等控制 Hugging Face / ModelScope / Modelers 三种 Hub 的模型加载流程；`use_fast_tokenizer` 默认 `True` 启用 tokenizers 快速实现，`split_special_tokens` 默认 `False` 保持特殊 token 完整性。

2. **仓库自定义模型前向开关**：`model_id` 是关键路由字段，未配置时执行「原生 transformer 模型前向」，配置后切换为仓库自定义前向；新增类型需在 `mindspeed_llm/fsdp2/models/model_registry.py` 的 `ModelRegistry` 类注册，可选字面量共 9 个：`gpt_oss, qwen3, qwen3_moe, qwen3_next, step35, mamba3, minimax_m27, longcat_flash_ngram, deepseek_v4`。

3. **特殊 token 扩展三件套**：`add_tokens` / `add_special_tokens` / `new_special_tokens_config` 配合 `init_special_tokens`（三选一：`noise_init` / `desc_init` / `desc_init_w_noise`）实现新 token 的语义或噪声初始化；`new_special_tokens_config` 优先级高于 `add_special_tokens`，配置格式为 `{'<token>': 'description text'}` 的 YAML。

4. **MXFP8 量化策略**：`quant_recipe_name` 当前仅支持 `mxfp8`；`quant_format` 默认 `E4M3`，另支持 `E5M2` 与 `HIF8`；`quant_block_size` 默认 `32`；`quant_apply_modules` 默认 `['model.layers.{*}']`，`quant_ignored_modules` 默认 `['*lm_head', '*gate']`，`quant_converters` 默认 `["quantize.linear.mx"]`。

5. **FSDP 低精度通信**：`enable_fsdp_low_precision_all_gather` 默认 `True`，`fsdp_low_precision_all_gather_mode` 提供 `on-demand`（默认，按需聚合前向或反向权重）与 `all`（全部聚合）两种策略。

6. **数据集混合与流式处理**：`mix_strategy` 支持 `concat`（默认）/ `interleave_under` / `interleave_over`，后者需配合 `interleave_probs`；`streaming=True` 时启用 `buffer_size=16384` 的随机采样缓冲区，且与 `max_samples` 互斥，要求 `val_size` 为整数。

7. **数据预处理与打包**：`cutoff_len=2048` 截断序列；`preprocessing_batch_size=1000`；`packing` 与 `neat_packing`（无交叉注意力打包，启用后自动开启 packing）控制多短序列打包为长序列。

---

## 【关键机制与数据】

**数据流与配置链路（原文信息整合）**：

- **数据集加载路径**：微调场景支持「内联配置」或通过 `dataset_info.json` 注册两种方式；预训练场景直接填写原始数据集路径。配置目录由 `dataset_dir` 控制，默认 `./configs/fsdp2/data`。
- **验证集划分互斥关系**：`val_size` 与 `eval_dataset` 互斥；`train_on_prompt` 与 `mask_history` 互斥；`streaming` 与 `max_samples` 互斥。
- **Prompt 模板机制**：`template` 字段为 `None` 时从 tokenizer 中解析；目前已注册支持 `gpt` 与 `qwen3`，新增模板需在 `mindspeed_llm/fsdp2/data/template.py` 注册。
- **评估机制**：`eval_num_beams` 控制 `model.generate` 的 beam 数；`ignore_pad_token_for_loss` 默认 `True` 在损失计算时忽略 pad；`eval_on_each_dataset` 支持按数据集分别评估。
- **Meta Device 初始化**：`init_model_with_meta_device=True` 时以 meta device 初始化模型，可节省初始化阶段显存占用。
- **工具调用与系统提示**：`tool_format` 用于规范函数调用示例；`default_system` 覆盖模板默认系统提示词；`enable_thinking`（默认 `True`）控制推理模型是否生成中间思考过程。

> 注：原文未提供具体性能数据或基准测试结果。

---

## 【表格解读】

### 表 1：ModelArguments（模型参数）

| 参数名 | 类型 | 默认值 | 详细说明 |
|---|---|---|---|
| model_name_or_path | str | 无（必填） | 模型的本地路径，必填项，未指定会抛出异常。 |
| model_id | Optional[Literal["gpt_oss", "qwen3", "qwen3_moe", "qwen3_next", "step35", "mamba3", "minimax_m27", "longcat_flash_ngram", "deepseek_v4"]] | None | 模型类型标识，未配置时执行原生 transformer 模型前向，配置时执行仓库自定义模型前向。新增模型类型需在 `mindspeed_llm/fsdp2/models/model_registry.py` 的 `ModelRegistry` 类中注册。 |
| init_model_with_meta_device | bool | False | 是否使用 meta device 初始化模型，启用后可节省模型初始化阶段的显存占用。 |
| trust_remote_code | bool | False | 是否允许加载 Hugging Face 上自定义建模文件中的模型，用于适配自定义模型架构。 |
| train_from_scratch | bool | False | 是否使用随机权重从头开始训练模型，不加载模型权重。 |
| tokenizer_name_or_path | Optional[str] | None | Tokenizer 的路径或名称，与 `model_name_or_path` 路径不一致时需要指定。 |
| cache_dir | Optional[str] | None | 模型缓存目录，用于存储从 Hugging Face、ModelScope 下载的模型。 |
| use_fast_tokenizer | bool | True | 是否使用 tokenizers 库实现的快速 Tokenizer，相比传统 Tokenizer 分词速度更快。 |
| resize_vocab | bool | False | 是否调整 Tokenizer 大小及模型对应 output_layer/lm_head 的维度，用于适配新增 token 后的词表扩展场景。 |
| split_special_tokens | bool | False | 分词过程中是否拆分特殊 token，默认不拆分，保持特殊 token 的完整性。 |
| add_tokens | Optional[str] | None | 需添加到 Tokenizer 的非特殊 token，多个 token 用逗号分隔。 |
| add_special_tokens | Optional[str] | None | 需添加到 Tokenizer 的特殊 token，多个 token 用逗号分隔。 |
| new_special_tokens_config | Optional[str] | None | 特殊 token 语义初始化的 YAML 配置文件路径，格式为 `{'<token>': 'description text'}`，优先级高于 `add_special_tokens`。 |
| init_special_tokens | Literal["noise_init", "desc_init", "desc_init_w_noise"] | noise_init | 新增特殊 token 的初始化方式：1. noise_init（默认）：基于均值的随机噪声初始化；2. desc_init：基于 `new_special_tokens_config` 中描述的语义初始化（需配置该参数）；3. desc_init_w_noise：语义初始化+随机噪声。 |
| model_revision | str | main | 指定使用的模型版本，可填写分支名、标签名或 commit id。 |
| hf_hub_token | Optional[str] | None | Hugging Face Hub 的认证令牌，适用于从 Hugging Face 下载/上传模型的场景。 |
| ms_hub_token | Optional[str] | None | ModelScope Hub 的认证令牌，适用于从 ModelScope 下载/上传模型的场景。 |
| om_hub_token | Optional[str] | None | Modelers Hub 的认证令牌，适用于从 Modelers 下载/上传模型的场景。 |
| quant_recipe_name | Optional[Literal["mxfp8"]] | None | 量化策略。 |
| quant_format | str | "E4M3" | 量化使用的 FP8 数据格式，支持 `E4M3`、`E5M2`、`HIF8`。 |
| quant_block_size | int | 32 | MXFP8 分块量化块大小。 |
| quant_apply_modules | List[str] | ['model.layers.{*}'] | 应用量化的层或模块。 |
| quant_ignored_modules | List[str] | ['*lm_head', '*gate'] | 不应用量化的子模块列表。 |
| quant_converters | List[str] | ["quantize.linear.mx"] | 使用的量化转换器列表。 |
| enable_fsdp_low_precision_all_gather | bool | True | 是否启用低精度通信。 |
| fsdp_low_precision_all_gather_mode | Literal["on-demand", "all"] | on-demand | FSDP 低精度 all-gather，按需聚合前向或反向权重 |

**逐行解读**：

- **model_name_or_path / train_from_scratch**：强制加载路径与「是否真要从零训练」成对存在；前者用于从已有 checkpoint 继续/微调，后者跳过权重加载。
- **model_id**：作为「仓库自定义模型前向」的路由开关，未配置则 fallback 到原生 HF 逻辑，配置后走仓库定制实现——这意味着新模型接入必须经过 ModelRegistry 注册流程。
- **init_model_with_meta_device**：通过延迟物化（meta tensor）规避一次性显存峰值，是大模型初始化的标准做法。
- **resize_vocab / add_tokens / add_special_tokens**：三者配合完成词表扩展链路：词表 resize → 新增 token → 嵌入层与 lm_head 同步调整维度。
- **new_special_tokens_config vs init_special_tokens**：构成「语义初始化」双开关——前者定义「什么是这个 token」（YAML 描述），后者定义「用何种方式初始化」（噪声/语义/语义+噪声）。
- **hf_hub_token / ms_hub_token / om_hub_token**：覆盖三大模型仓库（HuggingFace、ModelScope、Modelers）的鉴权，与 `cache_dir` 共同支持多源下载。
- **量化四件套（quant_recipe_name/quant_format/quant_block_size/quant_apply_modules/quant_ignored_modules/quant_converters）**：构成 MXFP8 量化的完整链路——recipe 选算法（仅 mxfp8）、format 选 FP8 子格式、block_size 决定分块粒度、apply/ignored 控制作用范围、converters 指定转换器实现。
- **FSDP 通信优化双参**：`enable_fsdp_low_precision_all_gather=True` 配合 `on-demand` 默认策略，是 FSDP2 节省通信带宽的核心开关。

---

### 表 2：DataArguments（数据参数）

| 参数名 | 类型 | 默认值 | 详细说明 |
|---|---|---|---|
| template | Optional[str] | None | 构建 prompt 的模板名称，None 表示从 tokenizer 中解析 template。新增 template 类型需在 `mindspeed_llm/fsdp2/data/template.py` 文件中注册，目前支持 gpt 和 qwen3。 |
| dataset | Optional[Union[Dict[str, Any], str]] | None | 训练数据集：微调场景数据集配置支持内联配置和通过 `dataset_info.json` 注册两种方式，预训练场景数据集配置直接填写原始数据集路径。具体配置示例参考 FSDP2 后端训练使用指南，此处提供简单配置示例：`dataset: file_name: "./my_data.json"   # 数据文件路径 formatting: "alpaca"          # 数据格式` |
| eval_dataset | Optional[Union[Dict[str, Any], str]] | None | 评估数据集：填写方式与 `dataset` 一致。与 `val_size` 互斥，不可同时设置。 |
| dataset_dir | str | ./configs/fsdp2/data | 数据集配置文件所在目录。 |
| cutoff_len | int | 2048 | 分词后输入序列的截断长度，超过该长度的序列会被截断。 |
| train_on_prompt | bool | False | 是否取消 prompt 部分的掩码，与 `mask_history` 不可同时为 True。 |
| mask_history | bool | False | 是否掩码对话历史，仅在最后一轮回复上训练；True 时对话历史部分不计算损失，与 `train_on_prompt` 不可同时为 True。 |
| streaming | bool | False | 是否启用数据集流式加载，与 `max_samples` 互斥，且 `val_size` 需为整数。 |
| buffer_size | int | 16384 | 流式加载时的随机采样缓冲区大小。 |
| mix_strategy | Literal["concat", "interleave_under", "interleave_over"] | concat | 多数据集混合策略：拼接/欠采样/过采样。 |
| interleave_probs | Optional[str] | None | 多数据集交叉采样概率，使用逗号分隔，仅在 `mix_strategy` 为 interleave_under/interleave_over 时生效。 |
| overwrite_cache | bool | False | 是否覆盖已缓存的预处理后数据集。 |
| preprocessing_batch_size | int | 1000 | 数据预处理时每组的样本数量。 |
| preprocessing_num_workers | Optional[int] | None | 数据预处理的进程数。 |
| max_samples | Optional[int] | None | 调试用，用于截断每个数据集的样本数量，与 `streaming` 互斥。 |
| eval_num_beams | Optional[int] | None | 评估时 `model.generate` 使用的 beam 数量。 |
| ignore_pad_token_for_loss | bool | True | 损失计算时是否忽略填充标签对应的 token。 |
| val_size | float | 0.0 | 验证集大小，整数或 0~1 的浮点数。需同时指定 `dataset`，与 `eval_dataset` 互斥。 |
| eval_on_each_dataset | bool | False | 是否分别在每个数据集上进行评估。 |
| packing | bool | False | 是否启用序列打包，将多个短序列打包为一个长序列。 |
| neat_packing | bool | False | 是否启用无交叉注意力的序列打包，启用后自动设置 `packing=True`。 |
| tool_format | Optional[str] | None | 构建函数调用示例使用的工具格式，用于适配工具调用类任务，统一函数调用的格式规范。 |
| default_system | Optional[str] | None | 覆盖模板中的默认系统提示词，用于自定义系统提示。 |
| enable_thinking | Optional[bool] | True | 是否为推理模型启用思考模式，启用后模型会生成中间思考过程。True 表示启用，False 表示不启用，None 表示不删除原始数据中的 [c …（原文截断） |

**逐行解读**：

- **template**：模板路由字段，与 `model_id` 类似需在 `template.py` 注册，目前支持 `gpt` 与 `qwen3`。
- **dataset**：训练数据集双轨制——微调走 `dataset_info.json` 或内联配置，预训练直接填原始路径。原文给出最简示例：`dataset: file_name: "./my_data.json" formatting: "alpaca"`。
- **三组互斥约束**：`eval_dataset ↔ val_size`、`train_on_prompt ↔ mask_history`、`streaming ↔ max_samples`——这些是用户配置时最易踩坑的开关对。
- **流式加载三联动**：`streaming=True` → 必须设 `buffer_size=16384` → 同时强制 `val_size` 为整数。
- **多数据集混合**：`mix_strategy` 三选一；`interleave_under`/`interleave_over` 必须配 `interleave_probs`（逗号分隔概率串）。
- **序列打包两级**：`packing`（标准打包）vs `neat_packing`（无交叉注意力打包，自动启用 packing），后者避免不同样本在 attention 中相互干扰。
- **eval_num_beams / ignore_pad_token_for_loss**：评估阶段标准配置——beam search 与 pad 掩码。
- **enable_thinking**：控制推理模型（如带 chain-of-thought 的 Qwen3）是否生成中间思考过程；原文此字段说明在「None 表示不删除原始数据中的...」处截断。

> ⚠️ 注意：原文 `DataArguments` 表中 `enable_thinking` 的说明在 `…原始数据中的<c` 处被截断，存在内容缺失。

---

## 【公式解读】

原文无公式。

---

## 【关联】

根据原文信息，本文档与其他模块/特性的关联如下：

1. **FSDP2 后端训练使用指南**（`docs/zh/pytorch/training/finetune/fsdp2/finetune_fsdp2.md`）：原文中 `dataset` 字段的「具体配置示例」明确指向该文档，是本文档的主要下游使用指引，定义了如何把这里罗列的参数组装成可运行的训练配置。

2. **ModelRegistry 类**（`mindspeed_llm/fsdp2/models/model_registry.py`）：`model_id` 字段的新增模型注册入口，决定了仓库支持的自定义模型前向范围（当前已注册 9 个：gpt_oss、qwen3、qwen3_moe、qwen3_next、step35、mamba3、minimax_m27、longcat_flash_ngram、deepseek_v4）。

3. **template 注册表**（`mindspeed_llm/fsdp2/data/template.py`）：`template` 字段的新增模板注册入口，决定了 prompt 构造的可用模板（目前支持 gpt 与 qwen3）。

4. **MXFP8 量化模块**：`quant_recipe_name/quant_format/quant_block_size/quant_apply_modules/quant_ignored_modules/quant_converters` 共同指向框架内置的 MXFP8 量化实现链路（`quantize.linear.mx` 转换器）。

5. **FSDP 通信底层**：`enable_fsdp_low_precision_all_gather` 与 `fsdp_low_precision_all_gather_mode` 是 FSDP2 通信优化的开关，依赖 PyTorch FSDP2 的 all-gather 实现。

6. **上游：Hugging Face / ModelScope / Modelers 三大模型 Hub**：通过 `hf_hub_token` / `ms_hub_token` / `om_hub_token` 与 `cache_dir` 对接，构成模型与分词器的来源链路。

---

## 【使用方法】

原文给出的具体使用方法集中在「数据集内联配置」一处，完整还原如下：

```yaml
dataset:
  file_name: "./my_data.json"   # 数据文件路径
  formatting: "alpaca"          # 数据格式
```

该配置属于 `DataArguments.dataset` 字段的「内联配置」方式（适用于微调场景），预训练场景可直接填写原始数据集路径字符串，复杂场景需通过 `dataset_info.json` 注册并配置 `dataset_dir`（默认 `./configs/fsdp2/data`）。

**其他配置项的启用方式**：

- **量化启用**：设置 `quant_recipe_name="mxfp8"`，配合 `quant_format`（默认 `E4M3`）、`quant_block_size=32`、`quant_apply_modules` 与 `quant_ignored_modules` 调整作用范围。
- **低精度通信启用**：`enable_fsdp_low_precision_all_gather=True`（默认即启用），按需切换 `fsdp_low_precision_all_gather_mode` 为 `on-demand`（默认）或 `all`。
- **特殊 token 扩展**：组合 `add_tokens` / `add_special_tokens` + `new_special_tokens_config`（YAML）+ `init_special_tokens`（`noise_init` / `desc_init` / `desc_init_w_noise`）+ `resize_vocab=True`。
- **Meta Device 初始化**：`init_model_with_meta_device=True`。
- **从零训练**：`train_from_scratch=True`（注意仍需设置 `model_name_or_path`，框架据此获取模型结构）。
- **流式数据加载**：`streaming=True`（自动启用 `buffer_size=16384`，需保证 `val_size` 为整数、不可同时设 `max_samples`）。
- **序列打包**：`packing=True` 或 `neat_packing=True`（后者自动启用前者）。

> 原文未提供完整命令行调用示例（如 `torchrun` 启动脚本）；具体启动方式需参考关联的「FSDP2 后端训练使用指南」（`finetune_fsdp2.md`）。
