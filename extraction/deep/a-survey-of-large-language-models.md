# A Survey of Large Language Models — 技术点深读（DEEP 2026-08-18）

> Source: `extraction/fulltext/a-survey-of-large-language-models.txt` (arXiv:2303.18223v19, 18 Mar 2026)。Zhao, Zhou, Li, Tang, Wang, Hou, Min, Zhang 等（中国人民大学高瓴人工智能学院 / Université de Montréal / JRDC）。GitHub: github.com/RUCAIBox/LLMSurvey；中文书: lmbook-zh.github.io。**survey 类锚点论文**——非单一机制，而是 LLM 全栈 taxonomy。本仓库 LLM-background 谱系的根索引。

## 核心问题

本文攻击的不是单一技术点，而是一个**认知/导航性问题**：LLM 在 2023 ChatGPT 发布后论文量从 0.40 篇/天暴涨到 8.58 篇/天（§1, Fig.1），技术栈横跨数据、架构、训练、对齐、提示、评测六大轴，但缺乏一篇在"模型规模 >10B"边界上、把 pre-training → adaptation → utilization → evaluation 四阶段串成统一脉络的综述（§1）。已有 PLM survey（[36–39]）止于 BERT/GPT-2 量级，未触及 emergent abilities；已有 LLM 专题 survey（[32, 48–54]）只覆盖某一侧面。

判据性区分（§1, "three major differences between LLMs and PLMs"）：
1. **Emergent abilities**——LLM 表现出小 PLM 没有的涌现能力（ICL / 指令跟随 / CoT 推理），是性能跃迁的根因。
2. **Prompting interface 取代 fine-tuning**——访问 LLM 的主要方式是 prompt/API，而非梯度更新；用户必须学会"如何让 LLM 跟随"。
3. **研究与工程的边界消融**——训练 LLM 需大规模数据处理 + 分布式并行的工程经验，研究者必须懂工程。

由此本文的产出是**四阶段 taxonomy + 资源清单 + GPT 系列技术演进史**作为对上述导航性问题的系统性应答，并附模型卡（Tab.1 / Tab.5）、优化设置（Tab.8）、能力-数据集对照（Tab.14）等结构化总表。

## 关键创新点

作为 survey，"创新点"指其 taxonomy 骨架与跨方法对照，而非新算法：

### 1. 四阶段主轴 taxonomy：Pre-training / Adaptation / Utilization / Evaluation（§4–§7）
- **机制**：按"模型生命周期"切分——§4 pre-training（数据→架构→训练）把能力注入；§5 adaptation（instruction tuning → alignment tuning → efficient tuning → quantization）把能力对齐/解锁；§6 utilization（prompting → ICL → CoT → planning）把能力用出来；§7 capacity evaluation（basic → advanced → benchmarks）把能力测出来。
- **效果**：将散乱数百篇文献归口到四条正交轴，每条轴再二/三级细分（如 §4.2 架构下分 mainstream arch / detailed config / pre-training task），共 14 张结构化表覆盖 ~100 个模型 + ~50 个数据集。该四阶段切分被后续 LLM 综述广泛沿用。

### 2. Scaling law 双型对照 + emergent abilities 的张力论述（§2.1）
- **机制**：并列 KM scaling law（Kaplan/OpenAI [30]，`L(N)=L(Nc/N)^αN`，αN≈0.076，倾向"model size 优先"）与 Chinchilla scaling law（Hoffmann/DeepMind [34]，`L(N,D)=E+A/N^α+B/D^β`，α=0.34, β=0.28，导出 `Nopt∝C^a, Dopt∝C^b` 且 a≈b，主张"model/data 等比"）。二者在 compute 分配上结论相反。
- **emergent abilities 三典型**（§2.1）：ICL（GPT-3 175B 显现，GPT-1/2 不行）、instruction following（LaMDA-PT 68B 临界，PaLM 62B 临界）、step-by-step reasoning/CoT（PaLM/LaMDA >60B 起、>100B 优势显著）。
- **张力**（§2.1 "How Emergent Abilities Relate to Scaling Laws"）：scaling law 是连续可预测的（diminishing returns），emergent abilities 是不可预测的相变式跃迁；并引述 [70, 71] 争点——emergence 可能部分源于不连续评测指标，改用连续指标后"sharpness 消失"。本文不裁决，而是用婴儿语言发育类比解释"连续成长 vs 阶段性跃迁"可共存。

### 3. 架构 taxonomy：三类主流 + MoE 扩展 + emergent architectures（§4.2.1）
- **三类主流**：encoder-decoder（T5/BART，LLM 中少见，如 Flan-T5）、causal decoder（GPT 系，主导，OPT/BLOOM/Gopher）、prefix decoder（双向编码 prefix + 单向生成，GLM-130B/U-PaLM，可由 causal decoder 转换而来加速收敛 [29]）。
- **MoE 扩展**：sparsely activated，参数量↑计算量不变（Switch Transformer [25]/GLaM [112]），但路由不稳、需高精度张量/小范围初始化 [25]；指出 GPT-4 疑为 MoE 但未官方确认。
- **Emergent architectures**（§4.2.1 末）：SSM 谱系——Mamba（selective state update [272]）、RWKV（time-mixing + channel-mixing + token shift [273]）、RetNet（multi-scale retention [271]）、Hyena [269]。自承"performance still lags behind Transformer"。

### 4. 详细配置四件套：Normalization / Position Embedding / Activation / Attention（§4.2.2）
- **Normalization**：LayerNorm [275] → RMSNorm [276]（去均值只保留 RMS，提速）→ DeepNorm [277]（残差缩放 α，支撑千层）。Position：post-LN（vanilla，不稳）/ pre-LN（主流，稳但略劣）/ sandwich-LN（pre-LN + 额外 LN，GLM-130B 发现在 >100B 时不稳甚至崩溃）。
- **Position embedding**：absolute（sinusoidal/learned）→ relative（T5 bias，可外推）→ **RoPE**（旋转矩阵，相对位置由绝对旋转复合得出，长程衰减，PaLM/LLaMA 采）→ ALiBi（无参 distance penalty，BLOOM 采，外推强）。
- **Activation**：ReLU → GeLU → GLU 变体（SwiGLU/GeGLU，PaLM/LaMDA/LLaMA 采，性能更好但 FFN 参数 +50% [291]）。
- **Attention**：full → sparse（GPT-3 factorized）→ multi-query（PaLM/StarCoder）→ **GQA**（LLaMA 2 [99]，MQA 与 MHA 折中）→ FlashAttention [302]（IO-aware fused kernel，已入 PyTorch/DeepSpeed/Megatron，v2 再 2× 加速）→ PagedAttention [304]（OS paging 思想解决 KV cache 碎片，vLLM）。
- **总体建议**（§4.2.2 末）：pre RMSNorm + SwiGLU/GeGLU + RoPE/ALiBi，embedding 后不加 LN。

### 5. 训练三件套：优化设置 + 3D parallelism + mixed precision（§4.3）
- **优化设置**（§4.3.1, Tab.8）：batch 动态增长（GPT-3 32K→3.2M tokens，PaLM 1M→4M）；lr warm-up 0.1–0.5% 后 cosine decay 至 10%（GPT-3 6e-5，LLaMA 1.5e-4）；Adam/AdamW（β1=0.9, β2=0.95, ε=1e-8）或 Adafactor（省显存，PaLM/T5）；grad clip 1.0、weight decay 0.1；loss spike 处理——PaLM/OPT 从早期 checkpoint 重启跳过坏数据 [56,90]，GLM 缩 embedding 梯度 [93]。
- **3D parallelism**（§4.3.2）：data parallel（复制参数切数据）+ pipeline parallel（GPipe [321]/PipeDream [322]，切层跨 GPU，microbatch 填 bubble）+ tensor parallel（Megatron-LM [75]，切参数矩阵，`Y=[XA1,XA2]`）。BLOOM 实证 8-way DP × 4-way TP × 12-way PP = 384 A100。
- **Mixed precision**（§4.3.2）：FP32 → FP16（A100 FP16 算力 2× FP32，但精度损失）→ BF16（更多指数位，BLOOM 实证优于 FP16）。
- **内存优化**：ZeRO / FSDP / activation recomputation [77,329] 已入 DeepSpeed/PyTorch/Megatron。**predictable scaling**（GPT-4 [46]）用小 proxy 模型预测大模型性能、早侦异常。

### 6. Adaptation 双轨：Instruction tuning（解锁能力）+ Alignment tuning（对齐价值）（§5）
- **Instruction tuning**（§5.1）：四类 instance 构造法——formatting NLP task datasets（加 task description，[28,66,67]）、formatting chat data、formatting synthetic instances（Self-Instruct [147]，LLM 自生成）、alignment-oriented formats。关键发现：去除 task description 导致性能剧降 [67]，证明 instruction 是泛化的关键因子。
- **Alignment tuning / RLHF**（§5.2）：三准则 helpful/honest/harmless（HHH，[66,366]）；三类反馈采集——ranking-based（Elo [116]）、question-based（WebGPT [81]）、rule-based（Sparrow [116]，GPT-4 用 zero-shot classifier 作 rule-based reward [46]）。RLHF 三组件（§5.2.3）：pre-trained LM + reward model + RL 算法（PPO [128]）。指出 **alignment tax**——对齐会损害 ICL 等通用能力 [366]。
- **Efficient tuning + quantization**（§5.3）：PEFT（LoRA/alpaca-lora）+ 量化（4-bit/8-bit）面向资源受限场景。

### 7. Utilization 四级递进：Prompting → ICL → CoT → Planning（§6, Tab.11）
- **Prompting**（§6.1）：四要素（task description / input data / contextual info / prompt style）+ 四原则（clear goal / decompose sub-tasks / few-shot demos / model-friendly format）。
- **ICL**（§6.2）：形式化 `LLM(I, f(x1,y1),...,f(xk,yk), f(xk+1)) → ŷk+1`（式 11）；demonstration design 三维——selection（k-NN [420] / dense retriever EPR [421] / LLM 自选 [489]）、format（Auto-CoT [427]、APE [423]）、order（recency bias，[481]）。与 instruction tuning 互补：后者需梯度更新，ICL 仅 prompt；instruction tuning 可增强 zero-shot ICL [69]。
- **CoT**（§6.3）："Let's think step by step"激发中间推理；self-consistency [429]（多路采样投票）、Selection-Inference [428]、DIVERSE [430]。
- **Planning**（§6.4, Tab.11）：least-to-most [432] / DECOMP [433]（text-based 分解）；PAL [436] / HuggingGPT [437]（code-based）；ReAct [442]（reason+act 协同）；Reflexion [443]（self-reflection 动态记忆）；Tree of Thoughts [444]（树搜索 + 投票）；RAP [440]（LLM 作 world model + MCTS）。

### 8. Capacity evaluation 双层：Basic + Advanced + Benchmarks（§7, Tab.14）
- **Basic**（§7.1）：language generation（LM/conditional gen/code synthesis, pass@k [105,223]）、knowledge utilization（closed-book QA / open-book QA / knowledge completion）、complex reasoning（knowledge reasoning / symbolic reasoning / mathematical reasoning, GSM8k [198]/MATH [362]）。
- **Advanced**（§7.2）：human alignment（TruthfulQA [558]/CrowS-Pairs [605]）、interaction with external environment（VirtualHome/ALFRED/BEHAVIOR/Minecraft Voyager [699]/GITM [698]）、tool manipulation（search/calculator/code executor/model interface）。
- **Benchmarks**（§7.3.1）：MMLU [362]（多任务知识）、BIG-bench [70]（204 任务）/ BBH [363]、HELM [522]（16 场景 × 7 指标）、人类考试（AGIEval [710]/C-Eval [713]/Xiezhi [714]）。GPT-4 MMLU 5-shot 86.4%。
- **Evaluation approaches**（§7.3.2）：benchmark-based / human-based / model-based（LLM-as-judge [152,633,634]，但有 order bias 与 self-preference bias [634,648,649]）。三类被评模型：base / fine-tuned / specialized。

## 表格（原文结构化）

### 表 A — Survey 四阶段 taxonomy 总览（据 §4–§7 重构，映射仓库 deep notes）

| 阶段 | 子轴 | 代表方法/模型（原文编号） | 仓库对应 deep note |
|---|---|---|---|
| Pre-training (§4) | Data (§4.1) | webpages/books/conv（general）；multilingual/scientific/code（specialized） | — |
| | Architecture mainstream (§4.2.1) | causal decoder（GPT-3/OPT/BLOOM/LLaMA）、prefix decoder（GLM-130B）、MoE（Switch/GLaM） | [[deepseek-v3-technical-report]]（MoE+MLA） |
| | Detailed config (§4.2.2) | RMSNorm、RoPE、SwiGLU、GQA、FlashAttention、PagedAttention | [[root-mean-square-layer-normalization]]、[[gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints]]、[[efficient-memory-management-for-large-language-model-serving-with-pagedattention]] |
| | Emergent arch (§4.2.1 末) | Mamba、RWKV、RetNet、Hyena | [[gated-delta-networks-improving-mamba2-with-delta-rule]]、[[kimi-linear-an-expressive-efficient-attention-architecture]] |
| | Training (§4.3) | 3D parallelism（Megatron-LM/DeepSpeed/Colossal-AI）、BF16、ZeRO/FSDP | [[megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism]]、[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]、[[zero-memory-optimizations-toward-training-trillion-parameter-models]] |
| Adaptation (§5) | Instruction tuning (§5.1) | T0/Flan/InstructGPT/Self-Instruct | — |
| | Alignment/RLHF (§5.2) | InstructGPT [66]、Sparrow [116]、WebGPT [81]、PPO [128] | [[hybridflow-a-flexible-and-efficient-rlhf-framework]] |
| | Efficient tuning (§5.3) | LoRA、PEFT、量化 | — |
| Utilization (§6) | ICL (§6.2) | kNN-ICL [420]、EPR [421]、APE [423] | — |
| | CoT (§6.3) | self-consistency [429]、Selection-Inference [428] | [[deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning]]（推理谱系下游） |
| | Planning (§6.4) | ReAct [442]、Reflexion [443]、ToT [444]、RAP [440]、HuggingGPT [437] | [[kimi-k2-open-agentic-intelligence]]（agentic 谱系下游） |
| Evaluation (§7) | Basic (§7.1) | MMLU/GSM8k/MATH/HumanEval/TriviaQA | — |
| | Advanced (§7.2) | TruthfulQA、VirtualHome、Voyager、tool use | — |
| | Benchmarks (§7.3) | MMLU/BIG-bench/HELM/AGIEval/C-Eval | — |

### 表 B — Scaling law 双型对照（据 §2.1 公式 1–3 重构）

| 维度 | KM scaling law (Kaplan/OpenAI [30]) | Chinchilla scaling law (Hoffmann/DeepMind [34]) |
|---|---|---|
| 形式 | `L(N)=(Nc/N)^αN`，分因素独立拟合 | `L(N,D)=E+A/N^α+B/D^β`，联合拟合 |
| 指数 | αN≈0.076, αD≈0.095, αC≈0.050 | α=0.34, β=0.28；E=1.69, A=406.4, B=410.7 |
| 拟合范围 | N: 768–1.5B, D: 22M–23B tokens | N: 70M–16B, D: 5B–500B tokens |
| Compute 最优分配 | model size 优先（a > b） | model/data 等比（a = α/(α+β) ≈ b） |
| 实证含义 | 大模型少数据 | Chinchilla(70B, 更多 tokens) > Gopher(280B, 少 tokens) |
| 任务可预测性 | predictable scaling（GPT-4 [46]）但存在 inverse scaling [62] | 同左 |

### 表 C — Transformer 详细配置选型（据 Tab.5 / Tab.7 / Tab.8 精简）

| 组件 | 主流选型 | 代表模型 | 备注 |
|---|---|---|---|
| Norm method | RMSNorm | Gopher/Chinchilla/LLaMA/LLaMA 2 | 比 LayerNorm 快，去均值 |
| Norm position | Pre-LN | GPT-3/OPT/BLOOM/LLaMA | 稳但略劣；GLM >100B 时 pre-LN 不稳需 DeepNorm |
| Activation | SwiGLU / GeGLU | PaLM/LLaMA/LaMDA | FFN 参数 +50% [291] |
| Position embedding | RoPE | PaLM/LLaMA/LLaMA 2 | 长程衰减；ALiBi(BLOOM) 外推更强 |
| Attention | GQA | LLaMA 2 | MQA(PaLM) 与 MHA 折中 |
| Optimizer | AdamW | LLaMA/Chinchilla/OPT | β1=0.9, β2=0.95 |
| Precision | BF16 | BLOOM/PaLM/MT-NLG/Gopher | 优于 FP16（更多指数位） |
| Batch size | 动态增长 4M tokens | GPT-3 32K→3.2M, PaLM 1M→4M | 稳定训练 + 吞吐 |

## 与同类对比

- **vs [[efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey]]（仓库内分布式训练 survey）**：本 survey 在 §4.3 仅做训练技术的入门级综述（3D parallelism + BF16 + ZeRO 一页纸），后者是分布式训练轴的深度展开（拓扑/通信/调度/容错全维）。本 survey 是四阶段总览，后者是 §4.3 的纵深特化。二者互补：本 survey 提供四阶段坐标，后者提供训练轴纵深。
- **vs [[a-survey-on-large-language-model-acceleration-based-on-kv-cache-management]]（仓库内 KV cache survey）**：本 survey §4.2.2 的 attention 节只点到 PagedAttention [304]/FlashAttention [302]（单段介绍），KV cache survey 把 attention/KV 优化做成 token/model/system 三级 12 子类机制级对照表。本 survey 是 LLM 全栈锚点，KV cache survey 是 inference/memory 轴的纵深特化。
- **vs 早期 PLM survey（[36–39]）**：本文 §1 明确划界——PLM survey 聚焦 BERT/GPT-2 量级（<1.5B）的 pre-training + fine-tuning 范式，未触及 emergent abilities 与 RLHF；本 survey 聚焦 >10B，四阶段中 adaptation/utilization/evaluation 三阶段是 PLM survey 基本不覆盖的。
- **vs LLM 专题 survey（[32, 48–54]）**：本文 §1 自称覆盖更全面——专题 survey 多只覆盖某一轴（如 [50] 仅 ICL、[331] 仅 instruction tuning、[43]/[44] 仅效率），本 survey 是四阶段统一脉络。
- **vs GPT-4 技术报告 [46] / InstructGPT [66]**：本 survey 是二手综述，GPT-4/InstructGPT 是其引用的一手来源；本 survey 把这些一手工作的技术点（predictable scaling、RLHF 三阶段、rule-based reward）归位到四阶段 taxonomy 中。

## 跨论文关系（→ MOC 谱系）

本 survey 是 **LLM-background 谱系的 taxonomy anchor / 根索引**——它把仓库内多篇具体技术论文归位到四阶段 taxonomy 的叶子节点：

### Pre-training 阶段
- **架构 / MoE + MLA**：[[deepseek-v3-technical-report]] — DeepSeek-V3 用 MoE（sparsely activated，§4.2.1）+ MLA（低秩 KV 压缩，是 §4.2.2 attention 节 GQA/MQA 谱系的延伸，走 latent compression 路线而非 head sharing）。
- **架构 / GQA**：[[gqa-training-generalized-multi-query-transformer-models-from-multi-head-checkpoints]] — GQA [301] 是 §4.2.2 attention 节 MQA→MHA 折中点，LLaMA 2 [99] 采用；uptraining 从 MHA checkpoint mean-pool 转 GQA。
- **架构 / RMSNorm**：[[root-mean-square-layer-normalization]] — RMSNorm [276] 是 §4.2.2 normalization 节的核心选型，Gopher/Chinchilla/LLaMA 采，比 LayerNorm 快。
- **架构 / 线性注意力**：[[gated-delta-networks-improving-mamba2-with-delta-rule]]（Mamba2，§4.2.1 emergent arch SSM 谱系的 delta rule 演进）、[[kimi-linear-an-expressive-efficient-attention-architecture]]（Kimi Linear，attention 替代架构）。
- **训练 / 并行**：[[megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism]]（Megatron-LM tensor parallelism [75]，§4.3.2 3D parallelism 的 TP 标杆）、[[efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm]]（PTD-P 组合 + interleaved schedule，§4.3.2 的纵深）、[[megascale-scaling-large-language-model-training-to-more-than-10000-gpus]]（万卡扩展）、[[zero-memory-optimizations-toward-training-trillion-parameter-models]]（ZeRO，§4.3.2 内存优化标杆）。
- **训练 / 优化器**：[[muon-is-scalable-for-llm-training]] — 对 §4.3.1 优化器节（Adam/AdamW）的新替代路线。

### Adaptation 阶段
- **RLHF 系统**：[[hybridflow-a-flexible-and-efficient-rlhf-framework]] — RLHF 三组件（pre-trained LM + reward model + RL algo, §5.2.3）的工程框架，解决 PPO 训练的 orchestration。
- **RL 推理**：[[deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning]] — 把 §5.2 RLHF 范式从"对齐人类偏好"迁移到"激励推理能力"，R1 是 RL 谱系从 alignment 到 reasoning 的转向。
- **数学推理**：[[deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models]] — 对应 §7.1.3 mathematical reasoning 评测轴（GSM8k/MATH）的能力增强方法。

### Frontier（下游综合产物）
- [[kimi-k3-open-frontier-intelligence]]、[[kimi-k2-open-agentic-intelligence]] — 是本 survey 四阶段全栈（pre-train + RLHF + tool use/planning + eval）的工业级集成产物；§6.4 planning（ReAct/Reflexion/ToT）与 §7.2.3 tool manipulation 是 K2 agentic 能力的方法论前身。

### Survey 互引
- [[efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey]] — §4.3 训练轴的纵深特化（见"与同类对比"）。
- [[a-survey-on-large-language-model-acceleration-based-on-kv-cache-management]] — §4.2.2 attention / inference-memory 轴的纵深特化。

谱系定位：本 survey = **LLM-background 谱系根节点 / 四阶段坐标索引**；上述具体论文 = 四阶段 taxonomy 的叶子实例。仓库内任一 LLM 技术论文都可在本 survey 的表 A 中找到归位。

## 局限与边界

- **时效性与更新滞后**：尽管 v19 标注 2026-03-07 更新，但四阶段主体框架与 §4–§7 的技术点仍以 2023–2024 初的工作为骨干；2024 H2–2025 的一批关键进展（如 Muon 优化器、Mamba2/delta rule、DeepSeek-R1 的 RL-for-reasoning 范式、long-context 的 1M+ 窗口、Speculative Decoding 的工程化）仅在补注中零星提及或未覆盖。emergent architectures（§4.2.1 末）对 Mamba/RWKV 的评价"lags behind Transformer"在 2025 后已部分过时。
- **无原创机制，无统一实验**：作为 survey，所有量化数字（如 GPT-4 MMLU 86.4%、scaling law 指数、batch size 数值）均引自原论文自报，未在统一模型/数据集下复现。Tab.1 / Tab.5 / Tab.8 是模型卡-配置对照表，不是精度/吞吐数值的 head-to-head 基准。
- **MoE 讨论偏浅**：§4.2.1 对 MoE 仅一段介绍（Switch/GLaM），未展开 expert routing（top-k vs expert choice）、load balancing loss、capacity factor、fine-grained expert（DeepSeek-MoE 路线）等关键技术细节；这与 2024 后 MoE 成为主流（DeepSeek-V3/Mixtral）的现实形成落差。
- **RLHF 简化为 PPO 路线**：§5.2 主要讲 InstructGPT 的 PPO [128] 三阶段，对 DPO [388]、SLiC、RRHF 等简化算法仅在 §5.2.4 / future direction 一笔带过（"develop simplified optimization algorithms for alignment [388,391]"），而 DPO 谱系在 2023 H2 后已成为主流替代。
- **emergent abilities 争论未裁决**：§2.1 引述 [70,71] 的"emergence 是不连续指标假象"争点但未给出本文立场；[72] 的连续指标修复方案仅一句带过。这是 2023–2025 持续争议的开放问题，本 survey 止于"more fundamental research is still in need"。
- **inference efficiency 轴单薄**：§4.2.2 attention 节对 FlashAttention/PagedAttention 各一段，但 speculative decoding、continuous batching、prefix caching、disaggregated serving 等 2023 H2 起的 inference 工程主流方向基本未覆盖（这些恰是仓库内 [[a-survey-on-large-language-model-acceleration-based-on-kv-cache-management]] 与多篇 serving 论文的领地）。
- **agentic / tool use 仍处早期**：§6.4 planning 与 §7.2.3 tool manipulation 的代表方法（ReAct/Reflexion/ToT/HuggingGPT）是 2022–2023 初的工作；2024 后的 function calling 标准化、MCP 协议、长程 agentic RL（仓库内 [[kimi-k2-open-agentic-intelligence]] / [[beyond-ten-turns-unlocking-long-horizon-agentic-search-with-large-scale-asynchronous-rl]]）未被纳入。
- **评测轴的 data contamination 议题仅作 future direction**：§10 提"data contamination has become a severe issue [740]"但未展开去污染方法与污染检测协议，而这是 2024 后 LLM 评测可信度的核心争议。
- **多模态覆盖薄**：尽管 §1 提及 GPT-4 多模态、§9 applications 有多模态一节，但 §4–§7 的技术 taxonomy 几乎纯文本 LLM；vision-language 的架构融合（projector / cross-attention / early fusion）未纳入 taxonomy。
- **定义边界（>10B）的任意性**：§2.1 脚注 4 自承"no formal consensus on the minimum parameter scale"，取 >10B 是"slightly loose definition"——这导致 T5(11B)/T0(11B) 这类实质是 PLM 的模型被纳入，而 Phi-2(2.7B)/Gemma-2(2B) 等小而强模型被排除，与 2024 后"小模型也涌现"的趋势冲突。
