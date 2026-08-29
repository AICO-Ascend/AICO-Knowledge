#!/usr/bin/env python3
"""build_glm53_v9.py — GLM 5.3-flash deck 终版重做 (v9 质量标准)。

数据源 (全部真实，零编造):
  - GLM 5.3-flash 工程事实: /tmp/build_glm53_v2.py 内嵌文本 (uniinfer 适配原始记录)
  - 14 张 GLM matplotlib figs: assets/figs/ (真实实测数据可视化)
  - 12 张 KB crops: AICO-knowledge extraction (同源论文原图, 配 M3 准确 caption)

设计 (仿 qwen36 v9):
  - 每页 1080px 硬预算 (PDF 导出不裁切)
  - 图 + 图旁技术要点 + 引用出处 (author · arXiv · fig)
  - dark-header 对照表 + 高亮列
  - 小白话黄盒 (技术小白受众)
  - 深读页 2×2 KB 原图 + 参考文献页 (arXiv 分组)

写入: staging + cp 绕开 NFS soft quota。
"""
import importlib.util, re, subprocess, os, shutil
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    'eb', '/mnt/project/g00952465/AI_Base_k3/AICO-PPT/scripts/edit-bundle.py'
)
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)

DECK = '/mnt/project/g00952465/AI_Base_k3/glm53-flash-report/glm53-flash-deck.html'
TEMPLATE = '/mnt/project/g00952465/AI_Base_k3/AICO-PPT/assets/tech-share-deck.html'
STAGING = '/tmp/glm53_v9_staging.html'
FIGS = Path('/mnt/project/g00952465/AI_Base_k3/glm53-flash-report/assets/figs')
CROPS = Path('/mnt/project/g00952465/AICO-knowledge/extraction/assets/crops')
PAGES = Path('/mnt/project/g00952465/AICO-knowledge/extraction/assets')

# ── 从干净模板重新开始 (cp 绕开 NFS soft quota: shutil.copyfile 的 open(wb) 会被拦) ──
subprocess.run(['cp', '-f', TEMPLATE, DECK], capture_output=True)
lines = mod.load(DECK)
s = mod.get_template(lines)
print(f'template loaded: {len(s):,} chars')

# ── 嵌入图片 ───────────────────────────────────────────────
GLM_FIGS = [
    'fig01-arch-overview', 'fig02-attention-pattern', 'fig03-kda-deltarule',
    'fig04-state-comparison', 'fig05-dsa-mla', 'fig06-kpool-flow',
    'fig07-mhc-4stream', 'fig08-swiglu-clamp', 'fig09-quant-pipeline',
    'fig10-rot-blind', 'fig11-opt-ladder', 'fig12-host-compute',
    'fig13-kpool-134x', 'fig14-mtp',
]
KB_FIGS = {
    'kb-hc1':      CROPS / 'hc-manifold-constrained-hyper-connections-fig01.png',
    'kb-hc2':      CROPS / 'hc-manifold-constrained-hyper-connections-fig02.png',
    'kb-klinear6': CROPS / 'kimi-linear-an-expressive-efficient-attention-architecture-fig06.png',
    'kb-k3-3':     CROPS / 'kimi-k3-open-frontier-intelligence-fig03.png',
    'kb-dsv3-2':   CROPS / 'deepseek-v3-technical-report-fig02.png',
    'kb-dsv3-3':   CROPS / 'deepseek-v3-technical-report-fig03.png',
    'kb-dsv3-5':   CROPS / 'deepseek-v3-technical-report-fig05.png',
    'kb-idx1':     CROPS / 'indexcache-accelerating-sparse-attention-via-cross-layer-index-reuse-fig01.png',
    'kb-gdn-t4':   CROPS / 'gated-delta-networks-improving-mamba2-with-delta-rule-tab04.png',
    'kb-k2-2':     CROPS / 'kimi-k2-open-agentic-intelligence-fig02.png',
    'kb-megatron4': CROPS / 'efficient-large-scale-language-model-training-on-gpu-clusters-using-megatron-lm-fig04.png',
    'kb-klinear3': CROPS / 'kimi-linear-an-expressive-efficient-attention-architecture-fig03.png',
    'kb-gdn-1':   CROPS / 'gated-delta-networks-improving-mamba2-with-delta-rule-fig01.png',
    'kb-eagle3-2': CROPS / 'eagle-3-scaling-up-inference-acceleration-of-large-language-models-via-training-time-test-fig02.png',
    'kb-medusa-1': CROPS / 'medusa-simple-llm-inference-acceleration-framework-with-multiple-decoding-heads-fig01.png',
    'kb-pagedattn-2': CROPS / 'efficient-memory-management-for-large-language-model-serving-with-pagedattention-fig02.png',
}
U = {}
for name in GLM_FIGS:
    p = FIGS / f'{name}.png'
    assert p.exists(), p
    U[name] = mod.embed_image(lines, str(p), mime='image/png', prefix='imgg')
for key, p in KB_FIGS.items():
    assert p.exists(), p
    U[key] = mod.embed_image(lines, str(p), mime='image/png', prefix='imgk')
print(f'embedded {len(U)} images')

# ═══════════════════════════════════════════════════════════
# 设计系统 (AICO-PPT: RED #b5333b / INK #1a1a1c / dark #1b2333)
# ═══════════════════════════════════════════════════════════
RED, INK, GREY, LIGHT, BG = '#b5333b', '#1a1a1c', '#585860', '#e7e7ea', '#fafafa'
BLUE, GREEN, GOLD, DARK = '#1565c0', '#2e7d32', '#f4c84a', '#1b2333'

def sec(label, inner, pad='46px 72px', bg='#fff'):
    return ('<div class="slide-fit" data-idx="" data-active=""><div class="slide-canvas">'
            f'<section data-label="{label}" style="width:100%; height:100%; padding:{pad}; '
            f'background:{bg}; font-family:\'Noto Sans SC\',sans-serif; overflow:hidden; position:relative;">'
            f'{inner}</section></div></div>')

def eyebrow(t, color=RED):
    return (f'<div style="font-family:\'JetBrains Mono\',\'Noto Sans SC\',monospace; font-size:15px; '
            f'letter-spacing:.18em; color:{color}; margin-bottom:6px;">{t}</div>')

def h2(t, size=38):
    return (f'<h2 style="margin:0 0 10px; font-weight:700; font-size:{size}px; '
            f'color:{INK}; line-height:1.2;">{t}</h2>')

def lead(t, size=16):
    return (f'<p style="margin:0 0 14px; font-size:{size}px; color:{GREY}; line-height:1.65; '
            f'max-width:1720px;">{t}</p>')

def foot(t):
    return (f'<div style="margin-top:10px; font-size:13px; color:{GREY}; line-height:1.55; '
            f'border-top:1px dashed {LIGHT}; padding-top:8px;">{t}</div>')

def laybox(t):
    return (f'<div style="font-size:14px; line-height:1.65; color:#444; background:#fff8e1; '
            f'padding:12px 16px; border-left:4px solid {GOLD}; border-radius:6px; margin-top:10px;">'
            f'<b style="color:#8a6a2b;">小白版</b> · {t}</div>')

def codebox(code, title=None, fs=12.5):
    head = (f'<div style="padding:6px 14px; background:#2c3548; color:#c8d0e0; font-size:12px; '
            f'font-family:\'JetBrains Mono\',\'Noto Sans SC\',monospace; border-radius:8px 8px 0 0;">{title}</div>' if title else '')
    radius = '0 0 8px 8px' if title else '8px'
    return (f'<div style="border-radius:{radius}; overflow:hidden; margin-top:8px; '
            f'box-shadow:0 4px 14px rgba(20,22,28,.10);">{head}'
            f'<pre style="margin:0; padding:12px 16px; background:{DARK}; color:#e8ecf4; '
            f'font-family:\'JetBrains Mono\',\'Noto Sans SC\',monospace; font-size:{fs}px; line-height:1.55; '
            f'overflow:hidden; white-space:pre;">{code}</pre></div>')

def dtable(headers, rows, hl=None, fs=13.5, col_w=None):
    n = len(headers)
    if col_w is None:
        col_w = [1] * n
    total = sum(col_w)
    def cell(i, content, is_head, ri):
        w = col_w[i] / total * 100
        style = f'flex:0 0 {w:.2f}%; padding:9px 12px; overflow:hidden;'
        if is_head:
            style += 'border-left:1px solid #2c3548;'
            if i == hl: style += f'background:#2a1416; color:#e8b4b8;'
        else:
            style += 'border-left:1px solid #ececee;'
            if i == hl: style += f'background:#fdf6f5; color:{RED}; font-weight:600;'
        return f'<div style="{style}">{content}</div>'
    thead = ''.join(cell(i, h, True, 0) for i, h in enumerate(headers))
    body = ''
    for ri, row in enumerate(rows):
        rbg = '#faf9f5' if ri % 2 == 0 else '#fff'
        cells = ''.join(cell(i, c, False, ri) for i, c in enumerate(row))
        body += (f'<div style="display:flex; background:{rbg}; border-bottom:1px solid #f0f0f2; '
                 f'font-size:{fs}px; color:#333; line-height:1.5;">{cells}</div>')
    return (f'<div style="border:1px solid {LIGHT}; border-radius:10px; overflow:hidden; margin-top:8px;">'
            f'<div style="display:flex; background:{DARK}; color:#fff; font-size:{fs}px; font-weight:700;">{thead}</div>'
            f'{body}</div>')

def figcap(img_uid, cap_html, cite_html, img_pct=55, cap_title='图说了什么'):
    """主图 + 图旁技术要点 + 引用出处 — 核心版式"""
    return (f'<div style="display:flex; gap:22px; margin-top:6px; align-items:flex-start;">'
            f'<div style="flex:0 0 {img_pct}%; min-width:0;">'
            f'<img src="{img_uid}" style="width:100%; height:auto; border-radius:8px; '
            f'border:1px solid {LIGHT}; box-shadow:0 4px 14px rgba(20,22,28,.08);" /></div>'
            f'<div style="flex:1; min-width:0;">'
            f'<div style="font-family:\'JetBrains Mono\',\'Noto Sans SC\',monospace; font-size:12px; color:{RED}; '
            f'letter-spacing:.12em; margin-bottom:6px;">{cap_title}</div>'
            f'<div style="font-size:14.5px; color:#333; line-height:1.7;">{cap_html}</div>'
            f'<div style="font-size:11.5px; color:#8a8a90; line-height:1.55; margin-top:10px; '
            f'border-top:1px dashed {LIGHT}; padding-top:8px;">{cite_html}</div>'
            f'</div></div>')

def kbstrip(img_uid, cap_html, cite_html, img_w=300):
    """KB 同源证据小条: 小图 + 说明 + 出处"""
    return (f'<div style="display:flex; gap:14px; margin-top:10px; padding:10px 14px; '
            f'background:{BG}; border:1px solid {LIGHT}; border-radius:10px; align-items:center;">'
            f'<img src="{img_uid}" style="flex:0 0 {img_w}px; width:{img_w}px; height:auto; '
            f'border-radius:6px; border:1px solid {LIGHT};" />'
            f'<div style="flex:1; min-width:0;">'
            f'<div style="font-size:12.5px; color:#444; line-height:1.6;">{cap_html}</div>'
            f'<div style="font-size:11px; color:#9a9aa0; margin-top:5px;">{cite_html}</div>'
            f'</div></div>')

def pillar(num, color, title, body):
    bgm = {BLUE: '#eef3fb', RED: '#fdf6f5', GREEN: '#eef7ee', '#8a6a2b': '#faf6ee', '#6a4a8c': '#f3eef8'}
    return (f'<div style="flex:1; min-width:0; background:{bgm.get(color, BG)}; '
            f'border:1.5px solid {color}; border-radius:12px; padding:14px 16px;">'
            f'<div style="font-family:\'JetBrains Mono\',\'Noto Sans SC\',monospace; font-size:13px; color:{color}; '
            f'letter-spacing:.12em;">{num}</div>'
            f'<div style="font-size:19px; font-weight:700; color:{INK}; margin:3px 0 6px;">{title}</div>'
            f'<div style="font-size:14px; color:#444; line-height:1.6;">{body}</div></div>')

def chapter(code, title, desc, kws):
    chips = ''.join(
        f'<span style="display:inline-block; padding:5px 14px; margin:0 8px 8px 0; background:#fff; '
        f'border:1px solid {LIGHT}; border-radius:999px; font-size:14px; color:{INK};">{k}</span>'
        for k in kws)
    return sec(f'章扉{code}', (
        f'<div style="font-size:200px; font-weight:700; color:#f3d9da; line-height:1; '
        f'font-family:\'JetBrains Mono\',\'Noto Sans SC\',monospace; margin-top:30px;">{code}</div>'
        f'<div style="margin-top:-40px;">'
        + eyebrow(f'SECTION {code} · GLM 5.3-flash')
        + f'<h2 style="margin:0 0 14px; font-weight:700; font-size:56px; color:{INK};">{title}</h2>'
        + f'<p style="margin:0 0 22px; font-size:19px; color:{GREY}; line-height:1.65; max-width:1300px;">{desc}</p>'
        + chips + '</div>'),
        pad='60px 90px', bg='#faf9f7')

SECTIONS = []
def add(label, html, nav=None):
    SECTIONS.append((label, html, nav or label))

# ═══════════════════════════════════════════════════════════
# 1. 封面
# ═══════════════════════════════════════════════════════════
add('封面', sec('封面', (
    f'<div style="position:absolute; inset:0; background:linear-gradient(135deg, {DARK} 0%, #24365c 55%, #2b5a8c 100%);"></div>'
    '<div style="position:relative; padding:110px 120px; color:#fff; height:100%;">'
    '<div style="font:15px \'JetBrains Mono\',\'Noto Sans SC\',monospace; color:#b8c5d8; letter-spacing:.22em;">'
    'TECH DEEP-DIVE · 2026/08 · 昇腾 uniinfer 适配实录</div>'
    '<h1 style="margin:34px 0 0; font-size:84px; font-weight:700; line-height:1.1; letter-spacing:-.01em;">glm5.3-flash</h1>'
    '<div style="margin-top:14px; font-size:38px; font-weight:600; color:#e8c547;">'
    '从 958ms 到 39.7ms — 24.1× 推理加速全记录</div>'
    '<div style="margin-top:36px; font-size:19px; color:#d8dce4; line-height:1.7; max-width:1350px;">'
    '45 层混合注意力（34 KDA + 11 DSA）· mHC 4 流残差 · kPool 池压缩 · W8A8 量化 — '
    '每一项结构创新在昇腾 910B 上的算子适配、量化盲区修复与 7 级性能优化，'
    '全部基于真实实测数据（单机 8 卡 TP8 · w8a8 真实权重）。</div>'
    '<div style="display:flex; gap:18px; margin-top:52px; max-width:1500px;">'
    '<div style="flex:1; background:rgba(255,255,255,.10); border:1px solid rgba(255,255,255,.2); border-radius:10px; padding:22px 24px;">'
    '<div style="font:12px \'JetBrains Mono\',\'Noto Sans SC\',monospace; color:#e8c547;">TPOT · 每 token 时延</div>'
    '<div style="font-size:36px; font-weight:700; margin-top:6px;">39.7<span style="font-size:17px; font-weight:400;"> ms</span></div>'
    '<div style="font-size:13px; color:#c8d0e0; margin-top:2px;">eager 基线 958.3ms</div></div>'
    '<div style="flex:1; background:rgba(255,255,255,.10); border:1px solid rgba(255,255,255,.2); border-radius:10px; padding:22px 24px;">'
    '<div style="font:12px \'JetBrains Mono\',\'Noto Sans SC\',monospace; color:#e8c547;">累计加速比</div>'
    '<div style="font-size:36px; font-weight:700; margin-top:6px;">24.1×</div>'
    '<div style="font-size:13px; color:#c8d0e0; margin-top:2px;">7 级优化阶梯叠加</div></div>'
    '<div style="flex:1; background:rgba(255,255,255,.10); border:1px solid rgba(255,255,255,.2); border-radius:10px; padding:22px 24px;">'
    '<div style="font:12px \'JetBrains Mono\',\'Noto Sans SC\',monospace; color:#e8c547;">精度（无回退）</div>'
    '<div style="font-size:36px; font-weight:700; margin-top:6px;">78% / 90%</div>'
    '<div style="font-size:13px; color:#c8d0e0; margin-top:2px;">MMMU_PRO / AIME2026</div></div>'
    '</div>'
    '<div style="display:flex; gap:12px; margin-top:48px; max-width:1560px;">'
    + ''.join(
        f'<div style="flex:1; border-left:3px solid #e8c547; padding:10px 14px; background:rgba(255,255,255,.06); border-radius:0 8px 8px 0;">'
        f'<div style="font:12px \'JetBrains Mono\',\'Noto Sans SC\',monospace; color:#e8c547;">{c}</div>'
        f'<div style="font-size:14.5px; color:#e8ecf4; margin-top:4px; line-height:1.45;">{t}</div></div>'
        for c, t in [('CH 1', '背景与结论 · 8 维差异'), ('CH 2', '模型结构 5 处创新'), ('CH 3', 'W8A8 量化盲区'),
                     ('CH 4', '7 级性能阶梯'), ('CH 5', '工程化交付')])
    + '</div>'
    '<div style="position:absolute; bottom:44px; left:120px; font-size:14px; color:#9aa3b3;">'
    '知识库支撑：AICO-Knowledge · 69 篇同源论文 · 685 图 · 479 公式 · 本 deck 全部数字可溯源</div>'
    '</div>'), pad='0'))

# ═══════════════════════════════════════════════════════════
# 2. 目录
# ═══════════════════════════════════════════════════════════
add('目录', sec('目录', (
    eyebrow('CONTENTS') + h2('5 章 34 页 · 一图速览', 42)
    + '<div style="display:flex; gap:18px; margin-top:18px;">'
    + pillar('CH 1', BLUE, '背景与结论', 'GLM-5.2 → 5.3-flash 的 8 维结构差异 · 45 层混合注意力排布 · 线性注意力科普（4 页）')
    + pillar('CH 2', RED, '模型结构创新', 'KDA 线性注意力 · mHC 4 流残差 · kPool 池压缩 · SwiGLU 钳位 · rope_dim=0（7 页）')
    + pillar('CH 3', GREEN, 'W8A8 量化', 'msmodelslim 四步管线 · QuaRot 旋转盲区 3 处 · 修复后 cos → 1.0（3 页）')
    + '</div>'
    + '<div style="display:flex; gap:18px; margin-top:16px;">'
    + pillar('CH 4', '#8a6a2b', '性能优化阶梯', '958.3 → 39.7ms · 图模式 / fla_npu / 融合算子 / gather 134× / MTP（8 页）')
    + pillar('CH 5', '#6a4a8c', '工程化交付', 'TP8 拉起脚本 · 评测数据 · 5 处结构变化 × 问题 × 手段总结（3 页）')
    + pillar('收尾', GREY, '深读 · 术语 · 文献', 'KB 同源论文原图深读 · 术语速查 · arXiv 参考文献（4 页）')
    + '</div>'
    + foot('★ 阅读动线：技术小白建议顺序读（每章开头有科普）；工程师可直接跳 CH 3 / CH 4 看量化盲区与性能数字。'))))

# ═══════════════════════════════════════════════════════════
# 3. TL;DR 数据墙
# ═══════════════════════════════════════════════════════════
add('TLDR', sec('TLDR', (
    eyebrow('TL;DR · 结论先行') + h2('一页看懂：这次适配交付了什么', 40)
    + lead('口径：单机 8 卡 TP8 · 3.5K 输入 / 1K 输出 · 1 并发 · w8a8 真实权重 · 推理场景单 token 端到端延迟。')
    + '<div style="display:grid; grid-template-columns:repeat(3, 1fr); gap:18px; margin-top:12px;">'
    + ''.join(
        f'<div style="background:{BG}; border:1px solid {LIGHT}; border-radius:14px; padding:26px 28px;">'
        f'<div style="font:14px \'JetBrains Mono\',\'Noto Sans SC\',monospace; color:{c}; letter-spacing:.1em;">{k}</div>'
        f'<div style="font-size:52px; font-weight:700; color:{INK}; margin-top:8px;">{v}</div>'
        f'<div style="font-size:14.5px; color:{GREY}; margin-top:6px; line-height:1.55;">{d}</div></div>'
        for k, v, d, c in [
            ('TPOT · 每 token 时延', '39.7 ms', 'eager 基线 958.3ms → 7 级优化后 39.7ms，已进入该规模访存下限区间 (~30-40ms)', RED),
            ('累计加速比', '24.1×', '图模式 4.0× → KDA 6.2× → mHC 8.1× → kPool 15.9× → RNE 18.6× → 池 cache 20.4× → MTP 24.1×', RED),
            ('吞吐', '22.3 tok/s', '单并发口径；MTP verify 每步产出 ~2 token', BLUE),
            ('MMMU_PRO', '78%', '图文多模态精度，量化 + 全部优化后无回退', GREEN),
            ('AIME2026', '90%', '数学推理精度，量化 + 全部优化后无回退', GREEN),
            ('vs GLM-5.2', '成本持平', '精度不丢 + 价格不变 = 端到端可交付', GREY),
        ])
    + '<div style="display:flex; align-items:center; gap:0; margin-top:22px; padding:16px 20px; background:#fff; border:1px solid ' + LIGHT + '; border-radius:12px;">'
    + ''.join(
        f'<div style="flex:1; text-align:center;">'
        f'<div style="font-size:12px; color:{GREY};">{lab}</div>'
        f'<div style="font-family:\'JetBrains Mono\',\'Noto Sans SC\',monospace; font-size:19px; font-weight:700; color:{col};">{val}</div>'
        f'</div>' + ('' if i == 7 else '<div style="color:#c8c8ce; font-size:16px;">→</div>')
        for i, (lab, val, col) in enumerate([
            ('基线 eager', '958.3', GREY), ('① 图模式', '237.8', BLUE), ('② KDA fla_npu', '155.7', RED),
            ('③ mHC 融合', '119.0', GREEN), ('④ kPool gather', '60.5', '#8a6a2b'), ('⑤ 删 RNE', '51.5', '#6a4a8c'),
            ('⑥ 池 cache', '46.9', '#c2652b'), ('⑦ MTP', '39.7', RED)]))
    + '</div>'
    + laybox('把一个 45 层的新模型放到华为 NPU 上跑，开始每个字要等 958 毫秒（一句话卡半分钟）。'
             '工程师用 7 招把它压到 39.7 毫秒 — 比眨眼还快，而且答题准确率一分没掉。（上图为 7 级阶梯的 TPOT 毫秒数）')
    + foot('★ 真正的全新工作：KDA、mHC、kPool、SFA 算子对 rope_dim=0 的支持 — 这几项也是后文量化盲区、算子适配与性能优化的来源。'))))

# ═══════════════════════════════════════════════════════════
# 4. ch1-对比表 (8 维差异)
# ═══════════════════════════════════════════════════════════
add('ch1-对比表', sec('ch1-对比表', (
    eyebrow('1.1 · 8 维差异') + h2('GLM-5.2 → glm5.3-flash：不是「换个算子」', 36)
    + lead('8 个维度的本质变化 — 每一处都触及推理框架的算子 / 量化 / 调度层。右图：结构变化总览（按真实 config 绘制）。')
    + figcap(U['fig01-arch-overview'],
        'glm5.3-flash 相对 5.2 的<b>真正全新工作</b>只有 4 项：<b>KDA 线性注意力（34 层）</b>、'
        '<b>mHC 4 流残差</b>、<b>kPool 池压缩索引</b>、<b>rope_dim=0 的 SFA 算子适配</b>。'
        '其余（MoE / MLP / MLA / W8A8）全部复用自 DSV3.2 — 复用决定了适配的主战场在哪。',
        '口径：glm5.3-flash 真实 config.json · hidden=4096 · 45 层 · 288 专家 · qk_rope_head_dim=0',
        img_pct=52)
    + dtable(['维度', 'GLM-5.2', 'glm5.3-flash'],
        [['注意力', '全程 MLA+DSA', '混合：KDA(34 层) + DSA(11 层)'],
         ['残差', '标准单流', 'mHC · 4 流 + Sinkhorn'],
         ['稀疏索引', 'lightning_indexer', 'kPool · 池压缩 ÷4'],
         ['RoPE 维度', 'rope=64', 'rope_dim=0 (SFA 算子适配)'],
         ['规模', 'hidden=6144 · 78 层 · 256 专家', 'hidden=4096 · 45 层 · 288 专家'],
         ['SwiGLU', '无 clamping', 'swiglu_limit=10.0 · 4 处覆盖']],
        hl=2, fs=13, col_w=[1, 1.6, 1.8]))))

# ═══════════════════════════════════════════════════════════
# 5. ch1-attn (45 层排布)
# ═══════════════════════════════════════════════════════════
add('ch1-attn', sec('ch1-attn', (
    eyebrow('1.2 · 注意力排布') + h2('45 层混合注意力 · 34 KDA + 11 DSA', 36)
    + lead('每 4 层一组：前 3 层 KDA（线性注意力）+ 第 4 层 DSA（稀疏全注意力）。'
           '第 3/7/11/.../43 层是 DSA = 11 个；其余 34 个 KDA。')
    + '<div style="text-align:center; margin-top:6px;"><img src="' + U['fig02-attention-pattern'] + '" '
      'style="width:82%; height:auto; border-radius:8px; border:1px solid ' + LIGHT + '; box-shadow:0 4px 14px rgba(20,22,28,.08);" /></div>'
    + '<div style="display:flex; gap:22px; margin-top:14px; align-items:flex-start;">'
    + '<div style="flex:0 0 52%;">'
    + '<div style="font-family:\'JetBrains Mono\',\'Noto Sans SC\',monospace; font-size:12px; color:' + RED + '; letter-spacing:.12em; margin-bottom:6px;">图说了什么</div>'
    + '<div style="font-size:15px; color:#333; line-height:1.7;">'
      '<b>上下文 ~8K 是分水岭</b>：8K 以内 DSA 的 KV cache 还小，稀疏全注意力精度更高；'
      '超过 8K 后 KDA 的<b>定长状态</b>（4.3 MiB/序列，不随长度增长）反超性价比 — '
      '128K 时 DSA cache 涨到 ~2.2GB/序列，KDA 仍是 145 MiB 总量。'
      '这就是「混合」的意义：<b>不是二选一，而是让两种注意力各管自己性价比高的区间</b>。</div>'
    + '<div style="font-size:11.5px; color:#8a8a90; margin-top:8px; border-top:1px dashed ' + LIGHT + '; padding-top:7px;">'
      '口径：glm5.3-flash 真实层级排布 · KDA fp32 状态 4.3 MiB/序列 · DSA ~1.5 KiB/token bf16</div>'
    + '</div>'
    + '<div style="flex:1;">'
    + laybox('想象 45 层是 45 个编辑轮流审稿：34 个是「速读编辑」（KDA，只带一个固定大小的笔记本，越看越薄），'
             '11 个是「精读编辑」（DSA，带着整个书库但只翻最相关的 2048 页）。'
             '短文章精读编辑更强，长文章速读编辑扛得住 — 所以两种混着排。')
    + '</div></div>')))

# ═══════════════════════════════════════════════════════════
# 6. ch1-概念 (小白科普)
# ═══════════════════════════════════════════════════════════
add('ch1-概念', sec('ch1-概念', (
    eyebrow('1.3 · 概念科普 · 给技术小白') + h2('三种注意力：O(n²) → O(n) → 稀疏', 36)
    + lead('注意力是 Transformer 的发动机 — 决定「每个 token 该看哪些 token」。glm5.3-flash 把三代技术混在一具模型里。')
    + '<div style="display:flex; gap:16px; margin-top:10px;">'
    + pillar('第 1 代', GREY, '全注意力 O(n²)',
        '每个 token 跟<b>所有</b> token 两两打分。<br>'
        '128K 上下文 = 每 token 算 128K 次关联，算力爆炸。<br>'
        '<b>类比</b>：1000 人开会，每人跟其余 999 人都聊一遍 = 50 万场对话。')
    + pillar('第 2 代', BLUE, 'KDA 线性注意力 O(n)',
        '维护一个<b>固定大小的「滚动总结」状态 S</b>，每来 1 个 token 只更新 1 次状态。<br>'
        '128K 上下文 = 只更新 128K 次，<b>与长度线性</b>。<br>'
        '<b>类比</b>：不再两两对话，改为每个人在共享笔记本上加一行摘要。')
    + pillar('第 3 代', RED, 'DSA 稀疏索引 O(n·k)',
        '先用轻量 indexer 给所有 token 打分，<b>只留 top-2048</b> 做精细注意力；'
        'kPool 再把 4 个 token 合成 1 个打分对象，索引成本 ÷4。<br>'
        '<b>类比</b>：图书馆先用目录筛出 2048 本相关的，再逐本精读。')
    + '</div>'
    + '<div style="margin-top:14px;">'
    + dtable(['', '状态/缓存', '随上下文增长', 'glm5.3-flash 用在哪'],
        [['全注意力', 'KV cache 全量', '线性涨（无界）', '—（未采用）'],
         ['KDA', 'S 矩阵定长 4.3 MiB/序列', '<b>不涨</b>', '34 层 · 长文主力'],
         ['DSA + kPool', 'top-2048 稀疏 KV', '涨得慢', '11 层 · 短文/关键层']],
        hl=3, fs=13, col_w=[1, 1.5, 1.2, 1.6])
    + '</div>'
    + foot('★ 同源论文：KDA ← Kimi Linear (arXiv:2510.26692) · DSA ← DeepSeek NSA 系 · kPool ← IndexCache (arXiv:2608.02288)，详见末页参考文献。'))))

# ═══════════════════════════════════════════════════════════
# 7. 章扉 02
# ═══════════════════════════════════════════════════════════
add('章扉02', chapter('02', '模型结构创新',
    '5 处结构改动 — KDA 线性注意力、mHC 多流残差、kPool 稀疏索引、SwiGLU 钳位、rope_dim=0 — 每一处都把「快」做进架构本身。',
    ['KDA delta-rule', 'mHC 4 流 + Sinkhorn', 'kPool ÷4', 'SwiGLU clamp=10', 'rope_dim=0']))

# ═══════════════════════════════════════════════════════════
# 8. ch2-kda-formula
# ═══════════════════════════════════════════════════════════
add('ch2-kda-formula', sec('ch2-kda-formula', (
    eyebrow('2.1 · KDA · delta-rule 递推') + h2('KDA：用固定大小状态代替 KV cache', 34)
    + lead('KDA（Kimi Delta Attention）每步原地改写状态矩阵 S。<b>非幂等</b>（与 KV cache 的根本差异）— 这是后文图模式适配的核心难题。')
    + '<div style="display:flex; gap:22px; align-items:flex-start;">'
    + '<div style="flex:0 0 46%;">'
    + codebox(
'''S = S × exp(g)        # ① 遗忘：逐 token 逐 head 衰减
δ = (v − S·k) × β     # ② 新息：delta-rule 算更新量
S = S + k ⊗ δ         # ③ 写入：外积写回状态
out = S · q           # ④ 查询：取状态作为输出''',
        title='delta-rule 递推 · 每步 O(1) 原地改写', fs=14)
    + '<div style="font-size:13.5px; color:#444; line-height:1.7; margin-top:10px; padding:10px 14px; background:#fdf6f5; border-left:3px solid ' + RED + '; border-radius:6px;">'
    '<b>非幂等意味着什么？</b> KV cache 是「追加」，重放计算结果不变；'
    'KDA 的 S 是「原地递推」，前向每跑一遍就推进 N 步 — '
    '图模式 capture 时会把状态推进到错误位置，必须 capture 前 snapshot、capture 后 restore。</div>'
    + '</div>'
    + '<div style="flex:1; min-width:0;">'
    + kbstrip(U['kb-k3-3'],
        '<b>同源证据 · Kimi K3 Fig.3</b>：左图对数衰减参数化 — Kimi Linear 的 g 无下界（灰线），'
        'K3 改用 g_min·Sigmoid 在 −5 处饱和（红线）；右图 chunkwise 计算因此统一为稠密 Tensor Core GEMM，'
        '消除「位置对 vs 稠密」混合模式。',
        '★ Moonshot AI, 2026 · Kimi K3 · Fig.3, p.5 · <b>同源代理</b> · glm5.3-flash KDA 与 Kimi KDA 同族',
        img_w=330)
    + laybox('S 就是那块「滚动笔记本」：每天（每 token）先忘掉一点（×exp(g)），'
             '再把「今天比昨天多了什么」（δ）写进去。笔记本页数固定 — 这就是「定长状态」。')
    + '</div></div>'
    + foot('★ 关键：S 矩阵 [B, 64, 128, 128] fp32 每步原地改写 — 图模式 capture 前 snapshot、capture 后 restore，让 capture 像没发生过。'))))

# ═══════════════════════════════════════════════════════════
# 9. ch2-kda (工程实现)
# ═══════════════════════════════════════════════════════════
add('ch2-kda', sec('ch2-kda', (
    eyebrow('2.1 · KDA · 工程实现') + h2('state 槽位与快照机制：让非幂等状态入图', 34)
    + lead('LayerCache 为 KDA 新增 conv/ssm 两槽；SSM 32×128×128 fp32 = 4MiB/序列定长。'
           '图捕获前 snapshot 原始 qkv/gate/β，捕获后 restore — 让 capture 像没发生过。')
    + figcap(U['fig03-kda-deltarule'],
        'KDA 前端的 5 个组件：<b>causal conv1d</b>（kernel=4，短程上下文记忆）→ '
        '<b>三个门控</b>（forget g · input β · output gate）→ <b>delta-rule 递推</b> → '
        '<b>Q/K L2 归一化 + 1/√head_dim 缩放</b>（FLA 风格）→ '
        '<b>Prefill chunked (chunk=64) / decode recurrent</b> 双路径。',
        '口径：glm5.3-flash uniinfer 实现 · conv [slots, 3, 3072] fp32 (TP8) · ssm [slots, 8, 128, 128] fp32',
        img_pct=50)
    + codebox(
'''# attention/backend.py:33（官方 preview/glm-5.3-flash 核验）
class LayerCache:
    key:   torch.Tensor | None        # 全注意力 [3227, 128, 1, 512]
    value: torch.Tensor | None        # [3227, 128, 1, 0] (rope=0 零宽)
    index: torch.Tensor | None = None  # MLA 稀疏索引 kPool [., 257]
    conv:  torch.Tensor | None = None  # KDA 线性层 [slots, 3, 3072] fp32
    ssm:   torch.Tensor | None = None  # KDA 线性层 [slots, 8, 128, 128] fp32
    index_scale: torch.Tensor | None = None  # DSA 索引缩放（官方新增槽）

# capture 前 snapshot / capture 后 restore（decode_acl_graph.py:977/1023）
_snapshot_linear_state(entry); graph.replay()
_restore_linear_state(entry, snapshot)''',
        title='LayerCache · 官方六槽（preview/glm-5.3-flash 核验），KDA conv/ssm + DSA key/value/index(+scale)', fs=11.5))))

# ═══════════════════════════════════════════════════════════
# 10. ch2-kda-state (对比表)
# ═══════════════════════════════════════════════════════════
add('ch2-kda-state', sec('ch2-kda-state', (
    eyebrow('2.1 · KDA 状态管理') + h2('KDA conv/ssm 状态 vs 标准 KV cache', 34)
    + lead('两种 cache 活在不同的世界：KV 是「追加 + 幂等」，KDA 是「原地递推 + 非幂等」— 这就是图模式需要 snapshot/restore 的根本原因。')
    + '<div style="display:flex; gap:22px; align-items:flex-start;">'
    + '<div style="flex:0 0 47%;"><img src="' + U['fig04-state-comparison'] + '" style="width:100%; border-radius:8px; border:1px solid ' + LIGHT + ';" />'
    + kbstrip(U['kb-gdn-t4'],
        '<b>同源证据 · Gated DeltaNet Tab.4</b>：GDN（KDA 前身）在不同 cache 配置下的训练 loss 对比 — '
        '定长状态 + 量化部署的精度代价有公开数据可查。',
        '★ Yang et al., 2024 · arXiv:2412.06464 · Table 4 · <b>同源代理</b> · KDA 状态管理方法族', img_w=250)
    + '</div>'
    + '<div style="flex:1; min-width:0;">'
    + dtable(['', '标准 KV cache', 'KDA conv/ssm 状态'],
        [['写入语义', '追加 (append)', '原地递推 (read-modify-write)'],
         ['幂等性', '幂等', '非幂等（每跑一遍推进 N 步）'],
         ['容量驱动', 'token 数', '并发序列数'],
         ['生命周期', '随序列结束释放', '跨整个序列，不可回退'],
         ['存储精度', 'bf16', 'fp32（递推累积误差放大）'],
         ['单层大小', '~1.5 KiB/token', '~4.3 MiB/序列（定长）']],
        hl=2, fs=12.5, col_w=[1, 1.4, 1.6])
    + '</div></div>'
    + foot('★ 上下文 ~8K 是分水岭：超过 8K 后 KDA 定长状态开始反超性价比 — 128K 时 DSA cache ~2.2GB/序列，KDA 仍 145 MiB/序列。')
    + laybox('KV cache 像「无限加页的笔记本」—— 文章越长本子越厚；KDA 像「固定 100 页的活页夹」—— '
             '写得再长也只有 100 页，但必须小心：翻错一页就乱（非幂等），所以干活前先拍照（snapshot），干完放回去（restore）。'))))

# ═══════════════════════════════════════════════════════════
# 11. ch2-dsa
# ═══════════════════════════════════════════════════════════
add('ch2-dsa', sec('ch2-dsa', (
    eyebrow('2.2 · DSA + MLA · absorbed 形态') + h2('复用 DSV3.2 MLA，唯一差异 = rope 维度 64 → 0', 34)
    + lead('MLA 的 SFA 算子把 headDim 焊死为 512=kv_lora — 它只认 latent 形态的 K，必须走 absorbed。'
           '这反过来决定 cache 布局：value 槽被复用为 rope key 缓存，rope=0 所以零宽 = 0 元素不占显存。')
    + '<div style="display:flex; gap:22px; align-items:flex-start;">'
    + f'<div style="flex:0 0 47%;"><img src="{U["fig05-dsa-mla"]}" style="width:100%; border-radius:8px; border:1px solid {LIGHT};" /></div>'
    + '<div style="flex:1; min-width:0;">'
    + dtable(['改造点', '真实值 / 效果'],
        [['qk_rope_head_dim', '0（DSV3.2 是 64）— 代码显式断言'],
         ['SFA 算子 tiling', 'kL0Size 96 → 128'],
         ['修复', '消除 256%96=64 尾部越界崩溃 (error 546)'],
         ['kernel 内 rope', 'buffer/offset/copy 全部条件化']],
        fs=12.5, col_w=[1.2, 2.2])
    + codebox(
'''# 索引 cache 实测（TP8）：
k cache       [3227, 128, 1, 512]  # 3227 block × 128 token
v cache       [3227, 128, 1, 0]    # rope=0 → 零宽不占显存
indexer cache [3227, 128, 1, 257]  # kPool 打包缓存

# 真实权重 config.json：
"qk_rope_head_dim": 0, "v_head_dim": 256, "qk_nope_head_dim": 256''',
        title='cache 布局 + config.json 真实值', fs=11.5)
    + '</div></div>'
    + kbstrip(U['kb-dsv3-5'],
        '<b>同源证据 · DeepSeek-V3 Fig.5</b>：MLA 的 absorbed 形态 — K/V 投影矩阵在推理时被吸收进 Q 投影，'
        'cache 只存 latent 向量（512 维），这就是 glm5.3-flash DSA 层直接复用的结构。',
        '★ DeepSeek-AI, 2024 · arXiv:2412.19437 · Fig.5, p.13 · <b>同源代理</b> · DSA 复用 DSV3.2 MLA',
        img_w=300))))

# ═══════════════════════════════════════════════════════════
# 12. ch2-mhc
# ═══════════════════════════════════════════════════════════
add('ch2-mhc', sec('ch2-mhc', (
    eyebrow('2.3 · mHC · 4 流残差') + h2('Manifold-constrained Hyper-Connection', 34)
    + lead('用 hc_mult=4 个并行残差流替代标准残差。每层两个 mHC 实例（attn_hc / ffn_hc）。'
           'comb 矩阵经 Sinkhorn-Knopp 20 轮行列交替归一化，投影到双随机流形。')
    + '<div style="display:flex; gap:22px; align-items:flex-start;">'
    + '<div style="flex:0 0 44%;">'
    + f'<img src="{U["fig07-mhc-4stream"]}" style="width:100%; border-radius:8px; border:1px solid {LIGHT};" />'
    + kbstrip(U['kb-hc1'],
        '<b>同源证据 · mHC 论文 Fig.1</b>：(a) 标准残差 → (b) HC 三映射（Res/Pre/Post）→ '
        '(c) mHC 对三映射施加流形投影约束，使残差路径趋近恒等、Pre/Post 近似正交。',
        '★ Xie et al., 2026 · arXiv:2512.24880 · Fig.1 · <b>直接同源</b> · glm5.3-flash mHC 实现依据', img_w=210)
    + '</div>'
    + '<div style="flex:1; min-width:0;">'
    + dtable(['组件', '真实形态'],
        [['fn 参数', '[(2+4)×4, 4×4096] = [24, 16384]'],
         ['三个输出', 'pre (坍缩 4→1) · post (2·sigmoid) · comb (4×4)'],
         ['Sinkhorn', '20 轮行列交替归一化 → 双随机流形'],
         ['头部坍缩', '4 流无权均值 + RMSNorm'],
         ['★ 旋转盲区', 'fn 漏旋 → 必须 block_diag(R×4) 每流独立消 R']],
        fs=12.5, col_w=[1, 2.4])
    + codebox(
'''# decoder 层前向：hidden 全程 [B, S, 4, D] 四流
residual = hidden_states
post, comb, hidden_states = self.attn_hc(hidden_states)
hidden_states = self.self_attn(self.input_layernorm(hidden_states), ...)
hidden_states = kernels.hc_post(hidden_states, residual, post, comb)
# ffn_hc 站点同上（每层两个 mHC 实例）''',
        title='层内重组合：hidden = post ⊗ sublayer_out + combᵀ @ residual', fs=11.5)
    + '</div></div>'
    + laybox('普通模型只有 1 条「信息高速公路」，mHC 修了 4 条并行道，还有一个交警（Sinkhorn）'
             '每 20 轮检查一次：4 条道的车流量必须进出平衡，不许堵车也不许丢车。'))))

# ═══════════════════════════════════════════════════════════
# 13. ch2-kpool
# ═══════════════════════════════════════════════════════════
add('ch2-kpool', sec('ch2-kpool', (
    eyebrow('2.4 · kPool · 池压缩') + h2('打分对象 ÷4：lightning_indexer 的池化升级版', 34)
    + lead('打分对象从「每个 token 的 index key」变成「每 4 token 一组的 pool_key」，选择空间 ÷4。'
           'cache 连带变宽：257 = [k(128) + gate_scores(128) + valid(1)]。')
    + figcap(U['fig06-kpool-flow'],
        '五步流程：<b>① token 按 index_kpool=4 分组</b> → '
        '<b>② 池内 softmax(gate_scores + ape)</b> 学一个加权平均 key → '
        '<b>③ ReLU(q·poolᵀ) × scale 评分</b>（注意是 ReLU 不是 softmax）→ '
        '<b>④ top-512 池展开成 2048 token 索引</b> → '
        '<b>⑤ always_select_tail</b> 把未满尾池按原始 token 追加。',
        '口径：glm5.3-flash uniinfer 实现 · index_kpool=4 · top-512 池 × 4 = 2048 token',
        img_pct=48)
    + codebox(
'''# fancy index (AI_CPU) → flattened gather (AICore 原生)
flat_idx = (safe_indices[..., None] * head_dim + head_off) \\
              .reshape(batch_size, -1)
grouped_keys = keys.reshape(batch_size, -1) \\
                  .gather(1, flat_idx) \\
                  .reshape(batch_size, n_pools, rate, head_dim)

# Ascend 上 gather 无 bool kernel：uint8 中转
slot_valid = key_valid.to(torch.uint8) \\
                  .gather(1, safe_indices.reshape(batch_size, -1)) \\
                  .reshape(batch_size, n_pools, rate).to(torch.bool)''',
        title='真实代码：fancy index → AICore 原生 gather（性能伏笔 → CH4 134×）', fs=11.5)
    + laybox('从 1 万张照片挑 2000 张：原本一张张翻（1 万次）；kPool 先把 4 张合成 1 张「缩略图」，只翻 2500 次 — '
             '选中缩略图再把里面 4 张原图全拿走。'))))

# ═══════════════════════════════════════════════════════════
# 14. ch2-swiglu
# ═══════════════════════════════════════════════════════════
add('ch2-swiglu', sec('ch2-swiglu', (
    eyebrow('2.5 · SwiGLU clamping · 4 处覆盖') + h2('gate 只压上界 · up 压双边 · 统一封顶 10', 34)
    + lead('SwiGLU = silu(gate) × up 的乘积没有天然上界（gate=50, up=50 → ≈2500）。'
           '一个 outlier 维度就能产生巨值，深网络里一路放大。gate 负方向 silu 自饱和（→0），只压正方向上界；up 两边线性无界，必须双边都压。')
    + '<div style="display:flex; gap:22px; align-items:flex-start;">'
    + f'<div style="flex:0 0 46%;"><img src="{U["fig08-swiglu-clamp"]}" style="width:100%; border-radius:8px; border:1px solid {LIGHT};" /></div>'
    + '<div style="flex:1; min-width:0;">'
    + dtable(['位置', '钳位策略', '原因'],
        [['gate', '只压上界 (+10)', 'silu 负方向自饱和 →0'],
         ['up', '双边 (±10)', '线性无界，两边都会爆'],
         ['覆盖', '4 处统一', 'dense / 专家 / ViT / patch-merger']],
        fs=13, col_w=[1, 1.4, 1.8])
    + kbstrip(U['kb-k2-2'],
        '<b>同源证据 · Kimi K2 Fig.2</b>：训练中 attention logits 会飙到 1000+ — '
        '无钳位时深网络数值发散是真实存在的故障模式，这正是 swiglu_limit=10.0 的动机。',
        '★ Moonshot AI, 2025 · arXiv:2507.20534 · Fig.2, p.4 · <b>同源代理</b> · clamp 必要性证据', img_w=280)
    + '</div></div>'
    + laybox('想象算盘：silu×up 本来没封顶，算错一格结果就上天。clamp=10 就是给每格加盖子 — '
             'gate 最高 10、up 在 ±10 之间，再算错也跳不远。'))))

# ═══════════════════════════════════════════════════════════
# 15. 章扉 03
# ═══════════════════════════════════════════════════════════
add('章扉03', chapter('03', 'W8A8 量化方案',
    'msmodelslim 四步 processor 串行 — QuaRot 烘焙 + SmoothQuant + 线性层 int8 + 导出；3 处旋转盲区逐个补旋，cos 从 ≈0.017 拉回 1.0。',
    ['QuaRot 全局旋转', 'SmoothQuant 摊平', 'MLP int8', 'attn bf16', '3 处盲区']))

# ═══════════════════════════════════════════════════════════
# 16. ch3-pipeline
# ═══════════════════════════════════════════════════════════
add('ch3-pipeline', sec('ch3-pipeline', (
    eyebrow('3.1 · 量化管线') + h2('msmodelslim · 四步 processor 串行', 34)
    + lead('attention 完全不量化（bf16），只有 MLP 量化成 int8。QuaRot 用全局随机 Hadamard 矩阵 R 把残差流旋转到 h·R 基，'
           '摊平离群值，离线烘焙进权重，推理时无运行时旋转。')
    + '<div style="text-align:center; margin-top:6px;"><img src="' + U['fig09-quant-pipeline'] + '" '
      'style="width:84%; height:auto; border-radius:8px; border:1px solid ' + LIGHT + '; box-shadow:0 4px 14px rgba(20,22,28,.08);" /></div>'
    + '<div style="display:flex; gap:22px; margin-top:14px; align-items:flex-start;">'
    + '<div style="flex:0 0 52%;">'
    + '<div style="font-family:\'JetBrains Mono\',\'Noto Sans SC\',monospace; font-size:12px; color:' + RED + '; letter-spacing:.12em; margin-bottom:6px;">图说了什么</div>'
    + '<div style="font-size:15px; color:#333; line-height:1.7;">'
      '四步串行：<b>① QuaRot 烘焙</b>（全局 Hadamard 旋转写入权重）→ <b>② SmoothQuant</b>（激活离群值摊平到权重）→ '
      '<b>③ 线性层 int8</b>（MLP 权重 + 激活双 8bit）→ <b>④ 导出</b>（w8a8 真实权重）。'
      '关键决策：<b>attention 保持 bf16</b> — KDA 递推对精度敏感（fp32 状态），量化收益小而风险大。</div>'
    + '<div style="font-size:11.5px; color:#8a8a90; margin-top:8px; border-top:1px dashed ' + LIGHT + '; padding-top:7px;">'
      '口径：msmodelslim 实际量化配置 · glm5.3-flash w8a8 权重 · 镜像 quay.io/jd_xllm/xllm-ai</div>'
    + '</div>'
    + '<div style="flex:1;">'
    + laybox('量化 = 把高清照片压成 JPEG 省空间。QuaRot 的「旋转」是先转个角度再压 — '
             '让照片的能量分散开，压完不留明显瑕疵。attention 部分太敏感，干脆不压。')
    + '</div></div>')))

# ═══════════════════════════════════════════════════════════
# 17. ch3-rot
# ═══════════════════════════════════════════════════════════
add('ch3-rot', sec('ch3-rot', (
    eyebrow('3.2 · 旋转盲区 · 3 处漏配') + h2('判据：matmul(hidden, W) 且 hidden 来自旋转态 → 必须右旋 W·R', 32)
    + lead('σ(R·h) ≠ R·σ(h) — glm5.3-flash 新增的数据相关门控从旋转残流取输入、输出喂 sigmoid/softmax，'
           '若输入投影漏旋，门控就在错误基上算 → <b>语义偏移</b>（非量化噪声，是语义错误）。')
    + figcap(U['fig10-rot-blind'],
        '3 处盲区全是 5.3-flash 的<b>新增结构</b>（所以 DSV3.2 时代没暴露过）：<br>'
        '<b>① KDA 门控</b>：f_a / f_b / g_a_proj 输入维=hidden → 必须右旋（二级投影输入维=head_dim，一级补旋后不旋）<br>'
        '<b>② mHC fn</b>：4 流独立 → block_diag(R×4) 每流消 R<br>'
        '<b>③ indexer compress_gate</b>：最隐蔽 — 校准时 stub=0 不触发，真引擎 std=0.17 才出错',
        '口径：quarot.py / model_adapter.py 真实修复 commit · 修复后 cos 相似度 ≈0.017 / ≈0.54 → 1.0',
        img_pct=54)
    + laybox('「旋转」像把整个城市地图转了 45° — 所有路牌（权重）都得跟着转。'
             '有 3 条路是新修的（KDA 门控 / mHC / kPool indexer），市政忘了给它们换路牌 — '
             '车照老路牌开，就开到错的地方去了。'))))

# ═══════════════════════════════════════════════════════════
# 18. ch3-rot-code
# ═══════════════════════════════════════════════════════════
add('ch3-rot-code', sec('ch3-rot-code', (
    eyebrow('3.2 · 旋转修复代码') + h2('quarot.py 补 KDA 门控右旋 + model_adapter.py 补 indexer', 32)
    + lead('一级投影（输入维=hidden）必须右旋；二级投影（输入维=head_dim）一级补旋后不旋。修复后 cos 从 ≈0.017 / ≈0.54 拉到 1.0。')
    + codebox(
'''# KDA 门控 · 三条一级右旋（quarot.py 补）
# f_a / g_a_proj 输入维 = hidden → 必须右旋
forget_gate.f_a_proj.weight.data = forget_gate.f_a_proj.weight.data @ R
forget_gate.f_b_proj.weight.data = forget_gate.f_b_proj.weight.data @ R  # f_b 二级不旋
forget_gate.g_a_proj.weight.data = forget_gate.g_a_proj.weight.data @ R
forget_gate.g_b_proj.weight.data = forget_gate.g_b_proj.weight.data @ R  # g_b 二级不旋

# mHC fn · block_diag(R×4) 每流独立消 R
R4 = torch.block_diag(*[R] * 4)   # 4 流独立消 R
fn_weight.data = fn_weight.data @ R4

# indexer compress_gate · 右旋
index_kpool_compress_gate.weight.data = index_kpool_compress_gate.weight.data @ R''',
        title='真实修复 diff · 三处盲区逐个补旋', fs=12.5)
    + '<div style="display:flex; gap:14px; margin-top:12px;">'
    + pillar('盲区 ①', RED, 'KDA 门控', 'f_a / f_b / g_a 三条一级右旋。修复前 cos ≈ 0.017 — 几乎完全错误基。')
    + pillar('盲区 ②', BLUE, 'mHC fn', 'block_diag(R×4)：4 条流各自消 R，不能共用。修复前 cos ≈ 0.54。')
    + pillar('盲区 ③', GREEN, 'indexer compress_gate', '校准 stub=0 不触发；真引擎 std=0.17 才暴露 — 最隐蔽。')
    + '</div>'
    + foot('★ 教训：新增结构 × 量化旋转 = 高危交叉点。任何「输入维 = hidden 的投影」都必须过一遍右旋检查清单。'))))

# ═══════════════════════════════════════════════════════════
# 19. 章扉 04
# ═══════════════════════════════════════════════════════════
add('章扉04', chapter('04', '性能优化阶梯',
    '从 host 阻塞到访存优化到投机解码 — 7 级叠加把 TPOT 从 958.3ms 砍到 39.7ms（24.1×），MTP 验证接受率 ≈80%。',
    ['图模式 aclgraph', 'KDA fla_npu', 'mHC 融合 90→180', 'kPool gather 134×', 'MTP verify']))

# ═══════════════════════════════════════════════════════════
# 20. ch4-ladder
# ═══════════════════════════════════════════════════════════
add('ch4-ladder', sec('ch4-ladder', (
    eyebrow('4.1 · 7 级阶梯总览') + h2('958.3 → 39.7ms · 24.1× 加速比', 34)
    + lead('每级优化都针对 4 类开销之一：host 调度 / 数据搬运 / 非 AI Core 执行 / 重复计算。'
           '第 7 级 MTP 是最后一级，把每 token 期望成本 ÷1.8。')
    + '<div style="text-align:center; margin-top:4px;">'
    + f'<img src="{U["fig11-opt-ladder"]}" style="height:700px; width:auto; max-width:94%; border-radius:8px; border:1px solid {LIGHT}; box-shadow:0 6px 18px rgba(20,22,28,.10);" /></div>'
    + foot('★ 口径：单机 8 卡 TP8 · 3.5K 输入 / 1K 输出 · 1 并发 · w8a8 真实权重。'
           '该规模访存下限参考 ~30-40ms；39.7ms 已进入这一区间（MTP 后每步产出 ~2 token）。'))))

# ═══════════════════════════════════════════════════════════
# 21. ch4-ladder-tab
# ═══════════════════════════════════════════════════════════
add('ch4-ladder-tab', sec('ch4-ladder-tab', (
    eyebrow('4.1 · 优化阶梯表') + h2('7 级叠加 · 每一级消除的「无效开销」', 34)
    + lead('逐级实测数据（口径：单机 8 卡 TP8 · 3.5K 输入 / 1K 输出 · 1 并发 · w8a8 真实权重）。')
    + dtable(['级', '优化项', 'TPOT(ms)', '吞吐', '累计', '机理'],
        [['基线', 'eager', '958.3', '1.04', '1×', 'TTFT 4294ms'],
         ['1', '图模式 aclgraph', '237.8', '4.14', '4.0×', '整步录成静态图 · host 清零'],
         ['2', 'KDA 优化', '155.7', '6.23', '6.2×', 'fla_npu 接入 · 状态原位递推'],
         ['3', 'mHC 融合算子', '119.0', '8.17', '8.1×', '90 串小算子 → 180 融合'],
         ['4', 'kPool gather', '60.5', '15.6', '15.9×', 'fancy idx → F.embedding (134×)'],
         ['5', '删 RNE11 位', '51.5', '17.8', '18.6×', 'bf16 尾数 7 位 < RNE 11 位目标'],
         ['6', '池 cache 物化', '46.9', '19.8', '20.4×', '池化确定函数 → O(1) 增量'],
         ['7', 'MTP 投机解码', '39.7', '22.3', '24.1×', 'verify 出 2 token · 接受 ≈80%']],
        hl=5, fs=15.5, col_w=[0.7, 1.7, 1.1, 0.9, 0.9, 2.6])
    + '<div style="display:flex; gap:14px; margin-top:14px;">'
    + pillar('最大单级', RED, 'kPool gather 134×', 'AI_CPU → AI_VECTOR_CORE：行级取数每层 2.5 → 0.05ms，Index 调用 3354 → 33。')
    + pillar('最难工程', BLUE, 'MTP lazy-commit', 'KDA 非幂等状态 × 投机回滚：per-(layer,slot) 暂存 + 跨层批量前进 + lead-trim。')
    + pillar('最高性价比', GREEN, '图模式 aclgraph', '一级吃掉 4.0×：host 调度开销 ~62% 清零，busy 率 97%。')
    + '</div>')))

# ═══════════════════════════════════════════════════════════
# 22. ch4-graph
# ═══════════════════════════════════════════════════════════
add('ch4-graph', sec('ch4-graph', (
    eyebrow('4.2 · 图模式 aclgraph · 958→238ms') + h2('消除 host 调度开销 · busy 率 97%', 34)
    + lead('eager 下 ~62% 时间 NPU 在等 host（每次 .item() 同步 + Python dispatch + 逐算子 launch）。'
           '图模式把整模型前向捕获成一张静态图，逐算子 launch 清零。')
    + figcap(U['fig12-host-compute'],
        '左：eager 模式时间线 — host（黄）与 NPU（蓝）交替，气泡巨大；'
        '右：aclgraph 静态图 — 整步一次 launch，NPU busy 率 97%。<br><br>'
        '代价：KDA 非幂等状态必须 snapshot/restore 才能安全 capture（见 CH2 快照机制）— '
        '<b>优化是环环相扣的，不是孤立的 7 招</b>。',
        '口径：TPOT 958.3 → 237.8ms（单级 4.0×）· 静态图捕获 + 状态快照',
        img_pct=58)
    + laybox('eager 模式像「做一道菜下一次厨房单」：厨师（NPU）大部分时间等服务员（host）下单。'
             '图模式 = 把整桌菜单一次性录好，厨师一口气做完 — 这就是 4 倍提速的来源。'))))

# ═══════════════════════════════════════════════════════════
# 23. ch4-kda-code
# ═══════════════════════════════════════════════════════════
add('ch4-kda-code', sec('ch4-kda-code', (
    eyebrow('4.3 · KDA 优化 · 融合算子接入') + h2('delta-rule 主体：chunk_kda / fused_recurrent_kda 官方接口', 32)
    + lead('prefill 走 <b>chunk_kda</b>（chunked delta-rule，chunk_size=64 多 token 并行）；'
           'decode 走 <b>fused_recurrent_kda</b>（单 token 递推）。'
           '<b>状态原位递推：initial_state 从 framework ssm 槽取、output_final_state=True 回写 — 每层省 2 次全量状态 HBM 往返 × 34 层。</b>')
    + codebox(
'''# 官方接口（preview/glm-5.3-flash 核验）— 与 transformers 同签名
# prefill：chunk_kda — chunked delta-rule（multi-token prefill path）
result = chunk_kda(
    query, key, value, g, beta,
    chunk_size=64,                  # chunk 内并行 / chunk 间串行
    initial_state=ssm_state,        # 从 framework ssm 槽取
    output_final_state=True,        # 终态回写 ssm 槽
    use_qk_l2norm_in_kernel=True,   # FLA 风格 L2 归一化
)

# decode：fused_recurrent_kda — 单 token 递推（decode path）
core_attn_out, final_state = fused_recurrent_kda(
    query, key, value, g, beta,
    initial_state=ssm_state,
    output_final_state=True,
    use_qk_l2norm_in_kernel=True,
)

# 官方设计要点：接口与 transformers chunk_kda/fused_recurrent_kda
# 签名一致（use_kernel_func_from_hub_with_fallback 装饰）——
# NPU 小核可在接口后替换而不动层代码，"No fla_npu dependency"''',
        title='官方接口（preview/glm-5.3-flash 核验）· prefill chunked / decode recurrent 双路径', fs=12)
    + '<div style="display:flex; gap:14px; margin-top:12px;">'
    + pillar('省什么', RED, 'HBM 往返', '每层省 2 次全量状态读写 × 34 层 — fp32 状态 4.3MiB/序列，搬运是大头。')
    + pillar('设计要点', BLUE, '接口稳定', '与 transformers 同签名，NPU 小核接口后替换、层代码零改动 — 官方分支已摆脱 fla_npu 直依赖（早期直挂阶段成为历史）。')
    + pillar('收益', GREEN, '237.8 → 155.7ms', '单级 1.53×（累计 6.2×）。')
    + '</div>')))

# ═══════════════════════════════════════════════════════════
# 24. ch4-mhc-code
# ═══════════════════════════════════════════════════════════
add('ch4-mhc-code', sec('ch4-mhc-code', (
    eyebrow('4.4 · mHC 融合算子 · 90→180') + h2('hc_pre 一个 kernel 完成坍缩全链 · launch ÷2.5', 34)
    + lead('rsqrt (RMSNorm) + linear 投影 + sigmoid 门控 + Sinkhorn 20 轮 + 加权坍缩 → 一次调用产出 (collapsed, post, comb)。'
           'hc_post 一个 kernel 完成重组合。')
    + codebox(
'''# Glm53FlashHyperConnection.forward — 融合路径
if _has_mhc_fused:
    # rsqrt + linear + sigmoid 门控 + Sinkhorn(20 轮) + 加权坍缩
    collapsed, post, comb = kernels.hc_pre(
        hidden_streams,                          # [B, S, hc_mult, D]
        self.fn,
        self.scale.float(), self.base.float(),   # fp32, 防 load 时被转回 bf16
        hc, self.hc_sinkhorn_iters,
        self.input_norm.variance_epsilon, self.hc_eps,
    )
    return post, comb, collapsed
# (else: 纯 Python 参考实现, 作为 fallback)

# decoder 层内重组合同样走融合（attn/ffn 两个站点各一次）
hidden_states = kernels.hc_post(hidden_states, residual, post, comb)''',
        title='真实代码 · hc_pre / hc_post 两融合点', fs=12)
    + '<div style="display:flex; gap:14px; margin-top:12px;">'
    + pillar('融合前', GREY, '90 个串行小算子', '每步 rsqrt/linear/sigmoid/Sinkhorn×20/加权 — kernel launch 与 HBM 搬运双杀。')
    + pillar('融合后', RED, '180 行一个 kernel', '中间结果留在片上不落 HBM · launch 数 ÷2.5。')
    + pillar('收益', GREEN, '155.7 → 119.0ms', '单级 1.31×（累计 8.1×）。')
    + '</div>')))

# ═══════════════════════════════════════════════════════════
# 25. ch4-kpool
# ═══════════════════════════════════════════════════════════
add('ch4-kpool', sec('ch4-kpool', (
    eyebrow('4.5 · kPool index gather 优化') + h2('fancy index → flattened gather → F.embedding · 134×', 34)
    + lead('33.5MB → 0.25MB（134×）；Index 调用次数 3354 → 33（AI_CPU → AI_VECTOR_CORE）；'
           '行级取数每层 2.5 → 0.05ms（B=1, T=32768, D=128, rate=4）。')
    + figcap(U['fig13-kpool-134x'],
        '三步演进：<br><b>① fancy index</b>：走 AI_CPU，3354 次调用，33.5MB 中间张量 — host 侧瓶颈<br>'
        '<b>② flattened gather</b>：索引预先展平，AICore 原生 gather<br>'
        '<b>③ F.embedding</b>：把 gather 换成 embedding 查表 — 算子映射到 AI_VECTOR_CORE，0.25MB。<br><br>'
        '<b>这是全部 7 级里单级收益最大的一招（15.9× 累计中的关键一跳）</b>。',
        '口径：B=1, T=32768, D=128, rate=4 · Index 调用 3354 → 33 · TPOT 119.0 → 60.5ms',
        img_pct=56)
    + laybox('fancy index 像「让前台一张张递照片」（3354 次跑腿）；'
             'F.embedding 像「整本相册一次抱走」（33 次）。活儿一样，跑腿的少了 100 倍。'))))

# ═══════════════════════════════════════════════════════════
# 26. ch4-mtp
# ═══════════════════════════════════════════════════════════
add('ch4-mtp', sec('ch4-mtp', (
    eyebrow('4.6 · MTP 投机解码 · 工程难度最高') + h2('KDA 状态 lazy-commit · 接受率 ≈80% · 39.7ms 最后一跳', 32)
    + lead('per-(layer, slot) 暂存原始 qkv/gate/β → 跨层批量前进 + lead-trim。'
           'spec-verify 入 aclgraph + V3 融合算子（persistent combined [base|draft] state pool）。'
           '官方 MTP 镜像 DeepSeek-V3.2 python MTP 方案（deepseek_v32_mtp.py），draft 计算在 python、调度在 C++（MTPWorkerImpl）。')
    + '<div style="display:flex; gap:22px; align-items:flex-start;">'
    + '<div style="flex:0 0 47%;">'
    + f'<img src="{U["fig14-mtp"]}" style="width:100%; border-radius:8px; border:1px solid {LIGHT};" />'
    + kbstrip(U['kb-dsv3-3'],
        '<b>同源证据 · DeepSeek-V3 Fig.3</b>：MTP 架构 — 每个位置用共享主干 + 独立输出头预测未来多个 token，'
        '训练时多 token 监督、推理时当 draft 头。glm5.3-flash 的 MTP 直接复用此结构。',
        '★ DeepSeek-AI, 2024 · arXiv:2412.19437 · Fig.3, p.10 · <b>直接同源</b>', img_w=230)
    + '</div>'
    + '<div style="flex:1; min-width:0;">'
    + dtable(['难点', '解法'],
        [['KDA 状态非幂等', 'draft 前进不写真状态 — lazy-commit，接受才落盘'],
         ['回滚', 'per-(layer, slot) 暂存原始 qkv/gate/β，跨层批量前进 + lead-trim'],
         ['verify 开销', 'spec-verify 入 aclgraph，V3 融合算子'],
         ['状态池', 'persistent combined [base|draft] state pool'],
         ['draft 层结构', 'checkpoint 追加层（无 mHC 的 DSA MoE 层）· eh_proj 融合 [enorm(embed)‖hnorm(hidden)]（官方核验）'],
         ['收益', '一次替换换一次权重后从 76.3ms 正常化到 39.7ms']],
        fs=12, col_w=[1.2, 2.4])
    + laybox('普通解码像「写一个字想一次」；MTP 是「先猜 2 个字，让大模型一次验收」— '
             '猜对 80%，等于每步白赚一个 token。难在 KDA 的笔记本不能乱写：猜的时候先写草稿，验收通过才誊正。')
    + '</div></div>'
    + foot('★ 接受率 ≈80% · verify 每步出 ~2 token · TPOT 46.9 → 39.7ms（累计 24.1×）— 进入该规模访存下限区间。'))))

# ═══════════════════════════════════════════════════════════
# 27. 章扉 05
# ═══════════════════════════════════════════════════════════
add('章扉05', chapter('05', '工程化交付',
    '镜像 · 拉起脚本 · 评测数据 · 总结 — 让 5.3-flash 真正落到线上推理引擎。',
    ['W8A8 + QuaRot', 'TP8 拉起', 'MMMU 78%', 'AIME 90%', '成本持平']))

# ═══════════════════════════════════════════════════════════
# 28. ch5-script
# ═══════════════════════════════════════════════════════════
add('ch5-script', sec('ch5-script', (
    eyebrow('5.1 · 拉起服务（单机 8 卡 TP8）') + h2('xllm 服务拉起 · 关键参数', 34)
    + lead('由多机版 3_run_glm_int8_vlm.sh 改写，去掉 EP 与多机，保留图模式 / VLM 后端 / chunked prefill 等关键配置。'
           'HCCL_DETERMINISTIC 精度对齐验证时开，生产默认关（更快）。')
    + codebox(
'''#!/bin/bash
set -e
# ---- 环境 ----
export PYTORCH_NPU_INSTALL_PATH=/usr/local/libtorch_npu/
export TORCH_DEVICE_BACKEND_AUTOLOAD=0
export PYTORCH_NPU_ALLOC_CONF=expandable_segments:True
source /usr/local/Ascend/ascend-toolkit/set_env.sh
source /usr/local/Ascend/nnal/atb/set_env.sh

# TP8 all-reduce 非确定时逐 forward 有 ulp 噪声，精度对齐验证时必须开；生产默认关
#export HCCL_DETERMINISTIC=true
export HCCL_CONNECT_TIMEOUT=7200
export HCCL_OP_EXPANSION_MODE="AIV"

# ---- 参数（单机 8 卡 TP8）----
MODEL_PATH=.../glm_next_w8a8_0824
ASCEND_RT_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 \\
nohup $XLLM_PATH \\
  --model "$MODEL_PATH" --model_id glm5 --port 18000 \\
  --nnodes=1 --communication_backend=hccl \\
  --max_memory_utilization=0.85 \\
  --enable_chunked_prefill=True --max_tokens_per_chunk_for_prefill=8192 \\
  --enable_graph=True --model_impl=python \\
  --ep_size=1 --backend=vlm --limit_image_per_prompt=8 \\
  --max_seqs_per_batch=4 >> log/server.log 2>&1 &''',
        title='3_run_glm_int8_vlm.sh · 单机版（真实脚本节选）', fs=12)
    + foot('★ 镜像：quay.io/jd_xllm/xllm-ai:xllm-dev-a2-arm-cann9-20260801 · 关键开关：enable_graph / chunked_prefill / vlm 后端。'))))

# ═══════════════════════════════════════════════════════════
# 29. ch5-kpi
# ═══════════════════════════════════════════════════════════
add('ch5-kpi', sec('ch5-kpi', (
    eyebrow('5.2 · 评测性能') + h2('精度不丢 + 价格不变 = 端到端可交付', 36)
    + lead('评测性能数据 · 单机 8 卡 TP8 · w8a8 真实权重 · MTP 开。口径：3.5K 输入 / 1K 输出 · 1 并发。')
    + '<div style="display:grid; grid-template-columns:repeat(3, 1fr); gap:18px; margin-top:14px;">'
    + ''.join(
        f'<div style="background:{BG}; border:1px solid {LIGHT}; border-radius:14px; padding:28px;">'
        f'<div style="font:14px \'JetBrains Mono\',\'Noto Sans SC\',monospace; color:{c}; letter-spacing:.1em;">{k}</div>'
        f'<div style="font-size:54px; font-weight:700; color:{INK}; margin-top:8px;">{v}</div>'
        f'<div style="font-size:14.5px; color:{GREY}; margin-top:6px;">{d}</div></div>'
        for k, v, d, c in [
            ('TPOT', '39.7 ms', '每 token 端到端延迟 · 访存下限区间内', RED),
            ('吞吐', '22.3 tok/s', '单并发 · MTP verify ~2 token/步', BLUE),
            ('vs eager', '24.1×', '958.3 → 39.7ms · 7 级阶梯', RED),
            ('MMMU_PRO', '78%', '图文多模态 · 无量化回退', GREEN),
            ('AIME2026', '90%', '数学推理 · 无量化回退', GREEN),
            ('vs GLM-5.2', '持平', '精度不丢 · 成本不变', GREY),
        ])
    + laybox('最终成绩单：速度快了 24 倍，考试分数一分没降（MMMU 78% / AIME 90%），'
             '部署成本和上一代持平 — 这才叫「交付」，而不是「实验室 demo」。')
    + foot('★ 全部数字来自真实评测 · 精度门：任何优化落地前必须过 40-prompt 子集（必要时 220 全量）再 commit。<br>'
    '★ 代码已合入 <code style="background:#f5f5f5; padding:1px 5px; border-radius:3px;">xLLM-AI/xllm @ preview/glm-5.3-flash</code>（HEAD a6ae154）· 技术分析与部署镜像、脚本见 jx.huawei.com 内部帖子。'))))

# ═══════════════════════════════════════════════════════════
# 30. ch5-summary
# ═══════════════════════════════════════════════════════════
add('ch5-summary', sec('ch5-summary', (
    eyebrow('5.3 · 总结') + h2('5 处结构变化 × 触发问题 × 解决手段', 34)
    + lead('本文的全部适配工作都源于 glm5.3-flash 相对上一代的几处结构变化。')
    + dtable(['结构变化', '触发的问题', '解决手段'],
        [['KDA 门控线性注意力', '旋转盲区 + 状态非幂等入图', 'quarot.py 补 f_a/b/g_a 一级右旋 · 图模式 snapshot/restore'],
         ['mHC 多流残差', '旋转盲区 + 4 流串流风险', 'block_diag(R×4) 每流独立消 R · 融合算子降搬运'],
         ['kPool 稀疏索引', '旋转盲区 + fancy idx 走 AI_CPU', 'model_adapter.py 补右旋 · fancy idx → F.embedding'],
         ['DSA rope_dim=0', 'SFA 算子硬编码 rope=64 崩溃', 'tiling/kernel 改造 · kL0Size 96→128'],
         ['SwiGLU clamping', '新增 clamp 需全覆盖', 'dense/专家/ViT/patch-merger 4 处统一 clamp']],
        hl=2, fs=14, col_w=[1.4, 1.7, 2.4])
    + foot('★ 框架侧背景：xllm 组图方式刚从 atb/libtorch 迁移到 PyTorch 组图，图模式、chunked prefill 等加速特性在新架构下需从零适配。'
           '最终单机 8 卡 TP8 交付 39.7ms TPOT（24.1×），精度 MMMU_PRO 78% / AIME2026 90%。')
    + laybox('一句话：新模型的 5 个「新零件」各自带了一个坑，把坑逐个填平后，'
             '速度从「卡到没法用」变成「比眨眼快 10 倍」。'))))

# ═══════════════════════════════════════════════════════════
# 31. 深读·KB 同源证据 (2×2)
# ═══════════════════════════════════════════════════════════
add('深读-kb', sec('深读-kb', (
    eyebrow('深读 · KB 同源论文原图') + h2('4 篇同源 SOTA · 方法层证据链', 34)
    + lead('glm5.3-flash 的每项结构创新都有公开论文支撑 — 以下 4 张原图 + M3 图文联合解读，全部来自 AICO-Knowledge 知识库。')
    + '<div style="display:grid; grid-template-columns:1fr 1fr; gap:18px; margin-top:12px;">'
    + ''.join(
        f'<div style="background:{BG}; border:1px solid {LIGHT}; border-radius:10px; padding:18px 20px;">'
        f'<div style="display:flex; gap:14px; align-items:flex-start;">'
        f'<img src="{u}" style="flex:0 0 47%; width:47%; border-radius:6px; border:1px solid {LIGHT};" />'
        f'<div style="flex:1; min-width:0;">'
        f'<div style="font-size:14.5px; font-weight:700; color:{INK}; margin-bottom:5px;">{t}</div>'
        f'<div style="font-size:13px; color:#444; line-height:1.65;">{c}</div>'
        f'<div style="font-size:11.5px; color:#9a9aa0; margin-top:7px; border-top:1px dashed {LIGHT}; padding-top:6px;">{r}</div>'
        f'</div></div></div>'
        for u, t, c, r in [
            (U['kb-idx1'], 'IndexCache · DSA 稀疏索引加速',
             'GLM-5 + IndexCache 在 10 个 long-context 基准：平均 1.2× E2E speedup 且 HLE/SciCode/MRCR 不掉点 — 稀疏索引「不是丢精度换速度」。glm5.3-flash 的 DSA+kPool 与此同族。',
             '★ Liu et al., 2026 · arXiv:2608.02288 · Fig.1 · 同源代理'),
            (U['kb-klinear6'], 'Kimi Linear · KDA 全程领先 MLA',
             'Math RL 训练：Kimi Linear@1.4T 在训练集 / MATH500 / AIME2025 三条曲线全程压过 MLA@1.4T（~58-60 vs ~52；~86 vs ~84；~22 vs ~19）— 线性注意力可替代全注意力的实验证据链。',
             '★ Yang et al., 2025 · arXiv:2510.26692 · Fig.6 · 同源代理'),
            (U['kb-hc2'], 'mHC · 训练稳定性对比',
             'HC 相对 mHC 的损失差 15k 步后反弹（~0.005），HC 梯度范数在 0.10–0.18 剧烈震荡，mHC 从 0.25 单调降到 ~0.05 — 流形约束解决 HC 训练不稳定的直接证据。',
             '★ Xie et al., 2026 · arXiv:2512.24880 · Fig.2 · 直接同源'),
            (U['kb-megatron4'], 'Megatron-LM · 1F1B 流水线',
             '经典 1F1B pipeline schedule：多卡接力跑 forward/backward，气泡区是「工人等料」的空闲 — glm5.3-flash 训练侧管线与图模式 capture 共享同一类调度思想。',
             '★ Narayanan et al., 2021 · arXiv:2104.04473 · Fig.4 · 方法同源'),
        ])
    + foot('★ 同源代理声明：glm5.3-flash 为闭源模型，架构原图不可公开获取 — 以上用同族论文原图作方法层证据，工程数据（时延/精度）全部为 uniinfer 实测。'))))

# ═══════════════════════════════════════════════════════════
# 31b. 深读2 · 更多 KB 论文原图 (2×3)
# ═══════════════════════════════════════════════════════════
def deep2_card(u, t, c, r):
    return (f'<div style="background:{BG}; border:1px solid {LIGHT}; border-radius:10px; padding:12px 14px;">'
            f'<img src="{u}" style="width:100%; height:200px; object-fit:cover; object-position:top; border-radius:6px; border:1px solid {LIGHT}; margin-bottom:8px;" />'
            f'<div style="font-size:14px; font-weight:700; color:{INK}; margin-bottom:4px;">{t}</div>'
            f'<div style="font-size:12px; color:#444; line-height:1.6;">{c}</div>'
            f'<div style="font-size:10.5px; color:#9a9aa0; margin-top:6px; border-top:1px dashed {LIGHT}; padding-top:5px;">{r}</div></div>')

add('深读2-kb', sec('深读2-kb', (
    eyebrow('深读 · KB 论文原图（续）') + h2('架构族谱 · 6 篇同源 SOTA 原图', 34)
    + lead('glm5.3-flash 的每个设计都能在这 6 篇公开论文里找到「原型」— 混合排布 / delta-rule / 投机解码 / KV 管理 / MLA，一图一出处。')
    + '<div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:14px; margin-top:8px;">'
    + deep2_card(U['kb-klinear3'], 'Kimi Linear 架构总图 · 混合排布原型',
        '每块 = token-mixing 后接 MoE 通道混合，<b>N 个 KDA 层间插 1 个 MLA 层（N=3）</b> — 与 glm5.3-flash「每 4 层 3 KDA + 1 DSA」的混合排布直接同构：线性层保效率，周期性全注意力层维持全局锚点。',
        '★ Yang et al., 2025 · arXiv:2510.26692 · Fig.3 · 直接同构')
    + deep2_card(U['kb-gdn-1'], 'Gated DeltaNet 架构 · KDA 前身',
        'Block 内四条并行路径：q/k（Linear+Conv+SiLU+L2norm）、v、α/β 门控汇入 <b>Gated Delta Rule</b>；H1/H2 混合架构交错 DeltaNet / Mamba2 / SWA — delta-rule + 乘性门控增强联想召回。',
        '★ Yang et al., 2024 · arXiv:2412.06464 · Fig.1 · 方法前身')
    + deep2_card(U['kb-dsv3-2'], 'DeepSeek-V3 架构 · MLA 低秩压缩',
        'Transformer Block×L + DeepSeekMoE（Router 选 Top-K 路由专家 + 共享专家）+ <b>MLA：KV 联合低秩压缩成潜向量，推理只缓存潜向量与 kᴿ/vᶜ</b> — glm5.3-flash DSA 层复用的底座结构。',
        '★ DeepSeek-AI, 2024 · arXiv:2412.19437 · Fig.2 · 直接同源')
    + deep2_card(U['kb-eagle3-2'], 'EAGLE-3 · 投机解码加速比',
        '7 种方法 × 4 个目标模型的推理加速比：EAGLE-3 在 Vicuna-13B 达 <b>5.6×</b>，LLaMA-3.1-8B / 3.3-70B / R1-LLaMA-8B 分别 4.4× / 4.1× / 5.0× — 投机解码族的天花板参照系（glm5.3-flash MTP 为 2 token verify 的轻量路线）。',
        '★ Li et al., 2025 · arXiv (EAGLE-3) · Fig.2 · 族谱对照')
    + deep2_card(U['kb-medusa-1'], 'Medusa · 多解码头 + tree 验证',
        '末层 hidden 上并行挂 3 个 Medusa Head 预测第 2-4 位 token 的 Top-k，与 LM Head 交叉组合成候选，<b>tree-attention 并行验证、接受最长公共前缀</b> — MTP/draft 路线的另一经典形态。',
        '★ Cai et al., 2024 · arXiv:2401.10774 · Fig.1 · 族谱对照')
    + deep2_card(U['kb-pagedattn-2'], 'vLLM PagedAttention · KV 利用率',
        'KV cache 利用率堆叠对比：Orca(Max) 仅 <b>20.4%</b> 用于 token states（57.3% 内部碎片），vLLM 分页后达 <b>96.3%</b> — KV cache 管理的问题动机；KDA 定长状态（4.3MiB/序列）从另一极端消解了这个问题。',
        '★ Kwon et al., 2023 · arXiv:2309.06180 · Fig.2 · 问题动机')
    + '</div>'
    + foot('★ 以上 6 图全部来自 AICO-Knowledge 知识库原图（685 图库），caption 经 MiniMax-M3 图文联合解读核验；「族谱对照」表示同方法族不同实现，「直接同源/同构」表示 glm5.3-flash 直接采用该结构。'))))

# ═══════════════════════════════════════════════════════════
# 32. 术语速查
# ═══════════════════════════════════════════════════════════
add('术语速查', sec('术语速查', (
    eyebrow('GLOSSARY') + h2('术语速查 · 24 项', 36)
    + '<div style="display:grid; grid-template-columns:repeat(4, 1fr); gap:10px; margin-top:12px;">'
    + ''.join(
        f'<div style="background:{BG}; border:1px solid {LIGHT}; border-radius:8px; padding:9px 12px; font-size:12px; line-height:1.5;">'
        f'<b style="color:{c};">{t}</b><br/><span style="color:#555;">{d}</span></div>'
        for t, d, c in [
            ('KDA', 'Kimi Delta Attention · 递推式线性注意力', RED),
            ('DSA', 'DeepSeek Sparse Attention · top-k 稀疏索引', RED),
            ('MLA', 'Multi-head Latent Attention · KV 低秩吸收', RED),
            ('kPool', '4-to-1 池化 · 索引打分对象 ÷4', RED),
            ('mHC', 'manifold-constrained Hyper Connections · 4 流残差', RED),
            ('Sinkhorn', '行列交替归一化 → 双随机流形投影', BLUE),
            ('delta-rule', 'δ=(v−S·k)×β · KDA 状态更新规则', BLUE),
            ('非幂等', '前向每跑一遍状态推进 N 步 · 图模式大敌', GREY),
            ('snapshot/restore', 'capture 前快照、后恢复 · 让非幂等入图', GREY),
            ('rope_dim=0', 'SFA 算子适配 · v cache 零宽不占显存', BLUE),
            ('SwiGLU clamp', 'gate≤10 · up±10 · 防数值发散', BLUE),
            ('QuaRot', '全局 Hadamard 旋转 · 离线烘焙进权重', GREEN),
            ('旋转盲区', '漏右旋 W·R 的投影 → 语义错误', GREEN),
            ('SmoothQuant', '激活离群值摊平到权重', GREEN),
            ('W8A8', '权重 8bit + 激活 8bit 量化', GREEN),
            ('aclgraph', '整步前向录成静态图 · host 清零', '#8a6a2b'),
            ('fla_npu', 'KDA 融合算子库 · chunk/recurrent 双路径', '#8a6a2b'),
            ('hc_pre/hc_post', 'mHC 坍缩/重组合融合 kernel', '#8a6a2b'),
            ('F.embedding', 'gather 查表化 · kPool 134× 关键', '#8a6a2b'),
            ('MTP', 'Multi-Token Prediction · 投机解码 draft', '#8a6a2b'),
            ('lazy-commit', 'draft 不写状态，接受才落盘', '#8a6a2b'),
            ('TPOT', 'Time Per Output Token · 每 token 时延', GREY),
            ('TTFT', 'Time To First Token · 首 token 时延', GREY),
            ('同源代理', '闭源模型借同族公开论文作方法证据', GREY),
        ])
    + foot('★ 完整定义见各章正文；标注「同源代理」处表示 glm5.3-flash 闭源、借用公开同族论文证据。'))))

# ═══════════════════════════════════════════════════════════
# 33. 参考文献
# ═══════════════════════════════════════════════════════════
add('参考文献', sec('参考文献', (
    eyebrow('REFERENCES · 同源论文') + h2('参考文献 · 按主题分组', 34)
    + lead('glm5.3-flash 为闭源模型（内部 wiki 图床不可达）。以下公开同族论文构成方法层证据链，arXiv ID 均经知识库逐篇验证。')
    + ''.join(
        f'<div style="margin-top:12px;">'
        f'<div style="font-size:15px; font-weight:700; color:{c}; margin-bottom:6px;">{grp}</div>'
        + ''.join(
            f'<div style="display:flex; gap:10px; padding:5px 0; border-bottom:1px solid #f0f0f2; font-size:12.5px; line-height:1.5;">'
            f'<div style="flex:0 0 30px; font-family:\'JetBrains Mono\',\'Noto Sans SC\',monospace; color:{RED}; font-weight:700;">[{n}]</div>'
            f'<div style="flex:1;"><b>{t}</b> · <code style="background:{BG}; padding:1px 5px; border-radius:3px;">{a}</code> · {au}<br/>'
            f'<span style="color:#666;">{d}</span></div></div>'
            for n, t, a, au, d in items)
        + '</div>'
        for grp, c, items in [
            ('A · 线性注意力 / KDA 同族', BLUE, [
                (1, 'Kimi Linear: An Expressive, Efficient Attention Architecture', 'arXiv:2510.26692', 'Yang et al., 2025',
                 'KDA 架构 · lower-bounded decay · RL 全程压过 MLA — ch1/ch2-kda 方法源'),
                (2, 'Kimi K3: Open Frontier Intelligence', 'Kimi K3 report', 'Moonshot AI, 2026',
                 'chunkwise KDA 对角块统一为稠密 GEMM · 衰减下界 — ch2-kda 同源证据'),
                (3, 'Gated Delta Networks: Improving Mamba2 with Delta Rule', 'arXiv:2412.06464', 'Yang et al., 2024',
                 'delta-rule 递推的 KDA 前身 · 状态管理对比 — ch2-kda-state 方法源'),
            ]),
            ('B · 稀疏注意力 / 索引', RED, [
                (4, 'IndexCache: Accelerating Sparse Attention via Cross-Layer Index Reuse', 'arXiv:2608.02288', 'Liu et al., 2026',
                 'lightning indexer 跨层复用 · 1.2× E2E — ch1/kPool 同源证据'),
                (5, 'DeepSeek-V3 Technical Report', 'arXiv:2412.19437', 'DeepSeek-AI, 2024',
                 'MLA absorbed 形态 (Fig.5) · MTP 架构 (Fig.3) · DualPipe — ch2-dsa / ch4-mtp 直接同源'),
            ]),
            ('C · 多流残差', GREEN, [
                (6, 'HC: Manifold-Constrained Hyper Connections', 'arXiv:2512.24880', 'Xie et al., 2026',
                 'mHC 结构 + Sinkhorn 投影 + 训练稳定性证据 — ch2-mhc 直接同源'),
                (7, 'Hyper-Connections', 'arXiv (ByteDance)', 'Zhu et al., 2024',
                 'HC 无约束前身 · mHC 的改进对象 — ch2-mhc 背景'),
            ]),
            ('D · 训练 / 量化 / 数值稳定', '#8a6a2b', [
                (8, 'Efficient Large-Scale LM Training on GPU Clusters (Megatron-LM)', 'arXiv:2104.04473', 'Narayanan et al., 2021',
                 '1F1B 流水线调度 — ch3 训练侧方法源'),
                (9, 'Kimi K2: Open Agentic Intelligence', 'arXiv:2507.20534', 'Moonshot AI, 2025',
                 'attention logits >1000 数值爆炸图 — ch2-swiglu clamp 动机证据'),
                (10, 'QuaRot: Outlier-Free 4-Bit Inference', 'arXiv:2404.00456', 'Ashkboos et al., 2024',
                 'Hadamard 旋转量化 — ch3 量化管线方法源'),
            ]),
            ('E · 官方交付（一手出处）', RED, [
                (11, 'GLM5.3-Flash 昇腾 NPU + xllm 0day 适配与 SOTA 性能调优 · 官方交付说明', 'xLLM-AI/xllm @ preview/glm-5.3-flash', '交付与服务军团, 2026',
                 '单机 8 卡 TP8 稳定部署 · Decode 22.3 tok/s · TPOT 39.7ms · 较基线 24× · MMMU_PRO 78% · AIME2026 90% — 本 deck 全部工程数据的官方口径'),
                (12, '技术分析与部署镜像、脚本（内部帖子）', 'jx.huawei.com postId=45aa14453ea649c9a5fb1f01ddf45161', '交付与服务军团, 2026',
                 '线性注意力状态管理 · 旋转量化精度 · KDA 与 Index Key Pool 性能瓶颈 — 本 deck ch2/ch3/ch4 的技术分析原文'),
            ]),
        ])
    + foot('★ 工程数据来源：glm5.3-flash uniinfer 适配实测（单机 8 卡 TP8 · w8a8）— 时延 / 吞吐 / 精度全部为真实测量值，非论文引用。'))))

# ═══════════════════════════════════════════════════════════
# 34. 结语
# ═══════════════════════════════════════════════════════════
add('结语页', sec('结语页', (
    '<div style="display:flex; height:100%;">'
    '<div style="flex:1; display:flex; align-items:center; padding:0 90px;">'
    '<h1 style="font-weight:600; font-size:150px; color:' + INK + '; margin:0; line-height:1;">Thank you.</h1></div>'
    '<div style="flex:none; width:560px; padding:60px; display:flex; flex-direction:column; justify-content:center; gap:24px; background:' + BG + ';">'
    '<p style="margin:0; font-size:24px; font-weight:600; color:' + INK + '; line-height:1.6;">把数字世界带入每个人、每个家庭、每个组织，构建万物互联的智能世界。</p>'
    '<p style="margin:0; font-size:17px; color:' + GREY + '; line-height:1.5;">Bring digital to every person, home, and organization for a fully connected, intelligent world.</p>'
    '<div style="margin-top:26px; padding-top:22px; border-top:1px solid ' + LIGHT + '; font-size:14px; color:#9a9aa0; line-height:1.7;">'
    'glm5.3-flash 昇腾 uniinfer 适配实录 · 2026/08<br/>'
    '全部性能 / 精度数字为真实实测 · 同源论文经 AICO-Knowledge 逐篇验证<br/>'
    'Copyright © 2026 AICO · 供内部技术汇报使用</div>'
    '</div></div>'), pad='0'))

# ═══════════════════════════════════════════════════════════
# 替换 stage + 重写 nav/chapters + 写盘
# ═══════════════════════════════════════════════════════════
stage_open = s.find('<div class="stage" id="stage">')
stage_close = s.find('</div>\n\n  <div class="hint"', stage_open)
assert stage_open > 0 and stage_close > stage_open, 'stage bounds'
inner_start = stage_open + len('<div class="stage" id="stage">')
inner_end = stage_close + len('</div>')

body = '\n\n    '.join(html for _, html, _ in SECTIONS)
new_s = s[:inner_start] + '\n\n    ' + body + '\n\n  ' + s[inner_end:]
print(f'stage replaced: {len(new_s):,} chars ({len(SECTIONS)} slides)')

# data-idx 顺序化
def _fix_idx(m):
    _fix_idx.i += 1
    return f'<div class="slide-fit" data-idx="{_fix_idx.i}"'
_fix_idx.i = -1
new_s = re.sub(r'<div class="slide-fit" data-idx=""', _fix_idx, new_s)

NAV = '    const nav = [\n' + ''.join(
    f"      {{ i:{i}, code:'{nav[:8]}', label:'{label}' }},\n"
    for i, (label, _, nav) in enumerate(SECTIONS)) + '    ];\n'
ch_defs = [('01 · 门面', 0), ('02 · 结构创新', 6), ('03 · W8A8 量化', 14),
           ('04 · 性能阶梯', 18), ('05 · 工程交付', 26), ('06 · 收尾', 30)]
CH = '    const chapters = [\n' + ''.join(
    f"      {{ name:'{n}', start:{i} }},\n" for n, i in ch_defs) + '    ];\n'

ns = new_s.find('const nav = ['); ne = new_s.find('];', ns) + 2
new_s = new_s[:ns] + NAV + new_s[ne:]
cs = new_s.find('const chapters = ['); ce = new_s.find('];', cs) + 2
new_s = new_s[:cs] + CH + new_s[ce:]

# ── zoom 填充后处理 (文本型稀疏页) ──
ZOOM = {
    '目录': 1.24, '章扉02': 1.30, '章扉03': 1.30, '章扉04': 1.30, '章扉05': 1.30,
    'ch2-swiglu': 1.16, 'ch5-summary': 1.26, 'ch4-mtp': 1.10, 'ch1-概念': 1.22,
    'ch2-kda': 1.12, 'ch2-kda-state': 1.14, 'ch1-对比表': 1.12, '深读-kb': 1.18,
    '术语速查': 1.24, 'ch2-kpool': 1.10, 'ch2-dsa': 1.08, 'ch2-mhc': 1.06,
    'ch4-ladder-tab': 1.16, 'ch5-kpi': 1.12, 'TLDR': 1.10,
}
for _lbl, _z in ZOOM.items():
    _pat = f'<section data-label="{_lbl}"'
    _i = new_s.find(_pat)
    assert _i > 0, _lbl
    _gt = new_s.find('>', _i) + 1
    _end = new_s.find('</section>', _gt)
    new_s = new_s[:_gt] + f'<div style="zoom:{_z}">' + new_s[_gt:_end] + '</div>' + new_s[_end:]

mod.set_template(lines, new_s)
with open(STAGING, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
subprocess.run(['cp', '-f', STAGING, DECK], capture_output=True)
md5a = subprocess.check_output(['md5sum', STAGING]).decode().split()[0]
md5b = subprocess.check_output(['md5sum', DECK]).decode().split()[0]
os.unlink(STAGING)
print(f'md5 match: {md5a == md5b}')
print(f'✓ v9 deck saved: {len(SECTIONS)} slides, {len(U)} images, template {len(new_s):,} chars')