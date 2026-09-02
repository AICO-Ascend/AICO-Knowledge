# Qwen3-Embedding

> 仓 `vllm-ascend` · 路径 `docs/source/tutorials/models/Qwen3-Embedding.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm-ascend/docs/source/tutorials/models/Qwen3-Embedding.md

# Qwen3-Embedding 文档深度解读

## 【定位】
本篇文档是 vLLM Ascend 项目下针对 **Qwen3 Embedding 模型系列** (0.6B/4B/8B 三种规格) 的部署与运行 guide, 解决"如何在 Ascend NPU 硬件 (A2/A3/Atlas 300I DUO) 上, 通过 vLLM Ascend 加载 Qwen3-Embedding 并对外提供 OpenAI 兼容的 embeddings 接口, 以及如何做精度和性能评估"的问题。

---

## 【技术要点】

1. **模型规格与版本门槛**: Qwen3 Embedding 是基于 Qwen3 密集基模型构建的专有 embedding/reranking 模型系列, 提供 0.6B / 4B / 8B 三种尺寸; **仅 vLLM Ascend 0.9.2rc1 及以上版本支持**该模型。
2. **三类硬件分支的镜像差异**:
   - A3 系列 → `quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}-a3`
   - A2 系列 → `quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}`
   - Atlas 300I DUO → `quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}-310p`
3. **运行时模式**: 必须显式声明 `--runner pooling` 切换到 pooling 推理路径, 而非默认的 generate 路径; `--max-model-len 1024` 用于限定单请求的最大 context length。
4. **Atlas 300I DUO 专属参数**:
   - `--compilation-config '{"cudagraph_capture_sizes": [1024,512]}'`: 因硬件 stream 数量受限, 限制 cudagraph 捕获尺寸。
   - `--additional-config '{"ascend_compilation_config": {"fuse_norm_quant": false}}'`: 关闭 norm-quant 融合。
   - `--dtype float16`: 显式指定 fp16。
5. **OOM 防护**: `--max-model-len` 的 attention mask 分配量级为 O(max_model_len²), Atlas 300I DUO 若自动解析到大 context, 易触发 NPU OOM, 因此文档**强制要求显式设定保守值 (例如 1024)**。
6. **评估体系**:
   - 精度评估走 MTEB (示例任务 `LeCaRDv2`), 使用 `VllmEncoderWrapper` 包装, `max_model_len=10240`, `batch_size=2`。
   - 性能评估走 `vllm bench serve`, `--backend openai-embeddings` 配合 `--endpoint /v1/embeddings`, `--random-input 200` 构造随机输入。

---

## 【关键机制与数据】

### 工作原理
- **推理范式**: Embedding 模型不走自回归 generate, 而是 forward 一次后取 pooled 表示, 所以服务端配置 `--runner pooling`, 启动 vllm serve 后开放 `POST /v1/embeddings` 端点 (OpenAI Embeddings 兼容协议)。
- **多节点数据流**: 模型权重下载到多节点共享目录 (推荐 `/root/.cache/`), Docker 通过 `-v /root/.cache:/root/.cache` 挂载, 各节点均可访问同一份权重, 避免重复下载。

### 关键运行数据 (原文)
- 服务端口: `--port 8000`
- 示例请求的 token 统计: `prompt_tokens=39`, `total_tokens=39`, `completion_tokens=0` (见第 6 节期望输出 JSON)。
- MTEB 评估中: `max_model_len=10240`, `encode_kwargs={"batch_size": 2}`, 缓存路径 `/home/data/mteb_data`。
- Benchmark 中: `--random-input 200` (随机生成 200 个输入), `--result-dir ./` (结果输出到当前目录)。

### 兼容性矩阵入口
- 文档第 2 节指向 `supported_models.md`, 该矩阵列出每个模型所支持的 vLLM 特性 (如是否支持 `--runner pooling`、是否支持 LoRA、量化方案等), 本文档不直接展开该矩阵, 仅引用。

---

## 【表格解读】

**原文无表格**。本文档的"表格化"信息以三种 Docker 镜像标签的并列代码块形式呈现 (A3 / A2 / Atlas 300I DUO 三选一), 以及两条 vllm serve 命令的并列代码块, 均为 `=== "..."` markdown tab 语法, 而非真正的 markdown 表格。

为辅助理解, 将其转写为参数对照表如下 (内容**全部来自原文**, 仅做排版整理):

| 硬件平台 | Docker 镜像标签 | 必加额外参数 (与 A3/A2 系列相比) |
|---|---|---|
| A3 series | `quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}-a3` | (无) |
| A2 series | `quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}` | (无) |
| Atlas 300I DUO | `quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}-310p` | `--compilation-config '{"cudagraph_capture_sizes": [1024,512]}'`、`--additional-config '{"ascend_compilation_config": {"fuse_norm_quant": false}}'`、`--dtype float16` |

| 启动项 | A3/A2 series 命令 | Atlas 300I DUO 命令 |
|---|---|---|
| 模型名 | `Qwen/Qwen3-Embedding-0.6B` | `Qwen/Qwen3-Embedding-0.6B` |
| `--served-model-name` | `Qwen/Qwen3-Embedding-0.6B` | `Qwen/Qwen3-Embedding-0.6B` |
| `--runner` | `pooling` | `pooling` |
| `--port` | `8000` | `8000` |
| `--max-model-len` | `1024` | `1024` |
| `--dtype` | (未指定, 默认) | `float16` |
| `--compilation-config` | (无) | `'{"cudagraph_capture_sizes": [1024,512]}'` |
| `--additional-config` | (无) | `'{"ascend_compilation_config": {"fuse_norm_quant": false}}'` |

---

## 【公式解读】

**原文无公式**。文档中出现的最接近"数学/逻辑表达式"的内容是:

- `--max-model-len` 的注意力 mask 分配复杂度描述: **O(max_model_len²)**, 这是用伪代码形式给出的, 含义是 attention mask 的显存占用与 `max_model_len` 的平方成正比, 因此过大的 context length 在 Atlas 300I DUO 这种显存受限的硬件上会触发 OOM。

文档没有其他 LaTeX 公式或伪代码算法。

---

## 【关联】

文档显式给出的内部链接及其指向如下, 体现该 guide 在整张文档网中的位置:

| 链接文本 | 路径锚点 | 与本文档的关系 |
|---|---|---|
| Supported Features List | `../../user_guide/support_matrix/supported_models.md` | 上游/横向: 查询 Qwen3-Embedding 在 vLLM Ascend 上支持的全部 feature 矩阵 |
| using docker | `../../getting_started/installation.md#installation-prebuilt-image` | 上游: Docker 预置镜像的安装方法总览 (本文 4.1 节是该方法的"模型特化版") |
| installation | `../../getting_started/installation.md` | 上游: 源码安装 vllm-ascend 的入口 (本文 4.2 节是它的子流程) |
| Public FAQs | `../../faqs.md` | 横向/下游: 通用环境、安装、参数类问题的故障排查 |
| (文末 FAQ 节自引用) | `../../faqs.md` | 横向: 第 9 节预留的 FAQ 内容由该页面承担 |

文档**外部链接** (非 vllm-ascend 仓内) 涉及的上下游:

- `https://www.modelscope.cn/models/Qwen/Qwen3-Embedding-{8B,4B,0.6B}`: 模型权重下载源 (ModelScope), 与 huggingface 上的 Qwen3-Embedding 同源。
- `https://docs.mteb.org/`: MTEB (Massive Text Embedding Benchmark) 官方文档, 提供 embedding 模型的标准评测任务集 (本文示例用 `LeCaRDv2`)。
- `https://docs.vllm.ai/en/latest/benchmarking/cli/`: 上游 vLLM 项目的 bench serve CLI 文档, 解释 `vllm bench serve` 各参数语义。
- `https://github.com/vllm-project/vllm/tree/main/examples/pooling/embed`: 上游 vLLM 仓库的 pooling/embed 示例代码, 提供更多调用范式。

模块层级关系可概括为: **getting_started/installation.md (基础设施)** → **本 guide (模型特化部署)** → **user_guide/support_matrix/supported_models.md (特性查询)** ↔ **faqs.md (问题排查)**。

---

## 【使用方法】

以下命令/配置全部摘自原文, 按"安装 → 启动 → 验证 → 评估"四阶段组织:

### ① 模型权重准备 (原文 3.1 节)
```text
下载到 /root/.cache/ 目录:
- Qwen3-Embedding-8B   https://www.modelscope.cn/models/Qwen/Qwen3-Embedding-8B
- Qwen3-Embedding-4B   https://www.modelscope.cn/models/Qwen/Qwen3-Embedding-4B
- Qwen3-Embedding-0.6B https://www.modelscope.cn/models/Qwen/Qwen3-Embedding-0.6B
```

### ② Docker 启动容器 (原文 4.1 节, 三选一)
```shell
# A3
export IMAGE=quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}-a3
# A2
export IMAGE=quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}
# Atlas 300I DUO
export IMAGE=quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}-310p

docker run --rm --name vllm-ascend --shm-size=1g --net=host --privileged=true \
  --device /dev/davinci0 --device /dev/davinci_manager \
  --device /dev/devmm_svm --device /dev/hisi_hdc \
  -v /usr/local/dcmi:/usr/local/dcmi \
  -v /usr/local/Ascend/driver/tools/hccn_tool:/usr/local/Ascend/driver/tools/hccn_tool \
  -v /usr/local/bin/npu-smi:/usr/local/bin/npu-smi \
  -v /usr/local/Ascend/driver/lib64/:/usr/local/Ascend/driver/lib64/ \
  -v /usr/local/Ascend/driver/version.info:/usr/local/Ascend/driver/version.info \
  -v /etc/ascend_install.info:/etc/ascend_install.info \
  -v /root/.cache:/root/.cache \
  -it $IMAGE bash
```

### ③ 启动 vllm serve (原文第 5 节)

A3 / A2 系列:
```shell
vllm serve Qwen/Qwen3-Embedding-0.6B \
  --served-model-name Qwen/Qwen3-Embedding-0.6B \
  --runner pooling \
  --port 8000 \
  --max-model-len 1024
```

Atlas 300I DUO:
```shell
vllm serve Qwen/Qwen3-Embedding-0.6B \
  --served-model-name Qwen/Qwen3-Embedding-0.6B \
  --compilation-config '{"cudagraph_capture_sizes": [1024,512]}' \
  --additional-config '{"ascend_compilation_config": {"fuse_norm_quant": false}}' \
  --runner pooling \
  --dtype float16 \
  --port 8000 \
  --max-model-len 1024
```

关键参数语义 (原文逐字):
- `--runner pooling`: 切换到 pooling 推理模式 (embedding 必需)。
- `--max-model-len`: 单请求 context length 上限; attention mask 显存占用 O(max_model_len²), Atlas 300I DUO 必须显式设置保守值 (如 1024)。
- `--compilation-config '{"cudagraph_capture_sizes": [1024,512]}'`: 受限于 Atlas 300I DUO 硬件 stream 数, cudagraph 捕获尺寸需限制。
- `--additional-config '{"ascend_compilation_config": {"fuse_norm_quant": false}}'`: 关闭 norm-quant 融合 (Atlas 300I DUO 专属)。
- `--dtype float16`: Atlas 300I DUO 显式 fp16。

### ④ 功能验证 (原文第 6 节)
```bash
curl -X POST http://localhost:8000/v1/embeddings \
  -H "Content-Type: application/json" -d '{
    "input": [
      "The capital of China is Beijing.",
      "Gravity is a force that attracts two bodies towards each other. It gives weight to physical objects and is responsible for the movement of planets around the sun."
    ]
  }'
```
成功响应应包含 `embedding` 字段 (HTTP 200), 示例响应中 `prompt_tokens=39, total_tokens=39, completion_tokens=0`。

### ⑤ 精度评估 — MTEB (原文第 7 节)
```python
import os
import mteb
from mteb.models.vllm_wrapper import VllmEncoderWrapper

if __name__ == "__main__":
    data_path = "/home/data/mteb_data"
    os.environ["HF_DATASETS_CACHE"] = data_path
    os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

    model = VllmEncoderWrapper("/root/.cache/Qwen3-Embedding-0.6B",
                               revision="norm",
                               dtype="float16",
                               max_model_len=10240)

    cache = mteb.ResultCache("/home/data/mteb_data")
    tasks = mteb.get_tasks(tasks=["LeCaRDv2"])
    results = mteb.evaluate(model, tasks=tasks, cache=cache,
                            encode_kwargs={"batch_size": 2},
                            overwrite_strategy="always")
    df = results.to_dataframe()
    print(df)
```

### ⑥ 性能评估 — vLLM Benchmark (原文第 8 节)
```bash
vllm bench serve \
  --model Qwen/Qwen3-Embedding-0.6B \
  --backend openai-embeddings \
  --port 8000 \
  --dataset-name random \
  --endpoint /v1/embeddings \
  --random-input 200 \
  --save-result \
  --result-dir ./
```

### ⑦ 版本与替代入口
- 仅 **vLLM Ascend 0.9.2rc1+** 支持该模型 (原文 1 节硬性约束)。
- 不愿用 Docker 时, 可走**源码安装**路径, 详见原文 4.2 节链接 `../../getting_started/installation.md`。
- 公共 FAQ 与故障排查请走原文第 9 节链接 `../../faqs.md`。
