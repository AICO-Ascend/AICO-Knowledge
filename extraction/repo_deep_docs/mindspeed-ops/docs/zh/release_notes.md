# 版本说明

> 仓 `mindspeed-ops` · 路径 `docs/zh/release_notes.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-ops/docs/zh/release_notes.md

# mindspeed-ops/docs/zh/release_notes.md 深度解读

## 【定位】
本文档是 MindSpeed Ops（昇腾优化的训练业务自定义算子实现）在研版本 master 分支的版本说明（changelog），明确告知用户当前产品版本、与其他软件栈（CANN/PyTorch/torch_npu/Triton-Ascend/Python）的版本配套关系、分支维护策略及当前已知问题，作为安装、升级、问题排查的入口参考。

## 【技术要点】
1. **当前发布状态**：MindSpeed Ops 处于"在研版本（master 分支）"，首个正式版本尚未发布，章节下尚无历史正式版本信息；维护周期为 6 个月。
2. **CANN 配套**：与 CANN 9.1.0 版本配套使用。
3. **PyTorch 配套**：要求 PyTorch 版本 ≥ 2.7.1，并要求 `torch_npu` 与对应 PyTorch 版本相匹配（"配套 PyTorch 版本"）。
4. **Triton-Ascend 配套**：要求 Triton-Ascend 3.2.2；且指出 Triton-Ascend 版本与 CANN 版本**强绑定**，必须一一对应。
5. **Python 配套**：要求 Python ≥ 3.10。
6. **TileLang-Ascend 可选依赖**：TileLang 算子依赖 TileLang-Ascend，**默认安装流程不包含**，需要从源码额外安装。
7. **ACLNN/AscendC 依赖芯片型号**：ACLNN（AscendC）算子依赖编译时的芯片型号环境变量 `SOC_VERSION`，不同芯片取值需参考源码安装方式。
8. **分支生命周期分四阶段**：计划（1-3 月）→ 开发（3 月）→ 维护（6/12 月，常规 6 个月、长期支持版本 12 个月）→ 无维护（0-3 月）→ EOL；其中维护阶段会"合入所有已解决的问题并发布版本"。
9. **已知问题**：存在 `module 'triton.language' has no attribute 'extract_slice'` 的 Triton 缺失属性错误。

## 【关键机制与数据】
- **版本强绑定机制**：Triton-Ascend 与 CANN 必须一一对应（原文："Triton-Ascend版本与CANN版本强绑定，Triton-Ascend的使用应该与CANN版本一一对应"），用户需通过外链 `https://triton-ascend.readthedocs.io/zh-cn/latest/release_note.html#id13` 查询兼容性矩阵。
- **TileLang-Ascend 异步安装机制**：默认 `pip` 安装不会拉取 TileLang-Ascend，导致 TileLang 算子在未手动安装时不可用（原文："TileLang算子依赖TileLang-Ascend，默认安装流程不包含该依赖，需从源码额外安装"）。
- **SOC_VERSION 编译期绑定机制**：ACLNN（AscendC）算子在编译时被绑定到具体芯片型号，跨芯片复用产物会触发二进制不匹配问题，因此需在源码编译阶段指定环境变量（原文："ACLNN（AscendC）算子依赖编译时的芯片型号（`SOC_VERSION`）"）。
- **维护周期数据**：常规版本维护 6 个月，长期支持版本维护 12 个月；无维护阶段仍接受 0-3 个月合入，无版本发布。
- **兼容版本数字清单**（原文）：
  - MindSpeed Ops：master（在研）
  - CANN：9.1.0
  - PyTorch：≥ 2.7.1
  - torch_npu：随 PyTorch 配套
  - Triton-Ascend：3.2.2
  - Python：≥ 3.10

## 【表格解读】

### 表 A：产品版本信息表（原文逐字还原）

| 产品名称 | MindSpeed |
| --- | --- |
| 产品版本 | master（在研版本） |
| 版本类型 | 在研版本 |
| 组件名称 | MindSpeed Ops |
| 维护周期 | 6个月 |

解读：该表声明本文档归属的"产品—组件—版本—状态—维护期"五元组。值得注意的是：**当前 master 分支尚未发布正式版本**，因此对应的版本号列填的是分支名而非语义化版本号；维护周期标注为 6 个月，符合正文中"常规版本维护周期为 6 个月"的约定。该表是版本配套说明的总纲，下方"相关产品版本配套说明"是它的依赖链展开。

### 表 B：MindSpeed Ops 软件版本配套表（原文表 1，逐字还原）

| MindSpeed Ops版本 | CANN版本 | PyTorch版本 | torch_npu版本 | Triton-Ascend版本 | Python版本 |
| --- | --- | --- | --- | --- | --- |
| master（在研版本） | 9.1.0 | >=2.7.1 | 配套PyTorch版本 | 3.2.2 | >=Python3.10 |

解读：这是用户安装/升级时最关键的兼容性矩阵。**逐列含义**：
- "**MindSpeed Ops版本**"列：master 表示当前唯一在研分支。
- "**CANN版本**"列：9.1.0 是被锁定的升腾计算架构版本，要求用户环境先安装对应 CANN 套件。
- "**PyTorch版本**"列：`>=2.7.1` 表示下界已固定，上界未在表中说明（即存在进一步兼容性需用户验证）。
- "**torch_npu版本**"列：未填具体数字，只写"配套 PyTorch 版本"——意为无需独立选版，**跟随 PyTorch 版本发布**即可，避免双源依赖导致的失配。
- "**Triton-Ascend版本**"列：3.2.2 是当前唯一可用版本；且与 CANN 9.1.0**必须一一对应**（见原文 NOTE）。
- "**Python版本**"列：`>=Python3.10` 限定了 Python 解释器最小版本。

> 表格下方的四条 NOTE 是对表的"补充规则"：①用户使用源码安装路径；②Triton-Ascend 与 CANN 强绑定；③TileLang-Ascend 需额外源码安装；④ACLNN 算子需在源码安装时按 `SOC_VERSION` 选用芯片型号。

### 表 C：分支维护策略表（原文逐字还原）

| 状态 | 时间 | 说明 |
| --- | --- | --- |
| 计划 🕐 | 1-3 个月 | 计划特性 |
| 开发 🕔 | 3 个月 | 开发特性 |
| 维护 🕚 | 6-12 个月 | 合入所有已解决的问题并发布版本，针对不同的MindSpeed Ops版本采取不同的维护策略，常规版本和长期支持版本维护周期分别为6个月和12个月 |
| 无维护 🕛 | 0-3 个月 | 合入所有已解决的问题，无专职维护人员，无版本发布 |
| 生命周期终止（EOL）🚫 | N/A | 分支不再接受任何修改 |

解读：这是发布生命周期的状态机图谱。
- **计划（1-3 月）**：仅做特性规划，不写代码。
- **开发（固定 3 个月）**：实际的特性开发窗口。
- **维护（6-12 个月）**：**唯一对外发布版本的窗口期**，并按发行类型分两条支线——常规版（6 个月）与 LTS 版（12 个月），由这条规则直接支撑了"产品版本信息表"中"维护周期 6 个月"的填值。
- **无维护（0-3 个月）**：进入衰退期，但仍可合入已修复的缺陷，仅不再有正式 Release。
- **EOL**：硬终止，任何合入都不被接受。
- 五列总计覆盖了一个版本分支从立项到废弃的完整时间区间，使下游用户能据此判断自己所处的分支处于支持窗口内还是外。

### 表 D：已知问题表（原文逐字还原）

| 现象 | 介绍 |
| --- | --- |
| `module 'triton.language' has no attribute 'extract_slice'` | [问题介绍](qa/extract_slice.md) |

解读：当前 master 分支已确认存在一项 Triton 内置属性缺失问题，错误信息为 `triton.language` 模块没有 `extract_slice` 属性。该问题指向性强——它通常发生在新版 Triton（≥2.x）已弃用或重命名了 `extract_slice`、但本仓库依赖链中又恰好调用旧版 API 的情形；用户遇到相同报错时可点击"问题介绍"链接（`qa/extract_slice.md`）跳转到仓库内部的问题答疑文档以获取解答或临时变通方案。

## 【公式解读】
原文无公式。

## 【关联】
- **安装路径**：文中"相关产品版本配套说明"小节明确指引用户参考 [`install_guide.md`](install_guide.md) 进行安装，是本文档与安装文档之间的主跳转链路。
- **TileLang-Ascend 安装分支**：[`install_guide.md#可选安装tilelang-ascend以使用tilelang算子`](install_guide.md#可选安装tilelang-ascend以使用tilelang算子)，对应 NOTE 中"TileLang算子依赖TileLang-Ascend，需从源码额外安装"——这说明 TileLang 算子是 MindSpeed Ops 的可选能力分支，**不在默认安装范围内**。
- **源码安装 / SOC_VERSION 选择**：[`install_guide.md#方式二源码安装`](install_guide.md#方式二源码安装)，对应 ACLNN（AscendC）算子的 `SOC_VERSION` 编译期变量说明，意味着用户从源码构建时必须先确定芯片型号（如 Ascend 910B/310P 等）才能产出可运行的二进制。
- **外部依赖 Triton-Ascend**：通过外链 `https://triton-Ascend.readthedocs.io/zh-cn/latest/release_note.html#id13` 与上游 Triton-Ascend 的兼容性矩阵联动，确认 3.2.2 版本对应的 CANN 版本。
- **已知问题答疑链路**：[`qa/extract_slice.md`](qa/extract_slice.md) 是本 changelog 中"已知问题"列的目标文，本文是该问题的总入口。
- **版本维护策略**：[`#分支维护策略`](release_notes.md#分支维护策略) 是本文档内自锚链接，上文产品版本表 NOTE 中"具体请参见版本维护策略"即指向此处。
- **PyTorch ↔ torch_npu**：通过表中"配套PyTorch版本"形成依赖对齐约束，二者必须**同源发布**，任一版本单独升级都会破坏 MindSpeed Ops 的运行环境。

## 【使用方法】
原文在"使用方法"层面只给出**指引路径**，未列具体 `pip`/环境变量命令。归纳如下：
1. **软件栈准入**：用户需先在环境中备齐 CANN 9.1.0、PyTorch ≥ 2.7.1、对应 `torch_npu`、Triton-Ascend 3.2.2、Python ≥ 3.10 这五项依赖（详见"相关产品版本配套说明 表 1"）。
2. **代码获取**：根据需要选择 MindSpeed Ops 的代码分支下载源码，进入 [`install_guide.md`](install_guide.md) 跟随安装步骤进行安装。
3. **Triton-Ascend 一致性校验**：在安装前先按外链 `https://triton-ascend.readthedocs.io/zh-cn/latest/release_note.html#id13` 确认 Triton-Ascend 3.2.2 与 CANN 9.1.0 的兼容性，避免跨版本组合。
4. **TileLang 算子启用（可选）**：若需使用 TileLang 算子，需额外按 [`install_guide.md#可选安装tilelang-ascend以使用tilelang算子`](install_guide.md#可选安装tilelang-ascend以使用tilelang算子) 章节从源码安装 TileLang-Ascend。
5. **ACLNN（AscendC）算子构建**：从源码编译时必须按 [`install_guide.md#方式二源码安装`](install_guide.md#方式二源码安装) 设置 `SOC_VERSION` 环境变量以匹配实际芯片型号，否则算子二进制与目标硬件不兼容。
6. **遇到 Triton `extract_slice` 报错**：跳转 [`qa/extract_slice.md`](qa/extract_slice.md) 查看已知原因与处理方式。

> 原文未涉及具体的 `pip install` / `export SOC_VERSION=...` 等命令级操作步骤，需结合安装文档使用。
