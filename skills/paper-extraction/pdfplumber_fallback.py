#!/usr/bin/env python3
"""pdfplumber_fallback.py — B1 借鉴自 AICO-Ascend/AICO-PPT/pdf/reference.md:
pdfplumber 的 lines-strategy 表格抽取作为装订线 walk 失效时的兜底路径。

用法:
  from pdfplumber_fallback import fallback_table_bbox
  region = fallback_table_bbox(doc, pno, cap_block)
  # region is fitz.Rect or None

原理:当 extract_visuals.autofix 的装订线 walk 找不到 ≥2 条横线时(纯文本堆叠表
或稀疏装订表),调 pdfplumber.extract_tables(lines strategy) 探测同 caption 区域
内的表格 bbox,合并 cell bbox 后作为候选区域。

参考:
  AICO-Ascend/AICO-PPT/.agents/skills/pdf/reference.md §pdfplumber Advanced Features
  snap_tolerance=3, intersection_tolerance=15 (生产事实标准)
"""
import fitz
from pathlib import Path

try:
    import pdfplumber
except ImportError:
    pdfplumber = None  # 可选依赖,缺则 fallback 退化为 None


def fallback_table_bbox(doc, pno, cap_block, pdf_path=None):
    """doc:fitz.Document; pno:int; cap_block:[x0,y0,x1,y1,text]; pdf_path:外部传入 PDF 路径
    返回 fitz.Rect(候选表 bbox) 或 None。

    算法:
      1. 用 pdfplumber 抽该页所有 table (lines strategy, snap_tolerance=3)
      2. 筛掉与 caption x 范围无交的 table
      3. 取与 caption y 距离最近的 table bbox (top 在 caption 上方或下方 750pt 内)
      4. 返回 fitz.Rect
    """
    if pdfplumber is None:
        return None
    x0, y0, x1, y1 = cap_block[0], cap_block[1], cap_block[2], cap_block[3]
    # fitz.Document 没有 .name,需要外部传入 pdf_path
    if pdf_path is None:
        return None
    if not Path(pdf_path).exists():
        return None
    try:
        with pdfplumber.open(pdf_path) as pp:
            page = pp.pages[pno]
            # AICO-Ascend 标准参数:lines strategy + snap_tolerance=3 + intersection_tolerance=15
            tables = page.find_tables({
                "vertical_strategy": "lines",
                "horizontal_strategy": "lines",
                "snap_tolerance": 3,
                "intersection_tolerance": 15,
            })
    except Exception:
        return None
    if not tables:
        return None
    # 筛 caption x 范围内 + y 在 ±750pt 的 table
    best = None
    best_dist = float("inf")
    # pdfplumber TableObject.bbox: (x0, top, x1, bottom) 单位 pt
    for tbl in tables:
        bx0, btop, bx1, bbot = tbl.bbox
        # x 必须与 caption 重叠
        if bx1 < x0 or bx0 > x1:
            continue
        # y 距离 caption 最近(上或下)
        dist = min(abs(btop - y0), abs(bbot - y1))
        if dist > 750:
            continue
        if dist < best_dist:
            best_dist = dist
            best = (bx0, btop, bx1, bbot)
    if best is None:
        return None
    return fitz.Rect(*best)