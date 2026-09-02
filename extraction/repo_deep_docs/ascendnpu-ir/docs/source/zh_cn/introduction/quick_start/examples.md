# 编译与执行示例

> 仓 `ascendnpu-ir` · 路径 `docs/source/zh_cn/introduction/quick_start/examples.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/ascendnpu-ir/docs/source/zh_cn/introduction/quick_start/examples.md

# 一体化深度解读：编译与执行示例

## 【定位】
这篇文档解决「AscendNPU-IR 端到端落地」的问题——以一段 `VecAdd` MLIR 为例，展示如何用 `bishengir-compile` 将 MLIR 编译为可在昇腾 NPU 上执行的算子二进制 `kernel.o`，并基于 CANN runtime（C++ ACL/RT 接口）完成二进制注册、Host↔Device 数据搬运、内核下发与结果回收的全流程。

---

## 【技术要点】

1. **IR 编译入口**：`bishengir-compile add.mlir -enable-hivm-compile -o kernel.o`，`-enable-hivm-compile` 启用 HiVector 向量化后端编译通道，产物为 `kernel.o`（设备端可执行算子对象）。
2. **MLIR 形态**：示例使用 `func.func` 包裹算子，函数属性 `hacc.entry` + `hacc.function_kind = #hacc.function_kind<DEVICE>` 标记为设备侧入口函数；算子主体由 `memref.alloc`、`hivm.hir.load`、`hivm.hir.vadd`、`hivm.hir.store` 组成。
3. **地址空间区分**：输入/输出位于 `#hivm.address_space<gm>`（Global Memory，全局内存），中间缓冲位于 `#hivm.address_space<ub>`（Unified Buffer，统一缓冲区），通过 `memref.alloc()` 在 UB 上分配算子工作区。
4. **数据类型与规模**：`memref<16xi16>`——`int16`，长度 16，是整篇示例的张量形状基线。
5. **Runtime 注册二元组**：
   - `rtDevBinaryRegister(&binary, &binHandle)`，其中 `binary.magic = RT_DEV_BINARY_MAGIC_ELF_AIVEC`、`binary.version = 0`，将 ELF 形式的 AI Vector 内核二进制注册到 runtime；
   - `rtFunctionRegister(binHandle, stubFunc, kernelName, kernelName, 0)`，把符号名 `"add"`（`stubFunc` 与 `kernelName` 同名）绑定到二进制句柄。
6. **数据搬运与下发**：`aclrtMalloc`（按 `ACL_MEM_MALLOC_HUGE_FIRST` 策略优先大页）→ `aclrtMemcpy(..., ACL_MEMCPY_HOST_TO_DEVICE)` → `rtKernelLaunch(stubFunc, 1, &args, sizeof(args), nullptr, stream)` → `aclrtSynchronizeStream(stream)` → `aclrtMemcpy(..., ACL_MEMCPY_DEVICE_TO_HOST)`，最后由 `aclrtMallocHost` 申请可被 runtime 直读的分页内存用于回拷。
7. **样例数值**：输入 0 = `[0, 1, 2, …, 15]`，输入 1 = 全 1（共 16 个），期望输出 = `[1, 2, 3, …, 16]`（即逐元素加 1）。

---

## 【关键机制与数据】

- **原文**：算子形状固定为 `memref<16xi16>`，3 个参数（2 入 1 出）均为该形状的 `gm` 张量，中间通过 `memref.alloc()` 在 `ub` 上各分配 3 块 16×i16 的临时缓冲。
- **原文**：HIVM HIR 算子组合严格遵循「Load → Compute → Store」三段式——`hivm.hir.load` 把 GM 拷到 UB，`hivm.hir.vadd` 在 UB 上做向量加，`hivm.hir.store` 把 UB 写回 GM。
- **原文**：Host 端 ABI 调用约定，`args` 为 `void *` 数组，分别填入 `input0Device`、`input1Device`、`outputDevice`，`rtKernelLaunch` 第二个参数 `1` 表示启动 1 个 block。
- **原文**：ACL 初始化路径 `aclInit(nullptr) → aclrtSetDevice(0) → aclrtCreateStream(&stream)`；收尾路径 `aclrtDestroyStream → aclrtResetDevice(0) → aclFinalize()`。
- **原文**：内存分配标志 `ACL_MEM_MALLOC_HUGE_FIRST`——优先申请大页内存；Host 端接收缓冲区通过 `aclrtMallocHost` 分配，对应释放接口为 `aclrtFreeHost`。
- **原文**：构建期环境变量为 `${ASCEND_HOME_PATH}`，对应包含路径 `${ASCEND_HOME_PATH}/include`、`${ASCEND_HOME_PATH}/include/experiment/msprof`、`${ASCEND_HOME_PATH}/pkg_inc`，链接路径 `${ASCEND_HOME_PATH}/lib64`，链接库 `-l runtime -l ascendcl`；`set_env.sh` 默认位置 `/usr/local/Ascend/ascend-toolkit/set_env.sh`（实际路径以安装为准）。
- **原文**：文档未给出性能数据（无 cycles / throughput / latency 等指标）。

---

## 【表格解读】

**原文无表格**。示例中的 `expectedValue` / `input0Value` / `input1Value` 是三段并列的 C++ 数组初始化列表，并非结构化对比表，故不进行表格还原。

---

## 【公式解读】

**原文无公式**。算子语义为「逐元素向量加」，但文中未以 LaTeX 或伪代码形式给出 `result[i] = lhs[i] + rhs[i]` 的显式表达，仅通过 MLIR 的 `hivm.hir.vadd` 操作名隐含。

---

## 【关联】

- **前置依赖（链接）**：[`installing_guide.md`](installing_guide.md)：文档在前置条件中明确「已完成[构建安装](installing_guide.md)，且 `bishengir-compile` 已加入 `PATH`」；同时在 `g++` 编译命令注释中再次指回「快速开始-安装与构建」一节。该链接是本文唯一的内部交叉引用，构成「先安装→再编译→再上板」的链式依赖。
- **下游工具链（涉及但未链内引用）**：
  - `bishengir-compile`：编译器驱动，本文档是它面向用户的最小可运行样例。
  - CANN ACL/RT C API（`acl/acl.h`、`runtime/runtime/rt.h`、`acl/error_codes/rt_error_codes.h`）：来自昇腾 CANN 软件栈，是上板执行的宿主侧接口来源。
- **上游/平行特性（涉及但未链内引用）**：
  - `hivm` 方言：`address_space<gm>` / `address_space<ub>`、`hir.load` / `hir.vadd` / `hir.store`，属 HiVector 设备侧 HIR；
  - `hacc` 方言：`hacc.entry` 与 `hacc.function_kind<DEVICE>`，用于标注函数为设备入口；
  - MLIR 标准方言：`func.func`、`memref.alloc`、`memref<…>` 类型——本示例的张量容器与函数包装均来自 MLIR 核心。
- **环境耦合**：链接中提及的 `installing_guide.md` 负责产出 `bishengir-compile` 与 `set_env.sh`，本文则消费这两者形成的产物完成「编译→注册→运行」闭环。

---

## 【使用方法】

1. **准备 IR 源文件**：`add.mlir`（内容即文档中给出的 `VecAdd` MLIR）。
2. **编译为设备端二进制**：
   ```bash
   bishengir-compile add.mlir -enable-hivm-compile -o kernel.o
   ```
3. **加载 CANN 环境**（已写入 Shell 配置可省略；路径以实际安装目录为准）：
   ```bash
   source /usr/local/Ascend/ascend-toolkit/set_env.sh
   ```
4. **编译 Host 程序**（将 `${ASCEND_HOME_PATH}` 替换为实际路径或 `set_env.sh` 设置的同名环境变量）：
   ```bash
   RT_INC=${ASCEND_HOME_PATH}/include
   PROF_INC=${ASCEND_HOME_PATH}/include/experiment/msprof
   PKG_INC=${ASCEND_HOME_PATH}/pkg_inc
   RT_LIB=${ASCEND_HOME_PATH}/lib64

   g++ main.cpp -I${RT_INC} -I${PROF_INC} -I${PKG_INC} -L ${RT_LIB} -l runtime -l ascendcl -o vec-add
   ```
5. **运行**（`main.cpp` 默认读取当前目录下的 `./kernel.o`）：
   ```bash
   ./vec-add
   ```
6. **预期输出（片段）**：`i0 Expect: 1 Result: 1`、`i1 Expect: 2 Result: 2`、`i2 Expect: 3 Result: 3`、`i3 Expect: 4 Result: 4`，……（共 16 行，至 `i15 Expect: 16 Result: 16`）。

> 原文未涉及：其它编译开关（如 `-O` 等级、目标芯片型号选择、profile/tiling 相关 flag）、多 block 启动参数以外的 kernel launch 调优、错误码对照表等——这些能力在本文档中均未给出，需结合 `installing_guide.md` 与 CANN 配套文档获取。
