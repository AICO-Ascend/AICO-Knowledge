# 快速开始

> 仓 `flashgen` · 路径 `docs/quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/flashgen/docs/quick_start.md

# FlashGen 快速开始 深度解读

---

## 【定位】

本文档是 FlashGen（基于昇腾 NPU 的多模态生成 DMD2 步数蒸馏训练套件）在 Atlas 800 / Ascend 910B 平台上的**端到端上手指南**，覆盖从环境准备、依赖安装、预训练模型获取、离线 negative prompt 编码、数据准备、单/多卡训练启动、checkpoint 导出到 VBench 基准评测的完整 8 步流程。

---

## 【技术要点】

1. **硬件/软件基线（昇腾 NPU 专用）**：昇腾 Atlas 800 训练服务器（Ascend 910B）或更高版本；CANN ≥ 8.5.0；Python ≥ 3.10；torch / torch_npu ≥ 2.7.1；FastVideo = 0.2.0。
2. **FastVideo 必须以 `--no-deps` 安装**：FastVideo 的 `pyproject.toml` 默认会拉取 CUDA 版 `torch==2.11.0` 和 CUDA-only `fastvideo-kernel`，在昇腾环境会覆盖 `torch_npu` 或安装失败；正确做法是先备好 NPU 版 `torch`/`torch_npu`，再用 `pip install -e . --no-deps`，其余纯 Python 依赖（transformers、diffusers、einops 等）按需手动安装。
3. **三角色共用同一预训练权重**：Student / Teacher / Critic 三个角色在 YAML 中分别配置 `init_from`，均指向 `/path/to/Wan2.1-T2V-1.3B-Diffusers`；同时三个角色的 `negative_prompt_embeds_path` 必须指向同一个离线编码目录。
4. **离线编码 negative prompt**：通过 `scripts/encode_negative_prompt.py` 预先编码，避免训练时各 rank 的 collective 死锁。
5. **两种 rollout 模式**：`data_latent`（默认）Student 起点为真实 VAE latent 加噪，需真实 latent 和文本条件；`simulate` 起点为纯随机噪声，不需要真实 latent，但仍要文本条件和批次元数据。
6. **DMD2 蒸馏步数可配置**：通过 `--method.dmd_denoising_steps "[1000, 750, 500, 250]"` 列表形式指定（JSON 风格）；checkpoint 以 DCP 格式保存，通过 `scripts/dcp_to_diffusers.py` 导出为 Diffusers 格式；评测入口 `benchmark.py evaluate` 仅依赖标准视频目录，可通用评测 DMD2 或其他算法结果。

---

## 【关键机制与数据】

**工作原理 / 数据流（基于原文）：**

- **训练循环复用**：FlashGen 复用 FastVideo 的训练循环和数据管线，原文明确 "FlashGen 复用 FastVideo 的训练循环和数据管线"。
- **数据流（data_latent 模式）**：训练样本须包含"文本条件、attention mask、样本元数据和预编码的 VAE latent，并保证 latent 的帧数、分辨率和时间长度与训练参数一致"。
- **数据流（simulate 模式）**：Student rollout 不使用真实 latent，但仍需要文本条件和批次元数据。
- **离线编码机制**：在训练启动前，用 `scripts/encode_negative_prompt.py` 配合 `--model_path` 和 `--output_dir` 把 negative prompt 编码成 embeds 持久化到磁盘，训练时各 rank 只需读取同一份文件，从而规避 collective 死锁。
- **多卡分布式切档机制**：通过 `torchrun --nproc_per_node=8` 启动，并使用 HSDP 分片维度 `--training.distributed.hsdp_shard_dim 8`。
- **Checkpoint 导出链路**：训练输出 DCP 格式 → `scripts/dcp_to_diffusers.py` 接收 `--checkpoint outputs/wan2.1_dmd2_3steps_npu/checkpoint-100` 与 `--role student`，输出到 `exported/wan2.1_t2v_1.3b_3step`。
- **基准验证链路**：`benchmark.py evaluate` 直接接受 `benchmark_outputs/0_05_kmeans/videos` 视频目录与 `--dataset_root /path/to/final_mini_dataset_0_05`（原文标注"评测入口只依赖标准视频目录，可直接评测 DMD2 或其他算法生成的视频"）。

**性能数据**：原文未给出任何性能/加速比/吞吐数字。

---

## 【表格解读】

### 表格 1：环境要求

| 组件 | 版本要求 |
|------|----------|
| 昇腾硬件 | Atlas 800 训练服务器（Ascend 910B）或更高版本 |
| CANN | 8.5.0 及以上 |
| Python | 3.10 及以上 |
| torch / torch_npu | 2.7.1 及以上 |
| FastVideo | 0.2.0 |

**逐行解读：**
- **昇腾硬件**：限定 Atlas 800 系列训练服务器（Ascend 910B）及更高 NPU 版本，是 FlashGen 运行的物理基础；意味着 FlashGen 不支持 GPU/CPU 训练。
- **CANN ≥ 8.5.0**：CANN 是昇腾的异构计算架构，8.5.0 是与 torch_npu 2.7.1 配套的最低栈版本。
- **Python ≥ 3.10**：3.10 是 PyTorch 2.7.x 兼容的 Python 下限。
- **torch / torch_npu ≥ 2.7.1**：torch_npu 是 NPU 上的 PyTorch 适配包；该版本要求解释了为何不能直接用 FastVideo 默认 `pyproject.toml` 拉取的 `torch==2.11.0`（过新且仅 CUDA）。
- **FastVideo = 0.2.0**：精确锁版本，而非 `>=0.2.0`，与 Git `git clone -b v0.2.0` 的 tag 严格对应，保证训练循环与数据管线的接口稳定。

---

### 表格 2：两种 rollout 模式的主要区别

| 模式 | Student 起点 | 数据要求 |
|------|--------------|----------|
| `data_latent`（默认） | 真实 VAE latent 加噪 | 需要真实 latent 和文本条件 |
| `simulate` | 纯随机噪声 | Student rollout 不使用真实 latent，但仍需要文本条件和批次元数据 |

**逐行解读：**
- **`data_latent`（默认）**：Student 在 rollout 阶段从一个加噪后的真实 VAE latent 出发，因而数据集必须事先用 VAE 把视频像素编码成 latent 存好；同时需要文本条件（caption）。这是更接近真实数据分布的 rollout 起点。
- **`simulate`**：Student rollout 完全从随机噪声起步，不依赖真实 latent，但仍需文本条件和批次元数据。这是一种"少步推理轨迹模拟"的轻数据路线，适合无真实视频但有 caption 的场景。

---

### 表格 3：关键参数覆盖速查（`--dotted.key value` 形式）

| 覆盖参数 | 说明 |
|----------|------|
| `--training.distributed.num_gpus N` | NPU 数量 |
| `--training.data.train_batch_size B` | 每卡 batch size |
| `--training.loop.max_train_steps S` | 最大训练步数 |
| `--training.checkpoint.output_dir path` | checkpoint 输出目录 |
| `--method.rollout_mode data_latent` | 使用真实 VAE latent 加噪进行 Student rollout（默认） |
| `--method.rollout_mode simulate` | 从随机噪声模拟少步推理轨迹 |
| `--method.dmd_denoising_steps "[1000, 750, 500, 250]"` | 蒸馏步数（列表类型用 JSON 风格） |
| `--models.<role>.negative_prompt_embeds_path path` | 对 `student`、`teacher`、`critic` 分别设置 negative prompt 路径 |

**逐行解读：**
- **`--training.distributed.num_gpus N`**：设定参与训练的 NPU 卡数；与 `torchrun --nproc_per_node=N` 协同使用。
- **`--training.data.train_batch_size B`**：每张 NPU 上的 batch size。
- **`--training.loop.max_train_steps S`**：训练总步数上限，控制训练时长。
- **`--training.checkpoint.output_dir path`**：DCP checkpoint 输出目录；多卡示例中可见默认输出到 `outputs/wan2.1_dmd2_3steps_npu/`。
- **`--method.rollout_mode data_latent`**：默认模式，Student 从真实 VAE latent 加噪起步。
- **`--method.rollout_mode simulate`**：替代模式，Student 从纯随机噪声起步；与表格 2 一致。
- **`--method.dmd_denoising_steps "[1000, 750, 500, 250]"`**：DMD2 蒸馏的目标去噪步数列表，原文示例从 1000 步降到 250 步共 4 个采样点；列表类型必须用 JSON 风格字符串传入，因为命令行只支持标量。
- **`--models.<role>.negative_prompt_embeds_path path`**：占位符 `<role>` 替换为 `student` / `teacher` / `critic` 之一，三者必须指向同一编码结果（与步骤 4 一致）。

---

## 【公式解读】

原文无公式。

（本文档为工程性 Quick Start，未包含任何 LaTeX 数学公式或伪代码公式。涉及的"DMD2 蒸馏步数"以列表 `[1000, 750, 500, 250]` 的纯数据形式给出，不构成数学公式。）

---

## 【关联】

本文档作为总入口，在文末"其他说明"和正文多处给出到具体特性页的跳转链接，构成如下上下游关系：

- **→ [features/step_distill.md](features/step_distill.md)**：DMD2 蒸馏原理与架构总览文档；本指南是其工程操作层的实现。
- **→ [features/step_distill.md#关键参数说明](features/step_distill.md#关键参数说明)**：本文档"关键参数覆盖速查"表只列了 8 个高频参数，更完整的配置项说明在此页面（如 rollout 模式、critic 配置、DMD loss 系数等未在速查表中列出的参数）。
- **→ [features/step_distill.md#rollout-模式](features/step_distill.md#rollout-模式)**：本文档步骤 5 仅以一个三列表格概述了 `data_latent` vs `simulate` 的差异，详细 rollout 流程、数据流图、teacher/critic 在 rollout 中的角色在该锚点页面展开。
- **→ [features/benchmark.md](features/benchmark.md)**：本文档步骤 8 给出的 `benchmark.py evaluate` 调用是 VBench 评测的最小示例，更详细的评测指标、prompt 集说明在该页面。
- **横向关联**：本文档的步骤 6 多卡示例配置 `wan_dmd_npu.yaml` 与 `--method.rollout_mode`、`--method.dmd_denoising_steps` 等参数同属 `step_distill` 特性域；步骤 7 的 `dcp_to_diffusers.py` 与步骤 8 的 `benchmark.py` 构成"训练 → 导出 → 评测"的串联链路。
- **外部依赖**：FastVideo（GitHub: `hao-ai-lab/FastVideo` v0.2.0）提供训练循环与数据管线；Hugging Face Hub 提供 Wan 2.1 T2V 1.3B Diffusers 模型权重；AISBench VBench 提供评测基线。

---

## 【使用方法】

### 1. 安装 FastVideo（必须 `--no-deps`）
```bash
git clone -b v0.2.0 https://github.com/hao-ai-lab/FastVideo.git
cd FastVideo
pip install -e . --no-deps
# 手动安装其余依赖: pip install transformers diffusers einops 等
```

### 2. 安装 FlashGen
```bash
git clone https://gitcode.com/Ascend/FlashGen.git
cd FlashGen
pip install -e .
python -c "import flashgen; print(flashgen.__version__)"
```

### 3. 下载预训练模型
```bash
pip install -U huggingface_hub
MODEL_PATH=/path/to/Wan2.1-T2V-1.3B-Diffusers
hf download Wan-AI/Wan2.1-T2V-1.3B-Diffusers --local-dir "$MODEL_PATH"
```

### 4. 离线编码 negative prompt
```bash
python scripts/encode_negative_prompt.py \
    --model_path /path/to/Wan2.1-T2V-1.3B-Diffusers \
    --output_dir /path/to/negative_prompt
```

### 5. 训练数据放置
按配置中 `training.data.data_path` 指定路径放置训练样本（data_latent 模式需 VAE latent、文本条件、attention mask、元数据；帧数/分辨率/时长与训练参数一致）。

### 6. 启动训练

**单卡：**
```bash
python train.py --config flashgen/configs/wan_dmd_npu.yaml
```

**8 卡分布式：**
```bash
torchrun --nproc_per_node=8 train.py \
    --config flashgen/configs/wan_dmd_npu.yaml \
    --method.rollout_mode data_latent \
    --training.distributed.num_gpus 8 \
    --training.distributed.hsdp_shard_dim 8
```

### 7. 导出模型（DCP → Diffusers）
```bash
python scripts/dcp_to_diffusers.py \
    --checkpoint outputs/wan2.1_dmd2_3steps_npu/checkpoint-100 \
    --output-dir exported/wan2.1_t2v_1.3b_3step \
    --role student
```

### 8. VBench 基准验证
```bash
python benchmark.py evaluate \
    --videos_dir benchmark_outputs/0_05_kmeans/videos \
    --work_dir benchmark_outputs/0_05_kmeans/evaluation \
    --dataset_root /path/to/final_mini_dataset_0_05 \
    --mini_ratio 0_05 \
    --sampling kmeans \
    --vbench_cache_dir /path/to/vbench-cache \
    --max_num_workers 16 \
    --max_workers_per_gpu 4 \
    --name wan_dmd_3step
```

### 配置项结构（YAML 关键路径汇总，原文出现）
- `models.<role>.init_from`（`<role>` ∈ {student, teacher, critic}）：预训练模型路径
- `models.<role>.negative_prompt_embeds_path`：离线编码的 negative prompt 路径
- `training.data.data_path`：训练数据路径
- `training.distributed.num_gpus` / `training.distributed.hsdp_shard_dim`：分布式参数
- `training.data.train_batch_size` / `training.loop.max_train_steps` / `training.checkpoint.output_dir`：训练循环参数
- `method.rollout_mode`（`data_latent` | `simulate`） / `method.dmd_denoising_steps`（JSON 列表）：蒸馏方法参数

### 平台支持
原文未涉及（非环境要求内的）其他启用方式或配置项；平台部署问题请联系 `#ascend_support`。
