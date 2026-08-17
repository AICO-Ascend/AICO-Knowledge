# AICO-knowledge

收集整理 AI 相关技术论文、代码仓来源、分析文章等，建成可「快速插图 + 引用」的深度加工知识库（图/公式/全文均可被工程直接取用，Obsidian 图谱化 + RAG 友好）。

## 目录

```
AICO-knowledge/
├── papers/                       # 源 PDF（61 篇，命名 <slug>.pdf）
├── papers_effective.md           # ⭐ 主干净索引（论文清单 + 链接 + 本地文件状态）
├── papers_download_list.txt      # slug | abs_url | pdf_url
├── archive/                      # 原始素材（清洗前索引、Moonlight 剪藏原文）
├── skills/paper-extraction/      # ⭐ 可复用 skill：清洗→校验下载→深度萃取→插图引用
│   ├── SKILL.md                  #   工作流手册（日常同步入口 + 决策树 + 约定 + 踩坑）
│   ├── sync_from_source.py       #   ⭐ 一键同步编排（源表→diff→下载→萃取→推送）
│   ├── kb_query.py               #   统一查询 CLI（search/fig/formula/topics，--json）
│   ├── extract_phase1.py         #   全量深度萃取（文本+图表+公式+相关论文+MOC+manifest）
│   ├── eprint_formulas.py        #   arxiv e-print LaTeX 源公式抽取
│   ├── chunk_download.py         #   arxiv 分块续传下载（jobs 文件/命令行驱动）
│   └── verify_pdfs.py            #   PDF 体检（截断/损坏/缺失/孤儿）
└── extraction/                   # 生成的知识库
    ├── <slug>.md                 #   每篇结构化解析（Obsidian-flavored：摘要/图表/公式/相关论文）
    ├── fulltext/<slug>.txt       #   全文纯文本（grep 检索 / RAG chunk 源）
    ├── assets/<slug>-pNN.png     #   图表页渲染（150 DPI）
    ├── figures_index.md          #   ⭐ 图表素材索引（精选深度解读 + 主题分类）
    ├── MOC.md                    #   🗺️ 主题图谱导航（wikilink 节点，Obsidian 图谱可视化）
    ├── papers.json               #   机器可读 manifest（RAG/程序化摄取入口）
    ├── formulas.json             #   LaTeX 源公式库（$$ 块可直接粘贴）
    ├── minimax_captions.json     #   架构图多模态深度解读
    └── README.md                 #   知识库使用说明
```

## 用法

**写技术报告/论文总结时插图引用**：开 `extraction/figures_index.md` → 「⭐ 精选架构图」挑图 → `![[assets/...png]]` 插入 → `[论文, Fig.N, p.X, arXiv:ID]` 引用。详见 `extraction/README.md`。

**引用公式**：单篇 MD 的「关键公式」节是 arxiv LaTeX 源抽出的 `$$` 块，直接粘贴即渲染。

**图谱浏览**：Obsidian 打开本仓，`extraction/MOC.md` 是总览节点；单篇 MD 内「相关论文」交叉链接自动成网。

**RAG 摄取**：读 `extraction/papers.json` manifest → 按 `fulltext/` 路径 chunk。

**新增论文/刷新**：只需更新 `archive/paper_source_moonlight.md`（Moonlight 文献库导出），然后：

```bash
python3 skills/paper-extraction/sync_from_source.py --push
```

一条命令全自动：diff 源表 → 解析新论文 arxiv → 下载体检 → 更新索引 → 深度萃取（图/公式/相关论文/MOC）→ 同步报告 → 推送远端。详见 `skills/paper-extraction/SKILL.md`。

**其他知识库复用此 skill**：把 `skills/paper-extraction/` 拷到任意论文仓即可（脚本路径相对，clone 即用）。

## 文档
- `skills/paper-extraction/SKILL.md` — 操作手册（5 阶段工作流 + 源列表同步 + 决策树 + 约定 + 踩坑/效率）
- `EXPERIENCE.md` — 案例复盘（建库 + 增量刷新全过程踩坑与解法）

## 现状

- 61 篇论文全部深度萃取（515 张图、22 张核心架构图多模态深度解读、LaTeX 公式库）
- 全部 PDF 校验有效（verify_pdfs.py 报 0 截断）；chunk_download.py（256KB 块+15 重试）解决了 arxiv 大文件截断
- 2026-08-16 增量：Kimi K3 / PrfaaS / LongSpec / SpecExtend / LLM 综述（源库 58 条 diff 出 5 新，2 条歧义待确认）
