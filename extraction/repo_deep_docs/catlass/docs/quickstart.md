# 快速上手指南

> 仓 `catlass` · 路径 `docs/quickstart.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/catlass/docs/quickstart.md

# CATLASS 快速上手指南 — 一体化深度解读

## 【定位】

这篇文档解决"初次接触 CATLASS 的开发者如何在 NPU 上从零搭建并运行一个 BasicMatmul 算子"的问题,系统性地展示了从环境准备、CANN 工具链安装,到 Kernel 层组件拼装、Device 层核函数封装、CMake 编译、最终上板执行的完整最小闭环。

---

## 【技术要点】

1. **环境前提**:依赖 CANN 开发套件包 `Ascend-cann-toolkit_<version>_linux-<arch>.run` 以及配套的 NPU 固件驱动;root 用户默认安装路径为 `/usr/local/Ascend/ascend-toolkit/`,通过 `source .../set_env.sh` 激活环境变量。
2. **Kernel 层三件套模板**:`<class BlockMmad_, class BlockEpilogue_, class BlockScheduler_>`,分别承担 block 层矩阵乘、后处理、数据走位(Scheduler/offset 计算)三类职责,共同组装出 `BasicMatmul` Kernel。
3. **关键 block 形状参数**:L1 基本块 `GemmShape<128, 256, 256>`,L0 基本块 `GemmShape<128, 256, 64>`;流水排布策略为 `MmadAtlasA2Pingpong<true>`,对应 Atlas A2 硬件的 ping-pong 双缓冲流水。
4. **Device 层封装范式**:以 `CATLASS_GLOBAL` 修饰符声明 `BasicMatmul` 模板函数,`()` 运算符接收 `MatmulKernel::Params` 参数对象,内核对象 `MatmulKernel matmul;` 实例化后直接以 `matmul(params)` 调用。
5. **核函数启动语法**:沿用 CUDA 风格的 `<<<BLOCK_NUM, nullptr, stream>>>` 三括号语法发起 BasicMatmul 调用,需显式给出矩阵数据类型/排布。
6. **编译双语言机制**:算子文件(`.cpp` 中的 ASCEND kernel 代码)通过 `set_source_files_properties(... LANGUAGE ASCEND)` 标记,与宿主 C++ 代码混编;`catlass_example_add_executable` 的第三个参数 `cube`/`vec`/`mix` 用于指定算子类型;最终以 `bash scripts/build.sh catlass_examples` 或 `bash scripts/build.sh 00_basic_matmul` 触发编译。

---

## 【关键机制与数据】

**工作原理与数据流**:

- **层级组装范式**(原文):CATLASS 把算子实现拆成 Device 层与 Kernel 层两层。Kernel 层由 Block 层组件(BlockMmad + BlockEpilogue + BlockScheduler)拼装而成,Kernel 层再被 Device 层包成可在 NPU 上 launch 的核函数。
- **数据流**(原文):Device 层的 `BasicMatmul(...)` 函数接收 `GM_ADDR gmA / gmB / gmC`(分别对应 A、B、C 矩阵在 Global Memory 上的指针)以及各自的 `LayoutA / LayoutB / LayoutC`,这些信息被打包进 `MatmulKernel::Params{problemShape, gmA, layoutA, gmB, layoutB, gmC, layoutC}`,最终交给 `MatmulKernel matmul; matmul(params)` 触发计算,结果写回 `gmC`。
- **Block 走位机制**(原文):`GemmIdentityBlockSwizzle<>` 模板类负责定义"数据走位方式"并提供 offset 计算方法,使得 block 在全局矩阵上能够正确分块。
- **可执行性能数据**:原文中没有性能数据(无 TFLOPS/带宽/时延等指标)。
- **正确性验证输出**(原文):算子执行成功后,终端输出 `Compare success.`,表明 Kernel 计算结果与参考结果一致。

---

## 【表格解读】

**原文无表格**。

(文档中没有出现参数表、性能对比表或配置项表格;关键参数以 C++ 模板参数形式散落在代码片段中。)

---

## 【公式解读】

**原文无公式**。

(文档没有出现 LaTeX 数学公式或伪代码形式的数学表达式。文档中出现的 `GemmShape<128, 256, 256>`、`GemmShape<128, 256, 64>` 是 C++ 模板类型参数,并非数学公式;按原文意图,这些参数分别表示 L1 基本块的 M/N/K 维度以及 L0 基本块的 M/N/K 维度。)

---

## 【关联】

文档通过文末/正文中的内部链接,与 CATLASS 仓库的其他文档/模块形成如下上下游关系:

- **环境配套 ↔ README**:`../README.md#软件硬件配套说明` 给出软件/硬件配套的总体说明,本文档的环境准备章节直接指向该锚点,作为 CANN 版本、NPU 型号配套的查证入口。
- **层级示意图 ↔ api 文档**:`api.md` 提供 CATLASS 分层(Device 层 / Kernel 层 / Block 层)的整体架构图,本文档"使用 CATLASS 开发 Matmul 算子"一节开头即提示"CATLASS 分层示意图见 api 文档",是理解本文 BlockMmad / BlockEpilogue / BlockScheduler 三件套语义的前置阅读材料。
- **走位策略 ↔ Swizzle 说明**:`swizzle_explanation.md` 是本文 `GemmIdentityBlockSwizzle<>` 的语义补充;本文只是"使用"该策略,完整 swizzle 算法/策略族解释需跳转阅读。
- **代码样例 ↔ examples 目录**:`../examples/00_basic_matmul/basic_matmul.cpp` 是本文档的"代码样例"完整实现,文档最后的"代码样例"小节明确指向该路径,作为可运行的最小参考实现。该样例支持的输入排布为 A/B 矩阵的 rowMajor(原文:"该示例支持 A/B 矩阵为 rowMajor 数据排布输入")。

---

## 【使用方法】

**环境准备(原文)**:
```bash
chmod +x Ascend-cann-toolkit_<version>_linux-<arch>.run
./Ascend-cann-toolkit_<version>_linux-<arch>.run --install
source /usr/local/Ascend/ascend-toolkit/set_env.sh
```

**编译(原文)**:
- 在 `CMakeLists.txt` 中:
  ```cmake
  set_source_files_properties(basic_matmul.cpp PROPERTIES LANGUAGE ASCEND)
  catlass_example_add_executable(
      00_basic_matmul
      cube
      basic_matmul.cpp
  )
  ```
  其中第三个参数 `cube`/`vec`/`mix` 用于指定算子类型。
- 在项目目录下执行:
  ```bash
  bash scripts/build.sh catlass_examples          # 编译 examples 内所有用例
  bash scripts/build.sh 00_basic_matmul           # 编译指定用例
  ```

**执行(原文)**:
```bash
cd output/bin
./00_basic_matmul 256 512 1024 0
# 参数依次:可执行文件名 | 矩阵 m 轴 | n 轴 | k 轴 | Device ID(可选)
```

**配置项/参数说明(原文)**:
- `L1TileShape = GemmShape<128, 256, 256>`:L1 基本块形状。
- `L0TileShape = GemmShape<128, 256, 64>`:L0 基本块形状。
- `DispatchPolicy = MmadAtlasA2Pingpong<true>`:Atlas A2 的 ping-pong 流水排布。
- `AType/BType/CType = GemmType<Element*, Layout*>`:分别封装 A/B/C 矩阵的数据类型与排布信息。
- `BlockEpilogue = void`:本基础示例不涉及后处理。
- `BlockScheduler = GemmIdentityBlockSwizzle<>`:默认 block 走位策略。
- 算子类型取值:`cube` / `vec` / `mix`。

**正确性判据(原文)**:执行后终端出现 `Compare success.` 即视为基于 CATLASS 编写的 Kernel 已成功执行并通过对比。
