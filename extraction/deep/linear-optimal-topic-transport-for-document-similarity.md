# Linear Optimal Topic Transport — 技术点深读（DEEP 2026-08-18）

> 论文：*Linear Optimal Topic Transport for Scalable Document Similarity*（Anonymous ACL submission）
> 定位：OT-族文档相似度方法，用 LOT（Linear Optimal Transport）线性化 HOTT 的 Wasserstein 几何，把成对 OT 求解降为 |D| 次离线 embedding + 欧式距离 k-NN。与 AICO-knowledge 主轴（LLM 训练/推理）正交，属"主题建模/文档相似度"正交分支。

## 核心问题

论文攻击的是一个**已被前人部分缓解但仍致命的scalability瓶颈**：在 OT-based 文档相似度家族中，距离计算复杂度与文档数 |D| 的成对组合数挂钩。

- **WMD 的根本病**（§4）：Word Mover's Distance 把文档表示为 nBOW，用 GloVe 嵌入欧氏距离作 ground cost 求 1-Wasserstein。其复杂度为 `O(|D|² n³ log n)`（§4 line 136），其中 n 为支持点（词）数。即使有 WCD（Word Centroid Distance）和 RWMD（Relaxed WMD）这类近似，也只做"部分削减"，对大规模 k-NN 仍不实用。
- **HOTT 的残留病**（§4 line 144-150）：Yurochkin et al. (2019) 的 Hierarchical Optimal Topic Transport 把支持点从词降到 LDA 主题（|T|=70），但**仍需对每对文档求解一次 Wasserstein**——即 `C(|D|,2)` 次 OT 求解。这在 k-NN 场景下（每个测试点对全部训练点）尤其致命。
- **LOTT 的破题点**：用 LOT embedding（Wang et al., 2012）把每个文档的 topic 分布先离线嵌入到一个 L² 空间（相对固定参考分布 σ），之后**所有成对距离退化为欧氏距离**。从 `C(|D|,2)` 次 OT 求解 → `|D|` 次 OT 求解（每文档一次到参考 σ 的 transport map），其余全部线性化（§4 line 158-170，Definition 4.1）。

换言之：HOTT 把"词空间"压成"主题空间"降维；LOTT 在此基础上把"成对非线性 Wasserstein"压成"对参考的线性 embedding"。两层压缩叠加。

## 关键创新点

1. **LOT 嵌入文档 topic 分布（核心机制）**
   - 机制：选固定参考分布 σ（在 70 个 topic embedding 上的 Gaussian mixture）；对每个文档 `d̄_k`（LDA 给出的 topic 比例向量，支撑在 |T| 个 topic embedding `e_{t_j} ∈ R^d` 上），求 `σ → d̄_k` 的 OT plan `T^d̄_k_σ ∈ R^{|T|×|T|}`；再对 σ 的每个 topic i 做重心投影 `z_i = Σ_j (T^d̄_k_σ)_{ij} · e_{t_j}`，堆叠得 `LOT(d̄_k) = [z_1,…,z_{|T|}] ∈ R^{|T|·d}`（§5.2 step 1–4）。
   - 效果：成对距离 `LOTT(d_{k1}, d_{k2}) = ||F_σ(d̄_{k1}) − F_σ(d̄_{k2})||_σ` 在欧氏空间计算，无需再解 OT。相对 HOTT 的标准化吞吐：BBCSPORT 12.7×（LOTT-5），OHSUMED 136.0×（LOTT-1），AMAZON 182.3×（LOTT-1）（§6.3 Table 2）。

2. **参数化参考分布 σ 提供 speed–accuracy 旋钮**
   - 机制：σ 用 K 个等距 Gaussian 混合（K∈{1,2,3,4,5,10,15}），中心在 topic 索引上等间距分布，共享固定 FWHM=10（§6.2 line 412-426）。
   - 效果：K 增大 → test error 单调下降，throughput 缓慢下降（Figure A.3）。LOTT-10 在 Table A.1 各数据集上几乎最低 error（如 AMAZON 0.112 vs HOTT 0.110；OHSUMED 0.462 = HOTT）；LOTT-1 最快但 error 略高（AMAZON 0.133）。FWHM 在大 label space 数据集上也是有效旋钮：OHSUMED FWHM 10→1000，test error 0.54→0.45（−17%），throughput 几乎不变（§6.3 line 508-514，Table A.2）。

3. **理论上下界 HOTT ≤ LOTT ≤ C·HOTT^{2/15}**
   - 机制：基于 Mérigot et al. (2020) 与 Moosmüller & Cloninger (2021) 的 LOT 稳定性界，在"每文档分布是固定参考经 shifting+scaling 的 pushforward"假设下推导（§5 Theorem 5.1，line 320-340）。
   - 效果：给出 LOTT 近似 HOTT 的双侧界，说明线性化误差受控。附录 D 用 CLASSIC 数据集经验验证该 affine pushforward 假设：受限全局 GMM（10-component，共享 shift/scale）总对数似然 −2993 vs 每文档独立 GMM −3683，+690 优势支持该假设（§D line 972-1000）。

4. **与 BERT 家族的 CPU-only 可比性**
   - 机制：在同一 CPU（Intel i9-13900HX, 32GB）上跑 SBERT/SBERT-LARGE/DistilBERT/RoBERTa/BERT 的 k-NN，对比 LOTT-10（§6.5 line 557-606）。
   - 效果：SBERT-LARGE 平均 test error 比 LOTT-10 低 0.065，但耗时 196×；SBERT 平均低 0.051，耗时 33×。LOTT-10 在 5/6 数据集上超过 RoBERTa（§7 conclusion line 650-651）。t-SNE（§6.6）显示 LOT embedding 类内聚团比 HOTT 更紧、比 SBERT 更分明。

5. **与 BM25 互补（hybrid k-NN）**
   - 机制：LOTT-10 距离与 BM25 检索分线性插值，做 hybrid k-NN（§6.4）。
   - 效果：6 数据集全部超越单独 LOTT-10；BBCSPORT 0.119→0.027，REUTERS 0.090→0.040（§6.4 line 547-555，Table A.6）。说明 OT-based topic 几何与词法 overlap 互补。

## 表格（原文结构化）

### Table 1 — 评估数据集统计（§6.1）
| DATASET | \|D\| | V | AVG(w) | CLASSES |
|---|---|---|---|---|
| BBCSPORT | 737 | 3657 | 116.5 | 5 |
| TWITTER | 3108 | 1205 | 9.7 | 3 |
| OHSUMED | 9152 | 8261 | 59.4 | 10 |
| CLASSIC | 7093 | 5813 | 38.5 | 4 |
| REUTERS | 7674 | 5495 | 35.7 | 8 |
| AMAZON | 8000 | 16753 | 44.3 | 4 |

LDA 配置：70 topics，Gibbs sampler 1500 iter（§6 line 344-346）；topic 用 top-20 词截断重归一化；topic 间距离用 WMD（Gurobi + POT 求解 LP）；k-NN k=7；75/25 train/test split。

### Table 2 — 标准化吞吐（HOTT=1.0）（§6.3）
| DATASET | WMD20 | HOFTT | HOTT | LOTT-1 | LOTT-5 | LOTT-10 | LOTT-15 |
|---|---|---|---|---|---|---|---|
| BBCSPORT | 0.374 | 0.307 | 1.000 | 11.467 | 12.683 | 12.524 | 12.593 |
| TWITTER | 0.397 | 0.290 | 1.000 | 98.579 | 101.807 | 101.073 | 101.646 |
| OHSUMED | 0.169 | 0.388 | 1.000 | 136.026 | 125.825 | 124.353 | 124.953 |
| CLASSIC | 0.275 | 0.212 | 1.000 | 93.333 | 87.735 | 86.156 | 84.983 |
| REUTERS | 0.149 | 0.177 | 1.000 | 92.032 | 91.417 | 89.976 | 89.441 |
| AMAZON | 0.074 | 0.287 | 1.000 | 182.299 | 168.049 | 168.388 | 165.111 |

观察：dataset 越大、vocab 越大，LOTT 相对 HOTT 优势越显著（AMAZON 182× vs BBCSPORT 12.7×）。WMD20/HOFTT 均 < 1.0，比 HOTT 还慢。

### Table A.1 — 各 LOTT 变体与 OT baseline 的 mean test error（§6.3）
| DATASET | LOTT-1 | LOTT-2 | LOTT-3 | LOTT-4 | LOTT-5 | LOTT-10 | LOTT-15 | HOFTT | HOTT |
|---|---|---|---|---|---|---|---|---|---|
| BBCSPORT | 0.164 | 0.139 | 0.132 | 0.098 | 0.079 | 0.070 | 0.081 | 0.041 | 0.036 |
| TWITTER | 0.342 | 0.338 | 0.326 | 0.316 | 0.331 | 0.321 | 0.326 | 0.342 | 0.350 |
| OHSUMED | 0.523 | 0.525 | 0.489 | 0.491 | 0.478 | 0.462 | 0.464 | 0.469 | 0.462 |
| CLASSIC | 0.082 | 0.066 | 0.055 | 0.062 | 0.057 | 0.053 | 0.079 | 0.057 | 0.051 |
| REUTERS | 0.113 | 0.105 | 0.106 | 0.097 | 0.103 | 0.093 | 0.096 | 0.058 | 0.062 |
| AMAZON | 0.133 | 0.113 | 0.125 | 0.115 | 0.114 | 0.112 | 0.114 | 0.112 | 0.110 |

关键观察：TWITTER 上 LOTT-4 (0.316) 反超 HOTT (0.350) 与 HOFTT (0.342)；OHSUMED 上 LOTT-10 = HOTT = 0.462。

### Table A.4 — BERT 对比（test error / normalized time, LOTT-10=1.0）（§6.5）
| DATASET | SBERT err | SBERT t | SBERT-LARGE err | SBERT-LARGE t | DistilBERT err | DistilBERT t | RoBERTa err | RoBERTa t | BERT err | BERT t |
|---|---|---|---|---|---|---|---|---|---|---|
| BBCSPORT | 0.054 | 40.9 | 0.027 | 245.5 | 0.034 | 90.9 | 0.095 | 193.2 | 0.014 | 181.8 |
| TWITTER | 0.278 | 2.4 | 0.268 | 15.9 | 0.305 | 7.1 | 0.292 | 14.0 | 0.291 | 14.1 |
| OHSUMED | 0.315 | 34.1 | 0.296 | 181.7 | 0.503 | 70.4 | 0.551 | 137.3 | 0.513 | 149.4 |
| CLASSIC | 0.038 | 20.3 | 0.021 | 113.2 | 0.037 | 46.2 | 0.058 | 86.8 | 0.039 | 93.0 |
| REUTERS | 0.067 | 24.3 | 0.059 | 148.2 | 0.086 | 62.4 | 0.091 | 112.6 | 0.084 | 137.4 |
| AMAZON | 0.056 | 42.6 | 0.049 | 238.0 | 0.121 | 91.9 | 0.131 | 164.5 | 0.078 | 179.9 |

### Table A.3 — 端到端时间分解（秒）（§6.3）
| Dataset | (a) Prep/LDA | (b) Topic-Topic Cost | (c) LOTT-Embed | (d) kNN Query | Total (c+d) | Total E2E |
|---|---|---|---|---|---|---|
| Twitter | 73.76 | 0.78 | 6.30 | 0.93 | 7.23 | 81.77 |
| BBC | 174.00 | 0.98 | 1.33 | 0.16 | 1.49 | 176.47 |
| R8 | 551.76 | 1.37 | 13.96 | 2.94 | 16.90 | 570.04 |
| Classic | 566.40 | 1.39 | 12.45 | 2.48 | 14.94 | 582.73 |
| Ohsumed | 1073.11 | 2.21 | 16.85 | 3.95 | 20.81 | 1096.13 |
| Amazon | 1633.53 | 6.47 | 14.28 | 3.18 | 17.46 | 1657.46 |

观察：one-time 预处理（a+b）是主成本（Amazon 1640s），但 per-doc inference (c+d) 全部 ≤21s，正是 LOTT 在线阶段高效的核心证据。

### Table A.6 — BM25+LOTT hybrid（§6.4）
| DATASET | LOTT-10 | BM25+LOTT |
|---|---|---|
| BBCSPORT | 0.070 | 0.027 |
| TWITTER | 0.321 | 0.323 |
| REUTERS | 0.093 | 0.040 |
| AMAZON | 0.112 | 0.074 |
| CLASSIC | 0.053 | 0.036 |
| OHSUMED | 0.462 | 0.395 |

## 与同类对比

| 维度 | WMD (Kusner 2015) | HOTT (Yurochkin 2019) | **LOTT (本文)** | SBERT |
|---|---|---|---|---|
| 文档表示 | nBOW over 词 | topic 分布 over LDA 主题 | topic 分布 → LOT embedding（参考 σ 的 pushforward） | 句向量 |
| 成对距离 | 1-Wasserstein over 词嵌入 | 1-Wasserstein over topic 分布 | 欧氏距离 over LOT embedding | 余弦 |
| OT 求解次数 | `C(\|D\|,2)` | `C(\|D\|,2)` | `\|D\|`（每文档到 σ 一次） | 0（无 OT） |
| 复杂度 | `O(\|D\|² n³ log n)` | `C(\|D\|,2)` 次 OT over |T|=70 | `\|D\|` 次离线 OT + 线性 k-NN | GPU 友好的 forward |
| 可解释性 | 高（词级 transport） | 中（topic 级） | 中（topic 级 + 参考几何） | 低（黑盒） |
| 词序/上下文 | 无 | 无 | 无 | 有 |
| HOTT 归一化 throughput | <1.0（WMD20） | 1.0 | 12.5×–182.3× | n/a（CPU 慢 33×–196×） |
| 精度（avg test error vs HOTT） | — | baseline | +0.02（nBOW-normalized 0.65 vs HOTT 0.63，§6.3 line 482-484） | −0.051（SBERT） |

机制级差异：
- **vs HOTT**：HOTT 把文档压成 |T| 点的分布，但每对文档仍要在该小空间解一次 Wasserstein；LOTT 把这个"每对一次"换成了"每文档一次（到参考）+ 之后纯欧氏"。代价是线性化引入几何近似误差，由 Theorem 5.1 的 `HOTT ≤ LOTT ≤ C·HOTT^{2/15}` 双侧界控制（§5 line 338-340）。
- **vs WMD**：WMD 支持点是词（V 上千维），LOTT 支持点是 |T|=70 主题，再加线性化——两层降复杂度。
- **vs SBERT**：SBERT 在 GPU 上会大幅提速，本文比较严格限定 CPU-only（§E 承认 GPU 比较会缩小 LOTT 优势）。LOTT 的定位是 edge/无 GPU 部署、且需要可解释 OT 几何的场景。
- **vs LDA-only baseline**（Table A.5）：直接用 LDA topic 比例 + 欧氏距离做 k-NN，LOTT-10 在 accuracy 与 throughput 上几乎全胜（除 BBCSPORT LDA 0.065 略低于 LOTT-10 0.070）——证明收益来自 OT 公式本身而非仅 LDA。

## 跨论文关系（→ MOC 谱系）

LOTT 在 AICO-knowledge 中属于**正交数据方法分支**（主题建模/文档相似度），与核心 LLM 训练/推理主轴无机制耦合。

- [[bertopic-neural-topic-modeling-with-a-class-based-tf-idf-procedure]] — **最强兄弟链接**。同为"主题建模"分支，但 BERTopic 用 class-based TF-IDF + 预训练句向量聚类生成 topic，是 HOTT/LOTT 所用 LDA 的神经替代。本文 §7 line 672-677 与附录 E line 1028-1031 明确指出：LOT embedding framework 与 topic 模型解耦，"replacing LDA with neural topic models such as BERTopic ... is a natural extension"——即 BERTopic 可作为 LOTT pipeline 的 drop-in topic 模型替换，有望缩小与 transformer 方法的精度差。这是机制级而非隐喻级连接。
- [[rllm-relational-table-learning-with-llms]] — 并列正交分支。rLLM 处理关系表结构化数据，LOTT 处理文档分布相似度；两者都是"非 LLM 训练"的数据方法，与 AICO 主轴正交，无机制关联。
- [[a-survey-of-large-language-models]] — 弱背景链接。SBERT/RoBERTa/DistilBERT/BERT 是该综述覆盖的 encoder LLM 家族，本文把它们作为 baseline。LOTT 本身不依赖 LLM。
- **OT-族内部**：WMD (Kusner 2015)、HOTT (Yurochkin 2019)、HOFTT 为直接前置工作，本文为同族线性化后继，但前两者不在 AICO 库内，故仅作内文引用，不产 wikilink。
- 本库未检索到其他 optimal-transport 论文，故 LOTT 在 OT 维度上**暂为独立条目**。

## 局限与边界

- **依赖 LDA 质量**（§Limitations line 680-683）：topic 结构弱或文档过短（如 TWITTER，AVG(w)=9.7）时，transport embedding 收益有限——TWITTER 上 LOTT-10 (0.321) 与 LDA-only (0.336) 差距很小，且 HOTT (0.350) 甚至更差，说明短文本场景 topic 建模本身退化。
- **超参数负担**（§Limitations line 684-687）：LDA topic 数（固定 70）、Gaussian 组件数 K（1–15）、FWHM（10–1000）均需调；FWHM 在大 label space（OHSUMED/REUTERS）才显著，小 label space 用默认 10 即可（§A line 866-868）。
- **规模验证有限**（§Limitations line 688-694）：实验语料仅数千文档（max AMAZON 8000），十万级 corpus 的经验验证未做。理论复杂度降阶在任意规模成立，且 LOT embedding 兼容 ANN 索引，但工程性能未证。
- **无词序/上下文**（§Limitations line 695-699）：BOW 表示，不捕获 word order；定位为"topic-transport 族内的改进"而非 contextual embedding 的通用替代。这是与 BERT 家族的**结构性鸿沟**，非调参可弥合。
- **CPU-only 比较的偏向**（§E line 1003-1023）：BERT 在 GPU 上 forward 会大幅加速，GPU-inclusive 比较会缩小 LOTT 的 33×–196× 优势。本文承认这点，未来版本会补 GPU 数据。这是评估公平性的真实边界。
- **RAG 场景未胜出**（附录 C line 891-961）：在 TREC-COVID (BEIR) 上，直接 BERT retrieval 在 Precision@K/Recall@K/NDCG/MRR 上均超 LOTT retrieval；两步 BERT-retrieve + LOTT-rerank 也未超直接 BERT。作者寄望于调 LDA topic 数与反转 pipeline（LOTT-retrieve + BERT-rerank），但目前 LOTT 在 RAG 检索阶段**实证劣于 BERT**，是其应用边界。
- **affine pushforward 假设的经验性**（附录 D）：双侧界依赖"文档分布是参考经 shifting+scaling 的 pushforward"假设，CLASSIC 上 +690 对数似然支持但未证普适；其他语料可能不满足，界可能松弛。
