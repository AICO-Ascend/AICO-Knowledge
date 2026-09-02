# Fused Sigmoid Gating Delta Rule SSM Scan — 设计文档

> 仓 `tilelang-ascend` · 路径 `examples/fused_sigmoid_gating_delta_rule/design.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/tilelang-ascend/examples/fused_sigmoid_gating_delta_rule/design.md

# Fused Sigmoid Gating Delta Rule SSM Scan — 设计文档深度解读

---

## 【定位】

本文档描述一个面向昇腾 NPU 的**融合算子**：将 Mamba 风格线性注意力中的 sigmoid 门控（含 softplus + σ）与 delta-rule 状态更新融合到单个 kernel 中，对变长多序列执行 SSM（State Space Model）扫描计算，并通过 24 核 Vector 并行 + ping-pong 预取提升吞吐。

---

## 【技术要点】

1. **编程模式与硬件目标**：Expert 模式（`T.copy` 显式内存分配 + 手动同步 + `T.tile.xxx` tile 原语）；目标硬件为**昇腾 NPU 的 24 核 Vector**。
2. **融合策略**：在一个 kernel 内同时计算 `softplus(x; β_s)`、`α = exp(-e^{A_log} · softplus)`、`g = σ(b)`、L2 Norm、Q 缩放、状态衰减、delta rule 更新与输出，避免中间结果回写 GM。
3. **变长序列与多核并行**：用 `cu_seqlens: (S+1,)`（int32）描述序列边界，`ssm_state_indices: (S,)`（int32，`-1` 表示空）映射到 `(C, H_v, d_v, d_k)` 缓存池；任务粒度为 `(seq_idx, v_head_idx, v_tile_idx)` 三元组。
4. **分块参数**：`block_v` 沿 $d_v$ 分块，必须是 32 的倍数且整除 $d_v$；vector unit 子分块 `vec_block_v = block_v / VEC_NUM = block_v / 2`；$d_k$ 整维放入 UB（约束 $d_k \le 128$）；分块数 $\text{num\_v\_tiles} = \lceil d_v / B_v \rceil$。
5. **24 核任务划分**：总任务数 `block_num = S · H_v · num_v_tiles`，前 `(block_num mod 24)` 个核分得 `⌊block_num/24⌋ + 1`，其余核分得 `⌊block_num/24⌋`，按 `flat_idx → (seq, v_head, v_tile)` 映射。
6. **Ping-pong UB 预取**：Q、K、V 在 UB 中各有两块 `[2, …]` 缓冲交替使用；状态矩阵 `H` 在 UB 中为 fp32 `h_vec`，加载/回存走 fp16 `h_load_vec` / `h_store_vec`；同步通过 `mte2→v` 与 `v→mte3` flag 完成。

---

## 【关键机制与数据】

### 核心数据流（原文图示）

```
GM → T.copy → UB (ping-pong: Q[2,dk], K[2,dk], V[2,vec_block_v])
   → T.copy → UB (fp32 workspace: q_f, k_f, v_f;  H[vec_block_v, dk])
   → tile compute → UB (fp32 result: out ping-pong [2, vec_block_v])
   → T.copy → GM (out)
```

### 每 token 时间步执行链（原文公式）
依次为：**可选 L2 Norm**（`q_t / √(||q_t||² + ε)`、`k_t` 同理）→ **Scale**（乘 `1/√d_k`）→ **State Decay**（`H ← H·α`）→ **Prediction**（`pred = H·k̂ ∈ ℝ^{B_v}`）→ **Delta Rule**（`δ = (v_t − pred) ⊙ g`）→ **State Update**（`H[i,j] += k̂[j]·δ[i]`，即 `H←H + k̂⊗δ`）→ **Output**（`o_t = H·q̂ ∈ ℝ^{B_v}`）。时间步严格串行（依赖未解除）。

### 性能/精度数据（原文约束）
- 精度验证：`rtol=2e-2, atol=2e-2`，对比对象为 **PyTorch 参考实现**。
- dtype：**仅支持 float16**（原文标注为 Ascend C 编译器限制）。
- Token 总数必须 padding 至 **64 的整数倍**。
- 显存预算：`init_state = (C, H_v, d_v, d_k)` fp16、`final_state = (S, H_v, d_v, d_k)` fp16，内部均转置为 `(..., d_k, d_v)` 形态参与矩阵乘。

### 工作分配（原文公式）
- `block_num = S · H_v · ⌈d_v / B_v⌉`
- 前 `block_num mod 24` 个核分到 `⌊block_num/24⌋ + 1`，其余分到 `⌊block_num/24⌋`。

---

## 【表格解读】

### 表 1 — 记号约定（原文逐字还原）

| 符号 | 含义 | 维度 |
|------|------|------|
| $T$ | 序列总 token 数 | — |
| $H_k$ | Query/Key head 数 (`nk`) | — |
| $H_v$ | Value head 数 (`nv`) | — |
| $d_k$ | Q/K 维度 (`dk`) | — |
| $d_v$ | V 维度 (`dv`) | — |
| $S$ | 序列数 (`num_seqs`) | — |
| $B_v$ | V 维度分块大小 (`block_v`) | — |
| $\beta_s$ | softplus 参数 (`softplus_beta`) | — |
| $\epsilon$ | L2 归一化 $\varepsilon$ | — |
| $\text{scale}$ | Q 缩放因子 $= 1/\sqrt{d_k}$ | — |

逐行解读：$T$ 是用于确定 `T_pad` 的总 token 上界；$H_k$、$H_v$、$d_k$、$d_v$ 是 GQA（Grouped Query Attention）风格的多 head 维度；$S$ 决定 cu_seqlens 与 ssm_state_indices 长度；$B_v$ 是 tiling 的核心切片单位，与 $d_v$ 一同决定分块数；$\beta_s$ 控制 softplus 的"软度"（阈值 $\beta_s·x > 20$ 时退化为恒等）；$\epsilon$ 是 L2 Norm 的防零分母；`scale` 是 Q 的缩放常数。文档另约束 **$H_v$ 必须是 $H_k$ 的整数倍，`v_per_k = H_v / H_k$**。

### 表 2 — 输入张量（原文逐字还原）

| 参数 | Shape | dtype | 说明 |
|------|-------|-------|------|
| `A_log` | $(H_v,)$ | fp16 | 每个 v_head 的 $\log(A)$ 参数 |
| `a` | $(T_{\text{pad}}, H_v)$ | fp16 | 输入门控参数 $a$ |
| `dt_bias` | $(H_v,)$ | fp16 | 每个 head 的 $\Delta t$ bias |
| `query` | $(T_{\text{pad}}, H_k, d_k)$ | fp16 | Query 张量 |
| `key` | $(T_{\text{pad}}, H_k, d_k)$ | fp16 | Key 张量 |
| `value` | $(T_{\text{pad}}, H_v, d_v)$ | fp16 | Value 张量 |
| `beta` | $(T_{\text{pad}}, H_v)$ | fp16 | Sigmoid 输入 $b$ |
| `init_state` | $(C, H_v, d_v, d_k)$ | fp16 | 缓存的状态池，内部运算转置为 $(C,H_v,d_k,d_v)$ |
| `ssm_state_indices` | $(S,)$ | int32 | 每条序列在状态缓存中的索引，$-1$ 表示空 |
| `cu_seqlens` | $(S+1,)$ | int32 | 累积序列长度，`cu_seqlens[i+1] - cu_seqlens[i]` 为序列长度 |

逐行解读：`A_log`、`dt_bias` 是 per-head 标量；`a`、`beta` 是 per-token × per-v_head 的门控输入；`query`/`key` 是 per-token × per-k_head，`value` 是 per-v_head；`init_state` 用一个容量为 `C` 的池化张量承载多条序列的状态（通过 `ssm_state_indices` 寻址，$-1$ 表示空槽），进算子时已在物理布局上转置为 $(C,H_v,d_k,d_v)$；`cu_seqlens` 是变长序列前缀和；$T_{\text{pad}}$ 是 64 倍对齐后的 token 数。

### 表 3 — 输出张量（原文逐字还原）

| 参数 | Shape | dtype | 说明 |
|------|-------|-------|------|
| `out` | $(T_{\text{pad}}, H_v, d_v)$ | fp16 | 每 token 输出（含 padding） |
| `final_state` | $(S, H_v, d_v, d_k)$ | fp16 | 每条序列最终状态（内部转置为 $d_k \times d_v$） |

逐行解读：每 token 输出直接落在 `T_pad` 维度上（含 padding）；`final_state` 的形状与 `init_state` 物理转置一致（外部写回时再次转回 $(..., d_v, d_k)$）。

### 表 4 — UB 分配明细（原文逐字还原）

| Buffer | Shape | dtype | 用途 |
|--------|-------|-------|------|
| `q_buf`, `k_buf` | $(2, d_k)$ | fp16 | Q/K ping-pong 预取 |
| `v_buf` | $(2, B_v/2)$ | fp16 | V ping-pong 预取 |
| `q_f`, `k_f` | $(d_k,)$ | fp32 | 当前 token Q/K |
| `v_f` | $(B_v/2,)$ | fp32 | 当前 token V |
| `h_vec` | $(B_v/2, d_k)$ | fp32 | 状态矩阵 $H$ |
| `h_load_vec` | $(B_v/2, d_k)$ | fp16 | 从 GM 加载 $H_0$ |
| `h_store_vec` | $(B_v/2, d_k)$ | fp16 | 回存 $H_T$ 到 GM |
| `pred_vec` | $(B_v/2,)$ | fp32 | $\text{pred} = H \hat{k}$ |
| `delta_vec` | $(B_v/2,)$ | fp32 | $\delta$ |
| `o_half_buf` | $(2, B_v/2)$ | fp16 | 输出 ping-pong |
| `k_broadcasted` | $(B_v/2, d_k)$ | fp32 | $\hat{k}$ 广播 |
| `compute_buffer` | $(B_v/2, d_k)$ | fp32 | 中间 workspace |

逐行解读：前 5 行负责数据加载/预取与状态矩阵驻留；`q_f`/`k_f`/`v_f` 是 fp32 提升后的当前 token；`h_vec` 是驻留在 UB 的核心状态矩阵；`h_load_vec`/`h_store_vec` 是 fp16 影子缓冲避免直接对 fp32 做 GM 拷入拷出；`pred_vec`/`delta_vec` 是预测与 delta 中间量；`o_half_buf` 是双缓冲输出；`k_broadcasted` 与 `compute_buffer` 提供 $\hat{k}$ 广播与中间矩阵运算的 workspace。

### 表 5 — 同步策略（原文逐字还原）

| 同步点 | Flag 类型 | 方向 | 用途 |
|--------|-----------|------|------|
| 加载 init_state | `mte2→v` | MTE2→Vector | 等待 $H_0$ 到达 UB |
| 加载 A_log | `mte2→v` | MTE2→Vector | 等待 $A_{\log}$ 到达 |
| 写回 out 后 | `v→mte3` | Vector→MTE3 | out 写回完成确认 |
| QKV 预取 | `mte2→v` | MTE2→Vector | 等待下一 token Q/K/V 到达 |

逐行解读：算子需要 4 类显式同步。`mte2→v` 用于"等数据从 GM 拷到 UB 后才能算"；`v→mte3` 用于"等 vector 算完并发出写回请求后再继续"，整体覆盖了状态初值、常数、预取与结果回写四个流水阶段。

---

## 【公式解读】

### 软门控参数（原文逐字保留）

$$
\text{softplus}(x;\; \beta_s) =
\begin{cases}
x & \text{if } \beta_s \cdot x > 20 \\
\displaystyle \frac{\log(1 + e^{\beta_s x})}{\beta_s} & \text{otherwise}
\end{cases}
$$

$$
x_t = a_{t,h} + \text{dt\_bias}_{h}
$$

$$
\alpha_{t,h} = \exp\!\big(-e^{A_{\text{log},h}} \cdot \text{softplus}(x_t; \beta_s)\big) \quad\in (0,1)
$$

$$
g_{t,h} = \sigma(b_{t,h}) = \frac{1}{1 + e^{-b_{t,h}}}
$$

符号解读：`softplus` 在 $\beta_s·x > 20$ 时数值饱和、退化为 $x$（数值稳定的常见工程截断）；$x_t$ 是把 per-token 输入 $a$ 与 per-head 偏置相加得到有效门控量；$\alpha_{t,h}$ 用 $A_{\text{log},h}$ 指数化后再求负指数，得到 $(0,1)$ 区间内的状态衰减因子；$g_{t,h}$ 是标准 sigmoid 门。

### 每时间步状态更新（原文逐字保留）

$$
\begin{aligned}
\text{(可选 L2 Norm)} \quad &\hat{q}_t = \frac{q_t}{\sqrt{\|q_t\|^2 + \epsilon}}, \quad
\hat{k}_t = \frac{k_t}{\sqrt{\|k_t\|^2 + \epsilon}} \\[4pt]
\text{(Scale)} \quad &\hat{q}_t \leftarrow \hat{q}_t \cdot \text{scale} \\[4pt]
\text{(State Decay)} \quad &H \leftarrow H \cdot \alpha_{t,h} \\[4pt]
\text{(Prediction)} \quad &\text{pred} = H \cdot \hat{k}_t \quad\in \mathbb{R}^{B_v} \\[4pt]
\text{(Delta Rule)} \quad &\delta = (v_t - \text{pred}) \odot g_{t,h} \quad\in \mathbb{R}^{B_v} \\[4pt]
\text{(State Update)} \quad &H \leftarrow H + \hat{k}_t \otimes \delta \qquad\big(H[i,j] \mathrel{+}= \hat{k}_t[j] \cdot \delta[i]\big) \\[4pt]
\text{(Output)} \quad &o_t = H \cdot \hat{q}_t \quad\in \mathbb{R}^{B_v}
\end{aligned}
$$

符号解读：$q_t,k_t,v_t$ 均为单个 token 的向量；$\|\cdot\|$ 为 L2 范数，$\epsilon$ 防零；`scale = 1/√d_k`；状态 $H\in\mathbb{R}^{B_v\times d_k}$ **按行存储**，每行是 V 维度的一段；$\odot$ 是逐元素乘；$\otimes$ 是外积，且用索引式 $H[i,j] \mathrel{+}= \hat{k}_t[j]\cdot\delta[i]$ 明确"行号索引 V 维度、列号索引 K 维度"的存储映射；最后 $o_t$ 再由 $H$ 与 $\hat{q}_t$ 做矩阵-向量乘得到。

### 分块与任务划分（原文逐字保留）

$$
\text{num\_v\_tiles} = \big\lceil d_v / B_v \big\rceil, \quad
\text{vec\_block\_v} = B_v / 2
$$

$$
\text{max\_work\_per\_block} = \begin{cases}
\lfloor \text{block\_num} / 24 \rfloor + 1 & \text{前 } (\text{block\_num} \bmod 24) \text{ 个核} \\
\lfloor \text{block\_num} / 24 \rfloor & \text{剩余核}
\end{cases}
$$

符号解读：$B_v$ 即 `block_v`，$\text{vec\_block\_v}$ 是 vector unit 子块（除以 `VEC_NUM=2`）；$\text{block\_num}$ 是 24 核要瓜分的总任务数；负载均衡公式把余数 `block_num mod 24` 个核多分 1 个子任务，其余核分摊基础量。

---

## 【关联】

原文为单文件 design，未提供文末内部链接（用户标注 **"内部链接: (无)"**）。从内容推断的隐含关联：

- 与上游 Mamba/GQA 注意力变体（如 mamba.py / fla 库中的 `fused_sigmoid_gating_delta_rule` 参考实现）共享同一数学语义，文档明确以 **PyTorch 参考实现** 做数值对齐（`rtol=atol=2e-2`）。
- 与底层 TileLang/Ascend C 编程模型的 tile/sync 原语（`T.tile.xxx`、`T.copy`、MTE2/Vector/MTE3 flag）耦合；24 核 Vector 的任务划分模型与硬件 AICore/AIV 拓扑相关。
- 与同仓其他 examples（属于 Expert 模式的 tile 编程范式）共享同一编程骨架，但本文未点名。

---

## 【使用方法】

原文未涉及调用入口、Python API、CLI 命令或配置文件。**可直接用于启用的配置/约束信息**（原文明确给出的部分）：

- dtype：**仅支持 `float16`**（Ascend C 编译器限制）。
- `block_v`：必须为 **32 的整数倍**，且整除 $d_v$，并满足 `block_v % VEC_NUM == 0`（`VEC_NUM=2`）。
- $H_v$：**必须是 $H_k$ 的整数倍**（支持 Grouped Query）。
- $d_k$：$\le 128$（整维驻留 UB）。
- 序列：`cu_seqlens` 长度 `S+1`，`ssm_state_indices` 中 `-1` 表示空槽；Token 总数需 **padding 至 64 的整数倍**。
- 验证：与 PyTorch 参考实现对齐，**`rtol=2e-2, atol=2e-2`**。

如需具体启动命令或 Python wrapper，请参考仓库其他文件（原文未提供）。
