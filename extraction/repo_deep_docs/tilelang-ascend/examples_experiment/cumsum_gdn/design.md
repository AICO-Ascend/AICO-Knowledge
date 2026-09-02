# cumsum_gdn 设计文档

> 仓 `tilelang-ascend` · 路径 `examples_experiment/cumsum_gdn/design.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/tilelang-ascend/examples_experiment/cumsum_gdn/design.md

# cumsum_gdn 设计文档 · 一体化深度解读

## 【定位】

这篇文档解决"如何在 TileLang Ascend 路径上落地一个分块前缀和算子 `chunk_cumsum`"的问题：它同时给定了算子语义（chunk 内正向/反向 cumsum、`use_fragment` 旁路、两种 head 布局）、Ascend 上的 fast path 边界（仅覆盖"对齐子集"）、片上缓冲的具体形态（强制 2D 退化 tile）、同步与 memory planning 策略，以及与主仓语义对齐的验证结论。整体可概括为"**语义完整、fast path 只覆盖对齐子集**"。

---

## 【技术要点】

1. **算子定义**：`chunk_cumsum`（位于 `examples/cumsum_gdn/example_cumsum.py`），将输入序列按 `chunk_size=C` 分块，每 chunk 内独立计算前缀和。
2. **三类开关**：`reverse=False/True`（正向 / 反向）、`use_fragment=True`（保留一条等价中间缓冲路径）、`head_first=True/False`（`(B, H, L)` / `(B, L, H)`）。
3. **fast path 准入条件**（同时满足）：`head_first=True`、`H % 2 == 0`、`L % C == 0`；其余场景（`head_first=False`、odd-H、`L % C != 0` 尾块）一律回退到 PyTorch reference。
4. **核心映射**：`chunk_num = ceildiv(L, C)`、`VEC_NUM = 2`、`h_block_num = H // VEC_NUM`，grid = `B * h_block_num * chunk_num`，每个 kernel block 负责 1 个 batch × 1 个 head 分片 × 1 个 chunk。
5. **编程模式**：Developer 模式 fast path + host wrapper fallback；使用 `T.alloc_shared`、自动同步、自动内存规划，**不显式**写 `T.Scope("V")`、`barrier/set_flag/wait_flag`；也**不要求**必须使用 `T.cumsum` 或 `T.Parallel`，当前 fast path 仍为手写 `for` 循环。
6. **片上缓冲（强制 2D 退化 tile）**：`g_ub=[1,C]`、`s_ub=[1,C]`、`total_ub=[1,1]`、`fragment_ub=[1,C]`；以 `float32` 计 `C=32` 时约 `388B`、`C=64` 时约 `772B`，均远小于 `192KB` UB/shared 预算；2D 化是为规避 Ascend shared-layout inference 对一维 buffer 注入 zN layout 在 lowering 阶段触发的异常。
7. **反向模式实现**：先规约得到 `total_ub[0,0]`，再按 `suffix_i = total - prefix_i + x_i` 完成转换，**不**直接做反向扫描。
8. **`T.cumsum` 真实状态**：已存在公开 API（`tilelang/language/__init__.py`、`tilelang/language/reduce.py`）以及 `src/op/reduce.cc` 中针对 `shared/shared.dyn` 的 lowering；本文档未采用是因为需要显式处理 `reverse`、`use_fragment` 语义，以及当前 Ascend shared layout 推导对临时 buffer 更稳妥的写法仍是显式循环。
9. **pass_configs**：`TL_ASCEND_AUTO_SYNC=True`（编译器插入同步）+ `TL_ASCEND_MEMORY_PLANNING=True`（编译器负责 shared 侧内存规划）；本算子因此不需手写同步原语。

---

## 【关键机制与数据】

- **工作原理（按 chunk 切分）**：每个 kernel block 只看一个 chunk，按 `T.cumsum` 语义在 shared 上做片内前缀和；反向模式以"先求 total，再做 `total - prefix + input` 变换"实现，避免反向访存。
- **数据流（fast path）**：`GM[G] -> shared[g_ub]` → `shared[g_ub] -> shared[s_ub]/shared[fragment_ub]`（`for` 循环 cumsum）→ `shared[s_ub] -> GM[S]`；反向模式额外先规约出 `total_ub[0, 0]`。
- **Grid 与并行度**：grid = `B * (H // 2) * ceildiv(L, C)`；沿 head 维只取 `H // 2`，这是 fast path 强制 `H % 2 == 0` 的直接体现。
- **占用与预算**（原文，`float32`）：`C=32` 约 `388B`、`C=64` 约 `772B`，远小于 `192KB` UB/shared 预算——这是"为何可以把整 chunk 一次性留在片上"的容量证据。
- **fallback 与 fast path 的边界**：原文明确"这不是功能缺失，而是优先保证当前 Ascend 路径的稳定性与 correctness"——`head_first=False`、odd-H、尾块三类均交回 PyTorch reference。
- **关于 `use_fragment`**：原文称其与主路径"行为等价"，仅作为一条额外中间缓冲路径保留，便于将来对齐主仓语义时切换。
- **性能数字**：原文未给出实测 FLOPS、吞吐或时延数据，仅给出容量预算与 grid 规模。

---

## 【表格解读】

原文 4.2 节"片上缓冲"表格逐字还原：

| Buffer | Shape | 作用 |
|---|---:|---|
| `g_ub` | `[1, C]` | 当前 chunk 输入 |
| `s_ub` | `[1, C]` | 当前 chunk 输出 |
| `total_ub` | `[1, 1]` | reverse 模式总和 |
| `fragment_ub` | `[1, C]` | `use_fragment=True` 中间缓冲 |

逐行解读：

- **`g_ub [1, C]`**：装载本 chunk 输入 `x_0..x_{C-1}`，是后续 `for` 循环 cumsum 的唯一源；写成 `[1, C]` 而非 `[C]`，是为契合 Ascend shared-layout inference 要求的二维 `(i, j)` 形式以规避 lowering 异常。
- **`s_ub [1, C]`**：存放本 chunk 输出 `y_0..y_{C-1}`，计算完成后由 `shared -> GM` 写出；与 `g_ub` 同形，保证输入/输出形状一致，便于回写。
- **`total_ub [1, 1]`**：仅 reverse 模式使用，承载本 chunk 的 `sum(x_j)`，用于 `suffix_i = total - prefix_i + x_i` 变换；规模 `[1,1]` 体现"这是一个标量 reduce 结果"。
- **`fragment_ub [1, C]`**：`use_fragment=True` 路径的中间缓冲，原文称其与主路径行为等价，因此是预留的等价旁路。
- **总体观察**：四个 buffer 的形状都属于二维退化 tile（一维逻辑），这种形态不是出于算子语义需要，而是出于实现稳定性需要（规避 zN layout 注入），原文明确"这只是实现层面的稳定性处理，不改变算子语义"。

---

## 【公式解读】

**正向（前缀和）**：

$$
y_i = \sum_{j=0}^{i} x_j
$$

- 符号：`y_i` 为 chunk 内第 `i` 个位置的输出；`x_j` 为同 chunk 内第 `j` 个位置的输入；求和下标 `j` 从 `0` 跑到 `i`（含端点）。这是标准的 inclusive prefix sum。

**反向（后缀和）**：

$$
y_i = \sum_{j=i}^{C-1} x_j
$$

- 符号：`C` 为本 chunk 长度；求和下标 `j` 从 `i` 跑到 `C-1`；`y_i` 表示"从 `i` 到 chunk 末尾"的后缀累加。

**实现上的等价变换**（**反向不直接反向扫描，而是先算 total 再变换**）：

$$
\text{suffix}_i = \text{total} - \text{prefix}_i + x_i
$$

- 符号：
  - `prefix_i = sum_{j=0}^{i} x_j`：正向前缀和（已经能在正向循环中算出）；
  - `total = sum_{j=0}^{C-1} x_j`：整个 chunk 的总和（反向模式需额外先规约得到 `total_ub[0, 0]`）；
  - `suffix_i`：等价于反向模式定义的 `y_i`。
- 推导思路：`sum_{j=i}^{C-1} x_j = total - sum_{j=0}^{i-1} x_j = total - (prefix_i - x_i) = total - prefix_i + x_i`。这条恒等式把后缀和"折叠"成对前缀和与 total 的代数运算，因此反向模式可以**复用同一条正向 `for` 循环**，只需在循环末尾补上 `total - prefix_i + x_i`，从而避免反向访存与反向同步。

---

## 【关联】

- **代码位置**：本算子入口在 `examples/cumsum_gdn/example_cumsum.py`（文档 1.1 节明确给出）。
- **主仓 API 与 lowering**：`tilelang/language/__init__.py`、`tilelang/language/reduce.py` 提供公开的 `T.cumsum`；`src/op/reduce.cc` 已具备针对 `shared/shared.dyn` 的 lowering——本文档把它们列为"已存在但本算子暂未直接采用"的上游依赖。
- **TileLang 原语**：文中显式提及但**不强制**使用的原语包括 `T.cumsum`、`T.Parallel`、`T.Scope("V")`、`barrier/set_flag/wait_flag`；**实际使用**的原语是 `T.alloc_shared`，以及 `for` 循环手写 cumsum。
- **Pass 配置（编译期）**：`tilelang.PassConfigKey.TL_ASCEND_AUTO_SYNC`、`tilelang.PassConfigKey.TL_ASCEND_MEMORY_PLANNING`；二者均置 `True`，由编译器自动插同步与自动做 shared 侧内存规划，因此本算子**不出现**显式同步原语。
- **硬件预算锚点**：原文以 `A2/A3 / 910B` 的 `192KB` UB/shared 预算作为容量对照，说明 4 个 buffer 全部驻留片上的可行性；这暗示本设计与 Ascend A2/A3 系列（910B）共享内存规模直接耦合。
- **语义对齐对象**：主仓 `example` 中的 `reverse`、`use_fragment`、`head_first=False`、odd-H、尾块五个语义点；其中前三者由 kernel 内显式支持，后两者由 wrapper 级 fallback 保证语义一致。
- **文末内部链接**：原文标注"(无)"，故未提供额外跳转锚；以上关联均来自文档正文中的显式引用。

---

## 【使用方法】

启用本算子 fast path 的方式（原文第 5 节）：

```python
pass_configs = {
    tilelang.PassConfigKey.TL_ASCEND_AUTO_SYNC: True,
    tilelang.PassConfigKey.TL_ASCEND_MEMORY_PLANNING: True,
}
```

- `TL_ASCEND_AUTO_SYNC=True`：由编译器插入同步，等价于"开发者不再写 `barrier/set_flag/wait_flag`"。
- `TL_ASCEND_MEMORY_PLANNING=True`：由编译器负责 shared 侧内存规划，因此开发者也无需手写 `T.Scope("V")` 这类作用域声明。
- 在满足 `head_first=True && H % 2 == 0 && L % C == 0` 时进入 Ascend fast path；其余场景（`head_first=False`、odd-H、`L % C != 0`）由 host wrapper 自动回退到 PyTorch reference。

**自测覆盖（原文第 7 节）**：正向 / 反向、`use_fragment=True/False`、`head_first=True/False`、odd-H、非整除尾块均已覆盖；验证结论为"对齐场景走 Developer-mode fast path，非对齐场景走 PyTorch reference fallback，两条路径在 example 自测中与 reference 对齐"。

**当前未启用项（原文第 8 节显式列出的边界）**：
1. 并非"所有场景都由 Ascend kernel 直接处理"——非对齐场景走 PyTorch reference；
2. 当前形态是"Developer fast path + wrapper fallback"，而非纯 Ascend kernel；
3. `T.cumsum` 已具备公开 API 与 shared 路径 lowering，但本算子暂未直接采用，仍以手写 `for` 循环承载语义。

**调用入口**：运行 `examples/cumsum_gdn/example_cumsum.py`（原文未提供 CLI 命令或环境变量）。
