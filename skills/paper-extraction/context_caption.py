#!/usr/bin/env python3
"""context_caption.py — 上下文增强的图/表/公式 M3 解读（用户核心诉求 2026-08-24）。

铁律升级：不再只把孤立图片丢给 M3，而是把「论文原文中讲解该图/表的段落」
+ caption 一起喂给 M3，让解读锚定在论文自己的论述上：
  "图片的理解要结合对应的这篇文章的文本内容，一般这个文章里面一定是有对应
   的文本去讲解这个图片、表格或者公式的，不要单独只依赖 m3 去看这个单一的
   对象去理解，往往是不够的，要关联对应这篇文章的内容描述"

上下文来源：
  - visuals.json 里该 crop 的 caption（PDF 原文）
  - extraction/<slug>.md 全文中引用 "Figure N"/"Table N"/"Fig. N"/"图N-M" 的段落
    （最多 2 段，总上下文 ≤1600 字符）

产出：minimax_captions.json 里 crop 自己的 key（extraction/assets/crops/...），
以 "【图文联合解读】" 开头（幂等标记：已有该前缀的跳过）。

用法：
  python3 context_caption.py              # 全部 crop（跳过已增强的）
  python3 context_caption.py --slug xxx   # 只跑一篇
  python3 context_caption.py --workers 6
"""
import json, re, sys, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
OUT = REPO / "extraction"
SKILL = REPO / "skills" / "paper-extraction"
sys.path.insert(0, str(SKILL))
import m3_caption

MARKER = "【图文联合解读】"

PROMPT_TMPL = """这是论文 «{slug}» 的 {label}。
论文原文 caption：{caption}
论文正文中对它的讲解（引用段落）：
{refs}
---
要求：结合上面的原文论述与你看到的图片内容，做图文联合解读（中文，≤220字）：
1) 该{kind_cn}展示的核心对象与结构/数据（具体、量化，不空泛）；
2) 原文用它论证的关键技术结论；
3) 它在论文整体方法/实验链路中的作用。
若图片本身乱码/无有效内容，直接说明"图像无法辨认，仅依据原文"并按原文解读。"""

KIND_CN = {"fig": "图", "tab": "表", "eq": "公式"}


def cn_label(kind, num):
    """fig/tab 编号 → 正文引用匹配的正则。章节目 图N-M 编码为 N*100+M。"""
    if num >= 100:
        chapter, n = num // 100, num % 100
        pats = [rf"图\s*{chapter}\s*[-–.]\s*{n}\b", rf"表\s*{chapter}\s*[-–.]\s*{n}\b",
                rf"Figure\s*{chapter}\s*[-–.]\s*{n}\b", rf"Table\s*{chapter}\s*[-–.]\s*{n}\b"]
    else:
        pats = [rf"\bFigure\s*{num}\b", rf"\bFig\.?\s*{num}\b",
                rf"\bTable\s*{num}\b", rf"\bTABLE\s*{num}\b",
                rf"图\s*{num}\b", rf"表\s*{num}\b"]
    return re.compile("|".join(pats), re.I)


def paper_paragraphs(slug):
    md = OUT / f"{slug}.md"
    if not md.exists():
        return []
    text = md.read_text(encoding="utf-8", errors="ignore")
    # 去掉 base64/图片嵌入行，按空行切段
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    return paras


def build_context(slug, kind, num, caption):
    paras = paper_paragraphs(slug)
    pat = cn_label(kind, num)
    hits = []
    for p in paras:
        if pat.search(p) and len(p) > 60:
            # 排除 MD 里的 caption 行本身与图片嵌入行
            if p.startswith("!") or p.startswith("[!"):
                continue
            hits.append(re.sub(r"\s+", " ", p))
        if len(hits) >= 2:
            break
    refs = "\n".join(h[:700] for h in hits) or "（正文未找到显式引用段落）"
    ctx = PROMPT_TMPL.format(
        slug=slug, label=f"{'Figure' if kind=='fig' else 'Table' if kind=='tab' else 'Equation'} {num}",
        caption=caption or "（无）", refs=refs, kind_cn=KIND_CN[kind])
    return ctx[:2600]


def all_crops(only_slug=None):
    vis = json.loads((OUT / "visuals.json").read_text())
    todo = []
    for slug, v in vis.items():
        if only_slug and slug != only_slug:
            continue
        for key, kind in (("figures", "fig"), ("tables", "tab"), ("formulas", "eq")):
            for it in v.get(key, []):
                p = OUT / it["path"]
                if not p.exists():
                    continue
                num = it.get("num")
                if num is None:  # formulas 条目无 num，从文件名 eqNN 解析
                    m = re.search(r"-(?:fig|tab|eq)(\d+)\.png$", p.name)
                    num = int(m.group(1)) if m else 0
                todo.append((slug, kind, num,
                             it.get("caption") or it.get("text", ""), p))
    return todo


def already_done(caps, path):
    key = str(path.relative_to(REPO))
    key2 = key.replace("extraction/", "", 1)
    for k in (key, key2):
        if caps.get(k, "").startswith(MARKER):
            return True
    return False


def worker(item, caps_path):
    slug, kind, num, caption, path = item
    prompt = build_context(slug, kind, num, caption)
    text = m3_caption.caption(str(path), prompt)
    if not text.startswith(MARKER):
        text = MARKER + text
    m3_caption.save_caption(str(path), text)
    return f"{slug}-{kind}{num:02d}"


def main():
    only_slug = None
    workers = 5
    args = sys.argv[1:]
    if "--slug" in args:
        only_slug = args[args.index("--slug") + 1]
    if "--workers" in args:
        workers = int(args[args.index("--workers") + 1])
    todo = all_crops(only_slug)
    caps = json.loads((OUT / "minimax_captions.json").read_text())
    todo = [t for t in todo if not already_done(caps, t[4])]
    print(f"crops to (re)caption with context: {len(todo)} (workers={workers})")
    if not todo:
        return
    fail_path = OUT / "context_caption_failures.txt"
    fails = []
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=workers) as ex:
        for i, fut in enumerate(ex.map(lambda it: _safe(it, fails), todo), 1):
            if i % 25 == 0 or i == len(todo):
                el = time.time() - t0
                print(f"  [{i}/{len(todo)}] {el:.0f}s elapsed, fails={len(fails)}", flush=True)
    if fails:
        fail_path.write_text("\n".join(fails))
        print(f"failures ({len(fails)}) -> {fail_path}")
    print(f"DONE in {time.time()-t0:.0f}s")


def _safe(item, fails):
    try:
        return worker(item, None)
    except Exception as e:
        fails.append(f"{item[4].name}: {str(e)[:120]}")
        return None


if __name__ == "__main__":
    main()
