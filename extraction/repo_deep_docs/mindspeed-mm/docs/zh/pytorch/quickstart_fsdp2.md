# 快速入门：Qwen3-VL模型微调

> 仓 `mindspeed-mm` · 路径 `docs/zh/pytorch/quickstart_fsdp2.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-mm/docs/zh/pytorch/quickstart_fsdp2.md

# Qwen3-VL 模型微调 (FSDP2) 快速入门 — 一体化深度解读

---

## 【定位】

这篇文档是 MindSpeed-MM 套件面向多模态理解模型微调的 **FSDP2 框架快速上手指南**，以 Qwen3-VL-30B-A3B-Instruct 为示例，完整跑通"环境准备 → 权重下载/转换 → 数据集准备 → YAML 配置 → 启动微调 → 权重回灌 HF"的全链路，让开发者能够在昇腾 NPU 上一键完成多模态理解模型的高效分布式微调。

---

## 【技术要点】

1. **FSDP2 训练框架**: 采用 PyTorch 原生 FSDP2（Fully Sharded Data Parallel 2），沿数据并行维对参数、梯度、优化器状态做 **全分片**，显著降低单卡显存占用；与模型结构解耦，适配新模型成本低。
2. **训练入口**: 训练器位于 `mindspeed_mm/fsdp/train/trainer.py`，一行 `torchrun` 命令即可启动。
3. **集中化配置**: 一份 YAML 配置文件覆盖 6 个顶层段——`parallel` / `data` / `model` / `features` / `training` / `tools`，无需多文件修改。
4. **权重格式与初始化**: 使用 DCP（PyTorch 分布式检查点）格式，配合 **meta init** 初始化降低峰值显存；**Qwen3-VL-30B / 235B 必须使用 meta init**（仓库默认开启）。
5. **可扩展并行**: 在 FSDP 分片基础上可叠加 **Ulysses 上下文并行**（`ulysses_parallel_size`）与 **MoE 专家并行**（`expert_parallel_size`）。
6. **权重转换工具 `mm-convert`**: 提供 `hf_to_dcp`（HF→DCP，进入训练）与 `dcp_to_hf`（DCP→HF，回灌推理）双向转换；转换产物包含 `release/` 目录与 `latest_checkpointed_iteration.txt`。

---

## 【关键机制与数据】

### 工作原理

- **FSDP2 分片机制**: 沿数据并行维对参数、梯度、优化器状态做全分片，单卡显存占用随分片组大小下降；与模型结构解耦，使得新增模型仅需在 `fsdp_plan.apply_modules` 中声明需要分片的模块路径（如 `model.visual.blocks.{*}`、`model.language_model.layers.{*}`、`lm_head` 等）即可。
- **meta init 路径**: meta init 先以元数据占位模型结构、不分配实际显存，待加载 DCP 权重时再按需 materialize，从而显著降低启动峰值显存。原文：「使用 meta init 初始化时需要 DCP 权重……**Qwen3-VL-30B / 235B 必须使用 meta init，仓库默认开启**」。
- **数据流**: COCO2017 图像 + LLaVA-Instruct-150K 描述 → `llava_instruct_2_mllm_demo_format.py` 脚本 → 生成 `mllm_format_llava_instruct_data.json`（mllm 格式）→ 由 `data` 段的 `dataset_dir` / `dataset` 字段定位加载。
- **精度配置**: FSDP 内部 `param_dtype: bf16`（参数与计算精度）、`reduce_dtype: fp32`（梯度归约精度），可在不损失训练稳定性的前提下节省显存。

### 硬件与启动规模（原文摘录）

- 支持 **Ascend 950 系列产品、Atlas A3 训练系列产品、Atlas A2 训练系列产品**。
- 要求 **单 NPU 片上内存 ≥ 64GB**。
- 示例脚本默认 `NPUS_PER_NODE=16`（即需要 16 张 NPU），若低于该配置可能遇到 OOM。

### 性能数据

原文未提供实测吞吐/加速比等性能数据，仅有"显著降低单卡显存占用"等定性描述。

---

## 【表格解读】

### 表 1：权重转换工具参数解析（`hf_to_dcp` 子命令）

| 参数 | 说明 | 是否必选 | 默认值 |
|---|---|---|---|
| `GenericDCPConverter` | Qwen3-VL 模型转换工具 | 是 | / |
| `hf_to_dcp` | Hugging Face 模型转换 MindSpeed MM 模型权重 | 是 | / |
| `dcp_dir` | 转换后保存目录 | 是 | / |
| `hf_dir` | Hugging Face 权重目录 | 是 | / |

**逐行解读**：
- `GenericDCPConverter`：转换器名称，是调用 `mm-convert` 时第一个位置参数，标识使用通用 DCP 转换器。
- `hf_to_dcp`：子命令，指定将 HF 格式转换为 DCP 格式（HF → DCP 的"入训"方向）。
- `dcp_dir`：转换后的 DCP 权重保存目录，本例为 `./ckpt/Qwen3-VL-30B-A3B-Instruct-dcp`，该目录下会生成 `release/` 文件夹与 `latest_checkpointed_iteration.txt`。
- `hf_dir`：原始 HF 权重目录，本例为 `./ckpt/Qwen3-VL-30B-A3B-Instruct`。所有参数均为必选，无默认值。

---

### 表 2：必改字段清单

| 所在段 | 字段 | 改成 |
|---|---|---|
| `data` | `model_name_or_path` | 转换前的**原始 HF 权重**路径，即 `./ckpt/Qwen3-VL-30B-A3B-Instruct` |
| `data` | `dataset_dir` | 数据集根目录，即 `./data` |
| `data` | `dataset` | 预处理后的 `./data/mllm_format_llava_instruct_data.json` |
| `training` | `load` | 转换出的 **DCP 权重**路径 `./ckpt/Qwen3-VL-30B-A3B-Instruct-dcp`（默认注释，meta init 时取消注释并填写） |
| `training` | `init_model_with_meta_device` | `true`（默认已开；30B/235B 必须） |
| `training` | `save` / `save_interval` | 权重保存路径与间隔 |
| `features` | `loss_type` | loss 计算方式（`default` 等，见下） |

**逐行解读**：
- `data.model_name_or_path`：使用 **HF 原始权重路径**（注意：此处不要写 DCP 目录）。
- `data.dataset_dir` / `data.dataset`：分别定位数据集根目录与预处理后的 mllm 格式标注文件。
- `training.load`：指向 DCP 权重目录（写到 `release` 的上一级），仅在开启 meta init 时启用。
- `training.init_model_with_meta_device`：开启 meta init 开关，30B/235B 模型必需。
- `training.save` / `save_interval`：控制训练过程中 DCP 权重的输出位置与保存频率。
- `features.loss_type`：默认 `default`；若需按样本（per-sample）或按 token（per-token）归一等自定义方式，需调整该字段。

---

## 【公式解读】

原文无公式。

---

## 【关联】

根据文档内出现的内部链接，建立如下上下游关联：

1. **环境准备 → 安装指导**: 文档首节"环境准备"指引读者参考 [MindSpeed MM 安装指导](install_guide.md)，用于完成 PyTorch 框架与 Python 3.12 的训练环境搭建。这是启动微调的前置依赖。
2. **DCP → HF 回灌 → HF 推理**: 文档末尾"后续处理"小节完成训练后 DCP 权重转回 HF 格式，以便 HuggingFace/Transformers 加载，形成"HF 权重 → DCP 训练 → DCP 权重 → HF 权重回灌"的完整闭环。
3. **全参数微调 → LoRA 低成本微调**: 文档最后一句"如只想低成本微调，可改用 LoRA"，并指向 [LoRA 微调（FSDP2）](../features/lora_finetune_fsdp2.md)，说明本文档的全参数微调与 LoRA 微调共享同一套 FSDP2 框架底座，LoRA 是其轻量替代方案。

模块关系图（文字版）：

```
install_guide.md (环境依赖)
        ↓
本文档 FSDP2 全参数微调 (Qwen3-VL-30B)
        ↓                          ↘
mm-convert dcp_to_hf (回灌 HF)    lora_finetune_fsdp2.md (LoRA 轻量替代)
```

---

## 【使用方法】

### 1. 环境与目录准备（原文摘录）

```bash
# 1) 安装 PyTorch + Python 3.12 环境（详见 install_guide.md）
# 2) 创建目录
mkdir logs
mkdir data
mkdir ckpt
```

### 2. 权重下载与转换（原文摘录）

```bash
# 从 HF 下载 Qwen3-VL-30B-A3B-Instruct 至 ckpt/Qwen3-VL-30B-A3B-Instruct/

# HF → DCP 转换
mm-convert GenericDCPConverter hf_to_dcp \
  --hf_dir ckpt/Qwen3-VL-30B-A3B-Instruct \
  --dcp_dir ckpt/Qwen3-VL-30B-A3B-Instruct-dcp
```

### 3. 数据集准备（原文摘录）

```bash
# 下载 COCO2017 至 data/COCO2017/
# 从 HF 下载 LLaVA-Instruct-150K 描述文件至 ./data/

# 数据预处理（Qwen2-VL / Qwen3-VL 通用）
python mindspeed_mm/fsdp/tools/data_tool/llava_instruct_2_mllm_demo_format.py
```

### 4. YAML 配置（关键配置项，原文摘录）

- 配置文件：`examples/qwen3vl/qwen3vl_30B_config_v1.yaml`
- `parallel.fsdp_plan.apply_modules`：声明需要 fully_shard 分片的模块（如 `model.visual.blocks.{*}`、`model.language_model.layers.{*}`、`lm_head`）
- `parallel.fully_shard_parallel_size: auto`（按全局卡数自动设定 FSDP 全分片组大小）
- `parallel.param_dtype: bf16`、`parallel.reduce_dtype: fp32`
- `parallel.ulysses_parallel_size: 1`、`parallel.expert_parallel_size: 1`
- `training.init_model_with_meta_device: true`（30B/235B 必须）
- `training.load`：指向 DCP 权重目录（默认注释，meta init 时取消注释）

### 5. 启动脚本与微调（原文摘录）

```bash
# examples/qwen3vl/finetune_qwen3vl_30B_v1.sh 关键变量
source /usr/local/Ascend/ascend-toolkit/set_env.sh
NPUS_PER_NODE=16
MASTER_ADDR=localhost
MASTER_PORT=6000
NNODES=1
NODE_RANK=0

# 启动
bash examples/qwen3vl/finetune_qwen3vl_30B_v1.sh
# 日志输出到 logs/，权重保存到 YAML 中 training.save 指定的目录
```

### 6. 训练后回灌 HF（原文摘录）

```bash
mm-convert GenericDCPConverter dcp_to_hf \
  --load_dir save_dir/release \
  --save_dir save_dir_hf \
  --model_assets_dir ./ckpt/Qwen3-VL-30B-A3B-Instruct
```

参数说明：
- `--load_dir`：训练保存目录下存放 DCP 分片的目录（`training.save` 路径下的 `release`，按实际保存结构填写）
- `--save_dir`：导出的 HF 权重输出目录
- `--model_assets_dir`：原始 HF 权重目录，用于复制 `config`/`tokenizer` 等资产
- 完整参数以 `mm-convert GenericDCPConverter dcp_to_hf -h` 为准

### 7. 轻量替代方案

如只需低成本微调，可改用 LoRA，参见 [LoRA 微调（FSDP2）](../features/lora_finetune_fsdp2.md)。
