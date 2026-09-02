# T.Parallel on TileLang-Ascend

> 仓 `tilelang-ascend` · 路径 `docs/tutorials/t_parallel.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/tilelang-ascend/docs/tutorials/t_parallel.md

# 「T.Parallel on TileLang-Ascend」深度解读

## 【定位】

这篇文档系统阐述 TileLang-Ascend 中 `T.Parallel` 原语的设计目标、语法用法与支持的运算语义，重点解决"如何在 Ascend 核函数中以统一的 IR 抽象表达瓦片内（intra-tile）向量级数据并行计算"的问题，使开发者既能通过符号数学 API 编写可移植核函数，又能与 AscendC 特有的向量化能力（`T.tile.xxx`）协同使用。

---

## 【技术要点】

1. **原语定位**：`T.Parallel` 是 TileLang 中表达"瓦片内逐元素并行计算"的 IR 原语（**primitive**），抽象了数据并行的循环语义并隐藏硬件细节，在 Ascend 上对应核函数 Compute 阶段的向量化语义。
2. **Ascend 典型计算流**：Split 大张量成 tile → Load 到片上 **UB (Unified Buffer)** → Load → Compute → Store；Compute 阶段对 tile 内所有元素使用向量化指令。
3. **两层编程范式并存**：
   - 符号 API 路径：在 `T.Parallel` 内调用 `T.exp` / `T.log` / `T.max` 等 → 跨 CPU / GPU / Ascend 后端可移植。
   - AscendC 显式路径：通过 `ascend_tile.py` 包装的 `T.tile.add`、`T.tile.exp` 等 tile-level 向量指令。
4. **复杂表达式自动拆解**：`T.Parallel` 会对如 `a*b + a/b` 这类表达式分配 **临时缓冲区**（`c_tmp_0`、`c_tmp_1`）将其拆成多条简单语句；临时缓冲区大小与 tile 相同，原文**强烈建议开启 automatic buffer reuse** 以避免空间浪费。
5. **多维度与广播支持**：
   - 支持 1D / 2D（及更高维）`T.Parallel` 迭代；
   - 原生支持向量-标量二元运算；
   - 支持按行广播（`a_ub[i,j] * b_ub[i]`，`b_ub.shape = (block_M // VEC_NUM,)`）；
   - 支持"维度不匹配"的右侧维度扩展（`b_ub[j] + 5`，其中 `b_ub` 为 1D、`c_ub` 为 2D），但索引须为简单变量或表达式。
6. **行-列混合模式（Row-Split）**：通过外层 `for i in range(...)` 串行遍历行，内层 `for j in T.Parallel(...)` 并行遍历列，可在不需要整瓦片并行时进行"部分并行化"。

---

## 【关键机制与数据】

### IR 层工作原理
- `T.Parallel` 在 IR 层级抽象并行循环，描述数据并行语义，对应 Ascend Compute 阶段的向量化执行；其语义不直接绑定到某一具体硬件指令，而是通过后续 codegen 映射为 AscendC 向量指令。
- 用户既可写高级符号表达式（`+`、`*`、`T.max` 等），也可写 AscendC tile-level intrinsic（`T.tile.exp` 等）。

### 数据流（典型 Compute 阶段）
1. `T.copy(A, a_ub)` 将片外张量拷入 UB；
2. `T.Parallel` 循环对 `a_ub` 中各元素执行符号运算，结果写回 `b_ub`（或就地写 `a_ub`）；
3. `T.copy(b_ub, B)` 将 UB 写回片外张量。
- 整个流程被包在 `with T.Scope("V"):` 的 Vector Scope 中。

### 复杂表达式 → 多语句分解（原文给出的对照）
- 原文：`c_ub[i,j] = a_ub[i,j] * b_ub[i,j] + a_ub[i,j] / b_ub[i,j]`
- 拆解后：
  - `c_tmp_0[i,j] = a_ub[i,j] * b_ub[i,j]`
  - `c_tmp_1[i,j] = a_ub[i,j] / b_ub[i,j]`
  - `c_ub[i,j]    = c_tmp_0[i,j] + c_tmp_1[i,j]`
- 原文："Currently, temporary buffer will be the same size of tiles. So we strongly recommend to turn automatic buffer reuse on in order to avoid space waste."

### 性能 / 量化数据
- 原文未给出具体性能数字、benchmark、吞吐或时延数据。

---

## 【表格解读】

### 原文表格 1：Binary Operations（二元运算）

| Category | Formula | TileLang Expression |
|---|---|---|
| Addition | `c = a + b` | `a + b` |
| Subtraction | `c = a - b` | `a - b` |
| Multiplication | `c = a * b` | `a * b` |
| Division | `c = a / b` | `a / b` |
| Min | `c = min(a, b)` | `T.min(a, b)` |
| Max | `c = max(a, b)` | `T.max(a, b)` |

**逐行解读**：列出 6 类数值二元运算。前 4 类（加减乘除）使用 Python 内置运算符，`Min`/`Max` 必须通过 `T.min` / `T.max` 命名空间函数调用，避免与 Python 内建名冲突。

### 原文表格 2：Integer Bitwise Operations（整数位运算）

| Category | Formula | TileLang Expression |
|---|---|---|
| AND | `c = a & b` | `a & b` |
| OR | `c = a \| b` | `a \| b` |

**逐行解读**：仅显式列出 AND、OR 两类。注：原文中 OR 行的公式用 `\|` 转义，是 markdown 表格内的合法写法，对应 `c = a | b`。

### 原文表格 3：Floating-Point Unary Operations（浮点一元运算）

| Category | Formula | TileLang Expression |
|---|---|---|
| Abs | `y = \|x\|` | `T.abs(a)` |
| Exp | `y = e^x` | `T.exp(a)` |
| Log | `y = log(x)` | `T.log(a)` |
| Sqrt | `y = sqrt(x)` | `T.sqrt(a)` |
| Rsqrt | `y = 1/sqrt(x)` | `T.rsqrt(a)` |
| ReLU | `y = max(x, 0)` | `T.max(a, 0)` |

**逐行解读**：6 类浮点一元运算。注意 **ReLU 通过 `T.max(a, 0)` 实现**，并未给出独立的 `T.relu` 命名；`Rsqrt` 在硬件层可映射到高速近似倒数平方根指令。

### 原文表格 4：Integer Unary Operations（整数一元运算）

| Category | Formula | TileLang Expression |
|---|---|---|
| Bitwise NOT | `y = ~x` | `~a` |
| Left Shift | `y = x << s` | `a << scalar_val` |
| Right Shift | `y = x >> s` | `a >> scalar_val` |

**逐行解读**：3 类整数位运算一元形式。移位的 `s` 在 TileLang 表达式中以 **标量**（`scalar_val`）形式出现，表明移位量不支持张量，仅支持编译期/运行期常量标量。

---

## 【公式解读】

原文并非以传统数学公式排版，而是用 `Formula` 列以行内伪公式形式给出。逐式还原并解释：

1. **加法**：`c = a + b` —— `c` 为结果张量/缓冲元素，`a`、`b` 为同形状 tile 内元素；对应表达式 `a + b`，向量化加法。
2. **减法**：`c = a - b` —— 元素级减法，语义同上加号变减号。
3. **乘法**：`c = a * b` —— 元素级乘法，可对应 SIMD 乘或 AscendC `T.tile.mul`。
4. **除法**：`c = a / b` —— 元素级除法。
5. **Min**：`c = min(a, b)` —— 元素级取小；表达式 `T.min(a, b)`。
6. **Max**：`c = max(a, b)` —— 元素级取大；表达式 `T.max(a, b)`，同时也是 ReLU（`y = max(x, 0)`）的底层实现。
7. **AND**：`c = a & b` —— 整数按位与；表达式 `a & b`。
8. **OR**：`c = a | b` —— 整数按位或；表达式 `a | b`。
9. **Abs**：`y = |x|` —— 取绝对值，调用 `T.abs(a)`。
10. **Exp**：`y = e^x` —— 自然指数；`T.exp(a)`，可映射到 AscendC 硬件 `exp` 指令。
11. **Log**：`y = log(x)` —— 自然对数；`T.log(a)`。
12. **Sqrt**：`y = sqrt(x)` —— 平方根；`T.sqrt(a)`。
13. **Rsqrt**：`y = 1/sqrt(x)` —— 反平方根；`T.rsqrt(a)`，通常对应高速近似指令。
14. **ReLU**：`y = max(x, 0)` —— `T.max(a, 0)`，通过与 0 取大实现 ReLU。
15. **Bitwise NOT**：`y = ~x` —— 按位取反，表达式 `~a`。
16. **Left Shift**：`y = x << s` —— 左移 `s` 位，`s` 为标量 `scalar_val`；表达式 `a << scalar_val`。
17. **Right Shift**：`y = x >> s` —— 右移 `s` 位，`s` 为标量 `scalar_val`；表达式 `a >> scalar_val`。

---

## 【关联】

- **与 UB 内存分配关联**：`T.Parallel` 操作的对象是已分配到 UB 的 tile 缓冲（如 `T.alloc_ub((block_M // VEC_NUM, block_N), "float16")`），与 `T.alloc_ub` 配套使用。
- **与 `T.copy` 关联**：典型的 `T.copy(src, dst)` 在 `T.Parallel` 循环之前做 Load、之后做 Store，构成完整 tile 级 Load → Compute → Store 流。
- **与 `T.Scope("V")` 关联**：示例代码统一在 Vector Scope 内执行 `T.Parallel`，表明该原语语义定位于 V 核向量计算阶段。
- **与 `ascend_tile.py` 中的 `T.tile.xxx` 关联**：`T.Parallel + T.exp / T.log / T.max` 属于符号 API 路径；`T.tile.add / T.tile.exp` 属于 AscendC 显式向量 intrinsic 路径，二者在文档中被并列为"两种编程范式"（§4.1 与 §4.2）。
- **与 `T.prim_func` / `@T.prim_func` 装饰器关联**：示例以 `@T.prim_func` 装饰的函数作为入口，包装 `Buffer` 输入输出参数。
- **与 automatic buffer reuse 关联**：由于复杂表达式拆解会产生与 tile 同尺寸的临时缓冲，文档建议启用 buffer reuse 以节省 UB 空间（原文未给出具体开关名称/位置）。
- **文末"未来支持场景"**：Vertical slicing、Non-linear index access、Complex nested expressions —— 表明当前 `T.Parallel` 在这些维度尚不支持（与 §3.5 的 "indx needs to be a simple variable or expression" 限制相呼应）。

---

## 【使用方法】

### 基本语法（1D / 2D）
```python
for j in T.Parallel(block_N // VEC_NUM):
    c_ub[j] = a_ub[j] + b_ub[j]

for (i, j) in T.Parallel(block_M // VEC_NUM, block_N):
    c_ub[i, j] = a_ub[i, j] + b_ub[i, j]
```
每次迭代 `(i, j)` 独立执行，代表可并行区域。

### 复杂表达式
```python
for (i, j) in T.Parallel(block_M // VEC_NUM, block_N):
    c_ub[i, j] = a_ub[i, j] * b_ub[i, j] + a_ub[i, j] / b_ub[i, j]
```
会被自动拆解为带临时缓冲的多条语句；**强烈建议开启 automatic buffer reuse**。

### 向量-标量 / 行广播
```python
for j in T.Parallel(block_N):
    c_ub[j] = a_ub[j] + 1

for (i, j) in T.Parallel(block_M // VEC_NUM, block_N):
    c_ub[i, j] = a_ub[i, j] * b_ub[i]   # a_ub.shape=(block_M//VEC_NUM, block_N), b_ub.shape=(block_M//VEC_NUM,)
```

### 行-列混合（部分并行）
```python
for i in range(block_M // VEC_NUM):     # 行：串行
    for j in T.Parallel(block_N):       # 列：并行
        c_ub[i, j] = a_ub[i, j] * b_ub[i, j]
```

### 维度不匹配的右侧广播
```python
for (i, j) in T.Parallel(block_M // VEC_NUM, block_N):
    c_ub[i, j] = b_ub[j] + 5           # b_ub 1D, c_ub 2D；索引须为简单变量/表达式
```

### 端到端示例（§4.1 符号 API 范式）
```python
@T.prim_func
def main(A: T.Buffer((M, N), "float16"), B: T.Buffer((M, N), "float16")):
    with T.Scope("V"):
        a_ub = T.alloc_ub((block_M // VEC_NUM, block_N), "float16")
        b_ub = T.alloc_ub((block_M // VEC_NUM, block_N), "float16")
        T.copy(A, a_ub)
        for (i, j) in T.Parallel(block_M // VEC_NUM, block_N):
            b_ub[i, j] = T.exp(a_ub[i, j])
        T.copy(b_ub, B)
```

### 端到端示例（§4.2 AscendC tile-level intrinsic 范式）
```python
@T.prim_func
def main(A: T.Buffer((M, N), "float16"), B: T.Buffer((M, N), "float16")):
    with T.Scope("V"):
        T.copy(A, a_ub)
        T.tile.exp(b_ub, a_ub)
        T.copy(b_ub, B)
```

### 配置项 / 命令开关
- 文档**未给出** `T.Parallel` 的具名参数、开关或命令行配置项；
- 文档**未给出** "automatic buffer reuse" 的具体启用命令/接口名；
- 文档**未给出** Ascend target 选型、编译命令或运行时调度参数。
- （原文未涉及具体启用方式/配置项，以上信息均严格出自原文。）
