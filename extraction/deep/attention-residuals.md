# Attention Residuals — 技术点深读（DEEP 2026-08-18, 公式重跑）

> 全要素深读笔记。独立文件，extract_phase1 重跑不丢。
> 论文：Attention Residuals（Kimi Team, Technical Report, 16 Mar 2026）· arXiv:2603.15031v1
> 作者：Guangyu Chen*, Yu Zhang*, Jianlin Su* et al.（Moonshot AI / Kimi Team）
> 公式权威源 = extraction/formulas.json LaTeX（下方 $$...$$ 直接引用）；图上下文 = M3 caption 文本（禁图直读）。

## 核心问题

标准残差 `h_l = h_{l-1} + f_{l-1}(h_{l-1})` 在 PreNorm 主导的现代 LLM 中是事实构件，但其展开形式表明：**深度方向的聚合始终用固定的单位权重（fixed unit weights）**，没有任何机制选择性地强调或抑制某一层的贡献（§1, §2.1）。这一展开形式由 formulas.json 的标准残差 mixing matrix 给出（Eq.见下方关键创新点 §4 与 §6.2，all-ones 下三角）：

$$
\begin{bmatrix} \bm{h}_1 \\ \bm{h}_2 \\ \vdots \\ \bm{h}_L \end{bmatrix} = \begin{bmatrix} 1 & & & \\ 1 & 1 & & \\ \vdots & \vdots & \ddots & \\ 1 & 1 & \cdots & 1 \end{bmatrix} \begin{bmatrix} \bm{v}_0 \\ \bm{v}_1 \\ \vdots \\ \bm{v}_{L-1} \end{bmatrix}
$$

全 1 下三角 = 1-semiseparable 且 fixed。Figure 1（p.1, M3）把这一定性对比画成同一张架构图的三栏：**(a) Standard Residuals** 用 ⊕ 级联 Attention/MoE，全部 prior outputs 等权相加；**(b) Full AttnRes** 把 ⊕ 换成 Q·K^T-over-V 的 ∝-op，每层对全部先前表示做 softmax；**(c) Block AttnRes** 把层聚合成 block 后只在 block summary 上做 attention。M3 caption 明确点出三栏共同传达的唯一变量是"聚合算子从固定加法 → 学习型 softmax"。由此衍生三类机制级缺陷：

1. **PreNorm dilution（§1, §5.2, §7）**：PreNorm 保留了 identity 梯度路径，但 `‖h_l‖` 随深度 `O(L)` 增长，每层的相对贡献被稀释；深层被迫学越来越大、偏离 normalized scale 的输出来维持影响力，限制有效深度，并使大量深层可被剪枝而几乎无损 [11]。Figure 5(b)（p.10, M3）给出最直接证据：Baseline 的 per-block output magnitude 随 block index 单调增长至 ~12，而 Block AttnRes 的 magnitude 保持在 ~1–2 区间并在 block 边界周期性 reset——M3 解读"可视化地看见 dilution 的消除"。
2. **无选择性访问（§2.1 Limitations）**：每层只能拿到 `h_{l-1}` 这一个压缩态（conflates all earlier outputs），attention 与 MLP 接收同一聚合态，无法差异化加权；早期层信息一旦在聚合中丢失就无法在深层恢复。
3. **不可控的输出生长**：深层为争夺残差通道的话语权而放大自身输出，进一步 destabilize 训练；Figure 5(c)（p.10, M3）显示 Baseline 早期层 gradient magnitude 出现 ~2.4×10⁻⁵ 的尖峰随后衰减，而 AttnRes 几乎全层均匀。

作者把这一瓶颈对偶到 RNN 在序列维度的瓶颈：RNN 把全部历史压进单一 `h_t`，Transformer 用 sequence-wise softmax attention 解决之；同理，depth-wise aggregation 仍受 fixed recurrence 束缚，应当用 **depth-wise softmax attention** 替换（§3）。这是论文的核心立场——把"linear-to-softmax over sequence"的同一种过渡，**在 depth 维度上重演一次**（§1, §6.1, §6.2）。Figure 9（p.15, M3）用 L=4 的 depth mixing matrix `M` 把这一立场形式化：Highway 是 1-semiseparable（标量门 γ 累积积），(m)HC 是 m-semiseparable（A× 转移矩阵），Full AttnRes 是 dense rank-L 的 φ(w,k) 矩阵，Block AttnRes 介于 N 与 N+S 之间——M3 解读明确"AttnRes 并非全新机制，而是 structured, input-dependent depth mixing 的一个特例"，同一张图同时给出了"线性→softmax"过渡与统一分类视角。

## 关键创新点

### 1. Full Attention Residuals（Full AttnRes）— 深度 softmax attention（§3.1, Eq.1–4）
**机制**：每层 l 引入一个**学习型 pseudo-query** `w_l ∈ R^d`（与 forward 计算解耦的纯参数），把 embedding `h_1` 当作 `v_0/k_0`、把每层输出 `f_i(h_i)` 当作 `k_i = v_i`，对 `i < l` 的所有来源做 **softmax 加权聚合**。核心公式（formulas.json Eq.1–4，权威源）：

$$
\bm{h}_{l} = \brickred{\alpha_{0 \to l}} \cdot \bm{h}_1 + \sum_{i=1}^{l-1} \brickred{\alpha_{i \to l}} \cdot f_i(\bm{h}_{i})
$$

$$
\brickred{\alpha_{i \to l}} = \frac{\phi\left(\bm{q}_{l}, \bm{k}_{i}\right)}{\sum_{j=0}^{l-1} \phi\left(\bm{q}_{l}, \bm{k}_{j}\right)}
$$

$$
\bm{q}_{l} = \bm{w}_{l}, \quad \quad \bm{k}_{i} = \bm{v}_{i} = \begin{cases} \bm{h}_1 & i = 0 \\ f_i(\bm{h}_{i}) & 1 \leq i \leq l-1 \end{cases}
$$

$$
\bm{h}_{l} = \sum_{i=0}^{l-1} \brickred{\alpha_{i \to l}} \cdot \bm{v}_{i}
$$

其中 `ϕ(q,k) = exp(qᵀ·RMSNorm(k))`（§3.1 文本给定，formulas.json 未单列 ϕ 定义但 Eq.2 内嵌）。RMSNorm-in-ϕ 防止"输出幅度大的层"主导 softmax（§3.1）。

**LaTeX↔M3 双源校验**：Figure 1(b)（p.1, M3）架构图标出每个 AttnRes 节点带 `w`（pseudo-query）、`α`（softmax 权重）、`Q/K/V` 标签——M3 解读"Q·K^T over V 的 ∝-op 替换 ⊕"。这与 Eq.2 的 `α = ϕ(q_l,k_i)/Σϕ` 完全对应：图中 `w` = 公式 `q_l = w_l`，图中 `α` = 公式 `α_{i→l}`，图中 `⊕` 被替换为 `Σ α·v`（Eq.4）。`w` 在图中作为独立节点（非从 forward 流出）正对应"pseudo-query decoupled from forward"这一关键设计。

**初始化关键**：所有 `w_l` 必须零初始化，使初始 `α` 在来源间均匀（退化为等权平均），避免训练 volatility（§5）。

**效果**：
- 16 层 ablation（§5.3 Table 4）：Full AttnRes loss = **1.737** vs PreNorm baseline 1.766（−0.029），vs DenseFormer 1.767（几乎无改善），vs mHC 1.747。
- Scaling law（§5.1 Fig.4, p.9, M3）：log-log 图上三条幂律曲线 Baseline `1.891·C^{-0.057}`、Full `1.865·C^{-0.057}`、Block `1.870·C^{-0.058}`；M3 解读指出 Full 与 Block 曲线在最大尺度几乎重合，双头箭头标注 **1.25×** compute advantage。
- Block AttnRes 在 5.6 PFLOP/s-days 达 loss 1.692 vs Baseline 1.714，等价 **1.25× compute advantage**（§1, §5.1）。

### 2. Block Attention Residuals（Block AttnRes）— 可扩展变体（§3.2, §4）
**机制**：把 L 层划分成 N 个大小 S=L/N 的 block。**块内**用普通 residual 求和得到 block 表示（Eq.5，权威源）：

$$
\bm{b}_n = \sum_{j \in \mathcal{B}_n} f_j(\bm{h}_j)
$$

**块间**仅在 N 个 block 表示 + embedding 上做 softmax attention。第 n 个 block 内第 i 层的 V 集合（Eq.6，权威源）：

$$
\mathbf{V} = \begin{cases} [\bm{b}_0, \bm{b}_1, \ldots, \bm{b}_{n-1}]^\top & \text{if } i = 1 \text{ (first layer of block } n\text{)} \\ [\bm{b}_0, \bm{b}_1, \ldots, \bm{b}_{n-1}, \bm{b}_n^{i-1}]^\top & \text{if } i \geq 2 \text{ (subsequent layers)} \\ \end{cases}
$$

Keys 与 attention weights 沿用 Eq.2/Eq.3。`b_0 = h_1`（embedding 恒为 source）。`N=L` 退化为 Full AttnRes，`N=1` 退化为标准 residual（embedding 独立为 b_0）。

**LaTeX↔M3 双源校验**：Figure 2（p.5, M3）给出 PyTorch 伪代码 `block_attn_res`，其 `V = torch.stack(blocks + [partial_block])` 直接对应 Eq.6 中 `[b_0,...,b_{n-1}, b_n^{i-1}]`（i≥2 分支）；M3 明确"无 per-token query"——对应 `q_l = w_l` 为纯参数而非 h_l 投影。M3 还指出"每层 forward 调用 `block_attn_res` 两次（attention 前、MLP 前一次）"——对应伪代码 `block_size // 2` 的计数逻辑（block_size 按 ATTN+MLP 计数故除 2）。Figure 1(c) 架构图中"Block n-2 / Block n-1"的 block 节点 + 单个 `w` per AttnRes op 即 Eq.5/Eq.6 的可视化。

**效果**：
- 内存/通信从 `O(Ld)` 降到 `O(Nd)`；算力 `O(L²)` 降到 `O(LN)`（§3.2 Efficiency）。
- **经验上 N≈8 即可恢复 Full AttnRes 的大部分增益**，每 token 仅需存储 8 个 hidden state（§3.2, §5）。
- 16 层 ablation（Table 4, S=4）：Block AttnRes loss = 1.746，与 Full 仅差 0.009。
- Fig.6（p.11, M3）block-size sweep：曲线 S=32→2 为 1.757/1.753/1.748/1.746/1.746，Baseline 1.766 横线、Full(S=1) 1.737 横线；M3 解读点出 S=4 已与 S=2 持平（1.746），构成"内存/精度 sweet spot"。

### 3. 工程化：让 Block AttnRes 在大规模训练/推理实用（§4）
**机制（训练侧 — cross-stage caching）**：在 interleaved pipeline schedule（P 物理 stage × V 虚拟 stage，C=PV）下，naïve 每次跨 stage 传全部累积 block（Eq.7，权威源）：

$$
\mathrm{Comm}_{\text{na\"ive}} = \sum_{j=1}^{C-1} jN_p \cdot d = \frac{C(C{-}1)}{2}\,N_p d.
$$

**Cross-stage caching**：每个物理 stage 缓存早期虚拟 stage 收到的 block，后续 transition 只传增量；总通信降到（Eq.8，权威源）：

$$
\mathrm{Comm}_{\text{cached}} = \underbrace{\frac{P(P{-}1)}{2}\, N_p d}_{\text{first virtual stage}} + \underbrace{(V{-}1)\, P^2\, N_p d}_{\text{subsequent virtual stages}}.
$$

把 peak per-transition cost 从 `O(C)` 降到 `O(P)`，即 V× 改善，可与 1F1B 稳态完全重叠。

**LaTeX↔M3 双源校验**：Figure 3（p.6, M3）用 P=4/V=2 的矩阵可视化这一过程。M3 caption 明确"左列 Virtual Stage 0 各 rank 累积接收 `[b0]`→`[b0,b1]`→…（对应 Eq.8 的 first virtual stage 累积项 `P(P−1)/2·N_p d`），右列 Virtual Stage 1 只传增量 `+[b1,b2]`/`+[b2,b3]`（对应 subsequent virtual stages 的增量项 `(V−1)·P²·N_p d`）"。M3 称第二个 virtual stage 因此省去 6 次冗余块传输——与正文 §4.1 "for the second virtual stage, caching eliminates 6 redundant block transmissions" 一致。hatched boxes = AttnRes block 边界（即 Eq.5 的 `b_n` 完成点）。

**机制（推理侧 — Two-phase computation, Algorithm 1）**：利用 pseudo-query `w_l` 与 forward 解耦这一性质——同一 block 内 S 个 query 可批量对 N 个 block 表示做一次矩阵乘：
- Phase 1：并行算 inter-block attention（一次 batched query vs cached block reps），返回 output + softmax 统计量（max, log-sum-exp）。
- Phase 2：按序算 intra-block attention（对 evolving partial sum `b_n^i`），用 **online softmax [31]** 与 Phase 1 结果 element-wise merge，便于 kernel fusion。

I/O 推导见 Appendix B（formulas.json Eq.10–17，权威源）：

$$
\mathrm{Read}_{\text{inter}}^{(n)} = 2(n-1)Sd
$$

$$
\mathrm{Read}_{\text{inter}} = \sum_{n=1}^{N} 2(n-1)Sd = 2Sd \cdot \frac{N(N-1)}{2} = dL(N-1).
$$

$$
\mathrm{Write}_{\text{inter}} = Ld
$$

$$
\mathrm{Read}_{\text{intra}}^{(n)} = \sum_{t=1}^{S} 2(t-1)d = S(S-1)d.
$$

$$
\mathrm{Read}_{\text{total}} = dL(N-1) + N \cdot S(S-1)d, \qquad \mathrm{Write}_{\text{total}} = 2Ld.
$$

$$
\text{Read per layer} = (N-1)d + (S-1)d = (S + N - 2)d, \qquad \text{Write per layer} = 2d,
$$

$$
\boxed{\;\text{Total I/O per layer} = (S + N)\,d.\;}
$$

即 batching inter-block reads 把 per-layer I/O 从 `O(L)` 降到 `O(S+N)`。**Memory-efficient prefilling**：128K-token/8-block 的 block reps 本需 15 GB；沿 sequence 维 TP-shard 后每设备 1.9 GB，配 16K chunked prefill 进一步降到 <0.3 GB（§4.2）。

**效果**：
- 训练端到端 overhead：不开 pipeline 时可忽略；开 pipeline 时 **<4%**（§4.1）。
- 推理端到端 latency overhead **<2%**（§1, §4.2）。
- per-layer I/O（Table 1, L=128,N=8,S=16,m=4）：Standard 3d；mHC(m=4) **34d**；AttnRes Full **24d**；AttnRes Block 仅 **5.5d**（Phase1 5.5d + Phase2 4d）。即在更低 I/O 下匹配 mHC 的 loss。

### 4. 结构化矩阵统一视角 + Sequence-Depth Duality（§6.1, §6.2, Table 5, Fig.9）
**机制**：用 depth mixing matrix `M ∈ R^{L×L}`（`h_l = Σ_i M_{i→l} v_i`）的 **semiseparable rank** 统一定位所有残差变体。Figure 9（p.15, M3）把 L=4 的 M 矩阵画成四联图。

**(m)HC 的 mixing matrix**（Eq.10，权威源）：

$$
\mathbf{M}_{i \to l} = \bm{\beta}_{i}^\top \, \mathbf{A}_{i+1 \to l}^{\times} \, \bm{\alpha}_{l},
$$

**(m)HC 的 stream 递推**（formulas.json，权威源）：

$$
\mathbf{H}_{l} = \mathbf{H}_{l-1} \mathbf{A}_{l} + f_{l-1}(\mathbf{H}_{l-1} \bm{\alpha}_{l-1})\, \bm{\beta}_{l-1}^\top,
$$

**TTT 的序列侧同构**（Eq.9，权威源，sequence-depth duality）：

$$
\mathbf{W}_t = \mathbf{W}_{t-1} - \eta\,\nabla\ell(\mathbf{W}_{t-1};\, \bm{x}_t),
$$

linear 时退化为 `S_t = S_{t-1} + k_t v_tᵀ`，与标准 residual 的深度累加同形。

**LaTeX↔M3 双源校验**：Figure 9 四联图与公式逐项对应——(1) Highway 面板用标量门 `g` 与累积积 `γ×_{i→l}` 填充下三角（M3 caption 写出 `γ×_{1→2}, g_2, γ×_{1→3}, g_2·γ×_{2→3}, ...`），即 Highway 的 `M_{i→l} = g_{i+1}·Π(1−g_j)`，1-semiseparable；(2) (m)HC 面板每项为 `β_iᵀ·A×_{i+1→l}·α_l`，即 Eq.10 的逐 entry 展开，M3 caption 直接列出 `β_0ᵀα_1, β_0ᵀA×_{1→2}α_2, β_1ᵀα_2, ...`，m-semiseparable；(3) Full AttnRes 面板每项为未归一化 `φ(w_l, k_i)`（M3 caption：`ϕ(w1,k0), ϕ(w2,k0), ϕ(w2,k1), ...`），对应 Eq.2 的分子项，dense rank-L；(4) Block AttnRes(S=2) 面板同 block 内项共享 block key（背景色分组），如 `ϕ(w3,k1+k2)` 表示 block 内两层的 key 合并——对应 Eq.5 的 `b_n = Σ f_j` 求和。M3 解读明确"四变体都塌缩成单一线性 mixing 视图 M·v，暴露有效 rank（1 → m → N → L）"。背景色分组在 AttnRes 面板标注"同 source（Full）/同 source block（Block）"——这是公式中 `k_i = v_i`（Full）vs `k_i = b_n`（Block）的图形化对照。

- Standard residual：`M_{i→l}=1` 全 1 下三角（上方 Eq.），**1-semiseparable**（fixed）。
- Highway：`M_{i→l}=g_{i+1}·Π(1−g_j)`，仍是 **1-semiseparable** 但 input-dependent（stick-breaking softmax-free depth attention, [49]）。
- (m)HC [72,59]：`M_{i→l}=β_iᵀ·A^{×}_{i+1→l}·α_l`（Eq.10），`m×m` transitions 使 M **m-semiseparable**。
- **Full AttnRes**：`M_{i→l}=α_{i→l}` 直接来自 softmax，**dense, rank-L**。
- **Block AttnRes**：rank 在 N 到 N+S 之间（§6.2）。

**核心论断（§6.2 末段）**：当 `ϕ` 可分解为 `ϕ(q,k)=φ(q)ᵀφ(k)`（线性 attention kernel），depth-wise attention 退化为 recurrence——这正是 **MRLA↔GLA**、**DDL↔DeltaNet** 对应的根源。因此 (m)HC 本质是 **depth-wise linear attention with matrix-valued states**，AttnRes 是 **depth-wise softmax attention**，完成 depth 上的 linear→softmax 过渡。

### 5. 48B/3B MoE 大规模验证（§5.2）
**机制**：在 Kimi Linear [69] 配置上叠加 AttnRes——27 Transformer blocks（54 层）、8/256 routed + 1 shared expert、48B total / 3B act；Block AttnRes 用 6 层/block → 9 blocks + embedding = 10 个 depth-wise source。1.4T tokens（1T WSD + 400B mid-training），Muon 优化器，WSD LR schedule，32K context extension（NoPE-MLA 无需 YaRN）。

**效果**：
- Training dynamics（Fig.5, p.10, M3 三联图）：(a) Validation loss 中 AttnRes 全程低于 Baseline，decay 阶段 gap 拉大；(b) Output magnitude 中 Baseline 随深度单调发散至 ~12，AttnRes 在 block 边界周期性 reset、bounded 在 ~1–2；(c) Gradient magnitude（×10⁻⁵）中 Baseline 早期层 ~2.4 尖峰后衰减，AttnRes 通过 softmax 竞争显著均匀化。M3 解读总结："Block AttnRes 修复了 PreNorm 的 hidden-state 爆炸并产生均衡的深度梯度流"。Figure 5(b) 的 bounded periodic pattern 直接对应 Eq.5 中 block 边界 reset 机制——`b_n` 在 block 末完成、下一 block 从 partial sum 重启，故 magnitude 不跨 block 累积。
- Downstream（Table 3，14 项）：**全部 ≥ baseline**。最显著：GPQA-Diamond **+7.5**（36.9→44.4）、Minerva Math **+3.6**（53.5→57.1）、HumanEval **+3.1**（59.1→62.2）；knowledge 类 MMLU +1.1、TriviaQA +1.9。模式符合"深度信息流改善组合式任务"假说（§5.2）。

## 表格（原文结构化）

### Table 1 — 残差机制 per-layer memory I/O（每 token，excludes fl 内部；典型 L=128,N=8,S=16,m=4）
| 方案 | 操作 | Read | Write | Total (symbolic) | Total (typical) |
|---|---|---|---|---|---|
| Standard Residuals | Residual Merge | 2d | d | 3d | **3d** |
| mHC (m streams) | Compute α_l,β_l,A_l + Apply α/β/A + Residual Merge | md + m²+2m + ... | (8m+2)d + 2m²+4m | — | **34d** |
| AttnRes Full | Phase 1 (amortized) | (N−1)d | d | (S+N)d | **24d** |
| AttnRes Full | Phase 2 | (S−1)d | d | — | — |
| AttnRes Block | Phase 1 (amortized) | (N/S)d | d | (N/S+5)d | **5.5d** |
| AttnRes Block | Phase 2 | 3d | d | — | — |

→ Block AttnRes 的 per-layer I/O 比 mHC(m=4) 低 ~6×，且 loss 与 mHC 相当。典型数值与 Appendix B 推导（Eq.17 `Total I/O per layer = (S+N)d`）一致：Full 下 (S+N)d = (16+8)d = 24d。

### Table 2 — Scaling law 配置与 Val. Loss（5 个尺度，N=8 blocks）
| Act. Params | Tokens | L_b | d_model | d_ff | lr | batch | Baseline | Block AttnRes | Full AttnRes | mHC(-lite) |
|---|---|---|---|---|---|---|---|---|---|---|
| 194M | 38.7B | 12 | 896 | 400 | 2.99e-3 | 192 | 1.931 | 1.909 | **1.899** | 1.906 |
| 241M | 45.4B | 13 | 960 | 432 | 2.80e-3 | 256 | 1.895 | 1.875 | **1.874** | 1.869 |
| 296M | 62.1B | 14 | 1024 | 464 | 2.50e-3 | 320 | 1.829 | 1.809 | **1.804** | 1.807 |
| 436M | 87.9B | 16 | 1168 | 528 | 2.20e-3 | 384 | 1.766 | 1.746 | **1.737** | 1.747 |
| 528M | 119.0B | 17 | 1264 | 560 | 2.02e-3 | 432 | 1.719 | 1.693 | **1.692** | 1.694 |

→ Full ≈ mHC(-lite) loss，但 Block 用更低 I/O；最大尺度 Full-Block gap 收窄到 0.001（与 Fig.4 M3 解读"Block 在最大尺度贴近 Full"一致）。

### Table 3 — 48B/3B MoE downstream（Kimi Linear 1.4T-tokens recipe）
| 任务 | Baseline | AttnRes | Δ |
|---|---|---|---|
| MMLU | 73.5 | 74.6 | +1.1 |
| MMLU-Pro | 52.2 | 52.2 | 0.0 |
| GPQA-Diamond | 36.9 | 44.4 | **+7.5** |
| BBH | 76.3 | 78.0 | +1.7 |
| ARC-Challenge | 64.6 | 65.7 | +1.1 |
| HellaSwag | 83.2 | 83.4 | +0.2 |
| TriviaQA | 69.9 | 71.8 | +1.9 |
| GSM8K | 81.7 | 82.4 | +0.7 |
| MGSM | 64.9 | 66.1 | +1.2 |
| Math | 53.5 | 57.1 | **+3.6** |
| CMath | 84.7 | 85.1 | +0.4 |
| HumanEval | 59.1 | 62.2 | **+3.1** |
| MBPP | 72.0 | 73.9 | +1.9 |
| CMMLU | 82.0 | 82.9 | +0.9 |
| C-Eval | 79.6 | 82.5 | +2.9 |

### Table 4 — 16 层 ablation（关键设计选择）
| Variant | Loss |
|---|---|
| Baseline (PreNorm) | 1.766 |
| DenseFormer [36] | 1.767 |
| mHC [59] | 1.747 |
| AttnRes Full | **1.737** |
| Full w/ input-dependent query | 1.731（更低但 d×d 投影 + 顺序解码，未采用） |
| Full w/ input-independent mixing | 1.749 |
| Full w/ sigmoid (vs softmax) | 1.741 |
| Full w/o RMSNorm | 1.743 |
| SWA (W=1+8) | 1.764 |
| Block (S=4) | 1.746 |
| Block w/ multihead (H=16) | 1.752 |
| Block w/o RMSNorm | 1.750 |

### Table 5（精简） — 残差变体统一分类（Weight × Source）
| 方法 | Weight 类型 | Source | semiseparable rank |
|---|---|---|---|
| Residual / ReZero / LayerScale / Highway / DeepNorm / KEEL | Fixed / Static / Dynamic | h_{l-1}（单态） | 1 |
| SiameseNorm / (m)HC / DDL | Fixed / Dynamic | m streams | m / d_v |
| DenseNet / DenseFormer | Static | [h_1,...,h_{l-1}] | dense (static) |
| MRLA | Dynamic (sigmoid, ~linear attn) | [h_1,...,h_{l-1}] | dense |
| **AttnRes Full** | **Dynamic (softmax)** | **[h_1,...,h_{l-1}]** | **rank-L dense** |
| **AttnRes Block** | Dynamic (softmax) | [b_0,...,b_{n-1}, b_n^i] | ∈ [N, N+S] |

## 与同类对比

- **vs Standard Residual / PreNorm（§2.1, §7）**：标准残差是 depth-wise 全 1 下三角 M（1-semiseparable, fixed），对应 Figure 9 第一象限的对偶视角。AttnRes 把它推广为 input-dependent softmax 加权的 dense M，且**保留对个别早期层输出的直接访问**（vs 单一压缩态 h_{l-1}），从机制上消除 PreNorm dilution——Figure 5(b)(c)（p.10, M3）给出 magnitude/gradient 双重可视化证据。
- **vs Highway [45] / ReZero [2] / LayerScale [50]（§2.1, §6.2, Table 5）**：这些都是单态 recurrence + element-wise 或 scalar gate。Highway 仍 1-semiseparable（只是 input-dependent），AttnRes 跳到 rank-L dense（Figure 9 对比 Highway↔Full AttnRes 两象限）。`w_l` 零初始化使 AttnRes 起点 ≈ Highway 的等权退化解，但 softmax 提供 competitive normalization。
- **vs DenseFormer [36] / DenseNet [17] / ELMo [38] / ANCRe [68]（§5.3, §7）**：同样跨层访问，但 DenseFormer 用**学到的、训练后固定的标量系数**——ablation 显示它甚至不优于 baseline（1.767 vs 1.766），证明 **input-dependent 加权是关键**。AttnRes 的 softmax 给出 content-dependent 选择。
- **vs (m)HC / Hyper-Connections [72,59]（§5.3, §6.2, Table 1, Table 4, Fig.9）**：(m)HC 维护 m 个并行 stream，`M_{i→l} = β_iᵀ A^{×}_{i+1→l} α_l`（Eq.10），是 **m-semiseparable = depth-wise linear attention with matrix state**（Figure 9 第二象限）。AttnRes 是 **depth-wise softmax attention**，dense rank-L（Figure 9 第三象限）。Table 1 显示 Block AttnRes 在 I/O 5.5d vs mHC 34d（m=4）下达到相当 loss（1.746 vs 1.747）。Table 2 显示 Full AttnRes 在多数尺度略优 mHC(-lite)，最大尺度持平。论文据此把 AttnRes 定位为 HC 家族的"softmax 升级版"，与线性→softmax attention 的序列侧过渡同构。
- **vs MRLA [10] / MUDDFormer [56]（§6.2, §7）**：MRLA 用 element-wise sigmoid（separable query-key product，更接近 linear attention 而非 softmax retrieval）；MUDDFormer 用小 MLP 生成 4-stream 位置相关权重。AttnRes 用单 d 维 pseudo-query + 真 softmax，机制更轻、选择更尖锐。
- **vs SWA（sliding window, §5.3）**：SWA(W=1+8) loss 1.764，几乎无改善——证明**远距离层的选择性访问比邻近多层的密集访问更重要**，是 AttnRes 全局 attention 的关键论据。
- **vs DDL [67]（§6.2）**：DDL 是序列侧 delta rule 在 depth 侧的对偶（erase-and-write matrix state），仍属 recurrence paradigm；AttnRes 直接跨层 attention，绕开 recurrence。
- **架构偏好分析（§5.4.1, Fig.7, p.12, M3）**：5×5 heatmap sweep 显示 AttnRes 在全部 25 个 (d_model/L_b, H/L_b) 配置上均优于 Baseline 0.019–0.063，且把最优 d_model/L_b 从 60（loss 1.847）移到 45（loss 1.802）——M3 解读为"AttnRes 偏好更窄更深的配置"，但作者明确这不直接等同于部署建议（更深模型推理延迟更高 [39]）。
- **学习模式分析（§5.4.2, Fig.8, p.13, M3）**：2×2 heatmap 可视化 α 权重——M3 解读强调 Block(N=8) 比 Full 的对角更尖锐、更果断，同时保留 locality、source 0（embedding）持续权重与 skip-connection 结构，说明 block 压缩起到隐式正则化作用。Figure 8 中"persistent weights on source 0"与公式 `b_0 = h_1`（embedding 恒为 source）对应——即 attention sink 现象（§6.2 Practicality 指出）。

## 跨论文关系（→ MOC 谱系）

- **残差/层间拓扑谱系**：[[hyper-connections]] 与 [[hc-manifold-constrained-hyper-connections]] 是 AttnRes 最直接的对照点。HC/mHC = depth-wise **linear** attention with m×m matrix state（m-semiseparable M，Figure 9 第二象限，对应 Eq.10 `M_{i→l}=β_iᵀ A^{×} α_l`），AttnRes = depth-wise **softmax** attention（dense rank-L M，Figure 9 第三象限）。论文 §6.2 明确把 HC 的 `M_{i→l}=β_iᵀ A^{×} α_l` 解读为 "α_l=query, β_i=key, A^{×}=depth-relative positional operator"，与 mHC-lite [64] 实证对照（Table 2 列）。Block AttnRes 在更低 per-layer I/O（5.5d vs mHC 34d）下匹配 mHC(-lite) loss——是 HC 谱系的 softmax 后继候选。
- **被生产模型采用**：[[kimi-k3-open-frontier-intelligence]] — AttnRes 集成进 Kimi Linear 48B/3B MoE（§5.2），与 Kimi Linear 的 hybrid KDA/MLA 架构 [69] 协同，是 K3 系列 depth-wise 拓扑的具体实现。
- **注意力架构谱系**：[[kimi-linear-an-expressive-efficient-attention-architecture]] — AttnRes 的 48B 实验直接搭建在 Kimi Linear 之上（KDA:MLA=3:1 interleaving），context extension 阶段借助 MLA 的 NoPE 特性免 YaRN；[[gated-delta-networks-improving-mamba2-with-delta-rule]] — GDN 是序列侧 delta-rule，与 DDL（depth 侧 delta 对偶）同源，AttnRes §6.2 用此对偶论证"linear→softmax"在 depth 维度的必要性。
- **归一化谱系**：[[root-mean-square-layer-normalization]] — RMSNorm 在两处关键使用：(1) ϕ 内 `exp(qᵀ·RMSNorm(k))` 防止大幅度层主导 softmax（§3.1，ablation 1.743 vs 1.737）；(2) AttnRes 自带的 per-layer RMSNorm 用于 block 表示。AttnRes 还从机制上**同时规避** PreNorm dilution 与 PostNorm 的梯度坍缩。
- **TTT / Fast Weight Programmers**：§6.1 用 TTT [46] 与 Fast Weight Programmers [43,32] 形式化 sequence-depth duality，把 `W_t = W_{t-1} − η∇ℓ`（Eq.9）当作 residual 一步梯度下降的序列侧同构。

## 局限与边界

1. **Full AttnRes 在当前硬件不可扩展（§1, §3.1, Conclusion）**：Full 形式必须保留全部 L 个层输出并在 pipeline stage 间传输，`O(Ld)` 内存 + 通信在大规模训练不可行——Block AttnRes 是工程妥协。作者明确"future interconnect improvements will make the full O(Ld) communication practical"，即 Full 的潜力被当前硬件限流。推理侧虽有两-phase 调度把 I/O 降到 `O((S+N)d)`（Appendix B 推导 Eq.17：Total I/O per layer = (S+N)d），但 Block AttnRes 仍是生产实际形态。
2. **Block 数 N 是工程固定值（§3.2, §5.3, Fig.6）**：经验取 N≈8，但这是"infra efficiency"权衡而非架构最优点。Figure 6（p.11, M3）sweep 显示 S=2/4/8 几乎无差（均 ~1.746），意味着在 N=L 与 N=8 之间存在未探索的 finer-grained 空间；N 固定后无法随模型深度自适应。
3. **Pseudo-query 的 input-independence 是设计妥协（§5.3）**：input-dependent query（从 h_l 投影）loss 更低（1.731 vs 1.737），但引入 d×d 投影 + 顺序解码，故默认用学习的 `w_l`。这是"为可并行 + 省 param 主动放弃部分表达力"——未来若硬件可承担顺序解码，是潜在改进点。
4. **sigmoid vs softmax 的解释是 post-hoc（§5.3）**：softmax 优于 sigmoid（1.737 vs 1.741）被归因于"competitive normalization 强迫尖锐选择"，但未给出理论证明；Figure 8（p.13, M3）的 Block 权重更尖锐可视化为这一解释提供了间接支持。
5. **Multihead depth aggregation 反而更差（§5.3）**：H=16 loss 1.752 vs Block 1.746，说明"当某层输出 relevant，则整体 relevant"——但这是单数据点的归纳，未必普适；不同任务/模态可能受益于 channel-grouped 选择。
6. **架构偏好深但不等于部署建议（§5.4.1, Fig.7）**：Figure 7（p.12, M3）sweep 显示 AttnRes 把最优 d_model/L_b 从 60 移到 45（更深更窄），但作者明确"this preference does not directly translate to a deployment recommendation"——deeper 模型推理延迟更高 [39]，架构选择需结合 inference cost。
7. **大模型 gain 模式偏向组合/推理任务（§5.2）**：增益集中在 GPQA(+7.5)、Math(+3.6)、HumanEval(+3.1)，而知识类（MMLU +1.1, TriviaQA +1.9）改善有限。若模型主要服务于知识检索，AttnRes 的边际收益相对小。
8. **下游基准未含长上下文 retrieval 评测**：虽然 32K context extension 已做，但 Table 3 仅 14 项短 benchmark，未报告 NIAH/long-context retrieval——AttnRes 改善深度信息流，理论上利好长上下文，但缺实证。
9. **zero-init `w_l` 的训练稳定性是经验法则（§5）**：作者"validated empirically"但未给消融数据；其他初始化方案未被探索。
10. **未解决 depth-wise attention 的 linear-complexity 表达（§6.1 末段）**：作者自列 future direction——"incorporating more expressive yet memory-efficient (e.g. linear-complexity) alternatives"。当前用 vanilla softmax 是因为 L<1000 可承受 `O(L²)`；若未来模型深度继续增长，需 depth-wise linear/linear-attention 变体。
