# EAGLE-3: Scaling up Inference Acceleration of Large Language Models via Training-Time Test — 技术点深读（DEEP 2026-08-18）
> 全要素深读笔记。独立文件，extract_phase1 重跑不丢。
> 论文：EAGLE-3: Scaling up Inference Acceleration of Large Language Models via Training-Time Test · arXiv:2503.01840v3 (23 Apr 2025)
> 作者：Yuhui Li (PKU), Fangyun Wei (MSRA), Chao Zhang (PKU), Hongyang Zhang (Waterloo/Vector)
> 图表上下文来源：extraction/minimax_captions.json（6 张 figure 的 M3 caption，本文禁直读 PNG）

## 核心问题

LLM 社区的主流趋势是 **scaling up 训练数据**以提升模型智能（LLaMA 1/2/3 的 7B(8B) 训练数据从 1T → 2T → 15T tokens，§1），而推理成本几乎不变。EAGLE-3 的出发点是把这一思路移植到 speculative sampling 的 draft model 上——通过扩大 draft model 训练数据来提升接受率与加速比。

然而作者观察到关键反常现象（§1, Figure 1（p.1））：**对 EAGLE-1/2 的 draft model 增加训练数据，加速比几乎不涨**。M3 解读 Figure 1：EAGLE-2 的 speedup 曲线随数据规模 1×→8× 基本走平于 ~3.2–3.3，accept length 也平台化于 ~4.1；EAGLE-3 则单调上升（speedup ~3.7→4.4，accept length ~5.2→6.1）。M3 据此点出 EAGLE-2 的 feature-prediction 设计是数据红利的"饱和盖"。这是 EAGLE 系列继续提升的"scaling 天花板"。

根因分析（§1, Figure 3 上部（p.3））：EAGLE 在 **feature 层做自回归**——draft model 预测 next feature ˆf，再经 target model 的 LM head 得到 token 分布。其损失含两项：feature prediction loss `l_fea` + token prediction loss `l_token`。`l_fea` 让 draft model 仅在 Step 1 训练即可获得多步预测能力（好处），但 token prediction 才是终极目标，**feature prediction 实际上是额外约束**，压制了 draft model 的表达能力，使其无法从数据扩张中受益。

直接移除 `l_fea`（Figure 3 中部）会暴露新问题（M3 解读 Figure 3：此时 draft model 直接输出 unconstrained vector â，再过 LM head 出 token）：Step 1 输出的 ˆa_{t+1} 偏离 ground-truth f_{t+1}，使 Step 2 的输入序列 `f_1,…,f_t,ˆa_{t+1}` 落在训练分布之外，导致 **1-α（第二个 draft token 的接受率）骤降**（Figure 4）。这就是 train/inference context mismatch——训练时输入是 ground-truth feature，推理时输入是 draft model 自身的估计。

进一步约束（§1, §3.2）：EAGLE/Medusa 复用 target model 的 **top-layer feature**（LM head 前的 feature）。当 LM head 权重矩阵满秩时，top-layer feature 与 next-token logits 一一对应，因此它**本质只能承载 next-token 信息**——仅凭 top-layer feature 去预测 next-next token 信息量先天不足。要突破此瓶颈必须改用中间层 feature，但只有先移除 `l_fea`（不再要求 draft output 拟合 top-layer feature）才能解放对 feature 层级的选择。

## 关键创新点

1. **Training-time test（核心训练技术，§1, §3.2, Figure 3 底部（p.3）+ M3 要点）**。
   把推理时的多步生成过程**纳入训练**：训练时即执行 "test step"——draft model 生成 `a` 后，把 `a` 反馈回 draft model 自身作为下一步输入继续训练。M3 解读 Figure 3 强调存在一条"红色虚线 feedback loop"把 Step 1 的输出 â 喂回 Step 2，实现 end-to-end 多步监督。这使训练分布与推理分布对齐（推理时 Step 2+ 的输入也是 draft model 自己的输出 `a`），消除 train/inference mismatch。机制上：Step 1 用 ground-truth feature `g_1,…,g_t` 作输入；Step 2+ 用 `g_1,…,g_t, a_{t+1},…,a_{t+j}` 作输入，其中 `a` 是 draft model 前一步的输出。效果（Figure 4（p.4））：随数据规模 1×→8×，0-α 与 1-α 都显著上升，且 1-α 不再塌陷——数据规模红利被打开。

2. **移除 feature prediction 约束 + 直接 token 预测（§1, §3）**。
   去掉 `l_fea`，只保留 token prediction loss `l_token`；draft model 输出 `a`（unconstrained vector）经 LM head 直接得 token 分布。这给了 draft model input 完全自由（不再要求 ˆa≈top-layer f），是 training-time test 能 work 的前提，也是 multi-layer feature fusion 能 work 的前提（不再被 top-layer 唯一性锁定）。Ablation（Table 2）：在 EAGLE-2 基础上仅 +remove fea con，MT-bench 3.16x→3.82x（+0.66x），GSM8K 3.39x→3.77x（+0.38x）。

3. **Multi-layer feature fusion（§1, §3.1, Figure 5（p.4）+ M3 要点）**。
   从 target model 同时取 **low / middle / high-level feature** l, m, h（分别对应不同 decoder layer 的输出），各 k 维（k = hidden size），concat 成 3k 维向量，过一个 FC 层压回 k 维得到 fused feature `g`。M3 解读 Figure 5 指出：target-model 的 l_how/m_how/h_how、l_can/m_can/h_can 通过 FC 投影进统一 k 维 g，token embedding e 与 g 一并喂入每个 draft layer，实现 feature-level autoregression + context-aware dynamic tree（而非 EAGLE-2 的 static structure）。`g` 整合了不同层级的语义信息。只移除 `l_fea` 而仍用 top-layer feature，增益有限；multi-layer fusion 才把信息瓶颈真正打开。Ablation（Table 2）：在 +remove fea con 之上再 +fused features，MT-bench 3.82x→4.40x（再 +0.58x），GSM8K 3.77x→4.48x（再 +0.71x）。

4. **Inference pipeline 三步式 draft（§3.1, Figure 5（p.4）+ M3 要点）**。
   以 prefix "How can" 生成 draft "I do it …" 为例：
   - Prefill/上一次 verification 时 target model 前向，记录 l/m/h，融合得 `g_how, g_can`。
   - Step ①（M3 标注）：输入 `g_how, g_can` + sampled token "I" 的 embedding `e_I`（沿用 EAGLE-1 思路：把上一时间步的采样结果 token embedding 喂入 draft model，以补偿 token 层采样的不确定性），过 FC + 单层 decoder → 输出 `a_I`，过 LM head 采样得 draft token "do"。
   - Step ②：无法获得 target model 的 `g_I`（"I" 尚未验证），用 draft model 的 `a_I` 替代 `g_I`，与 `e_do` concat 作为输入 → 输出 `a_do` → "it"。
   - Step ③（M3 标注）：仅过 LM Head 对 features 展开多个并行子节点（can/I/do/it），完成 tree expansion。
   即 ground-truth fused feature `g` 与 draft 自身输出 `a` 在序列中交替出现，这正是 training-time test 所对齐的输入分布。

5. **Draft model 仅一层 Transformer decoder + 自注意力 mask 调整（§3.2, Figure 6（p.5））**。
   Draft model 核心是单层 Transformer decoder。除 self-attention 外无其他组件与 context 交互，故训练/测试时只需改 self-attention。原始训练数据（如 "How can I"）是顺序依赖，attention mask 为标准下三角；其输出 "are/we/do" 与 "how/can/I" 成树状依赖，喂入 Step 2 时 mask 改为 **diagonal**（除以原始训练数据为 key 的位置外）。用矩阵乘法在这些位置会造成计算浪费，故改用 **vector dot product** 只算对应位置的 attention score。M3 在 p.5 未能渲染 Figure 6 本体（仅见正文对 Figure 6 的两处文字引用），此处解读依正文 §3.2。注意：HASS 也做了类似 mask 修改以在训练中模拟测试过程，但论文强调这是**非 EAGLE-3 主要贡献**，二者动机/方法/结果完全不同（见对比节）。

6. **发现 inference acceleration 的 scaling law（§1, §4.1, Figure 1（p.1）+ M3 要点）**。
   在新架构下，**增加 draft model 训练数据 → speedup 比例成比例上升**，曲线单调上升——这是前作从未观察到的现象。M3 解读 Figure 1：EAGLE-2 speedup 平台于 ~3.2–3.3、accept length 平台于 ~4.1；EAGLE-3 speedup 从 ~3.7 升至 ~4.4、accept length 从 ~5.2 升至 ~6.1，斜率显著。论文用 ~8× 训练数据训练 EAGLE-3，并明确预期更大数据规模会进一步提升 speedup。

7. **兼容 EAGLE-2 的 dynamic draft tree（§1, §2.2）**。
   EAGLE-3 直接采纳 EAGLE-2 的 context-aware dynamic draft tree（基于 confidence 的 expansion + reranking，保证连通树）。EAGLE-3 的改进集中在 draft model **训练侧与输入特征构造**，与 EAGLE-2 的 tree-shape 优化正交、可叠加。Appendix A：EAGLE-3 因接受率更高，把 draft tree 深度从 EAGLE-2 的 6 提升到 **8**，节点总数保持不变。

8. **训练设置（§4 Implementation）**。
   AdamW，β=(0.9, 0.95)，gradient clipping 0.5，lr 5e-5。训练数据：ShareGPT（~68K）+ UltraChat-200K（~464K）——后者约是前者的 8×，对应 Figure 1 的 8× 数据点。对 reasoning model DeepSeek-R1-Distill-LLaMA 8B 额外用 OpenThoughts-114k-math。调用 target model 生成 response 而非用固定数据集（保证 draft 与 target 分布对齐）。

## 表格（原文结构化）

### Table 1 — Speedup / 平均接受长度 τ，temperature=0 与 temperature=1
（V=Vicuna, L31=LLaMA-Instruct 3.1, L33=LLaMA-Instruct 3.3, DSL=DeepSeek-R1-Distill-LLaMA；SpS=标准 speculative sampling 用 Vicuna-68M；Medusa 类在 non-greedy 放松接受条件不保证无损，故 T=1 不与之比较）

**Temperature=0**

| Model | Method | MT-bench Spd/τ | HumanEval Spd/τ | GSM8K Spd/τ | Alpaca Spd/τ | CNN/DM Spd/τ | Mean Spd/τ |
|---|---|---|---|---|---|---|---|
| V 13B | SpS | 1.93x / 2.27 | 2.23x / 2.57 | 1.77x / 2.01 | 1.76x / 2.03 | 1.93x / 2.33 | 1.92x / 2.24 |
| V 13B | PLD | 1.58x / 1.63 | 1.85x / 1.93 | 1.68x / 1.73 | 1.16x / 1.19 | 2.42x / 2.50 | 1.74x / 1.80 |
| V 13B | Medusa | 2.07x / 2.59 | 2.50x / 2.78 | 2.23x / 2.64 | 2.08x / 2.45 | 1.71x / 2.09 | 2.12x / 2.51 |
| V 13B | Lookahead | 1.65x / 1.69 | 1.71x / 1.75 | 1.81x / 1.90 | 1.46x / 1.51 | 1.46x / 1.50 | 1.62x / 1.67 |
| V 13B | Hydra | 2.88x / 3.65 | 3.28x / 3.87 | 2.93x / 3.66 | 2.86x / 3.53 | 2.05x / 2.81 | 2.80x / 3.50 |
| V 13B | EAGLE | 3.07x / 3.98 | 3.58x / 4.39 | 3.08x / 3.97 | 3.03x / 3.95 | 2.49x / 3.52 | 3.05x / 3.96 |
| V 13B | EAGLE-2 | 4.26x / 4.83 | 4.96x / 5.41 | 4.22x / 4.79 | 4.25x / 4.89 | 3.40x / 4.21 | 4.22x / 4.83 |
| V 13B | **EAGLE-3** | **5.58x / 6.65** | **6.47x / 7.54** | **5.32x / 6.29** | **5.16x / 6.17** | **5.01x / 6.47** | **5.51x / 6.62** |
| L31 8B | EAGLE-2 | 3.16x / 4.05 | 3.66x / 4.71 | 3.39x / 4.24 | 3.28x / 4.12 | 2.65x / 3.45 | 3.23x / 4.11 |
| L31 8B | **EAGLE-3** | **4.40x / 6.13** | **4.85x / 6.74** | **4.48x / 6.23** | **4.82x / 6.70** | **3.65x / 5.34** | **4.44x / 6.23** |
| L33 70B | EAGLE-2 | 2.83x / 3.67 | 3.12x / 4.09 | 2.83x / 3.69 | 3.03x / 3.92 | 2.44x / 3.55 | 2.85x / 3.78 |
| L33 70B | **EAGLE-3** | **4.11x / 5.63** | **4.79x / 6.52** | **4.34x / 6.15** | **4.30x / 6.09** | **3.27x / 5.02** | **4.12x / 5.88** |
| DSL 8B | EAGLE-2 | 2.92x / 3.80 | 3.42x / 4.29 | 3.40x / 4.40 | 3.01x / 3.80 | 3.53x / 3.33 | 3.26x / 3.92 |
| DSL 8B | **EAGLE-3** | **4.05x / 5.58** | **4.59x / 6.38** | **5.01x / 6.93** | **3.65x / 5.37** | **3.52x / 4.92** | **4.16x / 5.84** |

**Temperature=1**

| Model | Method | MT-bench Spd/τ | HumanEval Spd/τ | GSM8K Spd/τ | Alpaca Spd/τ | CNN/DM Spd/τ | Mean Spd/τ |
|---|---|---|---|---|---|---|---|
| V 13B | SpS | 1.62x / 1.84 | 1.72x / 1.97 | 1.46x / 1.73 | 1.52x / 1.78 | 1.66x / 1.89 | 1.60x / 1.84 |
| V 13B | EAGLE | 2.32x / 3.20 | 2.65x / 3.63 | 2.57x / 3.60 | 2.45x / 3.57 | 2.23x / 3.26 | 2.44x / 3.45 |
| V 13B | EAGLE-2 | 3.80x / 4.40 | 4.22x / 4.89 | 3.77x / 4.41 | 3.78x / 4.37 | 3.25x / 3.97 | 3.76x / 4.41 |
| V 13B | **EAGLE-3** | **4.57x / 5.42** | **5.15x / 6.22** | **4.71x / 5.58** | **4.49x / 5.39** | **4.33x / 5.72** | **4.65x / 5.67** |
| L31 8B | EAGLE-2 | 2.44x / 3.16 | 3.39x / 4.39 | 2.86x / 3.74 | 2.83x / 3.65 | 2.44x / 3.14 | 2.80x / 3.62 |
| L31 8B | **EAGLE-3** | **3.07x / 4.24** | **4.13x / 5.82** | **3.32x / 4.59** | **3.90x / 5.56** | **2.99x / 4.39** | **3.45x / 4.92** |
| L33 70B | EAGLE-2 | 2.73x / 3.51 | 2.89x / 3.81 | 2.52x / 3.36 | 2.77x / 3.73 | 2.32x / 3.27 | 2.65x / 3.54 |
| L33 70B | **EAGLE-3** | **3.96x / 5.45** | **4.36x / 6.16** | **4.17x / 5.95** | **4.14x / 5.87** | **3.11x / 4.88** | **3.95x / 5.66** |
| DSL 8B | EAGLE-2 | 2.69x / 3.41 | 3.01x / 3.82 | 3.16x / 4.05 | 2.64x / 3.29 | 2.35x / 3.13 | 2.77x / 3.54 |
| DSL 8B | **EAGLE-3** | **3.20x / 4.49** | **3.77x / 5.28** | **4.38x / 6.10** | **3.16x / 4.30** | **3.08x / 4.27** | **3.52x / 4.89** |

峰值：V13B HumanEval T=0 达 **6.47x / τ=7.54**（论文 abstract 与 §4.1 所称 6.5x 上限即此处）。Figure 2（p.2，M3 柱状图解读）确认 EAGLE-3 在四个目标模型上分别达 5.6x / 4.4x / 4.1x / 5.0x，全面最优，与 Table 1 数字一致。

### Table 2 — Ablation（LLaMA-Instruct 3.1 8B）
"remove fea con"=移除 feature prediction 约束；"fused features"=low/mid/high feature fusion 替代 top-layer feature

| Method | MT-bench Spd/τ | GSM8K Spd/τ |
|---|---|---|
| EAGLE-2 | 3.16x / 4.05 | 3.39x / 4.24 |
| + remove fea con | 3.82x / 5.37 | 3.77x / 5.22 |
| + fused features (EAGLE-3) | **4.40x / 6.13** | **4.48x / 6.23** |

两项改进各自有效且可叠加：remove fea con 贡献 +0.66x speedup / +1.32 τ（MT-bench），fused features 在其上再贡献 +0.58x / +0.76 τ。两项改进对应 Figure 3 中部与底部的两次范式跃迁（M3 解读）。

### Table 3 — SGLang v0.4.4 吞吐量提升（H100, LLaMA-Instruct 3.1 8B, MT-Bench，无 tree 结构，chain length=3；baseline=SGLang w/o spec=1.00x）

| Batch size | 2 | 4 | 8 | 16 | 24 | 32 | 48 | 56 | 64 |
|---|---|---|---|---|---|---|---|---|---|
| EAGLE | 1.40x | 1.38x | 1.23x | 1.02x | 0.93x | 0.94x | 0.88x | 0.99x | 0.99x |
| EAGLE-3 | 1.81x | 1.82x | 1.62x | 1.48x | 1.39x | 1.32x | 1.38x | 1.34x | **1.38x** |

关键观察：EAGLE 在 batch=24 起就跌破 1.0x（即 spec 反而降吞吐）；EAGLE-3 在 batch=64 仍保持 1.38x，即 **40% 吞吐提升**（abstract 所称）。EAGLE-3 的优势随 batch 增大收窄但仍为正，说明 training-time test 在 memory-bound 减弱场景下仍能产出更高质量的 draft。

### Table 4 — SGLang bs=1 吞吐（H100, LLaMA-Instruct 3.1 8B, MT-bench）

| Method | Throughput (bs=1) |
|---|---|
| SGLang (w/o speculative, 1x H100) | 158.34 tokens/s |
| SGLang + EAGLE-2 (1x H100) | 244.10 tokens/s |
| SGLang + EAGLE-3 (1x H100) | **373.25 tokens/s** |

EAGLE-3 vs EAGLE-2 在 SGLang bs=1 上吞吐比 ≈ 1.53x，与 latency speedup 4.40x vs 3.16x（≈1.39x）的差距说明 EAGLE-3 在 SGLang 上获得了超越纯接受率提升的额外工程收益。

### Table 5 — vLLM 吞吐量提升（A100, LLaMA-Instruct 3.1 8B, MT-Bench，无 tree 结构，max chain length=2；baseline=vLLM w/o spec=1.00x）

| Batch size | 2 | 4 | 8 | 16 | 24 | 32 | 48 | 56 |
|---|---|---|---|---|---|---|---|---|
| EAGLE | 1.30x | 1.25x | 1.21x | 1.10x | 1.03x | 0.93x | 0.82x | 0.71x |
| EAGLE-3 | 1.75x | 1.68x | 1.58x | 1.49x | 1.42x | 1.36x | 1.21x | **1.01x** |

EAGLE 的吞吐峰值在 batch=24，EAGLE-3 的峰值推迟到 batch=56——EAGLE-3 的有效 batch 窗口更宽，在更大 batch 下仍维持正收益。

### Figure 1（结构化，p.1，M3 解读）— Scaling law（LLaMA-Instruct 3.1 8B, MT-bench）

| 数据规模 (×ShareGPT) | EAGLE-2 Speedup | EAGLE-3 Speedup | EAGLE-2 AcceptLen | EAGLE-3 AcceptLen |
|---|---|---|---|---|
| 1 | ~3.2x | ~3.7x | ~4.1 | ~5.2 |
| 2 | ~3.2x | ~3.9x | ~4.1 | ~5.5 |
| 4 | ~3.3x | ~4.1x | ~4.1 | ~5.8 |
| 8 | ~3.3x | ~4.4x | ~4.1 | ~6.1 |

M3 解读要点：EAGLE-2 双曲线近水平（speedup 平台 ~3.2–3.3，accept length 平台 ~4.1）；EAGLE-3 双曲线单调上升（speedup ~3.7→4.4，accept length ~5.2→6.1）。M3 据此判定 EAGLE-2 的 feature-prediction 设计导致数据饱和，EAGLE-3 的 direct token prediction + multi-layer fusion 解锁了 monotonic scaling。

### Figure 4（结构化，p.4）— 接受率 vs 数据规模（LLaMA-Instruct 3.1 8B, MT-bench）

| 数据规模 | EAGLE 0-α | EAGLE w/o fea pred 0-α | EAGLE-3 0-α | EAGLE 1-α | EAGLE w/o fea pred 1-α | EAGLE-3 1-α |
|---|---|---|---|---|---|---|
| 1× | ~0.78 | ~0.78 | ~0.78 | ~0.72 | ~0.25 (塌陷) | ~0.70 |
| 2× | ~0.78 | ~0.79 | ~0.79 | ~0.71 | ~0.30 | ~0.72 |
| 4× | ~0.78 | ~0.79 | ~0.79 | ~0.70 | ~0.40 | ~0.75 |
| 8× | ~0.79 | ~0.80 | ~0.80 | ~0.70 | ~0.55 | ~0.78 |

核心证据：(a) 仅 remove fea pred（中段）时 0-α 上升但 1-α 在 1× 处塌到 ~0.25，验证 train/inference mismatch；(b) training-time test（EAGLE-3）下 1-α 与 0-α 接近且随数据同步上升——mismatch 被消除。

### Figure 7（结构化，p.8，M3 解读）— 接受率 vs 估计特征数 n（LLaMA-Instruct 3.1 8B, MT-bench）

| n (输入中估计 feature 数) | EAGLE 接受率 | EAGLE-3 接受率 |
|---|---|---|
| 0 | ~0.71 | ~0.79 |
| 1 | ~0.69 | ~0.79 |
| 2 | ~0.66 | ~0.78 |
| 3 | ~0.62 | ~0.78 |
| 4 | ~0.58 | ~0.77 |
| 5 | ~0.55 | ~0.77 |
| 6 | ~0.52 | ~0.76 |
| 7 | ~0.53 (微回升) | ~0.76 |

M3 解读要点：EAGLE 从 ~0.71 单调衰减至 ~0.52（6-α），7-α 处轻微回升；EAGLE-3 全程持平于 ~0.76–0.79。M3 据此判定 multi-layer fusion + 移除 feature-prediction 约束使 EAGLE-3 能支撑长 speculative chain（长链是 4.40x MT-bench speedup 的前提）。

## 与同类对比

- **vs EAGLE-1（[[eagle-speculative-sampling-requires-rethinking-feature-uncertainty]]）**：EAGLE-1 的特征级自回归 + `l_fea` 是 EAGLE-3 的直接改造对象。EAGLE-1 用 top-layer feature + feature prediction loss；EAGLE-3 移除 `l_fea`、改 multi-layer fusion、加 training-time test。V13B T=0 MT-bench：EAGLE 3.07x → EAGLE-3 5.58x（+2.51x）。EAGLE-3 沿用 EAGLE-1 的"喂入上一时间步 token embedding 以补偿采样不确定性"设计（§3.1）。Figure 3（p.3，M3）完整对照了 EAGLE / EAGLE-without-fea-pred / EAGLE-3 三种范式。
- **vs EAGLE-2（[[eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees]]）**：EAGLE-2 改 tree **结构**（dynamic tree），EAGLE-3 改 draft model **训练与输入特征**。两者正交且可叠加——EAGLE-3 直接采纳 EAGLE-2 的 dynamic tree。V13B T=0 Mean：EAGLE-2 4.22x → EAGLE-3 5.51x（+1.29x，约 +30%）；L33 70B T=0 Mean：2.85x → 4.12x（+45%）。论文 abstract 概括为"约 1.4x over EAGLE-2"。Figure 2（p.2，M3 柱状图）直观呈现此差距。
- **vs HASS**：最易混淆的对比对象。HASS 也修改 self-attention mask 在训练中模拟测试过程，但 (a) 动机不同：HASS 缓解 EAGLE feature prediction 不准的 **error accumulation**，EAGLE-3 移除约束提升 **表达能力**；(b) 方法不同：HASS 仍保留 `l_fea`、输入必须是 top-layer feature，EAGLE-3 移除 `l_fea`、输入自由、改 multi-layer fusion；(c) 结果不同：EAGLE-3 显著优于 HASS（Figure 2 中 V13B 5.6x vs HASS ~3.1x）。EAGLE-3 明确指出"mask 修改不是 EAGLE-3 的主要关注点"（§3.2）。
- **vs Medusa（[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]）**：Medusa 用 multiple decoding heads 并行预测多 token、static tree，且在 non-greedy 下放松接受条件（不保证无损）。EAGLE-3 用单层 decoder + dynamic tree + 严格接受条件（lossless），V13B T=0 Mean 5.51x vs Medusa 2.12x。
- **vs Hydra**：Medusa 的 sequentially-dependent heads 升级版，仍 static tree。EAGLE-3 V13B T=0 5.51x vs Hydra 2.80x。
- **vs Lookahead**：Jacobi 迭代、无神经网络 draft model，τ 短（~1.67）。EAGLE-3 V13B T=0 5.51x vs 1.62x。
- **vs 标准 SpS（Vicuna-68M draft）**：标准 speculative sampling 需独立训练小 LLM 作 draft（pretrain+SFT 成本高）。EAGLE-3 仅训单层 decoder，V13B T=0 5.51x vs SpS 1.92x。但 SpS 在 QA/摘要任务相对下滑较小（仍受 draft model 知识面限制，见局限）。
- **vs DeepSeek-v3 multi-token prediction**：§2.2 提到 EAGLE 启发了 DeepSeek-v3 pretraining 的 multi-token prediction 技术，后者反过来启发了 EAGLE-3 的架构设计——存在双向灵感回流。
- **vs self-speculative / layer-skip 类（GLIDE/CAPE, Kangaroo, Draft & Verify, LayerSkip, Triforce, SpecExec, PASS）**：这类方法复用 target model 的 KV cache 或通过 layer skipping/early exit 复用 target model 部分参数作 draft。EAGLE-3 走独立 draft model 路线（单层 decoder），不复用 target model 参数做 layer-skip，但复用 target model 的 feature `g` 作输入信息源（§5）。

## 跨论文关系（→ MOC 谱系）

EAGLE-3 位于 **speculative feature-prediction 分支**的 **training-time scaling step**：

- **[[eagle-speculative-sampling-requires-rethinking-feature-uncertainty]]**（EAGLE-1，前身）：EAGLE-3 直接 build upon 并改造其核心设计。EAGLE-1 的 feature-level AR + `l_fea` + top-layer feature reuse 是 EAGLE-3 的"被改造对象"。EAGLE-3 沿用 EAGLE-1 的 token-embedding-as-input 设计（补偿采样不确定性，§3.1），但替换其 feature prediction 范式。Figure 3（p.3，M3）完整对照了 EAGLE / EAGLE-3 / EAGLE-without-fea-pred 三种范式。
- **[[eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees]]**（EAGLE-2，前代）：EAGLE-3 采纳 EAGLE-2 的 dynamic draft tree（expansion + reranking + confidence-based pruning），改进集中在 draft model 训练侧与输入特征构造。两者改进维度正交，EAGLE-3 把 draft tree 深度从 EAGLE-2 的 6 提升到 8（Appendix A）。谱系：EAGLE-1 feature AR → EAGLE-2 dynamic tree → **EAGLE-3 training-time scaling**。
- **[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]**（Medusa，多头前身）：Medusa 的 multi-head static tree + top-layer feature reuse 思路被 EAGLE 系列吸收并改造。EAGLE-3 进一步放弃 top-layer feature 限制，证明 multi-layer fusion 优于单层 top-layer。
- **[[deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference]]**（DeFT，tree-attention kernel）：EAGLE-3 沿用 tree attention 验证（继承自 EAGLE-1/2），draft tree 深度增至 8 后 tree-attention 计算开销上升，DeFT 类高效 tree-attention kernel 可作为 EAGLE-3 verification stage 的 drop-in 加速器。
- **[[sglang-efficient-execution-of-structured-language-model-programs]]**（SGLang，生产级推理框架）：EAGLE-3 已被 SGLang 团队集成评估（§4.3, Table 3/4），在 H100 bs=1 上达 373.25 tokens/s，bs=64 仍 1.38x 吞吐提升。EAGLE-3 是 SGLang 生态的 spec-decoding 后端之一。
- **[[efficient-memory-management-for-large-language-model-serving-with-pagedattention]]**（vLLM/PagedAttention）：EAGLE-3 在 vLLM 上评估大 batch 吞吐（§4.4, Table 5），EAGLE-3 把正收益窗口从 EAGLE 的 batch≤24 推到 batch≤56。

谱系定位：speculative decoding → tree-structured draft → feature-level autoregression (EAGLE-1) → context-aware dynamic tree (EAGLE-2) → **training-time scaling + multi-layer fusion (EAGLE-3, 本文)**。

## 局限与边界

1. **Scaling law 仅在 ≤8× 数据范围内验证（§1, Figure 1（p.1））**。论文观察到 1×→8× 数据的 speedup 单调上升（M3 解读 EAGLE-3 ~3.7→4.4），但 8× 之后曲线是否饱和、何时饱和未给出。作者仅"预期更大数据规模会进一步提升"，未提供外推的理论依据或上界分析。UltraChat-200K（~464K entries）已是当前可用的较大开源对话数据，再扩大数据规模受限于数据获取。

2. **未在 405B / 671B 超大模型上测试（§4）**。明确说明 "Due to the GPU constraint, we are unable to test EAGLE-3 on the 405B and 671B models"。最大测试模型为 LLaMA-Instruct 3.3 70B 与 DeepSeek-R1-Distill-LLaMA 8B。EAGLE-3 在超大模型上的 scaling 行为（draft model 容量是否足够、multi-layer fusion 的层选择策略是否仍有效）未验证。

3. **QA / 摘要任务的相对短板未解决（§4.1, Table 1）**。EAGLE-3 在 CNN/DM 上 speedup 最低（V13B T=0：5.01x vs HumanEval 6.47x）。这继承自 EAGLE 系列的固有短板——draft model 用 SFT 数据训练，世界知识/摘要依赖 pretraining 知识。EAGLE-3 的 training-time test 与 multi-layer fusion 提升 draft model 表达力，但无法补足 draft model 训练数据本身的知识缺口。DSL 8B 上 GSM8K 反超其他任务（5.01x）是因为额外用了 OpenThoughts-114k-math 训练——这反证了"任务特定数据有效但通用知识仍是瓶颈"。

4. **Multi-layer feature fusion 的层选择未给出原则（§3.1, Figure 5（p.4））**。论文说取 low/mid/high 三层特征 l/m/h，但**如何选择具体哪三层**、为何三层而非更多/更少、不同 target model 的最优层选择是否一致，均未讨论。FC 层把 3k→k 的融合是简单线性投影（M3 解读 Figure 5 确认为 FC projection），未探索更复杂的融合机制（如 gated/attention-based fusion）。这是工程化的可优化空间，但也是泛化到新模型族时的不确定性来源。

5. **Draft tree 深度 8 的设定缺乏自适应（Appendix A）**。EAGLE-3 因接受率提升把深度从 6 增到 8，但仍为**手工设定的全局常量**，未随上下文/任务自适应。不同任务（HumanEval vs CNN/DM）的最佳深度可能不同，论文未做深度敏感性分析。

6. **大 batch 下收益仍收窄（Table 3, 5）**。EAGLE-3 在 SGLang batch=64 仍 1.38x，但相比 batch=2 的 1.81x 已下降 23%。speculative sampling 在大 batch 下 memory-bound 优势减弱是共性，EAGLE-3 缓解但未根本解决。在 batch>64 的生产场景（如高并发服务）下收益是否仍为正未测试。

7. **Training-time test 的训练成本与稳定性未详述**。训练时需执行多步 test step（生成 `a` 并反馈），相比 EAGLE 单步训练有额外开销；论文未给出训练时间对比、收敛步数、test step 数量对效果的影响。多步训练是否引入梯度不稳定、是否需要特殊学习率调度未讨论。

8. **Lossless 性质继承自严格接受条件，依赖实现正确性**。EAGLE-3 不改 target model 权重、用严格 speculative sampling 接受条件（§4 Metrics），理论上 lossless。但 training-time test 引入的多步训练 + diagonal mask + vector dot-product attention 是新的实现面，工程 bug 会破坏分布等价性——属实现风险而非理论局限。

9. **与 HASS 的边界划分依赖叙述而非消融（§3.2）**。EAGLE-3 强调自身与 HASS 的 mask 修改"动机/方法/结果不同"，但未在 ablation 中隔离"mask 修改"本身的贡献。Table 2 的 ablation 只拆 remove fea con 与 fused features 两项，未拆 mask 修改——故 mask 修改的边际贡献无法从论文数据中量化。

10. **Figure 6 缺失 M3 视觉验证（p.5）**。M3 caption 在 p.5 未能渲染 Figure 6 本体（仅见正文文字引用），本文对 Figure 6（attention mask 三阶段：native training step + 两轮 simulated training step）的解读完全依正文 §3.2 文字，未经图像二次校验。
