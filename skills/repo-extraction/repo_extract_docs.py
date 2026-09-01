#!/usr/bin/env python3
"""repo_extract_docs.py — 代码仓文档收割与分类 (repo-extraction phase 2)。

输入: repos_src/<slug>/ (repo_fetch.py 的稀疏克隆) + extraction/repo_inventory.json
输出:
  extraction/repo_docs/<slug>/<原相对路径>     收割的文档原文 (markdown 图片改指 figures/)
  extraction/repo_docs/<slug>/figures/...      文档引用的图片
  extraction/repo_docs_index.json              每文档: 标题/类型/大纲/图片/大小/链接

分类 (路径启发式):
  readme · changelog · feature · api · guide · design · faq · overview · doc
  - README* → readme; CHANGELOG/HISTORY/release_notes → changelog
  - docs/**/features/** → feature; **/api* → api
  - **/(user-guide|guide|tutorial|quick_start|get-started)/** → guide
  - **/design/** → design; FAQ* → faq; overview/introduction/dir_structure → overview

镜像论文萃取的「先全量收割再分级深读」: 本阶段零 LLM, 纯机械;
LLM 深读 (repo 卡片 / 关键 feature 文档) 在 phase 3。
"""
import argparse, json, re, shutil, subprocess, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SRC = REPO / 'repos_src'
DOCS_OUT = REPO / 'extraction' / 'repo_docs'
INDEX = REPO / 'extraction' / 'repo_docs_index.json'
INVENTORY = REPO / 'extraction' / 'repo_inventory.json'

IMG_RE = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')
HEAD_RE = re.compile(r'^(#{1,3})\s+(.+)$', re.M)
LINK_RE = re.compile(r'(?<!!)\[([^\]]+)\]\(([^)]+)\)')


def classify(rel):
    p = rel.lower()
    name = Path(p).name
    if name.startswith('readme'):
        return 'readme'
    if any(k in name for k in ('changelog', 'history', 'release_notes', 'releasenotes')):
        return 'changelog'
    if name.startswith('faq'):
        return 'faq'
    if '/features/' in p or '/feature/' in p:
        return 'feature'
    if 'api' in name or '/api/' in p or '/reference/' in p:
        return 'api'
    if any(k in p for k in ('/user-guide/', '/guide/', '/guides/', '/tutorial', '/quick_start', '/get-started', '/quickstart')):
        return 'guide'
    if '/design/' in p or 'design' in name:
        return 'design'
    if any(k in name for k in ('overview', 'introduction', 'dir_structure', 'architecture')):
        return 'overview'
    return 'doc'


def parse_doc(text):
    title = None
    outline = []
    for m in HEAD_RE.finditer(text):
        level, heading = len(m.group(1)), m.group(2).strip()
        if level == 1 and title is None:
            title = heading
        if level <= 3:
            outline.append(heading)
    figures = [(alt, src.strip()) for alt, src in IMG_RE.findall(text)]
    links = [(t, u.strip()) for t, u in LINK_RE.findall(text)
             if not u.strip().startswith(('http://', 'https://', '#', 'mailto:'))]
    return title, outline[:40], figures, links


def harvest(slug):
    src_root = SRC / slug
    out_root = DOCS_OUT / slug
    docs = sorted(src_root.rglob('*.md'))
    docs = [d for d in docs if '.git' not in d.parts]
    entries = []
    fig_count = 0
    for d in docs:
        rel = d.relative_to(src_root).as_posix()
        text = d.read_text(encoding='utf-8', errors='ignore')
        title, outline, figures, links = parse_doc(text)
        dst = out_root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        # 图片收割: 相对路径引用 → 复制到 figures/ 并改写引用
        new_text = text
        for alt, fsrc in figures:
            if fsrc.startswith(('http://', 'https://', 'data:')):
                continue
            cand = (d.parent / fsrc).resolve()
            if cand.exists() and cand.is_file():
                fig_dst = out_root / 'figures' / cand.name
                fig_dst.parent.mkdir(parents=True, exist_ok=True)
                if not fig_dst.exists():
                    shutil.copyfile(cand, fig_dst)
                new_text = new_text.replace(f']({fsrc})', f'](figures/{cand.name})')
                fig_count += 1
        dst.write_text(new_text, encoding='utf-8')
        entries.append(dict(
            slug=slug, path=rel, type=classify(rel),
            title=title or Path(rel).stem,
            outline=outline, figures=[f[1] for f in figures],
            internal_links=[u for _, u in links][:20],
            bytes=len(text.encode('utf-8')),
        ))
    return entries, fig_count


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--only', default=None)
    args = ap.parse_args()
    inv = json.loads(INVENTORY.read_text(encoding='utf-8'))['repos']
    slugs = [r['slug'] for r in inv]
    if args.only:
        slugs = [s for s in slugs if s in set(args.only.split(','))]
    all_entries = []
    if INDEX.exists():
        old = json.loads(INDEX.read_text(encoding='utf-8'))['docs']
        all_entries = [e for e in old if e['slug'] not in slugs]
    for slug in slugs:
        if not (SRC / slug).exists():
            print(f'── {slug}: repos_src 不存在, 先跑 repo_fetch.py')
            continue
        entries, fig_count = harvest(slug)
        types = {}
        for e in entries:
            types[e['type']] = types.get(e['type'], 0) + 1
        print(f'── {slug}: {len(entries)} docs ({types}) figures_copied={fig_count}')
        all_entries.extend(entries)
    INDEX.write_text(json.dumps(dict(docs=all_entries), ensure_ascii=False, indent=1),
                     encoding='utf-8')
    print(f'✓ docs index: {INDEX} ({len(all_entries)} docs)')


if __name__ == '__main__':
    sys.exit(main())
