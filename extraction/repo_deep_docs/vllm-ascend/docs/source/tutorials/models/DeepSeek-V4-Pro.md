# DeepSeek-V4-Pro

> 仓 `vllm-ascend` · 路径 `docs/source/tutorials/models/DeepSeek-V4-Pro.md` · 类型 guide · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/vllm-ascend/docs/source/tutorials/models/DeepSeek-V4-Pro.md

# DeepSeek-V4-Pro 部署文档深度解读

## 【定位】
本篇文档描述 vllm-ascend 上 DeepSeek-V4-Pro (量化版 `DeepSeek-V4-Pro-w4a8-mtp`) 的多节点在线推理部署全流程,涵盖镜像选择、环境准备、HCCL 多节点互联、`vllm serve` 启动参数与投机解码/MoE 专家并行/Ascend 量化等关键开关。

## 【技术要点】

1. **硬件拓扑要求**:`DeepSeek-V4-Pro-w4a8-mtp` 量化版需要至少 **2 个 Atlas 800 A3 (128GB × 8)** 节点,或 **4 个 Atlas 800 A2 (64GB × 8)** 节点。

2. **镜像选择**(对应 series):
   - A3 系列:`quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}-a3`
   - A2 系列:`quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}`

3. **多节点并行策略**(A2 系列 Node0):`--data-parallel-size 4` 配合 `--tensor-parallel-size 8`,即 4 节点 × 每节点 8 卡 TP,跨节点开启 DP;同节点内 `--data-parallel-size-local 1`、`--enable-expert-parallel`、`--quantization ascend`、`--speculative-config { "method": "mtp", "num_speculative_tokens": 1, "enforce_eager": true }`、`--tokenizer-mode deepseek_v4`、`--tool-call-parser deepseek_v4`、`--reasoning-parser deepseek_v4`。

4. **上下文与服务上限**:`--max-model-len 135000`、`--max-num-batched-tokens 4096`、`--max-num-seqs 16`、`--gpu-memory-utilization 0.9`、`--block-size 128`、`--served-model-name dsv4`、服务端口 `10010`、`--no-enable-prefix-caching` (显式关闭)、权重加载策略 `'prefetch'`,并通过 `--model-loader-extra-config '{"enable_multithread_load":"true","num_threads":128}'` 多线程加载。

5. **HCCL 集合通信关键环境变量**(A2 系列每个节点):`HCCL_IF_IP`/`IFNAME` 锁定本节点网卡;`HCCL_BUFFSIZE=512`;`HCCL_SOCKET_IFNAME` 与 `TP_SOCKET_IFNAME`、`GLOO_SOCKET_IFNAME` 共用同一 `IFNAME`;`HCCL_OP_EXPANSION_MODE="AIV"`;`HCCL_CONNECT_TIMEOUT=7200`;`ASCEND_CONNECT_TIMEOUT=10000`;`ASCEND_TRANSFER_TIMEOUT=10000`;`VLLM_RPC_TIMEOUT=1800000`;`ASCEND_RT_VISIBLE_DEVICES=0,1,2,3,4,5,6,7`(本节点 8 卡全开);`VLLM_ENGINE_READY_TIMEOUT_S=3600`;`ACL_OP_INIT_MODE=1`;`TASK_QUEUE_ENABLE=1`;`OMP_PROC_BIND=false`、`OMP_NUM_THREADS=10`;`PYTORCH_NPU_ALLOC_CONF=expandable_segments:True`;`LD_PRELOAD=/usr/lib/aarch64-linux-gnu/libjemalloc.so.2:$LD_PRELOAD`。

6. **Ascend compilation / 共享专家重叠配置**(通过 `--additional-config` 与 `--compilation-config` 注入):
   - `"ascend_compilation_config": { "enable_npugraph_ex": true, "enable_static_kernel": false }`
   - `"enable_cpu_binding": true`
   - `"enable_shared_expert_dp": true`
   - `"multistream_overlap_shared_expert": true`
   - `cudagraph_mode = "FULL_DECODE_ONLY"`

## 【关键机制与数据】

- **模型架构背景**(原文 Section 1):DeepSeek-V4 在 V3 之上引入 **(1)** Manifold-Constrained Hyper-Connections (**mHC**) 用于加强传统残差连接;**(2)** 混合注意力 (hybrid attention),通过 **Compress-4-Attention** 与 **Compress-128-Attention** 提升长上下文效率;MoE 部分仍采用 DeepSeekMoE 架构,仅有 minor adjustments。"DeepSeek-V4-Pro" 是 DeepSeek-V4 的 maximum reasoning effort 模式,声称在 coding benchmarks 上 top-tier,在 reasoning 与 agentic tasks 上显著缩小与领先闭源模型的差距(原文表述)。

- **量化路径**(原文 Section 3.1):模型权重本身为 `w4a8` 量化 (权重 4-bit、激活 8-bit),与 `--quantization ascend` 共同构成部署侧的量化链路;`--tokenizer-mode deepseek_v4` / `--tool-call-parser deepseek_v4` / `--reasoning-parser deepseek_v4` 是 DeepSeek-V4 系列专用的 tokenizer 与 tool/reasoning 解析器。

- **投机解码**(原文 Node0 `vllm serve` 命令):`--speculative-config` 选用 MTP (Multi-Token Prediction) 方法,每次生成 `num_speculative_tokens = 1`,并强制 `enforce_eager = true`,说明在该路径下投机模块走 eager 模式。

- **多线程加载**(原文):`--model-loader-extra-config {"enable_multithread_load": "true", "num_threads": 128}`,以 128 线程并发读盘,服务于大模型冷启动加速。

- **性能数据**:原文未提供吞吐量、latency、token/s 等具体数值,仅给出硬件规模与并行策略。**原文未涉及可量化的性能/准确率数字**。

## 【表格解读】
原文无表格 (仅有 Docker 启动命令、`vllm serve` 命令等代码块,不具备"逐字还原表格"的形式)。

## 【公式解读】
原文无公式。

## 【关联】

- **Supported Features List** (`../../user_guide/support_matrix/supported_models.md`):Section 2 将 DeepSeek-V4-Pro 的支持矩阵 (feature matrix) 委托给此页,本文档未在正文中枚举具体 feature 是否启用,需跳转对照。
- **Feature Guide** (`../../user_guide/feature_guide/index.md`):Section 2 同样将 "各 feature 如何配置" 委托到此处,例如 MTP、专家并行、Ascend 量化等开关的语义细节应在该索引页查找。
- **Verify multi-node communication environment** (`../../getting_started/installation.md#installation-multi-node-interconnect`):在 Section 3.2 中作为多节点部署的前置可选步骤被引用,与本教程中 `HCCL_IF_IP` / `IFNAME` / `HCCL_CONNECT_TIMEOUT` 等集合通信环境变量相互呼应。
- **Using docker / prebuilt image** (`../../getting_started/installation.md#installation-prebuilt-image`):Section 4.1 中根据 A3/A2 series 选择对应镜像即来自该节。
- **Installation** (`../../getting_started/installation.md`):Section 4.2 提供源码安装替代路径 (不依赖 Docker)。
- **FAQs** (`../../faqs.md`):由内部链接清单给出,文档正文中未直接展示,作为通用问题排查入口与本文档的部署步骤互补。
- **PD Disaggregation with Mooncake (multi-node)** (`../features/pd_disaggregation_mooncake_multi_node.md`):由内部链接清单给出。在已展示的 `vllm serve` 命令中未显式启用 PD 分离,二者作为"标准在线推理"与"Prefill/Decode 解耦的 MoonCake 部署"两条路径的对照参考;若在多节点场景进一步做 P/D 拆分,可迁移本文档中的 HCCL / DP-TP / expert-parallel 配置。

## 【使用方法】

- **下载权重**(原文 Section 3.1):`DeepSeek-V4-Pro-w4a8-mtp` 来源于 ModelScope,推荐下载到共享目录 `/root/.cache/`(本教程假设路径 `/root/.cache/modelscope/hub/models/vllm-ascend/`)。

- **Docker 启动 A3 系列**:在每个节点上导出 `IMAGE=quay.io/ascend/vllm-ascend:{{ vllm_ascend_version }}-a3`,以 `--shm-size=512g`、`--net=host`、`--privileged=true` 并透传 16 个 `/dev/davinci*` 设备 + `/dev/davinci_manager`、`/dev/devmm_svm`、`/dev/hisi_hdc`;挂载 `/usr/local/dcmi`、`hccn_tool`、`npu-smi`、Ascend driver `lib64/` 与 `version.info`、`/etc/ascend_install.info`、`/etc/hccn.conf`、`/root/.cache`,最后以 `-it $IMAGE bash` 进入容器。

- **Docker 启动 A2 系列**:同 A3,但镜像去掉 `-a3` 后缀,且只透传 8 个 `/dev/davinci0..7` (原文措辞:Node0 与 Node1-Node3 中 `ASCEND_RT_VISIBLE_DEVICES=0,1,2,3,4,5,6,7`),其余挂载相同。

- **验证容器**:原文推荐 `docker ps`。

- **多节点推理 (A2)**:在 Node0 与 Node1-Node3 上分别执行 `vllm serve /root/.cache/modelscope/hub/models/vllm-ascend/DeepSeek-V4-Pro-w4a8-mtp` 同一条命令,差异仅在 `local_ip` / `node0_ip` 与 `--data-parallel-start-rank`(Node0 为 0,其它节点需替换为相应 rank,原文 Node1-Node3 段在所提供内容尾部截断,未完整体给出)。共同参数:`--host 0.0.0.0 --port 10010 --max-model-len 135000 --max-num-batched-tokens 4096 --served-model-name dsv4 --gpu-memory-utilization 0.9 --max-num-seqs 16 --data-parallel-size 4 --tensor-parallel-size 8 --data-parallel-size-local 1 --data-parallel-start-rank <rank> --data-parallel-address $node0_ip --enable-expert-parallel --quantization ascend --no-enable-prefix-caching --tokenizer-mode deepseek_v4 --tool-call-parser deepseek_v4 --enable-auto-tool-choice --reasoning-parser deepseek_v4 --safetensors-load-strategy 'prefetch' --block-size 128`,并通过 `--speculative-config`、`--additional-config`、`--compilation-config`、`--model-loader-extra-config` 分别注入 MTP、Ascend 编译/共享专家重叠、`FULL_DECODE_ONLY` cudagraph、128 线程多线程加载四组配置。

- **源码安装**(原文 Section 4.2):不依赖 Docker 时,按 `../../getting_started/installation.md` 从源码安装 `vllm-ascend`,多节点场景需在每个节点上重复该步骤。

- **下游验证**:原文 Section 1 提到还会展示 "accuracy and performance evaluation",但所提供内容中**原文未涉及**具体的精度/性能评估命令,需要由其它章节(或链接到的特性页)给出。
