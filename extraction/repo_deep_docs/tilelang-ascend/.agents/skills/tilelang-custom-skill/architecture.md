# TileLang-Ascend 架构参考

> 仓 `tilelang-ascend` · 路径 `.agents/skills/tilelang-custom-skill/architecture.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/tilelang-ascend/.agents/skills/tilelang-custom-skill/architecture.md

# TileLang-Ascend 架构参考 · 一体化深度解读

## 【定位】

**这篇文档是 TileLang-Ascend 的整体架构速览,系统描述了从 Python DSL 经多层 IR 变换 Pass、代码生成到 CANN 工具链最终在 NPU 上执行的端到端编译流水线,并给出目录结构、硬件原语映射与核心 API 的对照视图,作为理解与导航该代码仓库的参考蓝图。**

---

## 【技术要点】

1. **六阶段编译流程**: Python DSL(`@tilelang.jit`)→ IR 变换 Pass(双源:`tilelang/transform/` + `src/transform/`)→ 代码生成(`src/target/codegen_ascend_pto.cc`)→ 模板库(`src/tl_templates/`)→ CANN 工具链编译 → NPU 执行。
2. **关键 Pass 链(10 步)**: `frontend_legalize` → `layout_inference` → `flatten_buffer` → `loop_vectorize` → `inject_pipeline` → `ascend_lower_parallel_to_vector` → `ascend_memory_planning` → `ascend_sync_insert` → `ascend_combinecv` → `lower_tile_op`,覆盖合法化、布局推断、缓冲展平、向量化、流水注入、并行降维、内存规划、同步插入、CV 合并与算子降低。
3. **前端 Python 包分层**: `jit/`(JIT 入口)、`language/`(DSL 原语,含 ascend.py、ascend_tile.py、pto.py、gemm.py、copy_op.py、reduce.py、allocate.py、parallel.py)、`engine/`(lower.py 编译引擎)、`transform/`、`autotuner/`、`carver/`、`layout/`、`intrinsics/`、`profiler/`。
4. **后端 C++ 双代码生成路径**: `codegen_ascend_pto.cc`(3225 行,主要 PTO 代码生成)与 `codegen_ascend.cc`(2050 行,Ascend C 代码生成);另有 `rt_mod_ascend*.cc` 运行时模块;`src/transform/` 含 **47 个** IR 变换文件,关键模块为 `ascend_storage_rewrite.cc`(70KB)、`ascend_sync_insert.cc`(46KB)、`ascend_lower_parallel_to_vector.cc`(49KB)、`ascend_memory_planning.cc`(24KB)、`cross_core_pipeline.cc`(35KB)。
5. **多级硬件存储映射**: `T.alloc_L1`(L1 缓存/Cube 核)、`T.alloc_ub`(统一缓冲区/Vector 核)、`T.alloc_L0A/L0B/L0C`(L0 寄存器),由 `T.gemm`/`T.mma`(矩阵乘法加速器)、`T.Parallel`(向量化指令)、`T.Pipelined`(流水线调度)驱动。
6. **规模数据**: `ascend_tile.py` 56KB(标注"最大模块");`examples/` 含 **31 类**算子示例;`3rdparty/` 托管 TVM 与 pto-isa 第三方依赖。

---

## 【关键机制与数据】

- **编译流水线工作原理**: Python 端通过 `@tilelang.jit` 装饰器捕获用户 DSL,经 `engine/lower.py` 调度一系列 IR 变换 Pass(部分 Python 侧、部分 C++ 侧),最终通过 `src/target/codegen_ascend_pto.cc` 将高层 IR 落地为 PTO 指令代码,套用 `src/tl_templates/` 中的模板,交由 CANN 工具链编译并下发到 NPU 执行。
- **数据流方向**: `tilelang/`(Python 前端 DSL) → `src/transform/`(C++ IR Pass 链) → `src/target/`(代码生成) → `src/tl_templates/`(模板填充) → CANN → NPU。
- **同步与流水线机制**: `ascend_sync_insert.cc` 负责在 IR 中插入同步原语以保证核内/核间数据依赖;`cross_core_pipeline.cc`(35KB)处理跨核流水;`inject_pipeline` Pass 与之配套完成软件流水注入。
- **性能/规模数据(原文标注)**:
  - 原文:`codegen_ascend_pto.cc` **3225 行**(主要 PTO 代码生成)
  - 原文:`codegen_ascend.cc` **2050 行**(Ascend C 代码生成)
  - 原文:`src/transform/` 共 **47 个** C++ 变换文件
  - 原文:`ascend_storage_rewrite.cc` **70KB**
  - 原文:`ascend_sync_insert.cc` **46KB**
  - 原文:`ascend_lower_parallel_to_vector.cc` **49KB**
  - 原文:`ascend_memory_planning.cc` **24KB**
  - 原文:`cross_core_pipeline.cc` **35KB**
  - 原文:`ascend_tile.py` **56KB,最大模块**
  - 原文:`examples/` 含 **31 类**算子示例

---

## 【表格解读】

### 原文表格:硬件原语映射

| DSL 原语 | 硬件资源 |
|---------|---------|
| `T.alloc_L1` | L1 缓存 (Cube 核) |
| `T.alloc_ub` | 统一缓冲区 (Vector 核) |
| `T.alloc_L0A/L0B/L0C` | L0 寄存器 |
| `T.gemm` / `T.mma` | 矩阵乘法加速器 |
| `T.Parallel` | 向量化指令 |
| `T.Pipelined` | 流水线调度 |

**逐行解读**:

- **`T.alloc_L1` → L1 缓存 (Cube 核)**: 表示用户在 DSL 中声明的 L1 缓冲在硬件上映射到 Ascend NPU 的 L1 缓存,由 Cube 核使用,典型用于矩阵乘的输入分片暂存。
- **`T.alloc_ub` → 统一缓冲区 (Vector 核)**: 统一缓冲区(UB)由 Vector 核访问,常用于向量化计算、归约与数据搬运的中间暂存。
- **`T.alloc_L0A/L0B/L0C` → L0 寄存器**: 三个 L0 寄存器分别对应矩阵乘的 A 操作数、B 操作数与累加器 C,是距离计算单元最近的存储级,带宽最高、容量最小。
- **`T.gemm` / `T.mma` → 矩阵乘法加速器**: `gemm`/`mma` 调用映射到硬件的矩阵乘法加速单元(Cube),通常配合 L0A/L0B 输入与 L0C 输出寄存器使用。
- **`T.Parallel` → 向量化指令**: 用于将循环或表达式向量化,生成 Vector 核的 SIMD 指令,主要消费 UB 中的数据。
- **`T.Pipelined` → 流水线调度**: 描述计算与访存的重叠策略,由 `inject_pipeline` Pass 与 `cross_core_pipeline.cc` 配合实现核内/核间软件流水。

---

## 【公式解读】

**原文无公式**(文档以编译流程图、Pass 链、目录树与表格为主,未出现数学公式或伪代码表达式)。

---

## 【关联】

原文未提供内部链接(标注"无")。基于文档自身的目录与流水线描述,可梳理出以下**模块间上下游/并列关系**:

- **Python 前端 ↔ C++ 后端桥接**: `tilelang/engine/lower.py`(编译引擎)是调度中枢,串接 Python 侧 `tilelang/transform/` 与 C++ 侧 `src/transform/` 的 47 个 IR 变换文件;`tilelang/transform/` 与 `src/transform/` 是**双源 Pass 实现**,分别在 Python 与 C++ 层完成 IR 变换。
- **Pass 链 ↔ 单文件实现**: 关键 Pass 链中的 `ascend_lower_parallel_to_vector`、`ascend_memory_planning`、`ascend_sync_insert`、`ascend_combinecv` 与 `src/transform/` 下同名 `.cc` 文件一一对应(如 `ascend_sync_insert.cc` 46KB、`ascend_memory_planning.cc` 24KB);`lower_tile_op` 与 `cross_core_pipeline.cc`(35KB)负责算子降低与跨核流水。
- **代码生成双路径并列**:
  - PTO 路径:`codegen_ascend_pto.cc`(3225 行,主要) → 依赖 `src/tl_templates/` 中的 PTO 模板 → 配合 `tilelang/language/pto.py` 与 `ascend_tile.py`。
  - Ascend C 路径:`codegen_ascend.cc`(2050 行) → 配合 `tilelang/language/ascend.py`。
  - 二者共享 `rt_mod_ascend*.cc` 运行时模块。
- **DSL 原语 ↔ 编译 Pass**: `tilelang/language/` 中的 `parallel.py`、`allocate.py`、`copy_op.py`、`reduce.py`、`gemm.py` 等分别驱动 `loop_vectorize`、`ascend_memory_planning`、`inject_pipeline`、`lower_tile_op` 等 Pass;`ascend_tile.py`(56KB,最大模块)作为顶层封装聚合各原语。
- **支撑模块并列关系**: `tilelang/autotuner/`(自动调优)、`tilelang/carver/`(调度与资源映射)、`tilelang/layout/`(内存布局)、`tilelang/intrinsics/`(硬件内建函数)、`tilelang/profiler/`(性能分析)是围绕主编译流水线的辅助子系统。
- **测试/示例/依赖**: `examples/`(31 类算子示例)与 `testing/python/` 为上述编译链路提供回归用例;`3rdparty/` 提供 TVM 与 pto-isa 依赖,构成 IR 与 PTO ISA 的底层支撑。

---

## 【使用方法】

- **JIT 编译入口**: 使用 `@tilelang.jit` 装饰器(原文核心 API 一节列出)即可启动从 Python DSL 到 NPU 可执行文件的端到端编译流程。
- **核心 API 列表(原文)**:
  - `@tilelang.jit` — JIT 编译装饰器
  - `T.alloc_L1 / alloc_ub / alloc_L0A / alloc_L0B / alloc_L0C` — 多级内存分配
  - `T.copy` — 数据搬运
  - `T.gemm` / `T.mma` — 矩阵计算
  - `T.Parallel` — 向量化
  - `T.Pipelined` — 流水线
  - `T.printf` / `T.dump_tensor` — 调试
- **配置项 / 命令 / 启用方式**: **原文未涉及**(文档仅给出 API 名称与目录结构,未提供具体的命令行、配置文件或参数说明;具体启用细节需参考 `examples/`、`docs/` 或各子模块文档)。
