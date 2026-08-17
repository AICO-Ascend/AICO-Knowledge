# 论文深度解析知识库（extraction/）

> 对 `papers/` 下 50 篇论文做深度解析萃取，供技术报告撰写 / 论文总结时**快速插入合适技术图片 + 引用出处**。

## 目录结构

```
extraction/
├── <slug>.md              # 每篇论文的结构化解析（Obsidian-flavored：properties + 图表 embed + caption）
├── fulltext/<slug>.txt    # 每篇全文纯文本（供关键词检索 / 引用原文片段）
├── assets/<slug>-pNN.png  # 抽取的图表页渲染图（150 DPI）
├── figures_index.md       # ⭐ 主索引：按主题分组 + 精选深度解读，插图入口
└── minimax_captions.json  # MiniMax 多模态对关键架构图的技术解读（图路径 → 解读）
```

## 快速插图 + 引用（工作流）

### 1. 按主题找图
打开 `figures_index.md` → 「按主题分类」节。主题标签：`speculative` `sparse-attention` `kv-cache` `moe` `disaggregated-serving` `training` `rl` `multimodal` `long-context` `architecture`。

### 2. 优先用深度解读图
`figures_index.md` 顶部「⭐ 精选架构图」是 MiniMax 多模态解读过的核心方法 / 架构图，带 `[!tip] 技术解读`，最适合插技术报告做论据。

### 3. 插入图片
在 Obsidian / 任意 Markdown 里用 embed：
```
![[assets/eagle-speculative-sampling-...-p02.png]]
```
图片文件就在 `extraction/assets/`，复制到报告目录或直接引用路径即可。

### 4. 标注引用
每张图条目都带：**论文标题 + Fig.N + 页码 + 论文 wikilink `[[<slug>]]` + arxiv 链接**（见对应 `<slug>.md` 的 properties）。引用模板：
> 「EAGLE 通过在特征层自回归并引入超前一步的 token 序列解决特征预测不确定性 [EAGLE, Fig.4, arXiv:2401.15077]」

### 5. 检索原文片段
`grep -l "关键词" extraction/fulltext/*.txt` 找到论文，再 `<slug>.md` 看摘要 + 图表，或直接读 `<slug>.txt` 全文。

## 单篇 MD 结构

```markdown
---
paper_num / title / authors / date / arxiv / pdf / slug / tags
---
# 标题
> [!abstract] 摘要（原文）
## 元信息（日期/作者/arxiv/页数）
## 图表（原文 caption + 页码）
### Figure N (p.X)  ⭐MiniMax深度解读   ← 仅深度解读的图标⭐
![[assets/...png]]
> [!quote] caption
> [!tip] 技术解读（MiniMax 多模态）   ← 仅⭐图有
## 全文文本 → extraction/<slug>.txt
```

## 重新生成

```bash
cd /mnt/project/g00952465/AICO-knowledge
python3 skills/paper-extraction/extract_phase1.py  # 重跑 Phase 1（脚本已移至 skills/）（文本+图表+caption，merge MiniMax 解读）
```
MiniMax 深度解读增量加到 `extraction/minimax_captions.json`（key=图片相对路径 `assets/xxx.png` 或 `extraction/assets/xxx.png`），重跑脚本自动 merge。

## 外部工程接入（其他 project 怎么用）

本仓在 4 台服务器共享的 NFS（`/mnt/project/g00952465/AICO-knowledge`）上，任何工程可按**绝对路径**直接读取，无需拷贝。

**统一查询入口 `kb_query.py`**（不要手 grep）：

```bash
KB=/mnt/project/g00952465/AICO-knowledge/skills/paper-extraction/kb_query.py
python3 $KB stats                        # 库总量
python3 $KB search speculative decoding  # 论文检索（标题+全文打分排序）
python3 $KB fig architecture             # 按 caption 找图 → embed 路径+引用串
python3 $KB formula softmax              # 按内容找 LaTeX 公式（$$ 块直贴）
python3 $KB topics                       # 主题 → 论文映射
python3 $KB info <slug>                  # 单篇全卡片（路径/图数/公式数）
# 全部子命令支持 --json（agent/RAG 程序化消费）
```

**典型场景**：
- 写报告插图：`kb_query.py fig <关键词>` → 拿 `![[assets/...png]]` + `[slug, Fig.N, p.X]` 引用 → arxiv 号在 `papers.json` 或 MD frontmatter。
- 引用公式：`kb_query.py formula <关键词>` → 复制 `$$` 块。
- RAG 摄取：读 `extraction/papers.json` manifest → 按 `fulltext` 字段 chunk；或定时 `kb_query.py search --json`。
- Obsidian 图谱：把本仓加为 vault，`MOC.md` 为入口节点。

**Agent（Claude Code 等）提示词模板**：
> 论文知识库在 /mnt/project/g00952465/AICO-knowledge，检索用 `python3 skills/paper-extraction/kb_query.py <search|fig|formula|topics> <kw> [--json]`；图片在 extraction/assets/，引用格式 [slug, Fig.N, p.X, arXiv:ID]。

## 当前覆盖

- **61 篇论文**全文 + 图表 caption 萃取（515 张图）
- **22 张核心架构图**多模态深度解读（IndexCache / EAGLE-1/3 / Medusa / DFlash / JetSpec / Sarathi / Mooncake / SGLang / Step-3 / DeepSeek-V4 / Kimi K3 / PrfaaS / LongSpec / SpecExtend 等）
- 主索引 `figures_index.md`：精选区 + 主题分类 + 按论文；图谱导航 `MOC.md`；manifest `papers.json`

### 全部完成（2026-08-16 刷新）
61 篇全部深度萃取（515 图、22 张架构图多模态深度解读）。`verify_pdfs.py` 报 0 截断。
新增：`MOC.md` 主题图谱导航（wikilink 节点，Obsidian 图谱可视化）、`papers.json` 机器可读 manifest（RAG 摄取用）、`formulas.json` LaTeX 源公式库（arxiv e-print 提取，可直接粘贴）、单篇 MD 内「相关论文」交叉链接。

2026-08-16 增量：#57 Kimi K3 / #58 PrfaaS / #59 LongSpec / #60 SpecExtend / #61 A Survey of LLMs（源列表 58 条 diff 出 7 条新条目，2 条歧义待确认：Delivery Note、Reinforcement learning）。

## 工具脚本

- `extract_phase1.py` — 全量深度萃取（文本+图表+caption，merge MiniMax 解读）
- `chunk_download.py` — arxiv 大文件分块续传（应对网络截断）
