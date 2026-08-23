#!/usr/bin/env python3
"""full_pipeline.py — 一条命令跑完「源列表 → 全要素萃取 → 图/表/公式解读 → 推送发布」全链路。

把原来「sync_from_source 入库 + agent 夜间收尾」两段式并成一条命令。
每步幂等：无新增时全链路 ~1-2 分钟（eprint/深读无目标即跳过）。

  python3 skills/paper-extraction/full_pipeline.py [--push] [--skip-deep-queue]

步骤：
  1. sync_from_source（源表 diff → arxiv 解析 → 下载体检 → 索引追加，不 push）
  2. extract_phase1（文本+图表+公式+MOC+manifest 全量重萃取）
  3. extract_visuals（图/表/公式区域裁剪成单图，幂等跳过已裁）
  4. m3_caption 批量解读新增图/表/公式裁剪（只补 minimax_captions.json 缺失项）
  5. eprint_formulas（LaTeX 源公式，失败冷却 3 天；无网时自动跳过）
  6. extract_phase1 再合并（把 4/5 的增量嵌进 MD）
  7. orchestrate_deep_reread（生成深读队列，新增论文的全要素深读交夜间 cron/agent）
  8. --push 时 token-safe commit + push（推完抹 push URL token）

铁律保持：图/表/公式理解全走 MiniMax-M3（m3_caption.py），公式以 formulas.json
LaTeX 为权威源，深读产出落 extraction/deep/ 独立文件（extract 重跑不丢）。
"""
import json, os, re, subprocess, sys, time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
SKILL = REPO / "skills" / "paper-extraction"
OUT = REPO / "extraction"


def run(script, *args, timeout=1800, bg_log=None):
    cmd = [sys.executable, str(SKILL / script), *args]
    print(f"\n>>> {' '.join(cmd)}", flush=True)
    if bg_log:
        with open(bg_log, "w") as lf:
            p = subprocess.Popen(cmd, cwd=REPO, stdout=lf, stderr=subprocess.STDOUT)
        print(f"    (background pid={p.pid}, log={bg_log})")
        return p
    r = subprocess.run(cmd, cwd=REPO, timeout=timeout,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    tail = "\n".join(r.stdout.splitlines()[-6:])
    print(tail, flush=True)
    return r.returncode


def uncaptioned_crops():
    cap_path = OUT / "minimax_captions.json"
    cap = json.loads(cap_path.read_text()) if cap_path.exists() else {}
    keys = set(cap) | {k.replace("extraction/", "") for k in cap}
    # fig crops inherit their page-level caption (same content) — only caption a
    # fig crop when its page PNG was never captioned (e.g. new paper whose pages
    # weren't M3-read yet). visuals.json maps crop -> page number.
    vis_path = OUT / "visuals.json"
    vis = json.loads(vis_path.read_text()) if vis_path.exists() else {}
    def page_captioned(slug, page):
        for k in (f"extraction/assets/{slug}-p{page:02d}.png",
                  f"assets/{slug}-p{page:02d}.png"):
            if k in keys:
                return True
        return False
    fig_has_page_cap = set()
    for slug, v in vis.items():
        for f in v.get("figures", []):
            if page_captioned(slug, f["page"]):
                fig_has_page_cap.add(f"{slug}-fig{f['num']:02d}.png")
    imgs = []
    for pat in ("assets/crops/*-tab*.png", "assets/crops/*-eq*.png",
                "assets/crops/*-fig*.png"):
        for p in sorted(OUT.glob(pat)):
            rel = str(p.relative_to(REPO))
            rel2 = str(p.relative_to(OUT))
            if rel in keys or rel2 in keys:
                continue
            if "-fig" in p.name and p.name in fig_has_page_cap:
                continue  # inherits page caption
            imgs.append(rel)
    return imgs


def batch_caption(imgs, concurrency=5):
    """Drive m3_caption.py --save over imgs with bounded concurrency."""
    if not imgs:
        print("    nothing to caption")
        return
    print(f"    captioning {len(imgs)} images (concurrency {concurrency})", flush=True)
    procs = []
    env = dict(os.environ)
    for img in imgs:
        while len([p for p in procs if p.poll() is None]) >= concurrency:
            time.sleep(0.5)
        procs.append(subprocess.Popen(
            [sys.executable, str(SKILL / "m3_caption.py"), "--save", img],
            cwd=REPO, env=env,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
        time.sleep(0.2)
    for p in procs:
        p.wait()
    print("    caption batch done", flush=True)


def token_safe_push(msg):
    tok_path = Path.home() / ".config" / "aico" / "gitcode_token"
    tok = os.environ.get("AICO_GITCODE_TOKEN") or \
          (tok_path.read_text().strip() if tok_path.exists() else "")
    def git(*a):
        return subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True)
    # pre-commit token leak check
    staged = git("diff", "--cached").stdout
    if tok and tok in staged:
        raise SystemExit("FATAL: token found in staged diff, abort push")
    git("add", "-A")
    n = len(git("diff", "--cached", "--name-only").stdout.splitlines())
    if n == 0:
        print("    nothing to commit")
        return
    git("commit", "-q", "-m", msg + "\n\nCo-Authored-By: Claude <noreply@anthropic.com>")
    if tok:
        git("remote", "set-url", "--push", "origin",
            f"https://gxliboy:{tok}@gitcode.com/gxliboy/AICO-knowledge.git")
    git("pull", "--rebase")
    r = git("push")
    print("    push:", (r.stdout + r.stderr).strip().splitlines()[-1] if (r.stdout or r.stderr) else "ok")
    # strip token from push url
    git("remote", "set-url", "--push", "origin",
        "https://gitcode.com/gxliboy/AICO-knowledge.git")
    cfg = (REPO / ".git" / "config").read_text()
    assert not tok or tok not in cfg, "token still in .git/config!"
    print("    token stripped, push url clean")


def main():
    push = "--push" in sys.argv
    t0 = time.time()
    print("=" * 60)
    print("FULL PIPELINE: source -> extract -> visuals -> captions -> formulas -> push")
    print("=" * 60)

    print("\n[1/8] sync_from_source (no push)")
    run("sync_from_source.py")

    print("\n[2/8] extract_phase1 (base extraction)")
    run("extract_phase1.py")

    print("\n[3/8] extract_visuals (figure/table/formula crops)")
    run("extract_visuals.py")

    print("\n[4/8] m3_caption for new crops")
    batch_caption(uncaptioned_crops())

    print("\n[5/8] eprint_formulas (latex source; background-safe)")
    run("eprint_formulas.py", timeout=600)

    print("\n[6/8] extract_phase1 (merge captions + formulas)")
    run("extract_phase1.py")

    print("\n[7/8] orchestrate_deep_reread (queue for night cron)")
    if (SKILL / "orchestrate_deep_reread.py").exists():
        run("orchestrate_deep_reread.py", timeout=300)
    else:
        print("    (orchestrate_deep_reread.py not present, skip)")

    if push:
        print("\n[8/8] token-safe commit + push")
        token_safe_push("pipeline: full source->extract->visuals->captions->formulas auto-sync")
    else:
        print("\n[8/8] --push not set, skip push")

    print(f"\nFULL PIPELINE DONE in {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
