# 🌙 夜间深度学习规范（DEEP_LEARNING_PROTOCOL）

> 目标：把 AICO-knowledge 从"PDF 萃取的素材库"升级为"全要素深读 + 知识图谱完备 + 跨论文关系挖掘"的高质量知识库。
> 凌晨窗口（资源空闲）分批执行；每批追求**极致深度**，非图数量吞吐。
> 用户要求：极致深度分析、思考，确保高质量——**深度优先于覆盖**。

## 深度缺口（2026-08-18 盘点，夜间学习的真实目标）

| 维度 | 现状 | 缺口 |
|---|---|---|
| 图深读 | 382 张图，仅 27 张深读（7%） | 355 张未深读（**不止架构图，所有图都要**） |
| 技术点结构化 | 60 篇 MD，仅 7 篇（12%）有结构化技术点段 | 53 篇文本未深度提炼 |
| 表格萃取 | 无（fulltext txt 有但未结构化） | 全缺 |
| MOC 图谱 | 11 主题浅聚类（按主题列论文） | 无跨论文关系/对比/演进分析 |
| 公式 | 48 篇有 LaTeX，但启发式/缺失 12 篇 | e-print 补 + tex 无 display 不强求 |

## 每批深度学习的标准动作（不是只学图）

每批 fire 选 **1 篇论文做全要素深读**（深度优先，1 篇做透 > 30 张图浅尝）：

### Step 0 — 自检（全绿才动）
```bash
# 网关连通(MiniMax-M3 文本 say ok) + kb_query stats + git clean
python3 - <<'PY'
import json,os,urllib.request
U=os.environ["VOLC_GATEWAY_URL"];K=os.environ["VOLC_GATEWAY_KEY"]
def t(m,mt=200):
    b={"model":m,"messages":[{"role":"user","content":"say ok"}],"max_tokens":mt}
    r=urllib.request.Request(U,data=json.dumps(b).encode(),headers={"Authorization":f"Bearer {K}","Content-Type":"application/json"})
    print(m,"->",json.load(urllib.request.urlopen(r,timeout=120))["choices"][0]["message"]["content"][:20])
t("MiniMax-M3",4000)
PY
python3 skills/paper-extraction/kb_query.py stats | head -4
git status --short  # 应空
```

### Step 1 — 选论文（挑缺口最大的）
优先级：
1. **技术点未结构化**（53 篇候选）——文本深度提炼缺口
2. 该篇的**所有未深读图**（含非架构图：结果图、流程图、消融图）
3. **表格**未萃取的篇
脚本：`python3 skills/paper-extraction/pick_deep_paper.py`（见下）输出 1 个 slug + 待办清单。

### Step 2 — 全要素深读（4 类产出）

> **持久化铁律**（2026-08-18 修复）：extract_phase1.py 全量重生成论文 MD 与 MOC.md，**任何写进这两处的手工内容都会被下次重跑抹掉**。所以夜间深读产出**必须落到独立文件**，extract_phase1 只嵌入 wikilink 指针：
> - 技术点 / 表格 / 跨论文关系 → `extraction/deep/<slug>.md`（独立文件，extract 检测后嵌入 `![[deep/<slug>]]`）
> - MOC 跨论文关系谱系 → `extraction/moc_relations.md`（独立文件，MOC 嵌入 `![[moc_relations]]`）
> - 图深度解读 → `extraction/minimax_captions.json`（extract 直接读取，天然持久）
> - **绝不**把深读内容直接写进 `<slug>.md` 或 `MOC.md` 正文——会被覆盖。

**a. 文本技术点提炼**（最重要，缺口最大）：
读 `extraction/fulltext/<slug>.txt`（glm-5.2 有 1M 上下文整篇灌入），产出结构化技术点段，写入**独立文件** `extraction/deep/<slug>.md`（文件头注明"全要素深读笔记，extract_phase1 重跑不丢"）：
- 核心问题 + 解决思路（2-3 句话）
- 关键创新点（分点，每点含动机→机制→效果）
- 与同类方法对比（显式点出 vs 谁、差在哪）
- 局限/边界（作者承认或可推断的）

**b. 所有未深读图深读**（不止架构图）：
该篇每张未深读 PNG，`m3_caption.py --save`（MiniMax-M3，max_tokens≥8000）**并行 3 张/批**（实测：并发 11 触发网关 rate limit 全部 0s 失败，并发 3 稳定，9 张 39s 内完成）：
- 架构图：组件/数据流/核心要点
- 结果图：实验设置 + 关键数字 + 结论
- 流程图：步骤 + 决策点
- **吃图模型仅 MiniMax-M3 / doubao-seed-2.1-pro；glm-5.2 不吃图（喂图返回 400）**

**c. 表格萃取**：
从 fulltext 识别表格（`\n.*\|.*\n` 多行结构或 Table N 标记），结构化为 Markdown 表格 + 一句话解读，**追加进 `extraction/deep/<slug>.md`**（同 a 段同一文件，不进论文 MD 正文）。

**d. 公式核验**：
该篇若有启发式/缺失公式，走 `eprint_formulas.py --only <slug>`（先删其在 formulas.json 的启发式条目）；tex 无 display 环境则保留启发式，不强求。

### Step 3 — 知识图谱完备化（MOC + 跨论文关系）
深读完后，更新**独立文件** `extraction/moc_relations.md`（不直接改 MOC.md，extract 会嵌入 `![[moc_relations]]`）：
- 该篇加入对应主题的演进谱系（KV cache 复用 / 调度 / 推测解码 / 训练 / RL 已有分类）
- 显式写关系：`[A] 继承 [B] / [A] 改进 [B] 的 X / [A] 与 [B] 互补在 Y`

### Step 4 — 落地
```bash
python3 skills/paper-extraction/extract_phase1.py   # 合并图解读进 MD
# token 从 ~/.config/aico/gitcode_token，推完抹 push URL，绝不落仓
git add -A && git commit -m "deep: <slug> 全要素深读(图×N/技术点/表格/MOC关系)" && git push
```

### Step 5 — 汇报
简短报告：本批深读哪篇、新增图解读数、技术点段、表格数、MOC 关系更新、剩余缺口（未深读图数 / 技术点未结构化篇数）。

## 规模控制（token 分位数的诚实替代）

**无法在 cron 里真实度量 token 消耗分位数**（m3_caption.py 是 urllib 直调网关，没接 Anthropic budget API）。用硬上限替代，且**深度优先**：
- 单篇全要素深读（~5-15 张图 + 文本技术点 + 表格 + 公式核验 + 跨论文关系）约 **4-12 分钟主动模型时间**；深度展开（含跨篇对比推理）可到 ~15-20 分钟。
- **实测容量基线**（2026-08-18 sglang 测试）：12 张图 M3 并发 3 ≈ 1 分钟；文本技术点提炼 + 跨论文关系 ≈ 数分钟。**单晚 8 小时窗口估计 20-30 篇深度处理**（深度优先，不追上限）。
- 若单批 token 消耗大（图多/文本长），自然降速——网关侧有 rate limit 兜底，不会失控。
- **绝不牺牲深度换覆盖**：宁可 1 篇做透，不 30 张图浅尝。
- NPU 加速：8× Ascend 910B3 在位，但 m3_caption 走远程火山网关 API，**NPU 无法加速远程 API 调用**；NPU 仅在本机跑开源模型时有用（当前深读流程不涉及，不接入）。

## 模型分工（吃图 vs 文本）

| 任务 | 模型 | 备注 |
|---|---|---|
| 图深读 | MiniMax-M3（默认）/ doubao-seed-2.1-pro | reasoning，max_tokens≥8000 |
| 文本技术点提炼 | glm-5.2（1M 上下文整篇灌入）/ 主 session 模型 | 文本强，不吃图 |
| 公式抽取 | eprint_formulas.py（确定性脚本） | 不用模型 |

## 知识组织（确保其他 project 高效取用）

已用 Obsidian 结构（SKILL.md 约定），夜间学习**严格保持**：
- per-paper MD：frontmatter + `> [!abstract]` + `## 元信息` + `## 图表`（⭐深读，读自 minimax_captions.json）+ `## 技术点深读（DEEP）`（embed `![[deep/<slug>]]`，内容在独立文件）+ `## 全文文本`
- `extraction/deep/<slug>.md`：技术点 / 表格 / 跨论文关系（独立维护，重跑不丢）
- `extraction/moc_relations.md`：跨论文关系谱系（独立维护，MOC 嵌入 `![[moc_relations]]`）
- MOC.md：主题聚类（自动）+ `## 跨论文关系与演进`（embed moc_relations）
- wikilink `[[slug]]` 跨篇链接（已有，深读时补强）
- 外部工程取用统一走 `kb_query.py search|fig|formula|topics|info|stats`——不整库载入（小窗模型友好）

回灌材料走 `BACKFILL_PROTOCOL.md` 质检；本规范产出的非回灌，是自驱深读，无需回灌质检但仍遵循"不猜来源、ID 验证"铁律。
