# testngpp在2010.7~12月的改进 #

> 仓 `mockcpp` · 路径 `docs/UpdateHistory.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mockcpp/docs/UpdateHistory.md

# mockcpp `docs/UpdateHistory.md` 深度解读

## 【定位】

本篇文档是一份**轻量级C++单元测试框架 mockcpp（原 testngpp）在 2010 年 7 月至 12 月期间的变更日志（Changelog）**，记录了该时间段内框架新增的多框架支持、ApiHook 跨平台能力、调用约定支持、自动化构建与自动重置等改进，并附带了 Release 2.5（20110326）和 Release 2.6（20111002）两个版本节点，说明了版本演进脉络。

---

## 【技术要点】

1. **多 xUnit 框架兼容**：同时支持 `testngpp`、`gtest`、`CppUnit`、`CppUTest` 四种测试框架，让同一套 mock 桩机制可在不同测试体系下复用。
2. **约束关键字扩展**：
   - `spy`：窥探被 mock 函数实际接收到的入参。
   - `check`：以函数或仿函数（functor）自定义参数合法性校验规则。
3. **ApiHook 跨平台化**：
   - 修复 Windows 7 下原有 ApiHook 异常问题。
   - 将 ApiHook 由仅 Windows 扩展至 Linux，从而在 Linux 上**无需使用 `MOCKABLE` 宏**即可 mock C 函数。
   - 增加 64 位平台支持，测试覆盖 **Windows XP 64bit + VS2008** 与 **Linux + GCC**。
   - **限制项**：单用例中打桩函数不超过 **10 个**。
4. **调用约定扩展**：支持 VC **`stdcall`** 调用约定的函数 mock；该约定清栈方式与默认（`cdecl`）不同，VC 下 socket 操作函数均属此类。
5. **自动化构建脚本**：新增 `build.sh`、`build_install.sh`（Linux & cygwin）及其 Windows PowerShell 版本；前者用于编译并运行测试用例，后者用于编译并安装，详细用法参见代码根目录 `BuildGuide`。
6. **自动 reset 机制**：`verify` 之后**自动**执行 `reset`，全局函数 mock 与对象 mock 均适用，用户无需再手动调用 `reset`。

---

## 【关键机制与数据】

| 工作原理 / 数据流 | 原文标注 |
| --- | --- |
| 多框架适配通过统一的 mock 桩抽象层，将 testngpp/gtest/CppUnit/CppUTest 接入同一套 mock 接口 | 原文："支持多种的xUnit测试框架。（支持testngpp、gtest、CppUnit、CppUTest）" |
| `spy` 用于"窥探给某个被mock函数传入的入参"，是**只读观测**机制 | 原文："用于窥探给某个被mock函数传入的入参" |
| `check` 以"函数，或者仿函数对象"封装校验逻辑，可由用户自定义规则 | 原文："以函数，或者仿函数对象来自定义参数检查规则" |
| ApiHook 在 Windows 7 由异常转为正常 | 原文："原来的ApiHook功能在Win7上使用有异常" |
| Linux 上 ApiHook 使得 C 函数 mock **无需** `MOCKABLE` 宏 | 原文："在Linux下页可以不用MOCKABLE来进行C函数的mock" |
| 64 位平台 ApiHook 测试覆盖 **Windows XP 64bit + VS2008** 与 **Linux + GCC**；单用例 mock 函数数硬上限 **10 个** | 原文："增加限制：一个用例中打桩的函数不超过10个）……在Windows XP 64bit + VS2008和Linux + GCC 下测试通过" |
| `stdcall` 与默认约定在**清栈方式**上存在差异 | 原文："stdcall调用约定的函数，清栈的方式与默认不同。VC下socket操作函数都是stdcall" |
| `verify` 之后自动 `reset`，对**全局函数 mock 与对象 mock** 均生效 | 原文："无论是全局函数mock，还是对象mock，都支持这种方式，用户不用调用reset" |
| Windows 与 Linux 平台用例差异已被梳理，两端均能跑通所有用例 | 原文："[DEV](DEV.md) 梳理了Windows和Linux用例的差异，现在两种平台上都可以运行通过所有用例" |
| 版本数据：Release 2.5（20110326）；Release 2.6（20111002）；Release 2.6 的变更——减小库体积、修复 cppunit 编译错误、为 mockable 提供默认 mocker | 原文："20110326 Release 2.5" / "20111002 Release 2.6" / "reduce lib file size. fix compile error when compile for cppunit. add default mocker for mockable." |

---

## 【表格解读】

**原文无表格**。

（文档为 changelog 体裁，仅以编号列表与粗体标题罗列改进项，未包含参数表/性能对比/配置表等结构化表格。）

---

## 【公式解读】

**原文无公式**。

（文档为面向功能的描述性变更说明，未给出 LaTeX 或伪代码形式的数学/逻辑公式。）

---

## 【关联】

- **`DEV.md`**：原文唯一内部链接，由文末条目"梳理了 Windows 和 Linux 用例的差异，现在两种平台上都可以运行通过所有用例"引出。该文件承担跨平台兼容性说明与差异排查职责，与本篇 changelog 中第 4、5、6、7、10 条（Win7 修复、Linux ApiHook、64 位 ApiHook、stdcall、跨平台用例跑通）形成**强耦合**：changelog 仅披露现象与结论，**具体差异细节需跳转 DEV.md 查阅**。
- **`BuildGuide`**（代码根目录）：被第 8 条显式引用，用于说明 `build.sh` / `build_install.sh` 及其 Windows PowerShell 版本的详细用法；该文件**不在本仓库 markdown 链接列表中**（本篇末尾仅出现 `DEV.md`），属于代码仓内文件路径引用。
- **`mockable` 宏**：在第 5 条与 Release 2.6 变更中被两次提及——一是 Linux ApiHook 后**可省略**该宏对 C 函数进行 mock，二是 2.6 版本为 `mockable` 增加**默认 mocker**；它是 mockcpp 中**用于声明可被 hook/mock 的函数入口**的核心宏，与 `verify`、`reset` 共同构成 mock 三件套。
- **`testngpp` / `gtest` / `CppUnit` / `CppUTest`**：第 1 条所列四种下游测试框架，mockcpp 通过桩抽象层与之解耦。

---

## 【使用方法】

> 原文未涉及完整启用步骤，仅披露以下可操作线索：

1. **编译并运行测试**（Linux / cygwin）：
   ```bash
   ./build.sh
   ```
   Windows 等价物为 PowerShell 脚本版本。原文："build.sh用于编译和运行测试用例……Windows版本(PowerShell脚本)"。
2. **编译并安装**（Linux / cygwin）：
   ```bash
   ./build_install.sh
   ```
   详细用法参见代码根目录 `BuildGuide`。原文："build_install.sh用于编译并安装，详细用法参见代码根目录的BuildGuide"。
3. **mock 桩约束**：
   - 观测入参：使用 `spy` 关键字。
   - 自定义参数校验：使用 `check` 关键字，传入函数或仿函数对象。
4. **C 函数 mock（Linux）**：在 ApiHook 支持下，无需 `MOCKABLE` 宏即可直接打桩。
5. **自动清理**：调用 `verify` 后框架自动执行 `reset`，无需用户手动重置（全局函数 mock 与对象 mock 均适用）。
6. **64 位平台**：单个测试用例内打桩函数数量**不超过 10 个**——这是硬性约束，原文："增加限制：一个用例中打桩的函数不超过10个"。
7. **跨平台用例对齐**：Windows 与 Linux 两端的用例运行差异已被 `DEV.md` 梳理，两端均可跑通所有用例。
