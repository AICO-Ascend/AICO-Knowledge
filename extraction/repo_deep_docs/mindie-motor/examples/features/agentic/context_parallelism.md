# Prefill Context Parallel (PCP) 与跨节点 PCP

> 仓 `mindie-motor` · 路径 `examples/features/agentic/context_parallelism.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindie-motor/examples/features/agentic/context_parallelism.md

# mindie-motor · PCP / 跨节点 PCP Feature 文档深度解读

---

## 【定位】

这篇文档描述了 MindIE Motor 如何编排 **Prefill Context Parallel (PCP)** 能力——把长序列的 prefill 计算切分到多张/多节点 NPU 上并行执行,并覆盖了用户在 MindIE Motor 这一层需要关心和配置的参数、自动管理行为、控制面流程、与 DP 叠加的组合方式,以及 Coordinator 侧调度模式与 KV Connector 的兼容性建议。

---

## 【技术要点】

1. **两种部署形态**:单节点 PCP(所有 PCP rank 在同一节点的 NPU 上,只需通过 `prefill-context-parallel-size` 透传给 vLLM)和**跨节点 PCP**(PCP rank 跨节点分布,需要 MindIE Motor 自动化处理节点注册、主从分配、通信地址注入)。
2. **用户最少配置**:跨节点 PCP 用户只需在 `engine_config` 增加 `nnodes` 和 `master-port` 两个字段,其余分布式通信参数(`node-rank`、`master-addr`、`headless` 等)由 MindIE Motor 自动推导和注入。
3. **控制面五步流程**:注册(各节点 NodeManager 带 `nnodes` 注册) → 组装(等待 `dp_size × nnodes` 个节点到齐) → 主从分配(每 `nnodes` 个为一组,组内首节点 `node_rank=0`) → 差异化 StartCmdMsg 下发(带 `node_rank` 和 `master_dp_ip`) → 主节点起 EngineCore+API Server / 从节点仅起 Worker(headless)。
4. **DP × PCP 叠加**:支持 `data_parallel_size > 1` 与跨节点 PCP 组合,例如 DP=4、PCP=2、每节点 16 卡时总共需要 `4 × 2 = 8` 个节点,Controller 等待全部到位后统一组装。
5. **推荐调度组合**:`MooncakeConnectorV1`(非 layerwise)+ `cpcd_separate`;不推荐 `MooncakeLayerwiseConnector`,原因在于 layerwise 按层拆 KV transfer 与 CP 场景的 block 切分不兼容,会产生两类断言失败(Prefill 侧 CP group 数不匹配 / Decode 侧 `num_external_tokens` 不一致)。
6. **从节点生命周期**:跨节点 PCP 的从节点因 headless 不暴露 API Server,因此 NodeManager 仅依据原生引擎进程状态维护其生命周期,业务端口、健康探测、请求调度都只发生在主节点上。

---

## 【关键机制与数据】

**核心工作原理与数据流**

- **配置透传(单节点 PCP)**:用户配置 `prefill-context-parallel-size`,MindIE Motor 将其透传给 vLLM 引擎,无需额外编排逻辑。
- **跨节点 PCP 编排**:MindIE Motor 在 Controller ↔ NodeManager 之间插入完整的分布式协调流程,把 PCP 跨节点所需的 `nnodes` 个 Worker 进程拉起并接入同一通信组。
- **节点到 PCP rank 的映射**:`prefill-context-parallel-size` 表示**全局** PCP 并行度,MindIE Motor 自动计算每节点贡献的 PCP rank 数(`原文: MindIE Motor 会自动计算每节点贡献的 PCP rank 数`)。
- **KV cache 分片粒度**:`cp-kv-cache-interleave-size: 128`,原文为该参数的取值示例(原文字段为示例 JSON 给出),用于控制 PCP rank 间 KV cache 的分片大小。
- **主从节点标识**:`master-port: 7001`(原文示例值),为 PCP 主节点(`node_rank=0`)的通信端口;`master-addr` 由系统自动复用**首注册节点**的 IP。
- **从节点角色固化**:组内 `node_rank != 0` 的节点自动追加 `headless`,跳过 API 服务器启动。
- **DP 与 PCP 组装约束**:Controller 必须等待 `dp_size × nnodes` 个节点全部注册完成才进入组装阶段,组内按注册顺序从 0 开始编号 `node_rank`,组间通过 DP 维度叠加。
- **健康/调度可见性**:只有主节点(`node_rank=0`)暴露业务端口并参与健康探测和请求调度;从节点对上层不可见。
- **不兼容组合的错误路径**:`MooncakeConnectorV1` + `pd_separate` 会走 `SeparateCDPRouter`,其 KV transfer block 切分逻辑与 CP 不兼容,具体触发的两条断言:
  - `assert len(selected_p_cp_groups) == len(selected_d_cp_groups)`(Prefill 侧 CP group 数量不匹配)
  - `assert num_external_tokens == 0`(Decode 侧 `remote_block_ids` 为空但 `num_external_tokens > 0`,非 layerwise connector 的 block 分配与 CDP 调度不一致)

**性能数据**:原文未给出。

---

## 【表格解读】

### 表格 1:用户配置字段说明

| 字段 | 说明 |
|------|------|
| `nnodes` | PCP 组包含的节点数。每个 PCP 组内 `nnodes` 个节点协同完成跨节点上下文并行 |
| `master-port` | PCP 主节点(`node_rank=0`)的通信端口 |
| `prefill-context-parallel-size` | 全局 PCP 并行度。MindIE Motor 会自动计算每节点贡献的 PCP rank 数 |
| `cp-kv-cache-interleave-size` | CP KV cache 交错粒度,控制 PCP rank 间 KV cache 的分片大小 |

**逐行解读**:
- `nnodes` 决定了一个 PCP 组需要几个节点协同;Controller 层面以此为分组的最小单元,组装时按 `nnodes` 个节点一组的粒度切分注册队列。
- `master-port` 只在主节点(`node_rank=0`)上有意义,用于组内从节点定位主节点;从节点的端口不需要用户关心,由系统在 StartCmdMsg 中下发。
- `prefill-context-parallel-size` 是全局值,**不是**单节点值;MindIE Motor 隐式做"全局 ÷ 节点数"的拆分,把每节点 PCP rank 数注入到下层 vLLM。
- `cp-kv-cache-interleave-size` 决定 KV cache 在 PCP rank 间的交错粒度,粒度大小直接影响跨 rank KV 传输的带宽/延迟权衡(原文未给出推荐值的选取依据)。

### 表格 2:MindIE Motor 自动管理的 vLLM 原生参数

| 参数 | 自动管理方式 |
|------|-------------|
| `node-rank` | Controller 按 NodeManager 注册顺序分配(每 `nnodes` 个节点为一组,组内从 0 开始编号) |
| `master-addr` | 自动复用首注册节点(`node_rank=0`)的 IP 地址 |
| `headless` | `node_rank != 0` 的从节点自动追加,跳过 API 服务器启动 |
| `data-parallel-rank` | 由 Endpoint ID 决定 |
| `data-parallel-address` | 由 Controller 根据组装结果确定 |

**逐行解读**:
- `node-rank` 由 Controller 端**纯运行时推导**,完全依赖 NodeManager 注册到达顺序,组内 `0..nnodes-1` 编号,因此**节点启动顺序会直接影响谁被选为主节点**。
- `master-addr` 取自**首注册节点**的 IP,与 `node_rank=0` 节点对齐;此设计避免了用户在多节点场景手动配置 IP,但要求首注册节点必须稳定可见。
- `headless` 是从节点专用开关,意味着 Controller 下发的 StartCmdMsg 在主/从节点之间是**有差异的**(差异化下发),从节点只跑 Worker 进程、不暴露 API Server。
- `data-parallel-rank` 由 Endpoint ID 映射,体现"DP 维度叠加在 PCP 维度之上"的组合关系。
- `data-parallel-address` 由 Controller 在组装完成(知道所有节点位置)后才能确定,体现"先组装、后注入地址"的控制面时序。

### 表格 3:KV Connector × 调度模式 兼容性

| KV Connector | 调度模式 | 推荐? | 说明 |
|-------------|---------|:---:|------|
| `MooncakeConnectorV1` | `cpcd_separate` | ✅ 推荐 | 非 layerwise connector 配合 CPCD 调度模式,block 切分与 CP 场景兼容 |
| `MooncakeLayerwiseConnector` | `pd_separate` | ❌ 不推荐 | Layerwise 按层拆分 KV 传输,与 CP 场景存在兼容性问题 |

**逐行解读**:
- **推荐组合**:`MooncakeConnectorV1`(非 layerwise)+ `cpcd_separate`。原文逻辑链是:block 切分 → 与 CP group 数量对齐 → 与 CDP 调度一致 → 不触发断言失败。
- **不推荐组合**:`MooncakeLayerwiseConnector` + `pd_separate`。`pd_separate` 在 CP 场景下走 `SeparateCDPRouter`,该路由的 KV transfer block 切分假设与 layerwise 按层拆分模式冲突;即使把 `MooncakeConnectorV1` 错配成 `pd_separate`,也会触发相同断言(Prefill CP group 数不匹配 / Decode `num_external_tokens` 不一致),因此问题根源在于 **CP 场景只能走 CPCD 调度**。

---

## 【公式解读】

原文无公式。

---

## 【关联】

原文未提供文末内部链接。文档本身提及的**上下游关联**如下:

- **下游引擎:vLLM(及 vLLM Ascend)**——MindIE Motor 将 PCP 配置透传给 vLLM 引擎,跨节点 PCP 的底层原理参考 vLLM 社区文档(`https://docs.vllm.ai/projects/vllm-ascend-cn/zh-cn/v0.18.0/tutorials/features/long_sequence_context_parallel_multi_node.html`)。
- **CLI ↔ engine_config 映射**:`motor/node_manager/core/services/native_engine/backends/vllm/config.py` 中的 `VLLMConfig` 类维护 CLI 参数与 `engine_config` 键名的完整映射,本文档是面向用户的语义层,该模块是实现层。
- **Coordinator 调度层**:`motor_coordinator_config.scheduler_config.deploy_mode = cpcd_separate` 与 KV Connector 选择(`MooncakeConnectorV1`)是本文档强相关的另一配置面,涉及 `SeparateCDPRouter` 等内部路由组件。
- **组合特性**:**DP(数据并行)叠加 PCP**——本文档明确支持两者叠加,Controller 在组装阶段以 `dp_size × nnodes` 为总节点数收敛。
- **节点生命周期管理**:NodeManager 在跨节点 PCP 场景下需要根据 `nnodes`/`master-port` 注册,并按注册顺序触发差异化 StartCmdMsg,这是 NodeManager ↔ Controller 协议的一部分(原文未给出具体协议字段)。

---

## 【使用方法】

### 启用方式

**单节点 PCP**:在 `engine_config` 中设置 `prefill-context-parallel-size`,MindIE Motor 透传给 vLLM 即可。

**跨节点 PCP**:在 `engine_config` 中增加 `nnodes` 与 `master-port`,其余参数(`node-rank`、`master-addr`、`headless`、`data-parallel-rank`、`data-parallel-address`)由 MindIE Motor 自动管理。

### 配置示例(原文给出)

```json
{
  "motor_engine_prefill_config": {
    "engine_type": "vllm",
    "engine_config": {
      "model": "/mnt/weight/your_model",
      "tensor_parallel_size": 16,
      "data_parallel_size": 1,
      "prefill-context-parallel-size": 2,
      "cp-kv-cache-interleave-size": 128,
      "nnodes": 2,
      "master-port": 7001
    }
  }
}
```

### Coordinator 调度模式(原文给出)

```json
"motor_coordinator_config": {
    "scheduler_config": {
        "deploy_mode": "cpcd_separate"
    }
}
```

### DP × PCP 组合示例(原文描述)

- `data_parallel_size=4`、`prefill-context-parallel-size=2`、每节点 16 卡时,总共需要 `4 × 2 = 8` 个节点;Controller 等待 8 个节点全部注册后再统一组装与下发。
- 用户需自行确保 DP、TP、PCP 的总 rank 数与节点数匹配;原文未给出具体校验逻辑。

### CLI ↔ engine_config 映射

CLI 参数与 `engine_config` 键名的完整映射由 `motor/node_manager/core/services/native_engine/backends/vllm/config.py` 中的 `VLLMConfig` 维护(原文指向该实现文件,未给出具体映射表)。
