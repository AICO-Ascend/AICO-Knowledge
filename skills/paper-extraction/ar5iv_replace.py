#!/usr/bin/env python3
"""ar5iv_replace.py — 坏字体/坏结构 PDF 的裁剪修复：从 ar5iv HTML 拿原始图/表替换。

背景：少数 arXiv PDF 字体子集化在源头就坏了（MuPDF/pdfium 渲染都乱码，
pikepdf 修复无效），或 PDF 结构坏到 drawings 解析不出来。这类论文的图/表
裁剪只能从 ar5iv HTML 的原图（SVG/PNG）和原始 <table> 重新生成。

用法：
  python3 ar5iv_replace.py <arxiv_id> fig 2 7 8     # 替换/补齐 Figure 2,7,8
  python3 ar5iv_replace.py <arxiv_id> tab 4 5       # 替换/补齐 Table 4,5
  python3 ar5iv_replace.py <arxiv_id> fig 2 --slug <slug>  # 显式指定 slug

行为：
  - 图：ar5iv <figure> 里的 <img>（SVG 经 cairosvg 转 PNG，PNG/JPG 直接下载）
  - 表：ar5iv ltx_table 的 <table> 用 matplotlib 渲染成 PNG（内容优先）
  - 写入 extraction/assets/crops/<slug>-figNN.png / -tabNN.png
  - 同步 visuals.json（保留原 entry 的 page/caption；新 entry page=0）
  - 使这些裁剪在 minimax_captions.json 里的旧解读失效（描述的是乱码版），
    交给后续 M3 重解读
"""
import json, re, sys, urllib.request
from html.parser import HTMLParser
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
OUT = REPO / "extraction"
CROPS = OUT / "assets" / "crops"
PAPERS = REPO / "papers"

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as _fm

# CJK 字体（仓外 ~/.config/aico/fonts/，首次由使用方下载；deepseek-r1 附录
# 中文 prompt 表格必须有 CJK 才能渲染，否则全豆腐块）
_CJK = Path.home() / ".config" / "aico" / "fonts" / "NotoSansSC.ttf"
if _CJK.exists():
    _fm.fontManager.addfont(str(_CJK))
    plt.rcParams["font.family"] = ["DejaVu Sans", "Noto Sans SC"]


# ---------- 极简 DOM（stdlib，避免 bs4 依赖） ----------
class Node:
    def __init__(self, tag, attrs, parent=None):
        self.tag, self.attrs, self.parent = tag, dict(attrs), parent
        self.flow = []          # str 与 Node 按文档顺序混合

    @property
    def children(self):
        return [x for x in self.flow if isinstance(x, Node)]

    def iter(self, tag=None):
        for c in self.children:
            if tag is None or c.tag == tag:
                yield c
            yield from c.iter(tag)

    def all_text(self):
        return "".join(x if isinstance(x, str) else x.all_text() for x in self.flow)

    def to_html(self):
        if self.tag == "root":
            return "".join(x if isinstance(x, str) else x.to_html() for x in self.flow)
        attrs = "".join(f' {k}="{v}"' if v is not None else f" {k}"
                        for k, v in self.attrs.items())
        inner = "".join(x if isinstance(x, str) else x.to_html() for x in self.flow)
        if self.tag in DOM.VOID:
            return f"<{self.tag}{attrs}/>"
        return f"<{self.tag}{attrs}>{inner}</{self.tag}>"


class DOM(HTMLParser):
    VOID = {"img", "br", "hr", "meta", "link", "input", "col", "wbr"}
    # <math> 里的 <annotation>\times</annotation> 是 LaTeX 源码副本，
    # 与渲染字形并存会导致 "×\times" 双重文本 —— 整棵子树丢弃
    SKIP = {"annotation", "annotation-xml"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("root", {})
        self.cur = self.root
        self._skip_depth = 0

    def handle_starttag(self, tag, attrs):
        if self._skip_depth or tag in self.SKIP:
            self._skip_depth += 1
            return
        n = Node(tag, attrs, self.cur)
        self.cur.flow.append(n)
        if tag not in self.VOID:
            self.cur = n

    def handle_endtag(self, tag):
        if self._skip_depth:
            self._skip_depth -= 1
            return
        n = self.cur
        while n is not self.root and n.tag != tag:
            n = n.parent
        if n is not self.root:
            self.cur = n.parent

    def handle_data(self, data):
        if not self._skip_depth:
            self.cur.flow.append(data)


def fetch(url, binary=False):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 aico-kb"})
    last = None
    for attempt in range(3):          # arxiv 偶发假 404，重试
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                data = r.read()
            return data if binary else data.decode("utf-8", "ignore")
        except Exception as e:
            last = e
            import time
            time.sleep(2 * (attempt + 1))
    raise last


def _roman(s):
    vals = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100}
    total = 0
    for a, b in zip(s, s[1:] + " "):
        total += -vals[a] if vals.get(b, 0) > vals[a] else vals[a]
    return total


def find_figures(dom, kind, wanted):
    """-> {num: node} for <figure> blocks whose figcaption matches kind+num.
    兼容 "Figure 2" / "Fig. 1:" / "TABLE IV:"（罗马数字转阿拉伯）。"""
    word = r"(?:Figure|Fig\.?)" if kind == "fig" else r"(?:Table|TABLE)"
    pat = re.compile(rf"^\s*{word}\s*([0-9]+|[IVXLC]+)\b", re.I)
    found = {}
    for fig in dom.root.iter("figure"):
        cap = None
        for fc in fig.iter("figcaption"):
            cap = fc
            break
        if cap is None:
            continue
        m = pat.match(re.sub(r"\s+", " ", cap.all_text()))
        if not m:
            continue
        g = m.group(1)
        num = _roman(g.upper()) if g[0] in "IVXLCivxlc" else int(g)
        if num in wanted:
            found[num] = fig
    return found


def _resolve_ltx_css_vars(svg_text):
    """LaTeXML SVG 用 CSS 变量 --ltx-fill-color/--ltx-stroke-color 表达颜色，
    cairosvg 不支持 var()，无 fill 属性的元素继承根节点黑色 → 整图黑底
    （kimi-linear fig2 事故）。把变量展开成元素自身的 fill/stroke。"""
    import re
    def _expand(m):
        tag, style = m.group(1), m.group(2)
        fill = re.search(r'--ltx-fill-color:\s*([^;]+)', style)
        stroke = re.search(r'--ltx-stroke-color:\s*([^;]+)', style)
        extra = ""
        if fill and 'fill:' not in style and ' fill=' not in tag:
            extra += f";fill:{fill.group(1)}"
        if stroke and 'stroke:' not in style and ' stroke=' not in tag:
            extra += f";stroke:{stroke.group(1)}"
        if extra:
            return f'{tag}style="{style}{extra}"'
        return m.group(0)
    return re.sub(r'(<(?:g|path|rect|text|use)[^>]*?)style="([^"]*)"', _expand, svg_text)


def save_figure(fig_node, base_url, out_path):
    from urllib.parse import urljoin
    img = next(fig_node.iter("img"), None)
    src = None
    if img is not None:
        src = img.attrs.get("src", "")
    if not src:
        # <object type="image/svg+xml" data="....svg">（deepseek-r1 v2 HTML）
        obj = next(fig_node.iter("object"), None)
        if obj is not None:
            src = obj.attrs.get("data", "")
    if not src:
        # 内联 <svg>（dynamic-lcm fig2）：序列化子树交给 cairosvg
        svg = next(fig_node.iter("svg"), None)
        if svg is None:
            return False, "no <img>/<object>/<svg> in figure"
        import cairosvg
        cairosvg.svg2png(bytestring=_resolve_ltx_css_vars(
            svg.to_html()).encode("utf-8"),
                         write_to=str(out_path), scale=2.0)
        return True, "inline svg via cairosvg"
    # ar5iv 图片在 <id>/ 目录下（base+'/'）；arxiv 原生 HTML 的 src 自带版本目录
    # （"2512.24617v2/x.png"，相对 /html/）。两种候选按序尝试。
    if src.startswith("http"):
        candidates = [src]
    else:
        candidates = [urljoin(base_url.rstrip("/") + "/", src),
                      urljoin(base_url, src)]
    data, url = None, candidates[0]
    for cand in candidates:
        try:
            data = fetch(cand, binary=True)
            url = cand
            break
        except Exception:
            continue
    if data is None:
        return False, f"all URL candidates 404 for {src[:60]}"
    if src.lower().endswith(".svg"):
        import cairosvg
        cairosvg.svg2png(bytestring=_resolve_ltx_css_vars(
            data.decode("utf-8", "ignore")).encode("utf-8"),
                         write_to=str(out_path), scale=2.0)
    else:
        out_path.write_bytes(data)
    return True, f"{len(data)}B from {url.rsplit('/',1)[-1]}"


def table_grid(tab_node):
    """<table> -> rows of cell texts (colspan 简单展开)."""
    rows = []
    for tr in tab_node.iter("tr"):
        row = []
        for cell in list(tr.iter("td")) + list(tr.iter("th")):
            txt = re.sub(r"\s+", " ", cell.all_text()).strip()
            span = int(cell.attrs.get("colspan", "1") or "1")
            row.extend([txt] + [""] * (span - 1))
        if row:
            rows.append(row)
    return rows


def render_table(tab_node, caption, out_path):
    import textwrap
    rows = table_grid(tab_node)
    if not rows:
        return False, "no rows"
    ncol = max(len(r) for r in rows)
    rows = [r + [""] * (ncol - len(r)) for r in rows]
    wrap = lambda s, w: "\n".join(textwrap.wrap(s, w) or [""])
    cw = [min(42, max(8, max((len(r[c]) for r in rows), default=8))) for c in range(ncol)]
    wrapped = [[wrap(c, cw[i]) for i, c in enumerate(r)] for r in rows]
    rh = [max(str(c).count("\n") + 1 for c in r) for r in wrapped]
    W = sum(cw) * 0.105 + 0.8
    H = sum(rh) * 0.24 + 0.9
    fig = plt.figure(figsize=(min(W, 22), min(H, 30)), dpi=150)
    # 图内不画 caption —— MD 里 visuals.json 的 caption + M3 解读紧邻展示；
    # 图内长 caption 折行后必然压首行（2026-08-24 两轮实测）
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis("off")
    tbl = ax.table(cellText=wrapped, colWidths=[c / sum(cw) for c in cw],
                   cellLoc="left", loc="center")
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(7.5)
    for (r, c), cell in tbl.get_celld().items():
        cell.set_edgecolor("#888888")
        cell.set_linewidth(0.4)
        if r == 0:
            cell.set_facecolor("#e8e8e8")
        cell.set_height(rh[r - 1] * 0.24 / H * 1.6)
    fig.savefig(str(out_path), bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return True, f"{len(rows)}x{ncol} via matplotlib"


def slug_for(aid):
    import subprocess
    out = subprocess.run(["python3", "-c", f"""
import json
pj = json.load(open('{OUT}/papers.json'))
papers = pj if isinstance(pj, list) else pj.get('papers', [])
for p in papers:
    if '{aid}' in str(p.get('arxiv', '')):
        print(p['slug']); break
"""], capture_output=True, text=True)
    s = out.stdout.strip()
    if not s:
        raise SystemExit(f"slug not found for arxiv {aid}")
    return s


def main():
    args = [a for a in sys.argv[1:]]
    slug = None
    if "--slug" in args:
        i = args.index("--slug")
        slug = args[i + 1]
        del args[i:i + 2]
    aid, kind, nums = args[0], args[1], [int(x) for x in args[2:]]
    slug = slug or slug_for(aid)
    # arXiv 原生 HTML（最新版，如 deepseek-r1 v2 长文）优先；ar5iv 兜底
    # （ar5iv 对多版本论文可能只渲染 v1 短版；新论文 ar5iv 偶发 404）
    html, base = None, None
    for cand in (f"https://arxiv.org/html/{aid}",
                 f"https://ar5iv.labs.arxiv.org/html/{aid}"):
        try:
            html = fetch(cand)
            base = cand
            break
        except Exception as e:
            print(f"  {cand}: {str(e)[:60]}, trying next")
    if html is None:
        raise SystemExit("no HTML source available")
    print(f"slug={slug} base={base}")
    dom = DOM()
    dom.feed(html)
    found = find_figures(dom, kind, set(nums))
    print(f"matched {sorted(found)} of wanted {nums}")

    vis_path = OUT / "visuals.json"
    vis = json.loads(vis_path.read_text())
    entry_list = vis.setdefault(slug, {}).setdefault(
        "figures" if kind == "fig" else "tables", [])
    caps_path = OUT / "minimax_captions.json"
    caps = json.loads(caps_path.read_text())

    for num in nums:
        node = found.get(num)
        if node is None:
            print(f"  {kind}{num}: NOT FOUND in ar5iv, skip")
            continue
        out = CROPS / f"{slug}-{kind}{num:02d}.png"
        cap_node = next(node.iter("figcaption"), None)
        caption = re.sub(r"\s+", " ", cap_node.all_text()).strip() if cap_node else ""
        if kind == "fig":
            try:
                ok, msg = save_figure(node, base, out)
            except Exception as e:
                ok, msg = False, f"fetch error: {str(e)[:60]}"
        else:
            ok, msg = render_table(node, caption, out)
        if not ok:
            print(f"  {kind}{num}: FAIL {msg}")
            continue
        # visuals.json：替换则保留原 page，新增则 page=0
        existing = next((e for e in entry_list if e["num"] == num), None)
        item = {"num": num,
                "page": existing["page"] if existing else 0,
                "caption": re.sub(rf"^\s*{'Figure' if kind=='fig' else 'Table'}\s*{num}\s*[:.\-|]?\s*",
                                  "", caption, flags=re.I)[:300],
                "path": f"assets/crops/{out.name}"}
        if existing:
            entry_list[entry_list.index(existing)] = item
        else:
            entry_list.append(item)
            entry_list.sort(key=lambda e: e["num"])
        # 登记所有权：extract_visuals 全量重裁时不得覆盖/丢失 ar5iv 产物
        # （这些论文的 PDF 字体/结构坏了，重裁只会得到乱码或缺失）
        reg_path = OUT / "ar5iv_crops.json"
        reg = json.loads(reg_path.read_text()) if reg_path.exists() else {}
        reg[item["path"]] = {"slug": slug, "kind": kind, **item}
        reg_path.write_text(json.dumps(reg, ensure_ascii=False, indent=1))
        # 旧解读失效（描述的是乱码/错误版本）
        for key in (f"extraction/assets/crops/{out.name}", f"assets/crops/{out.name}"):
            if key in caps:
                del caps[key]
                msg += " [stale caption invalidated]"
        print(f"  {kind}{num}: OK {msg}")

    vis_path.write_text(json.dumps(vis, ensure_ascii=False, indent=1))
    caps_path.write_text(json.dumps(caps, ensure_ascii=False, indent=1))
    print("visuals.json + minimax_captions.json updated")


if __name__ == "__main__":
    main()
