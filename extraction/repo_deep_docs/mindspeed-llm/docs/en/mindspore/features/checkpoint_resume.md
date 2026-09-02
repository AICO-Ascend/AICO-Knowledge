# Checkpoint-based Resumable Training

> 仓 `mindspeed-llm` · 路径 `docs/en/mindspore/features/checkpoint_resume.md` · 类型 feature · MiniMax-M3 文档深读 + 图文关联 · ver=v2
> 原文: extraction/repo_docs/mindspeed-llm/docs/en/mindspore/features/checkpoint_resume.md

```markdown
# 一体化深度解读: Checkpoint-based Resumable Training

## 【定位】
这篇文档描述 mindspeed-llm(昇腾 LLM 分布式训练框架)在**大规模预训练因硬件故障或资源调度等原因中断后**,如何通过**基于检查点(checkpoint)的可恢复训练机制**让任务从中断处继续运行而非从头开始的能力,并给出对应的参数配置、保存/加载流程与一致性约束。

---

## 【技术要点】

1. **启用前提: 分布式优化器必须开启**  
   在 `pretrain` 脚本的 `GPT_ARGS` 中必须携带 `--use-distributed-optimizer`,其作用是将 optimizer state 跨 data parallel rank 分布式保存,为后续恢复做准备。

2. **三类禁用参数**  
   启用可恢复训练时**不得**设置 `--finetune`、`--no-load-optim`、`--no-load-rng`,否则系统会跳过 optimizer state 与随机状态的恢复,无法真正"续训"。

3. **训练中自动保存**  
   通过 `--save $SAVE_PATH` 指定保存路径,配合 `--save-interval`(原文示例 `500`,即**每 500 步保存一次**)由系统在迭代过程中自动落盘完整 checkpoint;每次保存都包含 model weights、optimizer states、训练迭代数、随机状态四类信息。

4. **checkpoint 落盘目录结构**  
   每次保存形成 `iter_XXXXXXXX/` 目录,内含各 `mp_rank_XX_YYY` 子目录,子目录下挂载两份核心文件: `distrib_optim.pt`(分布式优化器状态)与 `model_optim_rng.pt`(模型参数 + 优化器状态 + 随机状态)。路径顶层由 `latest_checkpointed_iteration.txt` 记录最新迭代号。

5. **续训加载机制**  
   通过 `--load $CHECKPOINT_PATH` 指定之前的保存路径,系统**自动读取 `latest_checkpointed_iteration.txt`** 定位最新迭代,再恢复模型与优化器状态,无需人工指定 iteration。

6. **环境一致性硬约束**  
   恢复训练时 batch size、模型结构、训练迭代数、optimizer 类型必须与原 run 完全一致;**NPUs 数量与 TP/DP 并行策略必须保持不变**,否则加载失败。

---

## 【关键机制与数据】

### 工作原理(数据流)
- **保存阶段**: 训练循环在每 `--save-interval` 步触发落盘 → 写两份互补的 `.pt` 文件(`distrib_optim.pt` + `model_optim_rng.pt`)→ 同时更新顶层 `latest_checkpointed_iteration.txt` 作为下次恢复的入口指针。
- **加载阶段**: `pretrain_gpt.py` 通过 `--load` 接收路径 → 解析 `latest_checkpointed_iteration.txt` → 按 `iter_XXXXXXXX/mp_rank_XX_YYY` 的目录布局回灌 `distrib_optim.pt`(优化器 Adam 的 momentum 与 variance、学习率调度器状态)与 `model_optim_rng.pt`(模型参数 + 随机状态)→ 从该 iteration 继续训练。
- **校验语义**: 恢复后系统会重新建立"已完成训练迭代数"以避免重复训练,因此**optimizer 状态(含 Adam 动量与方差)、学习率调度器状态、迭代计数**三者缺一不可,这也解释了为何 `--finetune`/`--no-load-optim`/`--no-load-rng` 任何一个被启用都会破坏续训。

### 性能数据(原文日志样本)
- 原文给出的加载耗时日志(一次实测样本):
  - `successfully loaded checkpoint from xx at iteration x`
  - `(min, max) time across ranks(ms):`
  - `load-checkpoint ....................:(9289.88, 9288.22)`
- 该日志展示了**跨 rank 加载 checkpoint 的耗时区间**(以 ms 为单位),用于运维侧观察恢复开销;原文**仅给出此一例样本**,未提供平均/峰值统计数据或吞吐对比。

---

## 【表格解读】

原文包含 1 个参数表,逐字还原如下:

| Parameter | Description |
|------|------|
| `--use-distributed-optimizer` | This parameter must be enabled. This saves the optimizer state across data parallel ranks in a distributed manner, which makes later restoration easier. |
| `--finetune` | ❌ Do not set this option. Otherwise, the system skips loading the optimizer state. |
| `--no-load-optim` | ❌ Do not set this option. Otherwise, the system does not restore the optimizer state, such as the learning rate and momentum. |

逐行解读:

- **`--use-distributed-optimizer`(必启用)**: 这是 checkpoint-based resumable training 的**使能开关**。其效果是将 optimizer state 沿 data parallel rank 做分布式切分并落盘,既降低单 rank 内存压力,也让后续按 rank 还原时一一对应,这是可恢复训练能成立的基础条件。
- **`--finetune`(禁止使用)**: 该参数用于"只加载模型权重做下游微调",会**跳过 optimizer state 加载**。一旦开启,恢复出来的训练既无 Adam momentum/variance 也无学习率调度器状态,等同于把"续训"降级为"从头微调",因此文档明确禁止。
- **`--no-load-optim`(禁止使用)**: 字面意义即"不加载 optimizer 状态",会使学习率(learning rate)和动量(momentum)等关键状态缺失,导致训练从错误的状态基线继续,迭代计数也无法严格对齐,文档同样明确禁止。

> 文档正文补充提示(不在表格中但与表格语义绑定): `--no-load-rng` 也被禁止,因为它会使随机状态无法恢复,无法真正"续训"。

---

## 【公式解读】

原文无公式。

---

## 【关联】

文档未提供文末内部链接(原文 `(无)`),但从内容中可识别出与以下模块/特性的耦合关系:

- **分布式优化器(Distributed Optimizer)**: `--use-distributed-optimizer` 是该特性的入口;`distrib_optim.pt` 文件是其产物。resumable training 的可行性建立在 optimizer state 已被分布式切分保存的前提之上。
- **Adam 优化器状态(动量 momentum / 方差 variance)**: 是 `model_optim_rng.pt` 与 `distrib_optim.pt` 中必须被恢复的关键载荷,这也是 `--no-load-optim` 被禁用的根本原因。
- **学习率调度器(Learning Rate Scheduler)**: 其状态随 optimizer state 一起被持久化与恢复,保证恢复后学习率曲线与中断前连续。
- **张量并行 / 数据并行(TP / DP)**: 文档将 TP/DP 并行策略列为"恢复时必须保持不变"的硬约束,说明 checkpoint 的并行维度布局(TP shard)与 DP rank 拓扑必须与原 run 一致,否则张量分片无法对齐、加载会失败。
- **`pretrain_gpt.py` 训练脚本与 `msrun` 分布式启动器**: 文档给出的命令范式为 `msrun ${DISTRIBUTED_ARGS} pretrain_gpt.py ...`,即续训触发入口是 msrun 启动下的 GPT 预训练脚本。
- **MindSpore 侧训练主循环(checkpoint 落盘/加载子系统)**: `latest_checkpointed_iteration.txt` 的写入与读取、`iter_XXXXXXXX/mp_rank_XX_YYY/` 的目录组织方式,均表明该特性复用/对齐了 MindSpore 通用 checkpoint 管理约定。

---

## 【使用方法】

### 1. 启动预训练脚本时的 GPT_ARGS(开启可恢复训练)

```bash
GPT_ARGS="
    [other parameters...] \
    --use-distributed-optimizer \  # Use the distributed optimizer. Required.
"
```

> 同时需确认 `GPT_ARGS` 中**未**携带 `--finetune`、`--no-load-optim`、`--no-load-rng`。

### 2. 配置训练中自动保存

```bash
--save /your/checkpoint/path \
--save-interval 500   # Save once every 500 steps.
```

保存产物结构:

```shell
/your/checkpoint/path/
├── latest_checkpointed_iteration.txt
├── iter_0000001/
│   ├── mp_rank_00_000
│   │   ├── distrib_optim.pt
│   │   └── model_optim_rng.pt
│   └── ...
└── iter_0000500/
    ├── mp_rank_00_000
    │   ├── distrib_optim.pt
    │   └── model_optim_rng.pt
    └── ...
```

### 3. 中断后恢复训练

```bash
GPT_ARGS="
    [other parameters...] \
    --use-distributed-optimizer \  # Use the distributed optimizer. Required.
"

...

msrun ${DISTRIBUTED_ARGS} pretrain_gpt.py \
    [other parameters...] \
    --load $CHECKPOINT_PATH \
```

系统会自动读取 `latest_checkpointed_iteration.txt` 找到最新 iteration 并恢复模型 + 优化器状态。

### 4. 恢复成功后的日志形态(原文示例)

```shell
successfully loaded checkpoint from xx at iteration x
(min, max) time across ranks(ms):
load-checkpoint ....................:(9289.88, 9288.22)
```

### 5. 注意事项(N原文 Notes 节)

1. **文件完整性**: `$CHECKPOINT_PATH` 下 checkpoint 文件须完整无缺。
2. **训练配置一致性**: 恢复时 batch size、模型结构、训练迭代数、optimizer 类型等需与原 run 保持一致。
3. **分布式环境匹配**: NPUs 数量及 TP/DP 等并行策略必须不变,否则加载失败。

> 原文未涉及: 跨集群/跨存储后端的恢复、不同 `--save-interval` 下的恢复策略对比、checkpoint 保留份数与清理策略等均未在文档中给出。
```
