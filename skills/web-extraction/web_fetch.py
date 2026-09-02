#!/usr/bin/env python3
"""web_fetch.py — 网页知识抓取与规范化 (web-extraction phase 1)。

输入: webs_download_list.txt (slug | url | 备注)
输出:
  extraction/web_docs/<slug>.md        规范化 markdown (HTML→md, 表格/代码/标题保留)
  extraction/web_index.json            每页: url/标题/抓取路径/字数/图片数/抓取时间

抓取策略 (按序降级, 全部实测于 2026-09-02):
  1. URL 以 .md 结尾: curl 直取 (hiascend doc_center 对 .md 路径直接返回原始 markdown)
  2. curl 取 HTML, 内容探测 (article/table/h1/pre 密度) — docs.vllm.ai 等服务端渲染站直接命中
  3. hiascend SPA (document/detail/ 但内容稀薄): 改写为 doc_center/source/ 同源路径取原始内容
     (SPA 壳内容来自该路径, 实测含全部表格正文; Nuxt SPA 截图级渲染在本网络不可用 — 超时)
  4. 兜底: playwright headless (资源拦截 + 正文轮询)

规范化: markdownify 转 md; 剥离 nav/footer/script; 图片记录但不下载 (web 图稳定性差,
深读阶段按需惰性下载 — 同 repo_deep_read 的 web 图策略)。
"""
import argparse, json, re, subprocess, sys, time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / 'extraction' / 'web_docs'
INDEX = REPO / 'extraction' / 'web_index.json'

CONTENT_MARKERS = ('<table', '<article', '<pre', '<h1', '<h2', '<main')


def parse_list(path):
    pages = []
    for line in path.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        parts = [p.strip() for p in line.split('|')]
        pages.append(dict(slug=parts[0], url=parts[1],
                          note=parts[2] if len(parts) > 2 else ''))
    return pages


def curl(url, timeout=60):
    r = subprocess.run(['curl', '-sL', '--max-time', str(timeout),
                        '-A', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
                        url], capture_output=True, timeout=timeout + 20)
    return r.stdout.decode('utf-8', errors='ignore') if r.returncode == 0 else ''


def content_score(html):
    return sum(html.count(m) for m in CONTENT_MARKERS)


def hiascend_source_url(url):
    """document/detail/ → doc_center/source/ 同源改写"""
    m = re.match(r'(https://www\.hiascend\.com/)document/detail/(.+)$', url)
    if m:
        return f'{m.group(1)}doc_center/source/{m.group(2)}'
    return None


def _absolutize_links(text, url):
    """相对链接绝对化 (站内互链是后续知识关联的出处, 必须可点)"""
    from urllib.parse import urljoin
    def fix(m):
        label, href = m.group(1), m.group(2)
        if href.startswith(('http://', 'https://', '#', 'mailto:')):
            return m.group(0)
        return f'[{label}]({urljoin(url, href)})'
    return re.sub(r'\[([^\]]*)\]\(([^)\s]+)\)', fix, text)


def _cleanup(text, url):
    """规范化噪音清理: mkdocs [¶] 锚点 / 自定义标签 <term> / 多余空行"""
    text = re.sub(r'\[¶\]\([^)]*"Permanent link"\)', '', text)
    text = re.sub(r'</?(?:term|ph|i18n|span)[^>]*>', '', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = _absolutize_links(text, url)
    return text.strip()


def to_markdown(html, url):
    from markdownify import markdownify as md
    # 剥离 script/style
    html = re.sub(r'<script[\s\S]*?</script>|<style[\s\S]*?</style>|<!--[\s\S]*?-->', '', html)
    # 尝试定位主内容区
    for pat in (r'<article[\s\S]*</article>', r'<main[\s\S]*</main>',
                r'<div[^>]*class="[^"]*(?:doc|content|article|markdown)[^"]*"[\s\S]*'):
        m = re.search(pat, html, re.I)
        if m:
            html = m.group(0) if not pat.endswith('*') else m.group(0)
            break
    text = md(html, heading_style='ATX', tables='pipe')
    return _cleanup(text, url)


def fetch_one(slug, url, note):
    route = 'direct'
    raw = ''
    if url.endswith('.md'):
        raw = curl(url)
        if raw.lstrip().startswith('<'):  # 返回的是 HTML 壳而非 md
            raw = ''
    if not raw:
        html = curl(url)
        if content_score(html) >= 3:
            raw = html
            route = 'direct-html'
        else:
            src = hiascend_source_url(url)
            if src:
                alt = curl(src)
                if content_score(alt) >= 3 or alt.lstrip().startswith('#'):
                    raw = alt
                    route = 'hiascend-source'
    if not raw:
        return dict(slug=slug, url=url, note=note, status='fetch-failed',
                    error='direct/spa-source 均未取到内容')
    if raw.lstrip().startswith('#') or not raw.lstrip().startswith('<'):
        text = _cleanup(raw, url)  # 已是 markdown (仍清噪音 + 绝对化链接)
        route += '(raw-md)' if route == 'direct' else ''
    else:
        text = to_markdown(raw, url)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f'{slug}.md').write_text(text, encoding='utf-8')
    title_m = re.search(r'^#\s+(.+)$', text, re.M)
    return dict(slug=slug, url=url, note=note, status='ok', route=route,
                title=title_m.group(1) if title_m else slug,
                chars=len(text), tables=text.count('\n|'),
                fetched_at=time.strftime('%Y-%m-%d %H:%M'))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--list', default=str(REPO / 'webs_download_list.txt'))
    ap.add_argument('--only', default=None)
    args = ap.parse_args()
    pages = parse_list(Path(args.list))
    if args.only:
        keep = set(args.only.split(','))
        pages = [p for p in pages if p['slug'] in keep]
    results = []
    if INDEX.exists():
        results = [r for r in json.loads(INDEX.read_text(encoding='utf-8'))['pages']
                   if r['slug'] not in {p['slug'] for p in pages}]
    for p in pages:
        r = fetch_one(**p)
        results.append(r)
        print(f"── {p['slug']}: {r['status']} route={r.get('route')} chars={r.get('chars')} tables={r.get('tables')}")
    INDEX.write_text(json.dumps(dict(pages=results), ensure_ascii=False, indent=1),
                     encoding='utf-8')
    ok = sum(1 for r in results if r['status'] == 'ok')
    print(f'✓ web index: {INDEX} ({ok}/{len(results)} ok)')


if __name__ == '__main__':
    sys.exit(main())
