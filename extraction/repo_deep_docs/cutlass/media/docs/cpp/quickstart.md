# Quickstart

> 仓 `cutlass` · 路径 `media/docs/cpp/quickstart.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/cutlass/media/docs/cpp/quickstart.md

# CUTLASS Quickstart 文档深度解读

## 【定位】
本篇文档解决的是 **CUTLASS 库从环境准备到首次构建、运行 Profiler 与单元测试、以及将 CUTLASS 集成进第三方应用的"一键入门"问题**,面向首次接触 CUTLASS 的开发者提供一条按步骤可复制的入门路径。

---

## 【技术要点】

1. **环境前提**: NVIDIA CUDA Toolkit ≥ 11.4(推荐 **12.0**)、CMake ≥ **3.18**、支持 C++17 的 host 编译器(最低 g++ **7.5.0**)、Python ≥ **3.6+**;可选依赖 cuBLAS 与 cuDNN ≥ **v7.6**。

2. **基础构建骨架**:通过设置环境变量 `CUDACXX=${CUDA_INSTALL_PATH}/bin/nvcc`,随后在 `build/` 目录运行 `cmake .. -DCUTLASS_NVCC_ARCHS=<arch>`,其中 `arch` 取 `90a`(Hopper)/`100a`(Blackwell SM100)/`80`(Ampere)/`75`(Turing)/`70`(Volta)/`"60;61"`(Pascal)/`"50;53"`(Maxwell)。

3. **加速构建的可选开关**:通过 `-DCUTLASS_ENABLE_TESTS=OFF -DCUTLASS_UNITY_BUILD_ENABLED=ON` 仅构建 Profiler 并加速编译;通过 `-DCUTLASS_LIBRARY_OPERATIONS=conv2d` 仅编译 2D 卷积 kernel;通过 `-DCUTLASS_LIBRARY_KERNELS=cutlass3x*` 按名称过滤仅生成 CUTLASS-3 kernel;亦可使用 `-DCUTLASS_ENABLE_CUBLAS=OFF` / `-DCUTLASS_ENABLE_CUDNN=OFF` 显式排除可选依赖。

4. **CUTLASS Profiler**:用 `make cutlass_profiler -j12` 编译,命令行入口为 `./tools/profiler/cutlass_profiler`。支持两类操作 —— GEMM 通过 `--kernels=sgemm --m=4352 --n=4096 --k=4096` 触发(sgemm, 单精度, 列主序),convolution 通过 `--kernels=s1688fprop` 或 `--operation=conv2d` 触发,运行后输出 Bytes、FLOPs、Runtime(ms)、Memory(GiB/s)、Math(GFLOP/s) 五项关键指标。

5. **单元测试**:通过 `make test_unit -j` 编译并执行全部单元测试;通过 `make test_unit_gemm_warp -j` 执行 warp 级 GEMM 子集;测试按层级组织,与 CUTLASS Template Library 的层级对应,可按目标切片并行编译。

6. **嵌入第三方应用**:把 [`/include`](https://github.com/NVIDIA/cutlass/tree/main/include) 加入 include 路径,以 C++17 及以上编译即可调用 `cutlass::half_t`、`cutlass::gemm::device::Gemm<...>` 等模板;示例给出打印 `half_t` 与一个面向 Turing Tensor Cores(Sm75, OpClassTensorOp, half/float 累加器)的混合精度 GEMM 模板实例。

---

## 【关键机制与数据】

**构建机制**:CMake 在 `build/` 下解析 `CUTLASS_NVCC_ARCHS` 来按架构生成 SASS,可在同一构建内通过 `;` 分号列出多个 SM 数字(见 Pascal `60;61`、Maxwell `50;53`)。可选 `CUTLASS_UNITY_BUILD_ENABLED=ON` 与 `CUTLASS_LIBRARY_OPERATIONS`/`CUTLASS_LIBRARY_KERNELS` 通过限制编译范围与合并翻译单元两种手段压缩编译耗时。

**Profiler 数据流**:Profiler 接受问题规模参数(--m/--n/--k 或 --n/--h/--w/--c/--k/--r/--s 等),自动枚举可用 kernel 实现,选取实际运行的实现并报告。

**原文: GEMM Profiler 输出(sgemm, m=n=k=4096 类型问题):**
- Provider:`CUTLASS`;Operation:`cutlass_simt_sgemm_128x128_nn`
- Bytes:**52428800 bytes**;FLOPs:**146064539648 flops**
- Runtime:**10.5424 ms**;Memory:**4.63158 GiB/s**;Math:**13854.9 GFLOP/s**
- 关键 CTA/warp 参数:`cta_m=128 cta_n=128 cta_k=8 stages=2 warps_m=2 warps_n=2 warps_k=1`,`op_class=simt`,`accum=f32`,`min_cc=50 max_cc=1024`

**原文: conv2d Profiler 输出**(n=8, h=w=224, c=k=128, r=s=3, pad_h=pad_w=1):
- Operation:`cutlass_simt_sfprop_optimized_128x128_8x2_nhwc`
- Bytes:**2055798784 bytes**;FLOPs:**118482796544 flops**
- Runtime:**8.13237 ms**;Memory:**235.431 GiB/s**;Math:**14569.3 GFLOP/s**
- 关键参数:`cta_m=128 cta_n=128 cta_k=8 stages=2 warps_m=4 warps_n=2 warps_k=1`,`iterator_algorithm=optimized`,`Activation/Filter/Output=f32:nhwc`,`conv_mode=cross`,`split_k_mode=serial`

**单元测试规模(原文):**
- 完整 `test_unit`:**946 tests from 57 test cases**,10812 ms
- 仅 `test_unit_gemm_warp`:**104 tests from 32 test cases**,294 ms
- 文中明确说明"具体测试数随功能迭代而变化";并指出测试运行时"自动构造 runtime filters 以跳过不支持全部功能的架构",因此同一构建在不同 GPU 上实际执行的用例集合不同。

---

## 【表格解读】
**原文无表格**。架构对应关系虽以列表形式呈现,但未作为表格列出,故此处按原文形式保留为分项列表。

---

## 【公式解读】
**原文无公式**。文档不包含任何 LaTeX 或伪代码数学公式;运行时的 Bytes、FLOPs、Runtime、Memory bandwidth、Math throughput 等数值均为 Profiler 实际打印的运行结果,非显式公式。

---

## 【关联】

- **[`quickstart.md#example-cmake-commands`](#example-cmake-commands)**:文档在 `CUTLASS_LIBRARY_KERNELS` 用法处显式提示 "See more examples on selectively compiling CUTLASS GEMM and convolution kernels here" —— 即同一 `quickstart.md` 文档锚点下的"示例 CMake 命令"段落包含更多选择性编译的范例,本节为入口而该锚点为扩展示例集。

- **[`profiler.md`](#)**:文档在 Profiler 两段示例输出结尾处直接提示"See documentation for the CUTLASS Profiler for more details",表明 `profiler.md` 是 Profiler 的详尽参考(参数语义、性能模型、扩展选项等),本篇只演示最小可运行实例。

- **[`./blackwell_functionality.md`](#)**:文档在 "Building for Multiple Architectures" 中以 NVIDIA Blackwell 架构(`100a`)作为顶层示例列出,且在 `cmake .. -DCUTLASS_NVCC_ARCHS=100a` 与 `NVIDIA Blackwell SM100 GPU architecture` 两个地方强调 Blackwell 是首发支持对象之一,`blackwell_functionality.md` 应提供 Blackwell 上 CUTLASS 各功能(GEMM/Convolution/Epilogue 等)的可用性矩阵与配置细节。

---

## 【使用方法】

### 构建与可选开关(原文 CMake 命令)

```bash
# 最小构建(任选其一架构)
$ export CUDACXX=${CUDA_INSTALL_PATH}/bin/nvcc
$ mkdir build && cd build
$ cmake .. -DCUTLASS_NVCC_ARCHS=90a            # NVIDIA Hopper
$ cmake .. -DCUTLASS_NVCC_ARCHS=100a           # NVIDIA Blackwell SM100

# 仅构建 Profiler,加速编译
$ cmake .. -DCUTLASS_NVCC_ARCHS=90a -DCUTLASS_ENABLE_TESTS=OFF -DCUTLASS_UNITY_BUILD_ENABLED=ON

# 仅编译 2D 卷积 kernel
$ cmake .. -DCUTLASS_NVCC_ARCHS=90a -DCUTLASS_LIBRARY_OPERATIONS=conv2d

# 仅按名称过滤(CUTLASS-3)
$ cmake .. -DCUTLASS_NVCC_ARCHS=90a -DCUTLASS_LIBRARY_KERNELS=cutlass3x*

# 显式排除可选依赖
$ cmake .. -DCUTLASS_ENABLE_CUBLAS=OFF -DCUTLASS_ENABLE_CUDNN=OFF
```

### 多架构构建(原文)

```bash
$ cmake .. -DCUTLASS_NVCC_ARCHS=100a   # Blackwell
$ cmake .. -DCUTLASS_NVCC_ARCHS=90a    # Hopper
$ cmake .. -DCUTLASS_NVCC_ARCHS=80     # Ampere
$ cmake .. -DCUTLASS_NVCC_ARCHS=75     # Turing
$ cmake .. -DCUTLASS_NVCC_ARCHS=70     # Volta
$ cmake .. -DCUTLASS_NVCC_ARCHS="60;61" # Pascal
$ cmake .. -DCUTLASS_NVCC_ARCHS="50;53" # Maxwell
```

### 构建并运行 Profiler(原文)

```bash
# 编译
$ make cutlass_profiler -j12

# 运行 GEMM
$ ./tools/profiler/cutlass_profiler --kernels=sgemm --m=4352 --n=4096 --k=4096

# 运行 2D convolution(fprop)
$ ./tools/profiler/cutlass_profiler --kernels=s1688fprop \
        --n=8 --h=224 --w=224 --c=128 --k=128 --r=3 --s=3 --pad_h=1 --pad_w=1

# 穷举所有 2D convolution 实现
$ ./tools/profiler/cutlass_profiler --operation=conv2d \
        --n=8 --h=224 --w=224 --c=128 --k=128 --r=3 --s=3
```

### 编译并运行单元测试(原文)

```bash
# 全量
$ make test_unit -j

# warp 级 GEMM 子集
$ make test_unit_gemm_warp -j
```

### 在第三方应用中使用 CUTLASS(原文)

1. 将仓库内的 `/include` 加入编译的 include 路径;
2. 编译标准不低于 C++17;
3. 在源文件中 `#include <cutlass/cutlass.h>` 与子模块头文件(`numeric_types.h`、`core_io.h`、`gemm/device/gemm.h` 等);
4. 若使用 `tools/util/include` 中的工具(如 `cutlass/util/host_tensor.h`),需将该路径同样加入 include 列表;
5. 通过模板实例化使用 kernel,例如 Turing Tensor Core 上 half 输入 / float 累加器的 GEMM:

```c++
using Gemm = cutlass::gemm::device::Gemm<
    cutlass::half_t,                       // ElementA
    cutlass::layout::ColumnMajor,          // LayoutA
    cutlass::half_t,                       // ElementB
    cutlass::layout::ColumnMajor,          // LayoutB
    cutlass::half_t,                       // ElementOutput
    cutlass::layout::ColumnMajor,          // LayoutOutput
    float,                                 // ElementAccumulator
    cutlass::arch::OpClassTensorOp,        // tag indicating Tensor Cores
    cutlass::arch::Sm75                    // SM 标签
>;
```

## 图文联合解读

- `gemm-hierarchy-with-epilogue-no-labels.png`: 1）图以虚线把 A/B 及输出从整块逐级展开为线程块瓦片、线程束/线程片段和标量乘加，彩色区标出当前 K 块；右侧 F(…I…) 表示片段级尾处理。  
2）说明 GEMM 依靠多级并行、分块及寄存器/共享内存复用提升吞吐。  
3）对应 Quickstart 按 Hopper/Blackwell 架构编译，并用 Profiler/名称过滤验证、筛选内核。
