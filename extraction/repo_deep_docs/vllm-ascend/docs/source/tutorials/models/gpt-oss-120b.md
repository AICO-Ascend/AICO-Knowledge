# gpt-oss-120b

> 仓 `vllm-ascend` · 路径 `docs/source/tutorials/models/gpt-oss-120b.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm-ascend/docs/source/tutorials/models/gpt-oss-120b.md

# 「gpt-oss-120b」指南文档深度解读

## 【定位】

本指南文档是 vllm-ascend 项目中关于 **OpenAI 开源推理模型 gpt-oss-120b（BF16 版）在昇腾 Atlas 800 A2/A3 硬件上从环境准备、容器化部署、专家并行推理启动到功能/精度评测的端到端 onboarding 文档**，目的是让开发者能够在 Ascend NPU 上以最小摩擦完成该 MoE 推理模型的拉起与基本验证。

---

## 【技术要点】

1. **模型与硬件最低要求**（原文：Environment Preparation → Model Weight）
   - `gpt-oss-120b`（BF16 版本）部署规模：**1 台 Atlas 800 A3（64GB × 16）或 1 台 Atlas 800 A2（64GB × 8）**；模型权重下载指向 `unsloth/gpt-oss-120b-BF16`。

2. **容器化部署与设备映射**（原文：Docker run）
   - 镜像：`quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}`，A3 机器使用 `-a3` 后缀标签；
   - Atlas A2 通过 `/dev/davinci[0-7]`、`Atlas A3` 通过 `/dev/davinci[0-15]` 进行设备挂载，并额外挂载 `davinci_manager`、`devmm_svm`、`hisi_hdc`、`/usr/local/dcmi`、hccn_tool、npu-smi、Ascend driver lib64 与 version.info 等昇腾运行时依赖；
   - `--shm-size=1g`、`--net=host`、`/root/.cache` 挂载以承载已下载权重；
   - 默认工作目录 `/workspace`，vLLM 与 vLLM Ascend 源码位于 `/vllm-workspace` 并以 `pip install -e` 开发模式安装，便于修改即时生效。

3. **关键运行时环境变量**（原文：Single-node Deployment 脚本导出）
   - `VLLM_USE_MODELSCOPE=True`（走 ModelScope 加速权重下载）；
   - `HCCL_OP_EXPANSION_MODE="AIV"`、`HCCL_BUFFSIZE=512`（集合通信优化）；
   - `NPU_MEMORY_FRACTION=0.95`（降低显存碎片、规避 OOM）；
   - `VLLM_USE_V1=1`、`TASK_QUEUE_ENABLE=1`（启用 v1 调度与任务队列）；
   - `OMP_PROC_BIND=false`、`OMP_NUM_THREADS=1`、`TIKTOKEN_ENCODINGS_BASE=${PWD}/tiktoken_encodings`（规避 HarmonyError 与线程绑核干扰）。

4. **vLLM serve 启动参数**（原文：Single-node Deployment）
   - `--served-model-name gpt-oss-120b-bf16`、`--port 8000`、`--trust-remote-code`；
   - `--tensor-parallel-size 4`（4 路张量并行，文档也提到该参数为 TP 通用设置）；
   - `--max-model-len 4096`、`--max-num-batched-tokens 4096`（上下文与单步 token 上限均为 4096）；
   - `--max-num-seqs 4`、`--gpu-memory-utilization 0.90`（每 DP 组最多并发 4 个请求，HBM 利用率 0.9）；
   - `--enable-expert-parallel`（启用专家并行，匹配 MoE 架构）；
   - `--compilation_config '{"cudagraph_mode": "FULL_DECODE_ONLY", "cudagraph_capture_sizes":[1,2,3,4]}'`（aclgraph 全解码图模式，仅捕获 [1,2,3,4] 4 个 batch 等级）。

5. **aclgraph / ChunkPrefill 调度机制说明**（原文：参数解释）
   - `cudagraph_mode` 当前支持 `PIECEWISE` 与 `FULL_DECODE_ONLY`，**文档明确推荐 `FULL_DECODE_ONLY`** 以减少算子下发开销；
   - vLLM v1 调度默认启用 `ChunkPrefill/SplitFuse`：当请求输入长度 > `--max-num-batched-tokens` 时按该值切片多轮计算；decode 请求优先调度，prefill 仅在剩余容量时被调度；
   - 性能测试建议：`--max-num-seqs` × `--data-parallel-size` ≥ 实际总并发（否则排队耗时也会计入 TTFT/TPOT）。

6. **openai_harmony / tiktoken 故障绕过**（原文：Troubleshooting）
   - 触发条件：启动时报 `openai_harmony.HarmonyError: error downloading or loading vocab file`；
   - 解决方案：预先下载 `o200k_base.tiktoken` 与 `cl100k_base.tiktoken` 到 `tiktoken_encodings/` 目录，并通过 `export TIKTOKEN_ENCODINGS_BASE=${PWD}/tiktoken_encodings` 让 openai_harmony 加载本地词表。

---

## 【关键机制与数据】

- **原文**：gpt-oss-120b 与 gpt-oss-20b 均是 **MoE（mixture-of-experts）Transformer 架构**，采用大规模蒸馏 + 强化学习训练，针对 deep research 浏览、Python 工具调用与开发者提供函数等 agentic 能力做了优化，并以渲染过的 chat 格式保证指令遵循与角色划分清晰；权重、推理实现、工具环境与 tokenizer 均以 Apache 2.0 发布。
- **原文**：服务启动后可通过 `curl http://localhost:8000/v1/chat/completions` 以 OpenAI 兼容 chat 协议做功能性打点验证，请求体形如 `{"model":"gpt-oss-120b-bf16","messages":[{"role":"user","content":"who are you"}]}`。
- **原文**：精度评测路径为 AISBench，文档仅声明“参考执行 AISBench 后可得结果（仅作参考）”，未给出具体分数；该表格在原文中**被截断**（仅残留 `| datas` 一行片段），本文不臆造任何评测数字。
- **原文**（warm-up / kv_cache 计算语义）：`--gpu-memory-utilization` 的本质是在 profile run 阶段记录以 `--max-num-batched-tokens` 为输入的单次推理峰值显存，然后计算 `kv_cache 可用量 = --gpu-memory-utilization × HBM size − 峰值显存`；因 MoE 的 EP（专家并行）负载不均可能导致 profile 与实际峰值不一致，故不宜将该值设得过高，默认 `0.9`。
- **原文**（未提供的字段）：**原文未给出**任何吞吐量（tokens/s）、TTFT/TPOT、显存实测占用或与 GPU 参考实现的对比数据，本节不予补全。

---

## 【表格解读】

> 原文表格仅在文档末尾出现一处，但被截断，完整内容如下（**逐字保留**，可见原文已不完整）：

```markdown
| datas
```

- **解读**：该表格位于 "Accuracy Evaluation → Using AISBench" 第 2 步说明之后，标题意图为"`gpt-oss-120b-bf16` 在 AISBench 上的精度结果"，但原文仅保留了 `| datas`（列分隔符后的 `datas` 一段），其后行全部缺失。该表无法恢复为有效行/列结构，因此本文**不进行逐行解读**，也**不补造**任何评测分数；如需查阅实际结果，应以 AISBench 工具执行后的输出为准。

> 其余章节（Supported Features、Environment Preparation、Deployment 参数、Functional Verification、Accuracy Evaluation 方法说明）**均为参数说明与命令块，无结构化表格**。

---

## 【公式解读】

原文无独立公式。

**但**在 `--gpu-memory-utilization` 参数解释段落中，文档以自然语言给出一个**推导关系式**（非 LaTeX 形式），逐字保留并解释如下：

```
可用 kv_cache = --gpu-memory-utilization × HBM size − 峰值 GPU 显存
```

| 符号 | 含义（依据原文） | 作用 |
|---|---|---|
| `--gpu-memory-utilization` | vLLM 实际用于推理的 HBM 占比 | 控制 kv_cache 的预算乘子；越大 kv_cache 越多，但过高会因 EP 负载不均导致 OOM |
| `HBM size` | 设备高带宽内存总容量 | 计算 kv_cache 预算的基线 |
| `峰值 GPU 显存` | warm-up（profile run）阶段记录到的单次推理峰值显存（输入取自 `--max-num-batched-tokens`） | 必须预留扣除的固定开销 |

> 原文无 LaTeX / 伪代码形式的公式；其它运行参数（如 `--tensor-parallel-size`、`--max-num-batched-tokens`、`HCCL_BUFFSIZE`、`NPU_MEMORY_FRACTION=0.95`、`--gpu-memory-utilization=0.90`）为常量数值，不构成公式。

---

## 【关联】

依据文末给出的内部链接：

- **上游能力矩阵**：[Supported Features List](../../user_guide/support_matrix/supported_models.md) — 本文中 "Supported Features" 一节直接指向该页，用以确认 `gpt-oss-120b` 在 vllm-ascend 上的功能支持矩阵（TP、ChunkPrefill、aclgraph、专家并行等是否启用需在该页核对）。
- **特性配置总入口**：[Feature Guide](../../user_guide/feature_guide/index.md) — 同上，用于查阅每个特性（如 ChunkPrefill、专家并行、cudagraph 模式）的具体配置写法与默认值。
- **安装与构建路径**：[installation](../../getting_started/installation.md) — 当用户不愿直接使用 all-in-one 容器时，本文档 "Environment Preparation → Installation" 末尾指向此处，引导从源码构建 `vllm-ascend`。
- **精度评测工具**：[Using AISBench](../../developer_guide/evaluation/using_ais_bench.md) 与 [Using AISBench → Execute Performance Evaluation](../../developer_guide/evaluation/using_ais_bench.md#execute-performance-evaluation) — 本文 "Accuracy Evaluation → Using AISBench" 步骤 1 与潜在的性能评测步骤均依赖这两个锚点，提供评测脚本、运行方式与结果解读模板。
- **模型权重外链**：[unsloth/gpt-oss-120b-BF16（HuggingFace）](https://huggingface.co/unsloth/gpt-oss-120b-BF16) 与 [quay.io/ascend/vllm-ascend（tags）](https://quay.io/repository/ascend/vllm-ascend?tab=tags) — 镜像与权重的外部下载入口，与上述内部链接共同构成完整 onboarding 链路。
- **外部问题追踪**：[openai/harmony#35](https://github.com/openai/harmony/issues/35) — 解释 tiktoken 词表预下载绕过方案的来源，影响 `openai_harmony` tokenizer 加载。

---

## 【使用方法】

> 以下命令均**逐字保留**原文，必要的解释放在条目说明中。

**1. 拉取并启动容器（Atlas A3 为例）**

```bash
docker pull quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}-a3

docker run --rm \
    --name vllm-ascend-env \
    --shm-size=1g \
    --net=host \
    --device /dev/davinci0 ... /dev/davinci7 \
    --device /dev/davinci_manager \
    --device /dev/devmm_svm \
    --device /dev/hisi_hdc \
    -v /usr/local/dcmi:/usr/local/dcmi \
    -v /usr/local/Ascend/driver/tools/hccn_tool:/usr/local/Ascend/driver/tools/hccn_tool \
    -v /usr/local/bin/npu-smi:/usr/local/bin/npu-smi \
    -v /usr/local/Ascend/driver/lib64/:/usr/local/Ascend/driver/lib64/ \
    -v /usr/local/Ascend/driver/version.info:/usr/local/Ascend/driver/version.info \
    -v /etc/ascend_install.info:/etc/ascend_install.info \
    -v /root/.cache:/root/.cache \
    -it $IMAGE bash
```

> 原文提示：Atlas A2 使用 `/dev/davinci[0-7]`，Atlas A3 使用 `/dev/davinci[0-15]`；`--device` 列表需按实际机器调整。

**2. 规避 HarmonyError（启动前一次性操作）**

```bash
mkdir -p tiktoken_encodings
wget -O tiktoken_encodings/o200k_base.tiktoken "https://openaipublic.blob.core.windows.net/encodings/o200k_base.tiktoken"
wget -O tiktoken_encodings/cl100k_base.tiktoken "https://openaipublic.blob.core.windows.net/encodings/cl100k_base.tiktoken"
export TIKTOKEN_ENCODINGS_BASE=${PWD}/tiktoken_encodings
```

**3. 单节点启动 vLLM serve（TP=4）**

```bash
#!/bin/sh
export VLLM_USE_MODELSCOPE=True
export HCCL_OP_EXPANSION_MODE="AIV"
export HCCL_BUFFSIZE=512
export NPU_MEMORY_FRACTION=0.95
export ASCEND_RT_VISIBLE_DEVICES=0,1,2,3
export OMP_PROC_BIND=false
export VLLM_USE_V1=1
export TASK_QUEUE_ENABLE=1
export OMP_NUM_THREADS=1
export TIKTOKEN_ENCODINGS_BASE=${PWD}/tiktoken_encodings

vllm serve unsloth/gpt-oss-120b-BF16 \
    --served-model-name gpt-oss-120b-bf16 \
    --port 8000 \
    --trust-remote-code \
    --max-num-seqs 4 \
    --gpu-memory-utilization 0.90 \
    --tensor-parallel-size 4 \
    --max-model-len 4096 \
    --max-num-batched-tokens 4096 \
    --enable-expert-parallel \
    --compilation_config '{"cudagraph_mode": "FULL_DECODE_ONLY", "cudagraph_capture_sizes":[1,2,3,4]}'
```

**4. 功能性打点验证（OpenAI 兼容协议）**

```bash
curl http://localhost:8000/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d '{
        "model": "gpt-oss-120b-bf16",
        "messages": [{"role":"user", "content":"who are you"}]
    }'
```

**5. 精度评测入口**

原文仅指向：[Using AISBench](../../developer_guide/evaluation/using_ais_bench.md)，并注明执行后可参考 `gpt-oss-120b-bf16` 的运行结果（仅作参考；原文中对应的结果表格被截断）。具体的 AISBench 安装、数据集下载、命令模板与结果文件位置等**未在本文展开**，请以该指南为准。
