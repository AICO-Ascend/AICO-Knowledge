# 快速入门：Qwen3-8B 模型预训练及微调

> 仓 `mindspeed-llm` · 路径 `docs/zh/pytorch/training/quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-llm/docs/zh/pytorch/training/quick_start.md

# 「快速入门：Qwen3-8B 模型预训练及微调」深度解读

---

## 【定位】

这篇文档是 **MindSpeed LLM（昇腾 LLM 分布式训练框架）的入门级实操指南**，面向首次接触该框架的开发者，以 Qwen3-8B 为具体示例，贯通"环境准备 → 权重与数据集准备 → 预训练 → 指令微调"的端到端最小化流程，让开发者能够在昇腾 NPU 上快速启动一次完整的 LLM 预训练和单机 SFT 微调任务。

---

## 【技术要点】

1. **硬件与平台约束**：MindSpeed LLM 支持 Ascend 950 / Atlas A3 / Atlas A2 三类训练系列产品；要求 **单 NPU 片上内存 ≥ 64GB**；示例脚本默认配置 `NPUS_PER_NODE=8`（即 8 卡 NPU），低于此配置可能触发 OOM。
2. **权重双源获取**：提供 HuggingFace 与 ModelScope 两条 wget 通道，二选一即可；Qwen3-8B 权重被切分为 **5 个 safetensors 分片**（model-00001 至 00005-of-00005），配套下载 `config.json`、`generation_config.json`、`merges.txt`、`tokenizer.json`、`tokenizer_config.json`、`vocab.json`、`model.safetensors.index.json`；下载后可使用 `sha256sum` 校验完整性。
3. **数据准备**：使用 Alpaca 数据集（`train-00000-of-00001-a09b74b3ef9c3b56.parquet`），同样支持 HuggingFace 与 ModelScope 双源下载。
4. **环境变量加载**：必须执行 `source /usr/local/Ascend/cann/set_env.sh` 与 `source /usr/local/Ascend/nnal/atb/set_env.sh`（路径以 root 用户默认安装为例），缺一不可。
5. **分布式训练三要素配置**：`NPUS_PER_NODE=8`、`MASTER_ADDR=localhost`、`MASTER_PORT=6000`、`NNODES=1`、`NODE_RANK=0`；并由 `WORLD_SIZE=$(($NPUS_PER_NODE * $NNODES))` 算出总算力规模；其中 `NODE_RANK=0` 为主节点。
6. **预训练关键开关**：`--use-mcore-models`（Mcore 分支）、`--disable-bias-linear`、`--group-query-attention` + `--num-query-groups 8`（GQA）、`--position-embedding-type rope`（RoPE）、`--untie-embeddings-and-output-weights`、`--bf16`。
7. **微调关键开关**：`--finetune`、`--stage sft/dpo`、`--is-instruction-dataset`、`--prompt-type`（对话模板在 `templates.json` 中查表）、`--no-pad-to-seq-lengths`（默认按 8 的倍数 padding）、`--sequence-parallel`、`--use-distributed-optimizer`、`--use-flash-attn`、`--bf16`。
8. **多机存储边界**：多机训练若未配置 NFS 等共享存储，必须在脚本中追加 `--no-shared-storage`，否则非主节点会因跨节点读取预处理结果而报错；启用后非主节点自动在本地缓存数据预处理产物。

---

## 【关键机制与数据】

**分布式节点身份与通信机制**（原文）：通过 `MASTER_ADDR / MASTER_PORT` 建立主节点通信锚点；`NODE_RANK` 在不同节点上互不重复，标识节点身份；主节点 = `NODE_RANK=0`。`WORLD_SIZE` 是进程级别的全局卡数，等于 `NPUS_PER_NODE × NNODES`。

**多机共享存储兜底机制**（原文）：在无 NFS 场景下，`--no-shared-storage` 让非主节点将数据预处理结果本地化生成并缓存，避免跨节点读取失败；多机启动必须在多个终端各开一个脚本，每个终端仅 `NODE_RANK` 不同、`MASTER_ADDR` 保持一致指向主节点 IP。

**预训练产物路径约定**（原文）：`CKPT_SAVE_DIR="./ckpt/qwen3-8b"` 保存训练后的权重；`CKPT_LOAD_DIR="./model_from_hf/qwen3_hf/"` 指向 HuggingFace 原始开源权重；`TOKENIZER_PATH` 与 `CKPT_LOAD_DIR` 同源，均来自开源权重目录。

**精度选择机制**（原文）：昇腾芯片对 bf16 精度支持良好，因此训练与微调脚本均启用 `--bf16` 以"显著提升训练速度"。

**GQA 注意力机制**（原文）：Qwen3-8B 需要开启 GQA 并将 groups 设为 8（即 `--group-query-attention` 配 `--num-query-groups 8`），与原模型结构对齐。

**动态 padding 机制**（原文）：微调默认按 8 的倍数做定长 padding；`--no-pad-to-seq-lengths` 可关闭该定长行为，切换到动态序列长度微调。

**性能/量化指标**：原文未提供吞吐、loss 收敛曲线、训练时长等具体数据，仅以截图（图 1、图 2 的运行日志）作为运行成功的视觉佐证。

---

## 【表格解读】

### 表 1：预训练脚本参数说明

| 参数名 | 说明 |
|----|----|
| `--use-mcore-models` | 使用 Mcore 分支运行模型 |
| `--disable-bias-linear` | 去掉 linear 的偏移值，与 Qwen 原模型一致 |
| `--group-query-attention` | 开启 GQA 注意力处理机制 |
| `--num-query-groups 8` | 配合 GQA 使用，设置 groups 为 8 |
| `--position-embedding-type rope` | 位置编码采用 RoPE 方案 |
| `--untie-embeddings-and-output-weights` | 根据原模型要求将 output 层和 embedding 层的权重解耦 |
| `--bf16` | 昇腾芯片对 bf16 精度支持良好，可显著提升训练速度 |

**逐行解读**：
- `--use-mcore-models`：选择 Megatron-Core（Mcore）分支作为后端，这是 MindSpeed LLM 在昇腾上承载并行能力的核心 runtime，不开则无法触发 mcore 体系下的张量并行/流水线并行/序列并行优化。
- `--disable-bias-linear`：Qwen 原模型在 Linear 层不带 bias；为保证权重与开源版可对齐转换，必须显式关掉 bias。
- `--group-query-attention` + `--num-query-groups 8`：Qwen3-8B 使用 GQA（Grouped-Query Attention），每 8 个 Query 共享一组 KV head；这两个开关必须配套出现，否则会破坏注意力形状。
- `--position-embedding-type rope`：Qwen 系模型原生即用 RoPE 位置编码，这里显式声明以避免框架默认使用绝对位置编码导致不兼容。
- `--untie-embeddings-and-output-weights`：将 LM Head（output 层）和 Embedding 的权重参数解耦；适用于参数量较大的模型，可显著节省不必要共享带来的内存开销并与 Qwen 原模型结构对齐。
- `--bf16`：bf16 在昇腾上有硬件加速通路，相比 fp32 可显著提升训练吞吐。

### 表 2：微调脚本参数说明

| 参数名 | 说明 |
|----|----|
| `--finetune` | 启动模型的微调模式 |
| `--stage` | 训练方法，如 sft（监督微调）、dpo 等 |
| `--is-instruction-dataset` | 用于指定微调过程中采用指令微调数据集，以确保模型依据特定指令数据进行微调 |
| `--prompt-type` | 用于指定模型模板，能够让 base 模型微调后能具备更好的对话能力。可在 templates.json 文件内查看 `prompt-type` 的可选项 |
| `--no-pad-to-seq-lengths` | 关闭固定序列长度 padding，支持动态序列长度微调，默认按照 8 的倍数进行 padding |
| `--sequence-parallel` | 开启序列并行 |
| `--use-distributed-optimizer` | 启用分布式优化器 |
| `--use-flash-attn` | 启用 Flash Attention |
| `--bf16` | 昇腾芯片对 bf16 精度支持良好，可显著提升训练速度 |

**逐行解读**：
- `--finetune`：模式开关，与预训练阶段互斥；开启后框架会按微调流程加载优化器状态、冻结/解冻策略以及构造 instruction 风格的数据管道。
- `--stage`：算法选择层；当前示例使用 `sft`（监督微调），也可切换 `dpo` 等偏好对齐算法。Alpaca 数据集天然适配 sft。
- `--is-instruction-dataset`：数据形态标识；开启后框架会把数据按"指令/输入/输出"三元组组织，而非纯续写式堆叠。
- `--prompt-type`：对话模板选择，决定了 instruction 字段如何被包进 prompt；该参数的可选值表维护在 `configs/finetune/templates.json` 中，可按需查表。
- `--no-pad-to-seq-lengths`：默认为了对齐效率按 8 的倍数做定长 padding；如希望节省 padding 算力并贴合变长样本，可关闭它走动态长度路径。
- `--sequence-parallel`：开启序列维度的切分；可与张量并行协同降低长序列场景下的激活显存。
- `--use-distributed-optimizer`：将优化器状态在数据并行维度切分到各 rank 显存，显著降低单卡 optimizer state 占用，是大模型训练的标准实践。
- `--use-flash-attn`：启用 Flash Attention，将注意力计算中的中间激活做 tiling 处理，长序列训练必备。
- `--bf16`：与预训练一致，硬件友好。

---

## 【公式解读】

原文无 LaTeX/数学公式，但脚本中包含一条隐含的算式：

```bash
WORLD_SIZE=$(($NPUS_PER_NODE * $NNODES))
```

**符号解释**：
- `WORLD_SIZE`：分布式集合通信域（process group）中的总进程数，等于物理资源总卡数。
- `NPUS_PER_NODE`：单节点上参与训练的 NPU 数量，示例为 `8`。
- `NNODES`：参与训练的物理节点数量，示例单机为 `1`，多机时按节点数累加。
- `$(($...*...))`：shell 的算术展开语法，等价于 `NPUS_PER_NODE × NNODES`。

**作用**：让 torch.distributed 等后端在自动推导全局 rank 范围、初始化 rendezvous 时获得正确的进程总数；改变其中任一项都会自动重算，是脚本中"自适应规模"的关键。

---

## 【关联】

本文档处于"MindSpeed LLM 入门到深入"文档链路的起点，依托三处内部链接：

1. **`../models/supported_models.md`**（模型支持列表）：在概述处被引用，用于确认 Qwen3-8B 之外想尝试的其他模型是否在 Ascend 950 / Atlas A3 / Atlas A2、64GB 单 NPU 内存的约束下得到官方支持；它是"我能跑什么模型"的唯一权威索引。
2. **`install_guide.md`**（MindSpeed LLM 软件安装）：在"环境准备"章节被引用，承接上层 MindSpeed 安装页（`https://www.hiascend.com/developer/software/mindspeed/download`），承担 driver/firmware/CANN/PyTorch/torch_npu/MindSpeed LLM 全套安装细节。
3. **`../../../../configs/finetune/templates.json`**（微调 prompt 模板配置）：在表 2 注释中被引用，承载所有可选的 `--prompt-type` 取值，是微调阶段决定数据如何被格式化进输入的关键配置文件。

**上下游关系**：
- **上游**：依赖 HuggingFace / ModelScope 的开源生态（Qwen3-8B 权重、Alpaca 数据集）；依赖昇腾 CANN + ATB 运行时（`set_env.sh`）；以 Megatron-LM / Megatron-Core 为算法底座。
- **下游**：预训练和微调流程均将权重落盘至 `CKPT_SAVE_DIR="./ckpt/qwen3-8b"`；这一产物通常作为后续指令对齐、推理服务化（DeeSpeed / vLLM-on-Ascend 等）的输入。

---

## 【使用方法】

**1. 环境搭建命令**（原文）：
```shell
source /usr/local/Ascend/cann/set_env.sh
source /usr/local/Ascend/nnal/atb/set_env.sh
```
请按实际安装路径调整。

**2. 预训练启动命令**（原文）：
```shell
vi examples/mcore/qwen3/pretrain_qwen3_8b_4K_ptd.sh   # 编辑脚本
bash examples/mcore/qwen3/pretrain_qwen3_8b_4K_ptd.sh # 执行预训练
```
脚本内必须配置：`NPUS_PER_NODE=8`、`MASTER_ADDR=localhost`、`MASTER_PORT=6000`、`NNODES=1`、`NODE_RANK=0`、`CKPT_SAVE_DIR`、`DATA_PATH`、`TOKENIZER_PATH`、`CKPT_LOAD_DIR`。

**3. 微调启动命令**（原文）：
```shell
vi examples/mcore/qwen3/tune_qwen3_8b_4K_full_ptd.sh # 编辑脚本
bash examples/mcore/qwen3/tune_qwen3_8b_4K_full_ptd.sh # 执行微调
```
脚本内配置项含义与预训练一致，`CKPT_LOAD_DIR` 加载 HuggingFace 开源权重（也可指向预训练产物继续 SFT），`CKPT_SAVE_DIR` 指向微调后权重的落盘路径。

**4. 关键多机配置**（原文）：
- 多机时每个终端脚本的 `NODE_RANK` 依次取 `(0, NNODES-1)`，`MASTER_ADDR` 全部指向同一主节点 IP，其余参数保持一致。
- 多机未配置 NFS 等共享存储时，必须在训练脚本中追加 `--no-shared-storage`。

## 图文联合解读

- `running_log.png`: 图示为Qwen3-8B训练终端日志：模型总参7.62B，8卡NPU吞吐从25.1升至152 TFLOPs/s，各Rank显存分配28-39GB。证明文档要求NPUS_PER_NODE=8配置下预训练可正常启动，loss稳定收敛、warmup正常生效，吞吐稳步爬升。
- `tune_log.png`: **图示内容**：终端训练日志，展示了Qwen3-8B的参数统计（总参8.19B，Transformer块6.95B，嵌入层1.24B）、权重+优化器理论显存约35.1GB，以及5次迭代的loss（3.05→3.53）、grad norm（44→85.5）和耗时（首次5609ms，后续稳定~1.5s）。

**技术结论**：参数量精确匹配Qwen3-8B规模，单卡分配约35GB显存未触发OOM，迭代2后耗时稳定在1.5s左右，表明模型在8卡NPU上加载与训练流程正常。

**与文档关系**：佐证"NPUS_PER_NODE=8"配置下模型可成功启动预训练，并直观呈现参数切分与显存占用，与文档"启动训练任务"步骤形成证据闭环。
