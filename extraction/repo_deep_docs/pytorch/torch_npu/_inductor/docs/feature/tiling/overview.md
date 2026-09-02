# 自动Tiling优化

> 仓 `pytorch` · 路径 `torch_npu/_inductor/docs/feature/tiling/overview.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/pytorch/torch_npu/_inductor/docs/feature/tiling/overview.md

# 自动Tiling优化 — 一体化深度解读

---

## 【定位】

这篇文档描述了 Ascend for PyTorch（TorchNPU）在 Inductor-Ascend 模块中、面向 A5+ 硬件与 PyTorch-v2.9.0 版本所提供的 **"对融合算子自动生成候选 tiling 集合 + 自动寻优"** 能力，重点解决 NPU 上因双层切分（核间 + 核内）导致候选 tiling 配置数量爆炸（原文称 100k+）所带来的寻优开销不可接受问题，同时阐述配套的并行 autotune 与最优配置缓存机制。

---

## 【技术要点】

1. **目标平台与版本**：面向 A5+ 硬件，PyTorch-v2.9.0，作用范围为 Inductor-Ascend 模块内自动生成的融合算子。
2. **覆盖算子类型**：Inductor 中的 "VV（Vector-Vector）融合算子"，包括 pointwise、规约（reduction）、离散访存等不同类别。
3. **NPU 双层切分机制**（与 GPU 关键差异）：
   - 核间切分（inter-core）：控制每个核处理的数据总量，等价于控制发射的逻辑核数；
   - 核内切分（intra-core）：控制单次计算搬运的数据量，即 tiling 大小本身。
   - 这一双层结构是 NPU tiling 复杂度的根源——若仅按 GPU 思路做单层切分，会因发射逻辑核数量过多造成显著硬件调度开销。
4. **候选集合规模问题**：NPU 可选候选 tiling 配置数量 "100k+" 量级，全量寻优时间开销不可接受，因此需要一个"自动 tiling 生成算法"在缩小候选集的同时尽量保留最优 tiling。
5. **寻优加速手段**：对 autotune 寻优过程进行**并行加速**；并对单个融合算子的最优配置提供**缓存**，避免后续重复运行的寻优开销。
6. **Autotune 编译期加速手段**（原文表述）：可使用**多进程多 kernel 并发编译**以及**单 kernel 内部多线程并发编译每个 tiling config** 进行 precompile 阶段的加速。

---

## 【关键机制与数据】

- **两阶段工作流**：
  1. **候选集生成阶段**：对每个融合算子，通过"自动 tiling 生成算法"产生一个规模适中、且尽可能包含最优 tiling 的候选集合；
  2. **最优配置选取阶段**：在候选集合内实测（或基于 profiling）找出性能最优的 tiling 配置；
  3. **结果缓存**：把融合算子对应的最优配置缓存下来，避免后续多次运行的重复寻优。
- **并行化的必要性**：原文指出"一个模型中可能存在成百上千个融合算子，一个融合算子可能有成百上千个 tiling 配置"，若串行执行寻优，整体开销"非常长"——这给出了文档强调并行加速与缓存机制的客观背景。
- **性能数据（原文）**："训练/推理速度提高 10-50%（视操作而定），尤其 GEMM、conv、reduction"——但请注意，此 10-50% 出现在"Tiling 的作用"小节中，是作为 Tiling+Autotune 结合作用的整体收益描述，并非 NPU 专属实测数字。
- **Tile Size 示例（原文）**：`[32, 32]` 是文档给出的典型 tile size 示例，用于说明"每个块的大小需根据矩阵尺寸、寄存器压力和共享内存调优"。
- **Heuristics 候选示例（原文）**：tile sizes 候选 `[16, 32, 64]`、thread blocks 候选 `[128, 256, 512]`，用作缩小搜索空间的预设规则说明。
- **Search Space 缩窄策略（原文）**：通过 heuristics（根据矩阵大小选 tile 等预设规则）缩小候选，再以 profiling 实际运行小基准测试不同配置性能。
- **Backend 兼容性（原文）**：autotune 跨 Triton、CUTLASS、C++ template 等后端间选择最佳，提升跨硬件兼容性。

---

## 【表格解读】

**原文无表格。**

文档全文未出现 markdown 表格或结构化参数表，所有配置示例（如 `[16, 32, 64]`、`[128, 256, 512]`、`[32, 32]`）均以行内文本方式给出。

---

## 【公式解读】

**原文无公式。**

文档未包含 LaTeX 数学公式或伪代码公式。仅在描述 SymPy 符号化索引时，给出了一段示意性代码片段：

```
i0 = tl.program_id(0) * XBLOCK + tl.arange(0, XBLOCK)
```

该片段并非严格数学公式，而是用于说明"用 SymPy 符号表示索引、支持动态形状与 masking（offsets < size）"的写法示例——其中 `XBLOCK` 表示 X 维度的 block 大小，`tl.program_id(0)` 是 Triton 中的程序（block）编号轴 0 的 ID，`tl.arange(0, XBLOCK)` 表示该 block 内 X 维度的偏移序列。

---

## 【关联】

由于文末"内部链接"标注为 **（无）**，文档未显式给出可点击的内部跳转链接；但从正文内容可梳理出如下关联结构：

- **上游模块**：
  - **Inductor**（PyTorch Inductor）：文档所讨论的 tiling / autotune 机制均位于 Inductor 体系内，融合算子由 Inductor 动态生成。
  - **Triton 内核**（GPU 侧）：Inductor 在 GPU 上主要通过 `@triton.jit` 内核使用 `tl.arange` 与 mask 实现 tiling；本文是把这套机制思想迁移、改造到 NPU。
- **本特性在仓内的位置**：`torch_npu/_inductor/docs/feature/tiling/overview.md` —— 表明其属于 **`torch_npu._inductor` 子模块**下、专门描述 tiling 这一**特性（feature）** 的概览（overview）文档。
- **关联算子类别**：pointwise、规约（reduction）、离散访存 —— 这是文档明确点名要被自动 tiling 覆盖的"VV（Vector-Vector）融合算子"子类。
- **关联加速手段（与 Autotune 同位提及）**：
  - **Heuristics**：作为预设规则用于缩小搜索空间；
  - **Profiling**：用于实测各 tiling config 的运行时间；
  - **Precompile 并行加速**：包括多进程多 kernel 并发编译 + 单 kernel 内多线程并发编译每个 tiling config。
- **与"跨后端 autotune"的关联**：Triton、CUTLASS、C++ template 三类后端是文档明确列出的 autotune 适用面。
- **下游使用场景（文档暗示）**：模型中存在成百上千融合算子的场景——即典型的训练/推理图编译阶段，其首次编译耗时会因 autotune 增大，但后续运行通过缓存复用最优 tiling 配置。

---

## 【使用方法】

**原文未涉及**具体的启用方式、配置项、开关命令或 API 调用。

文档通篇为概念性/原理性叙述，仅提及如下间接相关的可调维度（均非可执行开关）：

- **Autotune 级别**：原文提到 Inductor 支持多种 autotune 级别，并以 `max-autotune` 作为示例——"max-autotune 接受长编译时间，换取更高运行时速度"。
- **max-autotune 行为描述**：原文说明在该模式下，"autotune 发生在首次编译，增加时间，但后续运行更快"。
- **缓存机制的存在**：文档语义上承诺了"对融合算子的最优配置需要具有缓存功能"，但**未给出**缓存 key 的构成、缓存生命周期、如何清理或强制重寻优等具体配置方式。
- **并行加速开关**：文档提及"多进程多 kernel 并发编译"与"单 kernel 内多线程并发编译每个 tiling config"，但**未给出**对应环境变量、参数名或默认开关状态。

如需在 A5+ 上实际启用该自动 tiling 优化能力，并控制其并行度、缓存策略或 autotune 级别，需查阅 `torch_npu._inductor` 模块下的其他文档、源码或 README —— 本 overview.md 文档本身**未提供**直接的启用命令或配置项。
