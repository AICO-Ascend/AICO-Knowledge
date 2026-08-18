#!/usr/bin/env python3
"""orchestrate_deep_reread.py — 按论文维度一体化深读的编排器。

对每篇有 deep note 的论文，组装 subagent prompt：
  - 全文 .txt 路径
  - 该论文全部 M3 caption（从 minimax_captions.json 按 slug 过滤）
  - 该论文全部 LaTeX 公式（从 formulas.json 按 slug 过滤）  ← 公式权威源
  - 已有 deep/<slug>.md 内容
输出每篇的 prompt 草稿 + 待处理论文列表，供人工/批量启动 subagent。

铁律（三条）：
1. subagent 禁止 Read PNG（text-only 模型，400）；图表上下文走 minimax_captions.json 文本。
2. 公式必须以 formulas.json 的 LaTeX 为权威源（可渲染、完全正确），不得靠训练知识
   重写 .txt 里缺失/乱码的公式；M3 caption 提供公式在架构图中的角色对照（LaTeX↔图双源校验）。
3. 以整篇论文为单位一体化分析，文本/图/表/公式交织，禁止拆孤立片段。
"""
import json, os
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CAP = REPO / "extraction" / "minimax_captions.json"
FORMULAS = REPO / "extraction" / "formulas.json"
DEEP = REPO / "extraction" / "deep"
FULL = REPO / "extraction" / "fulltext"

PROMPT_TMPL = """你是 AICO-knowledge 的深度分析 agent。**铁律（三条，全部强制）**：

1. **禁图直读**：禁止用 Read 工具直接开任何 PNG/JPG/图片文件（你自身模型 text-only，会 400 报错）；图表上下文一律从下方「M3 figure caption（文本）」获取，这些 caption 已由 MiniMax-M3 vision 模型对图做过结构化解读。

2. **公式权威源 = formulas.json LaTeX**（未来跨 project 复用要求关键公式**完全正确**）：
   - 论文的核心/关键公式必须**以下方提供的 formulas.json LaTeX 为准**（直接引用、可渲染，用 `$$...$$` 包裹），**禁止**凭训练记忆重写、改写或补全 .txt 里缺失/乱码的公式。
   - .txt 里若公式抽成空白/乱码（PDF 把公式当图片），**只认 formulas.json LaTeX + M3 caption**，不得臆造。
   - **LaTeX ↔ M3 双源校验**：把 LaTeX 公式与 M3 对架构图/数据流图的解读对照——公式里出现的变量/算子在图中如何连线、对应哪个 block，写进创新点机制叙述。M3 caption 若提及图内公式/表达式，与 formulas.json LaTeX 交叉核验后再用。
   - 每个关键公式给：LaTeX 渲染 + 一句话机制 + cite Eq./§号 + 与图/表/前后文的对照。

3. **一体化**：以整篇论文为单位，全文前后文一致（架构图↔公式推导↔ablation 表；结果图数字↔方法节↔超参表）；文本/图/表/公式交织，把图表与公式解读**织进**核心问题/关键创新点/表格/对比各节。禁止拆孤立片段。

# 任务：按论文维度一体化深读，重写该论文的 deep note

## 输入
- 全文：extraction/fulltext/{slug}.txt
- 该论文全部 M3 figure caption（文本，安全可读）：
{captions_block}
- 该论文全部 LaTeX 公式（formulas.json，权威源，直接引用勿改写）：
{formulas_block}
- 已有 deep note（extraction/deep/{slug}.md，先 Read 参考其结构与已有内容，再增强重写）：
{existing_note_head}

## 输出：用 Write 覆盖 extraction/deep/{slug}.md，严格 6 段结构
1. ## 核心问题
2. ## 关键创新点（编号，每条=机制+效果+cite §+精确数字；凡涉及公式，引用 formulas.json LaTeX 渲染 + 一句话机制；凡涉及图，cite Figure N 并融入 M3 解读要点）
3. ## 表格（原文结构化；含 ablation/超参/结果表）
4. ## 与同类对比
5. ## 跨论文关系（→ MOC 谱系, wikilinks [[slug]]）
6. ## 局限与边界
中文散文 + 英文技术术语，cite § + 精确数字，无模糊总结，无臆造（原文/图/公式没有的标 not-available）。

## 返回（给主 loop，不要写成文件内容）
- 一行 core contribution
- 跨论文关系 bullets（如需更新 moc_relations，否则说明 existing sufficient）
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


def formulas_for_slug(slug, formulas):
    """返回该 slug 的 LaTeX 公式列表: [latex_str, ...]（formulas.json 权威源）。
    formulas.json 结构: {slug: [{env, latex}, ...]}。"""
    entries = formulas.get(slug) or []
    out = []
    for e in entries:
        if isinstance(e, dict) and e.get("latex"):
            out.append(e["latex"])
        elif isinstance(e, str):
            out.append(e)
    return out



def main():
    cap = json.loads(CAP.read_text())
    formulas = json.loads(FORMULAS.read_text()) if FORMULAS.exists() else {}
    # 所有有 deep note 的论文
    slugs = sorted(p.stem for p in DEEP.glob("*.md"))
    print(f"deep notes: {len(slugs)}")
    # 统计每篇 caption 数 + 公式数
    have_cap = []
    for s in slugs:
        cs = captions_for_slug(s, cap)
        fs = formulas_for_slug(s, formulas)
        if cs:
            have_cap.append((s, len(cs), len(fs)))
    print(f"papers with M3 captions: {len(have_cap)}")
    no_cap = [s for s in slugs if not captions_for_slug(s, cap)]
    print(f"papers with NO caption (text-only, no figures captioned): {len(no_cap)}")
    # 公式密集论文（>=5 formulas）= 公式权威源重跑候选
    formula_heavy = [(s, n, f) for s, n, f in have_cap if f >= 5]
    print(f"formula-heavy (>=5 formulas, rerun candidates): {len(formula_heavy)}")
    for s, n, f in sorted(have_cap, key=lambda x: -x[1])[:20]:
        print(f"  cap={n:3d} form={f:3d}  {s}")
    # 写一份待处理清单
    (REPO / "extraction" / "deep_reread_queue.json").write_text(
        json.dumps({"with_captions": [s for s, _, _ in have_cap],
                    "formula_heavy": [s for s, _, _ in formula_heavy],
                    "no_captions": no_cap}, ensure_ascii=False, indent=1))
    print("-> wrote extraction/deep_reread_queue.json")


if __name__ == "__main__":
    main()
