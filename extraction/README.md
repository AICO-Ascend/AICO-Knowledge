# 论文深度解析知识库（extraction/）

> 对 `papers/` 下 50 篇论文做深度解析萃取，供技术报告撰写 / 论文总结时**快速插入合适技术图片 + 引用出处**。

## 目录结构

```
extraction/
├── <slug>.md              # 每篇论文的结构化解析（Obsidian-flavored：properties + 图表 embed + caption）
├── <slug>.txt             # 每篇全文纯文本（供关键词检索 / 引用原文片段）
├── assets/<slug>-pNN.png  # 抽取的图表页渲染图（150 DPI）
├── figures_index.md       # ⭐ 主索引：按主题分组 + 精选深度解读，插图入口
├── minimax_captions.json  # MiniMax 多模态对关键架构图的技术解读（图路径 → 解读）
└── extract_phase1.py      # 萃取脚本（可重跑）
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
`grep -l "关键词" extraction/*.txt` 找到论文，再 `<slug>.md` 看摘要 + 图表，或直接读 `<slug>.txt` 全文。

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
python3 extraction/extract_phase1.py   # 重跑 Phase 1（文本+图表+caption，merge MiniMax 解读）
```
MiniMax 深度解读增量加到 `extraction/minimax_captions.json`（key=图片相对路径 `assets/xxx.png` 或 `extraction/assets/xxx.png`），重跑脚本自动 merge。

## 当前覆盖

- 50 篇论文全文 + 图表 caption 萃取（308 张图）
- 11 张核心架构图 MiniMax 多模态深度解读（IndexCache / EAGLE-1/3 / Medusa / DFlash / JetSpec / Sarathi / Mooncake / SGLang / Step-3 / DeepSeek-V4）
- 主索引 `figures_index.md`：精选区 + 主题分类 + 按论文
