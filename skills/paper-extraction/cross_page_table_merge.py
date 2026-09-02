#!/usr/bin/env python3
"""cross_page_table_merge.py — A3 (MinerU 借鉴): 跨页表格合并检测。

来源:MinerU magic_pdf/post_proc/parse_spell_magic.py 中的跨页合并逻辑
     + magic_pdf/pre_proc/xy_cut.py 的相邻页 IoU 探测。

原理:学术论文的大表经常被 TeX 切成两半,第一页末是表底,第二页首是表顶 +
"Continued" 字样。MuPDF 的 page.get_drawings() 在两页分别给出表横线;若
bottom-of-page-N 与 top-of-page-(N+1) 的 bounding box IoU>0.7 → 合并
(bbox IoU = 表格视觉上确实连续,大概率是同一表)。

本脚本独立运行,扫描 papers/ 下所有 PDF,生成跨页表提示 JSON 供人工/lint gate
确认。**不动现有 crops** — 只是产出清单(低风险,Lint gate 才消费)。

用法:
  python3 cross_page_table_merge.py            # 扫描全部 + 输出 cross_page_table_hints.json
  python3 cross_page_table_merge.py <slug>     # 只扫单篇
  python3 cross_page_table_merge.py --dry-run  # 只打印统计,不写文件

输出:extraction/cross_page_table_hints.json
{
  "<slug>": [
    {"pages": [3, 4], "iou": 0.85, "kind": "table",
     "src_a": "page3 bbox", "src_b": "page4 bbox", "confidence": "high"},
    ...
  ]
}
"""
import fitz, json, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
PAPERS = REPO / "papers"
OUT = REPO / "extraction"
HINTS = OUT / "cross_page_table_hints.json"

# 装订线判据:横线宽度 >150pt、高度 <3pt(同 propose_region)
def page_table_lines(page):
    rects = []
    for d in page.get_drawings():
        r = d["rect"]
        if r.width > 150 and r.height < 3 and r.y0 > 60 and r.y1 < page.rect.height - 60:
            rects.append(r)
    return rects

def iou(a, b):
    inter = a & b
    if inter.is_empty:
        return 0.0
    ua = a.get_area() + b.get_area() - inter.get_area()
    return inter.get_area() / ua if ua > 0 else 0.0

def scan_pdf(slug, pdf_path, iou_thr=0.7):
    doc = fitz.open(str(pdf_path))
    hints = []
    for pno in range(doc.page_count - 1):
        p_a = doc[pno]
        p_b = doc[pno + 1]
        lines_a = page_table_lines(p_a)
        lines_b = page_table_lines(p_b)
        if len(lines_a) < 2 or len(lines_b) < 2:
            continue
        # 表底 = page A 底部 100pt 内的线组 union
        bot_a = fitz.Rect()
        for r in lines_a:
            if r.y0 > p_a.rect.height - 100:
                bot_a |= r
        # 表顶 = page B 顶部 100pt 内的线组 union
        top_b = fitz.Rect()
        for r in lines_b:
            if r.y1 < 100:
                top_b |= r
        if bot_a.is_empty or top_b.is_empty:
            continue
        # IoU 高 + x 范围对齐(允许 ±15pt 误差)→ 高置信合并
        x_overlap = (min(bot_a.x1, top_b.x1) - max(bot_a.x0, top_b.x0))
        x_align = x_overlap > 0 and (bot_a.width - x_overlap) < 30
        if iou(bot_a, top_b) > iou_thr and x_align:
            hints.append({
                "pages": [pno + 1, pno + 2],
                "iou": round(iou(bot_a, top_b), 3),
                "kind": "table",
                "bbox_a": [bot_a.x0, bot_a.y0, bot_a.x1, bot_a.y1],
                "bbox_b": [top_b.x0, top_b.y0, top_b.x1, top_b.y1],
                "confidence": "high" if iou(bot_a, top_b) > 0.85 else "medium",
            })
    doc.close()
    return hints

def main():
    args = sys.argv[1:]
    dry = "--dry-run" in args
    args = [a for a in args if a != "--dry-run"]
    only_slug = args[0] if args else None
    existing = {}
    if HINTS.exists():
        try:
            existing = json.loads(HINTS.read_text())
        except Exception:
            existing = {}
    scanned = 0
    updated = 0
    if only_slug:
        pdf = PAPERS / f"{only_slug}.pdf"
        if not pdf.exists():
            print(f"no pdf for {only_slug}", file=sys.stderr); return 1
        existing[only_slug] = scan_pdf(only_slug, pdf)
        scanned = 1
        if existing[only_slug]:
            updated += len(existing[only_slug])
    else:
        for pdf in sorted(PAPERS.glob("*.pdf")):
            slug = pdf.stem
            hints = scan_pdf(slug, pdf)
            scanned += 1
            if hints:
                existing[slug] = hints
                updated += len(hints)
    if not dry:
        HINTS.write_text(json.dumps(existing, ensure_ascii=False, indent=1))
    print(f"scanned={scanned} cross_page_hints={updated} -> {HINTS}")
    return 0

if __name__ == "__main__":
    sys.exit(main())