# vllm serve

> 来源 https://docs.vllm.ai/en/latest/cli/serve/
> 抓取路由 direct-html · 2026-09-02 17:37 · 原文 95556 字符 · 0 图
> MiniMax-M3 七节深读 · ver=v1 · 原文: extraction/web_docs/vllm-cli-serve.md

# vLLM serve CLI 参数文档 深度解读

## 【定位】

本文档为 `vllm serve` 命令行启动 vLLM 推理服务提供了**完整的参数参考手册**，覆盖从模型加载、并行调度、KV 缓存、注意力/MoE 内核、多模态、LoRA、可观测性到 API 前端配置的全部选项，供运维/开发者在生产部署或调优时按需查阅。

---

## 【技术要点】

### 1. JSON CLI 参数语法约定
- 嵌套字典/JSON 字符串两种写法等价：
  - JSON 形式：`--json-arg '{"key1": "value1", "key2": {"key3": "value2"}}'`
  - 点分键形式：`--json-arg.key1 value1 --json-arg.key2.key3 value2`
- 列表元素可使用 `+` 逐项追加：`--json-arg.key4+ value3 --json-arg.key4+='value4,value5'`

### 2. 通用运行控制
- `--headless` (Default: `False`)、`--config` (从 YAML 读取)
- `--api-server-count, -asc` (默认 = `data_parallel_size`)
- `--grpc` (需 `pip install vllm[grpc]`，Default: `False`)
- `--gdn-prefill-backend`: `flashinfer` / `triton` / `cutedsl`
- `--kda-prefill-backend`: `auto` / `triton` / `flashkda`
- `--shutdown-timeout`（0 = abort，>0 = wait，Default: `0`）

### 3. OpenAI 兼容前端
- 监听：`--host`、`--port` (Default: `8000`)、`--data-parallel-supervisor-port` (Default: `9256`)
- DP Supervisor 探针：`--dp-supervisor-probe-interval-s` (Default: `5.0`)、`--dp-supervisor-probe-timeout-s` (Default: `5.0`)、`--dp-supervisor-probe-failure-threshold` (Default: `3`)
- `--uds`（设置后忽略 `--host/--port`）、`--uvicorn-log-level`（Default: `info`）
- HTTP 防护：`--h11-max-incomplete-event-size` (Default: `4194304`，4 MiB)、`--h11-max-header-count` (Default: `256`)
- CORS：`--allow-credentials` (Default: `False`)、`--allowed-origins/methods/headers` (Default: `['*']`)
- 认证：`--api-key`（⚠️ 仅保护 `/v1`、`/v2`、`/inference` 前缀）
- SSL：`--ssl-keyfile/certfile/ca-certs`、`--ssl-cert-reqs` (Default: `0`)、`--enable-ssl-refresh`
- 工具调用/响应格式：`--enable-auto-tool-choice`、`--tool-call-parser`、`--tool-parser-plugin` (Default: `""`)
- Cohere 模型：`--cohere-is-reasoning-model` (Default: `True`)、`--cohere-format` (Default: `cmd4`)
- 流式/保活：`--sse-keep-alive-interval` (Default: `0`)、`--enable-log-deltas` (Default: `True`)

### 4. ModelConfig（关键模型参数）
- `--model` (Default: `Qwen/Qwen3-0.6B`)、`--runner` (`auto`/`draft`/`generate`/`pooling`)
- `--tokenizer-mode` 支持 8 个取值：`auto`、`cohere`、`deepseek_v32`、`deepseek_v4`、`hf`、`inkling`、`kimi_k3`、`mistral`、`slow`
- `--dtype`: `auto`/`bfloat16`/`float`/`float16`/`float32`/`half`
- `--max-model-len` 支持人类可读单位：`1k`→1000、`1K`→1024、`-1`/`'auto'` → 自动适配显存
- `--quantization, -q` + `--quantization-config` (逐层类型 + 忽略模式)
- `--seed` (Default: `0`)、`--enforce-eager` (Default: `False`)
- `--max-logprobs` (Default: `20`，`-1`=不限制)、`--logprobs-mode` (`processed_logits`/`processed_logprobs`/`raw_logits`/`raw_logprobs`，Default: `raw_logprobs`)
- 模型实现：`--model-impl` (`auto`/`vllm`/`transformers`/`terratorch`)
- 睡眠模式：`--enable-sleep-mode` (仅 CUDA/HIP)，`--enable-cumem-allocator`，`--enable-nccl-comm-suspend`
- 渲染线程池：`--renderer-num-workers` (Default: `1`，仅对异步 online 路径生效)

### 5. LoadConfig（权重加载）
- `--load-format` 12+ 取值：`auto`/`safetensors`/`pt`/`instanttensor`/`npcache`/`dummy`/`tensorizer`/`runai_streamer`/`runai_streamer_sharded`/`sharded_state`/`mistral`/`modelexpress`
- `--safetensors-load-strategy`：`None` (mmap lazy)、`lazy`、`eager`、`prefetch`、`torchao`（None 在 NFS 总大小 ≤ 90% RAM 时自动 prefetch）
- `--safetensors-prefetch-num-threads` (Default: `8`)、`--safetensors-prefetch-block-size` (Default: `16777216`，即 16 MiB)
- `--pt-load-map-location` (Default: `cpu`)

### 6. ParallelConfig（分布式执行）
- 后端：`--distributed-executor-backend` (`external_launcher`/`mp`/`ray`/`uni`)，TPU 仅支持 Ray
- 主节点（`mp` 多节点）：`--master-addr` (Default: `127.0.0.1`)、`--master-port` (Default: `29501`)、`--nnodes`/`-n` (Default: `1`)、`--node-rank`/`-r` (Default: `0`)
- 张量并行：`--tensor-parallel-size, -tp` (Default: `1`)
- 上下文并行：`--decode-context-parallel-size, -dcp`、`--prefill-context-parallel-size, -pcp`、`--dcp-comm-backend` (`a2a`/`ag_rs`)、`--dcp-kv-cache-interleave-size`/`--cp-kv-cache-interleave-size` (Default: `1`)
- 数据并行：`--data-parallel-size, -dp` (Default: `1`)、`--data-parallel-backend, -dpb` (Default: `mp`)
- 混合/外部 LB：`--data-parallel-hybrid-lb, -dph`/`--data-parallel-external-lb, -dpe`/`--data-parallel-multi-port-external-lb, -dpm`
- 专家并行：`--enable-expert-parallel, -ep` (Default: `False`)、`--enable-eplb` (Default: `False`)、`--eplb-config` (Default: `window_size=1000, step_interval=3000, num_redundant_experts=0`)、`--expert-placement-strategy` (`linear`/`round_robin`，Default: `linear`)
- All2All 后端（12 个）：`allgather_reducescatter` (Default)、`deepep_high_throughput`、`deepep_low_latency`、`deepep_v2`、`mori_high_throughput`、`mori_low_latency`、`nixl_ep`、`flashinfer_nvlink_one_sided`、`flashinfer_nvlink_two_sided`、`flashinfer_all2allv`、`naive`、`pplx`
- NUMA 绑定：`--numa-bind` (Default: `False`)、`--numa-bind-nodes/cpus`
- 双批次重叠：`--enable-dbo` (Default: `False`)、`--uboatch-size` (Default: `0`)、`--dbo-decode-token-threshold` (Default: `32`)、`--dbo-prefill-token-threshold` (Default: `512`)
- 容错：`--enable-fault-tolerance` (Default: `False`)、`--fault-tolerance-config` (Default: `engine_recovery_timeout_sec=120`)

### 7. CacheConfig（KV 缓存）
- `--gpu-memory-utilization` (Default: `0.92`)
- `--kv-cache-dtype` 含 17 个取值：`auto` (Default)、`bfloat16`/`float16`/`fp8`/`fp8_ds_mla`/`fp8_e4m3`/`fp8_e5m2`/`fp8_inc`/`fp8_per_token_head`/`int4_per_token_head`/`int8_per_token_head`/`nvfp4`/`nvfp4_4over6`/`nvfp4_ds_mla`/`turboquant_3bit_nc`/`turboquant_4bit_nc`/`turboquant_k3v4_nc`/`turboquant_k8v4`
- 前缀缓存哈希：`sha256` (Default，安全)/`sha256_cbor`/`xxhash`/`xxhash_cbor`（xxHash 速度更快但有哈希碰撞风险）
- KV 卸载：`--kv-offloading-size` (GiB) + `--kv-offloading-backend` (`lmcache`/`native`，Default: `native`)
- Mamba 缓存：`--mamba-cache-dtype` (`auto`/`bfloat16`/`float16`/`float32`)、`--mamba-ssm-cache-dtype`、`--mamba-cache-mode` (`align`/`all`/`none`，Default: `none`)、`--use-replayssm`
- 滑动窗口保留：`--prefix-cache-retention-interval` (Default: `0`)
- KV Sharing 快预填充：`--kv-sharing-fast-prefill` (不兼容 MRv2)

### 8. MultiModalConfig
- `--limit-mm-per-prompt`（含 `count`/`num_frames`/`width`/`height` 配置）
- FP8 ViT 编码器量化：`--mm-encoder-attn-dtype` (`fp8`/`None`)、`--mm-encoder-fp8-scale-path`/`--mm-encoder-fp8-scale-save-path`/`--mm-encoder-fp8-scale-save-margin` (Default: `1.5`)
- IPC 传输：`--mm-tensor-ipc` (`direct_rpc` Default / `torch_shm` 零拷贝)
- MM 缓存：`--mm-processor-cache-gb` (Default: `4`，每个 API+engine core 进程独立一份)、`--mm-processor-cache-type` (`lru`/`shm`)、`--mm-hasher-algorithm` (`blake3` Default / `sha256` / `sha512`)
- 视频 token 剪枝：`--video-pruning-rate`、`--video-pruning-method` (`evs` Default / `vidcom2`)
- 编码器 TP 模式：`--mm-encoder-tp-mode` (`data`/`weights`，Default: `weights`)

### 9. LoRAConfig
- `--enable-lora`、`--max-loras` (Default: `1`)、`--max-lora-rank` (Default: `16`，9 档可选)
- `--lora-dtype` (Default: `auto`)、`--fully-sharded-loras` (Default: `False`)
- MoE LoRA 专用：`--enable-mixed-moe-lora-format`/`--enable-moe-shared-loras`
- MM LoRA：`--enable-tower-connector-lora`、`--default-mm-loras`、`--specialize-active-lora`

### 10. ObservabilityConfig
- OTel traces：`--otlp-traces-endpoint`、`--collect-detailed-traces`
- KV cache metrics：`--kv-cache-metrics` (Default: `False`)、`--kv-cache-metrics-sample` (Default: `0.01`)
- `--enable-layerwise-nvtx-tracing` (与 CUDA graph 冲突)、`--enable-mfu-metrics`
- JIT 监听：`--jit-monitor-mode` (`error`/`warn`，Default: `warn`)、`--jit-monitor-verbose`

### 11. SchedulerConfig
- 容量阀：`--max-num-batched-tokens`、`--max-num-seqs`、`--max-num-queued-reqs`、`--max-num-queued-tokens`
- `--scheduling-policy` (`fcfs` Default / `priority`)
- 长预填阈值：`--long-prefill-token-threshold` (Default: `0`)、`--enable-chunked-prefill`
- KV 腾挪：`--watermark` (Default: `0.0`)、`--scheduler-reserve-full-isl` (Default: `True`)
- 异步：`--async-scheduling`、`--stream-interval` (Default: `1`)、`--prefill-schedule-interval` (Default: `1`)

### 12. KernelConfig / CompilationConfig
- MoE 后端 18 选 1：`auto` (Default)、`triton`、`batched_triton`、`deep_gemm`、`deep_gemm_mega_moe`、`cutlass`、`flashinfer_trtllm`、`flashinfer_cutlass`、`flashinfer_cutedsl` (FP4)、`flashinfer_b12x` (SM12x)、`b12x`、`flashinfer_moe_ep_mega_deep_gemm` (MXFP4 Blackwell)、`flashinfer_moe_ep_mega_cutedsl`、`marlin`、`humming`、`triton_unfused`、`aiter`/`aiter_triton_mxfp4_bf16`、`flydsl`、`hpc`、`emulation`
- Linear 后端 21 选 1：`auto`、`cutlass`、`flashinfer_cutlass`、`flashinfer_cutedsl`、`flashinfer_trtllm`、`flashinfer_cudnn`、`flashinfer_b12x`、`b12x`、`marlin`、`triton`、`deep_gemm`、`torch`、`aiter`、`machete`、`fbgemm`、`conch`、`exllama`、`emulation`、`xpu`、`xpu_woq`、`humming`
- CompilationConfig 默认：`backend='inductor'`, `compile_mm_encoder=False`, `dynamic_shapes_config.type='backed'`, `cudagraph_specialize_lora=True`
- `--cudagraph-capture-sizes` 自动模式（无显式列表时）：`[1, 2, 4] + list(range(8, 256, 8)) + list(range(256, max_cudagraph_capture_size + 1, 16))`，`max_cudagraph_capture_size` 默认上限 **512**（数据级 Blackwell 为 **1024**）

### 13. VllmConfig 顶层 / 性能优化
- 推测解码：`--spec-method` 支持 38 种（含 `ngram`、`ngram_gpu`、`eagle`、`eagle3`、`medusa`、`mlp_speculator`、`deepseek_mmtp`、`mtp`、各厂商 `_mtp` 后缀…）、`--spec-model`、`--spec-tokens`、`--speculative-config, -sc`
- 传输：KV 传输 (`--kv-transfer-config`)、事件发布 (`--kv-events-config`)、EC 编码器传输 (`--ec-transfer-config`)、RL 权重迁移 (`--weight-transfer-config`)
- 性能模式：`--optimization-level` (Default: `2`，-O0 最快启动 / -O3 最高性能)、`--performance-mode` (`balanced` Default / `interactivity` / `throughput`)

---

## 【关键机制与数据】

### JSON CLI 参数编码机制（原文：第 1 段）
`--json-arg` 既接受 JSON 字符串，也接受点分键（`--json-arg.key1 value1 --json-arg.key2.key3 value2`）的等价形式；列表通过 `+` 后缀逐项追加（`--json-arg.key4+ value3 --json-arg.key4+='value4,value5'`）。这是关键的可读性设计，复杂嵌套参数无需手写 JSON 转义。

### DP Supervisor 多端口外部 LB（原文：`--data-parallel-multi-port-external-lb` / `--dp-supervisor-*`）
启动一个 node-local supervisor，每个本地 DP 副本各自起一个 API server，再把聚合健康状态暴露到 supervisor port（默认 `9256`）。子节点健康探针：间隔 `5.0s`、超时 `5.0s`、失败阈值 `3`。这是 K8s 中 "one-pod-per-rank" MoE 部署的官方推荐路径。

### `--api-key` 安全边界（原文：`--api-key` 警告段落）
仅保护 `/v1`、`/v2`、`/inference` 前缀；`/invocations` 暴露相同推理能力但**不要求 api-key**。原文提醒"do not rely on `--api-key` alone to secure vLLM"。

### KV 缓存密度与 dtype 强耦合（原文：`--kv-cache-dtype`）
DeepSeekV3.2 等模型默认 `fp8`；CUDA 11.8+ 支持 `fp8_e4m3`/`fp8_e5m2`；ROCm 仅支持 `fp8_e4m3`；Gaudi 通过 `fp8_inc`；MLA 模型可使用 `fp8_ds_mla`。`--kv-cache-dtype-skip-layers` 接受层索引或类型名（如 `sliding_window`）。

### cudagraph 自动捕获尺寸公式（原文：`--max-cudagraph-capture-size`）
当 `--cudagraph-capture-sizes` 未显式给出时，捕获列表按 ` [1, 2, 4] + list(range(8, 256, 8)) + list(range(256, max_cudagraph_capture_size + 1, 16)) ` 自动生成；`max_cudagraph_capture_size` 默认 **512**，Blackwell 数据中心 GPU 提升至 **1024**。

### `--max-model-len` 人类可读解析（原文：`--max-model-len`）
`1k`→`1,000`、`1K`→`1,024`、`25.6k`→`25,600`、`-1` 或 `'auto'` → 自动选择能装入 GPU 显存的上下文最大值。

### SAB 量化跳过层（原文：`--prefix-caching-hash-algo`）
默认 SHA256 + Pickle（最安全）；xxHash 速度更快但存在哈希碰撞风险，原文明确警告多租户环境下可能泄露私有信息。

### 多模态缓存放大效应（原文：`--mm-processor-cache-gb`）
总占用 = `mm_processor_cache_gb * (api_server_count + data_parallel_size)`，每个进程独立占用——直接放大 DP 部署内存。

### `--renderer-num-workers` 只作用于异步路径（原文：默认 `1`）
离线 `LLM` 入口使用同步渲染，此参数不生效；只有 async 渲染路径（如 OpenAI API server）才会真正派发到该线程池。

### DCP A2A 后端差异（原文：`--dcp-comm-backend`）
MLA 解码阶段：`ag_rs` 是 AllGather + ReduceScatter 三次 NCCL；`a2a` 用 All-to-All + LSE + Triton kernel 合并，将每次 layer 的 NCCL 调用从 **3 降到 2**，对 MLA 模型显著降低通信开销。

### EPLB 默认配置（原文：`--eplb-config` 默认值）
`window_size=1000, step_interval=3000, num_redundant_experts=0, log_balancedness=False, log_balancedness_interval=1, use_async=True, policy='default', communicator=None`。

### 编解码安全组合（原文：`--mm-encoder-fp8-scale-save-margin` Default: `1.5`）
大于 1 留出 headroom，防止输入激活大于标定集时 FP8 溢出。配合 dynamic scaling 自动保存路径 `--mm-encoder-fp8-scale-save-path` 完成一次性校准。

### DP-LB 模式三分法（原文：`--data-parallel-*`）
- `mp` Default：node 内部数据并行
- `hybrid` (`-dph`)：node 内部 vLLM 自有 LB + 跨 node 外部 LB
- `external` (`-dpe`)：每 rank 一个 pod，仅支持 MoE；非 MoE 应启动独立实例
- `multi_port_external` (`-dpm`)：每个 DP rank 独立 API server，supervisor 聚合健康端点

### 推测解码方法白名单（原文：`--spec-method`）
38 个值，包括通用 `ngram`/`ngram_gpu`/`eagle`/`eagle3`/`medusa`/`mlp_speculator`/`mtp`，各厂商私有 `*_mtp`，以及模型级 `deepseek_mtp`/`qwen3_5_mtp`/`qwen4_exp_mtp`/`kimi_k3_mtp`/`longcat_flash_mtp`/`gemma4_mtp`/`step3p5_mtp`/`dots3_note_mtp`/`ernie_mtp`/`exaone4_5_mtp`/`exaone_moe_mtp`/`extractive_hidden_states`/`pangu_ultra_moe_mtp`/`mimo_mtp`/`mimo_v2_mtp`/`minimax_m3_mtp`/`mlp_speculator`/`dflash`/`dspark`/`hy_v3_mtp`/`hy_v4_mtp`/`bailing_hybrid_mtp`/`bailing_hybrid_v3_mtp`/`glm4_moe_mtp`/`glm4_moe_lite_mtp`/`glm_ocr_mtp`/`inkling_mtp`/`nemotron_h_mtp`/`suffix`/`custom_class`。

---

## 【表格解读】

原文没有显式表格形式，只有按 `--flag` 标签排列的定义列表。以下用 markdown 表格**逐字还原**几个最有分类价值的参数组，再做归并解读。

### A. 通用运行与前端网络默认值

| 参数 | 默认值 / 可能取值 | 原文关键说明 |
|------|------------------|--------------|
| `--api-server-count, -asc` | Defaults to `data_parallel_size` if not specified | How many API server processes to run |
| `--port` | `8000` | Port number |
| `--data-parallel-supervisor-port` | `9256` | HTTP port for aggregated health endpoints in multi-port external LB mode |
| `--dp-supervisor-probe-interval-s` | `5.0` | Seconds between aggregated health probes in multi-port external LB mode |
| `--dp-supervisor-probe-timeout-s` | `5.0` | Seconds to wait between retries when a child health probe fails with a connection error in multi-port external LB mode |
| `--dp-supervisor-probe-failure-threshold` | `3` | Number of consecutive connection-error retries before a child health probe is declared failed in multi-port external LB mode |
| `--uvicorn-log-level` | `info` | 取值: `critical`/`debug`/`error`/`info`/`trace`/`warning` |
| `--disable-uvicorn-access-log` | `False` | Disable uvicorn access log |
| `--allowed-origins` / `-methods` / `-headers` | `['*']` | 默认全放行 |
| `--allow-credentials` | `False` | Allow credentials |
| `--h11-max-incomplete-event-size` | `4194304` (4 MiB) | Maximum size (bytes) of an incomplete HTTP event |
| `--h11-max-header-count` | `256` | Maximum number of HTTP headers allowed |
| `--sse-keep-alive-interval` | `0` | SSE 心跳间隔 |
| `--enable-log-deltas` | `True` | — |
| `--cohere-is-reasoning-model` | `True` | — |
| `--cohere-format` | `cmd4` | — |
| `--fingerprint-mode` | `full` | 取值: `custom`/`full`/`hash`/`none` |
| `--fingerprint-value` | — | 未列默认值 |
| `--enable-flash-late-interaction` | `True` | pooling score MaxSim on GPU |

**解读**：前端默认监听 `0.0.0.0:8000`；CORS 默认全开（生产建议收紧 `--allowed-origins`）；`--api-server-count` 与 DP 强耦合，DP > 1 时自动复制 API server。`--h11-*` 防御 header abuse，建议在公网部署时显式降低。

---

### B. ModelConfig 默认值对照

| 参数 | 默认 | 可选取值 |
|------|------|----------|
| `--model` | `Qwen/Qwen3-0.6B` | — |
| `--runner` | `auto` | `auto`/`draft`/`generate`/`pooling` |
| `--convert` | `auto` | `auto`/`classify`/`embed`/`none` |
| `--tokenizer-mode` | `auto` | `auto`/`cohere`/`deepseek_v32`/`deepseek_v4`/`hf`/`inkling`/`kimi_k3`/`mistral`/`slow` |
| `--dtype` | `auto` | `auto`/`bfloat16`/`float`/`float16`/`float32`/`half` |
| `--seed` | `0` | — |
| `--trust-remote-code` | `False` | — |
| `--allowed-local-media-path` | `""` | — |
| `--max-model-len` | 来自 model config | 支持 `1k`/`1K`/`-1`/`auto` |
| `--max-logprobs` | `20` | `-1` 表示不限制 |
| `--logprobs-mode` | `raw_logprobs` | `processed_logits`/`processed_logprobs`/`raw_logits`/`raw_logprobs` |
| `--disable-cascade-attn` | `True` | 默认关闭，要 opt-in 设为 `False` |
| `--skip-tokenizer-init` | `False` | — |
| `--enable-prompt-embeds` | `False` | ⚠️ 引擎可能因错误 shape 崩溃 |
| `--served-model-name` | = `--model` | — |
| `--config-format` | `auto` | `auto`/`hf`/`mistral` |
| `--generation-config` | `auto` | `"auto"`/`"vllm"`/folder path |
| `--override-generation-config` | `{}` | JSON |
| `--enable-sleep-mode` | `False` | 仅 cuda / hip |
| `--enable-cumem-allocator` | `False` | 睡眠模式自动启用；多节点 NVLink |
| `--enable-nccl-comm-suspend` | `False` | 实验性，启用 suspend NCCL comm |
| `--model-impl` | `auto` | `auto`/`terratorch`/`transformers`/`vllm` |
| `--renderer-num-workers` | `1` | 仅 async 路径生效 |

**解读**：`--dtype=auto` 在 FP32/FP16 模型上用 FP16，在 BF16 上用 BF16；`AWQ` 推荐 `half`。`--tokenizer-mode=cohere` 走 `cohere_melody` cmd3/cmd4 渲染 chat 模板并暴露 grounded-citation metadata；`kimi_k3` 走 Python XTML 不走 Jinja。Bfloat16 是精度/范围平衡的常见选择；`float` ≡ `float32`。

---

### C. CacheConfig 关键默认值

| 参数 | 默认 | 取值/说明 |
|------|------|-----------|
| `--block-size` | `None`（自动） | — |
| `--gpu-memory-utilization` | `0.92` | per-instance 限制 |
| `--kv-cache-memory-bytes` | `None`（自动） | 支持 `1k`/`2M` 等 |
| `--kv-cache-dtype` | `auto` | 17 取值（见上） |
| `--num-gpu-blocks-override` | `None` | 测试抢占 |
| `--enable-prefix-caching` | — | 未列出默认值 |
| `--prefix-caching-hash-algo` | `sha256` | `sha256`/`sha256_cbor`/`xxhash`/`xxhash_cbor` |
| `--prefix-cache-retention-interval` | `0` | 0=仅语义 checkpoint |
| `--kv-cache-dtype-skip-layers` | `[]` | 例: `'0','2','4'` 或 `'sliding_window'` |
| `--kv-sharing-fast-prefill` | `False` | 不支持 MRv2 |
| `--mamba-cache-dtype` / `--mamba-ssm-cache-dtype` | `auto` | `auto`/`bfloat16`/`float16`/`float32` |
| `--mamba-cache-mode` | `none` | `align`/`all`/`none` |
| `--replayssm-buffer-len` | `16` | Mamba2 history length B；Triton 用 B 物理行，FlashInfer 用 B+1 |
| `--use-replayssm` | `False` | 需 `mamba_cache_mode='none'/'align'` |
| `--kv-offloading-size` | `None` | GiB；TP>1 时为 TP 总和 |
| `--kv-offloading-backend` | `native` | `lmcache`/`native` |

**解读**：默认使用 92% GPU 内存，预留 8% 给系统/激活；kv-cache-dtype `auto` 跟随模型 dtype。`xxhash` 哈希算法原文明确警告多租户环境哈希碰撞风险。`--mamba-cache-mode` 在 prefix caching 启用时默认变 `align`。

---

### D. MultiModalConfig 默认值对照

| 参数 | 默认 | 说明 |
|------|------|------|
| `--language-model-only` | `False` | 等价将各模态 limit 设 0 |
| `--limit-mm-per-prompt` | `{}` | 默认每模态 999 |
| `--enable-mm-embeds` | `False` | 接受 `prompt_embeds`/`*_embeds`；与 0 限制联动 |
| `--media-io-kwargs` | `{}` | JSON |
| `--mm-processor-cache-gb` | `4` | 总占用 = cache_gb × (api_server_count + dp_size) |
| `--mm-processor-cache-type` | `lru` | `lru`/`shm` |
| `--mm-hasher-algorithm` | `blake3` | `blake3`/`sha256`/`sha512` |
| `--mm-shm-cache-max-object-size-mb` | `128` | 仅 shm 模式有效 |
| `--mm-encoder-only` | `False` | 解耦编码器进程 |
| `--mm-encoder-tp-mode` | `weights` | `data`/`weights` |
| `--mm-encoder-attn-dtype` | `None` | `fp8`/`None` |
| `--mm-encoder-fp8-scale-save-margin` | `1.5` | 自动保存时的安全系数 |
| `--interleave-mm-strings` | `False` | 需 `--chat-template-content-format=string` |
| `--skip-mm-profiling` | `False` | 跳过 MM 显存分析 |
| `--video-pruning-method` | `evs` | `evs`/`vidcom2` |
| `--mm-tensor-ipc` | `direct_rpc` | `direct_rpc`/`torch_shm` |
| `--mm-processor-device` | `auto` | `auto`/`cpu` |
| `--mm-ipc-gpu-memory-gb` | `0` | 0=关闭前端 GPU 多模态 gating |

**解读**：`--language-model-only` 是"零多模态"开关，等价把 limit 全置 0；`--enable-mm-embeds` 与"limit=0"组合可跳过 encoder 加载但仍接受嵌入输入，节省显存。`mm_processor_cache_gb` 在 DP 大时会被显著放大。

---

### E. ParallelConfig / All2All & DCP 默认值

| 参数 | 默认 | 说明 |
|------|------|------|
| `--distributed-executor-backend` | — | `external_launcher`/`mp`/`ray`/`uni` |
| `--pipeline-parallel-size, -pp` | `1` | — |
| `--master-addr` | `127.0.0.1` | — |
| `--master-port` | `29501` | — |
| `--nnodes, -n` | `1` | — |
| `--node-rank, -r` | `0` | — |
| `--tensor-parallel-size, -tp` | `1` | — |
| `--decode-context-parallel-size, -dcp` | `1` | 不扩 world size；无 PCP 时复用 TP |
| `--dcp-comm-backend` | `None` | 选 `"ag_rs"`/`"a2a"`/`None` |
| `--cp-kv-cache-interleave-size` | `1` | 替代旧 `--dcp-kv-cache-interleave-size` |
| `--prefill-context-parallel-size, -pcp` | `1` | 扩 world size，不增加 KV shard |
| `--data-parallel-size, -dp` | `1` | — |
| `--data-parallel-backend, -dpb` | `mp` | — |
| `--data-parallel-hybrid-lb, -dph` | `False` | — |
| `--data-parallel-external-lb, -dpe` | `False` | 仅 MoE |
| `--data-parallel-multi-port-external-lb, -dpm` | `False` | — |
| `--enable-expert-parallel, -ep` | `False` | MoE |
| `--enable-ep-weight-filter` | `False` | 仅 MoE，3D fused checkpoint 失效 |
| `--all2all-backend` | `allgather_reducescatter` | 12 取值 |
| `--enable-dbo` | `False` | — |
| `--ubatch-size` | `0` | — |
| `--enable-elastic-ep` | `False` | — |
| `--dbo-decode-token-threshold` | `32` | — |
| `--dbo-prefill-token-threshold` | `512` | — |
| `--enable-eplb` | `False` | EPLB 启用 |
| `--expert-placement-strategy` | `linear` | `linear`/`round_robin` |
| `--disable-custom-all-reduce` | `False` | 回退 NCCL |
| `--ray-workers-use-nsight` | `False` | Ray 性能分析 |
| `--enable-fault-tolerance` | `False` | — |

**解读**：TP=1+PP=1+DP=1 是单机单卡默认；All2All 默认 `allgather_reducescatter`，要换成 `deepep_*`/`flashinfer_*`/`mori_*`/`nixl_ep` 等需显式指定。`--data-parallel-external-lb` 默认 False，但当 `--data-parallel-rank` 显式给出时会被隐式设为 True。

---

### F. KernelConfig / CompilationConfig 默认值

| 参数 | 默认 | 取值 |
|------|------|------|
| `--moe-backend` | `auto` | 18 取值 |
| `--linear-backend` | `auto` | 21 取值 |
| `--enable-bf16x3
