#!/usr/bin/env python3
"""repo_deep_read.py — 代码仓文档图文关联深读 (repo-extraction phase 3b 批量层)。

镜像论文 DEEP_LEARNING_PROTOCOL, 对 repo_docs_index.json 中的目标文档
(默认 feature/design/overview/guide/changelog 五类高价值型) 做:

  1) 文档深读 (text): MiniMax-M3 结构化解读 → extraction/repo_deep_docs/<slug>/<path>
     【定位】【技术要点】【关键机制与真实数据】【关联(内部链接/上下游)】【使用方法】
  2) 图文关联 (vision): 带图文档的每张收割图, 文档正文作上下文喂 M3 vision
     → extraction/repo_m3_captions.json (slug#path#fig → 图文联合解读)
  3) 深读笔记按仓组织, 供 repo 卡片 §4 聚合与 kb 查询

纪律 (与论文域一致):
- 文档维度一体化: 每篇笔记含该篇全文上下文, 不拆孤立片段
- 图必须配文档正文上下文喂 M3 (禁止裸读图)
- 幂等: 已产出的笔记/解读跳过, 断点续跑
- 并发 5, fcntl 锁写 captions JSON (同 bulk_caption.sh 模式)

用法:
  python3 repo_deep_read.py [--only slug1,slug2] [--types feature,design,...]
                            [--limit N] [--workers 5]
"""
import argparse, fcntl, importlib.util, json, sys, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DOCS_ROOT = REPO / 'extraction' / 'repo_docs'
INDEX = REPO / 'extraction' / 'repo_docs_index.json'
OUT_ROOT = REPO / 'extraction' / 'repo_deep_docs'
CAPTIONS = REPO / 'extraction' / 'repo_m3_captions.json'

spec = importlib.util.spec_from_file_location(
    'm3', str(REPO / 'skills' / 'paper-extraction' / 'm3_caption.py'))
m3 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m3)

DOC_PROMPT = '''你是技术知识库分析员。这是代码仓「{slug}」({repo_note})中路径为 {path} 的一篇{doctype}文档。
请基于原文做一体化深度解读 (不拆孤立片段, 不臆造原文没有的数字/机制), 输出七节:
【定位】一句话: 这篇文档解决什么问题/描述什么能力
【技术要点】核心机制分条 (3-6 条, 保留原文关键数字/参数/命令)
【关键机制与数据】工作原理/数据流/性能数据 (原文有的才写, 标注"原文:")
【表格解读】原文中的关键表格 (参数表/性能对比/配置项), 用 markdown 表格**逐字还原**后逐行解读; 无表格写"原文无表格"
【公式解读】原文中的公式 (LaTeX 或伪代码形式), **逐字保留原式**并解释每个符号含义与作用; 无公式写"原文无公式"
【关联】与文中提到的其他特性/模块/上下游的关系 (利用文末内部链接信息)
【使用方法】启用方式/配置项/命令 (原文有则写, 无则写"原文未涉及")
内部链接: {links}

原文:
---
{text}
---'''

VERSION = 'v2'  # prompt 版本: 升级后旧笔记自动重生成 (幂等按版本判定)

FIG_PROMPT = '''这是代码仓「{slug}」特性文档「{title}」的配图。文档上下文:
{ctx}
请做图文联合解读: 1) 图里画了什么 (结构/数据流/关键标注) 2) 论证了什么技术结论 3) 与文档论点的关系。≤150字。'''


def read_doc_text(slug, path, limit=9000):
    p = DOCS_ROOT / slug / path
    if not p.exists():
        return None
    t = p.read_text(encoding='utf-8', errors='ignore')
    return t[:limit]


def fig_path(slug, fig_src):
    """figures 收割后统一在 <slug>/figures/<basename>; http(s) 外链图惰性下载后同路径"""
    cleaned = fig_src.strip().strip('<>').split()[0].strip('"').strip("'").split('?')[0]
    p = DOCS_ROOT / slug / 'figures' / Path(cleaned).name
    if p.exists():
        return p
    if fig_src.startswith(('http://', 'https://')):
        import subprocess as sp
        p.parent.mkdir(parents=True, exist_ok=True)
        r = sp.run(['curl', '-sL', '--max-time', '60', '-o', str(p), fig_src],
                   capture_output=True)
        if r.returncode == 0 and p.exists() and p.stat().st_size > 1000:
            return p
    return None


def save_caption(key, caption):
    with open(CAPTIONS, 'a+', encoding='utf-8') as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        f.seek(0)
        try:
            d = json.load(f)
        except Exception:
            d = {}
        d[key] = caption
        f.seek(0)
        f.truncate()
        json.dump(d, f, ensure_ascii=False, indent=1)


def load_captions():
    if CAPTIONS.exists():
        return json.loads(CAPTIONS.read_text(encoding='utf-8'))
    return {}


def process_doc(entry, note_map):
    slug, path = entry['slug'], entry['path']
    out = OUT_ROOT / slug / path
    if out.exists() and f'ver={VERSION}' in out.read_text(encoding='utf-8', errors='ignore')[:300]:
        return 'skip'
    text = read_doc_text(slug, path)
    if not text or len(text.strip()) < 200:
        return 'thin'
    note = note_map.get(slug, '')
    prompt = DOC_PROMPT.format(slug=slug, repo_note=note, path=path,
                               doctype=entry['type'],
                               links=', '.join(entry.get('internal_links', [])[:10]) or '(无)',
                               text=text)
    try:
        body = m3.caption_text(prompt) if hasattr(m3, 'caption_text') else None
        if body is None:
            body = m3_call_text(prompt)
    except Exception as e:
        return f'err:{str(e)[:80]}'
    # 图文关联: 带图文档逐图 vision (正文作上下文)
    caps = load_captions()
    fig_section = []
    ctx = text[:1500].replace('\n', ' ')
    for fig in entry.get('figures', []):
        key = f'{slug}#{path}#{Path(fig).name}'
        if key in caps:
            cap = caps[key]
        else:
            fp = fig_path(slug, fig)
            if not fp:
                continue
            try:
                cap = m3.caption(str(fp), FIG_PROMPT.format(
                    slug=slug, title=entry['title'], ctx=ctx), max_tokens=8000)
                save_caption(key, cap)
                time.sleep(0.5)
            except Exception as e:
                cap = f'(图解读失败: {str(e)[:60]})'
        fig_section.append(f'- `{Path(fig).name}`: {cap}')
    out.parent.mkdir(parents=True, exist_ok=True)
    header = (f'# {entry["title"]}\n\n> 仓 `{slug}` · 路径 `{path}` · 类型 {entry["type"]} · '
              f'MiniMax-M3 文档深读 + 图文关联 · ver={VERSION}\n> 原文: extraction/repo_docs/{slug}/{path}\n\n')
    figs_md = ('\n\n## 图文联合解读\n\n' + '\n'.join(fig_section)) if fig_section else ''
    out.write_text(header + body + figs_md + '\n', encoding='utf-8')
    return 'ok'


def m3_call_text(prompt):
    """text-only 调用走同一网关 (MiniMax-M3 reasoning, max_tokens 留足)"""
    import os, urllib.request
    key = m3.get_key()
    url = os.environ.get('VOLC_GATEWAY_URL', m3.DEFAULT_URL)
    payload = {
        'model': os.environ.get('M3_MODEL', 'MiniMax-M3'),
        'messages': [{'role': 'user', 'content': prompt}],
        'max_tokens': 8000,
    }
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers={'Authorization': f'Bearer {key}',
                                          'Content-Type': 'application/json'})
    r = json.loads(urllib.request.urlopen(req, timeout=300).read())
    content = r['choices'][0]['message'].get('content') or ''
    if not content.strip():
        raise RuntimeError(f"empty content (usage={r.get('usage')})")
    return content


FIG_SECTION_RE = None


def _backfill_one(entry):
    caps = load_captions()
    made = 0
    slug, path = entry['slug'], entry['path']
    figs = entry.get('figures', [])
    if not figs:
        return 0
    text = read_doc_text(slug, path) or ''
    ctx = text[:1500].replace('\n', ' ')
    for fig in figs:
        key = f'{slug}#{path}#{Path(fig.strip().strip("<>").split()[0].strip(chr(34)).strip(chr(39)).split("?")[0]).name}'
        if key in caps:
            continue
        fp = fig_path(slug, fig)
        if not fp:
            continue
        try:
            cap = m3.caption(str(fp), FIG_PROMPT.format(
                slug=slug, title=entry['title'], ctx=ctx), max_tokens=8000)
            save_caption(key, cap)
            made += 1
            time.sleep(0.3)
        except Exception as e:
            print(f'  fig err {key}: {str(e)[:80]}', flush=True)
    return made


def backfill_captions(sel, workers=5):
    """补齐所有缺失图解读 (含 web 外链图, 并发), 并重写已存在笔记的『图文联合解读』段。"""
    import re as _re
    with_fig = [e for e in sel if e.get('figures')]
    made = 0
    with ThreadPoolExecutor(max_workers=workers) as ex:
        for i, m in enumerate(ex.map(_backfill_one, with_fig), 1):
            made += m
            if i % 20 == 0 or i == len(with_fig):
                print(f'[backfill {i}/{len(with_fig)}] made={made}', flush=True)
    caps = load_captions()
    for entry in with_fig:
        slug, path = entry['slug'], entry['path']
        figs = entry.get('figures', [])
        # 重写笔记图段 (保证段与 captions store 一致)
        out = OUT_ROOT / slug / path
        if out.exists():
            note = out.read_text(encoding='utf-8')
            fig_section = []
            for fig in figs:
                key = f'{slug}#{path}#{Path(fig.split("?")[0]).name}'
                if key in caps:
                    fig_section.append(f'- `{Path(fig.split("?")[0]).name}`: {caps[key]}')
            if fig_section:
                new_sec = '\n\n## 图文联合解读\n\n' + '\n'.join(fig_section) + '\n'
                if '## 图文联合解读' in note:
                    note = _re.sub(r'\n\n## 图文联合解读\n\n.*', lambda _m: new_sec, note, flags=_re.S)
                else:
                    note = note.rstrip() + new_sec
                out.write_text(note, encoding='utf-8')
    print(f'✓ backfill: {made} new captions')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--only', default=None)
    ap.add_argument('--backfill-captions', action='store_true')
    ap.add_argument('--types', default='feature,design,overview,guide,changelog')
    ap.add_argument('--limit', type=int, default=0)
    ap.add_argument('--workers', type=int, default=5)
    args = ap.parse_args()
    docs = json.loads(INDEX.read_text(encoding='utf-8'))['docs']
    types = set(args.types.split(','))
    sel = [e for e in docs if e['type'] in types]
    if args.only:
        keep = set(args.only.split(','))
        sel = [e for e in sel if e['slug'] in keep]
    # 高价值仓优先 (断点续跑时部分进度也有用)
    PRIORITY = ['mindspeed', 'xllm', 'vllm-ascend', 'vllm', 'mindspeed-llm', 'mindspeed-mm',
                'mindspeed-rl', 'mindspeed-bridge', 'mindspeed-ops', 'megatronadaptor',
                'transformerenginenpu', 'mindie-llm', 'mindie-turbo', 'mindie-motor', 'mindie-sd',
                'msmodelslim', 'torchair', 'pytorch', 'op-plugin', 'vision', 'apex',
                'triton-ascend', 'tilelang-ascend', 'catlass', 'xllm_ops', 'torch_npu_ops',
                'hccl_transfer', 'memfabric_hybrid', 'memcache', 'parakv', 'docs', 'agent-skills']
    sel.sort(key=lambda e: (PRIORITY.index(e['slug']) if e['slug'] in PRIORITY else 999, e['slug'], e['path']))
    if args.limit:
        sel = sel[:args.limit]
    note_map = {}
    inv_p = REPO / 'extraction' / 'repo_inventory.json'
    if inv_p.exists():
        for r in json.loads(inv_p.read_text(encoding='utf-8'))['repos']:
            note_map[r['slug']] = r.get('note', '')
    if args.backfill_captions:
        backfill_captions(sel, workers=args.workers)
        return
    print(f'深读目标: {len(sel)} 篇 (types={sorted(types)})')
    stat = {'ok': 0, 'skip': 0, 'thin': 0, 'err': 0}
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        for i, res in enumerate(ex.map(lambda e: process_doc(e, note_map), sel), 1):
            k = res.split(':')[0]
            stat[k if k in stat else 'err'] += 1
            if i % 20 == 0 or i == len(sel):
                print(f'[{i}/{len(sel)}] {stat}', flush=True)
    print(f'✓ done {stat}')


if __name__ == '__main__':
    sys.exit(main())
