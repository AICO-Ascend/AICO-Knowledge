# random_1d 算子设计文档

> 仓 `tilelang-ascend` · 路径 `examples_experiment/random_1d/design.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/tilelang-ascend/examples_experiment/random_1d/design.md

# random_1d 算子设计文档深度解读

---

## 【定位】

本文档是 `tilelang-ascend` 仓库中 `random_1d` 算子的完整设计说明,定义了一种基于经典 LCG（线性同余生成器）在 NPU 上高并行生成 int32 伪随机数序列的 TileLang Developer 模式实现方案,涵盖数学公式、性能指标、API 映射、内存规划、Tiling 策略及同步策略。

---

## 【技术要点】

1. **LCG 经典参数 + 3 轮迭代**:采用 `A = 1103515245`、`C = 12345` 的经典 LCG 常量（glibc 同款参数族）,每个元素独立执行 3 轮 `state = A × state + C`,使用 int32 溢出自动截断（模 2^32）实现无依赖纯并行。
2. **Developer 模式 + 自动 Pass 优化**:通过 `pass_configs` 启用 `TL_ASCEND_AUTO_CV_COMBINE`、`TL_ASCEND_AUTO_SYNC`、`TL_ASCEND_MEMORY_PLANNING` 三个 Pass,移除手工 `T.Scope("V")` 与 `T.barrier_all()`,由编译器自动处理 Cube/Vector 分离、屏障插入与 UB 内存规划。
3. **两级并行划分**:`TOTAL_BLOCK_SIZE = VEC_NUM × BLOCK_SIZE = 2 × 128 = 256`,并行度公式为 `num_blocks × VEC_NUM`,即 `M / 256 × 2`,实现 kernel 级 + vid 级双层并行。
4. **纯 Vector 核 + T.copy 批量写回**:整个算子不涉及 Cube 核,核心是 6 个 UB buffer（`idx_ub / state_ub / temp_ub / a_ub / c_ub / seed_ub`）的 element-wise 运算,最终通过 `T.copy` 一次性写回 GM。
5. **API 参数顺序关键约定**:TileLang 的 `T.tile.add` / `T.tile.mul` 采用**首参为 dst** 的语义（`dst = src0 op src1`）,与常见 NumPy/PyTorch 风格不同,文档明确标注此为常见错误点。
6. **大规模数据带宽峰值 533 MB/s**:M=65536 时吞吐量达到 533 MB/s,被文档定性为"接近硬件带宽极限";小数据量（<4K）则 kernel launch overhead 占主导。

---

## 【关键机制与数据】

### 工作原理

算子采用 **per-element 独立计算 + 向量化 LCG 迭代** 工作流:

1. **初始化阶段**:用 `T.tile.fill` 把 LCG 常量 `A`、`C` 和种子 `seed` 各自填充成 `[BLOCK_SIZE]` 长度的同值 buffer,用 `T.tile.arith_progression(idx_ub, global_base, 1, block_size)` 生成与全局位置对应的等差数列索引。
2. **状态初始化**:`T.tile.add(state_ub, idx_ub, seed_ub)` 实现 `state = global_idx + seed`,得到每个元素的 LCG 起始状态。
3. **LCG 3 轮迭代**:`for _ in range(3)` 循环内执行 `mul(temp_ub, state_ub, a_ub)` → `add(state_ub, temp_ub, c_ub)`,完全 element-wise,无跨元素依赖。
4. **批量写回**:`T.copy(state_ub, output[base_offset:base_offset + block_size])` 一次性将 128 个 int32 元素搬出 UB 至 GM,充分利用 NPU DMA 带宽。

### 数据流（原文图示）

```
初始化阶段:
  T.tile.fill → a_ub=[A,A,...,A]
  T.tile.fill → c_ub=[C,C,...,C]
  T.tile.fill → seed_ub=[seed,...]
  T.tile.arith_progression → idx_ub=[global_base, global_base+1, ..., global_base+127]
计算阶段:
  idx_ub + seed_ub → state_ub      # state = global_idx + seed
  LCG 循环(3 轮, 向量化):
    state_ub × a_ub → temp_ub
    temp_ub + c_ub → state_ub
输出阶段:
  T.copy → 128 元素一次性写入 GM
```

### 性能数据（原文: Section 1.5）

| M | 并行度 | 平均耗时 | 吞吐量 |
|---|---|---|---|
| 1024 | 4×2 = 8 | 0.46 ms | 8.5 MB/s |
| 4096 | 16×2 = 32 | 0.52 ms | 29.8 MB/s |
| 16384 | 64×2 = 128 | 0.46 ms | 136.4 MB/s |
| 65536 | 256×2 = 512 | 0.47 ms | **533.0 MB/s** |

原文分析:小数据量（M < 4K）kernel launch overhead 占比大;大数据量（M > 16K）接近硬件带宽极限;并行度随 M 线性增长,可充分利用 NPU 多核。

### UB 容量（原文: 196KB 上限,本文 6 个 buffer 总计 ≈ 3KB）

每个 UB buffer: `128 × 4B = 512B`,6 个 buffer 总计 `6 × 512B = 3072B ≈ 3KB`,远小于 196KB 上限,在安全范围内。

---

## 【表格解读】

### 表 1: 计算特征分析（Section 1.3）

| 维度 | 分析结果 |
|------|---------|
| **计算类型** | 纯 Vector（element-wise 乘加运算） |
| **复杂度级别** | 单步（arith_progression + fill + 3轮 mul/add + 批量 copy） |
| **动态 shape** | M 为参数维度，支持任意大小 |
| **核间协作** | 纯 Vector 核，无需 Cube 核 |
| **并行模式** | 多 kernel + 多 vid 高并行 |
| **数据搬运** | T.copy 批量写回，充分利用 NPU 带宽 |

**逐行解读**:
- **计算类型**:完全是 Vector 核可处理的 element-wise 操作,不存在 GEMM/Conv 等 Cube 核场景。
- **复杂度级别**:原文将单条算子拆解为"等差数列 + 3 次常量填充 + 3 轮 mul/add 循环 + 1 次 T.copy" 6 类原语组合。
- **动态 shape**:M 作为参数传入,理论上支持任意正整数（实际会被对齐到 `TOTAL_BLOCK_SIZE` 边界）。
- **核间协作**:无 Cube 核参与,因此选择 Developer 模式而非依赖 Cube 库的更高级封装。
- **并行模式**:两层并行——kernel 数（grid）+ 每个 kernel 内 vid 数,VEC_NUM=2 时总并行度 = `2 × num_blocks`。
- **数据搬运**:关键是输出阶段用 `T.copy` 整段搬出而非 `T.serial` 循环,这是性能差异的核心来源（533 MB/s vs 低效版本）。

---

### 表 2: 典型配置示例（Section 1.4）

| 参数 | 值 | 说明 |
|------|-----|------|
| M | 65536 | 输出元素数量（推荐大数据量） |
| seed | 42 | 随机种子 |
| BLOCK_SIZE | 128 | 每个 vid 处理的元素数 |
| VEC_NUM | 2 | 每个 kernel 的 Vector 单元数 |
| TOTAL_BLOCK_SIZE | 256 | 每个 kernel 处理的总元素数 = VEC_NUM × BLOCK_SIZE |
| num_blocks | 256 | kernel 数量 = M / TOTAL_BLOCK_SIZE |
| 总并行单元 | 512 | num_blocks × VEC_NUM |

**逐行解读**:
- M=65536 是 Section 1.5 中达到峰值吞吐量的代表性配置。
- BLOCK_SIZE=128 与 VEC_NUM=2 共同构成 `TOTAL_BLOCK_SIZE=256` 这一 kernel 处理单元粒度。
- num_blocks=256 来自 `M / TOTAL_BLOCK_SIZE = 65536 / 256`。
- 总并行单元 512 = `256 kernels × 2 vids/kernel`,这是 NPU 上的逻辑并行槽位数。

---

### 表 3: 性能指标（Section 1.5）

| 数据量 M | 并行度 (kernels × vids) | 平均耗时 | 吞吐量 |
|---------|------------------------|---------|--------|
| 1024 | 4 × 2 = 8 | 0.46 ms | 8.5 MB/s |
| 4096 | 16 × 2 = 32 | 0.52 ms | 29.8 MB/s |
| 16384 | 64 × 2 = 128 | 0.46 ms | 136.4 MB/s |
| 65536 | 256 × 2 = 512 | 0.47 ms | **533.0 MB/s** |

**逐行解读**:
- M=1024 时并行度仅 8,平均耗时仍是 0.46 ms,说明存在显著的固定 launch overhead,导致吞吐量只有 8.5 MB/s。
- M=4096 耗时反而略升到 0.52 ms（最大值）,原文未解释此现象,推测与调度切换有关。
- M 增长 4 倍时吞吐量近似增长 4 倍（如 4096→16384: 29.8→136.4 MB/s,约 4.58×）,验证"耗时常数 + 带宽线性"特性。
- M=65536 加粗显示 **533.0 MB/s** 是本文档重点突出的最优吞吐量,"接近硬件带宽极限"。

---

### 表 4: Developer 模式选型理由（Section 2.2）

| 因素 | 分析 |
|------|------|
| 无 GEMM 计算 | 纯 element-wise 运算，不需要 Cube 核 |
| 需要精细 buffer 管理 | 多个临时 buffer（state_ub, temp_ub, a_ub 等） |
| 需要动态偏移 | 使用 `cid * TOTAL_BLOCK_SIZE + vid * block_size` 组合表达式 |
| 启用 pass_configs | 利用编译器自动优化（CV 融合、同步、内存规划） |

**逐行解读**:
- 四个理由均为"放弃高层封装、改用 Developer 模式"的动因。
- "动态偏移"指 kernel 内通过 `cid * TOTAL_BLOCK_SIZE + vid * block_size` 在每个 kernel 实例内独立计算 base_offset,而非由上层 API 注入。

---

### 表 5: Pass 功能说明（Section 2.3）

| Pass | 功能 |
|------|------|
| TL_ASCEND_AUTO_CV_COMBINE | 自动融合连续的 mul+add 操作，减少中间存储开销 |
| TL_ASCEND_AUTO_SYNC | 自动在必要位置插入 barrier，无需手动同步 |
| TL_ASCEND_MEMORY_PLANNING | 自动内存规划，优化 UB 使用 |

**逐行解读**:
- `AUTO_CV_COMBINE` 把 mul 和后续 add 融合成单条 CV 指令,消除 `temp_ub` 的中间写回需求。
- `AUTO_SYNC` 替代原手写 `T.barrier_all()`,降低出错概率。
- `AUTO_MEMORY_PLANNING` 让编译器复用 6 个 buffer 的内存页,实际 UB 占用可能小于 Section 4.4 估算的 3KB 上限。

---

### 表 6: 核心计算步骤 → TileLang API 映射（Section 3.1）

| 计算步骤 | PyTorch 参考 | TileLang API |
|---------|-------------|--------------|
| 生成本地索引序列 | `torch.arange(block_size)` | `T.tile.arith_progression(idx_ub, global_base, 1, block_size)` |
| 填充 LCG 常量 A | `A = 1103515245` | `T.tile.fill(a_ub, LCG_A)` |
| 填充 LCG 常量 C | `C = 12345` | `T.tile.fill(c_ub, LCG_C)` |
| 填充种子 | `seed = 42` | `T.tile.fill(seed_ub, seed)` |
| **state = idx + seed** | `state = global_idx + seed` | `T.tile.add(state_ub, idx_ub, seed_ub)` |
| **temp = state × A** | `temp = state * A` | `T.tile.mul(temp_ub, state_ub, a_ub)` |
| **state = temp + C** | `state = temp + C` | `T.tile.add(state_ub, temp_ub, c_ub)` |
| 存储输出 | `output[i] = state` | `T.copy(state_ub, output[base_offset:base_offset + block_size])` |

**逐行解读**:
- 索引列生成用 `arith_progression` 而非 PyTorch 风格 `arange`,首参是 dst buffer,后三参是 (first, diff, count)。
- 三次 `fill` 把标量常量广播成长度为 BLOCK_SIZE 的 UB buffer,为后续向量计算做准备。
- 加法与乘法的 API 签名是 `T.tile.{op}(dst, src0, src1)`,与 PyTorch 的 `torch.add(a, b)` 中 dst 在最后相反,文档 Section 3.3 专门强调这是易错点。
- 最后一行用 `T.copy` 而非 `for i in T.serial` 循环写入,是性能关键点。

---

### 表 7: 输入张量（Section 4.1）

| 张量 | Shape | Dtype | 说明 |
|------|-------|-------|------|
| 无输入张量 | - | - | 本算子仅输出，不读取输入数据 |

**逐行解读**:算子是"无中生有"的纯生成算子,所有输入(seed、A、C)通过函数参数传入,运行时无 GM 读操作。

---

### 表 8: 输出张量（Section 4.2）

| 张量 | Shape | Dtype | 说明 |
|------|-------|-------|------|
| output | `[M_aligned]` | int32 | 生成的随机数（1D tensor） |

**逐行解读**:输出 shape 为 `M_aligned` 而非 `M`,`M_aligned` 会向上对齐到 `TOTAL_BLOCK_SIZE` 倍数（实际由 `T.copy` 切片决定可见范围,文档未给出 masking 方案）。

---

### 表 9: Block 划分策略（Section 5.1）

| 维度 | 策略 | 说明 |
|------|------|------|
| **Grid** | `T.Kernel(num_blocks, is_npu=True)` | 每个 kernel 处理 TOTAL_BLOCK_SIZE 个元素 |
| **vid 分块** | `BLOCK_SIZE = 128` | 每个 vid 处理 BLOCK_SIZE 个元素 |
| **VEC_NUM** | `2` | 每个 kernel 有 2 个 vid 并行执行 |
| **TOTAL_BLOCK_SIZE** | `256` | 每个 kernel 总处理量 = VEC_NUM × BLOCK_SIZE |
| **并行度计算** | `num_blocks × VEC_NUM` | 总并行单元数，随 M 线性增长 |

**逐行解读**:Grid 维度为 `num_blocks = M_aligned / 256`,kernel 内 2 个 vid 各自处理 128 个不重叠区间,组合表达式为 `cid * 256 + vid * 128`。

---

### 表 10: Tile Shape 设计（Section 5.2）

| Buffer | Shape | 说明 |
|--------|-------|------|
| idx_ub | `[128]` | 等差数列 [base, base+1, ..., base+127] |
| a_ub | `[128]` | 填充值 A（批量填充） |
| c_ub | `[128]` | 填充值 C（批量填充） |
| seed_ub | `[128]` | 填充值 seed（批量填充） |
| state_ub | `[128]` | 计算结果 |
| temp_ub | `[128]` | 临时结果 |

**逐行解读**:所有 UB 形状统一为 `[BLOCK_SIZE]=[128]`,这是 SIMD/Vector 核友好的对齐大小;`temp_ub` 在开启 `AUTO_CV_COMBINE` 时可能被融合掉。

---

### 表 11: 调度选择（Section 6.2）

| 循环/操作 | 调度类型 | 理由 |
|----------|---------|------|
| 初始化 fill | `T.tile.fill` | Vector 核批量填充，128 元素同时操作 |
| 等差数列 | `T.tile.arith_progression` | Vector 核生成序列，128 元素同时生成 |
| element-wise | `T.tile.mul/add` | Vector 核自动向量化，128 元素同时计算 |
| 输出写入 | `T.copy(state_ub, output[...])` | **批量写回**，充分利用 NPU 带宽 |

**逐行解读**:全文无 `T.serial` 循环,所有操作均向量化;输出阶段明确加粗"批量写回"是 Section 6.3 强调的关键优化点。

---

## 【公式解读】

### 公式 1: LCG 核心迭代（Section 1.2, 伪代码形式）

```
对于每个元素 i (i = 0, 1, ..., M-1):
    state = seed + i               # 初始状态（每个元素独立）
    state = A * state + C          # LCG 第 1 轮
    state = A * state + C          # LCG 第 2 轮
    state = A * state + C          # LCG 第 3 轮
    output[i] = state              # 输出随机数
```

**符号含义**:
- `i ∈ [0, M)`:元素在输出数组中的全局索引,用于给每个元素一个独立可复现的 LCG 起始状态。
- `seed`:用户传入的随机种子（典型值 42）,用作状态线性偏移量。
- `A = 1103515245`:LCG 乘数,glibc 经典参数;符号含义是状态放大因子。
- `C = 12345`:LCG 增量,glibc 经典参数;符号含义是每轮必加的偏移。
- `state`:当前 LCG 内部状态变量,逐轮更新。
- `output[i]`:第 i 个元素的最终随机值,直接取 3 轮迭代后的 state。

**作用**:这是整篇文档的核心数学定义,刻画了 random_1d 的输出分布生成方式——注意 state 是 int32,自然模 2^32 溢出截断,因此每元素独立且确定。

---

### 公式 2: M 对齐与并行划分（Section 6.1, Python 代码内）

```
M_aligned = (M + TOTAL_BLOCK_SIZE - 1) // TOTAL_BLOCK_SIZE * TOTAL_BLOCK_SIZE
num_blocks = M_aligned // TOTAL_BLOCK_SIZE
global_base = cid * TOTAL_BLOCK_SIZE + vid * block_size
base_offset = cid * TOTAL_BLOCK_SIZE + vid * block_size
```

**符号含义**:
- `M`:用户请求的元素数（可能非 256 倍数）。
- `TOTAL_BLOCK_SIZE = 256`:kernel 处理粒度。
- `M_aligned`:向上对齐到 256 的倍数,保证 num_blocks 整除。
- `num_blocks`:Grid 维度,即 kernel 实例数。
- `cid`/`vid`:kernel 内坐标,(cid, vid) 唯一确定一个并行单元。
- `global_base` / `base_offset`:第 (cid, vid) 个单元负责的输出区间起始地址,两者数值相等（文档中两处表达式一致）。

**作用**:`global_base` 在 `arith_progression` 中用于生成本地索引,`base_offset` 在 `T.copy` 中用于切片回写。

---

### 公式 3: UB 容量估算（Section 4.4, 简单算术）

```
idx_ub:       128×4B = 512B
state_ub:     128×4B = 512B
temp_ub:      128×4B = 512B
a_ub:         128×4B = 512B
c_ub:         128×4B = 512B
seed_ub:      128×4B = 512B
总计 ≈ 3KB << 196KB（安全范围内）
```

**符号含义**:
- `128`:BLOCK_SIZE,即每个 buffer 元素数。
- `4B`:int32 dtype 字节数。
- `196KB`:NPU 单核 UB 上限（典型硬件值,文档隐含）。
- `3KB`:6 个 buffer 总占用,`<< 196KB` 表示远小于。

**作用**:验证 UB 内存规划不会超限,是 Tiling 方案可行性的资源约束检查。

---

### 公式 4: 并行度与吞吐量（Section 1.4 / 1.5, 派生公式）

```
并行单元总数 = num_blocks × VEC_NUM = (M / TOTAL_BLOCK_SIZE) × 2 = M / 128
```

**符号含义**:
- `num_blocks = M / 256`:kernel 实例数。
- `VEC_NUM = 2`:每个 kernel 内 vid 数。
- `M / 128`:等价的"每个并行单元处理 128 元素"视图。

**作用**:Section 1.5 性能表中所有"并行度"列均由此式计算(如 M=65536 → 65536/128=512)。

---

## 【关联】

文档用户给定的文末内部链接信息为 **(无)**,因此本文档在仓库 `examples_experiment/random_1d/` 路径下属于**自包含**的设计说明。它与 `tilelang-ascend` 框架的关联主要通过以下 API 接触面体现:

1. **TileLang Python 装饰器**:`@tilelang.jit(out_idx=[-1], pass_configs=pass_configs)` —— out_idx=[-1] 表示输出 shape 末维由运行时推导,这是 tilelang-ascend 框架的 JIT 入口约定。
2. **Pass 系统依赖**:`PassConfigKey.TL_ASCEND_AUTO_CV_COMBINE / AUTO_SYNC / MEMORY_PLANNING` 是 tilelang-ascend 编译器的基础 Pass,本文档依赖它们,且 Section 6.1 标题明确指出这是相对"旧版本"的关键变化。
3. **NPU 硬件抽象**:`is_npu=True` 标志、`T.alloc_ub`、`T.Kernel(cid, vid)` 二元组语义,这些是 tilelang-ascend 框架对 Ascend NPU 的硬件特定抽象。
4. **对比"旧版本"**:Section 6.3 的代码对比块存在 `T.serial(block_size)` 旧实现,文档本身未给出旧实现文件路径,但提示该算子历史上经历过"逐元素写回"到"批量 copy"的性能重构。

文档**未涉及**与 `tilelang-ascend` 仓库其他 module（如 GEMM、Conv、Attention 等算子）的直接接口,本身是一个独立的 element-wise 教学/基准算子。

---

## 【使用方法】

### 调用入口

文档 Section 6.1 给出了完整的 JIT 函数签名:

```python
@tilelang.jit(out_idx=[-1], pass_configs=pass_configs)
def random_1d(M, block_size, seed, lcg_a, lcg_c):
    ...
    return main
```

**调用方式**（根据文档可推导）:
- `M`:输出元素总数（向上对齐到 256 倍数,实际由 `M_aligned` 内部处理）。
- `block_size`:典型值 `128`。
- `seed`:随机种子（典型示例 `42`）。
- `lcg_a`:典型值 `1103515245`（虽文档未显式约束,但 Section 1.2 已说明这是经典 LCG 参数）。
- `lcg_c`:典型值 `12345`。

### 启用方式

文档 Section 2.3 给出**启用优化 Pass** 的配置:

```python
pass_configs = {
    tilelang.PassConfigKey.TL_ASCEND_AUTO_CV_COMBINE: True,  # 自动融合 mul+add
    tilelang.PassConfigKey.TL_ASCEND_AUTO_SYNC: True,        # 自动插入 barrier
    tilelang.PassConfigKey.TL_ASCEND_MEMORY_PLANNING: True,  # 自动内存规划
}
```

### 配置项与命令

| 配置维度 | 关键参数 | 典型值 | 来源 |
|---|---|---|---|
| 输出规模 | M | 65536（推荐大数据量） | Section 1.4 |
| 调度粒度 | BLOCK_SIZE / VEC_NUM / TOTAL_BLOCK_SIZE | 128 / 2 / 256 | Section 1.4、5.1 |
| 随机源 | seed / lcg_a / lcg_c | 42 / 1103515245 / 12345 | Section 1.2、1.4 |
| 编译优化 | AUTO_CV_COMBINE / AUTO_SYNC / MEMORY_PLANNING | True × 3 | Section 2.3 |
| 同步方式 | 手动 vs Auto Sync | 启用 AUTO_SYNC 后无需 `T.barrier_all()` | Section 6.1 |
| 输出写回 | T.copy vs T.serial 循环 | 使用 `T.copy(state_ub, output[base_offset:base_offset + block_size])` | Section 6.3 |

### 注意事项（原文 Section 3.3 显式提示）

- `T.tile.add(dst, src0, src1)` 而**非** `T.tile.add(src0, src1, dst)`:`dst` 必须为首参。
- `T.tile.mul(dst, src0, src1)` 同理。

### 文档截断说明

> ⚠️ **原始文档在 Section 7.1 表格处截断**:原文以 `| TL_ASCE` 结束(疑似 `TL_ASCEND_AUTO_SYNC` 的表格行被截断),Section 7.1 标题为"自动同步（pass_configs）",但具体同步策略的剩余章节内容未完整提供,故本解读未对 7.1 之后内容做推论,涉及该部分的具体数据原文中无。

### 原文未涉及

- CLI 启动命令、配置文件路径、环境变量——原文**未涉及**。
- 多卡/分布式部署方式——原文**未涉及**。
- 算子的反向/梯度/校验工具——原文**未涉及**（LCG 不可微,设计上无梯度）。
- 与其他 random 算子（如 Philox、uniform/normal 分布）的对比——原文**未涉及**。
