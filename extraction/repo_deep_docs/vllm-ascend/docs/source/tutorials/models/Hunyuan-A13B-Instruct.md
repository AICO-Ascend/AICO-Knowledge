# Hunyuan-A13B-Instruct

> 仓 `vllm-ascend` · 路径 `docs/source/tutorials/models/Hunyuan-A13B-Instruct.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm-ascend/docs/source/tutorials/models/Hunyuan-A13B-Instruct.md

# Hunyuan-A13B-Instruct 教程文档深度解读

## 【定位】
这篇文档是 vllm-ascend 在华为昇腾 NPU 上部署腾讯混元 Hunyuan-A13B-Instruct（细粒度混合专家 MoE 模型）的端到端操作指南，覆盖权重下载、容器/源码两种安装方式、单节点 4 卡 NPU 部署、基于 AISBench 的功能/精度/性能验证全流程。

## 【技术要点】

- **模型规模**：总参数量 **80B**，激活参数 **13B**，原生支持 **256k** 超长上下文，原生 thought chain (CoT) 推理。
- **权重来源**：BF16 版本从 ModelScope 下载，路径 `Tencent-Hunyuan/Hunyuan-A13B-Instruct`，建议放入多节点共享目录 `/root/.cache/`。
- **运行环境**：基于 GiteeAI 平台内置的 **CANN**（verified 版本 **8.5.1**）+ Python **3.11.6** Conda 环境，跑通 vLLM 与 vLLM-Ascend 的 `{{ vllm_ascend_version }}` 版本；Atlas A3 机器需使用带 `-a3` 后缀的镜像。
- **4-NPU 单节点部署**：通过 `vllm serve` 启动，`--tensor-parallel-size 4` 跨 4 张 NPU 张量并行，`--max-model-len 32768`，`--gpu-memory-utilization 0.90`，并设置 `HCCL_INTRA_ROCE_ENABLE=1` 启用 HCCL 集合通信。
- **ACL Graph 加速**：启用 PIECEWISE 模式后系统自动捕获图，约 **18 秒**完成捕获，可显著加速后续推理。
- **精度与性能基线**：GSM8K（7cd45e 版本，gen 模式）准确率 **94.77%**；AISBench demo_gsm8k 性能测试中 TTFT 均值 **238.6 ms**、TPOT 均值 **60.1 ms**、端到端均值 **29982.6 ms**、吞吐 **16.5261 token/s**。

## 【关键机制与数据】

- **工作原理**：模型为混合专家（MoE）架构，单 token 推理只激活约 13B 参数，但需将全部 80B 权重驻留在 NPU 显存，因此每张 NPU 静态占用约 **37.46 GB** 用于权重，剩余显存用于 KV cache（可并发容纳约 **529,152 tokens**）。
- **数据流/通信**：单节点内 4 张 NPU 通过 HCCL（启用 RoCE `HCCL_INTRA_ROCE_ENABLE=1`）进行张量并行通信；外部 HTTP 调用走 8000 端口的 OpenAI 兼容 `/v1/chat/completions` 接口。
- **性能数据（原文，CANN 8.5.1 验证日志）**：
  - 权重静态显存：每 NPU 约 **37.46 GB**
  - ACL Graph 捕获耗时：约 **18 s**（PIECEWISE 模式）
  - KV cache 并发容量：约 **529,152 tokens**
  - GSM8K 准确率：**94.77%**（AISBench，accuracy 模式，sample N=8）
  - TTFT avg 238.6 ms / TPOT avg 60.1 ms / ITL avg 59.7 ms / E2EL avg 29982.6 ms / OutputTokenThroughput avg 16.5261 token/s

## 【表格解读】

### 表 1：GSM8K 精度汇总（原文 markdown 逐字还原）

| dataset | version | metric  | mode | vllm-api-general-chat |
| ------- | ------- | ------- | ---- | --------------------- |
| gsm8k   | 7cd45e  | accuracy | gen | 94.77                 |

**逐行解读**：
- 第一行表头：`dataset`（数据集名）/ `version`（AISBench 数据集版本号）/ `metric`（评估指标）/ `mode`（评估模式）/ `vllm-api-general-chat`（使用 vLLM general chat 接口作为推理后端）。
- 第二行数据：`gsm8k` 数据集、版本 `7cd45e`、指标 `accuracy`、模式 `gen`（生成式）、得分 **94.77**（原文同时给出未截断的浮点值 94.76876421531463），表示模型在该基准上答对了约 94.77% 的题目。

### 表 2：AISBench 性能参数表（原文字符框线表，逐字段还原）

| Performance Parameters | Stage | Average | Min | Max | Median | P75 | P90 | P99 | N |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| E2EL | total | 29982.6 ms | 16472.9 ms | 41147.2 ms | 30919.1 ms | 33514.9 ms | 39413.8 ms | 40973.9 ms | 8 |
| TTFT | total | 238.6 ms | 107.9 ms | 276.7 ms | 254.0 ms | 265.6 ms | 272.4 ms | 276.3 ms | 8 |
| TPOT | total | 60.1 ms | 57.7 ms | 61.3 ms | 60.4 ms | 60.8 ms | 61.2 ms | 61.3 ms | 8 |
| ITL | total | 59.7 ms | 0.0 ms | 219.7 ms | 51.7 ms | 64.1 ms | 81.9 ms | 146.2 ms | 8 |
| InputTokens | total | 1457.5 | 1426.0 | 1511.0 | 1456.5 | 1465.25 | 1481.6 | 1508.06 | 8 |
| OutputTokens | total | 497.5 | 268.0 | 710.0 | 508.5 | 555.75 | 666.6 | 705.66 | 8 |
| OutputTokenThroughput | total | 16.5261 token/s | 16.2402 token/s | 17.2551 token/s | 16.4461 token/s | 16.5728 token/s | 16.9063 token/s | 17.2202 token/s | 8 |

**逐行解读**：
- `E2EL`（End-to-End Latency）：从请求发起到全部 token 返回的总时延，平均约 30 秒，分布跨度大（min 16.5 s / max 41.1 s），说明存在首请求编译/缓存命中的冷热差异。
- `TTFT`（Time To First Token）：首 token 延迟，平均 **238.6 ms**，P99 约 276.3 ms，体现 ACL Graph 捕获后预填充阶段的稳定性。
- `TPOT`（Time Per Output Token）：平均每输出一个 token 的耗时，平均 **60.1 ms**，分布极窄（57.7–61.3 ms），说明解码阶段已十分稳定。
- `ITL`（Inter-Token Latency）：相邻输出 token 间隔，平均 59.7 ms，但 min=0.0 ms、P99=146.2 ms，提示偶发的 token 突发调度抖动（与流式 chunk 输出有关）。
- `InputTokens`：每次请求输入长度均值 1457.5 tokens，波动小（1426–1511），对应 demo_gsm8k 的 4-shot CoT prompt 模板。
- `OutputTokens`：单次输出长度均值 497.5 tokens，跨度 268–710。
- `OutputTokenThroughput`：单请求级输出吞吐约 **16.5 token/s**（与 TPOT≈60 ms 互为倒数关系）；N=8 表示样本量仅 8 条，统计意义有限。

## 【公式解读】

原文无公式（无 LaTeX 或伪代码形式的数学公式；仅有命令行参数与 AISBench 表格中的统计字段定义）。原文无公式。

## 【关联】

- **上游/平台层**：依赖 GiteeAI 平台预装 CANN 8.5.1 与 Python 3.11.6 Conda 环境，验证基线即在此平台上产出。
- **基础栈**：vLLM（`{{ vllm_version }}` 版本，需 `VLLM_TARGET_DEVICE=empty` 安装）作为推理框架，vLLM-Ascend（`{{ vllm_ascend_version }}` 版本）作为 NPU 后端插件，二者通过 `pip install -e .` 共同部署；源码安装时需 `git submodule update --init --recursive`。
- **硬件适配**：通过镜像 tag `-a3` 后缀区分 Atlas A2 与 Atlas A3 机型；容器需透传 `/dev/davinci_manager`、`/dev/devmm_svm`、`/dev/hisi_hdc` 等昇腾专用字符设备，以及 `/usr/local/dcmi`、`/usr/local/bin/npu-smi`、Ascend driver 库与版本信息文件。
- **推理引擎特性**：启用 ACL Graph 的 PIECEWISE 模式进行图捕获，是 vLLM-Ascend 在昇腾上的关键加速特性，与本文观察到的"~18 s 首次捕获、后续推理显著加速"直接对应。
- **下游验证工具**：使用 AISBench 分别在 `--mode perf`（流式 chat + demo_gsm8k 4-shot CoT）下做性能压测，在 `accuracy` 模式 + `gsm8k_gen_0_shot_cot_chat_prompt` 下做精度评估。

## 【使用方法】

### 启用方式

1. **拉取/下载权重**：BF16 版本从 ModelScope 下载至共享目录 `/root/.cache/`。
2. **启动容器**：Atlas A2 用 `quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}`，Atlas A3 用 `…{{ vllm_ascend_version }}-a3`；需挂载 `/root/.cache` 用于权重、`/usr/local/dcmi` 与 `/usr/local/bin/npu-smi`、Ascend driver 目录与版本文件；映射 `-p 8000:8000`。
3. **或从源码构建**：`git clone` vLLM（`VLLM_TARGET_DEVICE=empty pip install -e .`）→ clone vllm-ascend（`git submodule update --init --recursive && pip install -e .`）。

### 部署配置项（vLLM serve 关键参数）

| 参数 | 值 | 说明 |
| --- | --- | --- |
| `--trust-remote-code` | true | 允许执行模型仓库自定义代码（Hunyuan-A13B-Instruct 必需） |
| `--host` | `0.0.0.0` | 监听所有网卡 |
| `--port` | `8000` | HTTP 服务端口 |
| `--served-model-name` | `Hunyuan` | 对外暴露的模型名（与 curl 调用一致） |
| `--tensor-parallel-size` | `4` | 4 张 NPU 张量并行 |
| `--max-model-len` | `32768` | 最大上下文长度（注意：模型本身支持 256k，文档此次部署截断为 32k） |
| `--gpu-memory-utilization` | `0.90` | NPU 显存利用率上限 |

### 环境变量

- `HCCL_INTRA_ROCE_ENABLE=1`：启用 HCCL 通过 RoCE 通信。
- `ASCEND_RT_VISIBLE_DEVICES=0,1,2,3`：限制进程可见的 NPU 为 0–3 号。
- `HF_HOME=/data`：HuggingFace 缓存目录。

### 验证命令

- **功能验证**：`curl http://localhost:8000/v1/chat/completions` 发起 chat completion 请求（`model=Hunyuan`, `max_tokens=100`, `temperature=0.7`），原文给出预期输出片段含 `<think>` 标签，体现 CoT 能力。
- **精度评估**：`ais_bench --models vllm_api_general_chat --datasets gsm8k_gen_0_shot_cot_chat_prompt --summarizer example --debug`。
- **性能压测**：`ais_bench --models vllm_api_stream_chat --datasets demo_gsm8k_gen_4_shot_cat_chat_prompt --summarizer default_perf --mode perf`（原文命令为 `demo_gsm8k_gen_4_shot_cot_chat_prompt`）。
