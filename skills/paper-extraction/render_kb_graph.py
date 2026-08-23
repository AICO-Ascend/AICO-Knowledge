#!/usr/bin/env python3
"""render_kb_graph.py — render the knowledge base's topic graph + coverage stats as PNGs
for README embedding (shows extraction depth visually).

Outputs:
  docs/images/kb_topic_graph.png     — papers clustered by topic, edges = shared topics
  docs/images/kb_coverage_stats.png  — per-dimension coverage bars (fig/tab/formula/deep)
  docs/images/kb_pipeline.png        — pipeline architecture diagram
"""
import json, re, sys
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx

REPO = Path(__file__).resolve().parent.parent.parent
OUT = REPO / "extraction"
IMG = REPO / "docs" / "images"
IMG.mkdir(parents=True, exist_ok=True)

TOPIC_COLORS = {
    "speculative": "#E63946", "kv-cache": "#F4A261", "training": "#2A9D8F",
    "moe": "#457B9D", "rl": "#9B5DE5", "multimodal": "#00B4D8",
    "disaggregated-serving": "#E76F51", "long-context": "#606C38",
    "architecture": "#B5179E", "sparse-attention": "#3A86FF",
    "topic-modeling": "#8D99AE", "relational-table": "#6A4C93",
}


def load():
    papers = json.load(open(OUT / "papers.json"))
    vis = json.load(open((OUT / "visuals.json"))) if (OUT / "visuals.json").exists() else {}
    caps = json.load(open(OUT / "minimax_captions.json"))
    forms = json.load(open(OUT / "formulas.json"))
    return papers, vis, caps, forms


def short(title, n=28):
    t = title.split(":")[0] if ":" in title else title
    t = re.sub(r'[^\x00-\x7F]+', ' ', t).strip()  # drop CJK (no CJK font on this box)
    return (t[:n] + "…") if len(t) > n else t


def topic_graph(papers):
    G = nx.Graph()
    tag_of = {}
    for p in papers:
        slug, title, tags = p["slug"], p["title"], p.get("tags", [])
        main = tags[0] if tags else "misc"
        tag_of[slug] = main
        G.add_node(slug, label=short(title), tag=main, ntags=len(tags))
    # edges: papers sharing >=2 topic tags
    by_tag = defaultdict(list)
    for p in papers:
        for t in p.get("tags", []):
            by_tag[t].append(p["slug"])
    for t, ss in by_tag.items():
        for i in range(len(ss)):
            for j in range(i + 1, len(ss)):
                if G.has_edge(ss[i], ss[j]):
                    G[ss[i]][ss[j]]["w"] += 1
                else:
                    G.add_edge(ss[i], ss[j], w=1)
    # drop weak edges for readability (keep shared-topic edges; tags are sparse so >=1)
    G.remove_edges_from([(u, v) for u, v, d in G.edges(data=True) if d["w"] < 1])
    return G, tag_of


def render_graph(G, tag_of):
    fig, ax = plt.subplots(figsize=(22, 15), dpi=110)
    fig.patch.set_facecolor("#FAFAF8")
    ax.set_facecolor("#FAFAF8")
    pos = nx.spring_layout(G, k=2.6, iterations=120, seed=42)
    # edges
    widths = [G[u][v]["w"] * 0.5 for u, v in G.edges()]
    nx.draw_networkx_edges(G, pos, ax=ax, width=widths, alpha=0.25,
                           edge_color="#888888")
    # nodes by tag
    tags = sorted({d["tag"] for _, d in G.nodes(data=True)})
    for t in tags:
        ns = [n for n, d in G.nodes(data=True) if d["tag"] == t]
        nx.draw_networkx_nodes(
            G, pos, nodelist=ns, ax=ax,
            node_color=TOPIC_COLORS.get(t, "#999999"),
            node_size=[150 + 60 * G.nodes[n]["ntags"] for n in ns],
            alpha=0.9, edgecolors="white", linewidths=1.2, label=t)
    # labels
    labels = {n: d["label"] for n, d in G.nodes(data=True)}
    nx.draw_networkx_labels(G, pos, labels, font_size=6.5, ax=ax,
                            font_family="DejaVu Sans")
    ax.legend(loc="upper left", fontsize=11, frameon=True, title="Topic cluster",
              title_fontsize=12)
    ax.set_title("AICO-Knowledge — 69 Papers Topic Graph\n"
                 "(node = paper, color = primary topic, edge = shared topic, size = topic breadth)",
                 fontsize=15, pad=18)
    ax.axis("off")
    plt.tight_layout()
    fig.savefig(IMG / "kb_topic_graph.png", bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"  graph: {IMG/'kb_topic_graph.png'} ({G.number_of_nodes()} nodes, {G.number_of_edges()} edges)")


def render_stats(papers, vis, caps, forms):
    fig, axes = plt.subplots(1, 3, figsize=(19, 5.6), dpi=110)
    fig.patch.set_facecolor("#FAFAF8")
    n = len(papers)
    n_fig = sum(1 for p in papers if vis.get(p["slug"], {}).get("figures"))
    n_tab = sum(1 for p in papers if vis.get(p["slug"], {}).get("tables"))
    n_form = sum(1 for p in papers if forms.get(p["slug"]))
    n_eq_img = sum(1 for p in papers if vis.get(p["slug"], {}).get("formulas"))
    n_deep = len(list((OUT / "deep").glob("*.md")))
    n_cap = len(caps)

    # panel 1: coverage bars
    ax = axes[0]
    dims = ["Figures\n(cropped)", "Tables\n(as image)", "LaTeX\nformulas",
            "Formula\nscreenshots", "Deep notes\n(6-section)"]
    vals = [n_fig, n_tab, n_form, n_eq_img, n_deep]
    colors = ["#457B9D", "#2A9D8F", "#9B5DE5", "#F4A261", "#E63946"]
    bars = ax.barh(dims, vals, color=colors, alpha=0.88, height=0.62)
    for b, v in zip(bars, vals):
        ax.text(v + 0.4, b.get_y() + b.get_height() / 2, f"{v}/{n}",
                va="center", fontsize=11, fontweight="bold")
    ax.set_xlim(0, n + 12)
    ax.set_title(f"Per-dimension coverage (of {n} papers)", fontsize=13)
    ax.spines[["top", "right"]].set_visible(False)

    # panel 2: asset totals
    ax = axes[1]
    total_fig = sum(len(v.get("figures", [])) for v in vis.values())
    total_tab = sum(len(v.get("tables", [])) for v in vis.values())
    total_eq = sum(len(v.get("formulas", [])) for v in vis.values())
    total_form = sum(len(v) for v in forms.values() if v)
    labels = ["Cropped\nfigures", "Cropped\ntables", "Formula\nimages",
              "LaTeX\nformulas", "M3 vision\ncaptions"]
    counts = [total_fig, total_tab, total_eq, total_form, n_cap]
    bars = ax.bar(labels, counts, color=["#457B9D", "#2A9D8F", "#F4A261", "#9B5DE5", "#E63946"])
    for b, v in zip(bars, counts):
        ax.text(b.get_x() + b.get_width() / 2, v + 8, str(v),
                ha="center", fontsize=11, fontweight="bold")
    ax.set_title("Extracted asset inventory", fontsize=13)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_ylabel("count")

    # panel 3: topic distribution (group small slices to avoid label overlap)
    ax = axes[2]
    tc = Counter()
    for p in papers:
        for t in p.get("tags", [])[:1]:
            tc[t] += 1
    items = tc.most_common(8)
    big = [(t, c) for t, c in items if c >= 3]
    other = sum(c for t, c in items if c < 3) + sum(c for _, c in tc.most_common()[8:])
    if other:
        big.append(("other", other))
    ax.pie([c for _, c in big], labels=[f"{t} ({c})" for t, c in big],
           colors=[TOPIC_COLORS.get(t, "#8D99AE") for t, _ in big],
           autopct="%1.0f%%", startangle=90, textprops={"fontsize": 9.5},
           wedgeprops={"alpha": 0.88, "edgecolor": "white"})
    ax.set_title("Topic distribution (primary tag)", fontsize=13)

    fig.suptitle("AICO-Knowledge — Extraction Depth Dashboard", fontsize=15, y=1.02)
    plt.tight_layout()
    fig.savefig(IMG / "kb_coverage_stats.png", bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"  stats: {IMG/'kb_coverage_stats.png'}")


def render_pipeline():
    fig, ax = plt.subplots(figsize=(20, 6.5), dpi=110)
    fig.patch.set_facecolor("#FAFAF8")
    ax.set_facecolor("#FAFAF8")
    steps = [
        ("Source list\n(.bib / moonlight)", "#8D99AE"),
        ("Diff + arXiv\nresolve", "#606C38"),
        ("Chunked\ndownload", "#F4A261"),
        ("extract_phase1\ntext+fig+MOC", "#457B9D"),
        ("extract_visuals\ncrops", "#2A9D8F"),
        ("MiniMax-M3\ncaptions", "#E63946"),
        ("eprint LaTeX\nformulas", "#9B5DE5"),
        ("Deep read\n6-sec notes", "#B5179E"),
        ("Obsidian\n+ kb_query", "#00B4D8"),
    ]
    n = len(steps)
    for i, (label, color) in enumerate(steps):
        x = 0.02 + i * (0.97 / n)
        w = 0.97 / n - 0.006
        ax.add_patch(mpatches.FancyBboxPatch((x, 0.28), w, 0.42,
                     boxstyle="round,pad=0.006", facecolor=color, alpha=0.9,
                     edgecolor="white", linewidth=2, transform=ax.transAxes))
        ax.text(x + w / 2, 0.49, label, ha="center", va="center",
                transform=ax.transAxes, fontsize=9, color="white",
                fontweight="bold")
        if i < n - 1:
            ax.annotate("", xy=(x + w + 0.006, 0.49), xytext=(x + w - 0.001, 0.49),
                        xycoords="axes fraction",
                        arrowprops=dict(arrowstyle="-|>", color="#555", lw=1.6))
    ax.text(0.5, 0.88, "AICO-Knowledge — full_pipeline.py: one command, source list -> production KB",
            ha="center", transform=ax.transAxes, fontsize=13.5, fontweight="bold")
    ax.text(0.5, 0.10, "Iron rules: figures/tables via MiniMax-M3 vision | formulas from arXiv LaTeX source | "
            "per-paper integrated 6-section deep notes | token-safe push",
            ha="center", transform=ax.transAxes, fontsize=10.5, style="italic", color="#444")
    ax.axis("off")
    fig.savefig(IMG / "kb_pipeline.png", bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"  pipeline: {IMG/'kb_pipeline.png'}")


def main():
    papers, vis, caps, forms = load()
    G, tag_of = topic_graph(papers)
    render_graph(G, tag_of)
    render_stats(papers, vis, caps, forms)
    render_pipeline()
    print("DONE -> docs/images/")


if __name__ == "__main__":
    main()
