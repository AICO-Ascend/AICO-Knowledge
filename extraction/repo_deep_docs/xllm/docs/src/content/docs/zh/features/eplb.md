# eplb

> 仓 `xllm` · 路径 `docs/src/content/docs/zh/features/eplb.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/xllm/docs/src/content/docs/zh/features/eplb.md

# xLLM EPLB 文档深度解读

## 【定位】
本文描述 xLLM 的 **Expert Parallel Load Balancing（EPLB）** 能力——面向 MoE 模型在线推理，通过在热点逻辑专家上创建冗余物理副本，并在服务运行期间逐层调整 EP rank 上的专家分布，缓解因请求分布不均导致的"最慢 EP rank 瓶颈"，同时不改变模型逻辑专家数与路由结果。

---

## 【技术要点】

1. **逻辑专家 vs 物理槽位的双层映射**：EPLB 仅维护「逻辑专家 → 物理槽位」映射并迁移权重，不改变路由；同一逻辑专家可拥有多个物理副本。当前一 worker 对应一 EP rank 时，每 rank 槽位数为 `local_physical_experts = logical_experts / ep_size + redundant_experts_num`，全局为 `logical_experts + ep_size * redundant_experts_num`，并要求 `logical_experts` 能被 `ep_size` 整除。

2. **两阶段发布协议（prepare / activate）**：控制面通过 `EplbInfo` 携带 `prepare_layer_id` + `prepare_token` + `expert_ids` 触发后台 prepare；所有 rank 上报同一 prepare token 后再发布 `update_layer_id` + `activation_token`；激活以"旧布局完成本次 forward，下一次 forward 才看到新布局"的边界方式落地，迟到/重复 token 会被忽略。

3. **基于实测物理负载的改进率门控**：候选峰值根据候选布局估算，发布条件是预计峰值下降比例 ≥ `eplb_min_peak_load_improvement`（默认 0.05）且布局发生变化；prepare 超时调用策略 `abort_layer` 回滚，绝不把未部署布局当成已生效。

4. **DeepSeek V4 稳定地址 + staging 切换**：启动时扩展每层权重并预热可复用 staging buffer（MTP 模型不重复预留）；prepare 阶段只在 host 侧生成映射与 P2P 计划；同 rank 已驻留专家直接复制到 pending buffer，非驻留通过专用 `ProcessGroupHCCL` 做批量 `isend/irecv`；活动 tensor 原地更新内容与映射以满足 ACL graph 对稳定地址的要求；变化槽位 < 一半走增量 copy，≥ 一半走整 tensor `copy_` 激活。

5. **可插拔策略与发布门控**：`eplb_policy_kind` 选 `balanced`（默认，先按最大负载下降选副本，再在全互联 HCCS 超节点所有 rank 间等容量 LPT packing）或 `greedy`（历史贪心 + LPT），字符串大小写不敏感、未知值回退 `greedy`；历史策略名作为兼容别名映射到 `balanced`；同一逻辑专家在同一 rank 上最多一个副本。

6. **EPLB 与 MC2/EP2/ACL Graph 的正交集成**：`expert_parallel_degree=2` 决定是否走 EP2 dispatch/combine；`enable_fused_mc2`（-1/0/1/2）进一步在 `DispatchFFNCombine` / `DispatchGmmCombineDecode` 与普通 `moe_distribute_dispatch_v2 + group_gemm + moe_distribute_combine_v2` 间选择；MC2 模式只改变执行与物理负载采集，不改变 EPLB 策略与切换协议；ACL graph 路径下 log2phy 与权重保持稳定存储，decode mask 按 DP rank 对齐补零避免污染负载。

---

## 【关键机制与数据】

**工作原理与数据流（运行流程 7 步，原文 §运行流程）：**
- 步骤 1：每个 worker 在 MoE forward 中按"槽位前缀和编码"记录各层本地物理专家槽位 token 数，`EplbAggregator` 通过差分恢复每个槽位的真实负载。
- 步骤 2：`LLMEngine` 收集所有 worker 负载，并把"采样时生效的专家分布与负载一起入队"，防止随后激活导致旧样本被错误解释为新布局的负载。
- 步骤 3：第一份有效负载到达后启动 `eplb_update_interval` 定时器；定时器到期且无其他 rebalance 进行时，manager 要求策略为每个层重新计算候选布局。
- 步骤 4：候选用当前实测物理负载计算最慢 rank 改善率，**只有布局变化且改善率 ≥ `eplb_min_peak_load_improvement` 的层才发布**。
- 步骤 5：`EplbExecutor` 在后台线程计算 log2phy、变化槽位与 EP-wide P2P 迁移计划；prepare 成功才原子上报 token，失败不会伪装成 ready。
- 步骤 6：所有 rank 上报同一 prepare token 后 manager 发布 `update_layer_id`；worker 在 forward 前物化 staging 权重并启动 P2P，forward 后等待迁移完成并激活。
- 步骤 7：携带 `activation_token` 的 forward 输出回到 engine 后，manager 才提交策略状态、切换活动分布，并清空物理负载窗口。

**下发边界约束（原文）：**
> "EPLB 命令只会在至少一个 DP batch 非空、所有非空 DP batch 都处于 decode、且不是 graph warmup 的 forward 边界下发。空 DP rank 可以参与该边界。"
> "副作用是持续没有纯 decode 边界时，已经准备好的层会延迟激活。"

**ACL graph pool 优化（原文）：**
> "同一个 `AclGraphExecutor` 创建的 decode graph bucket 共用一个固定 capture stream 和一个 private graph pool，使不同 bucket 可以复用 graph 临时地址，避免每个预热 bucket 都独立保留一组 expandable segment。该优化避免 graph pool 显存随 bucket 数量线性增长，但 graph pool、persistent tensor 和运行时缓存仍会占用显存。"

**关键默认参数（原文 §配置参数）：**
- `eplb_update_interval` 默认 `1000` 秒，文中示例覆盖为 `300`。
- `eplb_min_peak_load_improvement` 默认 `0.05`，范围 `[0,1]`。
- `eplb_prepare_timeout_seconds` 默认 `30`，必须 > 0，超时后跳过并回滚该层。
- `redundant_experts_num` 默认 `1`，必须 ≥ 0。

> 原文未给出端到端性能数字（如吞吐、延迟、显存节省的实测值），仅给出**发布门控阈值**与**策略耗时相关日志**（`EPLB rebalance`、`prepare_expert_weight`、`materialize_expert_weight`、`update_expert_weight` 等）。

---

## 【表格解读】

### 表格 1：当前架构组件与职责（原文 §当前架构）

| 组件 | 主要职责 |
|---|---|
| `LLMEngine` | 从所有 worker 收集负载与 prepare token，把 `EplbInfo` 命令写入下一次 forward 输入。 |
| `EplbManager` | 管理更新定时器、活动分布、逐层 prepare/activate 状态机、超时和提交。 |
| `EplbAggregator` | 把各 rank 的物理槽位计数还原为本轮增量，同时保留物理负载并聚合逻辑专家负载。 |
| `IEplbPolicy` | 根据逻辑负载、物理负载和当前分布生成候选布局及逐层更新掩码。 |
| `EplbExecutor` | 在每个 worker 上执行异步 prepare，并在 forward 边界启动迁移和激活。 |
| 模型 EPLB hook | 维护逻辑到物理映射、生成 P2P 计划、迁移权重并切换活动权重。 |
| `ProcessGroup` | 通过专用 `ProcessGroupHCCL` 批量调用 HCCL 点对点 send/recv；当前全互联超节点的数据面使用 HCCS。 |

**逐行解读：**
- `LLMEngine` 是控制面入口，负责收集与转发，本身不参与权重搬运。
- `EplbManager` 是总调度器，拥有"定时器 + 状态机 + 提交权"，是协议一致性的核心。
- `EplbAggregator` 通过**前缀和编码的差分**反解每个槽位真实负载，并同时输出物理与逻辑两层聚合。
- `IEplbPolicy` 是策略接口，根据聚合结果产出**候选布局**与**逐层更新掩码**（决定哪些层值得发布）。
- `EplbExecutor` 是 worker 侧执行器，把策略产物落地为真实的 prepare 与迁移。
- 模型 EPLB hook 是模型侧适配点（原文 §概述 强调其他模型必须实现 `prepare_expert_weight`、`start_expert_weight_transfer`、`update_expert_weight` 才能复用同一运行时协议）。
- `ProcessGroup`（`ProcessGroupHCCL`）负责 P2P 通信；原文明确"当前全互联超节点的数据面使用 HCCS"，EPLB 不再区分机器边界。

### 表格 2：Rebalance 策略（原文 §Rebalance 策略）

| 策略 | 布局算法 | 适用场景 |
|---|---|---|
| `balanced` | 先按最大负载下降选择副本，再在全互联 HCCS 超节点的所有 rank 间做等容量 LPT packing。 | 默认策略，推荐用于当前超节点部署。 |
| `greedy` | 历史 xLLM 贪心副本选择和 LPT packing。 | 兼容历史行为。 |

**逐行解读：**
- `balanced` 是当前推荐策略，先解决"在哪儿多放一份热点专家"（副本选择），再解决"放在哪个 rank 最均衡"（跨 rank 等容量 LPT packing）。
- `greedy` 保留历史行为，仅作兼容；原文明确"历史策略名称仍作为兼容别名解析为 `balanced`，新配置统一使用 `balanced`"。
- 两者共享同一组发布门控（见技术要点 3）。

### 表格 3：`enable_fused_mc2` 取值与行为（原文 §EP2、MC2 与 ACL Graph）

| `enable_fused_mc2` | 行为 |
|---:|---|
| `-1` | 自动选择。`expert_parallel_degree=2` 时解析为 `1`，否则解析为 `0`。 |
| `0` | 使用 `moe_distribute_dispatch_v2 + group_gemm + moe_distribute_combine_v2` 路径。 |
| `1` | 满足量化、dtype、算子和 graph 准备条件时使用 `DispatchFFNCombine`。 |
| `2` | 纯 decode 且满足前置条件时使用 `DispatchGmmCombineDecode`。 |

**逐行解读：**
- `-1` 是自动模式，与 `expert_parallel_degree` 联动——EP2 时倾向融合算子，非 EP2 时回退普通路径。
- `0` 走 v2 dispatch/combine + group_gemm，是稳定基准路径。
- `1` 走 `DispatchFFNCombine`（更激进的融合），前提是量化、dtype、算子可用、graph 准备都满足。
- `2` 是纯 decode 特化的 `DispatchGmmCombineDecode`，对混合 batch 不友好。
- 当请求的 MC2 路径不满足前置条件时，运行时会**自动回退到可用普通 MoE 路径**；MC2 只影响执行与负载采集，不影响 EPLB 策略。

### 表格 4：EPLB 配置参数（原文 §配置参数）

| 参数 | 默认值 | 约束与说明 |
|---|---:|---|
| `enable_eplb` | `false` | 开启动态专家负载均衡。 |
| `redundant_experts_num` | `1` | 每个 EP rank 的额外物理专家槽位数，必须大于等于 0。 |
| `eplb_update_interval` | `1000` | 从第一份有效负载开始计时的 rebalance 间隔，单位为秒，必须大于等于 0。本文示例显式覆盖为 `300`。 |
| `eplb_min_peak_load_improvement` | `0.05` | 所有策略候选布局需要达到的最慢 rank 最小预计改善比例，范围 `[0, 1]`。 |
| `eplb_policy_kind` | `balanced` | `balanced`（默认）或 `greedy`；历史名称兼容映射到 `balanced`，未知值回退到 `greedy`。 |
| `eplb_use_decode_only_load` | `false` | eager 路径是否只统计真实 decode token。graph 路径始终过滤 padding。 |
| `eplb_prepare_timeout_seconds` | `30` | 所有 rank 等待同一层 prepare 完成的超时，必须大于 0。超时后跳过并回滚该层。 |
| `expert_parallel_degree` | `0` | EP 模式参数；设为 `2` 时启用满足条件的 EP2 dispatch/combine 路径。 |
| `enable_fused_mc2` | `-1`（自动） | 有效值为 `-1/0/1/2`；自动模式在 `expert_parallel_degree=2` 时解析为 `1`，否则解析为 `0`。 |

**逐行解读：**
- `enable_eplb` 是总开关；默认关闭，部署时需显式打开。
- `redundant_experts_num` 决定"还能多放几个副本"，直接放大权重显存与 EPLB staging 显存（原文 §运行约束 强调要在启动前为 KV cache 与 EPLB staging 留余量）。
- `eplb_update_interval` 与 `eplb_min_peak_load_improvement` 共同决定**再均衡的频率与门槛**——更新太频繁会浪费 P2P 带宽，更新太迟则缓解滞后。
- `eplb_prepare_timeout_seconds=30` 给出 30 秒全 rank 等待窗口；超时不会让 manager 卡死，而是跳过该层。
- `eplb_use_decode_only_load=false` 表示默认统计全部 token；启用后 eager 路径会过滤 mixed batch 中的 prefill 行，graph 路径始终过滤 padding。
- `expert_parallel_degree` 与 `enable_fused_mc2` 是执行路径开关，**EPLB 不依赖 EP2**（"EPLB 控制面不要求 `expert_parallel_degree=2`"）。

### 表格 5：可观测性日志前缀（原文 §可观测性与排障）

| 日志前缀 | 含义 |
|---|---|
| `EPLB manager start` | 实际策略、MoE 层数、device 数和每 device 物理槽位数。 |
| `EPLB rebalance` | 本轮策略耗时和需要更新的层数。 |
| `EPLB placement benefit` | 策略的当前峰值、候选峰值、改善比例和收益门控结果。 |
| `prepare_expert_weight` | worker 后台 prepare 的层、槽位表大小、耗时和失败状态。 |
| `materialize_expert_weight` | DeepSeek V4 在 forward 边界物化 staging tensor 的耗时。 |
| `update_expert_weight` | 层、rank、MC2 模式、变化槽位、P2P 数、迁移耗时、激活耗时和总耗时。 |
| `EPLB heartbeat` | rebalance、manager、executor 和 P2P bucket 的存活及进度信息。 |
| `EPLB staging reservation warmed` | 启动时预留的 staging bytes 和 tensor 数。 |

**逐行解读：**
- `EPLB manager start` 是部署态观测点，能反查实际生效的策略、拓扑与每 device 槽位数。
- `EPLB placement benefit` 是**门控可观测性**——能直接看到当前峰值、候选峰值、改善比例是否越过门槛。
- `prepare_expert_weight` / `materialize_expert_weight` / `update_expert_weight` 是端到端三段耗时；排障时需联合看以区分 prepare、staging 物化、迁移/激活瓶颈。
- 排障流程（原文）：先确认所有 rank 的 `prepare_token` 是否一致 → 再看 `tasks_failed_since_last` / `layers_timed_out` / `update_expert_weight` → 仅部分 rank 进入 P2P 表现为 prepare 超时 → SHM 不兼容会在启动阶段直接报 layout 错误。

---

## 【公式解读】

### 公式 1：每 rank 物理专家槽位数

```text
local_physical_experts = logical_experts / ep_size + redundant_experts_num
```

**符号含义：**
- `logical_experts`：模型路由器输出的专家 ID 数量，由模型结构决定。
- `ep_size`：EP rank 数；当前 EPLB 聚合要求 `ep_size == worker_num`（一 worker 对一 EP rank）。
- `redundant_experts_num`：每 EP rank 上额外预留的物理专家槽位数，用于放置热点逻辑专家的副本，必须 ≥ 0。
- `local_physical_experts`：单个 EP rank 上的总物理槽位数（基础均分 + 冗余）。

**作用：** 决定每 rank 的显存基线；`redundant_experts_num` 直接放大权重显存与 staging 显存。

### 公式 2：全局物理专家槽位数

```text
global_physical_experts = logical_experts + ep_size * redundant_experts_num
```

**符号含义：**
- `logical_experts`：见公式 1。
- `ep_size`：见公式 1。
- `redundant_experts_num`：见公式 1。
- `global_physical_experts`：所有 EP rank 的物理槽位总和。

**作用：** 由于 `local_physical_experts × ep_size = (logical_experts + ep_size * redundant_experts_num) / 1`，即基础均分正好放下 `logical_experts` 个逻辑专家，每个 rank 多出来的 `redundant_experts_num` 槽位就是用来放副本的。该式还隐含约束 `logical_experts % ep_size == 0`（基础均分必须整除）。

---

## 【关联】

- **EP 并行参数（./moe_params.md）**：原文末尾明确"EP 和 DP/TP 组合方式参见 [EP 并行](./moe_params.md)"。`expert_parallel_degree` 与 EP 并行配置共同决定 EP2 路径与 DP/TP 拓扑，是 EPLB 启用的前置上下文。
- **DeepSeek V4 NPU `npu_torch/FusedMoE`**：本文重点描述的实现路径；其他模型若要复用同一运行时协议，必须实现 `prepare_expert_weight`、`start_expert_weight_transfer`、`update_expert_weight` 三个模型 hook（原文 §概述）。
- **ACL graph 体系**：EPLB 在 graph 模式下要求 log2phy 与权重保持稳定存储、decode mask 按 DP rank 对齐补零；同一 `AclGraphExecutor` 的 decode graph bucket 共享 capture stream 与 private graph pool（原文 §EP2、MC2 与 ACL Graph）。
- **HCCL / HCCS 通信栈**：`ProcessGroupHCCL::send/recv` 是 P2P 落地点；当前全互联超节点数据面使用 HCCS，EPLB 不再区分机器边界（原文 §DeepSeek V4 权重切换）。
- **SharedMemoryManager（layout v2）**：EPLB 控制字段与 worker 输出经过 xLLM forward 共享内存，SHM 不兼容会在启动阶段直接失败（原文 §共享内存兼容性）。
- **xLLM JSON 配置 / gflags**：所有 EPLB 参数双通道生效，manager 创建时快照到 `EplbOptions`，修改后必须重启（原文 §配置参数）。

---

## 【使用方法】

### 启用方式（原文 §启动示例，16 worker 全互联 HCCS 超节点，300 秒测试周期）

```bash
--enable_eplb=true \
--ep_size=16 \
--expert_parallel_degree=2 \
--redundant_experts_num=1 \
--eplb_update_interval=300 \
--eplb_policy_kind=balanced \
--eplb_min_peak_load_improvement=0.05 \
--eplb_use_decode_only_load=true \
--enable_fused_mc2=1
```

### 关键配置项与硬约束

| 类别 | 内容 |
|---|---|
| 总开关 | `--enable_eplb=true` |
| 拓扑 | `--ep_size=16`（必须与实际 worker 数一致，且 > 1） |
| 副本量 | `--redundant_experts_num=1`（≥ 0） |
| 再均衡节奏 | `--eplb_update_interval=300`（默认 1000 秒） |
| 策略 | `--eplb_policy_kind=balanced`（默认；`greedy` 仅作兼容） |
| 发布门槛 | `--eplb_min_peak_load_improvement=0.05`（[0,1]） |
| 负载语义 | `--eplb_use_decode_only_load=true`（graph 路径始终过滤 padding） |
| MC2 路径 | `--enable_fused_mc2=1`（与 `expert_parallel_degree=2` 联动） |
| 整除约束 | 模型逻辑专家数必须能被 `ep_size` 整除 |
| 生效时机 | manager 创建时快照到 `EplbOptions`；修改后**必须重启服务**才能生效 |
| 显存预算 | 需为 KV cache 与 EPLB staging 显存留余量 |
| 升级兼容 | SHM 不兼容会在启动阶段直接失败；新旧二进制滚动混跑不受支持 |
