# Transform Dialect Tutorial

> 仓 `msdebug` · 路径 `mlir/docs/Tutorials/transform/_index.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msdebug/mlir/docs/Tutorials/transform/_index.md

# Transform Dialect Tutorial (索引页) 一体化深度解读

## 【定位】
本篇文档是 MLIR "Transform Dialect Tutorial" 的索引/总览页,用于介绍 MLIR 中基于 transform dialect 的声明式编译器变换控制机制,并给出该教程的章节结构与三类应用场景的概览。

## 【技术要点】
1. **声明式变换控制**: MLIR 支持通过 transform dialect,使用编译器 IR 自身声明式地指定对编译器的变换请求(原文: "MLIR supports declarative specification for controlling compiler transformations via the transform dialect")。
2. **两种 IR 嵌入方式**: 变换请求既可嵌入到被变换的原始 IR 中(类似 pragma),也可独立提供(类似 scheduling language)(原文: "embedded into the original IR that is being transformed (similarly to pragmas) or supplied separately (similarly to scheduling languages)")。
3. **三类使用场景**: 
   - 组合上游 MLIR 已有的 transform dialect 操作,对 linalg 线性代数操作做一串优化变换以产出高效代码;
   - 定义新的 transform dialect 操作,并适配已有变换代码到 transform dialect 基础设施;
   - 在带自定义 dialect / 变换 / pass 的下游 out-of-tree 项目中搭建并使用 transform dialect 基础设施。
4. **教程章节结构**: 共 6 章 — Chapter #0 至 Chapter #4,以及额外的 Chapter H(Reproducing Halide Schedule)。
5. **代码与测试路径**: 教程对应代码位于 `mlir/Examples/transform`,对应测试位于 `mlir/test/Examples/transform`。
6. **前置条件**: 需要具备 MLIR 基础知识,原文明示参见 Toy tutorial 作为 MLIR 入门。

## 【关键机制与数据】
- **工作机制(原文表述)**: transform dialect 通过编译器 IR 本身来"请求"编译器变换;该 IR 既能与被变换的 IR 内联(pragma 风格),也能作为独立模块提供(scheduling language 风格)。
- **应用场景目标产物(原文表述)**: 在第一类场景下,目标是"results in efficient code for an MLIR linear algebra operation",即对 linalg 操作生成高效的优化后代码。
- **扩展性(原文表述)**: 学完本教程后,读者将"able to apply the Transform dialect in their work and extend it when necessary"。
- **范围限定(原文表述)**: 本教程覆盖三种场景 — composing 现有操作、定义新操作、下游项目落地 — 并未给出具体的性能数字或量化数据(原文未提供任何性能基准/统计数字)。

## 【表格解读】
原文无表格。

## 【公式解读】
原文无公式。

## 【关联】
- **上游/下游关系**: 文中区分了 "(upstream) MLIR"(组合其已有 transform dialect 操作)与 "downstream out-of-tree project with custom dialects, transformations and passes"(场景三),说明 transform dialect 既服务于上游标准用法,也支持下游自定义扩展。
- **领域方言引用**: 第一类使用场景明确涉及 "MLIR linear algebra operation" 和 "Linalg Operations"(Ch0 标题),表明 transform dialect 与 MLIR 的 linalg dialect 紧密协作。
- **与其他方言/项目的关系**: ChH 标题为 "Reproducing Halide Schedule",暗示 transform dialect 可用于复现/借鉴 Halide 这类 scheduling language 的调度思路。
- **章节间的递进关系**: 
  - Ch0 — 概念预备("Structured Linalg Operations") 
  - Ch1 — 组合已有变换(Ch0→Ch1 是从概念到实践)
  - Ch2 — 添加简单新变换操作(从使用到扩展)
  - Ch3 — 超越简单操作(更复杂的扩展)
  - Ch4 — 将 transform 操作与 payload 做匹配(将变换绑定到目标 IR)
  - ChH — 综合应用(Reproducing Halide Schedule)
- **外部教程关联**: 文末明示"See [Toy tutorial](../Toy) for introduction to MLIR",将本教程锚定在以 Toy tutorial 作为 MLIR 入门先修。
- **代码/测试组织**: `mlir/Examples/transform`(代码)与 `mlir/test/Examples/transform`(测试)的并列说明,表明教程在仓库中以"示例 + 测试"双轨形式组织。

## 【使用方法】
- **教程代码路径**: `mlir/Examples/transform`(原文)
- **教程测试路径**: `mlir/test/Examples/transform`(原文)
- **前置条件**: "Basic familiarity with MLIR is a prerequisite"(原文);入门指引见 [Toy tutorial](../Toy)。
- **章节入口(逐章链接)**:
  - [Chapter #0](Ch0.md) — A Primer on "Structured" Linalg Operations
  - [Chapter #1](Ch1.md) — Combining Existing Transformations
  - [Chapter #2](Ch2.md) — Adding a Simple New Transformation Operation
  - [Chapter #3](Ch3.md) — More than Simple Transform Operations
  - [Chapter #4](Ch4.md) — Matching Payload with Transform Operations
  - [Chapter H](ChH.md) — Reproducing Halide Schedule
- **未涉及项**: 原文未给出具体的编译命令、CMake 配置项、启用开关或运行方式 — 这些细节在各章节(Ch0–Ch4、ChH)正文中另行说明,本索引页不涉及。
