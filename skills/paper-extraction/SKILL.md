---
name: paper-extraction
description: Curate a paper knowledge base — clean source clippings, verify/download missing/truncated PDFs (correct method per case), deep-extract text+figures+captions, MiniMax multimodal figure interpretation, build a quick-insert figure library with citations. Use when managing a repo of academic papers for tech-report/summary writing.
---

# paper-extraction

Turn a folder of source-paper clippings + PDFs into a clean, deep-extracted knowledge base optimized for **inserting technical figures + citing sources** into reports.

Encodes the workflow proven on `AICO-knowledge` (50 inference-accel papers). Portable: scripts derive repo root from their own path, so clone-and-run anywhere.

## When to use

- You have a batch of paper clippings (titles + abstracts + dates) and/or PDFs.
- Goal: a browsable figure library + per-paper structured notes, so writing a tech report = pick a figure + paste citation.
- Also: a previously-built KB needs refreshing (new papers added, or some PDFs found truncated).

## Repo layout (convention)

```
<repo>/
├── papers/                      # source PDFs (named <slug>.pdf)
├── papers_effective.md          # ⭐ master clean index (source of truth)
├── papers_download_list.txt     # slug | abs_url | pdf_url
├── archive/                     # raw provenance (pre-clean index, original clippings)
├── skills/paper-extraction/    # THIS skill + scripts
│   ├── SKILL.md
│   ├── extract_phase1.py
│   ├── chunk_download.py
│   └── verify_pdfs.py
└── extraction/                 # generated knowledge base
    ├── <slug>.md               # per-paper structured (Obsidian-flavored, 含相关论文交叉链接+关键公式)
    ├── fulltext/<slug>.txt     # full text for grep
    ├── assets/<slug>-pNN.png   # figure-page renders (150 DPI)
    ├── figures_index.md        # ⭐ figure library: featured + topic + per-paper
    ├── MOC.md                  # 🗺️ map of content: topic clusters + wikilinks (Obsidian graph)
    ├── papers.json             # machine-readable manifest (RAG/programmatic ingestion)
    ├── minimax_captions.json   # MiniMax deep-captioned figures (png→解读)
    └── README.md
```

## Workflow (5 phases)

### Phase 0 — Clean source index → `papers_effective.md`
Source clippings (e.g. Moonlight export) carry garbage: base64 images, `![\](...)` broken markers, mangled columns (date↔abstract swapped). Clean:
- Strip `![\]([base64图片已去除])`, `![](...)`, residual base64.
- Realign columns: detect date field (`\d{4}[/-]\d{1,2}[/-]\d{1,2}`) wherever it landed; abstract = the long non-date field. Emit 7-col table: `| # | title | date | abs_link | pdf_link | local_file | abstract |`.
- Preserve 2 "no-source" rows (non-arxiv: ACM paywall, OpenReview bot-block) with `✗` + reason — record the source link anyway.

### Phase 1 — Deep extract (cheap, all papers) → `extraction/`
`python3 skills/paper-extraction/extract_phase1.py`
Per paper (PyMuPDF):
- Full text → `extraction/fulltext/<slug>.txt` (for `grep`).
- Find figure pages (regex `Figure N:` per page) → render page @150 DPI → `extraction/assets/<slug>-pNN.png`.
- Extract caption (text after `Figure N:`), strip arxiv boilerplate.
- Heuristic key-formula extraction (lines with `=` + math symbols) → `## 关键公式` section (marked heuristic — verify against PDF page before quoting).
- Per-paper MD: frontmatter (title/authors/date/arxiv/slug/tags) + abstract + figures (embed `![[assets/...]]` + `[!quote] caption`) + 相关论文 wikilinks + fulltext pointer.
- Cross-paper graph: `## 相关论文` auto-computed (shared tags ×2 + title-token Jaccard, top 6) → Obsidian graph view works out of the box.
- Master `figures_index.md`: ⭐featured (deduped) + topic-tagged catalog + per-paper listing.
- `MOC.md`: topic clusters with wikilinks (map of content).
- `papers.json`: full manifest (num/title/slug/arxiv/tags/pages/figs/paths/char counts) — ingest this for RAG indexing.
Tags auto-derived: speculative / sparse-attention / kv-cache / moe / training / rl / multimodal / disaggregated-serving / long-context / architecture.

### Phase 2 — MiniMax multimodal deep-caption key architecture figures (optional, high-value)
For core method/architecture diagrams (pick by caption keywords: overview/architecture/framework/design/method, usually Fig.1-2), call `mcp__minimax-coding-plan__understand_image`:
- prompt: "Describe the main figure: architecture/components/data flow + technical takeaway ≤120 words + transcribe caption."
- Save to `extraction/minimax_captions.json` keyed by `assets/<slug>-pNN.png`.
- Re-run Phase 1 → merges `[!tip] 技术解读` into the figure entry; figures_index marks ⭐.
~10-15 calls covers the insert-worthy architecture figures; don't caption result charts/tables.

### Phase 3 — Verify links + fix missing/truncated PDFs
**Detect truncation**: PDF header `%PDF-` present but `fitz.open(f).page_count == 0` ⇒ truncated download (not HTML error). HEAD-verify all pdf URLs (HTTP 200 + content-type pdf).
**Choose download method by case** (the key decision tree):

| Symptom | Cause | Fix |
|---|---|---|
| 404 / HTML page | wrong arxiv ID (hallucinated) | scrape `https://arxiv.org/abs/<id>` HTML `<title>` to verify ID/title (arxiv API `export.arxiv.org/api/query` returns empty — don't use) |
| HTTP 200 + small + pages=0 | parallel batch got rate-limited → truncated | retry **sequential** with browser UA + Referer, 1 req at a time |
| Large PDF (>3MB), keeps truncating ~1MB | flaky network caps connection | `chunk_download.py` — HTTP Range 256KB chunks, 15 retries/chunk, 90s timeout |
| OpenReview `ChallengeRequiredError` / "Verifying your browser" | Cloudflare JS challenge | server curl/headless chromium can't pass → user downloads in browser, drops PDF into `papers/` |
| ACM `403` | subscription paywall | needs institutional auth; mark `✗ ACM 订阅墙`, keep link |
| Chinese-title PDF | auto-slug drops CJK → `950-npu` | keep English transliteration name, don't slugify |

After download: update `papers_effective.md` local-file column (`✗`→`✓ papers/<slug>.pdf`) + counts; append to `papers_download_list.txt`; re-run Phase 1 to extract the newly-valid PDF.

### Phase 4 — Commit + push
```bash
git add -A
git -c user.email=… -c user.name=… commit -m "extraction: …"
git remote set-url --push origin "https://<user>:<token>@gitcode.com/<user>/<repo>.git"
git push origin main
git remote set-url --push origin "https://gitcode.com/<user>/<repo>.git"  # strip token
```

## Conventions (sticky — follow exactly)

- **Slug**: paper title → lowercase → drop commas → other non-alnum → `-` → collapse. E.g. "Root Mean Square Layer Normalization" → `root-mean-square-layer-normalization`. Filename = `<slug>.pdf`.
- **Citation template**: `[<Title>, Fig.<N>, p.<X>, arXiv:<ID>]` — all in the per-paper MD frontmatter.
- **Figure embed**: Obsidian `![[assets/<slug>-pNN.png]]`.
- **Output MD**: Obsidian-flavored (frontmatter properties, `> [!abstract]`, `> [!quote]`, `> [!tip]`, wikilinks `[[<slug>]]`).
- **TOML gotcha (unrelated, but if you touch model pricing)**: keys with dots (`glm-5.2`) MUST be quoted `"glm-5.2"` or TOML parses nested table.

## Tools (this skill's scripts)

- `verify_pdfs.py` — file-integrity pre-check (truncated/corrupt/missing/orphan). **Run first.**
- `extract_phase1.py` — Phase 1 + merges MiniMax captions. Args: none (reads `papers_effective.md`, writes `extraction/` incl. MOC.md + papers.json). Path-relative.
- `chunk_download.py` — arxiv downloader. Args: `chunk_download.py jobs.txt` (lines `<arxiv_id> <slug>`) or inline pairs `chunk_download.py <aid> <slug> ...`. 256KB Range chunks + 15 retries/chunk + 90s timeout. Path-relative.
- MiniMax MCP: `understand_image(image_source=<local path or URL>, prompt=...)` — multimodal figure reading.

## Quick-insert workflow (the payoff)

1. Open `extraction/figures_index.md` → **⭐ 精选架构图** (MiniMax deep-captioned) for insert-ready core diagrams.
2. Insert: `![[assets/<slug>-pNN.png]]`.
3. Cite: `[<Title>, Fig.N, p.X, arXiv:ID]` from the per-paper MD.
4. Find original snippet: `grep -l "keyword" extraction/fulltext/*.txt` → read that paper's MD or fulltext.

## Refresh when new papers arrive

1. Add rows to `papers_effective.md` (+ `papers_download_list.txt`).
2. Download PDFs to `papers/` (Phase 3 decision tree).
3. `python3 skills/paper-extraction/extract_phase1.py` — picks up new PDFs, preserves existing `minimax_captions.json`.
4. (Optional) MiniMax-caption new architecture figures → append to `minimax_captions.json` → re-run Phase 1.
5. Commit + push.

## Source-list sync (autonomous full refresh — the "user drops a new source export" flow)

When the user updates the raw source list (e.g. `archive/paper_source_moonlight.md` — Moonlight library export), do the **whole pipeline autonomously**:

1. **Parse source**: extract `[title](https://www.themoonlight.io/paper/<uuid>) ... date` rows via regex. Moonlight exports are one long line per table row; the file also embeds full-text captures — ignore everything except the table rows. There are **no arxiv links in the export** — titles only.
2. **Diff vs `papers_effective.md`**: fuzzy title match (token-set Jaccard; >0.6 = same paper, 0.35-0.6 = eyeball, <0.35 = new). Watch for same-paper-different-title-version rows (e.g. "LOTT for Document Similarity" vs "…for Scalable Document Similarity" = same paper).
3. **Resolve new titles → arxiv IDs**: web search `"<exact title>" arxiv`. Confirm by scraping the abs page (title must match). Ambiguous generic titles ("Delivery Note", "Reinforcement learning") that don't resolve → **don't guess**: list them in the commit/report as 待确认 and skip.
4. **HEAD-check sizes** (`arxiv.org/pdf/<id>` Content-Length) → write jobs file `<aid> <slug>` per line.
5. **Download**: `python3 skills/paper-extraction/chunk_download.py jobs.txt` (takes a jobs file or inline `aid slug` pairs — don't edit the script). Poll every 1-2 min.
6. **Verify**: `verify_pdfs.py` → any 0-page truncated file goes back through chunk_download.
7. **Index**: append rows to `papers_effective.md` (scrape abs page for abstract — reliable; don't parse from PDF), flip `⏳`→`✓` after download, update header counts.
8. **Extract**: `extract_phase1.py` (regenerates MOC/papers.json/related-links for the whole graph — cheap, idempotent).
9. **MiniMax**: caption new architecture figures (caption keywords: overview/architecture/framework/design), 4-5 parallel `understand_image` calls per message → append `minimax_captions.json` → re-run Phase 1.
10. **Commit + push** (pull --rebase first; strip token from push URL after).

## Pitfalls & efficiency (bake these in — they cost real time)

**Always run `verify_pdfs.py` first** — 0-page `%PDF`-header files are *truncated downloads*, not "missing" or "HTML error". Don't waste cycles re-running Phase 1 on truncated PDFs; download-fix first, then extract once.

**Download strategy — don't use parallel `curl` for arxiv**. 6-concurrent looked fast but rate-limited → ~13/50 came back truncated (%PDF header, 0 pages) → re-download cycle cost more than it saved. **Fast path = `chunk_download.py` for everything** (sequential, HTTP Range, 8 retries/chunk). It's not slower in practice because it avoids rework. Only fall back to plain `curl` for tiny (<500KB) PDFs.

**arxiv large files (>3MB) on flaky networks**: connections get cut at ~1MB and even Range requests for later bytes can fail repeatedly. `chunk_download.py` (**256KB chunks + 15 retries + 90s timeout** — small chunks dodge the per-connection ceiling) is the only reliable server-side path; if even that stalls, the file exceeds this environment's per-connection ceiling — mark `✗ 网络` and have the user drop the PDF in `papers/` manually (browser session works).

**arxiv API (`export.arxiv.org/api/query`) returns empty XML** — don't use it. Scrape title from `https://arxiv.org/abs/<id>` HTML `<title>` tag instead.

**Don't capture binary PDFs in bash `$(curl ...)`** — null bytes get stripped, corrupting the file. Use `curl -o file` or Python `urllib` (binary-safe) / Range requests writing to file in append mode.

**Two-column PDFs scramble `get_text`** → abstract regex may miss. Robust: try `Abstract|ABSTRACT` → stop at `1 Introduction`/`Keywords:`/`CCS Concepts`; if miss, fall back to first 380 chars of body text. Phase 1 uses the index's abstract field, so get it right there or leave a placeholder.

**Figure-page ≠ architecture figure**. "Figure 2 page" can be a results bar-chart, not the method diagram. Pick architecture figures by **caption keywords** (overview/architecture/framework/design/method/system/scan), not by figure number.

**Featured-figure dedupe by PNG path** — the same PNG hosts multiple figure numbers (Fig.2 + Fig.4 on one page). Dedupe featured list by `img` or you'll list the same image N times.

**Duplicate index rows for one paper** (e.g. GEPA appears twice) → one PDF, two rows. Canonicalize to one slug, point both rows at it.

**`git push` non-fast-forward** when the repo was pushed from elsewhere → always `git pull --rebase <url> main` before push. Token in push URL: set, push, then strip token (`git remote set-url --push origin <clean-url>`).

**OpenReview**: `ChallengeRequiredError` on both web `/pdf` and API; headless chromium (even with stealth) stuck on "Verifying your browser". Server-side can't pass — go manual (browser download → drop PDF in `papers/`).

**ACM DL**: `403` = subscription paywall, no bypass without institutional auth — record link, mark `✗ ACM 订阅墙`.

**TOML dotted keys** (`glm-5.2`): MUST quote `"glm-5.2"` or TOML parses nested table → custom value silently drops. (Applies to pricing config, not this skill directly, but a recurring trap.)

**Efficiency levers**:
- `verify_pdfs.py` pre-check (seconds) → fix downloads → extract once. Avoids "extract → find broken → re-download → re-extract" loops.
- MiniMax calls: batch 3-5 `understand_image` tool calls per message (parallel), not one-at-a-time.
- Phase 1 is idempotent + skips existing PNGs (`if not path.exists`) — safe to re-run; only changed papers re-render.
- Abstract: prefer arxiv abs-page scrape for new rows (reliable) over PDF parsing (two-column fragile).

## File-integrity helpers

- `verify_pdfs.py` — `python3 skills/paper-extraction/verify_pdfs.py`. Reports truncated (0-page), corrupt (open-error), missing, and orphan PDFs. Exit 1 if any bad → use in CI/gate.
- `chunk_download.py` — `python3 skills/paper-extraction/chunk_download.py jobs.txt`. The only reliable arxiv downloader in flaky-network environments.
