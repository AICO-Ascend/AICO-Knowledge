# Kimi-VL — 技术点深读（DEEP 2026-08-18）
> 全要素深读笔记。独立文件，extract_phase1 重跑不丢。
> 论文：Kimi-VL Technical Report · arXiv:2504.07491v3 (23 Jun 2025)

## 核心问题

开源 VLM 社区在三方面落后于纯语言模型：(1) 规模化与计算效率（主流开源 VLM 如 Qwen2.5-VL、Gemma-3 仍用 dense 架构，未上 MoE）；(2) 先进推理（不支持 long-CoT）；(3) 视觉前端灵活性（早期 MoE-VLM 如 DeepSeek-VL2、Aria 仍用 fixed-size vision encoder，前者仅 4K context、后者细粒度视觉任务弱，且都不支持 long-thinking）。§1 明确点出：缺一个同时整合"结构创新（MoE + native-resolution 视觉）+ 稳定能力 + long-thinking 增强推理"的开源 VLM。

Kimi-VL 给出的答案是：Moonlight MoE LLM（2.8B activated / 16B total，DeepSeek-V3-like）+ MoonViT native-resolution vision encoder（400M，SigLIP-SO-400M 初始化）+ 128K context + 后续 long-CoT SFT & RL。最终在 ~3B 激活参数下，OSWorld、MMBench、MathVista、InfoVQA、MLVU、EgoSchema 等多项超越 GPT-4o。

## 关键创新点

1. **MoonViT：native-resolution 视觉编码器，去 sub-image splitting**（§2.1）
   - 机制：采用 NaViT 的 "Patch n' Pack" 思路——图像切 patch → flatten → 顺序拼成 1D 序列，同一 batch 内可处理不同分辨率图像，无需 LLaVA-OneVision 式的子图切分拼接。
   - 关键技巧：复用 SigLIP-SO-400M 的 learnable fixed-size absolute positional embedding（对其做插值以保留 SigLIP 能力），但随分辨率升高插值不够用 → 在 H/W 维度叠加 2D RoPE，提升高分辨率下细粒度位置表示。两套位置编码协同 + flatten/packing 无缝集成，可与 FlashAttention 的 variable-length sequence attention 共用算子，训练吞吐不打折。
   - 2506 版本进一步 continual-train MoonViT，把单图上限从原始限制提到 **3.2 million pixels（4×）**，直接驱动 V* 83.2、ScreenSpot-Pro 52.8、OSWorld-G 52.5（§4.3）。

2. **MoE 语言解码器 + 中途 checkpoint 续训**（§2.1）
   - 用 Moonlight MoE（2.8B activated / 16B total，架构类 DeepSeek-V3）。不是 from-scratch，而是从 Moonlight 预训练中的一个**中间 checkpoint** 续训——该 checkpoint 已吃 5.2T 纯文本、激活 8K context。随后用 multimodal+text 混合 2.3T tokens 继续预训练（§2.3 的 joint recipe）。这种"加载中间点 + joint 续训"是保留文本能力的关键设计。

3. **MLP Projector：pixel shuffle 压空间**（§2.1）
   - 两层 MLP。先用 pixel shuffle 做 2×2 空间下采样、对应扩展 channel 维，再喂入 MLP 投到 LLM embedding 维度。简单但对 token 经济性重要——native-resolution 下视觉 token 数会爆炸，pixel shuffle 把空间压缩 4×。

4. **4 阶段预训练，共 4.4T tokens**（§2.3, Table 1）
   - **ViT Training（2T + 0.1T）**：CoCa 式双目标 `L = L_siglip + λ·L_caption`（λ=2）。两个 encoder 用 SigLIP SO-400M 初始化，text decoder 用 tiny decoder-only LM 初始化，progressive resolution sampling。观察到 scaling OCR 数据时 caption loss 出现 emergence（text decoder 自发学到 OCR 能力）。之后再 0.1T 仅更新 MoonViT + MLP projector 做对齐，显著降低 MoonViT embedding 在 LLM 中的初始 perplexity，平滑进入 joint 阶段。
   - **Joint Pre-training（1.4T）**：纯文本（同初始 LM 分布）+ 多模态混合，多模态比例渐进上升。前几步只用语言数据。progressive + 前置对齐 = 保留语言能力同时注入视觉。
   - **Joint Cooldown（0.6T）**：高质量文本 + 多模态。文本侧对 math/knowledge/code 用"selected pretrain subset + 合成 QA（proprietary LM 生成 + rejection sampling + validation）"混合；多模态侧除 QA 合成 + 高质量子集 replay 外，还把学术视觉/VL 源过滤改写成 QA。QA 比例刻意压低以避免 overfit QA pattern。
   - **Joint Long-context Activation（0.3T）**：8192→131072 (128K)。RoPE inverse frequency 从 **50,000 重置到 800,000**。分两个子阶段，每个把 context ×4。数据组成：每子阶段长数据占 25%、短数据 replay 75%；长数据含长文本 + 长交织 + 长视频 + 长文档；并合成少量长 QA。结果：NIAH 128K text 87.0、video 91.7（Table 2）。

5. **增强版 Muon 优化器 + 分布式实现**（§2.2）
   - 在原版 Muon 基础上加 weight decay + per-parameter update scale 精调。按 ZeRO-1 策略做分布式实现，memory 最优 + 通信开销低 + 保留算法数学性质。全程（ViT/projector/LLM）都用它。

6. **4D 并行 + 选择性重计算**（§2.5）
   - DP + EP + PP + CP（CP 配合 FlashAttention 切长序列降峰值显存）。PP 划分有讲究：把 Vision Tower + 若干 decoder 层放第一阶段，output layer + 若干 decoder 层放最后阶段，中间层按时间开销均分以减少 bubble。再叠加 ZeRO1 + Selective Checkpointing Activation（只重算低时间开销高显存层），超长序列时扩展重算层集合防 OOM。最终训练吞吐比 7B dense VLM（基于 Qwen2.5-7B）**高约 60%**。

7. **Post-training：两段式 joint SFT + long-CoT SFT + RL**（§2.4）
   - **Joint SFT**：ChatML 格式，仅对 answer + special tokens 监督（system/user prompt masked），format-aware packing 保跨模态位置关系。先 32K 训 1 epoch（LR 2e-5→2e-6），再 128K 训 1 epoch（re-warmup 到 1e-5→1e-6）。
   - **Long-CoT SFT**：小而精的 warmup set，prompt 工程生成 + 类 rejection sampling 验证。覆盖 4 类认知过程：planning（执行前系统列步）、evaluation（中间步批判）、reflection（重审改进）、exploration（考虑替代方案）。
   - **RL**：online policy mirror descent 变体（同 Kimi k1.5），目标函数 Eq.(1) `max_θ E[ E_{(y,z)~πθ}[r] - τ·KL(π_θ(x)||π_{θ_i}(x)) ]`，r∈{0,1}。每轮迭代后新策略变下一轮 reference。三个提效手段：length-based reward 惩罚过长响应（治 overthinking）；curriculum sampling（用难度标签）；prioritized sampling（用 per-instance 成功率）。推理时仍标准 autoregressive，不需专门 planning 算法的并行计算。

8. **Kimi-VL-Thinking-2506：reasoning 与 perception 一体化**（§4.3, Table 4/5）
   - Thinking 在 MathVision +20.1%（36.8→56.9）、MathVista +8.4%、MMMU-Pro +3.2%、MMMU +2.1%。
   - 同时把 Kimi-VL-A3B-Instruct 的感知/视频/长文档/OS-agent 能力整合进 thinking 模型：MMBench 84.4、MMStar 70.4、RealWorldQA 70.0、MMVet 78.1（非推理任务也不退化反而提升）。
   - Token 效率：平均输出 token 缩约 20%（MMMU-val 2.9K→2.4K，MathVision 5.8K→4.4K）；MMBench 平均仅 180 tokens/answer，是前一代 thinking 的 1/3 且精度 +8.4%。
   - 长上下文/视频新 SOTA：VideoMMMU 65.2（开源 SOTA，比 GPT-4o 高 4%）；MMLongBench-Doc 42.1（首个匹配 GPT-4o 的开源模型，比上代 thinking +10%、比 instruct +7%）。

9. **Test-time scaling 可控**（§4.2, Figure 13）
   - 推理时调大 max thinking token 长度持续提升精度：MathVision 1k→18.7%、16k→36.8%；MMMU 1k→49.2%、16k→60.1%。但 MathVista 4k 即饱和（70.9%），说明该任务短 context 已捕获所需推理深度。

## 表格（原文结构化）

### Table 1: 预训练阶段总览（数据组成 / token 量 / 序列长度 / 训练组件）
| Stage | Data | Tokens | Seq Len | Training |
|---|---|---|---|---|
| ViT Training | Alt text / Synthesis Caption / Grounding / OCR | 2T + 0.1T | 8192 | ViT |
| Joint Pre-training | Text, Knowledge, Interleaving, Video, Agent | 1.4T | 8192 | ViT & LLM |
| Joint Cooldown | High-quality Text / Multimodal / Academic Sources | 0.6T | 8192 | ViT & LLM |
| Joint Long-context | Long Text / Long Video / Long Document | 0.3T | 32768→131072 | ViT & LLM |

### Table 2: NIAH recall（text / video haystack，至 128K）
| Haystack Length | (0,2048] | (2048,4096] | (4096,8192] | (8192,16384] | (16384,32768] | (32768,6536] | (6536,131072] |
|---|---|---|---|---|---|---|---|
| text | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 87.0 |
| video | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 91.7 |

### Table 3: Kimi-VL vs SoTA（节选关键 benchmark，Pass@1/Acc）
| Benchmark | GPT-4o | GPT-4o-mini | Qwen2.5-VL-7B | Llama3.2-11B | Gemma3-12B | DeepSeek-VL2 | Kimi-VL-A3B |
|---|---|---|---|---|---|---|---|
| Architecture | - | - | Dense | Dense | Dense | MoE | MoE |
| # Act. Params (LLM+VT) | - | - | 7.6B+0.7B | 8B+2.6B | 12B+0.4B | 4.1B+0.4B | **2.8B+0.4B** |
| # Total Params | - | - | 8B | 11B | 12B | 28B | 16B |
| MMMU (val) | 69.1 | 60.0 | 58.6 | 48 | 59.6 | 51.1 | 57.0 |
| VideoMMMU | 61.2 | - | 47.4 | 41.8 | 57.2 | 44.4 | 52.6 |
| MMBench-EN-v1.1 | 83.1 | 77.1 | 82.6 | 65.8 | 74.6 | 79.6 | 83.1 |
| BLINK | 68.0 | 53.6 | 56.4 | 39.8 | 50.3 | - | 57.3 |
| MathVista | 63.8 | 52.5 | 68.2 | 47.7 | 56.1 | 62.8 | 68.7 |
| MathVision | 30.4 | - | 25.1 | 13.6 | 32.1 | 17.3 | 21.4 |
| InfoVQA | 80.7 | 57.9 | 82.6 | 34.6 | 43.8 | 78.1 | 83.2 |
| OCRBench | 815 | 785 | 864 | 753 | 702 | 811 | 867 |
| ScreenSpot-V2 | 18.1 | - | 86.8 | - | - | - | 92.8 |
| ScreenSpot-Pro | 0.8 | - | 29.0 | - | - | - | 34.5 |
| OSWorld | 5.03 | - | 2.5 | - | - | - | 8.22 |
| WindowsAgentArena | 9.4 | 2.7 | 3.4 | - | - | - | 10.4 |
| MMLongBench-Doc | 42.8 | 29.0 | 29.6 | 13.8 | 21.3 | - | 35.1 |
| Video-MME (w/o / w sub) | 71.9/77.2 | 64.8/68.9 | 65.1/71.6 | 46/49.5 | 58.2/62.1 | - | 67.8/72.6 |
| MLVU (MCQ) | 64.6 | 48.1 | 70.2 | 44.4 | 52.3 | - | 74.2 |
| LongVideoBench | 66.7 | 58.2 | 56.0 | 45.5 | 51.5 | - | 64.5 |
| EgoSchema (full) | 72.2 | - | 65.0 | 54.3 | 56.9 | 38.5 | 78.5 |
| VSI-Bench | 34.0 | - | 34.2 | 20.6 | 32.4 | 21.7 | 37.4 |
| TOMATO | 37.7 | 28.8 | 27.6 | 21.5 | 28.6 | 27.2 | 31.7 |

Kimi-VL 在 24 个 benchmark 中 19 个超过 Qwen2.5-VL-7B（后者激活参数多 2.59×）。

### Table 4: Thinking 系列推理 benchmark（Pass@1）
| Benchmark | GPT-4o | GPT-4o-mini | o1-1217 | Qwen2.5-VL-7B | Gemma-3-27B | Gemma-3-12B | QVQ-72B-Preview | Kimi k1.5 | Kimi-VL-Thinking | Thinking-2506 |
|---|---|---|---|---|---|---|---|---|---|---|
| MathVision (full) | 30.4 | - | 38.1 | 25.1 | 35.5 | 32.1 | - | 35.9 | 38.6 | **36.8→56.9*** |
| MathVista (mini) | 63.8 | 56.7 | 74.8 | 68.2 | 62.3 | 56.4 | 71.0 | 71.4 | 74.9 | 71.3→80.1 |
| MMMU (val) | 69.1 | 60.0 | 74.8 | 58.6 | 64.8 | 59.6 | 77.3 | 70.3 | 70.0 | 61.7→64.0 |
| MMMU-Pro (avg) | 51.7 | 37.6 | 51.1 | 38.1 | - | 32.1 | - | - | - | 43.0→46.3 |
| VideoMMMU | 61.1 | - | 60.2 | 47.0 | 61.8 | 57.2 | - | - | 55.5 | 65.2 |

*2506 版相对原 Thinking 的增益见 §4.3。

### Table 5: Thinking-2506 非推理 benchmark（Acc）
| Benchmark | GPT-4o | Qwen2.5-VL-7B | Gemma3-12B | Kimi-VL-A3B-Instruct | Kimi-VL-A3B-Thinking | Thinking-2506 |
|---|---|---|---|---|---|---|
| MMBench-EN-v1.1 | 83.1 | 83.2 | 74.6 | 82.9 | 76.0 | **84.4** |
| RealWorldQA | 75.4 | 68.5 | 59.1 | 68.1 | 64.0 | 70.0 |
| OCRBench | 815 | 864 | 702 | 864 | 864 | **869** |
| MMStar | 64.0 | 63.0 | 56.1 | 61.7 | 64.2 | **70.4** |
| MMVet | 69.1 | 67.1 | 64.9 | 66.7 | 69.5 | 78.1 |
| MMVU (val) | 67.4 | 50.1 | 57.0 | 52.7 | 53.0 | 57.5 |
| Video-MME (w/ sub) | 77.2 | 71.6 | 62.1 | 72.7 | 66.0 | 71.9 |
| ScreenSpot-Pro | 0.8 | 29.0 | — | 35.4 | — | **52.8** |
| ScreenSpot-V2 | 18.1 | 84.2 | — | 92.8 | — | 91.4 |
| OSWorld-G | - | 31.5 | — | 41.6 | — | **52.5** |
| MMLongBench-Doc | 42.8 | 29.6 | 21.3 | 35.1 | 32.5 | 42.1 |

## 与同类对比

- **vs Qwen2.5-VL-7B（dense, 7.6B+0.7B act）**：Kimi-VL 激活参数仅 2.8B+0.4B（约 1/2.6），却在 24 项中 19 项超越。Qwen2.5-VL 用 fixed-size vision encoder，Kimi-VL 用 native-resolution MoonViT——这是视觉端路线分歧。Qwen 系在 [[qwen3-vl-technical-report]] 进一步迭代，可对照 VLM scaling 策略差异。
- **vs DeepSeek-VL2（MoE, 4.1B+0.4B act, 28B total）**：同为 MoE 但 Kimi-VL 激活更少（2.8B vs 4.5B）、total 更少（16B vs 28B），多数 benchmark 超越；DeepSeek-VL2 仅 4K context、fixed-size encoder，Kimi-VL 128K + native-resolution。
- **vs Gemma-3-12B-IT（dense）**：MMMU 接近（57.0 vs 59.6），但 InfoVQA/OCRBench/ScreenSpot-Pro/OSWorld/EgoSchema 等 Kimi-VL 大幅领先。
- **vs GPT-4o（参考）**：MMBench 平手（83.1）、AI2D 超（84.9 vs 84.6）、MathVista 超（68.7 vs 63.8）、InfoVQA 超（83.2 vs 80.7）、OCRBench 超（867 vs 815）、OSWorld 超（8.22 vs 5.03）、EgoSchema 超（78.5 vs 72.2）、VSI-Bench 超（37.4 vs 34.0）、MLVU 超（74.2 vs 64.6）。仅 ~3B 激活参数。
- **vs long-thinking VLM（QVQ-72B/Max）**：Thinking-2506 在 MathVision 56.9 大幅超过 QVQ-72B-Preview 35.9（Figure 1），以 2.8B 激活重新定义高效多模态思维模型。

## 跨论文关系（→ MOC 谱系）

- **Kimi agentic 谱系**：Kimi-VL 是 Moonshot 开源 VLM 主干；long-thinking 能力直接继承自 Kimi k1.5 的 online policy mirror descent + RL 框架（§2.4 明确"similar as Kimi k1.5"）。后续 [[kimi-k2-open-agentic-intelligence]] / [[kimi-k2-5-visual-agentic-intelligence]] 是 Kimi agentic 主线在更大规模上的延续，Kimi-VL 是其开源小尺寸对应物。
- **VLM/MoE 谱系**：Moonlight MoE LLM（架构类 DeepSeek-V3）+ DeepSeek-VL2/Aria 是 MoE-VLM 早期探索；Kimi-VL 用 native-resolution ViT 修正二者 fixed-size encoder 不足。与 [[deepseek-v4-towards-highly-efficient-million-token-context-intelligence]]、[[kimi-linear-an-expressive-efficient-attention-architecture]] 同属长上下文高效化主线（RoPE base 50K→800K、CP 并行、128K NIAH 验证）。
- **Qwen VLM 对照**：与 [[qwen2-5-vl-technical-report]] / [[qwen3-vl-technical-report]] 是同期开源 VLM 主要竞争/对照对象——dense vs MoE、fixed-size vs native-resolution 两条路线的效率对比。Qwen3-VL 是其后继对比点。
- **视觉 token 表示对照**：[[deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms]] 主张 deeply stacking visual tokens 改善表示；Kimi-VL 走另一条路——native-resolution + pixel shuffle 压空间 + 2D RoPE，是 visual token 表示的"原生分辨率"替代方案。
- **多模态服务对照**：Kimi-VL 作为 MoE VLM workload（128K context + native-res 变长视觉序列 + long-CoT）是 [[efficiently-serving-large-multimodal-models-using-epd-disaggregation]] 这类 EPD disaggregation 服务优化研究的典型目标负载——其 ViT 与 MoE LLM 解耦天然适合 encode/prefill/decode 分离。

## 局限与边界

1. **模型规模受限**（§5）：当前尺寸对高度专业化/领域特定、或强依赖语言能力的极复杂场景仍不够。
2. **推理未达理论上限**：尤其多步推理或更深上下文理解任务，long-CoT 仍有提升空间。
3. **长上下文的注意力层容量瓶颈**：虽给到 128K，但 attention 层参数仅相当于 3B 模型，对极长序列或高体积上下文的高级应用仍不足——这是 MoE"FFN 稀疏但 attention 稠密"的固有结构限制。
4. **MathVision（base Kimi-VL）仍弱**：21.4 落后 Qwen2.5-VL-7B（25.1）和 Gemma-3-12B（32.1），需靠 Thinking 版本才能反超（§4.1.3 承认）。
5. **合成数据幻觉风险**：caption 数据、视频 dense caption 数据均"strictly limit 合成比例"以降低 hallucination，暗示这是已知风险面。
6. **Test-time scaling 不普适**：MathVista 在 4k token 即饱和（§4.2, Figure 13），并非所有任务都受益于更长 thinking——盲目加长 thinking token 有 overthinking 风险（需 length penalty 治理）。
