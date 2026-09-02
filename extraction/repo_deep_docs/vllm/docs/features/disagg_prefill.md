# Disaggregated Prefilling (experimental)

> 仓 `vllm` · 路径 `docs/features/disagg_prefill.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm/docs/features/disagg_prefill.md

# Disaggregated Prefilling 文档深度解读

## 【定位】

本文档介绍 vLLM 的**分离式 Prefill（Disaggregated Prefilling）**特性——将 LLM 推理的 prefill 阶段与 decode 阶段拆分到两套独立的 vLLM 实例中运行,通过 KV 缓存传输连接器（Connector）在二者之间传递 KV cache,从而实现 TTFT（首 token 延迟）与 ITL（token 间延迟）的独立调优以及对尾部 ITL 的精准控制。

---

## 【技术要点】

1. **架构本质**: 运行 2 个 vLLM 实例——prefill 实例与 decode 实例,通过 connector 传递 KV caches 和结果。代码实现位于 `vllm/distributed/kv_transfer`。
2. **核心目的（两条）**:
   - **独立调优 TTFT 与 ITL**: 可分别为 prefill 与 decode 阶段指派不同的并行策略（`tp`、`pp` 等）,互不影响。
   - **控制尾部 ITL**: 避免 decode 过程中插入 prefill 任务造成的高尾延迟;相比 chunked prefill,无需反复调试 chunk size。
3. **明确边界**: 文档显式声明「Disaggregated prefill DOES NOT improve throughput」——该特性只优化延迟形态,不解吞吐瓶颈。
4. **9 类 Connector**（原文如此表述）: ExampleConnector、LMCacheConnectorV1（含 `LMCacheMPConnector` 多进程模式）、NixlConnector、MooncakeConnector、MoRIIOConnector（仅 ROCm）、MultiConnector、OffloadingConnector、FlexKVConnectorV1。
5. **三大抽象**: `Connector`（kv producer/consumer 之间的 KV cache 检索/传输）、`LookupBuffer`（提供 `insert` 与 `drop_select` 两种语义类似 SQL 的 API）、`Pipe`（单方向 FIFO 张量传输通道,支持 `send_tensor` / `recv_tensor`）。其中 `insert` 非阻塞,`drop_select` 阻塞。
6. **进程级 Connector 划分**: Scheduler connector（与 scheduler 同进程,负责调度 KV 传输操作）与 Worker connectors（位于 worker 进程,执行实际的 KV 传输）。
7. **Token IDs 复用优化（实验性）**: 在 `/v1/chat/completions` 端点上,通过 `kv_transfer_params["prompt_token_ids"]` 把 prefill 阶段产出的 token ids 直接传给 decode 阶段,跳过 decode 端的模板渲染与 tokenize。

---

## 【关键机制与数据】

**工作原理**:

- **数据流**: 用户请求进入 prefill 实例 → prefill 实例产出 KV caches → 通过 Connector 传输至 decode 实例 → decode 实例在已就绪的 KV cache 上做逐 token 生成。
- **端到端双实例编排**: 每个进程都会持有一个对应的 connector,Scheduler connector 调度传输,Worker connector 执行传输;Worker connector 与 attention 模块配合,**逐层（layer-by-layer）** 存储/加载 KV cache。
- **NIXL 后端可多选**: 通过 `kv_connector_extra_config.backends` 数组,可在 `UCX`、`GDS` 等 NIXL transfer backend 中选择一个或多个。
- **LMCacheMP 多进程模式**: 一台独立的 `lmcache server` 持有 KV cache,由一个或多个 vLLM 实例共享。
- **Token ID 复用流程**（原文示例代码）:
  1. prefill 请求开启 `return_token_ids=True` 与 `kv_transfer_params={"do_remote_decode": True}`;
  2. 从 prefill 响应中读取 `prompt_token_ids`;
  3. decode 请求附带 `kv_transfer_params={"do_remote_prefill": True, "prompt_token_ids": ids}`;`messages` 仍需提供但其内容不再被 tokenize。
- **输出行为**: token id 复用后,detokenize、tool/reasoning 解析、流式输出、结构化输出约束仍然按常规 chat completion 行为生效。

**性能数据**: 原文未给出任何性能基准数字（无 TTFT/ITL 量化数据、无吞吐对比表）。

---

## 【表格解读】

**原文无表格**。但为方便读者,这里把文档中各 Connector 的关键配置参数以表格形式整理（参数取自原文示例命令,非原文表格）:

| Connector | 关键配置（原文示例） | 后端 / 模式 |
|---|---|---|
| ExampleConnector | 见 `examples/disaggregated/example_connector/run.sh` | 示例用 |
| LMCacheConnectorV1 | 见 `disagg_prefill_lmcache_v1/disagg_example_nixl.sh`,底层走 NIXL;另有 `LMCacheMPConnector` 多进程模式,通过独立 `lmcache server` 共享 KV | NIXL / MP |
| NixlConnector | `kv_connector=NixlConnector`,`kv_role=kv_both`,`kv_buffer_device=cuda`,`kv_connector_extra_config.backends=[UCX, GDS]`;支持 fully async send/recv | NIXL (UCX/GDS 等) |
| MooncakeConnector | 见 `run_mooncake_connector.sh` | Mooncake |
| MoRIIOConnector | 见 `moriio_connector_usage.md` | ROCm 专用 |
| MultiConnector | `kv_connector=MultiConnector`,`kv_connector_extra_config.connectors=[{...},{...}]`,按顺序串联多个 connector | 多 connector 串联 |
| OffloadingConnector | `kv_connector=OffloadingConnector`,`kv_role=kv_both`,`kv_connector_extra_config={"block_size":64, "cpu_bytes_to_use":1000000000}`;支持 CPU + filesystem 多层 | CPU / 多层 offload |
| FlexKVConnectorV1 | `kv_connector=FlexKVConnectorV1`,`kv_role=kv_both`;分布式 KV Store + 多级缓存 | FlexKV |

---

## 【公式解读】

**原文无公式**。文档不含 LaTeX 或伪代码形式的数学/逻辑公式。涉及 KV 缓存传输的语义描述以三个抽象的 API 命名（`insert` / `drop_select` / `send_tensor` / `recv_tensor`）表达,未给出符号化的数学表达。

---

## 【关联】

文档处于 vLLM features 文档树下,与以下外部/内部资源形成上下游关系（均来自文末及正文内部链接）:

- **示例脚本（运行环境）**:
  - `examples/disaggregated/example_connector/run.sh` —— ExampleConnector 入口示例
  - `examples/disaggregated/lmcache/disagg_prefill_lmcache_v1/disagg_example_nixl.sh` —— LMCacheConnectorV1 + NIXL 入口示例
  - `examples/disaggregated/mooncake_connector/run_mooncake_connector.sh` —— MooncakeConnector 入口示例
  - `examples/disaggregated/flexkv_connector/prefix_caching_flexkv.py` —— FlexKVConnectorV1 入口示例
- **配套使用指南**（同文档树下的特性页）:
  - `nixl_connector_usage.md` —— NixlConnector 详细使用指南
  - `nixl_connector_compatibility.md` —— NixlConnector 功能兼容矩阵
  - `mooncake_connector_usage.md` —— MooncakeConnector 使用指南
  - `moriio_connector_usage.md` —— MoRIIOConnector 使用指南（ROCm）
  - `kv_offloading_usage.md` —— KV offloading 多层（CPU + filesystem 等）配置参考
- **测试入口**:
  - `tests/v1/kv_connector/nixl_integration/run_accuracy_test.sh` —— NixlConnector 准确率/集成测试脚本
- **第三方 LMCache 文档**:
  - `examples/disaggregated/lmcache/README.md` —— LMCache 示例索引
  - 外链 `https://docs.lmcache.ai` —— LMCache 官方文档
- **代码实现位置**: `vllm/distributed/kv_transfer`（Scheduler connector、Worker connector、LookupBuffer、Pipe 等抽象的真实实现）。
- **上下游依赖**: 上游为请求入口 `/v1/chat/completions`（token id 复用特性的承载端点）;下游为 vLLM attention 模块（与 Worker connector 协作做逐层 KV cache store/load）。

---

## 【使用方法】

**1. 通用启用形式**: 通过 `--kv-transfer-config` JSON 字符串启用,并选取对应 `kv_connector` 名称,典型 `kv_role=kv_both`。原文给出了以下具体命令模板:

```bash
# NixlConnector: 启用 UCX 与 GDS 两个 NIXL backend
--kv-transfer-config '{"kv_connector":"NixlConnector","kv_role":"kv_both",
  "kv_buffer_device":"cuda",
  "kv_connector_extra_config":{"backends":["UCX", "GDS"]}}'

# MultiConnector: 把多个 connector 串成一个有序列表
--kv-transfer-config '{"kv_connector":"MultiConnector","kv_role":"kv_both",
  "kv_connector_extra_config":{"connectors":[
    {"kv_connector":"NixlConnector","kv_role":"kv_both"},
    {"kv_connector":"ExampleConnector","kv_role":"kv_both",
     "kv_connector_extra_config":{"shared_storage_path":"local_storage"}}]}}'

# OffloadingConnector: KV offload 到 CPU,block_size=64 tokens,占用 ~1GB
--kv-transfer-config '{"kv_connector":"OffloadingConnector","kv_role":"kv_both",
  "kv_connector_extra_config":{"block_size":64, "cpu_bytes_to_use":1000000000}}'

# FlexKVConnectorV1
--kv-transfer-config '{"kv_connector":"FlexKVConnectorV1","kv_role":"kv_both"}'
```

**2. Token id 复用（实验性）**: 在 `/v1/chat/completions` 客户端侧通过 `extra_body` 开启,完整 Python 范式见【关键机制与数据】节。

**3. 注意事项**: 文档顶部明确标注该特性为 **experimental,subject to change**;Token id 复用段落同样标注 experimental,且目前仅适用于 chat completions 端点。文档对启动 prefill/decode 实例所需的最小 GPU 数、端口协调、共享存储路径等具体部署细节**未涉及**（仅以示例脚本代替说明）。

## 图文联合解读

- `abstraction.jpg`: **图示内容**：Connector 容器内，左右两侧分别为 KV producer 与 KV consumer，中部通过 pipe 双向连接；producer 经 "insert kv cache (non-blocking)" 写入 Lookup Buffer+Request handler，consumer 经 "drop_select kv cache (blocking)" 读取对应组件。

**技术结论**：KV 缓存在 prefill 与 decode 实例间通过 pipe 异步传输，写入非阻塞、读取阻塞，实现两阶段解耦通信。

**与文档关系**：直观支撑"prefill/decode 分置于不同 vLLM 实例"的核心论点，解释其独立调优 TTFT 与 ITL、控制尾延迟的工程机制。
- `overview.jpg`: **图文联合解读：**

图示三泳道（Proxy / vLLM prefill / vLLM decode）数据流：请求经代理转发至 prefill 实例，先设 `max_tokens=1` 完成 Prefill 生成首个 token 并将 KV 缓存入 buffer；KV transfer thread 将缓存跨实例传输至 decode 实例，后者通过 `drop_select` 跳过 prefill 直接复用 KV 解码输出后续 token。论证了 prefill 与 decode 阶段解耦可独立调优 TTFT 与 ITL，并消除 decode 中插入 prefill 带来的尾延迟——印证文档"分离两阶段、控制尾 ITL"的核心论点。
- `high_level_design.png`: **图文联合解读：**

图示左侧详细描绘单个vLLM实例：调度进程（含调度器连接器）通过新增`connector_metadata`字段的SchedulerOutput，将任务分发至含Worker连接器与Paged KV buffer的工作进程；右侧为其他vLLM实例，对称结构；所有实例经底部"Data transfer layer"通信。

技术结论：跨实例KV cache传输由"调度器+Worker双层Connector"协同完成，调度输出新增元数据字段是关键握手机制。

与文档论点对应：直观印证"prefill与decode分离到不同vLLM实例"的设计，通过连接器层实现灵活并行策略与尾延迟控制。
- `workflow.png`: **1) 图中内容**：UML时序图，含 ModelRunner、Attention、Connector 三条泳道。Decode 节点先 `start_load_kv()`，每步 `wait_for_kv_layer()` 再 `forward()`；Prefill 节点每层 `save_kv_layer()`，最后 `wait_for_save()` 结束 `set_forward_context()`。

**2) 技术结论**：Prefill 与 Decode 通过 Connector 异步传输 KV 缓存，实现两阶段在独立 vLLM 实例上的解耦执行。

**3) 与文档关系**：以调用时序佐证 "prefill 与 decode 分置不同实例" 的核心设计，证明 Connector 是跨实例共享 KV、从而独立调优 TTFT 与 ITL 的关键机制。
