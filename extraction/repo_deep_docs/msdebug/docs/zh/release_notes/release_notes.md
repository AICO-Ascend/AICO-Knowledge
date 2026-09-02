# MindStudio Debugger 版本说明

> 仓 `msdebug` · 路径 `docs/zh/release_notes/release_notes.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msdebug/docs/zh/release_notes/release_notes.md

# 「msdebug」release_notes.md 一体化深度解读

---

## 【定位】

本文档是 **MindStudio Debugger (msDebug)** 的版本变更说明,记录 26.0.0（内测）与 8.3.0（正式）两个版本的功能新增、删除、Bugfix 以及配套依赖版本与构建发布侧改动。

---

## 【技术要点】

1. **上板调试能力扩展**：26.0.0 新增「不设置 kernel object 路径即可上板调试」、支持 asc 编译算子的 coredump 与上板调试,以及从 host 传入 kernel 的结构体变量打印。
2. **调试信息读取增强**：读内存支持跳过元素个数展示;`var` 命令针对 gm 等 `uint8_t *` 类型变量的乱码显示被优化;`shared_memory` 算子场景与 mix 算子场景的调试/回显均被纳入支持。
3. **Coredump 解析增强**：26.0.0 在 coredump 解析功能中增加「非 inline 编译下的调用栈回溯」能力(8.3.0 仅支持调用栈、寄存器、变量展示)。
4. **构建与发布约束变更**：
   - root 用户安装时目录最小权限由默认收紧至 **700**;
   - 安装包名称统一整改;
   - 修复 UT 编译在 **GCC 7 / GCC 12** 上不通过问题;
   - 修复编译时找错 `libtinfo` 动态库路径的问题;
   - 新增交付件 `libform.so.5` 以满足部分环境的构建依赖;
   - 新增 **Unix Makefiles** 构建方式支持。
5. **基础调试面（8.3.0 基线）**：上板调试覆盖断点展示、变量/寄存器/内存打印、代码行级单步、核信息展示与切换、调用栈展示;coredump 文件解析覆盖调用栈、寄存器、变量三项。
6. **依赖配套**：26.0.0 与 8.3.0 均要求 `makeself >= release-2.5.0`;`libedit` 与 `ncurses` 与 `openEuler-24.03-LTS-SP1-release` 保持对齐(26.0.0 中 `libedit` 显式声明为 `openEuler-24.03-LTS-SP1-release`,`ncurses` 版本为 `6.6`;8.3.0 中两者均沿用同一 openEuler 发布版本)。

---

## 【关键机制与数据】

> 原文为版本说明文档,不含性能/数据流类条目,所有可提取的机制均以「新增/修复/约束」形式呈现,无量化性能数据。

- **原文**:上板调试运行时,新增允许省略 kernel object 路径的前置配置环节;同时仍保留原有 kernel object 指定路径的方式。
- **原文**:coredump 解析器在 26.0.0 中新增对 **非 inline 编译产物** 的调用栈回溯能力,即用户使用非 inline 编译选项生成的二进制在 coredump 后仍可还原调用栈。
- **原文**:读内存命令在 26.0.0 中扩展为支持「跳过元素个数展示结果」(即不再强约束每次都打印元素计数)。
- **原文**:构建侧引入 **Unix Makefiles** 构建方式,并对 root 安装场景收紧目录最小权限为 700。
- **原文**:文档本身在 26.0.0 进行了「全面优化重构,提升易用性」,但未细化指标。

---

## 【表格解读】

### 表 1:产品版本信息

| 产品名称 | 产品版本  | 版本类型 |
|------|-------|------|
| msDebug | 26.0.0 | 内测版本 |
| msDebug | 8.3.0 | 正式版本 |

- **行 1**:`msDebug 26.0.0` 标注为「内测版本」,提示该版本处于内部验证阶段,可能不稳定,仅供内测使用。
- **行 2**:`msDebug 8.3.0` 为「正式版本」,表明其可作为对外稳定基线使用,与 26.0.0 形成「内测先行 / 正式兜底」的双轨版本策略。

### 表 2:相关产品版本配套说明

| msDebug | makeself | libedit | ncurses |
|----------|-----------------|----------|-------|
| 26.0.0 | release-2.5.0及以上 | openEuler-24.03-LTS-SP1-release | 6.6 |
| 8.3.0 | release-2.5.0及以上 | openEuler-24.03-LTS-SP1-release | openEuler-24.03-LTS-SP1-release |

- **行 1（26.0.0）**:`makeself` 要求 ≥ `release-2.5.0`;`libedit` 锁定到 `openEuler-24.03-LTS-SP1-release`;`ncurses` 采用独立版本号 `6.6`(与 openEuler 发布版本解耦)。
- **行 2（8.3.0）**:三项依赖均与 openEuler-24.03-LTS-SP1-release 对齐,`libedit` 与 `ncurses` 同源(均来自该 openEuler release),`makeself` 仍为 `release-2.5.0 及以上`。
- **对比解读**:两版本对 `makeself` 的下限要求一致;但在 26.0.0 中 `ncurses` 显式锁为 `6.6`,而 8.3.0 中 `ncurses` 仍跟随 openEuler 发布版本——表明 26.0.0 对 `ncurses` 的版本基线做了更精确的固定,提升了构建可复现性。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **关联文档**:同目录或同仓库内未给出内部链接,根据上下文可推断本文档属于 msDebug 整体发布说明的一部分,与 msDebug 自身的安装/调试使用文档、openEuler-24.03-LTS-SP1 操作系统发行版、以及 `makeself`、`libedit`、`ncurses`、`libtinfo`、`libform.so.5` 等底层依赖存在配套关系。
- **关联特性(同版本内)**:
  - 「上板调试」与「coredump 解析」构成 msDebug 的两大调试面,26.0.0 同时增强了二者(上板调试新增 kernel object 路径可选、shared_memory、asc 算子调试;coredump 新增非 inline 调用栈回溯)。
  - 「`var` 命令 gm 乱码优化」与「读内存跳过元素个数」属于「读变量/读内存」相关命令族的体验改进。
  - 「UT 编译在 GCC7/12 上不通过修复」与「`libtinfo` 路径找错」「`libform.so.5` 交付」「Unix Makefiles 构建」「安装包名称统一」共同构成 26.0.0 的构建发布侧闭环改动。
- **上下游依赖**:
  - 下游使用方受 `makeself`、`libedit`、`ncurses` 版本约束;
  - 上游依赖 openEuler-24.03-LTS-SP1-release 对 `libedit` / `ncurses` 的发布内容。
- **本任务提供**的内部链接列表为:(无),因此无法进一步引申到其他 markdown 文档。

---

## 【使用方法】

原文未涉及具体启用方式、配置项或命令行调用语法;仅描述了功能点的「存在与否」。如下游用户需要具体使用步骤,需参考 msDebug 的用户手册或调试命令文档(本文档未提供链接)。
