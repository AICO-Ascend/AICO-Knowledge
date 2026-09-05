#!/usr/bin/env python3
"""render_ai_core.py — AI Core 数据通路动图 (AscendInfra 硬件节)。

版式参考昇腾官方可视化页面: 严格网格 · 左→右单向数据流 · 代际标签页 ·
Cube/Vector 双车道分区 · 数据包到右缘淡出(不写回绕总线) · 风扇转动。
  Cube 车道   GM → L2 → L1 → L0A/L0B → CUBE → L0C → FixPipe → GM
  Vector 车道 GM → L2 → UB → VECTOR → MTE3 → GM
  MTE1       L1 → UB
输出: docs/images/ai_core_datapath.gif
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.patches import FancyBboxPatch, Circle
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / 'docs/images/ai_core_datapath.gif'

BG = '#ffffff'
INK = '#1f2937'
SUB = '#6b7280'
FAINT = '#9ca3af'
EDGE = '#c7d0dd'       # 框线
WIRE = '#d6dde8'       # 静置走线
FILL = '#ffffff'
CORE_FILL = '#f7f9fc'  # 容器
LANE_CUBE = '#f4f7fd'  # Cube 车道
LANE_VEC = '#f3faf8'   # Vector 车道
C_CUBE = '#4472c4'     # 素蓝
C_VEC = '#2e9e8f'      # 素青
C_MTE1 = '#b45309'     # 素棕

FONT = 'DejaVu Sans'

# (x, y, w, h, fill, edge)
BOXES = {
    'GM':      (0.5, 4.6, 2.0, 2.0, '#f8fafc', '#94a3b8', 'GM\nHBM / DDR'),
    'L2':      (3.1, 4.9, 1.4, 1.4, '#f8fafc', '#94a3b8', 'L2\ncache'),
    'L1':      (5.5, 5.95, 1.4, 1.3, FILL, EDGE, 'L1\n512KB'),
    'L0A':     (7.5, 6.85, 1.3, 0.7, FILL, EDGE, 'L0A 64KB'),
    'L0B':     (7.5, 5.55, 1.3, 0.7, FILL, EDGE, 'L0B 64KB'),
    'CUBE':    (9.4, 5.9, 2.0, 1.4, '#eff4fc', '#9db8dd', 'CUBE\n16×16×16'),
    'L0C':     (12.0, 5.95, 1.4, 1.3, FILL, EDGE, 'L0C\n128KB'),
    'FixPipe': (13.9, 5.95, 1.4, 1.3, FILL, EDGE, 'FixPipe'),
    'UB':      (5.5, 2.6, 1.4, 1.3, FILL, EDGE, 'UB\n192KB'),
    'VEC':     (9.4, 2.6, 2.0, 1.3, '#edf8f5', '#8cc8bb', 'VECTOR'),
    'Scalar':  (13.9, 2.6, 1.4, 1.3, FILL, EDGE, 'Scalar'),
}

CUBE_PATH = [(1.5,5.6),(2.5,5.6),(3.8,5.6),(4.5,5.6),(5.15,5.6),(5.15,6.6),
             (5.5,6.6),(6.9,6.6),(7.15,6.6),(7.15,7.2),(7.5,7.2),(8.8,7.2),
             (9.15,7.2),(9.15,6.6),(10.4,6.6),(11.4,6.6),(12.7,6.6),(13.4,6.6),
             (14.6,6.6),(15.3,6.6),(15.95,6.6)]
VEC_PATH = [(1.5,5.6),(2.5,5.6),(3.8,5.6),(4.5,5.6),(5.15,5.6),(5.15,3.25),
            (5.5,3.25),(6.2,3.25),(6.9,3.25),(9.4,3.25),(10.4,3.25),(11.4,3.25),
            (11.9,3.25),(11.9,1.9),(15.3,1.9),(15.95,1.9)]
MTE1_PATH = [(6.2,5.95),(6.2,3.9)]
STATIC_LINKS = [[(7.15,6.6),(7.15,5.9),(7.5,5.9)], [(8.8,5.9),(9.15,5.9),(9.15,6.6)]]

STAGES = [
    ('STAGE 1/3  LOAD · MTE2/MTE1 : GM → L2 → L1 / UB',
     [(0, range(0, 11)), (1, range(0, 8)), (2, range(0, 1))]),
    ('STAGE 2/3  COMPUTE · CUBE (L0A×L0B→L0C) · VECTOR (UB)',
     [(0, range(11, 17)), (1, range(8, 11)), (2, range(0))]),
    ('STAGE 3/3  WRITE-BACK · FixPipe / MTE3 → GM',
     [(0, range(17, 20)), (1, range(11, 15)), (2, range(0))]),
]
PATHS = [CUBE_PATH, VEC_PATH, MTE1_PATH]
PATH_COLORS = [C_CUBE, C_VEC, C_MTE1]
PATH_DOTS = [6, 5, 2]
PATH_SPEED = [0.50, 0.46, 0.32]

ARROWS = [(0, 1), (0, 4), (0, 6), (0, 9), (0, 13), (0, 15), (0, 17), (0, 19),
          (1, 1), (1, 5), (1, 8), (1, 12), (1, 13), (2, 0)]

N_FRAMES = 96
STAGE_LEN = N_FRAMES // 3


def arc_points(wps):
    pts = np.array(wps, float)
    seg = np.diff(pts, axis=0)
    L = np.hypot(seg[:, 0], seg[:, 1])
    cum = np.concatenate([[0], np.cumsum(L)])
    return pts, cum, cum[-1]


def pos_on(pts, cum, total, d):
    d = d % total
    i = min(np.searchsorted(cum, d, side='right') - 1, len(pts) - 2)
    t = (d - cum[i]) / max(cum[i + 1] - cum[i], 1e-9)
    return pts[i] + t * (pts[i + 1] - pts[i])


def draw_fan(ax, cx, cy, r, ang, color):
    ax.add_patch(Circle((cx, cy), r * 1.3, fc='white', ec=color, lw=1.3, zorder=7))
    for k in range(3):
        a = ang + k * 2 * np.pi / 3
        ax.plot([cx, cx + r * np.cos(a)], [cy, cy + r * np.sin(a)],
                color=color, lw=2.4, solid_capstyle='round', zorder=8)
    ax.add_patch(Circle((cx, cy), r * 0.22, fc=color, ec='none', zorder=8))


fig = plt.figure(figsize=(11.5, 6.5), dpi=90, facecolor=BG)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 16); ax.set_ylim(0, 9); ax.axis('off')

arcs = [arc_points(p) for p in PATHS]


def render(f):
    ax.clear()
    ax.set_xlim(0, 16); ax.set_ylim(0, 9); ax.axis('off')
    ax.set_facecolor(BG)
    stage = f // STAGE_LEN

    # 标题区
    ax.text(0.45, 8.55, 'Ascend AI Core — Data Path', color=INK,
            fontsize=16, family=FONT, weight='bold', zorder=10)
    ax.text(0.45, 8.14, 'MTE moves data · Cube & Vector compute',
            color=SUB, fontsize=9, family=FONT, zorder=10)

    # AI Core 容器 + 车道分区
    ax.add_patch(FancyBboxPatch((4.95, 1.2), 10.85, 7.25, boxstyle='round,pad=0.06',
                                fc=CORE_FILL, ec=EDGE, lw=1.2, zorder=1))
    ax.add_patch(FancyBboxPatch((5.15, 5.35), 10.45, 2.35, boxstyle='round,pad=0.04',
                                fc=LANE_CUBE, ec='none', zorder=1.2))
    ax.add_patch(FancyBboxPatch((5.15, 2.3), 10.45, 2.2, boxstyle='round,pad=0.04',
                                fc=LANE_VEC, ec='none', zorder=1.2))
    ax.text(5.32, 5.44, 'CUBE LANE', color='#9db8dd', fontsize=7, family=FONT,
            weight='bold', zorder=1.3)
    ax.text(5.32, 2.40, 'VECTOR LANE', color='#8cc8bb', fontsize=7, family=FONT,
            weight='bold', zorder=1.3)

    # 代际标签页 (910B 现役)
    for i, tab in enumerate(['910_95 / A5', '910B / A2', '310P / 910A']):
        x = 5.25 + i * 1.8
        on = (i == 1)
        ax.add_patch(FancyBboxPatch((x, 7.82), 1.65, 0.44, boxstyle='round,pad=0.03',
                                    fc='#e8edf5' if on else 'white',
                                    ec='#94a3b8' if on else '#e2e8f0', lw=1.0, zorder=3))
        ax.text(x + 0.825, 8.04, tab, color=INK if on else FAINT, fontsize=7.5,
                family=FONT, ha='center', va='center',
                weight='bold' if on else 'normal', zorder=3)
    ax.text(15.55, 8.04, 'AI Core ×N', color=SUB, fontsize=10, family=FONT,
            weight='bold', ha='right', va='center', zorder=3)

    # 通路: 当前阶段着色, 其余浅灰
    active = {(pi, si) for pi, rng_ in STAGES[stage][1] for si in rng_}
    for pi, (wps, color) in enumerate(zip(PATHS, PATH_COLORS)):
        for si in range(len(wps) - 1):
            p0, p1 = wps[si], wps[si + 1]
            on = (pi, si) in active
            ax.plot([p0[0], p1[0]], [p0[1], p1[1]],
                    color=color if on else WIRE, lw=2.0 if on else 1.1,
                    solid_capstyle='round', zorder=2)
    for link in STATIC_LINKS:
        ax.plot([p[0] for p in link], [p[1] for p in link], color=WIRE, lw=1.1, zorder=2)

    # 方向箭头
    for pi, si in ARROWS:
        wps = PATHS[pi]
        p0 = np.array(wps[si]); p1 = np.array(wps[si + 1])
        mid = (p0 + p1) / 2
        d = p1 - p0
        n = np.hypot(*d) or 1
        ax.annotate('', xy=mid + d / n * 0.11, xytext=mid - d / n * 0.11,
                    arrowprops=dict(arrowstyle='-|>', lw=1.3,
                                    color=PATH_COLORS[pi] if (pi, si) in active else '#b6bfcd'),
                    zorder=5)

    # 方框
    for name, (x, y, w, h, fc, ec, label) in BOXES.items():
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.04',
                                    fc=fc, ec=ec, lw=1.3, zorder=4))
        lines = label.split('\n')
        if len(lines) > 1:
            ax.text(x + w / 2, y + h / 2 + 0.16, lines[0], color=INK, fontsize=10.5,
                    family=FONT, weight='bold', ha='center', va='center', zorder=5)
            ax.text(x + w / 2, y + h / 2 - 0.22, lines[1], color=SUB, fontsize=7.5,
                    family=FONT, ha='center', va='center', zorder=5)
        else:
            ax.text(x + w / 2, y + h / 2, lines[0], color=INK, fontsize=8.5,
                    family=FONT, weight='bold', ha='center', va='center', zorder=5)

    # 引擎/出口标签
    for txt, (tx, ty) in [('MTE2', (4.62, 5.92)), ('MTE1', (6.48, 4.9)),
                          ('MTE3', (13.6, 2.14)), ('→ GM', (15.52, 6.88)),
                          ('→ GM', (15.45, 2.18))]:
        ax.text(tx, ty, txt, color=FAINT, fontsize=7.5, family=FONT,
                ha='center', style='italic', zorder=5)

    # 风扇
    ang = f * 0.28
    draw_fan(ax, 11.08, 6.10, 0.26, ang, C_CUBE)
    draw_fan(ax, 10.98, 2.98, 0.26, -ang * 1.3, C_VEC)

    # 数据包 (端点淡入淡出)
    for pi, ((pts, cum, total), color, nd, spd) in enumerate(
            zip(arcs, PATH_COLORS, PATH_DOTS, PATH_SPEED)):
        for k in range(nd):
            d = f * spd + k * total / nd
            p = pos_on(pts, cum, total, d)
            a = max(0.0, min(1.0, d / 0.9, (total - d) / 0.9))
            p_tr = pos_on(pts, cum, total, d - 0.55)
            ax.plot([p_tr[0], p[0]], [p_tr[1], p[1]], color=color,
                    lw=1.5, alpha=0.4 * a, zorder=6)
            ax.scatter(*p, s=48, c=color, ec='white', lw=0.9, alpha=a, zorder=7)

    # 阶段横幅 + 阶段指示点
    ax.add_patch(FancyBboxPatch((0.4, 0.22), 8.3, 0.58, boxstyle='round,pad=0.05',
                                fc='#f1f5f9', ec=EDGE, lw=1.0, zorder=8))
    ax.text(0.66, 0.51, STAGES[stage][0], color=INK, fontsize=8.8,
            family=FONT, weight='bold', va='center', zorder=9)
    for i in range(3):
        ax.add_patch(Circle((7.95 + i * 0.22, 0.51), 0.055,
                            fc=INK if i == stage else '#d1d5db', ec='none', zorder=9))


anim = FuncAnimation(fig, render, frames=N_FRAMES)
OUT.parent.mkdir(parents=True, exist_ok=True)
anim.save(OUT, writer=PillowWriter(fps=14))
print(f'✓ {OUT}  {OUT.stat().st_size/1e6:.1f} MB · {N_FRAMES} 帧')
