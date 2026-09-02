# MiniMax-M3

> 仓 `vllm-ascend` · 路径 `docs/source/tutorials/models/MiniMax-M3.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm-ascend/docs/source/tutorials/models/MiniMax-M3.md

# MiniMax-M3 文档深度解读

## 【定位】
本文档是 vLLM-Ascend 项目中针对 **MiniMax-M3 多模态大模型** 在 Ascend NPU 上的部署与使用指南,涵盖从环境准备、镜像安装、单/多节点部署到功能验证与故障排查的完整流程,重点描述 BF16 与 W8A8 量化两种部署形态及对应硬件资源要求。

---

## 【技术要点】

1. **模型与硬件资源**:MiniMax-M3 BF16 模型需 **16 × 64 GB NPU**;W8A8 量化模型至少需要 **8 × 64 GB NPU**;支持 Atlas 800 A3 (64GB × 16)、Atlas 800 A2 (64GB × 8) 等平台。
2. **多模态与解析能力**:支持 **文本、图像、视频** 输入;支持 **thinking mode、reasoning parsing、tool-call parsing**。
3. **并行策略**:BF16 单节点使用 `--tensor-parallel-size 16` + `--enable-expert-parallel`;W8A8 单节点使用 TP=4 + DP=4;多节点 BF16 使用 TP=8 + DP=2(双节点)。
4. **关键环境变量**:`HCCL_OP_EXPANSION_MODE="AIV"`、`PYTORCH_NPU_ALLOC_CONF=expandable_segments:True`、`LD_PRELOAD` 指向 jemalloc、`HCCL_IF_IP`、`HCCL_SOCKET_IFNAME`、`GLOO_SOCKET_IFNAME`、`ASCEND_RT_VISIBLE_DEVICES`。
5. **Ascend 特有配置(通过 `--additional-config`)**:`enable_cpu_binding: true`、`ascend_compilation_config.enable_static_kernel: true`、`ascend_compilation_config.fuse_norm_quant: false`、`multistream_overlap_shared_expert: true`、`weight_nz_mode: 2`、`enable_flashcomm1: true`、`enable_reduce_sample: true`(W8A8 额外 `enable_shared_expert_dp: true`)。
6. **推理与投机解码**:`--reasoning-parser minimax_m3`;W8A8 启用 EAGLE3 投机解码,`num_speculative_tokens=3`,并配合 `--max-model-len 131072`、`--max-num-batched-tokens 32768`、`--long-prefill-token-threshold 4096`。
7. **容器与设备映射**:`--device /dev/davinci_manager`、`/dev/devmm_svm`、`/dev/hisi_hdc`,Atlas A3 使用 `/dev/davinci[0-15]`,Atlas A2 使用 `/dev/davinci[0-7]`;`--shm-size=100g`;使用 `--net=host` 简化端口转发(若使用桥接网络需预先开放多节点通信端口)。

---

## 【关键机制与数据】

- **编译与算子融合**:原文通过 `--compilation-config '{"cudagraph_mode":"FULL_DECODE_ONLY"}'` 限定 cudagraph 仅在 decode 阶段捕获;通过 `ascend_compilation_config.enable_static_kernel=true` 启用静态 kernel,减少动态调度开销。
- **量化与权重格式**:W8A8 模型权重以 `weight_nz_mode: 2` 的 Nz 格式存储;`enable_flashcomm1` 启用 FlashComm1 通信优化,降低集合通信延迟。
- **多模态输入限制**:通过 `--limit-mm-per-prompt '{"image":1,"video":0}'` 控制单请求中图像与视频数量;原文示例默认为 1 张图 0 视频,可按请求 shape 调整为 `{"image":2,"video":0}` 或 `{"image":0,"video":1}`;纯文本部署可省略该参数。
- **数据并行与本地并行**:多节点 BF16 中 `--data-parallel-size 2`、`--data-parallel-size-local 1`、`--data-parallel-start-rank 0`、`--data-parallel-address $node0_ip` 协同定义跨节点 DP 拓扑。
- **max-num-seqs 含义**:原文:"`max-num-seqs` is set to 16, which represents the maximum number of sequences the scheduler can process in a single iteration",即单次调度迭代可处理的最大序列数,需根据业务动态调整。
- **日志与输出重定向**:启动命令统一将 stdout/stderr 重定向至 `${LOG_PATH}`,便于多节点问题定位。
- **Rust 前端编译**:Step 3 中通过 `./build_rust.sh` 与 `pip install setuptools-rust` 安装 `_rust_tool_parser`,作为 Rust 前端依赖。

> 原文:未给出具体的吞吐量、首 token 延迟、tokens/s 等性能数字,亦未提供 Prefill/Decode 时延基准。

---

## 【表格解读】

原文无表格。

> 原文未提供任何参数表、性能对比表或配置项矩阵(如模型清单表)。所涉及的硬件/部署形式对比以行内文字描述呈现,详见"技术要点"第 1 条。

---

## 【公式解读】

原文无公式。

> 原文未给出任何 LaTeX 公式、伪代码公式或数学推导式。所有机制均以配置参数、命令行开关和文字说明形式给出。

---

## 【关联】

文档通过章节引用与文末内部链接,形成以下依赖关系:

| 引用文档 | 关联作用 |
| --- | --- |
| `../../user_guide/support_matrix/supported_models.md` | 第 2 节:查询 MiniMax-M3 在 vLLM-Ascend 中的模型支持矩阵(支持的功能与硬件组合)。 |
| `../../user_guide/feature_guide/index.md` | 第 2 节:查询各项功能(thinking mode、reasoning parsing、tool-call 等)的配置说明。 |
| `../../getting_started/installation.md#installation-multi-node-interconnect` | 第 3.2 节:多节点部署前的通信环境校验流程,对应本文多节点 BF16/W8A8 部署前置步骤。 |
| `../../getting_started/installation.md#installation-prebuilt-image` | 第 4.1 节:官方 all-in-one Docker 镜像的可用 tag 与发布版本说明。 |
| `../../user_guide/configuration/additional_config.md` | 第 5 节:`--additional-config` 中 Ascend 特有选项(如 `enable_static_kernel`、`enable_flashcomm1` 等)的官方解释。 |
| `../../user_guide/configuration/env_vars.md` | 第 5 节:`HCCL_OP_EXPANSION_MODE`、`PYTORCH_NPU_ALLOC_CONF` 等 Ascend 特有环境变量的官方说明。 |
| `../../developer_guide/evaluation/using_ais_bench.md` | (文末引入)使用 AIS Bench 进行功能/精度验证的指引。 |
| `../../developer_guide/performance_and_debug/optimization_and_tuning.md` | (文末引入)性能调优与问题排查的开发者指南。 |
| `../../user_guide/support_matrix/feature_matrix.md` | (文末引入)功能兼容性矩阵,用于交叉验证 MiniMax-M3 支持的特性。 |

**模块上下游关系**:
- 上游:模型权重来源于 ModelScope(`MiniMax-M3` 与 `Eco-Tech/MiniMax-M3-w8a8-0626`);容器基镜像为 `quay.io/ascend/vllm-ascend:{tag}`。
- 下游:推理服务由 `vllm serve` 启动,对外暴露端口 11223,通过 `--reasoning-parser minimax_m3` 接入推理后处理,通过 `--speculative-config`(W8A8)接入 EAGLE3 投机解码模型。
- 平行能力:BF16 与 W8A8 是同一模型的不同量化形态,共享同一套 reason parser 与 multimodal 限制,差异在于硬件门槛与是否启用 EAGLE3。

---

## 【使用方法】

### 一、Docker 镜像部署(原文 Step 1–4)

1. **拉取镜像**:`docker pull quay.io/ascend/vllm-ascend:{tag}`(`{tag}` 见 [installation-prebuilt-image](../../getting_started/installation.md#installation-prebuilt-image))。
2. **启动容器**:参考原文 `docker run --rm --name $NAME --net=host --shm-size=100g ...` 命令,Atlas A3 映射 `/dev/davinci[0-15]`,Atlas A2 映射 `/dev/davinci[0-7]`,并挂载 `/usr/local/dcmi`、`/usr/local/Ascend/driver/...`、`/root/.cache` 等目录。
3. **编译 Rust 前端**:`cd /vllm-workspace/vllm && pip install setuptools-rust && ./build_rust.sh`。
4. **安装校验**:`docker ps | grep vllm-ascend-env`(期望 `Up` 状态)、`pip show vllm-ascend`(期望版本与镜像 tag 一致)。

### 二、单节点在线服务部署(原文第 5.1 节)

- **BF16**:在 1 台 Atlas 800 A3 (64GB × 16) 上,T=16 + expert parallel,`--max-model-len 43008`、`--max-num-seqs 16`、`--gpu-memory-utilization 0.92`。
- **W8A8**:可在 1 台 Atlas 800 A3(64GB × 16)或 1 台 Atlas 800 A2 (64GB × 8) 上,TP=4 + DP=4 + `api_server_count=1`,`--max-model-len 131072`、`--max-num-batched-tokens 32768`、`--max-num-seqs 32`、启用 EAGLE3(`num_speculative_tokens=3`)。
- **多模态限制**:`--limit-mm-per-prompt '{"image":1,"video":0}'`(纯文本可省略;按请求 shape 调整)。
- **reasoning parser**:`--reasoning-parser minimax_m3`。
- **service 端口**:`--port 11223`。

### 三、多节点在线服务部署(原文第 5.2 节,原文末尾截断)

- 适用场景:**float(BF16)模型**在 Ascend A2 服务器上,至少需要 2 个节点;**A3 上不推荐不带 PD 分离的多节点部署**。
- **node 0(BF16,原文示例)**:TP=8 + DP=2、`--data-parallel-size-local 1`、`--data-parallel-start-rank 0`、`--data-parallel-address $node0_ip`、`--max-model-len 40960`、`--max-num-seqs 8`、`--gpu-memory-utilization 0.94`;需设置 `HCCL_IF_IP`、`IFNAME`、`HCCL_SOCKET_IFNAME`、`GLOO_SOCKET_IFNAME`、`ASCEND_RT_VISIBLE_DEVICES=0,1,2,3,4,5,6,7`。
- **占位变量**(须按实际环境替换):`WEIGHT_PATH`、`EAGLE3_WEIGHT_PATH`、`LOG_PATH`、`local_ip`、`node0_ip`、`IFNAME`。
- **node 1 / W8A8 多节点命令**:原文在交付范围内被截断,未给出完整命令(原文未涉及该部分)。

### 四、功能验证、精度评估、故障排查(原文涉及,细节在关联文档)

- 功能/精度验证:见 [using_ais_bench](../../developer_guide/evaluation/using_ais_bench.md)。
- 性能调优与故障排查:见 [optimization_and_tuning](../../developer_guide/performance_and_debug/optimization_and_tuning.md)。
- 特性兼容性交叉确认:见 [feature_matrix](../../user_guide/support_matrix/feature_matrix.md)。
