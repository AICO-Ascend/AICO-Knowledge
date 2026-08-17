# AICO-knowledge

收集整理 AI 相关技术论文、代码仓来源、分析文章等，建成可「快速插图 + 引用」的深度加工知识库（图/公式/全文均可被工程直接取用，Obsidian 图谱化 + RAG 友好）。

**TL;DR**：
- 📥 **刷新知识库**：更新 `archive/paper_source_moonlight.md` → `python3 skills/paper-extraction/sync_from_source.py --push`（一条命令全自动）
- 🔍 **查询取用**：`python3 skills/paper-extraction/kb_query.py search|fig|formula|topics|info|stats <关键词> [--json]`
- 🗺️ **浏览图谱**：Obsidian 打开本仓 → `extraction/MOC.md`

## 目录

```
AICO-knowledge/
├── papers/                       # 源 PDF（61 篇，命名 <slug>.pdf）
├── papers_effective.md           # ⭐ 主干净索引（论文清单 + 链接 + 本地文件状态）
├── papers_download_list.txt      # slug | abs_url | pdf_url
├── archive/                      # 原始素材（paper_source_moonlight.md = 唯一需人工维护的文件）
├── skills/paper-extraction/      # ⭐ 可复用 skill（脚本路径相对，clone 即用）
│   ├── SKILL.md                  #   工作流手册（日常同步入口 + agent 收尾 + 决策树 + 踩坑）
│   ├── sync_from_source.py       #   ⭐ 一键同步编排（源表→diff→下载→萃取→推送，幂等）
│   ├── kb_query.py               #   统一查询 CLI（search/fig/formula/topics/info/stats，--json）
│   ├── extract_phase1.py         #   全量深度萃取（文本+图表+公式+相关论文+MOC+manifest）
│   ├── eprint_formulas.py        #   arxiv e-print LaTeX 源公式抽取（失败冷却 3 天）
│   ├── chunk_download.py         #   arxiv 分块续传下载（256KB 块+15 重试，jobs 文件驱动）
│   └── verify_pdfs.py            #   PDF 体检（截断/损坏/缺失/孤儿，CI gate）
└── extraction/                   # 生成的知识库
    ├── <slug>.md                 #   每篇结构化解析（Obsidian-flavored：摘要/图表/公式/相关论文）
    ├── fulltext/<slug>.txt       #   全文纯文本（grep 检索 / RAG chunk 源）
    ├── assets/<slug>-pNN.png     #   图表页渲染（150 DPI）
    ├── figures_index.md          #   ⭐ 图表素材索引（⭐精选深度解读 + 主题分类 + 按论文）
    ├── MOC.md                    #   🗺️ 主题图谱导航（wikilink 节点，Obsidian 图谱可视化）
    ├── papers.json               #   机器可读 manifest（RAG/程序化摄取入口）
    ├── formulas.json             #   LaTeX 源公式库（$$ 块可直接粘贴）
    ├── minimax_captions.json     #   架构图多模态深度解读
    ├── sync_report.md            #   最近一次同步报告（新增/待确认/失败/待解读）
    └── README.md                 #   知识库使用说明 + 外部工程接入指南
```

## 用法

**刷新（唯一人工动作 = 更新源文件）**：

```bash
# 1. 把新的 Moonlight 文献库导出覆盖 archive/paper_source_moonlight.md
# 2. 一条命令完成全链路并推送远端：
python3 skills/paper-extraction/sync_from_source.py --push
```

自动完成：diff 源表（Jaccard 模糊匹配）→ 新标题 arxiv 解析 → 分块下载+体检 → 摘要抓取+索引追加 → 深度萃取 → LaTeX 公式 → `sync_report.md` → commit+push（token 取 env `AICO_GITCODE_TOKEN` 或 `~/.config/aico/gitcode_token`，推完抹除）。幂等，无新增 ~40s。剩余两件需判断的事（待确认条目、架构图深度解读）列在 `sync_report.md` 里，见 `SKILL.md`「同步后的 agent 收尾」。

**写技术报告/论文总结时插图引用**：`kb_query.py fig <关键词>` → 拿 `![[assets/...png]]` + `[slug, Fig.N, p.X]` 引用串；或开 `extraction/figures_index.md`「⭐ 精选架构图」挑图。详见 `extraction/README.md`。

**引用公式**：`kb_query.py formula <关键词>` → 复制 `$$` 块（arxiv LaTeX 源，直接渲染）。

**图谱浏览**：Obsidian 打开本仓，`extraction/MOC.md` 是总览节点；单篇 MD 内「相关论文」交叉链接自动成网。

**RAG 摄取**：读 `extraction/papers.json` manifest → 按 `fulltext/` 路径 chunk；或 `kb_query.py search --json`。

**其他工程接入**：本仓在共享 NFS 上，绝对路径直读零拷贝；接入指南+agent 提示词模板见 `extraction/README.md`「外部工程接入」。

**其他知识库复用此 skill**：把 `skills/paper-extraction/` 拷到任意论文仓即可。

## 文档
- `skills/paper-extraction/SKILL.md` — 操作手册（一键同步 + agent 收尾 + 决策树 + 约定 + 踩坑/效率）
- `EXPERIENCE.md` — 案例复盘（建库 + 增量刷新全过程踩坑与解法）
- `extraction/README.md` — 知识库使用说明 + 外部工程接入指南

## 现状（2026-08-17）

- **61 篇**论文全部深度萃取：**515 张图**、**22 张**核心架构图多模态深度解读、**48 篇 390 条** LaTeX 源公式
- 全部 PDF 校验有效（verify_pdfs.py 报 0 截断）
- 一键同步已上线并实测（源库 58 条 → 自动识别 2 条待确认，41s 完成全链路+自动推送）
- 主题覆盖：speculative decoding（10 篇成簇）、kv-cache、disaggregated-serving、sparse-attention、training、moe、rl、multimodal、long-context、architecture
