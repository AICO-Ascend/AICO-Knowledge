# HC: Manifold-Constrained Hyper-Connections — 技术点深读（DEEP 2026-08-18）

> 全要素深读笔记。独立文件，extract_phase1 重跑不丢。
> 论文：mHC: Manifold-Constrained Hyper-Connections · arXiv:2512.24880v2 (5 Jan 2026)
> 作者：Zhenda Xie*, Yixuan Wei*, Huanqi Cao* 等，DeepSeek-AI
> 注：本仓库 slug 为 `hc-manifold-constrained-hyper-connections`；MOC 中亦以 `mhc-manifold-constrained-hyper-connections` 引用同一论文。本文是 [[hyper-connections]] 的直接后继与改进变体。

## 核心问题

Hyper-Connections（HC, Zhu et al. 2024）通过把 residual stream 宽度从 `C` 扩展到 `nC`（expansion rate `n`）并引入三个可学习线性映射 `Hres_l ∈ R^{n×n}`、`Hpre_l, Hpost_l ∈ R^{1×n}`，在不增加单层 FLOPs 的前提下显著提升拓扑复杂度与性能（§1, Eq.3）。要理解 mHC 修复的靶点，须先回看 ResNet 的"信号守恒"基底。ResNet (He et al. 2016a) 单层结构由 Eq.1 给出：

$$
\mathbf{x}_{l+1} = \mathbf{x}_l + \mathcal{F}(\mathbf{x}_l, \mathcal{W}_l),
$$

其中 `x_l, x_{l+1}` 是第 `l` 层的 `C` 维输入/输出，`F` 为残差函数。将 residual connection 跨层递归展开（Eq.2）：

$$
\mathbf{x}_L = \mathbf{x}_l + \sum_{i=l}^{L-1} \mathcal{F}(\mathbf{x}_i, \mathcal{W}_i),
$$

其中 `L` 为更深、`l` 为更浅层。所谓 identity mapping 性质即 `x_l` 这一项——浅层信号不经修改直达深层，正是 ResNet 十年来支撑大规模训练稳定性的根基（§1）。HC 把这条基底改写为 Eq.3：

$$
\mathbf{x}_{l+1} = \mathcal{H}_{l}^{\mathrm{res}}\mathbf{x}_l + \mathcal{H}_{l}^{\mathrm{post}\, \top}\mathcal{F}(\mathcal{H}_{l}^{\mathrm{pre}}\mathbf{x}_l, \mathcal{W}_l),
$$

其中 `x_l, x_{l+1}` 特征维度由 `C` 扩展为 `n×C`，`Hres_l ∈ R^{n×n}` 控制流内混合、`Hpre_l ∈ R^{1×n}` 把 `nC` 流聚合为 `C` 维层输入、`Hpost_l ∈ R^{1×n}` 把层输出映射回流（§3）。但作者指出 HC 在大规模训练下暴露出两个机制级根因问题：

1. **数值不稳定（Numerical Instability, §3.1）**：HC 递归地跨层展开后，浅层 `l` 到深层 `L` 的有效信号传播由复合映射 `∏_{i=1}^{L-l} Hres_{L-i}` 控制。把 Eq.3 递归展开得多层形式（Eq.4）：

$$
\mathbf{x}_{L} = \left(\prod_{i=1}^{L-l}\mathcal{H}_{L-i}^{\mathrm{res}}\right)\mathbf{x}_l + \sum_{i=l}^{L-1}\left(\prod_{j=1}^{L-1-i}\mathcal{H}_{L-j}^{\mathrm{res}}\right)\mathcal{H}_{i}^{\mathrm{post}\, \top}\mathcal{F}(\mathcal{H}_{i}^{\mathrm{pre}}\mathbf{x}_i, \mathcal{W}_i),
$$

对比 Eq.2 可见，Eq.2 中 `x_l` 直接出现在和号外（守恒），而 Eq.4 中 `x_l` 被复合映射 `∏ Hres_{L-i}` 调制——由于 `Hres_l` **无任何约束**，该复合映射偏离 identity mapping 的"信号守恒"性质，导致前向/反向信号范数无界放大或衰减。实证证据（§3.1, Fig.2/3，27B 模型）：
   - HC 在 ~12k step 出现 loss surge，与 gradient norm 失稳高度相关（Fig.2）。
   - 用"Amax Gain Magnitude"（复合映射的 max 绝对行和=前向增益、max 绝对列和=反向增益）度量，HC 的复合映射峰值达 **3000**（Fig.3b），与理想值 1 形成三个数量级的偏离——直接证明 residual stream 在爆炸。
   - 消融（Tab.1）显示 `Hres_l` 是 HC 性能增益的主要来源（关掉它 loss gap 从 −0.027 退到 −0.022），但它同时也是不稳定根源——这正是要修复的靶点。

2. **系统开销（System Overhead, §3.2）**：HC 的 FLOPs 增量可忽略，但 memory access（I/O）成本近似按 `n` 倍增长（Tab.2：residual connection 总 I/O 为 `2C` 读 / `C` 写，而 HC 为 `(5n+1)C + n²+2n` 读 / `(3n+1)C + n²+2n` 写）；中间激活需保留用于反向，推高 GPU 显存，常需 gradient checkpointing；pipeline parallelism 下通信成本也 `n` 倍增加，bubble 变大。

核心矛盾：HC 通过"放宽 identity mapping 以换取拓扑表达力"，但这恰好破坏了 ResNet (He et al. 2016b) 十年来支撑大规模训练稳定性的 identity mapping 性质。mHC 的命题是——**能否在保留 HC 拓扑表达力的同时，把 residual mapping 投影回一个使 identity mapping 性质被"恢复"的流形上？**

> 公式权威源：本节 Eq.1/2/3/4 的 LaTeX 取自 `extraction/formulas.json[hc-manifold-constrained-hyper-connections][0..3]`，与 `fulltext/...txt` Eq.(1)(2)(3)(4) 逐字符校验一致；本 slug 无 M3 图描述（`minimax_captions.json` 未收录对应 PNG），Fig.2/3 的图机制描述按 `.txt` §3.1 转述，不走 `$$` 渲染。

## 关键创新点

### 1. Manifold-Constrained Hyper-Connections：把 `Hres_l` 投影到 Birkhoff polytope（§4.1）
**机制**：约束 `Hres_l ∈ Mres`，其中 `Mres` 是 doubly stochastic matrix 流形（Birkhoff polytope）——非负且行和、列和均为 1。形式化定义（Eq.6）：

$$
\mathcal{P}_{\mathcal{M}^\mathrm{res}}(\hres{l}) \coloneq \left\{ \hres{l} \in \mathbb{R}^{n \times n} \mid \hres{l}\mathbf{1}_n = \mathbf{1}_n, \ \mathbf{1}^\top_n\hres{l} = \mathbf{1}^\top_n, \ \hres{l} \geq 0 \right\},
$$

其中 `1_n` 是全 1 的 `n` 维向量。当 `n=1` 时 doubly stochastic 条件退化为标量 1，即恢复原始 identity mapping（§4.1）——这是 mHC 严格泛化 ResNet/HC 的关键节点。

这一约束带来三条严格理论性质（§4.1）：
- **Norm Preservation**：doubly stochastic 矩阵的 spectral norm `‖Hres_l‖_2 ≤ 1`，即 non-expansive，从机制上抑制梯度爆炸。
- **Compositional Closure**：doubly stochastic 矩阵集合在矩阵乘法下闭合，因此复合映射 `∏ Hres_{L-i}`（见 §1 Eq.4）仍是 doubly stochastic——任意深度上都保持守恒，这是 HC 最缺的性质。
- **Geometric Interpretation**：Birkhoff polytope 是所有 permutation matrix 的凸包，故 `Hres_l` 是置换的凸组合，反复作用单调增强跨流混合，充当稳健的特征融合。

此外对 `Hpre_l`、`Hpost_l` 施加非负约束（§4.1 末），防止正负系数叠加引起的信号对消——也可视为一种特殊流形投影。

**效果**：在 27B 模型上，mHC 把复合映射的 Amax Gain Magnitude 从 HC 的峰值 3000 压到最大约 1.6（§5.4, Fig.7b）——**减少约三个数量级**；训练曲线不再出现 HC 的 12k-step loss surge，gradient norm 与 baseline 平稳度相当（Fig.5）。同时仍保留了 HC 的性能增益：相对 baseline 最终 loss 降低 0.021（§5.2）。

### 2. Sinkhorn-Knopp 参数化与 manifold projection（§4.2）
**机制**：mHC 沿用 HC 的 dynamic + static 双部分参数化。HC 原始形式（§3 Eq.5）对 `x_l ∈ R^{n×C}` 逐行 RMSNorm 后生成三组系数：

$$
\begin{cases} \tilde{\mathbf{x}}_l = \text{RMSNorm}(\mathbf{x}_l) \\ \hpre{l} = \alpha_l^\mathrm{pre} \cdot \tanh(\theta^\mathrm{pre}_l \tilde{\mathbf{x}}^\top_l) + \mathbf{b}_l^\mathrm{pre} \\ \hpost{l} = \alpha_l^\mathrm{post} \cdot \tanh(\theta^\mathrm{post}_l \tilde{\mathbf{x}}^\top_l) + \mathbf{b}_l^\mathrm{post} \\ \hres{l} = \alpha_l^\mathrm{res} \cdot \tanh(\theta^\mathrm{res}_l \tilde{\mathbf{x}}^\top_l) + \mathbf{b}_l^\mathrm{res}, \\ \end{cases}
$$

其中 RMSNorm 作用于最后维度，标量 `α_pre/α_post/α_res` 是初值很小的可学习 gating factor，`θ_*` 是动态映射线性投影、`b_*` 是静态偏置（§3）。mHC 在此基础上做两步改造：

**改造一：flatten 保留全部上下文。** mHC 把输入 `x_l ∈ R^{n×C}` **flatten** 为 `x̃_l = vec(x_l) ∈ R^{1×nC}`（而非 HC 的逐行 RMSNorm），线性投影参数变为 `φ_pre, φ_post ∈ R^{nC×n}`、`φ_res ∈ R^{nC×n²}`。新的参数化（Eq.7）：

$$
\begin{cases} \vec{\mathbf{x}}'_l = \text{RMSNorm}(\vec{\mathbf{x}}_l) \\ \tlhpre{l} = \alpha_l^\mathrm{pre} \cdot (\vec{\mathbf{x}}'_l\phi^\mathrm{pre}_l) + \mathbf{b}_l^\mathrm{pre} \\ \tlhpost{l} = \alpha_l^\mathrm{post} \cdot (\vec{\mathbf{x}}'_l\phi^\mathrm{post}_l) + \mathbf{b}_l^\mathrm{post} \\ \tlhres{l} = \alpha_l^\mathrm{res} \cdot \text{mat}(\vec{\mathbf{x}}'_l\phi^\mathrm{res}_l) + \mathbf{b}_l^\mathrm{res}, \\ \end{cases}
$$

其中 `mat(·)` 是 `R^{1×n²} → R^{n×n}` 的 reshape。

**改造二：manifold projection。** 把上述未约束的 `H̃_*` 经由算子投影到目标流形（Eq.8）：

$$
\begin{cases} \hpre{l} = \sigma(\tlhpre{l}) \\ \hpost{l} = 2\sigma(\tlhpost{l}) \\ \hres{l} = \text{Sinkhorn-Knopp}(\tlhres{l}), \end{cases}
$$

- `Hpre_l = σ(H̃_pre_l)`（Sigmoid → 非负）
- `Hpost_l = 2σ(H̃_post_l)`（Sigmoid×2 → 非负且均值为 1，匹配 residual merge 量纲）
- `Hres_l = Sinkhorn-Knopp(H̃_res_l)` → 投影到 Eq.6 定义的 Birkhoff polytope

Sinkhorn-Knopp 算子：先 `exp(·)` 使所有元素为正得到 `M^(0)=exp(H̃_res_l)`，再交替做行归一化 `T_r` 与列归一化 `T_c`（Eq.9）：

$$
\mathbf{M}^{(t)} = \mathcal{T}_r\left(\mathcal{T}_c(\mathbf{M}^{(t-1)})\right),
$$

迭代 `t_max` 次收敛到 doubly stochastic，`Hres_l = M^(t_max)`，`t_max → ∞` 时严格收敛。**实验取 `t_max = 20`**（§4.2）。

**效果**：以可微迭代近似实现 Birkhoff 投影。`t_max=20` 下前向信号增益≈1、反向梯度增益略偏离 1（Fig.7a），复合后偏差积累但被闭包性质约束在 ≤1.6（§5.4）——这是用有限迭代换取计算效率的明确边界。

### 3. Efficient Infrastructure Design：把 `n=4` 的训练时间开销压到 6.7%（§4.3）
**机制**：针对三处瓶颈分别定制：

- **Kernel Fusion（§4.3.1）**：把 RMSNorm 的除以范数操作 **reorder 到矩阵乘之后**（数学等价但避免对 `R^{1×nC}` 高维向量直接做 norm 的延迟）；用 mixed precision（`φ_l: tfloat32`、`x̃_l: bfloat16`、标量与 bias 为 `float32`，Eq.10–13）；用 TileLang (Wang et al. 2025) 实现三个专用 kernel：① fused 两遍 scan + 前向/反向 matrix mul（Eq.14–15）；② 轻量系数操作合并（Eq.16–18）；③ Sinkhorn-Knopp 迭代单 kernel + 自定义反向 kernel 在片上重算整条迭代链（Eq.19）。另外把 `Hpost_l ⊤ F(·)` 与 `Hres_l` 应用与 residual merge 融合，使该 kernel 的读从 `(3n+1)C` 降到 `(n+1)C`、写从 `3nC` 降到 `nC`。

- **Selective Recomputing（§4.3.2）**：丢弃 mHC kernel 的中间激活，反向时只重跑 mHC kernel（不重跑重的层函数 `F`）。对连续 `L_r` 层只存首层输入 `x_{l0}`。最优化目标给出最优 block size（Eq.20）：在 resident 内存 `nC×⌈L/L_r⌉` 与 transient 内存 `(n+2)C×L_r` 之间取最小：

$$
L_r^* = \arg\min_{L_r} \left[ nC\times \left\lceil\frac{L}{L_r}\right\rceil + (n+2)C\times L_r \right] \approx \sqrt{\frac{nL}{n+2}}.
$$

理论最优值恰好与 pipeline stage 的层数对齐，故**把 recomputation 边界与 pipeline stage 对齐**。

- **Overlapping Communication in DualPipe（§4.3.3）**：扩展 DualPipe (DeepSeek-V3) 调度，处理 `n`-stream residual 跨 stage 的额外通信与 stage 边界处的 `L_r` 层 mHC 重算开销（Fig.4）。关键技巧：MLP 层的 `F_post,res` kernel 在**专用高优先级 compute stream** 上执行避免阻塞通信流；attention 层不使用 persistent kernel 以允许抢占式调度；重算与 pipeline 通信解耦（每 stage 初始激活 `x_{l0}` 已本地缓存）。

**效果**：在 `n=4` 的大规模训练中仅引入 **6.7% 额外时间开销**（§1, §4.3），使 mHC 在工业规模上可行。

### 4. 性能与可扩展性实证（§5）
- **27B main results（Tab.4）**：mHC 在 8 个下游 benchmark 上 8/8 优于 baseline，多数优于 HC。相对 HC 的额外增益：BBH +2.1%（51.0 vs 48.9）、DROP +2.3%（53.9 vs 51.6）、MMLU +0.4%、GSM8K +0.6%、TriviaQA +1.3%。说明稳定性不仅没损害、反而进一步释放了 HC 的表达力（推理类任务受益最显著）。
- **Scaling（§5.3, Fig.6）**：compute scaling curve（3B/9B/27B）显示 mHC 相对 baseline 的 loss 优势随规模增大仅"轻微衰减"——robust to scale；token scaling curve（3B on 1T tokens）持续保持优势。
- **Stability Analysis（§5.4, Fig.7/8）**：可视化 HC 与 mHC 的单层/复合映射矩阵——HC 在大增益时其他路径也普遍失稳（整体不稳定）；mHC 始终平稳。

## 表格（原文结构化）

### Tab.1 — HC 组件消融（absolute loss gap，越负越好）
| Hres_l | Hpre_l | Hpost_l | Absolute Loss Gap |
|---|---|---|---|
| ✗（identity） | ✗（uniform 1/n） | ✗（ones） | 0.0（baseline） |
| ✓ | ✗ | ✗ | −0.022 |
| ✓ | ✓ | ✗ | −0.025 |
| ✓ | ✓ | ✓ | −0.027 |

→ `Hres_l` 单独贡献 −0.022（占整体 −0.027 的 81%），是 HC 的核心增益源——也正是 mHC 约束的目标。

### Tab.2 — 单 residual 层 per-token memory access（forward, 排除 `F` 内部 I/O）
| Method | Read (Elements) | Write (Elements) |
|---|---|---|
| Residual Connection | `2C` | `C` |
| Hyper-Connections | `(5n+1)C + n² + 2n` | `(3n+1)C + n² + 2n` |

→ HC 的读约为 baseline 的 `(5n+1)/2` 倍；`n=4` 时读为 `21C+24` vs `2C`——这是 mHC 必须用 kernel fusion 缓解的"memory wall"。

### Tab.4 — 27B 模型 8-benchmark 对比
| Benchmark (Metric) | # Shots | Baseline | HC | mHC |
|---|---|---|---|---|
| BBH (EM) | 3-shot | 43.8 | 48.9 | **51.0** |
| DROP (F1) | 3-shot | 47.0 | 51.6 | **53.9** |
| GSM8K (EM) | 8-shot | 46.7 | 53.2 | **53.8** |
| HellaSwag (Acc.) | 10-shot | 73.7 | 74.3 | **74.7** |
| MATH (EM) | 4-shot | 22.0 | **26.4** | 26.0 |
| MMLU (Acc.) | 5-shot | 59.0 | 63.0 | **63.4** |
| PIQA (Acc.) | 0-shot | 78.5 | 79.9 | **80.5** |
| TriviaQA (EM) | 5-shot | 54.3 | 56.3 | **57.6** |

→ mHC 仅在 MATH 上以 0.4 pt 微弱落后 HC，其余 7 项均胜；推理密集型（BBH/DROP）增益最大。

### Tab.5（节选）— 模型规格与超参
| Attribute | 3B | 9B | 27B | 3B / 1T Tokens |
|---|---|---|---|---|
| Total Params | 2.97B | 9.18B | 27.0B | 2.97B |
| Layers | 12 | 18 | 30 | 12 |
| Routed / Active / Shared Experts | 64 / 6 / — | 64 / 6 / 2 | 72 / 6 / 2 | 64 / 6 / — |
| Dimension / FFN Dim | 1280 / 896 | 1920 / 1280 | 2560 / 1536 | 1280 / 896 |
| Attention Heads / Dim | 16 / 128 | 24 / 128 | 32 / 128 | 16 / 128 |
| Attention Variant | MLA | MLA | MLA | MLA |
| mHC/HC Expansion `n` | 4 | 4 | 4 | 4 |
| Gating Factor Init `α` | 0.01 | 0.01 | 0.01 | 0.01 |
| Sinkhorn-Knopp `t_max` | 20 | 20 | 20 | 20 |
| Training Tokens | 39.3B | 105B | 262B | 1.05T |
| Base LR | 8.6e-4 | 5.9e-4 | 4.0e-4 | 9.0e-4 |

→ 架构基于 DeepSeek-V3（MoE + MLA + RoPE + RMSNorm），mHC 是即插即用替换；`α=0.01` 的小初值保证训练初期接近 identity（与 HC 的初始化哲学一致）。

## 与同类对比

- **vs [[hyper-connections]]（HC, Zhu et al. 2024）**：mHC 是 HC 的严格泛化——`n=1` 或 unconstrained `Hres` 时退化回 HC。机制差异只在 `Hres_l`（HC：unconstrained learnable；mHC：Sinkhorn-Knopp 投影到 Birkhoff polytope）及 `Hpre_l, Hpost_l` 加非负约束。效果差异：mHC 把复合映射增益从 ~3000 压到 ~1.6，消除 12k-step loss surge；下游在 7/8 benchmark 上进一步优于 HC（BBH +2.1, DROP +2.3）。代价：Sinkhorn-Knopp 20 次迭代 + 自定义反向 kernel 的工程复杂度。
- **vs ResNet identity mapping（He et al. 2016b）**：ResNet 强制 `Hres = I` 最稳但完全禁止跨流信息交换；mHC 把 `Hres` 放在 `I` 所在的同一闭包流形（Birkhoff polytope 包含所有置换矩阵，`I` 是其中一个顶点）上，允许"受控的跨流混合"——是 identity mapping 的连续松弛而非放弃。
- **vs [[root-mean-square-layer-normalization]]（RMSNorm）**：正交关系。RMSNorm 承运**层内**激活稳定（mHC 沿用 HC 用 RMSNorm 归一化 `x̃_l`，§3 Eq.5 / §4.2 Eq.7）；mHC 承运**跨层**信号守恒。两者可叠加，论文中已并用。
- **vs RMT（Mak & Flanigan 2025）/ MUDDFormer（Xiao et al. 2025）/ DenseFormer（Pagliardini et al. 2024）**：同属 §2.2 "扩展 residual stream 宽度"的 macro-design 家族，但都**未约束**复合映射的守恒性，因此同样面临 instability & scalability 风险且伴有 memory access 开销；mHC 是这一谱系中首个明确以"流形约束恢复 identity mapping"为命题的工作。
- **vs [[attention-residuals]] / [[kimi-k3-open-frontier-intelligence]] 的 AttnRes**：同为 residual topology 变体分支，但 mHC 聚焦"宽度扩展 + 双随机约束"，AttnRes 聚焦"用注意力替代固定残差权重"——两者是 residual 拓扑设计的不同切面，可视为 HC 谱系的兄弟分支。

## 跨论文关系（→ MOC 谱系）

- **[[hyper-connections]]**：mHC 的直接前身与基底。HC 提出可学习/动态连接矩阵（Eq.3, 5），mHC 在其之上施加 Birkhoff polytope 流形投影。同属 ByteDance/DeepSeek 系作者链。
- **[[root-mean-square-layer-normalization]]**：mHC 参数化中 RMSNorm 是必备组件（归一化 `x̃_l` 后做动态映射），与跨层流形约束正交叠加。
- **[[attention-residuals]]**：残差/层间拓扑谱系的兄弟分支——同样把固定残差替换为可学习结构，但用注意力机制而非矩阵流形投影。
- **[[kimi-k3-open-frontier-intelligence]]**：frontier 模型实例，hybrid KDA-MLA + AttnRes 类拓扑的生产规模部署；mHC 是同谱系（层间拓扑）的工业可行替代路径。
- **[[deepseek-v3-technical-report]]**：mHC 的实验架构基座（MoE + MLA + DualPipe + auxiliary-loss-free load balancing），Tab.5 全部超参对齐 V3 体系。
- **[[deepseek-v4-towards-highly-efficient-million-token-context-intelligence]]**：DeepSeek 系后继，可能继承 mHC/DualPipe 这类基础设施成果（同实验室演进线）。

## 局限与边界

- **Sinkhorn-Knopp 是近似解**：`t_max=20` 有限迭代不能精确达到 doubly stochastic，反向梯度增益单层略偏离 1（Fig.7a），复合后最大偏差 ~1.6。虽然比 HC 的 3000 改善三个数量级，但并非严格 1——若未来 `n` 或深度进一步增大，累积偏差是否仍可控未被验证。
- **`n` 的上限未探索**：所有实验 `n=4`。论文未报告更大 `n`（如 8、16）下 Birkhoff 投影的数值/性能/工程表现，也未给出 `n` 的选择准则。Birkhoff polytope 的几何性质随 `n` 增大如何影响表达力与可优化性是开放问题。
- **流形选择的单一性**：作者仅在 §6 展望中提到"框架可容纳 diverse manifold constraints"，但本文只实证了 doubly stochastic 一种。其他流形（如 orthogonal group、stochastic but non-doubly-stochastic）是否更优未探究。
- **基础设施复杂度高**：6.7% 开销依赖 TileLang 自定义 kernel + 自定义 Sinkhorn-Knopp 反向 + DualPipe 扩展 + 高优先级流调度（§4.3）。这套栈强耦合 DeepSeek-V3 训练系统，迁移到其他框架/硬件（非 Ascend/non-Hopper）成本显著，复现门槛高。
- **仅在 DeepSeek-V3 系 MoE+MLA 上验证**：缺 dense 模型、非-MoE 架构、非-MLA attention 的对照；mHC 是否对 dense Transformer 同样有效未知。
- **MATH 上微弱输给 HC**（26.0 vs 26.4, Tab.4）：约束带来的稳定性在个别推理任务上可能略损表达力——作者未深入分析此例外。
- **未解决 `Hpre_l/Hpost_l` 的理论保证**：仅施加非负约束（Sigmoid×2）防信号对消，但未像 `Hres_l` 那样给出 spectral norm / 闭包等严格性质——这两个映射的复合行为是否在超深网络下也稳定，缺乏形式化分析。
- **forward Amax gain 与 backward 不对称**：Fig.7 显示前向增益≈1 而反向略偏，意味着梯度的有偏性可能影响优化轨迹——长期训练（远超 50k/100k step）是否累积偏差未知。
