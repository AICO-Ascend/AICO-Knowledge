# Gated DeltaNet — 全要素深读（DEEP 2026-08-18, rewritten）
> 独立文件，extract_phase1 重跑不丢。文本/图/表/公式一体化分析。
> 论文：Gated Delta Networks: Improving Mamba2 with Delta Rule · arXiv:2412.06464v3 (2025-03-06, ICLR 2025)
> 作者：Songlin Yang (MIT CSAIL) / Jan Kautz, Ali Hatamizadeh (NVIDIA)。代码 https://github.com/NVlabs/GatedDeltaNet

## 核心问题

Linear Transformers（含 Mamba2、GLA 等）以矩阵态 linear RNN 形式把 softmax attention 改为线性 kernel，显著降低推理显存并支持并行训练，但在 **in-context retrieval 与 long-context 任务上仍弱于 Transformer**（§1）。其根因在 §1 指出：linear attention 本质是 outer-product key-value 联想记忆（tensor product representation, Smolensky 1990），可正交存储的 KV 对数受 head dimension 上界约束，序列长度一旦超过 d 即出现"memory collision"，破坏精确检索（Schlag et al. 2021）。

两条既有改进路径各有短板（§1）：

1. **Mamba2 的 gated update rule** `St = αt St-1 + vt kt^T`（αt∈(0,1) 标量衰减，§2.1）：能快速遗忘，但 αt 对 *所有* KV 关联按同一比率均匀衰减，无法定向擦除某个特定 KV——"if the model needs to forget a specific key-value association, all key-value associations are equally forgotten, making the process less targeted and efficient"（§1）。
2. **DeltaNet 的 delta rule**（Widrow 1960; Schlag 2021; Yang 2024b）`St = St-1(I − βt kt kt^T) + βt vt kt^T`（§2.2）：以 generalized Householder 转移矩阵 (I − βt kt kt^T) 选择性软替换当前 key 对应的旧 value，in-context associative recall 强，但一次只改一个 KV 对，**缺乏快速清空机制**，context switch 时旧信息难以及时清除，导致真实任务表现平庸（Yang 2024b）。

论文核心动机：上述两机制是 **互补的**——gating 擅长 rapid memory erasure，delta rule 擅长 targeted update。二者合流即得本文 gated delta rule。Fig.1（M3 解读）所绘的 Gated DeltaNet block 把 α（衰减门）与 β（delta 写入强度）作为并列的两条 linear-projection 分支同时驱动状态更新，正是这一"互补合流"动机在结构层面的具象化；该图同时标出最终性能坐标（Wiki ppl 16.42、zero-shot avg 55.32、H2 混合 ppl 15.91），把"动机→block→结果"串成单一图示。

## 关键创新点

1. **Gated delta rule（Eq.10, §3.1）** —— 核心机制
   `St = St-1 ( αt (I − βt kt kt^T) ) + βt vt kt^T`
   数据相关门控 αt∈(0,1) 控制状态衰减。统一优势：
   - αt→0 时退化为快速清空（gating 优势）。
   - αt→1 时退化为纯 delta rule（定向更新优势）。
   中间值则同时实现"遗忘 + 定向写入"。结构上即把 Mamba2 的对角转移 αt I 升级为 generalized Householder 矩阵 αt(I − βt kt kt^T)，兼顾遗忘幅度与方向性。Fig.1（M3 解读）的 block 设计把 α、β 画为仅经 linear projection 的两条独立分支（区别于 q/k 的 linear+shortconv+SiLU+L2norm 与 v 的 linear+shortconv+SiLU），与 Eq.10 中 α、β 各司其职（α 管状态衰减、β 管 delta 写入强度）的数学分工严格对应。

2. **Online-learning 视角的形式化（Table 1, §3.1）** —— 用 Liu et al. 2024 的在线学习框架解释
   - LA 目标 `‖St − St-1‖²_F − 2⟨St kt, vt⟩` → Hebbian 更新。
   - Mamba2 在正则项前置自适应缩放 αt：`‖St − αt St-1‖²_F` → 允许 St 偏离 St-1，提供 selective forgetting。
   - DeltaNet 把损失换成 delta regression `−2⟨St kt, βt(vt − St-1 kt)⟩`（一步显式 SGD）。
   - **Gated DeltaNet 同时在前正则项与回归项内引入 αt**：`‖St − αt St-1‖²_F − 2⟨St kt, βt(vt − αt St-1 kt)⟩`，相当于在 SGD 上加 adaptive weight decay。注：Longhorn（Liu 2024）用 implicit online learning 推出近似 delta rule 的闭式全局最优，GDN 则用一步显式梯度下降优化同目标（§3.1 脚注 3）。

3. **Test-time training / fast weight 视角（§3.1）** —— 把 S 解释为 fast weight，delta rule 是对 `L(St)=½‖St kt − vt‖²` 的 SGD：`St+1 = St − βt ∇L = St(I − βt kt kt^T) + βt vt kt^T`，βt 为 adaptive learning rate，αt 为 adaptive weight decay（Krogh & Hertz 1991）。与 Titans（Behrouz 2024）的 weight-decay 思路同期呼应。

4. **S-NIAH 案例研究（Table 2, §3.2）的三大观察**（1.3B 模型，RULER）—— 直接验证"互补性"
   - *Decay hurts retention*：S-NIAH-1（repeated synthetic，测长期记忆保持）DeltaNet 接近满分；Mamba2 在 >2K 时显著退化；GDN 退化较轻（4K 91.4 / 8K 91.8，vs Mamba2 65.4/30.4）——delta rule 帮助保持。
   - *Gating facilitates filtering*：S-NIAH-2/3（真实文本上下文，测内存管理）DeltaNet 在长序列因无 clearance 而崩溃（S-NIAH-2 4K 仅 18.6，8K 14.4）；Mamba2/GDN 靠 gating 过滤无关信息维持表现——gating 帮助清除。
   - *Delta rule helps memorization*：S-NIAH-3 UUID needle，Mamba2 急剧退化（4K 4.6），GDN 表现更优（4K 27.6 / 2K 84.2）。
   这三条观察与 Eq.10 的两个极限情形（αt→1 退化为 DeltaNet 保 retention、αt→0 退化为快速清空保 filtering）在机理上一一对应，构成"公式 ↔ 表格"的闭环验证。

5. **硬件高效 chunkwise 训练算法（§3.3, Appendix A）** —— 工程核心贡献
   - 部分展开 Eq.10 得 `Sr[t] = S[t]·Fr[t] + Gr[t]`，其中 Fr[t] = γr[t]·Pr[t] 即 Mamba2 风格衰减后的 Householder 累积积，Gr[t] 为带衰减的增量。
   - 把 Yang 2024b 的 WY 表示（Bischof & Loan 1985）扩展到含 αt：`Pr[t] = I − Σ wi[t] ki[t]^T`，`wr = βr (kr − Σ wi (ki^T kr))`；Gr[t] = Σ (γr/γi) ũi ki^T，`ũr = βr (vr − Σ ũi (γr/γi ki^T kr))`（§3.3, 附录 A 数学归纳法证明）。
   - UT transform（Joffrain 2006）给出矩阵形式 `Ũ[t] = [I + strictLower(diag(β) (Γ⊙ KK^T))]^−1 diag(β) V`，全部转化为 matmul，可上 tensor core。
   - 最终 chunkwise 更新（§3.3）：`S[t+1] = →S[t] + (Ũ − ←W S[t]^T)^T →K`，`O[t] = ←Q S[t]^T + (QK^T ⊙ M)(Ũ − ←W S[t]^T)`，箭头记号定义见 Eq.2（←q=γr q 衰减到 chunk 首位置；→k=γ^C/γr k 衰减到末位置；→S=γ^C S 衰减整 chunk）。
   - 关键工程结论（§4 throughput + Fig.3 验证）：gated delta rule 相对纯 delta rule **只引入边际开销**。Fig.3（M3 解读）的 1.3B/H100 吞吐曲线显示 Gated DeltaNet 与 DeltaNet 在 2K×16→16K×2 各配置下基本重合（约 38–50 K t/s 区间），二者仅比 Mamba2 慢 2–3K t/s——正是"更 expressive 的 generalized Householder 转移矩阵"带来的可测量但很小的代价；而 Transformer++ 虽在 2K 短窗因 Flash-Attention-2 冲到约 55 K t/s，却随序列增长陡降至约 27 K t/s，GDN 全程平直，体现线性 scaling。

6. **Block 设计与混合架构（§3.4, Fig.1）**
   - Token mixer block：沿用 Llama 宏观结构（mixer + SwiGLU MLP 堆叠），self-attention 替换为 gated delta rule。Fig.1（M3 解读）的 block 设计图细化：q/k 路径 = linear proj + short conv + SiLU + L2 norm；v 路径 = linear proj + short conv + SiLU；α、β 仅 linear proj；输出 norm + gating（SiLU）+ output proj。α 复用 Mamba2 的参数化（§3.4 脚注 4）。该 block 的每条支路在 Table S.1 ablation（400M/15B）中都有对应消融：去 short conv 使 Avg-PPL 27.35→28.95、去 output gate→29.12、去 α（即 naive Delta Rule）→30.87，定量印证 Fig.1 所画各支路的必要性。
   - **H1 = GDN + SWA**（类 Griffin/Samba）；**H2 = Mamba2 + GDN + SWA**（三路交错）。Fig.1（M3 解读）把 H1/H2 的层叠模式（H1: GDN-MLP-SWA-MLP；H2: Mamba2-MLP-GDN-MLP-SWA-MLP）与 standalone GDN 并排画出。Fig.3 显示 H1/H2 因 SWA 局部并行而吞吐高于 standalone GDN（约 50–54 K t/s，且 H1 在短序列也维持高吞吐，无 DeltaNet 短序列吞吐短板）；Table S.2 进一步给出 H2 内部排列顺序的最优选为 Mamba2+GDN+SWA（Avg-PPL 23.54 / Avg-Acc 48.73），与 Fig.1 所画 H2 的层序一致。

## 表格（原文结构化）

### Table 1（§3.1）— Linear RNN 在线学习目标与闭式更新对比
| 方法 | Online Learning Objective | Online Update |
|---|---|---|
| LA | ‖St − St-1‖²_F − 2⟨St kt, vt⟩ | St = St-1 + vt kt^T |
| Mamba2 | ‖St − αt St-1‖²_F − 2⟨St kt, vt⟩ | St = αt St-1 + vt kt^T |
| Longhorn | ‖St − St-1‖²_F − βt‖St kt − vt‖² | St = St-1(I − ɛt kt kt^T) + ɛt vt kt^T，ɛt = βt/(1+βt k^T k) |
| DeltaNet | ‖St − St-1‖²_F − 2⟨St kt, βt(vt − St-1 kt)⟩ | St = St-1(I − βt kt kt^T) + βt vt kt^T |
| **Gated DeltaNet** | ‖St − αt St-1‖²_F − 2⟨St kt, βt(vt − αt St-1 kt)⟩ | St = St-1(αt(I − βt kt kt^T)) + βt vt kt^T |

### Table 2（§3.2）— S-NIAH 1.3B zero-shot 准确率
| Model | S-NIAH-1 (passkey) 1K/2K/4K/8K | S-NIAH-2 (number) 1K/2K/4K/8K | S-NIAH-3 (uuid) 1K/2K/4K |
|---|---|---|---|
| DeltaNet | 97.4 / 96.8 / 99.0 / 98.8 | 98.4 / 45.6 / 18.6 / 14.4 | 85.2 / 47.0 / 22.4 |
| Mamba2 | 99.2 / 98.8 / 65.4 / 30.4 | 99.4 / 98.8 / 56.2 / 17.0 | 64.4 / 47.6 / 4.6 |
| **Gated DeltaNet** | 98.4 / 88.4 / 91.4 / 91.8 | 100.0 / 99.8 / 92.2 / 29.6 | 86.6 / 84.2 / 27.6 |

### Table 3（§4）— 语言建模 ppl + commonsense zero-shot（1.3B / 100B tokens FineWeb-Edu）
| Model | Wiki ppl↓ | LMB ppl↓ | LMB acc↑ | PIQA | Hella. | Wino. | ARC-e | ARC-c | SIQA | BoolQ | Avg↑ |
|---|---|---|---|---|---|---|---|---|---|---|---|
| RetNet | 19.08 | 17.27 | 40.52 | 70.07 | 49.16 | 54.14 | 67.34 | 33.78 | 40.78 | 60.39 | 52.02 |
| HGRN2 | 19.10 | 17.69 | 39.54 | 70.45 | 49.53 | 52.80 | 69.40 | 35.32 | 40.63 | 56.66 | 51.79 |
| Mamba | 17.92 | 15.06 | 43.98 | 71.32 | 52.91 | 52.95 | 69.52 | 35.40 | 37.76 | 61.13 | 53.12 |
| Mamba2 | 16.56 | 12.56 | 45.66 | 71.87 | 55.67 | 55.24 | 72.47 | 37.88 | 40.20 | 60.13 | 54.89 |
| DeltaNet | 17.71 | 16.88 | 42.46 | 70.72 | 50.93 | 53.35 | 68.47 | 35.66 | 40.22 | 55.29 | 52.14 |
| **Gated DeltaNet** | **16.42** | **12.17** | 46.65 | 72.25 | 55.76 | 57.45 | 71.21 | 38.39 | 40.63 | 60.24 | **55.32** |
| Transformer++ | 18.53 | 18.32 | 42.60 | 70.02 | 50.23 | 53.51 | 68.83 | 35.10 | 40.66 | 57.09 | 52.25 |
| Samba | 16.13 | 13.29 | 44.94 | 70.94 | 53.42 | 55.56 | 68.81 | 36.17 | 39.96 | 62.11 | 54.00 |
| **GDN-H1** | 16.07 | 12.12 | 47.73 | 72.57 | 56.53 | 58.40 | 71.75 | 40.10 | 41.40 | 63.21 | **56.40** |
| **GDN-H2** | **15.91** | 12.55 | 48.76 | 72.19 | 56.88 | 57.77 | 71.33 | 39.07 | 41.91 | 61.55 | 56.18 |

注：Fig.1（M3 解读）所标的 Wiki ppl 16.42 / zero-shot avg 55.32 / H2 ppl 15.91 即对应本表 GDN 与 GDN-H2 两行，图与表数字一致。

### Table 4（§4）— In-context retrieval（输入截断到 2K，Cloze Completion）
| Model | SWDE | SQuAD | FDA | TQA | NQ | Drop | Avg |
|---|---|---|---|---|---|---|---|
| RetNet | 14.0 | 28.5 | 7.0 | 54.4 | 16.2 | 17.3 | 22.9 |
| HGRN2 | 8.3 | 25.3 | 4.8 | 51.2 | 14.2 | 16.9 | 20.1 |
| Mamba | 9.8 | 25.8 | 3.7 | 54.3 | 14.9 | 17.4 | 21.0 |
| Mamba2 | 19.1 | 33.6 | 25.3 | 61.0 | 20.8 | 19.2 | 29.8 |
| DeltaNet | 17.9 | 30.9 | 18.4 | 53.9 | 17.3 | 18.6 | 26.2 |
| **Gated DeltaNet** | 25.4 | 34.8 | 23.7 | 60.0 | 20.0 | 19.8 | **30.6** |
| Transformer++ | 29.5 | 38.0 | 52.2 | 58.3 | 22.5 | 21.6 | 37.0 |
| Samba | 33.0 | 39.2 | 50.5 | 57.7 | 23.5 | 20.2 | 37.3 |
| **GDN-H1** | 35.6 | 39.7 | 52.0 | 60.1 | 24.6 | 22.2 | 39.0 |
| **GDN-H2** | 38.2 | 40.4 | 50.7 | 63.3 | 24.8 | 23.3 | **40.1** |

### Table 5（§4）— LongBench 14 任务（avg 列）
| Model | NQA | QQA | MFQ | HQA | 2WM | Mus | GvR | QMS | MNs | TRC | TQA | SSM | LCC | RBP | **Avg** |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| RetNet | 12.1 | 10.7 | 19.1 | 10.7 | 18.0 | 5.8 | 4.8 | 15.8 | 7.9 | 19.0 | 18.0 | 12.8 | 14.1 | 17.9 | 13.2 |
| HGRN2 | 10.7 | 12.1 | 19.1 | 11.3 | 15.7 | 6.0 | 5.2 | 15.1 | 9.2 | 16.0 | 15.8 | 10.3 | 18.6 | 20.8 | 13.5 |
| Mamba | 13.0 | 10.1 | 20.4 | 10.1 | 16.7 | 6.0 | 7.2 | 15.9 | 8.4 | 23.1 | 21.9 | 11.2 | 17.9 | 19.0 | 14.6 |
| DeltaNet | 12.9 | 10.8 | 21.5 | 10.9 | 13.2 | 5.1 | 6.5 | 13.5 | 7.2 | 15.5 | 23.3 | 11.6 | 17.6 | 20.3 | 13.6 |
| Mamba2 | 11.1 | 11.3 | 18.6 | 11.8 | 15.1 | 6.7 | 6.7 | 14.5 | 7.4 | 13.0 | 23.6 | 8.4 | 17.9 | 20.6 | 13.5 |
| **Gated DeltaNet** | 14.1 | 14.0 | 23.3 | 13.7 | 14.4 | 5.8 | 7.5 | 16.4 | 7.9 | 30.0 | 22.4 | 23.0 | 18.7 | 22.1 | **16.6** |
| Transformer++ | 11.8 | 9.3 | 10.0 | 10.9 | 4.2 | 6.1 | 7.4 | 15.8 | 6.6 | 16.9 | 13.5 | 3.9 | 17.2 | 18.7 | 11.0 |
| Samba | 12.5 | 12.9 | 25.4 | 11.2 | 19.7 | 6.8 | 9.1 | 15.7 | 11.0 | 20.0 | 22.7 | 22.8 | 18.1 | 21.1 | 15.9 |
| **GDN-H1** | 14.5 | 12.3 | 26.6 | 12.6 | 23.6 | 6.1 | 9.1 | 16.1 | 12.8 | 33.5 | 23.9 | 26.8 | 15.5 | 19.2 | 17.8 |
| **GDN-H2** | 12.7 | 13.0 | 27.1 | 12.7 | 20.6 | 7.5 | 10.4 | 16.2 | 13.0 | 40.5 | 22.7 | 27.9 | 19.9 | 22.1 | **18.4** |

### Table S.1（附录 B.2）— GDN block ablation（400M, 15B tokens）
| 变体 | Avg-PPL↓ | Avg-Acc↑ |
|---|---|---|
| GDN (head dim 128, baseline) | 27.35 | 47.26 |
| w. naive Delta Rule（去 α 门控） | 30.87 | 45.12 |
| w/o Short Conv | 28.95 | 46.16 |
| w/o Output Gate | 29.12 | 45.46 |
| w/o Output Norm | 27.55 | 47.07 |
| w. L1-norm & ReLU | 30.79 | 45.92 |
| w. L1-norm & 1+ELU | 30.34 | 46.05 |
| w. L1-norm & SiLU | 30.18 | 46.09 |
| w. L2-norm & ReLU | 27.67 | 46.94 |
| w. L2-norm & 1+ELU | 27.58 | 47.17 |
| w. Head Dim 64 | 28.31 | 46.35 |
| w. Head Dim 256 | 27.13 | 47.38 |

### Table S.2（附录 B.2）— 混合架构排列顺序 ablation（500M/15B）
| 排列顺序 | Avg-PPL↓ | Avg-Acc↑ |
|---|---|---|
| GDN + SWA + Mamba2 | 24.02 | 47.88 |
| GDN + Mamba2 + SWA | 23.69 | 47.54 |
| Mamba2 + SWA + GDN | 24.14 | 47.92 |
| **Mamba2 + GDN + SWA** | **23.54** | **48.73** |

## 与同类对比

- **vs Mamba2**（§1, §3.2, Table 3/5）：Mamba2 用对角转移 αt I，均匀衰减；GDN 用 αt(I − βt kt kt^T) 兼具遗忘幅度与方向性。S-NIAH-1 长序列上 GDN 8K 91.8 vs Mamba2 30.4；Wiki ppl 16.42 vs 16.56；LongBench avg 16.6 vs 13.5（Mamba2 仅 13.5）。Mamba2 在 S-NIAH-3 UUID 上崩塌（4K 4.6）而 GDN 保持 27.6。Fig.3（M3 解读）进一步显示 Mamba2、DeltaNet、GDN 三者在 1.3B/H100 上吞吐曲线几乎贴合并保持平直（约 38–50 K t/s），而 Transformer++ 随序列增长陡降——说明 GDN 的质量提升不以线性 scaling 的吞吐为代价。
- **vs DeltaNet**（§1, §3.2, Table 2/4）：DeltaNet 无 forget gate，真实世界 retrieval（Table 4 avg 26.2）与 S-NIAH-2/3 长序列（4K 18.6/22.4）显著掉点；GDN 在两者上均升级（30.6 / 92.2 / 27.6）。但纯 synthetic S-NIAH-1 DeltaNet 接近满分，说明 retention 任务无需 gating。Fig.3（M3 解读）指出 DeltaNet 在短序列吞吐偏低、而 GDN-H1/H2 通过 SWA 弥补了这一短板并在所有序列长度上保持最高吞吐。
- **vs Longhorn**（§3.1 脚注 3）：优化同一 delta 目标，Longhorn 用 implicit online learning（Kulis & Bartlett 2010）推闭式全局最优；DeltaNet/GDN 用一步显式梯度下降——后者更简单、可并行。
- **vs RWKV-7**（§5, concurrent）：思想类似但 RWKV-7 用 diagonal-plus-low-rank 转移 `St = St-1(diag(dt) − at bt^T) + vt kt^T`，形式更松散；其 chunkwise 算法已在 Flash Linear Attention 库（Yang & Zhang 2024）实现，可类比迁移到 GDN。
- **vs Titans / TTT**（§3.1, §5）：均把 S 视作 fast weight + 在线 SGD；Titans/TTT 用非线性回归 `½‖fS(kt) − vt‖²`，表达力更强但需在整 chunk 后做非线性更新，损失并行性；GDN 仍是一阶线性递归，保持完全并行。
- **吞吐对比**（Fig.3, §4）：Transformer++ 在 2K 短上下文因 Flash-Attention-2 最快（约 55 K t/s）；GDN ≈ DeltaNet，比 Mamba2 慢 2–3K t/s（更 expressive 的转移矩阵所致）；混合模型 H1/H2 因 SWA 局部并行而吞吐高于 standalone GDN（约 50–54 K t/s）。Fig.3（M3 解读）强调 GDN-H1 在短序列也保持高吞吐，是"质量 + 速度"双优的最优部署形态。

## 长度外推（Fig.2 专项，与 §4 叙述交织）

Fig.2（M3 解读）给出 4K→20K 六项 long-context benchmark（GovReport、QMSum、NarrativeQA、Qasper、CodeParrot、PG19）的 ppl-vs-length 曲线，对比 7 个模型（Mamba1、DeltaNet、Mamba2、Samba、GatedDeltaNet、GatedDeltaNet-H1、GatedDeltaNet-H2）。M3 解读的核心结论：GatedDeltaNet 及其 H1/H2 混合变体在六项任务上一致取得最低 ppl，且在 20K 外推点退化最小——即把 gating 加到 delta update rule 上同时改善了外推稳定性与记忆管理。这与 §4 正文"Gated DeltaNet achieves the lowest overall perplexity across tasks among RNN models…exhibits relatively more robust performance, suggesting better memory management"的叙述逐字对应，并把"混合模型靠 SWA 处理局部上下文以进一步缓解长序列压力"这一文字结论落到 H1/H2 曲线在 20K 端点的更低 ppl 上。需注意 §4 同时坦承"we observe mixed results in length extrapolation"——即 GDN 并非在每一项的每一长度都领先，Fig.2 中部分任务的曲线在 14K 附近出现 U 形回升，作者把 >20K 的进一步扩展列为 future work。

## 跨论文关系（→ MOC 谱系）

- **[[mamba2-transformers-are-ssms-generalized-models-and-efficient-algorithms-through-structured-state-space-duality]]** — 直接前身：Mamba2 的 gated update rule 与 SSD chunkwise 算法是 GDN 的"gating 侧"基础（St=αt St-1+vt kt^T，§2.1）。GDN 把对角 αt I 升级为 Householder αt(I−βt kt kt^T)。
- **[[deltanet-parallelizing-linear-transformers-with-the-delta-rule-over-sequence-length]]**（Yang 2024b）— 直接前身：WY 表示 + UT transform + chunkwise 并行算法被本文扩展到含 αt 的情况（§3.3, Appendix A 证明）。GDN 是 DeltaNet 的"gated 补完"。
- **[[gated-linear-attention-transformers-with-hardware-efficient-training]]**（GLA, Yang 2024a）— 同作者前作：matrix-valued decay + 通用化 chunkwise；GDN 沿用其 fine-grained decay 与 chunkwise 思路。
- **[[kimi-linear-an-expressive-efficient-attention-architecture]]**（KDA / Kimi Linear）— **下游精化**：KDA = GDN + channel-wise fine gating；GDN 是 head-wise coarse-gating 前身，Kimi Linear 在其上把 α/β 从 head 粒度细化到 channel 粒度。谱系：Mamba2 → GDN → KDA。
- **[[parallel-scan-on-ascend-ai-accelerators]]** — 工程侧下游：GDN 的 chunkwise scan kernel 在 NPU 上的实现/优化研究。
- **[[longhorn-state-space-models-are-amortized-online-learners]]**（Liu 2024）— 提供在线学习统一视角（Table 1），GDN 在其框架下被解释为带 adaptive scaling 的 delta 回归。
- **[[titans-learning-to-memorize-at-test-time]]**（Behrouz 2024）— 同期并行：同样在 test-time SGD 上引入 weight decay，但用非线性回归；思路对照。
- **[[samba-simple-hybrid-state-space-models]]** & **[[griffin-mixing-gated-linear-recurrences-with-local-attention]]** — 混合架构前作；GDN-H1/H2 直接对标其 linear+SWA 范式（Fig.1 H1/H2 层叠模式）。
- **[[retnet-retentive-network]]**, **[[hgrn2-gated-linear-rnns-with-state-expansion]]**, **[[rwkv6-eagle-and-finch]]**, **[[mamba-linear-time-sequence-modeling-with-selective-state-spaces]]** — linear RNN 谱系中的姊妹节点，数据相关/无关 decay 分支。
- 谱系定位：**GDN 是 delta-rule 分支的锚点**——线性/混合注意力基因树上 Mamba2（gated decay 分支）与 DeltaNet（delta rule 分支）的合流点，向上承接 SSD chunkwise 与 WY/UT 算法，向下衍生 KDA（channel-wise 精化）与 NPU 上的并行 scan 优化。

## 局限与边界

1. **真实 retrieval 提升幅度小于 synthetic**（§4）：Table 4 中 GDN 对 Mamba2/DeltaNet 的优势（30.6 vs 29.8 / 26.2）远小于 Table 2 S-NIAH 上的优势。作者归因于 instruction-unaligned 小模型易产生 repetition errors（Arora 2024b Appendix E），而该错误与 update rule 选择无关，缩小了模型间差距。
2. **Length extrapolation 结果混合**（§4, Fig.2）：GDN 在六项 long-context 任务上整体 ppl 最低，但并非一致领先；Fig.2（M3 解读）显示部分任务曲线在 14K 附近出现 U 形回升，hybrid 模型靠 SWA 处理局部上下文才进一步缓解——说明 GDN 的记忆管理在 >20K 序列上仍有压力，作者明示"future work will explore…even longer sequences"。
3. **纯 recurrent 在真实 retrieval 仍输给 attention**（§4）：Table 4 中 GDN（30.6）远低于 Transformer++（37.0）与 hybrid（40.1），印证 linear RNN 固定 state size 在真实检索上的天花板未被 GDN 完全打破。
4. **delta rule 的理论局限**（§5 引 Irie 2023）：delta rule 存在已知表达力限制；GDN 未根本解决，只是靠 gating 缓解饱和。提升表达力需外挂 negative eigenvalues（Grazzi 2024）、Householder 连乘（DeltaProduct, Siems 2025）或非线性回归（TTT/Titans）——这些可叠加到 GDN，但会牺牲并行性或需 workaround。
5. **算法证明范围**（Appendix A）：扩展 WY 表示的数学归纳法证明仅以"first chunk"演示，作者以"notation clutter"为由略去一般化推导；多 chunk 通用性需读者自验。
6. **门控参数化沿袭 Mamba2**（§3.4 脚注 4）：α 直接复用 Mamba2 的参数化但未展开细节，可能限制了 α 的设计自由度——这正是后续 KDA channel-wise fine gating 改进的切入点。
7. **无大规模实验**：主实验仅 1.3B / 100B tokens，scaling 行为未验证；ablation 在 400M / 15B tokens（Table S.1）与 500M / 15B（Table S.2）上完成。Fig.3 的吞吐仅报单 H100、1.3B，未覆盖更大模型/多卡。

## 文件状态

- 深读笔记已写入：`/mnt/project/g00952465/AICO-knowledge/extraction/deep/gated-delta-networks-improving-mamba2-with-delta-rule.md`
- 未修改任何其他文件，未执行 git commit/push。
