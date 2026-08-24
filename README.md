# AICO-Knowledge

> 69 篇 LLM 系统/推理/训练论文的**生产级深度萃取知识库**——每张图、每个表、每条公式都可被工程直接取用：裁剪单图 + MiniMax-M3 多模态解读 + arXiv LaTeX 权威公式 + 6 段一体化深读。Obsidian 图谱化 + RAG 友好。

![pipeline](docs/images/kb_pipeline.png)

## 为什么这个知识库不一样

普通论文仓 = 一堆 PDF + 摘要。本库对每篇论文做了**全要素深度加工**，三条铁律保证质量：

| 铁律 | 做法 | 效果 |
|---|---|---|
| **图/表理解全走多模态** | 所有架构图/数据流图/表格经 MiniMax-M3 vision 逐张解读，写进 `minimax_captions.json` | 不是"有图"，是"每张图都有可读的技术解读" |
| **公式以 arXiv LaTeX 源为权威** | e-print 源码抽取，禁止凭训练知识重写；无 LaTeX 源的论文公式裁成原文截图 | `$$` 块直接渲染、完全正确，可粘贴进报告 |
| **按论文维度一体化深读** | 全文+图+表+公式交织成 6 段结构，前后文一致 | 不是孤立片段，是吃透整篇的结构化笔记 |

## 萃取深度一图看懂

![coverage](docs/images/kb_coverage_stats.png)

- **682 张裁剪单图**（不再是整页截图——每张 figure 独立裁剪，可直接插入报告）
- **429 张裁剪表格**（表格第一次成为"可插入的图"，不再只是 Markdown 文本）
- **479 条 LaTeX 权威公式**（58 篇）+ **4 张公式截图**（无 LaTeX 源论文兜底，引用前核对）
- **1600+ 条 MiniMax-M3 多模态解读**（架构图/数据流图/表格逐张技术解读；全部裁剪图均为**图文联合解读**——论文正文引用段落 + 图片联合喂 M3，解读锚定原文论述）
- **69 篇 6 段深读笔记**（核心问题/关键创新点(机制+效果+精确数字+公式+图解读)/表格/对比/谱系/局限）
- **19 页原子概念页**（`wiki/concepts/`，跨论文累积综合 + 谱系嵌入，Obsidian 图谱 hub）

## 知识图谱（主题聚类 + 跨论文谱系）

![topic graph](docs/images/kb_topic_graph.png)

> 节点=论文，颜色=主主题，边=共享主题。Obsidian 打开本仓 → `extraction/MOC.md` 可视化交互式图谱；跨论文演进谱系见 `extraction/moc_relations.md`。

## 快速取用（生产级工作流）

**统一查询入口 `kb_query.py`**（全部子命令支持 `--json`，agent/RAG 程序化消费）；**LLM 读库先读 `extraction/index.md`**（内容目录，按主题定位论文/概念页，再钻取细节）：

```bash
KB=skills/paper-extraction/kb_query.py
python3 $KB stats                        # 库总量
python3 $KB search speculative decoding  # 论文检索
python3 $KB fig moe dispatch             # 按 caption 找图 → 裁剪图 embed + 引用串
python3 $KB formula softmax              # 按内容找 LaTeX 公式（$$ 直贴，权威正确）
python3 $KB topics                       # 主题 → 论文映射
python3 $KB info <slug>                  # 单篇全卡片
```

> 📚 **LLM Wiki 三层架构**（参考 [Karpathy LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)）：raw（`papers/` 不可变）→ wiki（`extraction/` + `wiki/concepts/`，LLM 全权维护）→ schema（`SKILL.md`）。三个操作：**Ingest**=`full_pipeline.py` 一条命令；**Query**=先读 index.md 再钻取，好答案回填 `wiki/` 复利增长；**Lint**=定期体检（一致性/缺解读/概念页覆盖）。编年动态见 `extraction/log.md`（`grep "^## \[" extraction/log.md | tail -5`）。

**写报告插图**：`kb_query.py fig <关键词>` → 拿裁剪单图 `![[assets/crops/<slug>-figNN.png]]` + `[slug, Fig.N, p.X]` 引用串。图已是干净单元素裁剪，不用再裁。

**引用表格**：单篇 MD 的「表格」节有裁剪表格图 + caption + M3 解读，直接 embed。

**引用公式**：`kb_query.py formula <关键词>` → 复制 `$$` 块（arXiv LaTeX 源，权威正确）。无 LaTeX 源的论文在「关键公式（原文截图）」节。

**取深度分析**：`extraction/deep/<slug>.md`（6 段一体化，图表+公式已织入，前后文一致）。

## 目录结构

```
AICO-knowledge/
├── papers/                          # 源 PDF（69 篇）
├── papers_effective.md              # 主索引（清单+链接+本地状态）
├── skills/paper-extraction/         # ⭐ 可复用 skill（clone 即用）
│   ├── full_pipeline.py             #   ⭐ 全链路一条命令（source→KB→push）
│   ├── sync_from_source.py          #   源表 diff→下载→萃取→推送
│   ├── extract_phase1.py            #   深度萃取（merge 解读+公式+裁剪图）
│   ├── extract_visuals.py           #   图/表/公式区域裁剪成单图
│   ├── render_kb_graph.py           #   知识图谱+覆盖统计图生成
│   ├── m3_caption.py                #   MiniMax-M3 图/表多模态解读
│   ├── eprint_formulas.py           #   arXiv e-print LaTeX 公式抽取
│   ├── kb_query.py                  #   统一查询 CLI（--json）
│   ├── wiki_index.py                #   📚 LLM Wiki 簿记层（index.md + 概念页种子 + log.md）
│   ├── chunk_download.py            #   分块续传下载
│   └── verify_pdfs.py               #   PDF 体检（CI gate）
├── wiki/
│   └── concepts/<slug>.md           # 📚 19 页原子概念页（跨论文综合，图谱 hub）
├── extraction/                      # 生成的知识库
│   ├── index.md                     #   📚 LLM-reads-first 内容目录（先读定位再钻取）
│   ├── log.md                       #   📚 编年日志（ingest/lint/pipeline 动态）
│   ├── <slug>.md                    #   每篇结构化解析（摘要/裁剪图/表格/公式/相关论文）
│   ├── deep/<slug>.md               #   ⭐ 6 段一体化深读（图/表/公式织入）
│   ├── fulltext/<slug>.txt          #   全文纯文本（RAG chunk 源）
│   ├── assets/<slug>-pNN.png        #   整页渲染（150 DPI）
│   ├── assets/crops/<slug>-figNN.png  # ⭐ 裁剪单图（报告直接插入）
│   ├── assets/crops/<slug>-tabNN.png  # ⭐ 裁剪表格
│   ├── assets/crops/<slug>-eqNN.png   # ⭐ 公式截图（无 LaTeX 源兜底）
│   ├── figures_index.md             #   图表主索引（⭐精选+主题分类+按论文）
│   ├── MOC.md                       #   主题图谱导航（Obsidian 图谱视图）
│   ├── moc_relations.md             #   跨论文关系谱系（人工维护）
│   ├── papers.json                  #   机器可读 manifest（RAG 摄取入口）
│   ├── formulas.json                #   LaTeX 公式库（58 篇 479 条，权威源）
│   ├── visuals.json                 #   裁剪图 manifest（fig/tab/eq）
│   └── minimax_captions.json        #   多模态解读（1600+ 条）
└── docs/images/                     # 知识图谱/覆盖统计/流水线图（README 嵌入）
```

## 增量更新（一条命令）

唯一人工动作 = 更新源文件（`archive/paper_source_moonlight.bib` 或 `.md`），然后：

```bash
python3 skills/paper-extraction/full_pipeline.py --push
```

自动：源表 diff → arXiv 解析 → 分块下载+体检 → 萃取 → **图/表/公式裁剪** → **MiniMax-M3 批量解读新增** → LaTeX 公式 → 深读队列 → token-safe push。幂等，无新增 ~1-2 分钟。

## 主题覆盖

speculative decoding（10 篇成簇：EAGLE 全家族/Medusa/SpecExtend/LongSpec…）｜kv-cache（Mooncake/CacheBlend/Prefill-as-a-Service…）｜training（Megatron/MegaScale/ZeRO/Muon…）｜moe（Scalable-MoE/OmniMoE…）｜rl（DeepSeek-R1/GRPO/DAPO/AREAL/HybridFlow/CUDA-Agent…）｜multimodal（Qwen3-VL/Kimi-VL…）｜disaggregated-serving（Sarathi/NanoFlow/SGLang…）｜long-context / sparse-attention / architecture / topic-modeling / relational-table

## 文档

- `skills/paper-extraction/SKILL.md` — 操作手册（全链路 + agent 收尾 + 决策树 + 踩坑）
- `skills/paper-extraction/DEEP_LEARNING_PROTOCOL.md` — 夜间深度学习规范
- `extraction/README.md` — 知识库使用说明 + 外部工程接入指南
- `EXPERIENCE.md` — 建库全过程踩坑与解法复盘

---

**现状（2026-08-24）**：69 唯一论文 ｜ 682 裁剪图 + 429 裁剪表 + 4 公式截图 ｜ 479 LaTeX 公式（58 篇）｜ 1600+ MiniMax-M3 解读（全部裁剪图 = 图文联合解读）｜ 69 篇 6 段深读 ｜ 19 页概念页 + index.md/log.md 簿记层（Karpathy LLM Wiki 落地）｜ 96 张坏字体/坏结构论文裁剪由 ar5iv 原图/手工区域保护 ｜ PDF 0 截断 ｜ 三铁律全绿。
