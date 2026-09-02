# Kimi-K2.5

> 仓 `vllm-ascend` · 路径 `docs/source/tutorials/models/Kimi-K2.5.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm-ascend/docs/source/tutorials/models/Kimi-K2.5.md

# Kimi-K2.5 部署指南 — 一体化深度解读

## 【定位】

本篇文档面向在 vLLM-Ascend 上部署并验证 **Kimi-K2.5**（基于 Kimi-K2-Base 持续预训练的开源原生多模态 agentic 模型）的工程场景，给出从模型权重、镜像/源码安装、单节点在线服务到多节点部署、精度与性能评估的全链路操作指引。文档的版本基线明确锁定在 **vLLM-Ascend v0.17.0rc1**，并声明该版本起 Kimi-K2.5 首次获得稳定运行支持。

---

## 【技术要点】

1. **模型与权重** — Kimi-K2.5 是在 ~15 万亿（原文 "approximately 15 trillion"）混合视觉/文本 token 上持续预训练而来；其工程化交付包含两个权重：
   - `Kimi-K2.5-w4a8`（量化版本）：1 节点 Atlas 800 A3（64GB × 16）或 2 节点 Atlas 800 A2（64GB × 8）。
   - `kimi-k2.5-eagle3`：Eagle3 MTP 投机解码 draft 模型，配合主模型做推理加速。

2. **Atlas 硬件拓扑建议** — A3 单节点即可承载 w4a8 量化主模型；多节点仅在 A2 场景或更大规模需求下使用。单节点推荐并行策略 **`dp4 tp4`**，原文显式不推荐 `dp2 tp8`。

3. **关键运行时环境变量** —
   - `HCCL_BUFFSIZE=800`
   - `HCCL_OP_EXPANSION_MODE="AIV"`
   - `PYTORCH_NPU_ALLOC_CONF=expandable_segments:True`
   - `OMP_PROC_BIND=false`、`OMP_NUM_THREADS=1`
   - `TASK_QUEUE_ENABLE=1`
   - 可选 `LD_PRELOAD=/usr/lib/aarch64-linux-gnu/libjemalloc.so.2:$LD_PRELOAD`（jemalloc 提升性能）。

4. **系统层调优（sysctl/调速器）** —
   - `sysctl -w vm.swappiness=0`
   - `sysctl -w kernel.numa_balancing=0`
   - `sysctl -w kernel.sched_migration_cost_ns=50000`
   - `echo performance | tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor`

5. **vLLM serve 关键参数** —
   - 并行：`--tensor-parallel-size 4`、`--data-parallel-size 4`、`--enable-expert-parallel`。
   - 显存/上下文：`--gpu-memory-utilization 0.9`、`--max-num-seqs 64`、`--max-model-len 32768`、`--max-num-batched-tokens 16384`。
   - 量化/前缀缓存：`--quantization ascend`、`--no-enable-prefix-caching`（开启前缀缓存需去掉该参数）。
   - 多模态/工具调用：`--mm-encoder-tp-mode data`、`--enable-auto-tool-choice`、`--tool-call-parser kimi_k2`、`--reasoning-parser kimi_k2`。
   - 编译/调度：`--compilation-config '{"cudagraph_mode":"FULL_DECODE_ONLY"}'`、`--additional-config '{"scheduler_config":{"enable_balance_scheduling":true},"enable_mlapo":true}'`。
   - 投机解码：`--speculative-config '{"method":"eagle3", "model":"lightseekorg/kimi-k2.5-eagle3", "num_speculative_tokens":3}'`。

6. **上下文长度阈值经验** — 性能测试（输入 3.5K / 输出 1.5K）下 `--max-model-len 16384` 即够用；精度测试则需将 `--max-model-len` 设为 **至少 35000**。

---

## 【关键机制与数据】

- **数据/工作流**（原文）：文档将部署生命周期拆为"前置准备（权重 + 多节点互联验证）→ 安装（Docker 镜像 或 源码）→ 在线服务部署（单节点 / 多节点）→ 精度与性能评估"。w4a8 量化模型 + Eagle3 投机解码 + 多模态 encoder TP 是核心运行时组合。
- **balance scheduling 取舍**（原文：`additional_config.scheduler_config.enable_balance_scheduling=true`）：v1 scheduler 下可提升 output 吞吐、降低 TPOT，但 TTFT 在部分场景可能劣化，且 **PD 分离场景不推荐**开启。
- **Eagle3 投机解码参数**（原文）：`method=eagle3`、`num_speculative_tokens=3`、draft 模型为 `lightseekorg/kimi-k2.5-eagle3`。
- **kv cache 与 w4a8 的关系**（原文）：w4a8 权重下系统会分配更多内存给 kv cache，可通过上调系统吞吐（`max-num-seqs` / `max-num-batched-tokens` 等）换取更高吞吐。
- **HTTP 验证契约**（原文）：通过 `curl http://<node_ip>:8088/v1/chat/completions` 调用 `/v1/chat/completions`，期望返回 HTTP 200 且 JSON 含 `choices` 字段；示例请求使用 `model=kimi_k25`、`temperature=1.0`、`top_p=0.95`、`max_tokens=1024`，system 提示为 "The future of AI is"。

> 文档中关于"性能数字 / 精度数字"的实测数据表在给出的原文片段中未出现，**原文未提供具体吞吐量/精度数值**。

---

## 【表格解读】

**原文无表格。**

（给出的原文片段内不包含 markdown 表格；硬件拓扑、参数建议等均以列表/正文形式给出。）

---

## 【公式解读】

**原文无公式。**

（文档主体为 Docker / vLLM serve / curl 命令行示例与说明性文字，未出现 LaTeX 公式或伪代码式公式。）

---

## 【关联】

依据文末列出的内部链接，可梳理出 Kimi-K2.5 指南在 vllm-ascend 文档体系中的上下游关系：

- **能力矩阵 →** [Supported Models](../../user_guide/support_matrix/supported_models.md)：查询 Kimi-K2.5 在 vLLM-Ascend 上的功能支持矩阵（哪些特性可开/受限）。
- **特性配置 →** [Feature Guide](../../user_guide/feature_guide/index.md)：获取本文 `--additional-config`、`--speculative-config`、`--compilation-config` 等特性开关的详细配置说明。
- **多节点互联 →** [Installation — Multi-node Interconnect](../../getting_started/installation.md#installation-multi-node-interconnect)：本文 3.2 节直接引用的多节点通信验证流程。
- **镜像安装 →** [Installation — Prebuilt Image](../../getting_started/installation.md#installation-prebuilt-image)：本文 4.1 节 Docker 启动命令的官方基础说明。
- **通用安装 →** [Installation](../../getting_started/installation.md)：本文 4.2 节源码构建 `vllm-ascend` 的入口。
- **PD 分离（多节点） →** [PD Disaggregation (Mooncake, Multi-node)](../features/pd_disaggregation_mooncake_multi_node.md)：与本文 5.1 节"balance scheduling 在 PD 分离场景不推荐开启"形成互文，决定是否启用 PD 分离部署形态。
- **常见问题 →** [Public FAQs](../../faqs.md)：在"Common Issues Tip"中作为排错跳转入口。
- **评估工具 →** [Using AIS Bench](../../developer_guide/evaluation/using_ais_bench.md)：与本文声称的"精度与性能评估"流程配套的官方评估器使用文档。

---

## 【使用方法】

> 以下命令/配置项均直接来自原文，按使用顺序汇总。

**1. 下载权重（推荐至共享目录 `/root/.cache/`）**

- `Kimi-K2.5-w4a8`：[ModelScope](https://www.modelscope.cn/models/Eco-Tech/Kimi-K2.5-W4A8)
- `kimi-k2.5-eagle3`：[HuggingFace](https://huggingface.co/lightseekorg/kimi-k2.5-eagle3)

**2. Docker 镜像启动（A3 系列）**

```shell
export IMAGE=quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}-a3
docker run --rm \
    --name vllm-ascend \
    --shm-size=1g \
    --net=host --privileged=true \
    --device /dev/davinci0 ... --device /dev/davinci15 \
    --device /dev/davinci_manager --device /dev/devmm_svm --device /dev/hisi_hdc \
    -v /usr/local/dcmi:/usr/local/dcmi \
    -v /usr/local/Ascend/driver/tools/hccn_tool:/usr/local/Ascend/driver/tools/hccn_tool \
    -v /usr/local/bin/npu-smi:/usr/local/bin/npu-smi \
    -v /usr/local/Ascend/driver/lib64/:/usr/local/Ascend/driver/lib64/ \
    -v /usr/local/Ascend/driver/version.info:/usr/local/Ascend/driver/version.info \
    -v /etc/ascend_install.info:/etc/ascend_install.info \
    -v /root/.cache:/root/.cache \
    -it $IMAGE bash
```
（A2 系列镜像 tag 不带 `-a3` 后缀，且只 `--device /dev/davinci0..7`，其余设备与挂载点相同。）

**3. 单节点在线服务启动（A3 节点，量化 w4a8）**

```shell
#!/bin/sh
# [Optional] jemalloc
export LD_PRELOAD=/usr/lib/aarch64-linux-gnu/libjemalloc.so.2:$LD_PRELOAD

echo performance | tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
sysctl -w vm.swappiness=0
sysctl -w kernel.numa_balancing=0
sysctl -w kernel.sched_migration_cost_ns=50000
export HCCL_OP_EXPANSION_MODE="AIV"
export PYTORCH_NPU_ALLOC_CONF=expandable_segments:True
export OMP_PROC_BIND=false
export OMP_NUM_THREADS=1
export TASK_QUEUE_ENABLE=1
export HCCL_BUFFSIZE=800

vllm serve Eco-Tech/Kimi-K2.5-w4a8 \
  --additional-config '{"scheduler_config":{"enable_balance_scheduling":true},"enable_mlapo":true}' \
  --host 0.0.0.0 --port 8088 \
  --quantization ascend \
  --served-model-name kimi_k25 \
  --allowed-local-media-path / \
  --trust-remote-code \
  --no-enable-prefix-caching \
  --seed 1024 \
  --tensor-parallel-size 4 --data-parallel-size 4 \
  --enable-expert-parallel \
  --max-num-seqs 64 \
  --max-model-len 32768 \
  --max-num-batched-tokens 16384 \
  --gpu-memory-utilization 0.9 \
  --compilation-config '{"cudagraph_mode":"FULL_DECODE_ONLY"}' \
  --speculative-config '{"method":"eagle3", "model":"lightseekorg/kimi-k2.5-eagle3", "num_speculative_tokens":3}' \
  --mm-encoder-tp-mode data \
  --enable-auto-tool-choice \
  --tool-call-parser kimi_k2 \
  --reasoning-parser kimi_k2
```

**4. 服务验证（curl）**

```shell
curl http://<node_ip>:8088/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d '{
        "model": "kimi_k25",
        "messages": [{
            "role": "user",
            "content": [
            {
                "type": "text",
                "text": "The future of AI is"
            }]
        }],
        "max_tokens": 1024,
        "temperature": 1.0,
        "top_p": 0.95
    }'
```

**5. 上下文长度经验值（原文给出）**

- 性能测试（输入 3.5K / 输出 1.5K）：`--max-model-len 16384` 即可。
- 精度测试：`--max-model-len` ≥ `35000`。

**6. 启用/关闭要点**

- 关闭前缀缓存：`--no-enable-prefix-caching`；开启则删除该参数。
- 多模态 encoder TP 模式：`--mm-encoder-tp-mode data`（原文建议）。
- 投机解码：默认已配 `num_speculative_tokens=3`。
- 调度：`enable_balance_scheduling=true`（PD 分离场景下不推荐）。
- 多节点环境：需在每个节点分别执行 docker 启动 / 源码安装；多机互联需参照 [installation-multi-node-interconnect](../../getting_started/installation.md#installation-multi-node-interconnect) 验证。

> 说明：给出的原文片段在第 5.1 节"Expected Result"示例 JSON 中被截断，**多节点部署（5.2）、精度/性能评估章节的完整命令与配置项原文未在本片段中给出**——如有需要，应直接回到原文后续小节继续核对。
