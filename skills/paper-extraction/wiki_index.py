#!/usr/bin/env python3
"""wiki_index.py — LLM Wiki 簿记层：index.md + log.md + 概念页种子。

参考 Karpathy "LLM Wiki" 模式（gist 442a6bf5）在本库的落地：
- **index.md**（内容目录）：LLM 回答查询时先读它定位页面，再钻取细节。
  覆盖 69 篇论文 MD + deep 深读 + 概念页 + 索引文件，每条一行摘要。
- **log.md**（编年日志）：append-only，`## [YYYY-MM-DD] op | detail` 统一前缀，
  `grep "^## \[" log.md | tail -5` 即可查最近动态（ingest/lint/crop-fix）。
- **wiki/concepts/*.md**（原子概念页）：一个概念一页，跨论文累积综合，
  Obsidian 图谱里作为 hub 节点。种子 = MOC 聚类成员 + moc_relations 谱系段
  的嵌入引用（单一事实源仍在 moc_relations，概念页只做结构化聚合）。
  种子幂等且不覆盖：已存在的概念页（可能已被夜间深读丰富）原样保留。

用法:
  wiki_index.py                 # 重建 index.md + 种子概念页（幂等）
  wiki_index.py --log "ingest | qwen3-vl-technical-report（+fig12 tab5）"
"""
import json, re, sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
OUT = REPO / "extraction"
CONCEPTS = REPO / "wiki" / "concepts"

# 概念页定义：(页 slug, 中文名, moc_relations 谱系段标题列表, 关联 MOC 聚类)
# 谱系段是策展的跨论文 lineage（单一事实源），概念页嵌入对应段；
# MOC 聚类提供成员结构。元段（全部论文/跨论文关系与演进/深读锚点）不建页。
CONCEPT_PAGES = [
    ("speculative-decoding", "推测解码", ["推测解码谱系", "推测解码 tree-attention 分支"], "speculative"),
    ("kv-cache", "KV Cache", ["KV cache 复用谱系", "KV-cache 架构性压缩谱系"], "kv-cache"),
    ("disaggregated-serving", "分离式推理服务与调度", ["调度谱系", "调度/disagg 谱系（第一轮深读补充）"], "disaggregated-serving"),
    ("training", "大规模训练系统", ["训练系统谱系"], "training"),
    ("normalization", "归一化原语", ["归一化原语谱系"], None),
    ("rl", "强化学习系统", ["RL 系统谱系"], "rl"),
    ("reasoning-distillation", "Reasoning 蒸馏", ["Reasoning 蒸馏谱系"], None),
    ("linear-attention", "线性/混合注意力", ["线性/混合注意力谱系"], None),
    ("npu-ascend", "NPU/Ascend 体系", ["NPU/Ascend 谱系"], None),
    ("frontier-models", "前沿模型", ["frontier 模型谱系"], None),
    ("residual-topology", "残差/层间拓扑", ["残差/层间拓扑谱系"], None),
    ("multimodal", "多模态/VLM", ["多模态/VLM 谱系"], "multimodal"),
    ("long-context", "长上下文", ["长上下文模型谱系"], "long-context"),
    ("sparsity-axes", "稀疏性轴", ["稀疏性谱系（Sparsity Axes）"], "sparse-attention"),
    ("llm-taxonomy", "LLM 全栈 taxonomy", ["LLM 全栈 taxonomy anchor"], None),
    ("table-learning", "结构化/表格学习", ["结构化/表格学习（正交分支）"], None),
    ("topic-modeling", "主题建模/文档相似度", ["主题建模/文档相似度（正交分支）"], None),
    ("moe", "MoE 架构", [], "moe"),
    ("architecture", "模型架构", [], "architecture"),
]


def moc_clusters():
    """MOC.md → {cluster: [(slug, title_line)]}"""
    clusters, cur = {}, None
    for line in (OUT / "MOC.md").read_text(encoding="utf-8").splitlines():
        m = re.match(r"## (.+?) \((\d+)\)\s*$", line)
        if m:
            cur = m.group(1)
            clusters[cur] = []
            continue
        m = re.match(r"- \[\[([^\]]+)\]\] — (.+)", line)
        if m and cur:
            clusters[cur].append((m.group(1), m.group(2)))
    return clusters


def relations_sections():
    """moc_relations.md → {段标题: 段文本}"""
    txt = (OUT / "moc_relations.md").read_text(encoding="utf-8")
    secs, cur, buf = {}, None, []
    for line in txt.splitlines():
        if line.startswith("## "):
            if cur:
                secs[cur] = "\n".join(buf).strip()
            cur, buf = line[3:].strip(), []
        elif cur:
            buf.append(line)
    if cur:
        secs[cur] = "\n".join(buf).strip()
    return secs


def seed_concepts():
    CONCEPTS.mkdir(parents=True, exist_ok=True)
    clusters = moc_clusters()
    secs = relations_sections()
    created, kept = 0, 0
    for slug, cn_name, rel_keys, cluster in CONCEPT_PAGES:
        page = CONCEPTS / f"{slug}.md"
        if page.exists():
            kept += 1
            continue
        members = list(clusters.get(cluster, [])) if cluster else []
        # 谱系段正文里的 [[wikilink]] 也是成员（深读策展的发现）
        seen = {s for s, _ in members}
        for key in rel_keys:
            for w in re.findall(r"\[\[([^\]|#]+)", secs.get(key, "")):
                w = w.strip()
                if w not in seen and (OUT / f"{w}.md").exists():
                    title = w
                    members.append((w, title))
                    seen.add(w)
        embeds = "\n".join(f"![[moc_relations#{k}]]" for k in rel_keys if k in secs)
        links = "\n".join(f"- [[{s}]] — {t}" for s, t in members)
        deep_links = "\n".join(
            f"- [[deep/{s}|{s}（深读）]]" for s, _ in members
            if (OUT / "deep" / f"{s}.md").exists())
        page.write_text(f"""---
concept: {cn_name}
papers: {len(members)}
updated: {date.today().isoformat()}
---

# {cn_name}（{slug}）

> 概念页（LLM Wiki 层）：跨论文累积综合，Obsidian 图谱 hub。
> 谱系叙述的单一事实源是 [[moc_relations]]，本页嵌入对应段落并随其更新。
> 新论文入库时由 full_pipeline / 夜间深读补充本页；lint 时检查成员完整性。

## 成员论文（{len(members)}）

{links or "（暂无）"}

## 深读笔记

{deep_links or "（暂无）"}

## 谱系（引自 [[moc_relations]]）

{embeds or "（暂无谱系段）"}
""", encoding="utf-8")
        created += 1
    return created, kept


def build_index():
    papers = json.loads((OUT / "papers.json").read_text(encoding="utf-8"))
    plist = papers if isinstance(papers, list) else papers.get("papers", [])
    clusters = moc_clusters()
    slug2cluster = {}
    for c, members in clusters.items():
        for s, _ in members:
            slug2cluster.setdefault(s, c)
    vis = json.loads((OUT / "visuals.json").read_text(encoding="utf-8"))
    lines = ["""# 📇 知识库内容索引（LLM-reads-first）

> LLM Wiki 簿记层的内容目录：回答查询时**先读本页定位，再钻取**。
> 由 `wiki_index.py` 在 full_pipeline 里自动重建（幂等），勿手改。
> 编年动态见 [[log]]；主题图谱见 [[MOC]]；跨论文谱系见 [[moc_relations]]。

## 使用约定

- 查论文 → 下方「论文」节按主题分组，每行：标题（链接）+ 一句定位 + 要素计数
- 查概念/谱系 → `wiki/concepts/` 原子概念页（跨论文综合，图谱 hub）
- 查图/表/公式 → [[INTERPRETATION_MAP]]（三层产物与 key 规则）
- 机器查询 → `kb_query.py search|fig|formula|topics|info|stats`（--json）

## 论文（%d 篇，按主题）
"""]
    by_cluster = {}
    for p in plist:
        slug = p["slug"]
        c = slug2cluster.get(slug, "other")
        by_cluster.setdefault(c, []).append(p)
    n_fig = n_tab = 0
    for c in sorted(by_cluster):
        lines.append(f"\n### {c}（{len(by_cluster[c])}）\n")
        for p in sorted(by_cluster[c], key=lambda x: x["slug"]):
            slug = p["slug"]
            v = vis.get(slug, {})
            nf = len(v.get("figures", []))
            nt = len(v.get("tables", []))
            n_fig += nf; n_tab += nt
            deep = " +深读" if (OUT / "deep" / f"{slug}.md").exists() else ""
            title = re.sub(r"\s+", " ", p.get("title", slug))[:80]
            lines.append(
                f"- [[{slug}|{title}]] — {p.get('date','?')} ｜ fig{nf} tab{nt}{deep}")
    n_concepts = len(list(CONCEPTS.glob("*.md"))) if CONCEPTS.exists() else 0
    concept_links = ""
    if CONCEPTS.exists():
        concept_links = "\n".join(
            f"- [[concepts/{p.stem}|{p.stem}]]"
            for p in sorted(CONCEPTS.glob("*.md")))
    lines.append(f"""
## 概念页（wiki/concepts/，{n_concepts} 页）

跨论文原子概念页：一个概念一页，累积综合 + 谱系嵌入 + 成员链接。
新论文 ingest 时按主题归属更新对应概念页。

{concept_links}

## 索引与清单文件

| 文件 | 内容 |
|---|---|
| [[MOC]] | 主题聚类图谱导航 |
| [[moc_relations]] | 跨论文演进谱系（机制级，人工/夜读维护） |
| [[figures_index]] | 全部图表主索引（⭐精选） |
| [[INTERPRETATION_MAP]] | 图/表/公式三层产物与 M3 解读 key 规则 |
| [[log]] | 编年日志（ingest/lint/crop-fix 动态） |
| papers.json | 论文 manifest（RAG 摄取入口；发表时间以 pub_month 字段为权威） |
| visuals.json | 裁剪图 manifest（fig {n_fig} + tab {n_tab} + eq） |
| minimax_captions.json | M3 图文联合解读（裁剪图 100%） |
| formulas.json | LaTeX 公式权威库 |

## 代码仓域与网页域（本索引由论文流水线重建 —— 三域全貌入口在此）

| 入口 | 内容 |
|---|---|
| repo_inventory.json | 134 仓清单 + 版本血缘 snapshots（重拉留历史快照） |
| repo_docs_index.json | 21,954 篇仓文档收割索引（九类分类/大纲/图片/互链） |
| repo_deep_index.json | 1,722 篇仓文档七节深读索引（85 仓） |
| repo_m3_captions.json | 881 张仓内图图文联合解读 |
| repo_cards/ + deep/repo-* | 仓卡片（机械骨架 / 分析层） |
| web_index.json | 网页注册表（抓取路由/版本线/深读登记） |
| web_deep_docs/ | 网页七节深读（表格逐字还原） |
| web_moc.md | 网页域知识地图（版本对照结论） |
| ../AGENTS.md | 面向 AI 系统的机器消费契约（铁律/注册表/RAG 建议） |
| ../bookshelf/SHELF.md | 面向人类学习者的知识书架（技术栈六层主线） |
""")
    (OUT / "index.md").write_text(
        "\n".join(lines).replace("%d 篇，按主题", f"{len(plist)} 篇，按主题"),
        encoding="utf-8")
    return len(plist), n_fig, n_tab


def append_log(entry):
    log = OUT / "log.md"
    if not log.exists():
        log.write_text("# 🕐 知识库编年日志（append-only）\n\n"
                       "> `## [YYYY-MM-DD] op | detail` 统一前缀，"
                       "`grep \"^## \\[\" log.md | tail -5` 查最近动态。\n",
                       encoding="utf-8")
    with log.open("a", encoding="utf-8") as f:
        f.write(f"\n## [{date.today().isoformat()}] {entry}\n")


def main():
    if "--log" in sys.argv:
        i = sys.argv.index("--log")
        append_log(sys.argv[i + 1])
        print("log appended")
        return
    np_, nf, nt = build_index()
    created, kept = seed_concepts()
    print(f"index.md: {np_} papers, fig {nf}, tab {nt}; "
          f"concepts: {created} seeded, {kept} kept")


if __name__ == "__main__":
    main()
