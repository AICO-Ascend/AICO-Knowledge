# 项目目录

> 仓 `mindspeed-mm` · 路径 `docs/zh/dir_structure.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-mm/docs/zh/dir_structure.md

# mindspeed-mm 项目目录文档深度解读

---

## 【定位】

**一句话定位**：本文档系统地列出 `mindspeed-mm` 项目的全量目录层级结构，帮助开发者快速建立对"多模态训练-推理-评估"全链路代码组织的整体认知，明确各子模块（权重转换、核心代码、训练/推理入口、示例、文档、测试、第三方适配）在仓库中的归属与定位。

---

## 【技术要点】

按功能维度归纳的核心机制要点（关键术语保留原文表述）：

1. **三条入口主链路**：仓库根目录并列了**训练**（`pretrain_omni.py` / `pretrain_sora.py` / `pretrain_vlm.py` / `pretrain_transformers.py`）、**推理**（`inference_sora.py` / `inference_vlm.py`）、**评估**（`evaluate_gen.py` / `evaluate_vlm.py`）三类 Python 入口脚本，分别对应**全模态训练、SORA 类生成模型训练/推理、VLM 类理解模型训练/推理、Transformers 类模型训练、生成/理解模型的离线评估**。

2. **核心代码 `mindspeed_mm/` 采用 9 段式架构**：`configs`（配置读取与处理）、`data`（数据处理）、`models`（模型结构）、`optimizer`（优化器）、`patchs`（patch 目录）、`tasks`（sft/infer/rl 等任务 pipeline）、`tools`（性能/内存分析工具）、`utils`（工具函数）、`training.py`（训练统一入口），覆盖**配置 → 数据 → 模型 → 优化 → 任务**完整链路。

3. **权重转换分"在线/离线"两层**：`bridge/` 提供 **mbridge 在线权重转换**；`checkpoint/` 提供**离线权重转换工具**，并按**模型族细分为 `common`（通用方法）、`sora_model`（多模态生成类）、`vlm_model`（多模态理解类）**。

4. **示例代码按"模型族 + 适配框架"二维组织**：`examples/` 顶层按模型名组织 `<model_name>/` 子目录（包含启动脚本 `xxx.sh`、配置文件 `xxx.json/yaml`、说明文档 `README.md`），并通过 `diffsynth/`、`diffusers/`、`rl/` 子目录分别承载 **DiffSynth 相关模型、Diffusers 相关模型、多模态强化学习模型**的支持代码。

5. **RL 框架通过 `verl_plugin/` 适配**：含 `verl_npu/`（verl 适配代码）、`README.md`（verl 适配说明）、`setup.py`（verl 环境安装），表明项目在昇腾 NPU 上对 verl 强化学习框架做了适配层封装。

6. **测试与文档双轨**：`tests/` 分为 `st/`（系统测试）与 `ut/`（单元测试）；`docs/` 分 `en/` 与 `zh/`，中文目录下进一步划 `features/`（特性说明文档）与 `pytorch/`（pytorch 后端迁移文档）。`scripts/install.sh` 为 **pytorch 环境配置脚本**。

---

## 【关键机制与数据】

原文未给出任何性能数据、训练参数、显存占用、吞吐数字、模型规模或工作流时序图。

- **原文**：仅以一段 `bash` 代码块列出**目录树文本**，并在树形注释中给出每个目录/文件的**一句话功能说明**（例如 `# mbridge在线权重转换`、`# sft/infer/rl等不同任务的pipeline代码`、`# 训练统一入口`）。除目录路径与这些短注释外，**不包含任何量化指标、运行机制图、数据流描述**。

- 因此本节其余部分无法基于原文展开，**严格遵循"原文未涉及即不臆造"原则**。

---

## 【表格解读】

**原文无表格**。原文中唯一的结构化呈现是一段 ASCII 目录树（位于 ` ```bash ``` 代码块内），其本身是层级清单而非参数表或对比表，故不构成"表格"。按照要求，此处明文标注无表格。

---

## 【公式解读】

**原文无公式**。原文既无 LaTeX 数学式，也无伪代码式公式片段，整篇均为目录注释文字。

---

## 【关联】

虽然原文未提供内部超链接（题头已注明"内部链接: (无)"），但从目录树的**模块邻接与命名蕴含**可梳理出项目内部的功能依赖与上下游关系：

1. **训练入口 → 核心代码层**
   `pretrain_omni.py` / `pretrain_sora.py` / `pretrain_vlm.py` / `pretrain_transformers.py` 四份训练入口脚本位于仓库根目录，应作为 `mindspeed_mm/training.py`（训练统一入口）的**外层调用方**；后者再调用 `mindspeed_mm/tasks/` 下 sft/infer/rl 等 pipeline，pipeline 进一步调用 `models/`、`data/`、`optimizer/`、`configs/`、`utils/`。

2. **推理与评估入口 ↔ 任务 pipeline**
   `inference_sora.py`、`inference_vlm.py` 与 `evaluate_gen.py`、`evaluate_vlm.py` 入口脚本服务于 `tasks/` 下的 infer / eval pipeline，与训练入口共同挂载到统一的 `training.py` 调度枢纽上。

3. **权重转换 ↔ 训练/推理**
   `bridge/`（在线权重转换）与 `checkpoint/{common, sora_model, vlm_model}`（离线权重转换，分别为生成/理解两类模型）提供**跨框架（HuggingFace / Megatron 等）与本仓模型实现之间的权重桥接**，是训练前与训练后与 `models/`、`tasks/` 衔接的横切关注点。

4. **示例 ↔ 模型族**
   `examples/diffsynth/` 与 `examples/diffusers/` 子目录承担**对 DiffSynth / Diffusers 生态模型的接入**，可视为 `models/` 与 `tasks/` 之外的**第三方生态适配面**；`examples/rl/` 指向**多模态强化学习**示例。

5. **`verl_plugin/` ↔ RL pipeline**
   `verl_plugin/`（含 `verl_npu/verl_npu 适配代码`、`setup.py` 安装脚本）作为**对 verl 强化学习框架的昇腾 NPU 适配层**，与 `examples/rl/` 的多模态 RL 支持、`tasks/` 中 rl pipeline 三者构成"框架适配 + 示例 + 任务 pipeline"的 RL 三件套。

6. **文档 ↔ 代码**
   `docs/zh/features/`（特性说明文档）与 `docs/zh/pytorch/`（pytorch 后端迁移文档）配合 `mindspeed_mm/patchs/`（patch 目录），共同支撑**新增特性与 PyTorch 后端迁移**的可解释性；`UserGuide/` 作为面向用户的另一文档入口与 `README.md` 形成冗余互补。

7. **工程基础设施**
   `ci/`（持续集成）、`tests/st/` + `tests/ut/`（系统/单元测试）、`scripts/install.sh`（pytorch 环境配置）、`pyproject.toml`（项目配置与构建文件）构成**CI → 测试 → 环境 → 构建**的工程化闭环。

---

## 【使用方法】

**原文未涉及**具体的启用方式、配置项细节或命令行调用写法。

可从原文直接抽取到的、与"使用"相关的最简信息仅有：

- **环境准备**：仓库提供 `scripts/install.sh`（原文注释为 `# pytorch环境配置脚本`），但原文未给出该脚本的内容、参数或执行步骤。
- **训练启动**：可通过根目录的 `pretrain_omni.py` / `pretrain_sora.py` / `pretrain_vlm.py` / `pretrain_transformers.py` 作为训练入口（原文仅以文件名形式提及，未列出 CLI 参数）。
- **推理与评估启动**：可通过 `inference_sora.py` / `inference_vlm.py` 启动推理，`evaluate_gen.py` / `evaluate_vlm.py` 启动评估（原文同样仅以文件名形式提及，无参数说明）。
- **verl 适配安装**：可通过 `verl_plugin/setup.py` 安装 verl 适配环境（原文仅以文件名形式提及）。

> 任何具体的启动命令、配置项默认值、超参数表、显存/卡数/序列长度等运行参数，原文均未给出，故严格不臆造。
