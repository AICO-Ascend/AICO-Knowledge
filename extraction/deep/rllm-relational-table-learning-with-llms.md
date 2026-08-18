# RLLM — 技术点深读（DEEP 2026-08-18）

> 原文：rLLM: Relational Table Learning with LLMs (arXiv:2407.20157v2, 12 Nov 2025)。Shanghai Jiao Tong University + Tsinghua University。本文是一篇 **系统/框架型论文**（PyTorch 库 rLLM/relationLLM），并附带的 BRIDGE 示例算法与 SJTUTables 数据集，并非提出新的 LLM 训练范式。

## 核心问题

论文攻击的不是"模型能力不足"，而是 **"将 LLM 应用于真实关系型大数据的成本与工程不可行性"**，以及由此衍生的 **RTL（Relational Table Learning）方法学碎片化**问题。机制层面：

- **成本不可持续性（§1 + Figure 1）**：作者引用 Statista [23] 估计 2025 年全球数据量达 181 ZB，其中关系型数据库托管约 **73%** 的世界数据 [6]。若将这些数据喂给 GPT-3.5 Turbo 分析，2025 年 LLM 总成本预计近 **$5,000 trillion**，约为"2023 年美国 GDP（$27.37 trillion）的 214 倍"（§1 原文）。
- **token 成本分布失衡（§1 + Figure 1 右图 + §A.1）**：文本与结构化数据体量小于多媒体，但因 UTF-8 编码（每字符 1 字节，英文词约 6–11 字符 [26]）+ OpenAI token 经验公式 [27]，其 token 成本占比反而最高；多媒体（图像 256×256 RGB 按 ViT [28] 切 patch + OpenAI 定价 [29]；视频按 Gemini 1.5 [30] 每秒一帧抽样）单位 token 成本相对低。这意味着 **直接把关系表文本化喂 LLM 在经济上不成立**。
- **方法学碎片化（§2）**：GNN、LLM、TNN（Table Neural Network）三类工具各自发展，缺少统一的模块化分解，研究者无法快速组合它们来构建 RTL 模型。
- **数据集缺失（§4.2 + §A.2）**：RTL 是新兴领域，现有 RelBench [9]（爬取自 Amazon/Stack Overflow）噪声高、不平衡、任务复杂，不利于标准化方法验证，缺少干净的对照基准。

## 关键创新点

1. **三层架构的模块化分解（§2 + Figure 2/3）**
   - **机制**：将整个 RTL 流水线拆为 Data Engine Layer（`Dataset` 子类负责加载，`BaseGraph`/`BaseTable` 负责存储，二者解耦以追求 flexibility & scalability，§2.1）、Module Layer（GNN 的 `GraphTransform`/`GraphConv`；LLM 的 `Predictor`/`Enhancer`；TNN 的 `TableTransform`/`TableConv`）、Model Layer。
   - **效果**：使任一 RTL 模型可由标准化模块组合，论文将 GCN/GAT/RECT/TAPE/OGC（同构）、HAN/HGT（异构）、TabTransformer/TabNet/FT-Transformer（单表）统一封装进同一接口（§4.1）。

2. **"Combine / Align / Co-Train"三策略范式（§2.3）**
   - **机制**：
     - **Combine** — 串联不同模块（如 LLM Predictor 先标注 → GCN 分类，引用 [10][11]）。
     - **Align** — 对齐不同模块的输入输出特征空间（如 LLM Enhancer 生成 embedding 与 GNN 节点 embedding 在最终空间对齐，对应 ConGraT [13]）。
     - **Co-Train** — 不同模块协同训练（如 BRIDGE 把 TNN 与 GNN 联合训练）。
   - **效果**：三策略可独立或组合使用，"rapidly develop various RTL-type models"（§2.3 末），为后续 RTL 方法提供构造模板。

3. **BRIDGE 示例算法（§3 + Figure 4）**
   - **机制**：简化 RDL [9] 工作流——(1) **只考虑与目标表相连的单张关系表**；(2) **其余表统一预编码为 dense embeddings**。Table Encoder（TableTransform + TableConv）处理表内异构列特征；Graph Encoder（GraphTransform + GraphConv）处理外键构成的关系图，并将目标表 embedding + 其余表预计算 embedding 一并输入做联合建模。训练目标可监督（cross-entropy）或无监督（基于表/外键的数据重构）。
   - **效果（§5.3 + Table 2）**：在 TML1M 上 BRIDGE 用 TabTransformer 作 table encoder + GCN 作 graph encoder，准确率 **0.362±0.03**，相比单一 TabTransformer（0.347±0.02）/ FT-Transformer（0.352±0.02）有提升但幅度有限；在 TLF2K 上 **0.422±0.03**（vs TabTransformer 0.137±0.08，提升 ~3 倍）；在 TACM12K 上 **0.256±0.01**（vs TabNet 0.135±0.01，约 1.9 倍）。关系表信息越丰富（TLF2K、TACM12K 含多张关系表）BRIDGE 优势越显著。

4. **SJTUTables 数据集（§4.2 + Table 1 + §A.2）**
   - **机制**：对 MovieLens1M / LastFM2K / ACM 三个经典数据集做增强——TML1M 抓取 MovieLens 网站补全 movie 表 11 列（Title/Year/Genre/Director/Cast/Runtime/Languages/Certificate/Plot/Url），任务为用户年龄段（7 类）分类；TLF2K 抓 Last.FM 补 artists 10 列，并用 **ChatGPT 给每位 artist 基于 tag_list 分配单一 genre 标签（含置信度，低置信人工干预）**，原 tag 因此不可用于该任务；TACM12K 手工标注 venue 年份、修正 PvsC 标注、将 STOC 重分类为 COLT，重算 PvsV*VvsC 得 conference 属性。
   - **效果**：每个数据集 **每类 20 个标注样本 + 500 val + 1000 test**，固定平衡划分，便于标准化评估；相比 RelBench 噪声更低、任务更经典。

## 表格（原文结构化）

**Table 1：SJTUTables 数据集概览（§4.2 + §A.2）**

| Dataset | Tables [#row/#col] | Relation Tables | Label | Classes | #Train/#Val/#Test |
|---|---|---|---|---|---|
| TML1M | users [6,040/5]; movies [3,883/11]; ratings [1,000,209/4] | ratings: user-movie | Age range of user | 7 | 140/500/1000 |
| TLF2K | artists [9,047/10]; user_artists [80,009/3]; user_friends [12,717/3] | user_artists: user-artist; user_friends: user-user | Genre of artist | 11 | 220/500/1000 |
| TACM12K | papers [12,499/5]; authors [17,431/3]; citations [30,789/2]; writings [37,055/2] | citations: paper-paper; writings: paper-author | Conference of paper | 14 | 280/500/1000 |

**Table 2：分类准确率（§5 + 脚注6：GNN 类方法因无法直接处理表数据未纳入对比）**

| Method | TML1M | TLF2K | TACM12K |
|---|---|---|---|
| Random | 0.144±0.01 | 0.091±0.03 | 0.075±0.0 |
| TabTransformer | 0.347±0.02 | 0.1370±0.08 | 0.091±0.01 |
| TabNet | 0.259±0.08 | 0.1346±0.03 | 0.135±0.01 |
| FT-Transformer | 0.352±0.02 | 0.1319±0.01 | 0.099±0.01 |
| **BRIDGE** | **0.362±0.03** | **0.422±0.03** | **0.256±0.01** |

**rLLM 已收录方法清单（§4.1）**

| 类别 | 方法 |
|---|---|
| GNN 同构 | GCN, GAT, RECT, TAPE, OGC |
| GNN 异构 | HAN, HGT |
| TNN 单表 | TabTransformer, TabNet, FT-Transformer |
| TNN 关系表 | BRIDGE |

## 与同类对比

- **vs RDL [9]（Relational Deep Learning, Fey et al.）**：BRIDGE 是 RDL 的简化版——RDL 把整个关系数据库的多张表与外键全部建模为异构图；BRIDGE 仅保留 **单张关系表**，其余表预编码为 dense embedding 后注入。代价是损失了多关系建模能力，收益是架构复杂度大幅降低，便于教学/快速实验。RelBench 数据集 [9] 与 SJTUTables 互补：RelBench 贴近商业（user lifetime value、论坛活跃度预测）但噪声高、不平衡；SJTUTables 是经典数据集增强版，干净、平衡、固定划分，适合方法原型期对照（§4.2 末尾作者建议先用 SJTUTables 再去 RelBench 评估）。
- **vs ConGraT [13]**：ConGraT 用 LM 与 GNN 分别生成节点 embedding 再对齐，是 rLLM 中 "Align" 策略的代表；rLLM 把它泛化为 Enhancer（LLM 生成 embedding）+ GNN module + 对齐操作的可复用模块。
- **vs 单表 TNN（TabTransformer/TabNet/FT-Transformer）**：单表 TNN 只学目标表内部列间关系，忽视跨表外键信息，在 TLF2K/TACM12K 上准确率塌陷（TabTransformer 仅 0.137/0.091）。BRIDGE 通过 Graph Encoder 引入跨表关系，在 TLF2K 上提升约 3 倍，证明关系表建模的边际价值。
- **vs "Let your graph do the talking" [10] / Label-free node classification [11]**：二者用 LLM 给图节点做标注再喂 GCN，是 rLLM 中 "Combine" 策略的实例化；rLLM 将其抽象为 Predictor 模块 + GNN 模块的通用拼装。
- **vs LLM 直接推理范式**：论文核心立场是 **避免把关系表文本化喂 LLM**（成本不可持续，§1），改为用 LLM 做 Predictor（标注）/ Enhancer（增广）这类局部工作，主体表征学习交给 TNN+GNN。这与"用 LLM 端到端处理一切"的路线形成方法论分歧。

## 跨论文关系（→ MOC 谱系）

本文是一篇 **结构化/表格学习的工程框架论文**，与 AICO-knowledge 以 LLM 训练/推理为主轴的谱系 **正交**：它不训练 LLM，也不改进推理，而是用 LLM 作为标注/增广的局部组件来服务关系表学习。有限的连接点：

- [[a-survey-of-large-language-models]] — rLLM 引用 [2] 即此综述，作为 LLM 背景锚点；rLLM 的 Predictor/Enhancer 模块正是该综述所归纳的 LLM 能力在结构化数据上的落地接口。结构化数据 grounding 是 LLM 应用层的一个重要分支。
- [[deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning]] / [[deepseekmath-pushing-the-limits-of-mathematical-reasoning-in-open-language-models]] — 这两者关注 LLM 在符号化/数学结构上的推理；rLLM 处理的是关系表结构，二者同属"让模型处理结构化信息"但路径不同：DeepSeek 系走"训练 LLM 内化结构推理"，rLLM 走"外部 GNN/TNN 承载结构、LLM 仅做标注/增广"。可视为 **结构化推理的两条互补路线**。
- [[cuda-agent-large-scale-agentic-rl-for-high-performance-cuda-kernel-generation]] / [[search-r1-training-llms-to-reason-and-leverage-search-engines-with-reinforcement-learning]] — 这两者是 RL + 工具/数据 的训练范式；rLLM 不涉及 RL，但其 "Combine" 策略（LLM 标注 → 下游模型）与 Search-R1（LLM 调用搜索引擎作为外部工具）在"LLM 与外部模块协作"的架构思想上有弱类比，仅作谱系旁注。
- [[bertopic-neural-topic-modeling-with-a-class-based-tf-idf-procedure]] — 同为非核心 LLM 训练的独立数据方法（主题建模 vs 关系表学习），二者都是 AICO-knowledge 中的"正交数据方法"分支，可并列放置，无直接机制关联。

**结论**：本文在 AICO-knowledge 谱系中相对独立，主要价值是补全"结构化/表格数据学习"这一正交分支；与 LLM 综述、结构化推理论文有接口级联系，与 RL+工具类论文仅有思想类比。

## 局限与边界

- **实验规模极小**：仅 TML1M 上的 BRIDGE 演示性实验（§5），三个数据集只有单点准确率，无消融、无方差控制说明、无多 seed 详细曲线；脚注6 明确承认 GNN 类方法因无法直接处理表数据而未参与对比，导致对比表缺一类强基线。
- **BRIDGE 建模能力有损**：BRIDGE 只保留单张关系表，其余表压缩为 dense embedding，相比 RDL [9] 的全异构图建模会损失多跳关系信息；作者坦承这是为简化而做的取舍（§3 开头），并未给出与 RDL 的直接实验对比来量化这一损失。
- **LLM 作用被刻意边缘化**：论文反对直接用 LLM 处理关系表（成本论证 §1），因此 LLM 仅作为 Predictor/Enhancer 出现，未探索 LLM + 结构化数据的更深融合（如 LLM 端到端表理解、table-grounded reasoning）；这是方法论选择而非技术突破。
- **成本论证的假设粗放（§A.1）**：token 成本估算基于"均匀喂 GPT-3.5 Turbo、忽略输出 token、视频每秒一帧抽样"等强假设；$5,000 trillion / 214× GDP 这类数字的量级可信但精度有限，仅作动机论证。
- **数据集偏小且任务单一**：SJTUTables 三个数据集均为单标签分类、每类仅 20 标注样本；与 RelBench 的商业任务复杂度相比规模与任务多样性不足，作者自己也建议后续去 RelBench 评估（§4.2 末）。
- **未解决**：关系表的 schema 演化、跨数据库异构、SQL 注入式噪声、超大表（亿级行）的工程效率（§6 结论提及"plan to optimize relevant data structures to improve system efficiency"作为未来工作，即当前效率未优化）。
