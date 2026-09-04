#!/usr/bin/env python3
"""render_pipeline_3domain.py — 三域知识流水线 PNG (README 头图)。

matplotlib 绘制（英文标签——本机无 CJK 字体，中文会乱码）。
输出: docs/images/kb_pipeline_3domain.png
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / 'docs' / 'images' / 'kb_pipeline_3domain.png'

LANES = [
    ('PAPERS', '#B2182B', 'arXiv · 69 papers', [
        'bib source', 'sync &\ndownload', 'extract\ntext+figs', 'crop\nvisuals',
        'M3 vision\ncaptions', 'LaTeX\nformulas', 'Lint gate\n(audit→fix)', 'deep-read\nqueue']),
    ('REPOS', '#0B6E4F', 'gitcode/github · 134 repos', [
        'repos list\n(.txt)', 'sparse fetch\n+ lineage', 'harvest docs\n(21,954)', 'repo cards\n2-layer', 'M3 7-section\ndeep-read\n(1,719)', 'deep index\n+ links']),
    ('WEB', '#B7860B', 'docs.vllm.ai / hiascend', [
        'webs list\n(.txt)', '3-route fetch\n(.md / SSR / SPA)', 'M3 deep-read\nverbatim tables', 'web index\n(registry)']),
]

fig, ax = plt.subplots(figsize=(16.5, 8.2), dpi=130)
fig.patch.set_facecolor('#FAFAF8')
ax.set_facecolor('#FAFAF8')
ax.set_xlim(0, 100)
ax.set_ylim(0, 62)
ax.axis('off')

ax.text(2, 59.5, 'AICO-Knowledge — Three-Domain Knowledge Pipelines',
        fontsize=17, fontweight='bold', color='#1d2129')
ax.text(2, 56.6, 'papers / repos / web · same discipline: mechanical layer zero-invention, '
                 'LLM deep-reads with provenance, registry-first',
        fontsize=10.5, color='#86909c')

BW, BH = 8.6, 7.2
y_lanes = [42, 26, 10]
for (name, color, subtitle, steps), y0 in zip(LANES, y_lanes):
    lane = FancyBboxPatch((1.2, y0 - 3.4), 97.6, BH + 6.4, boxstyle='round,pad=0.4',
                          fill=False, edgecolor='#e0e1e6', linestyle='--', linewidth=1.1)
    ax.add_patch(lane)
    ax.text(3, y0 + BH / 2 + 2.2, name, fontsize=13, fontweight='bold', color=color)
    ax.text(3, y0 + BH / 2 + 0.4, subtitle, fontsize=9, color='#86909c')
    n = len(steps)
    total_w = 80.0
    gap = (total_w - n * BW) / (n - 1) if n > 1 else 0
    x = 14.5
    for i, s in enumerate(steps):
        box = FancyBboxPatch((x, y0), BW, BH, boxstyle='round,pad=0.35',
                             facecolor='white', edgecolor='#c9cdd4', linewidth=1.2)
        ax.add_patch(box)
        ax.text(x + BW / 2, y0 + BH / 2, s, ha='center', va='center',
                fontsize=9.6, color='#1d2129', linespacing=1.35)
        if i < n - 1:
            ax.add_patch(FancyArrowPatch((x + BW + 0.4, y0 + BH / 2), (x + BW + gap - 0.4, y0 + BH / 2),
                                         arrowstyle='-|>', mutation_scale=13, color='#8a8f99'))
        x += BW + gap
    # lane → sink arrow
    ax.add_patch(FancyArrowPatch((57, y0 - 3.6), (57, y0 - 6.2),
                                 arrowstyle='-|>', mutation_scale=13, color='#8a8f99'))

# sink row
sink = FancyBboxPatch((30, 0.6), 26, 6.4, boxstyle='round,pad=0.4',
                      facecolor='#C7000B', edgecolor='none')
ax.add_patch(sink)
ax.text(43, 3.8, 'extraction/  KB (wiki layer)', ha='center', va='center',
        fontsize=12, fontweight='bold', color='white')
ax.add_patch(FancyArrowPatch((56.5, 3.8), (61.5, 3.8), arrowstyle='-|>',
                             mutation_scale=13, color='#8a8f99'))
shelf = FancyBboxPatch((62, 0.6), 34, 6.4, boxstyle='round,pad=0.4',
                       facecolor='white', edgecolor='#c9cdd4', linewidth=1.2)
ax.add_patch(shelf)
ax.text(79, 4.6, 'bookshelf — 3 entries', ha='center', fontsize=10.5,
        fontweight='bold', color='#1d2129')
ax.text(79, 2.4, 'SHELF.md · AscendInfra · NvidiaInfra', ha='center',
        fontsize=9.5, color='#86909c')

plt.tight_layout()
fig.savefig(OUT, bbox_inches='tight', facecolor=fig.get_facecolor())
print(f'✓ {OUT} ({OUT.stat().st_size // 1024} KB)')
