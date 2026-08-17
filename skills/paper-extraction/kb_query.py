#!/usr/bin/env python3
"""kb_query.py — unified query entry for the paper knowledge base.

Other projects consume the KB through this one CLI instead of hand-grepping.
Repo-root-relative (works from anywhere via absolute path).

Usage:
  kb_query.py search  <kw> [kw...]   papers by title/abstract/fulltext (ranked)
  kb_query.py fig     <kw> [kw...]   figures by caption -> embed path + citation
  kb_query.py formula <kw> [kw...]   latex formulas by content
  kb_query.py topics                 topic -> papers map
  kb_query.py info    <slug>         one paper's full card (paths, figs, formulas)
  kb_query.py stats                  KB totals
Add --json for machine-readable output (RAG/agents). Default: human-readable.
"""
import json, re, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "extraction"


def load_manifest():
    return json.loads((OUT / "papers.json").read_text(encoding="utf-8"))


def load_formulas():
    p = OUT / "formulas.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def kws(args):
    return [a.lower() for a in args]


def match(text, ks):
    t = text.lower()
    return sum(t.count(k) for k in ks)


def cmd_search(ks, limit=10):
    res = []
    for p in load_manifest():
        score = 3 * match(p["title"], ks)
        full = OUT / "fulltext" / f"{p['slug']}.txt"
        body = ""
        if full.exists():
            body = full.read_text(encoding="utf-8", errors="replace")[:200000]
        score += match(body, ks)
        if score:
            res.append((score, p))
    res.sort(key=lambda x: -x[0])
    return [{"slug": p["slug"], "title": p["title"], "arxiv": p["arxiv"],
             "tags": p["tags"], "md": p["md"], "score": s} for s, p in res[:limit]]


def cmd_fig(ks, limit=20):
    res = []
    idx = (OUT / "figures_index.md").read_text(encoding="utf-8")
    # per-paper sections: "- ⭐Fig.N (p.X) ![[assets/<slug>-pNN.png]]" + caption line
    cur = None
    for ln in idx.splitlines():
        m = re.match(r"- (⭐ )?Fig\.(\d+) \(p\.(\d+)\) !\[\[(assets/[^]]+)\]\]", ln)
        if m:
            cur = {"fig": int(m.group(2)), "page": int(m.group(3)),
                   "img": m.group(4), "star": bool(m.group(1)), "caption": ""}
            continue
        if cur is not None and ln.startswith("  - "):
            cur["caption"] = ln[4:].strip()
            slug = re.sub(r"^assets/(.+)-p\d+\.png$", r"\1", cur["img"])
            score = match(cur["caption"], ks) + match(slug.replace("-", " "), ks)
            if score:
                cur["slug"] = slug
                cur["embed"] = f"![[{cur['img']}]]"
                cur["cite"] = f"[{slug}, Fig.{cur['fig']}, p.{cur['page']}]"
                cur["score"] = score
                res.append(cur)
            cur = None
    res.sort(key=lambda x: (-x["star"], -x["score"]))
    return res[:limit]


def cmd_formula(ks, limit=20):
    res = []
    for slug, fs in load_formulas().items():
        for f in fs:
            score = match(f["latex"], ks)
            if score:
                res.append({"slug": slug, "env": f["env"], "latex": f["latex"],
                            "score": score})
    res.sort(key=lambda x: -x["score"])
    return res[:limit]


def cmd_topics():
    out = {}
    for p in load_manifest():
        for t in p["tags"]:
            if p["slug"] not in out.setdefault(t, []):
                out[t].append(p["slug"])
    return out


def cmd_info(slug):
    for p in load_manifest():
        if p["slug"] == slug:
            caps = load_formulas().get(slug, [])
            d = dict(p)
            d["formulas"] = len(caps)
            d["pdf"] = f"papers/{slug}.pdf"
            return d
    return {"error": f"slug not found: {slug}"}


def cmd_stats():
    ms = load_manifest()
    fj = load_formulas()
    nfig = sum(p["figs"] for p in ms)
    return {"papers": len(ms), "figures": nfig,
            "papers_with_latex_formulas": sum(1 for v in fj.values() if v),
            "total_formulas": sum(len(v) for v in fj.values()),
            "topics": cmd_topics()}


def main():
    args = sys.argv[1:]
    as_json = "--json" in args
    args = [a for a in args if a != "--json"]
    if not args:
        print(__doc__)
        return
    cmd, rest = args[0], args[1:]
    if cmd == "search":
        r = cmd_search(kws(rest))
    elif cmd == "fig":
        r = cmd_fig(kws(rest))
    elif cmd == "formula":
        r = cmd_formula(kws(rest))
    elif cmd == "topics":
        r = cmd_topics()
    elif cmd == "info":
        r = cmd_info(rest[0]) if rest else {"error": "need slug"}
    elif cmd == "stats":
        r = cmd_stats()
    else:
        print(__doc__)
        return
    if as_json:
        print(json.dumps(r, ensure_ascii=False, indent=1))
        return
    # human-readable
    if cmd == "search":
        for x in r:
            print(f"[{x['score']:4d}] {x['title'][:60]}\n       {x['arxiv']}  tags={','.join(x['tags'])}  -> {x['md']}")
    elif cmd == "fig":
        for x in r:
            print(f"{'⭐' if x['star'] else ' '} {x['embed']}\n   {x['caption'][:90]}\n   引用: {x['cite']}  论文: [[{x['slug']}]]")
    elif cmd == "formula":
        for x in r:
            print(f"[[{x['slug']}]] ({x['env']})\n   $$\n   {x['latex'][:150]}\n   $$")
    elif cmd == "topics":
        for t, ps in sorted(r.items()):
            print(f"{t} ({len(ps)})")
            for s in ps:
                print(f"  - {s}")
    else:
        print(json.dumps(r, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
