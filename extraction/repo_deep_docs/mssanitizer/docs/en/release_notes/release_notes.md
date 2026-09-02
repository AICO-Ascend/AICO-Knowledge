# MindStudio Sanitizer Release Notes

> 仓 `mssanitizer` · 路径 `docs/en/release_notes/release_notes.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mssanitizer/docs/en/release_notes/release_notes.md

# msSanitizer 26.0.0 / 8.3.0 发布说明深度解读

---

## 【定位】

本文档是 **MindStudio Sanitizer（msSanitizer）** 的版本发布说明，覆盖两个版本：**26.0.0（内测版）** 与 **8.3.0（正式版）**，集中说明了与上游 CANN/编译器/工具链的版本映射与兼容性，并详细罗列了 26.0.0 的新增功能（含 AscendC 算子内存/竞争/同步检查、UI 优化、MSTX 可扩展接口、构建发布改进）与 18+ 条 Bug Fix，以及 8.3.0 这个首个正式版所支持的四大基础检查能力。

---

## 【技术要点】

**T1. AscendC 算子检查能力扩展**
原文：「Added out-of-bounds check support for `LocalTensor` across AscendC monocular and binocular computation APIs as well as data movement APIs.」以及 SIMT ↔ Main-Scalar 跨流水线内存腐蚀检查、SIMTR VF 内线程间竞争检查、`SET_FLAG` 冗余检查。

**T2. 新增同步原语插桩与上报**
原文新增插桩命令：`SET_FLAG` / `WAIT_FLAG` / `SET_FLAGI` / `WAIT_FLAGI` / `HSET` / `HWAIT` / `GET_BUF` / `RLS_BUF`，用于增强 inter-core 与 intra-core 同步场景下的竞争检查能力（race check）。

**T3. 适配毕昇编译器新编译选项**
原文：「Adapted to the new `--cce-use-legacy-mixkernel-mangling` compilation option of the BiSheng Compiler.」并同步适配了 CANN 包内 chip 标识变化与多个新 chip 规格/模型变体。

**T4. 可扩展接口（MSTX）**
原文：「Added the MSTX interface on the kernel for reporting inter-core barrier and `set_flag`/`wait_flag` semantics.」并通过新增的 `sanitizer_report.h` 头文件对外暴露 MSTX 接口，支持用户自定义集成；移除了内存池信息上报接口中绑定 region 与 heap 的限制，允许直接注册 region。

**T5. UI 与开发者体验**
原文新增 `--demangle` 命令行选项（控制 UI 中函数名显示格式）、检查过程中实时显示 kernel 信息并在结束时提示是否存在异常、支持获取程序开始时的实时寄存器状态与结束时的默认值。

**T6. 构建/发布工程化改进**
原文：「Optimized the download of UT dependencies, increasing the speed by 10 times and completely resolving the issue of occasional failures.」并启用 UT 默认 debug 编译、新增 VS Code 断点调试、安装最小权限收紧为 `700`、解决了 GCC 11.x 后期版本 UT 编译失败及 GCC 12.x 兼容性、标准化安装包名称并将 `sanitizer_report.h` 纳入发布包。

---

## 【关键机制与数据】

> 注：原文未提供工作原理图或数据流图；以下仅基于原文语句梳理可推导出的机制与量化数据。

- **检查分层机制（原文）**：26.0.0 的"Function"分类下划分为 *Check function*（运行时检查逻辑）与 *UI*（结果呈现），再叠加 *Scalability*（MSTX 可扩展）层，形成"检测—上报—展示—扩展"分层结构。
- **同步指令插桩扩面（原文）**：一次性新增 8 条同步类指令的 instrumentation，目的是"enhance race check capabilities"，覆盖 inter-core 与 intra-core 两类同步。
- **UI 提示机制（原文）**：检查完成后用户会被明确提示"whether any exceptions were detected"，并支持查看程序起始的实时寄存器状态与结束时的默认寄存器值。
- **UT 下载性能数据（原文量化）**：「increasing the speed by 10 times and completely resolving the issue of occasional failures」——原文明确给出 10× 加速，并强调消除了偶发失败。
- **可扩展 MSTX（原文）**：`sanitizer_report.h` 作为用户自定义集成的对外入口；移除 region↔heap 绑定限制后，可直接注册 region（降低用户接入成本）。
- **安装权限收紧（原文）**：root 用户对安装相关文件夹的最小权限由原值变为 `700`。

---

## 【表格解读】

### 表 1：Product Version（产品版本映射）

| Product Name| Version | Version Type |
|------|-------|------|
| msSanitizer | 26.0.0 | Internal test version |
| msSanitizer | 8.3.0 | Official version |

**逐行解读**：
- 第 1 行：`msSanitizer 26.0.0` 为**内测版本（Internal test version）**，用于提前验证新能力。原文将其版本号置于 8.3.0 之后但标记为内测，意味着新版本号体系（26.0.0）已替代旧的 8.x 体系作为内测线。
- 第 2 行：`msSanitizer 8.3.0` 为**正式版本（Official version）**，是首个对外官方版本（与下方"8.3.0 是首个正式版"的说明一致）。

### 表 2：Related Product Versions（关联产品/依赖版本映射）

| msSanitizer Version | CANN Version | Python version | JSON Version | SecureC Version | Makeself Version | llvm-project Version |
|----------|-----------------|----------|----------|----------|----------|----------|
| 26.0.0 | 9.0.0 or later is recommended. | Python 3.11 or later is recommended. | v3.12.0 or later | v1.1.16 or later | release-2.5.0 or later | 19.1.7 |
| 8.3.0 | 8.2.RC1 or later | Python 3.11 or later is recommended. | v3.12.0 or later | v1.1.16 or later | release-2.5.0 or later | 19.1.7 |

**逐行解读**：
- **第 1 行（26.0.0 内测线）**：要求 **CANN ≥ 9.0.0（推荐）**、**Python ≥ 3.11（推荐）**、JSON ≥ v3.12.0、SecureC ≥ v1.1.16、Makeself ≥ release-2.5.0、llvm-project 锁定 **19.1.7**。反映 26.0.0 需要与较新的 CANN 9.0 主线对齐，享受新 chip 标识/规格带来的检查能力。
- **第 2 行（8.3.0 正式线）**：CANN 阈值下放至 **8.2.RC1**（即 8.2 RC1 之后即可），其余依赖与 26.0.0 完全一致。两条线共享同一套下游依赖，差异主要集中在 CANN 主版本。
- **共同列（Python/JSON/SecureC/Makeself/llvm-project）**：在两个版本中均保持一致，表明工程团队已统一底座依赖，只在产品本身与 CANN 主版本上演进。

---

## 【公式解读】

**原文无公式**。文档内容以版本说明、功能条目、Bug 列表为主，未出现任何 LaTeX 数学表达式或伪代码公式。本节不予展开。

---

## 【关联】

由原文表格与"Version Compatibility / Feature Updates"段落，可推导 msSanitizer 在上下游生态中的位置如下：

- **上游依赖（编译器侧）**
  - **BiSheng Compiler**：26.0.0 适配其新编译选项 `--cce-use-legacy-mixkernel-mangling`，说明 sanitizer 在算子构建产物上对该编译器的新行为有明确对接。
- **上游依赖（运行时侧）**
  - **CANN（推荐 ≥ 9.0.0）**：同步适配了 CANN 包内的 chip 标识变化与新 chip 规格/模型变体，是 sanitizer 解析目标二进制与硬件行为的基础。
  - **Python ≥ 3.11**：驱动工具链或脚本侧能力。
  - **JSON v3.12.0、SecureC v1.1.16、Makeself release-2.5.0、llvm-project 19.1.7**：底座库，与 sanitizer 自身能力无直接耦合，但决定可发布范围。
- **下游集成接口**
  - **`sanitizer_report.h`**：作为 sanitize 暴露给算子/用户代码的可扩展入口，用户可通过该头自定义 MSTX 集成。
  - **MSTX（Sanitizer Tracing eXtension）接口**：用于上报 inter-core barrier 以及 `set_flag`/`wait_flag` 语义，连接 sanitizer 与运行时追踪体系。
- **横跨能力（本工具自身四大领域）**
  - 与 8.3.0 引入的四大能力一一对照：Memory check / Race check / Uninitialization check / Synchronization check。26.0.0 在这四大领域均做了扩展（新增 LocalTensor OOB、SIMT↔Main-Scalar、SIMTR VF 内 race、`SET_FLAG` 冗余、同步指令插桩等）。
- **开发者侧**
  - **VS Code + 调试编译**：构建/发布章节新增的"debug 编译 + 断点调试"链路，将 sanitizer 工程与 IDE 调试整合。

---

## 【使用方法】

以下条目均来自原文（Version Compatibility、Feature Updates、Scalability、Build and release 等小节）：

- **启用 AscendC 算子内存/竞争/同步检查**：在 26.0.0 / 8.3.0 上对 Ascend C 算子运行 sanitizer，即可自动覆盖——
  - Global memory 与 Local memory 的越界与未对齐访问（8.3.0 基础能力；26.0.0 扩展至 LocalTensor 跨 monocular/binocular 计算 API 与数据搬运 API 的越界检查）。
  - 并发内存访问导致的数据竞争（race check）。
  - 未初始化变量造成的内存读取异常。
  - Ascend C 算子中 `SetFlag`/`WaitFlag` 配对检查；26.0.0 进一步覆盖 `SET_FLAG` / `WAIT_FLAG` / `SET_FLAGI` / `WAIT_FLAGI` / `HSET` / `HWAIT` / `GET_FLAG` / `RLS_FLAG`(注：原文为 `GET_BUF`/`RLS_BUF`)。
- **UI 控制**：使用命令行选项 `--demangle` 控制界面中函数名的显示格式；检查完成后通过 UI 提示查看是否存在异常。
- **寄存器查看**：启用"实时寄存器状态获取"以在程序开始时查看实时寄存器值，并在结束时查看默认值。
- **自定义集成 MSTX**：包含 `sanitizer_report.h` 头文件，使用其暴露的内核侧 MSTX 接口上报 inter-core barrier 及 `set_flag`/`wait_flag` 语义，并可直接通过新版内存池上报接口注册 region（不再要求预先绑定 region 与 heap）。
- **构建/调试工程**：
  - 26.0.0 启用了 UT 的**默认 debug 编译模式**，并新增了对 **VS Code 断点调试**的支持。
  - 安装时 root 用户对相关文件夹的最小权限为 `700`；安装包名称已标准化。
  - 26.0.0 适配 GCC 12.x，并修复了 GCC 11.x 后期版本的 UT 编译失败问题。
- **命令行选项变更**：呼栈回溯的命令行选项名称已按行业惯例更名（原文未给出旧/新名字，仅声明"Changed the name ... to comply with industry conventions"）；同时新增 `--demangle`。

> 原文未涉及的项：未提供具体的环境变量名、未给出 CI 触发流程、未给出 API SDK 配置示例，此处不再补全。
