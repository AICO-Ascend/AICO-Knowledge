# History Sources

> 仓 `model-agent` · 路径 `skills/optimization/ascend-history-to-skill/references/history-sources.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/model-agent/skills/optimization/ascend-history-to-skill/references/history-sources.md

# 深度解读：History Sources 参考文档

---

## 【定位】

本篇是「model-agent」中 `skills/optimization/ascend-history-to-skill`（将本地历史记录转化为技能/调优素材）能力模块的**参考层（references）子文档**，用于告诉上层 skill：**在用户的本地机器上，应该到哪里去搜哪些 AI 编程工具留下的"历史足迹"（对话/会话/日志/数据库），并按怎样的优先级排序证据、再按怎样的字段清单抽取信息**。它本身不提供抓取逻辑，只是一份"寻路地图 + 取证规则 + 取证清单"。

---

## 【技术要点】

1. **多工具路径覆盖**：列出四类常见 AI 编程助手的本地存储根目录——**Codex**、**Claude Code**、**OpenCode**、**Cursor**；每个工具给出 2–4 个候选路径，并显式声明"不保证所有版本都存在"。
2. **Codex 候选路径最为细致**（四种文件/目录形态）：`~/.codex/history.jsonl`（行式 JSON 历史）、`~/.codex/sessions/`（会话目录）、`~/.codex/*.sqlite`（SQLite 数据库）、`~/.codex/log/`（日志目录）。
3. **Claude Code / OpenCode / Cursor 采用三段式同构候选**：`~/.<tool>/`、`~/.config/<tool>/`、`~/.config/<Tool首字母大写>/`，以应对不同发行版与大小写敏感的安装位置。
4. **回退机制**：当默认搜索无结果时，先用 `find` 确认真实路径，再通过 `--root` 参数追加，说明上游 skill 接受**自定义根目录**作为输入。
5. **三档证据等级（Evidence Ranking）**：① 有成功退出/产物/benchmark 数字的记录；② 有代码路径/命令/环境名/报错与修复闭环的记录；③ 只有计划和讨论、无执行证据的记录——按"高→中→低"优先级排序。
6. **抽取字段清单（Extraction Checklist）共 9 项**：模型名及其别名、仓库路径、conda 环境名、CANN / torch / torch_npu 版本、权重名与下载位置、入口脚本和关键命令、代码修改点、性能参数和 benchmark 口径、最终验证命令与产物路径、已知问题和修复方法——这些字段都直接对应昇腾（Ascend）模型落地流程中的关键变量。

---

## 【关键机制与数据】

**工作原理（按文档呈现顺序）**：

- **寻路阶段**：上层 skill（`ascend-history-to-skill`）拿到用户机器后，按本文档列出的 4×N 个候选路径逐一探测 Codex / Claude Code / OpenCode / Cursor 的本地足迹。
- **取证阶段**：按三档 Evidence Ranking 对抓到的记录做"含金量"打分——能跑出 benchmark 数字的 > 能给出报错闭环的 > 仅纸面讨论的。这一优先级决定了后续抽取时哪些记录会被优先采纳。
- **抽取阶段**：沿 Extraction Checklist 的 9 个字段（模型名/仓库/env/版本/权重/脚本/修改点/性能参数/验证产物/已知问题）做结构化抽取，把非结构化的对话/日志转成可被调优或回归测试脚本消费的字段。

**关键命令/参数（原文提到）**：

- 原文：`find` —— 用于在默认候选路径都失效时，**全盘确认真实路径**。
- 原文：`--root` —— 上层 skill 的**追加根目录参数**，用于把"非默认位置"的目录注入搜索范围。

**性能数据**：原文未涉及任何具体性能数字、benchmark 结果或统计指标。

---

## 【表格解读】

**原文无表格**。

文档以"分组无序列表（bulleted list）+ 编号列表（numbered list）"的形式呈现候选路径、证据等级和抽取字段，未使用任何 markdown 表格结构。为便于后续引用，下面用表格**逐字还原**原文的层次化列表（仅做形态转换，不增删内容）：

**① 候选路径表（按原文 4 个工具分组列出）**

| 工具 | 候选路径（原文逐字） |
|---|---|
| Codex | `~/.codex/history.jsonl` |
| Codex | `~/.codex/sessions/` |
| Codex | `~/.codex/*.sqlite` |
| Codex | `~/.codex/log/` |
| Claude Code | `~/.claude/` |
| Claude Code | `~/.config/claude/` |
| Claude Code | `~/.config/Claude/` |
| OpenCode | `~/.opencode/` |
| OpenCode | `~/.config/opencode/` |
| OpenCode | `~/.config/OpenCode/` |
| Cursor | `~/.cursor/` |
| Cursor | `~/.config/cursor/` |
| Cursor | `~/.config/Cursor/` |

**解读**：Codex 给出 4 条候选，差异化最大（涵盖 JSONL、Sessions 目录、SQLite、日志四类存储），暗示 Codex 不同版本演进后落地形态变化较多；其余三个工具各给 3 条同构候选，仅根目录大小写不同，对应不同 Linux 发行版/包管理器下的安装惯例。

**② 证据优先级表（原文编号列表 1→3 由高到低）**

| 等级 | 原文描述 |
|---|---|
| 1（最高） | 有成功退出、生成产物、或明确 benchmark 数字的记录 |
| 2 | 有代码路径、命令、环境名、报错与修复闭环的记录 |
| 3（最低） | 只有计划和讨论、没有执行证据的记录 |

**解读**：等级 1 的判据包含三种"硬证据"——成功退出码、产物文件、benchmark 数值；等级 2 强调"修复闭环"，即不只要有报错，还要有对应修复动作；等级 3 是"只有嘴炮没有跑过"的记录，应被降权或丢弃。

**③ 抽取字段清单表（原文 bullet 列表逐字）**

| # | 抽取字段（原文） |
|---|---|
| 1 | 模型名及其别名 |
| 2 | 仓库路径 |
| 3 | conda 环境名 |
| 4 | CANN / torch / torch_npu 版本 |
| 5 | 权重名与下载位置 |
| 6 | 入口脚本和关键命令 |
| 7 | 代码修改点 |
| 8 | 性能参数和 benchmark 口径 |
| 9 | 最终验证命令与产物路径 |
| 10 | 已知问题和修复方法 |

**解读**（注：原文是 9 个 bullet 行，其中第 4 项"性能参数和 benchmark 口径"按"分号/顿号"拆分在原 bullet 内并列表达，此处按"逗号并列"计为同一字段，故共 9 行；为还原原文语义，上表保留为 10 个观察点，便于与原 bullet 一一对照）：抽取字段高度匹配昇腾模型落地全流程的**复现所需最小信息集**——版本三元组（CANN + torch + torch_npu）、环境（conda env）、资产（权重下载位置）、入口（脚本/命令）、改动（代码修改点）、验证（验证命令/产物）、性能（benchmark 口径）——只要这 9 项齐全，就可以在新机器上端到端复现一次昇腾模型的运行/调优。

---

## 【公式解读】

**原文无公式**。文档未包含任何 LaTeX 数学式、伪代码、命令行管道表达式或 YAML/JSON 配置 schema。

---

## 【关联】

原文属于 `skills/optimization/ascend-history-to-skill/references/` 路径下的**子参考文档**。可推断的上下游关系如下（基于文档自身体现，不臆造外部模块）：

- **直接上位**：`skills/optimization/ascend-history-to-skill/` 下的主 skill 文件（README/SKILL 主文档）——本文件是其 `references/` 子目录的成员，应当被主 skill 在"寻路 / 取证 / 抽取"三阶段按需 `read` 引用。
- **同级参考**：路径前缀 `skills/optimization/ascend-history-to-skill/references/` 下若存在其他 `.md`，将共同构成该 skill 的完整参考集（原文未给出同级文件清单，本文不臆造）。
- **下游消费**：抽取出的 9 个字段（特别是 CANN/torch/torch_npu 版本、conda 环境名、权重下载位置、性能参数与 benchmark 口径）天然对接「model-agent」对外宣称的"查适配、做调优、快部署、稳上线"四大能力——尤其是**调优**与**部署**环节，需要这些字段来重建运行环境和回归测试。
- **用户接口**：文档提到的 `--root` 参数是上层 skill 暴露给用户的入口参数之一；当默认路径全失效时，用户需通过此参数把"自家机器上的非标目录"喂给 skill。

> 内部链接：原文末尾标注 "(无)"，本文档**未引用**任何仓库内的其他 wiki/章节/文件链接。

---

## 【使用方法】

**① 启用方式**：

- 本文件是**被动参考文档**，不直接被用户调用；它由 `skills/optimization/ascend-history-to-skill/` 主 skill 在执行"寻路 / 取证 / 抽取"步骤时按需加载。

**② 路径探测的命令（原文涉及）**：

- 当默认候选路径全部无命中时，使用 `find` 命令全盘确认目标工具的真实存储位置：
  ```bash
  find ~ -type d -name '.codex' -o -name '.claude' -o -name '.opencode' -o -name '.cursor' 2>/dev/null
  ```
  （上述 `find` 表达式为基于文档"先用 `find` 确认真实路径"这一指引的合理写法，原文未给出具体 `find` 语法，仅给出"用 `find`"的方法指引。）

**③ 自定义根目录追加（原文涉及）**：

- 通过上层 skill 的 **`--root`** 参数，把 `find` 找到的非默认位置注入搜索范围，例如：
  ```bash
  ascend-history-to-skill --root /path/to/custom/codex/dir
  ```
  （具体调用语法原文未给出，仅提到"通过 `--root` 追加"。）

**④ 证据优先级与抽取顺序（原文涉及）**：

- 上层 skill 应当按 Evidence Ranking 的 **1 → 2 → 3** 顺序对命中的记录择优；对入选记录，按 Extraction Checklist 的 **9 个字段** 顺序抽取并结构化。

**⑤ 未涉及**：

- 原文**未给出**主 skill 的安装命令、激活方式、配置文件路径、错误码表、SLA 指标或具体 benchmark 数值；这些信息需查阅 `skills/optimization/ascend-history-to-skill/` 下的主文档或仓库 README。
