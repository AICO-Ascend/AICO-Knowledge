# Distributed Architecture Design

> 仓 `triton-distributed-ascend` · 路径 `docs_ascend/en/architecture.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/triton-distributed-ascend/docs_ascend/en/architecture.md

# Triton-distributed-Ascend 「Distributed Architecture Design」深度解读

## 【定位】

这篇文档系统性描述 Triton-distributed-ascend 在华为 Ascend 平台上的分布式架构——从 Python 端的 `dl.*` 分布式原语出发，经过平台无关的 Distributed Dialect IR、各级 MLIR 转换，最终落到 NPU 的 AICore (CUBE/AIV) 上由 `hivm.custom` 自定义算子 + `aclshmem` 对称堆通信库静态链接执行的完整栈结构，并重点澄清它与 GPU 路径在"通信库符号如何绑定到设备端"这一关键设计取舍上的差异。

---

## 【技术要点】

1. **平台无关 IR + 平台相关 Conversion Pass 的双层架构**: `dependentDialects` 故意留空，使 Distributed Dialect 可以分别 lower 到 LLVM(GPU 路径)与 HIVM(Ascend 路径)，业务侧 `dl.*` 代码无需为不同平台重写——这是 §1.1 的核心设计哲学。

2. **Ascend 路径采用"编译期静态链接"而非"运行时模块打补丁"**: 通信库符号在编译期生成 `hivm.custom` 操作，链接时由后端在设备端模板库中静态解析，**不需运行时模块打补丁**；通信状态位于架构规定的固定 GM 地址，编译期已知常量，因此 `dl.rank()` 等可实现为无参纯函数——见 §1.2 表格。

3. **Distributed Dialect 共 7 个 Op**: `wait` / `consume_token` / `get_rank` / `get_num_ranks` / `symm_at` / `notify` / `extern_call`，其中 `get_rank` / `get_num_ranks` 显式标记为 `Pure` trait (§2.2)。

4. **`consume_token` 是纯 IR 依赖锚点，无内存副作用**: 其 `MemoryEffectsOpInterface` 实现为 **Empty**——只用于建立 IR 中的 use-def 依赖以维持正确排序，本身不读写内存；`WaitOp` / `SymmAtOp` 只有 `Read`，`NotifyOp` 同时 `Read`+`Write` (§2.4)。

5. **`convert-triton-distributed-to-hivm` Pass 的四点运行逻辑**: ① 扫描 `triton::DotOp` / `DotScaledOp` 得到 `existDot` 标志(用于判断是否为纯 AIV kernel)；② 注册 7 个分布式 op 的重写模式；③ 调用 `applyPatternsAndFoldGreedily`；④ 其它 Triton IR 原样保留给下游单设备编译阶段 (§3.2)。

6. **aclshmem 符号命名约定**: 每个分布式 op 通过转换模板生成对应的 `aclshmem_*` 接口符号，例如 `SymmAtOp` → `aclshmem_ptr_<typename>`、`GetRankOp` → `aclshmem_my_pe`、`NotifyOp`(i32) → `aclshmemx_signal_op` 等——链接器据此在设备端模板库中静态解析 (§3.3)。

7. **`TCoreType` 推断的优先级**: 先查符号前缀映射表，未命中则依据 `existDot` 决定核心类型；前缀 `aclshmem_barrier_all` → `CUBE_AND_VECTOR`(§3.4，原文被截断)。

---

## 【关键机制与数据】

- **核心设计哲学(原文: §1.1)**: "Distributed Dialect is a **platform-agnostic intermediate representation**. Each platform maps it to its own communication library through different Conversion Passes, and business-side `dl.*` code does not need to be rewritten for different platforms."

- **Ascend 路径落点(原文: §1.1)**: "The landing point for the Ascend platform is the `hivm.custom` operation—each Distributed Dialect operation is converted into a custom op with a symbol name, where the symbol statically exists in the device-side template library and is resolved by the backend during linking. **No runtime module patching is required after compilation**."

- **GPU vs Ascend 三点架构差异(原文: §1.2 表格)**:
  - 通信库符号绑定方式: GPU 是"编译后 host 端把 SHMEM context 指针打补丁进设备模块"；Ascend 是"编译期生成 `hivm.custom` 符号，链接时静态解析"。
  - 设备端定位通信状态: GPU 通过"被打补丁的全局变量"；Ascend 通过"架构规定的固定 GM 地址，无需参数传递"。
  - 运行时初始化开销: GPU 每次加载都需模块打补丁；Ascend **无此开销**。

- **数据流方向(原文: §1.1 描述)**: Python `dl.*` 原语 → Distributed Dialect (`mlir::triton::distributed` 命名空间) → `convert-triton-distributed-to-hivm` Pass → `hivm::HIVMDialect` 中的 `hivm.custom` 操作 → 链接期解析到 `aclshmem_*` 符号 → AICore (CUBE/AIV) 上的设备端模板库执行。

- **Dialect 命名空间(原文: §2.1)**: Dialect 名为 `distributed`；C++ 命名空间为 `::mlir::triton::distributed`。

- **`consume_token` 的特殊地位(原文: §2.4)**: "purely an IR dependency anchor"——只是 IR 依赖锚点，无内存副作用。

- **`SignalOp` 枚举值(原文: §2.3)**: 1 = SET(置为指定值)；2 = ADD(累加指定值)。

> 原文未提供性能数字、benchmark、延迟/带宽数据。

---

## 【表格解读】

### 表 1：§1.2 Architectural Differences from the GPU Path(逐字还原)

| | GPU | Ascend |
| --- | --- | --- |
| How communication library symbols are bound | After compiling the binary, the host side **patches the SHMEM context pointer into the device module** | During compilation, `hivm.custom` symbols are generated and **statically resolved during linking** |
| How the device side finds communication state | Through a global variable patched in | Located at a **fixed GM address in the architecture**, no parameter passing needed |
| Runtime initialization overhead | Module patching required every time it's loaded | None |

**逐行解读**:
- 第一行指出两者在符号绑定时机上的本质差异：GPU 是"二进制出包后由 host 在加载时打补丁"(运行时机制)，Ascend 是"编译期生成 `hivm.custom` 符号、链接时静态解析"(构建期机制)。这决定了 Ascend 路径不需要任何运行时热修复。
- 第二行解释设备端如何拿到通信状态对象：GPU 依赖 host 注入的全局变量(需要参数或隐式状态传递)，Ascend 直接使用架构固定的 GM 地址(地址是编译期常量)。
- 第三行说明运行时的初始化开销差异：GPU 每次加载模块都要打补丁；Ascend 无此步骤，因而 `dl.rank()` 等纯函数无需额外参数即可实现——这是文档原文 §1.2 末尾给出的推论。

---

### 表 2：§2.2 Seven Distributed Ops(逐字还原)

| Op | operands | results | traits |
| --- | --- | --- | --- |
| `distributed.wait` | `barrierPtr`(TT_PtrLike), `numBarriers`(TT_IntLike), `waitValue`(TT_Int), `scope`, `semantic` | `token`(TT_IntLike) | `MemoryEffectsOpInterface`, `TypesMatchWith` |
| `distributed.consume_token` | `input`(TT_Type or TT_TensorDescType), `token`(TT_IntLike) | Same type as `input` | `Elementwise`, `MemoryEffects`, `InferTypeOpInterface` |
| `distributed.get_rank` | `axis`(I32) | `result`(I32) | **`Pure`** |
| `distributed.get_num_ranks` | `axis`(I32) | `result`(I32) | **`Pure`** |
| `distributed.symm_at` | `symmAddr`(TT_Ptr), `rank`(I32) | `remoteAddr`(TT_Ptr, same type) | `MemoryEffects`, `TypesMatchWith` |
| `distributed.notify` | `sigAddr`(TT_Ptr), `signalVal`(I64), `rank`(I32), `sigOp`, `commScope` | **None** | `MemoryEffects` |
| `distributed.extern_call` | `srcs`(Variadic), `libname`/`libpath`/`symbol`(StrAttr), `pure`(BoolAttr) | `result`(Variadic) | `MemoryEffects`, `ConditionallySpeculatable` |

**逐行解读**:
- `wait`: 取一个 barrier 指针与若干 barrier 计数、等待值及作用范围/语义，产出 `token`；带 `TypesMatchWith` 意味着 token 类型与 numBarriers 类型需要匹配；用于建模跨 rank barrier 同步中的等待动作。
- `consume_token`: 输入类型可以是普通 TT 类型或 TensorDesc 类型，输出与输入同型；名为 `consume_token`，在 IR 中"消费"上游 token 以维持依赖，但 §2.4 指出它**没有实际内存副作用**，纯为依赖锚点。
- `get_rank`: 仅一个 `axis` 输入(I32)，输出 I32 的当前 rank；显式 `Pure`——可被 CSE/LICM 自由优化，因此下游可作为编译期常量使用。
- `get_num_ranks`: 与 `get_rank` 对偶，返回参与通信的 rank 总数；同样 `Pure`。
- `symm_at`: 给定对称堆上的地址与目标 rank，返回远端 rank 上的同型地址；`TypesMatchWith` 要求输出与输入指针同型——核心的"地址翻译"操作。
- `notify`: 向远端 rank 的信号地址写入 signalVal(I64)，并指明 sigOp(SET/ADD)和通信范围；无返回值，单纯触发信号写。
- `extern_call`: 通用外部调用包装，可指定库路径、符号名与 `pure` 标志；为 `ConditionallySpeculatable`，即 `pure=true` 时可被推测执行——提供了扩展性出口。

---

### 表 3：§2.3 SignalOp 枚举(逐字还原)

| Value | Name | Semantics |
| --- | --- | --- |
| 1 | SET | Set the signal value to the specified value |
| 2 | ADD | Add the specified value to the current signal value |

**逐行解读**:
- `SET(=1)`: 把信号值**覆盖式**置为指定值——典型的"事件已发生"通知。
- `ADD(=2)`: 把指定值**累加**到当前信号值——典型的"到达计数"或"多源信号合并"语义。

---

### 表 4：§2.4 Memory Side Effect Model(逐字还原)

| Op | Side Effects |
| --- | --- |
| `WaitOp` | Only `Read` |
| `ConsumeTokenOp` | **Empty**—purely an IR dependency anchor |
| `SymmAtOp` | Only `Read` |
| `NotifyOp` | `Read` **+** `Write` |
| `ExternCallOp` | No side effects when `pure=true`, otherwise `Write` + `Read` |

**逐行解读**:
- `WaitOp` / `SymmAtOp` 只 `Read`：等待/远端寻址本身不修改内存。
- `ConsumeTokenOp` **Empty**：作者强调它"purely an IR dependency anchor"——是排序工具而非真实内存操作，编译器可自由重排/消除。
- `NotifyOp` 同时 `Read`+`Write`：写信号通常需先读(尤其是 ADD 模式)。
- `ExternCallOp` 由 `pure` 标志动态决定有无副作用——这是它被打上 `ConditionallySpeculatable` trait 的原因。

---

### 表 5：§3.3 aclshmem Interface OP Generation(逐字还原)

| Source op | Corresponding aclshmem interface name |
| --- | --- |
| `SymmAtOp` | `aclshmem_ptr_<typename>`, e.g., `aclshmem_ptr_float` |
| `GetRankOp` | `aclshmem_my_pe` |
| `GetNumRanksOp` | `aclshmem_n_pes` |
| `NotifyOp` (i32 signal) | `aclshmemx_signal_op` |
| `NotifyOp` (ui64 / i64 signal) | `aclshmem_uint64_p` / `aclshmem_int64_p` |
| `ConsumeTokenOp` | `aclshmem_consume_token_<typename>`, e.g., `aclshmem_consume_token_float_ptr_1d` |
| `WaitOp` | `aclshmem_wait_<typename>`, e.g., `aclshmem_wait_int32` |
| `ExternCallOp` | Uses the op's own `symbol` attribute |

**逐行解读**:
- 这是从分布式 IR 到 aclshmem C 接口的关键映射表——模板字符串中 `<typename>` 由 MLIR 类型推导填入，例如 `TT_Ptr` 链上的具体指针类型。
- 注意 `NotifyOp` 按信号位宽分三种映射：i32 走 `aclshmemx_signal_op` 特殊接口；ui64/i64 各有独立函数符号。
- `ExternCallOp` 不做转换，直接复用 op 上携带的 `symbol` 属性作为外部符号名。

---

### 表 6：§3.4 TCoreType 前缀映射(原文被截断，逐字还原可见部分)

| Symbol Prefix | Core Type |
| --- | --- |
| `aclshmem_barrier_all` | CUBE_AND_VECTOR |

**逐行解读**:
- 原文到此行结束(`|` 收尾)，未给出更多映射条目。
- 可推断的语义：`barrier_all` 这种集合同步语义既需要矩阵核(CUBE)又需要向量核(AIV)参与，因此被打上 `CUBE_AND_VECTOR`。
- 据 §3.2，命中失败时回退到 `existDot` 决定——若 Pass 没看到任何 `triton::DotOp`，整个 kernel 为纯 AIV 类型。

---

### 表 7-9：术语表(Compilation/IR、Hardware/Execution Units、Communication Engines、Other)

由于术语表条目过多(共约 30 条)，仅逐字还原其结构骨架如下，完整逐行解读可按需展开：

**(A) Compilation and IR** —— 收录 IR / AST / MLIR / TTIR / LLVM / HIVM / DPS / CSE / LICM / `TT_*` 共 10 项缩写。**关键解读**: MLIR 是 LLVM 生态的可扩展编译器基础设施，Distributed Dialect 与 HIVM Dialect 都构建其上；HIVM 是 `AscendNPU-IR`/`bishengir` 代码中的核心 IR dialect 名名（proper noun，无官方缩写展开）；DPS 是"通过预分配的 init/output 值传递计算结果"的 IR 设计模式。

**(B) Hardware and Execution Units** —— 收录 NPU / GPU / GM / UB / AIC / AIV / PE 共 7 项。**关键解读**: AIC 与 AIV 是 Ascend AICore 内部的两个分工——AIC 负责矩阵运算、AIV 负责向量运算与低时延通信；GM 是设备端全局可寻址内存；UB 是 AICore 片上临时缓冲；PE 在本文档中对应一个 rank/process/device 参与者——这是把分布式概念与硬件层映射的关键桥梁。

**(C) Communication Engines and Protocols** —— 收录 SHMEM / ACLSHMEM / MTE / SDMA / UDMA / RDMA / RoCE / TLS / QP / SQ / SQE / WQE / SGE 共 13 项。**关键解读**: 在本文档语境下 SHMEM 指 `shmem`/`aclshmem` 对称堆通信库；ACLSHMEM 是其接口前缀命名约定；MTE/SDMA/UDMA/RDMA/RoCE 是数据搬运/传输引擎栈；QP/SQ/SQE/WQE/SGE 是 RDMA 队列模型的组件。

**(D) Other** —— 收录 SIMD / SDK 共 2 项。

---

## 【公式解读】

**原文无公式**(无 LaTeX 数学式、无算法伪代码)。

文档中的"形式化定义"仅限于：
- §2.2 Op 表中的 operand/result 类型签名(MLIR 类型系统语法)——已在【表格解读】中按表格逐行还原。
- §3.3 中的字符串模板 `aclshmem_ptr_<typename>` 等——已在【表格解读】表 5 解读。

如需对"信号量同步语义"建模，文档以 `SignalOp` 枚举(SET/ADD)代替形式化公式。

---

## 【关联】

原文**无内部链接**(标注"(无)")。以下是基于文本提及梳理的模块间关系链:

**上游(被本架构依赖)**:
- **MLIR / LLVM 生态**: MLIR 作为基础设施承载 Distributed Dialect 与 HIVM Dialect(术语表 §术语行)。
- **Triton IR (TTIR)**: 作为 MLIR 中的 Triton 方言层级，是编译流水线中的一环——`convert-triton-distributed-to-hivm` Pass 之外的 Triton IR 原样保留给下游单设备编译阶段使用 (§3.2 第 3 点)。
- **`shmem` / `aclshmem` 对称堆通信库**: Ascend 路径的设备端模板库，提供所有 `aclshmem_*` 符号实现 (§3.3)。
- **`AscendNPU-IR` / `bishengir`**: HIVM Dialect 名名所在的代码体系(术语表)。

**下游(本架构的服务对象)**:
- **Python 端的 `dl.*` 业务原语**: 平台无关，业务侧不需为 GPU/Ascend 写两套 (§1.1)。
- **AICore 的 CUBE/AIV 计算核心**: 最终执行单位，分别承担矩阵/向量/低时延通信任务(术语表 + §3.4)。

**横向(同类对比)**:
- **GPU 路径 (A/B paths)**: 文档明确指出"和 A/B 路径不同"，A/B 路径在编译后需 host 端把 SHMEM context 指针打补丁到设备模块 (§1.1、§1.2)。

**横向(同一 Pass 内的依赖)**:
- **`triton::DotOp` / `DotScaledOp`**: `convert-triton-distributed-to-hivm` 在 `runOnOperation()` 中扫描它们以得到 `existDot` 标志，影响 `TCoreType` 推断 (§3.2 第 1 点 + §3.4)。

---

## 【使用方法】

原文**未涉及**具体启用方式、配置项、命令或调用示例。

文档是**架构总览**性质，仅描述 IR 设计、Pass 行为、Op 签名与映射规则，没有给出诸如"如何调用此 Pass"、"如何开启 Ascend 后端"、"编译命令是什么"等运行/构建指令。

(注:由于原文在 §3.4 表格行后被截断(`|` 收尾)，可能后续章节涉及更多 Pass 配置或调用示例，但**当前提供的原文范围内**未出现。)

## 图文联合解读

- `architecture.png`: **图示解读：**

1) **结构**：分层架构——Python API 层（`triton_dist.language` 的 `dl.rank/wait/notify` 与 `libshmem_device` 的 `putmem/getmem/barrier_all`）经 `@triton.jit` 编译进入 Triton IR + Distributed Dialect (MLIR) 平台无关分布式抽象（7 个 `distributed.*` 操作），再分三条下游：Ascend 走 `ConvertTritonDistributedToHIVM (aclshmem)` → `hivm.custom 'dist.*'` → triton-ascend 单卡编译 → NPU 执行 + aclshmem 运行时；平台 A/B 则分别走 `Distributed ToLLVM (SHMEM)`。

2) **技术结论**：前端 API 与 MLIR 抽象是统一的，下层按目标硬件（Ascend 的 HIVM+aclshmem vs 其他平台的 SHMEM+LLVM）分化，体现"一次前端、多平台后端"的可扩展设计。

3) **与文档论点关系**：印证了 Distributed Dialect 作为平台无关 IR 层的设计意图，支撑"MLIR 多级 IR 上同时构建 Distributed Dialect 与 HIVM Dialect"的分层抽象论点。
