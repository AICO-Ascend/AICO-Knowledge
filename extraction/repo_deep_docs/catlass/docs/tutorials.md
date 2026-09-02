# Catlass 算子模板库开发者体验说明文档

> 仓 `catlass` · 路径 `docs/tutorials.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/catlass/docs/tutorials.md

# Catlass 算子模板库教程文档深度解读

## 【定位】

本文档是 Catlass（CANN Templates for Linear Algebra Subroutines）算子模板库的**开发者入门与体验教程**，定位为：以 BasicMatmul 为例，演示如何在昇腾硬件上基于 Catlass 模板库完成 GEMM 算子从代码搭建、编译、运行、精度验证到性能测试与 tiling 调优的完整开发闭环。

---

## 【技术要点】

1. **分层模块化设计理念**：将 GEMM 计算解耦为"数据分块策略 + 计算单元配置"等可灵活组合的组件，算法框架的特定步骤延迟到子类实现（Template Method 模式），既保证共性复用又允许差异化扩展。原文配图 `figures/api_level.png` 展示了分层抽象，`figures/api_custom.png` 展示了组件级流水可配置性。

2. **Block / Tile 双层模板示例矩阵**：库在 Block 与 Tile 层级提供 **40+** 高性能模块示例，覆盖数据搬运、异步流水编排、关键接口用法。代码完全开源，从上至下可参考。

3. **核心模板拼装（BasicMatmul Kernel 组装链）**：
   - 硬件标签：`ArchTag = Arch::AtlasA2`
   - 调度策略：`DispatchPolicy = Gemm::MmadAtlasA2Pingpong<true>`（乒乓流水）
   - L1/L0 Tile 切分：`L1TileShape = GemmShape<128,256,256>`，`L0TileShape = GemmShape<128,256,64>`
   - 数据类型与排布：`AType/BType/CType = GemmType<half, RowMajor>`
   - Block 组件：`BlockMmad`（计算）+ `BlockScheduler = GemmIdentityBlockSwizzle<3, 0>`（Block 调度）
   - Kernel 装配：`BasicMatmul<BlockMmad, BlockEpilogue, BlockScheduler>`
   - Device 适配层：`DeviceGemm<MatmulKernel>`

4. **典型算子执行四步流程**（原文 Run 函数注释）：
   - 第一步：流初始化 + device 侧空间申请（A、B、C 三块矩阵 + workspace）
   - 第二步：选择优化策略（Arch + Dispatch + Tile）
   - 第三步：选择数据类型并组装组件
   - 第四步：执行模板样例（CanImplement → GetWorkspaceSize → Initialize → 调用）

5. **依赖与构建**：要求 **CANN 8.2.RC1.alpha002 及之后版本**，`cmake >= 3.15`；源码仓库 `https://gitcode.com/cann/catlass.git`；构建脚本 `bash scripts/build.sh basic_matmul`，成功标识 `[INFO]Target 'basic_matmul' built successfully`。

6. **调优路径**：通过修改 `L1TileShape` / `L0TileShape` 两行模板参数即可切换切分策略，配合 `msprof` 工具对比 `Task Duration(us)`，完成 tiling 性能调优。文档给出的对照 case：`m,n,k=128,256,4096` 下 `<128,256,256>/<128,256,64>` vs `<32,128,256>/<32,128,64>`。

---

## 【关键机制与数据】

### 工作原理（按 Run 函数执行顺序）

1. **参数解析**：命令行形如 `basic_matmul m n k [device_id]`，默认 `GemmCoord{128,128,128}`，默认 device_id=0。
2. **资源申请**：依据 `m·k`、`k·n`、`m·n` 计算 A/B/C 三矩阵元素量；统一采用 `ACL_MEM_MALLOC_HUGE_FIRST` 大页优先策略；矩阵排布统一用 `layout::RowMajor`（行优先）。
3. **硬件核心数获取**：`platform_ascendc::PlatformAscendCManager::GetInstance()->GetCoreNumAic()` 取得 AIC 核心数，调用 Kernel 时传入。
4. **Kernel 生命周期管理**（Device 适配层职责）：
   - `CanImplement(arguments)`：判定当前参数能否被 Kernel 执行；
   - `GetWorkspaceSize(arguments)`：返回所需 workspace 大小；
   - `Initialize(arguments, deviceWorkspace)`：分配内部状态；
   - `matmulOp(stream, aicCoreNum)`：真正发起计算；
   - `aclrtSynchronizeStream(stream)`：阻塞同步等待执行完成。
5. **精度比对闭环**：用 `golden::ComputeMatmul` 在 CPU 端计算参考结果，`golden::CompareData` 以 `k` 为比较维度逐元素对比 fp16 输出与 float 参考，输出 `Compare success` 或错误数。
6. **性能采集**：`msprof op ./basic_matmul 128 256 4096 0` 在 `output/bin` 下生成 `OPPROF_xxxx` 目录，查阅 `OpBasicInfo.csv` 中 `Task Duration(us)` 字段即得耗时。

### 性能/对照数据（原文明确给出的）

- 原文默认/调优 case：**`m, n, k = 128, 256, 4096`**；
- TileShape 调优对比（原文 case1）：
  - 原始：`L1TileShape: <128,256,256>`，`L0TileShape: <128,256,64>`
  - 调整：`L1TileShape: <32,128,256>`，`L0TileShape: <32,128,64>`
  - 比对方式：相同命令 `msprof op ./basic_matmul 128 256 4096 0` 在修改前后各跑一次。
- 调优原理（原文）：通过 `catlass/examples/basic_matmul/basic_matmul.cpp` 中**仅两行** TileShape 代码即可完成切分策略调整，体现"组件级替换即可改变流水组合"的设计目标。
- 备注（原文）：精度比对使用 CPU 计算，会引入额外耗时。

---

## 【表格解读】

**原文无表格**（文档以代码示例、命令行、流程注释为主要表达形式，无 markdown 表格）。如需将示例中的关键参数结构化，可参考下文"使用方法"章节给出的命令参数表。

---

## 【公式解读】

**原文无公式**（无 LaTeX 或伪代码形式数学公式）。涉及的数学对象仅有 `GemmCoord{m, n, k}` 描述的 GEMM 形状，其语义为：A 矩阵 `m×k`、B 矩阵 `k×n`、C 矩阵 `m×n`，且 `lenA = m·k`、`lenB = k·n`、`lenC = m·n`，元素量计算体现在 `Run()` 中 `sizeA/sizeB/sizeC = len · sizeof(fp16_t)` 的代码行。

---

## 【关联】

文档中通过 `#include` 与代码实例暗示了 Catlass 内部模块的依赖与组织关系，主要关联如下：

| 引用头文件 | 角色定位（基于原文语境） |
|---|---|
| `catlass/catlass.hpp` | 总入口头文件 |
| `catlass/arch/arch.hpp` | 硬件架构标签（`Arch::AtlasA2`） |
| `catlass/layout/layout.hpp` | 矩阵排布（`RowMajor`） |
| `catlass/status.hpp` | 状态/错误码封装（`ACL_CHECK`） |
| `catlass/gemm/gemm_type.hpp` | GEMM 类型封装（`GemmType<half, Layout>`） |
| `catlass/gemm/dispatch_policy.hpp` | 调度策略（`MmadAtlasA2Pingpong<true>`） |
| `catlass/gemm/block/block_mmad.hpp` | Block 级矩阵乘计算组件 |
| `catlass/gemm/block/block_swizzle.hpp` | Block 级调度（`GemmIdentityBlockSwizzle<3, 0>`） |
| `catlass/gemm/device/device_gemm.hpp` | Device 层适配器 |
| `catlass/gemm/kernel/basic_matmul.hpp` | BasicMatmul Kernel 模板本体 |
| `helper.hpp`、`golden.hpp`（examples 内） | 辅助/参考实现（随机数据、CPU 对照、CompareData） |

文档中提到的特性—组件对应关系：
- "**分层模块化设计**" → 对应 `catlass/gemm/...` 下的 kernel/block/device 三层抽象（见 `figures/api_level.png`，原文未给出图片内容细节）。
- "**算子流水自定义灵活配置**" → 对应通过替换 `DispatchPolicy`/`L1TileShape`/`L0TileShape`/`BlockScheduler` 即可重组流水（见 `figures/api_custom.png`，原文未给出图片内容细节）。
- "**40+ 高性能模块示例**" → 文中以 `basic_matmul.cpp` 为一个端到端入口，暗示 `examples/` 目录提供更多同类样例。

文末内部链接标注为（无），表明该教程文档作为独立 README/Markdown 形式存在，未在文末嵌入额外跳转链接。

---

## 【使用方法】

### 环境与依赖
```bash
source /usr/local/Ascend/ascend-toolkit/set_env.sh
git clone https://gitcode.com/cann/catlass.git
# 要求：CANN 8.2.RC1.alpha002 及之后版本，cmake >= 3.15
```

### 目录与文件准备
```bash
cd catlass/examples
mkdir basic_matmul
# 在 basic_matmul/ 下创建 basic_matmul.cpp 与 CMakeLists.txt
```

### 编译
```bash
# 在 catlass 根目录下
bash scripts/build.sh basic_matmul
# 成功标识：[INFO]Target 'basic_matmul' built successfully
```

### 运行与验证
```bash
cd output/bin
./basic_matmul 128 256 4096 0
# 成功标识：Compare success.
# 注：CPU 精度比对会引入额外耗时
```

### 性能测试
```bash
# 在 output/bin 目录下
msprof op ./basic_matmul 128 256 4096 0
# 同目录生成 OPPROF_xxxx 文件夹
# 关键指标：OpBasicInfo.csv 中的 "Task Duration(us)"
```

### tiling 调优（原文 case1：`m,n,k=128,256,4096`）
修改 `basic_matmul.cpp` 中：
```cpp
using L1TileShape = GemmShape<...>;
using L0TileShape = GemmShape<...>;
```
- 原配置：`L1TileShape=<128,256,256>`, `L0TileShape=<128,256,64>`
- 调整后：`L1TileShape=<32,128,256>`, `L0TileShape=<32,128,64>`
- 重新编译后用相同 `msprof` 命令采集，对比 `Task Duration(us)` 差异。

### 关键命令行/配置项速查

| 命令/配置项 | 取值 | 含义（原文） |
|---|---|---|
| `./basic_matmul m n k [device_id]` | `128 256 4096 0` | 算子执行参数与 device id |
| `bash scripts/build.sh basic_matmul` | — | 编译指定算子样例 |
| `msprof op ./basic_matmul ...` | — | 算子性能采集（生成 OPPROF 目录） |
| `Arch::AtlasA2` | — | 硬件架构标签（A2 系列） |
| `MmadAtlasA2Pingpong<true>` | `<true>` | 调度策略：乒乓流水 |
| `L1TileShape` | `<128,256,256>` 或 `<32,128,256>` | L1 层切分（M,N,K） |
| `L0TileShape` | `<128,256,64>` 或 `<32,128,64>` | L0 层切分（M,N,K） |
| `GemmIdentityBlockSwizzle<3, 0>` | `<3, 0>` | Block 调度 swizzle 次序 |
| `dataType` | `fp16_t / half` | 矩阵元素数据类型 |
| `LayoutA/B/C` | `RowMajor` | 矩阵排布（行优先） |
| 内存分配 flag | `ACL_MEM_MALLOC_HUGE_FIRST` | device 内存大页优先策略 |

## 图文联合解读

- `api_level.png`: **1) 图示内容**：自上而下五层分层架构——调用接口(Device)：DeviceGemm/GemmV；多核计算(Kernel)：Gemm/Matmul/GroupedMatmul/FA；单核计算(Block)：BlockMmad/BlockEpilogue；单个步骤(Tile)：CopyGmToL1/CopyL1ToL0/TileMmad/CopyUbToGm；单条指令(Basic)：Load2D/DataCopy/VAdd/VSub/Mmad。

**2) 技术结论**：算子实现按"设备→核→块→片→指令"粒度逐级细化，高层通过组合低层模块拼装完整计算流水线，每层封装对应不同硬件结构与流水阶段。

**3) 与文档关系**：直观印证文档"分层模块化设计"与"分层抽象"论点，体现各层软件抽象精准映射硬件层级，支持模块化快速搭建与灵活替换。
- `api_custom.png`: ## 图文联合解读

**1) 图中内容：** 展示Catlass算子分层模块化的树形结构。从顶层`DeviceGemm`（设备级接口，橙色）向下逐层分解：经`kernel: xxxMatmul`（蓝色核函数模板）分流为两个绿色Block级组件——`BlockMmad`（主计算）和`BlockEpilogue`（尾部处理）；再下沉至红色Tile级算子（`CopyGmToL1`/`CopyL1ToL0A/B`/`TileMmad`/`CopyL0CToGM`/`CopyGmToUb`/`TileOperation`/`CopyUbToGm`），最终落地为灰色基础硬件指令（`DataCopy`、`Mmad`、`add/cast/mul...`）。

**2) 技术结论：** 论证了GEMM算子可按"设备→核函数→Block→Tile→硬件指令"五级层次解耦，各层职责清晰、数据流向明确（GM↔L1↔L0/UB），实现模块化可拼装。

**3) 与文档关系：** 对应文档"算子实现分层模块化设计"章节，直观印证"分层抽象、模板化提取共性、保留差异化扩展"的设计理念。
- `split_k_matmul.png`: # 图文联合解读

**1) 图中内容：** 上方展示A矩阵(M×K，沿K分蓝/绿/粉三段)、B矩阵(K×N，沿K分三段)与C矩阵；箭头下方将B按K拆为三个独立列向量，分别与A对应段相乘得到中间结果0/1/2，最终通过"Reduce Add"归约累加得到C矩阵。

**2) 技术结论：** GEMM计算可沿K维拆分为多个子乘加单元并行执行，各子结果通过归约合并完成全K维规约，体现K维分块流水编排策略。

**3) 与文档关系：** 佐证"算子流水自定义灵活配置"论点——开发者可通过更换组件（如K维分块数与归约方式）灵活定制流水组合，实现自定义算子内核。
