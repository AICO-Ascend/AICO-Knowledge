# Conditional Memory via Scalable Lookup — 技术点深读（DEEP 2026-08-18）

<!-- 独立文件：本 deep note 由 subagent 撰写，存放于 extraction/deep/<slug>.md；与 extract_phase1 再生的 MD/MOC 解耦，可被 moc_relations.md 与 kb_query.py 引用。 -->

> 来源：DeepSeek-AI 与北京大学（Cheng 等，arXiv:2601.07372v2，12 Jul 2026）。代码：https://github.com/deepseek-ai/Engram。本文提出 **conditional memory** 作为 MoE conditional computation 之外的"第二条稀疏轴"，实例化为 Engram 模块（现代化 N-gram 哈希查表 + context-aware gating），并通过 Sparsity Allocation 的 U-shaped scaling law 指导配比，扩至 27B/40B 总参数规模。

## 核心问题

论文攻击的是一个机制级的低效：**标准 Transformer 没有原生的 knowledge lookup 原语，被迫用"计算"去模拟"检索"**（§1，Abstract）。

- 机制层面（§1，引 Table 3）：解析一个常见的多 token 实体（如 "Diana, Princess of Wales"），LLM 必须消耗多层 Attention + FFN 才能逐步组合出该实体的内部表征——Layer 1-2 仅识别 "Wales"，Layer 3 才得到 "Country in Europe"，Layer 4-5 才得到泛化的 "Princess of Wales"，Layer 6 才完整还原 "Diana, Princess of Wales (1961-1997)"。这一过程本质上是 **在运行时用算力重建一个本应是静态查表的 key-value 表**，浪费了宝贵的 sequential depth。
- 语言学动因（§1）：语言建模包含两类质不同的子任务——**compositional reasoning**（需要深层动态计算）与 **knowledge retrieval**（命名实体、公式化表达，局部、静态、高度刻板，正是经典 N-gram 模型擅长的）。
- 资源分配动因（§3.1）：MoE 通过 conditional computation 稀疏激活 expert 来扩容，但 `P_sparse = P_tot − P_act` 这部分"免费参数"目前只给了 routed experts（即"未选中 expert"），缺少把它分给"静态查表"的机制。

因此问题被精确化为 **Sparsity Allocation**：在固定 `P_tot` 与 `P_act`（iso-parameter、iso-FLOPs）下，如何在 MoE expert 容量与 Engram 嵌入查表之间分配 `P_sparse`？该问题之所以可解，关键在于 Engram 把存储与计算解耦——其寻址仅依赖输入 token（确定性 hash），与 MoE 依赖 hidden state 的动态路由在系统行为上正交，正如图示的系统实现所强调（Figure 2，p.6；M3 解读：训练阶段嵌入表跨 GPU 分片 + All-to-All 收集活跃行/分发梯度，使总容量随加速器线性扩展；推理阶段表常驻 host DRAM，利用确定性索引在前置 block 计算窗口内异步经 PCIe 预取，并按 N-gram Zipf 分布建立 HBM→Host DRAM→NVMe 多级缓存）。

## 关键创新点

1. **将 conditional memory 定义为独立稀疏轴，并以 Engram 实例化（§2）**
   - 机制：如图示架构（Figure 1，p.4）所示，Engram 在特定 layer 残差注入、保留标准 input/un-embedding 不变；模块分两个相位工作。**Retrieval**：对位置 `t` 抽取 suffix N-gram `g_{t,n}`，先经 tokenizer compression（§2.2 满射 `P: V→V'`，基于 NFKC+lowercasing 的规范化等价类，128k tokenizer 实际压缩 23.43%，见 Appendix C），再用 K-head multiplicative-XOR hash 映射到素数大小 `M_{n,k}` 的嵌入表 `E_{n,k}`，最终拼接所有 `e_{t,n,k}` 得到 `e_t ∈ R^{d_mem}`；权威 LaTeX（formulas.json，Eq. 1-2）：

$$
z_{t,n,k} \triangleq \phi_{n,k}(g_{t,n}), \quad \mathbf{e}_{t,n,k} = \mathbf{E}_{n,k}[z_{t,n,k}].
$$

$$
\mathbf{e}_t \triangleq \mathop{\Vert}_{n=2}^{N} \mathop{\Vert}_{k=1}^{K} \mathbf{e}_{t,n,k}.
$$

   一句话机制：`φ_{n,k}` 为 multiplicative-XOR hash 把压缩后的 N-gram 上下文映射到素数大小的嵌入表索引，再沿 N-gram 阶 `n` 与 head `k` 拼接成统一 memory 向量（§2.2，Eq. 1-2）。**Fusion**：把 `e_t` 当 Key/Value 源，当前 hidden state `h_t` 当 Query，经 RMSNorm 后算 scalar gate（Eq. 3-4）：

$$
\mathbf{k}_t = \mathbf{W}_K \mathbf{e}_t, \quad \mathbf{v}_t = \mathbf{W}_V \mathbf{e}_t
$$

$$
\alpha_t = \sigma\left( \frac{\text{RMSNorm}(\mathbf{h}_t)^\top \text{RMSNorm}(\mathbf{k}_t)}{\sqrt{d}} \right).
$$

   一句话机制：`h_t` 作 Query、检索到的 `e_t` 作 K/V 源，RMSNorm 后做 scaled dot-product 得到 sigmoid gate `α_t∈(0,1)`，门控输出 `ṽ_t = α_t·v_t`；当检索 memory 与上下文矛盾时 `α_t→0` 抑制噪声（§2.3，Eq. 3-4）。再经 kernel=4、dilation=最大 N-gram 阶的 depthwise causal conv + SiLU + residual（Eq. 5）：

$$
\mathbf{Y} = \text{SiLU}\left( \text{Conv1D}( \text{RMSNorm}(\tilde{\mathbf{V}}) ) \right) + \tilde{\mathbf{V}},
$$

   最后以 residual `H^(l) ← H^(l) + Y` 注入 backbone，随后才是标准 Attention 与 MoE。
   - 效果：gating 趋零时自动抑制哈希碰撞/多义噪声（§2.3）；case study（§6.5, Figure 7，p.18）显示 gate 在多 token 命名实体（"Alexander the Great"、"the Milky Way"）与公式化短语（"By the way"、"Princess of Wales"）、中文成语与历史实体（"四大发明"、"张仲景"）处一致激活——证明它确实识别了刻板语言依赖（M3 解读：因为 Engram 作用于 suffix N-gram，某 token 上的高激活意味着以该 token 结尾的短语被识别为可静态查表的 pattern；图中 mHC M=4 + 双 layer 注入共产生 8 个 gate scalar，仅展示与语义 pattern 最相关的分支）。

2. **U-shaped Sparsity Allocation scaling law（§3.1）**
   - 机制：定义分配比 `ρ ∈ [0,1]`，权威 LaTeX（formulas.json，Eq. 7）：

$$
P_{\mathrm{MoE}}^{(\mathrm{sparse })} = \rho\, P_{\mathrm{sparse}}, \qquad P_{\mathrm{Engram}} = (1-\rho)\, P_{\mathrm{sparse}}.
$$

   一句话机制：把"未激活参数预算" `P_sparse = P_tot − P_act` 在 MoE routed expert (`ρ` 份额) 与 Engram 嵌入 slot (`1−ρ` 份额) 之间切分；`ρ=1` 即纯 MoE，`ρ<1` 把腾出的 routed expert 容量转成 Engram 嵌入（§3.1，Eq. 7）。固定稀疏比 `P_tot/P_act ≈ 10`，在 `C=2e20`（`P_tot≈5.7B`, `P_act=568M`, baseline 106 experts）与 `C=6e20`（`P_tot≈9.9B`, `P_act=993M`, baseline 99 experts）两个量级下，仅调整 routed expert 数与 Engram slot 数构造不同 ρ。
   - 效果：Figure 3(left)（p.8）呈现一致的 U 形。在 10B 量级（`C=6e20`），validation loss 从 ρ=100% 的 1.7248 降至 ρ≈80% 最优点的 1.7109（Δ=0.0139）。最优点在两量级下都稳定在 **ρ≈75%-80%**，即把 20%-25% 的稀疏预算让给 Engram。ρ=1 时缺静态存储需靠深度重建；ρ→0 时失去 conditional computation 伤害动态推理——验证了两模块的结构互补性。
   - 反直觉点：ρ≈40% 时 Engram 模型已可与纯 MoE baseline 相当（5.7B 模型从 106 expert 减到 46；9.9B 模型从 99 减到 43），即便在大幅让出 expert 容量后仍不输。

3. **Infinite Memory Regime 的 power-law scaling（§3.2）**
   - 机制：固定 3B MoE backbone（`P_tot≈3B`, `P_act=568M`，训 100B tokens），单独扫 Engram slot 数 M 从 2.58×10^5 到 1.0×10^7（最多加约 13B 参数）。
   - 效果：Figure 3(right)（p.8）表现 **严格的 log-space 线性（幂律）**，意味着扩 slot 持续有收益且不增计算。同 slot 预算下 Engram 比 OverEncoding（直接平均进 vocab embedding，Huang et al. 2025a）解锁了更大的 scaling 潜力——这条曲线把"扩 slot"确立为一个可预测、可外推的容量旋钮。

4. **多分支架构整合与 FP8 融合（§2.4）**
   - 机制：默认 backbone 为 mHC（Manifold-Constrained Hyper-Connections, M=4, Xie et al. 2025）。Engram topology-agnostic 地接入：**单个嵌入表 + 单个 W_V 在 M 个分支间共享，M 个不同 W_K^(m) 实现分支特异 gating**，权威 LaTeX（formulas.json，Eq. 6）：

$$
\alpha_t^{(m)} = \sigma\left( \frac{\text{RMSNorm}(\mathbf{h}_t^{(m)})^\top \text{RMSNorm}(\mathbf{W}_K^{(m)} \mathbf{e}_t)}{\sqrt{d}} \right).
$$

   一句话机制：对第 m 个分支用其专属 `W_K^(m)` 与共享 `e_t` 计算分支特异性 gate `α_t^(m)`，再调制共享 value `u_t^(m) = α_t^(m)·(W_V e_t)`；从而 W_V 与 M 个 W_K^(m) 可融合为单个 dense FP8 matmul（§2.4，Eq. 6）。
   - 效果：最大化 GPU 算力利用率，同时保留分支特异性调制；ablation 证明去掉 multi-branch 融合是损失最大的几项之一（§6.2, Figure 5 markers，p.16）。

5. **27B/40B 实证：推理增益超过知识任务本身（§4.2, Table 1）**
   - 机制：Engram-27B 把 MoE-27B 的 routed expert 从 72 减到 55，腾出 5.7B 给 Engram（ρ=74.3%），插入 layer 2 与 15；激活参数严格 3.8B、训练 token 严格 262B。Engram-40B 同 backbone 同 P_act，仅扩 Engram 至 18.5B。
   - 效果（Engram-27B vs MoE-27B，iso-param/iso-FLOPs）：知识任务 MMLU +3.0（57.4→60.4）、MMLU-Pro +1.8（28.3→30.1）、CMMLU +4.0（57.9→61.9）。**更显著的是一般推理**：BBH +5.0（50.9→55.9）、ARC-Challenge +3.7（70.1→73.8）、DROP +3.3（55.7→59.0）。代码/数学：HumanEval +3.0（37.8→40.8）、MBPP +1.6、GSM8K +2.2（58.4→60.6）、MATH +2.4（28.3→30.7）。Validation loss 从 1.634 降到 1.622，Pile loss 1.960→1.950。
   - 关键解释（§6.1，Figure 4，p.13）：Engram 把"早期静态重建"从 backbone 卸载，相当于 **加深了有效深度**。LogitLens（Figure 4a）显示 Engram 各层 KL divergence 系统性低于 MoE baseline，尤其在早期 block 最明显，曲线下降更陡；CKA 软对齐（Figure 4b-c，权威 LaTeX Eq. 8-9，top-k=5）显示 Engram layer 5 对齐 MoE layer ~12（`a_j > j` 的 off-diagonal shift 在 Engram-27B/40B 上均成立），即 Engram 的浅层在功能上等价于 MoE 的深层。CKA 与 soft alignment index 的权威 LaTeX（formulas.json，Eq. 8-9）：

$$
\text{CKA}(K, L) = \frac{\text{HSIC}(K, L)}{\sqrt{\text{HSIC}(K, K)\text{HSIC}(L, L)}}
$$

$$
a_j = \frac{\sum_{i \in \mathcal{I}_j} S_{i,j} \cdot i}{\sum_{i \in \mathcal{I}_j} S_{i,j}}, \quad \text{where } \mathcal{I}_j = \mathop{\text{argtop}k}_{i} (S_{i,j}).
$$

   一句话机制：CKA 用 HSIC 度量两表示集合的独立性归一化相似度；`a_j` 是 Engram 层 j 相对 top-k 最相似 MoE 层的加权质心，作为"对应 MoE 有效深度"的鲁棒代理（§6.1.2，Eq. 8-9）。LaTeX↔M3 双源校验：M3 对 Figure 2/5/Table 4 的文本级解读与公式所定义的机制（确定性 hash 寻址、context-aware gating、ρ 分配）完全一致；M3 明确指出 Figure 2 的 prefetch-and-overlap 与 Zipf 多级缓存正源于 §2.5 描述的确定性寻址特性，公式 Eq. 1-2 的 `φ_{n,k}`（token-ID 函数）是该系统特性的数学根因。

6. **结构消融：layer 2 单层最优，layer 2+6 双层更优（§6.2, Figure 5，p.16）**
   - 机制：12-layer 3B MoE backbone（0.56B activated，训 100B tokens），1.6B Engram 预算，{2,3}-gram，参考配置插入 Layers 2&6 得 Val Loss = 1.768（vs baseline 1.808，Δ=0.04）。固定预算单层 sweep layer 1→12，再对参考配置做组件 ablation。
   - 效果：M3 解读 Figure 5（p.16）——橙色虚线为 3B MoE baseline 1.808；深蓝 "Layer Sweep" 曲线显示 **Layer 2 单层最优（1.770）**，越往深层越差，说明仅一轮 attention 已能为 gating 提供足够 contextualized `h_t`，又足够早以替换 backbone 底层局部聚合；但 **拆成两小模块放 Layers 2+6 更优（1.768）**，把"早期卸载静态 pattern"与"后期丰富 context gating"统一。组件 ablation markers（p.16）显示三组件损失最大：multi-branch 融合、context-aware gating、tokenizer compression；去 4-gram 与去 short conv 影响较小。
   - 系统协同：分层插入还顺带提供系统红利——更好地利用 §2.5 的多级存储层级。

7. **长上下文：把局部依赖让给查表，腾出 attention 容量给全局（§5, Table 2）**
   - 机制：DeepSeek-V3 风格 YaRN 上下文扩展（scale s=10, α=1, β=32, f=0.707），32k context，训 5000 步（30B tokens）。设置 iso-loss 对照（Engram-27B @46k 与 MoE-27B @50k 预训练 loss 相等）。
   - 效果：Iso-Loss 下 Multi-Query NIAH 97.0 vs 84.2、Variable Tracking 87.2 vs 77.0、FWE 98.6 vs 73.0、QA 37.5 vs 34.5；iso-FLOPs (50k) 下进一步全指标领先。即便用 82% 算力（41k）的 Engram-27B 仍在 LongPPL 平手、RULER 上反超 MoE baseline。

8. **infrastructure-aware efficiency：确定性寻址→host-memory offload 几乎零开销（§2.5, §6.4, Table 4，p.18）**
   - 机制：与 MoE 依赖 hidden state 动态路由不同，Engram 的 hash ID 仅由 input token 决定（数学根因见 Eq. 1 的 `φ_{n,k}(g_{t,n})`，`g_{t,n}` 仅依赖输入 token ID），前向之前完全已知 → inference 时把整个表常驻 host DRAM，异步经 PCIe 预取与前一 block 计算重叠（Figure 2(b)，p.6；M3 解读：前置 dense block 的计算强度提供了掩盖检索延迟的时间窗，且单步实际通信量随 *activated slot 数* 缩放而非表大小）；并利用 N-gram 的 Zipf 分布做多级缓存（HBM→DRAM→NVMe）。训练时用 All-to-All 跨 GPU 分片（Figure 2(a)，p.6；M3 解读：forward 收集活跃行、backward 分发梯度，容量随 GPU 数线性扩展）。M3 逐字转录 Table 4 caption："End-to-end Inference Throughput. We measure inference throughput with a 100B-parameter Engram layer entirely offloaded to host memory."
   - 效果：在 nano-vLLM 上把 100B 参数 Engram 层 offload 到 host（H800, 512 序列, len~Uniform(100,1024)），4B backbone 吞吐仅降 1.92%（9031.62→8858.28），8B backbone 仅降 2.79%（6315.52→6140.02）。这是保守基线（强制所有检索走 PCIe，未用 HBM 缓存热点），全优化后开销可忽略。LaTeX↔M3 双源校验：M3 给出的吞吐数字（4B 降 1.92%、8B 降 2.79%、峰值 2.8%）与 §6.4 正文/Table 4 完全一致；M3 指出"有效通信量随 activated slot 数缩放而非表大小"正是 Eq. 1-2 每位置仅取常数 K·(N-1) 个 slot 的直接推论。

## 表格（原文结构化）

### Table 1｜主预训练对比（关键列，§4）
| Benchmark (shots) | Dense-4B | MoE-27B | Engram-27B | Engram-40B |
|---|---|---|---|---|
| Total / Active params | 4.1B / 3.8B | 26.7B / 3.8B | 26.7B / 3.8B | 39.5B / 3.8B |
| Trained tokens | 262B | 262B | 262B | 262B |
| Experts (shared+routed, top-k) | - | 2+72, top-6 | 2+55, top-6 | 2+55, top-6 |
| Engram params | - | - | 5.7B | 18.5B |
| Pile (loss) | 2.091 | 1.960 | 1.950 | 1.942 |
| Validation (loss) | 1.768 | 1.634 | 1.622 | 1.610 |
| MMLU (5-shot) | 48.6 | 57.4 | 60.4 | 60.6 |
| MMLU-Pro (5-shot) | 21.1 | 28.3 | 30.1 | 31.3 |
| CMMLU (5-shot) | 47.9 | 57.9 | 61.9 | 63.4 |
| ARC-Challenge (25-shot) | 59.3 | 70.1 | 73.8 | 76.4 |
| BBH (3-shot) | 42.8 | 50.9 | 55.9 | 57.5 |
| DROP (1-shot, F1) | 41.6 | 55.7 | 59.0 | 60.7 |
| HumanEval (Pass@1) | 26.8 | 37.8 | 40.8 | 38.4 |
| GSM8K (8-shot) | 35.5 | 58.4 | 60.6 | 62.6 |
| MATH (4-shot) | 15.2 | 28.3 | 30.7 | 30.6 |
| TriviaQA (5-shot, EM) | 33.0 | 48.8 | 50.7 | 51.8 |

注意 Engram-40B 在 HumanEval（38.4 < 40.8）、MATH（30.6 ≈ 30.7）等未严格优于 Engram-27B，作者归因于 under-training——训练末期 loss gap 仍在扩大（§4.2）。

### Table 2｜长上下文（§5）
| Model (step, loss) | LongPPL-PPL↓ | NIAH S | MK | MV | MQ | VT | CWE | FWE | QA |
|---|---|---|---|---|---|---|---|---|---|
| MoE-27B (50k, 1.63) | 14.16 | 100.0 | 88.0 | 92.7 | 84.2 | 77.0 | 4.5 | 73.0 | 34.5 |
| Engram-27B (41k, 1.66) | 14.26 | 99.6 | 88.3 | 93.0 | 89.5 | 83.2 | 3.8 | 99.6 | 44.0 |
| Engram-27B (46k, 1.63) Iso-Loss | 13.59 | 97.6 | 89.0 | 95.5 | **97.0** | **87.2** | 4.3 | 98.6 | 37.5 |
| Engram-27B (50k, 1.62) Iso-FLOPs | **13.41** | 99.3 | 89.3 | 96.5 | **97.0** | **89.0** | 5.9 | 99.3 | 40.5 |

### Table 4｜推理吞吐（100B Engram offload，§6.4，p.18；M3 逐字转录 caption）
> **Table 4 | End-to-end Inference Throughput.** We measure inference throughput with a 100B-parameter Engram layer entirely offloaded to host memory.

| Backbone | Config | Throughput (tok/s) | 下降 |
|---|---|---|---|
| 4B-Dense | Baseline | 9,031.62 | — |
| 4B-Dense | +100B Engram (CPU Offload) | 8,858.28 | 1.92% |
| 8B-Dense | Baseline | 6,315.52 | — |
| 8B-Dense | +100B Engram (CPU Offload) | 6,140.02 | 2.79% |

### Table 3｜实体解析示例（§6.1，reproduced from Ghandeharioun et al. 2024）
| Layer | Latent State Translation（"Wales" token，PatchScope） | 解释 |
|---|---|---|
| 1-2 | Country in the United Kingdom | Wales |
| 3 | Country in Europe | Wales |
| 4 | Title held by female sovereigns... | Princess of Wales（unspecific） |
| 5 | Title given to the wife of the Prince of Wales | Princess of Wales（unspecific） |
| 6 | Diana, Princess of Wales (1961-1997), first wife of Prince Charles... | Diana, Princess of Wales |

### Appendix Table 5｜Engram-27B 关键超参
| 项 | 值 |
|---|---|
| Layers / dim / heads | 30 / 2560 / 32 (MLA) |
| Engram layers | [2, 15] |
| Engram N-gram orders | [2, 3] |
| Engram num head K | 8 |
| Engram dim `d_mem` | 1280 |
| Engram vocab size (27B/40B) | 2,262,400 / 7,239,680 |
| Embedding optimizer | Adam (lr ×5, weight decay 0) |
| Conv zero-init | True |
| Backbone optimizer | Muon |
| Tokenizer compression ratio | 23.43% |

## 与同类对比

- **vs OverEncoding (Huang et al. 2025a)**：OverEncoding 把 hash N-gram 嵌入直接平均进 vocab embedding。论文 §3.2 同 slot 预算下 Engram 解锁更大 scaling 潜力（Figure 3 right）；§7 指出 OverEncoding 在 sparse MoE backbone 上即便非 iso-param 也"无有意义提升"。机制上 OverEncoding 必须放在 Layer 0，**串行化内存访问与计算**；Engram 放深层 layer 实现 comm-comp overlap（Figure 2，p.6）。
- **vs SCONE (Yu et al. 2025)**：SCONE 面向 inference，带额外 f-gram 模块并增加训练 FLOPs，**破坏 iso-compute 约束**，故未纳入主对比；Engram 严格 iso-FLOPs。
- **vs N-Grammer (Roy et al. 2022)** / **SuperBPE (Liu et al. 2025a)** / **BLT (Pagnoni et al. 2025)**：都把 N-gram 嵌入注入表示空间，但都放在输入层；Engram 区别在于 (i) 深层插入 + context-aware gating；(ii) 把它当作 first-class 建模原语并与 MoE 做 Sparsity Allocation 联合优化。
- **vs parametric memory networks (PKM, PEER, UltraMem, Memory+)**：这些用稀疏 key-value store 直接挂在 layer，依赖 query-dependent 路由（动态、需运行时 hidden state 决定寻址）；Engram 寻址是 deterministic token-ID 函数（Eq. 1 的 `φ_{n,k}`），天然支持 prefetch，这是它独有的系统优势（§2.5，Figure 2 p.6）。
- **vs non-parametric retrieval (RETRO, REALM, CoG, PlugLM)**：外部 KV store 可编辑可扩展，但检索是运行时动态；Engram 是 in-model 静态查表，无需检索器、无 retrieval latency。
- **vs MoE (DeepSeekMoE)**：MoE 是 conditional computation 轴，用动态路由稀疏激活 expert 处理动态逻辑；Engram 是 conditional memory 轴，用确定性 hash 查表取静态嵌入。两者结构互补——纯 MoE 浪费深度重建静态知识，纯 Engram 失去动态推理能力，U 形配比给出最优分工。

## 跨论文关系（→ MOC 谱系）

本论文确立的"第二稀疏轴"概念，与现有 KB 中多条谱系交汇：

- [[deepseek-v3-technical-report]] — Engram 直接复用 DeepSeek-V3 的 tokenizer（128k vocab）、MLA 注意力、YaRN 长上下文扩展（s=10/α=1/β=32/f=0.707）、Loss-Free load balancing；并把 MoE-V3 视为 conditional computation 轴的代表，正是 Engram 要"互补"的对象。在 MOC 中应置于 **DeepSeek 系稀疏架构** 子谱系下，作为 V3 之外的并列演进支线。
- [[scalable-training-of-mixture-of-experts-models-with-megatron-core]] — Engram 训练侧用 All-to-All 跨 GPU 分片嵌入表（§2.5, Figure 2a p.6），与 MoE Expert Parallel 同源，可放在 **MoE 训练系统** 谱系下作为"另一种可分片稀疏参数"。
- [[a-survey-on-large-language-model-acceleration-based-on-kv-cache-management]] — Engram 把"局部依赖让给查表 → 腾出 attention 容量给全局上下文"（Multi-Query NIAH 84.2→97.0），是从 **架构侧** 间接缓解 KV/attention 压力的正交思路，应在 KV-cache 综述的 **架构性注意力容量优化** 小节并列。
- [[gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints]] — GQA/MQA/MLA 是 **KV 结构性压缩**（降低每 token KV 体积）；Engram 是 **attention 容量再分配**（让 attention 不再做静态重建）。两者方向不同但同属"重新分配 attention 预算"的家族。
- [[a-survey-of-large-language-models]] — LLM 综述定位：Engram 代表 conditional memory 这条"非 MoE 稀疏轴"，可作为综述中稀疏化分类法的新增条目。
- [[hyper-connections]] / [[attention-residuals]]（若存在）— Engram 默认 backbone 即 mHC（Manifold-constrained Hyper-Connections, M=4）；其多分支融合（共享 W_V + M 个 W_K）正是建立在 hyper-connection 拓扑之上的。`[[hyper-connections]]` 应作为直接前置依赖；`[[attention-residuals]]` 若涉残差/注意力容量再分配议题则相关。

## 局限与边界

- **U 形最优点的尺度外推未验证**：ρ≈75%-80% 的最优点在 5.7B/9.9B 两量级稳定，但作者明确只在"examined scales (under fixed sparsity)"内成立（§3.1）；千亿级或不同稀疏比下是否漂移未知。
- **Engram-40B 未严格 dominate 27B**：HumanEval 38.4 < 40.8、MATH 30.6 ≈ 30.7 等。作者归因 under-training（loss gap 仍在扩大），但 18.5B 嵌入在 262B token 下是否充分收敛未证实。
- **哈希碰撞未显式建模**：多 head hash 只"缓解"碰撞（§2.2），gating 是软抑制而非消除；高阶 N-gram 或更大表下碰撞率对质量的影响未量化。
- **Tokenizer compression 是启发式**：NFKC+lowercasing 等价类对大小写/重音敏感的任务（如代码区分大小写、专有名词大小写）可能损失信息；论文未报告此类细粒度下游影响。
- **Offload 实验在 dense backbone 上**：Table 4（p.18）的 100B offload 测的是 Dense-4B/8B，**未在 MoE backbone 上测**（作者解释是为避开 Expert Parallel 通信混淆）；真实 MoE+Engram 联合部署的端到端开销未给出。
- **Post-hoc ablation 有训练-推理不一致**（§6.3，Figure 6）：直接 inference 时关掉 Engram 输出去测功能贡献会引入噪声，故只对 Factual（保留 29-44%，TriviaQA 29%）与 Reading（保留 81-93%，C3 93%）两极做高置信结论，中间任务（CCPM、ARC、BBH 等）的归因仅供参考。
- **未解决动态知识更新**：Engram 是 in-model 静态表，知识更新仍需重训或微调嵌入；与 non-parametric retrieval（RETRO/PlugLM）相比牺牲了可编辑性。
- **placement 的 modeling-system trade-off 无解析解**：layer 2/15 是经验选择（§6.2, Figure 5 p.16 显示 layer 2 单层最优 1.770、layer 2+6 双层更优 1.768），但更深/更浅在不同规模下的最优解需重扫，论文未给可迁移公式。
- **仅英文+中文验证**：gating case study（§6.5, Figure 7 p.18）覆盖英中，但其他语言/脚本（agglutinative、low-resource）下 N-gram 静态性假设是否成立未验证。
