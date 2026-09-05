---
name: bookshelf
description: Use when updating or extending the AICO-Knowledge knowledge bookshelf (bookshelf/SHELF.md；昇腾专区为独立手工页 ascend_infra.md, HTML 旧版备份) — the human-learner navigation layer over the three knowledge domains (papers/repos/web). All edits go in bookshelf/CURATION.md (embedded yaml blocks), then regenerate with bookshelf_build.py which resolves refs against registries, lints dead links and enforces the G1-G4 curation gates (non-zero exit on violation). Never hand-edit the generated shelf files.
---

# bookshelf — 知识书架生成与策展

## 这是什么

知识库的**第四种视图**（人类学习者导航），与前三个入口分工：
README（门面/规模）· extraction/index.md（LLM 查询）· extraction/MOC.md（图谱探索）· **bookshelf/（学习路径）**。

双入口：
- `bookshelf/SHELF.md` — 技术栈六层主线自上而下：L1 Agent → L2 模型/算法(单表) → L3 训推框架 → L4 算子 → L5 系统软件 → L6 硬件/集群；另有模型卡片 + 辅助工具
- `bookshelf/ascend_infra.md` — AscendInfra 昇腾专区（**独立手工 MD 页，非书架生成逻辑**；`ascend_infra.html` 为旧版备份）：AI Core 数据通路动图（render_ai_core.py 生成）/AscendC 概念与 API 族/算子全景/CANN 手册速查/精度性能 12 步方法论/知识对照表，数据全部来自本库深读资产；不出现任何第三方平台名字与链接

设计稿：`docs/bookshelf-design.md`（v5）。

## 操作（唯一姿势）

```bash
# 1. 改策展定义（唯一人工文件）
$EDITOR bookshelf/CURATION.md
# 2. 重新生成 + 死链 lint（死链非零退出，不静默）
python3 skills/bookshelf/bookshelf_build.py
```

**铁律**：
- **SHELF.md 只改 CURATION.md 重生成**（产物头部有 GENERATED 标记）；**ascend_infra.md 恰好相反——手工维护**
- **上架四闸门 G1-G4（生成器机械强制，违规拒绝生成）**：G1 概念页种子不上书架 ·
  G2 骨架仓卡不上架（无 deep/repo-* 分析层的 repocard 禁止引用，移泊车场或改链 reponote/仓外链）·
  G3 论文摘要必须中文（机械提取自 deep「核心问题」首段，禁英文 abstract 凑数）·
  G4 分类词表收敛（仅 CATEGORY_ORDER 登记词）。规则原文：CURATION.md 头部「上架铁律」
- **降级不删除**：条目下架一律进 CURATION.md 末尾「泊车场」注明原因，深读补齐后恢复
- 条目元数据（标题/版本/发表时间）一律由生成器从注册表机械解析——
  **发表时间以 arXiv ID(YYMM) 派生为权威**（papers.json 的 date 对 2026-01 批次混入入库日期，34/66 不一致实测）
- 热度🔥/难度⚡/昇腾亲和注记是策展层人工标注，机械层禁止臆造
- paper slug 支持唯一前缀兜底（防手抄截断），但新条目建议写全

## 条目引用协议

`paper:<slug>` 论文深读 · `papermd:<slug>` 结构化解构 · `reponote:<slug>:<path>` 仓文档深读 ·
`repocard:<slug>` 仓卡片（有分析层自动优先 deep/）· `web:<slug>` 网页深读 ·
`concept:<slug>` 概念页 · `crop:<file>` 裁剪图 · `ext:<label>:<url>` 外链

## 缺口反哺闭环

ascend_infra.md 尾部「共同缺口」清单 → 追加 `webs_download_list.txt` →
web-extraction 流水线入库 → CURATION.md 挂条目 → 重跑生成器。
**不猜 URL**：新网页源的 URL 必须来自已抓页面的真实内链或用户给定。

## 基线（2026-09-05 v7.1）

SHELF.md 104 条目（69/69 论文全覆盖，摘要列全中文，「知识源」列直链原始出处）· 0 死链 · G1-G4 全过。
ascend_infra.md 本地链接 lint 全过 · 无 AscendV 名字与链接 · AI Core 动图 docs/images/ai_core_datapath.gif（render_ai_core.py 重生成）。

**ascend_infra.md 死链 lint**（改后跑；html 备份同理）：
```bash
python3 - << 'LINT'
import re, pathlib
base = pathlib.Path('bookshelf'); s = open(base/'ascend_infra.md', encoding='utf-8').read()
bad = []
for h in re.findall(r'href="([^"]+)"', s):
    if h.startswith(('http','mailto:')): continue
    path, _, anchor = h.partition('#')
    p = (base/path).resolve() if path else base/'ascend_infra.md'
    if not p.exists(): bad.append(h); continue
    if anchor and path and f'id="{anchor}"' not in p.read_text(encoding='utf-8', errors='ignore'):
        bad.append(h+' (锚点缺失)')
print('死链:', len(bad)); [print(' ✗', b) for b in bad]
LINT
```
P3 补抓：HCCL 用户指南页（hcclug，源自 CANN 手册真实内链）入库；
达芬奇架构缺口由 agent-skills 仓 hardware-architecture 深读（L1 512KB/L0/UB 192KB 数值全）关闭。
