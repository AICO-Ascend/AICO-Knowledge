# VBench Evaluate

> 仓 `mindspeed-mm` · 路径 `docs/zh/features/vbench-evaluate.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-mm/docs/zh/features/vbench-evaluate.md

# VBench Evaluate 深度解读

## 【定位】
本篇文档面向 mindspeed-mm 套件中的视频生成模型，提供基于 VBench 评测框架的**端到端自动化评测指南**，覆盖 **t2v（文生视频）、i2v（图生视频）、long（≥5 秒长视频）三种场景**的评测维度配置、数据准备、环境安装与脚本启动方法。

---

## 【技术要点】

1. **三种评测场景的明确边界**：t2v 与 long 共用一套数据/配置体系，以视频时长 **5 秒** 为分界（`eval_type` 决定）；i2v 走独立的图-文-视频三元组数据通道。
2. **固定依赖版本约束**：vbench==0.1.5、transformers==4.45.0、scenedetect==0.6.5.2、av==13.1.0、moviepy==1.0.3、dreamsim==0.2.1、cloudpickle==3.1.1、imageio_ffmpeg==0.5.1、portalocker==2.8.2、timm==1.0.8；detectron2 需从 facebookresearch 官方 Git 仓库安装。
3. **源码文件补齐**：需将 `vbench2_beta_i2v/third_party` 与 `vbench2_beta_long/configs` 从 VBench 源码目录 `cp -r` 至 site-packages 对应目录，否则模型推理子模块缺失。
4. **i2v 图片比例白名单**：`extra_param.ratio` 仅支持 `1-1`、`8-5`、`7-4`、`16-9` 四种。
5. **dataloader 强制一致性**：`drop_last=false` 用以保证所有 prompt 都参与生成；三个场景的 `dataloader_param` 字段完全一致（除 i2v 多出 `image_path`）。
6. **维度（dimensions）按场景分流**：t2v/long 共用 16 个维度；i2v 为 10 个维度（含 `i2v_subject`、`i2v_background`、`camera_motion` 等专用维度）。

---

## 【关键机制与数据】

- **评测入口实现**：`evaluation_impl: "vbench_eval"` 表明 mindspeed-mm 调用 VBench 库作为后端评测实现；被评测模型由 `evaluation_model: "cogvideox-1.5"` 指定（原文以 cogvideox-1.5 为示例，可按需替换）。
- **t2v/long 数据流**：`data_path` 指向 `$VBench_full_info.json` 元信息文件，`data_folder` 指向 `$vbench_prompts` 目录（含 `prompts_per_dimension/`、`augmented_prompts/` 等子目录）。`augment=false` 时使用 `prompt_file`（默认 `all_dimension.txt`，英文全维度）；`augment=true` 时切换至 `augmented_prompt_file`（默认 `all_dimension_longer.txt`，GPT 强化版）。
- **long 模式关键开关**：需额外提供 `long_eval_config` 字段，指向 vbench 安装后 `vbench2_beta_long` 的路径；否则会报模块缺失。
- **i2v 数据流**：以图-文对组织，`data_folder` 指向 `$vbench_i2v` 根目录，内含 `data/crop/<ratio>/` 与 `data/origin/` 两级；`image_path` 单独指向 `$vbench_i2v_crop`，与 `ratio` 配合完成裁剪子集筛选。
- **数据增强机制**：原文出现 `augment`（bool）、`prompt_file`、`augmented_prompt_file` 三个联动字段，构成「是否启用 GPT 强化 prompt + 用哪个维度文件」的二选一开关；当 `dimensions` 为空列表时，`prompt_file` 还会作为生成视频的文件名前缀。

> 原文未给出实测性能数据（如单卡吞吐、维度得分均值等），故不臆造。

---

## 【表格解读】

### 表 1：t2v / long 场景评测配置参数表（逐字还原 `eval_model_t2v_1.5.json`）

| 字段层级 | 字段名 | 取值 | 说明 |
|---|---|---|---|
| eval_config.dataset.type | dataset.type | `vbench_eval` | 表示 t2v / long 场景 |
| eval_config.dataset.basic_param.data_path | basic_param.data_path | `$VBench_full_info.json` | 元信息 JSON 路径 |
| eval_config.dataset.basic_param.data_folder | basic_param.data_folder | `$vbench_prompts` | prompt 根目录 |
| eval_config.dataset.basic_param.return_type | basic_param.return_type | `list` | 返回类型 |
| eval_config.dataset.basic_param.data_storage_mode | basic_param.data_storage_mode | `standard` | 数据存储模式 |
| eval_config.dataset.extra_param.augment | extra_param.augment | `false` | 数据增强开关，开启后使用强化 prompt |
| eval_config.dataset.extra_param.prompt_file | extra_param.prompt_file | `all_dimension.txt` | dimension 为空列表时的视频文件前缀；默认英文全维度 |
| eval_config.dataset.extra_param.augmented_prompt_file | extra_param.augmented_prompt_file | `augmented_prompts/gpt_enhanced_prompts/all_dimension_longer.txt` | augment=true 且 dimension 为空时使用；默认 GPT 强化英文全维度 |
| eval_config.dataloader_param.dataloader_mode | dataloader_param.dataloader_mode | `sampler` | dataloader 模式 |
| eval_config.dataloader_param.sampler_type | dataloader_param.sampler_type | `SequentialSampler` | 采样器类型 |
| eval_config.dataloader_param.shuffle | dataloader_param.shuffle | `true` | 是否打乱 |
| eval_config.dataloader_param.drop_last | dataloader_param.drop_last | `false` | 关闭 drop_last 保证所有 prompt 都生成视频 |
| eval_config.dataloader_param.pin_memory | dataloader_param.pin_memory | `true` | pin_memory |
| eval_config.dataloader_param.group_frame | dataloader_param.group_frame | `false` | 是否按帧数分组 |
| eval_config.dataloader_param.group_resolution | dataloader_param.group_resolution | `false` | 是否按分辨率分组 |
| eval_config.dataloader_param.collate_param | dataloader_param.collate_param | `{}` | collate 参数 |
| eval_config.dataloader_param.prefetch_factor | dataloader_param.prefetch_factor | `4` | 预取因子 |
| eval_config.evaluation_model | evaluation_model | `cogvideox-1.5` | 被评测模型 |
| eval_config.evaluation_impl | evaluation_impl | `vbench_eval` | 使用 vbench 评测 |
| eval_config.eval_type | eval_type | `t2v` | t2v 或 long，以 5 秒为界 |
| eval_config.load_ckpt_from_local | load_ckpt_from_local | `true` | 从本地加载权重 |
| eval_config.long_eval_config | long_eval_config | `path_to_long_eval_configs` | eval_type=long 时需配置，指向 vbench 安装后 vbench2_beta_long 路径 |
| eval_config.dimensions | dimensions | 见下方「表 4」 | 评测维度配置 |

**逐行解读**：该表是 t2v/long 评测的「数据 + 调度 + 模型」三段式配置。`basic_param` 负责定位元信息与 prompt 目录；`extra_param` 引入 `augment` 三态开关控制 prompt 注入策略；`dataloader_param` 与训练侧一致，但强制 `drop_last=false` 以避免尾部 prompt 被丢弃导致维度统计不全；`evaluation_model/evaluation_impl/eval_type` 共同确定走 cogvideox-1.5 + VBench 后端；`long_eval_config` 是 long 模式的唯一外部依赖入口。

---

### 表 2：i2v 场景评测配置参数表（逐字还原 `eval_model_i2v_1.5.json`）

| 字段层级 | 字段名 | 取值 | 说明 |
|---|---|---|---|
| eval_config.dataset.type | dataset.type | `vbench_i2v` | 数据集合类型，适用于 i2v |
| eval_config.dataset.basic_param.data_path | basic_param.data_path | `$vbench2_i2v_full_info.json` | i2v_full_info 文件路径 |
| eval_config.dataset.basic_param.data_folder | basic_param.data_folder | `$vbench_i2v` | 配置根路径 |
| eval_config.dataset.basic_param.return_type | basic_param.return_type | `list` | 返回类型 |
| eval_config.dataset.basic_param.data_storage_mode | basic_param.data_storage_mode | `standard` | 数据存储模式 |
| eval_config.dataset.extra_param.ratio | extra_param.ratio | `16-9` | 图片比例，支持 1-1、8-5、7-4、16-9 四种 |
| eval_config.dataloader_param | dataloader_param | 同表 1 | 与 t2v/long 一致 |
| eval_config.evaluation_model | evaluation_model | `cogvideox-1.5` | 被评测模型 |
| eval_config.evaluation_impl | evaluation_impl | `vbench_eval` | 使用 vbench 评测 |
| eval_config.eval_type | eval_type | `i2v` | 评测场景 i2v |
| eval_config.load_ckpt_from_local | load_ckpt_from_local | `true` | 从本地加载权重 |
| eval_config.dimensions | dimensions | `["subject_consistency"]`（示例）/见表 4 | 评测维度配置 |
| eval_config.image_path | image_path | `$vbench_i2v_crop` | 原始图片路径 |

**逐行解读**：i2v 与 t2v/long 的差异点集中在三处：① `dataset.type=vbench_i2v` 触发图生视频数据通道；② 新增 `ratio` 与 `image_path` 字段，分别从数据集维度和原始图片维度定位裁剪后子集；③ 去掉了 `augment/prompt_file/augmented_prompt_file/long_eval_config`，因为 i2v 不使用 prompt 增强，也不参与 long 模式。

---

### 表 3：i2v 数据集目录结构表

| 路径层级 | 类型 | 内容 |
|---|---|---|
| `$vbench_i2v/data/crop` | 目录 | 各比例裁剪后的图片集，`$vbench_i2v_crop` 指向此处 |
| `$vbench_i2v/data/crop/<ratio>` | 目录 | 如 `1-1`、`7-4`、`16-9` 等比例子目录 |
| `$vbench_i2v/data/crop/<ratio>/<file>.jpg` | 文件 | 单张图片，如 `a bald eagle flying over a tree filled forest.jpg` |
| `$vbench_i2v/data/origin` | 目录 | 原始图片 |
| `$vbench_i2v/vbench2_i2v_full_info.json` | 文件 | 元信息 JSON，路径变量为 `$vbench2_i2v_full_info.json` |

**逐行解读**：原始素材以「比例 × 文件名」二维组织，`extra_param.ratio` 在此完成子集筛选；`vbench2_i2v_full_info.json` 同时被 `data_path` 与目录结构顶层共用，是数据流的唯一元信息入口。

---

### 表 4：三种场景支持维度对比表（逐字还原 `dimensions` 列表）

| 评测类型 | 支持维度 |
|---|---|
| t2v | `subject_consistency`, `background_consistency`, `aesthetic_quality`, `imaging_quality`, `object_class`, `multiple_objects`, `color`, `spatial_relationship`, `scene`, `temporal_style`, `overall_consistency`, `human_action`, `temporal_flickering`, `motion_smoothness`, `dynamic_degree`, `appearance_style` |
| i2v | `subject_consistency`, `background_consistency`, `aesthetic_quality`, `imaging_quality`, `temporal_flickering`, `motion_smoothness`, `dynamic_degree`, `i2v_subject`, `i2v_background`, `camera_motion` |
| long | 与 t2v 完全一致 |

**逐行解读**：t2v 与 long 共享 16 个维度，差异仅在视频时长；i2v 显著收窄至 10 个维度，并新增 `i2v_subject`（主体一致性）、`i2v_background`（背景一致性）、`camera_motion`（镜头运动）三类图生视频专用度量，去掉了依赖纯文本先验的 `object_class/multiple_objects/color/spatial_relationship/scene/temporal_style/overall_consistency/human_action/appearance_style` 等维度。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **`$vbench_i2v_crop`**：作为 i2v 数据集目录下的裁剪子集路径，被 `eval_config.image_path` 字段直接引用；同时也是 `data/crop/<ratio>/` 二级目录的根，决定了 `extra_param.ratio` 实际筛选的目录层级。
- **`$vbench2_i2v_full_info.json`**：被 `eval_config.dataset.basic_param.data_path` 字段引用，是 i2v 元信息文件入口；与 `data/data_path` 配合形成「元信息 + 真实图片」双通道。
- **VBench GitHub 仓库**：本文档所有数据（`VBench_full_info.json`、`vbench2_i2v_full_info.json`、prompts、long json）与源码文件（`vbench2_beta_i2v/third_party`、`vbench2_beta_long/configs`）均从 `https://github.com/Vchitect/VBench` 下载或复制，是外部依赖源。
- **`cogvideox-1.5`**：`evaluation_model` 字段默认指向 cogvideox-1.5，是本评测在 mindspeed-mm 中的具体落地模型；启动脚本位于 `examples/cogvideox/i2v_1.5/` 与 `examples/cogvideox/t2v_1.5/`，表明该评测与 CogVideoX 推理链路强耦合。
- **「推理-配置参数」章节**：「权重及模型文件配置」一节指向此章节，用于补齐 `eval_cogvideox_i2v_1.5.sh` 与 `eval_model_i2v_1.5.json` 中的模型与权重路径，是本文档的同级上游依赖。
- **`examples/cogvideox/i2v_1.5/eval_cogvideox_i2v_1.5.sh` / `examples/cogvideox/t2v_1.5/eval_cogvideox_t2v_1.5.sh`**：i2v、t2v、long 三种模式的启动入口；long 模式复用 t2v 启动脚本，仅需修改配置文件中的 `eval_type`。

---

## 【使用方法】

### 启动命令

| 场景 | 命令 |
|---|---|
| i2v | `bash examples/cogvideox/i2v_1.5/eval_cogvideox_i2v_1.5.sh` |
| t2v | `bash examples/cogvideox/t2v_1.5/eval_cogvideox_t2v_1.5.sh` |
| long | 修改 `examples/cogvideox/t2v_1.5/eval_model_t2v_1.5.json` 中的 `eval_type` 为 `long`，再执行 `bash examples/cogvideox/t2v_1.5/eval_cogvideox_t2v_1.5.sh` |

### 关键配置项

- **`evaluation_impl`**：固定为 `vbench_eval`，决定走 VBench 后端。
- **`evaluation_model`**：默认 `cogvideox-1.5`，需根据实际被评测模型替换。
- **`eval_type`**：`t2v` / `i2v` / `long` 三选一；`long` 以 5 秒为时长分界。
- **`dimensions`**：按表 4 选择对应场景的支持维度，可配置多个。
- **`load_ckpt_from_local`**：固定 `true`，从本地加载权重。
- **`long_eval_config`**：`eval_type=long` 时必填，指向 vbench 安装后的 `vbench2_beta_long` 路径。
- **`extra_param.augment` / `prompt_file` / `augmented_prompt_file`**（仅 t2v/long）：prompt 注入策略三态开关。
- **`extra_param.ratio`**（仅 i2v）：图片比例，`1-1`、`8-5`、`7-4`、`16-9` 四选一。
- **`image_path`**（仅 i2v）：指向 `$vbench_i2v_crop`。
- **`data_path` / `data_folder`**：分别指向元信息 JSON 与 prompt/图片根目录。

### 环境前置

- 先按 README 完成 mindspeed-mm 基础环境安装；
- 再 `pip install` 文档列出的固定版本依赖包，并从 facebookresearch 安装 detectron2；
- 从 VBench 源码 `cp -r vbench2_beta_i2v/third_party` 与 `vbench2_beta_long/configs` 至 site-packages 对应目录。

### 数据集准备

- **t2v/long**：下载 `VBench_full_info.json` 至 `$VBench_full_info.json`，下载 prompts 至 `$vbench_prompts`。
- **i2v**：下载 `vbench2_i2v_full_info.json` 至 `$vbench2_i2v_full_info.json`，下载 Google Drive 图片集解压后按 `data/crop/<ratio>/` 与 `data/origin/` 组织。
- **long**：额外下载 long 场景专用 JSON `VBench_full_info.json`（vbench2_beta_long 分支）。
