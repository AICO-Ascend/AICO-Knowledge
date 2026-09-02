# 分布式架构设计

> 仓 `triton-distributed-ascend` · 路径 `docs_ascend/zh/architecture.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/triton-distributed-ascend/docs_ascend/zh/architecture.md

```markdown
# 一体化深度解读:docs_ascend/zh/architecture.md

---

## 【定位】

本文档系统阐述 Triton-distributed-ascend 在华为昇腾 NPU 上的**分布式架构设计**:从 Python 层 `dl.*` 分布式原语出发,经过 Distributed Dialect 中间表示、ConvertTritonDistributedToHIVM Pass 转换、HIVM 方言下沉,最终链接到 aclshmem 对称堆模板库完成跨卡通信执行;并揭示其与 GPU 路径(运行时 module patch)的**架构本质差异**——Ascend 通过"符号链接期静态解析 + GM 架构固定地址"实现零运行时初始化开销。

---

## 【技术要点】

1. **双路径架构对比**:Ascend 路径下,Distributed Dialect 操作在 `ttadapter` 阶段被转换为 `hivm.custom` 符号,**编译期结束无运行时 module patch**;GPU 路径需 host 侧把 SHMEM 上下文指针 patch 进 device module,每次加载都有运行时初始化开销。

2. **七个分布式 Op**:Distributed Dialect 的 `dependentDialects` 被刻意置空(不依赖任何后端方言),包含 `wait` / `consume_token` / `get_rank` / `get_num_ranks` / `symm_at` / `notify` / `extern_call` 七个 op,这是它能同时下沉到 LLVM(GPU)和 HIVM(Ascend)的前提。

3. **核心 Pass**:`convert-triton-distributed-to-hivm` 是项目对编译流程的**唯一插入点**,作用域 `ModuleOp`,依赖 `hivm::HIVMDialect` + `triton::distributed::DistributedDialect`;其 `runOnOperation()` 做四件事:扫描 `tl.dot` 得 `existDot` 标志 → 注册七个 op 的重写模式 → `applyPatternsAndFoldGreedily` → 替换/擦除。

4. **TCoreType 推导顺序**:**先查前缀映射表,未命中则按 `existDot` 决定**——`aclshmem_barrier_all` → CUBE_AND_VECTOR;`aclshmemx_barrier_all_vec` 与 putmem/getmem/putmem_nbi/getmem_nbi/putmem_signal/putmem_signal_nbi → VECTOR;其他按 `existDot ? CUBE_AND_VECTOR : VECTOR`。barrier 标为 CUBE_AND_VECTOR 是**计算-通信重叠得以成立的机制**。

5. **Signal Slot Stride**:NPU 不保证多核并发写入同一 cacheline(64B)的访存一致性,`dl.wait` 遍历多个 barrier 时按 **64 字节硬编码跨步**,即 `SIGNAL_SLOT_STRIDE = 64 / sizeof(dtype)`——int32 信号 16 个元素,int64 信号 8 个元素。

6. **符号链接链路**:`symbol = "aclshmem_my_pe"` → `_mlir_ciface_aclshmem_my_pe`(无 memref 入参/返回时加前缀)→ 编译为四个变体 bitcode(`aic`/`aiv`/`mix_aiv`/`mix_aic`)→ 链接期静态解析到设备端模板库;模板库以 `ACLSHMEM_PTR_WRAPPER` / `ACLSHMEM_P_WRAPPER` / `ACLSHMEM_WAIT_WRAPPER` / `CONSUME_TOKEN_*_WRAPPER` 宏展开实现。

---

## 【关键机制与数据】

### 数据流路径

```
Python AST → Triton IR(DistributedOpBuilder 生成 distributed.*)
  → 【stage "ttir"】标准 Triton 优化(inliner/combine/canonicalize/cse/licm/loop_unroll)
  → 【stage "ttadapter"】★唯一插入点★ add_convert_triton_distributed_to_hivm(pm)
       (distributed 操作在进入 TTIR→Linalg 转换前已变成 hivm.custom)
  → 【stage "npubin"】单卡 NPU 编译(TTIR → Linalg IR → AscendNPU IR → 机器码,由 triton-ascend 完成)
  → Ascend NPU 可执行 kernel
```

### 性能/架构差异(原文:)

| 维度 | GPU 路径 | Ascend 路径 |
|------|---------|------------|
| 符号绑定 | 编译出二进制后,host 侧把 SHMEM 上下文指针 **patch 进 device module** | 编译期生成 `hivm.custom` 符号,**链接期静态解析** |
| device 端定位通信状态 | 通过被 patch 进去的全局变量 | 位于**架构固定的 GM 地址**,无需传参 |
| 运行时初始化开销 | 每次加载 module 都要 patch | 无 |

由此,Ascend 上 `dl.rank()` 等操作可做成**无额外参数的纯函数**(设备状态地址是编译期已知常量)。

### 副作用模型机制

副作用不在 TableGen 声明,而在 C++ 侧实现 `MemoryEffectsOpInterface`:`WaitOp` 只有 Read;`ConsumeTokenOp` 空(纯粹 IR 依赖锚点);`SymmAtOp` 只有 Read;`NotifyOp` Read + Write;`ExternCallOp` 在 `pure=true` 时无副作用,否则 Write + Read。

### PIPE 现状(原文)

符号到流水线的映射表在代码中已声明但**当前为空**,所有 distributed 操作实际落到 `PIPE_S`(标量流水)——这是预留扩展点,而非按操作类型分配流水线的既成设计。

---

## 【表格解读】

### 表格 1:术语缩写表——编译与 IR(逐字还原)

| 缩写 | 英文全称 | 中文说明 |
| --- | --- | --- |
| IR | Intermediate Representation | 中间表示 |
| AST | Abstract Syntax Tree | 抽象语法树 |
| MLIR | Multi-Level Intermediate Representation | 多级中间表示,LLVM 生态下可扩展的编译器基础设施,Distributed Dialect / HIVM Dialect 均构建于其上 |
| TTIR | Triton IR | Triton 方言层面的中间表示,也是编译流程中一个 stage 的名字 |
| LLVM | (项目专名,不再对应缩写展开) | GPU 路径的下沉目标 IR / 后端基础设施 |
| HIVM | Ascend 后端核心 IR 方言名 | `AscendNPU-IR`/`bishengir` 代码中作为专有名词使用,暂未见官方缩写全称展开 |
| DPS | Destination-Passing Style | 目标传递风格:通过预先分配的 init/输出值来传递计算结果的 IR 设计模式 |
| CSE | Common Subexpression Elimination | 公共子表达式消除 |
| LICM | Loop-Invariant Code Motion | 循环不变代码外提 |
| `TT_*`(如 `TT_Type`/`TT_Ptr`/`TT_IntLike`) | Triton Type | TableGen 中 Triton 方言类型约束的前缀 |

**解读**:此表定义了分布式编译流程涉及的核心 IR 层次抽象。MLIR 作为承载所有方言(Distributed Dialect 与 HIVM Dialect)的根基础设施,是跨平台下沉可能性的来源。DPS 模式在 Pass 转换中被使用(构造 `tensor::EmptyOp` 作为 init 值);CSE 与 LICM 是 `ttir` 阶段标准优化项。

### 表格 2:术语缩写表——硬件与执行单元(逐字还原)

| 缩写 | 英文全称 | 中文说明 |
| --- | --- | --- |
| NPU | Neural Processing Unit | 神经网络处理器,本文指华为昇腾 AI 处理器 |
| GPU | Graphics Processing Unit | 图形处理器 |
| GM | Global Memory | 全局内存,Device 侧全局可寻址内存 |
| UB | Unified Buffer | 统一缓冲区,AICore 片上临时缓冲区 |
| AIC | AI Cube Core | 矩阵单元,负责矩阵运算 |
| AIV | AI Vector Core | 向量单元,负责向量计算与低时延通信 |
| PE | Processing Element | 处理单元,对应一个 rank / 进程 / 设备参与方 |

**解读**:此表区分了 Ascend 硬件的两类执行单元。AIC 负责矩阵(AICube),AIV 负责向量与通信,这对应到 `TCoreType` 的 `CUBE` / `VECTOR` / `CUBE_AND_VECTOR` 三种派生选项——`existDot` 标志决定哪些操作需要矩阵单元协同。GM 是设备状态地址的物理载体。

### 表格 3:术语缩写表——通信引擎与协议(逐字还原)

| 缩写 | 英文全称 | 中文说明 |
| --- | --- | --- |
| SHMEM | Symmetric Hierarchical Memory / Shared Memory | 对称内存通信库,本文指 `shmem`/`aclshmem` 对称堆通信库 |
| ACLSHMEM | ACL(AscendCL)+ SHMEM | 本文对称堆通信接口/符号的前缀命名 |
| MTE | Memory Transfer Engine | 内存传输引擎,昇腾 AICore 侧数据搬运引擎 |
| SDMA | System Direct Memory Access | 系统直接内存访问 |
| UDMA | UB Direct Memory Access | 统一直接内存访问 |
| RDMA | Remote Direct Memory Access | 远程直接内存访问 |
| RoCE / ROCE | RDMA over Converged Ethernet | 基于融合以太网的 RDMA |
| TLS | Transport Layer Security | 传输层安全协议 |
| QP | Queue Pair | 队列对 |
| SQ | Send Queue | 发送队列 |
| SQE | Send Queue Element | 发送队列元素 |
| WQE | Work Queue Element | 工作队列元素 |
| SGE | Scatter/Gather Element | 分散/聚合元素 |

**解读**:此表定义了从硬件传输引擎(MTE/SDMA/UDMA)到上层通信协议(RDMA/RoCE/TLS)的完整链路。`aclshmem` 是本项目模板库所用的对称堆 API 前缀;RDMA/RoCE 描述底层物理传输能力,QP/SQ/WQE/SGE 描述网卡侧队列接口。

### 表格 4:术语缩写表——其他(逐字还原)

| 缩写 | 英文全称 | 中文说明 |
| --- | --- | --- |
| SIMD | Single Instruction Multiple Data | 单指令多数据 |
| SDK | Software Development Kit | 软件开发工具包 |

**解读**:`SIMD` 对应 `VFMode` 属性,被无条件设置为 SIMD 模式,影响指令生成方式。

### 表格 5:GPU vs Ascend 架构差异(逐字还原)

| | GPU | Ascend |
| --- | --- | --- |
| 通信库符号如何绑定 | 编译出二进制后,host 侧把 SHMEM 上下文指针 **patch 进 device module** | 编译期生成 `hivm.custom` 符号,**链接期静态解析** |
| device 端如何找到通信状态 | 通过被 patch 进去的全局变量 | 位于**架构固定的 GM 地址**,无需传参 |
| 运行时初始化开销 | 每次加载 module 都要 patch | 无 |

**解读**:此表是全文核心论点。Ascend 路径的零运行时开销来源于"符号链接期静态解析 + GM 架构固定地址"——硬件地址常量已知,host 不需要做 module patch,device 端亦无需上下文传参。

### 表格 6:七个分布式 Op(逐字还原)

| Op | operands | results | traits |
| --- | --- | --- | --- |
| `distributed.wait` | `barrierPtr`(TT_PtrLike), `numBarriers`(TT_IntLike), `waitValue`(TT_Int), `scope`, `semantic` | `token`(TT_IntLike) | `MemoryEffectsOpInterface`, `TypesMatchWith` |
| `distributed.consume_token` | `input`(TT_Type 或 TT_TensorDescType), `token`(TT_IntLike) | 同 `input` 类型 | `Elementwise`, `MemoryEffects`, `InferTypeOpInterface` |
| `distributed.get_rank` | `axis`(I32) | `result`(I32) | **`Pure`** |
| `distributed.get_num_ranks` | `axis`(I32) | `result`(I32) | **`Pure`** |
| `distributed.symm_at` | `symmAddr`(TT_Ptr), `rank`(I32) | `remoteAddr`(TT_Ptr,同类型) | `MemoryEffects`, `TypesMatchWith` |
| `distributed.notify` | `sigAddr`(TT_Ptr), `signalVal`(I64), `rank`(I32), `sigOp`, `commScope` | **无** | `MemoryEffects` |
| `distributed.extern_call` | `srcs`(Variadic), `libname`/`libpath`/`symbol`(StrAttr), `pure`(BoolAttr) | `result`(Variadic) | `MemoryEffects`, `ConditionallySpeculatable` |

**解读**:这是 Distributed Dialect 的核心接口定义。`get_rank` / `get_num_ranks` 标为 `Pure`,对应 GPU 路径 host patch / Ascend 路径 GM 固定地址两种设计;`symm_at` 输入本地地址 + rank,返回远端地址,实现跨卡寻址;`notify` 无结果输出,纯副作用操作;`extern_call` 是 escape hatch,允许携带任意符号名调用扩展库。

### 表格 7:SignalOp 属性(逐字还原)

| 值 | 名称 | 语义 |
| --- | --- | --- |
| 1 | SET | 将信号值设置为指定值 |
| 2 | ADD | 将指定值加到当前信号值 |

**解读**:`sigOp` 决定 Notify 的语义——覆盖式赋值 vs 累加。ADD 模式在多次通知合并、累加计数等场景下使用。

### 表格 8:内存副作用模型(逐字还原)

| Op | 副作用 |
| --- | --- |
| `WaitOp` | 只有 `Read` |
| `ConsumeTokenOp` | **空**——纯粹的 IR 依赖锚点 |
| `SymmAtOp` | 只有 `Read` |
| `NotifyOp` | `Read` **+** `Write` |
| `ExternCallOp` | `pure=true` 时无副作用,否则 `Write` + `Read` |

**解读**:副作用模型直接影响编译器对操作的优化自由度——`ConsumeTokenOp` 副作用空,意味着它可以在不破坏语义的前提下被 CSE / LICM 优化;`NotifyOp` 有副作用,不能被消除或重排;`ExternCallOp` 依赖 `pure` 标记决定是否可推测执行。

### 表格 9:aclshmem 接口映射(逐字还原)

| 源 op | 对应aclshmem接口名 |
| --- | --- |
| `SymmAtOp` | `aclshmem_ptr_<typename>`,如 `aclshmem_ptr_float` |
| `GetRankOp` | `aclshmem_my_pe` |
| `GetNumRanksOp` | `aclshmem_n_pes` |
| `NotifyOp`(i32 信号) | `aclshmemx_signal_op` |
| `NotifyOp`(ui64 / i64 信号) | `aclshmem_uint64_p` / `aclshmem_int64_p` |
| `ConsumeTokenOp` | `aclshmem_consume_token_<typename>`,如 `aclshmem_consume_token_float_ptr_1d` |
| `WaitOp` | `aclshmem_wait_<typename>`,如 `aclshmem_wait_int32` |
| `ExternCallOp` | 沿用 op 自带的 `symbol` 属性 |

**解读**:这是 Pass 输出的"字符串符号名"清单——每个 Distributed Dialect 操作对应一个 aclshmem API 符号,这些符号在模板库中有静态实现(由 `ACLSHMEM_PTR_WRAPPER` / `ACLSHMEM_P_WRAPPER` / `ACLSHMEM_WAIT_WRAPPER` 宏展开)。`NotifyOp` 的符号随信号类型分派——i32 走 `aclshmemx_signal_op`,i64 走 P 系列。

### 表格 10:TCoreType 推导(逐字还原)

| 符号前缀 | Core Type |
| --- | --- |
| `aclshmem_barrier_all` | CUBE_AND_VECTOR |
| `aclshmemx_barrier_all_vec` | VECTOR |
| `aclshmem_putmem` / `getmem` / `putmem_nbi` / `getmem_nbi` / `putmem_signal` / `putmem_signal_nbi` | VECTOR |
| 其他(未命中前缀表) | `existDot ? CUBE_AND_VECTOR : VECTOR` |

**解读**:barrier 同时标为 CUBE_AND_VECTOR 是**计算-通信重叠**的硬件机制——barrier 在 kernel 被拆为 cube func 与 vector func 后同时存在于两个 func 中,矩阵计算与通信可在不同核上并行进行。put/get 系列均为 VECTOR,因为它们属于低时延通信路径。

### 表格 11:其余 hivm.custom 属性(逐字还原)

| 属性 | 取值 | 说明 |
| --- | --- | --- |
| `PIPE` | `PIPE_S` | 见下方说明 |
| `VFMode` | `SIMD` | 无条件设置 |
| `hivm.is_distributed` | UnitAttr | 下游标记,供内存作用域推导、块指针分析、mix kernel 拆分等多个后续阶段识别分布式操作 |
| `symbol` | StrAttr | 裸符号名 |
| `no_side_effect` | UnitAttr(条件) | 仅当源 op 的内存副作用为空时设置 |
| `gm_addr_args_indices` | DenseI32Array | 收集「既是指针类型、又是 `tt.func` 入口块参数」的操作数下标。张量指针与 `tt.addptr` 的结果都不计入 |

**解读**:`hivm.is_distributed` 是分布式语义的"通行证"——下游多个阶段(内存作用域推导、块指针分析、mix kernel 拆分)依赖此标记识别分布式操作,做特定优化或分析。`gm_addr_args_indices` 排除张量指针与 `tt.addptr` 结果,只收集真正的标量指针入口参数。

---

## 【公式解读】

**原文无标准数学公式**。但文档中存在两处表达式式定义,逐字保留并解读如下:

### 表达式 1:符号名 mangle 规则

```cpp
std::string prefix = concreteOp.getSymbol();
if (!hasMemrefInArgOrRet()) { prefix = "_mlir_ciface_" + prefix; }
return prefix + callNameMangleSuffix(op);
```

即 `symbol = "aclshmem_my_pe"` → 链接名 `_mlir_ciface_aclshmem_my_pe`。

**符号含义**:
- `concreteOp.getSymbol()`:从转换后得到的 `hivm::CustomOp` 上读取裸符号名字符串(如 `aclshmem_my_pe`)。
- `hasMemrefInArgOrRet()`:判断操作是否有 memref 类型的入参或返回。
- `_mlir_ciface_` 前缀:当无 memref 入参/返回时,加上此 MLIR 标准 C 接口前缀。
- `callNameMangleSuffix(op)`:根据 op 的入参/返回类型推导 mangled 后缀(类型信息编码)。
- 最终返回值为链接期可解析的链接名。

### 表达式 2:Signal Slot Stride

`SIGNAL_SLOT_STRIDE = 64 / sizeof(dtype)`

**符号含义**:
- `64`:NPU cacheline 字节数(硬编码常量,因 NPU 架构不保证多核并发写入同一 cacheline 的访存一致性)。
- `sizeof(dtype)`:信号值类型的字节宽度(int32 = 4,int64 = 8)。
- `SIGNAL_SLOT_STRIDE`:每个 barrier 元素之间在张量维度上的跨步数。
- 推论:int32 信号 stride = 64/4 = **16 个元素**;int64 信号 stride = 64/8 = **8 个元素**。

---

## 【关联】

文档**未提供内部链接**(文末链接列表为空)。但文中存在多处**前向/后向引用**,勾勒出本架构与其他模块的关系:

1. **与编译流水线的上下游关系**:本架构描述 `ttadapter` 阶段的 `convert-triton_distributed_to_hivm` Pass,上游依赖 Triton 标准 `ttir` 阶段(inliner/combine/canonicalize/cse/licm/loop_unroll),下游依赖 `triton-ascend` 三方库完成 `npubin` 阶段的 TTIR → Linalg → AscendNPU IR → 机器码转换。**`distributed` 模块是编译器的可选依赖**——通过 `try / except ImportError` 加载,未构建分布式支持时自动跳过该 Pass。

2. **与运行时关系**:对称堆初始化在文档末尾(第五章)开始展开,host 端由用户代码直接调用 `shmem` Python 接口(文档未完)。设备端通信状态位于"架构固定的 GM 地址",与 device 端模板库(`ACLSHMEM_PTR_WRAPPER` 等宏)共同构成运行时支撑。

3. **与混合 kernel 拆分的关系**:`hivm.is_distributed` 标记是 mix kernel 拆分阶段识别分布式操作的依据——见 3.4 节"其余属性"说明,拆分阶段会依据此标记决定是否在 cube func / vector func 中保留相应操作。

4. **与 6.3 节(本架构文档未包含)**:`aclshmem_barrier_all` 标为 CUBE_AND_VECTOR 这一点"与 A/B 路径有本质区别(见 6.3)"——文档指引读者参阅后续章节,但本章未给出 6.3 的内容。

5. **与 5.3 节 symm_at 机制的关系**:文档在第五章开头提及"对称张量"概念,引用 5.3 节 `symm_at` 实现"本地偏移 + 目标 PE 堆基址"的远端地址计算,但 5.3 节内容同样未包含在截取的文档片段中。

---

## 【使用方法】

**原文文档在 5.1 节处被截断**(末尾为"Ascend 的对称堆初始化由用户代码直接调用 `shmem` Pytho")。基于已读章节,涉及启用/配置的内容如下:

- **可选依赖加载机制**(原文 4.1 节):`distributed` 模块通过 `try / except ImportError` 加载,未构建分布式支持时自动跳过 `ConvertTritonDistributedToHIVM` Pass;即无需显式启用开关——有无 `distributed` 模块决定该 Pass 是否生效。

- **编译流程介入点**(原文 4.1 节):本项目对编译流程的介入**只有一处**——在 `ttadapter` 阶段最开始插入 `add_convert_triton_distributed_to_hivm(pm)`,在此之前无任何 distributed 相关转换。

- **关于 PIPE 的扩展点**(原文 3.4 节说明):符号到流水线的映射表已声明但**当前为空**,预留作为按操作类型分配流水线的扩展点——若需启用,需填充该映射表。

文档**未涉及**的内容(因截断而缺失):
- 完整的对称堆运行时初始化流程(5.1 节未完);
- `shmem` Python 接口的具体调用方式;
- 任何运行时配置项、命令行参数、环境变量;
- 用户态 `dl.*` 原语的使用方法、API 文档。

如需了解运行时初始化与用户 API 的完整使用方法,需参阅该 architecture.md 文档的后续章节(5.1 节之后)及项目其他文档。
```

## 图文联合解读

- `architecture.png`: 图示自上而下三层流程：Python API（triton_dist.language、libshmem_device）→@triton.jit编译→平台无关Distributed Dialect（7个distributed.*操作）→分三路下沉：Ascend经ConvertTritonDistributedToHIVM→hivm.custom'dist.*'→triton-ascend单卡编译→aclshmem运行时；平台A/B走Distributed ToLLVM/SHMEM。

论证：分布式原语与硬件解耦，7个distributed.*作统一抽象，Ascend专属HIVM+aclshmem特化路径，其余走LLVM+SHMEM，体现"一抽象、多端落地"的可扩展架构设计。

文档关系：与术语表中Distributed Dialect、HIVM、SHMEM/ACLSHMEM等概念一一对应，佐证"平台无关分布式抽象层"这一核心论点。
