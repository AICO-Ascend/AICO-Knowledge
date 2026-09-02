# Compile and Run Example

> 仓 `ascendnpu-ir` · 路径 `docs/source/en/introduction/quick_start/examples.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/ascendnpu-ir/docs/source/en/introduction/quick_start/examples.md

# ascendnpu-ir 文档深度解读：Compile and Run Example

---

## 【定位】

这篇文档解决的是 **"如何将一段 MLIR/HIVM IR 编译成昇腾 NPU 设备二进制，并在 CANN 运行时中注册、launch、验证计算正确性"** 的端到端落地问题——即 bishengir 编译工具链产出 `kernel.o` 之后，从 C++ 宿主侧完成设备初始化、内核注册、内存搬运、核函数调用、回拷验证的最小可运行示例（VecAdd）。

---

## 【技术要点】

1. **IR 入口：VecAdd MLIR 示例**
   - 一个名为 `@add` 的 `func.func`，含属性 `{hacc.entry, hacc.function_kind = #hacc.function_kind<DEVICE>}`，标识这是 Device 侧入口函数。
   - 三段 GM 内存参数：`memref<16xi16, #hivm.address_space<gm>>`。
   - 三段 UB 中间分配：`memref.alloc() : memref<16xi16, #hivm.address_space<ub>>`。
   - 三个 HIVM 算子：`hivm.hir.load`、`hivm.hir.vadd`、`hivm.hir.store`，完成"GM→UB→vadd→GM"流程。
   - 元素类型 `i16`，长度 `16`，使用 `gm`（global memory）与 `ub`（unified buffer）两种 address space。

2. **编译命令：生成 device binary**
   - 命令：`bishengir-compile add.mlir -enable-hivm-compile -o kernel.o`。
   - 产物：`kernel.o`，即 NPU 上运行的算子二进制。
   - 隐含路径依赖：需 `bishengir-compile` 已在 PATH 上（由前置"Build and install"步骤保证）。

3. **运行时二进制注册（CANN Runtime）**
   - `rtDevBinary_t binary` 字段填充：`data`、`length`、`magic = RT_DEV_BINARY_MAGIC_ELF_AIVEC`、`version = 0`。
   - `rtDevBinaryRegister(&binary, &binHandle)`：把二进制注册到运行时，得到 `binHandle`。
   - `rtFunctionRegister(binHandle, (const void *)stubFunc, kernelName, (void *)kernelName, 0)`：把 stub 函数 `add` 与内核符号绑定；本例 `stubFunc == kernelName == "add"`。
   - 任意注册步骤返回非 `RT_ERROR_NONE` 即打印 `errorCode=%d` 并失败退出。

4. **设备/Stream 初始化**
   - `aclInit(nullptr)` → `aclrtSetDevice(0)` → `aclrtCreateStream(&stream)`。
   - 三个 API 全部以 `EXPECT_EQ(error, ACL_RT_SUCCESS, ...)` 宏校验。

5. **数据搬运：Host → Device**
   - 三块显存分配：`outputDevice`、`input0Device`、`input1Device`，分配策略均为 `ACL_MEM_MALLOC_HUGE_FIRST`。
   - 两块输入通过 `aclrtMemcpy(..., ACL_MEMCPY_HOST_TO_DEVICE)` 下发。
   - 输入数据：  
     - `input0Value = {0,1,2,3,4,5,6,7, 8,9,10,11,12,13,14,15}`  
     - `input1Value = {1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1}`（全 1）  
     - 期望 `expectedValue = {1,2,...,16}`（即 `input0 + input1`）。

6. **核函数 Launch 与同步**
   - 参数数组：`void *args[] = {input0Device, input1Device, outputDevice};`
   - `rtKernelLaunch(stubFunc, 1, static_cast<void *>(&args), sizeof(args), nullptr, stream);`——blockDim=1，args 传首地址，`sizeof(args)` 是指针数组大小。
   - `aclrtSynchronizeStream(stream)` 等待完成。
   - `aclrtMallocHost` 分配 host 端 pinned buffer，`aclrtMemcpy(..., ACL_MEMCPY_DEVICE_TO_HOST)` 回拷，再按索引逐元素 `Expect vs Result` 打印。

7. **编译可执行文件的链接配置**
   - 头文件：`${ASCEND_HOME_PATH}/include`、`${ASCEND_HOME_PATH}/include/experiment/msprof`、`${ASCEND_HOME_PATH}/pkg_inc`。
   - 库路径：`${ASCEND_HOME_PATH}/lib64`。
   - 链接库：`-l runtime -l ascendcl`。
   - 输出名：`vec-add`。

---

## 【关键机制与数据】

- **数据流（原文流程）**：`add.mlir (MLIR/HIVM)` → `bishengir-compile -enable-hivm-compile` → `kernel.o` → `readBinFile` 读取到 buffer → `rtDevBinaryRegister` 注册 ELF 镜像 → `rtFunctionRegister` 把 stub 函数 `"add"` 绑定到符号 `"add"` → `aclrtMalloc` 三块 device buffer → `aclrtMemcpy (H2D)` 两次 → `rtKernelLaunch("add", 1, &args, sizeof(args), nullptr, stream)` → `aclrtSynchronizeStream` → `aclrtMallocHost` + `aclrtMemcpy (D2H)` → 逐元素核对 → 释放。
- **运行时错误码契约（原文）**：所有 `aclError` 必须等于 `ACL_RT_SUCCESS`；所有 `rtError_t` 必须等于 `RT_ERROR_NONE`。宏 `EXPECT_EQ` 不满足时打印 `[failed] <msg>` 并 `exit(1)`。
- **成功标记（原文）**：初始化成功、`register kernel success`、`memcpy host to device success`、`stream synchronize success`、`memcpy device to host success`、`compare output success` 六个 `[success]` 串行打印。
- **向量规模（原文）**：`16` 个 `i16` 元素；输入一 `{0..15}`，输入二全 `1`，期望 `{1..16}`。原文期望输出片段显示 `i0 Expect:1 Result:1`、`i1 Expect:2 Result:2`、… 直至 `i3 Expect:4 Result:4`，其余以 `...` 省略。
- **关键常量（原文）**：`RT_DEV_BINARY_MAGIC_ELF_AIVEC`（`rtDevBinary_t.magic` 字段）、`version = 0`、`blockDim=1`。
- **资源释放顺序（原文）**：`free(buffer)` → `aclrtFreeHost(outHost)` → `aclrtFree(outputDevice/input0Device/input1Device)` → `aclrtDestroyStream(stream)` → `aclrtResetDevice(0)` → `aclFinalize()`。

---

## 【表格解读】

**原文无表格**（全文为一段 MLIR 示例、三段 bash 命令、一段 C++ 代码以及一段预期输出文本，不含任何参数表、性能对比或配置项表格）。

---

## 【公式解读】

**原文无公式**（既无 LaTeX 表达式，也无伪代码形式的数学公式；唯一"算术性"的语义是 `input0[i] + 1 = expected[i]`，这是 C++ 中由 `vadd` 与初始化常量隐含实现的，并非以公式形式给出）。

---

## 【关联】

- **前置依赖：Build and install（`installing_guide.md`）**
  - 文档开篇明确要求完成该指南的构建安装、确保 `bishengir-compile` 在 PATH 上、安装 CANN 并执行 `set_env.sh`。
  - 编译 `main.cpp` 的 bash 片段也再次提示"If CANN is installed elsewhere, set `ASCEND_HOME_PATH` or use the variable from `set_env.sh`"，并指向同一份"Build and Install"指南——这是本文档在工具链层面的唯一外部锚点。
- **编译工具链模块：`bishengir-compile`**
  - 是 MLIR→device binary 的入口；本文档以 `-enable-hivm-compile` 这一选项触发 HIVM 后端 codegen，得到 `kernel.o`。
- **IR 方言：HIVM Dialect**
  - 示例 IR 依赖 `#hivm.address_space<gm/ub>`、`hivm.hir.load`、`hivm.hir.vadd`、`hivm.hir.store` 等方言算子，因此本文档隐式依赖项目中 HIVM 方言与 lowering pass 的实现。
- **HACC Dialect 属性**
  - `hacc.entry` 与 `hacc.function_kind<DEVICE>` 表明本函数为 device 端入口，由 HACC 方言标注，与 host 侧调用约定配合。
- **CANN Runtime / ACL 头文件集合**
  - 文档 import 的 `acl/acl.h`、`acl/error_codes/rt_error_codes.h`、`runtime/runtime/rt.h` 分别对应 ACL（Ascend Computing Language）与 RT（Runtime）两层 API，构成 device binary 在 host 端的注册、launch、内存、同步接口集合。
- **内存属性 `ACL_MEM_MALLOC_HUGE_FIRST`**
  - 表明本示例优先使用"大页优先"分配策略，属于 CANN/ACL 的内存策略选项，与文档中其他"quick start"或"runtime"说明可能共享配置语义。

---

## 【使用方法】

**1. 准备 MLIR 源（原文）：**
将示例 IR 保存为 `add.mlir`，包含 `func.func @add`、三段 GM 参数、三次 `memref.alloc()`（UB）、`hivm.hir.load` ×2、`hivm.hir.vadd`、`hivm.hir.store`，以及 `return`。

**2. 编译为设备二进制（原文命令）：**
```bash
bishengir-compile add.mlir -enable-hivm-compile -o kernel.o
```
产物 `kernel.o` 即 NPU 算子二进制，运行在 NPU 上。

**3. 加载 CANN 环境（原文命令，路径可能因安装位置而异）：**
```bash
source /usr/local/Ascend/ascend-toolkit/set_env.sh
```
（若 CANN 安装在其他位置，需配置 `ASCEND_HOME_PATH` 或使用 `set_env.sh` 导出的同名变量。）

**4. 构建宿主可执行文件（原文命令）：**
```bash
RT_INC=${ASCEND_HOME_PATH}/include
PROF_INC=${ASCEND_HOME_PATH}/include/experiment/msprof
PKG_INC=${ASCEND_HOME_PATH}/pkg_inc
RT_LIB=${ASCEND_HOME_PATH}/lib64

g++ main.cpp -I${RT_INC}  -I${PROF_INC} -I${PKG_INC} -L ${RT_LIB} -l runtime -l ascendcl -o vec-add
```
注意：`main.cpp` 从当前目录读取 `./kernel.o`，因此编译步骤应在 `kernel.o` 所在目录执行。

**5. 运行（原文命令）：**
```bash
./vec-add
```
运行后将看到六个 `[success] ...` 标记以及 `i0..i3`（其余省略）的 `Expect / Result` 对照行，验证 `Result == Expect`（即 `1..16`）即说明 vadd 在 NPU 上跑通。

**6. 运行时配置项（原文显式涉及）**
- 设备号：`aclrtSetDevice(0)`——使用 0 号卡。
- Stream：`aclrtCreateStream(&stream)` 默认参数，未指定优先级/标志。
- 内存分配策略：`ACL_MEM_MALLOC_HUGE_FIRST`。
- 拷贝方向：`ACL_MEMCPY_HOST_TO_DEVICE`、`ACL_MEMCPY_DEVICE_TO_HOST`。
- 二进制 magic：`RT_DEV_BINARY_MAGIC_ELF_AIVEC`，`version = 0`。
- Launch 维度：`blockDim = 1`（`rtKernelLaunch` 第 2 参数），`args` 传首地址、`sizeof(args)` 作为长度。
- Stub / kernel 名：均为字符串 `"add"`。
