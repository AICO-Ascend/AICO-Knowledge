# msDebug Quick Start

> 仓 `msdebug` · 路径 `docs/en/quick_start/msdebug_quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msdebug/docs/en/quick_start/msdebug_quick_start.md

# msDebug Quick Start 深度解读

---

## 【定位】

这篇文档面向 Ascend NPU 算子开发者,介绍 **msDebug 调试工具**的使用流程,使开发者能够在 NPU 上以断点方式调试算子内核代码,并支持读取 NPU 内存与寄存器、暂停/恢复程序运行状态。

---

## 【技术要点】

1. **依赖与前提**:前置依赖"Ascend Operator Development Toolchain Quick Start"中 2.1 与 2.3 节,环境按"Installation Guide"完成;Python 依赖验证覆盖 numpy/sympy/scipy/attrs/psutil/decorator,且 numpy 版本需 ≤ 1.26.4(原文命令:`assert version.parse(numpy.__version__) <= version.parse('1.26.4')`)。

2. **内核调试开关**:msDebug 工作前提是 `/proc/debug_switch` 被设置为 `1`;该开关默认关闭,仅 `root` 用户可写入;容器中常因 CoW / shadow files / overlay mount 隔离 `/proc` 而呈现"假阳性 1"。

3. **编译选项改造**:在算子内核 `op_kernel/CMakeLists.txt` 首行插入 `add_ops_compile_options(ALL OPTIONS -g -O0)`,即开启调试信息并关闭优化;随后通过 `bash ./build.sh` 重新编译,使用 `custom_opp_*.run` 包重新部署。

4. **调试器入口**:在 caller 工程构建产物目录下执行 `msdebug execute_add_op`,进入 `(msdebug)` 交互提示符。

5. **断点与执行**:使用 `b <file>:<line>` 设置断点(原文示例 `b add_custom.cpp:34`),`run` 启动程序直至命中;`var` 列出当前作用域全部局部变量,`register read -a` 读取全部寄存器。

6. **NPU 拓扑与任务查询**:`ascend info devices / cores / tasks` 分别查看设备、AI Core、任务维度的运行态信息,均支持在断点暂停状态下查询。

---

## 【关键机制与数据】

- **工作原理(原文)**:msDebug 通过内核调试开关 `/proc/debug_switch = 1` 激活对 NPU 内核的调试能力;若开关未生效,设置断点运行后会出现 `'A' packet returned an error: 8` 错误(原文引用)。

- **数据流(原文)**:在 `add_custom.cpp:34` 命中后,示例输出展示了 `KernelAdd::Init` 的栈帧与入参:实例指针 `this=0x00000000001d78a8`、输入/输出 GM 缓冲区地址 `x=0x12c0c0013000`、`y=0x000012c0c001c000`、`z=0x000012c0c0025000`,`totalLength=16384`,`tileNum=8`。

- **寄存器快照(原文)**:`register read -a` 示例显示 `PC = 0x12C04120088C`,`CTRL = 0x100000000003C`,以及 `GPR0=0x1D78A8`、`GPR1=0x1D7E28`、`GPR2=0x800`、`GPR3=0x0`、`GPR4=0x0`、`GPR5=0x8`,对应函数入口参数与运行上下文。

- **AI 拓扑(原文)**:示例设备 `Device 3` 具有 `Aic_Num=0, Aiv_Num=8, Aic_Mask=0x0, Aiv_Mask=0xf0000000000f`;`ascend info cores` 显示 8 个 aiv Core(CoreId 0-3、44-47)均停于 `breakpoint 1.1`,`PC=0x12c041200920`,分布在 Stream 47 的不同 Block 上。

- **容器陷阱(原文)**:即使容器内 `cat /proc/debug_switch` 显示 `1`,底层主机可能通过 CoW/shadow/overlay 等机制隔离 `/proc`,导致写操作不生效,断点不真正启用。

- **版本与依赖(原文)**:Python 依赖检查命令固定为 `python3 -c "import numpy, sympy, scipy, attrs, psutil, decorator; ..."`,输出 `All is OK` 才视为合规。

---

## 【表格解读】

### 表格 1 — 设备信息(`ascend info devices` 输出)

| Device | Aic_Num | Aiv_Num | Aic_Mask | Aiv_Mask |
|--------|---------|---------|----------|----------|
| * 3    | 0       | 8       | 0x0      | 0xf0000000000f |

**逐行解读**:
- 表头列出设备号与 AI CPU / AI Vector 单元数量及掩码。
- 当前聚焦设备为 `3`(`*` 标识),该设备没有 AI CPU(`Aic_Num=0`、`Aic_Mask=0x0`),仅有 8 个 Vector 单元,可用掩码 `0xf0000000000f` 表示按位启用。

### 表格 2 — AI Core 信息(`ascend info cores` 输出)

| CoreId | Type | Device | Stream | Task | Block | PC              | stop reason  | Filename | Line |
|--------|------|--------|--------|------|-------|-----------------|--------------|----------|------|
| * 0    | aiv  | 3      | 47     | 0    | 4     | 0x12c041200920  | breakpoint 1.1 | NA      | NA   |
| 1      | aiv  | 3      | 47     | 0    | 5     | 0x12c041200920  | breakpoint 1.1 | NA      | NA   |
| 2      | aiv  | 3      | 47     | 0    | 6     | 0x12c041200920  | breakpoint 1.1 | NA      | NA   |
| 3      | aiv  | 3      | 47     | 0    | 7     | 0x12c041200920  | breakpoint 1.1 | NA      | NA   |
| 44     | aiv  | 3      | 47     | 0    | 0     | 0x12c041200920  | breakpoint 1.1 | NA      | NA   |
| 45     | aiv  | 3      | 47     | 0    | 1     | 0x12c041200920  | breakpoint 1.1 | NA      | NA   |
| 46     | aiv  | 3      | 47     | 0    | 2     | 0x12c041200920  | breakpoint 1.1 | NA      | NA   |
| 47     | aiv  | 3      | 47     | 0    | 3     | 0x12c041200920  | breakpoint 1.1 | NA      | NA   |

**逐行解读**:
- 表头枚举 Core 标识、类型、所在设备、Stream、Task、Block、当前 PC、停机原因及源码定位列。
- 8 个 aiv 核(`*` 标识 CoreId 0 表示当前焦点)共享同一个 Stream 47、Task 0,Block 编号覆盖 0-7;所有核的 `PC` 一致(命中同一断点),停机原因均为 `breakpoint 1.1`,源码定位未填充(`NA`)说明内核符号对源码行的反向映射在该视图暂不可用。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **前置工具链指南**:`Ascend Operator Development Toolchain Quick Start`(gitcode 链接)——本文档要求先完成该指南的 §2.1(项目准备)与 §2.3(算子构建/部署),并基于其中的 `AddCustom` 加法算子示例进行调试。
- **环境安装文档**:`Ascend AI Operator Development Toolchain Learning Environment Installation Guide`(gitcode 链接)——提供 msDebug 运行所需的依赖安装与工作区初始化步骤,文中强调"即便已有类似环境也应重做一遍以保证组件一致"。
- **依赖算子工程**:示例算子 `AddCustom`(位于 `~/ot_demo/workspace/src/AddCustom`)、构建产物 caller 二进制 `execute_add_op`,由 `build.sh` 与 `custom_opp_*.run` 部署包串联。
- **运行依赖**:依赖上一节的 Python 包检查结果作为运行环境前置校验;`/proc/debug_switch` 开关为整个 msDebug 能力链路的开关节点。

---

## 【使用方法】

- **环境前置校验**:执行 `python3 -c "import numpy, sympy, scipy, attrs, psutil, decorator; from packaging import version; assert version.parse(numpy.__version__) <= version.parse('1.26.4'); print('All is OK')"`;期望输出 `All is OK`。

- **启用内核调试开关**:
  ```
  cat /proc/debug_switch
  echo 1 > /proc/debug_switch
  ```
  需以 `root` 执行,目标值 `1`;若写入失败则 msDebug 不可用,建议跳过本节。

- **改造编译选项并重部署算子**:
  ```
  cd ~/ot_demo/workspace/src/AddCustom
  \cp -f op_kernel/CMakeLists.txt op_kernel/CMakeLists.txt.orig.bak
  sed -i "1i\\add_ops_compile_options(ALL OPTIONS -g -O0)" op_kernel/CMakeLists.txt
  bash ./build.sh
  MY_OP_PKG=$(find ./build_out -maxdepth 1 -name "custom_opp_*.run" | head -1) && bash $MY_OP_PKG
  ```

- **启动调试器**:
  ```
  cd ~/ot_demo/workspace/src/caller/build
  msdebug execute_add_op
  ```

- **断点设置与运行**:
  ```
  b add_custom.cpp:34
  run
  ```
  命中后 msDebug 切换到对应 Kernel(`CoreId 1, Type aiv`)并打印停机栈帧。

- **查看变量与寄存器**:
  ```
  var
  register read -a
  ```

- **查询设备/核/任务信息**:
  ```
  ascend info devices
  ascend info cores
  ascend info tasks
  ```

- **容器环境注意(原文 CAUTION)**:若在云厂商容器中遇到 `'A' packet returned an error: 8`,说明主机层面 `/proc/debug_switch` 未真正启用,需在具备主机 `root` 的环境中复现,或放弃本次动手体验。
