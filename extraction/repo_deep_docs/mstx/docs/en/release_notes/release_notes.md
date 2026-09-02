# MindStudio Tools Extension Library Release Notes

> 仓 `mstx` · 路径 `docs/en/release_notes/release_notes.md` · 类型 changelog · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mstx/docs/en/release_notes/release_notes.md

# MindStudio Tools Extension Library Release Notes 深度解读

## 【定位】
本文档是「MindStudio Tools Extension Library (msTX)」的版本发布说明 (Release Notes), 用于记录 msTX 库各版本的能力边界、版本依赖关系 (与 CANN、Python 的版本对应) 以及新增特性, 是一份面向开发者 / 工具链用户的版本基线说明文档。

---

## 【技术要点】

1. **双轨版本发布**: msTX 同时维护 `26.0.0` (Internal release, 内部发布) 与 `8.3.0` (Official release, 正式发布) 两个版本, 表明该库存在内部 / 正式两条发布线并行推进。
2. **强版本依赖**: msTX `26.0.0` 必须搭配 CANN `9.0.0 or later` + Python `3.11 or later`; msTX `8.3.0` 必须搭配 CANN `8.2.RC1 or later` + Python `3.11 or later`。Python 3.11 是统一基线。
3. **本轮无兼容变更**: 26.0.0 与 8.3.0 在 "Version Compatibility" 章节均明确标注 "No compatibility changes / No new features", 即本轮发版不引入破坏性改动。
4. **三大初始能力 (8.3.0 Initial release)**:
   - 核心 Tracing API: 支持代码执行点 marking 与 scope (作用域) 测量。
   - 域管理 API (Domain Management): 对 marks / scopes 进行分类管理, 实现多工具场景下的数据类型隔离。
   - 内存 Tracing API: 支持对内存区域 (memory region) 进行注册 / 注销, 供内存调试工具使用。
5. **定位为「工具扩展库」**: 透过 "Extension Library"、"tracing"、"memory debugging" 等措辞可见, msTX 本身不直接提供可视化或独立工具, 而是为上层 profiling / debugging 工具提供底层 API。

---

## 【关键机制与数据】

(原文无性能数据 / 数据流图, 以下仅为基于原文能力描述的机制还原)

- **Mark + Scope 机制**: 原文: "Provides core tracing APIs, supporting code execution point marking and scope measurement." 即 API 层提供两类基本动作 ——「mark」(代码执行点标记) 与「scope」(作用域计时 / 测量), 这是 tracing 工具的最底层原语。
- **Domain 隔离机制**: 原文: "Provides domain management APIs for categorizing marks and scopes, enabling data type isolation in multi-tool scenarios." 即通过 domain 把不同的 marks/scopes 划入命名空间, 避免多个工具同时插桩时数据相互覆盖 / 冲突。
- **Memory Region 注册机制**: 原文: "Provides memory tracing APIs, supporting registration and deregistration of memory regions for memory debugging tools." 即通过 register / deregister 让上层内存调试工具感知感兴趣内存区域的边界, 这是被动采集 → 主动注册语义的典型内存追踪做法。

> 原文未给出任何具体性能数据 (如延迟、吞吐、采样率), 也未给出数据流图。

---

## 【表格解读】

### 表格 1: Product Version Information

| Product | Version | Version Type |
|------|-------|------|
| msTX | 26.0.0 | Internal release |
| msTX | 8.3.0 | Official release |

**逐行解读**:
- 第 1 行 (26.0.0 / Internal release): msTX 26.0.0 为内部发布版, 通常面向内部联调 / 验证通道。
- 第 2 行 (8.3.0 / Official release): msTX 8.3.0 为正式对外发布版, 与下文 "Initial release" 对应, 是用户可引用的稳定基线。

### 表格 2: Related Product Version Mapping

| msTX | CANN Version | Python Version |
|----------|-----------------|----------|
| 26.0.0 | 9.0.0 or later | Python 3.11 or later |
| 8.3.0 | 8.2.RC1 or later | Python 3.11 or later |

**逐行解读**:
- 第 1 行 (26.0.0 ↔ CANN ≥ 9.0.0 ↔ Python ≥ 3.11): 内部版 msTX 26.0.0 强制绑定下一代 CANN 主线 (9.0.0+), Python 须为 3.11 及以上。
- 第 2 行 (8.3.0 ↔ CANN ≥ 8.2.RC1 ↔ Python ≥ 3.11): 正式版 msTX 8.3.0 兼容 CANN 8.2.RC1 及更高版本, Python 同样要求 3.11+, 说明 CANN 与 Python 升级是同步推进的。

---

## 【公式解读】

原文无公式。

---

## 【关联】

原文文末标注 "内部链接: (无)", 因此本节无法基于内置链接分析上下游关系。仅能依据原文能力描述做如下关联推断 (注意: 以下非原文直接给出的引用关系, 仅作能力层面梳理):

- **与 CANN 的关系**: msTX 在版本映射上显式依赖 CANN (`8.2.RC1 or later` / `9.0.0 or later`), 说明 msTX 是 CANN 工具链生态的一环, 应与 CANN 同步升级。
- **与 Python 的关系**: 强制 Python 3.11+, 表明 msTX 的 API 至少部分以 Python 绑定形式暴露, 需要 Python 解释器加载。
- **与上层 profiling / debugging 工具的关系**: 原文将 tracing / memory tracing 能力定位为 "for memory debugging tools"、"in multi-tool scenarios", 即 msTX 是底层 API 提供方, 上游是各种 profiler / debugger。
- **自身版本演进关系**: 8.3.0 标记为 "Initial release with the following features", 而 26.0.0 标注 "No new features", 说明本轮 26.0.0 是对内部通道的同步刷新, 没有新增能力, 真正具备新特性的是 8.3.0。

---

## 【使用方法】

原文未涉及。文档仅列出 API 能力点 (tracing / domain / memory tracing), 但**未给出**任何启用方式、配置项、命令行参数、环境变量、代码示例或 import 语句。
