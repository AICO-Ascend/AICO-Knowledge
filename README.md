# AICO-knowledge

收集整理 AI 相关技术论文、代码仓来源、分析文章等，建成可「快速插图 + 引用」的知识库。

## 目录

```
AICO-knowledge/
├── papers/                       # 源 PDF（50 篇，命名 <slug>.pdf）
├── papers_effective.md           # ⭐ 主干净索引（论文清单 + 链接 + 本地文件状态）
├── papers_download_list.txt      # slug | abs_url | pdf_url
├── archive/                      # 原始素材（清洗前索引、Moonlight 剪藏原文）
├── skills/paper-extraction/      # ⭐ 可复用 skill：清洗→校验下载→深度萃取→插图引用
│   ├── SKILL.md                  #   工作流 + 决策树 + 约定
│   ├── extract_phase1.py         #   全量深度萃取（文本+图表+caption，merge MiniMax）
│   └── chunk_download.py         #   arxiv 大文件分块续传
└── extraction/                   # 生成的知识库
    ├── <slug>.md                 #   每篇结构化解析（Obsidian-flavored）
    ├── fulltext/<slug>.txt       #   全文纯文本（grep 检索）
    ├── assets/<slug>-pNN.png     #   图表页渲染（150 DPI）
    ├── figures_index.md          #   ⭐ 图表素材索引（精选深度解读 + 主题分类）
    ├── minimax_captions.json     #   MiniMax 多模态架构图技术解读
    └── README.md                 #   知识库使用说明
```

## 用法

**写技术报告/论文总结时插图引用**：开 `extraction/figures_index.md` → 「⭐ 精选架构图」挑图 → `![[assets/...png]]` 插入 → `[论文, Fig.N, p.X, arXiv:ID]` 引用。详见 `extraction/README.md`。

**新增论文/刷新**：按 `skills/paper-extraction/SKILL.md` 的 5 阶段工作流走（清洗→下载→萃取→MiniMax 解读→推送）。

**其他知识库复用此 skill**：把 `skills/paper-extraction/` 拷到任意论文仓即可（脚本路径相对，clone 即用）。

## 现状

- 55 篇论文全部深度萃取（340 张图、17 张核心架构图 MiniMax 多模态深度解读）
- 全部 PDF 校验有效（verify_pdfs.py 报 0 截断）；chunk_download.py（256KB 块+15 重试）解决了 arxiv 大文件截断
