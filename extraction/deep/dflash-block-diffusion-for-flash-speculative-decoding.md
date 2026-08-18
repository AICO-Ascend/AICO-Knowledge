# DFlash: Block Diffusion for Flash Speculative Decoding — 技术点深读（DEEP 2026-08-18）

<!-- 独立深读文件：内容来自 dflash-block-diffusion-for-flash-speculative-decoding.txt + minimax_captions.json (5 张 figure caption)，与 extract_phase1 生成的 MD/MOC 解耦，避免被覆盖。 -->

## 核心问题

DFlash 攻击的是 speculative decoding 中 **autoregressive drafting 的串行瓶颈**，这是一个被 §3.2 形式化揭示的根本性 Pareto 困境：

- **机制层面**（§3.1, eq. 1）：speculative decoding 的 per-token 平均延迟为 `L = (T_draft + T_verify) / τ`，其中 τ 为期望接受长度（含 bonus token，∈[1, γ+1]）。加速比 `π = L_target / L` 只能通过两条路径改善：增大 τ 或减小 T_draft。
- **AR drafter 的死结**（§3.2, eq. 2）：autoregressive drafter 的 `T_draft = γ · t_step`，起草成本随 speculation budget γ **线性增长**。为压低延迟，drafter 必须极浅（EAGLE-3 仅用单层 transformer，§1）。但浅模型容量不足，τ 随 γ 很快饱和——"increasing γ increases drafting cost, acceptance length τ quickly saturates due to limited model capacity"（§3.2）。这把 SOTA 方法（EAGLE-3）的实际加速比锁死在 **约 2–3×**（§1, abstract）。
- **Diffusion drafter 的两条既有死路**（§1, §2.3）：(i) 大型 dLLM drafter（DiffuSpec、SpecDiff-2，7B 参数）内存不可负担，起草延迟高，实际仅 3–4×；(ii) PARD 用小 AR 模型模拟 diffusion 式并行，但容量不足，加速天花板约 3×。同时独立 dLLM 本身质量劣于 AR（§1），且需要大量 denoising steps 才能保质量（§1, §2.2，引 d3LLM/Qian et al. 2026）。

DFlash 的核心命题：**能否同时做到轻量 + 高接受率 + 并行起草？** 关键 insight 是 "the target knows best"——大 AR target 的 hidden features 隐式编码了未来多 token 信息（§1, §4.1，引用 Samragh et al. 2025）。DFlash 把 draft model 重新定位为 **diffusion adapter**，直接复用 target 已建模的深层上下文，而非让小模型从零推理。这一命题在 Figure 1（p.2）的端到端 speedup 对比中得到直接验证：在 Qwen3-8B 上，Baseline 归一化为 1.00×，EAGLE-3 落在 1.81×–2.23×，DFlash 跨 7 个 benchmark 跳升至 2.75×（MT-Bench）至 6.08×（Math500），峰值 Math500 达 6.08×——M3 解读明确指出 "block-diffusion drafting substantially outperforms autoregressive speculative decoding on reasoning-heavy tasks"。

## 关键创新点

1. **KV injection 条件化机制**（§4.1, §A.3，对应 Figure 2 p.4）
   - **机制**：从 target model 浅到深均匀采样 5 层 hidden states，concat 后过一个轻量投影 `H_t = RMSNorm(W_c [H^(l_1);...;H^(l_5)])`（§A.3）。与 EAGLE-3 把特征 fuse 到 drafter 输入 embedding 不同，DFlash 把 `H_t` 作为 **persistent KV entries 直接注入每一层 draft layer 的 K/V 投影**：`K_i = [W^K_i H_t ; W^K_i H_d]`, `V_i = [W^V_i H_t ; W^V_i H_d]`（§A.3）。target 特征只作为额外 KV，bypass draft 的 Q 投影、output projection、self-attention update、FFN。
   - **图证**：Figure 2（p.4）的 M3 解读点出架构核心：block-diffusion draft model 块内并行生成多 token → 低 draft 延迟；target LLM 先 prefill 产首 token 并取若干层隐藏态，concat 后过投影层融成 target context feature，**注入每个 draft 层的 KV cache 并跨轮复用**，持续提供上下文引导 → 接受长度随 draft 深度增长，无 token-embedding 稀释（优于 EAGLE 式输入融合）。这正对应 §4.1 "Conditioning via KV injection enables acceptance scaling" 的论断。
   - **效果**：EAGLE-3 式 input fusion 在 draft 深度增加时 target 信息逐层稀释，acceptance 增益递减；DFlash 的 per-layer 注入让 acceptance length 随 draft 层数 **有效 scaling**（§4.1, §5.5.2）。消融（Table 9, §5.5.5）：block-diffusion + KV injection 在 GSM8K/HumanEval/MT-Bench 上 τ=4.2/4.0/3.0，speedup 3.3×/3.2×/2.2×，全面优于 block-diffusion + input fusion（τ=3.5/3.5/2.6，2.9×/2.9×/2.0×）。内存开销可忽略：Qwen3.5-35B-A3B 上 `W_c` 仅 ~42 MB（相对 70 GB target），block size 16 解码时临时 activation < 400 KB（§A.3）。

2. **Block-diffusion 并行起草**（§3.2 eq. 3, §4.1，对应 Figure 3 p.3）
   - **机制**：所有 γ 个 masked token 在 **单次 forward pass** 内并行解码，`T_draft = t_parallel`，与 γ **几乎无关**。GPU 对并行操作效率远高于多次串行 pass，`t_parallel ≪ γ · t_step`。
   - **图证**：Figure 3（p.3）的 M3 解读给出量化对比——1-layer EAGLE-3 的 latency 随 draft token 数 (4/8/16) 几乎线性增长（~6→11→25 ms），而 DFlash 1/3/5-layer 的 latency 在所有 budget 下近乎平坦（~2–6 ms），因为"所有 draft token 在单次 forward pass 内并行生成，decoupling cost from speculation length"。这从图层面坐实 §3.2 eq.2 (AR 线性) vs eq.3 (diffusion 平坦) 的对比。
   - **效果**：打破 AR drafter 的"浅模型-低 τ"瓶颈，可负担 5 层（Qwen3-Coder 用 8 层）更深、更具表达力的 drafter。5 层 DFlash 生成 16 token 的延迟 **低于** 1 层 EAGLE-3 生成 8 token，Pareto 前移：同时获得更低 latency + 更高 acceptance length（§3.2 末段）。

3. **Speculative-decoding-tailored 训练**（§4.2，对应 Figure 4 p.5 + Figure 5 p.13）
   - **Random anchor sampling**：标准 block diffusion 把 response 均匀切块、块内随机 mask。DFlash 改为随机采样 anchor token 作为每个 block 起点，mask 后续 block_size−1 个位置。这 (i) 精确匹配推理时 drafter 总是以上一验证步的 bonus token 为起点的行为；(ii) 每个 epoch 对同一序列采不同 anchor，提供数据增强。Table 13（§A.5.2）：3-layer 模型上，Sample vs Standard τ 5.64/4.61/3.18 vs 4.94/3.86/2.80，speedup 4.69×/3.90×/2.38× vs 4.13×/3.29×/2.13×——全面显著提升。
   - **训练侧注意力结构**（Figure 4 p.5）：M3 解读两块 attention-mask grid——左 grid 编码输入序列（prompt tokens p 蓝色、作为 anchor 的 clean response tokens r 黄色、并行预测的 mask tokens m 绿色、块间 invisible 白色）；右 grid 显示 attention pattern：块内 bidirectional attention + KV-injected target features，**跨块 attention 禁止**。这正对应 §4.2 "Tokens attend bidirectionally within the same block and to the corresponding injected target context features, while attention across different blocks is disallowed"，使多个 draft block 在单次 forward/backward pass 内联合训练（Flex Attention）且无 inter-block 信息泄漏。
   - **Exponential loss decay**（eq. 4，对应 Figure 5 p.13）：`w_k = exp(−(k−1)/α)`，α 对 block size 16/10/8 分别为 7/5/4（§A.1）。理由：speculative decoding 中 block 早期位置错误会 **invalidates all subsequent tokens**，早期预测对 τ 不成比例地重要。Figure 5（p.13）M3 解读给出收敛曲线对比：两条曲线（with/without loss decay）最终在 epoch 7 后趋同于 ~6.35 acceptance length，但 **with loss decay 在 epoch 2–4 领先约 0.2–0.3 个点**，证明强调早期 token 准确性加速了早期训练收敛。注意 M3 指出两者最终接近，说明 loss decay 主要收益在收敛速度而非最终上限。
   - **Shared embedding + LM head**：drafter 与 target 共享 frozen token embedding 和 LM head，只训练 draft transformer 层，减少可训练参数并迫使 drafter 对齐 target 表示空间（§4.2）。

4. **Efficient long-context training**（§4.2）
   - **机制**：固定每个序列的 masked block 数，每 epoch 随机采样 anchor 位置——数据增强的同时训练成本有界。绕开 EAGLE-3 "training-time test" 在长上下文上的高昂成本。
   - **效果**：base 4K 训练的 drafter 仅用 1.6K LongAlign 样本 fine-tune 3 epoch 即可适配长上下文。Table 4（§5.4）：Base 在 16K/32K hotpotqa 上 τ 跌至 3.61/–，Long 版升至 6.05；gov_report 32K 从 2.09 升至 3.56。证明 target 特征在长上下文下仍具代表性。

5. **Block-size 跨设定泛化**（§5.5.4）
   - **机制/发现**：train block size 16 的模型可很好地泛化到 inference block size 8（acceptance 接近 b8→b8 训练的模型），但反之不行——**大 block 训练 → 小 block 推理** 成立。b8 模型 35.7% 的 block 被全接受，说明 block size 8 常被 underutilized；b16 接受分布更分散、τ 更高。
   - **效果**：为 compute-bound（大 batch）场景下动态缩小 block size 以降低 verification 成本提供基础（论文留作 future work）。

## 表格（原文结构化）

### Table 1（§5.1）：Qwen3-4B/8B（thinking off，max 2048 token）vs EAGLE-3，温度 0/1
| Model | Method | GSM8K τ | GSM8K Sp | MATH500 τ | MATH500 Sp | AIME25 τ | AIME25 Sp | HumanEval τ | HumanEval Sp | MBPP τ | MBPP Sp | LCB τ | LCB Sp | MT-Bench τ | MT-Bench Sp | Avg Sp |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Q3-4B T=0 | EAGLE-3(16) | 3.30 | 1.99× | 3.08 | 1.83 | 3.05 | 1.79 | 3.05 | 1.84 | 2.95 | 1.78 | 2.91 | 1.73 | 3.02 | 1.74 | 1.81× |
| Q3-4B T=0 | EAGLE-3(60) | 3.77 | 2.27 | 3.52 | 2.10 | 3.51 | 2.13 | 3.47 | 2.12 | 3.38 | 2.02 | 3.22 | 1.90 | 3.49 | 2.04 | 2.08× |
| Q3-4B T=0 | **DFlash(16)** | 6.53 | 5.15 | 7.84 | 6.09 | 7.27 | 5.68 | 6.64 | 5.21 | 6.09 | 4.78 | 7.09 | 5.41 | 4.35 | 2.85 | **4.91×** |
| Q3-8B T=0 | DFlash(16) | 6.54 | 5.15 | 7.87 | 6.08 | 7.08 | 5.62 | 6.50 | 5.14 | 5.95 | 4.65 | 7.27 | 5.51 | 4.24 | 2.75 | 4.86× |
| Q3-4B T=1 | DFlash(16) | 6.00 | 4.71 | 6.67 | 5.09 | 4.92 | 3.73 | 6.04 | 4.74 | 5.66 | 4.42 | 6.50 | 4.90 | 4.07 | 2.67 | 4.24× |
| Q3-8B T=1 | DFlash(16) | 5.98 | 4.67 | 6.40 | 4.84 | 4.73 | 3.57 | 5.52 | 4.32 | 5.21 | 4.04 | 6.69 | 4.93 | 3.80 | 2.47 | 4.03× |

**关键数字**：T=0 平均加速 4.9×，比 EAGLE-3(16) 提升 2.4×；T=1 平均 4.1×，比 EAGLE-3(16) 提升 2.2×。DFlash(16) 的 τ 在多数任务上甚至超过 EAGLE-3(60)，且 verification 开销更低。Q3-8B 的 Math500 DFlash 6.08× 即对应 Figure 1（p.2）M3 解读的峰值 bar。

### Table 3（§5.3）：SGLang + FA4 + B200，throughput (tok/s) 与 speedup
| Model | Task | Conc=1 Sp | Conc=4 Sp | Conc=8 Sp | Conc=16 Sp | Conc=32 Sp | Avg τ |
|---|---|---|---|---|---|---|---|
| Qwen3-4B | Math500 | 4.8× | 4.3× | 4.1× | 3.5× | 2.9× | 8.01 |
| Qwen3-8B | Math500 | 5.1× | 4.5× | 4.5× | 3.9× | 2.8× | 8.01 |
| Qwen3-8B | HumanEval | 4.2× | 3.6× | 3.6× | 3.0× | 2.4× | 6.50 |
| Qwen3-Coder-30B-A3B | HumanEval | 3.5× | 3.0× | 3.2× | 3.2× | 3.1× | 8.09 |
| Qwen3-Coder-30B-A3B | MBPP | 3.2× | 3.0× | 3.2× | 3.3× | 3.1× | 7.23 |

### Table 5（§5.5.1）：LLaMA-3.1-8B-Instruct on SGLang/Flashinfer/B200，同训练数据公平对比
| Method | GSM8K τ | GSM8K@1 Sp | HumanEval τ | HumanEval@1 Sp | Alpaca τ | Alpaca@1 Sp |
|---|---|---|---|---|---|---|
| EAGLE-3(10) | 3.49 | 1.6× | 3.62 | 2.0× | 3.11 | 1.5× |
| EAGLE-3(60) | 4.55 | 1.9× | 4.65 | 2.0× | 4.07 | 1.8× |
| **DFlash(10)** | 4.32 | 2.4× | 4.91 | 2.8× | 3.73 | 2.2× |

注意高并发 32 时 EAGLE-3(60) speedup 降至 0.5–0.6×（负加速），DFlash 仍保 1.4×–1.8×。

### Table 9（§5.5.5）：KV injection vs Input fusion（Qwen3-4B, 5-layer, block 8）
| Variant | Injection | GSM8K τ/Sp | HumanEval τ/Sp | MT-Bench τ/Sp |
|---|---|---|---|---|
| EAGLE-3-5L (AR drafting) | Input | 4.2/2.1 | 4.3/2.2 | 3.1/1.4 |
| DFlash-AR (AR drafting) | KV | 4.8/2.4 | 4.6/2.3 | 3.4/1.5 |
| DFlash (block-diff) | Input | 3.5/2.9 | 3.5/2.9 | 2.6/2.0 |
| **DFlash (block-diff)** | **KV** | **4.2/3.3** | **4.0/3.2** | **3.0/2.2** |

### Table 2（§5.2）：Reasoning models（thinking on）
| Model | Temp | GPQA τ/Sp | MATH-500 τ/Sp | AIME25 τ/Sp |
|---|---|---|---|---|
| Q3-4B | 0 | 5.23/4.23× | 5.74/4.59× | 5.54/4.39× |
| Q3-8B | 0 | 5.17/4.17× | 5.82/4.64× | 5.74/4.51× |
| Q3-8B | 1 | 4.65/3.75× | 5.06/4.03× | 4.69/3.70× |

### Table 11（§A.4）：更多模型，SGLang, B200, conc=8，τ/Sp
| Model | Math500 | HumanEval | MT-Bench |
|---|---|---|---|
| Qwen3.5-27B DFlash | 7.7/3.8× | 9.1/3.9× | 5.5/2.5× |
| Qwen3.5-35B-A3B DFlash | 7.2/2.4× | 7.9/2.3× | 5.4/1.7× |
| GPT-OSS-120B DFlash | 5.4/1.6× | 4.4/1.7× | 3.7/1.3× |

## 与同类对比

- **vs EAGLE 系列（[[eagle-speculative-sampling-requires-rethinking-feature-uncertainty]], [[eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees]], [[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]]）**：EAGLE-1 引入 feature-level context，EAGLE-2 加自适应 draft tree，EAGLE-3 用 training-time test 优化训练目标。三者共享同一底层范式：**AR drafting + input fusion**。DFlash 在两个机制维度上超越：(1) drafting 从串行 `γ·t_step` 变为并行 `t_parallel`（Figure 3 p.3 的 M3 量化对比：EAGLE-3 latency 6→25 ms 线性，DFlash 2–6 ms 平坦），使深层 drafter 可负担；(2) input fusion 在深层会稀释 target 信息（§4.1，Figure 2 p.4 M3 指出 KV injection 跨轮复用解决此问题），KV injection 让 target 特征每层可见，acceptance 随层数 scaling。公平同数据对比（Table 5, LLaMA-3.1-8B）：DFlash 在 conc=1 上 2.4×/2.8×/2.2× vs EAGLE-3(60) 1.9×/2.0×/1.8×。但 EAGLE-3 在低并发、小 batch 上仍是强 baseline；DFlash 的优势在高并发下被放大（EAGLE-3(60) @conc32 跌到 0.5–0.6×，DFlash 维持 1.4–1.8×）。

- **vs Medusa（[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]]）**：Medusa 用多 prediction head + tree attention 省去外部 drafter，但仍是 AR 式逐层 head 预测，本质串行，acceptance 受限。DFlash 用 block-diffusion 在单 pass 内并行出整个 block，τ 上限显著更高（Qwen3-4B Math500 τ=6.00–6.53）。

- **vs Block Diffusion（[[block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models]]）**：Block diffusion 是 DFlash 的技术基座（§1, §2.2, §4.2），但独立 dLLM 质量劣于 AR 且需要多 denoising step（§1, §2.2）。DFlash 的关键重构：把 block diffusion **限定在 drafting stage**，由 AR target 做无损验证，"aggressive reduction in denoising steps to maximize parallelism, while speculative verification provides a principled guarantee of output quality"（§6）。训练侧也偏离标准 block diffusion：random anchor sampling + loss decay + KV injection 共同对齐 speculative 推理行为，其中训练注意力结构（Figure 4 p.5）的块内 bidirectional + 跨块禁止 + KV-injected target features 即为此改造的可视化证据。

- **vs DSPark / 其他 semi-AR（[[dspark-confidence-scheduled-speculative-decoding-with-semi-autoregressive-generation]]）**：semi-AR 方法介于 AR 与 diffusion 之间。DFlash 走纯 block-diffusion 路线，通过 KV injection 直接借力 target 的 future-token 隐信息，避免 semi-AR 在置信度调度上的复杂度。

- **vs DiffuSpec / SpecDiff-2**（§1, §2.3）：均用 7B 级 pretrained dLLM 作 drafter，内存不可负担、起草延迟高，实际加速限于 3–4×。DFlash 用 5–8 层轻量 drafter + target feature 复用，达到 4.9×–6.1×，"lightweight and highly accurate"（§1）。

- **vs PARD**（§1, §2.3）：PARD 训练小 AR 模型模仿 diffusion 式并行起草，但小模型容量不足，τ 与加速天花板约 3×。DFlash 直接用 block diffusion + target KV 注入，τ 翻倍（Q3-8B GSM8K τ=6.54）。

- **vs Samragh et al. 2025**（§2.3, §4.1）：Samragh 观察到 AR LLM 隐式编码 future-token 信息，训 LoRA adapter 做并行 drafting，保留 base model 验证。DFlash 共享此 insight（"target knows best"），但实现路径不同——用 block-diffusion + per-layer KV injection 而非 LoRA adapter，acceptance 随 draft 深度 scaling（§4.1）。

- **vs TiDAR**（§2.3）：TiDAR 联合训练 diffusion（think）+ AR（talk），但最终生成 **非 lossless**。DFlash 由 AR target 验证保证 lossless（abstract, §6）。

- **vs Tree-based long-context（[[jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting]], [[longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification]], [[specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences]]）**：这些方法仍在 AR tree drafting 框架内扩展。DFlash 通过 random anchor + 固定 block 数实现有界长上下文训练（§4.2），并在 §5.4 展示 4K base 模型仅用 1.6K 样本微调即可适配 32K 上下文，τ 不降反升，从机制层面提供了不同的长上下文适配路径。

## 跨论文关系（→ MOC 谱系）

**推测解码谱系**：

- **Block diffusion 锚点**：[[block-diffusion-interpolating-between-autoregressive-and-diffusion-language-models]] —— DFlash 的技术基座；DFlash 把 block diffusion 从独立生成模型重构为 speculative decoding 的 drafting adapter，并用 KV injection + random anchor sampling + loss decay 改造训练目标对齐推理行为（Figure 4 p.5 训练注意力结构即此改造的可视化）。
- **Sister semi-AR 方法**：[[dspark-confidence-scheduled-speculative-decoding-with-semi-autoregressive-generation]] —— 同为突破 AR drafting 串行瓶颈的尝试，DFlash 走纯 block-diffusion 路线。
- **EAGLE 家族**（DFlash 的主要对照基线）：
  - [[eagle-speculative-sampling-requires-rethinking-feature-uncertainty]] —— feature-level context 范式奠基，DFlash 继承"借力 target hidden feature"思想但改 input fusion 为 KV injection（Figure 2 p.4 M3 解读明确点出此差异）。
  - [[eagle-2-faster-inference-of-language-models-with-dynamic-draft-trees]] —— 动态 draft tree；DFlash 用 block-diffusion 单 pass 并行替代 tree drafting（Figure 3 p.3 M3 量化对比 latency 平坦 vs 线性）。
  - [[eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test]] —— DFlash 的 head-to-head 对照（§5.1, §5.5.1，Figure 1 p.2 端到端 2.5× 优势），2.2–2.5× 优势；EAGLE-3 的 training-time test 在长上下文上成本高，DFlash 用固定 block 数 + random anchor 规避。
- **多 head 加速**：[[medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads]] —— 同属 spec decoding 谱系，DFlash 以并行 block diffusion 取代串行多 head 预测。
- **长上下文 spec decoding**：
  - [[jetspec-breaking-the-scaling-ceiling-of-speculative-decoding-with-parallel-tree-drafting]] —— parallel tree drafting，DFlash 在长上下文适配（§5.4）上提供 block-diffusion 替代路径。
  - [[longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification]] —— 长上下文无损 spec decoding 同道。
  - [[specextend-a-drop-in-enhancement-for-speculative-decoding-of-long-sequences]] —— drop-in 长序列增强，与 DFlash 的 1.6K 样本微调即适配长上下文思路呼应。

## 局限与边界

- **高并发下加速衰减**：Table 3/5 显示 conc=32 时 speedup 显著下降（Qwen3-4B Math500 从 4.8×→2.9×；LLaMA-3.1 HumanEval DFlash 2.8×→1.8×）。原因是大 batch 下 verification 成本上升、并行 block 的 verification 开销在 compute-bound 区域放大。论文承认"large blocks can increase verification cost under compute-bound settings (e.g., large batch sizes)"（§5.5.4）但把 adaptive block-size scheduling 留作 future work。
- **Lossless 保证依赖 AR target 验证**：DFlash 的无损性来自 target model 并行 verify（§6），本身不解决 verify 成本；在极端长输出或超大 batch 下，verification 仍是瓶颈。
- **MT-Bench/chat 任务加速偏低**：Table 1 中 MT-Bench speedup 仅 2.75×（Q3-8B）/2.85×（Q3-4B），远低于 Math 任务的 5–6×。chat 任务的 τ 也最低（4.24–4.35）。说明 block-diffusion drafting 在自由对话、低结构化输出上优势收窄——Figure 1（p.2）M3 解读亦确认峰值在 Math500 (6.08×)，MT-Bench 仅 2.75×。
- **未与同类开源 dLLM spec 方法直接对比**：§5 明确声明未与 TiDAR、Samragh、DiffuSpec、SpecDiff-2 对比（"lack of open-source implementation"），只能从论文声称的 3–4× 间接论证优势。EAGLE-3 是唯一实测对照。
- **Block-size 推理泛化不对称**：§5.5.4 仅 b16→b8 方向成立，b8→b16 明显退化（Math500 τ 5.02 vs 6.33）。说明训练 block size 选择有不可逆性，部署需谨慎。
- **Loss decay 最终收益有限**：Figure 5（p.13）M3 解读指出 with/without loss decay 两条曲线在 epoch 7 后趋同于 ~6.35 acceptance length，loss decay 主要加速早期训练收敛（epoch 2–4 领先 0.2–0.3 点），对最终上限提升不显著。
- **Reasoning 模型加速低于 instruct**：thinking on 时（Table 2）speedup 4.2–4.6×，低于 thinking off 的 4.9×。reasoning trace 的长尾、低重复结构压缩了 acceptance 空间。
- **训练数据依赖 target 自蒸馏**：§5 datasets 用 target model 生成 response 作训练集（"responses generated by the target model for better target alignment"）。迁移到新 target 需重新生成训练数据，限制了 drafter 的开箱即用性。
- **超大模型（120B）加速有限**：Table 11 GPT-OSS-120B 仅 1.6×/1.7×/1.3×，说明 target 越大、verification 占比越高，diffusion drafting 的相对收益被稀释。
- **Denoising step 数未深入消融**：论文强调"aggressive reduction in denoising steps"（§6）但正文未给出 step 数与质量/延迟的曲线，仅 Figure 3（p.3）给出 draft latency 对比。
