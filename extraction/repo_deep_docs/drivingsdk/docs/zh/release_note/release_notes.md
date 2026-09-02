# 版本说明

> 仓 `drivingsdk` · 路径 `docs/zh/release_note/release_notes.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/drivingsdk/docs/zh/release_note/release_notes.md

# Driving SDK 26.1.0 Release Notes 深度解读

## 【定位】

本篇文档是华为昇腾自动驾驶加速库 **Driving SDK 26.1.0 正式版本** 的版本说明（changelog），系统性描述该版本的版本配套关系、上下游组件兼容矩阵、本次新增/删除特性、升级影响评估、配套文档清单以及安全扫描结果，用于指导开发者进行版本选型、升级评估和环境搭建。

---

## 【技术要点】

1. **版本基线**：Driving SDK 26.1.0（正式版本），发布时间 **2026年7月**，维护周期 **6个月**；对应代码分支为 `branch_v26.1.0`，配套 **CANN 9.1.0** 与 **TorchNPU 26.1.0**。
2. **语言与框架**：配套 **Python 3.9 / 3.10 / 3.11**，**PyTorch 2.7.1 / 2.8.0**。
3. **硬件适配扩展**：Driving SDK 全量算子新增支持 **Ascend 950 系列产品**；自动驾驶模型 BEVFormer、BEVFusion、Sparse4D、MapTRv2、UniAD、SparseDrive 同步适配 Ascend 950。
4. **VLA 模型新增**：新增 GR00T-N1.6、LingBot-VLA、StarVLA 三款 VLA（视觉-语言-动作）模型；其中 GR00T-N1.6 与 Pi0.5 已支持 Ascend 950 系列产品。
5. **兼容性政策**：TorchNPU 与 CANN 均回溯兼容至前若干代版本（TorchNPU 7.2.0 起、CANN 8.3.RCX 起），但 **26.0.0 版本不与最新一代（TorchNPU 26.1.0 / CANN 9.1.X）配套**——只有升级到 26.1.0 才能获得最新一代 CANN/TorchNPU 支持。
6. **升级影响**：软件版本升级过程中**会导致业务中断**；对网络通信无影响；无删除特性、无接口变更、无遗留问题。

---

## 【关键机制与数据】

- **版本维护周期机制**（原文）：Driving SDK 26.1.0 维护周期为 6 个月，与 26.0.0 同样形成 6 个月一迭代的节奏；旧分支 `branch_v26.0.0` 仍在表中列出但已不能搭配最新 CANN/TorchNPU 使用。
- **版本配套数据流**（原文）：Driving SDK 与底层硬件能力通过 CANN（计算架构）→ TorchNPU（PyTorch NPU 适配层）→ Driving SDK（自动驾驶领域算子与模型）三层级联，每一层版本号需在配套表中对齐。
- **升级业务中断提示**（原文）：软件版本升级过程中会导致业务中断——意味着升级需在停机窗口进行，不能热升级。
- **模型新增覆盖**（原文）：本次新增覆盖感知类（BEVFormer、BEVFusion、Sparse4D、MapTRv2、UniAD、SparseDrive）+ VLA 类（GR00T-N1.6、LingBot-VLA、StarVLA），共 6+3=9 个模型条目（Pi0.5 仅声明支持 Ascend 950，未列为新增）。
- **病毒扫描结论**（原文）：QiAnXin、Kaspersky、Bitdefender 三款防病毒软件于 2026-07-06 扫描，结论均为"无病毒，无恶意"。

---

## 【表格解读】

### 表 1：Driving SDK 软件版本配套表（产品分支 × 配套软件）

| Driving SDK代码分支 | CANN版本 | TorchNPU版本 | Python版本 | PyTorch版本 |
|---|---|---|---|---|
| master（在研版本） | 在研版本 | 在研版本 | 3.9, 3.10, 3.11 | 2.7.1, 2.8.0 |
| branch_v26.1.0 | 9.1.0 | 26.1.0 | 3.9, 3.10, 3.11 | 2.7.1, 2.8.0 |
| branch_v26.0.0 | 9.0.0 | 26.0.0 | 3.9, 3.10, 3.11 | 2.7.1, 2.8.0 |

**解读**：表中列出三个代码分支的横截面配套。`master` 分支是"在研"状态，意味着未来正式版本可能演进 Python/PyTorch 支持范围（目前统一为 3.9–3.11 与 2.7.1/2.8.0）。`branch_v26.1.0` 是本文档主版本，CANN 9.1.0 + TorchNPU 26.1.0 为最新一代组合。Python 与 PyTorch 跨度在三个分支间保持一致，说明这三层只更新 CANN/TorchNPU 而不强行抬高 Python/PyTorch 需求，降低了升级成本。注释提示用户可根据需要选择分支下载源码安装。

### 表 2：Driving SDK 与 TorchNPU 版本兼容矩阵

| Driving SDK \ TorchNPU版本 | 7.2.0 | 7.3.0 | 26.0.0 | 26.1.0 |
|---|---|---|---|---|
| 26.0.0 | Y | Y | Y | / |
| 26.1.0 | Y | Y | Y | Y |

**解读**：横向 4 列覆盖 TorchNPU 7.2.0 → 26.1.0 共四个版本；纵向 2 个 Driving SDK 版本。"Y"表示可配套，"/"表示不可配套。关键观察：Driving SDK 26.0.0 与 TorchNPU 26.1.0 不配套——即在 26.1.0 发布时旧的 SDK 不会自动支持新的 TorchNPU；Driving SDK 26.1.0 向后兼容全部四个 TorchNPU 版本。表头用 `rowspan="2"` 标识 Driving SDK 列与下层 4 列版本号并列，结构上是 2×4 矩阵。

### 表 3：Driving SDK 与 CANN 版本兼容矩阵

| Driving SDK \ CANN版本 | 8.3.RCX | 8.5.X | 9.0.X | 9.1.X |
|---|---|---|---|---|
| 26.0.0 | Y | Y | Y | / |
| 26.1.0 | Y | Y | Y | Y |

**解读**：结构与表 2 完全对称。Driving SDK 26.0.0 仅支持到 CANN 9.0.X，不支持 9.1.X；26.1.0 才打通 9.1.X。这隐含 **CANN 9.1.X 是与 26.1.0 同步发布的关键节点**，可能与 Ascend 950 系列产品支持相关——因为更新说明中 Ascend 950 全量算子支持正是在 26.1.0 中提供。

### 配套文档清单

| 文档名称 | 内容简介 | 更新说明 |
|---|---|---|
| 《[软件安装](../installation/installation.md)》 | 指导用户在NPU上完成Driving SDK的安装，内容涵盖硬件与操作系统兼容性说明、软件版本配套说明、驱动固件安装，以及三种软件安装的方式：镜像安装、在线安装、源码安装。帮助用户快速搭建Driving SDK开发环境。 | - |
| 《[快速入门](../get_started/quick_start_guide.md)》 | 以`scatter_max`算子和BEVFusion模型为例，指导初次接触Driving SDK的开发者完成NPU上的高性能算子调用和模型训练任务，帮助用户快速上手自动驾驶模型分布式训练。 | - |

**解读**：两份配套文档覆盖了从"环境搭建"到"上手训练"的完整上线路径。其中安装文档明确给出 **三种安装方式**：镜像安装、在线安装、源码安装；快速入门文档给出 **两个示例**：`scatter_max` 算子（算子级别调用）和 BEVFusion 模型（端到端训练）——BEVFusion 正是本次声明支持 Ascend 950 的模型之一。

### 病毒扫描结果

| 防病毒软件名称 | 防病毒软件版本 | 病毒库版本 | 扫描时间 | 扫描结果 |
|---|---|---|---|---|
| QiAnXin | 8.0.5.5260 | 2026-07-05 08:00:00.0 | 2026-07-06 | 无病毒，无恶意 |
| Kaspersky | 12.0.0.6672 | 2026-07-06 10:03:00 | 2026-07-06 | 无病毒，无恶意 |
| Bitdefender | 7.5.1.200224 | 7.101158 | 2026-07-06 | 无病毒，无恶意 |

**解读**：三种主流杀毒引擎在发布前均完成扫描，时间集中在 2026-07-06，结果一致为"无病毒，无恶意"，表明交付包安全性已通过外部验证。漏洞修补列表为空（"无"），说明本次未涉及 CVE 修补条目。

---

## 【公式解读】

**原文无公式**。

---

## 【关联】

- **分支维护策略**（[README.md#driving-sdk-分支维护策略](../../../README.md#driving-sdk-分支维护策略)）：本文档顶部 NOTE 直接指向该链接，说明每个 Driving SDK 分支的维护时长与终止策略——表 1 中 `branch_v26.0.0` 与 `branch_v26.1.0` 的并存正是该策略的产物；6 个月维护周期是该策略的具体表现。
- **软件安装文档**（[../installation/installation.md](../installation/installation.md)）：是本版本落地的"入口文档"，本文档的"配套文档"节明确依赖该文档完成环境搭建；其内容覆盖驱动固件安装、三种安装方式。
- **快速入门文档**（[../get_started/quick_start_guide.md](../get_started/quick_start_guide.md)）：以 `scatter_max` 算子 + BEVFusion 模型作为示例；后者恰好是本次"新增特性"中声明支持 Ascend 950 的模型之一，文档与版本能力保持同步。

**上下游关系链**：硬件 Ascend 950 ← CANN 9.1.0（计算架构层）← TorchNPU 26.1.0（PyTorch 适配层）← **Driving SDK 26.1.0**（自动驾驶领域算子与模型封装层）← 应用开发者（通过安装文档和快速入门上手）。

---

## 【使用方法】

原文明确给出以下可操作信息（**不涉及具体启用命令**）：

- **代码分支获取**：用户可根据需要选择 Driving SDK 代码分支（`master` / `branch_v26.1.0` / `branch_v26.0.0`）下载源码。
- **版本选型规则**：若需使用 Ascend 950 系列产品（算子或 BEVFormer/BEVFusion/Sparse4D/MapTRv2/UniAD/SparseDrive 模型），或需配套 TorchNPU 26.1.0 / CANN 9.1.X，应选择 `branch_v26.1.0`；若仅维持 26.0.0 的运行环境可继续使用 `branch_v26.0.0`。
- **安装方式**（依据配套文档）：提供三种——**镜像安装**、**在线安装**、**源码安装**，具体步骤参见《软件安装》。
- **Python 运行时选择**：3.9 / 3.10 / 3.11 任一即可；PyTorch 选 2.7.1 或 2.8.0。
- **升级窗口**：升级过程中会导致业务中断，需在停机窗口执行；网络通信不受影响。
- **上手示例**：通过《快速入门》文档运行 `scatter_max` 算子调用与 BEVFusion 模型训练任务。

具体 CLI 命令、API 调用语法、配置文件参数原文未涉及。
