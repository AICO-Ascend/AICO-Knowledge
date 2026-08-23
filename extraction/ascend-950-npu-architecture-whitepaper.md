---
paper_num: "15"
title: "昇腾 950 NPU 架构白皮书"
authors: ""
date: "2026/1/1"
arxiv: "—"
pdf: "papers/ascend-950-npu-architecture-whitepaper.pdf"
slug: "ascend-950-npu-architecture-whitepaper"
tags: []
---

# 昇腾 950 NPU 架构白皮书

> [!abstract] 摘要（原文）
> 1\. ✨ 华为昇腾950系列芯片（昇腾950PR和昇腾950DT）是面向下一代人工智能应用的旗舰计算芯片，搭载自研第三代达芬奇架构，旨在赋能大模型全生命周期及AIGC、智能推荐等多元化场景。 2. ⚡️ 该系列芯片在算力密度、存储带宽和互联拓扑上实现跨越式升级，通过引入NDDMA、SIMD/SIMT混合编程和原生支持MXFP4/MXFP8/HiF8等格式（MXFP4张量浮点峰值算力提升高达4倍），显著提升了Transformer类模型的训练与推理效率。 3. 💾 昇腾950系列配备大容量高速片上内存（PR最高128GB/1.6TB/s，DT最高144GB/4TB/s）和128MB L2 Cache，并采用灵衢（Unified Bus）互联总线，支持URMA、UB Memory、PCIe 5.0及UBoE等先进协议，可构建超128K卡大规模集群。

## 元信息
- **发表日期**: 2026/1/1
- **作者**: —
- **arXiv**: —
- **本地 PDF**: `papers/ascend-950-npu-architecture-whitepaper.pdf`
- **页数**: 40

## 图表（原文 caption + 页码）

### Figure 301 (p.12) ⭐深度解读
![[assets/crops/ascend-950-npu-architecture-whitepaper-fig301.png]]
*整页渲染: ![[assets/ascend-950-npu-architecture-whitepaper-p12.png]]*
> [!quote] caption
> 昇腾950 芯片架构示意图

> [!tip] 技术解读（多模态）
> # Figure Description: Ascend 950 Chip Architecture (图3-1)

## Architecture / Components / Data Flow

The schematic depicts a **multi-die chiplet** layout with a symmetric, two-AI-Die structure flanked by two IO Dies:

- **Two central AI Dies** (mirror-symmetric), each containing:
  - A large central **AI Core** tile
  - Two **Linx816 CPU** cores (left & right flanks)
  - **L2 Cache** rails (top & bottom)
  - **DVPP** (Digital Video Pre-Processing) units on outer edges
  - **D2D** (Die-to-Die) links on the inner edge facing the peer AI Die, plus **STARS** interconnect bridges between the two AI Dies
  - **Memory Interface** controllers on top/bottom, each feeding external **Global Memory** (HBM)
- **Two IO Dies** (leftmost & rightmost) hosting **PCIe5.0 CTRL**, **Security Core**, **UB CTRL**, additional D2D links, and **Hilink** I/O ports at the bottom
- **Data flow**: Compute → AI Core ↔ Linx816 CPU/L2 Cache ↔ Memory Interface ↔ Global Memory; die-to-die traffic flows via D2D/STARS between AI Dies and IO Dies; external connectivity via PCIe5.0 and Hilink.

## Key Technical Takeaway

The Ascend 950 uses a **2 AI-Die + 2 IO-Die chiplet design** unified via high-speed **D2D links** into a single **UMA (Unified Memory Access)** domain — pairing in-package HBM with the new **CCU** and **Cube-Vector/MXFP8/MXFP4** compute paths to deliver ~**1.5–2× per-core LLM inference gains** over the prior generation while scaling super-nodes to 8K cards (128K-card clusters).

## Verbatim Caption

**图3-1 昇腾 950 芯片架构示意图**

### Figure 401 (p.17) ⭐深度解读
![[assets/ascend-950-npu-architecture-whitepaper-p17.png]]
> [!quote] caption
> AI Core 架构及各层级SRAM 示意图

> [!tip] 技术解读（多模态）
> **Architecture Description:**

The figure depicts a three-column AI Core architecture under a top-level **Bus Interface**:

- **Middle column (control & compute hub):** Scalar 0 → **L1 buffer (512KB)** → split into **L0A (64KB) + L0B (64KB)** inputs → fed into the **Cube Core (16×16×16 FP16 matrix multiply)** → output written to **L0C (256KB)**.
- **Left column:** Scalar 2 controls **Vector Core 1** (two 64×64 FP32 / 128×128 FP16 lanes) backed by **UB1 (256KB)** and a **Register File**.
- **Right column:** Scalar 1 controls the mirror **Vector Core 0** with **UB0 (256KB)** and its own Register File.
- **Data flow:** Bus Interface → L1 → L0A/L0B → Cube Core → L0C → back to UB0/UB1 or L1; Vector Cores stream data between Unified Buffers and Register Files in parallel.

**Key takeaway (≈90 words):** The design decouples *matric-heavy* workloads (Cube Core with split input buffers L0A/L0B and accumulator L0C) from *vector/elementwise* workloads (dual Vector Cores with symmetric UBs). This separation enables concurrent execution — the Cube handles GEMM/FlashAttention while Vector Cores handle non-linear ops — sharing the L1 tier and bus to maximize throughput and memory reuse.

**Caption (verbatim):** 图4-1 AI Core 架构及各层级 SRAM 示意图

### Figure 402 (p.18) ⭐深度解读
![[assets/ascend-950-npu-architecture-whitepaper-p18.png]]
> [!quote] caption
> Cube Core 处理架构示意图

> [!tip] 技术解读（多模态）
> **Figure 4-2 (Cube Core Architecture):** A linear chain of multipliers (×) receives inputs x₀…x_{k-1} horizontally and y₀…y_{k-1} vertically (green arrows). Each multiplier's product feeds a shared Σ (accumulator), whose output feeds a 4×4 grid of PE_s (Processing Elements) — the cubic compute array.

**Figure 4-3 (Supported Numerical Precisions):** Bit-layout diagrams show supported formats grouped by width: **32-bit** (FP32: 1/8/23, TF32: 1/8/10), **16-bit** (BF16: 1/8/7, FP16: 1/5/10), **8-bit** (HiFi8: dynamic, FP8-E5M2: 1/5/2, FP8-E4M3: 1/4/3), and **4-bit** (FP4: 1/2/1). Legend: SIGN (1 bit) / EXPONENT / MANTISSA.

**Key takeaway:** The Cube Core pairs a systolic MAC pipeline with a configurable PE array and natively scales precision from FP32 down to FP4, letting users trade accuracy for throughput/bandwidth within the same hardware.

**Captions verbatim:**
- 图4-2 Cube Core 处理架构示意图
- 图4-3 Cube Core 支持的数值精度示意

### Figure 403 (p.18) ⭐深度解读
![[assets/crops/ascend-950-npu-architecture-whitepaper-fig403.png]]
*整页渲染: ![[assets/ascend-950-npu-architecture-whitepaper-p18.png]]*
> [!quote] caption
> Cube Core 支持的数值精度示意

> [!tip] 技术解读（多模态）
> **Figure 4-2 (Cube Core Architecture):** A linear chain of multipliers (×) receives inputs x₀…x_{k-1} horizontally and y₀…y_{k-1} vertically (green arrows). Each multiplier's product feeds a shared Σ (accumulator), whose output feeds a 4×4 grid of PE_s (Processing Elements) — the cubic compute array.

**Figure 4-3 (Supported Numerical Precisions):** Bit-layout diagrams show supported formats grouped by width: **32-bit** (FP32: 1/8/23, TF32: 1/8/10), **16-bit** (BF16: 1/8/7, FP16: 1/5/10), **8-bit** (HiFi8: dynamic, FP8-E5M2: 1/5/2, FP8-E4M3: 1/4/3), and **4-bit** (FP4: 1/2/1). Legend: SIGN (1 bit) / EXPONENT / MANTISSA.

**Key takeaway:** The Cube Core pairs a systolic MAC pipeline with a configurable PE array and natively scales precision from FP32 down to FP4, letting users trade accuracy for throughput/bandwidth within the same hardware.

**Captions verbatim:**
- 图4-2 Cube Core 处理架构示意图
- 图4-3 Cube Core 支持的数值精度示意

### Figure 404 (p.19) ⭐深度解读
![[assets/crops/ascend-950-npu-architecture-whitepaper-fig404.png]]
*整页渲染: ![[assets/ascend-950-npu-architecture-whitepaper-p19.png]]*
> [!quote] caption
> HiF8 数值精度

> [!tip] 技术解读（多模态）
> **Figure Description:**

The figure (图4-4 HiF8 数值精度) illustrates the bit-layout of the HiF8 floating-point format using two tables.

**Components / Data Flow:**
- **HiF8 Normal encoding:** Formula `X = (-1)^S * 2^E * 1.M`. An 8-bit word is partitioned as: 1 sign bit (S) + a variable-length exponent prefix (Dot: 0–4) + remaining exponent bits (E, with 1 hidden bit, shown in red) + mantissa bits (M). The Dot field doubles the exponent range per increment (E=0, ±1, ±[2,3], ±[4,7], ±[8,15]).
- **HiF8 Denormal encoding:** Formula `X = (-1)^S * 2^(M−23) * 1.0`, extending the range down to E=[−22, −16] via a Subnormal design.
- Legend: Dot = variable-length prefix (also flags Denormal); 阶码 = unbiased code, 1-bit hidden value not stored (red); SE = Sign of Exponent.

**Key Technical Takeaway (≤120 words):**
HiF8 uses a **variable-length exponent prefix** (Dot, 0–4) to signal how many exponent bits follow, creating a tapered precision layout suited to AI data distributions. Exponents use **unbiased code** with a hidden 1-bit (saving one bit per code) so that exponent ranges of different widths do not overlap, achieving redundancy-free encoding. Combined with a Subnormal-number design, the total exponent space is extended from [−15, 15] to **[−22, 15]** — 38 unique values — approaching FP16's 40 values while keeping an 8-bit width and eliminating the need for an 8-bit MX scaling factor used in MXFP8.

**Caption (verbatim):**

图4-4 HiF8 数值精度

HiF8 Normal编码 : X = (-1)^S * 2^E * 1.M          阶码值

Dot = 0    | S | 0 | 0 | 0 | 1 | 0 | M | M | M | E = 0
Dot = 1    | S | 0 | 0 | 1 | SE | 1 | M | M | M | E = ±1
Dot = 2    | S | 0 | 1 | SE | 1 | E | M | M | M | E = ±[2, 3]
Dot = 3    | S | 1 | 0 | SE | 1 | E | E | M | M | E = ±[4, 7]
Dot = 4    | S | 1 | 1 | SE | 1 | E | E | E | M | E = ±[8, 15]

HiF8 Denormal编码 : X = (-1)^S * 2^(M - 23) * 1.0

Dot = Denormal    | S | 0 | 0 | 0 | 0 | M | M | M |          E = [-22, -16]

说明：
• 点位域Dot：变长前缀码，编码阶码存储的位宽，和Denormal标志
• 阶码：原码编码，含1-bit隐藏位不存储(红色数字表示)
• SE: Sign of Exponent

1. HiF8 利用变长前缀码编码的点位域 Dot，显式指示阶码存储的位宽和 Denormal 标志，实现符合 AI 数据分布特征的锥形精度格式。
2. 同时阶码采用原码编码，并隐藏了 1 比特固定值不存储，确保了不同位宽的阶码表达范围不重复，进而实现无冗余编码。
3. 最后通过特殊的浮点 Subnormal number 设计，将综合阶码范围从[-15, 15]提升到了[-22, 15]共 38 个阶码，接近 FP16 的 40 个综合阶码值表达。

### Figure 405 (p.21) ⭐深度解读
![[assets/crops/ascend-950-npu-architecture-whitepaper-fig405.png]]
*整页渲染: ![[assets/ascend-950-npu-architecture-whitepaper-p21.png]]*
> [!quote] caption
> Vector Core 架构示意图

> [!tip] 技术解读（多模态）
> **Architecture Overview**

The Vector Core diagram shows a unified core feeding two execution modes from shared infrastructure.

**Left (Core Front-end):** Scalar Unit, Async Function Queues tagged with execution type (SIMD/SIMT/NULL), DMA Unit, Vector Unit (SIMD/SIMT), Vector Cache/Buffer, Bus Interface, and Global Memory.

**Right-Top — SIMD Mode:** I Cache → Program Sequence → QoO Dispatch → Vector Cache/Uniform Buffer (N banks + Cache Controller + Coalescing Unit) → Vector Load/Store Unit → Vector Register File (Lanes 0…VL-1) → Vector Execution Unit.

**Right-Bottom — SIMT Mode:** I Cache → Program Sequence → Warp Scheduler → In-order Dispatch → Shared Vector Cache/Uniform Buffer → SIMT Load/Store Unit → SIMT Register File (Lanes 0…warp_size-1) → Vector Execution Unit.

Both modes reuse the **same Vector Cache/Buffer banks and Vector Execution Unit**, differing only in front-end scheduling (QoO vs. Warp) and register layout.

**Key Technical Takeaway:** SIMD/SIMT heterogeneity is achieved by sharing the memory subsystem and execution backend while swapping the dispatch logic — allowing per-VF mode selection at compile/launch time for performance–portability trade-offs.

**Caption (verbatim):** 图4-5 Vector Core 架构示意图

### Figure 406 (p.22) ⭐深度解读
![[assets/crops/ascend-950-npu-architecture-whitepaper-fig406.png]]
*整页渲染: ![[assets/ascend-950-npu-architecture-whitepaper-p22.png]]*
> [!quote] caption
> AI Core Cube-Vector 融合示意图

> [!tip] 技术解读（多模态）
> **Description:**
The diagram depicts an AI Core with Cube-Vector fusion architecture. Two **Vector Cores** (left: Vector Core 1 with UB1; right: Vector Core 0 with UB0) flank a central **Cube Core** block. The Cube Core sits between **L0A/L0B** buffers (above) and the **L0C** buffer (below), with an **L1** buffer on top. Bidirectional arrows show direct data pathways: UB1 � L0A and L0B ↔ UB0 enable Vector-to-Cube operand sharing, while L0C feeds results back to the Vector cores via UB0/UB1. **Bus Interfaces** on top and bottom handle external traffic. Each Vector Core has its own Register File.

**Key takeaway:** Direct UB↔L0A/L0B/L0C coupling bypasses L2 traffic, enabling efficient Cube-Vector fusion (e.g., for FlashAttention) while supporting inline data-layout/precision conversions to boost end-to-end throughput and energy efficiency.

**Caption (verbatim):** 图4-6 AI Core Cube-Vector 融合示意图

### Figure 407 (p.23) ⭐深度解读
![[assets/ascend-950-npu-architecture-whitepaper-p23.png]]
> [!quote] caption
> NDDMA 指令

> [!tip] 技术解读（多模态）
> # Figure Description: 图4-7 NDDMA 指令

## Architecture / Components / Data Flow

The figure illustrates a two-stage memory transformation:

**Left – Global Memory (32-row array):** Data elements (1–24) are scattered sparsely across non-contiguous rows (e.g., row 0 holds {1,13}, row 2 holds {5,17}, row 4 holds {9,21}, row 11 holds {10,22}, row 21 holds {4}, row 31 holds {24}). Values are color-coded by original row group (teal, blue, orange, gray) and arranged in a column-wise stride pattern.

**Center – NDDMA arrow:** A single hardware-level DMA operation.

**Right – Unified Buffer:** The same values emerge densely packed in sequential order (1, 2, 3, 5, 6, 7, 9, 10, 11, 13, 14, 15, 17, 18, 19, 21, 22, 23, …), now contiguous and stride-free.

## Key Technical Takeaway
NDDMA fuses data movement **and** reordering/transposition in one instruction (up to 5 dimensions). Its internal cache exploits locality, collapsing many small element-wise reads into efficient 128-byte burst reads — drastically improving effective memory bandwidth and reducing programming complexity.

---

## Caption (verbatim)
**图4-7 NDDMA 指令**

### Figure 408 (p.24) ⭐深度解读
![[assets/ascend-950-npu-architecture-whitepaper-p24.png]]
> [!quote] caption
> 昇腾950 新同步机制代码示例

> [!tip] 技术解读（多模态）
> **Figure 4-8 Description:**

The figure presents a side-by-side comparison of two synchronization code patterns used in the Ascend 950 NPU pipeline, with an arrow indicating the evolution from the legacy mechanism to the new one.

**Left block — 基于set_flag/wait_flag (flag-based synchronization):**
A 100-iteration loop uses explicit flag-setting primitives to coordinate the MTE2 (memory transfer) and Vector units. Each iteration must: wait for the upstream Vector unit's flag, execute MTE2, set/clear its own flag, then wait for MTE2's flag before running Vector(), and finally emit the next producer flag.

**Right block — 基于BufferID (BufferID-based synchronization):**
The same 100-iteration pipeline is expressed through explicit buffer acquisition/release. Each iteration calls `get_buf`/`rel_buf` on MTE2 and Vector pipeline stages in lockstep — acquire MTE2 buffer, transfer, release; acquire Vector buffer, compute, release — replacing all flag operations with buffer-ownership semantics.

**Key technical takeaway:**
The new BufferID API replaces four flag operations per stage per iteration with two `get_buf`/`rel_buf` pairs, removing the `if i>0` boundary checks and the trailing `if i<99` tail condition. This eliminates edge-iteration corner cases, shortens instruction sequences, and exposes pipeline buffer occupancy to the runtime for improved scheduling and overlap.

**Caption (verbatim):**
图4-8 昇腾950新同步机制代码示例

### Figure 409 (p.25) ⭐深度解读
![[assets/crops/ascend-950-npu-architecture-whitepaper-fig409.png]]
*整页渲染: ![[assets/ascend-950-npu-architecture-whitepaper-p25.png]]*
> [!quote] caption
> 昇腾950 内存层次示意图

> [!tip] 技术解读（多模态）
> ## Description

**Architecture/Components:**
The diagram shows a **two-Die structure** (Die 0 and Die 1), each containing:
- **AI Cores**: composed of AIC (with L1, L0A, L0B, L0C buffers) and AIV (with UB — Unified Buffer)
- **AI CPUs**: each with CPU L1 and CPU L2 caches

**Data Flow (bottom-up hierarchy):**
L0A/L0B/L0C, L1, UB → **L2 Cache** (serves AIC/AIV) → **Directory (Cache Coherence)** → **Global Memory**
CPU L1/L2 → **L3 Cache** (serves AI CPUs) → Directory → Global Memory

---

## Key Technical Takeaway (≤120 words)

The Ascend 950 implements a **heterogeneous, multi-tier memory hierarchy** that decouples AI accelerator (AIC/AIV) from general-purpose CPU memory paths. AIC/AIV accesses flow through dedicated L2 Cache optimized for tensor/matrix operations, while AI CPUs use their own L3 Cache for scalar control logic — both unified by a **Directory-based cache coherence** layer above Global Memory. Local Memory buffers (L1, L0A/L0B/L0C, UB) inside each AI Core minimize high-bandwidth on-chip memory traffic. This split-path design with cache coherence enables **parallel AI compute and control without contention**, while keeping global data consistent across dies.

---

## Caption (Verbatim)

**图4-9 昇腾950内存层次示意图**

### Figure 410 (p.27) ⭐深度解读
![[assets/ascend-950-npu-architecture-whitepaper-p27.png]]
> [!quote] caption
> Non-allocate（L2 hint）典型应用场景示意图

> [!tip] 技术解读（多模态）
> ## Main Figure Description (Figure 4-11)

**Architecture & Components:**
- **STARS container** holds an array of **Task** slots, alongside sidecar features: **Notify Sync**, **Conds**, **Profiling**, and **Fusion**. A **Sched** bar sits beneath, dispatching tasks to two interconnect fabrics:
  - **HSCB** → **AIV**, **AIC** (compute engines)
  - **NoC** → **UB DMA**, **SDMA**, **CCU**, **CPU**, **DVPP** (data-movement & general engines)

**Data Flow:** Tasks are queued in STARS → the scheduler (Sched) fans them out through HSCB/NoC to heterogeneous engines, with Notify Sync/Conds orchestrating dependencies and Profiling/Fusion collecting runtime telemetry.

**Key Takeaway:** STARS2.0 centralizes whole-chip task and resource orchestration, unifying compute (AIC/AIV/CPU/DVPP) and DMA engines (SDMA/UB/CCU) under one scheduler to enable efficient software–hardware co-scheduling with top-down profiling.

## Caption (verbatim)
**图4-11 STARS2.0 架构示意图**

### Figure 411 (p.27) ⭐深度解读
![[assets/crops/ascend-950-npu-architecture-whitepaper-fig411.png]]
*整页渲染: ![[assets/ascend-950-npu-architecture-whitepaper-p27.png]]*
> [!quote] caption
> STARS2.0 架构示意图

> [!tip] 技术解读（多模态）
> ## Main Figure Description (Figure 4-11)

**Architecture & Components:**
- **STARS container** holds an array of **Task** slots, alongside sidecar features: **Notify Sync**, **Conds**, **Profiling**, and **Fusion**. A **Sched** bar sits beneath, dispatching tasks to two interconnect fabrics:
  - **HSCB** → **AIV**, **AIC** (compute engines)
  - **NoC** → **UB DMA**, **SDMA**, **CCU**, **CPU**, **DVPP** (data-movement & general engines)

**Data Flow:** Tasks are queued in STARS → the scheduler (Sched) fans them out through HSCB/NoC to heterogeneous engines, with Notify Sync/Conds orchestrating dependencies and Profiling/Fusion collecting runtime telemetry.

**Key Takeaway:** STARS2.0 centralizes whole-chip task and resource orchestration, unifying compute (AIC/AIV/CPU/DVPP) and DMA engines (SDMA/UB/CCU) under one scheduler to enable efficient software–hardware co-scheduling with top-down profiling.

## Caption (verbatim)
**图4-11 STARS2.0 架构示意图**

### Figure 412 (p.31) ⭐深度解读
![[assets/crops/ascend-950-npu-architecture-whitepaper-fig412.png]]
*整页渲染: ![[assets/ascend-950-npu-architecture-whitepaper-p31.png]]*
> [!quote] caption
> URMA 异步访存通信的过程示意图

> [!tip] 技术解读（多模态）
> **Architecture/Data Flow:**
The diagram illustrates URMA (Ultra-Remote Memory Access) asynchronous communication between two nodes. On the left (local) node: **Core** triggers a *Doorbell* signal to the **URMA** engine, which fetches data from local **Memory** via the local **UMMU** (Unified Memory Management Unit), then distributes it across multiple **Ports** to the remote node. On the right (remote) node: incoming **Ports** feed into the remote **UMMU**, which performs translation and writes data into remote **Memory**.

**Key Takeaway:**
UMMU sits in the critical path on both sides, providing VA→PA address translation and access permission control for cross-node memory access—ensuring secure, virtualized remote memory operations while enabling multi-port parallel data transfer.

**Caption (verbatim):**
图4-12 URMA 异步访存通信的过程示意图

### Figure 413 (p.32) ⭐深度解读
![[assets/crops/ascend-950-npu-architecture-whitepaper-fig413.png]]
*整页渲染: ![[assets/ascend-950-npu-architecture-whitepaper-p32.png]]*
> [!quote] caption
> UB Memory 同步访存语义地址通信过程示意图

> [!tip] 技术解读（多模态）
> ## Figure Description

**Architecture/Components:**
The figure (图4-13) depicts two chips in a multi-chip system:

- **Left chip (source):** Contains a `Core` → `UB Mem Decoder` → multiple `Port` modules, with local `Memory` below.
- **Right chip (destination):** Contains multiple `Port` modules feeding into a `UMMU` (Unified Memory Management Unit), with local `Memory` below.

**Data Flow (orange arrow):**
1. Core issues an access → 
2. UB Mem Decoder routes the operation to one of the outgoing Ports → 
3. Operation crosses the chip-to-chip interconnect → 
4. A Port on the destination chip receives it → 
5. UMMU performs **address translation + permission checking** → 
6. Direct access to the remote chip's Memory.

**Key Technical Takeaway:**
UB Memory relies on hardware-level **semantic address translation via UMMU** at the destination, enabling the source Core to directly access remote memory without software intervention. This supports synchronous Write/Read plus atomic operations (AtomicStore, AtomicLoad, AtomicSwap, AtomicCompareAndSwap), preserving memory consistency across chips while keeping coherence overhead low.

## Caption (verbatim)

**图4-13 UB Memory 同步访存语义地址通信过程示意图**

### Figure 414 (p.33) ⭐深度解读
![[assets/ascend-950-npu-architecture-whitepaper-p33.png]]
> [!quote] caption
> CCU 架构示意图

> [!tip] 技术解读（多模态）
> ## Figure Description (Architecture / Components / Data Flow)

The CCU (Collective Communication Unit) architecture is a three-tier hierarchical design. **Top tier — CCUM (Management):** The Mission Call Interface feeds the Mission Commander, which routes instructions through the Instruction Implementation Unit to either a Reduce Call Interface or a URMA Call Interface. **Middle tier — CCUA (Agents):** Multiple CCUA instances each integrate Memory Slices (storage) and a Reduce Unit (computation). **Bottom tier — I/O:** The URMA module bridges the URMA Call Interface to an array of Ports for remote transfers. Data flow splits at the dispatcher: Reduce tasks go down to CCUA compute units, while URMA tasks go through the URMA block to Ports. **Key takeaway:** Hardware-managed dispatch cleanly separates local reduction from remote RDMA-style data movement, with CCUA agents acting as unified compute+storage endpoints.

## Caption (Verbatim)

图4-14 CCU 架构示意图

集合通信软件通过 CCU Management（CCUM）中的 Mission 任务的入口进行软件编程，硬件完成指令的解析和处理，并根据指令判断当前是执行 Reduce 计算还是 URMA 搬运。CCU Agent（CCUA）中集成了 MemorySlice 用作数据存储，集成了 Reduce Unit 用作数据计算。

如果是 URMA 搬运则调用 URMA 执行数据搬移，可完成远端节点到本端节点 DRAM 或 MemorySlice 之间的灵活数据搬运。

如果是 Reduce 则调用 CCUA 的计算单元进行计算。

CCU 完成集合通信任务后通过 Mission 任务的编程接口上报任务完成状态。

### Figure 415 (p.34) ⭐深度解读
![[assets/ascend-950-npu-architecture-whitepaper-p34.png]]
> [!quote] caption
> UB On Chip Switch 转发示意图

> [!tip] 技术解读（多模态）
> # Figure Description: UB On-Chip Switch Forwarding Diagram

**Architecture / Components (top-to-bottom):**
- **Network On Chip (NoC)** — purple block at top representing the on-chip interconnect fabric
- **Routing Table** — green band in the middle, shared across all ports
- **Ports** — 9 × x4 ports (blue blocks) at the bottom, each connected upward to both the routing table and the NoC

**Data Flow:**
Solid vertical lines carry traffic between ports and the routing table. Dashed arrows depict a forwarding path: a packet enters an ingress port → the routing table determines it is **not** destined for the local chip → it is forwarded through the NoC → it exits from a different egress port. The "…" between ports indicates the remaining (unshown) ports in the array.

---

## Key Technical Takeaway (≤120 words)

The UB on-chip switch performs **local forwarding entirely within the IO DIE**, without ever consuming compute DIE resources or DRAM bandwidth. Traffic arriving at any of the 9 × x4 ports is classified by a shared routing table; non-local traffic is switched across ports via the Network-on-Chip and emitted directly from the determined egress port. This effectively turns the IO DIE into an embedded Layer-2-style switch fabric, enabling mixed deployment of injection and pass-through traffic and giving operators flexible, low-cost topology options (e.g., leaf-spine, ring, or hybrid) for service chaining without burdening compute dies.

---

## Verbatim Caption Transcription

**图4-15 UB On Chip Switch 转发示意图**

本芯片支持单 IO DIE 内 9 个 x4 Port 之间进行流量转发。从每个端口进入的流量在查询路由表后如判断该流量并非本芯片流量且判断得到转发的出端口，此时该流量会经过片上互联网络（Network on Chip，即 NoC）转发至出口端口送出。此转发流量不会进入计算 DIE，也不会占用 DRAM 带宽，在 IO DIE 上即完成数据转发。

本芯片支持注入流量和转发流量的混合部署，提供更多样的组网和业务规划可能性。

### Figure 416 (p.35) ⭐深度解读
![[assets/ascend-950-npu-architecture-whitepaper-p35.png]]
> [!quote] caption
> PCIe 5.0 架构示意图

> [!tip] 技术解读（多模态）
> **Architecture / Components / Data Flow**

The figure shows the PCIe 5.0 subsystem inside the Ascend 950 SoC, bridged to the on-chip **System Bus** via a bidirectional link. The **PCIe Gen5x16** controller is structured as a stacked protocol stack: an **Application** layer (top, hosting embedded **MCTP** and **DMA** accelerators) sits above the standard **Transaction Layer**, **DataLink Layer**, and a 16-lane **Physical Layer**. A separate **Serdes** block sits beneath the controller and handles the physical signaling to the off-chip lanes.

Data flows from the System Bus down through the four-layer PCIe stack, out the x16 Physical Layer into the Serdes, and across the link; inbound traffic follows the reverse path, with DMA/MCTP accelerating host-to-device transfers at the application layer.

**Key Technical Takeaway:** Backward compatibility with Gen4/3/2/1, configurable link widths (x16/x8/x4/x2), dual EP/RC roles (statically selected), and integrated DMA + MCTP accelerators make this a flexible, host-agnostic Gen5 endpoint/root-complex block.

**Caption (verbatim):** 图4-16 PCIe 5.0 架构示意图

### Figure 417 (p.36) ⭐深度解读
![[assets/crops/ascend-950-npu-architecture-whitepaper-fig417.png]]
*整页渲染: ![[assets/ascend-950-npu-architecture-whitepaper-p36.png]]*
> [!quote] caption
> 昇腾950 的一种超节点示意图

> [!tip] 技术解读（多模态）
> ## Main Figure Description (Figure 4-17)

**Architecture / Components:**
- **Top tier (Spine):** A row of UB Switches (with "…" indicating scalability)
- **Middle tier (Leaf):** Two switch groups, each serving a pod/rack
- **Bottom tier (Compute):** Multiple Ascend 950 chips per group, fully meshed
- Interconnects form a **two-level fat-tree / Clos-like topology** with full-mesh links between Ascend 950 chips within each group, fanning up through leaf switches to spine switches

**Data flow:** Ascend 950 ↔ (full mesh) ↔ Leaf Switch ↔ Spine Switch ↔ Leaf Switch (other pod) ↔ Ascend 950

**Key technical takeaway (≤120 words):**
Ascend 950 chips leverage the **UB (Unified Bus) interconnect protocol** to compose a hierarchical super-node. By chaining UB Switches, the architecture scales to K-level super-nodes while enabling high-bandwidth, low-latency intra-super-node communication. The topology is flexible — supporting Full Mesh, Clos, or hybrid layouts — allowing the same silicon to be re-deployed across different cluster shapes. Crucially, UB is not just a chip-to-chip link but a hierarchical switching fabric: every Ascend 950 can reach any peer through at most two switch hops, making the super-node behave like a single logical compute domain.

**Verbatim caption:**
> 图4-17 昇腾950的一种超节点示意图

### Figure 418 (p.36) ⭐深度解读
![[assets/crops/ascend-950-npu-architecture-whitepaper-fig418.png]]
*整页渲染: ![[assets/ascend-950-npu-architecture-whitepaper-p36.png]]*
> [!quote] caption
> 昇腾950 访问CPU 超大内存池示意图

> [!tip] 技术解读（多模态）
> ## Main Figure Description (Figure 4-17)

**Architecture / Components:**
- **Top tier (Spine):** A row of UB Switches (with "…" indicating scalability)
- **Middle tier (Leaf):** Two switch groups, each serving a pod/rack
- **Bottom tier (Compute):** Multiple Ascend 950 chips per group, fully meshed
- Interconnects form a **two-level fat-tree / Clos-like topology** with full-mesh links between Ascend 950 chips within each group, fanning up through leaf switches to spine switches

**Data flow:** Ascend 950 ↔ (full mesh) ↔ Leaf Switch ↔ Spine Switch ↔ Leaf Switch (other pod) ↔ Ascend 950

**Key technical takeaway (≤120 words):**
Ascend 950 chips leverage the **UB (Unified Bus) interconnect protocol** to compose a hierarchical super-node. By chaining UB Switches, the architecture scales to K-level super-nodes while enabling high-bandwidth, low-latency intra-super-node communication. The topology is flexible — supporting Full Mesh, Clos, or hybrid layouts — allowing the same silicon to be re-deployed across different cluster shapes. Crucially, UB is not just a chip-to-chip link but a hierarchical switching fabric: every Ascend 950 can reach any peer through at most two switch hops, making the super-node behave like a single logical compute domain.

**Verbatim caption:**
> 图4-17 昇腾950的一种超节点示意图

### Figure 419 (p.37) ⭐深度解读
![[assets/ascend-950-npu-architecture-whitepaper-p37.png]]
> [!quote] caption
> 昇腾950 直接访问超大存储资源池示意图

> [!tip] 技术解读（多模态）
> **Architecture / Data Flow Description**

The diagram illustrates a fat-tree-style topology with a central Switch (depicted as a stacked unit) fanning out to two Racks. The **left Rack** is a compute pod containing two stacked server groups, each pairing CPUs with **Ascend950** AI accelerator chips. The **right Rack** is a dedicated storage pod built from a 5×4 grid of Storage nodes. The Switch provides a single high-bandwidth interconnect plane that lets Ascend950 chips reach the entire storage pool directly.

**Key Technical Takeaway:** Native UB (Unified Bus) ports on the Ascend950 enable direct, protocol-translation-free access to a shared storage pool, eliminating intermediate storage gateway overhead and delivering high bandwidth at lower cost.

---

**Verbatim Caption / Surrounding Text**

> **4.7.3 昇腾超节点与超大存储资源池组网**
>
> 图4-19 昇腾950直接访问超大存储资源池示意图
>
> 基于UB 互连可以构建超大存储资源池，昇腾 950 Rack/Pod 的计算芯片可以通过 UB 端口直接访问该超大存储资源池，不需要中间的存储协议转换开销，从而实现高带宽和低成本的存储资源访问。

### Figure 420 (p.38) ⭐深度解读
![[assets/ascend-950-npu-architecture-whitepaper-p38.png]]
> [!quote] caption
> 昇腾超节点基于UB Switch 转换为以太网与以太世界互通示意图

> [!tip] 技术解读（多模态）
> **Architecture & Data Flow**
The figure illustrates an Ascend super-node bridging the UB (Unified Bus) fabric with the external Ethernet world. Two external **Ethernet Switches** connect downward via ETH links in a cross-redundant topology to two **UB Switches** enclosed within the super-node boundary. Each UB Switch exposes both ETH (uplink) and UB (downlink) ports. Below, multiple **Ascend950** processors form a fully-meshed UB network — each chip links to both UB Switches and interconnects with every other Ascend950 over UB. Data flows upward: Ascend950 ↔ UB Switch � Ethernet Switch, with cross-links providing failover.

**Key Technical Takeaway:** The UB Switch natively translates UB ↔ Ethernet, enabling seamless integration of an Ascend super-node into existing data-center Ethernet fabrics **without extra gateway hardware**, lowering cost and operational complexity.

**Caption (verbatim):**
图4-20 昇腾超节点基于UB Switch转换为以太网与以太世界互通示意图

### Figure 421 (p.39) ⭐深度解读
![[assets/ascend-950-npu-architecture-whitepaper-p39.png]]
> [!quote] caption
> 昇腾芯片支持以太网与以太世界互通示意图

> [!tip] 技术解读（多模态）
> ## Description

**Architecture / Data Flow:**
- **Top tier:** Two external *Ethernet Switches* (industry-standard).
- **Middle tier (server box):** Two internal *Ethernet Switches* with ETH ports, cross-connected to the top switches for redundancy.
- **Bottom tier:** A row of *Ascend950* AI accelerator chips, each equipped with an ETH port and linked to both middle-layer switches (full mesh) via ETH.
- **Inter-chip:** Ascend950 chips are tied together by a green **UB** (Unified Bus) ring/bus for chip-to-chip communication.

**Key Takeaway:** Ascend 950 leverages **UBoE (UB-over-Ethernet)**, allowing it to plug directly into standard off-the-shelf Ethernet switches — eliminating proprietary fabric hardware and enabling seamless interop with the wider Ethernet ecosystem.

## Caption (verbatim)
**图4-21 昇腾芯片支持以太网与以太世界互通示意图**

## 表格（裁剪图 + caption，可直接插入报告）

### Table 101 (p.5) ⭐深度解读
![[assets/crops/ascend-950-npu-architecture-whitepaper-tab101.png]]
> [!quote] caption
> 关键术语

> [!tip] 表格解读（多模态）
> **Note:** The provided image is not a figure (architecture/components/data flow diagram) — it is a glossary table titled **表1-1 关键术语** (Table 1-1 Key Terms). There is no figure to describe for architecture or data flow. Below is the requested verbatim transcription of the caption and full table content.

**Caption / Title (verbatim):**
**表1-1 关键术语**

**Column headers (verbatim):** 术语 | 描述

**Content (verbatim):**

| 术语 | 描述 |
|---|---|
| AIC | AI Cube Core。在 AI Core 分离架构下，一组 Cube Core 和 Vector Core 组合中的 Cube Core。 |
| AIGC | Artificial Intelligence Generated Content，人工智能生成内容，指利用深度学习模型（如 GPT、Diffusion Models）自动生成文本、图像、音频、视频等内容的技术。 |
| AIV | AI Vector Core。在 AI Core 分离架构下，一组 Cube Core 和 Vector Core 组合中的 Vector Core。 |
| AI CPU | 芯片内的自研 ARM 架构 CPU 内核，在昇腾 950 芯片中指自研 Linx816 CPU Core。 |
| AI Die | 昇腾 950PR 芯片和昇腾 950DT 芯片中的计算 Die。 |
| CANN | Compute Architecture for Neural Networks，昇腾异构计算架构软件栈。 |
| Clos | Clos 组网是一种基于多级交换的无阻塞网络架构，主要用于构建高性能、高扩展性的数据中心网络。其核心特点是通过多级互连和全连接拓扑实现任意节点间的无阻塞通信，同时支持水平扩展和成本优化。 |
| CMO | Cache Maintenance Operations，通过 SDMA 实现的 L2 Cache 管理机制。 |
| CTP | Compact Transport，Unified Bus 的轻量级传输层模式，借助下层协议共同提供可靠和拥塞控制的传输服务。 |
| Device | Host-Device 架构的设备侧，本文指昇腾 950 系列 NPU 芯片。 |
| Die | 芯片中具体的晶粒（Die）描述，一般一个芯片中集成一个或者多个 Die。 |

### Table 301 (p.13) ⭐深度解读
![[assets/crops/ascend-950-npu-architecture-whitepaper-tab301.png]]
> [!quote] caption
> 昇腾 950 系列芯片支持的主要规格

> [!tip] 表格解读（多模态）
> # Description of the Main Figure

**Architecture/Components:** The table presents the **Ascend 950 series chip specifications**, organized as a comparison matrix between two variants — 昇腾950PR and 昇腾950DT. The AI Subsystem is the sole subsystem shown, broken down into core counts (Cube Core, Vector Core) and combined "Cube+Vector" compute performance across five precision tiers: MXFP4, HiF8/MXFP8/FP8, INT8, BF16/FP16, and TF32. A separate "Cube" row isolates matrix-only throughput at MXFP4 precision. Each cell lists multiple numeric values corresponding to sub-configurations of each chip variant.

**Data Flow:** Rows = spec items → Columns = chip variants (PR vs. DT) → Values = performance metrics across precision formats.

**Key Technical Takeaway:** The 昇腾950DT achieves ~12% higher peak compute than 950PR at the top tier (2007 vs. 1784 TFLOPS MXFP4), with INT8 throughput closely matching MXFP8 performance — indicating a balanced heterogeneous-precision AI accelerator design optimized for both training and inference workloads. (120 words)

---

## Verbatim Caption Transcription

**表3-1 昇腾 950 系列芯片支持的主要规格**

### Table 401 (p.20) ⭐深度解读
![[assets/crops/ascend-950-npu-architecture-whitepaper-tab401.png]]
> [!quote] caption
> HiF8 特殊值编码

> [!tip] 表格解读（多模态）
> ## Description

**Components/Structure:** The figure is a reference table (not an architecture diagram) listing four special floating-point values and their 8-bit HiF8 encodings across two columns: *特殊值* (Special Value) and *编码* (Encoding).

**Data Flow / Encoding Layout:** Each encoding is an 8-bit word with color-coded bit fields:
- **ZERO** = `00000000` (all bits zero)
- **NAN** = `10000000` (only the sign bit set)
- **+INF** = `01101111`
- **-INF** = `11101111` (+INF with sign bit flipped)

**Key Technical Takeaway:** HiF8 uses a non-IEEE-754 convention for NaN — it is signaled with the sign bit alone (`10000000`) rather than saturating the exponent and mantissa. Infinities share an identical exponent/mantissa pattern, distinguished solely by the sign bit, simplifying hardware comparison logic but requiring explicit handling for NaN propagation. (≈115 words)

---

**Caption (verbatim):**

表4-1 HiF8 特殊值编码

### Table 402 (p.25) ⭐深度解读
![[assets/crops/ascend-950-npu-architecture-whitepaper-tab402.png]]
> [!quote] caption
> 昇腾 950 Memory 层次中主要 Memory 及其大小

> [!tip] 表格解读（多模态）
> **Architecture & Data Flow:**
The schematic depicts Ascend 950's multi-die memory hierarchy. Each die (Die 0 / Die 1) contains AI Cores and AI CPUs:

- **AI Core** = AIC (L1, L0A, L0B, L0C) + AIV (L1, Unified Buffer); connects upward to **L2 Cache**.
- **AI CPU** = CPU L1 + CPU L2; connects upward to **L3 Cache**.
- **L2 / L3 Cache** ↔ **Directory (Cache Coherence)** ↔ **Global Memory** (bidirectional).

**Key takeaway (≤120 words):** Ascend 950 splits the memory hierarchy into two purpose-built paths: **L2 Cache** specifically accelerates AIC/AIV AI compute via high-bandwidth, low-latency data staging with on-chip DRAM, while **L3 Cache** serves general-purpose AI CPU compute. Local buffers (L1/L0A/L0B/L0C/UB) supply per-tile operands, and a hardware Directory maintains cross-die coherence before reaching Global Memory — enabling heterogeneous AI CPU + accelerator workloads on a unified memory space.

## 技术点深读（DEEP）

![[deep/ascend-950-npu-architecture-whitepaper]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->

## 全文文本
全文已存 `extraction/fulltext/ascend-950-npu-architecture-whitepaper.txt`（28777 字符）供引用检索。