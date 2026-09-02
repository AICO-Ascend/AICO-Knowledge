# eplb

> 仓 `xllm` · 路径 `docs/src/content/docs/en/features/eplb.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/xllm/docs/src/content/docs/en/features/eplb.md

# xLLM EPLB 文档一体化深度解读

---

## 【定位】

本文档系统描述了 xLLM 推理引擎中 **Expert Parallel Load Balancing (EPLB)** 能力的定位、架构组件、运行时流程、负载采集、再平衡策略以及 DeepSeek V4 NPU 路径上的权重切换机制,核心目的是解决 MoE 模型在线服务中"热门专家造成的 EP rank 间负载不均、个别 rank 成为整批推理瓶颈"的问题,通过冗余物理专家副本与运行时层粒度的位置重映射来动态平衡 Expert Parallel 各 rank 的负载,同时不改变模型逻辑专家数量与路由结果。

---

## 【技术要点】

1. **逻辑专家 vs 物理槽位分离**: 文档严格区分 *Logical expert*(路由器输出的 ID,数量由模型架构决定) 与 *Physical expert slot*(EP rank 上的驻留副本,一个逻辑专家可有多个物理副本),EPLB 通过维护 logical-to-physical 映射并迁移对应权重实现重平衡。

2. **冗余副本与槽位公式** (原文):
   - `local_physical_experts = logical_experts / ep_size + redundant_experts_num`
   - `global_physical_experts = logical_experts + ep_size * redundant_experts_num`
   
   要求 `logical_experts` 必须能被 `ep_size` 整除;`redundant_experts_num` 在每个 rank 上增加额外槽位,会同时增加专家权重内存与 EPLB staging 内存。

3. **控制平面 `EplbInfo` 字段**: 包含 `prepare_layer_id` / `prepare_token`(隔离超时后的过期结果) / `expert_ids`(待生效的全局物理槽位表) / `update_layer_id` / `activation_token`(证明对应 forward 真正完成)。

4. **组件职责** (7 大模块): `LLMEngine`(收集每个 worker 的 load 与 prepare token) → `EplbManager`(定时器、active placement、状态机、超时) → `EplbAggregator`(差分解码物理槽位计数器、聚合并保留物理负载) → `IEplbPolicy`(基于逻辑/物理负载生成候选 placement 与逐层 update mask) → `EplbExecutor`(异步 prepare、前向边界触发迁移与激活) → Model EPLB hooks(`prepare_expert_weight` / `start_expert_weight_transfer` / `update_expert_weight`) → `ProcessGroup`(通过专用 `ProcessGroupHCCL` 批量 HCCL 点对点 send/recv,全互联超节点数据面走 HCCS)。

5. **发布门控 (Publication gate)**: 仅当候选 placement 的峰值降幅 ≥ `eplb_min_peak_load_improvement` 时才发布迁移;每层独立发布、逐层 prepare 与 update;同一逻辑专家在同一 rank 上最多一个副本;prepare 超时调用 `abort_layer` 回滚候选状态(不把未部署的 placement 当作 active)。

6. **前向边界约束**: EPLB 命令仅在「至少一个非空 DP batch、全部非空 DP batch 都处于 decoding、且输入非 graph warmup」的前向边界发出,目的是**禁止在 prefill 或 graph capture 仍可能读取旧权重时切换**,因此一个已 prepare 的层若 workload 始终不到 all-decode 边界,会一直 pending。

---

## 【关键机制与数据】

### 1) 运行时再平衡的完整序列 (原文 Runtime Flow,7 步):

1. 每个 worker 在 MoE forward 时记录**每个本地物理槽位的 token 数**,沿槽位维做**前缀编码 (prefix encoded)**,`EplbAggregator` 通过**差分运算**还原每个槽位的值。
2. `LLMEngine` 收集所有 worker 的负载;**样本提交时所处的 active placement 与该样本一同排队**,因此历史样本不会在后续被新激活的 placement 错误解释。
3. 第一份有效负载样本启动 `eplb_update_interval` 定时器;到期且无其他 rebalance 进行时,manager 请求所选策略**为每一层重算候选**。
4. 每个候选相对当前测得的物理峰值进行评估;仅当 placement 改变 **且** 改善量达到 `eplb_min_peak_load_improvement` 时,manager **逐层**发布 `prepare_layer_id`、`prepare_token` 与新的 `expert_ids`。
5. worker 的 `EplbExecutor` 后台线程计算 logical-to-physical map、changed slots 与 EP-wide P2P migration plan;**仅在 prepare 成功后才原子上报匹配 token,失败的 prepare 永远不会被报为 ready**。
6. **所有 rank 都上报同一 prepare token 后**,manager 才发布 `update_layer_id`。在 DeepSeek V4 路径上,每个 worker 在 forward 前物化 staging 权重并启动 P2P,等待迁移完成,**在 forward 之后激活权重**。
7. **只有对应 forward 输出带着 `activation_token` 返回后**,manager 才提交策略状态、切换 active placement 并重置 physical-load window;迟到或重复的 token 被忽略。

### 2) 负载采集的两视图 (原文 Load Collection):

- **Logical expert load**: 通过 active slot table 将物理副本负载聚合到逻辑专家 ID,供策略识别热门专家并选副本。
- **Physical slot load**: 保持 `[layer, rank, slot]` 形态,让策略在当前 placement 下测量真实的**最慢 rank**,而非假设同一逻辑专家的多个副本负载相等。

DeepSeek V4 在三种执行模式下统一使用同一负载语义:

- Graph warmup **不进入** manager 的负载窗口。
- ACL graph 使用 per-token mask 去除 graph padding 与空 DP rank 上的合成 token。
- `eplb_use_decode_only_load=true` 时,**eager 执行也仅记录真实 decode token**,并从 mixed batch 中剔除 prefill 行。
- Fused dispatch 在可能时记录 operator 返回的接收端观察到的物理专家计数;当无法从 aggregate operator 计数中过滤混合阶段时,回退到 route-ID 计数。

### 3) DeepSeek V4 权重切换 (原文 DeepSeek V4 Weight Switching,节选/截断):

- `FusedMoE` 路径维护**稳定地址的 active 权重、pending staging 权重**与 **`log2phy` map**。
- 启动时权重存储已扩展为包含每个 rank 的冗余专家槽位。
- 主模型权重加载后,**复用的 staging buffer 会被预热**,使首次 rebalance 不会按需分配大块 NPU buffer;**MTP 模型不复用 staging pool**(不预留重复)。
- Prepare **仅在 host 端计算 slot map 与 P2P plan**,不与可能正在读取同一组 NPU tensor 的 forward 并发物化私有格式。
- 同 rank 已驻留的 expert 直接拷贝到 pending buffer;**非驻留 expert 通过专用 EPLB `ProcessGroupHCCL` 迁移**。
- `batch_isend_irecv` 最终调用 `ProcessGroupHCCL::send/recv`;HCCL 是通信库 API,当前全互联超节点上 rank-to-rank 数据走 HCCS;**EPLB 不建模 host 边界**。

> 注:原文最后一句 "Send and receive operations for all tensors share one batched plan" 在文档中被 `---` 截断,后续内容(若存在)在所提供的原文中不可见。

### 4) 数据/性能数字

**原文未给出数值化的性能基准或吞吐数字**,所有出现的数字/参数均为配置项或公式常量(详见【表格解读】与【使用方法】)。按指令「不臆造原文没有的数字/机制」,此处不补充任何具体百分比/毫秒/QPS。

---

## 【表格解读】

### 表 1:组件职责表 (Current Architecture)

> 原文逐字还原:

| Component | Responsibility |
|---|---|
| `LLMEngine` | Collects load and prepare tokens from every worker and places `EplbInfo` commands in the next forward input. |
| `EplbManager` | Owns the update timer, active placement, per-layer prepare/activate state machine, timeout handling, and commit. |
| `EplbAggregator` | Decodes physical-slot counters into per-round deltas, preserves physical load, and aggregates logical-expert load. |
| `IEplbPolicy` | Produces a candidate placement and per-layer update mask from logical load, physical load, and the active placement. |
| `EplbExecutor` | Runs asynchronous prepare work on each worker and starts migration and activation at forward boundaries. |
| Model EPLB hooks | Maintain logical-to-physical maps, build P2P plans, migrate weights, and activate the new weights. |
| `ProcessGroup` | Batches HCCL point-to-point send/recv calls through a dedicated `ProcessGroupHCCL`; the current all-connected super-node uses HCCS as its data plane. |

**逐行解读**:
- **`LLMEngine`**: 控制平面入口,统一收口 load 与 prepare token,并把 `EplbInfo` 注入下一个 forward input——把 EPLB 与推理主循环解耦到 forward 边界。
- **`EplbManager`**: 全局调度核心,持有定时器(active placement 生命周期)、逐层 prepare/activate 状态机、超时兜底与最终 commit。
- **`EplbAggregator`**: 数据解码层,将前缀编码还原为 per-slot 增量,**同时保留物理负载**(不让 logical 聚合覆盖 physical 视图)。
- **`IEplbPolicy`**: 策略接口,可插拔,输入是 logical/physical load + active placement,输出是 candidate placement 与 update mask。
- **`EplbExecutor`**: 每个 worker 上的执行体,异步驱动 prepare,并把迁移与激活对齐到 forward boundary。
- **Model EPLB hooks**: 模型侧适配点,负责 map 维护、P2P plan 构建、权重迁移与权重激活——是 EPLB 协议扩展到其他模型的关键接口。
- **`ProcessGroup`**: 通信层抽象,把 HCCL 点对点批量化,由专用 `ProcessGroupHCCL` 承载;数据面在当前全互联超节点上是 HCCS。

### 表 2:再平衡策略表 (Rebalance Policies)

> 原文逐字还原:

| Policy | Placement Algorithm | Intended Use |
|---|---|---|
| `balanced` | Select replicas by maximum load reduction, then equal-capacity LPT packing across every rank in the all-connected HCCS super-node. | Default policy and recommended for the current super-node deployment. |
| `greedy` | Historical xLLM greedy replica selection and LPT packing. | Compatibility with historical behavior. |

**逐行解读**:
- **`balanced`(默认/推荐)**: 先按「最大负载下降」挑选副本,再在 HCCS 全互联超节点的**每个 rank 上做 equal-capacity LPT 装箱**;适合当前的全互联超节点部署形态,峰值降幅可被 `eplb_min_peak_load_improvement` 进一步过滤。
- **`greedy`(历史兼容)**: 保留历史 xLLM 贪心副本选择 + LPT 装箱行为,仅用于向后兼容;**新部署应使用 `balanced`**。文档明确说明 historical 名称保留为 `balanced` 的别名。

---

## 【公式解读】

### 公式 1:每个 EP rank 上的本地物理专家数

```text
local_physical_experts = logical_experts / ep_size + redundant_experts_num
```

**符号含义**:
- `local_physical_experts`: 单个 EP rank 上**驻留**的物理专家副本数(含冗余)。
- `logical_experts`: 模型逻辑专家总数(由架构决定)。
- `ep_size`: Expert Parallel 度(EP 切分大小)。
- `redundant_experts_num`: 每个 rank 额外预留的冗余槽位数(全局共有 `ep_size * redundant_experts_num` 个冗余槽位)。

**作用**: 给出一对一 rank 上的容量上限;该项决定了该 rank 上需要容纳的权重张量数量与 EPLB staging buffer 的规模上限。

**约束**: `logical_experts` 必须能被 `ep_size` 整除,否则无法均匀切分基础槽位。

### 公式 2:全局物理槽位总数

```text
global_physical_experts = logical_experts + ep_size * redundant_experts_num
```

**符号含义**:
- `global_physical_experts`: 全集群所有 EP rank 上的物理专家副本总数。
- 其它符号同公式 1。

**作用**: 用于核算 EPLB 可调度的总容量上限;新增的 `ep_size * redundant_experts_num` 槽位既是负载均衡的"调节阀",也是权重内存与 staging 内存的额外开销来源(原文明确指出这两类内存会随冗余数量同步增长)。

---

## 【关联】

- **`./moe_params.md`** (文末内部链接): MoE 参数相关说明文档,与 EPLB 直接耦合——`ep_size`、`logical_experts`、`redundant_experts_num` 等公式中出现的字段均属于 MoE 并行参数,具体取值与约束需参考该文档。
- **DeepSeek V4 NPU `npu_torch/FusedMoE`**: 文档明确指出"本文档聚焦该路径",意味着 EPLB 协议的具体落地实现(`stable-address active weights` + `pending staging weights` + `log2phy` map)在该算子内完成;其他模型只有实现了 `prepare_expert_weight` / `start_expert_weight_transfer` / `update_expert_weight` 三个 hook 后才能复用同一运行时协议。
- **`ProcessGroupHCCL` / HCCL / HCCS**: EPLB 在通信层与 NPU 集合通信库(HCCL)及超节点互联(HCCS)耦合——HCCL 提供 API,数据面走 HCCS,但 EPLB **不建模 host 边界**,意味着权重迁移仅考虑 device-to-device 拓扑。
- **ACL graph 与 eager 执行**: 负载采集在两种执行模式下使用同一语义,但分别通过 per-token mask 与 `eplb_use_decode_only_load` 处理 graph padding / 合成 token / prefill 行的过滤——这是与图执行/前向执行模块的耦合点。
- **MTP 模型**: 文档指出 **MTP 模型不复用 staging pool**(不预留重复),这意味着 EPLB 在主模型与 MTP 模型上的 staging buffer 分配策略不同——这是与 MTP/投机解码模块的关联点。
- **`LLMEngine` 与 forward 输入注入**: EPLB 通过把 `EplbInfo` 放入下一个 forward input 来同步,故与主推理循环的 forward 调度器是紧耦合关系;此外「all-decode 边界」约束又把 EPLB 与 **prefill / decode 阶段判定** 模块绑定在一起。

---

## 【使用方法】

文档中明确列出的 EPLB 配置项 / 命令如下:

| 配置项 | 作用 / 取值 |
|---|---|
| `eplb_policy_kind` | 选择再平衡策略,大小写不敏感;取值为 `balanced`(默认/推荐,全互联 HCCS 超节点)或 `greedy`(历史兼容);**未知值回退到 `greedy` 而非终止 rebalance 线程**;历史策略名作为 `balanced` 的兼容别名保留。 |
| `eplb_update_interval` | EPLB 更新定时器周期;由"第一份有效负载样本"启动,到期且无其他 rebalance 进行时触发重算。 |
| `eplb_min_peak_load_improvement` | 候选 placement 相对当前物理峰值的最低降幅阈值;**未达到则不发布迁移**。 |
| `eplb_use_decode_only_load=true` | 在 eager 执行下也仅记录真实 decode token,并从 mixed batch 中剔除 prefill 行(ACL graph 默认使用 per-token mask 处理)。 |
| `redundant_experts_num`(公式变量) | 每个 EP rank 的冗余专家槽位数,直接增加本地/全局物理槽位数与权重 + staging 内存开销。 |
| `ep_size`(公式变量) | Expert Parallel 度;**`logical_experts` 必须能被其整除**。 |

**关于模型启用**: 文档聚焦 DeepSeek V4 NPU `npu_torch/FusedMoE` 路径;**其他模型启用 EPLB 的前置条件是实现 3 个 model hook**:`prepare_expert_weight` / `start_expert_weight_transfer` / `update_expert_weight`,然后复用同一运行时协议——具体启用命令(如某 CLI flag / config 文件字段)在提供的原文中未涉及。

> 原文末尾存在 `---` 截断,任何关于 "Send and receive operations for all tensors share one batched plan" 之后的启用细节,在所提供的原文中不可见,故此处不臆测补充。
