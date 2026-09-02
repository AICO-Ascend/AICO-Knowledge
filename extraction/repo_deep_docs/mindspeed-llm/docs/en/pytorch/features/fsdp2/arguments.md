# Full Parameter Reference

> 仓 `mindspeed-llm` · 路径 `docs/en/pytorch/features/fsdp2/arguments.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-llm/docs/en/pytorch/features/fsdp2/arguments.md

# mindspeed-llm FSDP2 全量参数参考 — 深度解读

## 【定位】

这篇文档是 **mindspeed-llm 框架 FSDP2 训练后端的「全量参数参考手册」**, 系统罗列了在该后端下启动分布式训练任务时可配置的全部参数(目前文档展示了 `ModelArguments` 与 `DataArguments` 两类), 旨在为用户提供一份**逐字段、可检索、可对照默认值的参数清单**, 避免翻阅源码反推配置项。

## 【技术要点】

1. **模型架构注册机制**: 通过 `model_id` 字段选择内置或自定义模型; 支持的字面量类型为 `Literal["gpt_oss", "qwen3", "qwen3_moe", "qwen3_next", "step35", "mamba3", "minimax_m27"]`, 不配置时回退到原生 Transformer forward。注册入口位于 `mindspeed_llm/fsdp2/models/model_registry.py` 的 `ModelRegistry` 类。
2. **元设备初始化**: `init_model_with_meta_device=True`(默认 `False`) 可降低模型初始化阶段的显存占用。
3. **量化策略矩阵**: 通过 `quant_recipe_name`(当前仅 `"mxfp8"`)、`quant_format`(支持 `E4M3`/`E5M2`/`HIF8`, 默认 `E4M3`)、`quant_block_size`(默认 `32`)、`quant_apply_modules`(默认 `['model.layers.{*}']`)、`quant_ignored_modules`(默认 `['*lm_head', '*gate']`)、`quant_converters`(默认 `["quantize.linear.mx"]`) 六个参数协同定义 MXFP8 块级量化行为。
4. **FSDP 低精度通信**: `enable_fsdp_low_precision_all_gather=True`(默认) 配合 `fsdp_low_precision_all_gather_mode`, 取值 `"on-demand"`(默认) 或 `"all"`, 控制前向/反向权重按需或全部以低精度聚合。
5. **Tokenizer 与词表扩展**: 提供 `resize_vocab`、`split_special_tokens`、`add_tokens`、`add_special_tokens`、`new_special_tokens_config`、`init_special_tokens`(`noise_init`/`desc_init`/`desc_init_w_noise`) 一组参数, 支持在加载后向词表注入普通 token 或语义初始化特殊 token。
6. **数据/模板机制**: `template` 字段从 `mindspeed_llm/fsdp2/data/template.py` 注册, 当前支持 `gpt` 和 `qwen3`; `dataset` 同时支持微调场景的内联配置/`dataset_info.json` 注册, 以及预训练场景的裸数据集路径输入。

## 【关键机制与数据】

**工作原理与数据流**(原文):

- **模型加载路径**: 文档要求 `model_name_or_path` 为**必填字段**(原文: "This field is required, and the system raises an exception if you do not specify it."), 系统在未指定时会抛出异常; 同时 `tokenizer_name_or_path` 仅在分词器路径与模型路径不一致时需要单独指定。
- **特殊 token 初始化优先级**: 原文明确指出 `new_special_tokens_config` **优先级高于** `add_special_tokens`(原文: "This field takes precedence over `add_special_tokens`."), 且 `init_special_tokens="desc_init"` 必须配套提供 `new_special_tokens_config` 才能生效。
- **数据集评估互斥**: 原文写明 `eval_dataset` 与 `val_size` **互斥**(原文: "This field is mutually exclusive with `val_size`. Therefore, you cannot set both at the same time."); `train_on_prompt=True` 与 `mask_history=True` 也不能同时设置(原文: "This field cannot be True at the same time as `mask_history`.")。
- **缓存与鉴权**: `cache_dir` 同时承接 Hugging Face 与 ModelScope 下载缓存; 三个 hub token 分别对应 `hf_hub_token`(Hugging Face)、`ms_hub_token`(ModelScope)、`om_hub_token`(Modelers) 三种模型仓库的鉴权。

原文未提供性能数据、benchmark 数字或训练吞吐指标, 故本文档无可对照的性能数据。

## 【表格解读】

### 表 1 — ModelArguments 全量参数(逐字还原)

| Parameter name | Type | Default | Details |
|---|---|---|---|
| `model_name_or_path` | `str` | `None (required)` | The local path of the model. This field is required, and the system raises an exception if you do not specify it. |
| `model_id` | `Optional[Literal["gpt_oss", "qwen3", "qwen3_moe", "qwen3_next", "step35", "mamba3", "minimax_m27"]]` | `None` | Model type identifier. If you do not configure it, the system runs the native Transformer model forward pass. If you configure it, the system runs the repository's custom model forward pass. To add a new model type, register it in the `ModelRegistry` class in `mindspeed_llm/fsdp2/models/model_registry.py`. |
| `init_model_with_meta_device` | `bool` | `False` | Whether to initialize the model with the meta device. When you enable it, you can reduce the GPU memory used during model initialization. |
| `trust_remote_code` | `bool` | `False` | Whether to allow loading models from custom modeling files on Hugging Face for custom model architectures. |
| `train_from_scratch` | `bool` | `False` | Whether to train the model from scratch with random weights without loading pretrained weights. |
| `tokenizer_name_or_path` | `Optional[str]` | `None` | The path or name of the Tokenizer. Specify it when it differs from `model_name_or_path`. |
| `cache_dir` | `Optional[str]` | `None` | The model cache directory, used to store models downloaded from Hugging Face and ModelScope. |
| `use_fast_tokenizer` | `bool` | `True` | Whether to use the fast Tokenizer implementation from the tokenizers library. It tokenizes faster than the traditional Tokenizer. |
| `resize_vocab` | `bool` | `False` | Whether to resize the Tokenizer and the corresponding output_layer/lm_head dimensions of the model for vocabulary expansion after adding tokens. |
| `split_special_tokens` | `bool` | `False` | Whether to split special tokens during tokenization. By default, the system does not split them and keeps special tokens intact. |
| `add_tokens` | `Optional[str]` | `None` | Non-special tokens to add to the Tokenizer. Separate multiple tokens with commas. |
| `add_special_tokens` | `Optional[str]` | `None` | Special tokens to add to the Tokenizer. Separate multiple tokens with commas. |
| `new_special_tokens_config` | `Optional[str]` | `None` | The path to the YAML configuration file for semantic initialization of special tokens. The format is `{'<token>': 'description text'}`. This field takes precedence over `add_special_tokens`. |
| `init_special_tokens` | `Literal["noise_init", "desc_init", "desc_init_w_noise"]` | `noise_init` | The initialization method for newly added special tokens. 1. noise_init (default): initialize with random noise based on the mean value. 2. desc_init: initialize from the semantics described in `new_special_tokens_config` and requires that parameter. 3. desc_init_w_noise: semantic initialization plus random noise. |
| `model_revision` | `str` | `main` | The model version to use. You can specify a branch name, tag name, or commit ID. |
| `hf_hub_token` | `Optional[str]` | `None` | The authentication token for Hugging Face Hub, suitable for downloading or uploading models from Hugging Face. |
| `ms_hub_token` | `Optional[str]` | `None` | The authentication token for ModelScope Hub, suitable for downloading or uploading models from ModelScope. |
| `om_hub_token` | `Optional[str]` | `None` | The authentication token for Modelers Hub, suitable for downloading or uploading models from Modelers. |
| `quant_recipe_name` | `Literal["mxfp8"]` | `None` | The quantization strategy. |
| `quant_format` | `str` | `"E4M3"` | FP8 data format used for quantization. Supported values: `E4M3`, `E5M2`, `HIF8`. |
| `quant_block_size` | `int` | `32` | Block size for MXFP8 block-wise quantization. |
| `quant_apply_modules` | `List[str]` | `['model.layers.{*}']` | The layers or modules to which quantization applies. |
| `quant_ignored_modules` | `List[str]` | `['*lm_head', '*gate']` | The list of submodules that do not use quantization. |
| `quant_converters` | `List[str]` | `["quantize.linear.mx"]` | The list of quantization converters to use. |
| `enable_fsdp_low_precision_all_gather` | `bool` | `True` | Whether to enable low-precision communication. |
| `fsdp_low_precision_all_gather_mode` | `Literal["on-demand", "all"]` | `on-demand` | FSDP low-precision all-gather, which aggregates forward or backward weights on demand. |

**逐行解读**:

- `model_name_or_path`: 唯一硬性必填项, 缺则抛异常, 是整个训练任务的起点。
- `model_id`: 决定走「仓库内置自定义 forward」还是「HF 原生 Transformer forward」; 通过 `ModelRegistry` 实现可插拔模型扩展。
- `init_model_with_meta_device`: 借助 PyTorch meta device 跳过初始权重实体分配, 对超大模型可显著压低初始显存峰值。
- `trust_remote_code`: 是否信任 HF 仓库中的自定义 `modeling_*.py`, 与 `trust_remote_code=True` 习惯一致。
- `train_from_scratch`: 不加载任何预训练权重, 配合 `model_name_or_path` 仅取其结构配置。
- `tokenizer_name_or_path`: 与 `model_name_or_path` 解耦, 便于用不同分词器(如词表重训)训练同一模型结构。
- `cache_dir`: 统一管理 HF 与 ModelScope 下载缓存, 避免重复下载。
- `use_fast_tokenizer`: 默认开启, 使用 Rust 实现的 `tokenizers` 库以提速。
- `resize_vocab`: 与 `add_tokens`/`add_special_tokens` 配合, 在新增 token 后联动调整 `lm_head` 输出维度。
- `split_special_tokens`: 默认保持特殊 token 完整, 开启后会在分词阶段被切碎(通常用于特殊场景的 token 分析)。
- `add_tokens`: 注入非特殊 token, 逗号分隔。
- `add_special_tokens`: 注入特殊 token(如 ``), 逗号分隔。
- `new_special_tokens_config`: YAML 语义配置文件, 优先级**高于** `add_special_tokens`; 格式 `{<token>: description}`。
- `init_special_tokens`: 三种初始化策略 — `noise_init`(均值噪声)、`desc_init`(纯语义, 需配置项)、`desc_init_w_noise`(语义+噪声)。
- `model_revision`: 支持 branch / tag / commit ID 三种版本定位方式, 默认 `main` 分支。
- `hf_hub_token` / `ms_hub_token` / `om_hub_token`: 三个模型仓库(HF / ModelScope / Modelers)的独立鉴权 token。
- `quant_recipe_name`: 量化策略选择, 当前仅支持 `"mxfp8"`。
- `quant_format`: FP8 数据格式, 默认 `E4M3`, 可选 `E5M2` 与 `HIF8`。
- `quant_block_size`: MXFP8 块级量化的块大小, 默认 `32`。
- `quant_apply_modules`: 参与量化的层通配, 默认对所有 `model.layers.*` 生效。
- `quant_ignored_modules`: 不量化的子模块, 默认排除 `lm_head` 与所有 `gate` 类门控模块。
- `quant_converters`: 量化转换器列表, 默认仅启用 `quantize.linear.mx`(线性层 MXFP8)。
- `enable_fsdp_low_precision_all_gather`: 是否启用 FSDP 低精度集合通信, 默认开启。
- `fsdp_low_precision_all_gather_mode`: 取值 `"on-demand"` 按需聚合前/反向权重, 取值 `"all"` 全量聚合。

### 表 2 — DataArguments 全量参数(逐字还原, 原文此处截断)

| Parameter name | Type | Default | Details |
|---|---|---|---|
| `template` | `Optional[str]` | `None` | The template name used to build prompts. `None` means the system parses the template from the tokenizer. To add a new template type, register it in `mindspeed_llm/fsdp2/data/template.py`. It currently supports gpt and qwen3. |
| `dataset` | `Optional[Union[Dict[str, Any], str]]` | `None` | Training dataset. For fine-tuning scenarios, dataset configuration supports inline configuration and registration through `dataset_info.json`. For pretraining scenarios, enter the raw dataset path directly. For detailed configuration examples, see FSDP2 backend training guide. A simple example is shown here: `dataset: file_name: "./my_data.json"   # Data file path. formatting: "alpaca"          # Data format.` |
| `eval_dataset` | `Optional[Union[Dict[str, Any], str]]` | `None` | Evaluation dataset. Use the same format as `dataset`. This field is mutually exclusive with `val_size`. Therefore, you cannot set both at the same time. |
| `dataset_dir` | `str` | `./configs/fsdp2/data` | The directory that stores dataset configuration files. |
| `cutoff_len` | `int` | `2048` | The truncation length of the input sequence after tokenization. Sequences that exceed this length are truncated. |
| `train_on_prompt` | `bool` | `False` | Whether to remove the mask from the prompt part. This field cannot be True at the same time as `mask_history`. |
| `mask_history` | `bool` | `False` | Whether to mask conversation history and train only on the final response. When this field is True, the system does not comp[原文在此处截断] |

**逐行解读**:

- `template`: 提示词模板名, 缺省时按 tokenizer 自动解析; 注册入口 `mindspeed_llm/fsdp2/data/template.py`, 目前内置 `gpt` 与 `qwen3`。
- `dataset`: 训练数据集; 微调场景支持内联 YAML 或 `dataset_info.json` 注册, 预训练场景直接传裸路径; 示例格式为 `file_name` + `formatting`(如 `alpaca`)。
- `eval_dataset`: 评估数据集, 配置格式与 `dataset` 一致, 但与 `val_size` 互斥。
- `dataset_dir`: 数据集配置文件的默认存放目录, 默认 `./configs/fsdp2/data`。
- `cutoff_len`: 序列分词后截断长度, 默认 `2048`。
- `train_on_prompt`: 取消 prompt 部分的 loss mask, 让模型在 prompt token 上也计算损失; 与 `mask_history` 互斥。
- `mask_history`: 屏蔽对话历史, 仅在最后一轮 response 上计算损失; 原文此处被截断(`does not comp…`), 推测完整语义为"不在 history 部分计算 loss"(推断, 未在原文中得到确认)。

> 注: 原文 DataArguments 表格在 `mask_history` 行中途被截断, 后续参数(`val_size`、`packing`、`preprocessing_num_workers` 等典型字段)在原文中**未提供**, 故本文档不予臆造。

## 【公式解读】

原文无公式。

## 【关联】

- **模型注册扩展入口**: `mindspeed_llm/fsdp2/models/model_registry.py` 中的 `ModelRegistry` 类 — 文档明确指出添加新的 `model_id` 必须注册到此处, 该模块是文档中唯一被点名的模型层扩展点。
- **模板注册扩展入口**: `mindspeed_llm/fsdp2/data/template.py` — 添加新 `template` 必须注册到此处, 当前内置支持 `gpt` 与 `qwen3`。
- **数据配置示例与微调训练流程**: 文档中 `dataset` 字段给出了一个 `../../training/finetune/fsdp2/finetune_fsdp2.md` 的相对链接, 指向 **FSDP2 backend training guide**(FSDP2 后端训练指南), 用于查阅数据集配置的完整 YAML 示例与微调流程 — 这是文末提供的唯一一处显式交叉引用。
- **模型仓库生态**: `cache_dir` 同时面向 Hugging Face 与 ModelScope; `hf_hub_token` / `ms_hub_token` / `om_hub_token` 三个 token 字段将系统与 HF / ModelScope / Modelers 三大模型仓库串联。
- **FSDP 通信后端**: `enable_fsdp_low_precision_all_gather` 与 `fsdp_low_precision_all_gather_mode` 与 MXFP8 量化(`quant_recipe_name="mxfp8"`、`quant_format` 等)协同, 共同构成"训练-量化-通信"三段式低精度流水。
- **量化与门控**: `quant_ignored_modules` 默认排除 `*lm_head` 与 `*gate`, 说明量化被有意限定在 attention/MLP 主干线性层, 而非输出头与门控(原文表述, 未给出原因细节)。

## 【使用方法】

启用方式/配置项/命令(原文涉及):

1. **必填项**: 任何 FSDP2 训练任务都必须显式提供 `model_name_or_path` 字段, 否则系统会抛出异常。
2. **模型选择**: 二选一 — 不配置 `model_id` 走原生 HF Transformer forward; 配置 `model_id` 走仓库内置自定义 forward(可选取值见上文技术要点)。
3. **模型初始化**: 设置 `--init-model-with-meta-device True` 以在 meta device 上初始化模型, 降低初始显存占用。
4. **量化启用**: 组合 `quant_recipe_name=mxfpp8`、`quant_format=E4M3`(或 `E5M2`/`HIF8`)、`quant_block_size=32`, 并通过 `quant_apply_modules` / `quant_ignored_modules` / `quant_converters` 精确控制作用范围与转换器。
5. **FSDP 低精度通信**: 默认 `enable_fsdp_low_precision_all_gather=True`, 模式可选 `on-demand`(默认) 或 `all`。
6. **词表扩展**: 通过 `add_tokens` / `add_special_tokens`(逗号分隔)添加 token; 若需语义初始化, 配置 `new_special_tokens_config` 指向 YAML 文件(格式 `{'<token>': 'description text'}`), 并选择 `init_special_tokens ∈ {noise_init, desc_init, desc_init_w_noise}`(其中 `desc_init` 强制依赖 `new_special_tokens_config`)。
7. **数据集声明**: 微调场景使用 `dataset` 内联配置或 `dataset_info.json` 注册(示例 `file_name: "./my_data.json"` + `formatting: "alpaca"`); 预训练场景直接传入裸数据集路径; 配置目录默认 `./configs/fsdp2/data`。
8. **模板选择**: 设置 `template="gpt"` 或 `"qwen3"`(或不设置, 由 tokenizer 自动解析)。
9. **序列截断**: 默认 `cutoff_len=2048`, 超长序列被截断。
10. **互斥约束**: 同时避免启用 `eval_dataset` + `val_size`、以及 `train_on_prompt=True` + `mask_history=True` 这两组互斥字段。

> 说明: 文档未涉及具体启动命令(如 `torchrun` / `msrun` 等执行入口)与 YAML 配置文件的完整骨架, 启动命令相关说明需参考文档中提及的 `../../training/finetune/fsdp2/finetune_fsdp2.md`(FSDP2 backend training guide)以获取 — 原文未直接给出命令行示例。
