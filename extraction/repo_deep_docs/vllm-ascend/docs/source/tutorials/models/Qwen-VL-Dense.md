# Qwen-VL-Dense(Qwen3-VL-8B/32B)

> 仓 `vllm-ascend` · 路径 `docs/source/tutorials/models/Qwen-VL-Dense.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm-ascend/docs/source/tutorials/models/Qwen-VL-Dense.md

# 一体化深度解读:Qwen-VL-Dense(Qwen3-VL-8B/32B) 部署指南

> ⚠️ **解读前置说明**:原文在第 5.1 节「Atlas 300I DUO」的 `vllm serve` 命令行中部被截断(以 "exp" 结尾),后续的精度评测、性能调优、多节点部署、FAQ 等章节未在提供的原文片段中出现。下文严格基于已出现的原文内容进行解读,缺失章节在「关联」与「使用方法」中按原文元信息作显式标注。

---

## 【定位】

这篇文档是 vLLM-Ascend 镜像仓针对 **Qwen3-VL-Dense 系列多模态大模型(Qwen3-VL-8B-Instruct / Qwen3-VL-32B-Instruct 及其 w8a8 量化版)** 在华为昇腾 NPU(Atlas 800I A2 / Atlas 800 A3 / Atlas 300I DUO / Ascend950DT)上落地部署的端到端实操 Guide,覆盖模型权重获取、Docker / 源码两种安装路径、以及单节点在线推理服务(`vllm serve`)的启动命令模板。

---

## 【技术要点】

1. **模型与硬件版本基线**(原文):
   - 演示版本: vLLM-Ascend `v0.11.0rc3-a3`,以 `Qwen3-VL-8B-Instruct` 为示例展示单 NPU 与多 NPU 部署。
   - Atlas 推理产品: 需 vLLM-Ascend `v0.18.0` 或更高;Ascend950DT 上需 `vllm-ascend:v0.23.0rc1` 起;Atlas 推理产品上**禁用**演示版本。

2. **算力与显存门槛**(原文 §3.1):
   - `Qwen3-VL-8B-Instruct`: Atlas 800I A2 (64GB × 8)、Atlas 800 A3 (64GB × 16)、Atlas 300I DUO 各需 **1 卡**;Ascend950DT 系列 (96GB × 8) 节点亦需 1 卡(对应 w8a8 量化版)。
   - `Qwen3-VL-32B-Instruct`: Atlas 800I A2 / Atlas 800 A3 / Atlas 推理产品 各需 **2 卡**;Ascend950DT (96GB × 8) 节点需 1 卡(对应 w8a8 量化版)。
   - 推荐权重落地目录: 多节点共享目录,如 `/root/.cache/`。

3. **三种硬件分支的 Docker 镜像选择**(原文 §4.1):
   - Ascend950DT: `quay.io/ascend/vllm-ascend:|vllm_ascend_version|-#TODO`(原文占位符未补全),需暴露 8 个 davinci 设备及 davinci_manager / hisi_hdc / ummu / uburma。
   - A2 / A3: `quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}`(A3 后缀 `-a3`)。
   - Atlas 300I DUO: `quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}-310p`,且需 `--shm-size=10g`。

4. **在线服务启动参数骨架**(原文 §5.1,两种硬件变体):
   - Ascend950DT: 使用 `--quantization ascend` 加载 w8a8 量化权重。
   - A2 / A3: 使用 `--dtype bfloat16`。
   - 公共关键参数: `--max-num-seqs 128`、`--max-model-len 32768`、`--max-num-batched-tokens 16384`、`--gpu-memory-utilization 0.91`、`--mm-processor-cache-gb 0`、`--no-enable-prefix-caching`、`--trust-remote-code`、`--async-scheduling`、`--data-parallel-size $3`、`--tensor-parallel-size $4`,以及 `--served-model-name qwen3vl`。
   - CUDA Graph 编译配置(原文): `--compilation-config '{"cudagraph_mode": "FULL_DECODE_ONLY", "cudagraph_capture_sizes": [1,2,4,8,16,32]}'`。

5. **运行时环境变量**(原文 §5.1,三种硬件共用的前置 `export`):
   - `HCCL_OP_EXPANSION_MODE="AIV"`、`PYTORCH_NPU_ALLOC_CONF=expandable_segments:True`、`OMP_PROC_BIND=false`、`OMP_NUM_THREADS=1`、`TASK_QUEUE_ENABLE=1`、`ASCEND_RT_VISIBLE_DEVICES=$1`。

6. **Atlas 300I DUO 的源码安装特例**(原文 §4.2 注释):
   - 该平台不支持 `triton` 或 `triton-ascend`,源码安装若自动拉入需手动 `pip uninstall -y triton-ascend triton`。

---

## 【关键机制与数据】

### 数据流与工作原理(基于原文可推得)

**多模态推理链路**:Qwen-VL 系列接受 **图像 + 文本 + 边界框(bounding boxes)** 作为输入,产出 **文本 + 检测框(detection boxes)**,支撑图像检测、多模态对话、多图推理三大能力(原文 §1)。

**vLLM-Ascend 部署链路**:`vllm serve` 进程加载 HuggingFace/ModelScope 权重 → 通过 `--served-model-name qwen3vl` 注册 OpenAI 兼容 API → 利用 `--async-scheduling` 异步调度 + `--compilation-config` 的 `FULL_DECODE_ONLY` cudagraph 捕获尺寸 `[1,2,4,8,16,32]` 在预编译阶段固化 kernel,降低每次 decode 步的开销 → `--data-parallel-size` 与 `--tensor-parallel-size` 分别承担请求级并行与张量切分(原文 §5.1)。

**显存管理**:`--gpu-memory-utilization 0.91` 占用约 91% 设备显存,KV cache 占用 32K 上下文与 128 并发序列;`--mm-processor-cache-gb 0` 关闭多模态处理器缓存,适合长上下文视觉问答。

### 性能/容量相关数据(原文)

| 指标 | 原文数值 | 出处 |
|---|---|---|
| 并发序列上限 (`max-num-seqs`) | 128 | §5.1 命令行 |
| 单请求最大上下文 (`max-model-len`) | 32768 | §5.1 命令行 |
| 批处理 token 上限 (`max-num-batched-tokens`) | 16384 | §5.1 命令行 |
| 显存利用率 (`gpu-memory-utilization`) | 0.91 | §5.1 命令行 |
| Ascend950DT 单节点 8B 显存 | 96GB × 8 | §3.1 |
| A2 单机 8 卡 | 64GB × 8 | §3.1 |
| A3 单机 16 卡 | 64GB × 16 | §3.1 |
| 8B 模型所需 NPU 数 | 1 | §3.1 |
| 32B 模型所需 NPU 数 | 2 | §3.1 |
| Atlas 300I DUO 共享内存 | 10g | §4.1 |
| 其他分支共享内存 | 1g | §4.1 |

> 文档未给出吞吐量(tokens/s)、首 token 时延、显存峰值等具体 benchmark 数值,原文以"accuracy and performance evaluation"为后续章节标题但正文未提供。原文:"This document will show the main verification steps of the model, including supported features, feature configuration, environment preparation, NPU deployment, accuracy and performance evaluation."

---

## 【表格解读】

**原文无表格**。

(原文以 bulleted list 形式给出 §3.1 的硬件 / 权重清单,以代码块形式给出 §4 / §5 的命令,均未采用 markdown 表格结构。如需,可将 §3.1 的硬件清单按下方形式呈现,但严格意义上不属于"原文表格"的逐字还原:)

| 模型 | 硬件平台 | 所需 NPU 数 | 权重链接 |
|---|---|---|---|
| Qwen3-VL-8B-Instruct | Atlas 800I A2 (64GB×8) / Atlas 800 A3 (64GB×16) / Atlas 300I DUO | 1 | modelscope.cn/models/Qwen/Qwen3-VL-8B-Instruct |
| Qwen3-VL-8B-Instruct-w8a8(量化) | Ascend950DT 系列 (96GB×8) | 1 | modelscope.cn/models/Eco-Tech/Qwen3-VL-8B-Instruct-w8a8-mxfp8 |
| Qwen3-VL-32B-Instruct | Atlas 800I A2 (64GB×8) / Atlas 800 A3 (64GB×16) / Atlas 推理产品 | 2 | modelscope.cn/models/Qwen/Qwen3-VL-32B-Instruct |
| Qwen3-VL-32B-Instruct-w8a8(量化) | Ascend950DT 系列 (96GB×8) | 1 | modelscope.cn/models/Eco-Tech/Qwen3-VL-32B-Instruct-w8a8-mxfp8 |

---

## 【公式解读】

**原文无公式**。

(整篇文档均为配置/命令文本,未出现任何 LaTeX 数学表达式或伪代码公式。)

---

## 【关联】

基于原文显式提及的内部链接与上下文元信息:

| 链接 | 文档中的角色 | 关系性质 |
|---|---|---|
| [Supported Models](../../user_guide/support_matrix/supported_models.md) | §2 "Refer to ... to get the model's supported feature matrix" | 上游能力清单 → 本文档是该清单中 Qwen3-VL-Dense 的实操落地 |
| [Feature Guide](../../user_guide/feature_guide/index.md) | §2 "Refer to ... to get the feature's configuration" | 上游特性开关文档 → 解释 `--async-scheduling`、`--no-enable-prefix-caching` 等参数含义 |
| [Using Docker](../../getting_started/installation.md#installation-prebuilt-image) | §4.1 "refer to [using docker]..." | 通用镜像使用手册 → 本文档三段 `docker run` 是其特化 |
| [Installation Guide](../../getting_started/installation.md) | §4.2 末尾"For more details, please refer to..." | 通用安装手册 → 源码安装流程的兜底说明 |
| [Using lm-eval](../../developer_guide/evaluation/using_lm_eval.md) | 链接清单提供,正文未引用 | 下游精度评测工具 → 与原文 §1 承诺的"accuracy evaluation"对应 |
| [Using AIS-bench](../../developer_guide/evaluation/using_ais_bench.md) | 链接清单提供,正文未引用 | 下游性能压测工具 → 对应"performance evaluation" |
| [Optimization and Tuning](../../developer_guide/performance_and_debug/optimization_and_tuning.md) | 链接清单提供,正文未引用 | 下游调优指南 → 对 §5.1 命令参数的进一步解释 |
| [Feature Matrix](../../user_guide/support_matrix/feature_matrix.md) | 链接清单提供,正文未引用 | 横向特性矩阵 → 与 supported_models.md 互补 |
| [FAQs](../../faqs.md) | 链接清单提供,正文未引用 | 常见问题 → 与本指南版本选择、Atlas 300I DUO 限制等问题衔接 |

**上下游关系链**:
```
supported_models.md (能力登记)
        ↓
本指南 Qwen-VL-Dense.md (实施路径)
        ↓  ├─→ installation.md (环境)
        ↓  ├─→ feature_guide/index.md (参数含义)
        ↓  ├─→ using_lm_eval.md / using_ais_bench.md (验证)
        ↓  └─→ optimization_and_tuning.md / faqs.md (调优与排障)
```

**模块内聚点**:本文档与 vLLM-Ascend 的 `vllm serve` 入口、`Qwen-VL` multimodal processor、`HCCL` 集合通信(`AIV` 扩展模式)三个模块强耦合。

---

## 【使用方法】

### 启动前必备(原文 §3 + §4)

- **硬件匹配**:8B 用 1 卡,32B 用 2 卡,Atlas 推理产品必须用 vLLM-Ascend ≥ `v0.18.0`,Ascend950DT 用 ≥ `vllm-ascend:v0.23.0rc1`。
- **权重下载**:ModelScope 链接见原文 §3.1;推荐存放到 `/root/.cache/`。
- **镜像选择**:三选一镜像 tag 见原文 §4.1。
- **验证**:`docker ps | grep vllm-ascend` 应显示 `Up`;`pip show vllm-ascend` 应显示已拉取版本。

### 单节点在线服务(原文 §5.1 命令模板)

环境变量统一前置:
```bash
export HCCL_OP_EXPANSION_MODE="AIV"
export PYTORCH_NPU_ALLOC_CONF=expandable_segments:True
export OMP_PROC_BIND=false
export OMP_NUM_THREADS=1
export TASK_QUEUE_ENABLE=1
export ASCEND_RT_VISIBLE_DEVICES=$1
```

**Ascend950DT(量化版)**:`vllm serve Qwen/Qwen3-VL-8B-Instruct --host 0.0.0.0 --port $2 --quantization ascend --served-model-name qwen3vl --no-enable-prefix-caching --data-parallel-size $3 --tensor-parallel-size $4 --trust-remote-code --max-num-seqs 128 --max-model-len 32768 --max-num-batched-tokens 16384 --gpu-memory-utilization 0.91 --async-scheduling --compilation-config '{"cudagraph_mode": "FULL_DECODE_ONLY", "cudagraph_capture_sizes": [1,2,4,8,16,32]}' --mm-processor-cache-gb 0`

**A2 / A3(bf16 版)**:把 `--quantization ascend` 替换为 `--dtype bfloat16`,其余参数完全一致。

**Atlas 300I DUO**:原文命令在 `--dtype bfloat16` 之后被截断(以 "exp" 结尾),参数骨架应与 A2/A3 一致但镜像后缀为 `-310p`,且 Docker 启动需 `--shm-size=10g` 与 8 个 davinci 设备透传。**原文未涉及完整命令**。

### 端口与多卡参数占位符(原文)

- `$1` → `ASCEND_RT_VISIBLE_DEVICES` 取值(如 `0,1`)
- `$2` → 服务监听端口(如 `8000`,与 Docker `-p 8000:8000` 对齐)
- `$3` → 数据并行度(`--data-parallel-size`)
- `$4` → 张量并行度(`--tensor-parallel-size`)

### 缺失章节(原文未涉及,但在文档引言中承诺)

- 5.2 多节点在线部署(原文 §1 提到 "single NPU and multi-NPU deployment",但 §5.1 之后无内容)
- 6 精度评测(原文未给出 lm-eval / AIS-bench 的具体评测命令)
- 7 性能评测 / 调优(原文未给出 throughput、TTFT 等指标,亦未引用 optimization_and_tuning.md 的具体段落)
- 8 常见问题(链接清单提供 `faqs.md`,正文未引用具体条目)

> 上述章节需结合同仓 `developer_guide/evaluation/` 与 `performance_and_debug/` 下的姊妹文档补全。
