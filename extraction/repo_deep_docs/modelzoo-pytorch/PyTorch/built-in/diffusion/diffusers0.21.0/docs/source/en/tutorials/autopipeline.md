# AutoPipeline

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/diffusion/diffusers0.21.0/docs/source/en/tutorials/autopipeline.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/diffusion/diffusers0.21.0/docs/source/en/tutorials/autopipeline.md

# 《AutoPipeline》文档深度解读

## 【定位】

这篇文档解决的是 🤗 Diffusers 库中**任务入口碎片化**的问题——同一预训练权重可同时用于 text-to-image、image-to-image、inpainting 等多种任务,但用户往往不知道该用哪个具体 Pipeline 类。文档介绍了一种**"任务优先 (task-first)"的通用入口** `AutoPipeline`,让用户只关心"想做什么任务",由库自动从 `model_index.json` 中推断出正确的具体 Pipeline 子类。

---

## 【技术要点】

1. **三种任务入口类**:`AutoPipelineForText2Image`、`AutoPipelineForImage2Image`、`AutoPipelineForInpainting`,分别对应 text-to-image、image-to-image、inpainting 三类下游任务(原文:"Currently, it supports text-to-image, image-to-image, and inpainting.")。

2. **自动检测机制**:底层从 checkpoint 的 [`model_index.json`](https://huggingface.co/runwayml/stable-diffusion-v1-5/blob/main/model_index.json) 中识别 `"stable-diffusion"` class 字段,再映射到对应的具体 Pipeline 类(原文 `StableDiffusionPipeline` / `StableDiffusionImg2ImgPipeline` / `StableDiffusionInpaintPipeline`,原文写作 `StableDiffusionPipline`,保留拼写)。

3. **典型加载参数**:代码中反复出现的固定配置组合为 `torch_dtype=torch.float16, use_safetensors=True`,并通过 `.to("cuda")` 放置到 GPU。

4. **关键超参示例**(原文出现的具体数值):
   - text2img:`num_inference_steps=25`
   - img2img:`num_inference_steps=200, strength=0.75, guidance_scale=10.5`
   - inpainting(基于 SDXL):`num_inference_steps=50, strength=0.80`
   - 从 pipe 复用后覆盖 strength:`strength=0.3`

5. **复用加载 `from_pipe`**:用 `AutoPipelineForImage2Image.from_pipe(pipeline_text2img)` 从已有 Pipeline 派生新 Pipeline,**不重新加载权重**以节省显存;原 Pipeline 的可选项(如 `requires_safety_checker=False`)会自动传递给新 Pipeline,也可在 `from_pipe` 时覆盖(如 `requires_safety_checker=True, strength=0.3`)。

6. **不支持时报错**:对 `openai/shap-e-img2img` 等不支持的 checkpoint 抛出 `ValueError: AutoPipeline can't find a pipeline linked to ShapEImg2ImgPipeline for None`。

---

## 【关键机制与数据】

**工作原理(原文有):**

- **`AutoPipeline` 是一层薄包装**:本身不重新实现扩散过程,而是按"任务类型 → 识别 model_index 中的 class 字符串 → 实例化对应 Concrete Pipeline"的两步策略工作。
  - 原文(Under the hood):`AutoPipelineForText2Image` ① detects `"stable-diffusion"` class from `model_index.json`; ② loads the corresponding text-to-image `StableDiffusionPipline` (原文拼写)。
  - 同样地,`AutoPipelineForImage2Image` 与 `AutoPipelineForInpainting` 沿用同一机制。

- **`from_pipe` 工作原理(原文有):**"detects the original pipeline class and maps it to the new pipeline class corresponding to the task you want to do"。例如 `StableDiffusionPipeline` 被映射到 `StableDiffusionImg2ImgPipeline`,组件权重不复制,因此 "at no additional memory cost"。

**性能/数据流事实(原文有):**

- 加载文本示例图像:`requests.get(url)` 下载后用 `Image.open(BytesIO(...)).convert("RGB")`,再 `image.thumbnail((768, 768))` 控制输入尺寸。
- inpainting 示例从 GitHub raw 链接同时下载 `init_image` 与 `mask_image`,经 `load_image(...).convert("RGB")` 后送入管线。
- 显式内存收益声明:"reuse the same components from a checkpoint instead of reloading them which would unnecessarily consume additional memory"。

> 说明:原文未给出具体的显存/时延数字,以上为定性叙述。

---

## 【表格解读】

**原文无表格**(整篇文档只包含 Tip 提示框、代码块与文字段落,未出现 markdown 表格或参数表)。

---

## 【公式解读】

**原文无公式**(未涉及任何 LaTeX 数学表达式或伪代码公式;仅有常规 Python 调用代码)。

---

## 【关联】

- **同类教程分支(章节内部关系)**:
  - `Choose an AutoPipeline for your task`:三种任务的独立加载路径(text2img / img2img / inpainting)。
  - `Use multiple pipelines`:在前节基础上引入 `from_pipe` 做权重复用。
  - 错误处理段(`openai/shap-e-img2img`)展示不支持时的兜底行为,与官方"Currently, it supports text-to-image, image-to-image, and inpainting"的能力边界呼应。

- **上下游模块(原文链接)**:
  - **[`./pipelines/auto_pipeline`](./pipelines/auto_pipeline)**:文档末尾 Tip 中给出的 AutoPipeline API 参考页,用于查阅每个任务具体支持的 Pipeline 列表与详细参数。
  - **`model_index.json`**(`runwayml/stable-diffusion-v1-5/blob/main/model_index.json`):AutoPipeline 进行 class 推断的事实依据,决定了能否自动路由。
  - **被自动化的具体 Pipeline**(同仓 `pipelines/stable_diffusion/*`):`StableDiffusionPipeline`、`StableDiffusionImg2ImgPipeline`、`StableDiffusionInpaintPipeline` 是 AutoPipeline 的最终映射目标。
  - **关联任务类**:`AutoPipelineForText2Image` / `AutoPipelineForImage2Image` / `AutoPipelineForInpainting` 三者形成并列任务族,通过相同的 `from_pretrained` 入口和 `from_pipe` 桥接。
  - **上游预训练权重**:示例中用到的 [`runwayml/stable-diffusion-v1-5`](https://huggingface.co/runwayml/stable-diffusion-v1-5) 与 [`stabilityai/stable-diffusion-xl-base-1.0`](https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0) 提供"一权多用"前提,从而使 AutoPipeline 的多任务复用价值成立。

---

## 【使用方法】

### 1. 选任务并加载(原文示例代码,逐字保留)

**Text-to-Image(原文):**
```py
from diffusers import AutoPipelineForText2Image
import torch

pipeline = AutoPipelineForText2Image.from_pretrained(
    "runwayml/stable-diffusion-v1-5", torch_dtype=torch.float16, use_safetensors=True
).to("cuda")
prompt = "peasant and dragon combat, wood cutting style, viking era, bevel with rune"

image = pipeline(prompt, num_inference_steps=25).images[0]
```

**Image-to-Image(原文):**
```py
from diffusers import AutoPipelineForImage2Image

pipeline = AutoPipelineForImage2Image.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=torch.float16,
    use_safetensors=True,
).to("cuda")
prompt = "a portrait of a dog wearing a pearl earring"

url = "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0f/1665_Girl_with_a_Pearl_Earring.jpg/800px-1665_Girl_with_a_Pearl_Earring.jpg"

response = requests.get(url)
image = Image.open(BytesIO(response.content)).convert("RGB")
image.thumbnail((768, 768))

image = pipeline(prompt, image, num_inference_steps=200, strength=0.75, guidance_scale=10.5).images[0]
```

**Inpainting(原文):**
```py
from diffusers import AutoPipelineForInpainting
from diffusers.utils import load_image

pipeline = AutoPipelineForInpainting.from_pretrained(
    "stabilityai/stable-diffusion-xl-base-1.0", torch_dtype=torch.float16, use_safetensors=True
).to("cuda")

img_url = "https://raw.githubusercontent.com/CompVis/latent-diffusion/main/data/inpainting_examples/overture-creations-5sI6fQgYIuo.png"
mask_url = "https://raw.githubusercontent.com/CompVis/latent-diffusion/main/data/inpainting_examples/overture-creations-5sI6fQgYIuo_mask.png"

init_image = load_image(img_url).convert("RGB")
mask_image = load_image(mask_url).convert("RGB")

prompt = "A majestic tiger sitting on a bench"
image = pipeline(prompt, image=init_image, mask_image=mask_image, num_inference_steps=50, strength=0.80).images[0]
```

### 2. 多 Pipeline 复用(原文)

基础派生(原文):
```py
from diffusers import AutoPipelineForText2Image, AutoPipelineForImage2Image

pipeline_text2img = AutoPipelineForText2Image.from_pretrained(
    "runwayml/stable-diffusion-v1-5", torch_dtype=torch.float16, use_safetensors=True
)
print(type(pipeline_text2img))
# <class 'diffusers.pipelines.stable_diffusion.pipeline_stable_diffusion.StableDiffusionPipeline'>

pipeline_img2img = AutoPipelineForImage2Image.from_pipe(pipeline_text2img)
print(type(pipeline_img2img))
# <class 'diffusers.pipelines.stable_diffusion.pipeline_stable_diffusion_img2img.StableDiffusionImg2ImgPipeline'>
```

传递原 Pipeline 选项(原文):
```py
pipeline_text2img = AutoPipelineForText2Image.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=torch.float16,
    use_safetensors=True,
    requires_safety_checker=False,
).to("cuda")

pipeline_img2img = AutoPipelineForImage2Image.from_pipe(pipeline_text2img)
print(pipe.config.requires_safety_checker)  # 原文输出: "False"
```

覆盖选项(原文):
```py
pipeline_img2img = AutoPipelineForImage2Image.from_pipe(pipeline_text2img, requires_safety_checker=True, strength=0.3)
```

### 3. 常见配置项(原文出现过的可枚举项)

| 配置项 | 原文出现位置 | 作用/含义(原文语义) |
|---|---|---|
| `torch_dtype=torch.float16` | 所有 `from_pretrained` 调用 | 半精度加载以节省显存 |
| `use_safetensors=True` | 所有 `from_pretrained` 调用 | 启用 safetensors 格式加载 |
| `.to("cuda")` | 所有示例 | 将 Pipeline 放置到 GPU |
| `requires_safety_checker=False/True` | `from_pretrained` 与 `from_pipe` | 控制 NSFW 安全检查器开关 |
| `num_inference_steps` | text2img=25、img2img=200、inpaint=50 | 扩散去噪步数 |
| `strength` | img2img=0.75、inpaint=0.80、`from_pipe` 覆盖=0.3 | 加噪强度 / 图生图变化幅度 |
| `guidance_scale` | img2img=10.5 | Classifier-free guidance 强度 |
| `prompt` | 全部三任务示例 | 文本条件 |
| `image` / `mask_image` | img2img、inpaint 示例 | 初始图像 / 掩码(均为 `RGB`) |

> 备注:除 `requires_safety_checker` 外,其它参数(如 `strength`、`guidance_scale`)是各任务原 Pipeline 的原生参数,AutoPipeline 只是把它们透传给被路由到的具体 Pipeline;`from_pipe` 时可再次覆盖。

### 4. 启用方式总结(原文语义)

- **入口启用**:只需 `from diffusers import AutoPipelineFor{Text2Image|Image2Image|Inpainting}` 即可使用,**无需**手动选 Stable Diffusion / SDXL 等模型族——由 checkpoint 的 `model_index.json` 自动决定。
- **不支持的 checkpoint**:会抛 `ValueError`,提示 "AutoPipeline can't find a pipeline linked to <X>Pipeline for None",此时应回退到手动 `from_pretrained` 对应 Pipeline 类(原文未涉及具体回退写法)。
