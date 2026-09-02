# MoE

> 仓 `mindie-llm` · 路径 `docs/zh/user_guide/feature/moe.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-llm/docs/zh/user_guide/feature/moe.md

# MoE 文档深度解读

## 【定位】

本文档系统阐述了昇腾自研大模型推理引擎（mindie-llm）对 Mixture of Experts（MoE）架构模型的**支持范围、能力矩阵及推理执行方法**，帮助用户快速确认目标 MoE 模型是否在引擎受支持的能力集合内，以及如何以与传统 LLM 一致的方式执行推理。

---

## 【技术要点】

1. **MoE 架构的两大核心创新**：① 用 **Sparse MoE layer** 替换传统 Transformer 中的 **Feed Forward Network（FFN）**，每个 FFN 充当一个专家；② 引入 **Router（路由机制）**，在每一层决定每个 token 实际激活进入哪一个（或哪些）专家，而非所有专家全部激活。

2. **稀疏激活的取舍**：MoE 借助广阔的专家知识保证模型效果，但相对同等参数量的传统模型，**每个 token 仅需激活部分专家**，因此推理性能更优——这是 MoE 兼顾效果与效率的核心来源。

3. **典型支持模型清单**：包括 Mixtral 8\*7B、Mixtral 8\*22B、DeepSeek-16B-MoE、DeepSeek-V2、DeepSeek-V3、DeepSeek-R1、Qwen3-30B-A3B、Qwen3-235B-A22B 等共 8 个模型（原文表格内覆盖）。

4. **支持的并行方式分两类**：① 仅支持 **TP（Tensor Parallel，张量并行）**：Mixtral 8\*7B、Mixtral 8\*22B、DeepSeek-16B-MoE、Qwen3-30B-A3B；② 支持 **TP 与 EP（Expert Parallel，专家并行）**：DeepSeek-V2、DeepSeek-V3、DeepSeek-R1；Qwen3-235B-A22B 仅 TP。

5. **量化与数据格式差异**：Mixtral 系列与 DeepSeek-16B-MoE 采用 **FP16**，DeepSeek 系列（V2/V3/R1）与 Qwen3 系列使用 **BF16**；Mixtral 系列与 DeepSeek-16B-MoE **暂不支持量化**，DeepSeek-V2/V3/R1 与 Qwen3-30B-A3B/Qwen3-235B-A22B **支持量化**。

6. **推理执行无需额外配置**：MoE 类模型执行推理的方式与其他模型一致，使用方式可参考传统 LLM，仅需以对应模型的启动脚本执行即可（如 `run_pa_deepseek_moe.sh`）。

---

## 【关键机制与数据】

- **工作原理（原文）**：每一个 FFN 可扮演一个专家角色，针对每一个 token 的推理，仅需激活其中部分专家即可；Router 决定了 token 在每一层会进入到哪一个专家。基于"稀疏专家层 + 路由机制"二者结合，MoE 兼顾效果与推理性能。

- **数据流（原文）**：token → 经每层的 Router 路由 → 选择性进入被激活的 FFN 专家 → 输出结果。每个 token 在每一层只走少数专家路径，而非全量专家。

- **性能特征（原文定性描述）**：相较于同等参数量的传统模型，由于仅激活部分专家，推理性能更优；模型效果依赖于广阔的专家知识面。原文未给出具体吞吐量、时延或加速比的数字。

- **能力分布观察**：在 8 个支持模型中，**FP16 占比 3/8（Mixtral 系列与 DeepSeek-16B-MoE）**，**BF16 占比 5/8**；**多机多卡推理仅 DeepSeek-V2、V3、R1 与 Qwen3-235B-A22B 共 4/8 支持**，其余 4 个仅支持单机多卡场景（"不支持"）。

---

## 【表格解读】

### 表 1：能力支持特征矩阵（原文逐字还原）

| 已支持模型 | 数据格式 | 量化 | 并行方式 | 硬件平台 | 多机多卡推理 |
|---|---|---|---|---|---|
| Mixtral 8*7B | FP16 | 暂不支持 | TP | Atlas 800I A2 推理服务器 | 不支持 |
| Mixtral 8*22B | FP16 | 暂不支持 | TP | Atlas 800I A2 推理服务器 | 不支持 |
| DeepSeek-16B-MoE | FP16 | 暂不支持 | TP | Atlas 800I A2 推理服务器 | 不支持 |
| DeepSeek-V2 | BF16 | 支持 | TP、EP | Atlas 800I A2 推理服务器 | 支持 |
| DeepSeek-V3 | BF16 | 支持 | TP、EP | Atlas 800I A2 推理服务器 | 支持 |
| DeepSeek-R1 | BF16 | 支持 | TP、EP | Atlas 800I A2 推理服务器 | 支持 |
| Qwen3-30B-A3B | BF16 | 支持 | TP | Atlas 800I A2 推理服务器 | 不支持 |
| Qwen3-235B-A22B | BF16 | 支持 | TP | Atlas 800I A2 推理服务器 | 支持 |

**逐行解读**：

- **Mixtral 8\*7B**：FP16 精度、暂不支持量化、仅 TP 并行、不支持多机多卡——属于能力最受限的早期支持档位。
- **Mixtral 8\*22B**：与 8\*7B 配置完全一致——同为 Mixtral 系列沿用同一能力档位（FP16 + 仅 TP + 不支持多机）。
- **DeepSeek-16B-MoE**：与 Mixtral 系列同档位（FP16 + 仅 TP + 不支持多机）——属于 DeepSeek 系列较早引入的模型。
- **DeepSeek-V2**：升级到 BF16、支持量化、支持 **TP 与 EP**、并**支持多机多卡**——属于能力完整的标杆档位。
- **DeepSeek-V3**：与 V2 完全一致——继承 V2 的全能力配置。
- **DeepSeek-R1**：与 V2/V3 完全一致——作为 R1 推理模型同样具备完整能力。
- **Qwen3-30B-A3B**：BF16 + 支持量化 + 仅 TP（无 EP） + **不支持多机多卡**——Qwen3 系列中受限于规模的轻量档位。
- **Qwen3-235B-A22B**：BF16 + 支持量化 + 仅 TP + **支持多机多卡**——Qwen3 系列中具备跨机推理能力的高配档位。

**横向规律**：① 硬件平台**统一为 Atlas 800I A2 推理服务器**；② FP16 系列均"暂不支持量化、仅 TP、不支持多机"；③ BF16 系列普遍"支持量化"；④ "TP + EP + 多机多卡"三件套仅在 DeepSeek-V2/V3/R1 三款上同时具备，是当前能力天花板。

---

## 【公式解读】

原文无公式。

---

## 【关联】

原文未涉及与其他特性/模块/上下游的内部链接关联（"内部链接: 无"）。从文档内容可观察到的隐含关联如下：

- **与"并行方式（TP / EP）"特性相关**：MoE 的专家并行（EP）是文档中明确点出的能力项，DeepSeek-V2/V3/R1 依赖 EP 才能扩展到多机多卡推理。
- **与"量化"特性相关**：表格中"支持量化"一栏直接关联到引擎的量化能力模块，Mixtral 系列与 DeepSeek-16B-MoE 暂不支持量化是其能力缺口。
- **与"传统 LLM 推理流程"上下游相关**：执行推理一节明确指出 MoE 模型"执行推理的方式与其他模型一致"，与传统 LLM 共享同一推理路径（启动脚本、对话测试方式等）。
- **与"硬件平台 Atlas 800I A2 推理服务器"绑定**：所有受支持模型均运行于该硬件平台之上，是能力矩阵的统一底座。

---

## 【使用方法】

### 启动脚本（原文命令）

以 DeepSeek-16B-MoE 为例，执行对话测试（推理内容为 "What's deep learning"）：

```bash
cd ${ATB_SPEED_HOME_PATH}
bash examples/models/deepseek/run_pa_deepseek_moe.sh {模型权重路径}
```

- **环境变量**：`${ATB_SPEED_HOME_PATH}`——需替换为实际 ATB Speed 部署根目录。
- **占位参数**：`{模型权重路径}`——需替换为具体的模型权重目录路径。
- **执行动作**：进入 ATB Speed 主目录后，通过 deepseek 系列 moe 专用脚本启动推理。

### 关键配置项（原文说明）

- **模型固有参数**：配置请参考官方权重文件中的 `config.json` 文件（原文："模型固有参数配置请参考官方权重文件中的config.json文件"），未在文档中列出具体配置项。
- **无需额外配置**：MoE 类模型执行推理的方式与其他模型一致，无需做额外配置修改（原文："MoE类模型执行推理的方式与其他模型一致，在执行推理时您可参考传统LLM的使用方式，无需做额外配置修改"）。
- **能力档位（按表 1 选择）**：根据目标模型所在的行，可知其允许的数据格式、是否可量化、可用的并行方式与是否支持多机多卡——若超出该档位能力，则当前引擎不可用。
