# Auto Blockify

> 仓 `ascendnpu-ir` · 路径 `docs/source/en/developer_guide/features/AutoBlockify/AutoBlockify.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/ascendnpu-ir/docs/source/en/developer_guide/features/AutoBlockify/AutoBlockify.md

# AutoBlockify 文档深度解读

## 【定位】

这篇文档描述了 AscendNPU IR 中 **Auto Blockify Pass（完整名 AutoBlockifyParallelLoop）** 的能力：当算子所需的逻辑 block 数远大于硬件可用物理 block 数时，该 Pass 通过在 IR 中引入额外的一层外层循环，将原本"逻辑 block 1-to-1 映射到物理 block"导致的高额调度开销，转化为"有限物理 block 多次轮转"的执行模式，从而减少调度、提升性能。

---

## 【技术要点】

1. **问题场景量化指标**：在 AscendNPU IR 架构经验中，**可用物理 block 数 < 50，而逻辑 block 数可达 500+**，构成 "10x 场景"，此时加速可超过原始速度的 2 倍以上。
2. **核心变换逻辑**：Pass 将 IR 中的 `block.idx` 使用模式改写为嵌套循环：
   - `outer ∈ [0, ceildiv(logical_block_dim, physical_block_dim))`
   - `inner ∈ [0, physical_block_dim)`，并直接作为 `block.idx`
   - `use(min(outer * physical_block_dim + inner, logical_block_dim))`
3. **Triton 启用方式**：在 triton-ascend 环境下通过环境变量 **`TRITON_ALL_PARALLEL`** 激活，该环境变量会"锁定 block 数"并自动调用带有正确 flag 的编译命令。
4. **命令行启用方式**：
   - `bishengir-compile` 加 flag：**`--enable-auto-blockify-loop`**
   - `bishengir-opt` 直接调用：**`--auto-blockify-parallel-loop`**
5. **必备 IR 前提**：Pass 通过 **`kLogicalBlockNumAttr`**（在 IR 中表现为 `logical_block_num` 属性）获取逻辑 block 数；必须存在 **`hivm.get_block_idx`** 操作；如果这些缺失，Pass 会失败。
6. **blockdim 设置要求**：启用 AutoBlockify 后，调用 device kernel 时必须将 blockdim 改为 **max physical block dim**，以使 `get_block_idx` 的输出范围变为 `[0, physical_block_num)`，由外层 `outer` 循环补全缺失索引。

---

## 【关键机制与数据】

### 工作原理（原文还原）

- **原始模式**（等价于）：
  ```
  block.idx = hivm.get_block_idx
  use(block.idx)
  ```
  即 `for block.idx from 0,...,logical_block_num` 直接使用。

- **Triton 适配器加 `TRITON_ALL_PARALLEL` 后的不完整逻辑**：
  ```
  for block.idx from 0,...,physical_block_num   <- from get_block_idx
      use(block.idx)
  ```
  由于 `logical num > physical num`，逻辑上会缺失索引，必须靠 Auto Blockify 补全外层循环。

- **Auto Blockify 完成后的最终逻辑**：
  ```
  for outer from 0,...,ceildiv(logical_block_dim, physical_block_dim)
      for inner from 0,...,physical_block_dim  <- get as block.idx
          use(min(outer * physical_block_dim + inner, logical_block_dim))
  ```

### 数据流关键点

- `annotation.mark %1 {logical_block_num} : i32` —— 这一句在示例 IR 中被显式标注，注释为 `// This logical_block_num is the original large number`，是 Pass 寻找 `kLogicalBlockNumAttr` 值的来源。
- `%2 = hivm.hir.get_block_idx -> i64` —— 配合调用时使用 max physical block dim，使返回值范围变 `[0, physical_block_num)`，作为 inner 索引。
- 输出侧会被改写为按 `min(outer * physical_block_dim + inner, logical_block_dim)` 进行安全的越界保护使用。

### 性能数据（原文）

- 原文："**Physical is < 50, logical may be 500+**"
- 原文："**In these 10x scenarios the acceleration can be over double the original speed**"
- 即：当逻辑 block 数与物理 block 数比例达 10× 量级时，加速 > 2×。

### Triton 适配器联动（原文）

- 原文："there is a pass called **`TritonGlobalKernelArgsToHIVMOpPass`** which will automatically make sure there is value marked with `logical_block_num` and create the `get_block_idx` op needed."
- 该 Pass 由 Triton 前端在设置好 `TRITON_ALL_PARALLEL=1` 后自动调用，是 Auto Blockify 在 Triton 流水线中能"即插即用"的关键。

---

## 【表格解读】

**原文无表格**（文档中未出现参数表、性能对比表或配置项表；唯一的"表格状"信息是嵌入在示例 MLIR module attribute 中的 `dlti.target_system_spec` 设备规格参数列表，但这是示例 IR 而非独立表格，故不进行表格化逐行解读）。

为完整性，列出示例 IR 中的设备规格参数（原文逐字）：

| 参数名 | 数值（原文） |
|---|---|
| `AI_CORE_COUNT` | 20 |
| `CUBE_CORE_COUNT` | 20 |
| `VECTOR_CORE_COUNT` | 40 |
| `UB_SIZE` | 1572864 |
| `L1_SIZE` | 4194304 |
| `L0A_SIZE` | 524288 |
| `L0B_SIZE` | 524288 |
| `L0C_SIZE` | 1048576 |
| `UB_ALIGN_SIZE` | 256 |
| `L1_ALIGN_SIZE` | 256 |
| `L0C_ALIGN_SIZE` | 4096 |
| `hivm.module_core_type` | `AIV` |

---

## 【公式解读】

原文给出的核心算法公式（伪代码逐字保留）：

```plaintext
for outer from 0,...,ceildiv(logical_block_dim, physical_block_dim)
    for inner from 0,...,physical_block_dim  <- get as block.idx
        use(min(outer * physical_block_dim + inner, logical_block_dim))
```

| 符号 | 含义与作用 |
|---|---|
| `outer` | 外层循环变量，控制"第几轮"block 调度；取值范围 `[0, ceildiv(logical_block_dim, physical_block_dim))`，负责覆盖所有超出物理 block 容量的逻辑索引 |
| `inner` | 内层循环变量，直接复用为 `block.idx`；取值范围 `[0, physical_block_dim)`，对应硬件单次调度最多能容纳的物理 block 数 |
| `logical_block_dim` | 用户在 IR 中通过 `kLogicalBlockNumAttr`（即示例 IR 里的 `logical_block_num`）标注的"原始逻辑 block 数"，是 Pass 改写的总目标规模 |
| `physical_block_dim` | 硬件实际可用的最大物理 block 数，由 kernel launch 时设定的 blockdim 决定；`inner` 范围直接由其决定 |
| `ceildiv(logical_block_dim, physical_block_dim)` | 向上取整除法，表示"用 `physical_block_dim` 个 block 跑完所有 `logical_block_dim` 个工作所需的最少轮次"，即外层循环次数 |
| `outer * physical_block_dim + inner` | 将二维索引 `(outer, inner)` 线性化，映射回原始的"逻辑 block 全局索引" |
| `min(..., logical_block_dim)` | 越界保护：保证线性索引不超过 `logical_block_dim`，避免最后一次循环不满一轮时访问非法索引 |
| `use(...)` | 对应原 IR 中所有使用 `block.idx` 的位置，Pass 将其统一改写为使用线性化且受 `min` 保护的新表达式 |

原文同时还给出了两个"等价但更朴素"的等价描述，分别对应原始调度模式与 Triton `TRITON_ALL_PARALLEL` 单独使用时的"不完整"模式，共同构成 Pass 改写前后对比。

---

## 【关联】

- **上游/前端**：Triton 适配器（triton-ascend），通过环境变量 **`TRITON_ALL_PARALLEL`** 启用；该环境变量会"锁定 block 数"并自动发起带正确 flag 的编译命令。
- **同级 Pass（在 Triton 流水线中）**：`TritonGlobalKernelArgsToHIVMOpPass` —— 负责自动注入 `logical_block_num` 属性值，并创建所需的 `hivm.get_block_idx` 操作；它是 AutoBlockify 在 Triton 路径下能"无前置准备即用"的依赖。
- **下游调用工具**：
  - `bishengir-compile`：高层编译入口，使用 `--enable-auto-blockify-loop` 启用；
  - `bishengir-opt`：底层 MLIR 工具，使用 `--auto-blockify-parallel-loop` 直接调用该 Pass（Pass 全名 `AutoBlockifyParallelLoop`）。
- **设备/Hardware Spec 上下文**：示例 IR 中以 `dlti.target_system_spec` 嵌入 `hacc.target_device_spec`，列出 `AI_CORE_COUNT = 20`、`VECTOR_CORE_COUNT = 40`、`UB_SIZE = 1572864`、`L1_SIZE = 4194304` 等参数，标定了此 Pass 面向的硬件能力上界。
- **作用 Op**：依赖并改写 `hivm.hir.get_block_idx`、`annotation.mark {logical_block_num}` 等操作。

---

## 【使用方法】

### 1. Triton 前端启用（推荐路径，原文有）

设置环境变量：
```bash
TRITON_ALL_PARALLEL=1
```
该环境变量会自动完成 block 锁定并以正确 flag 调用编译器，无需手动配置其余步骤。

### 2. bishengir-compile 启用（原文有）

```bash
bishengir-compile --enable-auto-blockify-loop <其它参数>
```

### 3. bishengir-opt 直接调用（原文有）

```bash
bishengir-opt --auto-blockify-parallel-loop <输入.mlir>
```

### 4. 必备前置条件（原文有）

- **必须存在 `kLogicalBlockNumAttr`**：IR 中需要有带 `logical_block_num` 属性的 `annotation.mark` 操作；如果不提供，Pass 调用时会失败。
- **必须存在 `hivm.get_block_idx` 操作**：作为 block 索引源；Triton 路径下由 `TritonGlobalKernelArgsToHIVMOpPass` 自动生成。
- **必须调整 blockdim**：启用 AutoBlockify 时，调用 device kernel 时应按 **max physical block dim** 启动，使得 `get_block_idx` 输出范围为 `[0, physical_block_num)`，再由外层 `outer` 循环补全。

> 原文备注：若不走 Triton 适配器，使用者需自行保证 block dim 与上述逻辑一致。

## 图文联合解读

- `AutoBlockify.jpg`: **图示解读：**

1) **画面结构**：上半"Normal Scheduling"中n个逻辑块（1,2,...,m,m+1,...,n）通过红色箭头前m个一对一映射到m个物理块，剩余逻辑块悬空；下半"Using Auto Blockify"展示三组相同的m个物理块（灰底圆角框），红色弧形箭头标注"Create outer loop"和"For: NumLogicBlock/Physical"，表示物理块被循环复用。

2) **技术结论**：当逻辑块数n远大于物理块数m时，传统调度需复杂映射；而Auto Blockify通过引入外层循环，让每次迭代内m个逻辑块仍1-to-1对应m个物理块，省去调度开销。

3) **与文档关系**：直观印证了"physical<50、logical 500+时加速超2倍"的论点，呼应算法伪代码的outer/inner双层循环与min截断逻辑。
