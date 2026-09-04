#!/usr/bin/env python3
"""bookshelf_build.py — 知识书架生成器 (bookshelf P1)。

从三域注册表 + CURATION.md(内嵌 yaml 策展定义) 幂等生成:
  bookshelf/SHELF.md         入口一 · 知识书架（技术栈六层主线 L1→L6 + 横向专题 + 模型卡片）
  bookshelf/ascend_infra.md  入口二 · AscendInfra 昇腾专区（L6→L1 全栈 + 知识对照表 + AscendV 引用地图 + 仓全景）

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
    lines += ['| 📚 条目 | 📖 知识分类 | 🔧 层次 | 📜 备注 |',
              '|---|---|---|---|']
    for item in sec.get('items', []):
        title, link, auto_note = resolver.resolve(item['ref'])
        category = item.get('category') or sec.get('category') or sec['title']
        remarks = render_remarks(item, auto_note, resolver)
        lines.append(f'| [{title}]({link}) | {category} | {sec["layer"]} | {remarks} |')
    lines.append('')
    return '\n'.join(lines)


def build_shelf(cur, reg, resolver):
    layers = cur['layers']
    L = [f'<!-- GENERATED by bookshelf_build.py from CURATION.md · 勿手改条目表, 策展改 CURATION.md -->',
         '', '# 📚 AICO-Knowledge 知识书架', '']
    L.append(cur['shelf_intro'].strip())
    L.append('')
    L.append('> 技术栈主线：' + ' → '.join(f'**{k} {layers[k]}**' for k in LAYER_ORDER)
             + '。任一层可横跳 [AscendInfra 昇腾专区](ascend_infra.md) 对应层。')
    L.append('')
    L.append('## 目录')
    L.append('')
    for k in LAYER_ORDER:
        secs = [s for s in cur['sections'] if s['layer'] == k]
        if secs:
            L.append(f'- **{k} {layers[k]}**：' + ' · '.join(f'[{s["title"]}](#{s["id"]})' for s in secs))
    L.append(f'- **横向专题**：' + ' · '.join(f'[{s["title"]}](#{s["id"]})' for s in cur.get('topics', [])))
    L.append('- **[主流模型卡片](#模型卡片)**')
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
    if cur.get('topics'):
        L += ['## 横向专题（跨层学习路径）', '']
        for sec in cur['topics']:
            L.append(f'<a id="{sec["id"]}"></a>')
            L.append(render_section(sec, layers, resolver))
    if cur.get('model_cards'):
        L += ['<a id="模型卡片"></a>', '## 主流模型卡片', '',
              '| 模型 | 架构关键词 | 入口 |', '|---|---|---|']
        for c in cur['model_cards']:
            links = []
            for a in c.get('links', []):
                title, link, _ = resolver.resolve(a['ref'])
                links.append(f'[{a.get("label", title)}]({link})')
            L.append(f'| {c["name"]} | {c["keywords"]} | {" · ".join(links)} |')
        L.append('')
    return '\n'.join(L)


def build_ascend_infra(cur, reg, resolver):
    ai = cur['ascend_infra']
    layers = cur['layers']
    L = ['<!-- GENERATED by bookshelf_build.py from CURATION.md · 勿手改, 策展改 CURATION.md -->',
         '', '# ♨️ AscendInfra · 昇腾全栈知识专区', '']
    L.append(ai['intro'].strip())
    L.append('')
    L.append('> 与技术栈主线反向展开（L6→L1，从硬件往上看）；横向通用知识回 [主书架](SHELF.md)。')
    L.append('')
    for k in reversed(LAYER_ORDER):
        secs = [s for s in ai['sections'] if s['layer'] == k]
        if not secs:
            continue
        L += [f'## {k} {layers[k]}（昇腾）', '']
        for sec in secs:
            L.append(render_section(sec, layers, resolver))
    if ai.get('cross_table'):
        L += ['## 知识对照表（可视化 ↔ 深读 ↔ 仓实现 三方互证）', '',
              '| 概念 | 外部可视化 | 本库深读/手册 | 仓实现锚点 |', '|---|---|---|---|']
        for row in ai['cross_table']:
            cells = []
            for key in ('external', 'ours', 'impl'):
                v = row.get(key)
                if not v:
                    cells.append('—')
                elif isinstance(v, str) and ':' in v and not v.startswith('http'):
                    title, link, _ = resolver.resolve(v)
                    cells.append(f'[{title}]({link})')
                else:
                    cells.append(str(v))
            L.append(f'| {row["concept"]} | {cells[0]} | {cells[1]} | {cells[2]} |')
        L.append('')
    if ai.get('reference_map'):
        L += ['## 外部可视化资源引用地图', '',
              '> 动画演示/交互案例优先去官方平台；论文机制/版本血缘/手册深读回本库。', '',
              '| 平台 | 模块 | 定位 | 何时用它而不是本库 |', '|---|---|---|---|']
        for r in ai['reference_map']:
            L.append(f'| {r["platform"]} | [{r["module"]}]({r["url"]}) | {r["desc"]} | {r["when"]} |')
        L.append('')
    if ai.get('repo_landscape'):
        L += ['## 昇腾仓全景（134 仓 · 版本血缘在册）', '']
        inv = reg['inventory']
        used = set()
        for g in ai['repo_landscape']:
            pats = g['match']
            slugs = sorted(s for s in inv if any(re.fullmatch(p, s) for p in pats) and s not in used)
            used.update(slugs)
            if not slugs:
                continue
            L += [f'### {g["name"]}（{len(slugs)} 仓）', '']
            rows = []
            for s in slugs:
                r = inv[s]
                card = f'../extraction/deep/repo-{s}.md'
                if not (SHELF_DIR / card).resolve().exists():
                    card = f'../extraction/repo_cards/{s}.md'
                tag = f'`{r["latest_tag"]}`' if r.get('latest_tag') else '—'
                rows.append(f'| [{s}]({card}) | {tag} | {(r.get("note") or "")[:60]} |')
            L += ['| 仓 | 最新 tag | 定位 |', '|---|---|---|'] + rows + ['']
        rest = sorted(s for s in inv if s not in used)
        if rest:
            L += [f'### 其他（{len(rest)} 仓）', '',
                  ' · '.join(f'[{s}](../extraction/repo_cards/{s}.md)' for s in rest), '']
    if ai.get('gap_list'):
        L += ['## 共同缺口（书架反哺抓取清单）', '']
        L += [f'- {g}' for g in ai['gap_list']]
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
    infra = build_ascend_infra(cur, reg, resolver)
    if resolver.errors:
        print('✗ 死链/引用错误:')
        for e in sorted(set(resolver.errors)):
            print('  -', e)
        return 1
    if not args.check_only:
        SHELF_DIR.mkdir(exist_ok=True)
        (SHELF_DIR / 'SHELF.md').write_text(shelf, encoding='utf-8')
        (SHELF_DIR / 'ascend_infra.md').write_text(infra, encoding='utf-8')
    n_shelf = shelf.count('| [')
    n_infra = infra.count('| [')
    print(f'✓ SHELF.md {n_shelf} 条目 · ascend_infra.md {n_infra} 条目 · 0 死链'
          f' · {"check-only" if args.check_only else "已写入"}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
