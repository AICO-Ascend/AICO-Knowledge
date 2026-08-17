---
name: paper-extraction
description: Curate a paper knowledge base — ONE-COMMAND source sync (moonlight export → diff → resolve → download → extract → formulas → report → push), plus deep-extract text+figures+formulas, multimodal figure interpretation, quick-insert figure library with citations, and a unified query CLI for other projects. Use when managing/refreshing a repo of academic papers.
---

# paper-extraction

Turn a folder of source-paper clippings + PDFs into a clean, deep-extracted knowledge base optimized for **inserting technical figures + citing sources** into reports — and keep it fresh with **one command** when the source list changes.

Proven on `AICO-knowledge` (61 papers). Portable: scripts derive repo root from their own path; clone `skills/paper-extraction/` into any paper repo.

## ⭐ 日常同步（唯一入口）

用户更新了 `archive/paper_source_moonlight.md`（Moonlight 文献库导出）后：

```bash
cd /mnt/project/g00952465/AICO-knowledge
python3 skills/paper-extraction/sync_from_source.py --push
```

**自动完成**：解析源表 → 与 `papers_effective.md` 模糊 diff（Jaccard≥0.6 同篇）→ 新标题 arxiv 解析（title-search scrape，相似度≥0.8 自动采纳）→ HEAD 查大小 → `chunk_dl` 分块下载（256KB/15 重试）→ 页数体检（失败重试 1 次）→ abs 页抓摘要 → 追加索引行+下载清单+头部计数 → `extract_phase1.py`（图/相关论文/MOC/papers.json）→ `eprint_formulas.py`（LaTeX 公式，失败冷却 3 天）→ 写 `extraction/sync_report.md` → commit+push（token 取 `AICO_GITCODE_TOKEN` 或 `~/.config/aico/gitcode_token`，推完抹除 push URL）。

**幂等**：随时重跑安全；无新增时 ~30s 完成。

### 同步后的 agent 收尾（脚本不做，由 Claude session 做）

读 `extraction/sync_report.md`：
1. **⚠️ 待确认**：arxiv 解析失败的条目——web 搜索人工解析（找到 arxiv ID 就手动加行进 `papers_effective.md` + 下载 + 重跑本脚本；确认非论文就如实报告用户）。**绝不猜来源**。
2. **🖼️ 架构图深度解读**：对新增论文，挑 caption 含 overview/architecture/framework/illustration 的图，`Read` PNG（或 MiniMax `understand_image`，key 有效时）写解读 → 追加 `extraction/minimax_captions.json`（key=`extraction/assets/<slug>-pNN.png`）→ 重跑 `extract_phase1.py` 合并 → 再次 `--push`。
3. 若 `--push` 未带：手动 commit + push（pull --rebase 先行）。

## Repo layout (convention)

```
<repo>/
├── papers/                      # source PDFs (named <slug>.pdf)
├── papers_effective.md          # ⭐ master clean index (source of truth)
├── papers_download_list.txt     # slug | abs_url | pdf_url
├── archive/                     # raw provenance (paper_source_moonlight.md = 用户唯一要维护的文件)
├── skills/paper-extraction/     # THIS skill + scripts
│   ├── SKILL.md                 #   本文件
│   ├── sync_from_source.py      #   ⭐ 一键同步编排（日常入口）
│   ├── extract_phase1.py        #   深度萃取（文本+图+相关论文+MOC+manifest，merge 解读+公式）
│   ├── eprint_formulas.py       #   arxiv e-print LaTeX 公式抽取
│   ├── chunk_download.py        #   分块续传下载（jobs 文件/命令行驱动）
│   ├── verify_pdfs.py           #   PDF 体检（截断/损坏/缺失/孤儿）
│   └── kb_query.py              #   统一查询 CLI（外部工程/RAG 消费入口）
└── extraction/                  # generated knowledge base
    ├── <slug>.md                # per-paper structured (Obsidian-flavored)
    ├── fulltext/<slug>.txt      # full text for grep / RAG chunk 源
    ├── assets/<slug>-pNN.png    # figure-page renders (150 DPI)
    ├── figures_index.md         # ⭐ figure library
    ├── MOC.md                   # 🗺️ topic graph (wikilinks, Obsidian graph view)
    ├── papers.json              # machine-readable manifest (RAG ingestion)
    ├── formulas.json            # LaTeX formula library
    ├── minimax_captions.json    # deep-captioned figures (png→解读)
    ├── sync_report.md           # 最近一次同步报告（待确认/失败/待解读）
    └── README.md                # 使用说明 + 外部工程接入
```

## 查询（任何工程）

```bash
KB=/mnt/project/g00952465/AICO-knowledge/skills/paper-extraction/kb_query.py
python3 $KB search|fig|formula|topics|info|stats <kw> [--json]
```
详见 `extraction/README.md`「外部工程接入」。

## 非常规阶段（首次建库 / 修坏档时手动跑）

### Phase 0 — Clean source index → `papers_effective.md`
Source clippings carry garbage: base64 images, broken `![\](...)` markers, mangled columns (date↔abstract swapped). Realign: detect date (`\d{4}[/-]\d{1,2}[/-]\d{1,2}`) wherever it landed; abstract = long non-date field. 7 cols: `| # | title | date | abs_link | pdf_link | local_file | abstract |`.

### Phase 3 — Verify links + fix missing/truncated PDFs
**Detect truncation**: `%PDF-` header present but `fitz.open(f).page_count == 0`. Choose download method by case:

| Symptom | Cause | Fix |
|---|---|---|
| 404 / HTML page | wrong arxiv ID | scrape `https://arxiv.org/abs/<id>` HTML `<title>` (arxiv API `export.arxiv.org/api/query` returns empty — don't use) |
| HTTP 200 + small + pages=0 | parallel batch rate-limited → truncated | retry **sequential** browser UA, 1 at a time |
| Large PDF (>3MB), truncates ~1MB | flaky network caps connection | `chunk_download.py` — 256KB Range chunks, 15 retries, 90s timeout |
| OpenReview `ChallengeRequiredError` | Cloudflare JS challenge | server can't pass → user downloads in browser, drops PDF into `papers/` |
| ACM `403` | subscription paywall | mark `✗ ACM 订阅墙`, keep link |
| Chinese-title PDF | auto-slug drops CJK | keep English transliteration, don't slugify |

After download: update index local-file column + counts; append `papers_download_list.txt`; re-run extract.

## Conventions (sticky — follow exactly)

- **Slug**: title → lowercase → drop commas → non-alnum → `-` → collapse. Filename = `<slug>.pdf`.
- **Citation template**: `[<slug>, Fig.<N>, p.<X>, arXiv:<ID>]` — fields in per-paper MD frontmatter.
- **Figure embed**: Obsidian `![[assets/<slug>-pNN.png]]`.
- **Output MD**: Obsidian-flavored (frontmatter, `> [!abstract]`, `> [!quote]`, `> [!tip]`, wikilinks).
- **Git push**: token from env/file only, NEVER in repo; push URL set→push→strip; always `pull --rebase` first.

## Pitfalls & efficiency (bake these in — they cost real time)

**Run `verify_pdfs.py` first** on any repair task — 0-page `%PDF` files are *truncated downloads*, not "missing". Don't re-extract broken PDFs; download-fix first.

**Don't parallel-`curl` arxiv PDFs** — rate-limit truncation (~13/50 came back 0-page). Use `chunk_download.py` for everything; sequential-looking but avoids rework. e-print (LaTeX 源) 可以 8 线程（有 deadline+重试+冷却兜底）。

**arxiv large files (>3MB)**: per-connection ~1MB ceiling on this network. 256KB chunks + 15 retries is the only reliable path (verified up to 12.3MB). If it still stalls → mark `✗ 网络`, user drops PDF in `papers/`.

**arxiv API returns empty XML** — scrape abs-page HTML instead.

**Don't capture binary PDFs in bash `$(curl ...)`** — null bytes stripped → corrupt. Use `curl -o` / urllib.

**PDF 文本抽公式会碎**（多行公式断成残片）——公式必须走 arxiv e-print LaTeX 源（`eprint_formulas.py`）；启发式 PDF 抽取仅 fallback。eprint 失败有 `.cache/eprints/failed.json` 冷却 3 天，`--retry-failed` 强制。

**Two-column PDFs scramble `get_text`** → abstract regex may miss; prefer abs-page scrape.

**Figure-page ≠ architecture figure** — pick by caption keywords (overview/architecture/framework/design/illustration), not figure number.

**Featured-figure dedupe by PNG path** — same PNG hosts multiple figure numbers.

**Duplicate index rows** (GEPA twice) → one slug, both rows point at it.

**`pkill -f <script>` 会匹配自身命令行自杀（exit 144）**——用 `pgrep -f 'name[.]py'` 括号技巧，且同条命令里别再出现脚本的纯文本名。

**urlopen timeout 是 per-socket-op**——dribble 连接能挂死永远；eprint/PDF 下载都要包**总 deadline**（180s）。

**Efficiency levers**:
- MiniMax/Read 深度解读：4-5 张图并行/批处理。
- extract_phase1.py 幂等 + 跳过已存在 PNG —— 重跑免费。
- eprint_formulas.py 跳过确定性结果（含空）；只跑新增。
- Abstract：abs 页 scrape 可靠，PDF 两栏解析脆弱。

## File-integrity helpers

- `verify_pdfs.py` — truncated/corrupt/missing/orphan 报告，exit 1 if bad（CI gate）。
- `chunk_download.py` — `chunk_download.py jobs.txt` 或 `<aid> <slug> ...`。
