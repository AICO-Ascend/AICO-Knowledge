# 针对VL模型的数据构造

> 仓 `mindspeed-mm` · 路径 `docs/zh/features/building_data_for_VLModel.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-mm/docs/zh/features/building_data_for_VLModel.md

# 针对VL模型的数据构造 — 一体化深度解读

---

## 【定位】

本篇文档解决 mindspeed-mm 套件中**视觉-语言（VL）模型的数据准备问题**：说明如何将常见的开源多模态数据集（如 COCO2017 + LLaVA-Instruct-150K）转换为框架可直接训练的目标格式，以及如何在功能/性能压测场景下生成参数可控的虚构数据，覆盖真实数据通路与 mock 数据通路两条数据准备路径。

---

## 【技术要点】

1. **格式参考与设计来源**：当前数据处理方式参考 [LLaMAFactory](https://github.com/hiyouga/LLaMAFactory) 实现，采用本地多模态 ShareGPT 风格的字段约定（`messages` + `images`/`videos`）。
2. **通用适用范围**：通用于仓库内大多数 VL 模型（Qwen3.6、Qwen3.5、Qwen3VL、Qwen2.5VL、GLM4.5V、Kimi-K2.5、Step3-VL），特殊模态（视频/音频）以各模型 README 为准。
3. **真实数据通路三步走**：①下载 COCO2017 至 `./data/COCO2017`；②下载 LLaVA-Instruct-150K 描述文件至 `./data/`；③运行 `llava_instruct_2_mllm_demo_format.py` 完成格式转换。
4. **目标 JSON 格式双形态**：图文数据使用 `<image>sourceN` 作为 content token + `images` 列表；视频文本数据使用 `<video>sourceN` + `videos` 列表；多轮对话通过 `messages` 数组中 `role: user / assistant` 串联。
5. **多数据集与混合数据支持**：训练配置 `dataset` 字段支持以英文逗号 `,`（无空格）拼接多个 JSON；纯文本/图文混合数据均已支持。
6. **虚构数据可控生成**：通过 `generate_mock_data_for_vlmodel.py` 在指定 `--pic_width / --pic_height / --num_pics / --text_length / --num_samples` 与 `--tokenizer_path` 下，批量生成分辨率/长度可控的 mock 数据，用于规避真实数据长度抖动与下载成本。
7. **关键训练配置项**：`cutoff_len`（序列截断阈值，建议与构造数据图文总长接近，避免图片占位符被截断）、`max_samples`（快速验证时限制样本数，`null` 表示全量）。

---

## 【关键机制与数据】

**工作原理与数据流（真实数据）**：

1. 用户本地落盘 COCO2017 原始图像 + LLaVA-Instruct-150K 原始 JSON 描述。
2. 原始 JSON 是 LLaVA 风格字段（`image`、`conversations`、`from`、`value`），**不是**训练直接读取的格式。
3. 调用 `mindspeed_mm/fsdp/tools/data_tool/llava_instruct_2_mllm_demo_format.py`，通过 `--coco_path`、`--llava_json_path`、`--output_json_path` 三个参数把 LLaVA 风格转成 mllm 目标格式（`messages` + `images`）。
4. 修改 `xxx_config.yaml` 的 `data.dataset_param.basic_parameters`：填入 `dataset_dir`（图像根目录）、`dataset`（转换后的 JSON 路径），可选 `max_samples` 控制样本数。
5. 训练时框架读取 `dataset_dir` 中的图像 + `dataset` JSON 中的 `images` 字段完成图文对齐加载。

**工作原理与数据流（mock 数据）**：

1. 加载指定模型的 `--tokenizer_path`（如 `/home/weights/Qwen3.5-35B-A3B/`），以保证文本 token 化方式与训练一致。
2. 按 `--pic_width × --pic_height` 生成空像素图，按 `--num_pics` 张/样本组装，按 `--text_length` 长度的随机 token 化文本填充。
3. 重复 `--num_samples` 条样本，落到 `--save_dir`。
4. 配置 `cutoff_len` 需与构造数据的图文序列总长接近，否则图片占位符有被截断的风险。

**性能/规模数据（原文有的标注）**：

- 原文示例：生成 **512 条样本**，每条 **10 张 1024×1024 图片 + 16384 文本长度**。
- 原文示例：`cutoff_len: 16384`（与构造数据文本长度一致）。
- 原文未涉及具体吞吐/加速比等性能数据。

---

## 【表格解读】

> 原文无独立参数表，但包含 **2 段 YAML 配置** 与 **2 段 JSON 样例**，以下逐字还原并逐行解读。

### 表 A — 真实数据训练配置（原文 2.2 节 YAML，逐字还原）

| 字段路径 | 取值 | 解读 |
|---|---|---|
| `data.dataset_param.basic_parameters.dataset_dir` | `./data/COCO2017` | 指向已解压的 COCO2017 图像根目录；图片加载器会基于此路径与 JSON 中的 `images` 字段拼接得到实际文件路径。 |
| `data.dataset_param.basic_parameters.dataset` | `./data/mllm_format_llava_instruct_data.json` | 指向格式转换**后**的描述文件 JSON（非原始 LLaVA JSON），`&DATASET_PATH` 是 YAML 锚点，供其他字段复用。 |
| `data.dataset_param.basic_parameters.max_samples` | `null` | 限制只读取前 N 条样本；`null` 表示读取全部；可设为具体数字用于快速冒烟。 |

### 表 B — 多数据集拼接配置（原文 2.3 节 YAML，逐字还原）

| 字段路径 | 取值 | 解读 |
|---|---|---|
| `data.dataset_param.basic_parameters.dataset_dir` | `./data/COCO2017` | 多数据集共用同一图像根目录。 |
| `data.dataset_param.basic_parameters.dataset` | `./data/mllm_format_llava_instruct_data1.json,./data/mllm_format_llava_instruct_data2.json` | 多个 JSON 用英文逗号 `,` 拼接，**不能加空格**；框架按顺序拼接样本流。 |

### 表 C — 目标格式：图文数据（原文 JSON，逐字还原）

```json
[
  {
    "messages":[
      {"content": "<image>source1", "role": "user"},
      {"content": "target1", "role": "assistant"},
      {"content": "<image>source2", "role": "user"},
      {"content": "target2", "role": "assistant"}
    ],
    "images": ["demo_image_1.jpg", "demo_image_2.jpg"]
  }
]
```

解读：`<image>sourceN` 是图像占位符 token，`sourceN` 为自然语言描述或提问，对应的图像路径在 `images` 数组中按出现顺序对齐；多轮 `user/assistant` 模拟对话流。

### 表 D — 目标格式：视频文本数据（原文 JSON，逐字还原）

```json
[
  {
    "messages":[
      {"content": "<video>source1", "role": "user"},
      {"content": "target1", "role": "assistant"}
    ],
    "videos": ["demo_video.mp4"]
  }
]
```

解读：视频模态使用 `<video>` 占位符 + `videos` 列表，结构与图文一致，只是媒体容器替换。

### 表 E — mock 数据训练配置（原文第 3 节 YAML，逐字还原）

| 字段路径 | 取值 | 解读 |
|---|---|---|
| `data.dataset_param.basic_parameters.cutoff_len` | `16384` | 模型核心语言模块接受的最大序列长度；超出即截断。原文建议构造数据时**手动计算图文序列总长**并尽量接近该值，避免图片占位符被截断导致训练异常。 |
| `data.dataset_param.basic_parameters.dataset_dir` | `./data/mocked_vl_data` | mock 图像/视频的落盘根目录。 |
| `data.dataset_param.basic_parameters.dataset` | `./data/mocked_vl_data/mock_data_pic_num_10_textlen_16384.json` | 生成的 mock 描述 JSON；命名规则携带 `pic_num` 与 `textlen` 信息，便于追溯构造参数。 |
| `data.dataset_param.basic_parameters.max_samples` | `null` | 同表 A；快速验证时可设小值。 |

### 表 F — LLaVA 原始风格（转换前）字段说明（原文 2.3 节）

| 字段 | 含义 |
|---|---|
| `image` | 图片路径键；包含图片时必须保留，纯文本数据可去除。 |
| `conversations` | 对话数组，每轮含 `from` 与 `value`。 |
| `from` | 角色字段，取值 `human` / `gpt`。 |
| `value` | 内容字段，用户问题或助手回答。 |

---

## 【公式解读】

原文无 LaTeX 公式或伪代码公式。文档中的"参数关系"是文本性提示："构造数据的图文序列长度占比及总长度尽可能与 cutoff_len 数值接近"，不是数学公式，故本节写 **"原文无公式"**。

---

## 【关联】

文档中提及的关联模块与示例入口：

- **数据转换脚本**：`mindspeed_mm/fsdp/tools/data_tool/llava_instruct_2_mllm_demo_format.py` — 把 LLaVA 风格 JSON 转 mllm 目标格式。
- **mock 数据生成脚本**：`mindspeed_mm/fsdp/tools/data_tool/generate_mock_data_for_vlmodel.py` — 受控生成虚构数据。
- **格式参照上游**：[LLaMAFactory](https://github.com/hiyouga/LLaMAFactory) — 多模态 ShareGPT 风格来源。
- **覆盖的 VL 模型示例**（均链接到 `examples/` 目录下的具体模型 README）：
  - [Qwen3.6](../../../examples/qwen3_6)
  - [Qwen3.5](../../../examples/qwen3_5)
  - [Qwen3VL](../../../examples/qwen3vl)
  - [Qwen2.5VL](../../../examples/qwen2.5vl)
  - [GLM4.5V](../../../examples/glm4.5v)
  - [Kimi-K2.5](../../../examples/kimik2_5)
  - [Step3-VL](../../../examples/step3_vl)
- **下游依赖**：训练入口通过 `xxx_config.yaml` 的 `data.dataset_param.basic_parameters` 段读取本文产出的 JSON 与图像目录；不同模型 README 会在其专属配置中引用本文档说明的数据路径约定。
- **章节锚点**：`<a id="real-data"></a>` 与 `<a id="mock-data"></a>` 是文档内章节定位锚，便于 README 等上游文件跳转引用。

---

## 【使用方法】

### 真实数据通路

1. 下载 COCO2017 到 `./data/COCO2017`；下载 LLaVA-Instruct-150K 到 `./data/llava_instruct_150k.json`。
2. 执行格式转换：
   ```shell
   python mindspeed_mm/fsdp/tools/data_tool/llava_instruct_2_mllm_demo_format.py \
       --coco_path ./data/COCO2017 \
       --llava_json_path ./data/llava_instruct_150k.json \
       --output_json_path ./data/mllm_format_llava_instruct_data.json
   ```
3. 在 `xxx_config.yaml` 中设置 `dataset_dir` 与 `dataset`（多数据集以英文逗号无空格拼接）；可选 `max_samples: null`（全量）或具体数字。
4. 其他原始格式数据集可仿照 `llava_instruct_2_mllm_demo_format.py` 自行编写转换脚本。

### mock 数据通路

1. 配置 Ascend 环境变量：
   ```shell
   source /usr/local/Ascend/ascend-toolkit/set_env.sh
   ```
2. 构造 mock 数据（原文示例：1024×1024 图 × 10 张/样本、文本长度 16384、512 条样本）：
   ```shell
   SAVE_DIR=./data/mocked_vl_data/
   mkdir -p $SAVE_DIR
   python mindspeed_mm/fsdp/tools/data_tool/generate_mock_data_for_vlmodel.py \
       --tokenizer_path /home/weights/Qwen3.5-35B-A3B/ \
       --pic_width 1024 \
       --pic_height 1024 \
       --num_pics 10 \
       --text_length 16384 \
       --num_samples 512 \
       --save_dir $SAVE_DIR
   ```
3. 在 `xxx_config.yaml` 中设置 `cutoff_len: 16384`（与 `--text_length` 对齐）、`dataset_dir: ./data/mocked_vl_data`、`dataset: &DATASET_PATH ./data/mocked_vl_data/mock_data_pic_num_10_textlen_16384.json`。

> 备注：原文未涉及具体的训练启动命令/分布式配置开关/混合精度设置等；这些应在各模型示例（如 `examples/qwen3vl`、`examples/qwen2.5vl` 等）的 README 中查看。
