# IndexCache: Accelerating Sparse Attention via Cross-Layer Index Reuse — 技术点深读（DEEP 2026-08-18）

> 独立深读文件，extract_phase1 重跑不丢。全文/图/表/公式一体化分析。
> 论文：IndexCache: Accelerating Sparse Attention via Cross-Layer Index Reuse (Bai, Dong et al., Tsinghua / Z.ai) · arXiv:2603.12201v1 · 12 Mar 2026

## 核心问题

DeepSeek Sparse Attention (DSA) 把每层核心注意力从 O(L²) 降到 O(Lk)（k=2048 ≪ L），但负责 token 选择 的 **lightning indexer 自身仍保持 O(L²)**，且在 **N 层的每一层都独立运行一次**，总成本 O(NL²)。Profiling 30B DSA 模型（§1 引言图）显示 indexer 占总延迟比例随上下文单调上升：prefill 阶段从 10K 的 27% 涨到 200K 的 **81%**；decode 阶段从 27% 涨到 41%。**减少 indexer 计算是长上下文 DSA 推理加速的关键瓶颈**。

核心洞察（§2.2 + Appendix A，Figure 4 p.16）：indexer 选出的 top-k 集合在**相邻层高度相关**。M3 对 Figure 4 的解读要点：47×47 pairwise overlap heatmap（|T⁽ⁱ⁾∩T⁽ʲ⁾|/k, k=2048）显示沿对角线的明亮带 overlap **0.7–1.0**，并呈现清晰的层簇（layers 3-5, 6-8, 17-30, 31-36 等），仅少数"transition"层跨簇；左下/右上角（早期 vs 晚期层）overlap ≤ 0.4，说明早期与晚期层关注 fundamentally 不同的 token 子集。红色方框标注 greedy-searched 1/4 sharing blocks——它们与自然 overlap 簇**并不完全重合**（根因见 §局限）。即绝大多数 per-layer indexer 计算是冗余的。但既往跨层共享工作（TidalDecode / LessIsMore / OmniKV / DELTA / Kascade / HySparse）**都依赖 full attention 作为 oracle**，而 DSA **已彻底移除 full attention**——能否在 sparse attention 内部做跨层 index 复用、复用多大比例、能否训练适配，是本文要回答的问题。

**解决思路**：把 N 层二分划分为 **F (Full) 层**（保留 indexer，算自己的 top-k）和 **S (Shared) 层**（无 indexer，直接继承最近前驱 F 层的 top-k），推理时仅加一个条件分支（Figure 2 p.3，M3：对比 (a) 标准 DSA 每层跑 indexer 与 (b) IndexCache 加条件分支——F 层算并缓存索引到临时 `T_cache`，S 层直接复用 `T_cache` 跳过 indexer；`T_cache` 仅存当前索引张量、每 F 层覆写、无额外显存）。配套两条配置/优化路径：(1) training-free 的贪心层选择（直接最小化 LM loss，无需改权重）；(2) training-aware 的 multi-layer distillation loss（让保留的 indexer 学到服务多层的 consensus top-k）。30B DSA 上移除 **75%** indexer 计算、质量几乎无损，最高 1.82× prefill / 1.48× decode 加速；GLM-5 (744B) 上 1/2 retention 即 ~1.2× E2E speedup、质量无损（Figure 1 p.1）。

## 关键创新点

### 1. F/S 分层 + 单条件分支的跨层 index 复用（§3 + Figure 2 p.3）
- **机制**：用二值 pattern 串 `c = c₁…c_N`，`c_ℓ ∈ {F, S}`。F 层跑 `INDEXERℓ → Top-k → T_cache ← T(ℓ)`；S 层直接 `T(ℓ) ← T_cache`（来自最近 F 层 `f(ℓ)=max{j<ℓ: c_j=F}`）。第一层恒为 F 以 seed 初始 index。
- **图证（Figure 2 p.3，M3 要点）**：并排伪代码对比，(a) 标准 DSA 每层执行 `INDEXERℓ(X) → Top-k → SPARSEATTN → FFN`；(b) IndexCache 在循环内加一条红色条件分支，F 层多一行 `T_cache ← T(ℓ)`，S 层用注释 `▷reuse` 取 `T(ℓ) ← T_cache`。M3 强调 `T_cache` 是只存当前索引张量的临时 buffer、每 F 层覆写、**无额外 GPU 显存**（不超标准 DSA 已分配）。O(NL²) 的 indexer 总成本被砍掉 S 层占比，而 O(NLk) 的核心注意力不变。

### 2. Training-free：贪心层选择算法（§3.1.2 + Algorithm 1）
- **机制**：从全 F 出发，每步遍历当前所有 F 层（排除 layer 1），逐个 tentative flip 为 S，在**固定校准集**（B 个 mini-batch，batch=768, ctx=200K）上跑 forward 评估 LM loss，commit 使 loss 最小的那次 flip；共 K 步（如 K=3N/4 → 保留 1/4 indexer）。流水线并行 P 阶时把层切成 P 个 block（每 block 首层固定 F），每步内逐 block 搜索并 commit，forward pass 数约减 P×。
- **效果**：搜出的 pattern 在同保留比下**优于 uniform interleaving**（Table 2：1/4 uniform Long Avg 43.0 → +search 49.9，对比 Original DSA 50.2）。§3.1.2 右图 LM loss 曲线显示前 20 步是"easy"层、35 步后进入"critical"层，给出 index 重要性自然排序；结果跨校准集稳定，是模型内禀属性。
- **复杂度**：全程 all-F→all-S 需 N(N−1)/2 次 forward（47 层约 1081 次）。

### 3. 为什么 uniform interleaving 次优（§3.1.1）
- 不同层对 indexer 移除的敏感度差异极大，**early 和 transitional 区层**远比其他层关键；uniform（如 `FSSSFSSS…`）可能恰好移除关键 indexer 而保留冗余层 → 明显质量退化（§4.3 定量：1/2 uniform Long Avg 掉 2.8，1/4 掉 7.2）。这与 Figure 4 (p.16) 的"早期层因传播路径最长最脆弱"相吻合——M3 指出对角线外的早-晚层 overlap ≤ 0.4，early layers 的 perturbation 会 cascade 通过最长下游路径。

### 4. Training-aware：Multi-layer Distillation Loss（§3.2 + 公式 1-3 + Proposition 1）
- **机制**：标准 DSA 每 layer ℓ 的 indexer 只对自己层做 KL 蒸馏（原文 §2.1 式，未收录于 formulas.json，按 .txt 引用不渲染 `$$`：`L_I = Σ_t D_KL(p_t^(ℓ) ‖ q_t^(ℓ))`）。本文推广为：F 层 ℓ 的 indexer 要对其后续 m 个 S 层 ℓ+1…ℓ+m 的**聚合注意力分布**联合蒸馏，multi-layer distillation loss（公式 1，权威 LaTeX 源 formulas.json，`$$` 渲染）：

$$
\mathcal{L}^{\mathrm{I}}_{\mathrm{multi}} = \sum_{j=0}^{m} \frac{1}{m+1}\sum_{t} D_{\mathrm{KL}}\!\left( \mathbf{p}^{(\ell+j)}_{t} \,\big\|\, \mathbf{q}^{(\ell)}_t \right),
$$

- **梯度等价定理（Proposition 1）**：multi 与 avg 梯度等价，avg loss（公式 2，权威 LaTeX 源 formulas.json）：

$$
\mathcal{L}^{\mathrm{I}}_{\mathrm{avg}} = \sum_{t} D_{\mathrm{KL}}\!\left( \bar{\mathbf{p}}_{t} \,\big\|\, \mathbf{q}^{(\ell)}_t \right).
$$

  其中 $\bar{\mathbf{p}}_t = \sum_{j=0}^{m}\frac{1}{m+1}\mathbf{p}^{(\ell+j)}_t$ 为 served 层注意力分布的质心。证明（公式 3，权威 LaTeX 源 formulas.json，含 `&=`/`\notag` 对齐标记，包 `aligned` 环境渲染）：

$$
\begin{aligned}
\nabla_\theta \, \mathcal{L}^{\mathrm{I}}_{\mathrm{multi}} &= -\sum_{j=0}^{m} \frac{1}{m+1} \sum_{t} \nabla_\theta \sum_{s} \mathbf{p}^{(\ell+j)}_{t}(s) \log \mathbf{q}^{(\ell)}_t(s) \notag \\ &= -\sum_{t} \nabla_\theta \sum_{s} \underbrace{\Bigl(\textstyle\sum_{j=0}^{m} \frac{1}{m+1} \mathbf{p}^{(\ell+j)}_{t}(s)\Bigr)}_{\bar{\mathbf{p}}_{t}(s)} \log \mathbf{q}^{(\ell)}_t(s) \;=\; \nabla_\theta \, \mathcal{L}^{\mathrm{I}}_{\mathrm{avg}}.
\end{aligned}
$$

  关键步骤：$\mathbf{q}^{(\ell)}_t$ 是 DKL 中唯一参数依赖项，$\mathbf{p}$ 的熵在微分下消失（$\nabla_\theta D_{\mathrm{KL}}(\mathbf{p}\|\mathbf{q}^{(\ell)}_t) = -\nabla_\theta \sum_s \mathbf{p}(s)\log \mathbf{q}^{(\ell)}_t(s)$），故多层 KL 求和可合并为对质心 $\bar{\mathbf{p}}_t$ 的单层蒸馏。
- **双源校验**：上述三式 LaTeX 取自 `extraction/formulas.json`（权威源），与 `extraction/fulltext/...txt` §3.2 Eq.(1)(2)(3) + Proposition 1 证明段一致；M3 captions 未直接覆盖公式（M3 仅覆盖 Figure 1/2/3/4），故双源校验走 LaTeX↔fulltext .txt 两源，公式无训练记忆重写/补全。
- **结论**：**多层蒸馏 = 蒸馏到目标层注意力分布的质心 (centroid)**，indexer 学到跨所有 served 层的 consensus top-k。
- **实现取 multi 而非 avg**：avg 形式需同时前传 q^(ℓ) 和 p^(ℓ)，内存/运行时开销更大；multi 形式后续 S 层只需接收当前层预测 q^(ℓ)。
- **训练流程**：两阶段。warm-up 仅训 F 层 indexer 用 `L_I^multi`，其余参数冻结；sparse 阶段继续训 `L_I^multi`（仅 over 已选 top-k token 的 KL）+ LM loss 训其余参数。实验初始化自 GLM-4.7-Flash，1,000 步 dense warm-up + 4,000 步 sparse 训练（ctx=200K, SFT 数据）。
- **效果**：uniform 1/2 即达 Long Avg 51.6 超过 baseline 51.0（Table 3）；1/4 时 Long/G&R 均 within 0.4% of baseline。**training-free 中的 pattern 敏感性消失**——uniform 与 searched pattern 表现相当（甚至 uniform 略优）。去掉 cross-layer loss → Long Avg 51.6→49.8、AA-LCR 49.8→44.0，证明该 loss 实质有益。

### 5. 端到端推理加速随上下文单调放大（§4.2 + Table 1 + Figure 3 p.8）
- **机制/数据**：30B DSA 在 SGLang（dp attention, dp size=8, H100 node）上，1/4 配置在 200K 把 prefill 从 19.5s 降到 10.7s（**1.82×**），decode per-req 从 58 → 86 tok/s（**1.48×**），full-KV 从 197 → 297 tok/s（**1.51×**）；10K 时 prefill 仅 1.27×。
- **图证（Figure 3 p.8，M3 要点）**：三幅并排 grouped bar chart，共享 x 轴 (10K/60K/120K/200K) 与 y 轴 (Relative Speedup %, baseline=100%)，对比 DSA baseline / IndexCache 1/2 / IndexCache 1/4 三个配置。(a) Prefill time 在 200K 1/4 达 **182%**（即 1.82×），(b) decode per-request 200K 1/4 达 **148%**，(c) decode full throughput 200K 1/4 达 **151%**。M3 强调收益随 context length **monotonically scaling**——context 越长，indexer 在总延迟中占比越高（与 §1 引言图 81% 一致），消除冗余 indexer 的收益越大；1/4 retention 一致优于 1/2，说明更激进的 index 移除在长上下文更划算。

### 6. 负结果披露：similarity-based pattern search 失败（Appendix C + Table 5）
- **机制**：基于"复用 layer j 的 indexer 后 layer i 核心注意力输出的余弦相似度"构造 N×N 下三角矩阵 S，用 DP（公式 4-5）精确求解最大化总相似度的 pattern。
- **结果（Table 5）**：DP-similarity pattern 在下游任务上 **≈ uniform interleaving 水平**，相比 Original DSA (Avg 54.0) 同样显著退化（1/2 uniform 50.7、+similarity-search 49.8）。
- **根因**：层局部相似度是 **local metric**，无法捕捉"少量 critical token 错过"经剩余层 cascade 放大的端到端效应；S_{i,j}≈1 不代表质量无损。这与 Figure 4 (p.16) 中"greedy block ≠ overlap 簇"互为印证——overlap 是 aggregate metric，只数共享 token 数、不区分哪些 token 不同。Greedy loss-based 直接优化全局 LM loss，才能识别 critical 层。

### 7. 生产规模 scaling：GLM-5 (744B)（§4.5 + Table 4 + Figure 1 p.1）
- **数据**：training-free 在 GLM-5 上趋势一致；searched 1/2 略超 baseline（Long Avg 78.7 vs 78.4），1/4 searched 仍 within 0.4 pts（78.0 vs 78.4）。1/4 IndexCache 在 100K+ context 给出 ≥ 1.3× prefill & decode 加速。Artificial Analysis Index 全维评测几乎与原 GLM-5 重合。
- **图证（Figure 1 p.1，M3 要点）**：分组柱状图，10 个 benchmark 分 Long-Context (MRCR v2 71.1/72.3, Graph Walks 92.7/90.8, LongBench v2 64.5/66.0, RULER 97.7/97.3, AA-LCR 66.2/67.2) 与 General & Reasoning (HLE 30.4/30.4, HLE w/tools 50.4/50.3, SciCode 45.0/47.0, AIME25 95.9/95.9, IFBench 71.0/70.0) 两组，对比 GLM-5 vs GLM-5+IndexCache(1/2)，legend 标 "1.2× E2E Speedup"。M3 关键 takeaway：砍半 indexer（1 Full per 2 layers）在 retrieval-style 与 reasoning-style 任务上**精度损失可忽略**，端到端 ~1.2× 加速。SciCode 甚至 45.0→47.0 略升。

## 表格（原文结构化）

### Table 1 — 30B DSA 端到端推理性能（§4.2，对应 Figure 3 p.8）
| 指标 | Context | DSA baseline | IndexCache 1/2 | IndexCache 1/4 |
|---|---|---|---|---|
| Prefill time (s) ↓ | 10K | 0.57 | 0.47 | 0.45 |
| | 60K | 3.38 | 2.86 | 2.59 |
| | 120K | 8.57 | 6.57 | 5.66 |
| | 200K | 19.5 | 13.7 | **10.7 (1.82×)** |
| Decode per-req (tok/s) ↑ | 10K | 73.5 | 84.5 | 91.0 |
| | 60K | 67.0 | 80.0 | 89.5 |
| | 120K | 63.0 | 77.0 | 88.0 |
| | 200K | 58.0 | 73.0 | **86.0 (1.48×)** |
| Decode full-KV (tok/s/GPU) ↑ | 10K | 2700 | 3070 | 3310 |
| | 60K | 613 | 750 | 840 |
| | 120K | 341 | 431 | 498 |
| | 200K | 197 | 253 | **297 (1.51×)** |

加速随上下文增长；200K 时 1/4 配置 prefill 1.82×、decode per-req 1.48×、full-KV 1.51×——与 Figure 3 (p.8) 三幅子图的 182% / 148% / 151% 相对 speedup 完全对应。

### Table 2 — Training-free（§4.3），Long / G&R 聚合分
| Config | Long Avg | G&R Avg | MRCR | GW | LB2 | RULER | LCR | AIME | GPQA | LCB | IFB |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Original DSA | 50.2 | 74.6 | 24.5 | 49.6 | 45.5 | 87.9 | 43.6 | 91.0 | 77.6 | 71.4 | 58.4 |
| 1/2 Unif. | 47.4 | 74.3 | 22.0 | 46.6 | 46.0 | 83.6 | 38.6 | 92.2 | 76.4 | 69.7 | 59.0 |
| 1/2 +Search | 50.3 | 74.4 | 24.7 | 49.5 | 46.3 | 87.8 | 43.2 | 91.9 | 76.3 | 71.3 | 58.2 |
| 1/4 Unif. | 43.0 | 73.8 | 17.7 | 37.2 | 43.1 | 79.2 | 37.8 | 91.3 | 75.7 | 69.4 | 58.9 |
| 1/4 +Search | 49.9 | 74.9 | 25.1 | 47.4 | 45.7 | 87.6 | 43.8 | 92.6 | 78.6 | 70.0 | 58.3 |
| 1/8 Unif. | 35.3 | 70.0 | 12.9 | 33.1 | 37.7 | 68.8 | 24.0 | 89.1 | 74.1 | 58.7 | 58.0 |
| 1/8 +Search | 46.1 | 73.7 | 21.7 | 43.8 | 42.3 | 82.0 | 40.8 | 90.7 | 76.5 | 69.6 | 58.1 |

关键：searched pattern 在 1/2、1/4 几乎完全恢复 Long Avg 至 baseline 水平；1/4 searched 甚至在 AIME (92.6 vs 91.0) 和 GPQA (78.6 vs 77.6) 上略**超** baseline（移除冗余 indexer 起轻度正则作用）。1/8 时退化开始非可忽略。

### Table 3 — Training-aware（§4.4），uniform interleaving
| Config | Long Avg | G&R Avg | MRCR | GW | LB2 | RULER | LCR | AIME | GPQA | LCB | IFB |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Original DSA (shortened pipeline) | 51.0 | 74.2 | 24.7 | 49.1 | 46.9 | 87.3 | 47.0 | 88.8 | 79.4 | 70.5 | 57.9 |
| 1/2 Unif. IndexCache | 51.6 | 74.5 | 23.8 | 50.2 | 47.2 | 87.0 | 49.8 | 89.3 | 76.7 | 72.2 | 59.9 |
| 1/2 w/ searched pattern | 50.6 | 73.6 | 23.9 | 48.1 | 47.1 | 87.5 | 46.6 | 89.6 | 78.6 | 68.5 | 57.7 |
| 1/2 w/o cross-layer loss | 49.8 | 74.5 | 24.6 | 48.3 | 45.0 | 87.1 | 44.0 | 88.8 | 79.4 | 71.7 | 58.0 |
| 1/4 Unif. IndexCache | 50.6 | 74.1 | 23.7 | 48.1 | 46.9 | 86.1 | 48.4 | 89.3 | 78.0 | 70.5 | 58.7 |

关键：训练后 **uniform 1/2 甚至略超 baseline**；training-free 中的 pattern 敏感性消失（uniform ≈ searched）。去 cross-layer loss → AA-LCR 49.8→44.0，证明该 loss 实质有益。

### Table 4 — GLM-5 (744B, 40B active) Training-free（§4.5，对应 Figure 1 p.1）
| Config | Long Avg | MRCR v2 | GraphWalks | LongBench v2 | RULER | AA-LCR |
|---|---|---|---|---|---|---|
| Original DSA | 78.4 | 71.1 | 92.7 | 64.5 | 97.7 | 66.2 |
| 1/2 Unif. | 78.1 | 72.8 | 90.2 | 65.1 | 97.6 | 64.6 |
| 1/2 +Searched | 78.7 | 72.3 | 90.8 | 66.0 | 97.3 | 67.2 |
| 1/4 Unif. | 72.7 | 65.8 | 74.9 | 62.2 | 96.2 | 64.6 |
| 1/4 +Searched | 78.0 | 70.8 | 90.3 | 63.7 | 97.6 | 67.6 |

生产规模 744B 上趋势一致；searched 1/2 略超 baseline，1/4 searched 仍 within 0.4 pts。Figure 1 (p.1) 的 1/2 配置在 10 个 benchmark 上的柱状对比正是此表的视觉化呈现——M3 列出的逐 benchmark 数字（如 MRCR v2 71.1/72.3、AIME25 95.9/95.9、SciCode 45.0/47.0）与本表 + Artificial Analysis Index 全维评测一致。

### Appendix B — 搜出的 pattern（30B / GLM-5）
- 30B 1/2: `FSFSFSSSSFSFFFFSFFSSFFSFFFSSFFSSFSSSSFSFFFSFSSF`
- 30B 1/4: `FSFSFSSSSFSSSFSSFFSSFSSFSSSSFSSSFSSSSFSSSSSSSSS`
- 30B 1/8: `FSSSFSSSSSSSSFSSSFSSSSSFSSSSFSSSSSSSSFSSSSSSSSS`
- GLM-5 1/2: `FFSFSSSFSSFFFSSSFFFSFSSSSSSFFSFFSFFSSFFFFFFSFFFFFSFFSSSSSSFSFFFSFSSSFSFFSFFSSS`
- GLM-5 1/4: `FFSFSSSFSSFSFSSSSSSSFSSSSSSFSSSFSFSSSSFFFFFSSSFFSSSFSSSSSSSSFSSSFSSSSSSFSFSSSS`

### Appendix A — Figure 4 (p.16) 关键观察
47×47 heatmap，viridis colormap 0.0→1.0。相邻层 overlap 0.7–1.0；功能簇 layers 3-5, 6-8, 17-30, 31-36；overlap 跨簇边界快速衰减；早-晚层 corner overlap ≤ 0.4。红色方框为 greedy 1/4 sharing blocks，与自然簇**不完全重合**（overlap 是 aggregate metric，无法区分 critical token）。

## 与同类对比

- **vs TidalDecode / LessIsMore / OmniKV / DELTA / Kascade / HySparse**（§5.2）：这些跨层 top-k 复用方法**全部依赖 full attention anchor 层作为 oracle** 计算 exact top-k。IndexCache 的 oracle 是 DSA 的 **lightning indexer（远比 full O(L²) 便宜）**，且 DSA 已无 full attention 可用——本方法是首个**完全在 sparse attention 内部**做跨层 index 复用的工作。Figure 2 (p.3) 的 (a) vs (b) 对比正可视化这一差异：标准 DSA 已经没有 full attention，IndexCache 只在 sparse 内部加条件分支。此外 IndexCache 还提供系统化的配置优化（training-free greedy + training-aware multi-layer distillation），而前者多为固定 anchor 间隔或相似度 DP。
- **vs Kascade（Deshmukh et al., 2025）**：Kascade 用 DP over cross-layer similarity matrix 选 anchor，并指出 head-aware remapping 关键；但 anchor 仍是 full attention。IndexCache 的 Appendix C 负结果表明：即便是 sparse 版的相似度 DP 搜索也"≈ uniform interleaving"、无实质增益——local metric 无法预测 cascade 误差，必须用 end-to-end LM loss。这与 Figure 4 (p.16) 中 greedy blocks ≠ overlap 簇的观察互为印证。
- **vs cross-layer KV cache sharing（YOCO / MiniCache / SwiftKV / MLKV 等）**：方向正交——KV sharing 复用 key/value 张量省**内存**，IndexCache 复用 top-k **index**省**indexer 计算**。HySparse 同时做两件事但需 full attention 层。
- **vs 混合架构（gpt-oss / Gemma / Kimi Linear / Nemotron-H / Jamba）**：hybrid 用 sliding-window / linear / SSM 层替代部分二次层，从**结构**上减少二次层；IndexCache 不改架构，只**省 sparse attention 内部的 index 计算冗余**，与 hybrid 正交可叠加。
- **作者声明可推广**：虽实例化在 DSA，核心原则适用**任何非固定 pattern、含动态 token selection 步骤的 sparse attention**——如 MoBA（block-level）、NSA（native sparse）的 block-level selection 同样可跨层复用（§5.2 末）。

## 跨论文关系（→ MOC 谱系）

- **跨层稀疏 index 复用锚点（本文）**：确立"cross-layer index reuse within sparse attention"分支，与 full-attention-oracle 的 Kascade/HySparse 谱系并列，是 **DSA 原生的加速器**。
- **与 [[kimi-linear-an-expressive-efficient-attention-architecture]] 正交互补**：Kimi Linear 用 KDA(线性)+MLA(全注意力) 3:1 混合从**架构**上减少二次层；IndexCache 不改架构、在 sparse attention **内部**省 indexer 冗余。两者可叠加（若 Kimi Linear 含类似 DSA 的 dynamic selection 步骤）。
- **与 [[gated-delta-networks-improving-mamba2-with-delta-rule]] 同属高效注意力大谱系**：GDN 是 delta-rule 线性注意力改进，IndexCache 是 sparse attention 加速器；都为长上下文降复杂度，但路径不同（线性 vs 稀疏选择）。
- **与 [[a-survey-on-large-language-model-acceleration-based-on-kv-cache-management]]**：该 survey 把 IndexCache 归入 **cross-layer reuse** 分支；与 prefix-KV 复用（SGLang/vLLM 前缀共享）和 cross-node KV pool（Mooncake）三类并列——IndexCache 复用的是 **index 选择**而非 KV 张量，正交于后两者。
- **与 [[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]] / [[prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter]]**：Mooncake 做 cross-node KV pool 解耦 prefill/decode，Prefill-as-a-Service 跨数据中心调度 KVCache；IndexCache 是模型**推理层内**优化，与系统层解耦正交，可共存于 Mooncake 式 serving 架构之上。
- **与 [[sglang-efficient-execution-of-structured-language-model-programs]]**：本文实验在 **SGLang** 上 serve（dp attention, dp size=8, H100 node）——IndexCache 是 SGLang runtime 内的算法级加速，与 SGLang 的 RadixAttention 前缀共享是不同维度的优化。
- **与 [[cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion]] / [[kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference]]**：CacheBlend 复用 RAG 跨请求 KV；IndexCache 复用跨层 index。都属于"复用以省计算/内存"大类，但复用对象与作用维度不同。
- **生产谱系**：DeepSeek-V3.2 → GLM-5 都默认 sparse attention（DSA 类），作者预期 cross-layer index reuse 将成为 frontier LLM 高效推理管线的**标准组件**（§6）。Figure 1 (p.1) 的 GLM-5 实测正是这一谱系的 production-scale 验证。

## 局限与边界

- **方法绑定 DSA / dynamic-selection sparse attention**：依赖"每层有一个可被复用的 top-k index 输出"。对**固定 pattern** sparse（sliding window / sink / 纯 linear attention）不适用——后者无可复用的动态 index。对 MoBA/NSA 等 block-level selection 理论可推广但作者未实证。
- **1/8 retention 是退化拐点**：1/4 searched 仍可恢复质量，1/8 时 Long Avg 从 50.2 掉到 46.1（即使 searched），长上下文退化"non-negligible"——实用上界约在 75% indexer 移除。
- **training-free greedy 搜索成本**：N(N−1)/2 forward（47 层约 1081 次），需 pipeline 并行 P× 加速；对超大模型（744B GLM-5）仍是显著预算，作者只做了 training-free、training-aware 尚未上生产规模。
- **multi-layer distillation 的 m 由 pattern 决定**：uniform 下 m 是固定窗口，但非均匀 pattern 下每个 F 层 served 的 S 层数不同，loss 加权 `1/(m+1)` 是简单平均；更优加权（按层敏感度）未探索。
- **Proposition 1 仅在 KL(p‖q) 形式下成立**：梯度等价依赖 q 是唯一参数依赖项、p 熵微分消失。换其他蒸馏度量（如 JS、MSE over top-k mask）则等价性不保。
- **overlap 是 aggregate metric，不区分 token 重要性**（Figure 4 p.16 / Appendix A/C）：greedy block 与自然 overlap 簇不完全重合；早期层因传播路径最长最脆弱（M3：corner overlap ≤ 0.4）——本方法的 greedy search 恰好规避，但未给出"critical layer"的可解释形式化判据。
- **评测上下文上限 200K**：作者推测 >200K 加速更大但未实测；Figure 3 (p.8) 的 monotonic scaling 趋势外推到 >200K 仅是推断。decode 测评在 single-concurrency 与 full-KV 两设置，未涵盖中等并发混合负载。
- **GLM-5 结果为 preliminary**（Figure 1 p.1 / Table 4）：training-aware 尚未应用于 744B，作者表示"乐观"但未交付实证。
