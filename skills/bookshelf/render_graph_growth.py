#!/usr/bin/env python3
"""render_graph_growth.py — 知识图谱生长动图 (GIF)。

按 arXiv 发表月份（YYMM 权威派生）分批揭示节点，模拟"新知识进来 → 图谱生长"的效果。
布局在全图上一次性计算（seed 固定），帧间位置稳定，只有节点/边按时间出现；
最新一批节点高亮放大（脉冲），旧节点降为常态。

输出: docs/images/kb_topic_graph_growth.gif
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
OUT_GIF = IMG / 'kb_topic_graph_growth.gif'

N_BATCHES = 12


def pub_month(p):
    m = re.search(r'arxiv\.org/abs/(\d{2})(\d{2})\.', p.get('arxiv', ''))
    return f'20{m.group(1)}-{m.group(2)}' if m else '9999-99'


def main():
    papers, *_ = load()
    G, tag_of = topic_graph(papers)
    pos = nx.spring_layout(G, k=2.6, iterations=120, seed=42)

    months = {p['slug']: pub_month(p) for p in papers}
    ordered = sorted(G.nodes(), key=lambda s: months.get(s, '9999-99'))
    batches = [ordered[i::N_BATCHES] for i in range(N_BATCHES)]  # 轮转分批, 每帧都有多点
    # 按时间序切等份更符合"生长"语义:
    batches = [ordered[i * len(ordered) // N_BATCHES:(i + 1) * len(ordered) // N_BATCHES]
               for i in range(N_BATCHES)]

    frames_dir = IMG / '_growth_frames'
    frames_dir.mkdir(exist_ok=True)
    tags = sorted({d['tag'] for _, d in G.nodes(data=True)})
    seen = set()
    labeled = set()
    paths = []
    for bi, batch in enumerate(batches + [[]]):
        prev_seen = set(seen)
        seen.update(batch)
        fig, ax = plt.subplots(figsize=(16, 11), dpi=90)
        fig.patch.set_facecolor('#FAFAF8')
        ax.set_facecolor('#FAFAF8')
        sub_edges = [(u, v) for u, v in G.edges() if u in seen and v in seen]
        widths = [G[u][v]['w'] * 0.5 for u, v in sub_edges]
        nx.draw_networkx_edges(G, pos, edgelist=sub_edges, ax=ax, width=widths,
                               alpha=0.25, edge_color='#888888')
        for t in tags:
            ns = [n for n in seen if G.nodes[n]['tag'] == t]
            if not ns:
                continue
            sizes = [150 + 60 * G.nodes[n]['ntags'] for n in ns]
            # networkx 不支持逐点 alpha 列表稳定渲染 → 新旧分两次画
            new_ns = [n for n in ns if n in batch]
            old_ns = [n for n in ns if n not in batch]
            if old_ns:
                nx.draw_networkx_nodes(G, pos, nodelist=old_ns, ax=ax,
                                       node_color=TOPIC_COLORS.get(t, '#999'),
                                       node_size=[150 + 60 * G.nodes[n]['ntags'] for n in old_ns],
                                       alpha=0.55, edgecolors='white', linewidths=1.0)
            if new_ns:
                nx.draw_networkx_nodes(G, pos, nodelist=new_ns, ax=ax,
                                       node_color=TOPIC_COLORS.get(t, '#999'),
                                       node_size=[260 + 80 * G.nodes[n]['ntags'] for n in new_ns],
                                       alpha=0.95, edgecolors='#C7000B', linewidths=1.8,
                                       label=t if t not in labeled else None)
                labeled.add(t)
        nx.draw_networkx_labels(G, pos, {n: G.nodes[n]['label'] for n in seen},
                                font_size=6.5, ax=ax, font_family='DejaVu Sans')
        newest_month = months.get(batch[-1], '') if batch else '现在'
        ax.set_title(f'AICO-Knowledge Topic Graph Growth · {len(seen)}/{G.number_of_nodes()} papers'
                     f' (+{len(batch)} new · latest {newest_month})', fontsize=13, pad=12)
        ax.axis('off')
        plt.tight_layout()
        fp = frames_dir / f'f{bi:02d}.png'
        fig.savefig(fp, bbox_inches='tight', facecolor=fig.get_facecolor())
        plt.close(fig)
        paths.append(fp)
        print(f'  frame {bi + 1}/{len(batches) + 1}: {len(seen)} nodes')

    from PIL import Image
    imgs = [Image.open(p) for p in paths]
    durations = [500] * (len(imgs) - 1) + [2500]  # 末帧停留
    imgs[0].save(OUT_GIF, save_all=True, append_images=imgs[1:],
                 duration=durations, loop=0, optimize=True)
    for p in paths:
        p.unlink()
    frames_dir.rmdir()
    print(f'✓ {OUT_GIF} ({len(imgs)} 帧, {OUT_GIF.stat().st_size // 1024} KB)')


if __name__ == '__main__':
    main()
