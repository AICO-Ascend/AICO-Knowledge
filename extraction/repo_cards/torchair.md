# 代码仓卡片 · torchair

> 骨架由 repo_card.py 机械生成 (全部事实来自 inventory/docs_index);
> 「分析层」小节由 LLM 深读填写, 每个事实须带仓库内出处 (文件路径)。

## 0. 元信息

| 项 | 值 |
|---|---|
| 仓库 | https://gitcode.com/Ascend/torchair.git |
| 分支 / HEAD | `master` @ `12396e9f34a6` (2026-09-01) |
| 最新 tag | `None` |
| 版本候选 |
  - (未检出)
| 文件数 / md 文档 / 图片 | 1875 / 164 / 57 |
| 语言分布 | {"Python": 1263, "C/C++ hdr": 285, "Markdown": 164, "C++": 35, "YAML": 9, "Shell": 6, "TypeScript": 1} |
| 备注 | TorchAir 支持用户基于PyTorch框架和torch_npu插件在昇腾NPU上使用图模式进行推理。 |

## 1. 定位 (LLM)

## 2. 架构与模块 (LLM, 基于下表 + 源码走读)

| 顶层路径 | 文件数 |
|---|---|
| `AGENTS.md` | 文件 |
| `CMakeLists.txt` | 文件 |
| `CONTRIBUTING.md` | 文件 |
| `LICENSE` | 文件 |
| `OWNERS` | 文件 |
| `README.md` | 文件 |
| `RELEASE.md` | 文件 |
| `SECURITY_README.md` | 文件 |
| `Third_Party_Open_Source_Software_Notice` | 文件 |
| `build.sh` | 文件 |
| `build_and_install.sh` | 文件 |
| `classify_rule.txt` | 文件 |
| `classify_rule.yaml` | 文件 |
| `cmake` | 文件 |
| `codegen` | 文件 |
| `configure` | 文件 |
| `configure.py` | 文件 |
| `docker/` | 3 |

## 3. 功能逻辑 · 特性地图 (机械层: 38 篇特性文档聚类)

| 分组 | 数量 | 特性 |
|---|---|---|
| advanced | 25 | 计算与通信并行功能、模型编译缓存功能、算子Converter支持度导出功能、算子data dump功能、算子级确定性计算配置功能、动态shape图分档执行功能、Dynamo导图功能、图编译统计信息导出功能 … |
| basic | 12 | 基础功能、集合通信入图、TorchAir C++层日志打印、算子data dump功能（Eager模式）、多流并发死锁检测功能、图编译Debug信息保存功能、图结构dump功能、FX图算子融合Pass配置功能 … |
| (核心) | 1 | GE图模式功能 |

## 4. 关键特性深读 (LLM 选 3-6 篇, 图文联合)

## 5. 版本与演进

  - (无 changelog)

## 6. 文档地图 (机械层)

| 类型 | 数量 |
|---|---|
| doc | 61 |
| api | 54 |
| feature | 38 |
| readme | 7 |
| guide | 2 |
| overview | 2 |
| design | 2 |
| faq | 1 |

## 7. 证据与出处

- 文档收割: extraction/repo_docs/torchair/ (167 篇)
- 清单: extraction/repo_inventory.json · extraction/repo_docs_index.json
