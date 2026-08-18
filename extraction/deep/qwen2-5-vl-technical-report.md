# Qwen2.5-VL — 技术点深读（DEEP 2026-08-18）
> 全要素深读笔记。独立文件，extract_phase1 重跑不丢。
> 论文：Qwen2.5-VL Technical Report · arXiv:2502.13923v1 [cs.CV], 19 Feb 2025 · Qwen Team, Alibaba Group

## 核心问题

Qwen2.5-VL 要解决的是当下 LVLM/LVLMs 在"夹心饼干中段"困境（§1）：能力广而不精，具体四大瓶颈（§1）：
1. **计算复杂度高** — 原生分辨率输入导致 ViT 注意力随 patch 数二次增长；
2. **上下文受限** — 长视频/长文档难以端到端处理；
3. **细粒度视觉感知差** — 物体定位、文档解析、点定位精度不足；
4. **序列长度变化下性能不稳定** — 不同图像尺寸/FPS 下表现不一致。

同时作者希望把 VLM 从"被动理解"推进为"主动 agent"——能在手机/电脑上执行操作（§1, §3.3.5）。其旗舰 72B 目标对标 GPT-4o 与 Claude 3.5 Sonnet（Abstract; §3.1），并提供 7B/3B 覆盖边缘到高性能场景。

## 关键创新点

1. **ViT 中引入 Window Attention（仅 4 层全注意力）**（§2.1, §2.1.1）
   - 机制：32 层 ViT 中，仅第 {7,15,23,31} 层（Table 1 中 Full Attention Block Indexes）使用全自注意力，其余层用窗口注意力，窗口上限 112×112 像素（对应 8×8 patches，patch stride=14）；小于 112×112 的区域不 padding，保留原分辨率。
   - 效果：计算代价随 patch 数**线性**而非二次增长，使原生分辨率 ViT 在训练/推理上可行。ViT 与 LLM 设计对齐——采用 RMSNorm + SwiGLU 激活（§2.1.1），从零训练 ViT（DataComp + 内部数据初始化，§2.2.2）。

2. **动态 FPS 采样 + 绝对时间编码（MRoPE aligned to absolute time）**（§2.1.2, §2.1.3）
   - 机制：沿用 Qwen2-VL 的 MRoPE（位置嵌入分解为 temporal/height/width 三分量）。文本输入三分量同 ID（等价 1D RoPE）；图像 temporal ID 恒定、height/width 按空间位置赋值；视频 temporal ID 每帧递增。
   - 关键升级：Qwen2-VL 的 temporal ID 绑定**帧序号**，忽略内容速度与绝对时间。Qwen2.5-VL 把 temporal 分量**对齐到绝对时间戳**，使模型通过 temporal ID 之间的**间隔**直接学到时间节奏（tempo），跨不同 FPS 采样率保持一致的时间对齐——**无需额外计算开销**，也无需 textual timestamp 或额外 grounding head。
   - 视频输入：两连续帧打包为一组（3D patch 分割），显著降低送入 LLM 的 token 数（§2.1.1）。

3. **原生动态分辨率（空间）+ 绝对坐标训练**（§2.1.2, §2.2.1 "Grounding Data"）
   - 机制：图像 H/W resize 为 28 的倍数后送 ViT，patch stride=14 → 28×28 对应 2×2 patches；vision-language merger 把**4 个空间相邻 patch 特征**分组拼接，经 2 层 MLP 投影到 LLM embedding 维度（§2.1, Table 1: In Channel=1280, Out Channel=2048/3584/8192）。既压缩序列又支持动态可变长度。
   - 不做坐标归一化：bounding box/point 直接用图像**实际像素尺寸**表示，模型内化 scale 信息；支持 XML/JSON/自定义格式，含 copy-paste 增强、Grounding DINO + SAM 合成；开放词表检测扩到 >10,000 类别，并合成不存在的类别做负样本（§2.2.1）。

4. **预训练语料从 1.2T → 4.1T tokens，三阶段渐进训练**（§1, §2.2.1, §2.2.2; Table 2）
   - 阶段1（Visual Pre-Training, 1.5T tokens, seq 8192）：仅训 ViT，数据=image caption + visual knowledge + OCR；
   - 阶段2（Multimodal Pre-Training, 2T tokens, seq 8192）：全参数解冻，加 interleaved data、VQA、video、grounding、agent、纯文本；
   - 阶段3（Long-Context Pre-Training, 0.6T tokens, seq 32768）：引入长视频/长 agent/长文档，序列长度翻 4 倍以增强长程推理。
   - 负载均衡：因 ViT 已用 window attention 降算力，重点动态打包 LLM 输入序列使各 GPU 算力一致（§2.2.2）。

5. **文档 Omni-Parsing：统一 HTML 格式（QwenVL HTML Format）**（§2.2.1）
   - 机制：把表格/图表/公式/图片 OCR/图片 caption/乐谱/化学公式等元素统一编入 HTML，`data-bbox="x1 y1 x2 y2"` 同时携带布局坐标与内容描述，按阅读顺序排列。一个通用模型取代以往"布局分析+文本抽取+图表解释+插图处理"多模型流水线。
   - 乐谱用 ABC notation、化学式用 SMILES 格式（见 §2.2.1 代码块）；表格真实样本 600 万、图表合成 100 万（matplotlib/seaborn/plotly）。

6. **SFT 数据过滤双阶段流水线 + Rejection Sampling 强化推理**（§2.3.2, §2.3.3）
   - Stage 1：Qwen2-VL-Instag（源自 Qwen2-VL-72B）做层级分类——8 主域（如 Coding/Planning）细分为 30 子类（如 Code_Debugging/Generation/Translation/Understanding）。
   - Stage 2：rule-based + model-based 过滤；reward model 基于 Qwen2.5-VL 系列在多维度（query 复杂度/相关性，answer 正确性/完整性/清晰度/相关性/helpfulness，视觉信息利用）打分。
   - Rejection Sampling：用中间版 Qwen2.5-VL 对带 ground-truth 的数学/代码/VQA 数据生成 CoT，仅保留答案匹配样本；剔除 code-switching/过长/重复；并专门用 rule + model 校验中间推理步是否真正整合视觉信息（§2.3.3）。

7. **Post-training：SFT + DPO 双阶段，ViT 全程冻结**（§2.3, §2.3.4）
   - SFT：~2M 条，纯文本 50% / 多模态 50%（中英为主+多语），ChatML 格式，单/多轮、单/多图；含 General VQA、rejection sampling、Doc/OCR、Grounding、Video、Agent 子集。
   - DPO：仅 image-text + 纯文本，每样本只用一次，对齐人类偏好。

8. **统一 Agent 动作空间（mobile/web/desktop 共享 function call）**（§2.2.1 "Agent Data"）
   - 感知：mobile/web/desktop 截图 + 合成引擎生成 caption 与 UI element grounding 标注。
   - 决策：三平台操作统一为 function call 格式、共享 action space；多步轨迹来自开源 + agent framework 合成（Mobile-Agent 等）；每步由人/模型标注者写推理过程，模型过滤低质推理，防止对 ground-truth 过拟合。

## 表格（原文结构化）

### Table 1 — Qwen2.5-VL 架构配置（§2.1）
| Configuration | 3B | 7B | 72B |
|---|---|---|---|
| **ViT** Hidden Size | 1280 | 1280 | 1280 |
| # Layers | 32 | 32 | 32 |
| # Heads | 16 | 16 | 16 |
| Intermediate Size | 3456 | 3456 | 3456 |
| Patch Size | 14 | 14 | 14 |
| Window Size | 112 | 112 | 112 |
| Full Attention Block Indexes | {7,15,23,31} | {7,15,23,31} | {7,15,23,31} |
| **Merger** In Channel | 1280 | 1280 | 1280 |
| Out Channel | 2048 | 3584 | 8192 |
| **LLM** Hidden Size | 2048 | 3584 | 8192 |
| # Layers | 36 | 28 | 80 |
| # KV Heads | 2 | 4 | 8 |
| Head Size | 128 | 128 | 128 |
| Intermediate Size | 4864 | 18944 | 29568 |
| Embedding Tying | ✓ | ✗ | ✗ |
| Vocab Size | 151646 | 151646 | 151646 |
| # Trained Tokens | 4.1T | 4.1T | 4.1T |

> 备注：三尺寸 ViT 完全同构（1280/32L/16H/窗口112），差异仅在 LLM 规模与 merger 输出维度对齐 LLM hidden。72B 用 80 层、8 KV heads；7B 仅 28 层、4 KV heads。

### Table 2 — 三阶段预训练数据组成（§2.2.2）
| Stage | Data | Tokens | Seq Len | 训练模块 |
|---|---|---|---|---|
| Visual Pre-Training | Image Caption / Knowledge / OCR + 纯文本 | 1.5T | 8192 | ViT |
| Multimodal Pre-Training | Interleaved / VQA / Video / Grounding / Agent + 纯文本 | 2T | 8192 | ViT & LLM |
| Long-Context Pre-Training | Long Video / Long Agent / Long Document | 0.6T | 32768 | ViT & LLM |

### Table 3 — 与 SOTA 总览（节选 72B 关键项，§3.1）
| Benchmark | Prev. Open-source SoTA | Claude-3.5 Sonnet | GPT-4o | InternVL2.5-78B | Qwen2-VL-72B | **Qwen2.5-VL-72B** | 7B | 3B |
|---|---|---|---|---|---|---|---|---|
| MMMUval | 70.1 | 68.3 | 69.1 | 70.1 | 64.5 | **70.2** | 58.6 | 53.1 |
| MMMU-Pro | 48.6 | 51.5 | 51.9 | 48.6 | 46.2 | 51.1 | 38.3 | 31.56 |
| MathVista mini | 72.3 | 67.7 | 63.8 | 72.3 | 70.5 | **74.8** | 68.2 | 62.3 |
| MATH-Vision | 32.2 | — | 30.4 | 32.2 | 25.9 | **38.1** | 25.1 | 21.2 |
| MathVerse mini | 51.7 | — | 50.2 | 51.7 | — | **57.6** | 49.2 | 47.6 |
| MMBench-EN-V1.1 | 87.4 | 80.9 | 83.1 | 87.4 | 86.1 | **88.4** | 82.6 | 77.4 |
| MMStar | 69.5 | 65.1 | 64.7 | 69.5 | 68.3 | **70.8** | 63.9 | 55.9 |
| MME sum | 2494 | 1920 | 2328 | 2494 | 2483 | 2448 | 2347 | 2157 |
| MuirBench | 63.5 | — | 68.0 | 63.5 | — | **70.7** | 59.6 | 47.7 |
| MTVQA | 31.9 | 25.7 | 27.8 | 31.9 | 30.9 | 31.7 | 29.2 | 24.8 |
| MMVet turbo | 74.0 | 70.1 | 69.1 | 72.3 | 74.0 | **76.2** | 67.1 | 61.8 |
| MM-MT-Bench | 7.4 | 7.5 | 7.72 | — | 6.59 | 7.6 | 6.3 | 5.7 |
| MME-RealWorld en | 62.9 | 51.6 | 45.2 | 62.9 | — | **63.2** | 57.4 | 53.1 |

### Table 5 — OCR/Chart/Document（§3.3.2，72B 关键项）
| Benchmark | Claude-3.5 | Gemini 1.5 Pro | GPT-4o | InternVL2.5-78B | **72B** | 7B | 3B |
|---|---|---|---|---|---|---|---|
| CC-OCR | 62.5 | 73.0 | 66.9 | 64.7 | **79.8** | 77.8 | 74.5 |
| OmniDocBench edit en/zh ↓ | 0.330/0.381 | 0.230/0.281 | 0.265/0.435 | 0.275/0.324 | **0.226/0.324** | 0.308/0.398 | 0.409/0.543 |
| InfoVQA test | 74.3 | 81.0 | 80.7 | 84.1 | **87.3** | 82.6 | 77.1 |
| DocVQA test | 95.2 | 93.1 | 91.1 | 95.1 | **96.4** | 95.7 | 93.9 |
| ChartQA test Avg | 90.8 | 87.2 | 86.7 | 88.3 | 89.5 | 87.3 | 84.0 |
| CharXiv RQ/DQ | 60.2/84.3 | 43.3/72.0 | 47.1/84.5 | 42.4/82.3 | 49.7/87.4 | 42.5/73.9 | 31.3/58.6 |
| SEED-Bench-2-Plus | 71.7 | 70.8 | 72.0 | 71.3 | **73.0** | 70.4 | 67.6 |
| OCRBench | 788 | 754 | 736 | 854 | **885** | 864 | 797 |
| VCR En-Hard-EM | 41.7 | 28.1 | 73.2 | — | **79.8** | 80.5 | 37.5 |
| OCRBench_v2 en/zh | 45.2/39.6 | 51.9/43.1 | 46.5/32.2 | 49.8/52.1 | **61.5/63.7** | 56.3/57.2 | 54.3/52.1 |

> 72B 在 OCRBench_v2 较 Gemini 1.5-Pro 英/中分别 +9.6 / +20.6 个百分点（§3.3.2 原文）。

### Table 6 / 7 — Grounding & Counting（§3.3.3）
| Benchmark | Gemini 1.5 Pro | Grounding DINO | Molmo 72B | InternVL2.5-78B | **72B** | 7B | 3B |
|---|---|---|---|---|---|---|---|
| Refcoco val | 73.2 | 90.6 | — | 93.7 | 92.7 | 90.0 | 89.1 |
| Refcoco testA | 72.9 | 93.2 | — | 95.6 | 94.6 | 92.5 | 91.7 |
| Refcoco+ val | 62.5 | 88.2 | — | 90.4 | 88.9 | 84.2 | 82.4 |
| Refcocog test | 76.2 | 87.0 | — | 92.2 | 90.3 | 87.2 | 85.7 |
| ODinW | 36.7 | 55.0 | — | 31.7 | **43.1** | 37.3 | 37.5 |
| PointGrounding | — | — | 69.2 | — | 67.5 | 67.3 | 58.3 |

| CountBench | Gemini 1.5-Pro 85.5 | GPT-4o 87.9 | Claude-3.5 89.7 | Molmo-72B 91.2 | InternVL2.5-78B 72.1 | **Qwen2.5-VL-72B 93.6** |

### Table 8 — Video（§3.3.4；评测上限 768 帧 / 24,576 video tokens）
| Benchmark | Gemini 1.5 Pro | GPT-4o | **72B** | 7B | 3B |
|---|---|---|---|---|---|
| Video-MME w/o sub | 75.0 | 71.9 | 73.3 | 65.1 | 61.5 |
| Video-MME w/ sub | 81.3 | 77.2 | 79.1 | 71.6 | 67.6 |
| Video-MMMU | 53.9 | 61.2 | 60.2 | 47.4 | — |
| MVBench | 60.5 | 64.6 | **70.4** | 69.6 | 67.0 |
| MMBench-Video | 1.30 | 1.63 | **2.02** | 1.79 | 1.63 |
| LongVideoBench val | 64.0 | 66.7 | 60.7 | 56.0 | 54.2 |
| LVBench | 33.1 | 30.8 | **47.3** | 45.3 | 43.3 |
| EgoSchema test | 71.2 | 72.2 | **76.2** | 65.0 | 64.8 |
| MLVU M-Avg | — | 64.6 | **74.6** | 70.2 | 68.2 |
| TempCompass Avg | 67.1 | 73.8 | **74.8** | 71.7 | 64.4 |
| Charades-STA mIoU | — | 35.7 | **50.9** | 43.6 | 38.8 |

### Table 9 — GUI Agent（§3.3.5）
| Benchmark | GPT-4o | Gemini 2.0 | Claude | Aguvis-72B | Qwen2-VL-72B | **Qwen2.5-VL-72B** |
|---|---|---|---|---|---|---|
| ScreenSpot | 18.1 | 84.0 | 83.0 | 89.2 | — | 87.1 |
| ScreenSpot Pro | — | — | 17.1 | 23.6 | 1.6 | **43.6** |
| Android Control High EM | 20.8 | 28.5 | 12.5 | 66.4 | 59.1 | **67.36** |
| Android Control Low EM | 19.4 | 60.2 | 19.4 | 84.4 | 59.2 | **93.7** |
| AndroidWorld SR | 34.5%(SoM) | 26%(SoM) | 27.9% | 26.1% | 6%(SoM) | **35%** |
| MobileMiniWob++ SR | 61% | 42%(SoM) | 61%(SoM) | 66% | 50%(SoM) | **68%** |
| OSWorld | 5.03 | 4.70 | 14.90 | 10.26 | 2.42 | 8.83 |

### Table 4 — 纯文本任务（§3.2，70B+ 对比）
| Benchmark | Llama-3.1-70B | Llama-3.1-405B | Qwen2-72B | Qwen2.5-72B | **Qwen2.5-VL-72B** |
|---|---|---|---|---|---|
| MMLU-Pro | 66.4 | 73.3 | 64.4 | 71.1 | 71.2 |
| MMLU-redux | 83.0 | 86.2 | 81.6 | 86.8 | 85.9 |
| LiveBench-0831 | 46.6 | 53.2 | 41.5 | 52.3 | **57.0** |
| GPQA | 46.7 | 51.1 | 42.4 | 49.0 | 49.0 |
| MATH | 68.0 | 73.8 | 69.0 | 83.1 | 83.0 |
| GSM8K | 95.1 | 96.8 | 93.2 | 95.8 | 95.3 |
| HumanEval | 80.5 | 89.0 | 86.0 | 86.6 | 87.8 |
| MultiPL-E | 68.2 | 73.5 | 69.2 | 75.1 | **79.5** |
| IFEval | 83.6 | 86.0 | 77.6 | 84.1 | **86.3** |

> 多模态训练未牺牲纯文本能力——LiveBench/MultiPL-E/IFEval 均超过 Qwen2.5-72B 基座。

## 与同类对比

- **vs GPT-4o / Claude 3.5 Sonnet**（§3.1, §3.3.2）：72B 在 MMMU 70.2 vs GPT-4o 69.1/Claude 68.3；MathVista 74.8 > 两者；OCR/文档（OCRBench 885、CC-OCR 79.8、OCRBench_v2 61.5/63.7）显著领先。视频上 LVBench 47.3 vs GPT-4o 30.8、MLVU 74.6 vs 64.6、Charades-STA mIoU 50.9 vs 35.7。但部分项仍落后：MMMU-Pro 51.1 < GPT-4o 51.9/Claude 51.5；Video-MME w/ sub 79.1 < Gemini 81.3；LongVideoBench 60.7 < GPT-4o 66.7；OSWorld 8.83 < Claude 14.90。
- **vs InternVL2.5-78B**（开源同档）：在文档、grounding、video 多项超越；但 ODinW 43.1 < Grounding DINO 55.0；PointGrounding 67.5 < Molmo 69.2；Refcoco 系列略低于 InternVL2.5（如 val 92.7 vs 93.7）。
- **vs Qwen2-VL-72B**（自身前代）：ScreenSpot Pro 43.6 vs 1.6（巨幅提升，§3.3.5）；Android Control Low EM 93.7 vs 59.2；预训练语料 1.2T→4.1T；MRoPE 从帧序号升级到绝对时间。
- **架构同侪**：与 InternVL2.5、LLaVA-OneVision 同属 ViT+projector+LLM 范式，但 Qwen2.5-VL 的差异点是 (a) window attention 仅 4 层全注意力、(b) MRoPE 绝对时间对齐、(c) 绝对坐标训练、(d) 统一 HTML omni-parsing。

## 跨论文关系（→ MOC 谱系）

- → [[qwen3-vl-technical-report]]：直接后继。Qwen2.5-VL 的 MRoPE 绝对时间、window attention ViT、绝对坐标 grounding、HTML omni-parsing、统一 agent action space 是 Qwen3-VL 的基线；后续者在此上演进。
- → [[kimi-vl-technical-report]]：同为国产旗舰 VLM，对照 Kimi-VL 的架构选择（如 MoE / 不同 vision encoder 策略）与 Qwen2.5-VL 的"原生动态分辨率 + window attention"路线异同。
- → [[kimi-k2-5-visual-agentic-intelligence]]：Qwen2.5-VL 把 agent 能力（mobile/web/desktop 共享 function call、ScreenSpot Pro 43.6）作为一等公民，与 K2.5 visual agentic intelligence 形成视觉 agent 谱系对照——前者重 grounding+action、后者重 agentic reasoning。
- → [[deepstack-deeply-stacking-visual-tokens-is-surprisingly-simple-and-effective-for-lmms]]：Qwen2.5-VL 用 4-patch 合并 + MLP merger 压缩视觉 token，DeepStack 则主张"深堆叠"视觉 token；两者代表视觉 token 表示的两条路线，可互为消融对照。
- → [[efficiently-serving-large-multimodal-models-using-epd-disaggregation]]：Qwen2.5-VL 通过 window attention + 动态打包平衡训练算力，但服务端长序列多模态推理仍是瓶颈；EPD disaggregation 这类服务侧方法可与之互补——前者优化模型结构，后者优化部署。

## 局限与边界

1. **Window Attention 的局部性**（§2.1.1）：仅 4 层全注意力，跨全局视觉信息的长程依赖可能不足，对需要全图聚合的任务（如复杂图表推理）是潜在瓶颈——CharXiv RQ 仅 49.7（低于 Claude 60.2）可为一例（Table 5）。
2. **Video 评测硬上限**（§3.3.4）：所有视频评测限制 ≤768 帧 / ≤24,576 video tokens，更长视频（小时级以上）的真实表现未在 benchmark 内验证；LongVideoBench 60.7 落后 GPT-4o 66.7 也提示长视频理解仍有差距。
3. **Agent 在线表现仍弱于 Claude**（Table 9）：OSWorld 8.83 < Claude 14.90；AndroidWorld 35% 虽领先但绝对值仍低，动态真实环境鲁棒性有限。
4. **数学/科学顶尖项未达闭源 SoTA**（Table 3,4）：MMMU-Pro 51.1 < Claude 51.5；GPQA 49.0 < Llama-3.1-405B 51.1；MATH 83.0 略低于 Qwen2.5-72B 基座 83.1（多模态训练对纯数学有微弱代价）。
5. **Point grounding 不及专用模型**（Table 6）：PointGrounding 67.5 < Molmo-72B 69.2；ODinW 43.1 远低于 Grounding DINO 55.0——通用模型与专用检测器差距未完全闭合。
6. **MRoPE 绝对时间的依赖**（§2.1.3）：时间节奏学习依赖 temporal ID 间隔，对 timestamp 标注质量敏感；论文未给出在 FPS 极端稀疏或非均匀采样下的鲁棒性分析。
7. **数据合成依赖**（§2.2.1, §2.3.3）：grounding/document/agent 数据大量来自 Grounding DINO/SAM/内部合成引擎，存在合成偏差与 teacher 模型能力上限的传导风险；CoT rejection sampling 仍面临"中间步是否真正整合视觉信息"的未解难题（§2.3.3 末段自承）。
8. **纯文本与多模态的权衡**（Table 4）：MMLU-redux 85.9 < Qwen2.5-72B 86.8、GPQA 49.0 持平，多模态注入对个别纯文本项有轻微回落，未完全做到"无损"。
