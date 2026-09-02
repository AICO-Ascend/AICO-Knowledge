# Release Notes

> 仓 `mindspeed-llm` · 路径 `docs/en/release_notes_llm.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-llm/docs/en/release_notes_llm.md

# MindSpeed LLM 26.0.0 Release Notes 深度解读

## 【定位】

本文档是昇腾LLM分布式训练框架 **MindSpeed LLM v26.0.0** 的官方发布说明（changelog），系统性披露该商业版本的**产品元信息、上下游软件兼容性矩阵、新增/废弃特性、升级影响及安全扫描结果**，用于指导用户进行版本选型、升级评估与风险管控。

---

## 【技术要点】

1. **FSDP2 训练支持（新增）**：在原有训练范式之外新增 **Megatron FSDP2** 路径，支持 Qwen3-30B / Qwen3-32B / Qwen3-235B / Qwen3-Next 系列模型训练。
2. **128K 超长序列训练（新增）**：面向 gpt-oss 与 DeepSeekV3.2 模型开放 128K 上下文长度的训练能力。
3. **工具链效率优化（新增）**：支持"权重转换 + 训练"以及"数据预处理 + 训练"的**合并执行**模式，减少中间落盘与启动开销。
4. **安全加固（新增）**：为 LLM 微调流程引入 **PMCC（Privilege Management and Cybersecurity Compliance）保护**。
5. **商业版软件栈固定**：26.0.0 锁定 Megatron `core_v0.12.1`、PyTorch `2.7.1`、TorchNPU `26.0.0`、CANN `9.0.0`、Python `3.10`。
6. **大模型退役（Dense & MoE）**：批量下架 Llama-2/3 系列、ChatGLM3、GLM4、Baichuan2、InternLM2.5、Qwen2.5/3 系列、Dense Qwen3-8B、Qwen3-30B、GPT4-MoE-175B、Hunyuan-389B 等模型。

---

## 【关键机制与数据】

- **原文：** 本次为正式商业发布（Official release），发布日期 **2026 年 4 月**，维护周期 **6 个月**。
- **原文：** MindSpeed LLM 与底层加速库的版本耦合关系——`26.0.0 ↔ core_v0.12.1 ↔ TorchNPU 26.0.0 ↔ CANN 9.0.0`；上一商业版 `2.3.0` 对应 `TorchNPU 7.3.0 / CANN 8.5.0`。
- **原文：** 26.0.0 在 CANN 维度具备**向下多版本兼容**能力，可同时运行在 `CANN 9.0.0 / 8.5.0 / 8.3.RC1 / 8.2.RC1 / 8.1.RC1` 五套 CANN 之上，对应 TorchNPU 仍为 `26.0.0`。
- **原文：** 升级会造成**业务中断**（service interruption），但**不影响网络通信**。
- **原文：** 三款杀毒引擎（奇安信、Kaspersky、Bitdefender）于 **2026-04-02** 扫描，均报告 "No viruses, no malware"。
- 原文未提供训练吞吐、显存占用、收敛曲线等性能数据。

---

## 【表格解读】

### 表 A · 产品版本元信息（Product Version Information）

| Product | Product Version | Version Type | Component Name | Release Date | Maintenance |
|---|---|---|---|---|---|
| MindSpeed | 26.0.0 | Official release | MindSpeed LLM | April 2026 | 6 months |

**逐行解读**：单一产品线 MindSpeed 下唯一组件 MindSpeed LLM 升至 26.0.0，性质为正式商业版（非 RC/beta），与版本表 B 中标注 `(commercial)` 一致；6 个月维护窗口提示用户需在此期间完成后续小版本升级规划。

---

### 表 B · MindSpeed LLM 软件版本兼容矩阵（**Table 1** Related Product Version Mapping）

| MindSpeed LLM version | MindSpeed Core code branch name | Megatron version | PyTorch version | TorchNPU version | CANN version | Python version |
|---|---|---|---|---|---|---|
| master (under development) | master (under development) | core_v0.12.1 | 2.7.1 | In development | In development | Python 3.10 |
| 26.0.0 (commercial) | 26.0.0_core_r0.12.1 | core_v0.12.1 | 2.7.1 | 26.0.0 | 9.0.0 | Python 3.10 |
| 2.3.0 (commercial) | 2.3.0_core_r0.12.1 | core_v0.12.1 | 2.7.1 | 7.3.0 | 8.5.0 | Python 3.10 |
| 2.2.0 (commercial) | 2.2.0_core_r0.12.1 | core_v0.12.1 | 2.7.1 | 7.2.0 | 8.3.RC1 | Python 3.10 |

**逐行解读**：
- 三个商业版本均锁定 **Megatron core_v0.12.1 + PyTorch 2.7.1 + Python 3.10**，意味着上层训练脚本兼容性较好，主要差异集中在 **TorchNPU 与 CANN** 这两层昇腾原生栈。
- 26.0.0 相比 2.3.0，TorchNPU 由 `7.3.0 → 26.0.0`，CANN 由 `8.5.0 → 9.0.0`，对应 MindSpeed Core 分支从 `2.3.0_core_r0.12.1 → 26.0.0_core_r0.12.1`。
- master 行说明下一代的 TorchNPU / CANN 仍在开发中。

---

### 表 C · 版本兼容性信息（Version Compatibility Information）

| MindSpeed LLM version | CANN version | TorchNPU version |
|---|---|---|
| 26.0.0 | CANN 9.0.0 / 8.5.0 / 8.3.RC1 / 8.2.RC1 / 8.1.RC1 | 26.0.0 |
| 2.3.0 | CANN 8.5.0 / 8.3.RC1 / 8.2.RC1 / 8.1.RC1 / 8.0.0 | 7.3.0 |
| 2.2.0 | CANN 8.3.RC1 / 8.2.RC1 / 8.1.RC1 / 8.0.0 / 8.0.RC3 / 8.0.RC2 | 7.2.0 |

**逐行解读**：
- 同一 MindSpeed LLM 版本可承载**多个 CANN 版本**，但 **TorchNPU 严格一对一**——用户需按列右侧 TorchNPU 版本选择对应的驱动/CANN 组合。
- 26.0.0 向后兼容至 CANN 8.1.RC1，对老集群友好但**不再支持 CANN 8.0.x**；2.3.0 的 CANN 下限为 8.0.0。

---

### 表 D · 新增特性（New Features）

| Component | Description | Purpose |
|---|---|---|
| MindSpeed LLM | Added FSDP2 training support | Supports Qwen3-30B, Qwen3-32B, Qwen3-235B, and Qwen3-Next model training |
| MindSpeed LLM | Added 128K training support | Supports ultra-long sequence training for gpt-oss and DeepSeekV3.2 models |
| MindSpeed LLM | Improved tool efficiency | Supports combined weight conversion and training, and combined data preprocessing and training |
| MindSpeed LLM | Security hardening | Supports PMCC protection for LLM fine-tuning |

**逐行解读**：
- 第 1 行：FSDP2 是新增的**分布式策略路径**，目前仅覆盖 Qwen3 系列 MoE 与大尺寸 Dense。
- 第 2 行：128K 上下文是当前长文本训练的关键阈值，与 DeepSeekV3.2、gpt-oss 这类原生长上下文模型对齐。
- 第 3 行：将"权重转换"、"数据预处理"与"训练"合并为同一流水线，是**工具链层**的工程优化。
- 第 4 行：PMCC 是面向**微调场景**的安全护栏，与预训练解耦。

---

### 表 E · 移除特性（Removed Features）

| Component | Description | Purpose |
|---|---|---|
| MindSpeed LLM | Model retirement | Dense model retirement list:<br>Llama-2-34B<br>Llama-3-8B/70B<br>Llama-3.1-8B/50B/70B/200B<br>Llama-3.2-1B/3B<br>Llama-3.3-70B-Instruct<br>ChatGLM3-6B<br>GLM4-9B<br>Baichuan2-7B/13B<br>InternLM2.5-1.8B/7B/20B<br>Qwen2.5-0.5B/1.5B/3B/7B/14B/32B<br>Qwen3-8B (Megatron FSDP2)<br><br>MoE model retirement list:<br>Qwen3-30B (Megatron FSDP2)<br>GPT4-MoE-175B<br>Hunyuan-389B |

**逐行解读**：
- Dense 退役列表共 11 个模型族 / 24+ 个具体尺寸，覆盖 Llama 全系、ChatGLM3、GLM4、Baichuan2、InternLM2.5、Qwen2.5 全档位。
- **特殊点**：Qwen3-8B 仅在 **Megatron FSDP2 路径**被退役——意味着在其它训练后端（如 TP+PP）上仍可用；Qwen3-30B 同样仅在 FSDP2 路径退役。
- MoE 退役列表 3 个条目（Qwen3-30B、GPT4-MoE-175B、Hunyuan-389B），且 GPT4-MoE-175B 与 Hunyuan-389B 为**整模型退役**，无路径限定。

---

### 表 F · 相关文档（Related Documents）

| Document | Summary | Update Notes |
|---|---|---|
| [MindSpeed LLM Installation Guide](./pytorch/training/install_guide.md) | 本指南帮助用户在 NPU 上安装 MindSpeed LLM，覆盖硬件/操作系统兼容性、驱动固件与 CANN 基础软件安装，以及基于 PyTorch 框架的完整安装流程。 | - |
| [Quick Start: Qwen3-8B Model Pretraining and Fine-Tuning](./pytorch/training/quick_start.md) | 以 Qwen3-8B 为例，帮助 MindSpeed LLM 新手在 NPU 上完成预训练与微调任务。 | - |

**逐行解读**：两篇文档构成完整的"上手链路"——安装指南提供环境准备，Quick Start 提供 Qwen3-8B 端到端示例（恰好与本次 Qwen3-8B 在 FSDP2 路径下退役形成对照：Quick Start 中的 Qwen3-8B 应使用非 FSDP2 路径）。

---

### 表 G · 病毒扫描结果（Virus Scan Results）

| Antivirus Software Name | Antivirus Software Version | Virus Database Version | Scan Time | Scan Result |
|---|---|---|---|---|
| QiAnXin | 8.0.5.5260 | 2026-04-01 08:00:00.0 | 2026-04-02 | No viruses, no malware |
| Kaspersky | 12.0.0.6672 | 2026-04-02 10:05:00.0 | 2026-04-02 | No viruses, no malware |
| Bitdefender | 7.5.1.200224 | 7.100588 | 2026-04-02 | No viruses, no malware |

**逐行解读**：采用国内（奇安信）+ 国际（Kaspersky、Bitdefender）三引擎交叉验证；病毒库时间戳早于或等于扫描时间，逻辑合理；三方均报"无病毒、无恶意软件"。

---

## 【公式解读】

**原文无公式**。本文档作为 changelog，不包含任何 LaTeX 数学公式或伪代码形式的算法表达式。

---

## 【关联】

- **与 `./pytorch/training/install_guide.md` 的关系**：本次 26.0.0 发布需要匹配的 PyTorch 2.7.1、TorchNPU 26.0.0、CANN 9.0.0 等软件栈均通过该安装指南落地；Release Date（2026-04）与安装指南的版本对应是该文档的下游事实依据。
- **与 `./pytorch/training/quick_start.md` 的关系**：Quick Start 以 Qwen3-8B 为示例模型进行预训练与微调；而本 changelog 将 **Qwen3-8B 在 Megatron FSDP2 路径**列入了退役清单，提示用户使用 Quick Start 时需注意**不要走 FSDP2 路径**，或迁移至 Qwen3-30B/32B/235B/Next 等仍受 FSDP2 支持的模型。
- **与 MindSpeed Core / Megatron-LM 的关系**：本版本锁定 `MindSpeed Core 分支 26.0.0_core_r0.12.1` 与 `Megatron core_v0.12.1`，意味着上游变更需要 MindSpeed 仓库单独 cherry-pick，升级时三者必须同步。
- **与底层 CANN / TorchNPU 的关系**：表 C 表明 26.0.0 在 CANN 层向下兼容 5 个版本，但 TorchNPU 锁死 `26.0.0`，形成"N 选 1 的 CANN × 唯一 TorchNPU"组合约束。
- **与外部版本维护策略的关系**：原文中 NOTE 链接指向 GitCode 上的 *MindSpeed-LLM 版本维护策略*，是本 changelog 的元规则来源。

---

## 【使用方法】

**原文未涉及**具体的启用命令、配置开关或 CLI 参数。

文档中仅在 NOTE 区给出操作指引级别的一句话提示："You can choose the MindSpeed LLM code branch as needed to download the source code and install it."；具体的安装命令、模型启动脚本、FSDP2 启用开关、128K 序列长度配置、PMCC 启用方式等内容需查阅文末关联的 `install_guide.md` 与 `quick_start.md`。
