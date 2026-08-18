# EAGLE: Speculative Sampling Requires Rethinking Feature Uncertainty — 技术点深读（DEEP 2026-08-18）
<!-- 独立文件：extract_phase1 重跑不覆盖；深读内容只存活于此文件 + moc_relations.md -->
> 论文：EAGLE: Speculative Sampling Requires Rethinking Feature Uncertainty · arXiv:2401.15077v3 (4 Mar 2025)
> 作者：Yuhui Li, Fangyun Wei, Chao Zhang, Hongyang Zhang (PKU / Microsoft Research / Waterloo / Vector Institute)
> 代码：https://github.com/SafeAILab/EAGLE
> 图表解读来源：extraction/minimax_captions.json，key 前缀 `extraction/assets/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-p`（共 7 张，p01/02/03/04/07/08/12）。

## 核心问题

Speculative sampling（Leviathan et al., 2023; Chen et al., 2023a）通过「低开销 draft + 单次 forward 并行 verify」把 LLM 自回归解码从每 forward 1 token 提到多个 token，且理论上保证输出分布不变。但其加速依赖两点：**draft 模型延迟低** + **draft 接受率高**。EAGLE 聚焦三个痛点（§1, §5），三者均可在 Figure 1（p.1, M3：bar chart，6 方法 × 6 模型，EAGLE 蓝柱 2.78–3.07x 全列最高，Speculative sampling 在 7B 标 N/A、13B 仅 1.00x）与 Figure 2（p.2, M3：T=1 非贪婪设定，LC 7B 仅 2.68x、所有模型降到 2.06–2.68x）中直观读到：

1. **小模型 draft 难寻**：LLaMA2-Chat 系列仅 7B/13B/70B，7B 无更小同系列 draft；TinyLLaMA-Chat 指令模板不匹配 instruct 模型；用 7B 给 13B 做 draft 因开销过大反而比 vanilla 还慢（Figure 1 中 13B 的 Speculative sampling = 1.00x，7B 全标 N/A）。训练专用 draft 模型成本高（TinyLLaMA 用 3000B tokens vs EAGLE 仅 2–4B tokens，§1）。
2. **现有低开销 draft 精度不足**：Lookahead（n-gram + Jacobi）和 Medusa（MLP 头直接预测 token）接受率分别约 0.6 和更低，限制加速上限（§1: "Medusa achieving an accuracy of about 0.6 … our method attains an accuracy of approximately 0.8"）。
3. **Medusa 非贪婪下不保证无损**，Lookahead 仅支持 greedy（§1, Figure 2 caption: "Lookahead is confined to greedy decoding, and the non-greedy generation of Medusa does not guarantee lossless performance"）——分布保持的可靠性缺口。

EAGLE 的核心追问：能否在 draft 阶段做特征级自回归（而非 token 级），同时解决特征预测中由采样引入的不确定性，从而既低开销又高接受率且 distribution-preserving？

## 关键创新点

1. **特征（second-to-top-layer）级自回归取代 token 级**（§1, §3.1, Figure 4（p.3））。"feature" 指 LM head 之前的第二顶层 hidden state。论据：token 是自然语言的简单变换、离散且不规则；feature 序列更 regular，自回归更易学。Figure 4（M3：两条曲线随 epoch 上升，feature 曲线高于 token 曲线，token 曲线近乎平坦）的消融把 Vicuna 7B speedup 从 token-based 的 1.5x 提到 1.9x（§1: "1.9x compared to 1.5x"）。draft token 由 target LLM 的 LM Head 从预测 feature 直接算分布采样，保证 draft 与 target 同分布空间。

2. **"shifted-token" 超前一拍消除采样不确定性**（§1, §3.1, Figure 3（p.2）, Figure 4）——EAGLE 的命名性创新。问题（Figure 3, M3：以 `f_I` 为根，分叉为 am（p=0.6）→ f_am → excited/ready 与 always（p=0.4）→ f_always → begin/look，两支并行）说明给定 `f_I`，下一 feature 取决于采样结果，导致 feature 序列分叉，draft 模型对 `f_I` 的回归目标在 `p_am` 与 `p_always` 间二义。Medusa 同样面临 spaced-token 预测的二义性。EAGLE 解法：把**已经采样出的下一 token**（超前 feature 一个时间步的 token 序列 `T_{2:i+1}`）作为 draft 输入，于是 `f_{i+1}` 的预测条件包含采样结果 `t_{i+1}`，二义消解。公式见 §3.2 训练目标。Figure 4（M3：feature&shifted-token 蓝线在 acc 与 speedup 双图均居顶）的消融把 speedup 从 1.9x 进一步推到 2.8x（§1: "from 1.9x to 2.8x"）——单这一步贡献 ~0.9x 增益。注意：feature&unshifted-token（不超前）虽融合语义但无法消解随机性，1-α 改善但 0-α 与 feature-only 相近（§4.3.2, Figure 8（p.8, M3：2×4 grid，T=0/T=1 × Speedup/τ/0-α/1-α，feature&shifted-token 蓝线在所有 8 子图均居顶，token 绿线垫底））。

3. **极轻量 draft 架构 = 1 个 transformer decoder layer + FC**（§3.1, Figure 6（p.4, M3：三模块——冻结的 Embedding 与 LM Head（雪花图标）+ 可训练 Autoregression Head；输入 token→embedding 与 feature concat 成 2×hidden_dim，FC 降维→decoder layer 预测下一 feature→LM Head 采样多候选；3 次 forward 生成 10-token 树））。draft 模型仅 3 模块：Embedding 层、LM Head（均复用 target LLM 参数，不训练）、Autoregression Head（FC 降维 + 单 decoder layer，唯一可训练部分）。可训练参数规模：7B→0.24B，13B→0.37B，33B→0.56B，70B→0.99B，Mixtral 8x7B→0.28B（§4 Training）。对比 TinyLLaMA 训练用 3000B tokens，EAGLE 仅用 2-4B tokens（§1）。

4. **Tree attention + 多路 draft 树**（§3.1, §3.3, Appendix A.1, Figure 6, Figure 9（p.12, M3：左树根节点 k=4，分支不对称——左支最深约 5 层、最宽，右支快速终止；右图为无 tree attention 的线性链））。draft 阶段经 m 次 forward 生成深度 m、节点数 > m 的树（Figure 6 示例：3 次 forward 生成 10-token 树）。verify 阶段 target LLM 单次 forward 算树上所有 token 概率。树结构按直觉设计、未严格优化（§A.1: "not rigorously optimized but rather based on intuition"）。消融（§4.3.1, Table 5, Figure 7（p.7, M3：分组柱状图，w/ tree 蓝柱 2.78–3.07x，w/o tree 绿柱 2.27–2.66x，Vanilla 橙柱 1.00x））：tree vs chain 平均接受长度 τ 提升 +0.62~+0.75（Vicuna 7B: 3.20→3.94），speedup +0.3~0.5；不增 forward 次数，仅增每 forward 的 token 数。即使无 tree（chain-only），EAGLE 仍达 2.3x-2.7x（§4.3.1）。

5. **组合损失：回归 + 分类**（§3.2）。draft 的中间目标是预测 feature（回归），最终目标是 token（分类）。`L_reg = SmoothL1(f_{i+1}, Draft(T_{2:i+1}, F_{1:i}))`；`p_{i+2}=Softmax(LM_Head(f_{i+1}))`，`p̂_{i+2}=Softmax(LM_Head(f̂_{i+1}))`，`L_cls = CrossEntropy(p_{i+2}, p̂_{i+2})`。联合 `L = L_reg + w_cls·L_cls`，`w_cls=0.1`（因分类损失数值上比回归大约一个数量级）。注意分类目标是 target LLM 自家 LM_Head 上的分布，蒸馏对齐。

6. **数据增强对抗特征误差累积**（§3.2）。draft 阶段自回归处理 feature，feature 误差会累积。训练时对 target LLM 的 feature 加 `U(-0.1, 0.1)` 均匀噪声（借鉴 NEFTune, Jain et al. 2023），提升对失真 feature 的鲁棒性。对应 Table 2 中 1-α 到 4-α 几乎不衰减的现象（§4.1: "slight variation between 1-α to 4-α underscores EAGLE's robustness to feature errors"）。

7. **训练数据低敏感性 → 固定数据集即可**（§3.2, §4.3.3, Table 6）。理想训练数据应是 target LLM 自回归生成的文本，但成本高。Table 6：固定 ShareGPT 数据集 vs 用 target LLM 生成答案，speedup 2.78x vs 2.88x、τ 3.62 vs 3.75——增益微弱，故 EAGLE 全部实验统一用 ShareGPT 68k 对话训练，zero-shot 评测 MT-bench/GSM8K/HumanEval/Alpaca（§4.3.3）。训练配置：lr 3e-5，AdamW β=(0.9, 0.95)，grad clip 0.5，1-2 天 / 4×A100 40G（70B）。

8. **Multi-round speculative sampling 保证树形 draft 下分布不变**（§3.3, Appendix A.2, Algorithm 1（p.12））。树形 draft 有 k 个候选 token，标准 speculative sampling 的 reject-after-sample 不够。Algorithm 1：对 k 个 token 依次按 `min(1, p(t_i)/p̂(t_i))` 接受；拒绝时不直接从调整分布 `norm(max(0, p−p̂))` 采样，而是**递归调用 A**；全拒才直接采样。与 SpecInfer 一致，保证输出分布 = target LLM 分布，greedy 与 non-greedy 均成立（§1, §3.3）。

## 表格（原文结构化）

### Table 1 — Speedup & τ on HumanEval / GSM8K / Alpaca（§4.1）
T=0 下 LC 13B HumanEval 最高 speedup **3.76x** / τ 4.52；T=1 各模型普遍降到 2.2x-2.9x。代码任务（HumanEval）因模板固定加速最佳。

| Model | HumanEval Sp/τ | GSM8K Sp/τ | Alpaca Sp/τ |
|---|---|---|---|
| V 7B (T=0) | 3.33x / 4.29 | 3.01x / 4.00 | 2.79x / 3.86 |
| V 13B (T=0) | 3.58x / 4.39 | 3.08x / 3.97 | 3.03x / 3.95 |
| V 33B (T=0) | 3.67x / 4.28 | 3.25x / 3.94 | 2.97x / 3.61 |
| LC 7B (T=0) | 3.17x / 4.24 | 2.91x / 3.82 | 2.78x / 3.71 |
| LC 13B (T=0) | 3.76x / 4.52 | 3.20x / 4.03 | 3.01x / 3.83 |
| LC 70B (T=0) | 3.52x / 4.42 | 3.03x / 3.93 | 2.97x / 3.77 |
| V 7B (T=1) | 2.39x / 3.43 | 2.34x / 3.29 | 2.21x / 3.30 |
| LC 70B (T=1) | 2.92x / 3.76 | 2.74x / 3.58 | 2.65x / 3.47 |

### Table 2 — τ & n-α on MT-bench（§4.1）
揭示误差累积鲁棒性：0-α 显著高于 1-α（如 V7B T=0: 0.79→0.74），但 1-α→4-α 几乎平（0.74→0.67），证实数据增强 + shifted-token 抑制了误差传播。

| Model | τ | 0-α | 1-α | 2-α | 3-α | 4-α |
|---|---|---|---|---|---|---|
| V 7B (T=0) | 3.94 | 0.79 | 0.74 | 0.72 | 0.73 | 0.67 |
| LC 70B (T=0) | 3.81 | 0.75 | 0.69 | 0.65 | 0.64 | 0.64 |
| V 7B (T=1) | 3.17 | 0.71 | 0.68 | 0.66 | 0.66 | 0.65 |
| LC 70B (T=1) | 3.46 | 0.73 | 0.67 | 0.64 | 0.66 | 0.65 |

### Table 3 — Mixtral 8x7B Instruct（§4.1）
Speedup 仅 **1.50x** / τ 3.25。原因：MoE vanilla 只读 2 个 expert，speculative verify 多 token 可能触发 >2 expert，相对 dense 模型（无论如何都读全 weight）的相对优势减弱。

### Table 4 — EAGLE + gpt-fast（§4.2, §1）
单 RTX 3090，LLaMA2-Chat 7B，T=0。Vanilla HF FP16 24.5 tok/s；gpt-fast int4 106.9；**EAGLE+gpt-fast int4 = 160.4 tok/s**。证明 EAGLE 与量化+编译正交叠加。

### Table 5 — Tree vs Chain τ（§4.3.1, MT-bench T=0）
| Model | Chain τ | Tree τ (Δ) |
|---|---|---|
| V 7B | 3.20 | 3.94 (+0.74) |
| V 13B | 3.23 | 3.98 (+0.75) |
| V 33B | 2.97 | 3.68 (+0.71) |
| LC 7B | 3.00 | 3.62 (+0.62) |
| LC 13B | 3.18 | 3.90 (+0.68) |
| LC 70B | 3.12 | 3.81 (+0.69) |

### Table 6 — 训练数据敏感性（§4.3.3, LC 7B, T=0）
固定 ShareGPT：2.78x / τ 3.62；target LLM 生成答案：2.88x / τ 3.75。差 ~0.1x → 选固定数据集降成本。

### Table 7 — Batch size & Throughput（§4.4, MT-bench T=0）
| bs | 1 | 2 | 3 | 4 | Throughput |
|---|---|---|---|---|---|
| V 7B | 2.90x | 2.87x | 2.65x | 2.76x | 1.97x |
| LC 70B | 3.01x | 2.81x | 2.50x | 2.40x | 1.99x |

显存约束：单 RTX 3090 24G 下 V 7B vanilla bs_max=8 / EAGLE=7；4×A100 160G 下 LC 70B vanilla=5 / EAGLE=4。EAGLE 显存略高。Throughput（取各自最大 bs）翻倍。bs=4 > bs=3 反常：因 verify 阶段多 token 并行在 bs=4 更充分。

### Table 8 — HumanEval/GSM8K/Alpaca 详细 α（Appendix B, T=0）
（节选）LC 13B HumanEval 0-α=0.85, 4-α=0.75（最强鲁棒性）；LC 70B GSM8K 0-α=0.77→4-α=0.60（衰减最大）。

## 与同类对比

- **vs Medusa**（[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]）：Medusa 用一组 MLP **独立**预测 t4、t5（基于同一 f2，无自回归链），feature 复用但 token 间无依赖，且 non-greedy 不保证无损（用 hard threshold + entropy 截断）。EAGLE：feature 级**自回归链**（f3→f4 串联预测）+ shifted-token 消二义 → 接受率 0.8 vs 0.6，speedup 1.5-1.6x 优于 Medusa（§1, §5）。EAGLE draft token 经 target LM_Head 采样，分布天然对齐。Figure 1（p.1, M3）直观显示 EAGLE 蓝柱（2.78–3.07x）全面高于 Medusa 橙柱（1.92–1.97x，仅 Vicuna 系列）。
- **vs Lookahead**（n-gram + Jacobi）：仅支持 greedy；token 级预测精度低。EAGLE 比 Lookahead 快 1.7-2.1x（§6）。Figure 1（p.1, M3）中 Lookahead 仅 1.45–1.64x（LLaMA2-Chat 系列）。
- **vs 经典 Speculative Sampling**（Leviathan）：用同系列小 LLM 做 draft，7B 无可用 draft、13B 无增益（Figure 1 中 1.00x）、33B/70B 仅 1.12x/1.88x（§4.1）；EAGLE 单 decoder layer draft 开销极低、接受率高 → 全面碾压。
- **vs DistillSpec**：用 FKL 蒸馏改接受率，但 draft 开销才是瓶颈，增益有限（§4.1: "limited enhancement … bottleneck lies in the high overhead of the draft model"）。Figure 1（p.1, M3）中 DistillSpec 仅 1.12–2.13x。
- **vs lossy 方法**（DistillSpec lenience / BiLD 距离阈值 / Medusa 截断）：EAGLE **不引入任何 relaxation**，greedy & non-greedy 均理论无损（§5）。

## 跨论文关系（→ MOC 谱系）

- **[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]** — 直接前身。EAGLE 继承 Medusa「复用 target LLM feature、不另起小 LLM」的范式，但把多头独立预测改为单头特征级自回归 + shifted-token，并补上 Medusa 缺失的无损 non-greedy 保证。EAGLE 在 feature-prediction 分支上取代 Medusa 成为新 anchor。Figure 5（p.4，方法对比示意图）直观对照：Medusa Head1/Head2 独立、EAGLE 单 Autoregression Head 串联。
- **[[eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees]]** — EAGLE 的直接 follow-up。EAGLE-2 把 EAGLE 的静态直觉树结构（Figure 9（p.12, M3：根 k=4、分支不对称、高概率支更深更宽）, 论文自承 "not rigorously optimized"）升级为**动态、context-dependent draft tree**，正是 EAGLE §A.1 末尾点名的改进方向。
- **[[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]]** — EAGLE 系列第三代，沿 feature-prediction + tree draft 路线 scale up。
- **[[deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference]]** — EAGLE 依赖 tree attention（§3.1, §3.3, Figure 6/9），DEFT 提供更高效的 tree-attention kernel，是 EAGLE 系列底层 verify 阶段的潜在加速器。
- **[[jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting]]** — 同属 tree-drafting 谱系，但 JETSPEC 走 parallel tree drafting 突破 scaling 上限；EAGLE 是 single-draft-model + tree 的基础形态，JETSPEC 可视为 tree-drafting 的 scaling 延伸。
- **[[dflash-block-diffusion-for-flash-speculative-decoding]] / [[dspark-confidence-scheduled-speculative-decoding-with-semi-autoregressive-generation]]** — 同 KB 内的 speculative 变体，分别走 block-diffusion 与 confidence-scheduled semi-AR 路线，与 EAGLE 的 feature-AR + tree 路线互补对照。
- **[[longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification]] / [[specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences]]** — 长上下文场景的 speculative 扩展，EAGLE 的 feature-level drafting 可作为其 draft 模块候选。
- **谱系定位**：speculative decoding genealogy 中，EAGLE 是 **feature-prediction 分支的 anchor**——上游 Medusa（多头 token 预测，奠定 feature 复用），EAGLE 自身（feature-AR + shifted-token 消不确定 + tree），下游 EAGLE-2/3（动态树 + scaling），横向伴生 DEFT（tree kernel）、JETSPEC（parallel tree）。

## 局限与边界

1. **MoE 加速受限**（§4.1, Table 3）：Mixtral 8x7B 仅 1.50x。MoE vanilla 只读 2 expert，verify 阶段多 token 可能触发 >2 expert，相对 dense 模型的算力复用红利缩水。
2. **树结构未优化**（§A.1, Figure 9（p.12, M3：不对称树））：Figure 9 的树是直觉设定（高概率分支更深更宽），"not rigorously optimized"；作者承认最优树 context-dependent（batch 大时小树更优），为 EAGLE-2 的改进留口。
3. **batch size 增大收益递减**（§4.4, Table 7）：bs=1→4，V 7B 2.90x→2.76x，LC 70B 3.01x→2.40x。LLM 推理 memory-bound，GPU 空闲算力被 batch 占满后 speculative 的算力复用空间收窄。EAGLE 显存占用略高于 vanilla（V 7B 24G 下 bs_max 8→7；LC 70B 160G 下 5→4）。Figure 7（p.7, M3）中 tree 与 chain 的差距也会随 batch 增大而收窄。
4. **latency 优先，throughput 次之**（§4 Metrics）：EAGLE 主优化 latency（bs=1 设定，承袭 speculative sampling / DistillSpec / BiLD 传统），throughput 仅在最大 bs 下翻倍，非首指标。
5. **训练数据偏 ShareGPT 单域**：虽宣称低敏感性（§4.3.3, Table 6），但所有评测 zero-shot，跨域极端分布漂移下的鲁棒性未充分验证。
6. **draft 深度受误差累积上限制约**：尽管 1-α→4-α 衰减平缓（Figure 8（p.8, M3：feature&shifted-token 蓝线 1-α 维持高位）），Table 2 仍显示 0-α→4-α 累计降 ~0.1，深层 draft（m 大）的接受率仍会受影响，制约 tree 深度上限。
7. **无损保证依赖 tree 上的 Multi-round 算法**（§A.2, Alg.1（p.12））：分布不变性靠递归调用 A 保证，实现复杂度高于 chain speculative sampling；正确性依赖实现无误。
