# 架构设计

> 仓 `mindie-sd` · 路径 `docs/zh/architecture.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-sd/docs/zh/architecture.md

# mindie-sd `docs/zh/architecture.md` 深度解读

---

## 【定位】

这篇文档定位为 **MindIE SD 套件的架构总览**，目的是交代其在昇腾平台上承担"多模态推理加速套件"的角色边界——即说明它解决「如何把业内的多模态推理框架（如 diffusers）高效迁移到昇腾硬件」这一工程问题，并梳理出各加速能力（layer、kernel、compilation、cache、parallelism、quantization、sparse、FA_Power_Cap 等）的层次关系与组合使用方式。

---

## 【技术要点】

1. **架构定位与协同对象**：MindIE SD 自身定位为「昇腾亲和的多模态加速系列套件」，不替代 diffusers 等模型套件，而是作为配合的加速层；接口遵循 diffusers 的接口定义，支持对 diffusers 做"简单插件化改造"后接入（原文：*"MindIE SD的相关接口遵从diffusers的接口定义"*）。
2. **核心模块解耦**：layer、kernel、compilation、quantization、cache、parallelism 等模块独立解耦，可单独使用也可叠加；这意味着与业内 Cache-DiT、xDiT 等同类方案存在选择关系时，MindIE SD 的其他组件仍可单独与之叠加（原文：*"各模块间独立解耦设计，可单独使用也可以叠加使用"*）。
3. **基础三件套（layer / kernel / compilation）**：layer 模块提供 attn/moe/quant 等高层 PyTorch layer 接口；kernel 模块提供 AscendC 与 triton 编程语言接入的昇腾高性能算子；compilation 模块基于 fx graph 与 torch.compile 的 inductor 机制，开启 compile 后通过自定义融合 pass 实现昇腾亲和算子替换（自动亲和加速）。
4. **加速三策略**：
   - **以存代算**：cache 模块提供 DiT module、DiT block、attn 等多粒度 cache 算法，配合 cpu_offload 与 share_memory 形成完整 memory swap 体系；
   - **多卡并行**：parallelism 模块提供 CFG、USP 等并行能力，并将这些能力融入 layer 模块的 API，使外部仅需"接口替换"即可自动使能；
   - **MoE 动态专家负载均衡**：DyEPLB（EPLB）面向 MoE 场景。
5. **量化与稀疏**：quantization 与 sparse 模块针对昇腾的数据类型和算力分布提供亲和算法组合，需通过 quantization 模块导入使用。
6. **FA_Power_Cap 技术**：面向长序列视频生成场景，通过"切分 FA 并重排 FA 与通信执行顺序"来降低整网平均功耗并提升端到端性能（原文给出的两个动作：切分 FA、重排 FA 与通信的执行顺序）。

---

## 【关键机制与数据】

**工作机制层次（自下而上）：**

- **硬件执行层**（kernel 模块，原文）："提供多模态生成相关的昇腾高性能 kernel，支持 AscendC 和 triton 等编程语言的算子接入。"
- **算子封装层**（layer 模块，原文）："提供基础对外的加速接口（包含 attn，moe，quant 等特性的 layer），是高阶特性的基础，本身可以单独使用。"
- **图优化层**（compilation 模块，原文）："基于 fx graph 的能力，开启 compile 后使能融合 pass，实现昇腾自动亲和加速。"
- **高阶特性层**：quantization、cache、parallelism 模块作为高级特性，cache 模块"提供以存代算的加速能力的实现"；parallelism 模块"提供多卡并行的分布式加速能力，需要与 layer 模块和 PyTorch 协同实现"，且"融入加速算子的 API 中，实现接口替换后的自动使能"——这是其"自动使能"机制的关键数据流描述。

**FA_Power_Cap 机制（原文）：** "通过切分 FA 并重排 FA 与通信执行顺序，降低整网平均功耗并提升端到端性能。"——其作用对象是长序列视频生成场景，机理是"切分 + 重排"，性能收益维度是"平均功耗"与"端到端性能"两项。

**性能/数据数字**：原文未给出具体的数值（如加速比、显存节省比例、功耗下降幅度、tflops 等），仅给出目录结构与模块名称，故本节不做虚构推算。

---

## 【表格解读】

**原文无表格**。文档中的结构化呈现以代码块目录树代替表格（见【使用方法】中的目录结构块），其余均以项目符号与文字段落叙述。

---

## 【公式解读】

**原文无公式**。文档未包含任何 LaTeX 公式或伪代码公式。

---

## 【关联】

**与文中提到的其他特性/模块的上下游关系**（基于原文与文末内部链接）：

- **基础算子侧**
  - `layer` 模块（attn/moe/quant 的 layer）是 [核心加速 API](./features/core_layers.md) 的承载者；
  - `kernel` 模块由 [核心加速 API](./features/core_layers.md) 描述其能力入口；
  - `compilation` 模块在 [编译特性](./features/compilation.md) 中展开（链接 `./features/compilation.md`，原文已引用但未列入本次给定链接列表）。
- **存代算 / 内存策略侧**
  - `cache` 模块 ↔ [以存代算](./features/cache.md)；
  - 与之配套的 [CPU 卸载](./features/cpu_offload.md) 和 [显存共享](./features/share_memory.md) 共同构成"以存代算"的完整方案。
- **算法侧**
  - 量化通过 `quantization` 模块导入使用 ↔ [量化](./features/quantization.md)；
  - 稀疏能力 ↔ [稀疏](./features/sparse.md)。
- **并行侧**
  - `parallelism`（CFG、USP） ↔ [多卡并行](./features/parallelism.md)；
  - MoE 场景的动态专家负载均衡 ↔ [动态专家负载均衡（DyEPLB）](./features/DyEPLB.md)。
- **功耗优化侧**
  - 长序列视频生成场景的 FA_Power_Cap ↔ [FA_Power_Cap 技术](./features/fa_power_cap.md)。
- **外部生态衔接**
  - `examples/cache` 提供 cache 特性样例 ↔ 文档中提及的"多模态推理加速样例请参见[Cache](../../examples/cache)"（在文末 NOTE 中）；
  - `examples/service` 提供服务化部署样例 ↔ [服务化](../../examples/service)；
  - 已基于 MindIE SD 实现昇腾加速的 diffusers 模型发布在 Modelers / ModelZoo（原文链接已给出）。
- **与同类方案的关系**：原文提到业内存在 Cache-DiT、xDiT 等方案，"其效果与 cache 模块和 parallelism 模块功能相似，存在方案选择的问题，但是 MindIE SD 中其他组件依旧可以单独与之叠加使用"——这表明 cache 与 parallelism 模块与第三方同类方案存在功能重叠/替代关系，其余模块（layer / kernel / compilation / quantization / sparse / cpu_offload / share_memory / DyEPLB / FA_Power_Cap）则可与第三方方案叠加使用。

---

## 【使用方法】

**启用方式 / 模块入口（原文以"目录结构"形式给出）：**

```
|- benchmarks         // 提供核心kernel的性能看护和compilation的加速效果看护
|- build              // 编译脚本
|- csrc               // 昇腾kernel代码位置
|- docs               // 项目文档
|- examples
  |- cache            // cache特性样例：使能cache进行模型加速
  |- service          // 服务化样例：将命令行模式改造成服务化方式
  |- wan              // 模型推理样例：模型推理命令以及参数配置
|- mindiesd
  |- cache_agent      // 高阶特性：提供cache能力
  |- compilation      // 提供编译能力，基于fx graph实现自动改图（可依旧保持单算子下发）
  |- eplb             // 高阶特性：提供专家并行负载均衡能力
  |- layers           // 提供基础的PyTorch的layer接口
  |- quantization     // 高阶特性：提供量化能力
  |- utils            // 核心工具模块，提供共享的基础设施服务和通用功能
|- tests              // 测试用例
```

**关键使用入口（按原文表述）：**

- **layer / kernel 模块**：作为"基础对外的加速接口"可单独使用；layer 模块融入 CFG / USP 等并行能力，"实现接口替换后的自动使能"（原文）。具体 API 入口与签名请参见 [核心加速 API](./features/core_layers.md)。
- **compilation 模块**：需要"开启 compile"以使能融合 pass（原文：*"开启 compile 后使能融合 pass，实现昇腾自动亲和加速"*）。
- **quantization 模块**：作为高阶特性"支持量化能力的自动使能"，且稀疏/量化通过该模块导入使用（原文：*"通过 quantization 模块导入使用"*）。
- **cache 模块**：作为高阶特性提供以存代算能力；具体粒度（DiT module、DiT block、attn）见 [以存代算](./features/cache.md)。
- **parallelism 模块**：作为高阶特性，与 layer 模块和 PyTorch 协同使用（原文：*"需要与 layer 模块和 PyTorch 协同实现"*）。
- **examples 样例**：cache 加速样例见 `examples/cache`（README 路径在原文中已指示）；服务化部署样例见 [`examples/service`](../../examples/service)；模型推理样例见 `examples/wan`。
- **外部模型入口**：基于 MindIE SD 实现昇腾加速的 diffusers 模型发布在 [Modelers](https://modelers.cn/models?name=MindIE&page=1&size=16) 与 [ModelZoo](https://www.hiascend.com/software/modelzoo) 上（原文链接），亦"支持直接基于 diffusers 进行简单插件化改造"。

**具体 CLI 命令、配置项、参数表、环境变量**：原文未涉及（文档为架构 overview，不含具体的启动命令、yaml/ini 配置项或环境变量清单），故标注「原文未涉及」。

## 图文联合解读

- `architecture_overview.png`: **图文联合解读：**

图示采用分层架构，自顶向下分为三层：上层为外部生态（Modelers、ModelZoo、vllm-omni、diffusers、cache-dit）；中层为 MindIE SD 核心模块，包含 cache、quantization、parallelism、benchmark 四块并列组件，以及由 attn/moe/quant 构成的 layer 模块、kernel、compilation 和 example（service、MMInfer）；底层依次为 PyTorch 与 CANN 算能底座。

该图论证了三个技术结论：①各加速模块（cache/quantization/parallelism）独立解耦、可单独或叠加使用；②layer 模块封装了 attn、moe、quant 等核心算子，对外提供统一调用入口；③MindIE SD 基于 PyTorch 接口遵从 diffusers 规范，并下接 CANN 昇腾算力底座实现亲和加速。

与文档论点呼应：图示将文档中"模块独立解耦、配合 diffusers、基于 PyTorch 调用昇腾亲和算子"的核心架构思想可视化，并通过 diffusers/cache-dit 标注证明其与社区方案可叠加互通。
