# FSDP2

> 仓 `mindspeed-mm` · 路径 `docs/zh/features/fsdp2.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-mm/docs/zh/features/fsdp2.md

# FSDP2 文档深度解读

## 【定位】
本文档介绍 MindSpeed MM 套件中 FSDP2（全分片数据并行 v2）的两种使用路线（原生 FSDP2 与基于 Megatron 的 FSDP2），重点说明如何替换传统 FSDP1 的 FlatParameter 设计、采用 DTensor 实现参数分片，并提供从启动、配置到权重转换的完整使用指引。

---

## 【技术要点】

1. **FSDP1 的核心痛点**：将一组参数展平拼接成 `FlatParameter` 表示通信桶，导致桶内单个参数难以差异化操作（参数冻结、精度转换），状态字典逻辑长达数千行且需要额外通信。
2. **FSDP2 的核心改进**：移除 `FlatParameter`，改为沿 0 维分片的 `DTensor` 表示分片参数，支持单参数级操作、免通信的分片状态字典、简化的初始化流程。
3. **两条使用路线**：
   - **原生 FSDP2（推荐）**：入口 `mindspeed_mm/fsdp/train/trainer.py`，需 `export NON_MEGATRON=true`，YAML 六段式配置。
   - **基于 Megatron 的 FSDP2（不推荐，将淘汰）**：复用 Megatron 入口，通过 `--use-torch-fsdp2` 启用，配套 `fsdp2_config.yaml`。
4. **原生 FSDP2 关键启动命令**：
   ```shell
   export NON_MEGATRON=true
   torchrun $DISTRIBUTED_ARGS mindspeed_mm/fsdp/train/trainer.py ${config_path}
   ```
5. **权重转换（HF ↔ DCP）**：以 meta device 初始化时（`training.init_model_with_meta_device: true`）需加载 DCP，使用 `mm-convert GenericDCPConverter hf_to_dcp --hf_dir ... --dcp_dir ...`。
6. **Megatron-FSDP2 关键参数**：`sharding_size`（默认 1，取值 `auto` 或整数）、`sub_modules_to_wrap`、`ignored_modules`、`recompute_modules`、`reshard_after_forward`、`param_dtype/reduce_dtype/output_dtype`（`bf16/fp16/fp32`）、`num_to_forward_prefetch`、`num_to_backward_prefetch`、`offload_to_cpu`、`pin_memory` 等。

---

## 【关键机制与数据】

### 工作原理（原文）

- **FSDP1 → FSDP2**：FSDP1 通过 `FlatParameter` 把一组参数展平拼接为一个通信桶；FSDP2 移除该机制，改用沿 0 维分片的 `DTensor` 表示每个分片参数，使单参数粒度的差异化操作（冻结、精度转换）成为可能，且分片状态字典无需额外通信。
- **原生 FSDP2 入口与配置**：由 `mindspeed_mm/fsdp/train/trainer.py` 入口和一份 YAML 配置文件驱动；必须 `export NON_MEGATRON=true`，否则不会启用原生 FSDP2 所需的算子适配；YAML 采用六段式结构。
- **Megatron-FSDP2 入口**：复用 Megatron `pretrain_*.py`，通过 `--use-torch-fsdp2` 启用，分片参数由 `fsdp2_config.yaml` 提供；启动需 `export CUDA_DEVICE_MAX_CONNECTIONS=2`（不能为 1）。
- **`reshard_after_forward` 机制**：
  - `True`：前向后立即重新分片，反向再次 all-gather（更省显存）。
  - `False`：前向后保留聚合参数，反向不再 all-gather（省通信但更占显存）。
- **CPU 卸载与通信组**：`offload_to_cpu=True` 时需在入口脚本设置双后端通信组 `--distributed-backend npu:hccl,cpu:gloo`；`pin_memory` 仅在开启 `offload_to_cpu` 时生效。
- **混精机制**：FSDP2 混精在 YAML 中配置生效，`--bf16` 不再必要；为保持与 `--bf16` 计算行为对齐，新增 `--downcast-to-bf16` 在权重加载阶段 downcast；默认保持加载权重精度不变（推荐行为，避免精度损失）。

### 性能数据（原文）

> **原文：** 针对 Llama-7B，FSDP2 相比 FSDP1 实现了更高的 MFU，峰值内存降低 **7%**，且保持相同的损失曲线。

---

## 【表格解读】

### 表 1：原生 FSDP2 的 YAML 六段式配置结构

| 配置段 | 作用 |
| --- | --- |
| `parallel` | 并行与分片策略（FSDP 分片、张量并行、序列并行、专家并行） |
| `model` | 模型来源、注意力实现、融合算子等 |
| `data` | 数据集、预处理与 DataLoader |
| `features` | loss、重计算、激活值卸载、Chunk Loss 等优化特性 |
| `training` | 优化器、学习率、迭代步数、权重加载/保存等 |
| `tools` | profiling、内存分析等工具 |

**逐行解读：**
- `parallel`：负责声明分布式训练的多维并行策略，与 FSDP2 的核心能力（参数分片）直接对应，同时也覆盖张量并行、序列并行与专家并行。
- `model`：定义模型本身的来源与结构层面的选择（注意力实现、融合算子），是单参数级操作（精度、冻结等）的承载点。
- `data`：负责数据集、预处理与 DataLoader 装配，与模型分片解耦。
- `features`：覆盖训练中的优化特性开关（loss、重计算、激活值卸载、Chunk Loss），与 FSDP2 的内存优化能力互补。
- `training`：集中优化器、学习率、迭代步数以及权重加载/保存（如 DCP 格式的 `training.load` 指向转换输出）。
- `tools`：提供 profiling、内存分析等观测工具，便于排查 FSDP2 启用后的性能与内存表现。

### 表 2：Megatron-FSDP2 `fsdp2_config.yaml` 参数（原文以列表形式给出，结构化汇总如下）

| 配置项 | 描述 | 取值 / 格式 | 默认 |
| --- | --- | --- | --- |
| `sharding_size` | 控制模型并行度（张量分片） | `"auto"` 或整数值 | 1 |
| `sub_modules_to_wrap` | 使用 FSDP 进行参数分片的子模块 | 点号分隔路径，支持精确路径与模式匹配（`{*}`, `{0-20,22-40}`） | — |
| `ignored_modules` | 排除 FSDP 管理的模块类列表 | 同 `sub_modules_to_wrap` | — |
| `recompute_modules` | 配置激活值重计算（以计算换内存） | 同 `sub_modules_to_wrap`；与 Megatron 完全重计算冲突，需关闭 | — |
| `use_reentrant` | 检查点实现类型（是否可重入） | `True` / `False` | `True` |
| `reshard_after_forward` | 前向结束后是否对参数重新分片 | `True`（省显存）/ `False`（省通信） | — |
| `param_dtype` | 参数存储与计算的数据类型 | `"bf16"`, `"fp16"`, `"fp32"` | — |
| `reduce_dtype` | 梯度规约操作的数据类型 | `"bf16"`, `"fp16"`, `"fp32"` | — |
| `output_dtype` | 前向输出的数据类型 | `"bf16"`, `"fp16"`, `"fp32"` | — |
| `cast_forward_inputs` | 前向传播输入的自动类型转换 | `True` / `False` | — |
| `num_to_forward_prefetch` | 前向传播期间预取参数的后续层数 | 整数 | — |
| `num_to_backward_prefetch` | 反向传播期间预取参数的后续层数 | 整数 | — |
| `offload_to_cpu` | 参数/梯度/优化器状态卸载到 CPU 内存 | `True` / `False` | `False` |
| `pin_memory` | 锁定 CPU 内存以提高传输效率（需开启 `offload_to_cpu`） | `True` / `False` | — |

**逐行解读：**
- `sharding_size`：决定 FSDP 分片组大小；`auto` 由框架根据可用设备自动选取最优值，整数则为固定分片组大小（1 即关闭分片）。
- `sub_modules_to_wrap`：FSDP2 的核心开关，精确指定哪些子模块参与参数分片；支持 `model.model.deepstack_merger_list.{*}` 这类通配与区间语法，灵活度高于 FSDP1 的桶模式。
- `ignored_modules`：从 FSDP 管理中排除特定模块，避免无关子图（如视觉编码器 `image_encoder`）被分片。
- `recompute_modules`：在 FSDP 内部启用激活值重计算，进一步压低显存；与 Megatron 的 `--recompute-*` 系列开关互斥。
- `use_reentrant`：选择 checkpoint 实现是否可重入，默认 True。
- `reshard_after_forward`：在前向后立即把参数重新打散（True，显存友好）还是保留聚合形式（False，通信友好），是 FSDP 的核心 trade-off。
- `param_dtype` / `reduce_dtype` / `output_dtype`：分别控制参数、梯度规约、前向输出的数据类型；典型组合为 `param_dtype=bf16`、`reduce_dtype=fp32` 以兼顾速度与数值稳定。
- `cast_forward_inputs`：是否对前向输入做自动类型转换，配合 `param_dtype` 使用。
- `num_to_forward_prefetch` / `num_to_backward_prefetch`：分别控制前向/反向时预取后续层的参数个数，用于隐藏通信。
- `offload_to_cpu` / `pin_memory`：把状态卸载到 CPU（`pin_memory=True` 时锁定页内存以加速 H2D/D2H）。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **FSDP2 开发者迁移指南**（[`fsdp2_developer_migration_guide.md`](fsdp2_developer_migration_guide.md)）：本文在「原生 FSDP2」章节末尾指引读者参阅该指南，获取六段式 YAML 各字段的详细含义，作为配置参考的下游文档。
- **权重转换文档**（[`../pytorch/weight_conversion.md`](../pytorch/weight_conversion.md)）：本文「权重转换」一节指向该文档，用于了解 `dcp_to_hf`、完整参数说明以及个别模型的专用转换器，构成 HF ↔ DCP 双向转换的上游参考。
- **上游依赖关系**：原生 FSDP2 依赖算子适配（通过 `export NON_MEGATRON=true` 启用），与基于 Megatron 的 FSDP2 在配置体系上不通用；Megatron-FSDP2 与 Megatron 的分布式优化器、`--recompute-*` 系列、`--bf16` 等命令行参数存在显式互斥/冲突关系。
- **示例资产**：原生 FSDP2 的示例脚本 `examples/qwen3_5/finetune_qwen3_5_4B.sh` 与 `examples/qwen3_5/qwen3_5_4B_config.yaml` 为配置文件与启动方式的参考实现。

---

## 【使用方法】

### 启用方式

#### 原生 FSDP2（推荐）

1. 在启动脚本中先设置 `export NON_MEGATRON=true`（必须，否则不会启用算子适配）。
2. 用 `torchrun` 拉起 `mindspeed_mm/fsdp/train/trainer.py`，并将 YAML 配置路径作为唯一参数传入：
   ```shell
   export NON_MEGATRON=true
   torchrun $DISTRIBUTED_ARGS mindspeed_mm/fsdp/train/trainer.py ${config_path}
   ```
3. 准备 YAML 配置文件（参考 `examples/qwen3_5/qwen3_5_4B_config.yaml`），六段式结构：`parallel` / `model` / `data` / `features` / `training` / `tools`。

#### 基于 Megatron 的 FSDP2（不推荐，将淘汰）

1. 在 Megatron 入口脚本（`pretrain_*.py`）中传入以下命令行参数：
   ```shell
   export CUDA_DEVICE_MAX_CONNECTIONS=2 # 设置不能为1
   --use-torch-fsdp2 \
   --fsdp2-config-path ./fsdp2_config.yaml \
   --ckpt-format torch_dcp \
   --untie-embeddings-and-output-weights \
   # 注意不能打开分布式优化器
   ```
2. 准备 `fsdp2_config.yaml`，典型配置示例：
   ```shell
   sharding_size: auto
   sub_modules_to_wrap:
     - "text_decoder.output_layer"
     - "text_decoder.embedding"
     - "text_decoder.rotary_pos_emb"
     - "text_decoder.decoder.layers.{*}"
   param_dtype: "bf16"
   reduce_dtype: "fp32"
   cast_forward_inputs: True
   ignored_modules:
     - "image_encoder"
   recompute_modules:
     - "text_decoder.decoder.layers.{*}"
   num_to_forward_prefetch: 2
   num_to_backward_prefetch: 2
   offload_to_cpu: False
   ```

### 权重转换

以 meta device 初始化模型（`training.init_model_with_meta_device: true`）时需加载 DCP 权重，先用 `mm-convert` 将 HuggingFace 权重转换为 DCP，并将 `training.load` 指向转换输出（`release` 文件夹的上一级目录）：

```shell
mm-convert GenericDCPConverter hf_to_dcp \
    --hf_dir ckpt/hf_path/xxx \
    --dcp_dir ckpt/dcp_path/xxx
```

训练后导出 HF 权重（`dcp_to_hf`）、完整参数说明及个别模型的专用转换器，详见 [`../pytorch/weight_conversion.md`](../pytorch/weight_conversion.md)。

### 关键注意事项（原文要点摘录）

- **原生 FSDP2**：必须设置 `export NON_MEGATRON=true`；原生与 Megatron-FSDP2 配置体系不通用（字段不可混用）。
- **Megatron-FSDP2**：
  1. 需关闭分布式优化器及其相关配置。
  2. 权重保存格式 `--ckpt-format` 仅支持 `torch_dist` 或 `torch_dcp`：
     - `torch_dist`：模型需实现 `sharded_state_dict()`，且所有权重 0 维 size ≥ `sharding_size`。
     - `torch_dcp`：模型需实现 `state_dict_for_save_checkpoint()`，其返回值需与 `model.state_dict()` 一致。
  3. 需关闭重计算相关配置：`--recompute-granularity`、`--recompute-method`、`--recompute-num-layers`。
  4. `offload_to_cpu=True` 时需设置双后端通信组 `--distributed-backend npu:hccl,cpu:gloo`。
  5. 极大模型推荐启用 `--init-model-with-meta-device` 与 `--no-initialization`，避免一次性加载完整参数导致 OOM 并减少初始化等待。
  6. FSDP2 混精在 YAML 中生效，`--bf16` 不再必要；与断点续训存在冲突，需与 `--no-save-optim` 与 `--no-load-optim` 一同启用；通过 `--downcast-to-bf16` 在权重加载阶段做 downcast 以保持与 `--bf16` 一致性；默认保持加载权重精度不变（推荐）。
  7. `--untie-embeddings-and-output-weights=True` 会导致原本权重绑定的模型失效，当前框架不支持，需用户在权重转换阶段手动复制 `lm_head` 与 `embeddings`（注意此时模型结构会发生变化）。
