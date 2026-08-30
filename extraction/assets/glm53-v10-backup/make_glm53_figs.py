#!/usr/bin/env python3
"""make_figs.py — 为 GLM 5.3-flash deck 自制 13 张数据驱动插图。

图全部基于 paste-cache 里描述的真实数据 / 架构 / 公式绘制,
不依赖外部 wiki.huawei.com 图床。中文字体走本地 NotoSansCJKsc。
"""
from __future__ import annotations
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mp
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Circle
from matplotlib.lines import Line2D
import numpy as np
from pathlib import Path

OUT = Path("/mnt/project/g00952465/AI_Base_k3/glm53-flash-report/assets/figs")
OUT.mkdir(parents=True, exist_ok=True)

from matplotlib.font_manager import FontProperties, fontManager

# 注册 CJK 字体（OTF/CFF 不被 matplotlib 支持，必须用 TTF）
for f in ["/root/.config/aico/fonts/NotoSansSC.ttf"]:
    if Path(f).exists():
        fontManager.addfont(f)

plt.rcParams.update({
    "font.family": ["Noto Sans SC", "DejaVu Sans"],
    "axes.unicode_minus": False,
    "figure.facecolor": "white",
})

# ── 配色（参考 AICO-PPT 设计系统）────────────────────────────
RED   = "#b5333b"
INK   = "#1a1a1c"
INK2  = "#3a3a40"
GREY  = "#585860"
LIGHT = "#e7e7ea"
BG    = "#fafafa"
GOLD  = "#f4c84a"
BLUE  = "#1565c0"
GREEN = "#2e7d32"


def save(fig, name, dpi=180):
    fig.savefig(OUT / f"{name}.png", dpi=dpi, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  ✓ {name}.png")


# =================================================================
# 1. 5.2 vs 5.3-flash 8 维度对比表 (fig01-arch-overview.png)
# =================================================================
def fig_arch_overview():
    fig, ax = plt.subplots(figsize=(13.5, 5.5))
    ax.axis("off")
    ax.set_xlim(0, 14); ax.set_ylim(0, 6)
    ax.text(7, 5.55, "GLM-5.2 → glm5.3-flash · 八维结构变化总览", ha="center",
            fontsize=18, fontweight="bold", color=INK)

    rows = [
        ("维度",      "GLM-5.2",                              "glm5.3-flash"),
        ("注意力",    "全程 MLA+DSA",                          "混合：KDA(34) + DSA(11)"),
        ("残差",      "标准单流",                             "mHC · 4 流 + Sinkhorn"),
        ("稀疏索引",  "lightning_indexer",                    "kPool · 池压缩 ÷4"),
        ("RoPE 维度", "rope=64",                              "rope_dim=0（SFA 算子适配）"),
        ("规模",      "hidden=6144 · 78层 · 256 专家",         "hidden=4096 · 45层 · 288 专家"),
        ("SwiGLU",    "无 clamping",                          "swiglu_limit=10.0 · 4 处覆盖"),
        ("模态",      "纯文本",                               "VLM（图文）"),
        ("复用",      "—",                                    "MoE/MLP/MLA/W8A8 复用自 DSV3.2"),
    ]
    cell_h = 0.5
    for r, row in enumerate(rows):
        y = 4.6 - r * cell_h
        is_header = r == 0
        for c, val in enumerate(row):
            x = 0.6 + c * 4.4
            color = RED if is_header else (BG if r % 2 == 0 else "white")
            fc = color if is_header else (BG if r % 2 == 0 else "white")
            rect = FancyBboxPatch((x, y), 4.2, cell_h, boxstyle="round,pad=0.02",
                                  ec=GREY, fc=fc, lw=0.7)
            ax.add_patch(rect)
            tc = "white" if is_header else INK
            fs = 11 if is_header else 10
            fw = "bold" if is_header else ("bold" if c == 2 else "normal")
            ax.text(x + 4.2 / 2, y + cell_h / 2, val, ha="center", va="center",
                    fontsize=fs, color=tc, fontweight=fw)
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    save(fig, "fig01-arch-overview")


# =================================================================
# 2. 45 层混合注意力排布 (fig02-attention-pattern.png)
# =================================================================
def fig_attention_pattern():
    fig, ax = plt.subplots(figsize=(13.5, 4.5))
    ax.set_xlim(0, 46); ax.set_ylim(0, 8)
    ax.set_yticks([])
    ax.set_xticks(np.arange(0, 46, 5))
    ax.set_xticklabels([f"L{i}" for i in np.arange(0, 46, 5)], fontsize=10, color=GREY)
    for s in ["top", "right", "left"]:
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(GREY)
    ax.tick_params(axis="x", colors=GREY, length=0)

    ax.text(23, 7.4, "45 层混合注意力排布 · 34 层 KDA + 11 层 DSA",
            ha="center", fontsize=16, fontweight="bold", color=INK)

    # 画层柱
    bar_h = 2.2
    for i in range(1, 46):
        # 每 4 层一组: 3 KDA + 1 DSA
        pos = (i - 1) % 4
        if pos < 3:
            color = "#8e9aaf"
            label = "KDA"
        else:
            color = RED
            label = "DSA"
        # 跳过没有 DSA 的最后一组(i=45 是 KDA 收尾)
        # 实际: 第 3,7,11,...,43 是 DSA = 11 个; 第 1,2,4,5,6,...,45 中除 11 个 DSA 外的 34 个
        rect = Rectangle((i - 0.45, 3.5), 0.9, bar_h, fc=color, ec="white", lw=1)
        ax.add_patch(rect)
        # 标签防挤压: DSA 全标, KDA 只标首组 (图例在下方)
        if label == "DSA" or i <= 3:
            ax.text(i, 3.5 + bar_h / 2, label, ha="center", va="center",
                    fontsize=8, color="white", fontweight="bold")

    ax.text(2,  2.4, "KDA",  fontsize=11, color="#8e9aaf", fontweight="bold")
    ax.text(2,  1.9, "线性注意力", fontsize=9, color=GREY)
    ax.text(2,  1.4, "· delta-rule 递推", fontsize=9, color=GREY)
    ax.text(2,  0.9, "· 定长 fp32 状态 (4.3 MiB/序列)", fontsize=9, color=GREY)

    ax.text(28, 2.4, "DSA",  fontsize=11, color=RED, fontweight="bold")
    ax.text(28, 1.9, "稀疏全注意力", fontsize=9, color=GREY)
    ax.text(28, 1.4, "· MLA + kPool 索引", fontsize=9, color=GREY)
    ax.text(28, 0.9, "· 1.5 KiB/token · bf16", fontsize=9, color=GREY)
    save(fig, "fig02-attention-pattern")


# =================================================================
# 3. KDA delta-rule 状态递推 (fig03-kda-deltarule.png)
# =================================================================
def fig_kda_deltarule():
    fig, ax = plt.subplots(figsize=(13.5, 6.0))
    ax.axis("off"); ax.set_xlim(0, 14); ax.set_ylim(0, 7)
    ax.text(7, 6.55, "KDA · delta-rule 状态递推（线性注意力）",
            ha="center", fontsize=16, fontweight="bold", color=INK)

    # 输入流
    ax.text(0.4, 5.4, "输入 Q/K/V/g/β", fontsize=11, color=GREY, fontweight="bold")
    for i, name in enumerate(["Q", "K", "V", "g", "β"]):
        x = 1.6 + i * 0.9
        box = FancyBboxPatch((x, 4.6), 0.7, 0.7, boxstyle="round,pad=0.05",
                             ec=GREY, fc=BG, lw=1)
        ax.add_patch(box)
        ax.text(x + 0.35, 4.95, name, ha="center", va="center",
                fontsize=11, color=INK, fontweight="bold")

    # 遗忘门
    ax.annotate("", xy=(7.2, 3.6), xytext=(6, 4.6),
                arrowprops=dict(arrowstyle="->", color=GREY, lw=1.5))
    ax.text(6.7, 4.2, "遗忘", fontsize=10, color=GREY, ha="center")

    # S 状态矩阵
    S = FancyBboxPatch((6.6, 2.8), 1.6, 1.4, boxstyle="round,pad=0.05",
                       ec=RED, fc="#fff5f5", lw=2)
    ax.add_patch(S)
    ax.text(7.4, 3.85, "S", ha="center", fontsize=18, fontweight="bold", color=RED)
    ax.text(7.4, 3.45, "[B, 64, 128, 128]", ha="center", fontsize=8, color=GREY)
    ax.text(7.4, 3.05, "fp32 强制", ha="center", fontsize=8, color=RED, fontweight="bold")

    # 公式行
    formula_y = 1.55
    formulas = [
        ("S = S × exp(g)", "遗忘", GREY),
        ("δ = (v − S·k) × β", "新息", INK),
        ("S = S + k ⊗ δ", "写入", RED),
        ("out = S · q", "查询", BLUE),
    ]
    for i, (f_str, lbl, col) in enumerate(formulas):
        x = 0.6 + i * 3.3
        ax.text(x + 1.55, formula_y + 0.5, f_str, ha="center", fontsize=12,
                fontweight="bold", color=col, family=["DejaVu Sans Mono", "Noto Sans SC"])
        ax.text(x + 1.55, formula_y, lbl, ha="center", fontsize=9, color=GREY)

    # 底部对比
    ax.text(7, 0.4, "★ 关键：递推式原地改写 S 矩阵，每步非幂等 —— 图模式需 snapshot/restore",
            ha="center", fontsize=10, color=RED, fontweight="bold")
    save(fig, "fig03-kda-deltarule")


# =================================================================
# 4. KDA vs 标准 KV cache 状态对比 (fig04-state-comparison.png)
# =================================================================
def fig_state_comparison():
    fig, ax = plt.subplots(figsize=(13.5, 5.5))
    ax.axis("off"); ax.set_xlim(0, 14); ax.set_ylim(0, 6)
    ax.text(7, 5.55, "KDA 状态 vs 标准 KV cache · 7 维对比",
            ha="center", fontsize=16, fontweight="bold", color=INK)

    rows = [
        ("写入语义",   "追加（append）", "原地递推（read-modify-write）"),
        ("幂等性",     "幂等",          "非幂等（前向一遍推进 N 步）"),
        ("容量驱动",   "token 数",      "并发序列数"),
        ("生命周期",   "随序列结束",    "跨整个序列，不可回退"),
        ("存储精度",   "bf16",          "fp32（递推累积误差放大）"),
        ("prefix cache", "天然支持（前缀复用）", "难兼容（conv/ssm 每 token 变化）"),
        ("单层大小",   "~1.5 KiB/token", "~4.3 MiB/序列（定长）"),
    ]
    headers = ["", "标准 KV cache", "KDA conv/ssm 状态"]
    cell_h = 0.50
    for r, row in enumerate([tuple(headers)] + rows):
        y = 4.75 - r * cell_h
        is_header = r == 0
        for c, val in enumerate(row):
            x = 0.5 + c * 4.4
            fc = RED if is_header else (BG if r % 2 == 1 else "white")
            tc = "white" if is_header else INK
            fw = "bold" if is_header or c == 0 else "normal"
            ax.add_patch(FancyBboxPatch((x, y), 4.2, cell_h,
                                        boxstyle="round,pad=0.02",
                                        ec=GREY, fc=fc, lw=0.7))
            ax.text(x + 4.2 / 2, y + cell_h / 2, val, ha="center", va="center",
                    fontsize=10, color=tc, fontweight=fw)
    ax.text(7, 0.35, "★ KDA 状态 fp32 强制 + 非幂等 → 框架需 snapshot/restore + LayerCache 新增 conv/ssm 槽",
            ha="center", fontsize=10, color=RED, fontweight="bold")
    save(fig, "fig04-state-comparison")


# =================================================================
# 5. DSA+MLA absorbed 形态 (fig05-dsa-mla.png)
# =================================================================
def fig_dsa_mla():
    fig, ax = plt.subplots(figsize=(13.5, 5.5))
    ax.axis("off"); ax.set_xlim(0, 14); ax.set_ylim(0, 6)
    ax.text(7, 5.55, "DSA + MLA · absorbed 形态（SFA 算子硬约束）",
            ha="center", fontsize=16, fontweight="bold", color=INK)

    # decompressed (放弃的方案)
    ax.text(2.5, 4.6, "✗ decompressed 形态（放弃）", ha="center",
            fontsize=12, color=GREY, fontweight="bold")
    q = FancyBboxPatch((0.4, 3.5), 1.2, 0.5, boxstyle="round,pad=0.05",
                       ec=BLUE, fc="#e3f0ff", lw=1.2)
    ax.add_patch(q); ax.text(1, 3.75, "Q", ha="center", fontsize=11, fontweight="bold", color=BLUE)
    k = FancyBboxPatch((2.0, 3.5), 1.2, 0.5, boxstyle="round,pad=0.05",
                       ec=GREY, fc=BG, lw=1)
    ax.add_patch(k); ax.text(2.6, 3.75, "K (解压 256)", ha="center", fontsize=10)
    v = FancyBboxPatch((3.6, 3.5), 1.2, 0.5, boxstyle="round,pad=0.05",
                       ec=GREY, fc=BG, lw=1)
    ax.add_patch(v); ax.text(4.2, 3.75, "V (解压 256)", ha="center", fontsize=10)
    ax.text(2.7, 2.85, "SFA 算子 headDim=512", ha="center", fontsize=9, color=RED)
    ax.text(2.7, 2.55, "强制 absorbed → 此路走不通", ha="center", fontsize=9, color=RED, fontweight="bold")

    # 分隔
    ax.annotate("", xy=(6.6, 3.7), xytext=(5.4, 3.7),
                arrowprops=dict(arrowstyle="->", color=GREY, lw=2))

    # absorbed
    ax.text(10.2, 4.6, "✓ absorbed 形态（采用）", ha="center",
            fontsize=12, color=GREEN, fontweight="bold")
    q2 = FancyBboxPatch((7.4, 3.5), 1.2, 0.5, boxstyle="round,pad=0.05",
                        ec=BLUE, fc="#e3f0ff", lw=1.2)
    ax.add_patch(q2); ax.text(8, 3.75, "Q·W_UK", ha="center", fontsize=10, fontweight="bold", color=BLUE)
    kv = FancyBboxPatch((9.0, 3.5), 1.4, 0.5, boxstyle="round,pad=0.05",
                        ec=RED, fc="#fff5f5", lw=1.2)
    ax.add_patch(kv); ax.text(9.7, 3.75, "Latent 512", ha="center", fontsize=10, fontweight="bold", color=RED)
    ax.annotate("", xy=(11.0, 3.7), xytext=(10.5, 3.7),
                arrowprops=dict(arrowstyle="->", color=RED, lw=2))
    out = FancyBboxPatch((11.1, 3.5), 1.2, 0.5, boxstyle="round,pad=0.05",
                        ec=GREEN, fc="#e8f5e8", lw=1.2)
    ax.add_patch(out); ax.text(11.7, 3.75, "out·W_UV", ha="center", fontsize=10, fontweight="bold", color=GREEN)

    ax.text(10.2, 2.85, "q 吸收 W_UK → 与 512 维 latent 直算", ha="center", fontsize=9, color=GREEN)
    ax.text(10.2, 2.55, "64× 压缩 · 1 KiB/token · rope=0 零宽 V", ha="center", fontsize=9, color=GREEN, fontweight="bold")

    # 底部代码片段
    code = 'cache = [key [N,128,1,512], value [N,128,1,0], index [N,128,1,257]]'
    ax.text(7, 1.6, code, ha="center", fontsize=10, family=["DejaVu Sans Mono", "Noto Sans SC"], color=INK,
            bbox=dict(boxstyle="round,pad=0.4", fc=BG, ec=GREY))
    ax.text(7, 0.7, "★ 唯一差异：qk_rope_head_dim = 64 → 0   |   SFA 算子需 tiling 改 kL0Size 96→128",
            ha="center", fontsize=10, color=RED, fontweight="bold")
    save(fig, "fig05-dsa-mla")


# =================================================================
# 6. kPool 流程 (fig06-kpool-flow.png)
# =================================================================
def fig_kpool_flow():
    fig, ax = plt.subplots(figsize=(13.5, 5.5))
    ax.axis("off"); ax.set_xlim(0, 14); ax.set_ylim(0, 6)
    ax.text(7, 5.55, "kPool · 池压缩 + 选择（打分对象 ÷4）",
            ha="center", fontsize=16, fontweight="bold", color=INK)

    steps = [
        (1.0, "Q/K/Index",  "输入", BLUE),
        (3.4, "分池",       "4 个 token/池", GREY),
        (5.8, "softmax", "gate_scores + ape", INK),
        (8.2, "pool_key",   "学习到的加权 key", RED),
        (10.6, "ReLU 评分",  "relu(q·poolᵀ) × s", INK),
        (13.0, "top-512 池", "展开 2048 token", GREEN),
    ]
    for i, (x, name, sub, col) in enumerate(steps):
        b = FancyBboxPatch((x - 1.0, 3.5), 2.0, 1.0, boxstyle="round,pad=0.05",
                           ec=col, fc="white", lw=2)
        ax.add_patch(b)
        ax.text(x, 4.20, name, ha="center", fontsize=11, fontweight="bold", color=col)
        ax.text(x, 3.75, sub, ha="center", fontsize=9, color=GREY)
        if i < len(steps) - 1:
            ax.annotate("", xy=(steps[i+1][0] - 1.05, 4.0), xytext=(x + 1.05, 4.0),
                        arrowprops=dict(arrowstyle="->", color=GREY, lw=1.8))

    # 对比：DSV3.2 vs kPool
    ax.text(2.5, 2.4, "DSV3.2 lightning", ha="center", fontsize=10, color=GREY, fontweight="bold")
    ax.text(2.5, 2.0, "kv_len 个 token 选 top-2048", ha="center", fontsize=9, color=GREY)
    ax.text(2.5, 1.6, "O(kv_len)", ha="center", fontsize=10, color=GREY, family=["DejaVu Sans Mono", "Noto Sans SC"])

    ax.text(11.5, 2.4, "glm5.3-flash kPool", ha="center", fontsize=10, color=RED, fontweight="bold")
    ax.text(11.5, 2.0, "kv_len/4 个池 选 top-512 池", ha="center", fontsize=9, color=RED)
    ax.text(11.5, 1.6, "O(kv_len) ÷ 4", ha="center", fontsize=10, color=RED, fontweight="bold", family=["DejaVu Sans Mono", "Noto Sans SC"])

    ax.text(7, 0.5,
            "★ index cache 257 宽 = [k(128) + gate_scores(128) + valid(1)] — 池压缩需读历史 gate/valid",
            ha="center", fontsize=10, color=RED, fontweight="bold")
    save(fig, "fig06-kpool-flow")


# =================================================================
# 7. mHC 4 流残差 (fig07-mhc-4stream.png)
# =================================================================
def fig_mhc():
    fig, ax = plt.subplots(figsize=(13.5, 5.5))
    ax.axis("off"); ax.set_xlim(0, 14); ax.set_ylim(0, 6)
    ax.text(7, 5.55, "mHC · Manifold-constrained Hyper-Connection",
            ha="center", fontsize=16, fontweight="bold", color=INK)
    ax.text(7, 5.15, "4 流残差 + Sinkhorn-Knopp 20 轮行列归一化",
            ha="center", fontsize=11, color=GREY)

    # 输入 4 流
    in_streams = []
    for i, c in enumerate(["#8e9aaf", "#b5333b", "#2e7d32", "#f4c84a"]):
        y = 4.2 - i * 0.4
        b = FancyBboxPatch((0.4, y), 1.0, 0.3, boxstyle="round,pad=0.02",
                           ec=c, fc=c, lw=1)
        ax.add_patch(b)
        ax.text(0.9, y + 0.15, f"流 {i+1}", ha="center", va="center",
                fontsize=9, color="white", fontweight="bold")
        in_streams.append((y + 0.15, c))

    # fn 矩阵
    fn_box = FancyBboxPatch((2.2, 2.6), 2.6, 1.8, boxstyle="round,pad=0.05",
                            ec=RED, fc="#fff5f5", lw=2)
    ax.add_patch(fn_box)
    ax.text(3.5, 4.15, "fn", ha="center", fontsize=14, fontweight="bold", color=RED)
    ax.text(3.5, 3.80, "[24 × 16384]", ha="center", fontsize=10, color=GREY, family=["DejaVu Sans Mono", "Noto Sans SC"])
    ax.text(3.5, 3.45, "base / scale", ha="center", fontsize=9, color=GREY)
    ax.text(3.5, 3.05, "sigmoid · 2·sigmoid", ha="center", fontsize=9, color=GREY)

    # Sinkhorn
    sk_box = FancyBboxPatch((5.4, 2.6), 2.4, 1.8, boxstyle="round,pad=0.05",
                            ec=BLUE, fc="#e3f0ff", lw=2)
    ax.add_patch(sk_box)
    ax.text(6.6, 4.15, "Sinkhorn", ha="center", fontsize=12, fontweight="bold", color=BLUE)
    ax.text(6.6, 3.75, "20 轮", ha="center", fontsize=10, color=BLUE)
    ax.text(6.6, 3.30, "行归一 + 列归一", ha="center", fontsize=9, color=GREY)
    ax.text(6.6, 2.85, "→ 双随机流形 (comb)", ha="center", fontsize=9, color=GREY)

    # 重组合
    out_box = FancyBboxPatch((8.4, 2.6), 3.0, 1.8, boxstyle="round,pad=0.05",
                             ec=GREEN, fc="#e8f5e8", lw=2)
    ax.add_patch(out_box)
    ax.text(9.9, 4.15, "hidden = post ⊗ sub", ha="center", fontsize=11, fontweight="bold", color=GREEN)
    ax.text(9.9, 3.75, "+ combᵀ @ residual", ha="center", fontsize=11, fontweight="bold", color=GREEN)
    ax.text(9.9, 3.20, "[B, S, 4, D]", ha="center", fontsize=10, color=GREY, family=["DejaVu Sans Mono", "Noto Sans SC"])
    ax.text(9.9, 2.80, "→ 下一层继续 4 流", ha="center", fontsize=9, color=GREEN)

    # 输出 4 流
    for i, c in enumerate(["#8e9aaf", "#b5333b", "#2e7d32", "#f4c84a"]):
        y = 4.2 - i * 0.4
        ax.annotate("", xy=(12.0, y + 0.15), xytext=(11.5, y + 0.15),
                    arrowprops=dict(arrowstyle="->", color=c, lw=1.5))
        b = FancyBboxPatch((12.1, y), 1.0, 0.3, boxstyle="round,pad=0.02",
                           ec=c, fc=c, lw=1)
        ax.add_patch(b)
        ax.text(12.6, y + 0.15, f"流 {i+1}", ha="center", va="center",
                fontsize=9, color="white", fontweight="bold")

    # 流向连线
    for y, c in in_streams:
        ax.annotate("", xy=(2.15, 3.5), xytext=(1.45, y),
                    arrowprops=dict(arrowstyle="->", color=GREY, lw=0.8))
    ax.annotate("", xy=(5.35, 3.5), xytext=(4.85, 3.5),
                arrowprops=dict(arrowstyle="->", color=GREY, lw=1.5))
    ax.annotate("", xy=(8.35, 3.5), xytext=(7.85, 3.5),
                arrowprops=dict(arrowstyle="->", color=GREY, lw=1.5))

    ax.text(7, 1.5, "★ 每层两个 mHC 站点（attn_hc / ffn_hc）· 头部 4 流无权均值坍缩 + RMSNorm",
            ha="center", fontsize=10, color=RED, fontweight="bold")
    ax.text(7, 1.0, "★ 旋转盲区：fn 从 4 流旋转残差取输入 → 必须 block_diag(R×4) 每流独立消 R",
            ha="center", fontsize=10, color=RED, fontweight="bold")
    save(fig, "fig07-mhc-4stream")


# =================================================================
# 8. SwiGLU clamping 4 处覆盖 (fig08-swiglu-clamp.png)
# =================================================================
def fig_swiglu():
    fig, ax = plt.subplots(figsize=(13.5, 5.5))
    ax.axis("off"); ax.set_xlim(0, 14); ax.set_ylim(0, 6)
    ax.text(7, 5.55, "SwiGLU clamping · 4 处统一覆盖 swiglu_limit=10.0",
            ha="center", fontsize=16, fontweight="bold", color=INK)

    # 4 个覆盖点
    sites = [
        (1.5, "dense MLP",       "Glm5NextTextMLP",          "#1565c0"),
        (4.5, "MoE 288 专家",    "_apply_gate",              "#b5333b"),
        (8.0, "ViT MLP",         "Glm5NextVisionMLP",        "#2e7d32"),
        (11.5,"ViT patch-merger","Glm5NextVisionPatchMerger","#f4c84a"),
    ]
    for x, name, cls, col in sites:
        b = FancyBboxPatch((x - 1.3, 3.5), 2.6, 1.4, boxstyle="round,pad=0.05",
                           ec=col, fc="white", lw=2)
        ax.add_patch(b)
        ax.text(x, 4.55, name, ha="center", fontsize=11, fontweight="bold", color=col)
        ax.text(x, 4.15, cls, ha="center", fontsize=9, family=["DejaVu Sans Mono", "Noto Sans SC"], color=GREY)
        ax.text(x, 3.75, "✓ clamp 已覆盖", ha="center", fontsize=9, color=RED, fontweight="bold")

    # 公式
    code = (
        "gate = gate.clamp(max=10)              # silu 负方向自饱和, 只压上界\n"
        "up    = up.clamp(min=-10, max=10)      # 线性无界, 双边都压\n"
        "out  = F.silu(gate) * up               # 最大 ≈ silu(10) × 10 ≈ 100"
    )
    ax.text(7, 2.0, code, ha="center", va="center", fontsize=10, family=["DejaVu Sans Mono", "Noto Sans SC"],
            color=INK, bbox=dict(boxstyle="round,pad=0.5", fc=BG, ec=GREY))

    ax.text(7, 0.4, "★ 漏一处就破坏数值一致性 — GLM-5.2 没有，落地时全部 SwiGLU 通路必须带 clamp",
            ha="center", fontsize=10, color=RED, fontweight="bold")
    save(fig, "fig08-swiglu-clamp")


# =================================================================
# 9. W8A8 量化管线 (fig09-quant-pipeline.png)
# =================================================================
def fig_quant_pipeline():
    fig, ax = plt.subplots(figsize=(13.5, 4.5))
    ax.axis("off"); ax.set_xlim(0, 14); ax.set_ylim(0, 5)
    ax.text(7, 4.55, "W8A8 量化管线 · msmodelslim 四步串行 processor",
            ha="center", fontsize=16, fontweight="bold", color=INK)

    steps = [
        (1.2, "QuaRot",        "全局 Hadamard 旋转",          "数据无关 · 烘焙进权重", BLUE),
        (4.1, "flex_smooth_quant", "仅 attention norm-linear",  "SmoothQuant 离群摊平", GREY),
        (7.0, "linear_quant",  "仅 MLP (排除 gate)",            "w8a8 · per-token/per-ch", INK),
        (9.9, "ascendv1_saver","导出 + quarot.safetensors",      "rot.safetensors", RED),
        (12.8, "int8 模型",    "MLP 量化 · attn 保持 bf16",       "✓ 推理就绪", GREEN),
    ]
    for i, (x, name, sub, foot, col) in enumerate(steps):
        b = FancyBboxPatch((x - 1.1, 2.0), 2.2, 1.6, boxstyle="round,pad=0.05",
                           ec=col, fc="white", lw=2)
        ax.add_patch(b)
        ax.text(x, 3.20, name, ha="center", fontsize=11, fontweight="bold", color=col)
        ax.text(x, 2.80, sub, ha="center", fontsize=9, color=INK2, wrap=True)
        ax.text(x, 2.30, foot, ha="center", fontsize=8, color=GREY, style="italic")
        if i < len(steps) - 1:
            ax.annotate("", xy=(steps[i+1][0] - 1.15, 2.8), xytext=(x + 1.15, 2.8),
                        arrowprops=dict(arrowstyle="->", color=GREY, lw=2))

    ax.text(7, 1.1,
            "★ 关键事实：attention 完全不量化（bf16），只有 MLP 量化成 int8",
            ha="center", fontsize=10, color=RED, fontweight="bold")
    ax.text(7, 0.6,
            "★ QuaRot 离线烘焙，推理无运行时旋转 — R 仅存于 quarot.safetensors",
            ha="center", fontsize=10, color=GREY)
    save(fig, "fig09-quant-pipeline")


# =================================================================
# 10. 旋转盲区 3 处 (fig10-rot-blind.png)
# =================================================================
def fig_rot_blind():
    fig, ax = plt.subplots(figsize=(13.5, 5.5))
    ax.axis("off"); ax.set_xlim(0, 14); ax.set_ylim(0, 6)
    ax.text(7, 5.55, "旋转盲区 · 3 处漏配（QuaRot · R 矩阵）",
            ha="center", fontsize=16, fontweight="bold", color=INK)
    ax.text(7, 5.15,
            "判据：matmul(hidden, W) 且 hidden 来自旋转态 → 必须右旋 W ← W·R",
            ha="center", fontsize=10, color=GREY)

    boxes = [
        (2.0, "盲区 1 · KDA 门控",
         "forget_gate.f_a/b_proj、g_a_proj",
         "34 层 KDA output-gate cos ≈ 0.017（几乎正交）",
         "修复：quarot.py 补 3 条一级右旋",
         "修复后 cos = 1.0",
         BLUE),
        (7.0, "盲区 2 · mHC fn",
         "Parameter[24, 16384]",
         "4 流旋转残差取输入漏旋 · pre 门 cos ≈ 0.54",
         "修复：block_diag(R×4) 每流独立消 R",
         "MTP 层无 HC 不配",
         RED),
        (12.0, "盲区 3 · indexer compress_gate",
         "index_kpool_compress_gate [128,4096]",
         "校准时 stub=0 隐蔽，真引擎 std=0.17 才出错",
         "修复：model_adapter.py 补右旋 G ← G·R",
         "隐蔽性最强",
         GREEN),
    ]
    for x, title, param, prob, fix, extra, col in boxes:
        b = FancyBboxPatch((x - 2.0, 0.4), 4.0, 4.2, boxstyle="round,pad=0.05",
                           ec=col, fc="white", lw=2)
        ax.add_patch(b)
        ax.text(x, 4.30, title, ha="center", fontsize=11, fontweight="bold", color=col)
        ax.text(x, 3.90, param, ha="center", fontsize=9, family=["DejaVu Sans Mono", "Noto Sans SC"], color=INK2, wrap=True)
        ax.text(x, 3.30, "问题", ha="center", fontsize=9, color=GREY, fontweight="bold")
        ax.text(x, 2.90, prob, ha="center", fontsize=9, color=INK2, wrap=True)
        ax.text(x, 2.20, "修复", ha="center", fontsize=9, color=GREEN, fontweight="bold")
        ax.text(x, 1.80, fix, ha="center", fontsize=9, color=INK2, wrap=True)
        ax.text(x, 1.10, extra, ha="center", fontsize=9, color=col, style="italic")
    save(fig, "fig10-rot-blind")


# =================================================================
# 11. 7 级优化阶梯 (fig11-opt-ladder.png)
# =================================================================
def fig_opt_ladder():
    fig, ax = plt.subplots(figsize=(13.5, 8.0))
    ax.set_xlim(-0.7, 8.7); ax.set_ylim(0, 1100)

    labels = ["基线\neager", "1\naclgraph", "2\nKDA 优化", "3\nmHC 融合",
              "4\nkPool gather", "5\n删 RNE", "6\n池 cache", "7\nMTP"]
    tpot   = [958.3, 237.8, 155.7, 119.0, 60.5, 51.5, 46.9, 39.7]
    cum    = [1.0,   4.0,   6.2,   8.1,   15.9, 18.6, 20.4, 24.1]
    colors = ["#8e9aaf", "#1565c0", "#b5333b", "#2e7d32",
              "#f4c84a", "#9c27b0", "#ff7043", "#c62828"]

    # 阶梯柱
    bar_w = 0.7
    for i in range(len(tpot)):
        ax.bar(i, tpot[i], bar_w, color=colors[i], edgecolor="white", linewidth=2, zorder=3)
        ax.text(i, tpot[i] + 35, f"{tpot[i]:.1f}ms", ha="center",
                fontsize=12, color=colors[i], fontweight="bold")

    # 趋势线
    ax.plot(range(len(tpot)), tpot, "-", color=GREY, lw=1.5, alpha=0.5, zorder=2)
    for i in range(len(tpot)):
        ax.plot(i, tpot[i], "o", color=colors[i], markersize=10,
                markeredgecolor="white", markeredgewidth=2, zorder=4)

    # 双层 x 轴标签
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, fontsize=11, color=INK)
    # 第二个 x 轴放累计
    ax2 = ax.twiny()
    ax2.set_xlim(ax.get_xlim())
    ax2.set_xticks(range(len(cum)))
    ax2.set_xticklabels([f"{c:.1f}×" for c in cum], fontsize=11,
                        color=INK, fontweight="bold")
    ax2.tick_params(axis="x", colors=GREY, length=0, pad=10)
    ax2.set_xlabel("累计加速比", fontsize=11, color=GREY, labelpad=20)

    ax.set_ylabel("TPOT (ms)", fontsize=11, color=GREY)
    ax.set_yticks([0, 200, 400, 600, 800, 1000])
    ax.set_yticklabels(["0", "200", "400", "600", "800", "1000"])
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)
    ax.spines["left"].set_color(GREY); ax.spines["bottom"].set_color(GREY)
    ax.tick_params(axis="x", colors=GREY, length=0, pad=4)
    ax.tick_params(axis="y", colors=GREY)
    ax.set_title("7 级优化阶梯 · 958.3 → 39.7ms (24.1×)",
                 fontsize=16, fontweight="bold", color=INK, pad=14)

    # 标注
    ax.annotate("图模式\nhost 阻塞清零", xy=(1, 237.8), xytext=(1.6, 600),
                fontsize=10, color="#1565c0",
                bbox=dict(boxstyle="round,pad=0.4", fc="#e3f0ff", ec="#1565c0"),
                arrowprops=dict(arrowstyle="->", color="#1565c0"))
    ax.annotate("kPool gather\n134×", xy=(4, 60.5), xytext=(3.3, 380),
                fontsize=10, color="#9c27b0",
                bbox=dict(boxstyle="round,pad=0.4", fc="#f3e5f5", ec="#9c27b0"),
                arrowprops=dict(arrowstyle="->", color="#9c27b0"))
    ax.annotate("MTP\nverify 接受率 80%", xy=(7, 39.7), xytext=(5.5, 200),
                fontsize=10, color=RED,
                bbox=dict(boxstyle="round,pad=0.4", fc="#fff5f5", ec=RED),
                arrowprops=dict(arrowstyle="->", color=RED))

    fig.text(0.5, 0.02,
            "口径：单机 8 卡 TP8 · 3.5K 输入 / 1K 输出 · 1 并发 · w8a8 真实权重",
            ha="center", fontsize=10, color=GREY, style="italic")
    plt.subplots_adjust(bottom=0.18, top=0.92)
    save(fig, "fig11-opt-ladder")


# =================================================================
# 12. host vs compute breakdown (fig12-host-compute.png)
# =================================================================
def fig_host_compute():
    fig, axes = plt.subplots(1, 2, figsize=(13.5, 5.5))
    # 饼图 1 — eager
    ax = axes[0]
    sizes_eager = [62, 38]
    labels_eager = ["NPU 等 host\n62%", "NPU 真工作\n38%"]
    colors_eager = [GREY, BLUE]
    ax.pie(sizes_eager, labels=labels_eager, colors=colors_eager,
           autopct="", startangle=90, wedgeprops=dict(edgecolor="white", linewidth=2),
           textprops=dict(fontsize=11, color=INK))
    ax.set_title("eager · 958ms\nhost 阻塞占 62%", fontsize=14,
                 fontweight="bold", color=INK)
    ax.text(0, -1.5, "每次 .item() 同步\n逐算子 launch\nPython dispatch",
            ha="center", fontsize=9, color=GREY, style="italic")

    # 饼图 2 — graph
    ax = axes[1]
    sizes_g = [3, 97]
    labels_g = ["comm\n3%", "compute\n97%"]
    colors_g = ["#f4c84a", RED]
    ax.pie(sizes_g, labels=labels_g, colors=colors_g,
           autopct="", startangle=90, wedgeprops=dict(edgecolor="white", linewidth=2),
           textprops=dict(fontsize=11, color=INK))
    ax.set_title("aclgraph · 238ms\nhost 占比 ≈ 0%", fontsize=14,
                 fontweight="bold", color=INK)
    ax.text(0, -1.5, "整模型录成静态图\n一次 graph.replay()\nbusy 率 97%",
            ha="center", fontsize=9, color=GREY, style="italic")

    fig.suptitle("aclgraph 收益 · 消除 host 调度开销", fontsize=16,
                 fontweight="bold", color=INK, y=1.02)
    save(fig, "fig12-host-compute")


# =================================================================
# 13. kPool gather 134× (fig13-kpool-134x.png)
# =================================================================
def fig_kpool_134x():
    fig, axes = plt.subplots(1, 2, figsize=(13.5, 5.0))

    # Before
    ax = axes[0]
    methods_b = ["fancy index\n(AI_CPU)", "F.embedding\n(AI_VECTOR_CORE)"]
    time_b    = [3354, 33]
    bars = ax.bar(methods_b, time_b, color=["#8e9aaf", "#2e7d32"])
    ax.set_title("Index 调用次数 / 步 (越小越好)", fontsize=12, fontweight="bold", color=INK)
    ax.set_ylabel("次数", fontsize=11, color=GREY)
    for b, v in zip(bars, time_b):
        ax.text(b.get_x() + b.get_width() / 2, v + 60, f"{v}",
                ha="center", fontsize=11, fontweight="bold", color=INK)
    ax.set_ylim(0, 4000)
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(GREY); ax.spines["bottom"].set_color(GREY)
    ax.tick_params(colors=GREY)
    ax.text(0.5, -0.22,
            "3354 次/29.4% → 33 次/0.04% (÷100)\n官方分支微基准注释逐字命中",
            transform=ax.transAxes, ha="center", fontsize=9, color=GREY, style="italic")

    # 索引数据量
    ax = axes[1]
    sizes_l = ["fancy index", "flattened\ngather", "F.embedding"]
    sizes_v = [33.5, 33.5, 0.25]
    bars = ax.bar(sizes_l, sizes_v, color=["#8e9aaf", "#b5333b", "#2e7d32"])
    ax.set_title("索引数据量 (MB)", fontsize=12, fontweight="bold", color=INK)
    ax.set_ylabel("MB", fontsize=11, color=GREY)
    for b, v in zip(bars, sizes_v):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.7, f"{v}",
                ha="center", fontsize=11, fontweight="bold", color=INK)
    ax.set_ylim(0, 40)
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(GREY); ax.spines["bottom"].set_color(GREY)
    ax.tick_params(colors=GREY)
    ax.text(0.5, -0.22,
            "33.5MB → 0.25MB  (134×)\n行级取数每层 2.5 → 0.05ms",
            transform=ax.transAxes, ha="center", fontsize=9, color=RED,
            fontweight="bold", style="italic")

    fig.suptitle("kPool gather 优化 · 三步演进", fontsize=16,
                 fontweight="bold", color=INK, y=1.04)
    save(fig, "fig13-kpool-134x")


# =================================================================
# 14. MTP 投机解码 (fig14-mtp.png)
# =================================================================
def fig_mtp():
    fig, ax = plt.subplots(figsize=(13.5, 5.0))
    ax.axis("off"); ax.set_xlim(0, 14); ax.set_ylim(0, 5)
    ax.text(7, 4.55, "MTP 投机解码 · KDA 状态 lazy-commit",
            ha="center", fontsize=16, fontweight="bold", color=INK)

    # verify 流程
    flow_y = 2.8
    seq = [
        (1.0, "S=1\ndecode",  BLUE),
        (3.5, "draft\nKDA 步", INK),
        (6.0, "verify\nRMSNorm", INK),
        (8.5, "argmax\n校验", INK),
        (11.0, "S=2\n接受 ≈80%", GREEN),
        (13.0, "继续",  GREY),
    ]
    for i, (x, lbl, col) in enumerate(seq):
        b = FancyBboxPatch((x - 0.9, flow_y - 0.4), 1.8, 0.9,
                           boxstyle="round,pad=0.05", ec=col, fc="white", lw=2)
        ax.add_patch(b)
        ax.text(x, flow_y, lbl, ha="center", va="center",
                fontsize=10, fontweight="bold", color=col)
        if i < len(seq) - 1:
            ax.annotate("", xy=(seq[i+1][0] - 0.95, flow_y), xytext=(x + 0.95, flow_y),
                        arrowprops=dict(arrowstyle="->", color=GREY, lw=1.8))

    # lazy-commit 解释
    ax.text(7, 1.65,
            "per-(layer, slot) 暂存原始 qkv/gate/beta 行 → 跨层批量前进 + lead-trim",
            ha="center", fontsize=10, color=INK)
    ax.text(7, 1.25,
            "★ 工程难度最高 — KDA 状态非幂等与 verify 多 token 推进的语义冲突",
            ha="center", fontsize=10, color=RED, fontweight="bold")

    # 收益
    b1 = FancyBboxPatch((1.0, 0.1), 3.0, 0.7, boxstyle="round,pad=0.05",
                        ec=BLUE, fc="#e3f0ff", lw=1.5)
    ax.add_patch(b1)
    ax.text(2.5, 0.45, "TPOT 46.9 → 39.7ms", ha="center", fontsize=11,
            fontweight="bold", color=BLUE)

    b2 = FancyBboxPatch((5.0, 0.1), 4.0, 0.7, boxstyle="round,pad=0.05",
                        ec=GREEN, fc="#e8f5e8", lw=1.5)
    ax.add_patch(b2)
    ax.text(7.0, 0.45, "吞吐 19.8 → 22.3 tok/s", ha="center", fontsize=11,
            fontweight="bold", color=GREEN)

    b3 = FancyBboxPatch((10.0, 0.1), 3.5, 0.7, boxstyle="round,pad=0.05",
                        ec=RED, fc="#fff5f5", lw=1.5)
    ax.add_patch(b3)
    ax.text(11.75, 0.45, "接受率 ≈ 80%", ha="center", fontsize=11,
            fontweight="bold", color=RED)
    save(fig, "fig14-mtp")


# =================================================================
# main
# =================================================================
if __name__ == "__main__":
    fig_arch_overview()
    fig_attention_pattern()
    fig_kda_deltarule()
    fig_state_comparison()
    fig_dsa_mla()
    fig_kpool_flow()
    fig_mhc()
    fig_swiglu()
    fig_quant_pipeline()
    fig_rot_blind()
    fig_opt_ladder()
    fig_host_compute()
    fig_kpool_134x()
    fig_mtp()
    print(f"\n✓ 全部 {len(list(OUT.glob('*.png')))} 张图已生成到 {OUT}/")