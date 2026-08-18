#!/usr/bin/env python3
"""sync_from_source.py — one-command autonomous KB sync from the moonlight source export.

THE entry point. When archive/paper_source_moonlight.md is updated, run:

    python3 skills/paper-extraction/sync_from_source.py            # full sync, no push
    python3 skills/paper-extraction/sync_from_source.py --push     # sync + commit + push

Pipeline (idempotent — safe to re-run):
  1. parse moonlight table  -> [(title, date)]
  2. diff vs papers_effective.md (token Jaccard; >=0.6 same paper)
  3. resolve new titles -> arxiv IDs (arxiv title-search scrape; >=0.8 similarity auto-accept)
  4. HEAD size + chunk_download each new PDF (256KB chunks, retries)
  5. verify page_count>1 (retry failures once)
  6. scrape abs page abstract -> append rows to papers_effective.md + papers_download_list.txt
  7. run extract_phase1.py (figures/related/MOC/papers.json) + eprint_formulas.py
  8. write extraction/sync_report.md (added / 待确认 / failed — agent reads this)
  9. --push: git add+commit+pull--rebase+push, token from env AICO_GITCODE_TOKEN
     or ~/.config/aico/gitcode_token (NEVER written into the repo)

Not scripted (agent steps, see SKILL.md): confirming 待确认 entries, multimodal
deep-captions of new architecture figures (candidates listed in sync_report.md).
"""
import json, os, re, subprocess, sys, time, html, urllib.request, urllib.parse
from pathlib import Path

SCRIPT = Path(__file__).resolve()
SKILL_DIR = SCRIPT.parent
REPO = SKILL_DIR.parents[1]
SRC = REPO / "archive" / "paper_source_moonlight.md"
INDEX = REPO / "papers_effective.md"
DLLIST = REPO / "papers_download_list.txt"
REPORT = REPO / "extraction" / "sync_report.md"
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36"}

sys.path.insert(0, str(SKILL_DIR))
from chunk_download import chunk_dl  # noqa: E402
import fitz  # noqa: E402


# ---------- 1. parse ----------
# When archive/paper_source_moonlight.bib exists (clean Moonlight BibTeX export),
# it is preferred over the legacy .md web-capture: complete titles (no "待确认"
# truncations), and often arxiv eprint/url + abstract inline — which lets us
# short-circuit the fragile arxiv title-search scrape. _bib_extra carries those.
import importlib.util
_bib_extra = {}  # lowercased title -> {"arxiv": id|None, "abstract": ""}


def _load_bib():
    spec = importlib.util.spec_from_file_location(
        "parse_moonlight_bib", SKILL_DIR / "parse_moonlight_bib.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def parse_source():
    bib_path = REPO / "archive" / "paper_source_moonlight.bib"
    if bib_path.exists():
        mod = _load_bib()
        es = mod.entries(bib_path)
        out = []
        for e in es:
            t = e["title"].strip()
            _bib_extra[t.lower()] = {"arxiv": e["arxiv_id"], "abstract": e["abstract"]}
            out.append((t, e["date"] or ""))
        print(f"  [source] using clean BibTeX export ({len(out)} entries)")
        return out
    # legacy: web-capture markdown table (carries base64, column drift, truncated titles)
    txt = SRC.read_text(encoding="utf-8")
    rows = re.findall(r"\[([^\]]+)\]\(https://www\.themoonlight\.io/paper/[0-9a-f-]+\)[^\n]*?(\d{4}/\d{1,2}/\d{1,2})",
                      txt)
    seen, out = set(), []
    for t, d in rows:
        if t not in seen:
            seen.add(t)
            out.append((t.strip(), d))
    return out


# ---------- 2. diff ----------
def norm_tokens(t):
    return set(re.sub(r"[^a-z0-9一-鿿]+", " ", t.lower()).split())


def jaccard(a, b):
    u = a | b
    return len(a & b) / len(u) if u else 0.0


def load_existing():
    rows = []
    for line in INDEX.read_text(encoding="utf-8").splitlines():
        parts = [p.strip() for p in line.split("|")]
        inner = parts[1:-1]
        if not inner or not re.match(r"\d+$", inner[0] or ""):
            continue
        rows.append({"num": int(inner[0]), "title": inner[1], "abs": inner[3],
                     "tokens": norm_tokens(inner[1])})
    return rows


# ---------- 3. resolve ----------
def fetch(url, timeout=60):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def resolve_arxiv(title):
    """arxiv title search -> (arxiv_id, abs_title, score) or None."""
    q = urllib.parse.quote(f'"{title}"')
    url = f"https://arxiv.org/search/?query={q}&searchtype=title&abstracts=hide&size=10"
    try:
        h = fetch(url, timeout=45).decode("utf-8", "replace")
    except Exception:
        return None
    items = re.findall(r'<p class="title is-5 mathjax">\s*(.*?)\s*</p>', h, re.S)
    ids = re.findall(r'arxiv.org/abs/([0-9]{4}\.[0-9]{4,5})', h)
    want = norm_tokens(title)
    best, bs, bid = None, 0.0, None
    for t, i in zip(items, ids):
        t = html.unescape(re.sub(r"\s+", " ", t)).strip()
        sc = jaccard(want, norm_tokens(t))
        if sc > bs:
            best, bs, bid = t, sc, i
    if best and bs >= 0.8:
        return bid, best, bs
    return None


def abs_page_meta(aid):
    h = fetch(f"https://arxiv.org/abs/{aid}", timeout=60).decode("utf-8", "replace")
    clean = lambda s: html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s))).strip()
    title = re.search(r'<h1 class="title mathjax">\s*<span[^>]*>Title:</span>(.*?)</h1>', h, re.S)
    absr = re.search(r'<blockquote class="abstract mathjax">\s*<span[^>]*>Abstract:</span>(.*?)</blockquote>', h, re.S)
    date = re.search(r"\[Submitted on ([0-9]{1,2} \w+ [0-9]{4})", h)
    return {"title": clean(title.group(1)) if title else "",
            "abstract": clean(absr.group(1)) if absr else "",
            "date": date.group(1) if date else ""}


def iso_date(s):
    months = {m: i + 1 for i, m in enumerate(
        ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])}
    m = re.match(r"(\d{1,2}) (\w{3}) (\d{4})", s or "")
    return f"{m.group(3)}/{months.get(m.group(2), 1)}/{int(m.group(1))}" if m else ""


def slugify(title):
    s = title.lower().replace(",", "")
    s = re.sub(r"[^a-z0-9一-鿿]+", "-", s).strip("-")
    return re.sub(r"-+", "-", s)


# ---------- git ----------
def git(*a, check=True):
    return subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True, check=check)


def get_token():
    tok = os.environ.get("AICO_GITCODE_TOKEN", "").strip()
    if tok:
        return tok
    p = Path.home() / ".config" / "aico" / "gitcode_token"
    return p.read_text().strip() if p.exists() else ""


def do_push(msg):
    tok = get_token()
    if not tok:
        print("  [push] no token (set AICO_GITCODE_TOKEN or ~/.config/aico/gitcode_token) — commit only")
        return False
    git("add", "-A")
    if not git("status", "--porcelain").stdout.strip():
        print("  [push] nothing to commit")
        return True
    git("-c", "user.email=gxliboy@aico.local", "-c", "user.name=gxliboy",
        "commit", "-q", "-m", msg)
    url = f"https://gxliboy:{tok}@gitcode.com/gxliboy/AICO-knowledge.git"
    try:
        subprocess.run(["git", "pull", "--rebase", url, "main"], cwd=REPO,
                       capture_output=True, text=True)
        r = subprocess.run(["git", "push", "origin", "main"], cwd=REPO,
                           capture_output=True, text=True)
        print("  [push]", (r.stdout + r.stderr).strip().splitlines()[-1] if (r.stdout + r.stderr).strip() else r.returncode)
        return r.returncode == 0
    finally:
        git("remote", "set-url", "--push", "origin",
            "https://gitcode.com/gxliboy/AICO-knowledge.git", check=False)


# ---------- main ----------
def main():
    push = "--push" in sys.argv
    os.chdir(REPO)
    t0 = time.time()
    print("== 1. parse source ==")
    src = parse_source()
    print(f"  {len(src)} rows in moonlight export")

    print("== 2. diff vs index ==")
    existing = load_existing()
    ex_toks = [(e["tokens"], e) for e in existing]
    ex_ids = {re.search(r"([0-9]{4}\.[0-9]{4,5})", e["abs"]).group(1)
              for e in existing if re.search(r"([0-9]{4}\.[0-9]{4,5})", e["abs"])}
    candidates = []
    for title, date in src:
        best = max(((jaccard(norm_tokens(title), et), e) for et, e in ex_toks),
                   key=lambda x: x[0], default=(0, None))
        if best[0] >= 0.6:
            continue
        candidates.append({"title": title, "src_date": date, "near": best[1]["title"] if best[1] else ""})
    print(f"  {len(candidates)} new candidates")
    for c in candidates:
        print(f"   + {c['title'][:70]}")

    added, pending, failed = [], [], []
    if candidates:
        print("== 3. resolve arxiv IDs ==")
        for c in candidates:
            extra = _bib_extra.get(c["title"].lower())
            if extra and extra["arxiv"] and extra["arxiv"] not in ex_ids:
                # clean .bib source: arxiv ID + abstract known, skip fragile search
                c["arxiv"], c["abs_title"], c["score"] = extra["arxiv"], c["title"], 1.0
                print(f"   ✓ {c['title'][:55]:57} -> {c['arxiv']} (bib eprint)")
            elif extra and extra["arxiv"] and extra["arxiv"] in ex_ids:
                c["arxiv"] = None  # dup of existing
                print(f"   = {c['title'][:55]:57} (bib dup -> skipped)")
            else:
                r = resolve_arxiv(c["title"])
                if r and r[0] not in ex_ids:
                    c["arxiv"], c["abs_title"], c["score"] = r
                    print(f"   ✓ {c['title'][:55]:57} -> {r[0]} ({r[2]:.2f})")
                else:
                    c["arxiv"] = None
                    print(f"   ? {c['title'][:55]:57} (unresolved / dup -> 待确认)")

        print("== 4-5. download + verify ==")
        for c in candidates:
            if not c.get("arxiv"):
                pending.append(c)
                continue
            meta = abs_page_meta(c["arxiv"])
            c.update(meta)
            # prefer .bib abstract if abs-page scrape came back empty
            extra = _bib_extra.get(c["title"].lower())
            if (not c.get("abstract")) and extra and extra["abstract"]:
                c["abstract"] = extra["abstract"]
            c["slug"] = slugify(meta["title"] or c["title"])
            dest = REPO / "papers" / f"{c['slug']}.pdf"
            ok = False
            for attempt in range(2):
                ok, _sz = chunk_dl(f"https://arxiv.org/pdf/{c['arxiv']}", str(dest))
                try:
                    ok = ok and fitz.open(str(dest)).page_count > 1
                except Exception:
                    ok = False
                if ok:
                    break
                print(f"   retry {c['slug'][:45]}")
            if ok:
                c["pages"] = fitz.open(str(dest)).page_count
                added.append(c)
                ex_ids.add(c["arxiv"])
                print(f"   ✓ {c['slug'][:50]:52} pages={c['pages']}")
            else:
                failed.append(c)
                print(f"   ✗ {c['slug'][:50]:52} download failed")

        if added:
            print("== 6. update index ==")
            lines = INDEX.read_text(encoding="utf-8").rstrip("\n").split("\n")
            n = max(e["num"] for e in existing)
            dl = DLLIST.read_text(encoding="utf-8").rstrip("\n") + "\n"
            for c in added:
                n += 1
                ab = c["abstract"].replace("|", "\\|")
                lines.append(f"| {n} | {c['title']} | {iso_date(c['date'])} | "
                             f"https://arxiv.org/abs/{c['arxiv']} | https://arxiv.org/pdf/{c['arxiv']} | "
                             f"✓ papers/{c['slug']}.pdf | {ab} |")
                dl += f"{c['slug']} | https://arxiv.org/abs/{c['arxiv']} | https://arxiv.org/pdf/{c['arxiv']}\n"
            body = "\n".join(lines) + "\n"
            total = n
            body = re.sub(r"> 共 \d+ 篇 \| 已下载 \d+ 篇[^\n]*",
                          f"> 共 {total} 篇 | 已下载 {total} 篇 PDF（GEPA 在 #16/#19 重复，同一 PDF；ZCube/LOTT 人工补）| 无可下载源 0（全部已有原文）。",
                          body, count=1)
            INDEX.write_text(body, encoding="utf-8")
            DLLIST.write_text(dl, encoding="utf-8")
            print(f"   rows -> {total}")

    print("== 7. extract + formulas ==")
    subprocess.run([sys.executable, str(SKILL_DIR / "extract_phase1.py")], cwd=REPO)
    subprocess.run([sys.executable, str(SKILL_DIR / "eprint_formulas.py")], cwd=REPO)

    print("== 8. sync report ==")
    rep = ["# 🔄 源列表同步报告（sync_report.md）", "",
           f"> 生成：sync_from_source.py ｜ 源 {len(src)} 条 ｜ 已有 {len(existing)} 篇", ""]
    rep.append(f"## ✅ 新增入库（{len(added)}）")
    for c in added:
        rep.append(f"- **{c['title']}** — arXiv:{c['arxiv']}，{c['pages']} 页，`papers/{c['slug']}.pdf`")
    rep.append("")
    rep.append(f"## ⚠️ 待确认（{len(pending)}）— arxiv 未解析到，需人工/agent 判断")
    for c in pending:
        rep.append(f"- **{c['title']}**（源日期 {c['src_date']}，近似现有: {c['near'][:40]}）")
    rep.append("")
    rep.append(f"## ✗ 下载失败（{len(failed)}）")
    for c in failed:
        rep.append(f"- **{c['title']}** — arXiv:{c.get('arxiv','?')}，重跑本脚本会重试")
    rep.append("")
    rep.append("## 🖼️ 待深度解读的架构图候选（agent：Read PNG → 写 minimax_captions.json → 重跑 extract_phase1.py）")
    for c in added:
        rep.append(f"- {c['slug']}: 见 `extraction/{c['slug']}.md`，挑 caption 含 overview/architecture/framework/illustration 的图")
    REPORT.write_text("\n".join(rep) + "\n", encoding="utf-8")
    print(f"   -> {REPORT}")

    if push:
        print("== 9. commit + push ==")
        msg = (f"sync: source-list auto-sync (+{len(added)} papers, {len(pending)} pending)"
               if added or pending else "sync: source-list auto-sync (no changes)")
        do_push(msg)
    print(f"DONE in {time.time()-t0:.0f}s — added {len(added)}, pending {len(pending)}, failed {len(failed)}")


if __name__ == "__main__":
    main()
