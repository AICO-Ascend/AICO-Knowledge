# Disaggregated Encoder

> 仓 `vllm` · 路径 `docs/features/disagg_encoder.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm/docs/features/disagg_encoder.md

# vLLM 分离式编码器 (Disaggregated Encoder) 深度解读

## 【定位】
这篇文档描述了 vLLm 在多模态大模型推理中,把**视觉编码器 (vision encoder) 阶段**与**语言模型预填/解码 (prefill/decode) 阶段**拆开到独立进程中运行的能力,以此实现独立伸缩、降低首 token 时延 (TTFT) 以及跨进程的编码结果复用与缓存。

## 【技术要点】
- **三阶段分离架构**:Encoder (E) + Prefill/Decode (PD, 可进一步拆为 P→D) 三类实例通过 connector 解耦,而不是塞进同一 vLLM 进程。
- **参考实现 (Reference Connector)**:当前文档给出的参考路径是 **ExampleConnector**,对应两个开箱即用脚本 `disagg_1e1pd_example.sh` (1E+1PD) 与 `disagg_1e1p1d_example.sh` (1E+1P+1D)。
- **PD 内部两种形态**:
  - 单实例:`disagg_encoder_example.sh` (E→PD)
  - 进一步分离:`disagg_epd_example.sh` (E→P→D),其中 Prefill 执行 1 步 (prefill → 1 token output) 后,再把 KV cache 转给 Decode 实例继续执行。
- **EC (Encoder-Cache) Connector 抽象**:接口 `ECConnector`,在调用方扮演两种角色 —— **Scheduler 角色** (检查 cache 是否存在并调度 load)、**Worker 角色** (把 embedding 真正加载进显存)。所有相关代码位于 `vllm/distributed/ec_transfer`。
- **KV 传输复用现有组件**:P↔D 之间沿用 **NixlConnector** (`vllm/distributed/kv_transfer/kv_connector/v1/nixl/`),并参考 `tests/v1/kv_connector/nixl_integration/toy_proxy_server.py` 来转发 KV。
- **测试入口**:测试代码位于 `tests/v1/ec_connector`。

## 【关键机制与数据】

**工作原理 (原文:)** 文档把机制拆成"两段":Encoder 实例负责纯视觉编码;PD 实例负责语言预填/解码。EC embeddings 通过 connector 从 Encoder 端传到 PD 端;P↔D 之间再走 KV cache 传输(KV 传输严格发生在 PD 实例执行完毕之后)。Prefill 实例接收 cache 的方式与上面 disaggregated encoder 流程完全一致 —— 也就是说 EC 缓存传输和 KV 缓存传输是**两层独立的传输链路**,但都遵循"上游产出 → 序列化传输 → 下游消费"的同构模式。

**三条动机(原文:)**
1. **独立细粒度伸缩** — 视觉编码器轻量,而语言模型"orders of magnitude larger",因此语言模型的并行化不会影响 encoder 集群,encoder 节点可以独立加减。
2. **降低 TTFT** — 纯文本请求完全绕过视觉编码器;encoder 输出只在需要的 attention 层注入,缩短 prefill 的关键路径。
3. **跨进程复用与缓存** — 进程内编码器只能在单个 worker 内复用;远程共享 cache 让任意 worker 都能取到已有 embedding,消除重复计算。

文档中**没有任何数值化的性能数据**(如延迟对比、吞吐增益百分比等),仅有定性描述。

## 【表格解读】
原文无表格。

## 【公式解读】
原文无公式。

## 【关联】
- **内部模块/目录关联**(根据原文出现的路径):
  - `vllm/distributed/ec_transfer` —— EC 传输实现所在地。
  - `vllm/distributed/kv_transfer/kv_connector/v1/nixl/` —— P↔D 之间 KV 传输所用的 **NixlConnector**,说明 disagg encoder 与传统 disagg prefill 在 KV 通道上共用底层组件。
  - `tests/v1/ec_connector` —— 自身测试目录。
  - `tests/v1/kv_connector/nixl_integration/toy_proxy_server.py` —— 被借鉴用来"facilitate the kv transfer between P and D"的代理服务样例。
- **同仓关联文档**:`docs/features/disagg_prefill.md` —— 原文明确写"shows the brief idea about the disaggregated prefill (v0)",即本特性与 PD 解耦/分离式 prefill 在架构上是同构的(Encoder↔PD 对应 Prefill↔Decode),可视为同一思路在视觉端和语言端的两面。
- **设计文档**:`https://docs.google.com/document/d/1aed8KtC6XkXtdoV87pWT0a8OJlZ-CpnuLLzmR8l9BAE` —— Google Docs 上的设计稿,提供更深入的设计动机与权衡说明。
- **示例脚本**:`examples/disaggregated/disagg_encoder/disagg_1e1pd_example.sh`、`examples/disaggregated/disagg_encoder/disagg_1e1p1d_example.sh`、`disagg_encoder_example.sh` (E→PD 单实例版)、`disagg_epd_example.sh` (E→P→D 解耦版) —— 构成由浅入深的部署示例矩阵。

## 【使用方法】
根据原文可直接抄录的启用方式:
- **当前参考 connector**:`ExampleConnector`(原文明示 "The current reference pathway is ExampleConnector")。
- **示例脚本(原文路径,直接运行即可)**:
  - `examples/disaggregated/disagg_encoder/disagg_1e1pd_example.sh` —— 1 个 Encoder 实例 + 1 个 PD 实例。
  - `examples/disaggregated/disagg_encoder/disagg_1e1p1d_example.sh` —— 1 个 Encoder + 1 个 Prefill + 1 个 Decode。
  - `disagg_encoder_example.sh` —— PD 走单实例(E→PD)。
  - `disagg_epd_example.sh` —— PD 进一步拆为 P 与 D(E→P→D)。
- **底层传输组件**:`NixlConnector`(位于 `vllm/distributed/kv_transfer/kv_connector/v1/nixl/`),P↔D 间的 KV 传输沿用之。
- **验证方式**:跑 `tests/v1/ec_connector` 下的测试脚本。

原文未涉及具体的配置项、命令行 flag、环境变量、端口或参数取值。

## 图文联合解读

- `disagg_encoder_flow.png`: **图文联合解读：**

1）**图示内容**：序列图呈现请求从 Proxy 同时分发至 Encoder 与 PD 两个独立 vLLM 实例。Encoder 侧 Scheduler→EncoderInstance（execute）→ECConnector→RemoteStorage（store cache）写入编码缓存；PD 侧 ECConnector 从 RemoteStorage 拉取缓存（receive cache）并交 PDInstance 执行。虚线标注「(Option) P2P send cache」表示两 ECConnector 间可选直连，绕过 RemoteStorage。

2）**技术结论**：ECConnector 作为解耦层，使编码计算与缓存传输解耦；RemoteStorage 实现跨进程共享，P2P 旁路提供低延迟快捷通道。

3）**与文档关系**：直观印证 §1.3「Cross-process reuse and caching」论点——Encoder 与 PD 解耦部署，通过 ECConnector+RemoteStorage 实现缓存复用，消除冗余编码计算。
