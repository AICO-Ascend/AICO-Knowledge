#!/usr/bin/env python3
"""render_graph_growth.py — 知识图谱生长动图 (GIF)。

按 arXiv 发表月份（YYMM 权威派生）分批揭示节点，模拟"新知识进来 → 图谱生长"的效果。
布局在全图上一次性计算（seed 固定），帧间位置稳定，只有节点/边按时间出现；
最新一批节点高亮放大（脉冲），旧节点降为常态。

输出: docs/images/kb_topic_graph_growth_v2.gif
用法: python3 skills/bookshelf/render_graph_growth.py
"""
import json, re, sys
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import networkx as nx

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'paper-extraction'))
from render_kb_graph import TOPIC_COLORS, load, topic_graph  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
IMG = REPO / 'docs' / 'images'
OUT_GIF = IMG / 'kb_topic_graph_growth_v2.gif'

N_BATCHES = 12

CONCEPT_SLUGS = {p.stem for p in (Path(__file__).resolve().parents[2] / 'wiki' / 'concepts').glob('*.md')}


def pub_month(p):
    m = re.search(r'arxiv\.org/abs/(\d{2})(\d{2})\.', p.get('arxiv', ''))
    return f'20{m.group(1)}-{m.group(2)}' if m else '9999-99'


# 概念页 hub: 论文 tag → wiki/concepts 页 (别名归并)
TAG2CONCEPT = {
    'speculative': 'speculative-decoding', 'kv-cache': 'kv-cache', 'rl': 'rl',
    'training': 'training', 'moe': 'moe', 'multimodal': 'multimodal',
    'disaggregated-serving': 'disaggregated-serving', 'architecture': 'architecture',
    'long-context': 'long-context', 'sparse-attention': 'sparsity-axes',
}


def main():
    papers, *_ = load()
    G, tag_of = topic_graph(papers)
    # 概念 hub 节点: 边 = 论文 tag 命中概念页主题 (机械映射, 零臆造)
    concept_papers = defaultdict(list)
    for p in papers:
        for t in p.get('tags', []):
            c = TAG2CONCEPT.get(t, t)
            if c in CONCEPT_SLUGS:
                concept_papers[c].append(p['slug'])
    for c, slugs in concept_papers.items():
        hub = f'◇ {c}'
        G.add_node(hub, label=c, tag='__concept__', ntags=1)
        for s_ in slugs:
            G.add_edge(hub, s_, w=1)
    pos = nx.spring_layout(G, k=2.6, iterations=120, seed=42)

    months = {p['slug']: pub_month(p) for p in papers}
    CONCEPT_SLUGS_LOCAL = set(concept_papers)
    # 概念节点随其最早论文的月份出现
    for c, slugs in concept_papers.items():
        months[f'◇ {c}'] = min(months.get(s, '9999-99') for s in slugs)
    ordered = sorted(G.nodes(), key=lambda s: months.get(s, '9999-99'))
    batches = [ordered[i::N_BATCHES] for i in range(N_BATCHES)]  # 轮转分批, 每帧都有多点
    # 按时间序切等份更符合"生长"语义:
    batches = [ordered[i * len(ordered) // N_BATCHES:(i + 1) * len(ordered) // N_BATCHES]
               for i in range(N_BATCHES)]

    frames_dir = IMG / '_growth_frames'
    frames_dir.mkdir(exist_ok=True)
    tags = sorted({d['tag'] for _, d in G.nodes(data=True) if d['tag'] != '__concept__'})

    # ── 科技感调色板（暗色星空）──
    BG = '#060a1a'
    EDGE_C = '#3ec6ff'
    NEON = ['#3ec6ff', '#ff4fd8', '#7CFF6B', '#ffd166', '#b18cff', '#ff8a5c',
            '#4ff0e0', '#ff5c7a', '#a6ff4f', '#5c9dff', '#f0ff5c']
    TAG_NEON = {t: NEON[i % len(NEON)] for i, t in enumerate(tags)}
    # 星空背景（固定种子 → 帧间不动）
    import random
    rng = random.Random(7)
    xs_all = [xy[0] for xy in pos.values()]; ys_all = [xy[1] for xy in pos.values()]
    x0, x1 = min(xs_all), max(xs_all); y0, y1 = min(ys_all), max(ys_all)
    stars = [(rng.uniform(x0, x1), rng.uniform(y0, y1), rng.uniform(2, 9), rng.uniform(0.06, 0.25))
             for _ in range(260)]

    seen = set()
    paths = []
    for bi, batch in enumerate(batches + [[]]):
        seen.update(batch)
        fig, ax = plt.subplots(figsize=(16, 10), dpi=95)
        fig.patch.set_facecolor(BG)
        ax.set_facecolor(BG)
        ax.set_xlim(x0 - 0.08 * (x1 - x0), x1 + 0.08 * (x1 - x0))
        ax.set_ylim(y0 - 0.08 * (y1 - y0), y1 + 0.08 * (y1 - y0))
        # 星空
        for sx, sy, ss, sa in stars:
            ax.scatter([sx], [sy], s=ss, c='white', alpha=sa, linewidths=0)
        # 边: 霓虹微光
        sub_edges = [(u, v) for u, v in G.edges() if u in seen and v in seen]
        nx.draw_networkx_edges(G, pos, edgelist=sub_edges, ax=ax, width=0.7,
                               alpha=0.30, edge_color=EDGE_C)
        hot_edges = [(u, v) for u, v in sub_edges if u in batch or v in batch]
        nx.draw_networkx_edges(G, pos, edgelist=hot_edges, ax=ax, width=1.3,
                               alpha=0.75, edge_color=EDGE_C)
        # 概念 hub: 菱形 + 辉光
        hubs = [n for n in seen if G.nodes[n]['tag'] == '__concept__']
        for n in hubs:
            x, y = pos[n]
            is_new = n in batch
            for rr, aa in ([(2600, 0.05), (1500, 0.10), (760, 0.20)] if is_new
                           else [(1500, 0.04), (760, 0.08)]):
                ax.scatter([x], [y], s=rr, c='#ff3355', alpha=aa, linewidths=0, marker='D')
        nx.draw_networkx_nodes(G, pos, nodelist=hubs, ax=ax, node_color='#ff2244',
                               node_shape='D', node_size=[620 if n in batch else 380 for n in hubs],
                               alpha=1.0, edgecolors='#ffb3c0', linewidths=1.4)
        # 论文节点: 主题霓虹色 + 双层辉光
        for t in tags:
            ns = [n for n in seen if G.nodes[n]['tag'] == t]
            if not ns:
                continue
            col = TAG_NEON[t]
            new_ns = [n for n in ns if n in batch]
            old_ns = [n for n in ns if n not in batch]
            if old_ns:
                xy = [(pos[n][0], pos[n][1]) for n in old_ns]
                xs, ys = zip(*xy)
                ax.scatter(xs, ys, s=[340 + 90 * G.nodes[n]['ntags'] for n in old_ns],
                           c=col, alpha=0.08, linewidths=0)
                nx.draw_networkx_nodes(G, pos, nodelist=old_ns, ax=ax, node_color=col,
                                       node_size=[110 + 45 * G.nodes[n]['ntags'] for n in old_ns],
                                       alpha=0.85, edgecolors=BG, linewidths=0.4)
            if new_ns:
                xy = [(pos[n][0], pos[n][1]) for n in new_ns]
                xs, ys = zip(*xy)
                ax.scatter(xs, ys, s=[1500 + 200 * G.nodes[n]['ntags'] for n in new_ns],
                           c=col, alpha=0.16, linewidths=0)
                ax.scatter(xs, ys, s=[520 + 90 * G.nodes[n]['ntags'] for n in new_ns],
                           c=col, alpha=0.30, linewidths=0)
                nx.draw_networkx_nodes(G, pos, nodelist=new_ns, ax=ax, node_color=col,
                                       node_size=[230 + 70 * G.nodes[n]['ntags'] for n in new_ns],
                                       alpha=1.0, edgecolors='white', linewidths=1.5)
        # 标签: 白字 + 微光晕
        nx.draw_networkx_labels(G, pos, {n: G.nodes[n]['label'] for n in seen},
                                font_size=6.4, ax=ax, font_family='DejaVu Sans',
                                font_color='#dfe8ff')
        newest_month = months.get(batch[-1], '') if batch else 'now'
        ax.set_title(f'AICO-Knowledge · Knowledge Graph Growth\n'
                     f'{len(seen)}/{G.number_of_nodes()} nodes  ·  +{len(batch)} new  ·  latest {newest_month}',
                     fontsize=14, pad=14, color='#eaf2ff', fontweight='bold')
        ax.axis('off')
        plt.tight_layout()
        fp = frames_dir / f'f{bi:02d}.png'
        fig.savefig(fp, bbox_inches='tight', facecolor=BG)
        plt.close(fig)
        paths.append(fp)
        print(f'  frame {bi + 1}/{len(batches) + 1}: {len(seen)} nodes')

    from PIL import Image
    imgs = [Image.open(p) for p in paths]
    durations = [220] * (len(imgs) - 1) + [1600]  # 末帧停留
    imgs[0].save(OUT_GIF, save_all=True, append_images=imgs[1:],
                 duration=durations, loop=0, optimize=True)
    for p in paths:
        p.unlink()
    frames_dir.rmdir()
    print(f'✓ {OUT_GIF} ({len(imgs)} 帧, {OUT_GIF.stat().st_size // 1024} KB)')


if __name__ == '__main__':
    main()
