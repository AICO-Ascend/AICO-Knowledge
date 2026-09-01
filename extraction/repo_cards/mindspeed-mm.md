# 代码仓卡片 · mindspeed-mm

> 骨架由 repo_card.py 机械生成 (全部事实来自 inventory/docs_index);
> 「分析层」小节由 LLM 深读填写, 每个事实须带仓库内出处 (文件路径)。

## 0. 元信息

| 项 | 值 |
|---|---|
| 仓库 | https://gitcode.com/Ascend/MindSpeed-MM.git |
| 分支 / HEAD | `master` @ `ffb855ed62e4` (2026-09-01) |
| 最新 tag | `v26.1.0` |
| 版本候选 |
  - git_tag: `v26.1.0`
  - pyproject.toml: `0.1`
| 文件数 / md 文档 / 图片 | 1498 / 135 / 67 |
| 语言分布 | {"Python": 851, "Shell": 160, "Markdown": 135, "YAML": 71} |
| 备注 | 华为昇腾面向大规模分布式训练的多模态大模型套件，支撑多模态生成、多模态理解。 |

## 1. 定位 (LLM)

## 2. 架构与模块 (LLM, 基于下表 + 源码走读)

| 顶层路径 | 文件数 |
|---|---|
| `CONTRIBUTING.md` | 文件 |
| `LICENSE` | 文件 |
| `MANIFEST.in` | 文件 |
| `OWNERS` | 文件 |
| `README.md` | 文件 |
| `SECURITYNOTE.md` | 文件 |
| `Third-Party` | 文件 |
| `Open` | 文件 |
| `Source` | 文件 |
| `Software` | 文件 |
| `Notice.txt` | 文件 |
| `UserGuide/` | 68 |
| `bridge/` | 22 |
| `checkpoint/` | 48 |
| `ci` | 文件 |
| `docker/` | 13 |
| `docs/` | 73 |
| `evaluate_gen.py` | 文件 |

## 3. 功能逻辑 · 特性地图 (机械层: 43 篇特性文档聚类)

| 分组 | 数量 | 特性 |
|---|---|---|
| (核心) | 42 | EP Balance Strategy、FSDP2框架支持Agentic SFT、Async Activation Offload、AsyncPreprocessIterableDataset、Automatic Parallelism For Multi-Modal、数据负载均衡(数据分桶重排序)、针对VL模型的数据构造、标准等价模型 … |
| online-data-balance | 1 | Data balance |

## 4. 关键特性深读 (LLM 选 3-6 篇, 图文联合)

## 5. 版本与演进

  - 版本说明
  - 版本配套说明
  - 产品版本信息
  - 相关产品版本配套说明
  - 版本兼容性说明
  - 版本使用注意事项
  - 更新说明
  - 新增特性
  - 删除特性
  - 接口变更说明
  - 已解决问题
  - 遗留问题

## 6. 文档地图 (机械层)

| 类型 | 数量 |
|---|---|
| readme | 54 |
| feature | 43 |
| doc | 25 |
| overview | 6 |
| guide | 5 |
| faq | 1 |
| changelog | 1 |

## 7. 证据与出处

- 文档收割: extraction/repo_docs/mindspeed-mm/ (135 篇)
- 清单: extraction/repo_inventory.json · extraction/repo_docs_index.json
