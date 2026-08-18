# Muon — 技术点深读（DEEP 2026-08-18）
> 全要素深读笔记。独立文件，extract_phase1 重跑不丢。
> 论文：Muon is Scalable for LLM Training · arXiv:2502.16982

## 核心问题

Moonshot AI 团队针对 Muon optimizer（K. Jordan et al. 2024，通过对 2D weight matrix 的 momentum 做 Newton-Schulz 近似正交化来更新参数）在 small-scale LM 上展现的优势，回答三个悬而未决的开放问题（§1）：

1. **可扩展性**：基于 matrix orthogonalization 的 optimizer 能否 scale 到数十亿参数 + 数万亿 token 量级训练？
2. **分布式可行性**：近似正交化如何在分布式集群上计算？Muon 需要完整梯度矩阵（非 element-wise），与 ZeRO-1 直接冲突。
3. **训练阶段通用性**：是否能跨 pre-training 与 SFT 两个阶段都保持优势？

更深层动机（§2.1）：Muon 的 norm-constraint 视角下，Adam 对应动态 Max-of-Max norm，而 Muon 提供静态 Schatten-p（p→∞ 时为 spectral norm）约束；对作用在（局部）欧氏空间上的算子型权重，induced operator norm（spectral norm）比 Adam 的 norm 更合理（Cesista 2024, Bernstein et al. 2024）。该论文要把这一理论优势转化为大规模训练的实证优势。

## 关键创新点

1. **引入 Weight Decay 修复长尾发散（§2.2 Weight Decay）**
   机制：在原始 Muon 更新上叠加 AdamW 式 weight decay —— `W_t = W_{t-1} − η_t(O_t + λW_{t-1})`（Eq.3），λ 全程设 0.1（§3.3）。
   动机：scaling up 时观测到 weight RMS 与 layer output RMS 持续增长，超出 bf16 高精度范围，损害性能。原始 Muon 不带 weight decay。
   效果（§3.2，800M 模型 / 100B tokens ≈ 5× optimal）：vanilla Muon 早期收敛更快（iter 24000 处 val loss 领先 0.023），但长期权重过大被 Muon-with-WD 反超（iter 66000 处领先 0.017），最终在 over-train regime 优于 vanilla Muon 与 AdamW（Figure 2）。

2. **Consistent Update RMS —— 修正 shape-dependent 更新幅度（§2.2 Lemma 1）**
   机制：作者证明 **Lemma 1**：对 full-rank `[A, B]` 矩阵，Muon 理论 update RMS = `√(1/max(A,B))`（证明见 Appendix A：对正交更新 X=U[:,:r]V[:r,:]，RMS²=r/(mn)，full-rank 时 r=m 即 RMS=√(1/n)）。
   问题：scaling 时不同 shape 的矩阵 update RMS 不一致 —— `max(A,B)` 大（如 dense MLP）更新过小，限制表示能力；`max(A,B)` 小（如 GQA/MLA 下每个 KV head 单独参数）更新过大，导致训练不稳定。
   方案：将 Muon update 乘以 `√max(A,B)` 抵消 Lemma 1，进一步乘 0.2 以匹配 AdamW 经验 update RMS 区间 0.2~0.4 —— 最终更新规则 `W_t = W_{t-1} − η_t(0.2·O_t·√max(A,B) + λW_{t-1})`（Eq.4）。
   副产物：因 update RMS 与 AdamW 对齐，**Muon 可直接复用为 AdamW 调好的 LR / weight decay**，免超参调优（"out-of-the-box"）。

3. **Adjusted LR 作为低成本 RMS 控制方案（§3.1, Table 1）**
   三种 RMS 控制方案对比：Baseline（乘 0.2·√H）、Update Norm（直接 RMS(O_t)=0.2，Eq.6）、Adjusted LR（按 shape 乘 0.2·√max(A,B)，Eq.7）。
   800M/4B-token 实验在改用 2-layer MLP（`[H,4H]`）以放大 shape 差异后：Update Norm 与 Adjusted LR 都优于 Baseline；对 `[H,4H]` MLP 权重 RMS 约为 Baseline 的 2 倍（因 √max(H,4H)/√H=2）；对 `[H,H]` query 权重，Adjusted LR 退化为与 Baseline 相同（因 √max(H,H)/√H=1），而 Update Norm 仍放大。**作者选 Adjusted LR 因其计算成本更低**。

4. **Distributed Muon —— ZeRO-1 兼容的分布式实现（§2.3, Algorithm 1）**
   核心矛盾：ZeRO-1 按元素分片 optimizer states，但 Newton-Schulz 需要完整梯度矩阵。
   方案：在 ZeRO-1 基础上加两步 —— (a) **DP Gather**：把本地分片梯度 gather 成完整 G；(b) **Calculate Full Update**：对完整 G 跑 Newton-Schulz，算完后只保留本地分片 u，丢弃其余。
   性能分析：
   - **Memory**：Muon 只需 1 个 momentum buffer（AdamW 需 2 个），optimizer 额外内存仅为 Distributed AdamW 的一半。
   - **Communication**：通信量 ∈ (1, 1.25] × Distributed AdamW。Muon = 4(fp32 G reduce-scatter) + 2(bf16 Muon gather) + 4(fp32 P all-gather) = 10；AdamW = 4+4 = 8；比值 10/8 = 1.25 上界（bf16 因 Newton-Schulz 在 bf16 进行，通信减半）。实测多 DP 时更接近下界 1.5（注：1.5 应为相对 AdamW 单步开销的实测增量比）。
   - **Latency**：端到端延迟高于 AdamW，但仅约 1%~3% 占前向-反向时间，且可通过 gather/compute overlap、optimizer reduce-scatter 与 param gather overlap 进一步隐藏。
   将向 Megatron-LM 开源 PR。

5. **Scaling Law 验证 ~2× 计算效率（§3.2, Figure 1a, 3, Table 3）**
   在 Llama 架构 dense 模型上做 399M / 545M / 822M / 1.1B / 1.5B 五档 compute-optimal scaling law（Table 2），AdamW baseline 经多阶段 grid search 调优（Appendix B, Table 9: N(C)=0.0483·C^0.511, D(C)=3.448·C^0.489, η(C)=0.01273·C^−0.0575, B(C)=0.00652·C^0.4138）。
   拟合曲线（Table 3）：Muon `LM loss = 2.506·C^−0.052`，AdamW `2.608·C^−0.054`。
   结论：**Muon 仅需约 52% training FLOPs 即可匹配 AdamW compute-optimal 性能**，即 ~2× compute efficiency（§1, §3.2）。

6. **Moonlight：3B/16B MoE 实证落地（§3.3）**
   架构基于 DeepSeek-V3-Small（2.24B activated / 15.29B total，不含 embedding），5.7T tokens，8K context。三阶段 LR schedule（§3.3）：0–33B warmup 到 4.2e-4；33B–5.2T cosine 衰减到 4.2e-5，batch 2048→200B 后翻倍到 4096；5.2T–5.7T cooldown 阶段 LR 升到 1e-4 后线性衰减到 0，用最高质量 math/code/reasoning 数据。auxfree bias 更新率 stage1/2 为 1e-3，stage3 为 0。架构小修改（Appendix C）：去掉 MTP、改进 auxfree bias 公式为 `b_i += u·(sign(e_i) − sign(e).mean())`、gate scaling factor 设 2.446（Figure 6 给出计算代码）。

7. **SVD Entropy 谱分析佐证"多方向探索"直觉（§3.4, Figure 4/9/10）**
   对权重矩阵奇异值 σ 定义 SVD entropy `H(σ) = −(1/log n)·Σ (σ_i²/Σσ_j²)·log(σ_i²/Σσ_j²)`。
   1.2T-token 各 checkpoint × 6 组权重（AttnQO/AttnKV/Experts/SharedExperts/Router/Dense）下，Muon 的 SVD entropy 始终高于 AdamW，且 **Router 权重差异最显著** —— 暗示 MoE 从 Muon 获益更大。Appendix F 显示 >90% 权重矩阵 Muon 的 SVD entropy 高于 AdamW。

8. **SFT 阶段：Muon-pretrain + Muon-SFT 一致性最优（§3.5, Table 6/7）**
   Moonlight@1.2T 上用 tulu-3-sft-mixture 做 2-epoch SFT（LR 5e-5 线性衰减到 0）。
   4 组合（pretrain×SFT = Muon×Muon / AdamW×Muon / Muon×AdamW / AdamW×AdamW）中 Muon×Muon 全面最优（MMLU 55.7, HumanEval 57.3, GSM8K 68.0）。
   关键观察：**SFT optimizer 与 pretrain optimizer 不一致时，Muon-SFT 不显著优于 AdamW-SFT** —— 存在 optimizer mismatch。在 Qwen2.5-7B（AdamW 预训练）上做 Muon-SFT 与 AdamW-SFT 持平（Table 7），印证 Muon 主要在 pretraining 阶段发挥优势。

9. **训练稳定性观察（Appendix D, Figure 7）**
   全程无 loss spike / grad norm spike。但 Max Attention Logit 在特定层初期上升超过 100（Moonlight 蓝线比 Moonlight-A 红线更激进），引入 large attention logits ratio（~10⁻⁴）监控；随训练进行 max logit 逐渐下降。
   **关键工程结论：RMSNorm gamma 参数必须加 weight decay**，否则每层 output RMS 过高、影响稳定性。

## 表格（原文结构化）

**Table 1（§3.1）—— Muon Update RMS 控制方案对比（800M, 4B tokens / 20B schedule）**

| Method | Train loss | Val loss | query weight RMS | MLP weight RMS |
|---|---|---|---|---|
| Baseline (×0.2·√H) | 2.734 | 2.812 | 3.586e-2 | 2.52e-2 |
| Update Norm (RMS=0.2) | 2.72 | 2.789 | 4.918e-2 | 5.01e-2 |
| Adjusted LR (×0.2·√max(A,B)) | 2.721 | 2.789 | 3.496e-2 | 4.89e-2 |

**Table 2（§3.2）—— Scaling Law 模型与超参**

| #Params (w/o Embed) | Head | Layer | Hidden | Tokens | LR | Batch* |
|---|---|---|---|---|---|---|
| 399M | 12 | 12 | 1536 | 8.92B | 9.503e-4 | 96 |
| 545M | 14 | 14 | 1792 | 14.04B | 9.143e-4 | 128 |
| 822M | 16 | 16 | 2048 | 20.76B | 8.825e-4 | 160 |
| 1.1B | 18 | 18 | 2304 | 28.54B | 8.561e-4 | 192 |
| 1.5B | 20 | 20 | 2560 | 38.91B | 8.305e-4 | 256 |

\* 8K context length 下的 example 数。

**Table 3（§3.2）—— 拟合 scaling law 参数（LM loss, seqlen=8K）**

| Optimizer | Fitted curve |
|---|---|
| Muon | 2.506 × C^−0.052 |
| AdamW | 2.608 × C^−0.054 |

**Table 4（§3.3）—— ~1.2T tokens 对比（同架构）**

| Benchmark | DSV3-Small | Moonlight-A@1.2T (AdamW) | Moonlight@1.2T (Muon) |
|---|---|---|---|
| Activated/Total Params | 2.24B / 15.29B | 2.24B / 15.29B | 2.24B / 15.29B |
| Training Tokens | 1.33T | 1.2T | 1.2T |
| MMLU | 53.3 | 60.2 | **60.4** |
| MMLU-pro | – | 26.8 | **28.1** |
| BBH | 41.4 | 45.3 | 43.2 |
| TriviaQA | – | 57.4 | **58.1** |
| HumanEval | 26.8 | 29.3 | **37.2** |
| MBPP | 36.8 | 49.2 | **52.9** |
| GSM8K | 31.4 | 43.8 | **45.0** |
| MATH | 10.7 | 16.1 | **19.8** |
| CMath | – | 57.8 | **60.2** |
| C-Eval | – | 57.2 | **59.9** |
| CMMLU | – | 58.2 | **58.8** |

**Table 5（§3.3）—— 5.7T tokens 全量对比**

| Benchmark | Llama3.2-3B | Qwen2.5-3B | DSV2-Lite | Moonlight |
|---|---|---|---|---|
| Activated/Total Params | 2.81B dense | 2.77B dense | 2.24B / 15.29B | 2.24B / 15.29B |
| Training Tokens | 9T | 18T | 5.7T | 5.7T |
| Optimizer | AdamW | Unknown | AdamW | Muon |
| MMLU | 54.7 | 65.6 | 58.3 | **70.0** |
| MMLU-pro | 25.0 | 34.6 | 25.5 | **42.4** |
| BBH | 46.8 | 56.3 | 44.1 | **65.2** |
| TriviaQA | 59.6 | 51.1 | 65.1 | **66.3** |
| HumanEval | 28.0 | 42.1 | 29.9 | **48.1** |
| MBPP | 48.7 | 57.1 | 43.2 | **63.8** |
| GSM8K | 34.0 | 79.1 | 41.1 | 77.4 |
| MATH | 8.5 | 42.6 | 17.1 | **45.3** |
| CMath | – | 80.0 | 58.4 | **81.1** |
| C-Eval | – | 75.0 | 60.3 | **77.2** |
| CMMLU | – | 75.0 | 64.3 | **78.2** |

**Table 6（§3.5.1）—— Pretrain/SFT optimizer 互换性**

| Pretrain → SFT | Muon→Muon | AdamW→Muon | Muon→AdamW | AdamW→AdamW |
|---|---|---|---|---|
| MMLU (0-shot CoT) | **55.7** | 55.3 | 50.2 | 52.0 |
| HumanEval (Pass@1) | **57.3** | 53.7 | 52.4 | 53.1 |
| MBPP (Pass@1) | **55.6** | 55.5 | 55.2 | 55.2 |
| GSM8K (EM, 5-shot) | **68.0** | 62.1 | 64.9 | 64.6 |

**Table 7（§3.5.2）—— Qwen2.5-7B 上 SFT 对比**

| Benchmark | Adam-SFT | Muon-SFT |
|---|---|---|
| MMLU (EM, 0-shot CoT) | 71.4 | 70.8 |
| HumanEval (Pass@1) | 79.3 | 77.4 |
| MBPP (Pass@1) | 71.9 | 71.6 |
| GSM8K (EM, 5-shot) | 89.8 | 85.8 |

**Table 8（Appendix A）—— Muon Update RMS 扫描（2k steps ≈ 2B tokens）**

| Optimizer | AdamW | 0.05 RMS | 0.1 RMS | 0.2 RMS | 0.4 RMS | 0.8 RMS |
|---|---|---|---|---|---|---|
| LM train loss | 3.512 | 3.355 | 3.239 | 3.198 | 3.199 | 3.386 |
| LM val loss | 3.679 | 3.503 | 3.374 | 3.325 | 3.314 | 3.543 |
| AttnQ weight RMS | 1.01e-2 | 5.74e-3 | 8.44e-3 | 1.57e-2 | 2.95e-2 | 7.23e-2 |
| MLP weight RMS | 1.25e-2 | 8.01e-3 | 1.27e-2 | 2.35e-2 | 4.51e-2 | 8.73e-2 |

**Table 9（Appendix B）—— AdamW scaling law 经验关系**

| N(C) | D(C) | η(C) | B(C) |
|---|---|---|---|
| 0.0483359·C^0.5112684 | 3.4480927·C^0.4887316 | 0.0127339·C^−0.0574752 | 0.0065202·C^0.4137915 |

**Table 10（Appendix E）—— 与更大算力模型对比**

| Benchmark | Moonlight | Llama3.1-8B | Gemma2-9B | Qwen2.5-7B |
|---|---|---|---|---|
| Activated/Total | 2.24B / 15.29B | 7.38B dense | 8.32B dense | 6.83B dense |
| Tokens | 5.7T | 15T | 8T | 18T |
| MMLU | 70.0 | 66.7 | 71.3 | 74.2 |
| MMLU-pro | 42.4 | 37.1 | 44.7 | 45.0 |
| BBH | 65.2 | 57.7 | 68.2 | 70.4 |
| TriviaQA | 66.3 | 70.3 | – | 60.0 |
| HumanEval | 48.1 | 37.2 | 37.8 | 57.9 |
| MBPP | 63.8 | 47.6 | 62.2 | 74.9 |
| GSM8K | 77.4 | 57.2 | 70.7 | 85.4 |
| MATH | 45.3 | 20.3 | 37.7 | 49.8 |

## 与同类对比

- **vs AdamW（核心对照，全篇基线）**：scaling law 上 ~2× compute efficiency（52% FLOPs 匹配），Moonlight vs Moonlight-A（AdamW 同设置）在 Math/Code 任务增益最大（HumanEval +7.9, MATH +3.7 @1.2T）。但 AdamW 在 Max Attention Logit 控制上"更健康"（Appendix D）。SFT 阶段 Muon 不具备跨 optimizer 的迁移优势。
- **vs Sophia（Liu et al. 2024）**：同属超越 AdamW 的二阶/Hessian 类 optimizer 候选，但 Muon 走 matrix orthogonalization 路线，避免完整 Hessian 计算，更易做 ZeRO-1 分布式。
- **vs SOAP（Vyas et al. 2025）**：SOAP 改进 Shampoo with Adam，与 Muon 同列 norm-constrained optimizer 谱系（Bernstein et al. 2024 "Old Optimizer, New Norm" 框架下）。
- **vs Shampoo / Lie-group preconditioner（X.-L. Li 系列）**：作者将 Muon 归为 steepest descent under spectral norm；Shampoo/Lie-group 走 Kronecker/矩阵群 preconditioner 路线，理论更普适但大规模工程实现更重。
- **vs MARS（Yuan et al. 2024）**：variance reduction 路线，正交方向不同。
- **vs Pethick et al. 2025 "Norm-Constrained LMOs"**：concurrent work，同样讨论 update scaling 因子，作者在 §2.2 脚注 4 与之对齐说明。

## 跨论文关系（→ MOC 谱系）

- 训练-optimizer 主题核心节点。Muon 与 AdamW 形成"orthogonalize momentum vs element-wise adaptive momentum"的对照轴。
- [[megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism]] —— Distributed Muon 实现直接构建在 Megatron-LM 的 TP/PP/EP/DP 之上，作者将开源 Megatron-LM PR（§2.3）。ZeRO-1 通信量优化依赖 Megatron 多并行策略把 gather 范围从 global 收窄到 DP group。
- [[efficient-large-scale-language-models-training-on-gpu-clusters-using-megatron-lm]] —— 同谱系，Megatron-LM 工程实践指引。
- [[megascale-scaling-large-language-model-training-to-more-than-10000-gpus]] —— 同属"大规模 LLM 训练系统"主题；Muon 的 latency-overlap 技巧（gather/compute overlap）与 MegaScale 的 communication-overlap 哲学一致。
- [[zero-memory-optimizations-toward-training-trillion-parameter-models]] —— ZeRO-1 是 Distributed Muon 的内存与通信基线，Muon 在其上加 DP gather / full update 两步。Muon 内存仅为 ZeRO-1 AdamW 的一半（单 momentum buffer）。
- [[root-mean-square-layer-normalization]] —— RMSNorm gamma 必须加 weight decay（Appendix D 关键稳定性结论），直接关联 RMSNorm 在大模型训练中的工程用法。
- MoE 架构侧线：Moonlight 基于 DeepSeek-V3-Small 架构；SVD entropy 分析显示 MoE 的 Router 权重从 Muon 获益最大（§3.4），暗示 MoE + Muon 是值得深挖的组合。

## 局限与边界

1. **非矩阵参数仍需 AdamW 混用**：RMSNorm、LM head、embedding 等非矩阵参数仍由 AdamW 优化（§2.2 "Matching update RMS of AdamW"）。作者在 §4 将"全部参数纳入 Muon 框架"列为未来方向。
2. **Pretrain-SFT optimizer mismatch 未解**：AdamW 预训练 + Muon-SFT 无优势，反之亦然（§3.5, §4）。阻碍了复用现有 AdamW 预训练 checkpoint 生态，需理论解释。
3. **Newton-Schulz 仅近似 spectral norm**：N=5 步迭代是效率-精度折中；N=10 更精确但性能不升反降（§2.2）。Muon 实际提供的是 Schatten-p（p 有限）而非严格 spectral norm，扩展到一般 Schatten norm 是开放方向（§4）。
4. **Max Attention Logit 风险**：Moonlight 比 AdamW 在特定层 logit 更易冲过 100（Appendix D），虽 sparse（~10⁻⁴）且随训练收敛，但表明 Muon 的更新激进性可能引入注意力 logit 失稳，需监控。
5. **GSM8K 未全面超越**：5.7T 全量对比中 Moonlight GSM8K 77.4 略低于 Qwen2.5-3B 的 79.1（后者用了 18T tokens），并非绝对领先（Table 5）。
6. **Scaling law 仅到 1.5B dense**：实证 scaling law 只覆盖 399M–1.5B（Table 2），~2× 效率外推到 16B MoE 是基于 Moonlight 单点验证，缺多档 MoE scaling law 曲线。
7. **通信开销下界争议**：作者声称通信量 ∈ (1, 1.25]，但正文又写"实测接近下界 1.5" —— 1.5 > 1.25 上界，存在表述不一致（§2.3 Analysis），疑为"1.5× Distributed AdamW"实测增量，需 PR 代码澄清。
8. **数据集为私有**：scaling law 与 baseline 用 proprietary dataset，AdamW grid search（Appendix B）也在该私有数据上完成，可复现性受限（Moonlight 本身开源 checkpoint 弥补部分）。
9. **TP 下额外开销**：若启用 Tensor Parallel，Distributed Muon 还需一次 bf16 TP gather（§2.3 脚注 5），未计入主通信量分析。
