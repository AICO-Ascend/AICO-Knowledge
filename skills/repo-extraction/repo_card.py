#!/usr/bin/env python3
"""repo_card.py — 代码仓卡片骨架生成 (repo-extraction phase 3 机械层)。

聚合 phase 1/2 产物 → extraction/deep/repo-<slug>.md 骨架:
  版本裁决 · 文档统计 · 特性清单(feature 文档标题聚类) · 模块地图(顶层包+文件数)
  · changelog 最近条目 · 待 LLM 填写的分析小节 (定位/架构/功能逻辑/演进/文档地图)

设计: 本脚本只产出「事实层」骨架 (全部来自 inventory/docs_index, 零臆造);
LLM 深读在其上填写分析层 — 与论文 DEEP_LEARNING_PROTOCOL 同一纪律:
  全文前后一致, 每个事实有仓库内出处 (文件路径)。
"""
import argparse, json, re, subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SRC = REPO / 'repos_src'
CARDS = REPO / 'extraction' / 'repo_cards'
INVENTORY = REPO / 'extraction' / 'repo_inventory.json'
DOCS_INDEX = REPO / 'extraction' / 'repo_docs_index.json'
DEEP = REPO / 'extraction' / 'deep'

# 特性文档按子目录/主题聚类 (路径第一段语义)
def feature_groups(feature_entries):
    groups = {}
    for e in feature_entries:
        parts = Path(e['path']).parts
        # docs/zh/features/megatron_moe/xxx.md → megatron_moe; docs/zh/features/xxx.md → (root)
        if 'features' in parts:
            i = parts.index('features')
            grp = parts[i + 1] if i + 1 < len(parts) - 1 else '(核心)'
        else:
            grp = '(其他)'
        groups.setdefault(grp, []).append(e['title'])
    return dict(sorted(groups.items(), key=lambda kv: -len(kv[1])))


def module_map(slug, limit=18):
    r = subprocess.run(['git', 'ls-tree', '--name-only', 'HEAD'],
                       cwd=SRC / slug, capture_output=True, text=True)
    top = [d for d in r.stdout.split() if not d.startswith('.')]
    rows = []
    for d in top:
        if (SRC / slug / d).is_dir():
            n = subprocess.run(['git', 'ls-tree', '-r', '--name-only', 'HEAD', '--', d],
                               cwd=SRC / slug, capture_output=True, text=True).stdout.split()
            rows.append((d + '/', len(n)))
        else:
            rows.append((d, None))
    return rows[:limit]


def changelog_head(entries, n=12):
    logs = [e for e in entries if e['type'] == 'changelog']
    if not logs:
        return []
    src = DOCS_OUT_PATH / logs[0]['slug'] / logs[0]['path']
    if not src.exists():
        return []
    heads = re.findall(r'^#{1,3}\s+(.+)$', src.read_text(encoding='utf-8', errors='ignore'), re.M)
    return heads[:n]


DOCS_OUT_PATH = REPO / 'extraction' / 'repo_docs'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('slug')
    args = ap.parse_args()
    slug = args.slug
    inv = {r['slug']: r for r in json.loads(INVENTORY.read_text(encoding='utf-8'))['repos']}[slug]
    docs = [e for e in json.loads(DOCS_INDEX.read_text(encoding='utf-8'))['docs'] if e['slug'] == slug]
    feats = [e for e in docs if e['type'] == 'feature']
    groups = feature_groups(feats)
    types = {}
    for e in docs:
        types[e['type']] = types.get(e['type'], 0) + 1

    ver_lines = '\n'.join(f'  - {k}: `{v}`' for k, v in inv['version_candidates'].items()) or '  - (未检出)'
    feat_lines = '\n'.join(f'| {g} | {len(ts)} | {"、".join(ts[:8])}{" …" if len(ts) > 8 else ""} |'
                           for g, ts in groups.items())
    mod_lines = '\n'.join(f'| `{d}` | {n if n is not None else "文件"} |' for d, n in module_map(slug))
    log_lines = '\n'.join(f'  - {h}' for h in changelog_head(docs)) or '  - (无 changelog)'

    # 双层写入 (extract_phase1 overwrite 教训): 骨架机械层可无限重生成;
    # deep/ 卡片只在不存在时播种, 已有人工/LLM 分析层绝不覆盖
    CARDS.mkdir(exist_ok=True)
    DEEP.mkdir(exist_ok=True)
    skel = CARDS / f'{slug}.md'
    out = skel
    out.write_text(f"""# 代码仓卡片 · {slug}

> 骨架由 repo_card.py 机械生成 (全部事实来自 inventory/docs_index);
> 「分析层」小节由 LLM 深读填写, 每个事实须带仓库内出处 (文件路径)。

## 0. 元信息

| 项 | 值 |
|---|---|
| 仓库 | {inv['url']} |
| 分支 / HEAD | `{inv['ref']}` @ `{inv['head'][:12]}` ({inv['commit_date'][:10]}) |
| 最新 tag | `{inv['latest_tag']}` |
| 版本候选 |
{ver_lines}
| 文件数 / md 文档 / 图片 | {inv['tree_files']} / {inv['docs_md']} / {inv['figures_total']} |
| 语言分布 | {json.dumps(inv['languages'], ensure_ascii=False)} |
| 备注 | {inv['note']} |

## 1. 定位 (LLM)

## 2. 架构与模块 (LLM, 基于下表 + 源码走读)

| 顶层路径 | 文件数 |
|---|---|
{mod_lines}

## 3. 功能逻辑 · 特性地图 (机械层: {len(feats)} 篇特性文档聚类)

| 分组 | 数量 | 特性 |
|---|---|---|
{feat_lines}

## 4. 关键特性深读 (LLM 选 3-6 篇, 图文联合)

## 5. 版本与演进

{log_lines}

## 6. 文档地图 (机械层)

| 类型 | 数量 |
|---|---|
{chr(10).join(f'| {t} | {n} |' for t, n in sorted(types.items(), key=lambda kv: -kv[1]))}

## 7. 证据与出处

- 文档收割: extraction/repo_docs/{slug}/ ({len(docs)} 篇)
- 清单: extraction/repo_inventory.json · extraction/repo_docs_index.json
""", encoding='utf-8')
    print(f'✓ skeleton: {out}')
    deep_out = DEEP / f'repo-{slug}.md'
    if not deep_out.exists():
        import shutil
        shutil.copyfile(skel, deep_out)
        print(f'✓ seeded: {deep_out}')
    else:
        print(f'· deep card exists, not overwritten: {deep_out}')


if __name__ == '__main__':
    main()
