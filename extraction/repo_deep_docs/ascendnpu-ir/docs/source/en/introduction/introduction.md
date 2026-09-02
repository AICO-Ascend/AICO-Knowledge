# Introduction

> 仓 `ascendnpu-ir` · 路径 `docs/source/en/introduction/introduction.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/ascendnpu-ir/docs/source/en/introduction/introduction.md

# AscendNPU IR Introduction 文档一体化深度解读

## 【定位】

本文档是 AscendNPU-IR 代码仓的 **总览介绍（Overview）**，用一段定义性陈述加四大能力维度的结构，向读者说明 AscendNPU IR 是什么、面向什么场景、提供了哪些层级化的抽象与编译能力，并给出从安装到深入架构的下一步导航。

---

## 【技术要点】

1. **基本定位**：AscendNPU IR 是基于 MLIR（Multi-Level Intermediate Representation）构建的、面向昇腾（Ascend）亲和算子编译的中间表示，目标是提供完整的昇腾表达能力、通过编译优化提升昇腾 AI 处理器效率，并通过开放接口灵活对接生态框架。

2. **多层级抽象与易用性**：
   - 高层抽象接口屏蔽 Ascend 计算、数据搬运、同步细节；
   - 编译器自动适配硬件，将硬件无关表达式映射到底层指令；
   - 提供细粒度性能控制接口，允许精确控制**片上存储布局（on-chip memory layout）、流水线同步插入点（pipeline synchronization insertion points）、乒乓流水线启用（ping-pong pipeline enablement）**，兼顾易用性与性能调优。

3. **分层方言（Layered dialects）与编译**：
   - **HFusion**：基于 Linalg 的扩展，用于硬件无关优化与生态集成；与 Arith、Math、Torch 等互相转换；具备张量简化（tensor simplification）、类型合法化（type legalization）、算子融合（operator fusion）能力。
   - **HIVM**：Tile 级别抽象，覆盖 Ascend 的**计算、数据搬运、同步**；支持 CV 算子映射（含 Mix kernel CV fusion、inter-core sync、CVPipeline、AutoSubTiling）、片上存储映射（on-chip memory mapping）、多级流水线/指令映射（multi-stage pipeline/instruction mapping）。
   - **HACC**：异构硬件抽象，覆盖 Host/Device 编程与 launch 语义；包含 **Annotation（编译器提示）** 与 **Scope（作用域标记）** 两大机制。

4. **关键编译特性**：
   - CV fusion 与 pipelining（**CVPipeline、AutoSubTiling**）；
   - 自动化内存规划 **PlanMemory**；
   - 自动化流水线同步 **AutoSync**；
   - 块化与调度 **AutoBlockify、AutoFlatten、AutoSchedule**；
   - Custom ops、DFX、面向可移植性能的 CV 优化，同时保留高层语义。

5. **生态与开放性**：通过分层接口对接 **PyTorch（Torch-MLIR）、TileLang、Triton** 等框架，在性能与易用性之间取得平衡。

---

## 【关键机制与数据】

本节按工作机制视角整合原文描述（原文均为定性陈述，未给出量化性能/吞吐数据）：

- **多层级抽象的工作原理（原文）**：
  - 上层（HFusion）以 Linalg 为基础表达计算图，专注"硬件无关"优化与算子融合；
  - 中层（HIVM）将上层算子分解为 Tile 级别的计算、数据搬运与同步原语，并映射到 CV 算子与片上存储；
  - 下层（HACC）负责 Host/Device 编程模型与 launch 语义，并通过 Annotation/Scope 标记提示编译器行为。

- **数据/控制流主线（原文）**：硬件无关表达式 → HFusion 优化与融合 → HIVM Tile 化并映射到 CV 内核（含同步、流水线）→ HACC 调度与作用域管理 → 映射到 Ascend 底层指令。

- **性能与数据（原文）**：原文**未给出任何量化性能数据、基准测试结果或具体参数数字**；仅以定性方式描述"通过编译优化提升效率""可移植性能（portable performance）"。

---

## 【表格解读】

**原文无表格**。原文通过四级标题加项目符号（`Key capabilities`）结构呈现能力矩阵，未使用任何 markdown/HTML 表格。

---

## 【公式解读】

**原文无公式**。文中未出现 LaTeX、伪代码或任何数学表达式。

---

## 【关联】

依据文末"Next steps"部分给出的内部链接，文档明确指向以下三类资源，构成从入门到深入的阅读链路：

| 链接 | 角色 | 与本文的关系 |
|------|------|--------------|
| `quick_start/installing_guide.md` | 安装与构建 | 落地本文档所述 IR 的前提步骤：环境准备与构建 |
| `quick_start/index.rst` | 快速开始 | 给出示例与入口，把本文档提到的 HFusion/HIVM/HACC 等能力落到可运行例子上 |
| `architecture.md` | 架构 | 阐释本文档所列分层方言（HFusion / HIVM / HACC）与编译流的逻辑与代码架构 |

逻辑关联：本文档是**入口性 Overview**；要落地则需 `installing_guide.md` 与 `quick_start/index.rst`；要深入理解分层方言的内部实现，则需 `architecture.md`。

---

## 【使用方法】

**原文未涉及**具体启用方式、配置项、命令行或 API 调用样例；本文档只列出能力与下一步导航。具体的安装命令、构建配置与示例运行方式，应参考 `quick_start/installing_guide.md` 与 `quick_start/index.rst`（链接见上节）。
