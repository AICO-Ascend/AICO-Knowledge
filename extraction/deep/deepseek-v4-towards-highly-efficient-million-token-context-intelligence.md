# DeepSeek-V4 — 技术点深读（DEEP 2026-08-18）
> 全要素深读笔记。独立文件，extract_phase1 重跑不丢。
> 论文：DeepSeek-V4: Towards Highly Efficient Million-Token Context Intelligence · arXiv:2606.19348

## 核心问题

vanilla attention 的二次复杂度在百万 token 上下文下成为不可承受的瓶颈，直接卡死两条未来路径：(1) reasoning 模型的 test-time scaling（推理时扩展推理链长度）；(2) long-horizon 任务（agentic workflow、跨文档分析）。DeepSeek-V3/V3.2 虽已是高效基线（MLA+MoE+FP8），但在 1M 上下文下 attention 仍是计算/访存的主导成本（§1, §2.3 开头："the attention mechanism emerges as the dominant computational bottleneck in a model"）。V4 的目标：在保持/超越 V3.2 能力的前提下，把 1M 上下文的单 token 推理 FLOPs 与 KV cache 同时压下一个数量级，使百万上下文从"演示级"变为"可日常服务级"，进而为 online learning 等下一步范式铺路（§1 末段）。

## 关键创新点

1. **混合注意力 CSA + HCA（§2.3）** — V4 的核心机制。两类高效注意力交错（interleaved hybrid）配置：
   - **CSA（Compressed Sparse Attention，§2.3.1）**：两步。先压缩——每 `q` 个 KV entry 用 softmax 权重聚合成 1 个压缩 entry（序列长缩到 1/q）；再稀疏——用 "Lightning Indexer" 在压缩后的 KV 上做 DSA（DeepSeek Sparse Attention）top-k 选择，每个 query token 只 attend `p` 个压缩块。索引打分 `I_{t,s} = Σ_h w^I_{t,h} · ReLU(q^I_{t,h} · K^{IComp}_s)`（式 15–16），低秩生成（先 `c^Q_t = h_t·W^{DQ}` 降到 `d_q` 维，再升维成 indexer 头）。注意 CSA 的压缩是**重叠（overlapped）**的：用于 `C^{Comp}_i` 的 `C^b` 索引与 `C^a` 索引有重叠 → 实际压缩率恰为 1/q。
   - **HCA（Heavily Compressed Attention，§2.3.2）**：更激进压缩但保持 dense。每 `q'`（`q' ≫ q`）个 KV 聚合成 1 个 entry，序列长缩到 1/q'，**不做重叠压缩、不做稀疏选择**，直接对所有压缩 entry 做 dense attention。
   - 二者共享 Shared Key-Value MQA（每个压缩 entry 既当 key 又当 value，§2.3.1 "Shared Key-Value MQA"）与 Grouped Output Projection（把 `n_h` 个头分 6 组，先升到 `d_o` 中间维再聚合，缓解 `d_h·n_h` 过大的输出投影成本）。

2. **百万上下文效率量级（§1, §2.3.4, Figure 1 右）** — 量化效果。1M-token 上下文下，相对 DeepSeek-V3.2：
   - DeepSeek-V4-Pro（1.6T 总参 / 49B 激活）：单 token 推理 FLOPs 仅 **27%**（等效 FP8 FLOPs），KV cache 仅 **10%**。
   - DeepSeek-V4-Flash（284B 总参 / 13B 激活）：FLOPs 仅 **10%**，KV cache 仅 **7%**。
   - 相对 BF16 GQA8（head dim 128，常见 baseline）基线：1M 上下文下 V4 的 KV cache 仅约 **2%**（§2.3.4 末："can be dramatically reduced to approximately 2% times of that baseline"）。
   - 机制来源（§2.3.4）：(a) 混合存储格式——RoPE 维 BF16、其余 FP8，KV cache 比纯 BF16 几乎减半；(b) Lightning indexer 内部 attention 计算走 **FP4**，超长上下文下加速；(c) 相对 V3.2 选了更小的 attention top-k；(d) 压缩 + 混合注意力的结构性下降是主因。

3. **Manifold-Constrained Hyper-Connections / mHC（§2.2）** — 残差连接升级。标准 HC（Zhu et al., 2025）把残差流从 R^d 扩到 R^(λ_hc·d)（`λ_hc` 残差宽度因子，远小于隐藏维 d），引入输入映射 `A_l`、残差变换 `B_l`、输出映射 `C_l`（式 1）。问题：叠多层后数值频繁不稳定，阻碍 scaling。
   - mHC 核心约束：把残差映射 `B_l` 约束到**双随机矩阵流形（Birkhoff polytope）M**（式 2：行和=1、列和=1、非负）。保证 `||B_l||_2 ≤ 1`（非扩张），且 M 对乘法封闭（深栈稳定）。输入/输出映射用 Sigmoid 限制为非负有界（式 6–7：`A_l=σ(Ã_l)`，`C_l=2σ(C̃_l)`）。
   - 投影方法：Sinkhorn-Knopp 迭代——先 `M^(0)=exp(B̃_l)` 保正，再交替行/列归一化（式 8：`M^(t)=T_r(T_c(M^(t-1)))`），取 `t_max=20`。
   - Dynamic Parameterization（§2.2）：`A_l/B_l/C_l` 的原始参数 = 动态（输入相关）分量 + 静态偏置。先 `X̂_l=RMSNorm(vec(X_l))`，再用可学习矩阵 `U^{pre}/U^{res}/U^{post}` 生成 `Ã_l/B̃_l/C̃_l`（式 3–5）；门控因子 `U` 初始化为小值。

4. **Muon 优化器（§2.4 + Algorithm 1）** — 加快收敛 + 训练稳定。对大多数模块用 Muon，少数保留 AdamW：**embedding、prediction head、mHC 静态偏置与门控、所有 RMSNorm** 仍用 AdamW，其余统一 Muon。
   - 算法（Algorithm 1）：梯度→Nesterov 动量（`M_B=β·M_{B-1}+G_B`，再对 `β·M_B+G_B` 做正交化）→HybridNewtonSchulz 正交化→RMS 重缩放（复用 AdamW 超参）→weight decay 更新（`θ_B = θ_{B-1}·(1−ω) − η·O_B`）。
   - **Hybrid Newton-Schulz 双阶段系数**（§2.4，式 28）：共 10 次迭代；前 8 步用 `(a,b,c)=(3.4445, −4.7750, 2.0315)` 快速把奇异值推向 1；后 2 步切到 `(a,b,c)=(2, −1.5, 0.5)` 精细稳定到 1。兼顾收敛速度与数值精度。
   - **弃用 QK-Clip**（§2.4 末）：V4 的注意力架构允许直接对 Q 与 KV entry 做 RMSNorm，从根上避免 logits 爆炸，故无需 Liu et al.(2025) 的 QK-Clip 技巧。

5. **细粒度 EP 通信-计算重叠（§3.1）** — MoE expert parallelism 的 mega-kernel。把 MoE 层 4 段（Dispatch / Linear-1 / Linear-2 / Combine，2 通信 bound + 2 计算 bound）融合成单条流水 kernel；进一步把 expert 切成 wave，一波 dispatch 完即开算，下一波并行 dispatch，稳态下"当前波计算 + 下一波 token 传输 + 上一波结果回送"三路并发 = 连续计算-通信流水。Comet（Zhang et al., 2025b）只粗粒度重叠 Dispatch↔L1、L2↔Combine；V4 更细。
   - 性能（§3.1 末）：NVIDIA GPU + HUAWEI Ascend NPU 双平台验证；相对强非融合 baseline，通用推理 **1.50~1.73×** 加速，RL rollout 等延迟敏感场景最高 **1.96×**。开源为 MegaMoE（DeepGEMM 组件）。
   - 关键洞察（§3.1 "Observations"）：单层内通信总时 < 计算总时 → 通信可完全藏于计算之下。硬件平衡点：每 token-expert 对需 6d FLOPs（SwiGLU gate/up/down）但仅 3d 字节通信（FP8 Dispatch + BF16 Combine）→ `C/B ≥ 6144 FLOPs/Byte`，即每 1 GBps 互连带宽即可藏住 6.1 TFLOP/s 计算；超此点带宽不再是瓶颈，再堆带宽边际递减。

6. **基础设施其他项（§3.2–3.5，部分仅在 fulltext 截断前覆盖）**：
   - **TileLang DSL（§3.2）**：用 TileLang（Wang et al., 2026）写融合 kernel 替换数百个 Torch ATen 算子，兼顾开发效率与运行性能，便于快速原型化 attention 变体。
   - **细粒度 EP / TileLang 之后的内容**（§3.3–3.5，fulltext 在 §3.2 处截断，未在 46KB 摘录中展开，依据目录与摘要整合）：(§3.3) batch-invariant + deterministic kernel 库，保证 train/inference bitwise 可复现；(§3.4) 训练框架——Muon 的高效实现、mHC 的 recompute+fused 降成本实现、长上下文 attention 的两阶段 contextual parallelism、tensor 级 checkpointing 的扩展自动微分；(§3.5) 推理框架——异构 KV cache 结构 + on-disk 存储以支持 shared-prefix 复用。

7. **预训练规模（§1, §4，§4 正文未在 fulltext 中展开）**：V4-Flash 训练于 **32T tokens**，V4-Pro 训练于 **33T tokens**。两模型预训练后即可原生高效支持 1M 上下文（无需长上下文再训练）。内部评测中 V4-Flash-Base 已在多数 benchmark 上超 V3.2-Base（更 parameter-efficient），V4-Pro-Base 在 reasoning/coding/long-context/world knowledge 上全面领先 DeepSeek 基座模型。

8. **两阶段后训练：Specialist Training + On-Policy Distillation（§1, §5.1）**：
   - 阶段一 Specialist Training（§5.1.1）：每个目标域（数学、coding、agent、指令遵循）独立训练一个专家。先 SFT 建基础能力，再用 GRPO（DeepSeek-AI, 2025）+ 域定制 reward model 做 RL，得到一组专门化专家。
   - 阶段二 On-Policy Distillation / OPD（§5.1.2）：用单一统一模型作为 student，向多个 teacher 专家优化 **reverse KL** 损失整合能力（`L_OPD(θ)=Σ_i w_i·D_KL(π_θ‖π_{E_i})`，见 MD 关键公式）。
   - FP4 QAT（§5.2.1）：后训练阶段对 MoE 专家权重 + indexer QK 路径引入 FP4 quantization-aware training，降内存与计算。

## 表格（原文结构化）

### 表 1 — DeepSeek-V4 系列规格（§1, §2）
| 模型 | 总参数 | 激活参数 | 上下文长度 | 预训练 tokens | 备注 |
|---|---|---|---|---|---|
| DeepSeek-V4-Pro | 1.6T | 49B | 1M | 33T | Pro-Max = 最大推理强度模式 |
| DeepSeek-V4-Flash | 284B | 13B | 1M | 32T | 更 parameter-efficient |

### 表 2 — 1M-token 上下文效率对比（相对 DeepSeek-V3.2，§1 / §2.3.4 / Figure 1 右）
| 指标（1M ctx） | DeepSeek-V4-Pro | DeepSeek-V4-Flash |
|---|---|---|
| 单 token 推理 FLOPs（等效 FP8，vs V3.2） | 27% | 10% |
| KV cache size（vs V3.2） | 10% | 7% |
| KV cache（vs BF16 GQA8 head-dim-128 baseline） | ≈2% | ≈2% |

### 表 3 — Figure 1 左 benchmark 概览（依据摘要 §1 "Summary of Core Evaluation Results" + 图条文本；模型-数值精确对应以原文 PDF 为准）
| 类别 | 结论（§1 摘要） |
|---|---|
| Knowledge（SimpleQA / Chinese-SimpleQA / MMLU-Pro / HLE / GPQA） | V4-Pro-Max 显著超领先开源模型；与领先闭源 Gemini-3.1-Pro 仍有差距但已显著缩小 |
| Reasoning | V4-Pro-Max 优于 GPT-5.2、Gemini-3.0-Pro；略逊 GPT-5.4、Gemini-3.1-Pro（约落后前沿 3–6 个月）。V4-Flash-Max 与 GPT-5.2、Gemini-3.0-Pro 相当 |
| Agent | 公开 benchmark 上与 Kimi-K2.6、GLM-5.1 持平；内部评测超 Claude Sonnet 4.5、接近 Opus 4.5 |
| Long-Context | 1M 上下文在学术 benchmark 上超越 Gemini-3.1-Pro |

（图条文本读出的数值——SimpleQA/HLE/Apex Shortlist/Codeforces Rating/SWE Verified/Terminal Bench 2.0/Tolathlon——因 PDF 渲染顺序模糊，此处不强行配对模型，请以原 Figure 1 PDF 为准。）

### 表 4 — Muon 双优化器职责划分（§2.4 "Basic Configurations"）
| 模块 | 优化器 |
|---|---|
| embedding / prediction head | AdamW |
| RMSNorm 权重 | AdamW |
| mHC 静态偏置与门控因子 | AdamW |
| 其余模块（含 attention、MoE、mHC 动态映射） | Muon（Hybrid Newton-Schulz） |

## 与同类对比

- **vs DeepSeek-V3.2（直接前代，§1, §2.3.4）**：V4 在 1M 上下文把 FLOPs 压到 27%/10%、KV cache 压到 10%/7%。V3.2 用 MLA 压缩 KV，V4 进一步用 CSA+HCA 双重压缩 + 稀疏 + FP4 indexer 把量级再下一档。能力上 V4-Flash-Base 已超 V3.2-Base 多数 benchmark。
- **vs 通用注意力 baseline（BF16 GQA8 head-dim 128，§2.3.4）**：1M 上下文 KV cache 仅 ~2%。
- **vs Comet（Zhang et al., 2025b，§3.1 / Figure 5）**：Comet 粗粒度重叠 Dispatch↔L1、L2↔Combine；V4 wave-based 细粒度切分使通信完全藏于计算下。
- **vs Muon 原作（Liu et al., 2025，§2.4）**：V4 区别在用 hybrid Newton-Schulz（双阶段系数）而非单一系数；并因 Q/KV RMSNorm 而弃用 QK-Clip。
- **vs 闭源前沿（GPT-5.4 / Gemini-3.1-Pro / Claude-Opus-4.6，§1）**：能力约落后 3–6 个月；1M 长上下文学术 benchmark 上可超 Gemini-3.1-Pro。

## 跨论文关系（→ MOC 谱系）

- **[[deepseek-v3-technical-report]]** — 直接前身。V4 继承 DeepSeekMoE + MTP，仍属同一 MoE 家族；V3 的 MLA 思想在 V4 演进为 CSA/HCA 双重压缩 + 稀疏。V4-Flash-Base 多数 benchmark 超 V3.2-Base。效率对比基线即 V3.2。
- **[[deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning]]** — R1/GRPO 是 V4 后训练阶段一（Specialist Training）所用的 RL 方法；V4 把 test-time scaling 作为核心动机（§1），是 R1 路线的工程延续。
- **[[kimi-linear-an-expressive-efficient-attention-architecture]]** — 同属长上下文高效注意力方向。Kimi 用线性/混合注意力降复杂度，V4 用压缩+稀疏（CSA/HCA）路线；二者是百万上下文的两条主流架构解法，可对照"压缩+稀疏 vs 线性"范式。
- **[[indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse]]** — V4 的 Lightning Indexer 与 sparse attention 强相关；IndexCache 的跨层索引复用思想可作为 V4 每层独立 indexer 的潜在优化方向（V4 现为每层独立计算 indexer query/score）。
- **[[longspec-long-context-lossless-speculative-decoding-with-efficient-drafting-and-verification]]** — 长上下文 serving 侧。V4 把单 token FLOPs 压到 27%/10%，为 LongSpec 类 speculative decoding 在 1M 上下文下的 drafting/verification 提供了更低成本的基座（MD "相关论文"已链 LongSpec）。

## 局限与边界

1. **fulltext 覆盖边界**：本次深读的 fulltext（46KB）止于 §3.2 TileLang，§3.3–§6（batch-invariant kernel、训练/推理框架细节、预训练 setups 与 instability 缓解、post-training 全流程、benchmark 详表、conclusion/limitations 原文）不在摘录中；上述各节内容系据目录 + 摘要 + MD 图说整合，机制级细节需补原文 PDF。
2. **能力仍落后闭源前沿 3–6 个月**（§1 Reasoning 段），尤其在 knowledge 类评测上仍 trailing Gemini-3.1-Pro；Agent 公开 benchmark 上略逊前沿闭源模型。
3. **FP4 收益当前未兑现**（§1 末）：routed expert 用 FP4，但"FP4×FP8 当前硬件上峰值 FLOPs 与 FP8×FP8 相同"，理论 1/3 效率提升要等未来硬件。
4. **mHC 的 Sinkhorn 开销**：每层每步 20 次迭代投影到 Birkhoff polytope（§2.2，`t_max=20`），虽 M 对乘法封闭保证深栈稳定，但相对标准 HC 增加了一次 matrix-级迭代成本（论文用 recompute + fused kernel 缓解，§3.4.2）。
5. **CSA/HCA 的因果性代价**：为严格保因果，query 只 attend 前面的压缩块，导致 query 无法访问**同一压缩块内**的 token（§2.3.3 "Additional Branch"），需引入 sliding window 旁路（`n_win` 个未压缩 KV）补救局部依赖——这是压缩-稀疏架构的固有边界。
6. **通信-计算重叠有硬件前提**（§3.1 "Observations"）：平衡点 `C/B ≥ 6144 FLOPs/Byte` 一旦带宽达标，再加带宽边际递减；但极端 kernel fusion 带来 power throttling 限制（"Power Budget"），对硬件设计提出新要求——软件红利依赖硬件配合。
