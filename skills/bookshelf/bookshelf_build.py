#!/usr/bin/env python3
"""bookshelf_build.py — 知识书架生成器 (bookshelf P1)。

从三域注册表 + CURATION.md(内嵌 yaml 策展定义) 幂等生成:
  bookshelf/SHELF.md         入口一 · 知识书架（技术栈六层主线 L1→L6 + 横向专题 + 模型卡片）
  (入口二 AscendInfra 昇腾专区为独立手工 HTML 体系 bookshelf/ascend_infra.html, 不在此生成)

纪律:
- 机械层零臆造: 条目元数据(标题/版本/日期)一律从注册表解析, CURATION.md 只给引用与人工标注
- 双层写入: 条目表机械重生成; 导语/分级/对照表注入自 CURATION.md, 永不手写进产物
- 死链 lint: 所有本地链接校验存在性, 死链非零退出不静默

条目引用协议 (CURATION.md items[].ref):
  paper:<slug>              → ../extraction/deep/<slug>.md (标题取 papers.json)
  papermd:<slug>            → ../extraction/<slug>.md (结构化解构)
  reponote:<slug>:<path>    → ../extraction/repo_deep_docs/<slug>/<path> (标题取 repo_deep_index.json)
  repocard:<slug>           → ../extraction/deep/repo-<slug>.md (无则 repo_cards/<slug>.md, 备注自动带 latest_tag)
  web:<slug>                → ../extraction/web_deep_docs/<slug>.md
  concept:<slug>            → ../wiki/concepts/<slug>.md
  crop:<file>               → ../extraction/assets/crops/<file> (备注资产链接用)
  ext:<label>:<url>         → 外链 (AscendV 等)

用法: python3 skills/bookshelf/bookshelf_build.py [--check-only]
"""
import argparse, json, re, sys, time
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
SHELF_DIR = REPO / 'bookshelf'
CURATION = SHELF_DIR / 'CURATION.md'

LAYER_ORDER = ['L1', 'L2', 'L3', 'L4', 'L5', 'L6']


def load_registries():
    reg = {}
    papers = json.loads((REPO / 'extraction/papers.json').read_text(encoding='utf-8'))
    reg['papers'] = {p['slug']: p for p in papers}
    reg['inventory'] = {r['slug']: r for r in
                        json.loads((REPO / 'extraction/repo_inventory.json').read_text(encoding='utf-8'))['repos']}
    notes = json.loads((REPO / 'extraction/repo_deep_index.json').read_text(encoding='utf-8'))['notes']
    reg['notes'] = {(n['slug'], n['path']): n for n in notes}
    web = json.loads((REPO / 'extraction/web_index.json').read_text(encoding='utf-8'))['pages']
    reg['web'] = {p['slug']: p for p in web}
    return reg


def load_curation():
    """CURATION.md 中全部 ```yaml 块深度合并"""
    text = CURATION.read_text(encoding='utf-8')
    blocks = re.findall(r'```yaml\n(.*?)```', text, re.S)
    merged = {}
    for b in blocks:
        d = yaml.safe_load(b) or {}
        for k, v in d.items():
            if isinstance(v, dict) and isinstance(merged.get(k), dict):
                merged[k].update(v)
            elif isinstance(v, list) and isinstance(merged.get(k), list):
                merged[k].extend(v)
            else:
                merged[k] = v
    return merged


class Resolver:
    """ref → (标题, 相对链接, 自动备注)；死链记入 errors"""

    def __init__(self, reg):
        self.reg = reg
        self.errors = []

    def _exists(self, rel):
        return (SHELF_DIR / rel).resolve().exists()

    def original(self, ref):
        """原始出处链接: 论文→arXiv; 仓文档→gitcode blob 原始位置; 网页→原始页面; 概念页/裁剪图→—"""
        kind, _, rest = ref.partition(':')
        if kind in ('paper', 'papermd'):
            p = self.reg['papers'].get(rest)
            if not p:
                cands = [s for s in self.reg['papers'] if s.startswith(rest)]
                p = self.reg['papers'].get(cands[0]) if len(cands) == 1 else None
            return ('arXiv 原文', p['arxiv']) if p and p.get('arxiv') else None
        if kind == 'reponote':
            slug, _, path = rest.partition(':')
            inv = self.reg['inventory'].get(slug)
            if not inv or not inv.get('url'):
                return None
            base = inv['url'].removesuffix('.git')
            refname = inv.get('ref') or 'master'
            return (f'{slug} 仓原始文件', f'{base}/blob/{refname}/{path}')
        if kind == 'repocard':
            inv = self.reg['inventory'].get(rest)
            if not inv or not inv.get('url'):
                return None
            return ('代码仓', inv['url'].removesuffix('.git'))
        if kind == 'web':
            p = self.reg['web'].get(rest)
            return ('原始网页', p['url']) if p else None
        return None  # concept/crop/ext 无单一原始出处

    def resolve(self, ref):
        kind, _, rest = ref.partition(':')
        if kind == 'paper':
            p = self.reg['papers'].get(rest)
            if not p:
                # 唯一前缀兜底: 策展引用可写截断 slug, 唯一匹配即解析 (防手抄截断)
                cands = [s for s in self.reg['papers'] if s.startswith(rest)]
                if len(cands) == 1:
                    rest = cands[0]
                    p = self.reg['papers'][rest]
            link = f'../extraction/deep/{rest}.md'
            if not p:
                self.errors.append(f'paper 未注册: {rest}')
                return rest, link, ''
            if not self._exists(link):
                self.errors.append(f'死链: {link}')
            # 发表时间以 arXiv ID (YYMM) 为权威 —— papers.json 的 date 对 2026-01 批次
            # 混入的是入库日期 (34/66 不一致实测), 书架展示必须用 arXiv 派生值
            m = re.search(r'arxiv\.org/abs/(\d{2})(\d{2})\.', p.get('arxiv', ''))
            pub = f'20{m.group(1)}-{m.group(2)}' if m else (p.get('date') or '')
            return p['title'], link, pub
        if kind == 'papermd':
            link = f'../extraction/{rest}.md'
            if not self._exists(link):
                self.errors.append(f'死链: {link}')
            return rest, link, ''
        if kind == 'reponote':
            slug, _, path = rest.partition(':')
            n = self.reg['notes'].get((slug, path))
            link = f'../extraction/repo_deep_docs/{slug}/{path}'
            if not n:
                self.errors.append(f'reponote 未注册: {slug}:{path}')
            elif not self._exists(link):
                self.errors.append(f'死链: {link}')
            return (n['title'] if n else path), link, f'`{slug}`'
        if kind == 'repocard':
            inv = self.reg['inventory'].get(rest)
            deep = f'../extraction/deep/repo-{rest}.md'
            card = f'../extraction/repo_cards/{rest}.md'
            link = deep if self._exists(deep) else card
            if not self._exists(link):
                self.errors.append(f'死链: repocard {rest}')
            tag = (inv or {}).get('latest_tag') or ''
            return rest, link, (f'`{tag}`' if tag else '')
        if kind == 'web':
            p = self.reg['web'].get(rest)
            link = f'../extraction/web_deep_docs/{rest}.md'
            if not p:
                self.errors.append(f'web 未注册: {rest}')
            elif not self._exists(link):
                self.errors.append(f'死链: {link}')
            return (p or {}).get('title', rest), link, ''
        if kind == 'concept':
            link = f'../wiki/concepts/{rest}.md'
            if not self._exists(link):
                self.errors.append(f'死链: {link}')
            return rest, link, ''
        if kind == 'crop':
            link = f'../extraction/assets/crops/{rest}'
            if not self._exists(link):
                self.errors.append(f'死链: {link}')
            return rest, link, ''
        if kind == 'model':
            link = f'models/{rest}'
            if not self._exists(link):
                self.errors.append(f'死链: {link}')
            return rest, link, ''
        if kind == 'tool':
            link = f'tools/{rest}'
            if not self._exists(link):
                self.errors.append(f'死链: {link}')
            return rest, link, ''
        if kind == 'ext':
            label, _, url = rest.partition(':')
            if not url.startswith(('http://', 'https://')):
                self.errors.append(f'ext 链接格式错: {ref}')
            return label, url, ''
        self.errors.append(f'未知 ref 类型: {ref}')
        return ref, '', ''

    def asset_md(self, assets):
        """备注中的资产链接列表: [{label, ref}]"""
        out = []
        for a in assets or []:
            title, link, _ = self.resolve(a['ref'])
            out.append(f'[{a.get("label", title)}]({link})')
        return ' · '.join(out)


def render_remarks(item, auto_note, resolver):
    parts = []
    heat, diff = item.get('heat'), item.get('difficulty')
    if heat:
        parts.append('🔥' * int(heat))
    if diff:
        parts.append('⚡' * int(diff))
    if item.get('note'):
        parts.append(item['note'])
    if auto_note:
        parts.append(auto_note)
    assets = resolver.asset_md(item.get('assets'))
    if assets:
        parts.append(assets)
    if item.get('ascend'):
        parts.append(f'**昇腾**: {item["ascend"]}')
    return ' · '.join(parts)


def render_section(sec, layers, resolver):
    lines = [f'### {sec["title"]}（{sec["layer"]} {layers[sec["layer"]]}）', '']
    if sec.get('intro'):
        lines += [sec['intro'].strip(), '']
    lines += ['| 📚 知识源 | 📖 知识分类 | 🔧 层次 | 📜 摘要 | 📄 其他 |',
              '|---|---|---|---|---|']
    for item in sec.get('items', []):
        title, link, auto_note = resolver.resolve(item['ref'])
        category = item.get('category') or sec.get('category') or sec['title']
        # 知识源列: 标题链原始出处 (arXiv/仓原始文件/原网页); 无原始出处者链内部页
        orig = resolver.original(item['ref'])
        source_md = f'[{title}]({orig[1]})' if orig else f'[{title}]({link})'
        # 摘要列: 本仓萃取总结 (深读/卡片/概念页); 无独立萃取产物者 —
        digest_md = '—' if item['ref'].startswith(('ext:', 'crop:')) else f'[萃取总结]({link})'
        remarks = render_remarks(item, auto_note, resolver)
        lines.append(f'| {source_md} | {category} | {sec["layer"]} | {digest_md} | {remarks} |')
    lines.append('')
    return '\n'.join(lines)


def build_shelf(cur, reg, resolver):
    layers = cur['layers']
    L = [f'<!-- GENERATED by bookshelf_build.py from CURATION.md · 勿手改条目表, 策展改 CURATION.md -->',
         '', '# 📚 AICO-Knowledge 知识书架', '']
    L.append(cur['shelf_intro'].strip())
    L.append('')
    L.append('> 技术栈主线：' + ' → '.join(f'**{k} {layers[k]}**' for k in LAYER_ORDER)
             + '。配套入口：[♨️ AscendInfra 昇腾专区](ascend_infra.html)（独立可视化体系）· [🟩 NvidiaInfra 货架](nvidia_infra.md)（GPU 生态）。')
    L.append('')
    L.append('## 目录')
    L.append('')
    for k in LAYER_ORDER:
        secs = [s for s in cur['sections'] if s['layer'] == k]
        if secs:
            L.append(f'- **{k} {layers[k]}**：' + ' · '.join(f'[{s["title"]}](#{s["id"]})' for s in secs))
    L.append('- **[主流模型卡片](#模型卡片)** · **[辅助工具](#辅助工具)**')
    L.append('')
    for k in LAYER_ORDER:
        secs = [s for s in cur['sections'] if s['layer'] == k]
        if not secs:
            continue
        L += [f'## {k} {layers[k]}', '']
        if cur.get('layer_intros', {}).get(k):
            L += [cur['layer_intros'][k].strip(), '']
        for sec in secs:
            L.append(f'<a id="{sec["id"]}"></a>')
            L.append(render_section(sec, layers, resolver))
    if cur.get('model_cards'):
        L += ['<a id="模型卡片"></a>', '## 主流模型卡片', '',
              '> 架构关键词只列**模型结构组件**；链接列指向总体模型结构解析页（本库 `bookshelf/models/` 收纳，缺失的标注待生成）。', '',
              '| 模型 | 架构关键词 | 链接 |', '|---|---|---|']
        for c in cur['model_cards']:
            links = []
            for a in c.get('links', []):
                if a.get('empty'):
                    links.append(f'{a.get("label", "结构解析")}（待生成）')
                    continue
                title, link, _ = resolver.resolve(a['ref'])
                links.append(f'[{a.get("label", title)}]({link})')
            L.append(f'| {c["name"]} | {c["keywords"]} | {" · ".join(links)} |')
        L.append('')
    if cur.get('tools'):
        L += ['<a id="辅助工具"></a>', '## 🛠️ 辅助工具', '',
              '> 常用计算/可视化小工具：本库自建的在线可用页面（`bookshelf/tools/`，浏览器直接打开）+ 社区优质工具收录。', '',
              '| 🛠️ 工具 | 📖 知识分类 | 📜 说明 |', '|---|---|---|']
        for t in cur['tools']:
            title, link, _ = resolver.resolve(t['ref'])
            L.append(f'| [{t["name"]}]({link}) | {t.get("category", "工具")} | {t.get("note", "")} |')
        L.append('')
    return '\n'.join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check-only', action='store_true', help='只 lint 不写文件')
    args = ap.parse_args()
    reg = load_registries()
    cur = load_curation()
    resolver = Resolver(reg)
    shelf = build_shelf(cur, reg, resolver)
    if resolver.errors:
        print('✗ 死链/引用错误:')
        for e in sorted(set(resolver.errors)):
            print('  -', e)
        return 1
    if not args.check_only:
        SHELF_DIR.mkdir(exist_ok=True)
        (SHELF_DIR / 'SHELF.md').write_text(shelf, encoding='utf-8')
    import re as _re
    n_items = len(_re.findall(r'^\| \[', shelf, _re.M))
    print(f'✓ SHELF.md {n_items} 条目 · 0 死链'
          f' · {"check-only" if args.check_only else "已写入"}'
          f' (ascend_infra 为独立 HTML 体系, 不由本脚本生成)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
