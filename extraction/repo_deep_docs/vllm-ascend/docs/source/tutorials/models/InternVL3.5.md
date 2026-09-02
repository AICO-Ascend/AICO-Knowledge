# InternVL3.5(38B/241B-A28B)

> 仓 `vllm-ascend` · 路径 `docs/source/tutorials/models/InternVL3.5.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm-ascend/docs/source/tutorials/models/InternVL3.5.md

# InternVL3.5 (38B/241B-A28B) 部署指南深度解读

## 【定位】

这篇文档是 vllm-ascend 项目对 InternVL3.5 多模态模型（38B 稠密版与 241B-A28B MoE 版）的端到端部署验证指南，覆盖从环境准备、Docker/源码安装、单节点在线部署、curl 功能验证，到精度与性能评估的全流程，目标是在 Atlas 800 A3 (64GB × 16) NPU 上跑通 InternVL3.5 的 w8a8 量化版本。

## 【技术要点】

1. **支持版本与硬件门槛**：InternVL3.5 在 `vllm-ascend:v0.20.2` 中首次支持；`InternVL3_5-38B-w8a8` 与 `InternVL3_5-241B-A28B-w8a8`（均来自 ModelScope 的 Eco-Tech 量化版）均需要 **1 台 Atlas 800 A3 (64GB × 16)** 节点承载。
2. **Docker 镜像**：使用 `quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}-a3`（即 v0.20.2-a3），需 `--net=host`、`--shm-size=1g`，并把 16 张 NPU (`/dev/davinci0` ~ `/dev/davinci15`)、`/dev/davinci_manager`、`/dev/devmm_svm`、`/dev/hisi_hdc` 全部透传。
3. **系统层调优（两套部署共用）**：CPU governor 设为 performance；`vm.swappiness=0`、`kernel.numa_balancing=0`、`kernel.sched_migration_cost_ns=50000`。
4. **NPU/HCCL 环境变量**：`PYTORCH_NPU_ALLOC_CONF=expandable_segments:True`、`TASK_QUEUE_ENABLE=1`、`HCCL_OP_EXPANSION_MODE="AIV"`、`OMP_PROC_BIND=false`、`OMP_NUM_THREADS=1`、`VLLM_USE_V1=1`、`VLLM_TORCH_PROFILER_WITH_STACK=0`、`HCCL_BUFFSIZE=1536`。
5. **38B 部署关键参数**：`--max-model-len 40960`、`--max-num-batched-tokens 16384`、`--tensor-parallel-size 4`、`--max-num-seqs 32`、`--gpu-memory-utilization 0.9`、CUDAgraph 捕获 sizes `[4,32,64,128,192,256,512]`，**未启用** expert parallel。
6. **241B-A28B 部署关键参数**：在 38B 配置基础上 `--tensor-parallel-size 4` 之外叠加 `--data-parallel-size 2`、`--max-num-batched-tokens 4096`、`--max-num-seqs 70`、`--enable-expert-parallel`（用于 MoE 的专家并行），CUDAgraph 仅保留 `FULL_DECODE_ONLY`。
7. **Ascend 专属附加配置**：`--additional-config '{"enable_weight_nz_layout": true, "enable_cpu_binding": true,"enable_fused_mc2":1}'`；`enable_fused_mc2` 用于开启 dispatch_ffn_combine/mega_moe 融合算子。
8. **多模态/加载选项**：`--mm-processor-cache-gb 0`、`--enable-chunked-prefill`、`--safetensors-load-strategy 'prefetch'`、`--allowed-local-media-path "/"`。
9. **多节点 PD 分离部署**：原文明确"**Not support yet**"。
10. **功能验证请求**：OpenAI 兼容的 `/v1/chat/completions`，输入为远程图片 URL + 文本，期望回复 "The text in the illustration is: **a tiger**"。

## 【关键机制与数据】

- **工作原理**：以 vLLM-Ascend 提供的 OpenAI 兼容 HTTP 服务为入口，模型权重由 `safetensors-load-strategy='prefetch'` 预取；量化 (w8a8) 权重经 NZ 格式 layout (`enable_weight_nz_layout`) 转换后通过 HCCL AIV 通路在 16 张 NPU 上做张量并行 +（仅 241B）专家并行 + 数据并行；CPU 与 NPU 通过 `enable_cpu_binding` 绑核，避免跨 NUMA 抖动。
- **数据流（38B）**：单节点 16 卡中取 4 卡做 TP，其余卡空闲；输入图像通过 `--allowed-local-media-path "/"` 授权后由 multimodal processor（`mm-processor-cache-gb 0` 表示不缓存多模态预处理结果）解析；KV cache 在 chunked prefill 与 decode 之间复用，CUDAgraph 仅在 decode 阶段捕获并以多档 batch size 复用。
- **数据流（241B-A28B）**：4 卡 TP × 2 副本 DP 处理 MoE 路由后的 expert 切片；expert parallel 启用后，all-to-all 通过 HCCL 完成，并由 `enable_fused_mc2` 把 dispatch/combine 融合为单个算子。
- **性能数据**：
  - 原文功能验证响应字段：`prompt_tokens=107`、`completion_tokens=16`、`total_tokens=123`（基于一张示例图片 + 一句短文本提问）。
  - 性能数字（吞吐/时延）：原文未给出具体 TPS 或 latency，仅声明"参数已在特定测试环境验证、需按实际调整"。

## 【表格解读】

原文中的 Table 1（位于 §9.1 Recommended Configurations > Scenario Overview）表头如下，**正文在表头第二行处被截断，原文未提供完整的 Scenario / Deployment Mode / Total NPUs / Weight Version / Key Considerations 内容**：

| Scenario | Deployment Mode | *Total NPUs | Weight Version | Key Considerations |
| ---------- | ---------------- | ----------- | -------------- | ------------------- |

> 说明：原文在第二个分隔行 `| ---------- | ---------------- | -----------` 之后没有继续渲染数据行；后续表格内容在提供的原文中缺失。因此这里只能"逐字还原"出表头并标注截断，**不臆造原文没有的字段值**。结合文中其他章节可推断该表计划汇总若干场景（如 38B 单节点、241B 单节点等）的部署模式、所需 NPU 数、权重版本和注意事项，但这些条目**原文未给出**。

## 【公式解读】

原文无公式（无 LaTeX 或伪代码形式的数学表达式）。

## 【关联】

- **支持矩阵**：`../../user_guide/support_matrix/supported_models.md` —— §2 引用，确认 InternVL3.5 在 vllm-ascend 中实际启用的特性矩阵（图文理解、tool calling 等是否开启以此为准）。
- **特性配置索引**：`../../user_guide/feature_guide/index.md` —— §2 配套链接，介绍每个特性的开关配置（与 §5 中 `--enable-chunked-prefill`、`--enable-expert-parallel` 等开关对应）。
- **安装指南**：`../../getting_started/installation.md` —— §4.1、§4.2 引用，提供 Docker 与源码两种安装路径的细节。
- **常见问题**：`../../faqs.md`（§5.1 两次引用）—— 对在线推理中遇到的网络、HCCL、显存等"公共问题"的解答。
- **Ascend 附加配置**：`../../user_guide/configuration/additional_config.md` —— §5.1 Notice 引用，解释 `--additional-config` 中所有 Ascend 专属 key 的含义（如 `enable_weight_nz_layout`、`enable_cpu_binding`、`enable_fused_mc2`）。
- **Ascend 环境变量**：`../../user_guide/configuration/env_vars.md` —— §5.1 Notice 引用，给出 `HCCL_OP_EXPANSION_MODE`、`HCCL_BUFFSIZE`、`TASK_QUEUE_ENABLE`、`PYTORCH_NPU_ALLOC_CONF` 等环境变量的官方说明。
- **AISBench 精度评估**：`../../developer_guide/evaluation/using_ais_bench.md` —— §7.1 引用，InternVL3.5 精度验证流程。
- **AISBench 性能评估**：`../../developer_guide/evaluation/using_ais_bench.md#execute-performance-evaluation` —— §8.1 引用，InternVL3.5 性能基准流程。
- **vLLM Benchmark**：外链 https://docs.vllm.ai/en/latest/benchmarking/，§8.2 引用，补充原厂基准工具说明。

## 【使用方法】

**1. 准备模型权重**（两选一，二者均为 w8a8 量化版，部署在单台 Atlas 800 A3 64GB×16 节点上）：
- `InternVL3_5-38B-w8a8`：[ModelScope 下载](https://modelscope.cn/models/Eco-Tech/InternVL3_5-38B-w8a8)
- `InternVL3_5-241B-A28B-w8a8`：[ModelScope 下载](https://modelscope.cn/models/Eco-Tech/InternVL3_5-241B-A28B-w8a8)

**2. 启动容器**（Docker 方式，节选关键变量）：
```bash
export IMAGE=quay.io/ascend/vllm-ascend:v0.20.2-a3
export NAME=vllm-ascend
docker run --rm --name $NAME --net=host --shm-size=1g \
  --device /dev/davinci0 ... --device /dev/davinci15 \
  --device /dev/davinci_manager --device /dev/devmm_svm --device /dev/hisi_hdc \
  -v /usr/local/dcmi:/usr/local/dcmi \
  -v /root/.cache:/root/.cache \
  -it $IMAGE bash
```
（多机通信需额外暴露端口。）

**3. 在线推理 — 38B 单节点**：
```bash
echo performance | tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
sysctl -w vm.swappiness=0
sysctl -w kernel.numa_balancing=0
sysctl -w kernel.sched_migration_cost_ns=50000

export PYTORCH_NPU_ALLOC_CONF=expandable_segments:True
export TASK_QUEUE_ENABLE=1
export HCCL_OP_EXPANSION_MODE="AIV"
export OMP_PROC_BIND=false
export OMP_NUM_THREADS=1
export VLLM_USE_V1=1
export VLLM_TORCH_PROFILER_WITH_STACK=0
export HCCL_BUFFSIZE=1536

vllm serve /root/.cache/modelscope/hub/models/vllm-ascend/InternVL3_5-38B-w8a8/ \
    --port 2002 \
    --served-model-name internvl3_5 \
    --trust-remote-code \
    --max-model-len 40960 \
    --max-num-batched-tokens 16384 \
    --tensor-parallel-size 4 \
    --max-num-seqs 32 \
    --gpu-memory-utilization 0.9 \
    --compilation-config '{"cudagraph_mode":"FULL_DECODE_ONLY", "cudagraph_capture_sizes":[4,32,64,128,192,256,512]}' \
    --additional-config '{"enable_weight_nz_layout": true, "enable_cpu_binding": true,"enable_fused_mc2":1}' \
    --mm-processor-cache-gb 0 \
    --enable-chunked-prefill \
    --safetensors-load-strategy 'prefetch' \
    --allowed-local-media-path "/"
```

**4. 在线推理 — 241B-A28B 单节点**：
```bash
vllm serve /root/.cache/modelscope/hub/models/vllm-ascend/InternVL3_5-241B-A28B-w8a8/ \
    --port 2001 \
    --served-model-name internvl3_5 \
    --trust-remote-code \
    --max-model-len 40960 \
    --max-num-batched-tokens 4096 \
    --tensor-parallel-size 4 \
    --data-parallel-size 2 \
    --max-num-seqs 70 \
    --gpu-memory-utilization 0.9 \
    --compilation-config '{"cudagraph_mode":"FULL_DECODE_ONLY"}' \
    --additional-config '{"enable_weight_nz_layout": true, "enable_cpu_binding": true,"enable_fused_mc2":1}' \
    --mm-processor-cache-gb 0 \
    --enable-chunked-prefill \
    --enable-expert-parallel \
    --safetensors-load-strategy 'prefetch' \
    --allowed-local-media-path "/"
```

**5. 功能验证（curl 图像问答）**：
```bash
curl http://localhost:8000/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d '{
    "model": "internvl3_5",
    "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": [
        {"type": "image_url", "image_url": {"url": "https://modelscope.oss-cn-beijing.aliyuncs.com/resource/tiger.jpeg"}},
        {"type": "text", "text": "What is the text in the illustration?"}
    ]}
    ]
    }'
```
期望答复中 `content` 为 `The text in the illustration is: **a tiger**`，并附 `prompt_tokens=107, completion_tokens=16, total_tokens=123`。

**6. 精度与性能评估**：
- 精度：使用 AISBench（参见 `using_ais_bench.md`）。
- 性能：可使用 AISBench（`using_ais_bench.md#execute-performance-evaluation`）或 vLLM 原生 benchmark（https://docs.vllm.ai/en/latest/benchmarking/）。

**7. 参数调优原则**（原文 Notice 强调）：上述数值仅在特定测试环境下验证，实际部署需依据**输入/输出长度、并发量、硬件拓扑**重新调整 `--max-model-len`、`--max-num-seqs`、`--max-num-batched-tokens`、`--gpu-memory-utilization`；Ascend 专属 key 与环境变量的完整含义见 `additional_config.md` 与 `env_vars.md`。
