# 📊 图表素材索引（figures_index）


> 按主题分类的图表清单，含 caption + 页码 + 本地图片路径，便于技术报告快速插入与引用。

> 标 ⭐ 的图已用 MiniMax 多模态深度解读（技术解读见对应论文 MD 的 Figure [!tip]）。

共 588 张图，来自 62 篇论文；其中 ⭐50 张已深度解读。

## ⭐ 精选架构图（MiniMax 深度解读，可直接插入技术报告）

### IndexCache: Accelerating Sparse Attention via Cross-Layer In — Fig.2 (p.3)
![[assets/indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse-p03.png]]
> [!tip] 【MiniMax 解读】IndexCache 架构图(Fig.2)：对比 (a) 标准 DSA（每层跑 lightning indexer）与 (b) IndexCache（加条件分支：F 层算并缓存索引到临时 buffer T_cache，S 层直接复用 T_cache 跳过 indexer）。T_cache 仅存当前索引张量、每 F 层覆写、无额外显存。利用 token 选择跨层冗余消除稳定层 indexer 计算。架构核心图。
*caption: Side-by-side comparison of inference loops. (a) Standard DSA runs the lightning indexer at every layer. (b) IndexCache adds a single conditional branc… ｜ 论文 [[indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse]] ｜ arxiv 见 MD 元信息*

### MEDUSA: Simple LLM Inference Acceleration Framework with Mul — Fig.1 (p.2)
![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p02.png]]
> [!tip] ## Figure Description

The diagram illustrates the **MEDUSA** inference pipeline. On the left, the **Original Model** stacks an Embedding layer, Transformer Layers, and an LM Head. The **Last Hidden state** from the transformer is tapped and branched: it feeds both the standard LM Head (predicting token *t*) and multiple parallel **Medusa Heads** (1, 2, 3), each forecasting a future position (*t+1*, *t+2*, *t+3*). Each head emits **Top-k Predictions** (e.g., Head 1 → "is, ', the"; Head 2 → "difficult, is, '"; Head 3 → "not, difficult, a"). These are combined with the LM Head output ("It, I, As") into a set of **Candidates** (e.g., "It is difficult" ✓, "It' difficult" ✗). A verifier accepts the longest valid prefix, producing the **Single-step prediction** — here "It is difficult" — which then becomes the new input for the next decoding cycle.

### Key Technical Takeaway
MEDUSA eliminates the separate draft model required by speculative decoding by attaching lightweight, fine-tunable heads to the existing backbone's last hidden state; the backbone remains frozen, so the method drops into any deployed LLM with minimal memory overhead and yields 2.3–2.8× speedups without quality degradation.

### Caption (Verbatim)

*Figure 1.* MEDUSA introduces *multiple heads* on top of the last hidden states of the LLM, enabling the prediction of several subsequent tokens in parallel (Section 2.1.1). During inference, each head generates multiple top predictions for its designated position. These predictions are assembled into candidates, which are processed in parallel using a *tree-based attention* mechanism (Section 2.1.2). The final step is to verify the candidates and accept a continuation. Besides the standard rejection sampling scheme, a *typical acceptance* scheme (Section 2.3.1) can also be used here to select reasonable continuations, and the *longest accepted candidate prefix* will be used for the next decoding phase.
*caption: MEDUSA introduces multiple heads on top of the last hidden states of the LLM, enabling the prediction of several sub- sequent tokens in parallel (Sect… ｜ 论文 [[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]] ｜ arxiv 见 MD 元信息*

### MEDUSA: Simple LLM Inference Acceleration Framework with Mul — Fig.2 (p.3)
![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p03.png]]
> [!tip] 【MiniMax 解读】MEDUSA 框架：在 LLM 最后隐藏层挂多个轻量解码头，第 k 个头预测 t+k+1 位 token，单次前向并行产出多候选；候选组织成树，用 tree attention 掩掩码保证因果正确，一次前向验证多分支、接受最长有效续写。无需独立 draft model，2-3x 加速，兼容分布式 serving。架构核心图。
*caption: Remarkably, similar ideas have also been explored in independent works like Miao et al. (2023); Spector & Re (2023), where they follow a bottom-up app… ｜ 论文 [[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]] ｜ arxiv 见 MD 元信息*

### MEDUSA: Simple LLM Inference Acceleration Framework with Mul — Fig.3 (p.7)
![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p07.png]]
> [!tip] # Figure Description

The figure is a two-panel bar-chart benchmark, not an architecture diagram. **Panel (a)** "Speedup on different model sizes" plots *Tokens per Second* for Vicuna-7B and Vicuna-13B across three configurations (w/o Medusa, Medusa-1, Medusa-2). Medusa-1 reaches 2.18× (7B) and 2.33× (13B) over the HuggingFace baseline, while Medusa-2 pushes both to ~2.83×. **Panel (b)** breaks down Medusa-2 speedup on Vicuna-7B across 8 MT-Bench categories, ranging from Humanities (2.58×) up to Extraction (3.62×), with Coding (3.29×) and Math (3.01×) showing the strongest gains.

**Key takeaway:** Medusa's parallel decoding heads are especially effective on structured-output tasks (coding, extraction, math), where prediction is more deterministic and parallelizable, yielding >3× wall-time speedup without retraining the base model.

# Caption (verbatim)

*Figure 3.* Left: Speed comparison of baseline, M*EDUSA*-1 and M*EDUSA*-2 on Vicuna-7B/13B. M*EDUSA*-1 achieves more than 2× wall-time speedup compared to the baseline implementation while M*EDUSA*-2 further improves the speedup by a significant margin. Right: Detailed speedup performance of Vicuna-7B with M*EDUSA*-2 on 8 categories from MT-Bench.
*caption: Left: Speed comparison of baseline, MEDUSA-1 and MEDUSA-2 on Vicuna-7B/13B. MEDUSA-1 achieves more than 2× wall-time speedup compared to the baseline … ｜ 论文 [[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]] ｜ arxiv 见 MD 元信息*

### EAGLE-3: Scaling up Inference Acceleration of Large Language — Fig.2 (p.2)
![[assets/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-p02.png]]
> [!tip] 【MiniMax 解读】EAGLE-3 加速比柱状图（temp=0）：在 Vicuna-13B/LLaMA-3.1-8B/3.3-70B/DeepSeek-R1-LLaMA-8B 上对比 Vanilla/SpecDec/Medusa/HASS/EAGLE/EAGLE-2/EAGLE-3，EAGLE-3 分别达 5.6x/4.4x/4.1x/5.0x，全面最优。适合做「EAGLE-3 性能优势」论据。
*caption: Speedup ratios of different methods at temperature=0. For the standard speculative sampling, Vicuna-13B uses Vicuna-68M as the draft model. In Table 1… ｜ 论文 [[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]] ｜ arxiv 见 MD 元信息*

### EAGLE: Speculative Sampling Requires Rethinking Feature Unce — Fig.2 (p.2)
![[assets/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-p02.png]]
> [!tip] 【MiniMax 解读】EAGLE 架构图(Fig.4)：目标 LLM 产出第二顶层特征 f_t 与下一 token t_{t+1}；轻量 draft model 在特征层自回归，输入 f_t + 超前一拍的 t_{t+1}，预测 f_{t+1}，再经 LM head 得 draft token t_{t+2}。「特征+超前 token」消除采样下 f_{t+1} 的不确定性→接受率↑，Vicuna/LLaMA2-70B 上 2.68x。架构核心图。
*caption: Speedup ratio on the MT-bench for non-greedy (temperature=1) settings. Lookahead is confined to greedy decoding, and the non-greedy generation of Medu… ｜ 论文 [[eagle-speculative-sampling-requires-rethinking-feature-uncertainty]] ｜ arxiv 见 MD 元信息*

### DFlash: Block Diffusion for Flash Speculative Decoding — Fig.2 (p.4)
![[assets/dflash-block-diffusion-for-flash-speculative-decoding-p04.png]]
> [!tip] 【MiniMax 解读】DFlash 设计：block-diffusion draft model 块内并行生成多 token（非逐 token 自回归）→低 draft 延迟；目标 LLM 先 prefill 产首 token 并取若干层隐藏态，concat 后过投影层融成 target context feature，注入每个 draft 层的 KV cache 并跨轮复用，持续提供上下文引导→接受长度随 draft 深度增长，无 token-embedding 稀释（优于 EAGLE 式输入融合）。架构核心图。
*caption: DFlash Inference Design. Hidden context features extracted from the target model are fused and injected into each draft layer’s… ｜ 论文 [[dflash-block-diffusion-for-flash-speculative-decoding]] ｜ arxiv 见 MD 元信息*

### JETSPEC: Breaking the Scaling Ceiling of Speculative Decodin — Fig.2 (p.3)
![[assets/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-p03.png]]
> [!tip] 【MiniMax 解读】JetSpec 因果并行草稿头(Fig.3)：轻量 draft head 接冻结目标模型 M_q 中间层融合特征，单次前向并行预测所有 γ 个 draft 位的 top-k 候选→组成 k^γ 候选树；输出重排为广度优先、分支级因果序列再回灌 M_q 验证（满足 tree-SD 左到右依赖）。M_q 冻结只训 head。把草稿成本 c 压到 head 级、接受率 α 保持高→加速随 γ 单调增长，破解 c/α 鱼与熊掌。架构核心图。
*caption: Expected speculative decoding speedup scales as a function of draft length γ, under different per-token drafting costs c and acceptance rates α. Compa… ｜ 论文 [[jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting]] ｜ arxiv 见 MD 元信息*

### GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM REINFORCEM — Fig.1 (p.1)
![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p01.png]]
> [!tip] ## Main Figure Description

**Architecture/Components:** Figure 1 presents two side-by-side learning-curve plots comparing three optimization methods on Qwen3 8B across benchmarks (a) HotpotQA and (b) IFBench. Each panel plots score (y-axis) vs. rollouts sampled on a log scale (x-axis), tracking three lines — GEPA (green), GRPO (blue/black step function), and MIPROv2 (orange). Star markers (blue and gray/orange) denote held-out test-set scores at the start and end.

**Data Flow:** Rollouts are sampled → prompt optimizer updates prompts → performance evaluated → Pareto-frontier of attempted prompts evolves.

**Key Takeaway:** GEPA's natural-language reflection reaches a high-quality plateau with dramatically fewer rollouts than GRPO's gradient-based learning, while also surpassing MIPROv2 on final test-set accuracy.

## Caption (Verbatim)

Figure 1: A comparison of learning behavior of the GEPA prompt optimizer against a state-of-the-art prompt optimizer (MIPROv2) and GRPO (24,000 rollouts). As more rollouts are sampled, the prompt optimizers can learn much more quickly than GRPO. GEPA substantially outperforms both GRPO and MIPROv2 in final score. The Test-set star markers demonstrate the performance gap in a held-out set of questions.
*caption: A comparison of learning behavior of the GEPA prompt optimizer against a state-of-the-art prompt optimizer (MIPROv2) and GRPO (24,000 rollouts). As mo… ｜ 论文 [[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]] ｜ arxiv 见 MD 元信息*

### GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM REINFORCEM — Fig.2 (p.3)
![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p03.png]]
> [!tip] **Description (architecture/components/data flow + key takeaway):**

The figure presents a side-by-side comparison of two text panels. The top panel ("Seed Prompt") is a terse, one-line instruction: given fields *question* and *summary_1*, produce a *query*. The bottom panel ("GEPA's Optimized Prompt, GPT-4.1 Mini") is an expanded, richly structured system prompt with five sections — Input Understanding, Purpose/Context, Key Observations & Lessons, How to Build the Query, Practical Strategy, and Output — featuring bullet points, worked examples (e.g., parish→archipelago population), and explicit constraints like "not found in first hop." No explicit arrows are shown; data flow is implicit (question + summary_1 → query). Key takeaway: GEPA transforms a minimal seed prompt into a detailed, reasoning-guided prompt by injecting task-specific heuristics, examples, and negative constraints to improve multi-hop retrieval quality.

**Caption (verbatim):**

> Figure 2: This figure shows an example prompt generated by GEPA for the second-hop document retrieval to be performed in a multi-hop question-answer system, along with the seed prompt it started with. Appendix L compares GEPA's prompts for all tasks with prompts generated by MIPROv2.
*caption: This figure shows an example prompt generated by GEPA for the second-hop document retrieval to be performed in a multi-hop question-answer system, alo… ｜ 论文 [[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]] ｜ arxiv 见 MD 元信息*

### SARATHI: Efficient LLM Inference by Piggybacking Decodes wit — Fig.2 (p.3)
![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p03.png]]
> [!tip] 【MiniMax 解读】SARATHI chunked-prefill：把 prompt 切成等长 prefill chunk（匹配流水级算力），在途 decode 请求 piggyback 到每个 prefill chunk 上→单次前向混合 prefill+decode token。解耦长 prefill 与 decode 延迟：每个流水级跑统一 hybrid-phase 步、消除 prefill-decode bubble、打满 GPU。更高单卡利用率+decode 吞吐+更大 batch。架构核心图。
*caption: High-level architecture of a decoder block. sequence length of each request (i.e., the number of input tokens in the given query), and H is the model’… ｜ 论文 [[sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills]] ｜ arxiv 见 MD 元信息*

### Taming Throughput-Latency Tradeoff in LLM Inference with Sar — Fig.2 (p.2)
![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p02.png]]
> [!tip] **Figure Description:**

The figure is a 2D scatter plot comparing four LLM serving systems on a Throughput (y-axis) vs. TBT Latency (x-axis) plane. Four systems are plotted:
- **FasterTransformer** (bottom-left, red dot): Decode-prioritizing — low throughput, low TBT latency
- **Orca** (middle, pink dot): Prefill-prioritizing with iteration-level batching
- **vLLM** (top-right, blue dot): Prefill-prioritizing with paged attention — high throughput, high TBT latency
- **Sarathi-Serve** (top-left, green star): Stall-free batching — high throughput, low TBT latency

Dashed trajectory lines connect the points, illustrating how prior approaches (Orca → vLLM via paged attention) trend toward higher latency as throughput is optimized.

**Key Technical Takeaway:** Sarathi-Serve uniquely occupies the favorable top-left region, breaking the conventional throughput-latency tradeoff by using stall-free batching to coalesce ongoing decodes with prefill chunks from new requests.

**Caption (verbatim):**

Figure 2: Current LLM serving systems involve a tradeoff between throughput and latency depending on their scheduling policy. Prioritizing prefills optimizes throughput but sacrifices TBT (time-between-tokens) tail latency whereas prioritizing decodes has the opposite effect. Sarathi-Serve serves high throughput with low TBT latency via stall-free batching. (The figure is illustrative and actual values will depend on the model and workload characteristics.)
*caption: Current LLM serving systems involve a tradeoff be- tween throughput and latency depending on their scheduling policy. Prioritizing prefills optimizes … ｜ 论文 [[taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve]] ｜ arxiv 见 MD 元信息*

### Taming Throughput-Latency Tradeoff in LLM Inference with Sar — Fig.3 (p.5)
![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p05.png]]
> [!tip] ## Main Figure Description (Figure 4)

**Architecture/Components:** Two side-by-side stacked bar charts breaking down LLM inference runtime for Mistral-7B on a single A100 GPU. The left chart ("Prefill") plots total time (ms) against sequence length (128 → 2K), while the right chart ("Decode") plots time (ms) against batch size (1 → 64). Each bar is segmented into three stacked components shown in the legend: **linear** (teal, hatched), **attention** (gray), and **others** (red, hatched).

**Data Flow:** The decomposition shows how the wall-clock time of a forward pass is partitioned among operator categories. Prefill scales sharply with sequence length (peaking ~145 ms at 2K tokens), dominated by linear layers, while decode remains flat across batch sizes (~10–25 ms) since the per-token cost is nearly constant.

**Key Technical Takeaway:** **Linear (matmul) layers—not attention—dominate LLM inference runtime**, contributing >80% of total time even at long sequence lengths. Furthermore, because of low arithmetic intensity in decode, the cost of one linear operation on **1 decode token ≈ the cost on 128 prefill tokens**, implying decode is fundamentally memory-bound and batching is the lever to amortize linear-layer weight-loading cost. (~118 words)

---

## Captions Verbatim

**Figure 3:** "Throughput of the prefill and decode phases with different batch sizes for Mistral-7B running on a single A100 GPU. We use prompt length of 1024 for both prefill and decode experiments. Note that different y-axis, showing prefills are much more efficient than decode. Further, note that *batching boosts decode throughput almost linearly but has a marginal effect on prefill throughput*."

**Figure 4:** "Prefill and decode time with different input sizes for Mistral-7B running on single A100 GPU. Linear layers contribute to the majority of runtime in both prefill and decode phases. Due to the low arithmetic intensity in decode batches, the cost of linear operation for 1 decode token is nearly same as 128 prefill tokens."
*caption: Throughput of the prefill and decode phases with different batch sizes for Mistral-7B running on a single A100 GPU. We use prompt length of 1024 for b… ｜ 论文 [[taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve]] ｜ arxiv 见 MD 元信息*

### DeepSeek-V4: Towards Highly Efficient Million-Token Context  — Fig.1 (p.14)
![[assets/deepseek-v4-towards-highly-efficient-million-token-context-intelligence-p14.png]]
> [!tip] **1) 架构/组件/数据流描述（≤150字）**

算法流程：梯度计算 → 动量累积（Nesterov） → 混合Newton-Schulz正交化（10步：8步快速收敛+2步稳定） → 更新矩阵RMS重缩放（复用AdamW超参） → 权重衰减更新。双优化器策略：嵌入层、预测头、RMSNorm、mHC门控与静态偏置保留AdamW，其余模块统一用Muon。注意力侧通过对Q与KV做RMSNorm，使logits不再爆炸，从而弃用QK-Clip。

**2) 关键技术要点**

混合Newton-Schulz双阶段系数策略：前8步用 *(3.4445, 4.7750, 2.0315)* 快速把奇异值推向1，后2步切换为 *(2, 1.5, 0.5)* 精细稳定到1，兼顾收敛速度与数值精度。

**3) Caption 逐字转录**

```
Algorithm 1  Muon Optimizer for DeepSeek-V4

Require: Learning rate η, momentum β, weight decay ω, update rescaling factor W
 1: for each training step B do
 2:    for each logically independent weight, matrix R^(l,n) do
 3:       G = ∇_B L_B, B ← B                              Compute gradients
 4:       "M_B = β·"M_B + B                                 Accumulate momentum buffer
 5:       O_B = HybridNewtonSchulz("M_B, β, B)             Nesterov trick and hybrid Newton-Schulz
 6:       $B = $O_B / max(||·||,<,,"·W                     Rescale the update RMS
 7:       θ_B = θ_B − η·1"·[θ_B − ω·[$_B                   Perform weight decay and update
 8:    end for
 9: end for
```

（注：原图中第6–7行部分符号（带 "*""[]""$" 等字形）疑似 PDF 字体渲染异常；其中 `1""·` 应为 `1ᵀ·`（转置），`||·||<,,"` 应为更新矩阵的谱范数 `||·||_σ`，`[$_B` 应为 `θ_B` 的旧值项的标量系数。具体数学符号请以原文 PDF 为准。）
*caption: 2.4. Muon Optimizer… ｜ 论文 [[deepseek-v4-towards-highly-efficient-million-token-context-intelligence]] ｜ arxiv 见 MD 元信息*

### DeepSeek-V4: Towards Highly Efficient Million-Token Context  — Fig.5 (p.15)
![[assets/deepseek-v4-towards-highly-efficient-million-token-context-intelligence-p15.png]]
> [!tip] 【MiniMax 解读】DeepSeek-V4 细粒度 EP(Fig.5)：MoE 层拆 Dispatch/Linear-1/Linear-2/Combine 四段。Comet 仅粗粒度重叠 Dispatch↔L1、L2↔Combine；本方案把 expert 再切 wave，一波 dispatch 完即开算、下一波并行 dispatch→稳态下「当前波计算+下一波 token 传输+上一波结果回送」三路并发=连续计算-通信流水。因单层通信<计算，融合成单流水 kernel 藏住互连延迟→低带宽互连也不掉吞吐。架构核心图，与 MoE/EP 相关。
*caption: This forms a fine-grained pipeline among experts, keeping both computation and communication continuous throughout the wave. The wave-based scheduling… ｜ 论文 [[deepseek-v4-towards-highly-efficient-million-token-context-intelligence]] ｜ arxiv 见 MD 元信息*

### HYPER-CONNECTIONS — Fig.1 (p.1)
![[assets/hyper-connections-p01.png]]
> [!tip] **Figure description**

This is a four-panel empirical comparison (not an architecture diagram) plotting two model variants — `OLMoE-1B-7B` (baseline, red) vs `OLMoE-1B-7B-DHC×4` (hyper-connections, blue) — as a function of training tokens (100B → 500B):
1. Training loss (0.99 EMA smoothed) — blue sits below red throughout.
2. C4-en validation loss — same trend.
3. HellaSwag accuracy (%) — blue higher.
4. ARC-Challenge accuracy (%) — blue higher.

Annotations mark a "×1.8" convergence-speedup gap at ~0.027 / 0.028 loss. Lightly shaded regions indicate variance across runs.

**Key takeaway**: Hyper-connections yield ~1.8× faster convergence and sustained downstream-accuracy gains (HellaSwag, ARC-Challenge) over standard residual connections, without changing the underlying architecture.

**Caption (verbatim)**

"Figure 1: The performance of the baseline model `OLMoE-1B-7B` and the model with hyper-connections, `OLMoE-1B-7B-DHC×4`. (1) and (2) show the training loss (0.99 EMA smoothed) and the C4-en validation loss, respectively. Our method converges 1.8 times faster compared to the baseline and maintains a significant advantage at the 500B tokens. (3) and (4) show the accuracy curves on `HellaSwag` and `ARC-Challenge`, demonstrating the superior performance of the `OLMoE-1B-7B-DHC×4` model."
*caption: The performance of the baseline model OLMoE-1B-7B and the model with hyper- connections, OLMoE-1B-7B-DHC×4. (1) and (2) show the training loss (0.99 E… ｜ 论文 [[hyper-connections]] ｜ arxiv 见 MD 元信息*

### HYPER-CONNECTIONS — Fig.2 (p.2)
![[assets/hyper-connections-p02.png]]
> [!tip] 【MiniMax 解读】Hyper-Connections 架构(Fig.2)：(a) 传统残差连接=层输出与单隐层 h 求和；(b) HC n=2 把输入复制成两个隐向量 h1/h2，层输出经可学习标量(β,α)路由回→加权连接矩阵灵活跨深+宽组合特征。解耦成 (c) depth-connections（层输出与 h1 加权和）+ (d) width-connections（h1/h2 横向混合）。核心：用可学习、输入依赖的路由替固定恒等 skip，让网络自主调制 skip 强度→缓解固定 Pre/Post-Norm 残差的表征塌缩+梯度消失。架构核心图。
*caption: Hyper-connections (HC) with an expansion rate of n = 2. (a) Residual connections. (b) Hyper-connections: β1, β2, α0,0, α0,1, α1,0, α1,1, α2,1, and α2,… ｜ 论文 [[hyper-connections]] ｜ arxiv 见 MD 元信息*

### HYPER-CONNECTIONS — Fig.4 (p.5)
![[assets/hyper-connections-p05.png]]
> [!tip] **Figure 4 Description:**

Figure 4 illustrates two hyper-connection topologies with expansion rate n = 2, showing how a learnable matrix determines layer arrangement.

**Components (shared by both subfigures):**
- Blue/yellow rectangular token blocks (residual stream + expanded inputs)
- Rounded "layer 1" / "layer 2" modules
- ⊕ summation nodes connecting layer outputs back into the stream
- Directed arrows encoding weighted connections (the hyper-connection matrix entries)

**(a) Sequential Arrangement:** Lower-triangular HC = `(0,1;1,1)`; each layer feeds forward, and the depth connection degenerates into a standard residual connection.

**(b) Parallel Arrangement:** Odd/even HC matrices `(0,1,0;1,1,1;1,1,1)` and `(0,0,1;0,1,0;1,0,1)` route both layers' inputs simultaneously — analogous to parallel transformer blocks.

**Key takeaway:** The same layer stack yields sequential or parallel behavior purely from the HC matrix pattern, enabling a learnable sequential–parallel duality beyond fixed architectural choices.

**Caption (verbatim):**
> Figure 4: Sequential and parallel arrangements of hyper-connections with n = 2.
*caption: Sequential and parallel arrangements of hyper-connections with n = 2.… ｜ 论文 [[hyper-connections]] ｜ arxiv 见 MD 元信息*

### Let It Flow: Agentic Crafting on Rock and Roll — Fig.1 (p.1)
![[assets/let-it-flow-agentic-crafting-on-rock-and-roll-p01.png]]
> [!tip] **Architecture & Data Flow**
The figure presents the Agentic Learning Ecosystem (ALE) as a closed-loop, full-stack infrastructure. Three components interlock: **ROCK** (sandbox environment manager that generates executable trajectories), **iFlow CLI** (agent framework handling context engineering and environment interaction), and **ROLL** (scalable RL framework for multi-environment policy optimization). Data flows circularly: Instructions → iFlow → trajectories generated inside ROCK → consumed by ROLL → ROME model update → context/policy feedback returns to iFlow. A linear Task→Action→Execution→Feedback→Learning workflow underlies the loop.

**Key Technical Takeaway**
Empirical scaling is striking: ROME's accuracy climbs from 41.80% (initial) to 89.83% (peak) over training — a +47.07 absolute / +113.16% relative gain — while achieving 57.40% on SWE-bench Verified and 24.72% on Terminal-Bench 2.0, outperforming similarly-sized open models (100B parameters).

**Caption (verbatim):**
Figure 1: Overview of the Agentic Learning Ecosystem (ALE) and ROME Performance.
*caption: Overview of the Agentic Learning Ecosystem (ALE) and ROME Performance. 1[cs.AI] 12 Mar 2026… ｜ 论文 [[let-it-flow-agentic-crafting-on-rock-and-roll]] ｜ arxiv 见 MD 元信息*

### Let It Flow: Agentic Crafting on Rock and Roll — Fig.2 (p.4)
![[assets/let-it-flow-agentic-crafting-on-rock-and-roll-p04.png]]
> [!tip] ## Main Figure Description

The figure has two panels illustrating the **Agentic Learning Ecosystem (ALE)**:

**(a) Ecosystem architecture** — Two coupled subsystems. The left block, *ROLL* (RL training framework), contains an Actor-Train model whose weights are synced to an Actor-Infer model; an Env. Manager dispatches LLM Requests to multiple Env. Workers (each backed by Rock SDK) and collects LLM Responses/Training Data. The right block, *ROCK Sandbox* (execution engine), hosts the *iFlow CLI* agent framework and a ModelProxy Service that mediates Poll Request / LLM Request / Deliver Response traffic via Request and Response Queues. The two subsystems communicate over the Rock SDK interface.

**(b) RL training pipeline** — A closed loop: the *Rollout Stage* cycles Agentic LLM ↔ Environment through Action tokens and Observations, emitting Trajectory Data that drives the *Training Stage* (Weight Update), whose updated weights are synchronized back to rollout.

**Key takeaway:** Decoupling rollout environment execution (ROCK) from model training/inference (ROLL) — connected via queued ModelProxy RPCs — enables scalable, fault-tolerant, closed-loop agentic RL.

## Caption (verbatim)

Figure 2: The overview of agentic RL ecosystem (a) and its training pipeline (b).

(a) The overview of **A**gentic **L**earning **E**cosystem (**ALE**).
(b) Agentic RL training pipeline.
*caption: The overview of agentic RL ecosystem (a) and its training pipeline (b). technical stack, ALE is also a call to reframe the community’s priorities. In … ｜ 论文 [[let-it-flow-agentic-crafting-on-rock-and-roll]] ｜ arxiv 见 MD 元信息*

### Step-3 is Large yet Affordable: Model-system Co-design for C — Fig.4 (p.8)
![[assets/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-p08.png]]
> [!tip] 【MiniMax 解读】Step-3 attention 设计对比(Fig.5)：Decode 计算 vs 内存访问(8K→32K ctx)，对比 DSv3 MLA / Qwen3-MoE GQA / Step-3 MFA，叠 H800/910B/A800/H20 roofline。DSv3 MLA 算术强度512=H800 compute-bound；Qwen3 GQA 强度32=H20 memory-bound；Step-3 MFA 强度128≈910B(175)/A800(156) ridge 点→计算仅 DSv3 1/4、访存仅 Qwen3 1/3，跨硬件都省。⭐直击 910B roofline，与昇腾相关。
*caption: Step-3 and Pangu Pro MoE have very different trends of decoding cost and training cost.… ｜ 论文 [[step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding]] ｜ arxiv 见 MD 元信息*

### Step-3 is Large yet Affordable: Model-system Co-design for C — Fig.7 (p.12)
![[assets/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-p12.png]]
> [!tip] **1) 主要架构/组件/数据流描述**

图示展示了 **AFD（Attention-FFN 分离）架构** 的通信拓扑与多阶段流水线：
- **Attention 实例**（下方）和 **FFN 实例**（上方）通过 **Direct RDMA** 直连，每侧各包含多块 GPU（G）。
- 数据流沿时间轴分为 **Layer0 / Layer1** 两个阶段，三个样本 **D1, D2, D3** 依次经 Attn→A→F（fp8）送至 FFN，FFN 计算后经 **F→A（bf16）** 回传残差，再进入下一层 Attn。
- 三条独立通道并行：**Attn** 计算、**A→F（fp8）前向广播**、**F→A（bf16）反向回传**，互不抢占带宽。

**2) 关键技术要点**

**混合精度通信 + 多阶段流水线重叠**：Attention→FFN 方向采用 **FP8 量化**以节省带宽，FFN→Attention 方向保留 **BF16** 以保护残差精度；通过让 **A→F 与 F→A 两条独立路径并发**（不抢带宽），结合各阶段近似的计算耗时，使通信完全被计算掩盖，实现 **低延迟下的高吞吐** 流水（同一层可连续接收 D1', D2', D3'）。**

**3) 图 caption 逐字转录**

**Figure 7: Communication topology and the multi-stages pipeline of the AFD architecture.**
*caption: Communication topology and the multi-stages pipeline of the AFD architecture.… ｜ 论文 [[step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding]] ｜ arxiv 见 MD 元信息*

### SGLang: Efficient Execution of Structured Language Model Pro — Fig.1 (p.2)
![[assets/sglang-efficient-execution-of-structured-language-model-programs-p02.png]]
> [!tip] 【MiniMax 解读】SGLang 系统架构(Fig.1)：Python 嵌入式前端+高性能 runtime，流式 interpreter 提交原语(extend/gen/fork)异步执行并保留依赖。RadixAttention 用 LRU 基数树缓存 KV，跨请求共享前缀自动复用中间注意力态。Frontiers&Dependencies 跟踪就绪原语+数据依赖→批独立操作、重叠执行藏延迟。DSL+radix-cache+依赖调度统一，比 vLLM/Guidance/LMQL 快至 6.4x。架构核心图。
*caption: System architecture: An interpreter executes language primitives with optimized runtime.… ｜ 论文 [[sglang-efficient-execution-of-structured-language-model-programs]] ｜ arxiv 见 MD 元信息*

### SGLang: Efficient Execution of Structured Language Model Pro — Fig.2 (p.3)
![[assets/sglang-efficient-execution-of-structured-language-model-programs-p03.png]]
> [!tip] 这张图展示了一段使用SGLang实现多维度文章评判器的Python代码示例，通过分支-求解-合并（branch-solve-merge）提示技术来评估一篇关于图像的文章，从清晰度、原创性和证据性等多个维度并行评判，并附有关于编程模型、语言原语和执行模式的文字说明。
*caption: The implementation of a multi-dimensional essay judge in SGLang utilizes the branch-solve-merge prompting technique [40]. Primitives provided by SGLan… ｜ 论文 [[sglang-efficient-execution-of-structured-language-model-programs]] ｜ arxiv 见 MD 元信息*

### SGLang: Efficient Execution of Structured Language Model Pro — Fig.3 (p.5)
![[assets/sglang-efficient-execution-of-structured-language-model-programs-p05.png]]
> [!tip] **图3 (Figure 3) 概览**

这张图展示了 **RadixAttention** 操作在 9 个时间点的示例，使用 **LRU (最近最少使用) 淘汰策略**。

**节点颜色编码：**
- 🟢 **绿色**：新添加的节点
- 🔵 **蓝色**：该时间点访问的缓存节点
- 🔴 **红色**：已被淘汰的节点

**9个时间点的演化过程：**
1. **步骤 (1)**：radix 树初始为空
2. **步骤 (2)**：处理用户消息 "Hello"，系统提示 + 对话被合并到树的单个边
3. **步骤 (3)**：新提示到达，复用前缀的 KV 缓存
4. **步骤 (4)**：新聊天会话开始，节点 "b" 被分裂以共享系统提示
5. **步骤 (5)**：因内存限制，节点 "c" 被淘汰
6. **步骤 (6)**：few-shot 学习查询到达，根节点被分裂
7. **步骤 (7)**：批量 few-shot 查询，节点 "e" 被分裂以支持共享
8. **步骤 (8)**：第二个聊天会话的消息到达，其中节点 "g" 和 "h" 被淘汰
9. **步骤 (9)**：采样更多答案（自一致性提示），节点 "i"、"k"、"l" 被淘汰

**关键概念：**
- **Radix 树**结构用于动态管理 KV 缓存
- **前缀匹配**实现缓存复用
- **Frontend-Runtime 协同设计**：前端解释器发送完整提示，运行时执行前缀匹配和复用

---
*caption: Examples of RadixAttention operations with an LRU eviction policy, illustrated across nine time points. The figure demonstrates the dynamic evolution … ｜ 论文 [[sglang-efficient-execution-of-structured-language-model-programs]] ｜ arxiv 见 MD 元信息*

### SGLang: Efficient Execution of Structured Language Model Pro — Fig.4 (p.6)
![[assets/sglang-efficient-execution-of-structured-language-model-programs-p06.png]]
> [!tip] **图4 深度解读**

**1) 图类型**
**架构/机制对比图** —— 展示 SGLang 提出的**压缩有限状态机（Compressed FSM）**相对于传统 FSM 的解码机制差异。属于算法/系统设计图，而非性能数据图。**

**2) 核心内容**

**图例符号系统：**
- 🔵 蓝色方块/圆 = **FSM state**（状态节点）
- 🟠 橙色方块 = **Token**（已确定的 token）
- 🟢 绿色六边形 = **LLM decode**（一次模型前向调用）

**四个子图的对比：**

| 子图 | 内容 | 状态数 | 解码调用次数 |
|------|------|--------|-------------|
| **(a) Normal FSM** | 14 个状态 (0→13)，每条边对应**单一字符** `{`, `"`, `s`, `u`, `m`, `m`, `a`, `r`, `y`, `"`, `:`, `_` | 14 | — |
| **(b) Compressed FSM** | 仅 2 个状态 (0→1)，整个字符串 `{"summary":_` 被**压缩为单条边** | 2 | — |
| **(c) Normal 解码流程** | `{" → LLM → summary → LLM → " → LLM → : → LLM → "_ → LLM` | — | **4 次 LLM 前向** |
| **(d) Compressed 解码流程** | `{" → summary → ":_ → LLM`（确定性 token 直接放行，仅歧义处调用模型） | — | **1 次 LLM 前向** |

**关键数据流逻辑：**
- (c) 中每生成一个字符级 token 都需一次完整 LLM 前向传播，即使后续字符在 FSM 中**完全确定**。
- (d) 利用 FSM 分析，识别出**单例转移边（singular-transition edges）**——即当前状态下只有唯一合法 token 的边——将其压缩为单边，从而在该位置**跳过 LLM 调用**，直接放行 token。仅在必须由模型采样歧义 token 时才触发前向传播。

**3) 一个关键技术要点**

**核心创新：Singular-Transition 压缩** —— 将 FSM 中那些**没有分支的链式转移**（如 `s→u→m→m→a→r→y` 这一必然序列）合并为单一跳变，使确定性输出段**完全绕过 LLM 前向计算**。这与现有的 logits-mask 式逐 token 解码（如 Guidance、Outlines）形成本质区别：后者即使在 FSM 状态完全确定时仍会触发一次完整的 Transformer 前向，造成巨大浪费。对长确定性前缀（如 JSON schema、代码骨架）场景，加速比可与确定性 token 数线性成正比。**

**4) Caption 逐字转录**

> **Figure 4:** The decoding process of normal and compressed FSMs (the underscore `_` means a space).
>
> 子图标注：
> - (a) Normal FSM for regex `{"summary":_`
> - (b) Compressed FSM for regex `{"summary":_`
> - (c) Decoding process with normal FSM
> - (d) Decoding process with compressed FSM
>
> （脚注 2）：In practice, the computation is not the same as what is described in the proof of Theorem 3.1 because the unpredictable number of output tokens can cause the recomputation of the KV cache.
*caption: The decoding process of normal and compressed FSMs (the underscore _ means a space). requests by matched prefix length and prioritize requests with lo… ｜ 论文 [[sglang-efficient-execution-of-structured-language-model-programs]] ｜ arxiv 见 MD 元信息*

### SGLang: Efficient Execution of Structured Language Model Pro — Fig.5 (p.7)
![[assets/sglang-efficient-execution-of-structured-language-model-programs-p07.png]]
> [!tip] **SGLang论文 Figure 5 深度解读**

**1) 图类型**
**结果对比型柱状图（Bar Chart）**——属于端到端性能评估（End-to-End Performance）章节的标准基准对比图，用于展示 SGLang 与多个基线系统在多种 LLM 工作负载下的吞吐量对比。**

**2) 核心内容**

**组件与对比对象（共4个系统）**
| 系统 | 角色 | 颜色 |
|---|---|---|
| **SGLang** | 本文系统 | 橙色 |
| **vLLM** | 高吞吐推理引擎基线 | 绿色 |
| **Guidance** | 受控生成 DSL 基线 | 蓝色 |
| **LMQL** | 查询语言基线 | 灰色 |

**实验设置**
- **模型**：Llama-7B（开源权重，float16 精度）
- **归一化方式**：以 SGLang 为基准（SGLang 在所有 workload 上均为 1.0）
- **Y 轴**：Normalized Throughput（0.0 ~ 1.0）

**11 个测试 Workload**
MMLU、ReAct Agents、Generative Agents、Tree of Thought、Skeleton of Thought、LLM Judge、HellaSwag、JSON Decoding、Multi-Turn Chat (short)、Multi-Turn Chat (long)、DSPy RAG Pipeline

**关键数字（视觉读数）**
- **MMLU**：vLLM ≈ 0.15, Guidance ≈ 0.10（基线系统几乎"趴底"）
- **Generative Agents**：vLLM ≈ 0.9, Guidance ≈ 0.7（差距较小但仍明显）
- **Multi-Turn Chat (long)**：vLLM ≈ 0.97（最接近 SGLang）
- **Tree of Thought / Skeleton of Thought / LLM Judge / HellaSwag / JSON Decoding**：除 vLLM 有部分产出外，Guidance 和 LMQL 几乎为 0
- 跨所有负载，**SGLang 始终保持 1.0**（即最高吞吐）

**配套硬件与基线配置（正文上下文）**
- 硬件：AWS EC2 G5 实例，NVIDIA A10G（24GB）；7B 模型单卡 A10G，70B 模型用张量并行到多卡 A100 80GB
- 基线版本：Guidance v0.1.8（llama.cpp 后端），vLLM v0.2.5，LMQL v0.7.3（HF Transformers 后端）
- 指标：throughput（program instances/s）和 latency（平均延迟）

**3) 一个关键技术要点**

**SGLang 的"前端 DSL + 运行时协同设计"在结构化/多轮/Agent 工作负载上带来数量级提升**。**

具体而言，传统推理引擎（vLLM）虽然裸推理吞吐高，但**只把每个 `gen()` 调用当成一次独立 API 调用**，对结构化输出（如 JSON、select、LLM-as-judge）只能串行等待；对 Agent 类工作负载则无状态复用能力。SGLang 通过：

1. **RadixAttention**（基于前缀树的 KV cache 复用）——直接解释 Multi-Turn Chat 和 Agent 场景里反复出现的 system prompt / 上下文；
2. **推测式执行（speculative execution）**——在第一个 `gen()` 还没结束时继续吃后续 token，省一次 API 往返与输入 token 计费；
3. **结构化 primitive（`select`/`gen`+正则/regex constraint）**——避免 LMQL/Guidance 那种"先生成再校验再回滚"的浪费。

正如图中所示，**负载越"程序化"（含多 gen 调用、带约束、带分支），SGLang 相对 vLLM/Guidance/LMQL 的领先越显著**——Tree-of-Thought、JSON Decoding、LLM Judge 上 vLLM 都掉到 0.2 以下，而 SGLang 保持 1.0；最终体现为正文所述的 **最高 6.4× 吞吐提升、3.7× 延迟下降**。

**4) Caption 逐字转录**

> **Figure 5: Normalized throughput on Llama-7B models. Higher is better.**
*caption: Normalized throughput on Llama-7B models. Higher is better. pattern: s += context + "name:" + gen("name", stop="\n") + "job:" + gen("job", stop="\n").… ｜ 论文 [[sglang-efficient-execution-of-structured-language-model-programs]] ｜ arxiv 见 MD 元信息*

### SGLang: Efficient Execution of Structured Language Model Pro — Fig.6 (p.8)
![[assets/sglang-efficient-execution-of-structured-language-model-programs-p08.png]]
> [!tip] **SGLang论文第8页深度解读**

**1) 图类型**

**结果对比图**（性能基准评测）——共两张柱状图，属于实验结果展示类，专注于延迟与吞吐的归一化对比。**

---

**2) 核心内容**

**Figure 6：Llama-7B 模型上的归一化延迟（Lower is Better）**

| 组件 | 内容 |
|------|------|
| **对比系统** | SGLang（橙）、vLLM（绿）、Guidance（蓝）、LMQL（灰） |
| **基准任务** | 11项：MMLU、ReAct Agents、Generate Agents、Tree of Thought、Skeleton of Thought、LLM Judge、HellaSwag、JSON Decoding、Multi-Turn Chat (short/long)、DSPy RAG Pipeline |
| **归一化基线** | LMQL 在大多数任务上作为 1.0 基准 |
| **关键观察** | SGLang 在前 8 项任务上延迟显著低于三个基线（柱高极矮）；在后 3 项（JSON、Multi-Turn Chat、DSPy RAG）中 vLLM 与 SGLang 接近（GUIDANCE/LMQL 被排除） |

**Figure 7：Mixtral-8x7B 模型上的归一化吞吐（Higher is Better）**

| 组件 | 内容 |
|------|------|
| **对比系统** | 仅 SGLang（橙）vs vLLM（绿） |
| **模型规模** | Mixtral-8x7B + 张量并行（TP） |
| **关键观察** | SGLang 在大多数基准上吞吐显著高于 vLLM；HellaSwag、JSON Decoding、DSPy RAG 上 vLLM 表现极低（柱高接近 0） |

**实验设置要点**

- **双模型规模**：Llama-7B（Figure 6）与 Mixtral-8x7B（Figure 7），后者引入张量并行
- **基准多样性**：覆盖分类（MMLU）、Agent（ReAct/Generate）、CoT（Tree/Skeleton-of-Thought）、结构化输出（JSON）、多轮对话、RAG 等典型 LLM 工作负载
- **排除项**：Guidance 和 LMQL 在后五项基准被排除——因 LMQL 慢在 token 级处理和后端未优化，Guidance 缺乏批处理与并行支持

---

**3) 关键技术要点**

**RadixAttention + 缓存感知调度实现 50%–99% 缓存命中率，平均达最优命中率的 96%**

这是 SGLang 最核心的创新。论文正文明确指出三大加速来源：

1. **KV cache 复用**：通过 Radix Tree 将请求的 prompt 分解为 token 序列，按前缀自动复用 KV cache（如 MMLU 复用 5-shot 示例、HellaSwag 复用 few-shot 示例与公共问题前缀、Agent 任务复用模板和历史调用）
2. **单程序内并行**：Tree-of-Thought、Skeleton-of-Thought 中的并行生成调用
3. **约束解码加速**：JSON 解码使用压缩有限状态机一次解码多个 token

> 文本中的关键数字：
> - 多模态基准吞吐提升 **最高 6×**
> - 生产环境（Chatbot Arena）：**单 worker 每秒处理 52.4 个请求**
> - RadixAttention 缓存命中率：**LLaVA-NeXT-34B 74.1%，LLaVA-Nextt-34B 52.4%**
> - Vicuna-33B 首 token 延迟平均降低 **1.7×**

---

**4) 图上 caption 逐字转录**

**Figure 6:**
> Figure 6: Normalized latency on Llama-7B models. Lower is better.

**Figure 7:**
> Figure 7: Normalized throughput on Mixtral-8x7B models with tensor parallelism. Higher is better.

---

**附加：图例标签（X 轴任务名）**

> MMLU | ReAct Agents | Generate Agents | Tree of Thought | Skeleton of Thought | LLM Judge | HellaSwag | JSON Decoding | Multi-Turn Chat (short) | Multi-Turn Chat (long) | DSPy RAG Pipeline
*caption: Normalized latency on Llama-7B models. Lower is better. MMLU… ｜ 论文 [[sglang-efficient-execution-of-structured-language-model-programs]] ｜ arxiv 见 MD 元信息*

### SGLang: Efficient Execution of Structured Language Model Pro — Fig.8 (p.9)
![[assets/sglang-efficient-execution-of-structured-language-model-programs-p09.png]]
> [!tip] **SGLang论文第9页深度解读**

**1) 图类型**
**混合类型**：表格（Table 2，吞吐量对比）+ 三联子图（Figure 8，消融研究）。整体属于**消融实验 + 性能对比**页。**

**2) 核心内容**

**Table 2：多模态LLaVA吞吐量对比**
| Model | LLaVA-v1.5-7B (image) | LLaVA-NeXT-34B (video) |
|-------|---------------------|------------------------|
| Author's original implementation | 0.18 image/s | 0.02 frame/s |
| **SGLang** | **1.15 image/s** | **0.10 frame/s** |

→ 图像任务加速 **6.4×**，视频任务加速 **5×**

**Figure 8：三联消融图**
- **(a)** Cache Hit Rate vs Batch Size / Throughput（双Y轴折线）
  - 横轴：Cache Hit Rate 0–100%
  - 左轴（绿）：Batch Size 20→40+
  - 右轴（橙）：Throughput 0.4k→1.2k tokens/s
- **(b)** Cache Hit Rate vs Latency（双Y轴折线）
  - 红：Total Latency（s）从~400降到~100
  - 蓝：First Token Latency从~20降到~10
- **(c)** RadixAttention 组件消融柱状图（归一化吞吐量）
  - 4个基准：LLM Judge、Tree of Thought、MMLU、Multi-Turn Chat(short)
  - 7种配置：No Cache / No Tree Structure / FCFS Schedule / Random Schedule / No Frontend Parallelism / No Frontend Hint / **Full Optimization**

**3) 一个关键技术要点**

**RadixAttention 的"树结构 + LRU + 调度感知"三件套缺一不可。** Figure 8(c) 显示，禁用任何一个组件（缓存、树结构、调度策略、前端并行、前端hint）吞吐量都显著低于Full Optimization——尤其"Full Optimization"柱在所有基准上都接近1.0归一化值，而"No Cache"几乎贴近0。这印证了**前端语言（编程接口hint）与运行时共同设计**的重要性。**

附关键支撑数据：
- RadixAttention开销极低：管理数据结构仅0.2s/74.3s（**<0.3%**），可默认开启
- 压缩有限状态机使JSON解码吞吐量提升 **1.6×**，若不批量复用预处理反而会**降低2.4×**

**4) Caption逐字转录**

```
Table 2: Throughput comparison on multi-modal LLaVA image and video models.

Figure 8: (a)(b) Cache hit rate ablation study. (c) RadixAttention alation study.
```

（注：原图caption将"ablation"误拼为"alation"）

---

**附：6.3节消融结论摘要**
- **Cache命中率↑** → batch size↑、throughput↑、latency↓
- **RadixAttention各组件**：缓存、树结构、调度（cache-aware优于FCFS/Random）、前端并行、前端hint均为必需
- **运行时开销**：线性且微小（<0.3%）
- **压缩FSM**：批量复用是性能关键，per-request预处理会回退2.4×
*caption: (a)(b) Cache hit rate ablation study. (c) RadixAttention ablation study.… ｜ 论文 [[sglang-efficient-execution-of-structured-language-model-programs]] ｜ arxiv 见 MD 元信息*

### SGLang: Efficient Execution of Structured Language Model Pro — Fig.9 (p.14)
![[assets/sglang-efficient-execution-of-structured-language-model-programs-p14.png]]
> [!tip] **SGLang 论文页面深度解读**

**1) 图类型**

**架构/机制示意图（Mechanism Illustration）**：Figure 9 是**概念性/结构化的示意图**，用四种典型 LLM 编程模式（few-shot、self-consistency、multi-turn chat、tree-of-thought）展示 KV cache 的可共享结构。下文附录 A.1–A.3 包含**背景知识**（prefill/decoding/KV cache 定义）、**伪代码说明**和**定理证明**，整体属于论文方法论附录。**

---

**2) 核心内容**

**Figure 9 四个子图（颜色编码：蓝色=可共享 prompt 部分，绿色=不可共享部分，黄色=不可共享的模型输出）**

| 子图 | 模式 | 可共享结构（蓝） | 不可共享结构 |
|------|------|------------------|--------------|
| (a) Few-shot learning | 多个独立 Prompt 各自生成 | Few-shot examples（跨 Prompt 完全相同） | Question、Answer（每个 Prompt 不同） |
| (b) Self-consistency | 同一 Prompt 多次采样 | Question | Answer 1/2/3（多答案投票） |
| (c) Multi-turn chat | 对话多轮追加 | 累积的 Chat History | 当前轮的 Q/A |
| (d) Tree-of-thought | 树状推理分支 | 共享的 Search History 节点 | 各 Branch 状态 |

**关键概念**
- **KV Cache 定义**：自回归 Transformer 在 prefill 与 decoding 中产生的 key-value 对，仅依赖先前 token，因而**前缀相同则可复用**。
- **四种 sharing pattern**：现有系统（vLLM 仅支持 basic prefix sharing）**无法全部自动处理**，RadixAttention 能在运行时自动统一处理。
- **Theorem 3.1**（A.3）：当 cache size ≥ 最大请求长度时，**以 DFS（depth-first search）/ longest-shared-prefix-first 顺序遍历 radix tree，可获得最优 cache 命中率**。

---

**3) 一个关键技术要点**

> **RadixAttention 的核心机制**：将多请求的 prompt 视为一棵 radix tree，对共享前缀做 LRU 驱逐而非按请求驱逐，并以 DFS 顺序调度 batch，使得任意树形/分支/重复前缀结构都能在连续 batching 中复用 KV cache，从而在工程上实现"任意复杂度 prompt 程序"的自动 cache-aware 调度。Figure 9 直观地展示了它要覆盖的四类不规则 sharing pattern——正是 vLLM 等仅支持线性 prefix sharing 的系统无法处理的场景。

---

**4) 图上 caption 逐字转录**

> **Figure 9: KV cache sharing examples. Blue boxes represent shareable prompt parts, green boxes indicate non-shareable parts and yellow boxes mark non-shareable model outputs. Shareable elements include few-shot learning examples, questions in self-consistency [53], chat history in multi-turn chat, and search history in tree-of-thought [56].**

子图标签逐字转录：
- (a) Few-shot learning
- (b) Self-consistency
- (c) Multi-turn chat
- (d) Tree-of-thought

小框内文字逐字转录（按子图）：
- (a) Prompt 1 / Prompt 2 / Prompt 3；Few-shot examples；Question 1/2/3；Answer 1/2/3
- (b) Prompt → Question → {Answer 1, Answer 2, Answer 3}，分别对应 Generation 1/2/3
- (c) Turn 1 (Q/A) … Turn 4 (Q/A)；Chat History（每轮累积）
- (d) Question → Search History → Branch 1.1 / Branch 1.1.1 / Branch 1.1.1.1 / Branch 1.2 / Branch 1.2.1 / Branch 2 / Branch 2.1 / Branch 2.1.1 / Branch 2.2 / Branch 2.2.1
*caption: KV cache sharing examples. Blue boxes represent shareable prompt parts, green boxes indicate non-shareable parts and yellow boxes mark non-shareable m… ｜ 论文 [[sglang-efficient-execution-of-structured-language-model-programs]] ｜ arxiv 见 MD 元信息*

### SGLang: Efficient Execution of Structured Language Model Pro — Fig.10 (p.17)
![[assets/sglang-efficient-execution-of-structured-language-model-programs-p17.png]]
> [!tip] **SGLang论文 Figure 10 深度解读**

**1) 图类型**
**架构/流程示意 + 案例演示图**。该图综合展示了**正则表达式 → FSM → 受约束解码**的完整工作流，并用两个Harry Potter信息填充实例演示FSM如何动态屏蔽非法token。**

**2) 核心内容**

**组件构成（从左到右、自上而下）**

**① Regular Expression（正则源）**：JSON Schema片段**
```json
"name": "[\w\d\s]+",
"age": "[0-9]+",
"house": "(Gryffindor|Slytherin|Ravenclaw|Hufflepuff)"
```
高亮部分是 `"age": "[0-9]+"`，对应右边的FSM子图。

**② Finite State Machine（有限状态机）**：8个状态节点（0–7），其中：**
- 状态0→1→2→3→4→5→6→7构成线性骨架，对应 `"age": "` 这段固定字符串
- 状态6带**[0-9]自环**，匹配一个或多个数字字符
- 边上的字符集标记是**token屏蔽的依据**

**③ Decoding Status（解码状态）**：两轮解码快照**
- **第1轮**：已生成 `{"name":"Harry",`，合法下一token为 `age ✓`；`Age ✗`（大小写敏感被拒）、`hou ✗`（无法闭合JSON结构）
- **第2轮**：已生成 `{"name":"Harry","age":`，合法下一token为 `0 ✓`、`1 ✓`；`fir ✗`（数字上下文屏蔽）

图例：`✓ allowed next token`，`✗ not allowed next token`。

**3) 关键技术要点**

**Logits Mask驱动的字符级约束解码**：FSM的每个状态维护一组**当前合法字符集**（accepting set）。解码时，SGLang将该集合与**token词表求交集**，生成logits mask——交集内的token logits保留，交集外token logits置为−∞。如此：**
- ✅ **保证结构合法性**：JSON括号、引号、字段名逐字符对齐，永不偏离schema
- ✅ **保证语义合法性**：`age`字段只能接数字字符，即使模型倾向于生成"Fifteen"也会被屏蔽
- ✅ **实现零重写**：无需重采样或后处理修改，结构化输出一次到位

**4) Caption逐字转录**

> **Figure 10**: Example of how regex is converted into FSM and how FSM guides the decoding process.

---

**补充：与下文B.1/B.2节的关联**

正文紧接着讨论**Compressed FSM**（B.1）与**Retokenization**（B.2）：
- **B.1**：将字符级FSM中"源节点出度唯一 + 边字符集单一"的边（singular transition edge）递归合并为一条compressed edge（文本拼接），例如 `"age": "` 这段8步线性路径可压缩为单边跳转，加速匹配。
- **B.2**：当compressed边很长时引入**Jump Forward**机制——预读后续解码字符串，但因LLM的token化粒度与字符级FSM不一致，仍需retokenization对齐，从而在保证正确性的同时获得加速。
*caption: Example of how regex is converted into FSM and how FSM guides the decoding process.… ｜ 论文 [[sglang-efficient-execution-of-structured-language-model-programs]] ｜ arxiv 见 MD 元信息*

### SGLang: Efficient Execution of Structured Language Model Pro — Fig.11 (p.18)
![[assets/sglang-efficient-execution-of-structured-language-model-programs-p18.png]]
> [!tip] **SGLang论文 Figure 11 深度解读**

**1) 图类型**
**架构/流程对比图**（不是结果图）。属于"机制示意"类别：用 token 级别的展开图，对比两种 FSM-guided 解码方式在结构化生成中的执行路径差异。**

**2) 核心内容**

**组件构成**
- **左上图（Jump-Forward Decode With Compressed FSM）**：上半部为 Prefill（绿色块：`Please fill in the following information about Harry Potter.`），其后跟一连串橙色块（Jump-Forward 一次性跳过的 token 序列）和少量蓝色 Decode token。
- **左下图（Normal Decode With FSM）**：相同 Prefill 后，逐 token 展开的"密集蓝块"序列，每个结构化 token 都被独立解码。
- **右栏（Generated JSONs）**：两种方式最终输出的等价 JSON 内容：
  ```
  {
    "name": "Harry",
    "age": 15,
    "house": "Gryffindor"
  }
  ```

**关键 Token 流对比**
| 元素 | Compressed FSM（Jump-Forward） | Normal FSM |
|---|---|---|
| `{` `"name":"` `Harry` `"age":` `15` `"house":` `"Gryffindor"` `}` | 橙色块一次性 jump | 逐 token 蓝色解码 |
| 关键"内容 token" | 蓝色（`Har/ry/_Pot/ter/1/G/ryffindor`） | 全部蓝色 |
| 前向传播次数 | **显著减少** | 逐 token |

**图例（Legend）**
- 🟩 **Prefill**（绿色）：一次性前缀编码
- 🟦 **Decode**（蓝色）：常规自回归解码
- 🟧 **Jump-Forward**（橙色）：由 FSM 确定性"快进"跳过的 token

**3) 一个关键技术要点**

**Jump-Forward 解码的本质**：当 Compressed FSM 通过 regex/grammar 推断出某些 token 序列是**确定性必须出现**的（如空白 `_____`、引号 `"`、冒号 `:`、逗号 `,`、花括号 `{}`），无需 LLM 参与采样——直接在一次 forward pass 内将这些 token 整体"注入"到输出流，并只对真正的"自由 token"（如 `Harry`、`15`、`Gryffindor`）调用模型。**

**带来的收益**：**
- **减少 N 次 forward → 减少 N-1 次 decode step**，显著降低结构化输出（如 JSON、函数调用、regex-guided 文本）的端到端延迟；
- **不改变输出语义**：右侧 Generated JSONs 完全一致；
- **配合 B.2 节的 retokenization**：压缩 FSM 在跳进前会调用原 tokenizer 重对齐，避免"字符串↔token"边界错位（如 `summary` 不能被切成 `summa`+`ry`）。

这一机制是 SGLang 在结构化生成（JSON mode / regex / EBNF）场景下实现高吞吐的核心优化路径。

**4) Caption 逐字转录**

> **Figure 11**: Comparison of decoding using Compressed FSM versus normal FSM: The left subfigure depicts the decoding process per forward pass, while the right subfigure explains the origins of various result components.

**中文翻译**：**
> 图 11：使用 Compressed FSM 解码与使用普通 FSM 解码的对比：左侧子图描绘每次前向传播中的解码过程，右侧子图解释各输出结果的来源构成。
*caption: Comparison of decoding using Compressed FSM versus normal FSM: The left subfigure depicts the decoding process per forward pass, while the right subfi… ｜ 论文 [[sglang-efficient-execution-of-structured-language-model-programs]] ｜ arxiv 见 MD 元信息*

### SGLang: Efficient Execution of Structured Language Model Pro — Fig.12 (p.19)
![[assets/sglang-efficient-execution-of-structured-language-model-programs-p19.png]]
> [!tip] **SGLang论文第19页深度解读**

**一、图类型判定**

本页包含**两张结果对比图** + **两节技术正文**，均为性能基准与编译器设计内容的组合。

---

**二、Figure 12: 吞吐量归一化对比（结果图）**

**核心内容：**
- **Y轴**：Throughput (Normalized)，范围0.0–1.0
- **X轴**：11个基准测试任务，覆盖推理（MMLU、HellaSwag）、智能体（ReAct Agents、Generative Agents、Tree of Thought、Skeleton of Thought、LLM Judge）、结构化输出（JSON Decoding）以及多轮对话（短/长Chat、DSPy RAG Pipeline）
- **对比对象**：SGLang（橙色）vs vLLM（绿色）
- **实验设置**：Llama-2-70B模型 + 张量并行（tensor parallelism）
- **关键数字**：SGLang在所有基准上均显著优于vLLM，部分场景吞吐量倍数达到约3–6倍（vLLM柱体高度仅0.1–0.4左右）。ReAct Agents、MMLU、JSON Decoding、Multi-Turn Chat(long) 差距尤为悬殊。

---

**三、Figure 13: 缓存命中率分析（结果图）**

**核心内容：**
- **Y轴**：Cache Hit Rate (%)
- **对比**：Achieved cache hit rate with SGLang（橙色）vs Optimal cache hit rate（浅蓝）
- **关键观察**：
  - 在MMLU、ReAct Agents、Tree of Thought、Skeleton of Thought、HellaSwag、JSON Decoding、DSPy RAG Pipeline等任务上，SGLang的**实际命中率已接近理论最优值**（差距通常<5%）
  - **短板任务**：Multi-Turn Chat(short)和Multi-Turn Chat(long)实际命中率明显低于最优（Multi-Turn Chat(short)约50% vs 最优约60%；Multi-Turn Chat(long)约55% vs 最优约75%），存在20%左右的优化空间
  - **LLM Judge**任务几乎100%达成最优

---

**四、一个关键技术要点：**RadixAttention前缀缓存的近似最优性**

这两张图联合验证了SGLang的核心创新——**基于Radix Tree的自动前缀缓存机制**：
1. Figure 12证明该机制带来的**端到端性能收益**：通过KV cache复用，吞吐量实现数倍提升
2. Figure 13证明该机制的**效率上限**：在实际工作负载上命中率逼近理论最优，说明缓存调度算法（自动radix树匹配 + LRU驱逐）设计精良
3. 多轮对话场景的命中率差距揭示了**未来优化方向**——需要处理长前缀拼接、上下文碎片化等真实场景问题

---

**五、正文关键技术：D.1 中间表示(IR)与D.2 编译器优化**

**D.1 Design and Implementation — IR图设计**
- **IR本质**：将SGLang程序表示为**计算图**，节点为原始算子，边为依赖关系
- **节点类型**：包括 `ConstantText`、`Argument`、`Gen`、`Select`、`Variable`、`Fork`、`GetForkItem`、`Join` 八种IR节点
- **两类依赖**：
  - **流内依赖**（intra-stream）：`+=` 操作必须等待流内所有前序操作完成
  - **流间依赖**（inter-stream）：跨流取值的同步需求，`fork`操作会引入此类依赖
- **构造方法**：**Tracing法**——用抽象参数运行程序动态构建图（受限于无数据依赖控制流的程序）
- **执行方式**：图构建后由**图执行器**执行，**流执行器**按拓扑序向各数据流派发IR节点

**D.2 Code Movement 优化案例**
- **优化目标**：通过**节点重排序**延长共享前缀长度，从而提升prefix sharing效率
- **激进优化性质**：不严格保持原始计算语义（aggressive optimization），属于非安全变换
- **典型例子**：将 `"Here is a question + {question}. Please act as a math expert and solve..."` 重排为 `"Please act as a math expert and solve the given question. Here is a question + {question}."` ——使公共指令前缀更长
- **创新点**：用GPT-4做**程序分析**（通过prompt + 若干SGLang IR示例），实现传统编译器技术难以自动完成的自然语言指令重排

---

**六、Caption逐字转录**

**Figure 12**: "Normalized throughput on Llama-2-70B models with tensor parallelism. Higher is better."**

**Figure 13**: "Achieved cache hit rate and optimal cache hit rate on various benchmarks."**
*caption: Normalized throughput on Llama-2-70B models with tensor parallelism. Higher is better. MMLU… ｜ 论文 [[sglang-efficient-execution-of-structured-language-model-programs]] ｜ arxiv 见 MD 元信息*

### SGLang: Efficient Execution of Structured Language Model Pro — Fig.14 (p.20)
![[assets/sglang-efficient-execution-of-structured-language-model-programs-p20.png]]
> [!tip] **SGLang论文第20页深度解读**

**1) 图类型**

**类型：架构/示例图 + 数据流图（混合型说明图）**

本图为**Figure 14**，由两个子图组成：
- **(a) 代码示例**：展示SGLang程序源码（Python风格DSL），用以说明语言语法
- **(b) 数据流图**：将代码翻译为runtime计算图，展示执行时的并行机会

属于"**程序与数据流对照图**"，是论文用于向读者解释SGLang语义和执行模型的"教学型"插图。

---

**2) 核心内容**

**(a) SGLang程序结构**

程序实现 **Skeleton-of-Thought（SoT）提示范式** 的并行化：

```python
@function
def expand(s, tip):           # 将简短tip展开为详细段落
    s += "Please expand the following tip into a detailed paragraph: " + tip + "\n"
    s += gen("paragraph")

@function
def tip_suggestion(s, topic):
    s += "Here are 2 concise tips for " + topic + ".\n"
    # 1. 生成骨架（短tips）
    s += "1." + gen("tip_1", stop=["\n",":","."]) + "\n"
    s += "2." + gen("tip_2", stop=["\n",":","."]) + "\n"
    # 2. 并行展开
    detailed_tip1 = expand(tip=s["tip_1"])
    detailed_tip2 = expand(tip=s["tip_2"])
    # 3. 汇总
    s += "Tip 1: " + detailed_tip1["paragraph"] + "\n"
    s += "Tip 2: " + detailed_tip2["paragraph"] + "\n"
    s += "In summary" + gen("summary")
```

**关键技术语法**：**
- `@function` 装饰器：声明可复用子程序
- `gen(name, stop=...)`：调用LLM生成，`stop`参数控制生成边界
- `+=` 操作符：在共享state `s`上累积prompt
- `s["var"]`：从state中读取变量值

**(b) 数据流图**

三条**Stream**（流）对应三次函数调用：

| Stream | 角色 | 颜色 | 关键节点 |
|--------|------|------|----------|
| Stream 1 | tip_suggestion主函数 | 浅灰 | ConstantText, Argument(topic), Gen(tip_1/tip_2), Variable(paragraph), Gen(summary) |
| Stream 2 | expand(tip_1) | 黄色 | ConstantText("Please expand..."), Variable(tip_1), Gen(paragraph) |
| Stream 3 | expand(tip_2) | 蓝色 | ConstantText("Please expand..."), Variable(tip_1), Gen(paragraph) |

**数据依赖关系**：**
- Stream 1 的 `Gen("tip_1")` → Stream 1 的 `Variable("tip_1")` → 跨流边 → Stream 2 的 `Variable("tip_1")` → Stream 2 的 `Gen("paragraph")` → 跨流边 → Stream 1 的 `Variable("paragraph")`
- Stream 3 与 Stream 2 **结构对称**，二者之间无依赖 → **可并行执行**

**正文段落（评估结果）**

| 维度 | 数值/描述 |
|------|-----------|
| 收集prompt模板数 | 20 |
| 训练样本（few-shot） | 5 |
| 测试样本 | 15 |
| GPT-4成功重排序数 | 12 / 15 |
| 平均shareable prefix长度提升 | **+60 tokens** |
| 失败原因 | 过度激进地将所有常量前置，破坏语义 |
| 用途 | 探索GPT-4用于编译器优化 |

---

**3) 关键技术要点**

**🔑 核心：基于图结构的提示重排序（Prefix Merging / Reordering）**

SGLang允许用户以DSL表达LLM程序，runtime将其编译为**流式数据流图**。图中不同Stream的Gen节点**结构对称且互不依赖**，因此系统可将它们的前缀（包括常量prompt）合并成更长的**共享前缀（shareable prefix）**送入vLLM等引擎。

**该图揭示的本质**：SoT模式的两次expand调用，其prompt模板完全一致，仅输入的`tip`变量不同——这构成了**KV cache共享的机会**。通过GPT-4对图节点重排序，能将更多常量与可前缀共享的内容组织在一起，从而**延长KV cache复用的prefix长度，降低prefill冗余计算**。**

实验结果量化了此优化的有效性：**平均多共享60个token的prefix**，直接转化为吞吐量提升。

---

**4) 图上Caption逐字转录**

**Figure 14: An SGLang program and its corresponding dataflow graph.**

**子图caption (a)**：**
> The SGLang program for parallel tip suggestion with skeleton-of-thought prompting.

**子图caption (b)**：**
> A computational graph for the program in Fig. 14a. The three streams correspond to three function calls.

**节点标签（按出现顺序转录）**：**

*Stream 1*：
- ConstantText ("Here are ...")
- Argument (topic)
- ConstantText ("\n")
- ConstantText ("1.")
- Gen ("tip_1")
- ConstantText ("\n")
- ConstantText ("2.")
- Gen ("tip_2")
- ConstantText ("\n")
- ConstantText ("Tip 1:")
- Variable ("paragraph")
- ConstantText ("\n")
- ConstantText ("Tip 2:")
- Variable ("paragraph")
- ConstantText ("\n")
- ConstantText ("In summary")
- Gen (name="summary")

*Stream 2*（黄色）：
- ConstantText ("Please expand ...")
- Variable ("tip_1")
- ConstantText ("\n")
- Gen ("paragraph")

*Stream 3*（蓝色）：
- ConstantText ("Please expand ...")
- Variable ("tip_1")
- ConstantText ("\n")
- Gen ("paragraph")
*caption: An SGLang program and its corresponding dataflow graph.… ｜ 论文 [[sglang-efficient-execution-of-structured-language-model-programs]] ｜ arxiv 见 MD 元信息*

### Mooncake: A KVCache-centric Disaggregated Architecture for L — Fig.1 (p.2)
![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p02.png]]
> [!tip] **论文核心架构图分析**

**1) 主要架构/组件/数据流描述**

该图为 **Mooncake 架构图**，展示了一种以 KVCache 为中心的 LLM 服务解耦架构：

- **组件**：左侧为输入请求队列；中间区域包含多个 GPU 实例节点，分为 **prefill（预填充）节点**（上半部，含 KVCache 池 "3.450678"）和 **decoding（解码）节点**（下半部，含 KVCache 池）；中央为全局调度器（Conductor），负责调度决策。
- **数据流**：请求首先被路由到 prefill 节点；prefill 计算产生的 KVCache（图中上方柱状图表示）通过高速互联被流式传输到对应的 decoding 节点；decoding 节点加载 KVCache 后进行连续批处理生成输出（右侧生成的文本序列 "!\"#$%..."）。箭头与乘号 ⊗ 标示预填充与解码节点间的 KVCache 流转与匹配关系。

**2) 关键技术要点**

**基于 KVCache 的预填充-解码解耦（Disaggregation）：** 预填充（compute-bound）与解码（memory-bound）两种异构负载被分离到不同实例，KVCache 作为"一等公民"在实例间显式流转，全局 Conductor 综合考虑 TTFT/TBT SLO、KVCache 命中率、DRAM 容量与网络拥塞进行实例配对与调度优化，从而实现吞吐与时延的联合优化。**

**3) 图注逐字转录**

> **Figure 1: Mooncake Architecture.**
*caption: Mooncake Architecture. remote location will prolong the TTFT, and a large batch size will lead to a larger TBT. Thus, the utilization of both these th… ｜ 论文 [[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]] ｜ arxiv 见 MD 元信息*

### Mooncake: A KVCache-centric Disaggregated Architecture for L — Fig.2 (p.4)
![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p04.png]]
> [!tip] 【MiniMax 解读】Mooncake 解耦式 KVCache 服务架构：prefill（compute-bound，注意力二次复杂度）与 decode（memory-bound，自回归批处理）分到独立节点池。核心是 disaggregated KVCache 层，池化 CPU/DRAM/SSD/RDMA 资源→跨节点 cache 复用、减冗余计算；调度器做 early rejection + SLO 准入(TTFT/TBT)+负载均衡。把计算阶段与 KVCache 存储解耦→弹性扩展、严 SLO 下更高吞吐。架构核心图。
*caption: Normalized throughput and latency of prefill and decoding stages with different sequence lengths or batch sizes for the dummy LLaMA2-70B model. the co… ｜ 论文 [[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]] ｜ arxiv 见 MD 元信息*

### MegaScale: Scaling Large Language Model Training to More Tha — Fig.2 (p.3)
![[assets/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-p03.png]]
> [!tip] **1) 架构/组件/数据流描述**

该图为**交错式 1F1B 流水线调度图**（Interleaved 1F1B Pipeline）。纵轴为 3 个流水线阶段（stage 0/1/2），横轴为时间步。每个阶段被细分为多个**虚拟子阶段**（图中以红、蓝色块区分），相同数字（如 0、1、2…5）代表同一 micro-batch 的前向/反向传递。红色虚线标出阶段内的交错切换点。整体体现"前向-反向交替执行"的 1F1B 节奏，以及通过虚拟子阶段增加流水线深度来减少气泡（pipeline bubble）的设计。

**2) 关键技术要点**

**核心创新**：将每个流水线阶段再切分为多个虚拟子阶段（virtual stages / model chunks），在相同内存占用下使同一时刻处于 in-flight 的 micro-batch 数翻倍，从而**显著降低流水线气泡比例**，提升训练吞吐——这是 Megatron-LM 交错调度相较于经典 1F1B 的关键改进。**

**3) 逐字转录 Caption**

> **Figure 2: Interleaved 1F1B pipeline.**
*caption: Interleaved 1F1B pipeline. update the model. Instead of duplicating model states (like the optimizer states, gradients, and parameters), Zero Redun- d… ｜ 论文 [[megascale-scaling-large-language-model-training-to-more-than-10000-gpus]] ｜ arxiv 见 MD 元信息*

### Efficient Memory Management for Large Language Model Serving — Fig.1 (p.1)
![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p01.png]]
> [!tip] 【MiniMax 解读】PagedAttention 内存布局(Fig.1)：13B 模型在 A100-40G 上参数占 65%（26GB 常驻）、KV cache >30%（每请求动态）、激活小片。传统系统把每请求 KV 存成单连续张量→内部+外部碎片严重、batch 受限。PagedAttention 借 OS 虚拟内存分页：KV 切成固定块（如 16 token）存非连续物理显存，每请求 block table 映射逻辑→物理（类比页表）；请求间可共享物理块（并行采样/beam search/前缀共享）；碎片仅剩 sub-block 余量（~1 token vs GB 级）→近乎零 KV 浪费、吞吐 2-4x。架构核心图，KV-cache/serving 基石。
*caption: Left: Memory layout when serving an LLM with 13B parameters on NVIDIA A100. The parameters (gray) persist in GPU memory throughout serving. The memory… ｜ 论文 [[efficient-memory-management-for-large-language-model-serving-with-pagedattention]] ｜ arxiv 见 MD 元信息*

### DeFT: Decoding with Flash Tree-attention for Efficient Tree- — Fig.1 (p.1)
![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p01.png]]
> [!tip] No figure is visible on this page — it is the title page of the paper "DEFT: Decoding with Flash Tree-Attention for Efficient Tree-structured LLM Inference," containing only the title, author affiliations, abstract, and the opening of the Introduction. The text references "Figure 1" (illustrating tree-structured LLM applications such as self-consistency, few-shot prompting, multi-step reasoning, and speculative decoding) and "Table 1" (showing token volume differences), but neither the figure nor its caption appears in the provided image, so I cannot describe the figure's architecture/components/data flow or transcribe its caption verbatim.
*caption: Usually, these applications produce substantially more tokens than traditional ones, to provide large space for tree search (Graves, 2012; Lu et al., … ｜ 论文 [[deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference]] ｜ arxiv 见 MD 元信息*

### DeFT: Decoding with Flash Tree-attention for Efficient Tree- — Fig.2 (p.5)
![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p05.png]]
> [!tip] 【MiniMax 解读】DeFT flash 树注意力(Fig.2)：① Input Metadata（Q + 共享前缀 K0 + 分支 K1/K2 + 树拓扑）载入 SM；② Phase1 QKV 准备(HBM 2TB/s)：KV-Guided Grouping 跨分支复用 K0、Flattened Tree KV Splitting 把树切成均衡组 G0/G1/G2 并行；③ Phase2 注意力计算(Shared Mem 19TB/s)：DeFT kernel 各 split 跑部分注意力 + 树拓扑感知全局归约(A0/A1/A2→Final)，避免跨全分支全局同步。消除共享前缀冗余 KV IO、平衡 SM 负载→内存高效、硬件友好的树结构投机解码注意力。架构核心图。
*caption: Overview of DEFT. Input Metadata is prepared in the system elaborated in Appendix A.1. In QKV… ｜ 论文 [[deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference]] ｜ arxiv 见 MD 元信息*

### DeFT: Decoding with Flash Tree-attention for Efficient Tree- — Fig.3 (p.6)
![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p06.png]]
> [!tip] ## Main Figure Description (≤120 words)

The figure compares QKV partitioning strategies for tree-structured KV cache attention in three panels:

**(a)** Dataflow: Decoding Tree Metadata → Phase 1 (QKV Preparation) → Phase 2 (Attention Calculation, loading groups $G_i$ onto SM$_i$). Contrasts Vanilla Tree Attention (low parallelism, dense causal mask) with Q-Guided vs. KV-Guided grouping.

**(b)** Q-Guided grouping (Flash-Attention, Flash-Decoding/Radix) loads the prefix KV$_0$ redundantly for each query group, while KV-Guided grouping (DeFT-Node, DeFT-Node-Chunk) is IO-aware—KV$_0$ is loaded only once and shared.

**(c)** DeFT-Flatten performs load-balanced partitioning via depth-first flattening, blockwise splitting, and bitmask extraction (KV-BCM) for even workload distribution.

**Key takeaway:** KV-Guided grouping eliminates redundant prefix KV loads by binding each KV node to all queries sharing it, making the partitioning prefix-aware and IO-efficient compared to query-driven baselines.

## Caption (verbatim)

**Figure 3: Comparison of QKV partitioning strategies during the QKV Preparation Phase between DeFT-Node/Node-Chunk/Flatten and different attention algorithm baselines.** Note that the partitioning is logically designed without incurring any data movement costs for QKV. The amount of IO between the GPU HBM and shared memory required by each group is highlighted in red rectangles. Part (a) illustrates the dataflow of a two-cascaded decoding tree example and three categories of QKV partitioning strategies: no partition(Vanilla Tree Attention), Q-Guided Grouping and KV-Guided Grouping. The partitioning strategy will guide the loading of QKV during the subsequent *Attention calculation phase*, where each QKV group $G_i$ will be loaded into $SM_i$ on the GPU. Part (b) shows the comparison of Q-Guided Grouping and KV-Guided Grouping, where the latter can be IO-aware of prefix KV cache $KV_0$ and only load it once. DeFT-Node-Chunk is a weak load-balancing improvement of DeFT-Node by splitting large nodes (e.g., $KV_0$) to chunks. Part (c) illustrates the details (discussed in Remark 3.1) of Flattened Tree KV Splitting in DeFT-Flatten for load-balanced partitions, including Depth-first Flatten strategy, Evenly block-wise strategy, and Bit mask. For a summary of baselines and DeFT, see Table 2. See analysis of tree-attention baselines (Cai et al., 2024; Miao et al., 2023) in Remark 3.2.
*caption: Comparison of QKV partitioning strategies during the QKV Preparation Phase between DEFT-… ｜ 论文 [[deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference]] ｜ arxiv 见 MD 元信息*

### NanoFlow: Towards Optimal Large Language Model Serving Throu — Fig.1 (p.3)
![[assets/nanoflow-towards-optimal-large-language-model-serving-throughput-p03.png]]
> [!tip] 【MiniMax 解读】NanoFlow Transformer 流水(Fig.1)：算子分三类——compute-bound（W_O/K/V/up/down/gate 密集投影，跨请求共享权重、大 batch 摊权重载入）、memory-bound（prefill/decode attention，载每请求 KV、小 batch 避压 KV）、network-bound（AllGather/AllReduce，NVLink 同步）。device-stream 级算子融合：沿关键路径重排+协调度，单设备内只跨 CUDA stream 注入 micro-batch 状态→串行依赖转并行，吞吐 1.91x、达理论峰 68.5%。异构 batch 是关键。架构核心图。
*caption: Transformer architecture. The operations in the yellow boxes have large batch sizes and share model weight parameters across requests; hence, they are… ｜ 论文 [[nanoflow-towards-optimal-large-language-model-serving-throughput]] ｜ arxiv 见 MD 元信息*

### Gated Delta Networks: Improving Mamba2 with Delta Rule — Fig.1 (p.7)
![[assets/gated-delta-networks-improving-mamba2-with-delta-rule-p07.png]]
> [!tip] 【MiniMax 解读】Gated DeltaNet 架构(Fig.1)：delta-rule 线性注意力 + 乘性门控(α,β)增联想召回；H1/H2 混合变体把 Gated DeltaNet 与 Mamba2(SSM) + Sliding-Window Attention 交错，融合选择性长程记忆+结构化递归+局部上下文。block 设计：q/k 路径=线性投影+shortconv+SiLU+L2norm，v=线性投影+shortconv+SiLU，α/β=线性投影，输出 gate=线性投影+SiLU。Wiki ppl 16.42、zero-shot 55.32，H2 混合 ppl 15.91 最优。线性注意力/SSM 架构核心图。
*caption: Visualization of the (hybrid) architecture and block design of Gated DeltaNet models.… ｜ 论文 [[gated-delta-networks-improving-mamba2-with-delta-rule]] ｜ arxiv 见 MD 元信息*

### Parallel Scan on Ascend AI Accelerators — Fig.3 (p.3)
![[assets/parallel-scan-on-ascend-ai-accelerators-p03.png]]
> [!tip] 【MiniMax 解读】⭐Ascend 910B AI Core 架构(Fig.3)：单 AI Core = 1 个 AI Cube(AIC 矩阵乘引擎) + 2 个 AI Vector(AIV SIMD 核)，各有独立 Unified Buffer(UB) scratchpad，加 Memory Transfer Engine(MTE)+标量+控制块。AIC/AIV 共享全局 HBM/L2，Cube↔Vector 数据交换须走全局内存/L2（AIC 无直接写 AIV UB 的本地路径）。并行 scan：AIV 跑 element-wise/局部 scan + 解耦 look-back（在 UB 上），AIC 改作跨块前缀累积（矩阵乘式），MTE 编排块级 tile 传输。⭐结论：Ascend 非对称 Cube/Vector 划分 + UB 局部计算 + Cube↔Vector 仅全局通信→偏好 block-tiled、通信最小化的解耦 scan 设计，而非密集 GEMM 中心。直击昇腾线性注意力/SSM scan。
*caption: 1 shows the Ascend architecture where the… ｜ 论文 [[parallel-scan-on-ascend-ai-accelerators]] ｜ arxiv 见 MD 元信息*

### Kimi K3: Open Frontier Intelligence — Fig.2 (p.3)
![[assets/kimi-k3-open-frontier-intelligence-p03.png]]
> [!tip] Kimi K3 架构总览：每个 block 由 3 层 Kimi Delta Attention (KDA) + 1 层 Gated MLA 组成混合注意力，每个注意力层后接 Stable LatentMoE（16/896 路由专家+共享专家）做稀疏 channel mixing。深度维度引入 Attention Residuals (AttnRes)：用可学习 pseudo-query w 对 embedding 及前序各 block 输出算注意力权重 α，实现跨层选择性信息检索，突破顺序残差累积。输入侧原生视觉通路：MoonViT-V2 编码图像/视频经轻量 projector 映射进共享 embedding 空间。token/channel/layer 三维信息流设计，scaling 效率较 K2 提升 ~2.5×。
*caption: The Kimi K3 architecture, organized around token, channel, and layer mixing, with a native vision pathway at the input.… ｜ 论文 [[kimi-k3-open-frontier-intelligence]] ｜ arxiv 见 MD 元信息*

### Kimi K3: Open Frontier Intelligence — Fig.3 (p.5)
![[assets/kimi-k3-open-frontier-intelligence-p05.png]]
> [!tip] 下界衰减与 chunkwise KDA 计算：(a) Kimi Linear 用无界 negative-Softplus 映射 g=−e^A·Softplus(z)，K3 改为 g=g_min·Sigmoid(e^A·z) 把 log-decay 下界到 g_min=−5；(b) 有界范围使所有 causal tile（含对角 tile）都能用稠密 Tensor Core 矩阵乘，消掉逐位置对的 diagonal 路径。g_min=−5 时 16-token tile 累计 log-decay∈(−80,0)，rescale 因子 <e^80 仍在 BF16 动态范围内——分块线性注意力在 Tensor Core/NPU 上高效落地的关键参数化技巧。
*caption: Lower-bounded decay and its effect on chunkwise KDA computation. (a) Kimi Linear uses an unbounded negative-Softplus mapping, whereas Kimi K3 bounds t… ｜ 论文 [[kimi-k3-open-frontier-intelligence]] ｜ arxiv 见 MD 元信息*

### Kimi K3: Open Frontier Intelligence — Fig.5 (p.8)
![[assets/kimi-k3-open-frontier-intelligence-p08.png]]
> [!tip] **1) 架构描述**

图示展示 MoE 路由的 **Quantile Balancing (QB)** 三阶段流程：
- **(a) 不均衡路由**：8 个 token 通过 Top-1 路由到 4 个专家，产生负载 (4,3,1,0)；深色圆圈表示过载专家，浅色虚线圈表示欠训专家。
- **(b) Quantile Balancing**：每个专家列添加偏置调整 $b_j^{(t+1)} - b_j^{(t)}$（红色虚线），置于 margin $s_{i,j} + b_j^{(t)} - \alpha_i^{(t)}$ 的第 (q+1) 大值处，使得恰好 q=2 个 margin 高于阈值；★ 标记减去列调整后的行级 Top-k 选择。
- **(c) 均衡路由**：调整后负载变为 (2,2,2,2)，红色边表示被 QB 修改的分配。

**2) 关键技术要点**

**无辅助损失的负载均衡**：QB 通过单次前向传播从路由器得分分位数直接推导专家偏置 $b_j$，既调节分发又不影响混合权重 $p_{i,j}$ 与路由器梯度更新，避免了传统辅助损失在大规模专家池（如 LatentMoE 的 896 个专家）下适应性慢、易振荡的问题。**

**3) 图注逐字转录**

**Figure 5**: Illustration of Quantile Balancing with $m=8$ tokens, $n=4$ routed experts, and $k=1$ selected expert per token. (a) Token-wise Top-$k$ routing (tokens on the left, experts on the right) produces loads (4, 3, 1, 0); darker circles indicate overheated experts, whereas faded and dashed circles indicate underutilized and dying experts, respectively. (b) Each gray bar is the margin of the currently biased score, $s_{i,j} + b_j^{(t)} - \alpha_i^{(t)}$, so the row-wise maxima reproduce the routing in (a). The dashed red line in each column is the bias adjustment $b_j^{(t)} - \widehat{b}_j^{(t+1)}$, placed at the $(q+1)$-th largest margin so that exactly $q=2$ margins exceed it. The marker ★ denotes the row-wise Top-$k$ choice after subtracting the column adjustments, i.e., the routing in (c). (c) The retained choices yield the balanced load (2, 2, 2, 2); red edges denote assignments changed by **QB**.**
*caption: Illustration of Quantile Balancing with m = 8 tokens, n = 4 routed experts, and k = 1 selected expert per token. (a)… ｜ 论文 [[kimi-k3-open-frontier-intelligence]] ｜ arxiv 见 MD 元信息*

### Prefill-as-a-Service: KVCache of Next-Generation Models Coul — Fig.3 (p.6)
![[assets/prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter-p06.png]]
> [!tip] PrfaaS-PD 部署拓扑：Request Router 按长度阈值 t 分流——长请求 (l>t) 送独立 PrfaaS 集群（高算力 prefill 节点+集群内 RDMA），短请求留本地 PD 集群（高显存带宽）。PrfaaS 产出的 KVCache 经普通跨集群以太网传到本地 PD 集群 decode；两侧各挂 Hybrid Prefix Cache Pool（linear state 与 full-attention KV 分组、统一 block pool），Global KVCache Manager 全局协调。核心洞察：hybrid-attention 模型 KV 流量降一个数量级后（1T 模型 ~170Gbps、万卡总出口 ~1.8Tbps），跨数据中心 prefill 卸载在物理链路上首次可行。
*caption: Deployment topology of the PrfaaS-PD architecture.… ｜ 论文 [[prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter]] ｜ arxiv 见 MD 元信息*

### LongSpec: Long-Context Lossless Speculative Decoding with Ef — Fig.2 (p.4)
![[assets/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-p04.png]]
> [!tip] LongSpec 三件套：(a) 内存高效 draft 模型——滑窗自注意力（定长窗口捕捉局部）+ 无 KV cache 的 cross-attention（直接读 target 模型 last-layer K/V 收长程信息），draft KV 占用变常数；(b) Anchor-Offset Indices——保留前 4 个位置作 attention sink，其余 token 从随机大 offset 连续编号，短上下文训练即可覆盖大位置索引、且 target 模型不 OOD（loss 仅 +0.001），弥合训练-推理位置错配；(c) Hybrid Tree Attention——前缀走 FlashAttention（快）+ tree 走 Triton mask attention（灵活），兼得两者。
*caption: Illustration of the memory-efficient draft model, the Anchor-Offset Indices, and the Hybrid Tree Attention. (a) We use a sliding window self-attention… ｜ 论文 [[longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification]] ｜ arxiv 见 MD 元信息*

### SpecExtend: A Drop-in Enhancement for Speculative Decoding o — Fig.2 (p.2)
![[assets/specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences-p02.png]]
> [!tip] SpecExtend 总览：长输入分 chunk，target/draft 双模型 prefill 用 FlashAttention、verify 用 Hybrid Tree Attention 加速；核心 Cross-model Retrieval——用 target 模型 verify 阶段产出的 attention score 选出最相关 chunk（图中 1/3/7/8）动态保留进 draft KV cache，免训练同时提升 draft 速度与精度（平均接受长度最高 +2.55×；16K 摘要 2.84×、AIME-24 长推理 3.86× 加速）。training-free drop-in，可直接套 EAGLE-3 等短上下文优化的 draft。
*caption: Overview of SpecExtend. FlashAttention accelerates the prefill phases of both target and draft models, and Hybrid Tree Attention accelerates the verif… ｜ 论文 [[specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences]] ｜ arxiv 见 MD 元信息*

## 按主题分类

### architecture (45)

- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p01.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.1 (p.1): ATOP search results on different GPU scales, each point representing a topology.…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p03.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.2 (p.3): GPT-3 training timeline on rank 0 of classical in- terleaved 1F1B schedule, excl…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p04.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.3 (p.4): (a) The max number of flow per 100 Gbps under all-to-all traffic in a 256-GPUs t…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p05.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.4 (p.5): Overview of ATOP allows the system to explore novel topology designs automatical…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p06.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.5 (p.6): Examples of constructing inter-layer and intra-layer connections in ATOP. Unment…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p09.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.6 (p.9): During the 4k GPUs search process: (a) The Pareto- optimal topologies generated …  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p09.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.7 (p.9): (a) The search results of ATOP when adjusting an existing 4k-GPU DCN. (b) The se…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p10.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.8 (p.10): (a) A ZCube(n, k+1) is constructed from 𝑛ZCube(n, k) and 𝑛𝑘switches. (b) An exam…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p11.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.9 (p.11): The training iteration time for GPT-3 175B and MoE-GPT models and the correspond…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p11.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.10 (p.11): CDF of PP flow completion time during a GPT-3 175B training iteration on 16384 G…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p12.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.11 (p.12): The topology diagrams of ROFT and ZCube on a real testbed. 1M 4M 16M 64M 256M 1G…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p12.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.12 (p.12): Collective communication performance on real- world deployment. ZCube and ROFT a…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p15.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.13 (p.15): In the search results of Case 3, the comparison between the number of modified l…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p15.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.14 (p.15): The search results of ATOP when building a new data center for multi-tenancy.…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p15.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.15 (p.15): The search results of ATOP when building a new heterogeneous data center with st…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p16.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.16 (p.16): During the ATOP optimization process: (a) The relationship between the number of…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p17.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.17 (p.17): Two scenarios degrade all-to-all performance: (a) ECMP hash collision: In Non-bl…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p17.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.18 (p.17): The average JCT for group all-to-all communica- tion under different topologies …  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p18.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.19 (p.18): Comparison between packet-level network simulation (with packet spraying for loa…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p19.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.20 (p.19): Comparison of the CDF of flow completion times between NS-3 and flow-level simul…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p20.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.21 (p.20): ROFT topology for a 16384 GPU cluster based on 51.2 Tbps switches.…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p20.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.22 (p.20): Rail-only topology for a 16384 GPU cluster based on 51.2 Tbps switches. Each Rai…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p20.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.23 (p.20): HPN topology (dual-port designs for ROFT) for a 16384 GPU cluster based on 51.2 …  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p20.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.24 (p.20): ZCube(128,2) topology for a 16384 GPU cluster based on 51.2 Tbps switches. 880…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p01.png]] — **Efficient Large-Scale Language Model Training on G** Fig.1 (p.1): Trend of sizes of state-of-the-art Natural Language Pro- cessing (NLP) models wi…  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p03.png]] — **Efficient Large-Scale Language Model Training on G** Fig.2 (p.3): Combination of tensor and pipeline model parallelism (MP) used in this work for …  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p03.png]] — **Efficient Large-Scale Language Model Training on G** Fig.3 (p.3): GPipe pipeline schedule with forward passes (blue) for all microbatches (represe…  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p03.png]] — **Efficient Large-Scale Language Model Training on G** Fig.4 (p.3): Default and interleaved 1F1B pipeline schedules. The top figure shows the defaul…  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p05.png]] — **Efficient Large-Scale Language Model Training on G** Fig.5 (p.5): Blocks of transformer model partitioned with tensor model parallelism (figures b…  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p05.png]] — **Efficient Large-Scale Language Model Training on G** Fig.6 (p.5): Fraction of time spent idling due to pipeline flush (pipeline bubble size) versu…  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p06.png]] — **Efficient Large-Scale Language Model Training on G** Fig.7 (p.6): Per-GPU throughput versus microbatch size for a GPT model with a billion paramet…  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p06.png]] — **Efficient Large-Scale Language Model Training on G** Fig.8 (p.6): Behavior of normalized estimated throughput (time com- puted as 𝑡= (𝑏′/𝑏+ 𝑝−1) ·…  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p07.png]] — **Efficient Large-Scale Language Model Training on G** Fig.9 (p.7): Scatter/gather communication optimization. Light blue blocks are layers in the f…  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p08.png]] — **Efficient Large-Scale Language Model Training on G** Fig.10 (p.8): Throughput per GPU of PTD-P and ZeRO-3 for two differ- ent GPT models (the 175B …  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p09.png]] — **Efficient Large-Scale Language Model Training on G** Fig.11 (p.9): Throughput per GPU of pipeline parallelism using two different batch sizes in a …  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p09.png]] — **Efficient Large-Scale Language Model Training on G** Fig.12 (p.9): Throughput per GPU of interleaved and non-interleaved schedules for a GPT model …  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p09.png]] — **Efficient Large-Scale Language Model Training on G** Fig.13 (p.9): Throughput per GPU of various parallel configurations that combine pipeline and …  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p10.png]] — **Efficient Large-Scale Language Model Training on G** Fig.14 (p.10): Throughput per GPU of various parallel configurations that combine data and pipe…  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p10.png]] — **Efficient Large-Scale Language Model Training on G** Fig.15 (p.10): Throughput per GPU of various parallel configurations that combine data and tens…  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p10.png]] — **Efficient Large-Scale Language Model Training on G** Fig.16 (p.10): Throughput per GPU of a (𝑡, 𝑝) = (8, 8) parallel configura- tion for different m…  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p11.png]] — **Efficient Large-Scale Language Model Training on G** Fig.17 (p.11): Throughput (in sequences per second) with and without activation recomputation f…  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p11.png]] — **Efficient Large-Scale Language Model Training on G** Fig.18 (p.11): Throughput per GPU with and without the scatter/gather optimization for a GPT mo…  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ⭐ ![[assets/gated-delta-networks-improving-mamba2-with-delta-rule-p07.png]] — **Gated Delta Networks: Improving Mamba2 with Delta ** Fig.1 (p.7): Visualization of the (hybrid) architecture and block design of Gated DeltaNet mo…  `[[gated-delta-networks-improving-mamba2-with-delta-rule]]`
- ![[assets/gated-delta-networks-improving-mamba2-with-delta-rule-p08.png]] — **Gated Delta Networks: Improving Mamba2 with Delta ** Fig.2 (p.8): Length extrapolation on six long benchmarks.…  `[[gated-delta-networks-improving-mamba2-with-delta-rule]]`
- ![[assets/gated-delta-networks-improving-mamba2-with-delta-rule-p09.png]] — **Gated Delta Networks: Improving Mamba2 with Delta ** Fig.3 (p.9): Training throughput comparison of 1.3B models on a single H100 GPU. standalone m…  `[[gated-delta-networks-improving-mamba2-with-delta-rule]]`

### disaggregated-serving (66)

- ![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p01.png]] — **SARATHI: Efficient LLM Inference by Piggybacking D** Fig.1 (p.1): Example two-stage pipeline parallel schedule. (a)…  `[[sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills]]`
- ⭐ ![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p03.png]] — **SARATHI: Efficient LLM Inference by Piggybacking D** Fig.2 (p.3): High-level architecture of a decoder block. sequence length of each request (i.e…  `[[sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills]]`
- ![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p04.png]] — **SARATHI: Efficient LLM Inference by Piggybacking D** Fig.3 (p.4): Per-token prefill and decode time with different batch sizes (sequence length = …  `[[sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills]]`
- ![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p04.png]] — **SARATHI: Efficient LLM Inference by Piggybacking D** Fig.4 (p.4): Impact of the arithmetic intensity (bottom) on the throughput (top) of prefills …  `[[sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills]]`
- ![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p05.png]] — **SARATHI: Efficient LLM Inference by Piggybacking D** Fig.5 (p.5): Pipeline bubbles in LLM inference A 2-way PP iteration-level schedule [48] acros…  `[[sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills]]`
- ![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p06.png]] — **SARATHI: Efficient LLM Inference by Piggybacking D** Fig.6 (p.6): Example of how attention mask is set across dif- ferent chunk prefill iterations…  `[[sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills]]`
- ![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p07.png]] — **SARATHI: Efficient LLM Inference by Piggybacking D** Fig.7 (p.7): The effect of tile quantization on the runtime of one iteration of LLaMA-13B on …  `[[sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills]]`
- ![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p09.png]] — **SARATHI: Efficient LLM Inference by Piggybacking D** Fig.8 (p.9): Decode-only speedup with SARATHI on an A6000 GPU with LLaMA-13B (chunk size = 25…  `[[sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills]]`
- ![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p10.png]] — **SARATHI: Efficient LLM Inference by Piggybacking D** Fig.9 (p.10): Normalized throughput (tokens/ms) for LLaMa 13B on A6000 GPU with different sequ…  `[[sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills]]`
- ![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p10.png]] — **SARATHI: Efficient LLM Inference by Piggybacking D** Fig.10 (p.10): Breakdown of total time spent on different operations for LLaMa 13B on A6000 GPU…  `[[sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills]]`
- ![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p11.png]] — **SARATHI: Efficient LLM Inference by Piggybacking D** Fig.11 (p.11): Comparison with iteration-level scheduler Orca for LLaMa 13B on A6000 GPU. confi…  `[[sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills]]`
- ![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p12.png]] — **SARATHI: Efficient LLM Inference by Piggybacking D** Fig.12 (p.12): Impact of SARATHI on pipeline bubbles (top) and request completion times (bottom…  `[[sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills]]`
- ![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p13.png]] — **SARATHI: Efficient LLM Inference by Piggybacking D** Fig.13 (p.13): Ablation study: Effect of varying the chunk size on different components of the …  `[[sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills]]`
- ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p01.png]] — **Taming Throughput-Latency Tradeoff in LLM Inferenc** Fig.1 (p.1): Yi-34B running on two A100 GPUs serving 128 requests from arxiv-summarisation tr…  `[[taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve]]`
- ⭐ ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p02.png]] — **Taming Throughput-Latency Tradeoff in LLM Inferenc** Fig.2 (p.2): Current LLM serving systems involve a tradeoff be- tween throughput and latency …  `[[taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve]]`
- ⭐ ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p05.png]] — **Taming Throughput-Latency Tradeoff in LLM Inferenc** Fig.3 (p.5): Throughput of the prefill and decode phases with different batch sizes for Mistr…  `[[taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve]]`
- ⭐ ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p05.png]] — **Taming Throughput-Latency Tradeoff in LLM Inferenc** Fig.4 (p.5): Prefill and decode time with different input sizes for Mistral-7B running on sin…  `[[taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve]]`
- ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p06.png]] — **Taming Throughput-Latency Tradeoff in LLM Inferenc** Fig.5 (p.6): Arithmetic intensity trend for LLaMA2-70B lin- ear operations with different num…  `[[taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve]]`
- ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p06.png]] — **Taming Throughput-Latency Tradeoff in LLM Inferenc** Fig.6 (p.6): Linear layer execution time as function of number of tokens in a batch for LLaMA…  `[[taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve]]`
- ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p06.png]] — **Taming Throughput-Latency Tradeoff in LLM Inferenc** Fig.7 (p.6): A generation stall occurs when one or more prefills are scheduled in between con…  `[[taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve]]`
- ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p07.png]] — **Taming Throughput-Latency Tradeoff in LLM Inferenc** Fig.8 (p.7): A 2-way pipeline parallel iteration-level schedule in Orca across 4 requests (A,…  `[[taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve]]`
- ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p08.png]] — **Taming Throughput-Latency Tradeoff in LLM Inferenc** Fig.9 (p.8): The incremental cost of coalescing prefills with decode batches. We consider two…  `[[taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve]]`
- ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p11.png]] — **Taming Throughput-Latency Tradeoff in LLM Inferenc** Fig.10 (p.11): Capacity (in queries per second) of Mistral-7B and…  `[[taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve]]`
- ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p11.png]] — **Taming Throughput-Latency Tradeoff in LLM Inferenc** Fig.11 (p.11): Capacity of LLaMA2-70B and Falcon-180B (mod- els with pipeline parallelism) with…  `[[taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve]]`
- ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p12.png]] — **Taming Throughput-Latency Tradeoff in LLM Inferenc** Fig.12 (p.12): Latency – Throughput tradeoff in vLLM and…  `[[taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve]]`
- ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p12.png]] — **Taming Throughput-Latency Tradeoff in LLM Inferenc** Fig.13 (p.12): TP scales poorly across nodes. (a) Median TBT for decode-only batches: cross nod…  `[[taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve]]`
- ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p13.png]] — **Taming Throughput-Latency Tradeoff in LLM Inferenc** Fig.14 (p.13): Overhead of chunked-prefills in prefill computation for Yi-34B (TP-2) normalized…  `[[taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve]]`
- ⭐ ![[assets/sglang-efficient-execution-of-structured-language-model-programs-p02.png]] — **SGLang: Efficient Execution of Structured Language** Fig.1 (p.2): System architecture: An interpreter executes language primitives with optimized …  `[[sglang-efficient-execution-of-structured-language-model-programs]]`
- ⭐ ![[assets/sglang-efficient-execution-of-structured-language-model-programs-p03.png]] — **SGLang: Efficient Execution of Structured Language** Fig.2 (p.3): The implementation of a multi-dimensional essay judge in SGLang utilizes the bra…  `[[sglang-efficient-execution-of-structured-language-model-programs]]`
- ⭐ ![[assets/sglang-efficient-execution-of-structured-language-model-programs-p05.png]] — **SGLang: Efficient Execution of Structured Language** Fig.3 (p.5): Examples of RadixAttention operations with an LRU eviction policy, illustrated a…  `[[sglang-efficient-execution-of-structured-language-model-programs]]`
- ⭐ ![[assets/sglang-efficient-execution-of-structured-language-model-programs-p06.png]] — **SGLang: Efficient Execution of Structured Language** Fig.4 (p.6): The decoding process of normal and compressed FSMs (the underscore _ means a spa…  `[[sglang-efficient-execution-of-structured-language-model-programs]]`
- ⭐ ![[assets/sglang-efficient-execution-of-structured-language-model-programs-p07.png]] — **SGLang: Efficient Execution of Structured Language** Fig.5 (p.7): Normalized throughput on Llama-7B models. Higher is better. pattern: s += contex…  `[[sglang-efficient-execution-of-structured-language-model-programs]]`
- ⭐ ![[assets/sglang-efficient-execution-of-structured-language-model-programs-p08.png]] — **SGLang: Efficient Execution of Structured Language** Fig.6 (p.8): Normalized latency on Llama-7B models. Lower is better. MMLU…  `[[sglang-efficient-execution-of-structured-language-model-programs]]`
- ⭐ ![[assets/sglang-efficient-execution-of-structured-language-model-programs-p08.png]] — **SGLang: Efficient Execution of Structured Language** Fig.7 (p.8): Normalized throughput on Mixtral-8x7B models with tensor parallelism. Higher is …  `[[sglang-efficient-execution-of-structured-language-model-programs]]`
- ⭐ ![[assets/sglang-efficient-execution-of-structured-language-model-programs-p09.png]] — **SGLang: Efficient Execution of Structured Language** Fig.8 (p.9): (a)(b) Cache hit rate ablation study. (c) RadixAttention ablation study.…  `[[sglang-efficient-execution-of-structured-language-model-programs]]`
- ⭐ ![[assets/sglang-efficient-execution-of-structured-language-model-programs-p14.png]] — **SGLang: Efficient Execution of Structured Language** Fig.9 (p.14): KV cache sharing examples. Blue boxes represent shareable prompt parts, green bo…  `[[sglang-efficient-execution-of-structured-language-model-programs]]`
- ⭐ ![[assets/sglang-efficient-execution-of-structured-language-model-programs-p17.png]] — **SGLang: Efficient Execution of Structured Language** Fig.10 (p.17): Example of how regex is converted into FSM and how FSM guides the decoding proce…  `[[sglang-efficient-execution-of-structured-language-model-programs]]`
- ⭐ ![[assets/sglang-efficient-execution-of-structured-language-model-programs-p18.png]] — **SGLang: Efficient Execution of Structured Language** Fig.11 (p.18): Comparison of decoding using Compressed FSM versus normal FSM: The left subfigur…  `[[sglang-efficient-execution-of-structured-language-model-programs]]`
- ⭐ ![[assets/sglang-efficient-execution-of-structured-language-model-programs-p19.png]] — **SGLang: Efficient Execution of Structured Language** Fig.12 (p.19): Normalized throughput on Llama-2-70B models with tensor parallelism. Higher is b…  `[[sglang-efficient-execution-of-structured-language-model-programs]]`
- ⭐ ![[assets/sglang-efficient-execution-of-structured-language-model-programs-p19.png]] — **SGLang: Efficient Execution of Structured Language** Fig.13 (p.19): Achieved cache hit rate and optimal cache hit rate on various benchmarks. opport…  `[[sglang-efficient-execution-of-structured-language-model-programs]]`
- ⭐ ![[assets/sglang-efficient-execution-of-structured-language-model-programs-p20.png]] — **SGLang: Efficient Execution of Structured Language** Fig.14 (p.20): An SGLang program and its corresponding dataflow graph.…  `[[sglang-efficient-execution-of-structured-language-model-programs]]`
- ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p01.png]] — **Efficiently Serving Large Multimodal Models Using ** Fig.1 (p.1): Aggregated (top) vs. disaggregated (bottom) sys- tem architectures. In the aggre…  `[[efficiently-serving-large-multimodal-models-using-epd-disaggregation]]`
- ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p02.png]] — **Efficiently Serving Large Multimodal Models Using ** Fig.2 (p.2): Impact of disaggregation on supported batch size and number of images per reques…  `[[efficiently-serving-large-multimodal-models-using-epd-disaggregation]]`
- ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p03.png]] — **Efficiently Serving Large Multimodal Models Using ** Fig.3 (p.3): The inference pipeline of EPD Disaggregation. stages—EP-migration and PD-migrati…  `[[efficiently-serving-large-multimodal-models-using-epd-disaggregation]]`
- ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p04.png]] — **Efficiently Serving Large Multimodal Models Using ** Fig.4 (p.4): System architecture of the proposed EPD Disaggregated Inference. the data associ…  `[[efficiently-serving-large-multimodal-models-using-epd-disaggregation]]`
- ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p06.png]] — **Efficiently Serving Large Multimodal Models Using ** Fig.5 (p.6): SLO attainment (↑) for end-to-end inference across multiple models and image cou…  `[[efficiently-serving-large-multimodal-models-using-epd-disaggregation]]`
- ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p07.png]] — **Efficiently Serving Large Multimodal Models Using ** Fig.6 (p.7): Distribution of TTFT (Y-axis) across varying numbers of images per request (X-ax…  `[[efficiently-serving-large-multimodal-models-using-epd-disaggregation]]`
- ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p07.png]] — **Efficiently Serving Large Multimodal Models Using ** Fig.7 (p.7): SLO attainment (↑) versus request rate on the…  `[[efficiently-serving-large-multimodal-models-using-epd-disaggregation]]`
- ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p07.png]] — **Efficiently Serving Large Multimodal Models Using ** Fig.8 (p.7): As seen, EPD consistently outperforms vLLM and Dist-…  `[[efficiently-serving-large-multimodal-models-using-epd-disaggregation]]`
- ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p09.png]] — **Efficiently Serving Large Multimodal Models Using ** Fig.9 (p.9): As shown, EPD is the only configuration that achieves the SLO requirements, whil…  `[[efficiently-serving-large-multimodal-models-using-epd-disaggregation]]`
- ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p13.png]] — **Efficiently Serving Large Multimodal Models Using ** Fig.10 (p.13): Left: Impact of varying the number of encoding workers in the EPD method. The no…  `[[efficiently-serving-large-multimodal-models-using-epd-disaggregation]]`
- ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p13.png]] — **Efficiently Serving Large Multimodal Models Using ** Fig.11 (p.13): SLO attainment (↑) for end-to-end inference across multiple models and image cou…  `[[efficiently-serving-large-multimodal-models-using-epd-disaggregation]]`
- ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p16.png]] — **Efficiently Serving Large Multimodal Models Using ** Fig.12 (p.16): Breakdown of latency for encode and prefill stages using the InternVL2-8B model …  `[[efficiently-serving-large-multimodal-models-using-epd-disaggregation]]`
- ⭐ ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p02.png]] — **Mooncake: A KVCache-centric Disaggregated Architec** Fig.1 (p.2): Mooncake Architecture. remote location will prolong the TTFT, and a large batch …  `[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]`
- ⭐ ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p04.png]] — **Mooncake: A KVCache-centric Disaggregated Architec** Fig.2 (p.4): Normalized throughput and latency of prefill and decoding stages with different …  `[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]`
- ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p05.png]] — **Mooncake: A KVCache-centric Disaggregated Architec** Fig.3 (p.5): The KVCache pool in CPU memory. Each block is attached with a hash value determi…  `[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]`
- ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p06.png]] — **Mooncake: A KVCache-centric Disaggregated Architec** Fig.4 (p.6): Workflow of inference instances. ( ) For prefill instances, the load and store …  `[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]`
- ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p06.png]] — **Mooncake: A KVCache-centric Disaggregated Architec** Fig.5 (p.6): Input and output length distributions in the request trace. 4…  `[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]`
- ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p07.png]] — **Mooncake: A KVCache-centric Disaggregated Architec** Fig.6 (p.7): CDF (Cumulative Distribution…  `[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]`
- ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p09.png]] — **Mooncake: A KVCache-centric Disaggregated Architec** Fig.7 (p.9): Latency of storing KVCache of different request lengths (Layer-wise latency refe…  `[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]`
- ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p11.png]] — **Mooncake: A KVCache-centric Disaggregated Architec** Fig.8 (p.11): The prefill scheduling experiment in the Mooncake cluster.…  `[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]`
- ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p13.png]] — **Mooncake: A KVCache-centric Disaggregated Architec** Fig.9 (p.13): The load of prefill and decoding instances over 20 minutes, before using the pre…  `[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]`
- ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p14.png]] — **Mooncake: A KVCache-centric Disaggregated Architec** Fig.10 (p.14): Instance load when applying Early Rejection and Early Rejection Based on Predict…  `[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]`
- ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p16.png]] — **Mooncake: A KVCache-centric Disaggregated Architec** Fig.11 (p.16): End-to-end experiments of Mooncake and vLLM on the ArXiv Summarization and L-Eva…  `[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]`
- ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p16.png]] — **Mooncake: A KVCache-centric Disaggregated Architec** Fig.12 (p.16): End-to-end experiments of Mooncake and vLLM on simulated data.…  `[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]`
- ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p17.png]] — **Mooncake: A KVCache-centric Disaggregated Architec** Fig.13 (p.17): Request TTFT and TBT distributions of Mooncake and vLLM under real workloads…  `[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]`

### kv-cache (53)

- ![[assets/indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse-p01.png]] — **IndexCache: Accelerating Sparse Attention via Cros** Fig.1 (p.1): Benchmark comparison between GLM-5 and GLM-5 + IndexCache. IndexCache removes 50…  `[[indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse]]`
- ⭐ ![[assets/indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse-p03.png]] — **IndexCache: Accelerating Sparse Attention via Cros** Fig.2 (p.3): Side-by-side comparison of inference loops. (a) Standard DSA runs the lightning …  `[[indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse]]`
- ![[assets/indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse-p08.png]] — **IndexCache: Accelerating Sparse Attention via Cros** Fig.3 (p.8): Relative speedup of IndexCache over the DSA baseline across three inference sett…  `[[indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse]]`
- ![[assets/indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse-p16.png]] — **IndexCache: Accelerating Sparse Attention via Cros** Fig.4 (p.16): Pairwise top-k index overlap ratio between all layer pairs of the 30B DSA model.…  `[[indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse]]`
- ⭐ ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p02.png]] — **Mooncake: A KVCache-centric Disaggregated Architec** Fig.1 (p.2): Mooncake Architecture. remote location will prolong the TTFT, and a large batch …  `[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]`
- ⭐ ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p04.png]] — **Mooncake: A KVCache-centric Disaggregated Architec** Fig.2 (p.4): Normalized throughput and latency of prefill and decoding stages with different …  `[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]`
- ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p05.png]] — **Mooncake: A KVCache-centric Disaggregated Architec** Fig.3 (p.5): The KVCache pool in CPU memory. Each block is attached with a hash value determi…  `[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]`
- ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p06.png]] — **Mooncake: A KVCache-centric Disaggregated Architec** Fig.4 (p.6): Workflow of inference instances. ( ) For prefill instances, the load and store …  `[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]`
- ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p06.png]] — **Mooncake: A KVCache-centric Disaggregated Architec** Fig.5 (p.6): Input and output length distributions in the request trace. 4…  `[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]`
- ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p07.png]] — **Mooncake: A KVCache-centric Disaggregated Architec** Fig.6 (p.7): CDF (Cumulative Distribution…  `[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]`
- ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p09.png]] — **Mooncake: A KVCache-centric Disaggregated Architec** Fig.7 (p.9): Latency of storing KVCache of different request lengths (Layer-wise latency refe…  `[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]`
- ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p11.png]] — **Mooncake: A KVCache-centric Disaggregated Architec** Fig.8 (p.11): The prefill scheduling experiment in the Mooncake cluster.…  `[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]`
- ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p13.png]] — **Mooncake: A KVCache-centric Disaggregated Architec** Fig.9 (p.13): The load of prefill and decoding instances over 20 minutes, before using the pre…  `[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]`
- ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p14.png]] — **Mooncake: A KVCache-centric Disaggregated Architec** Fig.10 (p.14): Instance load when applying Early Rejection and Early Rejection Based on Predict…  `[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]`
- ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p16.png]] — **Mooncake: A KVCache-centric Disaggregated Architec** Fig.11 (p.16): End-to-end experiments of Mooncake and vLLM on the ArXiv Summarization and L-Eva…  `[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]`
- ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p16.png]] — **Mooncake: A KVCache-centric Disaggregated Architec** Fig.12 (p.16): End-to-end experiments of Mooncake and vLLM on simulated data.…  `[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]`
- ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p17.png]] — **Mooncake: A KVCache-centric Disaggregated Architec** Fig.13 (p.17): Request TTFT and TBT distributions of Mooncake and vLLM under real workloads…  `[[mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving]]`
- ![[assets/prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter-p02.png]] — **Prefill-as-a-Service: KVCache of Next-Generation M** Fig.1 (p.2): Comparison of two deployment paradigms for PD-disaggregated LLM serving.…  `[[prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter]]`
- ![[assets/prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter-p04.png]] — **Prefill-as-a-Service: KVCache of Next-Generation M** Fig.2 (p.4): KV throughput of MiniMax-M2.5 on an 8×H200 instance at various input lengths.…  `[[prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter]]`
- ⭐ ![[assets/prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter-p06.png]] — **Prefill-as-a-Service: KVCache of Next-Generation M** Fig.3 (p.6): Deployment topology of the PrfaaS-PD architecture.…  `[[prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter]]`
- ![[assets/prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter-p07.png]] — **Prefill-as-a-Service: KVCache of Next-Generation M** Fig.4 (p.7): Hybrid prefix cache pool. Linear states and full-attention KVCache are managed b…  `[[prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter]]`
- ![[assets/prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter-p11.png]] — **Prefill-as-a-Service: KVCache of Next-Generation M** Fig.5 (p.11): Illustration of the grid search process for the two optimization variables. (a) …  `[[prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter]]`
- ![[assets/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-p02.png]] — **KV Cache Optimization Strategies for Scalable and ** Fig.1 (p.2): Autoregressive generation, at each step the new token (orange) attends to all pr…  `[[kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference]]`
- ![[assets/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-p03.png]] — **KV Cache Optimization Strategies for Scalable and ** Fig.2 (p.3): Data-flow of the KV cache within a single transformer layer. Input token xt fans…  `[[kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference]]`
- ![[assets/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-p03.png]] — **KV Cache Optimization Strategies for Scalable and ** Fig.3 (p.3): KV cache memory as a function of context length for three LLaMA-2 model variants…  `[[kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference]]`
- ![[assets/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-p04.png]] — **KV Cache Optimization Strategies for Scalable and ** Fig.4 (p.4): Causal self-attention weight matrix for “The apple tastes sweet.” visualised wit…  `[[kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference]]`
- ![[assets/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-p05.png]] — **KV Cache Optimization Strategies for Scalable and ** Fig.5 (p.5): Taxonomy of KV cache optimization techniques surveyed in this paper, organized i…  `[[kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference]]`
- ![[assets/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-p06.png]] — **KV Cache Optimization Strategies for Scalable and ** Fig.6 (p.6): Upper plots illustrate symbolic plots of an attention map deploying different KV…  `[[kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference]]`
- ![[assets/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-p07.png]] — **KV Cache Optimization Strategies for Scalable and ** Fig.7 (p.7): The graph shows the simplified workflow of SnapKV, where the orange area represe…  `[[kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference]]`
- ![[assets/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-p09.png]] — **KV Cache Optimization Strategies for Scalable and ** Fig.8 (p.9): Definition of per-token and per-channel quantization. X ∈Rlprompt×d is the key/v…  `[[kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference]]`
- ![[assets/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-p09.png]] — **KV Cache Optimization Strategies for Scalable and ** Fig.9 (p.9): Palu’s low-rank projection method for KV-cache reduction. A weight matrix W of l…  `[[kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference]]`
- ![[assets/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-p11.png]] — **KV Cache Optimization Strategies for Scalable and ** Fig.10 (p.11): vLLM system overview [22]. 11…  `[[kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference]]`
- ![[assets/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-p12.png]] — **KV Cache Optimization Strategies for Scalable and ** Fig.11 (p.12): Operation flow of the prefetching module of InfiniGen. [23]. A layer-wise KV cac…  `[[kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference]]`
- ![[assets/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-p15.png]] — **KV Cache Optimization Strategies for Scalable and ** Fig.12 (p.15): Standard linear attention (top) vs. loglinear attention (bottom). The input cons…  `[[kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference]]`
- ![[assets/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-p17.png]] — **KV Cache Optimization Strategies for Scalable and ** Fig.13 (p.17): During Pre-filling, ShadowKV offloads the value cache to the CPU while maintaini…  `[[kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference]]`
- ![[assets/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-p17.png]] — **KV Cache Optimization Strategies for Scalable and ** Fig.14 (p.17): System overview of TailorKV. Offline identification categorizes the layers into …  `[[kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference]]`
- ![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p02.png]] — **CacheBlend: Fast Large Language Model Serving for ** Fig.1 (p.2): Contrasting full KV recompute, prefix caching, full KV reuse, and CacheBlend’s s…  `[[cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion]]`
- ![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p04.png]] — **CacheBlend: Fast Large Language Model Serving for ** Fig.2 (p.4): Generation quality improves as more text chunks are retrieved. and fetch top-k r…  `[[cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion]]`
- ![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p04.png]] — **CacheBlend: Fast Large Language Model Serving for ** Fig.3 (p.4): An illustrative example of an LLM input with two text chunks prepended to a quer…  `[[cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion]]`
- ![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p05.png]] — **CacheBlend: Fast Large Language Model Serving for ** Fig.4 (p.5): Contrasting the attention matrices of (a) full KV recompute and (b) full KV reus…  `[[cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion]]`
- ![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p06.png]] — **CacheBlend: Fast Large Language Model Serving for ** Fig.5 (p.6): Illustrated contrast between (a) full KV recompute and (b) selective KV recomput…  `[[cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion]]`
- ![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p06.png]] — **CacheBlend: Fast Large Language Model Serving for ** Fig.6 (p.6): Attention deviation reduces as we recompute the KV of more tokens on each layer.…  `[[cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion]]`
- ![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p07.png]] — **CacheBlend: Fast Large Language Model Serving for ** Fig.7 (p.7): Distribution of KV deviation of different tokens on one layer. 5 vs. 6 12 vs. 13…  `[[cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion]]`
- ![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p07.png]] — **CacheBlend: Fast Large Language Model Serving for ** Fig.8 (p.7): Rank correlation of the KV deviation per token be- tween two consecutive layers.…  `[[cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion]]`
- ![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p07.png]] — **CacheBlend: Fast Large Language Model Serving for ** Fig.9 (p.7): CacheBlend selects the HKVD (high KV deviation) tokens of one layer by computing…  `[[cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion]]`
- ![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p08.png]] — **CacheBlend: Fast Large Language Model Serving for ** Fig.10 (p.8): (a) Smartly picking the recompute ratio will not incur an extra delay. (b) Smart…  `[[cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion]]`
- ![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p09.png]] — **CacheBlend: Fast Large Language Model Serving for ** Fig.11 (p.9): CacheBlend system (green stared) in light of LLM context augmented generation fo…  `[[cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion]]`
- ![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p10.png]] — **CacheBlend: Fast Large Language Model Serving for ** Fig.12 (p.10): CacheBlend reduces TTFT by 2.2-3.3× compared to full KV recompute with negligibl…  `[[cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion]]`
- ![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p10.png]] — **CacheBlend: Fast Large Language Model Serving for ** Fig.13 (p.10): Generation quality of CacheBlend with Yi-34B vs MapReduce and MapRerank. 7…  `[[cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion]]`
- ![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p11.png]] — **CacheBlend: Fast Large Language Model Serving for ** Fig.14 (p.11): CacheBlend achieves lower TTFT with higher throughput in RAG scenarios compared …  `[[cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion]]`
- ![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p11.png]] — **CacheBlend: Fast Large Language Model Serving for ** Fig.15 (p.11): CacheBlend outperforms baseline with varying chunk numbers, chunk lengths, and b…  `[[cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion]]`
- ![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p08.png]] — **CacheBlend: Fast Large Language Model Serving for ** Fig.16 (p.8): This means that even if the storage device is a fast device (ex. CPU RAM), the d…  `[[cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion]]`
- ![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p12.png]] — **CacheBlend: Fast Large Language Model Serving for ** Fig.17 (p.12): CacheBlend’s outperforms baselines when using RAM and slower disks…  `[[cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion]]`

### long-context (8)

- ⭐ ![[assets/deepseek-v4-towards-highly-efficient-million-token-context-intelligence-p14.png]] — **DeepSeek-V4: Towards Highly Efficient Million-Toke** Fig.1 (p.14): 2.4. Muon Optimizer…  `[[deepseek-v4-towards-highly-efficient-million-token-context-intelligence]]`
- ⭐ ![[assets/deepseek-v4-towards-highly-efficient-million-token-context-intelligence-p15.png]] — **DeepSeek-V4: Towards Highly Efficient Million-Toke** Fig.5 (p.15): This forms a fine-grained pipeline among experts, keeping both computation and c…  `[[deepseek-v4-towards-highly-efficient-million-token-context-intelligence]]`
- ![[assets/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-p01.png]] — **LongSpec: Long-Context Lossless Speculative Decodi** Fig.1 (p.1): The SoTA SD method, EAGLE, has a training context length of 2048, which is signi…  `[[longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification]]`
- ⭐ ![[assets/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-p04.png]] — **LongSpec: Long-Context Lossless Speculative Decodi** Fig.2 (p.4): Illustration of the memory-efficient draft model, the Anchor-Offset Indices, and…  `[[longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification]]`
- ![[assets/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-p07.png]] — **LongSpec: Long-Context Lossless Speculative Decodi** Fig.3 (p.7): Decoding speed (tokens/s) across different models and settings. All results are …  `[[longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification]]`
- ![[assets/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-p08.png]] — **LongSpec: Long-Context Lossless Speculative Decodi** Fig.4 (p.8): Training loss curves on long-context data.…  `[[longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification]]`
- ![[assets/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-p08.png]] — **LongSpec: Long-Context Lossless Speculative Decodi** Fig.5 (p.8): Latency breakdown for a single speculative decoding loop comparing the EAGLE imp…  `[[longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification]]`
- ![[assets/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-p09.png]] — **LongSpec: Long-Context Lossless Speculative Decodi** Fig.6 (p.9): Throughput comparison of Vanilla, MagicDec, and LONGSPEC. not suitable for such …  `[[longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification]]`

### multimodal (43)

- ![[assets/kimi-k2-5-visual-agentic-intelligence-p01.png]] — **KIMI K2.5: VISUAL AGENTIC INTELLIGENCE** Fig.1 (p.1): Kimi K2.5 main results. 1…  `[[kimi-k2-5-visual-agentic-intelligence]]`
- ![[assets/kimi-k2-5-visual-agentic-intelligence-p04.png]] — **KIMI K2.5: VISUAL AGENTIC INTELLIGENCE** Fig.2 (p.4): Vision RL training curves on vision benchmarks starting from minimal zero-vision…  `[[kimi-k2-5-visual-agentic-intelligence]]`
- ![[assets/kimi-k2-5-visual-agentic-intelligence-p05.png]] — **KIMI K2.5: VISUAL AGENTIC INTELLIGENCE** Fig.3 (p.5): An agent swarm has a trainable orchestrator that dynamically creates specialized…  `[[kimi-k2-5-visual-agentic-intelligence]]`
- ![[assets/kimi-k2-5-visual-agentic-intelligence-p06.png]] — **KIMI K2.5: VISUAL AGENTIC INTELLIGENCE** Fig.4 (p.6): In our parallel-agent reinforcement learning environment, the training accuracy …  `[[kimi-k2-5-visual-agentic-intelligence]]`
- ![[assets/kimi-k2-5-visual-agentic-intelligence-p10.png]] — **KIMI K2.5: VISUAL AGENTIC INTELLIGENCE** Fig.5 (p.10): Comparison of model performance and token usage for Kimi K2 Thinking following t…  `[[kimi-k2-5-visual-agentic-intelligence]]`
- ![[assets/kimi-k2-5-visual-agentic-intelligence-p14.png]] — **KIMI K2.5: VISUAL AGENTIC INTELLIGENCE** Fig.6 (p.14): The word cloud visualizes heterogeneous K2.5-based sub-agents dynamically instan…  `[[kimi-k2-5-visual-agentic-intelligence]]`
- ![[assets/kimi-k2-5-visual-agentic-intelligence-p14.png]] — **KIMI K2.5: VISUAL AGENTIC INTELLIGENCE** Fig.7 (p.14): Comparison of Kimi K2.5 performance un- der Agent Swarm and Discard-all context …  `[[kimi-k2-5-visual-agentic-intelligence]]`
- ![[assets/kimi-k2-5-visual-agentic-intelligence-p15.png]] — **KIMI K2.5: VISUAL AGENTIC INTELLIGENCE** Fig.8 (p.15): Agent Swarm achieves 3×–4.5× faster execution time compared to single-agent base…  `[[kimi-k2-5-visual-agentic-intelligence]]`
- ![[assets/kimi-k2-5-visual-agentic-intelligence-p21.png]] — **KIMI K2.5: VISUAL AGENTIC INTELLIGENCE** Fig.9 (p.21): Learning curves comparing vision-to-text ratios (10:90, 20:80, 50:50) under fixe…  `[[kimi-k2-5-visual-agentic-intelligence]]`
- ![[assets/kimi-k2-5-visual-agentic-intelligence-p23.png]] — **KIMI K2.5: VISUAL AGENTIC INTELLIGENCE** Fig.10 (p.23): Overview of our agentic RL framework. environments with minimal overhead. Our de…  `[[kimi-k2-5-visual-agentic-intelligence]]`
- ![[assets/kimi-k2-5-visual-agentic-intelligence-p28.png]] — **KIMI K2.5: VISUAL AGENTIC INTELLIGENCE** Fig.11 (p.28): Qualitative example of Kimi K2.5 analyzing a complete playthrough of Black Myth:…  `[[kimi-k2-5-visual-agentic-intelligence]]`
- ![[assets/kimi-k2-5-visual-agentic-intelligence-p29.png]] — **KIMI K2.5: VISUAL AGENTIC INTELLIGENCE** Fig.12 (p.29): Qualitative examples of Kimi K2.5 solving visual reasoning tasks via tool use. 2…  `[[kimi-k2-5-visual-agentic-intelligence]]`
- ![[assets/deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms-p01.png]] — **DeepStack: Deeply Stacking Visual Tokens is Surpri** Fig.1 (p.1): Left: Conventional large multimodal models (LMMs) string all visual tokens into …  `[[deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms]]`
- ![[assets/deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms-p04.png]] — **DeepStack: Deeply Stacking Visual Tokens is Surpri** Fig.2 (p.4): Architecture of DeepStack. The main innovation lies in the DeepStack strategy th…  `[[deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms]]`
- ![[assets/deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms-p08.png]] — **DeepStack: Deeply Stacking Visual Tokens is Surpri** Fig.3 (p.8): Analysis on using LLM layers to process visual tokens. (a) We insert the visual …  `[[deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms]]`
- ![[assets/deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms-p10.png]] — **DeepStack: Deeply Stacking Visual Tokens is Surpri** Fig.4 (p.10): Visualization. Both LLaVA-1.5 and DeepStack use 576 visual context length for a …  `[[deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms]]`
- ![[assets/deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms-p09.png]] — **DeepStack: Deeply Stacking Visual Tokens is Surpri** Fig.5 (p.9): Visualization of three sam- pling methods for DeepStack.…  `[[deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms]]`
- ![[assets/kimi-vl-technical-report-p01.png]] — **KIMI-VL TECHNICAL REPORT** Fig.1 (p.1): Comparison between Kimi-VL-Thinking-2506 and frontier open-source VLMs, includin…  `[[kimi-vl-technical-report]]`
- ![[assets/kimi-vl-technical-report-p02.png]] — **KIMI-VL TECHNICAL REPORT** Fig.2 (p.2): Highlights of Kimi-VL performance for a wide range of benchmarks like, general b…  `[[kimi-vl-technical-report]]`
- ![[assets/kimi-vl-technical-report-p03.png]] — **KIMI-VL TECHNICAL REPORT** Fig.3 (p.3): The model architecture of Kimi-VL and Kimi-VL-Thinking, consisting of a MoonViT …  `[[kimi-vl-technical-report]]`
- ![[assets/kimi-vl-technical-report-p04.png]] — **KIMI-VL TECHNICAL REPORT** Fig.4 (p.4): The pre-training stages of Kimi-VL consume a total of 4.4T tokens after text-onl…  `[[kimi-vl-technical-report]]`
- ![[assets/kimi-vl-technical-report-p06.png]] — **KIMI-VL TECHNICAL REPORT** Fig.5 (p.6): The post-training stages of Kimi-VL and Kimi-VL-Thinking, including two stages o…  `[[kimi-vl-technical-report]]`
- ![[assets/kimi-vl-technical-report-p08.png]] — **KIMI-VL TECHNICAL REPORT** Fig.6 (p.8): Manuscript reasoning visualization. Kimi-VL-Thinking demonstrates the ability to…  `[[kimi-vl-technical-report]]`
- ![[assets/kimi-vl-technical-report-p12.png]] — **KIMI-VL TECHNICAL REPORT** Fig.7 (p.12): Kimi-VL exhibits strong visual reasoning capabilities by grounding visual conten…  `[[kimi-vl-technical-report]]`
- ![[assets/kimi-vl-technical-report-p13.png]] — **KIMI-VL TECHNICAL REPORT** Fig.8 (p.13): Kimi-VL demonstrates its capability to perform symbolic reasoning and geometric …  `[[kimi-vl-technical-report]]`
- ![[assets/kimi-vl-technical-report-p14.png]] — **KIMI-VL TECHNICAL REPORT** Fig.9 (p.14): Diverse OCR visualization. Kimi-VL demonstrates strong OCR capabilities across v…  `[[kimi-vl-technical-report]]`
- ![[assets/kimi-vl-technical-report-p15.png]] — **KIMI-VL TECHNICAL REPORT** Fig.10 (p.15): Kimi-VL is capable of following multi-step reasoning processes to complete compl…  `[[kimi-vl-technical-report]]`
- ![[assets/kimi-vl-technical-report-p16.png]] — **KIMI-VL TECHNICAL REPORT** Fig.11 (p.16): Video scene splitting. Kimi-VL processes a long-form video by segmenting it into…  `[[kimi-vl-technical-report]]`
- ![[assets/kimi-vl-technical-report-p17.png]] — **KIMI-VL TECHNICAL REPORT** Fig.12 (p.17): Catching and understanding key details from an hour-long video course. Kimi-VL d…  `[[kimi-vl-technical-report]]`
- ![[assets/kimi-vl-technical-report-p16.png]] — **KIMI-VL TECHNICAL REPORT** Fig.13 (p.16): Specifically, increasing the max thinking token length at inference time consist…  `[[kimi-vl-technical-report]]`
- ![[assets/qwen2-5-vl-technical-report-p03.png]] — **Qwen2.5-VL Technical Report** Fig.1 (p.3): The Qwen2.5-VL framework demonstrates the integration of a vision encoder and a …  `[[qwen2-5-vl-technical-report]]`
- ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p01.png]] — **Efficiently Serving Large Multimodal Models Using ** Fig.1 (p.1): Aggregated (top) vs. disaggregated (bottom) sys- tem architectures. In the aggre…  `[[efficiently-serving-large-multimodal-models-using-epd-disaggregation]]`
- ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p02.png]] — **Efficiently Serving Large Multimodal Models Using ** Fig.2 (p.2): Impact of disaggregation on supported batch size and number of images per reques…  `[[efficiently-serving-large-multimodal-models-using-epd-disaggregation]]`
- ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p03.png]] — **Efficiently Serving Large Multimodal Models Using ** Fig.3 (p.3): The inference pipeline of EPD Disaggregation. stages—EP-migration and PD-migrati…  `[[efficiently-serving-large-multimodal-models-using-epd-disaggregation]]`
- ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p04.png]] — **Efficiently Serving Large Multimodal Models Using ** Fig.4 (p.4): System architecture of the proposed EPD Disaggregated Inference. the data associ…  `[[efficiently-serving-large-multimodal-models-using-epd-disaggregation]]`
- ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p06.png]] — **Efficiently Serving Large Multimodal Models Using ** Fig.5 (p.6): SLO attainment (↑) for end-to-end inference across multiple models and image cou…  `[[efficiently-serving-large-multimodal-models-using-epd-disaggregation]]`
- ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p07.png]] — **Efficiently Serving Large Multimodal Models Using ** Fig.6 (p.7): Distribution of TTFT (Y-axis) across varying numbers of images per request (X-ax…  `[[efficiently-serving-large-multimodal-models-using-epd-disaggregation]]`
- ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p07.png]] — **Efficiently Serving Large Multimodal Models Using ** Fig.7 (p.7): SLO attainment (↑) versus request rate on the…  `[[efficiently-serving-large-multimodal-models-using-epd-disaggregation]]`
- ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p07.png]] — **Efficiently Serving Large Multimodal Models Using ** Fig.8 (p.7): As seen, EPD consistently outperforms vLLM and Dist-…  `[[efficiently-serving-large-multimodal-models-using-epd-disaggregation]]`
- ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p09.png]] — **Efficiently Serving Large Multimodal Models Using ** Fig.9 (p.9): As shown, EPD is the only configuration that achieves the SLO requirements, whil…  `[[efficiently-serving-large-multimodal-models-using-epd-disaggregation]]`
- ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p13.png]] — **Efficiently Serving Large Multimodal Models Using ** Fig.10 (p.13): Left: Impact of varying the number of encoding workers in the EPD method. The no…  `[[efficiently-serving-large-multimodal-models-using-epd-disaggregation]]`
- ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p13.png]] — **Efficiently Serving Large Multimodal Models Using ** Fig.11 (p.13): SLO attainment (↑) for end-to-end inference across multiple models and image cou…  `[[efficiently-serving-large-multimodal-models-using-epd-disaggregation]]`
- ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p16.png]] — **Efficiently Serving Large Multimodal Models Using ** Fig.12 (p.16): Breakdown of latency for encode and prefill stages using the InternVL2-8B model …  `[[efficiently-serving-large-multimodal-models-using-epd-disaggregation]]`

### rl (95)

- ⭐ ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p01.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM ** Fig.1 (p.1): A comparison of learning behavior of the GEPA prompt optimizer against a state-o…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ⭐ ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p03.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM ** Fig.2 (p.3): This figure shows an example prompt generated by GEPA for the second-hop documen…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p05.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM ** Fig.3 (p.5): GEPA proposes a new candidate in every iteration by improving existing candidate…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p04.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM ** Fig.4 (p.4): GEPA receives the following inputs: A system  instan- tiated with simple prompt…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p07.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM ** Fig.5 (p.7): GEPA’s reflective prompt mutation systematically incorporates task-specific nuan…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p10.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM ** Fig.6 (p.10): Comparing the impact of different candidate selection strategies. (Left) As can …  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p13.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM ** Fig.7 (p.13): GEPA with GPT-4o is able to generate kernels for AMD NPUs that achieve vector ut…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p13.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM ** Fig.8 (p.13): GEPA with GPT-4o is able to iteratively refine and improve CUDA Kernel Code. The…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p24.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM ** Fig.9 (p.24): Details of System Aware Merge. r represents a seeded stochastic sampler.…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p28.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM ** Fig.10 (p.28): Final test set performance for aggregate and individual benchmarks.…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p28.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM ** Fig.11 (p.28): This figure compares the learning behaviour of GEPA against GRPO with full-param…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p29.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM ** Fig.12 (p.29): Hotpot QA Bench: rollout vs. score for different models/settings. (a) GPT-4.1 Mi…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p29.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM ** Fig.13 (p.29): IFBench: rollout vs. score for different models/settings. (a) GPT-4.1 Mini - MIP…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p29.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM ** Fig.14 (p.29): HoverBench: rollout vs. score for different models/settings. (a) GPT-4.1 Mini - …  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p29.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM ** Fig.15 (p.29): PUPA: rollout vs. score for different models/settings. 29…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p30.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM ** Fig.16 (p.30): Generalization gaps for different optimization methods. Following Wan et al. (20…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p30.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM ** Fig.17 (p.30): These plots visualize the final aggregate scores against the aggregate prompt si…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p31.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM ** Fig.18 (p.31): Comparing the token counts of optimized programs across benchmarks. (a) Abl:Sele…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p31.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM ** Fig.19 (p.31): HotpotQA GPT-4.1 Mini 31…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p32.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM ** Fig.20 (p.32): HotpotQA Qwen3 8B (a) Abl:SelectBestCandidate (b) SelectBestCandidate +…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p32.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM ** Fig.21 (p.32): IFBench GPT-4.1 Mini (a) Abl:SelectBestCandidate (b)…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p32.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM ** Fig.22 (p.32): IFBench Qwen3 8B 32…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p33.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM ** Fig.23 (p.33): HoVer GPT-4.1 Mini (a) Abl:SelectBestCandidate (b) SelectBestCandidate +…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p33.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM ** Fig.24 (p.33): HoVer Qwen3 8B (a) Abl:SelectBestCandidate (b) SelectBestCandidate +…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p33.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM ** Fig.25 (p.33): PUPA GPT-4.1 Mini 33…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p34.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM ** Fig.26 (p.34): PUPA Qwen3 8B K.1 PROMPTS AT INTERMEDIATE STAGES FOR PUPA…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p12.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM ** Fig.27 (p.12): We also note that generation stochasticity (temperature based sampling) is elimi…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ⭐ ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p01.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUTPERFORM R** Fig.1 (p.1): A comparison of learning behavior of the GEPA prompt optimizer against a state-o…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ⭐ ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p03.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUTPERFORM R** Fig.2 (p.3): This figure shows an example prompt generated by GEPA for the second-hop documen…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p05.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUTPERFORM R** Fig.3 (p.5): GEPA proposes a new candidate in every iteration by improving existing candidate…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p04.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUTPERFORM R** Fig.4 (p.4): GEPA receives the following inputs: A system  instan- tiated with simple prompt…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p07.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUTPERFORM R** Fig.5 (p.7): GEPA’s reflective prompt mutation systematically incorporates task-specific nuan…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p10.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUTPERFORM R** Fig.6 (p.10): Comparing the impact of different candidate selection strategies. (Left) As can …  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p13.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUTPERFORM R** Fig.7 (p.13): GEPA with GPT-4o is able to generate kernels for AMD NPUs that achieve vector ut…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p13.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUTPERFORM R** Fig.8 (p.13): GEPA with GPT-4o is able to iteratively refine and improve CUDA Kernel Code. The…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p24.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUTPERFORM R** Fig.9 (p.24): Details of System Aware Merge. r represents a seeded stochastic sampler.…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p28.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUTPERFORM R** Fig.10 (p.28): Final test set performance for aggregate and individual benchmarks.…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p28.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUTPERFORM R** Fig.11 (p.28): This figure compares the learning behaviour of GEPA against GRPO with full-param…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p29.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUTPERFORM R** Fig.12 (p.29): Hotpot QA Bench: rollout vs. score for different models/settings. (a) GPT-4.1 Mi…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p29.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUTPERFORM R** Fig.13 (p.29): IFBench: rollout vs. score for different models/settings. (a) GPT-4.1 Mini - MIP…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p29.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUTPERFORM R** Fig.14 (p.29): HoverBench: rollout vs. score for different models/settings. (a) GPT-4.1 Mini - …  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p29.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUTPERFORM R** Fig.15 (p.29): PUPA: rollout vs. score for different models/settings. 29…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p30.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUTPERFORM R** Fig.16 (p.30): Generalization gaps for different optimization methods. Following Wan et al. (20…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p30.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUTPERFORM R** Fig.17 (p.30): These plots visualize the final aggregate scores against the aggregate prompt si…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p31.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUTPERFORM R** Fig.18 (p.31): Comparing the token counts of optimized programs across benchmarks. (a) Abl:Sele…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p31.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUTPERFORM R** Fig.19 (p.31): HotpotQA GPT-4.1 Mini 31…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p32.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUTPERFORM R** Fig.20 (p.32): HotpotQA Qwen3 8B (a) Abl:SelectBestCandidate (b) SelectBestCandidate +…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p32.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUTPERFORM R** Fig.21 (p.32): IFBench GPT-4.1 Mini (a) Abl:SelectBestCandidate (b)…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p32.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUTPERFORM R** Fig.22 (p.32): IFBench Qwen3 8B 32…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p33.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUTPERFORM R** Fig.23 (p.33): HoVer GPT-4.1 Mini (a) Abl:SelectBestCandidate (b) SelectBestCandidate +…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p33.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUTPERFORM R** Fig.24 (p.33): HoVer Qwen3 8B (a) Abl:SelectBestCandidate (b) SelectBestCandidate +…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p33.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUTPERFORM R** Fig.25 (p.33): PUPA GPT-4.1 Mini 33…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p34.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUTPERFORM R** Fig.26 (p.34): PUPA Qwen3 8B K.1 PROMPTS AT INTERMEDIATE STAGES FOR PUPA…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p12.png]] — **GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUTPERFORM R** Fig.27 (p.12): We also note that generation stochasticity (temperature based sampling) is elimi…  `[[gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning]]`
- ![[assets/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-p04.png]] — **Search-R1: Training LLMs to Reason and Leverage Se** Fig.1 (p.4): Demonstration of PPO and GRPO training with the search engine (SEARCH-R1).…  `[[search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning]]`
- ![[assets/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-p09.png]] — **Search-R1: Training LLMs to Reason and Leverage Se** Fig.2 (p.9): (a) PPO vs. GRPO: GRPO generally converges faster but may exhibit instability af…  `[[search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning]]`
- ![[assets/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-p17.png]] — **Search-R1: Training LLMs to Reason and Leverage Se** Fig.3 (p.17): Retrieved Token Loss Masking Study instruction-tuned models exhibit faster conve…  `[[search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning]]`
- ![[assets/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-p17.png]] — **Search-R1: Training LLMs to Reason and Leverage Se** Fig.4 (p.17): Study of SEARCH-R1 on base and instruct LLMs. The instruction model converges fa…  `[[search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning]]`
- ![[assets/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-p18.png]] — **Search-R1: Training LLMs to Reason and Leverage Se** Fig.5 (p.18): Training dynamics of SEARCH-R1 with PPO and GRPO as the base RL method across fo…  `[[search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning]]`
- ![[assets/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-p19.png]] — **Search-R1: Training LLMs to Reason and Leverage Se** Fig.6 (p.19): The training dynamics of SEARCH-R1 with a different number of retrieved pas- sag…  `[[search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning]]`
- ![[assets/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-p19.png]] — **Search-R1: Training LLMs to Reason and Leverage Se** Fig.7 (p.19): We observe that a larger group size generally leads to faster convergence but ma…  `[[search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning]]`
- ![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p03.png]] — **HybridFlow: A Flexible and Efficient RLHF Framewor** Fig.1 (p.3): Dataflow graph of 3 RLHF algorithms [19, 43, 55].…  `[[hybridflow-a-flexible-and-efficient-rlhf-framework]]`
- ![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p03.png]] — **HybridFlow: A Flexible and Efficient RLHF Framewor** Fig.2 (p.3): Programming model used in RLHF systems. (a)…  `[[hybridflow-a-flexible-and-efficient-rlhf-framework]]`
- ![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p04.png]] — **HybridFlow: A Flexible and Efficient RLHF Framewor** Fig.3 (p.4): Dataflow execution given a model placement plan.…  `[[hybridflow-a-flexible-and-efficient-rlhf-framework]]`
- ![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p06.png]] — **HybridFlow: A Flexible and Efficient RLHF Framewor** Fig.4 (p.6): Architecture of HybridFlow. 3D-HybridEngine and Auto-Mapping algorithm. The hybr…  `[[hybridflow-a-flexible-and-efficient-rlhf-framework]]`
- ![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p06.png]] — **HybridFlow: A Flexible and Efficient RLHF Framewor** Fig.5 (p.6): An illustration of hierarchical APIs. (a) Model with 3D parallel configuration, …  `[[hybridflow-a-flexible-and-efficient-rlhf-framework]]`
- ![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p07.png]] — **HybridFlow: A Flexible and Efficient RLHF Framewor** Fig.6 (p.7): Implementation of PPO [55], ReMax [43], and Safe- RLHF [19]. Users can adapt to …  `[[hybridflow-a-flexible-and-efficient-rlhf-framework]]`
- ![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p08.png]] — **HybridFlow: A Flexible and Efficient RLHF Framewor** Fig.7 (p.8): 3D-HybridEngine workflow in one RLHF iteration. 4 GPUs are used for actor traini…  `[[hybridflow-a-flexible-and-efficient-rlhf-framework]]`
- ![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p08.png]] — **HybridFlow: A Flexible and Efficient RLHF Framewor** Fig.8 (p.8): Model weights resharding. 2 machines each with 4 GPUs are used for actor trainin…  `[[hybridflow-a-flexible-and-efficient-rlhf-framework]]`
- ![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p11.png]] — **HybridFlow: A Flexible and Efficient RLHF Framewor** Fig.9 (p.11): PPO throughput. Numbers in parentheses are HybridFlow speedups compared with bas…  `[[hybridflow-a-flexible-and-efficient-rlhf-framework]]`
- ![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p11.png]] — **HybridFlow: A Flexible and Efficient RLHF Framewor** Fig.10 (p.11): ReMax throughput. Numbers in parentheses are HybridFlow speedups compared with b…  `[[hybridflow-a-flexible-and-efficient-rlhf-framework]]`
- ![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p11.png]] — **HybridFlow: A Flexible and Efficient RLHF Framewor** Fig.11 (p.11): Safe-RLHF throughput. Numbers in the parentheses are HybridFlow speedups compare…  `[[hybridflow-a-flexible-and-efficient-rlhf-framework]]`
- ![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p12.png]] — **HybridFlow: A Flexible and Efficient RLHF Framewor** Fig.12 (p.12): Throughput of HybridFlow under different placements 32 64 96 128 # of GPUs…  `[[hybridflow-a-flexible-and-efficient-rlhf-framework]]`
- ![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p12.png]] — **HybridFlow: A Flexible and Efficient RLHF Framewor** Fig.13 (p.12): Placement comparison under 13B actor and reference policy & 70B critic and rewar…  `[[hybridflow-a-flexible-and-efficient-rlhf-framework]]`
- ![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p13.png]] — **HybridFlow: A Flexible and Efficient RLHF Framewor** Fig.14 (p.13): Transition time between actor training and generation.…  `[[hybridflow-a-flexible-and-efficient-rlhf-framework]]`
- ![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p13.png]] — **HybridFlow: A Flexible and Efficient RLHF Framewor** Fig.15 (p.13): Time breakdown on different generation parallel sizes of the actor model on 16 G…  `[[hybridflow-a-flexible-and-efficient-rlhf-framework]]`
- ![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p13.png]] — **HybridFlow: A Flexible and Efficient RLHF Framewor** Fig.16 (p.13): Runtime of device mapping algorithm. The model size and # of GPUs are simultaneo…  `[[hybridflow-a-flexible-and-efficient-rlhf-framework]]`
- ![[assets/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-p04.png]] — **AREAL: A Large-Scale Asynchronous Reinforcement Le** Fig.1 (p.4): Execution timeline of a synchronous (left) and a one-step overlap (right) RL sys…  `[[areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning]]`
- ![[assets/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-p04.png]] — **AREAL: A Large-Scale Asynchronous Reinforcement Le** Fig.2 (p.4): The AREAL architecture featuring asynchronous generation and training components…  `[[areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning]]`
- ![[assets/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-p04.png]] — **AREAL: A Large-Scale Asynchronous Reinforcement Le** Fig.3 (p.4): Illustration of generation management in AREAL. Vertical lines show the ready ti…  `[[areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning]]`
- ![[assets/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-p08.png]] — **AREAL: A Large-Scale Asynchronous Reinforcement Le** Fig.4 (p.8): The strong scaling trend. Dotted lines indicate ideal linear scaling. verl consi…  `[[areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning]]`
- ![[assets/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-p09.png]] — **AREAL: A Large-Scale Asynchronous Reinforcement Le** Fig.5 (p.9): Ablation studies of the decoupled PPO objective and staleness control with a 1.5…  `[[areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning]]`
- ![[assets/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-p10.png]] — **AREAL: A Large-Scale Asynchronous Reinforcement Le** Fig.6 (p.10): Ablation studies on system optimizations. experimental setup, we configured 32 m…  `[[areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning]]`
- ![[assets/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-p06.png]] — **DeepSeek-R1: Incentivizing Reasoning Capability in** Fig.2 (p.6): In the initial stage, we collect thousands of cold-start data that exhibits a co…  `[[deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning]]`
- ![[assets/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-p14.png]] — **DeepSeek-R1: Incentivizing Reasoning Capability in** Fig.3 (p.14): For each question ? , GRPO samples a group of outputs f= 1, = 2,    , = g fro…  `[[deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning]]`
- ![[assets/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-p35.png]] — **DeepSeek-R1: Incentivizing Reasoning Capability in** Fig.6 (p.35): B.6. Ablation Study of Language Consistency Reward…  `[[deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning]]`
- ![[assets/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-p37.png]] — **DeepSeek-R1: Incentivizing Reasoning Capability in** Fig.7 (p.37): As can be seen, without the LC reward, language consistency gradually deteriorat…  `[[deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning]]`
- ![[assets/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-p48.png]] — **DeepSeek-R1: Incentivizing Reasoning Capability in** Fig.13 (p.48): We have categorized potential content safety challenges faced by language models…  `[[deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning]]`
- ![[assets/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-p53.png]] — **DeepSeek-R1: Incentivizing Reasoning Capability in** Fig.14 (p.53): For DeepSeek-V3 and DeepSeek-R1, we evaluated safety scores for models with and …  `[[deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning]]`
- ![[assets/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning-p01.png]] — **Single-Rollout Asynchronous Optimization for Agent** Fig.1 (p.1): The performance of SAO on reasoning and coding benchmarks. The four reasoning be…  `[[single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning]]`
- ![[assets/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning-p03.png]] — **Single-Rollout Asynchronous Optimization for Agent** Fig.2 (p.3): Overview of SAO with single rollout design. The numbers denote the generation or…  `[[single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning]]`
- ![[assets/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning-p06.png]] — **Single-Rollout Asynchronous Optimization for Agent** Fig.3 (p.6): Performance comparison between SAO and GRPO (w/ DIS) during training. It can be …  `[[single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning]]`
- ![[assets/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning-p07.png]] — **Single-Rollout Asynchronous Optimization for Agent** Fig.4 (p.7): Training dynamics of asynchronous single-rollout RL. (a) Explained Variance for …  `[[single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning]]`
- ![[assets/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning-p09.png]] — **Single-Rollout Asynchronous Optimization for Agent** Fig.5 (p.9): Online learning simulation under changing writing-style preferences. 5…  `[[single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning]]`
- ![[assets/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning-p13.png]] — **Single-Rollout Asynchronous Optimization for Agent** Fig.6 (p.13): Training reward for token-level SAO training and step-level variants, where toke…  `[[single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning]]`

### sparse-attention (4)

- ![[assets/indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse-p01.png]] — **IndexCache: Accelerating Sparse Attention via Cros** Fig.1 (p.1): Benchmark comparison between GLM-5 and GLM-5 + IndexCache. IndexCache removes 50…  `[[indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse]]`
- ⭐ ![[assets/indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse-p03.png]] — **IndexCache: Accelerating Sparse Attention via Cros** Fig.2 (p.3): Side-by-side comparison of inference loops. (a) Standard DSA runs the lightning …  `[[indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse]]`
- ![[assets/indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse-p08.png]] — **IndexCache: Accelerating Sparse Attention via Cros** Fig.3 (p.8): Relative speedup of IndexCache over the DSA baseline across three inference sett…  `[[indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse]]`
- ![[assets/indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse-p16.png]] — **IndexCache: Accelerating Sparse Attention via Cros** Fig.4 (p.16): Pairwise top-k index overlap ratio between all layer pairs of the 30B DSA model.…  `[[indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse]]`

### speculative (78)

- ⭐ ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p02.png]] — **MEDUSA: Simple LLM Inference Acceleration Framewor** Fig.1 (p.2): MEDUSA introduces multiple heads on top of the last hidden states of the LLM, en…  `[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]`
- ⭐ ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p03.png]] — **MEDUSA: Simple LLM Inference Acceleration Framewor** Fig.2 (p.3): Remarkably, similar ideas have also been explored in independent works like Miao…  `[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]`
- ⭐ ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p07.png]] — **MEDUSA: Simple LLM Inference Acceleration Framewor** Fig.3 (p.7): Left: Speed comparison of baseline, MEDUSA-1 and MEDUSA-2 on Vicuna-7B/13B. MEDU…  `[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]`
- ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p08.png]] — **MEDUSA: Simple LLM Inference Acceleration Framewor** Fig.4 (p.8): Effectiveness of numbers of candidate tokens for decoding introduced by trees (d…  `[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]`
- ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p05.png]] — **MEDUSA: Simple LLM Inference Acceleration Framewor** Fig.5 (p.5): 5…  `[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]`
- ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p15.png]] — **MEDUSA: Simple LLM Inference Acceleration Framewor** Fig.6 (p.15): Visualization of a sparse tree setting for MEDUSA-2 Vicuna-7B. The tree has 64 n…  `[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]`
- ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p15.png]] — **MEDUSA: Simple LLM Inference Acceleration Framewor** Fig.7 (p.15): Inference speed of various models using speculative decoding on MT-Bench. Baseli…  `[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]`
- ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p16.png]] — **MEDUSA: Simple LLM Inference Acceleration Framewor** Fig.8 (p.16): Speedup of various models with MEDUSA-2. MEDUSA-2 shows significant speed improv…  `[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]`
- ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p18.png]] — **MEDUSA: Simple LLM Inference Acceleration Framewor** Fig.9 (p.18): The figure shows the relationship between FLOP/s and Operational Intensity for a…  `[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]`
- ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p18.png]] — **MEDUSA: Simple LLM Inference Acceleration Framewor** Fig.10 (p.18): Llama-13B operators on A100-80GB-PCIe. 18…  `[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]`
- ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p19.png]] — **MEDUSA: Simple LLM Inference Acceleration Framewor** Fig.11 (p.19): Llama-33B operators on A100-80GB-PCIe. 1 10 100 1k 10k…  `[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]`
- ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p19.png]] — **MEDUSA: Simple LLM Inference Acceleration Framewor** Fig.12 (p.19): Llama-7B operators on A40. 19…  `[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]`
- ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p20.png]] — **MEDUSA: Simple LLM Inference Acceleration Framewor** Fig.13 (p.20): Llama-13B operators on A40. 1 10 100 1k 10k…  `[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]`
- ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p20.png]] — **MEDUSA: Simple LLM Inference Acceleration Framewor** Fig.14 (p.20): Llama-33B operators on A40. 20…  `[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]`
- ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p21.png]] — **MEDUSA: Simple LLM Inference Acceleration Framewor** Fig.15 (p.21): Llama-7B operators on A6000. 1 10 100 1k 10k…  `[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]`
- ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p21.png]] — **MEDUSA: Simple LLM Inference Acceleration Framewor** Fig.16 (p.21): Llama-13B operators on A6000. 21…  `[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]`
- ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p22.png]] — **MEDUSA: Simple LLM Inference Acceleration Framewor** Fig.17 (p.22): Llama-33B operators on A6000. 22…  `[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]`
- ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p23.png]] — **MEDUSA: Simple LLM Inference Acceleration Framewor** Fig.18 (p.23): FLOP/s vs. Operational Intensity of attention matrix multiplication with batch s…  `[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]`
- ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p24.png]] — **MEDUSA: Simple LLM Inference Acceleration Framewor** Fig.19 (p.24): FLOP/s vs. Operational Intensity of attention matrix multiplication with sequenc…  `[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]`
- ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p24.png]] — **MEDUSA: Simple LLM Inference Acceleration Framewor** Fig.20 (p.24): FLOP/s vs. Operational Intensity of Linear layers. 24…  `[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]`
- ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p26.png]] — **MEDUSA: Simple LLM Inference Acceleration Framewor** Fig.21 (p.26): Simulated acceleration rate, speedup, and normalized latency ablation using diff…  `[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]`
- ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p27.png]] — **MEDUSA: Simple LLM Inference Acceleration Framewor** Fig.22 (p.27): Simulated speedup with sequence length 1024 for Llama-7B. 1 16 32 48 64 80 96 11…  `[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]`
- ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p27.png]] — **MEDUSA: Simple LLM Inference Acceleration Framewor** Fig.23 (p.27): Simulated speedup with batch size 4 for Llama-7B. 27…  `[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]`
- ![[assets/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-p01.png]] — **EAGLE-3: Scaling up Inference Acceleration of Larg** Fig.1 (p.1): Scaling law evaluated on the MT-bench using LLaMA-Instruct 3.1 8B as the target …  `[[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]]`
- ⭐ ![[assets/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-p02.png]] — **EAGLE-3: Scaling up Inference Acceleration of Larg** Fig.2 (p.2): Speedup ratios of different methods at temperature=0. For the standard speculati…  `[[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]]`
- ![[assets/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-p03.png]] — **EAGLE-3: Scaling up Inference Acceleration of Larg** Fig.3 (p.3): Illustration of training-time test (the bottom part) and its comparison with oth…  `[[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]]`
- ⭐ ![[assets/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-p02.png]] — **EAGLE-3: Scaling up Inference Acceleration of Larg** Fig.4 (p.2): We can address this issue by incorporating Step 1 into the training process (the…  `[[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]]`
- ![[assets/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-p04.png]] — **EAGLE-3: Scaling up Inference Acceleration of Larg** Fig.5 (p.4): Diagram of the EAGLE-3 inference pipeline, illustrating the three steps of the d…  `[[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]]`
- ![[assets/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-p05.png]] — **EAGLE-3: Scaling up Inference Acceleration of Larg** Fig.6 (p.5): All attention masks are diagonal, except when the original training data is used…  `[[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]]`
- ![[assets/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-p08.png]] — **EAGLE-3: Scaling up Inference Acceleration of Larg** Fig.7 (p.8): Acceptance rate of EAGLE and EAGLE-3 on MT-bench, with the target model being LL…  `[[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]]`
- ![[assets/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-p01.png]] — **EAGLE: Speculative Sampling Requires Rethinking Fe** Fig.1 (p.1): Speedup ratio of Vicuna and LLaMA2-Chat inference latency on the MT-bench for gr…  `[[eagle-speculative-sampling-requires-rethinking-feature-uncertainty]]`
- ⭐ ![[assets/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-p02.png]] — **EAGLE: Speculative Sampling Requires Rethinking Fe** Fig.2 (p.2): Speedup ratio on the MT-bench for non-greedy (temperature=1) settings. Lookahead…  `[[eagle-speculative-sampling-requires-rethinking-feature-uncertainty]]`
- ⭐ ![[assets/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-p02.png]] — **EAGLE: Speculative Sampling Requires Rethinking Fe** Fig.3 (p.2): Uncertainty in feature sequences. The next fea- ture following fI is contingent …  `[[eagle-speculative-sampling-requires-rethinking-feature-uncertainty]]`
- ![[assets/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-p03.png]] — **EAGLE: Speculative Sampling Requires Rethinking Fe** Fig.4 (p.3): Accuracy and speedup ratio of draft models based on tokens, features and feature…  `[[eagle-speculative-sampling-requires-rethinking-feature-uncertainty]]`
- ![[assets/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-p04.png]] — **EAGLE: Speculative Sampling Requires Rethinking Fe** Fig.5 (p.4): A comparison of the methods for drafting the fourth and fifth tokens, t4 and t5.…  `[[eagle-speculative-sampling-requires-rethinking-feature-uncertainty]]`
- ![[assets/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-p04.png]] — **EAGLE: Speculative Sampling Requires Rethinking Fe** Fig.6 (p.4): Pipeline of EAGLE. The upper section illustrates the computational process, whil…  `[[eagle-speculative-sampling-requires-rethinking-feature-uncertainty]]`
- ![[assets/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-p07.png]] — **EAGLE: Speculative Sampling Requires Rethinking Fe** Fig.7 (p.7): Speedup ratios of EAGLE with and without the use of tree attention. The evaluati…  `[[eagle-speculative-sampling-requires-rethinking-feature-uncertainty]]`
- ![[assets/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-p08.png]] — **EAGLE: Speculative Sampling Requires Rethinking Fe** Fig.8 (p.8): Performance of draft models with varying inputs. The target LLM is Vicuna 7B, an…  `[[eagle-speculative-sampling-requires-rethinking-feature-uncertainty]]`
- ![[assets/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-p12.png]] — **EAGLE: Speculative Sampling Requires Rethinking Fe** Fig.9 (p.12): However, the optimal tree structure is likely context-dependent. For instance, a…  `[[eagle-speculative-sampling-requires-rethinking-feature-uncertainty]]`
- ![[assets/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-p01.png]] — **EAGLE-2: Faster Inference of Language Models with ** Fig.1 (p.1): Speedup ratios of different methods at tempera- ture=1. For speculative sampling…  `[[eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees]]`
- ![[assets/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-p02.png]] — **EAGLE-2: Faster Inference of Language Models with ** Fig.2 (p.2): Speedup ratios of different methods at temperature=0. For speculative sampling, …  `[[eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees]]`
- ![[assets/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-p03.png]] — **EAGLE-2: Faster Inference of Language Models with ** Fig.3 (p.3): Comparison of standard speculative sampling and EAGLE. For simplicity, EAGLE’s t…  `[[eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees]]`
- ![[assets/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-p03.png]] — **EAGLE-2: Faster Inference of Language Models with ** Fig.4 (p.3): Differences between EAGLE and EAGLE-2. EA- GLE always uses a fixed draft shape. …  `[[eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees]]`
- ![[assets/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-p03.png]] — **EAGLE-2: Faster Inference of Language Models with ** Fig.5 (p.3): Overall, the acceptance rate of draft tokens is position-dependent, with the hig…  `[[eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees]]`
- ![[assets/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-p04.png]] — **EAGLE-2: Faster Inference of Language Models with ** Fig.6 (p.4): Average acceptance rates for different confidence score intervals of the draft m…  `[[eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees]]`
- ![[assets/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-p05.png]] — **EAGLE-2: Faster Inference of Language Models with ** Fig.7 (p.5): Illustration of EAGLE-2. The numbers beside the edges represent the confidence s…  `[[eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees]]`
- ![[assets/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-p02.png]] — **BLOCK DIFFUSION: INTERPOLATING BETWEEN AUTOREGRESS** Fig.1 (p.2): Block diffusion sequentially generates blocks of tokens by performing diffusion …  `[[block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models]]`
- ![[assets/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-p06.png]] — **BLOCK DIFFUSION: INTERPOLATING BETWEEN AUTOREGRESS** Fig.2 (p.6): Train NLLs for modeling the per-token likelihood on LM1B. Models are trained on …  `[[block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models]]`
- ![[assets/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-p21.png]] — **BLOCK DIFFUSION: INTERPOLATING BETWEEN AUTOREGRESS** Fig.3 (p.21): x1 t x2 t x3 t x1 x2 x3 x1 t x2 t x3 t x1 x2 x3…  `[[block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models]]`
- ![[assets/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-p22.png]] — **BLOCK DIFFUSION: INTERPOLATING BETWEEN AUTOREGRESS** Fig.4 (p.22): We can adapt the masking strategy from Fig. 3 to a FlexAttention compatible spar…  `[[block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models]]`
- ![[assets/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-p23.png]] — **BLOCK DIFFUSION: INTERPOLATING BETWEEN AUTOREGRESS** Fig.5 (p.23): Attention computation using FlexAttention with our proposed custom mask.…  `[[block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models]]`
- ![[assets/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-p26.png]] — **BLOCK DIFFUSION: INTERPOLATING BETWEEN AUTOREGRESS** Fig.6 (p.26): Sample from MDLM (Sahoo et al., 2024a) of length L = 1024 and T = 5K diffusion s…  `[[block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models]]`
- ![[assets/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-p27.png]] — **BLOCK DIFFUSION: INTERPOLATING BETWEEN AUTOREGRESS** Fig.7 (p.27): Sample from BD3-LM for block size L′ = 16 of length L = 2031 under T = 5K diffus…  `[[block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models]]`
- ![[assets/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-p28.png]] — **BLOCK DIFFUSION: INTERPOLATING BETWEEN AUTOREGRESS** Fig.8 (p.28): Sample from an AR model (Sahoo et al., 2024a) with length L = 2003 (trained with…  `[[block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models]]`
- ![[assets/dflash-block-diffusion-for-flash-speculative-decoding-p02.png]] — **DFlash: Block Diffusion for Flash Speculative Deco** Fig.1 (p.2): Speedup comparison between DFlash, EAGLE-3 against Autoregressive Decoding on Qw…  `[[dflash-block-diffusion-for-flash-speculative-decoding]]`
- ⭐ ![[assets/dflash-block-diffusion-for-flash-speculative-decoding-p04.png]] — **DFlash: Block Diffusion for Flash Speculative Deco** Fig.2 (p.4): DFlash Inference Design. Hidden context features extracted from the target model…  `[[dflash-block-diffusion-for-flash-speculative-decoding]]`
- ![[assets/dflash-block-diffusion-for-flash-speculative-decoding-p03.png]] — **DFlash: Block Diffusion for Flash Speculative Deco** Fig.3 (p.3): Draft cost of 1, 3, 5-layer DFlash and 1-layer EAGLE-3.…  `[[dflash-block-diffusion-for-flash-speculative-decoding]]`
- ![[assets/dflash-block-diffusion-for-flash-speculative-decoding-p05.png]] — **DFlash: Block Diffusion for Flash Speculative Deco** Fig.4 (p.5): DFlash training attention. The target model provides context features (blue) tha…  `[[dflash-block-diffusion-for-flash-speculative-decoding]]`
- ![[assets/dflash-block-diffusion-for-flash-speculative-decoding-p13.png]] — **DFlash: Block Diffusion for Flash Speculative Deco** Fig.5 (p.13): The loss decay makes training converge faster and better. A.5.2. RANDOM SAMPLING…  `[[dflash-block-diffusion-for-flash-speculative-decoding]]`
- ![[assets/dspark-confidence-scheduled-speculative-decoding-with-semi-autoregressive-generation-p04.png]] — **DSpark: Confidence-Scheduled Speculative Decoding ** Fig.1 (p.4): Recall from Equation 1 that the per-token latency of speculative decoding is 𝐿= …  `[[dspark-confidence-scheduled-speculative-decoding-with-semi-autoregressive-generation]]`
- ![[assets/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-p02.png]] — **JETSPEC: Breaking the Scaling Ceiling of Speculati** Fig.1 (p.2): End-to-end decoding speedup over standard autoregressive decoding on H100 GPUs a…  `[[jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting]]`
- ⭐ ![[assets/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-p03.png]] — **JETSPEC: Breaking the Scaling Ceiling of Speculati** Fig.2 (p.3): Expected speculative decoding speedup scales as a function of draft length γ, un…  `[[jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting]]`
- ![[assets/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-p04.png]] — **JETSPEC: Breaking the Scaling Ceiling of Speculati** Fig.3 (p.4): JetSpec design overview. JetSpec extracts fused hidden features from the frozen …  `[[jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting]]`
- ![[assets/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-p15.png]] — **JETSPEC: Breaking the Scaling Ceiling of Speculati** Fig.4 (p.15): Tree-quality failure mode at MATH-500 prompt #0, decode step 0. Both heads draft…  `[[jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting]]`
- ![[assets/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-p18.png]] — **JETSPEC: Breaking the Scaling Ceiling of Speculati** Fig.5 (p.18): Figure 5: Causal attention mask used for training with multiple sampled blocks. …  `[[jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting]]`
- ![[assets/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-p19.png]] — **JETSPEC: Breaking the Scaling Ceiling of Speculati** Fig.6 (p.19): Each sampled block includes an anchor position and multiple future token positio…  `[[jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting]]`
- ![[assets/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-p01.png]] — **LongSpec: Long-Context Lossless Speculative Decodi** Fig.1 (p.1): The SoTA SD method, EAGLE, has a training context length of 2048, which is signi…  `[[longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification]]`
- ⭐ ![[assets/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-p04.png]] — **LongSpec: Long-Context Lossless Speculative Decodi** Fig.2 (p.4): Illustration of the memory-efficient draft model, the Anchor-Offset Indices, and…  `[[longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification]]`
- ![[assets/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-p07.png]] — **LongSpec: Long-Context Lossless Speculative Decodi** Fig.3 (p.7): Decoding speed (tokens/s) across different models and settings. All results are …  `[[longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification]]`
- ![[assets/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-p08.png]] — **LongSpec: Long-Context Lossless Speculative Decodi** Fig.4 (p.8): Training loss curves on long-context data.…  `[[longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification]]`
- ![[assets/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-p08.png]] — **LongSpec: Long-Context Lossless Speculative Decodi** Fig.5 (p.8): Latency breakdown for a single speculative decoding loop comparing the EAGLE imp…  `[[longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification]]`
- ![[assets/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-p09.png]] — **LongSpec: Long-Context Lossless Speculative Decodi** Fig.6 (p.9): Throughput comparison of Vanilla, MagicDec, and LONGSPEC. not suitable for such …  `[[longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification]]`
- ![[assets/specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences-p01.png]] — **SpecExtend: A Drop-in Enhancement for Speculative ** Fig.1 (p.1): Performance and memory usage of speculative decoding with Llama-3.1-8B-Instruct …  `[[specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences]]`
- ⭐ ![[assets/specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences-p02.png]] — **SpecExtend: A Drop-in Enhancement for Speculative ** Fig.2 (p.2): Overview of SpecExtend. FlashAttention accelerates the prefill phases of both ta…  `[[specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences]]`
- ![[assets/specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences-p04.png]] — **SpecExtend: A Drop-in Enhancement for Speculative ** Fig.3 (p.4): Left figure shows acceptance rates for hard and easy tokens, where CMR enables m…  `[[specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences]]`
- ![[assets/specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences-p05.png]] — **SpecExtend: A Drop-in Enhancement for Speculative ** Fig.4 (p.5): (a) Average accepted length of Vicuna-7B/68M across different draft model cache …  `[[specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences]]`
- ![[assets/specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences-p06.png]] — **SpecExtend: A Drop-in Enhancement for Speculative ** Fig.5 (p.6): Speedup comparison of standard speculative decoding and SpecExtend across varyin…  `[[specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences]]`
- ![[assets/specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences-p07.png]] — **SpecExtend: A Drop-in Enhancement for Speculative ** Fig.6 (p.7): Decoding speed (left) and average ac- cepted length (right) of the DeepSeek-R1-D…  `[[specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences]]`

### training (100)

- ![[assets/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-p01.png]] — **EAGLE-3: Scaling up Inference Acceleration of Larg** Fig.1 (p.1): Scaling law evaluated on the MT-bench using LLaMA-Instruct 3.1 8B as the target …  `[[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]]`
- ⭐ ![[assets/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-p02.png]] — **EAGLE-3: Scaling up Inference Acceleration of Larg** Fig.2 (p.2): Speedup ratios of different methods at temperature=0. For the standard speculati…  `[[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]]`
- ![[assets/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-p03.png]] — **EAGLE-3: Scaling up Inference Acceleration of Larg** Fig.3 (p.3): Illustration of training-time test (the bottom part) and its comparison with oth…  `[[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]]`
- ⭐ ![[assets/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-p02.png]] — **EAGLE-3: Scaling up Inference Acceleration of Larg** Fig.4 (p.2): We can address this issue by incorporating Step 1 into the training process (the…  `[[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]]`
- ![[assets/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-p04.png]] — **EAGLE-3: Scaling up Inference Acceleration of Larg** Fig.5 (p.4): Diagram of the EAGLE-3 inference pipeline, illustrating the three steps of the d…  `[[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]]`
- ![[assets/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-p05.png]] — **EAGLE-3: Scaling up Inference Acceleration of Larg** Fig.6 (p.5): All attention masks are diagonal, except when the original training data is used…  `[[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]]`
- ![[assets/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-p08.png]] — **EAGLE-3: Scaling up Inference Acceleration of Larg** Fig.7 (p.8): Acceptance rate of EAGLE and EAGLE-3 on MT-bench, with the target model being LL…  `[[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p01.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.1 (p.1): ATOP search results on different GPU scales, each point representing a topology.…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p03.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.2 (p.3): GPT-3 training timeline on rank 0 of classical in- terleaved 1F1B schedule, excl…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p04.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.3 (p.4): (a) The max number of flow per 100 Gbps under all-to-all traffic in a 256-GPUs t…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p05.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.4 (p.5): Overview of ATOP allows the system to explore novel topology designs automatical…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p06.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.5 (p.6): Examples of constructing inter-layer and intra-layer connections in ATOP. Unment…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p09.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.6 (p.9): During the 4k GPUs search process: (a) The Pareto- optimal topologies generated …  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p09.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.7 (p.9): (a) The search results of ATOP when adjusting an existing 4k-GPU DCN. (b) The se…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p10.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.8 (p.10): (a) A ZCube(n, k+1) is constructed from 𝑛ZCube(n, k) and 𝑛𝑘switches. (b) An exam…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p11.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.9 (p.11): The training iteration time for GPT-3 175B and MoE-GPT models and the correspond…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p11.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.10 (p.11): CDF of PP flow completion time during a GPT-3 175B training iteration on 16384 G…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p12.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.11 (p.12): The topology diagrams of ROFT and ZCube on a real testbed. 1M 4M 16M 64M 256M 1G…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p12.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.12 (p.12): Collective communication performance on real- world deployment. ZCube and ROFT a…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p15.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.13 (p.15): In the search results of Case 3, the comparison between the number of modified l…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p15.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.14 (p.15): The search results of ATOP when building a new data center for multi-tenancy.…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p15.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.15 (p.15): The search results of ATOP when building a new heterogeneous data center with st…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p16.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.16 (p.16): During the ATOP optimization process: (a) The relationship between the number of…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p17.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.17 (p.17): Two scenarios degrade all-to-all performance: (a) ECMP hash collision: In Non-bl…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p17.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.18 (p.17): The average JCT for group all-to-all communica- tion under different topologies …  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p18.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.19 (p.18): Comparison between packet-level network simulation (with packet spraying for loa…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p19.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.20 (p.19): Comparison of the CDF of flow completion times between NS-3 and flow-level simul…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p20.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.21 (p.20): ROFT topology for a 16384 GPU cluster based on 51.2 Tbps switches.…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p20.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.22 (p.20): Rail-only topology for a 16384 GPU cluster based on 51.2 Tbps switches. Each Rai…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p20.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.23 (p.20): HPN topology (dual-port designs for ROFT) for a 16384 GPU cluster based on 51.2 …  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p20.png]] — **From ATOP to ZCube: Automated Topology Optimizatio** Fig.24 (p.20): ZCube(128,2) topology for a 16384 GPU cluster based on 51.2 Tbps switches. 880…  `[[from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training]]`
- ![[assets/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-p04.png]] — **Search-R1: Training LLMs to Reason and Leverage Se** Fig.1 (p.4): Demonstration of PPO and GRPO training with the search engine (SEARCH-R1).…  `[[search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning]]`
- ![[assets/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-p09.png]] — **Search-R1: Training LLMs to Reason and Leverage Se** Fig.2 (p.9): (a) PPO vs. GRPO: GRPO generally converges faster but may exhibit instability af…  `[[search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning]]`
- ![[assets/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-p17.png]] — **Search-R1: Training LLMs to Reason and Leverage Se** Fig.3 (p.17): Retrieved Token Loss Masking Study instruction-tuned models exhibit faster conve…  `[[search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning]]`
- ![[assets/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-p17.png]] — **Search-R1: Training LLMs to Reason and Leverage Se** Fig.4 (p.17): Study of SEARCH-R1 on base and instruct LLMs. The instruction model converges fa…  `[[search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning]]`
- ![[assets/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-p18.png]] — **Search-R1: Training LLMs to Reason and Leverage Se** Fig.5 (p.18): Training dynamics of SEARCH-R1 with PPO and GRPO as the base RL method across fo…  `[[search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning]]`
- ![[assets/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-p19.png]] — **Search-R1: Training LLMs to Reason and Leverage Se** Fig.6 (p.19): The training dynamics of SEARCH-R1 with a different number of retrieved pas- sag…  `[[search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning]]`
- ![[assets/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-p19.png]] — **Search-R1: Training LLMs to Reason and Leverage Se** Fig.7 (p.19): We observe that a larger group size generally leads to faster convergence but ma…  `[[search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning]]`
- ![[assets/gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints-p01.png]] — **GQA: Training Generalized Multi-Query Transformer ** Fig.1 (p.1): Overview of conversion from multi-head to multi-query attention. Key and value p…  `[[gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints]]`
- ![[assets/gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints-p02.png]] — **GQA: Training Generalized Multi-Query Transformer ** Fig.2 (p.2): Overview of grouped-query method. Multi-head attention has H query, key, and val…  `[[gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints]]`
- ![[assets/gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints-p03.png]] — **GQA: Training Generalized Multi-Query Transformer ** Fig.3 (p.3): Uptrained MQA yields a favorable tradeoff compared to MHA with higher quality an…  `[[gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints]]`
- ![[assets/gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints-p04.png]] — **GQA: Training Generalized Multi-Query Transformer ** Fig.4 (p.4): Performance comparison of different check- point conversion methods for T5-Large…  `[[gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints]]`
- ![[assets/gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints-p04.png]] — **GQA: Training Generalized Multi-Query Transformer ** Fig.5 (p.4): Performance as a function of uptraining pro- portion for T5 XXL models with MQA …  `[[gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints]]`
- ![[assets/gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints-p04.png]] — **GQA: Training Generalized Multi-Query Transformer ** Fig.6 (p.4): Time per sample for GQA-XXL as a function of the number of GQA groups with input…  `[[gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints]]`
- ![[assets/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-p02.png]] — **MegaScale: Scaling Large Language Model Training t** Fig.1 (p.2): Data parallel training with ZeRO2. dependencies that contribute to stability iss…  `[[megascale-scaling-large-language-model-training-to-more-than-10000-gpus]]`
- ⭐ ![[assets/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-p03.png]] — **MegaScale: Scaling Large Language Model Training t** Fig.2 (p.3): Interleaved 1F1B pipeline. update the model. Instead of duplicating model states…  `[[megascale-scaling-large-language-model-training-to-more-than-10000-gpus]]`
- ![[assets/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-p04.png]] — **MegaScale: Scaling Large Language Model Training t** Fig.3 (p.4): Overlapping communication in tensor parallelism (TP) and sequence parallelism (S…  `[[megascale-scaling-large-language-model-training-to-more-than-10000-gpus]]`
- ![[assets/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-p04.png]] — **MegaScale: Scaling Large Language Model Training t** Fig.4 (p.4): The cool-down phase can be viewed as the inverse of the warm-up phase, allowing …  `[[megascale-scaling-large-language-model-training-to-more-than-10000-gpus]]`
- ![[assets/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-p06.png]] — **MegaScale: Scaling Large Language Model Training t** Fig.5 (p.6): Robust training workflow. interval and help recover the transmission more quickl…  `[[megascale-scaling-large-language-model-training-to-more-than-10000-gpus]]`
- ![[assets/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-p08.png]] — **MegaScale: Scaling Large Language Model Training t** Fig.6 (p.8): Inconsistent MFU observed in large-scale training. Differ- ent colors denote dis…  `[[megascale-scaling-large-language-model-training-to-more-than-10000-gpus]]`
- ![[assets/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-p08.png]] — **MegaScale: Scaling Large Language Model Training t** Fig.7 (p.8): We gather latency data of the computation phase (forward and backward) across de…  `[[megascale-scaling-large-language-model-training-to-more-than-10000-gpus]]`
- ![[assets/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-p09.png]] — **MegaScale: Scaling Large Language Model Training t** Fig.8 (p.9): The trace shows events collected in a pipeline group on a unified timeline. Depe…  `[[megascale-scaling-large-language-model-training-to-more-than-10000-gpus]]`
- ![[assets/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-p10.png]] — **MegaScale: Scaling Large Language Model Training t** Fig.9 (p.10): Weak-scaling training performance of Megatron-LM and…  `[[megascale-scaling-large-language-model-training-to-more-than-10000-gpus]]`
- ![[assets/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-p11.png]] — **MegaScale: Scaling Large Language Model Training t** Fig.10 (p.11): The training loss curves in microbenchmark experiments.…  `[[megascale-scaling-large-language-model-training-to-more-than-10000-gpus]]`
- ![[assets/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-p11.png]] — **MegaScale: Scaling Large Language Model Training t** Fig.11 (p.11): The normalized training loss curve of a real production run on more than 10,000 …  `[[megascale-scaling-large-language-model-training-to-more-than-10000-gpus]]`
- ![[assets/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-p12.png]] — **MegaScale: Scaling Large Language Model Training t** Fig.12 (p.12): The MFU becomes stable after addressing the stragglers and problematic code segm…  `[[megascale-scaling-large-language-model-training-to-more-than-10000-gpus]]`
- ![[assets/zero-memory-optimizations-toward-training-trillion-parameter-models-p03.png]] — **ZeRO: Memory Optimizations Toward Training Trillio** Fig.1 (p.3): Comparing the per-device memory consumption of model states, with three stages o…  `[[zero-memory-optimizations-toward-training-trillion-parameter-models]]`
- ![[assets/zero-memory-optimizations-toward-training-trillion-parameter-models-p04.png]] — **ZeRO: Memory Optimizations Toward Training Trillio** Fig.2 (p.4): ZeRO training throughput and speedup w.r.t SOTA baseline for varying model sizes…  `[[zero-memory-optimizations-toward-training-trillion-parameter-models]]`
- ![[assets/zero-memory-optimizations-toward-training-trillion-parameter-models-p05.png]] — **ZeRO: Memory Optimizations Toward Training Trillio** Fig.3 (p.5): Superlinear scalability and per GPU training throughput of a 60B parameter model…  `[[zero-memory-optimizations-toward-training-trillion-parameter-models]]`
- ![[assets/zero-memory-optimizations-toward-training-trillion-parameter-models-p16.png]] — **ZeRO: Memory Optimizations Toward Training Trillio** Fig.4 (p.16): Max model throughput with ZeRO-DP.…  `[[zero-memory-optimizations-toward-training-trillion-parameter-models]]`
- ![[assets/zero-memory-optimizations-toward-training-trillion-parameter-models-p16.png]] — **ZeRO: Memory Optimizations Toward Training Trillio** Fig.5 (p.16): SOTA Turing-NLG enabled by ZeRO.…  `[[zero-memory-optimizations-toward-training-trillion-parameter-models]]`
- ![[assets/zero-memory-optimizations-toward-training-trillion-parameter-models-p16.png]] — **ZeRO: Memory Optimizations Toward Training Trillio** Fig.6 (p.16): Max model size .…  `[[zero-memory-optimizations-toward-training-trillion-parameter-models]]`
- ![[assets/zero-memory-optimizations-toward-training-trillion-parameter-models-p16.png]] — **ZeRO: Memory Optimizations Toward Training Trillio** Fig.7 (p.16): Max cache allo- cated.…  `[[zero-memory-optimizations-toward-training-trillion-parameter-models]]`
- ![[assets/zero-memory-optimizations-toward-training-trillion-parameter-models-p16.png]] — **ZeRO: Memory Optimizations Toward Training Trillio** Fig.8 (p.16): Throughput per GPU. a Bert-Large model for a data sample. Even if we assume the …  `[[zero-memory-optimizations-toward-training-trillion-parameter-models]]`
- ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p01.png]] — **Efficient Large-Scale Language Model Training on G** Fig.1 (p.1): Trend of sizes of state-of-the-art Natural Language Pro- cessing (NLP) models wi…  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p03.png]] — **Efficient Large-Scale Language Model Training on G** Fig.2 (p.3): Combination of tensor and pipeline model parallelism (MP) used in this work for …  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p03.png]] — **Efficient Large-Scale Language Model Training on G** Fig.3 (p.3): GPipe pipeline schedule with forward passes (blue) for all microbatches (represe…  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p03.png]] — **Efficient Large-Scale Language Model Training on G** Fig.4 (p.3): Default and interleaved 1F1B pipeline schedules. The top figure shows the defaul…  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p05.png]] — **Efficient Large-Scale Language Model Training on G** Fig.5 (p.5): Blocks of transformer model partitioned with tensor model parallelism (figures b…  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p05.png]] — **Efficient Large-Scale Language Model Training on G** Fig.6 (p.5): Fraction of time spent idling due to pipeline flush (pipeline bubble size) versu…  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p06.png]] — **Efficient Large-Scale Language Model Training on G** Fig.7 (p.6): Per-GPU throughput versus microbatch size for a GPT model with a billion paramet…  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p06.png]] — **Efficient Large-Scale Language Model Training on G** Fig.8 (p.6): Behavior of normalized estimated throughput (time com- puted as 𝑡= (𝑏′/𝑏+ 𝑝−1) ·…  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p07.png]] — **Efficient Large-Scale Language Model Training on G** Fig.9 (p.7): Scatter/gather communication optimization. Light blue blocks are layers in the f…  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p08.png]] — **Efficient Large-Scale Language Model Training on G** Fig.10 (p.8): Throughput per GPU of PTD-P and ZeRO-3 for two differ- ent GPT models (the 175B …  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p09.png]] — **Efficient Large-Scale Language Model Training on G** Fig.11 (p.9): Throughput per GPU of pipeline parallelism using two different batch sizes in a …  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p09.png]] — **Efficient Large-Scale Language Model Training on G** Fig.12 (p.9): Throughput per GPU of interleaved and non-interleaved schedules for a GPT model …  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p09.png]] — **Efficient Large-Scale Language Model Training on G** Fig.13 (p.9): Throughput per GPU of various parallel configurations that combine pipeline and …  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p10.png]] — **Efficient Large-Scale Language Model Training on G** Fig.14 (p.10): Throughput per GPU of various parallel configurations that combine data and pipe…  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p10.png]] — **Efficient Large-Scale Language Model Training on G** Fig.15 (p.10): Throughput per GPU of various parallel configurations that combine data and tens…  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p10.png]] — **Efficient Large-Scale Language Model Training on G** Fig.16 (p.10): Throughput per GPU of a (𝑡, 𝑝) = (8, 8) parallel configura- tion for different m…  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p11.png]] — **Efficient Large-Scale Language Model Training on G** Fig.17 (p.11): Throughput (in sequences per second) with and without activation recomputation f…  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p11.png]] — **Efficient Large-Scale Language Model Training on G** Fig.18 (p.11): Throughput per GPU with and without the scatter/gather optimization for a GPT mo…  `[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]`
- ![[assets/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-p02.png]] — **Megatron-LM: Training Multi-Billion Parameter Lang** Fig.1 (p.2): Model (blue) and model+data (green) parallel FLOPS as a function of number of GP…  `[[megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism]]`
- ![[assets/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-p03.png]] — **Megatron-LM: Training Multi-Billion Parameter Lang** Fig.2 (p.3): Transformer Architecture. Purple blocks correspond to fully connected layers. Ea…  `[[megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism]]`
- ![[assets/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-p04.png]] — **Megatron-LM: Training Multi-Billion Parameter Lang** Fig.3 (p.4): Blocks of Transformer with Model Parallelism. f and g are conjugate. f is an ide…  `[[megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism]]`
- ![[assets/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-p05.png]] — **Megatron-LM: Training Multi-Billion Parameter Lang** Fig.4 (p.5): Communication operations in a transformer layer. There are 4 total communication…  `[[megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism]]`
- ![[assets/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-p06.png]] — **Megatron-LM: Training Multi-Billion Parameter Lang** Fig.5 (p.6): Model and model + data parallel weak scaling efﬁciency as a function of the numb…  `[[megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism]]`
- ![[assets/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-p07.png]] — **Megatron-LM: Training Multi-Billion Parameter Lang** Fig.6 (p.7): Validation set perplexity. All language models are trained for 300k iterations. …  `[[megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism]]`
- ![[assets/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-p08.png]] — **Megatron-LM: Training Multi-Billion Parameter Lang** Fig.7 (p.8): Training loss for BERT model using the original architec- ture (a) and the rearr…  `[[megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism]]`
- ![[assets/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-p12.png]] — **Megatron-LM: Training Multi-Billion Parameter Lang** Fig.8 (p.12): Grouping of GPUs for hybrid model and data parallelism with 8-way model parallel…  `[[megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism]]`
- ![[assets/muon-is-scalable-for-llm-training-p01.png]] — **Muon is Scalable for LLM Training** Fig.1 (p.1): Scaling up with Muon. (a) Scaling law experiments comparing Muon and Adam. Muon …  `[[muon-is-scalable-for-llm-training]]`
- ![[assets/muon-is-scalable-for-llm-training-p04.png]] — **Muon is Scalable for LLM Training** Fig.2 (p.4): Validation loss curves for AdamW (green), Muon without weight decay (red), and M…  `[[muon-is-scalable-for-llm-training]]`
- ![[assets/muon-is-scalable-for-llm-training-p07.png]] — **Muon is Scalable for LLM Training** Fig.3 (p.7): Fitted scaling law curves for Muon and AdamW optimizers.…  `[[muon-is-scalable-for-llm-training]]`
- ![[assets/muon-is-scalable-for-llm-training-p10.png]] — **Muon is Scalable for LLM Training** Fig.4 (p.10): SVD entropy of weight matrices across different training iterations. We categori…  `[[muon-is-scalable-for-llm-training]]`
- ![[assets/muon-is-scalable-for-llm-training-p15.png]] — **Muon is Scalable for LLM Training** Fig.5 (p.15): Optimization Landscapes for Scaling Law Hyper-parameters Across FLOPs Budgets…  `[[muon-is-scalable-for-llm-training]]`
- ![[assets/muon-is-scalable-for-llm-training-p15.png]] — **Muon is Scalable for LLM Training** Fig.6 (p.15): D…  `[[muon-is-scalable-for-llm-training]]`
- ![[assets/muon-is-scalable-for-llm-training-p17.png]] — **Muon is Scalable for LLM Training** Fig.7 (p.17): Training dynamics comparison between Moonlight and Moonlight-A…  `[[muon-is-scalable-for-llm-training]]`
- ![[assets/muon-is-scalable-for-llm-training-p09.png]] — **Muon is Scalable for LLM Training** Fig.8 (p.9): 6.…  `[[muon-is-scalable-for-llm-training]]`
- ![[assets/muon-is-scalable-for-llm-training-p18.png]] — **Muon is Scalable for LLM Training** Fig.9 (p.18): Distribution of singular values for each weight matrix in the attention layers. …  `[[muon-is-scalable-for-llm-training]]`
- ![[assets/muon-is-scalable-for-llm-training-p19.png]] — **Muon is Scalable for LLM Training** Fig.10 (p.19): Distribution of singular values for each weight matrix in the feed-forward netwo…  `[[muon-is-scalable-for-llm-training]]`

## 按论文

### #1 IndexCache: Accelerating Sparse Attention via Cross-Layer In

- Fig.1 (p.1) ![[assets/indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse-p01.png]]
  - Benchmark comparison between GLM-5 and GLM-5 + IndexCache. IndexCache removes 50% of indexer computations while maintaining comparable performance across both long-context and reasoning tasks, deliver
- ⭐ Fig.2 (p.3) ![[assets/indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse-p03.png]]
  - Side-by-side comparison of inference loops. (a) Standard DSA runs the lightning indexer at every layer. (b) IndexCache adds a single conditional branch (red lines): F layers compute and cache fresh in
- Fig.3 (p.8) ![[assets/indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse-p08.png]]
  - Relative speedup of IndexCache over the DSA baseline across three inference settings on the 30B model. DSA baseline is normalized to 100%.
- Fig.4 (p.16) ![[assets/indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse-p16.png]]
  - Pairwise top-k index overlap ratio between all layer pairs of the 30B DSA model.

### #2 MEDUSA: Simple LLM Inference Acceleration Framework with Mul

- ⭐ Fig.1 (p.2) ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p02.png]]
  - MEDUSA introduces multiple heads on top of the last hidden states of the LLM, enabling the prediction of several sub- sequent tokens in parallel (Section 2.1.1). During inference, each head generates 
- ⭐ Fig.2 (p.3) ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p03.png]]
  - Remarkably, similar ideas have also been explored in independent works like Miao et al. (2023); Spector & Re (2023), where they follow a bottom-up approach and construct the tree by merging mul- tiple
- ⭐ Fig.3 (p.7) ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p07.png]]
  - Left: Speed comparison of baseline, MEDUSA-1 and MEDUSA-2 on Vicuna-7B/13B. MEDUSA-1 achieves more than 2× wall-time speedup compared to the baseline implementation while MEDUSA-2 further improves the
- Fig.4 (p.8) ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p08.png]]
  - Effectiveness of numbers of candidate tokens for decoding introduced by trees (default number of candidate token for decoding is 1 when using KV cache). Left: The acceleration rate for randomly sample
- Fig.5 (p.5) ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p05.png]]
  - 5
- Fig.6 (p.15) ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p15.png]]
  - Visualization of a sparse tree setting for MEDUSA-2 Vicuna-7B. The tree has 64 nodes representing candidate tokens and a depth of 4 which indicates 4 MEDUSA heads involved in calculation. Each node in
- Fig.7 (p.15) ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p15.png]]
  - Inference speed of various models using speculative decoding on MT-Bench. Baseline model speeds are presented by grey dotted lines for comparison. γ denotes the draft token number. E. Additional Resul
- Fig.8 (p.16) ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p16.png]]
  - Speedup of various models with MEDUSA-2. MEDUSA-2 shows significant speed improvement over all the models, while models trained with self-distillation (Zephyr-7B, Vicuna-13/33B) have weaker speedup du
- Fig.9 (p.18) ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p18.png]]
  - The figure shows the relationship between FLOP/s and Operational Intensity for all benchmarked datapoints of Llama-7B operators on A100-80GB-PCIe. The dashed lines represent the HBM bandwidth limit (1
- Fig.10 (p.18) ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p18.png]]
  - Llama-13B operators on A100-80GB-PCIe. 18
- Fig.11 (p.19) ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p19.png]]
  - Llama-33B operators on A100-80GB-PCIe. 1 10 100 1k 10k
- Fig.12 (p.19) ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p19.png]]
  - Llama-7B operators on A40. 19
- Fig.13 (p.20) ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p20.png]]
  - Llama-13B operators on A40. 1 10 100 1k 10k
- Fig.14 (p.20) ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p20.png]]
  - Llama-33B operators on A40. 20
- Fig.15 (p.21) ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p21.png]]
  - Llama-7B operators on A6000. 1 10 100 1k 10k
- Fig.16 (p.21) ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p21.png]]
  - Llama-13B operators on A6000. 21
- Fig.17 (p.22) ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p22.png]]
  - Llama-33B operators on A6000. 22
- Fig.18 (p.23) ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p23.png]]
  - FLOP/s vs. Operational Intensity of attention matrix multiplication with batch size 16. 23
- Fig.19 (p.24) ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p24.png]]
  - FLOP/s vs. Operational Intensity of attention matrix multiplication with sequence length 1024. 1 10 100 1k 10k
- Fig.20 (p.24) ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p24.png]]
  - FLOP/s vs. Operational Intensity of Linear layers. 24
- Fig.21 (p.26) ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p26.png]]
  - Simulated acceleration rate, speedup, and normalized latency ablation using different numbers of candidate tokens under the setting of batch size 1 and sequence length 1024 for Llama-7B on an A100 80G
- Fig.22 (p.27) ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p27.png]]
  - Simulated speedup with sequence length 1024 for Llama-7B. 1 16 32 48 64 80 96 112
- Fig.23 (p.27) ![[assets/medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-p27.png]]
  - Simulated speedup with batch size 4 for Llama-7B. 27

### #3 EAGLE-3: Scaling up Inference Acceleration of Large Language

- Fig.1 (p.1) ![[assets/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-p01.png]]
  - Scaling law evaluated on the MT-bench using LLaMA-Instruct 3.1 8B as the target model, with the x-axis representing the data scale relative to ShareGPT.
- ⭐ Fig.2 (p.2) ![[assets/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-p02.png]]
  - Speedup ratios of different methods at temperature=0. For the standard speculative sampling, Vicuna-13B uses Vicuna-68M as the draft model. In Table 1, we present comparisons with additional methods, 
- Fig.3 (p.3) ![[assets/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-p03.png]]
  - Illustration of training-time test (the bottom part) and its comparison with other draft methods (the upper and middle parts). f denotes the feature, t denotes the token, and a represents the unconstr
- ⭐ Fig.4 (p.2) ![[assets/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-p02.png]]
  - We can address this issue by incorporating Step 1 into the training process (the bottom of Figure 3). Using this method, the benefits of increasing training data become more pronounced. We name this t
- Fig.5 (p.4) ![[assets/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-p04.png]]
  - Diagram of the EAGLE-3 inference pipeline, illustrating the three steps of the draft model. l, m, and h represent the low, middle, and high-level features of the target model, respectively. e denotes 
- Fig.6 (p.5) ![[assets/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-p05.png]]
  - All attention masks are diagonal, except when the original training data is used as the key. Using matrix multiplication in this case would result in significant computational waste, so we can use vec
- Fig.7 (p.8) ![[assets/eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-p08.png]]
  - Acceptance rate of EAGLE and EAGLE-3 on MT-bench, with the target model being LLaMA-

### #4 EAGLE: Speculative Sampling Requires Rethinking Feature Unce

- Fig.1 (p.1) ![[assets/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-p01.png]]
  - Speedup ratio of Vicuna and LLaMA2-Chat inference latency on the MT-bench for greedy (temperature=0) settings. Speedup ratio of Medusa and Lookahead are copied from their original technical reports. W
- ⭐ Fig.2 (p.2) ![[assets/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-p02.png]]
  - Speedup ratio on the MT-bench for non-greedy (temperature=1) settings. Lookahead is confined to greedy decoding, and the non-greedy generation of Medusa does not guarantee lossless performance. Theref
- ⭐ Fig.3 (p.2) ![[assets/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-p02.png]]
  - Uncertainty in feature sequences. The next fea- ture following fI is contingent on the sampling outcome and cannot be determined solely based on fI, where both “always” and “am” are possible to follow
- Fig.4 (p.3) ![[assets/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-p03.png]]
  - Accuracy and speedup ratio of draft models based on tokens, features and feature&shifted-token at tempera- ture=0, tested on MT-bench with Vicuna 7B as the original LLM. Feature&shifted-token refers t
- Fig.5 (p.4) ![[assets/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-p04.png]]
  - A comparison of the methods for drafting the fourth and fifth tokens, t4 and t5. t (represented by blue blocks) denotes tokens, and f (orange blocks) signifies the features, with subscripts indicating
- Fig.6 (p.4) ![[assets/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-p04.png]]
  - Pipeline of EAGLE. The upper section illustrates the computational process, while the lower section displays the corresponding generation results for each step. In the upper section, green blocks repr
- Fig.7 (p.7) ![[assets/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-p07.png]]
  - Speedup ratios of EAGLE with and without the use of tree attention. The evaluation dataset is MT-bench, with the temperature parameter set to 0.
- Fig.8 (p.8) ![[assets/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-p08.png]]
  - Performance of draft models with varying inputs. The target LLM is Vicuna 7B, and the test dataset is MT-bench.
- Fig.9 (p.12) ![[assets/eagle-speculative-sampling-requires-rethinking-feature-uncertainty-p12.png]]
  - However, the optimal tree structure is likely context-dependent. For instance, as batch size increases and redundant computational resources decrease, a smaller tree might be preferable. Tuning the dr

### #5 EAGLE-2: Faster Inference of Language Models with Dynamic Dr

- Fig.1 (p.1) ![[assets/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-p01.png]]
  - Speedup ratios of different methods at tempera- ture=1. For speculative sampling, the Vicuna series uses
- Fig.2 (p.2) ![[assets/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-p02.png]]
  - Speedup ratios of different methods at temperature=0. For speculative sampling, the Vicuna series uses Vicuna- 68M as the draft model. LLaMA2-Chat 7B, 13B, and LLaMA3-Instruct 8B lack suitable draft m
- Fig.3 (p.3) ![[assets/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-p03.png]]
  - Comparison of standard speculative sampling and EAGLE. For simplicity, EAGLE’s tree-structured draft is shown only in the verification stage, while the illustration of the drafting stage uses a chain-
- Fig.4 (p.3) ![[assets/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-p03.png]]
  - Differences between EAGLE and EAGLE-2. EA- GLE always uses a fixed draft shape. When the query is “10+2=”, the next token is very likely to be correctly pre- dicted as “1”. However, with a static draf
- Fig.5 (p.3) ![[assets/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-p03.png]]
  - Overall, the acceptance rate of draft tokens is position-dependent, with the highest acceptance rate at position P1 and the lowest at position P6. Draft tokens in the upper left side of the draft tree
- Fig.6 (p.4) ![[assets/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-p04.png]]
  - Average acceptance rates for different confidence score intervals of the draft model. The red dashed line connects (0,0) and (1,1) to aid in visual assessment. The original LLM is Vicuna 7B. aspects: 
- Fig.7 (p.5) ![[assets/eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees-p05.png]]
  - Illustration of EAGLE-2. The numbers beside the edges represent the confidence scores of the draft model, and the numbers in brackets within the blocks represent the value of the nodes. During the exp

### #6 BLOCK DIFFUSION: INTERPOLATING BETWEEN AUTOREGRESSIVE AND DI

- Fig.1 (p.2) ![[assets/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-p02.png]]
  - Block diffusion sequentially generates blocks of tokens by performing diffusion within each block and conditioning on previous blocks. By combining strength from autoregressive and diffusion models, b
- Fig.2 (p.6) ![[assets/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-p06.png]]
  - Train NLLs for modeling the per-token likelihood on LM1B. Models are trained on 16B tokens. Training under the discrete diffusion NELBO, where half of the tokens in a batch are masked on average, has 
- Fig.3 (p.21) ![[assets/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-p21.png]]
  - x1 t x2 t x3 t x1 x2 x3 x1 t x2 t x3 t x1 x2 x3
- Fig.4 (p.22) ![[assets/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-p22.png]]
  - We can adapt the masking strategy from Fig. 3 to a FlexAttention compatible sparse masking function as above. This enables the creation of a customized JIT attention operation that uses significantly 
- Fig.5 (p.23) ![[assets/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-p23.png]]
  - Attention computation using FlexAttention with our proposed custom mask.
- Fig.6 (p.26) ![[assets/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-p26.png]]
  - Sample from MDLM (Sahoo et al., 2024a) of length L = 1024 and T = 5K diffusion steps.
- Fig.7 (p.27) ![[assets/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-p27.png]]
  - Sample from BD3-LM for block size L′ = 16 of length L = 2031 under T = 5K diffusion steps (trained with a context length of L = 1024). The generative perplexity of this sample under GPT2-Large is 24.3
- Fig.8 (p.28) ![[assets/block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models-p28.png]]
  - Sample from an AR model (Sahoo et al., 2024a) with length L = 2003 (trained with a context length of L = 1024). The generative perplexity of this sample under GPT2-Large is 10.6 and its entropy is 5.5

### #7 DFlash: Block Diffusion for Flash Speculative Decoding

- Fig.1 (p.2) ![[assets/dflash-block-diffusion-for-flash-speculative-decoding-p02.png]]
  - Speedup comparison between DFlash, EAGLE-3 against Autoregressive Decoding on Qwen3-8B (Yang et al., 2025) with the
- ⭐ Fig.2 (p.4) ![[assets/dflash-block-diffusion-for-flash-speculative-decoding-p04.png]]
  - DFlash Inference Design. Hidden context features extracted from the target model are fused and injected into each draft layer’s
- Fig.3 (p.3) ![[assets/dflash-block-diffusion-for-flash-speculative-decoding-p03.png]]
  - Draft cost of 1, 3, 5-layer DFlash and 1-layer EAGLE-3.
- Fig.4 (p.5) ![[assets/dflash-block-diffusion-for-flash-speculative-decoding-p05.png]]
  - DFlash training attention. The target model provides context features (blue) that condition the draft model. The input consists of clean prompt tokens p and clean response tokens r.
- Fig.5 (p.13) ![[assets/dflash-block-diffusion-for-flash-speculative-decoding-p13.png]]
  - The loss decay makes training converge faster and better. A.5.2. RANDOM SAMPLING OF MASKED BLOCKS

### #8 DSpark: Confidence-Scheduled Speculative Decoding with Semi-

- Fig.1 (p.4) ![[assets/dspark-confidence-scheduled-speculative-decoding-with-semi-autoregressive-generation-p04.png]]
  - Recall from Equation 1 that the per-token latency of speculative decoding is 𝐿= (𝑇draft + 𝑇verify)/𝜏. Autoregressive drafters achieve high 𝜏but pay 𝑇draft ∝𝛾; parallel drafters collapse 𝑇draft to a si

### #9 JETSPEC: Breaking the Scaling Ceiling of Speculative Decodin

- Fig.1 (p.2) ![[assets/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-p02.png]]
  - End-to-end decoding speedup over standard autoregressive decoding on H100 GPUs across math, coding, and chat benchmarks. DFlash denotes the original block-parallel drafting method, DDTree is tree-base
- ⭐ Fig.2 (p.3) ![[assets/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-p03.png]]
  - Expected speculative decoding speedup scales as a function of draft length γ, under different per-token drafting costs c and acceptance rates α. Comparing the two panels shows that reducing c substant
- Fig.3 (p.4) ![[assets/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-p04.png]]
  - JetSpec design overview. JetSpec extracts fused hidden features from the frozen target model and conditions a causal-parallel draft head to generate high-quality candidate trees in one forward pass.
- Fig.4 (p.15) ![[assets/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-p15.png]]
  - Tree-quality failure mode at MATH-500 prompt #0, decode step 0. Both heads draft from the same prefix (last token “We”). The causal head’s rank-1 branch (“ are told that”) is faithful: target joint Σ 
- Fig.5 (p.18) ![[assets/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-p18.png]]
  - Figure 5: Causal attention mask used for training with multiple sampled blocks. Each query can attend to the full verified prefix and to the anchor plus earlier positions within its own block, but can
- Fig.6 (p.19) ![[assets/jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting-p19.png]]
  - Each sampled block includes an anchor position and multiple future token positions. The anchor is retained as block context and excluded from the loss, while loss is applied only to future token posit

### #10 From ATOP to ZCube: Automated Topology Optimization Pipeline

- Fig.1 (p.1) ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p01.png]]
  - ATOP search results on different GPU scales, each point representing a topology. For each scale, we label the three notable points in each plot: Best performance, Most
- Fig.2 (p.3) ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p03.png]]
  - GPT-3 training timeline on rank 0 of classical in- terleaved 1F1B schedule, excluding TP communication as it typically occurs on the intra-server network. • Expert parallelism (EP), used in mixture-of
- Fig.3 (p.4) ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p04.png]]
  - (a) The max number of flow per 100 Gbps under all-to-all traffic in a 256-GPUs topology. (b) The performance degradation of GPT-3 training after a Single ToR Fault in a 4k-GPUs topology. ZCube and Bes
- Fig.4 (p.5) ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p05.png]]
  - Overview of ATOP allows the system to explore novel topology designs automatically, not limited to variants or combinations of existing ones. It can produce high-performance asymmetric topologies, suc
- Fig.5 (p.6) ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p06.png]]
  - Examples of constructing inter-layer and intra-layer connections in ATOP. Unmentioned hyperparameters = 0.
- Fig.6 (p.9) ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p09.png]]
  - During the 4k GPUs search process: (a) The Pareto- optimal topologies generated by ATOP; (b) All the topologies generated by ATOP.
- Fig.7 (p.9) ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p09.png]]
  - (a) The search results of ATOP when adjusting an existing 4k-GPU DCN. (b) The search results when expanding a DCN from 1k GPUs to 4k GPUs. be unfair to other topologies. However, in Case 3, even expan
- Fig.8 (p.10) ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p10.png]]
  - (a) A ZCube(n, k+1) is constructed from 𝑛ZCube(n, k) and 𝑛𝑘switches. (b) An example of ZCube(2, 3). (c) An example of ZCube(84,3)-partial. ZCube(𝑛,𝑘+ 1) is equipped with (𝑘+ 1) NIC ports numbered from
- Fig.9 (p.11) ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p11.png]]
  - The training iteration time for GPT-3 175B and MoE-GPT models and the corresponding network costs on various topologies, under different numbers of GPUs.
- Fig.10 (p.11) ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p11.png]]
  - CDF of PP flow completion time during a GPT-3 175B training iteration on 16384 GPUs. GPU clusters, the failure probability of a single switch is 0.03%.
- Fig.11 (p.12) ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p12.png]]
  - The topology diagrams of ROFT and ZCube on a real testbed. 1M 4M 16M 64M 256M 1G 4G 16G
- Fig.12 (p.12) ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p12.png]]
  - Collective communication performance on real- world deployment. ZCube and ROFT achieve the same all-reduce and all-to-all perfor- mance, while ZCube reduces hardware cost by 25% by using only 48×200G 
- Fig.13 (p.15) ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p15.png]]
  - In the search results of Case 3, the comparison between the number of modified links (another cost metric) and training performance.
- Fig.14 (p.15) ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p15.png]]
  - The search results of ATOP when building a new data center for multi-tenancy.
- Fig.15 (p.15) ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p15.png]]
  - The search results of ATOP when building a new heterogeneous data center with strict search space con- straints.
- Fig.16 (p.16) ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p16.png]]
  - During the ATOP optimization process: (a) The relationship between the number of Pareto-optimal topologies and the total number of topologies generated by ATOP; (b) The Jaccard distance between the Pa
- Fig.17 (p.17) ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p17.png]]
  - Two scenarios degrade all-to-all performance: (a) ECMP hash collision: In Non-blocking 2-layer Rail-Optimized
- Fig.18 (p.17) ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p17.png]]
  - The average JCT for group all-to-all communica- tion under different topologies with link failures on 4096 GPUs, with shading representing the standard deviation of the JCT.
- Fig.19 (p.18) ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p18.png]]
  - Comparison between packet-level network simulation (with packet spraying for load balancing) and the real-world testbed in §6.2. I
- Fig.20 (p.19) ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p19.png]]
  - Comparison of the CDF of flow completion times between NS-3 and flow-level simulators.
- Fig.21 (p.20) ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p20.png]]
  - ROFT topology for a 16384 GPU cluster based on 51.2 Tbps switches.
- Fig.22 (p.20) ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p20.png]]
  - Rail-only topology for a 16384 GPU cluster based on 51.2 Tbps switches. Each Rail-interconnection adopts a 2-layer CLOS architecture, consistent with [51] and [57].
- Fig.23 (p.20) ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p20.png]]
  - HPN topology (dual-port designs for ROFT) for a 16384 GPU cluster based on 51.2 Tbps switches.
- Fig.24 (p.20) ![[assets/from-atop-to-zcube-automated-topology-optimization-pipeline-and-a-highly-cost-effective-network-topology-for-large-model-training-p20.png]]
  - ZCube(128,2) topology for a 16384 GPU cluster based on 51.2 Tbps switches. 880

### #11 KIMI K2.5: VISUAL AGENTIC INTELLIGENCE

- Fig.1 (p.1) ![[assets/kimi-k2-5-visual-agentic-intelligence-p01.png]]
  - Kimi K2.5 main results. 1
- Fig.2 (p.4) ![[assets/kimi-k2-5-visual-agentic-intelligence-p04.png]]
  - Vision RL training curves on vision benchmarks starting from minimal zero-vision SFT. By scaling vision RL FLOPs, the performance continues to improve, demonstrating that zero-vision activation paired
- Fig.3 (p.5) ![[assets/kimi-k2-5-visual-agentic-intelligence-p05.png]]
  - An agent swarm has a trainable orchestrator that dynamically creates specialized frozen subagents and decomposes complex tasks into parallelizable subtasks for efficient distributed execution.
- Fig.4 (p.6) ![[assets/kimi-k2-5-visual-agentic-intelligence-p06.png]]
  - In our parallel-agent reinforcement learning environment, the training accuracy increases smoothly as train- ing progresses. At the same time, the level of parallelism during training also gradually i
- Fig.5 (p.10) ![[assets/kimi-k2-5-visual-agentic-intelligence-p10.png]]
  - Comparison of model performance and token usage for Kimi K2 Thinking following token-efficient RL. compromise alleviates memory pressure, it does not fundamentally resolve the load imbalance caused by
- Fig.6 (p.14) ![[assets/kimi-k2-5-visual-agentic-intelligence-p14.png]]
  - The word cloud visualizes heterogeneous K2.5-based sub-agents dynamically instantiated by the
- Fig.7 (p.14) ![[assets/kimi-k2-5-visual-agentic-intelligence-p14.png]]
  - Comparison of Kimi K2.5 performance un- der Agent Swarm and Discard-all context management in BrowseComp. (60.6%) and surpassing even GPT-5.2 Pro (77.9%). Similarly, WideSearch sees a 6.3% improvement
- Fig.8 (p.15) ![[assets/kimi-k2-5-visual-agentic-intelligence-p15.png]]
  - Agent Swarm achieves 3×–4.5× faster execution time compared to single-agent baselines as target Item-F1 increases from 30% to 70% in WideSearch testing. rather than context truncation, allowing the sy
- Fig.9 (p.21) ![[assets/kimi-k2-5-visual-agentic-intelligence-p21.png]]
  - Learning curves comparing vision-to-text ratios (10:90, 20:80, 50:50) under fixed vision-text token budget across vision and language tasks. Early fusion with lower vision ratios tend to yield better 
- Fig.10 (p.23) ![[assets/kimi-k2-5-visual-agentic-intelligence-p23.png]]
  - Overview of our agentic RL framework. environments with minimal overhead. Our design prioritizes compositional modularity by integrating a suite of plug- gable components, such as a Tolset module for 
- Fig.11 (p.28) ![[assets/kimi-k2-5-visual-agentic-intelligence-p28.png]]
  - Qualitative example of Kimi K2.5 analyzing a complete playthrough of Black Myth: Wukong (24 hours of continuous gameplay across 32 videos at 1080p) using parallel visual agents. See generated webpage 
- Fig.12 (p.29) ![[assets/kimi-k2-5-visual-agentic-intelligence-p29.png]]
  - Qualitative examples of Kimi K2.5 solving visual reasoning tasks via tool use. 29

### #14 DeepStack: Deeply Stacking Visual Tokens is Surprisingly Sim

- Fig.1 (p.1) ![[assets/deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms-p01.png]]
  - Left: Conventional large multimodal models (LMMs) string all visual tokens into a sequence for high- and low-resolution images. Middle: Our DeepStack LMMs stack the tokens into a grid and infuse them 
- Fig.2 (p.4) ![[assets/deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms-p04.png]]
  - Architecture of DeepStack. The main innovation lies in the DeepStack strategy that infuses visual tokens into different layers. Left: DeepStack for LLMs. Given an input image, we feed the tokens extra
- Fig.3 (p.8) ![[assets/deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms-p08.png]]
  - Analysis on using LLM layers to process visual tokens. (a) We insert the visual tokens into different starting layers and initialize the correspondence input embeddings as zero; (b) We fix the first l
- Fig.4 (p.10) ![[assets/deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms-p10.png]]
  - Visualization. Both LLaVA-1.5 and DeepStack use 576 visual context length for a fair comparison.
- Fig.5 (p.9) ![[assets/deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms-p09.png]]
  - Visualization of three sam- pling methods for DeepStack.

### #16 GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUT-PERFORM REINFORCEM

- ⭐ Fig.1 (p.1) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p01.png]]
  - A comparison of learning behavior of the GEPA prompt optimizer against a state-of-the-art prompt optimizer (MIPROv2) and GRPO (24,000 rollouts). As more rollouts are sampled, the prompt optimizers can
- ⭐ Fig.2 (p.3) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p03.png]]
  - This figure shows an example prompt generated by GEPA for the second-hop document retrieval to be performed in a multi-hop question-answer system, along with the seed prompt it started with. Appendix 
- Fig.3 (p.5) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p05.png]]
  - GEPA proposes a new candidate in every iteration by improving existing candidates using one of the two strategies (Reflective Prompt Mutation (Section 3) or System Aware Merge (Appendix D.1)), first e
- Fig.4 (p.4) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p04.png]]
  - GEPA receives the following inputs: A system  instan- tiated with simple prompts to be optimized, training dataset D train (consisting of task instances (x; m) as described in Section 2), the standar
- Fig.5 (p.7) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p07.png]]
  - GEPA’s reflective prompt mutation systematically incorporates task-specific nuances, leading to substantial improvements in performance. This figure visualizes the optimization trajectory taken by GEP
- Fig.6 (p.10) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p10.png]]
  - Comparing the impact of different candidate selection strategies. (Left) As can be seen, selecting the best-performing candidate in every iteration led to a local-optima after one iteration, leading t
- Fig.7 (p.13) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p13.png]]
  - GEPA with GPT-4o is able to generate kernels for AMD NPUs that achieve vector utilization rates as high as 70%, with a mean utilization score of 30.52%. In comparison, GPT-4o, even after up to 10 sequ
- Fig.8 (p.13) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p13.png]]
  - GEPA with GPT-4o is able to iteratively refine and improve CUDA Kernel Code. The graphs shows fast p vs. rollouts plot for p=[0:5; 1], where the speedup is calculated over Pytorch-eager. fast p is a m
- Fig.9 (p.24) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p24.png]]
  - Details of System Aware Merge. r represents a seeded stochastic sampler.
- Fig.10 (p.28) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p28.png]]
  - Final test set performance for aggregate and individual benchmarks.
- Fig.11 (p.28) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p28.png]]
  - This figure compares the learning behaviour of GEPA against GRPO with full-parameter finetun- ing on the 2-hop HoVer task. The relative gap mirrors the previously observed comparison of GEPA against G
- Fig.12 (p.29) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p29.png]]
  - Hotpot QA Bench: rollout vs. score for different models/settings. (a) GPT-4.1 Mini - MIPRO (b) Qwen3 8B - MIPRO 0 50 10 150 20 250
- Fig.13 (p.29) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p29.png]]
  - IFBench: rollout vs. score for different models/settings. (a) GPT-4.1 Mini - MIPRO (b) Qwen3 8B - MIPRO (c) Qwen3 8B - GRPO
- Fig.14 (p.29) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p29.png]]
  - HoverBench: rollout vs. score for different models/settings. (a) GPT-4.1 Mini - MIPRO (b) Qwen3 8B - MIPRO (c) Qwen3 8B - GRPO
- Fig.15 (p.29) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p29.png]]
  - PUPA: rollout vs. score for different models/settings. 29
- Fig.16 (p.30) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p30.png]]
  - Generalization gaps for different optimization methods. Following Wan et al. (2024), we visualize the generalization gap (i.e., the difference between final test set performance and the best achieved 
- Fig.17 (p.30) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p30.png]]
  - These plots visualize the final aggregate scores against the aggregate prompt size (across all benchmarks) of the final optimized system for each optimizer. It can be seen that GEPA consistently pro- 
- Fig.18 (p.31) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p31.png]]
  - Comparing the token counts of optimized programs across benchmarks. (a) Abl:SelectBestCandidate (b) SelectBestCandidate +
- Fig.19 (p.31) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p31.png]]
  - HotpotQA GPT-4.1 Mini 31
- Fig.20 (p.32) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p32.png]]
  - HotpotQA Qwen3 8B (a) Abl:SelectBestCandidate (b) SelectBestCandidate +
- Fig.21 (p.32) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p32.png]]
  - IFBench GPT-4.1 Mini (a) Abl:SelectBestCandidate (b)
- Fig.22 (p.32) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p32.png]]
  - IFBench Qwen3 8B 32
- Fig.23 (p.33) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p33.png]]
  - HoVer GPT-4.1 Mini (a) Abl:SelectBestCandidate (b) SelectBestCandidate +
- Fig.24 (p.33) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p33.png]]
  - HoVer Qwen3 8B (a) Abl:SelectBestCandidate (b) SelectBestCandidate +
- Fig.25 (p.33) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p33.png]]
  - PUPA GPT-4.1 Mini 33
- Fig.26 (p.34) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p34.png]]
  - PUPA Qwen3 8B K.1 PROMPTS AT INTERMEDIATE STAGES FOR PUPA
- Fig.27 (p.12) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p12.png]]
  - We also note that generation stochasticity (temperature based sampling) is eliminated by operating under a cache; this ensures that ob- served improvements tie closely to inference scaling through pro

### #17 SARATHI: Efficient LLM Inference by Piggybacking Decodes wit

- Fig.1 (p.1) ![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p01.png]]
  - Example two-stage pipeline parallel schedule. (a)
- ⭐ Fig.2 (p.3) ![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p03.png]]
  - High-level architecture of a decoder block. sequence length of each request (i.e., the number of input tokens in the given query), and H is the model’s embedding size (e.g., 5120 for LLaMA-13B).
- Fig.3 (p.4) ![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p04.png]]
  - Per-token prefill and decode time with different batch sizes (sequence length = 1024) for LLaMa-13B on A6000 GPU. Prefill saturates GPU compute even at batch size of 1 and results in almost constant p
- Fig.4 (p.4) ![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p04.png]]
  - Impact of the arithmetic intensity (bottom) on the throughput (top) of prefills and decodes for LLaMA-13B on A6000 GPU. operations. Figure 4b shows the arithmetic intensity of each operation separatel
- Fig.5 (p.5) ![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p05.png]]
  - Pipeline bubbles in LLM inference A 2-way PP iteration-level schedule [48] across 4 requests (A,B,C,D) shows the existence of pipeline bubbles due to non-uniform batch execution times. set of layers; 
- Fig.6 (p.6) ![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p06.png]]
  - Example of how attention mask is set across dif- ferent chunk prefill iterations in SARATHI (q and k represent “query" and “key" tokens, respectively). The attention mask for v (“values") is set simil
- Fig.7 (p.7) ![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p07.png]]
  - The effect of tile quantization on the runtime of one iteration of LLaMA-13B on A6000 GPU. maximal batching with that of the baseline scheme that com- putes prefill and decode iterations separately. W
- Fig.8 (p.9) ![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p09.png]]
  - Decode-only speedup with SARATHI on an A6000 GPU with LLaMA-13B (chunk size = 256).
- Fig.9 (p.10) ![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p10.png]]
  - Normalized throughput (tokens/ms) for LLaMa 13B on A6000 GPU with different sequence lengths, P:D ratios, and chunk sizes. 2 4 6 8 10 12 14 16 18
- Fig.10 (p.10) ![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p10.png]]
  - Breakdown of total time spent on different operations for LLaMa 13B on A6000 GPU with varying sequence lengths and batch sizes, using prefill chunk sizes of 256 (top half) and 512 (bottom half). Orang
- Fig.11 (p.11) ![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p11.png]]
  - Comparison with iteration-level scheduler Orca for LLaMa 13B on A6000 GPU. configuration of sequence length and chunk size, we show the effect of varying batch sizes. Further, for each run, we also sh
- Fig.12 (p.12) ![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p12.png]]
  - Impact of SARATHI on pipeline bubbles (top) and request completion times (bottom) for GPT-3 deployed on DGX A100(s) in simulation. the effect of variable sequence lengths on request latencies.
- Fig.13 (p.13) ![[assets/sarathi-efficient-llm-inference-by-piggybacking-decodes-with-chunked-prefills-p13.png]]
  - Ablation study: Effect of varying the chunk size on different components of the system for LLaMa 13B on A6000 GPU. measure the time to compute the prefill phase for various se- quence lengths using th

### #18 Taming Throughput-Latency Tradeoff in LLM Inference with Sar

- Fig.1 (p.1) ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p01.png]]
  - Yi-34B running on two A100 GPUs serving 128 requests from arxiv-summarisation trace. 1a highlights one of the many generation stalls lasting over several seconds in vLLM [53]. 1b shows the impact of i
- ⭐ Fig.2 (p.2) ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p02.png]]
  - Current LLM serving systems involve a tradeoff be- tween throughput and latency depending on their scheduling policy. Prioritizing prefills optimizes throughput but sacrifices TBT (time-between-tokens
- ⭐ Fig.3 (p.5) ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p05.png]]
  - Throughput of the prefill and decode phases with different batch sizes for Mistral-7B running on a single A100 GPU. We use prompt length of 1024 for both prefill and decode experiments. Note that diff
- ⭐ Fig.4 (p.5) ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p05.png]]
  - Prefill and decode time with different input sizes for Mistral-7B running on single A100 GPU. Linear layers contribute to the majority of runtime in both prefill and decode phases. Due to the low arit
- Fig.5 (p.6) ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p06.png]]
  - Arithmetic intensity trend for LLaMA2-70B lin- ear operations with different number of token running on four A100s. Decode batches have low arithmetic intensity i.e., they are bottlenecked by memory f
- Fig.6 (p.6) ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p06.png]]
  - Linear layer execution time as function of number of tokens in a batch for LLaMA2-70B on A100(s) with different tensor parallel degrees. When the number of tokens is small, execution time is dictated 
- Fig.7 (p.6) ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p06.png]]
  - A generation stall occurs when one or more prefills are scheduled in between consecutive decode iterations of a request. A, B, C and D represent different requests. Sub- script d represents a decode i
- Fig.8 (p.7) ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p07.png]]
  - A 2-way pipeline parallel iteration-level schedule in Orca across 4 requests (A,B,C,D) shows the existence of pipeline bubbles due to non-uniform batch execution times.
- Fig.9 (p.8) ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p08.png]]
  - The incremental cost of coalescing prefills with decode batches. We consider two batching schemes – (i) Decode +
- Fig.10 (p.11) ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p11.png]]
  - Capacity (in queries per second) of Mistral-7B and
- Fig.11 (p.11) ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p11.png]]
  - Capacity of LLaMA2-70B and Falcon-180B (mod- els with pipeline parallelism) with different schedulers under strict (SLO-S) and relaxed (SLO-R) latency SLOs.
- Fig.12 (p.12) ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p12.png]]
  - Latency – Throughput tradeoff in vLLM and
- Fig.13 (p.12) ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p12.png]]
  - TP scales poorly across nodes. (a) Median TBT for decode-only batches: cross node TP increases median TBT by more than 2× compared to a 4-way TP within node and PP across nodes. (b) Capacity under str
- Fig.14 (p.13) ![[assets/taming-throughput-latency-tradeoff-in-llm-inference-with-sarathi-serve-p13.png]]
  - Overhead of chunked-prefills in prefill computation for Yi-34B (TP-2) normalized to the cost of no-chunking, shown for various prompt lengths using chunk lengths of 512, 1024 and 2048.

### #19 GEPA: REFLECTIVE PROMPT EVOLUTION CAN OUTPERFORM REINFORCEME

- ⭐ Fig.1 (p.1) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p01.png]]
  - A comparison of learning behavior of the GEPA prompt optimizer against a state-of-the-art prompt optimizer (MIPROv2) and GRPO (24,000 rollouts). As more rollouts are sampled, the prompt optimizers can
- ⭐ Fig.2 (p.3) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p03.png]]
  - This figure shows an example prompt generated by GEPA for the second-hop document retrieval to be performed in a multi-hop question-answer system, along with the seed prompt it started with. Appendix 
- Fig.3 (p.5) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p05.png]]
  - GEPA proposes a new candidate in every iteration by improving existing candidates using one of the two strategies (Reflective Prompt Mutation (Section 3) or System Aware Merge (Appendix D.1)), first e
- Fig.4 (p.4) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p04.png]]
  - GEPA receives the following inputs: A system  instan- tiated with simple prompts to be optimized, training dataset D train (consisting of task instances (x; m) as described in Section 2), the standar
- Fig.5 (p.7) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p07.png]]
  - GEPA’s reflective prompt mutation systematically incorporates task-specific nuances, leading to substantial improvements in performance. This figure visualizes the optimization trajectory taken by GEP
- Fig.6 (p.10) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p10.png]]
  - Comparing the impact of different candidate selection strategies. (Left) As can be seen, selecting the best-performing candidate in every iteration led to a local-optima after one iteration, leading t
- Fig.7 (p.13) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p13.png]]
  - GEPA with GPT-4o is able to generate kernels for AMD NPUs that achieve vector utilization rates as high as 70%, with a mean utilization score of 30.52%. In comparison, GPT-4o, even after up to 10 sequ
- Fig.8 (p.13) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p13.png]]
  - GEPA with GPT-4o is able to iteratively refine and improve CUDA Kernel Code. The graphs shows fast p vs. rollouts plot for p=[0:5; 1], where the speedup is calculated over Pytorch-eager. fast p is a m
- Fig.9 (p.24) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p24.png]]
  - Details of System Aware Merge. r represents a seeded stochastic sampler.
- Fig.10 (p.28) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p28.png]]
  - Final test set performance for aggregate and individual benchmarks.
- Fig.11 (p.28) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p28.png]]
  - This figure compares the learning behaviour of GEPA against GRPO with full-parameter finetun- ing on the 2-hop HoVer task. The relative gap mirrors the previously observed comparison of GEPA against G
- Fig.12 (p.29) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p29.png]]
  - Hotpot QA Bench: rollout vs. score for different models/settings. (a) GPT-4.1 Mini - MIPRO (b) Qwen3 8B - MIPRO 0 50 10 150 20 250
- Fig.13 (p.29) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p29.png]]
  - IFBench: rollout vs. score for different models/settings. (a) GPT-4.1 Mini - MIPRO (b) Qwen3 8B - MIPRO (c) Qwen3 8B - GRPO
- Fig.14 (p.29) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p29.png]]
  - HoverBench: rollout vs. score for different models/settings. (a) GPT-4.1 Mini - MIPRO (b) Qwen3 8B - MIPRO (c) Qwen3 8B - GRPO
- Fig.15 (p.29) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p29.png]]
  - PUPA: rollout vs. score for different models/settings. 29
- Fig.16 (p.30) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p30.png]]
  - Generalization gaps for different optimization methods. Following Wan et al. (2024), we visualize the generalization gap (i.e., the difference between final test set performance and the best achieved 
- Fig.17 (p.30) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p30.png]]
  - These plots visualize the final aggregate scores against the aggregate prompt size (across all benchmarks) of the final optimized system for each optimizer. It can be seen that GEPA consistently pro- 
- Fig.18 (p.31) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p31.png]]
  - Comparing the token counts of optimized programs across benchmarks. (a) Abl:SelectBestCandidate (b) SelectBestCandidate +
- Fig.19 (p.31) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p31.png]]
  - HotpotQA GPT-4.1 Mini 31
- Fig.20 (p.32) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p32.png]]
  - HotpotQA Qwen3 8B (a) Abl:SelectBestCandidate (b) SelectBestCandidate +
- Fig.21 (p.32) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p32.png]]
  - IFBench GPT-4.1 Mini (a) Abl:SelectBestCandidate (b)
- Fig.22 (p.32) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p32.png]]
  - IFBench Qwen3 8B 32
- Fig.23 (p.33) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p33.png]]
  - HoVer GPT-4.1 Mini (a) Abl:SelectBestCandidate (b) SelectBestCandidate +
- Fig.24 (p.33) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p33.png]]
  - HoVer Qwen3 8B (a) Abl:SelectBestCandidate (b) SelectBestCandidate +
- Fig.25 (p.33) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p33.png]]
  - PUPA GPT-4.1 Mini 33
- Fig.26 (p.34) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p34.png]]
  - PUPA Qwen3 8B K.1 PROMPTS AT INTERMEDIATE STAGES FOR PUPA
- Fig.27 (p.12) ![[assets/gepa-reflective-prompt-evolution-can-outperform-reinforcement-learning-p12.png]]
  - We also note that generation stochasticity (temperature based sampling) is eliminated by operating under a cache; this ensures that ob- served improvements tie closely to inference scaling through pro

### #20 DeepSeek-V4: Towards Highly Efficient Million-Token Context 

- ⭐ Fig.1 (p.14) ![[assets/deepseek-v4-towards-highly-efficient-million-token-context-intelligence-p14.png]]
  - 2.4. Muon Optimizer
- ⭐ Fig.5 (p.15) ![[assets/deepseek-v4-towards-highly-efficient-million-token-context-intelligence-p15.png]]
  - This forms a fine-grained pipeline among experts, keeping both computation and communication continuous throughout the wave. The wave-based scheduling speeds up the 15

### #21 KIMI-VL TECHNICAL REPORT

- Fig.1 (p.1) ![[assets/kimi-vl-technical-report-p01.png]]
  - Comparison between Kimi-VL-Thinking-2506 and frontier open-source VLMs, including short-thinking VLMs (e.g. Gemma-3 series, Qwen2.5-VL series) and long-thinking VLMs (QVQ-72B/Max-Preview), on MathVisi
- Fig.2 (p.2) ![[assets/kimi-vl-technical-report-p02.png]]
  - Highlights of Kimi-VL performance for a wide range of benchmarks like, general benchmarks (MMMU, MMBench), OCR (InfoVQA), multi-image (BLINK), long video (LongVideoBench, Video-MME), long document (MM
- Fig.3 (p.3) ![[assets/kimi-vl-technical-report-p03.png]]
  - The model architecture of Kimi-VL and Kimi-VL-Thinking, consisting of a MoonViT that allows native- resolution images, an MLP projector, and a Mixture-of-Experts (MoE) language decoder. 1) Kimi-VL is 
- Fig.4 (p.4) ![[assets/kimi-vl-technical-report-p04.png]]
  - The pre-training stages of Kimi-VL consume a total of 4.4T tokens after text-only pre-training of its language model. To preserve text abilities, all stages that update the language model are joint tr
- Fig.5 (p.6) ![[assets/kimi-vl-technical-report-p06.png]]
  - The post-training stages of Kimi-VL and Kimi-VL-Thinking, including two stages of joint SFT in 32K and 128K context, and further long-CoT SFT and RL stages to activate and enhance long thinking abilit
- Fig.6 (p.8) ![[assets/kimi-vl-technical-report-p08.png]]
  - Manuscript reasoning visualization. Kimi-VL-Thinking demonstrates the ability to perform historical and scientific inference by analyzing handwritten manuscripts step by step. In this example, our mod
- Fig.7 (p.12) ![[assets/kimi-vl-technical-report-p12.png]]
  - Kimi-VL exhibits strong visual reasoning capabilities by grounding visual content in spatial, contextual, and cultural knowledge. It accurately identifies matching urban locations based on structural 
- Fig.8 (p.13) ![[assets/kimi-vl-technical-report-p13.png]]
  - Kimi-VL demonstrates its capability to perform symbolic reasoning and geometric inference by solving a circle geometry problem step by step. The model analyzes given conditions, applies geometric theo
- Fig.9 (p.14) ![[assets/kimi-vl-technical-report-p14.png]]
  - Diverse OCR visualization. Kimi-VL demonstrates strong OCR capabilities across varied content types, including structured financial tables, complex mathematical formulas, and handwritten Chinese text.
- Fig.10 (p.15) ![[assets/kimi-vl-technical-report-p15.png]]
  - Kimi-VL is capable of following multi-step reasoning processes to complete complex GUI tasks. In this example, it successfully enables the “Do Not Track” feature in the Chrome browser to enhance onlin
- Fig.11 (p.16) ![[assets/kimi-vl-technical-report-p16.png]]
  - Video scene splitting. Kimi-VL processes a long-form video by segmenting it into coherent scenes and providing detailed start/end timestamps along with fine-grained natural language descriptions for e
- Fig.12 (p.17) ![[assets/kimi-vl-technical-report-p17.png]]
  - Catching and understanding key details from an hour-long video course. Kimi-VL demonstrates its ability to comprehend and interpret instructional video content by analyzing frame sequences and extract
- Fig.13 (p.16) ![[assets/kimi-vl-technical-report-p16.png]]
  - Specifically, increasing the max thinking token length at inference time consistently improves test-time accuracy across all three 16

### #23 High-Dimensional Continuous Control Using Generalized Advant

- Fig.1 (p.8) ![[assets/high-dimensional-continuous-control-using-generalized-advantage-estimation-p08.png]]
  - 6.2.1 ARCHITECTURE
- Fig.2 (p.10) ![[assets/high-dimensional-continuous-control-using-generalized-advantage-estimation-p10.png]]
  - Left: learning curves for cart-pole task, using generalized advantage estimation with varying values of λ at γ = 0.99. The fastest policy improvement is obtain by intermediate values of λ in the range
- Fig.3 (p.10) ![[assets/high-dimensional-continuous-control-using-generalized-advantage-estimation-p10.png]]
  - Left: Learning curves for 3D bipedal locomotion, averaged across nine runs of the algo- rithm. Right: learning curves for 3D quadrupedal locomotion, averaged across ﬁve runs.
- Fig.4 (p.11) ![[assets/high-dimensional-continuous-control-using-generalized-advantage-estimation-p11.png]]
  - (a) Learning curve from quadrupedal walking, (b) learning curve for 3D standing up, (c) clips from 3D standing up. 7 DISCUSSION

### #24 KIMI K2: OPEN AGENTIC INTELLIGENCE

- Fig.1 (p.1) ![[assets/kimi-k2-open-agentic-intelligence-p01.png]]
  - Kimi K2 main results.2 1https://huggingface.co/moonshotai/Kimi-K2-Instruct 2All models evaluated above are non-thinking models. For SWE-bench Multilingual, we evaluated only Claude 4 Sonnet because th
- Fig.2 (p.4) ![[assets/kimi-k2-open-agentic-intelligence-p04.png]]
  - Left: During a mid-scale training run, attention logits rapidly exceed 1000, which could lead to potential numerical instabilities and even training divergence. Right: Maximum logits for Kimi K2 with 
- Fig.3 (p.5) ![[assets/kimi-k2-open-agentic-intelligence-p05.png]]
  - Per-step training loss curve of Kimi K2, without smoothing or sub-sampling. It shows no spikes throughout the entire training process. Note that we omit the very beginning of training for clarity. A k
- Fig.4 (p.5) ![[assets/kimi-k2-open-agentic-intelligence-p05.png]]
  - • Fidelity verification: To ensure consistency between original and rewritten content, we perform fidelity checks that compare the semantic alignment of each rephrased passage with its source. This se
- Fig.5 (p.7) ![[assets/kimi-k2-open-agentic-intelligence-p07.png]]
  - Sparsity Scaling Law. Increasing sparsity leads to improved model performance. We fixed the number of activated experts to 8 and the number of shared experts to 1, and varied the total number of exper
- Fig.6 (p.7) ![[assets/kimi-k2-open-agentic-intelligence-p07.png]]
  - Scaling curves for models with number of atten- tion heads equals to number of layers and their counter- parts with doubled attention heads. Doubling the number of attention heads leads to a reduction
- Fig.7 (p.8) ![[assets/kimi-k2-open-agentic-intelligence-p08.png]]
  - Computation, communication and offloading overlapped in different PP phases.
- Fig.8 (p.10) ![[assets/kimi-k2-open-agentic-intelligence-p10.png]]
  - Data synthesis pipeline for tool use. (a) Tool specs are from both real-world tools and LLMs; agents and tasks are the generated from the tool repo. (b) Multi-agent pipeline to generate and filter tra
- Fig.9 (p.10) ![[assets/kimi-k2-open-agentic-intelligence-p10.png]]
  - t-SNE visualizations of tool embeddings. (a) Real-world MCP tools exhibit natural clustering based on their original source categories. (b) Synthetic tools are organized into pre-defined domain catego
- Fig.10 (p.14) ![[assets/kimi-k2-open-agentic-intelligence-p14.png]]
  - Parameter update utilizing a checkpoint engine
- Fig.11 (p.29) ![[assets/kimi-k2-open-agentic-intelligence-p29.png]]
  - Chinese in-house benchmark evaluation. rate, i.e. 98.9. On FaithJudge’s RAG tasks the hallucination rate is 7.4 %, likewise present as 92.6 for table consistency.
- Fig.12 (p.30) ![[assets/kimi-k2-open-agentic-intelligence-p30.png]]
  - Applying QK-Clip to Muon in a small-scale setting with an aggresive threshold (t = 30) has negligible impact on loss, indicating that it is a safe and effective method for constraining attention logit
- Fig.13 (p.32) ![[assets/kimi-k2-open-agentic-intelligence-p32.png]]
  - pipeline for RL weight update

### #25 Search-R1: Training LLMs to Reason and Leverage Search Engin

- Fig.1 (p.4) ![[assets/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-p04.png]]
  - Demonstration of PPO and GRPO training with the search engine (SEARCH-R1).
- Fig.2 (p.9) ![[assets/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-p09.png]]
  - (a) PPO vs. GRPO: GRPO generally converges faster but may exhibit instability after trained for a number of steps, whereas PPO provides more stable optimization but converges at a slower rate. (b) Bas
- Fig.3 (p.17) ![[assets/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-p17.png]]
  - Retrieved Token Loss Masking Study instruction-tuned models exhibit faster convergence and benefit from higher initial perfor- mance relative to their base counterparts. Despite this early advantage, 
- Fig.4 (p.17) ![[assets/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-p17.png]]
  - Study of SEARCH-R1 on base and instruct LLMs. The instruction model converges faster and starts from a better initial performance. However, the final performance of both models is very similar. F
- Fig.5 (p.18) ![[assets/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-p18.png]]
  - Training dynamics of SEARCH-R1 with PPO and GRPO as the base RL method across four LLMs. GRPO generally converges faster but may exhibit instability after trained for a number of steps, whereas PPO pr
- Fig.6 (p.19) ![[assets/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-p19.png]]
  - The training dynamics of SEARCH-R1 with a different number of retrieved pas- sages. (LLM: Qwen2.5-7b-base, RL: PPO)
- Fig.7 (p.19) ![[assets/search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning-p19.png]]
  - We observe that a larger group size generally leads to faster convergence but may also increase the risk of collapse due to the inherent instability of reinforcement learning.

### #26 HYPER-CONNECTIONS

- ⭐ Fig.1 (p.1) ![[assets/hyper-connections-p01.png]]
  - The performance of the baseline model OLMoE-1B-7B and the model with hyper- connections, OLMoE-1B-7B-DHC×4. (1) and (2) show the training loss (0.99 EMA smoothed) and the C4-en validation loss, respec
- ⭐ Fig.2 (p.2) ![[assets/hyper-connections-p02.png]]
  - Hyper-connections (HC) with an expansion rate of n = 2. (a) Residual connections. (b) Hyper-connections: β1, β2, α0,0, α0,1, α1,0, α1,1, α2,1, and α2,2 are learnable scalars or scalars predicted by th
- ⭐ Fig.3 (p.2) ![[assets/hyper-connections-p02.png]]
  - Cosine similarity be- tween the input of the current and the previous layers for the OLMo-1B models (Groeneveld et al., 2024). The curve represents the median of similarity, while the shaded area indi
- ⭐ Fig.4 (p.5) ![[assets/hyper-connections-p05.png]]
  - Sequential and parallel arrangements of hyper-connections with n = 2.
- Fig.5 (p.6) ![[assets/hyper-connections-p06.png]]
  - Comparison of training loss curves for different expansion rate. The left subfigure includes models with dynamic hyper-connections (DHC) at various expansion rates, while the right subfigure shows the
- Fig.6 (p.8) ![[assets/hyper-connections-p08.png]]
  - (1) and (2) Training loss (0.99 EMA smoothed) and C4-en validation loss for OLMo-7B and OLMo-7B-DHC×4 models. (3) and (4) Accuracy curves on hellaswag and sciq, demonstrating the superior performance 
- Fig.7 (p.9) ![[assets/hyper-connections-p09.png]]
  - Visualization of connection matrices for hyper-connections and various related baseline methods. The attention layers, which have odd ids, are marked with green tick marks.
- Fig.8 (p.14) ![[assets/hyper-connections-p14.png]]
  - Comparison between transformers with hyper-connections and that with residual connec- tions. 14
- Fig.9 (p.17) ![[assets/hyper-connections-p17.png]]
  - Loss curves in V3 validation sets and accuracy curves on downstream tasks for OLMoE-1B7B and OLMoE-1B7B-DHC×4 models. 17
- Fig.10 (p.18) ![[assets/hyper-connections-p18.png]]
  - Loss curves in V3 validation set and accuracy curves on downstream tasks for OLMo-7B and OLMo-7B-DHC×4 models. 18
- Fig.11 (p.20) ![[assets/hyper-connections-p20.png]]
  - Training loss curves of ViT/16-Large and ViT/16-Large-DHC×2, smoothed using an
- Fig.12 (p.21) ![[assets/hyper-connections-p21.png]]
  - Distribution of weights of last DHC in ViT-Base/16-DHC×2 model. F MORE VISUALIZATION AND ANALYSIS
- Fig.13 (p.22) ![[assets/hyper-connections-p22.png]]
  - Visualization of unfolded connection matrix.
- Fig.14 (p.23) ![[assets/hyper-connections-p23.png]]
  - Comparison of unfolded connection matrices for OLMo-1B-DHC×1, OLMo-1B-DHC×2 and OLMo-1B-DHC×4 model.
- Fig.15 (p.31) ![[assets/hyper-connections-p31.png]]
  - Training loss curves of related works, smoothed using Exponential Moving Average (EMA) with a decay rate of 0.99. 31
- Fig.16 (p.32) ![[assets/hyper-connections-p32.png]]
  - Training loss curves of DHC with tanh over 500 billion tokens, smoothed using
- Fig.17 (p.32) ![[assets/hyper-connections-p32.png]]
  - Training loss curves of DHC without tanh over 500 billion tokens, smoothed using
- Fig.18 (p.33) ![[assets/hyper-connections-p33.png]]
  - Training loss curves comparied with parallel transformer blocks (PTB), smoothed using

### #27 BERTopic: Neural topic modeling with a class-based TF-IDF pr

- Fig.1 (p.7) ![[assets/bertopic-neural-topic-modeling-with-a-class-based-tf-idf-procedure-p07.png]]
  - Computation time (wall time) in seconds of each topic model on the Trump dataset. Increasing sizes of vocabularies were regulated through selection of documents ranging from 1000 documents until 43000

### #28 Dual-Head Reasoning Distillation: Improving Classifier Accur

- Fig.1 (p.2) ![[assets/dual-head-reasoning-distillation-improving-classifier-accuracy-with-train-time-only-reasoning-p02.png]]
  - SuperGLUE per-task scores for four backbones. DHRD (train-time reasoning) consistently beats the pooled-classifier baseline and rivals teacher model Gemini 2.5 Flash, with the largest gains on CB/COPA
- Fig.2 (p.3) ![[assets/dual-head-reasoning-distillation-improving-classifier-accuracy-with-train-time-only-reasoning-p03.png]]
  - Dual-head fine-tuning on a shared decoder. The classification head pools hidden states over the input span (blue) to produce K class logits. The train-only reasoning head applies a causal LM loss over

### #29 Dynamic Large Concept Models: Latent Reasoning in an Adaptiv

- Fig.1 (p.4) ![[assets/dynamic-large-concept-models-latent-reasoning-in-an-adaptive-semantic-space-p04.png]]
  - 3.1
- Fig.9 (p.7) ![[assets/dynamic-large-concept-models-latent-reasoning-in-an-adaptive-semantic-space-p07.png]]
  - 4.3

### #30 HybridFlow: A Flexible and Efficient RLHF Framework

- Fig.1 (p.3) ![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p03.png]]
  - Dataflow graph of 3 RLHF algorithms [19, 43, 55].
- Fig.2 (p.3) ![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p03.png]]
  - Programming model used in RLHF systems. (a)
- Fig.3 (p.4) ![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p04.png]]
  - Dataflow execution given a model placement plan.
- Fig.4 (p.6) ![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p06.png]]
  - Architecture of HybridFlow. 3D-HybridEngine and Auto-Mapping algorithm. The hybrid programming model includes a set of hierarchical APIs to enable flexible expression of the RLHF dataflow and effi- ci
- Fig.5 (p.6) ![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p06.png]]
  - An illustration of hierarchical APIs. (a) Model with 3D parallel configuration, resource allocation, and 3DParallelWorker initialization. (b) Asynchronous data re- sharding between two models with col
- Fig.6 (p.7) ![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p07.png]]
  - Implementation of PPO [55], ReMax [43], and Safe- RLHF [19]. Users can adapt to different RLHF algorithms by simply adding or deleting a few lines of code. our programming model, HybridFlow is flexibl
- Fig.7 (p.8) ![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p08.png]]
  - 3D-HybridEngine workflow in one RLHF iteration. 4 GPUs are used for actor training and generation. 1-2-2 (𝑝-𝑡-𝑑) parallel groups are used in training and 1-1-2-2 (𝑝𝑔- 𝑡𝑔-𝑑𝑔-𝑑) parallel groups are used
- Fig.8 (p.8) ![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p08.png]]
  - Model weights resharding. 2 machines each with 4 GPUs are used for actor training and generation. model parameters updated in iteration 𝑖(step 1○in Figure 7), for generation within each micro DP group
- Fig.9 (p.11) ![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p11.png]]
  - PPO throughput. Numbers in parentheses are HybridFlow speedups compared with baselines. 8 16 32 64 128 # of GPUs 0 1 2 3
- Fig.10 (p.11) ![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p11.png]]
  - ReMax throughput. Numbers in parentheses are HybridFlow speedups compared with baselines 8 16 32 64 128 # of GPUs 0 1 2 3
- Fig.11 (p.11) ![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p11.png]]
  - Safe-RLHF throughput. Numbers in the parentheses are HybridFlow speedups compared with the baselines reward models. Each model is a Llama [73] model with sizes ranging from 7B to 70B. Safe-RLHF has an
- Fig.12 (p.12) ![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p12.png]]
  - Throughput of HybridFlow under different placements 32 64 96 128 # of GPUs
- Fig.13 (p.12) ![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p12.png]]
  - Placement comparison under 13B actor and reference policy & 70B critic and reward model.
- Fig.14 (p.13) ![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p13.png]]
  - Transition time between actor training and generation.
- Fig.15 (p.13) ![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p13.png]]
  - Time breakdown on different generation parallel sizes of the actor model on 16 GPUs. various model scales, which is the time to reshard model weights from training to generation, under the same settin
- Fig.16 (p.13) ![[assets/hybridflow-a-flexible-and-efficient-rlhf-framework-p13.png]]
  - Runtime of device mapping algorithm. The model size and # of GPUs are simultaneously scaled.

### #31 Let It Flow: Agentic Crafting on Rock and Roll

- ⭐ Fig.1 (p.1) ![[assets/let-it-flow-agentic-crafting-on-rock-and-roll-p01.png]]
  - Overview of the Agentic Learning Ecosystem (ALE) and ROME Performance. 1[cs.AI] 12 Mar 2026
- ⭐ Fig.2 (p.4) ![[assets/let-it-flow-agentic-crafting-on-rock-and-roll-p04.png]]
  - The overview of agentic RL ecosystem (a) and its training pipeline (b). technical stack, ALE is also a call to reframe the community’s priorities. In complex agentic settings, the central challenge is
- Fig.3 (p.5) ![[assets/let-it-flow-agentic-crafting-on-rock-and-roll-p05.png]]
  - ROLL Architecture. (a) ROLL pipelines LLM generation, environment interaction, and reward phases at trajectory-level granularity. Training is also decoupled via a sample buffer using an asyn- chronous
- Fig.4 (p.6) ![[assets/let-it-flow-agentic-crafting-on-rock-and-roll-p06.png]]
  - ROCK System Architecture.
- Fig.5 (p.8) ![[assets/let-it-flow-agentic-crafting-on-rock-and-roll-p08.png]]
  - The overview of iFlow CLI architecture and execution. these requests already contain the complete historical context, fully orchestrated by the iFlow CLI. The proxy then forwards these requests to the
- Fig.6 (p.10) ![[assets/let-it-flow-agentic-crafting-on-rock-and-roll-p10.png]]
  - Overview of data sources and composition pipelines for training agentic models, spanning code centric basic data and agentic data. 3
- Fig.7 (p.16) ![[assets/let-it-flow-agentic-crafting-on-rock-and-roll-p16.png]]
  - Overview of ROME’s Training Pipeline. incidents. Finally, we generated corresponding golden trajectories devoid of general-security issues for subsequent post-training (e.g., SFT and RL). Our overarch
- Fig.8 (p.20) ![[assets/let-it-flow-agentic-crafting-on-rock-and-roll-p20.png]]
  - Overview of the Proposed Interaction-Perceptive Agentic Policy Optimization (IPA) training pipeline. sample efficiency(§3.2.4.4). An overview of our framework, including its key components and data fl
- Fig.9 (p.22) ![[assets/let-it-flow-agentic-crafting-on-rock-and-roll-p22.png]]
  - Comparison of importance sampling strategies across token-level, chunk-level, and sentence- level granularities, where chunk-level aligns with the natural granularity of interactions.
- Fig.10 (p.23) ![[assets/let-it-flow-agentic-crafting-on-rock-and-roll-p23.png]]
  - Comparison of Chunk-Level Optimization and baseline on a mini-set of the training data. Left:
- Fig.11 (p.24) ![[assets/let-it-flow-agentic-crafting-on-rock-and-roll-p24.png]]
  - Illustration of the Chunk-Level Initialized Resampling Strategy (Sequential Rollback). Left: In challenging tasks, sampling high-quality trajectories from the beginning is difficult, severely limiting
- Fig.12 (p.25) ![[assets/let-it-flow-agentic-crafting-on-rock-and-roll-p25.png]]
  - Performance of Sequential Rollback and baseline (naive sampling) on a challenging training task. Left: Average success rate during training, which reflects the percentage of positive signals in traini
- Fig.13 (p.26) ![[assets/let-it-flow-agentic-crafting-on-rock-and-roll-p26.png]]
  - Comparison of IPA with & without Chunk-Level Initialized Resampling (Parallelized Initial- ization) on a mini-set of the training data. Left: Average success rate on training tasks. The gap between cu
- Fig.14 (p.27) ![[assets/let-it-flow-agentic-crafting-on-rock-and-roll-p27.png]]
  - Benchmark characterization and cross-benchmark comparison of Terminal Bench Pro against other benchmarks.
- Fig.15 (p.28) ![[assets/let-it-flow-agentic-crafting-on-rock-and-roll-p28.png]]
  - Performance-parameter trade-offs in agentic tasks. Scores represent averages on general agentic and code agent benchmarks. Models with known parameters are shown as circles, while proprietary models w
- Fig.16 (p.34) ![[assets/let-it-flow-agentic-crafting-on-rock-and-roll-p34.png]]
  - Pairwise win-rate matrix (%) on the 100-task real-world benchmark under 30-expert blinded majority voting. Each cell reports the percentage of tasks where the row model is judged better than the col- 
- Fig.17 (p.36) ![[assets/let-it-flow-agentic-crafting-on-rock-and-roll-p36.png]]
  - Case study 1 screenshot examples: Sleep Management System Generation. 36
- Fig.18 (p.37) ![[assets/let-it-flow-agentic-crafting-on-rock-and-roll-p37.png]]
  - Case study 2 screenshot examples: Solar System Modeling. 37

### #32 Beyond Ten Turns: Unlocking Long-Horizon Agentic Search with

- Fig.1 (p.1) ![[assets/beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl-p01.png]]
  - (Left) Asynchronous RL brings substantial improvements: Through RL training, our agent, ASearcher-Web-QwQ, obtains +15.0, +2.4, and +15.6 improvements on GAIA, xBench, and

### #33 AREAL: A Large-Scale Asynchronous Reinforcement Learning Sys

- Fig.1 (p.4) ![[assets/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-p04.png]]
  - Execution timeline of a synchronous (left) and a one-step overlap (right) RL system showing underutilized inference devices. … Rollout Controller Reward Service
- Fig.2 (p.4) ![[assets/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-p04.png]]
  - The AREAL architecture featuring asynchronous generation and training components.
- Fig.3 (p.4) ![[assets/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-p04.png]]
  - Illustration of generation management in AREAL. Vertical lines show the ready time for the next step training. Blue crosses show the interrupted requests when new parameters arrive. 4
- Fig.4 (p.8) ![[assets/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-p08.png]]
  - The strong scaling trend. Dotted lines indicate ideal linear scaling. verl consistently encounters OOM with 32k context length and the 32B model so the data points are missing. 8
- Fig.5 (p.9) ![[assets/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-p09.png]]
  - Ablation studies of the decoupled PPO objective and staleness control with a 1.5B model on math reasoning tasks. Both algorithmic choices are essential. With a moderate staleness value and the decoupl
- Fig.6 (p.10) ![[assets/areal-a-large-scale-asynchronous-reinforcement-learning-system-for-language-reasoning-p10.png]]
  - Ablation studies on system optimizations. experimental setup, we configured 32 micro-batches for the standard setting and established a token budget of 32,768 per micro-batch for the dynamic batching 

### #34 DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via 

- Fig.2 (p.6) ![[assets/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-p06.png]]
  - In the initial stage, we collect thousands of cold-start data that exhibits a conversational, human-aligned thinking process. RL training is then applied to improve the model perfor- mance with the co
- Fig.3 (p.14) ![[assets/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-p14.png]]
  - For each question ? , GRPO samples a group of outputs f= 1, = 2,    , = g from the old policy 14
- Fig.6 (p.35) ![[assets/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-p35.png]]
  - B.6. Ablation Study of Language Consistency Reward
- Fig.7 (p.37) ![[assets/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-p37.png]]
  - As can be seen, without the LC reward, language consistency gradually deteriorates as train- ing steps increase. However, when the LC reward is applied, stable language consistency is maintained throu
- Fig.13 (p.48) ![[assets/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-p48.png]]
  - We have categorized potential content safety challenges faced by language models into 4 major categories and 28 subcategories.
- Fig.14 (p.53) ![[assets/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning-p53.png]]
  - For DeepSeek-V3 and DeepSeek-R1, we evaluated safety scores for models with and without the risk control system (introduced in D.3.1). Additionally, we tested the multilingual safety performance of Cl

### #35 Conditional Memory via Scalable Lookup: A New Axis of Sparsi

- Fig.2 (p.6) ![[assets/conditional-memory-via-scalable-lookup-a-new-axis-of-sparsity-for-large-language-models-p06.png]]
  - During training, to accommodate large-scale embedding tables, we employ standard model parallelism by sharding the tables across available GPUs. An All-to-All communication primitive is used to gather
- Fig.5 (p.16) ![[assets/conditional-memory-via-scalable-lookup-a-new-axis-of-sparsity-for-large-language-models-p16.png]]
  - We find that three components yield the most significant gains: (i) branch- specific fusion within the multi-branch backbone, (ii) context-aware gating, and (iii) tokenizer compression. Removing any o
- Fig.7 (p.18) ![[assets/conditional-memory-via-scalable-lookup-a-new-axis-of-sparsity-for-large-language-models-p18.png]]
  - The results demonstrate a distinct pattern of selectivity. The gating mechanism consistently activates (shown in red) upon completing local, static patterns. In English, we observe strong activations 

### #37 Linear Optimal Topic Transport for Document Similarity

- Fig.1 (p.7) ![[assets/linear-optimal-topic-transport-for-document-similarity-p07.png]]
  - k-NN classification performance across datasets affects mean test error in the CLASSIC dataset. 531
- Fig.2 (p.8) ![[assets/linear-optimal-topic-transport-for-document-similarity-p08.png]]
  - t-SNE on CLASSIC

### #38 Root Mean Square Layer Normalization

- Fig.1 (p.1) ![[assets/root-mean-square-layer-normalization-p01.png]]
  - One major feature of LayerNorm that is widely regarded as contributions to the stabilization is its re-centering invariance property: the summed inputs after LayerNorm remain intact when the inputs or
- Fig.2 (p.6) ![[assets/root-mean-square-layer-normalization-p06.png]]
  - SacreBLEU score on newstest2013 for the RNNSearch. Models are implemented accord- ing to Nematus [25] in Tensorﬂow.
- Fig.3 (p.7) ![[assets/root-mean-square-layer-normalization-p07.png]]
  - SacreBLEU score on new- stest2013 (devset) for the RNNSearch with pRMSNorm. We use Tensorﬂow-version Ne- matus, and change p by a step size of 10%.
- Fig.4 (p.7) ![[assets/root-mean-square-layer-normalization-p07.png]]
  - SacreBLEU score curve of Layer-
- Fig.5 (p.8) ![[assets/root-mean-square-layer-normalization-p08.png]]
  - Error rate on validation set for the attentive reader model.
- Fig.6 (p.8) ![[assets/root-mean-square-layer-normalization-p08.png]]
  - Recall@K values on validation set for the order-embedding models. worse than RMSNorm. Although in Figure 5 the performance of RMSNorm and LayerNorm is comparable, RMSNorm is around 15% faster than Lay
- Fig.7 (p.13) ![[assets/root-mean-square-layer-normalization-p13.png]]
  - SacreBLEU score curve over train- ing steps on newstest2013 (devset) for the RNNSearch. Models are trained with Nema- tus in Theano.

### #39 GQA: Training Generalized Multi-Query Transformer Models fro

- Fig.1 (p.1) ![[assets/gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints-p01.png]]
  - Overview of conversion from multi-head to multi-query attention. Key and value projection matri- ces from all heads are mean pooled into a single head.
- Fig.2 (p.2) ![[assets/gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints-p02.png]]
  - Overview of grouped-query method. Multi-head attention has H query, key, and value heads. Multi-query attention shares single key and value heads across all query heads. Grouped-query attention instea
- Fig.3 (p.3) ![[assets/gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints-p03.png]]
  - Uptrained MQA yields a favorable tradeoff compared to MHA with higher quality and faster speed than MHA-Large, and GQA achieves even better performance with similar speed gains and comparable quality 
- Fig.4 (p.4) ![[assets/gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints-p04.png]]
  - Performance comparison of different check- point conversion methods for T5-Large uptrained to MQA with proportion α = 0.05. ‘Mean’ mean-pools key and value heads, ‘First’ selects the first head and ‘R
- Fig.5 (p.4) ![[assets/gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints-p04.png]]
  - Performance as a function of uptraining pro- portion for T5 XXL models with MQA and GQA-8.
- Fig.6 (p.4) ![[assets/gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints-p04.png]]
  - Time per sample for GQA-XXL as a function of the number of GQA groups with input length 2048 and output length 512. Going from 1 (MQA) to 8 groups adds modest inference overhead, with increasing cost 

### #40 Qwen2.5-VL Technical Report

- Fig.1 (p.3) ![[assets/qwen2-5-vl-technical-report-p03.png]]
  - The Qwen2.5-VL framework demonstrates the integration of a vision encoder and a language model decoder to process multimodal inputs, including images and videos. The vision encoder is designed to hand

### #41 DeepSeek-V3 Technical Report

- Fig.5 (p.12) ![[assets/deepseek-v3-technical-report-p12.png]]
  - It employs a bidirectional pipeline scheduling, which feeds micro-batches from both ends of the pipeline simultaneously and a significant portion of communications can be fully overlapped. This overla
- Fig.6 (p.15) ![[assets/deepseek-v3-technical-report-p15.png]]
  - Firstly, in order to accelerate model training, the majority of core computation kernels, i.e., GEMM operations, are implemented in FP8 precision. These GEMM operations accept FP8 tensors as inputs an
- Fig.10 (p.48) ![[assets/deepseek-v3-technical-report-p48.png]]
  - 48

### #42 Step-3 is Large yet Affordable: Model-system Co-design for C

- Fig.1 (p.1) ![[assets/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-p01.png]]
  - The Pareto frontier of recent models regarding acti- vated parameters and decoding costs. The darker area is GQA models’ Pareto frontier. Note: Step-3 also has the highest attention effective rank [7]
- Fig.2 (p.6) ![[assets/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-p06.png]]
  - With all the results shown, we make the following observations:
- Fig.3 (p.6) ![[assets/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-p06.png]]
  - Second, the time spent on each layer will be largely unbal- anced – when running with long context, the full GQA layers consume much more time than the linear attention layers. This may not be a probl
- ⭐ Fig.4 (p.8) ![[assets/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-p08.png]]
  - Step-3 and Pangu Pro MoE have very different trends of decoding cost and training cost.
- ⭐ Fig.5 (p.8) ![[assets/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-p08.png]]
  - The compute and memory access of different atten- tion designs during decoding, including DSv3’s MLA, Qwen3
- Fig.6 (p.11) ![[assets/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-p11.png]]
  - Module disaggregation in AFD architecture. FFN can be deployed in TP-only, EP-only, or a hybrid TP+EP way, depending on hardware and model architecture. start to be concerned about other issues like e
- ⭐ Fig.7 (p.12) ![[assets/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-p12.png]]
  - Communication topology and the multi-stages pipeline of the AFD architecture.
- Fig.8 (p.13) ![[assets/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-p13.png]]
  - StepMesh communication workflow tailored for AFD.
- Fig.9 (p.13) ![[assets/step-3-is-large-yet-affordable-model-system-co-design-for-cost-effective-decoding-p13.png]]
  - StepMesh framework for multiple accelerators. AF-

### #43 SGLang: Efficient Execution of Structured Language Model Pro

- ⭐ Fig.1 (p.2) ![[assets/sglang-efficient-execution-of-structured-language-model-programs-p02.png]]
  - System architecture: An interpreter executes language primitives with optimized runtime.
- ⭐ Fig.2 (p.3) ![[assets/sglang-efficient-execution-of-structured-language-model-programs-p03.png]]
  - The implementation of a multi-dimensional essay judge in SGLang utilizes the branch-solve-merge prompting technique [40]. Primitives provided by SGLang are shown in red. 2
- ⭐ Fig.3 (p.5) ![[assets/sglang-efficient-execution-of-structured-language-model-programs-p05.png]]
  - Examples of RadixAttention operations with an LRU eviction policy, illustrated across nine time points. The figure demonstrates the dynamic evolution of the radix tree in response to various requests.
- ⭐ Fig.4 (p.6) ![[assets/sglang-efficient-execution-of-structured-language-model-programs-p06.png]]
  - The decoding process of normal and compressed FSMs (the underscore _ means a space). requests by matched prefix length and prioritize requests with longer matched prefixes instead of using a first-com
- ⭐ Fig.5 (p.7) ![[assets/sglang-efficient-execution-of-structured-language-model-programs-p07.png]]
  - Normalized throughput on Llama-7B models. Higher is better. pattern: s += context + "name:" + gen("name", stop="\n") + "job:" + gen("job", stop="\n"). Naively, the two gen primitives correspond to two
- ⭐ Fig.6 (p.8) ![[assets/sglang-efficient-execution-of-structured-language-model-programs-p08.png]]
  - Normalized latency on Llama-7B models. Lower is better. MMLU
- ⭐ Fig.7 (p.8) ![[assets/sglang-efficient-execution-of-structured-language-model-programs-p08.png]]
  - Normalized throughput on Mixtral-8x7B models with tensor parallelism. Higher is better. result from KV cache reuse, the exploitation of parallelism within a single program, and faster constrained deco
- ⭐ Fig.8 (p.9) ![[assets/sglang-efficient-execution-of-structured-language-model-programs-p09.png]]
  - (a)(b) Cache hit rate ablation study. (c) RadixAttention ablation study.
- ⭐ Fig.9 (p.14) ![[assets/sglang-efficient-execution-of-structured-language-model-programs-p14.png]]
  - KV cache sharing examples. Blue boxes represent shareable prompt parts, green boxes indicate non-shareable parts and yellow boxes mark non-shareable model outputs. Shareable elements include few-shot 
- ⭐ Fig.10 (p.17) ![[assets/sglang-efficient-execution-of-structured-language-model-programs-p17.png]]
  - Example of how regex is converted into FSM and how FSM guides the decoding process.
- ⭐ Fig.11 (p.18) ![[assets/sglang-efficient-execution-of-structured-language-model-programs-p18.png]]
  - Comparison of decoding using Compressed FSM versus normal FSM: The left subfigure depicts the decoding process per forward pass, while the right subfigure explains the origins of various result compon
- ⭐ Fig.12 (p.19) ![[assets/sglang-efficient-execution-of-structured-language-model-programs-p19.png]]
  - Normalized throughput on Llama-2-70B models with tensor parallelism. Higher is better. MMLU
- ⭐ Fig.13 (p.19) ![[assets/sglang-efficient-execution-of-structured-language-model-programs-p19.png]]
  - Achieved cache hit rate and optimal cache hit rate on various benchmarks. opportunities for more compilation optimizations, as we can rewrite the graph and perform more static planning. D.1
- ⭐ Fig.14 (p.20) ![[assets/sglang-efficient-execution-of-structured-language-model-programs-p20.png]]
  - An SGLang program and its corresponding dataflow graph.

### #44 Efficiently Serving Large Multimodal Models Using EPD Disagg

- Fig.1 (p.1) ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p01.png]]
  - Aggregated (top) vs. disaggregated (bottom) sys- tem architectures. In the aggregated setup, the encoder (E) and LLM share the same GPUs, leading to interference be- tween encode and prefill stages (e
- Fig.2 (p.2) ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p02.png]]
  - Impact of disaggregation on supported batch size and number of images per request for the MiniCPM- V 2.6 model. Removing the LLM from the GPU signifi- cantly increases capacity, enabling larger batche
- Fig.3 (p.3) ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p03.png]]
  - The inference pipeline of EPD Disaggregation. stages—EP-migration and PD-migration—handle the trans- fer of data from encoding to prefill and from prefill to de- code, respectively. We denote the inpu
- Fig.4 (p.4) ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p04.png]]
  - System architecture of the proposed EPD Disaggregated Inference. the data associated with the request. In the decoding stage, workers load the LLM weights for decoding tasks and use the KV cache.
- Fig.5 (p.6) ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p06.png]]
  - SLO attainment (↑) for end-to-end inference across multiple models and image counts per request. Subfigures (a), (b), and (c) correspond to MiniCPM-V 2.6, InternVL2-8B, and InternVL2-26B, respectively
- Fig.6 (p.7) ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p07.png]]
  - Distribution of TTFT (Y-axis) across varying numbers of images per request (X-axis) for (a) MiniCPM-V 2.6, (b)
- Fig.7 (p.7) ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p07.png]]
  - SLO attainment (↑) versus request rate on the
- Fig.8 (p.7) ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p07.png]]
  - As seen, EPD consistently outperforms vLLM and Dist-
- Fig.9 (p.9) ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p09.png]]
  - As shown, EPD is the only configuration that achieves the SLO requirements, while the other baselines fail to meet the SLOs entirely, even at low request rates.
- Fig.10 (p.13) ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p13.png]]
  - Left: Impact of varying the number of encoding workers in the EPD method. The notation xEyP denotes a configuration with x encoder and y prefill workers. The DistServe method uses a fixed 7P configura
- Fig.11 (p.13) ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p13.png]]
  - SLO attainment (↑) for end-to-end inference across multiple models and image counts per request. Subfigures (a), (b), and (c) correspond to MiniCPM-V 2.6, InternVL2-8B, and InternVL2-26B, respectively
- Fig.12 (p.16) ![[assets/efficiently-serving-large-multimodal-models-using-epd-disaggregation-p16.png]]
  - Breakdown of latency for encode and prefill stages using the InternVL2-8B model across varying numbers of images per request. Subfigures (a) and (b) show results on GPU and NPU, respectively. Light gr

### #45 Mooncake: A KVCache-centric Disaggregated Architecture for L

- ⭐ Fig.1 (p.2) ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p02.png]]
  - Mooncake Architecture. remote location will prolong the TTFT, and a large batch size will lead to a larger TBT. Thus, the utilization of both these throughput-oriented optimizations may lead to violat
- ⭐ Fig.2 (p.4) ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p04.png]]
  - Normalized throughput and latency of prefill and decoding stages with different sequence lengths or batch sizes for the dummy LLaMA2-70B model. the computational complexity of attention networks scale
- Fig.3 (p.5) ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p05.png]]
  - The KVCache pool in CPU memory. Each block is attached with a hash value determined by both its own hash and its prefix for deduplication.
- Fig.4 (p.6) ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p06.png]]
  - Workflow of inference instances. ( ) For prefill instances, the load and store operations of the KVCache layer are performed layer-by-layer and in parallel with the prefill computation to mitigate tr
- Fig.5 (p.6) ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p06.png]]
  - Input and output length distributions in the request trace. 4
- Fig.6 (p.7) ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p07.png]]
  - CDF (Cumulative Distribution
- Fig.7 (p.9) ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p09.png]]
  - Latency of storing KVCache of different request lengths (Layer-wise latency refers to the difference in latency between Layer-wise Prefill and Prefill without storing KVCache).
- Fig.8 (p.11) ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p11.png]]
  - The prefill scheduling experiment in the Mooncake cluster.
- Fig.9 (p.13) ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p13.png]]
  - The load of prefill and decoding instances over 20 minutes, before using the prediction- based early rejection.
- Fig.10 (p.14) ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p14.png]]
  - Instance load when applying Early Rejection and Early Rejection Based on Prediction. conditions where resources are scarce and accurate predictions are necessary, making request-level predictions part
- Fig.11 (p.16) ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p16.png]]
  - End-to-end experiments of Mooncake and vLLM on the ArXiv Summarization and L-Eval datasets instances. In real-world clusters, the demand for prefill and decoding instances generally remains stable ove
- Fig.12 (p.16) ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p16.png]]
  - End-to-end experiments of Mooncake and vLLM on simulated data.
- Fig.13 (p.17) ![[assets/mooncake-a-kvcache-centric-disaggregated-architecture-for-llm-serving-p17.png]]
  - Request TTFT and TBT distributions of Mooncake and vLLM under real workloads

### #46 MegaScale: Scaling Large Language Model Training to More Tha

- Fig.1 (p.2) ![[assets/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-p02.png]]
  - Data parallel training with ZeRO2. dependencies that contribute to stability issues. We develop a robust training framework to automate fault localization and recovery. We design heartbeat messages en
- ⭐ Fig.2 (p.3) ![[assets/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-p03.png]]
  - Interleaved 1F1B pipeline. update the model. Instead of duplicating model states (like the optimizer states, gradients, and parameters), Zero Redun- dancy Optimizer (ZeRO) [11] shards these states acr
- Fig.3 (p.4) ![[assets/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-p04.png]]
  - Overlapping communication in tensor parallelism (TP) and sequence parallelism (SP) with parallel transformer block (PTB). with a large receptive field created by stacking layers of such windowed atten
- Fig.4 (p.4) ![[assets/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-p04.png]]
  - The cool-down phase can be viewed as the inverse of the warm-up phase, allowing for the inverse application of the same technique. As for the steady phase, both the forward and backward computation ar
- Fig.5 (p.6) ![[assets/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-p06.png]]
  - Robust training workflow. interval and help recover the transmission more quickly when the link flapping period is short. 4
- Fig.6 (p.8) ![[assets/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-p08.png]]
  - Inconsistent MFU observed in large-scale training. Differ- ent colors denote distinct executions of the same training job. mitigates the bandwidth constraints of HDFS, leading to a substantial reducti
- Fig.7 (p.8) ![[assets/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-p08.png]]
  - We gather latency data of the computation phase (forward and backward) across devices and average the latency across steps. The aggregated data is visualized host 0 0 1 2 3 host 3 12 13 14 15 host 6 2
- Fig.8 (p.9) ![[assets/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-p09.png]]
  - The trace shows events collected in a pipeline group on a unified timeline. Dependencies become visible when an event is selected.
- Fig.9 (p.10) ![[assets/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-p10.png]]
  - Weak-scaling training performance of Megatron-LM and
- Fig.10 (p.11) ![[assets/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-p11.png]]
  - The training loss curves in microbenchmark experiments.
- Fig.11 (p.11) ![[assets/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-p11.png]]
  - The normalized training loss curve of a real production run on more than 10,000 GPUs for several weeks. This run trains a model with hundreds of billions of parameters on multi-trillion tokens. Differ
- Fig.12 (p.12) ![[assets/megascale-scaling-large-language-model-training-to-more-than-10000-gpus-p12.png]]
  - The MFU becomes stable after addressing the stragglers and problematic code segments. Different colors represent different training trials with the same setup. executing diagnostic tests is less than 

### #47 ZeRO: Memory Optimizations Toward Training Trillion Paramete

- Fig.1 (p.3) ![[assets/zero-memory-optimizations-toward-training-trillion-parameter-models-p03.png]]
  - Comparing the per-device memory consumption of model states, with three stages of
- Fig.2 (p.4) ![[assets/zero-memory-optimizations-toward-training-trillion-parameter-models-p04.png]]
  - ZeRO training throughput and speedup w.r.t SOTA baseline for varying model sizes.
- Fig.3 (p.5) ![[assets/zero-memory-optimizations-toward-training-trillion-parameter-models-p05.png]]
  - Superlinear scalability and per GPU training throughput of a 60B parameter model using ZeRO-100B. 38 TFlops per GPU, and aggregate performance over 15 Petaﬂops. This is more than 10x improvement in tr
- Fig.4 (p.16) ![[assets/zero-memory-optimizations-toward-training-trillion-parameter-models-p16.png]]
  - Max model throughput with ZeRO-DP.
- Fig.5 (p.16) ![[assets/zero-memory-optimizations-toward-training-trillion-parameter-models-p16.png]]
  - SOTA Turing-NLG enabled by ZeRO.
- Fig.6 (p.16) ![[assets/zero-memory-optimizations-toward-training-trillion-parameter-models-p16.png]]
  - Max model size .
- Fig.7 (p.16) ![[assets/zero-memory-optimizations-toward-training-trillion-parameter-models-p16.png]]
  - Max cache allo- cated.
- Fig.8 (p.16) ![[assets/zero-memory-optimizations-toward-training-trillion-parameter-models-p16.png]]
  - Throughput per GPU. a Bert-Large model for a data sample. Even if we assume the same sequence length and the total number of samples required to train the model, training a 1T model would take 140 day

### #48 Efficient Large-Scale Language Model Training on GPU Cluster

- Fig.1 (p.1) ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p01.png]]
  - Trend of sizes of state-of-the-art Natural Language Pro- cessing (NLP) models with time. The number of floating-point op- erations to train these models is increasing at an exponential rate.
- Fig.2 (p.3) ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p03.png]]
  - Combination of tensor and pipeline model parallelism (MP) used in this work for transformer-based models.
- Fig.3 (p.3) ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p03.png]]
  - GPipe pipeline schedule with forward passes (blue) for all microbatches (represented by numbers) followed by backward passes (green). The gray area represents the pipeline bubble. For simplicity, we a
- Fig.4 (p.3) ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p03.png]]
  - Default and interleaved 1F1B pipeline schedules. The top figure shows the default non-interleaved 1F1B schedule. The bottom figure shows the interleaved 1F1B schedule, where each device is assigned mu
- Fig.5 (p.5) ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p05.png]]
  - Blocks of transformer model partitioned with tensor model parallelism (figures borrowed from Megatron [40]). 𝑓and 𝑔 are conjugate. 𝑓is the identity operator in the forward pass and all- reduce in the 
- Fig.6 (p.5) ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p05.png]]
  - Fraction of time spent idling due to pipeline flush (pipeline bubble size) versus data-parallel size (𝑑), for different numbers of GPUs (𝑛) and ratio of batch size to microbatch size (𝑏′ = 𝐵/𝑏).
- Fig.7 (p.6) ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p06.png]]
  - Per-GPU throughput versus microbatch size for a GPT model with a billion parameters (128 attention heads, hidden size of 4096, 4 transformer layers).
- Fig.8 (p.6) ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p06.png]]
  - Behavior of normalized estimated throughput (time com- puted as 𝑡= (𝑏′/𝑏+ 𝑝−1) ·  𝑡𝑓(𝑏) + 𝑡𝑏(𝑏)) with respect to the mi- crobatch size 𝑏for the same GPT model from Figure 7.
- Fig.9 (p.7) ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p07.png]]
  - Scatter/gather communication optimization. Light blue blocks are layers in the first pipeline stage, and dark blue blocks are layers in the second pipeline stage. Without the scatter/gather optimizati
- Fig.10 (p.8) ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p08.png]]
  - Throughput per GPU of PTD-P and ZeRO-3 for two differ- ent GPT models (the 175B GPT-3 model is shown with dotted lines, and the 530B model is shown with solid lines). Global batch sizes are fixed and 
- Fig.11 (p.9) ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p09.png]]
  - Throughput per GPU of pipeline parallelism using two different batch sizes in a weak-scaling experiment setup (model size increases with the pipeline-parallel size). 12 24 36 48 60
- Fig.12 (p.9) ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p09.png]]
  - Throughput per GPU of interleaved and non-interleaved schedules for a GPT model (175 billion parameters) on 96 GPUs. and a microbatch size of 1. As we increase the number of pipeline stages, we also i
- Fig.13 (p.9) ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p09.png]]
  - Throughput per GPU of various parallel configurations that combine pipeline and tensor model parallelism using a GPT model with 162.2 billion parameters and 64 A100 GPUs.
- Fig.14 (p.10) ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p10.png]]
  - Throughput per GPU of various parallel configurations that combine data and pipeline model parallelism using a GPT model with 5.9 billion parameters, three different batch sizes, mi- crobatch size of 
- Fig.15 (p.10) ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p10.png]]
  - Throughput per GPU of various parallel configurations that combine data and tensor model parallelism using a GPT model with 5.9 billion parameters, three different batch sizes, microbatch size of 1, a
- Fig.16 (p.10) ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p10.png]]
  - Throughput per GPU of a (𝑡, 𝑝) = (8, 8) parallel configura- tion for different microbatch sizes on a GPT model with 91 billion parameters, for two different batch sizes using 64 A100 GPUs. importance 
- Fig.17 (p.11) ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p11.png]]
  - Throughput (in sequences per second) with and without activation recomputation for a GPT model with 145 billion param- eters using 128 A100 GPUs ((𝑡, 𝑝) = (8, 16)). 12 24 36 48 60
- Fig.18 (p.11) ![[assets/efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-p11.png]]
  - Throughput per GPU with and without the scatter/gather optimization for a GPT model with 175 billion parameters using 96 A100 GPUs and the interleaved schedule.

### #49 Megatron-LM: Training Multi-Billion Parameter Language Model

- Fig.1 (p.2) ![[assets/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-p02.png]]
  - Model (blue) and model+data (green) parallel FLOPS as a function of number of GPUs. Model parallel (blue): up to 8-way model parallel weak scaling with approximately 1 billion parameters per GPU (e.g.
- Fig.2 (p.3) ![[assets/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-p03.png]]
  - Transformer Architecture. Purple blocks correspond to fully connected layers. Each blue block represents a single trans- former layer that is replicated N times. and compute efﬁciency. The original tr
- Fig.3 (p.4) ![[assets/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-p04.png]]
  - Blocks of Transformer with Model Parallelism. f and g are conjugate. f is an identity operator in the forward pass and all reduce in the backward pass while g is an all reduce in the forward pass and 
- Fig.4 (p.5) ![[assets/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-p05.png]]
  - Communication operations in a transformer layer. There are 4 total communication operations in the forward and backward pass of a single model parallel transformer layer. contains a portion of the emb
- Fig.5 (p.6) ![[assets/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-p06.png]]
  - Model and model + data parallel weak scaling efﬁciency as a function of the number of GPUs. done by scaling the batch-size, however, this approach does not address training large models that do not ﬁt
- Fig.6 (p.7) ![[assets/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-p07.png]]
  - Validation set perplexity. All language models are trained for 300k iterations. Larger language models converge notice- ably faster and converge to lower validation perplexities than their smaller cou
- Fig.7 (p.8) ![[assets/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-p08.png]]
  - Training loss for BERT model using the original architec- ture (a) and the rearranged architecture (b). Left ﬁgure shows the training loss for 336M and 752M BERT model. While the original architecture
- Fig.8 (p.12) ![[assets/megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism-p12.png]]
  - Grouping of GPUs for hybrid model and data parallelism with 8-way model parallel and 64-way data parallel. C. Text Samples

### #52 Efficient Memory Management for Large Language Model Serving

- ⭐ Fig.1 (p.1) ![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p01.png]]
  - Left: Memory layout when serving an LLM with 13B parameters on NVIDIA A100. The parameters (gray) persist in GPU memory throughout serving. The memory for the KV cache (red) is (de)allocated per servi
- Fig.2 (p.2) ![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p02.png]]
  - Average percentage of memory wastes in different LLM serving systems during the experiment in §6.2. percentage of memory is used for other data, including ac- tivations – the ephemeral tensors created
- Fig.3 (p.4) ![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p04.png]]
  - KV cache memory management in existing systems. Three types of memory wastes – reserved, internal fragmentation, and external fragmentation – exist that prevent other requests from fitting into the me
- Fig.4 (p.5) ![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p05.png]]
  - vLLM system overview.
- Fig.5 (p.5) ![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p05.png]]
  - Illustration of the PagedAttention algorithm, where the attention key and values vectors are stored as non-contiguous blocks in the memory. block size (𝐵). Denote the key block 𝐾𝑗= (𝑘(𝑗−1)𝐵+1, . . . ,
- Fig.6 (p.6) ![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p06.png]]
  - Block table translation in vLLM. divides it into physical KV blocks (this is also done on CPU RAM for swapping; see §4.5). The KV block manager also maintains block tables—the mapping between logical 
- Fig.7 (p.6) ![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p06.png]]
  - Storing the KV cache of two requests at the same time in vLLM. requests and the latest tokens for generation phase requests) as one sequence and feeds it into the LLM. During LLM’s computation, vLLM u
- Fig.8 (p.7) ![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p07.png]]
  - Parallel sampling example. generates a single sequence. In the remainder of this paper, we assume the more general case in which a request gener- ates multiple sequences. In parallel sampling, one req
- Fig.9 (p.7) ![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p07.png]]
  - Beam search example. sample space. The algorithm relies on the beam width pa- rameter 𝑘, which determines the number of top candidates retained at every step. During decoding, beam search ex- pands ea
- Fig.10 (p.8) ![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p08.png]]
  - Shared prompt example for machine translation.
- Fig.11 (p.9) ![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p09.png]]
  - Input and output length distributions of the (a)
- Fig.12 (p.10) ![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p10.png]]
  - Single sequence generation with OPT models on the ShareGPT and Alpaca dataset
- Fig.13 (p.10) ![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p10.png]]
  - Average number of batched requests when serv- ing OPT-13B for the ShareGPT (2 reqs/s) and Alpaca (30 reqs/s) traces.
- Fig.14 (p.11) ![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p11.png]]
  - Parallel generation and beam search with OPT-13B on the Alpaca dataset.
- Fig.15 (p.11) ![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p11.png]]
  - Average amount of memory saving from sharing KV blocks, when serving OPT-13B for the Alpaca trace.
- Fig.16 (p.12) ![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p12.png]]
  - Translation workload where the input prompts share a common prefix. The prefix includes (a) 1 example with 80 tokens or (b) 5 examples with 341 tokens.
- Fig.17 (p.12) ![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p12.png]]
  - Performance on chatbot workload.
- Fig.18 (p.12) ![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p12.png]]
  - Ablation experiments. handle the long prompts, as PagedAttention resolves the problem of memory fragmentation and reservation. 7
- Fig.19 (p.13) ![[assets/efficient-memory-management-for-large-language-model-serving-with-pagedattention-p13.png]]
  - (a) Overhead of recomputation and swapping for different block sizes. (b) Performance when serving OPT-13B with the ShareGPT traces at the same request rate.

### #53 DeFT: Decoding with Flash Tree-attention for Efficient Tree-

- ⭐ Fig.1 (p.1) ![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p01.png]]
  - Usually, these applications produce substantially more tokens than traditional ones, to provide large space for tree search (Graves, 2012; Lu et al., 2022; Liu et al., 2023) or selection, as shown in 
- ⭐ Fig.2 (p.5) ![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p05.png]]
  - Overview of DEFT. Input Metadata is prepared in the system elaborated in Appendix A.1. In QKV
- ⭐ Fig.3 (p.6) ![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p06.png]]
  - Comparison of QKV partitioning strategies during the QKV Preparation Phase between DEFT-
- Fig.4 (p.9) ![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p09.png]]
  - Latency breakdown for specula- tive decoding with a token tree of 32 queries, whose tree topology is from Medusa (Cai et al., 2024). U means unpaged memory.
- Fig.5 (p.15) ![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p15.png]]
  - Illustration of DEFT. (Left) System overview. (Right) The data flow of DEFT-Node (DEFT-Flatten is similar except for QKV partitioning) using a decoding tree example.
- Fig.6 (p.16) ![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p16.png]]
  - Discussion of tree-based decoding with tree queries (Miao et al., 2023) and tree KV.
- Fig.7 (p.17) ![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p17.png]]
  - Analysis for two case studies of tree-based decoding. (Left) Multi-step reasoning. (Right) Speculative decoding. Blue boxes mean shareable past KV cache in storage and memory access during the tree at
- Fig.8 (p.19) ![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p19.png]]
  - Operations of Tree Attention-Medusa (Cai et al., 2024). No Kernel Fusion or Tiling strategy is applied, which introduces significant IO of partial results like QK⊤, DCM, and Softmax between GPU global
- Fig.9 (p.19) ![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p19.png]]
  - Overview of two stages in DEFT Attention Kernel (DEFT-Node for example, and DEFT-Flatten is similar). Stage 1–calculate partial attentions. Based on the QKV grouping results after KV-Guided Grouping
- Fig.10 (p.20) ![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p20.png]]
  - Detailed attention operations of DEFT kernel (DEFT-Node for example, and DEFT-Flatten is similar). Based on the same decoding tree in Figure 3.
- Fig.11 (p.21) ![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p21.png]]
  - When the number of leaf nodes/queries ln is sufficiently large, the IO cost of partial results might become comparable to that of the KV cache. For instance, in the Llama models (Touvron et al., 2023a
- Fig.12 (p.23) ![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p23.png]]
  - The detailed procedure of reconstructing tree templates for multi-step reasoning. (Left)
- Fig.13 (p.25) ![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p25.png]]
  - Comparison of split strategies DEFT-Node and DEFT-Flatten in sorting task. Speedup ratio refers to the ratio between the per iteration latency of DEFT-Node and DEFT-Flatten. Tree Node Len std represen
- Fig.14 (p.26) ![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p26.png]]
  - Per iteration latency for few-shot prompting tasks with different tree width. e2e means decoding latency(optimal end-to-end latency), while Attn means only the attention overhead.
- Fig.15 (p.26) ![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p26.png]]
  - The chunk size selection is a trade-off between IO redundancy and threadblock scheduling: a larger chunk size means less redundancy of Query IO but may cause potential idle SMs of GPUs due to fewer th
- Fig.16 (p.27) ![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p27.png]]
  - Time per output token(TPOT) of DEFT with different prompt lengths in speculative decoding. 2500 5000 7500 10000 12500 15000 17500 20000
- Fig.17 (p.27) ![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p27.png]]
  - Decoding latency of DEFT with different prompt lengths in speculative decoding.
- Fig.18 (p.28) ![[assets/deft-decoding-with-flash-tree-attention-for-efficient-tree-structured-llm-inference-p28.png]]
  - Attention latency of DEFT with different prompt lengths in speculative decoding.

### #54 NanoFlow: Towards Optimal Large Language Model Serving Throu

- ⭐ Fig.1 (p.3) ![[assets/nanoflow-towards-optimal-large-language-model-serving-throughput-p03.png]]
  - Transformer architecture. The operations in the yellow boxes have large batch sizes and share model weight parameters across requests; hence, they are compute-bound. Operations in green boxes require 
- Fig.2 (p.5) ![[assets/nanoflow-towards-optimal-large-language-model-serving-throughput-p05.png]]
  - Comparison of network time and compute time. The closer to yellow, the more compute-bound the workload is, whereas the closer to blue indicates the workload is more network-bound. LMSYS-Chat Splitwise
- Fig.3 (p.5) ![[assets/nanoflow-towards-optimal-large-language-model-serving-throughput-p05.png]]
  - Comparison of compute time and memory time.
- Fig.4 (p.8) ![[assets/nanoflow-towards-optimal-large-language-model-serving-throughput-p08.png]]
  - Execution pipeline of existing systems. The green, yellow, and blue operations correspond to memory-, compute-, and network-bound operations. Operations in the previous and next layer are denoted by d
- Fig.5 (p.8) ![[assets/nanoflow-towards-optimal-large-language-model-serving-throughput-p08.png]]
  - Interference characteristics between GEMM and GEMV kernels. The points on the x-axis correspond unique GEMM-GEMV implementation pairs. The y-axis denotes the GEMM and GEMV kernels’ normalized performa
- Fig.6 (p.11) ![[assets/nanoflow-towards-optimal-large-language-model-serving-throughput-p11.png]]
  - Execution pipeline of LLaMA-2 70B, automatically generated by NanoFlow. The solid background and shaded background represents input batch 0-768 and 768-2048, respectively. R stands for resource utiliz
- Fig.7 (p.11) ![[assets/nanoflow-towards-optimal-large-language-model-serving-throughput-p11.png]]
  - Offline throughput comparison. NanoFlow outper- forms all baselines for all the workload settings. TP stands for the number of GPUs used with tensor parallelism. • How do the various techniques propos
- Fig.8 (p.13) ![[assets/nanoflow-towards-optimal-large-language-model-serving-throughput-p13.png]]
  - Latency comparison. The x-axis shows the number of incoming requests per second and the y-axis shows the normalized latency. NanoFlow handles higher request within 200ms SLO constraints.
- Fig.9 (p.13) ![[assets/nanoflow-towards-optimal-large-language-model-serving-throughput-p13.png]]
  - Ablation study results for NanoFlow. Nano-batching and overlapping improves NanoFlow’s performance.
- Fig.10 (p.13) ![[assets/nanoflow-towards-optimal-large-language-model-serving-throughput-p13.png]]
  - While the non-overlapping baseline sequentially executes operations, which mostly uses only one resource at a given time, the NanoFlow instance can concurrently utilize multiple resources and achieves
- Fig.11 (p.13) ![[assets/nanoflow-towards-optimal-large-language-model-serving-throughput-p13.png]]
  - We find that

### #55 Gated Delta Networks: Improving Mamba2 with Delta Rule

- ⭐ Fig.1 (p.7) ![[assets/gated-delta-networks-improving-mamba2-with-delta-rule-p07.png]]
  - Visualization of the (hybrid) architecture and block design of Gated DeltaNet models.
- Fig.2 (p.8) ![[assets/gated-delta-networks-improving-mamba2-with-delta-rule-p08.png]]
  - Length extrapolation on six long benchmarks.
- Fig.3 (p.9) ![[assets/gated-delta-networks-improving-mamba2-with-delta-rule-p09.png]]
  - Training throughput comparison of 1.3B models on a single H100 GPU. standalone mixers: Samba outperforms Mamba, while Gated DeltaNet-H1 and -H2 outperform

### #56 Parallel Scan on Ascend AI Accelerators

- ⭐ Fig.3 (p.3) ![[assets/parallel-scan-on-ascend-ai-accelerators-p03.png]]
  - 1 shows the Ascend architecture where the
- Fig.4 (p.4) ![[assets/parallel-scan-on-ascend-ai-accelerators-p04.png]]
  - 1: Data path from an input tile xℓto an output tile yℓof the ScanU (Algorithm 4.1).
- Fig.5 (p.7) ![[assets/parallel-scan-on-ascend-ai-accelerators-p07.png]]
  - 1: A diagram of well-known parallel scan applica- tions considered here along with their dependencies.
- Fig.6 (p.8) ![[assets/parallel-scan-on-ascend-ai-accelerators-p08.png]]
  - 1:

### #57 Kimi K3: Open Frontier Intelligence

- Fig.1 (p.1) ![[assets/kimi-k3-open-frontier-intelligence-p01.png]]
  - Kimi K3 main results. 1https://huggingface.co/moonshotai/Kimi-K3[cs.CL] 7 Aug 2026
- ⭐ Fig.2 (p.3) ![[assets/kimi-k3-open-frontier-intelligence-p03.png]]
  - The Kimi K3 architecture, organized around token, channel, and layer mixing, with a native vision pathway at the input.
- ⭐ Fig.3 (p.5) ![[assets/kimi-k3-open-frontier-intelligence-p05.png]]
  - Lower-bounded decay and its effect on chunkwise KDA computation. (a) Kimi Linear uses an unbounded negative-Softplus mapping, whereas Kimi K3 bounds the log-decay with a scaled sigmoid; the curves sho
- Fig.4 (p.7) ![[assets/kimi-k3-open-frontier-intelligence-p07.png]]
  - Gate and up branches of GLU, SwiGLU, and SiTU-GLU, together with their scalar responses, where σ denotes the sigmoid function. Both branches receive the scalar input x, and all curves share the domain
- ⭐ Fig.5 (p.8) ![[assets/kimi-k3-open-frontier-intelligence-p08.png]]
  - Illustration of Quantile Balancing with m = 8 tokens, n = 4 routed experts, and k = 1 selected expert per token. (a)
- Fig.6 (p.9) ![[assets/kimi-k3-open-frontier-intelligence-p09.png]]
  - Vision-tower gradient norms in our pre-training ablations. Compared with the SigLIP-initialized MoonViT-3D, the from-scratch MoonViT-V2 maintains lower gradient norms with fewer spikes, indicating mor
- Fig.7 (p.11) ![[assets/kimi-k3-open-frontier-intelligence-p11.png]]
  - Fitted scaling-law curves for Kimi K2 and Kimi K3. Kimi K3 achieves 2.5× gain in scaling efficiency over Kimi K2.
- Fig.8 (p.13) ![[assets/kimi-k3-open-frontier-intelligence-p13.png]]
  - Scores and the average assistant steps across a variety of public and in-house evaluations during RL. By scaling RL FLOPs, tool-call steps scale up consistently, accompanied by a comprehensive improve
- Fig.9 (p.15) ![[assets/kimi-k3-open-frontier-intelligence-p15.png]]
  - Overview of knowledge-graph-guided task synthesis. The hierarchically organized knowledge graph represents concepts at multiple levels, ranging from broad domains to fine-grained concepts. Related nod
- Fig.10 (p.17) ![[assets/kimi-k3-open-frontier-intelligence-p17.png]]
  - Completion curves on Camera Repair Management System, a black-box system replication task in which the agent reconstructs a hidden 3D-camera repair system as a web application through oracle queries. 
- Fig.11 (p.19) ![[assets/kimi-k3-open-frontier-intelligence-p19.png]]
  - Computation, communication and offloading overlapped in different PP phases.
- Fig.12 (p.23) ![[assets/kimi-k3-open-frontier-intelligence-p23.png]]
  - Fine-grained prefix caching within a physical cache block. A 6144-token physical block contains twelve 512-token hash blocks, with cached MLA blocks shown in blue and empty blocks in light gray. The m
- Fig.13 (p.32) ![[assets/kimi-k3-open-frontier-intelligence-p32.png]]
  - Score vs. per-task inference cost on Kimi Code Bench 2.0, BrowseComp, GDPval-AA v2, and AA-Briefcase. Kimi K3 is marked with a star.
- Fig.14 (p.33) ![[assets/kimi-k3-open-frontier-intelligence-p33.png]]
  - Case study: GPU kernel optimization on AttnRes. 7
- Fig.15 (p.34) ![[assets/kimi-k3-open-frontier-intelligence-p34.png]]
  - Case study: GPU compiler development with MiniTriton. (a) CUDA-core and (b) tensor-core rooflines of MiniTriton kernels on an NVIDIA L20 (sm_89) against torch eager, torch.compile, Triton, and cuBLAS 
- Fig.16 (p.46) ![[assets/kimi-k3-open-frontier-intelligence-p46.png]]
  - Structure of the Kimi K3 chat template. (a) Context layout: global option messages precede the input messages, while one-shot option messages follow them, so that per-request options leave the history

### #58 Prefill-as-a-Service: KVCache of Next-Generation Models Coul

- Fig.1 (p.2) ![[assets/prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter-p02.png]]
  - Comparison of two deployment paradigms for PD-disaggregated LLM serving.
- Fig.2 (p.4) ![[assets/prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter-p04.png]]
  - KV throughput of MiniMax-M2.5 on an 8×H200 instance at various input lengths.
- ⭐ Fig.3 (p.6) ![[assets/prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter-p06.png]]
  - Deployment topology of the PrfaaS-PD architecture.
- Fig.4 (p.7) ![[assets/prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter-p07.png]]
  - Hybrid prefix cache pool. Linear states and full-attention KVCache are managed by separate groups backed by a unified block pool. Blocks are categorized as prefix-cache (intra-cluster only, block-alig
- Fig.5 (p.11) ![[assets/prefill-as-a-service-kvcache-of-next-generation-models-could-go-cross-datacenter-p11.png]]
  - Illustration of the grid search process for the two optimization variables. (a) fixes t at the optimum and searches over the prefill/decode instance split within the local PD cluster. (b) fixes

### #59 LongSpec: Long-Context Lossless Speculative Decoding with Ef

- Fig.1 (p.1) ![[assets/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-p01.png]]
  - The SoTA SD method, EAGLE, has a training context length of 2048, which is significantly shorter than the context lengths of modern LLMs. 2023), and their ability to handle extensive con- texts is bec
- ⭐ Fig.2 (p.4) ![[assets/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-p04.png]]
  - Illustration of the memory-efficient draft model, the Anchor-Offset Indices, and the Hybrid Tree Attention. (a) We use a sliding window self-attention layer to capture the local context information an
- Fig.3 (p.7) ![[assets/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-p07.png]]
  - Decoding speed (tokens/s) across different models and settings. All results are computed at T = 1. The letters G, Q, M, L, and R on the horizontal axis represent the datasets GovReport, QMSum, Multi-N
- Fig.4 (p.8) ![[assets/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-p08.png]]
  - Training loss curves on long-context data.
- Fig.5 (p.8) ![[assets/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-p08.png]]
  - Latency breakdown for a single speculative decoding loop comparing the EAGLE implementation and the proposed Hybrid Tree Attention. Significant latency reduction is observed in the target model’s at- 
- Fig.6 (p.9) ![[assets/longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification-p09.png]]
  - Throughput comparison of Vanilla, MagicDec, and LONGSPEC. not suitable for such long-output scenarios because the initial inference stage of the long reasoning task is not the same as the traditional 

### #60 SpecExtend: A Drop-in Enhancement for Speculative Decoding o

- Fig.1 (p.1) ![[assets/specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences-p01.png]]
  - Performance and memory usage of speculative decoding with Llama-3.1-8B-Instruct and EAGLE-3 across varying input lengths. Performance significantly declines well before the shift of memory bottleneck.
- ⭐ Fig.2 (p.2) ![[assets/specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences-p02.png]]
  - Overview of SpecExtend. FlashAttention accelerates the prefill phases of both target and draft models, and Hybrid Tree Attention accelerates the verification phase. We use the target model’s attention
- Fig.3 (p.4) ![[assets/specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences-p04.png]]
  - Left figure shows acceptance rates for hard and easy tokens, where CMR enables more accurate drafting in both cases compared to StreamingLLM.
- Fig.4 (p.5) ![[assets/specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences-p05.png]]
  - (a) Average accepted length of Vicuna-7B/68M across different draft model cache settings. (b) End-to-end latency breakdown of speculative decoding on 16K-token inputs. retrieved context to identify an
- Fig.5 (p.6) ![[assets/specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences-p06.png]]
  - Speedup comparison of standard speculative decoding and SpecExtend across varying input lengths on
- Fig.6 (p.7) ![[assets/specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences-p07.png]]
  - Decoding speed (left) and average ac- cepted length (right) of the DeepSeek-R1-Distill-Llama- 8B/EAGLE-3 setup on the long reasoning task with the AIME-24 benchmark.

### #61 A Survey of Large Language Models

- Fig.1 (p.3) ![[assets/a-survey-of-large-language-models-p03.png]]
  - As discussed before, language model is not a new tech- nical concept specially for LLMs, but has evolved with the advance of artificial intelligence over the decades. Early lan- guage models mainly ai
- Fig.3 (p.99) ![[assets/a-survey-of-large-language-models-p99.png]]
  - – Section 4: add LLM-based data filtering and selec- tion methods in Section 4.1.2; update Section 4.2.1, “Emergent Architectures” to include more discus- sions about SSM-based architectures; add Tabl
- Fig.4 (p.7) ![[assets/a-survey-of-large-language-models-p07.png]]
  - The basic principle underlying GPT models is to compress the world knowledge into the decoder-only
- Fig.5 (p.12) ![[assets/a-survey-of-large-language-models-p12.png]]
  - Public API of LLMs. Instead of directly using the model copies, APIs provide a more convenient way for common users to use LLMs, without the need of running the model locally. As a representative inte
- Fig.7 (p.18) ![[assets/a-survey-of-large-language-models-p18.png]]
  - Filtering and Selection. To remove low-quality data from the collected corpus, existing work generally adopts two ap- proaches, namely classifier-based and heuristic-based. The former approach trains 
- Fig.8 (p.20) ![[assets/a-survey-of-large-language-models-p20.png]]
  - Data Mixture. Since each kind of data source is closely related to the development of certain capacities for LLMs (referring to the discussions in Section 4.1), it is important to set a suitable distr
- Fig.9 (p.22) ![[assets/a-survey-of-large-language-models-p22.png]]
  - Encoder-decoder Architecture. The vanilla Transformer model is built on the encoder-decoder architecture [22], which consists of two stacks of Transformer blocks as the encoder and decoder, respective
- Fig.13 (p.43) ![[assets/a-survey-of-large-language-models-p43.png]]
  - Adapter Tuning. Adapter tuning incorporates small neural network modules (called adapter) into the Transformer mod- els [406]. To implement the adapter module, a bottleneck architecture has been propo
- Fig.16 (p.54) ![[assets/a-survey-of-large-language-models-p54.png]]
  - In this paradigm, there are typically three components: task planner, plan executor, and environment36. Specifically, task planner, which is played by LLMs, aims to generate the whole plan to solve a 
- Fig.17 (p.59) ![[assets/a-survey-of-large-language-models-p59.png]]
  - Hallucination widely occurs in existing LLMs, even the most superior LLMs such as GPT-4 [46]. Furthermore, existing work shows that LLMs encounter difficulties in recognizing the hallucinated con- ten

### #62 KV Cache Optimization Strategies for Scalable and Efficient 

- Fig.1 (p.2) ![[assets/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-p02.png]]
  - Autoregressive generation, at each step the new token (orange) attends to all prior tokens (cyan). Without caching, keys and values for every past token would be recomputed from scratch at each step. 
- Fig.2 (p.3) ![[assets/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-p03.png]]
  - Data-flow of the KV cache within a single transformer layer. Input token xt fans into three projections; Kt and Vt are appended to their respective caches (teal); Qt attends over the full caches to pr
- Fig.3 (p.3) ![[assets/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-p03.png]]
  - KV cache memory as a function of context length for three LLaMA-2 model variants under fp16 precision.
- Fig.4 (p.4) ![[assets/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-p04.png]]
  - Causal self-attention weight matrix for “The apple tastes sweet.” visualised with the Viridis colormap (dark purple = low, yellow = high). Gray cells are causally masked future tokens. Each row sums t
- Fig.5 (p.5) ![[assets/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-p05.png]]
  - Taxonomy of KV cache optimization techniques surveyed in this paper, organized into five major categories.
- Fig.6 (p.6) ![[assets/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-p06.png]]
  - Upper plots illustrate symbolic plots of an attention map deploying different KV cache policies in LLM generation. Lower right: contrasts their accuracy-memory trade-off. Left: the overview of H2O fra
- Fig.7 (p.7) ![[assets/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-p07.png]]
  - The graph shows the simplified workflow of SnapKV, where the orange area represents the cluster of features per head selected by SnapKV. These features are then used to form new Key-Value pairs concat
- Fig.8 (p.9) ![[assets/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-p09.png]]
  - Definition of per-token and per-channel quantization. X ∈Rlprompt×d is the key/value cache, where lprompt is the number of tokens and d is the number of channels. zX is the zero-point, and sX is the s
- Fig.9 (p.9) ![[assets/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-p09.png]]
  - Palu’s low-rank projection method for KV-cache reduction. A weight matrix W of linear projection is decomposed into two low-rank matrices. Input X is down-projected to a latent representation H, which
- Fig.10 (p.11) ![[assets/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-p11.png]]
  - vLLM system overview [22]. 11
- Fig.11 (p.12) ![[assets/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-p12.png]]
  - Operation flow of the prefetching module of InfiniGen. [23]. A layer-wise KV cache management strategy is proposed in LayerKV [24]. The core concept is to split KV cache by layers, keeping only a subs
- Fig.12 (p.15) ![[assets/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-p15.png]]
  - Standard linear attention (top) vs. loglinear attention (bottom). The input consists of query, key, and value vectors [30]. at nearby keys and averages their value; while Linear Attention is alike glo
- Fig.13 (p.17) ![[assets/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-p17.png]]
  - During Pre-filling, ShadowKV offloads the value cache to the CPU while maintaining a low-rank key cache, landmarks, and outliers on the GPU. During decoding, it employs landmarks for sparse attention.
- Fig.14 (p.17) ![[assets/kv-cache-optimization-strategies-for-scalable-and-efficient-llm-inference-p17.png]]
  - System overview of TailorKV. Offline identification categorizes the layers into quantization-friendly and sparsity-friendly. For quantization-friendly layers, we employ aggressive static quantization.

### #63 Kimi Linear: An Expressive, Efficient Attention Architecture

- Fig.1 (p.1) ![[assets/kimi-linear-an-expressive-efficient-attention-architecture-p01.png]]
  - (a) Performance vs. acceleration. With strict fair comparisons with 1.4T training tokens, on MMLU-Pro (4k context length, red stars), Kimi Linear leads performance (51.0) at similar speed. On RULER (1
- Fig.2 (p.5) ![[assets/kimi-linear-an-expressive-efficient-attention-architecture-p05.png]]
  - Execution time of kernels for vary- ing input lengths, with a uniform batch size of 1 and 16 heads.
- Fig.3 (p.5) ![[assets/kimi-linear-an-expressive-efficient-attention-architecture-p05.png]]
  - Neural Parameterization
- Fig.4 (p.7) ![[assets/kimi-linear-an-expressive-efficient-attention-architecture-p07.png]]
  - Results on synthetic tasks: palindrome, multi query associative recall, and the state tracking.
- Fig.5 (p.9) ![[assets/kimi-linear-an-expressive-efficient-attention-architecture-p09.png]]
  - The fitted scaling law curves for MLA and Kimi Linear. balanced positional bias across layers, which improves robustness and extrapolation at long ranges, leading to stronger long-context performance.
- Fig.6 (p.12) ![[assets/kimi-linear-an-expressive-efficient-attention-architecture-p12.png]]
  - The training and test accuracy curves for Kimi Linear@1.4T and MLA@1.4T during Math RL training. Kimi Linear consistently outperforms the full attention baseline by a sizable margin during the whole R
- Fig.7 (p.13) ![[assets/kimi-linear-an-expressive-efficient-attention-architecture-p13.png]]
  - (a) The prefilling time of MLA (full attention), hybrid GDN-H and our Kimi Linear. (b) The time per output token (TPOT) for MLA, GDN-H and Kimi Linear during decoding. (We use batch size = 1 here for 

### #64 Muon is Scalable for LLM Training

- Fig.1 (p.1) ![[assets/muon-is-scalable-for-llm-training-p01.png]]
  - Scaling up with Muon. (a) Scaling law experiments comparing Muon and Adam. Muon is ∼2× more computational efficient than Adam with compute optimal training. (b) The MMLU performance of our Moonlight m
- Fig.2 (p.4) ![[assets/muon-is-scalable-for-llm-training-p04.png]]
  - Validation loss curves for AdamW (green), Muon without weight decay (red), and Muon with weight decay (blue).
- Fig.3 (p.7) ![[assets/muon-is-scalable-for-llm-training-p07.png]]
  - Fitted scaling law curves for Muon and AdamW optimizers.
- Fig.4 (p.10) ![[assets/muon-is-scalable-for-llm-training-p10.png]]
  - SVD entropy of weight matrices across different training iterations. We categorize the weight matrices into 6 different groups: 1) AttnQO denotes the weight matrices related to the query and output pr
- Fig.5 (p.15) ![[assets/muon-is-scalable-for-llm-training-p15.png]]
  - Optimization Landscapes for Scaling Law Hyper-parameters Across FLOPs Budgets
- Fig.6 (p.15) ![[assets/muon-is-scalable-for-llm-training-p15.png]]
  - D
- Fig.7 (p.17) ![[assets/muon-is-scalable-for-llm-training-p17.png]]
  - Training dynamics comparison between Moonlight and Moonlight-A
- Fig.8 (p.9) ![[assets/muon-is-scalable-for-llm-training-p09.png]]
  - 6.
- Fig.9 (p.18) ![[assets/muon-is-scalable-for-llm-training-p18.png]]
  - Distribution of singular values for each weight matrix in the attention layers. We use WC to denote the weight matrices at each layer that compress the hidden states to the shared latent spaces for ke
- Fig.10 (p.19) ![[assets/muon-is-scalable-for-llm-training-p19.png]]
  - Distribution of singular values for each weight matrix in the feed-forward network (FFN) layers. We use WI, WV and WO to denote the weight matrices involved in the FFN layer with SwiGLU activation fun

### #65 Attention Residuals

- Fig.1 (p.1) ![[assets/attention-residuals-p01.png]]
  - Overview of Attention Residuals. (a) Standard Residuals: standard residual connections with uniform additive accumulation. (b) Full AttnRes: each layer selectively aggregates all previous layer output
- Fig.2 (p.5) ![[assets/attention-residuals-p05.png]]
  - PyTorch-style pseudo code for Block Attention Residuals. block_attn_res computes softmax attention over block representations using a learned pseudo-query wl; forward is a single-layer pass that maint
- Fig.3 (p.6) ![[assets/attention-residuals-p06.png]]
  - Cache-based pipeline communication example with 4 physical ranks and 2 virtual stages per rank, where hatched boxes denote end of AttnRes blocks. Numbers indicate micro-batch indices. Each rank caches
- Fig.4 (p.9) ![[assets/attention-residuals-p09.png]]
  - Scaling law curves for Attention Residuals. Both Full and Block AttnRes consistently outperform the baseline across all scales. Block AttnRes closely tracks Full AttnRes, recovering most of the gain a
- Fig.5 (p.10) ![[assets/attention-residuals-p10.png]]
  - Training dynamics of Baseline and Block AttnRes. (a) Validation loss during training. (b) Each transformer block’s output magnitude at the end of training. (c) Each transformer block’s gradient magnit
- Fig.6 (p.11) ![[assets/attention-residuals-p11.png]]
  - Effect of block size on validation loss (16-layer model). • Language understanding and reasoning: MMLU [13], MMLU-Pro Hard [55], GPQA-Diamond [41], BBH [48], ARC-Challenge [6], HellaSwag [65], and Tri
- Fig.7 (p.12) ![[assets/attention-residuals-p12.png]]
  - Architecture sweep under fixed compute (≈6.5 × 1019 FLOPs, ≈2.3 × 108 active parameters). Each cell reports validation loss for a (dmodel/Lb, H/Lb) configuration, where Lb = L/2 is the number of Trans
- Fig.8 (p.13) ![[assets/attention-residuals-p13.png]]
  - Depth-wise attention weight distributions for a 16-head model with full (top) and block (bottom) Attention Residuals, averaged over tokens. The model has 16 attention and 16 MLP layers. Each row shows
- Fig.9 (p.15) ![[assets/attention-residuals-p15.png]]
  - Depth mixing matrices M for four residual variants (L=4; Block AttnRes uses block size S=2). Highway is shown with scalar gates for clarity. AttnRes panels show unnormalized ϕ scores; background color

### #66 Huawei Cloud Model-as-a-Service on the CloudMatrix384 SuperP

- Fig.2 (p.23) ![[assets/huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod-p23.png]]
  - FlowServe selects the appropriate DistFlow [10] backend based on the network fabric. For MLA models like DeepSeek and Kimi K2, both interconnects satisfy TTFT and TPOT SLAs.
- Fig.4 (p.8) ![[assets/huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod-p08.png]]
  - Step 1: The sender’s serving engine invokes XCCL’s send, passing the source buffer in the app data area (e.g., KV cache), an eventID (e.g., number of sends), the receiver NPU’s ID, and the number of A
- Fig.8 (p.12) ![[assets/huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod-p12.png]]
  - Trade-off between MTE and DMA. To improve communication efficiency, we employ NPU-Direct Unified Remote Memory Access (URMA), a technique on Ascend NPUs similar to IBGDA on GPUs [15]. NPU-Direct URMA 
- Fig.10 (p.12) ![[assets/huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod-p12.png]]
  - This redesign centers on three key components: • First, we introduce the Data Parallel (DP) group abstraction, inspired by SGLang [24].
- Fig.12 (p.16) ![[assets/huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod-p16.png]]
  - Step 1: Collecting Expert Load Distribution. First, we collect data on expert loads across NPUs. We define expert load as the total number of tokens routed to each expert within a given time interval.
- Fig.17 (p.22) ![[assets/huawei-cloud-model-as-a-service-on-the-cloudmatrix384-superpod-p22.png]]
  - 1. A request first arrives at a randomly selected Job Executor (JE), which assigns it to a prefill

### #67 CacheBlend: Fast Large Language Model Serving for RAG with C

- Fig.1 (p.2) ![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p02.png]]
  - Contrasting full KV recompute, prefix caching, full KV reuse, and CacheBlend’s selective KV recompute. full KV recompute (Figure 1(a)). Despite many optimizations, the delay and computation of prefill
- Fig.2 (p.4) ![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p04.png]]
  - Generation quality improves as more text chunks are retrieved. and fetch top-k relevant chunks from the database, based on the least L2 distance between the embeddings of the query and the chunk respe
- Fig.3 (p.4) ![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p04.png]]
  - An illustrative example of an LLM input with two text chunks prepended to a query. Full KV recompute (b), with- out reusing KV cache, is slow but gives the correct answer. Full KV reuse (c), however, 
- Fig.4 (p.5) ![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p05.png]]
  - Contrasting the attention matrices of (a) full KV recompute and (b) full KV reuse. The yellow boxes highlight the cross-attention. The right-hand side plots show the resulting forward attention matric
- Fig.5 (p.6) ![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p06.png]]
  - Illustrated contrast between (a) full KV recompute and (b) selective KV recompute on one layer. 0 10 20 30 40 50
- Fig.6 (p.6) ![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p06.png]]
  - Attention deviation reduces as we recompute the KV of more tokens on each layer. Importantly, the biggest drop in attention deviation results from recomputing the KV of the tokens with the highest KV 
- Fig.7 (p.7) ![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p07.png]]
  - Distribution of KV deviation of different tokens on one layer. 5 vs. 6 12 vs. 13 21 vs. 22 31 vs. 32
- Fig.8 (p.7) ![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p07.png]]
  - Rank correlation of the KV deviation per token be- tween two consecutive layers. expensive and defeats the purpose of selective KV recom- pute. Instead, we observe that the HKVD tokens on different la
- Fig.9 (p.7) ![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p07.png]]
  - CacheBlend selects the HKVD (high KV deviation) tokens of one layer by computing KV deviation of only the HKVD tokens selected from the previous layer and selecting the tokens among them with high KV 
- Fig.10 (p.8) ![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p08.png]]
  - (a) Smartly picking the recompute ratio will not incur an extra delay. (b) Smartly picking storage device(s) to store KVs saves cost while not increasing delay. recompute of one layer, the KV-loading 
- Fig.11 (p.9) ![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p09.png]]
  - CacheBlend system (green stared) in light of LLM context augmented generation for a single request. CacheBlend uses text provided by the retriever, interacts with the storage device(s), and provides K
- Fig.12 (p.10) ![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p10.png]]
  - CacheBlend reduces TTFT by 2.2-3.3× compared to full KV recompute with negligible quality drop across four datasets and three models.
- Fig.13 (p.10) ![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p10.png]]
  - Generation quality of CacheBlend with Yi-34B vs MapReduce and MapRerank. 7
- Fig.14 (p.11) ![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p11.png]]
  - CacheBlend achieves lower TTFT with higher throughput in RAG scenarios compared with baselines of similar quality. 3 6 9 12 (a) Number of chunks
- Fig.15 (p.11) ![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p11.png]]
  - CacheBlend outperforms baseline with varying chunk numbers, chunk lengths, and batch sizes. • SAMSum [25]: This dataset comprises multiple pairs of dialogues and summaries, and requires the LLM to out
- Fig.16 (p.8) ![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p08.png]]
  - This means that even if the storage device is a fast device (ex. CPU RAM), the delay will be lower-bounded by the minimal recomputation to guarantee quality.
- Fig.17 (p.12) ![[assets/cacheblend-fast-large-language-model-serving-for-rag-with-cached-knowledge-fusion-p12.png]]
  - CacheBlend’s outperforms baselines when using RAM and slower disks

### #69 Single-Rollout Asynchronous Optimization for Agentic Reinfor

- Fig.1 (p.1) ![[assets/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning-p01.png]]
  - The performance of SAO on reasoning and coding benchmarks. The four reasoning benchmarks are evaluated in a reasoning-with-Python-tool setting, where the baseline is the Qwen3- 30B-A3B SFT model; SWE-
- Fig.2 (p.3) ![[assets/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning-p03.png]]
  - Overview of SAO with single rollout design. The numbers denote the generation order of trajectories. For SAO, each trajectory becomes available for training immediately upon completion.
- Fig.3 (p.6) ![[assets/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning-p06.png]]
  - Performance comparison between SAO and GRPO (w/ DIS) during training. It can be observed that SAO almost consistently outperforms the optimized GRPO during the training process on different benchmarks
- Fig.4 (p.7) ![[assets/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning-p07.png]]
  - Training dynamics of asynchronous single-rollout RL. (a) Explained Variance for SAO and a single-critic-update baseline. (b) Critic gradient norm during value training under full-parameter optimizatio
- Fig.5 (p.9) ![[assets/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning-p09.png]]
  - Online learning simulation under changing writing-style preferences. 5
- Fig.6 (p.13) ![[assets/single-rollout-asynchronous-optimization-for-agentic-reinforcement-learning-p13.png]]
  - Training reward for token-level SAO training and step-level variants, where token-level shows better training rewards.

### #70 rLLM: Relational Table Learning with LLMs

- Fig.1 (p.1) ![[assets/rllm-relational-table-learning-with-llms-p01.png]]
  - Trends in global data volume and in LLM token costs by data type
- Fig.2 (p.2) ![[assets/rllm-relational-table-learning-with-llms-p02.png]]
  - The architecture of rLLM analyzed using GNNs. This design efficiently captures inter-table dependencies with minimal architectural complexity.
- Fig.3 (p.2) ![[assets/rllm-relational-table-learning-with-llms-p02.png]]
  - Base data structure in rLLM. Arrows indicate inher- itance relationships and parentheses indicate containment relationships. data, respectively. Overall, this design meets the familiar storage and pro
- Fig.4 (p.3) ![[assets/rllm-relational-table-learning-with-llms-p03.png]]
  - The architecture of BRIDGE columns, which can vary greatly in nature. Due to the diverse types of features and the often limited information provided by tables with fewer columns, it is crucial to map
