# Block Diffusion: Interpolating Between Autoregressive and Diffusion Language Models — 技术点深读（DEEP 2026-08-18）

> 独立文件，extract_phase1 重跑不丢。全要素深读 + M3 图文交叉验证。
> 论文：Block Diffusion: Interpolating Between Autoregressive and Diffusion Language Models · arXiv:2503.09573v3 (ICLR 2025)
> 图表来源：extraction/assets/block-diffusion-...-p{02,06,21,22,23,26,27,28}.png → minimax_captions.json（text-only 消费，未直接 Read PNG）。

## 核心问题

离散扩散（discrete diffusion）语言模型相对自回归（AR）有**并行生成 + 可控性**优势，但存在三大局限（§1）：

1. **定长生成**：D3PM/SEDD 等只能生成训练上下文固定长度的序列，无法像聊天系统那样产生任意长度输出（§1, §6.2）。
2. **无 KV cache**：离散扩散用双向上下文（bidirectional attention）做去噪，无法复用已生成 token 的前向计算，推理低效（§1，引 Israel et al., 2025）。
3. **困惑度差距**：标准指标（perplexity）落后于 AR，限制实用性（§1）。

这三点正是 Figure 1（p.2）用 token 级生成轨迹并排对比的三种范式所要刻画的：AR 左到右逐 token（✓ high quality / ✓ arbitrary-length / ✓ KV caching，✗ not parallelizable）；Diffusion 定长窗口并行去噪（✗ lower quality / ✗ fixed-length / ✗ no KV caching，✓ parallelizable）；Block Diffusion 在块内并行扩散、块间 AR 链接并 KV-cache 条件（M3 解读：四项性质全勾，蓝色箭头=下一解码步）。M3 的核心 takeaway 与论文叙述一致——把扩散放块内、AR 放块间，可同时继承 AR 的 KV cache / 变长与扩散的并行采样。

**解决思路**：引入 **Block Discrete Denoising Diffusion Language Models (BD3-LMs)**——在 AR 与扩散之间插值。对 token 序列分块（block），**块间自回归、块内离散扩散**：既继承 AR 的 KV cache 与变长生成能力，又保留扩散的块内并行采样。配套提出高效训练算法、梯度方差估计器、数据驱动噪声调度，逼近 AR 困惑度。

## 关键创新点

### 1. 块扩散分解：AR-over-blocks × diffusion-in-block（§3.1, Eq.4–6）
- **机制**：把长度 L 序列分为 B 个长度 L′ 的块（B = L/L′）。似然按块分解 $\log p_\theta(x) = \sum_{b=1}^B \log p_\theta(x^b | x^{<b})$（Eq.4），每个条件 $p_\theta(x^b | x^{<b})$ 由一个块内离散扩散过程建模（Eq.5，D3PM 式 reverse process restricted to block b）。对每块套 NELBO 得 $\mathcal{L}_{BD}(x;\theta) = \sum_b \mathcal{L}(x^b, x^{<b};\theta)$（Eq.6），是合法 NELBO 上界。
- **关键插值性质**：L′=1 时退化为纯 AR NLL（Suppl B.4 证明）；L′=L 时退化为纯扩散。BD3-LM 在两端间连续插值，NELBO 随块增大变松（Suppl B.5：$\mathcal{L}_1 \leq \mathcal{L}_2 \leq \dots$，越细分越紧）。这正是 Figure 1（p.2）所绘「插值」位置——BD3-LM 处于 AR 与 Diffusion 之间，且 M3 解读明确其同时占得 KV caching + Arbitrary-length + Parallelizable + High quality 四项。

### 2. 块因果注意力 + KV cache 架构（§3.1, Eq.7）
- **机制**：单一 transformer $x_\theta$（block-causal mask）参数化全部 B 个去噪器。块 b 的 token attend 到块 1…b。关键签名 $x^b_{\text{logits}}, K^b, V^b \leftarrow x^b_\theta(x^b_t, K^{1:b-1}, V^{1:b-1})$（Eq.7）：去噪预测 + 同时吐出本块 KV，并接收历史块 KV（等价于以 $x^{<b}$ 为条件）。
- **效果**：与 AR 一致地支持 **KV cache**——采样新块时复用 $K^{1:b-1}, V^{1:b-1}$，无需重算。这是相对纯扩散（双向、无法 cache）的根本效率改进，对应 Figure 1（p.2）M3 解读中 Block Diffusion 行的 "KV caching" 勾选项。

### 3. 高效训练算法：双通 + 向量化单通（§3.2, Alg.1, Suppl B.6–B.7）
- **挑战**：去噪 $x^b_t$ 需对噪声输入前向，而去噪下一块需对 *干净* $x^b$ 前向——每块至少过网两次。
- **Alg.1 训练**：①对全序列干净前向 $(∅, K_{1:B}, V_{1:B}) \leftarrow x_\theta(x)$ 预算 KV；②对每块 $x^b_{\text{logit}} \leftarrow x^b_\theta(x^b_t, K_{1:b-1}, V_{1:b-1})$ 算去噪 logits。每 token 过网两次。
- **向量化单通**（§3.2, Suppl B.6）：把 $x_{\text{noisy}} \oplus x$（长 2L）拼接送一次前向，配自定义注意力掩码
  $$\mathcal{M}_{\text{full}} = \begin{bmatrix} \mathcal{M}_{BD} & \mathcal{M}_{OBC} \\ \mathbf{0} & \mathcal{M}_{BC} \end{bmatrix}$$
  其中 $\mathcal{M}_{BD}$=块对角（噪声块内自注意）、$\mathcal{M}_{OBC}$=偏移块因果（噪声块 attend 到更早的干净块）、$\mathcal{M}_{BC}$=块因果（干净块更新表示）。避免 B 次 loop。
- **Figure 3（p.21）图文交叉验证**：M3 解读该图为 L=6、L′=2 的 6×6 注意力掩码实例，三个结构区域清晰可分——左上 3×3 块对角 $\mathcal{M}_{BD}$（橙色，$x^1_t,x^2_t,x^3_t$ 仅 attend 本 2-token 块内做去噪）；右上 3×3 偏移块因果 $\mathcal{M}_{OBC}$（蓝色，噪声 token cross-attend 更早的已定稿条件块）；下方 3×6 块因果 $\mathcal{M}_{BC}$（黄色，干净 token $x^1,x^2,x^3$ 按标准块因果更新表示）。M3 takeaway 与 §B.6 公式定义一致：掩码块级结构产生极端稀疏性，是后续 FlexAttention 单核融合的前提。
- **Figure 4（p.22）代码交叉验证**：M3 解读该图为 `block_diff_mask` 的 PyTorch 实现，操作 2n 长度的 q_idx/kv_idx（拼接 $x_t$ 与 $x_0$）。数据流：①用 `x0_flag_q/kv`（index≥n 判 $x_0$）标记 token 归属；②用 `block_size` 把位置映射到块（$x_0$ 用 index−n 偏移）；③三个布尔子掩码 OR 合成——$\mathcal{M}_{BD}$（同块且同侧）、$\mathcal{M}_{OBC}$（$x_t$ 块号 > $x_0$ 块号且 query 在 $x_t$ 侧/key 在 $x_0$ 侧）、$\mathcal{M}_{BC}$（query/key 均在 $x_0$ 侧且块号 ≥）。与 §B.6 的数学定义逐条对应，验证了实现忠实于推导。
- **FlexAttention 加速**（Suppl B.7, Fig.4–5）：把掩码编译为 JIT Triton kernel，相对原生 `scaled_dot_product_attention`（PyTorch≥2.5）在 A5000/L=1024/B=16 上 **≈5× 加速**，端到端 forward **≈15% 加速**，显存大幅降低（跳过全 mask 块）。**Figure 5（p.23）交叉验证**：M3 解读该图为 FlexAttention 调用代码——`functools.partial` 绑定 `seq_len`/`block_size`、`create_block_mask` 在编译期生成 (seq_len*2, seq_len*2) 稀疏掩码、`@torch.compile(mode="max-autotune-no-cudagraphs")` 融合 autotune（注释解释小图不用 cudagraph 避免额外拷贝）、最终 `flex_attention(q,k,v,block_mask=...)` 动态跳过未掩码块。M3 takeaway「块级稀疏预计算使能 kernel fusion，FlashAttention 无法利用」与 §B.7 末段≈15% 加速、A5000/L=1024/B=16 配置完全对齐。
- **效果**：向量化单通相对双通 **20–25% 训练加速**（§6.3 末）。训练成本被压在「<2× 纯扩散训练速度」内（§7 Limitations）。

### 4. 变长 + 块内并行采样（§3.2, Alg.2）
- **Alg.2 采样**：逐块采样 $x^b \leftarrow \text{SAMPLE}(x^b_\theta, K^{1:b-1}, V^{1:b-1})$，每采完一块做干净前向 $(∅, K^b, V^b) \leftarrow x^b_\theta(x^b)$ 累积 KV。块内用任意扩散采样器（cross-attention 注入历史 KV）。
- **效果**：①支持**任意长度**生成（超出训练上下文），纯扩散只能定长；②块内**并行**采样，AR 只能逐 token；③NFE 上界为 L——masked 扩散的 carry-over unmasking 性质保证 token 一旦 unmask 不再 remask（§6.2, Suppl B.3），NFE ≤ L。
- **Figure 7（p.27）+ Figure 8（p.28）定性交叉验证**：两图均为生成样本（非架构图），共同支撑「训练上下文外生成」主张。Figure 7（p.27）M3 解读：BD3-LM L′=16 在训练上下文 L=1024 下，用 T=5K 步生成 L=2031（≈2× 训练窗口）的连贯叙事（女孩赴墨西哥、母亲在曼谷机场被扣、Calais 难民评论），GPT2-Large Gen.PPL=24.3、entropy=5.5；M3 takeaway「block diffusion 可外推超训练上下文」直接落地。Figure 8（p.28）M3 解读：AR（Sahoo 2024a）同条件下生成 L=2003，Gen.PPL=10.6、entropy=5.5——数值最优，但 M3 指出文本跨多个无关主题（NFL 赛事、Charlotte Gardens 树木纠纷、建筑评论）漂移、实体幻觉，说明长上下文 AR 预训练本身不保证长程连贯。两图并看：BD3-LM 在 Gen.PPL 上仍逊 AR（24.3 vs 10.6），但 BD3-LM 样本主题一致性在 M3 定性观察中优于纯扩散基线 MDLM（见下条 Figure 6）。

### 5. 梯度方差诊断：解释 AR–扩散困惑度鸿沟（§4.2–4.3, Eq.9–10, Table 1, Fig.2）
- **观察**：L′=1 时 BD3-LM 在期望上与 AR NLL 等价（Suppl B.4 严格证明：$-\sum_b \log p_\theta(x^b | m, x^{<b})$，即 AR），但在 LM1B/16B tokens 上竟有 **~2 点 PPL 差距**（Table 1：BD3-LM L′=1 ≤25.56 vs AR 22.88）。
- **根因**：扩散 NELBO 每批只对约半数 token（被 mask 的）算交叉熵（$\mathbb{E}_t q(x^b_t=m|x^b)=0.5$），等价于 AR 用一半 batch size 训练 → **梯度方差翻倍**。
- **Figure 2（p.6）图文交叉验证**：M3 解读该图为 LM1B 单 token 生成的训练 NLL 曲线（x 轴 0–250K+ 步，y 轴 NLL 3.0–4.0；注意 NLL≈3.15 对应 exp(3.15)≈23 PPL，与 Table 1 AR=22.88 自洽）。四条曲线：BD3-LM(NELBO)（红）全程高抖动；BD3-LM(Tuned schedule)（紫）平滑；AR（橙）平滑基线；AR(random batch size)（绿）抖动。M3 takeaway 与 §4.2 叙述精准对齐——默认 NELBO 因半数 token 被 mask 产生与「AR 用随机 batch size」同量级的训练方差；tuned schedule（全 mask）把方差压回到 AR 水平。图 caption 亦点明 "half of the tokens in a batch are masked on average"，与正文 $q(x^\ell_t=m|x^\ell)=0.5$ 一致。
- **方差估计器**（Eq.9–10）：给 batch size K 的 NELBO 估计器 $l(X;\theta)=\frac{1}{K}\sum_{k,b}\frac{\alpha'_{t(k,b)}}{1-\alpha_{t(k,b)}}\log p_\theta(\cdot)$（Eq.9），梯度方差用 M 个 batch 的经验方差近似（Eq.10）。
- **验证**：328M tokens 后，NELBO 训练方差 1.52 vs 全 mask 调度 0.11（§4.2 末）。把调度设为全 mask（$q(x^b_t=m|x^b)=1$）使扩散目标等价 AR，Table 1 PPL 收敛到 22.88，方差消除。

### 6. Clipped 噪声调度 + 数据驱动优化（§5.2–5.3, Table 2, Table 8）
- **直觉**（§5.1）：mask 率两端（几乎不 mask / 全 mask）学习信号弱、梯度高方差；中间区间信号强。
- **Clipped 调度**（§5.2）：$1-\alpha_t \sim U[\beta, \omega]$，$0\leq\beta,\omega\leq1$。等价于连续调度在 $[\beta,\omega]$ 外 mask 概率≈0/≈1，区间内 $\alpha'_t \approx 1/(\beta-\omega)$ 线性。
- **数据驱动**（§5.3）：最优 mask 率随 L′ 变化。训练中定期（每 ~5K 梯度步，§6）网格搜索 $\min_{\beta,\omega}\text{Var}_{X,t}[\mathcal{L}(X;\theta,\beta,\omega)]$（用 NELBO 方差作梯度方差代理，因 Eq.10 的梯度方差不能直接套 Kingma 2021 的 squared-loss 方差隔离法）。
- **结果**（Table 2）：每个 L′∈{4,16,128} 存在唯一最优 clipped 分布同时最小化 NELBO 方差与 test PPL；方差与 PPL 强相关。Table 8：clipped 调度全面优于 linear/logarithmic/square-root/square/cosine（如 L′=4：clipped U[0.45,0.95] PPL 29.21/Var 6.24 vs linear U[0,1] PPL 30.18/Var 23.45）。小 L′ 偏好重 mask，大 L′ 偏好轻 mask。

### 7. SUBS 参数化与简化 NELBO（§4.1, Suppl B.3, Eq.8/19）
- **masked BD3-LM** 采用 Sahoo et al. 2024a (MDLM) 框架：per-token 前向 $q(x^\ell_t|x^\ell)=\text{Cat}(x^\ell_t; \alpha_t x^\ell + (1-\alpha_t)m)$，$\alpha_t$ 单调降 $\alpha_0=1,\alpha_1=0$，扩散矩阵 Eq.12–13。
- **SUBS 参数化**（Suppl B.3）：两约束——(1) zero masking probabilities（干净序列无 mask，$p_\theta(x^\ell=m|\cdot)=0$）；(2) carry-over unmasking（unmask 后不再 remask，$p_\theta(x^\ell_s=x^\ell_t|x^\ell_t\neq m)=1$）。模型只需近似 $p_\theta(x^\ell_s=x^\ell|x^\ell_t=m)$。
- **简化目标**（Eq.8/19）：$\mathcal{L}_{BD}(x;\theta)=\sum_b \mathbb{E}_{t\sim[0,1]}\mathbb{E}_q \frac{\alpha'_t}{1-\alpha_t}\log p_\theta(x^b|x^b_t,x^{<b})$，是加权交叉熵之和。$T\to\infty$ 时重建损失 $\mathcal{L}_{\text{recons}}=0$、先验损失 $\mathcal{L}_{\text{prior}}=0$（Suppl B.3 Eq.18）。NELBO 对调度不变（Suppl B.3 末），但 Monte Carlo 估计器方差依赖调度——正是创新点 5/6 的抓手。carry-over 性质亦是创新点 4 中 NFE≤L 上界的依据。

### 8. 生成质量定性对比：MDLM vs BD3-LM vs AR 样本（§6.2, Suppl D, Fig.6–8）
- **Figure 6（p.26）M3 交叉验证**：MDLM（Sahoo 2024a）样本 L=1024/T=5K，Gen.PPL=69.26、entropy=5.6。M3 解读：文本跨艺术评论（Paolo Capacotti、Romei 家族）、博物馆犯罪轶事（Franco Belzina、断烛、雕像修复）、二战史（加拿大/意大利 POW）、音乐产业混搭——topic drift、entity hallucination、incoherent transitions 明显，正是扩散式生成缺乏 AR 长程一致性的典型失败模式。
- 三图并看（Fig.6/7/8）数值梯度：MDLM 69.26 → BD3-LM L′=16 24.3 → AR 10.6（均 GPT2-Large Gen.PPL、entropy 5.5–5.6 可比）。BD3-LM 在 Gen.PPL 上把 MDLM 大幅拉近并向 AR 靠拢，且 M3 定性观察 BD3-LM 样本连贯性优于 MDLM、接近 AR——与 §6.2 末段 "BD3-LM samples have higher coherence than MDLM samples and approach the quality of AR" 叙述一致。

## 表格（原文结构化）

### Table 1（§4.2）— 单 token 生成 PPL，LM1B，16B tokens
| 配置 | PPL (↓) |
|---|---|
| AR | 22.88 |
| AR + random batch size | 24.37 |
| BD3-LM L′=1 | ≤25.56 |
| BD3-LM L′=1 + tuned schedule（全 mask） | 22.88 |

### Table 2（§5.3）— PPL & NELBO 方差 vs 调度 × 块大小，LM1B，65B tokens 预训练 + 10B 微调
| L′ | U[0,.5] PPL/Var | U[.3,.8] PPL/Var | U[.5,1] PPL/Var | U[0,1] PPL/Var |
|---|---|---|---|---|
| 128 | 31.72 / 1.03 | 31.78 / 1.35 | 31.92 / 1.83 | 31.78 / 3.80 |
| 16 | 31.27 / 7.90 | 31.19 / 3.62 | 31.29 / 3.63 | 31.33 / 7.39 |
| 4 | 29.23 / 32.68 | 29.37 / 10.39 | 29.16 / 8.28 | 29.23 / 23.65 |

### Table 3（§6.1）— LM1B test PPL，65B tokens
| 模型 | PPL (↓) |
|---|---|
| Transformer-X Base (AR) | 23.5 |
| Transformer (AR, Sahoo 2024a) | 22.83 |
| D3PM (absorb) | ≤82.34 |
| SEDD | ≤32.68 |
| MDLM | ≤31.78 |
| **BD3-LM L′=16** | ≤30.60 |
| **BD3-LM L′=8** | ≤29.83 |
| **BD3-LM L′=4** | **≤28.23** |

### Table 4（§6.1）— OWT test PPL，524B tokens
| 模型 | PPL (↓) |
|---|---|
| AR | 17.54 |
| SEDD | ≤24.10 |
| MDLM | ≤22.98 |
| **BD3-LM L′=16** | ≤22.27 |
| **BD3-LM L′=8** | ≤21.68 |
| **BD3-LM L′=4** | **≤20.73** |

### Table 5（§6.1）— Zero-shot PPL（OWT 训练，524B tokens，扩散值均为上界）
| 模型 | PTB | Wikitext | LM1B | Lambada | AG News | Pubmed | Arxiv |
|---|---|---|---|---|---|---|---|
| AR | 81.07 | 25.32 | 51.14 | 52.13 | 52.11 | 48.59 | 41.22 |
| SEDD | 96.33 | 35.98 | 68.14 | 48.93 | 67.82 | 45.39 | 40.03 |
| MDLM | 90.96 | 33.22 | 64.94 | 48.29 | 62.78 | 43.13 | 37.89 |
| BD3-LM L′=4 | 96.81 | 31.31 | 60.88 | 50.03 | 61.67 | 42.52 | 39.20 |

注：BD3-LM 在 **Pubmed 超过 AR**（42.52 vs 48.59），在 Wikitext/LM1B/AG News 上为扩散最佳。

### Table 6（§6.2）— 变长生成长度统计，500 篇 OWT 采样
| 模型 | 中位 #tokens | 最大 #tokens |
|---|---|---|
| OWT 训练集 | 717 | 131K |
| AR | 4008 | 131K |
| SEDD | 1021 | 1024（受限于训练上下文） |
| BD3-LM L′=16 | 798 | 9982（≈10× SEDD 最大长度） |

注：Table 6 的变长生成证据由 Figure 7（p.27）单样本 L=2031 定性佐证（M3 解读：训练上下文 L=1024，生成 L=2031≈2× 训练窗口仍连贯）。

### Table 7（§6.2）— 生成质量 Gen. PPL（GPT2-Large）& NFE，300 样本，OWT，110M params/524B tokens（SSD-LM 400M/122B）
| 模型 | L=1024 Gen.PPL / NFE | L=2048 Gen.PPL / NFE |
|---|---|---|
| AR | 14.1 / 1K | 13.2 / 2K |
| SEDD | 52.0 / 1K | – |
| MDLM | 46.8 / 1K | 41.3 / 2K |
| SSD-LM L′=25 (T=1K) | 37.2 / 40K | 35.3 / 80K |
| SSD-LM L′=25 (T=25) | 281.3 / 1K | 281.9 / 2K |
| BD3-LM L′=16 | 33.4 / 1K | 31.5 / 2K |
| BD3-LM L′=8 | 30.4 / 1K | 28.2 / 2K |
| **BD3-LM L′=4** | **25.7 / 1K** | **23.6 / 2K** |

注：BD3-LM 用比 SSD-LM 少一个数量级的 NFE 取得更优 Gen.PPL；L′=4 接近 AR（14.1）。采样用 T=5K 扩散步，NFE 由 carry-over 上界 L 约束。Table 7 数值梯度由 Figure 6/7/8 三样本定性格外印证：MDLM 69.26（Fig.6 单样本）→ BD3-LM L′=16 24.3（Fig.7 单样本）→ AR 10.6（Fig.8 单样本），趋势与表内 L=1024 列 MDLM 46.8 / BD3-LM L′=16 33.4 / AR 14.1 同向（单样本 Gen.PPL 噪声大但方向一致）。

### Table 8（§6.3）— 噪声调度消融，LM1B 3B tokens 微调
| L′ | 调度 | PPL / Var.NELBO |
|---|---|---|
| 4 | Clipped U[0.45,0.95] | 29.21 / 6.24 |
| 4 | U[0.3,0.8] | 29.38 / 10.33 |
| 4 | Linear U[0,1] | 30.18 / 23.45 |
| 4 | Logarithmic | 30.36 / 23.53 |
| 4 | Square root | 31.41 / 26.43 |
| 16 | Clipped U[0.45,0.95] | 31.42 / 3.60 |
| 16 | U[0.3,0.8] | 31.12 / 3.58 |
| 16 | Linear U[0,1] | 31.72 / 7.62 |
| 16 | Square | 31.43 / 13.03 |
| 16 | Cosine | 31.41 / 13.00 |

## 与同类对比

- **vs D3PM (Austin 2021)**（§7）：BD3-LM 建立在 D3PM 上并应用到每个 AR 条件块。三点改进——(1) 突破 D3PM 定长（对应 Figure 1 p.2 M3 解读中 Diffusion 行 "Fixed-length" 缺陷，BD3-LM 行改为 "Arbitrary-length"）；(2) 识别梯度方差为 PPL gap 贡献者并提出方差最小化调度（Figure 2 p.6 曲线可视化）；(3) PPL 优于 D3PM（82.34 → 28.23）。适用 D3PM 各连续时间扩展（Campbell/Sun 2022）。
- **vs MDLM (Sahoo 2024a)**（§7）：BD3-LM 复用 MDLM 的简化 NELBO/SUBS 参数化。两点推进——(1) MDLM 指出 NELBO 对调度不变，本文揭示调度显著影响**梯度方差**；(2) PPL 超 MDLM（LM1B 31.78 → 28.23，OWT 22.98 → 20.73）。注意 PPL 提升部分来自优化调度而非仅块扩散，可反哺 MDLM/D3PM。生成质量上，Figure 6（p.26）MDLM 单样本 Gen.PPL=69.26 主题漂移严重，Figure 7（p.27）BD3-LM L′=16 同设置 Gen.PPL=24.3 且 M3 定性观察连贯性显著优于 MDLM——直接定性证据支持 §6.2 "BD3-LM samples have higher coherence than MDLM"。
- **vs SSD-LM (Han 2022) / 高斯嵌入扩散**（§7, §6.2）：SSD-LM 在连续 embedding 上做高斯扩散的块扩散，不支持 tractable likelihood；BD3-LM 离散扩散支持似然估计。生成效率——BD3-LM NFE 上界 L（carry-over），SSD-LM 每块 T 步共 BT 步（T=1K,L′=25 → 40K NFE）。Table 7：BD3-LM L′=4 用 1K NFE 达 25.7 Gen.PPL，SSD-LM 需 40K NFE 仅达 37.2；NFE 可比时（T=25）SSD-LM 崩到 281.3。连续 embedding 高斯扩散整体 PPL 更差（引 Graves 2023, Gulrajani 2024）。
- **vs PARD (Zhao 2024)**（§7）：PARD 把离散块扩散用于图生成。BD3-LM 三点不同——(1) 在 AR/扩散性能间插值；(2) 支持 KV cache；(3) 在噪声块*内部*做 attention，而 PARD 注入新的空块。
- **vs AR-Diffusion (Wu 2023)**：AR-Diffusion 在 SSD-LM 上加 left-to-right 噪声调度；BD3-LM 走离散 + KV cache + AR/diff 插值路线。
- **vs AR（基线）**（§6.2, Fig.8）：Figure 8（p.28）M3 解读 AR 单样本 L=2003 Gen.PPL=10.6 数值最优，但 M3 定性指出文本跨 NFL/Charlotte Gardens 树木纠纷/建筑评论多主题漂移、实体幻觉——说明「长上下文 AR 预训练本身不保证长程连贯」，BD3-LM 在连贯性维度上的差距比 Gen.PPL 数值差距更小。

## 跨论文关系（→ MOC 谱系）

- **块级半自回归扩散解码分支 anchor**：BD3-LM(#6) 是「block-level semi-AR diffusion」路线的源头锚点——块间 AR + 块内离散扩散 + KV cache 兼容 + 变长生成。在推测解码谱系中与 MEDUSA/EAGLE 的「多头/特征 draft」分支互补平行：MEDUSA(#2)→EAGLE(#4)→EAGLE-2(#5)→EAGLE-3(#3) 走多头/特征预测 + 树校验；Block Diffusion(#6)→DFlash(#7)/DSpark(#8) 走块级半 AR 扩散。
- → **[[dflash-block-diffusion-for-flash-speculative-decoding]]**（DFlash, #7）：直接把 Block Diffusion 的块级半 AR 扩散范式适配到 **flash speculative decoding** 场景，是 BD3-LM 的工程化/推理加速演进。BD3-LM 的 FlexAttention 单核融合掩码（Figure 4/5, p.22/23）与 KV cache 复用机制为 DFlash 提供实现基底。
- → **[[dspark-confidence-scheduled-speculative-decoding-with-semi-autoregressive-generation]]**（DSpark, #8）：同属半 AR 家族，引入 confidence-scheduled 调度，与 BD3-LM 的 data-driven clipped schedule 在「调度驱动半 AR」思想上同源。BD3-LM 的梯度方差估计器（Eq.9–10）与网格搜索 β,ω（§5.3）是 DSpark confidence scheduling 的概念前驱。
- 与 **[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]**(#2) + **[[eagle-speculative-sampling-requires-rethinking-feature-uncertainty]]**(#4)：同处推测解码谱系的另两条分支（多头自推测 / 特征级单头 draft）。Block Diffusion 把「并行性」放在块内扩散而非 draft-then-verify 树，KV cache 复用路径与 EAGLE 系列不同（EAGLE 复用 target 末层特征，BD3-LM 复用历史块 KV）。
- 与 **[[longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification]]**(LongSpec, #59)：BD3-LM 的变长生成（Table 6 max 9982 tokens，Figure 7 p.27 单样本 L=2031，均超训练上下文 L=1024）是 LongSpec 长上下文推测需求的概念前驱——BD3-LM 已展示「训练上下文外生成」可行性，LongSpec 在推测解码侧解决长上下文 draft/verify。

## 局限与边界

- **训练成本**：BD3-LM 训练比纯扩散更贵（每 token 过网两次）。向量化算法压到 <2× 纯扩散训练速度；实验中用标准扩散 loss 预训练进一步缩差距（§7 Limitations）。Figure 4/5（p.22/23）的 FlexAttention 单核融合是压成本的关键工程手段（≈5× attention 加速 / ≈15% forward 加速）。
- **块仍顺序生成**：BD3-LM 逐块自回归，块小时面临与 AR 类似的速度/可控性约束；最优块大小 task-specific（更大块→更强控制，§7）。
- **NELBO 随块增大变松**：Suppl B.5 证明 $\mathcal{L}_1 \leq \mathcal{L}_K$，块越大似然上界越松——L′=L（纯扩散）PPL 最差，L′=1（纯 AR）最紧。存在「块越大并行度越高但似然越松」的根本权衡。
- **方差调度未完全闭环 PPL gap**：clipped 调度大幅降方差（Figure 2 p.6 曲线平滑化）但 BD3-LM L′=4 OWT PPL 20.73 仍落后 AR 17.54（Table 4），零 shot 多数数据集仍不及 AR（Table 5，Pubmed 例外）。
- **生成质量仍逊 AR**：Table 7 L′=4 Gen.PPL 25.7 vs AR 14.1（L=1024）；Figure 6/7/8 三图定性梯度（MDLM 69.26 → BD3-LM 24.3 → AR 10.6）显示 BD3-LM 样本连贯性优于 MDLM 但仍不及 AR（§6.2）。采样依赖 64-bit Gumbel + first-hitting sampler（Zheng 2024）才避免温度截断/速度退化。
- **继承生成模型通病**：幻觉、版权、可控性、有害输出（§7 Limitations 明列，引 Achiam/Gokaslan/Schiff/Wang/Bai）。Figure 6（p.26）MDLM 样本的 entity hallucination/topic drift、Figure 8（p.28）AR 样本的多主题漂移均为该通病的定性实例。
- **架构规模有限**：实验仅 110M 参数（12 层/d=768/12 头，§C.2），未验证 scaling 到大模型；MoE 等结构未触及。
