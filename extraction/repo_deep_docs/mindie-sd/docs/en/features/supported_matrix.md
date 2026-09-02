# Model/Framework Support Matrix

> 仓 `mindie-sd` · 路径 `docs/en/features/supported_matrix.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-sd/docs/en/features/supported_matrix.md

# 一体化深度解读：Model/Framework Support Matrix

## 【定位】

本文档是 MindIE SD（昇腾亲和的多模态加速系列套件）的**特性支持矩阵**，系统化罗列了 vLLM Omni、Cache DiT + diffusers、Modelers 社区三大框架下所支持的典型多模态模型，以及每个模型在 Atlas 系列硬件（Atlas 800I A2 Server / Atlas 800I A3 Supernode Server / Atlas 300I DUO Inference Card）上所"叠加"启用的加速特性（Cache / Parallelism / Sparse FA / Quantization / Fused Ops），为开发者**一眼判断某个模型在哪种硬件、哪条框架路径下具备哪些推理加速能力**提供权威依据。

---

## 【技术要点】

1. **三大框架分层支持模型**：vLLM Omni、Cache DiT + diffusers、Modelers 社区三者并行存在；多数模型仅在 Modelers 社区栈支持（28 个模型中仅 5 个进入 vLLM Omni 路径、2 个进入 Cache DiT+diffusers 路径），体现**新框架覆盖度仍在扩张中**。
2. **六类加速特性维度**：每个具体表格均以 "Cache / Parallelism / Sparse FA / Quantization / Fused Ops" 作为能力列，加上 Hardware 列，构成**6×N 的特性-模型堆叠矩阵**。
3. **三类昇腾硬件规格锚点**：
   - Atlas 300I DUO 推理卡：280T 算力 / 48 GB 显存
   - Atlas 800I A2 Server：313T 算力 / 64 GB 显存
   - Atlas 800I A3 超节点 Server：560T 算力 / 64 GB 显存
4. **旗舰模型特性全开**：FLUX.1-dev 在 vLLM Omni 与 Modelers 两条路径下均开启 Cache+Parallelism+Quantization+Fused Ops 四项（vLLM Omni 下 Sparse FA 标 No）；HunyuanVideo-1.5、Wan2.1、Wan2.2 在 Modelers 栈下**实现五项全开**（含 Sparse FA = Yes），代表最高特性覆盖水平。
5. **量化能力集中点**：Quantization=Yes 仅出现在 FLUX.1-dev / FLUX.2-dev（双框架）+ HunyuanVideo-1.5 / HunyuanVideo / Hunyuan3D-2.1 / Wan2.1 / Wan2.2 / Qwen-Image 系列 / FLUX.1-dev（Modelers 路径）等少数模型中，**是当前最具差异化的加速能力**。
6. **"特性叠加"而非孤立开关**：原文明确将能力列称为 "feature stacking"，意味着这些加速特性**可组合叠加**而非互斥，但实际能否同时启用仍取决于模型-硬件-框架的三元匹配。

---

## 【关键机制与数据】

### 工作原理（基于原文表述）

- **总原则**（原文："In theory, MindIE SD supports inference acceleration for any multimodal model."）：理论上 MindIE SD 可对任意多模态模型进行推理加速，但**实际路径取决于框架适配情况**——这是文档将模型×框架二维分类的根本原因。
- **特性叠加的判读顺序**（原文："This page only lists the feature stacking status for our supported typical models."）：表格只展示"已验证可叠加"的组合，未列出的组合**不等于不支持**，而是未被官方列举/验证。
- **硬件差异化的策略含义**（原文 Note）：A3 超节点（560T）相对 A2（313T）算力约提升 78.6%，主要承担 HunyuanVideo-1.5/Wan2.1/Wan2.2/FLUX/SDXL 等大参数量模型的五项全特性栈；A2 Server 承担绝大多数模型的混合栈；Atlas 300I DUO（280T/48GB，PCIE 形态）仅在 SD1.5/2.1/XL/SD3/Stable Audio Open v1.0 等轻量级模型上提供 Cache+Parallelism+Fused Ops 三件套（无 Quantization、无 Sparse FA）。

### 性能数据

原文**未给出**任何量化性能数据（如吞吐、延迟、加速比），仅给出硬件默认算力规格。所有 "Yes/No" 是**特性可用性**而非**性能数字**。

---

## 【表格解读】

### 表格 1：Model Support（模型-框架三维总览）

| Model | vLLM Omni | Cache DiT + diffusers | Modelers |
|:----------:|:---------:|:---------------------:|:------:|
| Stable Diffusion 1.5 | No | No | Yes |
| Stable Diffusion 2.1 | No | No | Yes |
| Stable Diffusion XL | No | No | Yes |
| Stable Diffusion XL_inpainting | No | No | Yes |
| Stable Diffusion XL_lighting | No | No | Yes |
| Stable Diffusion XL_controlnet | No | No | Yes |
| Stable Diffusion XL_prompt_weight | No | No | Yes |
| Stable Diffusion 3 | No | No | Yes |
| Stable Video Diffusion | No | No | Yes |
| Stable Audio Open v1.0 | No | No | Yes |
| OpenSora v1.2 | No | No | Yes |
| OpenSoraPlan v1.2 | No | No | Yes |
| OpenSoraPlan v1.3 | No | No | Yes |
| CogView3-Plus-3B | No | No | Yes |
| CogVideoX-2B | No | No | Yes |
| CogVideoX-5B | No | No | Yes |
| HunyuanDit | No | No | Yes |
| HunyuanVideo | No | No | Yes |
| HunyuanVideo-1.5 | No | No | Yes |
| Hunyuan3D-2.1 | No | No | Yes |
| Wan2.1 | No | No | Yes |
| Wan2.2 | No | No | Yes |
| FLUX.1-dev | Yes | Yes | Yes |
| FLUX.2-dev | No | Yes | Yes |
| Qwen-Image | Yes | No | Yes |
| Qwen-Image-Edit | Yes | No | Yes |
| Qwen-Image-Edit-2509 | Yes | No | Yes |
| Z-Image | No | No | Yes |
| Z-Image-Turbo | Yes | No | Yes |

**逐行解读：**

- **SDXL 及其衍生（XL_inpainting / _lighting / _controlnet / _prompt_weight）**：四条同族变体均**仅 Modelers 支持**，新框架未覆盖，体现 SDXL 生态在 MindIE SD 中属于"老一代稳定栈"。
- **OpenSora / CogVideoX / HunyuanVideo / Wan / Stable Video Diffusion / Hunyuan3D 等视频/3D 模态**：清一色 **Modelers 独享**，说明视频/3D 多模态当前主要依赖 Modelers 社区路径而非新框架。
- **FLUX.1-dev 是首个也是唯一一个三框架通吃模型**（vLLM Omni=Yes, Cache DiT+diffusers=Yes, Modelers=Yes），是当前框架适配最成熟的标杆。
- **FLUX.2-dev**：vLLM Omni=No，但 Cache DiT+diffusers=Yes、Modelers=Yes，说明 vLLM Omni 尚未跟进 FLUX.2。
- **Qwen-Image / Qwen-Image-Edit / Qwen-Image-Edit-2509**：三者在 vLLM Omni 与 Modelers 下均 Yes，但 Cache DiT+diffusers=No，**未启用 DiT 缓存**。
- **Z-Image 仅 Modelers 支持**；**Z-Image-Turbo 在 vLLM Omni 与 Modelers 下 Yes**——可见 Turbo 变体被新框架优先接纳。

### 表格 2：vLLM Omni Features and Model Performance

| Model | Hardware | Cache | Parallelism | Sparse FA | Quantization | Fused Ops |
|:----------:|:----:|:-------:|:--:|:----:|:--:|:---------:|
| FLUX.1-dev | Atlas 800I A2 Server | Yes | Yes | No | Yes | Yes |
| Qwen-Image | Atlas 800I A2 Server | Yes | Yes | No | No | Yes |
| Qwen-Image-Edit | Atlas 800I A2 Server | Yes | Yes | No | No | Yes |
| Qwen-Image-Edit-2509 | Atlas 800I A2 Server | Yes | Yes | No | No | Yes |
| Z-Image-Turbo | Atlas 800I A2 Server | Yes | No | No | No | Yes |

**逐行解读：**

- **FLUX.1-dev** 是该框架内唯一**四项全开**（Cache+Parallelism+Quantization+Fused Ops）的模型，仅 Sparse FA=No，是该框架的最强特性组合。
- **Qwen-Image / Edit / Edit-2509** 三者配置完全一致（Cache+Parallelism+Fused Ops 三件套，**未启用 Quantization 与 Sparse FA**），显示 Qwen-Image 系列在该路径下处于"中等成熟度"。
- **Z-Image-Turbo** 仅启用了 Cache+Fused Ops 两项，Parallelism=No、Quantization=No、Sparse FA=No，是该框架下**最轻量配置**，反映 Turbo 变体更看重单卡低延迟而非并行扩展。

### 表格 3：Cache DiT + diffusers Features and Model Performance

| Model | Hardware | Cache | Parallelism | Sparse FA | Quantization | Fused Ops |
|:----------:|:----:|:-------:|:--:|:----:|:--:|:---------:|
| FLUX.1-dev | Atlas 800I A2 Server | Yes | Yes | No | Yes | Yes |
| FLUX.2-dev | Atlas 800I A2 Server | No | Yes | No | No | Yes |

**逐行解读：**

- 仅两个模型进入该框架验证。**FLUX.1-dev** 与 vLLM Omni 路径下的特性组合**完全一致**（Cache+Parallelism+Quantization+Fused Ops 四项，Sparse FA=No），暗示两条新路径在 FLUX.1-dev 上**特性对齐**。
- **FLUX.2-dev 在该框架下 Cache=No**，意味着虽然 FLUX.2 已纳入 Cache DiT+diffusers 框架，但**未叠加 DiT 缓存机制**；与 FLUX.1-dev 唯一差异即在此处。

### 表格 4：Modelers Community Feature Stacking and Model Performance

| Model | Hardware | Cache | Parallelism | Sparse FA | Quantization | Fused Ops | Notes |
|:----------:|:----:|:-------:|:--:|:----:|:--:|:---------:|:--:|
| Stable Diffusion 1.5 | Atlas 800I A2 Server / Atlas 300I DUO Inference Card | Yes | Yes | No | No | Yes | N/A |
| Stable Diffusion 2.1 | Atlas 800I A2 Server / Atlas 300I DUO Inference Card | Yes | Yes | No | No | Yes | N/A |
| Stable Diffusion XL | Atlas 800I A2 Server / Atlas 800I A3 Supernode Server / Atlas 300I DUO Inference Card | Yes | Yes | No | No | Yes | N/A |
| Stable Diffusion XL_inpainting | Atlas 800I A2 Server / Atlas 800I A3 Supernode Server | Yes | No | No | No | Yes | Feature enabled |
| Stable Diffusion XL_lighting | Atlas 800I A2 Server / Atlas 800I A3 Supernode Server | Yes | No | No | No | Yes | Feature enabled |
| Stable Diffusion XL_controlnet | Atlas 800I A2 Server / Atlas 800I A3 Supernode Server | Yes | No | No | No | Yes | Feature enabled |
| Stable Diffusion XL_prompt_weight | Atlas 800I A2 Server / Atlas 800I A3 Supernode Server | Yes | No | No | No | Yes | Feature enabled |
| Stable Diffusion 3 | Atlas 800I A2 Server / Atlas 300I DUO Inference Card | Yes | Yes | No | No | Yes | N/A |
| Stable Video Diffusion | Atlas 800I A2 Server | Yes | Yes | No | No | Yes | N/A |
| Stable Audio Open v1.0 | Atlas 800I A2 Server / Atlas 300I DUO Inference Card | Yes | No | No | No | Yes | N/A |
| OpenSora v1.2 | Atlas 800I A2 Server / Atlas 800I A3 Supernode Server | Yes | Yes | No | No | Yes | N/A |
| OpenSoraPlan v1.2 | Atlas 800I A2 Server / Atlas 800I A3 Supernode Server | Yes | Yes | No | No | Yes | N/A |
| OpenSoraPlan v1.3 | Atlas 800I A2 Server | Yes | Yes | No | No | Yes | N/A |
| CogView3-Plus-3B | Atlas 800I A2 Server / Atlas 800I A3 Supernode Server | Yes | Yes | No | No | Yes | N/A |
| CogVideoX-2B | Atlas 800I A2 Server / Atlas 800I A3 Supernode Server | Yes | Yes | No | No | Yes | N/A |
| CogVideoX-5B | Atlas 800I A2 Server / Atlas 800I A3 Supernode Server | Yes | Yes | No | No | Yes | N/A |
| FLUX.1-dev | Atlas 800I A2 Server / Atlas 800I A3 Supernode Server | Yes | Yes | No | Yes | Yes | N/A |
| FLUX.2-dev | Atlas 800I A2 Server / Atlas 800I A3 Supernode Server | Yes | Yes | No | Yes | Yes | N/A |
| HunyuanDit | Atlas 800I A2 Server / Atlas 800I A3 Supernode Server | Yes | No | No | No | Yes | N/A |
| HunyuanVideo | Atlas 800I A2 Server / Atlas 800I A3 Supernode Server | Yes | Yes | No | Yes | Yes | N/A |
| HunyuanVideo-1.5 | Atlas 800I A2 Server / Atlas 800I A3 Supernode Server | Yes | Yes | Yes | Yes | Yes | N/A |
| Hunyuan3D-2.1 | Atlas 800I A2 Server / Atlas 800I A3 Supernode Server | Yes | Yes | No | Yes | Yes | N/A |
| Wan2.1 | Atlas 800I A2 Server / Atlas 800I A3 Supernode Server | Yes | Yes | Yes | Yes | Yes | N/A |
| Wan2.2 | Atlas 800I A2 Server / Atlas 800I A3 Supernode Server | Yes | Yes | Yes | Yes | Yes | N/A |
| Qwen-Image | Atlas 800I A2 Server / Atlas 800I A3 Supernode Server | Yes | Yes | No | Yes | Yes | N/A |
| Qwen-Image-Edit | Atlas 800I A2 Server / Atlas 800I A3 Supernode Server | Yes | Yes | No | Yes | Yes | N/A |
| Qwen-Image-Edit-2509 | Atlas 800I A2 Server / Atlas 800I A3 Supernode Server | Yes | Yes | No | Yes | Yes | N/A |
| Z-Image | Atlas 800I A2 Server / Atlas 800I A3 Supernode Server | No | No | No | No | No | N/A |
| Z-Image-Turbo | Atlas 800I A2 Server / Atlas 800I A3 Supernode Server | No | No | No | No | Yes | N/A |

**逐行解读（按特性覆盖层级分类）：**

- **唯一"五项全开"模型**（Cache+Parallelism+Sparse FA+Quantization+Fused Ops 全部 Yes）：**HunyuanVideo-1.5、Wan2.1、Wan2.2** 三者，代表 MindIE SD 在 Modelers 路径下的**最高特性成熟度**，且均同时支持 A2+A3 双硬件。
- **四项全开（不含 Sparse FA）**：**FLUX.1-dev、FLUX.2-dev、HunyuanVideo、Hunyuan3D-2.1、Qwen-Image、Qwen-Image-Edit、Qwen-Image-Edit-2509**——这是"次旗舰"组合，是当前 Modelers 栈下量化能力的主要承载。
- **三项组合（Cache+Parallelism+Fused Ops）**：SDXL、SD3、Stable Video Diffusion、OpenSora v1.2、OpenSoraPlan v1.2/v1.3、CogView3-Plus-3B、CogVideoX-2B/5B——经典 Stable Diffusion / OpenSora / CogVideoX 系列，未启用 Quantization 与 Sparse FA。
- **两项组合（Cache+Fused Ops，不含 Parallelism）**：SDXL_inpainting、SDXL_lighting、SDXL_controlnet、SDXL_prompt_weight（HunyuanDit 同此）——四类 SDXL 衍生模型与 HunyuanDit 都标 "Feature enabled"，表示这些**专用变体采用定向功能扩展而非通用并行**。
- **仅两项（Cache+Fused Ops，无 Parallelism）+ 仅 A2+DUO** ：SD1.5、SD2.1、Stable Audio Open v1.0 三款轻量级或边缘模型，**唯一支持 Atlas 300I DUO 的非 SDXL 模型**。
- **SDXL 是唯一同时跑在 A2+A3+300I DUO 三类硬件上的模型**，体现其作为旗舰底座的兼容广度。
- **Z-Image** 全部为 No（连 Cache 与 Fused Ops 都未开启），是表中**唯一一项零特性**模型。
- **Z-Image-Turbo** 仅 Fused Ops=Yes，其余 No——与表格 2 中 vLLM Omni 路径下的 Z-Image-Turbo 配置形成**跨框架对比**：同一模型在 Modelers 下仅启用 Fused Ops、在 vLLM Omni 下启用 Cache+Fused Ops，差异仅在 Cache 这一项。
- **Notes 列**：仅 SDXL 四个 _* 变体标 "Feature enabled" 而非 "N/A"，其余模型均为 N/A——表示这四个变体有特定功能注释需要查阅。

### 附：硬件规格 Note（原文逐字）

> Atlas 300I DUO inference cards default to 280T compute and 48 GB memory.
> Atlas 800I A2 servers default to 313T compute and 64 GB memory.
> Atlas 800I A3 supernode servers default to 560T compute and 64 GB memory.

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **三大框架横向关系**：
  - **vLLM Omni** 与 **Cache DiT + diffusers** 是 MindIE SD 新近集成的两大加速框架（仓库描述提到 "现已支持 vLLM Omni，Diffusers+CacheDit，lightx2v 等框架"），本文档是它们的**能力对账单**。
  - **Modelers 社区**（modelers.cn）是 ModelZoo 性质的开源模型仓库，承担最广泛模型的传统加速栈，与 vLLM Omni / Cache DiT 形成"广度 vs 新特性深度"的互补关系。
- **模型-仓库映射**：表格 4 中每个模型均带超链接，绝大多数指向 `https://modelers.cn/models/MindIE/...`，少数四个 SDXL 变体（_inpainting / _lighting / _controlnet / _prompt_weight）指向 `https://gitee.com/ascend/ModelZoo-PyTorch/tree/master/MindIE/MindIE-Torch/built-in/foundation/...`，说明**这两条 SDXL 变体仍走 Gitee ModelZoo 路径而非常规 modelers.cn 路径**。
- **硬件-特性关联**：A3 超节点仅出现在 HunyuanVideo-1.5、Wan2.x、FLUX、Sparse FA 等高特性组合中；A2 Server 覆盖最广；300I DUO 仅出现在 SD1.5/2.1/XL/SD3/Stable Audio Open v1.0 等轻量级模型，体现**硬件算力（280T/313T/560T）与特性栈深度正相关**的隐含设计。
- **本文档在仓库中的位置**：作为 `docs/en/features/supported_matrix.md`，属于 features 索引下的"特性支持矩阵"，与具体框架的 usage / install / migration 文档构成"能力清单 + 启用手册"的搭配关系（仓库内其他文档未在本页直接引用）。

---

## 【使用方法】

**原文未涉及**具体的启用命令、配置项或 API 调用方式。本文档为**纯支持矩阵/能力清单**，仅给出三类硬件的默认算力与显存规格作为参考锚点，未列出 model-config、CLI flag、环境变量或 SDK 接口。
