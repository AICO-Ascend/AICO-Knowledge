# 模型/框架支持介绍

> 仓 `mindie-sd` · 路径 `docs/zh/features/supported_matrix.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-sd/docs/zh/features/supported_matrix.md

# 「mindie-sd」supported_matrix.md 一体化深度解读

## 【定位】

本文档是 MindIE SD（昇腾亲和的多模态加速套件）的**模型与框架支持能力矩阵**，用于回答"该套件已适配哪些模型、在哪些推理框架下、运行在哪些 Atlas 硬件上、各框架叠加了哪些加速特性（Cache / 并行 / 稀疏FA / 量化 / 融合算子）"——本质是一份"型号×框架×硬件×特性"的兼容性快照，定位偏运维/集成参考。

---

## 【技术要点】

1. **三大框架并列**：MindIE SD 同时接入 **vLLM Omni**、**Cache DiT + diffusers**、**魔乐社区（modelers.cn）** 三个下游推理/分发入口，并声明"理论上支持任何多模态模型的推理加速"。
2. **五维加速特性（feature overlay）**：每一格用 ✅/✖️ 标注的加速项为——**Cache（缓存复用）、并行（并行策略）、稀疏FA（稀疏 FlashAttention）、量化、融合算子**；这套维度是衡量适配成熟度的核心 KPI。
3. **三类 Atlas 硬件**：分别为 **Atlas 800I A2 服务器**（算力 313T、内存 64 GB）、**Atlas 800I A3 超节点服务器**、**Atlas 300I DUO 推理卡**（算力 280T、内存 48 GB）；不同模型在不同硬件上的能力集不一致。
4. **模型族覆盖**：横跨 SD 全系（1.5 / 2.1 / XL / XL_inpainting / XL_lighting / XL_controlnet / XL_prompt_weight / SD3）、视频扩散（SVD / HunyuanVideo / HunyuanVideo-1.5 / OpenSora v1.2 / OpenSoraPlan v1.2 & v1.3 / Wan2.1 & Wan2.2 / CogVideoX-2B/5B）、3D（Hunyuan3D-2.1）、音频（Stable Audio Open v1.0）、国产文生图（CogView3-Plus-3B / HunyuanDit / FLUX.1-dev / FLUX.2-dev / Qwen-Image 系列 / Z-Image / Z-Image-Turbo）。
5. **特性命中差异**：vLLM Omni 仅命中 5 个模型、Cache DiT + diffusers 仅命中 2 个模型，魔乐社区则覆盖全部 29 个模型——魔乐社区是覆盖面最广的入口。
6. **个别条目标注 "功能打通"**：SDXL 的四个变体（inpainting / lighting / controlnet / prompt_weight）在并行列打 ✖️ 但保留 Cache+融合算子，表示仅完成通路打通、未做完整性能优化。

---

## 【关键机制与数据】

- **硬件规格（原文 NOTE 字段）**：
  - Atlas 800I A2 服务器：默认算力 **313T**、内存 **64 GB**。
  - Atlas 300I DUO 推理卡：默认算力 **280T**、内存 **48 GB**。
- **机制描述**：文档未给出具体工作原理/数据流/吞吐数字（如 tokens/s、时延、首帧延迟等），仅以 ✅/✖️ 枚举特性是否叠加。所有定量数字均仅出现在硬件算力与内存条目上。
- **数据流/性能数据**：原文未涉及——文档定位为"能力矩阵"而非基准报告。

---

## 【表格解读】

### 表 1 · 模型支持情况（粗选框架）

| 模型 | vLLM Omni | Cache DiT + diffusers | 魔乐社区 |
|:---:|:---:|:---:|:---:|
| Stable Diffusion 1.5 | ✖️ | ✖️ | ✅️ |
| Stable Diffusion 2.1 | ✖️ | ✖️ | ✅️ |
| Stable Diffusion XL | ✖️ | ✖️ | ✅️ |
| Stable Diffusion XL_inpainting | ✖️ | ✖️ | ✅️ |
| Stable Diffusion XL_lighting | ✖️ | ✖️ | ✅️ |
| Stable Diffusion XL_controlnet | ✖️ | ✖️ | ✅️ |
| Stable Diffusion XL_prompt_weight | ✖️ | ✖️ | ✅️ |
| Stable Diffusion 3 | ✖️ | ✖️ | ✅️ |
| Stable Video Diffusion | ✖️ | ✖️ | ✅️ |
| Stable Audio Open v1.0 | ✖️ | ✖️ | ✅️ |
| OpenSora v1.2 | ✖️ | ✖️ | ✅️ |
| OpenSoraPlan v1.2 | ✖️ | ✖️ | ✅️ |
| OpenSoraPlan v1.3 | ✖️ | ✖️ | ✅️ |
| CogView3-Plus-3B | ✖️ | ✖️ | ✅️ |
| CogVideoX-2B | ✖️ | ✖️ | ✅️ |
| CogVideoX-5B | ✖️ | ✖️ | ✅️ |
| HunyuanDit | ✖️ | ✖️ | ✅️ |
| HunyuanVideo | ✖️ | ✖️ | ✅️ |
| HunyuanVideo-1.5 | ✖️ | ✖️ | ✅️ |
| Hunyuan3D-2.1 | ✖️ | ✖️ | ✅️ |
| Wan2.1 | ✖️ | ✖️ | ✅️ |
| Wan2.2 | ✖️ | ✖️ | ✅️ |
| FLUX.1-dev | ✅️ | ✅️ | ✅️ |
| FLUX.2-dev | ✖️ | ✅️ | ✅️ |
| Qwen-Image | ✅️ | ✖️ | ✅️ |
| Qwen-Image-Edit | ✅️ | ✖️ | ✅️ |
| Qwen-Image-Edit-2509 | ✅️ | ✖️ | ✅️ |
| Z-Image | ✖️ | ✖️ | ✅️ |
| Z-Image-Turbo | ✅️ | ✖️ | ✅️ |

**逐行解读**：这张是粗粒度"哪个模型进了哪个框架"的入口表。**FLUX.1-dev** 是唯一在三框架下都打 ✅ 的模型，意味着它是 MindIE SD 当前最受验证的旗舰路径；**Qwen-Image / Qwen-Image-Edit / Qwen-Image-Edit-2509** 与 **Z-Image-Turbo** 仅 vLLM Omni 通道开启；**FLUX.2-dev** 仅 Cache DiT 通道开启；其余 23 个模型（SD 全系、SVD、SD3、Hunyuan 系列、OpenSora 全系、CogView3、CogVideoX、Wan2.1/2.2、Hunyuan3D-2.1、Z-Image、Stable Audio）仅在魔乐社区通道可用——三框架的"覆盖宽度"排序为：魔乐社区 > vLLM Omni > Cache DiT + diffusers。

---

### 表 2 · vLLM Omni 特性 & 模型性能

| 模型 | 硬件 | Cache | 并行 | 稀疏FA | 量化 | 融合算子 |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| FLUX.1-dev | Atlas 800I A2 服务器 | ✅️ | ✅️ | ✖️ | ✅️ | ✅️ |
| Qwen-Image | Atlas 800I A2 服务器 | ✅️ | ✅️ | ✖️ | ✖️ | ✅️ |
| Qwen-Image-Edit | Atlas 800I A2 服务器 | ✅️ | ✅️ | ✖️ | ✖️ | ✅️ |
| Qwen-Image-Edit-2509 | Atlas 800I A2 服务器 | ✅️ | ✅️ | ✖️ | ✖️ | ✅️ |
| Z-Image-Turbo | Atlas 800I A2 服务器 | ✅️ | ✖️ | ✖️ | ✖️ | ✅️ |

> 原文 NOTE：Atlas 800I A2 服务器默认使用算力 313T，内存 64 GB。

**逐行解读**：vLLM Omni 通道只覆盖 **5 个模型**，且**硬件全部是 Atlas 800I A2 服务器**（未上 A3 超节点，也未下沉到 300I DUO 卡）。**FLUX.1-dev** 是唯一同时具备"Cache + 并行 + 量化 + 融合算子"四件套的模型（缺稀疏FA）；**Qwen-Image 三件套**（Image / Image-Edit / Image-Edit-2509）特征一致——Cache+并行+融合算子，但**未叠加量化、稀疏FA**；**Z-Image-Turbo** 缺并行能力（其他三特性保留）。整体规律：vLLM Omni 通道默认启用 Cache 与融合算子作为"基线"，并行是常见叠加项，量化与稀疏FA 是有条件叠加。

---

### 表 3 · Cache DiT + diffusers 特性 & 模型性能

| 模型 | 硬件 | Cache | 并行 | 稀疏FA | 量化 | 融合算子 |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| FLUX.1-dev | Atlas 800I A2 服务器 | ✅️ | ✅️ | ✖️ | ✅️ | ✅️ |
| FLUX.2-dev | Atlas 800I A2 服务器 | ✖️ | ✅️ | ✖️ | ✖️ | ✅️ |

**逐行解读**：Cache DiT + diffusers 通道**只覆盖 FLUX 系列两个模型**，且同样限定在 Atlas 800I A2。**FLUX.1-dev** 与表 2 完全一致（Cache+并行+量化+融合算子，缺稀疏FA），意味着同一硬件下两个框架对其能力打平；**FLUX.2-dev** 在此通道中**未启用 Cache、未启用量化**，只打通并行+融合算子——暗示 Cache DiT 对 2-dev 的缓存复用适配尚不成熟。

---

### 表 4 · 魔乐社区的特性叠加 & 模型性能

| 模型 | 硬件 | Cache | 并行 | 稀疏FA | 量化 | 融合算子 | 说明 |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Stable Diffusion 1.5 | Atlas 800I A2 服务器 / Atlas 300I DUO 推理卡 | ✅️ | ✅️ | ✖️ | ✖️ | ✅️ | 无 |
| Stable Diffusion 2.1 | Atlas 800I A2 服务器 / Atlas 300I DUO 推理卡 | ✅️ | ✅️ | ✖️ | ✖️ | ✅️ | 无 |
| Stable Diffusion XL | Atlas 800I A2 / A3 超节点 / 300I DUO | ✅️ | ✅️ | ✖️ | ✖️ | ✅️ | 无 |
| Stable Diffusion XL_inpainting | Atlas 800I A2 / A3 超节点 | ✅️ | ✖️ | ✖️ | ✖️ | ✅️ | 功能打通 |
| Stable Diffusion XL_lighting | Atlas 800I A2 / A3 超节点 | ✅️ | ✖️ | ✖️ | ✖️ | ✅️ | 功能打通 |
| Stable Diffusion XL_controlnet | Atlas 800I A2 / A3 超节点 | ✅️ | ✖️ | ✖️ | ✖️ | ✅️ | 功能打通 |
| Stable Diffusion XL_prompt_weight | Atlas 800I A2 / A3 超节点 | ✅️ | ✖️ | ✖️ | ✖️ | ✅️ | 功能打通 |
| Stable Diffusion 3 | Atlas 800I A2 / 300I DUO | ✅️ | ✅️ | ✖️ | ✖️ | ✅️ | 无 |
| Stable Video Diffusion | Atlas 800I A2 服务器 | ✅️ | ✅️ | ✖️ | ✖️ | ✅️ | 无 |
| Stable Audio Open v1.0 | Atlas 800I A2 / 300I DUO | ✅️ | ✖️ | ✖️ | ✖️ | ✅️ | 无 |
| OpenSora v1.2 | Atlas 800I A2 / A3 超节点 | ✅️ | ✅️ | ✖️ | ✖️ | ✅️ | 无 |
| OpenSoraPlan v1.2 | Atlas 800I A2 / A3 超节点 | ✅️ | ✅️ | ✖️ | ✖️ | ✅️ | 无 |
| OpenSoraPlan v1.3 | Atlas 800I A2 服务器 | ✅️ | ✅️ | ✖️ | ✖️ | ✅️ | 无 |
| CogView3-Plus-3B | Atlas 800I A2 / A3 超节点 | ✅️ | ✅️ | ✖️ | ✖️ | ✅️ | 无 |
| CogVideoX-2B | Atlas 800I A2 / A3 超节点 | ✅️ | ✅️ | ✖️ | ✖️ | ✅️ | 无 |
| CogVideoX-5B | Atlas 800I A2 / A3 超节点 | ✅️ | ✅️ | ✖️ | ✖️ | ✅️ | 无 |
| FLUX.1-dev | Atlas 800I A2 / A3 超节点 | ✅️ | ✅️ | ✖️ | ✅️ | ✅️ | 无 |
| FLUX.2-dev | Atlas 800I A2 / A3 超节点 | ✅️ | ✅️ | ✖️ | ✅️ | ✅️ | 无 |
| HunyuanDit | Atlas 800I A2 / A3 超节点 | ✅️ | ✖️ | ✖️ | ✖️ | ✅️ | 无 |
| HunyuanVideo | Atlas 800I A2 / A3 超节点 | ✅️ | ✅️ | ✖️ | ✅️ | ✅️ | 无 |
| HunyuanVideo-1.5 | Atlas 800I A2 / A3 超节点 | ✅️ | ✅️ | ✅️ | ✅️ | ✅️ | 无 |
| Hunyuan3D-2.1 | Atlas 800I A2 / A3 超节点 | ✅️ | ✅️ | ✖️ | ✅️ | ✅️ | 无 |
| Wan2.1 | Atlas 800I A2 / A3 超节点 | ✅️ | ✅️ | ✅️ | ✅️ | ✅️ | 无 |
| Wan2.2 | Atlas 800I A2 / A3 超节点 | ✅️ | ✅️ | ✅️ | ✅️ | ✅️ | 无 |
| Qwen-Image | Atlas 800I A2 / A3 超节点 | ✅️ | ✅️ | ✖️ | ✅️ | ✅️ | 无 |
| Qwen-Image-Edit | Atlas 800I A2 / A3 超节点 | ✅️ | ✅️ | ✖️ | ✅️ | ✅️ | 无 |
| Qwen-Image-Edit-2509 | Atlas 800I A2 / A3 超节点 | ✅️ | ✅️ | ✖️ | ✅️ | ✅️ | 无 |
| Z-Image | Atlas 800I A2 / A3 超节点 | ✖️ | ✖️ | ✖️ | ✖️ | ✖️ | 无 |
| Z-Image-Turbo | Atlas 800I A2 / A3 超节点 | ✖️ | ✖️ | ✖️ | ✖️ | ✅️ | 无 |

> 原文 NOTE：Atlas 300I DUO 推理卡默认使用算力 280T、内存 48 GB；Atlas 800I A2 服务器默认使用算力 313T（原文末被截断）。

**逐行解读**（按特性分层）：
- **"Cache + 融合算子"基线几乎全量命中**：除 Z-Image、Z-Image-Turbo 外全部 ✅，说明魔乐社区通道默认开启缓存复用与算子融合。
- **并行能力差异**：SD1.5/2.1/XL/SD3/SVD/OpenSora 全系/OpenSoraPlan/Cog 系列/FLUX.1&2/HunyuanVideo & 1.5/Hunyuan3D-2.1/Wan2.1&2.2/Qwen-Image 三件套 全部 ✅；**SDXL 四个变体（inpainting/lighting/controlnet/prompt_weight）、Stable Audio Open、HunyuanDit、Z-Image、Z-Image-Turbo** 不支持并行——大多说明列标"功能打通"或仅在 A2 单机运行。
- **量化能力**：仅 **FLUX.1&2-dev、HunyuanVideo & 1.5、Hunyuan3D-2.1、Wan2.1&2.2、Qwen-Image 三件套** 启用；其余 SD 经典模型、Cog 系列、SD3、OpenSora、HunyuanDit 等尚未叠加量化。
- **稀疏FA**：仅 **HunyuanVideo-1.5、Wan2.1、Wan2.2** 三项 ✅——这是当前文档中"特性全满格"的三个模型（Cache+并行+稀疏FA+量化+融合算子全 ✅）。
- **硬件覆盖差异**：能下沉到 Atlas 300I DUO 推理卡（边缘/小卡场景）的仅 SD1.5/2.1/XL/SD3/Stable Audio Open——其余模型要么 A2、要么 A2+A3 双栈。说明 DUO 卡的适配偏保守，主要服务 SD 系经典模型。
- **"功能打通"标签**：SDXL 四个变体的说明列打上"功能打通"，与它们"无并行"的能力现状对应——属于"通路已联调、并行未优化"的中间状态。
- **零特性命中**：**Z-Image** 在魔乐社区通道下所有五项特性全 ✖️，等同于"仅占位"，尚未实际叠加任何加速；Z-Image-Turbo 仅命中融合算子一项。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **三大下游框架**：vLLM Omni、Cache DiT + diffusers、魔乐社区（modelers.cn）——文档以"模型支持矩阵"作为这三个框架入口能力的横截面对照。
- **硬件依赖**：与昇腾 Atlas 产品线强耦合——**Atlas 800I A2 服务器**（主力）、**Atlas 800I A3 超节点服务器**（大规模场景）、**Atlas 300I DUO 推理卡**（轻量/边缘场景）。同一模型在不同硬件上的特性命中表不同。
- **模型仓库来源**：魔乐社区通道中的多数模型链接指向 `https://modelers.cn/models/MindIE/...`；SDXL 的四个变体（inpainting/controlnet/prompt_weight）指向 Gitee `ascend/ModelZoo-PyTorch` 仓库的 MindIE-Torch 路径——与仓库内其他文档（如安装/部署/快速上手）共用同一模型来源。
- **同名模型跨表对比**：**FLUX.1-dev** 同时出现在表 2（vLLM Omni）、表 3（Cache DiT）、表 4（魔乐社区），可作为"三框架能力对齐"的参考基准；**Qwen-Image / Qwen-Image-Edit / Qwen-Image-Edit-2509** 出现在表 2 与表 4，对比可见 vLLM Omni 通道尚未给 Qwen 系列叠加量化、而魔乐社区已叠加。
- **文档自身声明**："理论上，MindIE SD 支持任何多模态模型的推理加速，此处仅列出了我们支持的典型模型的特性叠加情况"——意味着此表是一份"快照"而非穷举，且新模型理论上都可挂载。
- 内部链接：原文未提供任何内部链接（`(无)`）。

---

## 【使用方法】

原文未涉及——本文档**没有给出任何具体的启动命令、配置项或 API 开关**；它仅以 ✅/✖️ 枚举"哪些模型在哪些框架下、在哪些硬件上已经叠加了哪些特性"，作为兼容性/能力参考。具体如何启用 Cache、并行、稀疏FA、量化、融合算子，以及如何调用 vLLM Omni / Cache DiT + diffusers / 魔乐社区三个框架，需查阅同仓其他文档（如部署指南、特性说明）。
