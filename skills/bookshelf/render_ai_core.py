#!/usr/bin/env python3
"""render_ai_core.py — AI Core 数据通路动图 (AscendInfra 硬件节)。

自绘 910B AI Core 框图 + 数据沿正确路线流动的动画:
  Cube 流   GM → L2 → L1 → L0A/L0B → CUBE → L0C → FixPipe → GM
  Vector 流 GM → L2 → UB → VECTOR → MTE3 → GM
  MTE1 流   L1 → UB
三阶段横幅轮转 (LOAD → COMPUTE → WRITE-BACK) + CUBE/VECTOR 风扇转动。
风格: 素色工程图 (白底/灰线/扁平色块), 参考昇腾官方可视化页面版式。
输出: docs/images/ai_core_datapath.gif
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.patches import FancyBboxPatch, Circle, FancyArrowPatch
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / 'docs/images/ai_core_datapath.gif'

BG = '#ffffff'
INK = '#1f2937'        # 主文字
SUB = '#6b7280'        # 次要文字
EDGE = '#9ca3af'       # 框线灰
WIRE = '#d1d5db'       # 静置走线
FILL = '#f8fafc'       # 盒填充
FILL_CORE = '#eef2f7'  # 容器填充
C_CUBE = '#2563eb'     # Cube 流 (素蓝)
C_VEC = '#0d9488'      # Vector 流 (素青)
C_MTE1 = '#b45309'     # MTE1 (素棕)

BOXES = {
    'GM':      ((0.4, 3.2, 2.0, 2.6),  'GM\nHBM/DDR'),
    'L2':      ((2.9, 3.7, 1.6, 1.6),  'L2\ncache'),
    'L1':      ((5.5, 6.6, 1.9, 1.5),  'L1\n512KB'),
    'L0A':     ((8.0, 6.9, 1.4, 1.2),  'L0A\n64KB'),
    'L0B':     ((9.8, 6.9, 1.4, 1.2),  'L0B\n64KB'),
    'CUBE':    ((8.0, 4.7, 3.2, 1.7),  'CUBE\n16×16×16'),
    'L0C':     ((8.0, 3.1, 3.2, 1.2),  'L0C\n128KB'),
    'FixPipe': ((11.7, 3.1, 1.7, 1.2), 'FixPipe'),
    'UB':      ((5.5, 3.1, 1.9, 1.5),  'UB\n192KB'),
    'VEC':     ((8.0, 1.0, 3.2, 1.5),  'VECTOR'),
    'Scalar':  ((11.7, 5.0, 1.7, 1.1), 'Scalar'),
}

CUBE_PATH = [(1.4,4.5),(2.4,4.5),(3.7,4.5),(4.5,4.5),(4.9,4.5),(4.9,7.35),
             (5.5,7.35),(7.4,7.35),(8.7,7.5),(8.7,6.4),(9.6,5.55),(9.6,4.3),
             (9.6,3.7),(11.2,3.7),(12.55,3.7),(13.4,3.7),(14.9,3.7),(14.9,0.85),
             (5.15,0.85),(1.4,0.85),(1.4,3.2),(1.4,4.5)]
VEC_PATH = [(1.4,5.1),(2.4,5.1),(3.7,5.1),(4.5,5.1),(4.75,5.1),(4.75,3.85),
            (5.5,3.85),(6.45,3.85),(7.4,3.85),(7.7,3.85),(7.7,1.75),(8.0,1.75),
            (9.6,1.75),(11.2,1.75),(14.9,1.75),(14.9,0.85),(5.15,0.85),
            (1.4,0.85),(1.4,3.2),(1.4,5.1)]
MTE1_PATH = [(6.45,6.6),(6.45,4.6)]
STATIC_LINKS = [[(7.4,7.35),(10.5,7.5)], [(10.5,6.9),(10.5,6.4)]]

STAGES = [
    ('STAGE 1/3 · LOAD — MTE2/MTE1 : GM → L2 → L1 · UB',
     [(0, range(0, 9)), (1, range(0, 8)), (2, range(0, 1))]),
    ('STAGE 2/3 · COMPUTE — CUBE (L0A×L0B→L0C) · VECTOR (UB)',
     [(0, range(9, 14)), (1, range(8, 13)), (2, range(0))]),
    ('STAGE 3/3 · WRITE-BACK — FixPipe / MTE3 → GM',
     [(0, range(14, 21)), (1, range(13, 19)), (2, range(0))]),
]
PATHS = [CUBE_PATH, VEC_PATH, MTE1_PATH]
PATH_COLORS = [C_CUBE, C_VEC, C_MTE1]
PATH_DOTS = [6, 5, 2]
PATH_SPEED = [0.55, 0.5, 0.35]

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
    i = np.searchsorted(cum, d, side='right') - 1
    i = min(i, len(pts) - 2)
    t = (d - cum[i]) / max(cum[i + 1] - cum[i], 1e-9)
    return pts[i] + t * (pts[i + 1] - pts[i])


def draw_fan(ax, cx, cy, r, ang, color):
    ax.add_patch(Circle((cx, cy), r * 1.3, fc='white', ec=color, lw=1.4, zorder=7))
    for k in range(3):
        a = ang + k * 2 * np.pi / 3
        ax.plot([cx, cx + r * np.cos(a)], [cy, cy + r * np.sin(a)],
                color=color, lw=2.6, solid_capstyle='round', zorder=8)
    ax.add_patch(Circle((cx, cy), r * 0.22, fc=color, ec='none', zorder=8))


fig = plt.figure(figsize=(11.5, 6.5), dpi=90, facecolor=BG)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 16); ax.set_ylim(0, 9); ax.axis('off')
ax.set_facecolor(BG)

arcs = [arc_points(p) for p in PATHS]


def render(f):
    ax.clear()
    ax.set_xlim(0, 16); ax.set_ylim(0, 9); ax.axis('off')
    ax.set_facecolor(BG)
    stage = f // STAGE_LEN

    # AI Core 容器
    ax.add_patch(FancyBboxPatch((5.0, 0.4), 10.6, 8.2, boxstyle='round,pad=0.08',
                                fc=FILL_CORE, ec=EDGE, lw=1.2, zorder=1))
    ax.text(15.35, 8.28, 'AI Core ×N  (Ascend 910B)', color=SUB,
            fontsize=11, family='monospace', weight='bold', ha='right', zorder=3)

    # 静态连线 (L1→L0B→CUBE)
    for link in STATIC_LINKS:
        ax.plot([p[0] for p in link], [p[1] for p in link], color=WIRE,
                lw=1.1, zorder=2)

    # 通路: 当前阶段素色加深, 其余浅灰
    active = {(pi, si) for pi, rng_ in STAGES[stage][1] for si in rng_}
    for pi, (wps, color) in enumerate(zip(PATHS, PATH_COLORS)):
        for si in range(len(wps) - 1):
            p0, p1 = wps[si], wps[si + 1]
            on = (pi, si) in active
            ax.plot([p0[0], p1[0]], [p0[1], p1[1]],
                    color=color if on else WIRE,
                    lw=2.0 if on else 1.1, alpha=0.9 if on else 1.0,
                    solid_capstyle='round', zorder=2)

    # 方向箭头 (关键段中点, 沿流向)
    ARROWS = [(0, 1), (0, 4), (0, 7), (0, 9), (0, 11), (0, 13), (0, 16), (0, 19),
              (1, 1), (1, 5), (1, 10), (1, 13), (1, 18), (2, 0)]
    for pi, si in ARROWS:
        wps = PATHS[pi]
        p0 = np.array(wps[si]); p1 = np.array(wps[si + 1])
        mid = (p0 + p1) / 2
        d = p1 - p0
        n = np.hypot(*d) or 1
        on = any((pi, s) in active for s in range(si, si + 1))
        ax.annotate('', xy=mid + d / n * 0.12, xytext=mid - d / n * 0.12,
                    arrowprops=dict(arrowstyle='-|>', lw=1.4,
                                    color=PATH_COLORS[pi] if on else EDGE),
                    zorder=5)

    # 方框 (扁平, 白底灰边)
    for name, ((x, y, w, h), label) in BOXES.items():
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.05',
                                    fc=FILL, ec=EDGE, lw=1.4, zorder=4))
        lines = label.split('\n')
        ax.text(x + w / 2, y + h / 2 + (0.18 if len(lines) > 1 else 0), lines[0],
                color=INK, fontsize=11, family='monospace', weight='bold',
                ha='center', va='center', zorder=5)
        if len(lines) > 1:
            ax.text(x + w / 2, y + h / 2 - 0.28, lines[1], color=SUB,
                    fontsize=7.5, family='monospace', ha='center', va='center', zorder=5)

    # 引擎标签
    for txt, (tx, ty) in [('MTE2', (4.30, 6.05)), ('MTE2', (4.30, 3.05)),
                          ('MTE1', (6.75, 5.55)), ('MTE3', (12.9, 2.10)),
                          ('FixPipe out', (13.9, 4.05))]:
        ax.text(tx, ty, txt, color=SUB, fontsize=8, family='monospace',
                ha='center', style='italic', zorder=5)

    # 风扇 (CUBE / VECTOR 转动)
    ang = f * 0.30
    draw_fan(ax, 10.62, 5.12, 0.34, ang, C_CUBE)
    draw_fan(ax, 10.75, 1.38, 0.34, -ang * 1.3, C_VEC)

    # 流动数据包 (小圆点 + 短尾迹)
    for pi, ((pts, cum, total), color, nd, spd) in enumerate(
            zip(arcs, PATH_COLORS, PATH_DOTS, PATH_SPEED)):
        for k in range(nd):
            d = f * spd + k * total / nd
            p = pos_on(pts, cum, total, d)
            trail = [pos_on(pts, cum, total, d - dt) for dt in (0.9, 0.5)]
            ax.plot([trail[0][0], trail[1][0], p[0]],
                    [trail[0][1], trail[1][1], p[1]],
                    color=color, lw=1.4, alpha=0.45, zorder=6)
            ax.scatter(*p, s=42, c=color, ec='white', lw=0.8, zorder=7)

    # 标题 + 阶段横幅
    ax.text(0.45, 8.55, 'AI Core Data Path — Ascend 910B', color=INK,
            fontsize=15, family='monospace', weight='bold', zorder=8)
    ax.text(0.45, 8.12, 'MTE engines move data · Cube/Vector compute',
            color=SUB, fontsize=8.5, family='monospace', zorder=8)
    banner = STAGES[stage][0]
    ax.add_patch(FancyBboxPatch((0.35, 0.10), 9.2, 0.62, boxstyle='round,pad=0.06',
                                fc='#f1f5f9', ec=EDGE, lw=1.0, zorder=8))
    ax.text(0.62, 0.41, banner, color=INK, fontsize=9.5,
            family='monospace', weight='bold', va='center', zorder=9)


anim = FuncAnimation(fig, render, frames=N_FRAMES)
OUT.parent.mkdir(parents=True, exist_ok=True)
anim.save(OUT, writer=PillowWriter(fps=14))
print(f'✓ {OUT}  {OUT.stat().st_size/1e6:.1f} MB · {N_FRAMES} 帧')
