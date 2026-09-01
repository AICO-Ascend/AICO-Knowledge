#!/usr/bin/env python3
"""repo_deep_index.py — 深读笔记知识组织 (repo-extraction phase 3c)。

聚合深读产物 → 可查询的知识组织层:
  extraction/repo_deep_index.json   全量深读笔记索引 (slug/type/title/path/fig captions 数)
  extraction/deep/repo-<slug>.md    卡片 §4 末尾追加「深读笔记索引」链接块 (幂等, 标记段内重生成)

纪律: 卡片 §4 链接块为机械层 (<!-- DEEP_NOTES:BEGIN/END --> 标记内), 可安全重生成,
不触碰分析层手写内容。
"""
import json, re, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DEEP_DOCS = REPO / 'extraction' / 'repo_deep_docs'
OUT = REPO / 'extraction' / 'repo_deep_index.json'
DOCS_INDEX = REPO / 'extraction' / 'repo_docs_index.json'
DEEP = REPO / 'extraction' / 'deep'

BEGIN, END = '<!-- DEEP_NOTES:BEGIN -->', '<!-- DEEP_NOTES:END -->'


def main():
    idx = json.loads(DOCS_INDEX.read_text(encoding='utf-8'))['docs']
    meta = {(e['slug'], e['path']): e for e in idx}
    entries = []
    per_repo = {}
    for md in sorted(DEEP_DOCS.rglob('*.md')):
        parts = md.relative_to(DEEP_DOCS).parts
        slug, path = parts[0], '/'.join(parts[1:])
        e = meta.get((slug, path), {})
        title = e.get('title', md.stem)
        entries.append(dict(slug=slug, path=path, type=e.get('type', '?'),
                            title=title,
                            note=f'extraction/repo_deep_docs/{slug}/{path}'))
        per_repo.setdefault(slug, []).append(entries[-1])
    OUT.write_text(json.dumps(dict(notes=entries), ensure_ascii=False, indent=1),
                   encoding='utf-8')
    print(f'✓ deep index: {OUT} ({len(entries)} notes, {len(per_repo)} repos)')
    for slug, notes in sorted(per_repo.items()):
        card = DEEP / f'repo-{slug}.md'
        if not card.exists():
            continue
        s = card.read_text(encoding='utf-8')
        block = BEGIN + '\n\n### 深读笔记索引（机械层 · ' + str(len(notes)) + ' 篇）\n\n' + '\n'.join(
            f'- [{n["title"]}](../repo_deep_docs/{slug}/{n["path"]}) `{n["type"]}`'
            for n in notes[:60]) + ('\n- …' if len(notes) > 60 else '') + '\n\n' + END
        if BEGIN in s:
            s = re.sub(re.escape(BEGIN) + '.*?' + re.escape(END), block, s, flags=re.S)
        else:
            s = s.rstrip() + '\n\n' + block + '\n'
        card.write_text(s, encoding='utf-8')
    print(f'✓ cards updated: {len(per_repo)}')


if __name__ == '__main__':
    sys.exit(main())
