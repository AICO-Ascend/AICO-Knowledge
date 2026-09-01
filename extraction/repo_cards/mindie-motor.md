# 代码仓卡片 · mindie-motor

> 骨架由 repo_card.py 机械生成 (全部事实来自 inventory/docs_index);
> 「分析层」小节由 LLM 深读填写, 每个事实须带仓库内出处 (文件路径)。

## 0. 元信息

| 项 | 值 |
|---|---|
| 仓库 | https://gitcode.com/Ascend/MindIE-Motor.git |
| 分支 / HEAD | `master` @ `46c4b33fd48a` (2026-09-01) |
| 最新 tag | `3.1.0` |
| 版本候选 |
  - git_tag: `3.1.0`
| 文件数 / md 文档 / 图片 | 1046 / 137 / 64 |
| 语言分布 | {"Python": 542, "Markdown": 137, "Shell": 67, "YAML": 57, "Rust": 21, "C++": 5, "JavaScript": 1} |
| 备注 | 昇腾自研推理集群管理框架 |

## 1. 定位 (LLM)

## 2. 架构与模块 (LLM, 基于下表 + 源码走读)

| 顶层路径 | 文件数 |
|---|---|
| `AGENTS.md` | 文件 |
| `LICENSE.md` | 文件 |
| `Makefile` | 文件 |
| `README.md` | 文件 |
| `build.sh` | 文件 |
| `contributing.md` | 文件 |
| `docker/` | 30 |
| `docs/` | 154 |
| `examples/` | 289 |
| `image.png` | 文件 |
| `mkdocs.yml` | 文件 |
| `motor/` | 297 |
| `pre-commit` | 文件 |
| `pytest.ini` | 文件 |
| `requirements.txt` | 文件 |
| `requirements` | 文件 |
| `scripts` | 文件 |
| `security.md` | 文件 |

## 3. 功能逻辑 · 特性地图 (机械层: 24 篇特性文档聚类)

| 分组 | 数量 | 特性 |
|---|---|---|
| (核心) | 12 | EPD分离部署能力说明、自动弹性扩缩容、容器快照、KV Cache 亲和性调度、手动扩缩容、max_tokens 自适应、PD分离说明、精度检测功能 … |
| kv_cache_store | 4 | MemCache 后端、Mooncake 后端、在 MindIE Motor 中部署 UCM、Yuanrong 后端 |
| fault_tolerance | 3 | 故障场景重调度、ScaleP2D 故障恢复、主备倒换特性 |
| observability | 3 | 功能介绍、MindIE Motor 可观测性栈 · Grafana 使用指导、MindIE Motor 可观测性栈 · 服务拉起与停止指导 |
| agentic | 1 | Prefill Context Parallel (PCP) 与跨节点 PCP |
| security | 1 | secure_h2d功能使用指导 |

## 4. 关键特性深读 (LLM 选 3-6 篇, 图文联合)

## 5. 版本与演进

  - (无 changelog)

## 6. 文档地图 (机械层)

| 类型 | 数量 |
|---|---|
| doc | 65 |
| readme | 29 |
| feature | 24 |
| design | 11 |
| api | 4 |
| overview | 3 |
| guide | 1 |

## 7. 证据与出处

- 文档收割: extraction/repo_docs/mindie-motor/ (137 篇)
- 清单: extraction/repo_inventory.json · extraction/repo_docs_index.json
