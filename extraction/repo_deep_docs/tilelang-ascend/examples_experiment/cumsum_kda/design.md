# cumsum_kda 设计文档

> 仓 `tilelang-ascend` · 路径 `examples_experiment/cumsum_kda/design.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/tilelang-ascend/examples_experiment/cumsum_kda/design.md

# cumsum_kda 设计文档 一体化解读

---

## 【定位】

本文档描述了 `tilelang-ascend` 中 `cumsum_kda` example 的设计与实现——将主仓 KDA/FLA 的 cumsum 示例迁移到 Ascend 后端，覆盖 **local cumsum**（chunk 内独立前缀和）与 **global cumsum**（跨 chunk 累加、显式维护 `carry`）两类语义，提供 scalar/vector 两套 kernel 并通过 host wrapper 处理 fast path 之外的边界场景。

---

## 【技术要点】

1. **四类 kernel**：`chunk_local_cumsum_scalar` / `chunk_global_cumsum_scalar` / `chunk_local_cumsum_vector` / `chunk_global_cumsum_vector`，分别覆盖 local/global × scalar/vector 四种组合。
2. **两种编程模式**：当前采用 **Developer 模式 fast path**（手写 `for` 循环）+ **host wrapper fallback / slicing**；fast path 并不直接调用 `T.cumsum`，而是用显式循环维护 carry 与 prefix sum。
3. **fast path 触发条件**：scalar fast path 需要 `head_first=True && H % 2 == 0 && SEQ_LEN % BT == 0`；vector fast path 额外要求 `S_DIM % BS == 0`。其余场景（`head_first=False`、odd-H、T 尾块、S 尾块、varlen）由 wrapper 兜底。
4. **Developer 模式特征**（按原文列举）：使用 `T.alloc_shared`、开启自动同步、开启自动内存规划、不显式写 `T.Scope("V")`、不手写同步原语。
5. **Ascend 二维退化 tile 约束**：因为 Ascend shared layout 推导会注入默认 zN layout（按二维 `(i, j)` 构造），所以逻辑一维的 shared buffer 被显式写成 `[1, BT]`、`[1, 1]`、`[1, BS]` 这种二维退化形态。原文明确说明："这属于当前 Ascend lowering 稳定性约束，不改变算子语义。"
6. **pass_configs**：`TL_ASCEND_AUTO_SYNC: True` 与 `TL_ASCEND_MEMORY_PLANNING: True`，由编译器处理同步与 shared 内存规划。

---

## 【关键机制与数据】

### local 路径（原文 §5.1）

```
GM[s] -> shared[b_s]
shared[b_s] -> shared[b_o]     (for-loop prefix sum)
shared[b_o] -> GM[o]
```

若 `reverse=True`，先累加出 chunk 总和再做：

```
suffix = total - prefix + input
```

### global 路径（原文 §5.2）

```
for each chunk:
    GM[s] -> shared[b_s]
    shared[b_s] -> shared[b_o]         (chunk local prefix)
    shared[b_o] += carry
    write back
    carry += chunk_sum
```

原文强调 global 路径的 `carry` 维护逻辑是当前版本不直接用 `T.cumsum` 替代的最主要原因（global 需要显式 carry + 不同控制流 + wrapper 兼顾 fallback/varlen/dispatcher）。

### Block → 工作单元映射（原文 §4）

- local scalar: `grid: chunk_num * B * (H // 2)`，每个 block 处理一个 batch-head 的一个 chunk
- local vector: `grid: s_block_num * chunk_num * B * (H // 2)`
- global scalar/vector：block 负责一个 batch-head 的所有 chunk（通过 `carry[0, 0]` 跨 chunk 累加）

### Vector BS 计算（原文 §4.3）

```
BS = min(32, 2 ** floor(log2(S_DIM)))
```

### 片上内存预算（原文 §6，A2/A3 / 910B，按 192KB 评估）

- scalar（BT=64）：`b_s` 256B + `b_o` 256B + `carry/total` 4B + `b_ss_buf` 4B ≈ 520B
- vector（BT=64, BS=32）：`b_s` 8KB + `b_o` 8KB + `carry/total` 128B + `b_ss_buf` 128B ≈ 16.5KB

两者均 "远小于 192KB"（原文）。

### 公开入口与 lowering 路径（原文 §3.1）

- 公开入口：`tilelang/language/__init__.py` 与 `tilelang/language/reduce.py`
- `src/op/reduce.cc` 中已存在 `shared/shared.dyn` 的 lowering
- 原文结论：`T.cumsum` **不是未导出状态**，本 example 不直接使用是设计选择，不是能力缺失。

---

## 【表格解读】

### 表 1：local scalar 缓冲（原文 §4.1）

| Buffer | Shape |
|---|---:|
| `b_s` | `[1, BT]` |
| `b_o` | `[1, BT]` |
| `total_buf` | `[1, 1]` |

**解读**：local scalar 路径无跨 chunk carry，只需 `b_s`/`b_o` 两个 chunk 级共享缓冲（写入 GM 来的输入、在 shared 上做完 prefix sum 后写回），再加一个标量 `total_buf` 用于 `reverse=True` 时先累加 chunk 总和。shape 写成 `[1, BT]` 是原文 §3.2 解释的 Ascend lowering 二维退化约束。

### 表 2：global scalar 缓冲（原文 §4.2）

| Buffer | Shape |
|---|---:|
| `b_s` | `[1, BT]` |
| `b_o` | `[1, BT]` |
| `carry` | `[1, 1]` |
| `b_ss_buf` | `[1, 1]` |

**解读**：相对 local scalar 多出 `carry[0, 0]` 维护跨 chunk 累加值，以及 `b_ss_buf[0, 0]`。原文未给出 `b_ss_buf` 的具体语义用途（结合 §5.2 中"chunk_sum"逻辑推断，应为存放当前 chunk 总和的临时缓冲）。

### 表 3：local vector 缓冲（原文 §4.3）

| Buffer | Shape |
|---|---:|
| `b_s` | `[BT, BS]` |
| `b_o` | `[BT, BS]` |
| `total_buf` | `[1, BS]` |

**解读**：vector 路径按 `(T, S)` 二维处理 tile，每个 chunk 在 S 维被切成 `s_block_num = S_DIM / BS` 个块；shape 直接写成 `[BT, BS]`（无需二维退化）。`total_buf[1, BS]` 与 scalar 的 `total_buf` 同源，用于 reverse 时先算 chunk 总和。

### 表 4：global vector 缓冲（原文 §4.4）

| Buffer | Shape |
|---|---:|
| `b_s` | `[BT, BS]` |
| `b_o` | `[BT, BS]` |
| `carry` | `[1, BS]` |
| `b_ss_buf` | `[1, BS]` |

**解读**：在 local vector 上叠加跨 chunk carry，carry 沿 S 维独立维护（每个 S 列一条独立的前缀和链）。`b_ss_buf[1, BS]` 同 scalar 情形，原文未细化其内部语义。

---

## 【公式解读】

**原文无显式数学公式**。文档中仅以伪代码形式给出数据流（见 §5.1 / §5.2 "关键机制与数据"）以及一行 reverse 计算式：

```
suffix = total - prefix + input
```

符号含义：
- `total`：chunk 内所有元素的累加和（local 路径先在 for-loop 中累加得到）
- `prefix`：chunk 内正向前缀和
- `input`：原始 chunk 输入
- `suffix`：reverse=True 时输出的反向前缀和

文档未给出更形式化的递推式或闭式表达。

---

## 【关联】

文档内部的关系梳理（基于原文上下文）：

- **与 GDN example 的关系**：原文 §3.1 第一句 "和 GDN 一样，`T.cumsum` 当前**不是未导出状态**"——即本 example 与 GDN 共用同一套 `T.cumsum` 公开入口与 `src/op/reduce.cc` 的 lowering，但本 example 因 global carry + 控制流差异选择不直接调用它。
- **与主仓 KDA/FLA 的关系**：§1.1 注明 "该 example 迁移自主仓 KDA/FLA cumsum 示例"，§8 给出与主仓语义的逐项对齐方式（dense 对齐子集走 Ascend kernel fast path，其余由 wrapper/reference 保底）。
- **wrapper 层支持的特性**（§1.2 + §8）：`scale`（wrapper 后处理）、`cu_seqlens`（varlen，按序列切片复用 dense 路径）、canonical `chunk_indices`（仅接受 canonical 形式）、统一 dispatcher。
- **`T.cumsum` 与本 example 的关系**：已导出 + 已存在 `shared/shared.dyn` lowering，但本 example 显式选择手写 `for` 循环（原文 §3.1 列出三条理由 + §10 第 4 条再次确认）。

文末未提供任何 markdown 内部链接。

---

## 【使用方法】

### 启用 fast path 的隐含条件（原文 §2.2）

scalar fast path 需同时满足：
- `head_first=True`
- `H % 2 == 0`
- `SEQ_LEN % BT == 0`

vector fast path 额外要求：
- `S_DIM % BS == 0`

### pass_configs（原文 §7）

```python
pass_configs = {
    tilelang.PassConfigKey.TL_ASCEND_AUTO_SYNC: True,
    tilelang.PassConfigKey.TL_ASCEND_MEMORY_PLANNING: True,
}
```

- `AUTO_SYNC`：由编译器处理同步（Developer 模式下不手写同步原语）
- `MEMORY_PLANNING`：由编译器处理 shared 侧内存规划

### Wrapper 兜底场景（原文 §2.2 / §8）

以下情况通过 wrapper 保证语义一致：
- `head_first=False`
- odd-H
- T 尾块（SEQ_LEN 不被 BT 整除）
- S 尾块（S_DIM 不被 BS 整除）
- varlen（`cu_seqlens` 按序列切片复用 dense 路径）

### 入口脚本（原文 §1.1）

`examples/cumsum_kda/example_cumsum_kda.py`，提供 `chunk_local_cumsum_*` 与 `chunk_global_cumsum_*` 四类 kernel，对外通过统一 dispatcher 与 wrapper 暴露 `scale` / `cu_seqlens` / canonical `chunk_indices` 等语义。

> 注：原文未涉及具体命令行 / 环境变量 / 安装步骤。
