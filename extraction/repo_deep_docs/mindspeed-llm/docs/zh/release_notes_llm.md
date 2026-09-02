# 版本说明

> 仓 `mindspeed-llm` · 路径 `docs/zh/release_notes_llm.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-llm/docs/zh/release_notes_llm.md

# MindSpeed LLM 26.1.0 版本说明文档深度解读

## 【定位】

本文档是 MindSpeed LLM 26.1.0 正式版本的发布说明（changelog），用于向用户告知该版本的产品配套关系、与上游组件的版本兼容矩阵、新增/删除特性、升级影响以及配套文档索引，是该版本上线的官方版本声明文件。

## 【技术要点】

1. **版本基线**：MindSpeed LLM 26.1.0 配套 MindSpeed Core 分支 `26.1.0_core_r0.12.1`、Megatron `core_v0.12.1`、PyTorch `2.7.1`、TorchNPU `26.1.0`、CANN `9.1.0`、Triton-Ascend `3.2.2`、Python `3.10`，维护周期为 6 个月。
2. **模型新增**：新增 Megatron 训练后端对 **Seed-OSS** 与 **GLM5** 两种模型训练的支持。
3. **工具效率提升**：新增**异步保存权重**能力，可在不阻塞主训练流程的情况下完成 checkpoint 落盘。
4. **硬件支持扩展**：新增对 **Ascend 950 系列产品**的硬件适配。
5. **模型下架清单**：InternLM3-8B、LLaMA2-7B/70B、LLaMA3.1-405B、Mamba2-2.7B/8B、Mamba2-Hybrid-8B 共 7 个模型被移除。
6. **特性下架**：QLoRA 及其相关脚本被下架，不再随该版本提供。

## 【关键机制与数据】

本文档属于 release notes 性质，未描述训练机制/数据流/性能数据，仅以兼容性矩阵形式给出配套版本信息。"原文未涉及性能数据"。

## 【表格解读】

### 表 1：MindSpeed LLM 软件版本配套表

| MindSpeed LLM 版本 | MindSpeed Core 代码分支名称 | Megatron 版本 | PyTorch 版本 | TorchNPU 版本 | CANN 版本 | Triton-Ascend 版本 | Python 版本 |
|---|---|---|---|---|---|---|---|
| master（在研版本）| master（在研版本）| core_v0.12.1 | 2.10.0 | 在研版本 | 在研版本 | 在研版本 | Python3.12 |
| 26.1.0 | 26.1.0_core_r0.12.1 | core_v0.12.1 | 2.7.1 | 26.1.0 | 9.1.0 | 3.2.2 | Python3.10 |
| 26.0.0 | 26.0.0_core_r0.12.1 | core_v0.12.1 | 2.7.1 | 26.0.0 | 9.0.0 | 3.2.1 | Python3.10 |

**逐行解读**：
- 第 1 行：`master` 分支为在研版本，对应下一代 Megatron `core_v0.12.1`、PyTorch `2.10.0` 与 Python `3.12`，TorchNPU/CANN/Triton-Ascend 均为在研版本，作为未来演进方向。
- 第 2 行：本次发布的 `26.1.0` 正式版本，锁定 Core 分支 `26.1.0_core_r0.12.1`、Megatron `core_v0.12.1`、PyTorch `2.7.1`、TorchNPU `26.1.0`、CANN `9.1.0`、Triton-Ascend `3.2.2`、Python `3.10`，是当前推荐生产配套。
- 第 3 行：上一版本 `26.0.0`，区别于 `26.1.0` 之处仅在 TorchNPU（`26.0.0`）、CANN（`9.0.0`）与 Triton-Ascend（`3.2.1`），说明本次小版本升级主要驱动的是底层 NPU 栈与 Triton-Ascend 的同步升级。

### 表 2：MindSpeed LLM 与 TorchNPU 版本兼容

| MindSpeed LLM \ TorchNPU | 7.2.0 | 7.3.0 | 26.0.0 | 26.1.0 |
|---|---|---|---|---|
| 26.0.0 | Y | Y | Y | / |
| 26.1.0 | Y | Y | Y | Y |

**逐行解读**：
- `26.0.0` 行：与 TorchNPU `7.2.0`、`7.3.0`、`26.0.0` 均兼容，与 `26.1.0` 不兼容（"/"）。
- `26.1.0` 行：与 TorchNPU `7.2.0`、`7.3.0`、`26.0.0` 三个历史版本均保持向后兼容，并新增对 `26.1.0` 的官方支持，是兼容矩阵最宽的一行。

### 表 3：MindSpeed LLM 与 CANN 版本兼容

| MindSpeed LLM \ CANN | 8.3.RCX | 8.5.X | 9.0.X | 9.1.X |
|---|---|---|---|---|
| 26.0.0 | Y | Y | Y | / |
| 26.1.0 | Y | Y | Y | Y |

**逐行解读**：
- `26.0.0` 行：与 CANN `8.3.RCX`、`8.5.X`、`9.0.X` 兼容，与 `9.1.X` 不兼容。
- `26.1.0` 行：在保留 `26.0.0` 全部向下兼容项的基础上，新增对 CANN `9.1.X` 的官方支持，与表 2 中 TorchNPU `26.1.0` 的支持同步推进。

### 新增特性表

| 组件 | 描述 | 目的 |
|---|---|---|
| MindSpeed LLM | Megatron 训练后端新增模型支持 | 支持 Seed-OSS、GLM5 模型训练 |
| MindSpeed LLM | 工具效率提升 | 支持异步保存权重 |
| MindSpeed LLM | 新增硬件支持 | 支持 Ascend 950 系列产品 |

### 删除特性表

| 组件 | 描述 | 目的 |
|---|---|---|
| MindSpeed LLM | 模型下架 | 模型下架清单：InternLM3-8B / LLaMA2-7B/70B / LLaMA3.1-405B / Mamba2-2.7B/8B / Mamba2-Hybrid-8B |
| MindSpeed LLM | 特性下架 | 下架特性 QLoRA 以及相关脚本 |

### 配套文档表

| 文档名称 | 内容简介 | 更新说明 |
|---|---|---|
| MindSpeed LLM 软件安装 `./pytorch/training/install_guide.md` | 指导用户在 NPU 上完成安装，覆盖硬件/操作系统兼容性、驱动固件与 CANN 安装、PyTorch 框架完整安装流程 | 安装操作适配版本配套分支，新增 Triton-Ascend 安装 |
| MindSpeed LLM 快速入门（基于 Megatron 训练后端）`./pytorch/training/quick_start.md` | 以 Qwen3-8B 为例，演示 NPU 上基于 Megatron 后端的预训练与微调 | Qwen3 系列支持数据与权重在线加载训练，训练操作步骤同步优化 |
| MindSpeed LLM 快速入门（基于 FSDP2 训练后端）`./pytorch/training/fsdp2_quick_start.md` | 以 Qwen3-8B 为例，演示 NPU 上基于 FSDP2 后端的预训练与微调 | 新增文档，基于 FSDP2 后端进行模型预训练与微调 |

### 病毒扫描结果表

| 防病毒软件名称 | 防病毒软件版本 | 病毒库版本 | 扫描时间 | 扫描结果 |
|---|---|---|---|---|
| QiAnXin | 8.0.5.5260 | 2026-07-05 08:00:00.0 | 2026-07-06 | 无病毒，无恶意 |
| Kaspersky | 12.0.0.6672 | 2026-07-06 10:03:00 | 2026-07-06 | 无病毒，无恶意 |
| Bitdefender | 7.5.1.200224 | 7.101158 | 2026-07-06 | 无病毒，无恶意 |

## 【公式解读】

原文无公式。

## 【关联】

- **与配套文档的上下游关系**：本文档作为版本说明，向上承接 `install_guide.md`（安装前置）、`quick_start.md`（Megatron 后端训练入门）、`fsdp2_quick_start.md`（FSDP2 后端训练入门），三份文档均以本版本配套矩阵为前提。
- **与 Megatron 后端的关联**：`26.1.0` 在 Megatron `core_v0.12.1` 之上新增 Seed-OSS、GLM5 模型支持，新增异步保存权重能力，属于 Megatron 训练后端范畴。
- **与 FSDP2 后端的关联**：`fsdp2_quick_start.md` 是本版本首次配套引入的快速入门文档，表明 `26.1.0` 已具备 FSDP2 后端的训练能力。
- **与硬件栈的关联**：`26.1.0` 对 TorchNPU `26.1.0`、CANN `9.1.0`、Triton-Ascend `3.2.2` 同时升级，并新增 Ascend 950 系列硬件支持，说明该版本是底层驱动 + 中间件 + 训练框架的同步联动发布。
- **与外部链接的关联**：文末指向 `gitcode.com/Ascend/MindSpeed-LLM` 的版本维护策略，以及 `triton-ascend.readthedocs.io` 的 Triton-Ascend 兼容性说明，标明 Triton-Ascend 与 CANN 强绑定关系。

## 【使用方法】

本文档为版本说明，并未直接给出训练启动命令或配置项。其使用方法指向三份配套文档：

- 安装准备：参见 `./pytorch/training/install_guide.md`，按本文档"表 1"所示依赖（PyTorch 2.7.1、TorchNPU 26.1.0、CANN 9.1.0、Triton-Ascend 3.2.2、Python 3.10）进行环境搭建。
- Megatron 后端训练入门：参见 `./pytorch/training/quick_start.md`，可参考 Qwen3-8B 在新版本中"数据和权重在线加载训练"的步骤。
- FSDP2 后端训练入门：参见 `./pytorch/training/fsdp2_quick_start.md`（本版本新增）。

其他启用项（异步保存权重、Seed-OSS/GLM5 模型训练、Ascend 950 适配）原文未涉及具体配置命令，需查阅后续 feature 文档。
