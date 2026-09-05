# 论文深度解析知识库（extraction/）

> 入口导航：人类学习者 → ../bookshelf/SHELF.md；AI 系统/Agent/RAG → ../AGENTS.md。
> 本文件是 extraction/ 目录的详细使用说明（论文域为主，仓/网页域注册表见 AGENTS.md）。

> 对 `papers/` 下 69 篇论文做深度解析萃取，供技术报告撰写 / 论文总结时**快速插入合适技术图片 + 引用公式 + 取用深度分析 + 取用跨元素关联**，同时是 Obsidian 图谱化 + RAG 友好的知识底座。

## 四条铁律（深度分析质量保证）

1. **图深度理解走 MiniMax-M3**：所有图解读来自 `minimax_captions.json`（MiniMax-M3 vision），**上下文增强解读**——crop 图 + 论文正文引用段落联合喂 M3（`context_caption.py`），subagent 禁止直接 Read PNG。
2. **公式以 `formulas.json` LaTeX 为权威源**：核心关键公式直接引用 LaTeX（`$$` 直贴、完全正确），禁止凭训练知识重写/补全；M3 caption 提供公式在图中的角色对照。
3. **按论文维度一体化深读**：单篇全文前后文一致，文本/图/表/公式交织，织进 6 段结构。
4. **图/表/公式/文本跨元素关联**（2026-08-25 落地）：每篇 MD 顶部自动生成 `## 方法链（Cross-Element Synthesis）` 章节，从 fig/tab 块的「论文作用/论证结论/方法链地位」文本自动聚合，按论文论证链顺序串联；`cross_element_synthesis.py` 幂等执行。

## 架构与 Wiki 三层落地

参考 [Karpathy LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) raw→wiki→schema 三层模式：

- **Raw（不可变）**：`papers/` PDF + `archive/paper_source_moonlight.bib`
- **Wiki（LLM 全权维护）**：本目录 `extraction/` + `wiki/concepts/` 概念页 + `extraction/index.md` 内容目录 + `extraction/log.md` 编年日志
- **Schema（规范）**：`skills/paper-extraction/SKILL.md` + `DEEP_LEARNING_PROTOCOL.md` + 各脚本 docstring

**三个操作**：
1. **Ingest**：`python3 skills/paper-extraction/full_pipeline.py --push`（10 步：sync→萃取→裁剪→M3→公式→merge→**Lint gate**→深读→Wiki→push）
2. **Query**：先读 `extraction/index.md` 定位，再钻取；机器走 `kb_query.py --json`；好答案回填 `wiki/concepts/` 复利
3. **Lint**：全量机审（`audit_crops.py` → `discriminate_audit.py` → `autofix_crops.py` → 复核闭环）；orphan crops / phantom caption / M3 缺解读等体检问题按对应铁律修复并记 `log.md`

## 目录结构

```
extraction/
├── index.md                # 📚 LLM-reads-first 内容目录（按主题定位+概念页+索引文件表，先读它）
├── log.md                  # 📚 编年日志（append-only `## [date] op | detail`）
├── <slug>.md               # 每篇论文的结构化解析（Obsidian-flavored：properties + 摘要 + 方法链 + 图表 + 公式 + 相关论文）
├── deep/<slug>.md           # ⭐ 一体化深度分析（6 段：核心问题/关键创新点/表格/对比/跨论文关系/局限；图表+公式织入）
├── fulltext/<slug>.txt      # 每篇全文纯文本（关键词检索 / 引用原文片段 / RAG chunk 源）
├── assets/<slug>-pNN.png    # 抽取的图表页渲染图（150 DPI）
├── assets/crops/<slug>-figNN.png  # ⭐ 裁剪单图（报告直接插入）
├── assets/crops/<slug>-tabNN.png  # ⭐ 裁剪表格（429 张）
├── assets/crops/<slug>-eqNN.png   # ⭐ 公式截图（无 LaTeX 源论文兜底）
├── figures_index.md         # ⭐ 主索引：⭐精选深度解读 + 按主题分组 + 按论文，插图入口
├── MOC.md                   # 🗺️ 主题图谱导航（wikilink 节点，Obsidian 图谱视图可视化）
├── moc_relations.md         # 跨论文关系谱系（人工维护，重跑不丢）
├── papers.json              # 机器可读 manifest（69 篇全字段，RAG/程序化摄取入口）
├── formulas.json            # LaTeX 源公式库（58 篇 479 条，$$ 块可直接粘贴，公式权威源）
├── visuals.json             # 裁剪图 manifest（fig/tab/eq 的 path/page/num）
├── ar5iv_crops.json         # 坏字体/坏结构 PDF 的 ar5iv 替换清单 + 手工区域保护
├── minimax_captions.json    # 多模态深度解读（727 ⭐ 张全覆盖，路径 → 解读）
└── crop_audit.json          # Lint gate 审计结果（机审判决 + 复核状态）
```

## 快速插图 + 引用（工作流）

### 1. 按主题找图
打开 `figures_index.md` → 「按主题分类」节。主题标签：`speculative` `sparse-attention` `kv-cache` `moe` `disaggregated-serving` `training` `rl` `multimodal` `long-context` `architecture` `topic-modeling` `relational-table`。

### 2. 优先用深度解读图
`figures_index.md` 顶部「⭐ 精选架构图」是 MiniMax-M3 解读过的核心方法 / 架构图，带 `[!tip] 技术解读`，最适合插技术报告做论据。

### 3. 插入图片
在 Obsidian / 任意 Markdown 里用 embed：
```
![[assets/crops/<slug>-figNN.png]]
```
图片文件就在 `extraction/assets/crops/`，复制到报告目录或直接引用路径即可（1115 张单元素裁剪，全是已 clean 单图）。

### 4. 标注引用
每张图条目都带：**论文标题 + Fig.N + 页码 + 论文 wikilink `[[<slug>]]` + arxiv 链接**（见对应 `<slug>.md` 的 properties）。引用模板：
> 「EAGLE 通过在特征层自回归并引入超前一步的 token 序列解决特征预测不确定性 [EAGLE, Fig.4, arXiv:2401.15077]」

### 5. 引用公式（权威正确）
`kb_query.py formula <关键词>` → 复制 `$$` 块（arxiv LaTeX 源，直接渲染，完全正确）。单篇 MD 的「关键公式」节也是 `$$` 块。**公式以 `formulas.json` LaTeX 为权威源**，deep note 内引用同一来源。

### 6. 取用深度分析
直接读 `extraction/deep/<slug>.md`。每篇 6 段：核心问题 / 关键创新点（机制+效果+精确数字+公式LaTeX+图M3解读）/ 表格（原文结构化）/ 与同类对比 / 跨论文关系谱系 / 局限与边界。深度分析里的公式与图表解读已织进各节（前后文一致）。

### 7. 取用跨元素关联
每篇 MD 顶部 `## 方法链（Cross-Element Synthesis）` 章节自动聚合该篇 fig/tab/eq 的「论文作用/论证结论」，按论文链顺序串联——读这一节就能掌握作者怎么用图表论证核心论点。完整跨元素论证见 `extraction/deep/<slug>.md`（独立文件，含公式↔图↔表双源校验）。

### 8. 检索原文片段
`grep -l "关键词" extraction/fulltext/*.txt` 找到论文，再 `<slug>.md` 看摘要 + 图表，或直接读 `<slug>.txt` 全文。（更省事：`kb_query.py search <关键词>`）

## 单篇 MD 结构

```markdown
---
paper_num / title / authors / date / arxiv / pdf / slug / tags
---
# 标题
> [!abstract] 摘要（原文）
## 元信息（日期/作者/arxiv/页数）
## 方法链（Cross-Element Synthesis）         ← ⭐ 跨元素关联（自动聚合 fig/tab/eq 论证）
> 本节由各 fig/tab/eq 的「论证/作用」聚合，按论文论证链顺序串联
- **Figure N**：...
- **Table N**：...
## 图表（原文 caption + 页码）
### Figure N (p.X)  ⭐深度解读          ← 仅深度解读的图标⭐
![[assets/crops/...png]]
> [!quote] caption
> [!tip] 技术解读（多模态）             ← 仅⭐图有
## 关键公式（LaTeX 源，可直接粘贴）      ← 有 e-print 的篇目（权威源 formulas.json）
$$ ... $$
## 相关论文                            ← 自动交叉链接（共享标签+标题相似度）
- [[<slug>]] — 标题
## 全文文本 → extraction/fulltext/<slug>.txt
![[deep/<slug>]]                       ← 嵌入一体化深度分析（6 段）
```

## 重新生成 / 刷新

日常刷新**不要**手动跑单个脚本，用一键编排：

```bash
cd /mnt/project/g00952465/AICO-knowledge
python3 skills/paper-extraction/full_pipeline.py --push   # 10 步全链路+推送（幂等，无新增 ~1-2 分钟）
```

10 步流水线：`sync_from_source` → `extract_phase1` → `extract_visuals` → **上下文增强 M3 解读** → `eprint_formulas` → `extract_phase1 (merge)` → **Lint gate**（`audit_crops`→`discriminate_audit`→`autofix_crops`）→ `orchestrate_deep_reread` → `wiki_index` → token-safe push。

手动单跑（调试/补做时）：
```bash
python3 skills/paper-extraction/extract_phase1.py    # 深度萃取（merge 解读+公式+MOC+manifest+figures_index，幂等）
python3 skills/paper-extraction/extract_visuals.py   # 图/表/公式区域裁剪（幂等跳过已裁）
python3 skills/paper-extraction/context_caption.py   # 上下文增强 M3 解读（crop+正文段落联合喂 M3，幂等）
python3 skills/paper-extraction/cross_element_synthesis.py  # 每篇 MD 顶部「方法链」章节（幂等）
python3 skills/paper-extraction/orchestrate_deep_reread.py  # 生成 deep-reread 队列（含公式密集论文清单）
python3 skills/paper-extraction/eprint_formulas.py   # LaTeX 公式（失败冷却 3 天，--retry-failed 强制）
python3 skills/paper-extraction/verify_pdfs.py       # PDF 体检（修坏档前先跑）
python3 skills/paper-extraction/wiki_index.py        # Wiki 簿记层（重建 index.md + 概念页种子）
```

深度解读增量加到 `extraction/minimax_captions.json`（key=图片相对路径 `extraction/assets/xxx.png`），重跑 `extract_phase1.py` 自动 merge。新论文深读（喂 captions+formulas+全文，守四铁律）用 `orchestrate_deep_reread.py` 编排。

## 外部工程接入（其他 project 怎么用）

本仓在 4 台服务器共享的 NFS（`/mnt/project/g00952465/AICO-knowledge`）上，任何工程可按**绝对路径**直接读取，无需拷贝。

**统一查询入口 `kb_query.py`**（不要手 grep）：

```bash
KB=/mnt/project/g00952465/AICO-knowledge/skills/paper-extraction/kb_query.py
python3 $KB stats                        # 库总量
python3 $KB search speculative decoding  # 论文检索（标题+全文打分排序）
python3 $KB fig architecture             # 按 caption 找图 → embed 路径+引用串
python3 $KB formula softmax              # 按内容找 LaTeX 公式（$$ 块直贴，权威正确）
python3 $KB topics                       # 主题 → 论文映射
python3 $KB info <slug>                  # 单篇全卡片（路径/图数/公式数）
# 全部子命令支持 --json（agent/RAG 程序化消费）
```

**取深度分析**（跨 project 复用核心成果）：直接读 `extraction/deep/<slug>.md`。每篇含核心问题、关键创新点（机制+效果+精确数字+公式LaTeX+图M3解读）、结构化表格、同类对比、跨论文谱系、局限。公式已校验为 LaTeX 权威源、图已 M3 解读，可直接引用。

**典型场景**：
- 写报告插图：`kb_query.py fig <关键词>` → 拿 `![[assets/...png]]` + `[slug, Fig.N, p.X]` 引用 → arxiv 号在 `papers.json` 或 MD frontmatter。
- 引用公式：`kb_query.py formula <关键词>` → 复制 `$$` 块（权威正确）。
- 取深度分析：读 `extraction/deep/<slug>.md`（6 段一体化，公式+图表已织入）。
- RAG 摄取：读 `extraction/papers.json` manifest → 按 `fulltext` 字段 chunk；或定时 `kb_query.py search --json`。
- Obsidian 图谱：把本仓加为 vault，`MOC.md` 为入口节点。

**Agent（Claude Code 等）提示词模板**：
> 论文知识库在 /mnt/project/g00952465/AICO-knowledge。检索用 `python3 skills/paper-extraction/kb_query.py <search|fig|formula|topics> <kw> [--json]`；深度分析在 extraction/deep/<slug>.md（6 段，公式LaTeX权威源+图M3解读已织入）；图片在 extraction/assets/，引用格式 [slug, Fig.N, p.X, arXiv:ID]。

## 当前覆盖（2026-08-25）

- **69 篇论文**全文 + 图表 caption 萃取（**685 条图 caption 目录 / 548 张渲染页 / 1115 张裁剪单图**），`verify_pdfs.py` 报 0 截断
- **727 ⭐ 张**裁剪图经 MiniMax-M3 vision 精解读（**覆盖率 100%**，全部为「上下文增强解读」：crop 图 + 论文正文引用段落联合喂 M3）
- **69 篇**一体化深度分析 note（`extraction/deep/`，6 段结构，图表+公式织入）
- **69 篇**「## 方法链」跨元素关联章节（每篇 MD 顶部，自动聚合 fig/tab/eq 的「论文作用/论证结论」，按论文链顺序串联）
- **58 篇 479 条** LaTeX 源公式（e-print 提取，$$ 直贴，公式权威源）
- **429 张**裁剪表格 + **4 张**公式截图（兜底）
- 跨论文谱系 `moc_relations.md`：14 大主题簇 + taxonomy anchor
- 图谱三件套：`MOC.md` 主题导航 + 单篇「相关论文」交叉链接 + `papers.json` manifest
- Wiki 簿记：`index.md`（LLM-reads-first 内容目录）+ `log.md`（编年日志）+ 19 页 `wiki/concepts/` 原子概念页（Karpathy LLM Wiki 落地）
- 一键同步 `full_pipeline.py --push` 10 步流水线（**Lint gate 已永久嵌入 step 7**，新论文入库自动机审→白名单→规则重裁闭环，一遍过 95.5%）
- 96 张坏字体/坏结构论文裁剪由 `ar5iv_replace.py` + 手工 PDF 区域保护（`ar5iv_crops.json` overlay）

## 工具脚本（skills/paper-extraction/）

**⭐ 日常唯一入口**：
- `full_pipeline.py` — 10 步全链路一条命令（sync→extract→visuals→M3→formulas→merge→Lint→deep→wiki→push）

**Ingest / 同步 / 萃取**：
- `sync_from_source.py` — 源表 diff→下载→体检→索引追加（`full_pipeline` step 1）
- `extract_phase1.py` — 深度萃取（merge 解读+公式+MOC+manifest+figures_index，幂等）
- `extract_visuals.py` — 图/表/公式区域裁剪成单图（`assets/crops/`）
- `context_caption.py` — ⭐ 上下文增强 M3 解读（crop+正文段落联合喂 M3，幂等跳过）
- `m3_caption.py` — 火山网关 MiniMax-M3 图深度解读（--save 直写 minimax_captions.json）
- `eprint_formulas.py` — arxiv e-print LaTeX 公式抽取
- `chunk_download.py` — arxiv 分块续传下载（应对网络截断）

**Lint gate（step 7）**：
- `audit_crops.py` — 全库 M3 逐张判决
- `discriminate_audit.py` — 二阶白名单（合法子图/长 caption/原版排版 overlap/代码 listing 图）
- `autofix_crops.py` — 规则重裁闭环
- `crop_audit.json` — 审计结果（裁决+复核状态，CI gate）

**Wiki 簿记层**：
- `wiki_index.py` — 📚 重建 index.md + 概念页种子 + log.md 记帐（Karpathy LLM Wiki 落地）
- `cross_element_synthesis.py` — ⭐ 每篇 MD 顶部「方法链」跨元素章节（从 fig/tab 论证自动聚合）
- `orchestrate_deep_reread.py` — 按论文维度深读编排（喂 captions+formulas+全文，四铁律，生成 deep-reread 队列）

**查询 / 工程消费**：
- `kb_query.py` — 统一查询 CLI（search/fig/formula/topics/info/stats，--json）
- `render_kb_graph.py` — 知识图谱/覆盖统计图生成

**修复 / 兜底**：
- `verify_pdfs.py` — PDF 体检（截断/损坏/缺失/孤儿）
- `ar5iv_replace.py` — 坏字体/坏结构 PDF 的 ar5iv 原图替换 + matplotlib 表格渲染
