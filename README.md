# AICO-knowledge

收集整理 AI 相关技术论文、代码仓来源、分析文章等，建成可「快速插图 + 引用公式 + 取用深度分析」的深度加工知识库（图/公式/全文/deep note 均可被工程直接取用，Obsidian 图谱化 + RAG 友好）。

**TL;DR**：
- 📥 **刷新知识库**：更新 `archive/paper_source_moonlight.md` → `python3 skills/paper-extraction/sync_from_source.py --push`（一条命令全自动）
- 🔍 **查询取用**：`python3 skills/paper-extraction/kb_query.py search|fig|formula|topics|info|stats <关键词> [--json]`
- 🧠 **取深度分析**：`extraction/deep/<slug>.md`（每篇 6 段一体化深读：核心问题/关键创新点/表格/对比/跨论文关系/局限，图表解读+公式织入）
- 🗺️ **浏览图谱**：Obsidian 打开本仓 → `extraction/MOC.md`

## 三条铁律（深度分析质量保证）

1. **图文/图表/架构图深度理解强制走 MiniMax-M3 vision 通道**——`skills/paper-extraction/m3_caption.py` 调蓝区火山 AI 网关 MiniMax-M3（vision-capable），结构化图解读写入 `extraction/minimax_captions.json`；subagent 模型 text-only，**禁止直接 Read PNG**（会 400），一律消费 caption 文本。全部论文全部关键图都有 M3 解读。
2. **公式以 `extraction/formulas.json` LaTeX 为权威源**——PDF 抽取常把公式当图片（.txt 里空白/乱码），核心关键公式必须直接引用 formulas.json 的 LaTeX（`$$...$$` 可渲染、完全正确），**禁止凭训练知识重写/补全**；M3 caption 提供公式在架构图中的角色对照（LaTeX↔图双源校验）。未来跨 project 复用时关键公式必须完全正确。
3. **按论文维度一体化深读**——单篇论文全文前后文一致，文本/图/表/公式交织分析（架构图↔公式推导↔ablation 表；结果图↔方法节↔超参表），图表与公式解读织进 6 段结构各节，禁止拆孤立片段。

## 目录

```
AICO-knowledge/
├── papers/                       # 源 PDF（69 篇，命名 <slug>.pdf）
├── papers_effective.md           # ⭐ 主干净索引（论文清单 + 链接 + 本地文件状态）
├── papers_download_list.txt      # slug | abs_url | pdf_url
├── archive/                      # 原始素材（paper_source_moonlight.md = 唯一需人工维护的文件）
├── skills/paper-extraction/      # ⭐ 可复用 skill（脚本路径相对，clone 即用）
│   ├── SKILL.md                  #   工作流手册（日常同步入口 + agent 收尾 + 决策树 + 踩坑）
│   ├── sync_from_source.py       #   ⭐ 一键同步编排（源表→diff→下载→萃取→推送，幂等）
│   ├── kb_query.py               #   统一查询 CLI（search/fig/formula/topics/info/stats，--json）
│   ├── m3_caption.py             #   火山网关 MiniMax-M3 图深度解读（--save 直写 captions.json）
│   ├── extract_phase1.py         #   全量深度萃取（文本+图表+公式+相关论文+MOC+manifest）
│   ├── orchestrate_deep_reread.py#   按论文维度深读编排（喂 captions+formulas+全文，三铁律）
│   ├── bulk_caption.sh           #   可恢复批量 M3 caption 驱动（fcntl 锁，5 并行）
│   ├── eprint_formulas.py        #   arxiv e-print LaTeX 源公式抽取（失败冷却 3 天）
│   ├── chunk_download.py         #   arxiv 分块续传下载（256KB 块+15 重试，jobs 文件驱动）
│   └── verify_pdfs.py            #   PDF 体检（截断/损坏/缺失/孤儿，CI gate）
└── extraction/                   # 生成的知识库
    ├── <slug>.md                 #   每篇结构化解析（Obsidian-flavored：摘要/图表/公式/相关论文）
    ├── deep/<slug>.md            #   ⭐ 一体化深度分析（6 段，图表+公式织入；![[deep/<slug>]] 嵌入各 MD）
    ├── fulltext/<slug>.txt       #   全文纯文本（grep 检索 / RAG chunk 源）
    ├── assets/<slug>-pNN.png     #   图表页渲染（150 DPI）
    ├── figures_index.md          #   ⭐ 图表素材索引（⭐精选深度解读 + 主题分类 + 按论文）
    ├── MOC.md                    #   🗺️ 主题图谱导航（wikilink 节点，Obsidian 图谱可视化）
    ├── moc_relations.md          #   跨论文关系谱系（人工维护，重跑不丢）
    ├── papers.json               #   机器可读 manifest（RAG/程序化摄取入口）
    ├── formulas.json             #   LaTeX 源公式库（$$ 块可直接粘贴，公式权威源）
    ├── minimax_captions.json     #   架构图多模态深度解读（441 张）
    ├── sync_report.md            #   最近一次同步报告（新增/待确认/失败/待解读）
    └── README.md                 #   知识库使用说明 + 外部工程接入指南
```

## 用法

**刷新（唯一人工动作 = 更新源文件）**：

```bash
# 1. 把新的 Moonlight 文献库导出覆盖 archive/paper_source_moonlight.md
# 2. 一条命令完成全链路并推送远端：
python3 skills/paper-extraction/sync_from_source.py --push
```

自动完成：diff 源表（Jaccard 模糊匹配）→ 新标题 arxiv 解析 → 分块下载+体检 → 摘要抓取+索引追加 → 深度萃取 → LaTeX 公式 → `sync_report.md` → commit+push（token 取 env `AICO_GITCODE_TOKEN` 或 `~/.config/aico/gitcode_token`，推完抹除）。幂等，无新增 ~40s。剩余两件需判断的事（待确认条目、架构图深度解读）列在 `sync_report.md` 里，见 `SKILL.md`「同步后的 agent 收尾」。

**写技术报告/论文总结时插图引用**：`kb_query.py fig <关键词>` → 拿 `![[assets/...png]]` + `[slug, Fig.N, p.X]` 引用串；或开 `extraction/figures_index.md`「⭐ 精选架构图」挑图。详见 `extraction/README.md`。

**引用公式**：`kb_query.py formula <关键词>` → 复制 `$$` 块（arxiv LaTeX 源，直接渲染，权威正确）。

**取深度分析**：直接读 `extraction/deep/<slug>.md`（每篇 6 段一体化深读，核心问题/关键创新点(机制+效果+精确数字+公式LaTeX+图M3解读)/表格/与同类对比/跨论文关系谱系/局限与边界）。新论文深读用 `orchestrate_deep_reread.py` 编排（自动喂 captions+formulas+全文，守三铁律）。

**图谱浏览**：Obsidian 打开本仓，`extraction/MOC.md` 是总览节点；单篇 MD 内「相关论文」交叉链接 + `moc_relations.md` 谱系自动成网。

**RAG 摄取**：读 `extraction/papers.json` manifest → 按 `fulltext/` 路径 chunk；或 `kb_query.py search --json`。

**其他工程接入**：本仓在共享 NFS 上，绝对路径直读零拷贝；接入指南+agent 提示词模板见 `extraction/README.md`「外部工程接入」。

**其他知识库复用此 skill**：把 `skills/paper-extraction/` 拷到任意论文仓即可。

## 文档
- `skills/paper-extraction/SKILL.md` — 操作手册（一键同步 + agent 收尾 + 决策树 + 约定 + 踩坑/效率）
- `EXPERIENCE.md` — 案例复盘（建库 + 增量刷新全过程踩坑与解法）
- `extraction/README.md` — 知识库使用说明 + 外部工程接入指南

## 现状（2026-08-18）

- **69 篇**论文全部深度萃取：**588 张图**、**441 张**页级图经 MiniMax-M3 vision 精解读（覆盖 61 篇有图论文）、**69 篇**一体化深度分析 note（`extraction/deep/`，6 段结构，图表+公式织入）、**54 篇 459 条** LaTeX 源公式（公式权威源）
- 三条铁律已落地：M3 图解读全覆盖 + 公式 LaTeX 权威源 + 按论文维度一体化深读
- 全部 PDF 校验有效（verify_pdfs.py 报 0 截断，3 篇 truncated-PDF 的深读 note 已标 not-available 待回填）
- 一键同步已上线并实测（源库 58 条 → 自动识别 2 条待确认，41s 完成全链路+自动推送）
- 主题覆盖：speculative decoding（10 篇成簇）、kv-cache、disaggregated-serving、sparse-attention、training、moe、rl、multimodal、long-context、architecture、topic-modeling、relational-table-learning
- 跨论文谱系（`moc_relations.md`）：KV cache 复用/压缩/调度、推测解码全家族、训练系统+网络拓扑、RL 系统+GRPO 根、Reasoning 蒸馏+latent、线性/混合注意力、NPU/Ascend、frontier 模型、残差/层间拓扑、多模态/VLM、长上下文、结构化/表格学习、主题建模/文档相似度、稀疏性第二轴 + taxonomy anchor
