#!/usr/bin/env python3
"""Chunked range-download for arxiv PDFs that get truncated by network.
Downloads in small byte-ranges (handles flaky connections + binary safely)."""
import urllib.request, os, time, sys, fitz

UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
import os
from pathlib import Path
REPO=Path(__file__).resolve().parents[2]

def total_size(url):
    req=urllib.request.Request(url, headers={"User-Agent":UA}, method="HEAD")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return int(r.headers.get("Content-Length",0) or 0)
    except Exception:
        req=urllib.request.Request(url, headers={"User-Agent":UA})
        with urllib.request.urlopen(req, timeout=30) as r:
            return int(r.headers.get("Content-Length",0) or 0)

def chunk_dl(url, dest, chunk=262144, max_retries=15):
    total=total_size(url)
    if not total:
        print("  no content-length"); return False, 0
    with open(dest,"wb") as f:
        pos=0
        while pos<total:
            end=min(pos+chunk-1, total-1)
            done=False
            for attempt in range(max_retries):
                req=urllib.request.Request(url, headers={"User-Agent":UA,"Range":f"bytes={pos}-{end}"})
                try:
                    with urllib.request.urlopen(req, timeout=90) as r:
                        data=r.read()
                        if data:
                            f.write(data); f.flush()
                            pos+=len(data); done=True; break
                except Exception as e:
                    if attempt==max_retries-1:
                        print(f"  chunk {pos}-{end} failed: {e}"); return False, pos
                    time.sleep(3)
            if not done:
                print(f"  stuck at {pos}"); return False, pos
    return True, pos

# Jobs: pass a file path as argv[1] (lines: "<arxiv_id> <slug>", # comments ok),
# or inline pairs: chunk_download.py 2607.24653 kimi-k3-open-frontier-intelligence ...
# (kept generic on purpose — never hardcode per-batch job lists here again)
def load_jobs():
    args = sys.argv[1:]
    if len(args) == 1 and os.path.isfile(args[0]):
        jobs = []
        for ln in open(args[0], encoding="utf-8"):
            ln = ln.strip()
            if not ln or ln.startswith("#"):
                continue
            aid, slug = ln.split(None, 1)
            jobs.append((aid.strip(), slug.strip()))
        return jobs
    if args and len(args) % 2 == 0:
        return [(args[i], args[i + 1]) for i in range(0, len(args), 2)]
    return []

JOBS = load_jobs()

if __name__=="__main__":
    os.chdir(REPO)
    fixed=0
    for aid,slug in JOBS:
        dest=f"papers/{slug}.pdf"
        url=f"https://arxiv.org/pdf/{aid}"
        # skip if already valid
        try:
            if fitz.open(dest).page_count>1:
                print(f"{slug[:45]:47} already OK"); fixed+=1; continue
        except: pass
        ok,sz=chunk_dl(url,dest)
        try: pc=fitz.open(dest).page_count
        except: pc=0
        print(f"{slug[:45]:47} ok={ok} size={sz} pages={pc}")
        if pc>1: fixed+=1
    print(f"=== fixed {fixed}/{len(JOBS)} ===")
