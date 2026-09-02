# 简介

> 仓 `ascendnpu-ir` · 路径 `docs/source/zh_cn/introduction/introduction.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/ascendnpu-ir/docs/source/zh_cn/introduction/introduction.md

# AscendNPU-IR 简介文档一体化深度解读

## 【定位】
这篇文档是 AscendNPU IR 的官方 overview，旨在用一篇文章向读者说明：AscendNPU IR 是基于 MLIR 构建的、面向昇腾 AI 处理器亲和算子编译的中间表示层，它"提供什么能力、分几层抽象、支持哪些编译特性、如何对外生态对接"，并指明读者下一步该走向"安装构建 / 快速上手 / 架构设计"三条入口。

---

## 【技术要点】

1. **基础定位**：AscendNPU IR 基于 MLIR（Multi-Level Intermediate Representation），是面向昇腾亲和算子编译的中间表示，强调"完备表达能力 + 编译优化提升计算效率 + 开源社区开放接口"。
2. **多级抽象 / 双层接口**：
   - 高层接口屏蔽昇腾"计算、搬运、同步"指令细节，由编译器自动感知硬件架构并完成映射；
   - 细粒度接口允许手动控制"片上内存布局、流水同步插入位置、是否使能乒乓流水"等调优开关。
3. **三层方言（HFusion / HIVM / HACC）**：
   - **HFusion**：基于 Linalg 扩展，做硬件相对无关的优化与生态对接，支持与 Arith、Math、Torch 等方言的转换，负责 Tensor 化简、类型合法化、算子融合生成；
   - **HIVM**：面向昇腾对"计算、搬运、同步"做 Tile 级抽象，屏蔽底层指令参数；负责 CV 核映射（Mix Kernel 的 CV 融合、核间同步、CVPipeline 流水与 AutoSubTiling 等）、核内片上内存映射与多级流水 / 指令映射；
   - **HACC**：异构硬件抽象，表达 Host/Device 编程模型与 launch 语义；Annotation、Scope 等用于 `compiler hint` 与作用域标记。
4. **关键编译特性**：CV 融合与流水（CVPipeline、AutoSubTiling）、自动内存规划（PlanMemory）与流水同步（AutoSync）、块化与调度（AutoBlockify、AutoFlatten、AutoSchedule），以及自定义算子、DFX、CV 优化等。
5. **生态对接**：通过分层接口对接 PyTorch（Torch-MLIR）、TileLang、Triton 及各类框架，追求"高性能与易用性的灵活平衡"。
6. **下一步导航**：指向 installing_guide（环境与编译）、quick_start/index（示例与使用入口）、architecture（逻辑架构 / 代码架构 / 编译流程）三篇文档。

---

## 【关键机制与数据】

- **原文：抽象层级机制**——高层抽象接口"屏蔽昇腾计算、搬运、同步等指令细节"，由编译器"自动感知硬件架构并将硬件无关表达映射到底层指令"；细粒度接口则暴露"片上内存布局、流水同步插入位置、是否使能乒乓流水"等开关，做到"兼顾易用与性能调优"。
- **原文：HFusion 数据流**——以 Linalg 扩展为基座，承接 Arith / Math / Torch 等方言的转换输入，输出经过 Tensor 化简、类型合法化、算子融合生成后的 IR，作为生态对接和硬件相对无关优化的入口。
- **原文：HIVM 数据流**——输入是经过 HFusion 优化的硬件相对无关表达；HIVM 在 Tile 粒度上对"计算、搬运、同步"做抽象，屏蔽底层指令参数；向下产出三组结果：(a) CV 核映射（含 Mix Kernel 的 CV 融合、核间同步、CVPipeline 流水、AutoSubTiling）、(b) 核内片上内存映射、(c) 多级流水 / 指令映射。
- **原文：HACC 数据流**——表达 Host/Device 编程模型与 launch 语义；通过 Annotation、Scope 给编译器提供 hint 与作用域标记。
- **原文：编译优化全景**——同一条算子表达可依次经过：CV 融合与流水（CVPipeline、AutoSubTiling）→ 自动内存规划（PlanMemory）与流水同步（AutoSync）→ 块化与调度（AutoBlockify、AutoFlatten、AutoSchedule）→ 自定义算子 / DFX / CV 优化，文档强调这是在"保持高层语义的前提下获得可移植性能"。
- **性能数据**：原文未涉及任何具体数字（吞吐、时延、加速比等）。

---

## 【表格解读】

**原文无表格**（该 introduction.md 内未出现任何参数表、性能对比表或配置项表格）。

---

## 【公式解读】

**原文无公式**（该 introduction.md 内未出现 LaTeX 或伪代码形式的公式）。

---

## 【关联】

根据文末"下一步"一节给出的内部链接，可梳理出本文与同仓其他文档的上下游关系：

| 文中提到的特性 / 模块 | 对应的入口文档 | 关系性质 |
|---|---|---|
| 安装与构建（环境与编译） | [quick_start/installing_guide.md](quick_start/installing_guide.md) | 下游：本文介绍完能力后，引导读者先搭建编译环境 |
| 快速开始（示例与使用入口） | [quick_start/index.rst](quick_start/index.rst) | 下游：本文介绍完分层方言与编译特性后，给出可运行示例的入口 |
| 架构设计（逻辑架构、代码架构与编译流程） | [architecture.md](architecture.md) | 下游：本文仅"点到为止"地列出 HFusion / HIVM / HACC 三层方言与若干 Auto* 优化，详细逻辑/代码结构与端到端编译流程在 architecture.md 中展开 |

文档自身的逻辑链是：**定位 → 三层方言（HFusion/HIVM/HACC）→ 关键编译特性 → 生态对接 → 下一步导航**，其中 HFusion / HIVM / HACC 与 CVPipeline / AutoSubTiling / PlanMemory / AutoSync / AutoBlockify / AutoFlatten / AutoSchedule 等 Auto\* 系列是本文最核心的"特性名词锚点"，均会在 architecture.md 与 quick_start 中被进一步展开。

---

## 【使用方法】

**原文未涉及**任何具体的启用方式、配置项、命令行或 API 调用示例。原文仅在"下一步"一节中以链接形式提示：

- 编译环境的搭建见 [quick_start/installing_guide.md](quick_start/installing_guide.md)（原文标注："环境与编译"）；
- 示例与使用入口见 [quick_start/index.rst](quick_start/index.rst)（原文标注："示例与使用入口"）；
- 编译流程的完整说明见 [architecture.md](architecture.md)（原文标注："逻辑架构、代码架构与编译流程"）。

具体的构建命令、依赖列表、运行步骤需进入上述三篇文档查阅。
