# msDebug算子调试工具快速入门

> 仓 `msdebug` · 路径 `docs/zh/quick_start/msdebug_quick_start.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msdebug/docs/zh/quick_start/msdebug_quick_start.md

# msDebug 算子调试工具快速入门 — 深度解读

## 【定位】

这篇文档是面向昇腾 NPU 算子开发人员的 msDebug 调试工具的"零起步实操指南"，它基于入门教程中开发的简易加法算子（AddCustom），演示如何在内核调试开关、编译选项、调试器交互三步流程下，对运行在 NPU 上的算子内核进行断点暂停、内存/寄存器查看与设备/任务信息查询，以快速定位算子功能异常。

---

## 【技术要点】

1. **环境强依赖**：仅支持标准化 CANN 容器环境，自检脚本需检测 `/.dockerenv`、`$ASCEND_HOME_PATH`、`$ATB_HOME_PATH` 与 `~/ot_demo/msot/example/quick_start` 四个标识；环境安装预计耗时约 3 分钟。

2. **内核调试开关**：依赖 `/proc/debug_switch` 写为 `1` 才可正常工作，默认关闭且需 root 权限；若容器内虽能写为 1 但实际未生效（CoW/影子文件/overlay mount 隔离），后续 `run` 会报 `'A' packet returned an error: 8` 错误，整节 msDebug 实操需跳过。

3. **编译选项变更**：在 `op_kernel/CMakeLists.txt` 首行插入调试配置（`add_ops_compile_options(ALL OPTIONS -g -O0)` 或 `npu_op_kernel_options(ascendc_kernels ALL OPTIONS -g -O0)`），使用 `-g` 启用调试信息、`-O0` 禁用优化；调试结束后用备份文件 `.bak` 恢复。

4. **断点机制**：调试器启动命令为 `msdebug execute_add_op`（在 `caller/build` 目录）；断点命令为 `b add_custom.cpp:34`，命中后框架栈显示 `KernelAdd::Init(this=0x00000000001d78a8, x=0x12c0c0013000, y=0x12c0c001c000, z=0x12c0c0025000, totalLength=16384, tileNum=8)`。

5. **多维度变量/寄存器/拓扑查询**：提供 `var`（局部变量）、`register read -a`（含 PC、COND、CTRL、GPR0~GPR5）、`ascend info devices/cores/tasks/stream/blocks` 五类信息查询命令，输出均为结构化列表。

6. **退出流程**：使用 `q` 加 `y`（确认）退出调试器，避免残留状态。

---

## 【关键机制与数据】

**工作原理（原文表述的流程）**：

- **原文**：msDebug 通过内核调试开关 `/proc/debug_switch` 启用 → 配合编译器生成 `-g -O0` 的含调试信息、未优化二进制 → 调用 `msdebug` 启动调试器 → 通过 GDB 协议 (`'A' packet returned an error: 8` 即指该协议错误) 与 NPU 内核通信 → 在断点处冻结 AI Core 上 aiv 类型核 → 允许开发者读取 GM 指针、变量、寄存器与设备/任务元信息。

**关键运行时参数示例（原文给出的具体值）**：

| 数据项 | 原文示例值 | 含义 |
|---|---|---|
| `totalLength` | `16384` | 加法算子总元素数 |
| `tileNum` | `8` | 分块数 |
| `BUFFER_NUM` | 原文未明示数值 | 出现在计算 `tileLength = blockLength / tileNum / BUFFER_NUM` 中 |
| `GetBlockIdx()` | 原文未给出具体值 | 决定各核 GM 偏移 |
| GM 指针 `x/y/z` | `0x12c0c0013000 / 0x12c0c001c000 / 0x12c0c0025000` | 全局内存首地址 |
| PC 寄存器 | `0x12C04120088C` / `0x12c041200920` | 命中后程序计数器 |
| Device ID | `3` | 实测设备号 |
| Stream | `47` | 当前算子所在流 |
| Block 数 | `0~7`（共 8 个） | 任务占用的 block 列表 |
| CoreId 列表 | `0,1,2,3,44,45,46,47` | 8 个 aiv 核 |

**性能数据**：原文未提供 msDebug 的性能开销、吞吐量、断点命中延迟等数据。

---

## 【表格解读】

> 说明：原文无独立的"参数表/性能对比表"，但 `ascend info` 系列命令的输出本身为结构化表格形式，下面对其**逐字还原**并逐行解读。

### 表 1：`ascend info devices` 输出（设备信息）

| Device | Aic_Num | Aiv_Num | Aic_Mask | Aiv_Mask |
|---|---|---|---|---|
| * 3 | 0 | 8 | 0x0 | 0xf0000000000f |

**逐行解读**：
- `Device = 3`：当前调试聚焦的设备编号为 3，星号 `*` 表示这是调试器当前附着的活动设备。
- `Aic_Num = 0`：该设备中 AIC（Cube 计算核）的数量为 0，表示当前 Demo 不使用 AIC。
- `Aiv_Num = 8`：AIV（Vector 核）共 8 个，对应示例算子恰好占用 8 个 Vector 核处理 8 个分块。
- `Aic_Mask = 0x0`：AIC 核掩码为 0，确认无 AIC 参与。
- `Aiv_Mask = 0xf0000000000f`：AIV 核位掩码，低 4 位为 `0xf`（核 0~3）+ 高位 `0xf0000000000`（核 44~47），恰好对应下面 `cores` 表中实际命中断点的 8 个 aiv 核。

### 表 2：`ascend info cores` 输出（核信息）

| CoreId | Type | Device | Stream | Task | Block | PC | stop reason | Filename | Line |
|---|---|---|---|---|---|---|---|---|---|
| * 0 | aiv | 3 | 47 | 0 | 4 | 0x12c041200920 | breakpoint 1.1 | NA | NA |
| 1 | aiv | 3 | 47 | 0 | 5 | 0x12c041200920 | breakpoint 1.1 | NA | NA |
| 2 | aiv | 3 | 47 | 0 | 6 | 0x12c041200920 | breakpoint 1.1 | NA | NA |
| 3 | aiv | 3 | 47 | 0 | 7 | 0x12c041200920 | breakpoint 1.1 | NA | NA |
| 44 | aiv | 3 | 47 | 0 | 0 | 0x12c041200920 | breakpoint 1.1 | NA | NA |
| 45 | aiv | 3 | 47 | 0 | 1 | 0x12c041200920 | breakpoint 1.1 | NA | NA |
| 46 | aiv | 3 | 47 | 0 | 2 | 0x12c041200920 | breakpoint 1.1 | NA | NA |
| 47 | aiv | 3 | 47 | 0 | 3 | 0x12c041200920 | breakpoint 1.1 | NA | NA |

**逐行解读**：
- 星号 `*` 仅标记 `CoreId=0` 为当前调试器聚焦核；其他 7 核为同一断点命中但未聚焦状态。
- 所有 8 核 `Type=aiv`、`Device=3`、`Stream=47`、`Task=0`，与 `tasks`/`stream` 表一致，表明它们是同一任务的并行执行单元。
- `Block` 列 `4,5,6,7,0,1,2,3` 体现了 8 个核的 block 编号分配（并非 0~7 连续，可能是物理 block 排布），与 `blocks` 表一一对应。
- `PC = 0x12c041200920` 为断点命中后的程序计数器地址。
- `Filename = NA`、`Line = NA`：因为编译选项仅本地生效，断点符号位置在远端核视图显示为 NA，需开发者结合 `add_custom.cpp:34` 的源代码对应理解。

### 表 3：`ascend info tasks` 输出（任务信息）

| Device | Stream | Task | Invocation |
|---|---|---|---|
| * 3 | 47 | 0 | AddCustom_ab1b6750d7f510985325b603cb06dc8b_0 |

**逐行解读**：
- `Invocation` 字段 `AddCustom_ab1b6750d7f510985325b603cb06dc8b_0` 是算子内核二进制对象的唯一标识（哈希值 `ab1b6750d7f510985325b603cb06dc8b` + 序号 `0`），与断点命中栈顶 `AddCustom_ab1b6750d7f510985325b603cb06dc8b.o` 保持一致，证明内核模块已正确加载。

### 表 4：`ascend info stream` 输出（流信息）

| Device | Stream | Type |
|---|---|---|
| * 3 | 47 | aiv |

**逐行解读**：`Type=aiv` 表明当前 Stream 47 是 AIV 类型流，符合加法算子属于 Vector 计算的定位；与 `cores` 表中 `Type=aiv` 严格匹配。

### 表 5：`ascend info blocks` 输出（块信息）

| Device | Stream | Task | Block |
|---|---|---|---|
| * 3 | 47 | 0 | 4 |
| 3 | 47 | 0 | 5 |
| 3 | 47 | 0 | 6 |
| 3 | 47 | 0 | 7 |
| 3 | 47 | 0 | 0 |
| 3 | 47 | 0 | 1 |
| 3 | 47 | 0 | 2 |
| 3 | 47 | 0 | 3 |

**逐行解读**：仅展示 Block 维度的占用视图，与 `cores` 表中 block 列完全对应，星号 `*` 仍标记当前聚焦 Block=4。Block 编号 `4,5,6,7,0,1,2,3` 与 `CoreId` `0,1,2,3,44,45,46,47` 一一映射，揭示了"CoreId-Block"在该设备上的绑定关系。

---

## 【公式解读】

> 原文无 LaTeX 公式或伪代码公式。文档中出现的数学/逻辑表达式仅为源码注释中的赋值计算，如 `this->tileLength = this->blockLength / tileNum / BUFFER_NUM;`，这是算子开发中的常见分块公式，但文档未将其作为独立公式列出含义说明，故不强行解读为"公式"。

---

## 【关联】

文档虽在文末标注"内部链接: (无)"，但**正文**中实际嵌入了两个对其他文档的强引用，构成上下游关系：

1. **上游依赖 —《算子开发工具链快速入门》**：
   - 链接：`op_tool_quick_start.md`（gitcode.com/Ascend/msot）
   - 引用点 ①：开篇将"已完成该指南的全流程操作"作为本教程的前提。
   - 引用点 ②：在 2.2 节明确要求"按照 2.3 节操作完成算子工程准备"，即复用该指南的 `msopgen` 工程创建流程来生成 AddCustom 算子工程。
   - **关系定位**：本文是 msot 算子开发工具链流水线的"调试阶段"指南，前置流程由该上游文档提供。

2. **横向依赖 —《昇腾 AI 算子开发工具链学习环境安装指南》**：
   - 链接：`installation_guide.md`（gitcode.com/Ascend/msot）
   - 引用点：在 2.1.1 节强制要求按该指南完成 CANN 容器安装（标准容器是本工具的唯一支持环境）。
   - **关系定位**：环境基座，msDebug、msot 工具链均依赖同一套预装容器镜像。

3. **代码仓样本关联**：
   - 示例代码仓根路径 `~/ot_demo/msot/example/quick_start`（自检脚本第 2 项）。
   - 算子工程路径 `~/ot_demo/workspace/src/AddCustom`。
   - 调试可执行文件路径 `~/ot_demo/workspace/src/caller/build/execute_add_op`。
   - 这三个路径是 msot 工具链标准工程结构，意味着 msDebug 与 msot 的 `msopgen`、`build.sh`、`custom_opp_*.run` 打包脚本是同源协同的——只有经过 msot 流程编译出的 `*.run` 包并部署后，msDebug 才能正确符号化内核二进制。

---

## 【使用方法】

### 启用方式

1. **环境自检（必须通过）**：
   ```bash
   [ -f /.dockerenv ] && [ -n "$ASCEND_HOME_PATH" ] && [ -n "$ATB_HOME_PATH" ] && echo -e "\033[32m[PASS] CANN 容器环境 OK \033[0m" || echo -e "\033[31m[FAIL] 非标容器或未进入容器！\033[0m"
   [ -d ~/ot_demo/msot/example/quick_start ] && echo -e "\033[32m[PASS] 示例代码仓 OK\033[0m" || echo -e "\033[31m[FAIL] 代码仓缺失\033[0m"
   ```

2. **开启内核调试开关（需 root）**：
   ```bash
   cat /proc/debug_switch
   echo 1 > /proc/debug_switch
   ```

3. **修改编译选项插入（置于 `op_kernel/CMakeLists.txt` 首行）**：
   ```cmake
   if(COMMAND add_ops_compile_options)
     add_ops_compile_options(ALL OPTIONS -g -O0)
   elseif(COMMAND npu_op_kernel_options)
     npu_op_kernel_options(ascendc_kernels ALL OPTIONS -g -O0)
   endif()
   ```

### 配置项与命令清单

| 类别 | 命令/配置 | 用途 |
|---|---|---|
| 编译 | `-g -O0` | 启用调试信息、禁用优化 |
| 编译/部署 | `bash ./build.sh` + `bash custom_opp_*.run` | 重新编译并部署算子包 |
| 调试器启动 | `msdebug execute_add_op` | 进入 msDebug 交互界面 |
| 断点 | `b add_custom.cpp:34` | 在指定行设置断点 |
| 运行 | `run` | 启动程序并等待命中断点 |
| 变量查看 | `var` | 显示当前作用域所有局部变量 |
| 寄存器 | `register read -a` | 读取全部寄存器（含 PC、COND、CTRL、GPR0~GPR5） |
| 设备信息 | `ascend info devices` | 查看 Device、AIC/AIV 数量及掩码 |
| 核信息 | `ascend info cores` | 查看各 Core 的 CoreId、Type、Device、Stream、Task、Block、PC、断点原因 |
| 任务信息 | `ascend info tasks` | 查看算子 Invocation 名称（如 `AddCustom_ab1b6750d7f510985325b603cb06dc8b_0`） |
| 流信息 | `ascend info stream` | 查看 Stream 类型（aiv/aic） |
| 块信息 | `ascend info blocks` | 查看占用 Block 列表 |
| 退出 | `q` + `y` | 退出调试器 |
| 恢复 | `\cp -f op_kernel/CMakeLists.txt.bak op_kernel/CMakeLists.txt` | 调试完成后恢复原始 CMakeLists |

### 启用条件小结（原文未涉及的，本文亦不补充）

原文未涉及 `msDebug` 的远程调试 attach、多进程 attach、attach 到已运行进程、自定义断点条件、watchpoint 等高级用法；亦未提供配置文件（如 `.msdebugrc`）的说明。
