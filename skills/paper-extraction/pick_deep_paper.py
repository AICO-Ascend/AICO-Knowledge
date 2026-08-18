#!/usr/bin/env python3
"""pick_deep_paper.py — pick the paper with the largest deep-learning gap for
the next night-learning batch.

Outputs ONE slug + a todo checklist (uncaptioned figures / no tech-point section
/ no tables / heuristic formulas). DEEP_LEARNING_PROTOCOL.md Step 1.

Depth-first: 1 paper done thoroughly beats 30 figures skimmed. This picks the
paper where deep reading adds the most.

Usage:
  python3 skills/paper-extraction/pick_deep_paper.py            # pick 1 (default)
  python3 skills/paper-extraction/pick_deep_paper.py --list     # show gap ranking
"""
import json, re, sys, glob, os
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
EXTRA = REPO / "extraction"
CAPTIONS = json.load(open(EXTRA / "minimax_captions.json"))
CAPNAMES = {k.split("/")[-1] for k in CAPTIONS}
FORMULAS = json.load(open(EXTRA / "formulas.json")) if (EXTRA / "formulas.json").exists() else {}

TECHPOINT_RE = re.compile(r"技术点|关键.*要点|核心创新|## \d|> \[!note\]")
TABLE_RE = re.compile(r"^\s*\|.*\|.*\n\s*\|[-:\s|]+\|", re.M)


def paper_gap(slug):
    md = EXTRA / f"{slug}.md"
    if not md.exists():
        return None
    txt = md.read_text(encoding="utf-8", errors="ignore")
    # uncaptioned figures in this paper
    pngs = set(re.findall(r"assets/([^\]]+\.png)", txt))
    uncap = {p for p in pngs if p not in CAPNAMES}
    has_tech = bool(TECHPOINT_RE.search(txt))
    has_table = bool(TABLE_RE.search(txt)) or "## 表格" in txt
    has_heur = slug in FORMULAS and not any(
        (e.get("env") or "").lower() in
        ("equation", "align", "gather", "multline", "eqnarray", "displaymath", "$$", "\\[")
        for e in FORMULAS[slug] if isinstance(e, dict))
    return {
        "slug": slug,
        "uncap_figs": sorted(uncap),
        "n_uncap": len(uncap),
        "has_tech": has_tech,
        "has_table": has_table,
        "heuristic_formulas": has_heur,
        # gap score: missing tech-point is the biggest lever; then uncaptioned figs;
        # then tables; then heuristic formulas
        "score": (0 if has_tech else 100) + len(uncap) * 2 + (0 if has_table else 30) + (15 if has_heur else 0),
    }


def main():
    args = sys.argv[1:]
    do_list = "--list" in args
    slugs = [p.stem for p in EXTRA.glob("*.md")
             if p.stem not in ("MOC", "README", "figures_index", "sync_report", "backfill_log")]
    gaps = [g for g in (paper_gap(s) for s in slugs) if g]
    gaps.sort(key=lambda g: -g["score"])

    if do_list:
        print(f"== deep-learning gap ranking ({len(gaps)} papers) ==")
        for g in gaps[:25]:
            flags = []
            if not g["has_tech"]: flags.append("无技术点")
            if not g["has_table"]: flags.append("无表格")
            if g["heuristic_formulas"]: flags.append("启发式公式")
            print(f"  {g['score']:4}  未深读图{g['n_uncap']:2}  {', '.join(flags):<20}  {g['slug'][:55]}")
        return

    pick = gaps[0]
    print(f"== 本批深读论文: {pick['slug']} (gap score {pick['score']}) ==\n")
    print(f"待办清单：")
    print(f"  [文本] 技术点结构化: {'✅已有(补强)' if pick['has_tech'] else '❌缺(本批重点)'}")
    print(f"  [表格] 表格萃取: {'✅已有' if pick['has_table'] else '❌缺(本批做)'}")
    print(f"  [公式] {'启发式→e-print补' if pick['heuristic_formulas'] else '已有LaTeX/无公式'}")
    print(f"  [图] 未深读图 {pick['n_uncap']} 张:")
    for p in pick["uncap_figs"]:
        print(f"    extraction/assets/{p}")
    print(f"\n按 DEEP_LEARNING_PROTOCOL.md Step 2 执行全要素深读。")


if __name__ == "__main__":
    main()
