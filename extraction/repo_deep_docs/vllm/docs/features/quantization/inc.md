# Intel Quantization Support

> 仓 `vllm` · 路径 `docs/features/quantization/inc.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm/docs/features/quantization/inc.md

# 深度解读: docs/features/quantization/inc.md (Intel Quantization Support)

---

## 【定位】

本文档是 vLLM 对 **Intel AutoRound 量化算法** 的特性说明,解决"如何将 LLM 通过 Intel AutoRound 量化后,在 vLLM 中以高性能、低精度 (INT2–INT8、MXFP、NVFP、GGUF 等) 形式部署与评估"的问题,并给出从安装 → 量化 → 部署 → 评测的端到端操作链路。

---

## 【技术要点】

1. **量化算法核心**: AutoRound 是 Intel 推出的针对 LLM 的高级量化算法,支持 **INT2、INT3、INT4、INT8、MXFP8、MXFP4、NVFP4、GGUF** 等多种位宽/格式,并集成在 [Intel® Neural Compressor](https://github.com/intel/neural-compressor) 体系中。
2. **混合 Bit/Dtype 配方生成**: 支持在**几分钟**内自动完成 `Bits`/`Dtypes` 混合方案生成,支持 **Per-layer mixed-bit quantization** (逐层混合位) 细粒度控制,并提供三种 quantization recipes: **best、base、light**。
3. **导出格式支持**: 支持导出为 **AutoRound、AutoAWQ、AutoGPTQ、GGUF** 四种格式;同时具备 **RTN (Round-To-Nearest)** 快速量化模式,以及 **10+ vision-language models (VLMs)** 与 **10+ backends** 支持。
4. **Intel 平台当前已启用的 recipe**: vLLM 当前在 Intel 平台上支持 `W4A16` (weight-only, 4-bit 权重 + 16-bit 激活) 和 `W8A16` (weight-only, 8-bit 权重 + 16-bit 激活);其他 recipe/format 将后续版本支持。
5. **三档精度/速度权衡** (在 Python API 中以 nsamples/iters 体现):
   - **最高精度**: `nsamples=512, iters=1000`,外加 `low_gpu_mem_usage=True` 可**节省约 20G 显存但慢约 30%**,整体速度为基准的约 1/4–1/5 (即"4-5X slower")。
   - **轻量快速**: `nsamples=128, iters=50, lr=5e-3`,速度提升 **2-3X**,在 `W4G128` 上有轻微精度下降。
6. **端到端落地三步走**:
   - 安装: `uv pip install auto-round`
   - 量化: CLI 或 Python API,默认导出到 `./tmp_autoround`
   - 部署: `vllm serve` 加载 Intel 预量化模型
   - 评测: `lm_eval --model vllm` 接入量化模型

---

## 【关键机制与数据】

**1. 工作原理 (量化流程)**
- 原文描述的量化链路为: 安装 `auto-round` → 用 `auto-round` CLI 或 `AutoRound` Python 类对源模型 (例如 `Qwen/Qwen3-0.6B`) 做量化 → 通过 `quantize_and_save()` 以 `auto_round / auto_gptq / auto_awq` 三种 `format` 之一落盘 → 在 vLLM 中以 `vllm serve` 拉起服务 → 用 `lm_eval` 评估。
- CLI 与 Python API 共用同一组核心参数: `scheme`(如 `W4A16`)、`format`(默认 `auto_round`)、`bits`、`group_size`、`sym`,这些参数共同决定权重量化位宽、group 粒度与对称性。
- Python 注释中明确给出**精度-速度-显存**三方权衡:
  - 原文: "the best accuracy, 4-5X slower, low_gpu_mem_usage could save ~20G but ~30% slower"
  - 原文: "2-3X speedup, slight accuracy drop at W4G128"

**2. 数据流 (部署侧)**
- 部署命令读取的是已量化的预打包仓库 `Intel/DeepSeek-R1-0528-Qwen3-8B-int4-AutoRound`,通过 vLLM 启动 OpenAI 兼容服务,并显式控制:
  - `gpu-memory-utilization 0.8`
  - `max-model-len 4096`
- 评测侧以 `lm_eval` 直接对接 vLLM,通过 `--model_args` 透传模型仓库名及推理参数 (`max_model_len=8192, max_num_batched_tokens=32768, max_num_seqs=128, gpu_memory_utilization=0.8, dtype=bfloat16, max_gen_toks=2048`),任务为 `gsm8k`,`num_fewshot=5`,`batch_size=128`。

**3. 性能/能力数据 (均直接来自原文清单)**
- 原文 (Key Features 列表): "Delivers strong performance even at **2–3 bits**"
- 原文: "Automatically configure in **minutes**"
- 原文: 支持 **10+ vision-language models (VLMs)** 与 **10+ backends**
- 原文: 精度档位耗时差异 **4-5X slower** (高精度) 与 **2-3X speedup** (轻量)
- 原文: `low_gpu_mem_usage=True` 时节省显存约 **20G**,速度减慢约 **30%**

---

## 【表格解读】

**原文无表格。** (原文档全部内容以列表、代码块和说明文字形式组织,未出现参数表/性能对比表/配置项表格。)

如需对照 `W4A16` / `W8A16` 等 recipe 的差异,原文仅在文字段落中以项目符号方式列举,未以表格形式给出。

---

## 【公式解读】

**原文无公式。** (整篇文档未出现任何 LaTeX 公式或伪代码形式的算法表达式;量化算法细节需跳转至外链 [AutoRound step-by-step guide](https://github.com/intel/auto-round/blob/main/docs/step_by_step.md) 获取。)

---

## 【关联】

本文档显式涉及以下外部/上游组件,构成一条**量化 → 部署 → 评测**的依赖链:

1. **[AutoRound](https://github.com/intel/auto-round)** — 量化算法本身的实现仓库,负责 INT2–INT8、MXFP、NVFP、GGUF 等格式生成与导出 (auto_round / auto_awq / auto_gptq)。
2. **[Intel® Neural Compressor](https://github.com/intel/neural-compressor)** — AutoRound 隶属的工具链,提供底层压缩/量化基础设施。
3. **[AutoRound step-by-step guide](https://github.com/intel/auto-round/blob/main/docs/step_by_step.md)** — 进一步深入 AutoRound 用法的官方指南 (原文给出的"deeper introduction" 入口)。
4. **[2-3 bits example models](https://huggingface.co/collections/OPEA/2-3-bits)** — OPEA 在 HuggingFace 上提供的 2–3 bit 极低精度示例模型集合,用于验证 AutoRound 在低比特下的精度优势。
5. **vLLM 推理引擎** — 作为下游部署目标,通过 `vllm serve` 加载 Intel/DeepSeek-R1-0528-Qwen3-8B-int4-AutoRound 等预量化模型。
6. **lm_eval** — 评测框架,作为 vLLM 模型的下游消费者,通过 `pretrained=...` 形式把量化模型接入 `gsm8k` 等任务。
7. **上游预量化模型仓库** — `Intel/DeepSeek-R1-0528-Qwen3-8B-int4-AutoRound` 与源模型 `Qwen/Qwen3-0.6B`,体现 Intel 团队基于 Qwen 系列做 INT4 AutoRound 量化的产出链路。

文档本身处于 vLLM 量化特性体系的 **Intel 子树** 入口 (路径 `docs/features/quantization/inc.md`,"inc" 即 Intel Neural Compressor 的缩写),与同目录下的其他量化方案 (如 AWQ、GPTQ、BitsAndBytes、FP8 等) 平行,共享"quantize → serve → evaluate"的三段式流程范式。

---

## 【使用方法】

### 1. 安装 AutoRound

原文命令:
```bash
uv pip install auto-round
```

### 2. 通过 CLI 量化模型 (以 `Qwen/Qwen3-0.6B` 为例)

原文命令:
```bash
auto-round \
    --model Qwen/Qwen3-0.6B \
    --scheme W4A16 \
    --format auto_round \
    --output_dir ./tmp_autoround
```

### 3. 通过 Python API 量化模型

原文代码:
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
from auto_round import AutoRound

model_name = "Qwen/Qwen3-0.6B"
autoround = AutoRound(model_name, scheme="W4A16")

# the best accuracy, 4-5X slower, low_gpu_mem_usage could save ~20G but ~30% slower
# autoround = AutoRound(model, tokenizer, nsamples=512, iters=1000, low_gpu_mem_usage=True, bits=bits, group_size=group_size, sym=sym)

# 2-3X speedup, slight accuracy drop at W4G128
# autoround = AutoRound(model, tokenizer, nsamples=128, iters=50, lr=5e-3, bits=bits, group_size=group_size, sym=sym )

output_dir = "./tmp_autoround"
# format= 'auto_round'(default), 'auto_gptq', 'auto_awq'
autoround.quantize_and_save(output_dir, format="auto_round")
```

关键可调参数 (源自原文注释): `nsamples`、`iters`、`lr`、`bits`、`group_size`、`sym`、`low_gpu_mem_usage`;可导出 `format` 取值为 `auto_round` (默认) / `auto_gptq` / `auto_awq`。

### 4. 在 vLLM 中部署量化模型

原文命令:
```bash
vllm serve Intel/DeepSeek-R1-0528-Qwen3-8B-int4-AutoRound \
    --gpu-memory-utilization 0.8 \
    --max-model-len 4096
```

### 5. 用 lm_eval 评测 vLLM 上的量化模型

原文命令:
```bash
lm_eval --model vllm \
  --model_args pretrained="Intel/DeepSeek-R1-0528-Qwen3-8B-int4-AutoRound,max_model_len=8192,max_num_batched_tokens=32768,max_num_seqs=128,gpu_memory_utilization=0.8,dtype=bfloat16,max_gen_toks=2048" \
  --tasks gsm8k \
  --num_fewshot 5 \
  --batch_size 128
```

### 6. 当前已启用的 recipe (在 Intel 平台上)

- **`W4A16`**: weight-only, 4-bit 权重 + 16-bit 激活
- **`W8A16`**: weight-only, 8-bit 权重 + 16-bit 激活

(原文明确说明: "Additional recipes and formats will be supported in future releases.",其余 recipe/format 的具体启用步骤原文未涉及。)
