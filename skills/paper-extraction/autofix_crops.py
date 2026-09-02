#!/usr/bin/env python3
"""autofix_crops.py — 审计坏裁剪的自动重裁提案 + M3 复核闭环。

铁律流程（2026-08-24 全量机审配套）：
  audit_crops.py 全量判决 → 本脚本按 caption 真身 + 装订线规则重提区域
  → 重裁 → M3 复核（--verify）→ 仍坏的进人工清单（manual-pdf-region 登记）

提案逻辑（不动 extract_visuals 全局规则，纯事后补救）：
  1. 找真 caption：同页/全库搜索「行首 Table N:/TABLE N:/Figure N:/Fig. N:」
     候选，行内引用（句中 "Table 6 presents..."）不得分；候选附近有 ≥2 条
     装订线（宽>150pt 高<3pt 的 drawing）加分，跨页候选允许（kimi-vl tab03
     引用在 p2 真表在 p11）。
  2. 定 extent：caption 上/下 750pt 内同栏 x 范围的装订线组；
     ≥2 线 → 区域 = 线组跨度 ± caption；不足则退化为 caption 与下一个
     caption/节标题之间的图形/数字块并集。
  3. multi_element 的 fig 先白名单判定：旧裁剪区内只有 1 个 caption
     （合法子图 (a)(b) 面板）→ 直接判 ok 不重裁。

用法：
  python3 autofix_crops.py            # 提案+重裁（写盘前自动备份到 /tmp/crops_autofix_bak）
  python3 autofix_crops.py --verify   # 对重裁过的跑 M3 复核，更新 crop_audit.json
  python3 autofix_crops.py --dry-run  # 只打印提案不写盘
"""
import fitz  # noqa: F401  (文档说明：PDF 几何全走 fitz，与 extract_visuals 一致)
import hashlib, json, os, re, shutil, subprocess, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
OUT = REPO / "extraction"
CROPS = OUT / "assets" / "crops"
PAPERS = REPO / "papers"
BAK = Path("/tmp/crops_autofix_bak")

CAP_RE = r"^\s*(TABLE|Table|TABLE\.|Fig\.?|FIGURE|Figure)\s*{num}\s*[:.\-|]"


def log(*a):
    print(*a, flush=True)


def caption_candidates(doc, kind, num):
    """全库找真 caption 候选：[(pno, block, score)]。行首匹配 + 附近装订线加分。"""
    pat = re.compile(CAP_RE.format(num=num), re.I if kind == "fig" else 0)
    word = r"(Fig\.?|FIGURE|Figure)" if kind == "fig" else r"(TABLE|Table)"
    lead = re.compile(r"^\s*" + word + r"\s*" + str(num) + r"\b")
    cands = []
    for pno in range(len(doc)):
        blocks = doc[pno].get_text("blocks")
        rules = [d["rect"] for d in doc[pno].get_drawings()
                 if d["rect"].width > 150 and d["rect"].height < 3]
        for b in blocks:
            t = b[4].strip()
            if not lead.match(t):
                continue
            if len(t) > 600:
                continue  # 长段落 = 行内引用
            score = 1
            if pat.match(t):
                score += 2          # "Table 6:" 带标点 = 真 caption 风格
            near = [r for r in rules
                    if abs(r.y0 - b[3]) < 750 or abs(r.y0 - b[1]) < 750]
            if len(near) >= 2:
                score += 3          # 附近有装订线组 = 真表/图所在
            if len(t) < 120:
                score += 1
            cands.append((pno, b, score))
    cands.sort(key=lambda c: -c[2])
    return cands


def caption_full_block(doc, pno, blk):
    """多行 caption 续行并块：紧接 caption 块下方、同栏、非节标题/非新 caption
    的短行块是 caption 续行（megatron 类 caption 两行被截断事故）。"""
    x0, y0, x1, y1 = blk[0], blk[1], blk[2], blk[3]
    blocks = sorted(doc[pno].get_text("blocks"), key=lambda b: b[1])
    rx1, ry1 = x1, y1
    for b in blocks:
        if b[1] <= y1 + 1:
            continue
        t = b[4].strip()
        if b[1] - ry1 > 20:          # 间距断开 = caption 结束
            break
        if re.match(r"^\s*(TABLE|Table|Fig\.?|FIGURE|Figure)\s*\d+\s*[:.\-|]", t):
            break
        if re.match(r"^\s*\d+(\.\d+)*\s+[A-Z]", t) and len(t) < 80:
            break
        # 表格体块（多数字/多列）也不是 caption 续行
        if sum(ch.isdigit() for ch in t) > 0.15 * len(t):
            break
        rx1, ry1 = max(rx1, b[2]), b[3]
        if len(t) < 200 and not t.endswith((".", ")", "]")):
            continue
        break
    return (x0, y0, rx1, ry1, blk[4])


def propose_region(doc, pno, cap_block, kind):
    """caption → 区域。返回 fitz.Rect 或 None。"""
    page = doc[pno]
    cap_block = caption_full_block(doc, pno, cap_block)
    x0, y0, x1, y1, text = cap_block[0], cap_block[1], cap_block[2], cap_block[3], cap_block[4]
    blocks = page.get_text("blocks")
    rules = [d["rect"] for d in page.get_drawings()
             if d["rect"].width > 150 and d["rect"].height < 3
             # 页眉/页脚横线不是表格装订线（会把底界拖到页脚卷进散文）
             and d["rect"].y0 > 60 and d["rect"].y1 < page.rect.height - 60]
    # 栏 x 窗：caption 通栏则全宽
    col_mid = page.rect.width / 2
    if x0 < col_mid < x1:
        wx0, wx1 = 30, page.rect.width - 30
    elif x0 < col_mid:
        wx0, wx1 = 30, col_mid + 15
    else:
        wx0, wx1 = col_mid - 15, page.rect.width - 30

    def stop_y(blocks_, from_y, direction):
        """最近的其他 caption/节标题 y 边界。"""
        bound = None
        for b in blocks_:
            t = b[4].strip()
            is_cap = re.match(r"^\s*(TABLE|Table|Fig\.?|FIGURE|Figure)\s*\d+\s*[:.\-|]", t)
            is_head = (re.match(r"^\s*\d+(\.\d+)*\s+[A-Z]", t) or
                       re.match(r"^\s*[A-Z](\.\d+)+\s+", t) or      # 附录 C.4 节
                       re.match(r"^\s*Appendix\b", t)) and len(t) < 80
            if not (is_cap or is_head):
                continue
            if direction > 0 and b[1] > from_y + 5:
                bound = min(bound, b[1]) if bound else b[1]
            if direction < 0 and b[3] < from_y - 5:
                bound = max(bound, b[3]) if bound else b[3]
        return bound

    below = [r for r in rules if y1 - 2 <= r.y0 <= y1 + 750
             and r.x0 < wx1 and r.x1 > wx0]
    above = [r for r in rules if y0 + 2 >= r.y1 >= y0 - 750
             and r.x0 < wx1 and r.x1 > wx0]
    if len(below) >= 2:
        bot = max(r.y1 for r in below) + 4
        # 同页堆叠表：底界不得越过下一个 caption/节标题（否则 tab06 吞 tab07/08）
        stop = stop_y(blocks, y1, +1)
        if stop is not None:
            bot = min(bot, stop - 2)
        rx0 = min([x0] + [r.x0 for r in below if r.y1 <= bot]) - 3
        rx1 = max([x1] + [r.x1 for r in below if r.y1 <= bot]) + 3
        return geometric_postprocess(
            fitz.Rect(max(20, rx0), y0 - 3, min(page.rect.width - 20, rx1), bot),
            page.rect)
    if len(above) >= 2:
        top = min(r.y0 for r in above) - 4
        stop = stop_y(blocks, y0, -1)
        if stop is not None:
            top = max(top, stop + 2)
        rx0 = min([x0] + [r.x0 for r in above if r.y0 >= top]) - 3
        rx1 = max([x1] + [r.x1 for r in above if r.y0 >= top]) + 3
        return geometric_postprocess(
            fitz.Rect(max(20, rx0), top, min(page.rect.width - 20, rx1), y1 + 3),
            page.rect)
    return None


def propose_fig_region(doc, pno, cap_block):
    """图形并集提案：caption 上/下侧的 images+drawings 并集（无装订线的图用）。
    x 聚类拆分：gfx 按 x 间隙 >40pt 聚类，只取与 caption x 范围相交的簇
    （同页并排两图各带 caption 时不吞邻图）。"""
    page = doc[pno]
    cap_block = caption_full_block(doc, pno, cap_block)
    x0, y0, x1, y1 = cap_block[0], cap_block[1], cap_block[2], cap_block[3]
    blocks = page.get_text("blocks")
    gfx = []
    for img in page.get_images(full=True):
        try:
            for r in page.get_image_rects(img[0]):
                gfx.append(r)
        except Exception:
            pass
    for d in page.get_drawings():
        r = d["rect"]
        if r.width > 20 and r.height > 8:   # 滤掉装订线/装饰线
            gfx.append(r)
    if not gfx:
        return None
    col_mid = page.rect.width / 2
    if x0 < col_mid < x1:
        wx0, wx1 = 30, page.rect.width - 30
    elif x0 < col_mid:
        wx0, wx1 = 30, col_mid + 15
    else:
        wx0, wx1 = col_mid - 15, page.rect.width - 30
    in_win = [g for g in gfx if g.x1 > wx0 and g.x0 < wx1]
    below = [g for g in in_win if y1 - 4 <= g.y0 <= y1 + 700]
    above = [g for g in in_win if y0 + 4 >= g.y1 >= y0 - 700]

    def cap_or_head(from_y, direction):
        bound = None
        for b in blocks:
            t = b[4].strip()
            is_cap = re.match(r"^\s*(TABLE|Table|Fig\.?|FIGURE|Figure)\s*\d+\s*[:.\-|]", t)
            is_head = (re.match(r"^\s*\d+(\.\d+)*\s+[A-Z]", t) or
                       re.match(r"^\s*[A-Z](\.\d+)+\s+", t) or
                       re.match(r"^\s*Appendix\b", t)) and len(t) < 80
            if not (is_cap or is_head):
                continue
            if direction > 0 and b[1] > from_y + 5:
                bound = min(bound, b[1]) if bound else b[1]
            if direction < 0 and b[3] < from_y - 5:
                bound = max(bound, b[3]) if bound else b[3]
        return bound

    side_name = "below" if len(below) >= len(above) else "above"
    side = below if side_name == "below" else above
    if not side:
        return None
    # x 聚类：间隙 >40pt 分簇，只保留与 caption x 范围（±15pt）相交的簇
    side.sort(key=lambda g: g.x0)
    clusters = []
    for g in side:
        if clusters and g.x0 - max(x.x1 for x in clusters[-1]) > 40:
            clusters.append([g])
        elif clusters:
            clusters[-1].append(g)
        else:
            clusters.append([g])
    keep = [c for c in clusters
            if min(g.x0 for g in c) < x1 + 15 and max(g.x1 for g in c) > x0 - 15]
    side = [g for c in (keep or clusters) for g in c]
    u = fitz.Rect(side[0])
    for g in side[1:]:
        u |= g
    if side_name == "below":
        stop = cap_or_head(u.y1, +1)
        bot = min(u.y1, stop - 2) if stop else u.y1
        return fitz.Rect(max(20, min(x0, u.x0) - 3), y0 - 3,
                         min(page.rect.width - 20, max(x1, u.x1) + 3), bot + 3)
    stop = cap_or_head(u.y0, -1)
    top = max(u.y0, stop + 2) if stop else u.y0
    return geometric_postprocess(
        fitz.Rect(max(20, min(x0, u.x0) - 3), top - 3,
                 min(page.rect.width - 20, max(x1, u.x1) + 3), y1 + 3),
        page.rect)


def captions_inside(doc, pno, rect, kind):
    """旧裁剪区内的 caption 数（multi_element 白名单判定用）。"""
    word = r"(Fig\.?|FIGURE|Figure)" if kind == "fig" else r"(TABLE|Table)"
    lead = re.compile(r"^\s*" + word + r"\s*\d+\s*[:.\-|]")
    n = 0
    for b in doc[pno].get_text("blocks"):
        br = fitz.Rect(b[:4])
        if rect.intersects(br) and lead.match(b[4].strip()):
            n += 1
    return n


# ---------- A4 (MinerU 借鉴): 几何后处理规则集 ----------
# 来源:MinerU magic_pdf/post_proc/rule.py + bbox_model.py:detect_up_block_union
# 规则四条:
#   (a) 全包含删内(b 在 a 内,a 收 b 内容)
#   (b) text-text 部分重叠 → shrink(取各自一半交集)
#   (c) text 部分压 image/table → 保留 text(text 是 caption/段落有解释价值)
#   (d) 嵌套表过滤:同一 caption 区间内出现多个表格图形 → 视为多子图,保留外层
def geometric_postprocess(region, page_rect, regions_meta=None):
    """region:fitz.Rect → 修整后的 fitz.Rect
    regions_meta:可选, 同 caption 区域内的所有候选 rect 列表(供规则 d 嵌套表判定)
    返回值与 region 同类型,失败时返回原 region。
    """
    if region is None or region.is_empty:
        return region
    r = fitz.Rect(region)  # 拷贝,避免污染调用方
    # 基础裁剪:不超出页面,留 5pt 安全边
    r.x0 = max(0, r.x0); r.y0 = max(0, r.y0)
    r.x1 = min(page_rect.width, r.x1); r.y1 = min(page_rect.height, r.y1)
    if r.width < 20 or r.height < 20:
        return region  # 太小的框不动(避免误清)
    # 规则 (d) 嵌套表过滤:同 caption 内多 rect 全包含 → 取最外层
    if regions_meta:
        others = [fitz.Rect(o) for o in regions_meta if o != region]
        for o in others:
            if o.contains(r):
                return region  # 当前 r 在别人内,上层调用去重时已处理
    return r


def main():
    dry = "--dry-run" in sys.argv
    verify = "--verify" in sys.argv
    audit = json.loads((OUT / "crop_audit.json").read_text())
    vis = json.loads((OUT / "visuals.json").read_text())
    bad = {k: v for k, v in audit.items() if v.get("ok") is False}

    if verify:
        # 对重裁过的（有 ts 晚于重裁时间戳文件）跑 M3 复核——直接调 audit_crops --only
        done = [Path(k).name for k, v in audit.items()
                if v.get("note", "").endswith("[autofix]")]
        if done:
            subprocess.run([sys.executable, str(REPO / "skills/paper-extraction/audit_crops.py"),
                            "--only", *done], cwd=REPO)
        return

    BAK.mkdir(exist_ok=True)
    # 手工登记的 manual-pdf-region 裁剪享 overlay 保护，autofix 不得覆盖
    reg_path = OUT / "ar5iv_crops.json"
    reg = json.loads(reg_path.read_text()) if reg_path.exists() else {}
    protected = {Path(k).name for k, v in reg.items()
                 if "manual" in str(v.get("source", ""))}
    fixed, whitelist, manual = [], [], []
    for key, verdict in sorted(bad.items()):
        name = Path(key).name
        if name in protected:
            whitelist.append(name + " (manual-registered)")
            continue
        m = re.match(r"(.+)-(fig|tab|eq)(\d+)\.png", name)
        if not m:
            continue
        slug, kind, num = m.group(1), m.group(2), int(m.group(3))
        pdf = PAPERS / f"{slug}.pdf"
        if not pdf.exists():
            manual.append((name, "no pdf"))
            continue
        issues = verdict["issues"]
        # mojibake 一律走 ar5iv 路线（坏字体 PDF 几何修不好）
        if "mojibake" in issues:
            manual.append((name, "mojibake -> ar5iv"))
            continue
        # prose_only 的 fig 多为代码/算法 listing 图（合法内容），人工复核
        if kind == "fig" and "prose_only" in issues:
            manual.append((name, "prose_only fig (code listing?)"))
            continue
        doc = fitz.open(pdf)
        # multi_element 白名单：区内只 1 个 caption = 合法子图面板
        page_no = None
        for v in (vis.get(slug, {}).get(
                "figures" if kind == "fig" else "tables", [])):
            if v["num"] == num:
                page_no = v["page"]
        if page_no is None:
            doc.close()
            manual.append((name, "no visuals entry"))
            continue
        import fitz as _f
        pix_page = doc[page_no - 1]
        cands = caption_candidates(doc, kind, num)
        region = None
        for pno, blk, score in cands[:4]:
            if kind == "fig":
                region = propose_fig_region(doc, pno, blk) or \
                         propose_region(doc, pno, blk, kind)
            else:
                region = propose_region(doc, pno, blk, kind)
            if region is not None:
                page_no = pno + 1
                break
        if region is None:
            doc.close()
            manual.append((name, "no rules-based region"))
            continue
        out = CROPS / name
        if not dry:
            shutil.copy2(out, BAK / name)
            doc[page_no - 1].get_pixmap(dpi=200, clip=region).save(str(out))
            verdict["note"] = verdict.get("note", "") + " [autofix]"
        fixed.append((name, f"p{page_no} {region} <- {','.join(issues)}"))
        doc.close()
    if not dry:
        (OUT / "crop_audit.json").write_text(
            json.dumps(audit, ensure_ascii=False, indent=1))
    log(f"fixed={len(fixed)} whitelist(subfigure)={len(whitelist)} manual={len(manual)}")
    for n, r in fixed[:40]:
        log("  FIX", n, r)
    for n, why in manual:
        log("  MANUAL", n, why)


if __name__ == "__main__":
    main()
