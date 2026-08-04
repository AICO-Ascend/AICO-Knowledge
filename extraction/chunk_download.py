#!/usr/bin/env python3
"""Chunked range-download for arxiv PDFs that get truncated by network.
Downloads in small byte-ranges (handles flaky connections + binary safely)."""
import urllib.request, os, time, sys, fitz

UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
REPO="/mnt/project/g00952465/AICO-knowledge"

def total_size(url):
    req=urllib.request.Request(url, headers={"User-Agent":UA}, method="HEAD")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return int(r.headers.get("Content-Length",0) or 0)
    except Exception:
        req=urllib.request.Request(url, headers={"User-Agent":UA})
        with urllib.request.urlopen(req, timeout=30) as r:
            return int(r.headers.get("Content-Length",0) or 0)

def chunk_dl(url, dest, chunk=1048576, max_retries=8):
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
                    with urllib.request.urlopen(req, timeout=60) as r:
                        data=r.read()
                        if data:
                            f.write(data); f.flush()
                            pos+=len(data); done=True; break
                except Exception as e:
                    if attempt==max_retries-1:
                        print(f"  chunk {pos}-{end} failed: {e}"); return False, pos
                    time.sleep(2)
            if not done:
                print(f"  stuck at {pos}"); return False, pos
    return True, pos

JOBS=[
("2409.19606","hyper-connections"),
("2402.15627","megascale-scaling-large-language-model-training-to-more-than-10000-gpus"),
("2502.13923","qwen2-5-vl-technical-report"),
("2412.19437","deepseek-v3-technical-report"),
("1910.02054","zero-memory-optimizations-toward-training-trillion-parameter-models"),
("1909.08053","megatron-lm-training-multi-billion-parameter-language-models-using-model-parallelism"),
("2409.19256","hybridflow-a-flexible-and-efficient-rlhf-framework"),
("2512.24873","let-it-flow-agentic-crafting-on-rock-and-roll"),
("2407.20018","efficient-training-of-large-language-models-on-distributed-infrastructures-a-survey"),
]

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
