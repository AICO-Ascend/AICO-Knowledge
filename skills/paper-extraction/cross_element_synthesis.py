#!/usr/bin/env python3
"""cross_element_synthesis.py — 每篇 <slug>.md 顶部加「方法链」章节。

从 paper MD 现成的 fig/tab/eq 解读（每块的「原文论证 / 论文作用 / 方法链地位」）
聚合出顶层「方法链 / Methodology Chain」章节，把图/表/公式的论证角色串成一条主线。

读 extraction/<slug>.md → 抽取 fig/tab 块的论证文本 → M3 总结（或本地启发式拼接）
→ 在 `## 元信息` 之后插入 `## 方法链（Cross-Element Synthesis）` 章节。

幂等：已有该章节的跳过。
"""
import json, re, sys, time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
OUT = REPO / "extraction"

# 这三段提示模板用来在每个 fig/tab 块末尾已经写好的「论证/作用」摘出来
# 我们的目标不是再调用 M3（开销大），而是从现有 MD 自抽取
PAT_ARG = re.compile(r"原文论证[：:](.+?)(?:\n\n|\Z)", re.S)
# 实测发现 paper MD 多用「**论文作用**」「**论证结论**」「**方法链地位**」bold 段，
# 也兼容旧「原文论证」/「论证」平文本。三个正则一起匹配取最长者。
PAT_ROLE_BOLD = re.compile(r"\*\*(?:论文作用|论证结论|方法链地位)\*\*[：:](.+?)(?:\n\n|\Z)", re.S)
PAT_ROLE = re.compile(r"(?:方法链地位|论文作用|论证结论)[：:](.+?)(?:\n\n|\Z)", re.S)
# 新式（图解读 v3）的图/表证据段不再用「论证结论」前缀，转写为「该图论证核心结论：
# …」「该图作为 …」「架构核心图」「在论文链路中…证据作用」等富语义表达。
# 兜底取首段「该图…」「…核心图」类语义段落作为方法链输入
PAT_FIG_EVIDENCE = re.compile(
    r"(?:该图(?:论证核心结论|作为|论证|是)|"
    r"在论文链路中.*?(?:证据|作用)|"
    r"架构核心图|该表(?:是|为|说明|展示)|"
    r"该(?:实验|表格|章节)[一-龥]{0,8}(?:核心|总览|实证|关键|方法链))"
    r"[：:](.+?)(?:\n\n|\Z)", re.S)
# 紧贴图后第一段「该图/该表/该实验 + 中文句末」短描述（≥10 字为有效）
PAT_SHORT_DESC = re.compile(
    r"(?:该图|该表|该实验|该公式)[，：:]?\s*"
    r"([一-龥、，。；：""''「」—\-()（）0-9A-Za-z·\.]{15,200})", re.S)
PAT_FIG = re.compile(r"### (Figure|Fig\.?)\s*(\d+)", re.I)
PAT_TAB = re.compile(r"### Table\s*(\d+)", re.I)
PAT_EQ = re.compile(r"^## 关键公式", re.M)


def extract_section(txt, start_pat):
    """从 paper MD 抽取方法链草料：每个 fig/tab 的论证 + 作用文本。"""
    out = []
    # 找所有 ### Figure N / ### Table N 块
    blocks = re.split(r"(?=^### (?:Figure|Fig\.?|Table)\s*\d+)", txt, flags=re.M)
    for blk in blocks:
        if not re.match(r"^### (?:Figure|Fig\.?|Table)\s*\d+", blk, re.I):
            continue
        # 拿块首的 fig/tab 编号
        m = re.match(r"^### ((?:Figure|Fig\.?|Table)\s*\d+)", blk, re.I)
        if not m:
            continue
        label = m.group(1)
        # 找论证 + 作用（按优先级：bold > 平文本 > 新式「该图...」）
        arg = PAT_ARG.search(blk)
        role = PAT_ROLE_BOLD.search(blk) or PAT_ROLE.search(blk)
        role_txt_built = role.group(1).strip()[:200] if role else ""
        # 新式兜底：新解读协议不再标 bold，直接「该图论证核心结论：…」
        if not role_txt_built:
            m_ev = PAT_FIG_EVIDENCE.search(blk)
            if m_ev:
                role_txt_built = m_ev.group(0).strip()[:200]
        if not role_txt_built:
            m_sd = PAT_SHORT_DESC.search(blk)
            if m_sd:
                role_txt_built = m_sd.group(1).strip()[:200]
        arg_txt = arg.group(1).strip()[:200] if arg else ""
        if not arg_txt and not role_txt_built:
            continue
        out.append((label, arg_txt, role_txt_built))
    return out


def synth(label_arg_role_list, slug):
    """本地启发式拼装方法链段落——不调 M3，廉价稳定。"""
    if not label_arg_role_list:
        return None
    lines = ["> 本节由各 fig/tab/eq 的「论证/作用」聚合，按论文论证链顺序串联。\n"]
    for label, arg, role in label_arg_role_list[:30]:  # cap 30
        if arg:
            lines.append(f"- **{label}**：{arg.split(chr(10))[0]}")
        elif role:
            lines.append(f"- **{label}**：{role.split(chr(10))[0]}")
    lines.append(f"\n> 完整跨元素论证见 `![[deep/{slug}]]`（独立文件，含公式↔图↔表双源校验）。")
    return "\n".join(lines)


def main():
    n_added = 0
    n_skipped = 0
    for md in sorted(OUT.glob("*.md")):
        # 跳过非论文文件
        if md.name in ("index.md", "MOC.md", "figures_index.md",
                       "moc_relations.md", "README.md", "sync_report.md",
                       "backfill_log.md"):
            continue
        slug = md.stem
        txt = md.read_text()
        if "## 方法链" in txt or "## 跨元素" in txt:
            n_skipped += 1
            continue
        # 抽取 fig/tab 论证
        items = extract_section(txt, None)
        chain = synth(items, slug)
        if not chain:
            continue
        # 在「## 元信息」之后插入
        new_section = f"\n## 方法链（Cross-Element Synthesis）\n\n{chain}\n"
        # 找到「## 元信息」块结束位置（下一个 ## 或 #!abstract 之后）
        idx = txt.find("## 元信息")
        if idx < 0:
            continue
        # 找下一个 ## 位置
        next_h = re.search(r"^## ", txt[idx+10:], re.M)
        if not next_h:
            continue
        insert_pos = idx + 10 + next_h.start()
        new_txt = txt[:insert_pos] + new_section + txt[insert_pos:]
        md.write_text(new_txt)
        n_added += 1
    print(f"added={n_added} skipped={n_skipped}")


if __name__ == "__main__":
    main()