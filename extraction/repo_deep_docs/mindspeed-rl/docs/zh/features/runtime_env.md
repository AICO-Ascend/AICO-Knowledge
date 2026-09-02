# runtime_env 环境变量

> 仓 `mindspeed-rl` · 路径 `docs/zh/features/runtime_env.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-rl/docs/zh/features/runtime_env.md

# 「runtime_env 环境变量」文档一体化深度解读

## 【定位】

本文档系统梳理了 mindspeed-rl（昇腾强化学习加速库）在 `configs/envs/runtime_env.yaml` 中预设的运行时环境变量清单，覆盖 Ray 调度、NCCL/HCCL/LCCL/GLOO 集合通信、vLLM 推理引擎、NPU 内存分配、CPU 绑核、TOPK 优化、CoC 通信特性等关键开关，为用户在昇腾 NPU 集群上部署强化学习训练/推理提供"一份可抄的环境变量速查表"。

---

## 【技术要点】

1. **环境变量统一托管**：所有运行时开关集中定义在 `configs/envs/runtime_env.yaml`，通过环境变量形式下发，避免在代码中硬编码，便于在不同集群/拓扑之间灵活切换。
2. **多框架通信后端并存**：文档同时涉及 Ray（资源调度层）、NCCL/HCCL（昇腾集合通信）、LCCL（低延迟通信）、GLOO（CPU 侧通信）、TP_SOCKET_IFNAME（张量并行通信），覆盖 RL 训练"调度→集合通信→点对点通信→CPU 协同"完整链路。
3. **vLLM 推理引擎强耦合配置**：要求 `VLLM_USE_V1=1`（当前仅支持 v1 接口）；`VLLM_DP_SIZE` 在稠密模型下必须置 1，MOE 模型下必须与 EP（专家并行）一致；并通过 `VLLM_ENABLE_TOPK_OPTIMZE` 与 `VLLM_ASCEND_ACL_OP_INIT_MODE` 控制 vLLM 性能/初始化路径。
4. **性能优化三件套**：`TASK_QUEUE_ENABLE=2`（开启 Level 2 算子下发队列优化）、`CPU_AFFINITY_CONF=1`（开启绑核优化）、`VLLM_ENABLE_TOPK_OPTIMZE=true`（TOPK 性能优化），三者共同降低 RL rollout/inference 阶段的调度抖动与算子开销。
5. **故障诊断与超时保护**：`NCCL_DEBUG`（VERSION/WARN/INFO/TRACE 四级）、`HCCL_CONNECT_TIMEOUT`（连接超时）、`HCCL_EXEC_TIMEOUT`（执行超时）、`HYDRA_FULL_ERROR`（Hydra 完整错误日志），构成"通信失败—定位—修复"诊断闭环。
6. **CoC 与网卡隔离**：启用 CoC 特性时需配套 `LCAL_COMM_ID=127.0.0.1:27001`；通过 `HCCL_SOCKET_IFNAME / GLOO_SOCKET_IFNAME / TP_SOCKET_IFNAME` 分别指定 HCCL、GLOO、TP 三类流量的物理网卡，避免 RDMA 拥塞。

---

## 【关键机制与数据】

- **数据流（原文描述）**：用户编辑 `configs/envs/runtime_env.yaml` → 框架启动时将其解析为进程级环境变量 → 注入到 Ray worker / vLLM 推理进程 / 训练主进程 → 各依赖库（Ray、vLLM、HCCL、LCCL、GLOO、tokenizers、torch_npu）按变量名自行生效。
- **性能/约束类硬指标（原文直接给出）**：
  - `VLLM_DP_SIZE`：稠密模型 = **1**；MOE 模型 = **EP**。
  - `VLLM_USE_V1`：**当前只支持 v1**，需设为 `'1'`。
  - `TASK_QUEUE_ENABLE`：推荐设为 `'2'`（Level 2 优化）。
  - `CPU_AFFINITY_CONF`：推荐设为 `'1'`。
  - `LCAL_COMM_ID`：开启 CoC 特性时设为 `'127.0.0.1:27001'`。
  - `RAY_EXPERIMENTAL_NOSET_ASCEND_RT_VISIBLE_DEVICES`：`'true'` 表示**禁用** Ray 自动设置。
  - `USING_LCCL_COM`：用于指定**不使用** LCCL 通信。
- **缓冲区数据（原文）**：`HCCL_BUFFSIZE` 单位为 **MB**，决定 HCCL 通信层单次传输的最大缓冲区，直接影响跨设备通信效率。
- **NCCL Debug 级别枚举（原文）**：`VERSION`、`WARN`、`INFO`、`TRACE` 四级。
- **NCCL 模拟项（原文）**：`CUDA_DEVICE_MAX_CONNECTIONS` 复用自 CUDA 生态，用于限制单设备最大并发连接数，规避多 stream 竞争。
- 原文未提供任何 benchmark、吞吐量、延迟数字，亦无运行时序图。

---

## 【表格解读】

原文仅一张参数速查表，**逐字还原**如下：

| 参数名 | 说明 |
|--------|------|
| `RAY_EXPERIMENTAL_NOSET_ASCEND_RT_VISIBLE_DEVICES` | 是否禁用 Ray 对 ASCEND_RT_VISIBLE_DEVICES 的自动设置，'true'为禁用 |
| `TOKENIZERS_PARALLELISM` | 设置tokenizers是否支持并行，'true'为支持 |
| `NCCL_DEBUG` | NCCL Debug日志级别，VERSION、WARN、INFO、TRACE |
| `PYTORCH_NPU_ALLOC_CONF` | 设置缓存分配器行为 |
| `HCCL_CONNECT_TIMEOUT` | HCCL 连接超时时间 |
| `HCCL_EXEC_TIMEOUT` | HCCL 执行超时时间 |
| `HCCL_IF_BASE_PORT` | HCCL 通信端口 |
| `CUDA_DEVICE_MAX_CONNECTIONS` | 设备最大连接数 |
| `HYDRA_FULL_ERROR` | 设置 HYDRA 是否输出完整错误日志 |
| `VLLM_DP_SIZE` | vLLM数据并行度（Data Parallelism）大小，控制数据分片数量，稠密模型需要设置为1，MOE模型要求必须和EP一致 |
| `HCCL_BUFFSIZE` | HCCL通信层单次传输的最大缓冲区大小（单位MB），影响跨设备通信效率 |
| `VLLM_USE_V1` | 使用vLLM的V1 engine API（v1接口），当前只支持 v1 ，需设置为 '1' |
| `USING_LCCL_COM` | 指定不使用 LCCL 通信 |
| `VLLM_VERSION` | 指定使用的vLLM版本号 |
| `VLLM_ENABLE_TOPK_OPTIMZE` | 使能vLLM TOPK性能优化 |
| `VLLM_ASCEND_ACL_OP_INIT_MODE` | vLLM aclop 初始化模式: 0: default, normal init. |
| `TASK_QUEUE_ENABLE` | 控制开启task_queue算子下发队列优化的等级，推荐设置为 '2' 使能 Level 2 优化 |
| `CPU_AFFINITY_CONF` | 指定使用绑核优化，推荐设置为 '1' |
| `LCAL_COMM_ID` | 开启coc特性时配套启用，设置为'127.0.0.1:27001' |
| `GLOO_SOCKET_IFNAME` | 指定 GLOO 框架通信网卡 |
| `TP_SOCKET_IFNAME` | 指定 TP 相关通信网卡 |
| `HCCL_SOCKET_IFNAME` | 指定 HCCL 通信网卡 |

**逐行解读**：

| 行 | 变量 | 解读 |
|---|---|---|
| 1 | `RAY_EXPERIMENTAL_NOSET_ASCEND_RT_VISIBLE_DEVICES` | Ray 默认会向 worker 注入 `ASCEND_RT_VISIBLE_DEVICES`，在多 NPU 拓扑下会与 mindspeed-rl 自身分配策略冲突；设为 `'true'` 可禁用 Ray 的自动注入，由框架手动管理 device 可见性。 |
| 2 | `TOKENIZERS_PARALLELISM` | HuggingFace tokenizers 的多进程分词开关；RL 高频 rollout 场景下需设为 `'true'` 避免 tokenizer fork 死锁（标准 HF 文档建议）。 |
| 3 | `NCCL_DEBUG` | NCCL 日志级别四档递增：VERSION（仅版本）→WARN（默认，仅警告）→INFO（关键事件）→TRACE（全量收发），用于通信 hang 排查。 |
| 4 | `PYTORCH_NPU_ALLOC_CONF` | 透传 torch_npu 内存分配器配置（如 `expandable_segments:True` 等），控制 NPU 上的 caching allocator 行为以缓解 OOM/碎片。 |
| 5 | `HCCL_CONNECT_TIMEOUT` | HCCL 集合通信建立连接的超时阈值，避免在节点故障时无限等待。 |
| 6 | `HCCL_EXEC_TIMEOUT` | HCCL 一次集合通信操作（allreduce/broadcast 等）的执行超时。 |
| 7 | `HCCL_IF_BASE_PORT` | HCCL 起始监听端口，影响多实例/多 rank 共存时的端口规划。 |
| 8 | `CUDA_DEVICE_MAX_CONNECTIONS` | 沿用 CUDA 生态语义，限制单 NPU 上并发 HCCL/NCCL 连接数，缓解多 stream 竞争导致的 kernel launch 抖动。 |
| 9 | `HYDRA_FULL_ERROR` | Hydra（mindspeed-rl 配置层依赖）是否打印完整 stack trace，便于定位 yaml/CLI 解析错误。 |
| 10 | `VLLM_DP_SIZE` | vLLM 数据并行度；稠密模型必须置 1，MOE 模型必须等于 EP（专家并行度），否则会出现权重/路由不匹配。 |
| 11 | `HCCL_BUFFSIZE` | HCCL 单次传输最大缓冲（MB），增大可提升大消息吞吐，减小可降低延迟。 |
| 12 | `VLLM_USE_V1` | 强制使用 vLLM v1 engine API；当前 mindspeed-rl 仅兼容 v1。 |
| 13 | `USING_LCCL_COM` | 反向开关：置位表示**不使用** LCCL（低延迟通信），回退到 HCCL。 |
| 14 | `VLLM_VERSION` | 锁定 vLLM 版本号，避免上游 API 变更破坏兼容性。 |
| 15 | `VLLM_ENABLE_TOPK_OPTIMZE` | 开启 vLLM TOPK 采样/路由算子的性能优化路径（注意原拼写 `OPTIMZE`）。 |
| 16 | `VLLM_ASCEND_ACL_OP_INIT_MODE` | vLLM 内部 ACL 算子初始化模式；`0` 为默认 normal init。 |
| 17 | `TASK_QUEUE_ENABLE` | 算子下发队列优化等级；推荐 `'2'` 开启 Level 2，最大化 host→device 提交吞吐。 |
| 18 | `CPU_AFFINITY_CONF` | 绑核优化开关；推荐 `'1'` 启用，将 rank 绑定到指定 CPU core，减少跨 NUMA 访问。 |
| 19 | `LCAL_COMM_ID` | CoC（Collective over Communication）特性配套开关，固定为 `127.0.0.1:27001`。 |
| 20 | `GLOO_SOCKET_IFNAME` | GLOO（CPU 集合通信，多用于参数服务器/同步屏障）使用的物理网卡名。 |
| 21 | `TP_SOCKET_IFNAME` | 张量并行（TP）相关通信（如权重 allgather）使用的网卡名。 |
| 22 | `HCCL_SOCKET_IFNAME` | HCCL 主集合通信使用的网卡名，与上两条配合实现三类流量物理隔离。 |

---

## 【公式解读】

原文无公式（无 LaTeX、无伪代码、无数学表达式）。涉及定量约束仅为表格中的"必须等于 1 / 必须等于 EP / 推荐 '2' / 推荐 '1' / 127.0.0.1:27001"等离散取值。

**原文无公式。**

---

## 【关联】

- **配置文件载体**：`configs/envs/runtime_env.yaml` 是 mindspeed-rl 配置体系的一部分，与项目其他 yaml（如模型/RL 算法/并行策略配置）并列存在，受 Hydra 框架管理——因此 `HYDRA_FULL_ERROR` 的设置直接关系本文档的调试体验。
- **依赖框架**：Ray（调度与 worker 编排）、vLLM（推理 rollout）、HCCL（昇腾集合通信）、LCCL（低延迟通信，可被 `USING_LCCL_COM` 关闭）、GLOO（CPU 通信）、tokenizers（RL 的 prompt/response 编解码）、torch_npu（设备内存分配器）、Hydra（配置层）。
- **强约束的下游特性**：
  - MOE 模型训练要求 `VLLM_DP_SIZE == EP`，与 EP（Expert Parallel）特性联动；
  - CoC 特性要求同步设置 `LCAL_COMM_ID=127.0.0.1:27001`；
  - `VLLM_USE_V1=1` 表明当前仅对接 vLLM v1 engine API。
- **vLLM 内部子开关**：`VLLM_ENABLE_TOPK_OPTIMZE` 与 `VLLM_ASCEND_ACL_OP_INIT_MODE` 属于 vLLM Ascend 后端自定义变量，由 vLLM 自身识别生效。
- **性能优化三件套**：`TASK_QUEUE_ENABLE`、`CPU_AFFINITY_CONF`、`VLLM_ENABLE_TOPK_OPTIMZE` 分别作用于算子下发、CPU 调度、推理 TOPK 路径，在 RL 高频迭代中协同降抖动。
- **网络隔离三件套**：`HCCL_SOCKET_IFNAME`、`GLOO_SOCKET_IFNAME`、`TP_SOCKET_IFNAME` 用于在多网卡节点上把不同通信流量打散到不同物理网卡/RoCE 设备，避免 RDMA 拥塞。
- 原文**未提供**任何内部链接（如「参见 vLLM 配置」「参见并行策略」），本节关联均基于文档本身出现的变量名/特性名做语义推断。

---

## 【使用方法】

- **启用方式**：直接编辑仓库根目录下的 `configs/envs/runtime_env.yaml`，按 yaml 语法填写 `KEY: VALUE`；框架启动时会自动加载并 `os.environ` 注入到所有 Ray worker / 训练进程 / vLLM 推理进程。
- **典型推荐配置（按原文推荐值）**：
  - `RAY_EXPERIMENTAL_NOSET_ASCEND_RT_VISIBLE_DEVICES: 'true'`（避免 Ray 与 mindspeed-rl 的 device 分配冲突）
  - `TOKENIZERS_PARALLELISM: 'true'`
  - `VLLM_USE_V1: '1'`
  - `VLLM_DP_SIZE: '1'`（稠密模型）或 `VLLM_DP_SIZE: '<与 EP 相等>'`（MOE 模型）
  - `TASK_QUEUE_ENABLE: '2'`
  - `CPU_AFFINITY_CONF: '1'`
  - `VLLM_ENABLE_TOPK_OPTIMZE: 'true'`
  - `LCAL_COMM_ID: '127.0.0.1:27001'`（仅当启用 CoC 特性时）
- **调试场景**：
  - 通信 hang → 调高 `NCCL_DEBUG` 至 `INFO/TRACE`，并设置 `HCCL_CONNECT_TIMEOUT / HCCL_EXEC_TIMEOUT`；
  - OOM/内存碎片 → 调整 `PYTORCH_NPU_ALLOC_CONF`（如启用 expandable_segments）；
  - Hydra 配置报错 → 打开 `HYDRA_FULL_ERROR`；
  - 关闭 LCCL → 设置 `USING_LCCL_COM`（按字面理解为反义开关，需结合代码确认置位语义）。
- **多网卡部署**：在多 RoCE 网卡节点上，**必须**为 `HCCL_SOCKET_IFNAME / GLOO_SOCKET_IFNAME / TP_SOCKET_IFNAME` 分别指定不同网卡名，否则三类流量会在同一网卡上竞争。
- 原文**未涉及**具体的 CLI 启动命令、`ray start` 参数或脚本调用方式，亦未提供 docker/k8s 注入环境变量的样例。
