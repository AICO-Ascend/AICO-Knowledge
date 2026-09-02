# Hadamard 变换算子设计文档

> 仓 `tilelang-ascend` · 路径 `examples_experiment/hadamard_transform/design.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/tilelang-ascend/examples_experiment/hadamard_transform/design.md

# Hadamard 变换算子设计文档 深度解读

## 【定位】

本文档描述如何在 Ascend NPU 平台上,通过 TileLang 的 Developer 模式 + 共享内存(UB)数据交换实现**快速 Hadamard 变换(Fast Walsh-Hadamard Transform)**算子,支持 2~32768 维向量的高效蝶形网络计算,解决"在无 CUDA warp/thread 模型的 NPU 上用块级并行模拟蝶形网络"的问题。

---

## 【技术要点】

1. **算法本质**:利用 Hadamard 矩阵的 Kronecker 积递归定义,采用蝶形网络(butterfly)将 $y = H_n \cdot x$ 的复杂度从 $O(n^2)$ 降到 $O(n \log n)$(共 $\log_2 n$ 级,每级 $n/2$ 对加减)。
2. **平台架构映射**:Ascend NPU 无 CUDA thread/warp,采用 **Block 级并行 + 串行蝶形**;每个 Block 由 `cid`(计算任务 ID,块维度)与 `vid`(Vector 单元索引,**固定为 2**)两个轴标识,计算在 UB(Unified Buffer)中完成,块间数据交换**经 GM 中转**,由 **Host 端串行调用多个 kernel** 协调。
3. **两阶段拆分**:
   - **块内蝶形(hadamard_block_intra)**:`log2(block_size)` 级,数据先 Load 到 `data_ub`,在 UB 内串行完成蝶形再写回 GM。
   - **跨块蝶形(hadamard_cross_block_pair)**:每级**一次 kernel 调用**;同时加载配对的 src/dst 两个 half 到 `data_ub`/`data2_ub`,蝶形加/减结果先写 `tmp_ub` 再写回 GM(共 5 步伪代码)。
4. **维度约束**:输入向量长度 $n$ 必须是 **2 的幂次**,范围 **[2, 32768]**;支持 dtype 为 **float32 / float16 / bfloat16**;默认 `block_size = 1024`。
5. **编程模式**:**Developer 模式**(纯 Vector 算子,无 matmul);通过 `T.alloc_ub` 分配 UB 缓冲;通过 `T.serial` 做蝶形迭代;通过 `TL_ASCEND_AUTO_SYNC` 编译器自动同步。
6. **API 替代关系**:`T.alloc_local` 已从 TileLang-Ascend **移除**;Ascend 上标量 → `T.alloc_var`,Vector 缓冲 → `T.alloc_ub`;`T.alloc_shared` 由编译器自动映射到 L1/UB。

---

## 【关键机制与数据】

### 工作原理

- **蝶形操作的代数表达**(原文伪代码):
  ```
  for each stage i from 0 to log2(n)-1:
      for each pair (k, k + 2^i):
          a = x[k]
          b = x[k + 2^i]
          x[k] = a + b
          x[k + 2^i] = a - b
  ```
- **数据流**(原文):
  - 当 $n \le block\_size$:`GM[A] → UB[data_ub] → butterfly(intra-block serial) → GM[B]`(单 kernel)
  - 当 $n > block\_size$:先调 `hadamard_block_intra` 完成 `log2(block_size)` 级块内蝶形;再依次调 `log2(n) - log2(block_size)` 个 `hadamard_cross_block_pair`,**每一级一个 kernel**,Host 端串行编排。
- **核参数计算**:
  - 块内:`total_blocks = b * (n // block_size)`,`log_block = log2(block_size)`
  - 跨块某 stage `s`:`chunk_size = 1 << (s+1)`、`half = chunk_size // 2`、`num_chunks_per_batch = n // chunk_size`、`total_chunks = b * num_chunks_per_batch`

### 数据流(原文 ASCII 图)
```
n ≤ block_size:
  GM[A] → UB[data_ub] → butterfly(intra-block serial) → GM[B]

n > block_size:
  GM[A] → UB[data_ub] → butterfly(intra-block) → GM[B]
  GM → UB[data_ub/data2_ub] → butterfly(cross-block pair) → GM[B]  (one kernel call per stage)
```

### 性能/数值数据
原文**未给出实测吞吐、benchmark、加速比等性能数字**;性能相关的可量化指标仅来自约束:`n ∈ [2, 32768]`、dtype 列表、默认 `block_size=1024`、每级跨块蝶形 = 1 次 kernel 调用。

---

## 【表格解读】

### 表 1:模式选型影响(原文 §2.3)

| 维度 | 本算子的选择 |
|------|-------------|
| 内存分配 | T.alloc_ub(UB 内存,Vector 缓冲) |
| 计算方式 | T.serial 串行蝶形 + 符号运算(加减) |
| 作用域 | 编译器自动分离,无需手动 T.Scope |
| 同步方式 | Developer 模式自动同步(TL_ASCEND_AUTO_SYNC) |
| 数据交换 | 块内串行蝶形;跨块通过 Host 协调多 kernel 调用经 GM 中转 |

**解读**:此表说明在 Ascend 上,本算子**全程走 UB/Vector 通路**,没有 L1/Scalar 参与显式调度,也不需要手工 scope 与 barrier;同步完全靠编译器策略 + Host 串行 kernel 顺序保证。

### 表 2:块内蝶形公式拆解(原文 §3.1)

| 步骤 | 数学表达 | 说明 |
|------|----------|------|
| 1 | 加载:`data_ub[i] = A[batch, offset + i]` | 从 GM 加载 block_size 个元素到 UB |
| 2 | 块内蝶形:`log2(block_size)` 级迭代 | 在 UB 内串行完成蝶形操作 |
| 3 | 写回:`B[batch, offset + i] = data_ub[i]` | 从 UB 写回 GM |

**解读**:块内蝶形只有 3 步——Load → 串行 butterfly → Store,**单 kernel、单 UB 缓冲**(`data_ub`),in-place 更新。

### 表 3:跨块蝶形公式拆解(原文 §3.1)

| 步骤 | 数学表达 | 说明 |
|------|----------|------|
| 1 | 加载:`data_ub[k] = A[batch, src_offset + k]; data2_ub[k] = A[batch, dst_offset + k]` | 加载配对两个 half 到 UB |
| 2 | 蝶形:`tmp_ub[k] = data_ub[k] + data2_ub[k]` | 蝶形加法,结果写 tmp_ub |
| 3 | 写回上半:`B[batch, src_offset + k] = tmp_ub[k]` | 写回 GM |
| 4 | 蝶形:`tmp_ub[k] = data_ub[k] - data2_ub[k]` | 蝶形减法,结果写 tmp_ub |
| 5 | 写回下半:`B[batch, dst_offset + k] = tmp_ub[k]` | 写回 GM |

**解读**:跨块蝶形需要 **3 个 UB 缓冲**(`data_ub`、`data2_ub`、`tmp_ub`)——前两个保留原始配对数据,`tmp_ub` 复用于加减结果的中转,**避免覆盖源数据**(否则下一步蝶形会读到已污染的输入)。

### 表 4:块内蝶形 TileLang API 映射(原文 §3.2)

| 步骤 | 数学表达 | TileLang API | 参数 | 模式 |
|------|----------|-------------|------|------|
| 1 | 加载 | T.copy | `A[batch, offset:offset+block_size] → data_ub` | Developer |
| 2 | 块内蝶形 | T.serial(log_block) + T.serial 内层 | 蝶形加减操作 | Developer |
| 3 | 写回 | T.copy | `data_ub → B[batch, offset:offset+block_size]` | Developer |

**解读**:块内蝶形**没有任何 matmul/tensor 表达式**,纯靠 `T.serial` 双层循环(外层 stage,内层 chunk 内 half)做加减;`T.copy` 充当 GM↔UB 搬运指令。

### 表 5:跨块蝶形 TileLang API 映射(原文 §3.2)

| 步骤 | 数学表达 | TileLang API | 参数 | 模式 |
|------|----------|-------------|------|------|
| 1 | 加载配对 | T.copy ×2 | `A[src] → data_ub; A[dst] → data2_ub` | Developer |
| 2 | 蝶形加 | T.serial(half) | `tmp_ub[k] = data_ub[k] + data2_ub[k]` | Developer |
| 3 | 写回上半 | T.copy | `tmp_ub → B[src]` | Developer |
| 4 | 蝶形减 | T.serial(half) | `tmp_ub[k] = data_ub[k] - data2_ub[k]` | Developer |
| 5 | 写回下半 | T.copy | `tmp_ub → B[dst]` | Developer |

**解读**:跨块蝶形严格按"Load×2 → 加/写 → 减/写"5 步执行,**加法结果先写回 GM 再做减法**——这是为了避免 `tmp_ub` 被减法覆盖后仍要写上半(因此 `data_ub`/`data2_ub` 在整个 kernel 内必须保持原值)。

### 表 6:TileLang API 可行性(原文 §3.4)

| API | 来源 | 是否可用 | 说明 |
|-----|------|---------|------|
| T.alloc_ub | tilelang/language/allocate.py | ✅ | 用于分配 UB 内存(Vector 缓冲),蝶形计算数据缓冲 |
| T.copy | tilelang/language/copy.py | ✅ | GM↔UB 数据搬运 |
| T.serial | tilelang/language | ✅ | 串行循环,用于蝶形迭代 |
| T.Kernel | tilelang/language/kernel.py | ✅ | Kernel 定义,支持 threads 参数,用法参考 `with T.Kernel(..., threads=2, is_npu=True) as (cid):` |
| T.ceildiv | tilelang/language | ✅ | 整除向上取整 |
| T.barrier_all | tilelang/language/ascend.py | ✅ | 同步屏障(自动同步开启时由编译器插入) |

**解读**:本表是 API 落地的"可行性检查清单"。重点信息:**`T.Kernel` 支持 `threads=2` 参数**(对应 Ascend 上 `vid` 固定 2 个 Vector 单元);`T.barrier_all` 实际不需手动写,编译器在 `TL_ASCEND_AUTO_SYNC` 开启时会自动插入。

### 表 7:输入张量(原文 §4.1)

| 参数名 | Shape | dtype | 说明 |
|--------|-------|-------|------|
| A | (batch, n) | float32 / float16 / bfloat16 | 输入向量,n 必须是 2 的幂次,范围 [2, 32768] |

### 表 8:输出张量(原文 §4.2)

| 参数名 | Shape | dtype | 说明 |
|--------|-------|-------|------|
| B | (batch, n) | float32 / float16 / bfloat16 | 输出向量,shape 与输入相同 |

**解读**:输入/输出 shape/dtype 完全对齐,采用 ping-pong 风格——每个 kernel 读 A 写 B,Host 再把 B 作为下一级 kernel 的输入。

### 表 9:块内中间缓冲(原文 §4.3)

| Buffer 名 | Shape | dtype | 存储层级 | 用途 |
|-----------|-------|-------|----------|------|
| data_ub | (block_size,) | float32 | UB | 块内蝶形数据缓冲 |

### 表 10:跨块中间缓冲(原文 §4.3)

| Buffer 名 | Shape | dtype | 存储层级 | 用途 |
|-----------|-------|-------|----------|------|
| data_ub | (half,) | float32 | UB | 蝶形上半数据(src) |
| data2_ub | (half,) | float32 | UB | 蝶形下半数据(dst) |
| tmp_ub | (half,) | float32 | UB | 蝶形结果临时缓冲 |

**解读**:跨块 kernel 的 UB 用量是 3 × half × sizeof(dtype);注意表中 dtype 全部标 float32,但 §4.1 实际接受 float16/bfloat16,该列在原文里**只列举了 float32**(可能是模板化的示例值,需结合实际 kernel 实例化)。

---

## 【公式解读】

### 公式 1:Hadamard 矩阵递归定义(原文 §1.3)
$$
H_2 = \begin{bmatrix} 1 & 1 \\ 1 & -1 \end{bmatrix}
$$
$$
H_n = H_2 \otimes H_{n/2} = \begin{bmatrix} H_{n/2} & H_{n/2} \\ H_{n/2} & -H_{n/2} \end{bmatrix}
$$
- 符号含义:`$H_n$` 为 $n \times n$ 阶 Hadamard 矩阵;`$\otimes$` 为 Kronecker 积;`$H_2$` 是 2 阶基矩阵。
- 作用:这是 Hadamard 矩阵**自相似构造**的数学基础——任意 2 幂阶矩阵可由 2 阶反复 Kronecker 得到,从而保证快速蝶形算法(`$O(n \log n)$`)的存在性。

### 公式 2:正变换(原文 §1.3)
$$
y = H_n \cdot x
$$
- 符号含义:`$x$` 为输入向量,`$y$` 为输出向量。
- 作用:定义"对输入做 Hadamard 变换"的数学目标;实现上不直接做矩阵乘,而用蝶形网络。

### 公式 3:蝶形操作(原文 §1.4,伪代码)
```
for each stage i from 0 to log2(n)-1:
    for each pair (k, k + 2^i):
        a = x[k]
        b = x[k + 2^i]
        x[k] = a + b
        x[k + 2^i] = a - b
```
- 符号含义:`stage i` 指第 `i` 级蝶形,跨距为 `$2^i$`;`k` 与 `k + 2^i` 是该级的一对配对下标;`x` 既是输入也是输出(in-place)。
- 作用:这是**所有 kernel(块内、跨块)共享的核心操作**——把矩阵-向量乘拆成 `log2(n)` 级"加/减配对";本算子的两个 kernel 都是它的特化(块内版本 in-place;跨块版本为了跨 kernel 边界拆出 `tmp_ub` 中转)。

### 公式 4:复杂度(原文 §1.3)
- 表述:"使用快速蝶形网络算法,计算复杂度从 `$O(n^2)$` 降低到 `$O(n \log n)$`。"
- 符号含义:`$n$` 为向量维度。
- 作用:论证为何要采用蝶形而非直接矩阵乘。

> **注**:文档在 §4.4 "内存搬运路径"处明显被截断(原文档末尾只写到 `intra-block butterfly: GM[A] --T.copy--> UB[data_ub] --serial butterfly--> UB[data_ub] --T.copy-` 即中断),跨块搬运路径及后续章节内容在所给原文中缺失。

---

## 【关联】

文档明确点出的**上下游关联**包括:

1. **与 TileLang-Ascend 内存分配体系的耦合**:本算子用 `T.alloc_ub` 替代已移除的 `T.alloc_local`(`§3.4` 注意栏),与 `T.alloc_var`(标量)、`T.alloc_shared`(由编译器自动映射到 L1/UB,本算子未显式使用)并列存在——是 Ascend 内存 API 选型的下游案例。
2. **与 Developer 模式的耦合**:算子整体走 Developer 模式,依赖 `TL_ASCEND_AUTO_SYNC` 自动同步策略;`T.barrier_all` 由编译器按需插入(用户不显式调用)。
3. **与 Ascend Block/Vector 模型的耦合**:依赖 `T.Kernel(..., is_npu=True)` + `(cid, vid)` 双轴分解,其中 `vid` 固定为 2 个 Vector 单元(`§2.2` 平台特性约束);本算子**只走 `vid == 0` 分支**(见块内 kernel 伪代码 `if vid == 0:`)。
4. **与上层 Host 编排的耦合**:`hadamard_transform_complete`(`§3.3`)在 Host 端组合 `kernel_intra` + `cross_kernels`(`range(log_block, log_n)`)形成完整变换,体现"算子 = 多个 kernel + Host 调度"的分层结构。
5. **内部链接**:原文**无内部链接**(文档自带的链接信息为空)。

---

## 【使用方法】

原文给出了完整的 Python 调用范式(§3.3):

```python
def hadamard_transform_complete(b, n, dtype="float", block_size=1024):
    if n <= block_size:
        kernel = hadamard_block_intra(b, n, n, dtype)
        return lambda x: kernel(x)

    log_n = int(math.log2(n))
    log_block = int(math.log2(block_size))

    kernel_intra = hadamard_block_intra(b, n, block_size, dtype)
    cross_kernels = [
        hadamard_cross_block_pair(b, n, block_size, stage, dtype)
        for stage in range(log_block, log_n)
    ]

    def full_transform(x):
        y = kernel_intra(x)
        for kernel_cross in cross_kernels:
            y = kernel_cross(y)
        return y

    return full_transform
```

- **入口函数**:`hadamard_transform_complete(b, n, dtype="float", block_size=1024)`
- **关键参数**:
  - `b`:batch 维
  - `n`:向量长度,**必须为 2 的幂次,范围 [2, 32768]**
  - `dtype`:`"float"` / `"float16"` / `"bfloat16"`
  - `block_size`:块大小,默认 **1024**;当 `n <= block_size` 时只编译/调用 1 个 intra-block kernel;否则会额外生成 `log2(n) - log2(block_size)` 个 cross-block kernel
- **装饰器**:`@tilelang.jit(out_idx=[1], pass_configs=pass_configs)`,其中 `pass_configs` 由用户从 `tilelang/engine/param.py` 的 `PASS_CONFIGS` 中按需选用
- **Kernel 签名**:`hadamard_block_intra(b, n, block_size, dtype)` / `hadamard_cross_block_pair(b, n, block_size, cross_stage, dtype)`,均在内部用 `T.prim_func` 定义输入输出张量 `(b, n) × dtype`
- **返回**:一个 `lambda x: ...`(n ≤ block_size)或闭包 `full_transform`(n > block_size),逐级把上一 kernel 的输出作为下一 kernel 的输入

原文未提供 CLI/命令行入口、配置文件路径或 README 级别的安装/运行步骤;`pass_configs` 的具体取值也未在文档中给出,需要用户参考 `tilelang/engine/param.py`。
