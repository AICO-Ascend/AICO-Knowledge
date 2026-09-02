# MindStudio Ops Common 架构设计说明

> 仓 `msopcom` · 路径 `docs/zh/development_guide/architecture.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msopcom/docs/zh/development_guide/architecture.md

# MindStudio Ops Common 架构设计说明 — 深度解读

## 【定位】
本文档阐述「msopcom」(MindStudio Ops Common) 代码仓的目录设计思路、工具集成约束与 host/kernel 双链路劫持（injection）的协同方式，旨在为后续在该仓中新增插桩工具或扩展劫持能力提供统一规范。

---

## 【技术要点】

1. **目录分层设计**：采用 `csrc`（核心劫持源码）+ `runtime`（运行时劫持函数与原始接口别名）+ `bind`（接口与工具绑定）+ `kernel_injection`（kernel 侧动态插桩）+ `test` / `thirdparty` / `docs` 的分层；其中 `csrc/core` 承载通信（控制、数据-数据流/文件、父子孙进程）、接口注册与绑定三大核心功能。
2. **二进制分发与编译选项隔离**：仓内仅产出完整二进制库，不同工具的劫持诉求通过**编译选项**区分；同接口在不同工具的注入差异通过 `bind/Bindxxxx.cpp`（每个工具一个）进行关联。
3. **kernel_injection 边界**：仅承载**动态插桩能力**，静态插桩由各组件自身承载；当前支持 `bisheng-tune`，后续需支持 `msbit`；能力需与 `csrc` 的 kernel 替换能力配对，由其作为出口。
4. **插件归口策略**：通用插件优先集成到 `mstracekit`；特定插件按用途归口——监控插件到 `msprof`，检测插件到 `mssanitizer`。
5. **新增桩代码的五步流程**：`csrc/include`（头文件一次性放全）→ `csrc/xxx/xxxOrigin`（接口别名）→ `csrc/xxx/InjectionOfxxxx`（注入实现）→ `bind/Bindxxxx`（必须新增）→ `csrc/xxx/CMakeLists.txt`（新增文件登记）。
6. **同名接口差异化处理**：差异大 → 文件夹隔离；差异小 → 宏隔离；同名跨工具实现 → 命名末尾加 `ForXXX`，且不推荐宏隔离（"我们只有1个UT进程"），建议代码主干保持一致。

---

## 【关键机制与数据】

- **构建入口**：`build.py` 为一键式构建脚本入口；依赖通过 `.gitmodules` 的 submodule 管理，支持特定工具 injection 的单独编译（原文："提供submodule功能支持特定工具injection的单独编译"）。
- **进程通信层级**：`csrc/core` 支持**父子孙进程**三级通信，控制通道与数据通道分别承载，控制与数据-数据流/文件传输并列（原文："通信(控制，数据-数据流/文件，支持父子孙进程)"）。
- **劫持对象管理链路**：原生接口（`xxxOrigin.h` 提供别名）→ 注入函数（`InjectionOfxxx`）→ 绑定层（`BindCoverage.cpp` 等，按工具一文件）→ 工具自身 `.so`。
- **kernel_injection 与 host injection 协同方式**：kernel injection 通过**头文件方式**被引入到 host injection 的 decorated function 中，由集成模块负责 host 结构体的解析处理（原文："本身需要与host injection协同，自身通过头文件方式引入到host injection的decorated function中"）。
- **增量编译约束**：CMakeLists.txt 中**禁止全匹配**，必须写精确匹配以支持增量编译（原文："不能在CMakeLists.txt中全匹配，需要写精确匹配，从而支持增量编译"）。
- **性能/数值数据**：原文未提供任何性能数据或量化指标。

---

## 【表格解读】

**原文无表格**。

（原文仅以 `text` 代码块呈现目录树，不属于结构化表格。目录树已在【关键机制与数据】中按层级解读，此处不再重复。）

---

## 【公式解读】

**原文无公式**。

---

## 【关联】

本文档未提供任何内部超链接（"内部链接: (无)"），因此无 anchor 级别的关联可枚举。基于原文提及的外部模块/工具，可整理出如下上下游依赖与归属关系：

| 原文提及对象 | 角色定位 | 与本仓关系 |
|---|---|---|
| `bisheng-tune` | kernel 侧动态插桩，当前已支持 | kernel_injection 子模块承载 |
| `msbit` | kernel 侧动态插桩，**未来**需支持 | kernel_injection 子模块承载（待扩展） |
| `mstracekit` | 通用插件归口 | 非特定插件优先集成到此 |
| `msprof` | 监控类特定插件归口 | 监控插件集成到此 |
| `mssanitizer` | 检测类特定插件归口 | 检测插件集成到此 |
| 各工具仓（如 coverage、profile 等） | 通过 submodule 引用本仓二进制 | 不同工具劫持诉求由编译选项区分 |

> 注：以上关联均基于原文措辞（"现支持bisheng-tune，未来需要支持msbit"、"监控插件到msprof，检测插件到mssanitizer"等），未做臆测延伸。

---

## 【使用方法】

基于原文可直接抽取的启用方式/配置项如下：

1. **构建命令入口**：执行仓根目录下的 `build.py`（原文："`build.py` 一键式构建脚本入口"）。
2. **依赖管理**：通过 `.gitmodules` 拉取 submodule（原文："`.gitmodules` 管理依赖的submodule文件"）。
3. **CMake 编译隔离**：在 `csrc/xxx/CMakeLists.txt` 中新增文件时，必须使用**精确匹配**而非全匹配，以保留增量编译能力。
4. **同接口跨工具差异命名约定**：在 `InjectionOfxxx` 命名末尾追加 `ForXXX` 后缀以区分不同工具的实现（例如 `InjectionOfxxxForCoverage`）。
5. **工具特定劫持的注册位置**：新增接口时，**必须**在 `bind/` 下新增对应的 `Bindxxxx.cpp`，将 decorated function 与具体 runtime 接口绑定。

原文未涉及的具体配置项（如编译选项宏名、CMake 变量、submodule URL）未在文档中给出，故此处不列。
