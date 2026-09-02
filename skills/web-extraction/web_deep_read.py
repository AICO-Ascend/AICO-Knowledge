#!/usr/bin/env python3
"""web_deep_read.py — 网页知识深读 (web-extraction phase 2)。

镜像 repo_deep_read.py 的 M3 七节深读, 对 extraction/web_docs/ 每页:
  【定位】【技术要点】【关键机制与数据】【表格逐字还原解读】【公式逐字保留解读】
  【关联】【使用方法】
→ extraction/web_deep_docs/<slug>.md (ver=v1 版本标记幂等)

与 repo 域差异:
- 来源上下文 = 原文 URL + 站点 + URL 版本 token (canncommercial/900 → CANN 商用 9.0.0 一类
  版本线在 URL 里, 机械层只记原始 token 不解读)
- 长文全量进 prompt (网页多为参考手册, 截断丢表格 = 丢核心价值; 上限 100k 字符)
- 图文关联: UI 图标类 (public_sys-resources 等) 是页面装饰不是知识图, 跳过;
  真实配图按需 M3 vision (本批无)

产物登记: 深读完成后回写 web_index.json 每页 deep_note 字段 (单一注册表)。

用法:
  python3 skills/web-extraction/web_deep_read.py [--only slug1,slug2]
"""
import argparse, importlib.util, json, os, re, sys, time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DOCS = REPO / 'extraction' / 'web_docs'
INDEX = REPO / 'extraction' / 'web_index.json'
OUT = REPO / 'extraction' / 'web_deep_docs'

spec = importlib.util.spec_from_file_location(
    'm3', str(REPO / 'skills' / 'paper-extraction' / 'm3_caption.py'))
m3 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m3)

VERSION = 'v1'
MAX_CHARS = 100_000

DOC_PROMPT = '''你是技术知识库分析员。这是网页「{url}」(站点 {site}, 备注说明: {note})的一篇技术文档,
于 {fetched} 抓取入库 (URL 版本线索: {vhints})。
请基于原文做一体化深度解读 (不拆孤立片段, 不臆造原文没有的数字/机制/参数), 输出七节:
【定位】一句话: 这个页面解决什么问题/供什么场景查阅
【技术要点】核心机制/参数/命令分条 (3-8 条, 保留原文关键数字与写法)
【关键机制与数据】工作原理/配置语义/版本差异 (原文有的才写, 标注"原文:")
【表格解读】原文中的关键表格 (参数表/环境变量表/硬件支持表), 用 markdown 表格**逐字还原**后
逐类解读 (同类条目可归并说明, 但变量名/取值/默认值必须原样); 无表格写"原文无表格"
【公式解读】原文中的公式 (LaTeX 或伪代码), **逐字保留原式**并解释符号含义; 无公式写"原文无公式"
【关联】页面内链指向的相关文档/模块 (用原文链接说明知识脉络); 无写"原文未涉及"
【使用方法】可直接照抄的命令/配置/环境变量用法 (原文有则写, 无则写"原文未涉及")

原文:
---
{text}
---'''


def version_hints(url):
    """URL 路径中的版本 token (900/910beta1/2600/latest 等), 原样记录"""
    toks = re.findall(r'/(?:latest|[vV]?\d{3,}(?:beta\d*|rc\d*)?)(?=/|$)', url)
    return ', '.join(t.strip('/') for t in toks) if toks else '(URL 无版本段)'


def m3_call_text(prompt):
    import urllib.request
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


def read_page(slug):
    p = DOCS / f'{slug}.md'
    if not p.exists():
        return None
    t = p.read_text(encoding='utf-8', errors='ignore')
    return t[:MAX_CHARS]


def process(page):
    slug = page['slug']
    out = OUT / f'{slug}.md'
    if out.exists() and f'ver={VERSION}' in out.read_text(encoding='utf-8', errors='ignore')[:300]:
        return 'skip'
    text = read_page(slug)
    if not text or len(text.strip()) < 200:
        return 'thin'
    prompt = DOC_PROMPT.format(url=page['url'], site=page['url'].split('/')[2],
                               note=page.get('note') or '(无)', fetched=page.get('fetched_at', '?'),
                               vhints=version_hints(page['url']), text=text)
    try:
        body = m3_call_text(prompt)
    except Exception as e:
        return f'err:{str(e)[:80]}'
    n_imgs = len(re.findall(r'!\[', text))
    OUT.mkdir(parents=True, exist_ok=True)
    header = (f'# {page.get("title", slug)}\n\n'
              f'> 来源 {page["url"]}\n> 抓取路由 {page.get("route")} · {page.get("fetched_at")} · '
              f'原文 {len(text)} 字符 · {n_imgs} 图\n'
              f'> MiniMax-M3 七节深读 · ver={VERSION} · 原文: extraction/web_docs/{slug}.md\n\n')
    out.write_text(header + body + '\n', encoding='utf-8')
    return 'ok'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--only', default=None)
    args = ap.parse_args()
    data = json.loads(INDEX.read_text(encoding='utf-8'))
    pages = [p for p in data['pages'] if p.get('status') == 'ok']
    if args.only:
        keep = set(args.only.split(','))
        pages = [p for p in pages if p['slug'] in keep]
    print(f'深读目标: {len(pages)} 页')
    for p in pages:
        r = process(p)
        print(f'── {p["slug"]}: {r}', flush=True)
        if r == 'ok':
            p['deep_note'] = f'extraction/web_deep_docs/{p["slug"]}.md'
        time.sleep(0.5)
    INDEX.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding='utf-8')
    ok = sum(1 for p in data['pages'] if p.get('deep_note'))
    print(f'✓ web index (deep_note 登记): {INDEX} ({ok} 页有深读)')


if __name__ == '__main__':
    sys.exit(main())
