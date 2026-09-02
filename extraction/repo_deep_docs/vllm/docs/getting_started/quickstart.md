# Quickstart

> 仓 `vllm` · 路径 `docs/getting_started/quickstart.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm/docs/getting_started/quickstart.md

# vLLM Quickstart 文档深度解读

---

## 【定位】

这篇文档是 vLLM 的官方快速入门指南（Quickstart），面向首次接触 vLLM 的开发者，提供从零开始完成 **离线批量推理（Offline Batched Inference）** 与 **在线服务（Online Serving）** 两条核心路径所需的最小化、可直接复制的安装与代码示例，重点在于让读者在最短时间内把 vLLM 跑起来并理解其最基础用法。

---

## 【技术要点】

1. **环境前置条件** — 操作系统限定 Linux，Python 版本区间 `3.10 -- 3.13`；macOS 上需通过 `vllm-metal` 项目获得 Apple Silicon GPU 加速支持。
2. **多平台安装矩阵** — 文档以 mkdocs 的 `=== "..."` 选项卡分别覆盖六类硬件后端：
   - **NVIDIA CUDA**：`uv pip install vllm --torch-backend=auto` 或 `--torch-backend=cu126`，可通过 `UV_TORCH_BACKEND=auto` 环境变量自动选择与已安装 CUDA 驱动匹配的 PyTorch 索引。
   - **AMD ROCm**：使用 `https://wheels.vllm.ai/rocm/` 私有索引，原文注记当前支持 Python 3.12、ROCm 7.0、`glibc >= 2.35`；旧版 Docker 镜像 `rocm/vllm-dev` 已被弃用，新版 nightly 镜像为 `vllm/vllm-openai-rocm:nightly`。
   - **Intel GPU (XPU)**：v0.26.0 起官方 Docker 镜像已合并进 vLLM 发布，nightly 镜像为 `vllm/vllm-openai-xpu:nightly`；预编译 XPU wheels "will be available soon"。
   - **Google TPU**：安装专用包 `uv pip install vllm-tpu`，详细内容走 vLLM on TPU 独立文档站点。
   - **Ascend NPU**：vLLM Ascend 作为社区硬件插件独立维护，需参考 `vllm-project/vllm-ascend`。
   - **Apple Silicon (Mac)**：vLLM-Metal，使用 **MLX** 而非 PyTorch 作为计算后端，需搭配 `mlx-community` 上的 MLX 优化模型。
3. **离线推理核心类** — 仅需导入 `vllm.LLM` 与 `vllm.SamplingParams` 两个类；`LLM` 负责引擎初始化与离线推理调度，`SamplingParams` 负责采样参数设置。
4. **示例采样参数** — `temperature=0.8`、`top_p=0.95`（nucleus sampling）；默认行为是读取 HuggingFace 上的 `generation_config.json`，若需强制使用 vLLM 默认采样参数，可在创建 `LLM` 实例时设置 `generation_config="vllm"`。
5. **示例模型** — 使用 `facebook/opt-125m`（OPT-125M 论文 https://arxiv.org/abs/2205.01068），支持模型清单见 `../models/supported_models.md`。
6. **模型源切换** — 通过环境变量 `export VLLM_USE_MODELSCOPE=True` 可使 vLLM 从 ModelScope 而非 HuggingFace 下载模型权重。
7. **Chat/Instruct 模型注意** — `llm.generate` 不会自动套用模型 chat template；推荐做法是手动用 `transformers.AutoTokenizer.apply_chat_template()` 预处理对话，或直接调用 `llm.chat(messages)`（消息格式与 OpenAI `client.chat.completions` 保持一致）。（原文该 code 块在提供版本中被截断。）

---

## 【关键机制与数据】

| 流程节点 | 行为描述（原文摘录） |
|---|---|
| `LLM.__init__` | "initializes vLLM's engine and the OPT-125M model for offline inference"——即在 Python 进程内启动 vLLM 推理引擎并加载权重。 |
| `llm.generate(prompts, sampling_params)` | "adds the input prompts to the vLLM engine's waiting queue and executes the vLLM engine to generate the outputs with high throughput"——先把 prompt 入队再驱动引擎调度，返回 `RequestOutput` 列表。 |
| 返回对象结构 | `output.outputs[0].text` 包含首个候选完整文本；`output.prompt` 为原始 prompt。 |
| 默认采样来源 | "vLLM will use sampling parameters recommended by model creator by applying the `generation_config.json` from the Hugging Face model repository if it exists." |
| 模型源分发 | 通过 `VLLM_USE_MODELSCOPE` 环境变量在 HuggingFace 与 ModelScope 之间切换。 |

**性能/吞吐声明（原文）**：仅有一句定性描述——"executes the vLLM engine to generate the outputs with high throughput"，未给出 tokens/s、batch size、显存占用等具体性能数字。

**推导公式**：原文未涉及任何公式或伪代码算法。

---

## 【表格解读】

> **原文无表格**。原文中所有平台信息均以 mkdocs 选项卡（`=== "NVIDIA CUDA" / "AMD ROCm" / "Intel GPU" / "Google TPU" / "Ascend NPU" / "Apple Silicon (Mac)"`）形式呈现，并非结构化表格，因此本节不进行表格还原。

---

## 【公式解读】

> **原文无公式**。原文未出现任何 LaTeX 公式或伪代码表达式。

---

## 【关联】

文档构建了一条「安装 → 离线推理 → 在线服务」的纵向调用链，并通过文末链接横向连接到 vLLM 文档体系的其他模块：

| 链接（原文出现次数） | 关联资源 | 上下游关系 |
|---|---|---|
| `installation/gpu.md`（×4，出现在 macOS / Intel GPU / Apple Silicon 三个 note 与 NVIDIA tab 中） | 统一 GPU 安装指南，按 tab 切换 CUDA/AMD/Intel XPU/Apple Silicon | 上游：本文档的「Installation」仅给出最简命令；下游：详细编译、Docker、源码构建、版本兼容矩阵均在该指南中。 |
| `installation/README.md`（note 末尾） | 总入口安装 README，覆盖非 CUDA 平台及更多细节 | 与 `installation/gpu.md` 形成「总入口 → 平台专用」关系。 |
| `../../examples/basic/offline_inference/basic.py`（×2，在 Offline Inference 与 Online Serving 章均出现） | 可直接运行的离线推理示例脚本 | 本文档中所有 `LLM` / `SamplingParams` 用法均以该脚本为蓝本，可视为「最小可执行实现」。 |
| `../api/README.md#inference-parameters` | 推理 API 参数文档 | 上游：`SamplingParams` 各字段（temperature、top_p、max_tokens 等）官方定义在此。 |
| `../models/supported_models.md` | vLLM 支持的模型清单 | 横向：决定 `LLM(model=...)` 可填入哪些 model id。 |
| `../serving/online_serving/README.md#chat-template` | 在线服务 chat template 说明 | 上游：`llm.chat` / OpenAI 兼容 API 的对话模板格式在此定义。 |
| `https://github.com/vllm-project/vllm-metal` / `vllm-tpu` / `vllm-ascend` | 社区/官方硬件子项目 | 平台专用分支，与本仓 vLLM 上游同步发布。 |

文档结构上还形成了如下上下游闭环：

```
Quickstart (本文)
  ├─ prerequisites ─────► installation/gpu.md
  ├─ offline inference ─► examples/basic/offline_inference/basic.py
  │                      └─► api/README.md#inference-parameters
  │                      └─► models/supported_models.md
  └─ online serving ────► serving/online_serving/README.md#chat-template
```

---

## 【使用方法】

### 安装命令（按平台，原文逐字保留）

**NVIDIA CUDA**：

```bash
uv venv --python 3.12 --seed
source .venv/bin/activate
uv pip install vllm --torch-backend=auto
```

指定后端：`--torch-backend=cu126`（或环境变量 `UV_TORCH_BACKEND=cu126`）；无持久环境运行：`uv run --with vllm vllm --help`。

Conda 路径：

```bash
conda create -n myenv python=3.12 -y
conda activate myenv
pip install --upgrade uv
uv pip install vllm --torch-backend=auto
```

**AMD ROCm**：

```bash
uv venv --python 3.12 --seed
source .venv/bin/activate
uv pip install vllm --extra-index-url https://wheels.vllm.ai/rocm/
```

**Google TPU**：`uv pip install vllm-tpu`

### 离线推理最小代码（原文逐字保留）

```python
from vllm import LLM, SamplingParams

prompts = [
    "Hello, my name is",
    "The president of the United States is",
    "The capital of France is",
    "The future of AI is",
]
sampling_params = SamplingParams(temperature=0.8, top_p=0.95)

llm = LLM(model="facebook/opt-125m")

outputs = llm.generate(prompts, sampling_params)

for output in outputs:
    prompt = output.prompt
    generated_text = output.outputs[0].text
    print(f"Prompt: {prompt!r}, Generated text: {generated_text!r}")
```

### 关键配置开关（原文摘录）

| 配置项 | 取值 | 作用 |
|---|---|---|
| `LLM(model=..., generation_config="vllm")` | `"vllm"` | 强制使用 vLLM 默认采样参数，覆盖 HuggingFace `generation_config.json`。 |
| 环境变量 `VLLM_USE_MODELSCOPE` | `True` | 将模型下载源切换为 ModelScope。 |
| `--torch-backend=auto` / `UV_TORCH_BACKEND=auto` | 自动 / `cu126` 等 | 由 `uv` 按 CUDA 驱动版本自动选择 PyTorch wheel 索引。 |

### 在线服务与 Chat 用法

原文提供的 chat 模板代码块在截断片段中不完整，仅可读到开头部分：

```python
# Using tokenizer to apply chat template
from transformers import AutoTokenizer

tokenizer = Au  # ← 原文此处截断
```

可确认的用法是：

- 手动方案：使用 `transformers.AutoTokenizer` 的 `apply_chat_template()` 自行格式化消息；
- 自动方案：直接调用 `llm.chat(messages)`，其中 `messages` 与 OpenAI `client.chat.completions` 格式一致。

其余与 `vllm serve` 启动、API 端点、curl/OpenAI 客户端调用相关的具体命令，原文未在提供片段中展开，仅以「Online serving」章节标题与 `../serving/online_serving/README.md#chat-template` 链接指明路径，**原文未涉及具体命令细节**。
