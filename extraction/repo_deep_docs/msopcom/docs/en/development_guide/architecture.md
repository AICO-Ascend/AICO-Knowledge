# MindStudio Ops Common Architecture Design

> 仓 `msopcom` · 路径 `docs/en/development_guide/architecture.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msopcom/docs/en/development_guide/architecture.md

# 深度解读：msopcom 架构设计文档

## 【定位】
本文档解决的是 MindStudio-Ops-Common（msopcom）基础组件仓库的**整体架构说明**问题：它定义了该组件的目录划分原则、csrc 子模块在三类使用方（被 hook 对象 / 通用插件 / 具体工具）中的角色分工、kernel_injection 与 host injection 的协作边界，以及新增一个 runtime 模块 stub 时所需遵循的代码框架与命名约束。

---

## 【技术要点】

1. **目录骨架**：仓库根目录 MindStudio-Ops-Common 下设 `.gitsubmodules`（依赖管理）、`build.py`（一键构建入口）、`csrc`（提供 CPU 侧接口 hook 能力）、`test`、`thirdparty`、`docs`、`README.md`。其中 `csrc` 内部进一步划分 `include`（被 hook 对象原始头文件）、`core`（通信 / 接口注册 / 接口绑定）、`runtime`（runtime 接口的 hook 函数与原始接口别名）、`bind`（接口绑定到具体工具）、`kernel_injection`（kernel 侧 hook，内容极简）。

2. **csrc 的三类使用场景与角色**：
   - 对被 hook 目标：提供 native 接口管理；
   - 对统一通用插件：提供注入（装饰）函数管理；
   - 对具体工具：提供统一 hook 接口管理 + 支持注入函数的通信控制；
   - 具体工具直接引用本仓库完成二进制编译，通过 **submodule** 能力支持各工具单独编译各自的注入。

3. **kernel_injection 范围限定**：
   - 仅针对**动态插桩**能力，静态插桩由各组件自身承担；
   - 目前仅支持 `bisheng-tune`，未来需支持 `msbit`；
   - 必须配合 csrc 中的 **kernel replacement** 能力并以其作为退出点；
   - 除特定插件外，后续插件能力先集成进 `mstracekit`；监控类插件进 `msprof`，检测类插件进 `mssanitizer`。

4. **新增 runtime 模块 stub 的代码框架**（以 coverage 工具添加 runtime 模块为例）：
   - `csrc/include`：被 hook 函数的头文件，最好一次性全部包含；
   - `csrc/xxx/xxxOrigin`：被 hook 接口的别名（任一工具实现即新增）；
   - `csrc/xxx/InjectionOfxxxx`：注入函数实现，无变化时仅改 `CMakeLists.txt` 引入；
   - `bind/Bindxxxx`：每次新增接口必须新增；
   - `csrc/xxx/CMakeLists.txt`：新增文件需加入对应目录。

5. **CMake 与命名约束**：
   - `CMakeLists.txt` **禁止通配符匹配**，必须精确匹配以支持增量编译；
   - 同一接口不同工具的实现差异显著时按工具类别**分目录隔离**，差异较小时用**宏隔离**；
   - 同名接口多工具实现时 `InjectionOfXXX` 命名应不同，建议末尾追加 `ForXXX`，使用**编译隔离**而非宏隔离（仅有一个 UT 进程），并建议在同一主分支上开发。

6. **Host injection 与 Kernel injection 的边界**：
   - Host 端：本仓库只提供完整二进制库，不同工具的 hook 需求通过**编译选项**区分；同一接口不同工具的注入差异在 `bind` 目录内关联；
   - Kernel 端：`include` 提供外部头文件接口；`msbit` 当前仅有 1 个文件生成控制信息故暂未建文件夹；`.so` 解析与新 kernel 生成能力暂放在 `customDBI` 类内，未来外部接口可在 `core` 实现；工具自身 hook 与 bind 调用在工具内实现，构建产出 `.so` 不放回基础组件；不同插件感知不同指令执行操作；集成模块负责解析处理 host 端结构；需与 host injection 协同，通过头文件被引入到 host 注入的装饰函数中。

---

## 【关键机制与数据】

- **Hook/Injection 三层协作机制**（原文未给出具体数值）：
  - 接口层（`include` + `xxxOrigin.h`）：定义并别名化被 hook 的原始接口；
  - 注入层（`InjectionOfxxxx`）：实现装饰函数；
  - 绑定层（`Bindxxxx`）：把装饰函数绑定到具体 runtime 接口（每个工具一份，如 `BindCoverage.cpp`）。

- **core 核心能力**：原文明确 core 承担**通信（控制、数据——数据流/文件，支持父子孙进程）、接口注册、接口绑定**三类核心功能。

- **构建方式**：具体工具直接引用本仓库完成二进制编译，并通过 submodule 支持各工具**单独编译各自的注入**。

- **Kernel 侧插件分发路线**：原文给出明确路径——
  - 监控类插件 → msprof
  - 检测类插件 → mssanitizer
  - 其余插件 → 先集成 mstracekit
  - 特定插件 → 集成到对应工具
  - 目前已支持：bisheng-tune；未来需支持：msbit

- **kernel replacement 退出点**：kernel_injection 必须配合 csrc 中 kernel replacement 能力并以其作为**退出点**（原文明确表述）。

---

## 【表格解读】

**原文无表格**

（文档主体为目录树代码块与要点列表，未出现任何参数表、对比表或配置表）

---

## 【公式解读】

**原文无公式**

（文档未包含任何 LaTeX 公式或伪代码公式片段）

---

## 【关联】

原文**未提供任何内部链接**（任务说明已标注"内部链接: (无)"）。但文档在文本中提及了以下外部/上下游模块，可视为隐含的关联关系：

- **submodule（`.gitsubmodules`）**：本仓库作为被引用方，为各具体工具提供二进制与编译隔离支持——属于**上游分发**关系。
- **`runtime` 目录下的接口**（如被覆盖/被检测的 runtime API）：是 hook 的**作用对象**——属于**下游使用**关系。
- **`mstracekit`**：作为后续插件能力的统一集成入口——属于**插件下游汇聚**关系。
- **`msprof`**（监控插件）、**`mssanitizer`**（检测插件）：分别承接不同类别 kernel 插件——属于**插件下游分发**关系。
- **`bisheng-tune`**（已支持）、**`msbit`**（待支持）：kernel 动态插桩的目标工具——属于**功能覆盖对象**关系。
- **`kernel replacement` 能力（位于 csrc 中）**：kernel_injection 的**协同依赖与退出点**——属于**紧耦合**关系。
- **`host injection`**（csrc runtime 层）：kernel_injection 通过头文件被引入到 host 注入的装饰函数中——属于**跨侧嵌入**关系。

---

## 【使用方法】

### 启用 / 集成方式

1. **作为二进制依赖被引用**（原文）：具体工具直接引用本仓库完成二进制编译，通过 submodule 支持单独编译注入。
2. **按工具区分编译**（原文）：不同工具的 hook 需求通过**编译选项**区分；同一接口不同工具的注入差异在 `bind` 文件夹内关联。
3. **kernel_injection 启用**（原文）：必须配合 csrc 中的 kernel replacement 能力并以其作为退出点；目前支持 bisheng-tune，未来支持 msbit；启用时通过 host 注入装饰函数中的头文件引入。

### 配置项 / 命令

- `build.py`：仓库一键构建脚本入口（原文给出路径）。
- `CMakeLists.txt`（位于 `csrc/xxx/`）：新增文件需加入对应目录；**禁止通配符**，须精确匹配以支持增量编译（原文明确约束）。

### 命名规范（新增接口时）

- 别名文件：`csrc/xxx/xxxOrigin`
- 注入实现：`csrc/xxx/InjectionOfxxxx`
- 绑定文件：`bind/Bindxxxx`（每次新增接口**必须**新增）
- 同名接口多工具实现：建议追加 `ForXXX` 后缀，使用编译隔离而非宏隔离（原文明确建议）。

### 测试

原文仅提及仓库根目录下存在 `test/` 目录用于测试用例维护，**未涉及**具体的运行命令、测试配置或使用流程。
