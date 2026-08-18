# MEDUSA: Simple LLM Inference Acceleration Framework with Multiple Decoding Heads — 技术点深读（DEEP 2026-08-18，公式重跑）

> 独立文件，extract_phase1 重跑不丢（见 [[extract-phase1-overwrite-gotcha]]）。
> 论文：Cai et al., MEDUSA · arXiv:2401.10774v3 (ICML 2024)。
> 公式权威源 = extraction/formulas.json LaTeX，下文 `$$` 块为逐字引用，LaTeX↔M3 双源校验。

## 核心问题

LLM 自回归解码是 **memory-bandwidth-bound**：每步把全模型参数从 HBM 搬到加速器缓存，却只产 1 token，算力严重浪费（§1）。Appendix G 的 roofline 实测把这一诊断落到硬件层面——在 A100-80GB-PCIe / A40 / A6000 三块卡上对 Llama-7B/13B/33B 全部算子做 roofline（**Figure 9-17, p.18-22**；M3 解读要点：六类算子 × init/ar 两阶段，蓝色虚线=HBM 带宽墙，红色虚线=峰值算力，绿色虚线=ridge point）：decode 阶段的 `qk/pv ar` 与 `qkv mlp ar` / `up/gate/down ar` 全部落在带宽斜线上，操作强度约 1–30 FLOP/Byte，远低于 ridge point（A100 ≈200 FLOP/Byte），确认 decode-time attention 是带宽受限主瓶颈；prefill 阶段则贴在 compute-bound 顶。这意味着：**增加 arithmetic intensity（每字节数据搬运换来的 FLOP）** 就是直接出路。

经典 speculative decoding（Leviathan 2022; Chen 2023）用小 draft 模型先起草再由大模型校验，但**获取/对齐/维护独立 draft 模型困难**——SpecInfer（Miao 2023）报告 275 A100 GPU-hours 用于单独 pretrain draft，且多模型 serving 在分布式环境下复杂度高（§2.1.1）。MEDUSA 的核心问题陈述因此是：**能否不引入任何外部 draft 模型，仅靠主干自身，在单次 forward 内并行产出并校验多 token 候选，把每步 1 token 提升到 1+K 候选树？**

## 关键创新点

### 1. MEDUSA heads：在 last hidden state 上挂 K 个单层并行解码头（§2.1.1）
- **机制**：主干 LLM 原样不动，在最后隐状态 `h_t` 上接 K 个轻量头，第 k 头预测 `(t+k+1)` 位置的 token（原 LM head 仍预测 t+1）。每个头仅一层 FFN + 残差，定义（formulas.json [0]，逐字）：
$$
p_t^{(k)} = \text{softmax}\left(W_2^{(k)} \cdot \left(\text{SiLU}(W_1^{(k)} \cdot h_t)+h_t\right)\right),\\ \text{where } W_2^{(k)}\in\mathbb{R}^{d\times V}, W_1^{(k)}\in\mathbb{R}^{d\times d}.
$$
  `W_2` 用原 LM head 同值初始化、`W_1` 零初始化，使初始预测对齐主干；SiLU 沿用 Llama。机制一句话：单层残差 FFN 把 hidden state 映射到词表分布，作并行多步预测头。
- **效果 + 图**：**Figure 1（p.2）** M3 解读：主干 Embedding→Transformer Layers→LM Head 之外，从 Last Hidden 引出 Medusa Head 1/2/3，各头分别给出 top-k（如头1→"is,',the"；头2→"difficult,is,'"；头3→"not,difficult,a"）与 LM head 的"It,I,As"组合成候选树，校验后接受最长合法前缀"It is difficult"。LaTeX↔M3 双源校验：公式 [0] 的 W_2∈R^{d×V}（V=词表）正对应 M3 所述"each head forecasts a future position"的并行解码头结构，主干 last hidden `h_t` 同时供 LM head 与 K 个 Medusa head 分支。架构核心是把 draft 能力**塞回主干同一 forward**，无需独立模型、无需分布式多模型协调。
- **数字**：单层设计 + 主干冻结使其可在单卡 consumer GPU 上训练，QLoRA 量化主干下 Vicuna-7B MEDUSA-1 仅 **5 小时**（单 A100 PCIe，60k ShareGPT 样本，§2.2.1）。

### 2. Tree-based attention：树形掩码一次 forward 校验多候选（§2.1.2）
- **机制**：K 个头各取 top-s_k 预测做 Cartesian product，构成候选树；累计新 token 数 `Σ_{k=1}^K Π_{i=1}^k s_i`。多个候选 continuation 共享公共前缀，只需把因果掩码改为**树形掩码**（一个 token 只能 attend 到其前驱路径），并相应调整位置编码，即可在单次 forward 内并行校验所有候选，不扩 batch size。
- **图**：**Figure 2（p.3）** M3 解读：s_1=2、s_2=3 时得 2×3=6 候选分支，树形掩码确保每 token 只看前驱。MEDUSA 用 top-down 构树（与 SpecInfer/Staged Speculative 的 bottom-up merge 不同），因为其候选拓扑天然树状。
- **效果**：候选校验几乎零额外 forward，是加速的关键之一。

### 3. MEDUSA-1 vs MEDUSA-2 两级训练配方（§2.2）
- **MEDUSA-1（冻结主干）**损失（formulas.json [1]，逐字）：
$$
\mathcal{L}_{\text{\ours-1}} = \sum_{k=1}^K -\lambda_k\log p_t^{(k)}(y_{t+k+1}).
$$
  机制：各头交叉熵加权和，`λ_k = 0.8^k`（k 越大预测越不确定、权重越小）。可配 4-bit 量化主干（QLoRA），参数高效、无损（主干输出分布不变）。
- **MEDUSA-2（联合训练）**损失（formulas.json [2]，逐字）：
$$
\mathcal{L}_{\text{\ours-2}} = \mathcal{L}_{\text{LM}} + \lambda_0\mathcal{L}_{\text{\ours-1}}.
$$
  机制：在 MEDUSA-1 损失上加 LM 项 `L_LM = -log p^(0)_t(y_{t+1})` 约束主干 next-token 能力，权重 λ_0（实验中 Vicuna-7B/13B 设 `λ_0=0.2`，自蒸馏的 33B/Zephyr 设 `λ_0=0.01`）。需三策略防主干退化：①combined loss（加 LM 项，即上式）；②differential learning rates（MEDUSA heads LR = 4× backbone LR）；③heads warmup（两阶段：先 MEDUSA-1 训头，再联合；也可用 sine schedule 逐步抬升 λ_0）。
- **效果 + 图**：**Figure 3a（p.7）** M3 解读：Vicuna-7B MEDUSA-1=**2.18×**、MEDUSA-2=**2.83×**；Vicuna-13B MEDUSA-1=**2.33×**、MEDUSA-2=**2.83×**。**Figure 3b（p.7）** 按类别拆解 Vicuna-7B MEDUSA-2：Coding 3.29×、Extraction 3.62×——结构化/确定性强的任务收益最大；Humanities/Reasoning 2.58×。Table 3（§3.3 末）按"技术叠加→speedup"汇总：仅 MEDUSA-1 heads 无 tree attention ≈1.5× → +tree attention ≈1.9× → +optimized tree ≈2.2× → MEDUSA-2 ≈2.8×。
- **两阶段训练必要性**：Table 2（§3.3.3）证明直接联合训练（Direct Fine-tuning）质量从 6.17 跌到 5.925，而 MEDUSA-2 两阶段保持 6.18 + 2.83× speedup。

### 4. Typical Acceptance：以熵阈替代拒绝采样（§2.3.1）
- **机制**：拒绝采样保证与原模型同分布但**不能再提升加速率**——draft=original 时若贪心可全接受，而独立采样反而引入拒绝开销。MEDUSA 借鉴 truncation sampling（Hewitt 2022），用如下典型接受判据（formulas.json [3]，逐字）接受"typical"候选：
$$
p_{\text{original}}(x_{n+k}|x_1, x_2, \cdots, x_{n+k-1}) > \\\min\rbr{\epsilon, \delta\exp\rbr{-H(p_{\text{original}}(\cdot|x_1, x_2, \cdots, x_{n+k-1}))}},
$$
  机制一句话：候选 token 在原模型条件概率须超过硬阈 ε 与熵自适应阈 δ·e^{-H} 的较小者——高熵分布允许更多合理续写。首 token 无条件贪心接受以保每步至少产 1 token，后续 token 用上式，最终取最长被接受前缀。
- **图**：**Figure 5（p.8）** M3 解读：固定温度 0.7，画 greedy（星）、random sampling（点）与 typical sampling 曲线（ε 从 0.01 到 0.25 步长 0.01，α=√ε）。随 ε ↑，质量 ↑、加速率 ↓；typical sampling 在大 ε 下与 random sampling 质量相当且加速率更高。
- **退化边界**：温度=0 退化为 greedy（最大加速）；温度>0 时 greedy 输出恒被接受（概率最大）。LaTeX↔M3 双源校验：M3 caption 同样给出 `p_original(x_{n+k}|…) > min(ε, δ·exp(-H(...)))` 且指出 H 为熵函数、ε/δ 为硬阈/熵阈，与 formulas.json [3] 完全一致。

### 5. Self-distillation：无训练数据场景的数据生成（§2.3.2）
- **机制**：对 RLHF 模型或私有数据模型，用模型自身在 seed prompts（ShareGPT/UltraChat）上生成训练集；Zephyr 可 self-talk 单 prompt 生成多轮。MEDUSA-2 联合训练时若仅用自蒸馏数据会降质，故对主干用 KL 蒸馏损失替代 ground-truth label（formulas.json [4]，逐字）：
$$
\mathcal{L}_{\text{LM-distill}} = KL(p_{\text{original},t}^{(0)}||p_t^{(0)}),
$$
  机制：用原模型（关 adapter 即得）的预测分布作软标签蒸馏主干，避免双模型显存。提示：自蒸馏时**不要量化**，否则教师是量化模型、质量降。
- **效果 + 图**：**Table 1（p.7）** 汇总 MEDUSA-2 在四模型上的 acc. rate/overhead/quality（MT-Bench GPT-4 评分，差值）：Vicuna-7B 6.18(+0.01)、Zephyr-7B 7.25(-0.07)、Vicuna-13B 6.43(-0.14)、Vicuna-33B 7.18(+0.05)；speedup 2.35–2.83×。**Figure 8（p.16）** M3 解读：四模型 MEDUSA-2 speedup 分别 2.83/2.66/2.83/2.35×，自蒸馏模型（Zephyr、Vicuna-33B）因 quality-speed trade-off 偏低。Vicuna-33B acc rate 反而较低，作者归因为"hidden 训练数据与自蒸馏 seed 不匹配"。

### 6. Optimized sparse tree construction：贪心选高准确率节点（§2.3.3）
- **机制**：在 calibration set 上测各头 top-i 的准确率 `a^(i)_k`（定义为 top-i 减 top-(i-1) 的边际准确率），独立假设下候选路径准确率为 `Π_j a^(i_j)_j`；候选树节点边际贡献即其准确率。期望接受长度（formulas.json [5]，逐字）：
$$
\sum_{\sbr{i_1, i_2, \cdots, i_k}\in I}\prod_{j=1}^k a_j^{(i_j)}.
$$
  机制一句话：对所有候选组合求和、每组合路径准确率连乘，即期望接受长度；贪心地把"连到当前树且准确率最高"的节点逐个加入，直到达预算节点数，构造期望接受长度最大化的稀疏树。
- **图**：**Figure 6（p.15）** M3 解读：Vicuna-7B MEDUSA-2 的 64 节点稀疏树，深度 4（4 头参与），左偏（算法偏好高概率节点），红色路径标出命中的 ground-truth 分支。**Figure 4a/b（p.8）** M3 解读：稀疏树（红星）在不同候选数下 acc rate 稳定在 3.2–3.5×，dense 随机树（蓝点）聚在 2.5–3.0×；sparse tree 64 节点优于 dense 256 节点。**Figure 4b** speed 在 >150 候选后显著下降——compute-bound overhead 主导（linear layer + self-attention 矩阵乘开销随候选数线性/二次增长）。

### 7. 硬件层验证：MEDUSA 把算子从带宽受限推向 compute-bound（Appendix G）
- **机制 + 图**：**Figure 18（p.23）** M3 解读：固定 batch=16 在 Llama-33B/A100 上，qk/pv 算子随 MEDUSA 候选数 16→112 增加而右移上移，**64 候选 + batch 16 + seq 1024 下达 ~44× FLOP/s 与 ~41× 操作强度**（Table 6）。**Figure 20（p.24）** linear 层（up/gate/down）随候选数增加从带宽斜线推到 312 TFLOP/s compute 顶——证实"候选 token 是免费的算力摊销固定内存搬运"。**Figure 21（p.26）** M3 解读：解析模型 `acc rate = 0.477·log(num_candidate)` 拟合，speedup 在 ~48–64 候选处饱和后下降（attention 重算开销主导）。**Figure 22/23（p.27）** M3 解读：batch>32 后 speedup 下降甚至转负（linear 转入 compute-bound）；seq_len 增加主要抬高 attention 开销、整体性能下降，但最优候选数基本不变。
- **效果**：从硬件原理上回答"为什么 MEDUSA 在 batch=1 最有效，大 batch 失效"——大 batch 让 linear 层已 compute-bound，候选再摊销已无空间。

## 表格（原文结构化）

### Table 1（§3.2）— MEDUSA-2 各模型 acc rate / overhead / quality + 与 SpecDecoding 对比
| Model | Acc. rate | Overhead | Quality (MT-Bench, Δ) | S_SpecDecoding | S_MEDUSA |
|---|---|---|---|---|---|
| Vicuna-7B | 3.47 | 1.22 | 6.18 (+0.01) | 1.47 | 2.83 |
| Zephyr-7B | 3.14 | 1.18 | 7.25 (-0.07) | — | 2.66 |
| Vicuna-13B | 3.51 | 1.23 | 6.43 (-0.14) | 1.56 | 2.83 |
| Vicuna-33B | 3.01 | 1.27 | 7.18 (+0.05) | 1.60 | 2.35 |

> 关系（§B.1）：**Speedup = Acceleration rate / Overhead**（例：Vicuna-7B 3.47/1.22≈2.84）。MEDUSA speedup 全面对比 SpecDecoding 高 1.8×+。

### Table 2（§3.3.3）— Vicuna-7B 不同训练策略
| 配置 | Quality | Speedup |
|---|---|---|
| Baseline | 6.17 | N/A |
| Direct Fine-tuning | 5.925 | N/A |
| MEDUSA-1 | 6.23 | 2.18 |
| MEDUSA-2 | 6.18 | 2.83 |

### Table 3（§3 末）— 技术叠加 speedup
| Technique | Speedup |
|---|---|
| Medusa-1 heads without tree attention | ~1.5× |
| + tree attention | ~1.9× |
| + optimized tree configuration | ~2.2× |
| + Medusa-2 (joint training) | ~2.8× |

### Table 4（Appendix F）— AlpacaEval speedup
| Model | Base (tok/s) | MEDUSA (tok/s) | Acc. rate | Speedup |
|---|---|---|---|---|
| Vicuna-7B | 37.07 | 106.76 | 3.23 | 2.88 |
| Vicuna-13B | 29.01 | 91.54 | 3.28 | 3.16 |
| Vicuna-33B | 17.87 | 40.43 | 2.85 | 2.26 |
| Zephyr-7B | 34.21 | 99.50 | 3.08 | 2.91 |

### Table 5（Appendix G.1）— 各算子 Prefill / Decoding / Parallel-decoding 的计算与空间复杂度
关键行：Parallel decoding 阶段 `XWQ/XWK/XWV` = `O(bqh²)`、`QKT` = `O(bsqnd)`、`XWu/XWg` = `O(bqhi)`，其中 q 为候选长度（MEDUSA 引入的新维度）；线性层与 seq_len 解耦，attention 与 q 线性相关。

### Table 6/7/8（Appendix G.2）— Llama-33B/A100 上 MEDUSA 候选数 vs FLOP/s & 操作强度
- Table 6（batch=16）：seq 1024 + 64 候选 → 54.8 TFLOP/s & 40.96 OI（vs 无 MEDUSA 1.24 & 0.99）。
- Table 7（seq=1024）：batch 1 + 64 候选 → 19.79 & 40.96；batch 64 + 112 候选 → 246.14 & 2893.91（接近 compute-bound）。
- Table 8（linear up/gate/down）：batch 64 + 112 候选 → 246.14 & 2893.91，确证 linear 已 compute-bound。

### 超参（§B.2-B.4）
- K=5 heads，1 layer，`λ_k = 0.8^k`；8-bit AdamW + cosine LR + warmup 40 步。
- MEDUSA-2：QLoRA on all linear layers（含 LM head），rank=32，α=16，dropout=0.05；heads LR=4×backbone（5e-4 backbone / 2e-3 heads for Vicuna-7B/13B）；自蒸馏 backbone LoRA peak LR=1e-4，warmup 20 步。
- Vicuna-7B/13B：global batch 64，4-bit 量化主干，先 MEDUSA-1 初始化再 MEDUSA-2，`λ_0=0.2`。
- Vicuna-33B/Zephyr-7B：直接 MEDUSA-2 + sine schedule λ_0，seq 2048，batch 128，自蒸馏数据 ~100k 样本，温度 0.3 采样。
- MEDUSA-2 tree：64 节点，深度 4（sparse tree，calibration on Alpaca-eval）。

## 与同类对比

- **vs Speculative Decoding（Leviathan/Chen 2023）**：speculative 需独立 draft 模型（SpecInfer 报告 275 A100-hours 单独 pretrain），分布式多模型 serving 复杂；MEDUSA 用主干自己的多头，无 draft 模型、即插即用、分布式友好。Table 1 直接对比：Vicuna-7B SpecDecoding 1.47× vs MEDUSA 2.83×，Vicuna-13B 1.56× vs 2.83×，Vicuna-33B 1.60× vs 2.35×——MEDUSA 全面胜出（Appendix D 用 Llama-68M/160M/Tiny-Vicuna 等开源 draft 评测，最优 γ 随模型大小变化，Figure 7）。
- **vs Blockwise Parallel Decoding（Stern 2018）**：MEDUSA 复兴并有效应用了"多头预测后续 token"的旧思路，加 tree attention + typical acceptance + 优化稀疏树让它真正可用并达 2.3–2.8×。
- **vs SpecInfer（Miao 2023）/ Staged Speculative（Spector & Re 2023）**：两者也用 tree attention 但 bottom-up merge 多 draft 模型候选，仍需 draft；MEDUSA top-down 直接用主干多头 top-k 构静态稀疏树，免 draft。
- **vs 拒绝采样路线**：typical acceptance 不强求分布严格匹配，允许温度>0 时多接受候选换取更高加速（Figure 5）；温度=0 时退化为 greedy 即无损。
- **演进定位**：MEDUSA 是"多头自推测"分支的奠基；EAGLE 系列在其上改单头特征级自回归 + shifted-token 保无损。

## 跨论文关系（→ MOC 谱系, wikilinks [[slug]]）

- **推测解码多头分支奠基**：MEDUSA [[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]（#2）→ EAGLE [[eagle-speculative-sampling-requires-rethinking-feature-uncertainty]]（#4，特征不确定性 + shifted-token 取代多头独立预测）→ EAGLE-2 [[eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees]]（#5，context-aware 动态 draft 树，论文自承 MEDUSA 树结构"not rigorously optimized"埋点）→ EAGLE-3 [[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]]（#3，training-time test 扩展）。
- **与并行 block drafting 分支对比/互补**：MEDUSA 并行多头独立预测存在 independence→suffix decay 问题（被 DSpark 点名）；DFlash [[dflash-block-diffusion-for-flash-speculative-decoding]] 用 KV-injected 并行 + 强 position-1 修复，DSpark [[dspark-confidence-scheduled-speculative-decoding-with-semi-autoregressive-generation]] 进一步半自回归 + confidence + load-aware scheduling。谱系：Medusa（并行开端）→ DFlash → DSpark；Eagle/Eagle2/Eagle3 为 autoregressive 谱系。
- **kernel 层正交补**：DeFT [[deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference]] 把 MEDUSA tree-attention 验证 kernel 换成 Flash Tree-attention，KV IO 73–99% 降，给定树拓扑下 attention 1.02–1.70× over MEDUSA attention——直接增强 MEDUSA 路径。
- **Block Diffusion 分支对照**：BD3-LM/block-diffusion [[block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models]] 把并行性放块内扩散、KV 复用历史块，与 MEDUSA draft-then-verify 树路径互补；LongSpec [[longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification]] / SpecExtend [[specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences]] / JetSpec [[jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting]] 走长上下文/并行树起草路线。
- **正交于 SGLang** [[sglang-efficient-execution-of-structured-language-model-programs]]：MEDUSA 是单模型解码加速，SGLang 是多调用间 KV 复用——可叠加（SGLang runtime 可托管 MEDUSA 头）。
- **基础设施谱系**：MEDUSA 直接受益于 PagedAttention [[efficient-memory-management-for-large-language-model-serving-with-pagedattention]] / vLLM（作者致谢 Zhuohan Li）的 KV 内存管理；与 GQA [[gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints]]/MQA 的 KV 压缩正交可叠加。
- MOC 谱系定位：MEDUSA 是 [[moc_relations]] 明确收录的"多头并行预测 + tree attention 一次校验多候选，无需 draft 模型"锚点，位于"speculative decoding 多头分支"根基位置。

## 局限与边界

- **batch=1 场景为主**：作者明确实验聚焦本地部署 batch=1（§1/§4），大 batch 下内存带宽瓶颈减弱、加速收益下降。Appendix G 给出定量边界：**Figure 22** 显示 batch>32 后 speedup 下降甚至转负（linear 层转入 compute-bound，无空间摊销）；**Figure 23** 显示 seq_len 增加抬高 attention 开销、整体下降。讨论节提到 TensorRT/Huggingface TGI 已跟随实现大 batch 扩展（论文未给大 batch 实测数字）。
- **typical acceptance 引入轻微分布偏差**：温度>0 时多接受候选，质量近似而非严格无损（Figure 5 显示大 ε 下质量接近 random sampling 但仍有 -0.07~-0.14 的 MT-Bench 差值，Table 1）；MEDUSA-1 因主干冻结严格无损，MEDUSA-2 接近无损。
- **MEDUSA-2 联合训练主干退化风险**：Table 2 直接联合训练（Direct Fine-tuning）质量 6.17→5.925，必须靠 combined loss + differential LR + heads warmup 三策略缓解，复杂度高于 MEDUSA-1。
- **头数与树规模权衡**：§2.2.3 经验取 5 头足够，配 §2.3.3 优化树后 3–4 头可能即够；但 **Figure 4b** 显示候选数 >150 后 speed 显著下降，**Figure 21** 显示 speedup 在 ~48–64 候选处饱和——树太大会被 compute-bound 反噬。
- **稀疏树假设独立**：§2.3.3 候选路径准确率按 `Π a^(i_j)_j` 独立假设估算（对应 formulas.json [5] 的连乘项），实际头间存在相关性，估计有偏（论文未给敏感性分析）。
- **自蒸馏质量下降**：Vicuna-33B acc rate 3.01 低于 7B/13B 的 3.47/3.51（Table 1），作者归因 hidden 训练数据与 seed 不匹配；自蒸馏需 LoRA 不量化，否则教师为量化模型质量降。
- **draft 路径命中是稀疏事件**：**Figure 6** M3 解读指出 64 节点 k^4 候选空间单次验证，性能强依赖是否有路径命中 ground truth——acceptance rate 是主导杠杆，高熵/创意任务收益低（Humanities/Reasoning 仅 2.58×）。
