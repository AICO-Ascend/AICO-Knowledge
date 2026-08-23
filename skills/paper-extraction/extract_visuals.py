#!/usr/bin/env python3
"""extract_visuals.py — crop per-figure / per-table / per-formula images from PDFs.

Why: extract_phase1 renders whole pages (1275x1650) — a page may hold body text +
multiple figures. For report insertion we need clean single-element crops.

Strategy (pure geometry, no ML):
  figure: caption block ("Figure N[:.| ]...") anchors the element; the graphic
          cluster (drawings + images + short label blocks) sits directly ABOVE the
          caption. Crop = union of that cluster, bounded by nearest body/caption
          above, x-range = union of cluster members (handles 2-column via caption x).
  table : caption ("Table N[:.]...") sits ABOVE the table; consume text blocks
          below until a body paragraph / next caption / heading.
  formula: only for papers WITHOUT latex source (formulas.json miss) — heuristic
          display-math blocks (has '=', math indicator, short) cropped as images
          so the formula is at least on record as a picture.

Output: extraction/assets/crops/<slug>-figNN.png | -tabNN.png | -eqNN.png
        extraction/visuals.json  {slug: {figures:[...], tables:[...], formulas:[...]}}
Idempotent: existing crops are skipped (delete file to force re-crop).

Usage: python3 skills/paper-extraction/extract_visuals.py [--only slug1,slug2] [--dpi 200]
"""
import fitz, json, re, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
OUT = REPO / "extraction"
CROPS = OUT / "assets" / "crops"
PAPERS = REPO / "papers"

CAP_FIG = re.compile(r'^(Figure|Fig\.?)\s*(\d+)\s*[:.|]?\s*(.*)', re.S)
CAP_FIG_CN = re.compile(r'^图\s*(\d+)\s*[-‑–—]\s*(\d+)\s*[:：]?\s*(.*)', re.S)
CAP_TAB = re.compile(r'^(Table|TABLE)\s*(\d+)\s*[:.]?\s*(.*)', re.S)
CAP_TAB_CN = re.compile(r'^表\s*(\d+)\s*[-‑–—]\s*(\d+)\s*[:：]?\s*(.*)', re.S)

MATH_CHARS = set("∑∏√≈≤≥∈∀αβγδθλμπσφωΣΠ·×⊗⊙→←↑↓ⁿ∇∂∞≠∝⊆∪∩")
MATH_WORDS = ("softmax", "argmax", "argmin", "Attention(", "exp(", "KL(", "∇", "loss")
BODY_MIN_CHARS = 220          # a text block longer than this is body text, not figure label
LABEL_MAX_CHARS = 120         # short blocks inside figure region count as labels
MAX_CROP_H = 700              # pt; a "figure" taller than this is almost full page -> skip crop
MIN_CROP_H = 40
MIN_CROP_W = 80


def paper_slugs():
    out = []
    for line in open(REPO / "papers_effective.md", encoding="utf-8"):
        parts = [p.strip() for p in line.split("|")]
        inner = parts[1:-1]
        if not inner or not re.match(r'\d+$', inner[0] or ''):
            continue
        m = re.match(r'✓ papers/(.+)\.pdf', inner[5])
        if m and m.group(1) not in out:
            out.append(m.group(1))
    return out


def block_text(b):
    return " ".join(s["text"] for l in b.get("lines", []) for s in l["spans"]).strip()


def match_caption(txt):
    """-> (kind, num, caption_tail) or None. kind in {fig, tab}."""
    m = CAP_FIG_CN.match(txt)
    if m:
        return "fig", int(m.group(1)) * 100 + int(m.group(2)), m.group(3)
    m = CAP_TAB_CN.match(txt)
    if m:
        return "tab", int(m.group(1)) * 100 + int(m.group(2)), m.group(3)
    m = CAP_FIG.match(txt)
    if m and len(m.group(3)) > 3:
        return "fig", int(m.group(2)), m.group(3)
    m = CAP_TAB.match(txt)
    if m and len(m.group(3)) > 3:
        return "tab", int(m.group(2)), m.group(3)
    return None


def line_mathy(txt):
    """line-level display-math heuristic (mirrors extract_phase1.extract_formulas)."""
    s = re.sub(r'\s+', ' ', txt).strip()
    if not (6 <= len(s) <= 180) or '=' not in s:
        return False
    if not (any(c in MATH_CHARS for c in s) or any(w in s for w in MATH_WORDS)):
        return False
    if len(s.split('=', 1)[0].split()) > 8:
        return False
    if re.search(r'http|arxiv|figure|table|section', s, re.I):
        return False
    # prose guard (2026-08-23): a display equation's tokens are mostly math, not
    # English words. "γ = (γij) that redistributes mass ..." is prose with inline
    # math — reject when >55% of tokens are plain English words.
    toks = s.split()
    if toks:
        english = sum(1 for tk in toks if re.fullmatch(r'[a-zA-Z]{3,}', tk))
        if english / len(toks) > 0.55:
            return False
    return True


def formula_regions(page, max_keep=12):
    """Detect display-formula regions at LINE level, expand to adjacent short lines
    (multi-line equations: piecewise cases, subscript rows) + overlapping drawings.

    Guards against prose-capture (2026-08-23 fix): growth stays in the seed's
    column, merged region capped at 150pt tall / 30 words — a display equation is
    short; anything taller/longer is body text with inline math, not a formula."""
    col_mid = page.rect.width / 2
    lines = []
    for b in page.get_text("dict")["blocks"]:
        if b["type"] != 0:
            continue
        for l in b.get("lines", []):
            txt = "".join(s["text"] for s in l["spans"]).strip()
            if txt:
                lines.append((fitz.Rect(l["bbox"]), txt))
    # display equations are centered/short and never start with a prose
    # connective ("and νj, and that Σ..." is a body line with inline math)
    PROSE_START = ("and", "the", "that", "this", "these", "where", "with",
                   "which", "for", "from", "into", "over", "under", "when",
                   "while", "if", "in", "on", "at", "by", "to", "we", "it")
    def is_seed(r, t):
        if not line_mathy(t):
            return False
        first = t.split()[0].lower().strip(",;:()") if t.split() else ""
        if first in PROSE_START:
            return False
        col_w = col_mid if (r.x0 + r.x1) / 2 < col_mid else page.rect.width - col_mid
        col_w = col_w - 2 * 50  # minus typical margins
        strong_math = sum(1 for c in t if c in MATH_CHARS) >= 2
        return strong_math or r.width < 0.72 * col_w
    seeds = [(r, t) for r, t in lines if is_seed(r, t)]
    if not seeds:
        return []
    drawings = [dr["rect"] for dr in page.get_drawings()
                if dr["rect"].width > 4 and dr["rect"].height > 4]
    out, used = [], []
    for r, t in seeds:
        if len(out) >= max_keep:
            break
        if any(abs(r.y0 - u) < 30 for u in used):
            continue
        seed_col = 0 if (r.x0 + r.x1) / 2 < col_mid else 1
        # grow: merge nearby short non-body lines in the SAME column only
        region = fitz.Rect(r)
        words = len(t.split())
        for r2, t2 in lines:
            if r2 is r:
                continue
            if abs((r2.y0 + r2.y1) / 2 - (r.y0 + r.y1) / 2) > 42:
                continue
            r2_col = 0 if (r2.x0 + r2.x1) / 2 < col_mid else 1
            if r2_col != seed_col:
                continue
            if r2.x0 > r.x1 + 60 or r2.x1 < r.x0 - 60:
                continue
            if len(t2) <= 60 and not re.search(r'^(Figure|Table)\s+\d', t2):  # display-math lines are short; prose lines fill the column
                # merged line must itself be mathy or a tiny lead-in ("subject to:")
                lead_in = len(t2) <= 30
                if not (any(c in MATH_CHARS for c in t2) or '=' in t2 or lead_in):
                    continue
                cand = region | r2
                if cand.height <= 150 and words + len(t2.split()) <= 30:
                    region = cand
                    words += len(t2.split())
        for dr in drawings:
            if dr.y1 >= region.y0 - 6 and dr.y0 <= region.y1 + 6 \
               and dr.x1 >= region.x0 and dr.x0 <= region.x1:
                if (region | dr).height <= 150:
                    region |= dr
        used.append(r.y0)
        out.append((region, re.sub(r'\s+', ' ', t).strip()))
    return out


HEADING = re.compile(r'^\d+(\.\d+)+\.?\s')   # "2.2.2. Evaluation Results"


def crop_pix(page, rect, dpi):
    rect = rect & page.rect
    if rect.is_empty or rect.height < MIN_CROP_H or rect.width < MIN_CROP_W:
        return None
    if rect.height > MAX_CROP_H:
        return None
    mat = fitz.Matrix(dpi / 72, dpi / 72)
    return page.get_pixmap(matrix=mat, clip=rect)


def block_table_score(b):
    """table-likeness of a text block: multi-span lines (cells) or digit-dense."""
    lines = b.get("lines", [])
    if not lines:
        return 0
    multi = sum(1 for l in lines if len(l["spans"]) >= 2)
    txt = block_text(b)
    digits = sum(c.isdigit() for c in txt)
    return multi + (1 if len(txt) and digits / len(txt) > 0.15 else 0)


def is_heading_or_caption(t):
    return bool(HEADING.match(t)) or match_caption(t) is not None


def collect_table_region(blocks, cap_rect, x0, x1, direction):
    """Consume table blocks from caption in given direction (+1 below, -1 above)."""
    region = []
    for b in blocks:
        if b["type"] != 0:
            continue
        br = fitz.Rect(b["bbox"])
        if direction == +1:
            if br.y0 < cap_rect.y1 - 2 or br.y0 > cap_rect.y1 + 420:
                continue
        else:
            if br.y1 > cap_rect.y0 + 2 or br.y1 < cap_rect.y0 - 420:
                continue
        if br.x1 < x0 or br.x0 > x1:
            continue
        t = block_text(b)
        if not t:
            continue
        if is_heading_or_caption(t):
            break
        if len(t) > BODY_MIN_CHARS and block_table_score(b) < 2:
            break  # real body paragraph
        region.append((br, block_table_score(b), b))
    region.sort(key=lambda x: x[0].y0, reverse=(direction == -1))
    # walk from caption outward; stop when 2 consecutive non-table blocks
    picked, streak = [], 0
    for br, sc, b in region:
        if sc >= 1:
            picked.append(br); streak = 0
        else:
            streak += 1
            if streak >= 2:
                break
    return picked



def process_paper(slug, dpi, latex_slugs):
    pdf = PAPERS / f"{slug}.pdf"
    if not pdf.exists():
        return None
    doc = fitz.open(str(pdf))
    res = {"figures": [], "tables": [], "formulas": []}
    seen_fig, seen_tab, seen_eq = set(), set(), set()
    for pno in range(doc.page_count):
        page = doc[pno]
        d = page.get_text("dict")
        blocks = d["blocks"]
        # caption blocks with geometry
        caps = []
        for b in blocks:
            if b["type"] != 0:
                continue
            mc = match_caption(block_text(b))
            if mc:
                caps.append((mc[0], mc[1], mc[2], fitz.Rect(b["bbox"])))
        if not caps and slug in latex_slugs:
            continue
        # collect graphic + label elements for figure region union
        gfx = []
        for b in blocks:
            r = fitz.Rect(b["bbox"])
            if b["type"] == 1:  # embedded image
                gfx.append(r)
            elif b["type"] == 0:
                t = block_text(b)
                if 0 < len(t) <= LABEL_MAX_CHARS:
                    gfx.append(r)
        for dr in page.get_drawings():
            r = dr["rect"]
            if r.width > 2 and r.height > 2:
                gfx.append(r)
        # caption rects act as separators (another caption bounds this one's region)
        cap_rects = [c[3] for c in caps]
        for kind, num, tail, r in caps:
            if kind == "fig":
                if num in seen_fig:
                    continue
                seen_fig.add(num)
                # cluster: gfx above caption, overlapping caption x-range loosely
                x0, x1 = r.x0 - 30, r.x1 + 30
                above = [g for g in gfx
                         if g.y1 <= r.y0 + 4 and g.y0 > r.y0 - 500
                         and g.x1 > x0 and g.x0 < x1]
                other_caps_above = [c for c in cap_rects if c.y1 <= r.y0 + 1]
                floor = max([c.y1 for c in other_caps_above], default=50)
                # body text above also bounds the figure top
                body_above = [fitz.Rect(b["bbox"]).y1 for b in blocks
                              if b["type"] == 0
                              and len(block_text(b)) > BODY_MIN_CHARS
                              and fitz.Rect(b["bbox"]).y1 <= r.y0 - 30]
                floor = max(floor, max(body_above, default=50))
                above = [g for g in above if g.y1 > floor]
                if not above:
                    continue
                u = above[0]
                for g in above[1:]:
                    u |= g
                u.y1 = r.y0 - 2
                u.x0 = max(0, u.x0 - 4); u.x1 = min(page.rect.x1, u.x1 + 4)
                u.y0 = max(0, u.y0 - 4)
                out = CROPS / f"{slug}-fig{num:02d}.png"
                item = {"num": num, "page": pno + 1,
                        "caption": re.sub(r'\s+', ' ', tail).strip()[:300],
                        "path": f"assets/crops/{out.name}"}
                if out.exists():
                    res["figures"].append(item); continue
                pix = crop_pix(page, u, dpi)
                if pix:
                    pix.save(str(out))
                    res["figures"].append(item)
            else:  # table: caption above (default) or below — try below, fall back above
                if num in seen_tab:
                    continue
                x0, x1 = r.x0 - 20, r.x1 + 20
                below = collect_table_region(blocks, r, x0, x1, +1)
                region, cap_at_top = below, True
                if not below:
                    above = collect_table_region(blocks, r, x0, x1, -1)
                    if above:
                        region, cap_at_top = above, False
                if not region:
                    continue
                seen_tab.add(num)
                u = fitz.Rect(r.x0, r.y0, r.x1, r.y1)  # include caption line
                for g in region:
                    u |= g
                u.x0 = max(0, u.x0 - 4); u.x1 = min(page.rect.x1, u.x1 + 4)
                u.y0 = max(0, u.y0 - 3); u.y1 = min(page.rect.y1, u.y1 + 3)
                out = CROPS / f"{slug}-tab{num:02d}.png"
                item = {"num": num, "page": pno + 1,
                        "caption": re.sub(r'\s+', ' ', tail).strip()[:300],
                        "path": f"assets/crops/{out.name}"}
                if out.exists():
                    res["tables"].append(item); continue
                pix = crop_pix(page, u, dpi)
                if pix:
                    pix.save(str(out))
                    res["tables"].append(item)
        # formula-as-image only for papers without latex source (line-level detection)
        if slug not in latex_slugs:
            for region, txt in formula_regions(page):
                key = txt[:60]
                if key in seen_eq:
                    continue
                seen_eq.add(key)
                region.x0 = max(0, region.x0 - 8); region.x1 = min(page.rect.x1, region.x1 + 8)
                region.y0 = max(0, region.y0 - 5); region.y1 = min(page.rect.y1, region.y1 + 5)
                out = CROPS / f"{slug}-eq{len(res['formulas']) + 1:02d}.png"
                item = {"page": pno + 1, "text": txt[:180],
                        "path": f"assets/crops/{out.name}"}
                if out.exists():
                    res["formulas"].append(item); continue
                pix = crop_pix(page, region, dpi)
                if pix:
                    pix.save(str(out))
                    res["formulas"].append(item)
    doc.close()
    res["figures"].sort(key=lambda x: x["num"])
    res["tables"].sort(key=lambda x: x["num"])
    return res


def main():
    args = sys.argv[1:]
    only = None
    dpi = 200
    if "--only" in args:
        only = set(args[args.index("--only") + 1].split(","))
    if "--dpi" in args:
        dpi = int(args[args.index("--dpi") + 1])
    CROPS.mkdir(parents=True, exist_ok=True)
    fj = OUT / "formulas.json"
    latex = json.loads(fj.read_text()) if fj.exists() else {}
    latex_slugs = {k for k, v in latex.items() if v}
    vis_path = OUT / "visuals.json"
    vis = json.loads(vis_path.read_text()) if vis_path.exists() else {}
    slugs = paper_slugs()
    if only:
        slugs = [s for s in slugs if s in only]
    print(f"papers: {len(slugs)} | latex-covered: {len(latex_slugs)} (formula-img only for the rest)")
    nf = nt = ne = 0
    for i, slug in enumerate(slugs, 1):
        try:
            r = process_paper(slug, dpi, latex_slugs)
            if r is None:
                continue
            vis[slug] = r
            nf += len(r["figures"]); nt += len(r["tables"]); ne += len(r["formulas"])
            print(f"  [{i:2}] {slug[:52]:52} fig={len(r['figures']):2} tab={len(r['tables']):2} eq={len(r['formulas']):2}")
        except Exception as e:
            print(f"  [ERR] {slug}: {e}")
    vis_path.write_text(json.dumps(vis, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nDONE. crops: fig={nf} tab={nt} eq={ne} -> {vis_path}")


if __name__ == "__main__":
    main()
