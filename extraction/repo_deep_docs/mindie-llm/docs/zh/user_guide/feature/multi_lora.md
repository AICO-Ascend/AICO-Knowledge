# Multi-LoRA

> 仓 `mindie-llm` · 路径 `docs/zh/user_guide/feature/multi_lora.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-llm/docs/zh/user_guide/feature/multi_lora.md

# Multi-LoRA 特性文档深度解读

## 【定位】

本文档描述了 MindIE LLM 推理引擎中 **Multi-LoRA**（多 LoRA 适配器并行推理）特性：在加载单一基础模型的前提下，使推理服务能够按请求携带不同的 LoRA ID，动态匹配对应的 LoRA 适配器权重进行轻量级微调推理，从而在显存有限的情况下支撑多场景/多任务的高效部署。

---

## 【技术要点】

1. **LoRA 原理公式**：原始权重被分解为 $W' = W + BA$，其中 $B$ 与 $A$ 为低秩矩阵，乘积结果合入线性层向下传递，达到大模型轻量级微调目的。
2. **Multi-LoRA 匹配机制**：每个推理请求携带一个指定的 LoRA ID；引擎依据 ID 动态匹配对应 LoRA 权重；部署服务时 LoRA 权重与基础模型权重预先加载至显存中。一个推理请求至多使用一个 LoRA 权重，且兼容推理请求不使用 LoRA 权重（即使用基础模型）的场景。
3. **LoRA 权重文件要求**：权重目录必须包含 `adapter_config.json`（含 `r`、`rank_pattern`、`lora_alpha`、`alpha_pattern` 等超参）和 `adapter_model.safetensors`（键名前增加 `base_model.model.` 前缀、键名后增加 `.lora_A.weight` / `.lora_B.weight` 后缀）。
4. **大模型并行方案**：若模型参数量过大无法单卡加载，可启用 Tensor Parallel 并行。
5. **三大接口兼容**：仅支持 vLLM 接口、TGI 接口以及 vLLM 兼容 OpenAI 接口；动态加载/卸载 LoRA 仅在 ATB Models 使用 Python 组图方式时支持。
6. **三大新增服务化参数**：`maxLoras`（最大可加载 LoRA 数量）、`maxLoraRank`（可加载 LoRA 的最大秩）、`LoraModules`（LoRA 模块绑定关系列表，含 `name`/`path`/`baseModelName` 三字段）。

---

## 【关键机制与数据】

### 工作原理（原文）

- 推理时通过 LoRA ID 动态匹配对应的 LoRA 权重。
- LoRA 权重与基础模型权重在部署时即预先加载至显存。
- 一次请求至多使用一个 LoRA 权重，且允许请求"不使用 LoRA"（即退回基础模型）。
- 动态加载/卸载 LoRA 权重通过 `/v1/load_lora_adapter`、`/v1/unload_lora_adapter` 管理端口 API 实现；查询已加载模型则通过 `/v1/models` 业务端口实现。
- 推理请求中的 `"model"` 参数取值为基础模型名（不使用 LoRA）或 LoRA ID（启用对应 LoRA 权重）时，行为有所区分。

### 关键数据（原文：约束与限制）

- **硬件支持**：Atlas 800I A2 推理服务器、Atlas 800I A3 超节点服务器、Atlas 300I Duo 推理卡。
- **LoRA 数量上限**：受显存限制，**建议数量 ≤ 10 个**。
- **LoRA 名称长度上限**：≤ 256 字符。
- **支持模型清单（8 个）**：Qwen2.5-7B、Qwen2.5-14B、Qwen2.5-32B、Qwen2.5-72B、Qwen3-32B、LLaMA3.1-8B、LLaMA3.1-70B、Qwen2-72B。
- **互斥特性**：量化、PD 分离、并行解码、SplitFuse、MTP、异步调度、Micro Batch、Prefix Cache 均不能与 Multi-LoRA 同时开启。
- **配置示例（服务化）**：`maxLoras=4`、`maxLoraRank=296`、8 卡 TP（`worldSize=8`、`npuDeviceIds=[0..7]`）。

---

## 【表格解读】

### 表 1：LoRA 权重的文件说明

| 文件名称 | 文件描述 | 示例 |
|---|---|---|
| adapter_config.json | 包含 LoRA 权重的超参。 | r（LoRA 微调中的秩大小），rank_pattern，lora_alpha（LoRA 低秩矩阵的缩放系数）和 alpha_pattern。 |
| adapter_model.safetensors | 包含权重，权重以键值对的形式保存，其中 LoRA 权重的键名在基础模型的键名前后增加 "base_model.model" 前缀和 "lora_A.weight"、"lora_B.weight" 后缀。 | 基础模型中的键名为 "model.layers.9.self_attn.v_proj.weight" 时，则 LoRA 权重中对应的键名为："base_model.model.model.layers.9.self_attn.v_proj.lora_A.weight" 和 "base_model.model.model.layers.9.self_attn.v_proj.lora_B.weight"。 |

**解读**：
- 第一行说明 LoRA 超参存放在 JSON 配置文件中，必须包含 `r`、`lora_alpha` 等核心参数（`rank_pattern` 与 `alpha_pattern` 是按模块粒度覆盖上述超参的可选项）。
- 第二行描述权重文件命名映射规则：基础模型键名前拼接 `base_model.model.` 前缀，再将末尾 `.weight` 替换/追加为 `.lora_A.weight` 与 `.lora_B.weight`。例中 `model.layers.9.self_attn.v_proj.weight` 是 LLaMA 类模型 attention value 投影层的权重；其 LoRA 适配权重通过 A、B 两个低秩矩阵恢复，便于推理引擎按层精准注入。

### 表 2：Multi-LoRA 特性补充参数：**ModelDeployConfig 中的参数**

| 配置项 | 取值类型 | 取值范围 | 配置说明 |
|---|---|---|---|
| maxLoras | uint32_t | 上限根据显存和用户需求来决定，最小值需大于 0。 | 最大可加载的 LoRA 数量。选填，开启 LoRA 权重动态加载和卸载时需配置。默认值为 0。 |
| maxLoraRank | uint32_t | 上限根据显存和用户需求来决定，最小值需大于 0。 | 可加载 LoRA 权重最大的秩。选填，开启 LoRA 权重动态加载和卸载时需配置。默认值为 0。 |
| **LoraModules** | - | - | - |
| name | string | 由大写字母、小写字母、数字、中划线和下划线组成，且不以中划线和下划线作为开头和结尾，字符串长度小于或等于 256。 | 必填，LoRA ID。 |
| path | string | 文件绝对路径长度的上限与操作系统的设置（Linux 为 PATH_MAX）有关，最小值为 1。 | 必填，LoRA 权重路径。该路径会进行安全校验，需要和执行用户的属组和权限保持一致。 |
| baseModelName | string | 由大写字母、小写字母、数字、中划线、点和下划线组成，且不以中划线、点和下划线作为开头和结尾，字符串长度小于或等于 256。 | 必填，基础模型名称。与 ModelConfig 参数说明中的 modelName 参数保持一致。 |

**解读**：
- `maxLoras` 与 `maxLoraRank` **仅在需要动态加载/卸载时必填**，默认 0 表示不启用动态管理；上限由显存与业务需求共同决定。
- `LoraModules` 是一组键值绑定，**每一项**需明确三个字段：
  - `name` 即请求体中 `"model"` 字段可填写的 LoRA ID，须符合正则式（字母/数字/`-`/`_`，首尾不得为分隔符，长度 ≤ 256）。
  - `path` 是 LoRA 权重文件绝对路径，受 Linux `PATH_MAX` 上限约束，且引擎会做属组/权限安全校验。
  - `baseModelName` 须与 `ModelConfig.modelName` 完全一致，确保 LoRA 与基础模型严格绑定，避免错配。

---

## 【公式解读】

原文公式：

$$W' = W + BA$$

**符号含义与解读**：

| 符号 | 含义 | 作用 |
|---|---|---|
| $W$ | 原始权重矩阵（大模型预训练权重） | 推理时的基底权重，被冻结不更新 |
| $B$、$A$ | 两个低秩矩阵（LoRA 微调产物） | 训练参数量远小于 $W$，承担"微调量"的表达 |
| $BA$ | 低秩矩阵乘积 | 以极小参数量近似表达权重变化量 |
| $W'$ | 最终有效权重 | 推理时实际进入线性层的权重，与 $W$ 形状相同 |

**机制解读**：LoRA 通过将"权重更新量 $\Delta W$"约束为两个低秩矩阵的乘积（$BA$），使得微调阶段只需训练 $B$ 与 $A$ 的少量参数，而推理时只需将 $BA$ 合入线性层（$W + BA$）即可恢复微调效果，无需为每个微调任务保存一份完整的 $W$，从而实现"一份基础模型 + 多份轻量 LoRA"的 Multi-LoRA 部署模式。

---

## 【关联】

- **服务化参数配置主文档**：[`../user_manual/service_parameter_configuration.md`](../user_manual/service_parameter_configuration.md) —— 详细定义 `BackendConfig`、`ModelDeployConfig`、`ModelConfig` 等服务化参数体系；本文新增的 `maxLoras`、`maxLoraRank`、`LoraModules` 即嵌入于 `ModelDeployConfig` 之下。
- **离线推理参数手册**：[`../user_manual/offline_inference.md#table2`](../user_manual/offline_inference.md#table2) —— 提供 `run_pa` 脚本（如 `--lora_modules`、`--input_dict` 中 `"adapter"` 字段）的参数说明；纯模型（非服务化）路径下的 Multi-LoRA 推理直接依赖该脚本。
- **上游依赖**：
  - **CANN** 与 **ATB Models** 安装（参见《MindIE 安装指南》）—— 是执行推理、且在 ATB Models Python 组图下开启 LoRA 动态加载/卸载的前置条件。
  - **MindIE Motor `config.json`** —— 服务化场景下 Multi-LoRA 配置入口（含静态 `LoraModules` 与动态 `maxLoras`/`maxLoraRank`）。
- **下游/配套能力**：
  - **Tensor Parallel（TP）并行**：用于基础模型参数量过大、无法单卡加载的场景，与 LoRA 加载在同一服务内协同工作（示例中 `worldSize=8`、`npuDeviceIds=[0..7]`）。
  - **MindIE Service 管理/业务端口**：`load_lora_adapter`、`unload_lora_adapter` 走管理端口 `1026`；`/v1/models` 查询与 `/generate` 推理走业务端口 `1025`。

---

## 【使用方法】

### 1. 纯模型使用（ATB Models + `run_pa`）

- 前置：已安装 CANN 与 ATB Models，并 `source` 模型仓 `set_env.sh` 初始化 `${ATB_SPEED_HOME_PATH}`。
- 命令模板（原文 `bash` 示例）：
  ```bash
  cd ${ATB_SPEED_HOME_PATH}
  torchrun --nproc_per_node 8 --master_port 20030 -m examples.run_pa \
    --model_path {基础模型权重} \
    --max_output_length 20 --max_batch_size 3 \
    --input_dict '[{"prompt": "...", "adapter": "{Lora权重1的名称}"},
                  {"prompt": "...", "adapter": "{Lora权重2的名称}"},
                  {"prompt": "What is deep learning?", "adapter": "base"}]' \
    --lora_modules '{"{Lora权重1的名称}": "{Lora权重1的路径}",
                    "{Lora权重2的名称}": "{Lora权重2路径}"}'
  ```
- 关键点：每条请求 `"adapter"` 指定 LoRA 别名（`"base"` 表示不启用 LoRA）；`--lora_modules` 完成基础模型与多 LoRA 权重的绑定；`run_pa` 脚本参数详见离线推理手册表 2。

### 2. 服务化使用（MindIE Motor + config.json）

- **步骤 1**：编辑 `config.json`：
  - whl 包路径：`{MindIE 安装目录}/mindie_llm/conf/config.json`
  - run 包路径：`{MindIE 安装目录}/latest/mindie-service/conf/config.json`
- **步骤 2**：在 `ModelDeployConfig` 下添加 `maxLoras`、`maxLoraRank`、`LoraModules`（原文 JSON 示例中 `maxLoras=4`、`maxLoraRank=296`，`LoraModules` 单项 `name="adapter1"`、`path="/data/lora_model_weights/llama3.1-70b-lora"`、`baseModelName="llama3.1-70b"`）。
- **步骤 3**：启动服务：
  - whl 包：`mindie_llm_server`
  - run 包：`./bin/mindieservice_daemon`
- **步骤 4**：动态管理 LoRA：
  ```bash
  # 加载
  curl -X POST http://127.0.0.2:1026/v1/load_lora_adapter \
    -H "Content-Type: application/json" \
    -d '{"lora_name": "adapter2", "lora_path": "/data/lora_model_weights/llama3.1-70b-lora"}'
  # 卸载
  curl -X POST 127.0.0.2:1026/v1/unload_lora_adapter \
    -d '{"lora_name": "adapter2"}'
  # 查询
  curl http://127.0.0.1:1025/v1/models
  ```
- **步骤 5**：发送推理请求（业务端口 `1025`）：
  - `"model"` 填 **基础模型名称** → 不使用 LoRA 推理。
  - `"model"` 填 **LoRA ID**（如 `"adapter1"`）→ 启用对应 LoRA 权重推理。
  - 示例命令详见原文 `curl https://127.0.0.1:1025/generate` 段。

> 原文备注：旧的 `lora_adapter.json` 文件配置方式已下线，统一通过 `config.json` 中的 `LoraModules` 字段开启 Multi-LoRA 特性。
