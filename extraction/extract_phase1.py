#!/usr/bin/env python3
"""Phase 1: extract text + metadata + figure pages + text captions for all papers.
Produces per-paper Obsidian-flavored MD + a master figures index. Cheap, no MiniMax."""
import fitz, re, os, json, sys
from pathlib import Path

REPO=Path("/mnt/project/g00952465/AICO-knowledge")
PAPERS=REPO/"papers"
OUT=REPO/"extraction"
ASSETS=OUT/"assets"
OUT.mkdir(exist_ok=True); ASSETS.mkdir(exist_ok=True)

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

def write_paper_md(num, meta, doc, full_text, figs, fig_paths, mm):
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
        m.append(f"### Figure {f['num']} (p.{f['page']}){' ⭐MiniMax深度解读' if has_mm else ''}")
        if rel:
            m.append(f"![[{rel}]]")
        m.append(f'> [!quote] caption')
        m.append(f'> {f["caption"]}')
        if has_mm:
            m.append("")
            m.append(f"> [!tip] 技术解读（MiniMax 多模态）")
            m.append(f"> {mmcap}")
    m.append("")
    m.append("## 全文文本")
    m.append(f"全文已存 `extraction/{slug}.txt`（{len(full_text)} 字符）供引用检索。")
    # save full text
    (OUT/f"{slug}.txt").write_text(full_text,encoding="utf-8")
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
    print(f"papers to extract: {len(info)} | MiniMax captions: {len(mm)}")
    figures_catalog=[]  # for master index
    for num,meta in sorted(info.items(),key=lambda x:int(x[0])):
        slug=meta["slug"]; pdf=PAPERS/f"{slug}.pdf"
        if not pdf.exists():
            print(f"  [skip {num}] {slug}: pdf missing"); continue
        try:
            doc=fitz.open(str(pdf))
            full_text="\n".join(doc[i].get_text() for i in range(doc.page_count))
            figs=extract_figures(full_text,doc)
            fig_paths=render_figure_pages(doc,slug,figs)
            nch=write_paper_md(num,meta,doc,full_text,figs,fig_paths,mm)
            for f in figs:
                figures_catalog.append({"num":num,"title":meta["title"],"slug":slug,
                    "fig":f["num"],"page":f["page"],"caption":f["caption"],
                    "img":fig_paths.get(f["page"],""),"tags":slugify_topic(meta["title"])})
            print(f"  [{num}] {slug[:50]}: pages={doc.page_count} figs={len(figs)} text={nch}")
        except Exception as e:
            print(f"  [ERR {num}] {slug}: {e}")
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
