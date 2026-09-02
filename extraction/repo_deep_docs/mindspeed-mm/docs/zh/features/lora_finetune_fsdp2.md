# FSDP2 后端 LoRA 微调

> 仓 `mindspeed-mm` · 路径 `docs/zh/features/lora_finetune_fsdp2.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-mm/docs/zh/features/lora_finetune_fsdp2.md

# FSDP2 后端 LoRA 微调 —— 一体化深度解读

## 【定位】

本文档解决的是：在 MindSpeed MM 套件的 **FSDP2 分布式训练后端**下，如何**脱离 Megatron 框架依赖**，仅通过 YAML 配置文件即可完成多模态大模型（Qwen3-VL 系列等）的 **LoRA 低秩适配微调**任务，涵盖原理、配置、模块匹配、权重加载/保存/合并、断点续训及 MoE 模型特殊处理等完整链路。

---

## 【技术要点】

1. **核心机制：低秩权重分解**。在每一层权重矩阵上并行注入两个低秩矩阵 $A$ 与 $B$，更新后权重 $W' = W + A \cdot B$，基础权重 $W$ 冻结，仅训练 $A$、$B$。这是原文给出的唯一公式。
2. **配置入口：YAML 的 `training.lora` 字段**。无需任何额外命令行参数（如 Megatron 后端的 `--lora-r`、`--lora-alpha`），整套 LoRA 行为由 8 个参数控制：`enable`、`rank`、`alpha`、`target_modules`、`dropout`、`init_lora_weights`、`pretrained_lora_path`、`disable_peft_moe_conversion`。
3. **关键默认值与经验比例**。`rank=8`、`alpha=16`，即 $\alpha/r = 2$；`target_modules` 默认 `["q_proj", "k_proj", "v_proj"]`；`dropout=0.0`；`init_lora_weights=True`（支持 `gaussian`/`eva`/`olora`/`pissa`/`pissa_niter_[n]`/`corda`/`loftq`/`orthogonal` 等字符串初始化方案）。
4. **三种 `target_modules` 匹配模式**：
   - **`all-linear` 关键字（推荐）**：自动扫描模型中所有 `nn.Linear` 注入 LoRA，配合 `model.freeze` 排除 ViT/aligner 等多模态组件；
   - **精确匹配**：直接列模块名（如 `q_proj`），匹配所有同名后缀模块；
   - **通配符匹配**：使用 `{*}` 占位符，可精确控制到 Attention 或 MLP 的具体子层（如 `model.language_model.layers.{*}.self_attn.q_proj`）。
5. **MoE 模型特殊行为**。`all-linear` 会命中 `shared_expert` 的 `gate_proj`/`up_proj`/`down_proj`；路由专家（router experts）的 `nn.Parameter` 参数**暂不支持** LoRA 微调（功能开发中）。`disable_peft_moe_conversion=true` 用于屏蔽 PEFT 对 `gate_proj`/`up_proj`/`down_proj` 的自动重定向，使 LoRA 落在 `shared_expert` 的 `nn.Linear` 上。
6. **工程化与生态集成**。权重保存为 `lora_adapter.safetensors` 单文件（适配器形式），FSDP2 自动处理 DTensor 分片；通过 `merge_lora_safetensors_to_base.py` 可合并为完整 HuggingFace 权重；断点续训需启用 `no_save_optim`/`no_save_rng`/`no_load_optim`/`no_load_rng` 以恢复优化器状态；启动时自动校验 NaN/Inf，LoRA 参数自动升精度至 `float32`；依赖 `peft` 库（`pip install peft`）。当前文档明确支持的模型为：**qwen3vl、qwen3.5、qwen3.6、qwen3.8、qwen3omni**。

---

## 【关键机制与数据】

- **工作原理（原文）**：LoRA 通过低秩矩阵 $A$、$B$ 替代直接权重更新，由于秩较低，所需参数量显著减少，节省存储与计算成本。基础权重 $W$ 在 LoRA 开启后被**自动冻结**，仅 LoRA 适配器参数参与训练。
- **数据流（原文）**：
  1. YAML 配置解析 → `training.lora` 字段 → 框架依据 `target_modules` 匹配规则扫描模型；
  2. 启动时打印「LoRA 配置摘要」（含匹配的模块数量、可训练参数量）；
  3. 训练过程中 `float32` 精度训练 LoRA 参数；
  4. 保存时仅写出 `lora_adapter.safetensors`（safetensors 格式）；
  5. 加载时通过 `pretrained_lora_path` 加载续训，支持 `.safetensors` 与 `.pt/.bin`；
  6. 部署/导出时通过 `merge_lora_safetensors_to_base.py` 合并到 HF 权重。
- **性能数据（原文）**：原文未给出具体的训练速度、显存占用或吞吐数字；可观察到的"定量参数"仅为配置默认值（rank=8、alpha=16、dropout=0.0）以及 $\alpha/r = 2$ 的经验比例。

---

## 【表格解读】

> 原文表格：**参数说明**

| 参数 | 类型 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- |
| `enable` | bool | `false` | 是否开启 LoRA 微调 |
| `rank` | int | `8` | LoRA 低秩矩阵的维度。较低的 rank 值会使用更少的参数更新，减少计算量和内存消耗 |
| `alpha` | int | `16` | 控制 LoRA 权重对原始权重的影响比例，数值越高影响越大。一般保持 `α/r` 为 2 |
| `target_modules` | str \| List[str] | `["q_proj", "k_proj", "v_proj"]` | 需要添加 LoRA 的模块名称，或者通配符模式，或特殊关键字 `all-linear` |
| `dropout` | float | `0.0` | LoRA 层的 dropout 比例，取值范围 `[0, 1)` |
| `init_lora_weights` | bool \| str | `True` | 权重初始化方式。`True`；`False`；或选择以下字符串值：`"gaussian"`, `"eva"`, `"olora"`, `"pissa"`, `"pissa_niter_[number of iters]"`, `"corda"`, `"loftq"`, `"orthogonal"` |
| `pretrained_lora_path` | str | `null` | 预训练 LoRA 权重路径（可选），支持 `.safetensors` 和 `.pt/.bin` 格式 |
| `disable_peft_moe_conversion` | bool | `true` | 屏蔽 PEFT 对 MoE 模型 `gate_proj`/`up_proj`/`down_proj` 的 `target_modules→target_parameters` 自动重定向，使 LoRA 打在 `shared_expert` 的 `nn.Linear` 而非路由专家的 `nn.Parameter` 上。仅 MoE 模型相关 |

**逐行解读**：

- **`enable` / 默认 `false`**：总开关，必须显式置 `true` 才进入 LoRA 分支；这也意味着同一份 YAML 可在全量微调与 LoRA 微调之间无侵入切换。
- **`rank` / 默认 `8`**：低秩矩阵的秩，直接决定新增可训练参数量。原文强调"rank 越低 → 参数越少 → 计算/内存越省"，但代价是表达能力下降，使用者需在 `target_modules` 覆盖范围与 `rank` 之间权衡。
- **`alpha` / 默认 `16`**：LoRA 缩放因子，与 `rank` 联用形成实际缩放比例 $\alpha / r$。原文建议保持 `α/r = 2`（即默认 16/8 = 2 恰好符合），数值越高 LoRA 越能"压过"原始权重 $W$。
- **`target_modules` / 默认 `["q_proj", "k_proj", "v_proj"]`**：仅默认注入到 Attention 的 QKV 投影矩阵，是 LoRA 论文最经典的最小侵入配置；通过 `all-linear` 关键字可一键扩展到全量 `nn.Linear`。
- **`dropout` / 默认 `0.0`，取值 `[0, 1)`**：用于 LoRA 适配层的随机失活，训练数据极少时可适当调高以缓解过拟合。
- **`init_lora_weights` / 默认 `True`**：初始化策略。`True` 对应默认（等价于 `"default"` 风格）Kaiming 初始化；字符串值提供 8 种高级初始化：`gaussian`（高斯）/ `eva` / `olora` / `pissa`（含迭代版 `pissa_niter_[n]`）/ `corda` / `loftq` / `orthogonal`，其中 `pissa`、`loftq` 等为与初始化相关的近期改进方案。
- **`pretrained_lora_path` / 默认 `null`**：用于续训或迁移；支持 safetensors（推荐，更安全）与 PyTorch 传统 `.pt/.bin` 格式。
- **`disable_peft_moe_conversion` / 默认 `true`，仅 MoE 相关**：防止 PEFT 库把 `shared_expert` 中的 `gate_proj`/`up_proj`/`down_proj` 错误地重定向到**路由专家**的 `nn.Parameter`，确保 LoRA 仅落在共享专家的 `nn.Linear` 上。这是 MoE 模型接入 LoRA 的关键开关。

---

## 【公式解读】

> 原文公式（LaTeX 形式逐字保留）：

$$
W' = W + A \cdot B
$$

**符号说明**：

- $W$：**原始权重矩阵**（预训练大模型的固定参数），在 LoRA 模式下被冻结，不参与梯度更新。
- $A$：**低秩矩阵之一**（一般形状为 $d \times r$），随机初始化并参与训练，是 LoRA 适配器权重的"输入侧"矩阵。
- $B$：**低秩矩阵之一**（一般形状为 $r \times k$），常初始化为全零（这样训练开始时 $A \cdot B = 0$，模型行为与原始一致），参与训练，是"输出侧"矩阵。
- $r$：低秩维度，由 YAML 中 `rank` 字段控制（默认 `8`），$r \ll \min(d, k)$，是 LoRA 节省参数的根本来源。
- $A \cdot B$：两个低秩矩阵的乘积，形状与 $W$ 相同（$d \times k$），但内部秩不超过 $r$，因而参数总量为 $r \cdot (d + k)$，远小于 $d \cdot k$。
- $W'$：**更新后的有效权重**，推理时等价于把 $A \cdot B$ 加到 $W$ 上；训练过程中前向用 $W'$、反向只对 $A$、$B$ 求梯度。

**作用**：该公式表达了 LoRA 的"权重增量低秩化"思想——把全参数微调的 $\Delta W$（$d \times k$）替换为两个低秩矩阵的乘积 $A \cdot B$，从而以极少的可训练参数实现与全量微调相近的表达能力。

---

## 【关联】

- **与多模态组件的耦合**：`target_modules: all-linear` 会无差别命中 ViT、aligner（merger）、language_model 的所有 `nn.Linear`。文档指出需通过 `model.freeze` 排除 `model.visual`（整个视觉塔，含 merger/aligner）或更细粒度的 `model.visual.blocks`（仅排除 ViT blocks，保留 aligner LoRA），从而将 LoRA 局限在 `language_model`。
- **与 MoE 模型的耦合**：MoE 模型下 `all-linear` 命中 `shared_expert` 的 `gate_proj`/`up_proj`/`down_proj`；路由专家的 `nn.Parameter` 暂不支持 LoRA（开发中）。`disable_peft_moe_conversion` 是专门针对 PEFT 库行为的开关。
- **与 PEFT 库的关系**：功能依赖 `peft`（`pip install peft`）；`init_lora_weights` 字符串选项、`disable_peft_moe_conversion` 语义均源自 PEFT 生态。
- **与 Megatron 后端的对比**：FSDP2 后端使用 YAML 配置；Megatron 后端则通过命令行参数（`--lora-r`、`--lora-alpha` 等），原文明确点出该差异。
- **与权重保存/合并工具链**：训练产物 `lora_adapter.safetensors` 通过 `checkpoint/common/merge_lora_safetensors_to_base.py` 与 HuggingFace 基座权重（`--base_hf_dir`）合并为 `merged_xxx` 完整权重。
- **与断点续训的耦合**：依赖标准 checkpoint 加载机制，需启用 `no_save_optim`/`no_save_rng`/`no_load_optim`/`no_load_rng` 四个开关以恢复优化器状态。
- **与分布式训练（FSDP2）的耦合**：LoRA 权重保存自动处理 DTensor 分片，无需额外配置。
- **支持模型谱**（原文明确列出）：qwen3vl、qwen3.5、qwen3.6、qwen3.8、qwen3omni。
- **参考文献**：LoRA 原论文 *LoRA: Low-Rank Adaptation of Large Language Models* (arXiv:2106.09685)。
- **内部链接**：原文未提供任何内部链接（标注为"无"）。

---

## 【使用方法】

1. **安装依赖**（原文注意事项）：
   ```bash
   pip install peft
   ```

2. **在模型 YAML 配置文件中开启 LoRA**（以 `examples/qwen3_5/qwen3_5_35B_config.yaml` 为例）：
   ```yaml
   training:
     micro_batch_size: 1
     gradient_accumulation_steps: 8
     lr: 1.0e-4
     train_iters: 100
     save_interval: 20
     save: ./save_path
     lora:
       enable: true
       rank: 8
       alpha: 16
       target_modules: all-linear
       dropout: 0.0
       init_lora_weights: true
       pretrained_lora_path: null
   ```

3. **多模态组件排除（仅 LoRA 打在语言模型）**：
   ```yaml
   model:
     freeze:
       - model.visual
   lora:
     target_modules: all-linear
   ```

4. **MoE 模型专属配置**：
   ```yaml
   lora:
     target_modules: all-linear
     disable_peft_moe_conversion: true
   ```

5. **加载预训练 LoRA 权重续训**：
   ```yaml
   training:
     lora:
       enable: true
       pretrained_lora_path: ./save_path/iter_xxx
   ```

6. **断点续训**：YAML 中 `load` 指向上次 checkpoint 路径；前一次训练配置 `no_save_optim`/`no_save_rng: false`，续训时配置 `no_load_optim`/`no_load_rng: false`。

7. **启动训练**（与全量微调共用脚本，无需特殊命令行参数）：
   ```bash
   bash examples/qwen3_5/finetune_qwen3_5_xxB.sh
   ```
   启动后会**自动打印 LoRA 配置摘要**，包括匹配模块数量、可训练参数量等。

8. **合并 LoRA 到 HuggingFace 基座权重**：
   ```bash
   cd checkpoint/common
   python merge_lora_safetensors_to_base.py \
       --base_hf_dir ./Qwen3.5-27B \
       --lora_safetensors ./save_path/lora_adapter_iteration_10.safetensors \
       --save_merged_hf_dir ./merged_qwen3_5_27B_lora
   ```

9. **默认保存结构**（仅 LoRA 适配器）：
   ```bash
   save_path/
   ├── lora_adapter.safetensors
   └── ...
   ```
