# MindStudio Sanitizer 版本说明

> 仓 `mssanitizer` · 路径 `docs/zh/release_notes/release_notes.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mssanitizer/docs/zh/release_notes/release_notes.md

# MindStudio Sanitizer (msSanitizer) 版本说明 深度解读

## 【定位】

本文档是华为昇腾 CANN 生态下 MindStudio Sanitizer 工具的版本发布说明 (release notes),系统描述了 msSanitizer **26.0.0 (内测版)** 与 **8.3.0 (正式版)** 两个版本的配套兼容性、特性新增/删除变更与 Bug 修复清单,核心围绕 AscendC 算子的内存越界检测、数据竞争检测、未初始化变量检测与同步指令配对检测四大能力展开。

## 【技术要点】

1. **版本配套基线**:26.0.0 适配 CANN 9.0.0+ (推荐) 并要求 Python 3.11+、json v3.12.0+、securec v1.1.16+、makeself release-2.5.0+、llvm-project 19.1.7;8.3.0 适配 CANN 8.2.RC1+,其余依赖一致。
2. **编译选项适配**:26.0.0 新增对毕昇编译器 `--cce-use-legacy-mixkernel-mangling` 编译选项的适配,并兼容 CANN 包芯片标识变更。
3. **检测能力扩展**:
   - **内存检测**:支持 AscendC 单目/双目计算类与搬运类 API 中 LocalTensor 越界检测,以及 SIMT 与 Main-Scalar 流水间的内存踩踏检测。
   - **竞争检测**:支持 SIMTR VF 内线程间竞争、新增 `SET_FLAG/WAIT_FLAG/SET_FLAGI/WAIT_FLAGI/HSET/HWAIT/GET_BUF/RLS_BUF` 等核内/核间同步指令插桩。
   - **冗余检测**:支持冗余 `SET_FLAG` 指令检测。
   - **寄存器状态**:支持检测开始时获取实时寄存器状态,程序结束时检查寄存器默认值。
4. **用户接口**:
   - 新增 `--demangle` 命令行选项,用于控制函数名显示格式。
   - kernel 侧 mstx 接口通过新增的 `sanitizer_report.h` 头文件对外开放。
   - mstx 内存池信息上报接口去除 region 与 heap 的绑定限制,支持 region 直接注册。
5. **构建与发布**:
   - 增加 debug 编译功能,支持 VSCode 断点调试。
   - root 用户安装时文件夹最小权限要求改为 700。
   - UT 编译默认启用 debug 编译模式,并适配 GCC 11.x / GCC 12.x,UT 依赖下载速度提升 10 倍。
   - 安装包名称统一整改,并新增打包 `sanitizer_report.h` 头文件。
6. **首批能力 (8.3.0)**:内存检测、竞争检测、未初始化检测、同步检测 (SetFlag/WaitFlag 配对) 四大类。

## 【关键机制与数据】

- **毕昇编译器适配机制 (原文)**:26.0.0 通过适配 `--cce-use-legacy-mixkernel-mangling` 编译选项,使工具能在新版编译器 mix kernel mangling 策略下正确还原符号与函数关系,避免因 mangling 变更导致插桩失败或符号解析错乱。
- **多指令插桩机制 (原文)**:对 `SET_FLAG/WAIT_FLAG/SET_FLAGI/WAIT_FLAGI/HSET/HWAIT/GET_BUF/RLS_BUF` 八条指令新增插桩与处理,目的是增强竞争检测对核内/核间同步语义的覆盖。
- **寄存器状态采样机制 (原文)**:检测启动时抓取实时寄存器快照,程序结束时校验默认值,用于识别运行过程中被异常修改的寄存器,辅助错误归因。
- **mstx 上报扩展机制 (原文)**:kernel 侧 mstx 通过 `sanitizer_report.h` 开放接口,新增对核间 barrier 和 set_flag/wait_flag 语义的上报能力;内存池上报接口解耦 region 与 heap。
- **性能数据 (原文)**:UT 依赖下载"速度提升 10 倍,彻底解决概率失败问题"——属构建链优化,未涉及检测运行时性能数字。
- **权限策略 (原文)**:root 用户安装时文件夹最小权限由原策略下调为 700,降低安装包在多用户系统上的越权访问风险。
- **编译器兼容 (原文)**:同时适配 GCC 11.x (UT 编译修复) 与 CANN 镜像 GCC 12.x 变更。
- **流水线竞争覆盖 (原文)**:新增对 SIMT 与 Main-Scalar 流水间的内存踩踏检测,并修复 `pipe-s` 与其他流水间的竞争漏报。

## 【表格解读】

### 表 1:产品版本信息

| 产品名称 | 产品版本 | 版本类型 |
|------|-------|------|
| msSanitizer | 26.0.0 | 内测版本 |
| msSanitizer | 8.3.0 | 正式版本 |

**逐行解读**:
- 第 1 行:msSanitizer 26.0.0 为**内测版本**,意味着新特性集中但稳定性尚未对外承诺,通常面向内部或受邀用户。
- 第 2 行:msSanitizer 8.3.0 为**正式版本**,代表对外可用、稳定交付的能力基线,与 26.0.0 共享同一检测能力框架,但所适配的 CANN 版本与编译器选项不同。

### 表 2:相关产品版本配套说明

| msSanitizer版本 | CANN版本 | Python版本 | json版本 | securec版本 | makeself版本 | llvm-project版本 |
|----------|-----------------|----------|----------|----------|----------|----------|
| 26.0.0 | 推荐9.0.0及以上 | 推荐 Python 3.11及以上 | v3.12.0及以上 | v1.1.16及以上 | release-2.5.0及以上 | 19.1.7 |
| 8.3.0 | 8.2.RC1及以上 | 推荐 Python 3.11及以上 | v3.12.0及以上 | v1.1.16及以上 | release-2.5.0及以上 | 19.1.7 |

**逐行解读**:
- 第 1 行 (26.0.0):CANN 推荐使用 9.0.0 及以上,Python 推荐 3.11 及以上,其余 json/securec/makeself/llvm-project 版本基线固定 (v3.12.0+ / v1.1.16+ / release-2.5.0+ / 19.1.7)。
- 第 2 行 (8.3.0):CANN 适配起点为 8.2.RC1,其余依赖基线与 26.0.0 完全一致——这意味着两个版本共享同一依赖栈,差异仅在于 CANN 主版本配套范围。
- 横向看:两个版本的 Python、json、securec、makeself、llvm-project 版本要求**完全相同**,区别只在 CANN 配套范围与编译器适配选项,体现了"同一工具双轨配套"的发布策略。

## 【公式解读】

原文无公式。

## 【关联】

文档以"msSanitizer 版本说明"为中心,围绕以下关联点展开 (原文未提供内部链接,基于文本中提到的实体归纳):

- **上游编译器**:毕昇编译器 (适配 `--cce-use-legacy-mixkernel-mangling`)。
- **运行平台**:昇腾 CANN 软件栈 (8.2.RC1+ 或 9.0.0+),并随 CANN 镜像 GCC 12.x 一同演进。
- **检测对象**:AscendC 算子 (含 SIMT 流水、Main-Scalar 流水、SIMTR VF、mix 算子),涉及 API 涵盖 LocalTensor 操作、`DataCopy`、单/双目计算类、搬运类 API。
- **关联工具**:VSCode (debug 断点调试目标)、mstx (kernel 侧运行时上报通道,通过 `sanitizer_report.h` 头文件对外开放)。
- **配套开源组件**:json (v3.12.0+)、securec (v1.1.16+)、makeself (release-2.5.0+)、llvm-project (19.1.7)。
- **特性闭环**:26.0.0 在 8.3.0 的"四大基础检测 (内存/竞争/未初始化/同步)"之上,扩展了 SIMTR VF 竞争、冗余 SET_FLAG 检测、寄存器状态采集、demangle 显示控制等增强能力,呈现"基线版 → 增强版"的演进关系。

## 【使用方法】

原文未提供完整的"启用方式 / 配置文件 / 命令清单",但提及以下可在使用中直接利用的命令/接口:

- **编译选项 (毕昇编译器)**:`--cce-use-legacy-mixkernel-mangling`(26.0.0 新增适配,用于控制 mix kernel 符号命名策略)。
- **命令行选项**:`--demangle`(26.0.0 新增,用于控制用户界面中函数名的 demangle 显示格式)。
- **运行时接口**:`sanitizer_report.h`(26.0.0 新增,作为 kernel 侧 mstx 的对外开放头文件,提供针对核间 barrier 与 set_flag/wait_flag 语义的上报接口,以及 region 直接注册的内存池上报接口)。
- **安装权限**:root 用户安装时,文件夹最小权限要求为 700 (26.0.0 调整)。
- **Debug 调试**:26.0.0 支持启用 debug 编译功能,可在 VSCode 中进行断点调试。
- **环境基线**:使用 26.0.0 时建议搭配 CANN 9.0.0+ 与 Python 3.11+;使用 8.3.0 时需 CANN 8.2.RC1+ 与 Python 3.11+。

> 注:具体的检测启动命令 (如 `mssanitizer` 调用方式)、配置文件路径、检测类别开关等,原文未涉及。
