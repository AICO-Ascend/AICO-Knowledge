#!/usr/bin/env python3
"""audit_crops.py — 全量裁剪图质量机审（M3 vision 逐张判决，结构化 JSON）。

背景（用户 2026-08-24 三轮反馈"怎么每次都不彻底"）：此前修复都是「信号驱动」
——只修被 caption 异常/用户点名命中的子集，漏网不可避免。本脚本对
assets/crops/ 全部裁剪做 M3 逐张结构化判决，机审全量、分类修复、不再漏网。

判决类别（issues 数组，可多个）：
  prose_only      内容是大段正文散文，不是图/表（假裁剪）
  truncated       元素不完整（表只有 caption+表头/数据行被切断/图被拦腰切断）
  prose_pollution 真图/表但混入大段正文段落（一两行 caption 不算）
  overlap         文字互相重叠、错位压字
  mojibake        乱码/豆腐块/字体坏掉
  multi_element   混入多个独立元素（两张图/图+别的 caption）
  blank           大片空白或几乎无内容

用法：
  python3 audit_crops.py                  # 增量（跳过已判决）
  python3 audit_crops.py --force          # 全量重审
  python3 audit_crops.py --only a.png b.png
  python3 audit_crops.py --workers 8
产出：extraction/crop_audit.json  {assets/crops/<name>: {ok, issues, note, ts}}
"""
import json, re, sys, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
OUT = REPO / "extraction"
SKILL = REPO / "skills" / "paper-extraction"
sys.path.insert(0, str(SKILL))
import m3_caption

PROMPT = """你是论文裁剪图质量审计员。这张 PNG 是从论文 PDF 自动裁剪的「{kind_cn}」，合格标准：只含一个完整、干净、可读的图/表/公式元素（附带其 caption 行算合格）。
逐项检查：
1. prose_only — 内容其实是大段正文散文，根本没有图/表（假裁剪）
2. truncated — 元素不完整：表只有 caption+表头、数据行被切断、图被拦腰切断
3. prose_pollution — 真图/表但上方/下方混入大段正文段落
4. overlap — 文字互相重叠、错位压字
5. mojibake — 乱码/豆腐块/字体坏掉
6. multi_element — 混入多个独立元素（两张图、或图+另一张图的 caption）
7. blank — 大片空白或几乎无内容
只输出 JSON，不要任何其他文字：
{{"ok": true或false, "issues": ["类别标签"...], "note": "≤40字中文简述"}}"""

KIND_CN = {"fig": "图", "tab": "表", "eq": "公式"}


def kind_of(name):
    for k in ("tab", "eq", "fig"):
        if f"-{k}" in name:
            return k
    return "fig"


def audit_one(path):
    try:
        txt = m3_caption.caption(str(path), PROMPT.format(
            kind_cn=KIND_CN[kind_of(path.name)]), max_tokens=8000)
        m = re.search(r"\{.*\}", txt, re.S)
        v = json.loads(m.group(0))
        return {"ok": bool(v.get("ok")), "issues": list(v.get("issues", [])),
                "note": str(v.get("note", ""))[:120],
                "ts": time.strftime("%Y-%m-%d %H:%M")}
    except Exception as e:
        return {"ok": None, "issues": ["audit_error"], "note": str(e)[:120],
                "ts": time.strftime("%Y-%m-%d %H:%M")}


def main():
    workers = 8
    force = "--force" in sys.argv
    only = []
    if "--workers" in sys.argv:
        workers = int(sys.argv[sys.argv.index("--workers") + 1])
    if "--only" in sys.argv:
        only = set(sys.argv[sys.argv.index("--only") + 1:])
    audit_path = OUT / "crop_audit.json"
    audit = json.loads(audit_path.read_text()) if audit_path.exists() else {}
    crops = sorted(OUT.glob("assets/crops/*.png"))
    if only:
        crops = [p for p in crops if p.name in only]
    todo = [p for p in crops
            if force or str(p.relative_to(OUT)) not in audit]
    print(f"crops={len(crops)} audited={len(audit)} todo={len(todo)}", flush=True)
    t0 = time.time()
    done = 0
    with ThreadPoolExecutor(max_workers=workers) as ex:
        for p, res in zip(todo, ex.map(audit_one, todo)):
            audit[str(p.relative_to(OUT))] = res
            done += 1
            if done % 25 == 0 or done == len(todo):
                audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=1))
                bad = sum(1 for v in audit.values() if v.get("ok") is False)
                print(f"  [{done}/{len(todo)}] {time.time()-t0:.0f}s "
                      f"bad_so_far={bad}", flush=True)
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=1))
    bad = {k: v for k, v in audit.items() if v.get("ok") is False}
    err = {k: v for k, v in audit.items() if v.get("ok") is None}
    by_issue = {}
    for v in bad.values():
        for i in v["issues"]:
            by_issue[i] = by_issue.get(i, 0) + 1
    print(f"DONE in {time.time()-t0:.0f}s: total={len(audit)} bad={len(bad)} "
          f"err={len(err)} by_issue={by_issue}")


if __name__ == "__main__":
    main()
