# MindStudio Profiler Release Notes

> 仓 `msprof` · 路径 `docs/en/release_notes.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msprof/docs/en/release_notes.md

# MindStudio Profiler Release Notes 深度解读

## 【定位】
本篇文档是 MindStudio Profiler (msProf) 的版本发布追踪型 changelog，其核心目的是在 GitCode release 页面未提供详细特性摘要的前提下，**系统整理 26.0.0 系列的版本标签、发布日期与生命周期阶段**，帮助用户跟踪版本演进，而非描述具体功能实现。

## 【技术要点】

1. **版本命名格式**：采用 `tag_MindStudio_<major>.<minor>.<patch>.<stage>_<seq>` 的固定模板（例如 `tag_MindStudio_26.0.0.B090_004`），其中 `stage` 字段区分 alpha/beta/build 三类生命周期。
2. **三段式阶段命名**：`<stage>` 字段存在三种形式——`alpha.<n>`（如 `alpha.1`）、`Beta<n>_<seq>`（如 `Beta1_001`）、`B<n><m>_<seq>`（如 `B090_004`，其中 `090` 为阶段号、`004` 为该阶段内序号）。
3. **当前主版本聚焦**：截至 2026-04-01，所有可用版本均集中在 `26.0.0` 主版本号下；最新公开构建为 `tag_MindStudio_26.0.0.B090_004`（发布日期 2026-03-27）。
4. **同阶段增量发布模式**：每个 phase 通常包含多个子版本，按递增顺序发布（如 `B090_001` → `B090_004`，`B030_001` → `B030_008`）。
5. **版本数量统计**：截至 2026-04-01，共发布 **39** 个版本 tag，时间跨度为 2026-01-19 至 2026-03-27。
6. **同阶段日期聚簇**：同一 phase 的多个子版本通常在 1–2 天内集中发布（如 `B030` 阶段 8 个版本集中在 2026-02-09 至 2026-02-10，`B050` 阶段 8 个版本集中在 2026-02-26 至 2026-02-27）。

## 【关键机制与数据】

**原文：版本生命周期三阶段划分机制**
文档将 msProf 版本划分为三个生命周期阶段：
- **alpha 阶段（pre-release）**：`alpha.<n>` 命名，当前最新为 `tag_MindStudio_26.0.0-alpha.1`（2026-02-03）。
- **beta 阶段（testing）**：`Beta<n>_<seq>` 命名，当前最新为 `tag_MindStudio_26.0.0.Beta1_001`（2026-02-28）。
- **build 阶段（public）**：`B<n><m>_<seq>` 命名，按阶段号递增（`B010` → `B020` → `B030` → `B050` → `B060` → `B070` → `B080` → `B090`），共 8 个 build 阶段。

**原文：阶段编号跳号现象**
阶段编号非严格连续：`B010`、`B020`、`B030` 之后直接进入 `B050`，跳过 `B040`；阶段内序号也非严格连续（如 `B070` 仅有 `_001/_002/_003/_007`，缺 `_004-_006`；`B080` 仅有 `_001-_005/_007`，缺 `_006`）。

**原文：版本数量分布**
`B010`(1) + `B020`(2) + `alpha`(1) + `B030`(8) + `B050`(8) + `Beta1`(1) + `B060`(4) + `B070`(4) + `B080`(6) + `B090`(4) = 39 个版本，与文中"共发布 39 个 version tag"一致。

## 【表格解读】

### 表 1：Version Comparison（版本对比）

| Version | Type | Release Date | Description |
|------|------|------|------|
| 26.0.0.B090_004 | Latest build | 2026-03-27 | The most recent public build currently available. |
| 26.0.0.Beta1_001 | Latest beta version | 2026-02-28 | The most recent version in the beta phase currently available. |
| 26.0.0-alpha.1 | Latest alpha version | 2026-02-03 | The most recent pre-release version in the alpha phase currently available. |

**解读**：该表呈现三类阶段的"最新代表版本"，日期跨度从 2026-02-03 至 2026-03-27，约 8 周时间完成 alpha → beta → build 的三级跃迁；build 阶段比 beta 阶段晚 27 天，比 alpha 阶段晚近 2 个月。

### 表 2：Version Naming Convention Fields（版本命名字段说明）

| Field | Description |
|------|------|
| `26.0.0` | The major version number. |
| `alpha.1` | A version in the alpha pre-release phase. |
| `Beta1_001` | A version in the beta testing phase. |
| `B090_004` | A specific build within a phase. `090` represents the phase number, and `004` represents the sequence number within that phase. |

**解读**：明确 4 类字段含义——主版本号统一为 `26.0.0`，stage 字段是区分阶段的唯一标识，build 阶段号 `090` 为 3 位数字、阶段内序号 `004` 为 3 位数字。

### 表 3：Versions in the Same Phase (`B090`)

| Version | Release Date |
|------|------|
| `tag_MindStudio_26.0.0.B090_001` | 2026-03-26 |
| `tag_MindStudio_26.0.0.B090_002` | 2026-03-26 |
| `tag_MindStudio_26.0.0.B090_003` | 2026-03-27 |
| `tag_MindStudio_26.0.0.B090_004` | 2026-03-27 |

**解读**：`B090` 阶段共 4 个版本，2 天内发布完毕（2026-03-26 一天 2 个、2026-03-27 一天 2 个），序号严格递增。

### 表 4：Phase Statistics（阶段统计）

| Phase | Number of Versions | Time Range | Version Tag |
|------|------|------|------|
| `B010` | 1 | 2026-01-19 | `tag_MindStudio_26.0.0.B010_001` |
| `B020` | 2 | 2026-01-29 to 2026-01-30 | `tag_MindStudio_26.0.0.B020_001`, `tag_MindStudio_26.0.0.B020_002` |
| `alpha` | 1 | 2026-02-03 | `tag_MindStudio_26.0.0-alpha.1` |
| `B030` | 8 | 2026-02-09 to 2026-02-10 | `tag_MindStudio_26.0.0.B030_001` to `tag_MindStudio_26.0.0.B030_008` |
| `B050` | 8 | 2026-02-26 to 2026-02-27 | `tag_MindStudio_26.0.0.B050_001` to `tag_MindStudio_26.0.0.B050_008` |
| `Beta1` | 1 | 2026-02-28 | `tag_MindStudio_26.0.0.Beta1_001` |
| `B060` | 4 | 2026-03-05 to 2026-03-06 | `tag_MindStudio_26.0.0.B060_001` to `tag_MindStudio_26.0.0.B060_004` |
| `B070` | 4 | 2026-03-12 to 2026-03-16 | `tag_MindStudio_26.0.0.B070_001`, `tag_MindStudio_26.0.0.B070_002`, `tag_MindStudio_26.0.0.B070_003`, `tag_MindStudio_26.0.0.B070_007` |
| `B080` | 6 | 2026-03-19 to 2026-03-24 | `tag_MindStudio_26.0.0.B080_001`, `tag_MindStudio_26.0.0.B080_002`, `tag_MindStudio_26.0.0.B080_003`, `tag_MindStudio_26.0.0.B080_004`, `tag_MindStudio_26.0.0.B080_005`, `tag_MindStudio_26.0.0.B080_007` |
| `B090` | 4 | 2026-03-26 to 2026-03-27 | `tag_MindStudio_26.0.0.B090_001`, `tag_MindStudio_26.0.0.B090_002`, `tag_MindStudio_26.0.0.B090_003`, `tag_MindStudio_26.0.0.B090_004` |

**解读**：从阶段演进节奏可见——`B030` 与 `B050` 是发布密度最高的两个阶段（各 8 版），两者之间夹了 alpha（1 版）和 Beta1（1 版）形成"Build → Alpha → Build → Beta"的交错节奏；阶段间隔约 7 天（`B030→B050` 中间经过 2026-02-10→2026-02-26 共 16 天，因含 alpha/beta 节点）；`B070` 与 `B080` 阶段存在序号跳号（前者缺 `_004-_006`、后者缺 `_006`），说明发布并非严格连续递增。

### 表 5：Complete Version List（完整版本列表，共 39 条）

| No. | Version Tag | Release Date |
|------|------|------|
| 1 | `tag_MindStudio_26.0.0.B090_004` | 2026-03-27 |
| 2 | `tag_MindStudio_26.0.0.B090_003` | 2026-03-27 |
| 3 | `tag_MindStudio_26.0.0.B090_002` | 2026-03-26 |
| 4 | `tag_MindStudio_26.0.0.B090_001` | 2026-03-26 |
| 5 | `tag_MindStudio_26.0.0.B080_007` | 2026-03-24 |
| 6 | `tag_MindStudio_26.0.0.B080_005` | 2026-03-20 |
| 7 | `tag_MindStudio_26.0.0.B080_004` | 2026-03-20 |
| 8 | `tag_MindStudio_26.0.0.B080_003` | 2026-03-19 |
| 9 | `tag_MindStudio_26.0.0.B080_002` | 2026-03-19 |
| 10 | `tag_MindStudio_26.0.0.B080_001` | 2026-03-19 |
| 11 | `tag_MindStudio_26.0.0.B070_007` | 2026-03-16 |
| 12 | `tag_MindStudio_26.0.0.B070_003` | 2026-03-14 |
| 13 | `tag_MindStudio_26.0.0.B070_002` | 2026-03-12 |
| 14 | `tag_MindStudio_26.0.0.B070_001` | 2026-03-12 |
| 15 | `tag_MindStudio_26.0.0.B060_004` | 2026-03-06 |
| 16 | `tag_MindStudio_26.0.0.B060_003` | 2026-03-06 |
| 17 | `tag_MindStudio_26.0.0.B060_002` | 2026-03-05 |
| 18 | `tag_MindStudio_26.0.0.B060_001` | 2026-03-05 |
| 19 | `tag_MindStudio_26.0.0.Beta1_001` | 2026-02-28 |
| 20 | `tag_MindStudio_26.0.0.B050_008` | 2026-02-27 |
| 21 | `tag_MindStudio_26.0.0.B050_007` | 2026-02-27 |
| 22 | `tag_MindStudio_26.0.0.B050_006` | 2026-02-27 |
| 23 | `tag_MindStudio_26.0.0.B050_005` | 2026-02-27 |
| 24 | `tag_MindStudio_26.0.0.B050_004` | 2026-02-27 |
| 25 | `tag_MindStudio_26.0.0.B050_003` | 2026-02-26 |
| 26 | `tag_MindStudio_26.0.0.B050_002` | 2026-02-26 |
| 27 | `tag_MindStudio_26.0.0.B050_001` | 2026-02-26 |
| 28 | `tag_MindStudio_26.0.0.B030_008` | 2026-02-10 |
| 29 | `tag_MindStudio_26.0.0.B030_007` | 2026-02-10 |
| 30 | `tag_MindStudio_26.0.0.B030_006` | 2026-02-10 |
| 31 | `tag_MindStudio_26.0.0.B030_005` | 2026-02-10 |
| 32 | `tag_MindStudio_26.0.0.B030_004` | 2026-02-10 |
| 33 | `tag_MindStudio_26.0.0.B030_003` | 2026-02-10 |
| 34 | `tag_MindStudio_26.0.0.B030_002` | 2026-02-10 |
| 35 | `tag_MindStudio_26.0.0.B030_001` | 2026-02-09 |
| 36 | `tag_MindStudio_26.0.0-alpha.1` | 2026-02-03 |
| 37 | `tag_MindStudio_26.0.0.B020_002` | 2026-01-30 |
| 38 | `tag_MindStudio_26.0.0.B020_001` | 2026-01-29 |
| 39 | `tag_MindStudio_26.0.0.B010_001` | 2026-01-19 |

**解读**：该表是表 4 阶段统计的展开，按发布时间倒序排列（共 39 条，对应表 4 各阶段数量之和）；表中可再次确认 `B030` 阶段实际仅 1 天出现于 2026-02-09（仅 1 版），其余 7 版集中于 2026-02-10；`B020` 阶段跨 2 天（2026-01-29 与 2026-01-30）；整张表从最早 `B010_001`（2026-01-19）到最新 `B090_004`（2026-03-27），共约 67 天的发布跨度。

## 【公式解读】

**原文（伪代码模板）：**
```text
tag_MindStudio_<major>.<minor>.<patch>.<stage>_<seq>
```

**符号含义**：
- `tag_MindStudio_` — 固定前缀，标识这是 MindStudio 系列 tag。
- `<major>` — 主版本号，本系列统一为 `26`。
- `<minor>` — 次版本号，本系列统一为 `0`。
- `<patch>` — 补丁版本号，本系列统一为 `0`。
- `<stage>` — 生命周期阶段标识，三种取值：`alpha.<n>`（预发布）、`Beta<n>_<seq>`（测试期）、`B<n><m>_<seq>`（公开构建，其中 `n` `m` 共同构成阶段号如 `090`）。
- `<seq>` — 阶段内序列号，3 位数字（如 `004` 表示该阶段第 4 个发布版本）。

**示例对照**：
- `tag_MindStudio_26.0.0.B090_004` = `tag_MindStudio_` + `26` + `.0` + `.0` + `.` + `B090` (stage=build phase 090) + `_004` (阶段内第 4 版)
- `tag_MindStudio_26.0.0.Beta1_001` = `tag_MindStudio_` + `26.0.0` + `.Beta1` (stage=beta 1) + `_001` (beta 第 1 版)
- `tag_MindStudio_26.0.0-alpha.1` = `tag_MindStudio_` + `26.0.0` + `-alpha.1` (stage=alpha 预发布第 1 版，注意分隔符为 `-` 而非 `.`)

## 【关联】

- **上游/入口**：本文档明确说明 GitCode release 页（https://gitcode.com/Ascend/msprof/releases）未提供详细特性摘要，本文是其**聚合补充**——即用户先访问 release 页确认版本存在，再回到本 changelog 查看发布时间线与阶段划分。
- **下游/安装**：文末 "Related Links" 指向 `./getting_started/msprof_install_guide.md`（msProf 安装指南），意味着读者在选定了具体版本 tag（如 `tag_MindStudio_26.0.0.B090_004`）后，下一步应跳转至安装指南进行部署，构成本文档 → 安装指南的串联路径。
- **仓库主页**：同时指向 https://gitcode.com/Ascend/msprof 仓库主页，作为版本元数据来源的根入口。
- **阶段间依赖关系**：alpha (`2026-02-03`) → Beta1 (`2026-02-28`) → B090 (`2026-03-26~27`) 体现了版本从预发布到测试再到正式构建的递进链路，且 Beta1 与 B050 在时间上紧邻（仅差 1 天），暗示 beta 节点用于阶段质量关口。

## 【使用方法】

原文未涉及具体的启用命令、配置项或 API 调用参数。本文档作为 changelog 仅提供版本元数据（tag、日期、阶段），具体的安装/启用方式需参阅文末链接的安装指南 `./getting_started/msprof_install_guide.md`。
