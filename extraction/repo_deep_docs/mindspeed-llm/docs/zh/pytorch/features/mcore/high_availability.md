# 昇腾高可用性

> 仓 `mindspeed-llm` · 路径 `docs/zh/pytorch/features/mcore/high_availability.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-llm/docs/zh/pytorch/features/mcore/high_availability.md

# 昇腾高可用性 Feature 文档深度解读

---

## 【定位】

本篇文档描述 **昇腾 NPU 平台上基于「副本优化器 (Replica Optimizer)」设计的大规模分布式训练高可用能力**——当训练集群规模达千卡量级后，任何单卡故障都会造成大量机时损失，本特性通过将分布式优化器的状态数据在数据并行组内做"双副本"备份，使 TTP 临终遗言、UCE 卡内存不可修复错误的 Step 级重计算、以及 Data Parallel 粒度的弹性缩容/扩容成为可能，从而把故障恢复从"丢弃当前迭代、退回上一个 checkpoint"推进到"在线修复或在线缩容继续训练"。

---

## 【技术要点】

1. **副本优化器 (Replica Optimizer) 作为底层机制**：相比 Megatron 原生分布式优化器（按数据并行维度均匀切分优化器状态），副本优化器将数据并行组进一步切成两个副本 DP 组，优化器状态在副本组之间互为备份——这是 TTP、UCE、弹性训练三种高可用能力共同依赖的数据基础。

2. **TTP 临终遗言**：故障发生后校验优化器中间状态完整性与一致性，生成"临终 checkpoint"，恢复时直接恢复到故障前一刻状态——`原文:`"生成一次临终 checkpoint 数据，恢复训练时能够通过该 checkpoint 恢复到故障前一刻的状态，减少故障造成的训练迭代损失"。

3. **UCE Step 级重计算**：利用昇腾 NPU 对 HBM 不可修复错误的实时检测能力，配合副本机制在线修复故障卡并继续训练——`原文:`"检测到 UCE 故障后，基于优化器状态副本机制并完成故障卡的在线修复并继续训练"。

4. **弹性训练 (Elastic Training)**：当无可替换空闲资源时按 DP 域缩掉部分节点继续训练，有空闲资源时再扩容回原规模。`原文:`"当前阶段仅支持 Data Parallel 级别的弹性训练，即按照 Data Parallel 粒度缩掉部分数据并行域进行扩容或缩容"。

5. **存算代价（原文明确给出）**：副本优化器相比分布式优化器内存占用增加，详见下表（其中 `d` 为 Data Parallel Size）。

6. **总开关分层设计**：通过 `--enable-high-availability` 总开关 + `--enable-hbmfault-repair` / `--enable-worker-reboot` / `--enable-elastic-training` / `--distributed-optimizer-no-replica` 四个子开关组合不同高可用模式；并提供 `HIGH_AVAILABILITY` 环境变量以兼容 mindx 多组件场景，`原文:`"环境变量优先级高于 args，设置环境变量会被优先使用"。

---

## 【关键机制与数据】

**整体数据流**：训练梯度经 gradient buffer 进入分布式优化器 → 原生方案中优化器状态按 DP Size 切分（每张卡只持有 1/d 份）→ 副本优化器把数据并行组再切为两个"副本 DP 组"，每张卡仍持有部分优化器状态，但同一份状态在两个副本组中各有一份完整拷贝 → 任一卡故障后，未故障卡上仍持有故障卡所需优化器状态 → TTP 可据此生成临终 ckpt，UCE 可据此在线修复，弹性训练可据此剔除故障 DP 域而不丢失优化器全局完整性。

**关键性能/代价数据（原文表格，逐字见下节）**：
- 原生分布式优化器 fp16/bf16 参数 + 梯度：每卡占 `4 + 16/d` 单位
- 副本优化器同等情况下：每卡占 `4 + 32/d` 单位——即优化器状态占用 **翻倍**（系数从 `16/d` 升到 `32/d`），而参数本体（4 单位）保持不变
- 第二行 (fp32 grads) 同理：优化器状态系数从 `12/d` 升到 `24/d`

**关键工程约束（原文显式）**：
- Data Parallel Size 必须大于 1；MoE 场景下稠密层与稀疏层 DP Size 均需大于 1；长序列并行场景下 `dp_cp_size > 1`
- 推荐 **千卡及以上** 集群使用（`原文:`"推荐千卡及以上的大规模集群使用本特性，减少故障引起的机时损失"）
- `原文:`"MindSpeed-llm 的高可用特性仅针对基础模型和基础训练特性进行适配……暂未进行全量训练特性兼容"
- 弹性训练额外约束："当前仅支持开启 `enable-high-availability`、`use-distributed-optimizer`"；"当前仅支持不开启 `use-custom-fsdp`、`reuse-fp32-param` 的场景"；"当前仅支持 `Data Parallel`、`Tensor Parallel`、`Pipeline Parallel` 并行"；"当前缩容后不可再次缩容，扩容仅支持直接扩容回原有规模"
- 弹性训练恢复条件："未故障节点中至少存在一份完整的优化器数据"

---

## 【表格解读】

### 表格 1：副本优化器相对内存占用对比（原文逐字还原）

|                                  | Non-distributed optim | Distributed optim | Replica optim |
|----------------------------------|-----------------------|-------------------|---------------|
| fp16/bf16 param, fp16/bf16 grads | 20                    | 4 + 16/d          | 4 + 32/d      |
| fp16/bf16 param, fp32 grads      | 18                    | 6 + 12/d          | 6 + 24/d      |

**逐行解读**：

**表头三列含义**：
- `Non-distributed optim`：非分布式优化器（每张卡都持有完整的优化器状态、参数与梯度），用于给出"满量"的对照基线。
- `Distributed optim`：Megatron 原生分布式优化器，参数与梯度按 DP 维度切分。
- `Replica optim`：本特性引入的副本优化器，是高可用能力的数据基础。

**第一行（fp16/bf16 param, fp16/bf16 grads，纯低精度场景）**：
- `Non-distributed optim = 20`：每张卡均持有完整 fp16 参数 + 完整 fp16 梯度 + 完整 fp32 优化器状态（Adam 的 m 与 v）。
- `Distributed optim = 4 + 16/d`：参数本体在每张卡仍按 TP/PP 维度切但因 DP 内不切每卡仍持有完整副本（4 单位）；其余 16 单位（梯度 + 优化器状态）按 DP Size `d` 均分。
- `Replica optim = 4 + 32/d`：参数本体不变（4 单位），但 32/d 体现"梯度/优化器状态总量翻倍"——其中 16/d 仍是正常的 DP 切分，另外 16/d 是副本带来的冗余拷贝。**这正是高可用的内存代价来源**：`d` 越大，新增的副本分摊越显著；当 `d=8` 时分布式为 `4+2=6`，副本为 `4+4=8`，差 2 单位；当 `d=64` 时分布式为 `4+0.25=4.25`，副本为 `4+0.5=4.5`，差仅 0.25 单位——这也解释了为什么 `原文` 推荐"千卡及以上"集群使用，规模越大副本冗余越被摊薄。

**第二行（fp16/bf16 param, fp32 grads，混合精度梯度保留 fp32 场景）**：
- `Non-distributed optim = 18`：相比第一行少了 2 单位，因为 fp32 梯度相比 fp16 梯度内存占用更少。
- `Distributed optim = 6 + 12/d`：参数本体升到 6 单位（多了 fp32 梯度本体），剩余 12 单位按 `d` 切分。
- `Replica optim = 6 + 24/d`：fp32 梯度部分也参与副本切分（系数从 12/d 翻倍到 24/d）。

**总体结论（综合两行）**：副本优化器的内存增量严格发生在"梯度 + 优化器状态"这一项上（约翻倍），而**参数本体内存不受影响**——这一点对理解哪些层会感受到内存压力、以及为什么需要在 Data Parallel Size 大于 1 的前提下才划算，非常关键。

---

## 【公式解读】

原文未给出独立公式段落，但表格中的内存占用表达式本身即是一组形式化公式，逐字保留原式并解释符号含义如下：

### 公式组（来自原文表格逐字）

```
Non-distributed optim (fp16/bf16 param, fp16/bf16 grads)  = 20
Distributed optim   (fp16/bf16 param, fp16/bf16 grads)    = 4 + 16/d
Replica optim       (fp16/bf16 param, fp16/bf16 grads)    = 4 + 32/d

Non-distributed optim (fp16/bf16 param, fp32 grads)       = 18
Distributed optim   (fp16/bf16 param, fp32 grads)         = 6 + 12/d
Replica optim       (fp16/bf16 param, fp32 grads)         = 6 + 24/d
```

**符号含义与作用**：

- `20`、`18`、`4`、`6` 等常数项：**参数本体 + 在每张卡必须保留的、不按 DP 切分的那部分状态**。在第一行（fp16 梯度）下"4 单位"对应 fp16/bf16 参数 + 必需的 fp32 master 参数副本；在第二行（fp32 梯度）下"6 单位"则再叠加 fp32 梯度本体。
- `16/d`、`12/d`：在原生分布式优化器下，**梯度与优化器状态 (Adam 的 m、v、fp32 master) 在 DP Size = d 时被均分到每张卡的内存占用**。`d` 越大，分到每张卡的部分越小，整体显存越省。
- `32/d`、`24/d`：副本优化器下同样的梯度与优化器状态总量变为原来的 **2 倍**，因此分母仍是 `d`、但系数翻倍——这正是"副本"的代价。
- `d`：Data Parallel Size（数据并行组大小），文档下文明确要求 `Data Parallel Size > 1` 才能启用本特性，正是因为 `d=1` 时 `16/d` 与 `32/d` 退化为 16 vs 32，副本冗余 100% 而毫无收益。

**公式揭示的关键关系**：`Replica − Distributed = 16/d`（第一行）或 `12/d`（第二行），即**启用副本优化器增加的内存恰好等于"未启用时优化器状态量本身"**——副本优化器为高可用付出的代价与 `1/d` 成正比，规模越大越划算。

---

## 【关联】

本特性不是孤立的开关，而是与昇腾软件栈多个层级紧密耦合：

1. **Megatron 原生分布式优化器（Distributed Optimizer）**：`原文:`"Megatron原生的分布式优化器数据流及工作原理如下图"——副本优化器是 Megatron 分布式优化器的演进形态，是其上层而非替代。
2. **MindCluster 框架**：`原文:`"若需使用完整的高可用特性请参考 MindCluster 官方指导文档"——本特性是 MindCluster 故障恢复能力在 MindSpeed-LLM 中的训练侧实现，MindCluster 负责集群调度、故障检测与节点级操作。
3. **MindIO TTP**：`原文:` 给出 mindio_ttp 的下载地址，并标注 MindIO TTP 约束限制链接；功能上"高可用必须兼容的特性清单"由 MindIO TTP 给出约束边界。
4. **MindIO ACP SDK**：`原文:`"若环境上安装了 MindIO ACP SDK ，则会使用 mindio_acp 的一级异步 checkpoint 保存与加载优化"——开 `enable-high-availability` 后会自动选用 ACP 一级异步 checkpoint 优化保存/加载性能，与 TTP 临终 checkpoint 写入效率直接相关。
5. **PTD 三维并行（P × T × D）**：`原文:` 约束条款明确要求"在 PTD 切分时保障 Data Parallel Size 大于1"，并对 MoE 下的稠密/稀疏层 DP Size、长序列并行下 `dp_cp_size` 提出了额外约束——本特性深度耦合于并行切分策略。
6. **昇腾 NPU UCE 硬件检测能力**：`原文:`"昇腾芯片支持 NPU 卡内存发生 UCE 故障（内存不可修复）的实时检测"—— Step 级重计算依赖昇腾芯片层的 UCE 检测机制，是软硬协同的特性。
7. **上游开关（混精、梯度 overlap、checkpoint 格式、分布式优化器本身）**：`原文:` 列出的"高可用必须兼容的特性清单"——`--bf16`、`--overlap-grad-reduce`、`--load`、`--save`、`--ckpt-format torch`、`--use-distributed-optimizer`——表明本特性的可用性受上游训练配置的反向约束。

---

## 【使用方法】

### 软件包安装

- 功能以 whl 包形式提供，下载地址见原文：`mindio_ttp 下载地址：[MindIO TTP 下载软件包-昇腾社区](https://gitcode.com/Ascend/mind-cluster/blob/branch_v26.0.0/docs/zh/scheduling/fault_recovery_acceleration/02_installation_and_deployment.md#%E5%87%86%E5%A4%87%E8%BD%AF%E4%BB%B6%E5%8C%85)`
- 完整高可用特性需配合 MindCluster 组件使用，参考：`https://www.hiascend.com/software/mindcluster`
- 若环境中安装了 MindIO ACP SDK，会自动启用一级异步 checkpoint 保存与加载优化

### 启动脚本命令行参数（原文逐字）

| 参数 | 作用 | 修复时对优化器状态的要求 |
|---|---|---|
| `--enable-high-availability` | 高可用总开关，同时使能 TTP 临终遗言功能 | 保存 checkpoint 时要求全局至少存在一份完整的优化器数据 |
| `--enable-hbmfault-repair` | 使能片上内存故障的 Step 级重计算 | 全局至少存在一个故障卡的副本卡 |
| `--enable-worker-reboot` | 使能"空中加油"（hot swap）功能，配合 MindCluster 组件使用 | 未故障节点中至少存在一份完整的优化器数据 |
| `--distributed-optimizer-no-replica` | 不使用副本优化器而改用 CKPT 文件进行重计算和空中加油修复 | 故障时需存在 CKPT 文件 |
| `--enable-elastic-training` | 使能弹性训练功能，配合 MindCluster 组件使用 | 未故障节点中至少存在一份完整的优化器数据 |

### 环境变量（优先级高于 args，原文逐字）

```bash
export HIGH_AVAILABILITY=dump             # 启用 --enable-high-availability
export HIGH_AVAILABILITY=retry            # 启用 --enable-high-availability --enable-hbmfault-repair
export HIGH_AVAILABILITY=recover          # 启用 --enable-high-availability --enable-worker-reboot
export HIGH_AVAILABILITY=elastic-training # 启用 --enable-high-availability --enable-elastic-training
```

### 前置使用约束（必须满足）

- 训练并行策略需保证 **Data Parallel Size > 1**；MoE 场景下稠密层与稀疏层 DP Size 均需 > 1；长序列并行场景下 `dp_cp_size > 1`
- 必备训练特性：`--bf16`（覆盖混精计算）、`--overlap-grad-reduce`、`--load`、`--save`、`--ckpt-format torch`；`--use-distributed-optimizer` 开/未开均可
- 弹性训练额外约束：仅支持 `Data Parallel` / `Tensor Parallel` / `Pipeline Parallel` 并行；不可同时启用 `use-custom-fsdp`、`reuse-fp32-param`；缩容后不可再次缩容，扩容仅支持回到原规模

## 图文联合解读

- `grad_buffer_sharding.png`: **图文联合解读：**

1) 图示内容：4个DP rank的Megatron原生分布式优化器数据流。模型层产生grads/params，经reduce-scatter将梯度分片到各rank的optim shards上做optim step，再通过all-gather收集回完整参数；中间放大了grad buffer的分片视图。

2) 技术结论：原生方案将优化器状态分片到各DP以省内存，但分片单一、无备份。

3) 与文档论点关系：作为副本优化器的对比基线——正因原生方案缺乏状态冗余，才需设计副本优化器为TTP临终遗言、UCE在线修复、弹性训练提供状态备份支撑。
- `replica_optimizer.png`: **图示解读**

**1) 图中内容**：上方"Distributed Optimizer"展示原生方案——4个参数（绿/黄/蓝/红）经分片后由dp rank 0~3各持一份不重叠的梯度分片。下方"Replica Optimizer"将DP组拆为两个副本子组（rank0与rank2一组，rank1与rank3一组），每组完整持有全部4个参数的分片，形成备份关系。

**2) 技术结论**：副本优化器通过让两份DP子组各持一份参数/优化器状态的完整副本，以冗余存储换取得对每份参数状态的可用性备份，为故障恢复提供机制基础。

**3) 与文档论点对应**：图直接支撑文档"将数据并行组切分成两个副本数据并行组"的原理说明；其冗余结构正是TTP临终遗言（校验恢复）、UCE Step级重计算（在线修复）、弹性训练（DP级缩扩容）三大高可用功能得以实现的前提。
