# Load LoRAs for inference

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/diffusion/diffusers0.25.0/docs/source/en/tutorials/using_peft_for_inference.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/diffusion/diffusers0.25.0/docs/source/en/tutorials/using_peft_for_inference.md

# 文档深度解读:Load LoRAs for inference

## 【定位】

这篇文档是 🤗 Diffusers 中关于 **PEFT 集成下 LoRA 推理加载与组合** 的使用指南,聚焦于 Stable Diffusion XL (SDXL) 场景,演示如何加载、切换、组合、监控、禁用以及 fuse(融合) 多个 LoRA 适配器(adapter)进行推理,并生成可叠加风格效果的图像。

---

## 【技术要点】

1. **基础管道加载**:使用 `stabilityai/stable-diffusion-xl-base-1.0` 作为 SDXL 基座模型,`torch_dtype=torch.float16`,`.to("cuda")`。
2. **单 LoRA 加载**:通过 `pipe.load_lora_weights(repo_id, weight_name=..., adapter_name=...)` 加载 LoRA;此处加载 `CiroN2022/toy-face`(`toy_face_sdxl.safetensors`)并命名为 `"toy"`。
3. **推理参数**:`num_inference_steps=30`、`generator=torch.manual_seed(0)`、通过 `cross_attention_kwargs={"scale": lora_scale}` 注入 LoRA 缩放,`lora_scale=0.9`。
4. **切换 adapter**:先 `load_lora_weights(...)` 注册 `"pixel"`(来自 `nerijs/pixel-art-xl`),再调用 `pipe.set_adapters("pixel")` 激活;pipeline 默认将首次加载的 adapter 设为活跃。
5. **多 adapter 组合**:`pipe.set_adapters(["pixel", "toy"], adapter_weights=[0.5, 1.0])` 同时激活两个 LoRA 并按权重融合;prompt 必须包含各 LoRA 对应的 trigger word(本文为 `"toy_face"` 与 `"pixel art"`)。
6. **监控与禁用**:
   - `pipe.get_active_adapters()` → `["toy", "pixel"]`
   - `pipe.get_list_adapters()` → `{"text_encoder": [...], "unet": [...], "text_encoder_2": [...]}`(反映三组件:两个 text encoder + unet)
   - `pipe.disable_lora()` 关闭全部 LoRA 回到基础模型
7. **Fuse 加速**:`pipe.fuse_lora()` 将 LoRA 权重合并进 UNet 与 text encoder 的主权重,带来推理加速与显存下降;`pipe.unfuse_lora()` 还原;支持 `adapter_names=["pixel"]` 子集 fuse 以加快特定生成。

---

## 【关键机制与数据】

### 工作原理(原文:用 Diffusers + PEFT 集成管理 adapter)
- 加载: `load_lora_weights` 把远程 safetensors 权重通过 PEFT 接口注入到 pipe 内部组件(text_encoder / text_encoder_2 / unet)的 LoRA 层,并以 `adapter_name` 索引。
- 激活: `set_adapters` 标记当前活跃 adapter 集合及其权重;实际缩放在前向时被 `cross_attention_kwargs={"scale": lora_scale}` 或 `adapter_weights` 施加到 cross-attention 的 LoRA 分支。
- 融合: `fuse_lora` 把 LoRA 增量写回主权重,推理时不再走 LoRA 分支,从而省去额外计算与显存;`unfuse_lora` 反向还原,便于后续切换。
- 触发词机制: 由于社区 LoRA 多源自 DreamBooth 训练,需在 prompt 中显式给出各 LoRA 的 trigger word(如 `toy_face` 与 `pixel art`),组合时需全部出现。

### 性能与数据(原文:仅给出方法描述)
- 原文说明 `fuse_lora` 可以"speed-up in inference and lower VRAM usage",但**未给出具体数字**。
- 各推理调用固定使用 `num_inference_steps=30` 与 `torch.manual_seed(0)`,作为可复现性的固定项(并非性能基准)。

---

## 【表格解读】

**原文无表格。** 全文为代码块 + 散文描述,没有出现 markdown 表格/参数表/性能对比表。命令、参数与 adapter 名称已在上文【技术要点】中按代码块形式呈现。

---

## 【公式解读】

**原文无公式。** 文档未给出 LoRA 数学形式(例如 $W' = W + \alpha \cdot B A$)、attention 缩放公式或任何伪代码公式。LoRA 的 scale 仅作为 `cross_attention_kwargs={"scale": lora_scale}` 的数值参数(0.9 / 1.0)出现,而非形式化公式。

---

## 【关联】

- **Stable Diffusion XL pipeline**(`../api/pipelines/stable_diffusion/stable_diffusion_xl`):本文所有示例的载体,LoRA 挂载在该管道的 `text_encoder`、`text_encoder_2`、`unet` 三组件之上。
- **PEFT 库**(外部):adapter 的底层管理来自 🤗 PEFT,Diffusers 通过 `StableDiffusionXLLoraLoaderMixin` 与 `UNet2DConditionLoadersMixin` 暴露能力(`load_lora_weights`、`set_adapters`、`fuse_lora`、`get_active_adapters`、`get_list_adapters`、`disable_lora`)。
- **DreamBooth 训练**(外部链接 `https://huggingface.co/docs/diffusers/main/en/training/dreambooth`):解释了"为何 LoRA 几乎都需要 trigger word"以及"为何 prompt 必须包含触发词"。
- **LoRA 概念指南**(外部 `https://huggingface.co/docs/peft/conceptual_guides/lora`):作为前置阅读,本文对 LoRA 术语做了"LoRA / adapter 互换使用"的约定。
- **外部模型仓**:`CiroN2022/toy-face`、`nerijs/pixel-art-xl` 提供实际 LoRA 权重与 trigger word 定义。

---

## 【使用方法】

### 安装
```bash
!pip install -q transformers accelerate
!pip install peft
!pip install diffusers
```

### 加载基座 + LoRA
```python
from diffusers import DiffusionPipeline
import torch

pipe_id = "stabilityai/stable-diffusion-xl-base-1.0"
pipe = DiffusionPipeline.from_pretrained(pipe_id, torch_dtype=torch.float16).to("cuda")

pipe.load_lora_weights("CiroN2022/toy-face", weight_name="toy_face_sdxl.safetensors", adapter_name="toy")
```

### 单 adapter 推理
```python
prompt = "toy_face of a hacker with a hoodie"
lora_scale = 0.9
image = pipe(prompt, num_inference_steps=30,
             cross_attention_kwargs={"scale": lora_scale},
             generator=torch.manual_seed(0)).images[0]
```

### 切换/组合 adapter
```python
pipe.load_lora_weights("nerijs/pixel-art-xl", weight_name="pixel-art-xl.safetensors", adapter_name="pixel")
pipe.set_adapters("pixel")                                  # 切换到单 adapter
pipe.set_adapters(["pixel", "toy"], adapter_weights=[0.5, 1.0])  # 组合 + 权重
```

### 监控与禁用
```python
pipe.get_active_adapters()    # 当前活跃列表
pipe.get_list_adapters()      # 按组件(text_encoder/unet/text_encoder_2)查看
pipe.disable_lora()           # 关闭所有 LoRA,回到基座
```

### Fuse / Unfuse
```python
pipe.set_adapters(["pixel", "toy"], adapter_weights=[0.5, 1.0])
pipe.fuse_lora()              # 全部 fuse(注释明确:本文示例仅 fuse 到 UNet)
pipe.unfuse_lora()            # 还原

pipe.fuse_lora(adapter_names=["pixel"])   # 仅 fuse 指定子集
```

> 备注: 原文示例代码的注释写作 "# Fuses the LoRAs into the Unet",但 `fuse_lora()` 在文档正文中描述为 "fuse/unfuse multiple adapters directly into the model weights (both UNet and text encoder)",即同时影响 UNet 与 text encoder;此差异以正文描述为准。
