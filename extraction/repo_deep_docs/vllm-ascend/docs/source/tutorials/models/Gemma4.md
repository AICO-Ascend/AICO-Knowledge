# Gemma4

> 仓 `vllm-ascend` · 路径 `docs/source/tutorials/models/Gemma4.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm-ascend/docs/source/tutorials/models/Gemma4.md

# Gemma4 部署指南深度解读

## 【定位】

这篇文档系统性地描述了 Gemma4（Gemma 家族中包含 Dense 与 MoE 两种变体的语言模型）在 Atlas A2、Atlas A3 与 Ascend 950 三类 Ascend 产品上基于 vLLM Ascend 主流分支进行端到端验证与部署的标准操作流程，覆盖特性支持、前置条件、安装、单节点在线服务、功能验证、离线推理、精度评估、性能评估、性能调优及 FAQ 等环节。

---

## 【技术要点】

1. **模型形态与硬件平台**：Gemma4 同时包含 Dense 与 Mixture-of-Experts（MoE）两种变体，适用于通用文本生成、推理与指令跟随场景；支持在 Atlas A2、Atlas A3 与 Ascend 950 产品上运行，文档以"latest vLLM Ascend main branch"为基线。
2. **特性支持矩阵**：BF16、chunked prefill、automatic prefix caching、tensor parallelism、expert parallelism、ACLGraph 均被列入支持范围；图执行模式下 `FULL_DECODE_ONLY`（降低 decode 派发开销）与 `PIECEWISE` 两种 cudagraph_mode 均可用。
3. **典型启动参数**：示例以 4 张可见 NPU 为基准，`ASCEND_RT_VISIBLE_DEVICES=0,1,2,3`、`--tensor-parallel-size 4`、`--max-model-len 32768`，模型路径占位符为 `/root/.cache/path/to/gemma4`；Eager 模式用 `--enforce-eager`，ACLGraph 模式用 `--compilation-config '{"cudagraph_mode": "FULL_DECODE_ONLY"}'`。
4. **关键 CLI 参数集合**：`--enable-expert-parallel`（MoE 部署按需启用 EP）、`--trust-remote-code`（允许加载仓库内模型专属代码）、`--served-model-name gemma4`、通过 `export MODEL_PATH=…` 注入路径。
5. **安装与校验**：`git clone https://github.com/vllm-project/vllm-ascend.git` + `pip install -e .`；通过 `python -c "import vllm_ascend; print(vllm_ascend.__version__)"` 校验，通过 `npu-smi info` 校验 NPU 可见。
6. **OpenAI 兼容接口**：使用 `http://127.0.0.1:8000/v1/completions` 与 `/v1/chat/completions` 进行功能验证，离线推理通过 `vllm.LLM` + `SamplingParams` 完成；精度评估以 GPQA-Diamond 为例走 `lm_eval --model local-completions`。

---

## 【关键机制与数据】

- **执行模式双轨制**（原文:Gemma4 supports both eager execution and ACLGraph execution on Atlas A2, Atlas A3, and Ascend 950 Products）。Eager 模式作为功能验证基线，ACLGraph 模式（`FULL_DECODE_ONLY`）针对 decode 阶段降低派发开销；二者均通过同一个 `vllm serve` 入口接入，仅由 `--enforce-eager` 与 `--compilation-config` 切换。
- **多卡并行策略**（原文:Use tensor parallelism or expert parallelism according to the model size and deployment plan）：Dense 形态默认采用 TP（`--tensor-parallel-size 4`），MoE 形态可在 TP 之外通过 `--enable-expert-parallel` 启用 EP，TP/EP 的具体取值按模型体量与可见 NPU 数调整。
- **在线→离线一致性**（原文示例）：在线服务（`vllm serve`）与离线推理（`vllm.LLM`）使用相同的 NPU 可见性与并行配置：均设置 `tensor_parallel_size=4`、`trust_remote_code=True`、`compilation_config={"cudagraph_mode": "FULL_DECODE_ONLY"}`，确保两条路径行为一致。
- **多节点前置门控**（原文:If multi-node deployment is required, verify the multi-node communication environment according to [Verify Multi-node Communication Environment]…）：正式多节点部署前必须先完成跨节点互联验证，否则后续可能出现服务无法启动、HBM 不足或请求调度异常。
- **KV cache 与序列长度边界**（原文:`--max-model-len`…Increase it only when enough KV cache is available）：`--max-model-len 32768` 仅在 KV cache 充足时才可上调，避免超出 NPU 显存承载。
- **精度评估数据流**（原文:`lm_eval --model local-completions --model_args model=gemma4,base_url=http://127.0.0.1:8000/v1/completions,…`）：以 online 模式命中本机 8000 端口的 completions 端点，将 Gemma4 视作 OpenAI 兼容服务，配合 `tasks gpqa_diamond` 收集准确率；并明确后处理参数（`max_tokens`、`temperature`、stop tokens）须与权重内 `generation_config.json` 一致。

性能数字（如吞吐、时延、TPOT）原文未给出具体数值。

---

## 【表格解读】

### 原文表格：3.1 模型类型与推荐硬件

| Model type | Description | Recommended hardware |
| ---------- | ----------- | -------------------- |
| Gemma4 dense model | Dense Gemma4 weight. | A single Atlas A2, Atlas A3, or Ascend 950 node. Adjust the number of visible NPUs according to model size. |
| Gemma4 MoE model | Mixture-of-Experts Gemma4 weight. | A single Atlas A2, Atlas A3, or Ascend 950 node. Use tensor parallelism or expert parallelism according to the model size and deployment plan. |

逐行解读：

- **第 1 行（Dense）**：描述的是 Dense 形态 Gemma4 权重；硬件建议为单节点 Atlas A2 / Atlas A3 / Ascend 950，可见 NPU 数量按模型体量伸缩。这一行的隐含指引是——Dense 模型没有专家维度，因此部署策略集中在 TP 与 KV cache 维度上，无需引入 EP。
- **第 2 行（MoE）**：描述的是 MoE 形态 Gemma4 权重；硬件仍为单节点 Atlas A2 / Atlas A3 / Ascend 950，但行内追加了"按模型体量与部署计划选择 tensor parallelism 或 expert parallelism"。这一行的隐含指引是——MoE 模型可借由专家切分降低单卡专家参数与激活显存，因此 EP 与 TP 二者择一或组合均可，是 Dense 行之外额外引入的部署自由度。

---

## 【公式解读】

原文无公式。

（文档中所有数值与配置项均以命令行参数、环境变量或 JSON 配置的形式出现，未出现 LaTeX 或伪代码形式的数学表达式。）

---

## 【关联】

- **模型支持矩阵**（[`supported_models.md`](../../user_guide/support_matrix/supported_models.md)）：是 §2 "Supported Features" 的权威清单来源，决定 BF16、chunked prefill、automatic prefix caching、TP、EP、ACLGraph 等特性在 Gemma4 上的可用性结论。
- **特性配置手册**（[`feature_guide/index.md`](../../user_guide/feature_guide/index.md)）：在 §2 中被引用，提供 chunked prefill / prefix caching / 图执行等特性的详细配置方式，承接"特性支持"与"实际 CLI 参数"之间的映射。
- **多节点互联验证**（[`installation.md#installation-multi-node-interconnect`](../../getting_started/installation.md#installation-multi-node-interconnect)）：§3.2 显式要求在多节点部署前完成此步骤，是上游"环境准入"环节，下游直接影响 §5 服务能否稳定起来。
- **公共 FAQ**（[`faqs.md`](../../faqs.md)）：§5.1 的"Common Issues Tip"指引服务启动失败、HBM 不足或请求未按预期调度时优先查阅此文档，是排障入口；同时也是文末预告的 Section 10（model-specific FAQ）的上级文档。
- **AISBench（精度）**（[`using_ais_bench.md`](../../developer_guide/evaluation/using_ais_bench.md)）：§7.1 的精度评估实施细节入口；同一文档在 §8.1 的锚点（[`#execute-performance-evaluation`](../../developer_guide/evaluation/using_ais_bench.md#execute-performance-evaluation)）又承担性能评估的实施入口，因此 AISBench 同时承担"精度 + 性能"两类评测。
- **lm_eval（精度）**（[`using_lm_eval.md`](../../developer_guide/evaluation/using_lm_eval.md)）：§7.2 的安装与使用方法入口，决定 `lm_eval --model local-completions --tasks gpqa_diamond` 的可执行性。
- **vLLM Benchmark**（[`vLLM benchmarking`](https://docs.vllm.ai/en/latest/benchmarking/)）：§8.2 性能评估的官方上游入口，提供 throughput / TTFT / TPOT 等指标。
- **性能调优手册**（[`optimization_and_tuning.md`](../../developer_guide/performance_and_debug/optimization_and_tuning.md)）：§9 性能调优章节的上游方法论来源，承接"推荐配置 + 具体调优手段"链路（原文 §9.1 后续内容被截断，调优具体细节应回流到该手册）。
- **特性矩阵**（[`feature_matrix.md`](../../user_guide/support_matrix/feature_matrix.md)）：在内部链接清单中被列出，与 `supported_models.md` 一起构成模型×特性的二维查询入口。

---

## 【使用方法】

原文有明确写出的启用方式与命令；个别细节（如 §9 性能调优的具体调优动作、§10 FAQ 全文）原文被截断，原文未涉及。

**① NPU 可见性校验**

```shell
npu-smi info
```

预期结果：列出预期的 Ascend 设备。

**② 源码安装 vLLM Ascend**

```shell
git clone https://github.com/vllm-project/vllm-ascend.git
cd vllm-ascend
pip install -e .
```

验证安装：

```shell
python -c "import vllm_ascend; print(vllm_ascend.__version__)"
```

**③ Eager 模式在线服务（§5.1）**

```shell
export ASCEND_RT_VISIBLE_DEVICES=0,1,2,3
export MODEL_PATH=/root/.cache/path/to/gemma4

vllm serve ${MODEL_PATH} \
  --served-model-name gemma4 \
  --trust-remote-code \
  --tensor-parallel-size 4 \
  --max-model-len 32768 \
  --enforce-eager
```

**④ ACLGraph 模式在线服务（§5.1）**

```shell
export ASCEND_RT_VISIBLE_DEVICES=0,1,2,3
export MODEL_PATH=/root/.cache/path/to/gemma4

vllm serve ${MODEL_PATH} \
  --served-model-name gemma4 \
  --trust-remote-code \
  --tensor-parallel-size 4 \
  --max-model-len 32768 \
  --compilation-config '{"cudagraph_mode": "FULL_DECODE_ONLY"}'
```

> MoE 部署按需追加 `--enable-expert-parallel`；如启用 `PIECEWISE` 模式，将 `cudagraph_mode` 替换为对应值。

**⑤ 服务功能验证（§6）**

```shell
curl http://127.0.0.1:8000/v1/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemma4",
    "prompt": "Explain why graph execution improves decode performance.",
    "max_tokens": 128,
    "temperature": 0
  }'
```

Chat Completions：

```shell
curl http://127.0.0.1:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemma4",
    "messages": [
      {"role": "user", "content": "Explain why graph execution improves decode performance."}
    ],
    "max_tokens": 128,
    "temperature": 0
  }'
```

预期：HTTP 200，JSON 内含 `choices` 字段及生成文本。

**⑥ 离线推理（§6.3）**

```python
from vllm import LLM, SamplingParams

llm = LLM(
    model="/root/.cache/path/to/gemma4",
    trust_remote_code=True,
    tensor_parallel_size=4,
    compilation_config={"cudagraph_mode": "FULL_DECODE_ONLY"},
)

sampling_params = SamplingParams(temperature=0, max_tokens=128)
outputs = llm.generate(
    ["Explain why graph execution improves decode performance."],
    sampling_params,
)

for output in outputs:
    print(output.outputs[0].text)
```

**⑦ 精度评估（§7）**

AISBench 路径：参见 [`using_ais_bench.md`](../../developer_guide/evaluation/using_ais_bench.md)。

lm_eval 路径（以 GPQA-Diamond 为例，online 模式）：

```shell
lm_eval \
  --model local-completions \
  --model_args model=gemma4,base_url=http://127.0.0.1:8000/v1/completions,tokenized_requests=False,trust_remote_code=True \
  --tasks gpqa_diamond \
  --output_path ./
```

**⑧ 性能评估（§8）**

- AISBench：参见 [`using_ais_bench.md#execute-performance-evaluation`](../../developer_guide/evaluation/using_ais_bench.md#execute-performance-evaluation)。
- vLLM Benchmark：参见 [vLLM benchmarking](https://docs.vllm.ai/en/latest/benchmarking/)。

**⑨ 性能调优（§9.1）**

原文仅给出章节标题与开头 "The following configurations are for reference only. The optimal configuration depends on hardware resources, model size, maximum input/o…"，其后内容被截断，具体推荐配置表与调优动作原文未涉及（应回溯到 [`optimization_and_tuning.md`](../../developer_guide/performance_and_debug/optimization_and_tuning.md)）。
