# FP8 ViT Encoder Attention

> 仓 `vllm` · 路径 `docs/features/quantization/fp8_vit_attn.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm/docs/features/quantization/fp8_vit_attn.md

# FP8 ViT Encoder Attention 文档深度解读

## 【定位】

本文档描述 vLLM 针对视觉语言模型中 **ViT (Vision Transformer) 编码器注意力层** 的 **FP8 量化能力** —— 当处理大图 (QHD/4K) 而文本侧已被量化 (如 NVFP4) 时, ViT 编码器会成为瓶颈, FP8 注意力可在 NVIDIA (FlashInfer cuDNN) 与 AMD (AITER) 平台上以极小的精度损失换取显著的速度收益。

---

## 【技术要点】

1. **作用范围**: 仅覆盖 **ViT 编码器注意力** (Q/K/V 在 attention 调用前被量化到 FP8), 不涉及文本解码器; **当前仅支持 Qwen3-VL 系列模型** (`qwen3_vl`、`qwen3_vl_moe`、`qwen3_5`、`qwen3_5_moe` 及采用 Qwen3 ViT 的其他模型)。

2. **平台后端**:
   - **NVIDIA**: FlashInfer cuDNN 后端, 要求 **cuDNN ≥ 9.17.1**。
   - **AMD ROCm**: AITER, 需支持 `flash_attn_varlen_fp8_pertensor_func`, 运行于 **gfx942 (MI300) 或 gfx950 (MI350)**; 原生支持 packed variable-length 图/视频批次。

3. **两种 scale 策略**:
   - **动态 (dynamic)**: 默认, 用 **16 项循环缓冲 (circular buffer)** 累计观测到的 Q/K/V amax, 每个 forward 都更新 scale; 匹配 BF16 精度但有 per-forward 开销。
   - **静态 (static, 推荐生产)**: 用代表性数据 **一次性校准**, 之后复用; scale 还会乘以 **`--mm-encoder-fp8-scale-save-margin` (默认 1.5)** 以保留对校准集外异常值的余量。

4. **量化开销**: 每次 FP8 注意力调用需 **3 次量化 kernel launch + un-padding**, 小图场景下这部分开销可能抵消收益。

5. **限制**: 动态 scale **与 ViT 完整 CUDA graph 不兼容**; FP8 tensor-core 加速在 **GB300 上比 GB200 更显著**。

6. **精度验证**: 在 ChartQA (Qwen3-VL-8B-Instruct, 500 样本) 上, FP8 动态与静态 scale 的 relaxed_accuracy / anywhere_accuracy / exact_match 三个指标与 BF16 在统计噪声范围内一致; 用 VisionArena-Chat 校准的 scale 在 ChartQA 上仍能保持 BF16 精度。

---

## 【关键机制与数据】

### 工作原理

- **数据流**: ViT 视觉块 (例如 `visual.blocks.0.attn.attn`) 的 Q/K/V 在 attention kernel 调用前被量化为 FP8; 若启用静态模式, 直接加载预先校准好的 per-tensor scale (q/k/v 各一个); 若启用动态模式, kernel 内部维护 **16 项循环缓冲** 持续观测 amax 并实时更新 scale。
- **校准流程**: `vllm bench mm-processor` 在 16 个 pass 内运行动态量化, 之后将学习到的 scale **dump 为 JSON**; 加载时再乘以 margin 系数。
- **多模态前端** (mm-processor) 负责产出 ViT 编码器的输入张量与变长布局, varlen 注意力使得不同分辨率 / 不同图像数的请求可以在同一批处理中高效执行。

### 性能数据 (原文给出, 标注数字来源)

- 原文: GB200 核心 cuDNN kernel (head_dim=128, seq_len=8192) BF16 = 350 µs / FP8 = 312 µs → **1.12×**; GB300 BF16 = 300 µs / FP8 = 211 µs → **1.42×**。
- 原文: Qwen3-VL-30B-A3B-Instruct, GB200, **3 images/request** 端到端 ViT 前向: HD (720×1280) FP8 **慢于** BF16 (0.87×); FullHD (~1080×1920) 几乎持平; QHD (1440×2560) FP8 1.08×; 4K (2160×3840) FP8 1.18× → **crossover ≈ FullHD with 3 images/request**。
- 原文: MI300X 上完整 AITER 调用 (BF16 输入, 16 heads, head_dim=72) 在 seq_len ∈ {2304, 4096, 8192, 16384} 测得 speedup 为 **1.38× / 1.06× / 1.08× / 1.13×**, FP8 分支已包含 Q/K/V 量化开销。

---

## 【表格解读】

### 表 1: Core cuDNN attention kernel (GB200/GB300)

| Hardware | BF16 | FP8 | Speedup |
| -------- | ---- | ---- | ------- |
| GB200 | 350 us | 312 us | **1.12x** |
| GB300 | 300 us | 211 us | **1.42x** |

逐行解读:
- **GB200**: 纯 attention kernel 在 head_dim=128, seq_len=8192 时从 350 µs 降至 312 µs, 加速 **1.12×**, 提升较为温和。
- **GB300**: 同样条件下 FP8 直接降至 211 µs, **1.42×**; 表明新版 Blackwell 架构的 FP8 tensor-core 收益远高于 GB200。

### 表 2: End-to-end encoder forward time (Qwen3-VL-30B-A3B-Instruct, GB200, 3 images/request)

| Resolution | BF16 median | FP8 median | Speedup |
| ---------- | ----------- | ---------- | ------- |
| HD (720x1280) | 31.77 ms | 36.39 ms | 0.87x |
| FullHD (1080x1920) | 57.99 ms | 58.73 ms | ~same |
| QHD (1440x2560) | 131.83 ms | 122.30 ms | **1.08x** |
| 4K (2160x3840) | 543.44 ms | 460.31 ms | **1.18x** |

逐行解读:
- **HD**: FP8 反倒慢 13%, 量化 kernel launch 与 un-padding 开销压倒 attention 收益。
- **FullHD**: 与 BF16 几乎持平, 即文中所谓的 crossover 点。
- **QHD**: 开始出现正向收益, **1.08×**, 此时 attention 计算量已显著大于量化开销。
- **4K**: 收益扩大至 **1.18×**, 大图像下 FP8 性价比最佳。

### 表 3: Complete AITER attention call on MI300X (16 heads, head_dim=72)

| Sequence length | AITER BF16 | AITER FP8 | Speedup |
| --------------- | ---------- | --------- | ------- |
| 2304 | 0.467 ms | 0.337 ms | **1.38x** |
| 4096 | 0.812 ms | 0.764 ms | **1.06x** |
| 8192 | 2.555 ms | 2.364 ms | **1.08x** |
| 16384 | 9.769 ms | 8.655 ms | **1.13x** |

逐行解读:
- **seq_len=2304**: 短序列却达到 **1.38×** 最高加速比, 与 GB200 端到端结果不同 — 此处 AITER FP8 已把 Q/K/V 量化开销含入, 但其 FP8 kernel 在 MI300 上对小长度仍非常高效。
- **seq_len=4096**: 加速比回落至 **1.06×**, 与 NVIDIA 端在中段序列上的趋势一致。
- **seq_len=8192**: **1.08×**, 与上表同长度量级一致。
- **seq_len=16384**: **1.13×**, 长序列下 FP8 收益稳定回升。

### 表 4: Accuracy on ChartQA (Qwen3-VL-8B-Instruct, 500 samples)

| Metric | BF16 | FP8 dynamic | FP8 static |
| ------ | ---- | ----------- | ---------- |
| relaxed_accuracy | 0.780 | 0.776 | 0.780 |
| anywhere_accuracy | 0.806 | 0.816 | 0.814 |
| exact_match | 0.584 | 0.582 | 0.578 |

逐行解读:
- **relaxed_accuracy**: BF16 = 0.780, 动态 FP8 = 0.776 (-0.004), 静态 FP8 = 0.780 (与 BF16 完全相同); 静态方案在精度上与 BF16 等价。
- **anywhere_accuracy**: BF16 = 0.806, 动态 = 0.816 (+0.010), 静态 = 0.814 (+0.008); 两种 FP8 模式甚至略高于 BF16, 属统计噪声内波动。
- **exact_match**: BF16 = 0.584, 动态 = 0.582 (-0.002), 静态 = 0.578 (-0.006); 差距均在千分位, 属统计噪声。
- 综合三行可得出文中结论: 静态 scale **在不同数据集间可泛化** (VisionArena-Chat 校准 → ChartQA 推理)。

---

## 【公式解读】

原文无公式。

(校准 scale 的使用方式为 "Saved scales are multiplied by `--mm-encoder-fp8-scale-save-margin`", 即 `final_scale = saved_scale × margin`, 但原文未以数学式给出, 因此不在此节展开。)

---

## 【关联】

文档显式涉及的上下游依赖与互操作关系如下:

- **上游触发**: 由多模态处理器 (`vllm bench mm-processor`) 在校准阶段驱动, 产出 scale JSON。
- **下游消费**: `vllm serve` 启动时通过 `--mm-encoder-fp8-scale-path` 加载静态 scale, 在 ViT 编码器注意力层 (`visual.blocks.*.attn.attn`) 中生效。
- **后端依赖**:
  - NVIDIA 侧对接 **FlashInfer cuDNN backend** (`flashinfer` Python 库 + cuDNN ≥ 9.17.1)。
  - AMD 侧对接 **AITER**, 使用 `flash_attn_varlen_fp8_pertensor_func` 与 packed varlen 接口。
- **与文本侧量化的协同**: 当文本模型采用 NVFP4 等更激进量化时, ViT attention 常成为剩余瓶颈, FP8 ViT 即是为平衡端到端延迟而引入的"补位"能力。
- **与 CUDA Graph 的不兼容**: 动态 scale 模式与 ViT full CUDA graphs 互斥, 启用动态 FP8 时需要回退到非 graph 执行或切换到静态 scale。
- **模型覆盖**: 与 Qwen3-VL 家族模型 (`qwen3_vl` / `qwen3_vl_moe` / `qwen3_5` / `qwen3_5_moe` 及基于 Qwen3 ViT 的派生模型) 紧耦合; 其他 VLM 的 ViT 当前不在支持范围。

---

## 【使用方法】

### 启用 FP8 ViT attention (动态 scale, 默认)

NVIDIA:
```bash
vllm serve $MODEL \
    --mm-encoder-attn-backend FLASHINFER \
    --mm-encoder-attn-dtype fp8
```

AMD ROCm:
```bash
vllm serve $MODEL \
    --mm-encoder-attn-backend ROCM_AITER_FA \
    --mm-encoder-attn-dtype fp8
```

### 生产推荐: 校准一次, 静态复用

Step 1 — 校准并保存 scale (内部会先跑 16 pass 动态量化, 再 dump scale):
```bash
vllm bench mm-processor \
    --model $MODEL --mm-encoder-attn-backend $MM_ATTN_BACKEND \
    --mm-encoder-attn-dtype fp8 \
    --mm-encoder-fp8-scale-save-path /path/to/scales.json \
    --dataset-name hf --dataset-path lmarena-ai/VisionArena-Chat \
    --num-prompts 100
```

Step 2 — 使用静态 scale 启动服务 (无动态开销):
```bash
vllm serve $MODEL \
    --mm-encoder-attn-backend $MM_ATTN_BACKEND \
    --mm-encoder-attn-dtype fp8 \
    --mm-encoder-fp8-scale-path /path/to/scales.json
```

### 关键配置项汇总

| 配置项 | 含义 |
| ------ | ---- |
| `--mm-encoder-attn-dtype fp8` | 启用 ViT encoder 注意力 FP8 量化 |
| `--mm-encoder-attn-backend FLASHINFER` | NVIDIA 平台选择 FlashInfer cuDNN 后端 |
| `--mm-encoder-attn-backend ROCM_AITER_FA` | AMD 平台选择 AITER 后端 |
| `--mm-encoder-fp8-scale-save-path` | 校准时保存 scale 的 JSON 路径 |
| `--mm-encoder-fp8-scale-path` | 推理时加载静态 scale 的 JSON 路径 |
| `--mm-encoder-fp8-scale-save-margin` | 默认 `1.5`, 用于为校准集外异常值留余量 |
| `--num-prompts` (bench 子命令) | 校准用 prompt 数 (示例用 100) |
| `--dataset-name hf` / `--dataset-path` | 校准数据集来源 (示例 `lmarena-ai/VisionArena-Chat`) |

### Scale 文件格式

```json
{
    "visual.blocks.0.attn.attn": {"q": 224.0, "k": 198.0, "v": 210.0},
    "visual.blocks.1.attn.attn": {"q": 218.0, "k": 195.0, "v": 207.0}
}
```
键名 `q_scale` / `k_scale` / `v_scale` 与 `q` / `k` / `v` 等价, 均可被接受。
