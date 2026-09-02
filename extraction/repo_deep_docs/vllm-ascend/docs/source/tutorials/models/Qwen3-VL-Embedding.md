# Qwen3-VL-Embedding

> 仓 `vllm-ascend` · 路径 `docs/source/tutorials/models/Qwen3-VL-Embedding.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm-ascend/docs/source/tutorials/models/Qwen3-VL-Embedding.md

# Qwen3-VL-Embedding 文档深度解读

## 【定位】

本文档是 vllm-ascend 镜像仓库针对 Qwen3-VL-Embedding / Qwen3-VL-Reranker 多模态检索模型系列在华为 Ascend NPU 上的端到端部署指南，覆盖权重获取、Docker/源码安装、在线服务部署、功能验证、MTEB 精度评估与 vLLM 性能压测全流程。

---

## 【技术要点】

1. **模型族与输入模态**：Qwen3-VL-Embedding / Qwen3-VL-Reranker 基于开源 Qwen3-VL 基座，专为多模态信息检索与跨模态理解设计，**接受文本、图像、截图、视频及其混合输入**。
2. **可选模型规格**：`Qwen3-VL-Embedding-8B` 与 `Qwen3-VL-Embedding-2B` 两种规模，权重从 ModelScope 下载，建议存放于多节点共享目录 `/root/.cache/`。
3. **三类硬件平台差异化支持**：A3 系列（标签 `-a3`）、A2 系列（默认标签）、Atlas 300I DUO（标签 `-310p`），通过 Docker 镜像 tag 区分。
4. **核心推理模式**：`--runner pooling`（vLLM 的 pooling runner，用于 embedding 类推理，而非常规 generate runner），端口固定 `8000`，`--max-model-len 1024`。
5. **Atlas 300I DUO 专属配置**：因硬件流受限，需额外指定 `--compilation-config '{"cudagraph_capture_sizes": [1024,512]}'`、`--additional-config '{"ascend_compilation_config": {"fuse_norm_quant": false}}'`、`--dtype float16`。
6. **服务接口形态**：OpenAI 兼容的 `/v1/embeddings` 端点，可直接通过 `curl -X POST` 调用验证；精度评估经 MTEB 的 `VllmEncoderWrapper` 接入；性能评估使用 `vllm bench serve` 子命令配合 `--backend openai-embeddings` 与 `--endpoint /v1/embeddings`。

---

## 【关键机制与数据】

- **工作原理**（原文：Pooling 推理路径）：Qwen3-VL-Embedding 经 vLLM 的 **pooling runner** 加载，调用 `/v1/embeddings` 接口对单条或多条输入返回 embedding 向量；Atlas 300I DUO 因 NPU 流受限，通过限定 `cudagraph_capture_sizes = [1024, 512]` 与关闭 `fuse_norm_quant` 来规避编译/显存问题。
- **数据流**（原文：`POST http://localhost:8000/v1/embeddings`）：请求体为 JSON `{"input": ["...", "..."]}` → 响应 JSON 包含 `id / object / created / model / data[].embedding / usage` 字段。
- **典型响应样例**（原文）：
  - 第 0 条 embedding 前两维：`[-0.028474265709519386, -0.02678542211651802]`
  - 第 1 条 embedding 前两维：`[-0.016785264015197754, -0.003787524998188019]`
  - `usage`： `prompt_tokens=39, total_tokens=39, completion_tokens=0, prompt_tokens_details=null`
  - `id` 示例：`embd-8136155c01e8411d`；`created`：`1784538286`。
- **OOM 风险机制**（原文：第 5 节"Key Parameter Descriptions"）：Atlas 300I DUO 上 `--max-model-len` 过大时会触发 `O(max_model_len^2)` 量级的 attention mask 显存消耗，可能引发 NPU OOM；文档显式建议保守值 `--max-model-len 1024`。
- **MTEB 精度评估配置**（原文：第 7 节代码块）：使用 `VllmEncoderWrapper("/root/.cache/Qwen3-VL-Embedding-2B", revision="norm", dtype="float16", max_model_len=10240)`；`encode_kwargs={"batch_size": 2}`；评估任务示例 `LeCaRDv2`。
- **性能压测参数**（原文：第 8 节命令）：`--dataset-name random`、`--random-input 200`，通过 `--save-result --result-dir ./` 保存结果。

> 注：原文未提供具体性能数字（如 throughput、latency、QPS），仅描述命令；具体数值需读者执行后自行产出。

---

## 【表格解读】

**原文无表格。** 文档仅以代码块形式给出三段 Docker 启动命令（A3 / A2 / Atlas 300I DUO）、两段 `vllm serve` 启动命令，以及 curl 验证命令与 Python 评估脚本，未使用任何 markdown 表格。

---

## 【公式解读】

**原文无公式。** 文档仅在文字描述中提及注意力 mask 的规模量级 `O(max_model_len^2)`（属复杂度说明而非公式表达），未给出任何 LaTeX 或伪代码形式数学式。

---

## 【关联】

依据文末提供的内部链接清单，文档与以下模块/特性相互引用：

- **../../user_guide/support_matrix/supported_models.md** — 第 2 节"Supported Features"指向此文件，用于查询 Qwen3-VL-Embedding 在 Ascend 上的**功能支持矩阵**（即当前模型在 Ascend 上已支持哪些 vLLM 特性）。
- **../../getting_started/installation.md#installation-prebuilt-image** — 第 4.1 节引用此锚点，对应**Docker 预构建镜像的使用说明**，是 A3 / A2 / Atlas 300I DUO 三种 `docker run` 命令的前置依赖。
- **../../getting_started/installation.md** — 第 4.2 节"Source Code Installation"指向此文件，对应**源码安装 vllm-ascend** 的完整步骤（适用于不愿使用 Docker 的用户，且多节点部署需在每个节点执行）。
- **../../faqs.md**（两处引用） — 第 5 节末"Common Issues Tip"和第 9 节"FAQ"均指向此文件，作为**环境、安装与通用参数问题**的统一故障排查入口。

外部资源关联：
- **ModelScope 模型权重页**：`Qwen/Qwen3-VL-Embedding-8B` 与 `Qwen/Qwen3-VL-Embedding-2B`，为唯一权重下载源。
- **MTEB 官方文档**（`https://docs.mteb.org/`）与 **`vllm-pooling/embed` 示例目录**：分别用于第 7 节精度评估与第 6 节功能验证的扩展用法。
- **vLLM Benchmark CLI 文档**（`https://docs.vllm.ai/en/latest/benchmarking/cli/`）：第 8 节 `vllm bench serve` 的参数详解出处。

整体链路：**[Supported Models 矩阵] → [权重获取 ModelScope] → [Docker 或 源码安装 vllm-ascend] → [vllm serve + pooling runner] → [/v1/embeddings 接口验证] → [MTEB 精度 / vLLM 性能评估] → [FAQs 故障排查]**。

---

## 【使用方法】

> 以下命令均按原文逐字保留。

### ① 拉取 Docker 镜像（按硬件选择 tag）

```shell
# A3 系列
export IMAGE=quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}-a3
# A2 系列
export IMAGE=quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}
# Atlas 300I DUO
export IMAGE=quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}-310p
```

随后执行三平台通用的 `docker run`（挂载 `/root/.cache`、Ascend 设备 `/dev/davinci0` 等，详见原文第 4.1 节）。

### ② 启动 Embedding 在线服务

**A3 / A2 系列**：
```shell
vllm serve Qwen/Qwen3-VL-Embedding-2B  \
  --served-model-name Qwen/Qwen3-VL-Embedding-2B  \
  --runner pooling \
  --port 8000 \
  --max-model-len 1024
```

**Atlas 300I DUO**（额外三参数）：
```shell
vllm serve Qwen/Qwen3-VL-Embedding-2B  \
  --served-model-name Qwen/Qwen3-VL-Embedding-2B  \
  --compilation-config '{"cudagraph_capture_sizes": [1024,512]}' \
  --additional-config '{"ascend_compilation_config": {"fuse_norm_quant": false}}' \
  --runner pooling \
  --dtype float16 \
  --port 8000 \
  --max-model-len 1024
```

### ③ 功能验证

```bash
curl -X POST http://localhost:8000/v1/embeddings -H "Content-Type: application/json" -d '{
  "input": [
        "The capital of China is Beijing.",
        "Gravity is a force that attracts two bodies towards each other. It gives weight to physical objects and is responsible for the movement of planets around the sun."
    ]
}'
```
预期：HTTP 200，返回 `embedding` 字段含浮点向量数组。

### ④ MTEB 精度评估

```python
import os
import mteb
from mteb.models.vllm_wrapper import VllmEncoderWrapper

if __name__ == "__main__":
    data_path = "/home/data/mteb_data"
    os.environ["HF_DATASETS_CACHE"] = data_path
    os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

    model = VllmEncoderWrapper(f"/root/.cache/Qwen3-VL-Embedding-2B",
                                revision="norm",
                                dtype="float16",
                                max_model_len=10240,
                               )
    cache = mteb.ResultCache("/home/data/mteb_data")
    tasks = mteb.get_tasks(tasks=["LeCaRDv2"])
    results = mteb.evaluate(model, tasks=tasks, cache=cache,
                            encode_kwargs={"batch_size": 2},
                            overwrite_strategy="always")
    df = results.to_dataframe()
    print(df)
```

### ⑤ 性能压测

```bash
vllm bench serve --model Qwen/Qwen3-VL-Embedding-2B \
  --backend openai-embeddings --port 8000 \
  --dataset-name random --endpoint /v1/embeddings \
  --random-input 200 --save-result --result-dir ./
```

### 关键参数说明（原文逐字摘要）

- `--runner pooling`：启用 vLLM pooling runner，对应 embedding 类推理路径。
- `--max-model-len`：单请求输入 + 输出上下文上限；Atlas 300I DUO 上过大可能触发 NPU OOM（attention mask 占 `O(max_model_len^2)`），文档建议显式保守值 `--max-model-len 1024`。
- `--compilation-config '{"cudagraph_capture_sizes": [1024,512]}'`：Atlas 300I DUO 专属，因硬件流受限而限制 cudagraph capture 尺寸。
- `--additional-config '{"ascend_compilation_config": {"fuse_norm_quant": false}}'`：Atlas 300I DUO 专属，关闭 norm+quant 融合以规避编译问题。
- `--dtype float16`：Atlas 300I DUO 专属显式指定精度。

### 故障排查入口

遇环境、安装、通用参数问题时，统一回溯至 **[../../faqs.md](../../faqs.md)**（文档第 5 节末与第 9 节两处显式引导）。
