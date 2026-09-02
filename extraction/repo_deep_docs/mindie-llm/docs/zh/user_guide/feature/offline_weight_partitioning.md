# 权重离线切分

> 仓 `mindie-llm` · 路径 `docs/zh/user_guide/feature/offline_weight_partitioning.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-llm/docs/zh/user_guide/feature/offline_weight_partitioning.md

# 「权重离线切分」feature 文档一体化深度解读

## 【定位】
本文档针对 DeepSeek 等大规模参数模型在 MindIE 推理引擎中的权重加载流程提出**离线切分优化策略**——将原本"完整加载 → 内存切分 → H2D 传输"的在线流程，改造为"按并行策略预切分并写入 tmpfs → 推理时直接加载"的两阶段方案，以显著降低权重加载时间开销。

---

## 【技术要点】

1. **默认 vs 优化加载流程对比**
   - 默认：完整加载 safetensors 权重 → 内存中按并行策略切分 → H2D 传输至 NPU。
   - 优化：预先依据运行时并行策略切分权重 → 存储到 tmpfs → 推理时直接加载。

2. **支持范围（限制与约束）**
   - 仅支持 **DeepSeek-R1** 和 **DeepSeek-V3** 模型。
   - 切分配置必须与推理运行时配置**保持一致**。
   - 仅支持 **Atlas 800I A2 推理服务器双机** 与 **Atlas 800I A3 超节点服务器单机** 两种部署形态。
   - **互斥**：与"共享专家和路由专家合并"特性、动态负载均衡特性均不可同时开启。

3. **Atlas 800I A3 超节点单机切分命令**
   - 使用 `torchrun --nproc_per_node 16 --master_port 20030`，启用 `examples.convert.weight_sharder` 模块。
   - 并行参数：`--dp 2 --tp 8 --moe_tp 4 --moe_ep 4`（即 2×8 = 16 进程，与单机 16 卡对应）。
   - 若推理时使用 MTP，需先 `export DEEPSEEK_MTP=1`。

4. **Atlas 800I A2 双机切分命令**
   - 双机各 8 卡，共 16 卡；需要 `RANK_TABLE_FILE` 环境变量指向 ranktable 文件。
   - 主从节点分别设置 `--node_rank=0` 与 `--node_rank=1`，通过 `--master_addr` 与 `--master_port 20030` 建立集合通信。
   - 同一并行参数组合 `--dp 2 --tp 8 --moe_tp 4 --moe_ep 4`。

5. **切分后权重目录结构**（关键产出）
   - `model-000 … model-015`：按模型层切分的 16 份主权重。
   - `model-attn-tp-000 … model-attn-tp-007`：attention 模块按 tp=8 切分。
   - `model-dense-tp-000 … model-dense-tp-007`：dense 模块按 tp=8 切分。
   - `model-moe-tp-XXX-ep-XXX`：MoE 模块按 tp=4、ep=4 双重切分，每份内含 5 个分片（model-00001~00005-of-00005.safetensors），共 4×4=16 个 MoE 目录。
   - `model-norm`：norm 模块权重。
   - `model_sharded_metadata.json`：新增的**切分元数据索引文件**，记录切分策略与文件映射。
   - 此外保留 `config.json`、`generation_config.json`、`quant_model_description_w8a8_dynamic.json`（说明量化描述采用 **w8a8_dynamic** 方案）、`tokenizer.json`/`tokenizer_config.json` 等配置与分词器文件。

6. **推理侧配置接入**
   - 在 `conf/config.json` 中将 `modelName` 设为 `DeepSeek-R1_w8a8`，`modelWeightPath` 指向**切分后权重文件保存路径**。
   - `worldSize=16`、`cpuMemSize=5`、`npuMemSize=-1`、`backendType=atb`、`trustRemoteCode=false`。

---

## 【关键机制与数据】

- **工作原理（原文）**：默认权重加载过程为"首先完整加载 safetensors 格式的权重文件，然后在内存中依据并行策略执行切分处理，最终通过 H2D（Host-to-Device）方式将权重传输至 NPU 卡上"。离线切分将该流程的"内存切分"环节前移到运行前，并以 **tmpfs** 作为中间存储介质，从而减少推理启动时的内存切分与传输开销。
- **数据流（原文）**：模型完整权重 → `examples.convert.weight_sharder` 按 `--dp / --tp / --moe_tp / --moe_ep` 切分 → 写入指定 `--save_directory`（建议位于 tmpfs）→ 推理时 `modelWeightPath` 直接指向该目录 → 跳过内存切分。
- **关键数字（原文）**：单机 `--nproc_per_node=16`，双机 `--nnodes=2 --nproc_per_node=8`；并行组合统一为 `dp=2, tp=8, moe_tp=4, moe_ep=4`；`master_port=20030`；MoE 每份内 5 个 safetensors 分片；`cpuMemSize=5`、`maxSeqLen=2560`、`maxInputTokenLen=2048`、`truncation=0`。
- **量化方案（原文）**：`quant_model_description_w8a8_dynamic.json` 文件名表明离线切分适配 w8a8 dynamic 量化描述。
- 原文未提供具体的加载耗时对比、性能加速比、内存占用等量化数据。

---

## 【表格解读】

原文无表格。

（切分后目录以代码块形式给出，属文件系统结构而非参数表/对比表，故不在此处还原为表格。）

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **下游 — 服务化配置**：`../user_manual/service_parameter_configuration.md`
  文档在"执行推理"章节明确要求读者参考《配置参数说明（服务化）》来配置 `ModelDeployConfig` 中的 `ModelConfig` 子项，本 feature 通过修改 `modelWeightPath` 与 `worldSize` 等参数接入主流程，是服务化推理链路的一部分。

- **互斥特性**：
  - "共享专家和路由专家合并"特性；
  - "动态负载均衡"特性。
  本特性均不可与上述两者同时开启，表明三者在权重布局/路由层面存在冲突。

- **上游 — 硬件与模型绑定**：
  - 硬件侧仅适配 Atlas 800I A2/A3 服务器；
  - 模型侧仅适配 DeepSeek-R1/DeepSeek-V3。
  在更大特性矩阵中属"模型-硬件-特性"三维交集内的窄带能力。

- **隐含上游 — 量化链路**：`quant_model_description_w8a8_dynamic.json` 表明权重在切分前已经过 w8a8 dynamic 量化处理，离线切分位于量化之后、H2D 加载之前。

---

## 【使用方法】

### 步骤一：执行权重切分（按部署形态二选一）

**A3 超节点单机场景**：
```bash
export DEEPSEEK_MTP=1   # 仅当推理侧启用 MTP 时设置
torchrun --nproc_per_node 16 --master_port 20030 \
  -m examples.convert.weight_sharder \
  --model_path {完整权重路径} \
  --dp 2 --tp 8 --moe_tp 4 --moe_ep 4 \
  --save_directory {切分后权重文件保存路径}
```

**A2 双机场景**：
```bash
export DEEPSEEK_MTP=1
export RANK_TABLE_FILE={ranktable文件路径}

# 主节点
torchrun --nnodes=2 --nproc_per_node=8 --node_rank=0 \
  --master_addr="主节点IP" --master_port 20030 \
  -m examples.convert.weight_sharder \
  --model_path {完整权重路径} \
  --dp 2 --tp 8 --moe_tp 4 --moe_ep 4 \
  --save_directory {切分后权重文件保存路径}

# 从节点
torchrun --nnodes=2 --nproc_per_node=8 --node_rank=1 \
  --master_addr="主节点IP" --master_port 20030 \
  -m examples.convert.weight_sharder \
  --model_path {完整权重路径} \
  --dp 2 --tp 8 --moe_tp 4 --moe_ep 4 \
  --save_directory {切分后权重文件保存路径}
```

### 步骤二：配置推理服务

1. 编辑 `{MindIE安装目录}/mindie_llm/conf/config.json`。
2. 在 `ModelDeployConfig.ModelConfig` 中将：
   - `modelName` 设为 `DeepSeek-R1_w8a8`；
   - `modelWeightPath` 设为**步骤一中的 `--save_directory`**；
   - `worldSize=16`，其余参数按 `maxSeqLen=2560`、`maxInputTokenLen=2048`、`truncation=0`、`cpuMemSize=5`、`npuMemSize=-1`、`backendType=atb`、`trustRemoteCode=false` 模板填写。
3. 其他服务化参数含义参见《配置参数说明（服务化）》（`../user_manual/service_parameter_configuration.md`）。

### 步骤三：约束自检（启用前必读）

- 确认模型为 **DeepSeek-R1** 或 **DeepSeek-V3**。
- 确认硬件为 **Atlas 800I A2 双机** 或 **Atlas 800I A3 超节点单机**。
- 确认未同时启用"共享专家和路由专家合并"特性与"动态负载均衡"特性。
- 确认切分时的 `--dp/--tp/--moe_tp/--moe_ep` 与推理运行时配置完全一致。
- 建议将 `--save_directory` 指向 tmpfs 路径，以获得最佳加载速度收益。
