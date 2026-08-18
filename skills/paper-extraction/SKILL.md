---
name: paper-extraction
description: Curate a paper knowledge base — ONE-COMMAND source sync (moonlight export → diff → resolve → download → extract → formulas → report → push), plus deep-extract text+figures+formulas, multimodal figure interpretation, quick-insert figure library with citations, and a unified query CLI for other projects. Use when managing/refreshing a repo of academic papers.
---

# paper-extraction

Turn a folder of source-paper clippings + PDFs into a clean, deep-extracted knowledge base optimized for **inserting technical figures + citing sources** into reports — and keep it fresh with **one command** when the source list changes.

Proven on `AICO-knowledge` (61 papers). Portable: scripts derive repo root from their own path; clone `skills/paper-extraction/` into any paper repo.

## ⭐ 日常同步（唯一入口）

**输入**（用户唯一要维护的文件，二选一，`.bib` 优先）：

- **首选 `archive/paper_source_moonlight.bib`** — Moonlight「文献库」→ 右上设置每页 100 行 → 全选 → 导出 → **BibTeX**。结构化、标题完整、常带 arxiv eprint/url + abstract，解析 100% 确定性（无乱码/无截断/无需标题搜索）。
- 回退 `archive/paper_source_moonlight.md` — 旧网页剪藏，带 base64/列错位/标题截断（会产生「⚠️ 待确认」行），仅在无 .bib 时用。

```bash
cd /mnt/project/g00952465/AICO-knowledge
python3 skills/paper-extraction/parse_moonlight_bib.py     # 可选 dry-run：看 .bib 解析出几条
python3 skills/paper-extraction/sync_from_source.py --push
```

**自动完成**：解析源表 → 与 `papers_effective.md` 模糊 diff（Jaccard≥0.6 同篇）→ 新标题 arxiv 解析（title-search scrape，相似度≥0.8 自动采纳）→ HEAD 查大小 → `chunk_dl` 分块下载（256KB/15 重试）→ 页数体检（失败重试 1 次）→ abs 页抓摘要 → 追加索引行+下载清单+头部计数 → `extract_phase1.py`（图/相关论文/MOC/papers.json）→ `eprint_formulas.py`（LaTeX 公式，失败冷却 3 天）→ 写 `extraction/sync_report.md` → commit+push（token 取 `AICO_GITCODE_TOKEN` 或 `~/.config/aico/gitcode_token`，推完抹除 push URL）。

**幂等**：随时重跑安全；无新增时 ~30s 完成。

## 🔁 可移植性 / 换模型 / 一次搞定

**这个 skill 的「调教」分两层**：(1) 脚本（`sync_from_source.py`/`extract_phase1.py`/`eprint_formulas.py`/`kb_query.py`/`m3_caption.py`/`chunk_download.py`/`verify_pdfs.py`）—— 100% 确定性 Python，模型无关，换任何主模型都不变；(2) agent 推理（读 SKILL.md 的 pitfall、挑架构图、解析待确认）—— 跟模型强弱相关。**让能力可复制的本质 = 把判断尽量搬进脚本，让 agent 按清单执行而非临场推理。** 已落地的几手：

- **BibTeX 源**（上节）消除了最模型依赖的两步：Phase-0 垃圾清理 + arxiv 标题搜索（标题截断→待确认的根因）。弱模型只需 `--push`，不再做判断。
- **`m3_caption.py --model <m>` / `M3_MODEL` env**：模型可一行替换，默认 `MiniMax-M3`（多模态解读）。**吃图模型**：`MiniMax-M3`、`doubao-seed-2.1-pro`；`glm-5.2` / `deepseek-v4-*` 等仅文本（喂图返回 400）——图解读务必用吃图模型。换模型不换脚本。
- **小上下文模型友好**：永远走 `kb_query.py` 取用，**不要整库载入 MD**（glm-5.2 有 1M 上下文能整库 hold，换小窗模型必须用 `kb_query search|fig|formula` 按需取）。
- **一次搞掉的兜底 = 自检先行**：每次开干前跑这三条，全绿才继续，避免中途因环境问题返工——

  ```bash
  # ① 网关连通（glm-5.2 文本 + MiniMax-M3 文本各 say ok）
  # ② kb_query stats  ③ git clean
  python3 - <<'PY'
  import json,os,urllib.request
  U=os.environ["VOLC_GATEWAY_URL"];K=os.environ["VOLC_GATEWAY_KEY"]
  def t(m,mt=200):
      b={"model":m,"messages":[{"role":"user","content":"say ok"}],"max_tokens":mt}
      r=urllib.request.Request(U,data=json.dumps(b).encode(),headers={"Authorization":f"Bearer {K}","Content-Type":"application/json"})
      print(m,"->",json.load(urllib.request.urlopen(r,timeout=120))["choices"][0]["message"]["content"][:20])
  t("glm-5.2");t("MiniMax-M3",4000)
  PY
  python3 skills/paper-extraction/kb_query.py stats | head -5
  git status --short   # 应为空
  ```

- **Moonlight 抓取自动化**（诚实评估）：用户在 Moonlight「文献库」点「导出→BibTeX」是 1 分钟操作，落到 `archive/*.bib` 后即全自动。Playwright 全自动抓取**不推荐**：需 Moonlight 登录态 + 翻页（每页 100 全选逐页）+ 可能 Cloudflare 挑战，凭证入仓/易碎/UI 变动即崩。真要「定时自主」只能做到 **cron 定时提醒导出**（`CronCreate` 每天提醒），实际抓取仍需登录态人工点一下——这是该站点的天然边界，不是脚本能突破的。

### 同步后的 agent 收尾（脚本不做，由 Claude session 做）

读 `extraction/sync_report.md`：
1. **⚠️ 待确认**：arxiv 解析失败的条目——web 搜索人工解析（找到 arxiv ID 就手动加行进 `papers_effective.md` + 下载 + 重跑本脚本；确认非论文就如实报告用户）。**绝不猜来源**。改用 `.bib` 源后这一类（标题截断碎片）基本不再产生。
2. **🖼️ 架构图深度解读**：对新增论文，挑 caption 含 overview/architecture/framework/illustration 的图，用 `m3_caption.py --save <png>`（蓝区火山网关 MiniMax-M3，自动追加 `extraction/minimax_captions.json`）或 Claude `Read` PNG 手写解读 → 重跑 `extract_phase1.py` 合并 → 再次 `--push`。
3. 若 `--push` 未带：手动 commit + push（pull --rebase 先行）。

## Repo layout (convention)

```
<repo>/
├── papers/                      # source PDFs (named <slug>.pdf)
├── papers_effective.md          # ⭐ master clean index (source of truth)
├── papers_download_list.txt     # slug | abs_url | pdf_url
├── archive/                     # raw provenance (paper_source_moonlight.bib = 用户唯一要维护的文件，BibTeX 导出)
├── skills/paper-extraction/     # THIS skill + scripts
│   ├── SKILL.md                 #   本文件
│   ├── sync_from_source.py      #   ⭐ 一键同步编排（日常入口）
│   ├── extract_phase1.py        #   深度萃取（文本+图+相关论文+MOC+manifest，merge 解读+公式）
│   ├── eprint_formulas.py       #   arxiv e-print LaTeX 公式抽取
│   ├── chunk_download.py        #   分块续传下载（jobs 文件/命令行驱动）
│   ├── verify_pdfs.py           #   PDF 体检（截断/损坏/缺失/孤儿）
│   ├── kb_query.py              #   统一查询 CLI（外部工程/RAG 消费入口）
│   └── m3_caption.py            #   火山网关 MiniMax-M3 图深度解读（--save 直写 captions.json）
└── extraction/                  # generated knowledge base
    ├── <slug>.md                # per-paper structured (Obsidian-flavored)
    ├── deep/<slug>.md           # ⭐ 全要素深读笔记（技术点/表格/跨论文关系，独立维护，extract 重跑不丢）
    ├── moc_relations.md         # ⭐ MOC 跨论文关系谱系（独立维护，MOC 嵌入 ![[moc_relations]]）
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

> **持久化铁律**：`extract_phase1.py` 每次全量重生成所有 `<slug>.md` 与 `MOC.md`——任何手写进这两处正文的内容会被下次重跑抹掉。深读产出**必须落独立文件**：技术点/表格/跨论文关系 → `extraction/deep/<slug>.md`（extract 检测后嵌入 `![[deep/<slug>]]`）；MOC 谱系 → `extraction/moc_relations.md`（嵌入 `![[moc_relations]]`）；图解读 → `minimax_captions.json`（extract 直读）。详见 `DEEP_LEARNING_PROTOCOL.md`。

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

**arxiv PDF 下载慢是常态（本环境 ~17 KB/s）**——不是被墙（HTTP 206 正常返回），是 arxiv 对本环境限速/网络质量差。`chunk_download.py` 已加：① 已下好的文件跳过（幂等重跑）；② 每文件 300s 总 deadline（防 dribble 挂死）；③ 每块 60s timeout × 4 重试。大文件（>3MB 技术报告）单篇可能 5-8 分钟；中断会留 0 字节/部分损坏文件，重跑自动重下。若 `chunk_dl` 仍卡，**并行 curl 兜底**：`curl -sL --max-time 1500 --retry 5 -A "Mozilla/5.0 Chrome/120" https://arxiv.org/pdf/<aid> -o papers/<slug>.pdf &`（4 篇并行，墙钟取最慢一篇）。e-print（LaTeX 源）可以 8 线程。

**arxiv API returns empty XML** — scrape abs-page HTML instead.

**arxiv title-search URL**：用 `https://arxiv.org/search/?query=<title>&searchtype=title`（裸参数）。旧版 `&abstracts=hide&size=10` 现在返回 **HTTP 400**（arxiv 改了，2026-08 验证）。且结果页标题带 `<span class="search-hit">` 标签，jaccard 前必须 `re.sub(r"<[^>]+>","",t)` 去标签，否则分数被压低（SGLang 0.62<0.8 → 误判未解析）。阈值 `>=0.8` 自动接受，截断碎片（"Delivery Note"）解析不到→留待确认（绝不猜来源）。

**Don't capture binary PDFs in bash `$(curl ...)`** — null bytes stripped → corrupt. Use `curl -o` / urllib.

**PDF 文本抽公式会碎**（多行公式断成残片）——公式必须走 arxiv e-print LaTeX 源（`eprint_formulas.py`）；启发式 PDF 抽取仅 fallback。eprint 失败有 `.cache/eprints/failed.json` 冷却 3 天，`--retry-failed` 强制。

**Two-column PDFs scramble `get_text`** → abstract regex may miss; prefer abs-page scrape.

**Figure-page ≠ architecture figure** — pick by caption keywords (overview/architecture/framework/design/illustration), not figure number.

**Featured-figure dedupe by PNG path** — same PNG hosts multiple figure numbers.

**Duplicate index rows** (GEPA twice) → one slug, both rows point at it.

**`pkill -f <script>` 会匹配自身命令行自杀（exit 144）**——用 `pgrep -f 'name[.]py'` 括号技巧，且同条命令里别再出现脚本的纯文本名。

**urlopen timeout 是 per-socket-op**——dribble 连接能挂死永远；eprint/PDF 下载都要包**总 deadline**（180s）。

**`eprint_formulas.py` 是 `sync_from_source.py` 的慢瓶颈**——step 7 给每篇新论文下载 arxiv LaTeX e-print tarball（多 MB × ~17KB/s）。8 篇新论文轻易 >9 分钟，会把整个 sync 拖到 bash timeout，**连 step 6（index 更新）都跑不到**，留下一份旧的 sync_report.md（"0 added"假象）。解法：当 sync 卡死看 log 无 "== 6. update index ==" 时，把 index 更新与 extract 从 sync 解耦——直接调 `abs_page_meta`+append rows+`extract_phase1`（无网络秒级），eprint 单独 `nohup python3 .../eprint_formulas.py > /tmp/eprint.log 2>&1 &` 后台跑，下次 extract 自动并入 formulas.json。

**管道缓冲吞日志**——`python ... | tee log | grep` 时下游管道让 python stdout 全缓冲，`log` 文件空、看不到进度，误以为进程没动。诊断网络/下载问题时直接 `python ... > log 2>&1`（无下游管道）或前台跑不带 grep。

**Bash 工具里 `&` 后台是陷阱**——`python ... &` 后跟 `echo`，Bash 工具见 echo 完即返回 exit 0，python 被 detach，输出进缓冲日志看不到、`wait` 也等不到。要真后台：用工具的 `run_in_background:true`，或 `nohup ... > /tmp/x.log 2>&1 &` + 显式 `disown` + `pgrep -f` 轮询。

**Efficiency levers**:
- 深度解读：4-5 张图并行/批处理（`m3_caption.py` 走火山网关 M3，或 Claude Read PNG）。
- extract_phase1.py 幂等 + 跳过已存在 PNG —— 重跑免费。
- eprint_formulas.py 跳过确定性结果（含空）；只跑新增。
- Abstract：abs 页 scrape 可靠，PDF 两栏解析脆弱。

## File-integrity helpers

- `verify_pdfs.py` — truncated/corrupt/missing/orphan 报告，exit 1 if bad（CI gate）。
- `chunk_download.py` — `chunk_download.py jobs.txt` 或 `<aid> <slug> ...`。
