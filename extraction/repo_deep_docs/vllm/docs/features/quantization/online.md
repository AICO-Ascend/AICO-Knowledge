# Online Quantization

> 仓 `vllm` · 路径 `docs/features/quantization/online.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm/docs/features/quantization/online.md

# vllm Online Quantization 文档深度解读

## 【定位】

本文档描述 vLLM 的**在线量化(Online Quantization)能力**——允许在模型加载阶段将 BF16/FP16 模型的 Linear 与 MoE 权重即时量化到更低精度(如 FP8 / MXFP),无需预先量化好的 checkpoint,也无需校准数据;权重的转换在加载时完成,激活的缩放在每次前向传播时动态进行。

---

## 【技术要点】

1. **量化触发方式**: 通过 `LLM` 构造参数 `quantization=<scheme_name>` 启动在线量化;支持 Python API 与 CLI(`vllm serve ... --quantization <scheme>`)两种入口。
2. **支持四种 scheme**: `fp8_per_tensor`、`fp8_per_block`、`mxfp8`、`mxfp4`,覆盖 per-tensor / per-block / MX 三类缩放粒度。
3. **量化粒度与数据格式**: weight 端使用 `fp8_e4m3`(FP8 系列)或 `fp4_e2m1`(MXFP4);scale 在 FP8 系列使用 fp32,在 MX 系列使用 `e8m0` 微缩格式;块大小包括 per-tensor、128×128(权)、1×128(激)、1×32(MX)。
4. **细粒度配置**: `quantization_config` 字典按 `linear` / `moe` 维度分别设定 `{weight, activation}`,并通过 `ignore` 列表以精确名或 `re:` 正则跳过特定层(注意 fused `qkv_proj` 需匹配未融合的 `q_proj/k_proj/v_proj`)。
5. **硬件后端选择**: `--linear-backend` 可在 `flashinfer` / `xpu` / `xpu_woq` / `torch` 等之间 pin 特定 kernel;`mxfp8` 要求 SM 100+ (Blackwell)才能跑 w8a8,其他 GPU 退化为 w8a16 fallback;XPU 上非 block FP8 scaled-mm 默认 W8A16,显式 `--linear-backend xpu` 强制 W8A8,`--linear-backend torch` 走 `torch._scaled_mm`。
6. **已量化 checkpoint 的激活覆盖**: 可针对 gpt-oss 之类 MXFP4 MoE checkpoint,通过 `quantization_config.moe.activation` 单独指定激活格式(例如切到 `mxfp8`),与 `--moe-backend` 协同锁定 kernel 家族。

---

## 【关键机制与数据】

- **工作原理(原文)**:"Weights are converted during model loading and activations are dynamically scaled during each forward pass."——即一次性离线式转换权重 + 在线动态处理激活的混合范式,避免了 calibration dataset 的依赖。
- **数据流**: BF16/FP16 模型 → 加载时按 scheme 规则转出低精度 weight + 对应 scale → 每前向传播对 activation 做动态量化(scaling) → 进入低精度 GEMM。
- **MXFP4 权重规范(原文)**: "fp4_e2m1 data, e8m0 per-1x32-block scale ([OCP MX specs](https://www.opencompute.org/documents/ocp-microscaling-formats-mx-v1-0-spec-final-pdf))"——遵守 OCP 微缩格式 MX v1.0 规范。
- **MXFP8 硬件门槛(原文)**:"Requires SM 100+ (Blackwell or newer) for w8a8, other GPUs use a w8a16 fallback"——非 Blackwell 设备只能做到 weight-only MXFP8。
- **Linear MXFP4 激活不确定性(原文)**:"Linear MXFP4 backend is auto-selected per platform, not enforcing activation dtype. Some use BF16 activation."——激活端既可能是 MXFP4 也可能是 BF16,具体取决于 platform 自动选的 backend。
- **XPU 上的 W8A16 默认(原文)**:"On XPU, non-block FP8 scaled-mm linear layers default to W8A16; setting `--linear-backend xpu` forces W8A8."——这一默认对未指定 backend 的 XPU 用户有性能含义。
- **小细节:Per-token activation 加速(原文)**:"On some GPUs (Ada, Hopper) linear activations use per-token scaling for better performance"——Ada / Hopper 上即便 `fp8_per_tensor` 也会在线性层激活上悄悄改用 per-token scaling。

---

## 【表格解读】

**原文 Supported Schemes 表格逐字还原**:

| Scheme | Weight recipe | Activation recipe | Notes |
| ------ | ------------- | ----------------- | ----- |
| `fp8_per_tensor` | fp8_e4m3 data, fp32 per-tensor scale | fp8_e4m3 data, fp32 per-tensor scale | On some GPUs (Ada, Hopper) linear activations use per-token scaling for better performance |
| `fp8_per_block` | fp8_e4m3 data, fp32 per-128x128-block scale | fp8_e4m3 data, fp32 per-1x128-block scale |  |
| `mxfp8` | fp8_e4m3 data, e8m0 per-1x32-block scale | fp8_e4m3 data, e8m0 per-1x32-block scale | Requires SM 100+ (Blackwell or newer) for w8a8, other GPUs use a w8a16 fallback |
| `mxfp4` | fp4_e2m1 data, e8m0 per-1x32-block scale ([OCP MX specs](https://www.opencompute.org/documents/ocp-microscaling-formats-mx-v1-0-spec-final-pdf)) | - linear: fp4_e2m1 data, e8m0 per-1x32-block scale in some backends, or BF16. <br> - MOE: fp4_e2m1 data, e8m0 per-1x32-block scale. | Linear MXFP4 backend is auto-selected per platform, not enforcing activation dtype. Some use BF16 activation. Use `--linear-backend` to pin one (e.g. `--linear-backend flashinfer`). |

**逐行解读**:

- **`fp8_per_tensor`**: 最简单的全局标度方案,weight 与 activation 都只各保留一个 fp32 scale;数据用 E4M3(FP8);Notes 提示在 Ada/Hopper 上,**linear 层的激活会被悄悄替换为 per-token 缩放**(注意:此时只有 linear 激活是 per-token,weight 仍是 per-tensor),用 `--quantization fp8_per_tensor` 的用户无需任何额外操作即可能享受加速。
- **`fp8_per_block`**: 细粒度 block 方案。weight 用 128×128 二维 block,activation 用 1×128 一维 block(即 per-token、每 128 个连续元素的列方向分块)。Notes 列为空,表示无额外平台差异。
- **`mxfp8`**: 走 OCP MX 路径的 FP8,weight/activation 都使用 1×32 的 `e8m0` 微缩块 scale(块大小 32 是 MX 规范硬性约束)。**硬件门槛明确:必须 SM 100+ (Blackwell)才能跑 w8a8,否则 activation 端降级为 16-bit (w8a16 fallback)**,意味着该 scheme 在 Ampere/Hopper 上实际只做权重量化。
- **`mxfp4`**: 极致压缩路径,weight 用 FP4(E2M1) + 1×32 e8m0 scale,严格遵循 OCP MX v1.0 规范。Activation 在表格中明显比前几行更复杂:
  - **linear 激活**: 取决于 platform 自动选的 backend,某些 backend 下用 MXFP4,某些用 BF16,**用户可用 `--linear-backend` 显式 pin**(例:`--linear-backend flashinfer`)。
  - **MOE 激活**: 固定为 MXFP4(fp4_e2m1 + e8m0 per-1x32-block scale),与 linear 不同,MOE 路径不受该后端不确定性影响。
  - Notes 还强调 **MXFP4 不强制 activation dtype**,即 backend 选择会真实影响 activation 精度,这是一个"非确定精度"的 scheme,使用前需要明确所选 backend 的行为。

---

## 【公式解读】

原文无公式。

---

## 【关联】

- **同模块(`QUANT_KEY_NAMES`)**: 文档明确指出 `linear.weight` / `linear.activation` / `moe.weight` / `moe.activation` 接受的"name"取值参考 `vllm/config/quantization.py` 中的 `QUANT_KEY_NAMES`,字符串简写解析顺序为先 `--quantization` shorthand 再 fallback 到该常量。
- **Linear backend 选择(下游 kernel)**: `--linear-backend` 在 `flashinfer` / `xpu` / `xpu_woq` / `torch` 之间切换;`xpu` 与 `xpu_woq` 决定 XPU 上 FP8 是 W8A8 还是 W8A16;`torch` 让 GEMM 走 `torch._scaled_mm` 而非定制 XPU kernel。这是文档涉及的核心横向开关。
- **MoE backend(下游 kernel)**: "Combine with `--moe-backend` to pin a specific kernel family." —— 与 `--linear-backend` 类似,MOE kernel 也可独立 pin,与 `quantization_config.moe` 字段协同工作。
- **已量化 checkpoint 通路**: 通过 `--quantization-config.moe.activation mxfp8` 可对 gpt-oss 这类 MXFP4 MoE 预量化模型单独覆盖 activation 格式,体现"online 量化与 offline 量化在同一 API 表面下共存"的设计意图。
- **Fused layer 命名(模型层细节)**: ignore 的 regex 必须匹配 fused `qkv_proj` 内部的 unfused shard 名(`q_proj` / `k_proj` / `v_proj`),这与 vLLM 的 layer fusion 机制耦合,说明 quantization 层与模型图重写层存在顺序依赖。
- **加载时量化 vs 推理时量化**: 文档本身只讲 online(加载时)路径,但 `Already-quantized checkpoints` 一节表明系统也支持把已量化 checkpoint 加载并对 activation 端单独覆盖,可见 quantization 子系统同时承担了"在线转换"与"预量化加载"两条路径的统一入口。

---

## 【使用方法】

**Python API 启用**:

```python
from vllm import LLM
llm = LLM("meta-llama/Llama-3.1-8B", quantization="fp8_per_tensor")
llm = LLM("meta-llama/Llama-3.1-8B", quantization="fp8_per_block")
llm = LLM("meta-llama/Llama-3.1-8B", quantization="mxfp8")
llm = LLM("meta-llama/Llama-3.1-8B", quantization="mxfp4")
llm = LLM("Qwen/Qwen3.5-35B-A3B", quantization="mxfp4",
          quantization_config={"linear": {"activation": None, "weight": None}})
```

**CLI 启用**:

```bash
vllm serve <model> --quantization fp8_per_tensor
vllm serve <model> --quantization fp8_per_block
vllm serve <model> --quantization mxfp8
vllm serve <model> --quantization mxfp4
vllm serve <model> --quantization mxfp4 \
    --quantization-config '{"linear":{"activation":null,"weight":null}}'
```

**高级配置(`quantization_config` Schema)**:

```yaml
quantization_config:
  linear:  { weight: <name>, activation: <name> }
  moe:     { weight: <name>, activation: <name> }
  ignore:  [ <layer-name-or-regex>, ... ]
```

- `linear` / `moe` 既可传完整 `{weight, activation}` dict,也可传裸字符串(先解析为 shorthand,失败则视为 weight name)。
- 未设置字段:回退到 `--quantization` shorthand 的默认;或对已量化 checkpoint,回退到 checkpoint 自带的声明。
- `ignore` 支持精确名与 `re:` 前缀正则;fused 层(`qkv_proj`)必须匹配 unfused shard 名。

**Dense 与 MoE 分层配置**:

```python
llm = LLM("ibm-granite/granite-3.0-1b-a400m-base",
          quantization="fp8_per_tensor",
          quantization_config={"linear": "fp8_per_block"})  # linear 改 per-block,moe 继承 shorthand

llm = LLM("ibm-granite/granite-3.0-1b-a400m-base",
          quantization="fp8_per_tensor",
          quantization_config={"moe": "fp8_per_block"})    # moe 改 per-block,linear 继承 shorthand
```

**针对已量化 checkpoint 的激活覆盖**(以 gpt-oss 为例):

```bash
vllm serve openai/gpt-oss-20b --quantization-config.moe.activation mxfp8
```

**CLI 的两种等效写法**:

```bash
vllm serve <model> --quantization-config '{"moe":{"activation":"mxfp8"}}'
vllm serve <model> --quantization-config.moe.activation mxfp8
```

**Linear backend pin**:

```bash
vllm serve <model> --quantization mxfp4 --linear-backend flashinfer
# XPU 相关:
#   --linear-backend xpu      → 强制 W8A8 (定制 XPU kernel)
#   --linear-backend xpu_woq  → 显式 W8A16 (weight-only)
#   --linear-backend torch    → 强制 W8A8,走 torch._scaled_mm
```

**MoE backend pin**(与 activation override 组合):

```bash
vllm serve <model> --quantization-config.moe.activation mxfp8 --moe-backend <backend>
```
