# Accelerate inference of text-to-image diffusion models

> 仓 `modelzoo-pytorch` · 路径 `PyTorch/built-in/diffusion/diffusers0.25.0/docs/source/en/tutorials/fast_diffusion.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/modelzoo-pytorch/PyTorch/built-in/diffusion/diffusers0.25.0/docs/source/en/tutorials/fast_diffusion.md

# 《Accelerate inference of text-to-image diffusion models》深度解读

## 【定位】

这篇文档解决**文本到图像扩散模型推理速度慢**的问题,以 SDXL 为案例,演示如何通过 PyTorch 2.0 工具链(bfloat16 + SDPA + torch.compile + QKV 融合 + 动态量化)逐层叠加优化,一步步降低单张图像的推理延迟。

---

## 【技术要点】

1. **bfloat16 降精度推理**:通过 `torch_dtype=torch.bfloat16` 加载流水线,将 UNet/VAE 的权重和计算从 fp32 降到 bf16。
2. **SDPA 高效注意力**:调用 PyTorch 的 `scaled_dot_product_attention` 替代朴素 attention 实现(显式禁用的方式是 `pipe.unet.set_default_attn_processor()` / `pipe.vae.set_default_attn_processor()`)。
3. **torch.compile 编译**:对 UNet 与 VAE decoder 使用 `mode="max-autotune"`、`fullgraph=True`;配合 `torch.channels_last` 内存布局与若干 inductor flag。
4. **QKV 投影融合**:调用 `pipe.fuse_qkv_projections()` 把 Q/K/V 三个投影矩阵横向拼接成一个大矩阵,一次完成投影。
5. **动态 int8 量化**:对 UNet 与 VAE 应用 PyTorch 的 dynamic int8 quantization(原文该节内容被截断,未给出完整代码)。
6. **硬件基准**:原文在 **80GB / 400W A100**(锁最大 clock rate)上用 batch=1、num_inference_steps=30 测得延迟数字;同 prompt `"Astronaut in a jungle, cold color palette, muted colors, detailed, 8k"`。

---

## 【关键机制与数据】

### 优化栈与延迟收敛曲线(原文:累加式叠加,每一步在前一步基础上再加一种优化)

| 优化阶段 | 推理延迟(原文, A100) | 相对基线加速 |
|---|---|---|
| Baseline(fp32 + 默认 attention) | **7.36 s** | 1.00× |
| + bfloat16 | **4.63 s** | ≈1.59× |
| + bfloat16 + SDPA | **3.31 s** | ≈2.22× |
| + torch.compile(UNet+VAE, max-autotune, channels_last) | **2.54 s** | ≈2.90× |
| + `fuse_qkv_projections()` | **2.52 s** | ≈2.92× |
| + 动态 int8 量化 | 原文被截断,未给出数值 | — |

数据流:提示词 → tokenizer/text_encoder → UNet 反复去噪(num_inference_steps=30) → VAE decoder 解码到像素 → 输出图像。每一阶段优化作用于不同子模块:bfloat16 作用于 UNet/VAE 权重与算子 dtype;SDPA 作用于 attention 计算;torch.compile 作用于 UNet 与 VAE decoder 的整图执行;QKV 融合作用于 attention block 的输入投影;动态量化作用于 UNet 与 VAE 的权重。

加速来源直觉(原文表述):
- bf16 主要靠**降低内存带宽与算力**(同卡 GPU 对 bf16 吞吐更高)。
- SDPA 主要靠**更高效的 kernel**(包含 FlashAttention 风格实现)。
- torch.compile 主要靠**CUDA graph 捕获 + inductor 自动调优 + 算子融合**。
- QKV 融合主要靠**把三个小 matmul 合并成一个大 matmul**,对后续量化更友好。
- 动态量化:原文强调"小 matmul 场景下量化引入的转换开销可能反噬加速",这就是为什么需要先把 QKV 融合做大 matmul。

性能/质量权衡(原文表述):
- bf16/fp16 等降精度"对生成质量没有可感知影响,但显著降低延迟"。
- bf16 与 fp16 的优劣**取决于硬件**,现代 GPU 更偏 bf16。
- bf16 与量化联用时**比 fp16 更鲁棒**(原文实验结论)。
- QKV 融合在非 SD 流水线上**支持有限且实验性**,如 Kandinsky 暂未支持。

---

## 【表格解读】

**原文无表格**。文中各阶段的延迟数字以散落在小节末尾的自然句形式给出(7.36s / 4.63s / 3.31s / 2.54s / 2.52s),并配有同名的三连字符命名插图(`...Steps%3A_30_0.png` 到 `...Steps%3A_30_4.png`)作示意。本节上文"关键机制与数据"中的对照表为本解读的二次整理,**非原文表格**。

---

## 【公式解读】

**原文无公式**(无 LaTeX 或伪代码形式公式)。文中只有一段关于 QKV 融合机制的口语化描述(把 Q/K/V 三个投影矩阵"horizontally combine into a single matrix"以做一次性投影),可作为机制描述但未给出数学式。

---

## 【关联】

文档以 SDXL 为案例展开,但其方法论是泛化的,与以下内部链接对应的模块/教程强相关:

- **LCM LoRA**(`../using-diffusers/inference_with_lcm_lora.md`):文档开篇提到的"progressive timestep distillation"代表,通过蒸馏把采样步数砍到 4–8 步,与本文"减少单步成本"是**互补**的两条加速路径。
- **SDXL 使用文档**(`../using-diffusers/sdxl.md`):本文案例对应的流水线基线 `StableDiffusionXLPipeline`(`stabilityai/stable-diffusion-xl-base-1.0`)。
- **PyTorch 2.0 / SDPA 优化**(`../optimization/torch2.0.md`):解释了 `scaled_dot_product_attention` 的高效实现,本文是其针对 SDXL 的具体应用;该链接在文档中出现两次。
- **FP16 优化**(`../optimization/fp16.md`):提供了"降精度推理"的更完整指南;本文只取 bf16 视角,并指出 bf16 在现代 GPU 与量化场景中通常更优。
- **Kandinsky**(`../using-diffusers/kandinsky.md`):作为反例,在 `<Tip>` 中被点名 `fuse_qkv_projections()` **不支持** Kandinsky 这类非 SD 流水线,反映该优化的**适用边界**。
- **diffusion-fast**(`https://github.com/huggingface/diffusion-fast`):原文指向的完整 benchmark 代码仓库,本文只展示优化方法,不展示 benchmark 代码。
- **DeepCache 与 SSD-1B**:作为开篇并列的另外两条加速路线(progressive distillation、model compression、feature reuse)的代表性外部工作。
- **PyTorch 动态量化文档**(`https://pytorch.org/tutorials/recipes/recipes/dynamic_quantization.html`):最后阶段动态 int8 量化的官方说明。
- **diffusers PR #6179**:给希望在自定义流水线里支持 QKV 融合的开发者参考的合并细节。

优化技术之间的依赖关系(原文暗示):
- 量化要发挥作用,通常**需要先做 QKV 融合**以获得足够大的 matmul。
- torch.compile 与 SDPA 是协同的;若不启用 SDPA,compile 仍可工作但 kernel 不一定最优。
- 降精度(bf16/fp16)是量化与 compile 都受益的**基础前置条件**。

---

## 【使用方法】

### 环境安装(原文)
```bash
pip install -U diffusers
pip install -U transformers accelerate peft
```
并要求 **PyTorch nightly** 以获得最快的 kernel。

### 基准测试硬件(原文)
**80GB 400W A100,clock rate 锁到最大**,batch=1,num_inference_steps=30,prompt 为:
> "Astronaut in a jungle, cold color palette, muted colors, detailed, 8k"

### 启用各项优化(原文代码逐字)

1. **Baseline(全精度 + 默认 attention)**:
```python
from diffusers import StableDiffusionXLPipeline
pipe = StableDiffusionXLPipeline.from_pretrained(
    "stabilityai/stable-diffusion-xl-base-1.0"
).to("cuda")
pipe.unet.set_default_attn_processor()
pipe.vae.set_default_attn_processor()
image = pipe(prompt, num_inference_steps=30).images[0]
```

2. **bfloat16(去掉 `set_default_attn_processor`,加 `torch_dtype=torch.bfloat16`)**:
```python
pipe = StableDiffusionXLPipeline.from_pretrained(
    "stabilityai/stable-diffusion-xl-base-1.0", torch_dtype=torch.bfloat16
).to("cuda")
pipe.unet.set_default_attn_processor()
pipe.vae.set_default_attn_processor()
```

3. **SDPA(去掉 `set_default_attn_processor` 调用即可,因 diffusers 默认即使用 SDPA)**

4. **torch.compile(在 SDPA + bf16 之上叠加)**:
```python
torch._inductor.config.conv_1x1_as_mm = True
torch._inductor.config.coordinate_descent_tuning = True
torch._inductor.config.epilogue_fusion = False
torch._inductor.config.coordinate_descent_check_all_directions = True

pipe.unet.to(memory_format=torch.channels_last)
pipe.vae.to(memory_format=torch.channels_last)

pipe.unet = torch.compile(pipe.unet, mode="max-autotune", fullgraph=True)
pipe.vae.decode = torch.compile(pipe.vae.decode, mode="max-autotune", fullgraph=True)
image = pipe(prompt, num_inference_steps=30).images[0]
```
原文提示:`fullgraph=True` 避免图断裂;`mode="max-autotune"` 会启用 CUDA graph 并为延迟特化;**首次调用会很慢,后续调用受益**。

5. **QKV 融合**:
```python
pipe.fuse_qkv_projections()
```

6. **动态 int8 量化**:原文**该节在"`These techniques ma`"处被截断**,具体 `torch.ao.quantization.quantize_dynamic` 等调用写法与适用模块列表**原文未涉及**。

### 适用范围警告(原文 `<Tip>`)
`fuse_qkv_projections()` 当前是**实验性且支持有限**,在 Kandinsky 等非 SD 流水线上**不可用**;想自己扩展的读者需参考 diffusers PR #6179。

### Benchmark 代码
原文明确说明本文**不展示 benchmark 代码**,完整代码见 `https://github.com/huggingface/diffusion-fast`。
