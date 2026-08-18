#!/usr/bin/env python3
"""Phase 1: extract text + metadata + figure pages + text captions for all papers.
Produces per-paper Obsidian-flavored MD + a master figures index. Cheap, no MiniMax.

Portable: derives REPO root from this script's location
(skills/paper-extraction/extract_phase1.py → repo root 2 levels up)."""
import fitz, re, os, json, sys
from pathlib import Path

# repo root = 2 levels up from this script (skills/paper-extraction/..)
SCRIPT=Path(__file__).resolve()
REPO=SCRIPT.parents[2]
PAPERS=REPO/"papers"
OUT=REPO/"extraction"
FULLTEXT=OUT/"fulltext"
ASSETS=OUT/"assets"
OUT.mkdir(exist_ok=True); ASSETS.mkdir(exist_ok=True); FULLTEXT.mkdir(exist_ok=True)

def parse_index():
    """num -> (title, date, abs_link, pdf_link, slug, tags)"""
    info={}
    for line in open(REPO/"papers_effective.md",encoding="utf-8"):
        parts=[p.strip() for p in line.split("|")]; inner=parts[1:-1]
        if not inner or not re.match(r'\d+$',inner[0] or ''): continue
        num,title,date,al,pl,loc,ab=inner[:7]
        m=re.match(r'✓ papers/(.+)\.pdf',loc)
        if m: info[num]={"title":title,"date":date,"abs":al,"pdf":pl,"slug":m.group(1),"ab":ab}
    return info

def extract_authors(t):
    # authors: lines between title block and "Abstract". Drop the title
    # (first non-empty line) and arxiv/url/affiliation noise.
    m=re.search(r'(.*?)\n*Abstract\b', t, re.S)
    if not m: return ""
    pre=m.group(1)
    lines=[l.strip() for l in pre.splitlines() if l.strip()]
    if len(lines)<=1: return ""
    cand=lines[1:]  # drop first line (title)
    # keep lines that look like authors/affiliations: have letters, short-ish,
    # not pure URLs/arxiv refs
    out=[]
    for l in cand:
        if re.search(r'arXiv:\d', l) or l.lower().startswith('http'): continue
        if len(l)>250: continue
        if not re.search(r'[A-Za-z]', l): continue
        out.append(l)
    s=" ".join(out)
    s=re.sub(r'\s+',' ',s).strip()
    return s[:220]

def extract_figures(full_text, doc):
    """Find Figure N captions in text, return list of {num, page(1-indexed), caption}."""
    figs=[]
    seen=set()
    for p in range(doc.page_count):
        t=doc[p].get_text()
        for m in re.finditer(r'Figure\s+(\d+)[.:]\s*([^\n]*(?:\n(?![A-Z][a-z]|\d\.|Figure|Table)[^\n]*)*)', t):
            num=int(m.group(1)); cap=m.group(2).strip()
            cap=re.sub(r'\s+',' ',cap)
            # strip trailing arxiv boilerplate / page noise
            cap=re.sub(r'\s*(?:arXiv:\d+[^\s]*|†Work done[^.]*\.?)\s*','',cap).strip()
            if num in seen: continue
            seen.add(num)
            figs.append({"num":num,"page":p+1,"caption":cap[:400]})
    return sorted(figs,key=lambda x:x["num"])

def render_figure_pages(doc, slug, figs):
    """Render pages containing figures to PNG. Returns {page: png_relpath}."""
    mat=fitz.Matrix(150/72,150/72)
    out={}
    for f in figs:
        p=f["page"]-1
        if p<0 or p>=doc.page_count: continue
        path=ASSETS/f"{slug}-p{f['page']:02d}.png"
        if not path.exists():
            doc[p].get_pixmap(matrix=mat).save(str(path))
        out[f["page"]]=f"assets/{slug}-p{f['page']:02d}.png"
    return out

def slugify_topic(title):
    tags=[]
    t=title.lower()
    rules=[("speculative",["spec","eagle","medusa","dflash","dspark","jetspec","block diffusion","draft"]),
           ("sparse-attention",["sparse","indexcache","dsa","lightning"]),
           ("kv-cache",["kv cache","kvcache","cache"]),
           ("moe",["mixture","moe","expert"]),
           ("training",["training","megatron","zero","megascale"]),
           ("rl",["reinforcement","rlhf","grpo","ppo","reward"]),
           ("multimodal",["vl","visual","multimodal","vlm","lmm"]),
           ("disaggregated-serving",["disaggregat","mooncake","sarathi","sglang","serve"]),
           ("long-context",["long-context","long context","million-token"]),
           ("architecture",["topology","network","gpu cluster"])]
    for tag,kws in rules:
        if any(k in t for k in kws): tags.append(tag)
    return tags

MATH_CHARS = set("∑∏√≈≤≥∈∀αβγδθλμπσφωΣΠ·×⊗⊙→←↑↓ⁿ")
MATH_WORDS = ("softmax", "argmax", "arg min", "argmin", "Attention(", "exp(", "log ",
              "E[", "KL(", "loss", "Loss", "∇", "norm")

def extract_formulas(doc, max_keep=15):
    """Heuristic key-formula extraction: short display-ish lines containing '='
    plus math indicators. Lossy on two-column PDFs — marked heuristic in output.
    Returns [{page, text}]."""
    out, seen = [], set()
    for p in range(doc.page_count):
        for ln in doc[p].get_text().splitlines():
            s = re.sub(r'\s+', ' ', ln).strip()
            if not (8 <= len(s) <= 180):
                continue
            if '=' not in s:
                continue
            if not (any(c in MATH_CHARS for c in s) or any(w in s for w in MATH_WORDS)):
                continue
            # skip prose sentences (too many words before the '=')
            if len(s.split('=', 1)[0].split()) > 8:
                continue
            # skip URLs / refs / code-ish
            if re.search(r'http|arxiv|figure|table|section', s, re.I):
                continue
            key = s[:60]
            if key in seen:
                continue
            seen.add(key)
            out.append({"page": p + 1, "text": s})
            if len(out) >= max_keep:
                return out
    return out

def write_paper_md(num, meta, doc, full_text, figs, fig_paths, mm, related=None, formulas=None):
    slug=meta["slug"]
    authors=extract_authors(doc[0].get_text())
    tags=slugify_topic(meta["title"])
    m=[]
    m.append("---")
    m.append(f'paper_num: "{num}"')
    m.append(f'title: "{meta["title"]}"')
    m.append(f'authors: "{authors}"')
    m.append(f'date: "{meta["date"]}"')
    m.append(f'arxiv: "{meta["abs"]}"')
    m.append(f'pdf: "papers/{slug}.pdf"')
    m.append(f'slug: "{slug}"')
    m.append(f'tags: [{", ".join(tags)}]')
    m.append("---")
    m.append("")
    m.append(f"# {meta['title']}")
    m.append("")
    m.append(f"> [!abstract] 摘要（原文）")
    m.append(f"> {meta['ab']}")
    m.append("")
    m.append("## 元信息")
    m.append(f"- **发表日期**: {meta['date']}")
    m.append(f"- **作者**: {authors or '—'}")
    m.append(f"- **arXiv**: {meta['abs']}")
    m.append(f"- **本地 PDF**: `papers/{slug}.pdf`")
    m.append(f"- **页数**: {doc.page_count}")
    m.append("")
    m.append("## 图表（原文 caption + 页码）")
    if not figs:
        m.append("_未检测到带 caption 的 figure_")
    for f in figs:
        rel=fig_paths.get(f["page"])
        # minimax deep caption keyed by png relative path (assets/...)
        mmkey=rel[7:] if rel and rel.startswith("assets/") else None
        mmcap=mm.get(rel) or (mm.get("extraction/"+rel) if rel else None)
        has_mm = bool(mmcap)
        m.append("")
        m.append(f"### Figure {f['num']} (p.{f['page']}){' ⭐深度解读' if has_mm else ''}")
        if rel:
            m.append(f"![[{rel}]]")
        m.append(f'> [!quote] caption')
        m.append(f'> {f["caption"]}')
        if has_mm:
            m.append("")
            m.append(f"> [!tip] 技术解读（多模态）")
            m.append(f"> {mmcap}")
    m.append("")
    if formulas:
        if any("latex" in fo for fo in formulas):
            m.append("## 关键公式（LaTeX 源，可直接粘贴 Obsidian/报告）")
            m.append("")
            for fo in formulas:
                m.append(f"$$\n{fo['latex']}\n$$")
                m.append("")
        else:
            m.append("## 关键公式（启发式抽取，引用前请核对原文页码）")
            m.append("")
            for fo in formulas:
                m.append(f"- p.{fo['page']} `{fo['text']}`")
            m.append("")
    if related:
        m.append("## 相关论文")
        m.append("")
        for rslug, rtitle in related:
            m.append(f"- [[{rslug}]] — {rtitle}")
        m.append("")
    # 深度解读笔记：extraction/deep/<slug>.md 由夜间深读(DEEP_LEARNING_PROTOCOL)产出，
    # 独立文件、不参与重生成，故此处仅嵌入 wikilink 指针，重跑 extract 不丢深读产出。
    deep_path = OUT / "deep" / f"{slug}.md"
    if deep_path.exists():
        m.append("## 技术点深读（DEEP）")
        m.append("")
        m.append(f"![[deep/{slug}]]  <!-- 深度解读：技术点/表格/跨论文关系，独立维护，重跑不丢 -->")
        m.append("")
    m.append("## 全文文本")
    m.append(f"全文已存 `extraction/fulltext/{slug}.txt`（{len(full_text)} 字符）供引用检索。")
    # save full text
    (FULLTEXT/f"{slug}.txt").write_text(full_text,encoding="utf-8")
    (OUT/f"{slug}.md").write_text("\n".join(m),encoding="utf-8")
    return len(full_text)

def load_minimax():
    p=OUT/"minimax_captions.json"
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return {}

def main():
    info=parse_index()
    mm=load_minimax()
    fj=OUT/"formulas.json"
    latex_formulas=json.loads(fj.read_text(encoding="utf-8")) if fj.exists() else {}
    print(f"papers to extract: {len(info)} | MiniMax captions: {len(mm)} | latex-formula papers: {sum(1 for v in latex_formulas.values() if v)}")
    # related-paper graph: shared tags (weight 2) + title token Jaccard (weight 1)
    def tset(t): return set(re.findall(r'[a-z0-9]+', t.lower()))
    ptags={n: slugify_topic(m["title"]) for n,m in info.items()}
    ttoks={n: tset(m["title"]) for n,m in info.items()}
    related_map={}
    for n in info:
        scored=[]
        for n2 in info:
            if n2==n: continue
            sc=2*len(set(ptags[n])&set(ptags[n2]))
            u=ttoks[n]|ttoks[n2]
            sc+= (len(ttoks[n]&ttoks[n2])/len(u)) if u else 0
            if sc>=2: scored.append((sc,info[n2]["slug"],info[n2]["title"]))
        scored.sort(key=lambda x:-x[0])
        related_map[n]=[(s,t) for _,s,t in scored[:6]]
    figures_catalog=[]  # for master index
    manifest=[]
    for num,meta in sorted(info.items(),key=lambda x:int(x[0])):
        slug=meta["slug"]; pdf=PAPERS/f"{slug}.pdf"
        if not pdf.exists():
            print(f"  [skip {num}] {slug}: pdf missing"); continue
        try:
            doc=fitz.open(str(pdf))
            full_text="\n".join(doc[i].get_text() for i in range(doc.page_count))
            figs=extract_figures(full_text,doc)
            fig_paths=render_figure_pages(doc,slug,figs)
            formulas=latex_formulas.get(slug) or extract_formulas(doc)
            nch=write_paper_md(num,meta,doc,full_text,figs,fig_paths,mm,
                               related=related_map.get(num),formulas=formulas)
            for f in figs:
                figures_catalog.append({"num":num,"title":meta["title"],"slug":slug,
                    "fig":f["num"],"page":f["page"],"caption":f["caption"],
                    "img":fig_paths.get(f["page"],""),"tags":slugify_topic(meta["title"])})
            manifest.append({"num":int(num),"title":meta["title"],"slug":slug,
                "date":meta["date"],"arxiv":meta["abs"],"pdf_url":meta["pdf"],
                "tags":ptags[num],"pages":doc.page_count,"figs":len(figs),
                "md":f"extraction/{slug}.md","fulltext":f"extraction/fulltext/{slug}.txt",
                "fulltext_chars":nch})
            print(f"  [{num}] {slug[:50]}: pages={doc.page_count} figs={len(figs)} formulas={len(formulas)} text={nch}")
        except Exception as e:
            print(f"  [ERR {num}] {slug}: {e}")
    # machine-readable manifest (RAG / programmatic consumption)
    (OUT/"papers.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=1),encoding="utf-8")
    # MOC: map of content, topic clusters with wikilinks
    mo=["# 🗺️ 知识图谱总览（MOC — Map of Content）","",
        "> 按主题聚类的全库导航；每篇论文是一个 `[[wikilink]]` 节点，Obsidian 图谱视图可直接可视化。",
        "> 单篇 MD 内含「相关论文」交叉链接（共享主题标签 + 标题相似度自动计算）。",""]
    by_tag={}
    for m0 in manifest:
        for t in m0["tags"]: by_tag.setdefault(t,[]).append(m0)
    for t in sorted(by_tag):
        ps=sorted(by_tag[t],key=lambda x:x["num"])
        mo.append(f"## {t} ({len(ps)})"); mo.append("")
        for p0 in ps:
            mo.append(f"- [[{p0['slug']}]] — {p0['title']} ({p0['date']})")
        mo.append("")
    mo.append("## 全部论文（按编号）"); mo.append("")
    for p0 in manifest:
        mo.append(f"- #{p0['num']} [[{p0['slug']}]] — {p0['title']}")
    # 跨论文关系谱系：extraction/moc_relations.md 由夜间深读人工维护，
    # 独立文件、不参与重生成，此处仅嵌入 wikilink 指针，重跑 extract 不丢人工沉淀。
    rel_path = OUT / "moc_relations.md"
    if rel_path.exists():
        mo.append("")
        mo.append("## 跨论文关系与演进")
        mo.append("")
        mo.append("![[moc_relations]]  <!-- 人工维护的跨论文谱系，独立文件，重跑不丢 -->")
        mo.append("")
    (OUT/"MOC.md").write_text("\n".join(mo)+"\n",encoding="utf-8")
    # master figures index
    b=["# 📊 图表素材索引（figures_index）","","",
       "> 按主题分类的图表清单，含 caption + 页码 + 本地图片路径，便于技术报告快速插入与引用。","",
       "> 标 ⭐ 的图已用 MiniMax 多模态深度解读（技术解读见对应论文 MD 的 Figure [!tip]）。",""]
    # ⭐ Featured: MiniMax deep-captioned figures (dedupe by PNG)
    featured=[]
    seen_png=set()
    for f in figures_catalog:
        if f["img"] and ("extraction/"+f["img"] in mm or f["img"] in mm) and f["img"] not in seen_png:
            seen_png.add(f["img"]); featured.append(f)
    b.append(f"共 {len(figures_catalog)} 张图，来自 {len({f['num'] for f in figures_catalog})} 篇论文；其中 ⭐{len(featured)} 张已深度解读。")
    b.append("")
    if featured:
        b.append("## ⭐ 精选架构图（MiniMax 深度解读，可直接插入技术报告）"); b.append("")
        for f in featured:
            interp=mm.get("extraction/"+f["img"]) or mm.get(f["img"]) or ""
            b.append(f"### {f['title'][:60]} — Fig.{f['fig']} (p.{f['page']})")
            b.append(f"![[{f['img']}]]")
            b.append(f"> [!tip] {interp}")
            b.append(f"*caption: {f['caption'][:150]}… ｜ 论文 [[{f['slug']}]] ｜ arxiv 见 MD 元信息*")
            b.append("")
    by_tag={}
    for f in figures_catalog:
        for t in f["tags"]:
            by_tag.setdefault(t,[]).append(f)
    b.append("## 按主题分类"); b.append("")
    for t in sorted(by_tag):
        b.append(f"### {t} ({len(by_tag[t])})"); b.append("")
        for f in by_tag[t]:
            star="⭐ " if (f["img"] and ("extraction/"+f["img"] in mm or f["img"] in mm)) else ""
            b.append(f"- {star}![[{f['img']}]] — **{f['title'][:50]}** Fig.{f['fig']} (p.{f['page']}): {f['caption'][:80]}…  `[[{f['slug']}]]`")
        b.append("")
    b.append("## 按论文"); b.append("")
    for num in sorted({f['num'] for f in figures_catalog},key=int):
        fs=[f for f in figures_catalog if f["num"]==num]
        b.append(f"### #{num} {fs[0]['title'][:60]}"); b.append("")
        for f in fs:
            star="⭐ " if (f["img"] and ("extraction/"+f["img"] in mm or f["img"] in mm)) else ""
            b.append(f"- {star}Fig.{f['fig']} (p.{f['page']}) ![[{f['img']}]]")
            b.append(f"  - {f['caption'][:200]}")
        b.append("")
    (OUT/"figures_index.md").write_text("\n".join(b),encoding="utf-8")
    print(f"\nDONE. figures: {len(figures_catalog)} | ⭐featured: {len(featured)} | master index: extraction/figures_index.md")

if __name__=="__main__":
    main()
