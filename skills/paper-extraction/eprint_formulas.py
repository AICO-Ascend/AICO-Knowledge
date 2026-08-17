#!/usr/bin/env python3
"""Extract display-math formulas from arxiv e-print (LaTeX source) for each paper.

PDF text extraction shreds multi-line equations into fragments — useless for
citation. The arxiv e-print tarball carries the LaTeX source: equations come out
clean and paste-ready ($$...$$ in Obsidian).

Output: extraction/formulas.json  {slug: [{"env": "equation", "latex": "..."}]}
Cache:  .cache/eprints/<arxiv_id>.tar(.gz)  (gitignored)

Usage: python3 skills/paper-extraction/eprint_formulas.py [--limit N] [--only slug1,slug2]
"""
import urllib.request, tarfile, gzip, re, os, sys, json, time, io
from pathlib import Path

SCRIPT = Path(__file__).resolve()
REPO = SCRIPT.parents[2]
OUT = REPO / "extraction"
CACHE = REPO / ".cache" / "eprints"
CACHE.mkdir(parents=True, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36"}
MAX_FORMULAS = 20
MAX_EPRINT = 40 * 1024 * 1024  # skip monsters

def index_slugs():
    """slug -> arxiv id from papers_effective.md (✓ rows only)."""
    m = {}
    for line in open(REPO / "papers_effective.md", encoding="utf-8"):
        parts = [p.strip() for p in line.split("|")]
        inner = parts[1:-1]
        if not inner or not re.match(r"\d+$", inner[0] or ""):
            continue
        loc = inner[5]
        mm = re.match(r"✓ papers/(.+)\.pdf", loc)
        am = re.search(r"arxiv\.org/abs/([0-9.]+)", inner[3])
        if mm and am:
            m[mm.group(1)] = am.group(1)
    return m

def fetch_eprint(aid):
    """Download e-print tarball to cache (retry; hard total deadline per attempt —
    urlopen timeout is per-socket-op, a dribbling connection can hang forever)."""
    dest = CACHE / f"{aid}.bin"
    if dest.exists() and dest.stat().st_size > 1000:
        return dest
    url = f"https://arxiv.org/e-print/{aid}"
    for attempt in range(6):
        try:
            req = urllib.request.Request(url, headers=UA)
            deadline = time.time() + 180
            buf = bytearray()
            with urllib.request.urlopen(req, timeout=60) as r:
                while True:
                    remain = deadline - time.time()
                    if remain <= 0:
                        raise TimeoutError("total deadline exceeded")
                    chunk = r.read(262144)
                    if not chunk:
                        break
                    buf.extend(chunk)
                    if len(buf) > MAX_EPRINT:
                        print(f"  {aid}: eprint too big ({len(buf)/1e6:.0f}MB), skip")
                        return None
            dest.write_bytes(bytes(buf))
            return dest
        except Exception as e:
            if attempt == 5:
                print(f"  {aid}: download failed: {e}")
                return None
            time.sleep(3)

def read_tex_sources(path):
    """Yield concatenated .tex text from a tar/tar.gz/single-tex eprint."""
    raw = path.read_bytes()
    # try tar (gz or plain)
    for mode in ("r:gz", "r:", "r:bz2"):
        try:
            with tarfile.open(fileobj=io.BytesIO(raw), mode=mode) as tf:
                texs = [m for m in tf.getmembers()
                        if m.isfile() and m.name.endswith(".tex") and m.size < 3_000_000]
                texs.sort(key=lambda m: (("main" not in m.name.lower()), m.name))
                return "\n".join(tf.extractfile(m).read().decode("utf-8", "replace")
                                 for m in texs[:30])
        except tarfile.TarError:
            continue
    # single gzipped tex?
    try:
        return gzip.decompress(raw).decode("utf-8", "replace")
    except Exception:
        pass
    try:
        return raw.decode("utf-8", "replace")
    except Exception:
        return ""

ENVS = ["equation", "align", "alignat", "gather", "multline", "eqnarray", "displaymath"]

def extract_math(tex):
    """Pull display-math blocks, clean them, dedupe. Returns [{env, latex}]."""
    out, seen = [], set()
    pats = [r"\\begin\{(%s)\*?\}(.*?)\\end\{\1\*?\}" % e for e in ENVS]
    pats.append(r"\\\[(.*?)\\\]")
    for pat in pats:
        for mm in re.finditer(pat, tex, re.S):
            if len(mm.groups()) == 2:
                env, body = mm.group(1), mm.group(2)
            else:
                env, body = "display", mm.group(1)
            body = re.sub(r"%[^\n]*", "", body)          # strip comments
            body = re.sub(r"\\label\{[^}]*\}", "", body)  # strip labels
            body = re.sub(r"\s+", " ", body).strip()
            if not (10 <= len(body) <= 800):
                continue
            if not re.search(r"[=\\]", body):
                continue
            key = body[:80]
            if key in seen:
                continue
            seen.add(key)
            out.append({"env": env, "latex": body})
            if len(out) >= MAX_FORMULAS:
                return out
    return out

def main():
    limit = None
    only = None
    args = sys.argv[1:]
    if "--limit" in args:
        limit = int(args[args.index("--limit") + 1])
    if "--only" in args:
        only = set(args[args.index("--only") + 1].split(","))
    slugs = index_slugs()
    fj_path = OUT / "formulas.json"
    formulas = json.loads(fj_path.read_text(encoding="utf-8")) if fj_path.exists() else {}
    todo = [(s, a) for s, a in slugs.items()
            if (not only or s in only) and not (s in formulas and formulas[s])]
    if limit:
        todo = todo[:limit]
    print(f"todo: {len(todo)} papers")

    from concurrent.futures import ThreadPoolExecutor
    import threading
    lock = threading.Lock()

    def work(item):
        slug, aid = item
        ep = fetch_eprint(aid)
        if not ep:
            return slug, []
        tex = read_tex_sources(ep)
        if not tex.strip():
            print(f"  {slug[:45]:47} no tex source (pdf-only)")
            return slug, []
        fs = extract_math(tex)
        print(f"  {slug[:45]:47} formulas={len(fs)}")
        return slug, fs

    with ThreadPoolExecutor(max_workers=8) as ex:
        for slug, fs in ex.map(work, todo):
            with lock:
                formulas[slug] = fs
                fj_path.write_text(json.dumps(formulas, ensure_ascii=False, indent=1),
                                   encoding="utf-8")
    print(f"=== formulas.json: {sum(1 for v in formulas.values() if v)} papers with latex formulas ===")

if __name__ == "__main__":
    main()
