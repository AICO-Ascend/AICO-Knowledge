# 代码仓卡片 · ascendnpu-ir

> 骨架由 repo_card.py 机械生成 (全部事实来自 inventory/docs_index);
> 「分析层」小节由 LLM 深读填写, 每个事实须带仓库内出处 (文件路径)。

## 0. 元信息

| 项 | 值 |
|---|---|
| 仓库 | https://gitcode.com/Ascend/AscendNPU-IR.git |
| 分支 / HEAD | `master` @ `610d18b667fc` (2026-09-01) |
| 最新 tag | `v1.2.0-post` |
| 版本候选 |
  - git_tag: `v1.2.0-post`
| 文件数 / md 文档 / 图片 | 3778 / 102 / 35 |
| 语言分布 | {"C++": 992, "C/C++ hdr": 576, "Markdown": 102, "Python": 22, "YAML": 8, "C": 4, "Shell": 3, "JavaScript": 1} |
| 备注 | AscendNPU-IR是基于MLIR（Multi-Level Intermediate Representation）构建的，面向昇腾亲和算子编译时使用的中间 |

## 1. 定位 (LLM)

## 2. 架构与模块 (LLM, 基于下表 + 源码走读)

| 顶层路径 | 文件数 |
|---|---|
| `AGENTS.md` | 文件 |
| `CLAUDE.md` | 文件 |
| `CMakeLists.txt` | 文件 |
| `CODEOWNERS` | 文件 |
| `LICENSE` | 文件 |
| `NOTICE` | 文件 |
| `OWNERS` | 文件 |
| `README.md` | 文件 |
| `README_zh.md` | 文件 |
| `Third_Party_Open_Source_Software_Notice` | 文件 |
| `bishengir/` | 3524 |
| `build-tools/` | 83 |
| `docker` | 文件 |
| `docs/` | 142 |
| `third-party` | 文件 |

## 3. 功能逻辑 · 特性地图 (机械层: 23 篇特性文档聚类)

| 分组 | 数量 | 特性 |
|---|---|---|
| (核心) | 12 | 自动块化、自动展平、自动子块切分、自动同步、自定义算子、Cube与Vector优化、Cube与Vector软件流水优化、调试模块DFX … |
| CV | 2 | Cube-Vector Optimization Overview、Tile Cube and Vector Loop |
| AutoBlockify | 1 | Auto Blockify |
| AutoFlatten | 1 | Auto Flatten |
| AutoSchedule | 1 | AutoSchedule |
| AutoSubtiling | 1 | Auto-Subtiling |
| AutoSync | 1 | Auto-Sync |
| CVPipeline | 1 | Cube–Vector software pipelining |
| CustomOp | 1 | CustomOp |
| DFX | 1 | Debugging Module (DFX) |
| PlanMemory | 1 | Plan Memory |

## 4. 关键特性深读 (LLM 选 3-6 篇, 图文联合)

## 5. 版本与演进

  - (无 changelog)

## 6. 文档地图 (机械层)

| 类型 | 数量 |
|---|---|
| doc | 49 |
| feature | 23 |
| readme | 12 |
| api | 6 |
| guide | 6 |
| overview | 4 |
| faq | 2 |

## 7. 证据与出处

- 文档收割: extraction/repo_docs/ascendnpu-ir/ (102 篇)
- 清单: extraction/repo_inventory.json · extraction/repo_docs_index.json
