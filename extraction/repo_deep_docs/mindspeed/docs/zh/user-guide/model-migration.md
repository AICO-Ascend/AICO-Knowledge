# 模型迁移指南

> 仓 `mindspeed` · 路径 `docs/zh/user-guide/model-migration.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed/docs/zh/user-guide/model-migration.md

# 模型迁移指南 深度解读

> ⚠️ **原文截断提示**：原文在「多机多卡训练」一节的 Python 代码片段中截断（结束于 `# 原始 / if not path_to_cache or (` 处），以下解读严格基于已呈现内容。

---

## 【定位】

本文档是 `MindSpeed` 提供的**模型迁移指南**，指导具备 `Megatron-LM` 训练基础的用户将原本运行在 GPU 等其他硬件平台上的大模型**迁移到昇腾 NPU 平台**并实现高精度误差范围内的高性能运行。

---

## 【技术要点】

1. **一行代码适配机制**：在 `Megatron-LM` 仓库 `pretrain_gpt.py` 的 `import torch` 下方新增一行 `import mindspeed.megatron_adaptor`，即可完成对 `Megatron-LM` 的昇腾适配。

2. **版本与模型基线**：选用 **Megatron-LM core_v0.12.1** 仓库根目录下的 `pretrain_gpt.py` 中**内置 GPT 模型**作为迁移模型；迁移前需确保选定模型能在三方平台（如 GPU）上运行，并输出精度与性能基线。

3. **CANN 环境变量配置**：`source ${CANN_INSTALL_PATH}/ascend-toolkit/set_env.sh`（`CANN_INSTALL_PATH` 需按本机实际安装位置调整）。

4. **数据集链路**：
   - Tokenizer：从 `gpt-3.5-turbo`（HuggingFace `Xenova/gpt-3.5-turbo`）下载 `vocab.json`、`merges.txt`，重命名为 `gpt2-vocab.json`、`gpt2-merges.txt`，置于 `gpt-tokenizer/` 目录；
   - 语料：从 HuggingFace `tatsu-lab/alpaca` 下载 `train-00000-of-00001-a09b74b3ef9c3b56.parquet`，示例路径 `/home/datasets/Alpaca/`；
   - 依赖安装：`pip3 install nltk pyarrow pandas`；
   - 转换脚本 `convert_parquet.py` 将 parquet → JSON；
   - Megatron-LM 预处理：`tools/preprocess_data.py`，输出 `alpaca_text_document.bin` / `.idx`。

5. **分布式脚本参数化**：
   - 单机：`NNODES=1`、`MASTER_ADDR=localhost`、`NODE_RANK=0`、`MASTER_PORT=6000`、`CUDA_DEVICE_MAX_CONNECTIONS=1`；
   - 双机：`NNODES=2`，主节点 `NODE_RANK=0`、从节点 `NODE_RANK=1`，`MASTER_ADDR` 填主节点 IP；
   - 单机 `global-batch-size=64`，双机 `global-batch-size=128`；其它 GPT 超参一致。

6. **Python 版本约束**：从 `core_r0.10.0` 起，`Megatron-LM`/`MindSpeed` 大量使用 `Optional[list[int]]` 等高版本类型注解语法；若出现 `TypeError: 'type' object is not subscriptable`，需**升级 Python 到 3.10 及以上**。

7. **多机共享存储机制**：`Megatron-LM` 通过 `data_cache_path` 命令行参数设置多机共享数据路径；未设置表示不使用共享存储；若**未使用共享存储**，需修改 `megatron/core/datasets/gpt_dataset.py` 中 `if not path_to_cache or (not cache_hit` … 相关代码段（原文在此处截断）。

---

## 【关键机制与数据】

- **迁移原因分层（原文）**：硬件特性差异 / 计算架构差异（CUDA vs CANN）/ 深度学习框架差异（需 `MindSpeed` 适配张量运算、自动微分）。
- **目标范围（原文）**："在合理精度误差范围内高性能运行"。
- **数据集切分比例（原文）**：`--split 949,50,1`（训练/验证/测试按 949:50:1 划分 Alpaca）。
- **GPT 训练超参（原文脚本）**：`num-layers=24`、`hidden-size=1024`、`num-attention-heads=16`、`seq-length=1024`、`max-position-embeddings=1024`、`micro-batch-size=8`、`lr=0.00015`、`train-iters=1000`、`lr-decay-iters=320000`、`lr-decay-style=cosine`、`min-lr=1.0e-5`、`weight-decay=1e-2`、`lr-warmup-fraction=.01`、`clip-grad=1.0`、`--fp16`、`--transformer-impl local`。
- **预处理日志与工作进程（原文）**：`--log-interval 1000`、`--workers 8`。
- **训练日志与评估频率（原文）**：`--log-interval 100`、`--save-interval 100`、`--eval-interval 1000`、`--eval-iters 10`。
- **精度与基线（原文）**：要求"在合理精度误差范围内"，并需先采集 GPU 侧精度与性能基线，原文未给出具体数值阈值。
- **性能数据**：原文无具体性能数字与吞吐/加速比。

---

## 【表格解读】

**原文无表格**（markdown 表格）。

为便于理解，以下**非原文表格**，仅将训练脚本中的关键参数汇总（参数均来源于原文 shell 脚本，非外推）：

| 类别 | 参数名 | 单机值 | 多机（双机）值 | 原文依据 |
|---|---|---|---|---|
| 分布式 | `GPUS_PER_NODE` | 8 | 8 | 脚本注释「每个节点卡数，根据实际情况填写」 |
| 分布式 | `NNODES` | 1 | 2 | 脚本注释 |
| 分布式 | `NODE_RANK` | 0 | 主 0 / 从 1 | 脚本注释 |
| 分布式 | `MASTER_ADDR` | localhost | 主节点 IP | 脚本注释 |
| 分布式 | `MASTER_PORT` | 6000 | 6000 | 脚本 |
| 训练 | `num-layers` | 24 | 24 | GPT_ARGS |
| 训练 | `hidden-size` | 1024 | 1024 | GPT_ARGS |
| 训练 | `num-attention-heads` | 16 | 16 | GPT_ARGS |
| 训练 | `seq-length` | 1024 | 1024 | GPT_ARGS |
| 训练 | `micro-batch-size` | 8 | 8 | GPT_ARGS |
| 训练 | `global-batch-size` | 64 | 128 | GPT_ARGS |
| 训练 | `lr` | 0.00015 | 0.00015 | GPT_ARGS |
| 训练 | `train-iters` | 1000 | 1000 | GPT_ARGS |
| 训练 | `min-lr` | 1.0e-5 | 1.0e-5 | GPT_ARGS |
| 训练 | `weight-decay` | 1e-2 | 1e-2 | GPT_ARGS |
| 训练 | `clip-grad` | 1.0 | 1.0 | GPT_ARGS |
| 训练 | 精度 | `--fp16` | `--fp16` | GPT_ARGS |
| 训练 | 实现 | `transformer-impl local` | `transformer-impl local` | GPT_ARGS |
| 数据 | `split` | 949,50,1 | 949,50,1 | DATA_ARGS |
| 数据 | `tokenizer-type` | GPT2BPETokenizer | — | preprocess_data.py |
| 数据 | `workers` | 8 | — | preprocess_data.py |
| 输出 | `log-interval` | 100 | 100 | OUTPUT_ARGS |
| 输出 | `save-interval` | 100 | 100 | OUTPUT_ARGS |
| 输出 | `eval-interval` | 1000 | 1000 | OUTPUT_ARGS |
| 输出 | `eval-iters` | 10 | 10 | OUTPUT_ARGS |
| 后端 | `distributed-backend` | nccl | nccl | torchrun 参数 |
| Checkpoint | `ckpt-format` | torch | torch | torchrun 参数 |

逐行解读：原文中**仅单机与双机在 `global-batch-size`（64 vs 128）与 `MASTER_ADDR` / `NNODES` / `NODE_RANK` 上不同**，其余 GPT 模型超参与数据/输出配置完全一致；这表明迁移示例在保持模型结构与优化器配置不变的前提下，将全局 batch 随节点数线性放大，与数据并行的同步策略一致。

---

## 【公式解读】

**原文无公式**（无 LaTeX 或伪代码形式的数学公式）。脚本中的算式：

```
WORLD_SIZE=$(($GPUS_PER_NODE*$NNODES))
```

属于 shell 算术展开（`$(())`），表示「每节点卡数 × 节点数 = 全局 World Size」，并非数学公式；仅作为分布式 `torchrun` 的规模计算辅助说明。

---

## 【关联】

- **上游/外部依赖**：
  - `Megatron-LM`（NVIDIA，core_v0.12.1）：被迁移的源框架，提供 `pretrain_gpt.py`、`tools/preprocess_data.py`、`megatron/core/datasets/gpt_dataset.py`。
  - **CANN**（华为异构计算架构）：NPU 计算栈基础，需 `source ${CANN_INSTALL_PATH}/ascend-toolkit/set_env.sh`。
  - **HuggingFace**：`Xenova/gpt-3.5-turbo`（Tokenizer）、`tatsu-lab/alpaca`（Alpaca 数据集）；备选 **ModelScope** 国内源。
  - **`torchrun` / NCCL 后端**：分布式启动与通信。

- **内部链接与同库模块**：
  - [安装指南](../user-guide/install_guide.md)：在「模型迁移」一节明确引用，是 `import mindspeed.megatron_adaptor` 之前**必须先完成的基础环境搭建**步骤，构成"先安装 → 再适配 → 后训练"的链式依赖。
  - [模型保存与加载](#模型保存与加载)：同文档内部锚点（原文未展开），在单机训练"后续处理"小节被引用，用于基于 `CHECKPOINT_PATH=./ckpt` 的二次训练。
  - [昇腾 MindSpeed 开源社区](https://gitcode.com/Ascend/MindSpeed)：用于 CUDA 接口报错时的 ISSUE 求助入口。
  - [模型迁移总体流程](#模型迁移总体流程)：同文档内部锚点，对应 `figures/model-migration-procedure.png`，串联"模型选取 → 模型迁移 → 模型训练（环境变量 → 数据集 → 训练）"三大阶段。

- **下游/扩展能力**：原文未在已截断的篇幅中给出与其它 MindSpeed 子模块（如 LLM、MM 多模态、RL）的关系。

---

## 【使用方法】

以下命令与配置**均直接来源于原文**：

1. **基础环境**（依赖 [安装指南](../user-guide/install_guide.md)）：安装 MindSpeed 与 CANN 工具包。

2. **启用 MindSpeed 适配（一行代码）**：
   ```python
   import os
   import torch
   import mindspeed.megatron_adaptor   # 新增代码行
   from functools import partial
   from typing import Union
   ```

3. **配置 Ascend 环境变量**：
   ```shell
   source ${CANN_INSTALL_PATH}/ascend-toolkit/set_env.sh
   ```

4. **数据预处理**：
   ```shell
   pip3 install nltk pyarrow pandas
   cd /home/datasets/Alpaca/
   python convert_parquet.py
   ```
   ```shell
   mkdir -p ./gpt_pretrain_data
   python tools/preprocess_data.py \
       --input /home/datasets/Alpaca/alpaca_json.json \
       --output-prefix ./gpt_pretrain_data/alpaca \
       --tokenizer-type GPT2BPETokenizer \
       --vocab-file ./gpt-tokenizer/gpt2-vocab.json \
       --merge-file ./gpt-tokenizer/gpt2-merges.txt \
       --append-eod \
       --log-interval 1000 \
       --workers 8
   ```

5. **单机多卡训练**：
   ```shell
   bash pretrain_single.sh
   ```

6. **多机多卡训练（双机示例）**：
   - 两台机器各新建 `pretrain_distributed.sh`；
   - 主节点 `NODE_RANK=0`、`MASTER_ADDR` 填主节点 IP；从节点 `NODE_RANK=1`；
   - 共享存储：通过 `data_cache_path` 参数开启；**未使用共享存储**时需修改 `megatron/core/datasets/gpt_dataset.py`（原文该修改段截断）。

7. **Python 版本**：自 `core_r0.10.0` 起需 Python ≥ 3.10。

8. **常见报错处置**：CUDA 接口报错 → 前往 [昇腾 MindSpeed 开源社区](https://gitcode.com/Ascend/MindSpeed) 提 ISSUE；类型注解报错 → 升级 Python。

> 说明：原文未涉及「模型保存与加载」「多机多卡非共享存储的完整代码片段」等具体内容（已在原文截断处注明）。

## 图文联合解读

- `model-migration-procedure.png`: **图文解读：**

1) **图中内容**：流程图描绘从"开始"到"结束"的端到端迁移路径，依次为模型获取→模型迁移→模型训练（含环境变量配置、数据集准备、执行训练，后者嵌套单机/多机多卡训练）→模型保存与加载。

2) **技术结论**：迁移是一个有序的多阶段流水线，训练阶段还需按设备规模由单机向多机扩展，体现从基础适配到分布式高性能运行的递进逻辑。

3) **与文档关系**：将文档"端到端迁移流程指南"抽象为可视化路线图，支撑"如何在合理精度内高性能运行"的总论点。
- `iter_result.png`: **图文对照说明：文档与图像存在明显错配。**

文档中引用的是 `figures/model-migration-procedure.png`（迁移流程图），但实际图像为**终端训练日志截图**，并非流程图。

**1) 图中内容：** Megatron-LM GPT模型在NPU上的训练日志，记录iteration 100→700/2000000的运行状态，含lm loss（9.39→2.72递减）、sop loss、learning rate（warmup递增）、grad norm、单步耗时（约255ms）、显存占用（allocated 6.4GB/reserved 9.5GB）、skipped/NaN迭代数等指标，时间戳2023-06-08。

**2) 技术结论：** loss平稳下降、零NaN、显存稳定，论证了Megatron-LM GPT模型经MindSpeed迁移后在NPU上**可正常收敛运行**，作为迁移成功的**实证证据**。

**3) 与文档关系：** 文档论述"迁移后可高性能运行在精度误差范围内"，此日志本应作为该论点的**验证截图**，但**未配套流程图**，建议补充迁移流程示意图。
- `iter_result.png`: **图文对照说明：文档与图像存在明显错配。**

文档中引用的是 `figures/model-migration-procedure.png`（迁移流程图），但实际图像为**终端训练日志截图**，并非流程图。

**1) 图中内容：** Megatron-LM GPT模型在NPU上的训练日志，记录iteration 100→700/2000000的运行状态，含lm loss（9.39→2.72递减）、sop loss、learning rate（warmup递增）、grad norm、单步耗时（约255ms）、显存占用（allocated 6.4GB/reserved 9.5GB）、skipped/NaN迭代数等指标，时间戳2023-06-08。

**2) 技术结论：** loss平稳下降、零NaN、显存稳定，论证了Megatron-LM GPT模型经MindSpeed迁移后在NPU上**可正常收敛运行**，作为迁移成功的**实证证据**。

**3) 与文档关系：** 文档论述"迁移后可高性能运行在精度误差范围内"，此日志本应作为该论点的**验证截图**，但**未配套流程图**，建议补充迁移流程示意图。
- `model-load.png`: # 图文联合解读

## ⚠️ 图文不匹配说明

文档上下文引用的是 `figures/model-migration-procedure.png`（模型迁移总体流程图），但您上传的图片实际是**终端日志截图**，而非流程图。

## 1) 图里画了什么
当前图片内容为 Megatron 训练日志输出，包含：
- Rank 0 / Local Rank 0 标识
- 时间戳：`2025-07-01 14:41:57`
- 优化器日志：`learning rate decay style: cosine`（余弦学习率衰减策略）
- 训练日志：`loading checkpoint from ./ckpt at iteration 100`
- 训练日志：`checkpoint version 3.0`

## 2) 论证了什么技术结论
截图间接证明：在昇腾 NPU + MindSpeed 平台上已成功加载 Megatron-LM 的 checkpoint（iteration 100，version 3.0），并采用了 `cosine` 学习率衰减策略。

## 3) 与文档论点的关系
仅能**侧面佐证**文档所述「模型可在 NPU 上高效运行」，但**无法替代**原图所示的模型迁移总体流程示意图（应包含：模型选取 → 基线采集 → 环境搭建 → MindSpeed 适配 → 精度验证 → 性能调优 等步骤）。

> 📌 **建议**：请上传 `figures/model-migration-procedure.png` 的流程图，以便进行准确的图文联合解读。
- `iter_result.png`: **图文对照说明：文档与图像存在明显错配。**

文档中引用的是 `figures/model-migration-procedure.png`（迁移流程图），但实际图像为**终端训练日志截图**，并非流程图。

**1) 图中内容：** Megatron-LM GPT模型在NPU上的训练日志，记录iteration 100→700/2000000的运行状态，含lm loss（9.39→2.72递减）、sop loss、learning rate（warmup递增）、grad norm、单步耗时（约255ms）、显存占用（allocated 6.4GB/reserved 9.5GB）、skipped/NaN迭代数等指标，时间戳2023-06-08。

**2) 技术结论：** loss平稳下降、零NaN、显存稳定，论证了Megatron-LM GPT模型经MindSpeed迁移后在NPU上**可正常收敛运行**，作为迁移成功的**实证证据**。

**3) 与文档关系：** 文档论述"迁移后可高性能运行在精度误差范围内"，此日志本应作为该论点的**验证截图**，但**未配套流程图**，建议补充迁移流程示意图。
