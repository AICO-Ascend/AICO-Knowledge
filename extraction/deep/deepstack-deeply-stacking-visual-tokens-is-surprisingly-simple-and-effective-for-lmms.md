# DeepStack: Deeply Stacking Visual Tokens is Surprisingly Simple and Effective for LMMs — 技术点深读（DEEP 2026-08-18）
> 独立文件，extract_phase1 重跑不丢。整篇论文一体化深读：图/表/公式/文本交织分析，图表解读织进核心问题与创新点。
> 论文：DeepStack: Deeply Stacking Visual Tokens is Surprisingly Simple and Effective for LMMs · arXiv:2406.04334v1 (6 Jun 2024) · Fudan / Microsoft

## 核心问题

主流大型多模态模型（LMMs）——如 LLaVA-1.5 / LLaVA-Next——把所有视觉 token 拉平为一条 1D 序列，作为 prefix 注入 LLM 的**输入层（0-th layer）**（§1, §3.1, Eq. 2）。Figure 1（p.1）左半 "Sequence LMMs" 面板（M3 解读：高/低分辨率 token 经 Downscale 后被一次性 concat 进单一 Transformer Layers ×L 的输入），正是这一痛点的图示化：所有视觉信息必须挤进同一个入口序列。

这种 "Sequence LMMs" 范式带来两个根本痛点：

1. **计算/内存随视觉 token 数线性膨胀**。高分辨率图像、多帧视频场景下视觉 token 数（576 → 2880 → 14400）急剧增长，self-attention 在输入层对这些 prefix token 的开销与序列长度成二次关系（§1: "significantly increases computation and memory costs ... particularly significant when it comes to high-resolution images and multi-frame videos"）。
2. **token 压缩损害细粒度信息**。既有缓解手段——spatial grouping/pooling（如 Qwen-VL）、feature-dim 拼接（如 Sphinx/MoE 视觉专家）、Q-Former/Perceiver/Abstractor 重采样——都在 "compute overhead vs. information flow" 之间做权衡，本质上都要牺牲细粒度视觉信息；MM1 的系统消融也未发现这些方案有显著差异（§1: "all these works inherently sacrifice fine-grained visual information"；§2 LMMs 段）。而多裁剪（multi-crop, LLaVA-Next / InternLM-XComposer2-4KHD）虽然堆了数倍 token 但代价高昂。

DeepStack 的发问：**能否在不增加 context length、不改架构的前提下，把更多/更细的视觉 token 送进 LLM？** 关键洞察是放弃 left-to-right 视角，转而从 bottom-to-top 看 transformer decoder 层——把 LLM 的早期层当作"视觉 token 编码器"使用（§1: "we adopt a novel bottom-to-top perspective, revealing that they constitute a hierarchical arrangement of transformer layers"）。Figure 1（p.1）中半面板（M3：token 被重组为编号 1–4 的网格组，从底向上经残差连接 1→l_a, 2→l_b, 3→l_c, 4→l_d 注入对应 transformer layer）即这一 bottom-to-top 路由的可视化；右半雷达图（M3：DeepStack-V 与 DeepStack-L 在 VQAv2/GQA/TextVQA/DocVQA/InfoVQA/SEED/POPE 七轴上均包住 vis_tok=576/2880 的 Sequence 基线）则预告"4× token、同 context length、显著优势"的核心结论。

## 关键创新点

1. **DeepStack 残差注入策略（核心机制，§3.2, Eq. 4-5, Algorithm 1）**
   将高分辨率图像 patch 经 vision encoder + connector 后的 token 集合 `X^stack`，通过 `Sampling2D`（spatial dilation，2D 空间最近邻抽样）切成 N 组，每组长度等于全局视觉 token `X` 的长度。然后在 LLM 的若干早期层（自底向上）通过**残差加法** `H[vis_pos] += X^stack[i]` 注入；中后期层恢复为常规 sequence modeling。算法伪代码（Algorithm 1）极其简洁：在标准 transformer forward 循环里加一行 `if idx >= lstart & (idx - lstart) % n == 0: H[vis_pos] += X^stack[(idx-lstart)//n]`。`lstart` = 起始层，`n` = 注入间隔。**无架构改动、无新增可训练参数、context length 不变**。Figure 2（p.4）左半 "DeepStack-L" 面板（M3：低分辨率 token 进首层 LLM Block，高分辨率 token 的 2–5 neighbor 组逐层向更深 LLM Block 与文本 token 并行注入）即此机制的端到端数据流图。

2. **双相处理：早期层当视觉编码器，后期层做 sequence modeling（§3.2, Eq. 8）**
   DeepStack 把 `H^L` 的计算显式写成两阶段：早期 `P^{V1..Vn}` 像 encoder 一样反复残差增强视觉 token；后期 `P^L` 做常规 prefix sequence modeling（Eq. 8 同时被作者标注为 "Early layers for visual tokens encoding / Deep layers for LLM sequence modeling"）。"dual-phase processing fully leverages the LLM's capabilities by combining both encoding and sequence modeling"（§3.2 末）。这点是 DeepStack 区别于 Sequence Concat / Dimension Concat 的本质——后者要么加长序列（Eq. 6 `P(SeqCat[X, X^stack])`）要么在特征维拼接（Eq. 7 ≈ `P(M1(f)+M2(f^hires))`），都只在输入层一次性注入。

3. **DeepStack-L（注入 LLM 层）与 DeepStack-V（注入 ViT 层）双变体（§3.2, Fig. 2）**
   - **DeepStack-L**：把高分辨率 token 残差注入 LLM 的 decoder 层（默认 block length=1，等距注入）。
   - **DeepStack-V**：把同一思想搬到 vision encoder 内部——用 `PatchEmbedding + 前 N 层 ViT encoder` 做 tokenization，后 4 层做 DeepStack 残差注入。Figure 2（p.4）右半 "DeepStack-V" 面板（M3：Patch Embed + 单个 ViT Block 之后，2–5 视觉 token 组沿后续 ViT Blocks 注入，再经 Connector 入 LLM）即此变体的双流（global shallow + stacked hi-res deeper）数据流。需要 unfreeze vision encoder（§4.1: "We unfreeze the vision encoder in DeepStack-V and DeepStack-L-HD while freezing it in DeepStack-L for a fair comparison"）。
   - **DeepStack-L-HD**：在 LLaVA-Next（1344 eff. res.）基础上做 DeepStack，14400 视觉 token / 2880 context length。

4. **2D Spatial 采样优于 1D/Grid（§4.3, Table 5, Fig. 5）**
   三种组织方式对比（`✓ 2d Spatial` default）：2d Spatial (AVG 51.1) > 1d Sequential (49.3) > 2d Grid (49.0)；保持图像空间相干性（如 4-neighbor 采样）最佳。Figure 5（p.9，M3：三个 4×4 色块网格——2d Spatial 每个 2×2 块同色，保持 layer 间局部 2D 相干；1d Sequential 按 1→4 线性铺排，破坏空间局部性；2d Grid 切成 2D 子网格，棋盘式交错）直观解释了 Table 5 的排序：几何感知的采样让每层注入的 token 是上一层的最近邻，跨层递进形成"由粗到细"的层级视觉编码。同时高/低分辨率图都用 Resize（而非 Pad-Resize）保持 aspect ratio 一致也有助于（Consistent `✓` vs `None` = 49.1）。

5. **增益来自高分辨率 token，而非残差机制本身（§4.3, Table 6）**
   关键对照实验：把 Dummy（重复原始 token）当作 `X^stack` 注入——AVG 仍为 49.1，无提升；只有 Hi-Res 才到 51.1。"the performance boost in DeepStack comes from the high-resolution tokens, not from the residual connections"（§4.3）。排除"残差路径本身带来正则化收益"的混淆解释。这也回扣 Figure 4（p.10，M3：LLaVA-1.5 vs DeepStack 同用 576 context token，DeepStack 在卡片小字 / "Welcome to Washington DC" 标牌 / 糖果酒瓶品牌 / 手机 UI 这类细粒度问答上答对，而 LLaVA-1.5 幻觉或漏答；中段 detailed captioning 蓝色=正确、红色=幻觉，DeepStack 误述更少；底部七边形雷达 DeepStack 包住 LLaVA-1.5）——之所以能保住细节，正是因为注入的是真实 hi-res token 而非残差路径本身。

6. **最佳性能/效率平衡点（§4.3, Table 7）**
   对比四种 token enhancement：Dimension Concat (576 tok, AVG 49.4) / Hi-Res String (2304 tok, 50.7) / Global+Hi-Res String (2880 tok, 51.0) / **DeepStack (576 context tok, 2880 effective, AVG 51.1)**。DeepStack 用 1/5 的 context length 达到与 2880-token string 方案相当甚至略优的效果——对照 Figure 1（p.1）雷达图（M3：DeepStack 两变体在七轴上反超 2880-token Sequence 基线），数字与图一致。

7. **unfreeze vision encoder 后 DeepStack 才"释放威力"（§4.3, Table 8, Table 11）**
   单独 unfreeze backbone（无 DeepStack）AVG 反而略降（49.1 → 48.5）；DeepStack + unfreeze 升至 52.4。"because of the deep interaction between visual tokens and the LLM decoder"——只有让 encoder 适配 DeepStack 的多层级注入语义，深层交互才成立。Table 11 进一步给出 DeepStack-L⋆（finetune encoder）：7B 的 VQAv2 79.5→81.1、MMMU 35.7→37.1，13B 的 GQA 64.2→65.1、DocVQA 41.5→43.1，全表 9 个指标几乎全部上扬。

8. **LLM 早期层天然适合处理视觉 token（§4.3, Fig. 3）**
   Figure 3（p.8，M3：三个并列折线图）——(a) 起始层 0–24，score 在 0–8 层稳定 ~49，到第 24 层骤降，说明越早注入越好；(b) 注入间隔 s=0–5，s=1–2 处达峰 ~51 后缓慢回落；(c) stacking 层数 N=0–9，N=4 处达峰 ~51，过少过多都伤。即在 Phi-3（32 层）上把视觉 token 注入第 0/4/8/... 层并零初始化对应 input embedding：插入到第 8 层之前性能波动可接受，超过中点（>16 层）显著下降；任意 stacking interval 都带来稳定提升；stacking 层数越多越好，4 层最佳。这三组消融共同锁定经验最优配置：起始层 ≤8、间隔 ~1–2、stacking 4 层。

## 表格（原文结构化）

### Table 1 — 9 benchmarks 主对比（§4.2）
| Method | LLM | Eff.Res | Vis.Tok | Cxt.Len | PT | SFT | VQAv2 | GQA | TextVQA‡ | DocVQA‡ | InfoVQA‡ | SEED | POPE | MMMU‡ | MMVet |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| LLaVA-1.5 | Vicuna-7B | 336 | 576 | 576 | 558K | 665K | 78.5* | 62.0* | 58.2 | 28.1 | 25.8 | 58.6 | 85.9 | 35.3 | 30.5 |
| LLaVA-1.5 | Vicuna-13B | 672 | 576 | 576 | 558K | 665K | 80.0* | 63.3* | 61.3 | 30.3 | 28.4 | 61.6 | 85.9 | 34.8 | 35.4 |
| LLaVA-Next | Vicuna-7B | 672 | 2880 | 2880 | 558K | 765K | 81.8* | 64.2* | 64.9 | 74.4* | 37.1* | 64.7 | 86.5 | 35.1 | 44.1 |
| LLaVA-Next | Vicuna-7B | 672 | 2880 | 2880 | 558K | 765K | 82.8* | 65.4* | 66.9 | 77.5* | 44.5* | 65.6 | 86.2 | 35.9 | 49.1 |
| DeepStack-V | Vicuna-7B | 672 | 2880 | 576 | 558K | 665K | 80.4* | 64.1* | 63.5 | 41.0 | 30.0 | 62.3 | 87.6 | 34.9 | 33.0 |
| DeepStack-V | Vicuna-13B | 672 | 2880 | 576 | 558K | 665K | 81.1 | 64.2* | 63.9 | 41.7 | 33.1 | 63.0 | 86.6 | 34.7 | 31.1 |
| DeepStack-L | Vicuna-7B | 672 | 2880 | 576 | 558K | 665K | 79.5* | 63.1* | 62.4 | 39.1 | 29.8 | 60.6 | 86.7 | 35.7 | 29.9 |
| DeepStack-L | Vicuna-13B | 672 | 2880 | 576 | 558K | 665K | 80.9* | 64.2* | 64.6 | 41.5 | 33.0 | 63.5 | 87.7 | 35.2 | 35.9 |
| DeepStack-L-HD† | Vicuna-7B | 1344 | 14400 | 2880 | 558K | 748K | 82.0* | 65.2* | 66.7 | 78.8* | 41.2* | 63.6 | 86.5 | 35.6 | 37.5 |
| DeepStack-L-HD† | Vicuna-13B | 1344 | 14400 | 2880 | 558K | 748K | 83.0* | 66.2* | 68.7 | 81.0* | 45.2* | 65.1 | 86.7 | 33.4 | 39.3 |

> 核心对照：DeepStack-L-HD-7B vs LLaVA-1.5-7B（同 665K SFT 量级体系）—— TextVQA **+4.2**、DocVQA **+11.0**、InfoVQA **+4.0**（§1 摘要数字）。DeepStack 7B / 13B 在 9 benchmarks 上 9-bench 平均分别 **+2.7 / +2.9**；用 1/5 context length 即可逼近 full-context baseline（§Abstract）。DocVQA/InfoVQA/TextVQA 三列正是 Figure 4（p.10）定性对比所覆盖的细粒度任务类别。

### Table 2 — Text-Oriented benchmarks（§4.2）
| Method | LLM | Vis.Tok | Cxt.Len | PT | IT | ChartQA‡ | DocVQA‡ | InfoVQA‡ | Multi DocVQA‡ | TextVQA‡ |
|---|---|---|---|---|---|---|---|---|---|---|
| LLaVA-1.5 | Vicuna-7B | 576 | 576 | 558K | 665K | 18.2 | 28.1 | 25.8 | 16.7/7.2 | 58.2* |
| LLaVA-Next | Vicuna-7B | 2880 | 2880 | 558K | 765K | 54.8 | 74.4 | 37.1 | 44.4/31.3 | 64.9 |
| DeepStack-V | Vicuna-7B | 2880 | 576 | 558K | 665K | 20.6 | 41.0 | 30.0 | 23.0/11.0 | 63.5* |
| DeepStack-L | Vicuna-7B | 2880 | 576 | 558K | 665K | 21.0 | 39.3 | 30.1 | 22.2/10.5 | 64.5* |
| DeepStack-L | Vicuna-13B | 2880 | 576 | 558K | 665K | 21.2 | 43.1 | 34.0 | 24.8/12.2 | 65.2* |
| DeepStack-HD† | Vicuna-7B | 14400 | 2880 | 558K | 748K | 56.3 | 78.8 | 41.2 | 48.2/37.7 | 66.7 |
| DeepStack-HD† | Vicuna-13B | 14400 | 2880 | 748K | 748K | 64.0 | 81.0 | 45.2 | 49.4/39.1 | 68.7 |

### Table 3 — Zero-shot Video QA（§4.2）
| Method | EgoSchema | Next-QA | MSVD(Cas/Des/Tem) | ActivityNet(Acc/Score) |
|---|---|---|---|---|
| LLaVA-1.5-7B | 35.4 | 59.5 | 68.9/55.5/59.6 | 75.5/4.0 |
| DeepStack-L-7B | 38.4 | 61.9 | 69.4/55.5/61.0 | 76.0/4.0 |
> 6 帧 uniform sampling 拼成 2×3 grid，零样本直评视频 QA。DeepStack 因有效分辨率更高而稳定胜出（§4.2: "more visual information is included with the same context length"）。

### Table 4 — DeepStack-V 消融：N 个 ViT encoder 层用于 tokenization（§4.3）
| N Layers before DeepStack | Ft Enc. | GQA | POPE | SEED | TextVQA | DocVQA | ChartQA | InfoVQA | AVG |
|---|---|---|---|---|---|---|---|---|---|
| None(baseline, frozen) | ✗ | 62.5 | 85.5 | 63.5 | 56.7 | 31.7 | 15.8 | 28.3 | 49.1 |
| None | ✓ | 62.4 | 85.8 | 64.0 | 56.1 | 27.5 | 15.3 | 28.3 | 48.5 |
| PatchEmbed+0 Enc | ✓ | 56.9 | 80.8 | 54.9 | 44.4 | 13.7 | 12.3 | 25.3 | 41.2 |
| PatchEmbed+4 Enc | ✓ | 58.7 | 83.1 | 57.4 | 48.2 | 17.0 | 13.2 | 26.1 | 43.4 |
| PatchEmbed+8 Enc | ✓ | 60.4 | 84.2 | 59.7 | 51.8 | 23.1 | 14.7 | 26.6 | 45.8 |
| PatchEmbed+12 Enc | ✓ | 61.8 | 85.5 | 62.1 | 55.5 | 29.3 | 16.0 | 26.2 | 48.1 |
| PatchEmbed+16 Enc | ✓ | 62.9 | 86.3 | 63.9 | 59.1 | 36.9 | 18.2 | 29.3 | 50.9 |
| PatchEmbed+20 Enc | ✓ | 62.8 | 86.1 | 64.0 | 60.1 | 38.4 | 17.1 | 30.6 | 51.3 |
> ViT-Large 共 24 层；用前 16–20 层做 tokenization、后 4 层做 DeepStack 时反超 baseline。该消融对应 Figure 2（p.4）右半 DeepStack-V 数据流——Patch Embed + 前 N 层 ViT 作 tokenizer、剩余层做残差堆叠。

### Table 5 — 采样/一致性消融（§4.3）
| Consistent | Sampling | GQA | POPE | SEED | TextVQA | DocVQA | ChartQA | InfoVQA | AVG |
|---|---|---|---|---|---|---|---|---|---|
| None | None | 62.5 | 85.5 | 63.5 | 56.7 | 31.7 | 15.8 | 28.3 | 49.1 |
| ✗ | 2d Spatial | 62.2 | 85.1 | 62.3 | 58.1 | 35.1 | 16.4 | 30.1 | 49.9 |
| ✓ | 2d Spatial | 63.0 | 86.4 | 62.9 | 58.8 | 38.7 | 17.2 | 30.8 | **51.1** |
| ✓ | 2d Grid | 60.6 | 86.2 | 61.2 | 57.1 | 33.2 | 16.4 | 28.6 | 49.0 |
| ✓ | 1d Sequential | 61.6 | 86.2 | 61.9 | 57.1 | 33.1 | 15.2 | 30.0 | 49.3 |

### Table 6 — Hi-Res vs Dummy 注入消融（§4.3）
| Tok.Enhance | Stack Tok. | GQA | POPE | SEED | TextVQA | DocVQA | ChartQA | InfoVQA | AVG |
|---|---|---|---|---|---|---|---|---|---|
| None | None | 62.5 | 85.5 | 63.5 | 56.7 | 31.7 | 15.8 | 28.3 | 49.1 |
| DeepStack | Dummy | 62.2 | 85.3 | 63.8 | 56.9 | 31.2 | 15.4 | 28.8 | 49.1 |
| DeepStack | Hi-Res | 63.0 | 86.4 | 62.9 | 58.8 | 38.7 | 17.2 | 30.8 | **51.1** |

### Table 7 — Token Enhancement 策略对比（§4.3）
| Tok.Enhance | N Tok. | Eff.Tok. | GQA | POPE | SEED | TextVQA | DocVQA | ChartQA | InfoVQA | AVG |
|---|---|---|---|---|---|---|---|---|---|---|
| None | 576 | 576 | 62.5 | 85.5 | 63.5 | 56.7 | 31.7 | 15.8 | 28.3 | 49.1 |
| Dimension Concat | 576 | 2880 | 59.5 | 86.3 | 62.9 | 56.4 | 35.9 | 16.4 | 28.5 | 49.4 |
| Hi-Res String | 2304 | 2304 | 61.8 | 86.2 | 62.1 | 55.0 | 43.5 | 16.2 | 30.4 | 50.7 |
| Global+Hi-Res String | 2880 | 2880 | 62.3 | 86.4 | 62.6 | 54.7 | 43.3 | 16.7 | 31.2 | 51.0 |
| **DeepStack** | **576** | 2880 | 63.0 | 86.4 | 62.9 | 58.8 | 38.7 | 17.2 | 30.8 | **51.1** |

### Table 8 — Fine-tuning vision encoder 消融（§4.3）
| Tok.Enhance | Ft Enc. | GQA | POPE | SEED | TextVQA | DocVQA | ChartQA | InfoVQA | AVG |
|---|---|---|---|---|---|---|---|---|---|
| None | ✗ | 62.5 | 85.5 | 63.5 | 56.7 | 31.7 | 15.8 | 28.3 | 49.1 |
| None | ✓ | 62.4 | 85.8 | 64.0 | 56.1 | 27.5 | 15.3 | 28.3 | 48.5 |
| DeepStack | ✗ | 63.0 | 86.4 | 62.9 | 58.8 | 38.7 | 17.2 | 30.8 | 51.1 |
| DeepStack | ✓ | 63.1 | 86.8 | 63.9 | 61.1 | 41.2 | 18.9 | 31.5 | **52.4** |

### Table 10 — 训练超参（§A.2）
| Hyper-param | PT | DeepStack SFT | DeepStack-V SFT | DeepStack-HD SFT |
|---|---|---|---|---|
| global batch size | 256 | 128 | 128 | 128 |
| lr | 1e-3 | 2e-5 | 2e-5 | 2e-5 |
| backbone lr | freeze | freeze | 2e-6 | 2e-6 |
| lr schedule | cosine decay | cosine decay | cosine decay | cosine decay |
| lr warmup ratio | 0.03 | 0.03 | 0.03 | 0.03 |
| epoch | 1 | 1 | 1 | 1 |
| optimizer | AdamW | AdamW | AdamW | AdamW |

## 与同类对比

- **vs. Sequence Concat（LLaVA-Next, multi-crop）**：DeepStack 用 1/5 context length（576 vs 2880）达到相当甚至略优 AVG（Table 7: 51.1 vs 51.0），训练/推理开销显著降低（§3.2: "without increasing the overall sequence length the computation cost"）。Figure 1（p.1）右雷达（M3：DeepStack 在七轴全面包住 Sequence 基线）即此结论的图示。
- **vs. Dimension Concat（feature 维拼接，如 Sphinx/MoVE/MoUSi）**：DimCat 在特征维拼接 ≈ 两个 projection 之和（Eq. 7），仍在输入层一次性注入，AVG 仅 49.4，且 GQA 反降（59.5 vs 62.5）。DeepStack 的层级注入明显占优。
- **vs. Q-Former / Perceiver / Abstractor（resampler 类）**：§3.1 指出 resampler "easily struggle with hallucinations on spatial reasoning tasks"，且收敛成本与数据需求高；DeepStack 选 projection-based connector，POPE 87.6 显著优于 InstructBLIP 53.4 / BLIP-2 85.3（Table 1）。
- **vs. multi-crop 高分辨率方案（LLaVA-Next, InternLM-XComposer2-4KHD, Sphinx-X）**：DeepStack-L-HD-7B 在 DocVQA 78.8 / InfoVQA 41.2 / TextVQA 66.7，逼近甚至匹配 LLaVA-Next-7B（74.4 / 37.1 / 64.9，但 LLaVA-Next 用 765K SFT 而 DeepStack-HD 用 748K 自建数据，§4.1）。Figure 4（p.10）定性对比则进一步证明：在同等 576 context token 下，DeepStack 在小字 OCR、品牌标签、背景物体上不幻觉/不漏答，而 LLaVA-1.5 多处红圈区域失败。
- **DeepStack-L vs DeepStack-V**：L 版（注入 LLM 层）在 frozen encoder 下 AVG 略低（33.0 MMVet 等），但 unfreeze 后反超（Table 11: DeepStack-L⋆-7B VQAv2 81.1 / MMVet 37.1，vs frozen 版 79.5 / 29.9）。V 版需要 unfreeze ViT 才能稳定超越 baseline。
- **核心差异点**：所有竞品都在"输入层注入"框架内做文章（压缩/拼接/重采样），DeepStack 是少数从"注入位置"维度重新定义问题的方法——把视觉 token 分散到多层而非集中一层。

## 跨论文关系（→ MOC 谱系）

- **→ [[kimi-vl-technical-report]] / [[qwen2-5-vl-technical-report]] / [[qwen3-vl-technical-report]]**：这些是 DeepStack 的"宿主"——DeepStack 是 plug-in 视觉注入方法，可叠加到任何基于 transformer 的 LMM/VLM 上（§1 末: "this simple strategy could be generalized to any models or tasks built on top of transformer layers"）。Kimi-VL 的 MoonViT、Qwen-VL 系列的 native-resolution ViT 都是用 "Sequence Concat + 多分辨率" 思路处理高分辨率，DeepStack 提供了另一种不增 context length 的替代注入路径——可视为这些 VLM 在视觉 token 路由层的可选替换组件。
- **→ [[kimi-k2-5-visual-agentic-intelligence]]**：K2.5 强调 visual agentic intelligence 需要高保真视觉理解（OCR/UI/文档）。DeepStack 在 TextVQA/DocVQA/InfoVQA 上的细粒度增益（+4.2/+11.0/+4.0）正是 visual agentic 任务的基础能力，是 agentic 视觉栈底层可复用的注入增强。
- **→ [[hyper-connections]]**：HC = 残差拓扑中的 depth + width 双向连接。DeepStack 的"多层残差视觉注入"在概念上与 HC 的"多层残差路由"高度相邻——两者都打破"输入层→输出层"的单向残差链，在中间层引入跨层信息流。DeepStack 可视为 HC 思想在"视觉→语言"模态路由上的特例：固定路由模式（每 n 层注入一组视觉 token），而 HC 学习可学习路由权重。HC 的学习型拓扑或可改进 DeepStack 的"启发式"注入（见局限）。
- **→ [[efficiently-serving-large-multimodal-models-using-epd-disaggregation]]**：EPD §C 把 visual token pruning 列为未来方向。DeepStack 恰是推理效率方向的互补——它不 prune token，而是把 token 从"输入层 prefix（昂贵）"转移到"中间层残差（廉价，因不进入 KV-cache 主序列）"。两者可叠加：EPD 做 prefill/decode 解耦，DeepStack 做视觉 token 的层级分流，共同压缩服务成本。
- **MOC 定位**：DeepStack 是 **multimodal 主题下的 "visual-token-injection-method" 锚点**——与多 VLM 技术报告（架构侧）、EPD（服务侧）、HC（拓扑侧）形成"方法-架构-服务-拓扑"四象限中的"方法"象限。

## 局限与边界

1. **注入方式启发式、未学习（§5 Limitation）**：当前用简单残差 `+=` 在固定 `lstart`/`n` 下注入，作者自承"inserts the visual tokens into middle LLMs layers via a residual connection in a heuristic manner"。未来方向：gated function、layer-wise positional embeddings、可学习的注入权重（与 [[hyper-connections]] 学习型路由形成对照）。
2. **超参选择缺乏系统方法（§5）**："how to systematically decide the starting layer and number of layers also deserves more study"。当前靠 Figure 3（p.8）消融经验取值（Phi-3 起始层 ≤8、stacking 4 层最佳），不同 LLM/ViT 深度需重调。
3. **依赖高分辨率 token 流，对 vision encoder 敏感**：Table 6 证明收益来自 Hi-Res token；但 Hi-Res feature 仍需先经 vision encoder 提取（CLIP-large-336 + patch mosaic），encoder 容量与分辨率仍是上限。DeepStack-V 必须 unfreeze ViT 才能反超 baseline（Table 4），frozen 状态下 PatchEmbed+0~12 层均显著低于 baseline——说明 DeepStack-V 不能即插即用。
4. **未在 decoder-only 最新大模型上验证**：实验仅覆盖 Vicuna-7B/13B 与 Phi-3；未在 70B+ 或更现代的 Llama-3 / Qwen 系列上验证 scaling 行为。Figure 3c 显示 4 层优于 2 层，但"层数越多越好"是否对更深模型单调成立未知。
5. **增益集中在高分辨率/文本导向任务，通用 VQA 增益有限**：Table 1 中 DeepStack-L-7B 在 VQAv2/GQA 上相对 LLaVA-1.5 提升微弱（79.5 vs 78.5 / 63.1 vs 62.0），主要红利在 TextVQA/DocVQA/InfoVQA。对低分辨率自然图像场景的边际收益较小。
6. **MMMU/MMVet 未明显突破**：Table 1 中 DeepStack-L-HD-7B MMMU 35.6 / MMVet 37.5，未超越 LLaVA-Next-7B 的 35.9 / 49.1（后者用了 765K SFT 数据，公平性存疑，但仍说明 DeepStack 在综合推理 benchmark 上未占优）。作者将此归因于缺乏 LLaVA-Next 的 "fancy instruction-following data"（§4.2），但也暴露了 DeepStack 对指令调优数据质量的依赖。
7. **未探索与 token 压缩/resampler 的组合**：DeepStack 主张 projection-based connector，但未与 Q-Former 类重采样叠加；二者是否互补（resampler 降 token + DeepStack 多层注入）未验证。
