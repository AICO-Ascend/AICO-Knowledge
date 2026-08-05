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
│   └── chunk_download.py
└── extraction/                 # generated knowledge base
    ├── <slug>.md               # per-paper structured (Obsidian-flavored)
    ├── fulltext/<slug>.txt     # full text for grep
    ├── assets/<slug>-pNN.png   # figure-page renders (150 DPI)
    ├── figures_index.md        # ⭐ figure library: featured + topic + per-paper
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
- Per-paper MD: frontmatter (title/authors/date/arxiv/slug/tags) + abstract + figures (embed `![[assets/...]]` + `[!quote] caption`) + fulltext pointer.
- Master `figures_index.md`: ⭐featured (deduped) + topic-tagged catalog + per-paper listing.
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
| 404 / HTML page | wrong arxiv ID (hallucinated) | search arxiv API `http://export.arxiv.org/api/query?search_query=ti:"..."` for correct ID |
| HTTP 200 + small + pages=0 | parallel batch got rate-limited → truncated | retry **sequential** with browser UA + Referer, 1 req at a time |
| Large PDF (>3MB), keeps truncating ~1MB | flaky network caps connection | `chunk_download.py` — HTTP Range in 1MB chunks, 8 retries/chunk, resume |
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

- `extract_phase1.py` — Phase 1 + merges MiniMax captions. Args: none (reads `papers_effective.md`, writes `extraction/`). Path-relative.
- `chunk_download.py` — arxiv large-file resume. Edit `JOBS=[("arxiv_id","slug"),...]` list, run. Path-relative.
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
