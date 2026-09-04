---
name: bookshelf
description: Use when updating or extending the AICO-Knowledge knowledge bookshelf (bookshelf/SHELF.md；昇腾专区为独立 HTML 体系 ascend_infra.html) — the human-learner navigation layer over the three knowledge domains (papers/repos/web). All edits go in bookshelf/CURATION.md (embedded yaml blocks), then regenerate with bookshelf_build.py which resolves refs against registries and lints dead links. Never hand-edit the generated shelf files.
---

# bookshelf — 知识书架生成与策展

## 这是什么

知识库的**第四种视图**（人类学习者导航），与前三个入口分工：
README（门面/规模）· extraction/index.md（LLM 查询）· extraction/MOC.md（图谱探索）· **bookshelf/（学习路径）**。

双入口：
- `bookshelf/SHELF.md` — 技术栈六层主线自上而下：L1 Agent → L2 模型/算法 → L3 训推框架 → L4 算子 → L5 系统软件 → L6 硬件/集群；另有横向专题 + 模型卡片
- `bookshelf/ascend_infra.html` — AscendInfra 昇腾专区（**独立手工 HTML 体系，非书架生成逻辑**）：自绘 AI Core 架构 SVG/算子全景/AscendC 概念卡/知识对照表（概念↔本页可视化↔深读↔仓实现），数据全部来自本库深读资产；不出现任何第三方平台名字与链接

设计稿：`docs/bookshelf-design.md`（v3）。

## 操作（唯一姿势）

```bash
# 1. 改策展定义（唯一人工文件）
$EDITOR bookshelf/CURATION.md
# 2. 重新生成 + 死链 lint（死链非零退出，不静默）
python3 skills/bookshelf/bookshelf_build.py
```

**铁律**：
- **SHELF.md 只改 CURATION.md 重生成**（产物头部有 GENERATED 标记）；**ascend_infra.html 恰好相反——手工维护**，改完跑 HTML 死链 lint（见下）
- 条目元数据（标题/版本/发表时间）一律由生成器从注册表机械解析——
  **发表时间以 arXiv ID(YYMM) 派生为权威**（papers.json 的 date 对 2026-01 批次混入入库日期，34/66 不一致实测）
- 热度🔥/难度⚡/昇腾亲和注记是策展层人工标注，机械层禁止臆造
- paper slug 支持唯一前缀兜底（防手抄截断），但新条目建议写全

## 条目引用协议

`paper:<slug>` 论文深读 · `papermd:<slug>` 结构化解构 · `reponote:<slug>:<path>` 仓文档深读 ·
`repocard:<slug>` 仓卡片（有分析层自动优先 deep/）· `web:<slug>` 网页深读 ·
`concept:<slug>` 概念页 · `crop:<file>` 裁剪图 · `ext:<label>:<url>` 外链

## 缺口反哺闭环

ascend_infra.html 尾部「共同缺口」清单 → 追加 `webs_download_list.txt` →
web-extraction 流水线入库 → CURATION.md 挂条目 → 重跑生成器。
**不猜 URL**：新网页源的 URL 必须来自已抓页面的真实内链或用户给定。

## 基线（2026-09-04 落地）

SHELF.md 135 条目（69/69 论文全覆盖，含「原始出处」列：论文→arXiv、仓文档→gitcode blob 原始位置、网页→原页面）· 0 死链。
ascend_infra.html 79 本地链接 0 死链（含锚点校验）· 无 AscendV 名字与链接。

**HTML 死链 lint**（改 ascend_infra.html 后跑）：
```bash
python3 - << 'LINT'
import re, pathlib
base = pathlib.Path('bookshelf'); s = open(base/'ascend_infra.html', encoding='utf-8').read()
bad = []
for h in re.findall(r'href="([^"]+)"', s):
    if h.startswith(('http','mailto:')): continue
    path, _, anchor = h.partition('#')
    p = (base/path).resolve() if path else base/'ascend_infra.html'
    if not p.exists(): bad.append(h); continue
    if anchor and path and f'id="{anchor}"' not in p.read_text(encoding='utf-8', errors='ignore'):
        bad.append(h+' (锚点缺失)')
print('死链:', len(bad)); [print(' ✗', b) for b in bad]
LINT
```
P3 补抓：HCCL 用户指南页（hcclug，源自 CANN 手册真实内链）入库；
达芬奇架构缺口由 agent-skills 仓 hardware-architecture 深读（L1 512KB/L0/UB 192KB 数值全）关闭。
