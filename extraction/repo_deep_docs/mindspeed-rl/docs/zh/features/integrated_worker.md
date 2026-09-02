# 共卡机制介绍

> 仓 `mindspeed-rl` · 路径 `docs/zh/features/integrated_worker.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-rl/docs/zh/features/integrated_worker.md

# 深度解读：mindspeed-rl 共卡机制 (integrated_worker)

## 【定位】

本文档系统介绍了 MindSpeed RL 中"共卡"机制的两种部署形态——**全共卡部署（Full Co-card Deployment）**与**训推共卡（Training-Inference Co-card）**，核心目的是在有限 NPU 资源条件下，通过分时复用同一批机器与显存来支持强化学习后训练（RLHF）流程，并专门解决大规模 MoE 模型在 Actor 角色下"训-推"两态的资源争抢问题。

---

## 【技术要点】

1. **全共卡分时复用机制**：Actor、Reference 等 worker 通过分时复用同一批 NPU 资源完成交替计算；每个任务执行时仅将必要数据加载到显存，任务结束后立即将数据卸载到 CPU 侧 Host 内存，以节省显存。
2. **统一 Actor 配置回收**：在全共卡模式下，`ref_config` 与 `reward_config` 会被框架**自动忽略**，统一复用 `actor_config`；`actor_resource` 代表方案占用的**总 NPU 数量**，`reference_resource`、`reward_resource` 等不应被设置。
3. **训推共卡 Actor 双形态**：Actor 在同一角色内同时存在**训练态**（基于 Megatron，含 `model` + `optimizer`）与**推理态**（基于 vLLM，即 `inference_model`），由 `sharding_manager` 统一调度两态切换。
4. **动态权重 + 并行策略转换**：通过通信优化算法降低训推切换时的权重同步时延，并支持将**专家并行（EP）在线转换为张量并行（TP）**，以避免大规模 MoE 模型（原文以 DeepSeek V3 为例，权重约 1.3TB）出现 OOM。
5. **内存调度优化**：推理阶段将优化器状态、梯度、训练参数从 NPU 显存**卸载至 Host 内存**，为推理 KV Cache 让出显存；训练阶段再回加载，三类数据（`offload_train_optimizer` / `offload_train_grad` / `offload_train_param`）可独立开关。
6. **三阶段串行无缝切换**：基于 Megatron + vLLM 框架串联 Actor 的 `generate_sequences` → `compute_log_prob` → `update` 三阶段，消除模型级空泡、提升硬件利用率。

---

## 【关键机制与数据】

**工作原理（三阶段切换流程）**：

- **训练态 → 推理态**（原文："从训练态切换到推理态时，需要根据推理态的切分从训练权重构建出相应的推理权重，并将训练态的模型权重、优化器和梯度从显存上进行卸载，为推理时的 KV Cache 留出显存空间"）：核心是 *权重切分重组 + 训练态三件套卸载*。
- **推理态 → 训练态**（原文："从推理态切换到训练态时，则只需将推理态的权重和 KV Cache 卸载，并重新加载回训练态的权重、优化器和梯度"）：核心是 *卸载推理 KV Cache + 重新挂载训练三件套*。

**资源利用视角**（原文："如果采用分离方案进行 Actor 部署……即使采用了 MBS 间异步方案提升利用率，分离式部署的资源需求量也会远大于共卡部署方案"）：共卡方案相对分离方案在资源需求量上具有显著优势，尤其在 MoE 模型场景下"显著降低卡数需求"。

**关键数字/事实**（原文）：
- DeepSeek V3 权重规模：**1.3TB**（用于说明为何需要 EP↔TP 切分以避免 OOM）。
- 训推共卡框架构成：**Megatron（训练） + vLLM（推理）**。
- 卸载开关共 **3 个**：optimizer / grad / param，可独立设置为 `true`。
- 全共卡开关：**`use_integrated_worker: true`** + **`blocking: true`**。

**注**：原文未给出训推切换耗时、吞吐量提升倍数、显存峰值降幅等量化性能数据，本文不臆造。

---

## 【表格解读】

**原文无表格**。

> 补充说明：原文仅以 YAML 代码块形式给出了"全共卡配置示例"与"训推共卡切分配置示例"，并非 markdown 表格；其配置项已在【技术要点】与【使用方法】中按原文逐字保留并解释。

---

## 【公式解读】

**原文无公式**。

---

## 【关联】

- **算法层**：本文档围绕 GRPO、PPO 等 RLHF 算法的 Actor 部署展开；训推共卡的"三阶段串行"（`generate_sequences` / `compute_log_prob` / `update`）即为 GRPO 训练流程中的关键环节。
- **基础框架层**：
  - **Megatron**：负责训练态的 `model`、`optimizer` 实现；
  - **vLLM**：负责推理态的 `inference_model` 实现；
  - 两者通过 `sharding_manager` 协同。
- **类继承结构**：`ActorHybridWorker` 继承自 `BaseWorker`，作为"角色（role）"参与 GRPO 流程，承担 Actor 在 RLHF 中的全部功能。
- **配置示例引用**：以 `grpo_qwen25_7b_A3.yaml` 为范例，演示训练态 TP/PP/EP 与推理态 infer_TP/infer_PP/infer_EP 的独立切分配置。
- **目标模型族**：明确以 **MoE 大模型（DeepSeek V3）** 作为典型场景，论证 EP↔TP 切分转换的必要性。
- **相对方案**：与"分离式 Actor 部署"（训/推在不同物理资源）形成对比，论证共卡方案在资源受限场景下的优势。

---

## 【使用方法】

### 一、全共卡部署启用

在 `rl_config` 下设置：

```yaml
rl_config:
  use_integrated_worker: true   # 开启全共卡
  blocking: true                # 全共卡下应开启 blocking
  actor_forward_micro_batch_size: 8   # 可选：单独指定 actor log_p 计算的 micro batch size；不配则复用 actor_config 中的 micro_batch_size
  ref_forward_micro_batch_size: 8     # 可选：单独指定 reference log_p 计算的 micro batch size；不配则复用 actor_config 中的 micro_batch_size
  integrated_mode_config:
    ref_model_load_path: "path_to_ref_model"  # 可选：断点续训时单独加载 ref 权重；不配则 ref 与 actor 共享权重
```

**约束**（原文明确给出）：
- 全共卡下**不应给出** `ref_config` 与 `reward_config`（框架会自动忽略，复用 `actor_config`）。
- `actor_resource` 解读为方案占用的**总 NPU 数量**；**不应设置** `reference_resource`、`reward_resource`。

### 二、训推共卡 Actor 配置

训推共卡目前由框架自动启用（原文："当前框架会自动启用训推共卡式 Actor"），用户可在 yaml 中**分别配置训练态与推理态的切分策略**及**训练态数据卸载开关**：

```yaml
actor_config:
  tensor_model_parallel_size: 4        # 训练态 TP 切分
  pipeline_model_parallel_size: 1      # 训练态 PP 切分
  expert_model_parallel_size: 1        # 训练态 EP 切分

generate_config:
  infer_tensor_parallel_size: 4        # 推理态 TP 切分
  infer_pipeline_parallel_size: 1      # 推理态 PP 切分
  infer_expert_parallel_size: 1        # 推理态 EP 切分

  offload_train_optimizer: true        # 推理时是否卸载训练态优化器
  offload_train_grad: true             # 推理时是否卸载训练态梯度
  offload_train_param: true            # 推理时是否卸载训练态权重
```

**使用建议**（按原文逻辑推导，非臆造）：
- MoE 大模型（典型如 DeepSeek V3）建议开启全部三类卸载（`offload_train_optimizer` / `offload_train_grad` / `offload_train_param` 均为 `true`），为推理 KV Cache 让出显存。
- 训练态与推理态可采用**不同并行策略**（如训练态"大 TP/PP/小 EP"，推理态"小 TP/PP/大 EP"），由 `sharding_manager` 在线完成 EP↔TP 转换。

### 三、未涉及内容

- 文档未给出**集群拓扑要求**、**NPU 卡型最低要求**、**多机多卡下 actor_resource 与单机卡数的关系换算**等运维细节，原文未涉及。
- 文档未给出具体的**性能基准数字**（如吞吐量提升、显存节省比例、切换耗时），原文未涉及。

## 图文联合解读

- `pipeline.png`: **图示内容**：纵向流水线展示全共卡方案的五阶段显存调度流程——① Actor 推理态（onload 推理参数+KV cache、resharding，offload 训练参数）→ ② Ref 推理态 → ③ Reward 推理态 → ④ Actor 前向态（onload 训练参数）→ ⑤ Actor 训练态（onload 优化器+梯度），每阶段伴随 enter/exit_infer/forward/train_mode 切换与参数 onload/offload 操作。

**技术结论**：通过分时复用同一批 NPU、按需加载必要数据并卸载非必要数据，可在有限显存下串联 Actor/Reference/Reward 多个推理任务与 Actor 训练任务。

**与文档关系**：直接呼应"全共卡部署"中"仅将必要数据加载到显存、任务结束后卸载到 CPU 内存"的核心论点，并印证 ref/reward_config 被复用忽略、actor_resource 即为总 NPU 数量的设计。
- `background.jpg`: **1) 图示内容**：左侧"分离式部署"将Actor Gen(4卡)与Actor Train(4卡)分占两批卡，中间夹Reward/Reference，出现大量"空泡"，并通过"训推权重通信"箭头跨卡同步；右侧"共卡式部署"仅用4卡依次执行Actor Gen→Actor Fwd→Actor Train，靠"训推并行策略切换"衔接，无空泡，下方绿色框标注"计算资源节省"。

**2) 技术结论**：分离方案因双倍占卡+串行等待导致气泡多、需跨卡权重同步；共卡方案通过分时复用同一资源消除空闲，以并行策略切换替代权重通信，显著节约算力。

**3) 与文档论点关系**：图直接佐证文档论点——训推分离资源利用率低，共卡方案在资源受限时是高效部署方式。
- `actor_hybrid_worker.jpg`: **图文联合解读：**

图示**ActorHybridWorker**架构，含三大模块：训练引擎(PP0–PP3×TP0/1)→分片管理器(PB0–PB3 参数缓冲)→推理引擎(TP0，含 Infer Model)。箭头表示训练态参数经 PB 中转，再以"Model Structure/Tensor Reference"回流推理引擎，实现训推权重动态切换。

**论证结论**：训推可分时复用同一批 NPU，权重经 Param Buffer 桥接共享，避免分离部署的互等与资源浪费。

**与文档关系**：佐证"训推共卡"方案可行性，与正文"Actor 需在训练/推理态切换且共卡更高效"论点直接呼应。
- `sharding_process.jpg`: 图示展示NPU0/NPU1上训练态(PP=2,含权重/优化器/梯度)与推理态(PP=1,含权重/KV-cache)的分时复用：①优化器与梯度Offload节省显存，②PP并行策略训推间动态切换，③推理阶段分配vLLM KV-cache。论证训推共卡通过动态切分并行策略与显存调度，使Actor在同一集群资源上高效协同训练与推理，正对应文档"训推共卡"方案所提的动态权重更新与并行策略调整等关键技术。
