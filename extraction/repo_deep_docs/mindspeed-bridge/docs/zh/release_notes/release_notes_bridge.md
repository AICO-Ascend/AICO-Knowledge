# 版本说明

> 仓 `mindspeed-bridge` · 路径 `docs/zh/release_notes/release_notes_bridge.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-bridge/docs/zh/release_notes/release_notes_bridge.md

# MindSpeed Bridge v0.3.1 Release Notes 深度解读

---

## 【定位】

本文档为 MindSpeed Bridge v0.3.1 正式版本的版本说明（changelog），系统性描述了该版本的产品配套信息、组件依赖关系、运行兼容性矩阵、新增/删除特性、已解决问题以及升级影响与配套文档入口，为用户提供版本选型、升级决策与运维依据。

---

## 【技术要点】

1. **版本基线**：产品名 MindSpeed，组件名 MindSpeed Bridge，正式版本 v0.3.1，发布时间 **2026年7月**，维护周期 **6 个月**。
2. **核心依赖升级（master 在研版本）**：Megatron-Bridge 升至 **v0.5.0**，Megatron-LM 升至 **core_v0.18.0**，MindSpeed Core 升至 **core_r0.18.0**。
3. **架构替换**：v0.3.1 → master 路径中，以 **MegatronAdaptor + TransformerEngineNPU** 替换 MindSpeed；引入 **Git Submodule** 统一管理三方依赖；统一特性生命周期。
4. **运行环境基线（v0.3.1）**：Python **3.12**、PyTorch **2.9.0**、TorchNPU **26.1.0**、torchvision **0.24.0**、CANN **9.1.0**、Triton-Ascend **3.2.2**。
5. **新增模型与脚本**：Kimi-K3 多模态模型训练与适配、Qwen3.5-VL-397B-A17B SFT 脚本、GLM5.2 32k TND 高性能 POC 脚本。
6. **训练效率提升**：Qwen3.5-VL 支持 **pack（序列打包）+ CP（上下文并行）**、**MoE permute 融合**、GLM5/GLM5.2 支持 **融合算子 + packed TND 训练**、新增 **预加载 VLM 数据集 shuffle 控制**。

---

## 【关键机制与数据】

- **向下兼容机制（原文）**：「高版本 MindSpeed Bridge 兼容低版本运行环境，因此 master 可与较低版本的 TorchNPU/PyTorch/CANN 配套。」
- **Triton-Ascend ↔ CANN 强绑定（原文）**：「Triton-Ascend 版本与 CANN 版本强绑定，Triton-Ascend 的使用应该与 CANN 版本一一对应」，详见 Triton-Ascend 兼容性页面。
- **v0.3.1 组件缺失说明（原文）**：「v0.3.1 版本未使用 MegatronAdaptor 与 TransformerEngineNPU 组件，表中"/"表示不配套。」
- **升级业务影响（原文）**：「软件版本升级过程中会导致业务中断」；对网络通信无影响。
- **原文未涉及**：训练吞吐（tokens/s）、MFU、性能基准对比等性能数据均未出现。

---

## 【表格解读】

### 表格 1：产品版本信息

| 项目 | 内容 |
|---|---|
| 产品名称 | MindSpeed |
| 产品版本 | 0.3.1 |
| 版本类型 | 正式版本 |
| 组件名称 | MindSpeed Bridge |
| 发布时间 | 2026年7月 |
| 维护周期 | 6个月 |

**逐行解读**：
- 组件名明确为「MindSpeed Bridge」（昇腾适配 Bridge 模型代码集合）。
- 维护周期 6 个月意味着从 2026 年 7 月发布起，至 2027 年 1 月前应享受正式维护。
- 版本类型为「正式版本」（非 RC/beta）。

---

### 表格 2（原文表 1）：MindSpeed Bridge 核心组件版本配套表

| MindSpeed Bridge 版本 | Megatron-Bridge 版本 | Megatron-LM 代码分支 | MindSpeed Core 代码分支 | MegatronAdaptor 代码分支 | TransformerEngineNPU 版本 | MindSpeed-Ops 版本 |
|---|---|---|---|---|---|---|
| master（在研版本）| v0.5.0 | core_v0.18.0 | core_r0.18.0 | core_r0.18.0 | main（在研版本） | master（在研版本） |
| v0.3.1 | v0.3.1 | core_v0.16.1 | core_r0.16.0 | / | / | 26.1.0 |

**逐行解读**：
- **master 行**：核心三方全部对齐到 0.18.x 体系；首次引入 MegatronAdaptor（core_r0.18.0）和 TransformerEngineNPU（main）。
- **v0.3.1 行**：仍绑定 Megatron-Bridge v0.3.1、Megatron-LM core_v0.16.1、MindSpeed Core core_r0.16.0；**未使用** MegatronAdaptor 与 TransformerEngineNPU（"/"）；MindSpeed-Ops 固定为 26.1.0。
- 对比表明：从 v0.3.1 升级到 master 会发生**核心运行时栈的整体替换**（MindSpeed 栈 → MegatronAdaptor+TransformerEngineNPU 栈）。

---

### 表格 3（原文表 2）：MindSpeed Bridge 运行环境版本配套表

| MindSpeed Bridge 版本 | Python 版本 | PyTorch 版本 | TorchNPU 版本 | torchvision 版本 | CANN 版本 | Triton-Ascend 版本 |
|---|---|---|---|---|---|---|
| master（在研版本）| Python3.12 | 2.10.0 | 在研版本 | 0.25.0 | 在研版本 | 在研版本 |
| v0.3.1 | Python3.12 | 2.9.0 | 26.1.0 | 0.24.0 | 9.1.0 | 3.2.2 |

**逐行解读**：
- v0.3.1 运行环境完全固化：Python3.12 + PyTorch 2.9.0 + TorchNPU 26.1.0 + torchvision 0.24.0 + CANN 9.1.0 + Triton-Ascend 3.2.2。
- master 行 PyTorch 升至 2.10.0，torchvision 升至 0.25.0；TorchNPU/CANN/Triton-Ascend 均为在研版本号（待发布时确定）。
- Python 大版本一致（3.12），不涉及跨大版本 Python 兼容问题。

---

### 表格 4（原文表 3）：MindSpeed Bridge 与 TorchNPU 版本兼容

| MindSpeed Bridge \ TorchNPU 版本 | 26.1.0 | master（在研版本） |
|---|---|---|
| v0.3.1 | Y | / |
| master（在研版本） | Y | Y |

**逐行解读**：
- v0.3.1 仅与 **TorchNPU 26.1.0** 配套（Y），与 master 不配套（/）。
- master 同时兼容 TorchNPU 26.1.0 与自身 master，体现「高版本向下兼容」原则。

---

### 表格 5（原文表 4）：MindSpeed Bridge 与 CANN 版本兼容

| MindSpeed Bridge \ CANN 版本 | 9.1.0 | 在研版本 |
|---|---|---|
| v0.3.1 | Y | / |
| master（在研版本） | Y | Y |

**逐行解读**：
- v0.3.1 仅与 **CANN 9.1.0** 配套，与在研 CANN 未验证（/）。
- master 同时兼容 CANN 9.1.0 与在研 CANN；结合原文「Triton-Ascend 与 CANN 强绑定」可知，升级 CANN 时必须同步检查 Triton-Ascend 版本。

---

### 表格 6：新增特性

| 组件 | 描述 | 目的 |
|---|---|---|
| MindSpeed Bridge | 新增模型支持 | 新增 Kimi-K3 多模态模型训练与适配，新增 Qwen3.5-VL-397B-A17B SFT 脚本，新增 GLM5.2 32k TND 高性能 POC 脚本 |
| MindSpeed Bridge | 训练效率提升 | Qwen3.5-VL 支持 pack（序列打包）与上下文并行（CP）；支持 MoE permute 融合；GLM5/GLM5.2 支持融合算子与 packed TND 训练；新增预加载 VLM 数据集 shuffle 控制 |
| MindSpeed Bridge | 依赖升级与架构调整 | 升级 Megatron-Bridge 至 v0.5.0、Megatron-LM 至 core_v0.18.0；以 MegatronAdaptor 与 TransformerEngineNPU 替换 MindSpeed；通过 Git Submodule 统一管理三方依赖版本；统一特性生命周期 |

**逐行解读**：
- **模型覆盖**：从纯 LLM 扩展到多模态（Kimi-K3）、视觉语言大模型（Qwen3.5-VL-397B-A17B）、稠密/稀疏混合架构（GLM5.2）。
- **效率维度**：pack、CP、permute 融合、packed TND 全部面向**减少 padding 浪费**与**算子级融合**两个核心优化方向。
- **架构维度**：依赖从单一 MindSpeed 体系过渡到 Megatron 适配层 + TransformerEngineNPU 体系，依赖管理改为 Git Submodule 单一来源。

---

### 表格 7：已解决问题（仅 master 分支）

| 版本 | 描述 |
|---|---|
| master | 修复 Qwen3.5-VL 在 MTP、CP、PP 及 TP 大于 KV head 数等组合场景下的精度与报错问题 |
| master | 修复 Qwen3.5-VL 权重转换（含 MTP、GDN 离线转换）相关问题 |

**逐行解读**：
- 两条修复均聚焦 **Qwen3.5-VL**，且涉及 **MTP（Multi-Token Prediction）、CP（Context Parallel）、PP（Pipeline Parallel）、TP（Tensor Parallel）** 并行策略组合，说明该模型对并行拓扑敏感。
- 第二条针对权重转换（含 MTP、GDN 离线转换），与训练—推理一致性链路相关。

---

### 表格 8：配套文档

| 文档名称 | 内容简介 | 更新说明 |
|---|---|---|
| 《MindSpeed Bridge 软件安装》（install.md） | 指导用户如何在 NPU 上完成 MindSpeed Bridge 的安装，覆盖硬件/OS 兼容性、驱动固件、CANN 安装、基于 PyTorch 的完整安装流程 | 新增 Git Submodule 统一管理三方依赖的安装方式 |
| 《MindSpeed Bridge 快速入门》（quick_start.md） | 以 Qwen3.5-VL-9B 为例，指导初次使用者快速启动训练任务 | 新增文档 |

**逐行解读**：
- install.md 的关键更新点是「**Git Submodule** 统一管理三方依赖」——配合架构调整，使依赖安装方式与代码管理方式保持一致。
- quick_start.md 是首次新增的上手文档，以 **Qwen3.5-VL-9B** 作为入门样例（不是 397B 大模型），降低体验门槛。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **版本维护策略**（[../../README.md#版本维护策略](../../README.md#版本维护策略)）：本文档主 NOTE 指向该链接，说明 MindSpeed Bridge 的版本维护周期、长期支持等策略性约定，是 v0.3.1 「6 个月维护周期」的上位定义来源。
- **安装指南**（[./install.md](./install.md)）：本文档「配套文档」章节给出引用，本版本的安装方式变更（Git Submodule 统一管理三方依赖）即记录在该文档中。
- **快速入门**（[./quick_start.md](./quick_start.md)）：本文档「配套文档」章节给出引用，以 Qwen3.5-VL-9B 为样例的训练启动流程文档。
- **Triton-Ascend 兼容性**（外部链接）：运行环境表 2 的 NOTE 指向 Triton-Ascend 官方 release note，用于核对 Triton-Ascend ↔ CANN 版本对应关系。
- **上下游组件栈**：本文档通过表 1/表 2/表 3/表 4 显式拉通了 Megatron-Bridge、Megatron-LM、MindSpeed Core、MegatronAdaptor、TransformerEngineNPU、MindSpeed-Oops、TorchNPU、CANN、Triton-Ascend、PyTorch、torchvision、Python 共 12 个上下游依赖的版本/兼容性关系。

---

## 【使用方法】

原文未直接给出 CLI 命令或配置项开关，仅指向以下两份配套文档以获取具体使用方式：

1. **安装方式**：参考 [./install.md](./install.md) —— 本版本新增「Git Submodule 统一管理三方依赖」的安装方式。
2. **快速启动训练**：参考 [./quick_start.md](./quick_start.md) —— 以 Qwen3.5-VL-9B 为例启动首个训练任务。

版本配套选择规则（原文）：
- 选 **v0.3.1** → 需配套 **TorchNPU 26.1.0 + CANN 9.1.0 + Triton-Ascend 3.2.2 + PyTorch 2.9.0**。
- 选 **master** → 可向下兼容 TorchNPU 26.1.0、CANN 9.1.0，同时支持自身在研版本栈。
- 升级前评估：「软件版本升级过程中会导致业务中断」，对网络通信无影响。
