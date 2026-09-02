# MindStudio Kernel Launcher Release Notes

> 仓 `mskl` · 路径 `docs/en/release_notes/release_notes.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mskl/docs/en/release_notes/release_notes.md

# msKL Release Notes 深度解读

---

## 【定位】

本文档是 MindStudio Kernel Launcher (msKL) 产品的发布说明 (Release Notes),描述了两个产品版本 (26.0.0 Beta / 8.3.0 正式版) 与上下游依赖 (CANN、Python) 的版本映射关系,并首次披露 8.3.0 版本中面向算子调试与模板库自动调优的两组核心接口能力。

---

## 【技术要点】

1. **双产品版本并存**:同一时间线披露 Beta 版 `26.0.0` 与正式版 `8.3.0`,二者对应不同的 CANN 依赖版本。

2. **三组对外接口首次发布** (均在 8.3.0):
   - `tiling_func` —— 用于调用 msOpGen 项目中的 tiling 函数。
   - `get_kernel_from_binary` —— 用于调用用户自定义的 Kernel 函数 (便于快速调试)。
   - `autotune` 系列接口 —— 用于模板库 (template library) 算子的代码替换、编译执行与性能对比。

3. **关键依赖约束**:
   - msKL `26.0.0` → CANN `9.0.0` 或更高 + Python 3.11 或更高 (均为"推荐"等级)。
   - msKL `8.3.0` → CANN `8.2.RC1` 或更高 + Python 3.11 或更高 (8.2.RC1 为"或之后"要求,Python 为"推荐")。

4. **兼容性说明**:26.0.0 与 8.3.0 均标注"无兼容性变更 (No compatibility changes / No new features)"。

5. **能力范畴**:8.3.0 是 msKL 的"首次发布 (First release)",定位为算子快速调试 + 模板库高效调优两类开发辅助能力。

---

## 【关键机制与数据】

**工作原理与数据流 (基于原文描述):**

- **tiling_func 路径**:用户提供算子工程 → 通过 `tiling_func` 接口调用 msOpGen 项目里的 tiling 函数 (典型场景:在 host 侧生成 tiling 切分策略)。

- **get_kernel_from_binary 路径**:用户自定义 Kernel 二进制 → 通过 `get_kernel_from_binary` 加载并调用 (典型场景:绕过完整算子工程编译链路,快速验证 Kernel 正确性)。

- **autotune 路径**:模板库算子模板 → autotune 系列接口驱动"代码替换 (code replacement) → 编译 (compilation) → 执行 (execution) → 性能比较 (performance comparison)"四步闭环,用于高效调优。

**性能数据**:原文未提供任何量化性能数据 (如吞吐量、时延、加速比等)。

> 注:原文出现的全部"数字/参数/命令"仅为版本号、Python 主版本号与 CANN 版本号;未给出接口函数签名、调优步数、执行耗时等数据。

---

## 【表格解读】

### 表 1:Product Version Information (产品版本信息)

| Product Name | Product Version | Version Type |
|------|-------|------|
| msKL | 26.0.0 | Beta Version |
| msKL | 8.3.0 | Official Version |

**逐行解读:**

| 行 | 字段值 | 含义 |
|---|---|---|
| 第 1 行 | msKL / 26.0.0 / Beta Version | msKL 主线 Beta 版本,对应下一代 CANN (9.0.0+) 依赖 |
| 第 2 行 | msKL / 8.3.0 / Official Version | msKL 现行正式版本,对应 CANN 8.2.RC1+ 依赖,也是"首次发布"承载能力 |

### 表 2:Related Product Version Mapping (关联产品版本映射)

| msKL | CANN Version | Python Version |
|----------|-----------------|----------|
| 26.0.0 | 9.0.0 or later recommended | Python 3.11 or later recommended |
| 8.3.0 | 8.2.RC1 or later | Python 3.11 or later recommended |

**逐行解读:**

| 行 | 字段值 | 含义 |
|---|---|---|
| 第 1 行 | msKL 26.0.0 ↔ CANN 9.0.0+ (推荐) ↔ Python 3.11+ (推荐) | Beta 版锁定 CANN 9 主线,Python 仅给推荐底线 |
| 第 2 行 | msKL 8.3.0 ↔ CANN 8.2.RC1 or later ↔ Python 3.11+ (推荐) | 正式版可运行于 CANN 8.2 RC1 起的整个 8.2 系列 |

> **注意**:两行中 CANN 列的措辞并不完全对称 —— 26.0.0 标注 "recommended" (推荐),8.3.0 标注 "or later" (或之后,带下限 RC1),Python 列两行均使用 "recommended"。

---

## 【公式解读】

**原文无公式。**

---

## 【关联】

> 原文文末标注"内部链接: (无)",未提供任何超链接。但从文档正文可推断以下关联关系:

| 关联对象 | 关系性质 | 上下游说明 |
|---|---|---|
| **CANN (Compute Architecture for Neural Networks)** | 上游/运行时依赖 | msKL 是 CANN 算子开发工具链中的一环;不同 msKL 版本绑定不同 CANN 主版本 (26.0.0↔9.0.0、8.3.0↔8.2.RC1)。 |
| **msOpGen 项目** | 上游/输入源 | `tiling_func` 接口从 msOpGen 项目中获取 tiling 函数 —— msKL 通过该接口消费 msOpGen 生成的 tiling 策略。 |
| **用户自定义 Kernel (binary 形态)** | 上游/输入源 | `get_kernel_from_binary` 直接消费用户产出的 Kernel 二进制,用于快速调试。 |
| **模板库 (template library) 算子** | 上游/输入源 | autotune 系列接口面向"模板库算子"工作,提供模板替换→编译→执行→对比的闭环调优能力。 |
| **Python 3.11+** | 运行环境依赖 | 两版本均要求 Python 3.11 或更高版本 (推荐等级)。 |

> 原文未提及 msKL 与算子编译器 (AscendC/Ascend CCE)、profiling 工具、模型转换工具等其他 CANN 子模块的交互,故不在此处展开。

---

## 【使用方法】

**启用方式/配置项/命令 (基于原文):**

- **版本选择**:依据目标 CANN 环境选择对应 msKL 版本:
  - 已有 CANN 8.2.RC1 及以上环境 → 选用 msKL `8.3.0` (正式版)。
  - 规划对接 CANN `9.0.0+` → 选用 msKL `26.0.0` (Beta 版)。

- **Python 环境**:建议使用 Python `3.11` 或更高版本。

- **能力调用**:通过以下接口启用对应能力 (仅给出接口名称,原文未给出函数签名/参数):
  - 启用 tiling 函数调用 → 调用 `tiling_func` 接口,目标对象为 msOpGen 项目中的 tiling 函数。
  - 启用自定义 Kernel 快速调试 → 调用 `get_kernel_from_binary` 接口,目标对象为用户自定义 Kernel。
  - 启用模板库算子调优 → 调用 `autotune` 系列接口,依次完成"代码替换 → 编译 → 执行 → 性能比较"四步。

> **说明** —— 原文未涉及具体的命令行 (CLI)、环境变量、配置文件路径、API 参数签名或调用示例,故本节其余内容不予臆造。
