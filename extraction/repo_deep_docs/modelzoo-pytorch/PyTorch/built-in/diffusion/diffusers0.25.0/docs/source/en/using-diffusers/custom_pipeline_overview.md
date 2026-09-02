# Load community pipelines and components

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/diffusion/diffusers0.25.0/docs/source/en/using-diffusers/custom_pipeline_overview.md` · 类型 overview · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/diffusion/diffusers0.25.0/docs/source/en/using-diffusers/custom_pipeline_overview.md

# 一体化深度解读:custom_pipeline_overview.md

## 【定位】

这篇文档是 Diffusers 库的「社区生态总览」,系统介绍如何加载与构建两类非官方扩展:**Community Pipelines**(社区流水线)与 **Community Components**(社区组件),解决当用户需要使用或发布原始论文实现之外的扩散模型流水线时,如何从 Hub 安全加载、组合自定义模块并分享给社区的完整工作流问题。

---

## 【技术要点】

1. **Community Pipelines 定义**:任何与原论文实现不同的 `DiffusionPipeline` 子类(如 `StableDiffusionControlNetPipeline` 对应 ControlNet 论文 arXiv:2302.05543),官方社区流水线列表位于 `examples/community` 目录。
2. **加载任意社区流水线**:通过 `DiffusionPipeline.from_pretrained()` 传入 `custom_pipeline` 参数指定仓库 id,并通过另一参数加载权重/组件;示例:`custom_pipeline="hf-internal-testing/diffusers-dummy-pipeline"` + `"google/ddpm-cifar10-32"`。
3. **混合加载权重与组件**:除 `custom_pipeline` 外,可将外部组件(如 `CLIPModel`、`CLIPImageProcessor`)直接传给 `from_pretrained`,示例使用 `laion/CLIP-ViT-B-32-laion2B-b79K` 配合 `runwayml/stable-diffusion-v1-5`。
4. **安全警告**:Hub 加载第三方代码时须在线审核,需用户自行承担信任风险。
5. **Community Components 五步构建法**(以 `showlab/show-1-base` 为例):
   - 文本编码器:T5Tokenizer + T5EncoderModel(subfolder="tokenizer"/"text_encoder")
   - 调度器:DPMSolverMultistepScheduler(subfolder="scheduler")
   - 图像处理器:CLIPFeatureExtractor(subfolder="feature_extractor")
   - **自定义 UNet**:必须重命名(如 `UNet3DConditionModel` → `ShowOneUNet3DConditionModel`)以避免与 Diffusers 内置类名冲突,放在 `showone_unet_3d_condition.py` 脚本中
   - **自定义流水线**:自定义类如 `TextToVideoIFPipeline`,放在 `pipeline_t2v_base_pixel.py` 脚本中
6. **Hub 发布三步后续工作**:
   - 修改 `model_index.json` 中的 `_class_name` 字段为 `"pipeline_t2v_base_pixel"` 与 `"TextToVideoIFPipeline"`
   - 上传 `showone_unet_3d_condition.py` 到 unet 目录
   - 上传 `pipeline_t2v_base_pixel.py` 到流水线根目录
7. **运行推理关键参数**:必须加 `trust_remote_code=True`;示例生成参数 `num_frames=8`、`height=40`、`width=64`、`num_inference_steps=2`、`guidance_scale=9.0`、`output_type="pt"`,视频帧尺寸 **8×64×40,2fps**;`torch_dtype=torch.float16`。

---

## 【关键机制与数据】

**工作原理与数据流(原文梳理)**:

- **流水线加载机制**:`DiffusionPipeline.from_pretrained()` 通过 `custom_pipeline` 参数从 Hub 仓库下载 Python 脚本并动态加载类,同时从另一仓库加载预训练权重;`use_safetensors=True` 启用 safetensors 安全格式加载。
- **组件替换机制**:当流水线类已存在于 Diffusers 中时,自定义类必须改名(如 `UNet3DConditionModel` → `ShowOneUNet3DConditionModel`),否则会冲突;组件代码通过 subfolder 参数从指定子目录加载。
- **Hub 共享机制**:自定义流水线通过 `pipeline.push_to_hub("custom-t2v-pipeline")` 上传,需配合 `_class_name` 配置让 Diffusers 能正确路由到自定义 Python 文件。
- **trust_remote_code 机制**:在推理时 `trust_remote_code=True` 使 Diffusers 自动处理自定义脚本的下载与导入(原文称之"handle all the 'magic' behind the scenes")。

**原文性能/规模数据**:
- 文本编码器模型:laion/CLIP-ViT-B-32-laion2B-s34B-b79K
- 基础 SD 模型:runwayml/stable-diffusion-v1-5
- DDPM 基准:google/ddpm-cifar10-32
- 视频生成 demo 输出:8 帧、64×40 分辨率、2 fps、2 步推理、guidance_scale=9.0、torch.float16、`device="cuda"`

---

## 【表格解读】

**原文无表格**(本文档全部以代码块、Tip 警告框与文字描述形式呈现,未出现 markdown 表格或键值对照表)。

---

## 【公式解读】

**原文无公式**(文档为工程实践型指南,未出现任何数学公式、LaTeX 表达式或伪代码公式)。

---

## 【关联】

文末提到的内部链接映射了文档的上下游关系:

- **`custom_pipeline_examples`(Community pipelines 指南)**:本 overview 文档的"用例延伸",详细展示各类社区流水线(如 Speech-to-Image、Composable Stable Diffusion、CLIP Guided Stable Diffusion)的具体使用方式与示例代码。本文档给出"如何加载"的入口,而 `custom_pipeline_examples` 负责"如何用"。
- **`contribute_pipeline`(How to contribute a community pipeline 指南)**:本文档"如何添加自己流水线"的上游指引,对应 `pipeline.push_to_hub()` 之后的命名规范、目录结构、Hub 提交流程,与本文档第 5、6 节(三步后续工作)形成闭环。

**外部关联组件/特性**:
- `trust_remote_code` 特性:与 `stabilityai/japanese-stable-diffusion-xl` 仓库结构示例关联,展示真实生产级自定义流水线的目录布局。
- 自定义 UNet 示例源码:`showlab/Show-1` 仓库 `showone/models/unet_3d_condition.py` 是原始实现,经 `sayakpaul/show-1-base-with-code` 适配到 Diffusers 接口后存于 `unet/showone_unet_3d_condition.py`。
- 自定义流水线源码:`sayakpaul/show-1-base-with-code` 仓库 `pipeline_t2v_base_pixel.py` 是 `TextToVideoIFPipeline` 类的具体实现。

---

## 【使用方法】

**加载社区流水线(原文示例)**:

```python
from diffusers import DiffusionPipeline

pipeline = DiffusionPipeline.from_pretrained(
    "google/ddpm-cifar10-32",
    custom_pipeline="hf-internal-testing/diffusers-dummy-pipeline",
    use_safetensors=True
)
```

**加载官方社区流水线并混合外部组件(原文示例)**:

```python
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
    use_safetensors=True,
)
```

**构建自定义流水线(原文 5 步)**:

1. `T5Tokenizer.from_pretrained(pipe_id, subfolder="tokenizer")` + `T5EncoderModel.from_pretrained(pipe_id, subfolder="text_encoder")`
2. `DPMSolverMultistepScheduler.from_pretrained(pipe_id, subfolder="scheduler")`
3. `CLIPFeatureExtractor.from_pretrained(pipe_id, subfolder="feature_extractor")`
4. `ShowOneUNet3DConditionModel.from_pretrained(pipe_id, subfolder="unet")`(自定义类须改名)
5. `TextToVideoIFPipeline(unet=unet, text_encoder=text_encoder, tokenizer=tokenizer, scheduler=scheduler, feature_extractor=feature_extractor)` → `pipeline.to(device="cuda")` + `pipeline.torch_dtype = torch.float16`

**分享到 Hub**:`pipeline.push_to_hub("custom-t2v-pipeline")`,然后修改 `model_index.json` 的 `_class_name` 字段,并上传两个 `.py` 脚本到对应目录。

**推理调用(原文示例)**:

```python
pipeline = DiffusionPipeline.from_pretrained(
    "<change-username>/<change-id>",
    trust_remote_code=True,
    torch_dtype=torch.float16
).to("cuda")

prompt_embeds, negative_embeds = pipeline.encode_prompt("hello")
video_frames = pipeline(
    prompt_embeds=prompt_embeds,
    negative_prompt_embeds=negative_embeds,
    num_frames=8,
    height=40,
    width=64,
    num_inference_steps=2,
    guidance_scale=9.0,
    output_type="pt"
).frames
```
