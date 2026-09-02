# History Sources

> 仓 `model-agent` · 路径 `skills/optimization/ascend-history-to-skill/ascend-history-to-skill/references/history-sources.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/model-agent/skills/optimization/ascend-history-to-skill/ascend-history-to-skill/references/history-sources.md

# 一体化深度解读：History Sources

## 【定位】

这篇文档为 `ascend-history-to-skill` 技能模块提供**历史记录来源的探查清单与证据提取规范**，告诉该模块在用户主机上"去哪里找 AI 编码工具的历史数据"以及"按什么优先级、何种字段去提炼昇腾模型调优经验"。

## 【技术要点】

1. **多工具候选路径覆盖**：枚举了四款主流 AI 编码工具（Codex、Claude Code、OpenCode、Cursor）的常见历史存储路径，每款均提供 2–4 个候选位置，且明确标注"不保证所有版本都存在"。
2. **Codex 路径最具体**：唯一给出带文件名的精确路径（`~/.codex/history.jsonl`），同时辅以 `sessions/`、`*.sqlite`、`log/` 三个目录/通配符候选。
3. **容错探测机制**：当默认搜索无结果时，推荐先用 `find` 确认真实路径，再通过 `--root` 参数追加，扩大扫描范围。
4. **三档证据优先级**：从"成功退出 + 产物 + benchmark" → "代码路径 + 命令 + 环境 + 报错修复闭环" → "仅计划讨论"逐级降权，确保提取到的是可复用的执行经验而非空想。
5. **十字段提取清单**：要求从历史中提取模型名/别名、仓库路径、conda 环境名、CANN/torch/torch_npu 版本、权重名与下载位置、入口脚本与关键命令、代码修改点、性能参数与 benchmark 口径、最终验证命令与产物路径、已知问题与修复方法。
6. **昇腾生态强绑定**：提取字段中明确点名 `CANN`、`torch_npu` 等昇腾特有栈，说明该工具聚焦于华为昇腾平台的大模型调优经验沉淀。

## 【关键机制与数据】

- **工作原理**：`ascend-history-to-skill` 工具按本文给出的候选路径列表，去用户主机上扫描这四款 AI 编码工具留下的本地历史文件；扫描到后，按"证据优先级"筛选可信记录，再按"提取清单"字段化抽取与昇腾调优相关的信息，最终生成可复用的 Skill 文档。
- **路径形态**（原文）：四款工具的历史既可能存放在 home 根下的点目录（如 `~/.codex/`、`~/.claude/`、`~/.opencode/`、`~/.cursor/`），也可能放在 XDG 配置目录（如 `~/.config/claude/`、`~/.config/Cursor/`），且目录名大小写变体（`claude` vs `Claude`、`opencode` vs `OpenCode`、`cursor` vs `Cursor`）都需要同时尝试，体现出对不同发行版/安装方式的兼容设计。
- **Codex 路径唯一带文件名**（原文）：`~/.codex/history.jsonl`，是 JSON Lines 格式的对话历史。
- **降级搜索策略**（原文）：默认搜索无果 → `find` 探测 → `--root` 追加，三步递进。
- **原文未给出任何具体数字（版本号、路径深度、性能数据等均无）**。

## 【表格解读】

原文无表格。

文档以**分组列表**形式呈现候选路径，分组标题即工具名（Codex、Claude Code、OpenCode、Cursor），每组下用 `-` 列表罗列路径；另有"Evidence Ranking"用有序列表 1/2/3 表示优先级，"Extraction Checklist"用 `-` 列表罗列十个字段。整篇没有 markdown 表格结构。

## 【公式解读】

原文无公式。

## 【关联】

文档标题与所在路径 `skills/optimization/ascend-history-to-skill/ascend-history-to-skill/references/history-sources.md` 表明：

- **上游调用方**：目录层级暗示存在 `SKILL.md`（技能入口）和可能的 `scripts/`（扫描脚本），本文位于 `references/` 子目录，是被主技能按需引用的一份参考资料。
- **与 `optimization` 分类的关系**：归属"调优"类技能，说明历史数据沉淀的最终目的是为昇腾模型的调优提供经验复用。
- **下游产出**：文档本身未明示，但从提取字段（"生成产物"、"验证命令与产物路径"）可推断，被抽取的历史最终会生成可被其他 Skill 调用的知识条目。
- **与昇腾栈的耦合**：提取字段显式包含 `CANN`、`torch_npu`、`conda 环境名`，与仓库主标题"昇腾模型 Agent"完全对齐；其他通用字段（模型名、仓库路径、benchmark）则是跨平台通用的元数据。
- **内部链接**：原文未提供任何内部链接（包括交叉引用、跳转锚点、相关文档链接等），因此无相关上下游路径可引用。

## 【使用方法】

- **启用方式**：原文未涉及（属于参考资料，使用方式由同目录的 `SKILL.md` 或上层技能入口决定）。
- **关键参数**（原文提及）：
  - `--root`：在默认搜索无结果时用于追加自定义根目录路径。
  - `find`：建议先用该命令探测真实路径。
- **配置项**：原文未涉及具体配置文件或环境变量。
- **命令**：仅出现 `find` 一条命令作为排查手段，未给出完整调用示例。
