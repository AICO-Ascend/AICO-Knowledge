#!/usr/bin/env python3
"""Verify all PDFs in papers/ are valid (not truncated/corrupt) and match the index.
Reports: missing files, 0-page (truncated), open-errors (corrupt), size anomalies.
Run before AND after downloads to catch truncation early (avoids rework).

Portable: derives REPO from script location."""
import fitz, re, sys
from pathlib import Path
REPO=Path(__file__).resolve().parents[2]
PAPERS=REPO/"papers"
INDEX=REPO/"papers_effective.md"

def main():
    # indexed slugs
    indexed={}
    for line in open(INDEX,encoding="utf-8"):
        parts=[p.strip() for p in line.split("|")]; inner=parts[1:-1]
        if not inner or not re.match(r'\d+$',inner[0] or ''): continue
        m=re.match(r'✓ papers/(.+)\.pdf',inner[5])
        if m: indexed[m.group(1)]=inner[0]
    bad=[]; ok=0; missing=[]
    for slug,num in indexed.items():
        f=PAPERS/f"{slug}.pdf"
        if not f.exists():
            missing.append((num,slug)); continue
        try:
            pc=fitz.open(str(f)).page_count
            if pc==0:
                bad.append((num,slug,"0 pages (truncated)",f.stat().st_size))
            else:
                ok+=1
        except Exception as e:
            bad.append((num,slug,f"CORRUPT: {e}",f.stat().st_size if f.exists() else 0))
    print(f"indexed: {len(indexed)} | valid: {ok} | truncated/corrupt: {len(bad)} | missing: {len(missing)}")
    if missing:
        print("\n--- MISSING ---")
        for num,slug in missing: print(f"  #{num} {slug}")
    if bad:
        print("\n--- TRUNCATED/CORRUPT (re-download via chunk_download.py) ---")
        for num,slug,reason,sz in bad: print(f"  #{num} {slug[:55]} | {reason} | {sz}B")
    # also: PDFs in papers/ not indexed (orphans)
    allp={f.stem for f in PAPERS.glob("*.pdf")}
    orphans=allp-set(indexed)
    if orphans:
        print(f"\n--- ORPHAN PDFs (in papers/, not in index): {len(orphans)} ---")
        for o in sorted(orphans): print(f"  {o}")
    return 1 if (bad or missing) else 0

if __name__=="__main__":
    sys.exit(main())
