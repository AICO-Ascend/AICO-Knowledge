# 커스텀 파이프라인 불러오기

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/diffusion/diffusers0.25.0/docs/source/ko/using-diffusers/custom_pipeline_overview.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/diffusion/diffusers0.25.0/docs/source/ko/using-diffusers/custom_pipeline_overview.md

# 一体化深度解读:커스텀 파이프라인 불러오기

---

## 【定位】

本篇文档介绍 **diffusers 库中"社区/自定义 DiffusionPipeline"的加载机制**,说明如何从 Hugging Face Hub 调用非官方实现(community pipeline)、如何替换/注入自定义组件(如 `clip_model`、`feature_extractor`),以及加载外部代码时需要承担的安全审查责任。

---

## 【技术要点】

1. **社区管道定义**:Community pipeline 指任何与论文原始实现不同的 `DiffusionPipeline` 子类,典型如 `StableDiffusionControlNetPipeline`(对应 ControlNet 论文 arXiv:2302.05543),用于扩展功能。
2. **加载入口函数**:`DiffusionPipeline.from_pretrained()`,通过传入两个参数——**模型仓库 ID**(权重/组件来源)和 **`custom_pipeline` 参数**(管道代码来源)——从 Hub 同时拉取代码与权重。
3. **加载参数示例(原文)**:
   - 模型:`"google/ddpm-cifar10-32"`
   - 管道:`"hf-internal-testing/diffusers-dummy-pipeline"`(dummy 管道用于演示)
4. **官方社区管道加载**:除模型仓库外,`custom_pipeline` 可使用短名称(如 `"clip_guided_stable_diffusion"`),并允许通过 `from_pretrained(...)` 的关键字参数直接注入组件对象。
5. **可注入组件类型**(原文示例):
   - `feature_extractor` → 通过 `CLIPImageProcessor.from_pretrained(clip_model_id)` 实例化
   - `clip_model` → 通过 `CLIPModel.from_pretrained(clip_model_id)` 实例化
   - 示例 CLIP 模型仓库:`"laion/CLIP-ViT-B-32-laion2B-s34B-b79K"`
6. **安全警告**(原文 Tip):加载社区代码等同于信任该作者的代码,需在线上先审查其安全性,因 `from_pretrained` 会自动下载并执行 Python 代码。

---

## 【关键机制与数据】

**工作原理(原文):**

- **双仓库加载机制**:当 `custom_pipeline` 给出的是 GitHub 仓库 ID 时(例:`"hf-internal-testing/diffusers-dummy-pipeline"`),`from_pretrained` 会拉取该仓库的管道代码;同时仍需提供一个含权重的模型仓库 ID(如 `"google/ddpm-cifar10-32"`),以完成权重与默认组件的加载。
- **组件覆盖机制**:在加载官方社区管道时(例:`"clip_guided_stable_diffusion"`),用户可在 `from_pretrained` 调用处通过同名关键字参数直接传入已实例化的组件对象,管道实例化时将使用这些外部对象覆盖默认配置。原文示例中 `clip_model` 与 `feature_extractor` 即以此方式注入。
- **命名空间区分**:
  - 长字符串形式(例:`"hf-internal-testing/diffusers-dummy-pipeline"`)→ 指向 Hub 仓库
  - 短字符串形式(例:`"clip_guided_stable_diffusion"`)→ 指向 diffusers 官方 `examples/community` 目录中已收录的管道

**性能数据**:原文未涉及。

---

## 【表格解读】

**原文无表格**。文中所有信息以代码块、Tip 提示和正文段落形式呈现,未出现任何参数表、性能对比表或配置项表。

---

## 【公式解读】

**原文无公式**。文中未包含任何 LaTeX 公式或伪代码形式的算法表达式。

---

## 【关联】

文档内嵌及文末出现的内部/外部链接,以及与上下游特性的关系:

1. **`StableDiffusionControlNetPipeline`** — 文档开篇将其作为"社区管道"概念的首要示例,虽 ControlNet 已并入主分支,但原文将其归类为与原始论文实现不同的扩散管道变体。
2. **[Speech to Image](https://github.com/huggingface/diffusers/tree/main/examples/community#speech-to-image)** — 文档列举的社区管道示例之一,展示社区生态的多样性(文本/语音 → 图像)。
3. **[Composable Stable Diffusion](https://github.com/huggingface/diffusers/tree/main/examples/community#composable-stable-diffusion)** — 另一类社区管道示例,体现对原 Stable Diffusion 推理组合能力的扩展。
4. **[官方社区管道索引](https://github.com/huggingface/diffusers/tree/main/examples/community)** — 收录所有官方维护的社区管道,`custom_pipeline` 的短名称从此处解析。
5. **[CLIP Guided Stable Diffusion](https://github.com/huggingface/diffusers/tree/main/examples/community#clip-guided-stable-diffusion)** — 文档第二个代码示例使用的具体社区管道,依赖外部 CLIP 模型与处理器(通过 `transformers` 库加载)。
6. **[커뮤니티 파이프라인 가이드(custom_pipeline_examples)](https://github.com/huggingface/diffusers/blob/main/docs/source/en/using-diffusers/custom_pipeline_examples)** — 文末指向的扩展阅读,介绍更多社区管道用法。
7. **[커뮤니티 파이프라인에 기여하는 방법(contribute_pipeline)](https://github.com/huggingface/diffusers/blob/main/docs/source/en/using-diffusers/contribute_pipeline)** — 文末指向的贡献指南,说明向 diffusers 提交新社区管道的流程。
8. **与 `transformers` 库的边界**:文档示例中 `CLIPImageProcessor` 与 `CLIPModel` 均通过 `from transformers import ...` 加载,表明社区管道常与 `transformers` 生态联合使用,管线之外的模型/处理器由调用方自行准备。

---

## 【使用方法】

**启用方式(原文代码块摘录):**

**方式一:从 Hub 加载任意仓库的社区管道 + 指定权重仓库**

```py
from diffusers import DiffusionPipeline

pipeline = DiffusionPipeline.from_pretrained(
    "google/ddpm-cifar10-32", custom_pipeline="hf-internal-testing/diffusers-dummy-pipeline"
)
```

**方式二:加载官方社区管道 + 注入自定义组件**

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

**配置项说明(原文):**

| 参数 | 取值示例(原文) | 作用 |
|---|---|---|
| 第 1 位置参数(模型仓库 ID) | `"google/ddpm-cifar10-32"` / `"runwayml/stable-diffusion-v1-5"` | 指定从中加载权重与默认组件的模型仓库 |
| `custom_pipeline` | `"hf-internal-testing/diffusers-dummy-pipeline"`(Hub 仓库 ID) / `"clip_guided_stable_diffusion"`(官方短名) | 指定要加载的管道代码来源 |
| `clip_model` | `CLIPModel.from_pretrained(...)` 实例 | 覆盖管道默认的 CLIP 文本/图像编码模型 |
| `feature_extractor` | `CLIPImageProcessor.from_pretrained(...)` 实例 | 覆盖管道默认的图像预处理器 |

**安全审查建议(原文):** 加载前需在线审查 Hub 仓库中的管道代码;`from_pretrained` 会自动下载并执行其中的 Python 文件,等同于将代码信任权授予仓库作者。
