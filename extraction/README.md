# 论文深度解析知识库（extraction/）

> 对 `papers/` 下 69 篇论文做深度解析萃取，供技术报告撰写 / 论文总结时**快速插入合适技术图片 + 引用公式 + 取用深度分析**，同时是 Obsidian 图谱化 + RAG 友好的知识底座。

## 三条铁律（深度分析质量保证）

1. **图深度理解走 MiniMax-M3**：所有图解读来自 `minimax_captions.json`（MiniMax-M3 vision），subagent 禁止直接 Read PNG。
2. **公式以 `formulas.json` LaTeX 为权威源**：核心关键公式直接引用 LaTeX（`$$` 直贴、完全正确），禁止凭训练知识重写/补全；M3 caption 提供公式在图中的角色对照。
3. **按论文维度一体化深读**：单篇全文前后文一致，文本/图/表/公式交织，织进 6 段结构。

## 目录结构

```
extraction/
├── <slug>.md              # 每篇论文的结构化解析（Obsidian-flavored：properties + 摘要 + 图表 + 公式 + 相关论文）
├── deep/<slug>.md          # ⭐ 一体化深度分析（6 段：核心问题/关键创新点/表格/对比/跨论文关系/局限；图表+公式织入；![[deep/<slug>]] 嵌入各 MD）
├── fulltext/<slug>.txt     # 每篇全文纯文本（关键词检索 / 引用原文片段 / RAG chunk 源）
├── assets/<slug>-pNN.png   # 抽取的图表页渲染图（150 DPI）
├── figures_index.md       # ⭐ 主索引：⭐精选深度解读 + 按主题分组 + 按论文，插图入口
├── MOC.md                  # 🗺️ 主题图谱导航（wikilink 节点，Obsidian 图谱视图可视化）
├── moc_relations.md        # 跨论文关系谱系（人工维护，重跑不丢）
├── papers.json             # 机器可读 manifest（69 篇全字段，RAG/程序化摄取入口）
├── formulas.json           # LaTeX 源公式库（58 篇 479 条，$$ 块可直接粘贴，公式权威源）
├── minimax_captions.json   # 页级图多模态深度解读（548 张 100% 覆盖，图路径 → 解读）
└── sync_report.md          # 最近一次源列表同步报告（新增/待确认/失败/待解读）
```

## 快速插图 + 引用（工作流）

### 1. 按主题找图
打开 `figures_index.md` → 「按主题分类」节。主题标签：`speculative` `sparse-attention` `kv-cache` `moe` `disaggregated-serving` `training` `rl` `multimodal` `long-context` `architecture` `topic-modeling` `relational-table`。

### 2. 优先用深度解读图
`figures_index.md` 顶部「⭐ 精选架构图」是 MiniMax-M3 解读过的核心方法 / 架构图，带 `[!tip] 技术解读`，最适合插技术报告做论据。

### 3. 插入图片
在 Obsidian / 任意 Markdown 里用 embed：
```
![[assets/eagle-speculative-sampling-...-p02.png]]
```
图片文件就在 `extraction/assets/`，复制到报告目录或直接引用路径即可。

### 4. 标注引用
每张图条目都带：**论文标题 + Fig.N + 页码 + 论文 wikilink `[[<slug>]]` + arxiv 链接**（见对应 `<slug>.md` 的 properties）。引用模板：
> 「EAGLE 通过在特征层自回归并引入超前一步的 token 序列解决特征预测不确定性 [EAGLE, Fig.4, arXiv:2401.15077]」

### 5. 引用公式（权威正确）
`kb_query.py formula <关键词>` → 复制 `$$` 块（arxiv LaTeX 源，直接渲染，完全正确）。单篇 MD 的「关键公式」节也是 `$$` 块。**公式以 `formulas.json` LaTeX 为权威源**，deep note 内引用同一来源。

### 6. 取用深度分析
直接读 `extraction/deep/<slug>.md`。每篇 6 段：核心问题 / 关键创新点（机制+效果+精确数字+公式LaTeX+图M3解读）/ 表格（原文结构化）/ 与同类对比 / 跨论文关系谱系 / 局限与边界。深度分析里的公式与图表解读已织进各节（前后文一致）。

### 7. 检索原文片段
`grep -l "关键词" extraction/fulltext/*.txt` 找到论文，再 `<slug>.md` 看摘要 + 图表，或直接读 `<slug>.txt` 全文。（更省事：`kb_query.py search <关键词>`）

## 单篇 MD 结构

```markdown
---
paper_num / title / authors / date / arxiv / pdf / slug / tags
---
# 标题
> [!abstract] 摘要（原文）
## 元信息（日期/作者/arxiv/页数）
## 图表（原文 caption + 页码）
### Figure N (p.X)  ⭐深度解读          ← 仅深度解读的图标⭐
![[assets/...png]]
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
python3 skills/paper-extraction/sync_from_source.py --push   # 全链路+推送（幂等，无新增 ~40s）
```

手动单跑（调试/补做时）：
```bash
python3 skills/paper-extraction/extract_phase1.py    # 深度萃取（merge 解读+公式+MOC+manifest，幂等）
python3 skills/paper-extraction/orchestrate_deep_reread.py  # 生成 deep-reread 队列（含公式密集论文清单）
python3 skills/paper-extraction/eprint_formulas.py   # LaTeX 公式（失败冷却 3 天，--retry-failed 强制）
python3 skills/paper-extraction/verify_pdfs.py       # PDF 体检（修坏档前先跑）
```

深度解读增量加到 `extraction/minimax_captions.json`（key=图片相对路径 `extraction/assets/xxx.png`），重跑 `extract_phase1.py` 自动 merge。新论文深读（喂 captions+formulas+全文，守三铁律）用 `orchestrate_deep_reread.py` 编排。

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

## 当前覆盖（2026-08-21）

- **69 篇论文**全文 + 图表 caption 萃取（**685 条图 caption 目录 / 548 张渲染页**），`verify_pdfs.py` 报 0 截断（3 篇 truncated-PDF 已于 2026-08-19/20 全文回填并重新深读）
- **548 张**页级图经 MiniMax-M3 vision 精解读（**覆盖率 100%**，含 2026-08-21 图正则修复补抽的 68 张历史漏检图：deepseekmath/hc-manifold/cuda-agent/ascend-950/efficient-training，铁律：图理解全走 M3）
- **69 篇**一体化深度分析 note（`extraction/deep/`，6 段结构，图表+公式织入）
- **58 篇 479 条** LaTeX 源公式（e-print 提取，$$ 直贴，公式权威源）
- 跨论文谱系 `moc_relations.md`：14 大主题簇 + taxonomy anchor
- 图谱三件套：`MOC.md` 主题导航 + 单篇「相关论文」交叉链接 + `papers.json` manifest
- 一键同步 `sync_from_source.py` 已上线实测

## 工具脚本（skills/paper-extraction/）

- `sync_from_source.py` — ⭐ 一键同步编排（日常唯一入口）
- `kb_query.py` — 统一查询 CLI（search/fig/formula/topics/info/stats，--json）
- `m3_caption.py` — 火山网关 MiniMax-M3 图深度解读（--save 直写 minimax_captions.json）
- `extract_phase1.py` — 全量深度萃取（merge 解读+公式+MOC+manifest）
- `orchestrate_deep_reread.py` — 按论文维度深读编排（喂 captions+formulas+全文，三铁律，生成 deep-reread 队列）
- `bulk_caption.sh` — 可恢复批量 M3 caption 驱动（fcntl 锁，5 并行）
- `eprint_formulas.py` — arxiv e-print LaTeX 公式抽取
- `chunk_download.py` — arxiv 分块续传下载（应对网络截断）
- `verify_pdfs.py` — PDF 体检（截断/损坏/缺失/孤儿）
