# 特性设计：TensorCast 适配 FLUX.1-dev 图像生成仿真

> 仓 `msmodeling` · 路径 `docs/design/flux1_dev_image_generation_adaptation_design.md` · 类型 design · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/msmodeling/docs/design/flux1_dev_image_generation_adaptation_design.md

# 一体化深度解读：FLUX.1-dev 图像生成仿真适配设计

---

## 【定位】

本文档是 TensorCast 在 **图像生成公共 Core 基线（commit `bcfd4fa27a2e293ac62008ffae404e49f276f768`）** 之上，为精确模型 **`black-forest-labs/FLUX.1-dev`** 的 Transformer 子模块设计的**纯仿真（不下载权重、不生成图片）适配方案**，明确划定了"做什么 / 不做什么"的边界，并给出 FLUX 身份校验、CFG（含 parallel 模式）、Ulysses 序列并行、Q/K RMSNorm patch 与 DiT block cache 的全套实现规约。

---

## 【技术要点】

1. **仿真边界严格收敛**：明确不下载权重、不执行 prompt 编码/CLIP/T5 encoder/tokenizer/VAE/scheduler/latent 更新/图片 I/O；不引入 `tensor_cast/image_generation` 及 `ImageGenerationRequest`、`ImageGenerationResult`、`ImageModelProfile`、`ImageProfileCollection`、`ImageGenerationAdapter`、`CFGBranch` 等抽象；不引入通用 engine/registry/plugin/handler，也不修改公共 CLI 生命周期、Runtime 输出契约、video generation 或其它模型行为。仿真耗时**不**等于端到端图片生成耗时。
2. **FLUX 模块文件与 frozen procedural seams**：生产文件集中在 `cli/inference/image_generate.py`、`tensor_cast/diffusers/image_dispatch.py`、`tensor_cast/diffusers/flux_image.py`、`tests/assets/model_config/FLUX.1-dev/`；模块导入时不得解析 fixture、构造模型、访问网络或修改全局 registry；`image_dispatch.py` 仅在命中远端候选或本地 `FluxTransformer2DModel` 配置时 lazy import `flux_image`，未支持 kind fail closed。公共生命周期仅通过 8 个平面函数 `resolve_image_model_kind`/`validate_image_config`/`prepare_image_inputs`/`apply_image_cfg`/`shard_image_inputs`/`prepare_image_model`/`forward_image_model`/`image_cache_spec` 调用模型逻辑。
3. **远端身份 + 严格 config-only 本地校验**：远端仅接受 `remote_source=huggingface`、`model_id=black-forest-labs/FLUX.1-dev`；`FLUX.1-schnell`、Fill、Redux、社区 mirror、其它 source 全部失败并返回 expected/actual 错误。`FLUX.1-dev` 是 HF gated 模型，源码/命令/fixture/日志/测试不得记录 token；hermetic 测试只使用审核后的本地 config-only fixture，不访问 Hub。本地候选必须通过 `model_index.json`（`_class_name=FluxPipeline`，且 5 个 component 锁定为 `[diffusers, AutoencoderKL]`、`[transformers, CLIPTextModel]`、`[transformers, CLIPTokenizer]`、`[transformers, T5EncoderModel]`、`[transformers, T5TokenizerFast]`）+ Transformer 字段（`patch_size=1`、`in_channels=64`、`num_layers=19`、`num_single_layers=38`、`attention_head_dim=128`、`num_attention_heads=24`、`joint_attention_dim=4096`、`pooled_projection_dim=768`、`guidance_embeds=true`、`axes_dims_rope` 缺失按 Diffusers 0.38.0 默认 `(16,56,56)`、`out_channels` 缺失/null 规范化为 64）+ VAE 字段（`_class_name=AutoencoderKL`、`latent_channels=16`、`block_out_channels=[128,256,512,512]`、`down_block_types=4*DownEncoderBlock2D`、`up_block_types=4*UpDecoderBlock2D`、`layers_per_block=2`、`scaling_factor=0.3611`、`shift_factor=0.1159`、`latents_mean=null`、`latents_std=null`、`use_quant_conv=false`、`use_post_quant_conv=false`）+ 文本架构 (`text_encoder=CLIPTextModel`、`text_encoder_2=T5EncoderModel`) 的逐字段锁定。运行时严格绑定 `diffusers==0.38.0`，仅当完整验证成功才置 `model_config.image_dispatch_validated=True`，作为 builder 构建门禁。scheduler 不参与验证/构建/workload。
4. **输入几何 + 2×2 packing**：从 VAE 计算 `vae_scale_factor = 2**(len(block_out_channels)-1)`，按 `H_lat = 2*floor(H/(2*vae_scale_factor))`、`W_lat = 2*floor(W/(2*vae_scale_factor))`、`C_lat = transformer.in_channels/4`、`N_img = (H_lat/2)*(W_lat/2)` 推导。`1024×1024` 请求对应 `unpacked latent [B,16,128,128]` → `packed hidden [B,4096,64]` 与 `img_ids [4096,3]`。非对齐尺寸按 floor 公式处理，**不 padding、不隐式 trim**；无法形成正 latent 的尺寸失败；source-image 输入不支持。Packing 必须使用 Diffusers 0.38.0 source-faithful 顺序 `view→permute(0,2,4,1,3,5)→reshape`。
5. **CFG（普通与 parallel）+ Ulysses**：普通 CFG（`--use-cfg --no-cfg-parallel`）effective batch `2B`，沿 dim 0 复制 `hidden_states`/`encoder_hidden_states`/`pooled_projections`/`timestep`/`guidance`，**不复制** `img_ids [N_img,3]` 与 `txt_ids [L,3]`，**不接受**独立负向 text length、不做 numerical CFG combine 与 CFG scale。CFG parallel 仅在 `use_cfg=true` 时生效，固定 `world_size=2U`、`representative local batch=B`、`cfg group(u)=[u, U+u]`；Transformer local output 先完成 Ulysses dim-1 gather，再执行 CFG group dim-0 all-gather，公共生命周期不返回 combine 后 tensor。Ulysses 首次 forward 前强制 `N_img % U == 0 && text_seq_len % U == 0 && num_attention_heads % U == 0`；`U>1` 时 `hidden_states`/`encoder_hidden_states` 切 dim 1，`img_ids`/`txt_ids` 切 dim 0；Runtime 期间按 active model 设置 Diffusers sequence-parallel group，成功或异常退出时恢复为 `None`。
6. **Q/K RMSNorm patch + DiT block cache**：唯一首版融合适配是 FLUX attention 的 Q/K RMSNorm，目标 module 为 `norm_q`/`norm_k`/`norm_added_q`/`norm_added_k`，覆盖 `19 dual blocks * 4 + 38 single blocks * 2 = 152` 个 norm；source module 必须是 `torch.nn.RMSNorm` 或 `RMSNormFusedWrapper`，权重 shape `(128,)`、`eps=1e-6`；全部 152 个预检成功才修改模型，重复调用幂等。Cache 仅在 `dit_cache=true && cache_step_interval>1` 时构建第二模型；step range clamp 到 `[0, sample_step-1]`，空则失败；block range 半开区间 `[start,end)` 在 57 blocks 上 clamp；未替换任何 block 必须失败；`enable_dit_block_cache` 每次运行新建 `CacheState`；cache 窗口内按 interval 更新 `cache_state.reuse`，窗口外用 baseline；Chrome trace 仅在 Runtime 成功完成后导出。`flux_image.cache_spec()` 直接返回 class-bound `DiTBlockCacheSpec`（`class_name=FluxTransformer2DModel`、`model_type=flux1-dev`），不注册到 video cache registry，block discovery 顺序为 19 dual `transformer_blocks` → 38 single `single_transformer_blocks`，generic cache agent 以 hidden-first 处理，wrapper 进入/退出时各做一次顺序适配。
7. **Forward 与 Runtime 输出契约**：FLUX helper 调用 Diffusers 0.38.0 forward 仅传 `hidden_states`/`encoder_hidden_states`/`pooled_projections`/`timestep`/`img_ids`/`txt_ids`/`guidance` 与 `return_dict=False`，**不传** scheduler/ControlNet/IP-Adapter 等；输出必须是单一 rank-3 tensor，pre-gather shape 与本地 `hidden_states` 完全一致；全局 `generated_token_count` 是该本地 sequence 长度的正整数倍；公共 CLI 完成 Ulysses dim-1 gather 后 logical sequence 维才等于全局 `generated_token_count`；异常输出 fail closed。`sample_step=N` 恰好执行 N 次固定 shape forward，不涉及 scheduler read/call、schedule、sigma、latent 更新。`timestep`/`guidance` 直接传入，Diffusers 0.38.0 自行 cast 并乘 1000，模型 helper 不预乘、不引入 scheduler 数值语义。

---

## 【关键机制与数据】

- **基线锁定**：公共 Core 基线为 `bcfd4fa27a2e293ac62008ffae404e49f276f768`（原文）。
- **模型规模**：19 dual blocks + 38 single blocks = 57 blocks；Q/K RMSNorm patch 总量 `19*4 + 38*2 = 152`（原文）。
- **1024×1024 几何**：unpacked latent `[B,16,128,128]`、packed hidden `[B,4096,64]`、`img_ids [4096,3]`；`N_img = 4096`、`C_lat = 64/4 = 16`、`vae_scale_factor = 2**(4-1) = 8`、最终 `H_lat=128, W_lat=128`（原文公式推导）。
- **CFG parallel**：固定 `world_size = 2U`，`representative local batch = B`，每 step 每个 representative rank 一次 forward，`cfg group(u) = [u, U+u]`（原文）。
- **Ulysses 分片维度**：`hidden_states`/`encoder_hidden_states` 切 dim 1；`img_ids`/`txt_ids` 切 dim 0；`U=1` 不分片、不设 output gather dim（原文）。
- **Meta 输入 shape 与 dtype**：`hidden_states [B,N_img,64]`、`encoder_hidden_states [B,L,4096]`、`pooled_projections [B,768]` 用 Transformer dtype；`img_ids [N_img,3]`、`txt_ids [L,3]`、`timestep [B]`、`guidance [B]` 用 FP32（原文）。
- **ID 语义**：`img_ids[:,0]` 全零、后两列 row-major；`txt_ids` 全零；模型内部按 text-first 语义组合（原文）。
- **VAE 关键常数**：`scaling_factor=0.3611`、`shift_factor=0.1159`、`latents_mean=null`、`latents_std=null`、`use_quant_conv=false`、`use_post_quant_conv=false`（原文）。
- **版本约束**：运行时严格 `diffusers==0.38.0`；`axes_dims_rope` 缺失按 Diffusers 0.38.0 默认 `(16,56,56)`；`out_channels` 缺失/null 规范化为 64（原文）。
- **安全约束**：`FLUX.1-dev` 为 HF gated 模型；源码/命令/fixture/日志/测试不得记录 token；hermetic 测试只使用本地 config-only fixture，不访问 Hub（原文）。
- **数据流**：远端 HF 或本地 config → `_class_name == FluxTransformer2DModel` 入口 → `model_index.json` + Transformer + VAE + 文本编码器指纹校验 → `image_dispatch_validated=True` → 构造 baseline meta `FluxTransformer2DModel` → FLUX model patch → 独立构造 cache model（条件满足时）→ 分别 compile → Runtime 按 step 选 baseline/cache → 输出 operator table 与 Chrome trace（原文）。

---

## 【表格解读】

**修订记录表**（原文逐字还原）：

| 日期 | 版本 | 修改描述 | 作者 | 关联文档 |
| --- | --- | --- | --- | --- |
| 2026-08-12 | 0.1 | 锁定 FLUX.1-dev 模型专属实现与验收范围 | `minghang_c` | [FLUX.1-dev RFC](../RFC/rfc_add_flux1_dev_support_zh.md) |
| 2026-08-13 | 0.2 | 按更新后的 procedural image-generation Core 重写模块、CFG、cache 与生命周期设计 | `minghang_c` | [FLUX.1-dev RFC](../RFC/rfc_add_flux1_dev_support_zh.md) |

**逐行解读**：

- 第 1 行（v0.1，2026-08-12）：作者 `minghang_c` 完成首版设计，核心动作是**锁定 FLUX.1-dev 模型专属实现与验收范围**，明确这是为单个精确模型（`black-forest-labs/FLUX.1-dev`）而非通用图像生成栈而生的实现，验收边界随后续章节细化（不做图片生成、不下载权重等）。
- 第 2 行（v0.2，2026-08-13）：同作者基于**更新后的 procedural image-generation Core**对模块边界、CFG（普通 / parallel）、cache（FLUX DiT cache 57 blocks）、生命周期（frozen procedural seams、Runtime 输出契约）做了重写，反应了基线 commit `bcfd4fa27a2e293ac62008ffae404e49f276f768` 之上的核心 API 演进。
- 两行均关联到同一个上游 RFC 文档 `../RFC/rfc_add_flux1_dev_support_zh.md`，作为动机/范围的源头依据。

**配置锁定清单**（非表格但具有表格性质的逐字段锁定，原文以代码块给出；为便于理解以 markdown 表格汇总，但**所有字段值与原文逐字一致**）：

| 组件 | 字段 | 锁定值 | 备注 |
| --- | --- | --- | --- |
| Pipeline | `_class_name` | `FluxPipeline` | `model_index.json` 必验 |
| Pipeline | `vae` | `[diffusers, AutoencoderKL]` | |
| Pipeline | `text_encoder` | `[transformers, CLIPTextModel]` | |
| Pipeline | `tokenizer` | `[transformers, CLIPTokenizer]` | |
| Pipeline | `text_encoder_2` | `[transformers, T5EncoderModel]` | |
| Pipeline | `tokenizer_2` | `[transformers, T5TokenizerFast]` | |
| Pipeline | `transformer` | `[diffusers, FluxTransformer2DModel]` | |
| Transformer | `_class_name` | `FluxTransformer2DModel` | 单独类名不可通过验证 |
| Transformer | `patch_size` | `1` | |
| Transformer | `in_channels` | `64` | |
| Transformer | `num_layers` | `19` | dual blocks 数 |
| Transformer | `num_single_layers` | `38` | single blocks 数 |
| Transformer | `attention_head_dim` | `128` | RMSNorm 权重 shape 来源 |
| Transformer | `num_attention_heads` | `24` | 须满足 `num_attention_heads % U == 0` |
| Transformer | `joint_attention_dim` | `4096` | |
| Transformer | `pooled_projection_dim` | `768` | |
| Transformer | `guidance_embeds` | `true` | |
| Transformer | `axes_dims_rope` | 缺失时按 Diffusers 0.38.0 默认 `(16, 56, 56)` | |
| Transformer | `out_channels` | 缺失或 null 时规范化为 `64` | |
| VAE | `_class_name` | `AutoencoderKL` | |
| VAE | `latent_channels` | `16` | |
| VAE | `block_out_channels` | `[128, 256, 512, 512]` | 决定 `vae_scale_factor` |
| VAE | `down_block_types` | `4 * DownEncoderBlock2D` | |
| VAE | `up_block_types` | `4 * UpDecoderBlock2D` | |
| VAE | `layers_per_block` | `2` | |
| VAE | `scaling_factor` | `0.3611` | |
| VAE | `shift_factor` | `0.1159` | |
| VAE | `latents_mean` | `null` | |
| VAE | `latents_std` | `null` | |
| VAE | `use_quant_conv` | `false` | |
| VAE | `use_post_quant_conv` | `false` | |
| text_encoder | `architectures` | `[CLIPTextModel]` | text_encoder/config.json |
| text_encoder_2 | `architectures` | `[T5EncoderModel]` | text_encoder_2/config.json |
| 缓存规格 | `class_name` | `FluxTransformer2DModel` | class-bound |
| 缓存规格 | `model_type` | `flux1-dev` | 不注册到 video cache registry |

---

## 【公式解读】

**几何推导公式（原文逐字保留）**：

```
vae_scale_factor = 2 ** (len(block_out_channels) - 1)
H_lat = 2 * floor(H / (2 * vae_scale_factor))
W_lat = 2 * floor(W / (2 * vae_scale_factor))
C_lat = transformer.in_channels / 4
N_img = (H_lat / 2) * (W_lat / 2)
```

- `vae_scale_factor`：从 VAE `block_out_channels=[128,256,512,512]` 长度 4 计算得 `2**3 = 8`，表示 VAE 对空间维度的下采样倍率。
- `H_lat` / `W_lat`：unpacked latent 的空间高/宽，先用 `floor` 做整除，再乘 2 作为打包系数；非对齐尺寸**不 padding、不隐式 trim**，直接按 floor 截断。
- `C_lat = transformer.in_channels / 4`：FLUX 把 `C_lat=16` 通道的 latent 2×2 patch 打包为 `16*4 = 64` 的 hidden dim，对应原文 `in_channels=64` 的锁定。
- `N_img = (H_lat/2)*(W_lat/2)`：把 2D 网格展平为 token 序列长度，例如 `H_lat=W_lat=128` 时 `N_img=64*64=4096`。

**2×2 packing（原文逐字保留）**：

```python
latents.view(B, C, H_lat // 2, 2, W_lat // 2, 2) \
    .permute(0, 2, 4, 1, 3, 5) \
    .reshape(B, (H_lat // 2) * (W_lat // 2), C * 4)
```

- `B`：batch；`C`：latent channels（`C_lat=16`）；`H_lat//2`、`W_lat//2`：每个 2×2 patch 块在两个维度的分组数。
- `view`：把 `[B, C, H_lat, W_lat]` 拆成 `[B, C, H_lat//2, 2, W_lat//2, 2]`，显式表达 2×2 patch 分组。
- `permute(0, 2, 4, 1, 3, 5)`：将维度重排为 `[B, H_lat//2, W_lat//2, C, 2, 2]`，空间块在外、通道与 patch 索引在内。
- `reshape`：合并为 `[B, (H_lat//2)*(W_lat//2), C*4]`，得到 packed hidden states（`N_img = (H_lat//2)*(W_lat//2)`、通道 `C*4 = 64`）。
- 顺序必须与 Diffusers source-faithful 一致，否则会引入非预期的数值差异。

**CFG parallel 配置（原文逐字保留）**：

```
world_size = 2U
representative local batch = B
每 step 每个 representative rank 一次 forward
cfg group(u) = [u, U + u]
```

- `world_size = 2U`：总 rank 数固定为 Ulysses 分片数 `U` 的两倍，用于分别承载 conditional 与 unconditional 两个 CFG branch。
- `representative local batch = B`：每个 representative rank 上的本地 batch。
- `每 step 每个 representative rank 一次 forward`：体现"每 step 一次 forward" 的 CFG 设计。
- `cfg group(u) = [u, U + u]`：rank `u` 与 rank `U+u` 配对组成 CFG group，用于先 Ulysses dim-1 gather、再 CFG group dim-0 all-gather。

**Ulysses 分片维度（原文逐字保留）**：

```
hidden_states         dim 1
encoder_hidden_states dim 1
img_ids               dim 0
txt_ids               dim 0
```

- `hidden_states [B, N_img, 64]` 切 dim 1 → 每 rank `[B, N_img/U, 64]`，与 `forward_model` 返回本地 output sequence 长度 `N_img/U` 对齐。
- `encoder_hidden_states [B, L, 4096]` 切 dim 1 → 每 rank `[B, L/U, 4096]`。
- `img_ids [N_img, 3]`、`txt_ids [L, 3]` 切 dim 0，与各自对应张量保持同号分片，便于后续 attention all-to-all。

**前置整除校验（原文逐字保留）**：

```
N_img % U == 0
text_seq_len % U == 0
num_attention_heads % U == 0
```

- 保证 Ulysses 分片在 sequence length、text length、head 数三个维度上均能整除，避免在 `U>1` 时出现不可整除的形状。

**Block 发现顺序与 RMSNorm 覆盖（原文逐字保留）**：

```
19 dual blocks * 4 norms + 38 single blocks * 2 norms = 152
```

- 19 dual blocks（Diffusers `transformer_blocks`）每个含 `norm_q`/`norm_k`/`norm_added_q`/`norm_added_k` 共 4 个 RMSNorm → `19*4 = 76`；38 single blocks（`single_transformer_blocks`）每个含 `norm_q`/`norm_k` → `38*2 = 76`；合计 `76+76 = 152` 个目标 RMSNorm 需在首版适配中预检并替换为 `tensor_cast.rms_norm.default`。

---

## 【关联】

- **上游 RFC**：[`../RFC/rfc_add_flux1_dev_support_zh.md`](../RFC/rfc_add_flux1_dev_support_zh.md)（在修订记录两行均被引用）是本设计的源头依据，承载 FLUX.1-dev 支持引入的动机、范围与验收标准；本文档是该 RFC 在**精确模型专属仿真**方向上的具体实现规约。
- **基线 Core**：`bcfd4fa27a2e293ac62008ffae404e49f276f768` 是图像生成公共 Core 基线，本文所有 frozen procedural seams（8 个平面函数）、Runtime 输出契约（`Model compilation execution time` + operator table + 可选 Chrome trace）、公共 CLI 生命周期均建立其上；v0.2 重写即源于该 Core 的 procedural image-generation API 更新。
- **Diffusers 0.38.0**：作为唯一受支持的运行时，`axes_dims_rope` 默认值、2×2 packing 顺序、`timestep`/`guidance` 自乘 1000、sequence-parallel group 接口、`FluxTransformer2DModel` forward 签名等均以 0.38.0 为准，版本漂移会被 meta Transformer 构建前失败挡住。
- **公共 Core 抽象层**：与 `tensor_cast/image_generation`、`ImageGenerationRequest`、`ImageGenerationResult`、`ImageModelProfile`、`ImageProfileCollection`、`ImageGenerationAdapter`、`CFGBranch` 等抽象明确解耦；与通用 engine、registry、plugin、handler 解耦；不修改公共 CLI 生命周期、Runtime 输出契约、video generation 或其它模型行为。
- **下游 module 依赖**：`tensor_cast.rms_norm.default`（用于 Q/K RMSNorm 融合）、`DiTBlockCacheSpec`/`CacheState`（用于 FLUX DiT cache）、Diffusers sequence-parallel group（用于 Ulysses `U>1`）是本文直接消费的下游能力。
- **跨模型边界**：明确将 scheduler/CLIP/T5/VAE/tokenizer/prompt 编码/latent 数值/图片 I/O 排除在仿真之外，确保不与 video generation、其它图像模型或潜在未来扩展耦合。
- **关联文档引用**：`../RFC/rfc_add_flux1_dev_support_zh.md`（出现两次，分别在修订记录 v0.1 与 v0.2 的"关联文档"列）。

---

## 【使用方法】

原文未给出独立的"启用方式/配置项/命令"小节。可从文档各处汇总出的相关参数与开关如下（**全部为原文出现过的字段/标志**）：

- **远端身份**：`remote_source=huggingface`、`model_id=black-forest-labs/FLUX.1-dev`（原文"远端身份"小节）。
- **本地入口条件**：已加载 Transformer 配置的 `_class_name == "FluxTransformer2DModel"` + 完整 fingerprint（model_index.json / Transformer / VAE / text_encoder / text_encoder_2 五处配置全部通过），缺一即 fail closed；只有验证通过后才置 `model_config.image_dispatch_validated = True` 作为 builder 构建门禁（原文第 3 节）。
- **CFG 开关**：普通 CFG `--use-cfg --no-cfg-parallel`（effective batch `2B`、dim 0 复制、不复制 `img_ids`/`txt_ids`、不接受独立负向 text length、不做 numerical combine）；CFG parallel 仅 `use_cfg=true` 时生效，固定 `world_size=2U`（原文第 5.1、5.2 节）。
- **Ulysses 开关**：`U=1` 不分片；`U>1` 切 dim 0/1，并要求 `N_img % U == 0 && text_seq_len % U == 0 && num_attention_heads % U == 0`（原文第 5.3 节）。
- **Cache 开关**：`dit_cache=true` 且 `cache_step_interval>1` 才构建第二模型；`enable_dit_block_cache` 每次运行新建 `CacheState`；step range clamp 到 `[0, sample_step-1]`、空则失败；block range 半开 `[start,end)` 在 57 blocks 上 clamp；未替换任何 block 必须失败；Chrome trace 仅 Runtime 成功后导出（原文第 7 节）。
- **执行步数**：`sample_step=N` 恰好执行 N 次固定 shape forward，无 scheduler/sigma/latent 更新（原文第 8 节）。
- **成功边界输出**：公共 CLI 打印 `Model compilation execution time`、Runtime operator table，以及可选 Chrome trace 完成信息（原文第 2.2、7、8 节）。
- **Fixture 路径**：`tests/assets/model_config/FLUX.1-dev/`，含 config-only fixture、provenance 与 SHA256SUMS（原文第 2.1 节）。
- **Gated 模型注意**：`FLUX.1-dev` 为 Hugging Face gated 模型，远端真实 config-only 解析需用户先在官方页面接受条款并通过标准 HF 凭据存储提供有读取权限的 token；源码、命令、fixture、日志、测试**不得记录 token**；hermetic 测试只使用审核后的本地 config-only fixture，不访问 Hub 或个人凭据（原文第 3.1 节）。
- **运行时版本约束**：严格 `diffusers==0.38.0`（原文第 3.2 节）。

> 备注：用户提供的原文在第 8 节末尾截断（"成功输出由 `cli/inference/imag"），故是否存在更细粒度的 CLI 调用样例、trace 导出条件或 trace 路径模板，原文未涉及。
