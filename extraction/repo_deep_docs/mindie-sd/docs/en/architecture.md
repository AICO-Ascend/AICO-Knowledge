# Architecture Design

> 仓 `mindie-sd` · 路径 `docs/en/architecture.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-sd/docs/en/architecture.md

# mindie-sd 架构文档深度解读（docs/en/architecture.md）

---

## 【定位】

本文档定义了 MindIE SD（昇腾亲和的多模态加速系列套件）的整体架构设计，阐述其架构目标、能力边界、模块划分、特性归类与目录组织，作为该套件所有功能模块（layer、kernel、cache、parallelism、quantization、compilation 等）的总纲。

---

## 【技术要点】

基于原文，逐条保留关键术语与机制如下：

1. **总体定位与协同对象**：MindIE SD 旨在构建昇腾亲和的多模态加速套件，**配合 diffusers 等业界模型套件**实现昇腾上的高效多模态推理；接口遵循 diffusers 接口定义，支持基于 diffusers 的**插件式（simple plugin-based）适配**。
2. **加速算子层（layer 模块）**：提供昇腾亲和的多模态 FA、MM、MoE、quant 算子及融合算子，通过 layer 模块对外暴露 **attn、moe、quant 等 feature layer** 接口，是高级特性的基础并可独立使用。
3. **kernel 与 compilation 模块**：kernel 模块提供高性能昇腾算子，**支持 AscendC 与 Triton 等编程语言进行算子集成**；compilation 模块**基于 torch.compile inductor 机制**，通过自定义 fusion passes 实现昇腾亲和算子替换，**基于 FX 图能力**，开启编译后执行融合 pass，并在保留单算子派发的同时实现自动图改写。
4. **量化与稀疏**：通过 quantization 模块导入，为昇腾数据类型与计算分布提供**昇腾定制化的算法组合**（Ascend-tailored algorithm combinations），quantization 模块支持**自动启用（automatic enablement）**。
5. **计算-显存权衡（cache）**：在 **DiT 模块、DiT block、attention 等粒度**提供缓存算法，面向不同视角（view）场景支持加速。
6. **多卡并行**：提供 **CFG、USP 并行能力**，并为 MoE 场景提供**动态专家负载均衡（Dynamic EPLB）**；这些能力集成进加速算子 API，**接口替换后即自动启用**，parallelism 模块需要**与 layer 模块及 PyTorch 协同**。
7. **FA_Power_Cap 技术**：**拆分 FA 执行并与通信进行重排**，面向长序列视频生成，降低平均功耗并提升端到端性能。
8. **模块解耦与可组合性**：各模块**独立解耦**，可单独使用或组合使用；与业界 Cache-DiT、xDiT 等方案在 cache、parallelism 模块上形成选择关系，但 MindIE SD 的其他组件仍可与之**独立配合使用**。

---

## 【关键机制与数据】

**工作原理与数据流（原文表述）：**

- **layer 模块**：作为基础外部加速接口，包含 attn、moe、quant 等 feature layer；既是高级特性的依赖，也可独立使用。
- **kernel 模块**：提供面向多模态生成的昇腾高性能算子，通过 AscendC、Triton 等编程语言支持算子集成。
- **compilation 模块**：基于 FX 图能力（FX graph capabilities），开启编译后通过融合 pass 实现自动昇腾亲和加速；同时保留单算子派发能力。
- **quantization 模块**：作为高级特性，提供量化能力并支持自动启用。
- **cache 模块**：作为高级特性，提供"计算-显存权衡"（compute-to-memory tradeoff）加速能力的实现。
- **parallelism 模块**：作为高级特性，提供多卡分布式并行加速，需与 layer 模块及 PyTorch 协同。
- **多模态加速覆盖**：当前聚焦多模态**生成**；未来将进一步扩展至多模态**理解**、**全模态（omnimodal）** 等加速场景。

**性能数据：**

> 原文未提供任何具体的性能数字、加速比、吞吐量、显存占用、时延或功耗量化数据。文档仅以定性方式描述 FA_Power_Cap 可"降低平均功耗并提升端到端性能"，未给出原文数字。

---

## 【表格解读】

**原文无表格。** 文档中仅出现一处 `text` 代码块（目录结构树），不是参数表/性能对比/配置项意义上的表格，因此本节标注为"原文无表格"。目录结构如下（仅作结构参考，非表格）：

```text
|- benchmarks         // Core kernel performance monitoring and compilation acceleration effect monitoring
|- build              // Build scripts
|- csrc               // Ascend kernel source code location
|- docs               // Project documentation
|- examples
  |- cache            // Cache feature sample: enable cache for model acceleration
  |- service          // Servitization sample: convert command-line mode to servitization
  |- wan              // Model inference sample: model inference commands and parameter configuration
|- mindiesd
  |- cache_agent      // Advanced feature: provides cache capabilities
  |- compilation      // Provides compilation capabilities, implementing automatic graph modification based on FX graph (while still maintaining single-operator dispatch)
  |- eplb             // Advanced feature: provides expert parallel load balancing capabilities
  |- layers           // Provides basic PyTorch layer interfaces
  |- quantization     // Advanced feature: provides quantization capabilities
  |- utils            // Core utility module, providing shared infrastructure services and common functionality
|- tests              // Test cases
```

**目录解读**：源代码主体位于 `mindiesd/` 下，按职责分为 `layers`（基础层接口）、`compilation`（编译/FX图改写）、`quantization`、`cache_agent`、`eplb`（EPLB）、`utils`（共享基础设施）；昇腾算子源码在 `csrc/`；`examples/` 下提供 cache、service、wan 三类示例；`benchmarks/` 用于核心算子性能与编译加速效果监测。

---

## 【公式解读】

**原文无公式。** 文档中未出现任何 LaTeX 数学公式、伪代码公式或参数化表达式。

---

## 【关联】

依据原文"Key Features"与"Architecture Overview"段落及其内部链接，本文档与其他模块/特性/示例的关联如下：

| 文档中提到的主题 | 关联资源 | 关联描述（原文表述） |
|---|---|---|
| 昇腾亲和加速算子（FA/MM/MoE/quant、融合算子，layer 模块外部接口） | `./features/core_layers.md` | "accessible externally through the layer module. For details, see Core Acceleration API" |
| 稀疏能力 | `./features/sparse.md` | 与 Quantization 并列的"Sparsity and Quantization capabilities" |
| 量化能力 | `./features/quantization.md` | 量化模块支持自动启用 |
| 计算-显存权衡（缓存） | `./features/cache.md` | "cache algorithms at DiT module, DiT block, attention, and other granularities" |
| CPU Offload | `./features/cpu_offload.md` | 与 cache、share_memory 并列，属于计算-显存权衡的子手段 |
| 显存共享（VRAM Sharing） | `./features/share_memory.md` | 同上 |
| 多卡并行（CFG、USP） | `./features/parallelism.md` | 与 layer 模块及 PyTorch 协同 |
| 动态专家负载均衡（Dynamic EPLB） | `./features/DyEPLB.md` | "dynamic expert load balancing … for MoE scenarios" |
| FA_Power_Cap 技术 | `./features/fa_power_cap.md` | "Splits FA execution and reorders FA with communication" |
| 编译融合特性（FX 图、fusion passes） | `./features/compilation.md` | "Based on FX graph capabilities, enables fusion passes after compilation is turned on" |
| 服务化部署示例 | `../../examples/service` | "convert command-line mode to servitization" |
| 多模态推理加速示例 | `../../examples/cache` | "multimodal inference acceleration samples"（在文末 Note 段落中提及） |
| 已发布的模型 | Modelers / ModelZoo 外链 | "diffusers models accelerated on Ascend using MindIE SD are published on Modelers/ModelZoo" |

**上下游关系**：
- **上游**：diffusers（接口规范来源）、PyTorch（含 torch.compile inductor 与 FX 图能力）、昇腾硬件。
- **下游**：用户在 diffusers 上做"插件式适配"即可获得昇腾加速；可通过 `examples/service` 进行服务化部署。
- **平行替代**：与业界 Cache-DiT、xDiT 在 cache、parallelism 模块上属于"选择关系"，但 MindIE SD 其余组件仍可与这些方案独立配合。

---

## 【使用方法】

原文**未提供具体的启用命令、配置项、API 调用代码或参数表**。仅可从原文中推断出的使能约束如下：

- **quantization 模块**："Supports automatic enablement of quantization capabilities"——支持自动启用，但具体触发条件/配置未在本文档给出。
- **parallelism 模块**："requiring collaboration with the layer module and PyTorch"——需与 layer 模块及 PyTorch 协同使用。
- **MoE EPLB**：与并行能力一同"集成到加速算子 API，接口替换后自动启用（integrated into the acceleration operator APIs for automatic enablement after interface replacement）"。
- **compilation 融合**："after compilation is turned on"——需手动开启编译开关以触发融合 pass。
- **diffusers 插件式适配**："simple plugin-based adaptation directly on diffusers is also supported"——支持直接基于 diffusers 进行插件式适配，但具体接入步骤未在本文档列出。
- **示例参考**：`examples/cache`（cache 特性）、`examples/service`（服务化）、`examples/wan`（模型推理命令与参数配置）。

> 具体 API 形态、命令行参数、环境变量、量化位宽、并行拓扑等使能细节，请参阅上文【关联】一节列出的各子特性文档（`./features/*.md`）与示例代码（`../../examples/*`），本文档作为架构总纲不展开。

## 图文联合解读

- `architecture_overview.png`: 图示采用分层架构：上层为外部生态（Modelers、ModelZoo、vllm-omni、diffusers、cache-dit）；中间 MindIE SD 核心包含 cache、quantization、parallelism 三大加速模块，layer 子模块封装 attn、moe、quant 算子，底层由 kernel、compilation 支撑；右侧 benchmark、example（service、MMInfer）提供测试与样例；最底层为 PyTorch 与 CANN。

论证结论：MindIE SD 是位于 PyTorch/CANN 之上的"可独立、可组合"加速层，与行业方案解耦共存。

与文档呼应：直观印证"modules are independently decoupled，可单独或组合使用"的论点，cache/parallelism 可被 cache-dit 等替代，其余组件仍可复用。
