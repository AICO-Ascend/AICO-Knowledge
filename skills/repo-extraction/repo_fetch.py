#!/usr/bin/env python3
"""repo_fetch.py — 代码仓稀疏拉取 + 清单登记 (repo-extraction phase 1)。

输入: repos_download_list.txt (slug | git_url | ref? | note?)
输出:
  repos_src/<slug>/            稀疏克隆 (blob:none + no-cone sparse patterns, 只取文档/元数据 blob)
  extraction/repo_inventory.json   每仓: git 元数据 / 版本候选 / 文档树 / 语言分布 / 顶层结构

设计要点 (镜像论文 phase1, 但针对 git 仓):
- --filter=blob:none + sparse-checkout: 全 tree 可用 (git ls-tree), blob 按需下载,
  大仓 (GB 级) 也只拉文档与元数据 (~几十 MB)
- sparse patterns 覆盖常见文档位置: /docs /doc /README* /**\/README.md /CHANGELOG*
  /setup.py /pyproject.toml /requirements*.txt /**\/version.py /**\/__init__.py (版本探测)
- 版本探测顺序: git 最新 tag (ls-remote) > pyproject > setup.py > package __version__ >
  docs 里 release_notes 文件名; 全部记录到 inventory 供 phase 3 裁决
- 幂等: 已存在的 repos_src/<slug> 执行 git fetch + reset 到目标 ref

用法:
  python3 repo_fetch.py [--list repos_download_list.txt] [--only slug1,slug2]
"""
import argparse, json, re, subprocess, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SRC = REPO / 'repos_src'
INVENTORY = REPO / 'extraction' / 'repo_inventory.json'

SPARSE_PATTERNS = [
    '/README*', '/CHANGELOG*', '/HISTORY*', '/LICENSE*', '/NOTICE*',
    '/docs', '/doc', '/documentation', '/guide', '/guides',
    '/setup.py', '/setup.cfg', '/pyproject.toml', '/requirements*.txt',
    '/Pipfile', '/package.json', '/Cargo.toml', '/go.mod',
    '/**/*.md',
    '/**/version.py', '/**/_version.py', '/**/__init__.py',
]
DOC_EXTS = {'.md', '.rst', '.txt'}
LANG_BY_EXT = {
    '.py': 'Python', '.cpp': 'C++', '.cc': 'C++', '.c': 'C', '.h': 'C/C++ hdr',
    '.cu': 'CUDA', '.java': 'Java', '.go': 'Go', '.rs': 'Rust', '.ts': 'TypeScript',
    '.js': 'JavaScript', '.sh': 'Shell', '.md': 'Markdown', '.yaml': 'YAML', '.yml': 'YAML',
}


def sh(args, cwd=None, check=True, timeout=600):
    r = subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    if check and r.returncode != 0:
        raise RuntimeError(f'cmd failed: {" ".join(args)}\n{r.stderr[:400]}')
    return r


def parse_list(path):
    repos = []
    for line in path.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        parts = [p.strip() for p in line.split('|')]
        slug, url = parts[0], parts[1]
        ref = parts[2] if len(parts) > 2 and parts[2] else None
        note = parts[3] if len(parts) > 3 else ''
        repos.append(dict(slug=slug, url=url, ref=ref, note=note))
    return repos


def default_branch(url):
    r = sh(['git', 'ls-remote', '--symref', url, 'HEAD'], timeout=120)
    m = re.search(r'ref: refs/heads/(\S+)\s+HEAD', r.stdout)
    return m.group(1) if m else 'master'


def latest_tag(url):
    r = sh(['git', 'ls-remote', '--tags', '--sort=-version:refname', url], timeout=120)
    for line in r.stdout.splitlines():
        if line.endswith('^{}'):
            continue
        m = re.search(r'refs/tags/(\S+)$', line.strip())
        if m:
            return m.group(1)
    return None


def fetch_one(slug, url, ref):
    dst = SRC / slug
    ref = ref or default_branch(url)
    if (dst / '.git').exists():
        sh(['git', 'fetch', '--depth', '1', 'origin', ref], cwd=dst, timeout=900)
        sh(['git', 'reset', '--hard', 'FETCH_HEAD'], cwd=dst)
    else:
        SRC.mkdir(exist_ok=True)
        sh(['git', 'clone', '--depth', '1', '--filter=blob:none', '--sparse',
            '--branch', ref, url, str(dst)], timeout=1800)
        sh(['git', 'sparse-checkout', 'set', '--no-cone'] + SPARSE_PATTERNS, cwd=dst, timeout=1800)
    head = sh(['git', 'rev-parse', 'HEAD'], cwd=dst).stdout.strip()
    commit_date = sh(['git', 'show', '-s', '--format=%cI', 'HEAD'], cwd=dst).stdout.strip()
    tree = sh(['git', 'ls-tree', '-r', '--name-only', 'HEAD'], cwd=dst, timeout=300).stdout.splitlines()
    return ref, head, commit_date, tree


def version_candidates(dst, tree, tag):
    cands = {}
    if tag:
        cands['git_tag'] = tag
    for f in ('pyproject.toml', 'setup.cfg'):
        p = dst / f
        if p.exists():
            m = re.search(r'^\s*version\s*=\s*["\']([^"\']+)', p.read_text(errors='ignore'), re.M)
            if m:
                cands[f] = m.group(1)
    p = dst / 'setup.py'
    if p.exists():
        m = re.search(r'version\s*=\s*["\']([^"\']+)', p.read_text(errors='ignore'))
        if m:
            cands['setup.py'] = m.group(1)
    for f in tree:
        if f.endswith(('/version.py', '/_version.py')) and (dst / f).exists():
            m = re.search(r'version\s*=\s*["\']([^"\']+)', (dst / f).read_text(errors='ignore'))
            if m:
                cands[f] = m.group(1)
                break
    return cands


def inventory_one(slug, url, ref, note):
    dst = SRC / slug
    print(f'── {slug}: fetching {url} @{ref or "default"}')
    ref, head, commit_date, tree = fetch_one(slug, url, ref)
    tag = latest_tag(url)
    docs = [f for f in tree if Path(f).suffix.lower() in DOC_EXTS]
    md_docs = [f for f in tree if f.endswith('.md')]
    figures = [f for f in tree if Path(f).suffix.lower() in ('.png', '.jpg', '.jpeg', '.svg', '.gif')]
    lang_hist = {}
    for f in tree:
        lang = LANG_BY_EXT.get(Path(f).suffix.lower())
        if lang:
            lang_hist[lang] = lang_hist.get(lang, 0) + 1
    top_dirs = sorted({f.split('/')[0] for f in tree if '/' in f})
    checked_out = sum(1 for f in tree if (dst / f).is_file())
    inv = dict(
        slug=slug, url=url, ref=ref, note=note,
        head=head, commit_date=commit_date, latest_tag=tag,
        version_candidates=version_candidates(dst, tree, tag),
        tree_files=len(tree), checked_out_files=checked_out,
        docs_total=len(docs), docs_md=len(md_docs), figures_total=len(figures),
        languages=dict(sorted(lang_hist.items(), key=lambda kv: -kv[1])),
        top_dirs=top_dirs,
        # 版本关联: snapshots 追加式历史 (重拉时旧快照入列, 支撑仓更新后的知识关联/diff)
        snapshots=[],
    )
    print(f'   files={len(tree)} md={len(md_docs)} figs={len(figures)} tag={tag} '
          f'ver={inv["version_candidates"]}')
    return inv


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--list', default=str(REPO / 'repos_download_list.txt'))
    ap.add_argument('--only', default=None)
    args = ap.parse_args()
    repos = parse_list(Path(args.list))
    if args.only:
        keep = set(args.only.split(','))
        repos = [r for r in repos if r['slug'] in keep]
    INVENTORY.parent.mkdir(exist_ok=True)
    inv_all = {}
    if INVENTORY.exists():
        inv_all = {r['slug']: r for r in json.loads(INVENTORY.read_text(encoding='utf-8'))['repos']}
    done_n, err_n = 0, 0
    for i, r in enumerate(repos, 1):
        try:
            prev = inv_all.get(r['slug'])
            inv = inventory_one(**r)
            # 版本关联: 旧快照(不同 head/tag)入历史, 保留知识血缘
            if prev and prev.get('head') and prev['head'] != inv['head']:
                inv['snapshots'] = (prev.get('snapshots') or []) + [
                    dict(head=prev['head'], commit_date=prev.get('commit_date'),
                         ref=prev.get('ref'), latest_tag=prev.get('latest_tag'))]
            elif prev and prev.get('snapshots'):
                inv['snapshots'] = prev['snapshots']
            inv_all[r['slug']] = inv
            done_n += 1
        except Exception as e:
            err_n += 1
            inv_all[r['slug']] = dict(slug=r['slug'], url=r['url'], ref=r['ref'],
                                      note=r['note'], status='error',
                                      error=str(e)[:300])
            print(f'   ✗ {r["slug"]}: {str(e)[:200]}')
        # 每仓落盘一次 (批量长跑防中断丢失)
        out = dict(updated='phase1', repos=sorted(inv_all.values(), key=lambda x: x['slug']))
        INVENTORY.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding='utf-8')
        print(f'   [{i}/{len(repos)}] done={done_n} err={err_n}')
    print(f'✓ inventory: {INVENTORY} ({len(inv_all)} repos, err={err_n})')


if __name__ == '__main__':
    sys.exit(main())
