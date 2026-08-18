#!/usr/bin/env python3
"""orchestrate_deep_reread.py — 按论文维度一体化深读的编排器。

对每篇有 deep note 的论文，组装 subagent prompt：
  - 全文 .txt 路径
  - 该论文全部 M3 caption（从 minimax_captions.json 按 slug 过滤）
  - 已有 deep/<slug>.md 内容
输出每篇的 prompt 草稿 + 待处理论文列表，供人工/批量启动 subagent。

铁律：subagent 禁止 Read PNG，只读 .txt + caption 文本。
"""
import json, os
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CAP = REPO / "extraction" / "minimax_captions.json"
DEEP = REPO / "extraction" / "deep"
FULL = REPO / "extraction" / "fulltext"

PROMPT_TMPL = """你是 AICO-knowledge 的深度分析 agent。**铁律：禁止用 Read 工具直接开任何 PNG/JPG/图片文件**（你自身模型 text-only，会 400 报错）；图表上下文一律从下方提供的「M3 figure caption（文本）」获取，这些 caption 已由 MiniMax-M3 vision 模型对图做过结构化解读。

# 任务：按论文维度一体化深读，重写该论文的 deep note

## 一体化要求（铁律）
- 以**整篇论文**为单位理解，全文前后文必须一致：架构图要对照它前后文的公式推导与 ablation 表才解读；结果图数字要对照方法节叙述与超参表。
- 文本/图/表/公式**交织分析**，把图表解读**织进**核心问题/关键创新点/表格/对比各节，cite Figure N + M3 解读要点。禁止把图表分析拆成孤立片段硬塞。

## 输入
- 全文：extraction/fulltext/{slug}.txt
- 该论文全部 M3 figure caption（文本，安全可读）：
{captions_block}
- 已有 deep note（extraction/deep/{slug}.md，需参考其结构并增强）：
{existing_note_head}

## 输出：用 Write 覆盖 extraction/deep/{slug}.md，严格 6 段结构
1. ## 核心问题
2. ## 关键创新点（编号，每条=机制+效果+cite §+精确数字；凡涉及图，cite Figure N 并融入 M3 解读要点）
3. ## 表格（原文结构化；含 ablation/超参/结果表）
4. ## 与同类对比
5. ## 跨论文关系（→ MOC 谱系, wikilinks [[slug]]）
6. ## 局限与边界
中文散文 + 英文技术术语，cite § + 精确数字，无模糊总结，无臆造（原文/图没有的标 not-available）。

## 返回（给主 loop，不要写成文件内容）
- 一行 core contribution
- 跨论文关系 bullets（如需更新 moc_relations）
- 确认 deep note 已 Write
"""


def captions_for_slug(slug, cap):
    """返回该 slug 的 M3 caption: [(png_name, caption_text), ...]"""
    prefix = f"{slug}-p"
    out = []
    for k, v in cap.items():
        name = k.split('/')[-1]
        if name.startswith(prefix) and name.endswith('.png'):
            out.append((name, v))
    out.sort(key=lambda x: int(x[0].rsplit('-p', 1)[1].split('.')[0]))
    return out


def main():
    cap = json.loads(CAP.read_text())
    # 所有有 deep note 的论文
    slugs = sorted(p.stem for p in DEEP.glob("*.md"))
    print(f"deep notes: {len(slugs)}")
    # 统计每篇 caption 数
    have_cap = []
    for s in slugs:
        cs = captions_for_slug(s, cap)
        if cs:
            have_cap.append((s, len(cs)))
    print(f"papers with M3 captions: {len(have_cap)}")
    no_cap = [s for s in slugs if not captions_for_slug(s, cap)]
    print(f"papers with NO caption (text-only, no figures captioned): {len(no_cap)}")
    for s, n in sorted(have_cap, key=lambda x: -x[1])[:20]:
        print(f"  {n:3d}  {s}")
    # 写一份待处理清单
    (REPO / "extraction" / "deep_reread_queue.json").write_text(
        json.dumps({"with_captions": [s for s, _ in have_cap],
                    "no_captions": no_cap}, ensure_ascii=False, indent=1))
    print("-> wrote extraction/deep_reread_queue.json")


if __name__ == "__main__":
    main()
