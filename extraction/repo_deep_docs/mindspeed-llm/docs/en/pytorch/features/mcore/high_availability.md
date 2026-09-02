# Ascend High Availability

> 仓 `mindspeed-llm` · 路径 `docs/en/pytorch/features/mcore/high_availability.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-llm/docs/en/pytorch/features/mcore/high_availability.md

# Ascend High Availability 文档深度解读

## 【定位】
本文档介绍昇腾 LLM 分布式训练框架中基于「Replica Optimizer」的高可用（High Availability, HA）能力体系，覆盖 TTP 兜底检查点、UCE 步级重算、弹性训练三类故障恢复机制，旨在千卡以上大规模集群中降低训练宕机带来的机时损失。

---

## 【技术要点】

1. **核心思路：复制式优化器（Replica Optimizer）**——在 Megatron 原生 ZeRO-1 分布式优化器基础上，将每个 DP 组一分为二成为两个 replica DP 组，优化器状态在两组间均匀分片并互为副本，用更高显存开销换取故障恢复能力。
2. **使用门槛与规模建议**：建议在 **1,000 设备以上** 大规模集群使用，且 3D 并行（P+T+D）下 **DP 维度 ≥ 2**，否则故障后无法保留完整 optimizer state。
3. **三大子能力**：(a) Try-To-Persist（TTP）Checkpoint——故障后基于 optimizer 中间态生成 last-gasp checkpoint，恢复到故障前一刻；(b) UCE Step-Level Recomputation——NPU 内存不可纠正错误（UCE）实时检测后，借助 optimizer state 副本在线修复故障设备；(c) Elastic Training——无空闲资源时收缩部分 DP 域继续训练，资源恢复后扩回原规模。
4. **弹性训练的范围限制**：当前仅支持**数据并行粒度**的扩缩，不支持张量并行、流水并行维度上的弹性；且一次只能缩一次，扩容只能扩回原大小。
5. **五大启动参数**：高可用全局开关 `--enable-high-availability`、HBM 故障修复 `--enable-hbmfault-repair`、进程级重启（air-refueling）`--enable-worker-reboot`、禁用副本优化器回退到 checkpoint 的 `--distributed-optimizer-no-replica`、弹性训练 `--enable-elastic-training`。
6. **四档环境变量快捷配置**：`HIGH_AVAILABILITY=dump/retry/recover/elastic-training` 分别对应上述参数的组合包，环境变量优先级高于 CLI 参数。

---

## 【关键机制与数据】

**Replica Optimizer 工作原理（原文）：**
Megatron 原生分布式优化器把 optimizer state 均匀分片到 DP 组内各卡上以节省显存。Replica Optimizer 在此基础上把 DP 组拆成两个 replica DP 组，optimizer state 在两组间**均匀分片 + 互相备份**，因此机制层同时支撑 TTP 与 UCE 修复两类场景。

**三大特性数据流（原文）：**
- **TTP**：训练故障 → 检查 optimizer 中间数据完整性与一致性 → 生成 last-gasp checkpoint → 重启训练时恢复到故障前一刻，**减少迭代损失**。
- **UCE**：NPU 内存实时检测 UCE → 通过 optimizer state 副本机制**在线修复受影响设备** → 恢复训练，**最小化训练损失**。
- **Elastic Training**：故障后无空闲资源 → 按 DP 粒度**收缩部分 DP 域**继续训练 → 资源恢复后**扩回原规模**，全程依赖 optimizer state 副本机制提供数据完整性保障。

**显存开销对比（原文）：** 详见下方表格解读，Replica Optimizer 相比 Distributed Optimizer 显存占用翻倍。

**Checkpoint 优化（原文）：** 当 `enable-high-availability` 启用且环境安装了 MindIO ACP SDK 时，启用 `mindio_acp` 提供的一级异步 checkpoint 存读优化。

---

## 【表格解读】

> 原文表格**逐字还原**：

|                                  | Non-distributed Optimizer | Distributed Optimizer | Replica Optimizer |
|----------------------------------|---------------------------|-----------------------|-------------------|
| fp16/bf16 params, fp16/bf16 grads | 20                        | 4 + 16/d              | 4 + 32/d          |
| fp16/bf16 params, fp32 grads      | 18                        | 6 + 12/d              | 6 + 24/d          |

**逐行解读：**

- **行 1：fp16/bf16 精度参数 + fp16/bf16 精度梯度场景**
  - Non-distributed Optimizer：固定 **20**（每卡都保存完整参数 + 梯度）
  - Distributed Optimizer：**4 + 16/d**，其中 d 为 DP 大小
  - Replica Optimizer：**4 + 32/d**——梯度分片项的分子从 16 翻倍到 32，体现「在 replica DP 组中既保留自身分片又保留对端副本」的代价

- **行 2：fp16/bf16 精度参数 + fp32 精度梯度场景**
  - Non-distributed Optimizer：固定 **18**
  - Distributed Optimizer：**6 + 12/d**——相比 fp16 梯度场景，梯度基数项减少（12 vs 16）但固定开销增加（6 vs 4），反映 fp32 grad 需要 master 权重相关的固定存储
  - Replica Optimizer：**6 + 24/d**——同样梯度分片项翻倍（12 → 24）

- **整体趋势**：Replica Optimizer 相对 Distributed Optimizer 的额外开销主要落在「梯度分片项翻倍」，固定项（4 或 6）保持不变；分母 d 越大，每卡绝对额外开销越小，但相对成本仍存在，这正是文档建议 **d ≥ 2** 且**千卡以上**才启用的显存经济学依据。

---

## 【公式解读】

原文未给出独立的 LaTeX 公式，但表格中的"4 + 16/d"、"4 + 32/d"、"6 + 12/d"、"6 + 24/d" 是显存占用的代数表达，逐项解释其符号含义：

- **分子 4 / 6**：参数自身及与 optimizer 相关的固定项（与 d 无关的常数项），第一行 4 对应 fp16/bf16 梯度场景，第二行 6 对应 fp32 梯度场景（多出的 2 来自 fp32 master param 的固定开销）。
- **分子 16 / 12 / 32 / 24**：与梯度/optimizer state 相关的分片分子。
  - 16 → Distributed Optimizer 在 fp16/bf16 grads 场景下梯度分片的总份数
  - 32 → Replica Optimizer 下 16 × 2（梯度分片 + 副本）
  - 12 → fp32 grads 场景下 Distributed Optimizer 梯度分片总份数（与 fp16 场景数值不同的原因是 fp32 占用更高导致基数项重新分配）
  - 24 → Replica Optimizer 在 fp32 grads 场景下的 12 × 2
- **分母 d**：数据并行（DP）大小，表示分片份数；d 越大，每卡分到的梯度/optimizer 越少，公式值越小。
- **整体含义**：整个表达式描述「单卡显存占用 = 固定开销 + 可分片开销 / DP 大小」，是 ZeRO-1 类内存分片的标准代数写法。Replica Optimizer 用分子翻倍换取故障恢复能力，是「显存换可用性」的核心权衡。

---

## 【关联】

1. **上游基础**：本文档建立在 Megatron 原生 **Distributed Optimizer**（ZeRO-1 思想）之上，将 DP 组一分为二的拆分思想继承自该机制。
2. **配套组件**：`mindio_ttp`（MindIO TTP 故障恢复加速包，需独立下载安装，参见文末 Ascend Community 链接）与 `mindio_acp`（MindIO ACP SDK，提供异步 checkpoint 优化），二者均非 mindspeed-llm 内置，需在环境中额外安装。
3. **下游配套框架**：**MindCluster**——华为自研的集群级高可用框架，与本文档的各开关协同工作才能完成进程级重启（air-refueling）、弹性扩缩等端到端恢复动作。完整功能集需参阅官方 [MindCluster Guide](https://www.hiascend.com/software/mindcluster)。
4. **并行维度的耦合关系**：本特性与**张量并行（T）、流水并行（P）、MoE（dense/sparse 层 DP）、长序列并行（dp_cp_size）** 均有 DP 维度的耦合约束，并非独立特性。
5. **文末内部链接信息**：文档明确指引到 [MindIO TTP Constraints and Limitations - Ascend Community](https://gitcode.com/Ascend/mind-cluster/blob/branch_v26.0.0/docs/zh/scheduling/fault_recovery_acceleration/02_installation_and_deployment.md) 获取更详细的部署约束信息。

---

## 【使用方法】

**前置准备（原文）：**
- 安装 MindIO `mindio_ttp` wheel 包（需从 Ascend Community 链接下载）

**启动参数（原文）：**

| 参数 | 作用 |
|------|------|
| `--enable-high-availability` | 高可用全局开关 + TTP checkpoint；要求全局至少一份完整 optimizer 数据副本 |
| `--enable-hbmfault-repair` | 启用片上内存故障步级重算；要求全局至少存在故障设备的 1 个副本设备 |
| `--enable-worker-reboot` | 启用 air-refueling（空中加油）进程级重启修复；要求非故障节点上至少存在一份完整 optimizer 数据 |
| `--distributed-optimizer-no-replica` | 回退路径——禁用副本，使用 checkpoint 文件做重算和 air-refueling 修复；要求故障时存在 checkpoint |
| `--enable-elastic-training` | 启用弹性训练；移除故障设备对应 DP 域节点；要求非故障节点上至少存在一份完整 optimizer 数据 |

**环境变量快捷配置（原文，优先级高于 CLI）：**

| 环境变量 | 等价启用项 |
|----------|------------|
| `export HIGH_AVAILABILITY=dump` | `--enable-high-availability` |
| `export HIGH_AVAILABILITY=retry` | `--enable-high-availability` + `--enable-hbmfault-repair` |
| `export HIGH_AVAILABILITY=recover` | `--enable-high-availability` + `--enable-worker-reboot` |
| `export HIGH_AVAILABILITY=elastic-training` | `--enable-high-availability` + `--enable-elastic-training` |

**使用约束（原文）：**
- 3D 并行（P+T+D）下 **DP 维度 > 1**；MoE 场景下 dense 层与 sparse 层的 DP 维度均 > 1；长序列并行下 `dp_cp_size` > 1。
- 弹性训练额外约束：仅支持 `enable-high-availability` 与 `use-distributed-optimizer`；不支持 `use-custom-fsdp` 与 `reuse-fp32-param`；仅支持 DP/TP/PP 三种并行；一次只能缩一次，扩容仅支持扩回原大小。

## 图文联合解读

- `grad_buffer_sharding.png`: **图解**：

1) **画面内容**：4个dp rank（0-3）垂直分列，三层结构——上层"model"含各rank的grad/grad buf，中层"grad buffer sharding"横向拼接不同色块（绿/黄/蓝/红）表示梯度分片，下层"optim shards"为本地优化器分片。带编号步骤[1]-[8]串联"前向→分片buffer→本地optim step→all-gather参数"完整数据流。

2) **技术结论**：Replica Optimizer将数据并行组划分为多个replica组，组内做ZeRO式优化器分片、组间冗余备份，以片外内存换故障恢复能力。

3) **与文档关系**：支撑"分布式优化器节省显存"的核心论点，是TTP故障前最后检查点可基于该分片状态快速恢复的实现前提。
- `replica_optimizer.png`: **图文联合解读：**

1) **图示内容**：上半部展示传统分布式优化器的梯度分片方案——4个参数(Param0-3)的梯度分别由4个dp rank独立持有，互不冗余；下半部展示副本优化器方案，DP组拆分为两组副本(dp_rank0+dp_rank2为一组，dp_rank1+dp_rank3为一组)，每个参数的梯度状态在两组间各保存一份副本。

2) **技术结论**：通过将数据并行组一分为二，参数状态在副本组内交叉备份，实现冗余存储，代价是片上显存占用增加。

3) **与文档关系**：该图直接对应文档"Use Cases"段落——印证MindIO将DP组拆成两个副本DP组以备份optimizer states的设计思路，为"建议在≥1000卡大集群使用以降低故障机时损失"以及配合TTP检查点/UCE重计算实现高可用提供原理支撑。
