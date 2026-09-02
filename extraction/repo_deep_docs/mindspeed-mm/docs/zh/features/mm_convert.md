# 权重转换命令行工具

> 仓 `mindspeed-mm` · 路径 `docs/zh/features/mm_convert.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-mm/docs/zh/features/mm_convert.md

## 【定位】

本文档描述 `mindspeed-mm` 的权重转换命令行工具 `mm-convert`：以 Hugging Face 与 MindSpeed-MM 权重格式互转、重新切分权重为主要能力，并通过统一配置适配模型训练所需的流水并行和张量并行布局。

## 【技术要点】

1. **工具入口与适用范围**  
   新版权重转换接口于 **2025/1/20** 引入，当前支持 `qwen2vl` 各规格模型转换；命令行入口在 `pyproject.toml` 中注册为：
   ```toml
   [project.scripts]
   mm-convert = "checkpoint.convert_cli:main"
   ```
   安装 `mindspeed-mm` 后即可直接使用 `mm-convert`。

2. **两级命令结构**  
   顶层可选模型转换器：
   ```text
   Qwen2VLConverter
   InternVLConverter
   ```
   其中 `Qwen2VLConverter` 支持：
   ```text
   hf_to_mm   huggingface模型转换mindspeed-mm模型权重
   mm_to_hf   mindspeed-mm模型转换huggingface模型权重
   resplit    mindspeed-mm模型权重重新切分
   ```
   `InternVLConverter` 面向 `InternVL2.5/InternVL3` 模型。

3. **统一配置对象**  
   权重转换围绕 `cfg` 配置对象组织，主要包含：
   ```text
   cfg.mm_dir
   cfg.parallel_config.llm_pp_layers
   cfg.parallel_config.vit_pp_layers
   cfg.parallel_config.tp_size
   cfg.hf_config.hf_dir
   ```
   其中 `mm_dir` 和 `hf_dir` 为必填路径；`llm_pp_layers`、`vit_pp_layers` 为必填的逐卡层切分配置；`tp_size` 默认值为 `1`。

4. **三种配置传递方式**  
   `Qwen2VLConverter hf_to_mm` 同时支持：
   - 命令行直接传参；
   - 使用 `--print_config=comments` 生成 YAML，再填写并通过 `--config` 加载；
   - 通过环境变量传参，但需要先设置 `JSONARGPARSE_DEFAULT_ENV=true` 开启默认环境变量模式。

5. **训练并行配置必须一致**  
   `tp_size`、`llm_pp_layers`、`vit_pp_layers` 必须与训练脚本保持一致，否则生成的权重目录命名与切分不匹配，最终会导致加载失败。不同 `tp` 组在模型转换时需要切分到不同目录。

6. **权重版本兼容性要求**  
   转换过程会调用 `transformers` 相关 API，例如 `AutoConfig`。如果权重来自较旧的 `transformers` 生态，可能与当前版本不兼容；发生转换错误时，文档建议重新下载最新权重并再次转换。

## 【关键机制与数据】

- **原文:** 命令执行链为 `mindspeed-mm` 安装 → `pyproject.toml` 注册 `mm-convert` → 入口函数 `checkpoint.convert_cli:main` → 选择模型转换器 → 选择 `hf_to_mm`、`mm_to_hf` 或 `resplit` 子命令。
- **原文:** `Qwen2VL hf_to_mm` 的数据方向为：
  ```text
  cfg.hf_config.hf_dir
      → Qwen2VLConverter.hf_to_mm
      → cfg.mm_dir
  ```
  即从 `hf/Qwen2-VL-7B-Instruct` 读取 Hugging Face 权重，转换后写入 `mm/Qwen2-VL-7B-Instruct`。
- **原文:** `mm_to_hf` 执行相反的数据方向；`resplit` 则面向已经存在的 MindSpeed-MM 模型权重进行重新切分。
- **原文:** 并行配置参与权重目录和切分结果的生成。只有 `PP>1` 时，权重目录才带 stage 后缀，例如 `mp_rank_00_000`；`PP=1` 时目录为 `mp_rank_00`，此时 `llm_pp_layers` 应配置为单段，例如 `[[28]]`。
- **原文:** 示例转换配置为：
  ```text
  llm_pp_layers = [[1,10,10,7]]
  vit_pp_layers = [[32,0,0,0]]
  tp_size = 1
  ```
  文档未进一步说明数组中各数值的内部映射算法、张量重排规则或权重合并过程。
- **原文:** 未提供转换耗时、吞吐、显存占用、加速比等性能数据，因此不能对转换性能作定量判断。

## 【表格解读】

原文无表格。原文唯一结构化的配置项以 YAML 代码块给出；以下按最终填写后的 YAML 逐项还原并解读：

| YAML 位置 | 原文值 | 原文注释 | 逐项解读 |
|---|---|---|---|
| `cfg` |  |  | 所有转换参数的顶层配置对象。 |
| `cfg.mm_dir` | `"mm/Qwen2-VL-7B-Instruct"` | `mm保存的路径 (required, type: <class 'Path'>)` | 必填路径，指定转换后的 MindSpeed-MM 权重保存位置。 |
| `cfg.parallel_config` |  | `并行配置` | 集中管理 LLM、ViT 的流水并行切分和张量并行配置。 |
| `cfg.parallel_config.llm_pp_layers` | `[[1,10,10,7]]` | `llm模块pipeline parallel切分每张卡上切分几层 (required, type: list[list[Annotated[int, Ge(ge=0)]]])` | 必填，描述 LLM 模块在每张卡上的 pipeline parallel 层切分；必须与训练脚本一致。 |
| `cfg.parallel_config.vit_pp_layers` | `[[32,0,0,0]]` | `vit模块pipeline parallel切分每张卡上切分几层 (required, type: list[list[Annotated[int, Ge(ge=0)]]])` | 必填，描述 ViT 模块在每张卡上的 pipeline parallel 层切分；必须与训练脚本一致。 |
| `cfg.parallel_config.tp_size` | `1` | `tensor parallel张量并行组，模型转换时不同的tp组要切分到不同的目录下 (type: Annotated[int, Gt(gt=0)], default: 1)` | 张量并行组数量，默认 `1`；不同 `tp` 组会切分到不同目录。 |
| `cfg.hf_config` |  | `hf下载的原始权重路径配置` | 封装 Hugging Face 原始模型相关配置。 |
| `cfg.hf_config.hf_dir` | `"hf/Qwen2-VL-7B-Instruct"`` | `huggingface下载的路径 (required, type: Annotated[Path, PathType(path_type='dir')])` | 必填目录，指定待转换的 Hugging Face 权重路径。 |

## 【公式解读】

原文无公式。

## 【关联】

文末未提供内部链接，因此以下关系仅依据正文内容建立：

- **安装与入口关系：** 文档要求先按 README 安装 `mindspeed-mm`，随后由 `pyproject.toml` 的 `[project.scripts]` 注册并暴露 `mm-convert`。
- **模型与转换器关系：** `Qwen2VLConverter` 提供 Hugging Face 与 MindSpeed-MM 双向转换及权重重新切分；`InternVLConverter` 则对应 `InternVL2.5/InternVL3`。
- **格式上下游关系：** Hugging Face 权重是转换输入来源之一，MindSpeed-MM 权重是训练侧使用的目标格式；`mm_to_hf` 提供从 MindSpeed-MM 侧导出的反向能力。
- **转换与训练关系：** 训练脚本中的 `tp_size`、LLM pipeline 切分和 ViT pipeline 切分是转换布局的目标约束，转换结果必须在目录命名和权重切分上与其保持一致。
- **转换与依赖关系：** 转换过程依赖 `transformers` 提供的模型配置 API，文档以 `AutoConfig` 为例；Hugging Face 最新权重因此成为降低兼容性风险的输入来源。
- **并行维度关系：** `tp_size` 决定张量并行组，而 `llm_pp_layers`、`vit_pp_layers` 分别描述 LLM 和 ViT 模块的 pipeline parallel 层分布。

## 【使用方法】

### 1. 查看帮助

```bash
mm-convert -h
mm-convert Qwen2VLConverter -h
mm-convert Qwen2VLConverter hf_to_mm -h
```

### 2. 通过命令行参数执行转换

```bash
mm-convert  Qwen2VLConverter hf_to_mm \
  --cfg.mm_dir "mm/Qwen2-VL-7B-Instruct" \
  --cfg.hf_config.hf_dir "hf/Qwen2-VL-7B-Instruct" \
  --cfg.parallel_config.llm_pp_layers [[1,10,10,7]] \
  --cfg.parallel_config.vit_pp_layers [[32,0,0,0]] \
  --cfg.parallel_config.tp_size 1
```

### 3. 通过 YAML 文件执行转换

先生成带注释的基础配置：

```bash
mm-convert  Qwen2VLConverter hf_to_mm --print_config=comments > hf_to_mm.yaml
```

将配置填写为：

```yaml
# huggingface模型转换mindspeed-mm模型权重

# huggingface权重转换为mindspeed-mm权重配置
cfg:

  # mm保存的路径 (required, type: <class 'Path'>)
  mm_dir: "mm/Qwen2-VL-7B-Instruct"

  # 并行配置
  parallel_config:

    # llm模块pipeline parallel切分每张卡上切分几层 (required, type: list[list[Annotated[int, Ge(ge=0)]]])
    llm_pp_layers: [[1,10,10,7]]

    # vit模块pipeline parallel切分每张卡上切分几层 (required, type: list[list[Annotated[int, Ge(ge=0)]]])
    vit_pp_layers: [[32,0,0,0]] 

    # tensor parallel张量并行组，模型转换时不同的tp组要切分到不同的目录下 (type: Annotated[int, Gt(gt=0)], default: 1)
    tp_size: 1

  # hf下载的原始权重路径配置
  hf_config:

    # huggingface下载的路径 (required, type: Annotated[Path, PathType(path_type='dir')])
    hf_dir: "hf/Qwen2-VL-7B-Instruct"
```

然后执行：

```bash
mm-convert  Qwen2VLConverter hf_to_mm --config hf_to_mm.yaml
```

### 4. 通过环境变量执行转换

环境变量模式默认未开启，先启用：

```bash
export JSONARGPARSE_DEFAULT_ENV=true
```

配置转换参数：

```bash
export MM_CONVERT_QWEN2VLCONVERTER__HF_TO_MM__CFG__PARALLEL_CONFIG__LLM_PP_LAYERS="[[1,10,10,7]]"
export MM_CONVERT_QWEN2VLCONVERTER__HF_TO_MM__CFG__PARALLEL_CONFIG__VIT_PP_LAYERS="[[32,0,0,0]]"
export MM_CONVERT_QWEN2VLCONVERTER__HF_TO_MM__CFG__PARALLEL_CONFIG__TP_SIZE="1"
export MM_CONVERT_QWEN2VLCONVERTER__HF_TO_MM__CFG__HF_CONFIG__HF_DIR="hf/Qwen2-VL-7B-Instruct"
export MM_CONVERT_QWEN2VLCONVERTER__HF_TO_MM__CFG__MM_DIR="mm/Qwen2-VL-7B-Instruct"
```

最后执行：

```bash
mm-convert  Qwen2VLConverter hf_to_mm
```
