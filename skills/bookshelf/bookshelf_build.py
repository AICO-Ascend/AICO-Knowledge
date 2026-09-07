#!/usr/bin/env python3
"""bookshelf_build.py — 知识书架生成器 (bookshelf P1)。

从三域注册表 + CURATION.md(内嵌 yaml 策展定义) 幂等生成:
  bookshelf/SHELF.md         入口一 · 知识书架（技术栈六层主线 L1→L6 + 横向专题 + 模型卡片）
  (入口二 AscendInfra 昇腾专区为独立手工页 bookshelf/ascend_infra.md(html 可视化版), 不在此生成)

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

# 分类排序权重（表格内聚合顺序；未登记的排最后按字序）
CATEGORY_ORDER = ['RL', 'Agent', '架构', '稀疏注意力', 'MoE', '投机解码', '多模态', '综述', '扩展',
                  '训练系统', '训练框架', '推理系统', '推理框架', '算子', '系统软件', '硬件']


def cat_rank(c):
    return CATEGORY_ORDER.index(c) if c in CATEGORY_ORDER else len(CATEGORY_ORDER)


def clean_cn(text, max_chars=110, max_sents=3):
    """深读首段 → 简短中文摘要: 去 markdown/引用标记, 按句界截断"""
    s = re.sub(r'(^|\n)\s*(?:[-*+]|\d+\.)\s+', r'\1', text)    # 去列表符号
    s = re.sub(r'\$\$?.+?\$\$?', ' ', s)                    # 去行内公式
    s = re.sub(r'[（(][^）)]*§[^）)]*[）)]', '', s)             # 去 (§x.y) 引用
    s = re.sub(r'\[\[([^\]|]*\|)?([^\]]+)\]\]', r'\2', s)      # wikilink → 内文
    s = re.sub(r'[*`>#]', '', s)
    s = re.sub(r'\s+', ' ', s).strip()
    sents = [x for x in re.split(r'(?<=[。！？])', s) if x.strip()]
    out = ''
    for sent in sents[:max_sents]:
        if out and len(out) + len(sent) > max_chars:
            break
        out += sent
        if len(out) >= max_chars:
            break
    if not out and s:
        out = s[:max_chars - 1] + '…'
    return out


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
            arxiv = (p or {}).get('arxiv') or ''
            return ('arXiv 原文', arxiv) if arxiv.startswith('http') else None
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

    def summary(self, ref):
        """摘要列内容 (机械提取): 论文=发表月+深读「核心问题」首段中文摘要(≤3句); 仓卡片=定位+tag+提交日期;
        仓文档=所属仓定位; 网页=标题+备注; 概念页=主题名"""
        kind, _, rest = ref.partition(':')
        if kind in ('paper', 'papermd'):
            slug = rest
            p = self.reg['papers'].get(slug)
            if not p:
                cands = [x for x in self.reg['papers'] if x.startswith(slug)]
                if len(cands) == 1:
                    slug = cands[0]
                    p = self.reg['papers'][slug]
            if not p:
                return ''
            pub = re.search(r'arxiv\.org/abs/(\d{2})(\d{2})\.', p.get('arxiv', ''))
            pub = f'20{pub.group(1)}-{pub.group(2)}' if pub else (p.get('date') or '')
            # 中文摘要权威源 = deep/<slug>.md「核心问题」首段（面向人类学习者, 不用英文 abstract）
            cn = ''
            deep = REPO / 'extraction' / 'deep' / f'{slug}.md'
            if deep.exists():
                m = re.search(r'^##\s*(?:\d+\.\s*)?核心问题[^\n]*\n\s*((?:(?!\n\s*\n).)+)',
                              deep.read_text(encoding='utf-8', errors='ignore'), re.S | re.M)
                if m:
                    cn = clean_cn(m.group(1))
            return f'{pub} · {cn}' if cn else pub
        if kind == 'repocard':
            inv = self.reg['inventory'].get(rest) or {}
            bits = []
            if inv.get('note'):
                bits.append(inv['note'])
            if inv.get('latest_tag'):
                bits.append(f"最新 {inv['latest_tag']}")
            if inv.get('commit_date'):
                bits.append(f"更新于 {str(inv['commit_date'])[:10]}")
            return ' · '.join(bits)
        if kind == 'reponote':
            slug, _, path = rest.partition(':')
            inv = self.reg['inventory'].get(slug) or {}
            n = self.reg['notes'].get((slug, path)) or {}
            bits = [f"仓 {slug} · {n.get('type', 'doc')} 文档"]
            if inv.get('latest_tag'):
                bits.append(f"仓最新 {inv['latest_tag']}")
            return ' · '.join(bits)
        if kind == 'web':
            p = self.reg['web'].get(rest) or {}
            import re as _r
            toks = _r.findall(r'/(?:latest|[vV]?\d{3,}(?:beta\d*|rc\d*)?)(?=/|$)', p.get('url', ''))
            ver = '/'.join(t.strip('/') for t in toks)
            bits = []
            if ver:
                bits.append(f'版本线 {ver}')
            if p.get('fetched_at'):
                bits.append(f"抓取于 {str(p['fetched_at'])[:10]}")
            return ' · '.join(bits)
        if kind == 'concept':
            return f'概念页 · {rest}'
        return ''

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
            return rest, link, ''  # 版本 tag 由摘要列携带, 备注列不重复
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
            pretty = rest.replace('-', ' ').title().replace('Kv', 'KV').replace('Rl', 'RL').replace('Llm', 'LLM').replace('Moe', 'MoE').replace('Npu', 'NPU')
            return f'{pretty}（概念页）', link, ''
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


def guard_rules(cur):
    """上架铁律的机械闸门 (防架构腐蚀) —— 规则原文见 CURATION.md 头部「上架铁律」。
    违反即拒绝生成 (非零退出), 不允许带病上架。"""
    errs = []
    for sec in cur['sections']:
        for it in sec.get('items', []):
            ref = it['ref']
            kind, _, rest = ref.partition(':')
            cat = it.get('category') or sec.get('category') or sec['title']
            where = f"{sec['id']} :: {ref[:60]}"
            # G1 一跳直达: 概念页种子 (仅链接列表) 不上书架
            if kind == 'concept':
                errs.append(f'G1 概念页种子不上书架: {where}')
            # G2 骨架仓卡不上架: 无分析层 (deep/repo-<slug>.md) 的 repocard 禁止引用
            if kind == 'repocard' and not (REPO / f'extraction/deep/repo-{rest}.md').exists():
                errs.append(f'G2 骨架仓卡不上架: {where} — 移入泊车场, 或改链 reponote 深读文档/仓外链')
            # G3 中文摘要必须有来源: 论文条目须存在 deep 深读且含「核心问题」段
            if kind == 'paper':
                deep = REPO / 'extraction' / 'deep' / f'{rest}.md'
                if not deep.exists():
                    cands = list((REPO / 'extraction/deep').glob(f'{rest}*.md'))
                    deep = cands[0] if len(cands) == 1 else deep
                ok = deep.exists() and re.search(
                    r'^##\s*(?:\d+\.\s*)?核心问题[^\n]*\n\s*\S',
                    deep.read_text(encoding='utf-8', errors='ignore'), re.M)
                if not ok:
                    errs.append(f'G3 论文缺深读中文摘要来源: {where}')
            # G4 分类词表收敛: 分类必须在 CATEGORY_ORDER 内 (防词表漂移)
            if cat not in CATEGORY_ORDER:
                errs.append(f'G4 未登记分类 "{cat}": {where} — 词表见 bookshelf_build.CATEGORY_ORDER')
    return errs


def render_remarks(item, auto_note, resolver):
    # 备注流: 🔥⚡ 符号最前 → 策展备注 → 资产链接 → 昇腾注记; 日期由摘要列单独携带不重复
    parts = []
    heat, diff = item.get('heat'), item.get('difficulty')
    if heat:
        parts.append('🔥' * int(heat))
    if diff:
        parts.append('⚡' * int(diff))
    if item.get('note'):
        parts.append(item['note'])
    assets = resolver.asset_md(item.get('assets'))
    if assets:
        parts.append(assets)
    if item.get('ascend'):
        parts.append(f'昇腾：{item["ascend"]}')
    return ' · '.join(parts)


def render_section(sec, layers, resolver):
    lines = [f'### {sec["title"]}', '']
    if sec.get('intro'):
        lines += [sec['intro'].strip(), '']
    lines += ['| 📚 知识源 | 📖&nbsp;知⁠识⁠分⁠类 | 🔧 层次 | 📜 深读 | 📄 摘要 |',
              '|---|---|---|---|---|']
    def sort_key(it):
        cat = it.get('category') or sec.get('category') or sec['title']
        _, _, dt = resolver.resolve(it['ref'])
        return (cat_rank(cat), cat, str(dt))
    for item in sorted(sec.get('items', []), key=sort_key):
        title, link, auto_note = resolver.resolve(item['ref'])
        title = item.get('title') or title   # 策展级标题覆盖（注册表标题太笼统时）
        category = item.get('category') or sec.get('category') or sec['title']
        # 分类字间插零宽连接符 (U+2060): 禁止浏览器拆行, 把「知识分类」列撑到不折行
        cat_cell = '⁠'.join(category)
        orig = resolver.original(item['ref'])
        source_md = f'[{title}]({orig[1]})' if orig else f'[{title}]({link})'
        digest_md = '—' if item['ref'].startswith(('ext:', 'crop:')) else f'[link]({link})'
        remarks = render_remarks(item, auto_note, resolver)
        summary = resolver.summary(item['ref'])
        # 摘要列内部: 🔥⚡ 符号 → 日期/版本动态 → 正文/备注
        syms, rest_r = [], []
        for part in remarks.split(' · ') if remarks else []:
            (syms if part and all(ch in '🔥⚡' for ch in part) else rest_r).append(part)
        tail = ' · '.join(x for x in [' '.join(syms), summary] + rest_r if x)
        lines.append(f'| {source_md} | {cat_cell} | {sec["layer"]} | {digest_md} | {tail} |')
    lines.append('')
    return '\n'.join(lines)


def build_shelf(cur, reg, resolver):
    layers = cur['layers']
    L = [f'<!-- GENERATED by bookshelf_build.py from CURATION.md · 勿手改条目表, 策展改 CURATION.md -->',
         '', '# 📚 AICO-Knowledge 知识书架', '']
    L.append(cur['shelf_intro'].strip())
    L.append('')
    L.append('> 技术栈主线：' + ' → '.join(f'**{k} {layers[k]}**' for k in LAYER_ORDER)
             + '。配套入口：[♨️ AscendInfra 昇腾专区](ascend_infra.md)（昇腾全栈可视化讲解）· [🟩 NvidiaInfra 货架](nvidia_infra.md)（GPU 生态）。')
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
              '> 架构关键词只列**模型结构组件**；链接列只放总体模型结构解析页（本库 `bookshelf/models/` 本地化收纳；缺失的用 model-arch 技能从 HF config 实时生成补齐）；论文深读/裁剪图等入「其他」。', '',
              '| 模型 | 架构关键词 | 链接 | 其他 |', '|---|---|---|---|']
        for c in cur['model_cards']:
            st = c.get('structure')
            if st:
                _, link, _ = resolver.resolve(st)
                st_md = f'[结构解析]({link})'
            else:
                st_md = '（待生成）'
            others = []
            for a in c.get('others', []):
                title, link, _ = resolver.resolve(a['ref'])
                others.append(f'[{a.get("label", title)}]({link})')
            L.append(f'| {c["name"]} | {c["keywords"]} | {st_md} | {" · ".join(others) or "—"} |')
        L.append('')
    if cur.get('tools'):
        L += ['<a id="辅助工具"></a>', '## 🛠️ 辅助工具', '',
              '> 常用计算/可视化小工具：本库自建页面 [在线直开](https://aico-ascend.github.io/AICO-knowledge/)（GitHub Pages）或从 `bookshelf/tools/` 下载后用浏览器打开（自包含单文件）+ 社区优质文章收录。', '',
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
    guard_errs = guard_rules(cur)
    if guard_errs:
        print('✗ 上架铁律违规:')
        for e in guard_errs:
            print('  -', e)
        return 1
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
          f' (ascend_infra 为独立手工页(md 主入口/html 备份), 不由本脚本生成)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
