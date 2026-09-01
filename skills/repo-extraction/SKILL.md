---
name: repo-extraction
description: Use when archiving a code repository into the AICO-Knowledge knowledge base — fetch a repo sparsely (docs+metadata only, GB-scale repos cost ~tens of MB), inventory its docs/version/structure, harvest and classify all Markdown docs (feature/api/guide/changelog/readme), generate an evidence-based repo card (positioning, architecture, feature map, version lineage) mirroring the paper-extraction KB flow, with a repos_download_list.txt file as the batch entry point. Complements paper-extraction (which handles arXiv PDFs) — this skill handles git repos (gitcode/github/codehub).
---

# repo-extraction — 代码仓分析与知识归档

## 这是什么

把**代码仓**纳入 AICO-Knowledge 知识库的流水线，与 `paper-extraction`（论文 PDF 萃取）并列、同一纪律：
机械层零臆造、LLM 深读带出处、产物全部登记进 extraction/ registry。

两类知识（对应用户目标）：
1. **文档信息**：仓内 docs/**/*.md / README / release notes — 特性文档往往比论文更工程化、更贴近实现
2. **版本与功能逻辑**：版本线（tag/release notes/配套关系）、特性地图、模块架构

与 AICO-Repo（gitcode.com/AICO-Ascend/AICO-Repo）的分工：他们的 `understanding-codebases`
面向**重构/迁移**的代码级走读（CodeGraph 重型引擎）；本技能面向**知识归档**（文档收割 + 版本功能提取），
镜像论文 KB 的轻量流水线。需要代码级深读时再去装他们的 Skill，本技能不重造。

## 输入：repos_download_list.txt

镜像 papers_download_list.txt，每行一仓：

```
# slug | git_url | ref(可选) | 备注
mindspeed | https://gitcode.com/Ascend/MindSpeed.git | master | 昇腾 MoE/并行训练加速库
```

## 三阶段流水线

```bash
# phase 1: 稀疏拉取 + 清单 (blob:none + no-cone sparse — 全 tree 可用, blob 只取文档/元数据)
python3 skills/repo-extraction/repo_fetch.py [--only slug1,slug2]
#   → repos_src/<slug>/ (稀疏克隆, 已 gitignore) + extraction/repo_inventory.json
#   登记: HEAD/日期/最新 tag/版本候选(pyproject>setup.py>version.py)/文档数/语言分布/顶层结构

# phase 2: 文档收割与分类 (零 LLM 纯机械)
python3 skills/repo-extraction/repo_extract_docs.py [--only slug]
#   → extraction/repo_docs/<slug>/ (文档原文, 图片改指 figures/ 并收割)
#   → extraction/repo_docs_index.json (每文档: 标题/类型/大纲/图片/内部链接/大小)
#   类型: readme·changelog·feature·api·guide·design·faq·overview·doc

# phase 3a: 卡片骨架 (机械层事实聚合)
python3 skills/repo-extraction/repo_card.py <slug>
#   → extraction/deep/repo-<slug>.md 骨架 (元信息/模块地图/特性聚类/changelog)

# phase 3b: LLM 分析层 (人工/Agent 深读填写, 纪律同论文 DEEP_LEARNING_PROTOCOL)
#   - 按仓维度一体化分析, 全文前后一致, 每个事实带仓库内出处 (文件路径)
#   - 关键 feature 文档做图文联合解读: 文档正文(上下文) + figures/ 图 → MiniMax-M3
#     (走 paper-extraction/m3_caption.py, 禁止无上下文裸读图)
```

## 产物与登记

| 产物 | 位置 | 说明 |
|---|---|---|
| 稀疏克隆 | `repos_src/<slug>/`（gitignore，可重拉） | blob:none + sparse，大仓只拉文档 |
| 仓清单 | `extraction/repo_inventory.json` | 版本候选/git 元数据/语言/结构 |
| 文档库 | `extraction/repo_docs/<slug>/` | 收割的 markdown + figures/ |
| 文档索引 | `extraction/repo_docs_index.json` | 分类/大纲/图片/内部链接 |
| 仓卡片 | `extraction/deep/repo-<slug>.md` | 定位/架构/特性地图/版本演进/关键特性深读 |

## 验证基线（2026-09-01 · MindSpeed）

- 稀疏拉取：1516 文件 tree，只下载 39MB（文档+元数据）
- 收割：149 篇 md（86 特性文档）+ 41 张图；分类分布 feature 86 / doc 30 / readme 14 / guide 8 / overview 7
- 版本裁决：git tag `v26.1.0_core_r0.12.1` 与 docs/zh/release_notes_core.md「产品版本信息」互证
  （26.1.0_core_r0.12.1 · 正式版 · 2026-07 · 配套 Megatron-Core 0.12.1）
- 验证文档：docs/zh/features/megatron_moe/megatron-moe-fb-overlap.md — 大纲/4 图收割/内部链接
  （→dualpipev.md）/3 图 M3 图文联合解读全部落地于 extraction/deep/repo-mindspeed.md §4.1

## 注意

- gitcode 直连可用（git clone）；github 走 codeload zip（网络策略，参考 memory ocr-it-review）
- `git ls-tree -r HEAD` 拿全 tree（blob:none 下免费），按需 `git show` 补取文件
- 内部链接（feature 文档互链）已登记在 docs_index，做特性关系图时直接用
- 版本命名约定各仓不同，inventory 的 version_candidates 全量保留，裁决交给 phase 3 + release notes 互证
