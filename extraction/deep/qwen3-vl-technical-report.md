# Qwen3-VL — 技术点深读（DEEP 2026-08-18，全文回填版 2026-08-20）

> 来源说明：本地全文抽取 `extraction/fulltext/qwen3-vl-technical-report.txt` 已回填完整（42 页 / 150008 字符 / arXiv:2511.21631v2，2025-11-27），含 Abstract、§1 Introduction、§2 Model Architecture（§2.1 Interleaved MRoPE / §2.2 DeepStack / §2.3 Video Timestamp）、§3 Pre-Training（§3.1 Recipe + §3.2 Data 9 子节）、§4 Post-Training（§4.1 Recipe / §4.2 Cold Start / §4.3 Distillation / §4.4 RL / §4.5 Thinking with Images / §4.6 Infrastructure）、§5 Evaluation（§5.1–§5.12，Table 2–12 + Figure 2/3）、§6 Conclusion。本深读笔记的所有机制描述与数字均严格回溯至该全文。
>
> 公式合规审计（2026-08-20 复核）：`extraction/formulas.json` 中本 slug 仅收录 1 条 LaTeX = `\frac{-b \pm \sqrt{b^2 - 4ac}}{2a}`，系与本文无关的通用二次公式占位 stub；本文真实公式（square-root-normalized per-token loss 的重加权形式、Interleaved MRoPE 的频率分配、Strong-to-Weak Distillation 的 KL 散度、SAPO 策略梯度）**formulas.json 未收录**。按铁律#2「未收录按 .txt 引用不渲染 `$$`」，本笔记**不渲染任何 `$$` 公式块**；正文出现的 √N / KL(p‖q) / 1 FPS 等均为对原文术语的行内描述性引用（如 §3.1 L67–L69 "square-root-normalized per-token loss"、§4.3 L599–L600 "minimizing the KL divergence"），未引入训练记忆补全的闭式。
>
> 图合规审计：本 slug 共抽取 3 张 PNG，M3 caption 已全部补全（p03 / p17 / p25）。按铁律#1 禁图直读，所有图上下文均消费 `extraction/minimax_captions.json` 文本：**Figure 1（p03，Qwen3-VL 框架图）**织入「关键创新点」开头与 §2 架构；**Figure 2（p17，多语言 OCR 柱状图）**织入「表格」节 §5.4；**Figure 3（p25，NIAH 热图）**织入「关键创新点 #5」与「局限」节。

---

## 核心问题

Qwen3-VL 攻击的核心问题是**「多模态长上下文统一理解」下三组长期被割裂的目标的同时达成**（§Abstract L14–L20）：

1. **纯文本能力退化悖论**：传统 VLM 在注入视觉对齐训练后会牺牲纯文本能力。Qwen3-VL 要求纯文本理解"surpassing comparable text-only backbones in several cases"（§Abstract L15；§1 L45–L47 复述"multimodal models are expected to match or surpass their text-only counterparts on language benchmarks"）。Table 5/6 显示 235B-A22B-Instruct 在 AIME-25 (74.7) / HMMT-25 (57.4) / LiveCodeBench v6 (54.3) 上**全面超过 DeepSeek V3 0324 (46.6 / 27.5 / 45.2) 与 Claude-Opus-4-no-think (33.9 / 15.9 / 44.6)**；Thinking 版在 AIME-25 (89.7) / LiveCodeBench v6 (70.1) 上**超过 OpenAI o3 (medium) (88.9 / 58.6) 与 Claude-Opus-4-thinking (75.5 / 48.9)**，把多模态训练做成对文本能力的*净增益*而非*净损耗*。
2. **长上下文的"多模态一致性"**：现有 VLM 的长窗往往只针对文本，视觉/视频上下文在长程检索、跨段交叉引用（cross-referencing）下严重失真。Qwen3-VL 要求 native 256K-token window *同时*覆盖 text 与 interleaved multimodal 输入，实现"faithful retention, retrieval, and cross-referencing across long documents and videos"（§Abstract L16–L18）。Needle-in-a-Haystack 实测：**256K 训练上下文内 100% 准确率；YaRN 外推至 1M tokens（~2 小时视频）保留 99.5% 准确率**（§5.12.3 L3802–L3805）。
3. **空间-时间-模态三轴的对齐失效**：单图、多图、视频三类输入共享一套位置编码与对齐机制时，时间维度（视频）与空间维度（多图/单图）相互干扰。Qwen3-VL 需要在统一架构内同时强化三轴建模（§Abstract L21–L25；详见「关键创新点 #1/#3」）。

模型族覆盖 **dense（2B / 4B / 8B / 32B）** 与 **MoE（30B-A3B / 235B-A22B）** 两种形态以适配不同 latency–quality 权衡（§Abstract L12–L14；§2 L93–L95）。**旗舰 Qwen3-VL-235B-A22B 总参 235B、每 token 激活 22B**（§2 L95）。视觉编码器默认 **SigLIP2-SO-400M**，2B/4B 小模型用 **SigLIP2-Large (300M)**（§2 L108–L112）。

---

## 关键创新点

> **Figure 1（extraction/minimax_captions.json `qwen3-vl-technical-report-p03.png`）整体描绘**：原生分辨率输入（1248×9376 网页截图 → 11,427 token；256×32 logo → 8 token；1440×800 猫图 → 1,125 token；736×448 多帧小猫视频）经 **SigLIP-2 Vision Encoder** 产出可变长视觉 token，与文本 token 交错后送入 **Qwen3 LM Dense/MoE Decoder**；**DeepStack** 把 ViT 多层视觉 token 注入对应 LLM Block（1, 5, 7, 9, …, N）；Interleaved MRoPE 与文本格式时间戳 `<0.5 second>` 协同编码位置/时间。token 数随原生分辨率线性扩展（小图少 token、密集截图多 token），是 Qwen3-VL 长上下文效率的几何基础。

### 1. Enhanced Interleaved-MRoPE（增强交错多模态旋转位置编码）
- **机制**（§2.1 L117–L127）：Qwen2-VL 引入的 MRoPE 把 embedding 维度分为 temporal (t) / horizontal (h) / vertical (w) 三段并各自分配不同 rotary 频率，导致**频率谱不平衡（imbalanced frequency spectrum）**，已被证明在长视频理解上退化。Qwen3-VL 改用 **interleaved MRoPE**（Huang et al., 2025）：将 t / h / w 沿 embedding 维度**交错分布**到低频与高频带，使每个空间-时间轴在低/高频段**均匀出现**，缓解谱偏置，显著改善长程位置建模。
- **效果**：支撑 native 256K 交错上下文的"faithful retention, retrieval, and cross-referencing across long documents and videos"（§Abstract L16–L18）。Long-video 表现（§5.9, Table 2）：**MLVU-Avg 84.3 (Instruct) / 83.8 (Thinking)，LVBench 67.7 / 63.6**，与 Gemini-2.5-Pro (thinking budget-128) 86.2 / 73.0 同档；255K→1M YaRN 外推后 NIAH 99.5%（见创新点 #5）。

### 2. DeepStack Integration（深层堆叠视觉 token 集成）
- **机制**（§2.2 L130–L138；§2 L114–L116）：直接复用 [[deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms]] (Meng et al., 2024) 的核心思想，但做一处关键扩展——**原 DeepStack 把多尺度视觉输入的 token 堆叠，Qwen3-VL 改为从 ViT 中间层（intermediate layers）抽取**，覆盖从低级到高级的视觉表征。具体地（§2.2 L136–L138 + Figure 1）：从 vision encoder 选 **3 个不同层级** 的特征，由**专用 vision–language merger 模块**投影为视觉 token，**直接加（add）到 LLM 前 3 层的 hidden states**（"added directly to the corresponding hidden states of the first three LLM layers"）——不增加 context length、不增加新参数模块（merger 为已有 MLP 的专门实例）。
- **消融验证**（§5.12.2 Table 12，内部 15B-A2B LLM、200B tokens 预训练、无 post-training）：
  | Metric | Baseline | DeepStack | Δ |
  |---|---|---|---|
  | AVG | 74.7 | 76.0 | +1.3 |
  | InfoVQA | 71.9 | 74.2 | +2.3 |
  | ChartQA | 81.5 | 83.3 | +1.8 |
  | DocVQA | 89.5 | 91.1 | +1.6 |
  | AI2D | 81.8 | 83.2 | +1.4 |
  | OCRBench | 81.0 | 83.6 | +2.6 |
  | MMMU | 52.9 | 54.1 | +1.2 |
  
  印证原文「rich visual information effectively boosts fine-grained visual understanding, such as InfoVQA / DocVQA」——是 DeepStack 论文方法在生产级 VLM 上的正面工业证据。

### 3. Text-Based Time Alignment for Video（基于文本的时间对齐）
- **机制**（§2.3 L140–L153）：从 Qwen2.5-VL 的 T-RoPE（把时间位置 ID 直接绑定到绝对时间）演化为**显式文本时间戳**——每个视频时间 patch 前缀一段格式化文本（如 `<3.0 seconds>`）。原文指出 T-RoPE 的两条限制：(1) 长视频产生**过大且稀疏的 temporal position ids**，退化长时理解；(2) 有效学习要求**对多种 fps 大量均匀采样**，训练数据构造昂贵。文本时间戳方案（Chen et al., 2024b TimeMarker）在训练时**同时生成 seconds 与 HMS (hours:minutes:seconds) 两种格式**，使模型学会解释多种时间码表示。代价是 context length 适度增加。
- **效果**：视频接地任务（video grounding、dense captioning）精度提升；视频整体领先（§5.9）：VideoMMMU 80.0 (Thinking) / 74.7 (Instruct)，MMVU 71.1 / 68.1。

### 4. Square-Root-Normalized Per-Token Loss（平方根归一化 per-token 损失）
- **机制**（§1 L67–L69；§Abstract L26–L27）：原文措辞为"move from a per-sample loss to a **square-root-normalized per-token loss**"——即对每个样本的损失按其 token 数 N 改用 √N 归一化（而非线性 N 或 per-sample）。在多模态联合训练中，这抑制了文本（海量样本、长序列）对视觉（相对少样本）的梯度压制，同时避免对视觉过采样导致文本遗忘——介于"按比例"与"均匀"之间的温和去支配化。
- **formulas.json 状态**：未收录具体闭式。按铁律#2，本文**不渲染 $$**；只引用 §1 L68 原文术语 "square-root-normalized per-token loss" 作为行内描述。
- **效果**：§Abstract L26–L27 "boosts multimodal performance without compromising text capabilities"——直接支撑核心问题 #1「纯文本不退化」（Table 5/6 数据见上）。

### 5. Pretraining 4 阶段扩展至 256K + Post-training 3 阶段（thinking / non-thinking 双分支）
- **预训练 4 阶段**（§3.1 L156–L220 + Table 1 L164–L189）：
  | Stage | Objective | Training | Token Budget | Seq Length |
  |---|---|---|---|---|
  | S0 | Vision-Language Alignment | **Merger only**（ViT + LLM 冻结） | **67B** | 8,192 |
  | S1 | Multimodal Pre-Training | All（ViT + merger + LLM） | **~1T** | 8,192 |
  | S2 | Long-Context Pre-Training | All | **~1T** | 32,768 |
  | S3 | Ultra-Long-Context Adaptation | All | **100B** | **262,144** |
- **后训练 3 阶段**（§4.1 L480–L501）：(i) SFT on long-CoT（先 32K 一轮，再扩到 256K 二轮专注长文档/长视频）；(ii) Strong-to-Weak Distillation（**纯文本数据** fine-tune LLM backbone，KL 散度对齐 logits，off-policy + on-policy 两子阶段，§4.3）；(iii) **RL using SAPO**（Gao et al., 2025，smooth adaptive policy-gradient），分 Reasoning RL（~30K queries，每 query 采样 16 responses，pass rate > 90% 过滤）与 General RL（VQA / caption / OCR / parsing / grounding / clock recognition 多任务）。
- **post-training 算力加码**（§Abstract L30–L31）：原文 allocate additional compute to post-training 阶段，是 thinking 变体在 AIME-25/HMMT-25 等推理任务跃升的关键（Table 6）。
- **Needle-in-a-Haystack 极限验证**（§5.12.3 L3795–L3806 + Figure 3）：在 Qwen3-VL-235B-A22B-Instruct 上构造视频 NIAH——1 FPS 均匀采样、帧分辨率动态调整以维持恒定视觉 token 预算。**30 分钟视频内（对应 256K context）100% 准确率；YaRN 位置外推至 1M tokens（~2 小时视频）保留 99.5% 准确率**。

### 6. 跨架构（Dense + MoE）一致优势 + 跨规模可扩展
- **机制**：在 comparable token budgets 与 latency constraints 下，dense 与 MoE 两条线均采用上述统一架构升级。**Qwen3-ViT**（§5.12.1 Table 11，继续训练的 SigLIP-2 变体）在 1.5T tokens 同 Qwen3-1.7B 联合训练下，OmniBench 53.0 vs SigLIP-2 基线 50.1（+2.9）。
- **规模可扩展**（§5.1 L731–L734）：MMBench-EN thinking 从 2B (79.9) → 4B (84.6) → 8B (85.3)；MMStar thinking 从 2B (68.1) → 8B (75.3)，单调上升。
- **MoE 性能**（§Abstract L31–L33）：235B-A22B 总参 / 22B 激活的"极大总参/极小激活"配置在多模态推理（MMMU 80.6 / MathVista 85.8 / MathVision 74.6 thinking）与长视频（MLVU 83.8 / Video-MME 79.0）上达到 SOTA 同档。

---

## 表格（原文结构化）

### 表 A — 模型族（§Abstract L12–L14；§1 L49–L51；§2 L93–L95）

| 类型 | 参数规格 | 激活参数 | 视觉编码器 | 适用场景 |
|---|---|---|---|---|
| Dense | 2B | 全量 | SigLIP2-Large (300M) | 边缘部署 |
| Dense | 4B | 全量 | SigLIP2-Large (300M) | 边缘部署 |
| Dense | 8B | 全量 | SigLIP2-SO-400M | 中端 |
| Dense | 32B | 全量 | SigLIP2-SO-400M | 中端高质量 |
| MoE | 30B-A3B | 3B active | SigLIP2-SO-400M | 中等延迟高质量 |
| MoE | **235B-A22B** | **22B active** | SigLIP2-SO-400M | 旗舰，低激活延迟 |

> 注：Abstract 记作 "30B-A3B / 235B-A22B"（§Abstract L13），§2 L95 明确"235B total parameters with 22B activated per token"，已确认 22B 激活。早期 frontmatter "235B-A2B" 系笔误。

### 表 B — 预训练 4 阶段（§3.1 Table 1）

见「关键创新点 #5」Table。

### 表 C — 235B-A22B 旗舰关键 benchmark（§5 Table 2，Thinking / Instruct）

| 类别 | Benchmark | Thinking | Instruct | 对照 Gemini-2.5-Pro (tb-128) | 对照 GPT-5 (high) | 对照 Claude Opus 4.1 |
|---|---|---|---|---|---|---|
| STEM | MMMU | 80.6 | 78.7 | 81.7 | 84.2 | 74.4 |
| STEM | MMMU-Pro | 69.3 | 68.1 | 68.8 | 78.4 | 62.7 |
| STEM | MathVistamini | 85.8 | 84.9 | 82.7 | 81.3 | 50.9 |
| STEM | MathVision | 74.6 | 66.5 | 73.3 | 70.9 | 45.8 |
| STEM | MathVersemini | 85.0 | 72.5 | 82.9 | 84.1 | 43.0 |
| STEM | DynaMath | 82.8 | 79.4 | 80.0 | 85.4 | 74.0 |
| STEM | ZeroBench | 4 | 2 | 3 | 2 | 2 |
| Puzzle | VlmsAreBlind | 79.5 | 80.4 | 86.1 | 80.5 | 53.4 |
| Puzzle | LogicVista | 72.2 | 65.8 | 72.0 | 71.8 | 46.3 |
| Puzzle | VisuLogic | 34.4 | 29.9 | 31.6 | 28.5 | 27.2 |
| General VQA | MMBench-EN | 88.8 | **89.3** | 90.1 | 83.8 | 81.3 |
| General VQA | RealWorldQA | 81.3 | 79.2 | 78.0 | 82.8 | 77.3 |
| General VQA | MMStar | **78.7** | 78.4 | 77.5 | 76.4 | 65.2 |
| Alignment | HallusionBench | 66.7 | 63.2 | 63.7 | 65.7 | 53.7 |
| Alignment | MM-MT-Bench | 8.5 | 8.5 | 8.4 | 7.6 | 7.5 |
| Alignment | MIA-Bench | **92.7** | 91.3 | 92.3 | 92.4 | 92.6 |
| Document | DocVQA | 96.5 | **97.1** | 92.6 | 91.5 | 89.6 |
| Document | InfoVQA | 89.5 | 89.2 | 84.2 | 79.0 | 69.9 |
| Document | OCRBench | 875 | **920** | 866 | 810 | 764 |
| Document | CC-OCR | 81.5 | 82.2 | 77.2 | 68.3 | 66.1 |
| Document | CharXiv(DQ) | 90.5 | 89.4 | 94.4 | 89.2 | 79.5 |
| Document | CharXiv(RQ) | 66.1 | 62.1 | 67.9 | **81.1** | 57.8 |
| Document | MMLongBench-Doc | 56.2 | **57.0** | 55.6 | 51.5 | 42.4 |
| 2D/3D | RefCOCO-avg | 92.1 | 91.9 | 74.6 | 66.8 | - |
| 2D/3D | ODinW-13 (mAP) | 43.2 | 48.6 | 33.7 | - | - |
| 2D/3D | SUNRGBD | 53.7 | 56.9 | - | - | - |
| Multi-Image | BLINK | 67.1 | 70.7 | 70.6 | 71.0 | 62.8 |
| Multi-Image | MUIRBENCH | **80.1** | 73.0 | 77.2 | 77.5 | 66.5 |
| Video | Video-MME w/o sub | 79.0 | 79.2 | 85.1 | 84.7 | 77.3 |
| Video | MLVU-Avg | 83.8 | 84.3 | 85.6 | 86.2 | 78.3 |
| Video | LVBench | 63.6 | 67.7 | 73.0 | - | - |
| Video | VideoMMMU | 80.0 | 74.7 | 83.6 | 84.6 | 61.6 |
| Video | MMVU | 71.1 | 68.1 | 68.1 | 73.0 | 68.1 |
| Tool Perception | V* | 85.9 | **93.7+** | 83.8 | 72.8 | 56.7 |
| Tool Perception | HRBench-4K | 84.3 | 85.4+ | 87.3 | - | - |
| Tool Perception | HRBench-8K | 76.6 | 82.4+ | 85.4 | - | - |
| Multi-Modal Coding | Design2Code | 93.4 | 92.0 | 89.2 | 92.5 | 88.9 |
| Multi-Modal Coding | ChartMimic | 78.4 | 80.5 | 83.9 | 62.1 | 41.4 |
| Agent | ScreenSpot Pro | 61.8 | 62.0 | - | - | - |
| Agent | AndroidWorld | 62.0 | 63.7 | - | - | - |
| Agent | OSWorld | 38.1 | 31.6 | - | - | - |
| Agent | WindowsAA | 32.1 | 28.9 | - | - | - |

> 加 `+` 表示使用工具；加粗表示对应列（thinking/instruct）的领先项。Thinking 在 MathVistamini / MathVision / MathVersemini / ZeroBench / LogicVista / VisuLogic 达 SOTA；Instruct 在 non-thinking/低思考预算档多个基准（MathVistamini / MathVision / MathVersemini / DynaMath / ZeroBench / VlmsAreBlind / VisuLogic / VisualPuzzles）领先。MuirBench 80.1 (Thinking) 跨所有模型 SOTA；HallusionBench Thinking 比 Gemini-2.5-pro +3.0、GPT-5 +1.0、Claude Opus 4.1 +6.3（§5.3 L770）；MIA-Bench Thinking 跨所有模型 SOTA，且 math/textual 子项分别超过 GPT-5-high-thinking +10.0 / +5.0（§5.3 L773–L774）。

### 表 D — 中等规模模型（§5 Table 3）

- Qwen3-VL-32B / 30B-A3B 多数指标上**超过 Gemini-2.5-Flash 与 GPT-5-mini**（§5.2 L750–L753）。
- 中等规模 Qwen3-VL 已在推理任务上**超过上一代 Qwen2.5-VL-72B**（§5.2 L751）。
- 32B-Thinking：MMBench 89.5/89.5、RealWorldQA 79.4、MMMU 76.0；32B-Instruct：RealWorldQA 79.0（甚至超过自家 Thinking）。

### 表 E — 小规模模型（§5 Table 4，vs GPT-5-Nano）

- 8B 整体优势；4B 在 DynaMath / VisuLogic 取得最高分；2B 也展现强推理能力。
- MMBench-EN thinking: 2B 79.9 → 4B 84.6 → 8B 85.3；MMStar thinking: 2B 68.1 → 4B 73.2 → 8B 75.3。

### 表 F — 文本中心任务（§5.11 Table 5 / 6）

| Benchmark | 235B-A22B-Instruct | Qwen3-235B-A22B-Instruct-2507 | DeepSeek V3 0324 | Claude-Opus-4 (no-think) |
|---|---|---|---|---|
| MMLU-Pro | 81.8 | 83.0 | 81.2 | **86.6** |
| GPQA | 74.3 | 77.5 | 68.4 | 74.9 |
| AIME-25 | **74.7** | 70.3 | 46.6 | 33.9 |
| HMMT-25 | **57.4** | 55.4 | 27.5 | 15.9 |
| LiveBench 2024-11-25 | 74.8 | **75.4** | 66.9 | 74.6 |
| LiveCodeBench v6 | **54.3** | 51.8 | 45.2 | 44.6 |

| Benchmark | 235B-A22B-Thinking | Qwen3-235B-A22B-Thinking-2507 | OpenAI o3 (medium) | Claude-Opus-4 (think) |
|---|---|---|---|---|
| AIME-25 | 89.7 | **92.3** | 88.9 | 75.5 |
| HMMT-25 | 77.4 | **83.9** | 77.5 | 58.3 |
| LiveCodeBench v6 | **70.1** | 74.1 | 58.6 | 48.9 |

Qwen3-VL-235B-Thinking 在 AIME-25 (89.7) / LiveCodeBench v6 (70.1) 上**超过 OpenAI o3 (medium) (88.9 / 58.6) 与 Claude-Opus-4-thinking (75.5 / 48.9)**（§5.11 L2902–L2904）。

### 表 G — DeepStack 消融（§5.12.2 Table 12，15B-A2B LLM / 200B tokens）

见「关键创新点 #2」Table。

### 表 H — Qwen3-ViT vs SigLIP-2 消融（§5.12.1 Table 11）

| ViT | Clip Bench | ImageNet-1K | Omni OCR | AI2D | RLWDQA | InfoVQA | **Omni** |
|---|---|---|---|---|---|---|---|
| SigLIP-2 | 84.2 | 78.6 | 74.1 | 58.7 | 65.3 | 50.1 | 50.1 |
| Qwen3-ViT | 84.6 | 78.8 | 76.2 | 66.1 | 67.0 | 53.0 | **53.0** (+2.9) |

### 表 I — 训练数据关键量（§3.2 各子节）

| 数据类别 | 量级 | 来源 |
|---|---|---|
| S0 VL Alignment | 67B tokens | §3.1 L193 |
| S1 Multimodal Pre-Training | ~1T tokens | §3.1 L199 |
| S2 Long-Context | ~1T tokens | §3.1 L209 |
| S3 Ultra-Long-Context | 100B tokens | §3.1 L216 |
| OCR samples | **30M in-house** + **30M multilingual synthesized** + **1M internal real-world multilingual images** | §3.2.3 L283–L288 |
| Multilingual OCR languages | **39 (Qwen2.5-VL 10 + 29 added)** | §3.2.3 L286–L287 |
| Document parsing PDFs | 3M Common Crawl (10 doc types × 300K) + 4M internal | §3.2.3 L289–L290 |
| STEM point-grounding samples | 1M | §3.2.8 L431 |
| STEM perception VQA pairs | 2M | §3.2.8 L432 |
| STEM diagram captions | 6M | §3.2.8 L436 |
| K-12/undergrad exercises | **60M+** | §3.2.8 L438–L441 |
| Multimodal long-CoT reasoning samples | **12M+** | §3.2.8 L446 |
| SFT data | **~1,200,000** samples (1/3 text-only + 2/3 multimodal) | §4.2.1 L518–L520 |
| Long-CoT cold start VL:text | ~1:1 | §4.2.2 L567 |
| Thinking-with-Images Stage 1 | ~10k grounding SFT on Qwen2.5-VL-32B | §4.5 L673 |
| Thinking-with-Images Stage 2 | ~120k multi-turn agentic | §4.5 L679 |
| Reasoning RL queries | ~30K（每 query 采样 16 responses） | §4.4.1 L615–L617 |
| Grounding coord system | normalized [0, 1000] | §3.2.4 L343 |

### 表 J — 训练基础设施（§4.6）

- 平台：阿里云 **PAI-Lingjun** AI 计算服务
- 框架：**Megatron-LM**
- 并行：TP + PP + CP + EP + ZeRO-1 DP
- 规模：**up to 10,000 GPUs**
- 部署后端：**vLLM** (PagedAttention) + **SGLang** (structured generation)

---

## 与同类对比

- **vs [[qwen2-5-vl-technical-report]]（直接前作）**：Qwen3-VL 的 MRoPE→interleaved-MRoPE（频率谱从不平衡 → 交错均匀）、T-RoPE→textual timestamp alignment（相位隐式 → 符号显式）、新增 DeepStack（最后一层 → ViT 中间 3 层注入 LLM 前 3 层）、per-sample loss → √N 归一化 per-token loss、绝对坐标 grounding → **normalized [0, 1000]** 坐标系、10 语种 OCR → 39 语种、8K → 256K native 上下文。Qwen2.5-VL 是"相位隐式编码"，Qwen3-VL 在时间轴改为"符号显式编码"，在视觉注入改为"多层残差"，在长窗改为"native 256K 而非外推"。Table 2 显示 Qwen3-VL 在 MMBench-EN (89.3 vs Qwen2.5-VL-72B ~85)、MMMU (78.7 vs 70.2)、OCRBench (920 vs ~870) 上全面提升。
- **vs [[kimi-vl-technical-report]] / [[kimi-k2-5-visual-agentic-intelligence]]（rival VLM/agentic 路线）**：Kimi K2.5 走 early-fusion + MoonViT/MoonViT-3D（SigLIP-SO-400M + NaViT patch-n'--pack 推广到时间维）+ Agent Swarm/PARL；Qwen3-VL 走 late-fusion（vision encoder + merger + LLM 三模块）+ thinking/non-thinking 双分支。Kimi K2.5 在 OCR/InfoVQA/CharXiv 等 vision 子项上仍领先 Qwen3-VL（OCRBench 92.3 vs 87.5 / InfoVQA 92.6 vs 89.5 / CharXiv 77.5 vs 66.1，参见 moc_relations L105）。MoE 配置上 Qwen3-VL 的 235B-A22B（22B 激活）与 Kimi K2 的 MoE 路线在"低激活+大总参"方向一致；Qwen3-VL 的 22B 激活比 Kimi K2 的 1T 总参/小激活更"温和激进"。Agentic 上 Qwen3-VL 32B 在 OSWorld 41 / AndroidWorld 63.7（§5.10 L2756）超过当前基础 VLMs，但 Kimi K2.5 的 Agent Swarm/PARL 在 BrowseComp 等 3×–4.5× 延迟换 +17.8 abs 性能（moc_relations L105）属另一权衡。
- **vs [[deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms]]**：Qwen3-VL 直接集成 DeepStack 作为子模块，但做一处关键扩展——原 DeepStack 堆叠多尺度视觉输入 token，Qwen3-VL 改为从 ViT 中间层抽取（§2.2 L132–L135），并明确注入"the first three LLM layers"（§2.2 L138）。消融 Table 12 验证 +1.3 AVG / +2.3 InfoVQA / +1.6 DocVQA —— DeepStack 论文方法在生产级 VLM 上的工业级正面证据。
- **vs [[efficiently-serving-large-multimodal-models-using-epd-disaggregation]]**：EPD 关注多模态 serving 解耦（prefill/decode 分离），Qwen3-VL 关注模型本身架构/训练；两者正交。Qwen3-VL 的 256K 交错长窗 + 1M YaRN 外推（NIAH 99.5%）正是 EPD 类 serving 系统需要承载的负载。
- **vs [[deepseek-v3-technical-report]] / [[kimi-k3-open-frontier-intelligence]]（frontier 纯文本/混合模型）**：Qwen3-VL 强调其纯文本能力"surpassing comparable text-only backbones in several cases"（§Abstract L15）。Table 5 实证：235B-A22B-Instruct 在 AIME-25 (74.7) / HMMT-25 (57.4) / LiveCodeBench v6 (54.3) 上超过 DeepSeek V3 0324 (46.6 / 27.5 / 45.2)；Table 6 实证 Thinking 版在 AIME-25 (89.7) / LiveCodeBench v6 (70.1) 上超过 OpenAI o3 (medium) (88.9 / 58.6) 与 Claude-Opus-4-thinking (75.5 / 48.9)。这是 VLM 与 frontier LLM 纯文本基线对齐甚至超越的差异化定位点。
- **vs [[deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning]]**：Qwen3-VL 的 RL 路线承 R1 的 outcome-based verifiable reward（§4.4.1 L605–L607 "solutions can be verified deterministically via rules or code executors"），并采用 SAPO 算法（Gao et al., 2025）替代 PPO/GRPO。

---

## 跨论文关系（→ MOC 谱系）

- [[qwen2-5-vl-technical-report]] — **直接前作**。Qwen3-VL 的 MRoPE / T-RoPE / 绝对坐标 grounding 均源自 Qwen2.5-VL，逐项升级（interleaved-MRoPE / textual timestamp / normalized [0,1000]）。
- [[deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms]] — **被集成的子方法**。Qwen3-VL 把 DeepStack 作为 vision–language alignment 核心机制，是 DeepStack 在旗舰 VLM 的工业级验证（Table 12 消融）。
- [[kimi-vl-technical-report]] / [[kimi-k2-5-visual-agentic-intelligence]] — **同代 rival VLM/agentic 路线**。Kimi early-fusion + Agent Swarm/PARL；Qwen3-VL late-fusion + thinking/non-thinking 双分支。
- [[efficiently-serving-large-multimodal-models-using-epd-disaggregation]] — **下游 serving 正交关系**。Qwen3-VL 的 256K 交错长窗 + 1M YaRN 外推是 EPD 类多模态 serving 系统的典型负载。
- [[deepseek-v3-technical-report]] / [[kimi-k3-open-frontier-intelligence]] — **frontier 基线对照**。Qwen3-VL 的纯文本能力对标甚至超越 text-only frontier backbones（Table 5/6）。
- [[deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning]] — **RL 路线源头**。Qwen3-VL 的 Reasoning RL 承 R1 的 verifiable-reward 思路，采用 SAPO 算法实现。
- [[muon-is-scalable-for-llm-training]] — **优化器谱系对照**（间接）。Qwen3-VL 用 SAPO 而非 Muon 系列，但同属"为大规模训练定制的优化算法"。
- 基因位：Qwen-VL 系列 → Qwen2.5-VL → **Qwen3-VL**（当前）；侧支吸收 DeepStack；与 Kimi-VL/K2.5 形成 VLM/agentic 双线对照。

---

## 局限与边界

1. **256K 长窗的真实成本**：native 256K 交错上下文的推理显存、KV cache 成本原文未量化。NIAH 给出 256K 内 100% 与 1M 外推 99.5%（§5.12.3 + Figure 3），但**未给出 256K→1M 之间的衰减曲线**（仅两端点），远端有效性的中间段未披露。
2. **YaRN 外推的副作用**：1M tokens 外推通过 YaRN-based positional extension 实现（§5.12.3 L3804），但原文未给出 YaRN 外推对非 NIAH 任务（如长视频推理、长文档 QA）的影响。MMLongBench-Doc 57.0 (Instruct) 已是 SOTA，但相对 256K 训练分布的远端任务未见独立消融。
3. **Square-root reweighting 的边界**：√N 归一化是启发式（§1 L67–L69）。原文未给出与 linear / uniform / 温度调节等替代方案的消融对比，也未说明在何种数据配比下该启发式失效（极端不平衡时 √N 仍可能不足以保护少数模态）。formulas.json 亦未收录闭式，无法 LaTeX 双源校验。
4. **Text-based time alignment 的精度边界**：把时间戳符号化为文本（如 `<3.0 seconds>` 或 HMS 格式），对帧率极高或时间戳分辨率要求细于 token 粒度的场景（如毫秒级同步定位）存在天然离散化误差；原文仅说"modest increase in context length"（§2.3 L151–L152），未给时间定位的分辨率下限。
5. **视频评测的公平性**：§5.9 L2746–L2748 明确"comparison cannot guarantee full fairness due to resource and API limitations, which constrained the number of input frames used during evaluation: **512 for Gemini 2.5 Pro, 256 for GPT-5, and 100 for Claude Opus 4.1**"——Qwen3-VL 用 2048 帧上限、224K 总 token 预算，对照模型帧数显著更少。Video-MME / VideoMMMU 上 Gemini-2.5-Pro (85.1 / 83.6) 仍领先 Qwen3-VL (79.2 / 80.0) 部分受此影响。
6. **MoE 路由稳定性**：235B-A22B 这种"极大总参 / 极小激活（22B/235B ≈ 9.4%）"配置的专家负载均衡、路由坍塌、长尾专家利用率原文未讨论。基础设施仅提及 10,000 GPUs + EP 并行（§4.6）。
7. **纯文本超越的可比性**："surpassing comparable text-only backbones in several cases"（§Abstract L15）的"in several cases"在 Table 5/6 中体现为 AIME-25 / HMMT-25 / LiveCodeBench v6 等**推理-编码强任务**上超越，但在 MMLU-Pro (81.8 vs Qwen3 83.0 vs Claude 86.6) / GPQA (74.3 vs Qwen3 77.5) / Arena-Hard V2 (77.4 vs Qwen3 79.2) 等**知识/对齐**任务上仍落后于纯文本 frontier；PolyMATH (45.1 vs Qwen3 50.2) 等多语种数理任务也落后。**"several cases" 非"全面超越"**。
8. **DeepStack 的层级选择**：原文 §2.2 L138 明确"the first three LLM layers"对应"3 distinct levels of the vision encoder"——比之前 Abstract 阶段"multi-level"模糊表述精确，但**为何选前 3 层而非更深、层间距如何定**未给设计准则。消融 Table 12 也仅在 15B-A2B 上做，235B 规模的 DeepStack 收益未单独消融。
9. **Agent 任务的非全面覆盖**：Table 2 中 OSWorld / WindowsAA / AndroidWorld / OSWorldG 的对照模型大量为 "-"（缺失），说明 Qwen3-VL 在 agentic 评测上的对照面比 STEM/VQA 窄得多，"SOTA across multiple tasks"的claim局限。
10. **未涉及项**：原文未给出多模态幻觉率的系统性量化（HallusionBench 66.7 仅一bench）、安全对齐的 red-team 评测、跨语言 OCR 39 语种的具体语种列表与每语种精度分布（仅 Figure 2 给 32/39 > 70% 的总体阈值，M3 caption 显示 Romanian 最低 ~71% / Swedish 最高 ~97%）。
