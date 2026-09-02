# 快速入门：Qwen2.5-VL模型微调和Wan2.1模型微调

> 仓 `mindspeed-mm` · 路径 `docs/zh/pytorch/quickstart.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-mm/docs/zh/pytorch/quickstart.md

# MindSpeed MM 快速入门文档深度解读

## 【定位】

本文档是 MindSpeed MM 套件的快速入门指南，针对**多模态理解（Qwen2.5-VL-3B）**和**多模态生成（Wan2.1-T2V-1.3B）**两类典型模型，提供在昇腾 NPU 单机场景下完成"环境准备→权重下载转换→数据预处理→启动微调→后续处理"完整流程的操作指引，帮助开发者快速上手预置模型在 NPU 上的高效运行。

---

## 【技术要点】

1. **支持硬件与基础环境**：支持 Ascend 950 系列产品、Atlas A3 训练系列产品和 Atlas A2 训练系列产品，**单 NPU 片上内存 ≥64GB**；框架基于 PyTorch + Python 3.12；单节点示例使用 **NPUS_PER_NODE=8**。
2. **权重双向转换机制**：MindSpeed MM 修改了原始网络结构名称，需通过 `mm-convert` 工具实现 `hf_to_mm`（微调前）与 `mm_to_hf`（微调后）双向转换；Qwen2.5-VL 使用 `Qwen2_5_VLConverter`，Wan2.1 使用 `WanConverter`。
3. **PP/TP 切分参数一致性约束**：Qwen2.5-VL 权重转换时 `llm_pp_layers=[[36]]`、`vit_pp_layers=[[32]]`、`tp_size=1`，这些值必须与 `examples/qwen2.5vl/model_3b.json` 中 `pipeline_num_layers` 和微调启动脚本保持一致。
4. **理解模型数据链路**：COCO2017 图片 + LLaVA-Instruct-150K 描述 → 通过 `llava_instruct_2_mllm_demo_format.py` 脚本转为 `mllm_format_llava_instruct_data.json` → `examples/qwen2.5vl/data_3b.json` 中配置 dataset_dir/dataset/cache_dir。
5. **生成模型数据链路**：Wan2.1 依赖 Diffusers `0.33.1` + Decord `0.6.0`（X86）或 apt/yum 安装（ARM）；数据结构为视频-文本对（path/cap/num_frames=81/fps/resolution），需执行特征提取流程。
6. **分布式启动参数固化**：MASTER_ADDR=localhost、MASTER_PORT=29501、NNODES=1、NODE_RANK=0、WORLD_SIZE=NPUS_PER_NODE×NNODES，需先 `source /usr/local/Ascend/cann/set_env.sh` 激活 CANN 环境。

---

## 【关键机制与数据】

- **原文：权重名称重命名机制** — "MindSpeed MM 修改了部分原始网络的结构名称，可使用 `mm-convert` 工具对原始权重进行转换"，因此微调前后都需进行格式互转，才能保证与 Hugging Face 生态兼容。
- **原文：Qwen2_5_VL 与 Qwen2_VL 共用转换逻辑** — "由于 Qwen2_5_VL 和 Qwen2_VL 在权重转换逻辑上保持一致"、"在数据转换逻辑上保持一致"，因此可直接复用 Qwen2_VL 的 `mm-convert` 工具与 `llava_instruct_2_mllm_demo_format.py` 通用脚本。
- **原文：分布式 checkpoint IO 代价** — "由于分布式优化器保存文件较大，导致耗时较长，请谨慎设置保存间隔"，示例脚本默认 `--save-interval 5000`、`--log-interval 1`。
- **原文：多机 cache_dir 隔离要求** — "为了避免写入同一个文件导致冲突的问题，在多机上不要配置同一个挂载目录(`cache_dir`)"。
- **原文：OOM 风险阈值** — "当前示例脚本中 `NPUS_PER_NODE=8` 表示需要 8 个 NPU，如果实际情况低于此配置，可能遇到 OOM 问题"。
- **原文：吞吐统计开关** — "`--log-tps` 增加此参数可使能在训练中打印每步语言模块的平均序列长度，并在训练结束后计算每秒吞吐 tokens 量"。
- **原文：Wan2.1 特征采样规则** — "`num_frames`：表示最大帧数，默认为 81，超过则随机选取其中的 `num_frames` 帧"（原文在"特征提取"小节被截断）。

---

## 【表格解读】

### 表 1 — Qwen2.5-VL 权重转换工具参数（hf_to_mm）

|参数|说明|是否必选|默认值|
|-|-|-|-|
|Qwen2_5_VLConverter|Qwen2.5-VL模型转换工具|是|/|
|hf_to_mm|Hugging Face模型转换MindSpeed MM模型权重|是|/|
|mm_dir|转换后保存目录|是|/|
|hf_dir|Hugging Face权重目录|是|/|
|llm_pp_layers|llm在每个卡上切分的层数，注意要和examples/qwen2.5vl/model_3b.json中配置的pipeline_num_layers一致|否|36|
|vit_pp_layers|vit在每个卡上切分的层数，注意要和examples/qwen2.5vl/model_3b.json中配置的pipeline_num_layers一致|否|32|
|tp_size|TP并行数量，注意要和微调启动脚本中的配置一致|否|1|

**逐行解读**：前 4 行为必选核心参数，指定转换器类型、转换方向、源/目标目录；后 3 行为可选并行配置，`llm_pp_layers=36` 与 `vit_pp_layers=32` 需与 `model_3b.json` 中 `pipeline_num_layers` 保持一致，`tp_size=1` 需与启动脚本一致；任何不一致都会导致权重 shape 错配。

### 表 2 — `data_3b.json` 数据集参数

|参数|说明|取值|
|-|-|-|
|model_name_or_path|权重|"./ckpt/hf_path/Qwen2.5-VL-3B-Instruct"，与[权重下载及转换](#权重下载及转换)中的`hf_config.hf_dir`一致。|
|dataset_dir|数据集目录|"./data"|
|dataset|数据集|"./data/mllm_format_llava_instruct_data.json"|

**逐行解读**：`model_name_or_path` 指向 Hugging Face 原始权重目录（不是 mm 转换后的目录），用于 tokenizer/processor 加载；`dataset_dir` 与 `dataset` 路径必须与数据预处理产出的 `mllm_format_llava_instruct_data.json` 对齐。

### 表 3 — 微调启动脚本参数

|参数|说明|取值|
|-|-|-|
|LOAD_PATH|加载路径|ckpt/mm_path/Qwen2.5-VL-3B-Instruct|
|SAVE_PATH|保存路径|save_dir|
|`--log-interval`|日志间隔|1|
|`--save-interval`|保存间隔|5000|
|`--no-load-optim`|不加载优化器状态，若需加载请移除|/|
|`--no-load-rng`|不加载随机数状态，若需加载请移除|/|
|`--no-save-optim`|不保存优化器状态，若需保存请移除|/|
|`--no-save-rng`|不保存随机数状态，若需保存请移除|/|

**逐行解读**：`LOAD_PATH` 必须是 `mm-convert` 转换后的 mm 格式权重（区别于原始 HF 路径）；`--no-load-optim/--no-load-rng/--no-save-optim/--no-save-rng` 四项开关默认跳过优化器与 RNG 状态的存取以节省 IO，若需断点续训则需移除对应开关。

### 表 4 — `mm_to_hf` 反向转换参数

|参数|含义|是否必选|默认值|
|:----|:----|:----|:----|
|Qwen2_5_VLConverter|Qwen2.5-VL模型转换工具|是|/|
|mm_to_hf|MindSpeed MM模型转换Hugging Face模型权重|是|/|
|save_hf_dir|mm微调后转换回hf模型格式的目录|是|/|
|mm_dir|微调后保存的权重目录|是|/|
|hf_dir|Hugging Face权重目录|是|/|
|llm_pp_layers|llm在每个卡上切分的层数，注意要和微调时model.json中配置的pipeline_num_layers一致|否|36|
|vit_pp_layers|vit在每个卡上切分的层数，注意要和微调时model.json中配置的pipeline_num_layers一致|否|32|
|tp_size|TP并行数量，注意要和微调启动脚本中的配置一致|否|1|

**逐行解读**：与表 1 结构对称，但转换方向相反；`save_hf_dir` 为最终产物，`hf_dir` 为参考的原始 HF 权重结构，`mm_dir` 为微调后产物；三项并行参数需与微调阶段严格对齐。

### 表 5 — Wan2.1 权重转换工具参数

| 参数 |说明 |
| :-- | :--- |
|WanConverter|Wan2.1模型转换工具|
|hf_to_mm|Hugging Face模型转换MindSpeed MM模型权重|
| source_path | 原始权重路径|
| target_path | 转换或切分后权重保存路径|

**逐行解读**：Wan2.1 转换仅作用于 `transformer` 子目录（命令行中显式指定 `./weights/Wan2.1-T2V-1.3B-Diffusers/transformer/`），不涉及 PP/TP 切分参数（默认单机单卡即可），转换路径为 `transformer/` → `transformer_mm/`。

### 视频-文本对参数表（理解模型 data.json 字段）

|参数|说明|默认值|
|-|-|-|
|path|视频存放路径|/|
|cap|视频描述|根据用户实际情况配置|
|num_frames|最大的帧数|81|
|fps|视频帧数|根据用户实际情况配置|
|height|视频高度|根据用户实际情况配置|
|width|视频宽度|根据用户实际情况配置|

**逐行解读**：每个 video-caption 样本声明视频路径、文本描述、最大帧数（81）、原始帧率及分辨率；`num_frames` 超过时按原文规则随机采样。

---

## 【公式解读】

**原文无公式**。

文档中出现的仅为 JSON 配置片段、shell 脚本命令与 Python 脚本路径（如 `python mindspeed_mm/fsdp/tools/data_tool/llava_instruct_2_mllm_demo_format.py`），不涉及数学公式或伪代码公式表达。

---

## 【关联】

- **与 `install_guide.md` 的关系**：两节（Qwen2.5-VL 与 Wan2.1）环境准备的第一步都引用 [MindSpeed MM 安装指导](install_guide.md)，作为环境搭建的入口文档；同时 Wan2.1 在此基础上额外引入 Diffusers 0.33.1 与 Decord 依赖。
- **与 `../features/mm_convert.md` 的关系**：Qwen2.5-VL 的 `hf_to_mm` 与 `mm_to_hf` 两个方向的权重转换都基于 `mm-convert` 命令行工具，原文用 NOTE 指引"更多工具详情可参见[权重转换命令行工具](../features/mm_convert.md)"，表明该工具是 MindSpeed MM 权重格式适配的核心基础设施。
- **与 `../../../examples/qwen2.5vl/README.md` 的关系**：微调主脚本 `examples/qwen2.5vl/finetune_qwen2_5_vl_3b.sh`、数据配置 `examples/qwen2.5vl/data_3b.json`、并行配置 `examples/qwen2.5vl/model_3b.json` 均位于该 examples 目录，是本文档所有命令与配置项的物理落地点。
- **与 `../../../examples/wan2.1/README.md` 的关系**：Wan2.1 转换脚本、数据集目录 `dataset/`、`examples/wan2.1/feature_extract/data.txt` 与 `data.json` 均属于该 examples 目录，是生成模型微调流程的物理落地点。
- **两模型横向关联**：理解与生成两条流程共用同一 `mm-convert` 工具基础设施（仅 converter 类不同：`Qwen2_5_VLConverter` vs `WanConverter`），且都遵循"HF→mm→训练→mm→HF"的镜像对称链路，构成 MindSpeed MM 多模态双能力的产品形态。

---

## 【使用方法】

**原文涉及的关键启用命令与配置项**：

### Qwen2.5-VL 流程
1. 目录准备：
   ```bash
   mkdir logs && mkdir data && mkdir ckpt
   ```
2. 权重转换（hf→mm）：
   ```bash
   mm-convert Qwen2_5_VLConverter hf_to_mm \
     --cfg.mm_dir "ckpt/mm_path/Qwen2.5-VL-3B-Instruct" \
     --cfg.hf_config.hf_dir "ckpt/hf_path/Qwen2.5-VL-3B-Instruct" \
     --cfg.parallel_config.llm_pp_layers [[36]] \
     --cfg.parallel_config.vit_pp_layers [[32]] \
     --cfg.parallel_config.tp_size 1
   ```
3. 数据预处理：
   ```bash
   python mindspeed_mm/fsdp/tools/data_tool/llava_instruct_2_mllm_demo_format.py
   ```
4. 数据配置：编辑 `examples/qwen2.5vl/data_3b.json` 中的 `model_name_or_path` / `dataset_dir` / `dataset` / `cache_dir`。
5. 启动微调：
   ```bash
   bash examples/qwen2.5vl/finetune_qwen2_5_vl_3b.sh
   ```
   脚本内部含 `NPUS_PER_NODE=8`、`MASTER_ADDR=localhost`、`MASTER_PORT=29501`、`NNODES=1`、`NODE_RANK=0`，并 `source /usr/local/Ascend/cann/set_env.sh`。
6. 权重反向转换（mm→hf）：
   ```bash
   mm-convert Qwen2_5_VLConverter mm_to_hf \
     --cfg.save_hf_dir "ckpt/mm_to_hf/Qwen2.5-VL-3B-Instruct" \
     --cfg.mm_dir "ckpt/mm_path/Qwen2.5-VL-3B-Instruct" \
     --cfg.hf_config.hf_dir "ckpt/hf_path/Qwen2.5-VL-3B-Instruct" \
     --cfg.parallel_config.llm_pp_layers [36] \
     --cfg.parallel_config.vit_pp_layers [32] \
     --cfg.parallel_config.tp_size 1
   ```

### Wan2.1 流程
1. 额外依赖：
   ```bash
   pip install diffusers==0.33.1
   pip install decord==0.6.0   # X86；ARM 走 apt/yum
   ```
2. 权重转换（仅 transformer 子目录）：
   ```bash
   mm-convert WanConverter hf_to_mm \
     --cfg.source_path ./weights/Wan2.1-T2V-1.3B-Diffusers/transformer/ \
     --cfg.target_path ./weights/Wan2.1-T2V-1.3B-Diffusers/transformer_mm/
   ```
3. 数据集目录：创建 `dataset/videos/` 与 `dataset/data.json`（按视频-文本对 JSON 模板填写 path/cap/num_frames=81/fps/resolution）。
4. 特征提取（原文在"特征提取"小节被截断，具体 `num_frames`、`max_hei...` 后续参数原文未完整给出，**原文未涉及完整步骤**）。

### 硬件前提
- Ascend 950 / Atlas A3 / Atlas A2 训练系列产品；
- 单 NPU 片上内存 ≥64GB；
- NPUS_PER_NODE=8（不足时存在 OOM 风险）。
