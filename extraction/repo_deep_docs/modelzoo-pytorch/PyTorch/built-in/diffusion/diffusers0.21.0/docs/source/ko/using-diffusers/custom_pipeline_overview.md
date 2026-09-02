# 커스텀 파이프라인 불러오기

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/diffusion/diffusers0.21.0/docs/source/ko/using-diffusers/custom_pipeline_overview.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/diffusion/diffusers0.21.0/docs/source/ko/using-diffusers/custom_pipeline_overview.md

# 一体化深度解读：커스텀 파이프라인 불러오기（加载自定义 Pipeline）

---

## 【定位】

这篇文档解决的是 **在 🤗 Diffusers 中如何从 Hugging Face Hub 加载「社区（community）自定义 Pipeline」** 的问题——即当用户需要使用那些与论文原始实现不同的、非官方的 [`DiffusionPipeline`] 子类（如 ControlNet、CLIP Guided、Speech-to-Image 等）时，应当如何通过 `custom_pipeline` 参数将自定义实现与官方模型权重进行组合加载。

---

## 【技术要点】

1. **社区 Pipeline 的定义边界**：原文明确指出，社区 Pipeline 是指所有「与论文原始实现方式不同的 [`DiffusionPipeline`] 类」，例如 [`StableDiffusionControlNetPipeline`] 对应论文 *"Text-to-Image Generation with ControlNet Conditioning"* (arXiv:2302.05543)，它们提供额外功能或对原始实现进行扩展。

2. **`from_pretrained` + `custom_pipeline` 双仓库加载机制**：加载社区 Pipeline 需要同时提供 **两个** 仓库 ID——一个是社区 Pipeline 实现的仓库 ID（如 `hf-internal-testing/diffusers-dummy-pipeline`），另一个是承载模型权重与组件的官方仓库 ID（如 `google/ddpm-cifar10-32`），二者通过 `DiffusionPipeline.from_pretrained(...)` 组合传入。

3. **官方社区 Pipeline 的「组件覆盖」能力**：对于官方维护的社区 Pipeline，可以从官方仓库加载权重，同时在调用 `from_pretrained` 时 **直接通过关键字参数注入特定子组件**（例如 `clip_model=clip_model`、`feature_extractor=feature_extractor`），不必全部依赖默认下载的组件。

4. **🔒 安全警告（代码即信任）**：原文以 `<Tip warning={true}>` 形式强调，从 Hub 加载社区 Pipeline 等同于 **自动执行第三方 Python 代码**，因此必须在加载前在线验证代码可信度。

5. **典型组合示例（CLIP Guided Stable Diffusion）**：使用 `runwayml/stable-diffusion-v1-5` 作为基础模型仓库、`custom_pipeline="clip_guided_stable_diffusion"` 指定社区 Pipeline 实现，并以 `laion/CLIP-ViT-B-32-laion2B-s34B-b79K` 为来源预先实例化 `CLIPImageProcessor` 与 `CLIPModel` 两个组件，再注入到 Pipeline 中。

6. **完整索引与扩展入口**：所有官方社区 Pipeline 在 `examples/community` 目录下集中维护，并提供两类延伸指南——「社区 Pipeline 示例」与「社区 Pipeline 贡献指南」。

---

## 【关键机制与数据】

**工作原理（数据流）**：

- `DiffusionPipeline.from_pretrained(<model_repo>, custom_pipeline=<pipeline_repo>)` 的内部行为可以拆分为两条独立的数据通路：
  - **通路 A（模型权重）**：从 `model_repo`（如 `google/ddpm-cifar10-32`、`runwayml/stable-diffusion-v1-5`）下载并初始化 UNet、VAE、text encoder、scheduler 等核心组件的权重。
  - **通路 B（Pipeline 实现）**：从 `pipeline_repo`（如 `hf-internal-testing/diffusers-dummy-pipeline`，或官方社区管线 `clip_guided_stable_diffusion`）拉取 Python 源码，并将其作为 Pipeline 类加载，从而覆盖默认实现。
- 当用户额外传入组件关键字参数（如 `clip_model`、`feature_extractor`）时，这些 **用户传入的实例会覆盖从仓库自动加载的同名组件**，完成第三层级的「组件级覆盖」。

**性能/数据信息**：原文未涉及任何性能指标、参数量、推理时间等定量数据；所有出现的内容均为仓库 ID、类名、论文标题与论文链接。

---

## 【表格解读】

**原文无表格。** 全文未出现任何参数表、性能对比表或配置项表格，所有信息以叙述、`<Tip>` 提示框与代码块的形式呈现。

---

## 【公式解读】

**原文无公式。** 全文未出现任何 LaTeX 公式、伪代码公式或数学表达式，所有机制均通过自然语言 + Python 代码示例说明。

---

## 【关联】

由于本文为「概览（overview）」性质的文档，且原文未提供内部链接（`内部链接: (无)`），其关联关系完全以 **外部 GitHub URL** 的形式体现，与下列上下游资源相互引用：

- **社区 Pipeline 索引上游**：指向 `https://github.com/huggingface/diffusers/tree/main/examples/community`——这是所有官方社区 Pipeline 的总目录，本文以 [Speech to Image] 与 [Composable Stable Diffusion] 为代表案例引用之。
- **详细示例下游**：`커뮤니티 파이프라인 가이드 (custom_pipeline_examples)`——本文指向 `docs/source/en/using-diffusers/custom_pipeline_examples`，是本文的「细读篇」。
- **贡献入口下游**：`커뮤니티 파이프라인에 기여하는 방법 (contribute_pipeline)`——本文指向 `docs/source/en/using-diffusers/contribute_pipeline`，面向希望注册自定义实现的开发者。
- **与 ControlNet 实现的横向关联**：原文将 [`StableDiffusionControlNetPipeline`] 列为「社区 Pipeline」的语义示例，说明自定义 Pipeline 范畴 **既包含社区贡献，也涵盖官方对原始论文的二次封装**。
- **与 CLIP Guided Stable Diffusion 的横向关联**：作为「官方社区 Pipeline + 组件覆盖」的典型示例，与 ControlNet 示例共同覆盖了「从外部仓库加载实现」与「直接覆盖组件」两种加载模式。

---

## 【使用方法】

原文给出 **两种启用方式**，均基于 `DiffusionPipeline.from_pretrained`：

**方式一：从外部仓库加载「非官方实现」**

```py
from diffusers import DiffusionPipeline

pipeline = DiffusionPipeline.from_pretrained(
    "google/ddpm-cifar10-32", custom_pipeline="hf-internal-testing/diffusers-dummy-pipeline"
)
```
- 关键参数：`custom_pipeline` 接收 **社区仓库 ID**，对应非官方 Pipeline 源码。

**方式二：加载「官方社区 Pipeline」并手动覆盖子组件**

```py
from diffusers import DiffusionPipeline
from transformers import CLIPImageProcessor, CLIPModel

clip_model_id = "laion/CLIP-ViT-B-32-laion2B-s34B-b79K"

feature_extractor = CLIPImageProcessor.from_pretrained(clip_model_id)
clip_model = CLIPModel.from_pretrained(clip_model_id)

pipeline = DiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    custom_pipeline="clip_guided_stable_diffusion",
    clip_model=clip_model,
    feature_extractor=feature_extractor,
)
```
- 关键参数：
  - 第一个位置参数：官方模型权重仓库 ID（`runwayml/stable-diffusion-v1-5`）；
  - `custom_pipeline`：官方社区 Pipeline 短名（`"clip_guided_stable_diffusion"`）；
  - `clip_model` / `feature_extractor`：用户预先实例化的同名组件实例，用于覆盖默认组件。

**配置项 / 命令清单**：原文未涉及环境变量、CLI 命令、调度器（scheduler）切换、精度配置等额外配置项，相关主题属于本文指向的「详细示例指南」范畴。
