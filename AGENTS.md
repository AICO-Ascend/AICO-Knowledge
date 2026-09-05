# AGENTS.md — 面向 AI 系统的入口（AICO-Knowledge）

> 本仓是一个**预消化知识库**：信息的抽取、清洗、多模态理解、结构化组织已在入库时完成。
> 模型 / Agent / 自建 RAG 无需再做 PDF 解析、图表识别、网页抓取——直接消费结构化产物即可。
> 注意：本仓是知识库不是 RAG 服务，接入需自行 embedding/检索（建议见下「使用与接入」）。
> 人类学习者入口在 [bookshelf/](bookshelf/SHELF.md)；本文件是**机器消费契约**。
> 同一宏观理念的两面：AI 时代的瓶颈从"找答案"移到"提问题"——
> 书架让人知道"能问什么"（知识版图），本契约让 Agent 知道"能答什么、去哪取"（消费接口）。

## 三条铁律（消费前必读）

1. **出处可溯**：所有深读产物标注来源（arXiv ID / 仓内路径+ref / 原始 URL），引用时保留出处串。
2. **权威分层**：公式以 `extraction/formulas.json`（arXiv LaTeX 源）为权威；图解读以 `minimax_captions.json`（MiniMax-M3 图文联合解读）为权威；仓文档以 `repo_deep_docs/` 七节深读为权威。**禁止凭模型记忆重写这些内容**。
3. **机械层零臆造**：注册表（*.json）字段全部由脚本从原始源机械解析；发现不一致以原始源为准并提 issue 口径反馈。

## 快速定位（LLM reads first）

按序消费：
1. **`extraction/index.md`** — 全库内容目录（主题→论文/概念页映射），先读它定位再钻取
2. 本文件下方的注册表清单 — 机器可读的全面貌
3. 具体资产 — deep/ 深读、crops/ 裁剪图、repo_deep_docs/ 仓文档笔记

## 统一查询 CLI（程序化消费）

```bash
KB=skills/paper-extraction/kb_query.py     # 全部子命令支持 --json
python3 $KB stats                          # 库总量
python3 $KB search <关键词>                 # 论文检索
python3 $KB fig <关键词>                    # 按图解读找裁剪图（含引用串）
python3 $KB formula <关键词>                # 按内容找 LaTeX 公式
python3 $KB topics                         # 主题 → 论文映射
python3 $KB info <slug>                    # 单篇全卡片
```

## 注册表（机器可读全貌）

| 文件 | 域 | 内容 | 关键字段 |
|---|---|---|---|
| `extraction/papers.json` | 论文 | 69 篇 manifest | slug/title/arxiv/tags/md/fulltext/figs |
| `extraction/visuals.json` | 论文 | 裁剪图 manifest（685 图+429 表） | slug→figures/tables[{num,page,caption,path}] |
| `extraction/minimax_captions.json` | 论文 | 图/表 M3 图文联合解读（1600+） | 图路径→解读文本 |
| `extraction/formulas.json` | 论文 | LaTeX 公式库（479 条/58 篇） | slug→[{latex,context}] |
| `extraction/repo_inventory.json` | 代码仓 | 134 仓清单+**版本血缘** | slug/url/ref/latest_tag/snapshots[] |
| `extraction/repo_docs_index.json` | 代码仓 | 21,954 篇文档收割索引 | slug/path/type/title/outline/figures/internal_links |
| `extraction/repo_deep_index.json` | 代码仓 | 1,722 篇七节深读笔记索引 | slug/path/type/title/note |
| `extraction/repo_m3_captions.json` | 代码仓 | 881 张仓内图图文联合解读 | slug#path#fig→解读 |
| `extraction/web_index.json` | 网页 | 页面注册表（抓取路由/版本线/深读登记） | slug/url/route/title/deep_note |

## 使用与接入（含 RAG 摄取建议）

- **chunk 源**：`extraction/fulltext/<slug>.txt`（论文全文纯文本）；仓/网页域直接读 `repo_deep_docs/`、`web_deep_docs/` 的深读笔记（已是高信息密度摘要，比原文更适合 embedding）
- **元数据**：chunk 挂 slug + 域标记（paper/repo/web），过滤与混排用
- **图像**：`extraction/assets/crops/` 裁剪单图 + captions 配对可做图文 RAG
- **概念页**：`wiki/concepts/*.md` 是跨论文综合的"黄金 chunk"（19 页）

## Agent 技能（本仓自带 SKILL.md）

| 技能 | 位置 | 能力 |
|---|---|---|
| paper-extraction | `skills/paper-extraction/SKILL.md` | 论文萃取全链路 + 增量入库 + Lint gate |
| repo-extraction | `skills/repo-extraction/SKILL.md` | 代码仓稀疏归档 + 文档收割 + 版本血缘 + 深读 |
| web-extraction | `skills/web-extraction/SKILL.md` | 网页三级抓取路由 + 表格逐字深读 |
| bookshelf | `skills/bookshelf/SKILL.md` | 书架生成/策展（CURATION.md 协议） |

## 产物组织（三域对照）

| 产物 | 论文域 | 代码仓域 | 网页域 |
|---|---|---|---|
| 规范化原文 | `<slug>.md` | `repo_docs/<slug>/`（可重建） | `web_docs/<slug>.md` |
| 深读笔记 | `deep/<slug>.md`（6 段一体化） | `repo_deep_docs/<slug>/`（七节） | `web_deep_docs/<slug>.md`（七节） |
| 图解读 | `minimax_captions.json` | `repo_m3_captions.json` | —（UI 图标不入库） |
| 注册表 | `papers.json` 等 | `repo_*` 三件套 | `web_index.json` |
| 域地图 | `MOC.md` / `moc_relations.md` | 仓卡片 `repo_cards/` + `deep/repo-*` | `web_moc.md` |

## 版本与时效

- 论文发表时间以 arXiv ID（YYMM）为权威（`papers.json` 的 date 字段对批量入库的文章混入入库日期）
- 仓版本看 `repo_inventory.json` 的 `latest_tag` + `snapshots`（重拉自动留历史快照，可做版本 diff）
- 网页版本线在 URL 段（`web_index.json` 每页已机械提取）

## 编年日志

`extraction/log.md`（append-only，`## [date] op | detail` 格式）——审计知识库每次 ingest/lint/重构的历史。
