# 目录结构

> 仓 `mindspeed-rl` · 路径 `docs/zh/dir_structure.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-rl/docs/zh/dir_structure.md

# mindspeed-rl 「目录结构」文档深度解读

---

## 【定位】

这篇文档是 mindspeed-rl 仓库的**目录结构总览（map/概览）型文档**，解决「新人/开发者进入仓库后如何快速定位代码、配置、示例、文档模块」的导航问题，描述了仓库从顶层目录到三级子目录的文件级组成，定位为纯结构性参考文档，而非原理/性能/使用方法文档。

---

## 【技术要点】

本文档为目录结构型 overview，本身不涉及算法机制。核心信息条目如下：

1. **仓库定位**：基于昇腾生态的强化学习加速框架，提供**端到端的RL训推解决方案**（原文用语）。
2. **顶层目录共 13 个一级目录/文件**：`ci/`、`cli/`、`configs/`、`docs/`、`examples/`、`mindspeed_rl/`、`tests/`、`verl_npu/`、`setup.py`、`requirements.txt`、`README.md`、`LICENSE`、`OWNERS`、`SECURITYNOTE.md`。
3. **算法入口矩阵（cli 层）**：覆盖 **DAPO、DPO、GRPO、PPO** 四种主流 RL 算法的训练入口，外加 `preprocess_data.py`（数据预处理）、`eplb_generate_map_ds.py`（EPLB 映射数据集生成）两类工具入口。
4. **配置覆盖矩阵（configs 层）**：模型覆盖 **Qwen2.5-7B/32B、Qwen3-8B/32B/30B-A3B/235B-A22B、DeepSeek-V3-671B/DeepSeek-R1-671B**；数据集覆盖 **DeepScaler、MATH-17K、Orca-RLHF**；并行度标识出现 **A2/A3/A3 EPLB**；序列长度变体出现 **20K/32K**；多轮变体出现 `multi_turn`。
5. **文档体系（docs/zh/）**：四大子目录——`algorithms/`（算法使用指南）、`features/`（30+ 项特性说明）、`solutions/`（端到端方案）、`install_guide.md`（安装指南）。
6. **核心框架分层（mindspeed_rl/）**：`config_cls/`（配置类）、`datasets/`（数据）、`models/`（含 actor/critic/reference/reward 四大角色 + loss/orm/rollout 三个子模块）。
7. **昇腾适配层存在性**：根目录有独立的 `verl_npu/`（verl 昇腾 NPU 适配层），`mindspeed_rl/models/rollout/vllm_adapter/`（vLLM 适配器，含 `fused_moe.py`、`megatron_weight_loaders.py`、`vllm_parallel_state.py`、`patch/`）。
8. **多模态支持**：`datasets/multimodal_dataset.py` + `datasets/mm_utils.py`，并出现 `qwen2_5_vl_reuse_vi...` 截断条目（指向 Qwen2.5-VL 多模态相关 patch）。
9. **CI/CD 范围**：仅列出一个脚本 `ci/access_control_test.py`（访问控制测试）。

> 说明：原文在 `models/rollout/vllm_adapter/patch/qwen2_5_vl_reuse_vi...` 处被截断（文末不完整），下文的还原与解读仅基于已展示内容。

---

## 【关键机制与数据】

本文档为目录结构总览，**不描述工作原理、数据流或性能数据**。

- 原文无任何性能数据（无吞吐/时延/精度数字）。
- 原文无任何工作原理描述（无算法公式、无计算流程、无调度时序）。
- 仅出现的可量化信息为：模型参数规模（**7B/8B/32B/30B-A3B/235B-A22B/671B**）、并行拓扑标识（**A2/A3**）、上下文长度变体（**20K/32K**），以及目录/文件数量层级（13 个顶层条目、30+ 项 features 文档、20+ 项 grpo/dapo/ppo/dpo YAML 配置、20+ 项 shell 启动脚本）。

性能 / 原理类内容须跳转至其他文档（如 `docs/zh/algorithms/*.md`、`docs/zh/features/*.md`、`docs/zh/solutions/*.md`）。

---

## 【表格解读】

原文包含 **8 个核心表格**（加上目录树代码块共 9 个结构块），下面按文档顺序**逐字还原**并逐行/逐表解读。

### 表 1. 顶层目录结构（原文以 `text` 代码块呈现，本质等价于表格）

| 文件/目录 | 说明 |
| --------- | ---- |
| `ci/` | CI/CD 流水线脚本 |
| `cli/` | 命令行入口脚本 |
| `configs/` | 训练配置文件 |
| `docs/` | 项目文档 |
| `examples/` | 训练示例脚本 |
| `mindspeed_rl/` | 核心 RL 训练框架 |
| `tests/` | 测试用例 |
| `verl_npu/` | verl 昇腾 NPU 适配层 |
| `setup.py` | 安装脚本 |
| `requirements.txt` | 依赖列表 |
| `README.md` | 项目说明 |
| `LICENSE` | 许可证 |
| `OWNERS` | 仓库维护者 |
| `SECURITYNOTE.md` | 安全声明 |

**解读**：14 项顶层元素（含目录/文件）。从职责看，可分四组——**框架代码**（`mindspeed_rl/`、`verl_npu/`）、**入口与配置**（`cli/`、`configs/`、`examples/`）、**工程支撑**（`ci/`、`tests/`、`setup.py`、`requirements.txt`）、**治理与文档**（`docs/`、`README.md`、`LICENSE`、`OWNERS`、`SECURITYNOTE.md`）。注意 `verl_npu/` 与 `mindspeed_rl/` 并列，说明项目既自研核心框架、又外置一个独立的对 verl 的 NPU 适配包。

---

### 表 2. `ci/` 目录

| 文件/目录 | 说明 |
| --------- | ---- |
| `access_control_test.py` | 访问控制测试脚本 |

**解读**：CI/CD 维度公开的脚本仅 1 个，且聚焦在「访问控制」而非功能回归/构建，提示该仓的 CI 主线工作在其他仓库或内部完成，本目录只保留最小子集。

---

### 表 3. `cli/` 目录（启动入口）

| 文件/目录 | 说明 |
| --------- | ---- |
| `train_dapo.py` | DAPO 算法训练入口 |
| `train_dpo.py` | DPO 算法训练入口 |
| `train_grpo.py` | GRPO 算法训练入口 |
| `train_ppo.py` | PPO 算法训练入口 |
| `preprocess_data.py` | 数据预处理入口 |
| `eplb_generate_map_ds.py` | EPLB 映射数据集生成入口 |

**解读**：4 个 RL 算法入口 + 2 个工具入口。**算法维度**直接对应主流 RLHF/RLVR 训练家族（PPO 是经典、GRPO/DAPO 是 R1 时代的无 critic 变体、DPO 是直接偏好优化）。**工具维度**：`preprocess_data.py` 与 `examples/data/preprocess_data.sh` 在名称上呼应；`eplb_generate_map_ds.py` 与 `examples/eplb/` 下脚本呼应，提示 EPLB（Expert Parallel Load Balance，详见 `docs/zh/features/EPLB.md`）需要独立的「映射数据生成」步骤。

---

### 表 4. `configs/` 目录（YAML 配置矩阵）

| 文件/目录 | 说明 |
| --------- | ---- |
| `checkpoint/` | 检查点配置目录 |
| `checkpoint/model_cfg.json` | 模型检查点配置 |
| `datasets/` | 数据集配置目录 |
| `datasets/deepscaler.yaml` | DeepScaler 数据集配置 |
| `datasets/math_17k.yaml` | MATH-17K 数据集配置 |
| `datasets/orca_rlhf.yaml` | Orca-RLHF 数据集配置 |
| `model/` | 模型配置目录 |
| `model/qwen25_7b.yaml` | Qwen2.5-7B 模型配置 |
| `model/qwen25_32b.yaml` | Qwen2.5-32B 模型配置 |
| `model/qwen3_8b.yaml` | Qwen3-8B 模型配置 |
| `model/qwen3_32b.yaml` | Qwen3-32B 模型配置 |
| `model/qwen3_30b_a3b.yaml` | Qwen3-30B-A3B 模型配置 |
| `model/qwen3_235b_a22b.yaml` | Qwen3-235B-A22B 模型配置 |
| `model/deepseekv3_671b.yaml` | DeepSeek-V3-671B 模型配置 |
| `model/templates.json` | 模型模板配置 |
| `tools/` | 工具配置目录 |
| `tools/retool_config.yaml` | ReTool 配置 |
| `tools/search_tool_config.yaml` | SearchTool 配置 |
| `grpo_qwen25_7b_A3.yaml` | GRPO + Qwen2.5-7B A3 配置 |
| `grpo_qwen25_32b_A2.yaml` | GRPO + Qwen2.5-32B A2 配置 |
| `grpo_qwen25_32b_A3.yaml` | GRPO + Qwen2.5-32B A3 配置 |
| `grpo_qwen3_8b_A3.yaml` | GRPO + Qwen3-8B A3 配置 |
| `grpo_qwen3_235b_a22b_A2.yaml` | GRPO + Qwen3-235B-A22B A2 配置 |
| `grpo_lora_qwen25_32b_A2.yaml` | GRPO LoRA + Qwen2.5-32B A2 配置 |
| `grpo_deepseek_r1_671b_A2.yaml` | GRPO + DeepSeek-R1-671B A2 配置 |
| `grpo_deepseek_r1_671b_A3.yaml` | GRPO + DeepSeek-R1-671B A3 配置 |
| `grpo_deepseek_r1_671b_A3_eplb.yaml` | GRPO + DeepSeek-R1-671B A3 EPLB 配置 |
| `dapo_qwen25_32b_A3.yaml` | DAPO + Qwen2.5-7B（注：原文文件名以 `qwen25_32b` 出现）A3 配置 |
| `dapo_qwen25_32b_A2_20k.yaml` | DAPO + Qwen2.5-32B A2 20K 配置 |
| `dapo_qwen25_32b_A3_32k.yaml` | DAPO + Qwen2.5-32B A3 32K 配置 |
| `dapo_qwen25_7b_A2_multi_turn.yaml` | DAPO + Qwen2.5-7B A2 多轮配置 |
| `dapo_qwen3_30b_a3b_A3.yaml` | DAPO + Qwen3-30B-A3B A3 配置 |
| `dapo_qwen3_32b_A3.yaml` | DAPO + Qwen3-32B A3 配置 |
| `ppo_qwen25_32b_A3.yaml` | PPO + Qwen2.5-32B A3 配置 |
| `dpo_qwen3_30b_a3b_A3.yaml` | DPO + Qwen3-30B-A3B A3 配置 |

> **逐字忠实还原**注：原文 `dapo_qwen25_32b_A3.yaml` 一行的「说明」列中出现了「DAPO + Qwen2.5-7B A3 配置」，与文件名 `qwen25_32b` 明显不一致；此处按原文逐字保留。

**解读**：这是仓库最稠密的一张配置矩阵，分四组：

1. **数据/模型/工具模板**：3 个数据集（DeepScaler 数学、MATH-17K 数学、Orca-RLHF 偏好）+ 7 个模型 yaml + 1 个模板 JSON + 2 个工具配置（ReTool、SearchTool）。
2. **GRPO 系列**（10 个）：覆盖 Qwen2.5-7B/32B、Qwen3-8B/235B-A22B、DeepSeek-R1-671B；并行度含 A2/A3/A3+eplb；并出现 `grpo_lora_*`（LoRA 变体）。
3. **DAPO 系列**（6 个）：覆盖 Qwen2.5-32B（含 20K/32K 上下文）、Qwen2.5-7B（multi_turn）、Qwen3-30B-A3B、Qwen3-32B；并行度主要为 A3。
4. **PPO/DPO 系列**（各 1 个）：PPO 仅 Qwen2.5-32B；DPO 仅 Qwen3-30B-A3B。这与 cli 层的算法矩阵呼应——PPO/DPO 的预置配置明显少于 GRPO/DAPO。

**配置命名规律**：`{算法}[_lora]_{模型}_{并行度}[_20k|_32k|_multi_turn|_eplb].yaml`，命名中显式编码了「算法 + 模型 + 并行拓扑 + 可选变体」四个维度。

---

### 表 5. `docs/` 目录

| 文件/目录 | 说明 |
| --------- | ---- |
| `zh/` | 中文文档目录 |
| `zh/algorithms/` | 算法说明文档 |
| `zh/algorithms/grpo.md` | GRPO 算法使用指南 |
| `zh/algorithms/dapo.md` | DAPO 算法使用指南 |
| `zh/algorithms/ppo.md` | PPO 算法使用指南 |
| `zh/algorithms/dpo.md` | DPO 算法使用指南 |
| `zh/features/` | 特性说明文档 |
| `zh/features/README.md` | 特性总览 |
| `zh/features/integrated_worker.md` | 训推共卡特性 |
| `zh/features/resharding.md` | 权重重切分特性 |
| `zh/features/remove_padding.md` | 填充移除特性 |
| `zh/features/context_parallel.md` | 长序列并行特性 |
| `zh/features/partial_rollout.md` | Partial Rollout 特性 |
| `zh/features/expert_parallel.md` | 专家并行特性 |
| `zh/features/EPLB.md` | EPLB 特性 |
| `zh/features/vpp.md` | VPP 特性 |
| `zh/features/offload.md` | Offload 特性 |
| `zh/features/recompute.md` | 重计算特性 |
| `zh/features/norm_recompute.md` | Norm 重计算特性 |
| `zh/features/activation_function_recompute.md` | 激活函数重计算特性 |
| `zh/features/chunked_prefill.md` | Chunked Prefill 特性 |
| `zh/features/acl_graph.md` | ACL Graph 特性 |
| `zh/features/grpo_lora.md` | GRPO LoRA 特性 |
| `zh/features/grpo_yaml.md` | GRPO YAML 配置说明 |
| `zh/features/ppo_yaml.md` | PPO YAML 配置说明 |
| `zh/features/multi_turn.md` | 多轮迭代训练特性 |
| `zh/features/data_module_design.md` | 数据调度模块设计 |
| `zh/features/task_queue.md` | 任务队列特性 |
| `zh/features/log_metrics.md` | 指标日志特性 |
| `zh/features/logging_wandb_tensorboard.md` | WandB/TensorBoard 日志特性 |
| `zh/features/logging_swanlab.md` | SwanLab 日志特性 |
| `zh/features/profiler.md` | 性能调优特性 |
| `zh/features/msprobe.md` | 精度分析特性 |
| `zh/features/deterministic_computation.md` | 确定性计算特性 |
| `zh/features/reuse_fp32_param.md` | FP32 参数复用特性 |
| `zh/features/swap_attention.md` | Attention Swap 特性 |
| `zh/features/swap_optimizer.md` | Optimizer Swap 特性 |
| `zh/features/runtime_env.md` | 运行时环境配置 |
| `zh/features/vLLM_prefix_cache.md` | vLLM 前缀缓存特性 |
| `zh/figures/` | 文档图片资源目录 |
| `zh/install_guide.md` | 安装指南 |
| `zh/solutions/` | 解决方案文档 |
| `zh/solutions/r1_zero_qwen25_7b.md` | R1-Zero + Qwen2.5-7B 方案 |
| `zh/solutions/r1_zero_qwen25_32b.md` | R1-Zero + Qwen2.5-32B 方案 |
| `zh/solutions/r1_zero_deepseek_671b.md` | R1-Zero + DeepSeek-671B 方案 |
| `en/` | 英文文档目录 |
| `en/TODO` | 英文文档待办 |

**解读**：

- **四大文档子目录**：`algorithms/`（4 篇）、`features/`（30 项特性 + 1 篇 README）、`solutions/`（3 篇端到端方案）、`install_guide.md`（安装）。
- **features 主题聚类**：
  - *并行与拓扑*：`context_parallel`、`expert_parallel`、`EPLB`、`vpp`（虚拟流水线并行）、`resharding`；
  - *显存/换存*：`offload`、`recompute`、`norm_recompute`、`activation_function_recompute`、`swap_attention`、`swap_optimizer`、`reuse_fp32_param`；
  - *推理集成*：`integrated_worker`（训推共卡）、`chunked_prefill`、`acl_graph`、`vLLM_prefix_cache`、`partial_rollout`；
  - *训练机制*：`grpo_lora`、`multi_turn`、`data_module_design`、`task_queue`；
  - *可观测性/质量*：`log_metrics`、`logging_wandb_tensorboard`、`logging_swanlab`、`profiler`、`msprobe`、`deterministic_computation`；
  - *配置*：`grpo_yaml`、`ppo_yaml`、`runtime_env`。
- **solutions 矩阵**：3 篇 R1-Zero 方案，覆盖 Qwen2.5-7B、Qwen2.5-32B、DeepSeek-671B，与 configs 矩阵中的模型清单一致。
- **英文文档状态**：`en/TODO` 表明英文文档为待办，仅作占位。

---

### 表 6. `examples/` 目录

| 文件/目录 | 说明 |
| --------- | ---- |
| `grpo/` | GRPO 算法示例 |
| `grpo/grpo_trainer_qwen25_7b.sh` | GRPO + Qwen2.5-7B 训练脚本 |
| `grpo/grpo_trainer_qwen25_32b.sh` | GRPO + Qwen2.5-32B 训练脚本 |
| `grpo/grpo_trainer_qwen3_8b.sh` | GRPO + Qwen3-8B 训练脚本 |
| `grpo/grpo_trainer_qwen3_235b_a22b.sh` | GRPO + Qwen3-235B-A22B 训练脚本 |
| `grpo/grpo_trainer_deepseek_r1_671b.sh` | GRPO + DeepSeek-R1-671B 训练脚本 |
| `dapo/` | DAPO 算法示例 |
| `dapo/dapo_trainer_qwen25_32b.sh` | DAPO + Qwen2.5-32B 训练脚本 |
| `dapo/dapo_trainer_qwen25_32b_20k.sh` | DAPO + Qwen2.5-32B 20K 训练脚本 |
| `dapo/dapo_trainer_qwen25_32b_32k.sh` | DAPO + Qwen2.5-32B 32K 训练脚本 |
| `dapo/dapo_trainer_qwen3_30b_a3b.sh` | DAPO + Qwen3-30B-A3B 训练脚本 |
| `dapo/dapo_trainer_qwen3_32b.sh` | DAPO + Qwen3-32B 训练脚本 |
| `ppo/` | PPO 算法示例 |
| `ppo/ppo_trainer_qwen25_32b.sh` | PPO + Qwen2.5-32B 训练脚本 |
| `dpo/` | DPO 算法示例 |
| `dpo/dpo_trainer_qwen3_30b_a3b.sh` | DPO + Qwen3-30B-A3B 训练脚本 |
| `eplb/` | EPLB 示例 |
| `eplb/eplb.sh` | EPLB 启动脚本 |
| `eplb/grpo_trainer_deepseek_r1_671b_eplb.sh` | GRPO + DeepSeek-R1-671B EPLB 训练脚本 |
| `eplb/collect_json_file.sh` | JSON 文件收集脚本 |
| `multi_turn/` | 多轮训练示例 |
| `multi_turn/dapo_trainer_qwen25_7b_multi_turn.sh` | DAPO + Qwen2.5-7B 多轮训练脚本 |
| `data/` | 数据预处理示例 |
| `data/preprocess_data.sh` | 数据预处理脚本 |

**解读**：

- **算法 × 模型矩阵**：examples 层与 configs 层严格一一对应。例如 `examples/grpo/grpo_trainer_qwen25_7b.sh` 对应 `configs/grpo_qwen25_7b_A3.yaml`；`examples/eplb/grpo_trainer_deepseek_r1_671b_eplb.sh` 对应 `configs/grpo_deepseek_r1_671b_A3_eplb.yaml`。
- **变体脚本**：`dapo_trainer_qwen25_32b_20k.sh` / `_32k.sh` 对应 `_A2_20k.yaml` / `_A3_32k.yaml`；`dapo_trainer_qwen25_7b_multi_turn.sh` 对应 `_A2_multi_turn.yaml`。
- **EPLB 子目录** 额外提供 `eplb.sh`（通用启动）和 `collect_json_file.sh`（收集 JSON），与 `cli/eplb_generate_map_ds.py` 配合形成「生成映射 → 收集 → 训练」的 EPLB 数据流。
- **多轮训练**单独成目录 `multi_turn/`，印证 `docs/zh/features/multi_turn.md` 与 `configs/dapo_qwen25_7b_A2_multi_turn.yaml` 是一条独立特性线。
- **PPO/DPO 的脚本稀疏（各 1 个）**，再次印证这两个算法在仓库内的覆盖深度低于 GRPO/DAPO。

---

### 表 7. `mindspeed_rl/` 核心框架（顶层）

| 文件/目录 | 说明 |
| --------- | ---- |
| `__init__.py` | 包初始化文件 |
| `config_cls/` | 配置类定义与校验 |
| `config_cls/base_config.py` | 基础配置类 |
| `config_cls/rl_config.py` | RL 训练配置类 |
| `config_cls/megatron_config.py` | Megatron 配置类 |
| `config_cls/generate_config.py` | 生成配置类 |
| `config_cls/data_handler_config.py` | 数据处理配置类 |
| `config_cls/mindstudio_config.py` | MindStudio 配置类 |
| `config_cls/validate_config.py` | 配置校验 |
| `datasets/` | 数据集加载与预处理模块 |
| `datasets/base_dataset.py` | 基础数据集类 |
| `datasets/build_dataset.py` | 数据集构建 |
| `datasets/data_handler.py` | 数据处理器 |
| `datasets/dataloader.py` | 数据加载器 |
| `datasets/data_samplers.py` | 数据采样器 |
| `datasets/formatter.py` | 数据格式化 |
| `datasets/handler_utils.py` | 数据处理工具函数 |
| `datasets/datasets/indexed_dataset.py`（注：原文中目录拼写为 `indexed_dataset.py`） | 索引数据集 |
| `datasets/prompt_dataset.py` | 提示数据集 |
| `datasets/multimodal_dataset.py` | 多模态数据集 |
| `datasets/mm_utils.py` | 多模态工具函数 |
| `datasets/preprocess_data.py` | 数据预处理 |
| `datasets/templates.py` | 数据模板 |
| `datasets/utils.py` | 数据集工具函数 |

**解读**：核心包第一层有 3 个子模块。

- **`config_cls/`（7 个类）**：分层清晰——`base_config` 是父类，`rl_config` 是 RL 总配置，`megatron_config` 是底层训练引擎配置（呼应「训推共卡」+ Megatron 集成），`generate_config` 是 rollout/生成侧配置，`data_handler_config` 对应 `data_handler.py`，`mindstudio_config` 对应 MindStudio 精度分析（与 `features/msprobe.md` 呼应），`validate_config` 负责统一校验。
- **`datasets/`（13 个文件）**：从「构建（`build_dataset`、`base_dataset`）→ 加载（`dataloader`、`data_samplers`）→ 处理（`data_handler`、`handler_utils`、`preprocess_data`）→ 格式化（`formatter`、`templates`）→ 特殊形态（`prompt_dataset`、`indexed_dataset`、`multimodal_dataset`+`mm_utils`）」形成完整数据流。`prompt_dataset` 是 RL 训练的标准入口形态（仅 prompt，由 rollout 生成），与 `actor_rollout_hybrid.py` 配合。

---

### 表 8. `mindspeed_rl/models/` 模型定义

| 文件/目录 | 说明 |
| --------- | ---- |
| `models/actor.py` | Actor 模型 |
| `models/actor_rollout_hybrid.py` | Actor-Rollout 混合模型 |
| `models/critic.py` | Critic 模型 |
| `models/reference.py` | Reference 模型 |
| `models/reward.py` | Reward 模型 |
| `models/math_dapo.py` | DAPO 数学验证模型 |
| `models/math_verify.py` | 数学验证模型 |
| `models/rule_verifier.py` | 规则验证器 |
| `models/base/` | 模型基类 |
| `models/base/base_inference_engine.py` | 推理引擎基类 |
| `models/base/base_training_engine.py` | 训练引擎基类 |
| `models/loss/` | 损失函数模块 |
| `models/loss/base_loss_func.py` | 损失函数基类 |
| `models/loss/critic_loss_func.py` | Critic 损失函数 |
| `models/loss/ppo_actor_loss_func.py` | PPO Actor 损失函数 |
| `models/loss/grpo_actor_loss_func.py` | GRPO Actor 损失函数 |
| `models/loss/dapo_actor_loss_func.py` | DAPO Actor 损失函数 |
| `models/loss/reference_loss_func.py` | Reference 损失函数 |
| `models/loss/reward_loss_func.py` | Reward 损失函数 |
| `models/loss/logprob_computer.py` | 对数概率计算器 |
| `models/loss/loss_func_factory.py` | 损失函数工厂 |
| `models/loss/loss_register.py` | 损失函数注册 |
| `models/orm/` | ORM 模型模块 |
| `models/orm/orm_model.py` | ORM 模型 |
| `models/rollout/` | Rollout 模块 |
| `models/rollout/vllm_engine.py` | vLLM 推理引擎 |
| `models/rollout/vllm_adapter/` | vLLM 适配器 |
| `models/rollout/vllm_adapter/engine_core.py` | vLLM 引擎核心适配 |
| `models/rollout/vllm_adapter/fused_moe.py` | MoE 融合适配 |
| `models/rollout/vllm_adapter/megatron_weight_loaders.py` | Megatron 权重加载适配 |
| `models/rollout/vllm_adapter/vllm_parallel_state.py` | vLLM 并行状态适配 |
| `models/rollout/vllm_adapter/patch/` | vLLM 补丁 |
| `models/rollout/vllm_adapter/patch/qwen2_5_vl_reuse_vi...`（原文截断） | Qwen2.5-VL 多模态复用相关 patch（名称被截断） |

**解读**：这是 RL 框架最核心的「角色 × 损失 × 推理适配」三轴。

- **角色轴（5 个顶级角色）**：actor、critic、reference、reward 加上 **actor_rollout_hybrid**（训推共卡的实现，呼应 `features/integrated_worker.md`）；外加 **3 个验证器**（`math_dapo`、`math_verify`、`rule_verifier`），对应 DAPO/数学题场景下的规则化奖励。
- **基类层**：`base/base_inference_engine.py` + `base/base_training_engine.py` 提供「训练引擎」与「推理引擎」两个抽象，rollout/vllm_engine.py 与 actor.py 等具体类基于此实现，体现「训推同构」的设计意图。
- **损失函数（10 个）**：每个 RL 角色都有专用 loss_func（`critic_loss_func`、`reference_loss_func`、`reward_loss_func`）+ 三种 actor loss（PPO/GRPO/DAPO）+ `logprob_computer`（旧策略/参考策略的对数概率计算，是 PPO/GRPO 的核心）+ `loss_func_factory` + `loss_register`（工厂 + 注册器的标准可扩展模式）。
- **ORM（Outcome Reward Model）**：单独成目录，与 `reward.py` 并列。`reward` 通常是基于规则/小模型的瞬时奖励，ORM 是结果级奖励模型（如 DeepSeek-R1 时代的偏好打分），二者并存说明该项目支持 **规则奖励 + ORM 奖励** 的复合打分。
- **Rollout 与 vLLM 适配层**：
  - `vllm_engine.py` 是高层入口；
  - `vllm_adapter/` 下有 4 个具体适配：`engine_core`、`fused_moe`、`megatron_weight_loaders`、`vllm_parallel_state`，分别对应**引擎核心、MoE 融合、Megatron↔vLLM 权重互通、并行状态同步**——这是「Megatron 训练 + vLLM 推理」双栈的标准四件套；
  - `patch/qwen2_5_vl_reuse_vi...`（截断）说明 vLLM 在 Qwen2.5-VL 多模态模型上有专门的 patch，体现多模态推理的端到端支持。

> ⚠ 原文在 `qwen2_5_vl_reuse_vi...` 处截断，**未列出的后续目录**（如 `mindspeed_rl/trainer/`、`mindspeed_rl/workers/`、`mindspeed_rl/utils/`、`tests/`、`verl_npu/` 内部等）均**无法基于原文核实**，故本节不再臆测。

---

## 【公式解读】

**原文无公式。** 全文为目录结构与文字说明，未出现任何 LaTeX、伪代码、参数表达式或性能关系式。

---

## 【关联】

由于本任务给出的**内部链接信息为「(无)」**，以下仅基于文档自身出现的文件名/路径名交叉引用关系做模块关联梳理，不臆造未在原文出现的链接。

1. **算法 ↔ 配置 ↔ 示例三件套**：
   - 算法入口 `cli/train_*.py`（dapo/dpo/grpo/ppo）↔ 配置 `configs/*_qwen*_*.yaml` ↔ 示例 `examples/{dapo,dpo,grpo,ppo}/trainer_*.sh` 形成一一对应关系；示例脚本名内嵌的「算法_模型[_变体]」与 YAML 配置的命名规则一致。
2. **DAPO ↔ 数学验证**：`configs/dapo_*.yaml` + `cli/train_dapo.py` + `examples/dapo/*` + `mindspeed_rl/models/math_dapo.py` / `math_verify.py` / `rule_verifier.py` 形成「DAPO 训练 + 数学规则验证奖励」链路。
3. **EPLB ↔ MoE ↔ DeepSeek-R1-671B**：`features/EPLB.md` ↔ `cli/eplb_generate_map_ds.py` ↔ `examples/eplb/{eplb.sh, grpo_trainer_deepseek_r1_671b_eplb.sh, collect_json_file.sh}` ↔ `configs/grpo_deepseek_r1_671b_A3_eplb.yaml` ↔ `mindspeed_rl/models/rollout/vllm_adapter/fused_moe.py`，构成「MoE 模型专家并行负载均衡」端到端特性链。
4. **训推共卡 ↔ 引擎抽象**：`features/integrated_worker.md` ↔ `mindspeed_rl/models/actor_rollout_hybrid.py` ↔ `models/base/base_inference_engine.py` + `base_training_engine.py`。
5. **长序列 ↔ Partial Rollout**：`features/context_parallel.md`（长序列并行）↔ `features/partial_rollout.md`（部分 rollout）↔ `examples/multi_turn/` + `configs/dapo_*_multi_turn.yaml` + `cli/preprocess_data.py` 与 `examples/data/preprocess_data.sh`。
6. **多模态**：`configs/model/templates.json` + `mindspeed_rl/datasets/multimodal_dataset.py` + `mm_utils.py` + `models/rollout/vllm_adapter/patch/qwen2_5_vl_*`（截断）形成多模态数据→多模态 rollout patch 链路。
7. **精度/可观测性**：`features/msprobe.md` ↔ `config_cls/mindstudio_config.py`；`features/logging_{wandb_tensorboard,swanlab}.md` ↔ `features/log_metrics.md`。
8. **verl 适配层**：`verl_npu/` 与 `mindspeed_rl/` 并列，表明项目既自研核心，又提供对 verl 框架的 NPU 适配入口——这是仓库设计的「双框架」姿态，但原文未给出 `verl_npu/` 内部细节。
9. **文档语言分支**：`docs/zh/` 完整、`docs/en/TODO` 待办，说明英文文档尚未跟进。

---

## 【使用方法】

本文档为目录结构总览，**未给出任何「启用方式 / 配置项 / 命令」的运行指导**（即无 `python xxx.py --flag value` 类的可执行命令、无 yaml 字段说明、无 shell 启动指令）。所有训练命令均在 `examples/*/*.sh` 中，启动
