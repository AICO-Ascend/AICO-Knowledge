#!/usr/bin/env python3
"""extract_visuals.py — crop per-figure / per-table / per-formula images from PDFs.

Why: extract_phase1 renders whole pages (1275x1650) — a page may hold body text +
multiple figures. For report insertion we need clean single-element crops.

Strategy (pure geometry, no ML):
  figure: caption block ("Figure N[:.| ]...") anchors the element; the graphic
          cluster (drawings + images + short label blocks) sits directly ABOVE the
          caption. Crop = union of that cluster, bounded by nearest body/caption
          above, x-range = union of cluster members (handles 2-column via caption x).
  table : caption ("Table N[:.]...") sits ABOVE the table; consume text blocks
          below until a body paragraph / next caption / heading.
  formula: only for papers WITHOUT latex source (formulas.json miss) — heuristic
          display-math blocks (has '=', math indicator, short) cropped as images
          so the formula is at least on record as a picture.

Output: extraction/assets/crops/<slug>-figNN.png | -tabNN.png | -eqNN.png
        extraction/visuals.json  {slug: {figures:[...], tables:[...], formulas:[...]}}
Idempotent: existing crops are skipped (delete file to force re-crop).

Usage: python3 skills/paper-extraction/extract_visuals.py [--only slug1,slug2] [--dpi 200]
"""
import fitz, json, re, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
OUT = REPO / "extraction"
CROPS = OUT / "assets" / "crops"
PAPERS = REPO / "papers"

CAP_FIG = re.compile(r'^(Figure|Fig\.?)\s*(\d+)\s*[:.|]?\s*(.*)', re.S)
CAP_FIG_CN = re.compile(r'^图\s*(\d+)\s*[-‑–—]\s*(\d+)\s*[:：]?\s*(.*)', re.S)
CAP_TAB = re.compile(r'^(Table|TABLE)\s*(\d+)\s*[:.]?\s*(.*)', re.S)
CAP_TAB_CN = re.compile(r'^表\s*(\d+)\s*[-‑–—]\s*(\d+)\s*[:：]?\s*(.*)', re.S)

MATH_CHARS = set("∑∏√≈≤≥∈∀αβγδθλμπσφωΣΠ·×⊗⊙→←↑↓ⁿ∇∂∞≠∝⊆∪∩")
MATH_WORDS = ("softmax", "argmax", "argmin", "Attention(", "exp(", "KL(", "∇", "loss")
BODY_MIN_CHARS = 220          # a text block longer than this is body text, not figure label
LABEL_MAX_CHARS = 120         # short blocks inside figure region count as labels
MAX_CROP_H = 700              # pt; a "figure" taller than this is almost full page -> skip crop
MIN_CROP_H = 40
MIN_CROP_W = 80


def paper_slugs():
    out = []
    for line in open(REPO / "papers_effective.md", encoding="utf-8"):
        parts = [p.strip() for p in line.split("|")]
        inner = parts[1:-1]
        if not inner or not re.match(r'\d+$', inner[0] or ''):
            continue
        m = re.match(r'✓ papers/(.+)\.pdf', inner[5])
        if m and m.group(1) not in out:
            out.append(m.group(1))
    return out


def block_text(b):
    return " ".join(s["text"] for l in b.get("lines", []) for s in l["spans"]).strip()


# 同一编号出现多个 "Figure N ..." 块时，真 caption 几乎都是独立短块，
# 句首行内引用（"Figure 6 shows validation perplexity as a function of..."）
# 则是长段落块。不能用首词动词过滤（TMLR 风格真 caption 就是动词开头：
# "Table 19 summarizes the notation..."），改为：同页 caption 候选按块长
# 升序处理，短块（caption-like）先占位，长段落行内引用自然饿死。
# （2026-08-24：megatron fig06 双候选竞争 + 40 张真 caption 误杀教训）


def match_caption(txt):
    """-> (kind, num, caption_tail) or None. kind in {fig, tab}."""
    m = CAP_FIG_CN.match(txt)
    if m:
        return "fig", int(m.group(1)) * 100 + int(m.group(2)), m.group(3)
    m = CAP_TAB_CN.match(txt)
    if m:
        return "tab", int(m.group(1)) * 100 + int(m.group(2)), m.group(3)
    m = CAP_FIG.match(txt)
    if m and len(m.group(3)) > 3:
        return "fig", int(m.group(2)), m.group(3)
    m = CAP_TAB.match(txt)
    if m and len(m.group(3)) > 3:
        return "tab", int(m.group(2)), m.group(3)
    return None


def line_mathy(txt):
    """line-level display-math heuristic (mirrors extract_phase1.extract_formulas)."""
    s = re.sub(r'\s+', ' ', txt).strip()
    if not (6 <= len(s) <= 180) or '=' not in s:
        return False
    if not (any(c in MATH_CHARS for c in s) or any(w in s for w in MATH_WORDS)):
        return False
    if len(s.split('=', 1)[0].split()) > 8:
        return False
    if re.search(r'http|arxiv|figure|table|section', s, re.I):
        return False
    # prose guard (2026-08-23): a display equation's tokens are mostly math, not
    # English words. "γ = (γij) that redistributes mass ..." is prose with inline
    # math — reject when >55% of tokens are plain English words.
    toks = s.split()
    if toks:
        english = sum(1 for tk in toks if re.fullmatch(r'[a-zA-Z]{3,}', tk))
        if english / len(toks) > 0.55:
            return False
    return True


def formula_regions(page, max_keep=12):
    """Detect display-formula regions at LINE level, expand to adjacent short lines
    (multi-line equations: piecewise cases, subscript rows) + overlapping drawings.

    Guards against prose-capture (2026-08-23 fix): growth stays in the seed's
    column, merged region capped at 150pt tall / 30 words — a display equation is
    short; anything taller/longer is body text with inline math, not a formula."""
    col_mid = page.rect.width / 2
    lines = []
    for b in page.get_text("dict")["blocks"]:
        if b["type"] != 0:
            continue
        for l in b.get("lines", []):
            txt = "".join(s["text"] for s in l["spans"]).strip()
            if txt:
                lines.append((fitz.Rect(l["bbox"]), txt))
    # display equations are centered/short and never start with a prose
    # connective ("and νj, and that Σ..." is a body line with inline math)
    PROSE_START = ("and", "the", "that", "this", "these", "where", "with",
                   "which", "for", "from", "into", "over", "under", "when",
                   "while", "if", "in", "on", "at", "by", "to", "we", "it")
    def is_seed(r, t):
        if not line_mathy(t):
            return False
        first = t.split()[0].lower().strip(",;:()") if t.split() else ""
        if first in PROSE_START:
            return False
        col_w = col_mid if (r.x0 + r.x1) / 2 < col_mid else page.rect.width - col_mid
        col_w = col_w - 2 * 50  # minus typical margins
        strong_math = sum(1 for c in t if c in MATH_CHARS) >= 2
        return strong_math or r.width < 0.72 * col_w
    seeds = [(r, t) for r, t in lines if is_seed(r, t)]
    if not seeds:
        return []
    drawings = [dr["rect"] for dr in page.get_drawings()
                if dr["rect"].width > 4 and dr["rect"].height > 4]
    out, used = [], []
    for r, t in seeds:
        if len(out) >= max_keep:
            break
        if any(abs(r.y0 - u) < 30 for u in used):
            continue
        seed_col = 0 if (r.x0 + r.x1) / 2 < col_mid else 1
        # grow: merge nearby short non-body lines in the SAME column only
        region = fitz.Rect(r)
        words = len(t.split())
        for r2, t2 in lines:
            if r2 is r:
                continue
            if abs((r2.y0 + r2.y1) / 2 - (r.y0 + r.y1) / 2) > 42:
                continue
            r2_col = 0 if (r2.x0 + r2.x1) / 2 < col_mid else 1
            if r2_col != seed_col:
                continue
            if r2.x0 > r.x1 + 60 or r2.x1 < r.x0 - 60:
                continue
            if len(t2) <= 60 and not re.search(r'^(Figure|Table)\s+\d', t2):  # display-math lines are short; prose lines fill the column
                # merged line must itself be mathy or a tiny lead-in ("subject to:")
                lead_in = len(t2) <= 30
                if not (any(c in MATH_CHARS for c in t2) or '=' in t2 or lead_in):
                    continue
                cand = region | r2
                if cand.height <= 150 and words + len(t2.split()) <= 30:
                    region = cand
                    words += len(t2.split())
        for dr in drawings:
            if dr.y1 >= region.y0 - 6 and dr.y0 <= region.y1 + 6 \
               and dr.x1 >= region.x0 and dr.x0 <= region.x1:
                if (region | dr).height <= 150:
                    region |= dr
        # 区域级英文词率闸：growth 可能把种子周围的散文行卷进来
        # （linear-optimal eq02 整段 OT 定义散文被裁成"公式"）。
        # 真 display 公式区域英文词占比低；>45% 即整段散文，弃。
        region_tokens = []
        for r2, t2 in lines:
            if fitz.Rect(r2).intersects(region):
                region_tokens.extend(t2.split())
        eng = sum(1 for w in region_tokens
                  if len(w) >= 2 and w.isalpha() and w.isascii())
        if region_tokens and eng / len(region_tokens) > 0.45:
            continue
        used.append(r.y0)
        # x 拉满种子所在栏：多行 display 公式常有水平延展的独立 line 对象
        # （求和号右半、分段右支），±60pt 的 growth 窗会拦腰截断
        # （scalable-moe eq01 "output(x)=W↑·(Σp..." 右缘被切）。
        # y 区间已经收紧（≤150pt），x 给全栏不会卷入散文。
        cols = page_columns(page.get_text("dict")["blocks"], page.rect.width)
        gutter = 14
        if len(cols) == 1:
            region.x0, region.x1 = 8, page.rect.width - 8
        else:
            cx0, cx1 = cols[col_of(r, cols)]
            region.x0 = max(8, cx0 + (0 if cx0 == 0 else gutter))
            region.x1 = min(page.rect.width - 8, cx1 - (0 if cx1 >= page.rect.width else gutter))
        out.append((region, re.sub(r'\s+', ' ', t).strip()))
    return out


HEADING = re.compile(r'^\d+(\.\d+)+\.?\s|^\d+\.\s+[A-Z]')   # "2.2.2. X" or "4. Discussion"
# 附录节标题："K Validation Sets and ..."（字母+连续首大写词）或 small-caps
# 字距打散变体 "K V ALIDATION S ETS..."（letter-spacing 每字母一个 span，
# block_table_score 误判 multi-span=表格行 → hyper-connections tab13 假裁剪）。
# 第二词必须全大写或再跟首大写词——"S SpecDecoding 1.47"（表格行）不匹配。
HEADING_APPENDIX = re.compile(
    r'^[A-Z]\s+(?:[A-Z]\s?[A-Z]{2,}(?:\s+[A-Z]\s?[A-Za-z]{2,})+'
    r'|[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)')


def page_columns(blocks, page_w):
    """Detect column x-ranges. 2-column only when the page splits into two
    non-overlapping text bands; full-width blocks crossing mid => single column.
    (2026-08-24 fix: deepseek-v3 single-col pages were falsely split at mid,
    which truncated table x-windows to half a column.)
    (2026-08-24 fix2: 行级 cross 比例在"正文通栏+大量短行"的单栏页被稀释
     （scalable-moe p64: 27/89=0.30<0.4 误判双栏）。宽块判据更稳：单栏页有
     大量 >0.72 页宽的段落块；双栏页只有通栏图表 caption 一两条。)"""
    spans = []
    for b in blocks:
        if b["type"] != 0:
            continue
        r = b["bbox"]
        if r[2] - r[0] > 30:
            spans.append((r[0], r[2]))
    if len(spans) < 8:
        return [(0, page_w)]
    wide = sum(1 for x0, x1 in spans if x1 - x0 > 0.72 * page_w)
    if wide >= 4:
        return [(0, page_w)]
    mid = page_w / 2
    cross = sum(1 for x0, x1 in spans if x0 < mid - 20 and x1 > mid + 20)
    if cross > len(spans) * 0.4:
        return [(0, page_w)]
    left = [s for s in spans if (s[0] + s[1]) / 2 < mid]
    right = [s for s in spans if (s[0] + s[1]) / 2 >= mid]
    if len(left) >= 4 and len(right) >= 4:
        return [(0, mid), (mid, page_w)]
    return [(0, page_w)]


def col_of(rect, cols):
    c = (rect.x0 + rect.x1) / 2
    for i, (x0, x1) in enumerate(cols):
        if x0 <= c < x1:
            return i
    return 0


def col_window(rect, cols, page_w):
    """锚块的 x 工作窗：通栏锚（宽 >60% 页宽）→ 整页，否则所在栏。
    a-survey p24：通栏 TABLE caption 中心恰落页中，被 col_of 分进"右栏"，
    x 窗 [306,584] 把表格左半截没。"""
    if rect.width > 0.6 * page_w:
        return 0, page_w
    return cols[col_of(rect, cols)]


def crop_pix(page, rect, dpi, max_h=MAX_CROP_H):
    rect = rect & page.rect
    if rect.is_empty or rect.height < MIN_CROP_H or rect.width < MIN_CROP_W:
        return None
    if rect.height > max_h:
        return None
    mat = fitz.Matrix(dpi / 72, dpi / 72)
    return page.get_pixmap(matrix=mat, clip=rect)


def block_table_score(b):
    """table-likeness of a text block (2026-08-24 rework):
      2 = definitely table data (digit-dominated rows, symbol-dense formula rows,
          or majority multi-cell rows w/ digits)
      1 = probably table (majority multi-cell rows, or moderately digit/symbol-dense)
      0 = prose (justified text has ~1 span/line and few digits/symbols —
          italic words no longer inflate the score because we use RATIOS)
    sym 通道：公式表格行 "Post Norm [22] Norm(x+Sublayer(x))" 数字少但
    符号密度高（a-survey tab07 被 prose 闸误杀）。"""
    lines = b.get("lines", [])
    if not lines:
        return 0
    txt = block_text(b)
    if not txt:
        return 0
    multi_ratio = sum(1 for l in lines if len(l["spans"]) >= 2) / len(lines)
    digit_ratio = sum(c.isdigit() for c in txt) / len(txt)
    sym_ratio = sum(1 for c in txt if not c.isalnum() and not c.isspace()) / len(txt)
    if digit_ratio > 0.2 or sym_ratio > 0.18:
        return 2
    if multi_ratio >= 0.5 and digit_ratio > 0.1:
        return 2
    if multi_ratio >= 0.5 or digit_ratio > 0.12 or sym_ratio > 0.15:
        return 1
    return 0


def is_heading_or_caption(t):
    # HEADING_APPENDIX: 附录字母节标题 "K Validation Sets..." 及 small-caps
    # 字距打散变体 "K V ALIDATION S ETS..."（letter-spacing 每字母一个 span，
    # block_table_score 误判 multi-span=表格行 → hyper-connections tab13 假裁剪）
    return bool(HEADING.match(t) or HEADING_APPENDIX.match(t)) \
        or match_caption(t) is not None


def is_folio(br, t, page_h):
    """页码块：纯数字短文本且位于页顶/页底边距。a-survey tab07 的 "24" 因
    数字密度 sc=2 被当表格内容采进 crop（caption-only 假裁剪的根因）。"""
    return bool(re.fullmatch(r"\d{1,4}", t.strip())) and \
        (br.y0 < 50 or br.y1 > page_h - 50)


def drawing_zones(drawings, page_area=1, blocks=()):
    """页面矢量绘制 rect 列表（局部墨迹）。表格 walk 用"文字块与绘制相交"
    来排除图表内文字（图例/轴标签这类 sc=2 高分块，attention-residuals
    tab02 上报 #19）。两类不算局部墨迹：
      - 超大矩形（>30% 页面积）
      - 与 >10 个文字块相交的容器框（Figure 5 外框 [50,62,546,318] 把
        deepseek-v3 p13 的真表格行也框进去，25% 页面积但本质是容器）
    真表格行的文字 bbox 不与局部绘制相交（框线在行间隙），不受影响。"""
    out = []
    text_rects = [fitz.Rect(b["bbox"]) for b in blocks if b["type"] == 0]
    for d in drawings:
        r = d["rect"]
        if r.width <= 2 or r.height <= 2:
            continue
        if r.width * r.height >= 0.3 * page_area:
            continue
        if sum(1 for tr in text_rects if r.intersects(tr + (-8, -8, 8, 8))) > 10:
            continue
        out.append(r)
    return out


def zones_with_text(zones, blocks):
    """底纹色块判定：覆盖任一文字 span ≥60% 的 drawing = 表格单元格底纹
    （色块上有字，是表格自身组成部分），永不视为污染；上面没字的才是
    纯图形（图例 marker/轴元素）。页级判定——底纹常与相邻行块充气相交，
    按块判定会误杀邻行（a-survey tab10/tab16 全表数据行被排除的根因）。"""
    spans = [fitz.Rect(sp["bbox"]) for b in blocks if b["type"] == 0
             for line in b.get("lines", []) for sp in line.get("spans", [])]
    out = set()
    for i, dr in enumerate(zones):
        d = fitz.Rect(dr)
        for sr in spans:
            inter = sr & d
            if not inter.is_empty and abs(inter) >= 0.6 * abs(sr):
                out.add(i)
                break
    return out


def collect_table_region(blocks, cap_rect, x0, x1, direction, page_h=842,
                         zones=(), text_zones=(), prose_w=0):
    # 采集窗 ±640pt：堆叠子表（a-survey tab16 三段能力评测表 y91-592）
    # 表体可超 500pt，420 窗会砍掉末段数据行；真正的截断靠间距/节标题/
    # caption/prose 闸，不靠这个粗界
    """Consume table blocks from caption in given direction (+1 below, -1 above).
    Returns picked [(rect, block)] adjacent to the caption.

    流程：先按 y/x 窗过滤候选 → 按到 caption 的空间距离排序 → 在空间序上施加
    截断闸（遇其它 caption/节标题/长散文即停）→ sc>=1 连续拾取（短 score-0 行
    容忍 <=2 连）。2026-08-24 修复：旧版在 MuPDF 块序（PDF 内容流序，!=视觉序）
    上截断，deepseekmath tab09 把隔了两个表格的 Table 7 行采进来，bounding box
    一框三张表。"""
    cands = []
    for b in blocks:
        # 嵌入图像块：VL 系技术报告（qwen3-vl/kimi-vl/k2.5）把整表渲染为图片，
        # 只走文本块会漏掉表体 → caption-only 假裁剪。图像块视作 sc=2 表格内容。
        if b["type"] == 1:
            br = fitz.Rect(b["bbox"])
            if direction == +1:
                if br.y0 < cap_rect.y1 - 2 or br.y0 > cap_rect.y1 + 640:
                    continue
            else:
                if br.y1 > cap_rect.y0 + 2 or br.y1 < cap_rect.y0 - 640:
                    continue
            if br.x1 < x0 or br.x0 > x1 or br.width < 60 or br.height < 20:
                continue
            cands.append((br, b, ""))
            continue
        if b["type"] != 0:
            continue
        br = fitz.Rect(b["bbox"])
        if direction == +1:
            if br.y0 < cap_rect.y1 - 2 or br.y0 > cap_rect.y1 + 640:
                continue
        else:
            if br.y1 > cap_rect.y0 + 2 or br.y1 < cap_rect.y0 - 640:
                continue
        # x 窗微重叠排除：双栏论文左栏散文块常与右栏 caption 的 x 窗有
        # 6-12pt 微重叠，被当候选吸入并把 union 拉成通栏（block-diffusion
        # tab03）。排除条件 = 重叠 <20pt 且 不足块宽一半 —— 窄单元格块
        # （"93"/"2.78T" 宽 <20pt）整格在窗内是 100% 重叠，必须放行
        # （kimi-k3 tab01 整表被误杀的教训）
        _xov = min(br.x1, x1) - max(br.x0, x0)
        if br.x1 < x0 or br.x0 > x1 or (_xov < 20 and _xov < 0.5 * br.width):
            continue
        t = block_text(b)
        if not t or is_folio(br, t, page_h):
            continue
        def _polluting(dr):
            d = fitz.Rect(dr)
            if d.height <= 3:
                return False  # 表格横线（booktabs 横规），不是外来图形
            if d.contains(br):
                return False  # 行级底纹：文字坐在整行色块上
            return d.intersects(br + (-8, -8, 8, 8))
        if zones and any(_polluting(dr) for zi, dr in enumerate(zones)
                         if zi not in text_zones):
            continue  # 与无字矢量图形相交的文字（图例/轴标签），不是表格内容。
            # 用"块与绘制相交"而非"块在 zone bbox 内"：deepseek-v3 p13 的
            # 真表格行落在 Figure 5 zone 的 bbox 里但行上没有绘制
        cands.append((br, b, t))
    # 空间序：离 caption 由近及远
    cands.sort(key=lambda c: c[0].y0, reverse=(direction == -1))
    picked = []
    zero_run = 0  # 连续短 score-0 行容忍 <=2：纯文字表头/子表头行不得分，
                  # 但后面的数据行得分；valid_table 要求过半 sc>=1 兜底
    def strong_ahead(i, min_count):
        """后续 4 块内"硬表格证据"计数（图像块，或非宽长文的 sc>=1 块）。
        宽长文 sc1 块不算证据：medusa tab1 上方 fig4 caption 续行（宽长文 sc1）
        会让 look-ahead 连锁放行造成污染；let-it-flow tab1 的 "Architecture
        MoE..." 宽行则靠后面的数字数据行证明自己是表格行。"""
        n = 0
        for _, c2, t2 in cands[i + 1:i + 5]:
            if c2["type"] == 1:
                return True
            s2 = block_table_score(c2)
            if s2 >= 1:
                br2 = fitz.Rect(c2["bbox"])
                wordy = len(t2.split()) > 18 and s2 < 2
                if not (br2.width > 0.55 * (prose_w or (x1 - x0)) and wordy):
                    n += 1
        return n >= min_count

    edge_used = False   # 远端短表头/脚注吸收一次（deepseek-v3 tab5 的
                        # "Benchmark (Metric) # Shots..." 在表格远缘）
    prev_y = None       # 上一块的行进方向边缘 y
    prev_br = None      # 上一拾取块（并列单元格 same_row 判定用）
    for i, (br, b, t) in enumerate(cands):
        # 间距闸：表格行是紧排的；与上一块间距 >22pt 且非强表格行 ⇒ 已离开
        # 表格（medusa tab1 与其上方 fig4 caption 之间有 23pt 断层，
        # 断层另一侧的散点图轴标签会喂活 look-ahead 造成全图污染）
        if prev_y is not None:
            gap = (br.y0 - prev_y) if direction == +1 else (prev_y - br.y1)
            if gap > 22 and b["type"] != 1 and block_table_score(b) < 2:
                break
        if b["type"] == 1:              # 嵌入图像块 = 图像版表格主体，直接收
            picked.append((br, b))
            prev_y = br.y1 if direction == +1 else br.y0
            continue
        if match_caption(t):
            break                       # 其它表/图的 caption 永远是硬边界
        if is_heading_or_caption(t) and not strong_ahead(i, 1):
            # 节标题样式块后面还有硬表格证据 → 是表格内容（"4.5 GPT-5.2"
            # 版本号命中节标题正则，掐断 kimi-k2-5 tab04 的采集）
            break
        sc = block_table_score(b)
        # prose gate: 宽长文 + 非强表格 = 正文段落。窄块豁免（公式/单元格块
        # 天然窄，a-survey tab07）。宽长文行的证据阈值随已收行数升档：
        # 已收 <3 行（表格尚未成形，deepseek-v3 tab2 的公式行只领先 fig
        # caption 一步）1 个硬证据即放行；已收 >=3 行（表格大概率完整，
        # 再往外多半是他物）需 2 个（medusa tab1 的 fig4 caption 续行拦下）
        # 宽度参照用栏宽（prose_w）而非采集窗：双栏论文的通栏 caption 给
        # 整页窗，栏宽散文块就成"窄块"豁免 prose gate，整栏 sc1 散文被
        # 无限吸入（megatron tab08 表后整页散文尾巴的根因）
        wide_block = br.width > 0.55 * (prose_w or (x1 - x0))
        wordy = len(t.split()) > 18 or len(t) > BODY_MIN_CHARS
        need = 2 if len(picked) >= 3 else 1
        if wide_block and wordy and sc < 2 and not strong_ahead(i, need):
            break
        # 与上一拾取块同 y 带的是并列单元格（多列组合表头：a-survey tab10
        # 六个 sc0 表头单元格挤在 y125-146 同一带，逐个消耗 strong_ahead/
        # edge 额度会在第二个单元格就断行）
        same_row = prev_br is not None and br.y0 < prev_br.y1 - 2 \
            and br.y1 > prev_br.y0 + 2
        if sc >= 1:
            picked.append((br, b))
        elif len(t) <= 250 and strong_ahead(i, 1):
            # 长 sc0 块 + 后面有硬表格证据 = 合并表头单元格（a-survey tab9
            # "Models A800 Full Tuning A800 LoRA..." 211 字符一块）；散文行
            # 后面极少紧跟 sc2 数据行，strong_ahead 把关
            picked.append((br, b))
        elif len(t) <= 150 and (not edge_used or same_row):
            # 短 sc0 行：表格在后面继续 → 连接行（子表头）；
            # 否则作为远缘表头/脚注吸收一次
            picked.append((br, b))
            if not same_row:
                edge_used = True
        else:
            break
        prev_y = br.y1 if direction == +1 else br.y0
        prev_br = br
    return picked




def process_paper(slug, dpi, latex_slugs):
    pdf = PAPERS / f"{slug}.pdf"
    if not pdf.exists():
        return None
    doc = fitz.open(str(pdf))
    res = {"figures": [], "tables": [], "formulas": []}
    seen_fig, seen_tab, seen_eq = set(), set(), set()
    for pno in range(doc.page_count):
        page = doc[pno]
        d = page.get_text("dict")
        blocks = d["blocks"]
        # caption blocks with geometry
        caps = []
        for b in blocks:
            if b["type"] != 0:
                continue
            mc = match_caption(block_text(b))
            if mc:
                caps.append((mc[0], mc[1], mc[2], fitz.Rect(b["bbox"]),
                             len(block_text(b))))
        # 短块（caption-like）优先于长段落（行内引用）占位同一编号
        caps.sort(key=lambda c: c[4])
        if not caps and slug in latex_slugs:
            continue
        # collect graphic + label elements for figure region union
        cols = page_columns(blocks, page.rect.width)
        gfx = []        # (rect, is_visual) — is_visual=True for drawings/embedded images
        hard = []       # 真图形（嵌入图/矢量 drawings）——方向探测只认硬图形，
                        # 数字密集的散文行（"...示意图如下：" sc=2）不算
        for b in blocks:
            r = fitz.Rect(b["bbox"])
            if b["type"] == 1:  # embedded image
                gfx.append((r, True))
                hard.append(r)
            elif b["type"] == 0:
                t = block_text(b)
                # 节标题（"4.7 超节点能力"）数字密度高但不是图形内容 ——
                # digit_dense 和 block_table_score 都会被节编号骗过，
                # 导致 ascend-950 fig417 纯文本假图复活；数字节标题整体排除。
                # （只排数字 HEADING：HEADING_APPENDIX 类小型大写标题
                #  "VIRTUAL STAGE 0" 是图内面板标题，排除了会削掉图顶）
                if HEADING.match(t):
                    continue
                digit_dense = t and sum(c.isdigit() for c in t) / len(t) > 0.2
                if 0 < len(t) <= LABEL_MAX_CHARS or block_table_score(b) >= 2 \
                        or (len(t) <= 400 and digit_dense):
                    # digit-dense text blocks ARE the visual content of table-figures
                    gfx.append((r, bool(digit_dense) or block_table_score(b) >= 2))
        for dr in page.get_drawings():
            r = dr["rect"]
            if r.width > 2 and r.height > 2:
                gfx.append((r, True))
                hard.append(r)
        # caption rects act as separators (another caption bounds this one's region)
        cap_rects = [c[3] for c in caps]
        for kind, num, tail, r, _blen in caps:
            if kind == "fig":
                if num in seen_fig:
                    continue
                # NOTE: seen_fig.add(num) 只能在裁剪成功后做 —— 句首 "Figure 3 shows..."
                # 这类正文行内引用会先于真 caption 出现，提前占位会把真图饿死
                # （2026-08-24：28 张孤儿图的根因）
                # 栏位约束：图只在 caption 所在栏内聚类（2026-08-24 跨栏污染修复）
                cx0, cx1 = col_window(r, cols, page.rect.width)
                x0, x1 = max(r.x0 - 30, cx0), min(r.x1 + 30, cx1)
                # 方向判定：caption-above 布局（中文白皮书 ascend-950 全篇）的图
                # 在 caption 下方。判据 = caption 下方紧贴硬图形 且 上方 500pt
                # 窗口内没有"无主的"硬图形 —— 上方图形若被更早的 caption 紧贴
                # 认领（caption 在图顶上方），说明本篇是 caption-above 布局，
                # 该图属于上一张 caption，不能挡住本 caption 向下取图。
                # （a-survey fig01 上方是矢量折线图、下方 25pt 内是 fig02 的图，
                # 纯邻接探测会把 fig02 的图裁给 fig01）
                ADJ = 25
                adj_below = any(g.x1 > x0 and g.x0 < x1
                                and r.y1 - 4 <= g.y0 <= r.y1 + ADJ
                                for g in hard)
                hard_above = [g for g in hard
                              if g.y1 <= r.y0 + 4 and g.y0 > r.y0 - 500
                              and g.x1 > x0 and g.x0 < x1]
                def _owned(g):
                    return any(c is not r and c.y1 <= g.y0 + 4
                               and c.y1 > g.y0 - 120
                               and c.x1 > x0 and c.x0 < x1
                               for c in cap_rects)
                unowned_above = [g for g in hard_above if not _owned(g)]
                if adj_below and not unowned_above:
                    # caption-above 布局：收集 caption 下方的图形簇，
                    # 下一张 caption / 长正文块作为下界
                    below = [(g, vis) for g, vis in gfx
                             if g.y0 >= r.y1 - 4 and g.y0 < r.y1 + 500
                             and g.x1 > x0 and g.x0 < x1]
                    other_caps_below = [c for c in cap_rects
                                        if c.y0 >= r.y1 - 1
                                        and c.x1 > x0 and c.x0 < x1]
                    ceil = min([c.y0 for c in other_caps_below],
                               default=page.rect.y1 - 50)
                    below = [(g, vis) for g, vis in below if g.y0 < ceil]
                    # 链式 x 扩展（与 above 模式同理）：行内引用锚点在单栏内，
                    # 通栏图会被栏位 x 窗截断（longspec fig01 右半被切、
                    # kimi-k3 fig06 左半被切）。不越过 ceil（下一 caption）
                    if below:
                        ux = fitz.Rect(below[0][0])
                        for g, _ in below[1:]:
                            ux |= g
                        in_keys = {id(g) for g, _ in below}
                        grown = True
                        while grown:
                            grown = False
                            for g, vis in gfx:
                                if id(g) in in_keys or g.y0 >= ceil:
                                    continue
                                if g.y1 < ux.y0 - 10 or g.y0 > ux.y1 + 10:
                                    continue
                                if g.x1 > ux.x0 - 5 and g.x0 < ux.x1 + 5:
                                    below.append((g, vis))
                                    in_keys.add(id(g))
                                    ux |= g
                                    grown = True
                    if not below or not any(vis for _, vis in below):
                        continue
                    seen_fig.add(num)
                    # 内容下界只认硬图形：sc=2 的散文段（"L0C Buffer->...随路量化"）
                    # 会把 max_vis_y1 拖进正文，把整段散文/节标题框进裁剪
                    hard_ids = {id(g) for g in hard}
                    hard_below = [g for g, _vis in below if id(g) in hard_ids]
                    if hard_below:
                        max_vis_y1 = max(g.y1 for g in hard_below)
                        below = [(g, vis) for g, vis in below
                                 if id(g) in hard_ids or g.y0 <= max_vis_y1 + 40]
                    else:
                        max_vis_y1 = max(g.y1 for g, vis in below if vis)
                        below = [(g, vis) for g, vis in below
                                 if vis or g.y0 <= max_vis_y1 + 40]
                    # 拷贝再 union —— u |= g / u.y1=... 会原地改写 gfx/hard 里
                    # 共享的 Rect 对象，污染同页后续 caption 的方向探测
                    # （ascend-950 fig403 因此被拐进 above-mode 裁了 fig402 的图）
                    u = fitz.Rect(below[0][0])
                    for g, _ in below[1:]:
                        u |= g
                    u.y0 = max(r.y1 + 2, u.y0 - 4)
                    u.y1 = min(ceil - 2, max_vis_y1 + 45)
                    # 视觉元素之后的任何文字块（正文/节标题）都不能进裁剪框 ——
                    # 真图标签 ≤120 字符已进 gfx union，剩下的都是页内正文
                    tail_txt = [fitz.Rect(b["bbox"]).y0 for b in blocks
                                if b["type"] == 0
                                and fitz.Rect(b["bbox"]).y0 > max_vis_y1
                                and block_text(b).strip()
                                and fitz.Rect(b["bbox"]).x1 > x0
                                and fitz.Rect(b["bbox"]).x0 < x1]
                    if tail_txt:
                        u.y1 = min(u.y1, min(tail_txt) - 4)
                    u.x0 = max(0, u.x0 - 4); u.x1 = min(page.rect.x1, u.x1 + 4)
                    out = CROPS / f"{slug}-fig{num:02d}.png"
                    item = {"num": num, "page": pno + 1,
                            "caption": re.sub(r'\s+', ' ', tail).strip()[:300],
                            "path": f"assets/crops/{out.name}"}
                    if out.exists():
                        res["figures"].append(item); continue
                    pix = crop_pix(page, u, dpi)
                    if pix:
                        pix.save(str(out))
                        res["figures"].append(item)
                    continue
                above = [(g, vis) for g, vis in gfx
                         if g.y1 <= r.y0 + 4 and g.y0 > r.y0 - 500
                         and g.x1 > x0 and g.x0 < x1]
                other_caps_above = [c for c in cap_rects if c.y1 <= r.y0 + 1
                                    and c.x1 > x0 and c.x0 < x1]
                floor = max([c.y1 for c in other_caps_above], default=50)
                # floor 也必须栏位约束：双栏排版里另一栏的正文流得更低，
                # 会把本栏页首图的 floor 抬到图之上（sarathi fig02/megatron fig06）
                body_above = [fitz.Rect(b["bbox"]).y1 for b in blocks
                              if b["type"] == 0
                              and len(block_text(b)) > BODY_MIN_CHARS
                              and fitz.Rect(b["bbox"]).y1 <= r.y0 - 30
                              and fitz.Rect(b["bbox"]).x1 > x0
                              and fitz.Rect(b["bbox"]).x0 < x1]
                floor = max(floor, max(body_above, default=50))
                above = [(g, vis) for g, vis in above if g.y1 > floor]
                # 链式 x 扩展：多面板通栏图（attention-residuals fig05 左面板被
                # 栏位 x 窗切掉）——已收块的 y 带内，与 union x 相邻的图形块
                # 迭代并入，直到不动点。跨栏污染仍由初始栏位窗 + y 带约束。
                if above:
                    u0 = fitz.Rect(above[0][0])
                    for g, _ in above[1:]:
                        u0 |= g
                    in_keys = {id(g) for g, _ in above}
                    grown = True
                    while grown:
                        grown = False
                        for g, vis in gfx:
                            if id(g) in in_keys:
                                continue
                            if g.y1 < u0.y0 - 10 or g.y0 > u0.y1 + 10:
                                continue
                            if g.x1 > u0.x0 - 5 and g.x0 < u0.x1 + 5:
                                above.append((g, vis))
                                in_keys.add(id(g))
                                u0 |= g
                                grown = True
                # 图形有效性：union 里必须有真图形元素（drawings/嵌入图/表格块），
                # 纯文字标签簇 = 不是图（dynamic-lcm fig06 曾把节标题裁成图）
                has_visual = any(vis for _, vis in above)
                if not above or not has_visual:
                    continue
                seen_fig.add(num)
                # 尾部散文修剪：anchor 是行内引用（ascend-950 无真 caption 块）时，
                # 图与 anchor 之间的散文会被 bounding box 一并框入 —— union 的
                # 下缘收回到最后一个真图形元素（文字标签最多再带 40pt）
                max_vis_y1 = max(g.y1 for g, vis in above if vis)
                above = [(g, vis) for g, vis in above
                         if vis or g.y0 <= max_vis_y1 + 40]
                u = fitz.Rect(above[0][0])
                for g, _ in above[1:]:
                    u |= g
                u.y1 = min(r.y0 - 2, max_vis_y1 + 45)
                # x 只做页边距收敛，不做栏位硬钳：跨栏宽图（scalable-moe fig30/
                # cuda-agent fig01）被栏界拦腰截断；防跨栏污染靠上面的窗口过滤，
                # 不靠 union 钳制
                u.x0 = max(0, u.x0 - 4); u.x1 = min(page.rect.x1, u.x1 + 4)
                u.y0 = max(0, u.y0 - 4)
                out = CROPS / f"{slug}-fig{num:02d}.png"
                item = {"num": num, "page": pno + 1,
                        "caption": re.sub(r'\s+', ' ', tail).strip()[:300],
                        "path": f"assets/crops/{out.name}"}
                if out.exists():
                    res["figures"].append(item); continue
                pix = crop_pix(page, u, dpi)
                if pix:
                    pix.save(str(out))
                    res["figures"].append(item)
            else:  # table: 方向判定 —— 紧贴 caption 的表格块在哪侧
                zones = drawing_zones(page.get_drawings(), page.rect.width * page.rect.height, blocks)
                t_zones = zones_with_text(zones, blocks) if zones else set()
                if num in seen_tab:
                    continue
                cols = page_columns(blocks, page.rect.width)
                cx0, cx1 = col_window(r, cols, page.rect.width)
                x0, x1 = max(r.x0 - 20, cx0), min(r.x1 + 20, cx1)
                prose_w = min(c1 - c0 for c0, c1 in cols)
                # 堆叠表格（[tab8行][tab8 caption][tab9行][tab9 caption]）里
                # "先试下方"会把 tab8 错配到 tab9 的行（deepseekmath 实测）。
                # caption-below 风格的表格行紧贴 caption 上方，反之在下方；
                # 两侧都紧贴时上方优先（caption-below 约定）。
                above_adj = below_adj = False
                for b in blocks:
                    br = fitz.Rect(b["bbox"])
                    if br.x1 < x0 or br.x0 > x1:
                        continue
                    if b["type"] == 0 and is_folio(br, block_text(b), page.rect.height):
                        continue
                    tableish = b["type"] == 1 and br.width > 60 and br.height > 20 \
                               or b["type"] == 0 and block_table_score(b) >= 1
                    if not tableish:
                        continue
                    # 60pt 探测窗：caption 与表体首行间常有一个空行（>25pt
                    # 时 below_adj 漏检，方向被页眉抢走 → caption-only 假裁剪）
                    if r.y0 - 60 <= br.y1 <= r.y0 + 2:
                        above_adj = True
                    if r.y1 - 2 <= br.y0 <= r.y1 + 60:
                        below_adj = True
                # 方向选择：两侧都紧贴时双向采集，按得分取优（kimi-k2-5 tab04
                # 页眉 sc=1 触发 above_adj 抢方向 → caption-only；deepseekmath
                # 堆叠表格 above=7>below=3 仍正确归属）。
                # 先比单块最高分：mooncake tab03 上方 2 散文 sc1 与下方
                # 表头+sc2 数据行同分，同分取上即误选 —— 有 sc2 的一侧更像
                # 真表。同分再比总和，仍同取上（caption-below 布局）。
                # 采集尽头紧贴 fig caption ⇒ 该侧冲进了图内容（specextend
                # tab03 下方 Figure 6 柱状图标签 sc2 被当表体），改取对侧。
                region = []
                if above_adj and below_adj:
                    ra = collect_table_region(blocks, r, x0, x1, -1, page.rect.height, zones, t_zones, prose_w)
                    rb = collect_table_region(blocks, r, x0, x1, +1, page.rect.height, zones, t_zones, prose_w)
                    def _sc(p):
                        return [2 if b["type"] == 1 else block_table_score(b)
                                for _, b in p]
                    sa, sb = sum(_sc(ra)), sum(_sc(rb))
                    ma, mb = max(_sc(ra), default=0), max(_sc(rb), default=0)
                    def _hits_fig_cap(picked, direction):
                        if not picked:
                            return False
                        edge = (min(g.y0 for g, _ in picked) if direction == -1
                                else max(g.y1 for g, _ in picked))
                        for _k, _n, _t, c, _l in caps:
                            if _k != "fig" or c is r:
                                continue
                            if direction == -1 and c.y1 <= edge + 2 \
                                    and c.y1 > edge - 40:
                                return True
                            if direction == +1 and c.y0 >= edge - 2 \
                                    and c.y0 < edge + 40:
                                return True
                        return False
                    if _hits_fig_cap(ra, -1) and rb:
                        region = rb
                    elif _hits_fig_cap(rb, +1) and ra:
                        region = ra
                    elif ma != mb:
                        region = ra if ma > mb else rb
                    else:
                        region = ra if sa >= sb else rb
                elif above_adj:
                    region = collect_table_region(blocks, r, x0, x1, -1, page.rect.height, zones, t_zones, prose_w)
                elif below_adj:
                    region = collect_table_region(blocks, r, x0, x1, +1, page.rect.height, zones, t_zones, prose_w)
                if not region:
                    region = collect_table_region(blocks, r, x0, x1, +1, page.rect.height, zones, t_zones, prose_w)
                    if not region:
                        region = collect_table_region(blocks, r, x0, x1, -1, page.rect.height, zones, t_zones, prose_w)
                # 表格有效性：区域里必须真有表格状内容（多单元格行/数字行/嵌入表图），
                # 否则这块只是 caption+散文，宁可不裁也不产出假表格图（2026-08-24）
                def valid_table(picked):
                    if not picked:
                        return False
                    scores = [2 if b["type"] == 1 else block_table_score(b)
                              for _, b in picked]
                    # 多列组合表头全是 sc0 单元格（a-survey tab10：6 个表头
                    # 单元格 + 4 行 sc2 数据行；specextend tab07：6 个表头
                    # 单元格 + 1 行 sc2 数据行），过半校验会误杀真表 ——
                    # 有 sc=2 强数据行且采到表头结构（≥4 块）同样是硬证据；
                    # 纯散文采集全是 sc1 行，过不了这条（防假表的初衷不变）
                    return sum(1 for s in scores if s >= 1) >= max(1, len(picked) // 2) \
                        or (sum(1 for s in scores if s >= 2) >= 1 and len(picked) >= 4)
                if not valid_table(region) and r.y0 < 100 and pno > 0:
                    # caption 顶页首、表体在上一页页尾（caption-below 被分页：
                    # scalable-moe tab19 "summarizes the notation" 推到下页顶）
                    pb = doc[pno - 1].get_text("dict")["blocks"]
                    fake_cap = fitz.Rect(x0, doc[pno-1].rect.height + 5, x1,
                                         doc[pno-1].rect.height + 10)
                    region2 = collect_table_region(pb, fake_cap, x0, x1, -1,
                                                   doc[pno - 1].rect.height, prose_w=prose_w)
                    if valid_table(region2):
                        seen_tab.add(num)
                        u2 = region2[0][0]
                        for g, _b in region2[1:]:
                            u2 |= g
                        u2.x0 = max(0, u2.x0 - 4); u2.x1 = min(doc[pno-1].rect.x1, u2.x1 + 4)
                        u2.y0 = max(0, u2.y0 - 3); u2.y1 = min(doc[pno-1].rect.y1, u2.y1 + 4)
                        out = CROPS / f"{slug}-tab{num:02d}.png"
                        item = {"num": num, "page": pno,
                                "caption": re.sub(r'\s+', ' ', tail).strip()[:300],
                                "path": f"assets/crops/{out.name}"}
                        if out.exists():
                            res["tables"].append(item); continue
                        pix = crop_pix(doc[pno - 1], u2, dpi, max_h=doc[pno-1].rect.height - 50)
                        if pix:
                            pix.save(str(out))
                            res["tables"].append(item)
                        continue
                # caption 下方整页无块（float 把表体整体推到下一页：
                # conditional-memory tab05）也触发下一页采集
                no_blocks_below = not any(
                    b2["type"] == 0 and block_text(b2)
                    and fitz.Rect(b2["bbox"]).y0 > r.y1 + 2
                    and not is_folio(fitz.Rect(b2["bbox"]), block_text(b2),
                                     page.rect.height)
                    for b2 in blocks)
                if not valid_table(region) and pno + 1 < doc.page_count \
                        and (r.y1 > page.rect.height - 120 or no_blocks_below):
                    # caption 沉页底、表体在下一页页首（综述类多页表：
                    # a-survey tab07/11/15/16 五例）——从下一页页首采集，
                    # 裁下一页的表体区（caption 文本留在 visuals.json/MD）
                    nb = doc[pno + 1].get_text("dict")["blocks"]
                    fake_cap = fitz.Rect(x0, -10, x1, -5)
                    region2 = collect_table_region(nb, fake_cap, x0, x1, +1, doc[pno + 1].rect.height, prose_w=prose_w)
                    if valid_table(region2):
                        seen_tab.add(num)
                        u2 = region2[0][0]
                        for g, _b in region2[1:]:
                            u2 |= g
                        u2.x0 = max(0, u2.x0 - 4); u2.x1 = min(doc[pno+1].rect.x1, u2.x1 + 4)
                        u2.y0 = max(0, u2.y0 - 4); u2.y1 = min(doc[pno+1].rect.y1, u2.y1 + 3)
                        out = CROPS / f"{slug}-tab{num:02d}.png"
                        item = {"num": num, "page": pno + 2,
                                "caption": re.sub(r'\s+', ' ', tail).strip()[:300],
                                "path": f"assets/crops/{out.name}"}
                        if out.exists():
                            res["tables"].append(item); continue
                        pix = crop_pix(doc[pno + 1], u2, dpi, max_h=doc[pno+1].rect.height - 50)
                        if pix:
                            pix.save(str(out))
                            res["tables"].append(item)
                        continue
                if not valid_table(region):
                    continue
                seen_tab.add(num)
                u = fitz.Rect(r.x0, r.y0, r.x1, r.y1)  # include caption line
                for g, _b in region:
                    u |= g
                u.x0 = max(0, u.x0 - 4); u.x1 = min(page.rect.x1, u.x1 + 4)
                u.y0 = max(0, u.y0 - 3); u.y1 = min(page.rect.y1, u.y1 + 3)
                out = CROPS / f"{slug}-tab{num:02d}.png"
                item = {"num": num, "page": pno + 1,
                        "caption": re.sub(r'\s+', ' ', tail).strip()[:300],
                        "path": f"assets/crops/{out.name}"}
                if out.exists():
                    res["tables"].append(item); continue
                pix = crop_pix(page, u, dpi, max_h=page.rect.height - 50)
                if pix:
                    pix.save(str(out))
                    res["tables"].append(item)
        # formula-as-image only for papers without latex source (line-level detection)
        if slug not in latex_slugs:
            for region, txt in formula_regions(page):
                key = txt[:60]
                if key in seen_eq:
                    continue
                seen_eq.add(key)
                region.x0 = max(0, region.x0 - 8); region.x1 = min(page.rect.x1, region.x1 + 8)
                region.y0 = max(0, region.y0 - 5); region.y1 = min(page.rect.y1, region.y1 + 5)
                out = CROPS / f"{slug}-eq{len(res['formulas']) + 1:02d}.png"
                item = {"page": pno + 1, "text": txt[:180],
                        "path": f"assets/crops/{out.name}"}
                if out.exists():
                    res["formulas"].append(item); continue
                pix = crop_pix(page, region, dpi)
                if pix:
                    pix.save(str(out))
                    res["formulas"].append(item)
    doc.close()
    res["figures"].sort(key=lambda x: x["num"])
    res["tables"].sort(key=lambda x: x["num"])
    return res


def main():
    args = sys.argv[1:]
    only = None
    dpi = 200
    if "--only" in args:
        only = set(args[args.index("--only") + 1].split(","))
    if "--dpi" in args:
        dpi = int(args[args.index("--dpi") + 1])
    CROPS.mkdir(parents=True, exist_ok=True)
    fj = OUT / "formulas.json"
    latex = json.loads(fj.read_text()) if fj.exists() else {}
    latex_slugs = {k for k, v in latex.items() if v}
    vis_path = OUT / "visuals.json"
    vis = json.loads(vis_path.read_text()) if vis_path.exists() else {}
    slugs = paper_slugs()
    if only:
        slugs = [s for s in slugs if s in only]
    print(f"papers: {len(slugs)} | latex-covered: {len(latex_slugs)} (formula-img only for the rest)")
    nf = nt = ne = 0
    for i, slug in enumerate(slugs, 1):
        try:
            r = process_paper(slug, dpi, latex_slugs)
            if r is None:
                continue
            vis[slug] = r
            nf += len(r["figures"]); nt += len(r["tables"]); ne += len(r["formulas"])
            print(f"  [{i:2}] {slug[:52]:52} fig={len(r['figures']):2} tab={len(r['tables']):2} eq={len(r['formulas']):2}")
        except Exception as e:
            print(f"  [ERR] {slug}: {e}")
    # ar5iv 产物 overlay：坏字体/坏结构 PDF 的裁剪由 ar5iv_replace.py 从 HTML 原图
    # 生成并登记在 ar5iv_crops.json，这里强制覆盖回 visuals.json，防止全量重裁
    # 用乱码 PDF 裁剪覆盖或丢项（2026-08-24）
    reg_path = OUT / "ar5iv_crops.json"
    if reg_path.exists():
        reg = json.loads(reg_path.read_text())
        n_overlay = 0
        for path, e in reg.items():
            if not (OUT / path).exists():
                continue
            key = {"fig": "figures", "tab": "tables", "eq": "formulas"}[e["kind"]]
            lst = vis.setdefault(e["slug"], {}).setdefault(key, [])
            item = {k: e[k] for k in ("num", "page", "caption", "path")}
            ex = next((x for x in lst if x["num"] == e["num"]), None)
            if ex:
                lst[lst.index(ex)] = item
            else:
                lst.append(item)
            lst.sort(key=lambda x: x["num"])
            n_overlay += 1
        if n_overlay:
            print(f"  ar5iv overlay: {n_overlay} crops protected")
    vis_path.write_text(json.dumps(vis, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nDONE. crops: fig={nf} tab={nt} eq={ne} -> {vis_path}")


if __name__ == "__main__":
    main()
