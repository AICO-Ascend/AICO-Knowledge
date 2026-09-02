# 项目目录结构总览

> 仓 `msmodelslim` · 路径 `docs/zh/contributing/development_guide/dir_structure.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msmodelslim/docs/zh/contributing/development_guide/dir_structure.md

# msModelSlim 项目目录结构总览 · 七节深度解读

---

## 【定位】

这篇文档系统描述了 msModelSlim 代码仓的**整体目录组织与分层架构**，核心解决"**V1 分层解耦量化框架、V0 框架、小模型压缩代码三套体系共存**时，开发者和使用者如何快速定位源码、文档、最佳实践与工具脚本"的问题，是进入代码仓的第一份地图类 overview 文档。

---

## 【技术要点】

1. **V1 框架定位为推荐使用的新一代框架**：文档明确"我们推荐您使用V1框架，并期待您参与V1框架的共建"，并指出 V1 框架"仍在成长过程中，未完全覆盖V0框架能力和小模型压缩功能"。
2. **支持三类主流大模型量化算法**：原文列出 "SmoothQuant、GPTQ、HQQ等大模型量化算法"。
3. **量化进入 4 比特及极低比特时代**：原文"量化位宽也进入到4比特甚至极低比特时代，单一算法已经无法同时同时满足性能和精度的双重需求，复合策略成为常态"。
4. **三套代码共存，采用目录隔离策略**：原文"目前三套代码共存于msModelSlim代码仓，尽量以目录隔离，后续将逐步整理归一"，涉及小模型、V0、V1 三套体系。
5. **V1 框架采用 6+1 分层架构**：`app/`（应用层）、`cli/`（接口层）、`core/`（领域层）、`infra/`（基础设施层）、`ir/`（领域层，量化模式）、`model/`（基础设施层，模型适配）、`utils/`（通用模块），加上 `processor/`（领域层，量化算法）共构成清晰的分层知识库。
6. **CLI 与 app 一一对应**：原文明确"`msmodelslim quant`"（一键量化）、"`msmodelslim tune`"（自动调优）、"`msmodelslim analyze`"（量化分析）三个子命令入口。

---

## 【关键机制与数据】

| 来源 | 原文要点 |
|---|---|
| 原文 | "早期支持了小模型剪枝、蒸馏、量化等压缩功能，当大模型初现时，逐步转向大模型量化功能" — 体现项目演进的两个阶段 |
| 原文 | "大模型数量也呈井喷之势，亟需提升工具易用性，提高量化调优效率，减少单个模型的量化耗时" — 这是 V1 框架自动调优能力的业务驱动 |
| 原文 | "msModelSlim总结发展出了分层解耦的大模型量化框架，称为V1框架，而将过去的大模型量化手段归为V0框架" — 给出 V0 / V1 框架的定义边界 |
| 原文 | "量化分析服务使用特定指标分析特定模型以辅助设计该模型的量化方案"（`core/analysis_service/` 注释）— 给出量化分析服务的职责 |
| 原文 | "量化服务将浮点模型转化为量化模型并生成量化权重"（`core/quant_service/` 注释）— 给出量化服务的职责 |
| 原文 | "调优策略根据精度反馈调整量化配置"（`core/tune_strategy/` 注释）— 给出调优策略的职责 |
| 原文 | "上下文统一管理和共享处理流程中的状态，用户可以将上下文当作无限容量的存储空间"（`core/context/` 注释）— 给出上下文组件的语义 |

> 注：原文未给出任何量化精度损失、推理加速比、显存节省等**性能数据**，亦未给出版本号、时间线等具体数字。

---

## 【表格解读】

原文无传统 markdown 表格，但包含大量**目录结构树**，以下用表格形式**逐字还原**最关键的三层目录（顶层 / `msmodelslim/` 一级 / `app/`），并逐行解读。

### 表 1 · 仓库顶层目录（V1 框架视角）

| 路径 | 原文标注 |
|---|---|
| `msmodelslim/config/` | 全局配置目录（V1框架） |
| `msmodelslim/docs/` | 项目文档，如安装指南、快速入门、算法说明、功能指南、案例集等 |
| `msmodelslim/example/` | 各模型的量化示例（主要为V0框架量化脚本，但V1量化过程FAQ在此统一管理） |
| `msmodelslim/lab_calib/` | 量化校准数据集示例，如json、jsonl、图片等（V1框架） |
| `msmodelslim/lab_practice/` | 各模型最佳实践量化配置（V1框架） |
| `msmodelslim/msmodelslim/` | 源代码 |
| `msmodelslim/test/` | 测试用例与测试脚本 |
| `msmodelslim/install.sh` | 安装脚本 |
| `msmodelslim/requirements.txt` | 第三方依赖列表 |
| `msmodelslim/pytest.ini` | 测试配置 |
| `msmodelslim/README.md` | 项目总览与使用说明 |
| `msmodelslim/LICENSE` | 开源许可证 |
| `msmodelslim/OWNERS` | 代码维护审批配置 |
| `msmodelslim/setup.py` | 打包与安装配置脚本 |

**解读**：V1 视角下，V0 / 小模型专用的 `ascend_utils/`、`modelslim/`（V0 别名）、`precision_tool/`、`security/` 不再出现，仅保留 V1 通用资产与源代码；其中 `lab_calib/` 与 `lab_practice/` 是 V1 特有的"校准数据 + 最佳实践"知识库对。

### 表 2 · `msmodelslim/` 源码一级目录（V1 框架视角）

| 路径 | 原文标注 |
|---|---|
| `msmodelslim/app/` | 应用层，对外提供"一键量化、自动调优、量化分析"等功能 |
| `msmodelslim/cli/` | 接口层，命令行接口及各功能子命令 |
| `msmodelslim/core/` | 领域层，各类量化业务知识库 |
| `msmodelslim/infra/` | 基础设施层，各类外部依赖适配知识库 |
| `msmodelslim/ir/` | 领域层，量化模式知识库，最基础的知识，描述何为量化，如W8A8量化等 |
| `msmodelslim/model/` | 基础设施层，模型适配知识库，如DeepSeek、Qwen等 |
| `msmodelslim/processor/` | 领域层，量化算法知识库，描述如何做量化，如GPTQ算法等 |
| `msmodelslim/utils/` | 通用模块，如日志、配置、校验、安全等 |

**解读**：这是 V1 框架的核心分层。"ir" 描述"何为量化"（静态/动态 W8A8 等），"processor" 描述"如何做量化"（GPTQ 等算法），"model" 描述"对谁做量化"（DeepSeek、Qwen 等模型适配），三者构成 V1 知识库的"对象—方法—目标"三元结构。

### 表 3 · `app/` 应用层三个子应用

| 子应用 | application.py 职责 | 关键 infra/interface 文件 |
|---|---|---|
| `analysis/` | 量化分析的业务流程 | `result_displayer_infra.py`（结果展示基础设施需求） |
| `auto_tuning/` | 自动调优的业务流程 | `evaluation_service_infra.py`、`plan_manager_infra.py`、`practice_accuracy_infra.py`、`practice_history_infra.py`、`practice_manager_infra.py`、`model_info_interface.py` |
| `naive_quantization/` | 一键量化的业务流程 | `model_info_interface.py`、`practice_manager_infra.py` |

**解读**：三个应用共享"application.py + 多个基础设施需求（*_infra.py / *_interface.py）"的同构模式，体现了 V1 框架"应用层只编排流程、所需能力通过接口向基础设施层声明"的设计思想。

### 表 4 · `cli/` 与 `app/` 的一一对应

| CLI 子命令 | 入口文件 | 对应 app |
|---|---|---|
| `msmodelslim` 总入口 | `cli/__main__.py` | — |
| `msmodelslim analyze` | `cli/analysis/__main__.py` | `app/analysis/` |
| `msmodelslim tune` | `cli/auto_tuning/__main__.py` | `app/auto_tuning/` |
| `msmodelslim quant` | `cli/naive_quantization/__main__.py` | `app/naive_quantization/` |

**解读**：CLI 层是 app 层的"壳"，每个子命令入口与 app 子应用一一对应，`cli/utils.py` 提供通用工具函数。

### 表 5 · `core/` 领域层子库（V1 业务知识库全集）

| 子目录 | 原文职责标注 |
|---|---|
| `core/analysis_service/` | 量化分析服务知识库，量化分析服务使用特定指标分析特定模型以辅助设计该模型的量化方案 |
| `core/base/` | 基础协议（待移除，现有实现需移入对应的知识库） |
| `core/const.py` | 常量（待移除，现有实现需移入对应的知识库） |
| `core/context/` | 上下文知识库，上下文统一管理和共享处理流程中的状态，用户可以将上下文当作无限容量的存储空间；含 `local_dict_context/` 与 `shared_dict_context/` 两种实现 |
| `core/graph/` | 子图模式知识库，量化算法均是基于特定模式的模型结构子图；含离群值抑制子图模式 `adapter_types.py` |
| `core/observer/` | 特征统计知识库；含 `histogram.py`、`minmax.py`、`recall_window.py` |
| `core/practice/` | 最佳实践知识库（待优化，目前仅支持一种最佳实践格式） |
| `core/quant_service/` | 量化服务知识库，量化服务将浮点模型转化为量化模型并生成量化权重；含 `modelslim_v0/`、`modelslim_v1/`、`multimodal_sd_v1/`、`multimodal_vlm_v1/`、`proxy/` |
| `core/quantizer/` | 权重量化和激活值量化知识库（待梳理） |
| `core/runner/` | 调度知识库（待梳理）；含 `dp_layer_wise_runner.py`、`generated_runner.py`、`layer_wise_runner.py`、`pipeline_parallel_runner.py` 等 |
| `core/tune_strategy/` | 调优策略知识库，调优策略根据精度反馈调整量化配置；含 `standing_high/`、`standing_high_with_experience/`、`binary_fallback/` |

**解读**：`core/` 是 V1 的"业务大脑"。其中 `quant_service/` 同时存在 `modelslim_v0/` 与 `modelslim_v1/` 两条实现线，证明 V1 框架在底层仍以"服务实现"形式向下兼容 V0；`context/`、`observer/`、`graph/` 三个子库则承担跨调度的"状态 / 特征 / 子图"基础能力。

### 表 6 · `infra/` 基础设施层（外部依赖适配清单）

| 文件 / 子目录 | 原文标注 |
|---|---|
| `infra/dataset_loader/` | 数据集加载类基础设施 |
| `infra/evaluation/` | 测评工具类基础设施 |
| `infra/analysis_pipeline_loader.py` | 基于YAML的流水线模板加载基础设施 |
| `infra/debug_info_persistence.py` | 基于JSON和Safetensors的调试信息持久化基础设施 |
| `infra/file_dataset_loader.py` | 基于文件的LLM数据集加载基础设施 |
| `infra/logging_analysis_result_displayer.py` | 基于日志的分析结果展示基础设施 |
| `infra/plugin_practice_dirs.py` | （原文无附加说明） |
| `infra/service_oriented_evaluate_service.py` | 基于服务的模型测评服务基础设施 |
| `infra/vllm_ascend_server.py` | 基于vLLM-Ascend的服务化基础设施 |
| `infra/yaml_plan_manager.py` | 基于YAML的调优计划管理基础设施 |
| `infra/yaml_practice_accuracy_manager.py` | 基于YAML的调优精度缓存管理基础设施 |
| `infra/yaml_practice_history_manager.py` | 基于YAML的调优历史管理基础设施 |
| `infra/yaml_practice_manager.py` | 基于YAML的最佳实践管理基础设施 |
| `infra/yaml_quant_config_exporter.py` | 基于YAML的量化配置导出基础设施 |

**解读**：infra 层大量以"YAML + 服务化"为基调，承接 `app/` 中各应用声明的 `*_infra.py` 需求。`vllm_ascend_server.py` 表明 V1 框架与 vLLM-Ascend 推理栈有明确对接，用于服务化测评。

### 表 7 · `ir/` 量化模式知识库

| 文件 / 子目录 | 原文标注 |
|---|---|
| `ir/qal/` | 数据类型定义 |
| `ir/api/` | 汇总各数据类型的量化、反量化算法 |
| `ir/const.py` | 常见量化组合 |
| `ir/w8a8_static.py` | W8A8静态量化模式 |
| `ir/w8a8_dynamic.py` | W8A8动态量化模式 |
| `ir/...` | 其它量化模式 |

**解读**：`ir/` 是 V1 框架最底层的"量化模式语义层"，`w8a8_static.py` / `w8a8_dynamic.py` 是已列出的具体模式样例，`...` 表示还有其它位宽/动态性组合的同级文件。

---

## 【公式解读】

**原文无公式**（无 LaTeX、无伪代码表达式、无数学推导）。

---

## 【关联】

虽然文档本身标注"内部链接: (无)"，但从目录命名与注释可推断出以下**模块间耦合关系**：

1. **CLI ↔ app 一一映射**（已在表 4 中体现）：`cli/analysis` → `app/analysis`、`cli/auto_tuning` → `app/auto_tuning`、`cli/naive_quantization` → `app/naive_quantization`，CLI 是 app 的命令行封装层。
2. **app → infra（需求声明 → 基础设施提供）**：`app/auto_tuning/` 中 5 个 `*_infra.py` 文件与 `infra/` 下 `yaml_plan_manager.py`、`yaml_practice_accuracy_manager.py`、`yaml_practice_history_manager.py`、`yaml_practice_manager.py`、`service_oriented_evaluate_service.py` 一一对应（如 `practice_manager_infra.py`  `yaml_practice_manager.py`）。
3. **app → model（模型适配需求声明）**：`app/auto_tuning/model_info_interface.py` 与 `app/naive_quantization/model_info_interface.py` 共同依赖 `model/` 中的具体模型适配知识库（如 DeepSeek、Qwen）。
4. **core ↔ ir ↔ processor 三元组**：`ir/` 定义"何为量化"（W8A8 等模式）→ `processor/` 实现"如何做量化"（GPTQ 等算法）→ `core/quant_service/` 把"对谁做量化"（具体模型）和"如何做"组合起来，形成完整量化服务。
5. **core/quant_service 的 V0/V1 兼容桥**：`core/quant_service/modelslim_v0/` 与 `core/quant_service/modelslim_v1/` 共存，说明 V1 框架在服务层向下兼容 V0 实现；`core/quant_service/multimodal_sd_v1/` 与 `multimodal_vlm_v1/` 则将 V1 能力扩展到多模态生成与理解模型。
6. **顶层 lab_practice ↔ core/practice ↔ infra/yaml_practice_manager**：文档/数据/业务/基础设施四层贯穿"最佳实践"主题，从仓库根目录的 `lab_practice/`（已验证配置）到 `core/practice/`（业务定义）再到 `infra/yaml_practice_manager.py`（YAML 持久化）。
7. **coexist 关系（V1 / V0 / 小模型）**：仓库顶层目录中 `modelslim/`（V0 别名）、`precision_tool/`（V0）、`security/`（V0）、`mindspore/`、`onnx/`、`pytorch/`（V0+小模型）、`quant/`（V0 多模态）、`ascend_utils/`（小模型）与 V1 的 `app/cli/core/infra/ir/model/processor/utils` 目录隔离共存。
8. **context 跨进程能力**：`core/context/local_dict_context/` 与 `core/context/shared_dict_context/` 表明 V1 框架对单进程与多进程场景均有适配，影响 `core/runner/pipeline_parallel_runner.py` 等调度实现。

---

## 【使用方法】

原文未涉及具体命令调用、配置项或 API 启用方式，仅在仓库顶层目录中给出**安装与运行入口**：

| 方式 | 原文标注 | 用途 |
|---|---|---|
| `msmodelslim/install.sh` | 安装脚本 | 一键安装 |
| `msmodelslim/setup.py` | 打包与安装配置脚本 | 打包与安装 |
| `msmodelslim/requirements.txt` | 第三方依赖列表 | 依赖声明 |
| `msmodelslim/pytest.ini` | 测试配置 | 测试运行配置 |
| `python -m msmodelslim`（推断自 `msmodelslim/cli/__main__.py` 注释"msmodelslim命令总入口"） | CLI 总入口 | 启用命令行工具 |
| `msmodelslim quant` / `msmodelslim tune` / `msmodelslim analyze` | CLI 子命令（原文分别为 `msmodelslim quant命令入口`、`msmodelslim tune命令入口`、`msmodelslim analyze命令入口`） | 分别启用"一键量化、自动调优、量化分析" |

> 注：具体的配置项（如 YAML 模板路径、调优策略选择、最佳实践目录指向等）在本文档中**未涉及**，需结合 `infra/` 下各 YAML 管理模块（如 `yaml_practice_manager.py`、`yaml_plan_manager.py`）的源码或其它专项文档进一步查阅。原文的 `model/` 目录结构在所提供片段中也被截断（仅显示至 `model/ # 基础设施层，模型适配知识库，满足其 ---`），属于原文未完整给出的部分。
